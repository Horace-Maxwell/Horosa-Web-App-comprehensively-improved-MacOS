//! 运行时健康缓存、快路径标记、预置健康与启动看门狗。

use super::*;

pub(crate) fn runtime_health_cache_path(runtime_dir: &Path) -> PathBuf {
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

pub(crate) fn runtime_health_cache(runtime_dir: &Path) -> Option<RuntimeHealthCache> {
    let path = runtime_health_cache_path(runtime_dir);
    let text = fs::read_to_string(path).ok()?;
    serde_json::from_str(&text).ok()
}

fn runtime_fast_path_marker(runtime_dir: &Path) -> Option<RuntimeHealthCache> {
    let path = runtime_fast_path_marker_path(runtime_dir);
    let text = fs::read_to_string(path).ok()?;
    serde_json::from_str(&text).ok()
}

pub(crate) fn runtime_health_cache_matches(runtime_dir: &Path, cache: &RuntimeHealthCache) -> bool {
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

pub(crate) fn write_runtime_health_cache(runtime_dir: &Path, manifest: &RuntimeManifest) {
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
        let _ = write_file_replacing(&runtime_health_cache_path(runtime_dir), text.as_bytes());
    }
}

pub(crate) fn write_runtime_fast_path_marker(runtime_dir: &Path, manifest: &RuntimeManifest) {
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
        let _ = write_file_replacing(&runtime_fast_path_marker_path(runtime_dir), text.as_bytes());
    }
}

pub(crate) fn clear_runtime_health_cache(runtime_dir: &Path) {
    let _ = fs::remove_file(runtime_health_cache_path(runtime_dir));
}

pub(crate) fn clear_runtime_fast_path_marker(runtime_dir: &Path) {
    let _ = fs::remove_file(runtime_fast_path_marker_path(runtime_dir));
}

pub(crate) fn runtime_fast_path_allowed(runtime_dir: &Path) -> bool {
    runtime_fast_path_marker(runtime_dir)
        .map(|cache| runtime_health_cache_matches(runtime_dir, &cache))
        .unwrap_or(false)
}

// postinstall 预置信任子命令本体:安装器冒烟(python import+java -version)已证
// runtime 健康,此处以与 App 完全同一份格式代码预写健康缓存 + fast-path 标记,使首真启
// 直走 trusted 快路径(免 untrusted 深检/300s 预算档)。写后回验:探针实物缺位时
// write_* 会静默不写 → 回验不过=保持 untrusted(无害,首启照旧完整校验)。
// 退出码:0=预置成功;71=manifest 不可读;72=回验不过(探针缺位)。
pub(crate) fn run_preseed_health_cli(runtime_dir: &Path) -> i32 {
    let manifest_path = runtime_dir.join("runtime-manifest.json");
    let Some(manifest) = read_runtime_manifest_from_path(&manifest_path) else {
        eprintln!(
            "preseed-health: manifest unreadable at {}",
            manifest_path.display()
        );
        return 71;
    };
    write_runtime_health_cache(runtime_dir, &manifest);
    write_runtime_fast_path_marker(runtime_dir, &manifest);
    let cache_ok = runtime_health_cache(runtime_dir)
        .map(|c| runtime_health_cache_matches(runtime_dir, &c))
        .unwrap_or(false);
    if cache_ok && runtime_fast_path_allowed(runtime_dir) {
        println!(
            "preseed-health: trusted fast-path preseeded for {}",
            runtime_dir.display()
        );
        0
    } else {
        eprintln!("preseed-health: probes missing, left untrusted (harmless)");
        72
    }
}

// ============ 启动健康看门狗(WS-1d,A/B 槽自愈) ============
// 语义:每次 bootstrap 起点 pending+1;emit_ready 即确认(归零+清 previous 槽)。
// 连续 WATCHDOG_ROLLBACK_THRESHOLD 次未达 ready(崩溃/卡死被强退)→ 第三次启动时
// 自动把 previous 槽换回 current(previous 由更新路径保留到首次成功 ready)。
// 与 fast-path 回退互补:fast-path 兜「新 runtime 校验不过」,看门狗兜「新 runtime 起不来」。

pub(crate) const WATCHDOG_ROLLBACK_THRESHOLD: u32 = 2;

#[derive(Serialize, Deserialize, Default, Clone, Copy)]
pub(crate) struct LaunchHealth {
    #[serde(default)]
    pub(crate) pending_starts: u32,
}

pub(crate) fn launch_health_path(app: &AppHandle) -> Option<PathBuf> {
    app.path()
        .app_data_dir()
        .ok()
        .map(|dir| dir.join("launch-health.json"))
}

pub(crate) fn launch_health_read(path: &Path) -> LaunchHealth {
    fs::read_to_string(path)
        .ok()
        .and_then(|text| serde_json::from_str(&text).ok())
        .unwrap_or_default()
}

pub(crate) fn launch_health_write(path: &Path, health: &LaunchHealth) {
    if let Some(parent) = path.parent() {
        let _ = fs::create_dir_all(parent);
    }
    if let Ok(text) = serde_json::to_string(health) {
        let _ = fs::write(path, text);
    }
}

/// 启动起点登记:pending+1 落盘,返回累计未确认次数(含本次)。
pub(crate) fn launch_health_note_start(path: &Path) -> u32 {
    let mut health = launch_health_read(path);
    health.pending_starts = health.pending_starts.saturating_add(1);
    launch_health_write(path, &health);
    health.pending_starts
}

/// 启动成功确认:pending 归零。
pub(crate) fn launch_health_confirm(path: &Path) {
    launch_health_write(path, &LaunchHealth { pending_starts: 0 });
}
