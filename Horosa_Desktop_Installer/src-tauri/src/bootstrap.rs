//! 运行时引导、修复重入、退出清理与 panic 停服。

use super::*;

/// 修复引导在途旗标(与 BOOTSTRAP_BUSY 合判):两次点击之间引导线程尚未挂上 busy 守卫的窗口也要挡住。
pub(crate) static REINSTALL_INFLIGHT: AtomicBool = AtomicBool::new(false);

/// 引导结束(含 panic 展开)即清在途旗标,不会因一次异常永久拒绝修复。
pub(crate) struct ReinstallInflightGuard;
impl Drop for ReinstallInflightGuard {
    fn drop(&mut self) {
        REINSTALL_INFLIGHT.store(false, Ordering::SeqCst);
    }
}

/// 单飞:启动 / 修复 / 更新引导仍在进行时不再并发第二条 —— 两条引导线程会各自 stop_runtime 互杀、
/// 两次 emit_ready 抢导航(提前导航后页面里的「重启后端」按钮 15 s 就出现,更新后首启常在此窗口内)。
pub(crate) fn trigger_reinstall(app: AppHandle) -> std::result::Result<(), &'static str> {
    let Some(window) = app.get_webview_window(MAIN_WINDOW_LABEL) else {
        return Err("主窗口不可用");
    };
    if bootstrap_busy() || REINSTALL_INFLIGHT.swap(true, Ordering::SeqCst) {
        ledger_mark("rust.reinstall_refused_busy", None);
        return Err("启动/修复/更新流程正在进行,请稍候片刻再试");
    }
    let win = window.clone();
    let app_handle = app.clone();
    thread::spawn(move || {
        let outcome = {
            let _inflight = ReinstallInflightGuard;
            runtime_bootstrap(app_handle.clone(), win.clone(), true)
        };
        match outcome {
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
            Err(err) => emit_launcher_error(&win, &build_launcher_error_payload(&app_handle, &err)),
        }
    });
    Ok(())
}

pub(crate) fn cleanup_state(app: &AppHandle) {
    if let Some(state) = app.try_state::<AppState>() {
        if let Ok(mut shutdown) = state.web_shutdown.lock() {
            if let Some(flag) = shutdown.take() {
                flag.store(true, Ordering::Relaxed);
            }
        }
        if let Ok(session_slot) = state.session.lock() {
            if let Some(session) = session_slot.as_ref() {
                stop_runtime(
                    &session.paths,
                    Some((session.backend_port, session.chart_port)),
                );
            }
        }
    }
}

/// 退出清理只跑一次:红点路径 ExitRequested 与 Exit 各回调一次、`app.exit(0)` 也双发,
/// 不去重则 stop 脚本跑两遍。
static EXIT_CLEANUP_SPAWNED: AtomicBool = AtomicBool::new(false);

/// 抢占退出清理执行权:首个调用者得 true,其余 false(抽成函数便于单测)。
pub(crate) fn claim_exit_cleanup() -> bool {
    !EXIT_CLEANUP_SPAWNED.swap(true, Ordering::SeqCst)
}

/// 退出路径专用:detached 启动 stop 脚本,不等待。
/// 🔴 macOS 上菜单/Dock 的 Quit 走 native `terminate:`,tao 只回调 RunEvent::Exit(无
/// ExitRequested 可 prevent),且该回调跑在 applicationWillTerminate 内——任何同步
/// `.status()/.output()` 都让主事件循环停摆、系统标记 not responding。
/// 正确性:stop 脚本自含界(pid 文件+工作区路径守卫+端口兜底),app 死后脚本 reparent 给
/// launchd 继续完成回收;下次启动另有 reclaim_stale_port/stop_runtime 预清理兜底。
/// 把会话真实端口交给 stop 脚本(pid 文件名与端口兜底扫描都按端口寻址;不带时脚本只看默认口 8899/9999/8000)。
pub(crate) fn apply_stop_ports_env(command: &mut Command, ports: Option<(u16, u16, u16)>) {
    if let Some((backend_port, chart_port, web_port)) = ports {
        command
            .env("HOROSA_SERVER_PORT", backend_port.to_string())
            .env("HOROSA_CHART_PORT", chart_port.to_string())
            .env("HOROSA_WEB_PORT", web_port.to_string());
    }
}

fn stop_runtime_detached(paths: &RuntimePaths, ports: Option<(u16, u16, u16)>) {
    if !paths.stop_script.exists() {
        return;
    }
    let mut command = Command::new("/bin/bash");
    command
        .arg(&paths.stop_script)
        .current_dir(paths.runtime_dir.join("Horosa-Web"))
        .stdout(Stdio::null())
        .stderr(Stdio::null());
    // 把本会话真实动态端口交给脚本:端口兜底扫描打到真端口,而非默认 8899/9999/8000
    // (修旧盲点:动态选口后兜底扫描一直只看默认口)。
    apply_stop_ports_env(&mut command, ports);
    let _ = command.spawn();
}

/// 退出清理(非阻塞版):置静态服务器关闭位 + detached 停后端,毫秒级返回。
/// mid-life 的同步停服(runtime 更新前,必须停干净才能解压覆盖)仍走 cleanup_state,不经此函数。
pub(crate) fn spawn_exit_cleanup(app: &AppHandle) {
    if !claim_exit_cleanup() {
        return;
    }
    // 外部智能体服务:关 socket + 删端点文件(worker 250ms 内退出,不阻塞退出臂)
    mcp_server::stop_on_exit(app);
    if let Some(state) = app.try_state::<mcp_client::ClientState>() {
        mcp_client::stop_on_exit(&state);
    }
    if let Some(state) = app.try_state::<AppState>() {
        if let Ok(mut shutdown) = state.web_shutdown.lock() {
            if let Some(flag) = shutdown.take() {
                flag.store(true, Ordering::Relaxed);
            }
        }
        if let Ok(session_slot) = state.session.lock() {
            if let Some(session) = session_slot.as_ref() {
                stop_runtime_detached(
                    &session.paths,
                    Some((session.backend_port, session.chart_port, session.web_port)),
                );
            }
        }
    }
}

pub(crate) fn runtime_bootstrap(
    app: AppHandle,
    window: WebviewWindow,
    force_runtime_install: bool,
) -> Result<RuntimeSession> {
    // 引导期服务本就不在:挂 busy 守卫让探活看门狗静默,防误判抢跑重启。
    let _bootstrap_busy = BootstrapBusyGuard::hold();
    emit_mode(
        &window,
        if force_runtime_install {
            "repair"
        } else {
            "launch"
        },
    );
    emit_status(&window, "正在检查安装配置…");
    if let Ok(app_data_dir) = app.path().app_data_dir() {
        let logs_dir = app_data_dir.join("logs");
        ledger_init(&logs_dir);
        // 日志清扫后台化:本就 best-effort、只删 >14 天项且与本 run 新目录无交集,
        // 无任何序依赖 —— 挪出 bootstrap 关键路径(冷 FS 下同步 readdir+删除可达几十 ms)。
        // HOROSA_PRUNE_LOGS_ASYNC=0 回同步旧序。
        if std::env::var("HOROSA_PRUNE_LOGS_ASYNC")
            .map(|v| v == "0")
            .unwrap_or(false)
        {
            prune_logs_dir_best_effort(&logs_dir);
        } else {
            let dir = logs_dir.clone();
            thread::spawn(move || {
                prune_logs_dir_best_effort(&dir);
            });
        }
    }
    ledger_mark("rust.bootstrap_begin", None);
    // App Translocation 提示(非阻塞):zip 通道用户从「下载」直接双击时,macOS 会把 App
    // 转移到随机只读挂载点运行。运行本身不受影响(运行时在共享/用户目录),但自更新换
    // 不到真实 App 路径——温和引导拖入「应用程序」。pkg 用户不会命中。
    if let Ok(exe) = std::env::current_exe() {
        if exe.to_string_lossy().contains("/AppTranslocation/") {
            ledger_mark("rust.app_translocated", None);
            emit_status(
                &window,
                "检测到 App 正从下载的临时位置运行:可在菜单选择「移入「应用程序」文件夹…」一键搬迁并重开,以获得完整的自动更新体验。",
            );
        }
    }
    // 两段 rename 回退路径/postinstall shell 对换若在中间被断电强杀,
    // current 会整体缺失——启动最早期按候选完整度收养,先于看门狗与安装检查。
    {
        let mut torn_roots = vec![shared_runtime_root()];
        if let Ok(user_root) = user_runtime_root(&app) {
            torn_roots.push(user_root);
        }
        // 本账户只读的共享运行环境(多账户机上别的账户装的)不由本账户修,留给它的属主
        torn_roots.retain(|root| path_writable_by_current_user(root));
        for root in &torn_roots {
            match repair_torn_runtime_slots(root) {
                Ok(true) => emit_status(
                    &window,
                    "检测到上次更新中断，已自动恢复运行时，正在继续启动…",
                ),
                Ok(false) => {}
                Err(err) => eprintln!("[torn-repair] {} 修复失败: {err:#}", root.display()),
            }
            sweep_stale_runtime_stage_dirs(root);
        }
    }
    // 启动健康看门狗:连续 2 次未达 ready → 自动回滚 previous 槽(更新到坏版本的自愈)。
    if let Some(health_path) = launch_health_path(&app) {
        let pending = launch_health_note_start(&health_path);
        if pending > WATCHDOG_ROLLBACK_THRESHOLD && !force_runtime_install {
            let mut roots = vec![shared_runtime_root()];
            if let Ok(user_root) = user_runtime_root(&app) {
                roots.push(user_root);
            }
            // 本账户起不来不该回滚别的账户装的共享运行环境(本账户对它只读)
            roots.retain(|root| path_writable_by_current_user(root));
            let mut rolled = false;
            for root in &roots {
                match rollback_runtime_to_previous(root) {
                    Ok(true) => rolled = true,
                    Ok(false) => {}
                    Err(err) => eprintln!("[watchdog] 回滚 {} 失败: {err:#}", root.display()),
                }
            }
            if rolled {
                ledger_mark(
                    "rust.watchdog_rollback",
                    Some(serde_json::json!({"pending": pending})),
                );
                // 台账:看门狗自动回滚(耐久行)
                append_update_history(
                    &app,
                    serde_json::json!({ "event": "watchdog_rollback", "pending": pending }),
                );
                emit_status(
                    &window,
                    "检测到连续两次启动未成功，已自动回退到上一版本运行时；启动后可在菜单「检查更新」重试升级。",
                );
                // 回滚开新的一链:本次视为第 1 次尝试。
                launch_health_write(&health_path, &LaunchHealth { pending_starts: 1 });
            }
        }
    }
    let paths = ensure_runtime_installed(&app, &window, force_runtime_install)?;
    ledger_mark("rust.runtime_check_done", None);
    // panic 路径清理登记(只第一次生效):app panic 不触发 RunEvent::Exit,
    // 这里把 stop 脚本交给 panic hook,后端子进程不孤儿化。
    let _ = PANIC_STOP_SCRIPT.set((
        paths.stop_script.clone(),
        paths.runtime_dir.join("Horosa-Web"),
    ));
    // 同一进程再次引导(重装运行时 / 重启服务失败后的回退修复)沿用上一次会话的前端口,
    // 并先收掉本进程上一台静态服务器;首次引导没有旧会话,按 38991 起的阶梯选口。
    let previous_web_port = current_session_snapshot(&app).map(|s| s.web_port);
    let preferred_web_port = previous_web_port.unwrap_or(DEFAULT_FRONTEND_PORT);
    let mut web_port = match app.try_state::<AppState>() {
        Some(state) => pick_web_port_for_bootstrap(&state.web_shutdown, previous_web_port)?,
        None => choose_port_with_preference(preferred_web_port)?,
    };
    let shutdown = Arc::new(AtomicBool::new(false));
    // TOCTOU 防线:「探口空闲」与「真正 bind」之间存在毫秒级窗口,被其它进程抢先会
    // bind 失败——从首选口起重走阶梯 ×3,而不是把整次首启判死。
    let mut server_handle =
        start_static_server(paths.frontend_dir.clone(), web_port, shutdown.clone());
    for _ in 0..3 {
        if server_handle.is_ok() {
            break;
        }
        web_port = retry_web_port_after_bind_race(preferred_web_port)?;
        server_handle = start_static_server(paths.frontend_dir.clone(), web_port, shutdown.clone());
    }
    let _server_handle = server_handle?;
    let mut backend_port = choose_free_port()?;
    let mut chart_port = choose_free_port()?;

    ledger_mark(
        "rust.ports_chosen",
        Some(serde_json::json!({"web": web_port, "backend": backend_port, "chart": chart_port})),
    );
    if let Some(state) = app.try_state::<AppState>() {
        replace_web_shutdown(&state.web_shutdown, Some(shutdown));
    }
    ledger_mark("rust.static_server_up", None);

    // 修复(更新后卡顿)C①:标记「读取即消费」——检测到刚更新完即把通知缓存进内存并删除磁盘标记,
    // 这样无论本次首启成功/失败,标记都不残留 → 杜绝「首启失败后次次都走 300s 全量慢路径」。
    let first_launch_after_update = consume_update_complete_marker_into_state(&app);
    let first_launch_timeout = if first_launch_after_update {
        Some(300)
    } else {
        None
    };
    // 修复(更新后卡住、需重启两三次 — v2.3.2):
    // apply_update 在安装前已对 runtime 包做 sha256 校验(verify_sha256(runtime_sha256)),
    // runtime 即「按官方清单逐字节验签过」的副本,故「更新后首启」再走 300s 全量慢校验属冗余,
    // 反而让冷首启看起来卡死、用户强退 → 标记没写 → 下次又全量 → 反复重启。
    // 这里对刚装好的(已验签)runtime **在 start_runtime 之前**预写 fast-path 标记:
    //   ① 首启即走 trusted 快路径(实测 ~7s,远快于冷全量 22s+);
    //   ② 标记在 warmup/导航之前就落盘 → 即便用户把冷首启当卡死强退,下次仍是快路径,
    //      根除「每次强退都退回 300s 全量 → 要重启两三次才打开」。
    // 兜底:若快路径在新 runtime 上失败,下方 first_launch_after_update 分支会 clear 标记并自动全量复检。
    if first_launch_after_update {
        if let Some(manifest) = read_runtime_manifest(&paths) {
            write_runtime_fast_path_marker(&paths.runtime_dir, &manifest);
        }
    }
    // 提速(更新后卡顿)B:warmup 仅首启触发,且脚本内已改为后台非阻塞预热,不再卡启动;
    // mongo 为可选服务,一律跳过启动期 ping(mongo 缺席时 ping 会拖满等待)。
    let skip_runtime_warmup = !first_launch_after_update;
    let fast_path_enabled = !force_runtime_install && runtime_fast_path_allowed(&paths.runtime_dir);
    let skip_mongo_ping = true;
    if first_launch_after_update {
        emit_status(&window, "检测到刚完成更新，正在执行更新后的首次恢复启动…");
        // 修复(更新后卡顿):runtime 已在安装前逐字节验签,首启走 trusted 快路径(通常 ~10 秒内,
        // 冷启动略久)。用不确定进度动画 + 明确文案,避免冷启动的短暂停顿被当成「卡死」而被强退。
        emit_indeterminate_progress(&window, 78, "更新已完成，正在恢复启动,通常约 10 秒,请稍候…");
        // 修复(更新后卡在启动页 / 不进主界面 / 「进入主界面」按钮无效 —— 真因):
        // 原先此处调 `cleanup_state(&app)`,它会 `web_shutdown.take()` 后 `store(true)`,把本次
        // runtime_bootstrap 上方刚 `start_static_server` 起来的静态服务器(web_port)直接关掉 →
        // 之后 `emit_ready` 让 webview 导航到的 `frontend_url`(http://127.0.0.1:web_port/index.html)
        // 立刻连不上 → 永远停在启动页(每次更新必现;普通重启不走此分支故正常,这也是「重启就好」的原因)。
        // 实测:此刻 curl web_port 直接 connection-refused、进程零监听端口。`cleanup_state` 在这里对
        // session 是 no-op(`start_runtime` 还没跑、session 为 None),唯一实际效果就是误杀静态服务器。
        // 故直接去掉,只保留 1s 缓冲。
        thread::sleep(Duration::from_secs(1));
    }
    // 前后端启动重叠(仅温启快路径):静态服务器已起、三口已定 → 立即把 webview 导航到
    // 前端,umi 下载/解析/JS 启动与 Java/Python 引导并行;前端 request 层检测 URL 的 early=1
    // 后按目标根探活排队请求(L3 持久缓存命中不经门,温启即刻可渲染缓存盘)。
    // 更新后首启/修复/全量校验保持旧序(splash 全程可见;emit_overlay 内联卡与 launcher 错误
    // 面板本就页面无关,故障照常可见)。看门狗 confirm/supervisor 仍只在就绪后的
    // emit_ready_and_stabilize;彼时同参二次 ready 由 init-script __horosaReady 判定不重载。
    // 端口重试换口时,收尾 ready 参数不同 → 自动整页导航到正确端口(行为正确性兜底)。
    // 回退开关:HOROSA_EARLY_NAV=0(账本 rust.early_nav 可查是否生效)。
    // 更新后首次启动也提前进界面:页面 URL 多带 firstLaunch=1(前端就绪门兜底放行 90 s→900 s,与启动脚本就绪总上限同值,
    // StartupGate 从 t=0 显示「更新已完成,正在恢复启动」与已用时)与 boot=壳启动 epoch(已用时从壳起算)。
    // 回退开关:HOROSA_EARLY_NAV_POST_UPDATE=0(只回到「更新后首启保持旧序、splash 全程可见」,普通温启不受影响)。
    // rv(前端 L3 缓存版本闸)必须在第一次导航之前确立:早导航 URL 与收尾 ready 同参不重载,若等到 bootstrap
    // 末尾才记版本,整个会话的 URL 都不带 rv(前端信封恒为 net-v1)→ 更新后 24 h 内可能回放旧运行时的缓存结果。
    // 此处运行时已装好、manifest 即将启动的那一份;末尾那次保留为幂等刷新(引导中途换装则收尾 ready 的 rv 不同 → 整页重载)。
    if let Some(manifest) = read_runtime_manifest(&paths) {
        note_runtime_version_for_url(&manifest.version);
    }
    let post_update_early_nav = std::env::var("HOROSA_EARLY_NAV_POST_UPDATE")
        .map(|v| v != "0")
        .unwrap_or(true);
    let early_nav = fast_path_enabled
        && (!first_launch_after_update || post_update_early_nav)
        && std::env::var("HOROSA_EARLY_NAV")
            .map(|v| v != "0")
            .unwrap_or(true);
    if early_nav {
        ledger_mark(
            "rust.early_nav",
            Some(serde_json::json!({
                "web": web_port, "backend": backend_port, "chart": chart_port,
                "post_update": first_launch_after_update
            })),
        );
        let state = load_window_states(&app).main;
        let early_url = early_nav_url(
            web_port,
            backend_port,
            chart_port,
            first_launch_after_update,
        );
        emit_ready(&window, &early_url);
        stabilize_main_window_after_navigation(app.clone(), window.clone(), state);
    }
    // 修法1:首次启动走带「端口冲突重试」的封装(web/静态服务器不参与本环;仅 backend/chart 换口重试)。
    // 非端口类错误 / 端口重试耗尽时,原样落入下方既有的「更新后首启 / 快路径回退」分支(逻辑保持不变)。
    if let Err(first_err) = start_runtime_with_port_retry(
        &paths,
        &window,
        &mut backend_port,
        &mut chart_port,
        first_launch_timeout,
        skip_runtime_warmup,
        skip_mongo_ping,
        fast_path_enabled,
    ) {
        clear_runtime_fast_path_marker(&paths.runtime_dir);
        if first_launch_after_update {
            emit_status(&window, "更新后的第一次启动正在自动复检服务，请稍候…");
            // indeterminate + 与 start_runtime 入口同档(82):重试会再次进入 start_runtime,
            // 入口发 82,这里若发 84 会出现进度倒退。
            emit_indeterminate_progress(&window, 82, "更新后首次启动自动重试");
            stop_runtime(&paths, Some((backend_port, chart_port)));
            thread::sleep(Duration::from_secs(3));
            backend_port = choose_free_port()?;
            chart_port = choose_free_port()?;
            start_runtime(
                &paths,
                &window,
                backend_port,
                chart_port,
                first_launch_timeout,
                false,
                false,
                false,
            )
            .map_err(|retry_err| {
                anyhow!(
                    "更新后首次启动失败，已自动重试一次仍未恢复。\n首次错误:\n{:#}\n\n重试错误:\n{:#}",
                    first_err,
                    retry_err
                )
            })?;
        } else if fast_path_enabled {
            // WS-1c:回退从「一行状态」升级为醒目说明(属正常保护而非故障)+账本留痕(诊断中心可见)。
            ledger_mark("rust.fast_path_fallback", None);
            emit_status(
                &window,
                "快速启动校验未通过，已自动切换完整校验启动（预计 30-60 秒），属正常自我保护，请稍候…",
            );
            // 同上:与 start_runtime 入口同档防倒退。
            emit_indeterminate_progress(
                &window,
                82,
                "快速启动校验未通过 · 已自动切换完整校验(预计 30-60 秒,属正常保护)",
            );
            stop_runtime(&paths, Some((backend_port, chart_port)));
            thread::sleep(Duration::from_secs(1));
            backend_port = choose_free_port()?;
            chart_port = choose_free_port()?;
            start_runtime(
                &paths,
                &window,
                backend_port,
                chart_port,
                first_launch_timeout,
                false,
                false,
                false,
            )
            .map_err(|retry_err| {
                anyhow!(
                    "快速启动失败，已自动回退到完整校验启动一次仍未恢复。\n首次错误:\n{:#}\n\n回退错误:\n{:#}",
                    first_err,
                    retry_err
                )
            })?;
        } else {
            return Err(first_err);
        }
    }
    if let Some(manifest) = read_runtime_manifest(&paths) {
        write_runtime_fast_path_marker(&paths.runtime_dir, &manifest);
    }
    emit_progress(&window, 100, "星阙 已准备完成");
    // junk 后台 mop-up:trusted 快路径已不在启动期做全树元数据清理(start_runtime),
    // 这里在服务就绪后延迟 10s(避开 warmup IO 高峰)补扫一遍,保持「runtime 树最终无
    // .DS_Store/._* junk」的不变量;best-effort,失败静默(共享目录可能无权限)。
    {
        let mop_dir = paths.runtime_dir.clone();
        thread::spawn(move || {
            thread::sleep(Duration::from_secs(10));
            let _ = cleanup_runtime_metadata(&mop_dir);
        });
    }
    // 会话端口真值确立:刷新 panic 停服补给(崩溃路径也能按真实端口杀干净)。
    set_panic_stop_ports(backend_port, chart_port, web_port);
    // 刷新前端 URL 的 runtime 版本参数(L3 缓存版本闸;更新后重引导取到新值)。
    if let Some(manifest) = read_runtime_manifest(&paths) {
        note_runtime_version_for_url(&manifest.version);
    }
    Ok(RuntimeSession {
        paths,
        backend_port,
        chart_port,
        web_port,
    })
}

/// panic 路径的后端清理:正常退出走 RunEvent::Exit→stop_runtime,但 panic 不触发 Exit 事件,
/// java/python 子进程会孤儿化(start 脚本 reaper 只覆盖下次启动时回收)。bootstrap 成功后把
/// stop 脚本路径塞进这里,panic hook best-effort 执行。
static PANIC_STOP_SCRIPT: std::sync::OnceLock<(PathBuf, PathBuf)> = std::sync::OnceLock::new();
// panic 停服的端口补给:stop 脚本的 pid 文件名与端口兜底扫描都按端口寻址,
// 不带 env 时脚本只看默认口 8899/9999/8000 —— 动态选口的会话在 panic 路径一个都杀不到
// (崩溃后 Java / Python 留在后台)。每次会话端口确立 / 变更时刷新(引导成功、自动重启换口),
// panic 钩子据此注入真实端口。
pub(crate) static PANIC_STOP_PORTS: Mutex<Option<(u16, u16, u16)>> = Mutex::new(None);

/// 会话端口真值变更时同步 panic 停服补给(backend, chart, web)。
pub(crate) fn set_panic_stop_ports(backend_port: u16, chart_port: u16, web_port: u16) {
    if let Ok(mut slot) = PANIC_STOP_PORTS.lock() {
        *slot = Some((backend_port, chart_port, web_port));
    }
}

pub(crate) fn register_panic_runtime_cleanup() {
    let previous = std::panic::take_hook();
    std::panic::set_hook(Box::new(move |info| {
        if let Some((script, cwd)) = PANIC_STOP_SCRIPT.get() {
            if script.exists() {
                let mut command = Command::new("/bin/bash");
                command
                    .arg(script)
                    .current_dir(cwd)
                    .stdout(Stdio::null())
                    .stderr(Stdio::null());
                // 与 stop_runtime_detached 同律:把真实动态端口交给脚本,
                // 否则 pid 文件 / 端口兜底全打默认口,panic 路径必留残留进程。
                let ports = PANIC_STOP_PORTS.lock().ok().and_then(|slot| *slot);
                apply_stop_ports_env(&mut command, ports);
                let _ = command.status();
            }
        }
        previous(info);
    }));
}
