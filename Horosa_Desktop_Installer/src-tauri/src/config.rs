//! 常量、发布配置、偏好(读写与页面载荷)、安装来源。

use super::*;

pub(crate) const MAIN_WINDOW_LABEL: &str = "main";
pub(crate) const PREFERENCES_WINDOW_LABEL: &str = "preferences";
pub(crate) const DIAGNOSTICS_WINDOW_LABEL: &str = "diagnostics";
pub(crate) const MENU_CHECK_UPDATES: &str = "check_updates";
pub(crate) const MENU_REINSTALL_RUNTIME: &str = "reinstall_runtime";
pub(crate) const MENU_RESTART_SERVICES: &str = "restart_local_services";
pub(crate) const MENU_RELOCATE_APP: &str = "relocate_app";
pub(crate) const MENU_OPEN_PREFERENCES: &str = "open_preferences";
pub(crate) const MENU_SHOW_MAIN_WINDOW: &str = "show_main_window";
pub(crate) const MENU_SHOW_DIAGNOSTICS: &str = "show_diagnostics";
pub(crate) const MENU_OPEN_LOGS: &str = "open_logs";
pub(crate) const MENU_OPEN_DATA: &str = "open_data";
pub(crate) const MENU_OPEN_RUNTIME: &str = "open_runtime";
pub(crate) const MENU_RELOAD_MAIN: &str = "reload_main";
pub(crate) const MENU_OPEN_RELEASES: &str = "open_releases";
pub(crate) const MENU_ZOOM_IN: &str = "zoom_in";
pub(crate) const MENU_ZOOM_OUT: &str = "zoom_out";
pub(crate) const MENU_ZOOM_RESET: &str = "zoom_reset";
pub(crate) const DEFAULT_ZOOM: f64 = 1.0;
pub(crate) const MIN_ZOOM: f64 = 0.7;
pub(crate) const MAX_ZOOM: f64 = 1.8;
// 布局视口宽 = 窗口逻辑宽 ÷ zoom,低于此值三栏页主盘会被两侧栏挤成一条缝(小窗 × 极档实报)。
// 上限 = floor(窗口逻辑宽 / 1000, 0.1 档) 再夹进 [MIN_ZOOM, MAX_ZOOM]:1440 宽 → 1.4;1728 → 1.7;3008 → 1.8;最小主窗 1180 → 1.1。
pub(crate) const MIN_LAYOUT_WIDTH_CSS_PX: f64 = 1000.0;
pub(crate) const ZOOM_STEP: f64 = 0.1;

const DEFAULT_RUNTIME_ASSET_NAME: &str = "horosa-runtime-macos-arm64.tar.gz";
const DEFAULT_DESKTOP_ASSET_NAME: &str = "Horosa-Desktop-macos-arm64.zip";
const DEFAULT_DESKTOP_PKG_NAME: &str = "Horosa-Installer-macos-arm64.pkg";
const DEFAULT_DESKTOP_PKG_ZIP_NAME: &str = "Horosa-Installer-macos-arm64-pkg.zip";
const DEFAULT_DESKTOP_OFFLINE_PKG_NAME: &str = "Horosa-Installer-macos-arm64-offline.pkg";
const DEFAULT_DESKTOP_OFFLINE_PKG_ZIP_NAME: &str = "Horosa-Installer-macos-arm64-offline-pkg.zip";
const DEFAULT_UPDATE_MANIFEST_NAME: &str = "horosa-latest.json";
const DEFAULT_SUPPORTED_ARCH: &str = "arm64";
const DEFAULT_RELEASE_TAG_PREFIX: &str = "v";
pub(crate) const DOWNLOAD_MAX_ATTEMPTS: usize = 4;
pub(crate) const DEFAULT_FRONTEND_PORT: u16 = 38991;
// 修法1:backend/chart 端口冲突时最多换口重试的总尝试次数。
pub(crate) const PORT_RETRY_MAX: u32 = 5;
pub(crate) const UPDATE_COMPLETE_MARKER_NAME: &str = "update-complete.txt";
const PREFERENCES_FILE_NAME: &str = "preferences.json";
pub(crate) const WINDOW_STATE_FILE_NAME: &str = "window-state.json";
pub(crate) const WINDOW_STATE_SCHEMA_VERSION: u8 = 3;
pub(crate) const WINDOW_STATE_COORDINATE_SPACE: &str = "logical";
pub(crate) const MAIN_WINDOW_DEFAULT_SIZE: (f64, f64) = (1480.0, 960.0);
pub(crate) const MAIN_WINDOW_MIN_SIZE: (f64, f64) = (1180.0, 760.0);
#[cfg(target_os = "macos")]
pub(crate) const MACOS_LEGACY_OUTER_TO_INNER_HEIGHT_DELTA: f64 = 28.0;
pub(crate) const AI_ANALYSIS_IMPORT_EXTENSIONS: [&str; 6] =
    ["txt", "md", "markdown", "doc", "docx", "pdf"];
pub(crate) const AI_ANALYSIS_BACKUP_EXTENSIONS: [&str; 1] = ["zip"];

#[allow(dead_code)]
#[derive(Debug, Clone, Deserialize)]
pub(crate) struct ReleaseConfig {
    #[serde(rename = "repoOwner")]
    pub(crate) repo_owner: String,
    #[serde(rename = "repoName")]
    pub(crate) repo_name: String,
    #[serde(rename = "runtimeVersion")]
    pub(crate) runtime_version: String,
    #[serde(rename = "runtimeAssetName")]
    pub(crate) runtime_asset_name: String,
    #[serde(rename = "desktopAssetName")]
    pub(crate) desktop_asset_name: String,
    #[serde(rename = "desktopPkgName")]
    desktop_pkg_name: String,
    #[serde(rename = "desktopPkgZipName")]
    desktop_pkg_zip_name: String,
    #[serde(
        rename = "desktopOfflinePkgName",
        default = "default_desktop_offline_pkg_name"
    )]
    pub(crate) desktop_offline_pkg_name: String,
    #[serde(
        rename = "desktopOfflinePkgZipName",
        default = "default_desktop_offline_pkg_zip_name"
    )]
    pub(crate) desktop_offline_pkg_zip_name: String,
    #[serde(rename = "updateManifestName")]
    pub(crate) update_manifest_name: String,
    #[serde(rename = "primaryDownload", default)]
    primary_download: String,
    #[serde(rename = "supportedArch", default = "default_supported_arch")]
    supported_arch: String,
    #[serde(rename = "releaseTagPrefix")]
    pub(crate) release_tag_prefix: String,
    #[serde(rename = "appName")]
    pub(crate) app_name: String,
}

#[derive(Debug, Clone, Serialize, Deserialize)]
#[serde(rename_all = "camelCase")]
pub(crate) struct AppPreferences {
    pub(crate) auto_check_updates: bool,
    pub(crate) show_status_notifications: bool,
    compact_launcher_layout: bool,
    enable_experimental_features: bool,
    pub(crate) always_review_before_replace: bool,
    #[serde(default = "default_zoom")]
    pub(crate) zoom_level: f64,
    // AI 助手·行动能力总开关的壳侧镜像(页面开关同步写入;默认关)与外部智能体服务子开关(默认关)。
    // 二者皆真 + HOROSA_MCP_SERVER!=0 才起本机 MCP 监听;偏好窗保存不触碰这两键(save_preferences_command 保留现值)。
    #[serde(default)]
    pub(crate) agent_enabled: bool,
    #[serde(default)]
    pub(crate) mcp_server_enabled: bool,
    // 通知外部脚本钩(仅桌面壳、默认关、用户在界面确认后才开):路径须绝对·常规文件·可执行·非全员可写·位于 $HOME 或 /usr/local/bin;
    // 触发时 Command::new(path).arg(json) 零 shell、10s 超时 kill、复用桌面通知限流;env HOROSA_NOTIFY_HOOK=0 一票否决。
    #[serde(default)]
    pub(crate) notify_hook_enabled: bool,
    #[serde(default)]
    pub(crate) notify_hook_path: String,
    // 定时任务:壳侧 60 秒哑心跳的开关镜像(页面子开关同步写入;默认关=线程零动作);偏好窗保存不触碰。
    #[serde(default)]
    pub(crate) scheduler_enabled: bool,
    // 外部客户端策略「每分钟调用上限」的壳侧镜像(页面 1..600 同步写入;缺省 60);偏好窗保存不触碰。
    #[serde(default = "default_mcp_calls_per_minute")]
    pub(crate) mcp_calls_per_minute: u32,
    // [REST] 本机 REST 接口(/api/v1,与 MCP 同端口同令牌)子开关:缺省关;偏好窗保存不触碰(save_preferences_command 保留现值)
    #[serde(default)]
    pub(crate) mcp_rest_enabled: bool,
}

fn default_zoom() -> f64 {
    DEFAULT_ZOOM
}

impl Default for AppPreferences {
    fn default() -> Self {
        Self {
            auto_check_updates: true,
            show_status_notifications: true,
            compact_launcher_layout: false,
            enable_experimental_features: false,
            always_review_before_replace: true,
            zoom_level: DEFAULT_ZOOM,
            agent_enabled: false,
            mcp_server_enabled: false,
            notify_hook_enabled: false,
            notify_hook_path: String::new(),
            scheduler_enabled: false,
            mcp_calls_per_minute: 60,
            mcp_rest_enabled: false,
        }
    }
}

fn default_mcp_calls_per_minute() -> u32 {
    60
}

#[derive(Debug, Clone, Copy, Serialize, Deserialize, PartialEq, Eq)]
#[serde(rename_all = "snake_case")]
pub(crate) enum InstallSource {
    DmgOnline,
    PkgOnline,
    PkgOffline,
    Unknown,
}

#[derive(Debug, Clone, Serialize, Deserialize)]
#[serde(rename_all = "camelCase")]
pub(crate) struct InstallSourceMarker {
    pub(crate) source: InstallSource,
    pub(crate) installed_at: Option<u64>,
    pub(crate) runtime_version: Option<String>,
    pub(crate) app_version: Option<String>,
    /// 离线安装包缓存进共享 downloads 的运行时归档名与 sha256(安装器按包内校验值写;旧记录没有 = 不核 sha)
    #[serde(default)]
    pub(crate) runtime_archive_name: Option<String>,
    #[serde(default)]
    pub(crate) runtime_archive_sha256: Option<String>,
}

#[derive(Debug, Clone, Serialize)]
#[serde(rename_all = "camelCase")]
pub(crate) struct PreferencesPayload {
    pub(crate) preferences: AppPreferences,
    pub(crate) app_version: String,
    pub(crate) runtime_version: Option<String>,
    pub(crate) app_data_dir: String,
    pub(crate) logs_dir: String,
    pub(crate) runtime_dir: String,
    supported_arch: String,
    primary_download: String,
    /// 共享运行环境权限提示(早先安装包留下所有账户可写的旧树;None = 没问题)
    shared_runtime_warning: Option<String>,
    /// 提示里那几处归本账户所有:设置页给「收紧共享权限」按钮(用户点了才在后台收紧;读本页不改任何权限)
    shared_runtime_fixable: bool,
}

fn default_supported_arch() -> String {
    DEFAULT_SUPPORTED_ARCH.to_string()
}

fn default_desktop_offline_pkg_name() -> String {
    DEFAULT_DESKTOP_OFFLINE_PKG_NAME.to_string()
}

fn default_desktop_offline_pkg_zip_name() -> String {
    DEFAULT_DESKTOP_OFFLINE_PKG_ZIP_NAME.to_string()
}

fn fallback_release_config(app: &AppHandle) -> ReleaseConfig {
    ReleaseConfig {
        repo_owner: DEFAULT_REPO_OWNER.to_string(),
        repo_name: DEFAULT_REPO_NAME.to_string(),
        runtime_version: app.package_info().version.to_string(),
        runtime_asset_name: DEFAULT_RUNTIME_ASSET_NAME.to_string(),
        desktop_asset_name: DEFAULT_DESKTOP_ASSET_NAME.to_string(),
        desktop_pkg_name: DEFAULT_DESKTOP_PKG_NAME.to_string(),
        desktop_pkg_zip_name: DEFAULT_DESKTOP_PKG_ZIP_NAME.to_string(),
        desktop_offline_pkg_name: DEFAULT_DESKTOP_OFFLINE_PKG_NAME.to_string(),
        desktop_offline_pkg_zip_name: DEFAULT_DESKTOP_OFFLINE_PKG_ZIP_NAME.to_string(),
        update_manifest_name: DEFAULT_UPDATE_MANIFEST_NAME.to_string(),
        primary_download: DEFAULT_DESKTOP_OFFLINE_PKG_NAME.to_string(),
        supported_arch: DEFAULT_SUPPORTED_ARCH.to_string(),
        release_tag_prefix: DEFAULT_RELEASE_TAG_PREFIX.to_string(),
        app_name: APP_NAME.to_string(),
    }
}

fn preferences_path(app: &AppHandle) -> Result<PathBuf> {
    let dir = app
        .path()
        .app_config_dir()
        .context("missing app_config_dir")?;
    ensure_dir(&dir)?;
    Ok(dir.join(PREFERENCES_FILE_NAME))
}

pub(crate) fn load_preferences(app: &AppHandle) -> AppPreferences {
    let Ok(path) = preferences_path(app) else {
        return AppPreferences::default();
    };
    fs::read_to_string(path)
        .ok()
        .and_then(|data| serde_json::from_str::<AppPreferences>(&data).ok())
        .unwrap_or_default()
}

pub(crate) fn save_preferences(app: &AppHandle, preferences: &AppPreferences) -> Result<()> {
    let path = preferences_path(app)?;
    fs::write(path, serde_json::to_string_pretty(preferences)?).context("save preferences")
}

pub(crate) fn shared_assets_root() -> PathBuf {
    shared_runtime_root()
        .parent()
        .map(Path::to_path_buf)
        .unwrap_or_else(|| PathBuf::from("/Users/Shared/Horosa"))
}

pub(crate) fn shared_downloads_dir() -> PathBuf {
    shared_assets_root().join("downloads")
}

pub(crate) fn install_source_marker_path() -> PathBuf {
    std::env::var_os("HOROSA_INSTALL_SOURCE_PATH")
        .map(PathBuf::from)
        .unwrap_or_else(|| shared_assets_root().join("install-source.json"))
}

pub(crate) fn load_install_source_marker() -> Option<InstallSourceMarker> {
    let path = install_source_marker_path();
    let data = fs::read_to_string(path).ok()?;
    serde_json::from_str(&data).ok()
}

pub(crate) fn current_install_source(config: &ReleaseConfig) -> Option<InstallSource> {
    let marker = load_install_source_marker()?;
    if marker.source == InstallSource::PkgOffline
        && offline_install_marker_is_current(&marker, &config.runtime_version)
    {
        return Some(InstallSource::PkgOffline);
    }
    Some(marker.source)
}

pub(crate) fn source_label(source: InstallSource) -> &'static str {
    match source {
        InstallSource::PkgOffline => "离线安装包",
        InstallSource::PkgOnline => "在线安装包",
        InstallSource::DmgOnline => "DMG 安装",
        InstallSource::Unknown => "当前安装",
    }
}

fn build_preferences_payload(app: &AppHandle) -> Result<PreferencesPayload> {
    let config = load_release_config(app)?;
    let paths = resolve_runtime_paths(app)?;
    let (shared_warning, shared_fixable) = inspect_shared_tree().warning();
    Ok(PreferencesPayload {
        preferences: load_preferences(app),
        app_version: env!("CARGO_PKG_VERSION").to_string(),
        runtime_version: local_runtime_version(app),
        app_data_dir: paths.app_data_dir.to_string_lossy().to_string(),
        logs_dir: paths.logs_dir.to_string_lossy().to_string(),
        runtime_dir: paths.runtime_dir.to_string_lossy().to_string(),
        supported_arch: config.supported_arch,
        primary_download: config.primary_download,
        shared_runtime_warning: shared_warning,
        shared_runtime_fixable: shared_fixable,
    })
}

#[tauri::command]
pub(crate) fn load_preferences_payload(
    app: AppHandle,
) -> std::result::Result<PreferencesPayload, String> {
    build_preferences_payload(&app).map_err(|err| format!("{err:#}"))
}

#[tauri::command]
pub(crate) fn save_preferences_command(
    app: AppHandle,
    preferences: AppPreferences,
) -> std::result::Result<(), String> {
    // 偏好窗的载荷不含助手/外部智能体两键(serde 缺省=false 会把已开的开关静默关掉)→ 保留现值
    let current = load_preferences(&app);
    let mut next = preferences;
    next.agent_enabled = current.agent_enabled;
    next.mcp_server_enabled = current.mcp_server_enabled;
    next.scheduler_enabled = current.scheduler_enabled;
    next.notify_hook_enabled = current.notify_hook_enabled;
    next.notify_hook_path = current.notify_hook_path.clone();
    next.mcp_calls_per_minute = current.mcp_calls_per_minute;
    next.mcp_rest_enabled = current.mcp_rest_enabled;
    save_preferences(&app, &next).map_err(|err| format!("{err:#}"))
}

pub(crate) fn load_release_config(app: &AppHandle) -> Result<ReleaseConfig> {
    let resource_dir = app.path().resource_dir().context("missing resource dir")?;
    // 发行二进制只从 bundle 资源读 release_config.json。源码树相对路径仅 debug 构建保留
    // (方便从源码直接 `cargo run`);若编进 release,env!("CARGO_MANIFEST_DIR") 会把构建机
    // 绝对路径(含用户名与仓库目录名)烤进二进制常量,--remap-path-prefix 也去不掉。
    #[allow(unused_mut)] // release 构建无下方 debug-only push,mut 会被判未用
    let mut candidates = vec![
        resource_dir.join("_up_/config/release_config.json"),
        resource_dir.join("config/release_config.json"),
    ];
    #[cfg(debug_assertions)]
    candidates
        .push(PathBuf::from(env!("CARGO_MANIFEST_DIR")).join("../config/release_config.json"));
    let mut parse_errors = Vec::new();
    for path in candidates {
        if path.exists() {
            match fs::read_to_string(&path) {
                Ok(data) => match serde_json::from_str::<ReleaseConfig>(&data) {
                    Ok(mut config) => {
                        let runtime_version = config.runtime_version.trim().to_string();
                        if runtime_version.is_empty()
                            || runtime_version.eq_ignore_ascii_case("auto")
                            || runtime_version.eq_ignore_ascii_case("same-as-app")
                        {
                            config.runtime_version = app.package_info().version.to_string();
                        }
                        if config.primary_download.trim().is_empty() {
                            config.primary_download = DEFAULT_DESKTOP_OFFLINE_PKG_NAME.to_string();
                        }
                        if config.supported_arch.trim().is_empty() {
                            config.supported_arch = DEFAULT_SUPPORTED_ARCH.to_string();
                        }
                        return Ok(config);
                    }
                    Err(err) => {
                        parse_errors.push(format!("{}: {}", path.display(), err));
                    }
                },
                Err(err) => {
                    parse_errors.push(format!("{}: {}", path.display(), err));
                }
            }
        }
    }
    let fallback = fallback_release_config(app);
    if parse_errors.is_empty() {
        eprintln!(
            "release_config.json not found in bundle resources, using embedded defaults for {}/{}",
            fallback.repo_owner, fallback.repo_name
        );
    } else {
        eprintln!(
            "release_config.json unavailable, using embedded defaults for {}/{}; details: {}",
            fallback.repo_owner,
            fallback.repo_name,
            parse_errors.join(" | ")
        );
    }
    Ok(fallback)
}

/// 设置页「收紧共享权限」:用户点了才调,后台线程里把本账户名下、所有账户可写的共享几处收紧;回重查后的提示
#[tauri::command]
pub(crate) async fn seal_shared_runtime_permissions_command(
) -> std::result::Result<serde_json::Value, String> {
    let found = tauri::async_runtime::spawn_blocking(seal_my_open_shared_tree)
        .await
        .map_err(|e| format!("{e}"))?;
    let (warning, fixable) = found.warning();
    Ok(serde_json::json!({ "sharedRuntimeWarning": warning, "sharedRuntimeFixable": fixable }))
}
