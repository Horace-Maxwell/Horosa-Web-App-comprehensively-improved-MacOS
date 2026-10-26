//! 本机已有资产的清点、审查、提交与清理,离线重装入口。

use super::*;

#[derive(Debug, Clone, Copy, Serialize, Deserialize, PartialEq, Eq)]
#[serde(rename_all = "snake_case")]
pub(crate) enum AssetReviewMode {
    Install,
    Repair,
    Update,
}

impl AssetReviewMode {
    pub(crate) fn title(self) -> &'static str {
        match self {
            Self::Install => "安装审查",
            Self::Repair => "修复审查",
            Self::Update => "更新审查",
        }
    }

    pub(crate) fn progress_copy(self) -> &'static str {
        match self {
            Self::Install => "检查已安装内容",
            Self::Repair => "检查待修复内容",
            Self::Update => "检查将替换的内容",
        }
    }
}

#[derive(Debug, Clone, Copy, Serialize, Deserialize, PartialEq, Eq, Hash)]
#[serde(rename_all = "snake_case")]
pub(crate) enum DetectedAssetKind {
    InstalledApp,
    SharedRuntime,
    UserRuntime,
    PendingMarker,
    CachedRuntimeArchive,
    CachedAppUpdate,
}

impl DetectedAssetKind {
    pub(crate) fn key(self) -> &'static str {
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
pub(crate) enum DetectedAssetState {
    Healthy,
    Outdated,
    Broken,
    Pending,
    CacheOnly,
}

#[derive(Debug, Clone, Copy, Serialize, Deserialize, PartialEq, Eq)]
#[serde(rename_all = "snake_case")]
pub(crate) enum AssetDecision {
    Replace,
    Keep,
}

#[derive(Debug, Clone, Serialize, Deserialize)]
#[serde(rename_all = "camelCase")]
pub(crate) struct AssetInventoryItem {
    pub(crate) kind: DetectedAssetKind,
    pub(crate) label: String,
    pub(crate) path: String,
    pub(crate) state: DetectedAssetState,
    replace_recommended: bool,
    pub(crate) requires_admin: bool,
    pub(crate) details: String,
}

#[derive(Debug, Clone, Serialize, Deserialize)]
#[serde(rename_all = "camelCase")]
pub(crate) struct AssetReviewPayload {
    pub(crate) mode: AssetReviewMode,
    pub(crate) items: Vec<AssetInventoryItem>,
    blocking_issues: Vec<String>,
    pub(crate) default_selections: HashMap<String, AssetDecision>,
}

#[derive(Debug, Clone, Deserialize)]
#[serde(rename_all = "camelCase")]
pub(crate) struct AssetReviewCommitRequest {
    pub(crate) mode: AssetReviewMode,
    pub(crate) decisions: HashMap<String, AssetDecision>,
    pub(crate) cancelled: bool,
}

#[derive(Debug, Clone, Serialize)]
#[serde(rename_all = "camelCase")]
pub(crate) struct AssetReviewCommitResult {
    pub(crate) allowed: bool,
    blocking_issues: Vec<String>,
}

#[derive(Default)]
pub(crate) struct PendingAssetReviewState {
    pub(crate) payload: Option<AssetReviewPayload>,
    pub(crate) response: Option<AssetReviewCommitRequest>,
}

pub(crate) struct AssetReviewCoordinator {
    pub(crate) state: Mutex<PendingAssetReviewState>,
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

pub(crate) fn wait_for_asset_review(
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

pub(crate) fn clear_selected_assets_internal(
    app: &AppHandle,
    decisions: &HashMap<String, AssetDecision>,
) -> Result<Vec<String>> {
    let config = load_release_config(app)?;
    let mut cleared = Vec::new();

    if decision_for_kind(decisions, DetectedAssetKind::PendingMarker) == AssetDecision::Replace {
        let path = shared_runtime_pending_path();
        if path.exists() {
            match fs::remove_file(&path) {
                Ok(()) => cleared.push("已清理待处理安装标记".to_string()),
                // 标记在共享目录里、归安装者:其他账户删不动不算失败(与 clear_runtime_pending_marker 同口径)
                Err(err) if err.kind() == std::io::ErrorKind::PermissionDenied => {}
                Err(err) => {
                    return Err(err)
                        .with_context(|| format!("remove pending marker {}", path.display()))
                }
            }
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

pub(crate) fn replace_installed_app_if_selected(
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

pub(crate) fn open_offline_reinstall_flow(app: &AppHandle) -> Result<()> {
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
        .set_title(shell_text("dlg.reinstall.title"))
        .set_description(shell_text_fmt(
            "dlg.reinstall.not_found",
            &[("pkg", config.desktop_offline_pkg_name.as_str())],
        ))
        .set_buttons(MessageButtons::Ok)
        .show();
    Ok(())
}

#[tauri::command]
pub(crate) fn commit_asset_review(
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

pub(crate) fn decision_for_kind(
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

pub(crate) fn build_asset_review_payload(
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

pub(crate) fn should_recommend_installed_app_replacement(
    _mode: AssetReviewMode,
    state: DetectedAssetState,
) -> bool {
    state == DetectedAssetState::Outdated
}

pub(crate) fn validate_asset_review_payload(
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

pub(crate) fn should_present_review(app: &AppHandle, payload: &AssetReviewPayload) -> bool {
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
