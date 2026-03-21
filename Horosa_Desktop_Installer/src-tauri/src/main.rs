#![cfg_attr(not(debug_assertions), windows_subsystem = "windows")]

use anyhow::{anyhow, Context, Result};
use flate2::read::GzDecoder;
use mime_guess::from_path;
use reqwest::blocking::Client;
use rfd::{MessageButtons, MessageDialog, MessageDialogResult, MessageLevel};
use semver::Version;
use serde::{Deserialize, Serialize};
use sha2::{Digest, Sha256};
use std::collections::HashMap;
use std::fs::{self, File};
use std::io::{Read, Write};
use std::net::{SocketAddr, TcpListener};
use std::path::{Path, PathBuf};
use std::process::{Command, Stdio};
use std::sync::atomic::{AtomicBool, Ordering};
use std::sync::{Arc, Condvar, Mutex};
use std::thread;
use std::time::{Duration, SystemTime, UNIX_EPOCH};
use tar::Archive;
use tauri::menu::{Menu, MenuItem, PredefinedMenuItem, Submenu};
use tauri::{
    AppHandle, LogicalPosition, LogicalSize, Manager, Position, RunEvent, Runtime, Size,
    WebviewUrl, WebviewWindow, WebviewWindowBuilder, WindowEvent,
};
use tiny_http::{Header, Method, Response, Server, StatusCode};
use zip::ZipArchive;

const APP_NAME: &str = "星阙";
const MAIN_WINDOW_LABEL: &str = "main";
const PREFERENCES_WINDOW_LABEL: &str = "preferences";
const DIAGNOSTICS_WINDOW_LABEL: &str = "diagnostics";
const MENU_CHECK_UPDATES: &str = "check_updates";
const MENU_REINSTALL_RUNTIME: &str = "reinstall_runtime";
const MENU_OPEN_PREFERENCES: &str = "open_preferences";
const MENU_SHOW_MAIN_WINDOW: &str = "show_main_window";
const MENU_SHOW_DIAGNOSTICS: &str = "show_diagnostics";
const MENU_OPEN_LOGS: &str = "open_logs";
const MENU_OPEN_DATA: &str = "open_data";
const MENU_OPEN_RUNTIME: &str = "open_runtime";
const MENU_RELOAD_MAIN: &str = "reload_main";
const MENU_OPEN_RELEASES: &str = "open_releases";
const MENU_ZOOM_IN: &str = "zoom_in";
const MENU_ZOOM_OUT: &str = "zoom_out";
const MENU_ZOOM_RESET: &str = "zoom_reset";
const DEFAULT_ZOOM: f64 = 1.0;
const MIN_ZOOM: f64 = 0.7;
const MAX_ZOOM: f64 = 1.8;
const ZOOM_STEP: f64 = 0.1;
const DEFAULT_REPO_OWNER: &str = "Horace-Maxwell";
const DEFAULT_REPO_NAME: &str = "Horosa-Web-App-comprehensively-improved-MacOS";
const DEFAULT_RUNTIME_ASSET_NAME: &str = "horosa-runtime-macos-arm64.tar.gz";
const DEFAULT_DESKTOP_ASSET_NAME: &str = "Horosa-Desktop-macos-arm64.zip";
const DEFAULT_DESKTOP_PKG_NAME: &str = "Horosa-Installer-macos-arm64.pkg";
const DEFAULT_DESKTOP_PKG_ZIP_NAME: &str = "Horosa-Installer-macos-arm64-pkg.zip";
const DEFAULT_DESKTOP_OFFLINE_PKG_NAME: &str = "Horosa-Installer-macos-arm64-offline.pkg";
const DEFAULT_DESKTOP_OFFLINE_PKG_ZIP_NAME: &str = "Horosa-Installer-macos-arm64-offline-pkg.zip";
const DEFAULT_UPDATE_MANIFEST_NAME: &str = "horosa-latest.json";
const DEFAULT_SUPPORTED_ARCH: &str = "arm64";
const DEFAULT_RELEASE_TAG_PREFIX: &str = "v";
const DOWNLOAD_MAX_ATTEMPTS: usize = 4;
const DEFAULT_FRONTEND_PORT: u16 = 38991;
const UPDATE_COMPLETE_MARKER_NAME: &str = "update-complete.txt";
const PREFERENCES_FILE_NAME: &str = "preferences.json";
const WINDOW_STATE_FILE_NAME: &str = "window-state.json";

#[allow(dead_code)]
#[derive(Debug, Clone, Deserialize)]
struct ReleaseConfig {
    #[serde(rename = "repoOwner")]
    repo_owner: String,
    #[serde(rename = "repoName")]
    repo_name: String,
    #[serde(rename = "runtimeVersion")]
    runtime_version: String,
    #[serde(rename = "runtimeAssetName")]
    runtime_asset_name: String,
    #[serde(rename = "desktopAssetName")]
    desktop_asset_name: String,
    #[serde(rename = "desktopPkgName")]
    desktop_pkg_name: String,
    #[serde(rename = "desktopPkgZipName")]
    desktop_pkg_zip_name: String,
    #[serde(
        rename = "desktopOfflinePkgName",
        default = "default_desktop_offline_pkg_name"
    )]
    desktop_offline_pkg_name: String,
    #[serde(
        rename = "desktopOfflinePkgZipName",
        default = "default_desktop_offline_pkg_zip_name"
    )]
    desktop_offline_pkg_zip_name: String,
    #[serde(rename = "updateManifestName")]
    update_manifest_name: String,
    #[serde(rename = "primaryDownload", default)]
    primary_download: String,
    #[serde(rename = "supportedArch", default = "default_supported_arch")]
    supported_arch: String,
    #[serde(rename = "releaseTagPrefix")]
    release_tag_prefix: String,
    #[serde(rename = "appName")]
    app_name: String,
}

#[derive(Debug, Deserialize)]
struct GithubRelease {
    tag_name: String,
    html_url: Option<String>,
    body: Option<String>,
    assets: Vec<GithubAsset>,
}

#[derive(Debug, Deserialize)]
struct GithubAsset {
    name: String,
    browser_download_url: String,
}

#[allow(dead_code)]
#[derive(Debug, Deserialize)]
struct UpdateManifest {
    version: String,
    tag: Option<String>,
    notes: Option<String>,
    #[serde(rename = "platforms")]
    platforms: HashMap<String, UpdatePlatform>,
}

#[allow(dead_code)]
#[derive(Debug, Deserialize)]
struct UpdatePlatform {
    #[serde(rename = "appUrl")]
    app_url: String,
    #[serde(rename = "dmgUrl")]
    dmg_url: Option<String>,
    #[serde(rename = "pkgUrl")]
    pkg_url: Option<String>,
    #[serde(rename = "runtimeUrl")]
    runtime_url: Option<String>,
    #[serde(rename = "runtimeVersion")]
    runtime_version: Option<String>,
    #[serde(rename = "appSha256")]
    app_sha256: Option<String>,
    #[serde(rename = "pkgSha256")]
    pkg_sha256: Option<String>,
    #[serde(rename = "runtimeSha256")]
    runtime_sha256: Option<String>,
}

#[derive(Debug, Clone)]
struct UpdatePlan {
    latest_version: Version,
    notes: String,
    repo_url: String,
    release_url: String,
    app_url: String,
    app_sha256: Option<String>,
    runtime_url: Option<String>,
    runtime_version: Option<String>,
    runtime_sha256: Option<String>,
    source: UpdateSource,
}

#[derive(Debug, Clone, Copy, PartialEq, Eq)]
enum UpdateSource {
    Manifest,
    GithubApi,
}

#[derive(Debug, Clone, Deserialize)]
struct RuntimeManifest {
    version: String,
    built_at: String,
}

#[derive(Debug, Clone)]
struct RuntimePaths {
    app_data_dir: PathBuf,
    runtime_dir: PathBuf,
    logs_dir: PathBuf,
    frontend_dir: PathBuf,
    start_script: PathBuf,
    stop_script: PathBuf,
    manifest_path: PathBuf,
}

#[derive(Debug, Clone)]
struct RuntimeSession {
    paths: RuntimePaths,
    backend_port: u16,
    web_port: u16,
}

#[derive(Debug, Clone, Serialize, Deserialize)]
#[serde(rename_all = "camelCase")]
struct AppPreferences {
    auto_check_updates: bool,
    show_status_notifications: bool,
    compact_launcher_layout: bool,
    enable_experimental_features: bool,
    always_review_before_replace: bool,
}

impl Default for AppPreferences {
    fn default() -> Self {
        Self {
            auto_check_updates: true,
            show_status_notifications: true,
            compact_launcher_layout: false,
            enable_experimental_features: false,
            always_review_before_replace: true,
        }
    }
}

#[derive(Debug, Clone, Copy, Serialize, Deserialize, PartialEq, Eq)]
#[serde(rename_all = "snake_case")]
enum InstallSource {
    DmgOnline,
    PkgOnline,
    PkgOffline,
    Unknown,
}

#[derive(Debug, Clone, Serialize, Deserialize)]
#[serde(rename_all = "camelCase")]
struct InstallSourceMarker {
    source: InstallSource,
    installed_at: Option<u64>,
    runtime_version: Option<String>,
    app_version: Option<String>,
}

#[derive(Debug, Clone, Copy, Serialize, Deserialize, PartialEq, Eq)]
#[serde(rename_all = "snake_case")]
enum LauncherStateKind {
    LaunchReady,
    OfflineReady,
    OfflineReview,
    OfflineRepairRequired,
    RepairInProgress,
    UpdateInProgress,
}

#[derive(Debug, Clone, Copy, Serialize, Deserialize, PartialEq, Eq)]
#[serde(rename_all = "snake_case")]
enum RecoveryKind {
    OfflineReinstallRequired,
    RepairAvailable,
    GenericFailure,
}

#[derive(Debug, Clone, Copy, Serialize, Deserialize, PartialEq, Eq)]
#[serde(rename_all = "snake_case")]
enum LauncherActionKind {
    ReinstallOfflinePackage,
    OpenDiagnostics,
    RevealData,
    RevealRuntime,
}

#[derive(Debug, Clone, Serialize, Deserialize)]
#[serde(rename_all = "camelCase")]
struct LauncherStatePayload {
    kind: LauncherStateKind,
    badge: String,
    title: String,
    summary: String,
    detail: String,
    recommendation: Option<String>,
    install_source: Option<InstallSource>,
    recovery_kind: Option<RecoveryKind>,
    primary_action: Option<LauncherActionKind>,
    secondary_actions: Vec<LauncherActionKind>,
    raw_error: Option<String>,
}

#[derive(Debug, Clone, Copy, Serialize, Deserialize, PartialEq, Eq)]
#[serde(rename_all = "snake_case")]
enum AssetReviewMode {
    Install,
    Repair,
    Update,
}

impl AssetReviewMode {
    fn title(self) -> &'static str {
        match self {
            Self::Install => "安装审查",
            Self::Repair => "修复审查",
            Self::Update => "更新审查",
        }
    }

    fn progress_copy(self) -> &'static str {
        match self {
            Self::Install => "检查已安装内容",
            Self::Repair => "检查待修复内容",
            Self::Update => "检查将替换的内容",
        }
    }
}

#[derive(Debug, Clone, Copy, Serialize, Deserialize, PartialEq, Eq, Hash)]
#[serde(rename_all = "snake_case")]
enum DetectedAssetKind {
    InstalledApp,
    SharedRuntime,
    UserRuntime,
    PendingMarker,
    CachedRuntimeArchive,
    CachedAppUpdate,
}

impl DetectedAssetKind {
    fn key(self) -> &'static str {
        match self {
            Self::InstalledApp => "installed_app",
            Self::SharedRuntime => "shared_runtime",
            Self::UserRuntime => "user_runtime",
            Self::PendingMarker => "pending_marker",
            Self::CachedRuntimeArchive => "cached_runtime_archive",
            Self::CachedAppUpdate => "cached_app_update",
        }
    }
}

#[derive(Debug, Clone, Copy, Serialize, Deserialize, PartialEq, Eq)]
#[serde(rename_all = "snake_case")]
enum DetectedAssetState {
    Healthy,
    Outdated,
    Broken,
    Pending,
    CacheOnly,
}

#[derive(Debug, Clone, Copy, Serialize, Deserialize, PartialEq, Eq)]
#[serde(rename_all = "snake_case")]
enum AssetDecision {
    Replace,
    Keep,
}

#[derive(Debug, Clone, Serialize, Deserialize)]
#[serde(rename_all = "camelCase")]
struct AssetInventoryItem {
    kind: DetectedAssetKind,
    label: String,
    path: String,
    state: DetectedAssetState,
    replace_recommended: bool,
    requires_admin: bool,
    details: String,
}

#[derive(Debug, Clone, Serialize, Deserialize)]
#[serde(rename_all = "camelCase")]
struct AssetReviewPayload {
    mode: AssetReviewMode,
    items: Vec<AssetInventoryItem>,
    blocking_issues: Vec<String>,
    default_selections: HashMap<String, AssetDecision>,
}

#[derive(Debug, Clone, Deserialize)]
#[serde(rename_all = "camelCase")]
struct AssetReviewCommitRequest {
    mode: AssetReviewMode,
    decisions: HashMap<String, AssetDecision>,
    cancelled: bool,
}

#[derive(Debug, Clone, Serialize)]
#[serde(rename_all = "camelCase")]
struct AssetReviewCommitResult {
    allowed: bool,
    blocking_issues: Vec<String>,
}

#[derive(Debug, Clone, Serialize)]
#[serde(rename_all = "camelCase")]
struct PreferencesPayload {
    preferences: AppPreferences,
    app_version: String,
    runtime_version: Option<String>,
    app_data_dir: String,
    logs_dir: String,
    runtime_dir: String,
    supported_arch: String,
    primary_download: String,
}

#[derive(Debug, Clone, Serialize)]
#[serde(rename_all = "camelCase")]
struct DiagnosticsPayload {
    log_path: String,
    app_data_dir: String,
    runtime_dir: String,
    lines: Vec<String>,
    assets: Vec<AssetInventoryItem>,
    updated_at: u64,
}

#[derive(Debug, Clone, Serialize, Deserialize, Default)]
#[serde(rename_all = "camelCase")]
struct SavedWindowState {
    width: Option<f64>,
    height: Option<f64>,
    x: Option<f64>,
    y: Option<f64>,
    is_maximized: Option<bool>,
}

#[derive(Debug, Clone, Serialize, Deserialize, Default)]
#[serde(rename_all = "camelCase")]
struct WindowStateStore {
    main: SavedWindowState,
    preferences: SavedWindowState,
    diagnostics: SavedWindowState,
}

#[derive(Default)]
struct PendingAssetReviewState {
    payload: Option<AssetReviewPayload>,
    response: Option<AssetReviewCommitRequest>,
}

struct AssetReviewCoordinator {
    state: Mutex<PendingAssetReviewState>,
    condvar: Condvar,
}

impl Default for AssetReviewCoordinator {
    fn default() -> Self {
        Self {
            state: Mutex::new(PendingAssetReviewState::default()),
            condvar: Condvar::new(),
        }
    }
}

struct AppState {
    session: Mutex<Option<RuntimeSession>>,
    web_shutdown: Mutex<Option<Arc<AtomicBool>>>,
    zoom_level: Mutex<f64>,
    review: AssetReviewCoordinator,
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
        primary_download: DEFAULT_DESKTOP_OFFLINE_PKG_ZIP_NAME.to_string(),
        supported_arch: DEFAULT_SUPPORTED_ARCH.to_string(),
        release_tag_prefix: DEFAULT_RELEASE_TAG_PREFIX.to_string(),
        app_name: APP_NAME.to_string(),
    }
}

impl Default for AppState {
    fn default() -> Self {
        Self {
            session: Mutex::new(None),
            web_shutdown: Mutex::new(None),
            zoom_level: Mutex::new(DEFAULT_ZOOM),
            review: AssetReviewCoordinator::default(),
        }
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

fn load_preferences(app: &AppHandle) -> AppPreferences {
    let Ok(path) = preferences_path(app) else {
        return AppPreferences::default();
    };
    fs::read_to_string(path)
        .ok()
        .and_then(|data| serde_json::from_str::<AppPreferences>(&data).ok())
        .unwrap_or_default()
}

fn save_preferences(app: &AppHandle, preferences: &AppPreferences) -> Result<()> {
    let path = preferences_path(app)?;
    fs::write(path, serde_json::to_string_pretty(preferences)?).context("save preferences")
}

fn shared_assets_root() -> PathBuf {
    shared_runtime_root()
        .parent()
        .map(Path::to_path_buf)
        .unwrap_or_else(|| PathBuf::from("/Users/Shared/Horosa"))
}

fn shared_downloads_dir() -> PathBuf {
    shared_assets_root().join("downloads")
}

fn install_source_marker_path() -> PathBuf {
    std::env::var_os("HOROSA_INSTALL_SOURCE_PATH")
        .map(PathBuf::from)
        .unwrap_or_else(|| shared_assets_root().join("install-source.json"))
}

fn load_install_source_marker() -> Option<InstallSourceMarker> {
    let path = install_source_marker_path();
    let data = fs::read_to_string(path).ok()?;
    serde_json::from_str(&data).ok()
}

fn current_install_source(config: &ReleaseConfig) -> Option<InstallSource> {
    let marker = load_install_source_marker()?;
    if marker.source == InstallSource::PkgOffline
        && offline_install_marker_is_current(&marker, &config.runtime_version)
    {
        return Some(InstallSource::PkgOffline);
    }
    Some(marker.source)
}

fn source_label(source: InstallSource) -> &'static str {
    match source {
        InstallSource::PkgOffline => "离线安装包",
        InstallSource::PkgOnline => "在线安装包",
        InstallSource::DmgOnline => "DMG 安装",
        InstallSource::Unknown => "当前安装",
    }
}

fn build_offline_ready_state(config: &ReleaseConfig) -> LauncherStatePayload {
    LauncherStatePayload {
        kind: LauncherStateKind::OfflineReady,
        badge: "离线安装已完成".to_string(),
        title: "这台 Mac 已准备好，可直接打开使用".to_string(),
        summary: "当前离线安装来源已经把所需本机组件准备到位，本次不会联网下载。".to_string(),
        detail: format!(
            "当前安装来源：{}。本机组件版本 {} 已可直接使用；如需修复，请重新安装离线包。",
            source_label(InstallSource::PkgOffline),
            config.runtime_version
        ),
        recommendation: Some(
            "后续日常打开会直接进入主界面，只有在你主动修复或更新时才会继续处理。".to_string(),
        ),
        install_source: Some(InstallSource::PkgOffline),
        recovery_kind: None,
        primary_action: None,
        secondary_actions: vec![
            LauncherActionKind::RevealRuntime,
            LauncherActionKind::RevealData,
        ],
        raw_error: None,
    }
}

fn build_offline_review_state(mode: AssetReviewMode) -> LauncherStatePayload {
    LauncherStatePayload {
        kind: LauncherStateKind::OfflineReview,
        badge: mode.title().to_string(),
        title: "已发现本机已有内容，请决定这次要替换哪些项目".to_string(),
        summary: "这次不会自动覆盖已有资产，只有你勾选为“替换”的内容才会被处理。".to_string(),
        detail: "离线路径下会尽量复用已经可用的本机组件，不会因为审查而自动转为联网准备。"
            .to_string(),
        recommendation: Some("如果这台 Mac 已经能正常使用，通常保留可复用内容就够了。".to_string()),
        install_source: Some(InstallSource::PkgOffline),
        recovery_kind: None,
        primary_action: None,
        secondary_actions: vec![
            LauncherActionKind::OpenDiagnostics,
            LauncherActionKind::RevealRuntime,
        ],
        raw_error: None,
    }
}

fn build_repair_in_progress_state() -> LauncherStatePayload {
    LauncherStatePayload {
        kind: LauncherStateKind::RepairInProgress,
        badge: "组件修复".to_string(),
        title: "正在整理并恢复本机组件".to_string(),
        summary: "星阙 会尽量保留当前数据，并在准备完成后自动回到主界面。".to_string(),
        detail: "技术细节和完整日志仍然可用，但会退到第二层，避免打断当前恢复流程。".to_string(),
        recommendation: None,
        install_source: None,
        recovery_kind: None,
        primary_action: None,
        secondary_actions: vec![],
        raw_error: None,
    }
}

fn build_update_in_progress_state() -> LauncherStatePayload {
    LauncherStatePayload {
        kind: LauncherStateKind::UpdateInProgress,
        badge: "版本更新".to_string(),
        title: "正在准备新版本并保持当前数据不变".to_string(),
        summary: "下载、校验和替换都会在 app 内完成，准备好后会自动重开。".to_string(),
        detail: "只有被确认要替换的 app 或本机组件会参与这次更新。".to_string(),
        recommendation: None,
        install_source: None,
        recovery_kind: None,
        primary_action: None,
        secondary_actions: vec![],
        raw_error: None,
    }
}

fn build_generic_launcher_error(raw_error: &str) -> LauncherStatePayload {
    LauncherStatePayload {
        kind: LauncherStateKind::RepairInProgress,
        badge: "需要处理".to_string(),
        title: "这次准备没有按预期完成".to_string(),
        summary: "星阙 还没有准备好，但当前数据和诊断入口都已经保留。".to_string(),
        detail: "你可以先查看诊断信息，必要时再重新准备本机组件。".to_string(),
        recommendation: Some(
            "如果这是首次启动或刚完成更新，先查看诊断中心通常会更稳妥。".to_string(),
        ),
        install_source: None,
        recovery_kind: Some(RecoveryKind::GenericFailure),
        primary_action: Some(LauncherActionKind::OpenDiagnostics),
        secondary_actions: vec![
            LauncherActionKind::RevealData,
            LauncherActionKind::RevealRuntime,
        ],
        raw_error: Some(raw_error.to_string()),
    }
}

fn build_offline_repair_required_state(
    config: &ReleaseConfig,
    raw_error: &str,
) -> LauncherStatePayload {
    LauncherStatePayload {
        kind: LauncherStateKind::OfflineRepairRequired,
        badge: "离线修复".to_string(),
        title: "本机组件不完整，当前无法继续打开 星阙".to_string(),
        summary: "这台 Mac 之前通过离线安装包完成准备，但当前共享本机组件缺失、损坏或版本不完整。"
            .to_string(),
        detail: format!(
            "请优先重新运行 {}。重新安装会把离线路径需要的本机组件重新接管到位。",
            config.desktop_offline_pkg_name
        ),
        recommendation: Some(
            "重新安装离线包是首选恢复方式；诊断中心和 Finder 入口仍然保留给你排查。".to_string(),
        ),
        install_source: Some(InstallSource::PkgOffline),
        recovery_kind: Some(RecoveryKind::OfflineReinstallRequired),
        primary_action: Some(LauncherActionKind::ReinstallOfflinePackage),
        secondary_actions: vec![
            LauncherActionKind::OpenDiagnostics,
            LauncherActionKind::RevealRuntime,
            LauncherActionKind::RevealData,
        ],
        raw_error: Some(raw_error.to_string()),
    }
}

fn build_launcher_error_payload(app: &AppHandle, error: &anyhow::Error) -> LauncherStatePayload {
    let raw_error = format!("{error:#}");
    if let Ok(config) = load_release_config(app) {
        if current_install_source(&config) == Some(InstallSource::PkgOffline) {
            return build_offline_repair_required_state(&config, &raw_error);
        }
    }
    build_generic_launcher_error(&raw_error)
}

fn app_downloads_dir(app: &AppHandle) -> Result<PathBuf> {
    let dir = app.path().app_data_dir().context("missing app_data_dir")?;
    Ok(dir.join("downloads"))
}

fn cached_runtime_archive_path(app: &AppHandle, config: &ReleaseConfig) -> Result<PathBuf> {
    Ok(app_downloads_dir(app)?.join(&config.runtime_asset_name))
}

fn cached_app_update_path(app: &AppHandle, config: &ReleaseConfig) -> Result<PathBuf> {
    Ok(app_downloads_dir(app)?.join(&config.desktop_asset_name))
}

fn installed_app_target_path() -> PathBuf {
    PathBuf::from(format!("/Applications/{}.app", APP_NAME))
}

fn window_state_path(app: &AppHandle) -> Result<PathBuf> {
    let dir = app
        .path()
        .app_config_dir()
        .context("missing app_config_dir")?;
    ensure_dir(&dir)?;
    Ok(dir.join(WINDOW_STATE_FILE_NAME))
}

fn load_window_states(app: &AppHandle) -> WindowStateStore {
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

fn capture_window_state(window: &WebviewWindow) -> SavedWindowState {
    let mut state = SavedWindowState::default();
    state.is_maximized = window.is_maximized().ok();
    if let Ok(size) = window.outer_size() {
        state.width = Some(size.width as f64);
        state.height = Some(size.height as f64);
    }
    if let Ok(position) = window.outer_position() {
        state.x = Some(position.x as f64);
        state.y = Some(position.y as f64);
    }
    state
}

fn apply_saved_window_state(window: &WebviewWindow, state: &SavedWindowState) {
    if state.is_maximized == Some(true) {
        let _ = window.maximize();
        return;
    }
    if let (Some(width), Some(height)) = (state.width, state.height) {
        let _ = window.set_size(Size::Logical(LogicalSize::new(width, height)));
    }
    if let (Some(x), Some(y)) = (state.x, state.y) {
        let _ = window.set_position(Position::Logical(LogicalPosition::new(x, y)));
    }
}

fn persist_window_state_for_label(
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

fn escape_js(text: &str) -> String {
    serde_json::to_string(text).unwrap_or_else(|_| "\"\"".to_string())
}

fn overlay_json(value: Option<&str>) -> String {
    value.map(escape_js).unwrap_or_else(|| "null".to_string())
}

fn emit_overlay(
    window: &WebviewWindow,
    mode: Option<&str>,
    pct: Option<u8>,
    message: Option<&str>,
    error: Option<&str>,
    ready: bool,
) {
    let mode = overlay_json(mode);
    let message = overlay_json(message);
    let error = overlay_json(error);
    let pct = pct
        .map(|value| value.to_string())
        .unwrap_or_else(|| "null".to_string());
    let ready = if ready { "true" } else { "false" };
    let _ = window.eval(&format!(
        r#"
(function () {{
  if (!window.__horosaInlineProgress) {{
    window.__horosaInlineProgress = (function () {{
      const STYLE_ID = 'horosa-inline-progress-style';
      const CARD_ID = 'horosa-inline-progress';
      let hideTimer = null;
      let lastMode = 'launch';

      function isLauncherPage() {{
        return !!document.querySelector('.installer-shell');
      }}

      function injectStyle() {{
        if (document.getElementById(STYLE_ID)) return;
        const style = document.createElement('style');
        style.id = STYLE_ID;
        style.textContent = `
          #${{CARD_ID}} {{
            position: fixed;
            top: 18px;
            right: 18px;
            width: min(360px, calc(100vw - 28px));
            z-index: 2147483646;
            padding: 16px 16px 14px;
            border-radius: 18px;
            border: 1px solid rgba(22, 32, 45, 0.08);
            background:
              linear-gradient(180deg, rgba(255,255,255,0.96), rgba(245,248,252,0.92)),
              linear-gradient(135deg, rgba(25,118,210,0.08), rgba(255,255,255,0));
            box-shadow: 0 18px 48px rgba(21, 31, 44, 0.16);
            backdrop-filter: blur(16px);
            color: #182231;
            transform: translateY(-10px) scale(0.96);
            opacity: 0;
            pointer-events: none;
            transition: opacity 180ms ease, transform 180ms ease;
            font-family: "SF Pro Display", "PingFang SC", "Helvetica Neue", sans-serif;
          }}
          #${{CARD_ID}}.is-visible {{
            opacity: 1;
            transform: translateY(0) scale(1);
          }}
          #${{CARD_ID}}[data-tone="update"] {{
            background:
              linear-gradient(180deg, rgba(255,255,255,0.97), rgba(241,251,247,0.93)),
              linear-gradient(135deg, rgba(14,127,99,0.12), rgba(255,255,255,0));
          }}
          #${{CARD_ID}}[data-tone="install"],
          #${{CARD_ID}}[data-tone="repair"] {{
            background:
              linear-gradient(180deg, rgba(255,255,255,0.97), rgba(252,247,239,0.93)),
              linear-gradient(135deg, rgba(179,105,18,0.14), rgba(255,255,255,0));
          }}
          #${{CARD_ID}}[data-tone="error"] {{
            background:
              linear-gradient(180deg, rgba(255,250,248,0.98), rgba(255,244,239,0.95)),
              linear-gradient(135deg, rgba(182,72,38,0.16), rgba(255,255,255,0));
          }}
          #${{CARD_ID}} .hip-head {{
            display: flex;
            align-items: flex-start;
            justify-content: space-between;
            gap: 12px;
          }}
          #${{CARD_ID}} .hip-badge {{
            display: inline-flex;
            align-items: center;
            gap: 8px;
            padding: 7px 10px;
            border-radius: 999px;
            background: rgba(14, 91, 216, 0.08);
            color: #0f5cd5;
            font-size: 12px;
            font-weight: 700;
            letter-spacing: 0.05em;
          }}
          #${{CARD_ID}}[data-tone="update"] .hip-badge {{
            background: rgba(14,127,99,0.12);
            color: #0e7f63;
          }}
          #${{CARD_ID}}[data-tone="install"] .hip-badge,
          #${{CARD_ID}}[data-tone="repair"] .hip-badge {{
            background: rgba(179,105,18,0.12);
            color: #aa6517;
          }}
          #${{CARD_ID}}[data-tone="error"] .hip-badge {{
            background: rgba(182,72,38,0.12);
            color: #b64826;
          }}
          #${{CARD_ID}} .hip-dot {{
            width: 8px;
            height: 8px;
            border-radius: 999px;
            background: currentColor;
            box-shadow: 0 0 0 5px rgba(14, 91, 216, 0.08);
          }}
          #${{CARD_ID}} .hip-title {{
            margin-top: 12px;
            font-size: 19px;
            font-weight: 700;
            letter-spacing: -0.03em;
          }}
          #${{CARD_ID}} .hip-copy {{
            margin-top: 6px;
            color: #5b6878;
            font-size: 13px;
            line-height: 1.65;
          }}
          #${{CARD_ID}} .hip-metrics {{
            margin-top: 12px;
            display: flex;
            align-items: center;
            justify-content: space-between;
            gap: 12px;
          }}
          #${{CARD_ID}} .hip-percent {{
            font-size: 26px;
            font-weight: 700;
            letter-spacing: -0.04em;
          }}
          #${{CARD_ID}} .hip-phase {{
            color: #6f7c8d;
            font-size: 12px;
            font-weight: 700;
            letter-spacing: 0.06em;
            text-transform: uppercase;
          }}
          #${{CARD_ID}} .hip-track {{
            margin-top: 10px;
            height: 10px;
            border-radius: 999px;
            overflow: hidden;
            background: rgba(20,31,44,0.08);
          }}
          #${{CARD_ID}} .hip-fill {{
            width: 0%;
            height: 100%;
            border-radius: inherit;
            background: linear-gradient(90deg, #0f5cd5 0%, #67a0ff 58%, #bfe0ff 100%);
            transition: width 180ms ease;
          }}
          #${{CARD_ID}}[data-tone="update"] .hip-fill {{
            background: linear-gradient(90deg, #0e7f63 0%, #45c7a0 58%, #c2f0df 100%);
          }}
          #${{CARD_ID}}[data-tone="install"] .hip-fill,
          #${{CARD_ID}}[data-tone="repair"] .hip-fill {{
            background: linear-gradient(90deg, #b36912 0%, #f0b34d 62%, #f8dca3 100%);
          }}
          #${{CARD_ID}}[data-tone="error"] .hip-fill {{
            background: linear-gradient(90deg, #b64826 0%, #ea8a66 64%, #f4c3b0 100%);
          }}
        `;
        document.head.appendChild(style);
      }}

      function ensureCard() {{
        if (isLauncherPage()) return null;
        injectStyle();
        let card = document.getElementById(CARD_ID);
        if (card) return card;
        card = document.createElement('section');
        card.id = CARD_ID;
        card.innerHTML = `
          <div class="hip-head">
            <span class="hip-badge"><span class="hip-dot"></span><span class="hip-badge-text">更新进行中</span></span>
            <span class="hip-phase">准备中</span>
          </div>
          <div class="hip-title">正在处理更新事务</div>
          <div class="hip-copy">正在准备下载与替换，不需要额外操作。</div>
          <div class="hip-metrics">
            <div class="hip-percent">0%</div>
            <div class="hip-step">下载资产</div>
          </div>
          <div class="hip-track"><div class="hip-fill"></div></div>
        `;
        document.body.appendChild(card);
        return card;
      }}

      function shouldShow(mode, text, hasError) {{
        if (hasError) return true;
        if (mode === 'update') return true;
        return /下载|更新|替换应用|运行环境更新|本机组件更新|安装运行环境|安装本机组件|解压运行环境|解压本机组件|准备本机组件|部署本机组件|校验/.test(text || '');
      }}

      function tone(mode, hasError) {{
        if (hasError) return 'error';
        if (mode === 'update' || mode === 'install' || mode === 'repair') return mode;
        return 'update';
      }}

      function titleFor(mode, hasError) {{
        if (hasError) return '更新未完成';
        if (mode === 'install') return '正在准备本机组件';
        if (mode === 'repair') return '正在修复本机组件';
        return '正在下载并安装更新';
      }}

      function badgeFor(mode, hasError) {{
        if (hasError) return '需要处理';
        if (mode === 'install') return '首次准备';
        if (mode === 'repair') return '组件修复';
        return '更新进行中';
      }}

      function stepFor(text, ready) {{
        if (ready) return '即将完成';
        if (/校验/.test(text || '')) return '校验资产';
        if (/替换应用|重开/.test(text || '')) return '替换应用';
        if (/解压|切换|部署本机组件/.test(text || '')) return '部署组件';
        if (/运行环境更新|本机组件更新|运行环境|本机组件/.test(text || '')) return '准备组件';
        return '下载资产';
      }}

      function phaseFor(pct, text, ready) {{
        if (ready || pct >= 96) return '即将完成';
        if (/替换应用|重开/.test(text || '') || pct >= 88) return '替换与重开';
        if (/运行环境|本机组件/.test(text || '') || pct >= 56) return '组件事务';
        if (/下载/.test(text || '') || pct >= 10) return '下载中';
        return '准备中';
      }}

      function show(card) {{
        if (hideTimer) {{
          clearTimeout(hideTimer);
          hideTimer = null;
        }}
        card.classList.add('is-visible');
      }}

      function hideSoon(card) {{
        if (hideTimer) clearTimeout(hideTimer);
        hideTimer = setTimeout(() => {{
          card.classList.remove('is-visible');
        }}, 1800);
      }}

      function setState(payload) {{
        const mode = payload.mode || lastMode;
        const text = payload.error || payload.message || '';
        const hasError = !!payload.error;
        const ready = !!payload.ready;
        lastMode = mode;
        const card = ensureCard();
        if (!card) return;
        if (!shouldShow(mode, text, hasError)) {{
          if (!ready) card.classList.remove('is-visible');
          return;
        }}
        card.dataset.tone = tone(mode, hasError);
        card.querySelector('.hip-badge-text').textContent = badgeFor(mode, hasError);
        card.querySelector('.hip-title').textContent = titleFor(mode, hasError);
        card.querySelector('.hip-copy').textContent = text || '正在处理下载与安装事务。';
        const pct = payload.pct == null ? 0 : Math.max(0, Math.min(100, Number(payload.pct) || 0));
        card.querySelector('.hip-percent').textContent = `${{Math.round(pct)}}%`;
        card.querySelector('.hip-phase').textContent = phaseFor(pct, text, ready);
        card.querySelector('.hip-step').textContent = stepFor(text, ready);
        card.querySelector('.hip-fill').style.width = `${{pct}}%`;
        show(card);
        if (ready && !hasError) {{
          card.querySelector('.hip-copy').textContent = '更新准备完成，正在切回新版本。';
          hideSoon(card);
        }}
      }}

      return {{ setState }};
    }})();
  }}
  window.__horosaInlineProgress.setState({{
    mode: {mode},
    pct: {pct},
    message: {message},
    error: {error},
    ready: {ready}
  }});
}})();
"#,
    ));
}

fn emit_status(window: &WebviewWindow, message: &str) {
    let raw_message = message;
    let message = escape_js(message);
    let _ = window.eval(&format!(
        "window.__horosaPendingStatusLines = window.__horosaPendingStatusLines || []; \
window.__horosaPendingStatusLines.push({message}); \
if (window.__horosaStatus) {{ window.__horosaStatus({message}); }}",
    ));
    emit_overlay(window, None, None, Some(raw_message), None, false);
}

fn emit_progress(window: &WebviewWindow, pct: u8, message: &str) {
    let raw_message = message;
    let message = escape_js(message);
    let _ = window.eval(&format!(
        "window.__horosaPendingProgress = {{ pct: {}, message: {} }}; \
if (window.__horosaProgress) {{ window.__horosaProgress({}, {}); }}",
        pct, message, pct, message
    ));
    emit_overlay(window, None, Some(pct), Some(raw_message), None, false);
}

fn emit_mode(window: &WebviewWindow, mode: &str) {
    let raw_mode = mode;
    let mode = escape_js(mode);
    let _ = window.eval(&format!(
        "window.__horosaPendingMode = {mode}; \
if (window.__horosaMode) {{ window.__horosaMode({mode}); }}",
    ));
    emit_overlay(window, Some(raw_mode), None, None, None, false);
}

fn emit_ready(window: &WebviewWindow, url: &str) {
    let url = escape_js(url);
    let _ = window.eval(&format!(
        "window.__horosaPendingReadyUrl = {url}; \
if (window.__horosaReady) {{ window.__horosaReady({url}); }} else {{ window.location.replace({url}); }}",
    ));
    emit_overlay(
        window,
        None,
        Some(100),
        Some("更新准备完成，正在切回新版本。"),
        None,
        true,
    );
}

fn emit_launcher_state(window: &WebviewWindow, payload: &LauncherStatePayload) {
    let json = serde_json::to_string(payload).unwrap_or_else(|_| "null".to_string());
    let _ = window.eval(&format!(
        "window.__horosaPendingStatePayload = {json}; \
if (window.__horosaState) {{ window.__horosaState({json}); }}"
    ));
}

fn emit_launcher_error(window: &WebviewWindow, payload: &LauncherStatePayload) {
    let json = serde_json::to_string(payload).unwrap_or_else(|_| "null".to_string());
    let overlay_message = payload
        .recommendation
        .as_deref()
        .or(Some(payload.summary.as_str()));
    let _ = window.eval(&format!(
        "window.__horosaPendingStatePayload = {json}; \
window.__horosaPendingError = {json}; \
if (window.__horosaState) {{ window.__horosaState({json}); }} \
if (window.__horosaError) {{ window.__horosaError({json}); }}"
    ));
    emit_overlay(window, Some("error"), None, None, overlay_message, false);
}

fn emit_asset_review(window: &WebviewWindow, payload: &AssetReviewPayload) {
    let json = serde_json::to_string(payload).unwrap_or_else(|_| "null".to_string());
    let _ = window.eval(&format!(
        "window.__horosaPendingReviewPayload = {json}; \
if (window.__horosaPresentReview) {{ window.__horosaPresentReview({json}); }}"
    ));
}

fn clear_asset_review(window: &WebviewWindow) {
    let _ = window.eval(
        "window.__horosaPendingReviewPayload = null; \
if (window.__horosaClearReview) { window.__horosaClearReview(); }",
    );
}

fn wait_for_asset_review(
    app: &AppHandle,
    window: &WebviewWindow,
    payload: &AssetReviewPayload,
) -> Result<Option<HashMap<String, AssetDecision>>> {
    let state = app
        .try_state::<AppState>()
        .context("app review state missing")?;
    {
        let mut guard = state
            .review
            .state
            .lock()
            .map_err(|_| anyhow!("asset review state poisoned"))?;
        guard.payload = Some(payload.clone());
        guard.response = None;
    }
    emit_asset_review(window, payload);
    let response = {
        let mut guard = state
            .review
            .state
            .lock()
            .map_err(|_| anyhow!("asset review state poisoned"))?;
        while guard.response.is_none() {
            guard = state
                .review
                .condvar
                .wait(guard)
                .map_err(|_| anyhow!("asset review wait poisoned"))?;
        }
        let response = guard.response.take();
        guard.payload = None;
        response
    };
    clear_asset_review(window);
    let Some(response) = response else {
        return Ok(None);
    };
    if response.cancelled {
        return Ok(None);
    }
    Ok(Some(merge_asset_decisions(payload, &response.decisions)))
}

fn build_menu<R: Runtime>(app: &tauri::AppHandle<R>) -> tauri::Result<Menu<R>> {
    let preferences = MenuItem::with_id(
        app,
        MENU_OPEN_PREFERENCES,
        "偏好设置…",
        true,
        Some("CmdOrCtrl+,"),
    )?;
    let check_updates = MenuItem::with_id(
        app,
        MENU_CHECK_UPDATES,
        "检查更新",
        true,
        Some("CmdOrCtrl+U"),
    )?;
    let reinstall_runtime = MenuItem::with_id(
        app,
        MENU_REINSTALL_RUNTIME,
        "重装本机组件",
        true,
        None::<&str>,
    )?;
    let show_main_window = MenuItem::with_id(
        app,
        MENU_SHOW_MAIN_WINDOW,
        "显示主窗口",
        true,
        Some("CmdOrCtrl+1"),
    )?;
    let show_diagnostics = MenuItem::with_id(
        app,
        MENU_SHOW_DIAGNOSTICS,
        "诊断中心",
        true,
        Some("CmdOrCtrl+2"),
    )?;
    let open_logs = MenuItem::with_id(
        app,
        MENU_OPEN_LOGS,
        "在 Finder 中显示日志",
        true,
        None::<&str>,
    )?;
    let open_data = MenuItem::with_id(
        app,
        MENU_OPEN_DATA,
        "在 Finder 中显示数据目录",
        true,
        None::<&str>,
    )?;
    let open_runtime = MenuItem::with_id(
        app,
        MENU_OPEN_RUNTIME,
        "在 Finder 中显示本机组件",
        true,
        None::<&str>,
    )?;
    let reload_main = MenuItem::with_id(
        app,
        MENU_RELOAD_MAIN,
        "重新载入主界面",
        true,
        Some("CmdOrCtrl+R"),
    )?;
    let open_releases = MenuItem::with_id(
        app,
        MENU_OPEN_RELEASES,
        "打开下载与版本说明",
        true,
        None::<&str>,
    )?;
    let zoom_in = MenuItem::with_id(app, MENU_ZOOM_IN, "放大", true, Some("CmdOrCtrl+="))?;
    let zoom_out = MenuItem::with_id(app, MENU_ZOOM_OUT, "缩小", true, Some("CmdOrCtrl+-"))?;
    let zoom_reset =
        MenuItem::with_id(app, MENU_ZOOM_RESET, "实际大小", true, Some("CmdOrCtrl+0"))?;

    let app_menu = Submenu::with_items(
        app,
        APP_NAME,
        true,
        &[
            &PredefinedMenuItem::about(app, None, None)?,
            &PredefinedMenuItem::separator(app)?,
            &preferences,
            &PredefinedMenuItem::separator(app)?,
            &check_updates,
            &reinstall_runtime,
            &PredefinedMenuItem::separator(app)?,
            &PredefinedMenuItem::services(app, None)?,
            &PredefinedMenuItem::separator(app)?,
            &PredefinedMenuItem::hide(app, None)?,
            &PredefinedMenuItem::hide_others(app, None)?,
            &PredefinedMenuItem::show_all(app, None)?,
            &PredefinedMenuItem::separator(app)?,
            &PredefinedMenuItem::quit(app, None)?,
        ],
    )?;

    let file_menu = Submenu::with_items(
        app,
        "文件",
        true,
        &[
            &show_main_window,
            &show_diagnostics,
            &PredefinedMenuItem::separator(app)?,
            &open_runtime,
            &open_logs,
            &open_data,
            &PredefinedMenuItem::separator(app)?,
            &PredefinedMenuItem::close_window(app, None)?,
        ],
    )?;

    let edit_menu = Submenu::with_items(
        app,
        "编辑",
        true,
        &[
            &PredefinedMenuItem::undo(app, None)?,
            &PredefinedMenuItem::redo(app, None)?,
            &PredefinedMenuItem::separator(app)?,
            &PredefinedMenuItem::cut(app, None)?,
            &PredefinedMenuItem::copy(app, None)?,
            &PredefinedMenuItem::paste(app, None)?,
            &PredefinedMenuItem::select_all(app, None)?,
        ],
    )?;

    let view_menu = Submenu::with_items(
        app,
        "视图",
        true,
        &[
            &reload_main,
            &PredefinedMenuItem::separator(app)?,
            &zoom_in,
            &zoom_out,
            &zoom_reset,
            &PredefinedMenuItem::separator(app)?,
            &PredefinedMenuItem::fullscreen(app, None)?,
            &PredefinedMenuItem::maximize(app, None)?,
        ],
    )?;

    let window_menu = Submenu::with_items(
        app,
        "窗口",
        true,
        &[
            &PredefinedMenuItem::minimize(app, None)?,
            &PredefinedMenuItem::maximize(app, None)?,
            &PredefinedMenuItem::separator(app)?,
            &PredefinedMenuItem::close_window(app, None)?,
        ],
    )?;

    let help_menu = Submenu::with_items(app, "帮助", true, &[&open_releases])?;

    Menu::with_items(
        app,
        &[
            &app_menu,
            &file_menu,
            &edit_menu,
            &view_menu,
            &window_menu,
            &help_menu,
        ],
    )
}

fn show_or_focus_window(window: &WebviewWindow) {
    let _ = window.unminimize();
    let _ = window.show();
    let _ = window.set_focus();
}

fn create_secondary_window(
    app: &AppHandle,
    label: &str,
    title: &str,
    asset: &str,
    size: (f64, f64),
    min_size: (f64, f64),
) -> Result<WebviewWindow> {
    let builder = WebviewWindowBuilder::new(app, label, WebviewUrl::App(asset.into()))
        .title(title)
        .resizable(true)
        .center()
        .inner_size(size.0, size.1)
        .min_inner_size(min_size.0, min_size.1)
        .visible(true);
    let window = builder.build().context("build secondary window")?;
    let states = load_window_states(app);
    match label {
        PREFERENCES_WINDOW_LABEL => apply_saved_window_state(&window, &states.preferences),
        DIAGNOSTICS_WINDOW_LABEL => apply_saved_window_state(&window, &states.diagnostics),
        _ => {}
    }
    Ok(window)
}

fn open_preferences_window(app: &AppHandle) -> Result<()> {
    if let Some(window) = app.get_webview_window(PREFERENCES_WINDOW_LABEL) {
        show_or_focus_window(&window);
        return Ok(());
    }
    let window = create_secondary_window(
        app,
        PREFERENCES_WINDOW_LABEL,
        "偏好设置",
        "settings.html",
        (760.0, 680.0),
        (680.0, 620.0),
    )?;
    show_or_focus_window(&window);
    Ok(())
}

fn open_diagnostics_window(app: &AppHandle) -> Result<()> {
    if let Some(window) = app.get_webview_window(DIAGNOSTICS_WINDOW_LABEL) {
        show_or_focus_window(&window);
        return Ok(());
    }
    let window = create_secondary_window(
        app,
        DIAGNOSTICS_WINDOW_LABEL,
        "诊断中心",
        "diagnostics.html",
        (840.0, 720.0),
        (720.0, 620.0),
    )?;
    show_or_focus_window(&window);
    Ok(())
}

fn open_main_window(app: &AppHandle) -> Result<()> {
    if let Some(window) = app.get_webview_window(MAIN_WINDOW_LABEL) {
        show_or_focus_window(&window);
        return Ok(());
    }

    let window =
        WebviewWindowBuilder::new(app, MAIN_WINDOW_LABEL, WebviewUrl::App("index.html".into()))
            .title(APP_NAME)
            .resizable(true)
            .center()
            .inner_size(1480.0, 960.0)
            .min_inner_size(1180.0, 760.0)
            .build()
            .context("recreate main window")?;
    apply_saved_window_state(&window, &load_window_states(app).main);
    let _ = window.maximize();
    set_window_zoom(app, DEFAULT_ZOOM)?;
    if let Some(state) = app.try_state::<AppState>() {
        if let Ok(slot) = state.session.lock() {
            if let Some(session) = slot.as_ref() {
                emit_ready(
                    &window,
                    &frontend_url(session.web_port, session.backend_port),
                );
            }
        }
    }
    show_or_focus_window(&window);
    Ok(())
}

fn show_macos_notification(title: &str, body: &str) {
    let _ = Command::new("/usr/bin/osascript")
        .arg("-e")
        .arg(format!(
            "display notification {} with title {}",
            applescript_quote_text(body),
            applescript_quote_text(title)
        ))
        .stdout(Stdio::null())
        .stderr(Stdio::null())
        .spawn();
}

fn open_release_page(app: &AppHandle) -> Result<()> {
    let config = load_release_config(app)?;
    let url = format!(
        "https://github.com/{}/{}/releases/latest",
        config.repo_owner, config.repo_name
    );
    Command::new("open")
        .arg(url)
        .spawn()
        .context("open release page")?;
    Ok(())
}

fn build_preferences_payload(app: &AppHandle) -> Result<PreferencesPayload> {
    let config = load_release_config(app)?;
    let paths = resolve_runtime_paths(app)?;
    Ok(PreferencesPayload {
        preferences: load_preferences(app),
        app_version: env!("CARGO_PKG_VERSION").to_string(),
        runtime_version: local_runtime_version(app),
        app_data_dir: paths.app_data_dir.to_string_lossy().to_string(),
        logs_dir: paths.logs_dir.to_string_lossy().to_string(),
        runtime_dir: paths.runtime_dir.to_string_lossy().to_string(),
        supported_arch: config.supported_arch,
        primary_download: config.primary_download,
    })
}

fn replace_app_bundle(source: &Path, target: &Path) -> Result<()> {
    if source == target {
        return Ok(());
    }
    let backup = target.with_extension("app.previous");
    let command = format!(
        "set -euo pipefail\nTARGET={target}\nSOURCE={source}\nBACKUP={backup}\nrm -rf \"${{BACKUP}}\"\nif [ -d \"${{TARGET}}\" ]; then mv \"${{TARGET}}\" \"${{BACKUP}}\"; fi\nif /usr/bin/ditto \"${{SOURCE}}\" \"${{TARGET}}\"; then\n  rm -rf \"${{BACKUP}}\"\n  /usr/bin/xattr -dr com.apple.quarantine \"${{TARGET}}\" >/dev/null 2>&1 || true\nelse\n  rm -rf \"${{TARGET}}\"\n  if [ -d \"${{BACKUP}}\" ]; then mv \"${{BACKUP}}\" \"${{TARGET}}\" || true; fi\n  exit 1\nfi\n",
        target = shell_quote(target),
        source = shell_quote(source),
        backup = shell_quote(&backup)
    );
    if target_requires_admin_update(target) {
        let status = Command::new("/usr/bin/osascript")
            .arg("-e")
            .arg(format!(
                "do shell script {} with administrator privileges",
                applescript_quote_text(&format!("/bin/bash -lc {}", shell_quote_text(&command)))
            ))
            .status()
            .context("replace installed app with admin")?;
        if !status.success() {
            return Err(anyhow!("app replace command exited with {}", status));
        }
    } else {
        let status = Command::new("/bin/bash")
            .arg("-lc")
            .arg(command)
            .status()
            .context("replace installed app")?;
        if !status.success() {
            return Err(anyhow!("app replace command exited with {}", status));
        }
    }
    Ok(())
}

fn clear_selected_assets_internal(
    app: &AppHandle,
    decisions: &HashMap<String, AssetDecision>,
) -> Result<Vec<String>> {
    let config = load_release_config(app)?;
    let mut cleared = Vec::new();

    if decision_for_kind(decisions, DetectedAssetKind::PendingMarker) == AssetDecision::Replace {
        let path = shared_runtime_pending_path();
        if path.exists() {
            fs::remove_file(&path)
                .with_context(|| format!("remove pending marker {}", path.display()))?;
            cleared.push("已清理待处理安装标记".to_string());
        }
    }

    if decision_for_kind(decisions, DetectedAssetKind::CachedRuntimeArchive)
        == AssetDecision::Replace
    {
        let paths = [
            cached_runtime_archive_path(app, &config)?,
            shared_downloads_dir().join(&config.runtime_asset_name),
        ];
        for path in paths {
            if path.exists() {
                let _ = fs::remove_file(&path);
            }
        }
        cleared.push("已清理本机组件缓存".to_string());
    }

    if decision_for_kind(decisions, DetectedAssetKind::CachedAppUpdate) == AssetDecision::Replace {
        let path = cached_app_update_path(app, &config)?;
        if path.exists() {
            let _ = fs::remove_file(&path);
            cleared.push("已清理 app 更新缓存".to_string());
        }
    }

    if decision_for_kind(decisions, DetectedAssetKind::UserRuntime) == AssetDecision::Replace {
        let root = user_runtime_root(app)?;
        remove_dir_if_exists(&root)?;
        cleared.push("已清理当前用户本机组件目录".to_string());
    }

    Ok(cleared)
}

fn replace_installed_app_if_selected(
    decisions: &HashMap<String, AssetDecision>,
) -> Result<Option<String>> {
    if decision_for_kind(decisions, DetectedAssetKind::InstalledApp) != AssetDecision::Replace {
        return Ok(None);
    }
    let source = match app_bundle_path() {
        Some(path) => path,
        None => return Ok(None),
    };
    let target = installed_app_target_path();
    if !target.exists() || source == target {
        return Ok(None);
    }
    replace_app_bundle(&source, &target)?;
    Ok(Some(format!(
        "已将当前 app 副本同步到 {}",
        target.display()
    )))
}

fn offline_reinstall_candidates(config: &ReleaseConfig) -> Vec<PathBuf> {
    let mut candidates = Vec::new();
    if let Some(home) = std::env::var_os("HOME").map(PathBuf::from) {
        for root in [home.join("Downloads"), home.join("Desktop"), home] {
            candidates.push(root.join(&config.desktop_offline_pkg_name));
            candidates.push(root.join(&config.desktop_offline_pkg_zip_name));
        }
    }
    candidates
}

fn open_offline_reinstall_flow(app: &AppHandle) -> Result<()> {
    let config = load_release_config(app)?;
    if let Some(path) = offline_reinstall_candidates(&config)
        .into_iter()
        .find(|path| path.exists())
    {
        Command::new("open")
            .arg(&path)
            .spawn()
            .with_context(|| format!("open offline reinstall asset {}", path.display()))?;
        return Ok(());
    }

    open_release_page(app)?;
    MessageDialog::new()
        .set_level(MessageLevel::Info)
        .set_title("重新安装离线包")
        .set_description(format!(
            "没有在 Downloads 或 Desktop 中找到 {}。\n\n我已经为你打开最新 Release 页面，请重新获取离线安装包后再次安装。",
            config.desktop_offline_pkg_name
        ))
        .set_buttons(MessageButtons::Ok)
        .show();
    Ok(())
}

fn collect_diagnostics_payload(app: &AppHandle) -> Result<DiagnosticsPayload> {
    let paths = resolve_runtime_paths(app)?;
    ensure_dir(&paths.logs_dir)?;
    let mut latest_log = None;
    let mut latest_mtime = UNIX_EPOCH;
    for entry in fs::read_dir(&paths.logs_dir)? {
        let entry = entry?;
        let path = entry.path();
        if path.extension().and_then(|value| value.to_str()) != Some("log") {
            continue;
        }
        let modified = entry
            .metadata()
            .and_then(|meta| meta.modified())
            .unwrap_or(UNIX_EPOCH);
        if modified >= latest_mtime {
            latest_mtime = modified;
            latest_log = Some(path);
        }
    }
    let log_path = latest_log.unwrap_or_else(|| paths.logs_dir.join("update-installer.log"));
    let lines = fs::read_to_string(&log_path)
        .unwrap_or_else(|_| "暂无日志，应用会在首次启动和更新时逐步写入这里。".to_string())
        .lines()
        .map(|line| line.to_string())
        .collect::<Vec<_>>();
    let lines = if lines.len() > 200 {
        lines[lines.len() - 200..].to_vec()
    } else {
        lines
    };
    Ok(DiagnosticsPayload {
        log_path: log_path.to_string_lossy().to_string(),
        app_data_dir: paths.app_data_dir.to_string_lossy().to_string(),
        runtime_dir: paths.runtime_dir.to_string_lossy().to_string(),
        lines,
        assets: build_asset_review_payload(
            app,
            AssetReviewMode::Install,
            current_app_version(),
            local_runtime_version(app),
        )?
        .items,
        updated_at: unix_ts(),
    })
}

#[tauri::command]
fn load_preferences_payload(app: AppHandle) -> std::result::Result<PreferencesPayload, String> {
    build_preferences_payload(&app).map_err(|err| format!("{err:#}"))
}

#[tauri::command]
fn save_preferences_command(
    app: AppHandle,
    preferences: AppPreferences,
) -> std::result::Result<(), String> {
    save_preferences(&app, &preferences).map_err(|err| format!("{err:#}"))
}

#[tauri::command]
fn read_diagnostics_snapshot(app: AppHandle) -> std::result::Result<DiagnosticsPayload, String> {
    collect_diagnostics_payload(&app).map_err(|err| format!("{err:#}"))
}

#[tauri::command]
fn scan_existing_assets(
    app: AppHandle,
    mode: String,
) -> std::result::Result<AssetReviewPayload, String> {
    let mode = parse_asset_review_mode(&mode).map_err(|err| format!("{err:#}"))?;
    let config = load_release_config(&app).map_err(|err| format!("{err:#}"))?;
    build_asset_review_payload(
        &app,
        mode,
        current_app_version(),
        Some(config.runtime_version),
    )
    .map_err(|err| format!("{err:#}"))
}

#[tauri::command]
fn commit_asset_review(
    app: AppHandle,
    request: AssetReviewCommitRequest,
) -> std::result::Result<AssetReviewCommitResult, String> {
    let Some(state) = app.try_state::<AppState>() else {
        return Err("missing app state".to_string());
    };
    let payload = {
        let guard = state
            .review
            .state
            .lock()
            .map_err(|_| "asset review state poisoned".to_string())?;
        guard.payload.clone()
    }
    .ok_or_else(|| "当前没有待确认的安装审查".to_string())?;

    if payload.mode != request.mode {
        return Err("安装审查模式不匹配".to_string());
    }
    if request.cancelled {
        let mut guard = state
            .review
            .state
            .lock()
            .map_err(|_| "asset review state poisoned".to_string())?;
        guard.response = Some(request);
        state.review.condvar.notify_all();
        return Ok(AssetReviewCommitResult {
            allowed: false,
            blocking_issues: Vec::new(),
        });
    }

    let blocking_issues = validate_asset_review_payload(&app, &payload, &request.decisions)
        .map_err(|err| format!("{err:#}"))?;
    if !blocking_issues.is_empty() {
        return Ok(AssetReviewCommitResult {
            allowed: false,
            blocking_issues,
        });
    }
    let mut guard = state
        .review
        .state
        .lock()
        .map_err(|_| "asset review state poisoned".to_string())?;
    guard.response = Some(request);
    state.review.condvar.notify_all();
    Ok(AssetReviewCommitResult {
        allowed: true,
        blocking_issues: Vec::new(),
    })
}

#[tauri::command]
fn clear_selected_assets(
    app: AppHandle,
    decisions: HashMap<String, AssetDecision>,
) -> std::result::Result<Vec<String>, String> {
    clear_selected_assets_internal(&app, &decisions).map_err(|err| format!("{err:#}"))
}

#[tauri::command]
fn perform_launcher_action(
    app: AppHandle,
    action: LauncherActionKind,
) -> std::result::Result<(), String> {
    match action {
        LauncherActionKind::ReinstallOfflinePackage => {
            open_offline_reinstall_flow(&app).map_err(|err| format!("{err:#}"))
        }
        LauncherActionKind::OpenDiagnostics => {
            open_diagnostics_window(&app).map_err(|err| format!("{err:#}"))
        }
        LauncherActionKind::RevealData => reveal_special_path(app, "data".to_string()),
        LauncherActionKind::RevealRuntime => reveal_special_path(app, "runtime".to_string()),
    }
}

#[tauri::command]
fn reveal_special_path(app: AppHandle, kind: String) -> std::result::Result<(), String> {
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
fn open_preferences_window_command(app: AppHandle) -> std::result::Result<(), String> {
    open_preferences_window(&app).map_err(|err| format!("{err:#}"))
}

#[tauri::command]
fn open_diagnostics_window_command(app: AppHandle) -> std::result::Result<(), String> {
    open_diagnostics_window(&app).map_err(|err| format!("{err:#}"))
}

#[tauri::command]
fn trigger_update_check_command(app: AppHandle) -> std::result::Result<(), String> {
    thread::spawn(move || {
        if let Err(err) = check_for_updates(app.clone()) {
            MessageDialog::new()
                .set_level(MessageLevel::Error)
                .set_title("检查更新失败")
                .set_description(format!("{err:#}"))
                .set_buttons(MessageButtons::Ok)
                .show();
        }
    });
    Ok(())
}

#[tauri::command]
fn trigger_runtime_repair_command(app: AppHandle) -> std::result::Result<(), String> {
    trigger_reinstall(app);
    Ok(())
}

#[tauri::command]
fn open_login_items_settings_command() -> std::result::Result<(), String> {
    Command::new("open")
        .arg("x-apple.systempreferences:com.apple.LoginItems-Settings.extension")
        .spawn()
        .map(|_| ())
        .map_err(|err| err.to_string())
}

fn load_release_config(app: &AppHandle) -> Result<ReleaseConfig> {
    let resource_dir = app.path().resource_dir().context("missing resource dir")?;
    let candidates = [
        resource_dir.join("_up_/config/release_config.json"),
        resource_dir.join("config/release_config.json"),
        PathBuf::from(env!("CARGO_MANIFEST_DIR")).join("../config/release_config.json"),
    ];
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
                            config.primary_download =
                                DEFAULT_DESKTOP_OFFLINE_PKG_ZIP_NAME.to_string();
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

fn runtime_paths_for_dir(app_data_dir: PathBuf, runtime_dir: PathBuf) -> RuntimePaths {
    let logs_dir = app_data_dir.join("logs");
    let frontend_dir = runtime_dir.join("Horosa-Web/astrostudyui/dist-file");
    let start_script = runtime_dir.join("Horosa-Web/start_horosa_local.sh");
    let stop_script = runtime_dir.join("Horosa-Web/stop_horosa_local.sh");
    let manifest_path = runtime_dir.join("runtime-manifest.json");
    RuntimePaths {
        app_data_dir,
        runtime_dir,
        logs_dir,
        frontend_dir,
        start_script,
        stop_script,
        manifest_path,
    }
}

fn shared_runtime_dir() -> PathBuf {
    std::env::var_os("HOROSA_SHARED_RUNTIME_DIR")
        .map(PathBuf::from)
        .unwrap_or_else(|| PathBuf::from("/Users/Shared/Horosa/runtime/current"))
}

fn shared_runtime_root() -> PathBuf {
    shared_runtime_dir()
        .parent()
        .map(Path::to_path_buf)
        .unwrap_or_else(|| PathBuf::from("/Users/Shared/Horosa/runtime"))
}

fn shared_runtime_pending_path() -> PathBuf {
    shared_runtime_root()
        .parent()
        .map(|root| root.join("runtime-install-pending.txt"))
        .unwrap_or_else(|| PathBuf::from("/Users/Shared/Horosa/runtime-install-pending.txt"))
}

fn update_complete_marker_path(app: &AppHandle) -> Result<PathBuf> {
    let app_data_dir = app.path().app_data_dir().context("missing app_data_dir")?;
    ensure_dir(&app_data_dir)?;
    Ok(app_data_dir.join(UPDATE_COMPLETE_MARKER_NAME))
}

fn parse_marker_kv(data: &str) -> HashMap<String, String> {
    let mut values = HashMap::new();
    for line in data.lines() {
        let trimmed = line.trim();
        if trimmed.is_empty() {
            continue;
        }
        if let Some((key, value)) = trimmed.split_once('=') {
            values.insert(key.trim().to_string(), value.trim().to_string());
        }
    }
    values
}

fn consume_update_complete_notice(app: &AppHandle) -> Option<String> {
    let marker = update_complete_marker_path(app).ok()?;
    let data = fs::read_to_string(&marker).ok()?;
    let values = parse_marker_kv(&data);
    let _ = fs::remove_file(&marker);

    let version = values
        .get("version")
        .filter(|value| !value.trim().is_empty())
        .cloned()
        .unwrap_or_else(|| env!("CARGO_PKG_VERSION").to_string());
    let runtime_version = values
        .get("runtime_version")
        .map(|value| value.trim().to_string())
        .filter(|value| !value.is_empty());
    let installed_at = values
        .get("installed_at")
        .map(|value| value.trim().to_string())
        .filter(|value| !value.is_empty());

    let mut lines = vec![
        "星阙 已完成更新".to_string(),
        "".to_string(),
        "当前版本".to_string(),
        version,
    ];
    if let Some(runtime) = runtime_version {
        lines.push("".to_string());
        lines.push("运行环境".to_string());
        lines.push(runtime);
    }
    if let Some(installed_at) = installed_at {
        lines.push("".to_string());
        lines.push("完成时间".to_string());
        lines.push(installed_at);
    }
    lines.push("".to_string());
    lines.push("本次更新已经安装完成并重新生效。".to_string());
    Some(lines.join("\n"))
}

fn has_update_complete_marker(app: &AppHandle) -> bool {
    update_complete_marker_path(app)
        .map(|marker| marker.exists())
        .unwrap_or(false)
}

fn show_post_update_notice_if_needed(app: &AppHandle) {
    if let Some(message) = consume_update_complete_notice(app) {
        if load_preferences(app).show_status_notifications {
            show_macos_notification("星阙 已完成更新", "新版已经安装完成，并已重新生效。");
        }
        MessageDialog::new()
            .set_level(MessageLevel::Info)
            .set_title("更新完成")
            .set_description(message)
            .set_buttons(MessageButtons::Ok)
            .show();
    }
}

fn is_shared_runtime_dir(runtime_dir: &Path) -> bool {
    runtime_dir.starts_with(shared_runtime_root())
}

fn runtime_dir_has_required_files(runtime_dir: &Path) -> bool {
    runtime_dir.join("runtime-manifest.json").exists()
        && runtime_dir
            .join("Horosa-Web/start_horosa_local.sh")
            .exists()
        && runtime_dir
            .join("Horosa-Web/astrostudyui/dist-file/index.html")
            .exists()
}

fn runtime_python_bin(runtime_dir: &Path) -> PathBuf {
    runtime_dir.join("runtime/mac/python/bin/python3")
}

fn is_runtime_metadata_junk(name: &str) -> bool {
    name == ".DS_Store" || name.starts_with("._")
}

fn cleanup_runtime_metadata(root: &Path) -> Result<u64> {
    if !root.exists() {
        return Ok(0);
    }
    let mut removed = 0u64;
    let mut stack = vec![root.to_path_buf()];
    while let Some(dir) = stack.pop() {
        let entries = fs::read_dir(&dir).with_context(|| format!("read_dir {}", dir.display()))?;
        for entry in entries {
            let entry = entry?;
            let path = entry.path();
            let file_type = entry.file_type()?;
            let name = entry.file_name();
            let name = name.to_string_lossy();
            if is_runtime_metadata_junk(&name) {
                if file_type.is_dir() {
                    fs::remove_dir_all(&path)?;
                } else {
                    fs::remove_file(&path)?;
                }
                removed += 1;
                continue;
            }
            if file_type.is_dir() {
                stack.push(path);
            }
        }
    }
    Ok(removed)
}

fn runtime_python_ready(runtime_dir: &Path) -> bool {
    let python_bin = runtime_python_bin(runtime_dir);
    if !python_bin.exists() {
        return false;
    }
    Command::new(&python_bin)
        .arg("-c")
        .arg(
            "import importlib.util as iu; mods=('cherrypy','jsonpickle','swisseph'); missing=[m for m in mods if iu.find_spec(m) is None]; raise SystemExit(1 if missing else 0)",
        )
        .env("PYTHONNOUSERSITE", "1")
        .stdout(Stdio::null())
        .stderr(Stdio::null())
        .status()
        .map(|status| status.success())
        .unwrap_or(false)
}

fn prepare_runtime_dir(runtime_dir: &Path) -> Result<()> {
    let _ = cleanup_runtime_metadata(runtime_dir)?;
    Ok(())
}

fn runtime_dir_is_usable(runtime_dir: &Path) -> bool {
    if !runtime_dir_has_required_files(runtime_dir) {
        return false;
    }
    prepare_runtime_dir(runtime_dir).is_ok() && runtime_python_ready(runtime_dir)
}

fn choose_runtime_dir(
    shared_runtime_dir: &Path,
    shared_ok: bool,
    user_runtime_dir: &Path,
    user_ok: bool,
) -> PathBuf {
    match (shared_ok, user_ok) {
        (true, true) => {
            let shared_manifest =
                read_runtime_manifest_from_path(&shared_runtime_dir.join("runtime-manifest.json"));
            let user_manifest =
                read_runtime_manifest_from_path(&user_runtime_dir.join("runtime-manifest.json"));
            match compare_runtime_manifests(shared_manifest.as_ref(), user_manifest.as_ref()) {
                std::cmp::Ordering::Less => user_runtime_dir.to_path_buf(),
                _ => shared_runtime_dir.to_path_buf(),
            }
        }
        (true, false) => shared_runtime_dir.to_path_buf(),
        (false, true) => user_runtime_dir.to_path_buf(),
        (false, false) => user_runtime_dir.to_path_buf(),
    }
}

fn resolve_runtime_paths(app: &AppHandle) -> Result<RuntimePaths> {
    let app_data_dir = app.path().app_data_dir().context("missing app_data_dir")?;
    let user_runtime_dir = app_data_dir.join("runtime/current");
    let shared_runtime = shared_runtime_dir();
    let selected_runtime_dir = choose_runtime_dir(
        &shared_runtime,
        runtime_dir_is_usable(&shared_runtime),
        &user_runtime_dir,
        runtime_dir_is_usable(&user_runtime_dir),
    );
    Ok(runtime_paths_for_dir(app_data_dir, selected_runtime_dir))
}

fn read_runtime_manifest(paths: &RuntimePaths) -> Option<RuntimeManifest> {
    let data = fs::read_to_string(&paths.manifest_path).ok()?;
    serde_json::from_str(&data).ok()
}

fn read_runtime_manifest_from_path(path: &Path) -> Option<RuntimeManifest> {
    let data = fs::read_to_string(path).ok()?;
    serde_json::from_str(&data).ok()
}

fn runtime_version_rank(version: &str) -> Option<(Version, u64)> {
    let trimmed = version.trim();
    if trimmed.is_empty() {
        return None;
    }

    if let Some((base, runtime_rev)) = trimmed.split_once("-runtime") {
        let base_version = Version::parse(base.trim()).ok()?;
        let runtime_rev = runtime_rev.trim().parse::<u64>().ok().unwrap_or(0);
        return Some((base_version, runtime_rev));
    }

    Version::parse(trimmed).ok().map(|base| (base, 0))
}

fn compare_runtime_manifests(
    shared_manifest: Option<&RuntimeManifest>,
    user_manifest: Option<&RuntimeManifest>,
) -> std::cmp::Ordering {
    match (
        shared_manifest.and_then(|manifest| runtime_version_rank(&manifest.version)),
        user_manifest.and_then(|manifest| runtime_version_rank(&manifest.version)),
    ) {
        (Some(shared_rank), Some(user_rank)) => shared_rank.cmp(&user_rank),
        _ => std::cmp::Ordering::Equal,
    }
}

fn expected_runtime_url(config: &ReleaseConfig) -> String {
    format!(
        "https://github.com/{}/{}/releases/download/{}{}/{}",
        config.repo_owner,
        config.repo_name,
        config.release_tag_prefix,
        config.runtime_version,
        config.runtime_asset_name
    )
}

fn update_manifest_url(config: &ReleaseConfig) -> String {
    format!(
        "https://github.com/{}/{}/releases/latest/download/{}",
        config.repo_owner, config.repo_name, config.update_manifest_name
    )
}

fn current_platform_key() -> &'static str {
    match std::env::consts::ARCH {
        "aarch64" | "arm64" => "darwin-aarch64",
        _ => "darwin-x86_64",
    }
}

fn local_runtime_version(app: &AppHandle) -> Option<String> {
    let paths = resolve_runtime_paths(app).ok()?;
    read_runtime_manifest(&paths).map(|m| m.version)
}

fn shared_runtime_matches_expected(expected_version: &str) -> bool {
    let shared_runtime = shared_runtime_dir();
    runtime_dir_is_usable(&shared_runtime)
        && read_runtime_manifest_from_path(&shared_runtime.join("runtime-manifest.json"))
            .map(|manifest| manifest.version.trim() == expected_version.trim())
            .unwrap_or(false)
}

fn shared_runtime_paths(app: &AppHandle) -> Result<RuntimePaths> {
    let app_data_dir = app.path().app_data_dir().context("missing app_data_dir")?;
    Ok(runtime_paths_for_dir(app_data_dir, shared_runtime_dir()))
}

fn offline_install_marker_is_current(marker: &InstallSourceMarker, expected_runtime: &str) -> bool {
    marker.source == InstallSource::PkgOffline
        && marker
            .runtime_version
            .as_deref()
            .map(|version| version.trim() == expected_runtime.trim())
            .unwrap_or(false)
}

fn parse_asset_review_mode(value: &str) -> Result<AssetReviewMode> {
    match value.trim().to_ascii_lowercase().as_str() {
        "install" => Ok(AssetReviewMode::Install),
        "repair" => Ok(AssetReviewMode::Repair),
        "update" => Ok(AssetReviewMode::Update),
        other => Err(anyhow!("unknown asset review mode: {other}")),
    }
}

fn current_app_version() -> Option<Version> {
    Version::parse(env!("CARGO_PKG_VERSION")).ok()
}

fn app_version_from_bundle(path: &Path) -> Option<Version> {
    let plist = path.join("Contents/Info.plist");
    if !plist.exists() {
        return None;
    }
    let output = Command::new("/usr/bin/plutil")
        .arg("-extract")
        .arg("CFBundleShortVersionString")
        .arg("raw")
        .arg("-o")
        .arg("-")
        .arg(&plist)
        .output()
        .ok()?;
    if !output.status.success() {
        return None;
    }
    let value = String::from_utf8(output.stdout).ok()?;
    Version::parse(value.trim()).ok()
}

fn user_runtime_dir(app: &AppHandle) -> Result<PathBuf> {
    Ok(app
        .path()
        .app_data_dir()
        .context("missing app_data_dir")?
        .join("runtime/current"))
}

fn user_runtime_root(app: &AppHandle) -> Result<PathBuf> {
    Ok(user_runtime_dir(app)?
        .parent()
        .map(Path::to_path_buf)
        .unwrap_or_else(|| {
            app.path()
                .app_data_dir()
                .unwrap_or_default()
                .join("runtime")
        }))
}

fn runtime_dir_for_kind(app: &AppHandle, kind: DetectedAssetKind) -> Result<PathBuf> {
    match kind {
        DetectedAssetKind::SharedRuntime => Ok(shared_runtime_dir()),
        DetectedAssetKind::UserRuntime => user_runtime_dir(app),
        other => Err(anyhow!("asset kind {:?} is not a runtime dir", other)),
    }
}

fn runtime_root_for_kind(app: &AppHandle, kind: DetectedAssetKind) -> Result<PathBuf> {
    let current = runtime_dir_for_kind(app, kind)?;
    Ok(current
        .parent()
        .map(Path::to_path_buf)
        .unwrap_or_else(|| current))
}

fn merge_asset_decisions(
    payload: &AssetReviewPayload,
    decisions: &HashMap<String, AssetDecision>,
) -> HashMap<String, AssetDecision> {
    let mut merged = payload.default_selections.clone();
    for (key, value) in decisions {
        merged.insert(key.clone(), *value);
    }
    merged
}

fn decision_for_kind(
    decisions: &HashMap<String, AssetDecision>,
    kind: DetectedAssetKind,
) -> AssetDecision {
    decisions
        .get(kind.key())
        .copied()
        .unwrap_or(AssetDecision::Keep)
}

fn join_asset_paths(paths: &[PathBuf]) -> String {
    paths
        .iter()
        .map(|path| path.to_string_lossy().to_string())
        .collect::<Vec<_>>()
        .join("\n")
}

fn runtime_inventory_item(
    kind: DetectedAssetKind,
    path: &Path,
    target_runtime_version: Option<&str>,
) -> Option<AssetInventoryItem> {
    let exists = path.exists() || path.parent().map(|parent| parent.exists()).unwrap_or(false);
    if !exists {
        return None;
    }
    let manifest = read_runtime_manifest_from_path(&path.join("runtime-manifest.json"));
    let usable = runtime_dir_is_usable(path);
    let state = if usable {
        if let (Some(target), Some(manifest)) = (target_runtime_version, manifest.as_ref()) {
            if !target.trim().is_empty() && manifest.version.trim() != target.trim() {
                DetectedAssetState::Outdated
            } else {
                DetectedAssetState::Healthy
            }
        } else {
            DetectedAssetState::Healthy
        }
    } else {
        DetectedAssetState::Broken
    };
    let version_copy = manifest
        .as_ref()
        .map(|manifest| format!("当前版本 {}", manifest.version))
        .unwrap_or_else(|| "结构不完整或缺少运行文件".to_string());
    Some(AssetInventoryItem {
        kind,
        label: match kind {
            DetectedAssetKind::SharedRuntime => "共享本机组件".to_string(),
            DetectedAssetKind::UserRuntime => "当前用户本机组件".to_string(),
            _ => "本机组件".to_string(),
        },
        path: path.to_string_lossy().to_string(),
        state,
        replace_recommended: state != DetectedAssetState::Healthy,
        requires_admin: matches!(kind, DetectedAssetKind::SharedRuntime),
        details: version_copy,
    })
}

fn build_asset_review_payload(
    app: &AppHandle,
    mode: AssetReviewMode,
    target_app_version: Option<Version>,
    target_runtime_version: Option<String>,
) -> Result<AssetReviewPayload> {
    let config = load_release_config(app)?;
    let mut items = Vec::new();
    let mut default_selections = HashMap::new();
    let current_bundle = app_bundle_path();

    let app_asset_path = match mode {
        AssetReviewMode::Update => current_bundle.clone(),
        AssetReviewMode::Install | AssetReviewMode::Repair => {
            let target = installed_app_target_path();
            target.exists().then_some(target)
        }
    };
    if let Some(path) = app_asset_path {
        let bundle_version = app_version_from_bundle(&path);
        let state = if let (Some(target), Some(existing)) =
            (target_app_version.as_ref(), bundle_version.as_ref())
        {
            if existing < target {
                DetectedAssetState::Outdated
            } else {
                DetectedAssetState::Healthy
            }
        } else {
            DetectedAssetState::Healthy
        };
        let current_bundle_copy = current_bundle
            .as_ref()
            .filter(|bundle| bundle.as_path() != path)
            .map(|bundle| format!("当前运行副本位于 {}", bundle.display()))
            .unwrap_or_else(|| "当前将以这个 app 作为替换目标".to_string());
        items.push(AssetInventoryItem {
            kind: DetectedAssetKind::InstalledApp,
            label: "已安装 app".to_string(),
            path: path.to_string_lossy().to_string(),
            state,
            replace_recommended: state == DetectedAssetState::Outdated
                || matches!(mode, AssetReviewMode::Install)
                    && current_bundle
                        .as_ref()
                        .map(|bundle| bundle.as_path() != path)
                        .unwrap_or(false),
            requires_admin: target_requires_admin_update(&path),
            details: bundle_version
                .map(|version| format!("已安装版本 {}。{}", version, current_bundle_copy))
                .unwrap_or(current_bundle_copy),
        });
    }

    if let Some(item) = runtime_inventory_item(
        DetectedAssetKind::SharedRuntime,
        &shared_runtime_dir(),
        target_runtime_version.as_deref(),
    ) {
        items.push(item);
    }
    if let Some(item) = runtime_inventory_item(
        DetectedAssetKind::UserRuntime,
        &user_runtime_dir(app)?,
        target_runtime_version.as_deref(),
    ) {
        items.push(item);
    }

    let shared_runtime_is_healthy = items.iter().any(|item| {
        item.kind == DetectedAssetKind::SharedRuntime && item.state == DetectedAssetState::Healthy
    });
    if shared_runtime_is_healthy
        && matches!(mode, AssetReviewMode::Install | AssetReviewMode::Repair)
    {
        if let Some(item) = items
            .iter_mut()
            .find(|item| item.kind == DetectedAssetKind::UserRuntime)
        {
            item.replace_recommended = false;
        }
    }

    let pending_marker = shared_runtime_pending_path();
    if pending_marker.exists() {
        items.push(AssetInventoryItem {
            kind: DetectedAssetKind::PendingMarker,
            label: "待处理安装标记".to_string(),
            path: pending_marker.to_string_lossy().to_string(),
            state: DetectedAssetState::Pending,
            replace_recommended: true,
            requires_admin: true,
            details: "这表示上一次安装或修复没有完全收尾，建议清理后再继续。".to_string(),
        });
    }

    let runtime_cache_paths = [
        cached_runtime_archive_path(app, &config)?,
        shared_downloads_dir().join(&config.runtime_asset_name),
    ]
    .into_iter()
    .filter(|path| path.exists())
    .collect::<Vec<_>>();
    if !runtime_cache_paths.is_empty() {
        items.push(AssetInventoryItem {
            kind: DetectedAssetKind::CachedRuntimeArchive,
            label: "已下载的本机组件归档".to_string(),
            path: join_asset_paths(&runtime_cache_paths),
            state: DetectedAssetState::CacheOnly,
            replace_recommended: true,
            requires_admin: runtime_cache_paths
                .iter()
                .any(|path| path.starts_with(shared_assets_root())),
            details: "这些归档会在本次替换时重新下载或重新整理。".to_string(),
        });
    }

    let app_update_cache = cached_app_update_path(app, &config)?;
    if app_update_cache.exists() {
        items.push(AssetInventoryItem {
            kind: DetectedAssetKind::CachedAppUpdate,
            label: "已下载的 app 更新包".to_string(),
            path: app_update_cache.to_string_lossy().to_string(),
            state: DetectedAssetState::CacheOnly,
            replace_recommended: true,
            requires_admin: false,
            details: "这是之前缓存的 app 更新包，替换前可选择清理。".to_string(),
        });
    }

    for item in &items {
        default_selections.insert(
            item.kind.key().to_string(),
            if item.replace_recommended {
                AssetDecision::Replace
            } else {
                AssetDecision::Keep
            },
        );
    }

    let mut payload = AssetReviewPayload {
        mode,
        items,
        blocking_issues: Vec::new(),
        default_selections,
    };
    payload.blocking_issues = validate_asset_review_payload(app, &payload, &HashMap::new())?;
    Ok(payload)
}

fn validate_asset_review_payload(
    app: &AppHandle,
    payload: &AssetReviewPayload,
    decisions: &HashMap<String, AssetDecision>,
) -> Result<Vec<String>> {
    let merged = merge_asset_decisions(payload, decisions);
    let shared_kept_usable = decision_for_kind(&merged, DetectedAssetKind::SharedRuntime)
        == AssetDecision::Keep
        && runtime_dir_is_usable(&shared_runtime_dir());
    let user_kept_usable = decision_for_kind(&merged, DetectedAssetKind::UserRuntime)
        == AssetDecision::Keep
        && runtime_dir_is_usable(&user_runtime_dir(app)?);
    let shared_replace =
        decision_for_kind(&merged, DetectedAssetKind::SharedRuntime) == AssetDecision::Replace;
    let user_replace =
        decision_for_kind(&merged, DetectedAssetKind::UserRuntime) == AssetDecision::Replace;

    let mut issues = Vec::new();
    if matches!(
        payload.mode,
        AssetReviewMode::Install | AssetReviewMode::Repair
    ) && !shared_kept_usable
        && !user_kept_usable
        && !shared_replace
        && !user_replace
    {
        issues.push("当前没有可复用的本机组件。请至少替换一份本机组件后再继续。".to_string());
    }

    if payload.mode == AssetReviewMode::Update {
        let app_replace =
            decision_for_kind(&merged, DetectedAssetKind::InstalledApp) == AssetDecision::Replace;
        if !app_replace && !shared_replace && !user_replace {
            issues.push(
                "这次更新没有选择任何要替换的资产。请至少选择 app 或本机组件，或直接取消。"
                    .to_string(),
            );
        }
    }

    Ok(issues)
}

fn should_present_review(app: &AppHandle, payload: &AssetReviewPayload) -> bool {
    if payload.items.is_empty() {
        return false;
    }
    let has_replacement_candidate = payload.items.iter().any(|item| {
        item.state != DetectedAssetState::CacheOnly
            && (item.replace_recommended || item.state == DetectedAssetState::Broken)
    });
    let preferences = load_preferences(app);
    (preferences.always_review_before_replace && has_replacement_candidate)
        || has_replacement_candidate
        || !payload.blocking_issues.is_empty()
}

fn unix_ts() -> u64 {
    SystemTime::now()
        .duration_since(UNIX_EPOCH)
        .unwrap_or_else(|_| Duration::from_secs(0))
        .as_secs()
}

fn cache_busted_url(url: &str) -> String {
    let separator = if url.contains('?') { '&' } else { '?' };
    format!("{url}{separator}ts={}", unix_ts())
}

fn normalize_checksum(value: Option<String>) -> Option<String> {
    value
        .map(|text| text.trim().to_ascii_lowercase())
        .filter(|text| !text.is_empty())
}

fn build_github_client(timeout_secs: u64) -> Result<Client> {
    Client::builder()
        .timeout(Duration::from_secs(timeout_secs))
        .build()
        .context("build http client")
}

fn sha256_digest(path: &Path) -> Result<String> {
    let mut file = File::open(path).with_context(|| format!("open {}", path.display()))?;
    let mut hasher = Sha256::new();
    let mut buffer = [0u8; 64 * 1024];
    loop {
        let read = file.read(&mut buffer)?;
        if read == 0 {
            break;
        }
        hasher.update(&buffer[..read]);
    }
    Ok(format!("{:x}", hasher.finalize()))
}

fn verify_sha256(path: &Path, expected: Option<&str>, label: &str) -> Result<()> {
    let Some(expected) = expected.map(|value| value.trim().to_ascii_lowercase()) else {
        return Ok(());
    };
    if expected.is_empty() {
        return Ok(());
    }
    let actual = sha256_digest(path)?;
    if actual != expected {
        return Err(anyhow!(
            "{} 校验失败: expected {}, got {}",
            label,
            expected,
            actual
        ));
    }
    Ok(())
}

fn resolve_update_plan(client: &Client, app: &AppHandle) -> Result<UpdatePlan> {
    let config = load_release_config(app)?;
    let platform_key = current_platform_key();

    let manifest_url = cache_busted_url(&update_manifest_url(&config));
    if let Ok(response) = client
        .get(&manifest_url)
        .header("User-Agent", "HorosaDesktop")
        .header("Cache-Control", "no-cache")
        .header("Pragma", "no-cache")
        .send()
    {
        if response.status().is_success() {
            if let Ok(manifest) = response.json::<UpdateManifest>() {
                if let Some(platform) = manifest.platforms.get(platform_key) {
                    let latest = Version::parse(manifest.version.trim())?;
                    let repo_url = format!(
                        "https://github.com/{}/{}",
                        config.repo_owner, config.repo_name
                    );
                    let release_tag = manifest
                        .tag
                        .clone()
                        .unwrap_or_else(|| format!("{}{}", config.release_tag_prefix, latest));
                    let release_url = format!("{}/releases/tag/{}", repo_url, release_tag);
                    return Ok(UpdatePlan {
                        latest_version: latest,
                        notes: manifest
                            .notes
                            .unwrap_or_else(|| "See GitHub release notes.".to_string()),
                        repo_url,
                        release_url,
                        app_url: platform.app_url.clone(),
                        app_sha256: normalize_checksum(platform.app_sha256.clone()),
                        runtime_url: platform.runtime_url.clone(),
                        runtime_version: platform.runtime_version.clone(),
                        runtime_sha256: normalize_checksum(platform.runtime_sha256.clone()),
                        source: UpdateSource::Manifest,
                    });
                }
            }
        }
    }

    let api = format!(
        "https://api.github.com/repos/{}/{}/releases/latest",
        config.repo_owner, config.repo_name
    );
    let release = client
        .get(&api)
        .header("User-Agent", "HorosaDesktop")
        .header("Cache-Control", "no-cache")
        .header("Pragma", "no-cache")
        .send()?
        .error_for_status()?
        .json::<GithubRelease>()?;
    let latest = parse_version(&release.tag_name)?;
    let repo_url = format!(
        "https://github.com/{}/{}",
        config.repo_owner, config.repo_name
    );
    let asset = release
        .assets
        .iter()
        .find(|asset| asset.name == config.desktop_asset_name)
        .ok_or_else(|| anyhow!("desktop asset {} not found", config.desktop_asset_name))?;
    let runtime_asset = release
        .assets
        .iter()
        .find(|asset| asset.name == config.runtime_asset_name);
    Ok(UpdatePlan {
        latest_version: latest.clone(),
        notes: release.body.unwrap_or_default(),
        repo_url: repo_url.clone(),
        release_url: release
            .html_url
            .clone()
            .unwrap_or_else(|| format!("{}/releases/tag/{}", repo_url, release.tag_name)),
        app_url: asset.browser_download_url.clone(),
        app_sha256: None,
        runtime_url: runtime_asset.map(|asset| asset.browser_download_url.clone()),
        runtime_version: runtime_asset.map(|_| latest.to_string()),
        runtime_sha256: None,
        source: UpdateSource::GithubApi,
    })
}

fn ensure_dir(path: &Path) -> Result<()> {
    fs::create_dir_all(path).with_context(|| format!("mkdir -p {}", path.display()))
}

fn tmp_download_path(app_name: &str, suffix: &str) -> PathBuf {
    let ts = SystemTime::now()
        .duration_since(UNIX_EPOCH)
        .unwrap_or_else(|_| Duration::from_secs(0))
        .as_secs();
    std::env::temp_dir().join(format!("{}-{}-{}", app_name, ts, suffix))
}

fn download_with_progress(
    window: &WebviewWindow,
    url: &str,
    dest: &Path,
    start_pct: u8,
    end_pct: u8,
    label: &str,
) -> Result<()> {
    let mut last_err = None;
    for attempt in 1..=DOWNLOAD_MAX_ATTEMPTS {
        if attempt > 1 {
            let retry_msg = format!(
                "{} 失败，正在重试（{}/{}）…",
                label, attempt, DOWNLOAD_MAX_ATTEMPTS
            );
            emit_status(window, &retry_msg);
            emit_progress(window, start_pct, &retry_msg);
            thread::sleep(Duration::from_secs((attempt as u64 - 1) * 2));
        }
        match download_with_progress_once(window, url, dest, start_pct, end_pct, label) {
            Ok(()) => return Ok(()),
            Err(err) => {
                last_err = Some(err);
                let _ = fs::remove_file(dest);
            }
        }
    }
    let err = last_err.unwrap_or_else(|| anyhow!("download failed without error detail"));
    Err(wrap_download_error(label, url, err))
}

fn download_with_progress_once(
    window: &WebviewWindow,
    url: &str,
    dest: &Path,
    start_pct: u8,
    end_pct: u8,
    label: &str,
) -> Result<()> {
    let client = build_github_client(900)?;
    let mut response = client
        .get(url)
        .header("User-Agent", "HorosaDesktop")
        .header("Cache-Control", "no-cache")
        .header("Pragma", "no-cache")
        .send()
        .with_context(|| format!("download {}", url))?;
    if !response.status().is_success() {
        return Err(anyhow!("download failed: {} -> {}", url, response.status()));
    }
    if let Some(parent) = dest.parent() {
        ensure_dir(parent)?;
    }
    let total = response.content_length().unwrap_or(0);
    let mut file = File::create(dest)?;
    let mut downloaded: u64 = 0;
    let mut buffer = [0u8; 64 * 1024];
    loop {
        let read = response.read(&mut buffer)?;
        if read == 0 {
            break;
        }
        file.write_all(&buffer[..read])?;
        downloaded += read as u64;
        if total > 0 {
            let ratio = downloaded as f64 / total as f64;
            let span = end_pct.saturating_sub(start_pct) as f64;
            let pct = start_pct as f64 + span * ratio;
            emit_progress(window, pct.round() as u8, label);
        }
    }
    emit_progress(window, end_pct, label);
    Ok(())
}

fn wrap_download_error(label: &str, url: &str, err: anyhow::Error) -> anyhow::Error {
    let details = format!("{err:#}");
    let lower = details.to_ascii_lowercase();
    let summary = if lower.contains("tls handshake eof") {
        format!(
            "{}失败：已自动重试 {} 次，但和 GitHub 建立安全连接时仍被中断。请稍后重试，或切换更稳定的网络后再试。",
            label, DOWNLOAD_MAX_ATTEMPTS
        )
    } else if lower.contains("timed out") || lower.contains("timeout") {
        format!(
            "{}失败：已自动重试 {} 次，但下载仍然超时。请稍后重试，或切换更稳定的网络后再试。",
            label, DOWNLOAD_MAX_ATTEMPTS
        )
    } else if lower.contains("dns")
        || lower.contains("failed to lookup")
        || lower.contains("name or service not known")
        || lower.contains("nodename nor servname")
    {
        format!(
            "{}失败：已自动重试 {} 次，但当前网络无法稳定解析 GitHub 地址。请检查网络或代理设置后再试。",
            label, DOWNLOAD_MAX_ATTEMPTS
        )
    } else {
        format!(
            "{}失败：已自动重试 {} 次仍未完成。请稍后重试；如果反复失败，请优先检查当前网络是否能访问 GitHub。",
            label, DOWNLOAD_MAX_ATTEMPTS
        )
    };
    anyhow!("{summary}\n下载地址: {url}\n原始错误: {details}")
}

fn remove_dir_if_exists(path: &Path) -> Result<()> {
    if path.exists() {
        fs::remove_dir_all(path)?;
    }
    Ok(())
}

fn extract_runtime_archive(archive_path: &Path, dest_root: &Path) -> Result<()> {
    let extract_root = dest_root.join("_extract");
    remove_dir_if_exists(&extract_root)?;
    ensure_dir(&extract_root)?;
    let tar_gz = File::open(archive_path)?;
    let decoder = GzDecoder::new(tar_gz);
    let mut archive = Archive::new(decoder);
    archive.unpack(&extract_root)?;

    let extracted_runtime = extract_root.join("runtime-payload");
    if !extracted_runtime.exists() {
        return Err(anyhow!("runtime-payload folder missing inside archive"));
    }

    let final_runtime = dest_root.join("current");
    let backup_runtime = dest_root.join("previous");
    let had_previous = final_runtime.exists();
    if final_runtime.exists() {
        remove_dir_if_exists(&backup_runtime)?;
        fs::rename(&final_runtime, &backup_runtime)?;
    }
    if let Err(err) = fs::rename(&extracted_runtime, &final_runtime) {
        if had_previous && backup_runtime.exists() {
            let _ = fs::rename(&backup_runtime, &final_runtime);
        }
        return Err(err.into());
    }
    prepare_runtime_dir(&final_runtime)?;
    remove_dir_if_exists(&backup_runtime)?;
    remove_dir_if_exists(&extract_root)?;
    Ok(())
}

fn clear_runtime_pending_marker(runtime_dir: &Path) -> Result<()> {
    if !is_shared_runtime_dir(runtime_dir) {
        return Ok(());
    }
    let pending = shared_runtime_pending_path();
    if pending.exists() {
        match fs::remove_file(&pending) {
            Ok(()) => {}
            Err(err) if err.kind() == std::io::ErrorKind::PermissionDenied => {
                eprintln!(
                    "skip removing shared pending marker without elevated privileges: {} ({})",
                    pending.display(),
                    err
                );
            }
            Err(err) => {
                return Err(err)
                    .with_context(|| format!("remove pending marker {}", pending.display()));
            }
        }
    }
    Ok(())
}

fn selected_runtime_roots(
    app: &AppHandle,
    decisions: &HashMap<String, AssetDecision>,
) -> Result<Vec<PathBuf>> {
    let mut roots = Vec::new();
    if decision_for_kind(decisions, DetectedAssetKind::SharedRuntime) == AssetDecision::Replace {
        roots.push(runtime_root_for_kind(
            app,
            DetectedAssetKind::SharedRuntime,
        )?);
    }
    if decision_for_kind(decisions, DetectedAssetKind::UserRuntime) == AssetDecision::Replace {
        roots.push(runtime_root_for_kind(app, DetectedAssetKind::UserRuntime)?);
    }
    Ok(roots)
}

fn kept_runtime_available(
    app: &AppHandle,
    decisions: &HashMap<String, AssetDecision>,
) -> Result<bool> {
    let shared_ok = decision_for_kind(decisions, DetectedAssetKind::SharedRuntime)
        == AssetDecision::Keep
        && runtime_dir_is_usable(&shared_runtime_dir());
    let user_ok = decision_for_kind(decisions, DetectedAssetKind::UserRuntime)
        == AssetDecision::Keep
        && runtime_dir_is_usable(&user_runtime_dir(app)?);
    Ok(shared_ok || user_ok)
}

fn ensure_runtime_installed(
    app: &AppHandle,
    window: &WebviewWindow,
    force: bool,
) -> Result<RuntimePaths> {
    let config = load_release_config(app)?;
    if let Some(marker) = load_install_source_marker() {
        if offline_install_marker_is_current(&marker, &config.runtime_version) {
            if shared_runtime_matches_expected(&config.runtime_version) {
                if force {
                    return Err(anyhow!(
                        "检测到当前来自离线安装包，且共享本机组件已经完整可用。如需重装，请重新运行离线安装包；当前不会转为联网下载。"
                    ));
                }
                emit_launcher_state(window, &build_offline_ready_state(&config));
                let shared_paths = shared_runtime_paths(app)?;
                clear_runtime_pending_marker(&shared_paths.runtime_dir)?;
                emit_mode(window, "launch");
                emit_progress(window, 36, "离线安装已准备完成，可直接打开使用");
                emit_status(
                    window,
                    &format!(
                        "离线安装包已准备好本机组件 {}，本次不会联网下载。",
                        config.runtime_version
                    ),
                );
                return Ok(shared_paths);
            }
            return Err(anyhow!(
                "检测到当前来自离线安装包，但共享本机组件缺失、损坏或版本不完整。请重新安装离线包；当前不会转为联网下载。"
            ));
        }
    }

    let mut paths = resolve_runtime_paths(app)?;
    ensure_dir(&paths.app_data_dir)?;
    ensure_dir(&paths.logs_dir)?;

    let current = read_runtime_manifest(&paths);
    let review_mode = if force {
        AssetReviewMode::Repair
    } else if current.is_some() || runtime_dir_has_required_files(&paths.runtime_dir) {
        AssetReviewMode::Repair
    } else {
        AssetReviewMode::Install
    };
    let review_payload = build_asset_review_payload(
        app,
        review_mode,
        current_app_version(),
        Some(config.runtime_version.clone()),
    )?;
    let mut decisions = review_payload.default_selections.clone();
    if should_present_review(app, &review_payload) {
        if current_install_source(&config) == Some(InstallSource::PkgOffline) {
            emit_launcher_state(window, &build_offline_review_state(review_mode));
        }
        emit_mode(
            window,
            match review_mode {
                AssetReviewMode::Install => "install",
                AssetReviewMode::Repair => "repair",
                AssetReviewMode::Update => "update",
            },
        );
        emit_status(
            window,
            &format!(
                "已检测到已安装内容，等待你确认本次{}。",
                review_mode.title()
            ),
        );
        emit_progress(window, 12, review_mode.progress_copy());
        decisions = wait_for_asset_review(app, window, &review_payload)?
            .ok_or_else(|| anyhow!("已取消本次{}", review_mode.title()))?;
        for line in clear_selected_assets_internal(app, &decisions)? {
            emit_status(window, &line);
        }
        if let Some(line) = replace_installed_app_if_selected(&decisions)? {
            emit_status(window, &line);
        }
    }

    paths = resolve_runtime_paths(app)?;
    let refreshed_current = read_runtime_manifest(&paths);
    let refreshed_ok = refreshed_current
        .as_ref()
        .map(|m| m.version == config.runtime_version)
        .unwrap_or(false)
        && runtime_dir_is_usable(&paths.runtime_dir);
    let selected_roots = selected_runtime_roots(app, &decisions)?;
    if refreshed_ok && !force && selected_roots.is_empty() {
        clear_runtime_pending_marker(&paths.runtime_dir)?;
        emit_mode(window, "launch");
        emit_progress(
            window,
            36,
            &format!("检测到本机组件 {} 已可直接使用", config.runtime_version),
        );
        if let Some(m) = refreshed_current {
            emit_status(
                window,
                &format!("当前本机组件版本: {} ({})", m.version, m.built_at),
            );
        }
        return Ok(paths);
    }

    if selected_roots.is_empty() && kept_runtime_available(app, &decisions)? {
        emit_progress(window, 36, "保留当前已安装内容并继续启动");
        emit_status(window, "你选择保留可复用的本机组件，本次不会重新下载。");
        return resolve_runtime_paths(app);
    }

    let install_roots = if selected_roots.is_empty() {
        vec![user_runtime_root(app)?]
    } else {
        selected_roots
    };
    if matches!(review_mode, AssetReviewMode::Repair) {
        emit_launcher_state(window, &build_repair_in_progress_state());
    }
    emit_mode(
        window,
        match review_mode {
            AssetReviewMode::Install => "install",
            AssetReviewMode::Repair => "repair",
            AssetReviewMode::Update => "update",
        },
    );
    emit_status(window, "开始准备 星阙 本机组件…");
    emit_progress(window, 18, "准备本机组件");
    let archive_path = cached_runtime_archive_path(app, &config)?;
    let runtime_url = expected_runtime_url(&config);
    download_with_progress(window, &runtime_url, &archive_path, 8, 56, "准备本机组件")?;
    emit_status(window, "组件归档已就绪，正在部署本机组件…");
    emit_progress(window, 62, "部署本机组件");
    for runtime_root in &install_roots {
        ensure_dir(runtime_root)?;
        extract_runtime_archive(&archive_path, runtime_root)?;
        clear_runtime_pending_marker(&runtime_root.join("current"))?;
    }
    emit_progress(window, 74, "本机组件已准备完成");
    Ok(resolve_runtime_paths(app)?)
}

fn choose_free_port() -> Result<u16> {
    let listener = TcpListener::bind("127.0.0.1:0")?;
    let port = listener.local_addr()?.port();
    drop(listener);
    Ok(port)
}

fn choose_port_with_preference(preferred_port: u16) -> Result<u16> {
    match TcpListener::bind(("127.0.0.1", preferred_port)) {
        Ok(listener) => {
            let port = listener.local_addr()?.port();
            drop(listener);
            Ok(port)
        }
        Err(_) => choose_free_port(),
    }
}

fn start_static_server(
    frontend_dir: PathBuf,
    port: u16,
    shutdown: Arc<AtomicBool>,
) -> Result<thread::JoinHandle<()>> {
    let addr = SocketAddr::from(([127, 0, 0, 1], port));
    let server = Server::http(addr).map_err(|e| anyhow!(e.to_string()))?;
    let handle = thread::spawn(move || {
        while !shutdown.load(Ordering::Relaxed) {
            let request = match server.recv_timeout(Duration::from_millis(250)) {
                Ok(Some(req)) => req,
                Ok(None) => continue,
                Err(_) => continue,
            };
            if request.method() != &Method::Get && request.method() != &Method::Head {
                let _ = request.respond(Response::empty(StatusCode(405)));
                continue;
            }
            let url = request.url().split('?').next().unwrap_or("/");
            let rel = if url == "/" {
                "index.html".to_string()
            } else {
                url.trim_start_matches('/').to_string()
            };
            let mut target = frontend_dir.join(&rel);
            if !target.exists() {
                target = frontend_dir.join("index.html");
            }
            match fs::read(&target) {
                Ok(bytes) => {
                    let mime = from_path(&target).first_or_octet_stream().to_string();
                    let response = Response::from_data(bytes).with_header(
                        Header::from_bytes(&b"Content-Type"[..], mime.as_bytes()).unwrap(),
                    );
                    let _ = request.respond(response);
                }
                Err(_) => {
                    let _ = request.respond(Response::empty(StatusCode(404)));
                }
            }
        }
    });
    Ok(handle)
}

fn stop_runtime(paths: &RuntimePaths) {
    if !paths.stop_script.exists() {
        return;
    }
    let _ = Command::new("/bin/bash")
        .arg(&paths.stop_script)
        .current_dir(paths.runtime_dir.join("Horosa-Web"))
        .stdout(Stdio::null())
        .stderr(Stdio::null())
        .status();
}

fn start_runtime(
    paths: &RuntimePaths,
    window: &WebviewWindow,
    backend_port: u16,
    chart_port: u16,
    startup_timeout_secs: Option<u64>,
) -> Result<()> {
    ensure_dir(&paths.logs_dir)?;
    prepare_runtime_dir(&paths.runtime_dir)?;
    stop_runtime(paths);
    emit_status(window, "正在后台启动 星阙 Python / Java 服务…");
    emit_progress(window, 82, "启动本地服务");

    let python_bin = runtime_python_bin(&paths.runtime_dir);
    let java_bin = paths.runtime_dir.join("runtime/mac/java/bin/java");
    let mut command = Command::new("/bin/bash");
    command
        .arg(&paths.start_script)
        .current_dir(paths.runtime_dir.join("Horosa-Web"))
        .env("HOROSA_SKIP_UI_BUILD", "1")
        .env("HOROSA_PYTHON", python_bin)
        .env("HOROSA_JAVA_BIN", java_bin)
        .env("HOROSA_SERVER_PORT", backend_port.to_string())
        .env("HOROSA_CHART_PORT", chart_port.to_string())
        .env(
            "HOROSA_LOG_ROOT",
            paths.logs_dir.to_string_lossy().to_string(),
        )
        .env(
            "HOROSA_DIAG_DIR",
            paths.logs_dir.to_string_lossy().to_string(),
        );
    if let Some(timeout_secs) = startup_timeout_secs {
        command.env("HOROSA_STARTUP_TIMEOUT", timeout_secs.to_string());
    }
    let output = command.output().context("launch start_horosa_local.sh")?;
    if !output.status.success() {
        let stdout = String::from_utf8_lossy(&output.stdout);
        let stderr = String::from_utf8_lossy(&output.stderr);
        return Err(anyhow!(
            "星阙 backend start failed\nstdout:\n{}\nstderr:\n{}",
            stdout,
            stderr
        ));
    }
    emit_progress(window, 92, "本地服务已就绪");
    Ok(())
}

fn frontend_url(web_port: u16, backend_port: u16) -> String {
    let root = format!("http://127.0.0.1:{}", backend_port);
    format!(
        "http://127.0.0.1:{}/index.html?srv={}&v={}",
        web_port,
        urlencoding::encode(&root),
        unix_ts()
    )
}

fn open_path(path: &Path) {
    let _ = Command::new("open").arg(path).spawn();
}

fn clamp_zoom_level(value: f64) -> f64 {
    value.clamp(MIN_ZOOM, MAX_ZOOM)
}

fn set_window_zoom(app: &AppHandle, zoom: f64) -> Result<()> {
    let clamped = clamp_zoom_level(zoom);
    let window = app
        .get_webview_window(MAIN_WINDOW_LABEL)
        .context("main window missing for zoom")?;
    window.set_zoom(clamped)?;
    if let Some(state) = app.try_state::<AppState>() {
        if let Ok(mut slot) = state.zoom_level.lock() {
            *slot = clamped;
        }
    }
    Ok(())
}

fn adjust_window_zoom(app: &AppHandle, delta: f64) -> Result<()> {
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

fn shell_quote(path: &Path) -> String {
    let txt = path.to_string_lossy().replace('"', "\\\"");
    format!("\"{}\"", txt)
}

fn shell_quote_text(text: &str) -> String {
    format!("\"{}\"", text.replace('"', "\\\""))
}

fn applescript_quote_text(text: &str) -> String {
    format!("\"{}\"", text.replace('\\', "\\\\").replace('"', "\\\""))
}

fn current_uid_string() -> String {
    std::env::var("UID")
        .ok()
        .filter(|value| !value.trim().is_empty())
        .unwrap_or_else(|| {
            Command::new("/usr/bin/id")
                .arg("-u")
                .output()
                .ok()
                .and_then(|output| String::from_utf8(output.stdout).ok())
                .map(|value| value.trim().to_string())
                .filter(|value| !value.is_empty())
                .unwrap_or_else(|| "0".to_string())
        })
}

fn current_user_string() -> String {
    std::env::var("USER")
        .ok()
        .filter(|value| !value.trim().is_empty())
        .unwrap_or_else(|| {
            Command::new("/usr/bin/id")
                .arg("-un")
                .output()
                .ok()
                .and_then(|output| String::from_utf8(output.stdout).ok())
                .map(|value| value.trim().to_string())
                .filter(|value| !value.is_empty())
                .unwrap_or_else(|| "unknown".to_string())
        })
}

fn update_helper_log_path(app: &AppHandle, extract_root: &Path) -> PathBuf {
    let logs_dir = app
        .path()
        .app_data_dir()
        .map(|path| path.join("logs"))
        .unwrap_or_else(|_| extract_root.to_path_buf());
    let _ = ensure_dir(&logs_dir);
    logs_dir.join("update-installer.log")
}

fn target_requires_admin_update(target_app: &Path) -> bool {
    #[cfg(target_os = "macos")]
    {
        target_app.starts_with(Path::new("/Applications"))
    }
    #[cfg(not(target_os = "macos"))]
    {
        let _ = target_app;
        false
    }
}

fn app_bundle_path() -> Option<PathBuf> {
    let exe = std::env::current_exe().ok()?;
    for ancestor in exe.ancestors() {
        if ancestor.extension().and_then(|s| s.to_str()) == Some("app") {
            return Some(ancestor.to_path_buf());
        }
    }
    None
}

fn build_single_runtime_update_command(
    runtime_root: &Path,
    archive_path: &Path,
    runtime_version: Option<&str>,
    index: usize,
) -> String {
    format!(
        "install_runtime_{index}() {{\nRUNTIME_ROOT={runtime_root}\nWORK_ROOT=\"${{RUNTIME_ROOT}}/_update\"\nPREVIOUS_ROOT=\"${{RUNTIME_ROOT}}/previous\"\nEXPECTED_RUNTIME_VERSION={runtime_version}\nmkdir -p \"${{RUNTIME_ROOT}}\"\nrm -rf \"${{WORK_ROOT}}\"\nmkdir -p \"${{WORK_ROOT}}\"\n/usr/bin/tar -xzf {archive} -C \"${{WORK_ROOT}}\"\nif [ ! -f \"${{WORK_ROOT}}/runtime-payload/runtime-manifest.json\" ]; then\n  echo \"runtime manifest missing after extract\" >&2\n  exit 1\nfi\nACTUAL_RUNTIME_VERSION=\"$(/usr/bin/plutil -extract version raw -o - \"${{WORK_ROOT}}/runtime-payload/runtime-manifest.json\" 2>/dev/null || true)\"\nif [ -n \"${{EXPECTED_RUNTIME_VERSION}}\" ] && [ \"${{ACTUAL_RUNTIME_VERSION}}\" != \"${{EXPECTED_RUNTIME_VERSION}}\" ]; then\n  echo \"runtime version mismatch: ${{ACTUAL_RUNTIME_VERSION}} != ${{EXPECTED_RUNTIME_VERSION}}\" >&2\n  exit 1\nfi\nrm -rf \"${{PREVIOUS_ROOT}}\"\nHAD_RUNTIME=0\nif [ -d \"${{RUNTIME_ROOT}}/current\" ]; then\n  mv \"${{RUNTIME_ROOT}}/current\" \"${{PREVIOUS_ROOT}}\"\n  HAD_RUNTIME=1\nfi\nif mv \"${{WORK_ROOT}}/runtime-payload\" \"${{RUNTIME_ROOT}}/current\"; then\n  rm -rf \"${{WORK_ROOT}}\" \"${{PREVIOUS_ROOT}}\"\n  /usr/bin/xattr -dr com.apple.quarantine \"${{RUNTIME_ROOT}}/current\" >/dev/null 2>&1 || true\nelse\n  rm -rf \"${{RUNTIME_ROOT}}/current\"\n  if [ \"${{HAD_RUNTIME}}\" = \"1\" ] && [ -d \"${{PREVIOUS_ROOT}}\" ]; then\n    mv \"${{PREVIOUS_ROOT}}\" \"${{RUNTIME_ROOT}}/current\"\n  fi\n  exit 1\nfi\n}}\ninstall_runtime_{index}\n",
        index = index,
        runtime_root = shell_quote(runtime_root),
        archive = shell_quote(archive_path),
        runtime_version = shell_quote_text(runtime_version.unwrap_or(""))
    )
}

fn build_runtime_update_command(
    runtime_roots: &[PathBuf],
    archive_path: &Path,
    runtime_version: Option<&str>,
) -> String {
    runtime_roots
        .iter()
        .enumerate()
        .map(|(index, root)| {
            build_single_runtime_update_command(root, archive_path, runtime_version, index)
        })
        .collect::<Vec<_>>()
        .join("\n")
}

fn build_update_helper_script(
    update_log: &Path,
    completion_marker: &Path,
    target_app: &Path,
    app_src: &Path,
    current_uid: &str,
    current_user: &str,
    current_pid: &str,
    executable_name: &str,
    target_version: &str,
    runtime_version: Option<&str>,
    runtime_cmd: &str,
) -> String {
    format!(
        "#!/bin/bash\nset -euo pipefail\nLOG={log}\nMARKER={marker}\nTARGET={target}\nSRC={src}\nUSER_UID={user_uid}\nUSER_NAME={user_name}\nOLD_PID={old_pid}\nEXEC_NAME={exec_name}\nEXPECTED_VERSION={target_version}\nEXPECTED_RUNTIME_VERSION={runtime_version}\nAPP_DISPLAY_NAME=\"$(/usr/bin/basename \"${{TARGET}}\" .app)\"\nmkdir -p \"$(dirname \"${{LOG}}\")\"\nmkdir -p \"$(dirname \"${{MARKER}}\")\"\nexec >> \"${{LOG}}\" 2>&1\necho \"===== update helper start $(date '+%Y-%m-%d %H:%M:%S') =====\"\necho \"uid=$(/usr/bin/id -u) user=$(/usr/bin/id -un)\"\necho \"target=${{TARGET}}\"\necho \"src=${{SRC}}\"\nwait_for_old_app_exit() {{\n  if [ -z \"${{OLD_PID}}\" ] || [ \"${{OLD_PID}}\" = \"0\" ]; then\n    return 0\n  fi\n  for attempt in $(/usr/bin/seq 1 60); do\n    if ! /bin/kill -0 \"${{OLD_PID}}\" >/dev/null 2>&1; then\n      echo \"[app] old process exited\"\n      return 0\n    fi\n    sleep 1\n  done\n  echo \"[app] old process still running after wait window\"\n  return 0\n}}\n{runtime_cmd}mark_update_complete() {{\n  MARKER_DIR=\"$(dirname \"${{MARKER}}\")\"\n  /bin/mkdir -p \"${{MARKER_DIR}}\"\n  /usr/sbin/chown \"${{USER_UID}}\" \"${{MARKER_DIR}}\" >/dev/null 2>&1 || true\n  /bin/cat > \"${{MARKER}}\" <<EOF\nversion=${{EXPECTED_VERSION}}\nruntime_version=${{EXPECTED_RUNTIME_VERSION}}\ninstalled_at=$(/bin/date '+%Y-%m-%d %H:%M:%S')\nEOF\n  /usr/sbin/chown \"${{USER_UID}}\" \"${{MARKER}}\" >/dev/null 2>&1 || true\n}}\nis_target_running() {{\n  if [ -z \"${{EXEC_NAME}}\" ]; then\n    return 1\n  fi\n  /usr/bin/pgrep -f \"${{TARGET}}/Contents/MacOS/${{EXEC_NAME}}\" >/dev/null 2>&1\n}}\nwait_for_stable_relaunch() {{\n  local appeared=0\n  for wait_step in $(/usr/bin/seq 1 25); do\n    if is_target_running; then\n      appeared=1\n      break\n    fi\n    sleep 1\n  done\n  if [ \"${{appeared}}\" != \"1\" ]; then\n    echo \"[open] process never appeared\"\n    return 1\n  fi\n  for stable_step in $(/usr/bin/seq 1 10); do\n    if ! is_target_running; then\n      echo \"[open] process exited before becoming stable\"\n      return 1\n    fi\n    sleep 1\n  done\n  return 0\n}}\nactivate_app_once() {{\n  if [ -z \"${{APP_DISPLAY_NAME}}\" ]; then\n    return 0\n  fi\n  if [ \"$(/usr/bin/id -u)\" = \"${{USER_UID}}\" ]; then\n    /usr/bin/osascript -e \"tell application \\\"${{APP_DISPLAY_NAME}}\\\" to activate\" >/dev/null 2>&1 || true\n    return 0\n  fi\n  /bin/launchctl asuser \"${{USER_UID}}\" /usr/bin/osascript -e \"tell application \\\"${{APP_DISPLAY_NAME}}\\\" to activate\" >/dev/null 2>&1 || true\n}}\nopen_app_once() {{\n  if [ \"$(/usr/bin/id -u)\" = \"${{USER_UID}}\" ]; then\n    /usr/bin/open -n \"${{TARGET}}\"\n    activate_app_once\n    return 0\n  fi\n  if /bin/launchctl asuser \"${{USER_UID}}\" /usr/bin/open -n \"${{TARGET}}\"; then\n    activate_app_once\n    return 0\n  fi\n  if /usr/bin/sudo -u \"${{USER_NAME}}\" /usr/bin/open -n \"${{TARGET}}\"; then\n    activate_app_once\n    return 0\n  fi\n  /usr/bin/open -n \"${{TARGET}}\"\n  activate_app_once\n}}\nopen_app() {{\n  for attempt in $(/usr/bin/seq 1 8); do\n    echo \"[open] attempt ${{attempt}}\"\n    open_app_once || true\n    if wait_for_stable_relaunch; then\n      activate_app_once\n      echo \"[open] relaunch confirmed\"\n      return 0\n    fi\n    sleep 2\n  done\n  echo \"[open] relaunch not confirmed after retries\"\n  return 1\n}}\ninstall_app() {{\n  BACKUP_TARGET=\"${{TARGET}}.previous\"\n  for attempt in $(/usr/bin/seq 1 45); do\n    echo \"[app] attempt ${{attempt}}\"\n    rm -rf \"${{BACKUP_TARGET}}\"\n    HAD_TARGET=0\n    if [ -d \"${{TARGET}}\" ]; then\n      if mv \"${{TARGET}}\" \"${{BACKUP_TARGET}}\"; then\n        HAD_TARGET=1\n      else\n        echo \"[app] mv failed on attempt ${{attempt}}\"\n        /bin/ls -ld \"${{TARGET}}\" >/dev/null 2>&1 && /bin/ls -ld \"${{TARGET}}\"\n        sleep 1\n        continue\n      fi\n    fi\n    if /usr/bin/ditto \"${{SRC}}\" \"${{TARGET}}\"; then\n      rm -rf \"${{BACKUP_TARGET}}\"\n      /usr/bin/xattr -dr com.apple.quarantine \"${{TARGET}}\" >/dev/null 2>&1 || true\n      echo \"[app] install succeeded\"\n      return 0\n    fi\n    echo \"[app] ditto failed on attempt ${{attempt}}\"\n    rm -rf \"${{TARGET}}\"\n    if [ \"${{HAD_TARGET}}\" = \"1\" ] && [ -d \"${{BACKUP_TARGET}}\" ]; then\n      mv \"${{BACKUP_TARGET}}\" \"${{TARGET}}\" || true\n    fi\n    sleep 1\n  done\n  echo \"[app] install failed after retries\"\n  return 1\n}}\nwait_for_old_app_exit\ninstall_app\nsleep 1\nmark_update_complete\nopen_app || true\necho \"===== update helper success $(date '+%Y-%m-%d %H:%M:%S') =====\"\n",
        log = shell_quote(update_log),
        marker = shell_quote(completion_marker),
        runtime_cmd = runtime_cmd,
        target = shell_quote(target_app),
        src = shell_quote(app_src),
        user_uid = shell_quote_text(current_uid),
        user_name = shell_quote_text(current_user),
        old_pid = shell_quote_text(current_pid),
        exec_name = shell_quote_text(executable_name),
        target_version = shell_quote_text(target_version),
        runtime_version = shell_quote_text(runtime_version.unwrap_or(""))
    )
}

fn install_downloaded_app(
    app: AppHandle,
    zip_path: &Path,
    runtime_archive: Option<&Path>,
    runtime_roots: &[PathBuf],
    runtime_version: Option<&str>,
    target_version: &str,
) -> Result<()> {
    let extract_root = tmp_download_path(APP_NAME, "app-update");
    ensure_dir(&extract_root)?;
    let file = File::open(zip_path)?;
    let mut archive = ZipArchive::new(file)?;
    archive.extract(&extract_root)?;

    let mut app_src = None;
    for entry in fs::read_dir(&extract_root)? {
        let entry = entry?;
        let path = entry.path();
        if path.extension().and_then(|s| s.to_str()) == Some("app") {
            app_src = Some(path);
            break;
        }
    }
    let app_src = app_src.context("updated app bundle not found in zip")?;
    let target_app = app_bundle_path().context("current app bundle path not found")?;
    let update_log = update_helper_log_path(&app, &extract_root);
    let completion_marker = update_complete_marker_path(&app)?;
    let helper = extract_root.join("install_update.sh");
    let current_uid = current_uid_string();
    let current_user = current_user_string();
    let current_pid = std::process::id().to_string();
    let executable_name = std::env::current_exe()
        .ok()
        .and_then(|path| {
            path.file_name()
                .map(|name| name.to_string_lossy().to_string())
        })
        .unwrap_or_else(|| "horosa-desktop-installer".to_string());
    let requires_admin = target_requires_admin_update(&target_app);
    let runtime_cmd = if let Some(archive_path) = runtime_archive {
        build_runtime_update_command(runtime_roots, archive_path, runtime_version)
    } else {
        String::new()
    };
    let script = build_update_helper_script(
        &update_log,
        &completion_marker,
        &target_app,
        &app_src,
        &current_uid,
        &current_user,
        &current_pid,
        &executable_name,
        target_version,
        runtime_version,
        &runtime_cmd,
    );
    fs::write(&helper, script)?;
    #[cfg(unix)]
    {
        use std::os::unix::fs::PermissionsExt;
        let mut perms = fs::metadata(&helper)?.permissions();
        perms.set_mode(0o755);
        fs::set_permissions(&helper, perms)?;
    }
    if requires_admin {
        let command = format!("/bin/bash {}", shell_quote(&helper));
        Command::new("/usr/bin/osascript")
            .arg("-e")
            .arg(format!(
                "do shell script {} with administrator privileges",
                applescript_quote_text(&command)
            ))
            .stdout(Stdio::null())
            .stderr(Stdio::null())
            .spawn()?;
    } else {
        Command::new("/bin/bash")
            .arg(&helper)
            .stdout(Stdio::null())
            .stderr(Stdio::null())
            .spawn()?;
    }
    app.exit(0);
    Ok(())
}

fn parse_version(tag: &str) -> Result<Version> {
    let trimmed = tag.trim().trim_start_matches('v');
    Version::parse(trimmed).with_context(|| format!("parse version: {}", tag))
}

fn normalize_update_notes(notes: &str) -> String {
    let normalized = notes
        .replace(
            "
", "
",
        )
        .trim()
        .to_string();
    if normalized.is_empty() {
        return "暂无更新说明。".to_string();
    }
    let max_chars = 3200;
    let char_count = normalized.chars().count();
    if char_count <= max_chars {
        return normalized;
    }
    let trimmed: String = normalized.chars().take(max_chars).collect();
    format!(
        "{}

[更新说明较长，已截断显示。完整内容请查看 GitHub Release。]",
        trimmed.trim_end()
    )
}

fn strip_markdown_prefix(line: &str) -> &str {
    line.trim()
        .trim_start_matches('#')
        .trim_start_matches('-')
        .trim_start_matches('*')
        .trim_start_matches(char::is_numeric)
        .trim_start_matches('.')
        .trim_start_matches(')')
        .trim()
}

fn summarize_update_notes(notes: &str) -> String {
    let normalized = normalize_update_notes(notes);
    if normalized == "暂无更新说明。" {
        return normalized;
    }
    let mut items = Vec::new();
    for line in normalized.lines() {
        let clean = strip_markdown_prefix(line);
        if clean.is_empty() {
            continue;
        }
        items.push(clean.to_string());
        if items.len() >= 4 {
            break;
        }
    }
    if items.is_empty() {
        return "暂无可提炼的更新摘要。".to_string();
    }
    items.join(
        "
",
    )
}

fn format_runtime_status(local_runtime: Option<&str>, remote_runtime: Option<&str>) -> String {
    match (local_runtime, remote_runtime) {
        (Some(local), Some(remote)) if local.trim() == remote.trim() => {
            format!("{} (已是最新)", local.trim())
        }
        (Some(local), Some(remote)) => format!("{} -> {}", local.trim(), remote.trim()),
        (None, Some(remote)) => format!("未安装 -> {}", remote.trim()),
        (Some(local), None) if !local.trim().is_empty() => {
            format!("{} (远端未声明版本)", local.trim())
        }
        _ => "unknown".to_string(),
    }
}

fn format_update_check_dialog(
    current: &Version,
    latest: &Version,
    local_runtime: Option<&str>,
    remote_runtime: Option<&str>,
    runtime_needs_update: bool,
    source: UpdateSource,
    notes: &str,
    repo_url: &str,
    release_url: &str,
) -> String {
    let status = if latest > current {
        "发现可用更新"
    } else if runtime_needs_update {
        "应用已是最新，运行环境可更新"
    } else if latest == current {
        "已是最新版本"
    } else {
        "当前版本高于远端版本"
    };
    let update_source = match source {
        UpdateSource::Manifest => "固定更新清单",
        UpdateSource::GithubApi => "GitHub Releases 回退通道",
    };
    let summary = summarize_update_notes(notes);
    let changelog = normalize_update_notes(notes);
    format!(
        "检查结果
{}

当前版本
{}

新版本号
{}

运行环境
{}

更新来源
{}

更新摘要
{}

完整 Changelog
{}

GitHub 仓库
{}

Release 页面
{}",
        status,
        current,
        latest,
        format_runtime_status(local_runtime, remote_runtime),
        update_source,
        summary,
        changelog,
        repo_url,
        release_url
    )
}

fn check_for_updates(app: AppHandle) -> Result<()> {
    let client = build_github_client(90)?;
    let plan = resolve_update_plan(&client, &app)?;
    let current = Version::parse(env!("CARGO_PKG_VERSION"))?;
    let local_runtime = local_runtime_version(&app);
    let runtime_needs_update = match (&plan.runtime_version, &local_runtime) {
        (Some(remote), Some(local)) => remote.trim() != local.trim(),
        (Some(_), None) => true,
        _ => false,
    };
    let admin_update_notice = app_bundle_path()
        .filter(|path| target_requires_admin_update(path))
        .map(|_| {
            "\n\n由于当前应用安装在 /Applications，macOS 接下来会要求管理员密码来完成应用替换。"
                .to_string()
        })
        .unwrap_or_default();
    let summary = format_update_check_dialog(
        &current,
        &plan.latest_version,
        local_runtime.as_deref(),
        plan.runtime_version.as_deref(),
        runtime_needs_update,
        plan.source,
        &plan.notes,
        &plan.repo_url,
        &plan.release_url,
    );
    if plan.latest_version <= current && !runtime_needs_update {
        MessageDialog::new()
            .set_level(MessageLevel::Info)
            .set_title("更新检查结果")
            .set_description(summary)
            .set_buttons(MessageButtons::Ok)
            .show();
        return Ok(());
    }

    if plan.source == UpdateSource::Manifest
        && plan.latest_version > current
        && plan.app_sha256.is_none()
    {
        return Err(anyhow!("更新清单缺少桌面包 sha256，已停止自动更新"));
    }
    if plan.source == UpdateSource::Manifest
        && runtime_needs_update
        && plan.runtime_sha256.is_none()
    {
        return Err(anyhow!("更新清单缺少运行环境 sha256，已停止自动更新"));
    }

    let review_payload = build_asset_review_payload(
        &app,
        AssetReviewMode::Update,
        Some(plan.latest_version.clone()),
        plan.runtime_version.clone(),
    )?;
    let mut decisions = review_payload.default_selections.clone();
    if let Some(window) = app.get_webview_window(MAIN_WINDOW_LABEL) {
        emit_launcher_state(&window, &build_update_in_progress_state());
        emit_mode(&window, "update");
        emit_progress(&window, 8, "检查将替换的内容");
        emit_status(
            &window,
            &format!(
                "已获取更新信息，接下来会先审查本次要替换的资产。{}",
                admin_update_notice
            ),
        );
        if should_present_review(&app, &review_payload) {
            decisions = wait_for_asset_review(&app, &window, &review_payload)?
                .ok_or_else(|| anyhow!("已取消本次更新"))?;
            for line in clear_selected_assets_internal(&app, &decisions)? {
                emit_status(&window, &line);
            }
        }
    } else {
        let confirmed = MessageDialog::new()
            .set_level(MessageLevel::Info)
            .set_title("更新检查结果")
            .set_description(format!(
                "{summary}{admin_update_notice}\n\n当前没有主窗口可显示安装审查，将按推荐选项执行更新。是否继续？"
            ))
            .set_buttons(MessageButtons::YesNo)
            .show();
        if confirmed != MessageDialogResult::Yes {
            return Ok(());
        }
    }

    let app_should_update = plan.latest_version > current
        && decision_for_kind(&decisions, DetectedAssetKind::InstalledApp) == AssetDecision::Replace;
    let runtime_roots = if runtime_needs_update {
        selected_runtime_roots(&app, &decisions)?
    } else {
        Vec::new()
    };
    let runtime_should_update = runtime_needs_update && !runtime_roots.is_empty();
    if !app_should_update && !runtime_should_update {
        MessageDialog::new()
            .set_level(MessageLevel::Info)
            .set_title("未执行更新")
            .set_description("你保留了当前已安装内容，本次没有需要替换的资产。")
            .set_buttons(MessageButtons::Ok)
            .show();
        return Ok(());
    }

    let zip_path = cached_app_update_path(&app, &load_release_config(&app)?)?;
    if app_should_update {
        if let Some(window) = app.get_webview_window(MAIN_WINDOW_LABEL) {
            emit_status(&window, "正在下载桌面更新包…");
            download_with_progress(&window, &plan.app_url, &zip_path, 12, 52, "下载桌面更新包")?;
            emit_status(&window, "桌面更新包下载完成，正在校验…");
        } else {
            let client = build_github_client(900)?;
            let mut response = client.get(&plan.app_url).send()?.error_for_status()?;
            if let Some(parent) = zip_path.parent() {
                ensure_dir(parent)?;
            }
            let mut file = File::create(&zip_path)?;
            std::io::copy(&mut response, &mut file)?;
        }
        verify_sha256(&zip_path, plan.app_sha256.as_deref(), "桌面更新包")?;
    }

    let mut runtime_archive_path = None;
    if runtime_should_update {
        if let Some(runtime_url) = plan.runtime_url.as_ref() {
            let runtime_path = cached_runtime_archive_path(&app, &load_release_config(&app)?)?;
            if let Some(window) = app.get_webview_window(MAIN_WINDOW_LABEL) {
                emit_status(&window, "正在下载本机组件更新…");
                download_with_progress(
                    &window,
                    runtime_url,
                    &runtime_path,
                    if app_should_update { 56 } else { 18 },
                    88,
                    "下载本机组件更新",
                )?;
                emit_status(&window, "本机组件更新下载完成，正在校验…");
            } else {
                let client = build_github_client(900)?;
                let mut response = client.get(runtime_url).send()?.error_for_status()?;
                if let Some(parent) = runtime_path.parent() {
                    ensure_dir(parent)?;
                }
                let mut file = File::create(&runtime_path)?;
                std::io::copy(&mut response, &mut file)?;
            }
            verify_sha256(
                &runtime_path,
                plan.runtime_sha256.as_deref(),
                "运行环境更新包",
            )?;
            if let Some(window) = app.get_webview_window(MAIN_WINDOW_LABEL) {
                emit_progress(&window, 90, "本机组件更新已校验");
            }
            runtime_archive_path = Some(runtime_path);
        }
    }

    if app_should_update {
        if let Some(window) = app.get_webview_window(MAIN_WINDOW_LABEL) {
            emit_status(&window, "更新下载完成，准备替换应用并重开…");
            emit_progress(&window, 94, "替换应用并重开");
        }
        install_downloaded_app(
            app,
            &zip_path,
            runtime_archive_path.as_deref(),
            &runtime_roots,
            plan.runtime_version.as_deref(),
            &plan.latest_version.to_string(),
        )?;
        return Ok(());
    }

    if runtime_should_update {
        let window = app
            .get_webview_window(MAIN_WINDOW_LABEL)
            .context("main window missing for runtime-only update")?;
        emit_status(&window, "将只更新本机组件，并在当前 app 内完成重启。");
        emit_progress(&window, 92, "准备切换本机组件");
        cleanup_state(&app);
        let runtime_archive = runtime_archive_path
            .as_deref()
            .context("runtime archive missing for runtime-only update")?;
        for root in &runtime_roots {
            ensure_dir(root)?;
            extract_runtime_archive(runtime_archive, root)?;
            clear_runtime_pending_marker(&root.join("current"))?;
        }
        let app_handle = app.clone();
        let win = window.clone();
        thread::spawn(
            move || match runtime_bootstrap(app_handle.clone(), win.clone(), false) {
                Ok(session) => {
                    if let Some(state) = app_handle.try_state::<AppState>() {
                        if let Ok(mut slot) = state.session.lock() {
                            *slot = Some(session.clone());
                        }
                    }
                    emit_ready(&win, &frontend_url(session.web_port, session.backend_port));
                }
                Err(err) => {
                    emit_launcher_error(&win, &build_launcher_error_payload(&app_handle, &err))
                }
            },
        );
    }
    Ok(())
}

fn trigger_reinstall(app: AppHandle) {
    if let Some(window) = app.get_webview_window(MAIN_WINDOW_LABEL) {
        let win = window.clone();
        let app_handle = app.clone();
        thread::spawn(
            move || match runtime_bootstrap(app_handle.clone(), win.clone(), true) {
                Ok(session) => {
                    if let Some(state) = app_handle.try_state::<AppState>() {
                        if let Ok(mut slot) = state.session.lock() {
                            *slot = Some(session.clone());
                        }
                    }
                    emit_ready(&win, &frontend_url(session.web_port, session.backend_port));
                }
                Err(err) => {
                    emit_launcher_error(&win, &build_launcher_error_payload(&app_handle, &err))
                }
            },
        );
    }
}

fn cleanup_state(app: &AppHandle) {
    if let Some(state) = app.try_state::<AppState>() {
        if let Ok(mut shutdown) = state.web_shutdown.lock() {
            if let Some(flag) = shutdown.take() {
                flag.store(true, Ordering::Relaxed);
            }
        }
        if let Ok(session_slot) = state.session.lock() {
            if let Some(session) = session_slot.as_ref() {
                stop_runtime(&session.paths);
            }
        }
    }
}

fn runtime_bootstrap(
    app: AppHandle,
    window: WebviewWindow,
    force_runtime_install: bool,
) -> Result<RuntimeSession> {
    emit_mode(
        &window,
        if force_runtime_install {
            "repair"
        } else {
            "launch"
        },
    );
    emit_status(&window, "正在检查安装配置…");
    let paths = ensure_runtime_installed(&app, &window, force_runtime_install)?;
    let web_port = choose_port_with_preference(DEFAULT_FRONTEND_PORT)?;
    let mut backend_port = choose_free_port()?;
    let mut chart_port = choose_free_port()?;

    let shutdown = Arc::new(AtomicBool::new(false));
    let _server_handle =
        start_static_server(paths.frontend_dir.clone(), web_port, shutdown.clone())?;
    if let Some(state) = app.try_state::<AppState>() {
        if let Ok(mut slot) = state.web_shutdown.lock() {
            *slot = Some(shutdown);
        }
    }

    let first_launch_after_update = has_update_complete_marker(&app);
    let first_launch_timeout = if first_launch_after_update {
        Some(300)
    } else {
        None
    };
    if let Err(first_err) = start_runtime(
        &paths,
        &window,
        backend_port,
        chart_port,
        first_launch_timeout,
    ) {
        if first_launch_after_update {
            emit_status(&window, "更新后的第一次启动正在自动复检服务，请稍候…");
            emit_progress(&window, 84, "更新后首次启动自动重试");
            stop_runtime(&paths);
            thread::sleep(Duration::from_secs(3));
            backend_port = choose_free_port()?;
            chart_port = choose_free_port()?;
            start_runtime(
                &paths,
                &window,
                backend_port,
                chart_port,
                first_launch_timeout,
            )
            .map_err(|retry_err| {
                anyhow!(
                    "更新后首次启动失败，已自动重试一次仍未恢复。\n首次错误:\n{:#}\n\n重试错误:\n{:#}",
                    first_err,
                    retry_err
                )
            })?;
        } else {
            return Err(first_err);
        }
    }
    emit_progress(&window, 100, "星阙 已准备完成");
    Ok(RuntimeSession {
        paths,
        backend_port,
        web_port,
    })
}

fn main() {
    tauri::Builder::default()
        .manage(AppState::default())
        .menu(build_menu)
        .invoke_handler(tauri::generate_handler![
            load_preferences_payload,
            save_preferences_command,
            read_diagnostics_snapshot,
            scan_existing_assets,
            commit_asset_review,
            clear_selected_assets,
            perform_launcher_action,
            reveal_special_path,
            open_preferences_window_command,
            open_diagnostics_window_command,
            trigger_update_check_command,
            trigger_runtime_repair_command,
            open_login_items_settings_command
        ])
        .setup(|app| {
            let app_handle = app.handle().clone();
            let window = app
                .get_webview_window(MAIN_WINDOW_LABEL)
                .context("main window missing")?
                .clone();
            apply_saved_window_state(&window, &load_window_states(&app_handle).main);
            set_window_zoom(&app_handle, DEFAULT_ZOOM)?;
            thread::spawn(move || {
                match runtime_bootstrap(app_handle.clone(), window.clone(), false) {
                    Ok(session) => {
                        if let Some(state) = app_handle.try_state::<AppState>() {
                            if let Ok(mut slot) = state.session.lock() {
                                *slot = Some(session.clone());
                            }
                        }
                        emit_ready(
                            &window,
                            &frontend_url(session.web_port, session.backend_port),
                        );
                        show_post_update_notice_if_needed(&app_handle);
                    }
                    Err(err) => emit_launcher_error(
                        &window,
                        &build_launcher_error_payload(&app_handle, &err),
                    ),
                }
            });
            Ok(())
        })
        .on_menu_event(|app, event| {
            let id = event.id();
            if id == MENU_OPEN_PREFERENCES {
                let _ = open_preferences_window(app);
            } else if id == MENU_SHOW_MAIN_WINDOW {
                let _ = open_main_window(app);
            } else if id == MENU_SHOW_DIAGNOSTICS {
                let _ = open_diagnostics_window(app);
            } else if id == MENU_CHECK_UPDATES {
                let app_handle = app.clone();
                thread::spawn(move || {
                    if let Err(err) = check_for_updates(app_handle.clone()) {
                        MessageDialog::new()
                            .set_level(MessageLevel::Error)
                            .set_title("检查更新失败")
                            .set_description(format!("{err:#}"))
                            .set_buttons(MessageButtons::Ok)
                            .show();
                    }
                });
            } else if id == MENU_REINSTALL_RUNTIME {
                trigger_reinstall(app.clone());
            } else if id == MENU_OPEN_LOGS {
                if let Ok(paths) = resolve_runtime_paths(app) {
                    let _ = ensure_dir(&paths.logs_dir);
                    open_path(&paths.logs_dir);
                }
            } else if id == MENU_OPEN_DATA {
                if let Ok(paths) = resolve_runtime_paths(app) {
                    let _ = ensure_dir(&paths.app_data_dir);
                    open_path(&paths.app_data_dir);
                }
            } else if id == MENU_OPEN_RUNTIME {
                if let Ok(paths) = resolve_runtime_paths(app) {
                    let _ = ensure_dir(&paths.runtime_dir);
                    open_path(&paths.runtime_dir);
                }
            } else if id == MENU_RELOAD_MAIN {
                if let Some(window) = app.get_webview_window(MAIN_WINDOW_LABEL) {
                    let _ = window.eval("window.location.reload()");
                }
            } else if id == MENU_OPEN_RELEASES {
                let _ = open_release_page(app);
            } else if id == MENU_ZOOM_IN {
                let _ = adjust_window_zoom(app, ZOOM_STEP);
            } else if id == MENU_ZOOM_OUT {
                let _ = adjust_window_zoom(app, -ZOOM_STEP);
            } else if id == MENU_ZOOM_RESET {
                let _ = set_window_zoom(app, DEFAULT_ZOOM);
            }
        })
        .build(tauri::generate_context!())
        .expect("error while running 星阙 desktop shell")
        .run(|app, event| match event {
            RunEvent::WindowEvent { label, event, .. } => {
                if matches!(event, WindowEvent::Moved(_) | WindowEvent::Resized(_)) {
                    if let Some(window) = app.get_webview_window(&label) {
                        let _ = persist_window_state_for_label(app, &label, &window);
                    }
                }
            }
            RunEvent::ExitRequested { .. } => {
                cleanup_state(app);
            }
            _ => {}
        });
}

#[cfg(test)]
mod tests {
    use super::*;
    use flate2::write::GzEncoder;
    use flate2::Compression;
    use std::fs;
    use std::process::Command;
    use tar::Builder;

    #[test]
    fn saved_window_state_accepts_legacy_json_without_maximize_flag() {
        let state: SavedWindowState =
            serde_json::from_str(r#"{"width":1480.0,"height":960.0,"x":120.0,"y":80.0}"#)
                .expect("deserialize legacy window state");

        assert_eq!(state.width, Some(1480.0));
        assert_eq!(state.height, Some(960.0));
        assert_eq!(state.x, Some(120.0));
        assert_eq!(state.y, Some(80.0));
        assert_eq!(state.is_maximized, None);
    }

    fn temp_test_dir(name: &str) -> PathBuf {
        let unique = SystemTime::now()
            .duration_since(UNIX_EPOCH)
            .unwrap()
            .as_nanos();
        let path =
            std::env::temp_dir().join(format!("horosa-{}-{}-{}", name, std::process::id(), unique));
        fs::create_dir_all(&path).unwrap();
        path
    }

    fn create_runtime_archive(root: &Path, version: &str) -> PathBuf {
        let payload_root = root.join("payload/runtime-payload");
        fs::create_dir_all(&payload_root).unwrap();
        fs::write(
            payload_root.join("runtime-manifest.json"),
            format!("{{\"version\":\"{}\"}}\n", version),
        )
        .unwrap();
        fs::create_dir_all(payload_root.join("Horosa-Web")).unwrap();
        let archive_path = root.join("runtime.tar.gz");
        let tar_gz = File::create(&archive_path).unwrap();
        let encoder = GzEncoder::new(tar_gz, Compression::default());
        let mut builder = Builder::new(encoder);
        builder
            .append_dir_all("runtime-payload", &payload_root)
            .unwrap();
        builder.finish().unwrap();
        archive_path
    }

    #[test]
    fn runtime_update_command_uses_shell_resolved_manifest_path() {
        let runtime_root = Path::new("/tmp/horosa-runtime-root");
        let archive = Path::new("/tmp/horosa-runtime.tar.gz");
        let command = build_runtime_update_command(
            &[runtime_root.to_path_buf()],
            archive,
            Some("1.0.19-runtime1"),
        );
        assert!(command.contains(
            "ACTUAL_RUNTIME_VERSION=\"$(/usr/bin/plutil -extract version raw -o - \"${WORK_ROOT}/runtime-payload/runtime-manifest.json\" 2>/dev/null || true)\""
        ));
        assert!(!command
            .contains("pathlib.Path(r\"${WORK_ROOT}/runtime-payload/runtime-manifest.json\")"));
    }

    #[test]
    fn runtime_update_command_extracts_and_switches_payload() {
        let root = temp_test_dir("runtime-update-helper");
        let runtime_root = root.join("shared/runtime");
        let archive = create_runtime_archive(&root, "1.0.19-runtime1");
        let command = build_runtime_update_command(
            std::slice::from_ref(&runtime_root),
            &archive,
            Some("1.0.19-runtime1"),
        );
        let script_path = root.join("run.sh");
        fs::write(
            &script_path,
            format!(
                "#!/bin/bash\nset -euo pipefail\n{}\n[ -f \"{current}/runtime-manifest.json\" ]\nVERSION=$(/usr/bin/plutil -extract version raw -o - \"{current}/runtime-manifest.json\")\n[ \"$VERSION\" = \"1.0.19-runtime1\" ]\n",
                command,
                current = runtime_root.join("current").display()
            ),
        )
        .unwrap();
        let status = Command::new("/bin/bash")
            .arg(&script_path)
            .status()
            .unwrap();
        assert!(status.success());
        assert!(runtime_root.join("current/runtime-manifest.json").exists());
        assert!(!runtime_root.join("_update").exists());
    }

    #[test]
    fn choose_runtime_dir_prefers_shared_runtime_for_fresh_and_existing_shared_installs() {
        let shared = PathBuf::from("/Users/Shared/Horosa/runtime/current");
        let user = PathBuf::from("/tmp/horosa-user/runtime/current");

        assert_eq!(choose_runtime_dir(&shared, false, &user, false), user);
        assert_eq!(choose_runtime_dir(&shared, true, &user, false), shared);
        assert_eq!(choose_runtime_dir(&shared, false, &user, true), user);
        assert_eq!(choose_runtime_dir(&shared, true, &user, true), shared);
    }

    #[test]
    fn choose_runtime_dir_prefers_newer_runtime_when_both_are_usable() {
        let root = temp_test_dir("runtime-choose-newest");
        let shared = root.join("Users/Shared/Horosa/runtime/current");
        let user = root
            .join("Users/test/Library/Application Support/com.horacedong.horosa/runtime/current");
        fs::create_dir_all(&shared).unwrap();
        fs::create_dir_all(&user).unwrap();
        fs::write(
            shared.join("runtime-manifest.json"),
            r#"{"version":"1.0.23-runtime1","built_at":"2026-03-17 17:00:00"}"#,
        )
        .unwrap();
        fs::write(
            user.join("runtime-manifest.json"),
            r#"{"version":"1.0.12","built_at":"2026-03-11 13:58:50"}"#,
        )
        .unwrap();

        assert_eq!(choose_runtime_dir(&shared, true, &user, true), shared);

        fs::write(
            user.join("runtime-manifest.json"),
            r#"{"version":"1.0.24-runtime1","built_at":"2026-03-18 09:00:00"}"#,
        )
        .unwrap();

        assert_eq!(choose_runtime_dir(&shared, true, &user, true), user);
    }

    #[test]
    fn clear_runtime_pending_marker_only_touches_shared_runtime_marker() {
        let root = temp_test_dir("runtime-pending-clear");
        let shared_runtime = root.join("Users/Shared/Horosa/runtime/current");
        let shared_root = shared_runtime
            .parent()
            .unwrap()
            .parent()
            .unwrap()
            .to_path_buf();
        let pending = shared_root.join("runtime-install-pending.txt");
        fs::create_dir_all(shared_runtime.parent().unwrap()).unwrap();
        fs::write(&pending, "pending\n").unwrap();

        std::env::set_var("HOROSA_SHARED_RUNTIME_DIR", &shared_runtime);
        clear_runtime_pending_marker(&shared_runtime).unwrap();
        assert!(!pending.exists());

        fs::write(&pending, "pending\n").unwrap();
        let user_runtime = root.join("user/runtime/current");
        clear_runtime_pending_marker(&user_runtime).unwrap();
        assert!(pending.exists());

        fs::remove_file(&pending).unwrap();
        std::env::remove_var("HOROSA_SHARED_RUNTIME_DIR");
    }

    #[cfg(unix)]
    #[test]
    fn clear_runtime_pending_marker_ignores_permission_denied_for_shared_runtime_marker() {
        use std::os::unix::fs::PermissionsExt;

        let root = temp_test_dir("runtime-pending-clear-permissions");
        let shared_runtime = root.join("Users/Shared/Horosa/runtime/current");
        let shared_root = shared_runtime
            .parent()
            .unwrap()
            .parent()
            .unwrap()
            .to_path_buf();
        let pending = shared_root.join("runtime-install-pending.txt");
        fs::create_dir_all(shared_runtime.parent().unwrap()).unwrap();
        fs::write(&pending, "pending\n").unwrap();

        std::env::set_var("HOROSA_SHARED_RUNTIME_DIR", &shared_runtime);

        let mut perms = fs::metadata(&shared_root).unwrap().permissions();
        perms.set_mode(0o555);
        fs::set_permissions(&shared_root, perms).unwrap();

        clear_runtime_pending_marker(&shared_runtime).unwrap();
        assert!(pending.exists());

        let mut restore = fs::metadata(&shared_root).unwrap().permissions();
        restore.set_mode(0o755);
        fs::set_permissions(&shared_root, restore).unwrap();

        fs::remove_file(&pending).unwrap();
        std::env::remove_var("HOROSA_SHARED_RUNTIME_DIR");
    }

    #[test]
    fn parse_marker_kv_reads_expected_fields() {
        let values = parse_marker_kv(
            "version=1.0.25\nruntime_version=1.0.25-runtime1\ninstalled_at=2026-03-17 20:00:00\n",
        );
        assert_eq!(values.get("version").map(String::as_str), Some("1.0.25"));
        assert_eq!(
            values.get("runtime_version").map(String::as_str),
            Some("1.0.25-runtime1")
        );
        assert_eq!(
            values.get("installed_at").map(String::as_str),
            Some("2026-03-17 20:00:00")
        );
    }

    #[test]
    fn update_helper_script_waits_for_old_process_and_marks_completion() {
        let root = temp_test_dir("update-helper-script");
        let script = build_update_helper_script(
            &root.join("update.log"),
            &root.join("update-complete.txt"),
            Path::new("/Applications/星阙.app"),
            Path::new("/tmp/星阙.app"),
            "501",
            "horacedong",
            "43210",
            "horosa-desktop-installer",
            "1.0.25",
            Some("1.0.25-runtime1"),
            "",
        );
        assert!(script.contains("wait_for_old_app_exit"));
        assert!(script.contains("mark_update_complete"));
        assert!(script.contains("open -n"));
        assert!(script.contains("pgrep -f"));
        assert!(script.contains("wait_for_stable_relaunch"));
        assert!(script.contains("activate_app_once"));
        assert!(script.contains("osascript -e"));
        assert!(script.contains("EXPECTED_VERSION="));
        assert!(script.contains("1.0.25"));
        assert!(script.contains("EXPECTED_RUNTIME_VERSION="));
        assert!(script.contains("1.0.25-runtime1"));
    }
}
