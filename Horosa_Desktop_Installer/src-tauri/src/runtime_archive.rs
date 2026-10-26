//! 运行时归档的原生流式解压与外部 tar 回退。

use super::*;

// ============ 原生流式解压(WS-1c) ============
// flate2+tar 流式:进度=压缩流读取位置/归档大小(零预扫,一遍完成);
// 单线程解码(tar 流不可并行解码)+ 有界并发写盘(小文件投池,in-flight ≤64MB;
// 目录/链接/大文件主线程顺序,硬链前 flush 池保序)。
// 外部 /usr/bin/tar 路径整体保留:native 出错自动回退重解;HOROSA_EXTRACT_NATIVE=0 直退。

pub(crate) const SMALL_FILE_LIMIT: u64 = 8 * 1024 * 1024;
const EXTRACT_INFLIGHT_CAP: u64 = 64 * 1024 * 1024;

pub(crate) fn extract_native_enabled() -> bool {
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
pub(crate) struct CountingReader<R: Read> {
    pub(crate) inner: R,
    pub(crate) count: Arc<std::sync::atomic::AtomicU64>,
}
impl<R: Read> Read for CountingReader<R> {
    fn read(&mut self, buf: &mut [u8]) -> std::io::Result<usize> {
        let n = self.inner.read(buf)?;
        self.count
            .fetch_add(n as u64, std::sync::atomic::Ordering::Relaxed);
        Ok(n)
    }
}

/// 归档本身不安全(条目路径 / 链接目标逃出解压目录,或要经符号链接写盘)。调用方见到它**不回退外部 tar**:
/// 外部 tar 同样拒绝 `..` 与经链接写盘,但照建指向树外的链接 —— 坏包就该整包拒收,而不是换个解压器再试。
#[derive(Debug)]
pub(crate) struct ArchiveUnsafe(pub(crate) String);
impl std::fmt::Display for ArchiveUnsafe {
    fn fmt(&self, f: &mut std::fmt::Formatter<'_>) -> std::fmt::Result {
        f.write_str(&self.0)
    }
}
impl std::error::Error for ArchiveUnsafe {}
fn archive_unsafe(msg: String) -> anyhow::Error {
    anyhow::Error::new(ArchiveUnsafe(msg))
}
/// 错误链里有没有「归档本身不安全」(经 with_context 包过也认)。
pub(crate) fn is_archive_unsafe(err: &anyhow::Error) -> bool {
    err.chain()
        .any(|e| e.downcast_ref::<ArchiveUnsafe>().is_some())
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
                return Err(archive_unsafe(format!(
                    "archive entry path escapes dest: {}",
                    raw.display()
                )));
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

/// 符号链接的目标按「真实解析」留在 dest 之内:从链接所在目录出发逐段走,`..` 退一层(退出 dest = 逃逸);
/// 途经本树里已存在的符号链接就展开它(绝对目标 = 逃逸;展开超过 32 层 = 视为逃逸,含自指环);尚不存在的段按字面走。
/// 只按字面归一化不够:`b -> .` 落在第一层、真实位置却是 dest 本身,`b/../x` 字面在树内、真实已出树。
pub(crate) fn symlink_target_within(dest: &Path, link_rel: &Path, target: &Path) -> bool {
    fn walk(dest: &Path, stack: &mut Vec<std::ffi::OsString>, target: &Path, depth: u32) -> bool {
        if depth > 32 {
            return false;
        }
        for comp in target.components() {
            match comp {
                std::path::Component::CurDir => {}
                std::path::Component::ParentDir => {
                    if stack.pop().is_none() {
                        return false;
                    }
                }
                std::path::Component::Normal(seg) => {
                    stack.push(seg.to_os_string());
                    let here = stack.iter().fold(dest.to_path_buf(), |p, s| p.join(s));
                    if let Ok(meta) = fs::symlink_metadata(&here) {
                        if meta.file_type().is_symlink() {
                            let Ok(link) = fs::read_link(&here) else {
                                return false;
                            };
                            stack.pop();
                            if !walk(dest, stack, &link, depth + 1) {
                                return false;
                            }
                        }
                    }
                }
                _ => return false,
            }
        }
        true
    }
    let mut stack: Vec<std::ffi::OsString> = link_rel
        .parent()
        .map(|p| {
            p.components()
                .filter_map(|c| match c {
                    std::path::Component::Normal(s) => Some(s.to_os_string()),
                    _ => None,
                })
                .collect()
        })
        .unwrap_or_default();
    walk(dest, &mut stack, target, 0)
}

/// 写盘前核对:条目在 dest 之内的各级父目录(include_self 时连它自己)没有一级是符号链接 ——
/// 否则 create_dir_all / File::create / chmod 会跟着链接写到树外(先放 `x -> 树外目录`、再放 `x/evil` 的归档)。
/// verified 记已核过的真目录(相对 dest),免得每个条目都逐级 lstat。
fn ensure_no_symlink_on_path(
    dest: &Path,
    rel: &Path,
    include_self: bool,
    verified: &mut std::collections::HashSet<PathBuf>,
) -> Result<()> {
    let comps: Vec<_> = rel.components().collect();
    let n = if include_self {
        comps.len()
    } else {
        comps.len().saturating_sub(1)
    };
    let mut cur = PathBuf::new();
    for comp in comps.iter().take(n) {
        cur.push(comp);
        if verified.contains(&cur) {
            continue;
        }
        match fs::symlink_metadata(dest.join(&cur)) {
            Ok(meta) if meta.file_type().is_symlink() => {
                return Err(archive_unsafe(format!(
                    "archive entry would be written through a symlink: {}",
                    rel.display()
                )));
            }
            Ok(meta) if meta.is_dir() => {
                verified.insert(cur.clone());
            }
            _ => {}
        }
    }
    Ok(())
}

pub(crate) struct WriteJob {
    pub(crate) path: PathBuf,
    pub(crate) data: Vec<u8>,
    pub(crate) mode: Option<u32>,
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
pub(crate) struct WriterPool {
    pub(crate) tx: Option<std::sync::mpsc::Sender<WriteJob>>,
    pub(crate) workers: Vec<thread::JoinHandle<()>>,
    in_flight: Arc<(Mutex<u64>, std::sync::Condvar)>,
    pub(crate) error: Arc<Mutex<Option<String>>>,
}

impl WriterPool {
    pub(crate) fn new(concurrency: usize) -> Self {
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
    pub(crate) fn flush(&self) -> Result<()> {
        let (lock, cvar) = &*self.in_flight;
        {
            let mut cur = lock.lock().map_err(|_| anyhow!("写盘池额度锁中毒"))?;
            while *cur > 0 {
                cur = cvar.wait(cur).map_err(|_| anyhow!("写盘池额度锁中毒"))?;
            }
        }
        self.check_error()
    }

    pub(crate) fn finish(mut self) -> Result<()> {
        self.tx.take();
        for worker in self.workers.drain(..) {
            let _ = worker.join();
        }
        self.check_error()
    }
}

/// 原生流式解压(gz→tar 一遍过):progress(压缩流已读, 归档总字节, 已落文件数)。
pub(crate) fn extract_tar_gz_native_with(
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
    let mut verified_dirs: std::collections::HashSet<PathBuf> = std::collections::HashSet::new();
    let mut created_links: Vec<(PathBuf, PathBuf)> = Vec::new();
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
            // 目录条目连自身也核(已有同名链接时 create_dir_all / chmod 会跟着它走);其余条目核父链(自身先删再建)
            ensure_no_symlink_on_path(
                dest,
                &rel,
                matches!(entry_type, tar::EntryType::Directory),
                &mut verified_dirs,
            )?;
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
                    // 链接目标必须是相对路径、且真实解析后仍在 dest 之内(运行时里合法的链接都是 python3 -> python3.12 这类相对链)
                    if !symlink_target_within(dest, &rel, &target) {
                        return Err(archive_unsafe(format!(
                            "archive symlink target escapes dest: {} -> {}",
                            rel.display(),
                            target.display()
                        )));
                    }
                    if let Some(parent) = out.parent() {
                        fs::create_dir_all(parent)?;
                    }
                    let _ = fs::remove_file(&out);
                    std::os::unix::fs::symlink(&target, &out)
                        .with_context(|| format!("symlink {}", out.display()))?;
                    verified_dirs.retain(|p| !p.starts_with(&rel));
                    created_links.push((rel.clone(), target));
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
                    // 硬链目标也不许经链接指到树外(否则新条目与树外文件共用 inode)
                    ensure_no_symlink_on_path(dest, &target_rel, true, &mut verified_dirs)?;
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
        // 收尾复核:先建的链接可能被后建的链接改变真实落点(`a -> b/../x` 建时 b 还不存在,随后 `b -> .`)
        for (rel, target) in &created_links {
            if !symlink_target_within(dest, rel, target) {
                return Err(archive_unsafe(format!(
                    "archive symlink target escapes dest after extraction: {} -> {}",
                    rel.display(),
                    target.display()
                )));
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

pub(crate) fn extract_tar_gz_native(
    archive_path: &Path,
    dest: &Path,
    strip: usize,
    progress: Option<&dyn Fn(u64, u64, u64)>,
) -> Result<()> {
    extract_tar_gz_native_with(archive_path, dest, strip, extract_concurrency(), progress)
}

/// 外部 /usr/bin/tar 解压(历史行为原样保留,native 的回退路径)。
pub(crate) fn tar_extract_external(archive: &Path, dest: &Path, strip1: bool) -> Result<()> {
    let mut cmd = Command::new("/usr/bin/tar");
    if strip1 {
        cmd.arg("--strip-components=1");
    }
    let status = cmd
        // [更新槽复用] -U 先删条目再建新文件:暂存槽里的文件可能是与旧树共用 inode 的硬链接,就地覆盖写会伤到正在跑的旧树
        .arg("-U")
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

pub(crate) fn tar_extract_strip1(archive: &Path, dest: &Path) -> Result<()> {
    tar_extract_strip1_with(archive, dest, None)
}

pub(crate) fn tar_extract_strip1_with(
    archive: &Path,
    dest: &Path,
    progress: Option<&dyn Fn(u64, u64, u64)>,
) -> Result<()> {
    if extract_native_enabled() {
        match extract_tar_gz_native(archive, dest, 1, progress) {
            Ok(()) => return Ok(()),
            // 归档本身不安全:整包拒收,不换外部 tar 再试
            Err(err) if is_archive_unsafe(&err) => return Err(err),
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
