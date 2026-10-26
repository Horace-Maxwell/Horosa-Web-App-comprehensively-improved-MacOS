//! 壳层原生文案(菜单栏 / rfd 原生对话框 / 系统通知横幅 / 原生窗口标题)随界面简繁。
//!
//! 文案单源 = `shell_strings.json`(id → 简体 / 繁体,繁体由表给出,壳里不做简繁转换;繁体一栏由前端 jest 与页面显示层转换器逐字比对)。
//! 页面开机与切换简繁时调 `set_shell_script_command` 告诉壳当前档;壳记下(下次开机首帧前就按这一档建菜单)并重建菜单。
//! 对话框在弹出那一刻按当前档取文案。壳自带三页(启动器 / 偏好 / 诊断)的网页文字由 `web/shell_script.js` 按档就地转(建窗注入档位 + 切换时推送)。壳自己拼进去的动态细节(错误原文、更新说明)不在表里,照原样显示。

use super::*;

const SHELL_STRINGS_JSON: &str = include_str!("../shell_strings.json");
const SHELL_SCRIPT_FILE: &str = "shell_script";

#[derive(Debug, Clone, Deserialize)]
struct ShellString {
    hans: String,
    hant: String,
}

static SHELL_TABLE: std::sync::OnceLock<HashMap<String, ShellString>> = std::sync::OnceLock::new();
static SHELL_HANT: AtomicBool = AtomicBool::new(false);

fn shell_table() -> &'static HashMap<String, ShellString> {
    SHELL_TABLE.get_or_init(|| {
        let raw: HashMap<String, serde_json::Value> =
            serde_json::from_str(SHELL_STRINGS_JSON).unwrap_or_default();
        raw.into_iter()
            .filter(|(k, _)| !k.starts_with('_'))
            .filter_map(|(k, v)| {
                serde_json::from_value::<ShellString>(v)
                    .ok()
                    .map(|s| (k, s))
            })
            .collect()
    })
}

pub(crate) fn shell_script_is_hant() -> bool {
    SHELL_HANT.load(Ordering::Relaxed)
}

pub(crate) fn set_shell_script_hant(hant: bool) -> bool {
    SHELL_HANT.swap(hant, Ordering::Relaxed) != hant
}

/// 按当前档取文案;表里没有这个 id 时回 id 本身(单测保证所有调用点的 id 都在表里)
pub(crate) fn shell_text(id: &str) -> String {
    shell_text_in(id, shell_script_is_hant())
}

pub(crate) fn shell_text_in(id: &str, hant: bool) -> String {
    match shell_table().get(id) {
        Some(s) => {
            if hant {
                s.hant.clone()
            } else {
                s.hans.clone()
            }
        }
        None => id.to_string(),
    }
}

/// 模板 + 占位符一次替换(`{key}`;代入的内容里再出现的花括号不会被二次替换)
pub(crate) fn shell_text_fmt(id: &str, args: &[(&str, &str)]) -> String {
    fill_placeholders(&shell_text(id), args)
}

pub(crate) fn fill_placeholders(template: &str, args: &[(&str, &str)]) -> String {
    let mut out = String::with_capacity(template.len() + 32);
    let mut rest = template;
    while let Some(open) = rest.find('{') {
        out.push_str(&rest[..open]);
        let after = &rest[open + 1..];
        match after.find('}') {
            Some(close) => {
                let key = &after[..close];
                if let Some((_, v)) = args.iter().find(|(k, _)| *k == key) {
                    out.push_str(v);
                } else {
                    out.push('{');
                    out.push_str(key);
                    out.push('}');
                }
                rest = &after[close + 1..];
            }
            None => {
                out.push_str(&rest[open..]);
                rest = "";
            }
        }
    }
    out.push_str(rest);
    out
}

fn shell_script_path(app: &AppHandle) -> Option<PathBuf> {
    app.path()
        .app_config_dir()
        .ok()
        .map(|d| d.join(SHELL_SCRIPT_FILE))
}

/// 开机时读上次记下的档(菜单在首帧前就按这一档建);读不到 = 简体
pub(crate) fn load_persisted_shell_script(app: &AppHandle) {
    let hant = shell_script_path(app)
        .and_then(|p| fs::read_to_string(p).ok())
        .map(|s| s.trim() == "hant")
        .unwrap_or(false);
    set_shell_script_hant(hant);
}

fn shell_script_mode_str() -> &'static str {
    if shell_script_is_hant() {
        "hant"
    } else {
        "hans"
    }
}

/// 壳自带三页(启动器 / 偏好设置 / 诊断中心)不在主应用里,由 `web/shell_script.js` 就地转繁体:
/// 建窗时经初始化脚本把当前档交给页面(首帧前就知道,免得先闪简体)
pub(crate) fn shell_script_init_script() -> String {
    format!(
        "window.__HOROSA_SHELL_SCRIPT = {:?};",
        shell_script_mode_str()
    )
}

/// 页面载入后再确认一次档位(建窗注入的档在页面重新载入时可能已过时)
#[tauri::command]
pub(crate) fn get_shell_script_command() -> String {
    shell_script_mode_str().to_string()
}

/// 切换简繁时,已开着的壳自带页面跟着换(主窗口此刻若是主应用,只是写一个全局量,不影响主应用自己的显示层)
fn push_shell_script_to_pages(app: &AppHandle) {
    let m = shell_script_mode_str();
    let js = format!(
        "window.__HOROSA_SHELL_SCRIPT = {m:?}; if (window.HorosaShellScript) window.HorosaShellScript.setMode({m:?});"
    );
    for label in [
        MAIN_WINDOW_LABEL,
        PREFERENCES_WINDOW_LABEL,
        DIAGNOSTICS_WINDOW_LABEL,
    ] {
        if let Some(window) = app.get_webview_window(label) {
            let _ = window.eval(&js);
        }
    }
}

/// 页面告诉壳当前界面简繁档(hans / hant):记下、重建菜单。档没变时什么都不做
#[tauri::command]
pub(crate) fn set_shell_script_command(
    app: AppHandle,
    mode: String,
) -> std::result::Result<(), String> {
    let hant = match mode.as_str() {
        "hant" => true,
        "hans" => false,
        other => return Err(format!("unknown script mode: {other}")),
    };
    if !set_shell_script_hant(hant) {
        return Ok(());
    }
    if let Some(path) = shell_script_path(&app) {
        if let Some(dir) = path.parent() {
            let _ = fs::create_dir_all(dir);
        }
        let _ = fs::write(path, if hant { "hant" } else { "hans" });
    }
    push_shell_script_to_pages(&app);
    let menu = build_menu(&app).map_err(|e| format!("build menu: {e}"))?;
    app.set_menu(menu).map_err(|e| format!("set menu: {e}"))?;
    // 已开着的次窗口标题跟着换(新开的窗口建窗时就按当前档取)
    for (label, id) in [
        (PREFERENCES_WINDOW_LABEL, "win.preferences"),
        (DIAGNOSTICS_WINDOW_LABEL, "win.diagnostics"),
    ] {
        if let Some(window) = app.get_webview_window(label) {
            let _ = window.set_title(&shell_text(id));
        }
    }
    Ok(())
}
