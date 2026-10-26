//! 本机 REST 接口 `/api/v1`:与本机 MCP 同一服务、同一端口、同一令牌、同一道门(Host → Origin → Bearer)、同一套页面分发。
//! REST 只是把请求翻译成同一组 JSON-RPC 方法(tools/list · tools/call · resources/* · prompts/*)再转回 REST 形态 ——
//! 工具调用的限流 / 在途上限 / 外部审批 / 取消 / 进度与 MCP 完全同路(页面侧按调用方名 `rest` 分审批键与限流桶)。
//! 子开关缺省关:关 = 过了门之后一律 403 并说明去哪开。OpenAPI 文档由工具目录现生成(每件工具一条 POST,请求体 = 输入结构)。
use crate::mcp_server::{
    header_value, json_response, plain_response, progress_frame, CallControl, McpCore,
    PageDispatcher, SseResponse, ERR_CANCELLED, ERR_INTERNAL, ERR_INVALID_PARAMS,
    ERR_METHOD_NOT_FOUND, ERR_NOT_READY, ERR_RATE_LIMITED, ERR_RELOADED, ERR_TIMEOUT,
    MAX_BODY_BYTES, SSE_RESPONSE_KEEPALIVE,
};
use serde_json::{json, Value};
use std::io::Read;
use std::sync::atomic::{AtomicBool, AtomicU64, Ordering};
use std::sync::Arc;
use tiny_http::{Header, Method};

pub const REST_PREFIX: &str = "/api/v1";
/// 页面侧的调用方名(外部审批键 `mcp:rest`、限流桶都按它分)
pub const REST_CLIENT_NAME: &str = "rest";
pub const REST_DISABLED_MESSAGE: &str =
    "本机 REST 接口未开启:在星阙「AI 分析 › 进阶 › 外部连接」打开「REST 接口」";
/// GET 别名:常用读操作直接用 GET + 查询串(参数名同该工具的输入结构;数字 / 布尔由页面校验器转型)
pub const GET_ALIASES: [(&str, &str); 6] = [
    ("records", "list_records"),
    ("tasks", "list_tasks"),
    ("proposals", "list_proposals"),
    ("context", "get_current_context"),
    ("actions", "list_actions"),
    ("materials", "search_materials"),
];

static REST_SEQ: AtomicU64 = AtomicU64::new(1);

#[derive(Debug, PartialEq, Eq)]
pub enum RestRoute {
    Index,
    OpenApi,
    ToolsList,
    ToolCall(String),
    ResourcesList,
    ResourceTemplates,
    ResourceRead,
    PromptsList,
    PromptGet(String),
    Alias(&'static str),
    NotFound,
    MethodNotAllowed(&'static str),
}

/// 路由(纯函数):方法 + 去掉查询串的路径 → 内部动作
pub fn route(method: &Method, path: &str) -> RestRoute {
    let rest = path.strip_prefix(REST_PREFIX).unwrap_or("");
    let rest = rest.trim_end_matches('/');
    let segs: Vec<&str> = rest.split('/').filter(|s| !s.is_empty()).collect();
    let get = *method == Method::Get;
    let post = *method == Method::Post;
    match segs.as_slice() {
        [] => {
            if get {
                RestRoute::Index
            } else {
                RestRoute::MethodNotAllowed("GET")
            }
        }
        ["openapi.json"] => {
            if get {
                RestRoute::OpenApi
            } else {
                RestRoute::MethodNotAllowed("GET")
            }
        }
        ["tools"] => {
            if get {
                RestRoute::ToolsList
            } else {
                RestRoute::MethodNotAllowed("GET")
            }
        }
        ["tools", name] => {
            if post {
                RestRoute::ToolCall((*name).to_string())
            } else {
                RestRoute::MethodNotAllowed("POST")
            }
        }
        ["resources"] => {
            if get {
                RestRoute::ResourcesList
            } else {
                RestRoute::MethodNotAllowed("GET")
            }
        }
        ["resources", "templates"] => {
            if get {
                RestRoute::ResourceTemplates
            } else {
                RestRoute::MethodNotAllowed("GET")
            }
        }
        ["resources", "read"] | ["resource"] => {
            if get {
                RestRoute::ResourceRead
            } else {
                RestRoute::MethodNotAllowed("GET")
            }
        }
        ["prompts"] => {
            if get {
                RestRoute::PromptsList
            } else {
                RestRoute::MethodNotAllowed("GET")
            }
        }
        ["prompts", name] => {
            if post {
                RestRoute::PromptGet((*name).to_string())
            } else {
                RestRoute::MethodNotAllowed("POST")
            }
        }
        [alias] => match GET_ALIASES.iter().find(|(a, _)| a == alias) {
            Some((_, tool)) => {
                if get {
                    RestRoute::Alias(tool)
                } else {
                    RestRoute::MethodNotAllowed("GET")
                }
            }
            None => RestRoute::NotFound,
        },
        _ => RestRoute::NotFound,
    }
}

/// 查询串 → 键值(百分号解码;重复键取最后一个;空键丢弃)
pub fn parse_query(q: &str) -> serde_json::Map<String, Value> {
    let mut out = serde_json::Map::new();
    for pair in q.split('&') {
        if pair.is_empty() {
            continue;
        }
        let (k, v) = pair.split_once('=').unwrap_or((pair, ""));
        let dec = |s: &str| {
            urlencoding::decode(&s.replace('+', " "))
                .map(|c| c.into_owned())
                .unwrap_or_else(|_| s.to_string())
        };
        let key = dec(k);
        if key.is_empty() {
            continue;
        }
        out.insert(key, Value::String(dec(v)));
    }
    out
}

/// JSON-RPC 错误码 → HTTP 状态
pub fn rpc_error_status(code: i64) -> u16 {
    match code {
        ERR_INVALID_PARAMS => 400,
        ERR_METHOD_NOT_FOUND => 404,
        ERR_RATE_LIMITED => 429,
        ERR_TIMEOUT => 504,
        ERR_NOT_READY | ERR_RELOADED => 503,
        ERR_CANCELLED => 409,
        ERR_INTERNAL => 500,
        _ => 502,
    }
}

/// 工具结果(页面回的 {content, structuredContent?, isError})→ REST 形态 { ok, data?, text, error? };工具层失败 = 422
pub fn tool_result_body(result: &Value) -> (u16, Value) {
    let is_error = result
        .get("isError")
        .and_then(|v| v.as_bool())
        .unwrap_or(false);
    let text = result
        .get("content")
        .and_then(|c| c.as_array())
        .map(|arr| {
            arr.iter()
                .filter_map(|x| x.get("text").and_then(|t| t.as_str()))
                .collect::<Vec<_>>()
                .join("\n")
        })
        .unwrap_or_default();
    let mut body = json!({ "ok": !is_error, "text": text });
    if let Some(sc) = result.get("structuredContent").filter(|v| !v.is_null()) {
        body["data"] = sc.clone();
    }
    if is_error {
        if let Ok(e) = serde_json::from_str::<Value>(&text) {
            if e.get("code").and_then(|c| c.as_str()).is_some() {
                body["error"] = json!({
                    "code": e.get("code").cloned().unwrap_or(Value::Null),
                    "message": e.get("message").cloned().unwrap_or(Value::Null),
                    "retryable": e.get("retryable").cloned().unwrap_or(json!(false)),
                });
            }
            // 失败的结构化数据(候选 / 可用项)只在正文 JSON 里(结构化结果只给成功)
            if body.get("data").is_none() {
                if let Some(d) = e.get("data").filter(|d| d.is_object()) {
                    body["data"] = d.clone();
                }
            }
        }
    }
    (if is_error { 422 } else { 200 }, body)
}

fn error_body(status: u16, code: &str, message: &str) -> (u16, Value) {
    (
        status,
        json!({ "ok": false, "error": { "code": code, "message": message } }),
    )
}

/// 走同一份 JSON-RPC 分发(旧纪元路径,无会话);回 Ok(result) / Err((HTTP 状态, 错误体))
fn rpc(
    core: &McpCore,
    dispatcher: &dyn PageDispatcher,
    method: &str,
    params: Value,
    ctl: &CallControl,
) -> Result<Value, (u16, Value)> {
    let id = format!("rest-{}", REST_SEQ.fetch_add(1, Ordering::SeqCst));
    let req = json!({ "jsonrpc": "2.0", "id": id, "method": method, "params": params });
    let Some(v) = core.handle_rpc_ctl(&req, dispatcher, None, ctl) else {
        return Err(error_body(500, "INTERNAL", "no response"));
    };
    if let Some(err) = v.get("error") {
        let code = err
            .get("code")
            .and_then(|c| c.as_i64())
            .unwrap_or(ERR_INTERNAL);
        let msg = err
            .get("message")
            .and_then(|m| m.as_str())
            .unwrap_or("error");
        let mut body = json!({ "ok": false, "error": { "code": code, "message": msg } });
        if let Some(d) = err.get("data") {
            body["error"]["data"] = d.clone();
        }
        return Err((rpc_error_status(code), body));
    }
    Ok(v.get("result").cloned().unwrap_or(Value::Null))
}

fn with_client_meta(params: Value) -> Value {
    with_client_meta_idem(params, None)
}

/// 带幂等键(Idempotency-Key 请求头;与 MCP 的 `_meta.idempotencyKey` 同义,页面工具层据此让同键重试不重复写)
fn with_client_meta_idem(mut params: Value, idempotency_key: Option<&str>) -> Value {
    if let Some(obj) = params.as_object_mut() {
        let mut meta = json!({ "clientName": REST_CLIENT_NAME });
        if let Some(k) =
            idempotency_key.and_then(|k| crate::mcp_server::idempotency_key_norm(k).ok().flatten())
        {
            meta["idempotencyKey"] = json!(k);
        }
        obj.insert("_meta".to_string(), meta);
    }
    params
}

/// OpenAPI 3.1(由工具目录现生成;服务器地址用相对路径,端口随实例)
pub fn openapi_doc(tools: &[Value], app_version: &str) -> Value {
    let mut paths = serde_json::Map::new();
    let result_schema = |output: Option<&Value>| -> Value {
        let mut props = json!({ "ok": { "type": "boolean" }, "text": { "type": "string" }, "error": { "type": "object" } });
        props["data"] = output.cloned().unwrap_or(json!({ "type": "object" }));
        json!({ "type": "object", "required": ["ok"], "properties": props })
    };
    paths.insert("/tools".into(), json!({ "get": { "operationId": "listTools", "summary": "列出全部工具(与 MCP tools/list 同一份)", "responses": { "200": { "description": "工具清单" } } } }));
    for t in tools {
        let Some(name) = t.get("name").and_then(|v| v.as_str()) else {
            continue;
        };
        let summary = t.get("title").and_then(|v| v.as_str()).unwrap_or(name);
        let desc = t.get("description").and_then(|v| v.as_str()).unwrap_or("");
        let input = t
            .get("inputSchema")
            .cloned()
            .unwrap_or(json!({ "type": "object" }));
        let ok_schema = result_schema(t.get("outputSchema"));
        paths.insert(
            format!("/tools/{}", name),
            json!({ "post": {
                "operationId": name, "summary": summary, "description": desc,
                "parameters": [
                    { "name": "stream", "in": "query", "required": false, "schema": { "type": "string", "enum": ["1"] }, "description": "1 = 以 text/event-stream 回报进度(event: progress)与结果(event: result)" },
                    { "name": "Idempotency-Key", "in": "header", "required": false, "schema": { "type": "string", "maxLength": 200 }, "description": "写入类:同一个键重试回放第一次的结果、不重复写(同键换参数被拒;1..200 字,超长 = 400)" }
                ],
                "requestBody": { "required": false, "content": { "application/json": { "schema": input } } },
                "responses": {
                    "200": { "description": "工具成功", "content": { "application/json": { "schema": ok_schema } } },
                    "422": { "description": "工具失败(error.code 见错误码表)", "content": { "application/json": { "schema": result_schema(None) } } },
                    "429": { "description": "超出调用上限" }, "503": { "description": "页面未就绪 / 服务重启中(看 error.data.retryAfterMs)" }
                }
            } }),
        );
    }
    for (alias, tool) in GET_ALIASES.iter() {
        paths.insert(format!("/{}", alias), json!({ "get": { "operationId": format!("get_{}", alias), "summary": format!("{} 的 GET 别名(查询串 = 参数)", tool), "responses": { "200": { "description": "同 POST /tools/{tool}" } } } }));
    }
    paths.insert("/resources".into(), json!({ "get": { "operationId": "listResources", "parameters": [{ "name": "cursor", "in": "query", "required": false, "schema": { "type": "string" } }], "responses": { "200": { "description": "资源清单(nextCursor 翻页)" } } } }));
    paths.insert("/resources/templates".into(), json!({ "get": { "operationId": "listResourceTemplates", "responses": { "200": { "description": "资源模版" } } } }));
    paths.insert("/resources/read".into(), json!({ "get": { "operationId": "readResource", "parameters": [{ "name": "uri", "in": "query", "required": true, "schema": { "type": "string" } }], "responses": { "200": { "description": "资源正文" } } } }));
    paths.insert("/prompts".into(), json!({ "get": { "operationId": "listPrompts", "parameters": [{ "name": "cursor", "in": "query", "required": false, "schema": { "type": "string" } }], "responses": { "200": { "description": "提示清单" } } } }));
    paths.insert("/prompts/{name}".into(), json!({ "post": { "operationId": "getPrompt", "parameters": [{ "name": "name", "in": "path", "required": true, "schema": { "type": "string" } }], "requestBody": { "required": false, "content": { "application/json": { "schema": { "type": "object" } } } }, "responses": { "200": { "description": "提示消息" } } } }));
    json!({
        "openapi": "3.1.0",
        "info": { "title": "星阙 Horosa 本机接口", "version": app_version, "description": "与本机 MCP 同一服务、同一令牌(Authorization: Bearer)、同一套工具;只接受本机回环地址。写入类工具受「外部客户端策略」管(审批 / 上限)。" },
        "servers": [{ "url": REST_PREFIX }],
        "security": [{ "bearer": [] }],
        "components": { "securitySchemes": { "bearer": { "type": "http", "scheme": "bearer" } } },
        "paths": Value::Object(paths),
    })
}

fn respond(request: tiny_http::Request, status: u16, body: &Value) {
    let mut r = json_response(status, body);
    if status == 401 {
        if let Ok(h) = Header::from_bytes(&b"WWW-Authenticate"[..], &b"Bearer realm=\"horosa\""[..])
        {
            r = r.with_header(h);
        }
    }
    if status == 503 {
        let after = body
            .pointer("/error/data/retryAfterMs")
            .and_then(|v| v.as_u64())
            .map(|ms| ((ms + 999) / 1000).max(1))
            .unwrap_or(1);
        if let Ok(h) = Header::from_bytes(&b"Retry-After"[..], after.to_string().as_bytes()) {
            r = r.with_header(h);
        }
    }
    let _ = request.respond(r);
}

fn read_json_body(request: &mut tiny_http::Request) -> Result<Value, (u16, Value)> {
    if request.body_length().unwrap_or(0) > MAX_BODY_BYTES {
        return Err(error_body(413, "PAYLOAD_TOO_LARGE", "payload too large"));
    }
    let mut body = Vec::new();
    if request
        .as_reader()
        .take(MAX_BODY_BYTES as u64 + 1)
        .read_to_end(&mut body)
        .is_err()
        || body.len() > MAX_BODY_BYTES
    {
        return Err(error_body(413, "PAYLOAD_TOO_LARGE", "payload too large"));
    }
    if body.iter().all(|b| b.is_ascii_whitespace()) {
        return Ok(json!({}));
    }
    let v: Value = serde_json::from_slice(&body)
        .map_err(|e| error_body(400, "BAD_JSON", &format!("请求体不是 JSON: {}", e)))?;
    if !v.is_object() {
        return Err(error_body(
            400,
            "BAD_JSON",
            "请求体须为 JSON 对象(工具参数)",
        ));
    }
    Ok(v)
}

/// HTTP 入口(由 mcp_server::handle_request 按路径前缀转进来)
pub fn handle(core: &McpCore, dispatcher: &dyn PageDispatcher, mut request: tiny_http::Request) {
    let raw = request.url().to_string();
    let (path, query) = raw.split_once('?').unwrap_or((raw.as_str(), ""));
    let path = path.to_string();
    let query = parse_query(query);
    let method = request.method().clone();
    // 门:与 /mcp 同一道 Host → Origin → Bearer(REST 不看 MCP 协议版本头);门在前,开关在后(不对无令牌方透露开关状态)
    if let Err((status, msg)) = core.gate(
        header_value(&request, "Host"),
        header_value(&request, "Origin"),
        header_value(&request, "Authorization"),
        None,
    ) {
        if status == 401 {
            respond(
                request,
                401,
                &json!({ "ok": false, "error": { "code": "UNAUTHORIZED", "message": msg } }),
            );
        } else {
            let _ = request.respond(plain_response(status, msg));
        }
        return;
    }
    if !core.rest_enabled() {
        let (s, b) = error_body(403, "REST_DISABLED", REST_DISABLED_MESSAGE);
        respond(request, s, &b);
        return;
    }
    let none = CallControl::none();
    match route(&method, &path) {
        RestRoute::Index => {
            let aliases: Vec<Value> = GET_ALIASES
                .iter()
                .map(|(a, t)| json!({ "path": format!("{}/{}", REST_PREFIX, a), "tool": t }))
                .collect();
            respond(
                request,
                200,
                &json!({
                    "app": "horosa", "version": core.app_version(), "base": REST_PREFIX,
                    "docs": format!("{}/openapi.json", REST_PREFIX),
                    "endpoints": ["GET /tools", "POST /tools/{name}[?stream=1]", "GET /resources[?cursor=]", "GET /resources/templates", "GET /resources/read?uri=", "GET /prompts[?cursor=]", "POST /prompts/{name}", "GET /openapi.json"],
                    "aliases": aliases,
                }),
            );
        }
        RestRoute::OpenApi => match rpc(core, dispatcher, "tools/list", json!({}), &none) {
            Ok(r) => {
                let tools = r
                    .get("tools")
                    .and_then(|t| t.as_array())
                    .cloned()
                    .unwrap_or_default();
                respond(request, 200, &openapi_doc(&tools, core.app_version()));
            }
            Err((s, b)) => respond(request, s, &b),
        },
        RestRoute::ToolsList => match rpc(core, dispatcher, "tools/list", json!({}), &none) {
            Ok(r) => respond(
                request,
                200,
                &json!({ "ok": true, "tools": r.get("tools").cloned().unwrap_or(json!([])) }),
            ),
            Err((s, b)) => respond(request, s, &b),
        },
        RestRoute::ToolCall(name) => {
            let args = match read_json_body(&mut request) {
                Ok(v) => v,
                Err((s, b)) => return respond(request, s, &b),
            };
            // 幂等键:空 = 没带;超长 = 400(不静默丢:静默丢 = 调用方以为受了保护,重试照样重复写)
            let idem = match header_value(&request, "Idempotency-Key")
                .map(crate::mcp_server::idempotency_key_norm)
                .transpose()
            {
                Ok(k) => k.flatten(),
                Err(m) => {
                    let (s, b) = error_body(400, "BAD_REQUEST", m);
                    return respond(request, s, &b);
                }
            };
            let params =
                with_client_meta_idem(json!({ "name": name, "arguments": args }), idem.as_deref());
            let wants_stream = query.get("stream").and_then(|v| v.as_str()) == Some("1")
                || header_value(&request, "Accept")
                    .map(|a| a.contains("text/event-stream"))
                    .unwrap_or(false);
            if wants_stream && *request.http_version() >= (1, 1) {
                call_streaming(core, dispatcher, request, params);
                return;
            }
            match rpc(core, dispatcher, "tools/call", params, &none) {
                Ok(r) => {
                    let (s, b) = tool_result_body(&r);
                    respond(request, s, &b);
                }
                Err((s, b)) => respond(request, s, &b),
            }
        }
        RestRoute::Alias(tool) => {
            let params =
                with_client_meta(json!({ "name": tool, "arguments": Value::Object(query) }));
            match rpc(core, dispatcher, "tools/call", params, &none) {
                Ok(r) => {
                    let (s, b) = tool_result_body(&r);
                    respond(request, s, &b);
                }
                Err((s, b)) => respond(request, s, &b),
            }
        }
        RestRoute::ResourcesList | RestRoute::PromptsList => {
            let m = if route(&method, &path) == RestRoute::ResourcesList {
                "resources/list"
            } else {
                "prompts/list"
            };
            let mut p = json!({});
            if let Some(c) = query.get("cursor") {
                p["cursor"] = c.clone();
            }
            match rpc(core, dispatcher, m, p, &none) {
                Ok(r) => {
                    let mut b = r.clone();
                    if let Some(o) = b.as_object_mut() {
                        o.insert("ok".into(), json!(true));
                    }
                    respond(request, 200, &b);
                }
                Err((s, b)) => respond(request, s, &b),
            }
        }
        RestRoute::ResourceTemplates => match rpc(
            core,
            dispatcher,
            "resources/templates/list",
            json!({}),
            &none,
        ) {
            Ok(r) => respond(
                request,
                200,
                &json!({ "ok": true, "resourceTemplates": r.get("resourceTemplates").cloned().unwrap_or(json!([])) }),
            ),
            Err((s, b)) => respond(request, s, &b),
        },
        RestRoute::ResourceRead => {
            let Some(uri) = query
                .get("uri")
                .and_then(|u| u.as_str())
                .filter(|u| !u.is_empty())
                .map(|u| u.to_string())
            else {
                let (s, b) = error_body(
                    400,
                    "BAD_REQUEST",
                    "缺查询参数 uri(如 horosa://chart/local-…)",
                );
                return respond(request, s, &b);
            };
            match rpc(
                core,
                dispatcher,
                "resources/read",
                json!({ "uri": uri }),
                &none,
            ) {
                Ok(r) => respond(
                    request,
                    200,
                    &json!({ "ok": true, "contents": r.get("contents").cloned().unwrap_or(json!([])) }),
                ),
                Err((s, b)) => respond(request, s, &b),
            }
        }
        RestRoute::PromptGet(name) => {
            let args = match read_json_body(&mut request) {
                Ok(v) => v,
                Err((s, b)) => return respond(request, s, &b),
            };
            match rpc(
                core,
                dispatcher,
                "prompts/get",
                json!({ "name": name, "arguments": args }),
                &none,
            ) {
                Ok(r) => {
                    let mut b = r.clone();
                    if let Some(o) = b.as_object_mut() {
                        o.insert("ok".into(), json!(true));
                    }
                    respond(request, 200, &b);
                }
                Err((s, b)) => respond(request, s, &b),
            }
        }
        RestRoute::MethodNotAllowed(allow) => {
            let mut r = json_response(
                405,
                &json!({ "ok": false, "error": { "code": "METHOD_NOT_ALLOWED", "message": format!("只接受 {}", allow) } }),
            );
            if let Ok(h) = Header::from_bytes(&b"Allow"[..], allow.as_bytes()) {
                r = r.with_header(h);
            }
            let _ = request.respond(r);
        }
        RestRoute::NotFound => {
            let (s, b) = error_body(
                404,
                "NOT_FOUND",
                &format!("没有这个接口:{};接口清单见 GET {}", path, REST_PREFIX),
            );
            respond(request, s, &b);
        }
    }
}

/// 流式工具调用:`event: progress`(单调递增)… `event: result` / `event: error`;客户端断开 = 取消(同 MCP 现代纪元)
fn call_streaming(
    core: &McpCore,
    dispatcher: &dyn PageDispatcher,
    request: tiny_http::Request,
    params: Value,
) {
    let sink = SseResponse::open(request);
    let token = json!("rest");
    let last = std::cell::RefCell::new(None::<f64>);
    let on_progress = |v: &Value| -> bool {
        match progress_frame(&token, v, &mut last.borrow_mut()) {
            Some(f) => {
                let p = f.get("params").cloned().unwrap_or(json!({}));
                let mut out =
                    json!({ "progress": p.get("progress").cloned().unwrap_or(Value::Null) });
                if let Some(t) = p.get("total") {
                    out["total"] = t.clone();
                }
                if let Some(m) = p.get("message") {
                    out["message"] = m.clone();
                }
                sink.event("progress", &out)
            }
            None => !sink.is_broken(),
        }
    };
    let on_tick = || sink.keepalive_if_quiet(SSE_RESPONSE_KEEPALIVE);
    let ctl = CallControl {
        cancelled: Arc::new(AtomicBool::new(false)),
        on_progress: Some(&on_progress),
        on_tick: Some(&on_tick),
        cancel_on_disconnect: true,
    };
    match rpc(core, dispatcher, "tools/call", params, &ctl) {
        Ok(r) => {
            if !ctl.is_cancelled() {
                let (s, mut b) = tool_result_body(&r);
                b["status"] = json!(s);
                sink.event("result", &b);
            }
        }
        Err((s, mut b)) => {
            if !ctl.is_cancelled() {
                b["status"] = json!(s);
                sink.event("error", &b);
            }
        }
    }
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn idempotency_key_header_lands_in_meta() {
        let p = with_client_meta_idem(json!({ "name": "x", "arguments": {} }), Some(" k-1 "));
        assert_eq!(p["_meta"]["clientName"], json!(REST_CLIENT_NAME));
        assert_eq!(p["_meta"]["idempotencyKey"], json!("k-1"));
        let none = with_client_meta(json!({ "name": "x" }));
        assert!(none["_meta"].get("idempotencyKey").is_none());
        let long = "k".repeat(201);
        let p2 = with_client_meta_idem(json!({ "name": "x" }), Some(long.as_str()));
        assert!(p2["_meta"].get("idempotencyKey").is_none());
        let blank = with_client_meta_idem(json!({ "name": "x" }), Some("  "));
        assert!(blank["_meta"].get("idempotencyKey").is_none());
    }

    #[test]
    fn route_table_maps_methods_and_paths() {
        assert_eq!(route(&Method::Get, "/api/v1"), RestRoute::Index);
        assert_eq!(route(&Method::Get, "/api/v1/"), RestRoute::Index);
        assert_eq!(
            route(&Method::Get, "/api/v1/openapi.json"),
            RestRoute::OpenApi
        );
        assert_eq!(route(&Method::Get, "/api/v1/tools"), RestRoute::ToolsList);
        assert_eq!(
            route(&Method::Post, "/api/v1/tools/list_records"),
            RestRoute::ToolCall("list_records".into())
        );
        assert_eq!(
            route(&Method::Get, "/api/v1/tools/list_records"),
            RestRoute::MethodNotAllowed("POST")
        );
        assert_eq!(
            route(&Method::Get, "/api/v1/resources"),
            RestRoute::ResourcesList
        );
        assert_eq!(
            route(&Method::Get, "/api/v1/resources/templates"),
            RestRoute::ResourceTemplates
        );
        assert_eq!(
            route(&Method::Get, "/api/v1/resources/read"),
            RestRoute::ResourceRead
        );
        assert_eq!(
            route(&Method::Get, "/api/v1/resource"),
            RestRoute::ResourceRead
        );
        assert_eq!(
            route(&Method::Post, "/api/v1/prompts/guide:horosa"),
            RestRoute::PromptGet("guide:horosa".into())
        );
        assert_eq!(
            route(&Method::Get, "/api/v1/records"),
            RestRoute::Alias("list_records")
        );
        assert_eq!(
            route(&Method::Post, "/api/v1/records"),
            RestRoute::MethodNotAllowed("GET")
        );
        assert_eq!(route(&Method::Get, "/api/v1/nope"), RestRoute::NotFound);
        assert_eq!(
            route(&Method::Get, "/api/v1/tools/a/b"),
            RestRoute::NotFound
        );
    }

    #[test]
    fn query_parsing_decodes_and_keeps_last() {
        let q = parse_query("query=%E5%BC%A0&limit=5&limit=7&&=x&flag&a+b=c+d");
        assert_eq!(q.get("query").and_then(|v| v.as_str()), Some("张"));
        assert_eq!(q.get("limit").and_then(|v| v.as_str()), Some("7"));
        assert_eq!(q.get("flag").and_then(|v| v.as_str()), Some(""));
        assert_eq!(q.get("a b").and_then(|v| v.as_str()), Some("c d"));
        assert!(!q.contains_key(""));
    }

    #[test]
    fn tool_results_map_to_rest_shape_and_status() {
        let ok = json!({ "content": [{ "type": "text", "text": "已建档" }], "structuredContent": { "cid": "local-1" }, "isError": false });
        let (s, b) = tool_result_body(&ok);
        assert_eq!(s, 200);
        assert_eq!(b["ok"], json!(true));
        assert_eq!(b["data"]["cid"], json!("local-1"));
        let bad = json!({ "content": [{ "type": "text", "text": "{\"ok\":false,\"code\":\"E_RECORD_NOT_FOUND\",\"retryable\":false,\"message\":\"未找到\"}" }], "isError": true });
        let (s2, b2) = tool_result_body(&bad);
        assert_eq!(s2, 422);
        assert_eq!(b2["error"]["code"], json!("E_RECORD_NOT_FOUND"));
        // 失败的结构化数据从正文 JSON 回到 data(结构化结果只给成功)
        let amb = json!({ "content": [{ "type": "text", "text": "{\"ok\":false,\"code\":\"E_PLACE_AMBIGUOUS\",\"data\":{\"candidates\":[1,2]}}" }], "isError": true });
        let (s3, b3) = tool_result_body(&amb);
        assert_eq!(s3, 422);
        assert_eq!(b3["data"]["candidates"], json!([1, 2]));
        assert_eq!(rpc_error_status(ERR_RATE_LIMITED), 429);
        assert_eq!(rpc_error_status(ERR_NOT_READY), 503);
        assert_eq!(rpc_error_status(ERR_TIMEOUT), 504);
        assert_eq!(rpc_error_status(ERR_INVALID_PARAMS), 400);
    }

    #[test]
    fn openapi_lists_every_tool_with_its_schemas() {
        let tools = vec![
            json!({ "name": "list_records", "title": "检索档案", "description": "d", "inputSchema": { "type": "object", "properties": { "query": { "type": "string" } } }, "outputSchema": { "type": "object", "properties": { "items": { "type": "array" } } } }),
            json!({ "name": "create_chart_record", "inputSchema": { "type": "object" } }),
        ];
        let doc = openapi_doc(&tools, "9.9.9");
        assert_eq!(doc["openapi"], json!("3.1.0"));
        assert_eq!(doc["servers"][0]["url"], json!(REST_PREFIX));
        let p = &doc["paths"]["/tools/list_records"]["post"];
        assert_eq!(p["operationId"], json!("list_records"));
        assert_eq!(p["summary"], json!("检索档案"));
        assert_eq!(
            p["requestBody"]["content"]["application/json"]["schema"]["properties"]["query"]
                ["type"],
            json!("string")
        );
        assert_eq!(
            p["responses"]["200"]["content"]["application/json"]["schema"]["properties"]["data"]
                ["properties"]["items"]["type"],
            json!("array")
        );
        assert!(doc["paths"]["/tools/create_chart_record"]["post"].is_object());
        // 幂等请求头写进每个工具的 POST(与无头 rest.js 的 openApiDoc 同形)
        let params = doc["paths"]["/tools/create_chart_record"]["post"]["parameters"]
            .as_array()
            .unwrap();
        let h = params
            .iter()
            .find(|x| x["name"] == "Idempotency-Key")
            .expect("Idempotency-Key 头参数");
        assert_eq!(h["in"], json!("header"));
        assert_eq!(h["schema"]["maxLength"], json!(200));
        assert!(doc["paths"]["/records"]["get"].is_object());
    }
}
