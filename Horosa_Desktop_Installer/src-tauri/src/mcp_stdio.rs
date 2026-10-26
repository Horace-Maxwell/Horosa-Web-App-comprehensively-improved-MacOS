//! 本机 MCP 的 stdio 代理(给 Claude Desktop 这类只会 stdio 的客户端):
//! `Horosa --horosa-mcp-stdio <endpoint-file>`——读端点文件取 url+token → 循环读 stdin 一行 JSON-RPC(≤ 1MiB)
//! → POST /mcp(Bearer,回环)→ 把回体压成一行写 stdout。应用未运行(端点文件缺失 / 连接拒绝)→ 对每个带 id 的
//! 请求回 -32001,通知(无 id)静默丢;stdin EOF 即退。零 UI、零窗口、零日志(令牌永不落盘落屏)。
//! **本模块永不执行工具,只搬运** JSON-RPC;会话 id(Mcp-Session-Id)由服务端发、本代理原样回带。
//! [2026-07-28 双纪元] stdio 没有头层:带现代 `_meta.protocolVersion` 的行(或 `server/discover` 探测)按体派生三头
//! (MCP-Protocol-Version / Mcp-Method / Mcp-Name 哨兵编码)再转发、不带会话头;旧行逐字同今日。`subscriptions/listen`
//! 长流在串行代理里会卡死后续行 ⇒ 本地回 -32601(不转发);现代 400/404 的 JSON 错误原样透传。
use std::collections::HashMap;
use std::io::{BufRead, Write};
use std::path::Path;
use std::sync::atomic::{AtomicBool, AtomicU64, Ordering};
use std::sync::{Arc, Condvar, Mutex};
use std::time::Duration;

use serde_json::{json, Value};

pub const STDIO_LINE_MAX: usize = 1024 * 1024;
pub const ERR_NOT_RUNNING: i64 = -32001;
pub const ERR_PARSE: i64 = -32700;
pub const ERR_INVALID: i64 = -32600;
pub const ERR_INTERNAL: i64 = -32603;
pub const MCP_STDIO_FLAG: &str = "--horosa-mcp-stdio";
pub const ERR_METHOD_NOT_FOUND: i64 = -32601;
const MODERN_META_VERSION: &str = "io.modelcontextprotocol/protocolVersion";
const MODERN_DEFAULT_VERSION: &str = "2026-07-28";

/// 现代行的派生头(stdio 无头层,由行体推出;名字/URI 经哨兵编码)
#[derive(Debug, Clone, PartialEq, Eq)]
pub struct ModernLineHeaders {
    pub version: String,
    pub method: String,
    pub name: Option<String>,
}

/// 带现代 `_meta.protocolVersion` 的行 ⇒ Some;`server/discover` 无 _meta 的探测行也按现代(缺省版本);其余(含一切 initialize)⇒ None
pub fn modern_line_headers(parsed: &Value) -> Option<ModernLineHeaders> {
    let method = parsed.get("method").and_then(|m| m.as_str())?.to_string();
    let params = parsed.get("params").cloned().unwrap_or(json!({}));
    let meta_version = params
        .get("_meta")
        .and_then(|m| m.get(MODERN_META_VERSION))
        .and_then(|v| v.as_str())
        .map(|v| v.trim().to_string());
    let version = match meta_version {
        Some(v) => v,
        None if method == "server/discover" => MODERN_DEFAULT_VERSION.to_string(),
        None => return None,
    };
    if method == "initialize" {
        return None;
    }
    let name = match method.as_str() {
        "tools/call" | "prompts/get" => params
            .get("name")
            .and_then(|v| v.as_str())
            .map(|v| v.to_string()),
        "resources/read" => params
            .get("uri")
            .and_then(|v| v.as_str())
            .map(|v| v.to_string()),
        _ => None,
    };
    Some(ModernLineHeaders {
        version,
        method,
        name: name.map(|n| crate::mcp_server::encode_header_value(&n)),
    })
}

#[derive(Debug, Clone)]
pub struct Endpoint {
    pub url: String,
    pub token: String,
    pub pid: Option<u32>,
}

/// 端点文件形状 {url, token, pid, …};只认回环 http 地址,令牌须像样(≥16)。
pub fn parse_endpoint(text: &str) -> Result<Endpoint, String> {
    let v: Value =
        serde_json::from_str(text).map_err(|_| "endpoint file is not JSON".to_string())?;
    let url = v
        .get("url")
        .and_then(|x| x.as_str())
        .unwrap_or("")
        .trim()
        .to_string();
    let token = v
        .get("token")
        .and_then(|x| x.as_str())
        .unwrap_or("")
        .trim()
        .to_string();
    let pid = v.get("pid").and_then(|x| x.as_u64()).map(|p| p as u32);
    if !endpoint_url_ok(&url) {
        return Err("endpoint url must be a loopback http address".to_string());
    }
    if token.len() < 16 {
        return Err("endpoint token missing".to_string());
    }
    Ok(Endpoint { url, token, pid })
}

/// 端点地址按 URL 解析后核验(不做前缀匹配:`http://127.0.0.1:1@evil.example/mcp` 的主机其实是 evil.example):
/// 只认 http、主机是本机回环、不带用户信息。
fn endpoint_url_ok(url: &str) -> bool {
    match reqwest::Url::parse(url) {
        Ok(u) => {
            u.scheme() == "http"
                && u.username().is_empty()
                && u.password().is_none()
                && url_host_is_loopback(&u)
        }
        Err(_) => false,
    }
}

/// URL 的主机是不是本机回环(127.0.0.0/8 · ::1 · localhost)。
pub(crate) fn url_host_is_loopback(url: &reqwest::Url) -> bool {
    let Some(host) = url.host_str() else {
        return false;
    };
    if host.eq_ignore_ascii_case("localhost") {
        return true;
    }
    let bare = host.trim_start_matches('[').trim_end_matches(']');
    bare.parse::<std::net::IpAddr>()
        .map(|ip| ip.is_loopback())
        .unwrap_or(false)
}

/// 端点核验不过的原因(发令牌之前查):
/// 进程不在 / 不是本用户的进程、服务连不上、健康探针超时、探针回的进程号对不上(端口被别的程序占了)。
#[derive(Debug, Clone, PartialEq, Eq)]
pub enum EndpointCheck {
    NoPid,
    PidDead,
    Unreachable,
    Timeout,
    Mismatch,
}

/// 本用户的进程是否在(kill(pid, 0) 成功;别的用户的同号进程回 EPERM,按「不在」算)。
pub fn pid_alive(pid: u32) -> bool {
    #[cfg(unix)]
    {
        if pid <= 1 || pid > i32::MAX as u32 {
            return false;
        }
        // SAFETY: 信号 0 只做存在与权限检查,不投递任何信号
        unsafe { libc::kill(pid as libc::pid_t, 0) == 0 }
    }
    #[cfg(not(unix))]
    {
        let _ = pid;
        true
    }
}

/// 带令牌发请求之前先核对端点:端点文件里的进程还活着,且 GET /healthz(不带令牌)回的进程号与之一致 ——
/// 陈旧的端点文件(应用已退出、端口被别的程序占了)不会把令牌送出去。成功回健康探针的 JSON。
pub fn verify_endpoint(
    client: &reqwest::blocking::Client,
    ep: &Endpoint,
    timeout: Duration,
) -> Result<Value, EndpointCheck> {
    let pid = ep.pid.ok_or(EndpointCheck::NoPid)?;
    if !pid_alive(pid) {
        return Err(EndpointCheck::PidDead);
    }
    let base = ep.url.trim_end_matches("/mcp");
    let resp = client
        .get(format!("{}/healthz", base))
        .timeout(timeout)
        .send()
        .map_err(|e| {
            if e.is_timeout() {
                EndpointCheck::Timeout
            } else {
                EndpointCheck::Unreachable
            }
        })?;
    if !resp.status().is_success() {
        return Err(EndpointCheck::Mismatch);
    }
    let health: Value = resp.json().map_err(|e| {
        if e.is_timeout() {
            EndpointCheck::Timeout
        } else {
            EndpointCheck::Mismatch
        }
    })?;
    let same_app = health.get("app").and_then(|a| a.as_str()) == Some("horosa");
    let same_pid = health.get("pid").and_then(|p| p.as_u64()) == Some(pid as u64);
    if same_app && same_pid {
        Ok(health)
    } else {
        Err(EndpointCheck::Mismatch)
    }
}

pub fn read_endpoint(path: &Path) -> Result<Endpoint, String> {
    let text = std::fs::read_to_string(path)
        .map_err(|e| format!("cannot read endpoint file: {}", e.kind()))?;
    parse_endpoint(&text)
}

/// 读一行(不含换行,去尾 CR);EOF 且无残留 → Ok(None);超长 → 丢弃该行剩余并回 InvalidData(下一行仍可读)。
pub fn read_line_bounded<R: BufRead>(r: &mut R, max: usize) -> std::io::Result<Option<Vec<u8>>> {
    let mut buf: Vec<u8> = Vec::new();
    loop {
        let chunk = r.fill_buf()?;
        if chunk.is_empty() {
            return if buf.is_empty() {
                Ok(None)
            } else {
                Ok(Some(buf))
            };
        }
        match chunk.iter().position(|&b| b == b'\n') {
            Some(i) => {
                if buf.len() + i > max {
                    r.consume(i + 1);
                    return Err(std::io::Error::new(
                        std::io::ErrorKind::InvalidData,
                        "line too large",
                    ));
                }
                buf.extend_from_slice(&chunk[..i]);
                r.consume(i + 1);
                if buf.last() == Some(&b'\r') {
                    buf.pop();
                }
                return Ok(Some(buf));
            }
            None => {
                let n = chunk.len();
                if buf.len() + n > max {
                    r.consume(n);
                    // 丢到行尾(或 EOF),让下一行还能读
                    loop {
                        let c = r.fill_buf()?;
                        if c.is_empty() {
                            break;
                        }
                        match c.iter().position(|&b| b == b'\n') {
                            Some(j) => {
                                r.consume(j + 1);
                                break;
                            }
                            None => {
                                let m = c.len();
                                r.consume(m);
                            }
                        }
                    }
                    return Err(std::io::Error::new(
                        std::io::ErrorKind::InvalidData,
                        "line too large",
                    ));
                }
                buf.extend_from_slice(chunk);
                r.consume(n);
            }
        }
    }
}

pub fn error_response(id: Option<&Value>, code: i64, message: &str) -> Value {
    json!({ "jsonrpc": "2.0", "id": id.cloned().unwrap_or(Value::Null), "error": { "code": code, "message": message } })
}

fn is_notification(v: &Value) -> bool {
    let has_id = v.get("id").map(|i| !i.is_null()).unwrap_or(false);
    !has_id
}

/// 同时在途的转发上限(超出的请求线程排队等名额,读 stdin 的主循环不被堵 —— 取消通知随到随转)
pub const MAX_CONCURRENT: usize = 8;
/// 已派生未了结的请求线程硬顶(到顶才让主循环等;防一个客户端灌满线程)
const MAX_PENDING_THREADS: usize = 64;
const LEGACY_DEFAULT_VERSION: &str = "2025-06-18";

/// 在途请求的登记(按 JSON 序列化的 id):取消通知按原请求的纪元与会话转发,并让本地线程丢弃迟到的回包
struct InflightLine {
    modern: Option<ModernLineHeaders>,
    session: Option<String>,
    client_meta: Option<Value>,
    cancelled: Arc<AtomicBool>,
}

struct Shared<'a, W: Write + Send> {
    out: Mutex<&'a mut W>,
    client: &'a reqwest::blocking::Client,
    ep: Option<&'a Endpoint>,
    session: Mutex<Option<String>>,
    legacy_version: Mutex<String>,
    inflight: Mutex<HashMap<String, InflightLine>>,
    slots: (Mutex<usize>, Condvar),
    threads: (Mutex<usize>, Condvar),
    errors: AtomicU64,
}

impl<'a, W: Write + Send> Shared<'a, W> {
    fn emit(&self, v: &Value) {
        if let Ok(mut w) = self.out.lock() {
            let _ = writeln!(w, "{}", v);
            let _ = w.flush();
        }
    }
    fn error_line(&self, id: Option<&Value>, code: i64, message: &str) {
        self.errors.fetch_add(1, Ordering::SeqCst);
        self.emit(&error_response(id, code, message));
    }
    fn acquire(pair: &(Mutex<usize>, Condvar), cap: usize) {
        let (m, cv) = pair;
        let mut n = m.lock().unwrap_or_else(|e| e.into_inner());
        while *n >= cap {
            n = cv.wait(n).unwrap_or_else(|e| e.into_inner());
        }
        *n += 1;
    }
    fn release(pair: &(Mutex<usize>, Condvar)) {
        let (m, cv) = pair;
        if let Ok(mut n) = m.lock() {
            *n = n.saturating_sub(1);
        }
        cv.notify_one();
    }

    /// 发一条 POST;Ok(响应)/ Err(连接失败,文案不含令牌与地址)。
    /// `modern` 给定 ⇒ 注现代三头、不带会话头(无状态);None ⇒ 旧头(协商出的版本)+ 会话头。
    fn post(
        &self,
        body: &[u8],
        modern: Option<&ModernLineHeaders>,
        session: Option<&str>,
        accept_sse: bool,
        timeout: Duration,
    ) -> Result<reqwest::blocking::Response, String> {
        let ep = self.ep.ok_or_else(|| "no endpoint".to_string())?;
        let mut req = self
            .client
            .post(&ep.url)
            .timeout(timeout)
            .header("Authorization", format!("Bearer {}", ep.token))
            .header("Content-Type", "application/json");
        match modern {
            Some(m) => {
                req = req
                    .header("Accept", "application/json, text/event-stream")
                    .header("MCP-Protocol-Version", m.version.clone())
                    .header("Mcp-Method", m.method.clone());
                if let Some(n) = &m.name {
                    req = req.header("Mcp-Name", n.clone());
                }
            }
            None => {
                let v = self
                    .legacy_version
                    .lock()
                    .map(|v| v.clone())
                    .unwrap_or_else(|_| LEGACY_DEFAULT_VERSION.to_string());
                req = req
                    .header(
                        "Accept",
                        if accept_sse {
                            "application/json, text/event-stream"
                        } else {
                            "application/json"
                        },
                    )
                    .header("MCP-Protocol-Version", v);
                if let Some(s) = session {
                    req = req.header("Mcp-Session-Id", s.to_string());
                }
            }
        }
        let resp = req
            .body(body.to_vec())
            .send()
            .map_err(|e| format!("{}", e.without_url()))?;
        if modern.is_none() {
            if let Some(h) = resp
                .headers()
                .get("mcp-session-id")
                .and_then(|h| h.to_str().ok())
            {
                if !h.trim().is_empty() {
                    if let Ok(mut s) = self.session.lock() {
                        *s = Some(h.trim().to_string());
                    }
                }
            }
        }
        Ok(resp)
    }

    /// 转发一条请求并把回包(单体 JSON 或响应流里的每条消息)逐行写回;取消了就一个字也不写。回是否收到了该 id 的回包。
    fn forward_request(
        &self,
        line: &[u8],
        parsed: &Value,
        modern: Option<&ModernLineHeaders>,
        session: Option<&str>,
        cancelled: &AtomicBool,
    ) -> Option<Value> {
        let id = parsed.get("id").cloned();
        if cancelled.load(Ordering::SeqCst) {
            return None;
        }
        let wants_progress = parsed
            .get("params")
            .and_then(|p| p.get("_meta"))
            .and_then(|m| m.get("progressToken"))
            .is_some();
        let resp = match self.post(
            line,
            modern,
            session,
            wants_progress,
            request_timeout_for(parsed),
        ) {
            Ok(r) => r,
            Err(_) => {
                if !cancelled.load(Ordering::SeqCst) {
                    self.error_line(
                        id.as_ref(),
                        ERR_NOT_RUNNING,
                        "Horosa is not running (local MCP service unreachable)",
                    );
                }
                return None;
            }
        };
        let status = resp.status().as_u16();
        let is_sse = resp
            .headers()
            .get("content-type")
            .and_then(|h| h.to_str().ok())
            .map(|c| c.to_ascii_lowercase().starts_with("text/event-stream"))
            .unwrap_or(false);
        if is_sse {
            // 响应流:逐个事件取 data 行;请求级通知(进度)原样写回,带同一 id 的消息 = 回包,写完即止。
            let mut reader = std::io::BufReader::new(resp);
            let mut data: Vec<String> = Vec::new();
            let mut answer: Option<Value> = None;
            loop {
                if cancelled.load(Ordering::SeqCst) {
                    // 丢掉响应(关连接):现代纪元服务端据此判取消;旧纪元已另转取消通知
                    return None;
                }
                let mut l = String::new();
                match std::io::BufRead::read_line(&mut reader, &mut l) {
                    Ok(0) => break,
                    Ok(_) => {}
                    Err(_) => break,
                }
                let t = l.trim_end_matches(['\r', '\n']);
                if t.is_empty() {
                    if !data.is_empty() {
                        let payload = data.join("\n");
                        data.clear();
                        if let Ok(v) = serde_json::from_str::<Value>(&payload) {
                            let is_answer = v.get("method").is_none() && v.get("id").cloned() == id;
                            if cancelled.load(Ordering::SeqCst) {
                                return None;
                            }
                            self.emit(&v);
                            if is_answer {
                                answer = Some(v);
                                break;
                            }
                        }
                    }
                    continue;
                }
                if let Some(rest) = t.strip_prefix("data:") {
                    data.push(rest.strip_prefix(' ').unwrap_or(rest).to_string());
                }
                // 注释(: keep-alive)/ event: / id: 行一律忽略
            }
            if answer.is_none() && !cancelled.load(Ordering::SeqCst) {
                self.error_line(
                    id.as_ref(),
                    ERR_INTERNAL,
                    &format!("response stream ended without a result (HTTP {status})"),
                );
            }
            return answer;
        }
        let text = match resp.text() {
            Ok(t) => t,
            Err(_) => {
                if !cancelled.load(Ordering::SeqCst) {
                    self.error_line(
                        id.as_ref(),
                        ERR_NOT_RUNNING,
                        "Horosa is not running (local MCP service unreachable)",
                    );
                }
                return None;
            }
        };
        if cancelled.load(Ordering::SeqCst) {
            return None;
        }
        if status == 202 || text.trim().is_empty() {
            self.error_line(
                id.as_ref(),
                ERR_INTERNAL,
                &format!("empty response (HTTP {status})"),
            );
            return None;
        }
        match serde_json::from_str::<Value>(&text) {
            Ok(v) => {
                self.emit(&v);
                Some(v)
            }
            Err(_) => {
                self.error_line(
                    id.as_ref(),
                    ERR_INTERNAL,
                    &format!("non-JSON response (HTTP {status})"),
                );
                None
            }
        }
    }

    /// 通知:原样转发(202 不出行)。notifications/cancelled 按原请求的纪元 / 会话转,并就地置本地取消位。
    fn forward_notification(
        &self,
        line: &[u8],
        parsed: &Value,
        modern: Option<&ModernLineHeaders>,
    ) {
        if parsed.get("method").and_then(|m| m.as_str()) == Some("notifications/cancelled") {
            let rid = parsed
                .get("params")
                .and_then(|p| p.get("requestId"))
                .cloned()
                .unwrap_or(Value::Null);
            let routed = self.inflight.lock().ok().and_then(|map| {
                map.get(&rid.to_string()).map(|e| {
                    e.cancelled.store(true, Ordering::SeqCst);
                    (e.modern.clone(), e.session.clone(), e.client_meta.clone())
                })
            });
            if let Some((orig_modern, session, client_meta)) = routed {
                match orig_modern {
                    Some(m) => {
                        // 现代:补上原请求的身份(_meta 协议版本 / 客户端名),服务端据此精确定位;另外本地已关流(断开 = 取消)
                        let mut body = parsed.clone();
                        if let Some(p) = body.get_mut("params").and_then(|p| p.as_object_mut()) {
                            let meta = p.entry("_meta").or_insert(json!({}));
                            if let (Some(mm), Some(src)) = (
                                meta.as_object_mut(),
                                client_meta.as_ref().and_then(|c| c.as_object()),
                            ) {
                                for (k, v) in src {
                                    mm.entry(k.clone()).or_insert(v.clone());
                                }
                            }
                        }
                        let hdr = ModernLineHeaders {
                            version: m.version.clone(),
                            method: "notifications/cancelled".to_string(),
                            name: None,
                        };
                        let _ = self.post(
                            body.to_string().as_bytes(),
                            Some(&hdr),
                            None,
                            false,
                            Duration::from_secs(10),
                        );
                    }
                    None => {
                        let _ = self.post(
                            line,
                            None,
                            session.as_deref(),
                            false,
                            Duration::from_secs(10),
                        );
                    }
                }
                return;
            }
        }
        let session = self.session.lock().ok().and_then(|s| s.clone());
        let _ = self.post(
            line,
            modern,
            if modern.is_some() {
                None
            } else {
                session.as_deref()
            },
            false,
            Duration::from_secs(10),
        );
    }
}

/// 单条请求的 HTTP 预算:tools/call 跟壳同口径(客户端 _meta.timeoutMs 钳 1 s..600 s,缺省 120 s)再加 10 s 余量;其余 30 s。
/// 此前代理整体写死 120 s:客户端给了更长的工具预算(如 180 s 的无头分析)也会在代理这一跳先断。
pub fn request_timeout_for(parsed: &Value) -> Duration {
    let method = parsed.get("method").and_then(|m| m.as_str()).unwrap_or("");
    if method != "tools/call" {
        return Duration::from_secs(30);
    }
    let params = parsed.get("params").cloned().unwrap_or(json!({}));
    crate::mcp_server::tool_timeout_of(&params) + Duration::from_secs(10)
}

/// 一行进、一行(或多行:响应流里的进度通知 + 回包)出;回 (处理的行数, 出错数)。
/// 请求各起一个线程转发(同时在途 ≤ MAX_CONCURRENT),主循环只读 stdin —— 长调用期间取消通知照样随到随转;
/// initialize(旧纪元握手)在主循环里同步做完再读下一行,保证之后的请求都带上它发的会话头与协商出的版本。
/// 回包按完成先后写出(客户端按 id 配对);stdin EOF 后等全部在途请求了结再返回。
pub fn serve<R: BufRead, W: Write + Send>(
    r: &mut R,
    w: &mut W,
    client: &reqwest::blocking::Client,
    ep: Option<&Endpoint>,
) -> (u64, u64) {
    let mut handled: u64 = 0;
    let shared = Shared {
        out: Mutex::new(w),
        client,
        ep,
        session: Mutex::new(None),
        legacy_version: Mutex::new(LEGACY_DEFAULT_VERSION.to_string()),
        inflight: Mutex::new(HashMap::new()),
        slots: (Mutex::new(0), Condvar::new()),
        threads: (Mutex::new(0), Condvar::new()),
        errors: AtomicU64::new(0),
    };
    let shared = &shared;
    std::thread::scope(|scope| loop {
        let line = match read_line_bounded(r, STDIO_LINE_MAX) {
            Ok(None) => break,
            Ok(Some(l)) => l,
            Err(e) if e.kind() == std::io::ErrorKind::InvalidData => {
                shared.error_line(None, ERR_INVALID, "request line too large (limit 1MiB)");
                continue;
            }
            Err(_) => break,
        };
        if line.iter().all(|b| b.is_ascii_whitespace()) {
            continue;
        }
        handled += 1;
        let parsed: Value = match serde_json::from_slice(&line) {
            Ok(v) => v,
            Err(_) => {
                shared.error_line(None, ERR_PARSE, "parse error");
                continue;
            }
        };
        if parsed.is_array() {
            shared.error_line(None, ERR_INVALID, "batch requests are not supported");
            continue;
        }
        if !parsed.is_object() {
            shared.error_line(None, ERR_INVALID, "request must be a JSON object");
            continue;
        }
        let notification = is_notification(&parsed);
        let id = parsed.get("id").cloned();
        let modern = modern_line_headers(&parsed);
        // 现代长流在代理里会占死一个转发线程且无处投递 ⇒ 本地回 -32601,不转发(通知形态直接丢)
        if modern.is_some()
            && parsed.get("method").and_then(|m| m.as_str()) == Some("subscriptions/listen")
        {
            if !notification {
                shared.error_line(id.as_ref(), ERR_METHOD_NOT_FOUND, "subscriptions/listen is not available through the stdio proxy (use the HTTP endpoint for change notifications)");
            }
            continue;
        }
        if shared.ep.is_none() {
            if !notification {
                shared.error_line(
                    id.as_ref(),
                    ERR_NOT_RUNNING,
                    "Horosa is not running (endpoint file missing or invalid)",
                );
            }
            continue;
        }
        if notification {
            shared.forward_notification(&line, &parsed, modern.as_ref());
            continue;
        }
        let is_initialize =
            modern.is_none() && parsed.get("method").and_then(|m| m.as_str()) == Some("initialize");
        if is_initialize {
            // 握手同步做:之后的行都要用它发的会话头与协商出的版本
            let never = AtomicBool::new(false);
            if let Some(v) = shared.forward_request(&line, &parsed, None, None, &never) {
                if let Some(ver) = v
                    .get("result")
                    .and_then(|r| r.get("protocolVersion"))
                    .and_then(|x| x.as_str())
                {
                    if crate::mcp_server::MCP_PROTOCOL_VERSIONS.contains(&ver) {
                        if let Ok(mut lv) = shared.legacy_version.lock() {
                            *lv = ver.to_string();
                        }
                    }
                }
            }
            continue;
        }
        let key = id.clone().unwrap_or(Value::Null).to_string();
        let cancelled = Arc::new(AtomicBool::new(false));
        let session = if modern.is_some() {
            None
        } else {
            shared.session.lock().ok().and_then(|s| s.clone())
        };
        let client_meta = parsed
            .get("params")
            .and_then(|p| p.get("_meta"))
            .filter(|m| m.is_object())
            .cloned();
        if let Ok(mut map) = shared.inflight.lock() {
            map.insert(
                key.clone(),
                InflightLine {
                    modern: modern.clone(),
                    session: session.clone(),
                    client_meta,
                    cancelled: Arc::clone(&cancelled),
                },
            );
        }
        Shared::<W>::acquire(&shared.threads, MAX_PENDING_THREADS);
        scope.spawn(move || {
            Shared::<W>::acquire(&shared.slots, MAX_CONCURRENT);
            shared.forward_request(
                &line,
                &parsed,
                modern.as_ref(),
                session.as_deref(),
                &cancelled,
            );
            Shared::<W>::release(&shared.slots);
            if let Ok(mut map) = shared.inflight.lock() {
                if map
                    .get(&key)
                    .map(|e| Arc::ptr_eq(&e.cancelled, &cancelled))
                    .unwrap_or(false)
                {
                    map.remove(&key);
                }
            }
            Shared::<W>::release(&shared.threads);
        });
    });
    (handled, shared.errors.load(Ordering::SeqCst))
}

pub fn build_client() -> Option<reqwest::blocking::Client> {
    // 不设整体超时(长调用 + 响应流);每条请求按 request_timeout_for 单独给预算
    reqwest::blocking::Client::builder()
        .connect_timeout(Duration::from_secs(5))
        .timeout(None)
        .no_proxy()
        // 本机服务从不重定向:不跟随,令牌不会被 3xx 带去别处
        .redirect(reqwest::redirect::Policy::none())
        .build()
        .ok()
}

/// 端点健康核对的预算(本机回环,正常毫秒级)
pub const VERIFY_TIMEOUT: Duration = Duration::from_secs(5);

/// CLI 入口:退出码 0=正常到 EOF;2=HTTP 客户端建不起来。端点文件读不到不算错(每个请求回 -32001,让客户端能看到原因)。
pub fn run_cli(endpoint_path: &Path) -> i32 {
    let Some(client) = build_client() else {
        return 2;
    };
    // 端点核不过(进程不在 / 探针对不上)⇒ 当作服务没开:每个请求回 -32001,令牌一个字节都不发出去
    let ep = read_endpoint(endpoint_path)
        .ok()
        .filter(|ep| verify_endpoint(&client, ep, VERIFY_TIMEOUT).is_ok());
    let stdin = std::io::stdin();
    let mut reader = stdin.lock();
    let mut writer = std::io::stdout();
    let _ = serve(&mut reader, &mut writer, &client, ep.as_ref());
    0
}

#[cfg(test)]
mod tests {
    use super::*;
    use std::io::Cursor;

    fn fake_server(
        token: &'static str,
        mode: &'static str,
    ) -> (String, std::thread::JoinHandle<Vec<String>>) {
        let server = tiny_http::Server::http("127.0.0.1:0").expect("bind");
        let port = server.server_addr().to_ip().map(|a| a.port()).unwrap_or(0);
        let url = format!("http://127.0.0.1:{port}/mcp");
        let h = std::thread::spawn(move || {
            let mut seen = Vec::new();
            for _ in 0..8 {
                let Ok(Some(mut req)) = server.recv_timeout(Duration::from_secs(3)) else {
                    break;
                };
                let mut body = String::new();
                let _ = req.as_reader().read_to_string(&mut body);
                let auth = req
                    .headers()
                    .iter()
                    .find(|h| h.field.equiv("Authorization"))
                    .map(|h| h.value.as_str().to_string())
                    .unwrap_or_default();
                let hv = |name: &'static str| {
                    req.headers()
                        .iter()
                        .find(|h| h.field.equiv(name))
                        .map(|h| h.value.as_str().to_string())
                        .unwrap_or_default()
                };
                // 记录形态:`<auth> <body> | v=<版本头> m=<Mcp-Method> n=<Mcp-Name> s=<会话头>`
                seen.push(format!(
                    "{} {} | v={} m={} n={} s={}",
                    auth,
                    body.trim(),
                    hv("MCP-Protocol-Version"),
                    hv("Mcp-Method"),
                    hv("Mcp-Name"),
                    hv("Mcp-Session-Id")
                ));
                let v: Value = serde_json::from_str(&body).unwrap_or(Value::Null);
                let id = v.get("id").cloned().unwrap_or(Value::Null);
                if auth != format!("Bearer {token}") {
                    let _ =
                        req.respond(tiny_http::Response::from_string("{}").with_status_code(401));
                    continue;
                }
                if id.is_null() {
                    let _ = req.respond(tiny_http::Response::empty(202));
                    continue;
                }
                if mode == "modern404" {
                    let _ = req.respond(tiny_http::Response::from_string(json!({ "jsonrpc": "2.0", "id": id, "error": { "code": -32601, "message": "method not found" } }).to_string()).with_status_code(404));
                    continue;
                }
                if mode == "modern400" {
                    let _ = req.respond(tiny_http::Response::from_string(json!({ "jsonrpc": "2.0", "id": id, "error": { "code": -32022, "message": "Unsupported protocol version", "data": { "supported": ["2026-07-28"], "requested": "2099-01-01" } } }).to_string()).with_status_code(400));
                    continue;
                }
                let out = match mode {
                    "garbage" => "not json".to_string(),
                    _ => json!({ "jsonrpc": "2.0", "id": id, "result": { "ok": true, "echo": v.get("method").cloned().unwrap_or(Value::Null) } }).to_string(),
                };
                let mut resp = tiny_http::Response::from_string(out);
                if let Ok(h) = tiny_http::Header::from_bytes(&b"Mcp-Session-Id"[..], &b"sess-1"[..])
                {
                    resp.add_header(h);
                }
                let _ = req.respond(resp);
            }
            seen
        });
        (url, h)
    }

    #[test]
    fn parse_endpoint_only_accepts_loopback_with_token() {
        assert!(parse_endpoint("nope").is_err());
        assert!(
            parse_endpoint(r#"{"url":"http://evil.example/mcp","token":"0123456789abcdef"}"#)
                .is_err()
        );
        assert!(parse_endpoint(r#"{"url":"http://127.0.0.1:39991/mcp","token":"short"}"#).is_err());
        let ep = parse_endpoint(
            r#"{"url":"http://127.0.0.1:39991/mcp","token":"0123456789abcdef","pid":42}"#,
        )
        .unwrap();
        assert_eq!(ep.url, "http://127.0.0.1:39991/mcp");
        assert_eq!(ep.pid, Some(42));
    }

    #[test]
    fn read_line_bounded_handles_crlf_eof_and_oversize() {
        let mut c = Cursor::new(b"abc\r\ndef\n".to_vec());
        assert_eq!(
            read_line_bounded(&mut c, 64).unwrap(),
            Some(b"abc".to_vec())
        );
        assert_eq!(
            read_line_bounded(&mut c, 64).unwrap(),
            Some(b"def".to_vec())
        );
        assert_eq!(read_line_bounded(&mut c, 64).unwrap(), None);
        let mut tail = Cursor::new(b"no-newline".to_vec());
        assert_eq!(
            read_line_bounded(&mut tail, 64).unwrap(),
            Some(b"no-newline".to_vec())
        );
        let big = format!("{}\nnext\n", "x".repeat(200));
        let mut b = Cursor::new(big.into_bytes());
        let e = read_line_bounded(&mut b, 64).unwrap_err();
        assert_eq!(e.kind(), std::io::ErrorKind::InvalidData);
        assert_eq!(
            read_line_bounded(&mut b, 64).unwrap(),
            Some(b"next".to_vec())
        );
    }

    #[test]
    fn serve_forwards_requests_drops_notifications_and_rejects_bad_lines() {
        let (url, h) = fake_server("0123456789abcdef", "ok");
        let ep = Endpoint {
            url,
            token: "0123456789abcdef".into(),
            pid: None,
        };
        let client = build_client().unwrap();
        let input = concat!(
            "{\"jsonrpc\":\"2.0\",\"id\":1,\"method\":\"ping\"}\n",
            "{\"jsonrpc\":\"2.0\",\"method\":\"notifications/initialized\"}\n",
            "not json\n",
            "[{\"jsonrpc\":\"2.0\",\"id\":9,\"method\":\"ping\"}]\n",
            "\n",
            "{\"jsonrpc\":\"2.0\",\"id\":2,\"method\":\"tools/list\"}\n"
        );
        let mut r = Cursor::new(input.as_bytes().to_vec());
        let mut out: Vec<u8> = Vec::new();
        let (handled, errors) = serve(&mut r, &mut out, &client, Some(&ep));
        let lines: Vec<String> = String::from_utf8(out)
            .unwrap()
            .lines()
            .map(|s| s.to_string())
            .collect();
        assert_eq!(handled, 5);
        assert_eq!(errors, 2);
        assert_eq!(
            lines.len(),
            4,
            "两条请求各一行 + 两条本地错误;通知与空行零输出:{lines:?}"
        );
        // 请求并发转发、回包按完成先后写出(客户端按 id 配对)⇒ 按内容找,不按位置
        let has = |pred: &dyn Fn(&str) -> bool| lines.iter().filter(|l| pred(l)).count();
        assert_eq!(
            has(&|l| l.contains("\"id\":1") && l.contains("\"echo\":\"ping\"")),
            1
        );
        assert_eq!(has(&|l| l.contains("-32700")), 1);
        assert_eq!(has(&|l| l.contains("-32600")), 1);
        assert_eq!(
            has(&|l| l.contains("\"id\":2") && l.contains("tools/list")),
            1
        );
        // 本地错误由读行主循环当场写出:两条坏行的相对顺序不变
        let pos = |needle: &str| lines.iter().position(|l| l.contains(needle)).unwrap();
        assert!(pos("-32700") < pos("-32600"));
        let seen = h.join().unwrap();
        assert_eq!(
            seen.len(),
            3,
            "服务端收到:ping、通知、tools/list;坏行不转发"
        );
        assert!(seen
            .iter()
            .all(|s| s.starts_with("Bearer 0123456789abcdef ")));
    }

    #[test]
    fn serve_reports_not_running_when_unreachable_or_endpoint_missing() {
        let client = build_client().unwrap();
        let dead = Endpoint {
            url: "http://127.0.0.1:1/mcp".into(),
            token: "0123456789abcdef".into(),
            pid: None,
        };
        let mut r = Cursor::new(b"{\"jsonrpc\":\"2.0\",\"id\":5,\"method\":\"ping\"}\n{\"jsonrpc\":\"2.0\",\"method\":\"notifications/x\"}\n".to_vec());
        let mut out: Vec<u8> = Vec::new();
        let (handled, errors) = serve(&mut r, &mut out, &client, Some(&dead));
        assert_eq!((handled, errors), (2, 1));
        let s = String::from_utf8(out).unwrap();
        assert!(s.contains("-32001") && s.contains("\"id\":5"));
        assert!(!s.contains("0123456789abcdef"), "令牌永不出现在输出里");
        let mut r2 = Cursor::new(b"{\"jsonrpc\":\"2.0\",\"id\":6,\"method\":\"ping\"}\n".to_vec());
        let mut out2: Vec<u8> = Vec::new();
        serve(&mut r2, &mut out2, &client, None);
        assert!(String::from_utf8(out2)
            .unwrap()
            .contains("endpoint file missing"));
    }

    #[test]
    fn serve_turns_garbage_upstream_into_internal_error() {
        let (url, h) = fake_server("0123456789abcdef", "garbage");
        let ep = Endpoint {
            url,
            token: "0123456789abcdef".into(),
            pid: None,
        };
        let client = build_client().unwrap();
        let mut r = Cursor::new(b"{\"jsonrpc\":\"2.0\",\"id\":7,\"method\":\"ping\"}\n".to_vec());
        let mut out: Vec<u8> = Vec::new();
        serve(&mut r, &mut out, &client, Some(&ep));
        assert!(String::from_utf8(out).unwrap().contains("-32603"));
        let _ = h.join();
    }

    // ───────────────────────── [2026-07-28] 双纪元代理 ─────────────────────────
    fn serve_lines(url: &str, token: &'static str, lines: &str) -> String {
        let ep = Endpoint {
            url: url.to_string(),
            token: token.to_string(),
            pid: None,
        };
        let client = reqwest::blocking::Client::builder()
            .timeout(Duration::from_secs(5))
            .no_proxy()
            .build()
            .unwrap();
        let mut input = Cursor::new(lines.as_bytes().to_vec());
        let mut out: Vec<u8> = Vec::new();
        serve(&mut input, &mut out, &client, Some(&ep));
        String::from_utf8_lossy(&out).to_string()
    }

    #[test]
    fn serve_forwards_server_discover_and_injects_modern_headers() {
        let token = "0123456789abcdef";
        let (url, h) = fake_server(token, "ok");
        let m = r#"{"io.modelcontextprotocol/protocolVersion":"2026-07-28","io.modelcontextprotocol/clientInfo":{"name":"claude-desktop","version":"1"},"io.modelcontextprotocol/clientCapabilities":{}}"#;
        let lines = format!(
            "{{\"jsonrpc\":\"2.0\",\"id\":1,\"method\":\"server/discover\",\"params\":{{\"_meta\":{m}}}}}\n{{\"jsonrpc\":\"2.0\",\"id\":2,\"method\":\"tools/call\",\"params\":{{\"name\":\"get_time\",\"arguments\":{{}},\"_meta\":{m}}}}}\n{{\"jsonrpc\":\"2.0\",\"id\":3,\"method\":\"tools/call\",\"params\":{{\"name\":\"查詢\",\"arguments\":{{}},\"_meta\":{m}}}}}\n{{\"jsonrpc\":\"2.0\",\"id\":4,\"method\":\"initialize\",\"params\":{{\"protocolVersion\":\"2025-06-18\"}}}}\n{{\"jsonrpc\":\"2.0\",\"id\":5,\"method\":\"tools/list\"}}\n"
        );
        let out = serve_lines(&url, token, &lines);
        let seen = h.join().unwrap();
        assert_eq!(seen.len(), 5, "{seen:?}");
        // 并发转发 ⇒ 服务端收到的先后不定,按行体找
        let find = |needle: &str| {
            seen.iter()
                .find(|s| s.contains(needle))
                .cloned()
                .unwrap_or_else(|| panic!("缺 {needle}:{seen:?}"))
        };
        let disc = find("\"method\":\"server/discover\"");
        assert!(
            disc.contains("v=2026-07-28 m=server/discover n= s="),
            "{disc}"
        );
        let call = find("\"name\":\"get_time\"");
        assert!(
            call.contains("v=2026-07-28 m=tools/call n=get_time s="),
            "{call}"
        );
        let cjk = find("\"id\":3,");
        assert!(
            cjk.contains("m=tools/call n==?base64?"),
            "非 ASCII 名字须哨兵编码:{cjk}"
        );
        let init = find("\"method\":\"initialize\"");
        assert!(
            init.contains("v=2025-06-18 m= n= s="),
            "旧 initialize 行不带现代头、此前无会话:{init}"
        );
        assert!(init.ends_with("s="), "{init}");
        let legacy = find("\"method\":\"tools/list\"");
        assert!(
            legacy.contains("v=2025-06-18 m= n= s=sess-1"),
            "握手同步做完 ⇒ 之后的旧行必带回会话头:{legacy}"
        );
        assert_eq!(out.lines().count(), 5);
        assert!(!out.contains(token), "令牌零输出");
    }

    #[test]
    fn serve_passes_modern_json_errors_through_verbatim() {
        let token = "0123456789abcdef";
        let m = r#"{"io.modelcontextprotocol/protocolVersion":"2026-07-28"}"#;
        let line = format!("{{\"jsonrpc\":\"2.0\",\"id\":7,\"method\":\"tools/list\",\"params\":{{\"_meta\":{m}}}}}\n");
        let (url, h) = fake_server(token, "modern404");
        let out = serve_lines(&url, token, &line);
        let _ = h.join();
        assert!(out.contains("-32601") && out.contains("\"id\":7"), "{out}");
        let (url2, h2) = fake_server(token, "modern400");
        let out2 = serve_lines(&url2, token, &line);
        let _ = h2.join();
        assert!(
            out2.contains("-32022") && out2.contains("\"supported\""),
            "{out2}"
        );
    }

    #[test]
    fn serve_answers_subscriptions_listen_locally_without_forwarding() {
        let token = "0123456789abcdef";
        let (url, h) = fake_server(token, "ok");
        let m = r#"{"io.modelcontextprotocol/protocolVersion":"2026-07-28"}"#;
        let lines = format!("{{\"jsonrpc\":\"2.0\",\"id\":9,\"method\":\"subscriptions/listen\",\"params\":{{\"notifications\":{{\"toolsListChanged\":true}},\"_meta\":{m}}}}}\n{{\"jsonrpc\":\"2.0\",\"id\":10,\"method\":\"tools/list\",\"params\":{{\"_meta\":{m}}}}}\n");
        let t0 = std::time::Instant::now();
        let out = serve_lines(&url, token, &lines);
        // 只量代理本身(假服务器线程 recv_timeout 3 s 才退出,不算进去)
        let proxied_in = t0.elapsed();
        let seen = h.join().unwrap();
        assert_eq!(seen.len(), 1, "listen 不转发,只有 tools/list 到达:{seen:?}");
        assert!(out.contains("-32601") && out.contains("\"id\":9"), "{out}");
        assert!(
            proxied_in < Duration::from_secs(3),
            "listen 本地应答不得阻塞串行环:{proxied_in:?}"
        );
        // 纯函数向量
        let disc: Value =
            serde_json::from_str("{\"jsonrpc\":\"2.0\",\"id\":1,\"method\":\"server/discover\"}")
                .unwrap();
        assert_eq!(modern_line_headers(&disc).unwrap().version, "2026-07-28");
        let init: Value = serde_json::from_str(&format!("{{\"jsonrpc\":\"2.0\",\"id\":1,\"method\":\"initialize\",\"params\":{{\"_meta\":{m}}}}}")).unwrap();
        assert!(
            modern_line_headers(&init).is_none(),
            "initialize 永远旧纪元"
        );
        let legacy: Value =
            serde_json::from_str("{\"jsonrpc\":\"2.0\",\"id\":1,\"method\":\"tools/list\"}")
                .unwrap();
        assert!(modern_line_headers(&legacy).is_none());
        let rr: Value = serde_json::from_str(&format!("{{\"jsonrpc\":\"2.0\",\"id\":1,\"method\":\"resources/read\",\"params\":{{\"uri\":\"horosa://chart/x\",\"_meta\":{m}}}}}")).unwrap();
        assert_eq!(
            modern_line_headers(&rr).unwrap().name.as_deref(),
            Some("horosa://chart/x")
        );
    }

    // ───────────────────────── 并发转发 / 响应流透传 / 取消路由 ─────────────────────────
    /// 多线程假服务端:每条请求一个线程(慢请求不堵快请求)。name=slow ⇒ 1.5 s 后才回;name=streamy ⇒ 分块响应流(两条进度 + 回包)
    fn mt_server(token: &'static str) -> (String, Arc<Mutex<Vec<String>>>, Arc<AtomicBool>) {
        let server = Arc::new(tiny_http::Server::http("127.0.0.1:0").expect("bind"));
        let port = server.server_addr().to_ip().map(|a| a.port()).unwrap_or(0);
        let url = format!("http://127.0.0.1:{port}/mcp");
        let seen = Arc::new(Mutex::new(Vec::new()));
        let stop = Arc::new(AtomicBool::new(false));
        let (s2, seen2, stop2) = (Arc::clone(&server), Arc::clone(&seen), Arc::clone(&stop));
        std::thread::spawn(move || {
            while !stop2.load(Ordering::SeqCst) {
                let Ok(Some(mut req)) = s2.recv_timeout(Duration::from_millis(100)) else {
                    continue;
                };
                let seen3 = Arc::clone(&seen2);
                std::thread::spawn(move || {
                    let mut body = String::new();
                    let _ = req.as_reader().read_to_string(&mut body);
                    let hv = |name: &'static str| {
                        req.headers()
                            .iter()
                            .find(|h| h.field.equiv(name))
                            .map(|h| h.value.as_str().to_string())
                            .unwrap_or_default()
                    };
                    let auth_ok = hv("Authorization") == format!("Bearer {token}");
                    seen3.lock().unwrap().push(format!(
                        "{} | v={} s={} a={}",
                        body.trim(),
                        hv("MCP-Protocol-Version"),
                        hv("Mcp-Session-Id"),
                        hv("Accept")
                    ));
                    let v: Value = serde_json::from_str(&body).unwrap_or(Value::Null);
                    let id = v.get("id").cloned().unwrap_or(Value::Null);
                    let method = v["method"].as_str().unwrap_or("").to_string();
                    if !auth_ok {
                        let _ = req
                            .respond(tiny_http::Response::from_string("{}").with_status_code(401));
                        return;
                    }
                    if id.is_null() {
                        let _ = req.respond(tiny_http::Response::empty(202));
                        return;
                    }
                    let name = v["params"]["name"].as_str().unwrap_or("").to_string();
                    if name == "slow" {
                        std::thread::sleep(Duration::from_millis(1500));
                    }
                    if name == "streamy" {
                        let tok = v["params"]["_meta"]["progressToken"].clone();
                        let frames = [
                            json!({ "jsonrpc": "2.0", "method": "notifications/progress", "params": { "progressToken": tok, "progress": 1, "total": 2 } }),
                            json!({ "jsonrpc": "2.0", "method": "notifications/progress", "params": { "progressToken": tok, "progress": 2, "total": 2 } }),
                            json!({ "jsonrpc": "2.0", "id": id, "result": { "ok": true, "streamed": true } }),
                        ];
                        let mut w = req.into_writer();
                        let _ = w.write_all(b"HTTP/1.1 200 OK\r\nContent-Type: text/event-stream\r\nTransfer-Encoding: chunked\r\n\r\n");
                        for f in frames.iter() {
                            let data = format!(": keep-alive\n\nevent: message\ndata: {}\n\n", f);
                            let _ =
                                w.write_all(format!("{:X}\r\n{}\r\n", data.len(), data).as_bytes());
                            let _ = w.flush();
                        }
                        let _ = w.write_all(b"0\r\n\r\n");
                        let _ = w.flush();
                        return;
                    }
                    let out = json!({ "jsonrpc": "2.0", "id": id, "result": { "ok": true, "echo": method, "name": name } }).to_string();
                    let mut resp = tiny_http::Response::from_string(out);
                    if method == "initialize" {
                        if let Ok(h) =
                            tiny_http::Header::from_bytes(&b"Mcp-Session-Id"[..], &b"sess-9"[..])
                        {
                            resp.add_header(h);
                        }
                    }
                    let _ = req.respond(resp);
                });
            }
        });
        (url, seen, stop)
    }

    const INIT_LINE: &str = "{\"jsonrpc\":\"2.0\",\"id\":1,\"method\":\"initialize\",\"params\":{\"protocolVersion\":\"2025-06-18\"}}\n";

    #[test]
    fn serve_runs_requests_concurrently_slow_call_does_not_block_fast_one() {
        let token = "0123456789abcdef";
        let (url, _seen, stop) = mt_server(token);
        let lines = format!(
            "{INIT_LINE}{}\n{}\n",
            r#"{"jsonrpc":"2.0","id":2,"method":"tools/call","params":{"name":"slow","arguments":{}}}"#,
            r#"{"jsonrpc":"2.0","id":3,"method":"tools/call","params":{"name":"fast","arguments":{}}}"#
        );
        let t0 = std::time::Instant::now();
        let out = serve_lines(&url, token, &lines);
        let took = t0.elapsed();
        stop.store(true, Ordering::SeqCst);
        let ls: Vec<&str> = out.lines().collect();
        assert_eq!(ls.len(), 3, "{out}");
        let pos = |needle: &str| ls.iter().position(|l| l.contains(needle)).unwrap();
        assert!(
            pos("\"id\":3") < pos("\"id\":2"),
            "快请求先回,不在慢请求后面排队:{out}"
        );
        assert!(
            took < Duration::from_millis(2900),
            "两条并发,总耗时 ≈ 慢的那条:{took:?}"
        );
    }

    #[test]
    fn serve_relays_progress_stream_lines_and_asks_for_sse_only_with_a_token() {
        let token = "0123456789abcdef";
        let (url, seen, stop) = mt_server(token);
        let lines = format!(
            "{INIT_LINE}{}\n{}\n",
            r#"{"jsonrpc":"2.0","id":4,"method":"tools/call","params":{"name":"streamy","arguments":{},"_meta":{"progressToken":"p4"}}}"#,
            r#"{"jsonrpc":"2.0","id":5,"method":"tools/call","params":{"name":"plain","arguments":{}}}"#
        );
        let out = serve_lines(&url, token, &lines);
        stop.store(true, Ordering::SeqCst);
        let msgs: Vec<Value> = out
            .lines()
            .map(|l| serde_json::from_str(l).unwrap())
            .collect();
        let streamed: Vec<&Value> = msgs
            .iter()
            .filter(|m| m["params"]["progressToken"] == "p4" || m["id"] == 4)
            .collect();
        assert_eq!(streamed.len(), 3, "两条进度 + 回包逐行写出:{out}");
        assert_eq!(streamed[0]["method"], "notifications/progress");
        assert_eq!(streamed[1]["params"]["progress"], 2);
        assert_eq!(streamed[2]["result"]["streamed"], true, "回包在进度之后");
        assert!(msgs
            .iter()
            .any(|m| m["id"] == 5 && m["result"]["name"] == "plain"));
        let seen = seen.lock().unwrap();
        let with_tok = seen.iter().find(|s| s.contains("\"streamy\"")).unwrap();
        assert!(
            with_tok.contains("a=application/json, text/event-stream"),
            "{with_tok}"
        );
        assert!(with_tok.contains("s=sess-9"), "握手后带会话头:{with_tok}");
        let plain = seen.iter().find(|s| s.contains("\"plain\"")).unwrap();
        assert!(
            plain.ends_with("a=application/json"),
            "不带令牌的旧行照旧只收 JSON:{plain}"
        );
    }

    #[test]
    fn serve_routes_cancel_to_the_original_lane_and_never_writes_the_cancelled_answer() {
        let token = "0123456789abcdef";
        let (url, seen, stop) = mt_server(token);
        let m = r#"{"io.modelcontextprotocol/protocolVersion":"2026-07-28","io.modelcontextprotocol/clientInfo":{"name":"claude-desktop","version":"1"}}"#;
        let lines = format!(
            "{INIT_LINE}{}\n{}\n{}\n{}\n",
            r#"{"jsonrpc":"2.0","id":6,"method":"tools/call","params":{"name":"slow","arguments":{}}}"#,
            format!("{{\"jsonrpc\":\"2.0\",\"id\":7,\"method\":\"tools/call\",\"params\":{{\"name\":\"slow\",\"arguments\":{{}},\"_meta\":{m}}}}}"),
            r#"{"jsonrpc":"2.0","method":"notifications/cancelled","params":{"requestId":6,"reason":"user"}}"#,
            r#"{"jsonrpc":"2.0","method":"notifications/cancelled","params":{"requestId":7}}"#
        );
        let out = serve_lines(&url, token, &lines);
        stop.store(true, Ordering::SeqCst);
        assert!(
            !out.contains("\"id\":6") && !out.contains("\"id\":7"),
            "被取消的请求一个字也不写:{out}"
        );
        assert_eq!(out.lines().count(), 1, "只有握手回包:{out}");
        let seen = seen.lock().unwrap();
        let legacy_cancel = seen
            .iter()
            .find(|s| s.contains("notifications/cancelled") && s.contains("\"requestId\":6"))
            .unwrap_or_else(|| panic!("旧纪元取消未转发:{seen:?}"));
        assert!(
            legacy_cancel.contains("s=sess-9"),
            "旧纪元取消带原请求的会话头:{legacy_cancel}"
        );
        let modern_cancel = seen
            .iter()
            .find(|s| s.contains("notifications/cancelled") && s.contains("\"requestId\":7"))
            .unwrap_or_else(|| panic!("现代取消未转发:{seen:?}"));
        assert!(
            modern_cancel.contains("v=2026-07-28"),
            "现代取消走现代头:{modern_cancel}"
        );
        assert!(
            modern_cancel.contains("claude-desktop"),
            "补上原请求的客户端身份:{modern_cancel}"
        );
        assert!(
            !modern_cancel.contains("s=sess"),
            "现代行永不带会话头:{modern_cancel}"
        );
    }

    #[test]
    fn request_timeout_follows_tool_budget() {
        let call = |meta: Value| json!({ "method": "tools/call", "params": { "name": "x", "_meta": meta } });
        assert_eq!(
            request_timeout_for(&call(json!({}))),
            Duration::from_secs(130)
        );
        assert_eq!(
            request_timeout_for(&call(json!({ "timeoutMs": 180000 }))),
            Duration::from_secs(190),
            "长预算不再被代理 120 s 先断"
        );
        assert_eq!(
            request_timeout_for(&call(json!({ "timeoutMs": 99999999 }))),
            Duration::from_secs(610)
        );
        assert_eq!(
            request_timeout_for(&json!({ "method": "resources/read" })),
            Duration::from_secs(30)
        );
    }

    /// 🔴 旧实现按前缀判回环:`http://127.0.0.1:1@evil.example/mcp` 的主机其实是 evil.example(127.0.0.1:1 是用户信息),
    /// 令牌会被发去别处。现在按 URL 解析:只认 http、回环主机、不带用户信息。
    #[test]
    fn parse_endpoint_rejects_userinfo_and_lookalike_hosts() {
        let ep = |url: &str| {
            parse_endpoint(&format!(
                r#"{{"url":"{}","token":"0123456789abcdef","pid":42}}"#,
                url
            ))
        };
        for bad in [
            "http://127.0.0.1:1@evil.example/mcp",
            "http://user@127.0.0.1:39991/mcp",
            "http://user:pw@localhost:39991/mcp",
            "http://127.0.0.1.evil.example:39991/mcp",
            "http://localhost.evil.example:39991/mcp",
            "https://127.0.0.1:39991/mcp",
            "http://10.0.0.1:39991/mcp",
            "file:///tmp/x",
        ] {
            assert!(ep(bad).is_err(), "{} 必须被拒", bad);
        }
        for good in [
            "http://127.0.0.1:39991/mcp",
            "http://localhost:39991/mcp",
            "http://[::1]:39991/mcp",
        ] {
            assert!(ep(good).is_ok(), "{} 应放行", good);
        }
    }

    fn health_server(pid: u64) -> (String, std::thread::JoinHandle<Vec<String>>) {
        let server = tiny_http::Server::http("127.0.0.1:0").expect("bind");
        let port = server.server_addr().to_ip().map(|a| a.port()).unwrap_or(0);
        let h = std::thread::spawn(move || {
            let mut seen = Vec::new();
            while let Ok(Some(req)) = server.recv_timeout(Duration::from_millis(800)) {
                let auth = req.headers().iter().any(|h| h.field.equiv("Authorization"));
                seen.push(format!("{} auth={}", req.url(), auth));
                let body = json!({ "app": "horosa", "pid": pid }).to_string();
                let _ = req.respond(tiny_http::Response::from_string(body));
            }
            seen
        });
        (format!("http://127.0.0.1:{port}/mcp"), h)
    }

    /// 带令牌之前的端点核对:进程活着且健康探针回的进程号一致才算数;陈旧端点(进程不在 / 端口换了主人)一律不过。
    #[test]
    fn verify_endpoint_requires_live_pid_and_matching_health() {
        let client = build_client().unwrap();
        let me = std::process::id();
        let (url, h) = health_server(me as u64);
        let ok = Endpoint {
            url: url.clone(),
            token: "0123456789abcdef".into(),
            pid: Some(me),
        };
        let health = verify_endpoint(&client, &ok, Duration::from_secs(2)).expect("应通过");
        assert_eq!(health["pid"], json!(me));
        let no_pid = Endpoint {
            pid: None,
            ..ok.clone()
        };
        assert_eq!(
            verify_endpoint(&client, &no_pid, Duration::from_secs(2)).unwrap_err(),
            EndpointCheck::NoPid
        );
        let seen = h.join().unwrap();
        assert!(
            seen.iter().all(|l| l == "/healthz auth=false"),
            "核对只打不带令牌的健康探针:{:?}",
            seen
        );
        // 进程号对不上(端口被别的程序占了):探针回的是另一个进程
        let (url2, h2) = health_server(me as u64 + 1);
        let other = Endpoint {
            url: url2,
            token: "0123456789abcdef".into(),
            pid: Some(me),
        };
        assert_eq!(
            verify_endpoint(&client, &other, Duration::from_secs(2)).unwrap_err(),
            EndpointCheck::Mismatch
        );
        let _ = h2.join();
        // 端点文件里的进程已不在:连探针都不发
        let mut dead = std::process::Command::new("/usr/bin/true").spawn().unwrap();
        let dead_pid = dead.id();
        let _ = dead.wait();
        let gone = Endpoint {
            url,
            token: "0123456789abcdef".into(),
            pid: Some(dead_pid),
        };
        assert_eq!(
            verify_endpoint(&client, &gone, Duration::from_secs(2)).unwrap_err(),
            EndpointCheck::PidDead
        );
    }
}
