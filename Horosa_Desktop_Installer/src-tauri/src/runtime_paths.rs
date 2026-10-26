//! 运行时目录、清单、版本比较、缓存路径与更新完成标记。

use super::*;

#[derive(Debug, Clone, Deserialize)]
pub(crate) struct RuntimeManifest {
    pub(crate) version: String,
    pub(crate) built_at: String,
}

#[derive(Debug, Clone, Serialize, Deserialize)]
#[serde(rename_all = "camelCase")]
pub(crate) struct RuntimeHealthCache {
    pub(crate) manifest_version: String,
    pub(crate) manifest_mtime: u64,
    pub(crate) python_mtime: u64,
    pub(crate) java_mtime: u64,
    pub(crate) checked_at: u64,
}

#[derive(Debug, Clone)]
pub(crate) struct RuntimePaths {
    pub(crate) app_data_dir: PathBuf,
    pub(crate) runtime_dir: PathBuf,
    pub(crate) logs_dir: PathBuf,
    pub(crate) frontend_dir: PathBuf,
    pub(crate) start_script: PathBuf,
    pub(crate) stop_script: PathBuf,
    pub(crate) manifest_path: PathBuf,
}

#[derive(Debug, Clone)]
pub(crate) struct RuntimeSession {
    pub(crate) paths: RuntimePaths,
    pub(crate) backend_port: u16,
    pub(crate) chart_port: u16,
    pub(crate) web_port: u16,
}

fn app_downloads_dir(app: &AppHandle) -> Result<PathBuf> {
    let dir = app.path().app_data_dir().context("missing app_data_dir")?;
    Ok(dir.join("downloads"))
}

pub(crate) fn cached_runtime_archive_path(
    app: &AppHandle,
    config: &ReleaseConfig,
) -> Result<PathBuf> {
    Ok(app_downloads_dir(app)?.join(&config.runtime_asset_name))
}

pub(crate) fn local_runtime_archive_candidates(
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

pub(crate) fn cached_app_update_path(app: &AppHandle, config: &ReleaseConfig) -> Result<PathBuf> {
    Ok(app_downloads_dir(app)?.join(&config.desktop_asset_name))
}

pub(crate) fn installed_app_target_path() -> PathBuf {
    PathBuf::from(format!("/Applications/{}.app", APP_NAME))
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

pub(crate) fn shared_runtime_dir() -> PathBuf {
    std::env::var_os("HOROSA_SHARED_RUNTIME_DIR")
        .map(PathBuf::from)
        .unwrap_or_else(|| PathBuf::from("/Users/Shared/Horosa/runtime/current"))
}

pub(crate) fn shared_runtime_root() -> PathBuf {
    shared_runtime_dir()
        .parent()
        .map(Path::to_path_buf)
        .unwrap_or_else(|| PathBuf::from("/Users/Shared/Horosa/runtime"))
}

pub(crate) fn shared_runtime_pending_path() -> PathBuf {
    shared_runtime_root()
        .parent()
        .map(|root| root.join("runtime-install-pending.txt"))
        .unwrap_or_else(|| PathBuf::from("/Users/Shared/Horosa/runtime-install-pending.txt"))
}

pub(crate) fn update_complete_marker_path(app: &AppHandle) -> Result<PathBuf> {
    let app_data_dir = app.path().app_data_dir().context("missing app_data_dir")?;
    ensure_dir(&app_data_dir)?;
    Ok(app_data_dir.join(UPDATE_COMPLETE_MARKER_NAME))
}

pub(crate) fn parse_marker_kv(data: &str) -> HashMap<String, String> {
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
    // 台账:install_confirmed——「vX→vY 结果」闭环行(helper 写标记,消费即记账;
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
pub(crate) fn consume_update_complete_marker_into_state(app: &AppHandle) -> bool {
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

pub(crate) fn show_post_update_notice_if_needed(app: &AppHandle) {
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
        show_macos_notification(
            &shell_text("notify.update_done.title"),
            &shell_text("notify.update_done.body"),
        );
    }
}

pub(crate) fn is_shared_runtime_dir(runtime_dir: &Path) -> bool {
    runtime_dir.starts_with(shared_runtime_root())
}

pub(crate) fn runtime_dir_has_required_files(runtime_dir: &Path) -> bool {
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

pub(crate) fn runtime_python_bin(runtime_dir: &Path) -> PathBuf {
    runtime_dir.join("runtime/mac/python/bin/python3")
}

pub(crate) fn runtime_java_bin(runtime_dir: &Path) -> PathBuf {
    runtime_dir.join("runtime/mac/java/bin/java")
}

fn is_runtime_metadata_junk(name: &str) -> bool {
    name == ".DS_Store" || name.starts_with("._")
}

pub(crate) fn cleanup_runtime_metadata(root: &Path) -> Result<u64> {
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
                let result = if file_type.is_dir() {
                    fs::remove_dir_all(&path)
                } else {
                    fs::remove_file(&path)
                };
                match result {
                    Ok(()) => removed += 1,
                    // 多账户机上其他账户只读加载共享运行环境:删不动的元数据垃圾留给属主清,
                    // 不能因此把整份运行环境判成「不可用」(否则会去重装 / 走修复)
                    Err(err) if err.kind() == std::io::ErrorKind::PermissionDenied => {}
                    Err(err) => return Err(err.into()),
                }
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
            // 与 start 脚本的真启动门(6 包)对齐——缺 cn2an/sxtwl/cnlunar 的树
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

/// 先写同目录临时文件再换名:目标若是别的身份(安装器 root)留下的只读旧文件,只要目录可写照样换得掉;
/// 中途断电也不会留下写了一半的文件。目录不可写(多账户机上的其他账户)→ 返回错误,调用方吞掉。
pub(crate) fn write_file_replacing(path: &Path, bytes: &[u8]) -> std::io::Result<()> {
    let name = path
        .file_name()
        .map(|n| n.to_string_lossy().to_string())
        .unwrap_or_default();
    let tmp = path.with_file_name(format!(".{name}.tmp.{}", std::process::id()));
    if let Err(err) = fs::write(&tmp, bytes) {
        let _ = fs::remove_file(&tmp);
        return Err(err);
    }
    fs::rename(&tmp, path).map_err(|err| {
        let _ = fs::remove_file(&tmp);
        err
    })
}

pub(crate) fn prepare_runtime_dir(runtime_dir: &Path) -> Result<()> {
    let _ = cleanup_runtime_metadata(runtime_dir)?;
    Ok(())
}

// 健康缓存的实物锚:python/java 可执行 + site-packages 三个真启动门关键包
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

/// 运行环境归属:runtime-manifest.json 的 appName 必须等于本应用(与 postinstall 的
/// runtime_dir_is_usable 同一判据)。身份戳从 2.6.6 起由打包脚本与增量更新写入;没有戳、
/// 读不出来或属于别的应用的,一律不复用,交由替换流程重装本应用的运行环境——两个应用版本号
/// 同步发布,同一共享目录先后装过两个应用时,只有这个戳分得清是谁的。
fn runtime_dir_owned_by_this_app(runtime_dir: &Path) -> bool {
    fs::read_to_string(runtime_dir.join("runtime-manifest.json"))
        .ok()
        .and_then(|text| serde_json::from_str::<serde_json::Value>(&text).ok())
        .and_then(|manifest| {
            manifest
                .get("appName")
                .and_then(|name| name.as_str())
                .map(|name| name == APP_NAME)
        })
        .unwrap_or(false)
}

pub(crate) fn runtime_dir_is_usable(runtime_dir: &Path) -> bool {
    if !runtime_dir_has_required_files(runtime_dir) {
        return false;
    }
    if !runtime_dir_owned_by_this_app(runtime_dir) {
        return false;
    }
    if let Some(cache) = runtime_health_cache(runtime_dir) {
        // 健康缓存加锚:mtime 三探针之外,关键实物必须仍在(同 mtime 隐性损坏
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

pub(crate) fn choose_runtime_dir(
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

pub(crate) fn resolve_runtime_paths(app: &AppHandle) -> Result<RuntimePaths> {
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

pub(crate) fn read_runtime_manifest(paths: &RuntimePaths) -> Option<RuntimeManifest> {
    let data = fs::read_to_string(&paths.manifest_path).ok()?;
    serde_json::from_str(&data).ok()
}

pub(crate) fn read_runtime_manifest_from_path(path: &Path) -> Option<RuntimeManifest> {
    let data = fs::read_to_string(path).ok()?;
    serde_json::from_str(&data).ok()
}

pub(crate) fn runtime_version_rank(version: &str) -> Option<(Version, u64)> {
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

pub(crate) fn local_runtime_version(app: &AppHandle) -> Option<String> {
    let paths = resolve_runtime_paths(app).ok()?;
    read_runtime_manifest(&paths).map(|m| m.version)
}

pub(crate) fn shared_runtime_matches_expected(expected_version: &str) -> bool {
    let shared_runtime = shared_runtime_dir();
    runtime_matches_expected(&shared_runtime, expected_version)
}

pub(crate) fn runtime_matches_expected(runtime_dir: &Path, expected_version: &str) -> bool {
    runtime_dir_is_usable(runtime_dir)
        && read_runtime_manifest_from_path(&runtime_dir.join("runtime-manifest.json"))
            .map(|manifest| manifest.version.trim() == expected_version.trim())
            .unwrap_or(false)
}

pub(crate) fn user_runtime_matches_expected(
    app: &AppHandle,
    expected_version: &str,
) -> Result<bool> {
    Ok(runtime_matches_expected(
        &user_runtime_dir(app)?,
        expected_version,
    ))
}

pub(crate) fn shared_runtime_paths(app: &AppHandle) -> Result<RuntimePaths> {
    let app_data_dir = app.path().app_data_dir().context("missing app_data_dir")?;
    Ok(runtime_paths_for_dir(app_data_dir, shared_runtime_dir()))
}

pub(crate) fn offline_install_marker_is_current(
    marker: &InstallSourceMarker,
    expected_runtime: &str,
) -> bool {
    marker.source == InstallSource::PkgOffline
        && marker
            .runtime_version
            .as_deref()
            .map(|version| version.trim() == expected_runtime.trim())
            .unwrap_or(false)
}

pub(crate) fn user_runtime_dir(app: &AppHandle) -> Result<PathBuf> {
    Ok(app
        .path()
        .app_data_dir()
        .context("missing app_data_dir")?
        .join("runtime/current"))
}

pub(crate) fn user_runtime_root(app: &AppHandle) -> Result<PathBuf> {
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

pub(crate) fn runtime_root_for_kind(app: &AppHandle, kind: DetectedAssetKind) -> Result<PathBuf> {
    let current = runtime_dir_for_kind(app, kind)?;
    Ok(current
        .parent()
        .map(Path::to_path_buf)
        .unwrap_or_else(|| current))
}
