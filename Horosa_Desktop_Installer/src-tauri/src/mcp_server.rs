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
/// 握手纪元可协商的版本(2025-11-25 起:工具 icons / 输入校验错误走工具执行错误 / Origin 非法回 403 —— 本服务早已满足,补认版本即可)
pub const MCP_PROTOCOL_VERSIONS: [&str; 4] =
    ["2024-11-05", "2025-03-26", "2025-06-18", "2025-11-25"];
pub const MCP_LATEST_PROTOCOL: &str = "2025-11-25";
/// [2026-07-28 双纪元] 现代修订:无状态(无 initialize 握手、无会话头)、每请求 `params._meta` 携带协议版本/身份/能力、`server/discover`、
/// `subscriptions/listen` 长流取代 GET 流;旧握手纪元(上面三版)照旧服务——请求带现代 `_meta` 或现代版本头 ⇒ 现代纪元,`initialize` ⇒ 旧纪元。
pub const MCP_MODERN_VERSIONS: [&str; 1] = ["2026-07-28"];
/// 现代纪元的方法集(ping / logging/setLevel / initialize 在该修订里已移除 ⇒ 404 + -32601;completion/complete 两纪元都在)
pub const MODERN_METHODS: [&str; 10] = [
    "server/discover",
    "tools/list",
    "tools/call",
    "resources/list",
    "resources/templates/list",
    "resources/read",
    "prompts/list",
    "prompts/get",
    "completion/complete",
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
pub(crate) const MAX_BODY_BYTES: usize = 1 << 20;
const TOOLS_CACHE_TTL: Duration = Duration::from_secs(30);
const DEFAULT_TOOL_TIMEOUT: Duration = Duration::from_secs(120);
const MAX_TOOL_TIMEOUT: Duration = Duration::from_secs(600);
const RATE_PER_MINUTE: f64 = 60.0;
const RATE_BURST: f64 = 10.0;
/// 令牌桶速率可配(页面「外部客户端策略·每分钟调用上限」1..600 同步到壳;此前壳写死 60/分钟,页面设 >60 全部无效);600 = 洪泛硬顶
const RATE_MAX_PER_MINUTE: f64 = 600.0;
/// 页面桥改「只读小并发 + 写入串行」后,壳侧在途上限 4→6、收发线程 2→8:
/// 线程数必须大于在途上限,在途占满时仍有空闲线程收取消通知 / initialize / tools/list(缓存命中)
const MAX_INFLIGHT: usize = 6;
const WORKERS: usize = 8;
/// 请求自带响应流(POST 回 text/event-stream)期间的保活间隔:现代纪元靠它探测客户端断开 = 取消
pub(crate) const SSE_RESPONSE_KEEPALIVE: Duration =
    Duration::from_millis(if cfg!(test) { 200 } else { 2000 });
/// 单次调用最多转发的进度帧(页面已节流;这里是坏页面 / 洪泛的硬顶)
const PROGRESS_FRAMES_MAX: usize = 1000;
/// 取消通知先于请求到达(两条连接赛跑)时留的墓碑时效:时效内到达的同键请求一进门即判已取消
const CANCEL_TOMBSTONE_TTL: Duration = Duration::from_secs(5);
const CANCEL_TOMBSTONE_MAX: usize = 64;
// v2:SSE 通知通道(GET /mcp)与可选会话
const MAX_SSE_CLIENTS: usize = 4;
const SSE_KEEPALIVE: Duration = Duration::from_secs(15);
const SSE_QUEUE: usize = 32;
const MAX_SESSIONS: usize = 64;
/// 会话时效:发出超过这么久的 Mcp-Session-Id 既拒绝放行也从表里剔除(此前只有「表满 64 条挤最旧」,拿到过一次会话头就能永久复用)。
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
/// 已被客户端取消的请求(沿用 LSP RequestCancelled 码;客户端按规范应忽略取消后的回包,这里只为让收发线程有个了结)
pub const ERR_CANCELLED: i64 = -32800;

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

/// 单次页面派发的控制面(全部在发起请求的收发线程上用,不跨线程):
/// - `cancelled`:旧纪元 notifications/cancelled / 现代纪元响应流断开 / 墓碑 置位 → 派发循环停等、通知页面中止、回 -32800;
/// - `on_progress`:页面回传的进度(`{progress,total?,message?}`)→ 写进本请求自己的响应流;回 false = 写不进去(客户端已断开);
/// - `on_tick`:等待期每 ~250 ms 调一次(响应流保活 / 断流探测);回 false = 客户端已断开;
/// - `cancel_on_disconnect`:断开是否算取消(现代纪元按规范算;旧纪元规范写明断开不算取消)。
pub struct CallControl<'a> {
    pub cancelled: Arc<AtomicBool>,
    pub on_progress: Option<&'a dyn Fn(&Value) -> bool>,
    pub on_tick: Option<&'a dyn Fn() -> bool>,
    pub cancel_on_disconnect: bool,
}

impl<'a> CallControl<'a> {
    /// 无取消源、无进度、无保活(今日行为;核级调用与测试用)
    pub fn none() -> CallControl<'static> {
        CallControl {
            cancelled: Arc::new(AtomicBool::new(false)),
            on_progress: None,
            on_tick: None,
            cancel_on_disconnect: false,
        }
    }
    pub fn is_cancelled(&self) -> bool {
        self.cancelled.load(Ordering::SeqCst)
    }
    pub fn wants_progress(&self) -> bool {
        self.on_progress.is_some()
    }
    /// 等待期心跳:保活写失败且断开算取消 ⇒ 置取消位
    fn tick(&self) {
        if let Some(t) = self.on_tick {
            if !t() && self.cancel_on_disconnect {
                self.cancelled.store(true, Ordering::SeqCst);
            }
        }
    }
    fn progress(&self, v: &Value) {
        if let Some(f) = self.on_progress {
            if !f(v) && self.cancel_on_disconnect {
                self.cancelled.store(true, Ordering::SeqCst);
            }
        }
    }
}

pub fn cancelled_error() -> McpError {
    McpError::new(ERR_CANCELLED, "request cancelled by client")
}

/// 页面投递抽象:应用内 = eval 到 WebView;测试 = 假页面。
pub trait PageDispatcher: Send + Sync {
    fn dispatch(
        &self,
        method: &str,
        params: Value,
        timeout: Duration,
    ) -> std::result::Result<Value, McpError>;
    /// 带控制面的派发;缺省实现 = 先看取消位再走 `dispatch`(假页面 / 旧实现零改动即兼容)
    fn dispatch_ctl(
        &self,
        method: &str,
        params: Value,
        timeout: Duration,
        ctl: &CallControl,
    ) -> std::result::Result<Value, McpError> {
        if ctl.is_cancelled() {
            return Err(cancelled_error());
        }
        self.dispatch(method, params, timeout)
    }
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

/// 请求自带的进度令牌(`params._meta.progressToken`,规范只认字符串或整数)
pub fn progress_token_of(req: &Value) -> Option<Value> {
    let t = req.get("params")?.get("_meta")?.get("progressToken")?;
    if t.is_string() || t.is_i64() || t.is_u64() {
        Some(t.clone())
    } else {
        None
    }
}

/// 页面回传的进度 → 规范帧;强制单调递增(不增即丢)。回 None = 本帧不发。
pub fn progress_frame(token: &Value, v: &Value, last: &mut Option<f64>) -> Option<Value> {
    let p = v.get("progress").and_then(|x| x.as_f64())?;
    if !p.is_finite() {
        return None;
    }
    if let Some(prev) = *last {
        if p <= prev {
            return None;
        }
    }
    *last = Some(p);
    let mut params = json!({ "progressToken": token.clone(), "progress": p });
    if let Some(t) = v
        .get("total")
        .and_then(|x| x.as_f64())
        .filter(|t| t.is_finite())
    {
        params["total"] = json!(t);
    }
    if let Some(m) = v.get("message").and_then(|x| x.as_str()) {
        let m: String = m.chars().take(200).collect();
        if !m.is_empty() {
            params["message"] = json!(m);
        }
    }
    Some(json!({ "jsonrpc": "2.0", "method": "notifications/progress", "params": params }))
}

/// 取消登记表的键:旧纪元按会话分命名空间(无会话 = 匿名空间),现代纪元共一个空间(另记客户端名防误伤);id 取 JSON 序列化(5 与 "5" 不同)
fn call_key(ns: &str, id: &Value) -> String {
    format!("{}\u{1}{}", ns, id)
}
fn legacy_ns(session: Option<&str>) -> String {
    format!(
        "legacy:{}",
        session
            .map(|s| s.trim())
            .filter(|s| !s.is_empty())
            .unwrap_or("")
    )
}
const MODERN_NS: &str = "modern";
fn modern_client_name(req: &Value) -> Option<String> {
    req.get("params")
        .and_then(|p| p.get("_meta"))
        .and_then(|m| m.get(META_CLIENT_INFO))
        .and_then(|c| c.get("name"))
        .and_then(|v| v.as_str())
        .map(|s| s.to_string())
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
    /// 接收端还在不在(写流线程退出 / 客户端断开即丢弃接收端):订阅前据此清掉已断开的条目,不必往流里塞探测帧
    alive: std::sync::Weak<()>,
}

impl SseSubscriber {
    fn is_live(&self) -> bool {
        self.alive.strong_count() > 0
    }
}

/// 一条事件流的接收端:按 `mpsc::Receiver` 用(解引用);被丢弃即表示这条流已结束,订阅表随之可回收名额。
pub struct SseRx {
    rx: mpsc::Receiver<String>,
    _alive: Arc<()>,
}

impl std::ops::Deref for SseRx {
    type Target = mpsc::Receiver<String>;
    fn deref(&self) -> &Self::Target {
        &self.rx
    }
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

/// 现代请求路由:直接作答 / 可派发(HTTP 层对可派发的 tools/call 才开响应流)
enum ModernRoute {
    Answer(ModernOutcome),
    Dispatch {
        id: Value,
        method: String,
        params: Value,
    },
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

/// 工具定义的对外投影:规范字段原样透传(name / title / description / inputSchema / outputSchema / annotations / icons / _meta),
/// 内部字段(level / category / origin)一律不出壳。此前只投 name / description / inputSchema / annotations,
/// 页面生成的中文 title 与「需用户交互」标记 `_meta` 被丢,外部客户端看不到。
pub fn project_tool(t: &Value) -> Value {
    let mut out = serde_json::Map::new();
    out.insert("name".into(), t.get("name").cloned().unwrap_or(Value::Null));
    if let Some(title) = t.get("title").filter(|v| v.is_string()) {
        out.insert("title".into(), title.clone());
    }
    out.insert(
        "description".into(),
        t.get("description").cloned().unwrap_or(Value::Null),
    );
    out.insert(
        "inputSchema".into(),
        t.get("inputSchema")
            .filter(|v| v.is_object())
            .cloned()
            .unwrap_or(json!({"type":"object"})),
    );
    if let Some(os) = t.get("outputSchema").filter(|v| v.is_object()) {
        out.insert("outputSchema".into(), os.clone());
    }
    out.insert(
        "annotations".into(),
        t.get("annotations")
            .filter(|v| v.is_object())
            .cloned()
            .unwrap_or(json!({})),
    );
    if let Some(icons) = t.get("icons").filter(|v| v.is_array()) {
        out.insert("icons".into(), icons.clone());
    }
    if let Some(meta) = t.get("_meta").filter(|v| v.is_object()) {
        out.insert("_meta".into(), meta.clone());
    }
    Value::Object(out)
}

fn tool_name_ok(name: &str) -> bool {
    if name.is_empty() || name.len() > 48 {
        return false;
    }
    // 外部 MCP 客户端接进来的工具(ext_ 前缀)永不经本机服务再导出给别的客户端
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

/// 0600 + 临时文件 + rename 原子写(读端永远看到完整文件)。
/// 临时文件名随机、`create_new` 独占创建、建时即 0600、不跟随符号链接:目录里预先放好的同名文件 / 链接
/// 既不会被复用,也不会把令牌写到别处;rename 换掉的是目标路径本身(哪怕它原来是个链接,也不顺着它写)。
pub fn write_private_file(path: &Path, content: &[u8]) -> Result<()> {
    let parent = match path.parent() {
        Some(p) if !p.as_os_str().is_empty() => p.to_path_buf(),
        _ => PathBuf::from("."),
    };
    fs::create_dir_all(&parent).ok();
    let base = path
        .file_name()
        .map(|n| n.to_string_lossy().to_string())
        .unwrap_or_else(|| "private".to_string());
    let mut attempt = 0;
    let (tmp, mut file) = loop {
        let tmp = parent.join(format!(".{}.{}.tmp", base, random_suffix()));
        let mut opts = fs::OpenOptions::new();
        opts.write(true).create_new(true);
        #[cfg(unix)]
        {
            use std::os::unix::fs::OpenOptionsExt;
            opts.mode(0o600)
                .custom_flags(libc::O_NOFOLLOW | libc::O_CLOEXEC);
        }
        match opts.open(&tmp) {
            Ok(f) => break (tmp, f),
            Err(e) if e.kind() == std::io::ErrorKind::AlreadyExists && attempt < 8 => {
                attempt += 1;
            }
            Err(e) => return Err(e).with_context(|| format!("create {}", tmp.display())),
        }
    };
    let written = (|| -> std::io::Result<()> {
        #[cfg(unix)]
        {
            // 建时的 0600 受 umask 影响只会更严;这里按句柄再定一次,确保恰为 0600
            use std::os::unix::fs::PermissionsExt;
            file.set_permissions(fs::Permissions::from_mode(0o600))?;
        }
        file.write_all(content)?;
        file.sync_all().ok();
        Ok(())
    })();
    drop(file);
    if let Err(e) = written {
        let _ = fs::remove_file(&tmp);
        return Err(e).with_context(|| format!("write {}", tmp.display()));
    }
    if let Err(e) = fs::rename(&tmp, path) {
        let _ = fs::remove_file(&tmp);
        return Err(e).with_context(|| format!("rename to {}", path.display()));
    }
    Ok(())
}

/// 临时文件名后缀:系统随机源 8 字节(取不到就退回进程号 + 纳秒 + 计数,仍配合 create_new 防撞)。
fn random_suffix() -> String {
    static SEQ: AtomicU64 = AtomicU64::new(0);
    let mut bytes = [0u8; 8];
    if File::open("/dev/urandom")
        .and_then(|mut f| f.read_exact(&mut bytes))
        .is_ok()
    {
        return bytes.iter().map(|b| format!("{:02x}", b)).collect();
    }
    let nanos = std::time::SystemTime::now()
        .duration_since(std::time::UNIX_EPOCH)
        .map(|d| d.as_nanos())
        .unwrap_or(0);
    format!(
        "{}-{}-{}",
        std::process::id(),
        nanos,
        SEQ.fetch_add(1, Ordering::SeqCst)
    )
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
    /// 按用户值设速率(钳 1..600);突发额 = max(10, 速率/6),换档即按新突发额重置余额
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

/// 在途名额(RAII):拿不到 = 已满;了结(含 panic 展开)必还。此前 fetch_add / fetch_sub 手配对,派发 panic 会永久漏一个名额。
struct InflightSlot<'a>(&'a AtomicUsize);

impl<'a> InflightSlot<'a> {
    fn take(counter: &'a AtomicUsize) -> Option<Self> {
        if counter.fetch_add(1, Ordering::SeqCst) >= MAX_INFLIGHT {
            counter.fetch_sub(1, Ordering::SeqCst);
            return None;
        }
        Some(Self(counter))
    }
}

impl Drop for InflightSlot<'_> {
    fn drop(&mut self) {
        self.0.fetch_sub(1, Ordering::SeqCst);
    }
}

/// 幂等键上限(与页面注册表、无头协议层、REST 请求头同一个数)。按 Unicode 码点计(`chars().count()`):
/// 页面(`Array.from(k).length`)与无头协议层同口径 —— emoji / 扩展区汉字算一个字。共用用例表
/// `Horosa-Web/astrostudyui/src/utils/__tests__/fixtures/idempotencyKeyCases.tsv`(三边对拍)
pub const IDEMPOTENCY_KEY_MAX: usize = 200;
/// 超长 / 不是字符串的幂等键:各入口一律报参数错,不静默丢(静默丢 = 调用方以为受了保护,重试照样重复写)
pub const IDEMPOTENCY_KEY_ERROR: &str = "idempotency key must be a string of 1..200 characters";

/// 已去空白的键是否可用(单源:核心转发、REST 请求头、终端命令三处同判)
pub fn idempotency_key_ok(k: &str) -> bool {
    !k.is_empty() && k.chars().count() <= IDEMPOTENCY_KEY_MAX
}

/// 已去空白的原始键 → Ok(None)=没带键(空串)/ Ok(Some)=合法 / Err=超长(REST 请求头与终端命令同一判据)
pub fn idempotency_key_norm(raw: &str) -> std::result::Result<Option<String>, &'static str> {
    let k = raw.trim();
    if k.is_empty() {
        Ok(None)
    } else if idempotency_key_ok(k) {
        Ok(Some(k.to_string()))
    } else {
        Err(IDEMPOTENCY_KEY_ERROR)
    }
}

/// 客户端名上限(按码点计;与无头协议层 `CLIENT_NAME_MAX` 同一个数)
pub const CLIENT_NAME_MAX: usize = 64;
fn client_name_norm(v: Option<&Value>) -> Option<String> {
    let t = v.and_then(|x| x.as_str())?.trim();
    if t.is_empty() {
        None
    } else {
        Some(t.chars().take(CLIENT_NAME_MAX).collect())
    }
}
/// 客户端身份(单一来源;无头协议层 `protocol.clientIdentityOf` 同一规则,共用用例表
/// `Horosa-Web/astrostudyui/src/utils/__tests__/fixtures/clientIdentityCases.tsv`):
/// `_meta.clientName` → `_meta["io.modelcontextprotocol/clientInfo"].name` → 本会话 initialize 报的 clientInfo.name → 传输层缺省。
/// 只认非空字符串(去首尾空白),按码点截 64;全无 = None(页面取最终缺省)。
/// 幂等槽 / 审批键 / 来源标签都按它:同一客户端换传输层、经代理转发前后同一个名字(槽含客户端名,名字一变同键重试就重复写)。
pub fn client_identity_of(
    meta: Option<&Value>,
    session_client: Option<&str>,
    transport_default: Option<&str>,
) -> Option<String> {
    let m = meta.filter(|v| v.is_object());
    client_name_norm(m.and_then(|x| x.get("clientName")))
        .or_else(|| {
            client_name_norm(
                m.and_then(|x| x.get(META_CLIENT_INFO))
                    .filter(|c| c.is_object())
                    .and_then(|c| c.get("name")),
            )
        })
        .or_else(|| {
            client_name_norm(
                session_client
                    .map(|s| Value::String(s.to_string()))
                    .as_ref(),
            )
        })
        .or_else(|| {
            client_name_norm(
                transport_default
                    .map(|s| Value::String(s.to_string()))
                    .as_ref(),
            )
        })
}
/// initialize 里客户端自报的名字(旧纪元按会话记住,之后每条请求的身份缺省取它)
pub fn initialize_client_name(req: &Value) -> Option<String> {
    if req.get("method").and_then(|m| m.as_str()) != Some("initialize") {
        return None;
    }
    client_name_norm(
        req.get("params")
            .and_then(|p| p.get("clientInfo"))
            .filter(|c| c.is_object())
            .and_then(|c| c.get("name")),
    )
}
/// 把身份写进 params._meta.clientName(页面按它认客户端;缺 _meta 就建一个)
fn with_client_identity(params: &Value, session_client: Option<&str>) -> Value {
    let mut p = params.clone();
    let Some(name) = client_identity_of(p.get("_meta"), session_client, None) else {
        return p;
    };
    if let Some(obj) = p.as_object_mut() {
        let meta = obj.entry("_meta".to_string()).or_insert_with(|| json!({}));
        if !meta.is_object() {
            *meta = json!({});
        }
        if let Some(m) = meta.as_object_mut() {
            m.insert("clientName".to_string(), json!(name));
        }
    }
    p
}

/// 写入类调用的幂等键:`_meta.idempotencyKey` 或 `_meta["io.horosa/idempotencyKey"]`(同义);去首尾空白;
/// 没带 / null / 空串 = Ok(None);超长或不是字符串 = Err(调用方回 -32602)
pub fn idempotency_key_check(params: &Value) -> std::result::Result<Option<String>, &'static str> {
    let Some(meta) = params.get("_meta") else {
        return Ok(None);
    };
    let raw = match meta
        .get("idempotencyKey")
        .or_else(|| meta.get("io.horosa/idempotencyKey"))
    {
        None | Some(Value::Null) => return Ok(None),
        Some(v) => v,
    };
    match raw.as_str() {
        Some(t) => idempotency_key_norm(t),
        None => Err(IDEMPOTENCY_KEY_ERROR),
    }
}

/// 工具调用预算:客户端 `_meta.timeoutMs`(钳 1 s..600 s;页面同钳),缺省 120 s
pub fn tool_timeout_of(params: &Value) -> Duration {
    let timeout_ms = params
        .get("_meta")
        .and_then(|m| m.get("timeoutMs"))
        .and_then(|v| v.as_u64())
        .unwrap_or(0);
    if timeout_ms == 0 {
        DEFAULT_TOOL_TIMEOUT
    } else {
        Duration::from_millis(timeout_ms.max(1000)).min(MAX_TOOL_TIMEOUT)
    }
}

/// 取消登记守卫:请求了结(含 panic 展开)即按「同一个取消位」摘掉自己那条,不碰同键的别家
struct CallRegistration<'a> {
    core: &'a McpCore,
    key: String,
    flag: Arc<AtomicBool>,
}

impl Drop for CallRegistration<'_> {
    fn drop(&mut self) {
        if let Ok(mut map) = self.core.calls.lock() {
            if let Some(list) = map.get_mut(&self.key) {
                list.retain(|(_, f)| !Arc::ptr_eq(f, &self.flag));
                if list.is_empty() {
                    map.remove(&self.key);
                }
            }
        }
    }
}

pub struct McpCore {
    token: Mutex<String>,
    app_version: String,
    tools_cache: Mutex<Option<(Instant, Vec<Value>)>>,
    rate: Mutex<RateBucket>,
    inflight: AtomicUsize,
    /// 可选会话:带 Mcp-Session-Id 就必须是本服务发过的;不带一律放行(向下兼容旧客户端)。
    /// 第三项 = 该会话 initialize 时客户端报的 clientInfo.name(客户端身份的会话缺省,见 client_identity_of)
    sessions: Mutex<Vec<(String, Instant, Option<String>)>>,
    /// SSE 订阅者(旧 GET /mcp 流 + [2026-07-28] subscriptions/listen 长流);notify 广播 `event: message`
    sse: Mutex<Vec<SseSubscriber>>,
    /// [2026-07-28] 现代纪元开关(env HOROSA_MCP_MODERN=0 关 = 完全今日行为:现代探测得 400 纯文本再回退 initialize)
    modern_enabled: AtomicBool,
    /// logging/setLevel 记的级别(仅回显,不改变本模块行为;永不吐令牌)
    log_level: Mutex<String>,
    /// 在途请求的取消登记:键 = call_key(命名空间, id);值 = [(客户端名, 取消位)](现代空间里不同客户端可能撞同一个 id)
    calls: Mutex<HashMap<String, Vec<(Option<String>, Arc<AtomicBool>)>>>,
    /// 取消先于请求到达时留的墓碑(键, 客户端名, 时刻)
    cancel_tombstones: Mutex<Vec<(String, Option<String>, Instant)>>,
    /// [REST] 本机 REST 接口(/api/v1)子开关:缺省关(关 = /api/v1 一律 403 并说明去哪开);偏好镜像,服务重建时重新施加
    rest_enabled: AtomicBool,
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
            calls: Mutex::new(HashMap::new()),
            cancel_tombstones: Mutex::new(Vec::new()),
            rest_enabled: AtomicBool::new(false),
            #[cfg(test)]
            session_clock_skew_ms: AtomicU64::new(0),
        }
    }

    // ── [REST] 本机 REST 接口子开关 ─────────────────────────────
    pub fn rest_enabled(&self) -> bool {
        self.rest_enabled.load(Ordering::SeqCst)
    }
    pub fn set_rest_enabled(&self, on: bool) {
        self.rest_enabled.store(on, Ordering::SeqCst);
    }
    pub fn app_version(&self) -> &str {
        &self.app_version
    }

    // ── 取消登记 ────────────────────────────────────────
    /// 登记一条在途请求(派发前);墓碑命中 ⇒ 取消位一进门即置。返回的守卫在请求了结时摘掉登记。
    fn register_call(
        &self,
        key: String,
        client: Option<String>,
        flag: Arc<AtomicBool>,
    ) -> CallRegistration<'_> {
        if let Ok(mut tombs) = self.cancel_tombstones.lock() {
            let now = Instant::now();
            tombs.retain(|(_, _, at)| now.saturating_duration_since(*at) < CANCEL_TOMBSTONE_TTL);
            if let Some(i) = tombs.iter().position(|(k, c, _)| {
                k == &key && (c.is_none() || client.is_none() || c == &client)
            }) {
                tombs.remove(i);
                flag.store(true, Ordering::SeqCst);
            }
        }
        if let Ok(mut map) = self.calls.lock() {
            map.entry(key.clone())
                .or_default()
                .push((client, Arc::clone(&flag)));
        }
        CallRegistration {
            core: self,
            key,
            flag,
        }
    }

    /// 按键取消:给了客户端名 ⇒ 只取消同名(或未记名)的;没给 ⇒ 恰好一条才取消(多条 = 歧义,宁可不取消也不误伤别的客户端)。
    /// 键下一条都没有 ⇒ 留墓碑(取消通知跑在请求前面)。回是否取消了至少一条。
    pub fn cancel_call(&self, key: &str, client: Option<&str>) -> bool {
        let mut hit = 0usize;
        let mut known = false;
        if let Ok(map) = self.calls.lock() {
            if let Some(list) = map.get(key) {
                known = !list.is_empty();
                match client {
                    Some(c) => {
                        for (who, flag) in list.iter() {
                            if who.as_deref().map(|w| w == c).unwrap_or(true) {
                                flag.store(true, Ordering::SeqCst);
                                hit += 1;
                            }
                        }
                    }
                    None => {
                        if list.len() == 1 {
                            list[0].1.store(true, Ordering::SeqCst);
                            hit = 1;
                        }
                    }
                }
            }
        }
        if !known || (hit == 0 && client.is_some()) {
            if let Ok(mut tombs) = self.cancel_tombstones.lock() {
                if tombs.len() >= CANCEL_TOMBSTONE_MAX {
                    tombs.remove(0);
                }
                tombs.push((
                    key.to_string(),
                    client.map(|c| c.to_string()),
                    Instant::now(),
                ));
            }
        }
        hit > 0
    }

    pub fn inflight_call_count(&self) -> usize {
        self.calls
            .lock()
            .map(|m| m.values().map(|v| v.len()).sum())
            .unwrap_or(0)
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

    // ── 可选会话 ──────────────────────────────────────────
    /// 剔除过期会话(表内就地);每次发新会话 / 校验会话前都先做一遍。
    fn prune_expired_sessions(list: &mut Vec<(String, Instant, Option<String>)>, now: Instant) {
        list.retain(|(_, at, _)| now.saturating_duration_since(*at) < SESSION_TTL);
    }
    /// initialize 成功后发一个会话 id(响应头 Mcp-Session-Id);先剔过期,容量仍满则挤掉最旧的。
    pub fn new_session(&self) -> String {
        self.new_session_for(None)
    }
    /// 同上,并记下该会话 initialize 时客户端报的名字(之后这个会话每条请求的身份缺省取它)
    pub fn new_session_for(&self, client: Option<String>) -> String {
        let id = generate_token().unwrap_or_else(|_| format!("s{}", std::process::id()));
        if let Ok(mut list) = self.sessions.lock() {
            let now = self.session_now();
            Self::prune_expired_sessions(&mut list, now);
            if list.len() >= MAX_SESSIONS {
                list.remove(0);
            }
            list.push((id.clone(), now, client));
        }
        id
    }
    /// 会话 initialize 时报的客户端名(没带会话头 / 不认识的会话 / 没报 = None)
    pub fn session_client(&self, header: Option<&str>) -> Option<String> {
        let id = header.map(|s| s.trim()).filter(|s| !s.is_empty())?;
        self.sessions
            .lock()
            .ok()?
            .iter()
            .find(|(x, _, _)| x == id)
            .and_then(|(_, _, c)| c.clone())
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
                l.iter().any(|(x, _, _)| x == id)
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
                l.retain(|(x, _, _)| x != id);
                before != l.len()
            })
            .unwrap_or(false)
    }
    pub fn session_count(&self) -> usize {
        self.sessions.lock().map(|l| l.len()).unwrap_or(0)
    }

    // ── SSE 通知通道 ──────────────────────────────────────
    pub fn sse_count(&self) -> usize {
        self.sse.lock().map(|l| l.len()).unwrap_or(0)
    }
    /// 注册一个旧式 GET 流订阅者;超过上限返回 None(调用方回 429)。
    /// 上限只数旧式流(现代长流另有 MAX_LISTEN_STREAMS),数之前先清掉已断开的条目。
    pub fn sse_subscribe(&self) -> Option<SseRx> {
        let (tx, rx) = mpsc::sync_channel::<String>(SSE_QUEUE);
        let mut list = self.sse.lock().ok()?;
        list.retain(SseSubscriber::is_live);
        if list
            .iter()
            .filter(|s| matches!(s.kind, SseKind::Legacy))
            .count()
            >= MAX_SSE_CLIENTS
        {
            return None;
        }
        // 立刻推一条注释帧:tiny_http 的写缓冲要等到第一块 body 才 flush,不推的话客户端连响应头都读不到
        let _ = tx.try_send(": connected\n\n".to_string());
        let alive = Arc::new(());
        list.push(SseSubscriber {
            tx,
            kind: SseKind::Legacy,
            alive: Arc::downgrade(&alive),
        });
        Some(SseRx { rx, _alive: alive })
    }
    /// [2026-07-28] 现代长流订阅者(subscriptions/listen):与旧 GET 流分别计上限;首帧 = 订阅确认(带 subscriptionId 与同意的通知子集)
    pub fn listen_subscribe(&self, id: Value, filter: ListenFilter) -> Option<SseRx> {
        let (tx, rx) = mpsc::sync_channel::<String>(SSE_QUEUE);
        let mut list = self.sse.lock().ok()?;
        list.retain(SseSubscriber::is_live);
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
        let alive = Arc::new(());
        list.push(SseSubscriber {
            tx,
            kind: SseKind::Modern { id, filter },
            alive: Arc::downgrade(&alive),
        });
        Some(SseRx { rx, _alive: alive })
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

    /// 页面策略「每分钟调用上限」镜像到壳令牌桶(钳 1..600);回实际生效值
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
        "星阙(Horosa)本机工具:只读或只增——永不删除档案、不覆盖已有命盘/事盘;改设置在内的一切写入都记入应用内账本、可由用户撤销。长文本用 maxChars 限制并分页读取。仅在用户明确要求时调用写入类工具。写入类调用可在 _meta.idempotencyKey 带一个幂等键(1..200 字):同键重试回放第一次的结果、不重复写。"
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
        let filtered: Vec<Value> = filter_tools(&raw).iter().map(project_tool).collect();
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
        self.handle_rpc_ctl(req, dispatcher, session, &CallControl::none())
    }

    /// 旧纪元带控制面的分发:请求按(会话, id)登记取消位;notifications/cancelled 按同一键置位(先到则留墓碑)。
    pub fn handle_rpc_ctl(
        &self,
        req: &Value,
        dispatcher: &dyn PageDispatcher,
        session: Option<&str>,
        ctl: &CallControl,
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
            if method == "notifications/cancelled" {
                if let Some(rid) = params.get("requestId").filter(|v| !v.is_null()) {
                    self.cancel_call(&call_key(&legacy_ns(session), rid), None);
                }
            }
            return None;
        }
        let session_id = session
            .map(|s| s.trim())
            .filter(|s| !s.is_empty())
            .map(|s| json!(s))
            .unwrap_or(Value::Null);
        let rid = id.clone().unwrap_or(Value::Null);
        let _reg = self.register_call(
            call_key(&legacy_ns(session), &rid),
            None,
            Arc::clone(&ctl.cancelled),
        );
        // 客户端身份单源(client_identity_of):旧纪元客户端只在 initialize 报 clientInfo,之后按会话记下的名字认
        let params = with_client_identity(&params, self.session_client(session).as_deref());
        let result: std::result::Result<Value, McpError> =
            self.dispatch_method(&method, &params, dispatcher, session_id, ctl);
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
        ctl: &CallControl,
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
                    // v2:工具/资源/提示三面都会推 list_changed(资源不支持逐条 subscribe)
                    // completions:资源模版 / 提示参数补全(cid、技法键)
                    "capabilities": {
                        "tools": { "listChanged": true },
                        "resources": { "subscribe": false, "listChanged": true },
                        "prompts": { "listChanged": true },
                        "completions": {},
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
            "tools/call" => self.call_tool(&with_session(params), dispatcher, ctl),
            // 资源/提示:本模块只做传输,内容全部住页面(命盘/事盘/资料/模版/技法提示卡);params 带上会话身份供页面限流分桶
            // 列表类带 cursor 原样投页面、页面回 nextCursor 原样回客户端(游标对壳不透明)
            "resources/list" => self.page_passthrough(
                "resources/list",
                &with_session(params),
                dispatcher,
                "resources",
                ctl,
            ),
            "resources/templates/list" => self.page_passthrough(
                "resources/templates/list",
                &with_session(params),
                dispatcher,
                "resourceTemplates",
                ctl,
            ),
            "resources/read" => self.page_passthrough(
                "resources/read",
                &with_session(params),
                dispatcher,
                "contents",
                ctl,
            ),
            "prompts/list" => self.page_passthrough(
                "prompts/list",
                &with_session(params),
                dispatcher,
                "prompts",
                ctl,
            ),
            "prompts/get" => self.page_passthrough(
                "prompts/get",
                &with_session(params),
                dispatcher,
                "messages",
                ctl,
            ),
            // 参数补全:回体必须是 {completion:{values:[…]}}(≤100 条由页面保证,壳再截一次)
            "completion/complete" => {
                let mut v = self.page_passthrough(
                    "completion/complete",
                    &with_session(params),
                    dispatcher,
                    "",
                    ctl,
                )?;
                let ok = v
                    .get("completion")
                    .and_then(|c| c.get("values"))
                    .map(|x| x.is_array())
                    .unwrap_or(false);
                if !ok {
                    return Err(McpError::new(
                        ERR_INTERNAL,
                        "page returned malformed completion/complete result",
                    ));
                }
                if let Some(arr) = v
                    .get_mut("completion")
                    .and_then(|c| c.get_mut("values"))
                    .and_then(|x| x.as_array_mut())
                {
                    arr.truncate(100);
                }
                Ok(v)
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
            "capabilities": { "tools": {"listChanged": true}, "resources": {"subscribe": false, "listChanged": true}, "prompts": {"listChanged": true}, "completions": {}, "extensions": {} },
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
        self.handle_modern_ctl(req, headers, dispatcher, &CallControl::none())
    }

    /// 派发前全部判定(不碰页面):回 Some = 不必派发即可作答(HTTP 层据此决定是否改走响应流 —— 只有可派发的调用才值得开流);
    /// None = 可派发。notifications/cancelled 的置位副作用也在这里发生(恰一次)。
    pub fn modern_precheck(
        &self,
        req: &Value,
        headers: Option<&ModernHeaders>,
    ) -> Option<ModernOutcome> {
        match self.modern_route(req, headers) {
            ModernRoute::Answer(o) => Some(o),
            ModernRoute::Dispatch { .. } => None,
        }
    }

    fn modern_route(&self, req: &Value, headers: Option<&ModernHeaders>) -> ModernRoute {
        let id = req.get("id").cloned();
        let method = req
            .get("method")
            .and_then(|m| m.as_str())
            .unwrap_or("")
            .to_string();
        let params = req.get("params").cloned().unwrap_or(json!({}));
        if req.get("jsonrpc").and_then(|v| v.as_str()) != Some("2.0") || method.is_empty() {
            return ModernRoute::Answer(ModernOutcome::Json {
                status: 400,
                body: Self::error_response(
                    id,
                    McpError::new(ERR_INVALID_REQUEST, "invalid request"),
                ),
            });
        }
        let is_notification = id.is_none() || id.as_ref().map(|v| v.is_null()).unwrap_or(true);
        if is_notification {
            // 现代纪元的 HTTP 客户端以「关掉响应流」取消(规范);经 stdio 代理来的客户端发 notifications/cancelled —— 两条都认
            if method == "notifications/cancelled" {
                if let Some(rid) = params.get("requestId").filter(|v| !v.is_null()) {
                    self.cancel_call(
                        &call_key(MODERN_NS, rid),
                        modern_client_name(req).as_deref(),
                    );
                }
            }
            return ModernRoute::Answer(ModernOutcome::Accepted);
        }
        match headers {
            Some(h) => {
                if let Err(e) = validate_modern_request(h, req) {
                    return ModernRoute::Answer(ModernOutcome::Json {
                        status: modern_http_status(e.code),
                        body: Self::error_response(id, e),
                    });
                }
            }
            None => {
                let Some(v) = modern_meta_version(req) else {
                    return ModernRoute::Answer(ModernOutcome::Json {
                        status: 400,
                        body: Self::error_response(
                            id,
                            McpError::new(
                                ERR_INVALID_PARAMS,
                                format!("missing params._meta {}", META_PROTOCOL_VERSION),
                            ),
                        ),
                    });
                };
                if !MCP_MODERN_VERSIONS.contains(&v.as_str()) {
                    return ModernRoute::Answer(ModernOutcome::Json {
                        status: 400,
                        body: Self::error_response(
                            id,
                            McpError::new(ERR_UNSUPPORTED_VERSION, "Unsupported protocol version")
                                .with_data(
                                    json!({ "supported": MCP_MODERN_VERSIONS, "requested": v }),
                                ),
                        ),
                    });
                }
            }
        }
        if !MODERN_METHODS.contains(&method.as_str()) {
            return ModernRoute::Answer(ModernOutcome::Json { status: 404, body: Self::error_response(id, McpError::new(ERR_METHOD_NOT_FOUND, format!("method not found: {} (modern era: initialize/ping/logging are not served to per-request-metadata clients)", method))) });
        }
        if method == "server/discover" {
            return ModernRoute::Answer(ModernOutcome::Json {
                status: 200,
                body: json!({ "jsonrpc": "2.0", "id": id, "result": self.discover_result() }),
            });
        }
        if method == "subscriptions/listen" {
            return ModernRoute::Answer(ModernOutcome::Listen {
                id: id.unwrap_or(Value::Null),
                filter: ListenFilter::from_params(&params),
            });
        }
        ModernRoute::Dispatch {
            id: id.unwrap_or(Value::Null),
            method,
            params,
        }
    }

    /// 现代纪元带控制面的分发:按(现代空间, id, 客户端名)登记取消位;响应流断开 / 取消通知 → 置位 → 页面中止。
    pub fn handle_modern_ctl(
        &self,
        req: &Value,
        headers: Option<&ModernHeaders>,
        dispatcher: &dyn PageDispatcher,
        ctl: &CallControl,
    ) -> ModernOutcome {
        let (id, method, params) = match self.modern_route(req, headers) {
            ModernRoute::Answer(o) => return o,
            ModernRoute::Dispatch { id, method, params } => (id, method, params),
        };
        // 页面按 params._meta.clientName 认客户端;身份单源 client_identity_of(现代纪元逐条带 _meta.clientInfo,没有会话)
        let p = with_client_identity(&params, None);
        let _reg = self.register_call(
            call_key(MODERN_NS, &id),
            modern_client_name(req),
            Arc::clone(&ctl.cancelled),
        );
        match self.dispatch_method(&method, &p, dispatcher, json!("modern"), ctl) {
            Ok(r) => ModernOutcome::Json {
                status: 200,
                body: json!({ "jsonrpc": "2.0", "id": id, "result": self.wrap_modern(&method, r) }),
            },
            Err(e) => ModernOutcome::Json {
                status: 200,
                body: Self::error_response(Some(id), e),
            },
        }
    }

    /// 资源/提示类:参数原样投页面,回体必须带约定的数组字段(缺 → 视为页面畸形返回)。
    /// 与 tools/call 共用同一限流与在途上限:外部客户端读资源同样不能压垮页面。
    fn page_passthrough(
        &self,
        method: &str,
        params: &Value,
        dispatcher: &dyn PageDispatcher,
        expect_key: &str,
        ctl: &CallControl,
    ) -> std::result::Result<Value, McpError> {
        // 墓碑命中(取消先到)⇒ 零投递、也不占限流额
        if ctl.is_cancelled() {
            return Err(cancelled_error());
        }
        {
            let ok = self.rate.lock().map(|mut b| b.take()).unwrap_or(true);
            if !ok {
                return Err(McpError::new(ERR_RATE_LIMITED, "rate limited")
                    .with_data(json!({ "retryAfterMs": 1000 })));
            }
        }
        let Some(_slot) = InflightSlot::take(&self.inflight) else {
            return Err(McpError::new(ERR_RATE_LIMITED, "too many in-flight calls")
                .with_data(json!({ "retryAfterMs": 500 })));
        };
        let v = dispatcher.dispatch_ctl(method, params.clone(), Duration::from_secs(20), ctl)?;
        // expect_key 为空 = 调用方自己校验回体形状(completion/complete 的数组在 completion.values 里)
        if !expect_key.is_empty() && v.get(expect_key).and_then(|x| x.as_array()).is_none() {
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
        ctl: &CallControl,
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
        // 超长 / 非字符串的幂等键 ⇒ 参数错(不静默丢、不投递)
        let idem =
            idempotency_key_check(params).map_err(|m| McpError::new(ERR_INVALID_PARAMS, m))?;
        // 墓碑命中(取消先到)⇒ 零投递、也不占限流额
        if ctl.is_cancelled() {
            return Err(cancelled_error());
        }
        {
            let ok = self.rate.lock().map(|mut b| b.take()).unwrap_or(true);
            if !ok {
                return Err(McpError::new(ERR_RATE_LIMITED, "rate limited")
                    .with_data(json!({ "retryAfterMs": 1000 })));
            }
        }
        let Some(_slot) = InflightSlot::take(&self.inflight) else {
            return Err(McpError::new(ERR_RATE_LIMITED, "too many in-flight calls")
                .with_data(json!({ "retryAfterMs": 500 })));
        };
        let timeout = tool_timeout_of(params);
        // 页面执行预算跟壳同一个数(页面再减 3 s 先回话):此前壳只认客户端 _meta.timeoutMs、却不把它投给页面,
        //   客户端设了短预算时壳先回超时,页面照旧按 120 s 跑完 —— 写入在客户端收到超时之后才落地(重试 = 重复建档)。
        //   progress:true = 本请求有自己的响应流可收进度(页面据此给工具 ctx.progress)。
        let mut page_params = json!({
            "name": name,
            "arguments": arguments,
            "clientName": params.get("_meta").and_then(|m| m.get("clientName")).cloned().unwrap_or(Value::Null),
            "sessionId": params.get("sessionId").cloned().unwrap_or(Value::Null),
            "_meta": { "timeoutMs": timeout.as_millis() as u64 }
        });
        // 幂等键原样投页面(页面注册表据此让同键重试回放、换参报 E_IDEMPOTENCY_CONFLICT):此前这里重建 _meta 只留预算,
        //   MCP 的 _meta.idempotencyKey 与 REST 的 Idempotency-Key 头(rest_api 已放进 _meta)都在这一步被丢掉
        if let Some(k) = idem {
            page_params["_meta"]["idempotencyKey"] = json!(k);
        }
        if ctl.wants_progress() {
            page_params["progress"] = json!(true);
        }
        let v = dispatcher.dispatch_ctl("tools/call", page_params, timeout, ctl)?;
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

/// 句柄被丢弃(含启动半途出错提前返回)也要让服务停下:只置停止位、不等待 ——
/// worker 下一次轮询即退出,最后一个退出时释放端口;否则孤儿服务会一直占着端口且再也关不掉。
impl Drop for McpServerHandle {
    fn drop(&mut self) {
        self.signal_stop();
    }
}

pub(crate) fn header_value<'a>(request: &'a tiny_http::Request, name: &str) -> Option<&'a str> {
    request
        .headers()
        .iter()
        .find(|h| h.field.as_str().as_str().eq_ignore_ascii_case(name))
        .map(|h| h.value.as_str())
}

pub(crate) fn json_response(status: u16, body: &Value) -> Response<std::io::Cursor<Vec<u8>>> {
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

pub(crate) fn plain_response(status: u16, text: &str) -> Response<std::io::Cursor<Vec<u8>>> {
    Response::from_string(text.to_string()).with_status_code(StatusCode(status))
}

/// SSE 写流(旧 GET /mcp 与 [2026-07-28] subscriptions/listen 共用;唯一的 upgrade 裸 socket 出口):
/// 🔴 tiny_http 0.12 的 chunked 编码器有 8KB 内部缓冲:走 Response{reader} 时连响应头都发不出去(实测客户端读 header 即 WouldBlock)。
///    改用 upgrade 拿裸 socket:header 由 tiny_http 写完即 flush,SSE 帧由本线程逐帧写、逐帧 flush。
///    额外的 Connection/Upgrade 头是 hop-by-hop、本机回环无代理,SSE 客户端只认 Content-Type。
/// 独立线程写流:worker 立刻回去收下一个请求(WORKERS=2,被 SSE 占死就收不了 POST);服务停机时现代流先写收尾帧(closing_frame)再关。
fn stream_sse(
    request: tiny_http::Request,
    rx: SseRx,
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

/// 现代纪元「不必派发 / 单体 JSON」的作答(202 / JSON 带状态 / subscriptions/listen 长流)
fn respond_modern_outcome(
    core: &McpCore,
    request: tiny_http::Request,
    outcome: ModernOutcome,
    shutdown: &Arc<AtomicBool>,
) {
    match outcome {
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
}

/// 单请求响应流(POST 回 text/event-stream):进度帧 → 最终回包 → 分块结束标记。全程在本收发线程上写。
/// 🔴 不走 upgrade:upgrade 出去的响应没有长度也没有分块,只能靠关连接收尾,而 tiny_http 的连接循环还攥着写半边 ——
///    回包写完客户端也等不到流结束(每次调用漏一条半开连接)。这里拿 into_writer 的原始写口,自己写状态行与
///    `Transfer-Encoding: chunked`,每帧一个分块逐块 flush,末了 `0\r\n\r\n` —— 规范收尾,连接还能接着复用。
/// 写失败即记「已断开」,此后一切写入短路回 false(调用方据此判断客户端是否还在)。
pub(crate) struct SseResponse {
    writer: std::cell::RefCell<Box<dyn Write + Send>>,
    broken: std::cell::Cell<bool>,
    last_write: std::cell::Cell<Instant>,
}

impl SseResponse {
    pub(crate) fn open(request: tiny_http::Request) -> Self {
        let writer = request.into_writer();
        let me = Self {
            writer: std::cell::RefCell::new(writer),
            broken: std::cell::Cell::new(false),
            last_write: std::cell::Cell::new(Instant::now()),
        };
        me.write_bytes(b"HTTP/1.1 200 OK\r\nContent-Type: text/event-stream\r\nCache-Control: no-store\r\nX-Accel-Buffering: no\r\nTransfer-Encoding: chunked\r\n\r\n");
        me
    }
    pub(crate) fn is_broken(&self) -> bool {
        self.broken.get()
    }
    fn write_bytes(&self, bytes: &[u8]) -> bool {
        if self.broken.get() {
            return false;
        }
        let ok = {
            let mut w = self.writer.borrow_mut();
            w.write_all(bytes).is_ok() && w.flush().is_ok()
        };
        if ok {
            self.last_write.set(Instant::now());
        } else {
            self.broken.set(true);
        }
        ok
    }
    /// 一个 SSE 帧 = 一个分块(空帧永不写:零长分块就是结束标记)
    fn chunk(&self, data: &str) -> bool {
        if data.is_empty() {
            return !self.broken.get();
        }
        let mut buf = format!("{:X}\r\n", data.len()).into_bytes();
        buf.extend_from_slice(data.as_bytes());
        buf.extend_from_slice(b"\r\n");
        self.write_bytes(&buf)
    }
    fn frame(&self, payload: &Value) -> bool {
        self.chunk(&sse_frame(payload))
    }
    /// [REST] 带事件名的帧(`event: progress` / `event: result` …),一帧一个分块
    pub(crate) fn event(&self, name: &str, payload: &Value) -> bool {
        self.chunk(&format!("event: {}\ndata: {}\n\n", name, payload))
    }
    /// 安静超过 `every` 才写一个保活注释;回 false = 客户端已断开
    pub(crate) fn keepalive_if_quiet(&self, every: Duration) -> bool {
        if self.broken.get() {
            return false;
        }
        if self.last_write.get().elapsed() < every {
            return true;
        }
        self.chunk(": keep-alive\n\n")
    }
}

impl Drop for SseResponse {
    fn drop(&mut self) {
        // 分块结束标记:客户端据此知道这次回应完了(不必等关连接)
        let _ = self.write_bytes(b"0\r\n\r\n");
    }
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
        // 不要令牌(终端命令 / stdio 代理靠它核对端点文件里的 pid),但同样只认本机回环的 Host / Origin:
        // 挡住 DNS 重绑定的网页借浏览器探测本机服务与进程号
        if !host_allowed(header_value(&request, "Host")) {
            let _ = request.respond(plain_response(403, "forbidden host"));
            return;
        }
        if !origin_allowed(header_value(&request, "Origin")) {
            let _ = request.respond(plain_response(403, "forbidden origin"));
            return;
        }
        let body = json!({ "app": "horosa", "pid": std::process::id(), "version": app_version, "protocolVersion": MCP_LATEST_PROTOCOL, "modernProtocolVersions": MCP_MODERN_VERSIONS });
        let _ = request.respond(json_response(200, &body));
        return;
    }
    // [REST] 本机 REST 接口:同一服务、同一道门,翻译成同一组 JSON-RPC 方法(见 rest_api.rs)
    if url == crate::rest_api::REST_PREFIX || url.starts_with("/api/v1/") {
        crate::rest_api::handle(core, dispatcher, request);
        return;
    }
    if url != "/mcp" {
        let _ = request.respond(plain_response(404, "not found"));
        return;
    }
    // GET /mcp = SSE 通知通道;DELETE /mcp = 结束会话。两者都先过与 POST **同一** core.gate()
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
    // 客户端收不收响应流(Streamable HTTP 规范要求客户端 Accept 两种都写;只写 JSON 的旧客户端永远走单体 JSON)
    // 分块编码只有 HTTP/1.1 才有;1.0 客户端一律单体 JSON
    let accepts_sse = *request.http_version() >= (1, 1)
        && header_value(&request, "Accept")
            .map(|a| a.contains("text/event-stream"))
            .unwrap_or(false);
    let body_method = parsed
        .get("method")
        .and_then(|m| m.as_str())
        .unwrap_or("")
        .to_string();
    if detect_era(vh, &parsed, core.modern_enabled()) == Era::Modern {
        let hv_version = header_value(&request, "MCP-Protocol-Version").map(|v| v.to_string());
        let hv_method = header_value(&request, "Mcp-Method").map(|v| v.to_string());
        let hv_name = header_value(&request, "Mcp-Name").map(|v| v.to_string());
        let hdrs = ModernHeaders {
            version: hv_version.as_deref(),
            method: hv_method.as_deref(),
            name: hv_name.as_deref(),
        };
        if let Some(outcome) = core.modern_precheck(&parsed, Some(&hdrs)) {
            respond_modern_outcome(core, request, outcome, shutdown);
            return;
        }
        // 现代纪元的 tools/call 一律走响应流(客户端收得了时):规范以「关掉响应流」为取消信号 ——
        //   单体 JSON 等待期间壳看不见客户端断开;响应流每 2 s 一个保活注释,写不进去 = 已断开 = 取消。进度帧(若带令牌)同流下发。
        if accepts_sse && body_method == "tools/call" {
            let sink = SseResponse::open(request);
            let token = progress_token_of(&parsed);
            let last = std::cell::RefCell::new(None::<f64>);
            let on_progress = |v: &Value| -> bool {
                match token
                    .as_ref()
                    .and_then(|t| progress_frame(t, v, &mut last.borrow_mut()))
                {
                    Some(f) => sink.frame(&f),
                    None => !sink.is_broken(),
                }
            };
            let on_tick = || sink.keepalive_if_quiet(SSE_RESPONSE_KEEPALIVE);
            let ctl = CallControl {
                cancelled: Arc::new(AtomicBool::new(false)),
                on_progress: if token.is_some() {
                    Some(&on_progress)
                } else {
                    None
                },
                on_tick: Some(&on_tick),
                cancel_on_disconnect: true,
            };
            if let ModernOutcome::Json { body, .. } =
                core.handle_modern_ctl(&parsed, Some(&hdrs), dispatcher, &ctl)
            {
                if !ctl.is_cancelled() {
                    sink.frame(&body);
                }
            }
            return;
        }
        let outcome = core.handle_modern(&parsed, Some(&hdrs), dispatcher);
        respond_modern_outcome(core, request, outcome, shutdown);
        return;
    }
    if vh == VersionHeader::Unknown {
        // 旧纪元 + 未知版本头 = 今日行为(纯文本 400,不是 JSON-RPC 错误 ⇒ 双纪元客户端据此回退 initialize)
        let _ = request.respond(plain_response(400, "unsupported MCP-Protocol-Version"));
        return;
    }
    // 旧纪元:带进度令牌的 tools/call 且客户端收得了响应流 ⇒ 响应流(进度帧 → 回包);其余逐字同今日单体 JSON。
    //   旧纪元规范写明「断开不算取消」(取消靠 notifications/cancelled),这里断开只停写、不置取消位。
    let has_id = parsed.get("id").map(|v| !v.is_null()).unwrap_or(false);
    if accepts_sse && has_id && body_method == "tools/call" {
        if let Some(token) = progress_token_of(&parsed) {
            let session_owned = header_value(&request, "Mcp-Session-Id").map(|s| s.to_string());
            let sink = SseResponse::open(request);
            let last = std::cell::RefCell::new(None::<f64>);
            let on_progress = |v: &Value| -> bool {
                match progress_frame(&token, v, &mut last.borrow_mut()) {
                    Some(f) => sink.frame(&f),
                    None => !sink.is_broken(),
                }
            };
            let on_tick = || sink.keepalive_if_quiet(SSE_RESPONSE_KEEPALIVE);
            let ctl = CallControl {
                cancelled: Arc::new(AtomicBool::new(false)),
                on_progress: Some(&on_progress),
                on_tick: Some(&on_tick),
                cancel_on_disconnect: false,
            };
            if let Some(v) =
                core.handle_rpc_ctl(&parsed, dispatcher, session_owned.as_deref(), &ctl)
            {
                // 规范:被取消的请求不再回包(客户端也会忽略);关流即了结
                if !ctl.is_cancelled() {
                    sink.frame(&v);
                }
            }
            return;
        }
    }
    let is_init = parsed.get("method").and_then(|m| m.as_str()) == Some("initialize");
    let session_header = header_value(&request, "Mcp-Session-Id");
    match core.handle_rpc_with_session(&parsed, dispatcher, session_header.as_deref()) {
        None => {
            let _ = request.respond(plain_response(202, ""));
        }
        Some(v) => {
            let mut r = json_response(200, &v);
            // initialize 成功 → 发一个会话 id;客户端此后可带 Mcp-Session-Id(不带也照旧放行)
            if is_init && v.get("result").is_some() {
                if let Ok(h) = Header::from_bytes(
                    &b"Mcp-Session-Id"[..],
                    core.new_session_for(initialize_client_name(&parsed))
                        .as_bytes(),
                ) {
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
                    Err(e) => {
                        // 接受新连接出错(文件描述符耗尽等):接受线程会退避后自行续接,一串连续错误只报这一次;
                        // 落账留痕,不再静默吞掉
                        crate::ledger_mark(
                            "rust.mcp_server_accept_error",
                            Some(json!({ "port": port, "error": e.to_string() })),
                        );
                        continue;
                    }
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

/// 页面 → 壳的单次调用消息:进度(可多条)/ 了结(恰一条)。通道无界:壳侧发送永不阻塞
/// (回传命令跑在应用主线程上,有界通道满了会卡住界面);页面已节流,条数另有 PROGRESS_FRAMES_MAX 硬顶。
enum BridgeMsg {
    Progress(Value),
    Done(std::result::Result<Value, McpError>),
}

struct PendingCall {
    tx: mpsc::Sender<BridgeMsg>,
    progress_seen: usize,
}

/// 页面桥:eval 投递 + 等待页面 invoke 回传。
pub struct PageBridge {
    app: Mutex<Option<tauri::AppHandle>>,
    pending: Mutex<HashMap<u64, PendingCall>>,
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
        let tx = self
            .pending
            .lock()
            .ok()
            .and_then(|mut p| p.remove(&id))
            .map(|c| c.tx);
        match tx {
            Some(tx) => tx.send(BridgeMsg::Done(outcome)).is_ok(),
            None => false,
        }
    }

    /// 页面回传一条进度;调用已了结 / 超出硬顶 → 丢(回 false)。永不阻塞。
    pub fn progress(&self, id: u64, value: Value) -> bool {
        let Ok(mut p) = self.pending.lock() else {
            return false;
        };
        let Some(call) = p.get_mut(&id) else {
            return false;
        };
        if call.progress_seen >= PROGRESS_FRAMES_MAX {
            return false;
        }
        call.progress_seen += 1;
        call.tx.send(BridgeMsg::Progress(value)).is_ok()
    }

    pub fn fail_all_pending(&self, err: McpError) {
        if let Ok(mut p) = self.pending.lock() {
            for (_, c) in p.drain() {
                let _ = c.tx.send(BridgeMsg::Done(Err(err.clone())));
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

    /// 取消脚本:id 是壳自己发的整数,不经任何外部输入拼接;页面没挂取消钩子(旧页面)= 空操作,
    /// 还在就绪前队列里的同 id 请求一并摘掉(壳已回了结,页面再执行等于白跑 / 写入落地无人知)。
    pub fn cancel_script(id: u64) -> String {
        format!(
            "(function(){{try{{if(typeof window.__horosaAgentToolCancel==='function'){{window.__horosaAgentToolCancel({id});}}var q=window.__horosaPendingAgentTools;if(Array.isArray(q)){{for(var i=q.length-1;i>=0;i--){{if(q[i]&&q[i].id==={id}){{q.splice(i,1);}}}}}}}}catch(e){{}}}})();",
            id = id
        )
    }

    fn main_window(&self) -> std::result::Result<tauri::WebviewWindow, McpError> {
        let app = self.app.lock().ok().and_then(|a| a.clone());
        let Some(app) = app else {
            return Err(McpError::new(ERR_NOT_READY, "app not ready")
                .with_data(json!({ "retryAfterMs": 1500 })));
        };
        use tauri::Manager;
        app.get_webview_window(crate::MAIN_WINDOW_LABEL)
            .ok_or_else(|| {
                McpError::new(ERR_NOT_READY, "main window not ready")
                    .with_data(json!({ "retryAfterMs": 1500 }))
            })
    }
}

impl PageDispatcher for PageBridge {
    fn dispatch(
        &self,
        method: &str,
        params: Value,
        timeout: Duration,
    ) -> std::result::Result<Value, McpError> {
        self.dispatch_ctl(method, params, timeout, &CallControl::none())
    }

    fn dispatch_ctl(
        &self,
        method: &str,
        params: Value,
        timeout: Duration,
        ctl: &CallControl,
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
        if ctl.is_cancelled() {
            return Err(cancelled_error());
        }
        let window = self.main_window()?;
        let id = self.next_id.fetch_add(1, Ordering::SeqCst);
        let (tx, rx) = mpsc::channel();
        if let Ok(mut p) = self.pending.lock() {
            p.insert(
                id,
                PendingCall {
                    tx,
                    progress_seen: 0,
                },
            );
        }
        let payload = json!({ "id": id, "method": method, "params": params });
        if window.eval(&Self::dispatch_script(&payload)).is_err() {
            if let Ok(mut p) = self.pending.lock() {
                p.remove(&id);
            }
            return Err(McpError::new(ERR_NOT_READY, "page eval failed")
                .with_data(json!({ "retryAfterMs": 1500 })));
        }
        // 分片等待:停服/页面离场时 fail_all_pending 会立刻送错;这里再按 stopping 位兜底,绝不整段死等。
        // 每片顺带:转发进度、心跳(响应流保活 / 断流探测)、看取消位 —— 取消即通知页面中止并立刻了结
        let deadline = Instant::now() + timeout;
        loop {
            if ctl.is_cancelled() {
                if let Ok(mut p) = self.pending.lock() {
                    p.remove(&id);
                }
                let _ = window.eval(&Self::cancel_script(id));
                return Err(cancelled_error());
            }
            match rx.recv_timeout(Duration::from_millis(250)) {
                Ok(BridgeMsg::Done(r)) => return r,
                Ok(BridgeMsg::Progress(v)) => ctl.progress(&v),
                Err(mpsc::RecvTimeoutError::Disconnected) => break,
                Err(mpsc::RecvTimeoutError::Timeout) => ctl.tick(),
            }
            if self.stopping.load(Ordering::SeqCst) || Instant::now() >= deadline {
                break;
            }
        }
        if let Ok(mut p) = self.pending.lock() {
            p.remove(&id);
        }
        if self.stopping.load(Ordering::SeqCst) {
            return Err(McpError::new(ERR_NOT_READY, "server stopping")
                .with_data(json!({ "retryAfterMs": 5000 })));
        }
        // 超时同样通知页面中止(页面自带的超时比壳早 3 s,正常走不到这里;页面卡死时这是最后一道)
        let _ = window.eval(&Self::cancel_script(id));
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
    /// 用户设的每分钟调用上限(偏好镜像;服务重建时重新施加)
    pub calls_per_minute: u32,
    /// [REST] 本机 REST 接口子开关(偏好镜像;服务重建时重新施加)
    pub rest_enabled: bool,
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
                rest_enabled: false,
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
    load_or_create_token_at(&token_path(app)?)
}

/// 读已有令牌(须是普通文件;权限不是 0600 就当场纠正),没有 / 不像样 / 是符号链接 ⇒ 新生成并私有写入。
fn load_or_create_token_at(path: &Path) -> Result<String> {
    let regular = fs::symlink_metadata(path)
        .map(|m| m.file_type().is_file())
        .unwrap_or(false);
    if regular {
        if let Ok(existing) = fs::read_to_string(path) {
            let t = existing.trim().to_string();
            if t.len() >= 32 {
                #[cfg(unix)]
                {
                    use std::os::unix::fs::PermissionsExt;
                    let loose = fs::metadata(path)
                        .map(|m| m.permissions().mode() & 0o777 != 0o600)
                        .unwrap_or(false);
                    if loose {
                        fs::set_permissions(path, fs::Permissions::from_mode(0o600))
                            .with_context(|| format!("chmod 0600 {}", path.display()))?;
                    }
                }
                return Ok(t);
            }
        }
    }
    let token = generate_token()?;
    write_private_file(path, token.as_bytes())?;
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
    core.set_rest_enabled(inner.rest_enabled);
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
        // calls-per-minute in effect (mirror of the page-side external policy)
        "callsPerMinute": calls_per_minute,
        "modern": modern_on,
        "endpointFile": if running { endpoint_file } else { ep },
        // 本 App 二进制路径:给 stdio 代理形态的客户端配置(command/args)用;非秘密
        "binaryPath": std::env::current_exe().map(|p| p.display().to_string()).unwrap_or_default(),
        "pageReady": state.bridge.is_ready(),
        // 在途的外部调用数(诊断用;不含任何请求内容)
        "inflightCalls": inner.as_ref().and_then(|i| i.core.as_ref().map(|c| c.inflight_call_count())).unwrap_or(0),
        // [REST] 本机 REST 接口子开关与入口(与 /mcp 同端口、同令牌)
        "restEnabled": inner.as_ref().map(|i| i.rest_enabled).unwrap_or(false),
        "restUrl": if running { format!("http://127.0.0.1:{}{}", port, crate::rest_api::REST_PREFIX) } else { String::new() },
    })
}

/// [REST] 设本机 REST 接口子开关(偏好镜像 + 运行中的核即刻生效;服务重建时 start_locked 重新施加)
pub fn apply_rest_enabled(state: &McpState, on: bool) {
    if let Ok(mut inner) = state.inner.lock() {
        inner.rest_enabled = on;
        if let Some(core) = inner.core.as_ref() {
            core.set_rest_enabled(on);
        }
    }
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

/// 施加「每分钟调用上限」:记进 inner(服务重建时重施)并立即作用于在跑的核;回实际生效值
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
                // 资源/提示:页面侧回体形状(resources/read 对 horosa://bad 故意回畸形,验传输层不当成功)
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
        assert_eq!(init["result"]["capabilities"]["tools"]["listChanged"], true); // v2:三面都推 list_changed
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
        // resources/* 与 prompts/* 已实装;仍未支持的方法照旧 -32601
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

    /// 令牌桶跟随用户设置:1/分钟 ⇒ 第二次即拒;600/分钟 ⇒ 100 连发不拒;非法值钳到 1..600;桶余额超过新突发额即截断
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

    /// 读一条 HTTP 响应(状态 / 头 / 体):Content-Length 体照读;分块体按块拼回(响应流 = text/event-stream + chunked)
    fn read_response(reader: &mut BufReader<TcpStream>) -> (u16, Vec<String>, String) {
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
        let mut chunked = false;
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
            if lower.starts_with("transfer-encoding:") && lower.contains("chunked") {
                chunked = true;
            }
            headers.push(line.trim().to_string());
        }
        if chunked {
            let mut body = Vec::new();
            loop {
                let mut size_line = String::new();
                if reader.read_line(&mut size_line).unwrap_or(0) == 0 {
                    break;
                }
                let n = usize::from_str_radix(size_line.trim(), 16).unwrap_or(0);
                if n == 0 {
                    let mut crlf = String::new();
                    let _ = reader.read_line(&mut crlf);
                    break;
                }
                let mut chunk = vec![0u8; n + 2];
                reader.read_exact(&mut chunk).unwrap();
                body.extend_from_slice(&chunk[..n]);
            }
            return (status, headers, String::from_utf8_lossy(&body).to_string());
        }
        let mut body = vec![0u8; content_length];
        if content_length > 0 {
            reader.read_exact(&mut body).unwrap();
        }
        (status, headers, String::from_utf8_lossy(&body).to_string())
    }

    /// 响应流体里的每条 JSON-RPC 消息(按出现先后)
    fn sse_messages(body: &str) -> Vec<Value> {
        body.split("\n\n")
            .filter_map(|ev| {
                let data: Vec<&str> = ev
                    .lines()
                    .filter_map(|l| l.strip_prefix("data: ").or_else(|| l.strip_prefix("data:")))
                    .collect();
                if data.is_empty() {
                    None
                } else {
                    serde_json::from_str::<Value>(&data.join("\n")).ok()
                }
            })
            .collect()
    }

    fn http(port: u16, req: &str) -> (u16, String) {
        let mut stream = TcpStream::connect(("127.0.0.1", port)).unwrap();
        stream.write_all(req.as_bytes()).unwrap();
        stream.flush().unwrap();
        let mut reader = BufReader::new(stream);
        let (status, headers, body) = read_response(&mut reader);
        // 响应流 ⇒ 交出最后一条消息(回包)的 JSON,与单体 JSON 同一形状给断言用
        if headers.iter().any(|h| {
            h.to_ascii_lowercase()
                .starts_with("content-type: text/event-stream")
        }) {
            let last = sse_messages(&body)
                .pop()
                .map(|v| v.to_string())
                .unwrap_or_default();
            return (status, last);
        }
        (status, body)
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

    // ───────────────────── 通知洪泛 / 会话过期 / 会话 churn ─────────────────────

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
        // GET /mcp 已是 SSE 通道:门在语义之前——无令牌 → 401(不是 405/406)
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
        let (tx, rx) = mpsc::channel();
        bridge.pending.lock().unwrap().insert(
            42,
            PendingCall {
                tx,
                progress_seen: 0,
            },
        );
        // 进度只投给在途调用;了结后再来的进度一律丢
        assert!(bridge.progress(42, json!({ "progress": 1 })));
        assert!(!bridge.progress(43, json!({ "progress": 1 })));
        bridge.set_ready(false);
        assert!(matches!(
            rx.recv_timeout(Duration::from_millis(200)).unwrap(),
            BridgeMsg::Progress(_)
        ));
        match rx.recv_timeout(Duration::from_millis(200)).unwrap() {
            BridgeMsg::Done(r) => assert_eq!(r.unwrap_err().code, ERR_NOT_READY),
            BridgeMsg::Progress(_) => panic!("expected done"),
        }
        assert!(
            !bridge.progress(42, json!({ "progress": 2 })),
            "了结后进度丢弃"
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
        read_response(&mut reader)
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
        // 2025-11-25 已进支持表 ⇒ 按客户端所请协商(此前不认,降到 2025-06-18)
        assert_eq!(
            v["result"]["protocolVersion"], "2025-11-25",
            "2025-11-25 在支持表 ⇒ 原样协商"
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
        let (st4, out4) = post(port, &format!("Authorization: Bearer {}\r\nMCP-Protocol-Version: 2025-11-25\r\nMcp-Session-Id: {}\r\n", token, sid), "{\"jsonrpc\":\"2.0\",\"id\":3,\"method\":\"tools/list\"}");
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

    // ───────────────────────── 协议层补齐:字段透传 / 补全 / 分页 / 进度 / 取消 / 预算 ─────────────────────────

    /// 进度 / 取消 / 心跳的假页面:tools/call 先发 progress_steps,再跑 run_for(期间看取消位、打心跳)
    struct CtlPage {
        progress_steps: Vec<f64>,
        run_for: Duration,
        saw_cancel: Arc<AtomicBool>,
        done: Arc<AtomicUsize>,
        seen: Arc<Mutex<Vec<Value>>>,
    }

    fn ctl_page(steps: Vec<f64>, run_for: Duration) -> CtlPage {
        CtlPage {
            progress_steps: steps,
            run_for,
            saw_cancel: Arc::new(AtomicBool::new(false)),
            done: Arc::new(AtomicUsize::new(0)),
            seen: Arc::new(Mutex::new(Vec::new())),
        }
    }

    impl PageDispatcher for CtlPage {
        fn dispatch(
            &self,
            method: &str,
            params: Value,
            timeout: Duration,
        ) -> std::result::Result<Value, McpError> {
            self.dispatch_ctl(method, params, timeout, &CallControl::none())
        }
        fn dispatch_ctl(
            &self,
            method: &str,
            params: Value,
            _timeout: Duration,
            ctl: &CallControl,
        ) -> std::result::Result<Value, McpError> {
            if let Ok(mut v) = self.seen.lock() {
                v.push(json!({ "method": method, "params": params.clone() }));
            }
            match method {
                "tools/list" => Ok(json!({ "tools": fake_tools() })),
                "tools/call" => {
                    for p in &self.progress_steps {
                        ctl.progress(&json!({ "progress": p, "total": 3, "message": format!("第 {} 步", p) }));
                    }
                    let until = Instant::now() + self.run_for;
                    while Instant::now() < until {
                        if ctl.is_cancelled() {
                            self.saw_cancel.store(true, Ordering::SeqCst);
                            return Err(cancelled_error());
                        }
                        ctl.tick();
                        thread::sleep(Duration::from_millis(20));
                    }
                    self.done.fetch_add(1, Ordering::SeqCst);
                    Ok(json!({ "content": [{ "type": "text", "text": "done" }], "isError": false }))
                }
                _ => Err(McpError::new(ERR_METHOD_NOT_FOUND, "nope")),
            }
        }
    }

    #[test]
    fn tools_list_projects_title_meta_output_schema_and_drops_internal_fields() {
        let c = core();
        let page = FakePage {
            tools: vec![
                json!({ "name": "list_records", "title": "列出档案", "level": "read", "category": "query", "origin": "builtin", "description": "d", "inputSchema": {"type":"object"}, "outputSchema": {"type":"object","properties":{"items":{"type":"array"}}}, "annotations": {"readOnlyHint": true}, "_meta": {"anthropic/requiresUserInteraction": true}, "icons": [{"src":"data:image/png;base64,AA=="}] }),
            ],
            fail_with: None,
        };
        let list = c
            .handle_rpc(
                &json!({ "jsonrpc": "2.0", "id": 1, "method": "tools/list" }),
                &page,
            )
            .unwrap();
        let t = &list["result"]["tools"][0];
        assert_eq!(t["title"], "列出档案");
        assert_eq!(t["outputSchema"]["properties"]["items"]["type"], "array");
        assert_eq!(t["_meta"]["anthropic/requiresUserInteraction"], true);
        assert!(t["icons"].is_array());
        assert_eq!(t["annotations"]["readOnlyHint"], true);
        for k in ["level", "category", "origin"] {
            assert!(t.get(k).is_none(), "内部字段 {k} 不出壳");
        }
        // 判别力:没有的字段不凭空长出来;畸形字段(title 非串 / outputSchema 非对象 / _meta 非对象)不透传
        let bare = project_tool(&json!({ "name": "x", "description": "d" }));
        assert!(
            bare.get("title").is_none()
                && bare.get("outputSchema").is_none()
                && bare.get("_meta").is_none()
        );
        assert_eq!(bare["inputSchema"], json!({"type":"object"}));
        let weird = project_tool(
            &json!({ "name": "x", "title": 5, "outputSchema": "nope", "_meta": [], "inputSchema": "bad" }),
        );
        assert!(
            weird.get("title").is_none()
                && weird.get("outputSchema").is_none()
                && weird.get("_meta").is_none()
        );
        assert_eq!(weird["inputSchema"], json!({"type":"object"}));
    }

    #[test]
    fn completion_capability_new_legacy_version_and_passthrough() {
        let c = core();
        struct CompPage;
        impl PageDispatcher for CompPage {
            fn dispatch(
                &self,
                m: &str,
                p: Value,
                _t: Duration,
            ) -> std::result::Result<Value, McpError> {
                match m {
                    "completion/complete" => {
                        if p["ref"]["name"] == "bad" {
                            return Ok(json!({ "oops": 1 }));
                        }
                        let vals: Vec<String> = (0..150).map(|i| format!("v{i}")).collect();
                        Ok(
                            json!({ "completion": { "values": vals, "total": 150, "hasMore": true } }),
                        )
                    }
                    _ => Err(McpError::new(ERR_METHOD_NOT_FOUND, "nope")),
                }
            }
        }
        let init = c.handle_rpc(&json!({ "jsonrpc": "2.0", "id": 1, "method": "initialize", "params": { "protocolVersion": "2025-11-25" } }), &CompPage).unwrap();
        assert_eq!(init["result"]["protocolVersion"], "2025-11-25");
        assert!(init["result"]["capabilities"]["completions"].is_object());
        assert!(protocol_version_allowed(Some("2025-11-25")));
        assert_eq!(
            classify_version_header(Some("2025-11-25")),
            VersionHeader::Legacy
        );
        let r = c.handle_rpc(&json!({ "jsonrpc": "2.0", "id": 2, "method": "completion/complete", "params": { "ref": { "type": "ref/resource", "uri": "horosa://chart/{cid}" }, "argument": { "name": "cid", "value": "张" } } }), &CompPage).unwrap();
        assert_eq!(
            r["result"]["completion"]["values"]
                .as_array()
                .unwrap()
                .len(),
            100,
            "壳再截一次 ≤100"
        );
        assert_eq!(r["result"]["completion"]["hasMore"], true);
        let bad = c.handle_rpc(&json!({ "jsonrpc": "2.0", "id": 3, "method": "completion/complete", "params": { "ref": { "type": "ref/prompt", "name": "bad" }, "argument": { "name": "q", "value": "" } } }), &CompPage).unwrap();
        assert_eq!(bad["error"]["code"], ERR_INTERNAL, "畸形回体不当成功");
        // 现代纪元:方法在集内、discover 宣告 completions
        let m = modern_core();
        assert!(m.discover_result()["capabilities"]["completions"].is_object());
        assert!(MODERN_METHODS.contains(&"completion/complete"));
        match m.handle_modern(&mreq(4, "completion/complete", json!({ "ref": { "type": "ref/prompt", "name": "technique:bazi" }, "argument": { "name": "cid", "value": "" } })), None, &CompPage) {
            ModernOutcome::Json { status, body } => {
                assert_eq!(status, 200);
                assert!(body["result"]["completion"]["values"].is_array());
                assert_eq!(body["result"]["resultType"], "complete");
            }
            _ => panic!("expected json"),
        }
    }

    #[test]
    fn list_cursor_goes_to_page_and_next_cursor_comes_back() {
        let c = core();
        struct Pager;
        impl PageDispatcher for Pager {
            fn dispatch(
                &self,
                m: &str,
                p: Value,
                _t: Duration,
            ) -> std::result::Result<Value, McpError> {
                match m {
                    "resources/list" => {
                        let cur = p.get("cursor").and_then(|x| x.as_str()).unwrap_or("");
                        if cur.is_empty() {
                            Ok(
                                json!({ "resources": [{ "uri": "horosa://chart/a", "name": "a" }], "nextCursor": "c1" }),
                            )
                        } else if cur == "c1" {
                            Ok(json!({ "resources": [{ "uri": "horosa://chart/b", "name": "b" }] }))
                        } else {
                            Err(McpError::new(ERR_INVALID_PARAMS, "invalid cursor"))
                        }
                    }
                    "prompts/list" => Ok(json!({ "prompts": [], "nextCursor": "p2" })),
                    _ => Err(McpError::new(ERR_METHOD_NOT_FOUND, "nope")),
                }
            }
        }
        let r1 = c
            .handle_rpc(
                &json!({ "jsonrpc": "2.0", "id": 1, "method": "resources/list" }),
                &Pager,
            )
            .unwrap();
        assert_eq!(r1["result"]["nextCursor"], "c1");
        let r2 = c.handle_rpc(&json!({ "jsonrpc": "2.0", "id": 2, "method": "resources/list", "params": { "cursor": "c1" } }), &Pager).unwrap();
        assert!(
            r2["result"].get("nextCursor").is_none(),
            "最后一页不带 nextCursor"
        );
        assert_eq!(r2["result"]["resources"][0]["name"], "b");
        let r3 = c.handle_rpc(&json!({ "jsonrpc": "2.0", "id": 3, "method": "resources/list", "params": { "cursor": "zz" } }), &Pager).unwrap();
        assert_eq!(r3["error"]["code"], ERR_INVALID_PARAMS);
        let m = modern_core();
        match m.handle_modern(&mreq(4, "prompts/list", json!({})), None, &Pager) {
            ModernOutcome::Json { body, .. } => {
                assert_eq!(body["result"]["nextCursor"], "p2");
                assert_eq!(body["result"]["cacheScope"], "private");
            }
            _ => panic!("expected json"),
        }
    }

    #[test]
    fn progress_frame_and_token_vectors() {
        let tok = json!("t");
        let mut last = None;
        assert!(progress_frame(&tok, &json!({ "progress": "x" }), &mut last).is_none());
        let f = progress_frame(
            &tok,
            &json!({ "progress": 1, "total": 4, "message": "开始" }),
            &mut last,
        )
        .unwrap();
        assert_eq!(f["method"], "notifications/progress");
        assert_eq!(f["params"]["progressToken"], "t");
        assert_eq!(f["params"]["progress"], 1.0);
        assert_eq!(f["params"]["total"], 4.0);
        assert_eq!(f["params"]["message"], "开始");
        assert!(
            progress_frame(&tok, &json!({ "progress": 1 }), &mut last).is_none(),
            "相等不发(规范:必须递增)"
        );
        assert!(
            progress_frame(&tok, &json!({ "progress": 0.5 }), &mut last).is_none(),
            "回退不发"
        );
        let long = "长".repeat(500);
        let g = progress_frame(
            &json!(9),
            &json!({ "progress": 2, "message": long }),
            &mut last,
        )
        .unwrap();
        assert_eq!(g["params"]["progressToken"], 9);
        assert_eq!(
            g["params"]["message"].as_str().unwrap().chars().count(),
            200
        );
        assert!(g["params"].get("total").is_none());
        assert!(
            progress_token_of(&json!({ "params": { "_meta": { "progressToken": 1.5 } } }))
                .is_none()
        );
        assert!(
            progress_token_of(&json!({ "params": { "_meta": { "progressToken": {} } } })).is_none()
        );
        assert_eq!(
            progress_token_of(&json!({ "params": { "_meta": { "progressToken": 3 } } })),
            Some(json!(3))
        );
        assert!(progress_token_of(&json!({ "params": {} })).is_none());
    }

    #[test]
    fn tool_budget_reaches_page_and_progress_flag_only_with_a_stream() {
        let c = core();
        let page = ctl_page(vec![], Duration::from_millis(0));
        for (i, meta) in [
            json!({ "timeoutMs": 30000 }),
            json!({}),
            json!({ "timeoutMs": 5 }),
            json!({ "timeoutMs": 9999999 }),
        ]
        .iter()
        .enumerate()
        {
            c.handle_rpc(&json!({ "jsonrpc": "2.0", "id": i, "method": "tools/call", "params": { "name": "list_records", "arguments": {}, "_meta": meta } }), &page);
        }
        {
            let seen = page.seen.lock().unwrap();
            let ms: Vec<u64> = seen
                .iter()
                .map(|s| s["params"]["_meta"]["timeoutMs"].as_u64().unwrap())
                .collect();
            assert_eq!(
                ms,
                vec![30000, 120000, 1000, 600000],
                "壳的预算原样投页面(页面再减 3 s 先回话)"
            );
            assert!(
                seen.iter().all(|s| s["params"].get("progress").is_none()),
                "没有响应流就不向页面要进度"
            );
        }
        let f = |_v: &Value| true;
        let ctl = CallControl {
            cancelled: Arc::new(AtomicBool::new(false)),
            on_progress: Some(&f),
            on_tick: None,
            cancel_on_disconnect: false,
        };
        c.handle_rpc_ctl(&json!({ "jsonrpc": "2.0", "id": 9, "method": "tools/call", "params": { "name": "list_records", "arguments": {} } }), &page, None, &ctl);
        assert_eq!(page.seen.lock().unwrap()[4]["params"]["progress"], true);
    }

    #[test]
    fn legacy_cancel_notification_stops_inflight_call_and_tombstone_precancels() {
        let c = Arc::new(core());
        let page = Arc::new(ctl_page(vec![], Duration::from_secs(5)));
        let c2 = Arc::clone(&c);
        let p2 = Arc::clone(&page);
        let t0 = Instant::now();
        let h = thread::spawn(move || {
            c2.handle_rpc_with_session(&json!({ "jsonrpc": "2.0", "id": 41, "method": "tools/call", "params": { "name": "list_records", "arguments": {} } }), p2.as_ref(), Some("sess-A"))
        });
        let deadline = Instant::now() + Duration::from_secs(2);
        while c.inflight_call_count() == 0 && Instant::now() < deadline {
            thread::sleep(Duration::from_millis(5));
        }
        assert_eq!(c.inflight_call_count(), 1);
        // 别的会话发同 id 的取消 ⇒ 不误伤
        assert!(c.handle_rpc_with_session(&json!({ "jsonrpc": "2.0", "method": "notifications/cancelled", "params": { "requestId": 41 } }), page.as_ref(), Some("sess-B")).is_none());
        thread::sleep(Duration::from_millis(120));
        assert!(
            !page.saw_cancel.load(Ordering::SeqCst),
            "别的会话的取消不得命中"
        );
        // 同会话 ⇒ 命中、立刻了结
        c.handle_rpc_with_session(&json!({ "jsonrpc": "2.0", "method": "notifications/cancelled", "params": { "requestId": 41, "reason": "user" } }), page.as_ref(), Some("sess-A"));
        let out = h.join().unwrap().unwrap();
        assert_eq!(out["error"]["code"], ERR_CANCELLED);
        assert!(page.saw_cancel.load(Ordering::SeqCst));
        assert!(
            t0.elapsed() < Duration::from_secs(3),
            "取消后立刻了结,不等满 5 s"
        );
        assert_eq!(c.inflight_call_count(), 0, "登记随请求了结摘掉");
        // 墓碑:取消先到 ⇒ 随后到达的同键请求一进门即判取消,页面零投递;墓碑只用一次
        c.handle_rpc_with_session(&json!({ "jsonrpc": "2.0", "method": "notifications/cancelled", "params": { "requestId": 42 } }), page.as_ref(), Some("sess-A"));
        let before = page.seen.lock().unwrap().len();
        let r = c.handle_rpc_with_session(&json!({ "jsonrpc": "2.0", "id": 42, "method": "tools/call", "params": { "name": "list_records", "arguments": {} } }), page.as_ref(), Some("sess-A")).unwrap();
        assert_eq!(r["error"]["code"], ERR_CANCELLED);
        assert_eq!(
            page.seen.lock().unwrap().len(),
            before,
            "墓碑命中的请求零投递"
        );
        let quick = ctl_page(vec![], Duration::from_millis(0));
        let again = c.handle_rpc_with_session(&json!({ "jsonrpc": "2.0", "id": 42, "method": "tools/call", "params": { "name": "list_records", "arguments": {} } }), &quick, Some("sess-A")).unwrap();
        assert_eq!(
            again["result"]["isError"], false,
            "墓碑已用掉,同键再来照常执行"
        );
    }

    #[test]
    fn modern_cancel_matches_client_name_and_ambiguity_cancels_nothing() {
        let c = modern_core();
        let fa = Arc::new(AtomicBool::new(false));
        let fb = Arc::new(AtomicBool::new(false));
        let ra = c.register_call(
            call_key(MODERN_NS, &json!(5)),
            Some("claude-code".into()),
            Arc::clone(&fa),
        );
        let rb = c.register_call(
            call_key(MODERN_NS, &json!(5)),
            Some("codex".into()),
            Arc::clone(&fb),
        );
        assert!(
            !c.cancel_call(&call_key(MODERN_NS, &json!(5)), None),
            "没给客户端名 + 两家撞 id = 歧义,谁也不取消"
        );
        assert!(!fa.load(Ordering::SeqCst) && !fb.load(Ordering::SeqCst));
        let note = json!({ "jsonrpc": "2.0", "method": "notifications/cancelled", "params": { "requestId": 5, "_meta": meta(json!({})) } });
        assert!(matches!(
            c.handle_modern(
                &note,
                None,
                &FakePage {
                    tools: vec![],
                    fail_with: None
                }
            ),
            ModernOutcome::Accepted
        ));
        assert!(fa.load(Ordering::SeqCst), "claude-code 的 5 号被取消");
        assert!(!fb.load(Ordering::SeqCst), "codex 的 5 号不受牵连");
        drop(ra);
        drop(rb);
        assert_eq!(c.inflight_call_count(), 0);
        let fs = Arc::new(AtomicBool::new(false));
        let _rs = c.register_call(call_key(MODERN_NS, &json!("5")), None, Arc::clone(&fs));
        c.cancel_call(&call_key(MODERN_NS, &json!(5)), None);
        assert!(!fs.load(Ordering::SeqCst), "\"5\" 与 5 不是同一个 id");
    }

    fn sse_post(port: u16, extra_headers: &str, body: &str) -> String {
        format!("POST /mcp HTTP/1.1\r\nHost: 127.0.0.1:{port}\r\nContent-Type: application/json\r\nAccept: application/json, text/event-stream\r\n{extra_headers}Content-Length: {}\r\n\r\n{body}", body.len())
    }

    #[test]
    fn legacy_progress_streams_monotonic_frames_then_result_and_connection_is_reusable() {
        let c = Arc::new(core());
        let token = c.token();
        let page: Arc<dyn PageDispatcher> = Arc::new(ctl_page(
            vec![1.0, 2.0, 2.0, 1.5, 3.0],
            Duration::from_millis(50),
        ));
        let handle = start_server(0, Arc::clone(&c), page, "9.9.9".into()).unwrap();
        let port = handle.port();
        let auth = format!("Authorization: Bearer {token}\r\n");
        let body = json!({ "jsonrpc": "2.0", "id": 7, "method": "tools/call", "params": { "name": "list_records", "arguments": {}, "_meta": { "progressToken": "pt-1" } } }).to_string();
        let mut stream = TcpStream::connect(("127.0.0.1", port)).unwrap();
        stream
            .set_read_timeout(Some(Duration::from_secs(5)))
            .unwrap();
        stream
            .write_all(sse_post(port, &auth, &body).as_bytes())
            .unwrap();
        let mut reader = BufReader::new(stream.try_clone().unwrap());
        let (st, headers, raw) = read_response(&mut reader);
        assert_eq!(st, 200);
        assert!(
            headers
                .iter()
                .any(|h| h.eq_ignore_ascii_case("content-type: text/event-stream")),
            "{headers:?}"
        );
        assert!(
            headers
                .iter()
                .any(|h| h.eq_ignore_ascii_case("transfer-encoding: chunked")),
            "分块收尾,不靠关连接:{headers:?}"
        );
        let msgs = sse_messages(&raw);
        let progress: Vec<f64> = msgs
            .iter()
            .filter(|m| m["method"] == "notifications/progress")
            .map(|m| {
                assert_eq!(m["params"]["progressToken"], "pt-1");
                m["params"]["progress"].as_f64().unwrap()
            })
            .collect();
        assert_eq!(progress, vec![1.0, 2.0, 3.0], "不增的进度帧丢弃");
        let last = msgs.last().unwrap();
        assert_eq!(last["id"], 7);
        assert_eq!(last["result"]["isError"], false);
        // 分块结束标记已到 ⇒ 同一条连接接着发下一个请求(keep-alive 复用,不留半开连接)
        let ping = r#"{"jsonrpc":"2.0","id":8,"method":"ping"}"#;
        stream.write_all(format!("POST /mcp HTTP/1.1\r\nHost: 127.0.0.1:{port}\r\nContent-Type: application/json\r\n{auth}Content-Length: {}\r\n\r\n{ping}", ping.len()).as_bytes()).unwrap();
        let (st2, _, body2) = read_response(&mut reader);
        assert_eq!(st2, 200);
        assert_eq!(serde_json::from_str::<Value>(&body2).unwrap()["id"], 8);
        // 判别力:不带进度令牌 ⇒ 照旧单体 JSON(旧客户端字节同今日)
        let plain = json!({ "jsonrpc": "2.0", "id": 9, "method": "tools/call", "params": { "name": "list_records", "arguments": {} } }).to_string();
        let (st3, hdrs3, body3) = http_full(port, &sse_post(port, &auth, &plain));
        assert_eq!(st3, 200);
        assert!(
            hdrs3.iter().any(|h| h
                .to_ascii_lowercase()
                .starts_with("content-type: application/json")),
            "{hdrs3:?}"
        );
        assert_eq!(serde_json::from_str::<Value>(&body3).unwrap()["id"], 9);
        handle.stop();
    }

    #[test]
    fn legacy_stream_disconnect_is_not_cancellation_but_modern_disconnect_is() {
        // 旧纪元:规范写明断开不算取消 ⇒ 工具照常跑完
        let c = Arc::new(core());
        let token = c.token();
        let legacy_page = Arc::new(ctl_page(vec![1.0], Duration::from_millis(700)));
        let lp: Arc<dyn PageDispatcher> = legacy_page.clone();
        let handle = start_server(0, Arc::clone(&c), lp, "9.9.9".into()).unwrap();
        let port = handle.port();
        let body = json!({ "jsonrpc": "2.0", "id": 11, "method": "tools/call", "params": { "name": "list_records", "arguments": {}, "_meta": { "progressToken": 1 } } }).to_string();
        {
            let mut s = TcpStream::connect(("127.0.0.1", port)).unwrap();
            s.write_all(
                sse_post(port, &format!("Authorization: Bearer {token}\r\n"), &body).as_bytes(),
            )
            .unwrap();
            let mut r = BufReader::new(s.try_clone().unwrap());
            let mut l = String::new();
            r.read_line(&mut l).unwrap();
            assert!(l.contains("200"), "{l}");
            s.shutdown(std::net::Shutdown::Both).ok();
        }
        let deadline = Instant::now() + Duration::from_secs(5);
        while legacy_page.done.load(Ordering::SeqCst) == 0 && Instant::now() < deadline {
            thread::sleep(Duration::from_millis(20));
        }
        assert_eq!(
            legacy_page.done.load(Ordering::SeqCst),
            1,
            "旧纪元断开后工具照常跑完"
        );
        assert!(!legacy_page.saw_cancel.load(Ordering::SeqCst));
        handle.stop();
        // 现代纪元:关掉响应流 = 取消 ⇒ 保活写失败 ⇒ 置位 ⇒ 页面中止(不跑满 8 s)
        let m = Arc::new(modern_core());
        let mtoken = m.token();
        let modern_page = Arc::new(ctl_page(vec![], Duration::from_secs(8)));
        let mp: Arc<dyn PageDispatcher> = modern_page.clone();
        let mh = start_server(0, Arc::clone(&m), mp, "9.9.9".into()).unwrap();
        let mport = mh.port();
        let mbody = mreq(
            21,
            "tools/call",
            json!({ "name": "list_records", "arguments": {} }),
        )
        .to_string();
        let t0 = Instant::now();
        {
            let mut s = TcpStream::connect(("127.0.0.1", mport)).unwrap();
            s.write_all(sse_post(mport, &format!("Authorization: Bearer {mtoken}\r\nMCP-Protocol-Version: 2026-07-28\r\nMcp-Method: tools/call\r\nMcp-Name: list_records\r\n"), &mbody).as_bytes()).unwrap();
            let mut r = BufReader::new(s.try_clone().unwrap());
            let mut l = String::new();
            r.read_line(&mut l).unwrap();
            assert!(l.contains("200"), "{l}");
            s.shutdown(std::net::Shutdown::Both).ok();
        }
        let deadline = Instant::now() + Duration::from_secs(6);
        while !modern_page.saw_cancel.load(Ordering::SeqCst) && Instant::now() < deadline {
            thread::sleep(Duration::from_millis(20));
        }
        assert!(
            modern_page.saw_cancel.load(Ordering::SeqCst),
            "现代纪元断开即取消"
        );
        assert!(t0.elapsed() < Duration::from_secs(6));
        assert_eq!(modern_page.done.load(Ordering::SeqCst), 0);
        mh.signal_stop();
    }

    #[test]
    fn modern_tools_call_answers_on_a_stream_with_identity_and_without_sse_accept_stays_json() {
        let (_c, handle, port, token) = modern_server();
        let body = mreq(
            31,
            "tools/call",
            json!({ "name": "list_records", "arguments": {} }),
        )
        .to_string();
        let (st, hdrs, raw) = http_full(port, &sse_post(port, &format!("Authorization: Bearer {token}\r\nMCP-Protocol-Version: 2026-07-28\r\nMcp-Method: tools/call\r\nMcp-Name: list_records\r\n"), &body));
        assert_eq!(st, 200);
        assert!(
            hdrs.iter()
                .any(|h| h.eq_ignore_ascii_case("content-type: text/event-stream")),
            "{hdrs:?}"
        );
        let msgs = sse_messages(&raw);
        assert_eq!(msgs.len(), 1, "无进度令牌 ⇒ 流里只有回包");
        assert_eq!(msgs[0]["id"], 31);
        assert_eq!(msgs[0]["result"]["resultType"], "complete");
        // 只收 JSON 的客户端 ⇒ 单体 JSON
        let only_json = format!("POST /mcp HTTP/1.1\r\nHost: 127.0.0.1:{port}\r\nContent-Type: application/json\r\nAccept: application/json\r\nAuthorization: Bearer {token}\r\nMCP-Protocol-Version: 2026-07-28\r\nMcp-Method: tools/call\r\nMcp-Name: list_records\r\nContent-Length: {}\r\n\r\n{body}", body.len());
        let (st2, hdrs2, body2) = http_full(port, &only_json);
        assert_eq!(st2, 200);
        assert!(
            hdrs2.iter().any(|h| h
                .to_ascii_lowercase()
                .starts_with("content-type: application/json")),
            "{hdrs2:?}"
        );
        assert_eq!(serde_json::from_str::<Value>(&body2).unwrap()["id"], 31);
        // 头体不一致仍在开流之前判(HTTP 400,不是流里的错误)
        let (st3, _, _) = http_full(port, &sse_post(port, &format!("Authorization: Bearer {token}\r\nMCP-Protocol-Version: 2026-07-28\r\nMcp-Method: tools/call\r\nMcp-Name: wrong\r\n"), &body));
        assert_eq!(st3, 400);
        handle.signal_stop();
    }

    // ───────────────────────── 本机 REST 接口 /api/v1:同一端口、同一道门、子开关缺省关 ─────────────────────────

    fn rest(
        port: u16,
        method: &str,
        path: &str,
        auth: &str,
        body: Option<&str>,
    ) -> (u16, Vec<String>, String) {
        let mut stream = TcpStream::connect(("127.0.0.1", port)).unwrap();
        let req = match body {
            Some(b) => format!("{} {} HTTP/1.1\r\nHost: 127.0.0.1:{}\r\n{}Content-Type: application/json\r\nContent-Length: {}\r\n\r\n{}", method, path, port, auth, b.len(), b),
            None => format!("{} {} HTTP/1.1\r\nHost: 127.0.0.1:{}\r\n{}\r\n", method, path, port, auth),
        };
        stream.write_all(req.as_bytes()).unwrap();
        stream.flush().unwrap();
        let mut reader = BufReader::new(stream);
        read_response(&mut reader)
    }

    #[test]
    fn rest_api_end_to_end_gate_switch_routes_and_shapes() {
        let c = Arc::new(core());
        let token = c.token();
        let page: Arc<dyn PageDispatcher> = Arc::new(FakePage {
            tools: fake_tools(),
            fail_with: None,
        });
        let handle = start_server(0, Arc::clone(&c), page, "9.9.9".into()).unwrap();
        let port = handle.port();
        let auth = format!("Authorization: Bearer {}\r\n", token);
        // 门在开关之前:无令牌 401(带 WWW-Authenticate)、外来 Origin 403,都不透露开关状态
        let (st, hs, _) = rest(port, "GET", "/api/v1/tools", "", None);
        assert_eq!(st, 401);
        assert!(hs.iter().any(|h| h
            .to_ascii_lowercase()
            .starts_with("www-authenticate: bearer")));
        let (st, _, _) = rest(
            port,
            "GET",
            "/api/v1/tools",
            &format!("{}Origin: https://evil.example\r\n", auth),
            None,
        );
        assert_eq!(st, 403);
        // 有令牌、开关缺省关 → 403 REST_DISABLED(说明去哪开)
        assert!(!c.rest_enabled());
        let (st, _, body) = rest(port, "GET", "/api/v1/tools", &auth, None);
        assert_eq!(st, 403);
        let v: Value = serde_json::from_str(&body).unwrap();
        assert_eq!(v["error"]["code"], "REST_DISABLED");
        // 开
        c.set_rest_enabled(true);
        let (st, _, body) = rest(port, "GET", "/api/v1", &auth, None);
        assert_eq!(st, 200);
        let v: Value = serde_json::from_str(&body).unwrap();
        assert_eq!(v["version"], "9.9.9");
        assert_eq!(v["docs"], "/api/v1/openapi.json");
        // 工具清单 = MCP tools/list 同一份(同样滤掉破坏级与坏名)
        let (st, _, body) = rest(port, "GET", "/api/v1/tools", &auth, None);
        assert_eq!(st, 200);
        let v: Value = serde_json::from_str(&body).unwrap();
        assert_eq!(v["ok"], true);
        let names: Vec<&str> = v["tools"]
            .as_array()
            .unwrap()
            .iter()
            .filter_map(|t| t["name"].as_str())
            .collect();
        assert_eq!(names, vec!["list_records", "create_chart_record"]);
        // 工具调用:请求体 = 参数;回 {ok, text, data}
        let (st, _, body) = rest(
            port,
            "POST",
            "/api/v1/tools/list_records",
            &auth,
            Some("{\"query\":\"张\"}"),
        );
        assert_eq!(st, 200);
        let v: Value = serde_json::from_str(&body).unwrap();
        assert_eq!(v["ok"], true);
        assert_eq!(v["data"]["echo"]["query"], "张");
        assert!(v["text"].as_str().unwrap().contains("list_records"));
        // 空请求体 = 空参数
        let (st, _, _) = rest(port, "POST", "/api/v1/tools/list_records", &auth, Some(""));
        assert_eq!(st, 200);
        // 坏 JSON / 非对象 → 400
        let (st, _, body) = rest(
            port,
            "POST",
            "/api/v1/tools/list_records",
            &auth,
            Some("{oops"),
        );
        assert_eq!(st, 400);
        assert!(body.contains("BAD_JSON"));
        let (st, _, _) = rest(
            port,
            "POST",
            "/api/v1/tools/list_records",
            &auth,
            Some("[1,2]"),
        );
        assert_eq!(st, 400);
        // GET 别名:查询串 = 参数(百分号解码)
        let (st, _, body) = rest(
            port,
            "GET",
            "/api/v1/records?query=%E5%BC%A0&limit=5",
            &auth,
            None,
        );
        assert_eq!(st, 200);
        let v: Value = serde_json::from_str(&body).unwrap();
        assert_eq!(v["data"]["echo"]["query"], "张");
        assert_eq!(v["data"]["echo"]["limit"], "5");
        // OpenAPI:每件工具一条 POST,带输入结构
        let (st, _, body) = rest(port, "GET", "/api/v1/openapi.json", &auth, None);
        assert_eq!(st, 200);
        let v: Value = serde_json::from_str(&body).unwrap();
        assert_eq!(v["openapi"], "3.1.0");
        assert!(v["paths"]["/tools/list_records"]["post"].is_object());
        assert!(v["paths"]["/tools/wipe_all"].is_null());
        // 资源 / 模版 / 读 / 提示
        let (st, _, body) = rest(port, "GET", "/api/v1/resources", &auth, None);
        assert_eq!(st, 200);
        assert!(body.contains("horosa://chart/local-1"));
        let (st, _, body) = rest(port, "GET", "/api/v1/resources/templates", &auth, None);
        assert_eq!(st, 200);
        assert!(body.contains("uriTemplate"));
        let (st, _, body) = rest(
            port,
            "GET",
            "/api/v1/resources/read?uri=horosa%3A%2F%2Fchart%2Flocal-1",
            &auth,
            None,
        );
        assert_eq!(st, 200);
        let v: Value = serde_json::from_str(&body).unwrap();
        assert_eq!(v["contents"][0]["text"], "snapshot");
        let (st, _, _) = rest(port, "GET", "/api/v1/resources/read", &auth, None);
        assert_eq!(st, 400);
        let (st, _, body) = rest(port, "GET", "/api/v1/prompts", &auth, None);
        assert_eq!(st, 200);
        assert!(body.contains("technique:bazi"));
        let (st, _, body) = rest(
            port,
            "POST",
            "/api/v1/prompts/technique:bazi",
            &auth,
            Some("{}"),
        );
        assert_eq!(st, 200);
        assert!(body.contains("\"messages\""));
        // 未知路径 404、方法不对 405(带 Allow)
        let (st, _, _) = rest(port, "GET", "/api/v1/nope", &auth, None);
        assert_eq!(st, 404);
        let (st, hs, _) = rest(port, "GET", "/api/v1/tools/list_records", &auth, None);
        assert_eq!(st, 405);
        assert!(hs.iter().any(|h| h.to_ascii_lowercase() == "allow: post"));
        // 关回去 → 立刻 403;/mcp 不受影响
        c.set_rest_enabled(false);
        let (st, _, _) = rest(port, "GET", "/api/v1/tools", &auth, None);
        assert_eq!(st, 403);
        let (st, _) = post(
            port,
            &auth,
            "{\"jsonrpc\":\"2.0\",\"id\":1,\"method\":\"ping\"}",
        );
        assert_eq!(st, 200);
        handle.signal_stop();
    }

    #[test]
    fn rest_api_tool_call_streams_progress_then_result() {
        let c = Arc::new(core());
        c.set_rest_enabled(true);
        let token = c.token();
        let page: Arc<dyn PageDispatcher> =
            Arc::new(ctl_page(vec![1.0, 2.0, 3.0], Duration::from_millis(60)));
        let handle = start_server(0, Arc::clone(&c), page, "9.9.9".into()).unwrap();
        let port = handle.port();
        let auth = format!("Authorization: Bearer {}\r\n", token);
        let (st, hs, body) = rest(
            port,
            "POST",
            "/api/v1/tools/list_records?stream=1",
            &auth,
            Some("{}"),
        );
        assert_eq!(st, 200);
        assert!(hs.iter().any(|h| h
            .to_ascii_lowercase()
            .starts_with("content-type: text/event-stream")));
        let events: Vec<(String, Value)> = body
            .split("\n\n")
            .filter_map(|ev| {
                let name = ev
                    .lines()
                    .find_map(|l| l.strip_prefix("event: "))?
                    .to_string();
                let data = ev.lines().find_map(|l| l.strip_prefix("data: "))?;
                Some((name, serde_json::from_str::<Value>(data).ok()?))
            })
            .collect();
        let progress: Vec<f64> = events
            .iter()
            .filter(|(n, _)| n == "progress")
            .filter_map(|(_, v)| v["progress"].as_f64())
            .collect();
        assert_eq!(progress, vec![1.0, 2.0, 3.0]);
        let (last_name, last) = events.last().unwrap();
        assert_eq!(last_name, "result");
        assert_eq!(last["ok"], true);
        assert_eq!(last["status"], 200);
        assert_eq!(last["text"], "done");
        handle.signal_stop();
    }
    // ───────────────────────── 终端命令行 --horosa-cli:经端点文件连本机服务(真 HTTP)─────────────────────────

    fn cli_endpoint_file(port: u16, token: &str, tag: &str) -> std::path::PathBuf {
        let p = std::env::temp_dir().join(format!(
            "horosa-cli-ep-{}-{}-{}.json",
            std::process::id(),
            port,
            tag
        ));
        std::fs::write(
            &p,
            json!({ "url": format!("http://127.0.0.1:{}/mcp", port), "token": token, "pid": std::process::id() }).to_string(),
        )
        .unwrap();
        p
    }

    fn cli_run(
        argv: &[&str],
        ep: &std::path::Path,
        flag: &AtomicBool,
        stdin: &str,
    ) -> (i32, String, String) {
        let mut out = Vec::new();
        let mut err = Vec::new();
        let mut input = stdin.as_bytes();
        let argv: Vec<String> = argv.iter().map(|s| s.to_string()).collect();
        let code = {
            let mut io = crate::horosa_cli::CliIo {
                out: &mut out,
                err: &mut err,
                stdin: &mut input,
                err_is_tty: false,
                interrupted: flag,
            };
            crate::horosa_cli::execute(&argv, Some(ep.to_path_buf()), &mut io)
        };
        (
            code,
            String::from_utf8_lossy(&out).to_string(),
            String::from_utf8_lossy(&err).to_string(),
        )
    }

    /// 客户端身份与无头协议层读同一份用例表(_meta.clientName → clientInfo.name → 会话名 → 传输层缺省)
    #[test]
    fn client_identity_cases_match_shared_table() {
        let table = include_str!(
            "../../../Horosa-Web/astrostudyui/src/utils/__tests__/fixtures/clientIdentityCases.tsv"
        );
        let mut n = 0;
        for line in table
            .lines()
            .filter(|l| !l.is_empty() && !l.starts_with('#'))
        {
            let cols: Vec<&str> = line.split('\t').collect();
            let meta: Value = serde_json::from_str(cols[0]).expect("meta 列是 JSON");
            let sess: Option<String> = serde_json::from_str(cols[1]).expect("session 列是 JSON");
            let trans: Option<String> = serde_json::from_str(cols[2]).expect("transport 列是 JSON");
            let want: Option<String> = serde_json::from_str(cols[3]).expect("expected 列是 JSON");
            assert_eq!(
                client_identity_of(Some(&meta), sess.as_deref(), trans.as_deref()),
                want,
                "{}",
                cols[4]
            );
            n += 1;
        }
        assert!(n >= 10, "用例表读到 {n} 行");
        assert_eq!(
            client_identity_of(None, None, Some("http")),
            Some("http".to_string())
        );
    }

    /// 旧纪元客户端只在 initialize 报 clientInfo:按会话记下,之后这个会话的调用投给页面的 clientName 就是它;
    /// 逐条自报的 _meta.clientName 仍优先;不带会话头 / 没报名 = 不补(页面取缺省)
    #[test]
    fn legacy_session_remembers_initialize_client_name() {
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
        let core = McpCore::new("t".to_string(), "9.9.9".to_string());
        let init = json!({ "jsonrpc": "2.0", "id": 1, "method": "initialize", "params": { "protocolVersion": "2025-11-25", "clientInfo": { "name": "claude-code", "version": "2" } } });
        assert_eq!(
            initialize_client_name(&init).as_deref(),
            Some("claude-code")
        );
        let sid = core.new_session_for(initialize_client_name(&init));
        let call = |meta: Value, session: Option<&str>| -> Value {
            let req = json!({ "jsonrpc": "2.0", "id": 2, "method": "tools/call", "params": { "name": "list_records", "arguments": {}, "_meta": meta } });
            let out = core.handle_rpc_with_session(&req, &Echo, session).unwrap();
            serde_json::from_str(out["result"]["content"][0]["text"].as_str().unwrap()).unwrap()
        };
        assert_eq!(
            call(json!({}), Some(&sid))["clientName"],
            json!("claude-code")
        );
        assert_eq!(
            call(json!({ "clientName": "cli" }), Some(&sid))["clientName"],
            json!("cli")
        );
        assert_eq!(call(json!({}), None)["clientName"], Value::Null);
        let anon = core.new_session_for(None);
        assert_eq!(call(json!({}), Some(&anon))["clientName"], Value::Null);
        assert_eq!(
            core.session_client(Some(&sid)).as_deref(),
            Some("claude-code")
        );
    }

    /// 幂等键口径与页面注册表、无头协议层读同一份用例表(按码点计、去首尾空白、超长报错)
    #[test]
    fn idempotency_key_cases_match_shared_table() {
        let table = include_str!(
            "../../../Horosa-Web/astrostudyui/src/utils/__tests__/fixtures/idempotencyKeyCases.tsv"
        );
        let mut n = 0;
        for line in table
            .lines()
            .filter(|l| !l.is_empty() && !l.starts_with('#'))
        {
            let cols: Vec<&str> = line.split('\t').collect();
            let raw: String = serde_json::from_str(cols[0]).expect("raw 列是 JSON 字符串");
            let got = idempotency_key_check(&json!({ "_meta": { "idempotencyKey": raw } }));
            match cols[1] {
                "none" => assert_eq!(got, Ok(None), "{}", cols[2]),
                "error" => assert!(got.is_err(), "{}", cols[2]),
                exp => {
                    let want: String = serde_json::from_str(exp).unwrap();
                    assert_eq!(got, Ok(Some(want)), "{}", cols[2]);
                }
            }
            n += 1;
        }
        assert!(n >= 10, "用例表读到 {n} 行");
        assert!(
            idempotency_key_check(&json!({ "_meta": { "idempotencyKey": 7 } })).is_err(),
            "非字符串 = 参数错"
        );
        assert_eq!(
            idempotency_key_check(&json!({ "_meta": { "idempotencyKey": null } })),
            Ok(None)
        );
    }

    /// 幂等键三入口都到得了页面(页面注册表据此回放 / 报冲突):MCP `_meta`(两种写法)、REST `Idempotency-Key` 头、
    /// 终端命令 `--idempotency-key`;空 / 超长不投;不带键时页面 `_meta` 里没有这个键
    #[test]
    fn idempotency_key_reaches_page_from_mcp_rest_and_cli() {
        let c = Arc::new(core());
        c.set_rest_enabled(true);
        let token = c.token();
        let page = ctl_page(vec![], Duration::from_millis(0));
        let seen = Arc::clone(&page.seen);
        let page: Arc<dyn PageDispatcher> = Arc::new(page);
        let handle = start_server(0, Arc::clone(&c), Arc::clone(&page), "9.9.9".into()).unwrap();
        let port = handle.port();
        let last_meta = || -> Value {
            let v = seen.lock().unwrap();
            v.iter()
                .rev()
                .find(|x| x["method"] == "tools/call")
                .map(|x| x["params"]["_meta"].clone())
                .unwrap_or(Value::Null)
        };
        let call = |meta: Value| {
            c.handle_rpc(&json!({ "jsonrpc": "2.0", "id": 1, "method": "tools/call", "params": { "name": "create_chart_record", "arguments": {}, "_meta": meta } }), page.as_ref());
        };
        call(json!({ "idempotencyKey": " k-mcp " }));
        assert_eq!(last_meta()["idempotencyKey"], "k-mcp");
        call(json!({ "io.horosa/idempotencyKey": "k-alias" }));
        assert_eq!(last_meta()["idempotencyKey"], "k-alias");
        call(json!({ "idempotencyKey": "   " }));
        assert!(last_meta().get("idempotencyKey").is_none(), "空键不投");
        let before = seen.lock().unwrap().len();
        let over = c.handle_rpc(&json!({ "jsonrpc": "2.0", "id": 2, "method": "tools/call", "params": { "name": "create_chart_record", "arguments": {}, "_meta": { "idempotencyKey": "x".repeat(IDEMPOTENCY_KEY_MAX + 1) } } }), page.as_ref());
        assert_eq!(
            over.expect("请求有回包")["error"]["code"],
            json!(ERR_INVALID_PARAMS),
            "超长键 = 参数错,不静默丢"
        );
        assert_eq!(seen.lock().unwrap().len(), before, "超长不投递");
        call(json!({ "idempotencyKey": "键".repeat(IDEMPOTENCY_KEY_MAX) }));
        assert_eq!(
            last_meta()["idempotencyKey"],
            "键".repeat(IDEMPOTENCY_KEY_MAX),
            "按码点计(与页面同口径)"
        );
        call(json!({}));
        assert!(last_meta().get("idempotencyKey").is_none());
        assert!(last_meta()["timeoutMs"].as_u64().is_some(), "预算照投");
        // REST:请求头 → 页面
        let auth = format!(
            "Authorization: Bearer {}\r\nIdempotency-Key: k-rest\r\n",
            token
        );
        let (st, _, _) = rest(
            port,
            "POST",
            "/api/v1/tools/create_chart_record",
            &auth,
            Some("{}"),
        );
        assert_eq!(st, 200);
        assert_eq!(last_meta()["idempotencyKey"], "k-rest");
        // REST:超长键 = 400 BAD_REQUEST(不静默丢)
        let auth_long = format!(
            "Authorization: Bearer {}\r\nIdempotency-Key: {}\r\n",
            token,
            "x".repeat(IDEMPOTENCY_KEY_MAX + 1) // HTTP 头只走 ASCII;按码点计的口径另由共用用例表锁
        );
        let (st, _, _) = rest(
            port,
            "POST",
            "/api/v1/tools/create_chart_record",
            &auth_long,
            Some("{}"),
        );
        assert_eq!(st, 400);
        // 终端命令:--idempotency-key → 页面(另一种写法 = 也认)
        let ep = cli_endpoint_file(port, &token, "idem");
        let flag = AtomicBool::new(false);
        let (code, _, err) = cli_run(
            &["call", "create_chart_record", "--idempotency-key", "k-cli"],
            &ep,
            &flag,
            "",
        );
        assert_eq!(code, 0, "{err}");
        assert_eq!(last_meta()["idempotencyKey"], "k-cli");
        let (code, _, err) = cli_run(
            &["call", "create_chart_record", "--idempotency-key=k-cli-2"],
            &ep,
            &flag,
            "",
        );
        assert_eq!(code, 0, "{err}");
        assert_eq!(last_meta()["idempotencyKey"], "k-cli-2");
        let (code, _, _) = cli_run(&["call", "create_chart_record"], &ep, &flag, "");
        assert_eq!(code, 0);
        assert!(
            last_meta().get("idempotencyKey").is_none(),
            "不带键不凭空造键"
        );
        let (code, _, _) = cli_run(
            &["call", "create_chart_record", "--idempotency-key", " "],
            &ep,
            &flag,
            "",
        );
        assert_eq!(code, crate::horosa_cli::EXIT_USAGE, "空键是用法错");
        let _ = std::fs::remove_file(&ep);
        handle.signal_stop();
    }

    #[test]
    fn cli_end_to_end_status_tools_call_read_prompts_and_bad_token() {
        let c = Arc::new(core());
        let token = c.token();
        let page: Arc<dyn PageDispatcher> = Arc::new(FakePage {
            tools: fake_tools(),
            fail_with: None,
        });
        let handle = start_server(0, Arc::clone(&c), page, "9.9.9".into()).unwrap();
        let ep = cli_endpoint_file(handle.port(), &token, "a");
        let flag = AtomicBool::new(false);
        let (code, out, _) = cli_run(&["status"], &ep, &flag, "");
        assert_eq!(code, 0);
        assert!(
            out.contains("运行中") && out.contains("版本 9.9.9") && out.contains("工具 2 件"),
            "{out}"
        );
        let (code, out, _) = cli_run(&["tools"], &ep, &flag, "");
        assert_eq!(code, 0);
        assert!(
            out.contains("list_records")
                && out.contains("只读")
                && out.contains("create_chart_record"),
            "{out}"
        );
        assert!(!out.contains("wipe_all"));
        let (code, out, _) = cli_run(&["describe", "list_records"], &ep, &flag, "");
        assert_eq!(code, 0);
        assert!(out.contains("参数结构"));
        assert_eq!(
            cli_run(&["describe", "nope"], &ep, &flag, "").0,
            crate::horosa_cli::EXIT_USAGE
        );
        // 调用:k=v 与 JSON;--json 回整份结果(structuredContent 原样)
        let (code, out, _) = cli_run(
            &["call", "list_records", "query=张", "limit:=5", "--json"],
            &ep,
            &flag,
            "",
        );
        assert_eq!(code, 0);
        let v: Value = serde_json::from_str(&out).unwrap();
        assert_eq!(
            v["structuredContent"]["echo"],
            json!({ "query": "张", "limit": 5 })
        );
        // 简写 + 标准输入打底、命令行覆盖
        let (code, out, _) = cli_run(&["records", "李", "--json"], &ep, &flag, "");
        assert_eq!(code, 0);
        assert_eq!(
            serde_json::from_str::<Value>(&out).unwrap()["structuredContent"]["echo"]["query"],
            "李"
        );
        let (code, out, _) = cli_run(
            &["call", "list_records", "-", "kind=chart", "--json"],
            &ep,
            &flag,
            "{\"query\":\"王\",\"kind\":\"all\"}",
        );
        assert_eq!(code, 0);
        assert_eq!(
            serde_json::from_str::<Value>(&out).unwrap()["structuredContent"]["echo"],
            json!({ "query": "王", "kind": "chart" })
        );
        // 人读:正文 = text 段
        let (code, out, _) = cli_run(&["call", "list_records"], &ep, &flag, "");
        assert_eq!(code, 0);
        assert!(out.contains("called"), "{out}");
        // 资源 / 读 / 提示
        let (code, out, _) = cli_run(&["resources"], &ep, &flag, "");
        assert_eq!(code, 0);
        assert!(out.contains("horosa://chart/local-1  张三"), "{out}");
        let (code, out, _) = cli_run(&["read", "horosa://chart/local-1"], &ep, &flag, "");
        assert_eq!((code, out.as_str()), (0, "snapshot\n"));
        let (code, out, _) = cli_run(&["templates"], &ep, &flag, "");
        assert_eq!(code, 0);
        assert!(out.contains("horosa://chart/{cid}"));
        let (code, out, _) = cli_run(&["prompts"], &ep, &flag, "");
        assert_eq!(code, 0);
        assert!(out.contains("technique:bazi"));
        let (code, out, _) = cli_run(&["prompt", "technique:bazi", "cid=local-1"], &ep, &flag, "");
        assert_eq!(code, 0);
        assert!(out.contains("[user]"));
        // 令牌不对 → 4;服务停了 → 3
        let bad = cli_endpoint_file(handle.port(), "tok_WRONGWRONGWRONGWRONG0000000000", "bad");
        let (code, _, err) = cli_run(&["tools"], &bad, &flag, "");
        assert_eq!(code, crate::horosa_cli::EXIT_AUTH, "{err}");
        assert!(err.contains("令牌不对"));
        handle.signal_stop();
        thread::sleep(Duration::from_millis(300));
        let (code, _, err) = cli_run(&["status"], &ep, &flag, "");
        assert_eq!(code, crate::horosa_cli::EXIT_NOT_RUNNING, "{err}");
        for p in [ep, bad] {
            let _ = std::fs::remove_file(p);
        }
    }

    #[test]
    fn cli_progress_lines_and_ctrl_c_cancels_the_call_in_the_page() {
        let c = Arc::new(core());
        let token = c.token();
        // 进度:--progress 打到标准错误,正文照常
        let page = Arc::new(ctl_page(vec![1.0, 2.0, 3.0], Duration::from_millis(60)));
        let dp: Arc<dyn PageDispatcher> = page.clone();
        let handle = start_server(0, Arc::clone(&c), dp, "9.9.9".into()).unwrap();
        let ep = cli_endpoint_file(handle.port(), &token, "p");
        let flag = AtomicBool::new(false);
        let (code, out, err) = cli_run(&["call", "list_records", "--progress"], &ep, &flag, "");
        assert_eq!(code, 0, "{err}");
        assert_eq!(out, "done\n");
        assert!(
            err.contains("[1/3] 第 1 步") && err.contains("[3/3] 第 3 步"),
            "{err}"
        );
        // --json 时不打进度(机器读的输出保持干净)
        let (_, _, err) = cli_run(
            &["call", "list_records", "--progress", "--json"],
            &ep,
            &flag,
            "",
        );
        assert!(!err.contains("第 1 步"), "{err}");
        handle.signal_stop();
        // Ctrl-C:长调用跑着时置中断位 → 发取消通知 → 页面看到取消、CLI 回 130
        let page = Arc::new(ctl_page(vec![], Duration::from_secs(5)));
        let dp: Arc<dyn PageDispatcher> = page.clone();
        let handle = start_server(0, Arc::clone(&c), dp, "9.9.9".into()).unwrap();
        let ep2 = cli_endpoint_file(handle.port(), &token, "c");
        let flag = Arc::new(AtomicBool::new(false));
        let f2 = Arc::clone(&flag);
        thread::spawn(move || {
            thread::sleep(Duration::from_millis(400));
            f2.store(true, Ordering::SeqCst);
        });
        let t0 = Instant::now();
        let (code, _, err) = cli_run(&["call", "list_records"], &ep2, &flag, "");
        assert_eq!(code, crate::horosa_cli::EXIT_INTERRUPTED, "{err}");
        assert!(err.contains("已取消"));
        let deadline = Instant::now() + Duration::from_secs(3);
        while !page.saw_cancel.load(Ordering::SeqCst) && Instant::now() < deadline {
            thread::sleep(Duration::from_millis(20));
        }
        assert!(page.saw_cancel.load(Ordering::SeqCst), "页面应收到取消");
        assert!(t0.elapsed() < Duration::from_secs(4), "取消后不等满 5 s");
        handle.signal_stop();
        for p in [ep, ep2] {
            let _ = std::fs::remove_file(p);
        }
    }
    // ───────────────────────── 真页面联调宿主(手动跑,缺省忽略)─────────────────────────
    // 驱动脚本 Horosa_Desktop_Installer/scripts/verify_desktop_api_e2e.sh:页面侧 = 无头运行时当「页面」
    // (Horosa-Web/astrostudyui/headless/pagehost.js,HTTP 包一层,只认本机回环的 POST);这里起真本机服务(REST 开)
    // 接上它,写端点文件,等 STOP 文件出现再停。
    // 投递 / 进度 / 结果 / 取消四条路与 PageBridge 同形:POST /dispatch 逐行收进度与结果,取消位置位即 POST /cancel。

    struct HttpPage {
        base: String,
        client: reqwest::blocking::Client,
        seq: AtomicU64,
    }

    impl PageDispatcher for HttpPage {
        fn dispatch(
            &self,
            method: &str,
            params: Value,
            timeout: Duration,
        ) -> std::result::Result<Value, McpError> {
            self.dispatch_ctl(method, params, timeout, &CallControl::none())
        }
        fn dispatch_ctl(
            &self,
            method: &str,
            params: Value,
            timeout: Duration,
            ctl: &CallControl,
        ) -> std::result::Result<Value, McpError> {
            let id = self.seq.fetch_add(1, Ordering::SeqCst);
            let (tx, rx) = mpsc::channel::<Value>();
            let client = self.client.clone();
            let url = format!("{}/dispatch", self.base);
            let body = json!({ "id": id, "method": method, "params": params }).to_string();
            thread::spawn(move || {
                let Ok(resp) = client.post(url).body(body).send() else {
                    let _ = tx.send(json!({ "done": true, "ok": false, "error": { "code": ERR_NOT_READY, "message": "page host unreachable" } }));
                    return;
                };
                let reader = std::io::BufReader::new(resp);
                for line in std::io::BufRead::lines(reader) {
                    let Ok(l) = line else { break };
                    if let Ok(v) = serde_json::from_str::<Value>(&l) {
                        let done = v.get("done").is_some();
                        let _ = tx.send(v);
                        if done {
                            break;
                        }
                    }
                }
            });
            let deadline = Instant::now() + timeout;
            loop {
                if ctl.is_cancelled() {
                    let _ = self
                        .client
                        .post(format!("{}/cancel", self.base))
                        .body(json!({ "id": id }).to_string())
                        .send();
                    return Err(cancelled_error());
                }
                match rx.recv_timeout(Duration::from_millis(250)) {
                    Ok(v) => {
                        if let Some(p) = v.get("progress") {
                            ctl.progress(p);
                            continue;
                        }
                        if v.get("ok").and_then(|b| b.as_bool()) == Some(true) {
                            return Ok(v.get("result").cloned().unwrap_or(Value::Null));
                        }
                        let e = v.get("error").cloned().unwrap_or(Value::Null);
                        let mut err = McpError::new(
                            e.get("code")
                                .and_then(|c| c.as_i64())
                                .unwrap_or(ERR_INTERNAL),
                            e.get("message")
                                .and_then(|m| m.as_str())
                                .unwrap_or("tool failed")
                                .to_string(),
                        );
                        if let Some(d) = e.get("data") {
                            err = err.with_data(d.clone());
                        }
                        return Err(err);
                    }
                    Err(mpsc::RecvTimeoutError::Timeout) => ctl.tick(),
                    Err(mpsc::RecvTimeoutError::Disconnected) => {
                        return Err(McpError::new(ERR_INTERNAL, "page host closed"))
                    }
                }
                if Instant::now() >= deadline {
                    return Err(McpError::new(ERR_TIMEOUT, "e2e page timeout"));
                }
            }
        }
    }

    #[test]
    #[ignore]
    fn e2e_real_page_host() {
        let page = std::env::var("HOROSA_E2E_PAGE_URL").expect("HOROSA_E2E_PAGE_URL");
        let endpoint = std::env::var("HOROSA_E2E_ENDPOINT").expect("HOROSA_E2E_ENDPOINT");
        let stop = std::env::var("HOROSA_E2E_STOP").expect("HOROSA_E2E_STOP");
        let rest_on = std::env::var("HOROSA_E2E_REST")
            .map(|v| v != "0")
            .unwrap_or(true);
        let nanos = std::time::SystemTime::now()
            .duration_since(std::time::UNIX_EPOCH)
            .map(|d| d.as_nanos())
            .unwrap_or(0);
        let token = format!("tok_e2e_{:x}_{:x}", std::process::id(), nanos);
        let c = Arc::new(McpCore::new(token.clone(), "e2e".into()));
        c.set_rest_enabled(rest_on);
        let dp: Arc<dyn PageDispatcher> = Arc::new(HttpPage {
            base: page,
            client: reqwest::blocking::Client::builder()
                .no_proxy()
                .build()
                .unwrap(),
            seq: AtomicU64::new(1),
        });
        let handle = start_server(0, Arc::clone(&c), dp, "e2e".into()).unwrap();
        let url = format!("http://127.0.0.1:{}/mcp", handle.port());
        std::fs::write(
            &endpoint,
            json!({ "url": url, "token": token, "pid": std::process::id() }).to_string(),
        )
        .unwrap();
        eprintln!("e2e page host shell listening {}", url);
        let deadline = Instant::now() + Duration::from_secs(25 * 60);
        while !std::path::Path::new(&stop).exists() && Instant::now() < deadline {
            thread::sleep(Duration::from_millis(300));
        }
        handle.signal_stop();
        let _ = std::fs::remove_file(&endpoint);
    }

    // ───────────────────── 本机 HTTP 服务的连接级加固(请求体收尾 / 头上限 / 停服 / 孤儿服务)─────────────────────

    fn raw_conn(port: u16) -> TcpStream {
        let s = TcpStream::connect(("127.0.0.1", port)).unwrap();
        s.set_read_timeout(Some(Duration::from_secs(5))).unwrap();
        s
    }

    /// 读完一个回应之后,服务端应在 `within` 内关掉连接(读到 EOF / 连接被重置),而不是让客户端读超时
    fn closed_by_server(reader: &mut BufReader<TcpStream>, within: Duration) -> bool {
        reader.get_ref().set_read_timeout(Some(within)).unwrap();
        let mut rest = Vec::new();
        match reader.read_to_end(&mut rest) {
            Ok(_) => true,
            Err(e) => e.kind() == std::io::ErrorKind::ConnectionReset,
        }
    }

    fn plain_server() -> (Arc<McpCore>, McpServerHandle, u16, String) {
        let c = Arc::new(core());
        let token = c.token();
        let page: Arc<dyn PageDispatcher> = Arc::new(FakePage {
            tools: fake_tools(),
            fail_with: None,
        });
        let handle = start_server(0, Arc::clone(&c), page, "9.9.9".into()).unwrap();
        let port = handle.port();
        (c, handle, port, token)
    }

    /// 🔴 不带令牌的请求声明 Content-Length = u64::MAX:旧实现在回应后丢弃请求时按声明长度一次性申请缓冲
    /// (capacity overflow → 发布版 panic = abort,整个 App 退出)。条数多于 worker 数:一条都不许拖垮服务,
    /// 每条回应后连接必须关闭(剩余字节不得被当成下一条请求解析),之后正常请求照常应答。
    #[test]
    fn huge_content_length_without_token_never_crashes_and_server_keeps_serving() {
        let (_c, handle, port, token) = plain_server();
        let targets = [
            "GET /healthz",
            "POST /mcp",
            "GET /nope",
            "POST /api/v1/tools/list_records",
        ];
        for i in 0..(WORKERS + 4) {
            let line = targets[i % targets.len()];
            let mut s = raw_conn(port);
            s.write_all(
                format!(
                    "{} HTTP/1.1\r\nHost: 127.0.0.1:{}\r\nContent-Length: 18446744073709551615\r\n\r\n",
                    line, port
                )
                .as_bytes(),
            )
            .unwrap();
            let mut r = BufReader::new(s);
            let (st, _, _) = read_response(&mut r);
            assert!(st == 200 || st == 401 || st == 404, "{} → {}", line, st);
            assert!(
                closed_by_server(&mut r, Duration::from_secs(3)),
                "{}:声明长度远超上限的连接回应后必须关闭",
                line
            );
        }
        let (st, body) = post(
            port,
            &format!("Authorization: Bearer {}\r\n", token),
            r#"{"jsonrpc":"2.0","id":1,"method":"ping"}"#,
        );
        assert_eq!(st, 200, "{}", body);
        assert!(handle.stop(), "worker 全部按时退出");
    }

    /// 🔴 声明 Content-Length 2000 却一个字节体都不发(连接也不关):旧实现丢弃请求时在 worker 上阻塞读剩余字节、
    /// 没有超时 —— 8 条连接就卡死全部 worker,停服也等不到。现在丢弃请求零阻塞,剩余字节交给该连接自己的线程。
    #[test]
    fn declared_body_never_sent_does_not_pin_workers() {
        let (_c, handle, port, token) = plain_server();
        let mut held = Vec::new();
        for _ in 0..(WORKERS + 4) {
            let mut s = raw_conn(port);
            s.write_all(
                format!(
                    "POST /mcp HTTP/1.1\r\nHost: 127.0.0.1:{}\r\nContent-Type: application/json\r\nContent-Length: 2000\r\n\r\n",
                    port
                )
                .as_bytes(),
            )
            .unwrap();
            let mut r = BufReader::new(s);
            let (st, _, _) = read_response(&mut r);
            assert_eq!(st, 401, "不带令牌:门先拒,不读体");
            held.push(r); // 不关、不发体
        }
        let t0 = Instant::now();
        let (st, body) = post(
            port,
            &format!("Authorization: Bearer {}\r\n", token),
            r#"{"jsonrpc":"2.0","id":2,"method":"ping"}"#,
        );
        assert_eq!(st, 200, "{}", body);
        let (st, _) = http(
            port,
            &format!("GET /healthz HTTP/1.1\r\nHost: 127.0.0.1:{}\r\n\r\n", port),
        );
        assert_eq!(st, 200);
        assert!(
            t0.elapsed() < Duration::from_secs(2),
            "worker 不得被挂起的连接占住,实耗 {:?}",
            t0.elapsed()
        );
        let t1 = Instant::now();
        assert!(handle.stop(), "worker 没被卡住,停服按时收口");
        assert!(t1.elapsed() < Duration::from_secs(2));
        drop(held);
    }

    /// 🔴 请求行 + 头不设上限:一条不带换行的超长头会被无限攒进内存。现在超过 64 KiB 回 431 并关连接,服务照常。
    #[test]
    fn oversized_request_head_gets_431_and_connection_closes() {
        let (_c, handle, port, _token) = plain_server();
        let mut head = format!(
            "GET /healthz HTTP/1.1\r\nHost: 127.0.0.1:{}\r\nX-Pad: ",
            port
        )
        .into_bytes();
        // 恰好比上限(64 KiB)多一个字节、且不带结尾换行:服务端把发来的字节全读掉才判超限,关连接时不留未读数据
        head.resize(64 * 1024 + 1, b'a');
        let mut s = raw_conn(port);
        s.write_all(&head).unwrap();
        let mut r = BufReader::new(s);
        let (st, _, _) = read_response(&mut r);
        assert_eq!(st, 431);
        assert!(closed_by_server(&mut r, Duration::from_secs(3)));
        let (st, _) = http(
            port,
            &format!("GET /healthz HTTP/1.1\r\nHost: 127.0.0.1:{}\r\n\r\n", port),
        );
        assert_eq!(st, 200);
        assert!(handle.stop());
    }

    /// 🔴 停服后旧保活连接挂死:请求进了没人收的队列,客户端永远等不到回应;旧式 GET 事件流也永远不结束。
    /// 现在停服时空闲的保活连接当场被关掉(客户端马上看到连接结束,不会挂住,也不会再拿到「服务已停」的 503),
    /// 事件流随之结束。
    #[test]
    fn after_stop_old_keepalive_connection_is_closed_and_event_stream_ends() {
        let (_c, handle, port, token) = plain_server();
        let ping = r#"{"jsonrpc":"2.0","id":1,"method":"ping"}"#;
        let req = format!(
            "POST /mcp HTTP/1.1\r\nHost: 127.0.0.1:{}\r\nContent-Type: application/json\r\nAuthorization: Bearer {}\r\nContent-Length: {}\r\n\r\n{}",
            port,
            token,
            ping.len(),
            ping
        );
        let mut s = raw_conn(port);
        s.write_all(req.as_bytes()).unwrap();
        let mut r = BufReader::new(s.try_clone().unwrap());
        assert_eq!(read_response(&mut r).0, 200);
        // 旧式 GET 事件流(升级出去的裸流,没有长度也没有分块)
        let mut ev = raw_conn(port);
        ev.write_all(
            format!(
                "GET /mcp HTTP/1.1\r\nHost: 127.0.0.1:{}\r\nAuthorization: Bearer {}\r\nAccept: text/event-stream\r\n\r\n",
                port, token
            )
            .as_bytes(),
        )
        .unwrap();
        let mut er = BufReader::new(ev);
        let mut status = String::new();
        er.read_line(&mut status).unwrap();
        assert!(status.contains(" 200 "), "{}", status);
        loop {
            let mut line = String::new();
            er.read_line(&mut line).unwrap();
            if line == "\r\n" {
                break;
            }
        }
        assert!(handle.stop(), "worker 全部按时退出");
        let t0 = Instant::now();
        // 连接可能已经关了:写失败不算错,要的是客户端立刻看到连接结束
        let _ = s.write_all(req.as_bytes());
        r.get_ref()
            .set_read_timeout(Some(Duration::from_secs(3)))
            .unwrap();
        let mut rest = Vec::new();
        let ended = match r.read_to_end(&mut rest) {
            Ok(_) => true,
            Err(e) => e.kind() == std::io::ErrorKind::ConnectionReset,
        };
        assert!(ended, "停服后旧连接要立刻结束(不许挂住)");
        assert!(t0.elapsed() < Duration::from_secs(3));
        let text = String::from_utf8_lossy(&rest);
        assert!(
            !text.contains(" 503 "),
            "空闲保活连接应当被关掉,而不是回「服务已停」的 503: {text}"
        );
        assert!(
            closed_by_server(&mut er, Duration::from_secs(3)),
            "停服后事件流必须结束(服务端关连接)"
        );
    }

    /// 🔴 启动半途出错提前返回会把服务句柄丢掉:旧实现句柄没有 Drop,worker 永远在跑、端口永远占着。
    #[test]
    fn dropping_the_handle_without_stop_still_stops_the_server() {
        let (_c, handle, port, _token) = plain_server();
        drop(handle);
        let deadline = Instant::now() + Duration::from_secs(4);
        let mut free = false;
        while Instant::now() < deadline {
            if std::net::TcpListener::bind(("127.0.0.1", port)).is_ok() {
                free = true;
                break;
            }
            thread::sleep(Duration::from_millis(50));
        }
        assert!(free, "句柄丢弃后端口 {} 必须释放", port);
    }

    #[test]
    fn healthz_answers_only_loopback_host_and_origin() {
        let (_c, handle, port, _token) = plain_server();
        let (st, body) = http(
            port,
            &format!("GET /healthz HTTP/1.1\r\nHost: 127.0.0.1:{}\r\n\r\n", port),
        );
        assert_eq!(st, 200);
        let v: Value = serde_json::from_str(&body).unwrap();
        assert_eq!(v["pid"], json!(std::process::id()));
        assert_eq!(v["app"], "horosa");
        let (st, body) = http(port, "GET /healthz HTTP/1.1\r\nHost: evil.example\r\n\r\n");
        assert_eq!(st, 403);
        assert!(!body.contains("pid"));
        let (st, _) = http(
            port,
            &format!(
                "GET /healthz HTTP/1.1\r\nHost: 127.0.0.1:{}\r\nOrigin: http://evil.example\r\n\r\n",
                port
            ),
        );
        assert_eq!(st, 403);
        assert!(handle.stop());
    }

    /// 🔴 旧式 GET 流的名额按整张订阅表算:先开满新式长流,旧式 GET 一条都开不了。
    /// 现在两类分开计数,订阅前先清掉接收端已丢弃的条目。
    #[test]
    fn listen_streams_opened_first_do_not_eat_legacy_get_slots() {
        let c = modern_core();
        let mut listens = Vec::new();
        for i in 0..MAX_LISTEN_STREAMS {
            listens.push(
                c.listen_subscribe(json!(i), ListenFilter::default())
                    .expect("listen slot"),
            );
        }
        let mut legacy = Vec::new();
        for _ in 0..MAX_SSE_CLIENTS {
            legacy.push(c.sse_subscribe().expect("新式长流不得占旧式 GET 的名额"));
        }
        assert!(c.sse_subscribe().is_none(), "旧式自身的上限照旧");
        assert!(c
            .listen_subscribe(json!(99), ListenFilter::default())
            .is_none());
        // 接收端丢弃(流结束)⇒ 下次订阅前即被清掉,名额回来(不必等下一次广播)
        legacy.pop();
        assert!(c.sse_subscribe().is_some(), "断开的旧式流应先被清掉");
        listens.pop();
        assert!(c
            .listen_subscribe(json!(100), ListenFilter::default())
            .is_some());
        assert_eq!(c.listen_count(), MAX_LISTEN_STREAMS);
    }

    fn scratch_dir(tag: &str) -> PathBuf {
        let dir = std::env::temp_dir().join(format!(
            "horosa-private-file-{}-{}",
            std::process::id(),
            tag
        ));
        let _ = fs::remove_dir_all(&dir);
        fs::create_dir_all(&dir).unwrap();
        dir
    }

    /// 🔴 旧实现固定用 `<名>.tmp` 做临时文件、`File::create` 会跟随符号链接:目录里预先放一个同名链接就能把
    /// 令牌写到别处。现在随机临时名 + 独占创建 + 不跟随链接 + 0600,目标若是链接则被换成普通文件(链接指向的文件不动)。
    #[cfg(unix)]
    #[test]
    fn write_private_file_never_follows_symlinks_and_is_0600() {
        use std::os::unix::fs::PermissionsExt;
        let dir = scratch_dir("w");
        let victim = dir.join("victim.txt");
        let victim2 = dir.join("victim2.txt");
        fs::write(&victim, "keep").unwrap();
        fs::write(&victim2, "keep2").unwrap();
        let target = dir.join("mcp-token");
        std::os::unix::fs::symlink(&victim, &target).unwrap();
        std::os::unix::fs::symlink(&victim2, target.with_extension("tmp")).unwrap();
        write_private_file(&target, b"secret").unwrap();
        let meta = fs::symlink_metadata(&target).unwrap();
        assert!(meta.file_type().is_file(), "目标应被换成普通文件");
        assert_eq!(meta.permissions().mode() & 0o777, 0o600);
        assert_eq!(fs::read_to_string(&target).unwrap(), "secret");
        assert_eq!(fs::read_to_string(&victim).unwrap(), "keep");
        assert_eq!(fs::read_to_string(&victim2).unwrap(), "keep2");
        let leftovers: Vec<String> = fs::read_dir(&dir)
            .unwrap()
            .filter_map(|e| e.ok())
            .map(|e| e.file_name().to_string_lossy().to_string())
            .filter(|n| n.starts_with(".mcp-token."))
            .collect();
        assert!(leftovers.is_empty(), "临时文件不得残留:{:?}", leftovers);
        // 覆盖写仍是原子替换、权限不变
        write_private_file(&target, b"secret2").unwrap();
        assert_eq!(fs::read_to_string(&target).unwrap(), "secret2");
        assert_eq!(
            fs::metadata(&target).unwrap().permissions().mode() & 0o777,
            0o600
        );
        let _ = fs::remove_dir_all(&dir);
    }

    /// 🔴 已有令牌文件权限被放宽(如 0644)时旧实现照读不误;现在读到即纠正为 0600(令牌不变)。
    /// 令牌文件是符号链接 ⇒ 不采信,重新生成并写成普通文件。
    #[cfg(unix)]
    #[test]
    fn existing_token_file_permissions_are_tightened_on_load() {
        use std::os::unix::fs::PermissionsExt;
        let dir = scratch_dir("t");
        let path = dir.join(MCP_TOKEN_FILE);
        let tok = "tok_0123456789abcdefghijklmnopqrstuvwxyz";
        fs::write(&path, tok).unwrap();
        fs::set_permissions(&path, fs::Permissions::from_mode(0o644)).unwrap();
        assert_eq!(load_or_create_token_at(&path).unwrap(), tok);
        assert_eq!(
            fs::metadata(&path).unwrap().permissions().mode() & 0o777,
            0o600
        );
        let elsewhere = dir.join("elsewhere");
        fs::write(&elsewhere, "tok_ELSEWHEREELSEWHEREELSEWHEREELSEWHERE").unwrap();
        fs::remove_file(&path).unwrap();
        std::os::unix::fs::symlink(&elsewhere, &path).unwrap();
        let fresh = load_or_create_token_at(&path).unwrap();
        assert_ne!(fresh, "tok_ELSEWHEREELSEWHEREELSEWHEREELSEWHERE");
        assert!(fs::symlink_metadata(&path).unwrap().file_type().is_file());
        assert_eq!(
            fs::read_to_string(&elsewhere).unwrap(),
            "tok_ELSEWHEREELSEWHEREELSEWHEREELSEWHERE"
        );
        let _ = fs::remove_dir_all(&dir);
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
        // 函数头多了一行「生效中的每分钟上限」计算,窗口从 1200 放到 1800(仍只覆盖 status_json 本体)
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
