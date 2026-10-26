//! 剪贴板、外部链接、打印、更新 / 修复入口与系统设置跳转。

use super::*;

// 桌面剪贴板:webview 里 navigator.clipboard / execCommand 被拦,走原生剪贴板。
// 主路 arboard(NSPasteboard / CF_UNICODETEXT,Unicode 直写,跨平台同一实现);
// macOS 兜底 pbcopy——GUI .app 进程无 LANG/LC_CTYPE 时 pbcopy 按 MacRoman 解读 stdin
// (「技术」→「ÊäÄÊúØ」类乱码),必须显式钉 LC_CTYPE=UTF-8;绝对路径免 PATH 依赖。
pub(crate) struct DesktopClipboardState(pub(crate) Mutex<Option<arboard::Clipboard>>);

#[cfg(target_os = "macos")]
pub(crate) fn pbcopy_utf8_fallback(text: &str) -> std::result::Result<(), String> {
    use std::io::Write;
    let mut child = std::process::Command::new("/usr/bin/pbcopy")
        .env("LC_CTYPE", "UTF-8")
        .stdin(std::process::Stdio::piped())
        .spawn()
        .map_err(|err| format!("pbcopy spawn 失败: {err}"))?;
    {
        let stdin = child
            .stdin
            .as_mut()
            .ok_or_else(|| "pbcopy stdin 不可用".to_string())?;
        stdin
            .write_all(text.as_bytes())
            .map_err(|err| format!("pbcopy 写入失败: {err}"))?;
    }
    let status = child
        .wait()
        .map_err(|err| format!("pbcopy 等待失败: {err}"))?;
    if status.success() {
        Ok(())
    } else {
        Err(format!("pbcopy 退出码 {:?}", status.code()))
    }
}

#[tauri::command]
pub(crate) fn copy_text_to_clipboard_command(
    state: State<'_, DesktopClipboardState>,
    text: String,
) -> std::result::Result<(), String> {
    let native_err = {
        let mut guard = state.0.lock().map_err(|_| "剪贴板状态锁中毒".to_string())?;
        if guard.is_none() {
            // 构建期创建失败或上次写失败被重置 → 惰性重建(pasteboard 服务偶发异常可自愈)
            *guard = arboard::Clipboard::new().ok();
        }
        match guard.as_mut() {
            Some(clip) => match clip.set_text(text.clone()) {
                Ok(()) => return Ok(()),
                Err(err) => {
                    *guard = None;
                    format!("arboard 写入失败: {err}")
                }
            },
            None => "arboard 初始化失败".to_string(),
        }
    };
    #[cfg(target_os = "macos")]
    {
        return pbcopy_utf8_fallback(&text)
            .map_err(|fallback_err| format!("{native_err}; 兜底 {fallback_err}"));
    }
    #[cfg(not(target_os = "macos"))]
    {
        Err(native_err)
    }
}

// 桌面外链:webview 里 <a target="_blank"> / window.open 无新标签页可开 → 点了没反应;
// 走系统 `open` 在默认浏览器打开(macOS 自带、无新依赖,同 pbcopy 范式)。
// 安全:仅放行 http/https(挡 file:// javascript: 及以 - 开头的伪 flag),URL 作独立 arg 传入(不经 shell,免注入)。
#[tauri::command]
pub(crate) fn open_external_url_command(url: String) -> std::result::Result<(), String> {
    let target = url.trim();
    let lower = target.to_ascii_lowercase();
    if !(lower.starts_with("https://") || lower.starts_with("http://")) {
        return Err(format!("拒绝打开非 http(s) 链接: {target}"));
    }
    std::process::Command::new("open")
        .arg("--")
        .arg(target)
        .spawn()
        .map_err(|err| format!("open 外链失败: {err}"))?;
    Ok(())
}

#[tauri::command]
pub(crate) fn trigger_update_check_command(app: AppHandle) -> std::result::Result<(), String> {
    thread::spawn(move || {
        if let Err(err) = check_for_updates(app.clone()) {
            MessageDialog::new()
                .set_level(MessageLevel::Error)
                .set_title(shell_text("dlg.update_failed.title"))
                .set_description(format!("{err:#}"))
                .set_buttons(MessageButtons::Ok)
                .show();
        }
    });
    Ok(())
}

#[tauri::command]
pub(crate) fn trigger_runtime_repair_command(app: AppHandle) -> std::result::Result<(), String> {
    trigger_reinstall(app).map_err(|reason| reason.to_string())
}

#[tauri::command]
pub(crate) fn open_login_items_settings_command() -> std::result::Result<(), String> {
    Command::new("open")
        .arg("x-apple.systempreferences:com.apple.LoginItems-Settings.extension")
        .spawn()
        .map(|_| ())
        .map_err(|err| err.to_string())
}
