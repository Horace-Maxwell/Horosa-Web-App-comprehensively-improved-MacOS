//! 后台下载、暂存持久化与暂存安装。

use super::*;

// 后台下载校验完成的更新落盘 staged-update.json;下次启动
// (run_auto_update_check 开头)逐资产重验 sha + 与线上 latest 核对后直接恢复
// 「已就绪」——保守复用策略:manifest 必须可达且 target==线上 latest 才复用
// (无签名信任模型下「线上撤版」唯一挡板就是最新性核对);拉取失败留档下次再验。
const STAGED_UPDATE_MAX_AGE_MS: u64 = 7 * 24 * 3600 * 1000;

#[derive(Serialize, Deserialize)]
pub(crate) struct PersistedStagedUpdate {
    #[serde(default)]
    saved_at_ms: u64,
    pub(crate) staged: StagedUpdate,
    // 各资产落盘时自算 sha(不抄 manifest——GithubApi 源 app_sha256=None 也能护)
    #[serde(default)]
    asset_shas: Vec<PersistedAssetSha>,
}

#[derive(Serialize, Deserialize)]
pub(crate) struct PersistedAssetSha {
    pub(crate) path: PathBuf,
    pub(crate) sha256: String,
}

pub(crate) fn staged_update_file_path(app: &AppHandle) -> Option<PathBuf> {
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

pub(crate) fn persist_staged_update_file_at(path: &Path, staged: &StagedUpdate) -> Result<()> {
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
pub(crate) fn load_staged_update_file_at(path: &Path, now_ms: u64) -> Option<StagedUpdate> {
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
pub(crate) fn staged_matches_plan(
    staged: &StagedUpdate,
    latest: &str,
    runtime_version: &Option<String>,
) -> bool {
    staged.target_version == latest && staged.runtime_version == *runtime_version
}

// 清已消费的部件归档+lock 临时档(部件档只进不出会漏磁盘;全量 runtime/app
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

pub(crate) fn download_update_asset(
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
                "message": plan.notify_only_message(),
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
    // 落盘持久化:进程被杀/用户退出后,已下载校验的成果下次启动直接恢复(免重下)
    persist_staged_update_file(app, &staged);
    // 台账:下载校验完成(耐久行,进程死也留痕)
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
pub(crate) fn update_start_background(app: AppHandle) -> std::result::Result<(), String> {
    thread::spawn(move || {
        if let Err(err) = run_background_update_download(&app) {
            update_ledger_clear();
            // 台账:下载失败
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
    // 台账:开始应用
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
                    native_prewarm_after_runtime_update(
                        &root.join("current"),
                        &notify,
                        "update-incremental",
                    );
                }
            }
        }
        // 增量手术已成:清已消费部件档;交 helper 前消费暂存档(helper 接管即
        // 不可回头;此后 kill 由 helper 自身重试/回滚兜底,不再走 staged 恢复)。
        cleanup_consumed_component_archives(&staged);
        clear_staged_update_file(app);
        // 台账:交接 helper(结果由 install_confirmed 闭环)
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
                native_prewarm_after_runtime_update(
                    &root.join("current"),
                    &notify,
                    "update-incremental",
                );
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
                native_prewarm_after_runtime_update(&root.join("current"), &notify, "update-full");
            }
        }
        // 全部 root 应用成功:清已消费部件档+暂存档(失败路径 ? 早退不清,重试免重下)
        cleanup_consumed_component_archives(&staged);
        clear_staged_update_file(app);
        // 台账:runtime 更新应用成功(app 不换壳路径的结果行)
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
pub(crate) fn update_install_and_restart(app: AppHandle) -> std::result::Result<(), String> {
    run_staged_install(&app).map_err(|e| {
        // 台账:应用失败(staged 档保留,重试免重下)
        append_update_history(
            &app,
            serde_json::json!({ "event": "apply_failed", "error": format!("{e:#}") }),
        );
        format!("{e:#}")
    })
}
