//! [批三④] 本机 MCP 的 stdio 代理(给 Claude Desktop 这类只会 stdio 的客户端):
//! `Horosa --horosa-mcp-stdio <endpoint-file>`——读端点文件取 url+token → 循环读 stdin 一行 JSON-RPC(≤ 1MiB)
//! → POST /mcp(Bearer,回环)→ 把回体压成一行写 stdout。应用未运行(端点文件缺失 / 连接拒绝)→ 对每个带 id 的
//! 请求回 -32001,通知(无 id)静默丢;stdin EOF 即退。零 UI、零窗口、零日志(令牌永不落盘落屏)。
//! **本模块永不执行工具,只搬运** JSON-RPC;会话 id(Mcp-Session-Id)由服务端发、本代理原样回带。
//! [2026-07-28 双纪元] stdio 没有头层:带现代 `_meta.protocolVersion` 的行(或 `server/discover` 探测)按体派生三头
//! (MCP-Protocol-Version / Mcp-Method / Mcp-Name 哨兵编码)再转发、不带会话头;旧行逐字同今日。`subscriptions/listen`
//! 长流在串行代理里会卡死后续行 ⇒ 本地回 -32601(不转发);现代 400/404 的 JSON 错误原样透传。
use std::io::{BufRead, Write};
use std::path::Path;
use std::time::Duration;

use serde_json::{json, Value};

pub const STDIO_LINE_MAX: usize = 1024 * 1024;
pub const HTTP_TIMEOUT_SECS: u64 = 120;
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
    let loopback = url.starts_with("http://127.0.0.1:")
        || url.starts_with("http://localhost:")
        || url.starts_with("http://[::1]:");
    if !loopback {
        return Err("endpoint url must be a loopback http address".to_string());
    }
    if token.len() < 16 {
        return Err("endpoint token missing".to_string());
    }
    Ok(Endpoint { url, token, pid })
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

pub struct Proxy<'a> {
    pub client: &'a reqwest::blocking::Client,
    pub ep: &'a Endpoint,
    pub session: Option<String>,
}

impl<'a> Proxy<'a> {
    /// 转发一条;Ok((status, body));连接失败 → Err(不含令牌、不含地址)。
    /// `modern` 给定 ⇒ 注现代三头、不带会话头(无状态);None ⇒ 旧头与会话头逐字同今日。
    pub fn forward(
        &mut self,
        body: &[u8],
        modern: Option<&ModernLineHeaders>,
    ) -> Result<(u16, String), String> {
        let mut req = self
            .client
            .post(&self.ep.url)
            .header("Authorization", format!("Bearer {}", self.ep.token))
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
                req = req
                    .header("Accept", "application/json")
                    .header("MCP-Protocol-Version", "2025-06-18");
                if let Some(s) = &self.session {
                    req = req.header("Mcp-Session-Id", s.clone());
                }
            }
        }
        let resp = req
            .body(body.to_vec())
            .send()
            .map_err(|e| format!("{}", e.without_url()))?;
        if let Some(h) = resp
            .headers()
            .get("mcp-session-id")
            .and_then(|h| h.to_str().ok())
        {
            if !h.trim().is_empty() {
                self.session = Some(h.trim().to_string());
            }
        }
        let status = resp.status().as_u16();
        let text = resp.text().map_err(|e| format!("{}", e.without_url()))?;
        Ok((status, text))
    }
}

/// 一行进、一行出;回 (处理的请求数, 出错数)。通知不出行;超长/非 JSON/batch 本地拒;转发失败回 -32001。
pub fn serve<R: BufRead, W: Write>(
    r: &mut R,
    w: &mut W,
    client: &reqwest::blocking::Client,
    ep: Option<&Endpoint>,
) -> (u64, u64) {
    let mut handled: u64 = 0;
    let mut errors: u64 = 0;
    let mut proxy = ep.map(|e| Proxy {
        client,
        ep: e,
        session: None,
    });
    let mut emit = |w: &mut W, v: &Value| {
        let _ = writeln!(w, "{}", v);
        let _ = w.flush();
    };
    loop {
        let line = match read_line_bounded(r, STDIO_LINE_MAX) {
            Ok(None) => break,
            Ok(Some(l)) => l,
            Err(e) if e.kind() == std::io::ErrorKind::InvalidData => {
                errors += 1;
                emit(
                    w,
                    &error_response(None, ERR_INVALID, "request line too large (limit 1MiB)"),
                );
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
                errors += 1;
                emit(w, &error_response(None, ERR_PARSE, "parse error"));
                continue;
            }
        };
        if parsed.is_array() {
            errors += 1;
            emit(
                w,
                &error_response(None, ERR_INVALID, "batch requests are not supported"),
            );
            continue;
        }
        if !parsed.is_object() {
            errors += 1;
            emit(
                w,
                &error_response(None, ERR_INVALID, "request must be a JSON object"),
            );
            continue;
        }
        let notification = is_notification(&parsed);
        let id = parsed.get("id").cloned();
        let modern = modern_line_headers(&parsed);
        // 现代长流在串行代理里会卡死后续行 ⇒ 本地回 -32601,不转发(通知形态直接丢)
        if modern.is_some()
            && parsed.get("method").and_then(|m| m.as_str()) == Some("subscriptions/listen")
        {
            if !notification {
                errors += 1;
                emit(w, &error_response(id.as_ref(), ERR_METHOD_NOT_FOUND, "subscriptions/listen is not available through the stdio proxy (use the HTTP endpoint for change notifications)"));
            }
            continue;
        }
        let Some(p) = proxy.as_mut() else {
            if !notification {
                errors += 1;
                emit(
                    w,
                    &error_response(
                        id.as_ref(),
                        ERR_NOT_RUNNING,
                        "Horosa is not running (endpoint file missing or invalid)",
                    ),
                );
            }
            continue;
        };
        match p.forward(&line, modern.as_ref()) {
            Err(_) => {
                if !notification {
                    errors += 1;
                    emit(
                        w,
                        &error_response(
                            id.as_ref(),
                            ERR_NOT_RUNNING,
                            "Horosa is not running (local MCP service unreachable)",
                        ),
                    );
                }
            }
            Ok((status, text)) => {
                if notification {
                    continue;
                }
                if status == 202 || text.trim().is_empty() {
                    errors += 1;
                    emit(
                        w,
                        &error_response(
                            id.as_ref(),
                            ERR_INTERNAL,
                            &format!("empty response (HTTP {status})"),
                        ),
                    );
                    continue;
                }
                match serde_json::from_str::<Value>(&text) {
                    Ok(v) => emit(w, &v),
                    Err(_) => {
                        errors += 1;
                        emit(
                            w,
                            &error_response(
                                id.as_ref(),
                                ERR_INTERNAL,
                                &format!("non-JSON response (HTTP {status})"),
                            ),
                        );
                    }
                }
            }
        }
    }
    (handled, errors)
}

pub fn build_client() -> Option<reqwest::blocking::Client> {
    reqwest::blocking::Client::builder()
        .timeout(Duration::from_secs(HTTP_TIMEOUT_SECS))
        .no_proxy()
        .build()
        .ok()
}

/// CLI 入口:退出码 0=正常到 EOF;2=HTTP 客户端建不起来。端点文件读不到不算错(每个请求回 -32001,让客户端能看到原因)。
pub fn run_cli(endpoint_path: &Path) -> i32 {
    let Some(client) = build_client() else {
        return 2;
    };
    let ep = read_endpoint(endpoint_path).ok();
    let stdin = std::io::stdin();
    let stdout = std::io::stdout();
    let mut reader = stdin.lock();
    let mut writer = stdout.lock();
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
        assert!(lines[0].contains("\"id\":1") && lines[0].contains("\"echo\":\"ping\""));
        assert!(lines[1].contains("-32700"));
        assert!(lines[2].contains("-32600"));
        assert!(lines[3].contains("\"id\":2") && lines[3].contains("tools/list"));
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
        assert!(
            seen[0].contains("v=2026-07-28 m=server/discover n= s="),
            "{}",
            seen[0]
        );
        assert!(
            seen[1].contains("v=2026-07-28 m=tools/call n=get_time s="),
            "{}",
            seen[1]
        );
        assert!(
            seen[2].contains("m=tools/call n==?base64?"),
            "非 ASCII 名字须哨兵编码:{}",
            seen[2]
        );
        assert!(
            seen[3].contains("v=2025-06-18 m= n= s="),
            "旧 initialize 行不带现代头、此前无会话:{}",
            seen[3]
        );
        assert!(
            seen[4].contains("v=2025-06-18 m= n= s=sess-1"),
            "旧行带回会话头:{}",
            seen[4]
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
}
