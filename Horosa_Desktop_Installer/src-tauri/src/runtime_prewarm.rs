//! 首启原生库预检。

use super::*;

// ─────────────────────────────────────────────────────────────────────────────
// [首启原生库预检] 装包 / 更新后第一次打开,盘要等十几秒的根治件。
//
// 根因(已用「刚解包的运行时」在备用端口复现):macOS 对每个新落盘的原生库(Mach-O)在
// 第一次被加载时做一次系统安全评估(syspolicyd),约 0.07–0.1 s 一个,系统侧基本串行。
// 排盘服务预热 + JVM 引导要加载约 130 个,所以这一次启动多等 10–16 s;同一批文件第二次加载
// 只要 0.6 s。评估结果按文件身份记:整目录改名不失效,重新解包 / APFS 克隆出来的都算新文件。
//
// 做法:在用户启动之前把评估触发掉 —— 对运行时树里每个 Mach-O 的本机架构切片做两次 fcntl
// (挂签名 F_ADDFILESIGS_RETURN + 库校验 F_CHECK_LV)。不映射、不执行任何库代码;
// 实测此后同一批文件的服务启动回到 0.66 s。系统侧串行,所以按「启动要用的先做」排序
// (顺序表 config/native_prewarm_priority.json,编译期嵌入)。
//
// 接线:安装脚本装完即在后台跑一遍(子命令 --horosa-native-prewarm,做完即退)·
// 其余情形(应用内更新 / 首启自装 / 修复 / 手动拷贝 / 上次被打断)服务就绪后后台补做。
// 两处都是一次性的活,不驻留;App 进程内那条随进程结束。
// 总开关:HOROSA_NATIVE_PREWARM=0。
// ─────────────────────────────────────────────────────────────────────────────
pub(crate) const NATIVE_PREWARM_MARKER_FILE: &str = ".native-prewarm.json";
const NATIVE_PREWARM_PRIORITY_JSON: &str =
    include_str!("../../config/native_prewarm_priority.json");
#[cfg(target_os = "macos")]
const NATIVE_PREWARM_F_ADDFILESIGS_RETURN: libc::c_int = 97;
#[cfg(target_os = "macos")]
const NATIVE_PREWARM_F_CHECK_LV: libc::c_int = 98;
const NATIVE_PREWARM_LC_CODE_SIGNATURE: u32 = 0x1d;
/// 单个文件耗时 ≥ 此值(ms)记为「系统真的评估了一次」;评估过的文件约 0.1–2 ms。
const NATIVE_PREWARM_EVALUATED_MS: f64 = 15.0;

#[derive(Debug, Clone, Default, Serialize, Deserialize)]
pub(crate) struct NativePrewarmMarker {
    pub(crate) v: u32,
    identity: String,
    pub(crate) files: usize,
    evaluated: usize,
    pub(crate) ms: u64,
    pub(crate) complete: bool,
    pub(crate) at: u64,
}

#[derive(Debug, Clone, Default)]
pub(crate) struct NativePrewarmStats {
    pub(crate) files: usize,
    pub(crate) startup_files: usize,
    pub(crate) touched: usize,
    evaluated: usize,
    pub(crate) ms: u64,
    pub(crate) complete: bool,
    pub(crate) timed_out: bool,
}

#[cfg(target_os = "macos")]
#[repr(C)]
pub(crate) struct NativePrewarmFsignatures {
    fs_file_start: libc::off_t,
    fs_blob_start: *mut libc::c_void,
    fs_blob_size: libc::size_t,
    // 新版内核的结构体更长(fs_fsignatures_size / fs_cdhash / fs_hash_type),留足尾部
    pub(crate) tail: [u8; 64],
}

#[cfg(target_os = "macos")]
#[repr(C)]
struct NativePrewarmFchecklv {
    lv_file_start: libc::off_t,
    lv_error_message_size: libc::size_t,
    lv_error_message: *mut libc::c_void,
}

pub(crate) fn native_prewarm_enabled_from(value: Option<&str>) -> bool {
    value.map(|v| v.trim() != "0").unwrap_or(true)
}

fn native_prewarm_enabled() -> bool {
    native_prewarm_enabled_from(std::env::var("HOROSA_NATIVE_PREWARM").ok().as_deref())
}

/// 回 (各档片段表, 启动档数)。配置坏了 = 空表(全部同档,顺序退化为路径序,功能不受影响)。
pub(crate) fn native_prewarm_tiers() -> (Vec<Vec<String>>, u32) {
    let parsed = serde_json::from_str::<serde_json::Value>(NATIVE_PREWARM_PRIORITY_JSON).ok();
    let tiers: Vec<Vec<String>> = parsed
        .as_ref()
        .and_then(|v| v.get("tiers"))
        .and_then(|t| t.as_array())
        .map(|tiers| {
            tiers
                .iter()
                .map(|tier| {
                    tier.as_array()
                        .map(|a| {
                            a.iter()
                                .filter_map(|s| s.as_str().map(|s| s.to_string()))
                                .collect()
                        })
                        .unwrap_or_default()
                })
                .collect()
        })
        .unwrap_or_default();
    let startup = parsed
        .as_ref()
        .and_then(|v| v.get("startupTiers"))
        .and_then(|n| n.as_u64())
        .map(|n| n as u32)
        .unwrap_or(tiers.len() as u32)
        .min(tiers.len() as u32);
    (tiers, startup)
}

pub(crate) fn native_prewarm_tier_of(rel: &str, tiers: &[Vec<String>]) -> u32 {
    for (idx, tier) in tiers.iter().enumerate() {
        if tier.iter().any(|needle| rel.contains(needle.as_str())) {
            return idx as u32;
        }
    }
    tiers.len() as u32
}

/// 回本机架构切片的 (偏移, 长度);不是 Mach-O 回空。
/// Java .class 与 fat Mach-O 同魔数 CAFEBABE:class 文件此处 4 字节是版本号(≥ 45),按切片数 ≤ 32 区分。
pub(crate) fn native_prewarm_slices(head: &[u8], file_len: u64) -> Vec<(u64, u64)> {
    if head.len() < 8 {
        return Vec::new();
    }
    let magic = [head[0], head[1], head[2], head[3]];
    if magic == [0xcf, 0xfa, 0xed, 0xfe] || magic == [0xce, 0xfa, 0xed, 0xfe] {
        return vec![(0, file_len)];
    }
    let fat64 = magic == [0xca, 0xfe, 0xba, 0xbf];
    if magic != [0xca, 0xfe, 0xba, 0xbe] && !fat64 {
        return Vec::new();
    }
    let count = u32::from_be_bytes([head[4], head[5], head[6], head[7]]) as usize;
    if count == 0 || count > 32 {
        return Vec::new();
    }
    let want: i32 = if cfg!(target_arch = "aarch64") {
        0x0100_000c
    } else {
        0x0100_0007
    };
    let step = if fat64 { 32 } else { 20 };
    let mut all = Vec::new();
    let mut host = Vec::new();
    for i in 0..count {
        let o = 8 + i * step;
        if head.len() < o + step {
            break;
        }
        let cpu = i32::from_be_bytes([head[o], head[o + 1], head[o + 2], head[o + 3]]);
        let be32 = |p: usize| u32::from_be_bytes([head[p], head[p + 1], head[p + 2], head[p + 3]]);
        let be64 = |p: usize| ((be32(p) as u64) << 32) | be32(p + 4) as u64;
        let (off, size) = if fat64 {
            (be64(o + 8), be64(o + 16))
        } else {
            (be32(o + 8) as u64, be32(o + 12) as u64)
        };
        if off == 0 || size == 0 || off.saturating_add(size) > file_len {
            continue;
        }
        all.push((off, size));
        if cpu == want {
            host.push((off, size));
        }
    }
    if host.is_empty() {
        all
    } else {
        host
    }
}

/// 读切片的 LC_CODE_SIGNATURE:回 (签名在切片内的偏移, 长度);没签名回 None。
fn native_prewarm_codesig(file: &mut File, base: u64) -> Option<(u64, u64)> {
    use std::io::{Seek, SeekFrom};
    let mut header = [0u8; 32];
    file.seek(SeekFrom::Start(base)).ok()?;
    file.read_exact(&mut header).ok()?;
    let magic = [header[0], header[1], header[2], header[3]];
    let is64 = magic == [0xcf, 0xfa, 0xed, 0xfe];
    if !is64 && magic != [0xce, 0xfa, 0xed, 0xfe] {
        return None;
    }
    let le32 = |b: &[u8], p: usize| u32::from_le_bytes([b[p], b[p + 1], b[p + 2], b[p + 3]]);
    let ncmds = le32(&header, 16);
    let sizeofcmds = le32(&header, 20) as usize;
    if sizeofcmds == 0 || sizeofcmds > (1 << 20) {
        return None;
    }
    let header_len: u64 = if is64 { 32 } else { 28 };
    let mut cmds = vec![0u8; sizeofcmds];
    file.seek(SeekFrom::Start(base + header_len)).ok()?;
    file.read_exact(&mut cmds).ok()?;
    let mut p = 0usize;
    for _ in 0..ncmds {
        if p + 8 > cmds.len() {
            break;
        }
        let cmd = le32(&cmds, p);
        let size = le32(&cmds, p + 4) as usize;
        if size < 8 {
            break;
        }
        if cmd == NATIVE_PREWARM_LC_CODE_SIGNATURE && p + 16 <= cmds.len() {
            return Some((le32(&cmds, p + 8) as u64, le32(&cmds, p + 12) as u64));
        }
        p += size;
    }
    None
}

/// 只读文件头判「是不是 Mach-O」(收集阶段用;不触发任何评估)。
pub(crate) fn native_prewarm_is_macho(path: &Path) -> bool {
    let Ok(mut file) = File::open(path) else {
        return false;
    };
    let Ok(len) = file.metadata().map(|m| m.len()) else {
        return false;
    };
    let mut head = vec![0u8; 4096];
    let Ok(n) = file.read(&mut head) else {
        return false;
    };
    head.truncate(n);
    !native_prewarm_slices(&head, len).is_empty()
}

/// 对一个 Mach-O 触发系统的首次加载评估;回耗时(ms)。不是 Mach-O / 打不开回 None。
/// 只有两次 fcntl:不映射、不执行库里的任何代码;调用失败一律忽略(评估在调用里已经发生)。
#[cfg(target_os = "macos")]
pub(crate) fn native_prewarm_touch(path: &Path) -> Option<f64> {
    use std::os::unix::io::AsRawFd;
    let started = Instant::now();
    let mut file = File::open(path).ok()?;
    let len = file.metadata().ok()?.len();
    let mut head = vec![0u8; 4096];
    let n = file.read(&mut head).ok()?;
    head.truncate(n);
    let slices = native_prewarm_slices(&head, len);
    if slices.is_empty() {
        return None;
    }
    for (base, _size) in slices {
        let Some((sig_off, sig_len)) = native_prewarm_codesig(&mut file, base) else {
            continue;
        };
        let fd = file.as_raw_fd();
        let mut sig = NativePrewarmFsignatures {
            fs_file_start: base as libc::off_t,
            fs_blob_start: sig_off as usize as *mut libc::c_void,
            fs_blob_size: sig_len as libc::size_t,
            tail: [0u8; 64],
        };
        let mut message = [0u8; 1024];
        let mut lv = NativePrewarmFchecklv {
            lv_file_start: base as libc::off_t,
            lv_error_message_size: message.len() as libc::size_t,
            lv_error_message: message.as_mut_ptr() as *mut libc::c_void,
        };
        unsafe {
            let _ = libc::fcntl(
                fd,
                NATIVE_PREWARM_F_ADDFILESIGS_RETURN,
                &mut sig as *mut NativePrewarmFsignatures,
            );
            let _ = libc::fcntl(
                fd,
                NATIVE_PREWARM_F_CHECK_LV,
                &mut lv as *mut NativePrewarmFchecklv,
            );
        }
    }
    Some(started.elapsed().as_secs_f64() * 1000.0)
}

#[cfg(not(target_os = "macos"))]
pub(crate) fn native_prewarm_touch(_path: &Path) -> Option<f64> {
    None
}

/// 收集运行时树里全部 Mach-O,按(档, 相对路径)排好序。
pub(crate) fn native_prewarm_collect(
    runtime_dir: &Path,
    tiers: &[Vec<String>],
) -> Vec<(u32, PathBuf)> {
    use std::os::unix::fs::PermissionsExt;
    let mut found: Vec<(u32, String, PathBuf)> = Vec::new();
    for entry in WalkDir::new(runtime_dir)
        .follow_links(false)
        .into_iter()
        .filter_map(|e| e.ok())
    {
        if !entry.file_type().is_file() {
            continue;
        }
        let path = entry.path();
        let by_ext = matches!(
            path.extension().and_then(|e| e.to_str()),
            Some("so") | Some("dylib") | Some("jnilib")
        );
        let executable = entry
            .metadata()
            .map(|m| m.permissions().mode() & 0o111 != 0)
            .unwrap_or(false);
        if !by_ext && !executable {
            continue;
        }
        if !native_prewarm_is_macho(path) {
            continue;
        }
        let rel = path
            .strip_prefix(runtime_dir)
            .unwrap_or(path)
            .to_string_lossy()
            .replace('\\', "/");
        found.push((native_prewarm_tier_of(&rel, tiers), rel, path.to_path_buf()));
    }
    found.sort_by(|a, b| (a.0, &a.1).cmp(&(b.0, &b.1)));
    found
        .into_iter()
        .map(|(tier, _, path)| (tier, path))
        .collect()
}

/// 运行时树的「文件身份」:解释器 / JVM / 清单三者的 inode + 部件锁内容摘要。重新解包、克隆都会变,
/// 整目录改名不变;硬链接搭的暂存槽里未变部件的 inode 不变,靠锁摘要看出「换过部件」。
pub(crate) fn native_prewarm_identity(runtime_dir: &Path) -> Option<String> {
    use std::os::unix::fs::MetadataExt;
    let python = fs::metadata(runtime_python_bin(runtime_dir)).ok()?;
    let java = fs::metadata(runtime_java_bin(runtime_dir)).ok()?;
    let manifest = fs::metadata(runtime_dir.join("runtime-manifest.json")).ok()?;
    let lock_digest = fs::read(runtime_dir.join("components-lock.json"))
        .ok()
        .map(|bytes| {
            let mut hasher = Sha256::new();
            hasher.update(&bytes);
            format!("{:x}", hasher.finalize())[..16].to_string()
        })
        .unwrap_or_else(|| "nolock".to_string());
    Some(format!(
        "{}:{}:{}:{}:{}",
        python.ino(),
        java.ino(),
        manifest.ino(),
        manifest.len(),
        lock_digest
    ))
}

pub(crate) fn native_prewarm_marker(runtime_dir: &Path) -> Option<NativePrewarmMarker> {
    let text = fs::read_to_string(runtime_dir.join(NATIVE_PREWARM_MARKER_FILE)).ok()?;
    serde_json::from_str(&text).ok()
}

/// 这棵运行时还要不要预检:没有标记 / 标记记的是别的文件身份 / 上次没做完 → 要。
pub(crate) fn native_prewarm_needed(runtime_dir: &Path) -> bool {
    let Some(identity) = native_prewarm_identity(runtime_dir) else {
        return false; // 树不完整(缺解释器 / JVM / 清单):不是这里该管的事
    };
    match native_prewarm_marker(runtime_dir) {
        Some(marker) if marker.identity == identity => !marker.complete,
        _ => true,
    }
}

/// 跑一遍预检(全树,按档序)。budget 到了就收手(已派出的调用让它自己做完)。
/// 结束后落标记;没超时才记 complete。
pub(crate) fn native_prewarm_run(
    runtime_dir: &Path,
    threads: usize,
    budget: Duration,
    progress: Option<&dyn Fn(usize, usize)>,
) -> NativePrewarmStats {
    let started = Instant::now();
    let (tiers, startup_tiers) = native_prewarm_tiers();
    let all = native_prewarm_collect(runtime_dir, &tiers);
    let startup_files = all.iter().filter(|(tier, _)| *tier < startup_tiers).count();
    let targets: Vec<PathBuf> = all.into_iter().map(|(_, path)| path).collect();
    let total = targets.len();
    let targets = Arc::new(targets);
    let next = Arc::new(AtomicUsize::new(0));
    let done = Arc::new(AtomicUsize::new(0));
    let touched = Arc::new(AtomicUsize::new(0));
    let evaluated = Arc::new(AtomicUsize::new(0));
    let stop = Arc::new(AtomicBool::new(false));
    let workers = threads.clamp(1, 8).min(total.max(1));
    let alive = Arc::new(AtomicUsize::new(workers));
    for _ in 0..workers {
        let targets = Arc::clone(&targets);
        let next = Arc::clone(&next);
        let done = Arc::clone(&done);
        let touched = Arc::clone(&touched);
        let evaluated = Arc::clone(&evaluated);
        let stop = Arc::clone(&stop);
        let alive = Arc::clone(&alive);
        thread::spawn(move || {
            loop {
                if stop.load(Ordering::SeqCst) {
                    break;
                }
                let idx = next.fetch_add(1, Ordering::SeqCst);
                if idx >= targets.len() {
                    break;
                }
                if let Some(ms) = native_prewarm_touch(&targets[idx]) {
                    touched.fetch_add(1, Ordering::SeqCst);
                    if ms >= NATIVE_PREWARM_EVALUATED_MS {
                        evaluated.fetch_add(1, Ordering::SeqCst);
                    }
                }
                done.fetch_add(1, Ordering::SeqCst);
            }
            alive.fetch_sub(1, Ordering::SeqCst);
        });
    }
    let mut timed_out = false;
    let mut last_reported = usize::MAX;
    loop {
        if let Some(cb) = progress {
            let finished = done.load(Ordering::SeqCst).min(total);
            if finished != last_reported {
                cb(finished, total);
                last_reported = finished;
            }
        }
        if alive.load(Ordering::SeqCst) == 0 {
            break;
        }
        if started.elapsed() >= budget {
            timed_out = true;
            stop.store(true, Ordering::SeqCst);
            break;
        }
        thread::sleep(Duration::from_millis(50));
    }
    let stats = NativePrewarmStats {
        files: total,
        startup_files,
        touched: touched.load(Ordering::SeqCst),
        evaluated: evaluated.load(Ordering::SeqCst),
        ms: started.elapsed().as_millis() as u64,
        complete: !timed_out && done.load(Ordering::SeqCst) >= total,
        timed_out,
    };
    if let Some(identity) = native_prewarm_identity(runtime_dir) {
        let marker = NativePrewarmMarker {
            v: 1,
            identity,
            files: stats.files,
            evaluated: stats.evaluated,
            ms: stats.ms,
            complete: stats.complete,
            at: unix_ts(),
        };
        if let Ok(text) = serde_json::to_string(&marker) {
            // 换名落盘:安装器以 root 身份跑预检时写出的旧标记归 root,属主账户照样能换掉它(目录是属主的)。
            // 不再放开给所有账户写:多账户机上其他账户只读,写不进就算了(下次由属主补)。
            let _ = write_file_replacing(
                &runtime_dir.join(NATIVE_PREWARM_MARKER_FILE),
                text.as_bytes(),
            );
        }
    }
    stats
}

/// 子命令 --horosa-native-prewarm <运行时目录>:零界面,做完即退(上限 180 秒)。
/// 退出码恒 0 —— 预检是优化,任何情形都不该让安装失败。
pub(crate) fn run_native_prewarm_cli(runtime_dir: &Path) -> i32 {
    if !native_prewarm_enabled() {
        println!("native-prewarm: disabled by HOROSA_NATIVE_PREWARM=0");
        return 0;
    }
    if !native_prewarm_needed(runtime_dir) {
        println!(
            "native-prewarm: nothing to do for {}",
            runtime_dir.display()
        );
        return 0;
    }
    let stats = native_prewarm_run(runtime_dir, 4, Duration::from_secs(180), None);
    println!(
        "native-prewarm: files={} startup={} touched={} evaluated={} ms={} complete={} timed_out={}",
        stats.files,
        stats.startup_files,
        stats.touched,
        stats.evaluated,
        stats.ms,
        stats.complete,
        stats.timed_out
    );
    0
}

/// 服务就绪后后台补做:没预检过的运行时(应用内更新 / 首启自装 / 修复 / 手动拷贝 / 上次被打断)。
/// 同一文件身份每进程只起一次;延后 12 秒让首屏取盘与后端自热身先走;两线程,不与前台抢。
pub(crate) fn spawn_native_prewarm_after_ready(app: &AppHandle) {
    static LAST_IDENTITY: Mutex<Option<String>> = Mutex::new(None);
    if !native_prewarm_enabled() {
        return;
    }
    let runtime_dir = app
        .try_state::<AppState>()
        .and_then(|state| {
            state
                .session
                .lock()
                .ok()
                .and_then(|slot| slot.as_ref().map(|s| s.paths.runtime_dir.clone()))
        })
        .unwrap_or_else(shared_runtime_dir);
    let Some(identity) = native_prewarm_identity(&runtime_dir) else {
        return;
    };
    if let Ok(mut last) = LAST_IDENTITY.lock() {
        if last.as_deref() == Some(identity.as_str()) {
            return;
        }
        *last = Some(identity);
    }
    thread::spawn(move || {
        thread::sleep(Duration::from_secs(12));
        if !native_prewarm_needed(&runtime_dir) {
            return;
        }
        let stats = native_prewarm_run(&runtime_dir, 2, Duration::from_secs(180), None);
        ledger_mark(
            "rust.native_prewarm",
            Some(serde_json::json!({
                "where": "post-ready",
                "files": stats.files,
                "evaluated": stats.evaluated,
                "ms": stats.ms,
                "complete": stats.complete,
            })),
        );
    });
}
/// [更新槽复用] 换完运行时(增量 / 全量 / 首启自装 / helper 全量对换)立刻对新树做首次加载预检:硬链接复用的
/// 未变文件已评估过(约 1 ms 一个),只有本次真换的部件里的原生库要真评估;文件身份随后续 rename 不变,
/// 评估状态直接带进 current。say 收进度文案;失败 / 超时无害(就绪后补做兜底)。
pub(crate) fn native_prewarm_after_runtime_update(
    runtime_dir: &Path,
    say: &dyn Fn(&str),
    site: &str,
) {
    if !native_prewarm_enabled() || !native_prewarm_needed(runtime_dir) {
        return;
    }
    say("正在完成新版本的首次加载检查…");
    let last = std::cell::Cell::new(Instant::now());
    let progress = |done: usize, total: usize| {
        if total > 0 && (done == total || last.get().elapsed() >= Duration::from_millis(700)) {
            last.set(Instant::now());
            say(&format!("正在完成新版本的首次加载检查 {}/{}", done, total));
        }
    };
    let stats = native_prewarm_run(runtime_dir, 4, Duration::from_secs(120), Some(&progress));
    say(&format!(
        "首次加载检查完成:{} 个原生库,新评估 {} 个,{:.1} 秒",
        stats.files,
        stats.evaluated,
        stats.ms as f64 / 1000.0
    ));
    ledger_mark(
        "rust.native_prewarm",
        Some(serde_json::json!({
            "where": site,
            "files": stats.files,
            "evaluated": stats.evaluated,
            "ms": stats.ms,
            "complete": stats.complete,
        })),
    );
}
// ── [首启原生库预检] 块尾 ─────────────────────────────────────────────────────
