use super::*;
use std::os::unix::process::ExitStatusExt;
use std::process::{ExitStatus, Output};

#[test]
fn shadow_write_args_only_accepts_whitelisted_string_pair() {
    let ok = serde_json::json!({ "key": "horosa.localCharts.v1", "text": "[]" });
    assert_eq!(
        shadow_write_args(&ok),
        Some(("horosa.localCharts.v1".to_string(), "[]".to_string()))
    );
    for bad in [
        serde_json::json!({ "key": "../x", "text": "[]" }),
        serde_json::json!({ "key": "horosa.localCharts.v1" }),
        serde_json::json!({ "key": "horosa.localCharts.v1", "text": 1 }),
        serde_json::json!(null),
    ] {
        assert_eq!(shadow_write_args(&bad), None, "{bad}");
    }
}

#[test]
fn shadow_keys_whitelist_only_four_record_stores() {
    for k in SHADOW_ALLOWED_KEYS.iter() {
        assert!(shadow_key_allowed(k));
    }
    for bad in [
        "horosa.ai.agent.ledger.v1",
        "",
        "horosa.localCharts.v1.tmp",
        "../x",
        "horosa.localCharts.v1 ",
    ] {
        assert!(!shadow_key_allowed(bad), "{bad:?} 不该进影子副本");
    }
}

fn shadow_test_dir(tag: &str) -> PathBuf {
    let uniq = SystemTime::now()
        .duration_since(UNIX_EPOCH)
        .map(|d| d.as_nanos())
        .unwrap_or(0);
    let d = std::env::temp_dir().join(format!(
        "horosa-shadow-{}-{}-{}",
        tag,
        std::process::id(),
        uniq
    ));
    fs::create_dir_all(&d).unwrap();
    d
}

fn shadow_enqueue_and_collect(
    dir: &Path,
    key: &str,
    text: &str,
) -> std::sync::mpsc::Receiver<std::result::Result<(), String>> {
    let (tx, rx) = std::sync::mpsc::channel();
    enqueue_shadow_write(
        dir.to_path_buf(),
        key.to_string(),
        text.to_string(),
        Box::new(move |r| {
            let _ = tx.send(r);
        }),
    );
    rx
}

#[test]
fn shadow_writes_land_in_dispatch_order() {
    let dir = shadow_test_dir("order");
    let key = "horosa.localCharts.v1";
    let rxs: Vec<_> = (0..40)
        .map(|i| shadow_enqueue_and_collect(&dir, key, &format!("[{{\"v\":{i}}}]")))
        .collect();
    for rx in rxs {
        assert_eq!(rx.recv().unwrap(), Ok(()));
    }
    assert_eq!(
        fs::read_to_string(dir.join(format!("{key}.json"))).unwrap(),
        "[{\"v\":39}]",
        "同一把键连写:落盘的必须是最后派发的那一次"
    );
    assert!(!dir.join(format!("{key}.json.tmp")).exists());
    let bad = shadow_enqueue_and_collect(&dir, "../x", "[]");
    assert_eq!(
        bad.recv().unwrap(),
        Err("shadow.key.not-allowed".to_string())
    );
    let _ = fs::remove_dir_all(&dir);
}

#[test]
fn shadow_exit_wait_covers_writes_still_queued() {
    // 写线程被挡住(锁在本测试手里)时连派两次影子写:一次在写、一次还在排队。
    // 两次都必须在派发时刻就计入在途,退出等待放行时两份都已在盘。
    let dir = shadow_test_dir("exitwait");
    let first = dir.join("horosa.localCases.v1.json");
    let second = dir.join("horosa.localCharts.v1.json");
    let guard = SHADOW_FS_LOCK.lock().unwrap_or_else(|p| p.into_inner());
    let rx1 = shadow_enqueue_and_collect(&dir, "horosa.localCases.v1", "[{\"cid\":\"a\"}]");
    let rx2 = shadow_enqueue_and_collect(&dir, "horosa.localCharts.v1", "[{\"cid\":\"last\"}]");
    assert!(
        SHADOW_INFLIGHT_WRITES.load(Ordering::SeqCst) >= 2,
        "还在排队的影子写也要计入在途"
    );
    let (p1, p2) = (first.clone(), second.clone());
    let waiter = std::thread::spawn(move || {
        wait_shadow_writes_settle();
        p1.exists() && p2.exists()
    });
    std::thread::sleep(std::time::Duration::from_millis(80));
    drop(guard);
    assert!(
        waiter.join().unwrap(),
        "退出等待放行时,派发了的影子写必须都已在盘"
    );
    assert_eq!(rx1.recv().unwrap(), Ok(()));
    assert_eq!(rx2.recv().unwrap(), Ok(()));
    assert_eq!(fs::read_to_string(&second).unwrap(), "[{\"cid\":\"last\"}]");
    let _ = fs::remove_dir_all(&dir);
}

#[test]
fn shadow_diverged_copy_survives_later_writes() {
    let dir = shadow_test_dir("diverged");
    let key = "horosa.localCharts.trash.v1";
    assert_eq!(keep_diverged_shadow_copy(&dir, key, 1000), Ok(None));
    write_shadow_file(&dir, key, "[{\"cid\":\"shadow-newer\"}]").unwrap();
    let first = keep_diverged_shadow_copy(&dir, key, 1000).unwrap().unwrap();
    assert_eq!(first, format!("{key}.diverged-1000.json"));
    // 内容相同不重复留
    assert_eq!(
        keep_diverged_shadow_copy(&dir, key, 2000)
            .unwrap()
            .as_deref(),
        Some(first.as_str())
    );
    // 之后的保存覆盖影子:另存的那份原样还在
    write_shadow_file(&dir, key, "[{\"cid\":\"local\"}]").unwrap();
    assert_eq!(
        fs::read_to_string(dir.join(&first)).unwrap(),
        "[{\"cid\":\"shadow-newer\"}]"
    );
    let second = keep_diverged_shadow_copy(&dir, key, 1000).unwrap().unwrap();
    assert_eq!(
        second,
        format!("{key}.diverged-1001.json"),
        "同一时刻不覆盖已有副本"
    );
    assert_eq!(
        fs::read_to_string(dir.join(&second)).unwrap(),
        "[{\"cid\":\"local\"}]"
    );
    // 启动对账只读 <key>.json:副本不会被当成影子读回
    assert_eq!(
        fs::read_to_string(dir.join(format!("{key}.json"))).unwrap(),
        "[{\"cid\":\"local\"}]"
    );
    assert!(keep_diverged_shadow_copy(&dir, "horosa.other", 1).is_err());
    let _ = fs::remove_dir_all(&dir);
}

#[test]
fn auto_backups_live_in_per_build_subfolder_and_legacy_root_is_never_pruned() {
    let root = shadow_test_dir("backup-subfolder");
    let own = root.join(APP_NAME);
    fs::create_dir_all(&own).unwrap();
    let n = |s: &str| format!("horosa-backup-{s}.zip");
    // 根目录:分子目录之前写下的旧备份 2 份 + 另一个(尚未升级的)应用之后写的 1 份;子目录:本应用 2 份
    for name in [
        n("20261001-100000"),
        n("20261002-100000"),
        n("20261020-200000"),
    ] {
        fs::write(root.join(&name), "legacy").unwrap();
    }
    for name in [n("20261010-100000"), n("20261011-100000")] {
        fs::write(own.join(&name), "own").unwrap();
    }
    fs::write(root.join("notes.txt"), "x").unwrap();
    let listed = merged_backup_listing(&backup_names_in(&own), &backup_names_in(&root));
    assert_eq!(
        listed,
        vec![
            n("20261001-100000"),
            n("20261002-100000"),
            n("20261010-100000"),
            n("20261011-100000")
        ],
        "旧备份照列;比本应用最早一份还新的根目录文件(另一个应用的)不列"
    );
    // 子目录还空(刚升级):根目录全部照列,能从旧备份恢复
    assert_eq!(merged_backup_listing(&[], &backup_names_in(&root)).len(), 3);
    // 读:先子目录,再根目录
    assert_eq!(
        fs::read_to_string(backup_path_for_read(&own, &root, &n("20261011-100000"))).unwrap(),
        "own"
    );
    assert_eq!(
        fs::read_to_string(backup_path_for_read(&own, &root, &n("20261001-100000"))).unwrap(),
        "legacy"
    );
    // 修剪:只删子目录里的;根目录的旧备份点名删也不动
    let deleted = prune_backups_in(
        &own,
        &[
            n("20261010-100000"),
            n("20261001-100000"),
            "../escape.zip".to_string(),
        ],
    );
    assert_eq!(deleted, 1);
    assert!(!own.join(n("20261010-100000")).exists());
    assert!(
        root.join(n("20261001-100000")).exists(),
        "根目录旧备份被修剪了"
    );
    assert!(root.join(n("20261020-200000")).exists());
    let _ = fs::remove_dir_all(&root);
}

#[test]
fn shadow_drop_diverged_removes_only_that_keys_copies() {
    let dir = shadow_test_dir("drop-diverged");
    let key = "horosa.localCharts.v1";
    let other = "horosa.localCases.v1";
    write_shadow_file(&dir, key, "[{\"cid\":\"a\"}]").unwrap();
    keep_diverged_shadow_copy(&dir, key, 1000).unwrap();
    write_shadow_file(&dir, key, "[{\"cid\":\"b\"}]").unwrap();
    keep_diverged_shadow_copy(&dir, key, 2000).unwrap();
    write_shadow_file(&dir, other, "[{\"cid\":\"c\"}]").unwrap();
    keep_diverged_shadow_copy(&dir, other, 3000).unwrap();
    // 名字像副本但不是(时刻不是数字 / 后缀不对):不碰
    fs::write(dir.join(format!("{key}.diverged-x.json")), "keep").unwrap();
    fs::write(dir.join(format!("{key}.diverged-1000.json.tmp")), "keep").unwrap();
    assert_eq!(drop_diverged_shadow_copies(&dir, key), Ok(2));
    let names: std::collections::BTreeSet<String> = fs::read_dir(&dir)
        .unwrap()
        .flatten()
        .map(|e| e.file_name().to_string_lossy().to_string())
        .collect();
    assert!(names.contains(&format!("{key}.json")), "影子本体不许删");
    assert!(
        names.contains(&format!("{other}.diverged-3000.json")),
        "别的键的副本不许删"
    );
    assert!(names.contains(&format!("{key}.diverged-x.json")));
    assert!(names.contains(&format!("{key}.diverged-1000.json.tmp")));
    assert!(!names.contains(&format!("{key}.diverged-1000.json")));
    assert!(!names.contains(&format!("{key}.diverged-2000.json")));
    // 再删一次:没有可删的
    assert_eq!(drop_diverged_shadow_copies(&dir, key), Ok(0));
    assert!(drop_diverged_shadow_copies(&dir, "horosa.other").is_err());
    let _ = fs::remove_dir_all(&dir);
}

#[test]
fn shadow_diverged_copies_capped_per_key() {
    let dir = shadow_test_dir("cap");
    let key = "horosa.localCases.trash.v1";
    for i in 0..(SHADOW_DIVERGED_KEEP as u128 + 3) {
        write_shadow_file(&dir, key, &format!("[{{\"n\":{i}}}]")).unwrap();
        keep_diverged_shadow_copy(&dir, key, 5000 + i).unwrap();
    }
    let mut names: Vec<String> = fs::read_dir(&dir)
        .unwrap()
        .flatten()
        .map(|e| e.file_name().to_string_lossy().to_string())
        .filter(|n| n.contains(".diverged-"))
        .collect();
    names.sort();
    assert_eq!(names.len(), SHADOW_DIVERGED_KEEP);
    assert_eq!(
        names[0],
        format!("{key}.diverged-5003.json"),
        "超出时删最早的"
    );
    let _ = fs::remove_dir_all(&dir);
}

#[test]
fn backup_file_name_validation_vectors() {
    for ok in [
        "horosa-backup-20260909-120000.zip",
        "horosa-backup-x.zip",
        "horosa-backup-a.b-c.zip",
    ] {
        assert!(is_backup_file_name(ok), "{ok}");
    }
    for bad in [
        "backup.zip",
        "horosa-backup-.tar",
        "horosa-backup-../x.zip",
        "horosa-backup-a b.zip",
        "horosa-backup-中.zip",
        "/tmp/horosa-backup-x.zip",
        "horosa-backup-x.zip/",
        "horosa-backup-x.ZIP",
    ] {
        assert!(!is_backup_file_name(bad), "{bad}");
    }
}

#[test]
fn preferences_default_calls_per_minute_and_roundtrip() {
    // 旧偏好文件没有该键 ⇒ serde 缺省 60(不改旧用户行为)
    let mut v: serde_json::Value = serde_json::to_value(AppPreferences::default()).unwrap();
    v.as_object_mut().unwrap().remove("mcpCallsPerMinute");
    let p: AppPreferences =
        serde_json::from_value(v).expect("prefs without the new key deserialise");
    assert_eq!(p.mcp_calls_per_minute, 60);
    assert!(!p.scheduler_enabled && !p.mcp_server_enabled && !p.agent_enabled);
    let mut q = AppPreferences::default();
    q.mcp_calls_per_minute = 240;
    q.scheduler_enabled = true;
    let text = serde_json::to_string(&q).unwrap();
    let back: AppPreferences = serde_json::from_str(&text).unwrap();
    assert_eq!(back.mcp_calls_per_minute, 240);
    assert!(back.scheduler_enabled);
}

fn out(code: i32, stdout: &str) -> std::io::Result<Output> {
    Ok(Output {
        status: ExitStatus::from_raw(code << 8),
        stdout: stdout.as_bytes().to_vec(),
        stderr: Vec::new(),
    })
}

#[test]
fn master_key_runner_hit_miss_and_add_failure() {
    let calls = std::sync::Mutex::new(Vec::<String>::new());
    let hit = |args: &[&str]| {
        calls.lock().unwrap().push(args[0].to_string());
        out(0, "EXISTING-KEY\n")
    };
    assert_eq!(
        get_or_create_ai_master_key_with(&hit).unwrap(),
        "EXISTING-KEY"
    );
    assert_eq!(calls.lock().unwrap().as_slice(), ["find-generic-password"]);
    let calls2 = std::sync::Mutex::new(Vec::<String>::new());
    let miss_then_add = |args: &[&str]| {
        calls2.lock().unwrap().push(args[0].to_string());
        if args[0] == "find-generic-password" {
            out(44, "")
        } else {
            assert_eq!(args[7], "-U");
            out(0, "")
        }
    };
    let k = get_or_create_ai_master_key_with(&miss_then_add).unwrap();
    assert_eq!(k.len(), 44);
    assert!(BASE64_STANDARD
        .decode(&k)
        .map(|b| b.len() == 32)
        .unwrap_or(false));
    assert_eq!(
        calls2.lock().unwrap().as_slice(),
        ["find-generic-password", "add-generic-password"]
    );
    // find 非 44 失败(钥匙串锁定 36 / 命中空串)绝不新建:不得调用 add-generic-password
    for (code, stdout) in [(36, ""), (1, ""), (0, "")] {
        let calls3 = std::sync::Mutex::new(Vec::<String>::new());
        let locked = |args: &[&str]| {
            calls3.lock().unwrap().push(args[0].to_string());
            assert_eq!(args[0], "find-generic-password", "must not create a key");
            out(code, stdout)
        };
        assert!(get_or_create_ai_master_key_with(&locked).is_err());
        assert_eq!(calls3.lock().unwrap().as_slice(), ["find-generic-password"]);
    }
    let add_fail = |args: &[&str]| {
        if args[0] == "find-generic-password" {
            out(44, "")
        } else {
            out(1, "")
        }
    };
    assert!(get_or_create_ai_master_key_with(&add_fail).is_err());
    // 命中但只回空白(含换行):同属「命中空串」,一律 Err 且绝不调用 add-generic-password(旧钥不被覆盖)。
    let calls4 = std::sync::Mutex::new(Vec::<String>::new());
    let empty_hit = |args: &[&str]| {
        calls4.lock().unwrap().push(args[0].to_string());
        if args[0] == "find-generic-password" {
            out(0, "\n")
        } else {
            out(0, "")
        }
    };
    assert!(get_or_create_ai_master_key_with(&empty_hit).is_err());
    assert_eq!(calls4.lock().unwrap().as_slice(), ["find-generic-password"]);
}

#[test]
fn navigation_gate_allows_only_app_origins_and_hands_external_to_browser() {
    let d = |u: &str| navigation_decision(&tauri::Url::parse(u).expect(u));
    for ok in [
        "tauri://localhost/index.html",
        "http://tauri.localhost/index.html",
        "http://127.0.0.1:53817/index.html#/",
        "http://localhost:8000/",
        "http://[::1]:9999/x",
        "about:blank",
        "about:srcdoc",
        "data:text/html,hi",
        "blob:http://127.0.0.1:53817/0b1c",
        "asset://localhost/x.png",
        "ipc://localhost/cmd",
    ] {
        assert_eq!(d(ok), NavigationDecision::Allow, "{ok}");
    }
    assert_eq!(
        d("https://example.com/a?b=1"),
        NavigationDecision::OpenExternal("https://example.com/a?b=1".to_string())
    );
    assert_eq!(
        d("HTTP://Example.com"),
        NavigationDecision::OpenExternal("http://example.com/".to_string())
    );
    // 回环之外的本机名 / 局域网地址都不是本应用来源
    assert_eq!(
        d("http://127.0.0.2:8000/"),
        NavigationDecision::OpenExternal("http://127.0.0.2:8000/".to_string())
    );
    assert_eq!(
        d("http://localhost.example.com/"),
        NavigationDecision::OpenExternal("http://localhost.example.com/".to_string())
    );
    for deny in [
        "javascript:alert(1)",
        "file:///etc/hosts",
        "mailto:a@b.c",
        "ftp://example.com/x",
        "custom-scheme://x",
    ] {
        assert_eq!(d(deny), NavigationDecision::Deny, "{deny}");
    }
}

#[test]
fn navigation_gate_is_wired_on_main_and_secondary_windows() {
    let src = include_str!("ui_windows.rs");
    assert_eq!(src.matches(".on_navigation(navigation_gate)").count(), 2);
    let main_at = src.find("fn build_main_window(").unwrap();
    let sec_at = src.find("fn create_secondary_window(").unwrap();
    let gates: Vec<usize> = src
        .match_indices(".on_navigation(navigation_gate)")
        .map(|(i, _)| i)
        .collect();
    assert!(gates.iter().any(|&g| g > main_at && g < sec_at));
    assert!(gates.iter().any(|&g| g > sec_at));
}

/// 每个建窗链(`WebviewWindowBuilder::new(` 到 `.build()`)上必须挂导航闸 —— 扫全部壳源,不只 ui_windows.rs
fn window_builders_without_navigation_gate(name: &str, src: &str) -> Vec<String> {
    let code = strip_rust_comments(src);
    let mut bad = Vec::new();
    for (i, _) in code.match_indices("WebviewWindowBuilder::new(") {
        let rest = &code[i..];
        let end = rest.find(".build()").unwrap_or(rest.len());
        if !rest[..end].contains(".on_navigation(") {
            let line = code[..i].matches('\n').count() + 1;
            bad.push(format!("{name}:{line}"));
        }
    }
    bad
}

#[test]
fn every_window_builder_has_a_navigation_gate() {
    let mut bad = Vec::new();
    let mut builders = 0;
    for (name, src) in shell_src_files() {
        builders += strip_rust_comments(&src)
            .matches("WebviewWindowBuilder::new(")
            .count();
        bad.extend(window_builders_without_navigation_gate(&name, &src));
    }
    assert!(
        bad.is_empty(),
        "建窗没挂导航闸(外站链接会在本应用窗口里打开):\n{}",
        bad.join("\n")
    );
    assert!(builders >= 2, "建窗点扫描静默失效:{builders}");
    // 判别力:没挂闸的建窗链认得出,注释里的不算
    let sample = r#"
        WebviewWindowBuilder::new(&app, label, WebviewUrl::External(url)).title(t).build()
        WebviewWindowBuilder::new(&app, l2, u2).on_navigation(navigation_gate).build()
        // WebviewWindowBuilder::new(&app, l3, u3).build()
    "#;
    assert_eq!(
        window_builders_without_navigation_gate("sample", sample).len(),
        1
    );
}

// ── 原生菜单 / 对话框文案随界面简繁:单源表 + 调用点不许写死中文 ──
fn shell_src_files() -> Vec<(String, String)> {
    let dir = std::path::Path::new(env!("CARGO_MANIFEST_DIR")).join("src");
    let mut out = Vec::new();
    for e in std::fs::read_dir(&dir).unwrap() {
        let p = e.unwrap().path();
        let name = p.file_name().unwrap().to_string_lossy().to_string();
        if !name.ends_with(".rs") || name.ends_with("tests.rs") || name == "tests.rs" {
            continue;
        }
        out.push((name, std::fs::read_to_string(&p).unwrap()));
    }
    out
}

fn has_cjk(s: &str) -> bool {
    s.chars()
        .any(|c| ('\u{4e00}'..='\u{9fff}').contains(&c) || ('\u{3400}'..='\u{4dbf}').contains(&c))
}

/// 去掉 Rust 注释(字符串 / 字符字面量里的 // 与 /* 不算);换行保留,行号不变
fn strip_rust_comments(src: &str) -> String {
    let b: Vec<char> = src.chars().collect();
    let mut out = String::with_capacity(src.len());
    let mut i = 0;
    while i < b.len() {
        let c = b[i];
        if c == '/' && b.get(i + 1) == Some(&'/') {
            while i < b.len() && b[i] != '\n' {
                i += 1;
            }
            continue;
        }
        if c == '/' && b.get(i + 1) == Some(&'*') {
            i += 2;
            while i < b.len() && !(b[i] == '*' && b.get(i + 1) == Some(&'/')) {
                if b[i] == '\n' {
                    out.push('\n');
                }
                i += 1;
            }
            i += 2;
            continue;
        }
        if c == '"' {
            out.push(c);
            i += 1;
            while i < b.len() && b[i] != '"' {
                if b[i] == '\\' {
                    out.push(b[i]);
                    i += 1;
                }
                if i < b.len() {
                    out.push(b[i]);
                    i += 1;
                }
            }
            if i < b.len() {
                out.push('"');
                i += 1;
            }
            continue;
        }
        // 字符字面量('"' / '\'' / '/'):整个照抄,免得把里面的引号当字符串起点;生命周期('a)照常
        if c == '\'' {
            let close = if b.get(i + 1) == Some(&'\\') { 3 } else { 2 };
            if b.get(i + close) == Some(&'\'') {
                for k in 0..=close {
                    out.push(b[i + k]);
                }
                i += close + 1;
                continue;
            }
        }
        out.push(c);
        i += 1;
    }
    out
}

/// 代码(已去注释)里的普通字符串字面量内容
fn string_literals(code: &str) -> Vec<String> {
    let b: Vec<char> = code.chars().collect();
    let mut out = Vec::new();
    let mut i = 0;
    while i < b.len() {
        if b[i] == '\'' {
            let close = if b.get(i + 1) == Some(&'\\') { 3 } else { 2 };
            if b.get(i + close) == Some(&'\'') {
                i += close + 1;
                continue;
            }
        }
        if b[i] == '"' {
            let mut lit = String::new();
            i += 1;
            while i < b.len() && b[i] != '"' {
                if b[i] == '\\' {
                    i += 1;
                }
                if i < b.len() {
                    lit.push(b[i]);
                    i += 1;
                }
            }
            out.push(lit);
        }
        i += 1;
    }
    out
}

/// 从 open(左括号 / 左花括号的下一位)起到配平的右括号为止(跳过字符串)
fn balanced_span(code: &str, open: usize, l: char, r: char) -> &str {
    let mut depth = 1;
    let mut in_str = false;
    let mut esc = false;
    for (k, c) in code[open..].char_indices() {
        if in_str {
            if esc {
                esc = false;
            } else if c == '\\' {
                esc = true;
            } else if c == '"' {
                in_str = false;
            }
            continue;
        }
        if c == '"' {
            in_str = true;
        } else if c == l {
            depth += 1;
        } else if c == r {
            depth -= 1;
            if depth == 0 {
                return &code[open..open + k];
            }
        }
    }
    &code[open..]
}

/// 画在网页之外的原生文字的去处:这些调用的整个实参里(含 format! / unwrap_or_else 一类)不许出现写死的中文字面量
const NATIVE_TEXT_SINKS: &[&str] = &[
    ".set_title(",
    ".set_description(",
    ".title(",
    "OkCancelCustom(",
    "OkCustom(",
    "YesNoCancelCustom(",
    "MenuItem::with_id(",
    "CheckMenuItem::with_id(",
    "Submenu::with_items(",
    "PredefinedMenuItem::",
    "show_macos_notification(",
    "create_secondary_window(",
];

/// 返回值整段进原生对话框 / 通知的函数(函数体里不许有写死的中文字面量;改经 shell_text 取)
const NATIVE_TEXT_PRODUCERS: &[(&str, &str)] = &[
    ("updater_manifest.rs", "fn notify_only_message_in("),
    ("updater_check.rs", "fn format_runtime_status("),
    ("updater_helper.rs", "fn relocate_app_to_applications("),
    ("runtime_slots.rs", "fn message_in("),
    ("runtime_slots.rs", "fn inspect_shared_tree_at("),
    ("runtime_paths.rs", "fn show_post_update_notice_if_needed("),
];

fn hardcoded_native_texts(name: &str, src: &str) -> Vec<String> {
    let code = strip_rust_comments(src);
    let mut bad = Vec::new();
    for pat in NATIVE_TEXT_SINKS {
        for (i, _) in code.match_indices(pat) {
            // 看整个实参:format! / unwrap_or_else / 嵌套调用里的字面量都算(`PredefinedMenuItem::xxx(` 一族从方法名后的括号起)
            let mut open = i + pat.len();
            if pat.ends_with("::") {
                match code[open..].find('(') {
                    Some(k)
                        if k > 0
                            && code[open..open + k]
                                .chars()
                                .all(|c| c.is_ascii_alphanumeric() || c == '_') =>
                    {
                        open += k + 1
                    }
                    _ => continue, // `use …::{PredefinedMenuItem, …}` 一类不是调用
                }
            }
            let args = balanced_span(&code, open, '(', ')');
            for lit in string_literals(args) {
                if has_cjk(&lit) {
                    bad.push(format!("{name}: {pat}…\"{lit}\""));
                }
            }
        }
    }
    bad
}

fn hardcoded_producer_texts(name: &str, src: &str, fn_head: &str) -> Option<Vec<String>> {
    let code = strip_rust_comments(src);
    let at = code.find(fn_head)?;
    let open = at + code[at..].find('{')? + 1;
    let body = balanced_span(&code, open, '{', '}');
    Some(
        string_literals(body)
            .into_iter()
            .filter(|lit| has_cjk(lit))
            .map(|lit| format!("{name}: {fn_head}…\"{lit}\""))
            .collect(),
    )
}

#[test]
fn native_menu_and_dialog_texts_come_from_the_shell_string_table() {
    let mut bad = Vec::new();
    let files = shell_src_files();
    for (name, src) in &files {
        bad.extend(hardcoded_native_texts(name, src));
    }
    for (file, head) in NATIVE_TEXT_PRODUCERS {
        let (_, src) = files
            .iter()
            .find(|(n, _)| n == file)
            .unwrap_or_else(|| panic!("登记的文件不在:{file}"));
        match hardcoded_producer_texts(file, src, head) {
            Some(found) => bad.extend(found),
            None => panic!("登记的函数不在了(改名就改登记):{file} {head}"),
        }
    }
    assert!(bad.is_empty(), "原生菜单 / 对话框 / 通知 / 窗口标题写死了中文(改经 shell_text 取,文案进 shell_strings.json):\n{}", bad.join("\n"));
    // 判别力:写死的各种形态都认得出(含 format! / unwrap_or_else / 经函数实参),经表取的与注释里的不算
    let sample = r#"MessageDialog::new().set_title("检查更新失败").set_description(format!("搬迁未完成:{err}"))
        MenuItem::with_id(app, MENU_X, "放大", true, None)
        Submenu::with_items(app, "文件", true, &[])
        WebviewWindowBuilder::new(&app, l, u).title(title.unwrap_or_else(|| "打印".to_string()))
        show_macos_notification("已完成更新", &body);
        create_secondary_window(app, LABEL, "偏好设置", "settings.html", (1.0, 1.0), (1.0, 1.0))
        &PredefinedMenuItem::hide(app, Some("隐藏星阙"))?, &PredefinedMenuItem::separator(app)?,
        use tauri::menu::{Menu, PredefinedMenuItem}; let x = f("不是菜单文案");
        .set_title(shell_text("dlg.x")) MenuItem::with_id(app, MENU_Y, &shell_text("menu.y"), true, None)
        // .set_title("注释里的不算")
        .set_description(shell_text_fmt("dlg.relocate.failed", &[("err", &format!("{err:#}"))]))"#;
    assert_eq!(
        hardcoded_native_texts("sample", sample).len(),
        8,
        "{:?}",
        hardcoded_native_texts("sample", sample)
    );
    let producer = r#"fn relocate_app_to_applications(app: &AppHandle) -> Result<String> {
        if x { return Ok("当前已从「应用程序」文件夹运行".to_string()); }
        Err(anyhow!("{}", shell_text("dlg.relocate.copy_failed")))
    }"#;
    assert_eq!(
        hardcoded_producer_texts("p", producer, "fn relocate_app_to_applications(")
            .unwrap()
            .len(),
        1
    );
}

#[test]
fn shell_string_ids_used_in_source_all_exist_and_none_is_dead() {
    let table: std::collections::HashMap<String, serde_json::Value> =
        serde_json::from_str(include_str!("../shell_strings.json")).unwrap();
    let ids: std::collections::BTreeSet<String> = table
        .keys()
        .filter(|k| !k.starts_with('_'))
        .cloned()
        .collect();
    let mut used = std::collections::BTreeSet::new();
    for (_, src) in shell_src_files() {
        let mut rest = src.as_str();
        while let Some(q) = rest.find('"') {
            let body = &rest[q + 1..];
            let Some(end) = body.find('"') else { break };
            let lit = &body[..end];
            if ["menu.", "dlg.", "btn.", "update.", "win.", "notify."]
                .iter()
                .any(|p| lit.starts_with(p))
                && lit
                    .chars()
                    .all(|c| c.is_ascii_lowercase() || c == '.' || c == '_')
            {
                used.insert(lit.to_string());
            }
            rest = &body[end + 1..];
        }
    }
    let missing: Vec<_> = used.difference(&ids).collect();
    let dead: Vec<_> = ids.difference(&used).collect();
    assert!(missing.is_empty(), "源码用了表里没有的文案 id:{missing:?}");
    assert!(dead.is_empty(), "表里有、源码不用的文案 id:{dead:?}");
    for id in &ids {
        let v = &table[id];
        let hans = v["hans"].as_str().unwrap();
        let hant = v["hant"].as_str().unwrap();
        assert!(!hans.is_empty() && !hant.is_empty(), "{id}");
        assert_eq!(
            hans.chars().count(),
            hant.chars().count(),
            "{id} 简繁逐字等长"
        );
    }
}

#[test]
fn shell_text_follows_script_mode_and_fills_placeholders_once() {
    let was = shell_script_is_hant();
    set_shell_script_hant(false);
    assert_eq!(shell_text("menu.check_updates"), "检查更新");
    set_shell_script_hant(true);
    assert_eq!(shell_text("menu.check_updates"), "檢查更新");
    assert_eq!(
        shell_text_fmt("dlg.relocate.failed", &[("err", "x {err} y")]),
        "搬遷未完成:x {err} y"
    );
    set_shell_script_hant(was);
    assert_eq!(shell_text("no.such.id"), "no.such.id");
    assert_eq!(
        fill_placeholders("{a}-{b}-{c}", &[("a", "1"), ("b", "{a}")]),
        "1-{a}-{c}"
    );
    assert_eq!(fill_placeholders("no brace {", &[]), "no brace {");
    // 两个档的模板占位符一致
    let table: std::collections::HashMap<String, serde_json::Value> =
        serde_json::from_str(include_str!("../shell_strings.json")).unwrap();
    let holes = |s: &str| -> Vec<String> {
        let mut v = Vec::new();
        let mut r = s;
        while let Some(o) = r.find('{') {
            let a = &r[o + 1..];
            let Some(c) = a.find('}') else { break };
            v.push(a[..c].to_string());
            r = &a[c + 1..];
        }
        v
    };
    for (id, v) in table.iter().filter(|(k, _)| !k.starts_with('_')) {
        assert_eq!(
            holes(v["hans"].as_str().unwrap()),
            holes(v["hant"].as_str().unwrap()),
            "{id}"
        );
    }
}

#[test]
fn shell_pages_get_script_mode_at_window_build_and_on_switch() {
    let was = shell_script_is_hant();
    set_shell_script_hant(true);
    assert_eq!(
        shell_script_init_script(),
        r#"window.__HOROSA_SHELL_SCRIPT = "hant";"#
    );
    assert_eq!(get_shell_script_command(), "hant");
    set_shell_script_hant(false);
    assert_eq!(
        shell_script_init_script(),
        r#"window.__HOROSA_SHELL_SCRIPT = "hans";"#
    );
    assert_eq!(get_shell_script_command(), "hans");
    set_shell_script_hant(was);
    // 建窗链:主窗口与次窗口都注入档位;切换时推给已开着的壳自带页面
    let windows = include_str!("ui_windows.rs");
    assert_eq!(
        windows
            .matches(".initialization_script(shell_script_init_script())")
            .count(),
        2
    );
    let text = include_str!("shell_text.rs");
    let set = &text[text.find("fn set_shell_script_command(").unwrap()..];
    assert!(set[..set.find("\n}\n").unwrap()].contains("push_shell_script_to_pages(&app);"));
    assert!(include_str!("main.rs").contains("get_shell_script_command,"));
}
