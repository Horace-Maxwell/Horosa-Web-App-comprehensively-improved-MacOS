//! 窗口:状态持久化与复原、实例锁与角色、主窗 / 次窗构建、缩放。

use super::*;

#[cfg(target_os = "macos")]
pub(crate) const LEGACY_MACOS_WINDOW_DEFAULT_KEYS: [&str; 4] = [
    "NSWindow Frame main-workspace",
    "NSSplitView Subview Frames main-workspace, SidebarNavigationSplitView",
    "NSWindow Frame SwiftUI.ModifiedContent<SwiftUI.ModifiedContent<Horosa.RootWorkspaceView, SwiftUI._EnvironmentKeyWritingModifier<Swift.Optional<Horosa.AppModel>>>, SwiftUI._FlexFrameLayout>-1-AppWindow-1",
    "NSSplitView Subview Frames SwiftUI.ModifiedContent<SwiftUI.ModifiedContent<Horosa.RootWorkspaceView, SwiftUI._EnvironmentKeyWritingModifier<Swift.Optional<Horosa.AppModel>>>, SwiftUI._FlexFrameLayout>-1-AppWindow-1, SidebarNavigationSplitView",
];

#[derive(Debug, Clone, Serialize, Deserialize, Default)]
#[serde(rename_all = "camelCase")]
pub(crate) struct SavedWindowState {
    pub(crate) width: Option<f64>,
    pub(crate) height: Option<f64>,
    pub(crate) x: Option<f64>,
    pub(crate) y: Option<f64>,
    pub(crate) is_maximized: Option<bool>,
    #[serde(default)]
    pub(crate) state_version: Option<u8>,
    #[serde(default)]
    pub(crate) coordinate_space: Option<String>,
}

#[derive(Debug, Clone, Serialize, Deserialize, Default)]
#[serde(rename_all = "camelCase")]
pub(crate) struct WindowStateStore {
    pub(crate) main: SavedWindowState,
    pub(crate) preferences: SavedWindowState,
    pub(crate) diagnostics: SavedWindowState,
}

fn window_state_path(app: &AppHandle) -> Result<PathBuf> {
    let dir = app
        .path()
        .app_config_dir()
        .context("missing app_config_dir")?;
    ensure_dir(&dir)?;
    Ok(dir.join(WINDOW_STATE_FILE_NAME))
}

pub(crate) fn load_window_states(app: &AppHandle) -> WindowStateStore {
    let Ok(path) = window_state_path(app) else {
        return WindowStateStore::default();
    };
    fs::read_to_string(path)
        .ok()
        .and_then(|data| serde_json::from_str::<WindowStateStore>(&data).ok())
        .unwrap_or_default()
}

fn save_window_states(app: &AppHandle, states: &WindowStateStore) -> Result<()> {
    let path = window_state_path(app)?;
    fs::write(path, serde_json::to_string_pretty(states)?).context("save window state")
}

pub(crate) fn valid_scale_factor(scale_factor: f64) -> f64 {
    if scale_factor.is_finite() && scale_factor > 0.0 {
        scale_factor
    } else {
        1.0
    }
}

pub(crate) fn logical_value(value: f64, scale_factor: f64) -> f64 {
    value / valid_scale_factor(scale_factor)
}

fn state_uses_logical_coordinates(state: &SavedWindowState) -> bool {
    state.state_version.unwrap_or(0) >= WINDOW_STATE_SCHEMA_VERSION
        || state.coordinate_space.as_deref() == Some(WINDOW_STATE_COORDINATE_SPACE)
}

fn state_uses_inner_size(state: &SavedWindowState) -> bool {
    state.state_version.unwrap_or(0) >= WINDOW_STATE_SCHEMA_VERSION
}

#[cfg(target_os = "macos")]
fn migrate_legacy_outer_size_to_inner_size(state: &mut SavedWindowState) {
    if state_uses_inner_size(state) {
        return;
    }
    state.height = state.height.map(|height| {
        if height.is_finite() && height > MACOS_LEGACY_OUTER_TO_INNER_HEIGHT_DELTA {
            height - MACOS_LEGACY_OUTER_TO_INNER_HEIGHT_DELTA
        } else {
            height
        }
    });
}

#[cfg(not(target_os = "macos"))]
fn migrate_legacy_outer_size_to_inner_size(_state: &mut SavedWindowState) {}

fn should_migrate_legacy_window_state(
    state: &SavedWindowState,
    scale_factor: f64,
    monitor_width: Option<f64>,
    monitor_height: Option<f64>,
) -> bool {
    let scale_factor = valid_scale_factor(scale_factor);
    if state_uses_logical_coordinates(state) || scale_factor <= 1.0 {
        return false;
    }

    let width_limit = monitor_width.unwrap_or(2200.0) * 1.05;
    let height_limit = monitor_height.unwrap_or(1400.0) * 1.05;
    state
        .width
        .map(|width| width.is_finite() && width > width_limit)
        .unwrap_or(false)
        || state
            .height
            .map(|height| height.is_finite() && height > height_limit)
            .unwrap_or(false)
}

pub(crate) fn normalize_saved_window_state_for_apply(
    state: &SavedWindowState,
    scale_factor: f64,
    monitor_width: Option<f64>,
    monitor_height: Option<f64>,
) -> SavedWindowState {
    let mut next = state.clone();
    if should_migrate_legacy_window_state(state, scale_factor, monitor_width, monitor_height) {
        next.width = next.width.map(|value| logical_value(value, scale_factor));
        next.height = next.height.map(|value| logical_value(value, scale_factor));
        next.x = next.x.map(|value| logical_value(value, scale_factor));
        next.y = next.y.map(|value| logical_value(value, scale_factor));
    }
    migrate_legacy_outer_size_to_inner_size(&mut next);
    next.state_version = Some(WINDOW_STATE_SCHEMA_VERSION);
    next.coordinate_space = Some(WINDOW_STATE_COORDINATE_SPACE.to_string());
    next
}

fn current_monitor_logical_size(
    window: &WebviewWindow,
    scale_factor: f64,
) -> (Option<f64>, Option<f64>) {
    window
        .current_monitor()
        .ok()
        .flatten()
        .map(|monitor| {
            let size = monitor.size();
            (
                Some(logical_value(size.width as f64, scale_factor)),
                Some(logical_value(size.height as f64, scale_factor)),
            )
        })
        .unwrap_or((None, None))
}

pub(crate) fn effective_captured_maximized(
    raw_is_maximized: Option<bool>,
    width: Option<f64>,
    height: Option<f64>,
    monitor_width: Option<f64>,
    monitor_height: Option<f64>,
) -> Option<bool> {
    if raw_is_maximized != Some(true) {
        return raw_is_maximized;
    }

    let (Some(width), Some(height), Some(monitor_width), Some(monitor_height)) =
        (width, height, monitor_width, monitor_height)
    else {
        return raw_is_maximized;
    };
    if !width.is_finite()
        || !height.is_finite()
        || !monitor_width.is_finite()
        || !monitor_height.is_finite()
        || width <= 0.0
        || height <= 0.0
        || monitor_width <= 0.0
        || monitor_height <= 0.0
    {
        return raw_is_maximized;
    }

    let covers_monitor = width >= monitor_width * 0.92 && height >= monitor_height * 0.88;
    Some(covers_monitor)
}

fn finite_positive(value: f64) -> bool {
    value.is_finite() && value > 0.0
}

pub(crate) fn saved_launch_size(
    state: &SavedWindowState,
    fallback: (f64, f64),
    min_size: (f64, f64),
) -> (f64, f64) {
    if !state_uses_logical_coordinates(state) {
        return fallback;
    }

    let mut normalized = state.clone();
    migrate_legacy_outer_size_to_inner_size(&mut normalized);
    let (Some(width), Some(height)) = (normalized.width, normalized.height) else {
        return fallback;
    };
    if !finite_positive(width) || !finite_positive(height) {
        return fallback;
    }
    (width.max(min_size.0), height.max(min_size.1))
}

pub(crate) fn saved_launch_position(state: &SavedWindowState) -> Option<(f64, f64)> {
    if !state_uses_logical_coordinates(state) {
        return None;
    }
    let (Some(x), Some(y)) = (state.x, state.y) else {
        return None;
    };
    if !x.is_finite() || !y.is_finite() {
        return None;
    }
    Some((x, y))
}

fn capture_window_state(window: &WebviewWindow) -> SavedWindowState {
    let mut state = SavedWindowState::default();
    state.state_version = Some(WINDOW_STATE_SCHEMA_VERSION);
    state.coordinate_space = Some(WINDOW_STATE_COORDINATE_SPACE.to_string());
    let scale_factor = window.scale_factor().map(valid_scale_factor).unwrap_or(1.0);
    let (monitor_width, monitor_height) = current_monitor_logical_size(window, scale_factor);
    if let Ok(size) = window.inner_size() {
        state.width = Some(logical_value(size.width as f64, scale_factor));
        state.height = Some(logical_value(size.height as f64, scale_factor));
    }
    if let Ok(position) = window.outer_position() {
        state.x = Some(logical_value(position.x as f64, scale_factor));
        state.y = Some(logical_value(position.y as f64, scale_factor));
    }
    state.is_maximized = effective_captured_maximized(
        window.is_maximized().ok(),
        state.width,
        state.height,
        monitor_width,
        monitor_height,
    );
    state
}

fn apply_saved_window_state(window: &WebviewWindow, state: &SavedWindowState) {
    let scale_factor = window.scale_factor().map(valid_scale_factor).unwrap_or(1.0);
    let (monitor_width, monitor_height) = current_monitor_logical_size(window, scale_factor);
    let normalized =
        normalize_saved_window_state_for_apply(state, scale_factor, monitor_width, monitor_height);
    if let (Some(width), Some(height)) = (normalized.width, normalized.height) {
        let _ = window.set_size(Size::Logical(LogicalSize::new(width, height)));
    }
    if let (Some(x), Some(y)) = (normalized.x, normalized.y) {
        let _ = window.set_position(Position::Logical(LogicalPosition::new(x, y)));
        // 离屏防护:恢复坐标可能属于已拔掉的外接屏——与任一现有显示器都不相交就居中,
        // 否则窗口「消失」在不存在的屏幕坐标上,用户会以为应用没启动。
        let on_screen = window
            .outer_position()
            .ok()
            .zip(window.outer_size().ok())
            .zip(window.available_monitors().ok())
            .map(|((pos, size), monitors)| {
                monitors.iter().any(|monitor| {
                    let mp = monitor.position();
                    let ms = monitor.size();
                    let win_right = pos.x.saturating_add(size.width as i32);
                    let win_bottom = pos.y.saturating_add(size.height as i32);
                    let mon_right = mp.x.saturating_add(ms.width as i32);
                    let mon_bottom = mp.y.saturating_add(ms.height as i32);
                    pos.x < mon_right && win_right > mp.x && pos.y < mon_bottom && win_bottom > mp.y
                })
            })
            .unwrap_or(true);
        if !on_screen {
            let _ = window.center();
        }
    }
}

pub(crate) fn apply_main_window_launch_state(window: &WebviewWindow, state: &SavedWindowState) {
    apply_saved_window_state(window, state);
}

pub(crate) fn stabilize_main_window_after_navigation(
    app: AppHandle,
    window: WebviewWindow,
    state: SavedWindowState,
) {
    thread::spawn(move || {
        set_window_state_persistence_ready(&app, false);
        for delay_ms in [0_u64, 80, 240, 520, 960] {
            if delay_ms > 0 {
                thread::sleep(Duration::from_millis(delay_ms));
            }
            apply_main_window_launch_state(&window, &state);
        }
        thread::sleep(Duration::from_millis(500));
        set_window_state_persistence_ready(&app, true);
    });
}

pub(crate) fn emit_ready_and_stabilize(app: &AppHandle, window: &WebviewWindow, url: &str) {
    ledger_mark("rust.emit_ready", None);
    // 看门狗确认:达 ready = 当前槽健康,pending 归零;previous 槽后台回收(不占 ready 关键路径)。
    if let Some(health_path) = launch_health_path(app) {
        launch_health_confirm(&health_path);
    }
    {
        let app = app.clone();
        thread::spawn(move || cleanup_previous_slots(&app));
    }
    let state = load_window_states(app).main;
    emit_ready(window, url);
    stabilize_main_window_after_navigation(app.clone(), window.clone(), state);
    // 服务存活看门狗:每次达 ready 换代重启一条(旧线程按 generation 自退)。
    start_service_supervisor(app.clone());
    // [首启原生库预检] 没预检过的运行时,就绪后后台补做(不占就绪关键路径)。
    spawn_native_prewarm_after_ready(app);
}

pub(crate) fn set_window_state_persistence_ready(app: &AppHandle, ready: bool) {
    if let Some(state) = app.try_state::<AppState>() {
        state
            .window_state_persistence_ready
            .store(ready, Ordering::SeqCst);
    }
}

pub(crate) fn is_window_state_persistence_ready(app: &AppHandle) -> bool {
    app.try_state::<AppState>()
        .map(|state| state.window_state_persistence_ready.load(Ordering::SeqCst))
        .unwrap_or(true)
}

pub(crate) fn enable_window_state_persistence_after_launch(app: AppHandle) {
    thread::spawn(move || {
        thread::sleep(Duration::from_secs(3));
        set_window_state_persistence_ready(&app, true);
    });
}

pub(crate) fn persist_window_state_for_label(
    app: &AppHandle,
    label: &str,
    window: &WebviewWindow,
) -> Result<()> {
    let mut store = load_window_states(app);
    let state = capture_window_state(window);
    match label {
        MAIN_WINDOW_LABEL => store.main = state,
        PREFERENCES_WINDOW_LABEL => store.preferences = state,
        DIAGNOSTICS_WINDOW_LABEL => store.diagnostics = state,
        _ => return Ok(()),
    }
    save_window_states(app, &store)
}

pub(crate) fn persist_all_known_window_states(app: &AppHandle) {
    for label in [
        MAIN_WINDOW_LABEL,
        PREFERENCES_WINDOW_LABEL,
        DIAGNOSTICS_WINDOW_LABEL,
    ] {
        if let Some(window) = app.get_webview_window(label) {
            let _ = persist_window_state_for_label(app, label, &window);
        }
    }
}

#[cfg(target_os = "macos")]
pub(crate) fn configure_macos_native_window_restoration() {
    let _ = Command::new("/usr/bin/defaults")
        .args([
            "write",
            APP_IDENTIFIER,
            "ApplePersistenceIgnoreState",
            "-bool",
            "YES",
        ])
        .stdout(Stdio::null())
        .stderr(Stdio::null())
        .status();
    for key in LEGACY_MACOS_WINDOW_DEFAULT_KEYS {
        let _ = Command::new("/usr/bin/defaults")
            .args(["delete", APP_IDENTIFIER, key])
            .stdout(Stdio::null())
            .stderr(Stdio::null())
            .status();
    }
    let _ = Command::new("/usr/bin/defaults")
        .args(["synchronize", APP_IDENTIFIER])
        .stdout(Stdio::null())
        .stderr(Stdio::null())
        .status();
}

#[cfg(not(target_os = "macos"))]
pub(crate) fn configure_macos_native_window_restoration() {}

pub(crate) fn show_or_focus_window(window: &WebviewWindow) {
    let _ = window.unminimize();
    let _ = window.show();
    let _ = window.set_focus();
}

/// 主实例身份(与端口无关):本应用数据目录下一把进程锁,先拿到的进程就是主实例,进程退出锁自动释放。
/// 页面原先按端口推断(首选口 = 主实例):首选口被别的程序长期占着时,唯一开着的那个实例落在后继口,
/// 被当成独立实例 —— 影子副本与自动备份全停,还提示一个并不存在的「主窗口」。
/// 现在由壳层经初始化脚本告诉页面 window.__HOROSA_INSTANCE_ROLE__ = "primary" | "independent";
/// 锁文件都开不出来(数据目录异常)时不下结论,页面照旧按端口推断。
static INSTANCE_ROLE: std::sync::OnceLock<(Option<&'static str>, Option<File>)> =
    std::sync::OnceLock::new();

pub(crate) const PRIMARY_INSTANCE_LOCK_FILE: &str = ".primary-instance.lock";

/// 试拿进程锁:Ok(Some(文件)) = 拿到(文件活着锁就在);Ok(None) = 另一个进程正拿着;Err = 锁文件开不出来。
fn try_hold_instance_lock(path: &Path) -> std::io::Result<Option<File>> {
    use std::os::unix::fs::OpenOptionsExt;
    use std::os::unix::io::AsRawFd;
    if let Some(parent) = path.parent() {
        fs::create_dir_all(parent)?;
    }
    let file = std::fs::OpenOptions::new()
        .read(true)
        .write(true)
        .create(true)
        .mode(0o600)
        .open(path)?;
    if unsafe { libc::flock(file.as_raw_fd(), libc::LOCK_EX | libc::LOCK_NB) } == 0 {
        return Ok(Some(file));
    }
    let err = std::io::Error::last_os_error();
    if err.raw_os_error() == Some(libc::EWOULDBLOCK) {
        Ok(None)
    } else {
        Err(err)
    }
}

pub(crate) fn instance_role_for_lock(path: &Path) -> (Option<&'static str>, Option<File>) {
    match try_hold_instance_lock(path) {
        Ok(Some(file)) => (Some("primary"), Some(file)),
        Ok(None) => (Some("independent"), None),
        Err(_) => (None, None),
    }
}

fn instance_role(app: &AppHandle) -> Option<&'static str> {
    INSTANCE_ROLE
        .get_or_init(|| match app.path().app_data_dir() {
            Ok(dir) => instance_role_for_lock(&dir.join(PRIMARY_INSTANCE_LOCK_FILE)),
            Err(_) => (None, None),
        })
        .0
}

pub(crate) fn instance_role_init_script(role: &str) -> String {
    format!(
        r#"(() => {{
  try {{
    Object.defineProperty(window, "__HOROSA_INSTANCE_ROLE__", {{ value: "{role}", writable: false, configurable: false }});
  }} catch (_) {{
    try {{ window.__HOROSA_INSTANCE_ROLE__ = "{role}"; }} catch (_) {{}}
  }}
}})();"#
    )
}

// ── 导航闸(主窗口 / 次窗口):非本应用来源的导航一律拒绝,http(s) 外站转交系统浏览器 ──
// 页面侧外链已有单一出口(组件 ExternalLink + 文档级兜底),这里是壳层根闸:页面里漏网的链接 / 将来写的 location.href = 外站,
// 也换不掉应用界面。本应用来源 = 壳自带协议(tauri / asset / ipc)、页面内部文档(about / data / blob)、本机回环地址
// (静态服务端口动态分配,本机后端同在回环上)。CSP 的 frame-src 'self' 已挡住外站 iframe,所以这里看到的外站 http(s)
// 都是整页导航。
#[derive(Debug, Clone, PartialEq, Eq)]
pub(crate) enum NavigationDecision {
    Allow,
    Deny,
    OpenExternal(String),
}

fn is_loopback_host(host: &str) -> bool {
    let h = host
        .trim_start_matches('[')
        .trim_end_matches(']')
        .to_ascii_lowercase();
    h == "127.0.0.1" || h == "::1" || h == "localhost" || h.ends_with(".localhost")
}

pub(crate) fn navigation_decision(url: &tauri::Url) -> NavigationDecision {
    match url.scheme() {
        "tauri" | "asset" | "ipc" | "about" | "data" | "blob" => NavigationDecision::Allow,
        "http" | "https" => match url.host_str() {
            Some(h) if is_loopback_host(h) => NavigationDecision::Allow,
            Some(h) if !h.is_empty() => NavigationDecision::OpenExternal(url.as_str().to_string()),
            _ => NavigationDecision::Deny,
        },
        _ => NavigationDecision::Deny,
    }
}

// 同一地址 1.5 秒内只转交一次(一次点击可能连着来两次导航请求)
static LAST_EXTERNAL_NAV: Mutex<Option<(String, Instant)>> = Mutex::new(None);

pub(crate) fn navigation_gate(url: &tauri::Url) -> bool {
    apply_navigation_decision(navigation_decision(url))
}

/// 按判定放行 / 拦下;外站交系统浏览器(各窗口的导航闸共用这一条转交路径)
pub(crate) fn apply_navigation_decision(decision: NavigationDecision) -> bool {
    match decision {
        NavigationDecision::Allow => true,
        NavigationDecision::Deny => false,
        NavigationDecision::OpenExternal(target) => {
            let fresh = match LAST_EXTERNAL_NAV.lock() {
                Ok(mut last) => {
                    let dup = matches!(&*last, Some((u, at)) if *u == target && at.elapsed() < Duration::from_millis(1500));
                    *last = Some((target.clone(), Instant::now()));
                    !dup
                }
                Err(_) => true,
            };
            if fresh {
                let _ = open_external_url_command(target);
            }
            false
        }
    }
}

pub(crate) fn build_main_window(
    app: &AppHandle,
    state: &SavedWindowState,
) -> Result<WebviewWindow> {
    let size = saved_launch_size(state, MAIN_WINDOW_DEFAULT_SIZE, MAIN_WINDOW_MIN_SIZE);
    let mut builder =
        WebviewWindowBuilder::new(app, MAIN_WINDOW_LABEL, WebviewUrl::App("index.html".into()))
            .title(APP_NAME)
            .resizable(true)
            .inner_size(size.0, size.1)
            .min_inner_size(MAIN_WINDOW_MIN_SIZE.0, MAIN_WINDOW_MIN_SIZE.1)
            .initialization_script(DESKTOP_WINDOW_INIT_SCRIPT)
            .initialization_script(shell_script_init_script())
            // 🔴 页面载入完成后重打缩放(无害兜底,幂等):应用逻辑单源在 init script 的
            // __HOROSA_APPLY_SHELL_ZOOM;启动值另经 emit_ready 的 URL query 确定性送达。
            .on_page_load(|win, payload| {
                if matches!(payload.event(), tauri::webview::PageLoadEvent::Finished) {
                    let app = win.app_handle().clone();
                    let zoom = load_preferences(&app).zoom_level;
                    let _ = set_window_zoom(&app, zoom);
                }
            })
            // 关掉 tauri 的原生拖放处理器:它对每次拖放恒返回 true,wry(macOS)只在处理器返回 false 时
            // 才把拖放交还 WKWebView,页面永远收不到 HTML5 drop → 资料页 / AI 输入框的「拖入」在桌面版
            // 全部无反应。关掉后走 WebKit 原生拖放,网页 DataTransfer.files 正常;壳自身没有任何
            // drag-drop 事件消费方,零副作用。
            .disable_drag_drop_handler()
            .on_navigation(navigation_gate)
            .visible(false);
    if let Some(role) = instance_role(app) {
        builder = builder.initialization_script(instance_role_init_script(role));
    }
    if let Some((x, y)) = saved_launch_position(state) {
        builder = builder.position(x, y);
    } else {
        builder = builder.center();
    }
    builder.build().context("build main window")
}

fn create_secondary_window(
    app: &AppHandle,
    label: &str,
    title: &str,
    asset: &str,
    size: (f64, f64),
    min_size: (f64, f64),
) -> Result<WebviewWindow> {
    let states = load_window_states(app);
    let saved_state = match label {
        PREFERENCES_WINDOW_LABEL => Some(&states.preferences),
        DIAGNOSTICS_WINDOW_LABEL => Some(&states.diagnostics),
        _ => None,
    };
    let initial_size = saved_state
        .map(|state| saved_launch_size(state, size, min_size))
        .unwrap_or(size);
    let mut builder = WebviewWindowBuilder::new(app, label, WebviewUrl::App(asset.into()))
        .title(title)
        .resizable(true)
        .inner_size(initial_size.0, initial_size.1)
        .min_inner_size(min_size.0, min_size.1)
        .initialization_script(DESKTOP_WINDOW_INIT_SCRIPT)
        .initialization_script(shell_script_init_script())
        .on_navigation(navigation_gate)
        .visible(false);
    if let Some((x, y)) = saved_state.and_then(saved_launch_position) {
        builder = builder.position(x, y);
    } else {
        builder = builder.center();
    }
    let window = builder.build().context("build secondary window")?;
    match label {
        PREFERENCES_WINDOW_LABEL => apply_saved_window_state(&window, &states.preferences),
        DIAGNOSTICS_WINDOW_LABEL => apply_saved_window_state(&window, &states.diagnostics),
        _ => {}
    }
    Ok(window)
}

pub(crate) fn open_preferences_window(app: &AppHandle) -> Result<()> {
    if let Some(window) = app.get_webview_window(PREFERENCES_WINDOW_LABEL) {
        show_or_focus_window(&window);
        return Ok(());
    }
    let window = create_secondary_window(
        app,
        PREFERENCES_WINDOW_LABEL,
        &shell_text("win.preferences"),
        "settings.html",
        (760.0, 680.0),
        (680.0, 620.0),
    )?;
    show_or_focus_window(&window);
    Ok(())
}

pub(crate) fn open_diagnostics_window(app: &AppHandle) -> Result<()> {
    if let Some(window) = app.get_webview_window(DIAGNOSTICS_WINDOW_LABEL) {
        show_or_focus_window(&window);
        return Ok(());
    }
    let window = create_secondary_window(
        app,
        DIAGNOSTICS_WINDOW_LABEL,
        &shell_text("win.diagnostics"),
        "diagnostics.html",
        (840.0, 720.0),
        (720.0, 620.0),
    )?;
    show_or_focus_window(&window);
    Ok(())
}

pub(crate) fn open_main_window(app: &AppHandle) -> Result<()> {
    if let Some(window) = app.get_webview_window(MAIN_WINDOW_LABEL) {
        show_or_focus_window(&window);
        return Ok(());
    }

    set_window_state_persistence_ready(app, false);
    let state = load_window_states(app).main;
    let window = build_main_window(app, &state).context("recreate main window")?;
    apply_main_window_launch_state(&window, &state);
    set_window_zoom(app, load_preferences(app).zoom_level)?;
    if let Some(state) = app.try_state::<AppState>() {
        if let Ok(slot) = state.session.lock() {
            if let Some(session) = slot.as_ref() {
                emit_ready_and_stabilize(
                    app,
                    &window,
                    &frontend_url(session.web_port, session.backend_port, session.chart_port),
                );
            }
        }
    }
    show_or_focus_window(&window);
    enable_window_state_persistence_after_launch(app.clone());
    Ok(())
}

#[tauri::command]
pub(crate) fn reveal_special_path(app: AppHandle, kind: String) -> std::result::Result<(), String> {
    let paths = resolve_runtime_paths(&app).map_err(|err| format!("{err:#}"))?;
    let target = match kind.as_str() {
        "logs" => paths.logs_dir,
        "runtime" => paths.runtime_dir,
        _ => paths.app_data_dir,
    };
    ensure_dir(&target).map_err(|err| format!("{err:#}"))?;
    open_path(&target);
    Ok(())
}

#[tauri::command]
pub(crate) fn open_preferences_window_command(app: AppHandle) -> std::result::Result<(), String> {
    open_preferences_window(&app).map_err(|err| format!("{err:#}"))
}

#[tauri::command]
pub(crate) fn open_diagnostics_window_command(app: AppHandle) -> std::result::Result<(), String> {
    open_diagnostics_window(&app).map_err(|err| format!("{err:#}"))
}

pub(crate) fn open_path(path: &Path) {
    let _ = Command::new("open").arg(path).spawn();
}

pub(crate) fn clamp_zoom_level(value: f64) -> f64 {
    // [zoom-snap] ⌘± 为 f64 累加,历史 prefs 实锤出现 0.8999999999999999/1.0000000000000002;
    // 全部写入路径(启动加载/⌘±/⌘0/URL query 格式化)都流经本函数——吸到 0.1 档=单点根治,
    // 脏 prefs 下次启动即自愈,`v===1` 判等收到的是精确 1.0(菜单本就 0.1 步进,语义无损)。
    let snapped = (value * 10.0).round() / 10.0;
    snapped.clamp(MIN_ZOOM, MAX_ZOOM)
}

pub(crate) fn max_zoom_for_width(logical_width: f64) -> f64 {
    if !logical_width.is_finite() || logical_width <= 0.0 {
        return MAX_ZOOM;
    }
    let cap = (logical_width / MIN_LAYOUT_WIDTH_CSS_PX * 10.0).floor() / 10.0;
    cap.clamp(MIN_ZOOM, MAX_ZOOM)
}

pub(crate) fn window_zoom_cap(app: &AppHandle) -> (f64, f64) {
    // 回 (上限, 窗口逻辑宽);拿不到窗口 / 尺寸时按无封顶(MAX_ZOOM)处理,绝不因量不到而把用户缩回去。
    let window = match app.get_webview_window(MAIN_WINDOW_LABEL) {
        Some(window) => window,
        None => return (MAX_ZOOM, 0.0),
    };
    let scale = window.scale_factor().unwrap_or(1.0);
    match window.inner_size() {
        Ok(size) if scale > 0.0 => {
            let width = size.width as f64 / scale;
            (max_zoom_for_width(width), width)
        }
        _ => (MAX_ZOOM, 0.0),
    }
}

pub(crate) fn set_window_zoom(app: &AppHandle, zoom: f64) -> Result<()> {
    let requested = clamp_zoom_level(zoom);
    let window = app
        .get_webview_window(MAIN_WINDOW_LABEL)
        .context("main window missing for zoom")?;
    // 超过本窗宽度的上限 → 停在上限并让页面说明原因(⌘+ 不再放大;拉宽窗口 / 换大屏可继续)。
    let (cap, width) = window_zoom_cap(app);
    let clamped = if requested > cap { cap } else { requested };
    if requested > cap {
        let _ = window.eval(&format!(
            "if(window.__HOROSA_SHELL_ZOOM_CAPPED){{window.__HOROSA_SHELL_ZOOM_CAPPED({},{});}}",
            cap, width
        ));
    }
    // 🔴 缩放走页面内 CSS zoom(原生 pageZoom 恒 1.0):pageZoom≠1 时 clientHeight(物理域)
    // 与 100vh(布局域)劈叉,量高链错位=底空+可平移空间(真机实锤)。应用逻辑单源在
    // init script 的 __HOROSA_APPLY_SHELL_ZOOM(每个 document 必挂,导航后不丢);启动值
    // 另经 emit_ready 的 URL query(shellZoom)确定性送达页面 origin,global.js 先行同构应用。
    window.set_zoom(1.0)?;
    let _ = window.eval(&format!(
        "if(window.__HOROSA_APPLY_SHELL_ZOOM){{window.__HOROSA_APPLY_SHELL_ZOOM({});}}",
        clamped
    ));
    if let Some(state) = app.try_state::<AppState>() {
        if let Ok(mut slot) = state.zoom_level.lock() {
            *slot = clamped;
        }
    }
    // #22：持久化缩放到 preferences.json，重启恢复（修复字号重开复位）
    let mut prefs = load_preferences(app);
    prefs.zoom_level = clamped;
    let _ = save_preferences(app, &prefs);
    Ok(())
}

pub(crate) fn adjust_window_zoom(app: &AppHandle, delta: f64) -> Result<()> {
    let current = if let Some(state) = app.try_state::<AppState>() {
        if let Ok(slot) = state.zoom_level.lock() {
            *slot
        } else {
            DEFAULT_ZOOM
        }
    } else {
        DEFAULT_ZOOM
    };
    set_window_zoom(app, current + delta)
}
