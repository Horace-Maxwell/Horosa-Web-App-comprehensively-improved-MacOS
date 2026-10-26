//! 终端命令行:`<App 二进制> --horosa-cli <子命令> …`(安装终端命令后即 `horosa …`)。
//! 与外部智能体客户端同一条路:读本机服务的端点文件(地址 + 令牌)→ 经回环地址发 MCP JSON-RPC 到 `/mcp`;
//! 页面侧调用方名恒为 `cli`(外部审批键 `mcp:cli`、限流桶 `cli`),工具面 / 审批 / 上限 / 撤销与 MCP 客户端完全相同。
//! 零界面:main() 在建任何窗口之前分流到这里,并以本模块返回的退出码退出 —— 认不出的子命令也只打用法,绝不落到拉起界面。
//! 退出码:0 成功 · 1 工具回报失败 · 2 用法错 · 3 本机服务没开 / 连不上 · 4 令牌不对 · 5 其它失败(含本机服务响应超时)· 130 Ctrl-C 取消。
use crate::mcp_stdio::{
    build_client, parse_endpoint, verify_endpoint, Endpoint, EndpointCheck, VERIFY_TIMEOUT,
};
use serde_json::{json, Map, Value};
use std::io::{BufRead, BufReader, Read, Write};
use std::path::{Path, PathBuf};
use std::sync::atomic::{AtomicBool, AtomicU64, Ordering};
use std::sync::mpsc;
use std::time::Duration;

pub const CLI_FLAG: &str = "--horosa-cli";
/// 页面侧的调用方名(外部审批键 `mcp:cli`、限流桶都按它分)
pub const CLI_CLIENT_NAME: &str = "cli";
/// 终端命令垫片:`~/.local/bin/horosa`,首行注释带此标记;不带标记的同名文件一律不碰
pub const SHIM_NAME: &str = "horosa";
pub const SHIM_MARKER: &str = "horosa-cli-shim";
pub const ENDPOINT_ENV: &str = "HOROSA_MCP_ENDPOINT";

pub const EXIT_OK: i32 = 0;
pub const EXIT_TOOL_ERROR: i32 = 1;
pub const EXIT_USAGE: i32 = 2;
pub const EXIT_NOT_RUNNING: i32 = 3;
pub const EXIT_AUTH: i32 = 4;
pub const EXIT_FAILED: i32 = 5;
pub const EXIT_INTERRUPTED: i32 = 130;

const NOT_RUNNING_HINT: &str =
    "本机服务没开:在星阙「AI 分析 › 进阶 › 外部连接」打开「外部智能体连接」(行动能力总开关也要开)";
const TIMEOUT_HINT: &str = "本机服务响应超时";

/// 常用读操作的简写:子命令 → 工具名(可带一个位置参数 = 该工具的主参数)
pub const SHORTCUTS: [(&str, &str, Option<&str>); 6] = [
    ("records", "list_records", Some("query")),
    ("tasks", "list_tasks", None),
    ("context", "get_current_context", None),
    ("proposals", "list_proposals", None),
    ("actions", "list_actions", None),
    ("materials", "search_materials", Some("query")),
];

static RPC_SEQ: AtomicU64 = AtomicU64::new(1);
static INTERRUPTED: AtomicBool = AtomicBool::new(false);

#[derive(Debug, Clone, PartialEq, Default)]
pub struct Options {
    pub json: bool,
    pub endpoint: Option<PathBuf>,
    pub timeout_secs: Option<u64>,
    /// None = 跟随终端(标准错误是终端才打进度)
    pub progress: Option<bool>,
    /// 写入类调用的幂等键(同键同参重试回放、换参 E_IDEMPOTENCY_CONFLICT;与 MCP `_meta.idempotencyKey`、REST `Idempotency-Key` 同义)
    pub idempotency_key: Option<String>,
}

#[derive(Debug, Clone, PartialEq)]
pub enum Command {
    Help(Option<String>),
    Version,
    Status,
    Tools,
    Describe(String),
    Call {
        tool: String,
        args: Value,
        stdin: bool,
    },
    Resources {
        cursor: Option<String>,
    },
    Templates,
    Read(String),
    Prompts {
        cursor: Option<String>,
    },
    Prompt {
        name: String,
        args: Value,
    },
    Endpoint,
}

pub fn usage() -> String {
    let mut s = String::from(
        "星阙终端命令(与外部智能体客户端同一套工具、同一审批与上限;要先在星阙里打开本机服务)\n\n\
用法: horosa <子命令> [参数] [--json] [--timeout 秒] [--progress | --no-progress] [--endpoint 端点文件]\n\n\
子命令:\n\
  status                      本机服务是否在跑(地址 / 版本 / 工具件数)\n\
  tools                       列出全部工具(只读 / 写入)\n\
  describe <工具>             某件工具的说明与参数结构\n\
  call <工具> [参数…]         调用任意工具;参数 = JSON 对象 / k=v(字符串)/ k:=JSON / -(从标准输入读 JSON)\n\
  call … --idempotency-key K  写入类:同一个键重试不重复写(同键换参被拒)\n\
  resources [--cursor C]      列出资源(命盘 / 事盘 / 资料 / 任务 / 操作手册)\n\
  templates                   资源模版\n\
  read <资源地址>             读资源正文(如 horosa://chart/local-…)\n\
  prompts [--cursor C]        列出提示(使用指南 / 技法提示卡 / 技能包)\n\
  prompt <名称> [k=v…]        取一条提示的消息\n\
  endpoint                    显示正在用的端点文件路径\n\
  version                     版本\n\
  help [子命令]               本说明\n\n\
简写(= call 对应工具):\n",
    );
    for (cmd, tool, primary) in SHORTCUTS.iter() {
        let arg = primary.map(|p| format!(" [{}]", p)).unwrap_or_default();
        s.push_str(&format!(
            "  {:<28}= call {}\n",
            format!("{}{}", cmd, arg),
            tool
        ));
    }
    s.push_str(
        "\n例:\n\
  horosa records 张\n\
  horosa call cast_technique source:='{\"type\":\"record\",\"cid\":\"local-1\"}' technique=bazi\n\
  horosa call create_chart_record birth='1990-01-01 08:00' place=北京 gender=male name=张三\n\
  echo '{\"query\":\"张\"}' | horosa call list_records -\n\n\
退出码: 0 成功 · 1 工具回报失败 · 2 用法错 · 3 本机服务没开 · 4 令牌不对 · 5 其它失败 · 130 Ctrl-C 取消\n",
    );
    s
}

/// 参数记号 → 工具参数对象:JSON 对象合并;`k=v` = 字符串(页面校验器按参数结构转型);`k:=JSON` = 原样 JSON;`-` = 从标准输入读
pub fn build_arguments(tokens: &[String]) -> Result<(Value, bool), String> {
    let mut obj = Map::new();
    let mut stdin = false;
    for t in tokens {
        if t == "-" {
            stdin = true;
            continue;
        }
        if t.trim_start().starts_with('{') {
            let v: Value =
                serde_json::from_str(t).map_err(|e| format!("参数不是合法 JSON 对象: {}", e))?;
            let Value::Object(m) = v else {
                return Err("参数 JSON 须是对象".to_string());
            };
            obj.extend(m);
            continue;
        }
        if let Some((k, raw)) = t.split_once(":=") {
            if k.is_empty() || k.contains('=') {
                return Err(format!("看不懂的参数「{}」", t));
            }
            let v: Value = serde_json::from_str(raw)
                .map_err(|e| format!("参数 {} 的 JSON 值不合法: {}", k, e))?;
            obj.insert(k.to_string(), v);
            continue;
        }
        if let Some((k, v)) = t.split_once('=') {
            if k.is_empty() {
                return Err(format!("看不懂的参数「{}」", t));
            }
            obj.insert(k.to_string(), Value::String(v.to_string()));
            continue;
        }
        return Err(format!(
            "看不懂的参数「{}」:参数须是 JSON 对象、k=v、k:=JSON 或 -",
            t
        ));
    }
    Ok((Value::Object(obj), stdin))
}

/// 解析 `--horosa-cli` 之后的参数(纯函数):全局开关可放任意位置
fn parse_idempotency_key(v: &str) -> Result<String, String> {
    let k = v.trim();
    if !crate::mcp_server::idempotency_key_ok(k) {
        return Err(format!(
            "--idempotency-key 要 1..{} 字的键",
            crate::mcp_server::IDEMPOTENCY_KEY_MAX
        ));
    }
    Ok(k.to_string())
}

pub fn parse_args(args: &[String]) -> Result<(Options, Command), String> {
    let mut opts = Options::default();
    let mut pos: Vec<String> = Vec::new();
    let mut cursor: Option<String> = None;
    let mut help = false;
    let mut i = 0;
    while i < args.len() {
        let a = &args[i];
        let take_value = |i: &mut usize, name: &str| -> Result<String, String> {
            *i += 1;
            args.get(*i)
                .cloned()
                .ok_or_else(|| format!("{} 后面要跟一个值", name))
        };
        match a.as_str() {
            "--json" => opts.json = true,
            "--progress" => opts.progress = Some(true),
            "--no-progress" | "--quiet" | "-q" => opts.progress = Some(false),
            "-h" | "--help" => help = true,
            "--version" | "-V" => return Ok((opts, Command::Version)),
            "--endpoint" => opts.endpoint = Some(PathBuf::from(take_value(&mut i, "--endpoint")?)),
            "--timeout" => {
                opts.timeout_secs = Some(parse_timeout(&take_value(&mut i, "--timeout")?)?)
            }
            "--cursor" => cursor = Some(take_value(&mut i, "--cursor")?),
            "--idempotency-key" => {
                opts.idempotency_key = Some(parse_idempotency_key(&take_value(
                    &mut i,
                    "--idempotency-key",
                )?)?)
            }
            _ => {
                if let Some(v) = a.strip_prefix("--endpoint=") {
                    opts.endpoint = Some(PathBuf::from(v));
                } else if let Some(v) = a.strip_prefix("--timeout=") {
                    opts.timeout_secs = Some(parse_timeout(v)?);
                } else if let Some(v) = a.strip_prefix("--idempotency-key=") {
                    opts.idempotency_key = Some(parse_idempotency_key(v)?);
                } else if let Some(v) = a.strip_prefix("--cursor=") {
                    cursor = Some(v.to_string());
                } else if a.starts_with("--") {
                    return Err(format!("不认识的选项 {}", a));
                } else {
                    pos.push(a.clone());
                }
            }
        }
        i += 1;
    }
    if help {
        return Ok((opts, Command::Help(pos.first().cloned())));
    }
    let Some(sub) = pos.first().cloned() else {
        return Ok((opts, Command::Help(None)));
    };
    let rest = &pos[1..];
    let need = |n: usize, what: &str| -> Result<(), String> {
        if rest.len() < n {
            Err(format!("{} 要给{}", sub, what))
        } else {
            Ok(())
        }
    };
    let cmd = match sub.as_str() {
        "help" => Command::Help(rest.first().cloned()),
        "version" => Command::Version,
        "status" => Command::Status,
        "tools" => Command::Tools,
        "endpoint" => Command::Endpoint,
        "templates" => Command::Templates,
        "describe" => {
            need(1, "工具名")?;
            Command::Describe(rest[0].clone())
        }
        "call" => {
            need(1, "工具名")?;
            let (args, stdin) = build_arguments(&rest[1..])?;
            Command::Call {
                tool: rest[0].clone(),
                args,
                stdin,
            }
        }
        "resources" => Command::Resources { cursor },
        "prompts" => Command::Prompts { cursor },
        "read" => {
            need(1, "资源地址")?;
            Command::Read(rest[0].clone())
        }
        "prompt" => {
            need(1, "提示名称")?;
            let (args, stdin) = build_arguments(&rest[1..])?;
            if stdin {
                return Err("prompt 不收标准输入参数".to_string());
            }
            Command::Prompt {
                name: rest[0].clone(),
                args,
            }
        }
        other => match SHORTCUTS.iter().find(|(c, _, _)| *c == other) {
            Some((_, tool, primary)) => {
                let mut toks: Vec<String> = Vec::new();
                for (k, t) in rest.iter().enumerate() {
                    let is_kv = t == "-" || t.starts_with('{') || t.contains('=');
                    match (k, is_kv, primary) {
                        (0, false, Some(p)) => toks.push(format!("{}={}", p, t)),
                        _ => toks.push(t.clone()),
                    }
                }
                let (args, stdin) = build_arguments(&toks)?;
                Command::Call {
                    tool: (*tool).to_string(),
                    args,
                    stdin,
                }
            }
            None => return Err(format!("不认识的子命令 {}(horosa help 看全部)", other)),
        },
    };
    Ok((opts, cmd))
}

fn parse_timeout(v: &str) -> Result<u64, String> {
    match v.trim().parse::<u64>() {
        Ok(n) if (1..=600).contains(&n) => Ok(n),
        _ => Err("--timeout 要 1..600 之间的秒数".to_string()),
    }
}

/// 端点文件缺省位置:环境变量 `HOROSA_MCP_ENDPOINT` > 本应用配置目录(与壳写端点文件的 app_config_dir 同一处)
pub fn default_endpoint_path() -> Option<PathBuf> {
    if let Ok(p) = std::env::var(ENDPOINT_ENV) {
        if !p.trim().is_empty() {
            return Some(PathBuf::from(p.trim()));
        }
    }
    config_base().map(|d| {
        d.join(crate::APP_IDENTIFIER)
            .join(crate::mcp_server::MCP_ENDPOINT_FILE)
    })
}

#[cfg(target_os = "macos")]
fn config_base() -> Option<PathBuf> {
    std::env::var_os("HOME").map(|h| PathBuf::from(h).join("Library/Application Support"))
}
#[cfg(target_os = "windows")]
fn config_base() -> Option<PathBuf> {
    std::env::var_os("APPDATA").map(PathBuf::from)
}
#[cfg(not(any(target_os = "macos", target_os = "windows")))]
fn config_base() -> Option<PathBuf> {
    std::env::var_os("XDG_CONFIG_HOME")
        .map(PathBuf::from)
        .or_else(|| std::env::var_os("HOME").map(|h| PathBuf::from(h).join(".config")))
}

// ───────────────────────── 传输:一条 JSON-RPC(可带进度流)─────────────────────────

#[derive(Debug, Clone, PartialEq)]
pub enum CliError {
    NotRunning(String),
    Auth(String),
    Rpc {
        code: i64,
        message: String,
    },
    Failed(String),
    /// 连上了但等不到回应(与「没开」分开报:服务在跑,只是忙或卡住)
    Timeout,
    Interrupted,
}

/// 发送 / 读回体出错的归类:超时单独报,其余(连接被拒等)= 服务没开
fn transport_error(e: reqwest::Error) -> CliError {
    if e.is_timeout() {
        CliError::Timeout
    } else {
        CliError::NotRunning(NOT_RUNNING_HINT.to_string())
    }
}

impl CliError {
    pub fn exit_code(&self) -> i32 {
        match self {
            CliError::NotRunning(_) => EXIT_NOT_RUNNING,
            CliError::Auth(_) => EXIT_AUTH,
            CliError::Rpc { .. } | CliError::Failed(_) | CliError::Timeout => EXIT_FAILED,
            CliError::Interrupted => EXIT_INTERRUPTED,
        }
    }
    pub fn message(&self) -> String {
        match self {
            CliError::NotRunning(m) => m.clone(),
            CliError::Auth(m) => m.clone(),
            CliError::Rpc { code, message } => format!("{}(错误码 {})", message, code),
            CliError::Failed(m) => m.clone(),
            CliError::Timeout => TIMEOUT_HINT.to_string(),
            CliError::Interrupted => "已取消".to_string(),
        }
    }
}

enum Msg {
    Progress(Value),
    Done(Result<Value, CliError>),
}

#[derive(Clone)]
pub struct Conn {
    client: reqwest::blocking::Client,
    ep: Endpoint,
}

impl Conn {
    pub fn new(ep: Endpoint) -> Option<Conn> {
        build_client().map(|client| Conn { client, ep })
    }

    /// 健康探针(不带令牌)+ 带令牌之前先核对端点:端点文件里的进程活着、健康探针回的进程号一致;否则按「服务没开」报,令牌不发出去。
    /// 成功回健康探针的 JSON。
    pub fn verify(&self) -> Result<Value, CliError> {
        verify_endpoint(&self.client, &self.ep, VERIFY_TIMEOUT).map_err(|e| match e {
            EndpointCheck::Timeout => CliError::Timeout,
            EndpointCheck::NoPid
            | EndpointCheck::PidDead
            | EndpointCheck::Unreachable
            | EndpointCheck::Mismatch => CliError::NotRunning(NOT_RUNNING_HINT.to_string()),
        })
    }

    fn post(
        &self,
        body: &Value,
        timeout: Option<Duration>,
    ) -> Result<reqwest::blocking::Response, CliError> {
        let mut rb = self
            .client
            .post(&self.ep.url)
            .header("Authorization", format!("Bearer {}", self.ep.token))
            .header("Content-Type", "application/json")
            .header("Accept", "application/json, text/event-stream")
            .body(body.to_string());
        if let Some(t) = timeout {
            rb = rb.timeout(t);
        }
        let resp = rb.send().map_err(transport_error)?;
        let status = resp.status().as_u16();
        if status == 401 {
            return Err(CliError::Auth(
                "令牌不对:星阙里轮换过令牌,或端点文件不是这台机器上正在跑的那份(用 horosa endpoint 看路径)".to_string(),
            ));
        }
        if status == 403 {
            let t = resp.text().unwrap_or_default();
            return Err(CliError::Auth(format!("被拒绝(HTTP 403):{}", t.trim())));
        }
        Ok(resp)
    }

    /// 发一条请求;`on_progress` 收进度通知的 params。回 result,或错误(JSON-RPC 错误映射为 Rpc)
    pub fn rpc(
        &self,
        id: &str,
        method: &str,
        params: Value,
        timeout: Option<Duration>,
        on_progress: &mut dyn FnMut(&Value),
    ) -> Result<Value, CliError> {
        let body = json!({ "jsonrpc": "2.0", "id": id, "method": method, "params": params });
        let resp = self.post(&body, timeout)?;
        let status = resp.status().as_u16();
        let is_sse = resp
            .headers()
            .get("content-type")
            .and_then(|h| h.to_str().ok())
            .map(|c| c.to_ascii_lowercase().starts_with("text/event-stream"))
            .unwrap_or(false);
        let answer = if is_sse {
            read_sse_answer(resp, id, on_progress).ok_or_else(|| {
                CliError::Failed(format!("响应流没有回包就结束了(HTTP {})", status))
            })?
        } else {
            let text = resp.text().map_err(transport_error)?;
            serde_json::from_str::<Value>(&text).map_err(|_| {
                CliError::Failed(format!(
                    "回体不是 JSON(HTTP {}):{}",
                    status,
                    clip(text.trim(), 200)
                ))
            })?
        };
        if let Some(e) = answer.get("error") {
            let code = e.get("code").and_then(|c| c.as_i64()).unwrap_or(-32603);
            let message = e
                .get("message")
                .and_then(|m| m.as_str())
                .unwrap_or("error")
                .to_string();
            if code == -32001 {
                return Err(CliError::NotRunning(format!(
                    "{}({})",
                    NOT_RUNNING_HINT, message
                )));
            }
            return Err(CliError::Rpc { code, message });
        }
        Ok(answer.get("result").cloned().unwrap_or(Value::Null))
    }

    /// 旧纪元取消:按同一请求 id 发 notifications/cancelled(无会话 = 匿名空间,与服务端同键)
    pub fn cancel(&self, id: &str) {
        let body = json!({ "jsonrpc": "2.0", "method": "notifications/cancelled", "params": { "requestId": id, "reason": "用户在终端按了 Ctrl-C" } });
        let _ = self.post(&body, Some(Duration::from_secs(3)));
    }
}

/// 响应流:逐个事件取 data 行;进度通知回调,带同一 id 的消息 = 回包
pub fn read_sse_answer<R: Read>(
    r: R,
    id: &str,
    on_progress: &mut dyn FnMut(&Value),
) -> Option<Value> {
    let mut reader = BufReader::new(r);
    let mut data: Vec<String> = Vec::new();
    let want = Value::String(id.to_string());
    loop {
        let mut l = String::new();
        match reader.read_line(&mut l) {
            Ok(0) | Err(_) => return None,
            Ok(_) => {}
        }
        let t = l.trim_end_matches(['\r', '\n']);
        if t.is_empty() {
            if data.is_empty() {
                continue;
            }
            let payload = data.join("\n");
            data.clear();
            let Ok(v) = serde_json::from_str::<Value>(&payload) else {
                continue;
            };
            if v.get("method").and_then(|m| m.as_str()) == Some("notifications/progress") {
                if let Some(p) = v.get("params") {
                    on_progress(p);
                }
                continue;
            }
            if v.get("method").is_none() && v.get("id") == Some(&want) {
                return Some(v);
            }
            continue;
        }
        if let Some(rest) = t.strip_prefix("data:") {
            data.push(rest.strip_prefix(' ').unwrap_or(rest).to_string());
        }
    }
}

// ───────────────────────── 人读输出(纯函数)─────────────────────────

fn clip(s: &str, max: usize) -> String {
    if s.chars().count() <= max {
        return s.to_string();
    }
    let mut out: String = s.chars().take(max).collect();
    out.push('…');
    out
}

fn first_line(s: &str) -> &str {
    s.lines().next().unwrap_or("").trim()
}

pub fn fmt_tools(tools: &[Value]) -> String {
    let width = tools
        .iter()
        .filter_map(|t| t.get("name").and_then(|n| n.as_str()))
        .map(|n| n.len())
        .max()
        .unwrap_or(0);
    let mut out = String::new();
    for t in tools {
        let name = t.get("name").and_then(|n| n.as_str()).unwrap_or("");
        let ro = t
            .pointer("/annotations/readOnlyHint")
            .and_then(|v| v.as_bool())
            == Some(true);
        let title = t.get("title").and_then(|n| n.as_str()).unwrap_or("");
        let desc = first_line(t.get("description").and_then(|n| n.as_str()).unwrap_or(""));
        let summary = if title.is_empty() {
            clip(desc, 60)
        } else {
            format!("{} — {}", title, clip(desc, 48))
        };
        out.push_str(&format!(
            "{:<width$}  {}  {}\n",
            name,
            if ro { "只读" } else { "写入" },
            summary,
            width = width
        ));
    }
    out.push_str(&format!(
        "共 {} 件(horosa describe <工具> 看参数)\n",
        tools.len()
    ));
    out
}

pub fn fmt_describe(t: &Value) -> String {
    let mut out = String::new();
    let name = t.get("name").and_then(|n| n.as_str()).unwrap_or("");
    let title = t.get("title").and_then(|n| n.as_str()).unwrap_or("");
    out.push_str(&format!(
        "{}{}\n\n",
        name,
        if title.is_empty() {
            String::new()
        } else {
            format!(" · {}", title)
        }
    ));
    if let Some(d) = t.get("description").and_then(|n| n.as_str()) {
        out.push_str(d.trim());
        out.push_str("\n\n");
    }
    out.push_str("参数结构:\n");
    out.push_str(
        &serde_json::to_string_pretty(t.get("inputSchema").unwrap_or(&json!({})))
            .unwrap_or_default(),
    );
    out.push('\n');
    if let Some(o) = t.get("outputSchema") {
        out.push_str("\n回包结构(--json 时的 structuredContent):\n");
        out.push_str(&serde_json::to_string_pretty(o).unwrap_or_default());
        out.push('\n');
    }
    out
}

/// 工具回包 → (正文, 是否失败):正文 = 各 text 段拼接;没有 text 段时退回结构化结果
pub fn fmt_tool_result(r: &Value) -> (String, bool) {
    let is_error = r.get("isError").and_then(|v| v.as_bool()).unwrap_or(false);
    let texts: Vec<&str> = r
        .get("content")
        .and_then(|c| c.as_array())
        .map(|a| {
            a.iter()
                .filter_map(|x| x.get("text").and_then(|t| t.as_str()))
                .collect()
        })
        .unwrap_or_default();
    let mut body = texts.join("\n");
    if body.trim().is_empty() {
        if let Some(s) = r.get("structuredContent") {
            body = serde_json::to_string_pretty(s).unwrap_or_default();
        }
    }
    if !body.ends_with('\n') {
        body.push('\n');
    }
    (body, is_error)
}

pub fn fmt_list(items: &[Value], key: &str, label: &str, next: Option<&str>) -> String {
    let mut out = String::new();
    for it in items {
        let k = it.get(key).and_then(|v| v.as_str()).unwrap_or("");
        let name = it.get("name").and_then(|v| v.as_str()).unwrap_or("");
        let desc = first_line(it.get("description").and_then(|v| v.as_str()).unwrap_or(""));
        let tail = match (name.is_empty() || name == k, desc.is_empty()) {
            (true, true) => String::new(),
            (true, false) => format!("  {}", clip(desc, 60)),
            (false, true) => format!("  {}", name),
            (false, false) => format!("  {} — {}", name, clip(desc, 48)),
        };
        out.push_str(&format!("{}{}\n", k, tail));
    }
    out.push_str(&format!("共 {} 条{}\n", items.len(), label));
    if let Some(c) = next {
        out.push_str(&format!("还有下一页:加 --cursor {}\n", c));
    }
    out
}

pub fn fmt_contents(r: &Value) -> String {
    let mut out = String::new();
    for c in r
        .get("contents")
        .and_then(|c| c.as_array())
        .cloned()
        .unwrap_or_default()
    {
        if let Some(t) = c.get("text").and_then(|t| t.as_str()) {
            out.push_str(t);
            if !t.ends_with('\n') {
                out.push('\n');
            }
        } else if c.get("blob").is_some() {
            out.push_str(&format!(
                "[二进制内容 {}]\n",
                c.get("mimeType").and_then(|m| m.as_str()).unwrap_or("")
            ));
        }
    }
    out
}

pub fn fmt_prompt(r: &Value) -> String {
    let mut out = String::new();
    if let Some(d) = r.get("description").and_then(|d| d.as_str()) {
        out.push_str(&format!("# {}\n\n", d));
    }
    for m in r
        .get("messages")
        .and_then(|m| m.as_array())
        .cloned()
        .unwrap_or_default()
    {
        let role = m.get("role").and_then(|v| v.as_str()).unwrap_or("");
        let text = m
            .pointer("/content/text")
            .and_then(|v| v.as_str())
            .unwrap_or("");
        out.push_str(&format!("[{}]\n{}\n\n", role, text));
    }
    out
}

pub fn fmt_progress(p: &Value) -> String {
    let n = p.get("progress").and_then(|v| v.as_f64());
    let total = p.get("total").and_then(|v| v.as_f64());
    let msg = p.get("message").and_then(|v| v.as_str()).unwrap_or("");
    let head = match (n, total) {
        (Some(n), Some(t)) => format!("[{}/{}]", trim_num(n), trim_num(t)),
        (Some(n), None) => format!("[{}]", trim_num(n)),
        _ => "[…]".to_string(),
    };
    if msg.is_empty() {
        head
    } else {
        format!("{} {}", head, msg)
    }
}

fn trim_num(v: f64) -> String {
    if v.fract() == 0.0 && v.abs() < 1e15 {
        format!("{}", v as i64)
    } else {
        format!("{}", v)
    }
}

// ───────────────────────── 执行 ─────────────────────────

pub struct CliIo<'a> {
    pub out: &'a mut dyn Write,
    pub err: &'a mut dyn Write,
    pub stdin: &'a mut dyn Read,
    pub err_is_tty: bool,
    pub interrupted: &'a AtomicBool,
}

fn next_id() -> String {
    format!(
        "cli-{}-{}",
        std::process::id(),
        RPC_SEQ.fetch_add(1, Ordering::SeqCst)
    )
}

fn meta_params(mut params: Value, opts: &Options, progress_token: Option<&str>) -> Value {
    let mut meta = json!({ "clientName": CLI_CLIENT_NAME });
    if let Some(t) = opts.timeout_secs {
        meta["timeoutMs"] = json!(t * 1000);
    }
    if let Some(tok) = progress_token {
        meta["progressToken"] = json!(tok);
    }
    if let Some(k) = &opts.idempotency_key {
        meta["idempotencyKey"] = json!(k);
    }
    if let Some(o) = params.as_object_mut() {
        o.insert("_meta".to_string(), meta);
    }
    params
}

/// 带 Ctrl-C 的调用:请求在工作线程里跑,主线程转发进度并看中断位;中断 = 发取消通知、回 Interrupted
fn call_interruptible(
    conn: &Conn,
    method: &str,
    params: Value,
    opts: &Options,
    io: &mut CliIo,
) -> Result<Value, CliError> {
    let id = next_id();
    let show = opts.progress.unwrap_or(io.err_is_tty) && !opts.json;
    let params = meta_params(params, opts, if show { Some(id.as_str()) } else { None });
    let http_timeout = opts.timeout_secs.map(|t| Duration::from_secs(t + 15));
    let (tx, rx) = mpsc::channel::<Msg>();
    let worker = conn.clone();
    let (wid, wmethod) = (id.clone(), method.to_string());
    std::thread::spawn(move || {
        let ptx = tx.clone();
        let mut on_progress = |p: &Value| {
            let _ = ptx.send(Msg::Progress(p.clone()));
        };
        let r = worker.rpc(&wid, &wmethod, params, http_timeout, &mut on_progress);
        let _ = tx.send(Msg::Done(r));
    });
    loop {
        if io.interrupted.load(Ordering::SeqCst) {
            conn.cancel(&id);
            return Err(CliError::Interrupted);
        }
        match rx.recv_timeout(Duration::from_millis(100)) {
            Ok(Msg::Progress(p)) => {
                if show {
                    let _ = writeln!(io.err, "{}", fmt_progress(&p));
                }
            }
            Ok(Msg::Done(r)) => return r,
            Err(mpsc::RecvTimeoutError::Timeout) => {}
            Err(mpsc::RecvTimeoutError::Disconnected) => {
                return Err(CliError::Failed("调用线程意外退出".to_string()))
            }
        }
    }
}

fn simple(conn: &Conn, method: &str, params: Value, opts: &Options) -> Result<Value, CliError> {
    let params = meta_params(params, opts, None);
    conn.rpc(
        &next_id(),
        method,
        params,
        Some(Duration::from_secs(30)),
        &mut |_| {},
    )
}

fn emit_json(io: &mut CliIo, v: &Value) {
    let _ = writeln!(
        io.out,
        "{}",
        serde_json::to_string_pretty(v).unwrap_or_default()
    );
}

fn fail(io: &mut CliIo, e: CliError) -> i32 {
    let _ = writeln!(io.err, "horosa: {}", e.message());
    e.exit_code()
}

pub fn execute(argv: &[String], default_endpoint: Option<PathBuf>, io: &mut CliIo) -> i32 {
    let (opts, cmd) = match parse_args(argv) {
        Ok(x) => x,
        Err(e) => {
            let _ = writeln!(io.err, "horosa: {}\n(horosa help 看用法)", e);
            return EXIT_USAGE;
        }
    };
    match &cmd {
        Command::Help(_) => {
            let _ = write!(io.out, "{}", usage());
            return EXIT_OK;
        }
        Command::Version => {
            let _ = writeln!(io.out, "horosa {}", env!("CARGO_PKG_VERSION"));
            return EXIT_OK;
        }
        _ => {}
    }
    let path = opts.endpoint.clone().or(default_endpoint);
    if cmd == Command::Endpoint {
        match &path {
            Some(p) => {
                let exists = p.exists();
                let _ = writeln!(
                    io.out,
                    "{}{}",
                    p.display(),
                    if exists {
                        ""
                    } else {
                        "(不存在:本机服务没开)"
                    }
                );
                return if exists { EXIT_OK } else { EXIT_NOT_RUNNING };
            }
            None => {
                return fail(
                    io,
                    CliError::Failed("找不到配置目录(HOME 未设置)".to_string()),
                )
            }
        }
    }
    let Some(path) = path else {
        return fail(
            io,
            CliError::Failed("找不到配置目录(HOME 未设置);用 --endpoint 指定端点文件".to_string()),
        );
    };
    let ep = match std::fs::read_to_string(&path) {
        Ok(text) => match parse_endpoint(&text) {
            Ok(ep) => ep,
            Err(e) => {
                return fail(
                    io,
                    CliError::Failed(format!("端点文件不可用({}):{}", path.display(), e)),
                )
            }
        },
        Err(_) => return fail(io, CliError::NotRunning(NOT_RUNNING_HINT.to_string())),
    };
    let Some(conn) = Conn::new(ep) else {
        return fail(io, CliError::Failed("HTTP 客户端建不起来".to_string()));
    };
    // 任何带令牌的请求之前先核对端点(陈旧端点文件 / 端口被别的程序占了 ⇒ 服务没开,令牌不发出去)
    let health = match conn.verify() {
        Ok(h) => h,
        Err(e) => return fail(io, e),
    };
    match cmd {
        Command::Help(_) | Command::Version | Command::Endpoint => EXIT_OK,
        Command::Status => {
            let h = health;
            let tools = match simple(&conn, "tools/list", json!({}), &opts) {
                Ok(r) => r
                    .get("tools")
                    .and_then(|t| t.as_array())
                    .cloned()
                    .unwrap_or_default(),
                Err(e) => return fail(io, e),
            };
            if opts.json {
                emit_json(
                    io,
                    &json!({ "running": true, "url": conn.ep.url, "version": h.get("version").cloned().unwrap_or(Value::Null), "pid": h.get("pid").cloned().unwrap_or(Value::Null), "tools": tools.len() }),
                );
            } else {
                let _ = writeln!(
                    io.out,
                    "运行中 · {} · 版本 {} · 工具 {} 件",
                    conn.ep.url,
                    h.get("version").and_then(|v| v.as_str()).unwrap_or("?"),
                    tools.len()
                );
            }
            EXIT_OK
        }
        Command::Tools => match simple(&conn, "tools/list", json!({}), &opts) {
            Ok(r) => {
                let tools = r
                    .get("tools")
                    .and_then(|t| t.as_array())
                    .cloned()
                    .unwrap_or_default();
                if opts.json {
                    emit_json(io, &json!(tools));
                } else {
                    let _ = write!(io.out, "{}", fmt_tools(&tools));
                }
                EXIT_OK
            }
            Err(e) => fail(io, e),
        },
        Command::Describe(name) => match simple(&conn, "tools/list", json!({}), &opts) {
            Ok(r) => {
                let tools = r
                    .get("tools")
                    .and_then(|t| t.as_array())
                    .cloned()
                    .unwrap_or_default();
                match tools
                    .iter()
                    .find(|t| t.get("name").and_then(|n| n.as_str()) == Some(name.as_str()))
                {
                    Some(t) => {
                        if opts.json {
                            emit_json(io, t);
                        } else {
                            let _ = write!(io.out, "{}", fmt_describe(t));
                        }
                        EXIT_OK
                    }
                    None => {
                        let _ =
                            writeln!(io.err, "horosa: 没有这件工具 {}(horosa tools 看全部)", name);
                        EXIT_USAGE
                    }
                }
            }
            Err(e) => fail(io, e),
        },
        Command::Call { tool, args, stdin } => {
            let mut arguments = args;
            if stdin {
                let mut buf = String::new();
                if io.stdin.read_to_string(&mut buf).is_err() {
                    let _ = writeln!(io.err, "horosa: 读不了标准输入");
                    return EXIT_USAGE;
                }
                let v: Value = match serde_json::from_str(buf.trim()) {
                    Ok(Value::Object(m)) => Value::Object(m),
                    _ => {
                        let _ = writeln!(io.err, "horosa: 标准输入须是一个 JSON 对象");
                        return EXIT_USAGE;
                    }
                };
                // 标准输入打底,命令行上的 k=v 覆盖
                let mut merged = v.as_object().cloned().unwrap_or_default();
                if let Some(o) = arguments.as_object() {
                    for (k, val) in o {
                        merged.insert(k.clone(), val.clone());
                    }
                }
                arguments = Value::Object(merged);
            }
            match call_interruptible(
                &conn,
                "tools/call",
                json!({ "name": tool, "arguments": arguments }),
                &opts,
                io,
            ) {
                Ok(r) => {
                    let (text, is_error) = fmt_tool_result(&r);
                    if opts.json {
                        emit_json(io, &r);
                    } else if is_error {
                        let _ = write!(io.err, "{}", text);
                    } else {
                        let _ = write!(io.out, "{}", text);
                    }
                    if is_error {
                        EXIT_TOOL_ERROR
                    } else {
                        EXIT_OK
                    }
                }
                Err(e) => fail(io, e),
            }
        }
        Command::Resources { cursor } => list_cmd(
            &conn,
            &opts,
            io,
            ("resources/list", "resources", "uri", "资源"),
            cursor,
        ),
        Command::Prompts { cursor } => list_cmd(
            &conn,
            &opts,
            io,
            ("prompts/list", "prompts", "name", "提示"),
            cursor,
        ),
        Command::Templates => match simple(&conn, "resources/templates/list", json!({}), &opts) {
            Ok(r) => {
                if opts.json {
                    emit_json(io, &r);
                } else {
                    let items = r
                        .get("resourceTemplates")
                        .and_then(|v| v.as_array())
                        .cloned()
                        .unwrap_or_default();
                    let _ = write!(
                        io.out,
                        "{}",
                        fmt_list(&items, "uriTemplate", "资源模版", None)
                    );
                }
                EXIT_OK
            }
            Err(e) => fail(io, e),
        },
        Command::Read(uri) => {
            match call_interruptible(&conn, "resources/read", json!({ "uri": uri }), &opts, io) {
                Ok(r) => {
                    if opts.json {
                        emit_json(io, &r);
                    } else {
                        let _ = write!(io.out, "{}", fmt_contents(&r));
                    }
                    EXIT_OK
                }
                Err(e) => fail(io, e),
            }
        }
        Command::Prompt { name, args } => match simple(
            &conn,
            "prompts/get",
            json!({ "name": name, "arguments": args }),
            &opts,
        ) {
            Ok(r) => {
                if opts.json {
                    emit_json(io, &r);
                } else {
                    let _ = write!(io.out, "{}", fmt_prompt(&r));
                }
                EXIT_OK
            }
            Err(e) => fail(io, e),
        },
    }
}

/// 分页清单(资源 / 提示):(方法, 回体键, 每条主键, 中文名)
fn list_cmd(
    conn: &Conn,
    opts: &Options,
    io: &mut CliIo,
    spec: (&str, &str, &str, &str),
    cursor: Option<String>,
) -> i32 {
    let (method, key, field, label) = spec;
    let mut p = json!({});
    if let Some(c) = cursor {
        p["cursor"] = json!(c);
    }
    match simple(conn, method, p, opts) {
        Ok(r) => {
            if opts.json {
                emit_json(io, &r);
            } else {
                let items = r
                    .get(key)
                    .and_then(|v| v.as_array())
                    .cloned()
                    .unwrap_or_default();
                let _ = write!(
                    io.out,
                    "{}",
                    fmt_list(
                        &items,
                        field,
                        label,
                        r.get("nextCursor").and_then(|c| c.as_str())
                    )
                );
            }
            EXIT_OK
        }
        Err(e) => fail(io, e),
    }
}

#[cfg(unix)]
extern "C" fn on_sigint(_: libc::c_int) {
    INTERRUPTED.store(true, Ordering::SeqCst);
}

/// 进程入口(main() 在建窗口之前分流到这里;返回值即退出码)
pub fn run_cli(argv: &[String]) -> i32 {
    #[cfg(unix)]
    unsafe {
        libc::signal(
            libc::SIGINT,
            on_sigint as extern "C" fn(libc::c_int) as libc::sighandler_t,
        );
    }
    let mut out = std::io::stdout();
    let mut err = std::io::stderr();
    let mut stdin = std::io::stdin();
    let err_is_tty = std::io::IsTerminal::is_terminal(&std::io::stderr());
    let mut io = CliIo {
        out: &mut out,
        err: &mut err,
        stdin: &mut stdin,
        err_is_tty,
        interrupted: &INTERRUPTED,
    };
    let code = execute(argv, default_endpoint_path(), &mut io);
    let _ = io.out.flush();
    code
}

// ───────────────────────── 终端命令垫片(~/.local/bin/horosa)─────────────────────────

pub fn default_shim_dir() -> Option<PathBuf> {
    std::env::var_os("HOME").map(|h| PathBuf::from(h).join(".local/bin"))
}

fn sh_quote(s: &str) -> String {
    format!("'{}'", s.replace('\'', "'\\''"))
}

pub fn shim_script(exe: &Path) -> String {
    format!(
        "#!/bin/sh\n# {} — 星阙终端命令(由星阙「外部连接 › 终端命令」写入;可随时在那里移除)\nexec {} {} \"$@\"\n",
        SHIM_MARKER,
        sh_quote(&exe.display().to_string()),
        CLI_FLAG
    )
}

/// 读已装垫片指向的二进制;不是本应用的垫片 → None
pub fn shim_target(text: &str) -> Option<String> {
    if !text.lines().take(3).any(|l| l.contains(SHIM_MARKER)) {
        return None;
    }
    let line = text.lines().find(|l| l.starts_with("exec "))?;
    let rest = line.strip_prefix("exec ")?;
    let suffix = format!(" {} \"$@\"", CLI_FLAG);
    let quoted = rest.strip_suffix(&suffix)?;
    let inner = quoted.strip_prefix('\'')?.strip_suffix('\'')?;
    Some(inner.replace("'\\''", "'"))
}

pub fn shim_status(dir: &Path, exe: &Path) -> Value {
    let path = dir.join(SHIM_NAME);
    let text = std::fs::read_to_string(&path).ok();
    let target = text.as_deref().and_then(shim_target);
    json!({
        "path": path.display().to_string(),
        "installed": target.is_some(),
        "foreign": text.is_some() && target.is_none(),
        "current": target.as_deref() == Some(exe.display().to_string().as_str()),
        "target": target.unwrap_or_default(),
        "binaryPath": exe.display().to_string(),
    })
}

/// 写垫片:同名文件不是本应用写的 → 拒绝(绝不覆盖用户自己的 horosa);临时文件 + 改名;0755
pub fn install_shim(dir: &Path, exe: &Path) -> Result<PathBuf, String> {
    let path = dir.join(SHIM_NAME);
    if let Ok(text) = std::fs::read_to_string(&path) {
        if shim_target(&text).is_none() {
            return Err(format!("{} 已存在且不是星阙写的,不覆盖", path.display()));
        }
    } else if path.exists() {
        return Err(format!("{} 已存在且读不了,不覆盖", path.display()));
    }
    std::fs::create_dir_all(dir).map_err(|e| format!("建目录失败: {}", e.kind()))?;
    let tmp = dir.join(format!(".{}.tmp-{}", SHIM_NAME, std::process::id()));
    std::fs::write(&tmp, shim_script(exe)).map_err(|e| format!("写入失败: {}", e.kind()))?;
    #[cfg(unix)]
    {
        use std::os::unix::fs::PermissionsExt;
        std::fs::set_permissions(&tmp, std::fs::Permissions::from_mode(0o755))
            .map_err(|e| format!("设权限失败: {}", e.kind()))?;
    }
    std::fs::rename(&tmp, &path).map_err(|e| {
        let _ = std::fs::remove_file(&tmp);
        format!("改名失败: {}", e.kind())
    })?;
    Ok(path)
}

/// 移除垫片:只删本应用写的;回是否删了
pub fn remove_shim(dir: &Path) -> Result<bool, String> {
    let path = dir.join(SHIM_NAME);
    let Ok(text) = std::fs::read_to_string(&path) else {
        return Ok(false);
    };
    if shim_target(&text).is_none() {
        return Err(format!("{} 不是星阙写的,不删", path.display()));
    }
    std::fs::remove_file(&path).map_err(|e| format!("删除失败: {}", e.kind()))?;
    Ok(true)
}

/// 壳命令用:当前用户的垫片状态 / 安装 / 移除(都回最新状态;垫片指向正在运行的这份二进制)
pub fn shim_status_now() -> Result<Value, String> {
    let dir = default_shim_dir().ok_or_else(|| "HOME 未设置".to_string())?;
    let exe = std::env::current_exe().map_err(|e| format!("取不到本程序路径: {}", e.kind()))?;
    Ok(shim_status(&dir, &exe))
}
pub fn shim_install_now() -> Result<Value, String> {
    let dir = default_shim_dir().ok_or_else(|| "HOME 未设置".to_string())?;
    let exe = std::env::current_exe().map_err(|e| format!("取不到本程序路径: {}", e.kind()))?;
    install_shim(&dir, &exe)?;
    Ok(shim_status(&dir, &exe))
}
pub fn shim_remove_now() -> Result<Value, String> {
    let dir = default_shim_dir().ok_or_else(|| "HOME 未设置".to_string())?;
    let exe = std::env::current_exe().map_err(|e| format!("取不到本程序路径: {}", e.kind()))?;
    remove_shim(&dir)?;
    Ok(shim_status(&dir, &exe))
}

#[cfg(test)]
mod tests {
    use super::*;

    fn s(v: &[&str]) -> Vec<String> {
        v.iter().map(|x| x.to_string()).collect()
    }

    #[test]
    fn parse_subcommands_flags_and_shortcuts() {
        assert_eq!(parse_args(&s(&[])).unwrap().1, Command::Help(None));
        assert_eq!(parse_args(&s(&["status"])).unwrap().1, Command::Status);
        assert_eq!(parse_args(&s(&["--version"])).unwrap().1, Command::Version);
        let (o, c) = parse_args(&s(&[
            "tools",
            "--json",
            "--timeout",
            "30",
            "--endpoint=/tmp/e.json",
        ]))
        .unwrap();
        assert_eq!(c, Command::Tools);
        assert!(o.json);
        assert_eq!(o.timeout_secs, Some(30));
        assert_eq!(o.endpoint, Some(PathBuf::from("/tmp/e.json")));
        assert_eq!(
            parse_args(&s(&["call", "x", "--no-progress"]))
                .unwrap()
                .0
                .progress,
            Some(false)
        );
        // 简写:首个裸参数 = 主参数;其后 k=v 照常
        let (_, c) = parse_args(&s(&["records", "张", "limit=5"])).unwrap();
        assert_eq!(
            c,
            Command::Call {
                tool: "list_records".into(),
                args: json!({ "query": "张", "limit": "5" }),
                stdin: false
            }
        );
        let (_, c) = parse_args(&s(&["tasks"])).unwrap();
        assert_eq!(
            c,
            Command::Call {
                tool: "list_tasks".into(),
                args: json!({}),
                stdin: false
            }
        );
        assert!(
            matches!(parse_args(&s(&["resources", "--cursor", "o2s"])).unwrap().1, Command::Resources { cursor: Some(ref c) } if c == "o2s")
        );
        assert_eq!(
            parse_args(&s(&["help", "call"])).unwrap().1,
            Command::Help(Some("call".into()))
        );
        // 用法错
        assert!(parse_args(&s(&["nope"])).is_err());
        assert!(parse_args(&s(&["call"])).is_err());
        assert!(parse_args(&s(&["read"])).is_err());
        assert!(parse_args(&s(&["--bogus"])).is_err());
        assert!(parse_args(&s(&["tools", "--timeout", "0"])).is_err());
        assert!(parse_args(&s(&["tools", "--timeout"])).is_err());
    }

    #[test]
    fn idempotency_key_flag_parses_and_lands_in_meta() {
        let (o, _) = parse_args(&s(&["call", "x", "--idempotency-key", " k1 "])).unwrap();
        assert_eq!(o.idempotency_key.as_deref(), Some("k1"));
        let (o, _) = parse_args(&s(&["call", "x", "--idempotency-key=k2"])).unwrap();
        assert_eq!(o.idempotency_key.as_deref(), Some("k2"));
        assert!(parse_args(&s(&["call", "x", "--idempotency-key"])).is_err());
        assert!(parse_args(&s(&["call", "x", "--idempotency-key", "  "])).is_err());
        let long = "k".repeat(crate::mcp_server::IDEMPOTENCY_KEY_MAX + 1);
        assert!(parse_args(&s(&["call", "x", "--idempotency-key", long.as_str()])).is_err());
        let p = meta_params(json!({ "name": "x" }), &o, None);
        assert_eq!(p["_meta"]["idempotencyKey"], "k2");
        assert_eq!(p["_meta"]["clientName"], CLI_CLIENT_NAME);
        let none = meta_params(json!({ "name": "x" }), &Options::default(), None);
        assert!(none["_meta"].get("idempotencyKey").is_none());
        assert!(usage().contains("--idempotency-key"));
    }

    #[test]
    fn arguments_json_kv_rawjson_and_stdin_marker() {
        let (v, stdin) = build_arguments(&s(&[
            "{\"a\":1,\"b\":\"x\"}",
            "c=2",
            "d:=[1,2]",
            "e:=true",
            "f=a=b",
            "-",
        ]))
        .unwrap();
        assert_eq!(
            v,
            json!({ "a": 1, "b": "x", "c": "2", "d": [1, 2], "e": true, "f": "a=b" })
        );
        assert!(stdin);
        assert!(build_arguments(&s(&["oops"])).is_err());
        assert!(build_arguments(&s(&["=x"])).is_err());
        assert!(build_arguments(&s(&["k:=nojson"])).is_err());
        assert!(build_arguments(&s(&["[1]"])).is_err());
        assert!(build_arguments(&s(&["{bad"])).is_err());
    }

    #[test]
    fn formatting_tools_results_lists_progress() {
        let tools = vec![
            json!({ "name": "list_records", "title": "列出档案", "description": "列出命盘\n第二行", "annotations": { "readOnlyHint": true } }),
            json!({ "name": "create_chart_record", "description": "建命盘" }),
        ];
        let t = fmt_tools(&tools);
        assert!(
            t.contains("list_records         只读  列出档案 — 列出命盘"),
            "{t}"
        );
        assert!(t.contains("create_chart_record  写入  建命盘"), "{t}");
        assert!(t.contains("共 2 件"));
        assert!(!t.contains("第二行"));
        let (body, err) = fmt_tool_result(
            &json!({ "content": [{ "type": "text", "text": "a" }, { "type": "text", "text": "b" }], "isError": false }),
        );
        assert_eq!((body.as_str(), err), ("a\nb\n", false));
        let (body, err) = fmt_tool_result(
            &json!({ "content": [], "structuredContent": { "x": 1 }, "isError": true }),
        );
        assert!(body.contains("\"x\": 1") && err);
        assert_eq!(
            fmt_progress(&json!({ "progress": 2, "total": 3, "message": "起盘计算" })),
            "[2/3] 起盘计算"
        );
        assert_eq!(fmt_progress(&json!({ "progress": 0.5 })), "[0.5]");
        let l = fmt_list(
            &[json!({ "uri": "horosa://chart/local-1", "name": "张三" })],
            "uri",
            "资源",
            Some("o64"),
        );
        assert!(l.contains("horosa://chart/local-1  张三") && l.contains("--cursor o64"));
        assert_eq!(
            fmt_contents(&json!({ "contents": [{ "text": "正文" }] })),
            "正文\n"
        );
        assert!(fmt_prompt(&json!({ "messages": [{ "role": "user", "content": { "type": "text", "text": "问" } }] })).contains("[user]\n问"));
        assert!(fmt_describe(&json!({ "name": "x", "inputSchema": { "type": "object" }, "outputSchema": { "type": "object" } })).contains("回包结构"));
    }

    #[test]
    fn sse_answer_skips_keepalive_and_forwards_progress() {
        let body = ": keep-alive\n\nevent: message\ndata: {\"jsonrpc\":\"2.0\",\"method\":\"notifications/progress\",\"params\":{\"progressToken\":\"cli-1\",\"progress\":1,\"total\":2}}\n\nevent: message\ndata: {\"jsonrpc\":\"2.0\",\"id\":\"other\",\"result\":{}}\n\nevent: message\ndata: {\"jsonrpc\":\"2.0\",\"id\":\"cli-1\",\"result\":{\"ok\":true}}\n\n";
        let mut seen = Vec::new();
        let ans = read_sse_answer(body.as_bytes(), "cli-1", &mut |p| seen.push(p.clone())).unwrap();
        assert_eq!(ans["result"]["ok"], true);
        assert_eq!(seen.len(), 1);
        assert!(
            read_sse_answer("data: {\"id\":\"x\"}\n\n".as_bytes(), "cli-1", &mut |_| {}).is_none()
        );
    }

    #[test]
    fn shim_install_refuses_foreign_and_round_trips() {
        let dir = std::env::temp_dir().join(format!(
            "horosa-shim-test-{}-{}",
            std::process::id(),
            RPC_SEQ.fetch_add(1, Ordering::SeqCst)
        ));
        let exe = Path::new("/Applications/星 阙's.app/Contents/MacOS/horosa-desktop-installer");
        // 首装
        let p = install_shim(&dir, exe).unwrap();
        let text = std::fs::read_to_string(&p).unwrap();
        assert!(text.starts_with("#!/bin/sh\n# horosa-cli-shim"));
        assert_eq!(
            shim_target(&text).as_deref(),
            Some(exe.display().to_string().as_str())
        );
        #[cfg(unix)]
        {
            use std::os::unix::fs::PermissionsExt;
            assert_eq!(
                std::fs::metadata(&p).unwrap().permissions().mode() & 0o777,
                0o755
            );
        }
        let st = shim_status(&dir, exe);
        assert_eq!(
            (
                st["installed"].as_bool(),
                st["current"].as_bool(),
                st["foreign"].as_bool()
            ),
            (Some(true), Some(true), Some(false))
        );
        // 换了二进制路径 → 不是 current;重装覆盖自己写的
        let exe2 = Path::new("/Applications/Other.app/Contents/MacOS/x");
        assert_eq!(shim_status(&dir, exe2)["current"], false);
        install_shim(&dir, exe2).unwrap();
        assert_eq!(shim_status(&dir, exe2)["current"], true);
        // 移除只删自己的
        assert_eq!(remove_shim(&dir), Ok(true));
        assert_eq!(remove_shim(&dir), Ok(false));
        // 用户自己的同名文件:不覆盖、不删、标 foreign
        std::fs::write(dir.join(SHIM_NAME), "#!/bin/sh\necho mine\n").unwrap();
        assert!(install_shim(&dir, exe).is_err());
        assert!(remove_shim(&dir).is_err());
        assert_eq!(shim_status(&dir, exe)["foreign"], true);
        assert_eq!(
            std::fs::read_to_string(dir.join(SHIM_NAME)).unwrap(),
            "#!/bin/sh\necho mine\n"
        );
        let _ = std::fs::remove_file(dir.join(SHIM_NAME));
        let _ = std::fs::remove_dir(&dir);
    }

    #[test]
    fn execute_without_endpoint_reports_not_running_and_usage_codes() {
        let flag = AtomicBool::new(false);
        let run = |argv: &[&str], ep: Option<PathBuf>| -> (i32, String, String) {
            let mut out = Vec::new();
            let mut err = Vec::new();
            let mut input: &[u8] = b"";
            let code = {
                let mut io = CliIo {
                    out: &mut out,
                    err: &mut err,
                    stdin: &mut input,
                    err_is_tty: false,
                    interrupted: &flag,
                };
                execute(&s(argv), ep, &mut io)
            };
            (
                code,
                String::from_utf8_lossy(&out).to_string(),
                String::from_utf8_lossy(&err).to_string(),
            )
        };
        let missing = std::env::temp_dir().join("horosa-no-such-endpoint.json");
        let (c, out, _) = run(&["help"], Some(missing.clone()));
        assert_eq!(c, EXIT_OK);
        assert!(out.contains("用法: horosa"));
        let (c, _, err) = run(&["status"], Some(missing.clone()));
        assert_eq!(c, EXIT_NOT_RUNNING);
        assert!(err.contains("外部连接"));
        let (c, out, _) = run(&["endpoint"], Some(missing.clone()));
        assert_eq!(c, EXIT_NOT_RUNNING);
        assert!(out.contains("不存在"));
        let (c, _, err) = run(&["frobnicate"], Some(missing));
        assert_eq!(c, EXIT_USAGE);
        assert!(err.contains("不认识的子命令"));
    }

    fn run_with(argv: &[&str], ep: &Path) -> (i32, String) {
        let flag = AtomicBool::new(false);
        let mut out = Vec::new();
        let mut err = Vec::new();
        let mut input: &[u8] = b"";
        let code = {
            let mut io = CliIo {
                out: &mut out,
                err: &mut err,
                stdin: &mut input,
                err_is_tty: false,
                interrupted: &flag,
            };
            execute(&s(argv), Some(ep.to_path_buf()), &mut io)
        };
        (code, String::from_utf8_lossy(&err).to_string())
    }

    /// 假本机服务:记下每个请求的路径与是否带令牌;健康探针回指定进程号
    fn recording_server(health_pid: u64) -> (u16, std::thread::JoinHandle<Vec<String>>) {
        let server = tiny_http::Server::http("127.0.0.1:0").expect("bind");
        let port = server.server_addr().to_ip().map(|a| a.port()).unwrap_or(0);
        let h = std::thread::spawn(move || {
            let mut seen = Vec::new();
            while let Ok(Some(req)) = server.recv_timeout(Duration::from_millis(800)) {
                let auth = req.headers().iter().any(|h| h.field.equiv("Authorization"));
                seen.push(format!("{} auth={}", req.url(), auth));
                let body = json!({ "app": "horosa", "pid": health_pid, "version": "9.9.9" });
                let _ = req.respond(tiny_http::Response::from_string(body.to_string()));
            }
            seen
        });
        (port, h)
    }

    fn endpoint_file(port: u16, pid: u32, tag: &str) -> PathBuf {
        let p = std::env::temp_dir().join(format!(
            "horosa-cli-verify-{}-{}-{}.json",
            std::process::id(),
            port,
            tag
        ));
        std::fs::write(
            &p,
            json!({ "url": format!("http://127.0.0.1:{}/mcp", port), "token": "tok_0123456789abcdefghijklmnop", "pid": pid }).to_string(),
        )
        .unwrap();
        p
    }

    /// 🔴 旧实现不核对端点文件里的进程就带令牌发出:应用已退出、端口被别的程序占了,令牌照发。
    /// 现在先验进程活着、再用不带令牌的健康探针核对进程号,不一致按「服务没开」(退出码 3),令牌一个字节都不发。
    #[test]
    fn stale_endpoint_is_reported_not_running_and_token_never_sent() {
        let me = std::process::id();
        let (port, h) = recording_server(me as u64 + 1);
        let ep = endpoint_file(port, me, "mismatch");
        let (code, err) = run_with(&["tools"], &ep);
        assert_eq!(code, EXIT_NOT_RUNNING, "{err}");
        assert!(err.contains("外部连接"), "{err}");
        let seen = h.join().unwrap();
        assert_eq!(
            seen,
            vec!["/healthz auth=false".to_string()],
            "只许打不带令牌的健康探针"
        );
        let _ = std::fs::remove_file(&ep);

        // 端点文件里的进程已不在:连探针都不发
        let mut dead = std::process::Command::new("/usr/bin/true").spawn().unwrap();
        let dead_pid = dead.id();
        let _ = dead.wait();
        let (port2, h2) = recording_server(dead_pid as u64);
        let ep2 = endpoint_file(port2, dead_pid, "dead");
        let (code, _) = run_with(&["call", "list_records"], &ep2);
        assert_eq!(code, EXIT_NOT_RUNNING);
        assert!(h2.join().unwrap().is_empty(), "进程不在就什么都不发");
        let _ = std::fs::remove_file(&ep2);
    }

    /// 🔴 旧实现把超时报成「服务没开」(退出码 3):服务明明在跑,只是忙 / 卡住。现在超时单独报(退出码 5)。
    #[test]
    fn timeout_is_reported_separately_from_not_running() {
        let listener = std::net::TcpListener::bind("127.0.0.1:0").unwrap();
        let port = listener.local_addr().unwrap().port();
        let hold = std::thread::spawn(move || {
            // 接下连接、读掉请求,但永不回应
            let (mut sock, _) = listener.accept().unwrap();
            let mut buf = [0u8; 4096];
            let _ = sock.read(&mut buf);
            std::thread::sleep(Duration::from_millis(1500));
        });
        let conn = Conn::new(Endpoint {
            url: format!("http://127.0.0.1:{}/mcp", port),
            token: "tok_0123456789abcdefghijklmnop".into(),
            pid: Some(std::process::id()),
        })
        .unwrap();
        let e = conn
            .rpc(
                "t-1",
                "tools/list",
                json!({}),
                Some(Duration::from_millis(300)),
                &mut |_| {},
            )
            .unwrap_err();
        assert_eq!(e, CliError::Timeout);
        assert_eq!(e.exit_code(), EXIT_FAILED);
        assert_eq!(e.message(), "本机服务响应超时");
        let _ = hold.join();
        // 连不上(没人监听)仍是「服务没开」
        let closed = Conn::new(Endpoint {
            url: format!("http://127.0.0.1:{}/mcp", port),
            token: "tok_0123456789abcdefghijklmnop".into(),
            pid: Some(std::process::id()),
        })
        .unwrap();
        let e2 = closed
            .rpc(
                "t-2",
                "tools/list",
                json!({}),
                Some(Duration::from_millis(300)),
                &mut |_| {},
            )
            .unwrap_err();
        assert_eq!(e2.exit_code(), EXIT_NOT_RUNNING, "{:?}", e2);
    }
}
