//! 启动账本、更新台账与页面上报。

use super::*;

/// 页面侧桥自检上报:页面启动时把 typeof window.__TAURI__ / __TAURI_INTERNALS__ 与 event.listen 的 ACL 探测结果
/// 写进启动账本 —— 真机上「桥到底通没通」有据可查(诊断包一并导出),不靠猜。
#[tauri::command]
pub(crate) fn bridge_diag_report_command(
    payload: serde_json::Value,
) -> std::result::Result<bool, String> {
    ledger_mark("rust.bridge_diag", Some(payload));
    Ok(true)
}

/// 前端启动段上报:seg 限 `web.[a-z0-9_]{1,40}`;at_epoch_ms = 页面 Date.now()(壳按 run 标签折算到
/// 与 rust.* 同一 t_ms 尺度);extra 只放页面侧的小对象(sinceNavMs 等)。纯观测:账本关闭(HOROSA_STARTUP_LEDGER=0)
/// 时 ledger 未初始化即静默丢弃;非法段名拒收(不写账本)。
#[tauri::command]
pub(crate) fn web_ledger_mark_command(
    seg: String,
    at_epoch_ms: Option<f64>,
    extra: Option<serde_json::Value>,
) -> std::result::Result<bool, String> {
    if !web_ledger_seg_ok(&seg) {
        return Err("bad seg".to_string());
    }
    ledger_mark_layer_at("web", &seg, at_epoch_ms, web_ledger_extra_capped(extra));
    Ok(true)
}

/// 页面上报的附加字段只作诊断,序列化超过 4 KB 即只记长度(账本随诊断导出,不许被页面灌大)。
pub(crate) const WEB_LEDGER_EXTRA_MAX_BYTES: usize = 4096;

pub(crate) fn web_ledger_extra_capped(
    extra: Option<serde_json::Value>,
) -> Option<serde_json::Value> {
    let value = extra?;
    let bytes = serde_json::to_string(&value).map(|s| s.len()).unwrap_or(0);
    if bytes > WEB_LEDGER_EXTRA_MAX_BYTES {
        Some(serde_json::json!({ "truncated": true, "bytes": bytes }))
    } else {
        Some(value)
    }
}

pub(crate) fn web_ledger_seg_ok(seg: &str) -> bool {
    let Some(rest) = seg.strip_prefix("web.") else {
        return false;
    };
    !rest.is_empty()
        && rest.len() <= 40
        && rest
            .bytes()
            .all(|b| b.is_ascii_lowercase() || b.is_ascii_digit() || b == b'_')
}

/// ── 结构化启动账本(Rust 层写入端)────────────────────────────────────────────
/// 一行一段 JSON Lines,四层进程(Rust/shell/Java/Python)经 env(HOROSA_RUN_TAG/
/// HOROSA_LEDGER_FILE)共享同一文件;Rust 是 run 标签的生成者。只在段边界打点,
/// append + best-effort 吞错,账本绝不影响启动;HOROSA_STARTUP_LEDGER=0 总关。
pub(crate) static STARTUP_LEDGER: std::sync::OnceLock<Option<(String, PathBuf, Instant)>> =
    std::sync::OnceLock::new();

/// 日志目录防写满盘:每次启动都会新建一个 run 子目录(四层账本+服务 stdout),放任累积
/// 数月可达 GB 级——启动期 best-effort 修剪:>14 天的子目录/文件删除;常追加的单文件
/// (如 updater-events.log)超 20MB 轮转成 .old 保一代。失败只跳过,绝不阻塞启动。
pub(crate) fn prune_logs_dir_best_effort(logs_dir: &Path) {
    const MAX_AGE: Duration = Duration::from_secs(14 * 24 * 3600);
    const MAX_SINGLE_LOG_BYTES: u64 = 20 * 1024 * 1024;
    let now = SystemTime::now();
    let Ok(entries) = fs::read_dir(logs_dir) else {
        return;
    };
    for entry in entries.flatten() {
        let path = entry.path();
        let Ok(meta) = entry.metadata() else {
            continue;
        };
        let stale = meta
            .modified()
            .ok()
            .and_then(|m| now.duration_since(m).ok())
            .map(|age| age > MAX_AGE)
            .unwrap_or(false);
        if stale {
            if meta.is_dir() {
                let _ = fs::remove_dir_all(&path);
            } else {
                let _ = fs::remove_file(&path);
            }
            continue;
        }
        if meta.is_file()
            && meta.len() > MAX_SINGLE_LOG_BYTES
            && path
                .extension()
                .map(|e| e == "log" || e == "jsonl")
                .unwrap_or(false)
        {
            let rotated = path.with_extension("old");
            let _ = fs::remove_file(&rotated);
            let _ = fs::rename(&path, &rotated);
        }
    }
}

pub(crate) fn ledger_init(logs_dir: &Path) {
    let enabled = std::env::var("HOROSA_STARTUP_LEDGER")
        .map(|v| {
            !matches!(
                v.to_ascii_lowercase().as_str(),
                "0" | "false" | "no" | "off"
            )
        })
        .unwrap_or(true);
    if !enabled {
        let _ = STARTUP_LEDGER.set(None);
        return;
    }
    let millis = SystemTime::now()
        .duration_since(SystemTime::UNIX_EPOCH)
        .map(|d| d.as_millis())
        .unwrap_or(0);
    let run_tag = format!("r{}", millis);
    let dir = logs_dir.join(&run_tag);
    let _ = fs::create_dir_all(&dir);
    let file = dir.join("horosa-startup-ledger.jsonl");
    let _ = STARTUP_LEDGER.set(Some((run_tag, file, Instant::now())));
}

pub(crate) fn ledger_mark(seg: &str, extra: Option<serde_json::Value>) {
    ledger_mark_layer_at("rust", seg, None, extra);
}

/// 账本通用写入:layer = rust(壳自身)/ web(前端经 web_ledger_mark_command 上报)。
/// at_epoch_ms 给定时按 run 标签里的 epoch(r<millis>)折算成与 rust.* 同一尺度的 t_ms
/// (页面 Date.now() 与壳 SystemTime 同一墙钟),否则取当前 elapsed。
fn ledger_mark_layer_at(
    layer: &str,
    seg: &str,
    at_epoch_ms: Option<f64>,
    extra: Option<serde_json::Value>,
) {
    let Some(Some((run_tag, file, t0))) = STARTUP_LEDGER.get().map(|v| v.as_ref()).map(|v| v)
    else {
        return;
    };
    let elapsed = t0.elapsed().as_millis();
    let t_ms = at_epoch_ms
        .filter(|at| at.is_finite() && *at > 0.0)
        .and_then(|at| {
            run_tag
                .strip_prefix('r')
                .and_then(|digits| digits.parse::<u128>().ok())
                .map(|run_epoch| (at as i128 - run_epoch as i128).max(0) as u128)
        })
        .unwrap_or(elapsed);
    let mut row = serde_json::json!({
        "run": run_tag,
        "layer": layer,
        "seg": seg,
        "pid": std::process::id(),
        "t_ms": t_ms,
    });
    if let Some(extra) = extra {
        row["extra"] = extra;
    }
    if let Ok(mut fh) = fs::OpenOptions::new().create(true).append(true).open(file) {
        use std::io::Write;
        // 整行一次写出:壳线程与页面上报(IPC 线程池)会同时追加,O_APPEND 只保证单次写原子,
        // writeln! 按格式片段多次写,行内会被别的线程插进来。
        let line = format!("{row}\n");
        let _ = fh.write_all(line.as_bytes());
    }
}

pub(crate) fn ledger_env() -> Option<(String, PathBuf)> {
    STARTUP_LEDGER
        .get()
        .and_then(|v| v.as_ref())
        .map(|(tag, file, _)| (tag.clone(), file.clone()))
}

/// ── 更新进度可视化 v2:全局字节账本 ─────────────────────────────────────────────
/// 一次后台更新一本账(既有设计即单飞),download_update_asset_once 喂块、事件层读
/// 速度(10s 滑窗)/ETA/总量;HOROSA_PROGRESS_V2=0 时退化为老三样(phase/pct/message)。
pub(crate) struct DownloadLedger {
    pub(crate) mode: String,         // "incremental" | "full"
    pub(crate) total_bytes: u64,     // 计划总下载量(0=未知,前端显「大小待定」)
    pub(crate) completed_bytes: u64, // 已完成资产累计
    current_bytes: u64,              // 当前资产已下
    pub(crate) window: std::collections::VecDeque<(Instant, u64)>, // (时刻, 全局已下字节) 10s 滑窗
    pub(crate) component_index: u32,
    pub(crate) component_total: u32,
    pub(crate) component_name: String,
    pub(crate) last_emit: Instant,
    last_emit_bytes: u64,
}

impl DownloadLedger {
    pub(crate) fn new(mode: &str, total_bytes: u64) -> Self {
        Self {
            mode: mode.to_string(),
            total_bytes,
            completed_bytes: 0,
            current_bytes: 0,
            window: std::collections::VecDeque::new(),
            component_index: 0,
            component_total: 0,
            component_name: String::new(),
            last_emit: Instant::now(),
            last_emit_bytes: 0,
        }
    }

    pub(crate) fn downloaded(&self) -> u64 {
        self.completed_bytes + self.current_bytes
    }

    pub(crate) fn on_chunk(&mut self, delta: u64) {
        self.current_bytes += delta;
        let now = Instant::now();
        let total = self.downloaded();
        self.window.push_back((now, total));
        while let Some((t, _)) = self.window.front() {
            if now.duration_since(*t) > Duration::from_secs(10) {
                self.window.pop_front();
            } else {
                break;
            }
        }
    }

    fn finish_asset(&mut self) {
        self.completed_bytes += self.current_bytes;
        self.current_bytes = 0;
    }

    fn speed_bps(&self) -> u64 {
        match (self.window.front(), self.window.back()) {
            (Some((t0, b0)), Some((t1, b1))) if t1 > t0 => {
                let secs = t1.duration_since(*t0).as_secs_f64();
                if secs <= 0.0 {
                    0
                } else {
                    (((*b1 - *b0) as f64) / secs) as u64
                }
            }
            _ => 0,
        }
    }

    pub(crate) fn eta_secs(&self) -> Option<u64> {
        let speed = self.speed_bps();
        if speed == 0 || self.total_bytes == 0 {
            return None;
        }
        let remaining = self.total_bytes.saturating_sub(self.downloaded());
        Some(remaining / speed.max(1))
    }

    /// 节流:≥200ms 且(有明显增量 ≥1MB 或距上次 ≥1s)才 emit,防 window.eval 洪泛。
    fn should_emit(&mut self) -> bool {
        let now = Instant::now();
        let since = now.duration_since(self.last_emit);
        if since < Duration::from_millis(200) {
            return false;
        }
        let grown = self.downloaded().saturating_sub(self.last_emit_bytes);
        if grown < 1_048_576 && since < Duration::from_secs(1) {
            return false;
        }
        self.last_emit = now;
        self.last_emit_bytes = self.downloaded();
        true
    }
}

pub(crate) static UPDATE_LEDGER: Mutex<Option<DownloadLedger>> = Mutex::new(None);

pub(crate) fn progress_v2_enabled() -> bool {
    std::env::var("HOROSA_PROGRESS_V2")
        .map(|v| !matches!(v.as_str(), "0" | "false" | "no" | "off"))
        .unwrap_or(true)
}

pub(crate) fn update_ledger_init(mode: &str, total_bytes: u64) {
    if let Ok(mut slot) = UPDATE_LEDGER.lock() {
        *slot = Some(DownloadLedger::new(mode, total_bytes));
    }
}

pub(crate) fn update_ledger_begin_asset(name: &str, index: u32, total: u32) {
    if let Ok(mut slot) = UPDATE_LEDGER.lock() {
        if let Some(ledger) = slot.as_mut() {
            ledger.component_name = name.to_string();
            ledger.component_index = index;
            ledger.component_total = total;
        }
    }
}

pub(crate) fn update_ledger_finish_asset() {
    if let Ok(mut slot) = UPDATE_LEDGER.lock() {
        if let Some(ledger) = slot.as_mut() {
            ledger.finish_asset();
        }
    }
}

/// 资产下载失败重试前清当前资产字节(半成品作废,账本不虚增)。
pub(crate) fn update_ledger_reset_current() {
    if let Ok(mut slot) = UPDATE_LEDGER.lock() {
        if let Some(ledger) = slot.as_mut() {
            ledger.current_bytes = 0;
            ledger.window.clear();
        }
    }
}

/// 断点续传补入的既有字节:计入进度显示(downloadedBytes),不进速度滑窗(速度不虚高)。
pub(crate) fn update_ledger_note_resumed(bytes: u64) {
    if let Ok(mut slot) = UPDATE_LEDGER.lock() {
        if let Some(ledger) = slot.as_mut() {
            ledger.current_bytes = ledger.current_bytes.saturating_add(bytes);
        }
    }
}

pub(crate) fn update_ledger_clear() {
    if let Ok(mut slot) = UPDATE_LEDGER.lock() {
        *slot = None;
    }
}

/// 喂块并(按节流)返回要合并进 downloading 事件的 v2 字段;v2 关闭/无账本时返回 None。
pub(crate) fn update_ledger_chunk_fields(delta: u64) -> Option<serde_json::Value> {
    if !progress_v2_enabled() {
        return None;
    }
    let mut slot = UPDATE_LEDGER.lock().ok()?;
    let ledger = slot.as_mut()?;
    ledger.on_chunk(delta);
    if !ledger.should_emit() {
        return None;
    }
    let mut fields = serde_json::json!({
        "mode": ledger.mode,
        "downloadedBytes": ledger.downloaded(),
        "speedBps": ledger.speed_bps(),
    });
    if ledger.total_bytes > 0 {
        fields["totalBytes"] = serde_json::json!(ledger.total_bytes);
    }
    if let Some(eta) = ledger.eta_secs() {
        fields["etaSecs"] = serde_json::json!(eta);
    }
    if ledger.component_total > 0 {
        fields["component"] = serde_json::json!(ledger.component_name);
        fields["componentIndex"] = serde_json::json!(ledger.component_index);
        fields["componentTotal"] = serde_json::json!(ledger.component_total);
    }
    Some(fields)
}

pub(crate) fn update_ledger_summary() -> Option<(String, u64)> {
    let slot = UPDATE_LEDGER.lock().ok()?;
    let ledger = slot.as_ref()?;
    Some((ledger.mode.clone(), ledger.downloaded()))
}

/// 「本次需下载 XX MB(增量,复用 YY%)」的计算来源:display-only,真实下载路径照旧自决。
pub(crate) struct UpdateEstimate {
    pub(crate) mode: &'static str,      // "incremental" | "full"
    pub(crate) need_bytes: Option<u64>, // 预计下载量(None=大小待定)
    pub(crate) reuse_pct: Option<u8>,   // 增量复用率(仅 incremental)
    pub(crate) changed_names: Vec<String>,
}

pub(crate) fn compute_update_estimate(
    plan: &UpdatePlan,
    app_should_update: bool,
) -> UpdateEstimate {
    let app_bytes = if app_should_update {
        plan.app_size_bytes
    } else {
        Some(0)
    };
    let roots = vec![shared_runtime_root()];
    if let Some(changed) = plan_component_diff(plan, &roots) {
        let full_runtime: u64 = plan
            .components
            .as_ref()
            .map(|cs| cs.iter().filter_map(|c| c.size).sum())
            .unwrap_or(0);
        let need_runtime: u64 = changed.iter().filter_map(|c| c.size).sum();
        let reuse_pct = if full_runtime > 0 {
            Some((100u64.saturating_sub(need_runtime * 100 / full_runtime)) as u8)
        } else {
            None
        };
        let need_bytes = app_bytes.map(|a| a + need_runtime);
        return UpdateEstimate {
            mode: "incremental",
            need_bytes,
            reuse_pct,
            changed_names: changed.iter().map(|c| c.name.clone()).collect(),
        };
    }
    let need_bytes = match (app_bytes, plan.runtime_size_bytes) {
        (Some(a), Some(r)) => Some(a + r),
        _ => None,
    };
    UpdateEstimate {
        mode: "full",
        need_bytes,
        reuse_pct: None,
        changed_names: Vec::new(),
    }
}
