//! 影子副本、自动备份与自动导出。

use super::*;

// ── 影子副本:本地记录库(WebView localStorage 主存)的壳侧文件镜像 ──────────
// WebView 数据目录由系统按 bundle identifier 派生(macOS ~/Library/WebKit/<id>),app 不可
// 控、用户不可见、可被清理工具/磁盘压力驱逐整体清掉,且 localStorage 写后立即退出存在
// 未落盘窗口(上游 tauri #4455)。镜像住 app_data_dir/shadow/(dirs 跨平台语义,Windows 端
// %APPDATA% 同 API 同代码),每写 = 临时文件 + fsync + 原子 rename,invoke 返回即已在盘。
// 白名单键防「任意键名 → 任意文件写」;白名单键字符集本身即安全文件名。
// 恢复语义在前端(shadowMirror.reconcile):仅主存缺失时写回,绝不覆盖存在的主存。
// 两边不一致时页面先请壳层把影子那份另存为 shadow/<key>.diverged-<时刻>.json,再决定并回还是以本机为准。
pub(crate) const SHADOW_ALLOWED_KEYS: [&str; 4] = [
    "horosa.localCharts.v1",
    "horosa.localCases.v1",
    "horosa.localCharts.trash.v1",
    "horosa.localCases.trash.v1",
];

pub(crate) static SHADOW_INFLIGHT_WRITES: AtomicUsize = AtomicUsize::new(0);
/// 影子目录里的一切文件操作(写一把键 / 另存不一致副本)串在这一把锁上:同一临时文件不会被两处同时写。
pub(crate) static SHADOW_FS_LOCK: Mutex<()> = Mutex::new(());
/// 同一把键的「不一致副本」最多留这么多份(内容相同的不重复留;超出时删最早的那份)。
pub(crate) const SHADOW_DIVERGED_KEEP: usize = 10;

/// 影子副本键白名单判定(纯函数;命令入口与测试共用)
pub(crate) fn shadow_key_allowed(key: &str) -> bool {
    SHADOW_ALLOWED_KEYS.contains(&key)
}

fn shadow_store_dir<R: Runtime>(app: &AppHandle<R>) -> std::result::Result<PathBuf, String> {
    let base = app
        .path()
        .app_data_dir()
        .map_err(|err| format!("app_data_dir 不可用: {err}"))?;
    Ok(base.join("shadow"))
}

/// 退出路径等待在途影子写清空(上限 500ms):Exit 回调跑在 applicationWillTerminate 内,
/// 不允许无界等待;写本体毫秒级,此上限只为极端 IO 卡顿兜底。
/// 影子写不在主线程上做(见 enqueue_shadow_write):计数在主线程派发那一刻就加上、写线程落盘后才减,
/// 所以这里看得见「已派发、还在排队或正在写」的每一次影子写。
pub(crate) fn wait_shadow_writes_settle() {
    let deadline = std::time::Instant::now() + std::time::Duration::from_millis(500);
    while SHADOW_INFLIGHT_WRITES.load(Ordering::SeqCst) > 0 && std::time::Instant::now() < deadline
    {
        std::thread::sleep(std::time::Duration::from_millis(10));
    }
}

/// 写一把键的影子文件:临时文件 + fsync + 原子 rename(返回即已在盘)。
pub(crate) fn write_shadow_file(
    dir: &Path,
    key: &str,
    text: &str,
) -> std::result::Result<(), String> {
    if !shadow_key_allowed(key) {
        return Err("shadow.key.not-allowed".to_string());
    }
    let _guard = SHADOW_FS_LOCK.lock().unwrap_or_else(|p| p.into_inner());
    fs::create_dir_all(dir).map_err(|err| format!("影子副本目录创建失败: {err}"))?;
    let tmp = dir.join(format!("{key}.json.tmp"));
    let dst = dir.join(format!("{key}.json"));
    {
        let mut f =
            fs::File::create(&tmp).map_err(|err| format!("影子副本临时文件创建失败: {err}"))?;
        f.write_all(text.as_bytes())
            .map_err(|err| format!("影子副本写入失败: {err}"))?;
        f.sync_all()
            .map_err(|err| format!("影子副本落盘失败: {err}"))?;
    }
    fs::rename(&tmp, &dst).map_err(|err| format!("影子副本替换失败: {err}"))?;
    Ok(())
}

type ShadowWriteDone = Box<dyn FnOnce(std::result::Result<(), String>) + Send + 'static>;

pub(crate) struct ShadowWriteJob {
    pub(crate) dir: PathBuf,
    pub(crate) key: String,
    pub(crate) text: String,
    pub(crate) done: ShadowWriteDone,
}

/// 影子写专用线程:按派发先后一条条落盘(同一把键连写不会乱序,后写的不会被先写的盖回去)。
static SHADOW_WRITER: std::sync::OnceLock<Mutex<std::sync::mpsc::Sender<ShadowWriteJob>>> =
    std::sync::OnceLock::new();

fn run_shadow_write_job(job: ShadowWriteJob) {
    let result = write_shadow_file(&job.dir, &job.key, &job.text);
    SHADOW_INFLIGHT_WRITES.fetch_sub(1, Ordering::SeqCst);
    (job.done)(result);
}

fn shadow_writer() -> Option<std::sync::mpsc::Sender<ShadowWriteJob>> {
    let slot = SHADOW_WRITER.get_or_init(|| {
        let (tx, rx) = std::sync::mpsc::channel::<ShadowWriteJob>();
        let spawned = std::thread::Builder::new()
            .name("horosa-shadow-writer".to_string())
            .spawn(move || {
                while let Ok(job) = rx.recv() {
                    run_shadow_write_job(job);
                }
            });
        if spawned.is_err() {
            // 起不了写线程:发送端照留,send 必失败 → 调用方就地写(与原先同步写同一结果)
            let (dead_tx, _dead_rx) = std::sync::mpsc::channel::<ShadowWriteJob>();
            return Mutex::new(dead_tx);
        }
        Mutex::new(tx)
    });
    slot.lock().ok().map(|tx| tx.clone())
}

/// 把一次影子写交给写线程。在途计数在这里(调用方所在线程,派发时刻)先加上,写完再减;
/// 写线程不可用时就地写完再回调(结果与原先的同步写相同)。
pub(crate) fn enqueue_shadow_write(dir: PathBuf, key: String, text: String, done: ShadowWriteDone) {
    SHADOW_INFLIGHT_WRITES.fetch_add(1, Ordering::SeqCst);
    let job = ShadowWriteJob {
        dir,
        key,
        text,
        done,
    };
    match shadow_writer() {
        Some(tx) => {
            if let Err(std::sync::mpsc::SendError(job)) = tx.send(job) {
                run_shadow_write_job(job);
            }
        }
        None => run_shadow_write_job(job),
    }
}

/// 从影子写请求的载荷里取出 key / text(两者都得是字符串,键在白名单里);取不出返回 None。
pub(crate) fn shadow_write_args(payload: &serde_json::Value) -> Option<(String, String)> {
    let key = payload.get("key")?.as_str()?;
    let text = payload.get("text")?.as_str()?;
    if !shadow_key_allowed(key) {
        return None;
    }
    Some((key.to_string(), text.to_string()))
}

/// 影子写请求在主线程派发那一刻就交给写线程,主线程不再等 fsync;invoke 仍在落盘之后才回复(语义不变)。
/// 这一条请求取不出参数 / 取不到目录时原样交还,由常规命令处理(同步写,返回与原先相同的结果或错误)。
fn route_shadow_write_off_main<R: Runtime>(
    invoke: tauri::ipc::Invoke<R>,
) -> std::result::Result<(), tauri::ipc::Invoke<R>> {
    if invoke.message.command() != "shadow_store_write_command" {
        return Err(invoke);
    }
    let args = match invoke.message.payload() {
        tauri::ipc::InvokeBody::Json(value) => shadow_write_args(value),
        _ => None,
    };
    let Some((key, text)) = args else {
        return Err(invoke);
    };
    let Ok(dir) = shadow_store_dir(invoke.message.webview_ref().app_handle()) else {
        return Err(invoke);
    };
    let resolver = invoke.resolver;
    enqueue_shadow_write(
        dir,
        key,
        text,
        Box::new(move |result| match result {
            Ok(()) => resolver.resolve(()),
            Err(err) => resolver.reject(err),
        }),
    );
    Ok(())
}

/// 命令总表外再套一层:影子写在派发时刻转交写线程,其余命令原样交给总表。
pub(crate) fn shadow_write_off_main_handler<R, F>(
    commands: F,
) -> impl Fn(tauri::ipc::Invoke<R>) -> bool + Send + Sync + 'static
where
    R: Runtime,
    F: Fn(tauri::ipc::Invoke<R>) -> bool + Send + Sync + 'static,
{
    move |invoke| match route_shadow_write_off_main(invoke) {
        Ok(()) => true,
        Err(invoke) => commands(invoke),
    }
}

#[tauri::command]
pub(crate) fn shadow_store_write_command(
    app: AppHandle,
    key: String,
    text: String,
) -> std::result::Result<(), String> {
    if !shadow_key_allowed(key.as_str()) {
        return Err("shadow.key.not-allowed".to_string());
    }
    let dir = shadow_store_dir(&app)?;
    // 同样经写线程排队(与已派发的影子写保持先后),等它落盘再返回
    let (tx, rx) = std::sync::mpsc::channel();
    enqueue_shadow_write(
        dir,
        key,
        text,
        Box::new(move |result| {
            let _ = tx.send(result);
        }),
    );
    rx.recv()
        .unwrap_or_else(|_| Err("影子副本写线程已退出".to_string()))
}

/// 另存这把键当前的影子文件为 `<key>.diverged-<毫秒时刻>.json`(启动对账发现主存与影子不一致时调用),
/// 之后无论哪一次写覆盖影子,对账那一刻的影子内容都还在。
/// 影子文件不存在 / 为空 → Ok(None);已有内容完全相同的副本 → 不再另存,返回那份的文件名。
pub(crate) fn keep_diverged_shadow_copy(
    dir: &Path,
    key: &str,
    now_ms: u128,
) -> std::result::Result<Option<String>, String> {
    if !shadow_key_allowed(key) {
        return Err("shadow.key.not-allowed".to_string());
    }
    let _guard = SHADOW_FS_LOCK.lock().unwrap_or_else(|p| p.into_inner());
    let bytes = match fs::read(dir.join(format!("{key}.json"))) {
        Ok(b) if !b.is_empty() => b,
        _ => return Ok(None),
    };
    let prefix = format!("{key}.diverged-");
    let mut copies: Vec<(u128, String)> = Vec::new();
    if let Ok(entries) = fs::read_dir(dir) {
        for entry in entries.flatten() {
            let name = entry.file_name().to_string_lossy().to_string();
            let Some(stamp) = name
                .strip_prefix(prefix.as_str())
                .and_then(|rest| rest.strip_suffix(".json"))
                .and_then(|s| s.parse::<u128>().ok())
            else {
                continue;
            };
            copies.push((stamp, name));
        }
    }
    for (_, name) in &copies {
        if fs::read(dir.join(name))
            .map(|b| b == bytes)
            .unwrap_or(false)
        {
            return Ok(Some(name.clone()));
        }
    }
    let mut stamp = now_ms;
    while copies.iter().any(|(s, _)| *s == stamp) {
        stamp += 1;
    }
    let name = format!("{prefix}{stamp}.json");
    let tmp = dir.join(format!("{name}.tmp"));
    {
        let mut f = fs::File::create(&tmp)
            .map_err(|err| format!("影子不一致副本临时文件创建失败: {err}"))?;
        f.write_all(&bytes)
            .map_err(|err| format!("影子不一致副本写入失败: {err}"))?;
        f.sync_all()
            .map_err(|err| format!("影子不一致副本落盘失败: {err}"))?;
    }
    fs::rename(&tmp, dir.join(&name)).map_err(|err| format!("影子不一致副本替换失败: {err}"))?;
    copies.push((stamp, name.clone()));
    copies.sort();
    while copies.len() > SHADOW_DIVERGED_KEEP {
        let (_, old) = copies.remove(0);
        let _ = fs::remove_file(dir.join(old));
    }
    Ok(Some(name))
}

/// 启动对账发现某把键主存与影子不一致:先把影子那份另存一份,再由页面决定并回还是以本机为准。
/// 同步命令(主线程):在它之后派发的影子写一定排在这次另存之后。
#[tauri::command]
pub(crate) fn shadow_store_keep_diverged_command(
    app: AppHandle,
    key: String,
) -> std::result::Result<Option<String>, String> {
    let dir = shadow_store_dir(&app)?;
    let now_ms = SystemTime::now()
        .duration_since(UNIX_EPOCH)
        .map(|d| d.as_millis())
        .unwrap_or(0);
    keep_diverged_shadow_copy(&dir, key.as_str(), now_ms)
}

/// 用户选「以本机为准」之后:删掉这把键另存的全部不一致副本(里面是用户决定不要的那几条,可能有已经彻底删除的记录)。
/// 只删 `<key>.diverged-<数字>.json`;影子本体 `<key>.json` 与别的键一概不动。返回删掉的份数。
pub(crate) fn drop_diverged_shadow_copies(
    dir: &Path,
    key: &str,
) -> std::result::Result<u32, String> {
    if !shadow_key_allowed(key) {
        return Err("shadow.key.not-allowed".to_string());
    }
    let _guard = SHADOW_FS_LOCK.lock().unwrap_or_else(|p| p.into_inner());
    let prefix = format!("{key}.diverged-");
    let mut dropped = 0u32;
    if let Ok(entries) = fs::read_dir(dir) {
        for entry in entries.flatten() {
            let name = entry.file_name().to_string_lossy().to_string();
            let is_copy = name
                .strip_prefix(prefix.as_str())
                .and_then(|rest| rest.strip_suffix(".json"))
                .map(|stamp| !stamp.is_empty() && stamp.bytes().all(|b| b.is_ascii_digit()))
                .unwrap_or(false);
            if is_copy && fs::remove_file(dir.join(&name)).is_ok() {
                dropped += 1;
            }
        }
    }
    Ok(dropped)
}

#[tauri::command]
pub(crate) fn shadow_store_drop_diverged_command(
    app: AppHandle,
    key: String,
) -> std::result::Result<u32, String> {
    let dir = shadow_store_dir(&app)?;
    drop_diverged_shadow_copies(&dir, key.as_str())
}

// ── 自动备份壳侧四件:用户可见目录写/列/读/修剪(白名单目录+文件名模式双防呆) ──
// 目录=系统「文稿」/Horosa Backups/<本应用名>(用户可见、进 Time Machine 面、可自行软链到网盘目录;
// Win 端 dirs 同 API 落 %USERPROFILE%\Documents)。写=fsync+原子 rename;删=仅限本应用子目录内
// 匹配 horosa-backup-*.zip 的文件(任意路径/任意名一律拒)。
// 同一台机器上装着两个不同名的星阙构建时,各写各的子目录:以前共用 Horosa Backups 根目录,两边按时间修剪会互删对方的备份,
// 「从最近的自动备份恢复」也可能拿到另一个应用的数据。根目录里早先写下的备份(旧版本留下的)照旧能列出、能恢复,但任何一边都不修剪它们。
fn auto_backup_root(app: &AppHandle) -> std::result::Result<PathBuf, String> {
    let base = app
        .path()
        .document_dir()
        .map_err(|err| format!("document_dir 不可用: {err}"))?;
    Ok(base.join("Horosa Backups"))
}

fn auto_backup_dir(app: &AppHandle) -> std::result::Result<PathBuf, String> {
    Ok(auto_backup_root(app)?.join(APP_NAME))
}

pub(crate) fn backup_names_in(dir: &Path) -> Vec<String> {
    let mut out = Vec::new();
    if let Ok(entries) = fs::read_dir(dir) {
        for entry in entries.flatten() {
            let name = entry.file_name().to_string_lossy().to_string();
            if is_backup_file_name(&name) && entry.path().is_file() {
                out.push(name);
            }
        }
    }
    out.sort();
    out
}

/// 列备份:本应用子目录里的全部 + 根目录里早于子目录最早一份的旧备份(= 分子目录之前写下的那些)。
/// 文件名是本机时刻 YYYYMMDD-HHmmss,字典序即时间序。比子目录最早一份还新的根目录文件只可能是另一个(尚未升级的)应用写的,不列。
pub(crate) fn merged_backup_listing(own: &[String], legacy: &[String]) -> Vec<String> {
    let oldest_own = own.first();
    let mut out: Vec<String> = own.to_vec();
    for name in legacy {
        let older = oldest_own.map(|o| name < o).unwrap_or(true);
        if older && !out.contains(name) {
            out.push(name.clone());
        }
    }
    out.sort();
    out
}

/// 读一份备份:先找本应用子目录,没有再找根目录里的旧备份。
pub(crate) fn backup_path_for_read(own_dir: &Path, root_dir: &Path, file_name: &str) -> PathBuf {
    let own = own_dir.join(file_name);
    if own.is_file() {
        own
    } else {
        root_dir.join(file_name)
    }
}

/// 修剪:只删本应用子目录里、名字合规的备份;根目录里的旧备份永远不删(两个构建都不碰)。
pub(crate) fn prune_backups_in(own_dir: &Path, delete_names: &[String]) -> u32 {
    let mut deleted = 0u32;
    for name in delete_names {
        if !is_backup_file_name(name) {
            continue; // 模式外名一律拒(双侧防呆:前端只送 GFS 淘汰名单,壳侧再验)
        }
        if fs::remove_file(own_dir.join(name)).is_ok() {
            deleted += 1;
        }
    }
    deleted
}

pub(crate) fn is_backup_file_name(name: &str) -> bool {
    name.starts_with("horosa-backup-")
        && name.ends_with(".zip")
        && name
            .chars()
            .all(|c| c.is_ascii_alphanumeric() || c == '-' || c == '.')
        && !name.contains("..")
}

#[tauri::command]
pub(crate) fn auto_backup_write_command(
    app: AppHandle,
    file_name: String,
    base64_data: String,
) -> std::result::Result<String, String> {
    if !is_backup_file_name(&file_name) {
        return Err("backup.name.invalid".to_string());
    }
    let bytes = BASE64_STANDARD
        .decode(base64_data.as_bytes())
        .map_err(|err| format!("base64 解码失败: {err}"))?;
    let dir = auto_backup_dir(&app)?;
    fs::create_dir_all(&dir).map_err(|err| format!("备份目录创建失败: {err}"))?;
    let tmp = dir.join(format!("{file_name}.tmp"));
    let dst = dir.join(&file_name);
    {
        let mut f = fs::File::create(&tmp).map_err(|err| format!("备份临时文件创建失败: {err}"))?;
        f.write_all(&bytes)
            .map_err(|err| format!("备份写入失败: {err}"))?;
        f.sync_all()
            .map_err(|err| format!("备份 fsync 失败: {err}"))?;
    }
    fs::rename(&tmp, &dst).map_err(|err| format!("备份原子替换失败: {err}"))?;
    Ok(dst.to_string_lossy().to_string())
}

#[tauri::command]
pub(crate) fn auto_backup_list_command(app: AppHandle) -> std::result::Result<Vec<String>, String> {
    let own = backup_names_in(&auto_backup_dir(&app)?);
    let legacy = backup_names_in(&auto_backup_root(&app)?);
    Ok(merged_backup_listing(&own, &legacy))
}

#[tauri::command]
pub(crate) fn auto_backup_read_command(
    app: AppHandle,
    file_name: String,
) -> std::result::Result<String, String> {
    if !is_backup_file_name(&file_name) {
        return Err("backup.name.invalid".to_string());
    }
    let path = backup_path_for_read(
        &auto_backup_dir(&app)?,
        &auto_backup_root(&app)?,
        &file_name,
    );
    let bytes = fs::read(&path).map_err(|err| format!("备份读取失败: {err}"))?;
    Ok(BASE64_STANDARD.encode(bytes))
}

#[tauri::command]
pub(crate) fn auto_backup_prune_command(
    app: AppHandle,
    delete_names: Vec<String>,
) -> std::result::Result<u32, String> {
    Ok(prune_backups_in(&auto_backup_dir(&app)?, &delete_names))
}

#[tauri::command]
pub(crate) fn shadow_store_read_all_command(
    app: AppHandle,
) -> std::result::Result<std::collections::HashMap<String, String>, String> {
    let dir = shadow_store_dir(&app)?;
    let mut out = std::collections::HashMap::new();
    for key in SHADOW_ALLOWED_KEYS {
        let path = dir.join(format!("{key}.json"));
        if let Ok(text) = fs::read_to_string(&path) {
            if !text.is_empty() {
                out.insert(key.to_string(), text);
            }
        }
    }
    Ok(out)
}
