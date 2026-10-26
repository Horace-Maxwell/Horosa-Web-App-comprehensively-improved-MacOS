//! 桌面通知(限流 / 去重)与通知脚本钩。

use super::*;

pub(crate) fn show_macos_notification(title: &str, body: &str) {
    let _ = Command::new("/usr/bin/osascript")
        .arg("-e")
        .arg(format!(
            "display notification {} with title {}",
            applescript_quote_text(body),
            applescript_quote_text(title)
        ))
        .stdout(Stdio::null())
        .stderr(Stdio::null())
        .spawn();
}

// ── 桌面通知命令:偏好门(show_status_notifications)+ 脱控制字符/截断 + 令牌桶(6/min,突发 3)+ 10 秒同文去重;
//    页面永远拿不到 osascript,标题/正文只经本函数清洗后进 show_macos_notification。
fn sanitize_notification_text(text: &str, max_chars: usize) -> String {
    // 控制字符(含换行/制表)一律变空格再折叠:绝不把两个词粘在一起,也绝不让换行进 osascript 参数
    let cleaned: String = text
        .chars()
        .map(|c| if c.is_control() { ' ' } else { c })
        .collect::<String>()
        .split_whitespace()
        .collect::<Vec<_>>()
        .join(" ");
    if cleaned.chars().count() > max_chars {
        let mut s: String = cleaned.chars().take(max_chars.saturating_sub(1)).collect();
        s.push('…');
        s
    } else {
        cleaned
    }
}

pub(crate) struct NotifyLimiter {
    pub(crate) tokens: f64,
    last_refill: Instant,
    last_text: String,
    last_at: Option<Instant>,
}
static NOTIFY_LIMITER: Mutex<Option<NotifyLimiter>> = Mutex::new(None);
const NOTIFY_RATE_PER_MIN: f64 = 6.0;
const NOTIFY_BURST: f64 = 3.0;
const NOTIFY_DEDUPE_SECS: u64 = 10;

fn notify_limiter_decide(
    state: &mut NotifyLimiter,
    now: Instant,
    text: &str,
) -> std::result::Result<(), &'static str> {
    let elapsed = now
        .saturating_duration_since(state.last_refill)
        .as_secs_f64();
    state.tokens = (state.tokens + elapsed * NOTIFY_RATE_PER_MIN / 60.0).min(NOTIFY_BURST);
    state.last_refill = now;
    if let Some(at) = state.last_at {
        if state.last_text == text
            && now.saturating_duration_since(at).as_secs() < NOTIFY_DEDUPE_SECS
        {
            return Err("duplicate");
        }
    }
    if state.tokens < 1.0 {
        return Err("rate_limited");
    }
    state.tokens -= 1.0;
    state.last_text = text.to_string();
    state.last_at = Some(now);
    Ok(())
}

#[tauri::command]
pub(crate) fn show_desktop_notification_command(
    app: AppHandle,
    title: String,
    body: String,
) -> std::result::Result<serde_json::Value, String> {
    let prefs = load_preferences(&app);
    if !prefs.show_status_notifications {
        return Ok(serde_json::json!({ "shown": false, "reason": "preference_off" }));
    }
    let t = sanitize_notification_text(&title, 60);
    let b = sanitize_notification_text(&body, 240);
    if t.is_empty() && b.is_empty() {
        return Ok(serde_json::json!({ "shown": false, "reason": "empty" }));
    }
    let key = format!("{t}\n{b}");
    let decision = {
        let mut guard = NOTIFY_LIMITER
            .lock()
            .map_err(|_| "notify limiter poisoned".to_string())?;
        let state = guard.get_or_insert_with(|| NotifyLimiter {
            tokens: NOTIFY_BURST,
            last_refill: Instant::now(),
            last_text: String::new(),
            last_at: None,
        });
        let d = notify_limiter_decide(state, Instant::now(), &key);
        d
    };
    match decision {
        Ok(()) => {
            show_macos_notification(&t, &b);
            ledger_mark(
                "rust.notification",
                Some(
                    serde_json::json!({ "title_len": t.chars().count(), "body_len": b.chars().count() }),
                ),
            );
            Ok(serde_json::json!({ "shown": true, "reason": "" }))
        }
        Err(reason) => Ok(serde_json::json!({ "shown": false, "reason": reason })),
    }
}

#[cfg(test)]
mod desktop_notify_tests {
    use super::*;

    #[test]
    fn sanitize_notification_text_caps_and_strips_controls() {
        assert_eq!(
            sanitize_notification_text("a\u{0007}b\n\tc   d", 10),
            "a b c d"
        );
        let long = sanitize_notification_text(&"星".repeat(100), 60);
        assert_eq!(long.chars().count(), 60);
        assert!(long.ends_with('…'));
        assert_eq!(sanitize_notification_text("  \u{0001} ", 10), "");
    }

    #[test]
    fn notify_limiter_burst_then_blocks_and_dedupes() {
        let now = Instant::now();
        let mut st = NotifyLimiter {
            tokens: NOTIFY_BURST,
            last_refill: now,
            last_text: String::new(),
            last_at: None,
        };
        assert!(notify_limiter_decide(&mut st, now, "a").is_ok());
        assert_eq!(notify_limiter_decide(&mut st, now, "a"), Err("duplicate"));
        assert!(notify_limiter_decide(&mut st, now, "b").is_ok());
        assert!(notify_limiter_decide(&mut st, now, "c").is_ok());
        assert_eq!(
            notify_limiter_decide(&mut st, now, "d"),
            Err("rate_limited")
        );
        let later = now + std::time::Duration::from_secs(11);
        assert!(notify_limiter_decide(&mut st, later, "a").is_ok());
        let much_later = now + std::time::Duration::from_secs(120);
        assert!(notify_limiter_decide(&mut st, much_later, "e").is_ok());
        assert!(notify_limiter_decide(&mut st, much_later, "f").is_ok());
        assert!(notify_limiter_decide(&mut st, much_later, "g").is_ok());
        assert_eq!(
            notify_limiter_decide(&mut st, much_later, "h"),
            Err("rate_limited")
        );
    }
}

// ── 通知外部脚本钩 ──
pub const NOTIFY_HOOK_TIMEOUT_MS: u64 = 10_000;
pub const NOTIFY_HOOK_PAYLOAD_MAX: usize = 8 * 1024;

fn notify_hook_kill_switch() -> bool {
    std::env::var("HOROSA_NOTIFY_HOOK")
        .map(|v| v.trim() == "0")
        .unwrap_or(false)
}

fn notify_hook_allowed_roots() -> Vec<PathBuf> {
    let mut roots = vec![PathBuf::from("/usr/local/bin")];
    if let Some(h) = std::env::var_os("HOME") {
        let p = PathBuf::from(h);
        if !p.as_os_str().is_empty() {
            roots.insert(0, p);
        }
    }
    roots
}

/// 路径六道门:绝对 → 存在且常规文件(经 canonicalize,符号链接看目标)→ 位于允许根之下 → 可执行 → 非全员可写 → 目录也非全员可写。
/// 文案只说原因,不回显路径。
fn validate_notify_hook_path_with_roots(
    raw: &str,
    roots: &[PathBuf],
) -> std::result::Result<PathBuf, String> {
    use std::os::unix::fs::PermissionsExt;
    let p = Path::new(raw.trim());
    if raw.trim().is_empty() {
        return Err("路径为空".to_string());
    }
    if !p.is_absolute() {
        return Err("必须是绝对路径".to_string());
    }
    let canon = fs::canonicalize(p).map_err(|_| "文件不存在".to_string())?;
    let meta = fs::metadata(&canon).map_err(|_| "文件不可读".to_string())?;
    if !meta.is_file() {
        return Err("必须是常规文件(不是目录)".to_string());
    }
    let inside = roots.iter().any(|r| {
        fs::canonicalize(r)
            .map(|rc| canon.starts_with(&rc))
            .unwrap_or(false)
    });
    if !inside {
        return Err("脚本必须放在你的用户目录或 /usr/local/bin 之下".to_string());
    }
    let mode = meta.permissions().mode();
    if mode & 0o111 == 0 {
        return Err("文件不可执行(chmod +x)".to_string());
    }
    if mode & 0o002 != 0 {
        return Err("文件对所有人可写,拒绝(chmod o-w)".to_string());
    }
    if let Some(dir) = canon.parent() {
        if let Ok(dm) = fs::metadata(dir) {
            if dm.permissions().mode() & 0o002 != 0 && dm.permissions().mode() & 0o1000 == 0 {
                return Err("所在目录对所有人可写,拒绝".to_string());
            }
        }
    }
    Ok(canon)
}

fn validate_notify_hook_path(raw: &str) -> std::result::Result<PathBuf, String> {
    validate_notify_hook_path_with_roots(raw, &notify_hook_allowed_roots())
}

/// 跑脚本:零 shell(路径即程序,载荷是唯一参数);stdin 关、stdout/stderr 丢;10s 到点 kill。回 (exit_code, timed_out)。
fn run_notify_hook_process(
    path: &Path,
    payload: &str,
) -> std::result::Result<(Option<i32>, bool), String> {
    run_notify_hook_process_with_timeout(path, payload, NOTIFY_HOOK_TIMEOUT_MS)
}

/// 同上,超时可参数化(测试用短超时证明 kill 路径;生产恒 NOTIFY_HOOK_TIMEOUT_MS)
fn run_notify_hook_process_with_timeout(
    path: &Path,
    payload: &str,
    timeout_ms: u64,
) -> std::result::Result<(Option<i32>, bool), String> {
    let mut child = Command::new(path)
        .arg(payload)
        .stdin(Stdio::null())
        .stdout(Stdio::null())
        .stderr(Stdio::null())
        .spawn()
        .map_err(|e| format!("启动失败({})", e.kind()))?;
    let started = Instant::now();
    loop {
        match child.try_wait() {
            Ok(Some(status)) => return Ok((status.code(), false)),
            Ok(None) => {
                if started.elapsed() >= Duration::from_millis(timeout_ms) {
                    let _ = child.kill();
                    let _ = child.wait();
                    return Ok((None, true));
                }
                thread::sleep(Duration::from_millis(25));
            }
            Err(e) => return Err(format!("等待失败({})", e.kind())),
        }
    }
}

fn notify_hook_status_value(prefs: &AppPreferences) -> serde_json::Value {
    let valid = if prefs.notify_hook_path.trim().is_empty() {
        Err("未设置".to_string())
    } else {
        validate_notify_hook_path(&prefs.notify_hook_path).map(|_| ())
    };
    serde_json::json!({
        "enabled": prefs.notify_hook_enabled,
        "path": prefs.notify_hook_path,
        "killSwitch": notify_hook_kill_switch(),
        "valid": valid.is_ok(),
        "reason": valid.err().unwrap_or_default(),
        "timeoutMs": NOTIFY_HOOK_TIMEOUT_MS,
    })
}

#[tauri::command]
pub(crate) fn notify_hook_status_command(
    app: AppHandle,
) -> std::result::Result<serde_json::Value, String> {
    Ok(notify_hook_status_value(&load_preferences(&app)))
}

#[tauri::command]
pub(crate) fn notify_hook_set_command(
    app: AppHandle,
    enabled: bool,
    path: String,
) -> std::result::Result<serde_json::Value, String> {
    let mut prefs = load_preferences(&app);
    let trimmed = path.trim().to_string();
    if enabled {
        validate_notify_hook_path(&trimmed)?;
    }
    prefs.notify_hook_enabled = enabled;
    prefs.notify_hook_path = trimmed;
    save_preferences(&app, &prefs).map_err(|err| format!("{err:#}"))?;
    Ok(notify_hook_status_value(&prefs))
}

/// 页面(自动化动作 notify-script / 面板「测试运行」)触发:门 → 校验 → 限流 → 跑;永不吐路径以外的系统信息。
#[tauri::command]
pub(crate) fn notify_hook_run_command(
    app: AppHandle,
    payload: serde_json::Value,
    test: Option<bool>,
) -> std::result::Result<serde_json::Value, String> {
    let prefs = load_preferences(&app);
    if notify_hook_kill_switch() {
        return Ok(serde_json::json!({ "ran": false, "reason": "kill_switch" }));
    }
    if !prefs.notify_hook_enabled {
        return Ok(serde_json::json!({ "ran": false, "reason": "disabled" }));
    }
    let path = match validate_notify_hook_path(&prefs.notify_hook_path) {
        Ok(p) => p,
        Err(reason) => {
            return Ok(
                serde_json::json!({ "ran": false, "reason": format!("invalid_path:{reason}") }),
            )
        }
    };
    let mut body = payload;
    if !body.is_object() {
        body = serde_json::json!({ "text": body });
    }
    let text = body.to_string();
    if text.len() > NOTIFY_HOOK_PAYLOAD_MAX {
        return Ok(serde_json::json!({ "ran": false, "reason": "payload_too_large" }));
    }
    if test != Some(true) {
        let key = format!(
            "hook:{}",
            body.get("title").and_then(|t| t.as_str()).unwrap_or("")
        );
        let decision = {
            let mut guard = NOTIFY_LIMITER
                .lock()
                .map_err(|_| "notify limiter poisoned".to_string())?;
            let state = guard.get_or_insert_with(|| NotifyLimiter {
                tokens: NOTIFY_BURST,
                last_refill: Instant::now(),
                last_text: String::new(),
                last_at: None,
            });
            notify_limiter_decide(state, Instant::now(), &key)
        };
        if let Err(reason) = decision {
            return Ok(serde_json::json!({ "ran": false, "reason": reason }));
        }
    }
    let (code, timed_out) = run_notify_hook_process(&path, &text)?;
    ledger_mark(
        "rust.notify_hook",
        Some(
            serde_json::json!({ "exit": code, "timed_out": timed_out, "payload_len": text.len() }),
        ),
    );
    Ok(serde_json::json!({ "ran": true, "exit": code, "timedOut": timed_out }))
}

#[cfg(test)]
mod notify_hook_tests {
    use super::*;
    use std::os::unix::fs::PermissionsExt;

    fn tmp_root(tag: &str) -> PathBuf {
        let d = std::env::temp_dir().join(format!("horosa-hook-{}-{}", tag, std::process::id()));
        let _ = fs::remove_dir_all(&d);
        fs::create_dir_all(&d).unwrap();
        fs::set_permissions(&d, fs::Permissions::from_mode(0o755)).unwrap();
        d
    }
    fn script(dir: &Path, name: &str, mode: u32) -> PathBuf {
        let p = dir.join(name);
        fs::write(&p, "#!/bin/sh\nexit 0\n").unwrap();
        fs::set_permissions(&p, fs::Permissions::from_mode(mode)).unwrap();
        p
    }

    #[test]
    fn notify_hook_path_six_gates() {
        let root = tmp_root("gates");
        let roots = vec![root.clone()];
        let ok = script(&root, "ok.sh", 0o755);
        assert!(validate_notify_hook_path_with_roots(ok.to_str().unwrap(), &roots).is_ok());
        // ① 相对路径
        assert_eq!(
            validate_notify_hook_path_with_roots("ok.sh", &roots).unwrap_err(),
            "必须是绝对路径"
        );
        // ② 不存在
        assert_eq!(
            validate_notify_hook_path_with_roots(root.join("nope.sh").to_str().unwrap(), &roots)
                .unwrap_err(),
            "文件不存在"
        );
        // ③ 目录
        assert!(
            validate_notify_hook_path_with_roots(root.to_str().unwrap(), &roots)
                .unwrap_err()
                .contains("常规文件")
        );
        // ④ 根之外
        let outside = tmp_root("outside");
        let o = script(&outside, "o.sh", 0o755);
        assert!(
            validate_notify_hook_path_with_roots(o.to_str().unwrap(), &roots)
                .unwrap_err()
                .contains("用户目录")
        );
        // ⑤ 不可执行
        let nx = script(&root, "nx.sh", 0o644);
        assert!(
            validate_notify_hook_path_with_roots(nx.to_str().unwrap(), &roots)
                .unwrap_err()
                .contains("不可执行")
        );
        // ⑥ 全员可写
        let ww = script(&root, "ww.sh", 0o777);
        assert!(
            validate_notify_hook_path_with_roots(ww.to_str().unwrap(), &roots)
                .unwrap_err()
                .contains("所有人可写")
        );
        // 文案不回显路径
        let e = validate_notify_hook_path_with_roots(o.to_str().unwrap(), &roots).unwrap_err();
        assert!(!e.contains("horosa-hook"));
        let _ = fs::remove_dir_all(&root);
        let _ = fs::remove_dir_all(&outside);
    }

    #[test]
    fn notify_hook_process_runs_with_single_json_arg_and_times_out() {
        let root = tmp_root("run");
        let out = root.join("seen.txt");
        let p = root.join("echo.sh");
        fs::write(
            &p,
            format!(
                "#!/bin/sh\nprintf '%s' \"$1\" > '{}'\nexit 3\n",
                out.display()
            ),
        )
        .unwrap();
        fs::set_permissions(&p, fs::Permissions::from_mode(0o755)).unwrap();
        let (code, timed_out) =
            run_notify_hook_process(&p, r#"{"title":"t","a b":"$(rm -rf /) ; x"}"#).unwrap();
        assert_eq!(code, Some(3));
        assert!(!timed_out);
        let seen = fs::read_to_string(&out).unwrap();
        assert_eq!(
            seen, r#"{"title":"t","a b":"$(rm -rf /) ; x"}"#,
            "载荷原样作为唯一参数,零 shell 展开"
        );
        let slow = root.join("slow.sh");
        fs::write(&slow, "#!/bin/sh\nsleep 30\n").unwrap();
        fs::set_permissions(&slow, fs::Permissions::from_mode(0o755)).unwrap();
        // kill 路径真跑:同一条 try_wait 循环,超时参数化到 300ms —— 到点 kill + wait,回 (None, true),且不等 sleep 30
        let t0 = Instant::now();
        let (code2, timed_out2) = run_notify_hook_process_with_timeout(&slow, "{}", 300).unwrap();
        assert_eq!(code2, None);
        assert!(timed_out2, "sleep 30 的脚本必须被到点 kill");
        assert!(
            t0.elapsed() < Duration::from_secs(5),
            "kill 路径不该等子进程自己退出: {:?}",
            t0.elapsed()
        );
        let _ = fs::remove_dir_all(&root);
        assert_eq!(NOTIFY_HOOK_TIMEOUT_MS, 10_000);
    }
}
