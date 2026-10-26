//! 运行时安装与从缓存归档自愈。

use super::*;

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
        // 归档会被解压进本账户的运行目录并执行:别的账户能写的位置 / 与安装记录 sha 不符的一律不用
        if let Err(why) = cached_archive_trust(archive) {
            emit_status(
                window,
                &format!("跳过本地缓存归档 {}:{}", archive.display(), why),
            );
            last_err = Some(anyhow!(
                "untrusted runtime archive {}: {}",
                archive.display(),
                why
            ));
            continue;
        }
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
    // 共享运行环境只给安装它的账户写:本账户只读时不去修它,交给下面的「恢复当前用户本机组件」
    if !path_writable_by_current_user(&shared_runtime_root()) {
        return Ok(None);
    }
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

/// 要换掉的运行环境落到哪些根。共享运行环境只给安装它的账户写:多账户机上的其他账户选了「替换共享」,
/// 实际换进自己的用户目录(共享那份照旧只读加载;两份都可用时按版本取新的,见 choose_runtime_dir)。
/// 返回 (根列表, 是否改道)。
pub(crate) fn install_roots_for_decisions(
    shared_replace: bool,
    user_replace: bool,
    shared_root: PathBuf,
    user_root: PathBuf,
    shared_writable: bool,
) -> (Vec<PathBuf>, bool) {
    let mut roots: Vec<PathBuf> = Vec::new();
    let mut redirected = false;
    if shared_replace {
        if shared_writable {
            roots.push(shared_root);
        } else {
            roots.push(user_root.clone());
            redirected = true;
        }
    }
    if user_replace && !roots.contains(&user_root) {
        roots.push(user_root);
    }
    (roots, redirected)
}

pub(crate) fn selected_runtime_roots(
    app: &AppHandle,
    decisions: &HashMap<String, AssetDecision>,
) -> Result<Vec<PathBuf>> {
    let shared_replace =
        decision_for_kind(decisions, DetectedAssetKind::SharedRuntime) == AssetDecision::Replace;
    let user_replace =
        decision_for_kind(decisions, DetectedAssetKind::UserRuntime) == AssetDecision::Replace;
    let shared_root = runtime_root_for_kind(app, DetectedAssetKind::SharedRuntime)?;
    let shared_writable = !shared_replace || path_writable_by_current_user(&shared_root);
    let (roots, redirected) = install_roots_for_decisions(
        shared_replace,
        user_replace,
        shared_root,
        runtime_root_for_kind(app, DetectedAssetKind::UserRuntime)?,
        shared_writable,
    );
    if redirected {
        ledger_mark("rust.shared_runtime_readonly_redirect", None);
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

pub(crate) fn ensure_runtime_installed(
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
    if decision_for_kind(&decisions, DetectedAssetKind::SharedRuntime) == AssetDecision::Replace
        && !path_writable_by_current_user(&shared_runtime_root())
    {
        emit_status(
            window,
            "共享本机组件由安装它的账户维护，当前账户只能读取；这次会把本机组件装到当前用户自己的目录。",
        );
    }
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
        // [更新槽复用] 新解包的树里每个原生库都是新文件:在服务起来之前把首次加载评估做掉(带进度,不像卡住)
        let say_install = |msg: &str| emit_progress(window, 73, msg);
        native_prewarm_after_runtime_update(
            &runtime_root.join("current"),
            &say_install,
            "first-install",
        );
    }
    emit_progress(window, 74, "本机组件已准备完成");
    Ok(resolve_runtime_paths(app)?)
}
