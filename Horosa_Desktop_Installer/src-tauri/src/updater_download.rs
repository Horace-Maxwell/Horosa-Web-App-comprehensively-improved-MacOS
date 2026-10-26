//! 断点续传下载与临时下载清扫。

use super::*;

pub(crate) fn ensure_dir(path: &Path) -> Result<()> {
    fs::create_dir_all(path).with_context(|| format!("mkdir -p {}", path.display()))
}

pub(crate) fn tmp_download_path(app_name: &str, suffix: &str) -> PathBuf {
    let ts = SystemTime::now()
        .duration_since(UNIX_EPOCH)
        .unwrap_or_else(|_| Duration::from_secs(0))
        .as_secs();
    std::env::temp_dir().join(format!("{}-{}-{}", app_name, ts, suffix))
}

// ============ 断点续传下载核(WS-1b,launcher/update 双通道共用) ============
// 协议:数据写 dest.part,旁挂 dest.part.meta(url/etag/total/续传次数);
// 中断后(同进程重试或跨进程重启)part+meta 在位且 url 相同 → Range bytes=N- 请求:
//   206 且 etag 未变 → append 续传;200(服务器不理 Range)→ 就地当全新流用;
//   etag 冲突/416/续传次数超限 → 自动退全新下载。
// 完成 sync+原子 rename part→dest:dest 永远不出现半成品,sha 校验仍由调用方兜底;
// 若续传拼合出错,外层 sha 失败时 part 已被 rename 消费 → 下一轮天然全新重下。
// kill-switch: HOROSA_DOWNLOAD_NO_RESUME=1 退回全新下载(现状行为)。

pub(crate) const RESUME_MAX_ATTEMPTS: u32 = 4;

#[derive(Serialize, Deserialize, Default)]
pub(crate) struct PartMeta {
    pub(crate) url: String,
    #[serde(default)]
    pub(crate) etag: Option<String>,
    #[serde(default)]
    pub(crate) total: u64,
    #[serde(default)]
    pub(crate) resume_attempts: u32,
}

pub(crate) fn download_resume_enabled() -> bool {
    std::env::var("HOROSA_DOWNLOAD_NO_RESUME")
        .map(|v| !matches!(v.as_str(), "1" | "true" | "yes" | "on"))
        .unwrap_or(true)
}

pub(crate) fn download_part_paths(dest: &Path) -> (PathBuf, PathBuf) {
    let name = dest
        .file_name()
        .map(|s| s.to_string_lossy().to_string())
        .unwrap_or_else(|| "download".to_string());
    let dir = dest
        .parent()
        .map(|p| p.to_path_buf())
        .unwrap_or_else(|| PathBuf::from("."));
    (
        dir.join(format!("{}.part", name)),
        dir.join(format!("{}.part.meta", name)),
    )
}

fn load_part_meta(path: &Path) -> Option<PartMeta> {
    let text = fs::read_to_string(path).ok()?;
    serde_json::from_str(&text).ok()
}

pub(crate) fn save_part_meta(path: &Path, meta: &PartMeta) {
    if let Ok(text) = serde_json::to_string(meta) {
        let _ = fs::write(path, text);
    }
}

pub(crate) fn clear_part_files(part: &Path, meta: &Path) {
    let _ = fs::remove_file(part);
    let _ = fs::remove_file(meta);
}

fn response_etag(resp: &reqwest::blocking::Response) -> Option<String> {
    resp.headers()
        .get(reqwest::header::ETAG)
        .and_then(|v| v.to_str().ok())
        .map(|s| s.to_string())
}

/// 解析 206 的 Content-Range: bytes N-M/TOTAL,取 TOTAL。
fn parse_content_range_total(resp: &reqwest::blocking::Response) -> Option<u64> {
    let value = resp
        .headers()
        .get(reqwest::header::CONTENT_RANGE)?
        .to_str()
        .ok()?;
    value.rsplit('/').next()?.trim().parse::<u64>().ok()
}

/// 下载进度回执:downloaded 含续传补入的既有字节;delta=本次新读字节。
pub(crate) struct DownloadChunk {
    pub(crate) downloaded: u64,
    pub(crate) total: u64,
    pub(crate) delta: u64,
}

/// 断点续传单次下载。成功=dest 原子就位;失败=part/meta 保留供下一轮续传。
/// on_start(resumed_from,total) 连接建立后调一次;on_chunk 每读一块调(节流由调用方闭包自理)。
pub(crate) fn download_resumable_once(
    url: &str,
    dest: &Path,
    allow_resume: bool,
    on_start: impl FnOnce(u64, u64),
    mut on_chunk: impl FnMut(&DownloadChunk),
) -> Result<()> {
    let client = build_github_client(900)?;
    if let Some(parent) = dest.parent() {
        ensure_dir(parent)?;
    }
    let (part_path, meta_path) = download_part_paths(dest);
    if !allow_resume {
        clear_part_files(&part_path, &meta_path);
    }

    // 续传资格判定:part+meta 在位、同 url、长度>0 且未满、续传次数未超限。
    let mut resume_offset: u64 = 0;
    let mut resume_meta: Option<PartMeta> = None;
    if allow_resume {
        if let Some(meta) = load_part_meta(&meta_path) {
            let part_len = fs::metadata(&part_path).map(|m| m.len()).unwrap_or(0);
            let len_ok = part_len > 0 && (meta.total == 0 || part_len < meta.total);
            if meta.url == url && len_ok && meta.resume_attempts < RESUME_MAX_ATTEMPTS {
                resume_offset = part_len;
                resume_meta = Some(meta);
            } else {
                clear_part_files(&part_path, &meta_path);
            }
        } else if part_path.exists() {
            // 有 part 无 meta:无从判定来源,弃之。
            clear_part_files(&part_path, &meta_path);
        }
    }

    // 先试 Range 续传;拿不到干净的 206 就退全新(200 全量流可直接就地消费)。
    let mut session: Option<(reqwest::blocking::Response, File, u64, u64)> = None;
    let mut fresh_response: Option<reqwest::blocking::Response> = None;
    if resume_offset > 0 {
        let mut meta = resume_meta.take().unwrap_or_default();
        meta.resume_attempts += 1;
        save_part_meta(&meta_path, &meta);
        if let Ok(resp) = client
            .get(url)
            .header("User-Agent", "HorosaDesktop")
            .header("Range", format!("bytes={}-", resume_offset))
            .send()
        {
            let status = resp.status();
            if status == reqwest::StatusCode::PARTIAL_CONTENT {
                let etag_conflict = matches!(
                    (&meta.etag, &response_etag(&resp)),
                    (Some(old), Some(new)) if old != new
                );
                if !etag_conflict {
                    let total = parse_content_range_total(&resp).unwrap_or_else(|| {
                        resp.content_length()
                            .map(|len| resume_offset + len)
                            .unwrap_or(meta.total)
                    });
                    let file = fs::OpenOptions::new()
                        .append(true)
                        .open(&part_path)
                        .with_context(|| format!("open part {}", part_path.display()))?;
                    session = Some((resp, file, resume_offset, total));
                }
            } else if status.is_success() {
                // 服务器不支持 Range(回 200 全量):直接把这条响应当全新下载用,省一次握手。
                fresh_response = Some(resp);
            }
            // 416/其它状态:落空,下面统一发全新请求。
        }
    }

    let (mut response, mut file, start_offset, total) = match session {
        Some(s) => s,
        None => {
            let resp = match fresh_response {
                Some(r) => r,
                None => client
                    .get(url)
                    .header("User-Agent", "HorosaDesktop")
                    .header("Cache-Control", "no-cache")
                    .header("Pragma", "no-cache")
                    .send()
                    .with_context(|| format!("download {}", url))?,
            };
            if !resp.status().is_success() {
                return Err(anyhow!("download failed: {} -> {}", url, resp.status()));
            }
            let total = resp.content_length().unwrap_or(0);
            save_part_meta(
                &meta_path,
                &PartMeta {
                    url: url.to_string(),
                    etag: response_etag(&resp),
                    total,
                    resume_attempts: 0,
                },
            );
            // File::create 截断:etag 冲突/416 后的残余 part 在此归零重写。
            let file = File::create(&part_path)?;
            (resp, file, 0u64, total)
        }
    };

    on_start(start_offset, total);
    let mut downloaded = start_offset;
    let mut buffer = [0u8; 64 * 1024];
    loop {
        let read = response.read(&mut buffer)?;
        if read == 0 {
            break;
        }
        file.write_all(&buffer[..read])?;
        downloaded += read as u64;
        on_chunk(&DownloadChunk {
            downloaded,
            total,
            delta: read as u64,
        });
    }
    if total > 0 && downloaded < total {
        return Err(anyhow!(
            "download incomplete: {} -> {}/{} bytes",
            url,
            downloaded,
            total
        ));
    }
    let _ = file.sync_all();
    drop(file);
    fs::rename(&part_path, dest).with_context(|| format!("finalize {}", dest.display()))?;
    let _ = fs::remove_file(&meta_path);
    Ok(())
}

pub(crate) fn download_with_progress(
    window: &WebviewWindow,
    url: &str,
    dest: &Path,
    start_pct: u8,
    end_pct: u8,
    label: &str,
) -> Result<()> {
    let mut last_err = None;
    for attempt in 1..=DOWNLOAD_MAX_ATTEMPTS {
        if attempt > 1 {
            let retry_msg = format!(
                "{} 失败，正在重试（{}/{}）…",
                label, attempt, DOWNLOAD_MAX_ATTEMPTS
            );
            emit_status(window, &retry_msg);
            emit_progress(window, start_pct, &retry_msg);
            thread::sleep(Duration::from_secs((attempt as u64 - 1) * 2));
        }
        match download_with_progress_once(window, url, dest, start_pct, end_pct, label) {
            Ok(()) => return Ok(()),
            Err(err) => {
                last_err = Some(err);
                // 半成品在 dest.part(由下载核管理),保留供下一轮断点续传;
                // dest 只在成功 rename 后出现,这里无需清理。
            }
        }
    }
    let err = last_err.unwrap_or_else(|| anyhow!("download failed without error detail"));
    Err(wrap_download_error(label, url, err))
}

fn download_with_progress_once(
    window: &WebviewWindow,
    url: &str,
    dest: &Path,
    start_pct: u8,
    end_pct: u8,
    label: &str,
) -> Result<()> {
    // launcher 通道薄壳:下载/续传逻辑在 download_resumable_once;
    // 这里只负责把进度烧进 message 字符串(launcher 页零改动受益);
    // 节流 ≥400ms 才 emit(此前每 64KB 一次 window.eval,大包即洪泛)。
    let started = Instant::now();
    let mut last_emit = Instant::now();
    let mut last_pct: i32 = -1;
    // 续传补入的既有字节,不计入本次会话速度(Cell:on_start/on_chunk 两闭包共享)
    let session_base = std::cell::Cell::new(0u64);
    download_resumable_once(
        url,
        dest,
        download_resume_enabled(),
        |resumed_from, total| {
            session_base.set(resumed_from);
            if resumed_from > 0 {
                emit_progress(
                    window,
                    start_pct,
                    &format!(
                        "{label}：检测到未完成的下载，从 {} MB 处继续…",
                        resumed_from / 1_048_576
                    ),
                );
            } else if total > 0 {
                emit_progress(
                    window,
                    start_pct,
                    &format!("{label}：已连接服务器，开始接收数据"),
                );
            } else {
                emit_indeterminate_progress(
                    window,
                    start_pct,
                    &format!("{label}：已连接服务器，正在接收数据…"),
                );
            }
        },
        |chunk| {
            if chunk.total == 0 {
                return;
            }
            let ratio = chunk.downloaded as f64 / chunk.total as f64;
            let span = end_pct.saturating_sub(start_pct) as f64;
            let pct = (start_pct as f64 + span * ratio).round() as i32;
            let now = Instant::now();
            if pct != last_pct && now.duration_since(last_emit) >= Duration::from_millis(400) {
                last_pct = pct;
                last_emit = now;
                let elapsed = started.elapsed().as_secs_f64().max(0.001);
                // 字节/秒(本次会话均速:续传补入的字节不计,避免虚高)
                let speed = chunk.downloaded.saturating_sub(session_base.get()) as f64 / elapsed;
                let remaining = (chunk.total.saturating_sub(chunk.downloaded)) as f64;
                let eta_secs = if speed > 0.0 {
                    (remaining / speed) as u64
                } else {
                    0
                };
                let eta_text = if eta_secs >= 60 {
                    format!("约剩 {} 分 {} 秒", eta_secs / 60, eta_secs % 60)
                } else {
                    format!("约剩 {} 秒", eta_secs)
                };
                emit_progress(
                    window,
                    pct as u8,
                    &format!(
                        "{}：已下载 {}/{} MB · {:.1} MB/s · {}",
                        label,
                        chunk.downloaded / 1_048_576,
                        chunk.total / 1_048_576,
                        speed / 1_048_576.0,
                        eta_text
                    ),
                );
            }
        },
    )?;
    emit_progress(window, end_pct, label);
    Ok(())
}

pub(crate) fn wrap_download_error(label: &str, url: &str, err: anyhow::Error) -> anyhow::Error {
    let details = format!("{err:#}");
    let lower = details.to_ascii_lowercase();
    let summary = if lower.contains("tls handshake eof") {
        format!(
            "{}失败：已自动重试 {} 次，但和 GitHub 建立安全连接时仍被中断。请稍后重试，或切换更稳定的网络后再试。",
            label, DOWNLOAD_MAX_ATTEMPTS
        )
    } else if lower.contains("timed out") || lower.contains("timeout") {
        format!(
            "{}失败：已自动重试 {} 次，但下载仍然超时。请稍后重试，或切换更稳定的网络后再试。",
            label, DOWNLOAD_MAX_ATTEMPTS
        )
    } else if lower.contains("dns")
        || lower.contains("failed to lookup")
        || lower.contains("name or service not known")
        || lower.contains("nodename nor servname")
    {
        format!(
            "{}失败：已自动重试 {} 次，但当前网络无法稳定解析 GitHub 地址。请检查网络或代理设置后再试。",
            label, DOWNLOAD_MAX_ATTEMPTS
        )
    } else {
        format!(
            "{}失败：已自动重试 {} 次仍未完成。请稍后重试；如果反复失败，请优先检查当前网络是否能访问 GitHub。",
            label, DOWNLOAD_MAX_ATTEMPTS
        )
    };
    anyhow!("{summary}\n下载地址: {url}\n原始错误: {details}")
}

/// 启动期 best-effort 清扫:更新下载的临时文件带时间戳后缀(每次新名),进程中途被杀时遗留
/// 在系统临时目录累积。删 24h 前的本应用模式文件;失败静默(清扫绝不影响启动)。
pub(crate) fn sweep_stale_tmp_downloads() {
    thread::spawn(|| {
        let tmp = std::env::temp_dir();
        let prefix = format!("{}-", APP_NAME);
        let cutoff = SystemTime::now() - Duration::from_secs(24 * 3600);
        if let Ok(entries) = fs::read_dir(&tmp) {
            for entry in entries.flatten() {
                let name = entry.file_name().to_string_lossy().to_string();
                if !name.starts_with(&prefix) {
                    continue;
                }
                let Ok(meta) = entry.metadata() else { continue };
                let Ok(modified) = meta.modified() else {
                    continue;
                };
                if modified < cutoff {
                    let path = entry.path();
                    let _ = if meta.is_dir() {
                        fs::remove_dir_all(&path)
                    } else {
                        fs::remove_file(&path)
                    };
                }
            }
        }
    });
}
