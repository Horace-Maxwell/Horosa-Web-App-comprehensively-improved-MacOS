#![cfg_attr(not(debug_assertions), windows_subsystem = "windows")]

use anyhow::{anyhow, Context, Result};
use base64::engine::general_purpose::STANDARD as BASE64_STANDARD;
use base64::Engine as _;
use mime_guess::from_path;
use reqwest::blocking::Client;
use rfd::{AsyncFileDialog, FileDialog};
use rfd::{MessageButtons, MessageDialog, MessageDialogResult, MessageLevel};
use semver::Version;
use serde::{Deserialize, Serialize};
use sha2::{Digest, Sha256};
use std::collections::HashMap;
use std::fs::{self, File};
use std::io::{Read, Write};
use std::net::{SocketAddr, TcpListener};
use std::path::{Path, PathBuf};
use std::process::{Command, Stdio};
use std::sync::atomic::{AtomicBool, AtomicU64, AtomicUsize, Ordering};
use std::sync::{Arc, Condvar, Mutex};
use std::thread;
use std::time::{Duration, Instant, SystemTime, UNIX_EPOCH};
use tauri::menu::{Menu, MenuItem, PredefinedMenuItem, Submenu};
use tauri::{
    AppHandle, Emitter, LogicalPosition, LogicalSize, Manager, Position, RunEvent, Runtime, Size,
    State, WebviewUrl, WebviewWindow, WebviewWindowBuilder, WindowEvent,
};
use tiny_http::{Header, Method, Response, Server, StatusCode};
use walkdir::WalkDir;
use zip::ZipArchive;

// 外部智能体连接(本机 MCP 服务):协议核/三道门/传输/页面桥全在子模块,本文件只挂钩子。
mod horosa_cli;
mod mcp_client;
mod mcp_server;
mod mcp_stdio;
mod rest_api;

// 壳层按职责拆成的模块(各文件头一行说明职责)。模块之间、以及与本文件之间的引用一律经由下面的整体导入。
mod agent_bridge;
mod ai_files;
mod app_state;
mod asset_review;
mod bootstrap;
mod config;
mod desktop_io;
mod diagnostics;
mod edition;
mod ledger;
mod notify;
mod runtime_archive;
mod runtime_components;
mod runtime_health;
mod runtime_install;
mod runtime_paths;
mod runtime_prewarm;
mod runtime_slots;
mod services;
mod shell_init;
mod shell_text;
mod static_server;
mod storage;
mod ui_launcher;
mod ui_menu;
mod ui_windows;
mod updater_check;
mod updater_download;
mod updater_events;
mod updater_helper;
mod updater_manifest;
mod updater_staged;

use agent_bridge::*;
use ai_files::*;
use app_state::*;
use asset_review::*;
use bootstrap::*;
use config::*;
use desktop_io::*;
use diagnostics::*;
use edition::*;
use ledger::*;
use notify::*;
use runtime_archive::*;
use runtime_components::*;
use runtime_health::*;
use runtime_install::*;
use runtime_paths::*;
use runtime_prewarm::*;
use runtime_slots::*;
use services::*;
use shell_init::*;
use shell_text::*;
use static_server::*;
use storage::*;
use ui_launcher::*;
use ui_menu::*;
use ui_windows::*;
use updater_check::*;
use updater_download::*;
use updater_events::*;
use updater_helper::*;
use updater_manifest::*;
use updater_staged::*;

/// 命令行参数有损转成 UTF-8(非 UTF-8 字节 → U+FFFD),绝不 panic。
fn lossy_args<I: IntoIterator<Item = std::ffi::OsString>>(args: I) -> Vec<String> {
    args.into_iter()
        .map(|a| a.to_string_lossy().into_owned())
        .collect()
}

fn main() {
    // 隐藏 CLI 旗标:update helper 用「新版 app 自己的二进制」做原子互换,
    // 位于 tauri::Builder 之前(零 UI、零窗口即退)。
    {
        // 参数里可能有非 UTF-8 字节(终端里随手粘的文件名等):std::env::args() 会当场 panic(发布版 = 整个进程退出),
        // 这里逐个有损转换,坏字节变成 U+FFFD,交给各子命令按普通参数报错
        let args = lossy_args(std::env::args_os());
        // [CLI] 终端命令(`horosa …` 垫片即调这里):零界面;不论子命令认不认得都在此退出,绝不落到拉起界面
        if args.len() >= 2 && args[1] == horosa_cli::CLI_FLAG {
            std::process::exit(horosa_cli::run_cli(&args[2..]));
        }
        if args.len() == 4 && args[1] == "--horosa-atomic-swap" {
            std::process::exit(run_swap_cli(Path::new(&args[2]), Path::new(&args[3])));
        }
        // helper 全量 runtime 对换(与 --horosa-atomic-swap 同款先例:零 UI 即退)。
        if args.len() == 5 && args[1] == "--horosa-runtime-swap" {
            std::process::exit(run_runtime_swap_cli(
                Path::new(&args[2]),
                Path::new(&args[3]),
                &args[4],
            ));
        } // postinstall 预置信任:安装器已跑过 python import 冒烟 + java -version,
          // 由本子命令以【与 App 同一份格式代码】预写健康缓存 + fast-path 标记 → 首真启
          // 走 trusted 快路径(early-nav/免深检/180s 预算),免付 untrusted 全量校验档。
          // 失败无害:不写=首启照旧 untrusted 完整校验;启动失败仍有 fast_path_fallback+看门狗。
        if args.len() == 3 && args[1] == "--horosa-preseed-health" {
            std::process::exit(run_preseed_health_cli(Path::new(&args[2])));
        }
        // [首启原生库预检] 安装脚本装完后台调;零界面,做完即退(说明见 native_prewarm_run 上方)。
        if args.len() == 3 && args[1] == "--horosa-native-prewarm" {
            std::process::exit(run_native_prewarm_cli(Path::new(&args[2])));
        }
        // stdio 代理:Claude Desktop 这类只会 stdio 的客户端用「同一份 App 二进制 + 端点文件」接本机 MCP
        //(零 UI 即退;令牌只在端点文件里,不进任何客户端配置)。
        if args.len() == 3 && args[1] == mcp_stdio::MCP_STDIO_FLAG {
            std::process::exit(mcp_stdio::run_cli(Path::new(&args[2])));
        }
    }
    configure_macos_native_window_restoration();
    register_panic_runtime_cleanup();
    sweep_stale_tmp_downloads();
    tauri::Builder::default()
        .manage(AppState::default())
        .manage(mcp_server::McpState::default())
        .manage(mcp_client::ClientState::with_stdio_confirm(
            std::sync::Arc::new(|name: &str, display: &str| {
                mcp_client::native_stdio_confirm(name, display)
            }),
        ))
        // 主线程创建(照官方 clipboard-manager 插件形态);失败存 None,command 内惰性重建
        .manage(DesktopClipboardState(Mutex::new(
            arboard::Clipboard::new().ok(),
        )))
        .menu(build_menu)
        .invoke_handler(shadow_write_off_main_handler(tauri::generate_handler![
            bridge_diag_report_command,
            web_ledger_mark_command,
            set_agent_enabled_command,
            mcp_server_status_command,
            ai_master_key_command,
            mcp_server_set_enabled_command,
            mcp_server_set_limits_command,
            mcp_server_rotate_token_command,
            mcp_server_set_rest_enabled_command,
            cli_shim_status_command,
            cli_shim_install_command,
            cli_shim_remove_command,
            mcp_server_reveal_token_command,
            agent_tool_result_command,
            agent_tool_progress_command,
            agent_bridge_ready_command,
            agent_notify_command,
            notify_hook_status_command,
            notify_hook_set_command,
            notify_hook_run_command,
            mcp_client_list_command,
            mcp_client_upsert_command,
            mcp_client_remove_command,
            mcp_client_connect_command,
            mcp_client_call_command,
            mcp_client_disconnect_command,
            show_desktop_notification_command,
            set_scheduler_enabled_command,
            scheduler_status_command,
            load_preferences_payload,
            seal_shared_runtime_permissions_command,
            save_preferences_command,
            read_diagnostics_snapshot,
            commit_asset_review,
            perform_launcher_action,
            reveal_special_path,
            open_preferences_window_command,
            open_diagnostics_window_command,
            trigger_update_check_command,
            trigger_runtime_repair_command,
            open_login_items_settings_command,
            pick_ai_analysis_files_command,
            pick_ai_analysis_folder_command,
            save_ai_analysis_file_command,
            open_ai_analysis_backup_command,
            update_check_silent,
            app_version_local_command,
            update_start_background,
            update_install_and_restart,
            copy_text_to_clipboard_command,
            open_external_url_command,
            set_shell_script_command,
            get_shell_script_command,
            get_backend_endpoints,
            restart_local_services_command,
            export_diagnostics_bundle,
            shadow_store_write_command,
            shadow_store_read_all_command,
            shadow_store_keep_diverged_command,
            shadow_store_drop_diverged_command,
            auto_backup_write_command,
            auto_backup_list_command,
            auto_backup_read_command,
            auto_backup_prune_command
        ]))
        .setup(|app| {
            let app_handle = app.handle().clone();
            // 原生菜单 / 对话框随界面简繁:读上次页面报来的档,是繁体就按繁体重建菜单(页面开机后还会再报一次)
            load_persisted_shell_script(&app_handle);
            if shell_script_is_hant() {
                if let Ok(menu) = build_menu(&app_handle) {
                    let _ = app_handle.set_menu(menu);
                }
            }
            // 外部 MCP 服务器清单落私有目录(0600);启动即载入,失败不阻断(清单为空=零出站)
            if let Ok(dir) = app.path().app_data_dir() {
                if let Some(state) = app.try_state::<mcp_client::ClientState>() {
                    state.bind_dir(&dir);
                }
            }
            // 自动备份心跳:壳侧线程每 30 分钟 emit 一次(不依赖 WebView 定时器——
            // 窗口最小化/节能会漂移);首跳延后 5 分钟避开冷启高峰。前端 listen 组 zip 回送写盘;
            // 内容指纹未变则前端自行跳过,心跳本身零 IO。
            // 此前用 app.emit 投递 auto-backup-tick 事件(哨兵纯文本陷阱:注释里不复写字面量):页面没有 window.__TAURI__(withGlobalTauri
            // 缺省 false)且 capabilities 为空(event.listen 无授权)→ 从未有人接收,timer 触发路径一直是死的。
            // 改走壳→页面既有 eval 回调范式(同 emit_service_event):页面就绪调 __horosaAutoBackupTick,
            // 未就绪先进 __horosaPendingAutoBackupTicks,页面绑定时补跑。
            {
                let backup_handle = app_handle.clone();
                std::thread::spawn(move || {
                    std::thread::sleep(std::time::Duration::from_secs(300));
                    let mut seq: u64 = 0;
                    loop {
                        seq += 1;
                        dispatch_auto_backup_tick(&backup_handle, seq);
                        std::thread::sleep(std::time::Duration::from_secs(1800));
                    }
                });
            }
            // 定时任务哑心跳:壳侧线程每 60 秒投一次 tick(页面调度器决定跑什么);偏好 scheduler_enabled(缺省 false)
            // 或 HOROSA_SCHEDULER=0 时零动作;首跳延后 90 秒避开冷启;每 30 跳记一次账本。
            {
                let sched_handle = app_handle.clone();
                std::thread::spawn(move || {
                    std::thread::sleep(std::time::Duration::from_secs(SCHEDULER_FIRST_DELAY_SECS));
                    loop {
                        if !scheduler_kill_switch()
                            && load_preferences(&sched_handle).scheduler_enabled
                        {
                            let seq = SCHEDULER_TICKS
                                .fetch_add(1, std::sync::atomic::Ordering::Relaxed)
                                + 1;
                            dispatch_scheduler_tick(&sched_handle, seq);
                        }
                        std::thread::sleep(std::time::Duration::from_secs(SCHEDULER_INTERVAL_SECS));
                    }
                });
            }
            set_window_state_persistence_ready(&app_handle, false);
            let main_state = load_window_states(&app_handle).main;
            let window = if let Some(window) = app.get_webview_window(MAIN_WINDOW_LABEL) {
                window
            } else {
                build_main_window(&app_handle, &main_state)?
            };
            apply_main_window_launch_state(&window, &main_state);
            // 外部智能体连接:清扫陈旧端点文件;页面总开关与子开关皆开(且未被 HOROSA_MCP_SERVER=0 否决)才起监听
            {
                let prefs = load_preferences(&app_handle);
                // 先施加用户设的每分钟调用上限(偏好镜像),再决定是否起监听:服务重建时从 inner 重施
                if let Some(state) = app_handle.try_state::<mcp_server::McpState>() {
                    let _ = mcp_server::apply_limits(&state, prefs.mcp_calls_per_minute);
                    // [REST] REST 子开关同样先施加(服务重建时 start_locked 从 inner 重施)
                    mcp_server::apply_rest_enabled(&state, prefs.mcp_rest_enabled);
                }
                mcp_server::setup_on_launch(
                    &app_handle,
                    prefs.agent_enabled,
                    prefs.mcp_server_enabled,
                );
            }
            set_window_zoom(&app_handle, load_preferences(&app_handle).zoom_level)?;
            if handoff_to_newer_installed_app(&app_handle)? {
                return Ok(());
            }
            show_or_focus_window(&window);
            enable_window_state_persistence_after_launch(app_handle.clone());
            thread::spawn(move || {
                match runtime_bootstrap(app_handle.clone(), window.clone(), false) {
                    Ok(session) => {
                        if let Some(state) = app_handle.try_state::<AppState>() {
                            if let Ok(mut slot) = state.session.lock() {
                                *slot = Some(session.clone());
                            }
                        }
                        emit_ready_and_stabilize(
                            &app_handle,
                            &window,
                            &frontend_url(
                                session.web_port,
                                session.backend_port,
                                session.chart_port,
                            ),
                        );
                        show_post_update_notice_if_needed(&app_handle);
                    }
                    Err(err) => emit_launcher_error(
                        &window,
                        &build_launcher_error_payload(&app_handle, &err),
                    ),
                }
            });

            // 自动检查更新(若偏好启用):启动延迟 10s 首查——
            // 距上次成功检查 <4h 直接跳过(节流,防每次开关 app 都打网络);此后线程
            // 驻留每 24h 再查(长开 app 也能收到新版;偏好每轮重读,关闭即静默)。
            // 检查失败不再静默:账本 rust.update_check_failed + check-failed 低打扰事件。
            {
                let app_handle = app.handle().clone();
                thread::spawn(move || {
                    thread::sleep(std::time::Duration::from_secs(10));
                    loop {
                        if load_preferences(&app_handle).auto_check_updates {
                            run_auto_update_check(&app_handle);
                        }
                        thread::sleep(auto_update_check_cycle());
                    }
                });
            }

            Ok(())
        })
        .on_menu_event(|app, event| {
            let id = event.id();
            if id == MENU_OPEN_PREFERENCES {
                let _ = open_preferences_window(app);
            } else if id == MENU_SHOW_MAIN_WINDOW {
                let _ = open_main_window(app);
            } else if id == MENU_SHOW_DIAGNOSTICS {
                let _ = open_diagnostics_window(app);
            } else if id == MENU_CHECK_UPDATES {
                // 菜单「检查更新」并轨(消全量旁路):主窗口在时走非阻塞事件流(UpdateNotifier,
                // 天然增量,与自动检查同一条路)——此前菜单永远走老阻塞 check_for_updates 的
                // 全量 runtime 下载,同一次更新两个入口体积差 10 倍。无主窗口(启动早期/异常)
                // 或 HOROSA_MENU_UPDATE_LEGACY=1 时保留老路,老函数整体不删。
                let legacy =
                    std::env::var("HOROSA_MENU_UPDATE_LEGACY").ok().as_deref() == Some("1");
                let has_main = app.get_webview_window(MAIN_WINDOW_LABEL).is_some();
                if !legacy && has_main {
                    let app_handle = app.clone();
                    thread::spawn(move || match update_check_silent(app_handle.clone()) {
                        Ok(avail) if avail.available => {
                            let mut payload = serde_json::json!({
                                "phase": "available",
                                "currentVersion": avail.current_version,
                                "latestVersion": avail.latest_version,
                                "runtimeNeedsUpdate": avail.runtime_needs_update,
                                "notes": avail.notes,
                                "releaseUrl": avail.release_url,
                            });
                            if let Some(mode) = avail.update_mode {
                                payload["mode"] = serde_json::json!(mode);
                            }
                            if let Some(bytes) = avail.download_bytes {
                                payload["downloadBytes"] = serde_json::json!(bytes);
                            }
                            if let Some(pct) = avail.reuse_pct {
                                payload["reusePct"] = serde_json::json!(pct);
                            }
                            emit_update_event(&app_handle, &payload.to_string());
                        }
                        Ok(_) => {
                            emit_update_event(
                                &app_handle,
                                &serde_json::json!({
                                    "phase": "uptodate",
                                    "message": "已是最新版本",
                                })
                                .to_string(),
                            );
                        }
                        Err(err) => {
                            emit_update_event(
                                &app_handle,
                                &serde_json::json!({
                                    "phase": "error",
                                    "message": format!("检查更新失败:{err}"),
                                })
                                .to_string(),
                            );
                        }
                    });
                } else {
                    let app_handle = app.clone();
                    thread::spawn(move || {
                        if let Err(err) = check_for_updates(app_handle.clone()) {
                            MessageDialog::new()
                                .set_level(MessageLevel::Error)
                                .set_title(shell_text("dlg.update_failed.title"))
                                .set_description(format!("{err:#}"))
                                .set_buttons(MessageButtons::Ok)
                                .show();
                        }
                    });
                }
            } else if id == MENU_REINSTALL_RUNTIME {
                // 引导在途时单飞拒绝(已记账本),菜单侧无需再提示
                let _ = trigger_reinstall(app.clone());
            } else if id == MENU_OPEN_LOGS {
                if let Ok(paths) = resolve_runtime_paths(app) {
                    let _ = ensure_dir(&paths.logs_dir);
                    open_path(&paths.logs_dir);
                }
            } else if id == MENU_OPEN_DATA {
                if let Ok(paths) = resolve_runtime_paths(app) {
                    let _ = ensure_dir(&paths.app_data_dir);
                    open_path(&paths.app_data_dir);
                }
            } else if id == MENU_OPEN_RUNTIME {
                if let Ok(paths) = resolve_runtime_paths(app) {
                    let _ = ensure_dir(&paths.runtime_dir);
                    open_path(&paths.runtime_dir);
                }
            } else if id == MENU_RELOCATE_APP {
                // Translocation/任意非标准位置 → 一键拷入「应用程序」并重开。
                let app_handle = app.clone();
                thread::spawn(move || {
                    let bundle = app_bundle_path();
                    let dest = installed_app_target_path();
                    let already_installed = bundle
                        .as_deref()
                        .map(|b| b == dest.as_path())
                        .unwrap_or(false);
                    if already_installed {
                        MessageDialog::new()
                            .set_level(MessageLevel::Info)
                            .set_title(shell_text("dlg.relocate.title"))
                            .set_description(shell_text("dlg.relocate.already"))
                            .show();
                        return;
                    }
                    let proceed = MessageDialog::new()
                        .set_level(MessageLevel::Info)
                        .set_title(shell_text("dlg.relocate.title"))
                        .set_description(shell_text("dlg.relocate.confirm"))
                        .set_buttons(MessageButtons::YesNo)
                        .show();
                    if proceed != MessageDialogResult::Yes {
                        return;
                    }
                    match relocate_app_to_applications(&app_handle) {
                        Ok(done_msg) if !done_msg.is_empty() => {
                            MessageDialog::new()
                                .set_level(MessageLevel::Info)
                                .set_title(shell_text("dlg.relocate.title"))
                                .set_description(done_msg)
                                .show();
                        }
                        Ok(_) => {}
                        Err(err) => {
                            MessageDialog::new()
                                .set_level(MessageLevel::Error)
                                .set_title(shell_text("dlg.relocate.title"))
                                .set_description(shell_text_fmt(
                                    "dlg.relocate.failed",
                                    &[("err", &format!("{err:#}"))],
                                ))
                                .show();
                        }
                    }
                });
            } else if id == MENU_RESTART_SERVICES {
                // 手动兜底:服务被系统/杀软杀掉、探活看门狗已限频停手时,一键救活。
                let app_handle = app.clone();
                thread::spawn(move || {
                    let outcome = restart_local_services(&app_handle, "menu");
                    let (level, text) = match outcome {
                        Ok(()) => (MessageLevel::Info, shell_text("dlg.restart.ok")),
                        Err(err) => (
                            MessageLevel::Error,
                            shell_text_fmt("dlg.restart.failed", &[("err", &format!("{err:#}"))]),
                        ),
                    };
                    MessageDialog::new()
                        .set_level(level)
                        .set_title(shell_text("dlg.restart.title"))
                        .set_description(text)
                        .show();
                });
            } else if id == MENU_RELOAD_MAIN {
                if let Some(window) = app.get_webview_window(MAIN_WINDOW_LABEL) {
                    let _ = window.eval("window.location.reload()");
                }
            } else if id == MENU_OPEN_RELEASES {
                let _ = open_release_page(app);
            } else if id == MENU_ZOOM_IN {
                let _ = adjust_window_zoom(app, ZOOM_STEP);
            } else if id == MENU_ZOOM_OUT {
                let _ = adjust_window_zoom(app, -ZOOM_STEP);
            } else if id == MENU_ZOOM_RESET {
                let _ = set_window_zoom(app, DEFAULT_ZOOM);
            }
        })
        .build(build_app_context())
        .expect("error while running 星阙 desktop shell")
        .run(|app, event| match event {
            RunEvent::WindowEvent { label, event, .. } => {
                // [tahoe-resize-bridge] macOS 26(Tahoe)WKWebView 实测出现过拖窗页面不重排(window
                // resize 事件链缺席)——壳侧对每次 Resized/ScaleFactorChanged 主动补发一次页面
                // resize 通知。健康引擎上=多派发一次,页面各消费端(80ms 去抖/rAF 合并/签名守卫)
                // 天然幂等;不走 __horosaPending* 范式:resize 无载荷、无到达义务(页面未挂载时
                // 首帧布局本来就对),套 pending 反制造「挂载时补发陈旧 resize」伪语义。
                let is_resize_like = matches!(
                    event,
                    WindowEvent::Resized(_) | WindowEvent::ScaleFactorChanged { .. }
                );
                if is_resize_like {
                    if let Some(window) = app.get_webview_window(&label) {
                        let _ =
                            window.eval("try{window.dispatchEvent(new Event('resize'))}catch(_){}");
                    }
                }
                // 窗口变窄后当前档可能超过新的宽度上限 → 降到上限(只降不升;持久化随 set_window_zoom)。
                if is_resize_like && label == MAIN_WINDOW_LABEL {
                    let current = app
                        .try_state::<AppState>()
                        .and_then(|state| state.zoom_level.lock().ok().map(|slot| *slot))
                        .unwrap_or(DEFAULT_ZOOM);
                    let (cap, _) = window_zoom_cap(app);
                    if current > cap + 1e-9 {
                        let _ = set_window_zoom(app, cap);
                    }
                }
                let should_persist = match event {
                    WindowEvent::Moved(_) | WindowEvent::Resized(_) => {
                        is_window_state_persistence_ready(app)
                    }
                    WindowEvent::CloseRequested { .. } => true,
                    _ => false,
                };
                if should_persist {
                    if let Some(window) = app.get_webview_window(&label) {
                        let _ = persist_window_state_for_label(app, &label, &window);
                    }
                }
            }
            // 🔴 退出两臂禁同步子进程(cleanup_state → stop 脚本 .status() 会阻塞主事件循环,
            // macOS 标记 not responding 数秒)。Cmd+Q 走 native terminate: 只回调 Exit、不可
            // prevent,所以两臂都用 detached + 去重的 spawn_exit_cleanup。
            RunEvent::ExitRequested { .. } => {
                if is_window_state_persistence_ready(app) {
                    persist_all_known_window_states(app);
                }
                wait_shadow_writes_settle(); // 在途影子写清空(≤500ms)再放行退出
                spawn_exit_cleanup(app);
            }
            RunEvent::Exit => {
                if is_window_state_persistence_ready(app) {
                    persist_all_known_window_states(app);
                }
                wait_shadow_writes_settle(); // macOS terminate 路径只回调 Exit,同样兜底
                spawn_exit_cleanup(app);
            }
            _ => {}
        });
}

// ── 壳→页面事件桥死开关自证(不起 UI:MockRuntime + 真实 generate_context!) ──
// ① withGlobalTauri 缺省 false → 页面没有 window.__TAURI__(tauri-codegen 只在为 true 时注入全局 API 脚本);
// ② capabilities 为空 → core:event:allow-listen 未授权 → 即便拿到 __TAURI_INTERNALS__,plugin:event|listen 也被 ACL 拒;
// ③ 应用自身命令(generate_handler)不受此影响,仍可 invoke —— 三者一起解释了「emit 从未被接收」与「invoke 却正常」。
#[cfg(test)]
mod bridge_acl_tests;

#[cfg(test)]
mod tests;

// 壳侧零测试面补测:影子副本键白名单 / 自动备份文件名 / 偏好新字段缺省 / 主密钥取建(注入执行器)
#[cfg(test)]
mod shell_guard_tests;

#[cfg(test)]
mod cli_args_tests {
    /// 🔴 std::env::args() 遇到非 UTF-8 参数当场 panic(发布版 = 进程退出)。有损转换:坏字节变 U+FFFD,其余原样。
    #[cfg(unix)]
    #[test]
    fn lossy_args_never_panic_on_non_utf8() {
        use std::ffi::OsString;
        use std::os::unix::ffi::OsStringExt;
        let args = vec![
            OsString::from("horosa"),
            OsString::from("--horosa-cli"),
            OsString::from_vec(vec![b'r', b'e', 0xff, b'c']),
        ];
        let out = super::lossy_args(args);
        assert_eq!(out[0], "horosa");
        assert_eq!(out[1], "--horosa-cli");
        assert_eq!(out[2], "re\u{FFFD}c");
    }
}
