#![cfg_attr(not(debug_assertions), windows_subsystem = "windows")]

use anyhow::{anyhow, Context, Result};
use base64::engine::general_purpose::STANDARD as BASE64_STANDARD;
use base64::Engine as _;
use mime_guess::from_path;
use reqwest::blocking::Client;
use rfd::{AsyncFileDialog, FileDialog};
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
use std::sync::atomic::{AtomicBool, AtomicU64, AtomicUsize, Ordering};
use std::sync::{Arc, Condvar, Mutex};
use std::thread;
use std::time::{Duration, Instant, SystemTime, UNIX_EPOCH};
use tauri::menu::{Menu, MenuItem, PredefinedMenuItem, Submenu};
use tauri::{
    AppHandle, LogicalPosition, LogicalSize, Manager, Position, RunEvent, Runtime, Size, State,
    WebviewUrl, WebviewWindow, WebviewWindowBuilder, WindowEvent,
};
use tiny_http::{Header, Method, Response, Server, StatusCode};
use walkdir::WalkDir;
use zip::ZipArchive;

// ⚠️ 本仓身份三常量必须与 tauri.conf/release_config 一致:
// APP_NAME 用于 /Applications 定位、更新解压路径、窗口标题;APP_IDENTIFIER 用于 defaults 偏好域清理;
// DEFAULT_REPO_NAME 是读不到打包配置时的更新兜底源。任何一个配错取值,
// 就会去碰其它构建的安装位/偏好域/更新通道(串台事故)。
const APP_NAME: &str = "星阙";
const APP_IDENTIFIER: &str = "com.horacedong.horosa";
const MAIN_WINDOW_LABEL: &str = "main";
const PREFERENCES_WINDOW_LABEL: &str = "preferences";
const DIAGNOSTICS_WINDOW_LABEL: &str = "diagnostics";
const MENU_CHECK_UPDATES: &str = "check_updates";
const MENU_REINSTALL_RUNTIME: &str = "reinstall_runtime";
const MENU_RESTART_SERVICES: &str = "restart_local_services";
const MENU_RELOCATE_APP: &str = "relocate_app";
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
// 修法1:backend/chart 端口冲突时最多换口重试的总尝试次数。
const PORT_RETRY_MAX: u32 = 5;
const UPDATE_COMPLETE_MARKER_NAME: &str = "update-complete.txt";
const PREFERENCES_FILE_NAME: &str = "preferences.json";
const WINDOW_STATE_FILE_NAME: &str = "window-state.json";
const WINDOW_STATE_SCHEMA_VERSION: u8 = 3;
const WINDOW_STATE_COORDINATE_SPACE: &str = "logical";
const MAIN_WINDOW_DEFAULT_SIZE: (f64, f64) = (1480.0, 960.0);
const MAIN_WINDOW_MIN_SIZE: (f64, f64) = (1180.0, 760.0);
#[cfg(target_os = "macos")]
const MACOS_LEGACY_OUTER_TO_INNER_HEIGHT_DELTA: f64 = 28.0;
const AI_ANALYSIS_IMPORT_EXTENSIONS: [&str; 6] = ["txt", "md", "markdown", "doc", "docx", "pdf"];
const AI_ANALYSIS_BACKUP_EXTENSIONS: [&str; 1] = ["zip"];
const DESKTOP_WINDOW_INIT_SCRIPT: &str = r#"
(() => {
  const noop = () => undefined;
  const lock = (name) => {
    try {
      Object.defineProperty(window, name, {
        value: noop,
        writable: false,
        configurable: false
      });
    } catch (_) {
      try { window[name] = noop; } catch (_) {}
    }
  };
  try {
    Object.defineProperty(window, "__HOROSA_DESKTOP_SHELL__", {
      value: true,
      writable: false,
      configurable: false
    });
  } catch (_) {
    try { window.__HOROSA_DESKTOP_SHELL__ = true; } catch (_) {}
  }
  lock("resizeTo");
  lock("resizeBy");
  lock("moveTo");
  lock("moveBy");
})();
"#;
#[cfg(target_os = "macos")]
const LEGACY_MACOS_WINDOW_DEFAULT_KEYS: [&str; 4] = [
    "NSWindow Frame main-workspace",
    "NSSplitView Subview Frames main-workspace, SidebarNavigationSplitView",
    "NSWindow Frame SwiftUI.ModifiedContent<SwiftUI.ModifiedContent<Horosa.RootWorkspaceView, SwiftUI._EnvironmentKeyWritingModifier<Swift.Optional<Horosa.AppModel>>>, SwiftUI._FlexFrameLayout>-1-AppWindow-1",
    "NSSplitView Subview Frames SwiftUI.ModifiedContent<SwiftUI.ModifiedContent<Horosa.RootWorkspaceView, SwiftUI._EnvironmentKeyWritingModifier<Swift.Optional<Horosa.AppModel>>>, SwiftUI._FlexFrameLayout>-1-AppWindow-1, SidebarNavigationSplitView",
];

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
    // GitHub API 恒带 size(字节);容缺以防字段变动。
    // 起 API 回退不再直接组装下载 plan(改为取回 manifest asset,或降级 notify-only),
    // 故本字段当前无消费点;保留以备将来(如发布页展示体积)。
    #[allow(dead_code)]
    #[serde(default)]
    size: Option<u64>,
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
    // manifest v2 增量部件(缺省 = 老 manifest,自动全量)
    #[serde(default)]
    components: Option<Vec<ManifestComponent>>,
    #[serde(default, rename = "componentsLockUrl")]
    components_lock_url: Option<String>,
    #[serde(default, rename = "componentsLockSha256")]
    components_lock_sha256: Option<String>,
    // 进度可视化 v2:资产体积(「提前显示要下多大」的数据源;老 manifest 缺省 None → 前端退化「大小待定」)
    #[serde(default, rename = "appSizeBytes")]
    app_size_bytes: Option<u64>,
    #[serde(default, rename = "pkgSizeBytes")]
    pkg_size_bytes: Option<u64>,
    #[serde(default, rename = "runtimeSizeBytes")]
    runtime_size_bytes: Option<u64>,
    // [U-D 防降级] manifest 级逃生阀:显式 true 才允许把 runtime 退到更旧版本
    // (全网退版应急剧本见 INCREMENTAL_UPDATE_SOP §4.3);缺省 None=false=单调防降级。
    #[serde(default, rename = "allowDowngrade")]
    allow_downgrade: Option<bool>,
}

// manifest v2 的部件条目:客户端 diff(name+sha256)与下载(url)所需;应用细节
// (paths/files/preserve)在 components-lock.json asset 里,经 lockSha256 保真。
#[derive(Debug, Clone, Serialize, Deserialize)]
struct ManifestComponent {
    name: String,
    #[serde(rename = "type")]
    kind: String, // "tree" | "files"
    sha256: String,
    #[serde(default)]
    size: Option<u64>,
    file: String,
    url: String,
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
    // manifest v2 增量部件;GithubApi 回退源恒 None(天然全量)
    components: Option<Vec<ManifestComponent>>,
    components_lock_url: Option<String>,
    components_lock_sha256: Option<String>,
    // 进度可视化 v2:资产体积(GithubApi 回退源恒 None → 前端退化)
    app_size_bytes: Option<u64>,
    runtime_size_bytes: Option<u64>,
    // [U-D 防降级] manifest allowDowngrade 透传(GithubApi 回退源恒 false)
    allow_downgrade: bool,
    source: UpdateSource,
    /// 只通知不安装:主 manifest 与 manifest asset 双双不可得 → 无 sha 可校验。
    /// 信任模型(PLAYBOOK §4)= HTTPS + sha256;缺 sha 绝不自动下载安装,只引导去发布页。
    notify_only: bool,
}

#[derive(Debug, Clone, Copy, PartialEq, Eq)]
enum UpdateSource {
    Manifest,
    /// 主 manifest URL 不可达(5xx/CDN 故障),但经 GitHub API 定位到 release 里的
    /// manifest asset 并取回 —— 完整 sha/部件信息俱在,与 Manifest 同等可信。
    ManifestViaApi,
    GithubApi,
}

#[derive(Debug, Clone, Deserialize)]
struct RuntimeManifest {
    version: String,
    built_at: String,
    // runtime 身份戳(2.6.6 起由打包脚本写入):复用前验明归属,异主 runtime 一律拒绝。
    // 旧版无戳 → None,按原版本逻辑处理(本应用历史 runtime,版本闸自会汰换)。
    #[serde(default, rename = "appName")]
    app_name: Option<String>,
}

#[derive(Debug, Clone, Serialize, Deserialize)]
#[serde(rename_all = "camelCase")]
struct RuntimeHealthCache {
    manifest_version: String,
    manifest_mtime: u64,
    python_mtime: u64,
    java_mtime: u64,
    checked_at: u64,
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
    chart_port: u16,
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
    #[serde(default = "default_zoom")]
    zoom_level: f64,
}

fn default_zoom() -> f64 {
    DEFAULT_ZOOM
}

#[derive(Debug, Clone, Serialize, Deserialize)]
#[serde(rename_all = "camelCase")]
struct AiAnalysisFilePayload {
    file_name: String,
    mime_type: String,
    base64_data: String,
    #[serde(skip_serializing_if = "Option::is_none")]
    relative_path: Option<String>,
}

#[derive(Debug, Clone, Serialize, Deserialize)]
#[serde(rename_all = "camelCase")]
struct AiAnalysisSavePayload {
    default_file_name: String,
    base64_data: String,
    #[serde(default)]
    mime_type: String,
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
    UpdateReview,
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
    // 启动账本(本次 run 的分段耗时 JSONL 尾部,四层聚合;无账本时为空)
    #[serde(default)]
    ledger_lines: Vec<String>,
    // [U-G] 耐久更新台账尾部(vX→vY 结果历史;无台账时为空)
    #[serde(default)]
    update_history_lines: Vec<String>,
}

#[derive(Debug, Clone, Serialize, Deserialize, Default)]
#[serde(rename_all = "camelCase")]
struct SavedWindowState {
    width: Option<f64>,
    height: Option<f64>,
    x: Option<f64>,
    y: Option<f64>,
    is_maximized: Option<bool>,
    #[serde(default)]
    state_version: Option<u8>,
    #[serde(default)]
    coordinate_space: Option<String>,
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
    window_state_persistence_ready: AtomicBool,
    // v2.2.1 非阻塞软件内升级:后台下载完成后暂存,等用户主动点「重启更新」时消费。
    staged_update: Mutex<Option<StagedUpdate>>,
    // 修复(更新后卡顿)C①:更新完成通知文本。runtime_bootstrap 开头对 update-complete 标记
    // 「读取即消费」(解析后立刻删除磁盘标记),把通知缓存于此;本次首启成功后再弹窗。
    // 失败时磁盘标记已删 → 下次启动不会再误走 300s 全量慢路径(杜绝「次次都慢」)。
    pending_update_notice: Mutex<Option<String>>,
}

// v2.2.1 后台已下载并校验完成、等待用户重启安装的更新。
// [U-C] 增补 Serialize/Deserialize:下载完成即落盘 staged-update.json,进程被杀/
// 用户退出后下次启动逐资产重验 sha 直接恢复「已就绪」态,免重下几百 MB。
// 全字段 #[serde(default)]:老档新壳向前兼容(缺字段=默认,恢复门自会因资产/版本不符弃档)。
#[derive(Clone, Serialize, Deserialize)]
struct StagedUpdate {
    #[serde(default)]
    zip_path: Option<PathBuf>,
    #[serde(default)]
    runtime_archive_path: Option<PathBuf>,
    #[serde(default)]
    runtime_roots: Vec<PathBuf>,
    #[serde(default)]
    runtime_version: Option<String>,
    #[serde(default)]
    target_version: String,
    #[serde(default)]
    app_should_update: bool,
    #[serde(default)]
    runtime_should_update: bool,
    // 增量部件更新(下载校验完毕):Some = 应用阶段走部件手术;None = 全量 tar。
    #[serde(default)]
    staged_components: Option<StagedComponents>,
}

// 已下载校验完成的增量部件集:new_lock 是新版 components-lock.json 全文(paths/files/
// preserve 应用细节的真值源),archives 只含 sha 有变化的部件。
#[derive(Clone, Serialize, Deserialize)]
struct StagedComponents {
    #[serde(default)]
    archives: Vec<(ManifestComponent, PathBuf)>,
    #[serde(default)]
    new_lock_json: serde_json::Value,
    #[serde(default)]
    new_lock_text: String,
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

impl Default for AppState {
    fn default() -> Self {
        Self {
            session: Mutex::new(None),
            web_shutdown: Mutex::new(None),
            zoom_level: Mutex::new(DEFAULT_ZOOM),
            review: AssetReviewCoordinator::default(),
            window_state_persistence_ready: AtomicBool::new(false),
            staged_update: Mutex::new(None),
            pending_update_notice: Mutex::new(None),
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

fn build_update_review_state() -> LauncherStatePayload {
    LauncherStatePayload {
        kind: LauncherStateKind::UpdateReview,
        badge: "发现更新".to_string(),
        title: "已获取新版本信息，等待你确认是否开始更新".to_string(),
        summary: "这一步只负责检查和展示结果；只有你明确确认后，才会开始下载与替换。".to_string(),
        detail: "如果你选择稍后再说，本次不会下载任何资产，也不会替换当前 app 或本机组件。"
            .to_string(),
        recommendation: Some("确认开始后，星阙 才会进入下载、校验与重开流程。".to_string()),
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
    let mut payload = 'built: {
        if let Ok(config) = load_release_config(app) {
            if current_install_source(&config) == Some(InstallSource::PkgOffline)
                && !shared_runtime_matches_expected(&config.runtime_version)
                && !user_runtime_matches_expected(app, &config.runtime_version).unwrap_or(false)
            {
                break 'built build_offline_repair_required_state(&config, &raw_error);
            }
        }
        build_generic_launcher_error(&raw_error)
    };
    // 全球用户自助:失败面必须给出日志的确切路径(菜单「打开日志」不一定被发现;
    // 远程求助时用户只要把这个目录打包发来即可定位)。
    if let Ok(dir) = app.path().app_data_dir() {
        payload.detail = format!(
            "{}\n诊断日志目录:{}(菜单栏「打开日志」可直达)",
            payload.detail,
            dir.join("logs").display()
        );
    }
    payload
}

fn app_downloads_dir(app: &AppHandle) -> Result<PathBuf> {
    let dir = app.path().app_data_dir().context("missing app_data_dir")?;
    Ok(dir.join("downloads"))
}

fn cached_runtime_archive_path(app: &AppHandle, config: &ReleaseConfig) -> Result<PathBuf> {
    Ok(app_downloads_dir(app)?.join(&config.runtime_asset_name))
}

fn local_runtime_archive_candidates(
    app: &AppHandle,
    config: &ReleaseConfig,
) -> Result<Vec<PathBuf>> {
    let mut candidates = Vec::new();
    let user_cached = cached_runtime_archive_path(app, config)?;
    if user_cached.exists() {
        candidates.push(user_cached);
    }
    let shared_cached = shared_downloads_dir().join(&config.runtime_asset_name);
    if shared_cached.exists() && !candidates.iter().any(|path| path == &shared_cached) {
        candidates.push(shared_cached);
    }
    Ok(candidates)
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

fn valid_scale_factor(scale_factor: f64) -> f64 {
    if scale_factor.is_finite() && scale_factor > 0.0 {
        scale_factor
    } else {
        1.0
    }
}

fn logical_value(value: f64, scale_factor: f64) -> f64 {
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

fn normalize_saved_window_state_for_apply(
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

fn effective_captured_maximized(
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

fn saved_launch_size(
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

fn saved_launch_position(state: &SavedWindowState) -> Option<(f64, f64)> {
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

#[cfg(test)]
fn should_launch_main_window_maximized(_state: &SavedWindowState) -> bool {
    false
}

fn apply_main_window_launch_state(window: &WebviewWindow, state: &SavedWindowState) {
    apply_saved_window_state(window, state);
}

fn stabilize_main_window_after_navigation(
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

fn emit_ready_and_stabilize(app: &AppHandle, window: &WebviewWindow, url: &str) {
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
}

fn set_window_state_persistence_ready(app: &AppHandle, ready: bool) {
    if let Some(state) = app.try_state::<AppState>() {
        state
            .window_state_persistence_ready
            .store(ready, Ordering::SeqCst);
    }
}

fn is_window_state_persistence_ready(app: &AppHandle) -> bool {
    app.try_state::<AppState>()
        .map(|state| state.window_state_persistence_ready.load(Ordering::SeqCst))
        .unwrap_or(true)
}

fn enable_window_state_persistence_after_launch(app: AppHandle) {
    thread::spawn(move || {
        thread::sleep(Duration::from_secs(3));
        set_window_state_persistence_ready(&app, true);
    });
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

fn persist_all_known_window_states(app: &AppHandle) {
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
fn configure_macos_native_window_restoration() {
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
fn configure_macos_native_window_restoration() {}

fn escape_js(text: &str) -> String {
    serde_json::to_string(text).unwrap_or_else(|_| "\"\"".to_string())
}

fn overlay_json(value: Option<&str>) -> String {
    value.map(escape_js).unwrap_or_else(|| "null".to_string())
}

fn overlay_bool_json(value: Option<bool>) -> String {
    match value {
        Some(true) => "true".to_string(),
        Some(false) => "false".to_string(),
        None => "null".to_string(),
    }
}

fn emit_overlay(
    window: &WebviewWindow,
    mode: Option<&str>,
    pct: Option<u8>,
    message: Option<&str>,
    error: Option<&str>,
    ready: bool,
    indeterminate: Option<bool>,
) {
    let mode = overlay_json(mode);
    let message = overlay_json(message);
    let error = overlay_json(error);
    let pct = pct
        .map(|value| value.to_string())
        .unwrap_or_else(|| "null".to_string());
    let ready = if ready { "true" } else { "false" };
    let indeterminate = overlay_bool_json(indeterminate);
    let _ = window.eval(&format!(
        r#"
(function () {{
  if (!window.__horosaInlineProgress) {{
    window.__horosaInlineProgress = (function () {{
      const STYLE_ID = 'horosa-inline-progress-style';
      const CARD_ID = 'horosa-inline-progress';
      let hideTimer = null;
      let lastMode = 'launch';
      let lastPct = 0;
      let lastIndeterminate = false;

      function isLauncherPage() {{
        return !!document.querySelector('.launcher-shell');
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
            width: min(420px, calc(100vw - 48px));
            z-index: 2147483646;
            padding: 20px 22px 18px;
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
            letter-spacing: 0;
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
            letter-spacing: 0;
            line-height: 1.35;
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
            letter-spacing: 0;
          }}
          #${{CARD_ID}} .hip-phase {{
            color: #6f7c8d;
            font-size: 12px;
            font-weight: 700;
            letter-spacing: 0;
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
          #${{CARD_ID}}[data-indeterminate="true"] .hip-fill {{
            width: 38%;
            animation: horosa-inline-progress-sweep 1.2s linear infinite;
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
          @keyframes horosa-inline-progress-sweep {{
            0% {{
              transform: translateX(-130%);
            }}
            100% {{
              transform: translateX(310%);
            }}
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

      function stepFor(text, ready, indeterminate) {{
        if (ready) return '即将完成';
        if (indeterminate && /下载|接收/.test(text || '')) return '接收资产';
        if (/校验/.test(text || '')) return '校验资产';
        if (/替换应用|重开/.test(text || '')) return '替换应用';
        if (/解压|切换|部署本机组件/.test(text || '')) return '部署组件';
        if (/运行环境更新|本机组件更新|运行环境|本机组件/.test(text || '')) return '准备组件';
        return '下载资产';
      }}

      function phaseFor(pct, text, ready, indeterminate) {{
        if (ready || pct >= 96) return '即将完成';
        if (indeterminate && /下载|接收/.test(text || '')) return '接收中';
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
        const indeterminate = payload.indeterminate == null ? lastIndeterminate : !!payload.indeterminate;
        lastMode = mode;
        const card = ensureCard();
        if (!card) return;
        if (!shouldShow(mode, text, hasError)) {{
          if (!ready) card.classList.remove('is-visible');
          return;
        }}
        card.dataset.tone = tone(mode, hasError);
        card.dataset.indeterminate = indeterminate ? 'true' : 'false';
        card.querySelector('.hip-badge-text').textContent = badgeFor(mode, hasError);
        card.querySelector('.hip-title').textContent = titleFor(mode, hasError);
        card.querySelector('.hip-copy').textContent = text || '正在处理下载与安装事务。';
        const pct = payload.pct == null ? lastPct : Math.max(0, Math.min(100, Number(payload.pct) || 0));
        lastPct = pct;
        lastIndeterminate = indeterminate;
        card.querySelector('.hip-percent').textContent = indeterminate ? '接收中' : `${{Math.round(pct)}}%`;
        card.querySelector('.hip-phase').textContent = phaseFor(pct, text, ready, indeterminate);
        card.querySelector('.hip-step').textContent = stepFor(text, ready, indeterminate);
        if (!indeterminate) {{
          card.querySelector('.hip-fill').style.width = `${{pct}}%`;
        }}
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
    ready: {ready},
    indeterminate: {indeterminate}
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
    emit_overlay(window, None, None, Some(raw_message), None, false, None);
}

fn emit_progress(window: &WebviewWindow, pct: u8, message: &str) {
    let raw_message = message;
    let message = escape_js(message);
    let _ = window.eval(&format!(
        "window.__horosaPendingProgress = {{ pct: {}, message: {}, indeterminate: false }}; \
if (window.__horosaProgress) {{ window.__horosaProgress({}, {}, false); }}",
        pct, message, pct, message
    ));
    emit_overlay(
        window,
        None,
        Some(pct),
        Some(raw_message),
        None,
        false,
        Some(false),
    );
}

// v2.2.1 非阻塞升级事件:发到主窗口的独立通道(不接管 launcher 界面)。
// 镜像既有 __horosaPending* 模式:先存 pending,前端 UpdateNotifier 挂载时若已有 handler 立即调,否则挂载时补读 pending。
// [U-G] 日志轮转保代:超限先 rename 成 <name>.1(覆盖旧 .1)再由调用方新建续写。
fn rotate_log_keep_one(path: &Path, max_bytes: u64) {
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

// [U-G 耐久更新台账] 每行一事件 JSONL——「从哪版→哪版→结果」的耐久历史,与
// updater-events.log(瞬时事件镜像,2MB 保一代)互补:staged_ready/download_error/
// apply_begin/apply_runtime_ok/helper_handoff/install_confirmed/apply_failed/
// watchdog_rollback/downgrade_blocked/check_failed。>1MB 保尾 200 行重写(量级极小)。
fn update_history_path(app: &AppHandle) -> Option<PathBuf> {
    app.path()
        .app_data_dir()
        .ok()
        .map(|d| d.join("logs").join("update-history.jsonl"))
}

fn append_update_history_at(path: &Path, mut entry: serde_json::Value) {
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

fn append_update_history(app: &AppHandle, entry: serde_json::Value) {
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

fn emit_update_event(app: &AppHandle, json: &str) {
    log_updater_event(app, json);
    if let Some(window) = app.get_webview_window(MAIN_WINDOW_LABEL) {
        emit_update_event_window(&window, json);
    }
}

/// [WS-1f] updater 事件镜像:全部更新事件带时间戳落 logs/updater-events.log
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
    // [U-G] 轮转保代:超 2MB rename→.1 再新建。旧实现 File::create 直接清零——恰在
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
fn make_applying_notifier(
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

fn emit_indeterminate_progress(window: &WebviewWindow, pct: u8, message: &str) {
    let raw_message = message;
    let message = escape_js(message);
    let _ = window.eval(&format!(
        "window.__horosaPendingProgress = {{ pct: {}, message: {}, indeterminate: true }}; \
if (window.__horosaProgress) {{ window.__horosaProgress({}, {}, true); }}",
        pct, message, pct, message
    ));
    emit_overlay(
        window,
        None,
        Some(pct),
        Some(raw_message),
        None,
        false,
        Some(true),
    );
}

fn emit_mode(window: &WebviewWindow, mode: &str) {
    let raw_mode = mode;
    let mode = escape_js(mode);
    let _ = window.eval(&format!(
        "window.__horosaPendingMode = {mode}; \
if (window.__horosaMode) {{ window.__horosaMode({mode}); }}",
    ));
    emit_overlay(window, Some(raw_mode), None, None, None, false, None);
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
        Some("已准备就绪，正在进入主界面…"),
        None,
        true,
        Some(false),
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
    emit_overlay(
        window,
        Some("error"),
        None,
        None,
        overlay_message,
        false,
        Some(false),
    );
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
    let restart_services = MenuItem::with_id(
        app,
        MENU_RESTART_SERVICES,
        "重启本地服务",
        true,
        None::<&str>,
    )?;
    // [U-I G8] Translocation 自助搬迁:zip 通道用户从「下载」直接运行时,自更新链路
    // 找不到真实 App 路径——菜单一键拷入「应用程序」并重开(菜单事件=主线程,弹确认框安全)。
    let relocate_app = MenuItem::with_id(
        app,
        MENU_RELOCATE_APP,
        "移入「应用程序」文件夹…",
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
            &restart_services,
            &relocate_app,
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

fn build_main_window(app: &AppHandle, state: &SavedWindowState) -> Result<WebviewWindow> {
    let size = saved_launch_size(state, MAIN_WINDOW_DEFAULT_SIZE, MAIN_WINDOW_MIN_SIZE);
    let mut builder =
        WebviewWindowBuilder::new(app, MAIN_WINDOW_LABEL, WebviewUrl::App("index.html".into()))
            .title(APP_NAME)
            .resizable(true)
            .inner_size(size.0, size.1)
            .min_inner_size(MAIN_WINDOW_MIN_SIZE.0, MAIN_WINDOW_MIN_SIZE.1)
            .initialization_script(DESKTOP_WINDOW_INIT_SCRIPT)
            .visible(false);
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
    // 启动账本尾部(本次 run 优先;未初始化时回落 logs 下最新的账本文件)
    let ledger_path = ledger_env().map(|(_, file)| file).or_else(|| {
        let mut newest: Option<(SystemTime, PathBuf)> = None;
        if let Ok(entries) = fs::read_dir(&paths.logs_dir) {
            for entry in entries.flatten() {
                let candidate = entry.path().join("horosa-startup-ledger.jsonl");
                if let Ok(meta) = fs::metadata(&candidate) {
                    let modified = meta.modified().unwrap_or(UNIX_EPOCH);
                    if newest.as_ref().map(|(t, _)| modified > *t).unwrap_or(true) {
                        newest = Some((modified, candidate));
                    }
                }
            }
        }
        newest.map(|(_, p)| p)
    });
    let ledger_lines = ledger_path
        .and_then(|p| fs::read_to_string(p).ok())
        .map(|text| {
            let all: Vec<String> = text.lines().map(|l| l.to_string()).collect();
            if all.len() > 100 {
                all[all.len() - 100..].to_vec()
            } else {
                all
            }
        })
        .unwrap_or_default();
    // [U-G] 耐久更新台账尾 50 行
    let update_history_lines = update_history_path(app)
        .and_then(|p| fs::read_to_string(p).ok())
        .map(|text| {
            let all: Vec<String> = text.lines().map(|l| l.to_string()).collect();
            if all.len() > 50 {
                all[all.len() - 50..].to_vec()
            } else {
                all
            }
        })
        .unwrap_or_default();
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
        ledger_lines,
        update_history_lines,
    })
}

// [U-G] 用 ditto 打 zip(全仓 Command 惯例;比 zip crate 写侧对 xattr/资源叉更稳)
fn zip_dir_with_ditto(src: &Path, out: &Path) -> Result<()> {
    let status = Command::new("/usr/bin/ditto")
        .arg("-c")
        .arg("-k")
        .arg("--sequesterRsrc")
        .arg(src)
        .arg(out)
        .stdout(Stdio::null())
        .stderr(Stdio::null())
        .status()
        .context("spawn ditto")?;
    if !status.success() {
        return Err(anyhow!("ditto 打包失败: {}", out.display()));
    }
    Ok(())
}

// [U-G] 一键导出诊断包:logs 全目录(既有留存策略控体积)+关键状态文件+系统信息
// → ~/Desktop/<app>-诊断-<ts>.zip(桌面缺失退回数据目录),并 Finder 定位。
// 非技术用户排障从「教对方翻目录」变成「发一个 zip」。
// 诊断包 Java 日志选取器(纯函数可测):按 mtime 降序拣最新文件,总量 ≤ cap;
// 超预算的大文件跳过继续拣小的(宁可多收几份小日志,不为一份巨型日志放弃其余)。
fn select_recent_files_by_mtime(root: &Path, cap_bytes: u64) -> Vec<PathBuf> {
    let mut files: Vec<(SystemTime, u64, PathBuf)> = WalkDir::new(root)
        .into_iter()
        .flatten()
        .filter(|e| e.file_type().is_file())
        .filter_map(|e| {
            let md = e.metadata().ok()?;
            Some((md.modified().ok()?, md.len(), e.into_path()))
        })
        .collect();
    files.sort_by(|a, b| b.0.cmp(&a.0));
    let mut total = 0u64;
    let mut out = Vec::new();
    for (_, len, path) in files {
        if total.saturating_add(len) > cap_bytes {
            continue;
        }
        total += len;
        out.push(path);
    }
    out
}

#[tauri::command]
fn export_diagnostics_bundle(app: AppHandle) -> std::result::Result<String, String> {
    (|| -> Result<String> {
        let data_dir = app.path().app_data_dir().context("app data dir")?;
        let staging = tmp_download_path(APP_NAME, "diag-bundle");
        ensure_dir(&staging)?;
        let logs_src = data_dir.join("logs");
        if logs_src.exists() {
            clone_dir_fast(&logs_src, &staging.join("logs"))?;
        }
        for name in [
            "launch-health.json",
            "staged-update.json",
            "last-update-check.json",
        ] {
            let src = data_dir.join(name);
            if src.exists() {
                let _ = fs::copy(&src, staging.join(name));
            }
        }
        let manifest = shared_runtime_dir().join("runtime-manifest.json");
        if manifest.exists() {
            let _ = fs::copy(&manifest, staging.join("runtime-manifest.json"));
        }
        // Java 结构化日志:log4j2 落 ~/.horosa-logs/astrostudyboot(yyyy/MM/dd 滚动),
        // 不在 app_data/logs 内 —— 此前诊断包只有重定向 stdout 的 JAVA_LOG,spring/sql
        // 滚动日志全缺。按 mtime 取最新 ≤20MB 保持相对目录进 java-logs/。
        if let Ok(home_dir) = std::env::var("HOME").map(PathBuf::from) {
            let java_logs_root = home_dir.join(".horosa-logs").join("astrostudyboot");
            if java_logs_root.exists() {
                let picked =
                    select_recent_files_by_mtime(&java_logs_root, 20 * 1024 * 1024);
                for src in picked {
                    if let Ok(rel) = src.strip_prefix(&java_logs_root) {
                        let dest = staging.join("java-logs").join(rel);
                        if let Some(parent) = dest.parent() {
                            let _ = fs::create_dir_all(parent);
                        }
                        let _ = fs::copy(&src, &dest);
                    }
                }
            }
        }
        let sw = Command::new("/usr/bin/sw_vers")
            .output()
            .map(|o| String::from_utf8_lossy(&o.stdout).to_string())
            .unwrap_or_default();
        let info = format!(
            "app={}\nshellVersion={}\nlocalRuntime={}\n{}",
            APP_NAME,
            env!("CARGO_PKG_VERSION"),
            local_runtime_version(&app).unwrap_or_default(),
            sw
        );
        fs::write(staging.join("system-info.txt"), info)?;
        let ts = SystemTime::now()
            .duration_since(UNIX_EPOCH)
            .map(|d| d.as_secs())
            .unwrap_or(0);
        let home = std::env::var("HOME")
            .map(PathBuf::from)
            .unwrap_or_else(|_| data_dir.clone());
        let desktop = home.join("Desktop");
        let out_dir = if desktop.exists() { desktop } else { data_dir };
        let out = out_dir.join(format!("{}-诊断-{}.zip", APP_NAME, ts));
        zip_dir_with_ditto(&staging, &out)?;
        let _ = remove_dir_if_exists(&staging);
        let _ = Command::new("/usr/bin/open")
            .arg("-R")
            .arg(&out)
            .stdout(Stdio::null())
            .stderr(Stdio::null())
            .status();
        Ok(out.display().to_string())
    })()
    .map_err(|e| format!("{e:#}"))
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

// 桌面剪贴板:webview 里 navigator.clipboard / execCommand 被拦,走原生剪贴板。
// [E1] 主路 arboard(NSPasteboard / CF_UNICODETEXT,Unicode 直写,跨平台同一实现);
// macOS 兜底 pbcopy——GUI .app 进程无 LANG/LC_CTYPE 时 pbcopy 按 MacRoman 解读 stdin
// (「技术」→「ÊäÄÊúØ」类乱码),必须显式钉 LC_CTYPE=UTF-8;绝对路径免 PATH 依赖。
struct DesktopClipboardState(Mutex<Option<arboard::Clipboard>>);

#[cfg(target_os = "macos")]
fn pbcopy_utf8_fallback(text: &str) -> std::result::Result<(), String> {
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
fn copy_text_to_clipboard_command(
    state: State<'_, DesktopClipboardState>,
    text: String,
) -> std::result::Result<(), String> {
    let native_err = {
        let mut guard = state
            .0
            .lock()
            .map_err(|_| "剪贴板状态锁中毒".to_string())?;
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
fn open_external_url_command(url: String) -> std::result::Result<(), String> {
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

// [B-A5] 报告矢量打印:前端传完整 HTML(buildReportHtml 产物)→ 落临时文件 →
// 独立 WebviewWindow 加载 → 页面 Finished 后弹 macOS 原生打印对话框(wry Webview::print,
// 本平台恒 macOS)。打印对话框「另存为 PDF」= 文字可选的矢量 PDF——区别于前端
// html2canvas 位图 PDF(保留为「PDF(图片版)」)。窗口留着给用户预览/重印,自行关闭。
#[tauri::command]
fn print_report_html_command(
    app: AppHandle,
    html: String,
    title: Option<String>,
) -> std::result::Result<(), String> {
    let dir = std::env::temp_dir().join("horosa-print");
    fs::create_dir_all(&dir).map_err(|err| format!("建打印暂存目录失败: {err}"))?;
    let stamp = SystemTime::now()
        .duration_since(UNIX_EPOCH)
        .map(|d| d.as_millis())
        .unwrap_or(0);
    let page = dir.join(format!("report-{stamp}.html"));
    fs::write(&page, html).map_err(|err| format!("写打印页失败: {err}"))?;
    let url = tauri::Url::from_file_path(&page)
        .map_err(|_| "打印页路径无法转 URL".to_string())?;
    let label = format!("report-print-{stamp}");
    WebviewWindowBuilder::new(&app, label, WebviewUrl::External(url))
        .title(title.unwrap_or_else(|| "打印 / 另存矢量 PDF".to_string()))
        .inner_size(920.0, 1080.0)
        .on_page_load(|win, payload| {
            if matches!(payload.event(), tauri::webview::PageLoadEvent::Finished) {
                let target = win.clone();
                // 留 400ms 让嵌图/字体 settle 再弹打印;spawn 出回调线程避免阻塞页面事件。
                thread::spawn(move || {
                    thread::sleep(Duration::from_millis(400));
                    let _ = target.print();
                });
            }
        })
        .build()
        .map_err(|err| format!("打印窗口创建失败: {err}"))?;
    Ok(())
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

fn ai_analysis_async_dialog() -> AsyncFileDialog {
    let mut dialog = AsyncFileDialog::new();
    dialog = dialog.add_filter("AI Analysis Files", &AI_ANALYSIS_IMPORT_EXTENSIONS);
    dialog
}

fn build_ai_analysis_payload_from_bytes(
    path: &Path,
    root: Option<&Path>,
    bytes: Vec<u8>,
) -> AiAnalysisFilePayload {
    let relative_path = root
        .and_then(|base| path.strip_prefix(base).ok())
        .map(|value| value.to_string_lossy().replace('\\', "/"));
    AiAnalysisFilePayload {
        file_name: path
            .file_name()
            .map(|value| value.to_string_lossy().to_string())
            .unwrap_or_else(|| "unknown.bin".to_string()),
        mime_type: from_path(path)
            .first_or_octet_stream()
            .essence_str()
            .to_string(),
        base64_data: BASE64_STANDARD.encode(bytes),
        relative_path,
    }
}

fn build_ai_analysis_file_payload(
    path: &Path,
    root: Option<&Path>,
) -> std::result::Result<AiAnalysisFilePayload, String> {
    let bytes = fs::read(path).map_err(|err| format!("{err:#}"))?;
    Ok(build_ai_analysis_payload_from_bytes(path, root, bytes))
}

#[tauri::command]
async fn pick_ai_analysis_files_command() -> std::result::Result<Vec<AiAnalysisFilePayload>, String>
{
    let Some(handles) = ai_analysis_async_dialog().pick_files().await else {
        return Ok(Vec::new());
    };
    let mut items = Vec::new();
    for handle in handles.iter() {
        let bytes = handle.read().await;
        items.push(build_ai_analysis_payload_from_bytes(
            handle.path(),
            None,
            bytes,
        ));
    }
    Ok(items)
}

#[tauri::command]
async fn pick_ai_analysis_folder_command() -> std::result::Result<Vec<AiAnalysisFilePayload>, String>
{
    let Some(root_handle) = AsyncFileDialog::new().pick_folder().await else {
        return Ok(Vec::new());
    };
    let root = root_handle.path().to_path_buf();
    let mut items = Vec::new();
    let mut first_error = None;
    for entry in WalkDir::new(&root)
        .into_iter()
        .filter_map(|entry| entry.ok())
    {
        let path = entry.path();
        if !path.is_file() {
            continue;
        }
        let ext = path
            .extension()
            .and_then(|value| value.to_str())
            .unwrap_or_default()
            .to_ascii_lowercase();
        if !AI_ANALYSIS_IMPORT_EXTENSIONS.contains(&ext.as_str()) {
            continue;
        }
        match build_ai_analysis_file_payload(path, Some(&root)) {
            Ok(payload) => items.push(payload),
            Err(err) => {
                if first_error.is_none() {
                    first_error = Some(format!(
                        "读取文件失败：{} ({})",
                        path.to_string_lossy(),
                        err
                    ));
                }
            }
        }
    }
    if items.is_empty() {
        if let Some(err) = first_error {
            return Err(err);
        }
    }
    Ok(items)
}

#[tauri::command]
fn save_ai_analysis_file_command(
    payload: AiAnalysisSavePayload,
) -> std::result::Result<String, String> {
    let suggested_name = if payload.default_file_name.trim().is_empty() {
        "ai-analysis-export.bin".to_string()
    } else {
        payload.default_file_name.trim().to_string()
    };
    let Some(target_path) = FileDialog::new().set_file_name(&suggested_name).save_file() else {
        return Err("用户取消保存".to_string());
    };
    let bytes = BASE64_STANDARD
        .decode(payload.base64_data.as_bytes())
        .map_err(|err| format!("{err:#}"))?;
    if let Some(parent) = target_path.parent() {
        fs::create_dir_all(parent).map_err(|err| format!("{err:#}"))?;
    }
    fs::write(&target_path, bytes).map_err(|err| format!("{err:#}"))?;
    Ok(target_path.to_string_lossy().to_string())
}

#[tauri::command]
fn open_ai_analysis_backup_command() -> std::result::Result<Option<AiAnalysisFilePayload>, String> {
    let Some(path) = FileDialog::new()
        .add_filter("AI Analysis Backup", &AI_ANALYSIS_BACKUP_EXTENSIONS)
        .pick_file()
    else {
        return Ok(None);
    };
    build_ai_analysis_file_payload(&path, None).map(Some)
}

fn load_release_config(app: &AppHandle) -> Result<ReleaseConfig> {
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
    // [U-G] 台账:install_confirmed——「vX→vY 结果」闭环行(helper 写标记,消费即记账;
    // 标记本身读取即删,台账才是耐久历史)
    append_update_history(
        app,
        serde_json::json!({
            "event": "install_confirmed",
            "to": values.get("version").cloned().unwrap_or_default(),
            "runtimeVersion": values.get("runtime_version").cloned().unwrap_or_default(),
            "relaunchStatus": values.get("relaunch_status").cloned().unwrap_or_default(),
        }),
    );

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
    let relaunch_status = values
        .get("relaunch_status")
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
    if relaunch_status.as_deref() == Some("pending_manual") {
        lines.push("本次更新已经安装完成；这次是恢复启动，自动重开没有被系统确认。".to_string());
    } else {
        lines.push("本次更新已经安装完成并重新生效。".to_string());
    }
    Some(lines.join("\n"))
}

fn has_update_complete_marker(app: &AppHandle) -> bool {
    update_complete_marker_path(app)
        .map(|marker| marker.exists())
        .unwrap_or(false)
}

/// 修复(更新后卡顿)C①:对 update-complete 标记「读取即消费」。
/// 检测到刚完成更新时:解析通知文本缓存进 AppState、并**立即删除磁盘标记**——
/// 这样无论本次更新后首启成功或失败,标记都不会残留,杜绝「首启一旦失败 → 下次启动
/// 又走 300s 全量校验慢路径」的复发。返回是否为「更新后首次启动」。
fn consume_update_complete_marker_into_state(app: &AppHandle) -> bool {
    if !has_update_complete_marker(app) {
        return false;
    }
    // consume_update_complete_notice 在成功读取后会删除标记文件;把通知文本缓存起来,
    // 待 show_post_update_notice_if_needed 在首启成功后弹窗。
    let notice = consume_update_complete_notice(app);
    // 兜底:即便上面解析失败而未删,这里强制再删一次,确保标记绝不残留。
    if let Ok(marker) = update_complete_marker_path(app) {
        let _ = fs::remove_file(&marker);
    }
    if let Some(state) = app.try_state::<AppState>() {
        if let Ok(mut slot) = state.pending_update_notice.lock() {
            *slot = notice;
        }
    }
    true
}

fn show_post_update_notice_if_needed(app: &AppHandle) {
    // 修复(更新后卡顿)C①:通知文本已在 runtime_bootstrap 开头「读取即消费」并缓存进 AppState
    // (磁盘标记同时删除)。此处从内存取出,保证即便标记早已删除,首启成功后仍能正常弹窗。
    let cached_notice = app.try_state::<AppState>().and_then(|state| {
        state
            .pending_update_notice
            .lock()
            .ok()
            .and_then(|mut slot| slot.take())
    });
    // 修复(v2.4.1:更新后卡在启动页 / 不进主界面 /「进入主界面」按钮点不动):
    // 原先此处弹**阻塞式 MessageDialog**——它紧跟 emit_ready 注入的导航 JS 之后、从 spawn 出来的后台
    // 线程触发;macOS 上 NSAlert 会在主线程跑嵌套 run loop,抢在排队的导航 JS 执行前冻结 webview 事件
    // 循环 → 既不自动导航、「进入主界面」按钮也点不动。(v2.4.0 快路径修复让首启时序变紧后这条 race 才
    // 稳定暴露。)改为**只发非阻塞 macOS 通知**,绝不在首启关键路径上做任何模态阻塞。
    if cached_notice.is_some() && load_preferences(app).show_status_notifications {
        show_macos_notification("星阙 已完成更新", "新版已经安装完成,并已重新生效。");
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
        && runtime_dir.join("runtime/mac/python/bin/python3").exists()
        && runtime_dir.join("runtime/mac/java/bin/java").exists()
}

fn runtime_python_bin(runtime_dir: &Path) -> PathBuf {
    runtime_dir.join("runtime/mac/python/bin/python3")
}

fn runtime_java_bin(runtime_dir: &Path) -> PathBuf {
    runtime_dir.join("runtime/mac/java/bin/java")
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
            // [U-I G4] 与 start 脚本的真启动门(6 包)对齐——缺 cn2an/sxtwl/cnlunar 的树
            // 此前会通过「可用」判定、却在启动脚本处卡死。
            "import importlib.util as iu; mods=('cherrypy','jsonpickle','swisseph','cn2an','sxtwl','cnlunar'); missing=[m for m in mods if iu.find_spec(m) is None]; raise SystemExit(1 if missing else 0)",
        )
        .env("PYTHONNOUSERSITE", "1")
        .stdout(Stdio::null())
        .stderr(Stdio::null())
        .status()
        .map(|status| status.success())
        .unwrap_or(false)
}

fn runtime_java_ready(runtime_dir: &Path) -> bool {
    let java_bin = runtime_java_bin(runtime_dir);
    if !java_bin.exists() {
        return false;
    }
    Command::new(&java_bin)
        .arg("-version")
        .stdout(Stdio::null())
        .stderr(Stdio::null())
        .status()
        .map(|status| status.success())
        .unwrap_or(false)
}

fn runtime_health_cache_path(runtime_dir: &Path) -> PathBuf {
    runtime_dir.join(".runtime-health-cache.json")
}

fn runtime_fast_path_marker_path(runtime_dir: &Path) -> PathBuf {
    runtime_dir.join(".runtime-fast-path.json")
}

fn file_mtime_secs(path: &Path) -> Option<u64> {
    let modified = fs::metadata(path).ok()?.modified().ok()?;
    Some(
        modified
            .duration_since(UNIX_EPOCH)
            .unwrap_or_else(|_| Duration::from_secs(0))
            .as_secs(),
    )
}

fn runtime_health_cache(runtime_dir: &Path) -> Option<RuntimeHealthCache> {
    let path = runtime_health_cache_path(runtime_dir);
    let text = fs::read_to_string(path).ok()?;
    serde_json::from_str(&text).ok()
}

fn runtime_fast_path_marker(runtime_dir: &Path) -> Option<RuntimeHealthCache> {
    let path = runtime_fast_path_marker_path(runtime_dir);
    let text = fs::read_to_string(path).ok()?;
    serde_json::from_str(&text).ok()
}

fn runtime_health_cache_matches(runtime_dir: &Path, cache: &RuntimeHealthCache) -> bool {
    let manifest_path = runtime_dir.join("runtime-manifest.json");
    let manifest = read_runtime_manifest_from_path(&manifest_path);
    let python_bin = runtime_python_bin(runtime_dir);
    let java_bin = runtime_java_bin(runtime_dir);
    manifest
        .as_ref()
        .map(|manifest| manifest.version.trim() == cache.manifest_version.trim())
        .unwrap_or(false)
        && file_mtime_secs(&manifest_path) == Some(cache.manifest_mtime)
        && file_mtime_secs(&python_bin) == Some(cache.python_mtime)
        && file_mtime_secs(&java_bin) == Some(cache.java_mtime)
}

fn write_runtime_health_cache(runtime_dir: &Path, manifest: &RuntimeManifest) {
    let manifest_path = runtime_dir.join("runtime-manifest.json");
    let python_bin = runtime_python_bin(runtime_dir);
    let java_bin = runtime_java_bin(runtime_dir);
    let Some(manifest_mtime) = file_mtime_secs(&manifest_path) else {
        return;
    };
    let Some(python_mtime) = file_mtime_secs(&python_bin) else {
        return;
    };
    let Some(java_mtime) = file_mtime_secs(&java_bin) else {
        return;
    };
    let payload = RuntimeHealthCache {
        manifest_version: manifest.version.clone(),
        manifest_mtime,
        python_mtime,
        java_mtime,
        checked_at: unix_ts(),
    };
    if let Ok(text) = serde_json::to_string(&payload) {
        let _ = fs::write(runtime_health_cache_path(runtime_dir), text);
    }
}

fn write_runtime_fast_path_marker(runtime_dir: &Path, manifest: &RuntimeManifest) {
    let manifest_path = runtime_dir.join("runtime-manifest.json");
    let python_bin = runtime_python_bin(runtime_dir);
    let java_bin = runtime_java_bin(runtime_dir);
    let Some(manifest_mtime) = file_mtime_secs(&manifest_path) else {
        return;
    };
    let Some(python_mtime) = file_mtime_secs(&python_bin) else {
        return;
    };
    let Some(java_mtime) = file_mtime_secs(&java_bin) else {
        return;
    };
    let payload = RuntimeHealthCache {
        manifest_version: manifest.version.clone(),
        manifest_mtime,
        python_mtime,
        java_mtime,
        checked_at: unix_ts(),
    };
    if let Ok(text) = serde_json::to_string(&payload) {
        let _ = fs::write(runtime_fast_path_marker_path(runtime_dir), text);
    }
}

fn clear_runtime_health_cache(runtime_dir: &Path) {
    let _ = fs::remove_file(runtime_health_cache_path(runtime_dir));
}

fn clear_runtime_fast_path_marker(runtime_dir: &Path) {
    let _ = fs::remove_file(runtime_fast_path_marker_path(runtime_dir));
}

fn runtime_fast_path_allowed(runtime_dir: &Path) -> bool {
    runtime_fast_path_marker(runtime_dir)
        .map(|cache| runtime_health_cache_matches(runtime_dir, &cache))
        .unwrap_or(false)
}

fn prepare_runtime_dir(runtime_dir: &Path) -> Result<()> {
    let _ = cleanup_runtime_metadata(runtime_dir)?;
    Ok(())
}

// [U-I G5] 健康缓存的实物锚:python/java 可执行 + site-packages 三个真启动门关键包
// (swisseph .so/cn2an/cnlunar)。site-packages 路径按 lib/python3* 动态发现(不硬编
// 解释器小版本)。
fn runtime_site_packages_dir(runtime_dir: &Path) -> Option<PathBuf> {
    let lib = runtime_dir.join("runtime/mac/python/lib");
    for entry in fs::read_dir(&lib).ok()?.flatten() {
        let path = entry.path();
        let is_pyroot = path
            .file_name()
            .and_then(|n| n.to_str())
            .map(|n| n.starts_with("python3"))
            .unwrap_or(false);
        if is_pyroot {
            let sp = path.join("site-packages");
            if sp.exists() {
                return Some(sp);
            }
        }
    }
    None
}

fn runtime_health_probe_files_present(runtime_dir: &Path) -> bool {
    if !(runtime_python_bin(runtime_dir).exists() && runtime_java_bin(runtime_dir).exists()) {
        return false;
    }
    let Some(sp) = runtime_site_packages_dir(runtime_dir) else {
        return false;
    };
    let has_swisseph = fs::read_dir(&sp)
        .map(|it| {
            it.flatten()
                .any(|e| e.file_name().to_string_lossy().starts_with("swisseph"))
        })
        .unwrap_or(false);
    has_swisseph && sp.join("cn2an").exists() && sp.join("cnlunar").exists()
}

fn runtime_dir_is_usable(runtime_dir: &Path) -> bool {
    if !runtime_dir_has_required_files(runtime_dir) {
        return false;
    }
    // 身份验明:manifest 带 appName 且与本应用不符 → 异主 runtime(同机多应用共存时
    // 安装顺序意外可能串目录),无论内容多「健康」都拒绝复用,交由替换流程重装本应用 runtime。
    if let Some(manifest) =
        read_runtime_manifest_from_path(&runtime_dir.join("runtime-manifest.json"))
    {
        if let Some(owner) = manifest.app_name.as_deref() {
            if owner != APP_NAME {
                return false;
            }
        }
    }
    if let Some(cache) = runtime_health_cache(runtime_dir) {
        // [U-I G5] 健康缓存加锚:mtime 三探针之外,关键实物必须仍在(同 mtime 隐性损坏
        // ——如 site-packages 被清理工具删掉——不再被快路径放行)。纯 stat,不跑 import,
        // 快路径速度不变;不过锚即落全量深检。
        if runtime_health_cache_matches(runtime_dir, &cache)
            && runtime_health_probe_files_present(runtime_dir)
        {
            return true;
        }
    }
    let ready = prepare_runtime_dir(runtime_dir).is_ok()
        && runtime_python_ready(runtime_dir)
        && runtime_java_ready(runtime_dir);
    if ready {
        if let Some(manifest) =
            read_runtime_manifest_from_path(&runtime_dir.join("runtime-manifest.json"))
        {
            write_runtime_health_cache(runtime_dir, &manifest);
        }
    } else {
        clear_runtime_health_cache(runtime_dir);
    }
    ready
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

// [WS-1f] 本地假 release 全链路验证入口:仅 `--features update-url-override` 的
// 开发构建才编译此代码路径;发布二进制无此分支 → 出站仅 GitHub 铁律不破。
// verify_update_experience_local.sh 用 HOROSA_UPDATE_BASE_OVERRIDE=http://127.0.0.1:PORT
// 把 manifest/runtime/资产全部指到本地 python http.server。
#[cfg(feature = "update-url-override")]
fn update_base_override() -> Option<String> {
    std::env::var("HOROSA_UPDATE_BASE_OVERRIDE")
        .ok()
        .filter(|v| !v.trim().is_empty())
}

#[cfg(not(feature = "update-url-override"))]
fn update_base_override() -> Option<String> {
    None
}

fn expected_runtime_url(config: &ReleaseConfig) -> String {
    if let Some(base) = update_base_override() {
        return format!(
            "{}/{}",
            base.trim_end_matches('/'),
            config.runtime_asset_name
        );
    }
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
    if let Some(base) = update_base_override() {
        return format!(
            "{}/{}",
            base.trim_end_matches('/'),
            config.update_manifest_name
        );
    }
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
    runtime_matches_expected(&shared_runtime, expected_version)
}

fn runtime_matches_expected(runtime_dir: &Path, expected_version: &str) -> bool {
    runtime_dir_is_usable(runtime_dir)
        && read_runtime_manifest_from_path(&runtime_dir.join("runtime-manifest.json"))
            .map(|manifest| manifest.version.trim() == expected_version.trim())
            .unwrap_or(false)
}

fn user_runtime_matches_expected(app: &AppHandle, expected_version: &str) -> Result<bool> {
    Ok(runtime_matches_expected(
        &user_runtime_dir(app)?,
        expected_version,
    ))
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

fn should_handoff_to_installed_app(
    current_bundle: &Path,
    target_bundle: &Path,
    current_version: Option<&Version>,
    target_version: Option<&Version>,
) -> bool {
    if current_bundle == target_bundle {
        return false;
    }
    match (current_version, target_version) {
        (_, None) => false,
        (Some(current), Some(target)) => target > current,
        (None, Some(_)) => true,
    }
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
            replace_recommended: should_recommend_installed_app_replacement(mode, state),
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

    let user_runtime_is_healthy = items.iter().any(|item| {
        item.kind == DetectedAssetKind::UserRuntime && item.state == DetectedAssetState::Healthy
    });
    if user_runtime_is_healthy && matches!(mode, AssetReviewMode::Install | AssetReviewMode::Repair)
    {
        if let Some(item) = items
            .iter_mut()
            .find(|item| item.kind == DetectedAssetKind::SharedRuntime)
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

fn should_recommend_installed_app_replacement(
    _mode: AssetReviewMode,
    state: DetectedAssetState,
) -> bool {
    state == DetectedAssetState::Outdated
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

// manifest 获取(签名制度已于 2026-07-04 应用户决定取消——信任模型回到
// HTTPS + GitHub 账号 + 资产 sha256;取消记录见 docs/UPDATE_AND_PERF_PLAYBOOK.md §4):
// Fetched=清单可用;Absent=不存在/网络失败/JSON 异常 → 允许走 GitHub API fallback。
enum ManifestFetch {
    Fetched(UpdateManifest),
    Absent,
}

fn fetch_update_manifest(client: &Client, manifest_url: &str) -> ManifestFetch {
    let Ok(response) = client
        .get(manifest_url)
        .header("User-Agent", "HorosaDesktop")
        .header("Cache-Control", "no-cache")
        .header("Pragma", "no-cache")
        .send()
    else {
        return ManifestFetch::Absent;
    };
    if !response.status().is_success() {
        return ManifestFetch::Absent;
    }
    let Ok(manifest_bytes) = response.bytes() else {
        return ManifestFetch::Absent;
    };
    match serde_json::from_slice::<UpdateManifest>(&manifest_bytes) {
        Ok(manifest) => ManifestFetch::Fetched(manifest),
        Err(_) => ManifestFetch::Absent,
    }
}

// manifest → plan 的纯映射(可测;主通道与 API-asset 回退通道共用,零手抄分叉)。
fn plan_from_manifest(
    manifest: UpdateManifest,
    config: &ReleaseConfig,
    platform_key: &str,
    source: UpdateSource,
) -> Option<UpdatePlan> {
    let platform = manifest.platforms.get(platform_key)?;
    let latest = Version::parse(manifest.version.trim()).ok()?;
    let repo_url = format!(
        "https://github.com/{}/{}",
        config.repo_owner, config.repo_name
    );
    let release_tag = manifest
        .tag
        .clone()
        .unwrap_or_else(|| format!("{}{}", config.release_tag_prefix, latest));
    let release_url = format!("{}/releases/tag/{}", repo_url, release_tag);
    Some(UpdatePlan {
        latest_version: latest,
        notes: manifest
            .notes
            .clone()
            .unwrap_or_else(|| "See GitHub release notes.".to_string()),
        repo_url,
        release_url,
        app_url: platform.app_url.clone(),
        app_sha256: normalize_checksum(platform.app_sha256.clone()),
        runtime_url: platform.runtime_url.clone(),
        runtime_version: platform.runtime_version.clone(),
        runtime_sha256: normalize_checksum(platform.runtime_sha256.clone()),
        components: platform.components.clone(),
        components_lock_url: platform.components_lock_url.clone(),
        components_lock_sha256: normalize_checksum(platform.components_lock_sha256.clone()),
        app_size_bytes: platform.app_size_bytes,
        runtime_size_bytes: platform.runtime_size_bytes,
        allow_downgrade: platform.allow_downgrade.unwrap_or(false),
        source,
        notify_only: false,
    })
}

fn api_manifest_fetch_enabled() -> bool {
    std::env::var("HOROSA_UPDATE_API_MANIFEST_FETCH")
        .map(|v| v != "0")
        .unwrap_or(true)
}

// API 回退时,先在 release assets 里找 manifest 资产并取回真 manifest
// (horosa-latest.json 本身就是 release 的一个 asset,发布脚本随包上传)。
fn fetch_manifest_via_release_asset(
    client: &Client,
    release: &GithubRelease,
    manifest_name: &str,
) -> Option<UpdateManifest> {
    if !api_manifest_fetch_enabled() {
        return None;
    }
    let asset = release.assets.iter().find(|a| a.name == manifest_name)?;
    match fetch_update_manifest(client, &cache_busted_url(&asset.browser_download_url)) {
        ManifestFetch::Fetched(manifest) => Some(manifest),
        ManifestFetch::Absent => None,
    }
}

fn resolve_update_plan(client: &Client, app: &AppHandle) -> Result<UpdatePlan> {
    let config = load_release_config(app)?;
    let platform_key = current_platform_key();

    let manifest_url = cache_busted_url(&update_manifest_url(&config));
    if let ManifestFetch::Fetched(manifest) = fetch_update_manifest(client, &manifest_url) {
        if let Some(plan) =
            plan_from_manifest(manifest, &config, platform_key, UpdateSource::Manifest)
        {
            return Ok(plan);
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

    // 一级回退:经 API 定位 manifest asset → 取回真 manifest → 走含 sha 的正常通道。
    if let Some(manifest) =
        fetch_manifest_via_release_asset(client, &release, &config.update_manifest_name)
    {
        if let Some(plan) =
            plan_from_manifest(manifest, &config, platform_key, UpdateSource::ManifestViaApi)
        {
            ledger_mark(
                "rust.update_manifest_via_api",
                Some(serde_json::json!({ "tag": release.tag_name })),
            );
            return Ok(plan);
        }
    }

    // 二级降级:manifest 与其 asset 双双不可得 → notify-only。
    // 绝不再无 sha 自动下载安装(旧行为的安全洞):只把版本/发布页告诉用户。
    let latest = parse_version(&release.tag_name)?;
    let repo_url = format!(
        "https://github.com/{}/{}",
        config.repo_owner, config.repo_name
    );
    ledger_mark(
        "rust.update_notify_only",
        Some(serde_json::json!({ "tag": release.tag_name })),
    );
    Ok(UpdatePlan {
        latest_version: latest,
        notes: release.body.unwrap_or_default(),
        repo_url: repo_url.clone(),
        release_url: release
            .html_url
            .clone()
            .unwrap_or_else(|| format!("{}/releases/tag/{}", repo_url, release.tag_name)),
        app_url: String::new(),
        app_sha256: None,
        runtime_url: None,
        runtime_version: None,
        runtime_sha256: None,
        components: None,
        components_lock_url: None,
        components_lock_sha256: None,
        app_size_bytes: None,
        runtime_size_bytes: None,
        allow_downgrade: false,
        source: UpdateSource::GithubApi,
        notify_only: true,
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

// ============ 断点续传下载核(WS-1b,launcher/update 双通道共用) ============
// 协议:数据写 dest.part,旁挂 dest.part.meta(url/etag/total/续传次数);
// 中断后(同进程重试或跨进程重启)part+meta 在位且 url 相同 → Range bytes=N- 请求:
//   206 且 etag 未变 → append 续传;200(服务器不理 Range)→ 就地当全新流用;
//   etag 冲突/416/续传次数超限 → 自动退全新下载。
// 完成 sync+原子 rename part→dest:dest 永远不出现半成品,sha 校验仍由调用方兜底;
// 若续传拼合出错,外层 sha 失败时 part 已被 rename 消费 → 下一轮天然全新重下。
// kill-switch: HOROSA_DOWNLOAD_NO_RESUME=1 退回全新下载(现状行为)。

const RESUME_MAX_ATTEMPTS: u32 = 4;

#[derive(Serialize, Deserialize, Default)]
struct PartMeta {
    url: String,
    #[serde(default)]
    etag: Option<String>,
    #[serde(default)]
    total: u64,
    #[serde(default)]
    resume_attempts: u32,
}

fn download_resume_enabled() -> bool {
    std::env::var("HOROSA_DOWNLOAD_NO_RESUME")
        .map(|v| !matches!(v.as_str(), "1" | "true" | "yes" | "on"))
        .unwrap_or(true)
}

fn download_part_paths(dest: &Path) -> (PathBuf, PathBuf) {
    let name = dest
        .file_name()
        .map(|s| s.to_string_lossy().to_string())
        .unwrap_or_else(|| "download".to_string());
    let dir = dest
        .parent()
        .map(|p| p.to_path_buf())
        .unwrap_or_else(|| PathBuf::from("."));
    (
        dir.join(format!("{}.part", name)),
        dir.join(format!("{}.part.meta", name)),
    )
}

fn load_part_meta(path: &Path) -> Option<PartMeta> {
    let text = fs::read_to_string(path).ok()?;
    serde_json::from_str(&text).ok()
}

fn save_part_meta(path: &Path, meta: &PartMeta) {
    if let Ok(text) = serde_json::to_string(meta) {
        let _ = fs::write(path, text);
    }
}

fn clear_part_files(part: &Path, meta: &Path) {
    let _ = fs::remove_file(part);
    let _ = fs::remove_file(meta);
}

fn response_etag(resp: &reqwest::blocking::Response) -> Option<String> {
    resp.headers()
        .get(reqwest::header::ETAG)
        .and_then(|v| v.to_str().ok())
        .map(|s| s.to_string())
}

/// 解析 206 的 Content-Range: bytes N-M/TOTAL,取 TOTAL。
fn parse_content_range_total(resp: &reqwest::blocking::Response) -> Option<u64> {
    let value = resp
        .headers()
        .get(reqwest::header::CONTENT_RANGE)?
        .to_str()
        .ok()?;
    value.rsplit('/').next()?.trim().parse::<u64>().ok()
}

/// 下载进度回执:downloaded 含续传补入的既有字节;delta=本次新读字节。
struct DownloadChunk {
    downloaded: u64,
    total: u64,
    delta: u64,
}

/// 断点续传单次下载。成功=dest 原子就位;失败=part/meta 保留供下一轮续传。
/// on_start(resumed_from,total) 连接建立后调一次;on_chunk 每读一块调(节流由调用方闭包自理)。
fn download_resumable_once(
    url: &str,
    dest: &Path,
    allow_resume: bool,
    on_start: impl FnOnce(u64, u64),
    mut on_chunk: impl FnMut(&DownloadChunk),
) -> Result<()> {
    let client = build_github_client(900)?;
    if let Some(parent) = dest.parent() {
        ensure_dir(parent)?;
    }
    let (part_path, meta_path) = download_part_paths(dest);
    if !allow_resume {
        clear_part_files(&part_path, &meta_path);
    }

    // 续传资格判定:part+meta 在位、同 url、长度>0 且未满、续传次数未超限。
    let mut resume_offset: u64 = 0;
    let mut resume_meta: Option<PartMeta> = None;
    if allow_resume {
        if let Some(meta) = load_part_meta(&meta_path) {
            let part_len = fs::metadata(&part_path).map(|m| m.len()).unwrap_or(0);
            let len_ok = part_len > 0 && (meta.total == 0 || part_len < meta.total);
            if meta.url == url && len_ok && meta.resume_attempts < RESUME_MAX_ATTEMPTS {
                resume_offset = part_len;
                resume_meta = Some(meta);
            } else {
                clear_part_files(&part_path, &meta_path);
            }
        } else if part_path.exists() {
            // 有 part 无 meta:无从判定来源,弃之。
            clear_part_files(&part_path, &meta_path);
        }
    }

    // 先试 Range 续传;拿不到干净的 206 就退全新(200 全量流可直接就地消费)。
    let mut session: Option<(reqwest::blocking::Response, File, u64, u64)> = None;
    let mut fresh_response: Option<reqwest::blocking::Response> = None;
    if resume_offset > 0 {
        let mut meta = resume_meta.take().unwrap_or_default();
        meta.resume_attempts += 1;
        save_part_meta(&meta_path, &meta);
        if let Ok(resp) = client
            .get(url)
            .header("User-Agent", "HorosaDesktop")
            .header("Range", format!("bytes={}-", resume_offset))
            .send()
        {
            let status = resp.status();
            if status == reqwest::StatusCode::PARTIAL_CONTENT {
                let etag_conflict = matches!(
                    (&meta.etag, &response_etag(&resp)),
                    (Some(old), Some(new)) if old != new
                );
                if !etag_conflict {
                    let total = parse_content_range_total(&resp).unwrap_or_else(|| {
                        resp.content_length()
                            .map(|len| resume_offset + len)
                            .unwrap_or(meta.total)
                    });
                    let file = fs::OpenOptions::new()
                        .append(true)
                        .open(&part_path)
                        .with_context(|| format!("open part {}", part_path.display()))?;
                    session = Some((resp, file, resume_offset, total));
                }
            } else if status.is_success() {
                // 服务器不支持 Range(回 200 全量):直接把这条响应当全新下载用,省一次握手。
                fresh_response = Some(resp);
            }
            // 416/其它状态:落空,下面统一发全新请求。
        }
    }

    let (mut response, mut file, start_offset, total) = match session {
        Some(s) => s,
        None => {
            let resp = match fresh_response {
                Some(r) => r,
                None => client
                    .get(url)
                    .header("User-Agent", "HorosaDesktop")
                    .header("Cache-Control", "no-cache")
                    .header("Pragma", "no-cache")
                    .send()
                    .with_context(|| format!("download {}", url))?,
            };
            if !resp.status().is_success() {
                return Err(anyhow!("download failed: {} -> {}", url, resp.status()));
            }
            let total = resp.content_length().unwrap_or(0);
            save_part_meta(
                &meta_path,
                &PartMeta {
                    url: url.to_string(),
                    etag: response_etag(&resp),
                    total,
                    resume_attempts: 0,
                },
            );
            // File::create 截断:etag 冲突/416 后的残余 part 在此归零重写。
            let file = File::create(&part_path)?;
            (resp, file, 0u64, total)
        }
    };

    on_start(start_offset, total);
    let mut downloaded = start_offset;
    let mut buffer = [0u8; 64 * 1024];
    loop {
        let read = response.read(&mut buffer)?;
        if read == 0 {
            break;
        }
        file.write_all(&buffer[..read])?;
        downloaded += read as u64;
        on_chunk(&DownloadChunk {
            downloaded,
            total,
            delta: read as u64,
        });
    }
    if total > 0 && downloaded < total {
        return Err(anyhow!(
            "download incomplete: {} -> {}/{} bytes",
            url,
            downloaded,
            total
        ));
    }
    let _ = file.sync_all();
    drop(file);
    fs::rename(&part_path, dest).with_context(|| format!("finalize {}", dest.display()))?;
    let _ = fs::remove_file(&meta_path);
    Ok(())
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
                // 半成品在 dest.part(由下载核管理),保留供下一轮断点续传;
                // dest 只在成功 rename 后出现,这里无需清理。
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
    // launcher 通道薄壳:下载/续传逻辑在 download_resumable_once;
    // 这里只负责把进度烧进 message 字符串(launcher 页零改动受益);
    // 节流 ≥400ms 才 emit(此前每 64KB 一次 window.eval,大包即洪泛)。
    let started = Instant::now();
    let mut last_emit = Instant::now();
    let mut last_pct: i32 = -1;
    // 续传补入的既有字节,不计入本次会话速度(Cell:on_start/on_chunk 两闭包共享)
    let session_base = std::cell::Cell::new(0u64);
    download_resumable_once(
        url,
        dest,
        download_resume_enabled(),
        |resumed_from, total| {
            session_base.set(resumed_from);
            if resumed_from > 0 {
                emit_progress(
                    window,
                    start_pct,
                    &format!(
                        "{label}：检测到未完成的下载，从 {} MB 处继续…",
                        resumed_from / 1_048_576
                    ),
                );
            } else if total > 0 {
                emit_progress(
                    window,
                    start_pct,
                    &format!("{label}：已连接服务器，开始接收数据"),
                );
            } else {
                emit_indeterminate_progress(
                    window,
                    start_pct,
                    &format!("{label}：已连接服务器，正在接收数据…"),
                );
            }
        },
        |chunk| {
            if chunk.total == 0 {
                return;
            }
            let ratio = chunk.downloaded as f64 / chunk.total as f64;
            let span = end_pct.saturating_sub(start_pct) as f64;
            let pct = (start_pct as f64 + span * ratio).round() as i32;
            let now = Instant::now();
            if pct != last_pct && now.duration_since(last_emit) >= Duration::from_millis(400) {
                last_pct = pct;
                last_emit = now;
                let elapsed = started.elapsed().as_secs_f64().max(0.001);
                // 字节/秒(本次会话均速:续传补入的字节不计,避免虚高)
                let speed = chunk.downloaded.saturating_sub(session_base.get()) as f64 / elapsed;
                let remaining = (chunk.total.saturating_sub(chunk.downloaded)) as f64;
                let eta_secs = if speed > 0.0 {
                    (remaining / speed) as u64
                } else {
                    0
                };
                let eta_text = if eta_secs >= 60 {
                    format!("约剩 {} 分 {} 秒", eta_secs / 60, eta_secs % 60)
                } else {
                    format!("约剩 {} 秒", eta_secs)
                };
                emit_progress(
                    window,
                    pct as u8,
                    &format!(
                        "{}：已下载 {}/{} MB · {:.1} MB/s · {}",
                        label,
                        chunk.downloaded / 1_048_576,
                        chunk.total / 1_048_576,
                        speed / 1_048_576.0,
                        eta_text
                    ),
                );
            }
        },
    )?;
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

/// 目标路径所在卷的可用字节数(df -k,1024 块)。取不到时返回 None(调用方按"不拦"处理)。
fn available_disk_bytes(path: &Path) -> Option<u64> {
    let probe = if path.exists() {
        path.to_path_buf()
    } else {
        path.parent()
            .map(|p| p.to_path_buf())
            .unwrap_or_else(|| PathBuf::from("/"))
    };
    let output = Command::new("/bin/df")
        .arg("-k")
        .arg(&probe)
        .output()
        .ok()?;
    if !output.status.success() {
        return None;
    }
    let text = String::from_utf8_lossy(&output.stdout);
    let line = text.lines().nth(1)?;
    // Filesystem 1024-blocks Used Available Capacity ... ; 第 4 列 = Available
    let avail_kb: u64 = line.split_whitespace().nth(3)?.parse().ok()?;
    Some(avail_kb.saturating_mul(1024))
}

fn archive_runtime_version(archive_path: &Path) -> Result<String> {
    let output = Command::new("/usr/bin/tar")
        .arg("-xOf")
        .arg(archive_path)
        .arg("runtime-payload/runtime-manifest.json")
        .output()
        .with_context(|| format!("read runtime manifest from {}", archive_path.display()))?;
    if !output.status.success() {
        let stderr = String::from_utf8_lossy(&output.stderr);
        return Err(anyhow!(
            "runtime manifest missing in {}: {}",
            archive_path.display(),
            stderr.trim()
        ));
    }
    let manifest: RuntimeManifest =
        serde_json::from_slice(&output.stdout).context("parse runtime manifest json")?;
    Ok(manifest.version)
}

// ============ 启动健康看门狗(WS-1d,A/B 槽自愈) ============
// 语义:每次 bootstrap 起点 pending+1;emit_ready 即确认(归零+清 previous 槽)。
// 连续 WATCHDOG_ROLLBACK_THRESHOLD 次未达 ready(崩溃/卡死被强退)→ 第三次启动时
// 自动把 previous 槽换回 current(previous 由更新路径保留到首次成功 ready)。
// 与 fast-path 回退互补:fast-path 兜「新 runtime 校验不过」,看门狗兜「新 runtime 起不来」。

const WATCHDOG_ROLLBACK_THRESHOLD: u32 = 2;

#[derive(Serialize, Deserialize, Default, Clone, Copy)]
struct LaunchHealth {
    #[serde(default)]
    pending_starts: u32,
}

fn launch_health_path(app: &AppHandle) -> Option<PathBuf> {
    app.path()
        .app_data_dir()
        .ok()
        .map(|dir| dir.join("launch-health.json"))
}

fn launch_health_read(path: &Path) -> LaunchHealth {
    fs::read_to_string(path)
        .ok()
        .and_then(|text| serde_json::from_str(&text).ok())
        .unwrap_or_default()
}

fn launch_health_write(path: &Path, health: &LaunchHealth) {
    if let Some(parent) = path.parent() {
        let _ = fs::create_dir_all(parent);
    }
    if let Ok(text) = serde_json::to_string(health) {
        let _ = fs::write(path, text);
    }
}

/// 启动起点登记:pending+1 落盘,返回累计未确认次数(含本次)。
fn launch_health_note_start(path: &Path) -> u32 {
    let mut health = launch_health_read(path);
    health.pending_starts = health.pending_starts.saturating_add(1);
    launch_health_write(path, &health);
    health.pending_starts
}

/// 启动成功确认:pending 归零。
fn launch_health_confirm(path: &Path) {
    launch_health_write(path, &LaunchHealth { pending_starts: 0 });
}

/// 把 previous 槽换回 current。previous 不在/不完整 → Ok(false) 不动 current。
// 跨进程手术互斥锁:多实例/多用户可并发对同一 runtime 根做 clone→_comp_stage→swap,
// renamex 单 op 原子但多步手术未跨进程串行化 → flock 锁文件(内核级,进程崩溃/被杀自动释放)。
// 纪律([108] 反向锚强制):锁只允许出现在五个叶子手术函数内部——
//   extract_runtime_archive_with / apply_component_updates_with(required)
//   rollback_runtime_to_previous / repair_torn_runtime_slots / cleanup_previous_slots(optional)
// 五叶已核互不嵌套;flock 同进程两个 fd 也互斥,上层再取=自死锁,严禁。
// helper 经 --horosa-runtime-swap → extract 协议自动拿锁(零新增代数差)。
struct RuntimeSurgeryLock {
    _file: Option<File>,
}

fn runtime_surgery_lock_path(root: &Path) -> PathBuf {
    root.join(".horosa-surgery.lock")
}

fn surgery_lock_disabled() -> bool {
    std::env::var("HOROSA_SURGERY_LOCK_DISABLE")
        .map(|v| v == "1")
        .unwrap_or(false)
}

fn surgery_lock_wait_secs() -> u64 {
    std::env::var("HOROSA_SURGERY_LOCK_WAIT_SECS")
        .ok()
        .and_then(|v| v.parse().ok())
        .unwrap_or(300)
}

// Ok(Some)=拿到 / Ok(None)=等满未拿到 / Err=连锁文件都开不出(权限/只读卷)。
fn try_acquire_surgery_lock(root: &Path, wait: Duration) -> Result<Option<RuntimeSurgeryLock>> {
    if surgery_lock_disabled() {
        return Ok(Some(RuntimeSurgeryLock { _file: None }));
    }
    use std::os::unix::fs::{OpenOptionsExt, PermissionsExt};
    use std::os::unix::io::AsRawFd;
    ensure_dir(root)?;
    let lock_path = runtime_surgery_lock_path(root);
    let file = match std::fs::OpenOptions::new()
        .read(true)
        .write(true)
        .create(true)
        .mode(0o666)
        .open(&lock_path)
    {
        Ok(f) => {
            // umask(022) 会剥 o+w:多用户共享根必须显式补,否则 B 用户开不出写句柄。
            let _ = f.set_permissions(fs::Permissions::from_mode(0o666));
            f
        }
        Err(err) if err.kind() == std::io::ErrorKind::PermissionDenied => {
            // 他人先建且权限未放开:flock 对只读 fd 也能上 LOCK_EX。
            std::fs::OpenOptions::new()
                .read(true)
                .open(&lock_path)
                .with_context(|| format!("打开手术锁 {}", lock_path.display()))?
        }
        Err(err) => {
            return Err(anyhow::Error::from(err)
                .context(format!("创建手术锁 {}", lock_path.display())))
        }
    };
    let fd = file.as_raw_fd();
    let deadline = Instant::now() + wait;
    loop {
        if unsafe { libc::flock(fd, libc::LOCK_EX | libc::LOCK_NB) } == 0 {
            return Ok(Some(RuntimeSurgeryLock { _file: Some(file) }));
        }
        if Instant::now() >= deadline {
            return Ok(None);
        }
        thread::sleep(Duration::from_millis(500));
    }
}

// 手术必需(extract/apply):等不到=Err(用户可读文案);账本留证,Err 沿既有更新失败
// 通道(事件+update-history)上浮。默认等 300s——须盖住对方一次全量解压。
fn acquire_surgery_lock_required(root: &Path) -> Result<RuntimeSurgeryLock> {
    let started = Instant::now();
    let wait = Duration::from_secs(surgery_lock_wait_secs());
    match try_acquire_surgery_lock(root, wait)? {
        Some(guard) => {
            let waited = started.elapsed();
            if waited > Duration::from_secs(1) {
                ledger_mark(
                    "rust.surgery_lock_wait",
                    Some(serde_json::json!({
                        "root": root.display().to_string(),
                        "ms": waited.as_millis() as u64,
                    })),
                );
            }
            Ok(guard)
        }
        None => {
            ledger_mark(
                "rust.surgery_lock_timeout",
                Some(serde_json::json!({
                    "root": root.display().to_string(),
                    "mode": "required",
                })),
            );
            Err(anyhow!(
                "另一份星阙实例(可能是本机其他用户)正在更新或修复本机组件,请稍后重试。"
            ))
        }
    }
}

fn surgery_lock_optional_wait_secs() -> u64 {
    std::env::var("HOROSA_SURGERY_LOCK_OPT_WAIT_SECS")
        .ok()
        .and_then(|v| v.parse().ok())
        .unwrap_or(10)
}

// 尽力而为(启动兜底类:回滚/收养/回收):短等 10s,拿不到=跳过本项让位对方手术。
fn acquire_surgery_lock_optional(root: &Path) -> Option<RuntimeSurgeryLock> {
    match try_acquire_surgery_lock(root, Duration::from_secs(surgery_lock_optional_wait_secs())) {
        Ok(Some(guard)) => Some(guard),
        Ok(None) => {
            ledger_mark(
                "rust.surgery_lock_timeout",
                Some(serde_json::json!({
                    "root": root.display().to_string(),
                    "mode": "optional",
                })),
            );
            None
        }
        Err(err) => {
            eprintln!("[surgery-lock] {}: {err:#}", root.display());
            None
        }
    }
}

fn rollback_runtime_to_previous(root: &Path) -> Result<bool> {
    let current = root.join("current");
    let previous = root.join("previous");
    if !previous.join("runtime-manifest.json").exists() {
        return Ok(false);
    }
    // optional 锁:对方在手术=让位,本轮不回滚(下次启动再判)。
    let Some(_surgery) = acquire_surgery_lock_optional(root) else {
        return Ok(false);
    };
    let broken = root.join("_broken_rollback");
    remove_dir_if_exists(&broken)?;
    if current.exists() {
        fs::rename(&current, &broken)
            .with_context(|| format!("隔离故障槽 {}", current.display()))?;
    }
    if let Err(err) = fs::rename(&previous, &current) {
        // 换入失败:把故障槽放回,保持可诊断状态。
        let _ = fs::rename(&broken, &current);
        return Err(err).with_context(|| format!("回滚 previous 槽到 {}", current.display()));
    }
    let _ = remove_dir_if_exists(&broken);
    Ok(true)
}

/// ready 后清各 root 的 previous 槽(确认当前槽健康,回收磁盘)。
fn cleanup_previous_slots(app: &AppHandle) {
    let mut roots = vec![shared_runtime_root()];
    if let Ok(user_root) = user_runtime_root(app) {
        roots.push(user_root);
    }
    for root in roots {
        let previous = root.join("previous");
        if previous.exists() {
            // optional 锁:对方在手术期间 previous 可能是其回滚资本,绝不抢删。
            let Some(_surgery) = acquire_surgery_lock_optional(&root) else {
                continue;
            };
            let _ = remove_dir_if_exists(&previous);
        }
    }
}

/// 多用户机权限延续:postinstall 只放开「装机时刻」的共享树;此后任一用户做全量解压/
/// 增量对换,新落成的 current 树按该用户 umask(022)归其私有,其他用户能跑但无法再
/// 更新/回滚。每次新树落成后 best-effort 放开(仅共享域;失败不阻塞,单用户机零影响)。
fn open_shared_tree_permissions(path: &Path) {
    if !is_shared_runtime_dir(path) {
        return;
    }
    let _ = Command::new("/bin/chmod")
        .arg("-R")
        .arg("a+rwX")
        .arg(path)
        .stdout(Stdio::null())
        .stderr(Stdio::null())
        .status();
}

// [U-A kill-atomic] APFS 原子互换两目录(renamex_np + RENAME_SWAP,macOS 10.12+):
// 对换全程只有这一个原子点——任意时刻断电/强杀,current 恒为「全旧」或「全新」,
// 不再存在两段 rename 之间的 current 缺失窗口。返回 Ok(false)=本卷/内核不支持
// (ENOTSUP/EINVAL/EXDEV)或被 HOROSA_SWAP_DISABLE=1 禁用 → 调用方走两段 rename
// 回退路径(其 kill 窗口由启动期 repair_torn_runtime_slots 撕裂探测兜底)。
fn atomic_swap_dirs(a: &Path, b: &Path) -> Result<bool> {
    if std::env::var("HOROSA_SWAP_DISABLE")
        .map(|v| v.trim() == "1")
        .unwrap_or(false)
    {
        return Ok(false);
    }
    use std::os::unix::ffi::OsStrExt;
    let ca = std::ffi::CString::new(a.as_os_str().as_bytes())
        .with_context(|| format!("swap 路径含 NUL: {}", a.display()))?;
    let cb = std::ffi::CString::new(b.as_os_str().as_bytes())
        .with_context(|| format!("swap 路径含 NUL: {}", b.display()))?;
    let rc = unsafe { libc::renamex_np(ca.as_ptr(), cb.as_ptr(), libc::RENAME_SWAP) };
    if rc == 0 {
        return Ok(true);
    }
    let err = std::io::Error::last_os_error();
    match err.raw_os_error() {
        // 卷/内核不支持 → 走回退分支,不算错误
        Some(libc::ENOTSUP) | Some(libc::EINVAL) | Some(libc::EXDEV) => Ok(false),
        _ => Err(anyhow::Error::from(err))
            .with_context(|| format!("renamex_np swap {} ↔ {}", a.display(), b.display())),
    }
}

// [U-A 撕裂探测] 启动期兜底:两段 rename 回退路径(或 postinstall shell 两 mv)在
// 「current 已挪走、新树未就位」窗口被断电/强杀 → current 整体缺失。按候选新旧序
// 收养:_comp_stage(增量暂存,最新) > _extract/runtime-payload(全量暂存) > previous
// (旧版)。候选必须过 runtime_dir_has_required_files 完整性验,不完整绝不收养。
fn repair_torn_runtime_slots(root: &Path) -> Result<bool> {
    let current = root.join("current");
    if !root.exists() || current.exists() {
        return Ok(false);
    }
    // optional 锁:对方可能正在手术(即将产出 current),不抢收养。
    let Some(_surgery) = acquire_surgery_lock_optional(root) else {
        return Ok(false);
    };
    // 拿锁后复核:等锁期间对方可能已产出 current。
    if current.exists() {
        return Ok(false);
    }
    let candidates = [
        root.join("_comp_stage"),
        root.join("_extract").join("runtime-payload"),
        // 旧 helper 协议(过渡跳)的暂存位:断电撕裂时新树可被收养,不再成孤儿。
        root.join("_update").join("runtime-payload"),
        root.join("previous"),
    ];
    for candidate in candidates {
        if candidate.exists() && runtime_dir_has_required_files(&candidate) {
            fs::rename(&candidate, &current)
                .with_context(|| format!("撕裂修复:收养 {} → current", candidate.display()))?;
            ledger_mark(
                "rust.torn_slot_repaired",
                Some(serde_json::json!({
                    "root": root.display().to_string(),
                    "adopted": candidate.display().to_string(),
                })),
            );
            return Ok(true);
        }
    }
    Ok(false)
}

// 孤儿暂存清扫:current 在位(无需收养)但 _update/_extract 残留 = 上次手术
// 成功臂之外中断留下的孤儿树,只漏磁盘不碍事。仅清 24h 以上的陈旧目录——另一实例
// 正在进行的手术(_extract 活跃)绝不误伤;更细的互斥由跨进程手术锁承担。
fn sweep_stale_runtime_stage_dirs(root: &Path) {
    let current = root.join("current");
    if !current.exists() {
        return; // 无 current = 撕裂态,交给 repair_torn_runtime_slots,不清扫
    }
    for name in ["_update", "_extract"] {
        let stage = root.join(name);
        if !stage.exists() {
            continue;
        }
        let stale = fs::metadata(&stage)
            .and_then(|m| m.modified())
            .ok()
            .and_then(|t| t.elapsed().ok())
            .map(|age| age.as_secs() > 24 * 3600)
            .unwrap_or(false);
        if !stale {
            continue;
        }
        if remove_dir_if_exists(&stage).is_ok() {
            ledger_mark(
                "rust.stale_stage_swept",
                Some(serde_json::json!({
                    "root": root.display().to_string(),
                    "stage": name,
                })),
            );
        }
    }
}

fn extract_runtime_archive(archive_path: &Path, dest_root: &Path) -> Result<()> {
    extract_runtime_archive_with(archive_path, dest_root, None, None)
}

fn extract_runtime_archive_with(
    archive_path: &Path,
    dest_root: &Path,
    progress: Option<&dyn Fn(u64, u64, u64)>,
    // 版本闸:helper 经 --horosa-runtime-swap 走本协议时,归档内 manifest.version
    // 必须与期望一致(替代旧 helper 内联 plutil 核对);不符→清 _extract 返回 Err,current 零接触。
    expected_version: Option<&str>,
) -> Result<()> {
    // required 锁:全量手术全程独占(_extract 建立→解压→互换→previous 挪位)。
    let _surgery = acquire_surgery_lock_required(dest_root)?;
    let extract_root = dest_root.join("_extract");
    remove_dir_if_exists(&extract_root)?;
    // 磁盘预检:解压产物 ≈ 2.3× 压缩包;不足时 tar 写到一半才败,留半成品且报错难懂。
    if let Ok(meta) = fs::metadata(archive_path) {
        let need = meta.len().saturating_mul(5) / 2; // 2.5× 余量
        if let Some(avail) = available_disk_bytes(dest_root) {
            if avail < need {
                return Err(anyhow!(
                    "磁盘空间不足:解压本机组件约需 {:.1} GB 可用空间,当前仅 {:.1} GB。请清理磁盘后重试。",
                    need as f64 / 1e9,
                    avail as f64 / 1e9
                ));
            }
        }
    }
    ensure_dir(&extract_root)?;
    let mut extracted_ok = false;
    if extract_native_enabled() {
        match extract_tar_gz_native(archive_path, &extract_root, 0, progress) {
            Ok(()) => extracted_ok = true,
            Err(err) => {
                // native 半成品整目录重建后走外部 tar(_extract 是全新目录,可安全清)。
                eprintln!(
                    "[extract] native 解压失败,自动回退外部 tar 重解 {}: {err:#}",
                    archive_path.display()
                );
                let _ = remove_dir_if_exists(&extract_root);
                ensure_dir(&extract_root)?;
            }
        }
    }
    if !extracted_ok {
        if let Err(err) = tar_extract_external(archive_path, &extract_root, false) {
            // tar 半途失败(磁盘满/坏包)的半成品必须当场清掉,否则磁盘累积孤立解压目录。
            let _ = remove_dir_if_exists(&extract_root);
            return Err(err.context(format!(
                "extract runtime archive failed for {}",
                archive_path.display()
            )));
        }
    }

    let extracted_runtime = extract_root.join("runtime-payload");
    if !extracted_runtime.exists() {
        let _ = remove_dir_if_exists(&extract_root);
        return Err(anyhow!("runtime-payload folder missing inside archive"));
    }
    if let Some(expected) = expected_version.map(str::trim).filter(|v| !v.is_empty()) {
        let actual = read_runtime_manifest_from_path(&extracted_runtime.join("runtime-manifest.json"))
            .map(|m| m.version)
            .unwrap_or_default();
        if actual != expected {
            let _ = remove_dir_if_exists(&extract_root);
            return Err(anyhow!(
                "runtime version mismatch: {actual} != {expected}(归档与期望不符,current 未动)"
            ));
        }
    }

    let final_runtime = dest_root.join("current");
    let backup_runtime = dest_root.join("previous");
    let had_previous = final_runtime.exists();
    if had_previous {
        remove_dir_if_exists(&backup_runtime)?;
        // [U-A kill-atomic] 首选 renamex_np 单点互换:swap 后 extracted 位置上是旧树,
        // 再挪进 previous 槽;挪失败即撤销 swap 恢复原状(保住「prepare 失败回滚依赖
        // previous 在位」的既有不变量),报错走上游重试。
        if atomic_swap_dirs(&extracted_runtime, &final_runtime)? {
            if let Err(err) = fs::rename(&extracted_runtime, &backup_runtime) {
                let _ = atomic_swap_dirs(&extracted_runtime, &final_runtime);
                let _ = remove_dir_if_exists(&extract_root);
                return Err(anyhow::Error::from(err).context("旧运行时挪 previous 槽失败"));
            }
        } else {
            // 回退:两段 rename(kill 窗口由启动期 repair_torn_runtime_slots 撕裂探测兜底)
            fs::rename(&final_runtime, &backup_runtime)?;
            if let Err(err) = fs::rename(&extracted_runtime, &final_runtime) {
                let _ = fs::rename(&backup_runtime, &final_runtime);
                let _ = remove_dir_if_exists(&extract_root);
                return Err(err.into());
            }
        }
    } else if let Err(err) = fs::rename(&extracted_runtime, &final_runtime) {
        // 首装:单次 rename 本身即原子
        let _ = remove_dir_if_exists(&extract_root);
        return Err(err.into());
    }
    if let Err(err) = prepare_runtime_dir(&final_runtime) {
        // prepare 失败时 current 已是新内容但不可用:回滚到 previous,保住可用旧版。
        if had_previous && backup_runtime.exists() {
            let _ = remove_dir_if_exists(&final_runtime);
            let _ = fs::rename(&backup_runtime, &final_runtime);
        }
        let _ = remove_dir_if_exists(&extract_root);
        return Err(err);
    }
    let _ = Command::new("/usr/bin/xattr")
        .arg("-dr")
        .arg("com.apple.quarantine")
        .arg(&final_runtime)
        .stdout(Stdio::null())
        .stderr(Stdio::null())
        .status();
    open_shared_tree_permissions(&final_runtime);
    // WS-1d 看门狗:previous 槽保留到首次成功 ready(emit_ready→cleanup_previous_slots 回收);
    // 若新 runtime 连续起不来,启动侧自动 rollback_runtime_to_previous。
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

// ══════════════════════════ 增量部件更新(manifest v2) ══════════════════════════
// 全量 tar 自带 components-lock.json(打包脚本写进 stage 根),故任何全量安装路径
// (首装 pkg/离线/修复/回退)之后本地即有部件清单;增量更新按 manifest.components
// 与本地 lock 的 sha 差集只下载变化部件,应用采用「clone 暂存 → 部件手术 → 原子
// 对换」协议(与全量 extract_runtime_archive 的 current/previous 语义一致),任何
// 一步失败 current 纹丝不动,调用方回落全量。kill-switch:HOROSA_UPDATE_FULL_ONLY=1。

/// 本地已装部件清单(<root>/current/components-lock.json)。
fn read_local_components_lock(runtime_root: &Path) -> Option<serde_json::Value> {
    let path = runtime_root.join("current").join("components-lock.json");
    let text = fs::read_to_string(path).ok()?;
    serde_json::from_str(&text).ok()
}

fn lock_component_map(lock: &serde_json::Value) -> HashMap<String, serde_json::Value> {
    let mut out = HashMap::new();
    if let Some(items) = lock.get("components").and_then(|v| v.as_array()) {
        for item in items {
            if let Some(name) = item.get("name").and_then(|v| v.as_str()) {
                out.insert(name.to_string(), item.clone());
            }
        }
    }
    out
}

/// 增量可行性判定 + diff。返回需下载的部件集(可为空 = 纯版本标记更新);None = 走全量。
fn plan_component_diff(
    plan: &UpdatePlan,
    runtime_roots: &[PathBuf],
) -> Option<Vec<ManifestComponent>> {
    if std::env::var("HOROSA_UPDATE_FULL_ONLY").ok().as_deref() == Some("1") {
        return None;
    }
    let components = plan.components.as_ref()?;
    plan.components_lock_url.as_ref()?;
    plan.components_lock_sha256.as_ref()?;
    if components.is_empty() {
        return None;
    }
    // 多 root(共享+用户罕见修复态)一律全量:各 root 已装态可能不同,增量按单基准
    // diff 会漏;单 root 覆盖绝大多数常规更新场景。
    if runtime_roots.len() != 1 {
        return None;
    }
    let local = read_local_components_lock(&runtime_roots[0])?;
    let local_map = lock_component_map(&local);
    if local_map.is_empty() {
        return None;
    }
    let changed: Vec<ManifestComponent> = components
        .iter()
        .filter(|c| {
            local_map
                .get(&c.name)
                .and_then(|v| v.get("sha256"))
                .and_then(|v| v.as_str())
                != Some(c.sha256.as_str())
        })
        .cloned()
        .collect();
    Some(changed)
}

/// 下载并校验:components-lock + 变化部件。lock 与 manifest 逐部件核对(防两 asset 漂移)。
// [U-E 部件级重试] 单部件失败先原地重试,仍败才上抛(由上游整链降级全量——此前一个
// 部件坏一次就整链退全量重下 ~600MB)。按错误类型分治:sha 失配=坏资产,清 dest+续传
// 残档全新下;下载错=网络抖动,保留 .part 让断点续传接力(续传自身次数上限由
// .part.meta 的 attempts 管,与本层「整资产重试」正交)。
const COMPONENT_RETRY_MAX: u32 = 2;

fn download_component_with_retry(
    dest: &Path,
    download: &mut dyn FnMut() -> Result<()>,
    verify: &mut dyn FnMut() -> Result<()>,
    on_retry: &mut dyn FnMut(u32),
) -> Result<()> {
    let mut last_err: Option<anyhow::Error> = None;
    for attempt in 0..=COMPONENT_RETRY_MAX {
        if attempt > 0 {
            on_retry(attempt);
        }
        match download() {
            Ok(()) => {}
            Err(err) => {
                // 下载失败:保留 .part/.meta → 下一轮断点续传接力
                last_err = Some(err);
                continue;
            }
        }
        match verify() {
            Ok(()) => return Ok(()),
            Err(err) => {
                // sha 失配=坏资产:清 dest 与续传残档,下一轮全新下
                let _ = fs::remove_file(dest);
                let (part, meta) = download_part_paths(dest);
                clear_part_files(&part, &meta);
                last_err = Some(err);
            }
        }
    }
    Err(last_err.unwrap_or_else(|| anyhow!("component download failed")))
}

fn download_component_updates(
    app: &AppHandle,
    plan: &UpdatePlan,
    config: &ReleaseConfig,
    changed: &[ManifestComponent],
    start_pct: u8,
    end_pct: u8,
) -> Result<StagedComponents> {
    let lock_url = plan
        .components_lock_url
        .as_ref()
        .context("manifest 缺 componentsLockUrl")?;
    let lock_sha = plan
        .components_lock_sha256
        .as_deref()
        .context("manifest 缺 componentsLockSha256")?;
    let cache_dir = cached_runtime_archive_path(app, config)?
        .parent()
        .map(|p| p.to_path_buf())
        .context("runtime 缓存目录不可用")?;
    ensure_dir(&cache_dir)?;
    let lock_path = cache_dir.join("components-lock.update.json");
    update_ledger_begin_asset("components-lock", 0, 0);
    download_update_asset(
        app,
        lock_url,
        &lock_path,
        start_pct,
        start_pct,
        "下载部件清单",
    )?;
    verify_sha256(&lock_path, Some(lock_sha), "部件清单")?;
    let new_lock_text = fs::read_to_string(&lock_path)?;
    let new_lock_json: serde_json::Value =
        serde_json::from_str(&new_lock_text).context("解析部件清单 JSON")?;
    // 身份与一致性:lock 必须与 manifest 同 runtimeVersion/appName,且逐部件 sha 一致。
    let lock_rt = new_lock_json
        .get("runtimeVersion")
        .and_then(|v| v.as_str())
        .unwrap_or("");
    if Some(lock_rt) != plan.runtime_version.as_deref() {
        return Err(anyhow!(
            "部件清单 runtimeVersion({}) 与更新计划({:?})不符",
            lock_rt,
            plan.runtime_version
        ));
    }
    let lock_app = new_lock_json
        .get("appName")
        .and_then(|v| v.as_str())
        .unwrap_or("");
    if lock_app != APP_NAME {
        return Err(anyhow!(
            "部件清单归属({})与本应用({})不符,拒绝增量",
            lock_app,
            APP_NAME
        ));
    }
    let lock_map = lock_component_map(&new_lock_json);
    if let Some(manifest_comps) = plan.components.as_ref() {
        for c in manifest_comps {
            let ok = lock_map
                .get(&c.name)
                .and_then(|v| v.get("sha256"))
                .and_then(|v| v.as_str())
                == Some(c.sha256.as_str());
            if !ok {
                return Err(anyhow!("部件 {} 在清单与 manifest 间 sha 不一致", c.name));
            }
        }
    }
    let mut archives = Vec::new();
    let total = changed.len().max(1) as u32;
    for (idx, comp) in changed.iter().enumerate() {
        let dest = cache_dir.join(&comp.file);
        let seg = (end_pct - start_pct) as u32;
        let s = start_pct + (seg * idx as u32 / total) as u8;
        let e = start_pct + (seg * (idx as u32 + 1) / total) as u8;
        update_ledger_begin_asset(&comp.name, idx as u32 + 1, changed.len() as u32);
        let label = format!("下载组件 {}({}/{})", comp.name, idx + 1, changed.len());
        download_component_with_retry(
            &dest,
            &mut || download_update_asset(app, &comp.url, &dest, s, e, &label),
            &mut || verify_sha256(&dest, Some(&comp.sha256), &format!("组件 {}", comp.name)),
            &mut |attempt| {
                // 重试:进度段回卷重进(账本重挂当前资产),事件可视
                update_ledger_begin_asset(&comp.name, idx as u32 + 1, changed.len() as u32);
                emit_update_event(
                    app,
                    &serde_json::json!({
                        "phase": "downloading",
                        "pct": s,
                        "message": format!(
                            "组件 {} 下载/校验未过,第 {}/{} 次重试…",
                            comp.name, attempt, COMPONENT_RETRY_MAX
                        ),
                    })
                    .to_string(),
                );
            },
        )?;
        archives.push((comp.clone(), dest));
    }
    Ok(StagedComponents {
        archives,
        new_lock_json,
        new_lock_text,
    })
}

fn clone_dir_fast(src: &Path, dst: &Path) -> Result<()> {
    // APFS clonefile(秒级零空间);非 APFS 卷退化普通拷贝。cp -R 对 symlink 原样拷。
    let cloned = Command::new("/bin/cp")
        .arg("-Rc")
        .arg(src)
        .arg(dst)
        .stdout(Stdio::null())
        .stderr(Stdio::null())
        .status()
        .map(|s| s.success())
        .unwrap_or(false);
    if cloned {
        return Ok(());
    }
    remove_dir_if_exists(dst)?;
    let status = Command::new("/bin/cp")
        .arg("-R")
        .arg(src)
        .arg(dst)
        .status()
        .context("clone runtime for component staging")?;
    if !status.success() {
        return Err(anyhow!("复制 runtime 暂存副本失败"));
    }
    Ok(())
}

// ============ 原生流式解压(WS-1c) ============
// flate2+tar 流式:进度=压缩流读取位置/归档大小(零预扫,一遍完成);
// 单线程解码(tar 流不可并行解码)+ 有界并发写盘(小文件投池,in-flight ≤64MB;
// 目录/链接/大文件主线程顺序,硬链前 flush 池保序)。
// 外部 /usr/bin/tar 路径整体保留:native 出错自动回退重解;HOROSA_EXTRACT_NATIVE=0 直退。

const SMALL_FILE_LIMIT: u64 = 8 * 1024 * 1024;
const EXTRACT_INFLIGHT_CAP: u64 = 64 * 1024 * 1024;

fn extract_native_enabled() -> bool {
    std::env::var("HOROSA_EXTRACT_NATIVE")
        .map(|v| !matches!(v.as_str(), "0" | "false" | "no" | "off"))
        .unwrap_or(true)
}

fn extract_concurrency() -> usize {
    std::env::var("HOROSA_EXTRACT_CONCURRENCY")
        .ok()
        .and_then(|v| v.parse::<usize>().ok())
        .map(|n| n.clamp(1, 16))
        .unwrap_or(4)
}

/// 读取字节计数器:包在 gz 解码器之下,暴露压缩流位置作为进度分子。
struct CountingReader<R: Read> {
    inner: R,
    count: Arc<std::sync::atomic::AtomicU64>,
}
impl<R: Read> Read for CountingReader<R> {
    fn read(&mut self, buf: &mut [u8]) -> std::io::Result<usize> {
        let n = self.inner.read(buf)?;
        self.count
            .fetch_add(n as u64, std::sync::atomic::Ordering::Relaxed);
        Ok(n)
    }
}

/// 剥 strip 个前导组件并做路径消毒。Ok(None)=条目整个被剥掉(如顶层目录自身)。
/// ParentDir/RootDir 一律拒绝(路径逃逸);前导 CurDir(`./`)透明滤除。
fn strip_tar_path(raw: &Path, strip: usize) -> Result<Option<PathBuf>> {
    let mut normals: Vec<&std::ffi::OsStr> = Vec::new();
    for comp in raw.components() {
        match comp {
            std::path::Component::Normal(seg) => normals.push(seg),
            std::path::Component::CurDir => {}
            _ => {
                return Err(anyhow!(
                    "archive entry path escapes dest: {}",
                    raw.display()
                ));
            }
        }
    }
    if normals.len() <= strip {
        return Ok(None);
    }
    let mut out = PathBuf::new();
    for seg in &normals[strip..] {
        out.push(seg);
    }
    Ok(Some(out))
}

struct WriteJob {
    path: PathBuf,
    data: Vec<u8>,
    mode: Option<u32>,
    mtime: Option<u64>,
}

fn extract_write_one(job: &WriteJob) -> std::io::Result<()> {
    use std::os::unix::fs::PermissionsExt;
    if let Some(parent) = job.path.parent() {
        fs::create_dir_all(parent)?;
    }
    // 先删旧条目:防 File::create 写穿同名旧 symlink(组件解压目标树带旧内容)。
    let _ = fs::remove_file(&job.path);
    let mut file = File::create(&job.path)?;
    file.write_all(&job.data)?;
    if let Some(mode) = job.mode {
        let _ = file.set_permissions(fs::Permissions::from_mode(mode));
    }
    if let Some(mtime) = job.mtime {
        let _ = file
            .set_times(fs::FileTimes::new().set_modified(UNIX_EPOCH + Duration::from_secs(mtime)));
    }
    Ok(())
}

/// 有界并发写盘池:submit 按字节额度背压;flush=全部已提交 job 落盘;首个错误粘住。
struct WriterPool {
    tx: Option<std::sync::mpsc::Sender<WriteJob>>,
    workers: Vec<thread::JoinHandle<()>>,
    in_flight: Arc<(Mutex<u64>, std::sync::Condvar)>,
    error: Arc<Mutex<Option<String>>>,
}

impl WriterPool {
    fn new(concurrency: usize) -> Self {
        let (tx, rx) = std::sync::mpsc::channel::<WriteJob>();
        let rx = Arc::new(Mutex::new(rx));
        let in_flight: Arc<(Mutex<u64>, std::sync::Condvar)> =
            Arc::new((Mutex::new(0), std::sync::Condvar::new()));
        let error: Arc<Mutex<Option<String>>> = Arc::new(Mutex::new(None));
        let mut workers = Vec::new();
        for _ in 0..concurrency {
            let rx = rx.clone();
            let in_flight = in_flight.clone();
            let error = error.clone();
            workers.push(thread::spawn(move || loop {
                let job = {
                    let guard = match rx.lock() {
                        Ok(g) => g,
                        Err(_) => return,
                    };
                    guard.recv()
                };
                let Ok(job) = job else { return };
                let size = job.data.len() as u64;
                // 出错后仍消费队列(只减额度不写),防 submit 端死等背压。
                if error.lock().map(|g| g.is_none()).unwrap_or(false) {
                    if let Err(err) = extract_write_one(&job) {
                        if let Ok(mut slot) = error.lock() {
                            slot.get_or_insert(format!("{}: {}", job.path.display(), err));
                        }
                    }
                }
                let (lock, cvar) = &*in_flight;
                if let Ok(mut cur) = lock.lock() {
                    *cur = cur.saturating_sub(size);
                }
                cvar.notify_all();
            }));
        }
        Self {
            tx: Some(tx),
            workers,
            in_flight,
            error,
        }
    }

    fn check_error(&self) -> Result<()> {
        if let Ok(slot) = self.error.lock() {
            if let Some(msg) = slot.as_ref() {
                return Err(anyhow!("并发写盘失败: {}", msg));
            }
        }
        Ok(())
    }

    fn submit(&self, job: WriteJob) -> Result<()> {
        self.check_error()?;
        let size = job.data.len() as u64;
        let (lock, cvar) = &*self.in_flight;
        {
            let mut cur = lock.lock().map_err(|_| anyhow!("写盘池额度锁中毒"))?;
            while *cur > 0 && *cur + size > EXTRACT_INFLIGHT_CAP {
                cur = cvar.wait(cur).map_err(|_| anyhow!("写盘池额度锁中毒"))?;
            }
            *cur += size;
        }
        self.tx
            .as_ref()
            .context("写盘池已关闭")?
            .send(job)
            .map_err(|_| anyhow!("写盘池线程已退出"))?;
        Ok(())
    }

    /// 等全部已提交 job 落盘(硬链条目前必须调:链接目标先在)。
    fn flush(&self) -> Result<()> {
        let (lock, cvar) = &*self.in_flight;
        {
            let mut cur = lock.lock().map_err(|_| anyhow!("写盘池额度锁中毒"))?;
            while *cur > 0 {
                cur = cvar.wait(cur).map_err(|_| anyhow!("写盘池额度锁中毒"))?;
            }
        }
        self.check_error()
    }

    fn finish(mut self) -> Result<()> {
        self.tx.take();
        for worker in self.workers.drain(..) {
            let _ = worker.join();
        }
        self.check_error()
    }
}

/// 原生流式解压(gz→tar 一遍过):progress(压缩流已读, 归档总字节, 已落文件数)。
fn extract_tar_gz_native_with(
    archive_path: &Path,
    dest: &Path,
    strip: usize,
    concurrency: usize,
    progress: Option<&dyn Fn(u64, u64, u64)>,
) -> Result<()> {
    use std::os::unix::fs::PermissionsExt;
    let archive_size = fs::metadata(archive_path).map(|m| m.len()).unwrap_or(0);
    let file =
        File::open(archive_path).with_context(|| format!("open {}", archive_path.display()))?;
    let read_count = Arc::new(std::sync::atomic::AtomicU64::new(0));
    let counting = CountingReader {
        inner: file,
        count: read_count.clone(),
    };
    let gz = flate2::read::GzDecoder::new(counting);
    let mut archive = tar::Archive::new(gz);
    let pool = if concurrency > 1 {
        Some(WriterPool::new(concurrency))
    } else {
        None
    };
    let mut files_done: u64 = 0;
    let mut last_report = Instant::now();
    ensure_dir(dest)?;
    let result = (|| -> Result<()> {
        for entry in archive.entries().context("read tar entries")? {
            let mut entry = entry.context("read tar entry")?;
            let raw_path = entry.path().context("entry path")?.to_path_buf();
            let entry_type = entry.header().entry_type();
            // pax/GNU 元数据条目:内容已被 tar crate 应用到相邻条目,自身跳过。
            if matches!(
                entry_type,
                tar::EntryType::XHeader
                    | tar::EntryType::XGlobalHeader
                    | tar::EntryType::GNULongName
                    | tar::EntryType::GNULongLink
            ) {
                continue;
            }
            let Some(rel) = strip_tar_path(&raw_path, strip)? else {
                continue;
            };
            let out = dest.join(&rel);
            match entry_type {
                tar::EntryType::Directory => {
                    fs::create_dir_all(&out).with_context(|| format!("mkdir {}", out.display()))?;
                    if let Ok(mode) = entry.header().mode() {
                        let _ =
                            fs::set_permissions(&out, fs::Permissions::from_mode(mode & 0o7777));
                    }
                }
                tar::EntryType::Symlink => {
                    let target = entry
                        .link_name()
                        .context("symlink target")?
                        .context("symlink missing target")?
                        .to_path_buf();
                    if let Some(parent) = out.parent() {
                        fs::create_dir_all(parent)?;
                    }
                    let _ = fs::remove_file(&out);
                    std::os::unix::fs::symlink(&target, &out)
                        .with_context(|| format!("symlink {}", out.display()))?;
                    files_done += 1;
                }
                tar::EntryType::Link => {
                    // 硬链目标必须已落盘:flush 并发池后再建链。
                    if let Some(pool) = &pool {
                        pool.flush()?;
                    }
                    let raw_target = entry
                        .link_name()
                        .context("hardlink target")?
                        .context("hardlink missing target")?
                        .to_path_buf();
                    let target_rel = strip_tar_path(&raw_target, strip)?
                        .context("hardlink target stripped away")?;
                    let target = dest.join(target_rel);
                    if let Some(parent) = out.parent() {
                        fs::create_dir_all(parent)?;
                    }
                    let _ = fs::remove_file(&out);
                    fs::hard_link(&target, &out)
                        .with_context(|| format!("hardlink {}", out.display()))?;
                    files_done += 1;
                }
                tar::EntryType::Regular | tar::EntryType::Continuous => {
                    let size = entry.header().size().unwrap_or(0);
                    let mode = entry.header().mode().ok().map(|m| m & 0o7777);
                    let mtime = entry.header().mtime().ok();
                    if let Some(parent) = out.parent() {
                        fs::create_dir_all(parent)?;
                    }
                    let pooled = pool.is_some() && size <= SMALL_FILE_LIMIT;
                    if pooled {
                        let mut data = Vec::with_capacity(size as usize);
                        entry
                            .read_to_end(&mut data)
                            .with_context(|| format!("read entry data {}", raw_path.display()))?;
                        pool.as_ref().unwrap().submit(WriteJob {
                            path: out,
                            data,
                            mode,
                            mtime,
                        })?;
                    } else {
                        let _ = fs::remove_file(&out);
                        let mut file = File::create(&out)
                            .with_context(|| format!("create {}", out.display()))?;
                        std::io::copy(&mut entry, &mut file)
                            .with_context(|| format!("write {}", out.display()))?;
                        if let Some(mode) = mode {
                            let _ = file.set_permissions(fs::Permissions::from_mode(mode));
                        }
                        if let Some(mtime) = mtime {
                            let _ = file.set_times(
                                fs::FileTimes::new()
                                    .set_modified(UNIX_EPOCH + Duration::from_secs(mtime)),
                            );
                        }
                    }
                    files_done += 1;
                }
                other => {
                    return Err(anyhow!(
                        "archive entry type {:?} not supported by native extractor ({})",
                        other,
                        raw_path.display()
                    ));
                }
            }
            if let Some(cb) = progress {
                let now = Instant::now();
                if now.duration_since(last_report) >= Duration::from_millis(200) {
                    last_report = now;
                    cb(
                        read_count.load(std::sync::atomic::Ordering::Relaxed),
                        archive_size,
                        files_done,
                    );
                }
            }
        }
        Ok(())
    })();
    // 无论成败都要收池(join 线程);错误优先报主循环的。
    let pool_result = match pool {
        Some(pool) => pool.finish(),
        None => Ok(()),
    };
    result?;
    pool_result?;
    if let Some(cb) = progress {
        cb(archive_size, archive_size, files_done);
    }
    Ok(())
}

fn extract_tar_gz_native(
    archive_path: &Path,
    dest: &Path,
    strip: usize,
    progress: Option<&dyn Fn(u64, u64, u64)>,
) -> Result<()> {
    extract_tar_gz_native_with(archive_path, dest, strip, extract_concurrency(), progress)
}

/// 外部 /usr/bin/tar 解压(历史行为原样保留,native 的回退路径)。
fn tar_extract_external(archive: &Path, dest: &Path, strip1: bool) -> Result<()> {
    let mut cmd = Command::new("/usr/bin/tar");
    if strip1 {
        cmd.arg("--strip-components=1");
    }
    let status = cmd
        .arg("-xzf")
        .arg(archive)
        .arg("-C")
        .arg(dest)
        .env("COPYFILE_DISABLE", "1")
        .env("COPY_EXTENDED_ATTRIBUTES_DISABLE", "1")
        .status()
        .with_context(|| format!("extract {}", archive.display()))?;
    if !status.success() {
        return Err(anyhow!("解压失败: {}", archive.display()));
    }
    Ok(())
}

fn tar_extract_strip1(archive: &Path, dest: &Path) -> Result<()> {
    tar_extract_strip1_with(archive, dest, None)
}

fn tar_extract_strip1_with(
    archive: &Path,
    dest: &Path,
    progress: Option<&dyn Fn(u64, u64, u64)>,
) -> Result<()> {
    if extract_native_enabled() {
        match extract_tar_gz_native(archive, dest, 1, progress) {
            Ok(()) => return Ok(()),
            Err(err) => {
                // dest 此时可能有 native 半成品:外部 tar 重解同一批条目全量覆盖,无残留风险。
                eprintln!(
                    "[extract] native 解压失败,自动回退外部 tar 重解 {}: {err:#}",
                    archive.display()
                );
            }
        }
    }
    tar_extract_external(archive, dest, true)
        .with_context(|| format!("extract component {}", archive.display()))
}

/// 对单个 runtime root 应用增量部件:clone 暂存 → 手术 → 原子对换(失败 current 不动)。
fn apply_component_updates(dest_root: &Path, staged: &StagedComponents) -> Result<()> {
    apply_component_updates_with(dest_root, staged, None)
}

/// notify:安装阶段可视化(WS-1c)。None=现状逐字节一致(既有 component_apply_* 测试全绿即证明)。
fn apply_component_updates_with(
    dest_root: &Path,
    staged: &StagedComponents,
    notify: Option<&dyn Fn(&str)>,
) -> Result<()> {
    let say = |msg: &str| {
        if let Some(cb) = notify {
            cb(msg);
        }
    };
    let current = dest_root.join("current");
    if !current.exists() {
        return Err(anyhow!("增量前提缺失:{} 不存在", current.display()));
    }
    // required 锁:部件手术全程独占(clone→部件对换→swap;防两实例 _comp_stage 互踩)。
    let _surgery = acquire_surgery_lock_required(dest_root)?;
    let stage = dest_root.join("_comp_stage");
    remove_dir_if_exists(&stage)?;
    // 磁盘预检:非 APFS 退化拷贝最多需要一份 runtime 副本 + 解压余量。
    if let Some(avail) = available_disk_bytes(dest_root) {
        let need: u64 = staged
            .archives
            .iter()
            .map(|(_, p)| fs::metadata(p).map(|m| m.len()).unwrap_or(0))
            .sum::<u64>()
            .saturating_mul(3)
            .saturating_add(1_000_000_000);
        if avail < need {
            return Err(anyhow!(
                "磁盘空间不足:增量更新约需 {:.1} GB 可用空间,当前仅 {:.1} GB",
                need as f64 / 1e9,
                avail as f64 / 1e9
            ));
        }
    }
    let result = (|| -> Result<()> {
        say("克隆当前运行时(APFS 秒级)…");
        clone_dir_fast(&current, &stage)?;
        let old_lock = fs::read_to_string(stage.join("components-lock.json"))
            .ok()
            .and_then(|t| serde_json::from_str::<serde_json::Value>(&t).ok())
            .context("暂存副本缺已装部件清单(增量基准丢失)")?;
        let old_map = lock_component_map(&old_lock);
        let new_map = lock_component_map(&staged.new_lock_json);
        let comp_total = staged.archives.len();
        for (comp_idx, (comp, archive)) in staged.archives.iter().enumerate() {
            let comp_tag = format!("部件 {}/{}·{}", comp_idx + 1, comp_total, comp.name);
            let detail = new_map
                .get(&comp.name)
                .with_context(|| format!("新清单缺部件 {}", comp.name))?;
            if comp.kind == "tree" {
                // preserve:兄弟数据部件的子树先挪出(本部件 tar 不含它们),解压后放回。
                let preserve: Vec<String> = detail
                    .get("preserve")
                    .and_then(|v| v.as_array())
                    .map(|a| {
                        a.iter()
                            .filter_map(|v| v.as_str().map(|s| s.to_string()))
                            .collect()
                    })
                    .unwrap_or_default();
                let preserve_tmp = stage.join("_preserve_tmp");
                remove_dir_if_exists(&preserve_tmp)?;
                let mut moved = Vec::new();
                for (idx, rel) in preserve.iter().enumerate() {
                    let from = stage.join(rel);
                    if from.exists() {
                        let to = preserve_tmp.join(idx.to_string());
                        ensure_dir(preserve_tmp.as_path())?;
                        fs::rename(&from, &to).with_context(|| format!("暂存保留子树 {}", rel))?;
                        moved.push((rel.clone(), to));
                    }
                }
                let paths: Vec<String> = detail
                    .get("paths")
                    .and_then(|v| v.as_array())
                    .map(|a| {
                        a.iter()
                            .filter_map(|v| v.as_str().map(|s| s.to_string()))
                            .collect()
                    })
                    .unwrap_or_default();
                if paths.is_empty() {
                    return Err(anyhow!("tree 部件 {} 无 paths 声明", comp.name));
                }
                say(&format!("{}:清理旧内容…", comp_tag));
                for rel in &paths {
                    remove_dir_if_exists(&stage.join(rel))?;
                }
                let on_extract = |read: u64, total: u64, files: u64| {
                    if total == 0 {
                        return;
                    }
                    say(&format!(
                        "{}:解压 {}% · {} 个文件",
                        comp_tag,
                        ((read as f64 / total as f64) * 100.0).min(100.0).round() as u32,
                        files
                    ));
                };
                let extract_progress: Option<&dyn Fn(u64, u64, u64)> = if notify.is_some() {
                    Some(&on_extract)
                } else {
                    None
                };
                tar_extract_strip1_with(archive, &stage, extract_progress)?;
                for (rel, tmp) in moved {
                    let back = stage.join(&rel);
                    if back.exists() {
                        // 新 tar 已带该子树(部件边界调整),保留新内容。
                        remove_dir_if_exists(&tmp)?;
                    } else {
                        if let Some(parent) = back.parent() {
                            ensure_dir(parent)?;
                        }
                        fs::rename(&tmp, &back).with_context(|| format!("放回保留子树 {}", rel))?;
                    }
                }
                remove_dir_if_exists(&preserve_tmp)?;
            } else {
                // files 型:消失文件 =(旧清单 files − 新清单 files)逐个删除,再覆盖解压。
                let files_of = |v: &serde_json::Value| -> Vec<String> {
                    v.get("files")
                        .and_then(|x| x.as_array())
                        .map(|a| {
                            a.iter()
                                .filter_map(|x| x.as_str().map(|s| s.to_string()))
                                .collect()
                        })
                        .unwrap_or_default()
                };
                let new_files: std::collections::HashSet<String> =
                    files_of(detail).into_iter().collect();
                if new_files.is_empty() {
                    return Err(anyhow!("files 部件 {} 无 files 清单", comp.name));
                }
                if let Some(old_detail) = old_map.get(&comp.name) {
                    for f in files_of(old_detail) {
                        if !new_files.contains(&f) {
                            let _ = fs::remove_file(stage.join(&f));
                        }
                    }
                }
                say(&format!("{}:更新文件…", comp_tag));
                tar_extract_strip1(archive, &stage)?;
            }
        }
        say("写入部件清单…");
        // 新部件清单 + runtime-manifest(version/builtAt/appName 从新 lock 派生)落盘。
        fs::write(stage.join("components-lock.json"), &staged.new_lock_text)?;
        let manifest_json = serde_json::json!({
            "version": staged.new_lock_json.get("runtimeVersion").and_then(|v| v.as_str()).unwrap_or(""),
            "built_at": staged.new_lock_json.get("builtAt").and_then(|v| v.as_str()).unwrap_or(""),
            "appName": staged.new_lock_json.get("appName").and_then(|v| v.as_str()).unwrap_or(APP_NAME),
        });
        fs::write(
            stage.join("runtime-manifest.json"),
            serde_json::to_string_pretty(&manifest_json)? + "\n",
        )?;
        prepare_runtime_dir(&stage)?;
        Ok(())
    })();
    if let Err(err) = result {
        let _ = remove_dir_if_exists(&stage);
        return Err(err);
    }
    // [U-A kill-atomic] 原子对换(与全量 extract_runtime_archive_with 同款协议):
    // 首选 renamex_np 单点互换,current 恒为全旧或全新;回退两段 rename(kill 窗口
    // 由启动期 repair_torn_runtime_slots 撕裂探测兜底)。
    say("原子切换运行时…");
    let backup = dest_root.join("previous");
    remove_dir_if_exists(&backup)?;
    if atomic_swap_dirs(&stage, &current)? {
        // swap 后 stage 位置上是旧树 → 挪 previous;挪失败即撤销 swap 恢复原状
        if let Err(err) = fs::rename(&stage, &backup) {
            let _ = atomic_swap_dirs(&stage, &current);
            let _ = remove_dir_if_exists(&stage);
            return Err(anyhow::Error::from(err).context("旧运行时挪 previous 槽失败"));
        }
    } else {
        fs::rename(&current, &backup)?;
        if let Err(err) = fs::rename(&stage, &current) {
            let _ = fs::rename(&backup, &current);
            let _ = remove_dir_if_exists(&stage);
            return Err(err.into());
        }
    }
    let _ = Command::new("/usr/bin/xattr")
        .arg("-dr")
        .arg("com.apple.quarantine")
        .arg(&current)
        .stdout(Stdio::null())
        .stderr(Stdio::null())
        .status();
    open_shared_tree_permissions(&current);
    // WS-1d 看门狗:previous 槽保留到首次成功 ready(同 extract_runtime_archive_with 语义)。
    clear_runtime_pending_marker(&current)?;
    Ok(())
}

fn recover_runtime_from_cached_archives(
    window: &WebviewWindow,
    config: &ReleaseConfig,
    candidates: &[PathBuf],
    dest_root: &Path,
    recovered_runtime_dir: &Path,
    progress_step: &str,
    recovered_step: &str,
    start_status_prefix: &str,
    success_status: &str,
) -> Result<()> {
    emit_launcher_state(window, &build_repair_in_progress_state());
    emit_mode(window, "repair");
    emit_progress(window, 18, progress_step);

    let mut last_err = None;
    for archive in candidates {
        match archive_runtime_version(&archive) {
            Ok(version) if version.trim() != config.runtime_version.trim() => {
                emit_status(
                    window,
                    &format!(
                        "跳过本地缓存归档 {}：版本 {} 与当前要求的 {} 不一致。",
                        archive.display(),
                        version.trim(),
                        config.runtime_version
                    ),
                );
                last_err = Some(anyhow!(
                    "runtime archive {} has version {}, expected {}",
                    archive.display(),
                    version.trim(),
                    config.runtime_version
                ));
                continue;
            }
            Ok(_) => {}
            Err(err) => {
                last_err = Some(err);
                continue;
            }
        }
        emit_status(
            window,
            &format!("{}：{}", start_status_prefix, archive.display()),
        );
        match extract_runtime_archive(&archive, dest_root) {
            Ok(()) => {
                if runtime_matches_expected(recovered_runtime_dir, &config.runtime_version) {
                    emit_progress(window, 36, recovered_step);
                    emit_status(window, success_status);
                    return Ok(());
                }
                last_err = Some(anyhow!(
                    "runtime recovered from {} into {} but still not usable",
                    archive.display(),
                    recovered_runtime_dir.display()
                ));
            }
            Err(err) => {
                last_err = Some(err);
            }
        }
    }

    if let Some(err) = last_err {
        return Err(err);
    }
    Err(anyhow!("no cached runtime archive candidates were usable"))
}

fn recover_shared_runtime_from_cached_offline_assets(
    app: &AppHandle,
    window: &WebviewWindow,
    config: &ReleaseConfig,
) -> Result<Option<RuntimePaths>> {
    let candidates = local_runtime_archive_candidates(app, config)?;
    if candidates.is_empty() {
        return Ok(None);
    }
    recover_runtime_from_cached_archives(
        window,
        config,
        &candidates,
        &shared_runtime_root(),
        &shared_runtime_dir(),
        "恢复共享本机组件",
        "已恢复共享本机组件",
        "检测到共享离线路径不完整，正在尝试用本地缓存恢复共享本机组件",
        "已从本地缓存恢复共享本机组件，将继续打开主界面。",
    )?;
    Ok(Some(shared_runtime_paths(app)?))
}

fn recover_user_runtime_from_cached_offline_assets(
    app: &AppHandle,
    window: &WebviewWindow,
    config: &ReleaseConfig,
) -> Result<Option<RuntimePaths>> {
    let user_root = user_runtime_root(app)?;
    let candidates = local_runtime_archive_candidates(app, config)?;
    if candidates.is_empty() {
        return Ok(None);
    }
    recover_runtime_from_cached_archives(
        window,
        config,
        &candidates,
        &user_root,
        &user_root.join("current"),
        "恢复当前用户本机组件",
        "已恢复当前用户本机组件",
        "检测到共享离线路径不完整，正在尝试用本地缓存恢复当前用户本机组件",
        "已从本地缓存恢复当前用户本机组件，将继续打开主界面。",
    )?;
    Ok(Some(resolve_runtime_paths(app)?))
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
            let mut cached_recovery_error = None;
            match recover_shared_runtime_from_cached_offline_assets(app, window, &config) {
                Ok(Some(paths)) => return Ok(paths),
                Ok(None) => {}
                Err(err) => cached_recovery_error = Some(err),
            }
            if user_runtime_matches_expected(app, &config.runtime_version)? {
                emit_mode(window, "launch");
                emit_progress(window, 36, "共享离线路径异常，已回退到当前用户本机组件");
                emit_status(
                    window,
                    "检测到共享离线路径不完整，但当前用户本机组件仍可用。本次将直接使用当前用户本机组件继续打开。",
                );
                return resolve_runtime_paths(app);
            }
            match recover_user_runtime_from_cached_offline_assets(app, window, &config) {
                Ok(Some(paths)) => return Ok(paths),
                Ok(None) => {}
                Err(err) => {
                    if cached_recovery_error.is_none() {
                        cached_recovery_error = Some(err);
                    }
                }
            }
            if let Some(err) = cached_recovery_error {
                return Err(err);
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
    // 进度带 18→56(此前 8→56:上一行刚推到 18%,下载一开始又倒退回 8%,被用户视作卡死/回滚)
    download_with_progress(window, &runtime_url, &archive_path, 18, 56, "准备本机组件")?;
    emit_status(window, "组件归档已就绪，正在部署本机组件…");
    emit_progress(window, 62, "部署本机组件");
    // 62→73 进度带按压缩流位置推进:此前 4-8s 的解压黑盒改为「正在展开组件 · 43% · 12,304 个文件」。
    let roots_total = install_roots.len().max(1);
    for (root_idx, runtime_root) in install_roots.iter().enumerate() {
        ensure_dir(runtime_root)?;
        let base = 62.0 + 11.0 * (root_idx as f64 / roots_total as f64);
        let span = 11.0 / roots_total as f64;
        let last_pct = std::cell::Cell::new(0u8);
        let on_extract = |read: u64, total: u64, files: u64| {
            if total == 0 {
                return;
            }
            let ratio = (read as f64 / total as f64).min(1.0);
            let pct = (base + span * ratio).round() as u8;
            if pct != last_pct.get() {
                last_pct.set(pct);
                emit_progress(
                    window,
                    pct,
                    &format!(
                        "正在展开组件 · {}% · {} 个文件",
                        (ratio * 100.0).round() as u32,
                        files
                    ),
                );
            }
        };
        extract_runtime_archive_with(&archive_path, runtime_root, Some(&on_extract), None)?;
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
                    // Header 构造改 infallible 兜底:异常 mime 字节序列不再 panic 静态服务线程。
                    let mut response = Response::from_data(bytes);
                    if let Ok(header) = Header::from_bytes(&b"Content-Type"[..], mime.as_bytes()) {
                        response = response.with_header(header);
                    }
                    // CSP 纵深防御:主界面经本静态服务器加载(不走 tauri 协议,tauri.conf 的
                    // csp 管不到这里)。umi 产物含 inline script/style,antd 动态注入样式,
                    // 3D(three/Babylon) 需 wasm;AI/排盘走本机回环端口。
                    if mime == "text/html" {
                        if let Ok(csp) = Header::from_bytes(
                            &b"Content-Security-Policy"[..],
                            &b"default-src 'self'; script-src 'self' 'unsafe-inline' 'unsafe-eval' 'wasm-unsafe-eval'; style-src 'self' 'unsafe-inline'; img-src 'self' data: blob:; font-src 'self' data:; connect-src 'self' http://127.0.0.1:* http://localhost:* ws://127.0.0.1:* ws://localhost:*; worker-src 'self' blob:; media-src 'self' blob: data:; object-src 'none'; base-uri 'none'; form-action 'self'; frame-src 'self'"[..],
                        ) {
                            response = response.with_header(csp);
                        }
                    }
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

// ── 会话中服务自愈(G1)──────────────────────────────────────────────
// 启动看门狗管「起不来」;这里管「跑着跑着死了」:内存压力 jetsam/杀软误杀/误 kill 后,
// 前端身份自愈只会换口找服务、救不活死进程——由壳层探活并限频自动重启;重启后的新端口
// 经 get_backend_endpoints 真值 + 前端 renegotiate(verify-to-switch)闭环,前端零改动。
static BOOTSTRAP_BUSY: AtomicUsize = AtomicUsize::new(0);
static SUPERVISOR_GENERATION: AtomicU64 = AtomicU64::new(0);

/// 启动/修复/更新等「预期内服务不在」的窗口挂本守卫,探活线程静默跳过,防误判抢跑。
struct BootstrapBusyGuard;
impl BootstrapBusyGuard {
    fn hold() -> BootstrapBusyGuard {
        BOOTSTRAP_BUSY.fetch_add(1, Ordering::SeqCst);
        BootstrapBusyGuard
    }
}
impl Drop for BootstrapBusyGuard {
    fn drop(&mut self) {
        BOOTSTRAP_BUSY.fetch_sub(1, Ordering::SeqCst);
    }
}

fn bootstrap_busy() -> bool {
    BOOTSTRAP_BUSY.load(Ordering::SeqCst) > 0
}

fn probe_local_port(port: u16) -> bool {
    std::net::TcpStream::connect_timeout(
        &SocketAddr::from(([127, 0, 0, 1], port)),
        Duration::from_millis(600),
    )
    .is_ok()
}

// [U-F 深度健康探针] 手写 TcpStream HTTP GET /horosaIdentity——不用 reqwest:其默认吃
// HTTP_PROXY/系统代理,本机回环探针会被毒代理劫走出假阴性;TCP 直连天然免疫。
// 四分类:Ok=app 标记+nonce 全对;WrongIdentity=端口上是陌生进程/别的实例(立即判亡);
// HttpSilent=TCP 通但不答/非 JSON(wedged/GC 停顿/毒 200——TCP 探针的盲区,慢判);
// TcpDead=连不上(进程亡,快判)。
#[derive(Debug, Clone, Copy, PartialEq, Eq)]
enum IdentityProbe {
    Ok,
    WrongIdentity,
    HttpSilent,
    TcpDead,
    /// 身份/nonce 全对但「真算探针」失败:软 OOM/线程池被 hang 占满的灰区
    /// ——进程活着、身份线程秒回,业务算力已死。独立慢 streak 判定。
    DeepFail,
    /// 对端 proto<2(旧 runtime 不识 deep 参数):按通过处理,账本一次不误杀。
    DeepUnsupported,
}

fn probe_identity(
    port: u16,
    expect_app: &str,
    expect_nonce: &str,
    timeout: Duration,
    deep: bool,
) -> IdentityProbe {
    use std::io::{Read, Write};
    let addr = SocketAddr::from(([127, 0, 0, 1], port));
    let Ok(mut stream) = std::net::TcpStream::connect_timeout(&addr, timeout) else {
        return IdentityProbe::TcpDead;
    };
    let _ = stream.set_read_timeout(Some(timeout));
    let _ = stream.set_write_timeout(Some(timeout));
    // deep=1:服务端在身份响应里附带一次微型真算结果(deep:"ok"/"fail")——
    // 探「还能算」,非仅「身份线程活着」。仅 proto>=2 的对端支持;旧对端由 proto 门兜底。
    let path = if deep {
        "/horosaIdentity?deep=1"
    } else {
        "/horosaIdentity"
    };
    let request = format!(
        "GET {path} HTTP/1.1\r\nHost: 127.0.0.1:{port}\r\nConnection: close\r\nAccept: application/json\r\n\r\n"
    );
    if stream.write_all(request.as_bytes()).is_err() {
        return IdentityProbe::HttpSilent;
    }
    let mut raw = Vec::new();
    let mut buf = [0u8; 4096];
    loop {
        match stream.read(&mut buf) {
            Ok(0) => break,
            Ok(n) => {
                raw.extend_from_slice(&buf[..n]);
                // 有界读:身份响应是单行小 JSON,64KB 上限防陌生进程灌流
                if raw.len() > 64 * 1024 {
                    break;
                }
            }
            Err(_) => break,
        }
    }
    if raw.is_empty() {
        return IdentityProbe::HttpSilent;
    }
    let text = String::from_utf8_lossy(&raw);
    let Some(body_at) = text.find("\r\n\r\n") else {
        return IdentityProbe::HttpSilent;
    };
    let body = &text[body_at + 4..];
    // chunked 兜底:取首个 { 到末个 }(身份响应为单个小 JSON 对象)
    let json_slice = match (body.find('{'), body.rfind('}')) {
        (Some(s), Some(e)) if e >= s => &body[s..=e],
        _ => return IdentityProbe::HttpSilent,
    };
    let Ok(json) = serde_json::from_str::<serde_json::Value>(json_slice) else {
        return IdentityProbe::HttpSilent;
    };
    let app_tag = json.get("app").and_then(|v| v.as_str()).unwrap_or("");
    let nonce = json.get("nonce").and_then(|v| v.as_str()).unwrap_or("");
    if app_tag != expect_app {
        return IdentityProbe::WrongIdentity;
    }
    if !expect_nonce.is_empty() && nonce != expect_nonce {
        return IdentityProbe::WrongIdentity;
    }
    if deep {
        // proto 门(代数差免疫):旧 runtime(proto<2 或无 proto)不识 deep → 按通过,
        // 由调用方账本一次;proto>=2 必须回 deep 字段且为 "ok"。
        let proto = json.get("proto").and_then(|v| v.as_u64()).unwrap_or(1);
        if proto < 2 {
            return IdentityProbe::DeepUnsupported;
        }
        let deep_status = json.get("deep").and_then(|v| v.as_str()).unwrap_or("fail");
        if deep_status != "ok" {
            return IdentityProbe::DeepFail;
        }
    }
    IdentityProbe::Ok
}

// [U-F] 双 streak 判亡状态机(纯函数可测):TcpDead 快判(连续 2 轮=40s),HttpSilent
// 慢判(连续 6 轮=2min,容 GC 停顿/瞬时高载),WrongIdentity 立即判亡,Ok 全清零。
#[derive(Debug, Clone, Copy, Default, PartialEq, Eq)]
struct SupervisorStreak {
    dead: u32,
    silent: u32,
}
const SUPERVISOR_DEAD_ROUNDS: u32 = 2;
const SUPERVISOR_SILENT_ROUNDS: u32 = 6;

fn supervisor_step(streak: SupervisorStreak, probe: IdentityProbe) -> (SupervisorStreak, bool) {
    match probe {
        IdentityProbe::Ok => (SupervisorStreak::default(), false),
        // DeepFail=身份活着(浅层健康)→ 浅 streak 清零,由 deep_step 独立判;
        // DeepUnsupported=旧对端,等同 Ok。
        IdentityProbe::DeepFail | IdentityProbe::DeepUnsupported => {
            (SupervisorStreak::default(), false)
        }
        IdentityProbe::WrongIdentity => (SupervisorStreak::default(), true),
        IdentityProbe::TcpDead => {
            let next = SupervisorStreak {
                dead: streak.dead + 1,
                silent: 0,
            };
            (next, next.dead >= SUPERVISOR_DEAD_ROUNDS)
        }
        IdentityProbe::HttpSilent => {
            let next = SupervisorStreak {
                dead: 0,
                silent: streak.silent + 1,
            };
            (next, next.silent >= SUPERVISOR_SILENT_ROUNDS)
        }
    }
}

// 深探慢 streak(纯函数可测):连续 SUPERVISOR_DEEP_FAIL_ROUNDS 次深探失败
// (每 SUPERVISOR_DEEP_EVERY_ROUNDS 轮才发一次深探,即 ≈2×5min)才判「算力死」——
// 容忍单次高载/GC 长停顿;Ok 清零。
const SUPERVISOR_DEEP_EVERY_ROUNDS: u64 = 15;
const SUPERVISOR_DEEP_FAIL_ROUNDS: u32 = 2;

fn deep_step(streak: u32, deep_ok: bool) -> (u32, bool) {
    if deep_ok {
        (0, false)
    } else {
        let next = streak + 1;
        (next, next >= SUPERVISOR_DEEP_FAIL_ROUNDS)
    }
}

fn deep_probe_enabled() -> bool {
    std::env::var("HOROSA_DEEP_PROBE")
        .map(|v| v != "0")
        .unwrap_or(true)
}

fn deep_probe_every_rounds() -> u64 {
    std::env::var("HOROSA_DEEP_PROBE_EVERY")
        .ok()
        .and_then(|v| v.parse().ok())
        .filter(|v| *v > 0)
        .unwrap_or(SUPERVISOR_DEEP_EVERY_ROUNDS)
}

// [U-F] 服务监督事件通道(镜像 __horosaPending* 模式;老前端无 handler=无害)
fn emit_service_event(app: &AppHandle, json: &str) {
    if let Some(window) = app.get_webview_window(MAIN_WINDOW_LABEL) {
        let _ = window.eval(&format!(
            "window.__horosaPendingServiceEvent = {json}; \
if (window.__horosaServiceEvent) {{ window.__horosaServiceEvent({json}); }}"
        ));
    }
}

fn current_session_snapshot(app: &AppHandle) -> Option<RuntimeSession> {
    let state = app.try_state::<AppState>()?;
    let slot = state.session.lock().ok()?;
    slot.clone()
}

/// 菜单/探活看门狗共用的本地服务重启:停旧(带真实端口)→ 新端口全链拉起 → 会话真值更新。
// 失败定因包装:重启失败时做一次关键目录写测,PermissionDenied → 人话上浮
// (错误沿既有通道进对话框/账本,用户直接看到「哪个目录权限坏」而非泛化失败)。
fn restart_local_services(app: &AppHandle, origin: &str) -> Result<()> {
    let result = restart_local_services_inner(app, origin);
    if result.is_err() {
        if let Some(session) = current_session_snapshot(app) {
            if let Some(hint) = classify_permission_issue(&session.paths) {
                ledger_mark(
                    "rust.permission_probe_failed",
                    Some(serde_json::json!({ "hint": hint })),
                );
                return result.context(hint);
            }
        }
    }
    result
}

fn restart_local_services_inner(app: &AppHandle, origin: &str) -> Result<()> {
    if bootstrap_busy() {
        return Err(anyhow!("启动/修复/更新流程正在进行,请稍候片刻再试"));
    }
    let _busy = BootstrapBusyGuard::hold();
    let window = app
        .get_webview_window(MAIN_WINDOW_LABEL)
        .context("主窗口不可用")?;
    let session =
        current_session_snapshot(app).context("本地服务会话尚未建立(应用可能仍在启动中)")?;
    ledger_mark("rust.services_restart_begin", None);
    stop_runtime(
        &session.paths,
        Some((session.backend_port, session.chart_port)),
    );
    thread::sleep(Duration::from_millis(300));
    let mut backend_port = choose_free_port()?;
    let mut chart_port = choose_free_port()?;
    start_runtime_with_port_retry(
        &session.paths,
        &window,
        &mut backend_port,
        &mut chart_port,
        None,
        true,
        true,
        true,
    )?;
    if let Some(state) = app.try_state::<AppState>() {
        if let Ok(mut slot) = state.session.lock() {
            *slot = Some(RuntimeSession {
                paths: session.paths.clone(),
                backend_port,
                chart_port,
                web_port: session.web_port,
            });
        }
    }
    ledger_mark("rust.services_restarted", None);
    // 低打扰告知(信息横幅,可关闭):软 OOM 转硬死后自动拉起时,用户当次排盘
    // 会失败一次——明说「已自动恢复」,不留悬念。老前端无 handler=无害。
    emit_service_event(
        app,
        &serde_json::json!({
            "kind": "runtime_updated_elsewhere",
            "message": "本地计算服务已自动恢复。若刚才有操作失败,重试即可。",
        })
        .to_string(),
    );
    eprintln!("local services restarted via {origin}: backend={backend_port} chart={chart_port}");
    Ok(())
}

/// [U-F] 探活看门狗(深度化):ready 后每 20s 对双后端做 /horosaIdentity 深探
/// (probe_identity 四分类;TCP 探针只能看到「端口在听」,对 wedged/GC 死循环/陌生进程
/// squat 全盲——历史事故 的看门狗侧闭环)。TcpDead 连续 2 轮/HttpSilent 连续
/// 6 轮/WrongIdentity 立即 → 自动重启(30 分钟窗 ≤2 次,防坏环境重启风暴);
/// 超限单次闩锁:账本一行+emit supervisor_gave_up 事件(前端横幅显式化,不再静默)。
/// web 静态服务器一并纳管(TCP 探,不通连续 2 轮原地重建,独立限频)。
/// generation 令牌:每次 ready 换代,旧线程自退,不叠加。
// 磁盘水位闩(纯函数可测):低于阈值→触发一次(闩住不刷屏);回升到阈值×2 才解闩
// (防抖:在阈值附近抖动不会反复弹);读不到(卷异常)不动作。返回 (下一闩态, 本轮是否触发)。
fn disk_low_step(latched: bool, avail_bytes: Option<u64>, min_bytes: u64) -> (bool, bool) {
    match avail_bytes {
        None => (latched, false),
        Some(avail) => {
            if !latched && avail < min_bytes {
                (true, true)
            } else if latched && avail >= min_bytes.saturating_mul(2) {
                (false, false)
            } else {
                (latched, false)
            }
        }
    }
}

fn disk_watch_enabled() -> bool {
    std::env::var("HOROSA_DISK_WATCH")
        .map(|v| v != "0")
        .unwrap_or(true)
}

fn disk_min_bytes() -> u64 {
    std::env::var("HOROSA_DISK_MIN_MB")
        .ok()
        .and_then(|v| v.parse::<u64>().ok())
        .filter(|v| *v > 0)
        .unwrap_or(500)
        .saturating_mul(1024 * 1024)
}

// 权限自检:关键目录写测(临时探针文件)。PermissionDenied → 人话定因
// (此前权限坏只会泛化成启动失败/500,用户与排障者都无从下手)。其它错误不定因。
fn classify_permission_issue(paths: &RuntimePaths) -> Option<String> {
    for dir in [&paths.app_data_dir, &paths.logs_dir, &paths.runtime_dir] {
        let probe = dir.join(".horosa-perm-probe");
        match fs::write(&probe, b"x") {
            Ok(_) => {
                let _ = fs::remove_file(&probe);
            }
            Err(err) if err.kind() == std::io::ErrorKind::PermissionDenied => {
                return Some(format!(
                    "目录权限异常:{} 不可写。可尝试菜单「重装运行时」修复;公司管控机请联系管理员放开该目录。",
                    dir.display()
                ));
            }
            Err(_) => {}
        }
    }
    None
}

// 多实例更新感知纯函数:基线未定→以首见版本为基线;已定且磁盘版本不同→触发一次。
// (renamex 换 inode 后本实例仍跑旧树:探针恒 Ok,只有 manifest 版本对比能看见「别人更新了」。)
fn runtime_change_step(
    baseline: Option<String>,
    disk: Option<String>,
) -> (Option<String>, bool) {
    match (baseline, disk) {
        (None, Some(v)) => (Some(v), false),
        (Some(b), Some(now)) => {
            let changed = b != now;
            (Some(b), changed)
        }
        (b, None) => (b, false),
    }
}

fn start_service_supervisor(app: AppHandle) {
    let my_gen = SUPERVISOR_GENERATION.fetch_add(1, Ordering::SeqCst) + 1;
    thread::spawn(move || {
        let mut backend_streak = SupervisorStreak::default();
        let mut chart_streak = SupervisorStreak::default();
        let mut web_down = 0u32;
        let mut recent_restarts: Vec<Instant> = Vec::new();
        let mut recent_web_restarts: Vec<Instant> = Vec::new();
        let mut gave_up_latched = false;
        let mut round: u64 = 0;
        let mut boot_runtime_version: Option<String> = None;
        let mut runtime_changed_notified = false;
        let mut backend_deep_streak = 0u32;
        let mut chart_deep_streak = 0u32;
        let mut deep_unsupported_noted = false;
        let mut disk_low_latched = false;
        loop {
            thread::sleep(Duration::from_secs(20));
            if SUPERVISOR_GENERATION.load(Ordering::SeqCst) != my_gen {
                return;
            }
            if bootstrap_busy() {
                backend_streak = SupervisorStreak::default();
                chart_streak = SupervisorStreak::default();
                web_down = 0;
                continue;
            }
            let Some(session) = current_session_snapshot(&app) else {
                backend_streak = SupervisorStreak::default();
                chart_streak = SupervisorStreak::default();
                web_down = 0;
                continue;
            };
            round = round.wrapping_add(1);
            // 磁盘水位自感知(每 15 轮 ≈5min,statfs 零成本):写满盘是排盘 500/
            // 更新失败/日志丢失的共因,此前运行期零检测。跌破阈值一次性横幅告知;
            // 回升到 2× 阈值自动解闩(此后再跌破会再次提醒)。
            if disk_watch_enabled() && round % 15 == 0 {
                let avail = [
                    available_disk_bytes(&session.paths.app_data_dir),
                    available_disk_bytes(&session.paths.runtime_dir),
                ]
                .into_iter()
                .flatten()
                .min();
                let (next_latch, fire) = disk_low_step(disk_low_latched, avail, disk_min_bytes());
                disk_low_latched = next_latch;
                if fire {
                    ledger_mark(
                        "rust.disk_low",
                        Some(serde_json::json!({
                            "availBytes": avail.unwrap_or(0),
                        })),
                    );
                    emit_service_event(
                        &app,
                        &serde_json::json!({
                            "kind": "disk_low",
                            "message": "磁盘可用空间不足,可能影响排盘、日志与自动更新——请清理磁盘后继续使用。",
                        })
                        .to_string(),
                    );
                }
            }
            // 多实例感知:另一实例(可能是本机其他用户)更新共享 runtime 后,
            // 本实例仍持旧 inode 且探针恒 Ok → 每 15 轮(≈5min)比对 manifest 版本,
            // 变化即一次性提示(闩锁,不刷屏)。基线取首轮读到的版本。
            if !runtime_changed_notified {
                if boot_runtime_version.is_none() || round % 15 == 0 {
                    let disk_version =
                        read_runtime_manifest_from_path(&session.paths.manifest_path)
                            .map(|m| m.version);
                    let (next_baseline, changed) =
                        runtime_change_step(boot_runtime_version.take(), disk_version);
                    boot_runtime_version = next_baseline;
                    if changed {
                        runtime_changed_notified = true;
                        ledger_mark(
                            "rust.runtime_updated_elsewhere",
                            Some(serde_json::json!({
                                "baseline": boot_runtime_version.clone().unwrap_or_default(),
                            })),
                        );
                        emit_service_event(
                            &app,
                            &serde_json::json!({
                                "kind": "runtime_updated_elsewhere",
                                "message": "本机组件已在另一会话中完成更新(可能来自本机其他用户)。重启星阙后即可使用新版本。",
                            })
                            .to_string(),
                        );
                    }
                }
            }
            // web 静态服务器监督:tiny_http 线程死=整个 UI 白屏,且此前无任何看门狗。
            // 线程 panic 即 drop Server 即释放端口 → 同端口原地重建可行。
            if probe_local_port(session.web_port) {
                web_down = 0;
            } else {
                web_down += 1;
                if web_down >= 2 {
                    web_down = 0;
                    recent_web_restarts.retain(|t| t.elapsed() < Duration::from_secs(1800));
                    if recent_web_restarts.len() < 3 {
                        recent_web_restarts.push(Instant::now());
                        let shutdown = Arc::new(AtomicBool::new(false));
                        match start_static_server(
                            session.paths.frontend_dir.clone(),
                            session.web_port,
                            shutdown.clone(),
                        ) {
                            Ok(_handle) => {
                                if let Some(state) = app.try_state::<AppState>() {
                                    if let Ok(mut slot) = state.web_shutdown.lock() {
                                        if let Some(old) = slot.take() {
                                            old.store(true, Ordering::SeqCst);
                                        }
                                        *slot = Some(shutdown);
                                    }
                                }
                                ledger_mark("rust.web_server_restarted", None);
                            }
                            Err(err) => {
                                eprintln!("[supervisor] web 静态服务器重建失败: {err:#}")
                            }
                        }
                    }
                }
            }
            let nonce = launch_nonce();
            let probe_timeout = Duration::from_millis(1500);
            // 每 N 轮(默认 15≈5min)把浅探升级为深探(真算维度):
            // 软 OOM/线程池部分 wedge 时身份端点仍秒回 Ok,只有真算探针能看见。
            let deep_round = deep_probe_enabled() && round % deep_probe_every_rounds() == 0;
            let backend_probe = probe_identity(
                session.backend_port,
                "horosa-backend",
                nonce,
                probe_timeout,
                deep_round,
            );
            let chart_probe = probe_identity(
                session.chart_port,
                "horosa-chart",
                nonce,
                probe_timeout,
                deep_round,
            );
            if deep_round
                && !deep_unsupported_noted
                && (backend_probe == IdentityProbe::DeepUnsupported
                    || chart_probe == IdentityProbe::DeepUnsupported)
            {
                deep_unsupported_noted = true;
                ledger_mark("rust.deep_probe_unsupported", None);
            }
            let (bs, backend_dead) = supervisor_step(backend_streak, backend_probe);
            backend_streak = bs;
            let (cs, chart_dead) = supervisor_step(chart_streak, chart_probe);
            chart_streak = cs;
            // 深探独立慢 streak(仅深探轮推进)
            let mut deep_dead = false;
            if deep_round {
                let (bds, bd) = deep_step(
                    backend_deep_streak,
                    backend_probe != IdentityProbe::DeepFail,
                );
                backend_deep_streak = bds;
                let (cds, cd) =
                    deep_step(chart_deep_streak, chart_probe != IdentityProbe::DeepFail);
                chart_deep_streak = cds;
                if bd || cd {
                    deep_dead = true;
                    ledger_mark(
                        "rust.deep_probe_fail",
                        Some(serde_json::json!({
                            "backendStreak": backend_deep_streak,
                            "chartStreak": chart_deep_streak,
                        })),
                    );
                }
            }
            let backend_healthy = matches!(
                backend_probe,
                IdentityProbe::Ok | IdentityProbe::DeepUnsupported
            );
            let chart_healthy = matches!(
                chart_probe,
                IdentityProbe::Ok | IdentityProbe::DeepUnsupported
            );
            if backend_healthy && chart_healthy && !deep_dead {
                // 全健康:解除 gave_up 闩锁(人工重启成功后允许未来再次自动修复+提示)
                gave_up_latched = false;
                continue;
            }
            if !(backend_dead || chart_dead || deep_dead) {
                continue;
            }
            backend_streak = SupervisorStreak::default();
            chart_streak = SupervisorStreak::default();
            backend_deep_streak = 0;
            chart_deep_streak = 0;
            recent_restarts.retain(|t| t.elapsed() < Duration::from_secs(1800));
            if recent_restarts.len() >= 2 {
                // 越限:单次闩锁——账本一行(不再每 20s 刷屏)+显式事件交前端横幅
                if !gave_up_latched {
                    gave_up_latched = true;
                    ledger_mark("rust.supervisor_gave_up", None);
                    emit_service_event(
                        &app,
                        &serde_json::json!({
                            "kind": "supervisor_gave_up",
                            "message": "本地服务多次自动重启未果，已暂停自动修复。可点「重启服务」手动重启，或打开诊断中心查看原因。",
                        })
                        .to_string(),
                    );
                }
                continue;
            }
            recent_restarts.push(Instant::now());
            ledger_mark(
                "rust.supervisor_auto_restart",
                Some(serde_json::json!({
                    "backendProbe": format!("{:?}", backend_probe),
                    "chartProbe": format!("{:?}", chart_probe),
                    "reason": if deep_dead && !(backend_dead || chart_dead) {
                        "deep_probe"
                    } else {
                        "identity_probe"
                    },
                })),
            );
            if let Err(err) = restart_local_services(&app, "supervisor") {
                eprintln!("supervisor auto-restart failed: {err:#}");
            }
        }
    });
}

// [U-F] 轻量服务重启命令(前端横幅「重启服务」用;此前横幅错线到
// trigger_runtime_repair_command=全量修复流,对「服务死了」场景过重)。
#[tauri::command]
fn restart_local_services_command(app: AppHandle) -> std::result::Result<(), String> {
    restart_local_services(&app, "frontend").map_err(|err| format!("{err:#}"))
}

fn stop_runtime(paths: &RuntimePaths, ports: Option<(u16, u16)>) {
    if !paths.stop_script.exists() {
        return;
    }
    let mut command = Command::new("/bin/bash");
    command
        .arg(&paths.stop_script)
        .current_dir(paths.runtime_dir.join("Horosa-Web"))
        .stdout(Stdio::null())
        .stderr(Stdio::null());
    // 会话真实端口交给脚本(与 stop_runtime_detached 同款):pid 文件按端口后缀定位、
    // 端口兜底扫描打到真端口——不传则脚本只会看默认口 8899/9999,动态选口的会话
    // 停不干净(半启动服务在重试路径上泄漏)。
    if let Some((backend_port, chart_port)) = ports {
        command
            .env("HOROSA_SERVER_PORT", backend_port.to_string())
            .env("HOROSA_CHART_PORT", chart_port.to_string());
    }
    let _ = command.status();
}

fn start_runtime(
    paths: &RuntimePaths,
    window: &WebviewWindow,
    backend_port: u16,
    chart_port: u16,
    startup_timeout_secs: Option<u64>,
    skip_runtime_warmup: bool,
    skip_mongo_ping: bool,
    trusted_runtime: bool,
) -> Result<()> {
    // 进度前置:下方预清理/预停止在冷文件系统缓存下可耗时数秒,先把进度从 36 推到 82
    // (indeterminate 动画),否则 UI 冻在 36% 被当成卡死(用户实告)。
    emit_indeterminate_progress(window, 82, "正在准备启动环境…");
    ensure_dir(&paths.logs_dir)?;
    // trusted 快路径跳过全树元数据清理:cleanup_runtime_metadata 递归遍历整棵 runtime 树
    // (数万文件),冷缓存下可达数十秒;而解压末尾(extract_runtime_archive)与健康缓存 miss
    // 慢路径(runtime_dir_is_usable)都已各清过一次,trusted 启动时纯冗余。启动成功后另有
    // 后台 mop-up 兜底(runtime_bootstrap 尾部);fast-path 失败的回退分支以 trusted=false
    // 重启 → 清理照跑,自愈链完整。
    if !trusted_runtime {
        prepare_runtime_dir(&paths.runtime_dir)?;
    }
    stop_runtime(paths, Some((backend_port, chart_port)));
    emit_status(window, "正在后台启动 星阙 Python / Java 服务…");
    if trusted_runtime {
        emit_indeterminate_progress(window, 82, "正在后台启动本地服务,通常需 10~20 秒…");
    } else {
        // 首启/更新后走完整校验:冷 JVM + 首次预热在低速机上真实需要分钟级,
        // 预期管理到位,用户才不会当成卡死而强退(强退两次会触发看门狗回滚)。
        emit_indeterminate_progress(
            window,
            82,
            "首次(或更新后)启动正在完整校验并预热本地计算引擎,约需 1~2 分钟,请保持窗口打开…",
        );
    }

    let python_bin = runtime_python_bin(&paths.runtime_dir);
    let java_bin = paths.runtime_dir.join("runtime/mac/java/bin/java");
    let mut command = Command::new("/bin/bash");
    command
        .arg(&paths.start_script)
        .current_dir(paths.runtime_dir.join("Horosa-Web"))
        .env("HOROSA_SKIP_UI_BUILD", "1")
        .env("HOROSA_REQUIRE_EMBEDDED_RUNTIME", "1")
        .env("HOROSA_PYTHON", python_bin)
        .env("HOROSA_JAVA_BIN", java_bin)
        .env("HOROSA_SERVER_PORT", backend_port.to_string())
        .env("HOROSA_CHART_PORT", chart_port.to_string())
        // 启动会话 nonce:经 start 脚本环境继承进 Java/Python,被 /horosaIdentity 原样回显,
        // 前端据此确认「这个端口上的确是本会话拉起的后端」(防端口squat/跨实例串线)。
        .env("HOROSA_LAUNCH_NONCE", launch_nonce())
        // [U-I G1] GUI(LaunchServices)拉起的进程通常无 locale——非 ASCII(中文用户名)
        // home 路径在 JVM/子进程里有编解码风险;仅缺失时兜底,不覆盖用户显式设置。
        .env(
            "LANG",
            std::env::var("LANG").unwrap_or_else(|_| "zh_CN.UTF-8".to_string()),
        )
        .env(
            "HOROSA_SKIP_RUNTIME_WARMUP",
            if skip_runtime_warmup { "1" } else { "0" },
        )
        .env(
            "HOROSA_DESKTOP_MONGO_SKIP_PING",
            if skip_mongo_ping { "1" } else { "0" },
        )
        .env(
            "HOROSA_TRUSTED_RUNTIME",
            if trusted_runtime { "1" } else { "0" },
        )
        .env(
            "HOROSA_LOG_ROOT",
            paths.logs_dir.to_string_lossy().to_string(),
        )
        .env(
            "HOROSA_DIAG_DIR",
            paths.logs_dir.to_string_lossy().to_string(),
        )
        // 本地文档缓存每用户独立(app_data_dir 下):共享树无锁 JSON 多用户并发会互踩。
        .env(
            "HOROSA_MONGO_FALLBACK_DIR",
            paths
                .logs_dir
                .parent()
                .unwrap_or(&paths.logs_dir)
                .join("mongo-fallback")
                .to_string_lossy()
                .to_string(),
        );
    // 启动账本:把 run 标签与账本文件传给脚本层(shell 再传 Java/Python),四层同文件聚合。
    if let Some((run_tag, ledger_file)) = ledger_env() {
        command.env("HOROSA_RUN_TAG", run_tag).env(
            "HOROSA_LEDGER_FILE",
            ledger_file.to_string_lossy().to_string(),
        );
    }
    // 本地回环探测防代理劫持(双保险,脚本侧 curl --noproxy / urllib 禁代理是第一道):
    // 用户 shell/launchctl 注入的代理变量会把脚本内 127.0.0.1 探测与热身请求劫持进代理 →
    // 服务在听也探不到 → 首启永不就绪。spawn 前显式剥掉六个代理变量。
    for proxy_var in [
        "http_proxy",
        "https_proxy",
        "all_proxy",
        "HTTP_PROXY",
        "HTTPS_PROXY",
        "ALL_PROXY",
    ] {
        command.env_remove(proxy_var);
    }
    if let Some(timeout_secs) = startup_timeout_secs {
        command.env("HOROSA_STARTUP_TIMEOUT", timeout_secs.to_string());
    } else if !trusted_runtime {
        // 全新安装首启(untrusted)预算放宽:含 324MB jar 首次拷贝 + JVM 冷启 + 杀软扫描,
        // 慢盘机器 180s 临界(与脚本侧 untrusted 默认 300 对齐,这里显式传以防脚本默认被改)。
        command.env("HOROSA_STARTUP_TIMEOUT", "300");
    }
    // 心跳:output() 阻塞等脚本(就绪轮询通常 5~20s,冷启更久),每秒刷一次 indeterminate
    // 文案让进度条保持活动,避免长等待被当成卡死。错误路径同样先置停+join 再返回。
    // WS-1c 细分:借启动账本的 sh.py_http_ready / sh.java_http_ready 打点,
    // 把整段等待拆成「排盘引擎已就绪(1/2)→主服务已就绪(2/2)」两阶段可见。
    let heartbeat_stop = Arc::new(AtomicBool::new(false));
    let heartbeat = {
        let window = window.clone();
        let stop = heartbeat_stop.clone();
        let ledger_file = STARTUP_LEDGER
            .get()
            .and_then(|v| v.as_ref())
            .map(|(_, file, _)| file.clone());
        thread::spawn(move || {
            let started = Instant::now();
            loop {
                for _ in 0..10 {
                    thread::sleep(Duration::from_millis(100));
                    if stop.load(Ordering::Relaxed) {
                        return;
                    }
                }
                // 账本按 run 独立文件,读到什么段就是本次的(吞错:账本不可用退回笼统文案)
                let ledger_text = ledger_file
                    .as_ref()
                    .and_then(|f| fs::read_to_string(f).ok())
                    .unwrap_or_default();
                let stage = if ledger_text.contains("\"seg\":\"sh.java_http_ready\"") {
                    2u8
                } else if ledger_text.contains("\"seg\":\"sh.py_http_ready\"") {
                    1u8
                } else {
                    0u8
                };
                // progress-aware 续命可视:脚本侧账本出现 sh.ready_extend =
                // 预算已耗尽但检测到持续进展,正在自动延长——明说,防慢机用户当卡死强退。
                let extend_note = if ledger_text.contains("\"seg\":\"sh.ready_extend\"") {
                    "(检测到持续进展,已自动延长等待)"
                } else {
                    ""
                };
                let message = match stage {
                    2 => format!(
                        "主服务已就绪(2/2),正在完成收尾…已等待 {} 秒{extend_note}",
                        started.elapsed().as_secs()
                    ),
                    1 => format!(
                        "排盘引擎已就绪(1/2),正在启动主服务…已等待 {} 秒{extend_note}",
                        started.elapsed().as_secs()
                    ),
                    _ => format!(
                        "正在启动本地服务…已等待 {} 秒{extend_note}",
                        started.elapsed().as_secs()
                    ),
                };
                emit_indeterminate_progress(&window, 82, &message);
            }
        })
    };
    ledger_mark("rust.script_spawn", None);
    let output_result = command.output().context("launch start_horosa_local.sh");
    heartbeat_stop.store(true, Ordering::Relaxed);
    let _ = heartbeat.join();
    let output = output_result?;
    ledger_mark(
        "rust.script_returned",
        Some(serde_json::json!({"exit": output.status.code().unwrap_or(-1)})),
    );
    if !output.status.success() {
        let code = output.status.code().unwrap_or(-1);
        let stdout = String::from_utf8_lossy(&output.stdout);
        let stderr = String::from_utf8_lossy(&output.stderr);
        // 退出码 3 = 脚本判定为「端口被占 / bind 冲突」(可重试);其它码 = 真实故障(不重试)。
        // 把 (exit N) 写进错误消息,既供诊断也作为 error_is_port_conflict 的识别信号。
        return Err(anyhow!(
            "星阙 backend start failed (exit {})\nstdout:\n{}\nstderr:\n{}",
            code,
            stdout,
            stderr
        ));
    }
    emit_progress(window, 92, "本地服务已就绪");
    Ok(())
}

/// 修法1:脚本以 exit 3 表示「端口被占 / bind 冲突」,可换口重试。
/// 仅匹配本函数上方自己生成的固定前缀,避免脚本输出里偶然出现的同形文本误判。
fn error_is_port_conflict(e: &anyhow::Error) -> bool {
    format!("{:#}", e).contains("start failed (exit 3)")
}

/// 修法1:backend/chart 端口冲突自动重试。
/// 铁律:web 端口 / 静态服务器完全不参与本环(在 runtime_bootstrap 中已先于此起好并由 Rust 持有),
/// 这里只重选 backend/chart 一对端口;`AppState.web_shutdown` 绝不在此被读写。
/// - 失败码 == 端口冲突(exit 3)且仍有重试次数 → stop_runtime + 退避 + 换一对全新空闲端口重试;
/// - 非端口类错误,或端口重试已耗尽 → 原样返回错误,交回上层既有的「更新后首启 / 快路径回退」分支处理。
/// 成功时 `*backend_port`/`*chart_port` 持有真正生效的那对端口(供 frontend_url 使用)。
#[allow(clippy::too_many_arguments)]
fn start_runtime_with_port_retry(
    paths: &RuntimePaths,
    window: &WebviewWindow,
    backend_port: &mut u16,
    chart_port: &mut u16,
    startup_timeout_secs: Option<u64>,
    skip_runtime_warmup: bool,
    skip_mongo_ping: bool,
    trusted_runtime: bool,
) -> Result<()> {
    let mut last_err: Option<anyhow::Error> = None;
    for attempt in 0..PORT_RETRY_MAX {
        match start_runtime(
            paths,
            window,
            *backend_port,
            *chart_port,
            startup_timeout_secs,
            skip_runtime_warmup,
            skip_mongo_ping,
            trusted_runtime,
        ) {
            Ok(()) => return Ok(()),
            Err(e) => {
                let is_port = error_is_port_conflict(&e);
                last_err = Some(e);
                if is_port && attempt + 1 < PORT_RETRY_MAX {
                    emit_status(window, "检测到端口被占用，正在自动重选端口重试…");
                    stop_runtime(paths, Some((*backend_port, *chart_port)));
                    thread::sleep(Duration::from_millis(400));
                    *backend_port = choose_free_port()?;
                    *chart_port = choose_free_port()?;
                    continue;
                }
                break;
            }
        }
    }
    Err(last_err.unwrap_or_else(|| anyhow!("星阙 backend start failed (port retry exhausted)")))
}

/// 每次壳进程一枚的启动会话 nonce:注入后端环境(HOROSA_LAUNCH_NONCE)与前端 URL(&sid=)。
/// 前端身份握手(GET /horosaIdentity)据此把「端口被其它进程/其它星阙实例占用」与真后端
/// 区分开——本地服务地址永不盲信。非安全边界,只做防混淆凭据;同一壳会话内「重启后端」
/// 复用同值,前端无需重新协商。
fn launch_nonce() -> &'static str {
    use std::sync::OnceLock;
    static NONCE: OnceLock<String> = OnceLock::new();
    NONCE.get_or_init(|| {
        let mut hasher = Sha256::new();
        hasher.update(std::process::id().to_le_bytes());
        if let Ok(dur) = SystemTime::now().duration_since(UNIX_EPOCH) {
            hasher.update(dur.as_nanos().to_le_bytes());
        }
        let digest = hasher.finalize();
        digest
            .iter()
            .take(8)
            .map(|b| format!("{:02x}", b))
            .collect::<String>()
    })
}

/// 前端服务地址自愈再协商的真值源:返回本会话真实后端端点 + 启动 nonce,
/// 与启动 URL 的 srv/chartSrv/kentangSrv/sid 查询参数同构。
/// 前端在身份握手失败(端口被其它进程占用/localStorage 陈旧/推导落空)时调用。
#[derive(Debug, Clone, Serialize)]
#[serde(rename_all = "camelCase")]
struct BackendEndpoints {
    srv: String,
    chart_srv: String,
    kentang_srv: String,
    sid: String,
}

#[tauri::command]
fn get_backend_endpoints(app: AppHandle) -> std::result::Result<BackendEndpoints, String> {
    let state = app.state::<AppState>();
    let session = state.session.lock().map_err(|e| e.to_string())?;
    let Some(session) = session.as_ref() else {
        return Err("backend session not started".into());
    };
    Ok(BackendEndpoints {
        srv: format!("http://127.0.0.1:{}", session.backend_port),
        chart_srv: format!("http://127.0.0.1:{}", session.chart_port),
        kentang_srv: format!("http://127.0.0.1:{}", session.chart_port),
        sid: launch_nonce().to_string(),
    })
}

fn frontend_url(web_port: u16, backend_port: u16, chart_port: u16) -> String {
    let backend_root = format!("http://127.0.0.1:{}", backend_port);
    let chart_root = format!("http://127.0.0.1:{}", chart_port);
    format!(
        "http://127.0.0.1:{}/index.html?srv={}&chartSrv={}&kentangSrv={}&sid={}&v={}",
        web_port,
        urlencoding::encode(&backend_root),
        urlencoding::encode(&chart_root),
        urlencoding::encode(&chart_root),
        launch_nonce(),
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
    // #22：持久化缩放到 preferences.json，重启恢复（修复字号重开复位）
    let mut prefs = load_preferences(app);
    prefs.zoom_level = clamped;
    let _ = save_preferences(app, &prefs);
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

// [U-I G8] 把当前 .app 拷入 /Applications 固定安装位并重开(Translocation 只读挂载
// 点/桌面/下载目录直跑的用户,自更新链路找不到真实 App 路径——搬到固定位一劳永逸)。
// 成功即 exit(0) 交棒新副本;返回非空字符串=无需动作的说明文案。
fn relocate_app_to_applications(app: &AppHandle) -> Result<String> {
    let bundle = app_bundle_path().context("未在 .app 包内运行,无需搬迁")?;
    let dest = installed_app_target_path();
    if bundle == dest {
        return Ok("当前已从「应用程序」文件夹运行,无需搬迁。".to_string());
    }
    if dest.exists() {
        return Err(anyhow!(
            "「应用程序」里已存在 {},请直接打开它(或先删除旧副本再试)。",
            dest.display()
        ));
    }
    let copied = Command::new("/usr/bin/ditto")
        .arg(&bundle)
        .arg(&dest)
        .stdout(Stdio::null())
        .stderr(Stdio::null())
        .status()
        .map(|s| s.success())
        .unwrap_or(false);
    if !copied {
        return Err(anyhow!("拷贝到「应用程序」失败(可能没有写入权限)"));
    }
    let _ = Command::new("/usr/bin/xattr")
        .arg("-dr")
        .arg("com.apple.quarantine")
        .arg(&dest)
        .stdout(Stdio::null())
        .stderr(Stdio::null())
        .status();
    Command::new("/usr/bin/open")
        .arg("-n")
        .arg(&dest)
        .spawn()
        .context("打开「应用程序」里的新副本")?;
    app.exit(0);
    Ok(String::new())
}

fn handoff_to_newer_installed_app(app: &AppHandle) -> Result<bool> {
    let Some(current_bundle) = app_bundle_path() else {
        return Ok(false);
    };
    let target_bundle = installed_app_target_path();
    if !target_bundle.exists() {
        return Ok(false);
    }

    let current_version = app_version_from_bundle(&current_bundle).or_else(current_app_version);
    let target_version = app_version_from_bundle(&target_bundle);
    if !should_handoff_to_installed_app(
        &current_bundle,
        &target_bundle,
        current_version.as_ref(),
        target_version.as_ref(),
    ) {
        return Ok(false);
    }

    Command::new("open")
        .arg("-na")
        .arg(&target_bundle)
        .stdout(Stdio::null())
        .stderr(Stdio::null())
        .spawn()
        .with_context(|| format!("handoff to installed app {}", target_bundle.display()))?;
    app.exit(0);
    Ok(true)
}

// helper runtime 新协议开关:=0 时生成端回退旧模板(两段 mv,定义即执行)。
// 仅排障/对照用;发布环境勿设。
fn helper_runtime_swap_enabled() -> bool {
    std::env::var("HOROSA_HELPER_RUNTIME_SWAP")
        .map(|v| v != "0")
        .unwrap_or(true)
}

// 新协议:只生成**函数定义**(不立即执行),由模板底部 run_runtime_installs 在
// wait_for_old_app_exit 与 install_app 之后统一调用。手术本体 = TARGET 新二进制的
// --horosa-runtime-swap → extract_runtime_archive_with 同一协议(renamex 原子互换 +
// previous 保留到首次 ready + 版本闸 + 磁盘预检);失败 return 1(绝不 exit 杀 helper),
// 失败臂由模板层处理:重开新 app + exit 73,不写完成标记(铁律14)。
// 非共享根成功后 chown 归还用户(admin 更新时 root 跑 helper,防 root-owned 锁死后续用户态更新)。
fn build_single_runtime_update_command(
    runtime_root: &Path,
    archive_path: &Path,
    runtime_version: Option<&str>,
    index: usize,
) -> String {
    format!(
        "install_runtime_{index}() {{\n  RUNTIME_ROOT={runtime_root}\n  if ! \"${{TARGET}}/Contents/MacOS/${{EXEC_NAME}}\" --horosa-runtime-swap \"${{RUNTIME_ROOT}}\" {archive} {runtime_version}; then\n    echo \"[runtime] swap failed for ${{RUNTIME_ROOT}}\"\n    return 1\n  fi\n  case \"${{RUNTIME_ROOT}}\" in\n    /Users/Shared/*) : ;;\n    *) /usr/sbin/chown -R \"${{USER_UID}}\" \"${{RUNTIME_ROOT}}\" >/dev/null 2>&1 || true ;;\n  esac\n  return 0\n}}\n",
        index = index,
        runtime_root = shell_quote(runtime_root),
        archive = shell_quote(archive_path),
        runtime_version = shell_quote_text(runtime_version.unwrap_or(""))
    )
}

// 旧协议原样保留(HOROSA_HELPER_RUNTIME_SWAP=0 的逃生阀)。已知病:两段 mv 非原子、
// 成功即删 previous(无回滚资本)、定义即执行(先于 wait_for_old_app_exit)、失败臂 exit 杀 helper。
// 仅作对照/排障,发布环境勿关新协议。
fn build_single_runtime_update_command_legacy(
    runtime_root: &Path,
    archive_path: &Path,
    runtime_version: Option<&str>,
    index: usize,
) -> String {
    format!(
        "install_runtime_{index}() {{\nRUNTIME_ROOT={runtime_root}\nWORK_ROOT=\"${{RUNTIME_ROOT}}/_update\"\nPREVIOUS_ROOT=\"${{RUNTIME_ROOT}}/previous\"\nEXPECTED_RUNTIME_VERSION={runtime_version}\nmkdir -p \"${{RUNTIME_ROOT}}\"\nrm -rf \"${{WORK_ROOT}}\"\nmkdir -p \"${{WORK_ROOT}}\"\nCOPYFILE_DISABLE=1 COPY_EXTENDED_ATTRIBUTES_DISABLE=1 /usr/bin/tar -xzf {archive} -C \"${{WORK_ROOT}}\"\nif [ ! -f \"${{WORK_ROOT}}/runtime-payload/runtime-manifest.json\" ]; then\n  echo \"runtime manifest missing after extract\" >&2\n  exit 1\nfi\nACTUAL_RUNTIME_VERSION=\"$(/usr/bin/plutil -extract version raw -o - \"${{WORK_ROOT}}/runtime-payload/runtime-manifest.json\" 2>/dev/null || true)\"\nif [ -n \"${{EXPECTED_RUNTIME_VERSION}}\" ] && [ \"${{ACTUAL_RUNTIME_VERSION}}\" != \"${{EXPECTED_RUNTIME_VERSION}}\" ]; then\n  echo \"runtime version mismatch: ${{ACTUAL_RUNTIME_VERSION}} != ${{EXPECTED_RUNTIME_VERSION}}\" >&2\n  exit 1\nfi\nrm -rf \"${{PREVIOUS_ROOT}}\"\nHAD_RUNTIME=0\nif [ -d \"${{RUNTIME_ROOT}}/current\" ]; then\n  mv \"${{RUNTIME_ROOT}}/current\" \"${{PREVIOUS_ROOT}}\"\n  HAD_RUNTIME=1\nfi\nif mv \"${{WORK_ROOT}}/runtime-payload\" \"${{RUNTIME_ROOT}}/current\"; then\n  rm -rf \"${{WORK_ROOT}}\" \"${{PREVIOUS_ROOT}}\"\n  /usr/bin/xattr -dr com.apple.quarantine \"${{RUNTIME_ROOT}}/current\" >/dev/null 2>&1 || true\n  case \"${{RUNTIME_ROOT}}\" in /Users/Shared/*) /bin/chmod -R a+rwX \"${{RUNTIME_ROOT}}/current\" >/dev/null 2>&1 || true ;; esac\nelse\n  rm -rf \"${{RUNTIME_ROOT}}/current\"\n  if [ \"${{HAD_RUNTIME}}\" = \"1\" ] && [ -d \"${{PREVIOUS_ROOT}}\" ]; then\n    mv \"${{PREVIOUS_ROOT}}\" \"${{RUNTIME_ROOT}}/current\"\n  fi\n  exit 1\nfi\n}}\ninstall_runtime_{index}\n",
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
    if runtime_roots.is_empty() {
        return String::new();
    }
    if !helper_runtime_swap_enabled() {
        return runtime_roots
            .iter()
            .enumerate()
            .map(|(index, root)| {
                build_single_runtime_update_command_legacy(
                    root,
                    archive_path,
                    runtime_version,
                    index,
                )
            })
            .collect::<Vec<_>>()
            .join("\n");
    }
    let defs = runtime_roots
        .iter()
        .enumerate()
        .map(|(index, root)| {
            build_single_runtime_update_command(root, archive_path, runtime_version, index)
        })
        .collect::<Vec<_>>()
        .join("\n");
    let calls = (0..runtime_roots.len())
        .map(|index| format!("  install_runtime_{index} || return 1"))
        .collect::<Vec<_>>()
        .join("\n");
    format!("{defs}\nrun_runtime_installs() {{\n{calls}\n  return 0\n}}\n")
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
        "#!/bin/bash\nset -euo pipefail\nLOG={log}\nMARKER={marker}\nTARGET={target}\nSRC={src}\nUSER_UID={user_uid}\nUSER_NAME={user_name}\nOLD_PID={old_pid}\nEXEC_NAME={exec_name}\nEXPECTED_VERSION={target_version}\nEXPECTED_RUNTIME_VERSION={runtime_version}\nAPP_DISPLAY_NAME=\"$(/usr/bin/basename \"${{TARGET}}\" .app)\"\nmkdir -p \"$(dirname \"${{LOG}}\")\"\nmkdir -p \"$(dirname \"${{MARKER}}\")\"\nexec >> \"${{LOG}}\" 2>&1\necho \"===== update helper start $(date '+%Y-%m-%d %H:%M:%S') =====\"\necho \"uid=$(/usr/bin/id -u) user=$(/usr/bin/id -un)\"\necho \"target=${{TARGET}}\"\necho \"src=${{SRC}}\"\nwait_for_old_app_exit() {{\n  if [ -z \"${{OLD_PID}}\" ] || [ \"${{OLD_PID}}\" = \"0\" ]; then\n    return 0\n  fi\n  for attempt in $(/usr/bin/seq 1 60); do\n    if ! /bin/kill -0 \"${{OLD_PID}}\" >/dev/null 2>&1; then\n      echo \"[app] old process exited\"\n      return 0\n    fi\n    sleep 1\n  done\n  echo \"[app] old process still running after wait window\"\n  return 0\n}}\nrun_runtime_installs() {{\n  return 0\n}}\n{runtime_cmd}mark_update_complete() {{\n  local relaunch_status=\"${{1:-pending_manual}}\"\n  MARKER_DIR=\"$(dirname \"${{MARKER}}\")\"\n  /bin/mkdir -p \"${{MARKER_DIR}}\"\n  /usr/sbin/chown \"${{USER_UID}}\" \"${{MARKER_DIR}}\" >/dev/null 2>&1 || true\n  /bin/cat > \"${{MARKER}}\" <<EOF\nversion=${{EXPECTED_VERSION}}\nruntime_version=${{EXPECTED_RUNTIME_VERSION}}\ninstalled_at=$(/bin/date '+%Y-%m-%d %H:%M:%S')\nrelaunch_status=${{relaunch_status}}\nEOF\n  /usr/sbin/chown \"${{USER_UID}}\" \"${{MARKER}}\" >/dev/null 2>&1 || true\n}}\nis_target_running() {{\n  if [ -z \"${{EXEC_NAME}}\" ]; then\n    return 1\n  fi\n  /usr/bin/pgrep -f \"${{TARGET}}/Contents/MacOS/${{EXEC_NAME}}\" >/dev/null 2>&1\n}}\nwait_for_stable_relaunch() {{\n  local appeared=0\n  for wait_step in $(/usr/bin/seq 1 25); do\n    if is_target_running; then\n      appeared=1\n      break\n    fi\n    sleep 1\n  done\n  if [ \"${{appeared}}\" != \"1\" ]; then\n    echo \"[open] process never appeared\"\n    return 1\n  fi\n  for stable_step in $(/usr/bin/seq 1 10); do\n    if ! is_target_running; then\n      echo \"[open] process exited before becoming stable\"\n      return 1\n    fi\n    sleep 1\n  done\n  return 0\n}}\nactivate_app_once() {{\n  if [ -z \"${{APP_DISPLAY_NAME}}\" ]; then\n    return 0\n  fi\n  if [ \"$(/usr/bin/id -u)\" = \"${{USER_UID}}\" ]; then\n    /usr/bin/osascript -e \"tell application \\\"${{APP_DISPLAY_NAME}}\\\" to activate\" >/dev/null 2>&1 || true\n    return 0\n  fi\n  /bin/launchctl asuser \"${{USER_UID}}\" /usr/bin/osascript -e \"tell application \\\"${{APP_DISPLAY_NAME}}\\\" to activate\" >/dev/null 2>&1 || true\n}}\nopen_app_once() {{\n  if [ \"$(/usr/bin/id -u)\" = \"${{USER_UID}}\" ]; then\n    /usr/bin/open -n \"${{TARGET}}\"\n    activate_app_once\n    return 0\n  fi\n  if /bin/launchctl asuser \"${{USER_UID}}\" /usr/bin/open -n \"${{TARGET}}\"; then\n    activate_app_once\n    return 0\n  fi\n  if /usr/bin/sudo -u \"${{USER_NAME}}\" /usr/bin/open -n \"${{TARGET}}\"; then\n    activate_app_once\n    return 0\n  fi\n  /usr/bin/open -n \"${{TARGET}}\"\n  activate_app_once\n}}\nopen_app() {{\n  for attempt in $(/usr/bin/seq 1 8); do\n    echo \"[open] attempt ${{attempt}}\"\n    open_app_once || true\n    if wait_for_stable_relaunch; then\n      activate_app_once\n      echo \"[open] relaunch confirmed\"\n      mark_update_complete \"auto_relaunch_confirmed\"\n      return 0\n    fi\n    sleep 2\n  done\n  echo \"[open] relaunch not confirmed after retries\"\n  return 1\n}}\ninstall_app() {{\n  BACKUP_TARGET=\"${{TARGET}}.previous\"\n  STAGE_TARGET=\"${{TARGET%.app}}.update-stage.app\"\n  SRC_KB=\"$(/usr/bin/du -sk \"${{SRC}}\" 2>/dev/null | /usr/bin/awk '{{print $1}}')\"\n  AVAIL_KB=\"$(/bin/df -k \"$(dirname \"${{TARGET}}\")\" 2>/dev/null | /usr/bin/awk 'NR==2 {{print $4}}')\"\n  if [ -n \"${{SRC_KB}}\" ] && [ -n \"${{AVAIL_KB}}\" ] && [ \"${{AVAIL_KB}}\" -lt $((SRC_KB * 2)) ]; then\n    echo \"[app] insufficient disk space: need ~$((SRC_KB * 2))KB, avail ${{AVAIL_KB}}KB\"\n    return 1\n  fi\n  rm -rf \"${{STAGE_TARGET}}\"\n  for attempt in $(/usr/bin/seq 1 45); do\n    echo \"[app] attempt ${{attempt}}\"\n    if [ ! -d \"${{STAGE_TARGET}}\" ]; then\n      if ! /usr/bin/ditto \"${{SRC}}\" \"${{STAGE_TARGET}}\"; then\n        echo \"[app] stage ditto failed on attempt ${{attempt}}\"\n        rm -rf \"${{STAGE_TARGET}}\"\n        sleep 1\n        continue\n      fi\n      /usr/bin/xattr -dr com.apple.quarantine \"${{STAGE_TARGET}}\" >/dev/null 2>&1 || true\n    fi\n    if [ -d \"${{TARGET}}\" ]; then\n      if \"${{STAGE_TARGET}}/Contents/MacOS/${{EXEC_NAME}}\" --horosa-atomic-swap \"${{STAGE_TARGET}}\" \"${{TARGET}}\" >/dev/null 2>&1; then\n        echo \"[app] atomic swap succeeded\"\n        rm -rf \"${{BACKUP_TARGET}}\"\n        mv \"${{STAGE_TARGET}}\" \"${{BACKUP_TARGET}}\" 2>/dev/null || rm -rf \"${{STAGE_TARGET}}\"\n        return 0\n      fi\n      echo \"[app] atomic swap unavailable, fallback to mv pair\"\n      rm -rf \"${{BACKUP_TARGET}}\"\n      if ! mv \"${{TARGET}}\" \"${{BACKUP_TARGET}}\"; then\n        echo \"[app] mv failed on attempt ${{attempt}}\"\n        /bin/ls -ld \"${{TARGET}}\" >/dev/null 2>&1 && /bin/ls -ld \"${{TARGET}}\"\n        sleep 1\n        continue\n      fi\n      if mv \"${{STAGE_TARGET}}\" \"${{TARGET}}\"; then\n        rm -rf \"${{BACKUP_TARGET}}\"\n        echo \"[app] install succeeded (mv fallback)\"\n        return 0\n      fi\n      echo \"[app] stage mv failed; restoring previous\"\n      if [ -d \"${{BACKUP_TARGET}}\" ]; then\n        mv \"${{BACKUP_TARGET}}\" \"${{TARGET}}\" || true\n      fi\n      sleep 1\n      continue\n    fi\n    if mv \"${{STAGE_TARGET}}\" \"${{TARGET}}\"; then\n      echo \"[app] install succeeded (fresh)\"\n      return 0\n    fi\n    echo \"[app] fresh mv failed on attempt ${{attempt}}\"\n    sleep 1\n  done\n  echo \"[app] install failed after retries\"\n  rm -rf \"${{STAGE_TARGET}}\"\n  return 1\n}}\nwait_for_old_app_exit\nif ! install_app; then\n  echo \"[app] install failed; reopening previous app\"\n  for reopen_attempt in $(/usr/bin/seq 1 3); do\n    open_app_once || true\n    if wait_for_stable_relaunch; then\n      echo \"[open] previous app reopened\"\n      break\n    fi\n  done\n  exit 71\nfi\nsleep 1\nif ! run_runtime_installs; then\n  echo \"[runtime] runtime install failed; reopening app without completion marker\"\n  for reopen_attempt in $(/usr/bin/seq 1 3); do\n    open_app_once || true\n    if wait_for_stable_relaunch; then\n      echo \"[open] app reopened after runtime failure\"\n      break\n    fi\n  done\n  exit 73\nfi\nmark_update_complete \"pending_manual\"\nif ! open_app; then\n  echo \"[open] automatic relaunch could not be confirmed; waiting for manual reopen\"\n  exit 72\nfi\necho \"===== update helper success $(date '+%Y-%m-%d %H:%M:%S') =====\"\n",
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
        UpdateSource::ManifestViaApi => "更新清单(经 GitHub Releases 取回)",
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
    // [U-H] 手动检查不受节流,但成功同样计入节流窗
    write_update_check_stamp(&app);
    let current = Version::parse(env!("CARGO_PKG_VERSION"))?;
    let local_runtime = local_runtime_version(&app);
    let runtime_needs_update =
        runtime_update_decision(&app, &plan, &local_runtime) == RuntimeUpdateDecision::Needed;
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

    // notify-only:manifest 与其 asset 双双不可得 → 无 sha 可校验,绝不进下载流。
    // 给用户「打开发布页」的手动出口(仍是 HTTPS + GitHub 账号信任根,与自动更新同源)。
    if plan.notify_only {
        append_update_history(
            &app,
            serde_json::json!({
                "event": "notify_only",
                "to": plan.latest_version.to_string(),
            }),
        );
        let open_page = MessageDialog::new()
            .set_level(MessageLevel::Warning)
            .set_title("发现可用更新（暂不能自动更新）")
            .set_description(format!(
                "{summary}\n\n更新清单暂时无法获取，为确保安装包完整性，已停止自动下载。\n可稍后重试，或现在打开发布页手动下载安装包。"
            ))
            .set_buttons(MessageButtons::OkCancelCustom(
                "打开发布页".to_string(),
                "稍后再说".to_string(),
            ))
            .show();
        if open_page == MessageDialogResult::Custom("打开发布页".to_string()) {
            let _ = Command::new("open")
                .arg(&plan.release_url)
                .stdout(Stdio::null())
                .stderr(Stdio::null())
                .spawn();
        }
        return Ok(());
    }

    let proceed = MessageDialog::new()
        .set_level(MessageLevel::Info)
        .set_title("发现可用更新")
        .set_description(format!(
            "{summary}{admin_update_notice}\n\n是否现在开始更新？选择“否”只会结束本次检查，不会开始下载。"
        ))
        .set_buttons(MessageButtons::YesNo)
        .show();
    if proceed != MessageDialogResult::Yes {
        if let Some(window) = app.get_webview_window(MAIN_WINDOW_LABEL) {
            emit_launcher_state(&window, &build_update_review_state());
            emit_mode(&window, "update");
            emit_status(&window, "你已暂缓本次更新，当前不会开始下载。");
            emit_progress(&window, 0, "本次更新已暂缓");
        }
        return Ok(());
    }

    // sha 守门无条件:任何来源(含 API 回退)缺 sha 都不下载安装。notify-only 已在上游短路。
    if plan.latest_version > current && plan.app_sha256.is_none() {
        return Err(anyhow!("更新清单缺少桌面包 sha256，已停止自动更新"));
    }
    if runtime_needs_update && plan.runtime_sha256.is_none() {
        return Err(anyhow!("更新清单缺少运行环境 sha256，已停止自动更新"));
    }

    let review_payload = build_asset_review_payload(
        &app,
        AssetReviewMode::Update,
        Some(plan.latest_version.clone()),
        plan.runtime_version.clone(),
    )?;
    let decisions = review_payload.default_selections.clone();
    let default_review_issues = validate_asset_review_payload(&app, &review_payload, &decisions)?;
    if !default_review_issues.is_empty() {
        return Err(anyhow!(
            "更新前检查发现默认替换方案仍有阻断问题：\n{}",
            default_review_issues.join("\n")
        ));
    }
    if let Some(window) = app.get_webview_window(MAIN_WINDOW_LABEL) {
        emit_launcher_state(&window, &build_update_in_progress_state());
        emit_mode(&window, "update");
        emit_progress(&window, 8, "检查更新");
        emit_status(
            &window,
            &format!(
                "已确认开始更新，接下来会按推荐方案检查并准备本次要替换的资产。{}",
                admin_update_notice
            ),
        );
        for line in clear_selected_assets_internal(&app, &decisions)? {
            emit_status(&window, &line);
        }
    } else {
        MessageDialog::new()
            .set_level(MessageLevel::Info)
            .set_title("更新即将开始")
            .set_description("当前没有主窗口可显示进度卡片，将按推荐选项继续下载、校验与替换。")
            .set_buttons(MessageButtons::Ok)
            .show();
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
            // 无主窗口分支:同走断点续传下载核(原为裸 io::copy,零重试零续传零原子性)。
            download_resumable_once(
                &plan.app_url,
                &zip_path,
                download_resume_enabled(),
                |_, _| {},
                |_| {},
            )?;
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
                    emit_ready_and_stabilize(
                        &app_handle,
                        &win,
                        &frontend_url(session.web_port, session.backend_port, session.chart_port),
                    );
                }
                Err(err) => {
                    emit_launcher_error(&win, &build_launcher_error_payload(&app_handle, &err))
                }
            },
        );
    }
    Ok(())
}

// ============================================================================
// v2.2.1 非阻塞软件内升级:JS 可调命令 + 独立进度事件通道。
// 复用既有 resolve_update_plan / 下载校验 / install_downloaded_app 核心,只把交互层
// 从原生阻塞 MessageDialog 换成主窗口内的非模态 UpdateNotifier(可最小化、可延后重启)。
// ============================================================================

#[derive(serde::Serialize)]
#[serde(rename_all = "camelCase")]
struct UpdateAvailability {
    available: bool,
    current_version: String,
    latest_version: String,
    runtime_needs_update: bool,
    notes: String,
    release_url: String,
    // 可视化 v2(全部 optional 语义:老前端忽略,新前端判空退化)
    update_mode: Option<String>,     // "incremental" | "full"
    download_bytes: Option<u64>,     // 预计下载量
    reuse_pct: Option<u8>,           // 增量复用率
    changed_components: Vec<String>, // 变化部件名
    // 无 sha 可校验(manifest 与其 asset 双双不可得)→ 只通知不安装
    notify_only: bool,
}

// [U-D 防降级] runtime 更新判定:单一真值函数,菜单/静默检查/后台下载/自动检查四处共用
// (此前三处内联手抄同一段判定,已全部收口——内联回潮由 preflight[101] 反向锚拦)。
// 语义:runtime_version_rank 单调比较,remote 更新才更;remote 更旧=DowngradeBlocked
// (不动作,防 latest 指针异常/回滚把用户静默降级);任一侧 rank 解析失败回退老「不同即更」
// 语义(防脏版本串永久卡死更新链);allow_downgrade(env HOROSA_ALLOW_DOWNGRADE=1 或
// manifest allowDowngrade,应急全网退版剧本见 INCREMENTAL_UPDATE_SOP §4.3)恢复老语义。
#[derive(Debug, Clone, Copy, PartialEq, Eq)]
enum RuntimeUpdateDecision {
    UpToDate,
    Needed,
    DowngradeBlocked,
}

fn compute_runtime_update_decision(
    remote: Option<&str>,
    local: Option<&str>,
    allow_downgrade: bool,
) -> RuntimeUpdateDecision {
    let (remote, local) = match (remote, local) {
        (Some(remote), Some(local)) => (remote.trim(), local.trim()),
        (Some(_), None) => return RuntimeUpdateDecision::Needed,
        _ => return RuntimeUpdateDecision::UpToDate,
    };
    if remote == local {
        return RuntimeUpdateDecision::UpToDate;
    }
    if allow_downgrade {
        return RuntimeUpdateDecision::Needed;
    }
    match (runtime_version_rank(remote), runtime_version_rank(local)) {
        (Some(remote_rank), Some(local_rank)) => match remote_rank.cmp(&local_rank) {
            std::cmp::Ordering::Greater => RuntimeUpdateDecision::Needed,
            std::cmp::Ordering::Equal => RuntimeUpdateDecision::UpToDate,
            std::cmp::Ordering::Less => RuntimeUpdateDecision::DowngradeBlocked,
        },
        // 任一侧解析失败 → 回退「不同即更」老语义(此分支 remote != local 已成立)
        _ => RuntimeUpdateDecision::Needed,
    }
}

fn allow_runtime_downgrade(plan: &UpdatePlan) -> bool {
    if plan.allow_downgrade {
        return true;
    }
    std::env::var("HOROSA_ALLOW_DOWNGRADE")
        .map(|value| value.trim() == "1")
        .unwrap_or(false)
}

// 带副作用的统一入口:DowngradeBlocked 时记账本;仅在 base 版本真更旧时发 UI 事件
// (GithubApi 回退源的合成 runtime 版本串与本地只差 -runtimeN 修订位时属「合成不确定」,
// 静默记账即可,不吓用户)。事件字段全 optional,老前端无钩子=无害。
fn runtime_update_decision(
    app: &AppHandle,
    plan: &UpdatePlan,
    local_runtime: &Option<String>,
) -> RuntimeUpdateDecision {
    let decision = compute_runtime_update_decision(
        plan.runtime_version.as_deref(),
        local_runtime.as_deref(),
        allow_runtime_downgrade(plan),
    );
    if decision == RuntimeUpdateDecision::DowngradeBlocked {
        ledger_mark(
            "rust.update_downgrade_blocked",
            Some(serde_json::json!({
                "remote": plan.runtime_version.clone(),
                "local": local_runtime.clone(),
            })),
        );
        // [U-G] 台账:降级拦截
        append_update_history(
            app,
            serde_json::json!({
                "event": "downgrade_blocked",
                "remote": plan.runtime_version.clone(),
                "local": local_runtime.clone(),
            }),
        );
        let base_truly_older = match (
            plan.runtime_version
                .as_deref()
                .and_then(runtime_version_rank),
            local_runtime.as_deref().and_then(runtime_version_rank),
        ) {
            (Some(remote_rank), Some(local_rank)) => remote_rank.0 < local_rank.0,
            _ => false,
        };
        if base_truly_older {
            emit_update_event(
                app,
                &serde_json::json!({
                    "phase": "downgrade-blocked",
                    "remoteRuntime": plan.runtime_version.clone(),
                    "localRuntime": local_runtime.clone(),
                    "message": "线上运行环境版本低于本机，已按防降级策略跳过（如确需回退请使用离线安装包重装）。",
                })
                .to_string(),
            );
        }
    }
    decision
}

// [U-C staged 持久化] 后台下载校验完成的更新落盘 staged-update.json;下次启动
// (run_auto_update_check 开头)逐资产重验 sha + 与线上 latest 核对后直接恢复
// 「已就绪」——保守复用策略:manifest 必须可达且 target==线上 latest 才复用
// (无签名信任模型下「线上撤版」唯一挡板就是最新性核对);拉取失败留档下次再验。
const STAGED_UPDATE_MAX_AGE_MS: u64 = 7 * 24 * 3600 * 1000;

#[derive(Serialize, Deserialize)]
struct PersistedStagedUpdate {
    #[serde(default)]
    saved_at_ms: u64,
    staged: StagedUpdate,
    // 各资产落盘时自算 sha(不抄 manifest——GithubApi 源 app_sha256=None 也能护)
    #[serde(default)]
    asset_shas: Vec<PersistedAssetSha>,
}

#[derive(Serialize, Deserialize)]
struct PersistedAssetSha {
    path: PathBuf,
    sha256: String,
}

fn staged_update_file_path(app: &AppHandle) -> Option<PathBuf> {
    app.path()
        .app_data_dir()
        .ok()
        .map(|d| d.join("staged-update.json"))
}

fn staged_update_asset_paths(staged: &StagedUpdate) -> Vec<PathBuf> {
    let mut paths = Vec::new();
    if let Some(p) = &staged.zip_path {
        paths.push(p.clone());
    }
    if let Some(p) = &staged.runtime_archive_path {
        paths.push(p.clone());
    }
    if let Some(c) = &staged.staged_components {
        for (_, p) in &c.archives {
            paths.push(p.clone());
        }
    }
    paths
}

fn persist_staged_update_file_at(path: &Path, staged: &StagedUpdate) -> Result<()> {
    let mut asset_shas = Vec::new();
    for asset in staged_update_asset_paths(staged) {
        let sha = sha256_digest(&asset)?;
        asset_shas.push(PersistedAssetSha {
            path: asset,
            sha256: sha,
        });
    }
    let saved_at_ms = SystemTime::now()
        .duration_since(UNIX_EPOCH)
        .map(|d| d.as_millis() as u64)
        .unwrap_or(0);
    let payload = PersistedStagedUpdate {
        saved_at_ms,
        staged: staged.clone(),
        asset_shas,
    };
    fs::write(path, serde_json::to_string(&payload)?)?;
    Ok(())
}

fn persist_staged_update_file(app: &AppHandle, staged: &StagedUpdate) {
    if let Some(path) = staged_update_file_path(app) {
        if let Err(err) = persist_staged_update_file_at(&path, staged) {
            eprintln!("[updater] staged 持久化失败(不影响本次流程): {err:#}");
            let _ = fs::remove_file(&path);
        }
    }
}

// 读档:过期(>7 天)/坏 JSON/任一资产 sha 不符 → None(调用方删档;资产文件保留,
// 后续正常流按需续传/重下,安全自愈)。
fn load_staged_update_file_at(path: &Path, now_ms: u64) -> Option<StagedUpdate> {
    let data = fs::read_to_string(path).ok()?;
    let parsed: PersistedStagedUpdate = serde_json::from_str(&data).ok()?;
    if now_ms.saturating_sub(parsed.saved_at_ms) > STAGED_UPDATE_MAX_AGE_MS {
        return None;
    }
    if parsed.asset_shas.is_empty() {
        return None;
    }
    for item in &parsed.asset_shas {
        match sha256_digest(&item.path) {
            Ok(sha) if sha.eq_ignore_ascii_case(&item.sha256) => {}
            _ => return None,
        }
    }
    Some(parsed.staged)
}

fn clear_staged_update_file(app: &AppHandle) {
    if let Some(path) = staged_update_file_path(app) {
        let _ = fs::remove_file(&path);
    }
}

// 复用门(纯函数可测):暂存目标必须与线上 latest 完全一致(app 版本 + runtime 版本)
fn staged_matches_plan(
    staged: &StagedUpdate,
    latest: &str,
    runtime_version: &Option<String>,
) -> bool {
    staged.target_version == latest && staged.runtime_version == *runtime_version
}

// [U-C] 清已消费的部件归档+lock 临时档(部件档只进不出会漏磁盘;全量 runtime/app
// 归档有意保留=离线修复资本,不清)。
fn cleanup_consumed_component_archives(staged: &StagedUpdate) {
    if let Some(components) = &staged.staged_components {
        let mut cache_dir: Option<PathBuf> = None;
        for (_, path) in &components.archives {
            if cache_dir.is_none() {
                cache_dir = path.parent().map(|p| p.to_path_buf());
            }
            let _ = fs::remove_file(path);
        }
        if let Some(dir) = cache_dir {
            let _ = fs::remove_file(dir.join("components-lock.update.json"));
        }
    }
}

// [U-H 周期检查+节流] 自动检查:启动首查距上次成功检查 <4h 跳过;驻留线程每 24h
// 再查;检查失败不再静默(账本+check-failed 低打扰事件)。手动检查(菜单/前端)不受
// 节流但成功同样写 stamp。dev/e2e 覆盖:HOROSA_UPDATE_CHECK_INTERVAL_SECS(同时作
// 节流下限与周期,秒)。
const AUTO_CHECK_MIN_INTERVAL_SECS: u64 = 4 * 3600;
const AUTO_CHECK_CYCLE_SECS: u64 = 24 * 3600;

fn auto_check_interval_override() -> Option<u64> {
    std::env::var("HOROSA_UPDATE_CHECK_INTERVAL_SECS")
        .ok()
        .and_then(|v| v.trim().parse::<u64>().ok())
        .filter(|v| *v > 0)
}

fn auto_update_check_cycle() -> Duration {
    Duration::from_secs(auto_check_interval_override().unwrap_or(AUTO_CHECK_CYCLE_SECS))
}

fn update_check_stamp_path(app: &AppHandle) -> Option<PathBuf> {
    app.path()
        .app_data_dir()
        .ok()
        .map(|d| d.join("last-update-check.json"))
}

fn load_update_check_stamp(path: &Path) -> Option<u64> {
    let data = fs::read_to_string(path).ok()?;
    let json: serde_json::Value = serde_json::from_str(&data).ok()?;
    json.get("lastCheckMs").and_then(|v| v.as_u64())
}

fn write_update_check_stamp_at(path: &Path) {
    let now_ms = SystemTime::now()
        .duration_since(UNIX_EPOCH)
        .map(|d| d.as_millis() as u64)
        .unwrap_or(0);
    let _ = fs::write(
        path,
        serde_json::json!({ "lastCheckMs": now_ms }).to_string(),
    );
}

fn write_update_check_stamp(app: &AppHandle) {
    if let Some(path) = update_check_stamp_path(app) {
        write_update_check_stamp_at(&path);
    }
}

// 纯函数:是否该发起本轮自动检查(interval 由调用方合成 env 覆盖,测试不碰环境)
fn should_run_auto_check(last_ms: Option<u64>, now_ms: u64, min_interval_ms: u64) -> bool {
    match last_ms {
        None => true,
        Some(last) => now_ms.saturating_sub(last) >= min_interval_ms,
    }
}

// 检查失败不再静默:账本+低打扰事件(老前端无此 phase 钩子=无害;新前端 toast 单显)
fn note_auto_check_failure(app: &AppHandle, err: &anyhow::Error) {
    eprintln!("[updater] auto check failed: {err:#}");
    ledger_mark(
        "rust.update_check_failed",
        Some(serde_json::json!({ "error": format!("{err:#}") })),
    );
    // [U-G] 台账:检查失败(耐久留痕,排障可回看「源不可达从何时开始」)
    append_update_history(
        app,
        serde_json::json!({ "event": "check_failed", "error": format!("{err:#}") }),
    );
    emit_update_event(
        app,
        &serde_json::json!({
            "phase": "check-failed",
            "message": "更新检查未完成（网络或更新源暂不可达），稍后会自动重试；也可在菜单「检查更新」手动检查。",
        })
        .to_string(),
    );
}

// [U-H] 自动检查本体(原启动一次性线程体抽出,供 启动首查/24h 周期共用;
// U-C staged 断点恢复挂接于此)。
fn run_auto_update_check(app: &AppHandle) {
    let now_ms = SystemTime::now()
        .duration_since(UNIX_EPOCH)
        .map(|d| d.as_millis() as u64)
        .unwrap_or(0);
    // [U-C] 先看有无上次「已下载完成未安装」的暂存档(过期/坏档/资产被动即删)
    let staged_file = staged_update_file_path(app);
    let staged_candidate = staged_file.as_deref().and_then(|path| {
        if !path.exists() {
            return None;
        }
        let loaded = load_staged_update_file_at(path, now_ms);
        if loaded.is_none() {
            let _ = fs::remove_file(path);
        }
        loaded
    });
    // 节流:staged 在场=有待恢复成果,值得发起 manifest 核对 → 绕过
    if staged_candidate.is_none() {
        let min_interval_ms = auto_check_interval_override()
            .map(|s| s.saturating_mul(1000))
            .unwrap_or(AUTO_CHECK_MIN_INTERVAL_SECS * 1000);
        let last_ms = update_check_stamp_path(app)
            .as_deref()
            .and_then(load_update_check_stamp);
        if !should_run_auto_check(last_ms, now_ms, min_interval_ms) {
            ledger_mark(
                "rust.update_check_throttled",
                Some(serde_json::json!({ "lastCheckMs": last_ms })),
            );
            return;
        }
    }
    let client = match build_github_client(90) {
        Ok(c) => c,
        Err(err) => {
            // manifest 不可达:staged 留档下次再验(不复用不删除)
            note_auto_check_failure(app, &err);
            return;
        }
    };
    let plan = match resolve_update_plan(&client, app) {
        Ok(p) => p,
        Err(err) => {
            note_auto_check_failure(app, &err);
            return;
        }
    };
    write_update_check_stamp(app);
    let current = match Version::parse(env!("CARGO_PKG_VERSION")) {
        Ok(v) => v,
        Err(_) => return,
    };
    let local_runtime = local_runtime_version(app);
    let runtime_needs_update =
        runtime_update_decision(app, &plan, &local_runtime) == RuntimeUpdateDecision::Needed;
    let update_due = plan.latest_version > current || runtime_needs_update;
    if let Some(staged) = staged_candidate {
        if update_due
            && staged_matches_plan(
                &staged,
                &plan.latest_version.to_string(),
                &plan.runtime_version,
            )
        {
            // [U-C] 复用:回填内存槽 + 直接 ready(零重下)
            ledger_mark(
                "rust.staged_update_restored",
                Some(serde_json::json!({ "target": staged.target_version })),
            );
            let ready = serde_json::json!({
                "phase": "ready",
                "pct": 100,
                "version": staged.target_version,
                "message": "更新此前已下载完成，可随时重启更新",
            });
            if let Some(state) = app.try_state::<AppState>() {
                if let Ok(mut slot) = state.staged_update.lock() {
                    *slot = Some(staged);
                }
            }
            emit_update_event(app, &ready.to_string());
            return;
        }
        // 线上已推进/撤版/本机已装到位:废弃暂存档走正常流
        if let Some(path) = staged_file.as_deref() {
            let _ = fs::remove_file(path);
        }
    }
    if !update_due {
        // 无更新:静默
        return;
    }
    // 发现新版:非阻塞——只向主窗口 emit update-available 事件,由前端 UpdateNotifier
    // 显示右下角非模态卡片,用户自行选择下载/稍后;下载在后台、可最小化。
    let mut payload = serde_json::json!({
        "phase": "available",
        "currentVersion": current.to_string(),
        "latestVersion": plan.latest_version.to_string(),
        "runtimeNeedsUpdate": runtime_needs_update,
        "notes": summarize_update_notes(&plan.notes),
        "releaseUrl": plan.release_url.clone(),
    });
    // notify-only:无 sha 不自动下载。卡片带 notifyOnly 标记,前端把「下载」换「查看发布页」。
    // 老前端不认该字段 → 仍显示「下载」,点了会走 run_background_update_download 的 notify-only
    // 短路(发 notify-only 事件+不触网),故新旧前端皆安全。
    if plan.notify_only {
        payload["notifyOnly"] = serde_json::json!(true);
        payload["message"] = serde_json::json!(
            "检测到新版本，但更新清单暂不可获取，已暂停自动下载。可稍后重试，或到发布页手动下载安装包。"
        );
        emit_update_event(app, &payload.to_string());
        return;
    }
    // 可视化 v2:available 卡即显示「本次需下载约 XX MB(增量,复用 YY%)」
    let estimate = compute_update_estimate(&plan, plan.latest_version > current);
    payload["mode"] = serde_json::json!(estimate.mode);
    if let Some(bytes) = estimate.need_bytes {
        payload["downloadBytes"] = serde_json::json!(bytes);
    }
    if let Some(pct) = estimate.reuse_pct {
        payload["reusePct"] = serde_json::json!(pct);
    }
    emit_update_event(app, &payload.to_string());
}

#[tauri::command]
fn update_check_silent(app: AppHandle) -> std::result::Result<UpdateAvailability, String> {
    (|| -> Result<UpdateAvailability> {
        let client = build_github_client(90)?;
        let plan = resolve_update_plan(&client, &app)?;
        // [U-H] 前端手动检查同样计入节流窗
        write_update_check_stamp(&app);
        let current = Version::parse(env!("CARGO_PKG_VERSION"))?;
        let local_runtime = local_runtime_version(&app);
        let runtime_needs_update =
            runtime_update_decision(&app, &plan, &local_runtime) == RuntimeUpdateDecision::Needed;
        let available = plan.latest_version > current || runtime_needs_update;
        // 可视化 v2:检查阶段即算「本次需下载多大(增量/全量,复用率)」——display-only,
        // 真实下载路径届时自行重判(estimate 与实际有差时以实际为准)。
        // notify-only 无资产 URL/尺寸,估算无意义。
        let estimate = if available && !plan.notify_only {
            Some(compute_update_estimate(
                &plan,
                plan.latest_version > current,
            ))
        } else {
            None
        };
        Ok(UpdateAvailability {
            available,
            current_version: current.to_string(),
            latest_version: plan.latest_version.to_string(),
            runtime_needs_update,
            notes: summarize_update_notes(&plan.notes),
            release_url: plan.release_url.clone(),
            update_mode: estimate.as_ref().map(|e| e.mode.to_string()),
            download_bytes: estimate.as_ref().and_then(|e| e.need_bytes),
            reuse_pct: estimate.as_ref().and_then(|e| e.reuse_pct),
            changed_components: estimate.map(|e| e.changed_names).unwrap_or_default(),
            notify_only: plan.notify_only,
        })
    })()
    .map_err(|e| format!("{e:#}"))
}

fn download_update_asset_once(
    app: &AppHandle,
    url: &str,
    dest: &Path,
    start_pct: u8,
    end_pct: u8,
    label: &str,
) -> Result<()> {
    // update 事件通道薄壳:下载/续传逻辑在 download_resumable_once,这里只负责事件格式。
    let mut last_pct = start_pct;
    download_resumable_once(
        url,
        dest,
        download_resume_enabled(),
        |resumed_from, _total| {
            if resumed_from > 0 {
                // 续传补入的既有字节计入账本进度(不进速度滑窗);事件带 resumedFrom(可选字段)。
                update_ledger_note_resumed(resumed_from);
                emit_update_event(
                    app,
                    &serde_json::json!({
                        "phase": "downloading",
                        "pct": start_pct,
                        "message": format!("{}(断点续传,从 {} MB 处继续)", label, resumed_from / 1_048_576),
                        "resumedFrom": resumed_from,
                    })
                    .to_string(),
                );
            } else {
                emit_update_event(
                    app,
                    &serde_json::json!({"phase":"downloading","pct":start_pct,"message":label})
                        .to_string(),
                );
            }
        },
        |chunk| {
            let pct = if chunk.total > 0 {
                let ratio = chunk.downloaded as f64 / chunk.total as f64;
                let span = end_pct.saturating_sub(start_pct) as f64;
                (start_pct as f64 + span * ratio).round() as u8
            } else {
                last_pct
            };
            // v2 字节账本:速度/ETA/全局字节/部件三元组合并进事件(账本自带 200ms 节流);
            // v2 关闭或无账本时退回老「pct 变化才发」路径,行为与现状一致。
            if let Some(fields) = update_ledger_chunk_fields(chunk.delta) {
                last_pct = pct;
                let mut event = serde_json::json!({
                    "phase": "downloading",
                    "pct": pct,
                    "message": label,
                });
                if let (Some(event_obj), Some(field_obj)) =
                    (event.as_object_mut(), fields.as_object())
                {
                    for (k, v) in field_obj {
                        event_obj.insert(k.clone(), v.clone());
                    }
                }
                emit_update_event(app, &event.to_string());
            } else if chunk.total > 0 && pct != last_pct && !progress_v2_enabled() {
                last_pct = pct;
                emit_update_event(
                    app,
                    &serde_json::json!({"phase":"downloading","pct":pct,"message":label})
                        .to_string(),
                );
            }
        },
    )?;
    update_ledger_finish_asset();
    emit_update_event(
        app,
        &serde_json::json!({"phase":"downloading","pct":end_pct,"message":label}).to_string(),
    );
    Ok(())
}

fn download_update_asset(
    app: &AppHandle,
    url: &str,
    dest: &Path,
    start_pct: u8,
    end_pct: u8,
    label: &str,
) -> Result<()> {
    let mut last_err = None;
    for attempt in 1..=DOWNLOAD_MAX_ATTEMPTS {
        if attempt > 1 {
            emit_update_event(
                app,
                &serde_json::json!({
                    "phase": "downloading",
                    "pct": start_pct,
                    "message": format!("{} 失败,正在重试({}/{})…", label, attempt, DOWNLOAD_MAX_ATTEMPTS),
                })
                .to_string(),
            );
            thread::sleep(Duration::from_secs((attempt as u64 - 1) * 2));
        }
        match download_update_asset_once(app, url, dest, start_pct, end_pct, label) {
            Ok(()) => return Ok(()),
            Err(err) => {
                last_err = Some(err);
                // 半成品在 dest.part(下载核管理),保留供下一轮续传;dest 只在 rename 后出现。
                // 账本清当前资产字节:续传 attempt 会经 note_resumed 重新补入,口径自洽。
                update_ledger_reset_current();
            }
        }
    }
    Err(wrap_download_error(
        label,
        url,
        last_err.unwrap_or_else(|| anyhow!("download failed without error detail")),
    ))
}

fn run_background_update_download(app: &AppHandle) -> Result<()> {
    emit_update_event(
        app,
        &serde_json::json!({"phase":"checking","pct":2,"message":"正在检查更新…"}).to_string(),
    );
    let client = build_github_client(90)?;
    let plan = resolve_update_plan(&client, app)?;
    let current = Version::parse(env!("CARGO_PKG_VERSION"))?;
    let local_runtime = local_runtime_version(app);
    let runtime_needs_update =
        runtime_update_decision(app, &plan, &local_runtime) == RuntimeUpdateDecision::Needed;

    if plan.latest_version <= current && !runtime_needs_update {
        emit_update_event(
            app,
            &serde_json::json!({"phase":"uptodate","message":"已是最新版本"}).to_string(),
        );
        return Ok(());
    }
    // notify-only 短路:无 sha 可校验 → 绝不触网下载。给用户友好出口(发布页)而非报错。
    if plan.notify_only {
        append_update_history(
            app,
            serde_json::json!({
                "event": "notify_only",
                "to": plan.latest_version.to_string(),
            }),
        );
        emit_update_event(
            app,
            &serde_json::json!({
                "phase": "notify-only",
                "message": "检测到新版本，但更新清单暂不可获取，已暂停自动下载。可稍后重试，或到发布页手动下载安装包。",
                "latestVersion": plan.latest_version.to_string(),
                "releaseUrl": plan.release_url.clone(),
            })
            .to_string(),
        );
        return Ok(());
    }
    // sha 守门无条件:任何来源(含 API 回退)缺 sha 都不下载安装。notify-only 已在上游短路。
    if plan.latest_version > current && plan.app_sha256.is_none() {
        return Err(anyhow!("更新清单缺少桌面包 sha256,已停止自动更新"));
    }
    if runtime_needs_update && plan.runtime_sha256.is_none() {
        return Err(anyhow!("更新清单缺少运行环境 sha256,已停止自动更新"));
    }

    let review_payload = build_asset_review_payload(
        app,
        AssetReviewMode::Update,
        Some(plan.latest_version.clone()),
        plan.runtime_version.clone(),
    )?;
    let decisions = review_payload.default_selections.clone();
    let issues = validate_asset_review_payload(app, &review_payload, &decisions)?;
    if !issues.is_empty() {
        return Err(anyhow!("更新前检查发现阻断问题:\n{}", issues.join("\n")));
    }
    let app_should_update = plan.latest_version > current
        && decision_for_kind(&decisions, DetectedAssetKind::InstalledApp) == AssetDecision::Replace;
    let runtime_roots = if runtime_needs_update {
        selected_runtime_roots(app, &decisions)?
    } else {
        Vec::new()
    };
    let runtime_should_update = runtime_needs_update && !runtime_roots.is_empty();
    if !app_should_update && !runtime_should_update {
        emit_update_event(
            app,
            &serde_json::json!({"phase":"uptodate","message":"没有需要替换的资产"}).to_string(),
        );
        return Ok(());
    }

    let config = load_release_config(app)?;
    // 可视化 v2:先发 planning(预计体积/增量复用率/变化部件),再建全局字节账本。
    let estimate = compute_update_estimate(&plan, app_should_update);
    update_ledger_init(estimate.mode, estimate.need_bytes.unwrap_or(0));
    {
        let size_text = match estimate.need_bytes {
            Some(bytes) => format!("约 {} MB", bytes / 1_048_576),
            None => "大小待定".to_string(),
        };
        let mode_text = if estimate.mode == "incremental" {
            match estimate.reuse_pct {
                Some(pct) => format!("增量更新,复用 {}%", pct),
                None => "增量更新".to_string(),
            }
        } else {
            "完整更新".to_string()
        };
        let mut planning = serde_json::json!({
            "phase": "planning",
            "pct": 8,
            "message": format!("本次需下载 {}({})", size_text, mode_text),
            "mode": estimate.mode,
        });
        if let Some(bytes) = estimate.need_bytes {
            planning["totalBytes"] = serde_json::json!(bytes);
        }
        if let Some(pct) = estimate.reuse_pct {
            planning["reusePct"] = serde_json::json!(pct);
        }
        if !estimate.changed_names.is_empty() {
            planning["changedComponents"] = serde_json::json!(estimate.changed_names);
        }
        emit_update_event(app, &planning.to_string());
    }
    let zip_path = cached_app_update_path(app, &config)?;
    if app_should_update {
        update_ledger_begin_asset("app", 0, 0);
        download_update_asset(app, &plan.app_url, &zip_path, 10, 55, "下载桌面更新包")?;
        verify_sha256(&zip_path, plan.app_sha256.as_deref(), "桌面更新包")?;
    }
    let mut runtime_archive_path = None;
    let mut staged_components = None;
    if runtime_should_update {
        let start = if app_should_update { 58 } else { 12 };
        // 增量优先:manifest v2 + 本地部件清单在位时只下载 sha 变化的部件;
        // 任何一步失败只降级回全量下载,不失败整个更新。
        if let Some(changed) = plan_component_diff(&plan, &runtime_roots) {
            let full_mb = plan
                .components
                .as_ref()
                .map(|cs| cs.iter().filter_map(|c| c.size).sum::<u64>() / 1_048_576)
                .unwrap_or(0);
            let need_mb = changed.iter().filter_map(|c| c.size).sum::<u64>() / 1_048_576;
            emit_update_event(
                app,
                &serde_json::json!({
                    "phase": "downloading",
                    "pct": start,
                    "message": format!(
                        "增量更新:仅需下载 {} 个组件(约 {}MB,全量 {}MB)",
                        changed.len(), need_mb, full_mb
                    ),
                })
                .to_string(),
            );
            match download_component_updates(app, &plan, &config, &changed, start, 92) {
                Ok(staged) => staged_components = Some(staged),
                Err(err) => {
                    eprintln!("component update download failed, fallback to full: {err:#}");
                    // 可视化 v2:增量降级全量——账本改按全量口径重记(mode=full,总量=已下+全量运行时)。
                    update_ledger_reset_current();
                    if let Ok(mut slot) = UPDATE_LEDGER.lock() {
                        if let Some(ledger) = slot.as_mut() {
                            ledger.mode = "full".to_string();
                            ledger.total_bytes = match plan.runtime_size_bytes {
                                Some(bytes) => ledger.completed_bytes + bytes,
                                None => 0,
                            };
                            ledger.component_name.clear();
                            ledger.component_index = 0;
                            ledger.component_total = 0;
                        }
                    }
                    emit_update_event(
                        app,
                        &serde_json::json!({
                            "phase": "downloading",
                            "pct": start,
                            "mode": "full",
                            "message": "增量组件获取失败,改为下载完整本机组件…",
                        })
                        .to_string(),
                    );
                }
            }
        }
        if staged_components.is_none() {
            if let Some(runtime_url) = plan.runtime_url.as_ref() {
                let rp = cached_runtime_archive_path(app, &config)?;
                update_ledger_begin_asset("runtime", 0, 0);
                download_update_asset(app, runtime_url, &rp, start, 92, "下载本机组件更新")?;
                verify_sha256(&rp, plan.runtime_sha256.as_deref(), "运行环境更新包")?;
                runtime_archive_path = Some(rp);
            }
        }
    }

    let staged = StagedUpdate {
        zip_path: if app_should_update {
            Some(zip_path)
        } else {
            None
        },
        runtime_archive_path,
        runtime_roots,
        runtime_version: plan.runtime_version.clone(),
        target_version: plan.latest_version.to_string(),
        app_should_update,
        runtime_should_update,
        staged_components,
    };
    // [U-C] 落盘持久化:进程被杀/用户退出后,已下载校验的成果下次启动直接恢复(免重下)
    persist_staged_update_file(app, &staged);
    // [U-G] 台账:下载校验完成(耐久行,进程死也留痕)
    append_update_history(
        app,
        serde_json::json!({
            "event": "staged_ready",
            "from": env!("CARGO_PKG_VERSION"),
            "to": staged.target_version,
            "runtimeVersion": staged.runtime_version,
        }),
    );
    if let Some(state) = app.try_state::<AppState>() {
        if let Ok(mut slot) = state.staged_update.lock() {
            *slot = Some(staged);
        }
    }
    // ready 事件带模式与实际下载量(可视化 v2),随后清账。
    let mut ready = serde_json::json!({
        "phase": "ready",
        "pct": 100,
        "message": "更新已下载完成,可随时重启更新",
        "version": plan.latest_version.to_string(),
    });
    if let Some((mode, downloaded)) = update_ledger_summary() {
        ready["mode"] = serde_json::json!(mode);
        ready["downloadedBytes"] = serde_json::json!(downloaded);
        let mb = downloaded / 1_048_576;
        ready["message"] = serde_json::json!(format!(
            "更新已下载完成(本次共下载 {} MB,{}),可随时重启更新",
            mb,
            if mode == "incremental" {
                "增量"
            } else {
                "完整"
            }
        ));
    }
    update_ledger_clear();
    emit_update_event(app, &ready.to_string());
    Ok(())
}

#[tauri::command]
fn update_start_background(app: AppHandle) -> std::result::Result<(), String> {
    thread::spawn(move || {
        if let Err(err) = run_background_update_download(&app) {
            update_ledger_clear();
            // [U-G] 台账:下载失败
            append_update_history(
                &app,
                serde_json::json!({ "event": "download_error", "error": format!("{err:#}") }),
            );
            emit_update_event(
                &app,
                &serde_json::json!({"phase":"error","message":format!("{err:#}")}).to_string(),
            );
        }
    });
    Ok(())
}

fn run_staged_install(app: &AppHandle) -> Result<()> {
    // 更新安装会主动停服/对换 runtime:挂 busy 守卫让探活看门狗静默。
    let _install_busy = BootstrapBusyGuard::hold();
    let staged = {
        let state = app.try_state::<AppState>().context("应用状态不可用")?;
        let slot = state
            .staged_update
            .lock()
            .map_err(|_| anyhow!("更新暂存锁异常"))?;
        slot.clone().context("没有已下载完成的更新,请先下载")?
    };
    // [U-G] 台账:开始应用
    append_update_history(
        app,
        serde_json::json!({
            "event": "apply_begin",
            "to": staged.target_version,
            "mode": if staged.staged_components.is_some() { "incremental" } else { "full" },
        }),
    );
    if staged.app_should_update {
        let zip = staged
            .zip_path
            .as_deref()
            .context("已下载的桌面包丢失,请重新下载")?;
        // 增量部件:进程存活期先完成 runtime 手术(Rust 全逻辑 + 原子对换),
        // 之后 helper 脚本只负责替换 .app(runtime_archive 传 None)。
        if staged.runtime_should_update {
            if let Some(components) = staged.staged_components.as_ref() {
                cleanup_state(app);
                let roots_total = staged.runtime_roots.len();
                for (idx, root) in staged.runtime_roots.iter().enumerate() {
                    let notify = make_applying_notifier(app, idx + 1, roots_total);
                    apply_component_updates_with(root, components, Some(&notify))
                        .with_context(|| format!("增量应用本机组件到 {}", root.display()))?;
                }
            }
        }
        // [U-C] 增量手术已成:清已消费部件档;交 helper 前消费暂存档(helper 接管即
        // 不可回头;此后 kill 由 helper 自身重试/回滚兜底,不再走 staged 恢复)。
        cleanup_consumed_component_archives(&staged);
        clear_staged_update_file(app);
        // [U-G] 台账:交接 helper(结果由 install_confirmed 闭环)
        append_update_history(
            app,
            serde_json::json!({
                "event": "helper_handoff",
                "to": staged.target_version,
                "helperProtocol": if helper_runtime_swap_enabled() { "runtime-swap-v2" } else { "legacy" },
            }),
        );
        // 应用包安装会替换 + 重启(install_downloaded_app 内部 app.exit),全量 runtime 随同处理。
        install_downloaded_app(
            app.clone(),
            zip,
            staged.runtime_archive_path.as_deref(),
            &staged.runtime_roots,
            staged.runtime_version.as_deref(),
            &staged.target_version,
        )?;
        return Ok(());
    }
    if staged.runtime_should_update {
        let window = app
            .get_webview_window(MAIN_WINDOW_LABEL)
            .context("缺少主窗口,无法完成本机组件更新")?;
        cleanup_state(app);
        if let Some(components) = staged.staged_components.as_ref() {
            let roots_total = staged.runtime_roots.len();
            for (idx, root) in staged.runtime_roots.iter().enumerate() {
                let notify = make_applying_notifier(app, idx + 1, roots_total);
                apply_component_updates_with(root, components, Some(&notify))
                    .with_context(|| format!("增量应用本机组件到 {}", root.display()))?;
            }
        } else {
            let runtime_archive = staged
                .runtime_archive_path
                .as_deref()
                .context("已下载的本机组件包丢失,请重新下载")?;
            let roots_total = staged.runtime_roots.len();
            for (idx, root) in staged.runtime_roots.iter().enumerate() {
                ensure_dir(root)?;
                let notify = make_applying_notifier(app, idx + 1, roots_total);
                let on_extract = |read: u64, total: u64, files: u64| {
                    if total == 0 {
                        return;
                    }
                    notify(&format!(
                        "展开完整运行时 {}% · {} 个文件",
                        ((read as f64 / total as f64) * 100.0).min(100.0).round() as u32,
                        files
                    ));
                };
                extract_runtime_archive_with(runtime_archive, root, Some(&on_extract), None)?;
                clear_runtime_pending_marker(&root.join("current"))?;
            }
        }
        // [U-C] 全部 root 应用成功:清已消费部件档+暂存档(失败路径 ? 早退不清,重试免重下)
        cleanup_consumed_component_archives(&staged);
        clear_staged_update_file(app);
        // [U-G] 台账:runtime 更新应用成功(app 不换壳路径的结果行)
        append_update_history(
            app,
            serde_json::json!({
                "event": "apply_runtime_ok",
                "runtimeVersion": staged.runtime_version,
            }),
        );
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
                    emit_ready_and_stabilize(
                        &app_handle,
                        &win,
                        &frontend_url(session.web_port, session.backend_port, session.chart_port),
                    );
                }
                Err(err) => {
                    emit_launcher_error(&win, &build_launcher_error_payload(&app_handle, &err))
                }
            },
        );
    }
    Ok(())
}

#[tauri::command]
fn update_install_and_restart(app: AppHandle) -> std::result::Result<(), String> {
    run_staged_install(&app).map_err(|e| {
        // [U-G] 台账:应用失败(staged 档保留,重试免重下)
        append_update_history(
            &app,
            serde_json::json!({ "event": "apply_failed", "error": format!("{e:#}") }),
        );
        format!("{e:#}")
    })
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
                    emit_ready_and_stabilize(
                        &app_handle,
                        &win,
                        &frontend_url(session.web_port, session.backend_port, session.chart_port),
                    );
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
                stop_runtime(
                    &session.paths,
                    Some((session.backend_port, session.chart_port)),
                );
            }
        }
    }
}

/// 退出清理只跑一次:红点路径 ExitRequested 与 Exit 各回调一次、`app.exit(0)` 也双发,
/// 不去重则 stop 脚本跑两遍。
static EXIT_CLEANUP_SPAWNED: AtomicBool = AtomicBool::new(false);

/// 抢占退出清理执行权:首个调用者得 true,其余 false(抽成函数便于单测)。
fn claim_exit_cleanup() -> bool {
    !EXIT_CLEANUP_SPAWNED.swap(true, Ordering::SeqCst)
}

/// 退出路径专用:detached 启动 stop 脚本,不等待。
/// 🔴 macOS 上菜单/Dock 的 Quit 走 native `terminate:`,tao 只回调 RunEvent::Exit(无
/// ExitRequested 可 prevent),且该回调跑在 applicationWillTerminate 内——任何同步
/// `.status()/.output()` 都让主事件循环停摆、系统标记 not responding。
/// 正确性:stop 脚本自含界(pid 文件+工作区路径守卫+端口兜底),app 死后脚本 reparent 给
/// launchd 继续完成回收;下次启动另有 reclaim_stale_port/stop_runtime 预清理兜底。
fn stop_runtime_detached(paths: &RuntimePaths, ports: Option<(u16, u16, u16)>) {
    if !paths.stop_script.exists() {
        return;
    }
    let mut command = Command::new("/bin/bash");
    command
        .arg(&paths.stop_script)
        .current_dir(paths.runtime_dir.join("Horosa-Web"))
        .stdout(Stdio::null())
        .stderr(Stdio::null());
    // 把本会话真实动态端口交给脚本:端口兜底扫描打到真端口,而非默认 8899/9999/8000
    // (修旧盲点:动态选口后兜底扫描一直只看默认口)。
    if let Some((backend_port, chart_port, web_port)) = ports {
        command
            .env("HOROSA_SERVER_PORT", backend_port.to_string())
            .env("HOROSA_CHART_PORT", chart_port.to_string())
            .env("HOROSA_WEB_PORT", web_port.to_string());
    }
    let _ = command.spawn();
}

/// 退出清理(非阻塞版):置静态服务器关闭位 + detached 停后端,毫秒级返回。
/// mid-life 的同步停服(runtime 更新前,必须停干净才能解压覆盖)仍走 cleanup_state,不经此函数。
fn spawn_exit_cleanup(app: &AppHandle) {
    if !claim_exit_cleanup() {
        return;
    }
    if let Some(state) = app.try_state::<AppState>() {
        if let Ok(mut shutdown) = state.web_shutdown.lock() {
            if let Some(flag) = shutdown.take() {
                flag.store(true, Ordering::Relaxed);
            }
        }
        if let Ok(session_slot) = state.session.lock() {
            if let Some(session) = session_slot.as_ref() {
                stop_runtime_detached(
                    &session.paths,
                    Some((session.backend_port, session.chart_port, session.web_port)),
                );
            }
        }
    }
}

fn runtime_bootstrap(
    app: AppHandle,
    window: WebviewWindow,
    force_runtime_install: bool,
) -> Result<RuntimeSession> {
    // 引导期服务本就不在:挂 busy 守卫让探活看门狗静默,防误判抢跑重启。
    let _bootstrap_busy = BootstrapBusyGuard::hold();
    emit_mode(
        &window,
        if force_runtime_install {
            "repair"
        } else {
            "launch"
        },
    );
    emit_status(&window, "正在检查安装配置…");
    if let Ok(app_data_dir) = app.path().app_data_dir() {
        let logs_dir = app_data_dir.join("logs");
        ledger_init(&logs_dir);
        prune_logs_dir_best_effort(&logs_dir);
    }
    ledger_mark("rust.bootstrap_begin", None);
    // App Translocation 提示(非阻塞):zip 通道用户从「下载」直接双击时,macOS 会把 App
    // 转移到随机只读挂载点运行。运行本身不受影响(运行时在共享/用户目录),但自更新换
    // 不到真实 App 路径——温和引导拖入「应用程序」。pkg 用户不会命中。
    if let Ok(exe) = std::env::current_exe() {
        if exe.to_string_lossy().contains("/AppTranslocation/") {
            ledger_mark("rust.app_translocated", None);
            emit_status(
                &window,
                "检测到 App 正从下载的临时位置运行:可在菜单选择「移入「应用程序」文件夹…」一键搬迁并重开,以获得完整的自动更新体验。",
            );
        }
    }
    // [U-A 撕裂探测] 两段 rename 回退路径/postinstall shell 对换若在中间被断电强杀,
    // current 会整体缺失——启动最早期按候选完整度收养,先于看门狗与安装检查。
    {
        let mut torn_roots = vec![shared_runtime_root()];
        if let Ok(user_root) = user_runtime_root(&app) {
            torn_roots.push(user_root);
        }
        for root in &torn_roots {
            match repair_torn_runtime_slots(root) {
                Ok(true) => emit_status(
                    &window,
                    "检测到上次更新中断，已自动恢复运行时，正在继续启动…",
                ),
                Ok(false) => {}
                Err(err) => eprintln!("[torn-repair] {} 修复失败: {err:#}", root.display()),
            }
            sweep_stale_runtime_stage_dirs(root);
        }
    }
    // 启动健康看门狗:连续 2 次未达 ready → 自动回滚 previous 槽(更新到坏版本的自愈)。
    if let Some(health_path) = launch_health_path(&app) {
        let pending = launch_health_note_start(&health_path);
        if pending > WATCHDOG_ROLLBACK_THRESHOLD && !force_runtime_install {
            let mut roots = vec![shared_runtime_root()];
            if let Ok(user_root) = user_runtime_root(&app) {
                roots.push(user_root);
            }
            let mut rolled = false;
            for root in &roots {
                match rollback_runtime_to_previous(root) {
                    Ok(true) => rolled = true,
                    Ok(false) => {}
                    Err(err) => eprintln!("[watchdog] 回滚 {} 失败: {err:#}", root.display()),
                }
            }
            if rolled {
                ledger_mark(
                    "rust.watchdog_rollback",
                    Some(serde_json::json!({"pending": pending})),
                );
                // [U-G] 台账:看门狗自动回滚(耐久行)
                append_update_history(
                    &app,
                    serde_json::json!({ "event": "watchdog_rollback", "pending": pending }),
                );
                emit_status(
                    &window,
                    "检测到连续两次启动未成功，已自动回退到上一版本运行时；启动后可在菜单「检查更新」重试升级。",
                );
                // 回滚开新的一链:本次视为第 1 次尝试。
                launch_health_write(&health_path, &LaunchHealth { pending_starts: 1 });
            }
        }
    }
    let paths = ensure_runtime_installed(&app, &window, force_runtime_install)?;
    ledger_mark("rust.runtime_check_done", None);
    // panic 路径清理登记(只第一次生效):app panic 不触发 RunEvent::Exit,
    // 这里把 stop 脚本交给 panic hook,后端子进程不孤儿化。
    let _ = PANIC_STOP_SCRIPT.set((
        paths.stop_script.clone(),
        paths.runtime_dir.join("Horosa-Web"),
    ));
    let mut web_port = choose_port_with_preference(DEFAULT_FRONTEND_PORT)?;
    let shutdown = Arc::new(AtomicBool::new(false));
    // TOCTOU 防线:「探口空闲」与「真正 bind」之间存在毫秒级窗口,被其它进程抢先会
    // bind 失败——换随机口重试 ×3,而不是把整次首启判死。
    let mut server_handle =
        start_static_server(paths.frontend_dir.clone(), web_port, shutdown.clone());
    for _ in 0..3 {
        if server_handle.is_ok() {
            break;
        }
        web_port = choose_free_port()?;
        server_handle = start_static_server(paths.frontend_dir.clone(), web_port, shutdown.clone());
    }
    let _server_handle = server_handle?;
    let mut backend_port = choose_free_port()?;
    let mut chart_port = choose_free_port()?;

    ledger_mark(
        "rust.ports_chosen",
        Some(serde_json::json!({"web": web_port, "backend": backend_port, "chart": chart_port})),
    );
    if let Some(state) = app.try_state::<AppState>() {
        if let Ok(mut slot) = state.web_shutdown.lock() {
            *slot = Some(shutdown);
        }
    }
    ledger_mark("rust.static_server_up", None);

    // 修复(更新后卡顿)C①:标记「读取即消费」——检测到刚更新完即把通知缓存进内存并删除磁盘标记,
    // 这样无论本次首启成功/失败,标记都不残留 → 杜绝「首启失败后次次都走 300s 全量慢路径」。
    let first_launch_after_update = consume_update_complete_marker_into_state(&app);
    let first_launch_timeout = if first_launch_after_update {
        Some(300)
    } else {
        None
    };
    // 修复(更新后卡住、需重启两三次 — v2.3.2):
    // apply_update 在安装前已对 runtime 包做 sha256 校验(verify_sha256(runtime_sha256)),
    // runtime 即「按官方清单逐字节验签过」的副本,故「更新后首启」再走 300s 全量慢校验属冗余,
    // 反而让冷首启看起来卡死、用户强退 → 标记没写 → 下次又全量 → 反复重启。
    // 这里对刚装好的(已验签)runtime **在 start_runtime 之前**预写 fast-path 标记:
    //   ① 首启即走 trusted 快路径(实测 ~7s,远快于冷全量 22s+);
    //   ② 标记在 warmup/导航之前就落盘 → 即便用户把冷首启当卡死强退,下次仍是快路径,
    //      根除「每次强退都退回 300s 全量 → 要重启两三次才打开」。
    // 兜底:若快路径在新 runtime 上失败,下方 first_launch_after_update 分支会 clear 标记并自动全量复检。
    if first_launch_after_update {
        if let Some(manifest) = read_runtime_manifest(&paths) {
            write_runtime_fast_path_marker(&paths.runtime_dir, &manifest);
        }
    }
    // 提速(更新后卡顿)B:warmup 仅首启触发,且脚本内已改为后台非阻塞预热,不再卡启动;
    // mongo 为可选服务,一律跳过启动期 ping(mongo 缺席时 ping 会拖满等待)。
    let skip_runtime_warmup = !first_launch_after_update;
    let fast_path_enabled = !force_runtime_install && runtime_fast_path_allowed(&paths.runtime_dir);
    let skip_mongo_ping = true;
    if first_launch_after_update {
        emit_status(&window, "检测到刚完成更新，正在执行更新后的首次恢复启动…");
        // 修复(更新后卡顿):runtime 已在安装前逐字节验签,首启走 trusted 快路径(通常 ~10 秒内,
        // 冷启动略久)。用不确定进度动画 + 明确文案,避免冷启动的短暂停顿被当成「卡死」而被强退。
        emit_indeterminate_progress(&window, 78, "更新已完成，正在恢复启动,通常约 10 秒,请稍候…");
        // 修复(更新后卡在启动页 / 不进主界面 / 「进入主界面」按钮无效 —— 真因):
        // 原先此处调 `cleanup_state(&app)`,它会 `web_shutdown.take()` 后 `store(true)`,把本次
        // runtime_bootstrap 上方刚 `start_static_server` 起来的静态服务器(web_port)直接关掉 →
        // 之后 `emit_ready` 让 webview 导航到的 `frontend_url`(http://127.0.0.1:web_port/index.html)
        // 立刻连不上 → 永远停在启动页(每次更新必现;普通重启不走此分支故正常,这也是「重启就好」的原因)。
        // 实测:此刻 curl web_port 直接 connection-refused、进程零监听端口。`cleanup_state` 在这里对
        // session 是 no-op(`start_runtime` 还没跑、session 为 None),唯一实际效果就是误杀静态服务器。
        // 故直接去掉,只保留 1s 缓冲。
        thread::sleep(Duration::from_secs(1));
    }
    // 修法1:首次启动走带「端口冲突重试」的封装(web/静态服务器不参与本环;仅 backend/chart 换口重试)。
    // 非端口类错误 / 端口重试耗尽时,原样落入下方既有的「更新后首启 / 快路径回退」分支(逻辑保持不变)。
    if let Err(first_err) = start_runtime_with_port_retry(
        &paths,
        &window,
        &mut backend_port,
        &mut chart_port,
        first_launch_timeout,
        skip_runtime_warmup,
        skip_mongo_ping,
        fast_path_enabled,
    ) {
        clear_runtime_fast_path_marker(&paths.runtime_dir);
        if first_launch_after_update {
            emit_status(&window, "更新后的第一次启动正在自动复检服务，请稍候…");
            // indeterminate + 与 start_runtime 入口同档(82):重试会再次进入 start_runtime,
            // 入口发 82,这里若发 84 会出现进度倒退。
            emit_indeterminate_progress(&window, 82, "更新后首次启动自动重试");
            stop_runtime(&paths, Some((backend_port, chart_port)));
            thread::sleep(Duration::from_secs(3));
            backend_port = choose_free_port()?;
            chart_port = choose_free_port()?;
            start_runtime(
                &paths,
                &window,
                backend_port,
                chart_port,
                first_launch_timeout,
                false,
                false,
                false,
            )
            .map_err(|retry_err| {
                anyhow!(
                    "更新后首次启动失败，已自动重试一次仍未恢复。\n首次错误:\n{:#}\n\n重试错误:\n{:#}",
                    first_err,
                    retry_err
                )
            })?;
        } else if fast_path_enabled {
            // WS-1c:回退从「一行状态」升级为醒目说明(属正常保护而非故障)+账本留痕(诊断中心可见)。
            ledger_mark("rust.fast_path_fallback", None);
            emit_status(
                &window,
                "快速启动校验未通过，已自动切换完整校验启动（预计 30-60 秒），属正常自我保护，请稍候…",
            );
            // 同上:与 start_runtime 入口同档防倒退。
            emit_indeterminate_progress(
                &window,
                82,
                "快速启动校验未通过 · 已自动切换完整校验(预计 30-60 秒,属正常保护)",
            );
            stop_runtime(&paths, Some((backend_port, chart_port)));
            thread::sleep(Duration::from_secs(1));
            backend_port = choose_free_port()?;
            chart_port = choose_free_port()?;
            start_runtime(
                &paths,
                &window,
                backend_port,
                chart_port,
                first_launch_timeout,
                false,
                false,
                false,
            )
            .map_err(|retry_err| {
                anyhow!(
                    "快速启动失败，已自动回退到完整校验启动一次仍未恢复。\n首次错误:\n{:#}\n\n回退错误:\n{:#}",
                    first_err,
                    retry_err
                )
            })?;
        } else {
            return Err(first_err);
        }
    }
    if let Some(manifest) = read_runtime_manifest(&paths) {
        write_runtime_fast_path_marker(&paths.runtime_dir, &manifest);
    }
    emit_progress(&window, 100, "星阙 已准备完成");
    // junk 后台 mop-up:trusted 快路径已不在启动期做全树元数据清理(start_runtime),
    // 这里在服务就绪后延迟 10s(避开 warmup IO 高峰)补扫一遍,保持「runtime 树最终无
    // .DS_Store/._* junk」的不变量;best-effort,失败静默(共享目录可能无权限)。
    {
        let mop_dir = paths.runtime_dir.clone();
        thread::spawn(move || {
            thread::sleep(Duration::from_secs(10));
            let _ = cleanup_runtime_metadata(&mop_dir);
        });
    }
    Ok(RuntimeSession {
        paths,
        backend_port,
        chart_port,
        web_port,
    })
}

/// ── 结构化启动账本(Rust 层写入端)────────────────────────────────────────────
/// 一行一段 JSON Lines,四层进程(Rust/shell/Java/Python)经 env(HOROSA_RUN_TAG/
/// HOROSA_LEDGER_FILE)共享同一文件;Rust 是 run 标签的生成者。只在段边界打点,
/// append + best-effort 吞错,账本绝不影响启动;HOROSA_STARTUP_LEDGER=0 总关。
static STARTUP_LEDGER: std::sync::OnceLock<Option<(String, PathBuf, Instant)>> =
    std::sync::OnceLock::new();

/// 日志目录防写满盘:每次启动都会新建一个 run 子目录(四层账本+服务 stdout),放任累积
/// 数月可达 GB 级——启动期 best-effort 修剪:>14 天的子目录/文件删除;常追加的单文件
/// (如 updater-events.log)超 20MB 轮转成 .old 保一代。失败只跳过,绝不阻塞启动。
fn prune_logs_dir_best_effort(logs_dir: &Path) {
    const MAX_AGE: Duration = Duration::from_secs(14 * 24 * 3600);
    const MAX_SINGLE_LOG_BYTES: u64 = 20 * 1024 * 1024;
    let now = SystemTime::now();
    let Ok(entries) = fs::read_dir(logs_dir) else {
        return;
    };
    for entry in entries.flatten() {
        let path = entry.path();
        let Ok(meta) = entry.metadata() else {
            continue;
        };
        let stale = meta
            .modified()
            .ok()
            .and_then(|m| now.duration_since(m).ok())
            .map(|age| age > MAX_AGE)
            .unwrap_or(false);
        if stale {
            if meta.is_dir() {
                let _ = fs::remove_dir_all(&path);
            } else {
                let _ = fs::remove_file(&path);
            }
            continue;
        }
        if meta.is_file()
            && meta.len() > MAX_SINGLE_LOG_BYTES
            && path
                .extension()
                .map(|e| e == "log" || e == "jsonl")
                .unwrap_or(false)
        {
            let rotated = path.with_extension("old");
            let _ = fs::remove_file(&rotated);
            let _ = fs::rename(&path, &rotated);
        }
    }
}

fn ledger_init(logs_dir: &Path) {
    let enabled = std::env::var("HOROSA_STARTUP_LEDGER")
        .map(|v| {
            !matches!(
                v.to_ascii_lowercase().as_str(),
                "0" | "false" | "no" | "off"
            )
        })
        .unwrap_or(true);
    if !enabled {
        let _ = STARTUP_LEDGER.set(None);
        return;
    }
    let millis = SystemTime::now()
        .duration_since(SystemTime::UNIX_EPOCH)
        .map(|d| d.as_millis())
        .unwrap_or(0);
    let run_tag = format!("r{}", millis);
    let dir = logs_dir.join(&run_tag);
    let _ = fs::create_dir_all(&dir);
    let file = dir.join("horosa-startup-ledger.jsonl");
    let _ = STARTUP_LEDGER.set(Some((run_tag, file, Instant::now())));
}

fn ledger_mark(seg: &str, extra: Option<serde_json::Value>) {
    let Some(Some((run_tag, file, t0))) = STARTUP_LEDGER.get().map(|v| v.as_ref()).map(|v| v)
    else {
        return;
    };
    let t_ms = t0.elapsed().as_millis();
    let mut row = serde_json::json!({
        "run": run_tag,
        "layer": "rust",
        "seg": seg,
        "pid": std::process::id(),
        "t_ms": t_ms,
    });
    if let Some(extra) = extra {
        row["extra"] = extra;
    }
    if let Ok(mut fh) = fs::OpenOptions::new().create(true).append(true).open(file) {
        use std::io::Write;
        let _ = writeln!(fh, "{}", row);
    }
}

fn ledger_env() -> Option<(String, PathBuf)> {
    STARTUP_LEDGER
        .get()
        .and_then(|v| v.as_ref())
        .map(|(tag, file, _)| (tag.clone(), file.clone()))
}

/// ── 更新进度可视化 v2:全局字节账本 ─────────────────────────────────────────────
/// 一次后台更新一本账(既有设计即单飞),download_update_asset_once 喂块、事件层读
/// 速度(10s 滑窗)/ETA/总量;HOROSA_PROGRESS_V2=0 时退化为老三样(phase/pct/message)。
struct DownloadLedger {
    mode: String,                                       // "incremental" | "full"
    total_bytes: u64,                                   // 计划总下载量(0=未知,前端显「大小待定」)
    completed_bytes: u64,                               // 已完成资产累计
    current_bytes: u64,                                 // 当前资产已下
    window: std::collections::VecDeque<(Instant, u64)>, // (时刻, 全局已下字节) 10s 滑窗
    component_index: u32,
    component_total: u32,
    component_name: String,
    last_emit: Instant,
    last_emit_bytes: u64,
}

impl DownloadLedger {
    fn new(mode: &str, total_bytes: u64) -> Self {
        Self {
            mode: mode.to_string(),
            total_bytes,
            completed_bytes: 0,
            current_bytes: 0,
            window: std::collections::VecDeque::new(),
            component_index: 0,
            component_total: 0,
            component_name: String::new(),
            last_emit: Instant::now(),
            last_emit_bytes: 0,
        }
    }

    fn downloaded(&self) -> u64 {
        self.completed_bytes + self.current_bytes
    }

    fn on_chunk(&mut self, delta: u64) {
        self.current_bytes += delta;
        let now = Instant::now();
        let total = self.downloaded();
        self.window.push_back((now, total));
        while let Some((t, _)) = self.window.front() {
            if now.duration_since(*t) > Duration::from_secs(10) {
                self.window.pop_front();
            } else {
                break;
            }
        }
    }

    fn finish_asset(&mut self) {
        self.completed_bytes += self.current_bytes;
        self.current_bytes = 0;
    }

    fn speed_bps(&self) -> u64 {
        match (self.window.front(), self.window.back()) {
            (Some((t0, b0)), Some((t1, b1))) if t1 > t0 => {
                let secs = t1.duration_since(*t0).as_secs_f64();
                if secs <= 0.0 {
                    0
                } else {
                    (((*b1 - *b0) as f64) / secs) as u64
                }
            }
            _ => 0,
        }
    }

    fn eta_secs(&self) -> Option<u64> {
        let speed = self.speed_bps();
        if speed == 0 || self.total_bytes == 0 {
            return None;
        }
        let remaining = self.total_bytes.saturating_sub(self.downloaded());
        Some(remaining / speed.max(1))
    }

    /// 节流:≥200ms 且(有明显增量 ≥1MB 或距上次 ≥1s)才 emit,防 window.eval 洪泛。
    fn should_emit(&mut self) -> bool {
        let now = Instant::now();
        let since = now.duration_since(self.last_emit);
        if since < Duration::from_millis(200) {
            return false;
        }
        let grown = self.downloaded().saturating_sub(self.last_emit_bytes);
        if grown < 1_048_576 && since < Duration::from_secs(1) {
            return false;
        }
        self.last_emit = now;
        self.last_emit_bytes = self.downloaded();
        true
    }
}

static UPDATE_LEDGER: Mutex<Option<DownloadLedger>> = Mutex::new(None);

fn progress_v2_enabled() -> bool {
    std::env::var("HOROSA_PROGRESS_V2")
        .map(|v| !matches!(v.as_str(), "0" | "false" | "no" | "off"))
        .unwrap_or(true)
}

fn update_ledger_init(mode: &str, total_bytes: u64) {
    if let Ok(mut slot) = UPDATE_LEDGER.lock() {
        *slot = Some(DownloadLedger::new(mode, total_bytes));
    }
}

fn update_ledger_begin_asset(name: &str, index: u32, total: u32) {
    if let Ok(mut slot) = UPDATE_LEDGER.lock() {
        if let Some(ledger) = slot.as_mut() {
            ledger.component_name = name.to_string();
            ledger.component_index = index;
            ledger.component_total = total;
        }
    }
}

fn update_ledger_finish_asset() {
    if let Ok(mut slot) = UPDATE_LEDGER.lock() {
        if let Some(ledger) = slot.as_mut() {
            ledger.finish_asset();
        }
    }
}

/// 资产下载失败重试前清当前资产字节(半成品作废,账本不虚增)。
fn update_ledger_reset_current() {
    if let Ok(mut slot) = UPDATE_LEDGER.lock() {
        if let Some(ledger) = slot.as_mut() {
            ledger.current_bytes = 0;
            ledger.window.clear();
        }
    }
}

/// 断点续传补入的既有字节:计入进度显示(downloadedBytes),不进速度滑窗(速度不虚高)。
fn update_ledger_note_resumed(bytes: u64) {
    if let Ok(mut slot) = UPDATE_LEDGER.lock() {
        if let Some(ledger) = slot.as_mut() {
            ledger.current_bytes = ledger.current_bytes.saturating_add(bytes);
        }
    }
}

fn update_ledger_clear() {
    if let Ok(mut slot) = UPDATE_LEDGER.lock() {
        *slot = None;
    }
}

/// 喂块并(按节流)返回要合并进 downloading 事件的 v2 字段;v2 关闭/无账本时返回 None。
fn update_ledger_chunk_fields(delta: u64) -> Option<serde_json::Value> {
    if !progress_v2_enabled() {
        return None;
    }
    let mut slot = UPDATE_LEDGER.lock().ok()?;
    let ledger = slot.as_mut()?;
    ledger.on_chunk(delta);
    if !ledger.should_emit() {
        return None;
    }
    let mut fields = serde_json::json!({
        "mode": ledger.mode,
        "downloadedBytes": ledger.downloaded(),
        "speedBps": ledger.speed_bps(),
    });
    if ledger.total_bytes > 0 {
        fields["totalBytes"] = serde_json::json!(ledger.total_bytes);
    }
    if let Some(eta) = ledger.eta_secs() {
        fields["etaSecs"] = serde_json::json!(eta);
    }
    if ledger.component_total > 0 {
        fields["component"] = serde_json::json!(ledger.component_name);
        fields["componentIndex"] = serde_json::json!(ledger.component_index);
        fields["componentTotal"] = serde_json::json!(ledger.component_total);
    }
    Some(fields)
}

fn update_ledger_summary() -> Option<(String, u64)> {
    let slot = UPDATE_LEDGER.lock().ok()?;
    let ledger = slot.as_ref()?;
    Some((ledger.mode.clone(), ledger.downloaded()))
}

/// 「本次需下载 XX MB(增量,复用 YY%)」的计算来源:display-only,真实下载路径照旧自决。
struct UpdateEstimate {
    mode: &'static str,      // "incremental" | "full"
    need_bytes: Option<u64>, // 预计下载量(None=大小待定)
    reuse_pct: Option<u8>,   // 增量复用率(仅 incremental)
    changed_names: Vec<String>,
}

fn compute_update_estimate(plan: &UpdatePlan, app_should_update: bool) -> UpdateEstimate {
    let app_bytes = if app_should_update {
        plan.app_size_bytes
    } else {
        Some(0)
    };
    let roots = vec![shared_runtime_root()];
    if let Some(changed) = plan_component_diff(plan, &roots) {
        let full_runtime: u64 = plan
            .components
            .as_ref()
            .map(|cs| cs.iter().filter_map(|c| c.size).sum())
            .unwrap_or(0);
        let need_runtime: u64 = changed.iter().filter_map(|c| c.size).sum();
        let reuse_pct = if full_runtime > 0 {
            Some((100u64.saturating_sub(need_runtime * 100 / full_runtime)) as u8)
        } else {
            None
        };
        let need_bytes = app_bytes.map(|a| a + need_runtime);
        return UpdateEstimate {
            mode: "incremental",
            need_bytes,
            reuse_pct,
            changed_names: changed.iter().map(|c| c.name.clone()).collect(),
        };
    }
    let need_bytes = match (app_bytes, plan.runtime_size_bytes) {
        (Some(a), Some(r)) => Some(a + r),
        _ => None,
    };
    UpdateEstimate {
        mode: "full",
        need_bytes,
        reuse_pct: None,
        changed_names: Vec::new(),
    }
}

/// panic 路径的后端清理:正常退出走 RunEvent::Exit→stop_runtime,但 panic 不触发 Exit 事件,
/// java/python 子进程会孤儿化(start 脚本 reaper 只覆盖下次启动时回收)。bootstrap 成功后把
/// stop 脚本路径塞进这里,panic hook best-effort 执行。
static PANIC_STOP_SCRIPT: std::sync::OnceLock<(PathBuf, PathBuf)> = std::sync::OnceLock::new();

fn register_panic_runtime_cleanup() {
    let previous = std::panic::take_hook();
    std::panic::set_hook(Box::new(move |info| {
        if let Some((script, cwd)) = PANIC_STOP_SCRIPT.get() {
            if script.exists() {
                let _ = Command::new("/bin/bash")
                    .arg(script)
                    .current_dir(cwd)
                    .stdout(Stdio::null())
                    .stderr(Stdio::null())
                    .status();
            }
        }
        previous(info);
    }));
}

/// 启动期 best-effort 清扫:更新下载的临时文件带时间戳后缀(每次新名),进程中途被杀时遗留
/// 在系统临时目录累积。删 24h 前的本应用模式文件;失败静默(清扫绝不影响启动)。
fn sweep_stale_tmp_downloads() {
    thread::spawn(|| {
        let tmp = std::env::temp_dir();
        let prefix = format!("{}-", APP_NAME);
        let cutoff = SystemTime::now() - Duration::from_secs(24 * 3600);
        if let Ok(entries) = fs::read_dir(&tmp) {
            for entry in entries.flatten() {
                let name = entry.file_name().to_string_lossy().to_string();
                if !name.starts_with(&prefix) {
                    continue;
                }
                let Ok(meta) = entry.metadata() else { continue };
                let Ok(modified) = meta.modified() else {
                    continue;
                };
                if modified < cutoff {
                    let path = entry.path();
                    let _ = if meta.is_dir() {
                        fs::remove_dir_all(&path)
                    } else {
                        fs::remove_file(&path)
                    };
                }
            }
        }
    });
}

// [U-B] swap CLI 本体(纯函数可测):0=互换成功;2=不可用/入参不齐(调用方走 mv 回退);
// 1=真实错误(同样回退)。helper 借主二进制做 renamex_np——不新增 Mach-O 进签名面。
fn run_swap_cli(a: &Path, b: &Path) -> i32 {
    if !a.exists() || !b.exists() {
        eprintln!(
            "[swap-cli] 两侧路径必须都存在: {} / {}",
            a.display(),
            b.display()
        );
        return 2;
    }
    match atomic_swap_dirs(a, b) {
        Ok(true) => 0,
        Ok(false) => 2,
        Err(err) => {
            eprintln!("[swap-cli] {err:#}");
            1
        }
    }
}

// 隐藏 CLI:update helper 借「新版 app 自己的二进制」做全量 runtime 对换——
// 与进程内 extract_runtime_archive_with 完全同一协议(磁盘预检 + _extract 暂存 +
// 版本闸 + renamex 原子互换 + previous 保留到首次 ready)。stdout/stderr 由 helper
// 的 exec >> LOG 收进 update.log。exit: 0=成功 / 1=手术失败(current 未动或已回滚,
// 半成品已清或留给撕裂探测) / 2=入参不可用。
fn run_runtime_swap_cli(root: &Path, archive: &Path, expected_version: &str) -> i32 {
    if !archive.is_file() {
        eprintln!("[runtime-swap] archive 不存在: {}", archive.display());
        return 2;
    }
    if let Err(err) = ensure_dir(root) {
        eprintln!("[runtime-swap] runtime 根不可用 {}: {err:#}", root.display());
        return 2;
    }
    let expected = expected_version.trim();
    let expected = if expected.is_empty() {
        None
    } else {
        Some(expected)
    };
    match extract_runtime_archive_with(archive, root, None, expected) {
        Ok(()) => {
            let _ = clear_runtime_pending_marker(&root.join("current"));
            println!("[runtime-swap] promoted new runtime at {}", root.display());
            0
        }
        Err(err) => {
            eprintln!("[runtime-swap] {err:#}");
            1
        }
    }
}

fn main() {
    // [U-B] 隐藏 CLI 旗标:update helper 用「新版 app 自己的二进制」做原子互换,
    // 位于 tauri::Builder 之前(零 UI、零窗口即退)。
    {
        let args: Vec<String> = std::env::args().collect();
        if args.len() == 4 && args[1] == "--horosa-atomic-swap" {
            std::process::exit(run_swap_cli(Path::new(&args[2]), Path::new(&args[3])));
        }
        // helper 全量 runtime 对换(与 --horosa-atomic-swap 同款先例:零 UI 即退)。
        if args.len() == 5 && args[1] == "--horosa-runtime-swap" {
            std::process::exit(run_runtime_swap_cli(
                Path::new(&args[2]),
                Path::new(&args[3]),
                &args[4],
            ));
        }
    }
    configure_macos_native_window_restoration();
    register_panic_runtime_cleanup();
    sweep_stale_tmp_downloads();
    tauri::Builder::default()
        .manage(AppState::default())
        // [E1 剪贴板] 主线程创建(照官方 clipboard-manager 插件形态);失败存 None,command 内惰性重建
        .manage(DesktopClipboardState(Mutex::new(
            arboard::Clipboard::new().ok(),
        )))
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
            open_login_items_settings_command,
            pick_ai_analysis_files_command,
            pick_ai_analysis_folder_command,
            save_ai_analysis_file_command,
            open_ai_analysis_backup_command,
            update_check_silent,
            update_start_background,
            update_install_and_restart,
            copy_text_to_clipboard_command,
            open_external_url_command,
            print_report_html_command,
            get_backend_endpoints,
            restart_local_services_command,
            export_diagnostics_bundle
        ])
        .setup(|app| {
            let app_handle = app.handle().clone();
            set_window_state_persistence_ready(&app_handle, false);
            let main_state = load_window_states(&app_handle).main;
            let window = if let Some(window) = app.get_webview_window(MAIN_WINDOW_LABEL) {
                window
            } else {
                build_main_window(&app_handle, &main_state)?
            };
            apply_main_window_launch_state(&window, &main_state);
            set_window_zoom(&app_handle, load_preferences(&app_handle).zoom_level)?;
            if handoff_to_newer_installed_app(&app_handle)? {
                return Ok(());
            }
            show_or_focus_window(&window);
            enable_window_state_persistence_after_launch(app_handle.clone());
            thread::spawn(move || {
                match runtime_bootstrap(app_handle.clone(), window.clone(), false) {
                    Ok(session) => {
                        if let Some(state) = app_handle.try_state::<AppState>() {
                            if let Ok(mut slot) = state.session.lock() {
                                *slot = Some(session.clone());
                            }
                        }
                        emit_ready_and_stabilize(
                            &app_handle,
                            &window,
                            &frontend_url(
                                session.web_port,
                                session.backend_port,
                                session.chart_port,
                            ),
                        );
                        show_post_update_notice_if_needed(&app_handle);
                    }
                    Err(err) => emit_launcher_error(
                        &window,
                        &build_launcher_error_payload(&app_handle, &err),
                    ),
                }
            });

            // [U-H 周期检查+节流] 自动检查更新(若偏好启用):启动延迟 10s 首查——
            // 距上次成功检查 <4h 直接跳过(节流,防每次开关 app 都打网络);此后线程
            // 驻留每 24h 再查(长开 app 也能收到新版;偏好每轮重读,关闭即静默)。
            // 检查失败不再静默:账本 rust.update_check_failed + check-failed 低打扰事件。
            {
                let app_handle = app.handle().clone();
                thread::spawn(move || {
                    thread::sleep(std::time::Duration::from_secs(10));
                    loop {
                        if load_preferences(&app_handle).auto_check_updates {
                            run_auto_update_check(&app_handle);
                        }
                        thread::sleep(auto_update_check_cycle());
                    }
                });
            }

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
                // 菜单「检查更新」并轨(消全量旁路):主窗口在时走非阻塞事件流(UpdateNotifier,
                // 天然增量,与自动检查同一条路)——此前菜单永远走老阻塞 check_for_updates 的
                // 全量 runtime 下载,同一次更新两个入口体积差 10 倍。无主窗口(启动早期/异常)
                // 或 HOROSA_MENU_UPDATE_LEGACY=1 时保留老路,老函数整体不删。
                let legacy = std::env::var("HOROSA_MENU_UPDATE_LEGACY").ok().as_deref()
                    == Some("1");
                let has_main = app.get_webview_window(MAIN_WINDOW_LABEL).is_some();
                if !legacy && has_main {
                    let app_handle = app.clone();
                    thread::spawn(move || {
                        match update_check_silent(app_handle.clone()) {
                            Ok(avail) if avail.available => {
                                let mut payload = serde_json::json!({
                                    "phase": "available",
                                    "currentVersion": avail.current_version,
                                    "latestVersion": avail.latest_version,
                                    "runtimeNeedsUpdate": avail.runtime_needs_update,
                                    "notes": avail.notes,
                                    "releaseUrl": avail.release_url,
                                });
                                if let Some(mode) = avail.update_mode {
                                    payload["mode"] = serde_json::json!(mode);
                                }
                                if let Some(bytes) = avail.download_bytes {
                                    payload["downloadBytes"] = serde_json::json!(bytes);
                                }
                                if let Some(pct) = avail.reuse_pct {
                                    payload["reusePct"] = serde_json::json!(pct);
                                }
                                emit_update_event(&app_handle, &payload.to_string());
                            }
                            Ok(_) => {
                                emit_update_event(
                                    &app_handle,
                                    &serde_json::json!({
                                        "phase": "uptodate",
                                        "message": "已是最新版本",
                                    })
                                    .to_string(),
                                );
                            }
                            Err(err) => {
                                emit_update_event(
                                    &app_handle,
                                    &serde_json::json!({
                                        "phase": "error",
                                        "message": format!("检查更新失败:{err}"),
                                    })
                                    .to_string(),
                                );
                            }
                        }
                    });
                } else {
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
                }
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
            } else if id == MENU_RELOCATE_APP {
                // [U-I G8] Translocation/任意非标准位置 → 一键拷入「应用程序」并重开。
                let app_handle = app.clone();
                thread::spawn(move || {
                    let bundle = app_bundle_path();
                    let dest = installed_app_target_path();
                    let already_installed = bundle
                        .as_deref()
                        .map(|b| b == dest.as_path())
                        .unwrap_or(false);
                    if already_installed {
                        MessageDialog::new()
                            .set_level(MessageLevel::Info)
                            .set_title("移入「应用程序」文件夹")
                            .set_description("当前已从「应用程序」文件夹运行,无需搬迁。")
                            .show();
                        return;
                    }
                    let proceed = MessageDialog::new()
                        .set_level(MessageLevel::Info)
                        .set_title("移入「应用程序」文件夹")
                        .set_description(
                            "将把本应用拷贝到「应用程序」文件夹并重新打开(自动更新等功能需要固定安装位置)。是否继续?",
                        )
                        .set_buttons(MessageButtons::YesNo)
                        .show();
                    if proceed != MessageDialogResult::Yes {
                        return;
                    }
                    match relocate_app_to_applications(&app_handle) {
                        Ok(done_msg) if !done_msg.is_empty() => {
                            MessageDialog::new()
                                .set_level(MessageLevel::Info)
                                .set_title("移入「应用程序」文件夹")
                                .set_description(done_msg)
                                .show();
                        }
                        Ok(_) => {}
                        Err(err) => {
                            MessageDialog::new()
                                .set_level(MessageLevel::Error)
                                .set_title("移入「应用程序」文件夹")
                                .set_description(format!("搬迁未完成:{err:#}"))
                                .show();
                        }
                    }
                });
            } else if id == MENU_RESTART_SERVICES {
                // 手动兜底:服务被系统/杀软杀掉、探活看门狗已限频停手时,一键救活。
                let app_handle = app.clone();
                thread::spawn(move || {
                    let outcome = restart_local_services(&app_handle, "menu");
                    let (level, text) = match outcome {
                        Ok(()) => (
                            MessageLevel::Info,
                            "本地服务已重启完成。若界面上有请求刚好失败,重新操作一次即可。"
                                .to_string(),
                        ),
                        Err(err) => (
                            MessageLevel::Error,
                            format!(
                                "重启本地服务未成功:{err:#}\n可稍后再试;菜单「在 Finder 中显示日志」可取诊断日志。"
                            ),
                        ),
                    };
                    MessageDialog::new()
                        .set_level(level)
                        .set_title("重启本地服务")
                        .set_description(text)
                        .show();
                });
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
                let should_persist = match event {
                    WindowEvent::Moved(_) | WindowEvent::Resized(_) => {
                        is_window_state_persistence_ready(app)
                    }
                    WindowEvent::CloseRequested { .. } => true,
                    _ => false,
                };
                if should_persist {
                    if let Some(window) = app.get_webview_window(&label) {
                        let _ = persist_window_state_for_label(app, &label, &window);
                    }
                }
            }
            // 🔴 退出两臂禁同步子进程(cleanup_state → stop 脚本 .status() 会阻塞主事件循环,
            // macOS 标记 not responding 数秒)。Cmd+Q 走 native terminate: 只回调 Exit、不可
            // prevent,所以两臂都用 detached + 去重的 spawn_exit_cleanup。
            RunEvent::ExitRequested { .. } => {
                if is_window_state_persistence_ready(app) {
                    persist_all_known_window_states(app);
                }
                spawn_exit_cleanup(app);
            }
            RunEvent::Exit => {
                if is_window_state_persistence_ready(app) {
                    persist_all_known_window_states(app);
                }
                spawn_exit_cleanup(app);
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
    #[cfg(unix)]
    use std::os::unix::fs::PermissionsExt;
    use std::process::Command;
    use tar::Builder;

    // [E1 剪贴板] UTF-8 roundtrip:主路 arboard 与兜底 pbcopy(LC_CTYPE 钉死)两路合一,
    // 防 cargo test 并行互踩全局剪贴板;先存后还,尽量不打扰开发者剪贴板。
    // 读侧 pbpaste 同样要钉 LC_CTYPE:无 locale 时读侧也按 MacRoman 转码输出。
    #[test]
    #[cfg(target_os = "macos")]
    fn clipboard_utf8_roundtrip_native_and_pbcopy() {
        let sample = "技术·測試 ✓ 三式合一";
        let saved = arboard::Clipboard::new()
            .ok()
            .and_then(|mut c| c.get_text().ok());

        // ① arboard 主路
        let mut clip = arboard::Clipboard::new().expect("arboard 初始化失败");
        clip.set_text(sample.to_string()).expect("arboard 写入失败");
        assert_eq!(clip.get_text().expect("arboard 读回失败"), sample);
        drop(clip);

        // ② pbcopy 兜底
        pbcopy_utf8_fallback(sample).expect("pbcopy 兜底写入失败");
        let out = Command::new("/usr/bin/pbpaste")
            .env("LC_CTYPE", "UTF-8")
            .output()
            .expect("pbpaste 执行失败");
        assert_eq!(String::from_utf8_lossy(&out.stdout), sample);

        if let (Some(prev), Ok(mut c)) = (saved, arboard::Clipboard::new()) {
            let _ = c.set_text(prev);
        }
    }

    // [U-D 防降级] 单调判定矩阵:remote 更新才更;更旧被拦;rank 等价不重复下载;
    // 逃生阀恢复老「不同即更」语义;合成串(GithubApi 无 -runtimeN)同 base 视作更旧修订被拦。
    #[test]
    fn runtime_update_monotonic_gate() {
        use RuntimeUpdateDecision::*;
        let d = compute_runtime_update_decision;
        assert_eq!(
            d(Some("3.3.3-runtime1"), Some("3.3.2-runtime1"), false),
            Needed
        );
        // runtime 修订位数值序(非字典序):-runtime10 > -runtime2
        assert_eq!(
            d(Some("3.3.2-runtime10"), Some("3.3.2-runtime2"), false),
            Needed
        );
        assert_eq!(
            d(Some("3.3.2-runtime2"), Some("3.3.2-runtime10"), false),
            DowngradeBlocked
        );
        // 字符串不同但 rank 等价 → 视为已最新(不重复下载)
        assert_eq!(
            d(Some("3.3.2-runtime1"), Some("3.3.2-runtime01"), false),
            UpToDate
        );
        assert_eq!(
            d(Some("3.3.2-runtime1"), Some("3.3.2-runtime1"), false),
            UpToDate
        );
        // 远端更旧 → 拦;逃生阀放行
        assert_eq!(
            d(Some("3.3.1-runtime9"), Some("3.3.2-runtime1"), false),
            DowngradeBlocked
        );
        assert_eq!(
            d(Some("3.3.1-runtime9"), Some("3.3.2-runtime1"), true),
            Needed
        );
        // 本地无 runtime → 必装;远端无字段 → 不更
        assert_eq!(d(Some("3.3.2-runtime1"), None, false), Needed);
        assert_eq!(d(None, Some("3.3.2-runtime1"), false), UpToDate);
        // GithubApi 合成串(裸版本号):同 base 视作更旧修订 → 拦(避免无谓整包重下)
        assert_eq!(
            d(Some("3.3.2"), Some("3.3.2-runtime1"), false),
            DowngradeBlocked
        );
        assert_eq!(d(Some("3.3.3"), Some("3.3.2-runtime1"), false), Needed);
    }

    #[test]
    fn runtime_needs_update_unparseable_falls_back_to_neq() {
        use RuntimeUpdateDecision::*;
        // 任一侧 rank 解析失败 → 回退「不同即更」(防脏版本串永久卡死更新链)
        assert_eq!(
            compute_runtime_update_decision(Some("weird-tag"), Some("3.3.2-runtime1"), false),
            Needed
        );
        assert_eq!(
            compute_runtime_update_decision(Some("3.3.3-runtime1"), Some("corrupted"), false),
            Needed
        );
        // 双侧相同脏串 → 字符串相等短路,视为最新
        assert_eq!(
            compute_runtime_update_decision(Some("weird"), Some("weird"), false),
            UpToDate
        );
    }

    // [U-A] 撕裂测试用最小「完整」runtime 树(过 runtime_dir_has_required_files 五文件判据)
    fn write_minimal_runtime_tree(dir: &Path, marker: &str) {
        fs::create_dir_all(dir.join("Horosa-Web/astrostudyui/dist-file")).unwrap();
        fs::create_dir_all(dir.join("runtime/mac/python/bin")).unwrap();
        fs::create_dir_all(dir.join("runtime/mac/java/bin")).unwrap();
        fs::write(
            dir.join("runtime-manifest.json"),
            format!("{{\"version\":\"{}\"}}\n", marker),
        )
        .unwrap();
        fs::write(
            dir.join("Horosa-Web/start_horosa_local.sh"),
            "#!/bin/bash\n",
        )
        .unwrap();
        fs::write(
            dir.join("Horosa-Web/astrostudyui/dist-file/index.html"),
            marker,
        )
        .unwrap();
        fs::write(dir.join("runtime/mac/python/bin/python3"), "stub").unwrap();
        fs::write(dir.join("runtime/mac/java/bin/java"), "stub").unwrap();
    }

    #[test]
    fn atomic_swap_dirs_exchanges_trees_on_apfs() {
        let work = temp_test_dir("swap");
        let a = work.join("a");
        let b = work.join("b");
        fs::create_dir_all(&a).unwrap();
        fs::create_dir_all(&b).unwrap();
        fs::write(a.join("who.txt"), "aaa").unwrap();
        fs::write(b.join("who.txt"), "bbb").unwrap();
        let swapped = atomic_swap_dirs(&a, &b).expect("swap 调用不应报错");
        assert!(swapped, "本机 temp 卷应为 APFS,renamex_np 必须可用");
        assert_eq!(fs::read_to_string(a.join("who.txt")).unwrap(), "bbb");
        assert_eq!(fs::read_to_string(b.join("who.txt")).unwrap(), "aaa");
        // 禁用开关必须走回退分支(防两段 rename 回退路径死代码化)
        std::env::set_var("HOROSA_SWAP_DISABLE", "1");
        let disabled = atomic_swap_dirs(&a, &b).unwrap();
        std::env::remove_var("HOROSA_SWAP_DISABLE");
        assert!(!disabled, "HOROSA_SWAP_DISABLE=1 必须返回 false 走回退");
        let _ = fs::remove_dir_all(&work);
    }

    #[test]
    fn torn_slot_repair_promotes_complete_candidate() {
        // 场景1:current 缺失 + 仅 previous 完整 → 收养 previous
        let root1 = temp_test_dir("torn1");
        write_minimal_runtime_tree(&root1.join("previous"), "prev");
        assert!(repair_torn_runtime_slots(&root1).unwrap());
        assert!(root1.join("current/runtime-manifest.json").exists());
        assert!(!root1.join("previous").exists());

        // 场景2:_comp_stage(增量暂存,最新)优先于 previous;previous 保留作回滚资本
        let root2 = temp_test_dir("torn2");
        write_minimal_runtime_tree(&root2.join("_comp_stage"), "stage");
        write_minimal_runtime_tree(&root2.join("previous"), "prev");
        assert!(repair_torn_runtime_slots(&root2).unwrap());
        assert_eq!(
            fs::read_to_string(root2.join("current/Horosa-Web/astrostudyui/dist-file/index.html"))
                .unwrap(),
            "stage"
        );
        assert!(root2.join("previous").exists());

        // 场景3:_extract/runtime-payload(全量暂存)次优
        let root3 = temp_test_dir("torn3");
        write_minimal_runtime_tree(&root3.join("_extract/runtime-payload"), "extract");
        assert!(repair_torn_runtime_slots(&root3).unwrap());
        assert_eq!(
            fs::read_to_string(root3.join("current/Horosa-Web/astrostudyui/dist-file/index.html"))
                .unwrap(),
            "extract"
        );

        // 场景4:候选不完整(缺 java)绝不收养
        let root4 = temp_test_dir("torn4");
        write_minimal_runtime_tree(&root4.join("previous"), "broken");
        fs::remove_file(root4.join("previous/runtime/mac/java/bin/java")).unwrap();
        assert!(!repair_torn_runtime_slots(&root4).unwrap());
        assert!(!root4.join("current").exists());

        // 场景5:current 在位 → 零动作
        let root5 = temp_test_dir("torn5");
        write_minimal_runtime_tree(&root5.join("current"), "cur");
        write_minimal_runtime_tree(&root5.join("previous"), "prev");
        assert!(!repair_torn_runtime_slots(&root5).unwrap());
        assert_eq!(
            fs::read_to_string(root5.join("current/Horosa-Web/astrostudyui/dist-file/index.html"))
                .unwrap(),
            "cur"
        );
        for root in [root1, root2, root3, root4, root5] {
            let _ = fs::remove_dir_all(&root);
        }
    }

    // [U-E] 部件级重试矩阵:下载错(留 .part 续传接力)/sha 失配(清 dest 全新下)/耗尽上抛
    #[test]
    fn component_download_retry_then_success_and_exhaust() {
        let work = temp_test_dir("comp-retry");
        let dest = work.join("comp-x.tar.gz");
        // fail(下载),fail(校验),ok → 成功;共 3 次下载、2 次重试通知
        let calls = std::cell::Cell::new(0u32);
        let retries = std::cell::Cell::new(0u32);
        let result = download_component_with_retry(
            &dest,
            &mut || {
                calls.set(calls.get() + 1);
                fs::write(&dest, format!("payload-{}", calls.get())).unwrap();
                if calls.get() == 1 {
                    Err(anyhow!("network"))
                } else {
                    Ok(())
                }
            },
            &mut || {
                if calls.get() == 2 {
                    Err(anyhow!("sha mismatch"))
                } else {
                    Ok(())
                }
            },
            &mut |_| retries.set(retries.get() + 1),
        );
        assert!(result.is_ok());
        assert_eq!(calls.get(), 3);
        assert_eq!(retries.get(), 2);

        // 持续 sha 失配 → 1+COMPONENT_RETRY_MAX 次后 Err,坏资产不残留
        let fails = std::cell::Cell::new(0u32);
        let result = download_component_with_retry(
            &dest,
            &mut || {
                fails.set(fails.get() + 1);
                Ok(())
            },
            &mut || Err(anyhow!("sha mismatch")),
            &mut |_| {},
        );
        assert!(result.is_err());
        assert_eq!(fails.get(), 1 + COMPONENT_RETRY_MAX);
        assert!(!dest.exists(), "sha 失配路径必须清掉坏资产");
        let _ = fs::remove_dir_all(&work);
    }

    // [U-H] 节流三态:无 stamp=查;窗内=跳;窗外=查(interval 作参数传入,测试不碰 env)
    #[test]
    fn auto_check_throttle_gate() {
        let four_hours_ms: u64 = 4 * 3600 * 1000;
        let now: u64 = 1_000_000_000_000;
        assert!(should_run_auto_check(None, now, four_hours_ms));
        assert!(!should_run_auto_check(
            Some(now - 3 * 3600 * 1000),
            now,
            four_hours_ms
        ));
        assert!(should_run_auto_check(
            Some(now - 5 * 3600 * 1000),
            now,
            four_hours_ms
        ));
        // 恰在边界=可查;时钟倒拨(last>now)不 panic 且按窗内处理
        assert!(should_run_auto_check(
            Some(now - four_hours_ms),
            now,
            four_hours_ms
        ));
        assert!(!should_run_auto_check(
            Some(now + 60_000),
            now,
            four_hours_ms
        ));
    }

    #[test]
    fn update_check_stamp_roundtrip() {
        let work = temp_test_dir("check-stamp");
        let path = work.join("last-update-check.json");
        assert_eq!(load_update_check_stamp(&path), None);
        write_update_check_stamp_at(&path);
        let loaded = load_update_check_stamp(&path).expect("stamp 应可读回");
        assert!(loaded > 0);
        // 坏 JSON → None(自愈:下轮照常检查并重写)
        fs::write(&path, "not-json").unwrap();
        assert_eq!(load_update_check_stamp(&path), None);
        let _ = fs::remove_dir_all(&work);
    }

    // [U-C] staged 持久化门:往返/篡改一字节拒绝/复用门匹配
    #[test]
    fn staged_update_file_roundtrip_and_sha_gate() {
        let work = temp_test_dir("staged");
        let zip = work.join("app.zip");
        let comp = work.join("comp-web-app.tar.gz");
        fs::write(&zip, "zip-bytes").unwrap();
        fs::write(&comp, "comp-bytes").unwrap();
        let staged = StagedUpdate {
            zip_path: Some(zip.clone()),
            runtime_archive_path: None,
            runtime_roots: vec![work.join("root")],
            runtime_version: Some("9.9.9-runtime1".into()),
            target_version: "9.9.9".into(),
            app_should_update: true,
            runtime_should_update: true,
            staged_components: Some(StagedComponents {
                archives: vec![(
                    ManifestComponent {
                        name: "web-app".into(),
                        kind: "tree".into(),
                        sha256: "x".into(),
                        size: Some(1),
                        file: "comp-web-app.tar.gz".into(),
                        url: String::new(),
                    },
                    comp.clone(),
                )],
                new_lock_json: serde_json::json!({"runtimeVersion":"9.9.9-runtime1"}),
                new_lock_text: "{}".into(),
            }),
        };
        let file = work.join("staged-update.json");
        persist_staged_update_file_at(&file, &staged).expect("持久化应成功");
        let now = SystemTime::now()
            .duration_since(UNIX_EPOCH)
            .unwrap()
            .as_millis() as u64;
        let loaded = load_staged_update_file_at(&file, now).expect("原样资产应可恢复");
        assert_eq!(loaded.target_version, "9.9.9");
        assert!(staged_matches_plan(
            &loaded,
            "9.9.9",
            &Some("9.9.9-runtime1".into())
        ));
        assert!(!staged_matches_plan(
            &loaded,
            "9.9.10",
            &Some("9.9.9-runtime1".into())
        ));
        assert!(!staged_matches_plan(
            &loaded,
            "9.9.9",
            &Some("9.9.9-runtime2".into())
        ));
        // 篡改一个资产字节 → 拒绝复用
        fs::write(&comp, "comp-bytes-tampered").unwrap();
        assert!(load_staged_update_file_at(&file, now).is_none());
        let _ = fs::remove_dir_all(&work);
    }

    #[test]
    fn staged_update_expiry_discard() {
        let work = temp_test_dir("staged-exp");
        let zip = work.join("app.zip");
        fs::write(&zip, "zip").unwrap();
        let staged = StagedUpdate {
            zip_path: Some(zip),
            runtime_archive_path: None,
            runtime_roots: vec![],
            runtime_version: None,
            target_version: "9.9.9".into(),
            app_should_update: true,
            runtime_should_update: false,
            staged_components: None,
        };
        let file = work.join("staged-update.json");
        persist_staged_update_file_at(&file, &staged).unwrap();
        let now = SystemTime::now()
            .duration_since(UNIX_EPOCH)
            .unwrap()
            .as_millis() as u64;
        assert!(load_staged_update_file_at(&file, now).is_some());
        // 8 天后 → 过期废弃
        assert!(load_staged_update_file_at(&file, now + 8 * 24 * 3600 * 1000).is_none());
        // 无资产清单的档(异常构造)→ 拒绝
        fs::write(
            &file,
            serde_json::json!({
                "saved_at_ms": now,
                "staged": { "target_version": "9.9.9" },
                "asset_shas": []
            })
            .to_string(),
        )
        .unwrap();
        assert!(load_staged_update_file_at(&file, now).is_none());
        let _ = fs::remove_dir_all(&work);
    }

    // [U-F] 身份探针四分类:真 TcpListener 假服务(正确 JSON/陌生标记/不答话/不监听)
    #[test]
    fn identity_probe_classifies_squatter_and_silence() {
        use std::io::{Read, Write};
        let timeout = Duration::from_millis(800);
        // Ok:回正确身份 JSON(app 标记+nonce 全对)
        let ok_listener = std::net::TcpListener::bind("127.0.0.1:0").unwrap();
        let ok_port = ok_listener.local_addr().unwrap().port();
        let ok_thread = thread::spawn(move || {
            if let Ok((mut s, _)) = ok_listener.accept() {
                let mut buf = [0u8; 1024];
                let _ = s.read(&mut buf);
                let body = r#"{"app":"horosa-backend","proto":1,"nonce":"n-1"}"#;
                let resp = format!(
                    "HTTP/1.1 200 OK\r\nContent-Type: application/json\r\nContent-Length: {}\r\nConnection: close\r\n\r\n{}",
                    body.len(),
                    body
                );
                let _ = s.write_all(resp.as_bytes());
            }
        });
        assert_eq!(
            probe_identity(ok_port, "horosa-backend", "n-1", timeout, false),
            IdentityProbe::Ok
        );
        ok_thread.join().unwrap();

        // WrongIdentity:陌生 app 标记(毒 200 squatter)/ nonce 不符(别的实例)
        let sq = std::net::TcpListener::bind("127.0.0.1:0").unwrap();
        let sq_port = sq.local_addr().unwrap().port();
        let sq_thread = thread::spawn(move || {
            for _ in 0..2 {
                if let Ok((mut s, _)) = sq.accept() {
                    let mut buf = [0u8; 1024];
                    let _ = s.read(&mut buf);
                    let body = r#"{"app":"stranger","nonce":"zzz"}"#;
                    let resp = format!(
                        "HTTP/1.1 200 OK\r\nContent-Length: {}\r\nConnection: close\r\n\r\n{}",
                        body.len(),
                        body
                    );
                    let _ = s.write_all(resp.as_bytes());
                }
            }
        });
        assert_eq!(
            probe_identity(sq_port, "horosa-backend", "n-1", timeout, false),
            IdentityProbe::WrongIdentity
        );
        assert_eq!(
            probe_identity(sq_port, "stranger", "n-1", timeout, false),
            IdentityProbe::WrongIdentity
        );
        sq_thread.join().unwrap();

        // HttpSilent:端口在听但不答话(wedged 形态)
        let silent = std::net::TcpListener::bind("127.0.0.1:0").unwrap();
        let silent_port = silent.local_addr().unwrap().port();
        let silent_thread = thread::spawn(move || {
            if let Ok((s, _)) = silent.accept() {
                thread::sleep(Duration::from_millis(1200));
                drop(s);
            }
        });
        assert_eq!(
            probe_identity(silent_port, "horosa-backend", "n-1", timeout, false),
            IdentityProbe::HttpSilent
        );
        silent_thread.join().unwrap();

        // TcpDead:无人监听
        let dead_port = {
            let l = std::net::TcpListener::bind("127.0.0.1:0").unwrap();
            l.local_addr().unwrap().port()
        };
        assert_eq!(
            probe_identity(dead_port, "horosa-backend", "n-1", timeout, false),
            IdentityProbe::TcpDead
        );
    }

    // [U-F] 双 streak 状态机:快判/慢判/立即判/互清/Ok 归零
    #[test]
    fn supervisor_streak_state_machine() {
        let zero = SupervisorStreak::default();
        // Ok 全清零
        assert_eq!(
            supervisor_step(SupervisorStreak { dead: 1, silent: 3 }, IdentityProbe::Ok),
            (zero, false)
        );
        // TcpDead 连续 2 轮判亡
        let (s1, k1) = supervisor_step(zero, IdentityProbe::TcpDead);
        assert!(!k1);
        let (_, k2) = supervisor_step(s1, IdentityProbe::TcpDead);
        assert!(k2);
        // HttpSilent 连续 6 轮判亡
        let mut s = zero;
        for round in 1..=5u32 {
            let (next, kill) = supervisor_step(s, IdentityProbe::HttpSilent);
            s = next;
            assert!(!kill, "silent 第 {round} 轮不应判亡");
        }
        let (_, k6) = supervisor_step(s, IdentityProbe::HttpSilent);
        assert!(k6);
        // dead 与 silent 互清对方(交替抖动不误判)
        let (sd, _) = supervisor_step(
            SupervisorStreak { dead: 0, silent: 5 },
            IdentityProbe::TcpDead,
        );
        assert_eq!(sd.silent, 0);
        let (ss, _) = supervisor_step(
            SupervisorStreak { dead: 1, silent: 0 },
            IdentityProbe::HttpSilent,
        );
        assert_eq!(ss.dead, 0);
        // WrongIdentity 立即判亡
        assert!(supervisor_step(zero, IdentityProbe::WrongIdentity).1);
    }

    // [U-B] helper 模板契约:stage-first 序/swap 旗标/失败重开臂/磁盘预检/危险旧序零回潮
    #[test]
    fn update_helper_script_stages_before_swap() {
        let script = build_update_helper_script(
            Path::new("/tmp/log.txt"),
            Path::new("/tmp/marker.txt"),
            Path::new("/Applications/Demo.app"),
            Path::new("/tmp/extract/Demo.app"),
            "501",
            "demo",
            "1234",
            "demo-exec",
            "9.9.9",
            Some("9.9.9-runtime1"),
            "",
        );
        // stage-first:ditto 到暂存位必须先于任何对 TARGET 的 mv(长拷贝期间 TARGET 不动)
        let stage_at = script
            .find("ditto \"${SRC}\" \"${STAGE_TARGET}\"")
            .expect("缺 stage ditto");
        let mv_target_at = script
            .find("mv \"${TARGET}\" \"${BACKUP_TARGET}\"")
            .expect("缺 mv 回退");
        assert!(
            stage_at < mv_target_at,
            "ditto 必须先于 mv TARGET(stage-first)"
        );
        assert!(script.contains("--horosa-atomic-swap"));
        assert!(script.contains("update-stage.app"));
        // 失败臂:install 失败必须重开旧 app(而非 set -e 静默中止)
        assert!(script.contains("if ! install_app; then"));
        assert!(script.contains("reopening previous app"));
        // 磁盘预检在位
        assert!(script.contains("insufficient disk space"));
        // 危险旧序(把新版长时间 ditto 直写 TARGET)不得回潮
        assert!(!script.contains("ditto \"${SRC}\" \"${TARGET}\""));
    }

    #[test]
    fn atomic_swap_cli_flag_swaps_and_exits() {
        let work = temp_test_dir("swap-cli");
        let a = work.join("a.app");
        let b = work.join("b.app");
        fs::create_dir_all(&a).unwrap();
        fs::create_dir_all(&b).unwrap();
        fs::write(a.join("who.txt"), "new").unwrap();
        fs::write(b.join("who.txt"), "old").unwrap();
        assert_eq!(run_swap_cli(&a, &b), 0, "APFS 上应互换成功");
        assert_eq!(fs::read_to_string(b.join("who.txt")).unwrap(), "new");
        assert_eq!(fs::read_to_string(a.join("who.txt")).unwrap(), "old");
        // 入参路径缺失 → 2(helper 走 mv 回退的信号,非硬错误)
        assert_eq!(run_swap_cli(&work.join("nope"), &b), 2);
        let _ = fs::remove_dir_all(&work);
    }

    // [U-G] 台账追加+保尾轮转:超 1MB 保尾 200 行,新行在、头行不在,ts/shellVersion 自动补
    #[test]
    fn update_history_append_and_rotation_keeps_tail() {
        let work = temp_test_dir("uhist");
        let path = work.join("update-history.jsonl");
        append_update_history_at(&path, serde_json::json!({ "event": "staged_ready" }));
        let text = fs::read_to_string(&path).unwrap();
        assert!(text.contains("\"event\":\"staged_ready\""));
        assert!(text.contains("\"ts\":"));
        assert!(text.contains("\"shellVersion\":"));
        // 灌 >1MB 再追加 → 只留尾部+新行
        let filler: String = (0..40000)
            .map(|i| format!("{{\"event\":\"filler\",\"n\":{i}}}\n"))
            .collect();
        fs::write(&path, filler).unwrap();
        assert!(fs::metadata(&path).unwrap().len() > 1024 * 1024);
        append_update_history_at(&path, serde_json::json!({ "event": "install_confirmed" }));
        let text = fs::read_to_string(&path).unwrap();
        let lines: Vec<&str> = text.lines().collect();
        assert!(lines.len() <= 201, "保尾 200+新 1 行,实际 {}", lines.len());
        assert!(text.contains("install_confirmed"));
        assert!(!text.contains("\"n\":0}"), "头行必须被轮转掉");
        assert!(text.contains("\"n\":39999"), "尾行必须保留");
        let _ = fs::remove_dir_all(&work);
    }

    // [U-G] events 轮转保代:超限 rename→.1 保旧史(不再截断毁证)
    #[test]
    fn rotate_log_keep_one_generation() {
        let work = temp_test_dir("rotlog");
        let path = work.join("updater-events.log");
        fs::write(&path, "old-history\n".repeat(1000)).unwrap();
        // 未超限:不动
        rotate_log_keep_one(&path, 1024 * 1024);
        assert!(path.exists());
        assert!(!path.with_extension("log.1").exists());
        // 超限:rename → .1,主文件让位(调用方新建续写)
        rotate_log_keep_one(&path, 100);
        let older = path.with_extension("log.1");
        assert!(older.exists(), ".1 保代必须存在");
        assert!(!path.exists(), "主文件应让位");
        assert!(fs::read_to_string(&older).unwrap().contains("old-history"));
        let _ = fs::remove_dir_all(&work);
    }

    // [U-G] 诊断包 ditto 实跑:zip 产出且内容在包内
    #[test]
    fn diagnostics_bundle_staging_collects_expected_files() {
        let work = temp_test_dir("diagzip");
        let staging = work.join("staging");
        fs::create_dir_all(staging.join("logs")).unwrap();
        fs::write(staging.join("logs/update-history.jsonl"), "{}\n").unwrap();
        fs::write(staging.join("system-info.txt"), "app=test\n").unwrap();
        let out = work.join("bundle.zip");
        zip_dir_with_ditto(&staging, &out).expect("ditto 打包应成功");
        assert!(out.exists());
        let listing = Command::new("/usr/bin/unzip")
            .arg("-l")
            .arg(&out)
            .output()
            .expect("unzip -l");
        let text = String::from_utf8_lossy(&listing.stdout);
        assert!(text.contains("update-history.jsonl"));
        assert!(text.contains("system-info.txt"));
        let _ = fs::remove_dir_all(&work);
    }

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
        assert_eq!(state.state_version, None);
        assert_eq!(state.coordinate_space, None);
    }

    #[test]
    fn legacy_main_window_state_keeps_saved_size() {
        let state = SavedWindowState {
            width: Some(1480.0),
            height: Some(960.0),
            x: Some(120.0),
            y: Some(80.0),
            is_maximized: None,
            ..SavedWindowState::default()
        };

        assert!(!should_launch_main_window_maximized(&state));
    }

    #[test]
    fn legacy_retina_window_state_migrates_physical_pixels_to_logical_size() {
        let state = SavedWindowState {
            width: Some(2960.0),
            height: Some(1920.0),
            x: Some(240.0),
            y: Some(160.0),
            is_maximized: Some(false),
            state_version: None,
            coordinate_space: None,
        };

        let normalized =
            normalize_saved_window_state_for_apply(&state, 2.0, Some(1512.0), Some(982.0));

        assert_eq!(normalized.width, Some(1480.0));
        assert_eq!(normalized.height, Some(932.0));
        assert_eq!(normalized.x, Some(120.0));
        assert_eq!(normalized.y, Some(80.0));
        assert_eq!(normalized.state_version, Some(WINDOW_STATE_SCHEMA_VERSION));
        assert_eq!(
            normalized.coordinate_space.as_deref(),
            Some(WINDOW_STATE_COORDINATE_SPACE)
        );
    }

    #[test]
    fn logical_window_state_is_not_rescaled_on_retina_displays() {
        let state = SavedWindowState {
            width: Some(1480.0),
            height: Some(960.0),
            x: Some(120.0),
            y: Some(80.0),
            is_maximized: Some(false),
            state_version: Some(WINDOW_STATE_SCHEMA_VERSION),
            coordinate_space: Some(WINDOW_STATE_COORDINATE_SPACE.to_string()),
        };

        let normalized =
            normalize_saved_window_state_for_apply(&state, 2.0, Some(1512.0), Some(982.0));

        assert_eq!(normalized.width, Some(1480.0));
        assert_eq!(normalized.height, Some(960.0));
        assert_eq!(normalized.x, Some(120.0));
        assert_eq!(normalized.y, Some(80.0));
    }

    #[test]
    fn invalid_scale_factor_falls_back_to_one() {
        assert_eq!(valid_scale_factor(0.0), 1.0);
        assert_eq!(valid_scale_factor(f64::NAN), 1.0);
        assert_eq!(logical_value(960.0, 0.0), 960.0);
    }

    #[test]
    fn explicit_non_maximized_state_is_respected() {
        let state = SavedWindowState {
            is_maximized: Some(false),
            ..SavedWindowState::default()
        };

        assert!(!should_launch_main_window_maximized(&state));
    }

    #[test]
    fn explicit_maximized_state_restores_saved_bounds_without_native_zoom() {
        let state = SavedWindowState {
            is_maximized: Some(true),
            ..SavedWindowState::default()
        };

        assert!(!should_launch_main_window_maximized(&state));
    }

    #[test]
    fn captured_maximized_state_keeps_true_for_monitor_sized_bounds() {
        assert_eq!(
            effective_captured_maximized(
                Some(true),
                Some(1728.0),
                Some(1079.0),
                Some(1728.0),
                Some(1117.0)
            ),
            Some(true)
        );
    }

    #[test]
    fn captured_maximized_state_is_cleared_for_user_resized_bounds() {
        assert_eq!(
            effective_captured_maximized(
                Some(true),
                Some(1420.0),
                Some(880.0),
                Some(1728.0),
                Some(1117.0)
            ),
            Some(false)
        );
    }

    #[test]
    fn saved_launch_size_uses_logical_saved_bounds_before_window_is_shown() {
        let state = SavedWindowState {
            width: Some(1320.0),
            height: Some(840.0),
            x: Some(180.0),
            y: Some(120.0),
            is_maximized: Some(false),
            state_version: Some(WINDOW_STATE_SCHEMA_VERSION),
            coordinate_space: Some(WINDOW_STATE_COORDINATE_SPACE.to_string()),
        };

        assert_eq!(
            saved_launch_size(&state, MAIN_WINDOW_DEFAULT_SIZE, MAIN_WINDOW_MIN_SIZE),
            (1320.0, 840.0)
        );
        assert_eq!(saved_launch_position(&state), Some((180.0, 120.0)));
    }

    #[test]
    fn desktop_init_script_prevents_frontend_window_resize_fights() {
        assert!(DESKTOP_WINDOW_INIT_SCRIPT.contains("__HOROSA_DESKTOP_SHELL__"));
        assert!(DESKTOP_WINDOW_INIT_SCRIPT.contains("resizeTo"));
        assert!(DESKTOP_WINDOW_INIT_SCRIPT.contains("moveTo"));
    }

    #[cfg(target_os = "macos")]
    #[test]
    fn legacy_macos_defaults_cleanup_targets_old_main_workspace_frames() {
        assert!(LEGACY_MACOS_WINDOW_DEFAULT_KEYS.contains(&"NSWindow Frame main-workspace"));
        assert!(LEGACY_MACOS_WINDOW_DEFAULT_KEYS
            .contains(&"NSSplitView Subview Frames main-workspace, SidebarNavigationSplitView"));
        assert!(LEGACY_MACOS_WINDOW_DEFAULT_KEYS
            .iter()
            .any(|key| key.contains("Horosa.RootWorkspaceView")));
    }

    #[test]
    fn saved_launch_size_ignores_legacy_bounds_but_uses_maximized_saved_bounds() {
        let legacy_state = SavedWindowState {
            width: Some(2960.0),
            height: Some(1920.0),
            is_maximized: Some(false),
            ..SavedWindowState::default()
        };
        let maximized_state = SavedWindowState {
            width: Some(1320.0),
            height: Some(840.0),
            is_maximized: Some(true),
            state_version: Some(WINDOW_STATE_SCHEMA_VERSION),
            coordinate_space: Some(WINDOW_STATE_COORDINATE_SPACE.to_string()),
            ..SavedWindowState::default()
        };

        assert_eq!(
            saved_launch_size(
                &legacy_state,
                MAIN_WINDOW_DEFAULT_SIZE,
                MAIN_WINDOW_MIN_SIZE
            ),
            MAIN_WINDOW_DEFAULT_SIZE
        );
        assert_eq!(
            saved_launch_size(
                &maximized_state,
                MAIN_WINDOW_DEFAULT_SIZE,
                MAIN_WINDOW_MIN_SIZE
            ),
            (1320.0, 840.0)
        );
    }

    #[test]
    fn maximized_launch_uses_saved_bounds_as_builder_size() {
        let state = SavedWindowState {
            width: Some(1728.0),
            height: Some(1079.0),
            x: Some(0.0),
            y: Some(38.0),
            is_maximized: Some(true),
            state_version: Some(WINDOW_STATE_SCHEMA_VERSION),
            coordinate_space: Some(WINDOW_STATE_COORDINATE_SPACE.to_string()),
        };

        assert_eq!(
            saved_launch_size(&state, MAIN_WINDOW_DEFAULT_SIZE, MAIN_WINDOW_MIN_SIZE),
            (1728.0, 1079.0)
        );
        assert_eq!(saved_launch_position(&state), Some((0.0, 38.0)));
    }

    #[test]
    fn previous_maximized_outer_size_state_launches_with_inner_height() {
        let state = SavedWindowState {
            width: Some(1728.0),
            height: Some(1079.0),
            x: Some(-1.0),
            y: Some(38.0),
            is_maximized: Some(true),
            state_version: Some(2),
            coordinate_space: Some(WINDOW_STATE_COORDINATE_SPACE.to_string()),
        };

        assert_eq!(
            saved_launch_size(&state, MAIN_WINDOW_DEFAULT_SIZE, MAIN_WINDOW_MIN_SIZE),
            (1728.0, 1051.0)
        );
        assert_eq!(saved_launch_position(&state), Some((-1.0, 38.0)));
        assert!(!should_launch_main_window_maximized(&state));
    }

    #[test]
    fn previous_logical_outer_size_state_is_converted_to_inner_height_for_launch() {
        let state = SavedWindowState {
            width: Some(1260.0),
            height: Some(820.0),
            x: Some(260.0),
            y: Some(160.0),
            is_maximized: Some(false),
            state_version: Some(2),
            coordinate_space: Some(WINDOW_STATE_COORDINATE_SPACE.to_string()),
        };

        assert_eq!(
            saved_launch_size(&state, MAIN_WINDOW_DEFAULT_SIZE, MAIN_WINDOW_MIN_SIZE),
            (1260.0, 792.0)
        );
        assert_eq!(saved_launch_position(&state), Some((260.0, 160.0)));
    }

    #[test]
    fn frontend_url_injects_chart_service_for_packaged_kentang_routes() {
        let url = frontend_url(38991, 63968, 63967);

        assert!(url.contains("srv=http%3A%2F%2F127.0.0.1%3A63968"));
        assert!(url.contains("chartSrv=http%3A%2F%2F127.0.0.1%3A63967"));
        assert!(url.contains("kentangSrv=http%3A%2F%2F127.0.0.1%3A63967"));
        // 身份握手会话 nonce:必在 URL,且同壳进程内稳定复用(重启后端不换值)。
        assert!(url.contains(&format!("sid={}", launch_nonce())));
    }

    #[test]
    fn launch_nonce_is_stable_and_url_safe() {
        let a = launch_nonce();
        let b = launch_nonce();
        assert_eq!(a, b, "同壳会话内 nonce 必须稳定(重启后端复用)");
        assert_eq!(a.len(), 16);
        assert!(a.chars().all(|c| c.is_ascii_hexdigit()));
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
            format!(
                "{{\"version\":\"{}\",\"built_at\":\"2026-04-07 00:00:00\"}}\n",
                version
            ),
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

    #[cfg(unix)]
    fn create_usable_runtime_archive(root: &Path, version: &str) -> PathBuf {
        let payload_root = root.join("usable/runtime-payload");
        let runtime_dir = payload_root;
        fs::create_dir_all(runtime_dir.join("Horosa-Web/astrostudyui/dist-file")).unwrap();
        fs::write(
            runtime_dir.join("runtime-manifest.json"),
            format!(
                "{{\"version\":\"{}\",\"built_at\":\"2026-04-07 00:00:00\"}}\n",
                version
            ),
        )
        .unwrap();
        fs::write(
            runtime_dir.join("Horosa-Web/start_horosa_local.sh"),
            "#!/bin/sh\n",
        )
        .unwrap();
        fs::write(
            runtime_dir.join("Horosa-Web/astrostudyui/dist-file/index.html"),
            "<html></html>\n",
        )
        .unwrap();
        write_stub_executable(&runtime_dir.join("runtime/mac/python/bin/python3"));
        write_stub_executable(&runtime_dir.join("runtime/mac/java/bin/java"));
        let archive_path = root.join("usable-runtime.tar.gz");
        let tar_gz = File::create(&archive_path).unwrap();
        let encoder = GzEncoder::new(tar_gz, Compression::default());
        let mut builder = Builder::new(encoder);
        builder
            .append_dir_all("runtime-payload", runtime_dir)
            .unwrap();
        builder.finish().unwrap();
        archive_path
    }

    #[cfg(unix)]
    fn write_stub_executable(path: &Path) {
        if let Some(parent) = path.parent() {
            fs::create_dir_all(parent).unwrap();
        }
        fs::write(path, "#!/bin/sh\nexit 0\n").unwrap();
        let mut perms = fs::metadata(path).unwrap().permissions();
        perms.set_mode(0o755);
        fs::set_permissions(path, perms).unwrap();
    }

    #[cfg(unix)]
    fn create_fake_runtime_tree(root: &Path, version: &str, with_java: bool) -> PathBuf {
        let runtime_dir = root.join("runtime/current");
        fs::create_dir_all(runtime_dir.join("Horosa-Web/astrostudyui/dist-file")).unwrap();
        fs::write(
            runtime_dir.join("runtime-manifest.json"),
            format!(
                "{{\"version\":\"{}\",\"built_at\":\"2026-04-07 00:00:00\"}}\n",
                version
            ),
        )
        .unwrap();
        fs::write(
            runtime_dir.join("Horosa-Web/start_horosa_local.sh"),
            "#!/bin/sh\n",
        )
        .unwrap();
        fs::write(
            runtime_dir.join("Horosa-Web/astrostudyui/dist-file/index.html"),
            "<html></html>\n",
        )
        .unwrap();
        write_stub_executable(&runtime_dir.join("runtime/mac/python/bin/python3"));
        if with_java {
            write_stub_executable(&runtime_dir.join("runtime/mac/java/bin/java"));
        }
        runtime_dir
    }

    #[test]
    fn runtime_update_command_uses_shell_resolved_manifest_path() {
        let _env = HELPER_ENV_LOCK.lock().unwrap_or_else(|e| e.into_inner());
        let runtime_root = Path::new("/tmp/horosa-runtime-root");
        let archive = Path::new("/tmp/horosa-runtime.tar.gz");
        // 默认新协议:手术经 TARGET 新二进制(--horosa-runtime-swap),模板层只定义不执行
        let command = build_runtime_update_command(
            &[runtime_root.to_path_buf()],
            archive,
            Some("1.0.19-runtime1"),
        );
        assert!(command.contains("--horosa-runtime-swap"));
        assert!(command.contains("run_runtime_installs() {"));
        assert!(!command.contains("mv \"${WORK_ROOT}/runtime-payload\""));
        // 旧协议(逃生阀)保留 shell 原生 plutil 解析,零 python 依赖
        let legacy = build_single_runtime_update_command_legacy(
            runtime_root,
            archive,
            Some("1.0.19-runtime1"),
            0,
        );
        assert!(legacy.contains(
            "ACTUAL_RUNTIME_VERSION=\"$(/usr/bin/plutil -extract version raw -o - \"${WORK_ROOT}/runtime-payload/runtime-manifest.json\" 2>/dev/null || true)\""
        ));
        assert!(!legacy
            .contains("pathlib.Path(r\"${WORK_ROOT}/runtime-payload/runtime-manifest.json\")"));
    }

    #[test]
    fn runtime_update_command_legacy_extracts_and_switches_payload() {
        // 旧协议(HOROSA_HELPER_RUNTIME_SWAP=0 逃生阀)功能保真:自包含 bash 原地可跑。
        // 新协议的功能等价物 = run_runtime_swap_cli(见 runtime_swap_cli_* 测试)。
        let root = temp_test_dir("runtime-update-helper");
        let runtime_root = root.join("shared/runtime");
        let archive = create_runtime_archive(&root, "1.0.19-runtime1");
        let command = build_single_runtime_update_command_legacy(
            &runtime_root,
            &archive,
            Some("1.0.19-runtime1"),
            0,
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

    // HOROSA_HELPER_RUNTIME_SWAP 是进程级 env:读它的模板测试与设它的 killswitch
    // 测试并行会互毒 → 共用一把测试锁串行化(поisoned 也继续,锁只为互斥不为状态)。
    static HELPER_ENV_LOCK: std::sync::Mutex<()> = std::sync::Mutex::new(());

    // 新协议 helper 模板契约:定义不执行 / wait→app→runtime 时序 / 危险旧序零回潮
    #[test]
    fn update_helper_script_runtime_swap_after_wait_and_app() {
        let _env = HELPER_ENV_LOCK.lock().unwrap_or_else(|e| e.into_inner());
        let runtime_cmd = build_runtime_update_command(
            &[PathBuf::from("/Users/Shared/HorosaTest/runtime")],
            Path::new("/tmp/runtime.tar.gz"),
            Some("9.9.9-runtime1"),
        );
        let script = build_update_helper_script(
            Path::new("/tmp/log.txt"),
            Path::new("/tmp/marker.txt"),
            Path::new("/Applications/Demo.app"),
            Path::new("/tmp/extract/Demo.app"),
            "501",
            "demo",
            "1234",
            "demo-exec",
            "9.9.9",
            Some("9.9.9-runtime1"),
            &runtime_cmd,
        );
        assert!(
            script.contains("--horosa-runtime-swap"),
            "新协议必须经 TARGET 二进制做 runtime 对换"
        );
        // 旧危险序零回潮(默认脚本不得再出现两段 mv 序/成功即删 previous)
        assert!(!script.contains("mv \"${WORK_ROOT}/runtime-payload\""));
        assert!(!script.contains("rm -rf \"${WORK_ROOT}\" \"${PREVIOUS_ROOT}\""));
        // 时序:定义(install_runtime_0)→ wait 调用 → install_app 调用 → run_runtime_installs 调用
        let def_at = script
            .find("install_runtime_0() {")
            .expect("缺 runtime 安装函数定义");
        let wait_call_at = script
            .rfind("\nwait_for_old_app_exit\n")
            .expect("缺 wait 裸调用");
        let app_call_at = script
            .find("if ! install_app; then")
            .expect("缺 install_app 调用");
        let runtime_call_at = script
            .find("if ! run_runtime_installs; then")
            .expect("缺 run_runtime_installs 调用");
        assert!(def_at < wait_call_at, "runtime_cmd 必须只定义不执行");
        assert!(
            wait_call_at < app_call_at && app_call_at < runtime_call_at,
            "顺序必须 wait→app→runtime"
        );
    }

    // 铁律14:runtime 失败臂(exit 73)绝不写完成标记,重开用 open_app_once(open_app 会 mark)
    #[test]
    fn update_helper_runtime_failure_arm_never_marks() {
        let _env = HELPER_ENV_LOCK.lock().unwrap_or_else(|e| e.into_inner());
        let runtime_cmd = build_runtime_update_command(
            &[PathBuf::from("/Users/Shared/HorosaTest/runtime")],
            Path::new("/tmp/runtime.tar.gz"),
            Some("9.9.9-runtime1"),
        );
        let script = build_update_helper_script(
            Path::new("/tmp/log.txt"),
            Path::new("/tmp/marker.txt"),
            Path::new("/Applications/Demo.app"),
            Path::new("/tmp/extract/Demo.app"),
            "501",
            "demo",
            "1234",
            "demo-exec",
            "9.9.9",
            Some("9.9.9-runtime1"),
            &runtime_cmd,
        );
        let arm_start = script.find("if ! run_runtime_installs; then").unwrap();
        let arm_end = arm_start + script[arm_start..].find("exit 73").expect("缺 exit 73 臂");
        let arm = &script[arm_start..arm_end];
        assert!(
            !arm.contains("mark_update_complete"),
            "runtime 失败臂不得写完成标记"
        );
        assert!(arm.contains("open_app_once"), "失败臂用 open_app_once 重开");
        // 成功路径的 mark 必须在失败臂之后(即 run_runtime_installs 通过才 mark)
        let mark_at = script
            .rfind("mark_update_complete \"pending_manual\"")
            .unwrap();
        assert!(arm_end < mark_at);
    }

    // kill-switch:生成端回旧模板(证明开关真实闭环)
    #[test]
    fn update_helper_legacy_killswitch_restores_old_template() {
        let _env = HELPER_ENV_LOCK.lock().unwrap_or_else(|e| e.into_inner());
        std::env::set_var("HOROSA_HELPER_RUNTIME_SWAP", "0");
        let legacy = build_runtime_update_command(
            &[PathBuf::from("/Users/Shared/HorosaTest/runtime")],
            Path::new("/tmp/runtime.tar.gz"),
            Some("9.9.9-runtime1"),
        );
        std::env::remove_var("HOROSA_HELPER_RUNTIME_SWAP");
        assert!(
            legacy.contains("mv \"${WORK_ROOT}/runtime-payload\""),
            "开关下必须回旧模板"
        );
        assert!(!legacy.contains("--horosa-runtime-swap"));
        assert!(
            !legacy.contains("run_runtime_installs() {"),
            "旧模板不覆盖 run_runtime_installs(走默认空实现)"
        );
    }

    // helper 真执行演练:生成的脚本用 /bin/bash 实跑——文本契约测不出
    // set -euo pipefail 下的真实执行语义(函数定义顺序/失败臂 exit 码/标记纪律)。
    // 只换三个 GUI 命令(open/pgrep/osascript)为桩,mv/ditto/kill/df 全真;
    // 手术本体行为由 runtime_swap_cli_* 测试真实覆盖,此处桩只回执 exit 码。
    struct HelperExecFixture {
        root: PathBuf,
        script_path: PathBuf,
        log: PathBuf,
        marker: PathBuf,
        target_payload: PathBuf,
        calls: PathBuf,
        path_env: String,
    }

    fn write_exec_stub(path: &Path, body: &str) {
        use std::os::unix::fs::PermissionsExt;
        fs::write(path, body).unwrap();
        fs::set_permissions(path, fs::Permissions::from_mode(0o755)).unwrap();
    }

    fn build_helper_exec_fixture(name: &str, swap_exit: i32, old_pid: &str) -> HelperExecFixture {
        let root = temp_test_dir(name);
        let stub = root.join("stub");
        fs::create_dir_all(&stub).unwrap();
        let calls = root.join("calls.log");
        fs::write(&calls, "").unwrap();
        // 裸 sleep 走 PATH:压缩等待窗(60 轮×0.05s 仍足够旧进程真实退出)
        write_exec_stub(&stub.join("sleep"), "#!/bin/bash\n/bin/sleep 0.05\n");
        write_exec_stub(
            &stub.join("open"),
            &format!("#!/bin/bash\necho \"open $*\" >> {}\nexit 0\n", calls.display()),
        );
        write_exec_stub(&stub.join("osascript"), "#!/bin/bash\nexit 0\n");
        write_exec_stub(
            &stub.join("pgrep"),
            &format!("#!/bin/bash\necho \"pgrep $*\" >> {}\nexit 0\n", calls.display()),
        );
        // SRC 新 app 骨架:exec 桩处理两个子命令(atomic-swap 拒→逼 mv 回退;runtime-swap 落参回执)
        let src_app = root.join("src/Horosa.app");
        fs::create_dir_all(src_app.join("Contents/MacOS")).unwrap();
        fs::create_dir_all(src_app.join("Contents/Resources")).unwrap();
        write_exec_stub(
            &src_app.join("Contents/MacOS/horosa-exec"),
            &format!(
                "#!/bin/bash\ncase \"${{1:-}}\" in\n  --horosa-atomic-swap) exit 1 ;;\n  --horosa-runtime-swap) echo \"swap-args $2 $3 $4\" >> {}\n    exit {} ;;\nesac\nexit 0\n",
                calls.display(),
                swap_exit
            ),
        );
        fs::write(src_app.join("Contents/Resources/payload.txt"), "new").unwrap();
        // TARGET 旧 app(mv 回退路径要求它在位)
        let target_app = root.join("Applications/Horosa.app");
        fs::create_dir_all(target_app.join("Contents/MacOS")).unwrap();
        fs::create_dir_all(target_app.join("Contents/Resources")).unwrap();
        write_exec_stub(&target_app.join("Contents/MacOS/horosa-exec"), "#!/bin/bash\nexit 0\n");
        fs::write(target_app.join("Contents/Resources/payload.txt"), "old").unwrap();

        let runtime_cmd = {
            let _env = HELPER_ENV_LOCK.lock().unwrap_or_else(|e| e.into_inner());
            std::env::set_var("HOROSA_HELPER_RUNTIME_SWAP", "1");
            let cmd = build_runtime_update_command(
                &[root.join("runtime")],
                &root.join("runtime.tar.gz"),
                Some("9.9.9-runtime1"),
            );
            std::env::remove_var("HOROSA_HELPER_RUNTIME_SWAP");
            cmd
        };
        let log = root.join("update.log");
        let marker = root.join("update-complete.txt");
        let uid = unsafe { libc::getuid() }.to_string();
        let script = build_update_helper_script(
            &log,
            &marker,
            &target_app,
            &src_app,
            &uid,
            "helper-exec-test",
            old_pid,
            "horosa-exec",
            "9.9.9",
            Some("9.9.9-runtime1"),
            &runtime_cmd,
        )
        .replace("/usr/bin/open", &stub.join("open").display().to_string())
        .replace("/usr/bin/pgrep", &stub.join("pgrep").display().to_string())
        .replace(
            "/usr/bin/osascript",
            &stub.join("osascript").display().to_string(),
        );
        let script_path = root.join("helper.sh");
        fs::write(&script_path, script).unwrap();
        HelperExecFixture {
            path_env: format!("{}:/usr/bin:/bin:/usr/sbin:/sbin", stub.display()),
            target_payload: target_app.join("Contents/Resources/payload.txt"),
            root,
            script_path,
            log,
            marker,
            calls,
        }
    }

    fn run_helper_script(fx: &HelperExecFixture) -> i32 {
        Command::new("/bin/bash")
            .arg(&fx.script_path)
            .env("PATH", &fx.path_env)
            .status()
            .expect("run helper script")
            .code()
            .unwrap_or(-1)
    }

    #[test]
    fn update_helper_exec_happy_path_orders_wait_app_runtime_then_marks() {
        // 真旧进程:0.3s 后退出,验证 wait_for_old_app_exit 真的等到了它。
        // 必须即时收尸(僵尸 pid 对 kill -0 恒真,会骗过等待循环)→ 独立线程 wait()。
        let mut old = Command::new("/bin/sleep").arg("0.3").spawn().unwrap();
        let old_pid = old.id().to_string();
        let reaper = std::thread::spawn(move || {
            let _ = old.wait();
        });
        let fx = build_helper_exec_fixture("helper-exec-happy", 0, &old_pid);
        let code = run_helper_script(&fx);
        let _ = reaper.join();
        let log = fs::read_to_string(&fx.log).unwrap_or_default();
        let calls = fs::read_to_string(&fx.calls).unwrap_or_default();
        assert_eq!(code, 0, "log:\n{log}\ncalls:\n{calls}");
        assert!(log.contains("[app] old process exited"), "必须真等旧进程退出:\n{log}");
        let i_install = log.find("[app] install succeeded").expect("app 安装日志");
        assert!(log.contains("update helper success"));
        let swap_line = calls
            .lines()
            .find(|l| l.starts_with("swap-args"))
            .expect("runtime swap 必须被调用");
        assert!(
            swap_line.contains("9.9.9-runtime1") && swap_line.contains("runtime.tar.gz"),
            "swap 参数错:{swap_line}"
        );
        // 时序:app 安装成功日志先于 runtime 失败探测日志区(swap 在 install 之后才可能出现)
        let i_runtime_log = log.find("===== update helper success").unwrap();
        assert!(i_install < i_runtime_log);
        let marker = fs::read_to_string(&fx.marker).expect("成功路必须写完成标记");
        assert!(marker.contains("relaunch_status=auto_relaunch_confirmed"), "{marker}");
        assert_eq!(fs::read_to_string(&fx.target_payload).unwrap(), "new");
        let _ = fs::remove_dir_all(&fx.root);
    }

    #[test]
    fn update_helper_exec_runtime_failure_exits_73_without_marker() {
        let fx = build_helper_exec_fixture("helper-exec-rtfail", 1, "0");
        let code = run_helper_script(&fx);
        let log = fs::read_to_string(&fx.log).unwrap_or_default();
        assert_eq!(code, 73, "runtime 失败臂必须 exit 73:\n{log}");
        assert!(log.contains("[runtime] runtime install failed"));
        assert!(
            !fx.marker.exists(),
            "runtime 失败绝不写完成标记(铁律14)"
        );
        // 新 app 已上位(修复机器在场)+ 已尝试重开
        assert_eq!(fs::read_to_string(&fx.target_payload).unwrap(), "new");
        let calls = fs::read_to_string(&fx.calls).unwrap_or_default();
        assert!(calls.lines().any(|l| l.starts_with("open ")), "失败臂必须重开 app");
        let _ = fs::remove_dir_all(&fx.root);
    }

    #[test]
    fn update_helper_exec_app_install_failure_exits_71_keeps_old_app() {
        let fx = build_helper_exec_fixture("helper-exec-appfail", 0, "0");
        // 挖掉 SRC → ditto 永败 → install_app 失败臂
        fs::remove_dir_all(fx.root.join("src")).unwrap();
        let code = run_helper_script(&fx);
        let log = fs::read_to_string(&fx.log).unwrap_or_default();
        assert_eq!(code, 71, "app 安装失败臂必须 exit 71:\n{log}");
        assert!(!fx.marker.exists(), "安装失败绝不写完成标记");
        assert_eq!(
            fs::read_to_string(&fx.target_payload).unwrap(),
            "old",
            "旧 app 必须完好"
        );
        let calls = fs::read_to_string(&fx.calls).unwrap_or_default();
        assert!(
            !calls.contains("swap-args"),
            "app 未装成绝不能碰 runtime"
        );
        let _ = fs::remove_dir_all(&fx.root);
    }

    // CLI 手术版本闸:归档 manifest 与期望不符 → 失败且 current 纹丝不动、半成品清净
    #[test]
    fn runtime_swap_cli_rejects_version_mismatch() {
        let root = temp_test_dir("runtime-swap-cli-vgate");
        let runtime_root = root.join("runtime");
        write_minimal_runtime_tree(&runtime_root.join("current"), "old");
        let archive = create_runtime_archive(&root, "2.0.0-runtime1");
        let code = run_runtime_swap_cli(&runtime_root, &archive, "9.9.9-runtime1");
        assert_eq!(code, 1, "版本不符必须失败");
        assert_eq!(
            fs::read_to_string(
                runtime_root.join("current/Horosa-Web/astrostudyui/dist-file/index.html")
            )
            .unwrap(),
            "old"
        );
        assert!(!runtime_root.join("_extract").exists(), "半成品必须清");
        let _ = fs::remove_dir_all(&root);
    }

    // CLI 手术成功路:新树上位 + previous 保留到首次 ready(看门狗回滚资本)
    #[test]
    fn runtime_swap_cli_promotes_and_keeps_previous() {
        let root = temp_test_dir("runtime-swap-cli-promote");
        let runtime_root = root.join("runtime");
        write_minimal_runtime_tree(&runtime_root.join("current"), "old");
        let archive = create_runtime_archive(&root, "2.0.0-runtime1");
        let code = run_runtime_swap_cli(&runtime_root, &archive, "2.0.0-runtime1");
        assert_eq!(code, 0);
        let manifest =
            fs::read_to_string(runtime_root.join("current/runtime-manifest.json")).unwrap();
        assert!(manifest.contains("2.0.0-runtime1"));
        assert!(
            runtime_root.join("previous").exists(),
            "previous 必须保留(绝不像旧协议成功即删)"
        );
        assert_eq!(
            fs::read_to_string(
                runtime_root.join("previous/Horosa-Web/astrostudyui/dist-file/index.html")
            )
            .unwrap(),
            "old"
        );
        let _ = fs::remove_dir_all(&root);
    }

    // 旧协议(过渡跳)暂存 _update/runtime-payload:断电撕裂时可被收养,不再成孤儿
    #[test]
    fn repair_torn_slots_adopts_legacy_update_dir() {
        let root = temp_test_dir("torn-legacy-update");
        write_minimal_runtime_tree(&root.join("_update/runtime-payload"), "legacy-stage");
        assert!(repair_torn_runtime_slots(&root).unwrap());
        assert_eq!(
            fs::read_to_string(root.join("current/Horosa-Web/astrostudyui/dist-file/index.html"))
                .unwrap(),
            "legacy-stage"
        );
        let _ = fs::remove_dir_all(&root);
    }

    // 孤儿清扫:新鲜暂存/撕裂态零动作;仅清 24h 以上陈旧目录
    #[test]
    fn sweep_stale_stage_dirs_only_removes_old() {
        let root = temp_test_dir("sweep-stale");
        write_minimal_runtime_tree(&root.join("current"), "cur");
        fs::create_dir_all(root.join("_update/runtime-payload")).unwrap();
        fs::create_dir_all(root.join("_extract/runtime-payload")).unwrap();
        sweep_stale_runtime_stage_dirs(&root);
        assert!(root.join("_update").exists(), "新鲜目录绝不清");
        assert!(root.join("_extract").exists());
        // mtime 拨回 2020 → 判陈旧,必须清
        let _ = Command::new("/usr/bin/touch")
            .args(["-t", "202001010000"])
            .arg(root.join("_update"))
            .status();
        sweep_stale_runtime_stage_dirs(&root);
        assert!(!root.join("_update").exists(), "陈旧 _update 必须被清扫");
        assert!(root.join("_extract").exists(), "新鲜 _extract 仍不动");
        // 无 current(撕裂态)零动作,交给收养
        let root2 = temp_test_dir("sweep-torn");
        fs::create_dir_all(root2.join("_update/runtime-payload")).unwrap();
        let _ = Command::new("/usr/bin/touch")
            .args(["-t", "202001010000"])
            .arg(root2.join("_update"))
            .status();
        sweep_stale_runtime_stage_dirs(&root2);
        assert!(root2.join("_update").exists(), "撕裂态不清扫(留给收养)");
        let _ = fs::remove_dir_all(&root);
        let _ = fs::remove_dir_all(&root2);
    }

    // 手术锁簇:全部走 HELPER_ENV_LOCK 串行(读写手术锁相关 env,防并行互毒)
    #[test]
    fn surgery_lock_blocks_second_acquire_same_process() {
        let _env = HELPER_ENV_LOCK.lock().unwrap_or_else(|e| e.into_inner());
        let root = temp_test_dir("surgery-lock-same-proc");
        let guard = try_acquire_surgery_lock(&root, Duration::from_secs(1))
            .unwrap()
            .expect("首次必须拿到");
        // flock 同进程第二个 fd 也互斥(这正是「锁只进五叶、上层禁取」纪律的依据)
        let second = try_acquire_surgery_lock(&root, Duration::from_millis(600)).unwrap();
        assert!(second.is_none(), "持锁期间第二次 acquire 必须等超时");
        drop(guard);
        let third = try_acquire_surgery_lock(&root, Duration::from_secs(1)).unwrap();
        assert!(third.is_some(), "释放后立即可得");
        let _ = fs::remove_dir_all(&root);
    }

    // 子进程角色:仅当 HOROSA_LOCK_TEST_ROOT 在场才动作(直跑=零动作秒过)。
    #[test]
    fn surgery_lock_child_holder() {
        let Ok(root) = std::env::var("HOROSA_LOCK_TEST_ROOT") else {
            return;
        };
        let guard = try_acquire_surgery_lock(Path::new(&root), Duration::from_secs(5))
            .unwrap()
            .expect("child 必须拿到锁");
        thread::sleep(Duration::from_secs(3));
        drop(guard);
    }

    fn spawn_lock_holder_child(root: &Path) -> std::process::Child {
        let exe = std::env::current_exe().unwrap();
        Command::new(&exe)
            .args(["--exact", "tests::surgery_lock_child_holder", "--nocapture"])
            .env("HOROSA_LOCK_TEST_ROOT", root)
            .env_remove("HOROSA_SURGERY_LOCK_DISABLE")
            .stdout(Stdio::null())
            .stderr(Stdio::null())
            .spawn()
            .expect("spawn child")
    }

    fn wait_until_child_holds_lock(root: &Path) -> bool {
        for _ in 0..50 {
            thread::sleep(Duration::from_millis(100));
            match try_acquire_surgery_lock(root, Duration::from_millis(1)).unwrap() {
                Some(g) => drop(g), // 子进程还没锁上,继续等
                None => return true,
            }
        }
        false
    }

    #[test]
    fn surgery_lock_cross_process_contention() {
        let _env = HELPER_ENV_LOCK.lock().unwrap_or_else(|e| e.into_inner());
        let root = temp_test_dir("surgery-lock-xproc");
        fs::create_dir_all(&root).unwrap();
        let mut child = spawn_lock_holder_child(&root);
        assert!(wait_until_child_holds_lock(&root), "子进程应已持锁");
        // 短等拿不到(对方在手术)
        assert!(try_acquire_surgery_lock(&root, Duration::from_millis(300))
            .unwrap()
            .is_none());
        // 长等(≥子进程持锁 3s)排队拿到
        assert!(try_acquire_surgery_lock(&root, Duration::from_secs(10))
            .unwrap()
            .is_some());
        let _ = child.wait();
        let _ = fs::remove_dir_all(&root);
    }

    #[test]
    fn surgery_lock_released_on_sigkill() {
        let _env = HELPER_ENV_LOCK.lock().unwrap_or_else(|e| e.into_inner());
        let root = temp_test_dir("surgery-lock-sigkill");
        fs::create_dir_all(&root).unwrap();
        let mut child = spawn_lock_holder_child(&root);
        assert!(wait_until_child_holds_lock(&root), "子进程应已持锁");
        let _ = Command::new("/bin/kill")
            .args(["-9", &child.id().to_string()])
            .status();
        let _ = child.wait();
        // 内核级释放:kill -9 后立即可得(崩溃不留死锁)
        assert!(try_acquire_surgery_lock(&root, Duration::from_secs(2))
            .unwrap()
            .is_some());
        let _ = fs::remove_dir_all(&root);
    }

    #[test]
    fn surgery_lock_disable_env_bypasses() {
        let _env = HELPER_ENV_LOCK.lock().unwrap_or_else(|e| e.into_inner());
        let root = temp_test_dir("surgery-lock-disable");
        let guard = try_acquire_surgery_lock(&root, Duration::from_secs(1))
            .unwrap()
            .expect("先真实持锁");
        std::env::set_var("HOROSA_SURGERY_LOCK_DISABLE", "1");
        let bypass = try_acquire_surgery_lock(&root, Duration::from_millis(100)).unwrap();
        std::env::remove_var("HOROSA_SURGERY_LOCK_DISABLE");
        assert!(bypass.is_some(), "开关下必须旁路(退回无锁旧行为)");
        drop(guard);
        let _ = fs::remove_dir_all(&root);
    }

    #[test]
    fn torn_repair_skips_when_locked() {
        let _env = HELPER_ENV_LOCK.lock().unwrap_or_else(|e| e.into_inner());
        let root = temp_test_dir("torn-locked");
        write_minimal_runtime_tree(&root.join("previous"), "prev");
        std::env::set_var("HOROSA_SURGERY_LOCK_OPT_WAIT_SECS", "1");
        let guard = try_acquire_surgery_lock(&root, Duration::from_secs(1))
            .unwrap()
            .expect("模拟对方持锁");
        // optional 语义:拿不到 → Ok(false) 且绝不收养(current 不产出)
        let repaired = repair_torn_runtime_slots(&root).unwrap();
        std::env::remove_var("HOROSA_SURGERY_LOCK_OPT_WAIT_SECS");
        assert!(!repaired, "对方持锁期间不得收养");
        assert!(!root.join("current").exists());
        drop(guard);
        let _ = fs::remove_dir_all(&root);
    }

    // 多实例更新感知纯函数
    #[test]
    fn runtime_change_step_detects_version_drift() {
        // 首见=定基线,不触发
        let (b, changed) = runtime_change_step(None, Some("1.0.0-runtime1".into()));
        assert_eq!(b.as_deref(), Some("1.0.0-runtime1"));
        assert!(!changed);
        // 同版本不触发
        let (b, changed) = runtime_change_step(b, Some("1.0.0-runtime1".into()));
        assert!(!changed);
        // 版本漂移触发(基线保持,供账本引用)
        let (b, changed) = runtime_change_step(b, Some("1.0.1-runtime1".into()));
        assert!(changed);
        assert_eq!(b.as_deref(), Some("1.0.0-runtime1"));
        // 读不到 manifest(手术中途)不触发
        let (_b, changed) = runtime_change_step(b, None);
        assert!(!changed);
    }

    // ===== API 回退源 sha 闭环:三态 + 守门无条件 + notify-only 不触网 =====
    fn test_release_config(manifest_name: &str) -> ReleaseConfig {
        serde_json::from_value(serde_json::json!({
            "repoOwner": "demo", "repoName": "horosa",
            "runtimeVersion": "1.0.0-runtime1",
            "runtimeAssetName": "runtime.tar.gz",
            "desktopAssetName": "Horosa-Desktop.zip",
            "desktopPkgName": "a.pkg", "desktopPkgZipName": "a.pkg.zip",
            "updateManifestName": manifest_name,
            "primaryDownload": "pkg", "supportedArch": "arm64",
            "releaseTagPrefix": "v", "appName": "星阙",
        }))
        .unwrap()
    }

    fn manifest_json(version: &str, with_sha: bool) -> String {
        let sha = if with_sha {
            "\"appSha256\":\"aa\",\"runtimeSha256\":\"bb\","
        } else {
            ""
        };
        format!(
            "{{\"version\":\"{version}\",\"tag\":\"v{version}\",\"platforms\":{{\"macos-aarch64\":{{\
             \"appUrl\":\"https://x/app.zip\",{sha}\"runtimeUrl\":\"https://x/rt.tar.gz\",\
             \"runtimeVersion\":\"{version}-runtime1\"}}}}}}"
        )
    }

    /// 极简 raw HTTP:按 path 返回预置 body(200)或 404。返回 (base_url, 命中计数)。
    /// 用 raw TcpListener 而非 tiny_http:与 §7.1 规矩一致,协议级可控。
    fn spawn_asset_server(
        routes: Vec<(String, String)>,
    ) -> (String, Arc<AtomicUsize>, Arc<AtomicBool>) {
        let listener = std::net::TcpListener::bind("127.0.0.1:0").unwrap();
        let port = listener.local_addr().unwrap().port();
        listener.set_nonblocking(true).unwrap();
        let hits = Arc::new(AtomicUsize::new(0));
        let stop = Arc::new(AtomicBool::new(false));
        let (h, st) = (hits.clone(), stop.clone());
        thread::spawn(move || {
            while !st.load(Ordering::SeqCst) {
                match listener.accept() {
                    Ok((mut sock, _)) => {
                        h.fetch_add(1, Ordering::SeqCst);
                        let mut buf = [0u8; 2048];
                        let n = sock.read(&mut buf).unwrap_or(0);
                        let req = String::from_utf8_lossy(&buf[..n]).to_string();
                        let path = req
                            .split_whitespace()
                            .nth(1)
                            .unwrap_or("/")
                            .split('?')
                            .next()
                            .unwrap_or("/")
                            .to_string();
                        let body = routes.iter().find(|(p, _)| *p == path).map(|(_, b)| b.clone());
                        let resp = match body {
                            Some(b) => format!(
                                "HTTP/1.1 200 OK\r\nContent-Length: {}\r\nConnection: close\r\n\r\n{}",
                                b.len(),
                                b
                            ),
                            None => "HTTP/1.1 404 Not Found\r\nContent-Length: 0\r\nConnection: close\r\n\r\n".to_string(),
                        };
                        let _ = sock.write_all(resp.as_bytes());
                    }
                    Err(_) => thread::sleep(Duration::from_millis(20)),
                }
            }
        });
        (format!("http://127.0.0.1:{port}"), hits, stop)
    }

    #[test]
    fn api_fallback_fetches_manifest_asset_and_keeps_sha() {
        let _env = HELPER_ENV_LOCK.lock().unwrap_or_else(|e| e.into_inner());
        let (base, _hits, stop) = spawn_asset_server(vec![(
            "/horosa-latest.json".into(),
            manifest_json("9.9.9", true),
        )]);
        let release: GithubRelease = serde_json::from_value(serde_json::json!({
            "tag_name": "v9.9.9",
            "assets": [{"name": "horosa-latest.json",
                        "browser_download_url": format!("{base}/horosa-latest.json")}],
        }))
        .unwrap();
        let client = build_github_client(5).unwrap();
        let manifest =
            fetch_manifest_via_release_asset(&client, &release, "horosa-latest.json").unwrap();
        let plan = plan_from_manifest(
            manifest,
            &test_release_config("horosa-latest.json"),
            "macos-aarch64",
            UpdateSource::ManifestViaApi,
        )
        .unwrap();
        assert_eq!(plan.source, UpdateSource::ManifestViaApi);
        assert_eq!(plan.app_sha256.as_deref(), Some("aa"));
        assert_eq!(plan.runtime_sha256.as_deref(), Some("bb"));
        assert!(!plan.notify_only, "取回真 manifest 后绝不是 notify-only");
        stop.store(true, Ordering::SeqCst);
    }

    #[test]
    fn api_fallback_manifest_asset_missing_yields_none() {
        let _env = HELPER_ENV_LOCK.lock().unwrap_or_else(|e| e.into_inner());
        let release: GithubRelease = serde_json::from_value(serde_json::json!({
            "tag_name": "v9.9.9",
            "assets": [{"name": "Horosa-Desktop.zip", "browser_download_url": "https://x/app.zip"}],
        }))
        .unwrap();
        let client = build_github_client(2).unwrap();
        // assets 里没有 manifest 名 → None(上游据此降级 notify-only)
        assert!(fetch_manifest_via_release_asset(&client, &release, "horosa-latest.json").is_none());
    }

    #[test]
    fn api_fallback_manifest_asset_bad_json_yields_none() {
        let _env = HELPER_ENV_LOCK.lock().unwrap_or_else(|e| e.into_inner());
        let (base, _hits, stop) =
            spawn_asset_server(vec![("/horosa-latest.json".into(), "{ not json".into())]);
        let release: GithubRelease = serde_json::from_value(serde_json::json!({
            "tag_name": "v9.9.9",
            "assets": [{"name": "horosa-latest.json",
                        "browser_download_url": format!("{base}/horosa-latest.json")}],
        }))
        .unwrap();
        let client = build_github_client(5).unwrap();
        assert!(
            fetch_manifest_via_release_asset(&client, &release, "horosa-latest.json").is_none(),
            "坏 JSON 必须降级(不 panic)"
        );
        stop.store(true, Ordering::SeqCst);
    }

    #[test]
    fn api_manifest_fetch_killswitch_forces_notify_only_path() {
        let _env = HELPER_ENV_LOCK.lock().unwrap_or_else(|e| e.into_inner());
        let (base, hits, stop) = spawn_asset_server(vec![(
            "/horosa-latest.json".into(),
            manifest_json("9.9.9", true),
        )]);
        let release: GithubRelease = serde_json::from_value(serde_json::json!({
            "tag_name": "v9.9.9",
            "assets": [{"name": "horosa-latest.json",
                        "browser_download_url": format!("{base}/horosa-latest.json")}],
        }))
        .unwrap();
        let client = build_github_client(5).unwrap();
        std::env::set_var("HOROSA_UPDATE_API_MANIFEST_FETCH", "0");
        let got = fetch_manifest_via_release_asset(&client, &release, "horosa-latest.json");
        std::env::remove_var("HOROSA_UPDATE_API_MANIFEST_FETCH");
        assert!(got.is_none(), "开关下跳过 asset 取回");
        assert_eq!(hits.load(Ordering::SeqCst), 0, "开关下不得触网");
        stop.store(true, Ordering::SeqCst);
    }

    // 无 sha 的 manifest 也能映射成 plan(sha=None),真正的拦截在守门——
    // 守门已改无条件,故此处钉住「plan 侧 sha 缺失可观测」这一前置事实。
    #[test]
    fn plan_from_manifest_without_sha_leaves_none_for_guard() {
        let manifest: UpdateManifest = serde_json::from_str(&manifest_json("9.9.9", false)).unwrap();
        let plan = plan_from_manifest(
            manifest,
            &test_release_config("horosa-latest.json"),
            "macos-aarch64",
            UpdateSource::ManifestViaApi,
        )
        .unwrap();
        assert!(plan.app_sha256.is_none() && plan.runtime_sha256.is_none());
        assert!(!plan.notify_only);
        // 平台键不匹配 → None(老 manifest/异构平台)
        let m2: UpdateManifest = serde_json::from_str(&manifest_json("9.9.9", true)).unwrap();
        assert!(plan_from_manifest(
            m2,
            &test_release_config("horosa-latest.json"),
            "windows-x86_64",
            UpdateSource::Manifest
        )
        .is_none());
    }

    // 深探慢 streak 纯函数:1 次失败不杀、2 次杀、Ok 清零
    #[test]
    fn deep_step_state_machine() {
        let (s1, kill1) = deep_step(0, false);
        assert_eq!((s1, kill1), (1, false), "单次深探失败容忍(高载/GC)");
        let (s2, kill2) = deep_step(s1, false);
        assert_eq!((s2, kill2), (2, true), "连续 2 次深探失败判算力死");
        let (s3, kill3) = deep_step(s2, true);
        assert_eq!((s3, kill3), (0, false), "恢复即清零");
    }

    fn spawn_identity_stub(body: &'static str) -> u16 {
        let listener = std::net::TcpListener::bind("127.0.0.1:0").unwrap();
        let port = listener.local_addr().unwrap().port();
        thread::spawn(move || {
            if let Ok((mut sock, _)) = listener.accept() {
                let mut buf = [0u8; 1024];
                let _ = sock.read(&mut buf);
                let resp = format!(
                    "HTTP/1.1 200 OK\r\nContent-Type: application/json\r\nContent-Length: {}\r\nConnection: close\r\n\r\n{}",
                    body.len(),
                    body
                );
                let _ = sock.write_all(resp.as_bytes());
            }
        });
        port
    }

    // proto 门代数差免疫:旧对端(proto 1/无 deep 字段)在深探轮按通过处理,绝不误杀
    #[test]
    fn probe_identity_deep_unsupported_on_proto1() {
        use std::io::{Read, Write};
        let _ = (Read::read
            as fn(&mut std::net::TcpStream, &mut [u8]) -> std::io::Result<usize>);
        let port = spawn_identity_stub(r#"{"app":"horosa-backend","proto":1,"nonce":"n-1"}"#);
        let got = probe_identity(port, "horosa-backend", "n-1", Duration::from_secs(2), true);
        assert_eq!(got, IdentityProbe::DeepUnsupported);
    }

    #[test]
    fn probe_identity_deep_fail_on_proto2() {
        let port = spawn_identity_stub(
            r#"{"app":"horosa-backend","proto":2,"nonce":"n-1","deep":"fail"}"#,
        );
        let got = probe_identity(port, "horosa-backend", "n-1", Duration::from_secs(2), true);
        assert_eq!(got, IdentityProbe::DeepFail, "proto2 深探失败必须显式分类");
    }

    #[test]
    fn probe_identity_deep_ok_on_proto2() {
        let port = spawn_identity_stub(
            r#"{"app":"horosa-backend","proto":2,"nonce":"n-1","deep":"ok"}"#,
        );
        let got = probe_identity(port, "horosa-backend", "n-1", Duration::from_secs(2), true);
        assert_eq!(got, IdentityProbe::Ok);
        // 浅探不受 proto2 影响
        let port2 = spawn_identity_stub(
            r#"{"app":"horosa-backend","proto":2,"nonce":"n-1"}"#,
        );
        let got2 = probe_identity(port2, "horosa-backend", "n-1", Duration::from_secs(2), false);
        assert_eq!(got2, IdentityProbe::Ok);
    }

    // 诊断包 Java 日志选取器:mtime 最新优先 + cap 内尽量多收(大文件跳过继续拣小)
    #[test]
    fn select_recent_files_prefers_newest_within_cap() {
        let root = temp_test_dir("diag-select");
        fs::create_dir_all(root.join("2026/07/09")).unwrap();
        let old_big = root.join("2026/07/09/old-big.log");
        let mid = root.join("2026/07/09/mid.log");
        let newest = root.join("newest.log");
        fs::write(&old_big, vec![b'x'; 3000]).unwrap();
        fs::write(&mid, vec![b'y'; 400]).unwrap();
        fs::write(&newest, vec![b'z'; 500]).unwrap();
        let _ = Command::new("/usr/bin/touch").args(["-t", "202001010000"]).arg(&old_big).status();
        let _ = Command::new("/usr/bin/touch").args(["-t", "202601010000"]).arg(&mid).status();
        let _ = Command::new("/usr/bin/touch").args(["-t", "202607090000"]).arg(&newest).status();
        // cap=1000:newest(500)+mid(400) 收下;old_big(3000) 超预算跳过
        let picked = select_recent_files_by_mtime(&root, 1000);
        assert_eq!(picked.len(), 2, "cap 内应收两份小日志");
        assert_eq!(picked[0], newest, "mtime 最新优先");
        assert_eq!(picked[1], mid);
        assert!(!picked.contains(&old_big), "超预算大文件跳过而非截断全部");
        let _ = fs::remove_dir_all(&root);
    }

    // 磁盘水位闩:跌破触发一次/闩内不刷屏/回升 2× 解闩/卷异常不动作
    #[test]
    fn disk_low_step_latch_and_recovery() {
        let min = 500u64 * 1024 * 1024;
        // 正常 → 不触发
        assert_eq!(disk_low_step(false, Some(min * 4), min), (false, false));
        // 跌破 → 触发+闩
        assert_eq!(disk_low_step(false, Some(min - 1), min), (true, true));
        // 闩内仍低 → 不再刷屏
        assert_eq!(disk_low_step(true, Some(min / 2), min), (true, false));
        // 回升但未到 2× → 保持闩(防抖)
        assert_eq!(disk_low_step(true, Some(min + 1), min), (true, false));
        // 回升到 2× → 解闩(不触发)
        assert_eq!(disk_low_step(true, Some(min * 2), min), (false, false));
        // 解闩后再跌破 → 再次触发
        assert_eq!(disk_low_step(false, Some(min - 1), min), (true, true));
        // 读不到 → 原样不动作
        assert_eq!(disk_low_step(true, None, min), (true, false));
        assert_eq!(disk_low_step(false, None, min), (false, false));
    }

    // 权限定因:目录 chmod 000 → PermissionDenied → 人话 hint;正常目录 → None
    #[test]
    fn classify_permission_issue_detects_readonly_dir() {
        use std::os::unix::fs::PermissionsExt;
        let root = temp_test_dir("perm-probe");
        let ok_dir = root.join("ok");
        let bad_dir = root.join("bad");
        fs::create_dir_all(&ok_dir).unwrap();
        fs::create_dir_all(&bad_dir).unwrap();
        let paths = RuntimePaths {
            app_data_dir: ok_dir.clone(),
            runtime_dir: bad_dir.clone(),
            logs_dir: ok_dir.clone(),
            frontend_dir: ok_dir.clone(),
            start_script: ok_dir.join("s.sh"),
            stop_script: ok_dir.join("t.sh"),
            manifest_path: ok_dir.join("m.json"),
        };
        // 全可写 → None
        assert!(classify_permission_issue(&paths).is_none());
        // runtime 目录锁死 → Some(含目录路径的人话)
        fs::set_permissions(&bad_dir, fs::Permissions::from_mode(0o000)).unwrap();
        let hint = classify_permission_issue(&paths);
        fs::set_permissions(&bad_dir, fs::Permissions::from_mode(0o755)).unwrap();
        let hint = hint.expect("锁死目录必须定因");
        assert!(hint.contains("权限异常"));
        assert!(hint.contains(&bad_dir.display().to_string()));
        let _ = fs::remove_dir_all(&root);
    }

    #[test]
    fn archive_runtime_version_reads_manifest_version() {
        let root = temp_test_dir("runtime-archive-version");
        let archive = create_runtime_archive(&root, "1.2.3-runtime1");
        assert_eq!(
            archive_runtime_version(&archive).unwrap(),
            "1.2.3-runtime1".to_string()
        );
    }

    #[cfg(unix)]
    #[test]
    fn extract_runtime_archive_installs_usable_runtime() {
        let root = temp_test_dir("runtime-archive-extract");
        let archive = create_usable_runtime_archive(&root, "1.2.3-runtime1");
        let dest_root = root.join("runtime-root");
        extract_runtime_archive(&archive, &dest_root).unwrap();
        let current = dest_root.join("current");
        assert!(runtime_matches_expected(&current, "1.2.3-runtime1"));
        assert!(!dest_root.join("_extract").exists());
        assert!(!dest_root.join("previous").exists());
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

    #[cfg(unix)]
    #[test]
    fn runtime_dir_is_not_usable_when_java_runtime_is_missing() {
        let root = temp_test_dir("runtime-missing-java");
        let runtime_dir = create_fake_runtime_tree(&root, "1.2.2-runtime1", false);
        assert!(!runtime_dir_is_usable(&runtime_dir));
    }

    #[cfg(unix)]
    #[test]
    fn runtime_dir_is_usable_with_python_and_java_stubs() {
        let root = temp_test_dir("runtime-with-java");
        let runtime_dir = create_fake_runtime_tree(&root, "1.2.2-runtime1", true);
        assert!(runtime_dir_is_usable(&runtime_dir));
    }

    #[test]
    fn handoff_to_installed_app_only_when_target_is_newer() {
        let current_bundle = Path::new("/Users/test/Applications/星阙.app");
        let target_bundle = Path::new("/Applications/星阙.app");
        let current = Version::parse("1.2.1").unwrap();
        let target = Version::parse("1.2.3").unwrap();
        assert!(should_handoff_to_installed_app(
            current_bundle,
            target_bundle,
            Some(&current),
            Some(&target)
        ));
        assert!(!should_handoff_to_installed_app(
            target_bundle,
            target_bundle,
            Some(&target),
            Some(&target)
        ));
        assert!(!should_handoff_to_installed_app(
            current_bundle,
            target_bundle,
            Some(&target),
            Some(&current)
        ));
    }

    #[cfg(unix)]
    #[test]
    fn runtime_dir_usability_writes_health_cache() {
        let root = temp_test_dir("runtime-health-cache");
        let runtime_dir = create_fake_runtime_tree(&root, "1.2.3-runtime1", true);
        assert!(runtime_dir_is_usable(&runtime_dir));
        assert!(runtime_health_cache_path(&runtime_dir).exists());
    }

    #[cfg(unix)]
    #[test]
    fn runtime_health_cache_is_invalidated_when_runtime_changes() {
        let root = temp_test_dir("runtime-health-cache-invalidate");
        let runtime_dir = create_fake_runtime_tree(&root, "1.2.3-runtime1", true);
        assert!(runtime_dir_is_usable(&runtime_dir));
        let cache_path = runtime_health_cache_path(&runtime_dir);
        assert!(cache_path.exists());
        std::thread::sleep(Duration::from_secs(1));
        fs::write(
            runtime_dir.join("runtime-manifest.json"),
            "{\"version\":\"1.3.1-runtime3\"}\n",
        )
        .unwrap();
        let cache = runtime_health_cache(&runtime_dir).expect("cache exists");
        assert!(!runtime_health_cache_matches(&runtime_dir, &cache));
        assert!(runtime_dir_is_usable(&runtime_dir));
    }

    #[cfg(unix)]
    #[test]
    fn runtime_fast_path_marker_is_invalidated_when_runtime_changes() {
        let root = temp_test_dir("runtime-fast-path-invalidate");
        let runtime_dir = create_fake_runtime_tree(&root, "1.2.3-runtime1", true);
        let manifest =
            read_runtime_manifest_from_path(&runtime_dir.join("runtime-manifest.json")).unwrap();
        write_runtime_fast_path_marker(&runtime_dir, &manifest);
        assert!(runtime_fast_path_allowed(&runtime_dir));
        std::thread::sleep(Duration::from_secs(1));
        fs::write(
            runtime_dir.join("runtime-manifest.json"),
            "{\"version\":\"1.3.1-runtime3\"}\n",
        )
        .unwrap();
        assert!(!runtime_fast_path_allowed(&runtime_dir));
        clear_runtime_fast_path_marker(&runtime_dir);
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
            "version=1.0.25\nruntime_version=1.0.25-runtime1\ninstalled_at=2026-03-17 20:00:00\nrelaunch_status=pending_manual\n",
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
        assert_eq!(
            values.get("relaunch_status").map(String::as_str),
            Some("pending_manual")
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
        assert!(script.contains("relaunch_status="));
        assert!(script.contains("pending_manual"));
        assert!(script.contains("auto_relaunch_confirmed"));
        assert!(!script.contains("open_app || true"));
    }

    #[test]
    fn install_review_does_not_force_replace_for_healthy_existing_app() {
        assert!(!should_recommend_installed_app_replacement(
            AssetReviewMode::Install,
            DetectedAssetState::Healthy
        ));
        assert!(should_recommend_installed_app_replacement(
            AssetReviewMode::Install,
            DetectedAssetState::Outdated
        ));
    }

    #[test]
    fn exit_cleanup_claim_is_single_shot() {
        // 退出双回调(ExitRequested+Exit)/app.exit(0) 双发场景下,stop 脚本只许 spawn 一次。
        assert!(claim_exit_cleanup(), "first claim must win");
        assert!(!claim_exit_cleanup(), "second claim must lose");
        assert!(!claim_exit_cleanup(), "subsequent claims must lose");
    }

    fn repo_stop_script_path() -> PathBuf {
        Path::new(env!("CARGO_MANIFEST_DIR")).join("../../Horosa-Web/stop_horosa_local.sh")
    }

    fn repo_start_script_path() -> PathBuf {
        Path::new(env!("CARGO_MANIFEST_DIR")).join("../../Horosa-Web/start_horosa_local.sh")
    }

    // progress-aware 就绪门契约(文本面):
    // ① 三锚在位(续命账本段/总开关/总 cap);② 判死分支必须引用 last_progress_epoch
    //   (反锚:防有人把续命逻辑删回硬超时);③ 指纹函数禁 lsof(全进程 FD 扫描遇
    //   卡死进程可 stall 数十秒,曾拖死探测——沿用 stop 脚本同款禁令)。
    #[test]
    fn start_script_keeps_progress_extend_guard() {
        let script = fs::read_to_string(repo_start_script_path()).expect("read start script");
        assert!(script.contains("sh.ready_extend"), "缺续命账本段");
        assert!(script.contains("sh.ready_giveup"), "缺判死账本段");
        assert!(
            script.contains("HOROSA_READY_PROGRESS_EXTEND"),
            "缺总开关"
        );
        assert!(
            script.contains("HOROSA_READY_TOTAL_CAP_SECS"),
            "缺总 cap(无限等防线)"
        );
        // 判死分支必须以进展时刻为条件(硬超时回潮=红)
        let deadline_at = script
            .find(r#"-ge "${deadline_epoch}""#)
            .expect("缺 deadline 判定");
        let tail = &script[deadline_at..deadline_at + 1200.min(script.len() - deadline_at)];
        assert!(
            tail.contains("last_progress_epoch"),
            "判死分支未引用 last_progress_epoch(续命被删回硬超时)"
        );
        // 指纹函数体内禁 lsof
        let fp_at = script.find("_progress_fingerprint()").expect("缺指纹函数");
        let fp_end = script[fp_at..]
            .find("\n}")
            .map(|i| fp_at + i)
            .unwrap_or(script.len());
        assert!(
            !script[fp_at..fp_end].contains("lsof"),
            "指纹函数禁用 lsof"
        );
    }

    #[test]
    fn stop_script_keeps_workspace_guard_and_fast_primitives() {
        // 行为护栏的文本面:① ROOT 工作区守卫(防误杀第二份 checkout 的服务)不许丢;
        // ② 端口检查必须用 netstat(lsof 全进程 FD 扫描遇卡死进程可 stall 数十秒);
        // ③ 不许回归整秒 sleep(0.1s 轮询是退出提速的根)。
        let script = fs::read_to_string(repo_stop_script_path()).expect("read stop script");
        assert!(
            script.contains(r#"grep -Fq "${ROOT}""#),
            "workspace guard missing"
        );
        assert!(
            script.contains("netstat -anv -p tcp"),
            "port scan must use netstat (kernel table), not lsof"
        );
        assert!(script.contains("sleep 0.1"), "0.1s poll loop missing");
        for line in script.lines() {
            let code = line.trim_start();
            if code.starts_with('#') {
                continue; // 注释里允许提及 lsof(说明为什么禁用)
            }
            assert!(
                !code.contains("lsof"),
                "lsof is banned in stop script (full-FD scan can stall 30-100s): {line}"
            );
            assert!(
                !code.starts_with("sleep 1"),
                "fixed whole-second sleep regressed: {line}"
            );
        }
    }

    #[test]
    fn stop_script_kills_within_time_budget() {
        // 行为护栏(G2 升级版):
        // ① 起两个「指纹伪装成本产品服务」的假进程(exec -a 改 argv[0]),写入带端口后缀的
        //    pid 文件——脚本必须在 3s 内全停(旧实现 ≥2s 串行 sleep + lsof stall 可到 30s+)。
        // ② 反向断言:一个指纹不符的无辜进程(裸 sleep)即使 pid 被写进 pid 文件,也绝不能
        //    被误杀(pid 复用/跨实例覆写场景),脚本只清文件。tempdir 隔离,不碰真实工作区。
        let work = std::env::temp_dir().join(format!("horosa-stop-test-{}", std::process::id()));
        let _ = fs::remove_dir_all(&work);
        fs::create_dir_all(&work).expect("mk tempdir");
        fs::copy(repo_stop_script_path(), work.join("stop_horosa_local.sh")).expect("copy script");
        let spawn_marked_sleeper = |marker: &str| {
            Command::new("/bin/bash")
                .arg("-c")
                .arg(format!("exec -a {marker} /bin/sleep 100"))
                .spawn()
                .expect("spawn marked sleeper")
        };
        let mut py = spawn_marked_sleeper("webchartsrv.py");
        let mut java = spawn_marked_sleeper("astrostudyboot.jar");
        let mut innocent = Command::new("/bin/sleep")
            .arg("100")
            .spawn()
            .expect("spawn innocent sleeper");
        // 脚本无 env 时用默认端口 8899/9999/8000 → pid 文件名按同一约定生成。
        fs::write(work.join(".horosa_py.8899.pid"), py.id().to_string()).expect("write py pid");
        fs::write(work.join(".horosa_java.9999.pid"), java.id().to_string())
            .expect("write java pid");
        fs::write(work.join(".horosa_web.8000.pid"), innocent.id().to_string())
            .expect("write innocent pid");
        let started = Instant::now();
        let status = Command::new("/bin/bash")
            .arg(work.join("stop_horosa_local.sh"))
            .current_dir(&work)
            .stdout(Stdio::null())
            .stderr(Stdio::null())
            .status()
            .expect("run stop script");
        let elapsed = started.elapsed();
        assert!(status.success(), "stop script must exit 0");
        assert!(
            elapsed < Duration::from_secs(3),
            "stop script too slow: {elapsed:?}"
        );
        // 两个假服务必须已死。它们是本测试进程的子进程,被杀后先成僵尸(kill -0 对僵尸
        // 仍成功),必须用 try_wait 收尸判定;轮询 ≤2s 防 wait 永久阻塞。
        fn assert_reaped(label: &str, child: &mut std::process::Child) {
            for _ in 0..40 {
                if child.try_wait().expect("try_wait").is_some() {
                    return;
                }
                thread::sleep(Duration::from_millis(50));
            }
            panic!("{label} sleeper must be stopped by script");
        }
        assert_reaped("py", &mut py);
        assert_reaped("java", &mut java);
        // 无辜进程必须还活着(指纹校验拒杀),pid 文件应被清理。
        assert!(
            innocent.try_wait().expect("try_wait innocent").is_none(),
            "指纹不符的进程绝不能被停服脚本误杀(pid 复用防线失效)"
        );
        assert!(
            !work.join(".horosa_web.8000.pid").exists(),
            "指纹不符时应只清理 pid 文件"
        );
        let _ = innocent.kill();
        let _ = innocent.wait();
        let _ = fs::remove_dir_all(&work);
    }

    // ── 增量部件应用协议(apply_component_updates):tree/preserve/files 三机制 + 失败原子性 ──

    fn write_file(path: &Path, content: &str) {
        fs::create_dir_all(path.parent().unwrap()).unwrap();
        fs::write(path, content).unwrap();
    }

    /// 打一个部件 tar.gz:条目带 runtime-payload/ 前缀(与打包脚本产物同构)。
    fn build_component_tar(dest: &Path, entries: &[(&str, &str)]) {
        let file = fs::File::create(dest).unwrap();
        let enc = GzEncoder::new(file, Compression::fast());
        let mut builder = Builder::new(enc);
        for (rel, content) in entries {
            let mut header = tar::Header::new_gnu();
            header.set_size(content.len() as u64);
            header.set_mode(0o644);
            header.set_cksum();
            builder
                .append_data(
                    &mut header,
                    format!("runtime-payload/{}", rel),
                    content.as_bytes(),
                )
                .unwrap();
        }
        builder.into_inner().unwrap().finish().unwrap();
    }

    fn lock_json(version: &str, tree_files_note: &str, files_list: &[&str]) -> serde_json::Value {
        serde_json::json!({
            "schemaVersion": 1,
            "runtimeVersion": version,
            "appName": APP_NAME,
            "builtAt": tree_files_note,
            "components": [
                {"name": "t", "type": "tree", "paths": ["t"], "preserve": ["t/keep"],
                 "file": "comp-t.tar.gz", "sha256": "x", "size": 1},
                {"name": "f", "type": "files", "files": files_list,
                 "file": "comp-f.tar.gz", "sha256": "y", "size": 1},
            ],
        })
    }

    fn setup_v1_runtime(root: &Path) {
        let current = root.join("current");
        write_file(&current.join("t/old.txt"), "v1-old");
        write_file(&current.join("t/keep/k.txt"), "user-data");
        write_file(&current.join("f/a.txt"), "v1-a");
        write_file(&current.join("f/b.txt"), "v1-b");
        let lock = lock_json("1.0.0", "2026-01-01", &["f/a.txt", "f/b.txt"]);
        write_file(
            &current.join("components-lock.json"),
            &serde_json::to_string_pretty(&lock).unwrap(),
        );
        write_file(
            &current.join("runtime-manifest.json"),
            r#"{"version":"1.0.0","built_at":"2026-01-01","appName":"x"}"#,
        );
    }

    fn staged_v2(work: &Path) -> StagedComponents {
        let t_tar = work.join("comp-t.tar.gz");
        build_component_tar(&t_tar, &[("t/new.txt", "v2-new")]); // 不含 keep 子树
        let f_tar = work.join("comp-f.tar.gz");
        build_component_tar(&f_tar, &[("f/a.txt", "v2-a"), ("f/c.txt", "v2-c")]); // b 消失
        let new_lock = lock_json("2.0.0", "2026-02-02", &["f/a.txt", "f/c.txt"]);
        let mk = |name: &str, file: &str| ManifestComponent {
            name: name.into(),
            kind: if name == "t" {
                "tree".into()
            } else {
                "files".into()
            },
            sha256: "irrelevant-for-apply".into(),
            size: Some(1),
            file: file.into(),
            url: String::new(),
        };
        StagedComponents {
            archives: vec![
                (mk("t", "comp-t.tar.gz"), t_tar),
                (mk("f", "comp-f.tar.gz"), f_tar),
            ],
            new_lock_text: serde_json::to_string_pretty(&new_lock).unwrap(),
            new_lock_json: new_lock,
        }
    }

    #[test]
    fn component_apply_tree_preserve_and_files_semantics() {
        let work = std::env::temp_dir().join(format!("horosa-comp-apply-{}", std::process::id()));
        let _ = fs::remove_dir_all(&work);
        let root = work.join("root");
        setup_v1_runtime(&root);
        let staged = staged_v2(&work);

        apply_component_updates(&root, &staged).expect("incremental apply should succeed");

        let cur = root.join("current");
        // tree:整树替换 + preserve 子树幸存
        assert!(!cur.join("t/old.txt").exists(), "旧树文件应被整树替换清除");
        assert_eq!(fs::read_to_string(cur.join("t/new.txt")).unwrap(), "v2-new");
        assert_eq!(
            fs::read_to_string(cur.join("t/keep/k.txt")).unwrap(),
            "user-data",
            "preserve 子树必须在整树替换后放回"
        );
        // files:更新/新增/删除三态
        assert_eq!(fs::read_to_string(cur.join("f/a.txt")).unwrap(), "v2-a");
        assert_eq!(fs::read_to_string(cur.join("f/c.txt")).unwrap(), "v2-c");
        assert!(!cur.join("f/b.txt").exists(), "消失文件(旧−新)必须删除");
        // 清单/身份戳重写 + 暂存清理
        let lock: serde_json::Value =
            serde_json::from_str(&fs::read_to_string(cur.join("components-lock.json")).unwrap())
                .unwrap();
        assert_eq!(lock["runtimeVersion"], "2.0.0");
        let manifest: serde_json::Value =
            serde_json::from_str(&fs::read_to_string(cur.join("runtime-manifest.json")).unwrap())
                .unwrap();
        assert_eq!(manifest["version"], "2.0.0");
        assert_eq!(manifest["appName"], APP_NAME);
        // WS-1d 看门狗语义:previous 槽保留到首次成功 ready 才回收(供连续启动失败自动回滚);
        // 其内容必须是更新前的旧版(1.x lock)。
        let prev_lock: serde_json::Value = serde_json::from_str(
            &fs::read_to_string(root.join("previous/components-lock.json")).unwrap(),
        )
        .unwrap();
        assert_ne!(
            prev_lock["runtimeVersion"], "2.0.0",
            "previous 槽必须是旧版"
        );
        assert!(!root.join("_comp_stage").exists());
        let _ = fs::remove_dir_all(&work);
    }

    #[test]
    fn watchdog_health_state_machine_and_rollback() {
        let work = temp_test_dir("watchdog");
        // 状态机:连续 note_start 递增,confirm 归零
        let health = work.join("launch-health.json");
        assert_eq!(launch_health_note_start(&health), 1);
        assert_eq!(launch_health_note_start(&health), 2);
        assert_eq!(launch_health_note_start(&health), 3);
        launch_health_confirm(&health);
        assert_eq!(launch_health_read(&health).pending_starts, 0);
        assert_eq!(launch_health_note_start(&health), 1);

        // 回滚:previous 完整 → 换回 current,故障槽清除
        let root = work.join("runtime");
        fs::create_dir_all(root.join("current")).unwrap();
        fs::write(
            root.join("current/runtime-manifest.json"),
            r#"{"version":"9.9.9"}"#,
        )
        .unwrap();
        fs::write(root.join("current/marker.txt"), "broken-new").unwrap();
        fs::create_dir_all(root.join("previous")).unwrap();
        fs::write(
            root.join("previous/runtime-manifest.json"),
            r#"{"version":"9.9.8"}"#,
        )
        .unwrap();
        fs::write(root.join("previous/marker.txt"), "good-old").unwrap();
        assert!(rollback_runtime_to_previous(&root).unwrap());
        assert_eq!(
            fs::read_to_string(root.join("current/marker.txt")).unwrap(),
            "good-old"
        );
        assert!(!root.join("previous").exists());
        assert!(!root.join("_broken_rollback").exists());

        // previous 缺失/不完整 → Ok(false),current 纹丝不动
        assert!(!rollback_runtime_to_previous(&root).unwrap());
        fs::create_dir_all(root.join("previous")).unwrap(); // 无 runtime-manifest.json = 不完整
        assert!(!rollback_runtime_to_previous(&root).unwrap());
        assert_eq!(
            fs::read_to_string(root.join("current/marker.txt")).unwrap(),
            "good-old"
        );
        let _ = fs::remove_dir_all(&work);
    }

    #[test]
    fn component_apply_failure_leaves_current_untouched() {
        let work = std::env::temp_dir().join(format!("horosa-comp-fail-{}", std::process::id()));
        let _ = fs::remove_dir_all(&work);
        let root = work.join("root");
        setup_v1_runtime(&root);
        let staged = staged_v2(&work);
        fs::write(&staged.archives[1].1, b"not a tar.gz").unwrap(); // 损坏 files 部件

        let err = apply_component_updates(&root, &staged);
        assert!(err.is_err(), "坏包必须失败");
        let cur = root.join("current");
        assert_eq!(fs::read_to_string(cur.join("t/old.txt")).unwrap(), "v1-old");
        assert_eq!(fs::read_to_string(cur.join("f/b.txt")).unwrap(), "v1-b");
        let lock: serde_json::Value =
            serde_json::from_str(&fs::read_to_string(cur.join("components-lock.json")).unwrap())
                .unwrap();
        assert_eq!(
            lock["runtimeVersion"], "1.0.0",
            "失败后 current 必须纹丝不动"
        );
        assert!(!root.join("_comp_stage").exists(), "失败必须清理暂存");
        let _ = fs::remove_dir_all(&work);
    }

    #[test]
    fn component_diff_gates_and_change_detection() {
        let work = std::env::temp_dir().join(format!("horosa-comp-diff-{}", std::process::id()));
        let _ = fs::remove_dir_all(&work);
        let root = work.join("root");
        setup_v1_runtime(&root);
        let mk = |name: &str, sha: &str| ManifestComponent {
            name: name.into(),
            kind: "tree".into(),
            sha256: sha.into(),
            size: Some(1),
            file: format!("comp-{}.tar.gz", name),
            url: String::new(),
        };
        let plan = |comps: Option<Vec<ManifestComponent>>| UpdatePlan {
            latest_version: Version::parse("9.9.9").unwrap(),
            notes: String::new(),
            repo_url: String::new(),
            release_url: String::new(),
            app_url: String::new(),
            app_sha256: None,
            runtime_url: None,
            runtime_version: Some("9.9.9".into()),
            runtime_sha256: None,
            components: comps,
            components_lock_url: Some("u".into()),
            components_lock_sha256: Some("s".into()),
            app_size_bytes: None,
            runtime_size_bytes: None,
            allow_downgrade: false,
            source: UpdateSource::Manifest,
            notify_only: false,
        };
        let roots = vec![root.clone()];
        // v1 lock 里 t/f 的 sha 是 "x"/"y":同 sha 不下载,异 sha 进下载集
        let diff = plan_component_diff(&plan(Some(vec![mk("t", "x"), mk("f", "changed")])), &roots)
            .expect("应可增量");
        assert_eq!(diff.len(), 1);
        assert_eq!(diff[0].name, "f");
        // 新增部件(本地清单没有)按变化处理
        let diff2 = plan_component_diff(
            &plan(Some(vec![mk("t", "x"), mk("brand-new", "z")])),
            &roots,
        )
        .expect("应可增量");
        assert_eq!(diff2.len(), 1);
        assert_eq!(diff2[0].name, "brand-new");
        // 门:无 components → None;多 root → None;kill-switch → None
        assert!(plan_component_diff(&plan(None), &roots).is_none());
        assert!(plan_component_diff(
            &plan(Some(vec![mk("t", "x")])),
            &[root.clone(), work.clone()]
        )
        .is_none());
        std::env::set_var("HOROSA_UPDATE_FULL_ONLY", "1");
        assert!(plan_component_diff(&plan(Some(vec![mk("t", "q")])), &roots).is_none());
        std::env::remove_var("HOROSA_UPDATE_FULL_ONLY");
        let _ = fs::remove_dir_all(&work);
    }

    // ---- WS-1b 断点续传下载核:tiny_http 本地矩阵 ----
    // 全部走真实 HTTP(127.0.0.1 随机端口),allow_resume 走参数注入(不碰 env,测试可并行)。

    mod download_resume {
        use super::super::*;
        use super::temp_test_dir;
        use flate2::write::GzEncoder;
        use flate2::Compression;
        use std::io::{Read, Write};
        use std::net::{Shutdown, TcpListener, TcpStream};
        use std::sync::{Arc, Mutex};
        use std::thread;
        use tar::Builder;

        // 用 raw TcpListener 手写 HTTP 响应:断线时机/206/Content-Range/ETag 逐字节可控
        // (tiny_http 对「声明长度>实发字节」会自行降级成 EOF 定界,模拟不出真中断)。

        fn test_payload(len: usize) -> Vec<u8> {
            (0..len).map(|i| ((i * 31 + 7) % 251) as u8).collect()
        }

        fn read_request(stream: &mut TcpStream) -> String {
            let mut buf = [0u8; 8192];
            let mut req: Vec<u8> = Vec::new();
            loop {
                let n = stream.read(&mut buf).unwrap_or(0);
                if n == 0 {
                    break;
                }
                req.extend_from_slice(&buf[..n]);
                if req.windows(4).any(|w| w == b"\r\n\r\n") {
                    break;
                }
            }
            String::from_utf8_lossy(&req).to_string()
        }

        fn range_of(req: &str) -> Option<String> {
            req.lines().find_map(|line| {
                line.to_ascii_lowercase()
                    .strip_prefix("range:")
                    .map(|v| v.trim().to_string())
            })
        }

        fn parse_range_offset(range: &str) -> usize {
            range
                .trim_start_matches("bytes=")
                .trim_end_matches('-')
                .parse()
                .unwrap()
        }

        /// 200 响应:声明完整长度但只发 body 前缀,随即硬断连接(真·下载中断)。
        fn write_200_interrupted(
            stream: &mut TcpStream,
            full_len: usize,
            prefix: &[u8],
            etag: &str,
        ) {
            let head = format!(
                "HTTP/1.1 200 OK\r\nContent-Length: {}\r\nETag: {}\r\nConnection: close\r\n\r\n",
                full_len, etag
            );
            let _ = stream.write_all(head.as_bytes());
            let _ = stream.write_all(prefix);
            let _ = stream.flush();
            let _ = stream.shutdown(Shutdown::Both);
        }

        fn write_206(stream: &mut TcpStream, full: &[u8], offset: usize, etag: &str) {
            let body = &full[offset..];
            let head = format!(
                "HTTP/1.1 206 Partial Content\r\nContent-Length: {}\r\nContent-Range: bytes {}-{}/{}\r\nETag: {}\r\nConnection: close\r\n\r\n",
                body.len(),
                offset,
                full.len() - 1,
                full.len(),
                etag
            );
            let _ = stream.write_all(head.as_bytes());
            let _ = stream.write_all(body);
            let _ = stream.flush();
            let _ = stream.shutdown(Shutdown::Both);
        }

        fn write_200_full(stream: &mut TcpStream, full: &[u8], etag: &str) {
            let head = format!(
                "HTTP/1.1 200 OK\r\nContent-Length: {}\r\nETag: {}\r\nConnection: close\r\n\r\n",
                full.len(),
                etag
            );
            let _ = stream.write_all(head.as_bytes());
            let _ = stream.write_all(full);
            let _ = stream.flush();
            let _ = stream.shutdown(Shutdown::Both);
        }

        fn spawn_server() -> (TcpListener, String) {
            let listener = TcpListener::bind("127.0.0.1:0").unwrap();
            let port = listener.local_addr().unwrap().port();
            let url = format!("http://127.0.0.1:{}/asset.bin", port);
            (listener, url)
        }

        #[test]
        fn resume_completes_via_range_206() {
            let full = test_payload(300_000);
            let (server, url) = spawn_server();
            let ranges: Arc<Mutex<Vec<Option<String>>>> = Arc::new(Mutex::new(Vec::new()));
            let (ranges_srv, full_srv) = (ranges.clone(), full.clone());
            let handle = thread::spawn(move || {
                let mut s = server.accept().unwrap().0;
                let req = read_request(&mut s);
                ranges_srv.lock().unwrap().push(range_of(&req));
                write_200_interrupted(&mut s, full_srv.len(), &full_srv[..131_072], "\"v1\"");
                let mut s = server.accept().unwrap().0;
                let req = read_request(&mut s);
                let range = range_of(&req);
                let offset = parse_range_offset(range.as_deref().unwrap());
                ranges_srv.lock().unwrap().push(range);
                write_206(&mut s, &full_srv, offset, "\"v1\"");
            });
            let dir = temp_test_dir("dl-resume-206");
            let dest = dir.join("asset.bin");
            let (part, meta) = download_part_paths(&dest);

            let first = download_resumable_once(&url, &dest, true, |_, _| {}, |_| {});
            assert!(first.is_err(), "被中断的下载必须失败");
            assert!(part.exists() && meta.exists(), "part/meta 必须保留供续传");
            assert!(!dest.exists(), "finalize 前 dest 绝不出现");

            let mut resumed_from = 0u64;
            download_resumable_once(&url, &dest, true, |off, _| resumed_from = off, |_| {})
                .expect("续传应成功");
            assert!(resumed_from > 0, "第二次必须走续传而非全新");
            assert_eq!(fs::read(&dest).unwrap(), full, "拼合内容必须逐字节一致");
            assert!(
                !part.exists() && !meta.exists(),
                "完成后 part/meta 必须清除"
            );
            let seen = ranges.lock().unwrap();
            assert!(seen[0].is_none(), "首个请求必须无 Range");
            assert!(seen[1].as_deref().unwrap_or("").starts_with("bytes="));
            drop(seen);
            handle.join().unwrap();
            let _ = fs::remove_dir_all(&dir);
        }

        #[test]
        fn server_ignoring_range_falls_back_to_full_200() {
            let full = test_payload(220_000);
            let (server, url) = spawn_server();
            let ranges: Arc<Mutex<Vec<Option<String>>>> = Arc::new(Mutex::new(Vec::new()));
            let (ranges_srv, full_srv) = (ranges.clone(), full.clone());
            let handle = thread::spawn(move || {
                let mut s = server.accept().unwrap().0;
                let req = read_request(&mut s);
                ranges_srv.lock().unwrap().push(range_of(&req));
                write_200_interrupted(&mut s, full_srv.len(), &full_srv[..100_000], "\"v1\"");
                // 无视 Range 回 200 全量:客户端应就地当全新流消费(截断重写)
                let mut s = server.accept().unwrap().0;
                let req = read_request(&mut s);
                ranges_srv.lock().unwrap().push(range_of(&req));
                write_200_full(&mut s, &full_srv, "\"v1\"");
            });
            let dir = temp_test_dir("dl-resume-200");
            let dest = dir.join("asset.bin");

            assert!(download_resumable_once(&url, &dest, true, |_, _| {}, |_| {}).is_err());
            let mut resumed_from = 42u64;
            download_resumable_once(&url, &dest, true, |off, _| resumed_from = off, |_| {})
                .expect("降级全新下载应成功");
            assert_eq!(resumed_from, 0, "200 降级后按全新下载起算");
            assert_eq!(fs::read(&dest).unwrap(), full);
            let seen = ranges.lock().unwrap();
            assert!(
                seen[1].as_deref().unwrap_or("").starts_with("bytes="),
                "第二次应先尝试 Range"
            );
            drop(seen);
            handle.join().unwrap();
            let _ = fs::remove_dir_all(&dir);
        }

        #[test]
        fn etag_change_discards_part_and_redownloads() {
            let old = test_payload(180_000);
            let fresh: Vec<u8> = test_payload(180_000).iter().map(|b| b ^ 0x5a).collect();
            let (server, url) = spawn_server();
            let ranges: Arc<Mutex<Vec<Option<String>>>> = Arc::new(Mutex::new(Vec::new()));
            let (ranges_srv, old_srv, fresh_srv) = (ranges.clone(), old.clone(), fresh.clone());
            let handle = thread::spawn(move || {
                let mut s = server.accept().unwrap().0;
                let req = read_request(&mut s);
                ranges_srv.lock().unwrap().push(range_of(&req));
                write_200_interrupted(&mut s, old_srv.len(), &old_srv[..90_000], "\"v1\"");
                // 内容已换版:206 但 etag 变 → 客户端必须弃续传
                let mut s = server.accept().unwrap().0;
                let req = read_request(&mut s);
                let range = range_of(&req);
                let offset = parse_range_offset(range.as_deref().unwrap());
                ranges_srv.lock().unwrap().push(range);
                write_206(&mut s, &fresh_srv, offset, "\"v2\"");
                // 客户端随即发全新请求
                let mut s = server.accept().unwrap().0;
                let req = read_request(&mut s);
                ranges_srv.lock().unwrap().push(range_of(&req));
                write_200_full(&mut s, &fresh_srv, "\"v2\"");
            });
            let dir = temp_test_dir("dl-resume-etag");
            let dest = dir.join("asset.bin");

            assert!(download_resumable_once(&url, &dest, true, |_, _| {}, |_| {}).is_err());
            let mut resumed_from = 42u64;
            download_resumable_once(&url, &dest, true, |off, _| resumed_from = off, |_| {})
                .expect("etag 变化后全新重下应成功");
            assert_eq!(resumed_from, 0, "etag 冲突必须放弃续传");
            assert_eq!(fs::read(&dest).unwrap(), fresh, "必须拿到新版内容,绝不混拼");
            let seen = ranges.lock().unwrap();
            assert_eq!(seen.len(), 3);
            assert!(seen[2].is_none(), "第三个请求必须是全新(无 Range)");
            drop(seen);
            handle.join().unwrap();
            let _ = fs::remove_dir_all(&dir);
        }

        #[test]
        fn no_resume_flag_forces_fresh_download() {
            let full = test_payload(160_000);
            let (server, url) = spawn_server();
            let ranges: Arc<Mutex<Vec<Option<String>>>> = Arc::new(Mutex::new(Vec::new()));
            let (ranges_srv, full_srv) = (ranges.clone(), full.clone());
            let handle = thread::spawn(move || {
                let mut s = server.accept().unwrap().0;
                let req = read_request(&mut s);
                ranges_srv.lock().unwrap().push(range_of(&req));
                write_200_interrupted(&mut s, full_srv.len(), &full_srv[..80_000], "\"v1\"");
                let mut s = server.accept().unwrap().0;
                let req = read_request(&mut s);
                ranges_srv.lock().unwrap().push(range_of(&req));
                write_200_full(&mut s, &full_srv, "\"v1\"");
            });
            let dir = temp_test_dir("dl-resume-off");
            let dest = dir.join("asset.bin");
            let (part, meta) = download_part_paths(&dest);

            assert!(download_resumable_once(&url, &dest, true, |_, _| {}, |_| {}).is_err());
            assert!(part.exists());
            download_resumable_once(&url, &dest, false, |_, _| {}, |_| {})
                .expect("kill-switch 全新下载应成功");
            assert_eq!(fs::read(&dest).unwrap(), full);
            let seen = ranges.lock().unwrap();
            assert!(
                seen[1].is_none(),
                "HOROSA_DOWNLOAD_NO_RESUME 语义:第二次不得带 Range"
            );
            assert!(!part.exists() && !meta.exists());
            drop(seen);
            handle.join().unwrap();
            let _ = fs::remove_dir_all(&dir);
        }

        #[test]
        fn native_extract_parity_with_external_tar() {
            use super::super::{
                extract_tar_gz_native_with, tar_extract_external, SMALL_FILE_LIMIT,
            };
            use std::os::unix::fs::MetadataExt;
            use std::os::unix::fs::PermissionsExt;

            // fixture:普通/中文名/exec 位/symlink/硬链/深嵌套/超过小文件阈值的大文件(全零,gz 后极小)
            let dir = temp_test_dir("extract-parity");
            let src = dir.join("src/runtime-payload");
            fs::create_dir_all(src.join("nested/深层目录")).unwrap();
            fs::write(src.join("plain.txt"), b"hello horosa").unwrap();
            fs::write(
                src.join("nested/深层目录/星阙测试.dat"),
                test_payload(70_000),
            )
            .unwrap();
            fs::write(src.join("tool.sh"), b"#!/bin/sh\necho ok\n").unwrap();
            fs::set_permissions(src.join("tool.sh"), fs::Permissions::from_mode(0o755)).unwrap();
            let big = vec![0u8; (SMALL_FILE_LIMIT + 1024) as usize];
            fs::write(src.join("big.bin"), &big).unwrap();
            std::os::unix::fs::symlink("plain.txt", src.join("link-to-plain")).unwrap();

            // 打包(gnu tar builder;follow_symlinks(false) 保 symlink 条目本体;
            // 硬链条目手工构造——append_dir_all 不追踪 inode,会把硬链归成两个独立 Regular)
            let archive = dir.join("fixture.tar.gz");
            {
                let tar_gz = File::create(&archive).unwrap();
                let encoder = GzEncoder::new(tar_gz, Compression::default());
                let mut builder = Builder::new(encoder);
                builder.follow_symlinks(false);
                builder.append_dir_all("runtime-payload", &src).unwrap();
                let mut link_header = tar::Header::new_gnu();
                link_header.set_entry_type(tar::EntryType::Link);
                link_header.set_size(0);
                link_header.set_mode(0o644);
                builder
                    .append_link(
                        &mut link_header,
                        "runtime-payload/hard-to-plain",
                        "runtime-payload/plain.txt",
                    )
                    .unwrap();
                builder.finish().unwrap();
            }

            // 三方解压:native 顺序(=1)/native 并发(=4)/外部 /usr/bin/tar
            let out_seq = dir.join("out-seq");
            let out_par = dir.join("out-par");
            let out_ext = dir.join("out-ext");
            fs::create_dir_all(&out_ext).unwrap();
            extract_tar_gz_native_with(&archive, &out_seq, 1, 1, None).expect("native 顺序");
            let reported = std::cell::Cell::new((0u64, 0u64, 0u64));
            let cb = |read: u64, total: u64, files: u64| {
                reported.set((read, total, files));
            };
            extract_tar_gz_native_with(&archive, &out_par, 1, 4, Some(&cb)).expect("native 并发");
            let (rep_read, rep_total, rep_files) = reported.get();
            assert_eq!(rep_read, rep_total, "终报进度必须收敛到 100%");
            assert!(rep_files >= 6, "文件计数必须覆盖全部条目");
            tar_extract_external(&archive, &out_ext, true).expect("外部 tar");

            // 逐条目比对:路径集合/字节内容/mode/symlink 目标/硬链 inode 同一性/文件 mtime
            fn walk(root: &Path) -> Vec<PathBuf> {
                let mut out = Vec::new();
                let mut stack = vec![root.to_path_buf()];
                while let Some(cur) = stack.pop() {
                    for e in fs::read_dir(&cur).unwrap() {
                        let p = e.unwrap().path();
                        out.push(p.strip_prefix(root).unwrap().to_path_buf());
                        if p.is_dir() && !p.symlink_metadata().unwrap().file_type().is_symlink() {
                            stack.push(p);
                        }
                    }
                }
                out.sort();
                out
            }
            let listing = walk(&out_seq);
            assert_eq!(listing, walk(&out_par), "顺序/并发 路径集合必须一致");
            assert_eq!(listing, walk(&out_ext), "native/外部tar 路径集合必须一致");
            assert!(!listing.is_empty());
            for rel in &listing {
                let a = out_seq.join(rel);
                let b = out_par.join(rel);
                let c = out_ext.join(rel);
                let meta_a = a.symlink_metadata().unwrap();
                if meta_a.file_type().is_symlink() {
                    let ta = fs::read_link(&a).unwrap();
                    assert_eq!(ta, fs::read_link(&b).unwrap(), "symlink 目标 {rel:?}");
                    assert_eq!(ta, fs::read_link(&c).unwrap(), "symlink 目标 {rel:?}");
                    continue;
                }
                if meta_a.is_dir() {
                    continue;
                }
                let bytes_a = fs::read(&a).unwrap();
                assert_eq!(bytes_a, fs::read(&b).unwrap(), "内容 {rel:?}");
                assert_eq!(bytes_a, fs::read(&c).unwrap(), "内容 {rel:?}");
                let mode_a = meta_a.permissions().mode() & 0o7777;
                let mode_b = b.symlink_metadata().unwrap().permissions().mode() & 0o7777;
                let mode_c = c.symlink_metadata().unwrap().permissions().mode() & 0o7777;
                assert_eq!(mode_a, mode_b, "mode {rel:?}");
                assert_eq!(mode_a, mode_c, "mode {rel:?}");
                let mt = |p: &Path| {
                    p.symlink_metadata()
                        .unwrap()
                        .modified()
                        .unwrap()
                        .duration_since(UNIX_EPOCH)
                        .unwrap()
                        .as_secs()
                };
                assert_eq!(mt(&a), mt(&b), "mtime {rel:?}");
                assert_eq!(mt(&a), mt(&c), "mtime {rel:?}");
            }
            // 硬链同一性:hard-to-plain 与 plain.txt 同 inode(三方各自内部核对)
            for root in [&out_seq, &out_par, &out_ext] {
                let ino_plain = root.join("plain.txt").metadata().unwrap().ino();
                let ino_hard = root.join("hard-to-plain").metadata().unwrap().ino();
                assert_eq!(ino_plain, ino_hard, "硬链 inode 同一性 {root:?}");
            }
            // exec 位专项:tool.sh 三方都必须 0o755
            for root in [&out_seq, &out_par, &out_ext] {
                let mode = root
                    .join("tool.sh")
                    .metadata()
                    .unwrap()
                    .permissions()
                    .mode()
                    & 0o777;
                assert_eq!(mode, 0o755, "exec 位 {root:?}");
            }
            let _ = fs::remove_dir_all(&dir);
        }

        #[test]
        fn native_extract_rejects_path_escape() {
            use super::super::extract_tar_gz_native_with;
            // 恶意归档:条目路径带 ../ → 必须整体报错,绝不落盘到 dest 之外
            let dir = temp_test_dir("extract-escape");
            let archive = dir.join("evil.tar.gz");
            {
                let tar_gz = File::create(&archive).unwrap();
                let encoder = GzEncoder::new(tar_gz, Compression::default());
                let mut builder = Builder::new(encoder);
                let data = b"evil";
                let mut header = tar::Header::new_gnu();
                // Builder::append_data 自己拒 `..`(打包端防护)——直接写 header 名字段造恶意条目
                let name = b"root/../../escape.txt";
                header.as_old_mut().name[..name.len()].copy_from_slice(name);
                header.set_size(data.len() as u64);
                header.set_mode(0o644);
                header.set_cksum();
                builder.append(&header, &data[..]).unwrap();
                builder.finish().unwrap();
            }
            let out = dir.join("out");
            let err = extract_tar_gz_native_with(&archive, &out, 0, 1, None);
            assert!(err.is_err(), "路径逃逸归档必须报错");
            assert!(!dir.join("escape.txt").exists(), "逃逸文件绝不落盘");
            assert!(
                !dir.parent().unwrap().join("escape.txt").exists(),
                "逃逸文件绝不落盘到上层"
            );
            let _ = fs::remove_dir_all(&dir);
        }

        #[test]
        fn manifest_fetch_three_outcomes() {
            // 200+合法 JSON → Fetched;404 → Absent;200+坏 JSON → Absent(掉 API fallback)
            let client = build_github_client(10).unwrap();
            let cases: Vec<(Option<&[u8]>, bool)> = vec![
                (
                    Some(br#"{"version":"9.9.9","tag":"v9.9.9","platforms":{}}"#),
                    true,
                ),
                (None, false),
                (Some(b"not-json"), false),
            ];
            for (idx, (body, expect_fetched)) in cases.into_iter().enumerate() {
                let (server, base) = spawn_server();
                let manifest_url = base.replace("/asset.bin", "/horosa-latest.json");
                let handle = thread::spawn(move || {
                    let mut s = server.accept().unwrap().0;
                    let _ = read_request(&mut s);
                    match body {
                        Some(bytes) => write_200_full(&mut s, bytes, "\"m\""),
                        None => {
                            let head = "HTTP/1.1 404 Not Found\r\nContent-Length: 0\r\nConnection: close\r\n\r\n";
                            let _ = s.write_all(head.as_bytes());
                            let _ = s.shutdown(Shutdown::Both);
                        }
                    }
                });
                let got = fetch_update_manifest(&client, &manifest_url);
                assert_eq!(
                    matches!(got, ManifestFetch::Fetched(_)),
                    expect_fetched,
                    "case {} 结果不符",
                    idx + 1
                );
                handle.join().unwrap();
            }
        }

        #[test]
        fn resume_attempts_cap_forces_fresh() {
            let full = test_payload(140_000);
            let (server, url) = spawn_server();
            let ranges: Arc<Mutex<Vec<Option<String>>>> = Arc::new(Mutex::new(Vec::new()));
            let (ranges_srv, full_srv) = (ranges.clone(), full.clone());
            let handle = thread::spawn(move || {
                let mut s = server.accept().unwrap().0;
                let req = read_request(&mut s);
                ranges_srv.lock().unwrap().push(range_of(&req));
                write_200_full(&mut s, &full_srv, "\"v1\"");
            });
            let dir = temp_test_dir("dl-resume-cap");
            let dest = dir.join("asset.bin");
            let (part, meta) = download_part_paths(&dest);
            // 预造「续传次数已封顶」的病态 part:必须直接全新,防续传死循环
            fs::write(&part, &full[..70_000]).unwrap();
            save_part_meta(
                &meta,
                &PartMeta {
                    url: url.clone(),
                    etag: Some("\"v1\"".to_string()),
                    total: full.len() as u64,
                    resume_attempts: RESUME_MAX_ATTEMPTS,
                },
            );

            download_resumable_once(&url, &dest, true, |_, _| {}, |_| {})
                .expect("封顶后全新下载应成功");
            assert_eq!(fs::read(&dest).unwrap(), full);
            let seen = ranges.lock().unwrap();
            assert!(seen[0].is_none(), "封顶后不得再发 Range");
            drop(seen);
            handle.join().unwrap();
            let _ = fs::remove_dir_all(&dir);
        }
    }
}
