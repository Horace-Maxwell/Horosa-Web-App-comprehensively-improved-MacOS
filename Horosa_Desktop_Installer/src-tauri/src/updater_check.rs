//! 检查更新:节流、对话框、说明摘要与运行时更新决策。

use super::*;

pub(crate) fn open_release_page(app: &AppHandle) -> Result<()> {
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

pub(crate) fn parse_version(tag: &str) -> Result<Version> {
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
            shell_text_fmt("update.runtime.latest", &[("local", local.trim())])
        }
        (Some(local), Some(remote)) => format!("{} -> {}", local.trim(), remote.trim()),
        (None, Some(remote)) => {
            shell_text_fmt("update.runtime.not_installed", &[("remote", remote.trim())])
        }
        (Some(local), None) if !local.trim().is_empty() => {
            shell_text_fmt("update.runtime.remote_unknown", &[("local", local.trim())])
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
    let status = shell_text(if latest > current {
        "update.status.available"
    } else if runtime_needs_update {
        "update.status.runtime_only"
    } else if latest == current {
        "update.status.latest"
    } else {
        "update.status.ahead"
    });
    let update_source = shell_text(match source {
        UpdateSource::Manifest => "update.source.manifest",
        UpdateSource::ManifestViaApi => "update.source.manifest_via_api",
        UpdateSource::GithubApi => "update.source.github_api",
    });
    let summary = summarize_update_notes(notes);
    let changelog = normalize_update_notes(notes);
    let current = current.to_string();
    let latest = latest.to_string();
    let runtime = format_runtime_status(local_runtime, remote_runtime);
    shell_text_fmt(
        "update.summary",
        &[
            ("status", status.as_str()),
            ("current", current.as_str()),
            ("latest", latest.as_str()),
            ("runtime", runtime.as_str()),
            ("source", update_source.as_str()),
            ("summary", summary.as_str()),
            ("changelog", changelog.as_str()),
            ("repo", repo_url),
            ("release", release_url),
        ],
    )
}

pub(crate) fn check_for_updates(app: AppHandle) -> Result<()> {
    let client = build_github_client(90)?;
    let plan = resolve_update_plan(&client, &app)?;
    // 手动检查不受节流,但成功同样计入节流窗
    write_update_check_stamp(&app);
    let current = Version::parse(env!("CARGO_PKG_VERSION"))?;
    let local_runtime = local_runtime_version(&app);
    let runtime_needs_update =
        runtime_update_decision(&app, &plan, &local_runtime) == RuntimeUpdateDecision::Needed;
    let admin_update_notice = app_bundle_path()
        .filter(|path| target_requires_admin_update(path))
        .map(|_| shell_text("dlg.update_found.admin_notice"))
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
            .set_title(shell_text("dlg.update_result.title"))
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
            .set_title(shell_text("dlg.update_notify.title"))
            .set_description(match &plan.full_pkg_reason {
                Some(_) => format!("{summary}\n\n{}", plan.notify_only_message()),
                None => shell_text_fmt(
                    "dlg.update_notify.manifest_unavailable",
                    &[("summary", summary.as_str())],
                ),
            })
            .set_buttons(MessageButtons::OkCancelCustom(
                shell_text("btn.open_release_page"),
                shell_text("btn.later"),
            ))
            .show();
        if open_page == MessageDialogResult::Custom(shell_text("btn.open_release_page")) {
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
        .set_title(shell_text("dlg.update_found.title"))
        .set_description(shell_text_fmt(
            "dlg.update_found.body",
            &[
                ("summary", summary.as_str()),
                ("notice", admin_update_notice.as_str()),
            ],
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
            .set_title(shell_text("dlg.update_starting.title"))
            .set_description(shell_text("dlg.update_starting.body"))
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
            .set_title(shell_text("dlg.update_skipped.title"))
            .set_description(shell_text("dlg.update_skipped.body"))
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
pub(crate) struct UpdateAvailability {
    pub(crate) available: bool,
    pub(crate) current_version: String,
    pub(crate) latest_version: String,
    pub(crate) runtime_needs_update: bool,
    pub(crate) notes: String,
    pub(crate) release_url: String,
    // 可视化 v2(全部 optional 语义:老前端忽略,新前端判空退化)
    pub(crate) update_mode: Option<String>, // "incremental" | "full"
    pub(crate) download_bytes: Option<u64>, // 预计下载量
    pub(crate) reuse_pct: Option<u8>,       // 增量复用率
    changed_components: Vec<String>,        // 变化部件名
    // 无 sha 可校验(manifest 与其 asset 双双不可得)→ 只通知不安装
    pub(crate) notify_only: bool,
}

// runtime 更新判定:单一真值函数,菜单/静默检查/后台下载/自动检查四处共用
// (此前三处内联手抄同一段判定,已全部收口——内联回潮由 preflight[101] 反向锚拦)。
// 语义:runtime_version_rank 单调比较,remote 更新才更;remote 更旧=DowngradeBlocked
// (不动作,防 latest 指针异常/回滚把用户静默降级);任一侧 rank 解析失败回退老「不同即更」
// 语义(防脏版本串永久卡死更新链);allow_downgrade(env HOROSA_ALLOW_DOWNGRADE=1 或
// manifest allowDowngrade,应急全网退版剧本见 INCREMENTAL_UPDATE_SOP §4.3)恢复老语义。
#[derive(Debug, Clone, Copy, PartialEq, Eq)]
pub(crate) enum RuntimeUpdateDecision {
    UpToDate,
    Needed,
    DowngradeBlocked,
}

pub(crate) fn compute_runtime_update_decision(
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
pub(crate) fn runtime_update_decision(
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
        // 台账:降级拦截
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

// 自动检查:启动首查距上次成功检查 <4h 跳过;驻留线程每 24h
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

pub(crate) fn auto_update_check_cycle() -> Duration {
    Duration::from_secs(auto_check_interval_override().unwrap_or(AUTO_CHECK_CYCLE_SECS))
}

fn update_check_stamp_path(app: &AppHandle) -> Option<PathBuf> {
    app.path()
        .app_data_dir()
        .ok()
        .map(|d| d.join("last-update-check.json"))
}

pub(crate) fn load_update_check_stamp(path: &Path) -> Option<u64> {
    let data = fs::read_to_string(path).ok()?;
    let json: serde_json::Value = serde_json::from_str(&data).ok()?;
    json.get("lastCheckMs").and_then(|v| v.as_u64())
}

pub(crate) fn write_update_check_stamp_at(path: &Path) {
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
pub(crate) fn should_run_auto_check(
    last_ms: Option<u64>,
    now_ms: u64,
    min_interval_ms: u64,
) -> bool {
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
    // 台账:检查失败(耐久留痕,排障可回看「源不可达从何时开始」)
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

// 自动检查本体(原启动一次性线程体抽出,供 启动首查/24h 周期共用;
// U-C staged 断点恢复挂接于此)。
pub(crate) fn run_auto_update_check(app: &AppHandle) {
    let now_ms = SystemTime::now()
        .duration_since(UNIX_EPOCH)
        .map(|d| d.as_millis() as u64)
        .unwrap_or(0);
    // 先看有无上次「已下载完成未安装」的暂存档(过期/坏档/资产被动即删)
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
            // 复用:回填内存槽 + 直接 ready(零重下)
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
        payload["message"] = serde_json::json!(plan.notify_only_message());
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

/// 本地版本号(不联网、不写节流戳):「关于星阙」只需要版本号,此前它调 update_check_silent ——
/// 一打开就联网查更新、无视「自动检查更新」偏好、把「有新版」结果丢掉,还把 4 小时节流窗刷新一次
/// (导致启动时本该弹的新版提示被推迟);离线时请求失败连版本号都显示不出来。
#[tauri::command]
pub(crate) fn app_version_local_command(app: AppHandle) -> LocalVersionInfo {
    LocalVersionInfo {
        app_version: env!("CARGO_PKG_VERSION").to_string(),
        runtime_version: local_runtime_version(&app).unwrap_or_default(),
    }
}

#[derive(Debug, Clone, Serialize)]
#[serde(rename_all = "camelCase")]
pub(crate) struct LocalVersionInfo {
    pub(crate) app_version: String,
    pub(crate) runtime_version: String,
}

#[tauri::command]
pub(crate) fn update_check_silent(
    app: AppHandle,
) -> std::result::Result<UpdateAvailability, String> {
    (|| -> Result<UpdateAvailability> {
        let client = build_github_client(90)?;
        let plan = resolve_update_plan(&client, &app)?;
        // 前端手动检查同样计入节流窗
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
