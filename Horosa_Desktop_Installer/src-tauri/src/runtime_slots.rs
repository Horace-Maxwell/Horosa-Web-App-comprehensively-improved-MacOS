//! 运行时手术锁、槽位对换、撕裂修复、暂存与解压入口。

use super::*;

pub(crate) fn remove_dir_if_exists(path: &Path) -> Result<()> {
    if path.exists() {
        fs::remove_dir_all(path)?;
    }
    Ok(())
}

/// 目标路径所在卷的可用字节数(df -k,1024 块)。取不到时返回 None(调用方按"不拦"处理)。
pub(crate) fn available_disk_bytes(path: &Path) -> Option<u64> {
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

pub(crate) fn archive_runtime_version(archive_path: &Path) -> Result<String> {
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

/// 把 previous 槽换回 current。previous 不在/不完整 → Ok(false) 不动 current。
// 跨进程手术互斥锁:多实例/多用户可并发对同一 runtime 根做 clone→_comp_stage→swap,
// renamex 单 op 原子但多步手术未跨进程串行化 → flock 锁文件(内核级,进程崩溃/被杀自动释放)。
// 纪律([108] 反向锚强制):锁只允许出现在五个叶子手术函数内部——
//   extract_runtime_archive_with / apply_component_updates_with(required)
//   rollback_runtime_to_previous / repair_torn_runtime_slots / cleanup_previous_slots(optional)
// 五叶已核互不嵌套;flock 同进程两个 fd 也互斥,上层再取=自死锁,严禁。
// helper 经 --horosa-runtime-swap → extract 协议自动拿锁(零新增代数差)。
pub(crate) struct RuntimeSurgeryLock {
    _file: Option<File>,
}

pub(crate) fn runtime_surgery_lock_path(root: &Path) -> PathBuf {
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
pub(crate) fn try_acquire_surgery_lock(
    root: &Path,
    wait: Duration,
) -> Result<Option<RuntimeSurgeryLock>> {
    if surgery_lock_disabled() {
        return Ok(Some(RuntimeSurgeryLock { _file: None }));
    }
    use std::os::unix::fs::OpenOptionsExt;
    use std::os::unix::io::AsRawFd;
    ensure_dir(root)?;
    let lock_path = runtime_surgery_lock_path(root);
    let file = match std::fs::OpenOptions::new()
        .read(true)
        .write(true)
        .create(true)
        .mode(0o644)
        .open(&lock_path)
    {
        Ok(f) => f,
        Err(err) if err.kind() == std::io::ErrorKind::PermissionDenied => {
            // 共享根只属主可写(多账户机上的其他账户只读):锁文件开不出写句柄就开只读句柄,flock 对只读 fd 也能上 LOCK_EX。
            std::fs::OpenOptions::new()
                .read(true)
                .open(&lock_path)
                .with_context(|| format!("打开手术锁 {}", lock_path.display()))?
        }
        Err(err) => {
            return Err(
                anyhow::Error::from(err).context(format!("创建手术锁 {}", lock_path.display()))
            )
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
pub(crate) fn acquire_surgery_lock_required(root: &Path) -> Result<RuntimeSurgeryLock> {
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

pub(crate) fn rollback_runtime_to_previous(root: &Path) -> Result<bool> {
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
pub(crate) fn cleanup_previous_slots(app: &AppHandle) {
    let mut roots = vec![shared_runtime_root()];
    if let Ok(user_root) = user_runtime_root(app) {
        roots.push(user_root);
    }
    for root in roots {
        let previous = root.join("previous");
        // 别的账户装的共享运行环境(本账户只读):不归本账户收拾,也不去占它的手术锁
        if previous.exists() && path_writable_by_current_user(&root) {
            // optional 锁:对方在手术期间 previous 可能是其回滚资本,绝不抢删。
            let Some(_surgery) = acquire_surgery_lock_optional(&root) else {
                continue;
            };
            let _ = remove_dir_if_exists(&previous);
        }
    }
}

/// 共享运行环境的权限:读 / 执行对所有本机账户放开,写只留属主(安装者)。
/// 归档里个别文件自带组写位(0775;组 = staff = 所有本机账户),解压后照原样落盘,这里一并收掉。
pub(crate) const SHARED_TREE_CHMOD: &str = "u+rwX,go+rX,go-w";

/// 按 SHARED_TREE_CHMOD 收一遍整棵树(best-effort,失败不阻塞)。
pub(crate) fn seal_tree_permissions(path: &Path) {
    let _ = Command::new("/bin/chmod")
        .arg("-R")
        .arg(SHARED_TREE_CHMOD)
        .arg(path)
        .stdout(Stdio::null())
        .stderr(Stdio::null())
        .status();
}

/// 共享运行环境只给安装者写:每次新树落成(全量解压 / 增量对换)后收一遍权限。
/// 以前这里把整棵树放开给所有账户写 —— 同机任一账户都能改启动脚本 / 引擎 / 页面,
/// 下次别的账户打开星阙就以他的身份执行。多账户机上的其他账户只读加载这份运行环境:
/// pid 文件落各自的缓存目录(start / stop 脚本按目录可写性选),要换版本时换进自己的用户目录
/// (selected_runtime_roots)。仅共享域生效;单账户机上新树本来就归本人,收权限是空操作。
pub(crate) fn seal_shared_tree_permissions(path: &Path) {
    if !is_shared_runtime_dir(path) {
        return;
    }
    seal_tree_permissions(path);
}

/// 共享运行环境里会被执行 / 加载的几处(根、当前版本、网页与后端目录、起停脚本):看它们有没有「所有账户可写」
const SHARED_TREE_PROBES: &[&str] = &[
    "",
    "current",
    "current/Horosa-Web",
    "current/Horosa-Web/start_horosa_local.sh",
    "current/Horosa-Web/stop_horosa_local.sh",
];

/// 共享根(运行环境根的上一级,安装器按它整体封权)里 App 会读来用的几处:根本身(开着 = 别的账户能把整个
/// runtime 目录换掉)、downloads(自愈会把里面的归档解压进本账户的运行目录)、install-source.json(安装来源与归档 sha)
const SHARED_ROOT_PROBES: &[&str] = &["", "downloads", "install-source.json"];

/// 其他账户可写;或组可写且组是 staff(gid 20 = 所有本机账户)
fn writable_by_other_accounts(meta: &fs::Metadata) -> bool {
    use std::os::unix::fs::{MetadataExt, PermissionsExt};
    let mode = meta.permissions().mode();
    mode & 0o002 != 0 || (mode & 0o020 != 0 && meta.gid() == 20)
}

/// 别的账户名下、所有本机账户可写的一处(本账户收不动):要用完整安装包更新一次。
/// 存结构化发现,话在显示那一刻取:原生对话框按当前界面简繁(`message_in(shell_script_is_hant())`),
/// 设置页 / 诊断页的一行提示给简体原文(页面显示层自己转)
#[derive(Debug, Clone, PartialEq)]
pub(crate) struct ForeignSharedTree {
    pub(crate) path: PathBuf,
    pub(crate) uid: u32,
    pub(crate) mode: u32,
}

impl ForeignSharedTree {
    pub(crate) fn message_in(&self, hant: bool) -> String {
        fill_placeholders(
            &shell_text_in("update.shared_tree.foreign", hant),
            &[
                ("path", &self.path.display().to_string()),
                ("uid", &self.uid.to_string()),
                ("mode", &format!("{:o}", self.mode)),
            ],
        )
    }
}

/// 共享树权限的只读检查结果(检查本身不改任何东西)
#[derive(Debug, Default, Clone, PartialEq)]
pub(crate) struct SharedTreeFinding {
    /// 别的账户所有、所有本机账户可写(本账户收不动):要用完整安装包更新一次
    pub(crate) foreign: Option<ForeignSharedTree>,
    /// 本账户所有、但所有本机账户可写:用户在设置页确认后由后台收紧
    pub(crate) mine_open: Vec<PathBuf>,
}

impl SharedTreeFinding {
    /// 给设置页 / 诊断页的一行提示 + 能不能在 App 里一键收紧
    pub(crate) fn warning(&self) -> (Option<String>, bool) {
        if let Some(found) = &self.foreign {
            return (Some(found.message_in(false)), false);
        }
        match self.mine_open.first() {
            Some(p) => (
                Some(format!(
                    "共享运行环境 {} 等 {} 处归你所有、但所有本机账户都能改:在偏好设置「本机组件」里点「收紧共享权限」修复(只改权限,不动内容)",
                    p.display(),
                    self.mine_open.len()
                )),
                true,
            ),
            None => (None, false),
        }
    }
}

/// 早先安装包留下的「所有本机账户可写」共享树:探共享根(根 / downloads / install-source.json)与运行环境根下的
/// 会被执行的几处。别的账户(多为 root)名下的 → foreign(本账户收不动,其他账户能借它改星阙要执行的脚本 / 引擎,
/// 或在 downloads 放伪造归档等本账户自愈时解压执行);本账户名下的 → mine_open(不在这里改:读路径不许有副作用)。
pub(crate) fn inspect_shared_tree_at(
    shared_root: &Path,
    runtime_root: &Path,
    my_uid: u32,
) -> SharedTreeFinding {
    use std::os::unix::fs::{MetadataExt, PermissionsExt};
    let mut out = SharedTreeFinding::default();
    let probes = SHARED_ROOT_PROBES
        .iter()
        .map(|rel| (shared_root, *rel))
        .chain(SHARED_TREE_PROBES.iter().map(|rel| (runtime_root, *rel)));
    for (base, rel) in probes {
        let p = if rel.is_empty() {
            base.to_path_buf()
        } else {
            base.join(rel)
        };
        let Ok(meta) = fs::symlink_metadata(&p) else {
            continue;
        };
        if !writable_by_other_accounts(&meta) {
            continue;
        }
        if meta.uid() == my_uid {
            if !out.mine_open.contains(&p) {
                out.mine_open.push(p);
            }
            continue;
        }
        if out.foreign.is_none() {
            out.foreign = Some(ForeignSharedTree {
                path: p.clone(),
                uid: meta.uid(),
                mode: meta.permissions().mode() & 0o7777,
            });
        }
    }
    out
}

/// 只回「别的账户名下、本账户收不动」的那一类(更新策略据此改走完整安装包);只读,无副作用
pub(crate) fn legacy_open_shared_tree_at(
    shared_root: &Path,
    runtime_root: &Path,
    my_uid: u32,
) -> Option<ForeignSharedTree> {
    inspect_shared_tree_at(shared_root, runtime_root, my_uid).foreign
}

fn my_uid() -> u32 {
    unsafe { libc::geteuid() }
}

pub(crate) fn inspect_shared_tree() -> SharedTreeFinding {
    inspect_shared_tree_at(&shared_assets_root(), &shared_runtime_root(), my_uid())
}

pub(crate) fn legacy_open_shared_tree() -> Option<ForeignSharedTree> {
    inspect_shared_tree().foreign
}

/// 用户在设置页确认后才调(后台线程):把本账户名下、所有账户可写的几处收紧(目录整棵、文件单个),再重查一遍回结果
pub(crate) fn seal_my_open_shared_tree_at(
    shared_root: &Path,
    runtime_root: &Path,
    my_uid: u32,
) -> SharedTreeFinding {
    let found = inspect_shared_tree_at(shared_root, runtime_root, my_uid);
    let mut done: Vec<PathBuf> = Vec::new();
    let mut targets = found.mine_open.clone();
    targets.sort();
    for p in targets {
        if done.iter().any(|d| p.starts_with(d)) {
            continue;
        }
        seal_tree_permissions(&p);
        done.push(p);
    }
    inspect_shared_tree_at(shared_root, runtime_root, my_uid)
}

pub(crate) fn seal_my_open_shared_tree() -> SharedTreeFinding {
    seal_my_open_shared_tree_at(&shared_assets_root(), &shared_runtime_root(), my_uid())
}

/// 自愈要用的缓存归档可信吗:不是符号链接;归档与它往上直到共享根(或用户下载目录)的每一层都不能被别的账户写,
/// 属主只能是 root、本账户或共享运行环境的属主(安装者);安装来源记录里有这份归档的 sha256 时必须相符
/// (记录文件本身同样要过上面的权限判据)。不可信 ⇒ Err(原因),调用方跳过该候选。
pub(crate) fn cached_archive_trust_at(
    archive: &Path,
    shared_root: &Path,
    runtime_root: &Path,
    marker: Option<&InstallSourceMarker>,
    my_uid: u32,
) -> std::result::Result<(), String> {
    use std::os::unix::fs::MetadataExt;
    let meta =
        fs::symlink_metadata(archive).map_err(|e| format!("读不到 {}:{e}", archive.display()))?;
    if meta.file_type().is_symlink() || !meta.is_file() {
        return Err(format!("{} 不是普通文件", archive.display()));
    }
    let tree_owner = fs::metadata(runtime_root).map(|m| m.uid()).ok();
    let owner_ok = |uid: u32| uid == 0 || uid == my_uid || Some(uid) == tree_owner;
    let in_shared = archive.starts_with(shared_root);
    let stop = if in_shared {
        shared_root.to_path_buf()
    } else {
        archive.parent().map(Path::to_path_buf).unwrap_or_default()
    };
    let mut cur = Some(archive.to_path_buf());
    while let Some(p) = cur {
        let m = fs::symlink_metadata(&p).map_err(|e| format!("读不到 {}:{e}", p.display()))?;
        if writable_by_other_accounts(&m) {
            return Err(format!(
                "{} 所有本机账户都能写,里面的归档可能被换过",
                p.display()
            ));
        }
        if !owner_ok(m.uid()) {
            return Err(format!("{} 归别的账户(uid {})所有", p.display(), m.uid()));
        }
        if p == stop {
            break;
        }
        cur = p.parent().map(Path::to_path_buf);
    }
    if in_shared {
        if let Some(mk) = marker {
            let name = archive.file_name().and_then(|n| n.to_str()).unwrap_or("");
            let want = mk.runtime_archive_sha256.as_deref().unwrap_or("").trim();
            if !want.is_empty() && mk.runtime_archive_name.as_deref() == Some(name) {
                let got = sha256_file(archive)
                    .map_err(|e| format!("算不出 {} 的 sha256:{e:#}", archive.display()))?;
                if !got.eq_ignore_ascii_case(want) {
                    return Err(format!(
                        "{} 的 sha256 与安装记录不符(记录 {}…,实得 {}…)",
                        archive.display(),
                        &want[..want.len().min(12)],
                        &got[..got.len().min(12)]
                    ));
                }
            }
        }
    }
    Ok(())
}

/// 安装来源记录:只有过了权限判据(不是别的账户可写、属主是 root / 本账户 / 安装者)才拿来核 sha
pub(crate) fn trusted_install_source_marker_at(
    path: &Path,
    runtime_root: &Path,
    my_uid: u32,
) -> Option<InstallSourceMarker> {
    use std::os::unix::fs::MetadataExt;
    let meta = fs::symlink_metadata(path).ok()?;
    let tree_owner = fs::metadata(runtime_root).map(|m| m.uid()).ok();
    if meta.file_type().is_symlink()
        || writable_by_other_accounts(&meta)
        || !(meta.uid() == 0 || meta.uid() == my_uid || Some(meta.uid()) == tree_owner)
    {
        return None;
    }
    let data = fs::read_to_string(path).ok()?;
    serde_json::from_str(&data).ok()
}

pub(crate) fn cached_archive_trust(archive: &Path) -> std::result::Result<(), String> {
    let marker = trusted_install_source_marker_at(
        &install_source_marker_path(),
        &shared_runtime_root(),
        my_uid(),
    );
    cached_archive_trust_at(
        archive,
        &shared_assets_root(),
        &shared_runtime_root(),
        marker.as_ref(),
        my_uid(),
    )
}

fn sha256_file(path: &Path) -> Result<String> {
    use sha2::{Digest, Sha256};
    use std::io::Read;
    let mut f = fs::File::open(path)?;
    let mut h = Sha256::new();
    let mut buf = vec![0u8; 1 << 20];
    loop {
        let n = f.read(&mut buf)?;
        if n == 0 {
            break;
        }
        h.update(&buf[..n]);
    }
    Ok(h.finalize().iter().map(|b| format!("{b:02x}")).collect())
}

/// 当前账户能不能往这里写(路径不存在时看最近一层已存在的上级;`/Users/Shared` 本身对所有人可建子目录)。
pub(crate) fn path_writable_by_current_user(path: &Path) -> bool {
    use std::os::unix::ffi::OsStrExt;
    let mut probe = path;
    loop {
        if probe.exists() {
            let Ok(c_path) = std::ffi::CString::new(probe.as_os_str().as_bytes()) else {
                return false;
            };
            return unsafe { libc::access(c_path.as_ptr(), libc::W_OK) } == 0;
        }
        match probe.parent() {
            Some(parent) => probe = parent,
            None => return false,
        }
    }
}

// APFS 原子互换两目录(renamex_np + RENAME_SWAP,macOS 10.12+):
// 对换全程只有这一个原子点——任意时刻断电/强杀,current 恒为「全旧」或「全新」,
// 不再存在两段 rename 之间的 current 缺失窗口。返回 Ok(false)=本卷/内核不支持
// (ENOTSUP/EINVAL/EXDEV)或被 HOROSA_SWAP_DISABLE=1 禁用 → 调用方走两段 rename
// 回退路径(其 kill 窗口由启动期 repair_torn_runtime_slots 撕裂探测兜底)。
pub(crate) fn atomic_swap_dirs(a: &Path, b: &Path) -> Result<bool> {
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

// 启动期兜底:两段 rename 回退路径(或 postinstall shell 两 mv)在
// 「current 已挪走、新树未就位」窗口被断电/强杀 → current 整体缺失。按候选新旧序
// 收养:_comp_stage(增量暂存,最新) > _extract/runtime-payload(全量暂存) > previous
// (旧版)。候选必须过 runtime_dir_has_required_files 完整性验,不完整绝不收养。
pub(crate) fn repair_torn_runtime_slots(root: &Path) -> Result<bool> {
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
pub(crate) fn sweep_stale_runtime_stage_dirs(root: &Path) {
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

pub(crate) fn extract_runtime_archive(archive_path: &Path, dest_root: &Path) -> Result<()> {
    extract_runtime_archive_with(archive_path, dest_root, None, None)
}

pub(crate) fn extract_runtime_archive_with(
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
            // 归档本身不安全(路径 / 链接逃出解压目录):整包拒收、清掉半成品,不换外部 tar 再试
            Err(err) if is_archive_unsafe(&err) => {
                let _ = remove_dir_if_exists(&extract_root);
                return Err(err.context(format!(
                    "refuse unsafe runtime archive {}",
                    archive_path.display()
                )));
            }
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
        let actual =
            read_runtime_manifest_from_path(&extracted_runtime.join("runtime-manifest.json"))
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
        // 首选 renamex_np 单点互换:swap 后 extracted 位置上是旧树,
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
    seal_shared_tree_permissions(&final_runtime);
    // WS-1d 看门狗:previous 槽保留到首次成功 ready(emit_ready→cleanup_previous_slots 回收);
    // 若新 runtime 连续起不来,启动侧自动 rollback_runtime_to_previous。
    remove_dir_if_exists(&extract_root)?;
    Ok(())
}

pub(crate) fn clear_runtime_pending_marker(runtime_dir: &Path) -> Result<()> {
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

fn stage_hardlink_enabled() -> bool {
    std::env::var("HOROSA_STAGE_HARDLINK")
        .map(|v| v.trim() != "0")
        .unwrap_or(true)
}

/// [更新槽复用] 用硬链接搭暂存槽:未变部件的文件与 current 共用 inode —— 系统对原生库的首次加载评估按文件身份记,
/// 硬链接不换身份,更新后只有真换了的部件要重评估(此前整棵 APFS 克隆 = 全部换身份 = 更新后首启十几秒)。
/// 目录重建(权限照抄)、符号链接照抄;树根下的散文件(清单 / 锁 / 各标记)拷贝而不链接 —— 手术期要就地改写
/// 它们,链接会写穿到正在跑的旧树。安全前提:部件替换一律先删条目再建新文件(native 解压 remove_file 后
/// File::create;外部 tar 带 -U),绝不就地覆盖写;树内其余文件只读。
pub(crate) fn stage_dir_by_hardlink(src: &Path, dst: &Path) -> Result<()> {
    fs::create_dir_all(dst)?;
    if let Ok(meta) = fs::metadata(src) {
        let _ = fs::set_permissions(dst, meta.permissions());
    }
    for entry in WalkDir::new(src).follow_links(false).min_depth(1) {
        let entry = entry?;
        let rel = entry.path().strip_prefix(src)?;
        let target = dst.join(rel);
        let file_type = entry.file_type();
        if file_type.is_dir() {
            fs::create_dir_all(&target)?;
            if let Ok(meta) = entry.metadata() {
                let _ = fs::set_permissions(&target, meta.permissions());
            }
        } else if file_type.is_symlink() {
            let link = fs::read_link(entry.path())?;
            std::os::unix::fs::symlink(&link, &target)?;
        } else if file_type.is_file() {
            if rel.components().count() == 1 {
                fs::copy(entry.path(), &target)?;
            } else if let Err(err) = fs::hard_link(entry.path(), &target) {
                // 已签名应用包(Python.app)里的文件系统不许硬链接(EPERM):退单文件克隆(新 inode,
                // 更新后要重评估的只多这几个);其它错误同样退克隆,克隆也失败才整体失败。
                fs::copy(entry.path(), &target).with_context(|| {
                    format!("hardlink {} 失败({err}),克隆也失败", rel.display())
                })?;
            }
        }
    }
    Ok(())
}

/// 搭暂存槽:硬链接优先;HOROSA_STAGE_HARDLINK=0 或链接失败(卷不支持等)→ 清掉半成品回 APFS 克隆旧路。
pub(crate) fn stage_runtime_copy(current: &Path, stage: &Path, say: &dyn Fn(&str)) -> Result<()> {
    if stage_hardlink_enabled() {
        say("复用当前运行时(硬链接,秒级)…");
        match stage_dir_by_hardlink(current, stage) {
            Ok(()) => return Ok(()),
            Err(err) => {
                let _ = remove_dir_if_exists(stage);
                ledger_mark(
                    "rust.stage_hardlink_fallback",
                    Some(serde_json::json!({"error": format!("{err:#}")})),
                );
            }
        }
    }
    say("克隆当前运行时(APFS 秒级)…");
    clone_dir_fast(current, stage)
}

pub(crate) fn clone_dir_fast(src: &Path, dst: &Path) -> Result<()> {
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
