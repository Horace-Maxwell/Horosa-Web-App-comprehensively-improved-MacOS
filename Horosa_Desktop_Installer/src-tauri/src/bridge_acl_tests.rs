use tauri::test::{get_ipc_response, mock_builder, INVOKE_KEY};
use tauri::webview::InvokeRequest;

fn request(cmd: &str, body: serde_json::Value) -> InvokeRequest {
    InvokeRequest {
        cmd: cmd.to_string(),
        callback: tauri::ipc::CallbackFn(0),
        error: tauri::ipc::CallbackFn(1),
        url: "tauri://localhost".parse().unwrap(),
        body: body.into(),
        headers: Default::default(),
        invoke_key: INVOKE_KEY.to_string(),
    }
}

#[test]
fn shadow_write_router_passes_other_invokes_through() {
    // 其它命令、以及取不出合法参数的影子写,原样交给命令总表(这里用一个回显总表代替)
    let context = super::build_app_context::<tauri::test::MockRuntime>();
    let app = mock_builder()
        .invoke_handler(super::shadow_write_off_main_handler(
            |invoke: tauri::ipc::Invoke<tauri::test::MockRuntime>| {
                let cmd = invoke.message.command().to_string();
                invoke.resolver.resolve(format!("table:{cmd}"));
                true
            },
        ))
        .build(context)
        .expect("mock app");
    let webview =
        tauri::WebviewWindowBuilder::new(&app, super::MAIN_WINDOW_LABEL, Default::default())
            .build()
            .expect("main webview");
    for (cmd, body) in [
        ("app_version_local_command", serde_json::json!({})),
        (
            "shadow_store_write_command",
            serde_json::json!({ "key": "../x", "text": "[]" }),
        ),
        (
            "shadow_store_write_command",
            serde_json::json!({ "key": "horosa.localCharts.v1" }),
        ),
    ] {
        let got = get_ipc_response(&webview, request(cmd, body))
            .expect("回显总表应收到")
            .deserialize::<String>()
            .unwrap();
        assert_eq!(got, format!("table:{cmd}"));
    }
}

#[test]
fn packaged_context_has_no_global_tauri_and_event_listen_is_acl_denied() {
    let context = super::build_app_context::<tauri::test::MockRuntime>();
    assert!(
        !context.config().app.with_global_tauri,
        "withGlobalTauri 必须保持缺省 false:壳→页面通道走 eval 回调,不开全局 API 面"
    );
    // 不挂应用命令(它们按 Wry 运行时签名,MockRuntime 挂不上;本测只需核心插件命令的 ACL 判定)
    let app = mock_builder().build(context).expect("mock app");
    let webview =
        tauri::WebviewWindowBuilder::new(&app, super::MAIN_WINDOW_LABEL, Default::default())
            .build()
            .expect("main webview");
    let listen = get_ipc_response(
        &webview,
        request(
            "plugin:event|listen",
            serde_json::json!({ "event": "horosa://auto-backup-tick", "target": { "kind": "Any" }, "handler": 1 }),
        ),
    );
    let err = listen.expect_err("plugin:event|listen 必须被 ACL 拒绝(无 capabilities)");
    let msg = err.to_string();
    assert!(
        msg.contains("not allowed"),
        "拒绝理由应是 ACL not allowed, got: {msg}"
    );
}

#[test]
fn scheduler_tick_script_calls_handler_or_queues() {
    let s = super::scheduler_tick_script("{\"seq\":7,\"at\":9}");
    assert!(s.contains("window.__horosaSchedulerTick"));
    assert!(s.contains("__horosaPendingSchedulerTicks"));
    assert!(s.contains("{\"seq\":7,\"at\":9}"));
    assert!(!s.contains("emit("), "不得依赖 event emit");
    // pending 上限字面值 1 与页面侧 agentScheduler.test.js 的同构模拟一致;改上限两侧同改
    assert!(s.contains("q.length>1"), "pending 上限字面值 1 漂移");
    assert!(s.contains("q.splice(0,q.length-1)"), "超限须只留最新 1 条");
}

#[test]
fn scheduler_kill_switch_only_on_zero() {
    std::env::remove_var("HOROSA_SCHEDULER");
    assert!(!super::scheduler_kill_switch());
    std::env::set_var("HOROSA_SCHEDULER", "1");
    assert!(!super::scheduler_kill_switch());
    std::env::set_var("HOROSA_SCHEDULER", " 0 ");
    assert!(super::scheduler_kill_switch());
    std::env::remove_var("HOROSA_SCHEDULER");
}

#[test]
fn auto_backup_tick_script_calls_handler_or_queues() {
    let s = super::auto_backup_tick_script("{\"seq\":1,\"at\":2}");
    assert!(s.contains("window.__horosaAutoBackupTick"));
    assert!(s.contains("__horosaPendingAutoBackupTicks"));
    assert!(s.contains("{\"seq\":1,\"at\":2}"));
    assert!(!s.contains("emit("), "不得再依赖 event emit");
    // pending 队列上限字面值 8 与页面侧 autoBackupBridge.test.js 的复算一致;改上限两侧同改
    assert!(s.contains("q.length>8"), "pending 上限字面值 8 漂移");
    assert!(
        s.contains("q.splice(0,q.length-8)"),
        "超限须裁掉最旧、留最新 8 条"
    );
}
