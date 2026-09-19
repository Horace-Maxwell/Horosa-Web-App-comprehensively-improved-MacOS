//! 本机外部智能体连接(MCP streamable-HTTP 服务,零新增 crate)。
//!
//! 形态:`127.0.0.1:<port>` 上的 tiny_http 小服务,`POST /mcp` 收 JSON-RPC 2.0(旧纪元:initialize / ping / tools/list / tools/call /
//! resources·prompts 五方法 / logging/setLevel;[2026-07-28] 现代纪元:server/discover / 同名读写方法 / subscriptions/listen);工具本体全部住在页面(WebView)里——本模块只是
//! 传输适配器:把请求经 `window.eval` 投递给页面桥(`window.__horosaAgentTool`,未就绪时进
//! `__horosaPendingAgentTools` 队列),页面执行后经 `agent_tool_result_command` 回传。
//! 三道门:Host → Origin(若有,须本机) → Bearer 令牌(常量时间比较)。工具面只放行
//! level ∈ {read, additive}(只读或只增,永不删改);写入动作与应用内助手共用同一账本。
//! 开关层级:页面总开关(agentEnabled)与本服务子开关(mcpServerEnabled)同时为真才起监听;
//! `HOROSA_MCP_SERVER=0` 一票否决;退出/关开关 = 关 socket + 删端点文件。
use std::collections::HashMap;
use std::fs::{self, File};
use std::io::{Read, Write};
use std::net::SocketAddr;
use std::path::{Path, PathBuf};
use std::sync::atomic::{AtomicBool, AtomicU64, AtomicUsize, Ordering};
use std::sync::{mpsc, Arc, Mutex};
use std::thread;
use std::time::{Duration, Instant};

use anyhow::{anyhow, Context, Result};
use base64::Engine as _;
use serde_json::{json, Value};
use tiny_http::{Header, Method, Response, Server, StatusCode};

pub const MCP_DEFAULT_PORT: u16 = 39991;
pub const MCP_PROTOCOL_VERSIONS: [&str; 3] = ["2024-11-05", "2025-03-26", "2025-06-18"];
pub const MCP_LATEST_PROTOCOL: &str = "2025-06-18";
/// [2026-07-28 双纪元] 现代修订:无状态(无 initialize 握手、无会话头)、每请求 `params._meta` 携带协议版本/身份/能力、`server/discover`、
/// `subscriptions/listen` 长流取代 GET 流;旧握手纪元(上面三版)照旧服务——请求带现代 `_meta` 或现代版本头 ⇒ 现代纪元,`initialize` ⇒ 旧纪元。
pub const MCP_MODERN_VERSIONS: [&str; 1] = ["2026-07-28"];
/// 现代纪元的方法集(ping / logging/setLevel / initialize 在该修订里已移除 ⇒ 404 + -32601)
pub const MODERN_METHODS: [&str; 9] = [
    "server/discover",
    "tools/list",
    "tools/call",
    "resources/list",
    "resources/templates/list",
    "resources/read",
    "prompts/list",
    "prompts/get",
    "subscriptions/listen",
];
pub const META_PROTOCOL_VERSION: &str = "io.modelcontextprotocol/protocolVersion";
pub const META_CLIENT_INFO: &str = "io.modelcontextprotocol/clientInfo";
pub const META_CLIENT_CAPS: &str = "io.modelcontextprotocol/clientCapabilities";
pub const META_SERVER_INFO: &str = "io.modelcontextprotocol/serverInfo";
pub const META_SUBSCRIPTION_ID: &str = "io.modelcontextprotocol/subscriptionId";
pub const META_LOG_LEVEL: &str = "io.modelcontextprotocol/logLevel";
const MODERN_LOG_LEVELS: [&str; 8] = [
    "debug",
    "info",
    "notice",
    "warning",
    "error",
    "critical",
    "alert",
    "emergency",
];
/// 现代长流(subscriptions/listen)上限,与旧 GET 流分别计数
const MAX_LISTEN_STREAMS: usize = 4;
const DISCOVER_TTL_MS: u64 = 3_600_000;
const LIST_TTL_MS: u64 = 30_000;
pub const MCP_ENDPOINT_FILE: &str = "mcp-endpoint.json";
pub const MCP_TOKEN_FILE: &str = "mcp-token";
const MAX_BODY_BYTES: usize = 1 << 20;
const TOOLS_CACHE_TTL: Duration = Duration::from_secs(30);
const DEFAULT_TOOL_TIMEOUT: Duration = Duration::from_secs(120);
const MAX_TOOL_TIMEOUT: Duration = Duration::from_secs(600);
const RATE_PER_MINUTE: f64 = 60.0;
const RATE_BURST: f64 = 10.0;
/// [D74] 令牌桶速率可配(页面「外部客户端策略·每分钟调用上限」1..600 同步到壳;此前壳写死 60/分钟,页面设 >60 全部无效);600 = 洪泛硬顶
const RATE_MAX_PER_MINUTE: f64 = 600.0;
const MAX_INFLIGHT: usize = 4;
const WORKERS: usize = 2;
// [P5] v2:SSE 通知通道(GET /mcp)与可选会话
const MAX_SSE_CLIENTS: usize = 4;
const SSE_KEEPALIVE: Duration = Duration::from_secs(15);
const SSE_QUEUE: usize = 32;
const MAX_SESSIONS: usize = 64;
/// [压测二轮] 会话时效:发出超过这么久的 Mcp-Session-Id 既拒绝放行也从表里剔除(此前只有「表满 64 条挤最旧」,拿到过一次会话头就能永久复用)。
const SESSION_TTL: Duration = Duration::from_secs(24 * 3600);

pub const ERR_PARSE: i64 = -32700;
pub const ERR_INVALID_REQUEST: i64 = -32600;
pub const ERR_METHOD_NOT_FOUND: i64 = -32601;
pub const ERR_INVALID_PARAMS: i64 = -32602;
pub const ERR_INTERNAL: i64 = -32603;
pub const ERR_NOT_READY: i64 = -32001;
pub const ERR_TIMEOUT: i64 = -32002;
pub const ERR_RELOADED: i64 = -32003;
pub const ERR_RATE_LIMITED: i64 = -32004;
/// [2026-07-28] 规范保留段 -32020..-32099:头/体不一致 · 缺必需客户端能力 · 不支持的协议版本
pub const ERR_HEADER_MISMATCH: i64 = -32020;
pub const ERR_MISSING_CLIENT_CAP: i64 = -32021;
pub const ERR_UNSUPPORTED_VERSION: i64 = -32022;

#[derive(Debug, Clone)]
pub struct McpError {
    pub code: i64,
    pub message: String,
    pub data: Option<Value>,
}

impl McpError {
    pub fn new(code: i64, message: impl Into<String>) -> Self {
        Self {
            code,
            message: message.into(),
            data: None,
        }
    }
    pub fn with_data(mut self, data: Value) -> Self {
        self.data = Some(data);
        self
    }
    fn to_json(&self) -> Value {
        let mut e = json!({ "code": self.code, "message": self.message });
        if let Some(d) = &self.data {
            e["data"] = d.clone();
        }
        e
    }
}

/// 页面投递抽象:应用内 = eval 到 WebView;测试 = 假页面。
pub trait PageDispatcher: Send + Sync {
    fn dispatch(
        &self,
        method: &str,
        params: Value,
        timeout: Duration,
    ) -> std::result::Result<Value, McpError>;
}

// ───────────────────────── 纯函数:安全门 ─────────────────────────

pub fn constant_time_eq(a: &[u8], b: &[u8]) -> bool {
    if a.len() != b.len() {
        return false;
    }
    let mut diff: u8 = 0;
    for (x, y) in a.iter().zip(b.iter()) {
        diff |= x ^ y;
    }
    diff == 0
}

fn is_loopback_authority(authority: &str) -> bool {
    // 带方括号的 IPv6 字面量取括号内整体(::1 自身含冒号,不能按端口分隔切);其余按 host[:port] 切
    let a = authority.trim();
    let host = if let Some(rest) = a.strip_prefix('[') {
        rest.split(']').next().unwrap_or("")
    } else {
        a.split(':').next().unwrap_or("")
    };
    let host = host.to_ascii_lowercase();
    host == "127.0.0.1" || host == "localhost" || host == "::1"
}

/// Host 头:缺省放行(HTTP/1.0),存在则必须是本机回环。
pub fn host_allowed(host: Option<&str>) -> bool {
    match host {
        None => true,
        Some(h) => is_loopback_authority(h),
    }
}

/// Origin 头:浏览器跨站请求会带;缺省(CLI 客户端)放行,存在则必须 http(s)://127.0.0.1|localhost。
pub fn origin_allowed(origin: Option<&str>) -> bool {
    match origin {
        None => true,
        Some(o) => {
            let o = o.trim().to_ascii_lowercase();
            if o == "null" {
                return false;
            }
            let rest = if let Some(r) = o.strip_prefix("http://") {
                r
            } else if let Some(r) = o.strip_prefix("https://") {
                r
            } else {
                return false;
            };
            is_loopback_authority(rest.split('/').next().unwrap_or(rest))
        }
    }
}

pub fn bearer_allowed(authorization: Option<&str>, token: &str) -> bool {
    match authorization {
        None => false,
        Some(v) => {
            let v = v.trim();
            let presented = if v.len() >= 7 && v[..7].eq_ignore_ascii_case("bearer ") {
                v[7..].trim()
            } else {
                ""
            };
            !presented.is_empty() && constant_time_eq(presented.as_bytes(), token.as_bytes())
        }
    }
}

pub fn protocol_version_allowed(header: Option<&str>) -> bool {
    match header {
        None => true,
        Some(v) => MCP_PROTOCOL_VERSIONS.contains(&v.trim()),
    }
}

// ───────────────────────── [2026-07-28] 现代纪元纯函数(版本分类 / 纪元判定 / 头值哨兵编解码 / 头体校验) ─────────────────────────
#[derive(Debug, Clone, Copy, PartialEq, Eq)]
pub enum VersionHeader {
    Absent,
    Legacy,
    Modern,
    Unknown,
}

pub fn classify_version_header(h: Option<&str>) -> VersionHeader {
    match h.map(|s| s.trim()) {
        None | Some("") => VersionHeader::Absent,
        Some(v) if MCP_MODERN_VERSIONS.contains(&v) => VersionHeader::Modern,
        Some(v) if MCP_PROTOCOL_VERSIONS.contains(&v) => VersionHeader::Legacy,
        Some(_) => VersionHeader::Unknown,
    }
}

#[derive(Debug, Clone, Copy, PartialEq, Eq)]
pub enum Era {
    Legacy,
    Modern,
}

pub fn modern_meta_version(req: &Value) -> Option<String> {
    req.get("params")
        .and_then(|p| p.get("_meta"))
        .and_then(|m| m.get(META_PROTOCOL_VERSION))
        .and_then(|v| v.as_str())
        .map(|s| s.trim().to_string())
}

/// 纪元判定(每请求):带现代 `_meta.protocolVersion` ⇒ 现代;现代版本头且方法不是 initialize ⇒ 现代;其余(含一切 initialize)⇒ 旧纪元。
pub fn detect_era(hdr: VersionHeader, req: &Value, modern_enabled: bool) -> Era {
    if !modern_enabled {
        return Era::Legacy;
    }
    if modern_meta_version(req).is_some() {
        return Era::Modern;
    }
    let method = req.get("method").and_then(|m| m.as_str()).unwrap_or("");
    if hdr == VersionHeader::Modern && method != "initialize" {
        return Era::Modern;
    }
    Era::Legacy
}

const B64_SENTINEL_PREFIX: &str = "=?base64?";
const B64_SENTINEL_SUFFIX: &str = "?=";
fn header_ascii_ok(v: &str) -> bool {
    v.bytes()
        .all(|b| b == 0x20 || b == 0x09 || (0x21..=0x7E).contains(&b))
}
/// `Mcp-Name` / `Mcp-Param-*` 头值编码:可见 ASCII 且无首尾空白原样;否则 `=?base64?<STANDARD 带填充>?=`;本身形似哨兵的明文也编码。
pub fn encode_header_value(v: &str) -> String {
    let looks_sentinel = v.starts_with(B64_SENTINEL_PREFIX) && v.ends_with(B64_SENTINEL_SUFFIX);
    if !v.is_empty() && header_ascii_ok(v) && v.trim() == v && !looks_sentinel {
        return v.to_string();
    }
    format!(
        "{}{}{}",
        B64_SENTINEL_PREFIX,
        base64::engine::general_purpose::STANDARD.encode(v.as_bytes()),
        B64_SENTINEL_SUFFIX
    )
}
/// 解码(哨兵 ⇒ base64,带填充为准、无填充宽容;明文 ⇒ 须可见 ASCII);失败 Err(())。
pub fn decode_header_value(v: &str) -> std::result::Result<String, ()> {
    let t = v.trim();
    if let Some(inner) = t
        .strip_prefix(B64_SENTINEL_PREFIX)
        .and_then(|x| x.strip_suffix(B64_SENTINEL_SUFFIX))
    {
        let bytes = base64::engine::general_purpose::STANDARD
            .decode(inner)
            .or_else(|_| base64::engine::general_purpose::STANDARD_NO_PAD.decode(inner))
            .map_err(|_| ())?;
        return String::from_utf8(bytes).map_err(|_| ());
    }
    if !header_ascii_ok(t) {
        return Err(());
    }
    Ok(t.to_string())
}

/// Streamable HTTP 现代请求必带的三头(stdio 代理按行体派生后注入;核在此校验头体一致)
pub struct ModernHeaders<'a> {
    pub version: Option<&'a str>,
    pub method: Option<&'a str>,
    pub name: Option<&'a str>,
}

/// 现代请求校验序:_meta.protocolVersion 缺 ⇒ -32602;不支持 ⇒ -32022(data.supported);版本头缺/≠ ⇒ -32020;Mcp-Method 缺/≠ ⇒ -32020;
/// tools/call · prompts/get(params.name)/ resources/read(params.uri):体非串 ⇒ -32602,头缺/解不开/≠ ⇒ -32020;_meta.logLevel 非八级 ⇒ -32602。
/// 文案只提头名,永不回显令牌;clientCapabilities 缺席按 {} 宽容(本服务不要求任何客户端能力)。
pub fn validate_modern_request(
    h: &ModernHeaders,
    req: &Value,
) -> std::result::Result<(), McpError> {
    let method = req.get("method").and_then(|m| m.as_str()).unwrap_or("");
    let params = req.get("params").cloned().unwrap_or(json!({}));
    let meta_version = modern_meta_version(req).ok_or_else(|| {
        McpError::new(
            ERR_INVALID_PARAMS,
            format!("missing params._meta {}", META_PROTOCOL_VERSION),
        )
    })?;
    if !MCP_MODERN_VERSIONS.contains(&meta_version.as_str()) {
        return Err(
            McpError::new(ERR_UNSUPPORTED_VERSION, "Unsupported protocol version")
                .with_data(json!({ "supported": MCP_MODERN_VERSIONS, "requested": meta_version })),
        );
    }
    match h.version.map(|v| v.trim()) {
        Some(v) if v == meta_version => {}
        Some(_) => {
            return Err(McpError::new(
                ERR_HEADER_MISMATCH,
                "Header mismatch: MCP-Protocol-Version does not match params._meta protocolVersion",
            ))
        }
        None => {
            return Err(McpError::new(
                ERR_HEADER_MISMATCH,
                "Header mismatch: MCP-Protocol-Version header missing",
            ))
        }
    }
    match h.method.map(|v| v.trim()) {
        Some(v) if v == method => {}
        Some(_) => {
            return Err(McpError::new(
                ERR_HEADER_MISMATCH,
                "Header mismatch: Mcp-Method does not match body method",
            ))
        }
        None => {
            return Err(McpError::new(
                ERR_HEADER_MISMATCH,
                "Header mismatch: Mcp-Method header missing",
            ))
        }
    }
    let name_field = match method {
        "tools/call" | "prompts/get" => Some("name"),
        "resources/read" => Some("uri"),
        _ => None,
    };
    if let Some(f) = name_field {
        let body_val = params.get(f).and_then(|v| v.as_str()).ok_or_else(|| {
            McpError::new(ERR_INVALID_PARAMS, format!("params.{} must be a string", f))
        })?;
        let hv = h.name.ok_or_else(|| {
            McpError::new(
                ERR_HEADER_MISMATCH,
                "Header mismatch: Mcp-Name header missing",
            )
        })?;
        let decoded = decode_header_value(hv).map_err(|_| {
            McpError::new(
                ERR_HEADER_MISMATCH,
                "Header mismatch: Mcp-Name header value is not decodable",
            )
        })?;
        if decoded != body_val {
            return Err(McpError::new(
                ERR_HEADER_MISMATCH,
                format!("Header mismatch: Mcp-Name does not match params.{}", f),
            ));
        }
    }
    if let Some(lvl) = params.get("_meta").and_then(|m| m.get(META_LOG_LEVEL)) {
        let ok = lvl
            .as_str()
            .map(|x| MODERN_LOG_LEVELS.contains(&x))
            .unwrap_or(false);
        if !ok {
            return Err(McpError::new(
                ERR_INVALID_PARAMS,
                format!("invalid {}", META_LOG_LEVEL),
            ));
        }
    }
    Ok(())
}

/// 校验期错误 → HTTP 状态:-32020/-32021/-32022/-32602/-32600 ⇒ 400;-32601 ⇒ 404;其余 200(分发期错误照 JSON-RPC 走 200)。
pub fn modern_http_status(code: i64) -> u16 {
    match code {
        ERR_HEADER_MISMATCH
        | ERR_MISSING_CLIENT_CAP
        | ERR_UNSUPPORTED_VERSION
        | ERR_INVALID_PARAMS
        | ERR_INVALID_REQUEST => 400,
        ERR_METHOD_NOT_FOUND => 404,
        _ => 200,
    }
}

/// subscriptions/listen 的订阅过滤(资源逐条订阅本服务不支持,不回显)
#[derive(Debug, Clone, Default, PartialEq, Eq)]
pub struct ListenFilter {
    pub tools: bool,
    pub prompts: bool,
    pub resources: bool,
}

impl ListenFilter {
    pub fn from_params(params: &Value) -> Self {
        let n = params.get("notifications").cloned().unwrap_or(json!({}));
        let b = |k: &str| n.get(k).and_then(|v| v.as_bool()).unwrap_or(false);
        Self {
            tools: b("toolsListChanged"),
            prompts: b("promptsListChanged"),
            resources: b("resourcesListChanged"),
        }
    }
    pub fn admits(&self, method: &str) -> bool {
        match method {
            "notifications/tools/list_changed" => self.tools,
            "notifications/prompts/list_changed" => self.prompts,
            "notifications/resources/list_changed" => self.resources,
            _ => false,
        }
    }
    pub fn agreed(&self) -> Value {
        let mut m = serde_json::Map::new();
        if self.tools {
            m.insert("toolsListChanged".into(), json!(true));
        }
        if self.prompts {
            m.insert("promptsListChanged".into(), json!(true));
        }
        if self.resources {
            m.insert("resourcesListChanged".into(), json!(true));
        }
        Value::Object(m)
    }
}

enum SseKind {
    Legacy,
    Modern { id: Value, filter: ListenFilter },
}

struct SseSubscriber {
    tx: mpsc::SyncSender<String>,
    kind: SseKind,
}

fn sse_frame(payload: &Value) -> String {
    format!("event: message\ndata: {}\n\n", payload)
}

/// 现代分发结果:JSON 单体(带 HTTP 状态)/ 通知 202 / 长流(subscriptions/listen)
pub enum ModernOutcome {
    Json { status: u16, body: Value },
    Accepted,
    Listen { id: Value, filter: ListenFilter },
}

/// 工具面过滤:只放行 level ∈ {read, additive} 且命名合规(小写蛇形)且不含删改类词。
pub fn filter_tools(tools: &[Value]) -> Vec<Value> {
    tools
        .iter()
        .filter(|t| {
            let name = t.get("name").and_then(|v| v.as_str()).unwrap_or("");
            let level = t.get("level").and_then(|v| v.as_str()).unwrap_or("");
            tool_name_ok(name) && (level == "read" || level == "additive")
        })
        .cloned()
        .collect()
}

fn tool_name_ok(name: &str) -> bool {
    if name.is_empty() || name.len() > 48 {
        return false;
    }
    // [P5] 外部 MCP 客户端接进来的工具(ext_ 前缀)永不经本机服务再导出给别的客户端
    if name.starts_with("ext_") {
        return false;
    }
    let bytes = name.as_bytes();
    if !bytes[0].is_ascii_lowercase() {
        return false;
    }
    if !bytes
        .iter()
        .all(|b| b.is_ascii_lowercase() || b.is_ascii_digit() || *b == b'_')
    {
        return false;
    }
    const DENIED: [&str; 12] = [
        "delete",
        "remove",
        "purge",
        "clear",
        "reset",
        "overwrite",
        "update",
        "rename",
        "import",
        "export",
        "restore",
        "undo",
    ];
    !DENIED.iter().any(|d| name.contains(d))
}

pub fn generate_token() -> Result<String> {
    let mut bytes = [0u8; 32];
    File::open("/dev/urandom")
        .and_then(|mut f| f.read_exact(&mut bytes))
        .context("read urandom for mcp token")?;
    Ok(base64url_no_pad(&bytes))
}

fn base64url_no_pad(input: &[u8]) -> String {
    const ALPHABET: &[u8; 64] = b"ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789-_";
    let mut out = String::with_capacity((input.len() + 2) / 3 * 4);
    for chunk in input.chunks(3) {
        let b0 = chunk[0] as u32;
        let b1 = chunk.get(1).copied().unwrap_or(0) as u32;
        let b2 = chunk.get(2).copied().unwrap_or(0) as u32;
        let n = (b0 << 16) | (b1 << 8) | b2;
        out.push(ALPHABET[((n >> 18) & 63) as usize] as char);
        out.push(ALPHABET[((n >> 12) & 63) as usize] as char);
        if chunk.len() > 1 {
            out.push(ALPHABET[((n >> 6) & 63) as usize] as char);
        }
        if chunk.len() > 2 {
            out.push(ALPHABET[(n & 63) as usize] as char);
        }
    }
    out
}

// ───────────────────────── 端点文件 ─────────────────────────

#[derive(Debug, Clone)]
pub struct EndpointInfo {
    pub url: String,
    pub token: String,
    pub port: u16,
    pub pid: u32,
    pub app_version: String,
    pub started_at: String,
}

pub fn endpoint_json(info: &EndpointInfo) -> Value {
    json!({
        "schema": 1,
        "url": info.url,
        "token": info.token,
        "port": info.port,
        "pid": info.pid,
        "appVersion": info.app_version,
        "protocolVersion": MCP_LATEST_PROTOCOL,
        "startedAt": info.started_at,
    })
}

/// 0600 + tmp+rename 原子写(读端永远看到完整文件)。
pub fn write_private_file(path: &Path, content: &[u8]) -> Result<()> {
    if let Some(parent) = path.parent() {
        fs::create_dir_all(parent).ok();
    }
    let tmp = path.with_extension("tmp");
    {
        let mut f = File::create(&tmp).with_context(|| format!("create {}", tmp.display()))?;
        #[cfg(unix)]
        {
            use std::os::unix::fs::PermissionsExt;
            let _ = fs::set_permissions(&tmp, fs::Permissions::from_mode(0o600));
        }
        f.write_all(content)?;
        f.sync_all().ok();
    }
    fs::rename(&tmp, path).with_context(|| format!("rename to {}", path.display()))?;
    #[cfg(unix)]
    {
        use std::os::unix::fs::PermissionsExt;
        let _ = fs::set_permissions(path, fs::Permissions::from_mode(0o600));
    }
    Ok(())
}

pub fn write_endpoint_file(path: &Path, info: &EndpointInfo) -> Result<()> {
    write_private_file(path, endpoint_json(info).to_string().as_bytes())
}

pub fn remove_endpoint_file(path: &Path) {
    let _ = fs::remove_file(path);
}

fn endpoint_file_pid(path: &Path) -> Option<u32> {
    let text = fs::read_to_string(path).ok()?;
    let v: Value = serde_json::from_str(&text).ok()?;
    v.get("pid").and_then(|p| p.as_u64()).map(|p| p as u32)
}

/// 只删本进程写的端点文件:多实例并存时 A 退出不得抹掉 B 的发现文件。
pub fn remove_endpoint_file_if_owned(path: &Path) {
    match endpoint_file_pid(path) {
        Some(pid) if pid != std::process::id() && pid_alive(pid) => {}
        _ => remove_endpoint_file(path),
    }
}

/// 另一存活实例已占用主端点文件 → 本实例改写带端口后缀的文件(仍可被发现,不互踩)。
pub fn choose_endpoint_path(base: &Path, port: u16) -> PathBuf {
    match endpoint_file_pid(base) {
        Some(pid) if pid != std::process::id() && pid_alive(pid) => {
            base.with_file_name(format!("mcp-endpoint-{}.json", port))
        }
        _ => base.to_path_buf(),
    }
}

fn pid_alive(pid: u32) -> bool {
    #[cfg(unix)]
    {
        Path::new(&format!("/proc/{}", pid)).exists()
            || std::process::Command::new("/bin/kill")
                .args(["-0", &pid.to_string()])
                .stdin(std::process::Stdio::null())
                .stdout(std::process::Stdio::null())
                .stderr(std::process::Stdio::null())
                .status()
                .map(|s| s.success())
                .unwrap_or(false)
    }
    #[cfg(not(unix))]
    {
        let _ = pid;
        false
    }
}

/// 启动清扫:端点文件的 pid 不存活(上次崩溃残留)→ 删;存活(另一实例)→ 留。
pub fn sweep_stale_endpoint_file(path: &Path) -> bool {
    let Ok(text) = fs::read_to_string(path) else {
        return false;
    };
    let Ok(v) = serde_json::from_str::<Value>(&text) else {
        remove_endpoint_file(path);
        return true;
    };
    let pid = v.get("pid").and_then(|p| p.as_u64()).unwrap_or(0) as u32;
    if pid == 0 || pid == std::process::id() || !pid_alive(pid) {
        remove_endpoint_file(path);
        return true;
    }
    false
}

// ───────────────────────── 协议核 ─────────────────────────

struct RateBucket {
    tokens: f64,
    last: Instant,
    rate_per_minute: f64,
    burst: f64,
}

impl RateBucket {
    fn new() -> Self {
        Self {
            tokens: RATE_BURST,
            last: Instant::now(),
            rate_per_minute: RATE_PER_MINUTE,
            burst: RATE_BURST,
        }
    }
    /// [D74] 按用户值设速率(钳 1..600);突发额 = max(10, 速率/6),换档即按新突发额重置余额
    fn set_limit(&mut self, per_minute: u32) -> u32 {
        let n = per_minute.clamp(1, RATE_MAX_PER_MINUTE as u32);
        self.rate_per_minute = n as f64;
        self.burst = (n as f64 / 6.0).max(RATE_BURST);
        // 换档 = 用户动作:按新策略给一桶新突发额(不继承旧档余额;降档时也不会超过新突发额)
        self.tokens = self.burst;
        self.last = Instant::now();
        n
    }
    fn limit(&self) -> u32 {
        self.rate_per_minute as u32
    }
    fn take(&mut self) -> bool {
        let now = Instant::now();
        let elapsed = now.duration_since(self.last).as_secs_f64();
        self.last = now;
        self.tokens = (self.tokens + elapsed * (self.rate_per_minute / 60.0)).min(self.burst);
        if self.tokens >= 1.0 {
            self.tokens -= 1.0;
            true
        } else {
            false
        }
    }
}

pub struct McpCore {
    token: Mutex<String>,
    app_version: String,
    tools_cache: Mutex<Option<(Instant, Vec<Value>)>>,
    rate: Mutex<RateBucket>,
    inflight: AtomicUsize,
    /// [P5] 可选会话:带 Mcp-Session-Id 就必须是本服务发过的;不带一律放行(向下兼容旧客户端)
    sessions: Mutex<Vec<(String, Instant)>>,
    /// [P5] SSE 订阅者(旧 GET /mcp 流 + [2026-07-28] subscriptions/listen 长流);notify 广播 `event: message`
    sse: Mutex<Vec<SseSubscriber>>,
    /// [2026-07-28] 现代纪元开关(env HOROSA_MCP_MODERN=0 关 = 完全今日行为:现代探测得 400 纯文本再回退 initialize)
    modern_enabled: AtomicBool,
    /// [P5] logging/setLevel 记的级别(仅回显,不改变本模块行为;永不吐令牌)
    log_level: Mutex<String>,
    /// [测试缝·仅 cfg(test)] 会话时钟偏移(毫秒);release 构建里这个字段根本不存在,
    /// `session_now()` 就是 `Instant::now()` —— 运行时语义逐字不变。
    #[cfg(test)]
    session_clock_skew_ms: AtomicU64,
}

impl McpCore {
    pub fn new(token: String, app_version: String) -> Self {
        Self {
            token: Mutex::new(token),
            app_version,
            tools_cache: Mutex::new(None),
            rate: Mutex::new(RateBucket::new()),
            inflight: AtomicUsize::new(0),
            sessions: Mutex::new(Vec::new()),
            sse: Mutex::new(Vec::new()),
            modern_enabled: AtomicBool::new(
                std::env::var("HOROSA_MCP_MODERN")
                    .map(|v| v != "0")
                    .unwrap_or(true),
            ),
            log_level: Mutex::new("info".to_string()),
            #[cfg(test)]
            session_clock_skew_ms: AtomicU64::new(0),
        }
    }

    // ── [测试缝] 会话时钟 ────────────────────────────────────────
    /// 会话表记时用的「现在」。运行时 = `Instant::now()`;测试可用
    /// [`McpCore::advance_session_clock`] 把它拨快,以便验证会话过期而不必真的等。
    #[cfg(test)]
    fn session_now(&self) -> Instant {
        Instant::now() + Duration::from_millis(self.session_clock_skew_ms.load(Ordering::SeqCst))
    }
    #[cfg(not(test))]
    #[inline]
    fn session_now(&self) -> Instant {
        Instant::now()
    }
    /// [测试缝·仅 cfg(test)] 把本实例的会话时钟往前拨。
    #[cfg(test)]
    fn advance_session_clock(&self, by: Duration) {
        self.session_clock_skew_ms
            .fetch_add(by.as_millis() as u64, Ordering::SeqCst);
    }

    pub fn token(&self) -> String {
        self.token.lock().map(|t| t.clone()).unwrap_or_default()
    }

    pub fn set_token(&self, token: String) {
        if let Ok(mut t) = self.token.lock() {
            *t = token;
        }
    }

    pub fn invalidate_tools_cache(&self) {
        if let Ok(mut c) = self.tools_cache.lock() {
            *c = None;
        }
    }

    // ── [P5] 可选会话 ──────────────────────────────────────────
    /// 剔除过期会话(表内就地);每次发新会话 / 校验会话前都先做一遍。
    fn prune_expired_sessions(list: &mut Vec<(String, Instant)>, now: Instant) {
        list.retain(|(_, at)| now.saturating_duration_since(*at) < SESSION_TTL);
    }
    /// initialize 成功后发一个会话 id(响应头 Mcp-Session-Id);先剔过期,容量仍满则挤掉最旧的。
    pub fn new_session(&self) -> String {
        let id = generate_token().unwrap_or_else(|_| format!("s{}", std::process::id()));
        if let Ok(mut list) = self.sessions.lock() {
            let now = self.session_now();
            Self::prune_expired_sessions(&mut list, now);
            if list.len() >= MAX_SESSIONS {
                list.remove(0);
            }
            list.push((id.clone(), now));
        }
        id
    }
    /// 不带头 → 放行(旧客户端);带头 → 必须是本服务发过的**且未过期**的会话,否则 404(MCP 规范)。
    pub fn session_allowed(&self, header: Option<&str>) -> bool {
        let Some(id) = header.map(|s| s.trim()).filter(|s| !s.is_empty()) else {
            return true;
        };
        let now = self.session_now();
        self.sessions
            .lock()
            .map(|mut l| {
                Self::prune_expired_sessions(&mut l, now);
                l.iter().any(|(x, _)| x == id)
            })
            .unwrap_or(false)
    }
    pub fn drop_session(&self, header: Option<&str>) -> bool {
        let Some(id) = header.map(|s| s.trim()).filter(|s| !s.is_empty()) else {
            return false;
        };
        self.sessions
            .lock()
            .map(|mut l| {
                let before = l.len();
                l.retain(|(x, _)| x != id);
                before != l.len()
            })
            .unwrap_or(false)
    }
    pub fn session_count(&self) -> usize {
        self.sessions.lock().map(|l| l.len()).unwrap_or(0)
    }

    // ── [P5] SSE 通知通道 ──────────────────────────────────────
    pub fn sse_count(&self) -> usize {
        self.sse.lock().map(|l| l.len()).unwrap_or(0)
    }
    /// 注册一个订阅者;超过上限返回 None(调用方回 429)。
    pub fn sse_subscribe(&self) -> Option<mpsc::Receiver<String>> {
        let (tx, rx) = mpsc::sync_channel::<String>(SSE_QUEUE);
        let mut list = self.sse.lock().ok()?;
        if list.len() >= MAX_SSE_CLIENTS {
            return None;
        }
        // 立刻推一条注释帧:tiny_http 的写缓冲要等到第一块 body 才 flush,不推的话客户端连响应头都读不到
        let _ = tx.try_send(": connected\n\n".to_string());
        list.push(SseSubscriber {
            tx,
            kind: SseKind::Legacy,
        });
        Some(rx)
    }
    /// [2026-07-28] 现代长流订阅者(subscriptions/listen):与旧 GET 流分别计上限;首帧 = 订阅确认(带 subscriptionId 与同意的通知子集)
    pub fn listen_subscribe(
        &self,
        id: Value,
        filter: ListenFilter,
    ) -> Option<mpsc::Receiver<String>> {
        let (tx, rx) = mpsc::sync_channel::<String>(SSE_QUEUE);
        let mut list = self.sse.lock().ok()?;
        if list
            .iter()
            .filter(|s| matches!(s.kind, SseKind::Modern { .. }))
            .count()
            >= MAX_LISTEN_STREAMS
        {
            return None;
        }
        let ack = json!({ "jsonrpc": "2.0", "method": "notifications/subscriptions/acknowledged", "params": { "_meta": { META_SUBSCRIPTION_ID: id.clone() }, "notifications": filter.agreed() } });
        let _ = tx.try_send(sse_frame(&ack));
        list.push(SseSubscriber {
            tx,
            kind: SseKind::Modern { id, filter },
        });
        Some(rx)
    }
    pub fn listen_count(&self) -> usize {
        self.sse
            .lock()
            .map(|l| {
                l.iter()
                    .filter(|s| matches!(s.kind, SseKind::Modern { .. }))
                    .count()
            })
            .unwrap_or(0)
    }
    /// 广播一条 JSON-RPC 通知(无 id)。返回送达的订阅者数;队列满不断开、通道关就摘掉。
    /// 旧订阅者帧字节同今日;现代订阅者按其 listen 过滤,帧的 params._meta 带 subscriptionId。
    pub fn notify(&self, method: &str, params: Value) -> usize {
        let legacy_frame =
            sse_frame(&json!({ "jsonrpc": "2.0", "method": method, "params": params }));
        let mut sent = 0usize;
        if let Ok(mut list) = self.sse.lock() {
            list.retain(|sub| {
                let frame = match &sub.kind {
                    SseKind::Legacy => legacy_frame.clone(),
                    SseKind::Modern { id, filter } => {
                        if !filter.admits(method) {
                            return true;
                        }
                        let mut p = params.clone();
                        if !p.is_object() {
                            p = json!({});
                        }
                        if let Some(obj) = p.as_object_mut() {
                            let meta = obj.entry("_meta").or_insert(json!({}));
                            if let Some(m) = meta.as_object_mut() {
                                m.insert(META_SUBSCRIPTION_ID.to_string(), id.clone());
                            }
                        }
                        sse_frame(&json!({ "jsonrpc": "2.0", "method": method, "params": p }))
                    }
                };
                match sub.tx.try_send(frame) {
                    Ok(()) => {
                        sent += 1;
                        true
                    }
                    Err(mpsc::TrySendError::Full(_)) => true,
                    Err(mpsc::TrySendError::Disconnected(_)) => false,
                }
            });
        }
        sent
    }
    pub fn modern_enabled(&self) -> bool {
        self.modern_enabled.load(Ordering::SeqCst)
    }
    pub fn set_modern_enabled(&self, on: bool) {
        self.modern_enabled.store(on, Ordering::SeqCst);
    }
    pub fn log_level(&self) -> String {
        self.log_level
            .lock()
            .map(|l| l.clone())
            .unwrap_or_else(|_| "info".into())
    }

    /// HTTP 层三道门(顺序固定:Host → Origin → Bearer → 协议版本);Ok 才进 JSON-RPC。
    pub fn gate(
        &self,
        host: Option<&str>,
        origin: Option<&str>,
        authorization: Option<&str>,
        protocol_version: Option<&str>,
    ) -> std::result::Result<(), (u16, &'static str)> {
        if !host_allowed(host) {
            return Err((403, "forbidden host"));
        }
        if !origin_allowed(origin) {
            return Err((403, "forbidden origin"));
        }
        if !bearer_allowed(authorization, &self.token()) {
            return Err((401, "unauthorized"));
        }
        if !protocol_version_allowed(protocol_version) {
            return Err((400, "unsupported MCP-Protocol-Version"));
        }
        Ok(())
    }

    /// [D74] 页面策略「每分钟调用上限」镜像到壳令牌桶(钳 1..600);回实际生效值
    pub fn set_calls_per_minute(&self, per_minute: u32) -> u32 {
        self.rate
            .lock()
            .map(|mut b| b.set_limit(per_minute))
            .unwrap_or(RATE_PER_MINUTE as u32)
    }
    pub fn calls_per_minute(&self) -> u32 {
        self.rate
            .lock()
            .map(|b| b.limit())
            .unwrap_or(RATE_PER_MINUTE as u32)
    }

    fn instructions() -> &'static str {
        "星阙(Horosa)本机工具:只读或只增——永不删除、永不覆盖已有命盘/事盘/设置;写入动作全部记入应用内账本并可由用户撤销。长文本用 maxChars 限制并分页读取。仅在用户明确要求时调用写入类工具。"
    }

    fn list_tools(
        &self,
        dispatcher: &dyn PageDispatcher,
    ) -> std::result::Result<Vec<Value>, McpError> {
        if let Ok(cache) = self.tools_cache.lock() {
            if let Some((at, tools)) = cache.as_ref() {
                if at.elapsed() < TOOLS_CACHE_TTL {
                    return Ok(tools.clone());
                }
            }
        }
        let v = dispatcher.dispatch("tools/list", json!({}), Duration::from_secs(15))?;
        let raw = v
            .get("tools")
            .and_then(|t| t.as_array())
            .cloned()
            .unwrap_or_default();
        let filtered: Vec<Value> = filter_tools(&raw)
            .into_iter()
            .map(|t| {
                json!({
                    "name": t.get("name").cloned().unwrap_or(Value::Null),
                    "description": t.get("description").cloned().unwrap_or(Value::Null),
                    "inputSchema": t.get("inputSchema").cloned().unwrap_or(json!({"type":"object"})),
                    "annotations": t.get("annotations").cloned().unwrap_or(json!({})),
                })
            })
            .collect();
        if let Ok(mut cache) = self.tools_cache.lock() {
            *cache = Some((Instant::now(), filtered.clone()));
        }
        Ok(filtered)
    }

    /// 单条 JSON-RPC;返回 None = 通知(无 id)不回体。batch(数组)由调用方先拒。
    pub fn handle_rpc(&self, req: &Value, dispatcher: &dyn PageDispatcher) -> Option<Value> {
        self.handle_rpc_with_session(req, dispatcher, None)
    }

    /// 带会话身份的分发:`session` = 请求头 Mcp-Session-Id(壳已校验过是本服务发的)。
    /// 页面侧限流桶按它分(外部客户端自报的 clientName 换个名字就是一份新额度,会话 id 是壳发的、换不了)。
    pub fn handle_rpc_with_session(
        &self,
        req: &Value,
        dispatcher: &dyn PageDispatcher,
        session: Option<&str>,
    ) -> Option<Value> {
        let id = req.get("id").cloned();
        let method = req
            .get("method")
            .and_then(|m| m.as_str())
            .unwrap_or("")
            .to_string();
        let params = req.get("params").cloned().unwrap_or(json!({}));
        let is_notification = id.is_none() || id.as_ref().map(|v| v.is_null()).unwrap_or(true);
        if req.get("jsonrpc").and_then(|v| v.as_str()) != Some("2.0") || method.is_empty() {
            return Some(Self::error_response(
                id,
                McpError::new(ERR_INVALID_REQUEST, "invalid request"),
            ));
        }
        if is_notification {
            return None;
        }
        let session_id = session
            .map(|s| s.trim())
            .filter(|s| !s.is_empty())
            .map(|s| json!(s))
            .unwrap_or(Value::Null);
        let result: std::result::Result<Value, McpError> =
            self.dispatch_method(&method, &params, dispatcher, session_id);
        Some(match result {
            Ok(r) => json!({ "jsonrpc": "2.0", "id": id, "result": r }),
            Err(e) => Self::error_response(id, e),
        })
    }

    /// [2026-07-28] 单一分发表:旧纪元(handle_rpc_with_session)与现代纪元(handle_modern)共用同一份方法实现;
    /// `session_id` 进 params.sessionId 供页面限流分桶(旧纪元 = 壳发的会话 id;现代纪元 = 常量 "modern",全部现代客户端共一桶)。
    fn dispatch_method(
        &self,
        method: &str,
        params: &Value,
        dispatcher: &dyn PageDispatcher,
        session_id: Value,
    ) -> std::result::Result<Value, McpError> {
        let with_session = |p: &Value| -> Value {
            let mut q = p.clone();
            if let Some(obj) = q.as_object_mut() {
                obj.insert("sessionId".to_string(), session_id.clone());
            }
            q
        };
        match method {
            "initialize" => {
                let requested = params
                    .get("protocolVersion")
                    .and_then(|v| v.as_str())
                    .unwrap_or("");
                let negotiated = if MCP_PROTOCOL_VERSIONS.contains(&requested) {
                    requested
                } else {
                    MCP_LATEST_PROTOCOL
                };
                Ok(json!({
                    "protocolVersion": negotiated,
                    // [P5] v2:工具/资源/提示三面都会推 list_changed(资源不支持逐条 subscribe)
                    "capabilities": {
                        "tools": { "listChanged": true },
                        "resources": { "subscribe": false, "listChanged": true },
                        "prompts": { "listChanged": true },
                        "logging": {}
                    },
                    "serverInfo": { "name": "horosa", "version": self.app_version },
                    "instructions": Self::instructions(),
                }))
            }
            "ping" => Ok(json!({})),
            "tools/list" => self
                .list_tools(dispatcher)
                .map(|tools| json!({ "tools": tools })),
            "tools/call" => self.call_tool(&with_session(params), dispatcher),
            // [P5] 资源/提示:本模块只做传输,内容全部住页面(命盘/事盘/资料/模版/技法提示卡);params 带上会话身份供页面限流分桶
            "resources/list" => self.page_passthrough(
                "resources/list",
                &with_session(params),
                dispatcher,
                "resources",
            ),
            "resources/templates/list" => self.page_passthrough(
                "resources/templates/list",
                &with_session(params),
                dispatcher,
                "resourceTemplates",
            ),
            "resources/read" => self.page_passthrough(
                "resources/read",
                &with_session(params),
                dispatcher,
                "contents",
            ),
            "prompts/list" => {
                self.page_passthrough("prompts/list", &with_session(params), dispatcher, "prompts")
            }
            "prompts/get" => {
                self.page_passthrough("prompts/get", &with_session(params), dispatcher, "messages")
            }
            // logging/setLevel 本地记级别即可(本模块不产日志给客户端,永不回吐令牌/请求体)
            "logging/setLevel" => {
                let lvl = params.get("level").and_then(|v| v.as_str()).unwrap_or("");
                const LEVELS: [&str; 8] = [
                    "debug",
                    "info",
                    "notice",
                    "warning",
                    "error",
                    "critical",
                    "alert",
                    "emergency",
                ];
                if !LEVELS.contains(&lvl) {
                    Err(McpError::new(ERR_INVALID_PARAMS, "invalid level"))
                } else {
                    if let Ok(mut l) = self.log_level.lock() {
                        *l = lvl.to_string();
                    }
                    Ok(json!({}))
                }
            }
            _ => Err(McpError::new(
                ERR_METHOD_NOT_FOUND,
                format!("method not found: {}", method),
            )),
        }
    }

    fn server_info(&self) -> Value {
        json!({ "name": "horosa", "version": self.app_version })
    }

    /// [2026-07-28] server/discover:支持的现代版本 / 能力位 / 身份 / 指引;可缓存一小时(public)
    pub fn discover_result(&self) -> Value {
        json!({
            "resultType": "complete",
            "supportedVersions": MCP_MODERN_VERSIONS,
            "capabilities": { "tools": {"listChanged": true}, "resources": {"subscribe": false, "listChanged": true}, "prompts": {"listChanged": true}, "extensions": {} },
            "_meta": { META_SERVER_INFO: self.server_info() },
            "instructions": Self::instructions(),
            "ttlMs": DISCOVER_TTL_MS,
            "cacheScope": "public"
        })
    }

    /// 现代结果包装:resultType:"complete" + _meta.serverInfo;列表类带 ttlMs/cacheScope;现代 tools/list 按 name 稳定排序(旧纪元不动)
    fn wrap_modern(&self, method: &str, mut result: Value) -> Value {
        if let Some(obj) = result.as_object_mut() {
            obj.insert("resultType".into(), json!("complete"));
            let meta = obj.entry("_meta").or_insert(json!({}));
            if let Some(m) = meta.as_object_mut() {
                m.insert(META_SERVER_INFO.to_string(), self.server_info());
            }
            match method {
                "tools/list" => {
                    if let Some(arr) = obj.get_mut("tools").and_then(|t| t.as_array_mut()) {
                        arr.sort_by(|x, y| {
                            x.get("name")
                                .and_then(|v| v.as_str())
                                .unwrap_or("")
                                .cmp(y.get("name").and_then(|v| v.as_str()).unwrap_or(""))
                        });
                    }
                    obj.insert("ttlMs".into(), json!(LIST_TTL_MS));
                    obj.insert("cacheScope".into(), json!("private"));
                }
                "prompts/list" | "resources/list" | "resources/templates/list" => {
                    obj.insert("ttlMs".into(), json!(LIST_TTL_MS));
                    obj.insert("cacheScope".into(), json!("private"));
                }
                "resources/read" => {
                    obj.insert("ttlMs".into(), json!(0));
                    obj.insert("cacheScope".into(), json!("private"));
                }
                _ => {}
            }
        }
        result
    }

    /// [2026-07-28] 现代纪元入口(HTTP 层已按纪元分流):形状 → 通知 202 → 头体校验(headers=None 时只校验 _meta,给核级测试用)
    /// → 方法集(非现代方法 404/-32601)→ server/discover / subscriptions/listen / 其余走单一分发表并包装。
    pub fn handle_modern(
        &self,
        req: &Value,
        headers: Option<&ModernHeaders>,
        dispatcher: &dyn PageDispatcher,
    ) -> ModernOutcome {
        let id = req.get("id").cloned();
        let method = req
            .get("method")
            .and_then(|m| m.as_str())
            .unwrap_or("")
            .to_string();
        let params = req.get("params").cloned().unwrap_or(json!({}));
        if req.get("jsonrpc").and_then(|v| v.as_str()) != Some("2.0") || method.is_empty() {
            return ModernOutcome::Json {
                status: 400,
                body: Self::error_response(
                    id,
                    McpError::new(ERR_INVALID_REQUEST, "invalid request"),
                ),
            };
        }
        let is_notification = id.is_none() || id.as_ref().map(|v| v.is_null()).unwrap_or(true);
        if is_notification {
            return ModernOutcome::Accepted;
        }
        match headers {
            Some(h) => {
                if let Err(e) = validate_modern_request(h, req) {
                    return ModernOutcome::Json {
                        status: modern_http_status(e.code),
                        body: Self::error_response(id, e),
                    };
                }
            }
            None => {
                let Some(v) = modern_meta_version(req) else {
                    return ModernOutcome::Json {
                        status: 400,
                        body: Self::error_response(
                            id,
                            McpError::new(
                                ERR_INVALID_PARAMS,
                                format!("missing params._meta {}", META_PROTOCOL_VERSION),
                            ),
                        ),
                    };
                };
                if !MCP_MODERN_VERSIONS.contains(&v.as_str()) {
                    return ModernOutcome::Json {
                        status: 400,
                        body: Self::error_response(
                            id,
                            McpError::new(ERR_UNSUPPORTED_VERSION, "Unsupported protocol version")
                                .with_data(
                                    json!({ "supported": MCP_MODERN_VERSIONS, "requested": v }),
                                ),
                        ),
                    };
                }
            }
        }
        if !MODERN_METHODS.contains(&method.as_str()) {
            return ModernOutcome::Json { status: 404, body: Self::error_response(id, McpError::new(ERR_METHOD_NOT_FOUND, format!("method not found: {} (modern era: initialize/ping/logging are not served to per-request-metadata clients)", method))) };
        }
        if method == "server/discover" {
            return ModernOutcome::Json {
                status: 200,
                body: json!({ "jsonrpc": "2.0", "id": id, "result": self.discover_result() }),
            };
        }
        if method == "subscriptions/listen" {
            return ModernOutcome::Listen {
                id: id.unwrap_or(Value::Null),
                filter: ListenFilter::from_params(&params),
            };
        }
        // 页面按 params._meta.clientName 展示来源(旧纪元客户端自报);现代客户端的身份在 _meta.clientInfo.name ⇒ 缺席时补进 _meta.clientName
        let mut p = params.clone();
        if let Some(meta) = p.get_mut("_meta").and_then(|m| m.as_object_mut()) {
            if meta.get("clientName").is_none() {
                if let Some(n) = meta
                    .get(META_CLIENT_INFO)
                    .and_then(|c| c.get("name"))
                    .and_then(|v| v.as_str())
                    .map(|x| x.to_string())
                {
                    meta.insert("clientName".to_string(), json!(n));
                }
            }
        }
        match self.dispatch_method(&method, &p, dispatcher, json!("modern")) {
            Ok(r) => ModernOutcome::Json {
                status: 200,
                body: json!({ "jsonrpc": "2.0", "id": id, "result": self.wrap_modern(&method, r) }),
            },
            Err(e) => ModernOutcome::Json {
                status: 200,
                body: Self::error_response(id, e),
            },
        }
    }

    /// [P5] 资源/提示类:参数原样投页面,回体必须带约定的数组字段(缺 → 视为页面畸形返回)。
    /// 与 tools/call 共用同一限流与在途上限:外部客户端读资源同样不能压垮页面。
    fn page_passthrough(
        &self,
        method: &str,
        params: &Value,
        dispatcher: &dyn PageDispatcher,
        expect_key: &str,
    ) -> std::result::Result<Value, McpError> {
        {
            let ok = self.rate.lock().map(|mut b| b.take()).unwrap_or(true);
            if !ok {
                return Err(McpError::new(ERR_RATE_LIMITED, "rate limited")
                    .with_data(json!({ "retryAfterMs": 1000 })));
            }
        }
        if self.inflight.fetch_add(1, Ordering::SeqCst) >= MAX_INFLIGHT {
            self.inflight.fetch_sub(1, Ordering::SeqCst);
            return Err(McpError::new(ERR_RATE_LIMITED, "too many in-flight calls")
                .with_data(json!({ "retryAfterMs": 500 })));
        }
        let out = dispatcher.dispatch(method, params.clone(), Duration::from_secs(20));
        self.inflight.fetch_sub(1, Ordering::SeqCst);
        let v = out?;
        if v.get(expect_key).and_then(|x| x.as_array()).is_none() {
            return Err(McpError::new(
                ERR_INTERNAL,
                format!("page returned malformed {} result", method),
            ));
        }
        Ok(v)
    }

    fn call_tool(
        &self,
        params: &Value,
        dispatcher: &dyn PageDispatcher,
    ) -> std::result::Result<Value, McpError> {
        let name = params
            .get("name")
            .and_then(|v| v.as_str())
            .unwrap_or("")
            .to_string();
        if !tool_name_ok(&name) {
            return Err(McpError::new(ERR_INVALID_PARAMS, "invalid tool name"));
        }
        let arguments = params.get("arguments").cloned().unwrap_or(json!({}));
        if !arguments.is_object() {
            return Err(McpError::new(
                ERR_INVALID_PARAMS,
                "arguments must be an object",
            ));
        }
        {
            let ok = self.rate.lock().map(|mut b| b.take()).unwrap_or(true);
            if !ok {
                return Err(McpError::new(ERR_RATE_LIMITED, "rate limited")
                    .with_data(json!({ "retryAfterMs": 1000 })));
            }
        }
        if self.inflight.fetch_add(1, Ordering::SeqCst) >= MAX_INFLIGHT {
            self.inflight.fetch_sub(1, Ordering::SeqCst);
            return Err(McpError::new(ERR_RATE_LIMITED, "too many in-flight calls")
                .with_data(json!({ "retryAfterMs": 500 })));
        }
        let timeout_ms = params
            .get("_meta")
            .and_then(|m| m.get("timeoutMs"))
            .and_then(|v| v.as_u64())
            .unwrap_or(0);
        let timeout = if timeout_ms == 0 {
            DEFAULT_TOOL_TIMEOUT
        } else {
            Duration::from_millis(timeout_ms).min(MAX_TOOL_TIMEOUT)
        };
        let out = dispatcher.dispatch(
            "tools/call",
            json!({
                "name": name,
                "arguments": arguments,
                "clientName": params.get("_meta").and_then(|m| m.get("clientName")).cloned().unwrap_or(Value::Null),
                "sessionId": params.get("sessionId").cloned().unwrap_or(Value::Null)
            }),
            timeout,
        );
        self.inflight.fetch_sub(1, Ordering::SeqCst);
        let v = out?;
        // 页面返回 {content:[{type:'text',text}], structuredContent?, isError} —— 直接作为 result
        if v.get("content").is_none() {
            return Err(McpError::new(
                ERR_INTERNAL,
                "page returned malformed tool result",
            ));
        }
        Ok(v)
    }

    fn error_response(id: Option<Value>, e: McpError) -> Value {
        json!({ "jsonrpc": "2.0", "id": id.unwrap_or(Value::Null), "error": e.to_json() })
    }
}

// ───────────────────────── HTTP 传输 ─────────────────────────

pub struct McpServerHandle {
    shutdown: Arc<AtomicBool>,
    port: u16,
    workers: Vec<thread::JoinHandle<()>>,
}

impl McpServerHandle {
    pub fn port(&self) -> u16 {
        self.port
    }
    /// 先置停止位(worker 下一次 recv_timeout 轮询即退出),不等待。
    pub fn signal_stop(&self) {
        self.shutdown.store(true, Ordering::SeqCst);
    }
    /// 有界等待:worker 可能卡在慢体读取或页面派发上,退出臂/主线程绝不能被它拖死——
    /// 超过上限就放弃 join(线程随进程退出;端口由最后一个 worker 退出时释放)。返回是否全部退出。
    pub fn stop(mut self) -> bool {
        self.signal_stop();
        let deadline = Instant::now() + Duration::from_millis(1500);
        let mut all_done = true;
        for w in self.workers.drain(..) {
            while !w.is_finished() && Instant::now() < deadline {
                thread::sleep(Duration::from_millis(25));
            }
            if w.is_finished() {
                let _ = w.join();
            } else {
                all_done = false;
            }
        }
        all_done
    }
}

fn header_value<'a>(request: &'a tiny_http::Request, name: &str) -> Option<&'a str> {
    request
        .headers()
        .iter()
        .find(|h| h.field.as_str().as_str().eq_ignore_ascii_case(name))
        .map(|h| h.value.as_str())
}

fn json_response(status: u16, body: &Value) -> Response<std::io::Cursor<Vec<u8>>> {
    let mut r = Response::from_string(body.to_string()).with_status_code(StatusCode(status));
    if let Ok(h) = Header::from_bytes(
        &b"Content-Type"[..],
        &b"application/json; charset=utf-8"[..],
    ) {
        r = r.with_header(h);
    }
    if let Ok(h) = Header::from_bytes(&b"Cache-Control"[..], &b"no-store"[..]) {
        r = r.with_header(h);
    }
    r
}

fn plain_response(status: u16, text: &str) -> Response<std::io::Cursor<Vec<u8>>> {
    Response::from_string(text.to_string()).with_status_code(StatusCode(status))
}

/// SSE 写流(旧 GET /mcp 与 [2026-07-28] subscriptions/listen 共用;唯一的 upgrade 裸 socket 出口):
/// 🔴 tiny_http 0.12 的 chunked 编码器有 8KB 内部缓冲:走 Response{reader} 时连响应头都发不出去(实测客户端读 header 即 WouldBlock)。
///    改用 upgrade 拿裸 socket:header 由 tiny_http 写完即 flush,SSE 帧由本线程逐帧写、逐帧 flush。
///    额外的 Connection/Upgrade 头是 hop-by-hop、本机回环无代理,SSE 客户端只认 Content-Type。
/// 独立线程写流:worker 立刻回去收下一个请求(WORKERS=2,被 SSE 占死就收不了 POST);服务停机时现代流先写收尾帧(closing_frame)再关。
fn stream_sse(
    request: tiny_http::Request,
    rx: mpsc::Receiver<String>,
    shutdown: Arc<AtomicBool>,
    closing_frame: Option<String>,
) {
    let mut resp = Response::empty(StatusCode(200));
    for (k, v) in [
        ("Content-Type", "text/event-stream"),
        ("Cache-Control", "no-store"),
        ("X-Accel-Buffering", "no"),
    ] {
        if let Ok(h) = Header::from_bytes(k.as_bytes(), v.as_bytes()) {
            resp = resp.with_header(h);
        }
    }
    thread::spawn(move || {
        let mut socket = request.upgrade("sse", resp);
        let mut quiet_since = Instant::now();
        loop {
            if shutdown.load(Ordering::SeqCst) {
                if let Some(f) = closing_frame.as_ref() {
                    let _ = socket.write_all(f.as_bytes());
                    let _ = socket.flush();
                }
                break;
            }
            let frame = match rx.recv_timeout(Duration::from_millis(500)) {
                Ok(f) => f,
                Err(mpsc::RecvTimeoutError::Timeout) => {
                    if quiet_since.elapsed() < SSE_KEEPALIVE {
                        continue;
                    }
                    ": keep-alive\n\n".to_string()
                }
                Err(mpsc::RecvTimeoutError::Disconnected) => break,
            };
            if socket.write_all(frame.as_bytes()).is_err() || socket.flush().is_err() {
                break;
            }
            quiet_since = Instant::now();
        }
    });
}

fn handle_request(
    core: &McpCore,
    dispatcher: &dyn PageDispatcher,
    mut request: tiny_http::Request,
    app_version: &str,
    shutdown: &Arc<AtomicBool>,
) {
    let url = request.url().split('?').next().unwrap_or("").to_string();
    let method = request.method().clone();
    if url == "/healthz" && method == Method::Get {
        let body = json!({ "app": "horosa", "pid": std::process::id(), "version": app_version, "protocolVersion": MCP_LATEST_PROTOCOL, "modernProtocolVersions": MCP_MODERN_VERSIONS });
        let _ = request.respond(json_response(200, &body));
        return;
    }
    if url != "/mcp" {
        let _ = request.respond(plain_response(404, "not found"));
        return;
    }
    // [P5] GET /mcp = SSE 通知通道;DELETE /mcp = 结束会话。两者都先过与 POST **同一** core.gate()
    //      (Host → Origin → Bearer → 协议版本),门在前、语义在后。
    if method == Method::Get || method == Method::Delete {
        if let Err((status, msg)) = core.gate(
            header_value(&request, "Host"),
            header_value(&request, "Origin"),
            header_value(&request, "Authorization"),
            header_value(&request, "MCP-Protocol-Version"),
        ) {
            let mut r = plain_response(status, msg);
            if status == 401 {
                if let Ok(h) =
                    Header::from_bytes(&b"WWW-Authenticate"[..], &b"Bearer realm=\"horosa\""[..])
                {
                    r = r.with_header(h);
                }
            }
            let _ = request.respond(r);
            return;
        }
        if !core.session_allowed(header_value(&request, "Mcp-Session-Id")) {
            let _ = request.respond(plain_response(404, "unknown session"));
            return;
        }
        if method == Method::Delete {
            core.drop_session(header_value(&request, "Mcp-Session-Id"));
            let _ = request.respond(plain_response(204, ""));
            return;
        }
        let accepts_sse = header_value(&request, "Accept")
            .map(|a| a.contains("text/event-stream"))
            .unwrap_or(false);
        if !accepts_sse {
            let _ = request.respond(plain_response(
                406,
                "GET /mcp requires Accept: text/event-stream",
            ));
            return;
        }
        let Some(rx) = core.sse_subscribe() else {
            let _ = request.respond(plain_response(429, "too many event streams"));
            return;
        };
        // 🔴 tiny_http 0.12 的 chunked 编码器有 8KB 内部缓冲:走 Response{reader} 时连响应头都发不出去(实测客户端读 header 即 WouldBlock)。
        //    改用 upgrade 拿裸 socket:header 由 tiny_http 写完即 flush,SSE 帧由本线程逐帧写、逐帧 flush。
        //    额外的 Connection/Upgrade 头是 hop-by-hop、本机回环无代理,SSE 客户端只认 Content-Type。
        stream_sse(request, rx, Arc::clone(shutdown), None);
        return;
    }
    if method != Method::Post {
        let mut r = plain_response(405, "method not allowed");
        if let Ok(h) = Header::from_bytes(&b"Allow"[..], &b"POST, GET, DELETE"[..]) {
            r = r.with_header(h);
        }
        let _ = request.respond(r);
        return;
    }
    // [2026-07-28 双纪元] 先按版本头分类:旧头/无头 ⇒ 今日门序逐字(协议版本门 + 会话检查);现代头/未知头 ⇒ 只过 Host→Origin→Bearer 三门,
    //   版本与纪元在读体后判定(现代请求以 _meta 为准;旧纪元遇未知头仍回今日的 400 纯文本 —— 这正是现代客户端探测失败后回退 initialize 的路径)。
    let vh = classify_version_header(header_value(&request, "MCP-Protocol-Version"));
    let modern_lane =
        core.modern_enabled() && matches!(vh, VersionHeader::Modern | VersionHeader::Unknown);
    let gate = core.gate(
        header_value(&request, "Host"),
        header_value(&request, "Origin"),
        header_value(&request, "Authorization"),
        if modern_lane {
            None
        } else {
            header_value(&request, "MCP-Protocol-Version")
        },
    );
    if let Err((status, msg)) = gate {
        let mut r = plain_response(status, msg);
        if status == 401 {
            if let Ok(h) =
                Header::from_bytes(&b"WWW-Authenticate"[..], &b"Bearer realm=\"horosa\""[..])
            {
                r = r.with_header(h);
            }
        }
        let _ = request.respond(r);
        return;
    }
    if !modern_lane && !core.session_allowed(header_value(&request, "Mcp-Session-Id")) {
        let _ = request.respond(plain_response(404, "unknown session"));
        return;
    }
    if request.body_length().unwrap_or(0) > MAX_BODY_BYTES {
        let _ = request.respond(plain_response(413, "payload too large"));
        return;
    }
    let mut body = Vec::new();
    if request
        .as_reader()
        .take(MAX_BODY_BYTES as u64 + 1)
        .read_to_end(&mut body)
        .is_err()
        || body.len() > MAX_BODY_BYTES
    {
        let _ = request.respond(plain_response(413, "payload too large"));
        return;
    }
    let parsed: Value = match serde_json::from_slice(&body) {
        Ok(v) => v,
        Err(e) => {
            let _ = request.respond(json_response(
                400,
                &McpCore::error_response(
                    None,
                    McpError::new(ERR_PARSE, format!("parse error: {}", e)),
                ),
            ));
            return;
        }
    };
    if parsed.is_array() {
        let _ = request.respond(json_response(
            400,
            &McpCore::error_response(
                None,
                McpError::new(ERR_INVALID_REQUEST, "batch requests are not supported"),
            ),
        ));
        return;
    }
    if detect_era(vh, &parsed, core.modern_enabled()) == Era::Modern {
        let hv_version = header_value(&request, "MCP-Protocol-Version").map(|v| v.to_string());
        let hv_method = header_value(&request, "Mcp-Method").map(|v| v.to_string());
        let hv_name = header_value(&request, "Mcp-Name").map(|v| v.to_string());
        let hdrs = ModernHeaders {
            version: hv_version.as_deref(),
            method: hv_method.as_deref(),
            name: hv_name.as_deref(),
        };
        match core.handle_modern(&parsed, Some(&hdrs), dispatcher) {
            ModernOutcome::Accepted => {
                let _ = request.respond(plain_response(202, ""));
            }
            ModernOutcome::Json { status, body } => {
                let _ = request.respond(json_response(status, &body));
            }
            ModernOutcome::Listen { id, filter } => {
                let Some(rx) = core.listen_subscribe(id.clone(), filter) else {
                    let _ = request.respond(json_response(
                        429,
                        &McpCore::error_response(
                            Some(id),
                            McpError::new(ERR_RATE_LIMITED, "too many event streams")
                                .with_data(json!({ "retryAfterMs": 1000 })),
                        ),
                    ));
                    return;
                };
                let closing = sse_frame(
                    &json!({ "jsonrpc": "2.0", "id": id, "result": { "resultType": "complete", "_meta": { META_SUBSCRIPTION_ID: id } } }),
                );
                stream_sse(request, rx, Arc::clone(shutdown), Some(closing));
            }
        }
        return;
    }
    if vh == VersionHeader::Unknown {
        // 旧纪元 + 未知版本头 = 今日行为(纯文本 400,不是 JSON-RPC 错误 ⇒ 双纪元客户端据此回退 initialize)
        let _ = request.respond(plain_response(400, "unsupported MCP-Protocol-Version"));
        return;
    }
    let is_init = parsed.get("method").and_then(|m| m.as_str()) == Some("initialize");
    let session_header = header_value(&request, "Mcp-Session-Id");
    match core.handle_rpc_with_session(&parsed, dispatcher, session_header.as_deref()) {
        None => {
            let _ = request.respond(plain_response(202, ""));
        }
        Some(v) => {
            let mut r = json_response(200, &v);
            // [P5] initialize 成功 → 发一个会话 id;客户端此后可带 Mcp-Session-Id(不带也照旧放行)
            if is_init && v.get("result").is_some() {
                if let Ok(h) =
                    Header::from_bytes(&b"Mcp-Session-Id"[..], core.new_session().as_bytes())
                {
                    r = r.with_header(h);
                }
            }
            let _ = request.respond(r);
        }
    }
}

/// `port_pref`=0 → 系统分配临时口(测试用);否则 pref..pref+8 顺位试绑。
pub fn start_server(
    port_pref: u16,
    core: Arc<McpCore>,
    dispatcher: Arc<dyn PageDispatcher>,
    app_version: String,
) -> Result<McpServerHandle> {
    let server = if port_pref == 0 {
        Server::http(SocketAddr::from(([127, 0, 0, 1], 0))).map_err(|e| anyhow!(e.to_string()))?
    } else {
        let mut bound = None;
        for offset in 0..=8u16 {
            let Some(candidate) = port_pref.checked_add(offset) else {
                break;
            };
            if let Ok(s) = Server::http(SocketAddr::from(([127, 0, 0, 1], candidate))) {
                bound = Some(s);
                break;
            }
        }
        bound.ok_or_else(|| {
            anyhow!(
                "mcp: no free port in {}..{}",
                port_pref,
                port_pref.saturating_add(8)
            )
        })?
    };
    let port = match server.server_addr() {
        tiny_http::ListenAddr::IP(a) => a.port(),
        #[allow(unreachable_patterns)]
        _ => port_pref,
    };
    let server = Arc::new(server);
    let shutdown = Arc::new(AtomicBool::new(false));
    let mut workers = Vec::new();
    for _ in 0..WORKERS {
        let server = Arc::clone(&server);
        let shutdown = Arc::clone(&shutdown);
        let core = Arc::clone(&core);
        let dispatcher = Arc::clone(&dispatcher);
        let version = app_version.clone();
        workers.push(thread::spawn(move || {
            while !shutdown.load(Ordering::SeqCst) {
                let request = match server.recv_timeout(Duration::from_millis(250)) {
                    Ok(Some(req)) => req,
                    Ok(None) => continue,
                    Err(_) => continue,
                };
                handle_request(&core, dispatcher.as_ref(), request, &version, &shutdown);
            }
        }));
    }
    Ok(McpServerHandle {
        shutdown,
        port,
        workers,
    })
}

// ───────────────────────── Tauri 胶水 ─────────────────────────

/// 页面桥:eval 投递 + 等待页面 invoke 回传。
pub struct PageBridge {
    app: Mutex<Option<tauri::AppHandle>>,
    pending: Mutex<HashMap<u64, mpsc::SyncSender<std::result::Result<Value, McpError>>>>,
    next_id: AtomicU64,
    ready: AtomicBool,
    stopping: AtomicBool,
}

impl Default for PageBridge {
    fn default() -> Self {
        Self {
            app: Mutex::new(None),
            pending: Mutex::new(HashMap::new()),
            next_id: AtomicU64::new(1),
            ready: AtomicBool::new(false),
            stopping: AtomicBool::new(false),
        }
    }
}

impl PageBridge {
    pub fn attach(&self, app: tauri::AppHandle) {
        if let Ok(mut a) = self.app.lock() {
            *a = Some(app);
        }
    }

    /// 页面桥就绪/离场:两种情形在途请求都不可能再被应答——就绪=页面刚(重新)绑桥,之前投递的都丢了;
    /// 离场=页面总开关关。就绪用 -32003(可重试),离场用 -32001(不可用)。
    pub fn set_ready(&self, ready: bool) {
        self.ready.store(ready, Ordering::SeqCst);
        if ready {
            self.fail_all_pending(McpError::new(ERR_RELOADED, "page bridge reloaded; retry"));
        } else {
            self.fail_all_pending(
                McpError::new(ERR_NOT_READY, "agent ability disabled on page")
                    .with_data(json!({ "retryAfterMs": 5000 })),
            );
        }
    }

    pub fn mark_ready(&self) {
        self.set_ready(true);
    }

    pub fn set_stopping(&self, stopping: bool) {
        self.stopping.store(stopping, Ordering::SeqCst);
    }

    pub fn is_ready(&self) -> bool {
        self.ready.load(Ordering::SeqCst)
    }

    pub fn resolve(&self, id: u64, outcome: std::result::Result<Value, McpError>) -> bool {
        let tx = self.pending.lock().ok().and_then(|mut p| p.remove(&id));
        match tx {
            Some(tx) => tx.send(outcome).is_ok(),
            None => false,
        }
    }

    pub fn fail_all_pending(&self, err: McpError) {
        if let Ok(mut p) = self.pending.lock() {
            for (_, tx) in p.drain() {
                let _ = tx.send(Err(err.clone()));
            }
        }
    }

    /// 投递脚本:双层转义(JSON 串再经 JSON 字符串字面量)→ 页面 JSON.parse。
    pub fn dispatch_script(payload: &Value) -> String {
        // JSON 字符串字面量再把 "</" 写成 "<\/"(合法 JSON 转义):eval 上下文本无 HTML 语义,但杜绝任何 </script> 字样
        let literal = serde_json::to_string(&payload.to_string())
            .unwrap_or_else(|_| "\"{}\"".to_string())
            .replace("</", "<\\/");
        format!(
            "(function(){{try{{var r=JSON.parse({lit});if(typeof window.__horosaAgentTool==='function'){{window.__horosaAgentTool(r);}}else{{(window.__horosaPendingAgentTools=window.__horosaPendingAgentTools||[]).push(r);}}}}catch(e){{}}}})();",
            lit = literal
        )
    }
}

impl PageDispatcher for PageBridge {
    fn dispatch(
        &self,
        method: &str,
        params: Value,
        timeout: Duration,
    ) -> std::result::Result<Value, McpError> {
        if self.stopping.load(Ordering::SeqCst) {
            return Err(McpError::new(ERR_NOT_READY, "server stopping")
                .with_data(json!({ "retryAfterMs": 5000 })));
        }
        if !self.ready.load(Ordering::SeqCst) {
            // 页面桥未就绪/总开关关:直接拒,绝不投进页面队列等超时(那些请求永远无人应答)
            return Err(McpError::new(
                ERR_NOT_READY,
                "page bridge not ready (open the app / enable agent ability)",
            )
            .with_data(json!({ "retryAfterMs": 3000 })));
        }
        let app = self.app.lock().ok().and_then(|a| a.clone());
        let Some(app) = app else {
            return Err(McpError::new(ERR_NOT_READY, "app not ready")
                .with_data(json!({ "retryAfterMs": 1500 })));
        };
        use tauri::Manager;
        let Some(window) = app.get_webview_window(crate::MAIN_WINDOW_LABEL) else {
            return Err(McpError::new(ERR_NOT_READY, "main window not ready")
                .with_data(json!({ "retryAfterMs": 1500 })));
        };
        let id = self.next_id.fetch_add(1, Ordering::SeqCst);
        let (tx, rx) = mpsc::sync_channel(1);
        if let Ok(mut p) = self.pending.lock() {
            p.insert(id, tx);
        }
        let payload = json!({ "id": id, "method": method, "params": params });
        if window.eval(&Self::dispatch_script(&payload)).is_err() {
            if let Ok(mut p) = self.pending.lock() {
                p.remove(&id);
            }
            return Err(McpError::new(ERR_NOT_READY, "page eval failed")
                .with_data(json!({ "retryAfterMs": 1500 })));
        }
        // 分片等待:停服/页面离场时 fail_all_pending 会立刻送错;这里再按 stopping 位兜底,绝不整段死等
        let deadline = Instant::now() + timeout;
        loop {
            match rx.recv_timeout(Duration::from_millis(250)) {
                Ok(r) => return r,
                Err(mpsc::RecvTimeoutError::Disconnected) => break,
                Err(mpsc::RecvTimeoutError::Timeout) => {
                    if self.stopping.load(Ordering::SeqCst) || Instant::now() >= deadline {
                        break;
                    }
                }
            }
        }
        if let Ok(mut p) = self.pending.lock() {
            p.remove(&id);
        }
        if self.stopping.load(Ordering::SeqCst) {
            return Err(McpError::new(ERR_NOT_READY, "server stopping")
                .with_data(json!({ "retryAfterMs": 5000 })));
        }
        Err(McpError::new(
            ERR_TIMEOUT,
            format!("tool call timed out after {}s", timeout.as_secs()),
        )
        .with_data(json!({ "timeoutMs": timeout.as_millis() as u64 })))
    }
}

pub struct McpInner {
    pub core: Option<Arc<McpCore>>,
    pub server: Option<McpServerHandle>,
    pub endpoint_file: Option<PathBuf>,
    pub started_at: Option<String>,
    /// [D74] 用户设的每分钟调用上限(偏好镜像;服务重建时重新施加)
    pub calls_per_minute: u32,
}

pub struct McpState {
    pub inner: Mutex<McpInner>,
    pub bridge: Arc<PageBridge>,
}

impl Default for McpState {
    fn default() -> Self {
        Self {
            inner: Mutex::new(McpInner {
                core: None,
                server: None,
                endpoint_file: None,
                started_at: None,
                calls_per_minute: RATE_PER_MINUTE as u32,
            }),
            bridge: Arc::new(PageBridge::default()),
        }
    }
}

fn env_kill_switch() -> bool {
    std::env::var("HOROSA_MCP_SERVER")
        .map(|v| v == "0")
        .unwrap_or(false)
}

fn preferred_port() -> u16 {
    std::env::var("HOROSA_MCP_PORT")
        .ok()
        .and_then(|v| v.parse::<u16>().ok())
        .filter(|p| *p > 0)
        .unwrap_or(MCP_DEFAULT_PORT)
}

fn config_dir(app: &tauri::AppHandle) -> Result<PathBuf> {
    use tauri::Manager;
    Ok(app.path().app_config_dir()?)
}

fn token_path(app: &tauri::AppHandle) -> Result<PathBuf> {
    Ok(config_dir(app)?.join(MCP_TOKEN_FILE))
}

fn endpoint_path(app: &tauri::AppHandle) -> Result<PathBuf> {
    Ok(config_dir(app)?.join(MCP_ENDPOINT_FILE))
}

fn load_or_create_token(app: &tauri::AppHandle) -> Result<String> {
    let path = token_path(app)?;
    if let Ok(existing) = fs::read_to_string(&path) {
        let t = existing.trim().to_string();
        if t.len() >= 32 {
            return Ok(t);
        }
    }
    let token = generate_token()?;
    write_private_file(&path, token.as_bytes())?;
    Ok(token)
}

fn now_iso() -> String {
    let secs = std::time::SystemTime::now()
        .duration_since(std::time::UNIX_EPOCH)
        .map(|d| d.as_secs())
        .unwrap_or(0);
    format!("{}", secs)
}

/// 由页面总开关 + 子开关 + 环境 kill-switch 共同决定是否应运行。
pub fn should_run(agent_enabled: bool, mcp_enabled: bool) -> bool {
    agent_enabled && mcp_enabled && !env_kill_switch()
}

fn start_locked(app: &tauri::AppHandle, state: &McpState, inner: &mut McpInner) -> Result<u16> {
    if let Some(s) = inner.server.as_ref() {
        return Ok(s.port());
    }
    let token = load_or_create_token(app)?;
    let core = match inner.core.as_ref() {
        Some(c) => {
            c.set_token(token.clone());
            Arc::clone(c)
        }
        None => Arc::new(McpCore::new(
            token.clone(),
            app.package_info().version.to_string(),
        )),
    };
    core.set_calls_per_minute(inner.calls_per_minute);
    inner.core = Some(Arc::clone(&core));
    state.bridge.attach(app.clone());
    let version = app.package_info().version.to_string();
    let dispatcher: Arc<dyn PageDispatcher> = Arc::clone(&state.bridge) as Arc<dyn PageDispatcher>;
    let handle = start_server(preferred_port(), core, dispatcher, version.clone())?;
    let port = handle.port();
    let ep = choose_endpoint_path(&endpoint_path(app)?, port);
    let info = EndpointInfo {
        url: format!("http://127.0.0.1:{}/mcp", port),
        token,
        port,
        pid: std::process::id(),
        app_version: version,
        started_at: now_iso(),
    };
    write_endpoint_file(&ep, &info)?;
    inner.endpoint_file = Some(ep);
    inner.started_at = Some(info.started_at.clone());
    inner.server = Some(handle);
    crate::ledger_mark("rust.mcp_server_started", Some(json!({ "port": port })));
    Ok(port)
}

fn stop_locked(state: &McpState, inner: &mut McpInner) {
    // 顺序:先关门(stopping+shutdown 位)→ 再失败在途 → 有界等待 worker;反过来会留下 ≤250ms 的窗口
    // 让新请求进 pending 后死等满超时(曾实抓:关开关卡住主线程 120s)
    state.bridge.set_stopping(true);
    if let Some(s) = inner.server.as_ref() {
        s.signal_stop();
    }
    state.bridge.fail_all_pending(
        McpError::new(ERR_NOT_READY, "server stopping").with_data(json!({ "retryAfterMs": 5000 })),
    );
    if let Some(s) = inner.server.take() {
        let port = s.port();
        let clean = s.stop();
        crate::ledger_mark(
            "rust.mcp_server_stopped",
            Some(json!({ "port": port, "clean": clean })),
        );
    }
    if let Some(ep) = inner.endpoint_file.take() {
        remove_endpoint_file_if_owned(&ep);
    }
    inner.started_at = None;
    if let Some(core) = inner.core.as_ref() {
        core.invalidate_tools_cache();
    }
    state.bridge.set_stopping(false);
}

/// 壳启动:清扫陈旧端点文件;两开关皆开才起。
pub fn setup_on_launch(app: &tauri::AppHandle, agent_enabled: bool, mcp_enabled: bool) {
    use tauri::Manager;
    if let Ok(ep) = endpoint_path(app) {
        sweep_stale_endpoint_file(&ep);
    }
    let Some(state) = app.try_state::<McpState>() else {
        return;
    };
    state.bridge.attach(app.clone());
    if !should_run(agent_enabled, mcp_enabled) {
        return;
    }
    // 尾表达式里的临时 MutexGuard 会活过 `state`(借用检查报 E0597)→ 先落成具名局部再解构
    let guard = state.inner.lock();
    if let Ok(mut inner) = guard {
        if let Err(e) = start_locked(app, &state, &mut inner) {
            crate::ledger_mark(
                "rust.mcp_server_start_failed",
                Some(json!({ "error": e.to_string() })),
            );
        }
    }
}

pub fn stop_on_exit(app: &tauri::AppHandle) {
    use tauri::Manager;
    let Some(state) = app.try_state::<McpState>() else {
        return;
    };
    let guard = state.inner.lock();
    if let Ok(mut inner) = guard {
        stop_locked(&state, &mut inner);
    }
}

pub fn status_json(
    app: &tauri::AppHandle,
    state: &McpState,
    agent_enabled: bool,
    mcp_enabled: bool,
) -> Value {
    let inner = state.inner.lock().ok();
    let calls_per_minute = inner
        .as_ref()
        .map(|i| {
            i.core
                .as_ref()
                .map(|c| c.calls_per_minute())
                .unwrap_or(i.calls_per_minute)
        })
        .unwrap_or(RATE_PER_MINUTE as u32);
    let modern_on = inner
        .as_ref()
        .and_then(|i| i.core.as_ref().map(|c| c.modern_enabled()))
        .unwrap_or_else(|| {
            std::env::var("HOROSA_MCP_MODERN")
                .map(|v| v != "0")
                .unwrap_or(true)
        });
    let (running, port, token, endpoint_file) = match inner.as_ref() {
        Some(i) => (
            i.server.is_some(),
            i.server.as_ref().map(|s| s.port()).unwrap_or(0),
            i.core.as_ref().map(|c| c.token()).unwrap_or_default(),
            i.endpoint_file
                .as_ref()
                .map(|p| p.display().to_string())
                .unwrap_or_default(),
        ),
        None => (false, 0, String::new(), String::new()),
    };
    let ep = endpoint_path(app)
        .map(|p| p.display().to_string())
        .unwrap_or_default();
    json!({
        "enabled": mcp_enabled,
        "agentEnabled": agent_enabled,
        "killSwitch": env_kill_switch(),
        "running": running,
        "port": port,
        "url": if running { format!("http://127.0.0.1:{}/mcp", port) } else { String::new() },
        // 令牌不随状态查询外泄:状态是面板轮询/任何页面脚本都能拿的宽面,令牌只在用户点「复制」时经
        // reveal_token 按需取一次(缩小注入脚本可达的暴露面)。
        "token": String::new(),
        "hasToken": running && !token.is_empty(),
        // [D74] calls-per-minute in effect (mirror of the page-side external policy)
        "callsPerMinute": calls_per_minute,
        "modern": modern_on,
        "endpointFile": if running { endpoint_file } else { ep },
        // [批三④] 本 App 二进制路径:给 stdio 代理形态的客户端配置(command/args)用;非秘密
        "binaryPath": std::env::current_exe().map(|p| p.display().to_string()).unwrap_or_default(),
        "pageReady": state.bridge.is_ready(),
    })
}

/// 按需取令牌(仅服务运行中);面板「复制 Codex/Claude 配置 / 复制令牌」按钮专用。
pub fn reveal_token(state: &McpState) -> Option<String> {
    let inner = state.inner.lock().ok()?;
    if inner.server.is_none() {
        return None;
    }
    inner
        .core
        .as_ref()
        .map(|c| c.token())
        .filter(|t| !t.is_empty())
}

/// [D74] 施加「每分钟调用上限」:记进 inner(服务重建时重施)并立即作用于在跑的核;回实际生效值
pub fn apply_limits(state: &McpState, calls_per_minute: u32) -> Result<u32> {
    let mut inner = state
        .inner
        .lock()
        .map_err(|_| anyhow!("mcp state poisoned"))?;
    let n = calls_per_minute.clamp(1, RATE_MAX_PER_MINUTE as u32);
    inner.calls_per_minute = n;
    if let Some(core) = inner.core.as_ref() {
        core.set_calls_per_minute(n);
    }
    Ok(n)
}

pub fn apply_enabled(
    app: &tauri::AppHandle,
    state: &McpState,
    agent_enabled: bool,
    mcp_enabled: bool,
) -> Result<()> {
    let mut inner = state
        .inner
        .lock()
        .map_err(|_| anyhow!("mcp state poisoned"))?;
    if let Some(core) = inner.core.as_ref() {
        core.invalidate_tools_cache();
    }
    if should_run(agent_enabled, mcp_enabled) {
        start_locked(app, state, &mut inner)?;
    } else {
        stop_locked(state, &mut inner);
    }
    Ok(())
}

pub fn rotate_token(app: &tauri::AppHandle, state: &McpState) -> Result<String> {
    let token = generate_token()?;
    write_private_file(&token_path(app)?, token.as_bytes())?;
    if let Ok(mut inner) = state.inner.lock() {
        if let Some(core) = inner.core.as_ref() {
            core.set_token(token.clone());
        }
        if let (Some(server), Some(ep)) = (inner.server.as_ref(), inner.endpoint_file.as_ref()) {
            let info = EndpointInfo {
                url: format!("http://127.0.0.1:{}/mcp", server.port()),
                token: token.clone(),
                port: server.port(),
                pid: std::process::id(),
                app_version: app.package_info().version.to_string(),
                started_at: inner.started_at.clone().unwrap_or_default(),
            };
            let _ = write_endpoint_file(ep, &info);
        }
        let _ = &mut inner;
    }
    Ok(token)
}

// ───────────────────────── 单测(协议核 + 传输,假页面) ─────────────────────────
#[cfg(test)]
mod tests {
    use super::*;
    use std::io::{BufRead, BufReader};
    use std::net::TcpStream;

    struct FakePage {
        tools: Vec<Value>,
        fail_with: Option<McpError>,
    }

    impl PageDispatcher for FakePage {
        fn dispatch(
            &self,
            method: &str,
            params: Value,
            _timeout: Duration,
        ) -> std::result::Result<Value, McpError> {
            if let Some(e) = &self.fail_with {
                return Err(e.clone());
            }
            match method {
                "tools/list" => Ok(json!({ "tools": self.tools })),
                // [P5] 资源/提示:页面侧回体形状(resources/read 对 horosa://bad 故意回畸形,验传输层不当成功)
                "resources/list" => Ok(
                    json!({ "resources": [{ "uri": "horosa://chart/local-1", "name": "张三", "mimeType": "text/plain" }] }),
                ),
                "resources/templates/list" => Ok(
                    json!({ "resourceTemplates": [{ "uriTemplate": "horosa://chart/{cid}", "name": "命盘" }] }),
                ),
                "resources/read" => {
                    if params.get("uri").and_then(|v| v.as_str()) == Some("horosa://bad") {
                        return Ok(json!({ "oops": true }));
                    }
                    Ok(
                        json!({ "contents": [{ "uri": params.get("uri").cloned().unwrap_or(Value::Null), "mimeType": "text/plain", "text": "snapshot" }] }),
                    )
                }
                "prompts/list" => Ok(
                    json!({ "prompts": [{ "name": "technique:bazi", "description": "八字提示卡" }] }),
                ),
                "prompts/get" => Ok(
                    json!({ "description": "d", "messages": [{ "role": "user", "content": { "type": "text", "text": "x" } }] }),
                ),
                "tools/call" => Ok(
                    json!({ "content": [{ "type": "text", "text": format!("called {}", params["name"]) }], "structuredContent": { "echo": params["arguments"] }, "isError": false }),
                ),
                _ => Err(McpError::new(ERR_METHOD_NOT_FOUND, "nope")),
            }
        }
    }

    fn fake_tools() -> Vec<Value> {
        vec![
            json!({ "name": "list_records", "level": "read", "description": "d", "inputSchema": {"type":"object"}, "annotations": {"readOnlyHint": true} }),
            json!({ "name": "create_chart_record", "level": "additive", "description": "d", "inputSchema": {"type":"object"} }),
            json!({ "name": "delete_chart", "level": "additive", "description": "d", "inputSchema": {"type":"object"} }),
            json!({ "name": "wipe_all", "level": "destructive", "description": "d", "inputSchema": {"type":"object"} }),
            json!({ "name": "Bad-Name", "level": "read", "description": "d", "inputSchema": {"type":"object"} }),
        ]
    }

    fn core() -> McpCore {
        McpCore::new(
            "tok_ABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789".to_string(),
            "9.9.9".to_string(),
        )
    }

    #[test]
    fn constant_time_eq_and_bearer() {
        assert!(constant_time_eq(b"abc", b"abc"));
        assert!(!constant_time_eq(b"abc", b"abd"));
        assert!(!constant_time_eq(b"abc", b"abcd"));
        assert!(bearer_allowed(Some("Bearer tok"), "tok"));
        assert!(bearer_allowed(Some("bearer tok"), "tok"));
        assert!(!bearer_allowed(Some("Bearer tok2"), "tok"));
        assert!(!bearer_allowed(Some("Basic tok"), "tok"));
        assert!(!bearer_allowed(None, "tok"));
        assert!(!bearer_allowed(Some("Bearer "), ""));
    }

    #[test]
    fn origin_and_host_gates() {
        assert!(origin_allowed(None));
        assert!(origin_allowed(Some("http://127.0.0.1:39991")));
        assert!(origin_allowed(Some("http://localhost")));
        assert!(!origin_allowed(Some("https://evil.example")));
        assert!(!origin_allowed(Some("null")));
        assert!(!origin_allowed(Some("http://127.0.0.1.evil.example")));
        assert!(host_allowed(None));
        assert!(host_allowed(Some("127.0.0.1:39991")));
        assert!(host_allowed(Some("localhost:1")));
        assert!(!host_allowed(Some("evil.example:80")));
        assert!(protocol_version_allowed(Some("2025-06-18")));
        assert!(!protocol_version_allowed(Some("1999-01-01")));
        let c = core();
        assert_eq!(
            c.gate(Some("evil:1"), None, Some("Bearer x"), None)
                .unwrap_err()
                .0,
            403
        );
        assert_eq!(
            c.gate(None, Some("https://evil"), Some("Bearer x"), None)
                .unwrap_err()
                .0,
            403
        );
        assert_eq!(
            c.gate(None, None, Some("Bearer wrong"), None)
                .unwrap_err()
                .0,
            401
        );
        assert_eq!(
            c.gate(
                None,
                None,
                Some(&format!("Bearer {}", c.token())),
                Some("bad")
            )
            .unwrap_err()
            .0,
            400
        );
        assert!(c
            .gate(
                Some("127.0.0.1:1"),
                Some("http://localhost:1"),
                Some(&format!("Bearer {}", c.token())),
                Some("2024-11-05")
            )
            .is_ok());
    }

    #[test]
    fn filter_tools_only_read_and_additive_with_sane_names() {
        let names: Vec<String> = filter_tools(&fake_tools())
            .iter()
            .map(|t| t["name"].as_str().unwrap().to_string())
            .collect();
        assert_eq!(
            names,
            vec![
                "list_records".to_string(),
                "create_chart_record".to_string()
            ]
        );
    }

    #[test]
    fn rotate_token_invalidates_old_bearer() {
        // 「轮换令牌,旧令牌立即失效」此前无判据:set_token 后旧 Bearer 必 401、新 Bearer 放行
        let c = core();
        let old = c.token();
        assert!(c
            .gate(
                Some("127.0.0.1:1"),
                None,
                Some(&format!("Bearer {}", old)),
                Some("2024-11-05")
            )
            .is_ok());
        let fresh = generate_token().unwrap();
        c.set_token(fresh.clone());
        assert_eq!(
            c.gate(
                Some("127.0.0.1:1"),
                None,
                Some(&format!("Bearer {}", old)),
                Some("2024-11-05")
            )
            .unwrap_err()
            .0,
            401
        );
        assert!(c
            .gate(
                Some("127.0.0.1:1"),
                None,
                Some(&format!("Bearer {}", fresh)),
                Some("2024-11-05")
            )
            .is_ok());
        assert_eq!(c.token(), fresh);
    }

    #[test]
    fn token_is_base64url_32_bytes() {
        let t = generate_token().unwrap();
        assert_eq!(t.len(), 43);
        assert!(t
            .bytes()
            .all(|b| b.is_ascii_alphanumeric() || b == b'-' || b == b'_'));
        assert_eq!(base64url_no_pad(b"hello"), "aGVsbG8");
    }

    #[test]
    fn rpc_methods_and_errors() {
        let c = core();
        let page = FakePage {
            tools: fake_tools(),
            fail_with: None,
        };
        let init = c.handle_rpc(&json!({ "jsonrpc": "2.0", "id": 1, "method": "initialize", "params": { "protocolVersion": "2025-03-26" } }), &page).unwrap();
        assert_eq!(init["result"]["protocolVersion"], "2025-03-26");
        assert_eq!(init["result"]["serverInfo"]["name"], "horosa");
        assert_eq!(init["result"]["capabilities"]["tools"]["listChanged"], true); // [P5] v2:三面都推 list_changed
        let init2 = c.handle_rpc(&json!({ "jsonrpc": "2.0", "id": 2, "method": "initialize", "params": { "protocolVersion": "1999-01-01" } }), &page).unwrap();
        assert_eq!(init2["result"]["protocolVersion"], MCP_LATEST_PROTOCOL);
        assert_eq!(
            c.handle_rpc(
                &json!({ "jsonrpc": "2.0", "id": 3, "method": "ping" }),
                &page
            )
            .unwrap()["result"],
            json!({})
        );
        let list = c
            .handle_rpc(
                &json!({ "jsonrpc": "2.0", "id": 4, "method": "tools/list" }),
                &page,
            )
            .unwrap();
        assert_eq!(list["result"]["tools"].as_array().unwrap().len(), 2);
        assert!(list["result"]["tools"][0].get("level").is_none());
        let call = c.handle_rpc(&json!({ "jsonrpc": "2.0", "id": 5, "method": "tools/call", "params": { "name": "list_records", "arguments": { "kind": "chart" } } }), &page).unwrap();
        assert_eq!(call["result"]["isError"], false);
        assert_eq!(call["result"]["structuredContent"]["echo"]["kind"], "chart");
        let bad_name = c.handle_rpc(&json!({ "jsonrpc": "2.0", "id": 6, "method": "tools/call", "params": { "name": "delete_all", "arguments": {} } }), &page).unwrap();
        assert_eq!(bad_name["error"]["code"], ERR_INVALID_PARAMS);
        // resources/* 与 prompts/* 已实装([P5]);仍未支持的方法照旧 -32601
        let unknown = c
            .handle_rpc(
                &json!({ "jsonrpc": "2.0", "id": 7, "method": "roots/list" }),
                &page,
            )
            .unwrap();
        assert_eq!(unknown["error"]["code"], ERR_METHOD_NOT_FOUND);
        assert!(c
            .handle_rpc(
                &json!({ "jsonrpc": "2.0", "method": "notifications/initialized" }),
                &page
            )
            .is_none());
        let invalid = c
            .handle_rpc(&json!({ "id": 8, "method": "ping" }), &page)
            .unwrap();
        assert_eq!(invalid["error"]["code"], ERR_INVALID_REQUEST);
        let not_ready = McpCore::new("t".into(), "1".into());
        let down = FakePage {
            tools: vec![],
            fail_with: Some(
                McpError::new(ERR_NOT_READY, "x").with_data(json!({ "retryAfterMs": 1500 })),
            ),
        };
        let r = not_ready.handle_rpc(&json!({ "jsonrpc": "2.0", "id": 9, "method": "tools/call", "params": { "name": "list_records", "arguments": {} } }), &down).unwrap();
        assert_eq!(r["error"]["code"], ERR_NOT_READY);
        assert_eq!(r["error"]["data"]["retryAfterMs"], 1500);
    }

    /// [D74] 令牌桶跟随用户设置:1/分钟 ⇒ 第二次即拒;600/分钟 ⇒ 100 连发不拒;非法值钳到 1..600;桶余额超过新突发额即截断
    #[test]
    fn rate_bucket_follows_configured_limit() {
        let mut b = RateBucket::new();
        assert_eq!(b.limit(), 60);
        assert_eq!(b.set_limit(1), 1);
        assert!(b.take(), "钳到 1/分钟后仍有 10 个突发额");
        for _ in 0..9 {
            assert!(b.take());
        }
        assert!(!b.take(), "1/分钟:突发额耗尽后立即拒");
        assert_eq!(b.set_limit(600), 600);
        for i in 0..100 {
            assert!(b.take(), "600/分钟 突发 100:第 {} 次不该被拒", i);
        }
        assert_eq!(b.set_limit(0), 1);
        assert_eq!(b.set_limit(99_999), 600);
        let c = core();
        assert_eq!(c.calls_per_minute(), 60);
        assert_eq!(c.set_calls_per_minute(120), 120);
        assert_eq!(c.calls_per_minute(), 120);
        let st = McpState::default();
        assert_eq!(apply_limits(&st, 5000).unwrap(), 600);
        assert_eq!(st.inner.lock().unwrap().calls_per_minute, 600);
    }

    #[test]
    fn rate_bucket_limits_burst() {
        let c = core();
        let page = FakePage {
            tools: fake_tools(),
            fail_with: None,
        };
        let mut limited = 0;
        for i in 0..14 {
            let r = c.handle_rpc(&json!({ "jsonrpc": "2.0", "id": i, "method": "tools/call", "params": { "name": "list_records", "arguments": {} } }), &page).unwrap();
            if r.get("error")
                .map(|e| e["code"] == ERR_RATE_LIMITED)
                .unwrap_or(false)
            {
                limited += 1;
            }
        }
        assert!(
            limited >= 3,
            "burst 10 → 14 次里至少 3 次限流, got {}",
            limited
        );
    }

    #[test]
    fn endpoint_file_private_and_atomic_and_sweep() {
        let dir = std::env::temp_dir().join(format!("horosa-mcp-test-{}", std::process::id()));
        let _ = fs::remove_dir_all(&dir);
        let path = dir.join(MCP_ENDPOINT_FILE);
        let info = EndpointInfo {
            url: "http://127.0.0.1:1/mcp".into(),
            token: "t".into(),
            port: 1,
            pid: 4_000_000_000,
            app_version: "1".into(),
            started_at: "0".into(),
        };
        write_endpoint_file(&path, &info).unwrap();
        assert!(path.exists());
        assert!(!path.with_extension("tmp").exists());
        #[cfg(unix)]
        {
            use std::os::unix::fs::PermissionsExt;
            assert_eq!(
                fs::metadata(&path).unwrap().permissions().mode() & 0o777,
                0o600
            );
        }
        let v: Value = serde_json::from_str(&fs::read_to_string(&path).unwrap()).unwrap();
        assert_eq!(v["schema"], 1);
        assert_eq!(v["protocolVersion"], MCP_LATEST_PROTOCOL);
        // pid 不存活 → 清扫
        assert!(sweep_stale_endpoint_file(&path));
        assert!(!path.exists());
        let _ = fs::remove_dir_all(&dir);
    }

    #[test]
    fn dispatch_script_double_escapes() {
        let s = PageBridge::dispatch_script(
            &json!({ "id": 1, "method": "tools/call", "params": { "name": "x", "arguments": { "q": "he said \"hi\"\n</script>" } } }),
        );
        assert!(s.starts_with("(function(){try{var r=JSON.parse(\""));
        assert!(s.contains("__horosaAgentTool"));
        assert!(s.contains("__horosaPendingAgentTools"));
        assert!(!s.contains("</script>"));
        assert!(
            s.contains("<\\/script>")
                || s.contains("\\u003c/script")
                || s.contains("<\\\\/script>")
                || !s.contains("</script")
        );
    }

    fn http(port: u16, req: &str) -> (u16, String) {
        let mut stream = TcpStream::connect(("127.0.0.1", port)).unwrap();
        stream.write_all(req.as_bytes()).unwrap();
        stream.flush().unwrap();
        let mut reader = BufReader::new(stream);
        let mut status_line = String::new();
        reader.read_line(&mut status_line).unwrap();
        let status: u16 = status_line
            .split_whitespace()
            .nth(1)
            .unwrap_or("0")
            .parse()
            .unwrap_or(0);
        let mut content_length = 0usize;
        loop {
            let mut line = String::new();
            reader.read_line(&mut line).unwrap();
            if line == "\r\n" || line.is_empty() {
                break;
            }
            let lower = line.to_ascii_lowercase();
            if let Some(v) = lower.strip_prefix("content-length:") {
                content_length = v.trim().parse().unwrap_or(0);
            }
        }
        let mut body = vec![0u8; content_length];
        if content_length > 0 {
            reader.read_exact(&mut body).unwrap();
        }
        (status, String::from_utf8_lossy(&body).to_string())
    }

    fn post(port: u16, headers: &str, body: &str) -> (u16, String) {
        http(port, &format!("POST /mcp HTTP/1.1\r\nHost: 127.0.0.1:{}\r\nContent-Type: application/json\r\nContent-Length: {}\r\n{}\r\n{}", port, body.len(), headers, body))
    }

    #[test]
    fn filter_tools_drops_ext_prefix_and_write_levels() {
        let raw = vec![
            json!({ "name": "list_records", "level": "read" }),
            json!({ "name": "create_chart_record", "level": "additive" }),
            json!({ "name": "ext_time_get_current_time", "level": "read" }),
            json!({ "name": "delete_record", "level": "additive" }),
        ];
        let kept: Vec<String> = filter_tools(&raw)
            .iter()
            .map(|t| t["name"].as_str().unwrap().to_string())
            .collect();
        assert_eq!(
            kept,
            vec![
                "list_records".to_string(),
                "create_chart_record".to_string()
            ]
        );
        assert!(!tool_name_ok("ext_anything"));
        assert!(tool_name_ok("list_records"));
    }

    #[test]
    fn resources_prompts_methods_dispatch_to_page_and_capabilities_advertise_them() {
        let c = core();
        let page = FakePage {
            tools: fake_tools(),
            fail_with: None,
        };
        let init = c
            .handle_rpc(
                &json!({ "jsonrpc": "2.0", "id": 1, "method": "initialize", "params": {} }),
                &page,
            )
            .unwrap();
        let caps = &init["result"]["capabilities"];
        assert_eq!(caps["tools"]["listChanged"], true);
        assert_eq!(caps["resources"]["listChanged"], true);
        assert_eq!(caps["resources"]["subscribe"], false);
        assert_eq!(caps["prompts"]["listChanged"], true);
        assert!(caps.get("logging").is_some());
        for (method, key) in [
            ("resources/list", "resources"),
            ("resources/templates/list", "resourceTemplates"),
            ("resources/read", "contents"),
            ("prompts/list", "prompts"),
            ("prompts/get", "messages"),
        ] {
            let v = c
                .handle_rpc(
                    &json!({ "jsonrpc": "2.0", "id": 2, "method": method, "params": {} }),
                    &page,
                )
                .unwrap();
            assert!(
                v["result"][key].is_array(),
                "{} 应转发页面并回 {}",
                method,
                key
            );
        }
        // 页面回体缺约定字段 → 内部错误(不把畸形结果当成功)
        let bad = c.handle_rpc(&json!({ "jsonrpc": "2.0", "id": 3, "method": "resources/read", "params": { "uri": "horosa://bad" } }), &page);
        assert!(
            bad.unwrap()["error"].is_object(),
            "页面回体缺 contents → 内部错误,不当成功"
        );
        // logging/setLevel:合法级别 OK,非法拒
        assert!(c.handle_rpc(&json!({ "jsonrpc": "2.0", "id": 4, "method": "logging/setLevel", "params": { "level": "debug" } }), &page).unwrap()["result"].is_object());
        assert_eq!(c.log_level(), "debug");
        assert!(c.handle_rpc(&json!({ "jsonrpc": "2.0", "id": 5, "method": "logging/setLevel", "params": { "level": "loud" } }), &page).unwrap()["error"].is_object());
    }

    #[test]
    fn session_id_optional_and_delete_removes() {
        let c = core();
        assert!(c.session_allowed(None), "不带会话头一律放行(旧客户端)");
        assert!(!c.session_allowed(Some("nope")), "带未知会话 → 拒");
        let id = c.new_session();
        assert!(c.session_allowed(Some(&id)));
        assert_eq!(c.session_count(), 1);
        assert!(c.drop_session(Some(&id)));
        assert!(!c.session_allowed(Some(&id)));
        assert_eq!(c.session_count(), 0);
        for _ in 0..(MAX_SESSIONS + 5) {
            c.new_session();
        }
        assert_eq!(c.session_count(), MAX_SESSIONS, "会话表封顶");
    }

    #[test]
    fn sse_subscribe_capped_and_notify_broadcasts() {
        let c = core();
        let mut subs = Vec::new();
        for _ in 0..MAX_SSE_CLIENTS {
            subs.push(c.sse_subscribe().expect("应能订阅"));
        }
        assert_eq!(c.sse_count(), MAX_SSE_CLIENTS);
        assert!(
            c.sse_subscribe().is_none(),
            "超过上限 → None(HTTP 层回 429)"
        );
        assert_eq!(
            c.notify("notifications/tools/list_changed", json!({})),
            MAX_SSE_CLIENTS
        );
        for rx in &subs {
            let hello = rx
                .recv_timeout(Duration::from_secs(2))
                .expect("订阅即收到 connected 注释帧(触发 header flush)");
            assert!(hello.starts_with(": "), "首帧应是注释帧:{:?}", hello);
            let frame = rx.recv_timeout(Duration::from_secs(2)).expect("应收到广播");
            assert!(frame.starts_with("event: message\ndata: "));
            assert!(frame.ends_with("\n\n"));
            assert!(frame.contains("notifications/tools/list_changed"));
            assert!(frame.contains("\"jsonrpc\":\"2.0\""));
            assert!(!frame.contains("\"id\""), "通知不带 id");
        }
        // 订阅者掉线 → 广播时摘掉
        subs.truncate(1);
        assert_eq!(
            c.notify("notifications/resources/list_changed", json!({})),
            1
        );
        let _ = subs[0].recv_timeout(Duration::from_secs(2));
        assert_eq!(c.sse_count(), 1);
    }

    // ───────────────────── [L1·阶段 2] 通知洪泛 / 会话过期 / 会话 churn ─────────────────────

    /// 🟢 订阅者不消费也绝不拖垮广播:队列(SSE_QUEUE=32,订阅时那条 `: connected` 已占一格)
    /// 灌满后 `notify` 只是不再把这个订阅者计进 sent,既不断开也不阻塞;把队列排空后又照常计入。
    #[test]
    fn notify_full_queue_keeps_subscriber_and_counts_zero() {
        let c = core();
        let rx = c.sse_subscribe().expect("应能订阅");
        let mut sent_log = Vec::new();
        for i in 0..(SSE_QUEUE + 1) {
            sent_log.push(c.notify("notifications/tools/list_changed", json!({ "i": i })));
        }
        assert_eq!(sent_log[0], 1, "第一帧必然送达");
        assert_eq!(
            *sent_log.last().unwrap(),
            0,
            "队列灌满后不再计入该订阅者:{:?}",
            sent_log
        );
        assert_eq!(c.sse_count(), 1, "队列满绝不摘订阅者(只有通道关掉才摘)");
        // 排空:1 条 `: connected` 注释帧 + SSE_QUEUE-1 条广播
        let mut drained = 0usize;
        while rx.try_recv().is_ok() {
            drained += 1;
        }
        assert_eq!(
            drained, SSE_QUEUE,
            "队列容量恒为 SSE_QUEUE,实排空 {}",
            drained
        );
        assert_eq!(
            c.notify("notifications/resources/list_changed", json!({})),
            1,
            "排空后又能送达"
        );
        assert_eq!(c.sse_count(), 1);
    }

    /// 🟢 通知风暴:4 个订阅者其中 2 个把 receiver 丢掉(= 客户端断线),1000 帧广播必须
    /// 既不阻塞也不 panic,且断线的两个在第一帧就被摘掉。
    #[test]
    fn notify_storm_1000_frames_never_blocks() {
        let c = core();
        let keep_a = c.sse_subscribe().expect("订阅 1");
        let drop_a = c.sse_subscribe().expect("订阅 2");
        let keep_b = c.sse_subscribe().expect("订阅 3");
        let drop_b = c.sse_subscribe().expect("订阅 4");
        assert_eq!(c.sse_count(), MAX_SSE_CLIENTS);
        drop(drop_a);
        drop(drop_b);
        let t0 = Instant::now();
        for i in 0..1000 {
            c.notify("notifications/tools/list_changed", json!({ "i": i }));
        }
        let cost = t0.elapsed();
        assert!(
            cost < Duration::from_millis(200),
            "1000 帧广播必须无阻塞完成,实耗 {:?}",
            cost
        );
        assert_eq!(c.sse_count(), 2, "掉线的订阅者在广播时被摘掉,活的一个不少");
        // 活着的两个仍能读到帧(队列封顶,但通道没坏)
        assert!(keep_a.try_recv().is_ok());
        assert!(keep_b.try_recv().is_ok());
    }

    /// 🔴 先红:会话只有「表满 64 条挤最旧」,没有任何时效。
    ///
    /// 证据:`McpCore::sessions` 存了 `(String, Instant)`(mcp_server.rs:362),但
    /// `session_allowed`(mcp_server.rs:436)只 `iter().any(|(x, _)| x == id)` —— 第二元
    /// 从头到尾没人读;全模块也没有 `SESSION_TTL` 常量,`new_session` 唯一的淘汰手段是
    /// `list.remove(0)`(表满时,mcp_server.rs:429)。于是一个很久以前发出的 Mcp-Session-Id
    /// 永久有效,拿到过一次会话头就能一直复用。
    ///
    /// 期望(守卫落地后):超过 `SESSION_TTL` 的会话既拒绝放行、也从表里剔除;
    /// 新发的会话不受影响。本用例用 `advance_session_clock` 测试缝拨快 25 小时,不必真的等。
    #[test]
    fn session_ttl_expired_rejected_and_pruned() {
        let c = core();
        let stale = c.new_session();
        assert!(c.session_allowed(Some(&stale)), "刚发出时当然放行");
        c.advance_session_clock(Duration::from_secs(25 * 3600));
        assert!(
            !c.session_allowed(Some(&stale)),
            "拨过 TTL 的会话必须被拒(当前只比对 id → 恒 true)"
        );
        let fresh = c.new_session();
        assert!(
            c.session_allowed(Some(&fresh)),
            "回归锁:拨表之后新发的会话仍须放行"
        );
        assert_eq!(
            c.session_count(),
            1,
            "过期会话必须被剔出表,不能靠 64 条封顶慢慢挤:{}",
            c.session_count()
        );
    }

    /// 🟢 会话 churn:1e4 次 `new_session` 后表长恒 ≤ MAX_SESSIONS,且总耗时有界。
    /// 每次建会话都要开一次 /dev/urandom 读 32 字节,本机实测 ~85ms;阈值按「不得退化成秒级」
    /// 定在 2s(≈23 倍余量),刻意不当微基准用——并行跑测时墙钟闸门收太紧只会制造假红。
    #[test]
    fn stress_sessions_churn_10k() {
        let c = core();
        let t0 = Instant::now();
        for _ in 0..10_000 {
            c.new_session();
            assert!(c.session_count() <= MAX_SESSIONS);
        }
        let cost = t0.elapsed();
        assert_eq!(c.session_count(), MAX_SESSIONS, "表长恒定在封顶值");
        assert!(
            cost < Duration::from_millis(2000),
            "1e4 次建会话必须有界,实耗 {:?}",
            cost
        );
        // 表里留下的必须是最后 MAX_SESSIONS 个(最旧的被挤掉)——顺带证明 remove(0) 语义没被改坏
        let last = c.new_session();
        assert!(c.session_allowed(Some(&last)));
        assert_eq!(c.session_count(), MAX_SESSIONS);
    }

    #[test]
    fn sse_get_streams_keepalive_and_notifications() {
        let c = Arc::new(core());
        let token = c.token();
        let page: Arc<dyn PageDispatcher> = Arc::new(FakePage {
            tools: fake_tools(),
            fail_with: None,
        });
        let handle = start_server(0, Arc::clone(&c), page, "9.9.9".into()).unwrap();
        let port = handle.port();
        let mut stream = TcpStream::connect(("127.0.0.1", port)).unwrap();
        stream
            .write_all(
                format!(
                    "GET /mcp HTTP/1.1\r\nHost: 127.0.0.1:{}\r\nAuthorization: Bearer {}\r\nAccept: text/event-stream\r\n\r\n",
                    port, token
                )
                .as_bytes(),
            )
            .unwrap();
        stream.flush().unwrap();
        stream
            .set_read_timeout(Some(Duration::from_secs(5)))
            .unwrap();
        let mut reader = BufReader::new(stream);
        let mut status_line = String::new();
        reader.read_line(&mut status_line).unwrap();
        assert!(status_line.contains(" 200 "), "SSE 应 200:{}", status_line);
        let mut saw_content_type = false;
        loop {
            let mut line = String::new();
            reader.read_line(&mut line).unwrap();
            if line.to_ascii_lowercase().starts_with("content-type:") {
                saw_content_type = line.to_ascii_lowercase().contains("text/event-stream");
            }
            if line == "\r\n" {
                break;
            }
        }
        assert!(
            saw_content_type,
            "SSE 响应须 Content-Type: text/event-stream"
        );
        // SSE 占着连接时 POST 仍可服务(SSE 跑独立线程,不占 recv worker)
        let (st, _) = post(
            port,
            &format!("Authorization: Bearer {}\r\n", token),
            "{\"jsonrpc\":\"2.0\",\"id\":9,\"method\":\"ping\"}",
        );
        assert_eq!(st, 200, "SSE 连着时 POST 必须照常");
        // 页面侧变更 → 广播到达
        assert!(c.notify("notifications/tools/list_changed", json!({})) >= 1);
        let mut got = String::new();
        for _ in 0..8 {
            let mut line = String::new();
            if reader.read_line(&mut line).is_err() {
                break;
            }
            got.push_str(&line);
            if got.contains("list_changed") {
                break;
            }
        }
        assert!(got.contains("event: message"), "应收到 event 行:{:?}", got);
        assert!(
            got.contains("notifications/tools/list_changed"),
            "应收到通知:{:?}",
            got
        );
        handle.signal_stop();
        drop(reader);
    }

    #[test]
    fn http_transport_end_to_end_and_port_released_on_stop() {
        let c = Arc::new(core());
        let token = c.token();
        let page: Arc<dyn PageDispatcher> = Arc::new(FakePage {
            tools: fake_tools(),
            fail_with: None,
        });
        let handle = start_server(0, Arc::clone(&c), page, "9.9.9".into()).unwrap();
        let port = handle.port();
        assert!(port > 0);
        let (st, body) = http(
            port,
            &format!("GET /healthz HTTP/1.1\r\nHost: 127.0.0.1:{}\r\n\r\n", port),
        );
        assert_eq!(st, 200);
        assert!(body.contains("\"app\":\"horosa\""));
        // [P5] GET /mcp 已是 SSE 通道:门在语义之前——无令牌 → 401(不是 405/406)
        let (st, _) = http(
            port,
            &format!("GET /mcp HTTP/1.1\r\nHost: 127.0.0.1:{}\r\n\r\n", port),
        );
        assert_eq!(st, 401);
        // 带令牌但不声明 Accept: text/event-stream → 406
        let (st, _) = http(
            port,
            &format!(
                "GET /mcp HTTP/1.1\r\nHost: 127.0.0.1:{}\r\nAuthorization: Bearer {}\r\n\r\n",
                port, token
            ),
        );
        assert_eq!(st, 406);
        // PUT 仍是 405
        let (st, _) = http(port, &format!("PUT /mcp HTTP/1.1\r\nHost: 127.0.0.1:{}\r\nAuthorization: Bearer {}\r\nContent-Length: 0\r\n\r\n", port, token));
        assert_eq!(st, 405);
        let (st, _) = post(
            port,
            "",
            "{\"jsonrpc\":\"2.0\",\"id\":1,\"method\":\"ping\"}",
        );
        assert_eq!(st, 401);
        let (st, _) = post(
            port,
            &format!(
                "Authorization: Bearer {}\r\nOrigin: https://evil.example\r\n",
                token
            ),
            "{\"jsonrpc\":\"2.0\",\"id\":1,\"method\":\"ping\"}",
        );
        assert_eq!(st, 403);
        let auth = format!("Authorization: Bearer {}\r\n", token);
        let (st, body) = post(port, &auth, "{\"jsonrpc\":\"2.0\",\"id\":1,\"method\":\"initialize\",\"params\":{\"protocolVersion\":\"2025-06-18\"}}");
        assert_eq!(st, 200);
        assert!(body.contains("\"serverInfo\""));
        let (st, body) = post(
            port,
            &auth,
            "{\"jsonrpc\":\"2.0\",\"id\":2,\"method\":\"tools/list\"}",
        );
        assert_eq!(st, 200);
        let v: Value = serde_json::from_str(&body).unwrap();
        assert_eq!(v["result"]["tools"].as_array().unwrap().len(), 2);
        let (st, body) = post(port, &auth, "{\"jsonrpc\":\"2.0\",\"id\":3,\"method\":\"tools/call\",\"params\":{\"name\":\"create_chart_record\",\"arguments\":{\"name\":\"x\"}}}");
        assert_eq!(st, 200);
        assert!(body.contains("called \\\"create_chart_record\\\"") || body.contains("called"));
        let (st, body) = post(
            port,
            &auth,
            "[{\"jsonrpc\":\"2.0\",\"id\":1,\"method\":\"ping\"}]",
        );
        assert_eq!(st, 400);
        assert!(body.contains("-32600"));
        let (st, _) = post(port, &auth, "{bad json");
        assert_eq!(st, 400);
        let (st, _) = post(
            port,
            &auth,
            "{\"jsonrpc\":\"2.0\",\"method\":\"notifications/initialized\"}",
        );
        assert_eq!(st, 202);
        handle.stop();
        // 端口释放:关后可再绑(tiny_http 内部 accept 线程异步收口,最多等 2s)
        let mut rebind = std::net::TcpListener::bind(("127.0.0.1", port));
        for _ in 0..40 {
            if rebind.is_ok() {
                break;
            }
            thread::sleep(Duration::from_millis(50));
            rebind = std::net::TcpListener::bind(("127.0.0.1", port));
        }
        assert!(rebind.is_ok(), "port {} must be free after stop", port);
    }

    // ── 压测:并发洪泛 / 随机 RPC 体 / 随机 Origin·Host / 超大体 ──
    #[test]
    fn stress_concurrent_requests_all_answered_no_panic() {
        let c = Arc::new(core());
        let token = c.token();
        let page: Arc<dyn PageDispatcher> = Arc::new(FakePage {
            tools: fake_tools(),
            fail_with: None,
        });
        let handle = start_server(0, Arc::clone(&c), page, "9.9.9".into()).unwrap();
        let port = handle.port();
        let mut threads = Vec::new();
        for t in 0..12u32 {
            let token = token.clone();
            threads.push(thread::spawn(move || {
                let mut ok = 0u32;
                let mut limited = 0u32;
                for i in 0..25u32 {
                    let id = t * 1000 + i;
                    let body = match i % 3 {
                        0 => format!("{{\"jsonrpc\":\"2.0\",\"id\":{},\"method\":\"ping\"}}", id),
                        1 => format!("{{\"jsonrpc\":\"2.0\",\"id\":{},\"method\":\"tools/list\"}}", id),
                        _ => format!("{{\"jsonrpc\":\"2.0\",\"id\":{},\"method\":\"tools/call\",\"params\":{{\"name\":\"list_records\",\"arguments\":{{}}}}}}", id),
                    };
                    let (st, resp) = post(port, &format!("Authorization: Bearer {}\r\n", token), &body);
                    assert_eq!(st, 200, "thread {} req {} status", t, i);
                    let v: Value = serde_json::from_str(&resp).unwrap();
                    assert_eq!(v["id"], json!(id));
                    if v.get("error").map(|e| e["code"] == ERR_RATE_LIMITED).unwrap_or(false) { limited += 1; } else { ok += 1; }
                }
                (ok, limited)
            }));
        }
        let mut total_ok = 0;
        let mut total_limited = 0;
        for th in threads {
            let (o, l) = th.join().expect("worker thread panicked");
            total_ok += o;
            total_limited += l;
        }
        assert_eq!(total_ok + total_limited, 300);
        assert!(
            total_ok >= 200,
            "ping/list 不限流,至少 200 成功, got {}",
            total_ok
        );
        handle.stop();
    }

    #[test]
    fn stress_random_rpc_bodies_never_hang_or_panic() {
        let c = Arc::new(core());
        let token = c.token();
        let page: Arc<dyn PageDispatcher> = Arc::new(FakePage {
            tools: fake_tools(),
            fail_with: None,
        });
        let handle = start_server(0, Arc::clone(&c), page, "9.9.9".into()).unwrap();
        let port = handle.port();
        let auth = format!("Authorization: Bearer {}\r\n", token);
        let seeds: Vec<String> = vec![
            "{}".into(), "[]".into(), "null".into(), "42".into(), "\"s\"".into(), "{\"jsonrpc\":\"2.0\"}".into(),
            "{\"jsonrpc\":\"2.0\",\"id\":1}".into(), "{\"jsonrpc\":\"1.0\",\"id\":1,\"method\":\"ping\"}".into(),
            "{\"jsonrpc\":\"2.0\",\"id\":{\"a\":1},\"method\":\"ping\"}".into(),
            "{\"jsonrpc\":\"2.0\",\"id\":1,\"method\":\"tools/call\",\"params\":[]}".into(),
            "{\"jsonrpc\":\"2.0\",\"id\":1,\"method\":\"tools/call\",\"params\":{\"name\":\"../x\",\"arguments\":\"str\"}}".into(),
            "{\"jsonrpc\":\"2.0\",\"id\":1,\"method\":\"tools/call\",\"params\":{\"name\":\"list_records\",\"arguments\":{\"kind\":\"\u{0000}\"}}}".into(),
            "\u{feff}{\"jsonrpc\":\"2.0\",\"id\":1,\"method\":\"ping\"}".into(),
            "{\"jsonrpc\":\"2.0\",\"id\":1,\"method\":\"initialize\",\"params\":{\"protocolVersion\":123}}".into(),
            "\u{0}\u{1}\u{7f}".into(), "{\"jsonrpc\":\"2.0\",\"id\":1,\"method\":\"ping\",\"params\":{\"deep\":".to_string() + &"[".repeat(200) + &"]".repeat(200) + "}}",
        ];
        for (i, body) in seeds.iter().enumerate() {
            let (st, resp) = post(port, &auth, body);
            assert!(
                st == 200 || st == 202 || st == 400,
                "seed {} status {}",
                i,
                st
            );
            if st == 200 {
                let _: Value = serde_json::from_str(&resp).expect("200 body must be JSON");
            }
        }
        // 随机字节体 ×200
        let mut x: u64 = 0x9E3779B97F4A7C15;
        for _ in 0..200 {
            let mut bytes = Vec::new();
            x ^= x << 13;
            x ^= x >> 7;
            x ^= x << 17;
            let len = (x % 300) as usize;
            for k in 0..len {
                x ^= x << 13;
                x ^= x >> 7;
                x ^= x << 17;
                bytes.push(((x >> (k % 8 * 8)) & 0x7f) as u8);
            }
            let body = String::from_utf8_lossy(&bytes).to_string();
            let (st, _) = post(port, &auth, &body);
            assert!(
                st == 200 || st == 202 || st == 400,
                "random body status {}",
                st
            );
        }
        handle.stop();
    }

    #[test]
    fn stress_oversize_body_rejected_and_server_survives() {
        let c = Arc::new(core());
        let token = c.token();
        let page: Arc<dyn PageDispatcher> = Arc::new(FakePage {
            tools: fake_tools(),
            fail_with: None,
        });
        let handle = start_server(0, Arc::clone(&c), page, "9.9.9".into()).unwrap();
        let port = handle.port();
        let auth = format!("Authorization: Bearer {}\r\n", token);
        let big = format!(
            "{{\"jsonrpc\":\"2.0\",\"id\":1,\"method\":\"ping\",\"pad\":\"{}\"}}",
            "p".repeat(MAX_BODY_BYTES + 10)
        );
        let (st, _) = post(port, &auth, &big);
        assert_eq!(st, 413);
        let (st2, _) = post(
            port,
            &auth,
            "{\"jsonrpc\":\"2.0\",\"id\":2,\"method\":\"ping\"}",
        );
        assert_eq!(st2, 200);
        handle.stop();
    }

    #[test]
    fn stress_origin_and_host_fuzz_only_loopback_passes() {
        let mut x: u64 = 0x2545F4914F6CDD1D;
        let alphabet: Vec<char> = "abcdefghijklmnopqrstuvwxyz0123456789.:/-[]_%@"
            .chars()
            .collect();
        let mut passed = 0;
        for _ in 0..2000 {
            x ^= x << 13;
            x ^= x >> 7;
            x ^= x << 17;
            let len = (x % 24) as usize;
            let mut s = String::new();
            for k in 0..len {
                x ^= x << 13;
                x ^= x >> 7;
                x ^= x << 17;
                s.push(alphabet[(x as usize + k) % alphabet.len()]);
            }
            let origin = format!("http://{}", s);
            let allowed = origin_allowed(Some(&origin));
            // 参考模型(独立实现):authority = 首个 '/' 之前;方括号取括号内;否则取首个 ':' 之前
            let reference = |auth: &str| -> bool {
                let auth = auth.trim();
                let h = if let Some(rest) = auth.strip_prefix('[') {
                    rest.split(']').next().unwrap_or("").to_string()
                } else {
                    auth.split(':').next().unwrap_or("").to_string()
                };
                h == "127.0.0.1" || h == "localhost" || h == "::1"
            };
            let authority = s.split('/').next().unwrap_or("");
            let expected = reference(authority);
            assert_eq!(allowed, expected, "origin {}", origin);
            if allowed {
                passed += 1;
            }
            let host_ok = host_allowed(Some(&s));
            assert_eq!(host_ok, reference(&s), "host {}", s);
        }
        let _ = passed;
        for evil in [
            "http://127.0.0.1.evil.com",
            "http://localhost.evil.com",
            "http://evil.com/127.0.0.1",
            "http://127.0.0.1@evil.com",
            "file://",
            "chrome-extension://abc",
        ] {
            assert!(!origin_allowed(Some(evil)), "{}", evil);
        }
        assert!(origin_allowed(Some("http://[::1]:39991")));
    }

    #[test]
    fn stop_is_bounded_and_unready_bridge_rejects_immediately() {
        let bridge = PageBridge::default();
        // 未 attach、未就绪:dispatch 立刻 -32001,不进 pending
        let t0 = Instant::now();
        let r = bridge.dispatch("tools/list", json!({}), Duration::from_secs(30));
        assert_eq!(r.unwrap_err().code, ERR_NOT_READY);
        assert!(t0.elapsed() < Duration::from_millis(200));
        assert!(bridge.pending.lock().unwrap().is_empty());
        // stopping 位:同样立刻拒
        bridge.set_ready(true);
        bridge.set_stopping(true);
        let r2 = bridge.dispatch("tools/list", json!({}), Duration::from_secs(30));
        assert_eq!(r2.unwrap_err().code, ERR_NOT_READY);
        bridge.set_stopping(false);
        // set_ready(false) 让在途全部收到 -32001
        let (tx, rx) = mpsc::sync_channel(1);
        bridge.pending.lock().unwrap().insert(42, tx);
        bridge.set_ready(false);
        assert_eq!(
            rx.recv_timeout(Duration::from_millis(200))
                .unwrap()
                .unwrap_err()
                .code,
            ERR_NOT_READY
        );
        // 服务 stop 有界(空闲 worker 250ms 内退出)
        let c = Arc::new(core());
        let page: Arc<dyn PageDispatcher> = Arc::new(FakePage {
            tools: fake_tools(),
            fail_with: None,
        });
        let handle = start_server(0, c, page, "9.9.9".into()).unwrap();
        let t1 = Instant::now();
        assert!(handle.stop());
        assert!(t1.elapsed() < Duration::from_millis(1500));
    }

    #[test]
    fn endpoint_file_ownership_respected() {
        let dir = std::env::temp_dir().join(format!("horosa-mcp-own-{}", std::process::id()));
        let _ = fs::remove_dir_all(&dir);
        let base = dir.join(MCP_ENDPOINT_FILE);
        // 另一存活实例(本进程 pid 但假装是别人:用父进程 pid,必存活)
        let other = std::os::unix::process::parent_id();
        let info = EndpointInfo {
            url: "u".into(),
            token: "t".into(),
            port: 1,
            pid: other,
            app_version: "1".into(),
            started_at: "0".into(),
        };
        write_endpoint_file(&base, &info).unwrap();
        let chosen = choose_endpoint_path(&base, 39992);
        assert_ne!(chosen, base);
        assert!(chosen
            .to_string_lossy()
            .ends_with("mcp-endpoint-39992.json"));
        remove_endpoint_file_if_owned(&base);
        assert!(base.exists(), "不得删掉别人的端点文件");
        // 自己写的:可删
        let mine = EndpointInfo {
            url: "u".into(),
            token: "t".into(),
            port: 2,
            pid: std::process::id(),
            app_version: "1".into(),
            started_at: "0".into(),
        };
        write_endpoint_file(&base, &mine).unwrap();
        remove_endpoint_file_if_owned(&base);
        assert!(!base.exists());
        let _ = fs::remove_dir_all(&dir);
    }

    #[test]
    fn should_run_requires_both_switches() {
        std::env::remove_var("HOROSA_MCP_SERVER");
        assert!(!should_run(false, true));
        assert!(!should_run(true, false));
        assert!(should_run(true, true));
    }
    // ───────────────────────── [2026-07-28] 双纪元 ─────────────────────────
    fn modern_core() -> McpCore {
        let c = core();
        c.set_modern_enabled(true);
        c
    }
    fn meta(extra: Value) -> Value {
        let mut m = json!({ META_PROTOCOL_VERSION: "2026-07-28", META_CLIENT_INFO: { "name": "claude-code", "version": "2.1.240" }, META_CLIENT_CAPS: {} });
        if let (Some(a), Some(b)) = (m.as_object_mut(), extra.as_object()) {
            for (k, v) in b {
                a.insert(k.clone(), v.clone());
            }
        }
        m
    }
    fn mreq(id: u64, method: &str, params: Value) -> Value {
        let mut p = params;
        if let Some(obj) = p.as_object_mut() {
            obj.insert("_meta".into(), meta(json!({})));
        }
        json!({ "jsonrpc": "2.0", "id": id, "method": method, "params": p })
    }
    /// 读完整响应(状态 + 头 + Content-Length 体)
    fn http_full(port: u16, req: &str) -> (u16, Vec<String>, String) {
        let mut stream = TcpStream::connect(("127.0.0.1", port)).unwrap();
        stream.write_all(req.as_bytes()).unwrap();
        stream.flush().unwrap();
        let mut reader = BufReader::new(stream);
        let mut status_line = String::new();
        reader.read_line(&mut status_line).unwrap();
        let status: u16 = status_line
            .split_whitespace()
            .nth(1)
            .unwrap_or("0")
            .parse()
            .unwrap_or(0);
        let mut headers = Vec::new();
        let mut content_length = 0usize;
        loop {
            let mut line = String::new();
            reader.read_line(&mut line).unwrap();
            if line == "\r\n" || line.is_empty() {
                break;
            }
            let lower = line.to_ascii_lowercase();
            if let Some(v) = lower.strip_prefix("content-length:") {
                content_length = v.trim().parse().unwrap_or(0);
            }
            headers.push(line.trim().to_string());
        }
        let mut body = vec![0u8; content_length];
        if content_length > 0 {
            reader.read_exact(&mut body).unwrap();
        }
        (status, headers, String::from_utf8_lossy(&body).to_string())
    }
    /// 现代 POST:三头(版本 / Mcp-Method / 可选 Mcp-Name)
    fn mpost(
        port: u16,
        token: &str,
        method: &str,
        name: Option<&str>,
        version: &str,
        body: &str,
    ) -> (u16, String) {
        let name_h = name
            .map(|n| format!("Mcp-Name: {}\r\n", n))
            .unwrap_or_default();
        let headers = format!("Authorization: Bearer {}\r\nAccept: application/json, text/event-stream\r\nMCP-Protocol-Version: {}\r\nMcp-Method: {}\r\n{}", token, version, method, name_h);
        post(port, &headers, body)
    }
    fn modern_server() -> (Arc<McpCore>, McpServerHandle, u16, String) {
        let c = Arc::new(modern_core());
        let token = c.token();
        let page: Arc<dyn PageDispatcher> = Arc::new(FakePage {
            tools: fake_tools(),
            fail_with: None,
        });
        let handle = start_server(0, Arc::clone(&c), page, "9.9.9".into()).unwrap();
        let port = handle.port();
        (c, handle, port, token)
    }

    #[test]
    fn modern_discover_returns_versions_capabilities_and_cache_hints() {
        let (c, handle, port, token) = modern_server();
        let (st, headers, body) = http_full(port, &format!("POST /mcp HTTP/1.1\r\nHost: 127.0.0.1:{p}\r\nContent-Type: application/json\r\nAuthorization: Bearer {t}\r\nMCP-Protocol-Version: 2026-07-28\r\nMcp-Method: server/discover\r\nContent-Length: {n}\r\n\r\n{b}", p = port, t = token, n = mreq(1, "server/discover", json!({})).to_string().len(), b = mreq(1, "server/discover", json!({}))));
        assert_eq!(st, 200, "{}", body);
        let v: Value = serde_json::from_str(&body).unwrap();
        let r = &v["result"];
        assert_eq!(r["resultType"], "complete");
        assert_eq!(r["supportedVersions"], json!(["2026-07-28"]));
        assert_eq!(r["capabilities"]["tools"]["listChanged"], true);
        assert_eq!(r["capabilities"]["resources"]["subscribe"], false);
        assert_eq!(r["capabilities"]["extensions"], json!({}));
        assert_eq!(r["_meta"][META_SERVER_INFO]["name"], "horosa");
        assert_eq!(r["ttlMs"], 3_600_000);
        assert_eq!(r["cacheScope"], "public");
        assert!(
            !headers
                .iter()
                .any(|h| h.to_ascii_lowercase().starts_with("mcp-session-id:")),
            "现代纪元不发会话头"
        );
        assert_eq!(c.session_count(), 0);
        handle.signal_stop();
    }

    #[test]
    fn modern_tools_list_wraps_result_type_ttl_scope_server_info_sorted() {
        let (_c, handle, port, token) = modern_server();
        let body = mreq(2, "tools/list", json!({})).to_string();
        let (st, out) = mpost(port, &token, "tools/list", None, "2026-07-28", &body);
        assert_eq!(st, 200, "{}", out);
        let v: Value = serde_json::from_str(&out).unwrap();
        let names: Vec<&str> = v["result"]["tools"]
            .as_array()
            .unwrap()
            .iter()
            .map(|t| t["name"].as_str().unwrap())
            .collect();
        assert_eq!(
            names,
            vec!["create_chart_record", "list_records"],
            "现代 tools/list 按 name 稳定排序"
        );
        assert_eq!(v["result"]["resultType"], "complete");
        assert_eq!(v["result"]["ttlMs"], 30_000);
        assert_eq!(v["result"]["cacheScope"], "private");
        assert_eq!(v["result"]["_meta"][META_SERVER_INFO]["version"], "9.9.9");
        // 旧纪元 tools/list:注册序、无新键(字节同今日)
        let (st2, legacy) = post(
            port,
            &format!("Authorization: Bearer {}\r\n", token),
            "{\"jsonrpc\":\"2.0\",\"id\":3,\"method\":\"tools/list\"}",
        );
        assert_eq!(st2, 200);
        let l: Value = serde_json::from_str(&legacy).unwrap();
        let ln: Vec<&str> = l["result"]["tools"]
            .as_array()
            .unwrap()
            .iter()
            .map(|t| t["name"].as_str().unwrap())
            .collect();
        assert_eq!(ln, vec!["list_records", "create_chart_record"]);
        assert!(l["result"].get("resultType").is_none() && l["result"].get("ttlMs").is_none());
        handle.signal_stop();
    }

    #[test]
    fn modern_tools_call_dispatches_with_modern_identity() {
        let (_c, handle, port, token) = modern_server();
        let body = mreq(
            4,
            "tools/call",
            json!({ "name": "list_records", "arguments": { "kind": "chart" } }),
        )
        .to_string();
        let (st, out) = mpost(
            port,
            &token,
            "tools/call",
            Some("list_records"),
            "2026-07-28",
            &body,
        );
        assert_eq!(st, 200, "{}", out);
        let v: Value = serde_json::from_str(&out).unwrap();
        assert_eq!(v["result"]["resultType"], "complete");
        assert!(v["result"]["content"].is_array());
        assert_eq!(v["result"]["_meta"][META_SERVER_INFO]["name"], "horosa");
        assert!(
            v["result"].get("ttlMs").is_none(),
            "tools/call 不是列表类,不带 ttlMs"
        );
        // 核级:现代身份 = sessionId "modern" + clientName 取自 clientInfo(假页面把 params 原样回显进 structuredContent.echo? 这里用核直接看 dispatch 参数)
        let c2 = modern_core();
        struct Echo;
        impl PageDispatcher for Echo {
            fn dispatch(
                &self,
                _m: &str,
                params: Value,
                _t: Duration,
            ) -> std::result::Result<Value, McpError> {
                Ok(
                    json!({ "content": [{ "type": "text", "text": params.to_string() }], "isError": false }),
                )
            }
        }
        let out = c2.handle_modern(
            &mreq(
                5,
                "tools/call",
                json!({ "name": "list_records", "arguments": {} }),
            ),
            None,
            &Echo,
        );
        match out {
            ModernOutcome::Json { status, body } => {
                assert_eq!(status, 200);
                let text = body["result"]["content"][0]["text"]
                    .as_str()
                    .unwrap()
                    .to_string();
                assert!(text.contains("\"sessionId\":\"modern\""), "{}", text);
                assert!(text.contains("\"clientName\":\"claude-code\""), "{}", text);
            }
            _ => panic!("expected json"),
        }
        handle.signal_stop();
    }

    #[test]
    fn modern_header_mismatch_returns_400_minus_32020() {
        let (_c, handle, port, token) = modern_server();
        let body = mreq(
            6,
            "tools/call",
            json!({ "name": "list_records", "arguments": {} }),
        )
        .to_string();
        let (st, out) = mpost(
            port,
            &token,
            "tools/call",
            Some("wrong"),
            "2026-07-28",
            &body,
        );
        assert_eq!(st, 400);
        let v: Value = serde_json::from_str(&out).unwrap();
        assert_eq!(v["error"]["code"], ERR_HEADER_MISMATCH);
        assert!(v["error"]["message"].as_str().unwrap().contains("Mcp-Name"));
        assert!(!out.contains(&token), "文案永不回显令牌");
        // Mcp-Method 缺
        let (st2, out2) = post(
            port,
            &format!(
                "Authorization: Bearer {}\r\nMCP-Protocol-Version: 2026-07-28\r\n",
                token
            ),
            &mreq(7, "tools/list", json!({})).to_string(),
        );
        assert_eq!(st2, 400);
        assert_eq!(
            serde_json::from_str::<Value>(&out2).unwrap()["error"]["code"],
            ERR_HEADER_MISMATCH
        );
        // 头 2026-07-28 但 _meta 写 2025-06-18 ⇒ -32022(体里的版本不被支持:现代请求只认现代版本)
        let mut r = mreq(8, "tools/list", json!({}));
        r["params"]["_meta"][META_PROTOCOL_VERSION] = json!("2025-06-18");
        let (st3, out3) = mpost(
            port,
            &token,
            "tools/list",
            None,
            "2026-07-28",
            &r.to_string(),
        );
        assert_eq!(st3, 400);
        assert_eq!(
            serde_json::from_str::<Value>(&out3).unwrap()["error"]["code"],
            ERR_UNSUPPORTED_VERSION
        );
        // 版本头缺但 _meta 现代 ⇒ -32020
        let (st4, out4) = post(
            port,
            &format!(
                "Authorization: Bearer {}\r\nMcp-Method: tools/list\r\n",
                token
            ),
            &mreq(9, "tools/list", json!({})).to_string(),
        );
        assert_eq!(st4, 400);
        assert_eq!(
            serde_json::from_str::<Value>(&out4).unwrap()["error"]["code"],
            ERR_HEADER_MISMATCH
        );
        handle.signal_stop();
    }

    #[test]
    fn modern_unsupported_version_returns_400_minus_32022_with_supported_list() {
        let (_c, handle, port, token) = modern_server();
        let mut r = mreq(10, "tools/list", json!({}));
        r["params"]["_meta"][META_PROTOCOL_VERSION] = json!("2099-01-01");
        let (st, out) = mpost(
            port,
            &token,
            "tools/list",
            None,
            "2099-01-01",
            &r.to_string(),
        );
        assert_eq!(st, 400);
        let v: Value = serde_json::from_str(&out).unwrap();
        assert_eq!(v["error"]["code"], ERR_UNSUPPORTED_VERSION);
        assert_eq!(v["error"]["data"]["supported"], json!(["2026-07-28"]));
        assert_eq!(v["error"]["data"]["requested"], "2099-01-01");
        handle.signal_stop();
    }

    #[test]
    fn modern_mcp_name_base64_sentinel_decoded_before_compare() {
        let (_c, handle, port, token) = modern_server();
        let body = mreq(
            11,
            "tools/call",
            json!({ "name": "list_records", "arguments": {} }),
        )
        .to_string();
        let enc = encode_header_value("list_records");
        assert_eq!(enc, "list_records");
        let (st, out) = mpost(
            port,
            &token,
            "tools/call",
            Some("=?base64?bGlzdF9yZWNvcmRz?="),
            "2026-07-28",
            &body,
        );
        assert_eq!(st, 200, "{}", out);
        // resources/read:Mcp-Name = params.uri
        let uri = "horosa://chart/local-1";
        let rb = mreq(12, "resources/read", json!({ "uri": uri })).to_string();
        let (st2, out2) = mpost(
            port,
            &token,
            "resources/read",
            Some(&encode_header_value(uri)),
            "2026-07-28",
            &rb,
        );
        assert_eq!(st2, 200, "{}", out2);
        let v2: Value = serde_json::from_str(&out2).unwrap();
        assert!(v2["result"]["contents"].is_array());
        assert_eq!(v2["result"]["ttlMs"], 0);
        assert_eq!(v2["result"]["cacheScope"], "private");
        // 拿 params.name 当 Mcp-Name(resources/read 该用 uri)⇒ -32020
        let (st3, out3) = mpost(
            port,
            &token,
            "resources/read",
            Some("local-1"),
            "2026-07-28",
            &rb,
        );
        assert_eq!(st3, 400);
        assert_eq!(
            serde_json::from_str::<Value>(&out3).unwrap()["error"]["code"],
            ERR_HEADER_MISMATCH
        );
        // 非 ASCII 名字往返
        let cjk = "查詢";
        let e = encode_header_value(cjk);
        assert!(e.starts_with("=?base64?") && e.ends_with("?="));
        assert_eq!(decode_header_value(&e).unwrap(), cjk);
        handle.signal_stop();
    }

    #[test]
    fn header_value_sentinel_codec_vectors() {
        assert_eq!(encode_header_value("us-west1"), "us-west1");
        assert_eq!(
            encode_header_value("Hello, 世界"),
            "=?base64?SGVsbG8sIOS4lueVjA==?="
        );
        assert_eq!(encode_header_value(" padded "), "=?base64?IHBhZGRlZCA=?=");
        assert_eq!(
            encode_header_value("line1\nline2"),
            "=?base64?bGluZTEKbGluZTI=?="
        );
        assert_eq!(
            encode_header_value("=?base64?literal?="),
            "=?base64?PT9iYXNlNjQ/bGl0ZXJhbD89?="
        );
        for v in [
            "us-west1",
            "Hello, 世界",
            " padded ",
            "line1\nline2",
            "=?base64?literal?=",
            "查詢",
        ] {
            assert_eq!(decode_header_value(&encode_header_value(v)).unwrap(), v);
        }
        assert!(decode_header_value("bad\u{1}").is_err());
        assert_eq!(
            decode_header_value("=?base64?bGlzdF9yZWNvcmRz?=").unwrap(),
            "list_records"
        );
        assert_eq!(
            decode_header_value("=?base64?bGlzdF9yZWNvcmRz").unwrap(),
            "=?base64?bGlzdF9yZWNvcmRz",
            "缺后缀不算哨兵 ⇒ 按明文"
        );
        assert!(decode_header_value("=?base64?***?=").is_err());
    }

    #[test]
    fn modern_unknown_and_legacy_only_methods_return_404_minus_32601() {
        let (_c, handle, port, token) = modern_server();
        for m in ["nope/x", "ping", "logging/setLevel", "initialize"] {
            let mut p = json!({});
            if m == "logging/setLevel" {
                p = json!({ "level": "debug" });
            }
            if m == "initialize" {
                p = json!({ "protocolVersion": "2026-07-28" });
            }
            let body = mreq(13, m, p).to_string();
            let (st, out) = mpost(port, &token, m, None, "2026-07-28", &body);
            assert_eq!(st, 404, "{} → {}", m, out);
            assert_eq!(
                serde_json::from_str::<Value>(&out).unwrap()["error"]["code"],
                ERR_METHOD_NOT_FOUND,
                "{}",
                m
            );
        }
        // 旧纪元 ping 仍 200
        let (st, out) = post(
            port,
            &format!("Authorization: Bearer {}\r\n", token),
            "{\"jsonrpc\":\"2.0\",\"id\":14,\"method\":\"ping\"}",
        );
        assert_eq!(st, 200);
        assert_eq!(
            serde_json::from_str::<Value>(&out).unwrap()["result"],
            json!({})
        );
        handle.signal_stop();
    }

    #[test]
    fn modern_missing_meta_version_and_bad_log_level_are_minus_32602() {
        let (_c, handle, port, token) = modern_server();
        // 头 2026-07-28 + 无 _meta ⇒ -32602(400)
        let (st, out) = mpost(
            port,
            &token,
            "tools/list",
            None,
            "2026-07-28",
            "{\"jsonrpc\":\"2.0\",\"id\":15,\"method\":\"tools/list\",\"params\":{}}",
        );
        assert_eq!(st, 400, "{}", out);
        assert_eq!(
            serde_json::from_str::<Value>(&out).unwrap()["error"]["code"],
            ERR_INVALID_PARAMS
        );
        let mut r = mreq(16, "tools/list", json!({}));
        r["params"]["_meta"][META_LOG_LEVEL] = json!("loud");
        let (st2, out2) = mpost(
            port,
            &token,
            "tools/list",
            None,
            "2026-07-28",
            &r.to_string(),
        );
        assert_eq!(st2, 400);
        assert_eq!(
            serde_json::from_str::<Value>(&out2).unwrap()["error"]["code"],
            ERR_INVALID_PARAMS
        );
        // clientCapabilities 缺席宽容 ⇒ 200
        let mut r2 = mreq(17, "tools/list", json!({}));
        r2["params"]["_meta"]
            .as_object_mut()
            .unwrap()
            .remove(META_CLIENT_CAPS);
        let (st3, _) = mpost(
            port,
            &token,
            "tools/list",
            None,
            "2026-07-28",
            &r2.to_string(),
        );
        assert_eq!(st3, 200);
        handle.signal_stop();
    }

    #[test]
    fn modern_ignores_session_header_and_never_mints_one() {
        let (c, handle, port, token) = modern_server();
        let body = mreq(18, "tools/list", json!({})).to_string();
        let (st, headers, out) = http_full(port, &format!("POST /mcp HTTP/1.1\r\nHost: 127.0.0.1:{p}\r\nContent-Type: application/json\r\nAuthorization: Bearer {t}\r\nMCP-Protocol-Version: 2026-07-28\r\nMcp-Method: tools/list\r\nMcp-Session-Id: bogus\r\nContent-Length: {n}\r\n\r\n{b}", p = port, t = token, n = body.len(), b = body));
        assert_eq!(st, 200, "{}", out);
        assert!(!headers
            .iter()
            .any(|h| h.to_ascii_lowercase().starts_with("mcp-session-id:")));
        assert_eq!(c.session_count(), 0);
        // 旧纪元带 bogus 会话头 ⇒ 404(今日)
        let (st2, _) = post(
            port,
            &format!(
                "Authorization: Bearer {}\r\nMcp-Session-Id: bogus\r\n",
                token
            ),
            "{\"jsonrpc\":\"2.0\",\"id\":19,\"method\":\"ping\"}",
        );
        assert_eq!(st2, 404);
        handle.signal_stop();
    }

    /// 锁死今日与今后的互通路径:TS SDK v2(Claude Code ≥ 2.1.232)对旧纪元服务的探测 → 400 非 JSON → 回退 initialize 2025-11-25 → 协商到 2025-06-18 → 带旧版本头继续
    #[test]
    fn claude_code_v2_fallback_sequence_against_legacy_only_server() {
        let c = Arc::new(core());
        c.set_modern_enabled(false);
        let token = c.token();
        let page: Arc<dyn PageDispatcher> = Arc::new(FakePage {
            tools: fake_tools(),
            fail_with: None,
        });
        let handle = start_server(0, Arc::clone(&c), page, "9.9.9".into()).unwrap();
        let port = handle.port();
        let probe = mreq(1, "server/discover", json!({})).to_string();
        let (st, body) = mpost(port, &token, "server/discover", None, "2026-07-28", &probe);
        assert_eq!(st, 400);
        assert!(
            serde_json::from_str::<Value>(&body).is_err(),
            "旧纪元服务对现代探测回非 JSON 纯文本 ⇒ 客户端据此回退:{}",
            body
        );
        let init = "{\"jsonrpc\":\"2.0\",\"id\":2,\"method\":\"initialize\",\"params\":{\"protocolVersion\":\"2025-11-25\",\"capabilities\":{},\"clientInfo\":{\"name\":\"claude-code\",\"version\":\"2.1.240\"}}}";
        let (st2, headers, out2) = http_full(port, &format!("POST /mcp HTTP/1.1\r\nHost: 127.0.0.1:{p}\r\nContent-Type: application/json\r\nAuthorization: Bearer {t}\r\nContent-Length: {n}\r\n\r\n{b}", p = port, t = token, n = init.len(), b = init));
        assert_eq!(st2, 200, "{}", out2);
        let v: Value = serde_json::from_str(&out2).unwrap();
        assert_eq!(
            v["result"]["protocolVersion"], "2025-06-18",
            "2025-11-25 不在支持表 ⇒ 协商到最新旧版"
        );
        let sid = headers
            .iter()
            .find(|h| h.to_ascii_lowercase().starts_with("mcp-session-id:"))
            .map(|h| h.splitn(2, ':').nth(1).unwrap().trim().to_string())
            .expect("旧纪元 initialize 发会话头");
        let (st3, _) = post(
            port,
            &format!(
                "Authorization: Bearer {}\r\nMcp-Session-Id: {}\r\n",
                token, sid
            ),
            "{\"jsonrpc\":\"2.0\",\"method\":\"notifications/initialized\"}",
        );
        assert_eq!(st3, 202);
        let (st4, out4) = post(port, &format!("Authorization: Bearer {}\r\nMCP-Protocol-Version: 2025-06-18\r\nMcp-Session-Id: {}\r\n", token, sid), "{\"jsonrpc\":\"2.0\",\"id\":3,\"method\":\"tools/list\"}");
        assert_eq!(st4, 200);
        let l: Value = serde_json::from_str(&out4).unwrap();
        assert_eq!(l["result"]["tools"].as_array().unwrap().len(), 2);
        assert!(l["result"].get("resultType").is_none());
        handle.signal_stop();
    }

    #[test]
    fn dual_era_probe_goes_modern_when_enabled_and_legacy_still_served() {
        let (c, handle, port, token) = modern_server();
        let (st, body) = mpost(
            port,
            &token,
            "server/discover",
            None,
            "2026-07-28",
            &mreq(1, "server/discover", json!({})).to_string(),
        );
        assert_eq!(st, 200);
        assert_eq!(
            serde_json::from_str::<Value>(&body).unwrap()["result"]["supportedVersions"][0],
            "2026-07-28"
        );
        let (st2, _) = mpost(
            port,
            &token,
            "tools/list",
            None,
            "2026-07-28",
            &mreq(2, "tools/list", json!({})).to_string(),
        );
        assert_eq!(st2, 200);
        // 同一服务同时服务旧纪元 initialize(会话)
        let init = "{\"jsonrpc\":\"2.0\",\"id\":3,\"method\":\"initialize\",\"params\":{\"protocolVersion\":\"2025-06-18\"}}";
        let (st3, headers, out3) = http_full(port, &format!("POST /mcp HTTP/1.1\r\nHost: 127.0.0.1:{p}\r\nContent-Type: application/json\r\nAuthorization: Bearer {t}\r\nContent-Length: {n}\r\n\r\n{b}", p = port, t = token, n = init.len(), b = init));
        assert_eq!(st3, 200, "{}", out3);
        assert!(headers
            .iter()
            .any(|h| h.to_ascii_lowercase().starts_with("mcp-session-id:")));
        assert_eq!(c.session_count(), 1);
        handle.signal_stop();
    }

    fn read_sse_until(reader: &mut BufReader<TcpStream>, needle: &str, max_lines: usize) -> String {
        let mut got = String::new();
        for _ in 0..max_lines {
            let mut line = String::new();
            if reader.read_line(&mut line).is_err() {
                break;
            }
            got.push_str(&line);
            if got.contains(needle) {
                break;
            }
        }
        got
    }

    #[test]
    fn subscriptions_listen_acks_then_delivers_tagged_tools_list_changed_and_legacy_get_concurrently(
    ) {
        let (c, handle, port, token) = modern_server();
        // 旧 GET 流
        let mut legacy = TcpStream::connect(("127.0.0.1", port)).unwrap();
        legacy.write_all(format!("GET /mcp HTTP/1.1\r\nHost: 127.0.0.1:{}\r\nAuthorization: Bearer {}\r\nAccept: text/event-stream\r\n\r\n", port, token).as_bytes()).unwrap();
        legacy.flush().unwrap();
        legacy
            .set_read_timeout(Some(Duration::from_secs(5)))
            .unwrap();
        let mut lr = BufReader::new(legacy);
        let mut sl = String::new();
        lr.read_line(&mut sl).unwrap();
        assert!(sl.contains(" 200 "));
        loop {
            let mut line = String::new();
            lr.read_line(&mut line).unwrap();
            if line == "\r\n" {
                break;
            }
        }
        // 现代长流
        let body = mreq(7, "subscriptions/listen", json!({ "notifications": { "toolsListChanged": true, "resourcesListChanged": true, "resourceSubscriptions": ["horosa://x"] } })).to_string();
        let mut modern = TcpStream::connect(("127.0.0.1", port)).unwrap();
        modern.write_all(format!("POST /mcp HTTP/1.1\r\nHost: 127.0.0.1:{p}\r\nContent-Type: application/json\r\nAccept: application/json, text/event-stream\r\nAuthorization: Bearer {t}\r\nMCP-Protocol-Version: 2026-07-28\r\nMcp-Method: subscriptions/listen\r\nContent-Length: {n}\r\n\r\n{b}", p = port, t = token, n = body.len(), b = body).as_bytes()).unwrap();
        modern.flush().unwrap();
        modern
            .set_read_timeout(Some(Duration::from_secs(5)))
            .unwrap();
        let mut mr = BufReader::new(modern);
        let mut ms = String::new();
        mr.read_line(&mut ms).unwrap();
        assert!(ms.contains(" 200 "), "{}", ms);
        let mut ctype = false;
        let mut accel = false;
        loop {
            let mut line = String::new();
            mr.read_line(&mut line).unwrap();
            let low = line.to_ascii_lowercase();
            if low.starts_with("content-type:") && low.contains("text/event-stream") {
                ctype = true;
            }
            if low.starts_with("x-accel-buffering:") && low.contains("no") {
                accel = true;
            }
            if line == "\r\n" {
                break;
            }
        }
        assert!(ctype && accel);
        let ack = read_sse_until(&mut mr, "acknowledged", 8);
        let ack_json: Value = serde_json::from_str(
            ack.lines()
                .find(|l| l.starts_with("data:"))
                .unwrap()
                .trim_start_matches("data:")
                .trim(),
        )
        .unwrap();
        assert_eq!(
            ack_json["method"],
            "notifications/subscriptions/acknowledged"
        );
        assert_eq!(ack_json["params"]["_meta"][META_SUBSCRIPTION_ID], 7);
        assert_eq!(
            ack_json["params"]["notifications"],
            json!({ "toolsListChanged": true, "resourcesListChanged": true })
        );
        assert_eq!(c.listen_count(), 1);
        assert_eq!(c.sse_count(), 2);
        // 广播:两边都到;现代帧带 subscriptionId,旧帧无 _meta
        assert_eq!(c.notify("notifications/tools/list_changed", json!({})), 2);
        let mf = read_sse_until(&mut mr, "list_changed", 8);
        let mj: Value = serde_json::from_str(
            mf.lines()
                .find(|l| l.starts_with("data:") && l.contains("list_changed"))
                .unwrap()
                .trim_start_matches("data:")
                .trim(),
        )
        .unwrap();
        assert_eq!(mj["params"]["_meta"][META_SUBSCRIPTION_ID], 7);
        let lf = read_sse_until(&mut lr, "list_changed", 8);
        assert!(lf.contains("event: message\ndata: {\"jsonrpc\":\"2.0\",\"method\":\"notifications/tools/list_changed\",\"params\":{}}"), "旧帧字节同今日:{:?}", lf);
        // 过滤:prompts 只到旧流
        assert_eq!(c.notify("notifications/prompts/list_changed", json!({})), 1);
        // 两条流开着时 POST 仍可服务
        let (st, _) = post(
            port,
            &format!("Authorization: Bearer {}\r\n", token),
            "{\"jsonrpc\":\"2.0\",\"id\":9,\"method\":\"ping\"}",
        );
        assert_eq!(st, 200);
        handle.signal_stop();
        // 停机 ⇒ 现代流收尾帧带 subscriptionId
        let tail = read_sse_until(&mut mr, "\"resultType\":\"complete\"", 12);
        assert!(
            tail.contains(&format!("\"{}\":7", META_SUBSCRIPTION_ID)),
            "{:?}",
            tail
        );
        drop(mr);
        drop(lr);
    }

    #[test]
    fn listen_streams_capped_separately_from_legacy_get() {
        let c = modern_core();
        let mut keep = Vec::new();
        for _ in 0..MAX_SSE_CLIENTS {
            keep.push(c.sse_subscribe().expect("legacy slot"));
        }
        assert!(c.sse_subscribe().is_none());
        for i in 0..MAX_LISTEN_STREAMS {
            keep.push(
                c.listen_subscribe(
                    json!(i),
                    ListenFilter {
                        tools: true,
                        prompts: false,
                        resources: false,
                    },
                )
                .expect("listen slot"),
            );
        }
        assert!(c
            .listen_subscribe(json!(99), ListenFilter::default())
            .is_none());
        assert_eq!(c.listen_count(), MAX_LISTEN_STREAMS);
        assert_eq!(c.sse_count(), MAX_SSE_CLIENTS + MAX_LISTEN_STREAMS);
        // 第五条 listen 经 HTTP ⇒ 429 JSON(-32004)
        let (c2, handle, port, token) = modern_server();
        let mut hold = Vec::new();
        for i in 0..MAX_LISTEN_STREAMS {
            hold.push(
                c2.listen_subscribe(json!(i), ListenFilter::default())
                    .unwrap(),
            );
        }
        let body = mreq(
            5,
            "subscriptions/listen",
            json!({ "notifications": { "toolsListChanged": true } }),
        )
        .to_string();
        let (st, out) = mpost(
            port,
            &token,
            "subscriptions/listen",
            None,
            "2026-07-28",
            &body,
        );
        assert_eq!(st, 429, "{}", out);
        assert_eq!(
            serde_json::from_str::<Value>(&out).unwrap()["error"]["code"],
            ERR_RATE_LIMITED
        );
        handle.signal_stop();
        drop(hold);
        drop(keep);
    }

    #[test]
    fn detect_era_and_version_header_vectors() {
        assert_eq!(classify_version_header(None), VersionHeader::Absent);
        assert_eq!(
            classify_version_header(Some("2025-06-18")),
            VersionHeader::Legacy
        );
        assert_eq!(
            classify_version_header(Some(" 2026-07-28 ")),
            VersionHeader::Modern
        );
        assert_eq!(
            classify_version_header(Some("2099-01-01")),
            VersionHeader::Unknown
        );
        let legacy_init = json!({ "jsonrpc": "2.0", "id": 1, "method": "initialize", "params": { "protocolVersion": "2025-11-25" } });
        assert_eq!(
            detect_era(VersionHeader::Absent, &legacy_init, true),
            Era::Legacy
        );
        assert_eq!(
            detect_era(VersionHeader::Modern, &legacy_init, true),
            Era::Legacy,
            "initialize 永远是旧纪元"
        );
        assert_eq!(
            detect_era(
                VersionHeader::Modern,
                &json!({ "jsonrpc": "2.0", "id": 1, "method": "tools/list" }),
                true
            ),
            Era::Modern
        );
        assert_eq!(
            detect_era(
                VersionHeader::Absent,
                &mreq(1, "tools/list", json!({})),
                true
            ),
            Era::Modern,
            "无头但带现代 _meta ⇒ 现代(校验时再判 -32020)"
        );
        assert_eq!(
            detect_era(
                VersionHeader::Modern,
                &mreq(1, "tools/list", json!({})),
                false
            ),
            Era::Legacy,
            "开关关 ⇒ 一切旧纪元"
        );
        assert_eq!(modern_http_status(ERR_HEADER_MISMATCH), 400);
        assert_eq!(modern_http_status(ERR_METHOD_NOT_FOUND), 404);
        assert_eq!(modern_http_status(ERR_RATE_LIMITED), 200);
    }
}

#[cfg(test)]
mod token_exposure_tests {
    use super::*;

    // 令牌暴露面收敛:状态查询不再携带令牌(status_json 的 "token" 恒空串),按需取走 reveal_token;
    // 未运行时 reveal_token 必为 None。
    #[test]
    fn reveal_token_is_none_when_server_not_running() {
        let state = McpState::default();
        assert!(reveal_token(&state).is_none());
    }

    #[test]
    fn status_json_source_never_emits_token_value() {
        let src = include_str!("mcp_server.rs");
        let start = src
            .find("pub fn status_json(")
            .expect("status_json present");
        // [D74] 函数头多了一行「生效中的每分钟上限」计算,窗口从 1200 放到 1800(仍只覆盖 status_json 本体)
        let mut end = (start + 1800).min(src.len());
        while !src.is_char_boundary(end) {
            end -= 1;
        }
        let body = &src[start..end];
        assert!(
            body.contains("\"token\": String::new()"),
            "status_json 必须恒回空令牌"
        );
        assert!(
            !body.contains("\"token\": if running { token }"),
            "旧写法(运行中直接回令牌)不得回潮"
        );
    }
}
