//! 智能体相关命令:总开关、本机服务、令牌、终端命令垫片、工具回传、调度心跳、外部服务清单。

use super::*;

// ── AI 助手·行动能力 / 外部智能体连接(本机 MCP 服务)命令 ──
#[tauri::command]
pub(crate) async fn set_agent_enabled_command(
    app: AppHandle,
    enabled: bool,
) -> std::result::Result<serde_json::Value, String> {
    let mut prefs = load_preferences(&app);
    prefs.agent_enabled = enabled;
    save_preferences(&app, &prefs).map_err(|err| format!("{err:#}"))?;
    if let Some(state) = app.try_state::<mcp_server::McpState>() {
        mcp_server::apply_enabled(&app, &state, prefs.agent_enabled, prefs.mcp_server_enabled)
            .map_err(|err| format!("{err:#}"))?;
    }
    Ok(serde_json::json!({ "enabled": enabled }))
}

#[tauri::command]
pub(crate) fn mcp_server_status_command(
    app: AppHandle,
) -> std::result::Result<serde_json::Value, String> {
    let prefs = load_preferences(&app);
    let state = app
        .try_state::<mcp_server::McpState>()
        .ok_or_else(|| "missing mcp state".to_string())?;
    Ok(mcp_server::status_json(
        &app,
        &state,
        prefs.agent_enabled,
        prefs.mcp_server_enabled,
    ))
}

#[tauri::command]
pub(crate) async fn mcp_server_set_enabled_command(
    app: AppHandle,
    enabled: bool,
) -> std::result::Result<serde_json::Value, String> {
    let mut prefs = load_preferences(&app);
    prefs.mcp_server_enabled = enabled;
    save_preferences(&app, &prefs).map_err(|err| format!("{err:#}"))?;
    let state = app
        .try_state::<mcp_server::McpState>()
        .ok_or_else(|| "missing mcp state".to_string())?;
    mcp_server::apply_enabled(&app, &state, prefs.agent_enabled, prefs.mcp_server_enabled)
        .map_err(|err| format!("{err:#}"))?;
    Ok(mcp_server::status_json(
        &app,
        &state,
        prefs.agent_enabled,
        prefs.mcp_server_enabled,
    ))
}

// ── 定时任务:壳侧只做 60 秒哑心跳(调度大脑在页面 aiAgent/tasks/scheduler.js);偏好 scheduler_enabled 缺省 false;
//    HOROSA_SCHEDULER=0 一票否决;页面未绑定时 pending 只留最新一跳;每 30 跳记一次账本(rust.scheduler_tick)。
pub(crate) static SCHEDULER_TICKS: std::sync::atomic::AtomicU64 =
    std::sync::atomic::AtomicU64::new(0);
static SCHEDULER_LAST_TICK: Mutex<Option<u64>> = Mutex::new(None);
pub(crate) const SCHEDULER_FIRST_DELAY_SECS: u64 = 90;
pub(crate) const SCHEDULER_INTERVAL_SECS: u64 = 60;
const SCHEDULER_LEDGER_EVERY: u64 = 30;

pub(crate) fn scheduler_kill_switch() -> bool {
    std::env::var("HOROSA_SCHEDULER")
        .map(|v| v.trim() == "0")
        .unwrap_or(false)
}

/// 外部客户端策略「每分钟调用上限」的壳侧镜像:页面策略 1..600 ⇒ 壳令牌桶按用户值生效(此前壳写死 60/分钟,页面 >60 全部无效);
/// 落偏好,重启后服务重建时重施;回实际生效值。
#[tauri::command]
pub(crate) fn mcp_server_set_limits_command(
    app: AppHandle,
    calls_per_minute: u32,
) -> std::result::Result<serde_json::Value, String> {
    let n = calls_per_minute.clamp(1, 600);
    let mut prefs = load_preferences(&app);
    prefs.mcp_calls_per_minute = n;
    save_preferences(&app, &prefs).map_err(|err| format!("{err:#}"))?;
    let applied = match app.try_state::<mcp_server::McpState>() {
        Some(state) => mcp_server::apply_limits(&state, n).map_err(|err| format!("{err:#}"))?,
        None => n,
    };
    Ok(serde_json::json!({ "callsPerMinute": applied }))
}

#[tauri::command]
pub(crate) fn set_scheduler_enabled_command(
    app: AppHandle,
    enabled: bool,
) -> std::result::Result<serde_json::Value, String> {
    let mut prefs = load_preferences(&app);
    prefs.scheduler_enabled = enabled;
    save_preferences(&app, &prefs).map_err(|err| format!("{err:#}"))?;
    Ok(serde_json::json!({ "enabled": enabled, "killSwitch": scheduler_kill_switch() }))
}

#[tauri::command]
pub(crate) fn scheduler_status_command(
    app: AppHandle,
) -> std::result::Result<serde_json::Value, String> {
    let prefs = load_preferences(&app);
    let last = *SCHEDULER_LAST_TICK
        .lock()
        .unwrap_or_else(|e| e.into_inner());
    Ok(serde_json::json!({
        "enabled": prefs.scheduler_enabled,
        "killSwitch": scheduler_kill_switch(),
        "ticks": SCHEDULER_TICKS.load(std::sync::atomic::Ordering::Relaxed),
        "lastTickAt": last,
        "intervalSecs": SCHEDULER_INTERVAL_SECS,
    }))
}

/// 定时任务 tick 投递(壳→页面 eval 回调范式,同 dispatch_auto_backup_tick;页面未就绪只留最新一跳)。返回是否找到主窗口。
pub(crate) fn dispatch_scheduler_tick(app: &AppHandle, seq: u64) -> bool {
    let Some(window) = app.get_webview_window(MAIN_WINDOW_LABEL) else {
        return false;
    };
    let at = unix_ts();
    let payload =
        serde_json::json!({ "seq": seq, "at": at, "intervalSecs": SCHEDULER_INTERVAL_SECS });
    let script = scheduler_tick_script(&payload.to_string());
    let _ = window.eval(&script);
    *SCHEDULER_LAST_TICK
        .lock()
        .unwrap_or_else(|e| e.into_inner()) = Some(at);
    if seq % SCHEDULER_LEDGER_EVERY == 1 {
        ledger_mark("rust.scheduler_tick", Some(payload));
    }
    true
}

/// 纯函数(可单测):有回调即调,无回调入队且只留最新 1 条(页面绑定时补跑一次即可,多跳无意义)。
pub(crate) fn scheduler_tick_script(payload_json: &str) -> String {
    format!(
        "(function(){{var t={payload_json};if(typeof window.__horosaSchedulerTick==='function'){{try{{window.__horosaSchedulerTick(t);}}catch(e){{}}}}else{{var q=window.__horosaPendingSchedulerTicks=window.__horosaPendingSchedulerTicks||[];q.push(t);if(q.length>1){{q.splice(0,q.length-1);}}}}}})();"
    )
}

// [REST] 本机 REST 接口子开关:落偏好 → 施加到运行中的核 → 回最新状态(含 restEnabled / restUrl)
#[tauri::command]
pub(crate) async fn mcp_server_set_rest_enabled_command(
    app: AppHandle,
    enabled: bool,
) -> std::result::Result<serde_json::Value, String> {
    let mut prefs = load_preferences(&app);
    prefs.mcp_rest_enabled = enabled;
    save_preferences(&app, &prefs).map_err(|err| format!("{err:#}"))?;
    let state = app
        .try_state::<mcp_server::McpState>()
        .ok_or_else(|| "missing mcp state".to_string())?;
    mcp_server::apply_rest_enabled(&state, enabled);
    crate::ledger_mark(
        "rust.mcp_rest_enabled",
        Some(serde_json::json!({ "enabled": enabled })),
    );
    Ok(mcp_server::status_json(
        &app,
        &state,
        prefs.agent_enabled,
        prefs.mcp_server_enabled,
    ))
}

// [CLI] 终端命令垫片(~/.local/bin/horosa):只碰带本应用标记的那一个文件(用户自己的同名文件不覆盖、不删)
#[tauri::command]
pub(crate) fn cli_shim_status_command() -> std::result::Result<serde_json::Value, String> {
    horosa_cli::shim_status_now()
}

#[tauri::command]
pub(crate) fn cli_shim_install_command() -> std::result::Result<serde_json::Value, String> {
    let r = horosa_cli::shim_install_now();
    crate::ledger_mark(
        "rust.cli_shim_install",
        Some(serde_json::json!({ "ok": r.is_ok() })),
    );
    r
}

#[tauri::command]
pub(crate) fn cli_shim_remove_command() -> std::result::Result<serde_json::Value, String> {
    let r = horosa_cli::shim_remove_now();
    crate::ledger_mark(
        "rust.cli_shim_remove",
        Some(serde_json::json!({ "ok": r.is_ok() })),
    );
    r
}

#[tauri::command]
pub(crate) async fn mcp_server_rotate_token_command(
    app: AppHandle,
) -> std::result::Result<serde_json::Value, String> {
    let prefs = load_preferences(&app);
    let state = app
        .try_state::<mcp_server::McpState>()
        .ok_or_else(|| "missing mcp state".to_string())?;
    mcp_server::rotate_token(&app, &state).map_err(|err| format!("{err:#}"))?;
    Ok(mcp_server::status_json(
        &app,
        &state,
        prefs.agent_enabled,
        prefs.mcp_server_enabled,
    ))
}
/// 令牌只在用户点「复制」时按需取(状态查询不再携带令牌)。
#[tauri::command]
pub(crate) fn mcp_server_reveal_token_command(
    app: AppHandle,
) -> std::result::Result<serde_json::Value, String> {
    let state = app
        .try_state::<mcp_server::McpState>()
        .ok_or_else(|| "missing mcp state".to_string())?;
    let token = mcp_server::reveal_token(&state).unwrap_or_default();
    Ok(serde_json::json!({ "token": token, "running": !token.is_empty() }))
}

#[tauri::command]
pub(crate) fn agent_tool_result_command(
    app: AppHandle,
    id: u64,
    ok: bool,
    result: Option<serde_json::Value>,
    error: Option<serde_json::Value>,
) -> std::result::Result<bool, String> {
    let state = app
        .try_state::<mcp_server::McpState>()
        .ok_or_else(|| "missing mcp state".to_string())?;
    let outcome = if ok {
        Ok(result.unwrap_or(serde_json::Value::Null))
    } else {
        let e = error.unwrap_or(serde_json::Value::Null);
        Err(mcp_server::McpError {
            code: e
                .get("code")
                .and_then(|c| c.as_i64())
                .unwrap_or(mcp_server::ERR_INTERNAL),
            message: e
                .get("message")
                .and_then(|m| m.as_str())
                .unwrap_or("tool failed")
                .to_string(),
            data: e.get("data").cloned(),
        })
    };
    Ok(state.bridge.resolve(id, outcome))
}

/// 页面回传某次外部调用的进度(`{progress,total?,message?}`);壳只转发给带进度令牌、且有自己响应流的那次请求,
/// 其余情形(调用已了结 / 没要进度 / 超出硬顶)回 false。永不阻塞(主线程上跑)。
#[tauri::command]
pub(crate) fn agent_tool_progress_command(
    app: AppHandle,
    id: u64,
    progress: f64,
    total: Option<f64>,
    message: Option<String>,
) -> std::result::Result<bool, String> {
    let state = app
        .try_state::<mcp_server::McpState>()
        .ok_or_else(|| "missing mcp state".to_string())?;
    let mut v = serde_json::json!({ "progress": progress });
    if let Some(t) = total {
        v["total"] = serde_json::json!(t);
    }
    if let Some(m) = message {
        v["message"] = serde_json::json!(m);
    }
    Ok(state.bridge.progress(id, v))
}

#[tauri::command]
pub(crate) fn agent_bridge_ready_command(
    app: AppHandle,
    version: Option<u32>,
    ready: Option<bool>,
) -> std::result::Result<bool, String> {
    let state = app
        .try_state::<mcp_server::McpState>()
        .ok_or_else(|| "missing mcp state".to_string())?;
    let is_ready = ready.unwrap_or(true);
    state.bridge.set_ready(is_ready);
    // 页面桥(重新)绑定或离场 → 工具目录缓存作废,tools/list 与 tools/call 口径一致
    // 并向 SSE 订阅者推 tools/list_changed(外部客户端不必轮询)
    if let Ok(inner) = state.inner.lock() {
        if let Some(core) = inner.core.as_ref() {
            core.invalidate_tools_cache();
            if is_ready {
                core.notify("notifications/tools/list_changed", serde_json::json!({}));
            }
        }
    }
    ledger_mark(
        "rust.agent_bridge_ready",
        Some(serde_json::json!({ "version": version.unwrap_or(0), "ready": is_ready })),
    );
    Ok(true)
}

/// 外部 MCP 服务器(出站,默认关):清单/连接/调用全部经壳侧;令牌只落 0600 配置文件,回页面一律脱敏。
#[tauri::command]
pub(crate) fn mcp_client_list_command(
    app: AppHandle,
) -> std::result::Result<Vec<serde_json::Value>, String> {
    let state = app
        .try_state::<mcp_client::ClientState>()
        .ok_or_else(|| "missing mcp client state".to_string())?;
    Ok(state.list())
}

#[tauri::command]
pub(crate) fn mcp_client_upsert_command(
    app: AppHandle,
    spec: mcp_client::ServerSpec,
    keep_headers: Option<bool>,
) -> std::result::Result<serde_json::Value, String> {
    let state = app
        .try_state::<mcp_client::ClientState>()
        .ok_or_else(|| "missing mcp client state".to_string())?;
    // 面板「编辑」令牌留空 ⇒ keep_headers=true 沿用旧令牌
    let out = state
        .upsert_keeping(spec, keep_headers.unwrap_or(false))
        .map_err(|e| format!("{e:#}"))?;
    ledger_mark(
        "rust.mcp_client_upsert",
        Some(serde_json::json!({ "id": out.get("id").cloned() })),
    );
    Ok(out)
}

/// 删除 / 断开走后台线程(spawn_blocking):命令默认跑在主线程,断开要杀子进程、删除还要写盘,
/// 都不该占着界面线程(在途调用最长可达 120 s,此前同步断开会一直等它放锁)。
#[tauri::command]
pub(crate) async fn mcp_client_remove_command(
    app: AppHandle,
    id: String,
) -> std::result::Result<bool, String> {
    tauri::async_runtime::spawn_blocking(move || {
        let state = app
            .try_state::<mcp_client::ClientState>()
            .ok_or_else(|| "missing mcp client state".to_string())?;
        state.remove(&id).map_err(|e| format!("{e:#}"))
    })
    .await
    .map_err(|e| format!("{e}"))?
}

#[tauri::command]
pub(crate) async fn mcp_client_connect_command(
    app: AppHandle,
    id: String,
) -> std::result::Result<serde_json::Value, String> {
    tauri::async_runtime::spawn_blocking(move || {
        let state = app
            .try_state::<mcp_client::ClientState>()
            .ok_or_else(|| "missing mcp client state".to_string())?;
        state.connect(&id).map_err(|e| format!("{e:#}"))
    })
    .await
    .map_err(|e| format!("{e}"))?
}

#[tauri::command]
pub(crate) async fn mcp_client_call_command(
    app: AppHandle,
    id: String,
    tool: String,
    arguments: Option<serde_json::Value>,
) -> std::result::Result<serde_json::Value, String> {
    tauri::async_runtime::spawn_blocking(move || {
        let state = app
            .try_state::<mcp_client::ClientState>()
            .ok_or_else(|| "missing mcp client state".to_string())?;
        state
            .call(
                &id,
                &tool,
                arguments.unwrap_or_else(|| serde_json::json!({})),
            )
            .map_err(|e| format!("{e:#}"))
    })
    .await
    .map_err(|e| format!("{e}"))?
}

#[tauri::command]
pub(crate) async fn mcp_client_disconnect_command(
    app: AppHandle,
    id: String,
) -> std::result::Result<bool, String> {
    tauri::async_runtime::spawn_blocking(move || {
        let state = app
            .try_state::<mcp_client::ClientState>()
            .ok_or_else(|| "missing mcp client state".to_string())?;
        Ok(state.disconnect(&id))
    })
    .await
    .map_err(|e| format!("{e}"))?
}

/// 页面侧数据变了(建档/撤销/外部工具集变化)→ 向 MCP 的 SSE 订阅者推 list_changed。
/// kind 只认三枚白名单;服务没起或没人订阅一律回 0,永不报错、永不吐令牌。
#[tauri::command]
pub(crate) fn agent_notify_command(
    app: AppHandle,
    kind: String,
) -> std::result::Result<usize, String> {
    let method = match kind.as_str() {
        "tools" => "notifications/tools/list_changed",
        "resources" => "notifications/resources/list_changed",
        "prompts" => "notifications/prompts/list_changed",
        _ => return Err("unknown notify kind".to_string()),
    };
    let Some(state) = app.try_state::<mcp_server::McpState>() else {
        return Ok(0);
    };
    let sent = state
        .inner
        .lock()
        .ok()
        .and_then(|inner| {
            inner
                .core
                .as_ref()
                .map(|core| core.notify(method, serde_json::json!({})))
        })
        .unwrap_or(0);
    Ok(sent)
}
