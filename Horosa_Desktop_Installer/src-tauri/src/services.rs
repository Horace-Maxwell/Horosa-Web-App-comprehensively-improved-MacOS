//! 本机服务起停、身份探针、服务看门狗与前端地址。

use super::*;

// ── 会话中服务自愈(G1)──────────────────────────────────────────────
// 启动看门狗管「起不来」;这里管「跑着跑着死了」:内存压力 jetsam/杀软误杀/误 kill 后,
// 前端身份自愈只会换口找服务、救不活死进程——由壳层探活并限频自动重启;重启后的新端口
// 经 get_backend_endpoints 真值 + 前端 renegotiate(verify-to-switch)闭环,前端零改动。
static BOOTSTRAP_BUSY: AtomicUsize = AtomicUsize::new(0);
static SUPERVISOR_GENERATION: AtomicU64 = AtomicU64::new(0);

/// 启动/修复/更新等「预期内服务不在」的窗口挂本守卫,探活线程静默跳过,防误判抢跑。
pub(crate) struct BootstrapBusyGuard;
impl BootstrapBusyGuard {
    pub(crate) fn hold() -> BootstrapBusyGuard {
        BOOTSTRAP_BUSY.fetch_add(1, Ordering::SeqCst);
        BootstrapBusyGuard
    }
}
impl Drop for BootstrapBusyGuard {
    fn drop(&mut self) {
        BOOTSTRAP_BUSY.fetch_sub(1, Ordering::SeqCst);
    }
}

pub(crate) fn bootstrap_busy() -> bool {
    BOOTSTRAP_BUSY.load(Ordering::SeqCst) > 0
}

pub(crate) fn probe_local_port(port: u16) -> bool {
    std::net::TcpStream::connect_timeout(
        &SocketAddr::from(([127, 0, 0, 1], port)),
        Duration::from_millis(600),
    )
    .is_ok()
}

// 手写 TcpStream HTTP GET /horosaIdentity——不用 reqwest:其默认吃
// HTTP_PROXY/系统代理,本机回环探针会被毒代理劫走出假阴性;TCP 直连天然免疫。
// 四分类:Ok=app 标记+nonce 全对;WrongIdentity=端口上是陌生进程/别的实例(立即判亡);
// HttpSilent=TCP 通但不答/非 JSON(wedged/GC 停顿/毒 200——TCP 探针的盲区,慢判);
// TcpDead=连不上(进程亡,快判)。
#[derive(Debug, Clone, Copy, PartialEq, Eq)]
pub(crate) enum IdentityProbe {
    Ok,
    WrongIdentity,
    HttpSilent,
    TcpDead,
    /// 身份/nonce 全对但「真算探针」失败:软 OOM/线程池被 hang 占满的灰区
    /// ——进程活着、身份线程秒回,业务算力已死。独立慢 streak 判定。
    DeepFail,
    /// 对端 proto<2(旧 runtime 不识 deep 参数):按通过处理,账本一次不误杀。
    DeepUnsupported,
}

pub(crate) fn probe_identity(
    port: u16,
    expect_app: &str,
    expect_nonce: &str,
    timeout: Duration,
    deep: bool,
) -> IdentityProbe {
    use std::io::{Read, Write};
    let addr = SocketAddr::from(([127, 0, 0, 1], port));
    let Ok(mut stream) = std::net::TcpStream::connect_timeout(&addr, timeout) else {
        return IdentityProbe::TcpDead;
    };
    let _ = stream.set_read_timeout(Some(timeout));
    let _ = stream.set_write_timeout(Some(timeout));
    // deep=1:服务端在身份响应里附带一次微型真算结果(deep:"ok"/"fail")——
    // 探「还能算」,非仅「身份线程活着」。仅 proto>=2 的对端支持;旧对端由 proto 门兜底。
    let path = if deep {
        "/horosaIdentity?deep=1"
    } else {
        "/horosaIdentity"
    };
    let request = format!(
        "GET {path} HTTP/1.1\r\nHost: 127.0.0.1:{port}\r\nConnection: close\r\nAccept: application/json\r\n\r\n"
    );
    if stream.write_all(request.as_bytes()).is_err() {
        return IdentityProbe::HttpSilent;
    }
    let mut raw = Vec::new();
    let mut buf = [0u8; 4096];
    loop {
        match stream.read(&mut buf) {
            Ok(0) => break,
            Ok(n) => {
                raw.extend_from_slice(&buf[..n]);
                // 有界读:身份响应是单行小 JSON,64KB 上限防陌生进程灌流
                if raw.len() > 64 * 1024 {
                    break;
                }
            }
            Err(_) => break,
        }
    }
    if raw.is_empty() {
        return IdentityProbe::HttpSilent;
    }
    let text = String::from_utf8_lossy(&raw);
    let Some(body_at) = text.find("\r\n\r\n") else {
        return IdentityProbe::HttpSilent;
    };
    let body = &text[body_at + 4..];
    // chunked 兜底:取首个 { 到末个 }(身份响应为单个小 JSON 对象)
    let json_slice = match (body.find('{'), body.rfind('}')) {
        (Some(s), Some(e)) if e >= s => &body[s..=e],
        _ => return IdentityProbe::HttpSilent,
    };
    let Ok(json) = serde_json::from_str::<serde_json::Value>(json_slice) else {
        return IdentityProbe::HttpSilent;
    };
    let app_tag = json.get("app").and_then(|v| v.as_str()).unwrap_or("");
    let nonce = json.get("nonce").and_then(|v| v.as_str()).unwrap_or("");
    if app_tag != expect_app {
        return IdentityProbe::WrongIdentity;
    }
    if !expect_nonce.is_empty() && nonce != expect_nonce {
        return IdentityProbe::WrongIdentity;
    }
    if deep {
        // proto 门(代数差免疫):旧 runtime(proto<2 或无 proto)不识 deep → 按通过,
        // 由调用方账本一次;proto>=2 必须回 deep 字段且为 "ok"。
        let proto = json.get("proto").and_then(|v| v.as_u64()).unwrap_or(1);
        if proto < 2 {
            return IdentityProbe::DeepUnsupported;
        }
        let deep_status = json.get("deep").and_then(|v| v.as_str()).unwrap_or("fail");
        if deep_status != "ok" {
            return IdentityProbe::DeepFail;
        }
    }
    IdentityProbe::Ok
}

// 双 streak 判亡状态机(纯函数可测):TcpDead 快判(连续 2 轮=40s),HttpSilent
// 慢判(连续 6 轮=2min,容 GC 停顿/瞬时高载),WrongIdentity 立即判亡,Ok 全清零。
#[derive(Debug, Clone, Copy, Default, PartialEq, Eq)]
pub(crate) struct SupervisorStreak {
    pub(crate) dead: u32,
    pub(crate) silent: u32,
}
const SUPERVISOR_DEAD_ROUNDS: u32 = 2;
const SUPERVISOR_SILENT_ROUNDS: u32 = 6;

pub(crate) fn supervisor_step(
    streak: SupervisorStreak,
    probe: IdentityProbe,
) -> (SupervisorStreak, bool) {
    match probe {
        IdentityProbe::Ok => (SupervisorStreak::default(), false),
        // DeepFail=身份活着(浅层健康)→ 浅 streak 清零,由 deep_step 独立判;
        // DeepUnsupported=旧对端,等同 Ok。
        IdentityProbe::DeepFail | IdentityProbe::DeepUnsupported => {
            (SupervisorStreak::default(), false)
        }
        IdentityProbe::WrongIdentity => (SupervisorStreak::default(), true),
        IdentityProbe::TcpDead => {
            let next = SupervisorStreak {
                dead: streak.dead + 1,
                silent: 0,
            };
            (next, next.dead >= SUPERVISOR_DEAD_ROUNDS)
        }
        IdentityProbe::HttpSilent => {
            let next = SupervisorStreak {
                dead: 0,
                silent: streak.silent + 1,
            };
            (next, next.silent >= SUPERVISOR_SILENT_ROUNDS)
        }
    }
}

// 深探慢 streak(纯函数可测):连续 SUPERVISOR_DEEP_FAIL_ROUNDS 次深探失败
// (每 SUPERVISOR_DEEP_EVERY_ROUNDS 轮才发一次深探,即 ≈2×5min)才判「算力死」——
// 容忍单次高载/GC 长停顿;Ok 清零。
const SUPERVISOR_DEEP_EVERY_ROUNDS: u64 = 15;
const SUPERVISOR_DEEP_FAIL_ROUNDS: u32 = 2;

pub(crate) fn deep_step(streak: u32, deep_ok: bool) -> (u32, bool) {
    if deep_ok {
        (0, false)
    } else {
        let next = streak + 1;
        (next, next >= SUPERVISOR_DEEP_FAIL_ROUNDS)
    }
}

fn deep_probe_enabled() -> bool {
    std::env::var("HOROSA_DEEP_PROBE")
        .map(|v| v != "0")
        .unwrap_or(true)
}

fn deep_probe_every_rounds() -> u64 {
    std::env::var("HOROSA_DEEP_PROBE_EVERY")
        .ok()
        .and_then(|v| v.parse().ok())
        .filter(|v| *v > 0)
        .unwrap_or(SUPERVISOR_DEEP_EVERY_ROUNDS)
}

// 服务监督事件通道(镜像 __horosaPending* 模式;老前端无 handler=无害)
/// 自动备份 tick 投递(壳→页面 eval 回调范式;页面未就绪先入 pending 队列)。返回是否找到主窗口。
pub(crate) fn dispatch_auto_backup_tick(app: &AppHandle, seq: u64) -> bool {
    let Some(window) = app.get_webview_window(MAIN_WINDOW_LABEL) else {
        return false;
    };
    let payload = serde_json::json!({ "seq": seq, "at": std::time::SystemTime::now().duration_since(std::time::UNIX_EPOCH).map(|d| d.as_secs()).unwrap_or(0) });
    let script = auto_backup_tick_script(&payload.to_string());
    let _ = window.eval(&script);
    ledger_mark("rust.auto_backup_tick", Some(payload));
    true
}

/// 纯函数(可单测):生成投递脚本——有回调即调,无回调入队(队列上限 8,防页面长期未绑无限增长)。
pub(crate) fn auto_backup_tick_script(payload_json: &str) -> String {
    format!(
        "(function(){{var t={payload_json};if(typeof window.__horosaAutoBackupTick==='function'){{try{{window.__horosaAutoBackupTick(t);}}catch(e){{}}}}else{{var q=window.__horosaPendingAutoBackupTicks=window.__horosaPendingAutoBackupTicks||[];q.push(t);if(q.length>8){{q.splice(0,q.length-8);}}}}}})();"
    )
}

/// 应用上下文唯一构造点:`generate_context!` 内嵌 `_EMBED_INFO_PLIST` 链接段静态量,同一 crate 展开两次=重复符号
/// (测试里要用 MockRuntime 复用同一份 tauri.conf.json/ACL,故做成泛型函数由 main 与测试各自实例化)。
pub(crate) fn build_app_context<R: tauri::Runtime>() -> tauri::Context<R> {
    tauri::generate_context!()
}

fn emit_service_event(app: &AppHandle, json: &str) {
    if let Some(window) = app.get_webview_window(MAIN_WINDOW_LABEL) {
        let _ = window.eval(&format!(
            "window.__horosaPendingServiceEvent = {json}; \
if (window.__horosaServiceEvent) {{ window.__horosaServiceEvent({json}); }}"
        ));
    }
}

pub(crate) fn current_session_snapshot(app: &AppHandle) -> Option<RuntimeSession> {
    let state = app.try_state::<AppState>()?;
    let slot = state.session.lock().ok()?;
    slot.clone()
}

/// 菜单/探活看门狗共用的本地服务重启:停旧(带真实端口)→ 新端口全链拉起 → 会话真值更新。
// 失败定因包装:重启失败时做一次关键目录写测,PermissionDenied → 人话上浮
// (错误沿既有通道进对话框/账本,用户直接看到「哪个目录权限坏」而非泛化失败)。
pub(crate) fn restart_local_services(app: &AppHandle, origin: &str) -> Result<()> {
    let result = restart_local_services_inner(app, origin);
    if result.is_err() {
        if let Some(session) = current_session_snapshot(app) {
            if let Some(hint) = classify_permission_issue(&session.paths) {
                ledger_mark(
                    "rust.permission_probe_failed",
                    Some(serde_json::json!({ "hint": hint })),
                );
                return result.context(hint);
            }
        }
    }
    result
}

fn restart_local_services_inner(app: &AppHandle, origin: &str) -> Result<()> {
    if bootstrap_busy() {
        return Err(anyhow!("启动/修复/更新流程正在进行,请稍候片刻再试"));
    }
    let _busy = BootstrapBusyGuard::hold();
    let window = app
        .get_webview_window(MAIN_WINDOW_LABEL)
        .context("主窗口不可用")?;
    let session =
        current_session_snapshot(app).context("本地服务会话尚未建立(应用可能仍在启动中)")?;
    ledger_mark("rust.services_restart_begin", None);
    stop_runtime(
        &session.paths,
        Some((session.backend_port, session.chart_port)),
    );
    thread::sleep(Duration::from_millis(300));
    let mut backend_port = choose_free_port()?;
    let mut chart_port = choose_free_port()?;
    start_runtime_with_port_retry(
        &session.paths,
        &window,
        &mut backend_port,
        &mut chart_port,
        None,
        true,
        true,
        true,
    )?;
    if let Some(state) = app.try_state::<AppState>() {
        if let Ok(mut slot) = state.session.lock() {
            *slot = Some(RuntimeSession {
                paths: session.paths.clone(),
                backend_port,
                chart_port,
                web_port: session.web_port,
            });
        }
    }
    // 重启换口后同步 panic 停服补给,防崩溃路径按旧口杀空。
    set_panic_stop_ports(backend_port, chart_port, session.web_port);
    ledger_mark("rust.services_restarted", None);
    // 低打扰告知(信息横幅,可关闭):软 OOM 转硬死后自动拉起时,用户当次排盘
    // 会失败一次——明说「已自动恢复」,不留悬念。老前端无 handler=无害。
    emit_service_event(
        app,
        &serde_json::json!({
            "kind": "runtime_updated_elsewhere",
            "message": "本地计算服务已自动恢复。若刚才有操作失败,重试即可。",
        })
        .to_string(),
    );
    eprintln!("local services restarted via {origin}: backend={backend_port} chart={chart_port}");
    Ok(())
}

/// 探活看门狗(深度化):ready 后每 20s 对双后端做 /horosaIdentity 深探
/// (probe_identity 四分类;TCP 探针只能看到「端口在听」,对 wedged/GC 死循环/陌生进程
/// squat 全盲——历史事故 的看门狗侧闭环)。TcpDead 连续 2 轮/HttpSilent 连续
/// 6 轮/WrongIdentity 立即 → 自动重启(30 分钟窗 ≤2 次,防坏环境重启风暴);
/// 超限单次闩锁:账本一行+emit supervisor_gave_up 事件(前端横幅显式化,不再静默)。
/// web 静态服务器一并纳管(TCP 探,不通连续 2 轮原地重建,独立限频)。
/// generation 令牌:每次 ready 换代,旧线程自退,不叠加。
// 磁盘水位闩(纯函数可测):低于阈值→触发一次(闩住不刷屏);回升到阈值×2 才解闩
// (防抖:在阈值附近抖动不会反复弹);读不到(卷异常)不动作。返回 (下一闩态, 本轮是否触发)。
pub(crate) fn disk_low_step(
    latched: bool,
    avail_bytes: Option<u64>,
    min_bytes: u64,
) -> (bool, bool) {
    match avail_bytes {
        None => (latched, false),
        Some(avail) => {
            if !latched && avail < min_bytes {
                (true, true)
            } else if latched && avail >= min_bytes.saturating_mul(2) {
                (false, false)
            } else {
                (latched, false)
            }
        }
    }
}

fn disk_watch_enabled() -> bool {
    std::env::var("HOROSA_DISK_WATCH")
        .map(|v| v != "0")
        .unwrap_or(true)
}

fn disk_min_bytes() -> u64 {
    std::env::var("HOROSA_DISK_MIN_MB")
        .ok()
        .and_then(|v| v.parse::<u64>().ok())
        .filter(|v| *v > 0)
        .unwrap_or(500)
        .saturating_mul(1024 * 1024)
}

// 权限自检:关键目录写测(临时探针文件)。PermissionDenied → 人话定因
// (此前权限坏只会泛化成启动失败/500,用户与排障者都无从下手)。其它错误不定因。
pub(crate) fn classify_permission_issue(paths: &RuntimePaths) -> Option<String> {
    for dir in [&paths.app_data_dir, &paths.logs_dir, &paths.runtime_dir] {
        let probe = dir.join(".horosa-perm-probe");
        match fs::write(&probe, b"x") {
            Ok(_) => {
                let _ = fs::remove_file(&probe);
            }
            Err(err) if err.kind() == std::io::ErrorKind::PermissionDenied => {
                return Some(format!(
                    "目录权限异常:{} 不可写。可尝试菜单「重装运行时」修复;公司管控机请联系管理员放开该目录。",
                    dir.display()
                ));
            }
            Err(_) => {}
        }
    }
    None
}

// 多实例更新感知纯函数:基线未定→以首见版本为基线;已定且磁盘版本不同→触发一次。
// (renamex 换 inode 后本实例仍跑旧树:探针恒 Ok,只有 manifest 版本对比能看见「别人更新了」。)
pub(crate) fn runtime_change_step(
    baseline: Option<String>,
    disk: Option<String>,
) -> (Option<String>, bool) {
    match (baseline, disk) {
        (None, Some(v)) => (Some(v), false),
        (Some(b), Some(now)) => {
            let changed = b != now;
            (Some(b), changed)
        }
        (b, None) => (b, false),
    }
}

pub(crate) fn start_service_supervisor(app: AppHandle) {
    let my_gen = SUPERVISOR_GENERATION.fetch_add(1, Ordering::SeqCst) + 1;
    thread::spawn(move || {
        let mut backend_streak = SupervisorStreak::default();
        let mut chart_streak = SupervisorStreak::default();
        let mut web_down = 0u32;
        let mut recent_restarts: Vec<Instant> = Vec::new();
        let mut recent_web_restarts: Vec<Instant> = Vec::new();
        let mut gave_up_latched = false;
        let mut round: u64 = 0;
        let mut boot_runtime_version: Option<String> = None;
        let mut runtime_changed_notified = false;
        let mut backend_deep_streak = 0u32;
        let mut chart_deep_streak = 0u32;
        let mut deep_unsupported_noted = false;
        let mut disk_low_latched = false;
        loop {
            thread::sleep(Duration::from_secs(20));
            if SUPERVISOR_GENERATION.load(Ordering::SeqCst) != my_gen {
                return;
            }
            if bootstrap_busy() {
                backend_streak = SupervisorStreak::default();
                chart_streak = SupervisorStreak::default();
                web_down = 0;
                continue;
            }
            let Some(session) = current_session_snapshot(&app) else {
                backend_streak = SupervisorStreak::default();
                chart_streak = SupervisorStreak::default();
                web_down = 0;
                continue;
            };
            round = round.wrapping_add(1);
            // 磁盘水位自感知(每 15 轮 ≈5min,statfs 零成本):写满盘是排盘 500/
            // 更新失败/日志丢失的共因,此前运行期零检测。跌破阈值一次性横幅告知;
            // 回升到 2× 阈值自动解闩(此后再跌破会再次提醒)。
            if disk_watch_enabled() && round % 15 == 0 {
                let avail = [
                    available_disk_bytes(&session.paths.app_data_dir),
                    available_disk_bytes(&session.paths.runtime_dir),
                ]
                .into_iter()
                .flatten()
                .min();
                let (next_latch, fire) = disk_low_step(disk_low_latched, avail, disk_min_bytes());
                disk_low_latched = next_latch;
                if fire {
                    ledger_mark(
                        "rust.disk_low",
                        Some(serde_json::json!({
                            "availBytes": avail.unwrap_or(0),
                        })),
                    );
                    emit_service_event(
                        &app,
                        &serde_json::json!({
                            "kind": "disk_low",
                            "message": "磁盘可用空间不足,可能影响排盘、日志与自动更新——请清理磁盘后继续使用。",
                        })
                        .to_string(),
                    );
                }
            }
            // 多实例感知:另一实例(可能是本机其他用户)更新共享 runtime 后,
            // 本实例仍持旧 inode 且探针恒 Ok → 每 15 轮(≈5min)比对 manifest 版本,
            // 变化即一次性提示(闩锁,不刷屏)。基线取首轮读到的版本。
            if !runtime_changed_notified {
                if boot_runtime_version.is_none() || round % 15 == 0 {
                    let disk_version =
                        read_runtime_manifest_from_path(&session.paths.manifest_path)
                            .map(|m| m.version);
                    let (next_baseline, changed) =
                        runtime_change_step(boot_runtime_version.take(), disk_version);
                    boot_runtime_version = next_baseline;
                    if changed {
                        runtime_changed_notified = true;
                        ledger_mark(
                            "rust.runtime_updated_elsewhere",
                            Some(serde_json::json!({
                                "baseline": boot_runtime_version.clone().unwrap_or_default(),
                            })),
                        );
                        emit_service_event(
                            &app,
                            &serde_json::json!({
                                "kind": "runtime_updated_elsewhere",
                                "message": "本机组件已在另一会话中完成更新(可能来自本机其他用户)。重启星阙后即可使用新版本。",
                            })
                            .to_string(),
                        );
                    }
                }
            }
            // web 静态服务器监督:tiny_http 线程死=整个 UI 白屏,且此前无任何看门狗。
            // 线程 panic 即 drop Server 即释放端口 → 同端口原地重建可行。
            if probe_local_port(session.web_port) {
                web_down = 0;
            } else {
                web_down += 1;
                if web_down >= 2 {
                    web_down = 0;
                    recent_web_restarts.retain(|t| t.elapsed() < Duration::from_secs(1800));
                    if recent_web_restarts.len() < 3 {
                        recent_web_restarts.push(Instant::now());
                        let shutdown = Arc::new(AtomicBool::new(false));
                        match start_static_server(
                            session.paths.frontend_dir.clone(),
                            session.web_port,
                            shutdown.clone(),
                        ) {
                            Ok(_handle) => {
                                if let Some(state) = app.try_state::<AppState>() {
                                    replace_web_shutdown(&state.web_shutdown, Some(shutdown));
                                }
                                ledger_mark("rust.web_server_restarted", None);
                            }
                            Err(err) => {
                                eprintln!("[supervisor] web 静态服务器重建失败: {err:#}")
                            }
                        }
                    }
                }
            }
            let nonce = launch_nonce();
            let probe_timeout = Duration::from_millis(1500);
            // 每 N 轮(默认 15≈5min)把浅探升级为深探(真算维度):
            // 软 OOM/线程池部分 wedge 时身份端点仍秒回 Ok,只有真算探针能看见。
            let deep_round = deep_probe_enabled() && round % deep_probe_every_rounds() == 0;
            let backend_probe = probe_identity(
                session.backend_port,
                "horosa-backend",
                nonce,
                probe_timeout,
                deep_round,
            );
            let chart_probe = probe_identity(
                session.chart_port,
                "horosa-chart",
                nonce,
                probe_timeout,
                deep_round,
            );
            if deep_round
                && !deep_unsupported_noted
                && (backend_probe == IdentityProbe::DeepUnsupported
                    || chart_probe == IdentityProbe::DeepUnsupported)
            {
                deep_unsupported_noted = true;
                ledger_mark("rust.deep_probe_unsupported", None);
            }
            let (bs, backend_dead) = supervisor_step(backend_streak, backend_probe);
            backend_streak = bs;
            let (cs, chart_dead) = supervisor_step(chart_streak, chart_probe);
            chart_streak = cs;
            // 深探独立慢 streak(仅深探轮推进)
            let mut deep_dead = false;
            if deep_round {
                let (bds, bd) = deep_step(
                    backend_deep_streak,
                    backend_probe != IdentityProbe::DeepFail,
                );
                backend_deep_streak = bds;
                let (cds, cd) =
                    deep_step(chart_deep_streak, chart_probe != IdentityProbe::DeepFail);
                chart_deep_streak = cds;
                if bd || cd {
                    deep_dead = true;
                    ledger_mark(
                        "rust.deep_probe_fail",
                        Some(serde_json::json!({
                            "backendStreak": backend_deep_streak,
                            "chartStreak": chart_deep_streak,
                        })),
                    );
                }
            }
            let backend_healthy = matches!(
                backend_probe,
                IdentityProbe::Ok | IdentityProbe::DeepUnsupported
            );
            let chart_healthy = matches!(
                chart_probe,
                IdentityProbe::Ok | IdentityProbe::DeepUnsupported
            );
            if backend_healthy && chart_healthy && !deep_dead {
                // 全健康:解除 gave_up 闩锁(人工重启成功后允许未来再次自动修复+提示)
                gave_up_latched = false;
                continue;
            }
            if !(backend_dead || chart_dead || deep_dead) {
                continue;
            }
            backend_streak = SupervisorStreak::default();
            chart_streak = SupervisorStreak::default();
            backend_deep_streak = 0;
            chart_deep_streak = 0;
            recent_restarts.retain(|t| t.elapsed() < Duration::from_secs(1800));
            if recent_restarts.len() >= 2 {
                // 越限:单次闩锁——账本一行(不再每 20s 刷屏)+显式事件交前端横幅
                if !gave_up_latched {
                    gave_up_latched = true;
                    ledger_mark("rust.supervisor_gave_up", None);
                    emit_service_event(
                        &app,
                        &serde_json::json!({
                            "kind": "supervisor_gave_up",
                            "message": "本地服务多次自动重启未果，已暂停自动修复。可点「重启服务」手动重启，或打开诊断中心查看原因。",
                        })
                        .to_string(),
                    );
                }
                continue;
            }
            recent_restarts.push(Instant::now());
            ledger_mark(
                "rust.supervisor_auto_restart",
                Some(serde_json::json!({
                    "backendProbe": format!("{:?}", backend_probe),
                    "chartProbe": format!("{:?}", chart_probe),
                    "reason": if deep_dead && !(backend_dead || chart_dead) {
                        "deep_probe"
                    } else {
                        "identity_probe"
                    },
                })),
            );
            if let Err(err) = restart_local_services(&app, "supervisor") {
                eprintln!("supervisor auto-restart failed: {err:#}");
            }
        }
    });
}

// 轻量服务重启命令(前端横幅「重启服务」用;此前横幅错线到
// trigger_runtime_repair_command=全量修复流,对「服务死了」场景过重)。
#[tauri::command]
pub(crate) fn restart_local_services_command(app: AppHandle) -> std::result::Result<(), String> {
    restart_local_services(&app, "frontend").map_err(|err| format!("{err:#}"))
}

/// start / stop 脚本放 pid 文件的目录(与两个脚本里 [pid-dir:begin]…[pid-dir:end] 段同一规则,cargo 用例逐字对拍):
/// HOROSA_PID_DIR 给了就用它;脚本所在目录可写(单账户机 / 安装者本人)就放那里;
/// 只读(多账户机上的其他账户加载共享运行环境)落到 ~/Library/Caches/horosa-run/<目录路径把 / 换成 _>。
pub(crate) fn runtime_pid_dir_for(
    web_dir: &Path,
    home: &str,
    override_dir: Option<&str>,
    web_dir_writable: bool,
) -> PathBuf {
    if let Some(dir) = override_dir.filter(|d| !d.is_empty()) {
        return PathBuf::from(dir);
    }
    if web_dir_writable {
        return web_dir.to_path_buf();
    }
    let key = web_dir.to_string_lossy().replace('/', "_");
    PathBuf::from(home)
        .join("Library/Caches/horosa-run")
        .join(key)
}

fn runtime_pid_dir(web_dir: &Path) -> PathBuf {
    let home = std::env::var("HOME")
        .ok()
        .filter(|v| !v.is_empty())
        .or_else(|| std::env::var("TMPDIR").ok().filter(|v| !v.is_empty()))
        .unwrap_or_else(|| "/tmp".to_string());
    let override_dir = std::env::var("HOROSA_PID_DIR").ok();
    runtime_pid_dir_for(
        web_dir,
        &home,
        override_dir.as_deref(),
        path_writable_by_current_user(web_dir),
    )
}

pub(crate) fn stop_runtime(paths: &RuntimePaths, ports: Option<(u16, u16)>) {
    if !paths.stop_script.exists() {
        return;
    }
    let mut command = Command::new("/bin/bash");
    command
        .arg(&paths.stop_script)
        .current_dir(paths.runtime_dir.join("Horosa-Web"))
        .stdout(Stdio::null())
        .stderr(Stdio::null());
    // 会话真实端口交给脚本(与 stop_runtime_detached 同款):pid 文件按端口后缀定位、
    // 端口兜底扫描打到真端口——不传则脚本只会看默认口 8899/9999,动态选口的会话
    // 停不干净(半启动服务在重试路径上泄漏)。
    if let Some((backend_port, chart_port)) = ports {
        command
            .env("HOROSA_SERVER_PORT", backend_port.to_string())
            .env("HOROSA_CHART_PORT", chart_port.to_string());
    }
    let _ = command.status();
}

pub(crate) fn start_runtime(
    paths: &RuntimePaths,
    window: &WebviewWindow,
    backend_port: u16,
    chart_port: u16,
    startup_timeout_secs: Option<u64>,
    skip_runtime_warmup: bool,
    skip_mongo_ping: bool,
    trusted_runtime: bool,
) -> Result<()> {
    // 进度前置:下方预清理/预停止在冷文件系统缓存下可耗时数秒,先把进度从 36 推到 82
    // (indeterminate 动画),否则 UI 冻在 36% 被当成卡死(用户实告)。
    emit_indeterminate_progress(window, 82, "正在准备启动环境…");
    ensure_dir(&paths.logs_dir)?;
    // trusted 快路径跳过全树元数据清理:cleanup_runtime_metadata 递归遍历整棵 runtime 树
    // (数万文件),冷缓存下可达数十秒;而解压末尾(extract_runtime_archive)与健康缓存 miss
    // 慢路径(runtime_dir_is_usable)都已各清过一次,trusted 启动时纯冗余。启动成功后另有
    // 后台 mop-up 兜底(runtime_bootstrap 尾部);fast-path 失败的回退分支以 trusted=false
    // 重启 → 清理照跑,自愈链完整。
    if !trusted_runtime {
        prepare_runtime_dir(&paths.runtime_dir)?;
    }
    // 启动期 stop 条件跳过:choose_free_port 已证两口可绑,stop 在常态下是
    // 「pid 文件不存在 → 脚本空跑」的纯 no-op 固定税(bash spawn + 三并行 stop + netstat
    // ≈50-150ms)。预检对齐 stop 脚本的兜底扫描语义(通配 .horosa_{py,java,web}.*.pid ——
    // 任一 stale pid 在 → 照旧同步跑,回收覆盖零损失)。孤儿回收另有四道(退出停服/panic
    // 真端口/看门狗/postinstall sweep),本预检只省「明确无可回收」的那次 spawn;
    // 零残留铁律不涉——这是启动期预清理,不是退出路径。HOROSA_START_STOP_PRECHECK=0 关。
    let prestop_skip = std::env::var("HOROSA_START_STOP_PRECHECK")
        .map(|v| v != "0")
        .unwrap_or(true)
        && {
            // pid 文件所在目录与 start / stop 脚本同一规则(运行环境只读的账户落到自己的缓存目录)
            let web_dir = paths.runtime_dir.join("Horosa-Web");
            let pid_dir = runtime_pid_dir(&web_dir);
            let has_stale_pid = match fs::read_dir(&pid_dir) {
                Ok(it) => it
                    .filter_map(|e| e.ok())
                    .filter_map(|e| e.file_name().to_str().map(|s| s.to_string()))
                    .any(|n| {
                        n.ends_with(".pid")
                            && (n.starts_with(".horosa_py.")
                                || n.starts_with(".horosa_java.")
                                || n.starts_with(".horosa_web."))
                    }),
                // 缓存目录还没建过 = 本账户从没在这份运行环境上起过服务,没有残留
                Err(err) if err.kind() == std::io::ErrorKind::NotFound && pid_dir != web_dir => {
                    false
                }
                Err(_) => true, // 目录读不了 → 保守判「可能有残留」照旧跑 stop
            };
            !has_stale_pid
        };
    if prestop_skip {
        ledger_mark("rust.prestop_done", Some(serde_json::json!({"skipped": 1})));
    } else {
        stop_runtime(paths, Some((backend_port, chart_port)));
        ledger_mark("rust.prestop_done", Some(serde_json::json!({"skipped": 0})));
    }
    emit_status(window, "正在后台启动 星阙 Python / Java 服务…");
    if trusted_runtime {
        emit_indeterminate_progress(window, 82, "正在后台启动本地服务,通常需 10~20 秒…");
    } else {
        // 首启/更新后走完整校验:冷 JVM + 首次预热在低速机上真实需要分钟级,
        // 预期管理到位,用户才不会当成卡死而强退(强退两次会触发看门狗回滚)。
        emit_indeterminate_progress(
            window,
            82,
            "首次(或更新后)启动正在完整校验并预热本地计算引擎,约需 1~2 分钟,请保持窗口打开…",
        );
    }

    let python_bin = runtime_python_bin(&paths.runtime_dir);
    let java_bin = paths.runtime_dir.join("runtime/mac/java/bin/java");
    let mut command = Command::new("/bin/bash");
    command
        .arg(&paths.start_script)
        .current_dir(paths.runtime_dir.join("Horosa-Web"))
        .env("HOROSA_SKIP_UI_BUILD", "1")
        .env("HOROSA_REQUIRE_EMBEDDED_RUNTIME", "1")
        .env("HOROSA_PYTHON", python_bin)
        .env("HOROSA_JAVA_BIN", java_bin)
        .env("HOROSA_SERVER_PORT", backend_port.to_string())
        .env("HOROSA_CHART_PORT", chart_port.to_string())
        // 启动会话 nonce:经 start 脚本环境继承进 Java/Python,被 /horosaIdentity 原样回显,
        // 前端据此确认「这个端口上的确是本会话拉起的后端」(防端口squat/跨实例串线)。
        .env("HOROSA_LAUNCH_NONCE", launch_nonce())
        // GUI(LaunchServices)拉起的进程通常无 locale——非 ASCII(中文用户名)
        // home 路径在 JVM/子进程里有编解码风险;仅缺失时兜底,不覆盖用户显式设置。
        .env(
            "LANG",
            std::env::var("LANG").unwrap_or_else(|_| "zh_CN.UTF-8".to_string()),
        )
        .env(
            "HOROSA_SKIP_RUNTIME_WARMUP",
            if skip_runtime_warmup { "1" } else { "0" },
        )
        .env(
            "HOROSA_DESKTOP_MONGO_SKIP_PING",
            if skip_mongo_ping { "1" } else { "0" },
        )
        .env(
            "HOROSA_TRUSTED_RUNTIME",
            if trusted_runtime { "1" } else { "0" },
        )
        .env(
            "HOROSA_LOG_ROOT",
            paths.logs_dir.to_string_lossy().to_string(),
        )
        .env(
            "HOROSA_DIAG_DIR",
            paths.logs_dir.to_string_lossy().to_string(),
        )
        // 本地文档缓存每用户独立(app_data_dir 下):共享树无锁 JSON 多用户并发会互踩。
        .env(
            "HOROSA_MONGO_FALLBACK_DIR",
            paths
                .logs_dir
                .parent()
                .unwrap_or(&paths.logs_dir)
                .join("mongo-fallback")
                .to_string_lossy()
                .to_string(),
        );
    // 启动账本:把 run 标签与账本文件传给脚本层(shell 再传 Java/Python),四层同文件聚合。
    if let Some((run_tag, ledger_file)) = ledger_env() {
        command.env("HOROSA_RUN_TAG", run_tag).env(
            "HOROSA_LEDGER_FILE",
            ledger_file.to_string_lossy().to_string(),
        );
    }
    // 本地回环探测防代理劫持(双保险,脚本侧 curl --noproxy / urllib 禁代理是第一道):
    // 用户 shell/launchctl 注入的代理变量会把脚本内 127.0.0.1 探测与热身请求劫持进代理 →
    // 服务在听也探不到 → 首启永不就绪。spawn 前显式剥掉六个代理变量。
    for proxy_var in [
        "http_proxy",
        "https_proxy",
        "all_proxy",
        "HTTP_PROXY",
        "HTTPS_PROXY",
        "ALL_PROXY",
    ] {
        command.env_remove(proxy_var);
    }
    if let Some(timeout_secs) = startup_timeout_secs {
        command.env("HOROSA_STARTUP_TIMEOUT", timeout_secs.to_string());
    } else if !trusted_runtime {
        // 全新安装首启(untrusted)预算放宽:含 324MB jar 首次拷贝 + JVM 冷启 + 杀软扫描,
        // 慢盘机器 180s 临界(与脚本侧 untrusted 默认 300 对齐,这里显式传以防脚本默认被改)。
        command.env("HOROSA_STARTUP_TIMEOUT", "300");
    }
    // 心跳:output() 阻塞等脚本(就绪轮询通常 5~20s,冷启更久),每秒刷一次 indeterminate
    // 文案让进度条保持活动,避免长等待被当成卡死。错误路径同样先置停+join 再返回。
    // WS-1c 细分:借启动账本的 sh.py_http_ready / sh.java_http_ready 打点,
    // 把整段等待拆成「排盘引擎已就绪(1/2)→主服务已就绪(2/2)」两阶段可见。
    let heartbeat_stop = Arc::new(AtomicBool::new(false));
    let heartbeat = {
        let window = window.clone();
        let stop = heartbeat_stop.clone();
        let ledger_file = STARTUP_LEDGER
            .get()
            .and_then(|v| v.as_ref())
            .map(|(_, file, _)| file.clone());
        thread::spawn(move || {
            let started = Instant::now();
            loop {
                // 停止旗标 10ms 粒度:脚本一返回,output() 之后的 join() 最多再等 10ms
                //(原 100ms 粒度 = 每次温启在就绪之后白等 0~100ms 才发 ready)。文案仍每秒刷一次。
                for _ in 0..100 {
                    thread::sleep(Duration::from_millis(10));
                    if stop.load(Ordering::Relaxed) {
                        return;
                    }
                }
                // 账本按 run 独立文件,读到什么段就是本次的(吞错:账本不可用退回笼统文案)
                let ledger_text = ledger_file
                    .as_ref()
                    .and_then(|f| fs::read_to_string(f).ok())
                    .unwrap_or_default();
                let stage = if ledger_text.contains("\"seg\":\"sh.java_http_ready\"") {
                    2u8
                } else if ledger_text.contains("\"seg\":\"sh.py_http_ready\"") {
                    1u8
                } else {
                    0u8
                };
                // progress-aware 续命可视:脚本侧账本出现 sh.ready_extend =
                // 预算已耗尽但检测到持续进展,正在自动延长——明说,防慢机用户当卡死强退。
                let extend_note = if ledger_text.contains("\"seg\":\"sh.ready_extend\"") {
                    "(检测到持续进展,已自动延长等待)"
                } else {
                    ""
                };
                let message = match stage {
                    2 => format!(
                        "主服务已就绪(2/2),正在完成收尾…已等待 {} 秒{extend_note}",
                        started.elapsed().as_secs()
                    ),
                    1 => format!(
                        "排盘引擎已就绪(1/2),正在启动主服务…已等待 {} 秒{extend_note}",
                        started.elapsed().as_secs()
                    ),
                    _ => format!(
                        "正在启动本地服务…已等待 {} 秒{extend_note}",
                        started.elapsed().as_secs()
                    ),
                };
                emit_indeterminate_progress(&window, 82, &message);
            }
        })
    };
    ledger_mark("rust.script_spawn", None);
    let output_result = command.output().context("launch start_horosa_local.sh");
    heartbeat_stop.store(true, Ordering::Relaxed);
    let _ = heartbeat.join();
    let output = output_result?;
    ledger_mark(
        "rust.script_returned",
        Some(serde_json::json!({"exit": output.status.code().unwrap_or(-1)})),
    );
    if !output.status.success() {
        let code = output.status.code().unwrap_or(-1);
        let stdout = String::from_utf8_lossy(&output.stdout);
        let stderr = String::from_utf8_lossy(&output.stderr);
        // 退出码 3 = 脚本判定为「端口被占 / bind 冲突」(可重试);其它码 = 真实故障(不重试)。
        // 把 (exit N) 写进错误消息,既供诊断也作为 error_is_port_conflict 的识别信号。
        return Err(anyhow!(
            "星阙 backend start failed (exit {})\nstdout:\n{}\nstderr:\n{}",
            code,
            stdout,
            stderr
        ));
    }
    emit_progress(window, 92, "本地服务已就绪");
    Ok(())
}

/// 修法1:脚本以 exit 3 表示「端口被占 / bind 冲突」,可换口重试。
/// 仅匹配本函数上方自己生成的固定前缀,避免脚本输出里偶然出现的同形文本误判。
fn error_is_port_conflict(e: &anyhow::Error) -> bool {
    format!("{:#}", e).contains("start failed (exit 3)")
}

/// 修法1:backend/chart 端口冲突自动重试。
/// 铁律:web 端口 / 静态服务器完全不参与本环(在 runtime_bootstrap 中已先于此起好并由 Rust 持有),
/// 这里只重选 backend/chart 一对端口;`AppState.web_shutdown` 绝不在此被读写。
/// - 失败码 == 端口冲突(exit 3)且仍有重试次数 → stop_runtime + 退避 + 换一对全新空闲端口重试;
/// - 非端口类错误,或端口重试已耗尽 → 原样返回错误,交回上层既有的「更新后首启 / 快路径回退」分支处理。
/// 成功时 `*backend_port`/`*chart_port` 持有真正生效的那对端口(供 frontend_url 使用)。
#[allow(clippy::too_many_arguments)]
pub(crate) fn start_runtime_with_port_retry(
    paths: &RuntimePaths,
    window: &WebviewWindow,
    backend_port: &mut u16,
    chart_port: &mut u16,
    startup_timeout_secs: Option<u64>,
    skip_runtime_warmup: bool,
    skip_mongo_ping: bool,
    trusted_runtime: bool,
) -> Result<()> {
    let mut last_err: Option<anyhow::Error> = None;
    for attempt in 0..PORT_RETRY_MAX {
        match start_runtime(
            paths,
            window,
            *backend_port,
            *chart_port,
            startup_timeout_secs,
            skip_runtime_warmup,
            skip_mongo_ping,
            trusted_runtime,
        ) {
            Ok(()) => return Ok(()),
            Err(e) => {
                let is_port = error_is_port_conflict(&e);
                last_err = Some(e);
                if is_port && attempt + 1 < PORT_RETRY_MAX {
                    emit_status(window, "检测到端口被占用，正在自动重选端口重试…");
                    stop_runtime(paths, Some((*backend_port, *chart_port)));
                    thread::sleep(Duration::from_millis(400));
                    *backend_port = choose_free_port()?;
                    *chart_port = choose_free_port()?;
                    continue;
                }
                break;
            }
        }
    }
    Err(last_err.unwrap_or_else(|| anyhow!("星阙 backend start failed (port retry exhausted)")))
}

/// 每次壳进程一枚的启动会话 nonce:注入后端环境(HOROSA_LAUNCH_NONCE)与前端 URL(&sid=)。
/// 前端身份握手(GET /horosaIdentity)据此把「端口被其它进程/其它星阙实例占用」与真后端
/// 区分开——本地服务地址永不盲信。非安全边界,只做防混淆凭据;同一壳会话内「重启后端」
/// 复用同值,前端无需重新协商。
pub(crate) fn launch_nonce() -> &'static str {
    use std::sync::OnceLock;
    static NONCE: OnceLock<String> = OnceLock::new();
    NONCE.get_or_init(|| {
        let mut hasher = Sha256::new();
        hasher.update(std::process::id().to_le_bytes());
        if let Ok(dur) = SystemTime::now().duration_since(UNIX_EPOCH) {
            hasher.update(dur.as_nanos().to_le_bytes());
        }
        let digest = hasher.finalize();
        digest
            .iter()
            .take(8)
            .map(|b| format!("{:02x}", b))
            .collect::<String>()
    })
}

/// 前端服务地址自愈再协商的真值源:返回本会话真实后端端点 + 启动 nonce,
/// 与启动 URL 的 srv/chartSrv/kentangSrv/sid 查询参数同构。
/// 前端在身份握手失败(端口被其它进程占用/localStorage 陈旧/推导落空)时调用。
#[derive(Debug, Clone, Serialize)]
#[serde(rename_all = "camelCase")]
pub(crate) struct BackendEndpoints {
    srv: String,
    chart_srv: String,
    kentang_srv: String,
    pub(crate) sid: String,
}

#[tauri::command]
pub(crate) fn get_backend_endpoints(
    app: AppHandle,
) -> std::result::Result<BackendEndpoints, String> {
    let state = app.state::<AppState>();
    let session = state.session.lock().map_err(|e| e.to_string())?;
    let Some(session) = session.as_ref() else {
        return Err("backend session not started".into());
    };
    Ok(BackendEndpoints {
        srv: format!("http://127.0.0.1:{}", session.backend_port),
        chart_srv: format!("http://127.0.0.1:{}", session.chart_port),
        kentang_srv: format!("http://127.0.0.1:{}", session.chart_port),
        sid: launch_nonce().to_string(),
    })
}

// 前端 URL 的 runtime 版本参数:前端 L3 持久缓存(IndexedDB,TTL 24h)把它掺进信封
// rev —— runtime 更新后 24h 内绝不回放旧算法结果(旧口子:信封 rev 是常量 net-v1)。
// 取值=已装 runtime 的 manifest.version(真在跑的),bootstrap/重引导时刷新;未知则不带参
// (dev 直跑 umi 无此参,前端保持 net-v1 旧行为)。
pub(crate) static FRONTEND_RUNTIME_VERSION: Mutex<Option<String>> = Mutex::new(None);

pub(crate) fn note_runtime_version_for_url(version: &str) {
    let trimmed = version.trim();
    if trimmed.is_empty() {
        return;
    }
    if let Ok(mut slot) = FRONTEND_RUNTIME_VERSION.lock() {
        *slot = Some(trimmed.to_string());
    }
}

pub(crate) fn frontend_url(web_port: u16, backend_port: u16, chart_port: u16) -> String {
    let backend_root = format!("http://127.0.0.1:{}", backend_port);
    let chart_root = format!("http://127.0.0.1:{}", chart_port);
    let mut url = format!(
        "http://127.0.0.1:{}/index.html?srv={}&chartSrv={}&kentangSrv={}&sid={}&v={}",
        web_port,
        urlencoding::encode(&backend_root),
        urlencoding::encode(&chart_root),
        urlencoding::encode(&chart_root),
        launch_nonce(),
        unix_ts()
    );
    if let Ok(slot) = FRONTEND_RUNTIME_VERSION.lock() {
        if let Some(version) = slot.as_ref() {
            url.push_str("&rv=");
            url.push_str(&urlencoding::encode(version));
        }
    }
    url
}

/// 提前导航 URL:early=1(前端就绪门按目标根探活排队)+ boot=壳启动 epoch 毫秒(页面「已用时」从壳起算,
/// 与启动账本 run 标签同源)+ 更新后首启再带 firstLaunch=1(前端兜底放行拉长到 900 s、文案改「更新已完成,正在恢复启动」)。
pub(crate) fn early_nav_url(
    web_port: u16,
    backend_port: u16,
    chart_port: u16,
    post_update: bool,
) -> String {
    let mut url = frontend_url(web_port, backend_port, chart_port);
    url.push_str("&early=1");
    if post_update {
        url.push_str("&firstLaunch=1");
    }
    if let Some(epoch) = STARTUP_LEDGER
        .get()
        .and_then(|v| v.as_ref())
        .and_then(|(run_tag, _, _)| run_tag.strip_prefix('r'))
        .and_then(|digits| digits.parse::<u128>().ok())
    {
        url.push_str(&format!("&boot={}", epoch));
    }
    url
}
