//! 更新事件通道、更新历史与日志轮转。

use super::*;

// v2.2.1 非阻塞升级事件:发到主窗口的独立通道(不接管 launcher 界面)。
// 镜像既有 __horosaPending* 模式:先存 pending,前端 UpdateNotifier 挂载时若已有 handler 立即调,否则挂载时补读 pending。
// 日志轮转保代:超限先 rename 成 <name>.1(覆盖旧 .1)再由调用方新建续写。
pub(crate) fn rotate_log_keep_one(path: &Path, max_bytes: u64) {
    let over = fs::metadata(path)
        .map(|m| m.len() > max_bytes)
        .unwrap_or(false);
    if !over {
        return;
    }
    let older = match path.extension().and_then(|e| e.to_str()) {
        Some(ext) => path.with_extension(format!("{ext}.1")),
        None => path.with_extension("1"),
    };
    let _ = fs::remove_file(&older);
    let _ = fs::rename(path, &older);
}

// 每行一事件 JSONL——「从哪版→哪版→结果」的耐久历史,与
// updater-events.log(瞬时事件镜像,2MB 保一代)互补:staged_ready/download_error/
// apply_begin/apply_runtime_ok/helper_handoff/install_confirmed/apply_failed/
// watchdog_rollback/downgrade_blocked/check_failed。>1MB 保尾 200 行重写(量级极小)。
pub(crate) fn update_history_path(app: &AppHandle) -> Option<PathBuf> {
    app.path()
        .app_data_dir()
        .ok()
        .map(|d| d.join("logs").join("update-history.jsonl"))
}

pub(crate) fn append_update_history_at(path: &Path, mut entry: serde_json::Value) {
    if let Some(parent) = path.parent() {
        let _ = fs::create_dir_all(parent);
    }
    let ms = SystemTime::now()
        .duration_since(UNIX_EPOCH)
        .map(|d| d.as_millis() as u64)
        .unwrap_or(0);
    if let Some(obj) = entry.as_object_mut() {
        obj.insert("ts".into(), serde_json::json!(ms));
        obj.entry("shellVersion")
            .or_insert(serde_json::json!(env!("CARGO_PKG_VERSION")));
    }
    if fs::metadata(path)
        .map(|m| m.len() > 1024 * 1024)
        .unwrap_or(false)
    {
        if let Ok(text) = fs::read_to_string(path) {
            let tail: Vec<&str> = text.lines().rev().take(200).collect();
            let keep: Vec<&str> = tail.into_iter().rev().collect();
            let _ = fs::write(path, format!("{}\n", keep.join("\n")));
        }
    }
    if let Ok(mut fh) = fs::OpenOptions::new().create(true).append(true).open(path) {
        use std::io::Write;
        let _ = writeln!(fh, "{entry}");
    }
}

pub(crate) fn append_update_history(app: &AppHandle, entry: serde_json::Value) {
    if let Some(path) = update_history_path(app) {
        append_update_history_at(&path, entry);
    }
}

fn emit_update_event_window(window: &WebviewWindow, json: &str) {
    let _ = window.eval(&format!(
        "window.__horosaPendingUpdateEvent = {json}; \
if (window.__horosaUpdateEvent) {{ window.__horosaUpdateEvent({json}); }}"
    ));
}

pub(crate) fn emit_update_event(app: &AppHandle, json: &str) {
    log_updater_event(app, json);
    if let Some(window) = app.get_webview_window(MAIN_WINDOW_LABEL) {
        emit_update_event_window(&window, json);
    }
}

/// updater 事件镜像:全部更新事件带时间戳落 logs/updater-events.log
/// (本地文件,零遥测)。根治「用户更新出问题拿不到证据」;也是
/// verify_update_experience_local.sh 四剧本的断言依据。HOROSA_UPDATER_EVENT_LOG=0 关。
fn log_updater_event(app: &AppHandle, json: &str) {
    if std::env::var("HOROSA_UPDATER_EVENT_LOG")
        .map(|v| v == "0")
        .unwrap_or(false)
    {
        return;
    }
    let Ok(dir) = app.path().app_data_dir() else {
        return;
    };
    let path = dir.join("logs").join("updater-events.log");
    if let Some(parent) = path.parent() {
        let _ = fs::create_dir_all(parent);
    }
    // 轮转保代:超 2MB rename→.1 再新建。旧实现 File::create 直接清零——恰在
    // 「更新反复失败刷满」最需要证据时把全史毁掉(违背 §5「第一证据」定位)。
    rotate_log_keep_one(&path, 2 * 1024 * 1024);
    let file = fs::OpenOptions::new().create(true).append(true).open(&path);
    if let Ok(mut fh) = file {
        let ms = SystemTime::now()
            .duration_since(UNIX_EPOCH)
            .map(|d| d.as_millis())
            .unwrap_or(0);
        use std::io::Write;
        let payload = json.trim_start().trim_start_matches('{');
        let _ = writeln!(fh, "{{\"ts\":{},{}", ms, payload);
    }
}

/// 安装(applying)阶段通知器(WS-1c):UpdateNotifier 显「正在安装更新」卡;
/// 旧前端不识别该 phase = 安全忽略,零适配义务。
pub(crate) fn make_applying_notifier(
    app: &AppHandle,
    root_index: usize,
    roots_total: usize,
) -> impl Fn(&str) + '_ {
    move |msg: &str| {
        let text = if roots_total > 1 {
            format!("[{}/{}] {}", root_index, roots_total, msg)
        } else {
            msg.to_string()
        };
        emit_update_event(
            app,
            &serde_json::json!({"phase":"applying","message":text}).to_string(),
        );
    }
}
