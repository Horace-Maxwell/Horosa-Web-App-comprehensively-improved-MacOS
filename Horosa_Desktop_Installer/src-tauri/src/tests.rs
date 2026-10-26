use super::*;

// 偏好口被占必须走 +1 阶梯而非随机漂移 —— localStorage/IndexedDB 按 origin
// (含端口)分域,漂移=本地缓存/偏好「看起来清零」。
// stop 端口 env 注入:漏任一键,stop 脚本按默认口寻址,动态口会话在该路径必留后台进程。
#[test]
fn stop_ports_env_injection_is_complete() {
    let mut command = Command::new("/bin/true");
    apply_stop_ports_env(&mut command, Some((61632, 61633, 38991)));
    let envs: std::collections::HashMap<String, String> = command
        .get_envs()
        .filter_map(|(k, v)| {
            Some((
                k.to_string_lossy().to_string(),
                v?.to_string_lossy().to_string(),
            ))
        })
        .collect();
    assert_eq!(
        envs.get("HOROSA_SERVER_PORT").map(String::as_str),
        Some("61632")
    );
    assert_eq!(
        envs.get("HOROSA_CHART_PORT").map(String::as_str),
        Some("61633")
    );
    assert_eq!(
        envs.get("HOROSA_WEB_PORT").map(String::as_str),
        Some("38991")
    );
    // None = 不注入(脚本回默认口行为,兼容手工调用)
    let mut bare = Command::new("/bin/true");
    apply_stop_ports_env(&mut bare, None);
    assert_eq!(bare.get_envs().count(), 0);
}

// panic 停服补给槽:引导 / 重启刷新后,panic 钩子读到的必须是最新端口。
/// panic 停服补给的三处接线:引导成功与自动重启换口都刷新端口槽,panic 钩子把槽里的端口交给 stop 脚本。
#[test]
fn panic_stop_ports_wiring_in_bootstrap_restart_and_hook() {
    let src = concat!(include_str!("bootstrap.rs"), include_str!("services.rs"));
    let body_of = |name: &str| -> &str {
        let at = src.find(name).unwrap_or_else(|| panic!("缺 {name}"));
        let end = at + src[at..].find("\n}\n").expect("函数没收尾");
        &src[at..end]
    };
    assert!(body_of("fn runtime_bootstrap(")
        .contains("set_panic_stop_ports(backend_port, chart_port, web_port);"));
    assert!(body_of("fn restart_local_services_inner(")
        .contains("set_panic_stop_ports(backend_port, chart_port, session.web_port);"));
    let hook = body_of("fn register_panic_runtime_cleanup(");
    assert!(hook.contains("PANIC_STOP_PORTS.lock()"));
    assert!(hook.contains("apply_stop_ports_env(&mut command, ports);"));
}

#[test]
fn panic_stop_ports_slot_refreshes() {
    set_panic_stop_ports(50001, 50002, 38991);
    assert_eq!(
        PANIC_STOP_PORTS.lock().ok().and_then(|s| *s),
        Some((50001, 50002, 38991))
    );
    set_panic_stop_ports(50011, 50012, 38992);
    assert_eq!(
        PANIC_STOP_PORTS.lock().ok().and_then(|s| *s),
        Some((50011, 50012, 38992))
    );
}

#[test]
fn web_port_ladder_steps_instead_of_random_drift() {
    let preferred: u16 = 48991;
    let idle = choose_port_with_preference(preferred).expect("choose idle");
    assert_eq!(idle, preferred, "空闲时必须拿到偏好口");
    let _hold = TcpListener::bind(("127.0.0.1", preferred)).expect("hold preferred");
    let stepped = choose_port_with_preference(preferred).expect("choose stepped");
    assert_eq!(stepped, preferred + 1, "偏好口被占应顺位 +1,不得随机漂移");
}

fn static_test_dir(tag: &str) -> PathBuf {
    let uniq = SystemTime::now()
        .duration_since(UNIX_EPOCH)
        .map(|d| d.as_nanos())
        .unwrap_or(0);
    let d = std::env::temp_dir().join(format!(
        "horosa-static-{}-{}-{}",
        tag,
        std::process::id(),
        uniq
    ));
    fs::create_dir_all(d.join("web")).expect("mk web");
    fs::create_dir_all(d.join("outside")).expect("mk outside");
    fs::write(d.join("web").join("index.html"), b"<html>INDEX</html>").expect("index");
    fs::write(d.join("web").join("a.js"), b"console.log(1)").expect("a.js");
    fs::write(d.join("outside").join("secret.txt"), b"TOP-SECRET").expect("secret");
    d
}

fn raw_http_get(port: u16, path: &str, host: &str) -> (u16, String) {
    use std::io::{Read as _, Write as _};
    let mut s = std::net::TcpStream::connect(("127.0.0.1", port)).expect("connect");
    s.set_read_timeout(Some(Duration::from_secs(5))).ok();
    let req = format!(
        "GET {} HTTP/1.1\r\nHost: {}\r\nConnection: close\r\n\r\n",
        path, host
    );
    s.write_all(req.as_bytes()).expect("write");
    let mut buf = Vec::new();
    let _ = s.read_to_end(&mut buf);
    let text = String::from_utf8_lossy(&buf).to_string();
    let code = text
        .split_whitespace()
        .nth(1)
        .and_then(|c| c.parse::<u16>().ok())
        .unwrap_or(0);
    (code, text)
}

// 同一进程里再次引导(重装运行时 / 重启失败后的回退修复):本进程上一台静态服务器还占着原口时,
// 必须先把它收掉、沿用原口 —— 落到下一个口 = 页面换 origin = 本地数据整体「不见了」。连续两次都要守住。
#[test]
fn rebootstrap_keeps_web_port_when_own_static_server_still_listening() {
    let d = static_test_dir("rebootstrap");
    let port = choose_port_with_preference(47991).expect("pick base");
    let first = Arc::new(AtomicBool::new(false));
    let _h1 = start_static_server(d.join("web"), port, first.clone()).expect("first server");
    assert!(probe_local_port(port), "第一台服务器应在听");
    let slot: Mutex<Option<Arc<AtomicBool>>> = Mutex::new(Some(first.clone()));
    // 第二次引导
    let again = pick_web_port_for_bootstrap(&slot, Some(port)).expect("second pick");
    assert!(first.load(Ordering::SeqCst), "旧服务器的关停旗标必须先置位");
    assert_eq!(again, port, "再次引导必须沿用原前端口(origin 不变)");
    let second = Arc::new(AtomicBool::new(false));
    let _h2 = start_static_server(d.join("web"), again, second.clone()).expect("second server");
    replace_web_shutdown(&slot, Some(second.clone()));
    // 第三次引导
    let third = pick_web_port_for_bootstrap(&slot, Some(again)).expect("third pick");
    assert!(second.load(Ordering::SeqCst), "第二台的旗标同样要置位");
    assert_eq!(third, port, "连续两次再引导,前端口都不变");
    let _ = fs::remove_dir_all(&d);
}

// 引导选口接线:runtime_bootstrap 必须经 pick_web_port_for_bootstrap(沿用旧会话口、先收旧服务器),
// 绑定竞态重试走阶梯,旗标换新走 replace_web_shutdown。
#[test]
fn runtime_bootstrap_web_port_wiring() {
    let src = include_str!("bootstrap.rs");
    let at = src
        .find("fn runtime_bootstrap(")
        .expect("runtime_bootstrap");
    let end = at
        + src[at..]
            .find("let mut backend_port")
            .expect("backend port");
    let body = &src[at..end];
    assert!(body.contains("pick_web_port_for_bootstrap(&state.web_shutdown, previous_web_port)"));
    assert!(body.contains("retry_web_port_after_bind_race(preferred_web_port)"));
    assert!(!body.contains("web_port = choose_free_port()"));
    let tail = &src[end..end + 2000];
    assert!(tail.contains("replace_web_shutdown(&state.web_shutdown, Some(shutdown));"));
}

// 绑定竞态后的重试仍走阶梯(首选口被占 → +1),不跳随机口:随机口的实例页面既不当主实例、也不当阶梯上的独立实例。
#[test]
fn bind_race_retry_stays_on_port_ladder() {
    let preferred = choose_port_with_preference(45991).expect("pick base");
    let _hold = TcpListener::bind(("127.0.0.1", preferred)).expect("hold");
    let retried = retry_web_port_after_bind_race(preferred).expect("retry");
    assert!(
        retried > preferred && retried <= preferred + 8,
        "重试应落在阶梯上,得到 {retried}(首选 {preferred})"
    );
}

#[test]
fn replace_web_shutdown_retires_previous_flag() {
    let old = Arc::new(AtomicBool::new(false));
    let slot: Mutex<Option<Arc<AtomicBool>>> = Mutex::new(Some(old.clone()));
    let next = Arc::new(AtomicBool::new(false));
    replace_web_shutdown(&slot, Some(next.clone()));
    assert!(
        old.load(Ordering::SeqCst),
        "被换下的旧旗标必须置 true(否则旧服务器泄漏)"
    );
    assert!(!next.load(Ordering::SeqCst));
    assert!(Arc::ptr_eq(slot.lock().unwrap().as_ref().unwrap(), &next));
}

#[test]
fn static_rel_path_rejects_traversal_forms() {
    for ok in ["index.html", "a.js", "static/umi.1234abcd.js", "./a.js"] {
        assert!(static_rel_path_is_safe(ok), "{ok}");
    }
    for bad in [
        "",
        "../etc/hosts",
        "a/../../etc/hosts",
        "..",
        "%2e%2e/etc/hosts",
        "%2E%2e/etc/hosts",
        "..%2fetc%2fhosts",
        "a%5c..%5cb",
        "/etc/hosts",
        "a\\..\\b",
        "a\0b",
        "a%00.js",
    ] {
        assert!(!static_rel_path_is_safe(bad), "{bad:?}");
    }
}

#[test]
fn static_target_stays_inside_frontend_dir() {
    let d = static_test_dir("resolve");
    let web = d.join("web");
    std::os::unix::fs::symlink(d.join("outside").join("secret.txt"), web.join("link.txt"))
        .expect("file symlink");
    std::os::unix::fs::symlink(d.join("outside"), web.join("sub")).expect("dir symlink");
    let root = fs::canonicalize(&web).expect("canon");
    assert_eq!(
        resolve_static_target(&web, Some(&root), "a.js"),
        Some(web.join("a.js"))
    );
    assert_eq!(
        resolve_static_target(&web, Some(&root), "missing/route"),
        Some(web.join("index.html")),
        "不存在只回落 index.html"
    );
    assert_eq!(
        resolve_static_target(&web, Some(&root), "../outside/secret.txt"),
        None
    );
    assert_eq!(
        resolve_static_target(&web, Some(&root), "link.txt"),
        None,
        "文件符号链接出界"
    );
    assert_eq!(
        resolve_static_target(&web, Some(&root), "sub/secret.txt"),
        None,
        "目录符号链接出界"
    );
    assert_eq!(
        resolve_static_target(&web, None, "a.js"),
        Some(web.join("a.js")),
        "没有预取的根也能现取"
    );
    let _ = fs::remove_dir_all(&d);
}

#[test]
fn static_host_header_allows_loopback_only() {
    for ok in [
        None,
        Some("127.0.0.1:38991"),
        Some("127.0.0.1"),
        Some("localhost:38991"),
        Some("LOCALHOST"),
        Some("[::1]:38991"),
    ] {
        assert!(static_host_allowed(ok), "{ok:?}");
    }
    for bad in [
        Some("evil.example:38991"),
        Some("127.0.0.1.evil.example"),
        Some(""),
        Some("[::2]:1"),
    ] {
        assert!(!static_host_allowed(bad), "{bad:?}");
    }
}

// 真服务器端到端:请求行里的 `../` / 编码点 / 符号链接都读不到前端目录外的文件;外来 Host 拒。
#[test]
fn static_server_refuses_traversal_requests() {
    let d = static_test_dir("server");
    let web = d.join("web");
    std::os::unix::fs::symlink(d.join("outside").join("secret.txt"), web.join("link.txt"))
        .expect("file symlink");
    let port = choose_port_with_preference(46991).expect("pick");
    let stop = Arc::new(AtomicBool::new(false));
    let _h = start_static_server(web.clone(), port, stop.clone()).expect("server");
    let (code, body) = raw_http_get(port, "/a.js", "127.0.0.1");
    assert_eq!(code, 200, "{body}");
    for path in [
        "/../outside/secret.txt",
        "/../../../../../../../../../../../../../etc/hosts",
        "/%2e%2e/outside/secret.txt",
        "/link.txt",
    ] {
        let (code, body) = raw_http_get(port, path, "127.0.0.1");
        assert_eq!(code, 404, "{path}: {body}");
        assert!(!body.contains("TOP-SECRET"), "{path} 泄出了目录外文件");
    }
    let (code, _) = raw_http_get(port, "/a.js", "evil.example");
    assert_eq!(code, 403, "外来 Host 应拒");
    let (code, body) = raw_http_get(port, "/some/spa/route", "localhost:1");
    assert_eq!(code, 200);
    assert!(body.contains("INDEX"), "不存在的路径回落 index.html");
    stop.store(true, Ordering::SeqCst);
    let _ = fs::remove_dir_all(&d);
}

// 前端上报的账本段名只认 web.[a-z0-9_]{1,40}:页面无法伪造 rust./sh. 段、无法写超长段名。
#[test]
fn early_nav_url_marks_post_update_first_launch() {
    let normal = early_nav_url(7998, 9999, 8899, false);
    assert!(normal.contains("&early=1"));
    assert!(!normal.contains("firstLaunch=1"));
    let post = early_nav_url(7998, 9999, 8899, true);
    assert!(post.contains("&early=1"));
    assert!(post.contains("&firstLaunch=1"));
    assert!(post.starts_with("http://127.0.0.1:7998/index.html?"));
}

#[test]
fn web_ledger_seg_name_is_validated() {
    for ok in ["web.umi_exec", "web.first_render", "web.a1_b2"] {
        assert!(web_ledger_seg_ok(ok), "{ok}");
    }
    let too_long = format!("web.{}", "a".repeat(41));
    for bad in [
        "rust.emit_ready",
        "web.",
        "web.Bad",
        "web.a-b",
        "",
        too_long.as_str(),
    ] {
        assert!(!web_ledger_seg_ok(bad), "{bad}");
    }
}

// init 脚本必须带「同参二次 ready 不重载」的 __horosaReady 实现,且比对
// srv/chartSrv/kentangSrv 三键并置 __horosaBackendConfirmed —— 缺任一,早导航后的
// 收尾 ready 会整页重载(并行启动收益清零)或前端 boot-gate 收不到就绪短路信号。
#[test]
fn desktop_init_script_has_same_target_ready_guard() {
    assert!(DESKTOP_WINDOW_INIT_SCRIPT.contains("window.__horosaReady = function"));
    assert!(DESKTOP_WINDOW_INIT_SCRIPT.contains("__horosaBackendConfirmed"));
    // 同参确认必须同时派事件,前端就绪门等待者靠它即时放行(不等下一次探活)
    assert!(DESKTOP_WINDOW_INIT_SCRIPT.contains("horosa:backend-confirmed"));
    for key in ["\"srv\"", "\"chartSrv\"", "\"kentangSrv\"", "\"rv\""] {
        assert!(
            DESKTOP_WINDOW_INIT_SCRIPT.contains(key),
            "init script missing compare key {key}"
        );
    }
    assert!(DESKTOP_WINDOW_INIT_SCRIPT.contains("window.location.replace(url)"));
}

// [zoom-snap] 缩放档归一单测:f64 累加脏值必须吸回 0.1 档(⌘0 清理分支依赖精确 1.0)。
// 缩放上限随窗口宽度封顶:布局视口宽 ≥ 1000 CSS px。
#[test]
fn zoom_cap_follows_window_width() {
    assert_eq!(max_zoom_for_width(1440.0), 1.4);
    assert_eq!(max_zoom_for_width(1728.0), 1.7);
    assert_eq!(max_zoom_for_width(3008.0), MAX_ZOOM);
    assert_eq!(max_zoom_for_width(1180.0), 1.1);
    assert_eq!(max_zoom_for_width(1000.0), 1.0);
    // 比 1000 还窄的窗:夹到下限,永不为 0 / 负数
    assert_eq!(max_zoom_for_width(600.0), MIN_ZOOM);
    // 量不到尺寸 → 无封顶,不把用户缩回去
    assert_eq!(max_zoom_for_width(0.0), MAX_ZOOM);
    assert_eq!(max_zoom_for_width(f64::NAN), MAX_ZOOM);
}

#[test]
fn zoom_snap_normalizes_float_drift() {
    // ⌘± 累加路径:0.7 + 0.1*3 在 f64 上 ≠ 1.0,snap 后必须精确等于 1.0
    let accumulated = 0.7_f64 + 0.1 + 0.1 + 0.1;
    assert!(accumulated != 1.0, "前提:f64 累加确实产生漂移");
    assert_eq!(clamp_zoom_level(accumulated), 1.0);
    // 历史 prefs 实锤脏值
    assert_eq!(clamp_zoom_level(0.899_999_999_999_999_9), 0.9);
    assert_eq!(clamp_zoom_level(1.000_000_000_000_000_2), 1.0);
    // 越界仍 clamp 到 [MIN_ZOOM, MAX_ZOOM]
    assert_eq!(clamp_zoom_level(0.05), MIN_ZOOM);
    assert_eq!(clamp_zoom_level(9.9), MAX_ZOOM);
    // 正常档位不动
    assert_eq!(clamp_zoom_level(1.3), 1.3);
}
use flate2::write::GzEncoder;
use flate2::Compression;
use std::fs;
#[cfg(unix)]
use std::os::unix::fs::PermissionsExt;
use std::process::Command;
use tar::Builder;

// UTF-8 roundtrip:主路 arboard 与兜底 pbcopy(LC_CTYPE 钉死)两路合一,
// 防 cargo test 并行互踩全局剪贴板;先存后还,尽量不打扰开发者剪贴板。
// 读侧 pbpaste 同样要钉 LC_CTYPE:无 locale 时读侧也按 MacRoman 转码输出。
#[test]
#[cfg(target_os = "macos")]
fn clipboard_utf8_roundtrip_native_and_pbcopy() {
    let sample = "技术·測試 ✓ 三式合一";
    let saved = arboard::Clipboard::new()
        .ok()
        .and_then(|mut c| c.get_text().ok());

    // ① arboard 主路
    let mut clip = arboard::Clipboard::new().expect("arboard 初始化失败");
    clip.set_text(sample.to_string()).expect("arboard 写入失败");
    assert_eq!(clip.get_text().expect("arboard 读回失败"), sample);
    drop(clip);

    // ② pbcopy 兜底
    pbcopy_utf8_fallback(sample).expect("pbcopy 兜底写入失败");
    let out = Command::new("/usr/bin/pbpaste")
        .env("LC_CTYPE", "UTF-8")
        .output()
        .expect("pbpaste 执行失败");
    assert_eq!(String::from_utf8_lossy(&out.stdout), sample);

    if let (Some(prev), Ok(mut c)) = (saved, arboard::Clipboard::new()) {
        let _ = c.set_text(prev);
    }
}

// 单调判定矩阵:remote 更新才更;更旧被拦;rank 等价不重复下载;
// 逃生阀恢复老「不同即更」语义;合成串(GithubApi 无 -runtimeN)同 base 视作更旧修订被拦。
#[test]
fn runtime_update_monotonic_gate() {
    use RuntimeUpdateDecision::*;
    let d = compute_runtime_update_decision;
    assert_eq!(
        d(Some("3.3.3-runtime1"), Some("3.3.2-runtime1"), false),
        Needed
    );
    // runtime 修订位数值序(非字典序):-runtime10 > -runtime2
    assert_eq!(
        d(Some("3.3.2-runtime10"), Some("3.3.2-runtime2"), false),
        Needed
    );
    assert_eq!(
        d(Some("3.3.2-runtime2"), Some("3.3.2-runtime10"), false),
        DowngradeBlocked
    );
    // 字符串不同但 rank 等价 → 视为已最新(不重复下载)
    assert_eq!(
        d(Some("3.3.2-runtime1"), Some("3.3.2-runtime01"), false),
        UpToDate
    );
    assert_eq!(
        d(Some("3.3.2-runtime1"), Some("3.3.2-runtime1"), false),
        UpToDate
    );
    // 远端更旧 → 拦;逃生阀放行
    assert_eq!(
        d(Some("3.3.1-runtime9"), Some("3.3.2-runtime1"), false),
        DowngradeBlocked
    );
    assert_eq!(
        d(Some("3.3.1-runtime9"), Some("3.3.2-runtime1"), true),
        Needed
    );
    // 本地无 runtime → 必装;远端无字段 → 不更
    assert_eq!(d(Some("3.3.2-runtime1"), None, false), Needed);
    assert_eq!(d(None, Some("3.3.2-runtime1"), false), UpToDate);
    // GithubApi 合成串(裸版本号):同 base 视作更旧修订 → 拦(避免无谓整包重下)
    assert_eq!(
        d(Some("3.3.2"), Some("3.3.2-runtime1"), false),
        DowngradeBlocked
    );
    assert_eq!(d(Some("3.3.3"), Some("3.3.2-runtime1"), false), Needed);
}

#[test]
fn runtime_needs_update_unparseable_falls_back_to_neq() {
    use RuntimeUpdateDecision::*;
    // 任一侧 rank 解析失败 → 回退「不同即更」(防脏版本串永久卡死更新链)
    assert_eq!(
        compute_runtime_update_decision(Some("weird-tag"), Some("3.3.2-runtime1"), false),
        Needed
    );
    assert_eq!(
        compute_runtime_update_decision(Some("3.3.3-runtime1"), Some("corrupted"), false),
        Needed
    );
    // 双侧相同脏串 → 字符串相等短路,视为最新
    assert_eq!(
        compute_runtime_update_decision(Some("weird"), Some("weird"), false),
        UpToDate
    );
}

// 撕裂测试用最小「完整」runtime 树(过 runtime_dir_has_required_files 五文件判据)
fn write_minimal_runtime_tree(dir: &Path, marker: &str) {
    fs::create_dir_all(dir.join("Horosa-Web/astrostudyui/dist-file")).unwrap();
    fs::create_dir_all(dir.join("runtime/mac/python/bin")).unwrap();
    fs::create_dir_all(dir.join("runtime/mac/java/bin")).unwrap();
    fs::write(
        dir.join("runtime-manifest.json"),
        format!("{{\"version\":\"{}\"}}\n", marker),
    )
    .unwrap();
    fs::write(
        dir.join("Horosa-Web/start_horosa_local.sh"),
        "#!/bin/bash\n",
    )
    .unwrap();
    fs::write(
        dir.join("Horosa-Web/astrostudyui/dist-file/index.html"),
        marker,
    )
    .unwrap();
    fs::write(dir.join("runtime/mac/python/bin/python3"), "stub").unwrap();
    fs::write(dir.join("runtime/mac/java/bin/java"), "stub").unwrap();
}

#[test]
fn atomic_swap_dirs_exchanges_trees_on_apfs() {
    let work = temp_test_dir("swap");
    let a = work.join("a");
    let b = work.join("b");
    fs::create_dir_all(&a).unwrap();
    fs::create_dir_all(&b).unwrap();
    fs::write(a.join("who.txt"), "aaa").unwrap();
    fs::write(b.join("who.txt"), "bbb").unwrap();
    let swapped = atomic_swap_dirs(&a, &b).expect("swap 调用不应报错");
    assert!(swapped, "本机 temp 卷应为 APFS,renamex_np 必须可用");
    assert_eq!(fs::read_to_string(a.join("who.txt")).unwrap(), "bbb");
    assert_eq!(fs::read_to_string(b.join("who.txt")).unwrap(), "aaa");
    // 禁用开关必须走回退分支(防两段 rename 回退路径死代码化)
    std::env::set_var("HOROSA_SWAP_DISABLE", "1");
    let disabled = atomic_swap_dirs(&a, &b).unwrap();
    std::env::remove_var("HOROSA_SWAP_DISABLE");
    assert!(!disabled, "HOROSA_SWAP_DISABLE=1 必须返回 false 走回退");
    let _ = fs::remove_dir_all(&work);
}

#[test]
fn torn_slot_repair_promotes_complete_candidate() {
    // 场景1:current 缺失 + 仅 previous 完整 → 收养 previous
    let root1 = temp_test_dir("torn1");
    write_minimal_runtime_tree(&root1.join("previous"), "prev");
    assert!(repair_torn_runtime_slots(&root1).unwrap());
    assert!(root1.join("current/runtime-manifest.json").exists());
    assert!(!root1.join("previous").exists());

    // 场景2:_comp_stage(增量暂存,最新)优先于 previous;previous 保留作回滚资本
    let root2 = temp_test_dir("torn2");
    write_minimal_runtime_tree(&root2.join("_comp_stage"), "stage");
    write_minimal_runtime_tree(&root2.join("previous"), "prev");
    assert!(repair_torn_runtime_slots(&root2).unwrap());
    assert_eq!(
        fs::read_to_string(root2.join("current/Horosa-Web/astrostudyui/dist-file/index.html"))
            .unwrap(),
        "stage"
    );
    assert!(root2.join("previous").exists());

    // 场景3:_extract/runtime-payload(全量暂存)次优
    let root3 = temp_test_dir("torn3");
    write_minimal_runtime_tree(&root3.join("_extract/runtime-payload"), "extract");
    assert!(repair_torn_runtime_slots(&root3).unwrap());
    assert_eq!(
        fs::read_to_string(root3.join("current/Horosa-Web/astrostudyui/dist-file/index.html"))
            .unwrap(),
        "extract"
    );

    // 场景4:候选不完整(缺 java)绝不收养
    let root4 = temp_test_dir("torn4");
    write_minimal_runtime_tree(&root4.join("previous"), "broken");
    fs::remove_file(root4.join("previous/runtime/mac/java/bin/java")).unwrap();
    assert!(!repair_torn_runtime_slots(&root4).unwrap());
    assert!(!root4.join("current").exists());

    // 场景5:current 在位 → 零动作
    let root5 = temp_test_dir("torn5");
    write_minimal_runtime_tree(&root5.join("current"), "cur");
    write_minimal_runtime_tree(&root5.join("previous"), "prev");
    assert!(!repair_torn_runtime_slots(&root5).unwrap());
    assert_eq!(
        fs::read_to_string(root5.join("current/Horosa-Web/astrostudyui/dist-file/index.html"))
            .unwrap(),
        "cur"
    );
    for root in [root1, root2, root3, root4, root5] {
        let _ = fs::remove_dir_all(&root);
    }
}

// 部件级重试矩阵:下载错(留 .part 续传接力)/sha 失配(清 dest 全新下)/耗尽上抛
#[test]
fn component_download_retry_then_success_and_exhaust() {
    let work = temp_test_dir("comp-retry");
    let dest = work.join("comp-x.tar.gz");
    // fail(下载),fail(校验),ok → 成功;共 3 次下载、2 次重试通知
    let calls = std::cell::Cell::new(0u32);
    let retries = std::cell::Cell::new(0u32);
    let result = download_component_with_retry(
        &dest,
        &mut || {
            calls.set(calls.get() + 1);
            fs::write(&dest, format!("payload-{}", calls.get())).unwrap();
            if calls.get() == 1 {
                Err(anyhow!("network"))
            } else {
                Ok(())
            }
        },
        &mut || {
            if calls.get() == 2 {
                Err(anyhow!("sha mismatch"))
            } else {
                Ok(())
            }
        },
        &mut |_| retries.set(retries.get() + 1),
    );
    assert!(result.is_ok());
    assert_eq!(calls.get(), 3);
    assert_eq!(retries.get(), 2);

    // 持续 sha 失配 → 1+COMPONENT_RETRY_MAX 次后 Err,坏资产不残留
    let fails = std::cell::Cell::new(0u32);
    let result = download_component_with_retry(
        &dest,
        &mut || {
            fails.set(fails.get() + 1);
            Ok(())
        },
        &mut || Err(anyhow!("sha mismatch")),
        &mut |_| {},
    );
    assert!(result.is_err());
    assert_eq!(fails.get(), 1 + COMPONENT_RETRY_MAX);
    assert!(!dest.exists(), "sha 失配路径必须清掉坏资产");
    let _ = fs::remove_dir_all(&work);
}

// 节流三态:无 stamp=查;窗内=跳;窗外=查(interval 作参数传入,测试不碰 env)
#[test]
fn auto_check_throttle_gate() {
    let four_hours_ms: u64 = 4 * 3600 * 1000;
    let now: u64 = 1_000_000_000_000;
    assert!(should_run_auto_check(None, now, four_hours_ms));
    assert!(!should_run_auto_check(
        Some(now - 3 * 3600 * 1000),
        now,
        four_hours_ms
    ));
    assert!(should_run_auto_check(
        Some(now - 5 * 3600 * 1000),
        now,
        four_hours_ms
    ));
    // 恰在边界=可查;时钟倒拨(last>now)不 panic 且按窗内处理
    assert!(should_run_auto_check(
        Some(now - four_hours_ms),
        now,
        four_hours_ms
    ));
    assert!(!should_run_auto_check(
        Some(now + 60_000),
        now,
        four_hours_ms
    ));
}

#[test]
fn update_check_stamp_roundtrip() {
    let work = temp_test_dir("check-stamp");
    let path = work.join("last-update-check.json");
    assert_eq!(load_update_check_stamp(&path), None);
    write_update_check_stamp_at(&path);
    let loaded = load_update_check_stamp(&path).expect("stamp 应可读回");
    assert!(loaded > 0);
    // 坏 JSON → None(自愈:下轮照常检查并重写)
    fs::write(&path, "not-json").unwrap();
    assert_eq!(load_update_check_stamp(&path), None);
    let _ = fs::remove_dir_all(&work);
}

// staged 持久化门:往返/篡改一字节拒绝/复用门匹配
#[test]
fn staged_update_file_roundtrip_and_sha_gate() {
    let work = temp_test_dir("staged");
    let zip = work.join("app.zip");
    let comp = work.join("comp-web-app.tar.gz");
    fs::write(&zip, "zip-bytes").unwrap();
    fs::write(&comp, "comp-bytes").unwrap();
    let staged = StagedUpdate {
        zip_path: Some(zip.clone()),
        runtime_archive_path: None,
        runtime_roots: vec![work.join("root")],
        runtime_version: Some("9.9.9-runtime1".into()),
        target_version: "9.9.9".into(),
        app_should_update: true,
        runtime_should_update: true,
        staged_components: Some(StagedComponents {
            archives: vec![(
                ManifestComponent {
                    name: "web-app".into(),
                    kind: "tree".into(),
                    sha256: "x".into(),
                    size: Some(1),
                    file: "comp-web-app.tar.gz".into(),
                    url: String::new(),
                },
                comp.clone(),
            )],
            new_lock_json: serde_json::json!({"runtimeVersion":"9.9.9-runtime1"}),
            new_lock_text: "{}".into(),
        }),
    };
    let file = work.join("staged-update.json");
    persist_staged_update_file_at(&file, &staged).expect("持久化应成功");
    let now = SystemTime::now()
        .duration_since(UNIX_EPOCH)
        .unwrap()
        .as_millis() as u64;
    let loaded = load_staged_update_file_at(&file, now).expect("原样资产应可恢复");
    assert_eq!(loaded.target_version, "9.9.9");
    assert!(staged_matches_plan(
        &loaded,
        "9.9.9",
        &Some("9.9.9-runtime1".into())
    ));
    assert!(!staged_matches_plan(
        &loaded,
        "9.9.10",
        &Some("9.9.9-runtime1".into())
    ));
    assert!(!staged_matches_plan(
        &loaded,
        "9.9.9",
        &Some("9.9.9-runtime2".into())
    ));
    // 篡改一个资产字节 → 拒绝复用
    fs::write(&comp, "comp-bytes-tampered").unwrap();
    assert!(load_staged_update_file_at(&file, now).is_none());
    let _ = fs::remove_dir_all(&work);
}

#[test]
fn staged_update_expiry_discard() {
    let work = temp_test_dir("staged-exp");
    let zip = work.join("app.zip");
    fs::write(&zip, "zip").unwrap();
    let staged = StagedUpdate {
        zip_path: Some(zip),
        runtime_archive_path: None,
        runtime_roots: vec![],
        runtime_version: None,
        target_version: "9.9.9".into(),
        app_should_update: true,
        runtime_should_update: false,
        staged_components: None,
    };
    let file = work.join("staged-update.json");
    persist_staged_update_file_at(&file, &staged).unwrap();
    let now = SystemTime::now()
        .duration_since(UNIX_EPOCH)
        .unwrap()
        .as_millis() as u64;
    assert!(load_staged_update_file_at(&file, now).is_some());
    // 8 天后 → 过期废弃
    assert!(load_staged_update_file_at(&file, now + 8 * 24 * 3600 * 1000).is_none());
    // 无资产清单的档(异常构造)→ 拒绝
    fs::write(
        &file,
        serde_json::json!({
            "saved_at_ms": now,
            "staged": { "target_version": "9.9.9" },
            "asset_shas": []
        })
        .to_string(),
    )
    .unwrap();
    assert!(load_staged_update_file_at(&file, now).is_none());
    let _ = fs::remove_dir_all(&work);
}

// 身份探针四分类:真 TcpListener 假服务(正确 JSON/陌生标记/不答话/不监听)
#[test]
fn identity_probe_classifies_squatter_and_silence() {
    use std::io::{Read, Write};
    let timeout = Duration::from_millis(800);
    // Ok:回正确身份 JSON(app 标记+nonce 全对)
    let ok_listener = std::net::TcpListener::bind("127.0.0.1:0").unwrap();
    let ok_port = ok_listener.local_addr().unwrap().port();
    let ok_thread = thread::spawn(move || {
        if let Ok((mut s, _)) = ok_listener.accept() {
            let mut buf = [0u8; 1024];
            let _ = s.read(&mut buf);
            let body = r#"{"app":"horosa-backend","proto":1,"nonce":"n-1"}"#;
            let resp = format!(
                "HTTP/1.1 200 OK\r\nContent-Type: application/json\r\nContent-Length: {}\r\nConnection: close\r\n\r\n{}",
                body.len(),
                body
            );
            let _ = s.write_all(resp.as_bytes());
        }
    });
    assert_eq!(
        probe_identity(ok_port, "horosa-backend", "n-1", timeout, false),
        IdentityProbe::Ok
    );
    ok_thread.join().unwrap();

    // WrongIdentity:陌生 app 标记(毒 200 squatter)/ nonce 不符(别的实例)
    let sq = std::net::TcpListener::bind("127.0.0.1:0").unwrap();
    let sq_port = sq.local_addr().unwrap().port();
    let sq_thread = thread::spawn(move || {
        for _ in 0..2 {
            if let Ok((mut s, _)) = sq.accept() {
                let mut buf = [0u8; 1024];
                let _ = s.read(&mut buf);
                let body = r#"{"app":"stranger","nonce":"zzz"}"#;
                let resp = format!(
                    "HTTP/1.1 200 OK\r\nContent-Length: {}\r\nConnection: close\r\n\r\n{}",
                    body.len(),
                    body
                );
                let _ = s.write_all(resp.as_bytes());
            }
        }
    });
    assert_eq!(
        probe_identity(sq_port, "horosa-backend", "n-1", timeout, false),
        IdentityProbe::WrongIdentity
    );
    assert_eq!(
        probe_identity(sq_port, "stranger", "n-1", timeout, false),
        IdentityProbe::WrongIdentity
    );
    sq_thread.join().unwrap();

    // HttpSilent:端口在听但不答话(wedged 形态)
    let silent = std::net::TcpListener::bind("127.0.0.1:0").unwrap();
    let silent_port = silent.local_addr().unwrap().port();
    let silent_thread = thread::spawn(move || {
        if let Ok((s, _)) = silent.accept() {
            thread::sleep(Duration::from_millis(1200));
            drop(s);
        }
    });
    assert_eq!(
        probe_identity(silent_port, "horosa-backend", "n-1", timeout, false),
        IdentityProbe::HttpSilent
    );
    silent_thread.join().unwrap();

    // TcpDead:无人监听
    let dead_port = {
        let l = std::net::TcpListener::bind("127.0.0.1:0").unwrap();
        l.local_addr().unwrap().port()
    };
    assert_eq!(
        probe_identity(dead_port, "horosa-backend", "n-1", timeout, false),
        IdentityProbe::TcpDead
    );
}

// 双 streak 状态机:快判/慢判/立即判/互清/Ok 归零
#[test]
fn supervisor_streak_state_machine() {
    let zero = SupervisorStreak::default();
    // Ok 全清零
    assert_eq!(
        supervisor_step(SupervisorStreak { dead: 1, silent: 3 }, IdentityProbe::Ok),
        (zero, false)
    );
    // TcpDead 连续 2 轮判亡
    let (s1, k1) = supervisor_step(zero, IdentityProbe::TcpDead);
    assert!(!k1);
    let (_, k2) = supervisor_step(s1, IdentityProbe::TcpDead);
    assert!(k2);
    // HttpSilent 连续 6 轮判亡
    let mut s = zero;
    for round in 1..=5u32 {
        let (next, kill) = supervisor_step(s, IdentityProbe::HttpSilent);
        s = next;
        assert!(!kill, "silent 第 {round} 轮不应判亡");
    }
    let (_, k6) = supervisor_step(s, IdentityProbe::HttpSilent);
    assert!(k6);
    // dead 与 silent 互清对方(交替抖动不误判)
    let (sd, _) = supervisor_step(
        SupervisorStreak { dead: 0, silent: 5 },
        IdentityProbe::TcpDead,
    );
    assert_eq!(sd.silent, 0);
    let (ss, _) = supervisor_step(
        SupervisorStreak { dead: 1, silent: 0 },
        IdentityProbe::HttpSilent,
    );
    assert_eq!(ss.dead, 0);
    // WrongIdentity 立即判亡
    assert!(supervisor_step(zero, IdentityProbe::WrongIdentity).1);
}

// helper 模板契约:stage-first 序/swap 旗标/失败重开臂/磁盘预检/危险旧序零回潮
#[test]
fn update_helper_script_stages_before_swap() {
    let script = build_update_helper_script(
        Path::new("/tmp/log.txt"),
        Path::new("/tmp/marker.txt"),
        Path::new("/Applications/Demo.app"),
        Path::new("/tmp/extract/Demo.app"),
        "501",
        "demo",
        "1234",
        "demo-exec",
        "9.9.9",
        Some("9.9.9-runtime1"),
        "",
    );
    // stage-first:ditto 到暂存位必须先于任何对 TARGET 的 mv(长拷贝期间 TARGET 不动)
    let stage_at = script
        .find("ditto \"${SRC}\" \"${STAGE_TARGET}\"")
        .expect("缺 stage ditto");
    let mv_target_at = script
        .find("mv \"${TARGET}\" \"${BACKUP_TARGET}\"")
        .expect("缺 mv 回退");
    assert!(
        stage_at < mv_target_at,
        "ditto 必须先于 mv TARGET(stage-first)"
    );
    assert!(script.contains("--horosa-atomic-swap"));
    assert!(script.contains("update-stage.app"));
    // 失败臂:install 失败必须重开旧 app(而非 set -e 静默中止)
    assert!(script.contains("if ! install_app; then"));
    assert!(script.contains("reopening previous app"));
    // 磁盘预检在位
    assert!(script.contains("insufficient disk space"));
    // 危险旧序(把新版长时间 ditto 直写 TARGET)不得回潮
    assert!(!script.contains("ditto \"${SRC}\" \"${TARGET}\""));
}

#[test]
fn atomic_swap_cli_flag_swaps_and_exits() {
    let work = temp_test_dir("swap-cli");
    let a = work.join("a.app");
    let b = work.join("b.app");
    fs::create_dir_all(&a).unwrap();
    fs::create_dir_all(&b).unwrap();
    fs::write(a.join("who.txt"), "new").unwrap();
    fs::write(b.join("who.txt"), "old").unwrap();
    assert_eq!(run_swap_cli(&a, &b), 0, "APFS 上应互换成功");
    assert_eq!(fs::read_to_string(b.join("who.txt")).unwrap(), "new");
    assert_eq!(fs::read_to_string(a.join("who.txt")).unwrap(), "old");
    // 入参路径缺失 → 2(helper 走 mv 回退的信号,非硬错误)
    assert_eq!(run_swap_cli(&work.join("nope"), &b), 2);
    let _ = fs::remove_dir_all(&work);
}

// 台账追加+保尾轮转:超 1MB 保尾 200 行,新行在、头行不在,ts/shellVersion 自动补
#[test]
fn update_history_append_and_rotation_keeps_tail() {
    let work = temp_test_dir("uhist");
    let path = work.join("update-history.jsonl");
    append_update_history_at(&path, serde_json::json!({ "event": "staged_ready" }));
    let text = fs::read_to_string(&path).unwrap();
    assert!(text.contains("\"event\":\"staged_ready\""));
    assert!(text.contains("\"ts\":"));
    assert!(text.contains("\"shellVersion\":"));
    // 灌 >1MB 再追加 → 只留尾部+新行
    let filler: String = (0..40000)
        .map(|i| format!("{{\"event\":\"filler\",\"n\":{i}}}\n"))
        .collect();
    fs::write(&path, filler).unwrap();
    assert!(fs::metadata(&path).unwrap().len() > 1024 * 1024);
    append_update_history_at(&path, serde_json::json!({ "event": "install_confirmed" }));
    let text = fs::read_to_string(&path).unwrap();
    let lines: Vec<&str> = text.lines().collect();
    assert!(lines.len() <= 201, "保尾 200+新 1 行,实际 {}", lines.len());
    assert!(text.contains("install_confirmed"));
    assert!(!text.contains("\"n\":0}"), "头行必须被轮转掉");
    assert!(text.contains("\"n\":39999"), "尾行必须保留");
    let _ = fs::remove_dir_all(&work);
}

// events 轮转保代:超限 rename→.1 保旧史(不再截断毁证)
#[test]
fn rotate_log_keep_one_generation() {
    let work = temp_test_dir("rotlog");
    let path = work.join("updater-events.log");
    fs::write(&path, "old-history\n".repeat(1000)).unwrap();
    // 未超限:不动
    rotate_log_keep_one(&path, 1024 * 1024);
    assert!(path.exists());
    assert!(!path.with_extension("log.1").exists());
    // 超限:rename → .1,主文件让位(调用方新建续写)
    rotate_log_keep_one(&path, 100);
    let older = path.with_extension("log.1");
    assert!(older.exists(), ".1 保代必须存在");
    assert!(!path.exists(), "主文件应让位");
    assert!(fs::read_to_string(&older).unwrap().contains("old-history"));
    let _ = fs::remove_dir_all(&work);
}

// 诊断包 ditto 实跑:zip 产出且内容在包内
#[test]
fn diagnostics_bundle_staging_collects_expected_files() {
    let work = temp_test_dir("diagzip");
    let staging = work.join("staging");
    fs::create_dir_all(staging.join("logs")).unwrap();
    fs::write(staging.join("logs/update-history.jsonl"), "{}\n").unwrap();
    fs::write(staging.join("system-info.txt"), "app=test\n").unwrap();
    let out = work.join("bundle.zip");
    zip_dir_with_ditto(&staging, &out).expect("ditto 打包应成功");
    assert!(out.exists());
    let listing = Command::new("/usr/bin/unzip")
        .arg("-l")
        .arg(&out)
        .output()
        .expect("unzip -l");
    let text = String::from_utf8_lossy(&listing.stdout);
    assert!(text.contains("update-history.jsonl"));
    assert!(text.contains("system-info.txt"));
    let _ = fs::remove_dir_all(&work);
}

#[test]
fn saved_window_state_accepts_legacy_json_without_maximize_flag() {
    let state: SavedWindowState =
        serde_json::from_str(r#"{"width":1480.0,"height":960.0,"x":120.0,"y":80.0}"#)
            .expect("deserialize legacy window state");

    assert_eq!(state.width, Some(1480.0));
    assert_eq!(state.height, Some(960.0));
    assert_eq!(state.x, Some(120.0));
    assert_eq!(state.y, Some(80.0));
    assert_eq!(state.is_maximized, None);
    assert_eq!(state.state_version, None);
    assert_eq!(state.coordinate_space, None);
}

#[test]
fn legacy_retina_window_state_migrates_physical_pixels_to_logical_size() {
    let state = SavedWindowState {
        width: Some(2960.0),
        height: Some(1920.0),
        x: Some(240.0),
        y: Some(160.0),
        is_maximized: Some(false),
        state_version: None,
        coordinate_space: None,
    };

    let normalized = normalize_saved_window_state_for_apply(&state, 2.0, Some(1512.0), Some(982.0));

    assert_eq!(normalized.width, Some(1480.0));
    assert_eq!(normalized.height, Some(932.0));
    assert_eq!(normalized.x, Some(120.0));
    assert_eq!(normalized.y, Some(80.0));
    assert_eq!(normalized.state_version, Some(WINDOW_STATE_SCHEMA_VERSION));
    assert_eq!(
        normalized.coordinate_space.as_deref(),
        Some(WINDOW_STATE_COORDINATE_SPACE)
    );
}

#[test]
fn logical_window_state_is_not_rescaled_on_retina_displays() {
    let state = SavedWindowState {
        width: Some(1480.0),
        height: Some(960.0),
        x: Some(120.0),
        y: Some(80.0),
        is_maximized: Some(false),
        state_version: Some(WINDOW_STATE_SCHEMA_VERSION),
        coordinate_space: Some(WINDOW_STATE_COORDINATE_SPACE.to_string()),
    };

    let normalized = normalize_saved_window_state_for_apply(&state, 2.0, Some(1512.0), Some(982.0));

    assert_eq!(normalized.width, Some(1480.0));
    assert_eq!(normalized.height, Some(960.0));
    assert_eq!(normalized.x, Some(120.0));
    assert_eq!(normalized.y, Some(80.0));
}

#[test]
fn invalid_scale_factor_falls_back_to_one() {
    assert_eq!(valid_scale_factor(0.0), 1.0);
    assert_eq!(valid_scale_factor(f64::NAN), 1.0);
    assert_eq!(logical_value(960.0, 0.0), 960.0);
}

/// 主窗每次页面载入完成(启动页与前端页)都按偏好重打一次缩放;幂等兜底。
#[test]
fn main_window_reapplies_zoom_after_each_page_load() {
    let src = include_str!("ui_windows.rs");
    let at = src
        .find("fn build_main_window(")
        .expect("缺 build_main_window");
    let body = &src[at..at + src[at..].find("\n}\n").expect("函数没收尾")];
    let hook = &body[body.find(".on_page_load(").expect("主窗没挂页面载入回调")..];
    assert!(hook.contains("PageLoadEvent::Finished"));
    assert!(hook.contains("load_preferences(&app).zoom_level"));
    assert!(hook.contains("set_window_zoom(&app, zoom)"));
}

#[test]
fn env_or_id_prefers_env_then_id_then_fallback() {
    let _env = HELPER_ENV_LOCK.lock().unwrap_or_else(|e| e.into_inner());
    let var = "ENV_OR_ID_PROBE";
    let id_uid = Command::new("/usr/bin/id")
        .arg("-u")
        .output()
        .map(|out| String::from_utf8_lossy(&out.stdout).trim().to_string())
        .expect("run id -u");
    std::env::set_var(var, "4242");
    assert_eq!(env_or_id(var, "-u", "0"), "4242");
    std::env::set_var(var, "   ");
    assert_eq!(env_or_id(var, "-u", "0"), id_uid);
    std::env::remove_var(var);
    assert_eq!(env_or_id(var, "-u", "0"), id_uid);
    assert_eq!(env_or_id(var, "--no-such-flag", "fallback"), "fallback");
    assert!(current_uid_string().parse::<u32>().is_ok());
    assert!(!current_user_string().trim().is_empty());
}

#[test]
fn shell_quote_path_matches_text_quoting() {
    let text = "/tmp/a \"b\"/星阙 c";
    assert_eq!(shell_quote(Path::new(text)), "\"/tmp/a \\\"b\\\"/星阙 c\"");
    assert_eq!(shell_quote(Path::new(text)), shell_quote_text(text));
}

#[test]
fn unix_ts_is_wall_clock_seconds() {
    let now = SystemTime::now()
        .duration_since(UNIX_EPOCH)
        .unwrap()
        .as_secs();
    let ts = unix_ts();
    assert!(ts + 2 >= now && ts <= now + 2, "{ts} vs {now}");
}

/// 发行构建编译期把构建机路径(用户目录 / cargo 注册表 / 工具链 / 壳源码目录)换成占位符,二进制里不留本机路径。
#[test]
fn release_build_remaps_builder_paths() {
    let script = fs::read_to_string(
        Path::new(env!("CARGO_MANIFEST_DIR")).join("../scripts/build_desktop_release.sh"),
    )
    .expect("read build script");
    for prefix in [
        "--remap-path-prefix=${HOME}/.cargo/registry=cargo",
        "--remap-path-prefix=${HOME}/.rustup/toolchains=rust",
        "--remap-path-prefix=${INSTALLER_ROOT}/src-tauri=src",
        "--remap-path-prefix=${HOME}=user",
    ] {
        assert!(script.contains(prefix), "缺 {prefix}");
    }
    let build_lines: Vec<&str> = script
        .lines()
        .filter(|line| line.contains("npm run tauri:build"))
        .collect();
    assert!(!build_lines.is_empty(), "缺 tauri 构建行");
    for line in build_lines {
        assert!(
            line.contains("RUSTFLAGS=\"${HOROSA_RUSTFLAGS_REMAP} ${RUSTFLAGS:-}\""),
            "构建行没带路径替换: {line}"
        );
    }
}

/// 离线 pkg 只内嵌 tar.gz 运行环境:本壳的自愈 / 清点 / 清理只认 tar.gz 缓存,构建脚本不留内嵌
/// tar.zst 的口子(装进去的 zst 缓存本壳用不上,也清不掉)。
#[test]
fn offline_pkg_embeds_gz_runtime_archive_only() {
    let script = fs::read_to_string(
        Path::new(env!("CARGO_MANIFEST_DIR")).join("../scripts/build_desktop_release.sh"),
    )
    .expect("read build script");
    assert!(!script.contains("HOROSA_OFFLINE_ZSTD"));
    let embed: Vec<&str> = script
        .lines()
        .map(str::trim)
        .filter(|line| {
            line.starts_with("OFFLINE_EMBED_ARCHIVE=") || line.starts_with("OFFLINE_EMBED_ASSET=")
        })
        .collect();
    assert_eq!(
        embed,
        vec![
            "OFFLINE_EMBED_ARCHIVE=\"${RUNTIME_ARCHIVE}\"",
            "OFFLINE_EMBED_ASSET=\"${RUNTIME_ASSET}\"",
        ]
    );
}

/// 主窗启动只按保存的尺寸 / 位置复原,从不走系统原生最大化(保存过「最大化」也一样)。
#[test]
fn main_window_launch_never_uses_native_maximize() {
    let src = include_str!("ui_windows.rs");
    let body_of = |name: &str| -> &str {
        let at = src.find(name).unwrap_or_else(|| panic!("缺 {name}"));
        let end = at + src[at..].find("\n}\n").expect("函数没收尾");
        &src[at..end]
    };
    for name in [
        "fn build_main_window(",
        "fn apply_main_window_launch_state(",
        "fn apply_saved_window_state(",
    ] {
        let body = body_of(name);
        assert!(!body.contains(".maximized("), "{name} 用了原生最大化");
        assert!(!body.contains(".maximize()"), "{name} 用了原生最大化");
    }
}

#[test]
fn captured_maximized_state_keeps_true_for_monitor_sized_bounds() {
    assert_eq!(
        effective_captured_maximized(
            Some(true),
            Some(1728.0),
            Some(1079.0),
            Some(1728.0),
            Some(1117.0)
        ),
        Some(true)
    );
}

#[test]
fn captured_maximized_state_is_cleared_for_user_resized_bounds() {
    assert_eq!(
        effective_captured_maximized(
            Some(true),
            Some(1420.0),
            Some(880.0),
            Some(1728.0),
            Some(1117.0)
        ),
        Some(false)
    );
}

#[test]
fn saved_launch_size_uses_logical_saved_bounds_before_window_is_shown() {
    let state = SavedWindowState {
        width: Some(1320.0),
        height: Some(840.0),
        x: Some(180.0),
        y: Some(120.0),
        is_maximized: Some(false),
        state_version: Some(WINDOW_STATE_SCHEMA_VERSION),
        coordinate_space: Some(WINDOW_STATE_COORDINATE_SPACE.to_string()),
    };

    assert_eq!(
        saved_launch_size(&state, MAIN_WINDOW_DEFAULT_SIZE, MAIN_WINDOW_MIN_SIZE),
        (1320.0, 840.0)
    );
    assert_eq!(saved_launch_position(&state), Some((180.0, 120.0)));
}

#[test]
fn desktop_init_script_prevents_frontend_window_resize_fights() {
    assert!(DESKTOP_WINDOW_INIT_SCRIPT.contains("__HOROSA_DESKTOP_SHELL__"));
    assert!(DESKTOP_WINDOW_INIT_SCRIPT.contains("resizeTo"));
    assert!(DESKTOP_WINDOW_INIT_SCRIPT.contains("moveTo"));
}

#[test]
fn reinstall_inflight_guard_clears_flag_on_drop() {
    REINSTALL_INFLIGHT.store(true, Ordering::SeqCst);
    {
        let _g = ReinstallInflightGuard;
    }
    assert!(!REINSTALL_INFLIGHT.load(Ordering::SeqCst));
}

#[test]
fn web_ledger_extra_is_size_capped() {
    assert_eq!(web_ledger_extra_capped(None), None);
    let small = serde_json::json!({ "via": "probe", "waitedMs": 12 });
    assert_eq!(web_ledger_extra_capped(Some(small.clone())), Some(small));
    let big = serde_json::json!({ "blob": "x".repeat(WEB_LEDGER_EXTRA_MAX_BYTES + 1) });
    let capped = web_ledger_extra_capped(Some(big)).expect("capped value");
    assert_eq!(capped["truncated"], serde_json::json!(true));
    assert!(capped["bytes"].as_u64().unwrap() > WEB_LEDGER_EXTRA_MAX_BYTES as u64);
}

// 早导航 URL 必须带 rv:runtime_bootstrap 里「记运行时版本」要先于「生成早导航 URL」。
#[test]
fn runtime_version_noted_before_early_navigation() {
    let src = include_str!("bootstrap.rs");
    let body_at = src
        .find("fn runtime_bootstrap(")
        .expect("runtime_bootstrap present");
    let body = &src[body_at..];
    let note_at = body
        .find("note_runtime_version_for_url(&manifest.version);")
        .expect("version noted in bootstrap");
    let nav_at = body
        .find("let early_url = early_nav_url(")
        .expect("early navigation present");
    assert!(
        note_at < nav_at,
        "runtime version must be noted before the early navigation URL is built"
    );
}

#[cfg(target_os = "macos")]
#[test]
fn legacy_macos_defaults_cleanup_targets_old_main_workspace_frames() {
    assert!(LEGACY_MACOS_WINDOW_DEFAULT_KEYS.contains(&"NSWindow Frame main-workspace"));
    assert!(LEGACY_MACOS_WINDOW_DEFAULT_KEYS
        .contains(&"NSSplitView Subview Frames main-workspace, SidebarNavigationSplitView"));
    assert!(LEGACY_MACOS_WINDOW_DEFAULT_KEYS
        .iter()
        .any(|key| key.contains("Horosa.RootWorkspaceView")));
}

#[test]
fn saved_launch_size_ignores_legacy_bounds_but_uses_maximized_saved_bounds() {
    let legacy_state = SavedWindowState {
        width: Some(2960.0),
        height: Some(1920.0),
        is_maximized: Some(false),
        ..SavedWindowState::default()
    };
    let maximized_state = SavedWindowState {
        width: Some(1320.0),
        height: Some(840.0),
        is_maximized: Some(true),
        state_version: Some(WINDOW_STATE_SCHEMA_VERSION),
        coordinate_space: Some(WINDOW_STATE_COORDINATE_SPACE.to_string()),
        ..SavedWindowState::default()
    };

    assert_eq!(
        saved_launch_size(
            &legacy_state,
            MAIN_WINDOW_DEFAULT_SIZE,
            MAIN_WINDOW_MIN_SIZE
        ),
        MAIN_WINDOW_DEFAULT_SIZE
    );
    assert_eq!(
        saved_launch_size(
            &maximized_state,
            MAIN_WINDOW_DEFAULT_SIZE,
            MAIN_WINDOW_MIN_SIZE
        ),
        (1320.0, 840.0)
    );
}

#[test]
fn maximized_launch_uses_saved_bounds_as_builder_size() {
    let state = SavedWindowState {
        width: Some(1728.0),
        height: Some(1079.0),
        x: Some(0.0),
        y: Some(38.0),
        is_maximized: Some(true),
        state_version: Some(WINDOW_STATE_SCHEMA_VERSION),
        coordinate_space: Some(WINDOW_STATE_COORDINATE_SPACE.to_string()),
    };

    assert_eq!(
        saved_launch_size(&state, MAIN_WINDOW_DEFAULT_SIZE, MAIN_WINDOW_MIN_SIZE),
        (1728.0, 1079.0)
    );
    assert_eq!(saved_launch_position(&state), Some((0.0, 38.0)));
}

#[test]
fn previous_maximized_outer_size_state_launches_with_inner_height() {
    let state = SavedWindowState {
        width: Some(1728.0),
        height: Some(1079.0),
        x: Some(-1.0),
        y: Some(38.0),
        is_maximized: Some(true),
        state_version: Some(2),
        coordinate_space: Some(WINDOW_STATE_COORDINATE_SPACE.to_string()),
    };

    assert_eq!(
        saved_launch_size(&state, MAIN_WINDOW_DEFAULT_SIZE, MAIN_WINDOW_MIN_SIZE),
        (1728.0, 1051.0)
    );
    assert_eq!(saved_launch_position(&state), Some((-1.0, 38.0)));
}

#[test]
fn previous_logical_outer_size_state_is_converted_to_inner_height_for_launch() {
    let state = SavedWindowState {
        width: Some(1260.0),
        height: Some(820.0),
        x: Some(260.0),
        y: Some(160.0),
        is_maximized: Some(false),
        state_version: Some(2),
        coordinate_space: Some(WINDOW_STATE_COORDINATE_SPACE.to_string()),
    };

    assert_eq!(
        saved_launch_size(&state, MAIN_WINDOW_DEFAULT_SIZE, MAIN_WINDOW_MIN_SIZE),
        (1260.0, 792.0)
    );
    assert_eq!(saved_launch_position(&state), Some((260.0, 160.0)));
}

// frontend_url 的 rv 参数:置版本后必须带 &rv=(前端 L3 信封版本闸的唯一供给);
// 未置(dev)不带参=前端保持旧 rev。注意测试进程内 Mutex 是全局——先测未置态再置。
#[test]
fn frontend_url_carries_runtime_version_gate() {
    {
        let slot = FRONTEND_RUNTIME_VERSION.lock().unwrap();
        assert!(slot.is_none() || slot.is_some()); // 仅取锁确认可用
    }
    note_runtime_version_for_url("  ");
    note_runtime_version_for_url("3.4.0-runtime1");
    let url = frontend_url(38991, 61632, 61633);
    assert!(url.contains("&rv=3.4.0-runtime1"), "{url}");
    note_runtime_version_for_url("3.5.0-runtime1");
    let url2 = frontend_url(38991, 61632, 61633);
    assert!(
        url2.contains("&rv=3.5.0-runtime1"),
        "更新后重引导必须取新值: {url2}"
    );
}

#[test]
fn frontend_url_injects_chart_service_for_packaged_kentang_routes() {
    let url = frontend_url(38991, 63968, 63967);

    assert!(url.contains("srv=http%3A%2F%2F127.0.0.1%3A63968"));
    assert!(url.contains("chartSrv=http%3A%2F%2F127.0.0.1%3A63967"));
    assert!(url.contains("kentangSrv=http%3A%2F%2F127.0.0.1%3A63967"));
    // 身份握手会话 nonce:必在 URL,且同壳进程内稳定复用(重启后端不换值)。
    assert!(url.contains(&format!("sid={}", launch_nonce())));
}

#[test]
fn launch_nonce_is_stable_and_url_safe() {
    let a = launch_nonce();
    let b = launch_nonce();
    assert_eq!(a, b, "同壳会话内 nonce 必须稳定(重启后端复用)");
    assert_eq!(a.len(), 16);
    assert!(a.chars().all(|c| c.is_ascii_hexdigit()));
}

fn temp_test_dir(name: &str) -> PathBuf {
    let unique = SystemTime::now()
        .duration_since(UNIX_EPOCH)
        .unwrap()
        .as_nanos();
    let path =
        std::env::temp_dir().join(format!("horosa-{}-{}-{}", name, std::process::id(), unique));
    fs::create_dir_all(&path).unwrap();
    path
}

fn create_runtime_archive(root: &Path, version: &str) -> PathBuf {
    let payload_root = root.join("payload/runtime-payload");
    fs::create_dir_all(&payload_root).unwrap();
    fs::write(
        payload_root.join("runtime-manifest.json"),
        format!(
            "{{\"version\":\"{}\",\"built_at\":\"2026-04-07 00:00:00\"}}\n",
            version
        ),
    )
    .unwrap();
    fs::create_dir_all(payload_root.join("Horosa-Web")).unwrap();
    let archive_path = root.join("runtime.tar.gz");
    let tar_gz = File::create(&archive_path).unwrap();
    let encoder = GzEncoder::new(tar_gz, Compression::default());
    let mut builder = Builder::new(encoder);
    builder
        .append_dir_all("runtime-payload", &payload_root)
        .unwrap();
    builder.finish().unwrap();
    archive_path
}

#[cfg(unix)]
fn create_usable_runtime_archive(root: &Path, version: &str) -> PathBuf {
    let payload_root = root.join("usable/runtime-payload");
    let runtime_dir = payload_root;
    fs::create_dir_all(runtime_dir.join("Horosa-Web/astrostudyui/dist-file")).unwrap();
    // 与打包脚本同形:manifest 带 appName 身份戳
    fs::write(
        runtime_dir.join("runtime-manifest.json"),
        serde_json::json!({
            "version": version,
            "built_at": "2026-04-07 00:00:00",
            "appName": APP_NAME,
        })
        .to_string()
            + "\n",
    )
    .unwrap();
    fs::write(
        runtime_dir.join("Horosa-Web/start_horosa_local.sh"),
        "#!/bin/sh\n",
    )
    .unwrap();
    fs::write(
        runtime_dir.join("Horosa-Web/astrostudyui/dist-file/index.html"),
        "<html></html>\n",
    )
    .unwrap();
    write_stub_executable(&runtime_dir.join("runtime/mac/python/bin/python3"));
    write_stub_executable(&runtime_dir.join("runtime/mac/java/bin/java"));
    let archive_path = root.join("usable-runtime.tar.gz");
    let tar_gz = File::create(&archive_path).unwrap();
    let encoder = GzEncoder::new(tar_gz, Compression::default());
    let mut builder = Builder::new(encoder);
    builder
        .append_dir_all("runtime-payload", runtime_dir)
        .unwrap();
    builder.finish().unwrap();
    archive_path
}

#[cfg(unix)]
fn write_stub_executable(path: &Path) {
    if let Some(parent) = path.parent() {
        fs::create_dir_all(parent).unwrap();
    }
    fs::write(path, "#!/bin/sh\nexit 0\n").unwrap();
    let mut perms = fs::metadata(path).unwrap().permissions();
    perms.set_mode(0o755);
    fs::set_permissions(path, perms).unwrap();
}

#[cfg(unix)]
fn create_fake_runtime_tree(root: &Path, version: &str, with_java: bool) -> PathBuf {
    let runtime_dir = root.join("runtime/current");
    fs::create_dir_all(runtime_dir.join("Horosa-Web/astrostudyui/dist-file")).unwrap();
    fs::write(
        runtime_dir.join("runtime-manifest.json"),
        serde_json::json!({
            "version": version,
            "built_at": "2026-04-07 00:00:00",
            "appName": APP_NAME,
        })
        .to_string()
            + "\n",
    )
    .unwrap();
    fs::write(
        runtime_dir.join("Horosa-Web/start_horosa_local.sh"),
        "#!/bin/sh\n",
    )
    .unwrap();
    fs::write(
        runtime_dir.join("Horosa-Web/astrostudyui/dist-file/index.html"),
        "<html></html>\n",
    )
    .unwrap();
    write_stub_executable(&runtime_dir.join("runtime/mac/python/bin/python3"));
    if with_java {
        write_stub_executable(&runtime_dir.join("runtime/mac/java/bin/java"));
    }
    runtime_dir
}

#[test]
fn runtime_update_command_uses_shell_resolved_manifest_path() {
    let _env = HELPER_ENV_LOCK.lock().unwrap_or_else(|e| e.into_inner());
    let runtime_root = Path::new("/tmp/horosa-runtime-root");
    let archive = Path::new("/tmp/horosa-runtime.tar.gz");
    // 默认新协议:手术经 TARGET 新二进制(--horosa-runtime-swap),模板层只定义不执行
    let command = build_runtime_update_command(
        &[runtime_root.to_path_buf()],
        archive,
        Some("1.0.19-runtime1"),
    );
    assert!(command.contains("--horosa-runtime-swap"));
    assert!(command.contains("run_runtime_installs() {"));
    assert!(!command.contains("mv \"${WORK_ROOT}/runtime-payload\""));
    // 旧协议(逃生阀)保留 shell 原生 plutil 解析,零 python 依赖
    let legacy = build_single_runtime_update_command_legacy(
        runtime_root,
        archive,
        Some("1.0.19-runtime1"),
        0,
    );
    assert!(legacy.contains(
        "ACTUAL_RUNTIME_VERSION=\"$(/usr/bin/plutil -extract version raw -o - \"${WORK_ROOT}/runtime-payload/runtime-manifest.json\" 2>/dev/null || true)\""
    ));
    assert!(
        !legacy.contains("pathlib.Path(r\"${WORK_ROOT}/runtime-payload/runtime-manifest.json\")")
    );
}

#[test]
fn runtime_update_command_legacy_extracts_and_switches_payload() {
    // 旧协议(HOROSA_HELPER_RUNTIME_SWAP=0 逃生阀)功能保真:自包含 bash 原地可跑。
    // 新协议的功能等价物 = run_runtime_swap_cli(见 runtime_swap_cli_* 测试)。
    let root = temp_test_dir("runtime-update-helper");
    let runtime_root = root.join("shared/runtime");
    let archive = create_runtime_archive(&root, "1.0.19-runtime1");
    let command = build_single_runtime_update_command_legacy(
        &runtime_root,
        &archive,
        Some("1.0.19-runtime1"),
        0,
    );
    let script_path = root.join("run.sh");
    fs::write(
        &script_path,
        format!(
            "#!/bin/bash\nset -euo pipefail\n{}\n[ -f \"{current}/runtime-manifest.json\" ]\nVERSION=$(/usr/bin/plutil -extract version raw -o - \"{current}/runtime-manifest.json\")\n[ \"$VERSION\" = \"1.0.19-runtime1\" ]\n",
            command,
            current = runtime_root.join("current").display()
        ),
    )
    .unwrap();
    let status = Command::new("/bin/bash")
        .arg(&script_path)
        .status()
        .unwrap();
    assert!(status.success());
    assert!(runtime_root.join("current/runtime-manifest.json").exists());
    assert!(!runtime_root.join("_update").exists());
}

// HOROSA_HELPER_RUNTIME_SWAP 是进程级 env:读它的模板测试与设它的 killswitch
// 测试并行会互毒 → 共用一把测试锁串行化(поisoned 也继续,锁只为互斥不为状态)。
static HELPER_ENV_LOCK: std::sync::Mutex<()> = std::sync::Mutex::new(());

#[test]
fn diagnostics_redacts_secrets() {
    // 诊断包三段(日志/账本/更新历史)都经 redact_lines;密钥形状零明文
    let lines = vec![
        "2026-09-08 upstream auth sk-abcdefghijklmnopqrstuvwxyz1234 rejected".to_string(),
        "Authorization: Bearer eyJhbGciOiJIUzI1NiJ9.payload.sig".to_string(),
        "{\"api_key\":\"AIzaSyD-exampleexample\",\"apikey\": \"secret-value-here\"}".to_string(),
        "plain line without secrets sk-short".to_string(),
    ];
    let out = redact_lines(lines);
    let joined = out.join("\n");
    assert!(
        !joined.contains("abcdefghijklmnopqrstuvwxyz1234"),
        "{}",
        joined
    );
    assert!(!joined.contains("eyJhbGciOiJIUzI1NiJ9"), "{}", joined);
    assert!(!joined.contains("AIzaSyD-exampleexample"), "{}", joined);
    assert!(!joined.contains("secret-value-here"), "{}", joined);
    assert!(joined.contains("sk-***"));
    assert!(joined.contains("Bearer ***"));
    assert!(
        joined.contains("sk-short"),
        "短于 8 位的 sk- 不算密钥,保留:{}",
        joined
    );
    assert_eq!(redact_secrets("nothing here"), "nothing here");
}

// 新协议 helper 模板契约:定义不执行 / wait→app→runtime 时序 / 危险旧序零回潮
#[test]
fn update_helper_script_runtime_swap_after_wait_and_app() {
    let _env = HELPER_ENV_LOCK.lock().unwrap_or_else(|e| e.into_inner());
    let runtime_cmd = build_runtime_update_command(
        &[PathBuf::from("/Users/Shared/HorosaTest/runtime")],
        Path::new("/tmp/runtime.tar.gz"),
        Some("9.9.9-runtime1"),
    );
    let script = build_update_helper_script(
        Path::new("/tmp/log.txt"),
        Path::new("/tmp/marker.txt"),
        Path::new("/Applications/Demo.app"),
        Path::new("/tmp/extract/Demo.app"),
        "501",
        "demo",
        "1234",
        "demo-exec",
        "9.9.9",
        Some("9.9.9-runtime1"),
        &runtime_cmd,
    );
    assert!(
        script.contains("--horosa-runtime-swap"),
        "新协议必须经 TARGET 二进制做 runtime 对换"
    );
    // 旧危险序零回潮(默认脚本不得再出现两段 mv 序/成功即删 previous)
    assert!(!script.contains("mv \"${WORK_ROOT}/runtime-payload\""));
    assert!(!script.contains("rm -rf \"${WORK_ROOT}\" \"${PREVIOUS_ROOT}\""));
    // 时序:定义(install_runtime_0)→ wait 调用 → install_app 调用 → run_runtime_installs 调用
    let def_at = script
        .find("install_runtime_0() {")
        .expect("缺 runtime 安装函数定义");
    let wait_call_at = script
        .rfind("\nwait_for_old_app_exit\n")
        .expect("缺 wait 裸调用");
    let app_call_at = script
        .find("if ! install_app; then")
        .expect("缺 install_app 调用");
    let runtime_call_at = script
        .find("if ! run_runtime_installs; then")
        .expect("缺 run_runtime_installs 调用");
    assert!(def_at < wait_call_at, "runtime_cmd 必须只定义不执行");
    assert!(
        wait_call_at < app_call_at && app_call_at < runtime_call_at,
        "顺序必须 wait→app→runtime"
    );
}

// 铁律14:runtime 失败臂(exit 73)绝不写完成标记,重开用 open_app_once(open_app 会 mark)
#[test]
fn update_helper_runtime_failure_arm_never_marks() {
    let _env = HELPER_ENV_LOCK.lock().unwrap_or_else(|e| e.into_inner());
    let runtime_cmd = build_runtime_update_command(
        &[PathBuf::from("/Users/Shared/HorosaTest/runtime")],
        Path::new("/tmp/runtime.tar.gz"),
        Some("9.9.9-runtime1"),
    );
    let script = build_update_helper_script(
        Path::new("/tmp/log.txt"),
        Path::new("/tmp/marker.txt"),
        Path::new("/Applications/Demo.app"),
        Path::new("/tmp/extract/Demo.app"),
        "501",
        "demo",
        "1234",
        "demo-exec",
        "9.9.9",
        Some("9.9.9-runtime1"),
        &runtime_cmd,
    );
    let arm_start = script.find("if ! run_runtime_installs; then").unwrap();
    let arm_end = arm_start + script[arm_start..].find("exit 73").expect("缺 exit 73 臂");
    let arm = &script[arm_start..arm_end];
    assert!(
        !arm.contains("mark_update_complete"),
        "runtime 失败臂不得写完成标记"
    );
    assert!(arm.contains("open_app_once"), "失败臂用 open_app_once 重开");
    // 成功路径的 mark 必须在失败臂之后(即 run_runtime_installs 通过才 mark)
    let mark_at = script
        .rfind("mark_update_complete \"pending_manual\"")
        .unwrap();
    assert!(arm_end < mark_at);
}

// kill-switch:生成端回旧模板(证明开关真实闭环)
#[test]
fn update_helper_legacy_killswitch_restores_old_template() {
    let _env = HELPER_ENV_LOCK.lock().unwrap_or_else(|e| e.into_inner());
    std::env::set_var("HOROSA_HELPER_RUNTIME_SWAP", "0");
    let legacy = build_runtime_update_command(
        &[PathBuf::from("/Users/Shared/HorosaTest/runtime")],
        Path::new("/tmp/runtime.tar.gz"),
        Some("9.9.9-runtime1"),
    );
    std::env::remove_var("HOROSA_HELPER_RUNTIME_SWAP");
    assert!(
        legacy.contains("mv \"${WORK_ROOT}/runtime-payload\""),
        "开关下必须回旧模板"
    );
    assert!(!legacy.contains("--horosa-runtime-swap"));
    assert!(
        !legacy.contains("run_runtime_installs() {"),
        "旧模板不覆盖 run_runtime_installs(走默认空实现)"
    );
}

// helper 真执行演练:生成的脚本用 /bin/bash 实跑——文本契约测不出
// set -euo pipefail 下的真实执行语义(函数定义顺序/失败臂 exit 码/标记纪律)。
// 只换三个 GUI 命令(open/pgrep/osascript)为桩,mv/ditto/kill/df 全真;
// 手术本体行为由 runtime_swap_cli_* 测试真实覆盖,此处桩只回执 exit 码。
struct HelperExecFixture {
    root: PathBuf,
    script_path: PathBuf,
    log: PathBuf,
    marker: PathBuf,
    target_payload: PathBuf,
    calls: PathBuf,
    path_env: String,
}

fn write_exec_stub(path: &Path, body: &str) {
    use std::os::unix::fs::PermissionsExt;
    fs::write(path, body).unwrap();
    fs::set_permissions(path, fs::Permissions::from_mode(0o755)).unwrap();
}

fn build_helper_exec_fixture(name: &str, swap_exit: i32, old_pid: &str) -> HelperExecFixture {
    let root = temp_test_dir(name);
    let stub = root.join("stub");
    fs::create_dir_all(&stub).unwrap();
    let calls = root.join("calls.log");
    fs::write(&calls, "").unwrap();
    // 裸 sleep 走 PATH:压缩等待窗(60 轮×0.05s 仍足够旧进程真实退出)
    write_exec_stub(&stub.join("sleep"), "#!/bin/bash\n/bin/sleep 0.05\n");
    write_exec_stub(
        &stub.join("open"),
        &format!(
            "#!/bin/bash\necho \"open $*\" >> {}\nexit 0\n",
            calls.display()
        ),
    );
    write_exec_stub(&stub.join("osascript"), "#!/bin/bash\nexit 0\n");
    write_exec_stub(
        &stub.join("pgrep"),
        &format!(
            "#!/bin/bash\necho \"pgrep $*\" >> {}\nexit 0\n",
            calls.display()
        ),
    );
    // SRC 新 app 骨架:exec 桩处理两个子命令(atomic-swap 拒→逼 mv 回退;runtime-swap 落参回执)
    let src_app = root.join("src/Horosa.app");
    fs::create_dir_all(src_app.join("Contents/MacOS")).unwrap();
    fs::create_dir_all(src_app.join("Contents/Resources")).unwrap();
    write_exec_stub(
        &src_app.join("Contents/MacOS/horosa-exec"),
        &format!(
            "#!/bin/bash\ncase \"${{1:-}}\" in\n  --horosa-atomic-swap) exit 1 ;;\n  --horosa-runtime-swap) echo \"swap-args $2 $3 $4\" >> {}\n    exit {} ;;\nesac\nexit 0\n",
            calls.display(),
            swap_exit
        ),
    );
    fs::write(src_app.join("Contents/Resources/payload.txt"), "new").unwrap();
    // TARGET 旧 app(mv 回退路径要求它在位)
    let target_app = root.join("Applications/Horosa.app");
    fs::create_dir_all(target_app.join("Contents/MacOS")).unwrap();
    fs::create_dir_all(target_app.join("Contents/Resources")).unwrap();
    write_exec_stub(
        &target_app.join("Contents/MacOS/horosa-exec"),
        "#!/bin/bash\nexit 0\n",
    );
    fs::write(target_app.join("Contents/Resources/payload.txt"), "old").unwrap();

    let runtime_cmd = {
        let _env = HELPER_ENV_LOCK.lock().unwrap_or_else(|e| e.into_inner());
        std::env::set_var("HOROSA_HELPER_RUNTIME_SWAP", "1");
        let cmd = build_runtime_update_command(
            &[root.join("runtime")],
            &root.join("runtime.tar.gz"),
            Some("9.9.9-runtime1"),
        );
        std::env::remove_var("HOROSA_HELPER_RUNTIME_SWAP");
        cmd
    };
    let log = root.join("update.log");
    let marker = root.join("update-complete.txt");
    let uid = unsafe { libc::getuid() }.to_string();
    let script = build_update_helper_script(
        &log,
        &marker,
        &target_app,
        &src_app,
        &uid,
        "helper-exec-test",
        old_pid,
        "horosa-exec",
        "9.9.9",
        Some("9.9.9-runtime1"),
        &runtime_cmd,
    )
    .replace("/usr/bin/open", &stub.join("open").display().to_string())
    .replace("/usr/bin/pgrep", &stub.join("pgrep").display().to_string())
    .replace(
        "/usr/bin/osascript",
        &stub.join("osascript").display().to_string(),
    );
    let script_path = root.join("helper.sh");
    fs::write(&script_path, script).unwrap();
    HelperExecFixture {
        path_env: format!("{}:/usr/bin:/bin:/usr/sbin:/sbin", stub.display()),
        target_payload: target_app.join("Contents/Resources/payload.txt"),
        root,
        script_path,
        log,
        marker,
        calls,
    }
}

fn run_helper_script(fx: &HelperExecFixture) -> i32 {
    Command::new("/bin/bash")
        .arg(&fx.script_path)
        .env("PATH", &fx.path_env)
        .status()
        .expect("run helper script")
        .code()
        .unwrap_or(-1)
}

#[test]
fn update_helper_exec_happy_path_orders_wait_app_runtime_then_marks() {
    // 真旧进程:0.3s 后退出,验证 wait_for_old_app_exit 真的等到了它。
    // 必须即时收尸(僵尸 pid 对 kill -0 恒真,会骗过等待循环)→ 独立线程 wait()。
    let mut old = Command::new("/bin/sleep").arg("0.3").spawn().unwrap();
    let old_pid = old.id().to_string();
    let reaper = std::thread::spawn(move || {
        let _ = old.wait();
    });
    let fx = build_helper_exec_fixture("helper-exec-happy", 0, &old_pid);
    let code = run_helper_script(&fx);
    let _ = reaper.join();
    let log = fs::read_to_string(&fx.log).unwrap_or_default();
    let calls = fs::read_to_string(&fx.calls).unwrap_or_default();
    assert_eq!(code, 0, "log:\n{log}\ncalls:\n{calls}");
    assert!(
        log.contains("[app] old process exited"),
        "必须真等旧进程退出:\n{log}"
    );
    let i_install = log.find("[app] install succeeded").expect("app 安装日志");
    assert!(log.contains("update helper success"));
    let swap_line = calls
        .lines()
        .find(|l| l.starts_with("swap-args"))
        .expect("runtime swap 必须被调用");
    assert!(
        swap_line.contains("9.9.9-runtime1") && swap_line.contains("runtime.tar.gz"),
        "swap 参数错:{swap_line}"
    );
    // 时序:app 安装成功日志先于 runtime 失败探测日志区(swap 在 install 之后才可能出现)
    let i_runtime_log = log.find("===== update helper success").unwrap();
    assert!(i_install < i_runtime_log);
    let marker = fs::read_to_string(&fx.marker).expect("成功路必须写完成标记");
    assert!(
        marker.contains("relaunch_status=auto_relaunch_confirmed"),
        "{marker}"
    );
    assert_eq!(fs::read_to_string(&fx.target_payload).unwrap(), "new");
    let _ = fs::remove_dir_all(&fx.root);
}

#[test]
fn update_helper_exec_runtime_failure_exits_73_without_marker() {
    let fx = build_helper_exec_fixture("helper-exec-rtfail", 1, "0");
    let code = run_helper_script(&fx);
    let log = fs::read_to_string(&fx.log).unwrap_or_default();
    assert_eq!(code, 73, "runtime 失败臂必须 exit 73:\n{log}");
    assert!(log.contains("[runtime] runtime install failed"));
    assert!(!fx.marker.exists(), "runtime 失败绝不写完成标记(铁律14)");
    // 新 app 已上位(修复机器在场)+ 已尝试重开
    assert_eq!(fs::read_to_string(&fx.target_payload).unwrap(), "new");
    let calls = fs::read_to_string(&fx.calls).unwrap_or_default();
    assert!(
        calls.lines().any(|l| l.starts_with("open ")),
        "失败臂必须重开 app"
    );
    let _ = fs::remove_dir_all(&fx.root);
}

#[test]
fn update_helper_exec_app_install_failure_exits_71_keeps_old_app() {
    let fx = build_helper_exec_fixture("helper-exec-appfail", 0, "0");
    // 挖掉 SRC → ditto 永败 → install_app 失败臂
    fs::remove_dir_all(fx.root.join("src")).unwrap();
    let code = run_helper_script(&fx);
    let log = fs::read_to_string(&fx.log).unwrap_or_default();
    assert_eq!(code, 71, "app 安装失败臂必须 exit 71:\n{log}");
    assert!(!fx.marker.exists(), "安装失败绝不写完成标记");
    assert_eq!(
        fs::read_to_string(&fx.target_payload).unwrap(),
        "old",
        "旧 app 必须完好"
    );
    let calls = fs::read_to_string(&fx.calls).unwrap_or_default();
    assert!(!calls.contains("swap-args"), "app 未装成绝不能碰 runtime");
    let _ = fs::remove_dir_all(&fx.root);
}

// CLI 手术版本闸:归档 manifest 与期望不符 → 失败且 current 纹丝不动、半成品清净
#[test]
fn runtime_swap_cli_rejects_version_mismatch() {
    let root = temp_test_dir("runtime-swap-cli-vgate");
    let runtime_root = root.join("runtime");
    write_minimal_runtime_tree(&runtime_root.join("current"), "old");
    let archive = create_runtime_archive(&root, "2.0.0-runtime1");
    let code = run_runtime_swap_cli(&runtime_root, &archive, "9.9.9-runtime1");
    assert_eq!(code, 1, "版本不符必须失败");
    assert_eq!(
        fs::read_to_string(
            runtime_root.join("current/Horosa-Web/astrostudyui/dist-file/index.html")
        )
        .unwrap(),
        "old"
    );
    assert!(!runtime_root.join("_extract").exists(), "半成品必须清");
    let _ = fs::remove_dir_all(&root);
}

// CLI 手术成功路:新树上位 + previous 保留到首次 ready(看门狗回滚资本)
#[test]
fn runtime_swap_cli_promotes_and_keeps_previous() {
    let root = temp_test_dir("runtime-swap-cli-promote");
    let runtime_root = root.join("runtime");
    write_minimal_runtime_tree(&runtime_root.join("current"), "old");
    let archive = create_runtime_archive(&root, "2.0.0-runtime1");
    let code = run_runtime_swap_cli(&runtime_root, &archive, "2.0.0-runtime1");
    assert_eq!(code, 0);
    let manifest = fs::read_to_string(runtime_root.join("current/runtime-manifest.json")).unwrap();
    assert!(manifest.contains("2.0.0-runtime1"));
    assert!(
        runtime_root.join("previous").exists(),
        "previous 必须保留(绝不像旧协议成功即删)"
    );
    assert_eq!(
        fs::read_to_string(
            runtime_root.join("previous/Horosa-Web/astrostudyui/dist-file/index.html")
        )
        .unwrap(),
        "old"
    );
    let _ = fs::remove_dir_all(&root);
}

// 旧协议(过渡跳)暂存 _update/runtime-payload:断电撕裂时可被收养,不再成孤儿
#[test]
fn repair_torn_slots_adopts_legacy_update_dir() {
    let root = temp_test_dir("torn-legacy-update");
    write_minimal_runtime_tree(&root.join("_update/runtime-payload"), "legacy-stage");
    assert!(repair_torn_runtime_slots(&root).unwrap());
    assert_eq!(
        fs::read_to_string(root.join("current/Horosa-Web/astrostudyui/dist-file/index.html"))
            .unwrap(),
        "legacy-stage"
    );
    let _ = fs::remove_dir_all(&root);
}

// 孤儿清扫:新鲜暂存/撕裂态零动作;仅清 24h 以上陈旧目录
#[test]
fn sweep_stale_stage_dirs_only_removes_old() {
    let root = temp_test_dir("sweep-stale");
    write_minimal_runtime_tree(&root.join("current"), "cur");
    fs::create_dir_all(root.join("_update/runtime-payload")).unwrap();
    fs::create_dir_all(root.join("_extract/runtime-payload")).unwrap();
    sweep_stale_runtime_stage_dirs(&root);
    assert!(root.join("_update").exists(), "新鲜目录绝不清");
    assert!(root.join("_extract").exists());
    // mtime 拨回 2020 → 判陈旧,必须清
    let _ = Command::new("/usr/bin/touch")
        .args(["-t", "202001010000"])
        .arg(root.join("_update"))
        .status();
    sweep_stale_runtime_stage_dirs(&root);
    assert!(!root.join("_update").exists(), "陈旧 _update 必须被清扫");
    assert!(root.join("_extract").exists(), "新鲜 _extract 仍不动");
    // 无 current(撕裂态)零动作,交给收养
    let root2 = temp_test_dir("sweep-torn");
    fs::create_dir_all(root2.join("_update/runtime-payload")).unwrap();
    let _ = Command::new("/usr/bin/touch")
        .args(["-t", "202001010000"])
        .arg(root2.join("_update"))
        .status();
    sweep_stale_runtime_stage_dirs(&root2);
    assert!(root2.join("_update").exists(), "撕裂态不清扫(留给收养)");
    let _ = fs::remove_dir_all(&root);
    let _ = fs::remove_dir_all(&root2);
}

// 手术锁簇:全部走 HELPER_ENV_LOCK 串行(读写手术锁相关 env,防并行互毒)
#[test]
fn surgery_lock_blocks_second_acquire_same_process() {
    let _env = HELPER_ENV_LOCK.lock().unwrap_or_else(|e| e.into_inner());
    let root = temp_test_dir("surgery-lock-same-proc");
    let guard = try_acquire_surgery_lock(&root, Duration::from_secs(1))
        .unwrap()
        .expect("首次必须拿到");
    // flock 同进程第二个 fd 也互斥(这正是「锁只进五叶、上层禁取」纪律的依据)
    let second = try_acquire_surgery_lock(&root, Duration::from_millis(600)).unwrap();
    assert!(second.is_none(), "持锁期间第二次 acquire 必须等超时");
    drop(guard);
    let third = try_acquire_surgery_lock(&root, Duration::from_secs(1)).unwrap();
    assert!(third.is_some(), "释放后立即可得");
    let _ = fs::remove_dir_all(&root);
}

// 子进程角色:仅当 HOROSA_LOCK_TEST_ROOT 在场才动作(直跑=零动作秒过)。
#[test]
fn surgery_lock_child_holder() {
    let Ok(root) = std::env::var("HOROSA_LOCK_TEST_ROOT") else {
        return;
    };
    let guard = try_acquire_surgery_lock(Path::new(&root), Duration::from_secs(5))
        .unwrap()
        .expect("child 必须拿到锁");
    thread::sleep(Duration::from_secs(3));
    drop(guard);
}

fn spawn_lock_holder_child(root: &Path) -> std::process::Child {
    let exe = std::env::current_exe().unwrap();
    Command::new(&exe)
        .args(["--exact", "tests::surgery_lock_child_holder", "--nocapture"])
        .env("HOROSA_LOCK_TEST_ROOT", root)
        .env_remove("HOROSA_SURGERY_LOCK_DISABLE")
        .stdout(Stdio::null())
        .stderr(Stdio::null())
        .spawn()
        .expect("spawn child")
}

fn wait_until_child_holds_lock(root: &Path) -> bool {
    for _ in 0..50 {
        thread::sleep(Duration::from_millis(100));
        match try_acquire_surgery_lock(root, Duration::from_millis(1)).unwrap() {
            Some(g) => drop(g), // 子进程还没锁上,继续等
            None => return true,
        }
    }
    false
}

#[test]
fn surgery_lock_cross_process_contention() {
    let _env = HELPER_ENV_LOCK.lock().unwrap_or_else(|e| e.into_inner());
    let root = temp_test_dir("surgery-lock-xproc");
    fs::create_dir_all(&root).unwrap();
    let mut child = spawn_lock_holder_child(&root);
    assert!(wait_until_child_holds_lock(&root), "子进程应已持锁");
    // 短等拿不到(对方在手术)
    assert!(try_acquire_surgery_lock(&root, Duration::from_millis(300))
        .unwrap()
        .is_none());
    // 长等(≥子进程持锁 3s)排队拿到
    assert!(try_acquire_surgery_lock(&root, Duration::from_secs(10))
        .unwrap()
        .is_some());
    let _ = child.wait();
    let _ = fs::remove_dir_all(&root);
}

#[test]
fn surgery_lock_released_on_sigkill() {
    let _env = HELPER_ENV_LOCK.lock().unwrap_or_else(|e| e.into_inner());
    let root = temp_test_dir("surgery-lock-sigkill");
    fs::create_dir_all(&root).unwrap();
    let mut child = spawn_lock_holder_child(&root);
    assert!(wait_until_child_holds_lock(&root), "子进程应已持锁");
    let _ = Command::new("/bin/kill")
        .args(["-9", &child.id().to_string()])
        .status();
    let _ = child.wait();
    // 内核级释放:kill -9 后立即可得(崩溃不留死锁)
    assert!(try_acquire_surgery_lock(&root, Duration::from_secs(2))
        .unwrap()
        .is_some());
    let _ = fs::remove_dir_all(&root);
}

#[test]
fn surgery_lock_disable_env_bypasses() {
    let _env = HELPER_ENV_LOCK.lock().unwrap_or_else(|e| e.into_inner());
    let root = temp_test_dir("surgery-lock-disable");
    let guard = try_acquire_surgery_lock(&root, Duration::from_secs(1))
        .unwrap()
        .expect("先真实持锁");
    std::env::set_var("HOROSA_SURGERY_LOCK_DISABLE", "1");
    let bypass = try_acquire_surgery_lock(&root, Duration::from_millis(100)).unwrap();
    std::env::remove_var("HOROSA_SURGERY_LOCK_DISABLE");
    assert!(bypass.is_some(), "开关下必须旁路(退回无锁旧行为)");
    drop(guard);
    let _ = fs::remove_dir_all(&root);
}

#[test]
fn torn_repair_skips_when_locked() {
    let _env = HELPER_ENV_LOCK.lock().unwrap_or_else(|e| e.into_inner());
    let root = temp_test_dir("torn-locked");
    write_minimal_runtime_tree(&root.join("previous"), "prev");
    std::env::set_var("HOROSA_SURGERY_LOCK_OPT_WAIT_SECS", "1");
    let guard = try_acquire_surgery_lock(&root, Duration::from_secs(1))
        .unwrap()
        .expect("模拟对方持锁");
    // optional 语义:拿不到 → Ok(false) 且绝不收养(current 不产出)
    let repaired = repair_torn_runtime_slots(&root).unwrap();
    std::env::remove_var("HOROSA_SURGERY_LOCK_OPT_WAIT_SECS");
    assert!(!repaired, "对方持锁期间不得收养");
    assert!(!root.join("current").exists());
    drop(guard);
    let _ = fs::remove_dir_all(&root);
}

// 多实例更新感知纯函数
#[test]
fn runtime_change_step_detects_version_drift() {
    // 首见=定基线,不触发
    let (b, changed) = runtime_change_step(None, Some("1.0.0-runtime1".into()));
    assert_eq!(b.as_deref(), Some("1.0.0-runtime1"));
    assert!(!changed);
    // 同版本不触发
    let (b, changed) = runtime_change_step(b, Some("1.0.0-runtime1".into()));
    assert!(!changed);
    // 版本漂移触发(基线保持,供账本引用)
    let (b, changed) = runtime_change_step(b, Some("1.0.1-runtime1".into()));
    assert!(changed);
    assert_eq!(b.as_deref(), Some("1.0.0-runtime1"));
    // 读不到 manifest(手术中途)不触发
    let (_b, changed) = runtime_change_step(b, None);
    assert!(!changed);
}

// ===== API 回退源 sha 闭环:三态 + 守门无条件 + notify-only 不触网 =====
fn test_release_config(manifest_name: &str) -> ReleaseConfig {
    serde_json::from_value(serde_json::json!({
        "repoOwner": "demo", "repoName": "horosa",
        "runtimeVersion": "1.0.0-runtime1",
        "runtimeAssetName": "runtime.tar.gz",
        "desktopAssetName": "Horosa-Desktop.zip",
        "desktopPkgName": "a.pkg", "desktopPkgZipName": "a.pkg.zip",
        "updateManifestName": manifest_name,
        "primaryDownload": "pkg", "supportedArch": "arm64",
        "releaseTagPrefix": "v", "appName": "星阙",
    }))
    .unwrap()
}

fn manifest_json(version: &str, with_sha: bool) -> String {
    let sha = if with_sha {
        "\"appSha256\":\"aa\",\"runtimeSha256\":\"bb\","
    } else {
        ""
    };
    format!(
        "{{\"version\":\"{version}\",\"tag\":\"v{version}\",\"platforms\":{{\"macos-aarch64\":{{\
             \"appUrl\":\"https://x/app.zip\",{sha}\"runtimeUrl\":\"https://x/rt.tar.gz\",\
             \"runtimeVersion\":\"{version}-runtime1\"}}}}}}"
    )
}

/// 极简 raw HTTP:按 path 返回预置 body(200)或 404。返回 (base_url, 命中计数)。
/// 用 raw TcpListener 而非 tiny_http:与 §7.1 规矩一致,协议级可控。
fn spawn_asset_server(
    routes: Vec<(String, String)>,
) -> (String, Arc<AtomicUsize>, Arc<AtomicBool>) {
    let listener = std::net::TcpListener::bind("127.0.0.1:0").unwrap();
    let port = listener.local_addr().unwrap().port();
    listener.set_nonblocking(true).unwrap();
    let hits = Arc::new(AtomicUsize::new(0));
    let stop = Arc::new(AtomicBool::new(false));
    let (h, st) = (hits.clone(), stop.clone());
    thread::spawn(move || {
        while !st.load(Ordering::SeqCst) {
            match listener.accept() {
                Ok((mut sock, _)) => {
                    h.fetch_add(1, Ordering::SeqCst);
                    let mut buf = [0u8; 2048];
                    let n = sock.read(&mut buf).unwrap_or(0);
                    let req = String::from_utf8_lossy(&buf[..n]).to_string();
                    let path = req
                        .split_whitespace()
                        .nth(1)
                        .unwrap_or("/")
                        .split('?')
                        .next()
                        .unwrap_or("/")
                        .to_string();
                    let body = routes
                        .iter()
                        .find(|(p, _)| *p == path)
                        .map(|(_, b)| b.clone());
                    let resp = match body {
                        Some(b) => format!(
                            "HTTP/1.1 200 OK\r\nContent-Length: {}\r\nConnection: close\r\n\r\n{}",
                            b.len(),
                            b
                        ),
                        None => "HTTP/1.1 404 Not Found\r\nContent-Length: 0\r\nConnection: close\r\n\r\n".to_string(),
                    };
                    let _ = sock.write_all(resp.as_bytes());
                }
                Err(_) => thread::sleep(Duration::from_millis(20)),
            }
        }
    });
    (format!("http://127.0.0.1:{port}"), hits, stop)
}

#[test]
fn api_fallback_fetches_manifest_asset_and_keeps_sha() {
    let _env = HELPER_ENV_LOCK.lock().unwrap_or_else(|e| e.into_inner());
    let (base, _hits, stop) = spawn_asset_server(vec![(
        "/horosa-latest.json".into(),
        manifest_json("9.9.9", true),
    )]);
    let release: GithubRelease = serde_json::from_value(serde_json::json!({
        "tag_name": "v9.9.9",
        "assets": [{"name": "horosa-latest.json",
                    "browser_download_url": format!("{base}/horosa-latest.json")}],
    }))
    .unwrap();
    let client = build_github_client(5).unwrap();
    let manifest =
        fetch_manifest_via_release_asset(&client, &release, "horosa-latest.json").unwrap();
    let plan = plan_from_manifest(
        manifest,
        &test_release_config("horosa-latest.json"),
        "macos-aarch64",
        UpdateSource::ManifestViaApi,
    )
    .unwrap();
    assert_eq!(plan.source, UpdateSource::ManifestViaApi);
    assert_eq!(plan.app_sha256.as_deref(), Some("aa"));
    assert_eq!(plan.runtime_sha256.as_deref(), Some("bb"));
    assert!(!plan.notify_only, "取回真 manifest 后绝不是 notify-only");
    stop.store(true, Ordering::SeqCst);
}

#[test]
fn api_fallback_manifest_asset_missing_yields_none() {
    let _env = HELPER_ENV_LOCK.lock().unwrap_or_else(|e| e.into_inner());
    let release: GithubRelease = serde_json::from_value(serde_json::json!({
        "tag_name": "v9.9.9",
        "assets": [{"name": "Horosa-Desktop.zip", "browser_download_url": "https://x/app.zip"}],
    }))
    .unwrap();
    let client = build_github_client(2).unwrap();
    // assets 里没有 manifest 名 → None(上游据此降级 notify-only)
    assert!(fetch_manifest_via_release_asset(&client, &release, "horosa-latest.json").is_none());
}

#[test]
fn api_fallback_manifest_asset_bad_json_yields_none() {
    let _env = HELPER_ENV_LOCK.lock().unwrap_or_else(|e| e.into_inner());
    let (base, _hits, stop) =
        spawn_asset_server(vec![("/horosa-latest.json".into(), "{ not json".into())]);
    let release: GithubRelease = serde_json::from_value(serde_json::json!({
        "tag_name": "v9.9.9",
        "assets": [{"name": "horosa-latest.json",
                    "browser_download_url": format!("{base}/horosa-latest.json")}],
    }))
    .unwrap();
    let client = build_github_client(5).unwrap();
    assert!(
        fetch_manifest_via_release_asset(&client, &release, "horosa-latest.json").is_none(),
        "坏 JSON 必须降级(不 panic)"
    );
    stop.store(true, Ordering::SeqCst);
}

#[test]
fn api_manifest_fetch_killswitch_forces_notify_only_path() {
    let _env = HELPER_ENV_LOCK.lock().unwrap_or_else(|e| e.into_inner());
    let (base, hits, stop) = spawn_asset_server(vec![(
        "/horosa-latest.json".into(),
        manifest_json("9.9.9", true),
    )]);
    let release: GithubRelease = serde_json::from_value(serde_json::json!({
        "tag_name": "v9.9.9",
        "assets": [{"name": "horosa-latest.json",
                    "browser_download_url": format!("{base}/horosa-latest.json")}],
    }))
    .unwrap();
    let client = build_github_client(5).unwrap();
    std::env::set_var("HOROSA_UPDATE_API_MANIFEST_FETCH", "0");
    let got = fetch_manifest_via_release_asset(&client, &release, "horosa-latest.json");
    std::env::remove_var("HOROSA_UPDATE_API_MANIFEST_FETCH");
    assert!(got.is_none(), "开关下跳过 asset 取回");
    assert_eq!(hits.load(Ordering::SeqCst), 0, "开关下不得触网");
    stop.store(true, Ordering::SeqCst);
}

// 无 sha 的 manifest 也能映射成 plan(sha=None),真正的拦截在守门——
// 守门已改无条件,故此处钉住「plan 侧 sha 缺失可观测」这一前置事实。
#[test]
fn plan_from_manifest_without_sha_leaves_none_for_guard() {
    let manifest: UpdateManifest = serde_json::from_str(&manifest_json("9.9.9", false)).unwrap();
    let plan = plan_from_manifest(
        manifest,
        &test_release_config("horosa-latest.json"),
        "macos-aarch64",
        UpdateSource::ManifestViaApi,
    )
    .unwrap();
    assert!(plan.app_sha256.is_none() && plan.runtime_sha256.is_none());
    assert!(!plan.notify_only);
    // 平台键不匹配 → None(老 manifest/异构平台)
    let m2: UpdateManifest = serde_json::from_str(&manifest_json("9.9.9", true)).unwrap();
    assert!(plan_from_manifest(
        m2,
        &test_release_config("horosa-latest.json"),
        "windows-x86_64",
        UpdateSource::Manifest
    )
    .is_none());
}

// 深探慢 streak 纯函数:1 次失败不杀、2 次杀、Ok 清零
#[test]
fn deep_step_state_machine() {
    let (s1, kill1) = deep_step(0, false);
    assert_eq!((s1, kill1), (1, false), "单次深探失败容忍(高载/GC)");
    let (s2, kill2) = deep_step(s1, false);
    assert_eq!((s2, kill2), (2, true), "连续 2 次深探失败判算力死");
    let (s3, kill3) = deep_step(s2, true);
    assert_eq!((s3, kill3), (0, false), "恢复即清零");
}

fn spawn_identity_stub(body: &'static str) -> u16 {
    let listener = std::net::TcpListener::bind("127.0.0.1:0").unwrap();
    let port = listener.local_addr().unwrap().port();
    thread::spawn(move || {
        if let Ok((mut sock, _)) = listener.accept() {
            let mut buf = [0u8; 1024];
            let _ = sock.read(&mut buf);
            let resp = format!(
                "HTTP/1.1 200 OK\r\nContent-Type: application/json\r\nContent-Length: {}\r\nConnection: close\r\n\r\n{}",
                body.len(),
                body
            );
            let _ = sock.write_all(resp.as_bytes());
        }
    });
    port
}

// proto 门代数差免疫:旧对端(proto 1/无 deep 字段)在深探轮按通过处理,绝不误杀
#[test]
fn probe_identity_deep_unsupported_on_proto1() {
    use std::io::{Read, Write};
    let _ = (Read::read as fn(&mut std::net::TcpStream, &mut [u8]) -> std::io::Result<usize>);
    let port = spawn_identity_stub(r#"{"app":"horosa-backend","proto":1,"nonce":"n-1"}"#);
    let got = probe_identity(port, "horosa-backend", "n-1", Duration::from_secs(2), true);
    assert_eq!(got, IdentityProbe::DeepUnsupported);
}

#[test]
fn probe_identity_deep_fail_on_proto2() {
    let port =
        spawn_identity_stub(r#"{"app":"horosa-backend","proto":2,"nonce":"n-1","deep":"fail"}"#);
    let got = probe_identity(port, "horosa-backend", "n-1", Duration::from_secs(2), true);
    assert_eq!(got, IdentityProbe::DeepFail, "proto2 深探失败必须显式分类");
}

#[test]
fn probe_identity_deep_ok_on_proto2() {
    let port =
        spawn_identity_stub(r#"{"app":"horosa-backend","proto":2,"nonce":"n-1","deep":"ok"}"#);
    let got = probe_identity(port, "horosa-backend", "n-1", Duration::from_secs(2), true);
    assert_eq!(got, IdentityProbe::Ok);
    // 浅探不受 proto2 影响
    let port2 = spawn_identity_stub(r#"{"app":"horosa-backend","proto":2,"nonce":"n-1"}"#);
    let got2 = probe_identity(
        port2,
        "horosa-backend",
        "n-1",
        Duration::from_secs(2),
        false,
    );
    assert_eq!(got2, IdentityProbe::Ok);
}

// 诊断包 Java 日志选取器:mtime 最新优先 + cap 内尽量多收(大文件跳过继续拣小)
#[test]
fn select_recent_files_prefers_newest_within_cap() {
    let root = temp_test_dir("diag-select");
    fs::create_dir_all(root.join("2026/07/09")).unwrap();
    let old_big = root.join("2026/07/09/old-big.log");
    let mid = root.join("2026/07/09/mid.log");
    let newest = root.join("newest.log");
    fs::write(&old_big, vec![b'x'; 3000]).unwrap();
    fs::write(&mid, vec![b'y'; 400]).unwrap();
    fs::write(&newest, vec![b'z'; 500]).unwrap();
    let _ = Command::new("/usr/bin/touch")
        .args(["-t", "202001010000"])
        .arg(&old_big)
        .status();
    let _ = Command::new("/usr/bin/touch")
        .args(["-t", "202601010000"])
        .arg(&mid)
        .status();
    let _ = Command::new("/usr/bin/touch")
        .args(["-t", "202607090000"])
        .arg(&newest)
        .status();
    // cap=1000:newest(500)+mid(400) 收下;old_big(3000) 超预算跳过
    let picked = select_recent_files_by_mtime(&root, 1000);
    assert_eq!(picked.len(), 2, "cap 内应收两份小日志");
    assert_eq!(picked[0], newest, "mtime 最新优先");
    assert_eq!(picked[1], mid);
    assert!(!picked.contains(&old_big), "超预算大文件跳过而非截断全部");
    let _ = fs::remove_dir_all(&root);
}

// 旧运行时字面目录里的 Java 日志兜底:命中即收进 java-logs-legacy/,无命中不建目录
#[test]
fn export_legacy_java_logs_collects_literal_dirs() {
    let root = temp_test_dir("diag-legacy");
    let runtime = root.join("runtime-a");
    let lit_a = runtime
        .join("Horosa-Web")
        .join("${env:HOME:-${sys:user.home}}")
        .join(".horosa-logs/astrostudyboot/2026/09/03/error");
    let lit_b = runtime
        .join("runtime/mac/bundle/boot-exploded")
        .join("${env:HOME}")
        .join(".horosa-logs/astrostudyboot/2026/09/03/access");
    fs::create_dir_all(&lit_a).unwrap();
    fs::create_dir_all(&lit_b).unwrap();
    fs::write(lit_a.join("error.log"), b"legacy-error").unwrap();
    fs::write(lit_b.join("access.log"), b"legacy-access").unwrap();
    let staging = root.join("staging");
    fs::create_dir_all(&staging).unwrap();
    // 同一 runtime 根传两次 → 去重,不重复收
    let out = export_legacy_java_logs(
        &[runtime.clone(), runtime.clone()],
        &staging,
        10 * 1024 * 1024,
    )
    .expect("字面目录存在应命中");
    assert_eq!(
        out.file_name().and_then(|s| s.to_str()),
        Some("java-logs-legacy")
    );
    assert!(out.join("1/2026/09/03/error/error.log").is_file());
    assert!(out.join("2/2026/09/03/access/access.log").is_file());
    assert!(!out.join("3").exists(), "同根重复传入不得重复收");
    let index = fs::read_to_string(out.join("legacy-roots.txt")).unwrap();
    assert!(index.contains("Horosa-Web"));
    assert!(index.contains("boot-exploded"));
    // 无字面目录 → None,且不建 java-logs-legacy/
    let staging_empty = root.join("staging-empty");
    fs::create_dir_all(&staging_empty).unwrap();
    assert!(export_legacy_java_logs(&[root.join("runtime-none")], &staging_empty, 1024).is_none());
    assert!(!staging_empty.join("java-logs-legacy").exists());
    let _ = fs::remove_dir_all(&root);
}

// 磁盘水位闩:跌破触发一次/闩内不刷屏/回升 2× 解闩/卷异常不动作
#[test]
fn disk_low_step_latch_and_recovery() {
    let min = 500u64 * 1024 * 1024;
    // 正常 → 不触发
    assert_eq!(disk_low_step(false, Some(min * 4), min), (false, false));
    // 跌破 → 触发+闩
    assert_eq!(disk_low_step(false, Some(min - 1), min), (true, true));
    // 闩内仍低 → 不再刷屏
    assert_eq!(disk_low_step(true, Some(min / 2), min), (true, false));
    // 回升但未到 2× → 保持闩(防抖)
    assert_eq!(disk_low_step(true, Some(min + 1), min), (true, false));
    // 回升到 2× → 解闩(不触发)
    assert_eq!(disk_low_step(true, Some(min * 2), min), (false, false));
    // 解闩后再跌破 → 再次触发
    assert_eq!(disk_low_step(false, Some(min - 1), min), (true, true));
    // 读不到 → 原样不动作
    assert_eq!(disk_low_step(true, None, min), (true, false));
    assert_eq!(disk_low_step(false, None, min), (false, false));
}

// 权限定因:目录 chmod 000 → PermissionDenied → 人话 hint;正常目录 → None
#[test]
fn classify_permission_issue_detects_readonly_dir() {
    use std::os::unix::fs::PermissionsExt;
    let root = temp_test_dir("perm-probe");
    let ok_dir = root.join("ok");
    let bad_dir = root.join("bad");
    fs::create_dir_all(&ok_dir).unwrap();
    fs::create_dir_all(&bad_dir).unwrap();
    let paths = RuntimePaths {
        app_data_dir: ok_dir.clone(),
        runtime_dir: bad_dir.clone(),
        logs_dir: ok_dir.clone(),
        frontend_dir: ok_dir.clone(),
        start_script: ok_dir.join("s.sh"),
        stop_script: ok_dir.join("t.sh"),
        manifest_path: ok_dir.join("m.json"),
    };
    // 全可写 → None
    assert!(classify_permission_issue(&paths).is_none());
    // runtime 目录锁死 → Some(含目录路径的人话)
    fs::set_permissions(&bad_dir, fs::Permissions::from_mode(0o000)).unwrap();
    let hint = classify_permission_issue(&paths);
    fs::set_permissions(&bad_dir, fs::Permissions::from_mode(0o755)).unwrap();
    let hint = hint.expect("锁死目录必须定因");
    assert!(hint.contains("权限异常"));
    assert!(hint.contains(&bad_dir.display().to_string()));
    let _ = fs::remove_dir_all(&root);
}

#[test]
fn archive_runtime_version_reads_manifest_version() {
    let root = temp_test_dir("runtime-archive-version");
    let archive = create_runtime_archive(&root, "1.2.3-runtime1");
    assert_eq!(
        archive_runtime_version(&archive).unwrap(),
        "1.2.3-runtime1".to_string()
    );
}

#[cfg(unix)]
#[test]
fn extract_runtime_archive_installs_usable_runtime() {
    let root = temp_test_dir("runtime-archive-extract");
    let archive = create_usable_runtime_archive(&root, "1.2.3-runtime1");
    let dest_root = root.join("runtime-root");
    extract_runtime_archive(&archive, &dest_root).unwrap();
    let current = dest_root.join("current");
    assert!(runtime_matches_expected(&current, "1.2.3-runtime1"));
    assert!(!dest_root.join("_extract").exists());
    assert!(!dest_root.join("previous").exists());
}

#[test]
fn choose_runtime_dir_prefers_shared_runtime_for_fresh_and_existing_shared_installs() {
    let shared = PathBuf::from("/Users/Shared/Horosa/runtime/current");
    let user = PathBuf::from("/tmp/horosa-user/runtime/current");

    assert_eq!(choose_runtime_dir(&shared, false, &user, false), user);
    assert_eq!(choose_runtime_dir(&shared, true, &user, false), shared);
    assert_eq!(choose_runtime_dir(&shared, false, &user, true), user);
    assert_eq!(choose_runtime_dir(&shared, true, &user, true), shared);
}

#[test]
fn choose_runtime_dir_prefers_newer_runtime_when_both_are_usable() {
    let root = temp_test_dir("runtime-choose-newest");
    let shared = root.join("Users/Shared/Horosa/runtime/current");
    let user =
        root.join("Users/test/Library/Application Support/com.horacedong.horosa/runtime/current");
    fs::create_dir_all(&shared).unwrap();
    fs::create_dir_all(&user).unwrap();
    fs::write(
        shared.join("runtime-manifest.json"),
        r#"{"version":"1.0.23-runtime1","built_at":"2026-03-17 17:00:00"}"#,
    )
    .unwrap();
    fs::write(
        user.join("runtime-manifest.json"),
        r#"{"version":"1.0.12","built_at":"2026-03-11 13:58:50"}"#,
    )
    .unwrap();

    assert_eq!(choose_runtime_dir(&shared, true, &user, true), shared);

    fs::write(
        user.join("runtime-manifest.json"),
        r#"{"version":"1.0.24-runtime1","built_at":"2026-03-18 09:00:00"}"#,
    )
    .unwrap();

    assert_eq!(choose_runtime_dir(&shared, true, &user, true), user);
}

#[cfg(unix)]
#[test]
fn runtime_dir_is_not_usable_when_java_runtime_is_missing() {
    let root = temp_test_dir("runtime-missing-java");
    let runtime_dir = create_fake_runtime_tree(&root, "1.2.2-runtime1", false);
    assert!(!runtime_dir_is_usable(&runtime_dir));
}

#[cfg(unix)]
#[test]
fn runtime_dir_is_usable_with_python_and_java_stubs() {
    let root = temp_test_dir("runtime-with-java");
    let runtime_dir = create_fake_runtime_tree(&root, "1.2.2-runtime1", true);
    assert!(runtime_dir_is_usable(&runtime_dir));
}

/// 运行环境归属的几种 manifest:只有「self」写着本应用;别的应用、没有身份戳(2.6.6 之前的旧包)、
/// 戳不是字符串、manifest 读不出来,都不是本应用可用的运行环境。
#[cfg(unix)]
fn runtime_owner_manifest_cases() -> Vec<(&'static str, String)> {
    let base = |extra: serde_json::Value| {
        let mut manifest =
            serde_json::json!({ "version": "1.2.2-runtime1", "built_at": "2026-04-07 00:00:00" });
        if let (Some(target), Some(fields)) = (manifest.as_object_mut(), extra.as_object()) {
            for (key, value) in fields {
                target.insert(key.clone(), value.clone());
            }
        }
        manifest.to_string() + "\n"
    };
    vec![
        ("self", base(serde_json::json!({ "appName": APP_NAME }))),
        (
            "other",
            base(serde_json::json!({ "appName": format!("{APP_NAME} 另一个") })),
        ),
        ("unstamped", base(serde_json::json!({}))),
        ("not-a-string", base(serde_json::json!({ "appName": 1 }))),
        ("unreadable", "{ not json".to_string()),
    ]
}

#[cfg(unix)]
#[test]
fn runtime_dir_usable_only_when_manifest_names_this_app() {
    let root = temp_test_dir("runtime-owner");
    let runtime_dir = create_fake_runtime_tree(&root, "1.2.2-runtime1", true);
    for (label, manifest) in runtime_owner_manifest_cases() {
        fs::write(runtime_dir.join("runtime-manifest.json"), &manifest).unwrap();
        assert_eq!(
            runtime_dir_is_usable(&runtime_dir),
            label == "self",
            "{label}: {manifest}"
        );
    }
    let _ = fs::remove_dir_all(&root);
}

/// 安装器(postinstall)与壳层对「这份运行环境是不是本应用的」用同一判据:
/// 把模板里的 runtime_dir_is_usable 原样抠出来,在同一组 manifest 上真跑,结论逐个相同。
#[cfg(target_os = "macos")]
#[test]
fn postinstall_runtime_owner_check_matches_shell() {
    let template = fs::read_to_string(repo_postinstall_template_path()).expect("read template");
    let start = template
        .find("runtime_dir_is_usable() {")
        .expect("缺 runtime_dir_is_usable");
    let end = start + template[start..].find("\n}\n").expect("函数没收尾") + 3;
    let func = &template[start..end];
    let root = temp_test_dir("postinstall-owner");
    let runtime_dir = create_fake_runtime_tree(&root, "1.2.2-runtime1", true);
    for (label, manifest) in runtime_owner_manifest_cases() {
        fs::write(runtime_dir.join("runtime-manifest.json"), &manifest).unwrap();
        let script = format!(
            "APP_NAME={}\n{}\nruntime_dir_is_usable {}\n",
            shell_quote_text(APP_NAME),
            func,
            shell_quote(&runtime_dir)
        );
        let installer_ok = Command::new("/bin/bash")
            .arg("-c")
            .arg(&script)
            .status()
            .expect("run postinstall snippet")
            .success();
        assert_eq!(installer_ok, label == "self", "postinstall {label}");
        assert_eq!(
            runtime_dir_is_usable(&runtime_dir),
            installer_ok,
            "壳层与安装器判据不一致: {label}"
        );
    }
    let _ = fs::remove_dir_all(&root);
}

#[test]
fn handoff_to_installed_app_only_when_target_is_newer() {
    let current_bundle = Path::new("/Users/test/Applications/星阙.app");
    let target_bundle = Path::new("/Applications/星阙.app");
    let current = Version::parse("1.2.1").unwrap();
    let target = Version::parse("1.2.3").unwrap();
    assert!(should_handoff_to_installed_app(
        current_bundle,
        target_bundle,
        Some(&current),
        Some(&target)
    ));
    assert!(!should_handoff_to_installed_app(
        target_bundle,
        target_bundle,
        Some(&target),
        Some(&target)
    ));
    assert!(!should_handoff_to_installed_app(
        current_bundle,
        target_bundle,
        Some(&target),
        Some(&current)
    ));
}

#[cfg(unix)]
#[test]
fn runtime_dir_usability_writes_health_cache() {
    let root = temp_test_dir("runtime-health-cache");
    let runtime_dir = create_fake_runtime_tree(&root, "1.2.3-runtime1", true);
    assert!(runtime_dir_is_usable(&runtime_dir));
    assert!(runtime_health_cache_path(&runtime_dir).exists());
}

#[cfg(unix)]
#[test]
fn runtime_health_cache_is_invalidated_when_runtime_changes() {
    let root = temp_test_dir("runtime-health-cache-invalidate");
    let runtime_dir = create_fake_runtime_tree(&root, "1.2.3-runtime1", true);
    assert!(runtime_dir_is_usable(&runtime_dir));
    let cache_path = runtime_health_cache_path(&runtime_dir);
    assert!(cache_path.exists());
    std::thread::sleep(Duration::from_secs(1));
    fs::write(
        runtime_dir.join("runtime-manifest.json"),
        serde_json::json!({ "version": "1.3.1-runtime3", "appName": APP_NAME }).to_string() + "\n",
    )
    .unwrap();
    let cache = runtime_health_cache(&runtime_dir).expect("cache exists");
    assert!(!runtime_health_cache_matches(&runtime_dir, &cache));
    assert!(runtime_dir_is_usable(&runtime_dir));
}

// postinstall 预置信任:子命令双写(健康缓存+fast-path 标记)后,
// runtime_fast_path_allowed 必须放行 —— 首真启走 trusted 档的机器证明;
// manifest 缺失=71 且绝不放行(负锚)。
#[cfg(unix)]
#[test]
fn preseed_health_cli_enables_trusted_fast_path() {
    let root = temp_test_dir("preseed-health-ok");
    let runtime_dir = create_fake_runtime_tree(&root, "9.9.9-runtime1", true);
    assert!(!runtime_fast_path_allowed(&runtime_dir));
    let code = run_preseed_health_cli(&runtime_dir);
    assert_eq!(code, 0);
    assert!(runtime_fast_path_allowed(&runtime_dir));
    assert!(runtime_health_cache(&runtime_dir)
        .map(|c| runtime_health_cache_matches(&runtime_dir, &c))
        .unwrap_or(false));
}

#[cfg(unix)]
#[test]
fn preseed_health_cli_refuses_without_manifest() {
    let root = temp_test_dir("preseed-health-nomanifest");
    let runtime_dir = root.join("current");
    fs::create_dir_all(&runtime_dir).unwrap();
    let code = run_preseed_health_cli(&runtime_dir);
    assert_eq!(code, 71);
    assert!(!runtime_fast_path_allowed(&runtime_dir));
}

// ── [首启原生库预检] ──────────────────────────────────────────────────────
// Mach-O 判定:瘦 / 胖各一;Java class(与胖文件同魔数)、脚本、残缺文件头必须判否。
#[test]
fn native_prewarm_slices_recognize_macho_and_reject_java_class() {
    let thin = [0xcf, 0xfa, 0xed, 0xfe, 0, 0, 0, 0];
    assert_eq!(native_prewarm_slices(&thin, 4096), vec![(0, 4096)]);
    // 胖文件两片:x86_64 在 0x1000 长 0x100;arm64 在 0x4000 长 0x200
    let mut fat = vec![0xca, 0xfe, 0xba, 0xbe, 0, 0, 0, 2];
    fat.extend_from_slice(&0x0100_0007i32.to_be_bytes());
    fat.extend_from_slice(&3i32.to_be_bytes());
    fat.extend_from_slice(&0x1000u32.to_be_bytes());
    fat.extend_from_slice(&0x100u32.to_be_bytes());
    fat.extend_from_slice(&12u32.to_be_bytes());
    fat.extend_from_slice(&0x0100_000ci32.to_be_bytes());
    fat.extend_from_slice(&0i32.to_be_bytes());
    fat.extend_from_slice(&0x4000u32.to_be_bytes());
    fat.extend_from_slice(&0x200u32.to_be_bytes());
    fat.extend_from_slice(&14u32.to_be_bytes());
    let want = if cfg!(target_arch = "aarch64") {
        vec![(0x4000u64, 0x200u64)]
    } else {
        vec![(0x1000u64, 0x100u64)]
    };
    assert_eq!(native_prewarm_slices(&fat, 0x8000), want);
    // 切片越出文件末尾的条目丢弃
    assert!(native_prewarm_slices(&fat, 0x1000).is_empty());
    // Java class:CAFEBABE + 版本号 52
    let class = [0xca, 0xfe, 0xba, 0xbe, 0x00, 0x00, 0x00, 0x34];
    assert!(native_prewarm_slices(&class, 4096).is_empty());
    assert!(native_prewarm_slices(b"#!/bin/sh\n", 10).is_empty());
    assert!(native_prewarm_slices(&[0xcf, 0xfa], 2).is_empty());
}

#[test]
fn native_prewarm_tiers_put_startup_libraries_first() {
    let (tiers, startup) = native_prewarm_tiers();
    assert!(tiers.len() >= 4, "顺序表至少四档");
    assert!(startup >= 1 && startup as usize <= tiers.len());
    let t = |rel: &str| native_prewarm_tier_of(rel, &tiers);
    let py = t("runtime/mac/python/bin/python3.12");
    let jvm = t("runtime/mac/java/lib/server/libjvm.dylib");
    let dynload = t("runtime/mac/python/lib/python3.12/lib-dynload/_ssl.cpython-312-darwin.so");
    let pandas = t(
        "runtime/mac/python/lib/python3.12/site-packages/pandas/_libs/index.cpython-312-darwin.so",
    );
    let swe = t("runtime/mac/python/lib/python3.12/site-packages/swisseph.cpython-312-darwin.so");
    let other_pkg = t(
        "runtime/mac/python/lib/python3.12/site-packages/scipy/linalg/_fblas.cpython-312-darwin.so",
    );
    let other_java = t("runtime/mac/java/lib/libawt_lwawt.dylib");
    assert!(py < dynload && jvm < dynload && dynload < pandas);
    assert_eq!(pandas, swe);
    assert!(pandas < startup, "预热要装的包必须落在启动档内");
    assert_eq!(other_pkg, tiers.len() as u32);
    assert_eq!(other_java, tiers.len() as u32);
}

#[test]
fn native_prewarm_switch_reads_zero_as_off() {
    assert!(native_prewarm_enabled_from(None));
    assert!(native_prewarm_enabled_from(Some("1")));
    assert!(!native_prewarm_enabled_from(Some("0")));
    assert!(!native_prewarm_enabled_from(Some(" 0 ")));
}

// 标记跟的是「文件身份」:整目录改名不用重做;克隆 / 拷贝出来的树(标记文件也跟着拷过去)必须重做。
// 应用内更新的第一步就是克隆当前运行时,所以更新后的那棵树一定要重新预检。
#[cfg(unix)]
#[test]
fn native_prewarm_marker_follows_file_identity() {
    let root = temp_test_dir("native-prewarm-marker");
    let runtime_dir = create_fake_runtime_tree(&root, "9.9.9-runtime1", true);
    assert!(native_prewarm_needed(&runtime_dir));
    let stats = native_prewarm_run(&runtime_dir, 2, Duration::from_secs(30), None);
    assert!(stats.complete && !stats.timed_out);
    assert!(!native_prewarm_needed(&runtime_dir));

    let renamed = root.join("runtime/renamed");
    fs::rename(&runtime_dir, &renamed).unwrap();
    assert!(!native_prewarm_needed(&renamed));

    let cloned = root.join("runtime/cloned");
    clone_dir_fast(&renamed, &cloned).unwrap();
    assert!(cloned.join(NATIVE_PREWARM_MARKER_FILE).exists());
    assert!(native_prewarm_needed(&cloned));

    let mut marker = native_prewarm_marker(&renamed).unwrap();
    marker.complete = false;
    fs::write(
        renamed.join(NATIVE_PREWARM_MARKER_FILE),
        serde_json::to_string(&marker).unwrap(),
    )
    .unwrap();
    assert!(native_prewarm_needed(&renamed));

    let empty = root.join("runtime/empty");
    fs::create_dir_all(&empty).unwrap();
    assert!(!native_prewarm_needed(&empty));
}

#[cfg(target_os = "macos")]
#[test]
fn native_prewarm_touch_handles_real_binary_and_plain_file() {
    let exe = std::env::current_exe().unwrap();
    assert!(native_prewarm_is_macho(&exe));
    assert!(native_prewarm_touch(&exe).is_some());
    let root = temp_test_dir("native-prewarm-touch");
    let plain = root.join("plain.txt");
    fs::write(&plain, b"hello").unwrap();
    assert!(!native_prewarm_is_macho(&plain));
    assert!(native_prewarm_touch(&plain).is_none());
    assert!(native_prewarm_touch(&root.join("missing.dylib")).is_none());
}

#[cfg(target_os = "macos")]
#[test]
fn native_prewarm_collects_only_macho_in_priority_order() {
    use std::os::unix::fs::PermissionsExt;
    let root = temp_test_dir("native-prewarm-collect");
    let runtime_dir = create_fake_runtime_tree(&root, "9.9.9-runtime1", true);
    let exe = std::env::current_exe().unwrap();
    let put = |rel: &str| {
        let path = runtime_dir.join(rel);
        fs::create_dir_all(path.parent().unwrap()).unwrap();
        fs::copy(&exe, &path).unwrap();
    };
    put("runtime/mac/python/lib/python3.12/site-packages/zzz/other.so");
    put("runtime/mac/python/lib/python3.12/lib-dynload/_a.so");
    put("runtime/mac/java/lib/server/libjvm.dylib");
    // 扩展名像、内容不是 / 带执行位的脚本 / Java class:都不收
    fs::write(
        runtime_dir.join("runtime/mac/python/lib/python3.12/lib-dynload/fake.so"),
        b"not a mach-o",
    )
    .unwrap();
    let script = runtime_dir.join("runtime/mac/java/bin/tool.sh");
    fs::write(&script, b"#!/bin/sh\n").unwrap();
    fs::set_permissions(&script, fs::Permissions::from_mode(0o755)).unwrap();
    fs::write(
        runtime_dir.join("runtime/mac/java/lib/A.class"),
        [0xca, 0xfe, 0xba, 0xbe, 0, 0, 0, 0x34],
    )
    .unwrap();
    let (tiers, _) = native_prewarm_tiers();
    let got: Vec<String> = native_prewarm_collect(&runtime_dir, &tiers)
        .into_iter()
        .map(|(_, p)| {
            p.strip_prefix(&runtime_dir)
                .unwrap()
                .to_string_lossy()
                .to_string()
        })
        .collect();
    assert_eq!(
        got,
        vec![
            "runtime/mac/java/lib/server/libjvm.dylib".to_string(),
            "runtime/mac/python/lib/python3.12/lib-dynload/_a.so".to_string(),
            "runtime/mac/python/lib/python3.12/site-packages/zzz/other.so".to_string(),
        ]
    );
    let stats = native_prewarm_run(&runtime_dir, 2, Duration::from_secs(60), None);
    assert_eq!(stats.files, 3);
    assert_eq!(stats.startup_files, 2);
    assert_eq!(stats.touched, 3);
    assert!(stats.complete);
    let marker = native_prewarm_marker(&runtime_dir).unwrap();
    assert!(marker.complete && marker.files == 3);
}

// [更新槽复用] 标记身份掺部件锁摘要:锁内容变了(换过部件)即使三个 inode 都没变也要重做
#[cfg(unix)]
#[test]
fn native_prewarm_identity_changes_when_component_lock_changes() {
    let root = temp_test_dir("native-prewarm-lock");
    let runtime_dir = create_fake_runtime_tree(&root, "9.9.9-runtime1", true);
    fs::write(runtime_dir.join("components-lock.json"), b"{\"v\":1}").unwrap();
    let before = native_prewarm_identity(&runtime_dir).unwrap();
    native_prewarm_run(&runtime_dir, 1, Duration::from_secs(10), None);
    assert!(!native_prewarm_needed(&runtime_dir));
    fs::write(runtime_dir.join("components-lock.json"), b"{\"v\":2}").unwrap();
    let after = native_prewarm_identity(&runtime_dir).unwrap();
    assert_ne!(before, after);
    assert!(native_prewarm_needed(&runtime_dir));
}

// [更新槽复用] 硬链接搭槽:嵌套文件同 inode、符号链接照抄、目录权限照抄、树根散文件是拷贝(独立 inode)
#[cfg(unix)]
#[test]
fn stage_dir_by_hardlink_shares_inodes_but_copies_root_files() {
    use std::os::unix::fs::{MetadataExt, PermissionsExt};
    let root = temp_test_dir("stage-hardlink");
    let src = root.join("current");
    write_file(&src.join("runtime/mac/python/bin/python3"), "py");
    write_file(&src.join("runtime/mac/java/lib/libjvm.dylib"), "jvm");
    write_file(&src.join("components-lock.json"), "{}");
    write_file(&src.join("runtime-manifest.json"), "{}");
    fs::set_permissions(
        src.join("runtime/mac/python/bin"),
        fs::Permissions::from_mode(0o755),
    )
    .unwrap();
    std::os::unix::fs::symlink("python3", src.join("runtime/mac/python/bin/python")).unwrap();
    let dst = root.join("stage");
    stage_dir_by_hardlink(&src, &dst).unwrap();
    let ino = |p: &Path| fs::metadata(p).unwrap().ino();
    assert_eq!(
        ino(&src.join("runtime/mac/python/bin/python3")),
        ino(&dst.join("runtime/mac/python/bin/python3"))
    );
    assert_eq!(
        ino(&src.join("runtime/mac/java/lib/libjvm.dylib")),
        ino(&dst.join("runtime/mac/java/lib/libjvm.dylib"))
    );
    assert_eq!(
        fs::metadata(dst.join("runtime/mac/java/lib/libjvm.dylib"))
            .unwrap()
            .nlink(),
        2
    );
    assert_ne!(
        ino(&src.join("components-lock.json")),
        ino(&dst.join("components-lock.json"))
    );
    assert_ne!(
        ino(&src.join("runtime-manifest.json")),
        ino(&dst.join("runtime-manifest.json"))
    );
    assert_eq!(
        fs::read_to_string(dst.join("components-lock.json")).unwrap(),
        "{}"
    );
    let link = dst.join("runtime/mac/python/bin/python");
    assert!(fs::symlink_metadata(&link)
        .unwrap()
        .file_type()
        .is_symlink());
    assert_eq!(fs::read_link(&link).unwrap(), PathBuf::from("python3"));
    assert_eq!(
        fs::metadata(dst.join("runtime/mac/python/bin"))
            .unwrap()
            .permissions()
            .mode()
            & 0o777,
        0o755
    );
    // 树根散文件就地改写不会写穿到源树
    fs::write(dst.join("components-lock.json"), "{\"changed\":true}").unwrap();
    assert_eq!(
        fs::read_to_string(src.join("components-lock.json")).unwrap(),
        "{}"
    );
}

// [更新槽复用] 增量手术后:未变文件与更新前同 inode(首次加载评估状态跟着走)、换了的文件是新 inode、
// previous 槽的旧内容与旧锁一字未动(回滚资本完好,证明手术全程没有就地覆盖写)。
#[cfg(unix)]
#[test]
fn component_apply_keeps_inodes_of_untouched_files_and_isolates_root_files() {
    use std::os::unix::fs::MetadataExt;
    let work = temp_test_dir("comp-apply-hardlink");
    let root = work.join("root");
    setup_v1_runtime(&root);
    write_file(&root.join("current/u/lib.so"), "untouched-native");
    let ino = |p: &Path| fs::metadata(p).unwrap().ino();
    let before_u = ino(&root.join("current/u/lib.so"));
    let before_keep = ino(&root.join("current/t/keep/k.txt"));
    let before_a = ino(&root.join("current/f/a.txt"));
    let before_lock = ino(&root.join("current/components-lock.json"));
    let staged = staged_v2(&work);
    apply_component_updates(&root, &staged).expect("incremental apply should succeed");
    let cur = root.join("current");
    let prev = root.join("previous");
    assert_eq!(
        ino(&cur.join("u/lib.so")),
        before_u,
        "未变文件必须还是同一个 inode"
    );
    assert_eq!(
        ino(&prev.join("u/lib.so")),
        before_u,
        "previous 与 current 共用未变文件"
    );
    assert_eq!(fs::metadata(cur.join("u/lib.so")).unwrap().nlink(), 2);
    assert_eq!(
        ino(&cur.join("t/keep/k.txt")),
        before_keep,
        "preserve 子树同样保身份"
    );
    assert_ne!(
        ino(&cur.join("f/a.txt")),
        before_a,
        "换了的文件必须是新 inode"
    );
    assert_eq!(fs::read_to_string(cur.join("f/a.txt")).unwrap(), "v2-a");
    assert_eq!(
        fs::read_to_string(prev.join("f/a.txt")).unwrap(),
        "v1-a",
        "旧树文件不得被覆盖写穿"
    );
    assert_ne!(
        ino(&cur.join("components-lock.json")),
        before_lock,
        "树根散文件是拷贝"
    );
    let prev_lock: serde_json::Value =
        serde_json::from_str(&fs::read_to_string(prev.join("components-lock.json")).unwrap())
            .unwrap();
    assert_eq!(
        prev_lock["runtimeVersion"], "1.0.0",
        "previous 的锁必须还是旧版"
    );
    let prev_manifest: serde_json::Value =
        serde_json::from_str(&fs::read_to_string(prev.join("runtime-manifest.json")).unwrap())
            .unwrap();
    assert_eq!(prev_manifest["version"], "1.0.0");
}

// [更新槽复用] 回退路(APFS 克隆)仍可用且语义同旧:全部文件都是新 inode
#[cfg(unix)]
#[test]
fn stage_runtime_copy_clone_fallback_gives_fresh_inodes() {
    use std::os::unix::fs::MetadataExt;
    let root = temp_test_dir("stage-clone-fallback");
    let src = root.join("current");
    write_file(&src.join("runtime/mac/java/lib/libjvm.dylib"), "jvm");
    let dst = root.join("stage");
    clone_dir_fast(&src, &dst).unwrap();
    assert_ne!(
        fs::metadata(src.join("runtime/mac/java/lib/libjvm.dylib"))
            .unwrap()
            .ino(),
        fs::metadata(dst.join("runtime/mac/java/lib/libjvm.dylib"))
            .unwrap()
            .ino()
    );
    assert_eq!(
        fs::read_to_string(dst.join("runtime/mac/java/lib/libjvm.dylib")).unwrap(),
        "jvm"
    );
}

// 预检这一块只许做文件级校验调用:不许出现可执行映射 / 动态加载(那会执行库里的代码)。
#[test]
fn native_prewarm_block_never_maps_or_loads_code() {
    let source = include_str!("runtime_prewarm.rs");
    let begin = source
        .find("// [首启原生库预检] 装包 / 更新后第一次打开")
        .expect("预检块首标记");
    let end = source[begin..]
        .find("// ── [首启原生库预检] 块尾")
        .expect("预检块尾标记")
        + begin;
    let block = &source[begin..end];
    assert!(block.contains("NATIVE_PREWARM_F_CHECK_LV"));
    assert!(block.contains("NATIVE_PREWARM_F_ADDFILESIGS_RETURN"));
    for banned in ["mmap(", "dlopen(", "libloading", "Command::new"] {
        assert!(!block.contains(banned), "预检块里不许出现 {}", banned);
    }
}

#[cfg(unix)]
#[test]
fn runtime_fast_path_marker_is_invalidated_when_runtime_changes() {
    let root = temp_test_dir("runtime-fast-path-invalidate");
    let runtime_dir = create_fake_runtime_tree(&root, "1.2.3-runtime1", true);
    let manifest =
        read_runtime_manifest_from_path(&runtime_dir.join("runtime-manifest.json")).unwrap();
    write_runtime_fast_path_marker(&runtime_dir, &manifest);
    assert!(runtime_fast_path_allowed(&runtime_dir));
    std::thread::sleep(Duration::from_secs(1));
    fs::write(
        runtime_dir.join("runtime-manifest.json"),
        "{\"version\":\"1.3.1-runtime3\"}\n",
    )
    .unwrap();
    assert!(!runtime_fast_path_allowed(&runtime_dir));
    clear_runtime_fast_path_marker(&runtime_dir);
}

#[test]
fn clear_runtime_pending_marker_only_touches_shared_runtime_marker() {
    // 进程级环境变量(HOROSA_SHARED_RUNTIME_DIR)被并行测试线程共享:与 helper 用例同锁串行,否则偶发互踩(cargo 全套实抓)
    let _env = HELPER_ENV_LOCK.lock().unwrap_or_else(|e| e.into_inner());
    let root = temp_test_dir("runtime-pending-clear");
    let shared_runtime = root.join("Users/Shared/Horosa/runtime/current");
    let shared_root = shared_runtime
        .parent()
        .unwrap()
        .parent()
        .unwrap()
        .to_path_buf();
    let pending = shared_root.join("runtime-install-pending.txt");
    fs::create_dir_all(shared_runtime.parent().unwrap()).unwrap();
    fs::write(&pending, "pending\n").unwrap();

    std::env::set_var("HOROSA_SHARED_RUNTIME_DIR", &shared_runtime);
    clear_runtime_pending_marker(&shared_runtime).unwrap();
    assert!(!pending.exists());

    fs::write(&pending, "pending\n").unwrap();
    let user_runtime = root.join("user/runtime/current");
    clear_runtime_pending_marker(&user_runtime).unwrap();
    assert!(pending.exists());

    fs::remove_file(&pending).unwrap();
    std::env::remove_var("HOROSA_SHARED_RUNTIME_DIR");
}

#[cfg(unix)]
#[test]
fn clear_runtime_pending_marker_ignores_permission_denied_for_shared_runtime_marker() {
    // 进程级环境变量(HOROSA_SHARED_RUNTIME_DIR)被并行测试线程共享:与 helper 用例同锁串行,否则偶发互踩(cargo 全套实抓)
    let _env = HELPER_ENV_LOCK.lock().unwrap_or_else(|e| e.into_inner());
    use std::os::unix::fs::PermissionsExt;

    let root = temp_test_dir("runtime-pending-clear-permissions");
    let shared_runtime = root.join("Users/Shared/Horosa/runtime/current");
    let shared_root = shared_runtime
        .parent()
        .unwrap()
        .parent()
        .unwrap()
        .to_path_buf();
    let pending = shared_root.join("runtime-install-pending.txt");
    fs::create_dir_all(shared_runtime.parent().unwrap()).unwrap();
    fs::write(&pending, "pending\n").unwrap();

    std::env::set_var("HOROSA_SHARED_RUNTIME_DIR", &shared_runtime);

    let mut perms = fs::metadata(&shared_root).unwrap().permissions();
    perms.set_mode(0o555);
    fs::set_permissions(&shared_root, perms).unwrap();

    clear_runtime_pending_marker(&shared_runtime).unwrap();
    assert!(pending.exists());

    let mut restore = fs::metadata(&shared_root).unwrap().permissions();
    restore.set_mode(0o755);
    fs::set_permissions(&shared_root, restore).unwrap();

    fs::remove_file(&pending).unwrap();
    std::env::remove_var("HOROSA_SHARED_RUNTIME_DIR");
}

#[test]
fn parse_marker_kv_reads_expected_fields() {
    let values = parse_marker_kv(
        "version=1.0.25\nruntime_version=1.0.25-runtime1\ninstalled_at=2026-03-17 20:00:00\nrelaunch_status=pending_manual\n",
    );
    assert_eq!(values.get("version").map(String::as_str), Some("1.0.25"));
    assert_eq!(
        values.get("runtime_version").map(String::as_str),
        Some("1.0.25-runtime1")
    );
    assert_eq!(
        values.get("installed_at").map(String::as_str),
        Some("2026-03-17 20:00:00")
    );
    assert_eq!(
        values.get("relaunch_status").map(String::as_str),
        Some("pending_manual")
    );
}

#[test]
fn update_helper_script_waits_for_old_process_and_marks_completion() {
    let root = temp_test_dir("update-helper-script");
    let script = build_update_helper_script(
        &root.join("update.log"),
        &root.join("update-complete.txt"),
        Path::new("/Applications/星阙.app"),
        Path::new("/tmp/星阙.app"),
        "501",
        "horacedong",
        "43210",
        "horosa-desktop-installer",
        "1.0.25",
        Some("1.0.25-runtime1"),
        "",
    );
    assert!(script.contains("wait_for_old_app_exit"));
    assert!(script.contains("mark_update_complete"));
    assert!(script.contains("open -n"));
    assert!(script.contains("pgrep -f"));
    assert!(script.contains("wait_for_stable_relaunch"));
    assert!(script.contains("activate_app_once"));
    assert!(script.contains("osascript -e"));
    assert!(script.contains("EXPECTED_VERSION="));
    assert!(script.contains("1.0.25"));
    assert!(script.contains("EXPECTED_RUNTIME_VERSION="));
    assert!(script.contains("1.0.25-runtime1"));
    assert!(script.contains("relaunch_status="));
    assert!(script.contains("pending_manual"));
    assert!(script.contains("auto_relaunch_confirmed"));
    assert!(!script.contains("open_app || true"));
}

#[test]
fn install_review_does_not_force_replace_for_healthy_existing_app() {
    assert!(!should_recommend_installed_app_replacement(
        AssetReviewMode::Install,
        DetectedAssetState::Healthy
    ));
    assert!(should_recommend_installed_app_replacement(
        AssetReviewMode::Install,
        DetectedAssetState::Outdated
    ));
}

#[test]
fn exit_cleanup_claim_is_single_shot() {
    // 退出双回调(ExitRequested+Exit)/app.exit(0) 双发场景下,stop 脚本只许 spawn 一次。
    assert!(claim_exit_cleanup(), "first claim must win");
    assert!(!claim_exit_cleanup(), "second claim must lose");
    assert!(!claim_exit_cleanup(), "subsequent claims must lose");
}

fn repo_stop_script_path() -> PathBuf {
    Path::new(env!("CARGO_MANIFEST_DIR")).join("../../Horosa-Web/stop_horosa_local.sh")
}

fn repo_start_script_path() -> PathBuf {
    Path::new(env!("CARGO_MANIFEST_DIR")).join("../../Horosa-Web/start_horosa_local.sh")
}

/// 主实例身份由进程锁决定(与端口无关):先拿到锁的是主实例;锁被占着 = 独立实例;前一个进程退出后下一个接任。
#[cfg(unix)]
#[test]
fn primary_instance_role_follows_process_lock_not_port() {
    let root = temp_test_dir("instance-lock");
    let path = root.join("data").join(PRIMARY_INSTANCE_LOCK_FILE);
    let (first, first_file) = instance_role_for_lock(&path);
    assert_eq!(first, Some("primary"));
    assert!(first_file.is_some());
    let (second, second_file) = instance_role_for_lock(&path);
    assert_eq!(second, Some("independent"), "锁被占着时应判独立实例");
    assert!(second_file.is_none());
    drop(first_file);
    let (third, third_file) = instance_role_for_lock(&path);
    assert_eq!(third, Some("primary"), "前一个主实例退出后下一个接任");
    drop(third_file);
    // 锁文件开不出来(父路径是个文件):不下结论,页面照旧按端口推断
    let blocker = root.join("blocker");
    fs::write(&blocker, "x").unwrap();
    assert_eq!(instance_role_for_lock(&blocker.join("lock")).0, None);
    // 初始化脚本把身份写成只读全局量(页面 shellInstanceRole 读它)
    let script = instance_role_init_script("independent");
    assert!(script.contains("\"__HOROSA_INSTANCE_ROLE__\""));
    assert!(script.contains("value: \"independent\""));
    assert!(script.contains("writable: false"));
    let _ = fs::remove_dir_all(&root);
}

/// 静态服务器退役(同口重起)后,旧服务器上的空闲长连接必须当场关掉:客户端再拿它发请求只会看到连接已关
/// (浏览器对幂等请求换新连接重试,落到新服务器),而不是一个「服务已停」的 503(浏览器不重试 → 白页 / 分包加载失败)。
#[test]
fn retired_http_server_closes_idle_keepalive_connections() {
    use std::io::{Read, Write};
    let server = Arc::new(tiny_http::Server::http("127.0.0.1:0").expect("bind"));
    let port = server.server_addr().to_ip().expect("ip").port();
    let worker = {
        let server = Arc::clone(&server);
        thread::spawn(move || {
            if let Ok(Some(rq)) = server.recv_timeout(Duration::from_secs(5)) {
                let _ = rq.respond(tiny_http::Response::from_string("SERVER-A"));
            }
        })
    };
    let mut client = std::net::TcpStream::connect(("127.0.0.1", port)).expect("connect");
    client
        .set_read_timeout(Some(Duration::from_secs(3)))
        .unwrap();
    client
        .write_all(b"GET /index.html HTTP/1.1\r\nHost: 127.0.0.1\r\n\r\n")
        .unwrap();
    let mut first = Vec::new();
    let mut buf = [0u8; 1024];
    while !String::from_utf8_lossy(&first).ends_with("SERVER-A") {
        let n = client.read(&mut buf).expect("read first response");
        assert!(n > 0, "首个回应没收全");
        first.extend_from_slice(&buf[..n]);
    }
    assert!(String::from_utf8_lossy(&first).starts_with("HTTP/1.1 200"));
    worker.join().unwrap();
    drop(server); // 最后一个持有者放手 = 退役
    thread::sleep(Duration::from_millis(300));
    let _ = client.write_all(b"GET /index.html HTTP/1.1\r\nHost: 127.0.0.1\r\n\r\n");
    let mut second = Vec::new();
    loop {
        match client.read(&mut buf) {
            Ok(0) | Err(_) => break,
            Ok(n) => second.extend_from_slice(&buf[..n]),
        }
    }
    let text = String::from_utf8_lossy(&second);
    assert!(
        !text.contains("503"),
        "旧长连接上的请求拿到了 503(应当是连接已关): {text}"
    );
    assert!(text.is_empty(), "旧长连接上不该再有任何回应: {text}");
}

fn repo_postinstall_template_path() -> PathBuf {
    Path::new(env!("CARGO_MANIFEST_DIR")).join("../installer-scripts/postinstall.template")
}

// ── 共享运行环境只给安装者写(其他账户只读加载)──────────────────────────────

/// 造一棵带各种「放开写」权限的小树:目录 0777、普通文件 0666、可执行 0775(组 = staff = 所有本机账户)、只读 0444。
#[cfg(unix)]
fn make_open_tree(root: &Path) -> Vec<PathBuf> {
    use std::os::unix::fs::PermissionsExt;
    let dir = root.join("Horosa-Web/astrostudyui/dist-file");
    fs::create_dir_all(&dir).unwrap();
    let files = vec![
        (root.join("Horosa-Web/start_horosa_local.sh"), 0o775),
        (dir.join("index.html"), 0o666),
        (root.join("lib.so"), 0o775),
        (root.join("ro.dylib"), 0o444),
    ];
    for (path, mode) in &files {
        fs::write(path, "x").unwrap();
        fs::set_permissions(path, fs::Permissions::from_mode(*mode)).unwrap();
    }
    for d in [root.to_path_buf(), root.join("Horosa-Web"), dir.clone()] {
        fs::set_permissions(&d, fs::Permissions::from_mode(0o777)).unwrap();
    }
    let mut all: Vec<PathBuf> = files.into_iter().map(|(p, _)| p).collect();
    all.extend([root.to_path_buf(), root.join("Horosa-Web"), dir]);
    all
}

/// 树里每一项:组 / 其他账户不可写,所有账户可读,属主可写;目录与原本可执行的文件所有账户可进入 / 执行。
#[cfg(unix)]
fn assert_owner_only_writable(paths: &[PathBuf]) {
    use std::os::unix::fs::PermissionsExt;
    for path in paths {
        let meta = fs::symlink_metadata(path).unwrap();
        let mode = meta.permissions().mode() & 0o7777;
        assert_eq!(
            mode & 0o022,
            0,
            "{} 仍对组 / 其他账户可写: {:o}",
            path.display(),
            mode
        );
        assert_eq!(
            mode & 0o444,
            0o444,
            "{} 不是所有账户可读: {:o}",
            path.display(),
            mode
        );
        assert_ne!(mode & 0o200, 0, "{} 属主不可写: {:o}", path.display(), mode);
        if meta.is_dir() {
            assert_eq!(
                mode & 0o111,
                0o111,
                "目录 {} 不是所有账户可进入: {:o}",
                path.display(),
                mode
            );
        }
    }
}

/// 早先安装包留下的旧共享树:别的账户所有 + 所有账户可写 ⇒ 报出(要整包更新,App 里不提权);本账户名下的只报「可收紧」、
/// 检查本身不改权限(读路径无副作用),用户确认后 seal_my_open_shared_tree_at 才收紧;干净的树不报;
/// 更新策略据此只通知、引导完整安装包(不走 App 内增量 / 全量下载)
#[cfg(unix)]
#[test]
fn legacy_open_shared_tree_detected_and_forces_full_pkg() {
    use std::os::unix::fs::PermissionsExt;
    let shared = temp_test_dir("legacy-shared");
    let root = shared.join("runtime");
    let cur = root.join("current/Horosa-Web");
    fs::create_dir_all(&cur).unwrap();
    fs::write(cur.join("start_horosa_local.sh"), "x").unwrap();
    for d in [root.clone(), root.join("current"), cur.clone()] {
        fs::set_permissions(&d, fs::Permissions::from_mode(0o777)).unwrap();
    }
    let me = unsafe { libc::geteuid() };
    // 视作别的账户所有(当前进程收不动):报出
    let found = legacy_open_shared_tree_at(&shared, &root, me.wrapping_add(1))
        .expect("别人名下所有账户可写的树必须报出");
    assert_eq!(found.path, root, "{found:?}");
    assert!(found.message_in(false).contains("完整安装包"), "{found:?}");
    // 同一发现,两个档的话都从表里取(原生对话框随界面简繁)
    assert!(found.message_in(true).contains("完整安裝包"), "{found:?}");
    assert!(found.message_in(true).contains(&root.display().to_string()));
    assert_eq!(
        fs::metadata(&root).unwrap().permissions().mode() & 0o002,
        0o002,
        "别人名下的不该被本账户改动"
    );
    // 本账户名下的:不算 foreign;检查不改权限,只列进 mine_open 并给「可收紧」提示
    assert!(legacy_open_shared_tree_at(&shared, &root, me).is_none());
    let mine = inspect_shared_tree_at(&shared, &root, me);
    assert!(mine.mine_open.contains(&root), "{mine:?}");
    let (warn, fixable) = mine.warning();
    assert!(fixable && warn.unwrap_or_default().contains("收紧共享权限"));
    assert_eq!(
        fs::metadata(&root).unwrap().permissions().mode() & 0o002,
        0o002,
        "只读检查不许改权限"
    );
    // 用户确认后才收紧
    let after = seal_my_open_shared_tree_at(&shared, &root, me);
    assert!(
        after.mine_open.is_empty() && after.foreign.is_none(),
        "{after:?}"
    );
    for d in [root.clone(), root.join("current"), cur.clone()] {
        assert_eq!(
            fs::metadata(&d).unwrap().permissions().mode() & 0o022,
            0,
            "{} 应已收紧",
            d.display()
        );
    }
    // 收紧之后再看(哪怕当成别人名下)也不报;不存在的根不报
    assert!(legacy_open_shared_tree_at(&shared, &root, me.wrapping_add(1)).is_none());
    assert!(legacy_open_shared_tree_at(&shared.join("nope"), &root.join("nope"), me).is_none());
    // 更新策略:有发现 ⇒ notify_only + 话术指向完整安装包;没有 ⇒ 原样
    let mk = || UpdatePlan {
        latest_version: Version::parse("9.9.9").unwrap(),
        notes: String::new(),
        repo_url: String::new(),
        release_url: String::new(),
        app_url: String::new(),
        app_sha256: Some("a".into()),
        runtime_url: None,
        runtime_version: None,
        runtime_sha256: None,
        components: None,
        components_lock_url: None,
        components_lock_sha256: None,
        app_size_bytes: None,
        runtime_size_bytes: None,
        allow_downgrade: false,
        source: UpdateSource::Manifest,
        notify_only: false,
        full_pkg_reason: None,
    };
    let mut plan = mk();
    apply_shared_tree_policy(&mut plan, Some(found.clone()));
    assert!(plan.notify_only);
    assert!(
        plan.notify_only_message().contains(".pkg"),
        "{}",
        plan.notify_only_message()
    );
    assert!(
        plan.notify_only_message_in(true).contains("請到發佈頁"),
        "{}",
        plan.notify_only_message_in(true)
    );
    assert!(plan.notify_only_message_in(true).contains("完整安裝包"));
    let mut clean = mk();
    apply_shared_tree_policy(&mut clean, None);
    assert!(!clean.notify_only && clean.full_pkg_reason.is_none());
    assert!(clean.notify_only_message_in(false).contains("更新清单"));
    assert!(clean.notify_only_message_in(true).contains("更新清單"));
    let _ = fs::remove_dir_all(&shared);
}

/// 共享根本身 / downloads / install-source.json 开着(runtime 已收紧)也要报:父目录可写 = 别的账户能把整个 runtime 换掉,
/// downloads 可写 = 能放伪造归档等本账户自愈时解压执行
#[cfg(unix)]
#[test]
fn legacy_open_shared_root_downloads_and_marker_detected() {
    use std::os::unix::fs::PermissionsExt;
    let me = unsafe { libc::geteuid() };
    let other = me.wrapping_add(1);
    for (label, rel) in [
        ("父目录开着", ""),
        ("downloads 开着", "downloads"),
        ("安装记录开着", "install-source.json"),
    ] {
        let shared = temp_test_dir("legacy-shared-root");
        let root = shared.join("runtime");
        fs::create_dir_all(root.join("current/Horosa-Web")).unwrap();
        fs::create_dir_all(shared.join("downloads")).unwrap();
        fs::write(shared.join("install-source.json"), "{}").unwrap();
        for d in [
            shared.clone(),
            shared.join("downloads"),
            root.clone(),
            root.join("current"),
            root.join("current/Horosa-Web"),
        ] {
            fs::set_permissions(&d, fs::Permissions::from_mode(0o755)).unwrap();
        }
        fs::set_permissions(
            shared.join("install-source.json"),
            fs::Permissions::from_mode(0o644),
        )
        .unwrap();
        assert!(
            legacy_open_shared_tree_at(&shared, &root, other).is_none(),
            "{label}:收紧的树不报"
        );
        let target = if rel.is_empty() {
            shared.clone()
        } else {
            shared.join(rel)
        };
        let mode = if target.is_dir() { 0o777 } else { 0o666 };
        fs::set_permissions(&target, fs::Permissions::from_mode(mode)).unwrap();
        let found = legacy_open_shared_tree_at(&shared, &root, other);
        assert!(
            found
                .as_ref()
                .map(|f| f.message_in(false))
                .unwrap_or_default()
                .contains(&target.display().to_string()),
            "{label} 必须报出:{found:?}"
        );
        let _ = fs::remove_dir_all(&shared);
    }
}

/// 自愈用的缓存归档:所在目录别的账户能写 ⇒ 不用;安装记录有 sha 且不符 ⇒ 不用;相符 / 没记录 ⇒ 可用;符号链接不用
#[cfg(unix)]
#[test]
fn cached_runtime_archive_trust_checks_perms_and_sha() {
    use std::os::unix::fs::PermissionsExt;
    let me = unsafe { libc::geteuid() };
    let shared = temp_test_dir("archive-trust");
    let root = shared.join("runtime");
    let dl = shared.join("downloads");
    fs::create_dir_all(&root).unwrap();
    fs::create_dir_all(&dl).unwrap();
    for d in [shared.clone(), dl.clone(), root.clone()] {
        fs::set_permissions(&d, fs::Permissions::from_mode(0o755)).unwrap();
    }
    let archive = dl.join("horosa-runtime-macos-arm64.tar.gz");
    fs::write(&archive, b"payload").unwrap();
    fs::set_permissions(&archive, fs::Permissions::from_mode(0o644)).unwrap();
    let good_sha = "239f59ed55e737c77147cf55ad0c1b030b6d7ee748a7426952f9b852d5a935e5";
    let mk = |sha: &str| InstallSourceMarker {
        source: InstallSource::PkgOffline,
        installed_at: None,
        runtime_version: None,
        app_version: None,
        runtime_archive_name: Some("horosa-runtime-macos-arm64.tar.gz".into()),
        runtime_archive_sha256: Some(sha.into()),
    };
    assert!(
        cached_archive_trust_at(&archive, &shared, &root, None, me).is_ok(),
        "没记录 sha:权限对就可用"
    );
    assert!(
        cached_archive_trust_at(&archive, &shared, &root, Some(&mk(good_sha)), me).is_ok(),
        "sha 相符可用"
    );
    let bad = cached_archive_trust_at(&archive, &shared, &root, Some(&mk(&"0".repeat(64))), me)
        .expect_err("sha 不符必须拒");
    assert!(bad.contains("sha256"), "{bad}");
    fs::set_permissions(&dl, fs::Permissions::from_mode(0o777)).unwrap();
    let open = cached_archive_trust_at(&archive, &shared, &root, None, me)
        .expect_err("downloads 别人能写必须拒");
    assert!(open.contains("都能写"), "{open}");
    fs::set_permissions(&dl, fs::Permissions::from_mode(0o755)).unwrap();
    fs::set_permissions(&shared, fs::Permissions::from_mode(0o777)).unwrap();
    assert!(
        cached_archive_trust_at(&archive, &shared, &root, None, me).is_err(),
        "共享根别人能写必须拒"
    );
    fs::set_permissions(&shared, fs::Permissions::from_mode(0o755)).unwrap();
    let link = dl.join("link.tar.gz");
    std::os::unix::fs::symlink(&archive, &link).unwrap();
    assert!(
        cached_archive_trust_at(&link, &shared, &root, None, me).is_err(),
        "符号链接不用"
    );
    // 属主是别的(非 root、非本账户、非安装者)账户:不用(把本进程当成另一个账户、运行环境根不存在 = 没有安装者)
    let foreign = cached_archive_trust_at(
        &archive,
        &shared,
        &shared.join("no-runtime"),
        None,
        me.wrapping_add(7),
    );
    assert!(foreign.is_err() || me == 0, "{foreign:?}");
    // 安装记录本身别人能写:不拿来核
    let marker_path = shared.join("install-source.json");
    fs::write(&marker_path, serde_json::to_string(&mk(good_sha)).unwrap()).unwrap();
    fs::set_permissions(&marker_path, fs::Permissions::from_mode(0o644)).unwrap();
    assert!(trusted_install_source_marker_at(&marker_path, &root, me).is_some());
    fs::set_permissions(&marker_path, fs::Permissions::from_mode(0o666)).unwrap();
    assert!(trusted_install_source_marker_at(&marker_path, &root, me).is_none());
    let _ = fs::remove_dir_all(&shared);
}
#[cfg(unix)]
#[test]
fn shared_tree_seal_leaves_write_to_owner_only() {
    use std::os::unix::fs::PermissionsExt;
    let root = temp_test_dir("seal-tree");
    let all = make_open_tree(&root);
    seal_tree_permissions(&root);
    assert_owner_only_writable(&all);
    // 原本可执行的照旧可执行(启动脚本 / 原生库)
    let script = root.join("Horosa-Web/start_horosa_local.sh");
    assert_eq!(
        fs::metadata(&script).unwrap().permissions().mode() & 0o111,
        0o111
    );
    let _ = fs::remove_dir_all(&root);
}

#[cfg(unix)]
#[test]
fn seal_shared_tree_permissions_only_touches_shared_domain() {
    use std::os::unix::fs::PermissionsExt;
    let _env = HELPER_ENV_LOCK.lock().unwrap_or_else(|e| e.into_inner());
    let root = temp_test_dir("seal-shared-domain");
    let shared_current = root.join("Users/Shared/Horosa/runtime/current");
    let user_current = root.join("user/runtime/current");
    fs::create_dir_all(&shared_current).unwrap();
    fs::create_dir_all(&user_current).unwrap();
    let shared_all = make_open_tree(&shared_current);
    make_open_tree(&user_current);
    std::env::set_var("HOROSA_SHARED_RUNTIME_DIR", &shared_current);
    seal_shared_tree_permissions(&shared_current);
    seal_shared_tree_permissions(&user_current);
    std::env::remove_var("HOROSA_SHARED_RUNTIME_DIR");
    assert_owner_only_writable(&shared_all);
    // 共享域之外(用户自己的运行环境)不动
    assert_eq!(
        fs::metadata(user_current.join("lib.so"))
            .unwrap()
            .permissions()
            .mode()
            & 0o7777,
        0o775
    );
    let _ = fs::remove_dir_all(&root);
}

#[cfg(unix)]
#[test]
fn postinstall_seals_shared_root_for_installing_user_only() {
    let template = fs::read_to_string(repo_postinstall_template_path()).expect("read template");
    // 任何一条把共享树放开给所有账户写的命令都不许回来
    let open_to_all = ["a+", "rw"].concat();
    assert!(
        !template.contains(&open_to_all),
        "postinstall 回归了把共享树放开给所有账户写"
    );
    // 六条收尾路径(延后 / 降级 / 保留 ×2 / 正常装完 / 在线首启延后)全部收权限
    let calls = template
        .lines()
        .filter(|l| l.trim() == "seal_shared_root")
        .count();
    assert!(calls >= 6, "seal_shared_root 调用只有 {calls} 处");
    // 把两个函数原样抠出来,在临时树上真跑(属主取当前账户 —— 非 root 也能 chown 给自己)
    let start = template
        .find("SHARED_OWNER_UID=\"\"")
        .expect("缺 SHARED_OWNER_UID");
    let end_marker = "seal_shared_root() {";
    let seal_start = template.find(end_marker).expect("缺 seal_shared_root");
    let seal_end = seal_start
        + template[seal_start..]
            .find("\n}\n")
            .expect("seal 函数没收尾")
        + 3;
    let snippet = &template[start..seal_end];
    let root = temp_test_dir("postinstall-seal");
    let shared = root.join("shared");
    fs::create_dir_all(&shared).unwrap();
    let all = make_open_tree(&shared);
    let script = format!(
        "set -euo pipefail\nSHARED_ROOT={}\n{}\nSHARED_OWNER_UID=\"$(/usr/bin/id -u)\"\nseal_shared_root\n",
        shell_quote(&shared),
        snippet
    );
    let status = Command::new("/bin/bash")
        .arg("-c")
        .arg(&script)
        .status()
        .expect("run seal snippet");
    assert!(status.success());
    assert_owner_only_writable(&all);
    let _ = fs::remove_dir_all(&root);
}

#[cfg(unix)]
#[test]
fn runtime_metadata_cleanup_tolerates_read_only_runtime() {
    use std::os::unix::fs::PermissionsExt;
    let root = temp_test_dir("metadata-readonly");
    let sub = root.join("Horosa-Web");
    fs::create_dir_all(&sub).unwrap();
    fs::write(sub.join("._junk"), "x").unwrap();
    fs::write(sub.join(".DS_Store"), "x").unwrap();
    fs::set_permissions(&sub, fs::Permissions::from_mode(0o555)).unwrap();
    // 其他账户只读加载:删不动的元数据垃圾不算失败,运行环境照样判可用
    let result = cleanup_runtime_metadata(&root);
    fs::set_permissions(&sub, fs::Permissions::from_mode(0o755)).unwrap();
    assert!(
        result.is_ok(),
        "只读运行环境上清元数据报错: {:?}",
        result.err()
    );
    assert!(sub.join("._junk").exists());
    // 可写时照旧清掉
    assert_eq!(cleanup_runtime_metadata(&root).unwrap(), 2);
    let _ = fs::remove_dir_all(&root);
}

#[cfg(unix)]
#[test]
fn path_writable_by_current_user_follows_nearest_existing_ancestor() {
    use std::os::unix::fs::PermissionsExt;
    let root = temp_test_dir("writable-probe");
    assert!(path_writable_by_current_user(&root.join("not/yet/created")));
    let ro = root.join("ro");
    fs::create_dir_all(&ro).unwrap();
    fs::set_permissions(&ro, fs::Permissions::from_mode(0o555)).unwrap();
    let ro_ok = path_writable_by_current_user(&ro);
    let ro_child_ok = path_writable_by_current_user(&ro.join("runtime"));
    fs::set_permissions(&ro, fs::Permissions::from_mode(0o755)).unwrap();
    assert!(!ro_ok);
    assert!(!ro_child_ok);
    let _ = fs::remove_dir_all(&root);
}

#[test]
fn read_only_shared_runtime_installs_into_user_root() {
    let shared = PathBuf::from("/Users/Shared/Horosa/runtime");
    let user = PathBuf::from("/Users/b/Library/Application Support/x/runtime");
    // 属主账户:照旧换共享那份
    assert_eq!(
        install_roots_for_decisions(true, false, shared.clone(), user.clone(), true),
        (vec![shared.clone()], false)
    );
    // 其他账户(共享只读):改道到自己的用户目录
    assert_eq!(
        install_roots_for_decisions(true, false, shared.clone(), user.clone(), false),
        (vec![user.clone()], true)
    );
    // 两份都选替换 + 共享只读:用户目录只装一次
    assert_eq!(
        install_roots_for_decisions(true, true, shared.clone(), user.clone(), false),
        (vec![user.clone()], true)
    );
    assert_eq!(
        install_roots_for_decisions(true, true, shared.clone(), user.clone(), true),
        (vec![shared.clone(), user.clone()], false)
    );
    assert_eq!(
        install_roots_for_decisions(false, false, shared, user, false),
        (vec![], false)
    );
}

fn pid_dir_block(script: &str) -> String {
    let begin = script
        .find("# [pid-dir:begin]")
        .expect("缺 [pid-dir:begin]");
    let end = script.find("# [pid-dir:end]").expect("缺 [pid-dir:end]");
    script[begin..end].to_string()
}

#[cfg(unix)]
#[test]
fn pid_dir_rule_matches_start_and_stop_scripts() {
    use std::os::unix::fs::PermissionsExt;
    let start = fs::read_to_string(repo_start_script_path()).unwrap();
    let stop = fs::read_to_string(repo_stop_script_path()).unwrap();
    let block = pid_dir_block(&start);
    assert_eq!(
        block,
        pid_dir_block(&stop),
        "start / stop 两个脚本的 pid 目录规则不一致"
    );
    // pid 文件全部挂在 PID_DIR 下(不再直接写运行环境目录)
    assert!(start.contains("PY_PID_FILE=\"${PID_DIR}/.horosa_py.${CHART_PORT}.pid\""));
    assert!(stop.contains("WEB_PID_FILE=\"${PID_DIR}/.horosa_web.${WEB_PORT}.pid\""));
    assert!(!start.contains("\"${ROOT}\"/.horosa_py.*.pid"));
    assert!(
        !stop.contains("\"${ROOT}\"/.horosa_py.*.pid"),
        "stop 脚本的全实例回收还在扫运行环境目录"
    );
    let root = temp_test_dir("pid-dir-rule");
    let home = root.join("home dir");
    fs::create_dir_all(&home).unwrap();
    let ro = root.join("ro tree/Horosa-Web");
    let rw = root.join("rw tree/Horosa-Web");
    fs::create_dir_all(&ro).unwrap();
    fs::create_dir_all(&rw).unwrap();
    fs::set_permissions(&ro, fs::Permissions::from_mode(0o555)).unwrap();
    let run = |web: &Path, override_dir: Option<&str>| -> String {
        let mut cmd = Command::new("/bin/bash");
        cmd.arg("-c")
            .arg(format!(
                "set -euo pipefail\nROOT={}\n{}\nprintf '%s' \"${{PID_DIR}}\"",
                shell_quote(web),
                block
            ))
            .env("HOME", &home)
            .env_remove("HOROSA_PID_DIR");
        if let Some(dir) = override_dir {
            cmd.env("HOROSA_PID_DIR", dir);
        }
        String::from_utf8(cmd.output().unwrap().stdout).unwrap()
    };
    let home_s = home.to_string_lossy().to_string();
    let got_ro = run(&ro, None);
    let got_rw = run(&rw, None);
    let got_override = run(&ro, Some("/tmp/explicit-pid-dir"));
    fs::set_permissions(&ro, fs::Permissions::from_mode(0o755)).unwrap();
    assert_eq!(
        PathBuf::from(&got_ro),
        runtime_pid_dir_for(&ro, &home_s, None, false),
        "只读运行环境:脚本与壳层算出的 pid 目录不一致"
    );
    assert!(got_ro.starts_with(&home_s) && got_ro.contains("Library/Caches/horosa-run/"));
    assert_eq!(
        PathBuf::from(&got_rw),
        runtime_pid_dir_for(&rw, &home_s, None, true)
    );
    assert_eq!(PathBuf::from(&got_rw), rw);
    assert_eq!(
        PathBuf::from(&got_override),
        runtime_pid_dir_for(&ro, &home_s, Some("/tmp/explicit-pid-dir"), false)
    );
    let _ = fs::remove_dir_all(&root);
}

#[test]
fn start_script_never_opens_jar_to_all_accounts() {
    let start = fs::read_to_string(repo_start_script_path()).unwrap();
    let code: String = start
        .lines()
        .filter(|l| !l.trim_start().starts_with('#'))
        .collect::<Vec<_>>()
        .join("\n");
    assert!(
        !code.contains(&["chmod a+", "rw"].concat()),
        "start 脚本回归了把 jar 放开给所有账户写"
    );
    // 只读运行环境:不往里拷 jar,直接用随包 jar
    assert!(code.contains("launching bundled jar in place"));
}

#[test]
fn update_helper_runtime_commands_hand_root_to_updater_without_opening_it() {
    let shared_root = Path::new("/Users/Shared/Horosa/runtime");
    let archive = Path::new("/tmp/horosa-runtime.tar.gz");
    for command in [
        build_single_runtime_update_command(shared_root, archive, Some("1.0.0-runtime1"), 0),
        build_single_runtime_update_command_legacy(shared_root, archive, Some("1.0.0-runtime1"), 0),
    ] {
        assert!(
            !command.contains(&["a+", "rwX"].concat()),
            "更新助手又把共享树放开给所有账户写"
        );
        // 不分根(共享根也一样)无条件归还:不许再出现「/Users/Shared 下跳过 chown」的分支
        assert!(
            command.contains(
                "if [ -n \"${USER_UID:-}\" ]; then /usr/sbin/chown -R \"${USER_UID}\" \"${RUNTIME_ROOT}\""
            ),
            "共享根没有归还发起更新的账户: {command}"
        );
        assert!(
            !command.contains("/Users/Shared/*) : ;;"),
            "共享根被排除在归还之外"
        );
    }
    let legacy = build_single_runtime_update_command_legacy(shared_root, archive, None, 0);
    assert!(legacy.contains("chmod -R u+rwX,go+rX,go-w"));
}

/// 早先安装包留下的共享树(root 所有、所有账户可写):应用更新助手收尾时不论换没换运行环境都收一遍权限;
/// 默认空定义 + 真定义随 runtime_cmd 带入,调用排在「完成标记」之前。
#[cfg(unix)]
#[test]
fn update_helper_seals_shared_runtime_even_without_runtime_update() {
    let seal = build_shared_runtime_seal_command(Path::new("/Users/Shared/Horosa"));
    assert!(seal.contains("seal_shared_runtime() {"));
    assert!(seal.contains(&format!("/bin/chmod -R {SHARED_TREE_CHMOD}")));
    assert!(seal.contains("/usr/sbin/chown -R \"${USER_UID}\" \"${SHARED_SEAL_ROOT}\""));
    let script = build_update_helper_script(
        Path::new("/tmp/log.txt"),
        Path::new("/tmp/marker.txt"),
        Path::new("/Applications/Demo.app"),
        Path::new("/tmp/extract/Demo.app"),
        "501",
        "demo",
        "1234",
        "demo-exec",
        "9.9.9",
        None,
        &seal,
    );
    let default_at = script
        .find("seal_shared_runtime() {\n  return 0\n}")
        .expect("缺默认空定义");
    let real_at = script.find("SHARED_SEAL_ROOT=").expect("缺真定义");
    let call_at = script
        .find("seal_shared_runtime || true\nmark_update_complete \"pending_manual\"")
        .expect("缺调用");
    assert!(default_at < real_at && real_at < call_at);
    // 真跑一遍(非 root:不改属主,只收自己名下文件的组 / 其他写位)
    let root = temp_test_dir("helper-seal");
    let shared = root.join("Shared Horosa");
    fs::create_dir_all(shared.join("runtime")).unwrap();
    let all = make_open_tree(&shared.join("runtime"));
    let run = format!(
        "set -euo pipefail\nUSER_UID=\"$(/usr/bin/id -u)\"\n{}\nseal_shared_runtime\n",
        build_shared_runtime_seal_command(&shared)
    );
    assert!(Command::new("/bin/bash")
        .arg("-c")
        .arg(&run)
        .status()
        .unwrap()
        .success());
    assert_owner_only_writable(&all);
    // 共享目录不存在:什么也不做
    let missing = format!(
        "set -euo pipefail\n{}\nseal_shared_runtime\n",
        build_shared_runtime_seal_command(&root.join("absent"))
    );
    assert!(Command::new("/bin/bash")
        .arg("-c")
        .arg(&missing)
        .status()
        .unwrap()
        .success());
    let _ = fs::remove_dir_all(&root);
}

#[cfg(unix)]
#[test]
fn runtime_markers_are_replaceable_and_lock_is_not_world_writable() {
    use std::os::unix::fs::PermissionsExt;
    let root = temp_test_dir("marker-replace");
    // 安装器以 root 身份写出的旧标记(这里用只读文件模拟):目录可写就能换掉
    let marker = root.join(NATIVE_PREWARM_MARKER_FILE);
    fs::write(&marker, "old").unwrap();
    fs::set_permissions(&marker, fs::Permissions::from_mode(0o444)).unwrap();
    write_file_replacing(&marker, b"new").unwrap();
    assert_eq!(fs::read_to_string(&marker).unwrap(), "new");
    assert_eq!(
        fs::metadata(&marker).unwrap().permissions().mode() & 0o022,
        0
    );
    // 目录只读(多账户机上的其他账户):写不进只返回错误,不留临时文件
    let ro = root.join("ro");
    fs::create_dir_all(&ro).unwrap();
    fs::set_permissions(&ro, fs::Permissions::from_mode(0o555)).unwrap();
    let denied = write_file_replacing(&ro.join("m.json"), b"x");
    let leftovers = fs::read_dir(&ro).unwrap().count();
    fs::set_permissions(&ro, fs::Permissions::from_mode(0o755)).unwrap();
    assert!(denied.is_err());
    assert_eq!(leftovers, 0);
    // 手术锁文件不再对所有账户可写
    let lock_root = root.join("lockroot");
    let guard = try_acquire_surgery_lock(&lock_root, Duration::from_secs(1)).unwrap();
    assert!(guard.is_some());
    let lock_mode = fs::metadata(runtime_surgery_lock_path(&lock_root))
        .unwrap()
        .permissions()
        .mode();
    assert_eq!(
        lock_mode & 0o022,
        0,
        "手术锁文件对组 / 其他账户可写: {lock_mode:o}"
    );
    drop(guard);
    let _ = fs::remove_dir_all(&root);
}

// progress-aware 就绪门契约(文本面):
// ① 三锚在位(续命账本段/总开关/总 cap);② 判死分支必须引用 last_progress_epoch
//   (反锚:防有人把续命逻辑删回硬超时);③ 指纹函数禁 lsof(全进程 FD 扫描遇
//   卡死进程可 stall 数十秒,曾拖死探测——沿用 stop 脚本同款禁令)。
#[test]
fn start_script_keeps_progress_extend_guard() {
    let script = fs::read_to_string(repo_start_script_path()).expect("read start script");
    assert!(script.contains("sh.ready_extend"), "缺续命账本段");
    assert!(script.contains("sh.ready_giveup"), "缺判死账本段");
    assert!(script.contains("HOROSA_READY_PROGRESS_EXTEND"), "缺总开关");
    assert!(
        script.contains("HOROSA_READY_TOTAL_CAP_SECS"),
        "缺总 cap(无限等防线)"
    );
    // 判死分支必须以进展时刻为条件(硬超时回潮=红)
    let deadline_at = script
        .find(r#"-ge "${deadline_epoch}""#)
        .expect("缺 deadline 判定");
    let tail = &script[deadline_at..deadline_at + 1200.min(script.len() - deadline_at)];
    assert!(
        tail.contains("last_progress_epoch"),
        "判死分支未引用 last_progress_epoch(续命被删回硬超时)"
    );
    // 指纹函数体内禁 lsof
    let fp_at = script.find("_progress_fingerprint()").expect("缺指纹函数");
    let fp_end = script[fp_at..]
        .find("\n}")
        .map(|i| fp_at + i)
        .unwrap_or(script.len());
    assert!(!script[fp_at..fp_end].contains("lsof"), "指纹函数禁用 lsof");
}

#[test]
fn stop_script_keeps_workspace_guard_and_fast_primitives() {
    // 行为护栏的文本面:① ROOT 工作区守卫(防误杀第二份 checkout 的服务)不许丢;
    // ② 端口检查必须用 netstat(lsof 全进程 FD 扫描遇卡死进程可 stall 数十秒);
    // ③ 不许回归整秒 sleep(0.1s 轮询是退出提速的根)。
    let script = fs::read_to_string(repo_stop_script_path()).expect("read stop script");
    assert!(
        script.contains(r#"grep -Fq "${ROOT}""#),
        "workspace guard missing"
    );
    assert!(
        script.contains("netstat -anv -p tcp"),
        "port scan must use netstat (kernel table), not lsof"
    );
    assert!(script.contains("sleep 0.1"), "0.1s poll loop missing");
    for line in script.lines() {
        let code = line.trim_start();
        if code.starts_with('#') {
            continue; // 注释里允许提及 lsof(说明为什么禁用)
        }
        assert!(
            !code.contains("lsof"),
            "lsof is banned in stop script (full-FD scan can stall 30-100s): {line}"
        );
        assert!(
            !code.starts_with("sleep 1"),
            "fixed whole-second sleep regressed: {line}"
        );
    }
}

#[test]
fn stop_script_kills_within_time_budget() {
    // 行为护栏(G2 升级版):
    // ① 起两个「指纹伪装成本产品服务」的假进程(exec -a 改 argv[0]),写入带端口后缀的
    //    pid 文件——脚本必须在 3s 内全停(旧实现 ≥2s 串行 sleep + lsof stall 可到 30s+)。
    // ② 反向断言:一个指纹不符的无辜进程(裸 sleep)即使 pid 被写进 pid 文件,也绝不能
    //    被误杀(pid 复用/跨实例覆写场景),脚本只清文件。tempdir 隔离,不碰真实工作区。
    let work = std::env::temp_dir().join(format!("horosa-stop-test-{}", std::process::id()));
    let _ = fs::remove_dir_all(&work);
    fs::create_dir_all(&work).expect("mk tempdir");
    fs::copy(repo_stop_script_path(), work.join("stop_horosa_local.sh")).expect("copy script");
    let spawn_marked_sleeper = |marker: &str| {
        Command::new("/bin/bash")
            .arg("-c")
            .arg(format!("exec -a {marker} /bin/sleep 100"))
            .spawn()
            .expect("spawn marked sleeper")
    };
    let mut py = spawn_marked_sleeper("webchartsrv.py");
    let mut java = spawn_marked_sleeper("astrostudyboot.jar");
    let mut innocent = Command::new("/bin/sleep")
        .arg("100")
        .spawn()
        .expect("spawn innocent sleeper");
    // 脚本无 env 时用默认端口 8899/9999/8000 → pid 文件名按同一约定生成。
    fs::write(work.join(".horosa_py.8899.pid"), py.id().to_string()).expect("write py pid");
    fs::write(work.join(".horosa_java.9999.pid"), java.id().to_string()).expect("write java pid");
    fs::write(work.join(".horosa_web.8000.pid"), innocent.id().to_string())
        .expect("write innocent pid");
    let started = Instant::now();
    let status = Command::new("/bin/bash")
        .arg(work.join("stop_horosa_local.sh"))
        .current_dir(&work)
        .stdout(Stdio::null())
        .stderr(Stdio::null())
        .status()
        .expect("run stop script");
    let elapsed = started.elapsed();
    assert!(status.success(), "stop script must exit 0");
    assert!(
        elapsed < Duration::from_secs(3),
        "stop script too slow: {elapsed:?}"
    );
    // 两个假服务必须已死。它们是本测试进程的子进程,被杀后先成僵尸(kill -0 对僵尸
    // 仍成功),必须用 try_wait 收尸判定;轮询 ≤2s 防 wait 永久阻塞。
    fn assert_reaped(label: &str, child: &mut std::process::Child) {
        for _ in 0..40 {
            if child.try_wait().expect("try_wait").is_some() {
                return;
            }
            thread::sleep(Duration::from_millis(50));
        }
        panic!("{label} sleeper must be stopped by script");
    }
    assert_reaped("py", &mut py);
    assert_reaped("java", &mut java);
    // 无辜进程必须还活着(指纹校验拒杀),pid 文件应被清理。
    assert!(
        innocent.try_wait().expect("try_wait innocent").is_none(),
        "指纹不符的进程绝不能被停服脚本误杀(pid 复用防线失效)"
    );
    assert!(
        !work.join(".horosa_web.8000.pid").exists(),
        "指纹不符时应只清理 pid 文件"
    );
    let _ = innocent.kill();
    let _ = innocent.wait();
    let _ = fs::remove_dir_all(&work);
}

// ── 增量部件应用协议(apply_component_updates):tree/preserve/files 三机制 + 失败原子性 ──

fn write_file(path: &Path, content: &str) {
    fs::create_dir_all(path.parent().unwrap()).unwrap();
    fs::write(path, content).unwrap();
}

/// 打一个部件 tar.gz:条目带 runtime-payload/ 前缀(与打包脚本产物同构)。
fn build_component_tar(dest: &Path, entries: &[(&str, &str)]) {
    let file = fs::File::create(dest).unwrap();
    let enc = GzEncoder::new(file, Compression::fast());
    let mut builder = Builder::new(enc);
    for (rel, content) in entries {
        let mut header = tar::Header::new_gnu();
        header.set_size(content.len() as u64);
        header.set_mode(0o644);
        header.set_cksum();
        builder
            .append_data(
                &mut header,
                format!("runtime-payload/{}", rel),
                content.as_bytes(),
            )
            .unwrap();
    }
    builder.into_inner().unwrap().finish().unwrap();
}

fn lock_json(version: &str, tree_files_note: &str, files_list: &[&str]) -> serde_json::Value {
    serde_json::json!({
        "schemaVersion": 1,
        "runtimeVersion": version,
        "appName": APP_NAME,
        "builtAt": tree_files_note,
        "components": [
            {"name": "t", "type": "tree", "paths": ["t"], "preserve": ["t/keep"],
             "file": "comp-t.tar.gz", "sha256": "x", "size": 1},
            {"name": "f", "type": "files", "files": files_list,
             "file": "comp-f.tar.gz", "sha256": "y", "size": 1},
        ],
    })
}

fn setup_v1_runtime(root: &Path) {
    let current = root.join("current");
    write_file(&current.join("t/old.txt"), "v1-old");
    write_file(&current.join("t/keep/k.txt"), "user-data");
    write_file(&current.join("f/a.txt"), "v1-a");
    write_file(&current.join("f/b.txt"), "v1-b");
    let lock = lock_json("1.0.0", "2026-01-01", &["f/a.txt", "f/b.txt"]);
    write_file(
        &current.join("components-lock.json"),
        &serde_json::to_string_pretty(&lock).unwrap(),
    );
    write_file(
        &current.join("runtime-manifest.json"),
        r#"{"version":"1.0.0","built_at":"2026-01-01","appName":"x"}"#,
    );
}

fn staged_v2(work: &Path) -> StagedComponents {
    let t_tar = work.join("comp-t.tar.gz");
    build_component_tar(&t_tar, &[("t/new.txt", "v2-new")]); // 不含 keep 子树
    let f_tar = work.join("comp-f.tar.gz");
    build_component_tar(&f_tar, &[("f/a.txt", "v2-a"), ("f/c.txt", "v2-c")]); // b 消失
    let new_lock = lock_json("2.0.0", "2026-02-02", &["f/a.txt", "f/c.txt"]);
    let mk = |name: &str, file: &str| ManifestComponent {
        name: name.into(),
        kind: if name == "t" {
            "tree".into()
        } else {
            "files".into()
        },
        sha256: "irrelevant-for-apply".into(),
        size: Some(1),
        file: file.into(),
        url: String::new(),
    };
    StagedComponents {
        archives: vec![
            (mk("t", "comp-t.tar.gz"), t_tar),
            (mk("f", "comp-f.tar.gz"), f_tar),
        ],
        new_lock_text: serde_json::to_string_pretty(&new_lock).unwrap(),
        new_lock_json: new_lock,
    }
}

#[test]
fn component_apply_tree_preserve_and_files_semantics() {
    let work = std::env::temp_dir().join(format!("horosa-comp-apply-{}", std::process::id()));
    let _ = fs::remove_dir_all(&work);
    let root = work.join("root");
    setup_v1_runtime(&root);
    let staged = staged_v2(&work);

    apply_component_updates(&root, &staged).expect("incremental apply should succeed");

    let cur = root.join("current");
    // tree:整树替换 + preserve 子树幸存
    assert!(!cur.join("t/old.txt").exists(), "旧树文件应被整树替换清除");
    assert_eq!(fs::read_to_string(cur.join("t/new.txt")).unwrap(), "v2-new");
    assert_eq!(
        fs::read_to_string(cur.join("t/keep/k.txt")).unwrap(),
        "user-data",
        "preserve 子树必须在整树替换后放回"
    );
    // files:更新/新增/删除三态
    assert_eq!(fs::read_to_string(cur.join("f/a.txt")).unwrap(), "v2-a");
    assert_eq!(fs::read_to_string(cur.join("f/c.txt")).unwrap(), "v2-c");
    assert!(!cur.join("f/b.txt").exists(), "消失文件(旧−新)必须删除");
    // 清单/身份戳重写 + 暂存清理
    let lock: serde_json::Value =
        serde_json::from_str(&fs::read_to_string(cur.join("components-lock.json")).unwrap())
            .unwrap();
    assert_eq!(lock["runtimeVersion"], "2.0.0");
    let manifest: serde_json::Value =
        serde_json::from_str(&fs::read_to_string(cur.join("runtime-manifest.json")).unwrap())
            .unwrap();
    assert_eq!(manifest["version"], "2.0.0");
    assert_eq!(manifest["appName"], APP_NAME);
    // WS-1d 看门狗语义:previous 槽保留到首次成功 ready 才回收(供连续启动失败自动回滚);
    // 其内容必须是更新前的旧版(1.x lock)。
    let prev_lock: serde_json::Value = serde_json::from_str(
        &fs::read_to_string(root.join("previous/components-lock.json")).unwrap(),
    )
    .unwrap();
    assert_ne!(
        prev_lock["runtimeVersion"], "2.0.0",
        "previous 槽必须是旧版"
    );
    assert!(!root.join("_comp_stage").exists());
    let _ = fs::remove_dir_all(&work);
}

#[test]
fn watchdog_health_state_machine_and_rollback() {
    let work = temp_test_dir("watchdog");
    // 状态机:连续 note_start 递增,confirm 归零
    let health = work.join("launch-health.json");
    assert_eq!(launch_health_note_start(&health), 1);
    assert_eq!(launch_health_note_start(&health), 2);
    assert_eq!(launch_health_note_start(&health), 3);
    launch_health_confirm(&health);
    assert_eq!(launch_health_read(&health).pending_starts, 0);
    assert_eq!(launch_health_note_start(&health), 1);

    // 回滚:previous 完整 → 换回 current,故障槽清除
    let root = work.join("runtime");
    fs::create_dir_all(root.join("current")).unwrap();
    fs::write(
        root.join("current/runtime-manifest.json"),
        r#"{"version":"9.9.9"}"#,
    )
    .unwrap();
    fs::write(root.join("current/marker.txt"), "broken-new").unwrap();
    fs::create_dir_all(root.join("previous")).unwrap();
    fs::write(
        root.join("previous/runtime-manifest.json"),
        r#"{"version":"9.9.8"}"#,
    )
    .unwrap();
    fs::write(root.join("previous/marker.txt"), "good-old").unwrap();
    assert!(rollback_runtime_to_previous(&root).unwrap());
    assert_eq!(
        fs::read_to_string(root.join("current/marker.txt")).unwrap(),
        "good-old"
    );
    assert!(!root.join("previous").exists());
    assert!(!root.join("_broken_rollback").exists());

    // previous 缺失/不完整 → Ok(false),current 纹丝不动
    assert!(!rollback_runtime_to_previous(&root).unwrap());
    fs::create_dir_all(root.join("previous")).unwrap(); // 无 runtime-manifest.json = 不完整
    assert!(!rollback_runtime_to_previous(&root).unwrap());
    assert_eq!(
        fs::read_to_string(root.join("current/marker.txt")).unwrap(),
        "good-old"
    );
    let _ = fs::remove_dir_all(&work);
}

#[test]
fn component_apply_failure_leaves_current_untouched() {
    let work = std::env::temp_dir().join(format!("horosa-comp-fail-{}", std::process::id()));
    let _ = fs::remove_dir_all(&work);
    let root = work.join("root");
    setup_v1_runtime(&root);
    let staged = staged_v2(&work);
    fs::write(&staged.archives[1].1, b"not a tar.gz").unwrap(); // 损坏 files 部件

    let err = apply_component_updates(&root, &staged);
    assert!(err.is_err(), "坏包必须失败");
    let cur = root.join("current");
    assert_eq!(fs::read_to_string(cur.join("t/old.txt")).unwrap(), "v1-old");
    assert_eq!(fs::read_to_string(cur.join("f/b.txt")).unwrap(), "v1-b");
    let lock: serde_json::Value =
        serde_json::from_str(&fs::read_to_string(cur.join("components-lock.json")).unwrap())
            .unwrap();
    assert_eq!(
        lock["runtimeVersion"], "1.0.0",
        "失败后 current 必须纹丝不动"
    );
    assert!(!root.join("_comp_stage").exists(), "失败必须清理暂存");
    let _ = fs::remove_dir_all(&work);
}

#[test]
fn component_diff_gates_and_change_detection() {
    let work = std::env::temp_dir().join(format!("horosa-comp-diff-{}", std::process::id()));
    let _ = fs::remove_dir_all(&work);
    let root = work.join("root");
    setup_v1_runtime(&root);
    let mk = |name: &str, sha: &str| ManifestComponent {
        name: name.into(),
        kind: "tree".into(),
        sha256: sha.into(),
        size: Some(1),
        file: format!("comp-{}.tar.gz", name),
        url: String::new(),
    };
    let plan = |comps: Option<Vec<ManifestComponent>>| UpdatePlan {
        latest_version: Version::parse("9.9.9").unwrap(),
        notes: String::new(),
        repo_url: String::new(),
        release_url: String::new(),
        app_url: String::new(),
        app_sha256: None,
        runtime_url: None,
        runtime_version: Some("9.9.9".into()),
        runtime_sha256: None,
        components: comps,
        components_lock_url: Some("u".into()),
        components_lock_sha256: Some("s".into()),
        app_size_bytes: None,
        runtime_size_bytes: None,
        allow_downgrade: false,
        source: UpdateSource::Manifest,
        notify_only: false,
        full_pkg_reason: None,
    };
    let roots = vec![root.clone()];
    // v1 lock 里 t/f 的 sha 是 "x"/"y":同 sha 不下载,异 sha 进下载集
    let diff = plan_component_diff(&plan(Some(vec![mk("t", "x"), mk("f", "changed")])), &roots)
        .expect("应可增量");
    assert_eq!(diff.len(), 1);
    assert_eq!(diff[0].name, "f");
    // 新增部件(本地清单没有)按变化处理
    let diff2 = plan_component_diff(
        &plan(Some(vec![mk("t", "x"), mk("brand-new", "z")])),
        &roots,
    )
    .expect("应可增量");
    assert_eq!(diff2.len(), 1);
    assert_eq!(diff2[0].name, "brand-new");
    // 门:无 components → None;多 root → None;kill-switch → None
    assert!(plan_component_diff(&plan(None), &roots).is_none());
    assert!(plan_component_diff(
        &plan(Some(vec![mk("t", "x")])),
        &[root.clone(), work.clone()]
    )
    .is_none());
    std::env::set_var("HOROSA_UPDATE_FULL_ONLY", "1");
    assert!(plan_component_diff(&plan(Some(vec![mk("t", "q")])), &roots).is_none());
    std::env::remove_var("HOROSA_UPDATE_FULL_ONLY");
    let _ = fs::remove_dir_all(&work);
}

// ---- WS-1b 断点续传下载核:tiny_http 本地矩阵 ----
// 全部走真实 HTTP(127.0.0.1 随机端口),allow_resume 走参数注入(不碰 env,测试可并行)。

mod download_resume {
    use super::super::*;
    use super::temp_test_dir;
    use flate2::write::GzEncoder;
    use flate2::Compression;
    use std::io::{Read, Write};
    use std::net::{Shutdown, TcpListener, TcpStream};
    use std::sync::{Arc, Mutex};
    use std::thread;
    use tar::Builder;

    // 用 raw TcpListener 手写 HTTP 响应:断线时机/206/Content-Range/ETag 逐字节可控
    // (tiny_http 对「声明长度>实发字节」会自行降级成 EOF 定界,模拟不出真中断)。

    fn test_payload(len: usize) -> Vec<u8> {
        (0..len).map(|i| ((i * 31 + 7) % 251) as u8).collect()
    }

    fn read_request(stream: &mut TcpStream) -> String {
        let mut buf = [0u8; 8192];
        let mut req: Vec<u8> = Vec::new();
        loop {
            let n = stream.read(&mut buf).unwrap_or(0);
            if n == 0 {
                break;
            }
            req.extend_from_slice(&buf[..n]);
            if req.windows(4).any(|w| w == b"\r\n\r\n") {
                break;
            }
        }
        String::from_utf8_lossy(&req).to_string()
    }

    fn range_of(req: &str) -> Option<String> {
        req.lines().find_map(|line| {
            line.to_ascii_lowercase()
                .strip_prefix("range:")
                .map(|v| v.trim().to_string())
        })
    }

    fn parse_range_offset(range: &str) -> usize {
        range
            .trim_start_matches("bytes=")
            .trim_end_matches('-')
            .parse()
            .unwrap()
    }

    /// 200 响应:声明完整长度但只发 body 前缀,随即硬断连接(真·下载中断)。
    fn write_200_interrupted(stream: &mut TcpStream, full_len: usize, prefix: &[u8], etag: &str) {
        let head = format!(
            "HTTP/1.1 200 OK\r\nContent-Length: {}\r\nETag: {}\r\nConnection: close\r\n\r\n",
            full_len, etag
        );
        let _ = stream.write_all(head.as_bytes());
        let _ = stream.write_all(prefix);
        let _ = stream.flush();
        let _ = stream.shutdown(Shutdown::Both);
    }

    fn write_206(stream: &mut TcpStream, full: &[u8], offset: usize, etag: &str) {
        let body = &full[offset..];
        let head = format!(
            "HTTP/1.1 206 Partial Content\r\nContent-Length: {}\r\nContent-Range: bytes {}-{}/{}\r\nETag: {}\r\nConnection: close\r\n\r\n",
            body.len(),
            offset,
            full.len() - 1,
            full.len(),
            etag
        );
        let _ = stream.write_all(head.as_bytes());
        let _ = stream.write_all(body);
        let _ = stream.flush();
        let _ = stream.shutdown(Shutdown::Both);
    }

    fn write_200_full(stream: &mut TcpStream, full: &[u8], etag: &str) {
        let head = format!(
            "HTTP/1.1 200 OK\r\nContent-Length: {}\r\nETag: {}\r\nConnection: close\r\n\r\n",
            full.len(),
            etag
        );
        let _ = stream.write_all(head.as_bytes());
        let _ = stream.write_all(full);
        let _ = stream.flush();
        let _ = stream.shutdown(Shutdown::Both);
    }

    fn spawn_server() -> (TcpListener, String) {
        let listener = TcpListener::bind("127.0.0.1:0").unwrap();
        let port = listener.local_addr().unwrap().port();
        let url = format!("http://127.0.0.1:{}/asset.bin", port);
        (listener, url)
    }

    #[test]
    fn resume_completes_via_range_206() {
        let full = test_payload(300_000);
        let (server, url) = spawn_server();
        let ranges: Arc<Mutex<Vec<Option<String>>>> = Arc::new(Mutex::new(Vec::new()));
        let (ranges_srv, full_srv) = (ranges.clone(), full.clone());
        let handle = thread::spawn(move || {
            let mut s = server.accept().unwrap().0;
            let req = read_request(&mut s);
            ranges_srv.lock().unwrap().push(range_of(&req));
            write_200_interrupted(&mut s, full_srv.len(), &full_srv[..131_072], "\"v1\"");
            let mut s = server.accept().unwrap().0;
            let req = read_request(&mut s);
            let range = range_of(&req);
            let offset = parse_range_offset(range.as_deref().unwrap());
            ranges_srv.lock().unwrap().push(range);
            write_206(&mut s, &full_srv, offset, "\"v1\"");
        });
        let dir = temp_test_dir("dl-resume-206");
        let dest = dir.join("asset.bin");
        let (part, meta) = download_part_paths(&dest);

        let first = download_resumable_once(&url, &dest, true, |_, _| {}, |_| {});
        assert!(first.is_err(), "被中断的下载必须失败");
        assert!(part.exists() && meta.exists(), "part/meta 必须保留供续传");
        assert!(!dest.exists(), "finalize 前 dest 绝不出现");

        let mut resumed_from = 0u64;
        download_resumable_once(&url, &dest, true, |off, _| resumed_from = off, |_| {})
            .expect("续传应成功");
        assert!(resumed_from > 0, "第二次必须走续传而非全新");
        assert_eq!(fs::read(&dest).unwrap(), full, "拼合内容必须逐字节一致");
        assert!(
            !part.exists() && !meta.exists(),
            "完成后 part/meta 必须清除"
        );
        let seen = ranges.lock().unwrap();
        assert!(seen[0].is_none(), "首个请求必须无 Range");
        assert!(seen[1].as_deref().unwrap_or("").starts_with("bytes="));
        drop(seen);
        handle.join().unwrap();
        let _ = fs::remove_dir_all(&dir);
    }

    #[test]
    fn server_ignoring_range_falls_back_to_full_200() {
        let full = test_payload(220_000);
        let (server, url) = spawn_server();
        let ranges: Arc<Mutex<Vec<Option<String>>>> = Arc::new(Mutex::new(Vec::new()));
        let (ranges_srv, full_srv) = (ranges.clone(), full.clone());
        let handle = thread::spawn(move || {
            let mut s = server.accept().unwrap().0;
            let req = read_request(&mut s);
            ranges_srv.lock().unwrap().push(range_of(&req));
            write_200_interrupted(&mut s, full_srv.len(), &full_srv[..100_000], "\"v1\"");
            // 无视 Range 回 200 全量:客户端应就地当全新流消费(截断重写)
            let mut s = server.accept().unwrap().0;
            let req = read_request(&mut s);
            ranges_srv.lock().unwrap().push(range_of(&req));
            write_200_full(&mut s, &full_srv, "\"v1\"");
        });
        let dir = temp_test_dir("dl-resume-200");
        let dest = dir.join("asset.bin");

        assert!(download_resumable_once(&url, &dest, true, |_, _| {}, |_| {}).is_err());
        let mut resumed_from = 42u64;
        download_resumable_once(&url, &dest, true, |off, _| resumed_from = off, |_| {})
            .expect("降级全新下载应成功");
        assert_eq!(resumed_from, 0, "200 降级后按全新下载起算");
        assert_eq!(fs::read(&dest).unwrap(), full);
        let seen = ranges.lock().unwrap();
        assert!(
            seen[1].as_deref().unwrap_or("").starts_with("bytes="),
            "第二次应先尝试 Range"
        );
        drop(seen);
        handle.join().unwrap();
        let _ = fs::remove_dir_all(&dir);
    }

    #[test]
    fn etag_change_discards_part_and_redownloads() {
        let old = test_payload(180_000);
        let fresh: Vec<u8> = test_payload(180_000).iter().map(|b| b ^ 0x5a).collect();
        let (server, url) = spawn_server();
        let ranges: Arc<Mutex<Vec<Option<String>>>> = Arc::new(Mutex::new(Vec::new()));
        let (ranges_srv, old_srv, fresh_srv) = (ranges.clone(), old.clone(), fresh.clone());
        let handle = thread::spawn(move || {
            let mut s = server.accept().unwrap().0;
            let req = read_request(&mut s);
            ranges_srv.lock().unwrap().push(range_of(&req));
            write_200_interrupted(&mut s, old_srv.len(), &old_srv[..90_000], "\"v1\"");
            // 内容已换版:206 但 etag 变 → 客户端必须弃续传
            let mut s = server.accept().unwrap().0;
            let req = read_request(&mut s);
            let range = range_of(&req);
            let offset = parse_range_offset(range.as_deref().unwrap());
            ranges_srv.lock().unwrap().push(range);
            write_206(&mut s, &fresh_srv, offset, "\"v2\"");
            // 客户端随即发全新请求
            let mut s = server.accept().unwrap().0;
            let req = read_request(&mut s);
            ranges_srv.lock().unwrap().push(range_of(&req));
            write_200_full(&mut s, &fresh_srv, "\"v2\"");
        });
        let dir = temp_test_dir("dl-resume-etag");
        let dest = dir.join("asset.bin");

        assert!(download_resumable_once(&url, &dest, true, |_, _| {}, |_| {}).is_err());
        let mut resumed_from = 42u64;
        download_resumable_once(&url, &dest, true, |off, _| resumed_from = off, |_| {})
            .expect("etag 变化后全新重下应成功");
        assert_eq!(resumed_from, 0, "etag 冲突必须放弃续传");
        assert_eq!(fs::read(&dest).unwrap(), fresh, "必须拿到新版内容,绝不混拼");
        let seen = ranges.lock().unwrap();
        assert_eq!(seen.len(), 3);
        assert!(seen[2].is_none(), "第三个请求必须是全新(无 Range)");
        drop(seen);
        handle.join().unwrap();
        let _ = fs::remove_dir_all(&dir);
    }

    #[test]
    fn no_resume_flag_forces_fresh_download() {
        let full = test_payload(160_000);
        let (server, url) = spawn_server();
        let ranges: Arc<Mutex<Vec<Option<String>>>> = Arc::new(Mutex::new(Vec::new()));
        let (ranges_srv, full_srv) = (ranges.clone(), full.clone());
        let handle = thread::spawn(move || {
            let mut s = server.accept().unwrap().0;
            let req = read_request(&mut s);
            ranges_srv.lock().unwrap().push(range_of(&req));
            write_200_interrupted(&mut s, full_srv.len(), &full_srv[..80_000], "\"v1\"");
            let mut s = server.accept().unwrap().0;
            let req = read_request(&mut s);
            ranges_srv.lock().unwrap().push(range_of(&req));
            write_200_full(&mut s, &full_srv, "\"v1\"");
        });
        let dir = temp_test_dir("dl-resume-off");
        let dest = dir.join("asset.bin");
        let (part, meta) = download_part_paths(&dest);

        assert!(download_resumable_once(&url, &dest, true, |_, _| {}, |_| {}).is_err());
        assert!(part.exists());
        download_resumable_once(&url, &dest, false, |_, _| {}, |_| {})
            .expect("kill-switch 全新下载应成功");
        assert_eq!(fs::read(&dest).unwrap(), full);
        let seen = ranges.lock().unwrap();
        assert!(
            seen[1].is_none(),
            "HOROSA_DOWNLOAD_NO_RESUME 语义:第二次不得带 Range"
        );
        assert!(!part.exists() && !meta.exists());
        drop(seen);
        handle.join().unwrap();
        let _ = fs::remove_dir_all(&dir);
    }

    #[test]
    fn native_extract_parity_with_external_tar() {
        use super::super::{extract_tar_gz_native_with, tar_extract_external, SMALL_FILE_LIMIT};
        use std::os::unix::fs::MetadataExt;
        use std::os::unix::fs::PermissionsExt;

        // fixture:普通/中文名/exec 位/symlink/硬链/深嵌套/超过小文件阈值的大文件(全零,gz 后极小)
        let dir = temp_test_dir("extract-parity");
        let src = dir.join("src/runtime-payload");
        fs::create_dir_all(src.join("nested/深层目录")).unwrap();
        fs::write(src.join("plain.txt"), b"hello horosa").unwrap();
        fs::write(
            src.join("nested/深层目录/星阙测试.dat"),
            test_payload(70_000),
        )
        .unwrap();
        fs::write(src.join("tool.sh"), b"#!/bin/sh\necho ok\n").unwrap();
        fs::set_permissions(src.join("tool.sh"), fs::Permissions::from_mode(0o755)).unwrap();
        let big = vec![0u8; (SMALL_FILE_LIMIT + 1024) as usize];
        fs::write(src.join("big.bin"), &big).unwrap();
        std::os::unix::fs::symlink("plain.txt", src.join("link-to-plain")).unwrap();

        // 打包(gnu tar builder;follow_symlinks(false) 保 symlink 条目本体;
        // 硬链条目手工构造——append_dir_all 不追踪 inode,会把硬链归成两个独立 Regular)
        let archive = dir.join("fixture.tar.gz");
        {
            let tar_gz = File::create(&archive).unwrap();
            let encoder = GzEncoder::new(tar_gz, Compression::default());
            let mut builder = Builder::new(encoder);
            builder.follow_symlinks(false);
            builder.append_dir_all("runtime-payload", &src).unwrap();
            let mut link_header = tar::Header::new_gnu();
            link_header.set_entry_type(tar::EntryType::Link);
            link_header.set_size(0);
            link_header.set_mode(0o644);
            builder
                .append_link(
                    &mut link_header,
                    "runtime-payload/hard-to-plain",
                    "runtime-payload/plain.txt",
                )
                .unwrap();
            builder.finish().unwrap();
        }

        // 三方解压:native 顺序(=1)/native 并发(=4)/外部 /usr/bin/tar
        let out_seq = dir.join("out-seq");
        let out_par = dir.join("out-par");
        let out_ext = dir.join("out-ext");
        fs::create_dir_all(&out_ext).unwrap();
        extract_tar_gz_native_with(&archive, &out_seq, 1, 1, None).expect("native 顺序");
        let reported = std::cell::Cell::new((0u64, 0u64, 0u64));
        let cb = |read: u64, total: u64, files: u64| {
            reported.set((read, total, files));
        };
        extract_tar_gz_native_with(&archive, &out_par, 1, 4, Some(&cb)).expect("native 并发");
        let (rep_read, rep_total, rep_files) = reported.get();
        assert_eq!(rep_read, rep_total, "终报进度必须收敛到 100%");
        assert!(rep_files >= 6, "文件计数必须覆盖全部条目");
        tar_extract_external(&archive, &out_ext, true).expect("外部 tar");

        // 逐条目比对:路径集合/字节内容/mode/symlink 目标/硬链 inode 同一性/文件 mtime
        fn walk(root: &Path) -> Vec<PathBuf> {
            let mut out = Vec::new();
            let mut stack = vec![root.to_path_buf()];
            while let Some(cur) = stack.pop() {
                for e in fs::read_dir(&cur).unwrap() {
                    let p = e.unwrap().path();
                    out.push(p.strip_prefix(root).unwrap().to_path_buf());
                    if p.is_dir() && !p.symlink_metadata().unwrap().file_type().is_symlink() {
                        stack.push(p);
                    }
                }
            }
            out.sort();
            out
        }
        let listing = walk(&out_seq);
        assert_eq!(listing, walk(&out_par), "顺序/并发 路径集合必须一致");
        assert_eq!(listing, walk(&out_ext), "native/外部tar 路径集合必须一致");
        assert!(!listing.is_empty());
        for rel in &listing {
            let a = out_seq.join(rel);
            let b = out_par.join(rel);
            let c = out_ext.join(rel);
            let meta_a = a.symlink_metadata().unwrap();
            if meta_a.file_type().is_symlink() {
                let ta = fs::read_link(&a).unwrap();
                assert_eq!(ta, fs::read_link(&b).unwrap(), "symlink 目标 {rel:?}");
                assert_eq!(ta, fs::read_link(&c).unwrap(), "symlink 目标 {rel:?}");
                continue;
            }
            if meta_a.is_dir() {
                continue;
            }
            let bytes_a = fs::read(&a).unwrap();
            assert_eq!(bytes_a, fs::read(&b).unwrap(), "内容 {rel:?}");
            assert_eq!(bytes_a, fs::read(&c).unwrap(), "内容 {rel:?}");
            let mode_a = meta_a.permissions().mode() & 0o7777;
            let mode_b = b.symlink_metadata().unwrap().permissions().mode() & 0o7777;
            let mode_c = c.symlink_metadata().unwrap().permissions().mode() & 0o7777;
            assert_eq!(mode_a, mode_b, "mode {rel:?}");
            assert_eq!(mode_a, mode_c, "mode {rel:?}");
            let mt = |p: &Path| {
                p.symlink_metadata()
                    .unwrap()
                    .modified()
                    .unwrap()
                    .duration_since(UNIX_EPOCH)
                    .unwrap()
                    .as_secs()
            };
            assert_eq!(mt(&a), mt(&b), "mtime {rel:?}");
            assert_eq!(mt(&a), mt(&c), "mtime {rel:?}");
        }
        // 硬链同一性:hard-to-plain 与 plain.txt 同 inode(三方各自内部核对)
        for root in [&out_seq, &out_par, &out_ext] {
            let ino_plain = root.join("plain.txt").metadata().unwrap().ino();
            let ino_hard = root.join("hard-to-plain").metadata().unwrap().ino();
            assert_eq!(ino_plain, ino_hard, "硬链 inode 同一性 {root:?}");
        }
        // exec 位专项:tool.sh 三方都必须 0o755
        for root in [&out_seq, &out_par, &out_ext] {
            let mode = root
                .join("tool.sh")
                .metadata()
                .unwrap()
                .permissions()
                .mode()
                & 0o777;
            assert_eq!(mode, 0o755, "exec 位 {root:?}");
        }
        let _ = fs::remove_dir_all(&dir);
    }

    #[test]
    fn native_extract_rejects_path_escape() {
        use super::super::extract_tar_gz_native_with;
        // 恶意归档:条目路径带 ../ → 必须整体报错,绝不落盘到 dest 之外
        let dir = temp_test_dir("extract-escape");
        let archive = dir.join("evil.tar.gz");
        {
            let tar_gz = File::create(&archive).unwrap();
            let encoder = GzEncoder::new(tar_gz, Compression::default());
            let mut builder = Builder::new(encoder);
            let data = b"evil";
            let mut header = tar::Header::new_gnu();
            // Builder::append_data 自己拒 `..`(打包端防护)——直接写 header 名字段造恶意条目
            let name = b"root/../../escape.txt";
            header.as_old_mut().name[..name.len()].copy_from_slice(name);
            header.set_size(data.len() as u64);
            header.set_mode(0o644);
            header.set_cksum();
            builder.append(&header, &data[..]).unwrap();
            builder.finish().unwrap();
        }
        let out = dir.join("out");
        let err = extract_tar_gz_native_with(&archive, &out, 0, 1, None);
        assert!(err.is_err(), "路径逃逸归档必须报错");
        assert!(!dir.join("escape.txt").exists(), "逃逸文件绝不落盘");
        assert!(
            !dir.parent().unwrap().join("escape.txt").exists(),
            "逃逸文件绝不落盘到上层"
        );
        let _ = fs::remove_dir_all(&dir);
    }

    /// 直接写 header 造条目(Builder 的 append_* 自己会拒 `..` / 绝对链接目标 —— 恶意归档要绕过打包端防护)。
    /// 条目:(名字, 'f' 文件 / 'd' 目录 / 'l' 符号链接, 链接目标, 内容)。
    fn build_raw_tar_gz(path: &Path, entries: &[(&str, char, &str, &[u8])]) {
        let tar_gz = File::create(path).unwrap();
        let encoder = GzEncoder::new(tar_gz, Compression::default());
        let mut builder = Builder::new(encoder);
        for (name, kind, link, data) in entries {
            let mut header = tar::Header::new_gnu();
            let nb = name.as_bytes();
            header.as_old_mut().name[..nb.len()].copy_from_slice(nb);
            match kind {
                'd' => {
                    header.set_entry_type(tar::EntryType::Directory);
                    header.set_mode(0o755);
                    header.set_size(0);
                }
                'l' if link.len() > 100 => {
                    // 放不进 header 的长目标(绝对路径)走 GNU 长链接名条目
                    header.set_entry_type(tar::EntryType::Symlink);
                    header.set_mode(0o777);
                    header.set_size(0);
                    builder.append_link(&mut header, name, link).unwrap();
                    continue;
                }
                'l' => {
                    header.set_entry_type(tar::EntryType::Symlink);
                    let lb = link.as_bytes();
                    header.as_old_mut().linkname[..lb.len()].copy_from_slice(lb);
                    header.set_mode(0o777);
                    header.set_size(0);
                }
                _ => {
                    header.set_entry_type(tar::EntryType::Regular);
                    header.set_mode(0o644);
                    header.set_size(data.len() as u64);
                }
            }
            header.set_cksum();
            builder.append(&header, &data[..]).unwrap();
        }
        builder.finish().unwrap();
    }

    #[test]
    fn native_extract_rejects_write_through_symlink_to_outside_dir() {
        use super::super::{extract_tar_gz_native_with, is_archive_unsafe};
        // 先放 `x -> 树外目录`(绝对目标),再放 `x/evil.plist`:必须整包报错,树外目录里不许出现文件
        let dir = temp_test_dir("extract-symlink-escape");
        let outside = dir.join("outside");
        fs::create_dir_all(&outside).unwrap();
        let archive = dir.join("evil.tar.gz");
        let outside_s = outside.to_string_lossy().to_string();
        build_raw_tar_gz(
            &archive,
            &[
                ("x", 'l', outside_s.as_str(), b""),
                ("x/evil.plist", 'f', "", b"evil"),
            ],
        );
        for conc in [1usize, 4] {
            let out = dir.join(format!("out{conc}"));
            let err = extract_tar_gz_native_with(&archive, &out, 0, conc, None).unwrap_err();
            assert!(is_archive_unsafe(&err), "应判为不安全归档: {err:#}");
            assert!(!outside.join("evil.plist").exists(), "绝不经链接写到树外");
            assert!(!out.join("x").exists(), "指向树外的链接不建");
        }
        let _ = fs::remove_dir_all(&dir);
    }

    #[test]
    fn native_extract_rejects_symlink_targets_that_escape_dest() {
        use super::super::{extract_tar_gz_native_with, is_archive_unsafe};
        let dir = temp_test_dir("extract-symlink-target");
        // 相对目标字面就出树
        let a1 = dir.join("a1.tar.gz");
        build_raw_tar_gz(&a1, &[("lnk", 'l', "../../escape_dir", b"")]);
        let err = extract_tar_gz_native_with(&a1, &dir.join("o1"), 0, 1, None).unwrap_err();
        assert!(is_archive_unsafe(&err), "{err:#}");
        // 字面在树内、真实出树:`b -> .` 真实落点是解压根本身,`b/../x` 就出了树
        let a2 = dir.join("a2.tar.gz");
        build_raw_tar_gz(
            &a2,
            &[("b", 'l', ".", b""), ("a", 'l', "b/../escaped", b"")],
        );
        let err = extract_tar_gz_native_with(&a2, &dir.join("o2"), 0, 1, None).unwrap_err();
        assert!(is_archive_unsafe(&err), "{err:#}");
        // 先建的链接被后建的链接改了真实落点(建 a 时 b 还不存在):收尾复核必须抓到
        let a3 = dir.join("a3.tar.gz");
        build_raw_tar_gz(
            &a3,
            &[("a", 'l', "b/../escaped", b""), ("b", 'l', ".", b"")],
        );
        let err = extract_tar_gz_native_with(&a3, &dir.join("o3"), 0, 1, None).unwrap_err();
        assert!(is_archive_unsafe(&err), "{err:#}");
        // 自指环
        let a4 = dir.join("a4.tar.gz");
        build_raw_tar_gz(&a4, &[("loop", 'l', "loop", b"")]);
        let err = extract_tar_gz_native_with(&a4, &dir.join("o4"), 0, 1, None).unwrap_err();
        assert!(is_archive_unsafe(&err), "{err:#}");
        let _ = fs::remove_dir_all(&dir);
    }

    #[test]
    fn native_extract_refuses_writes_through_in_tree_symlink_and_keeps_legit_links() {
        use super::super::{
            extract_tar_gz_native_with, is_archive_unsafe, tar_extract_strip1_with,
        };
        let dir = temp_test_dir("extract-symlink-legit");
        // 经树内链接写盘同样拒(打包端从不这样产出条目)
        let bad = dir.join("bad.tar.gz");
        build_raw_tar_gz(
            &bad,
            &[
                ("sub/", 'd', "", b""),
                ("lnk", 'l', "sub", b""),
                ("lnk/f.txt", 'f', "", b"x"),
            ],
        );
        for conc in [1usize, 4] {
            let out = dir.join(format!("bad{conc}"));
            let err = extract_tar_gz_native_with(&bad, &out, 0, conc, None).unwrap_err();
            assert!(is_archive_unsafe(&err), "{err:#}");
            assert!(!out.join("sub/f.txt").exists());
        }
        // 运行时里合法的相对链接照常:python3 -> python3.12、../bin/python3
        let good = dir.join("good.tar.gz");
        build_raw_tar_gz(
            &good,
            &[
                ("bin/python3.12", 'f', "", b"py"),
                ("bin/python3", 'l', "python3.12", b""),
                ("lib/py", 'l', "../bin/python3", b""),
            ],
        );
        let out = dir.join("good");
        extract_tar_gz_native_with(&good, &out, 0, 4, None).unwrap();
        assert_eq!(fs::read(out.join("lib/py")).unwrap(), b"py");
        // 不安全归档不回退外部 tar 再试(外部 tar 会照建指向树外的链接)
        let strip = dir.join("strip.tar.gz");
        build_raw_tar_gz(
            &strip,
            &[("root/", 'd', "", b""), ("root/lnk", 'l', "/etc", b"")],
        );
        let err = tar_extract_strip1_with(&strip, &dir.join("strip_out"), None).unwrap_err();
        assert!(is_archive_unsafe(&err), "{err:#}");
        assert!(
            fs::symlink_metadata(dir.join("strip_out/lnk")).is_err(),
            "外部 tar 没被调起"
        );
        let _ = fs::remove_dir_all(&dir);
    }

    #[test]
    fn manifest_fetch_three_outcomes() {
        // 200+合法 JSON → Fetched;404 → Absent;200+坏 JSON → Absent(掉 API fallback)
        let client = build_github_client(10).unwrap();
        let cases: Vec<(Option<&[u8]>, bool)> = vec![
            (
                Some(br#"{"version":"9.9.9","tag":"v9.9.9","platforms":{}}"#),
                true,
            ),
            (None, false),
            (Some(b"not-json"), false),
        ];
        for (idx, (body, expect_fetched)) in cases.into_iter().enumerate() {
            let (server, base) = spawn_server();
            let manifest_url = base.replace("/asset.bin", "/horosa-latest.json");
            let handle = thread::spawn(move || {
                let mut s = server.accept().unwrap().0;
                let _ = read_request(&mut s);
                match body {
                    Some(bytes) => write_200_full(&mut s, bytes, "\"m\""),
                    None => {
                        let head = "HTTP/1.1 404 Not Found\r\nContent-Length: 0\r\nConnection: close\r\n\r\n";
                        let _ = s.write_all(head.as_bytes());
                        let _ = s.shutdown(Shutdown::Both);
                    }
                }
            });
            let got = fetch_update_manifest(&client, &manifest_url);
            assert_eq!(
                matches!(got, ManifestFetch::Fetched(_)),
                expect_fetched,
                "case {} 结果不符",
                idx + 1
            );
            handle.join().unwrap();
        }
    }

    #[test]
    fn resume_attempts_cap_forces_fresh() {
        let full = test_payload(140_000);
        let (server, url) = spawn_server();
        let ranges: Arc<Mutex<Vec<Option<String>>>> = Arc::new(Mutex::new(Vec::new()));
        let (ranges_srv, full_srv) = (ranges.clone(), full.clone());
        let handle = thread::spawn(move || {
            let mut s = server.accept().unwrap().0;
            let req = read_request(&mut s);
            ranges_srv.lock().unwrap().push(range_of(&req));
            write_200_full(&mut s, &full_srv, "\"v1\"");
        });
        let dir = temp_test_dir("dl-resume-cap");
        let dest = dir.join("asset.bin");
        let (part, meta) = download_part_paths(&dest);
        // 预造「续传次数已封顶」的病态 part:必须直接全新,防续传死循环
        fs::write(&part, &full[..70_000]).unwrap();
        save_part_meta(
            &meta,
            &PartMeta {
                url: url.clone(),
                etag: Some("\"v1\"".to_string()),
                total: full.len() as u64,
                resume_attempts: RESUME_MAX_ATTEMPTS,
            },
        );

        download_resumable_once(&url, &dest, true, |_, _| {}, |_| {})
            .expect("封顶后全新下载应成功");
        assert_eq!(fs::read(&dest).unwrap(), full);
        let seen = ranges.lock().unwrap();
        assert!(seen[0].is_none(), "封顶后不得再发 Range");
        drop(seen);
        handle.join().unwrap();
        let _ = fs::remove_dir_all(&dir);
    }
}
