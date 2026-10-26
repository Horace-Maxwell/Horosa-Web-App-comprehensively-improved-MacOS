//! 诊断:脱敏、诊断快照、诊断包导出、旧版日志收集。

use super::*;

#[derive(Debug, Clone, Serialize)]
#[serde(rename_all = "camelCase")]
pub(crate) struct DiagnosticsPayload {
    log_path: String,
    pub(crate) app_data_dir: String,
    pub(crate) runtime_dir: String,
    pub(crate) lines: Vec<String>,
    pub(crate) assets: Vec<AssetInventoryItem>,
    updated_at: u64,
    // 启动账本(本次 run 的分段耗时 JSONL 尾部,四层聚合;无账本时为空)
    #[serde(default)]
    ledger_lines: Vec<String>,
    // 耐久更新台账尾部(vX→vY 结果历史;无台账时为空)
    #[serde(default)]
    update_history_lines: Vec<String>,
    /// 共享运行环境权限提示(早先安装包留下所有账户可写的旧树;None = 没问题)
    shared_runtime_warning: Option<String>,
}

/// 诊断包脱敏:日志/账本/更新历史尾部里任何形如 `sk-…`(≥8 位)、`Bearer <token>`、`api_key=<value>` 的片段掩成 `***`。
/// 诊断 zip 是用户外发的最高后果泄漏通道;此前收集器零脱敏。手写扫描器(不引 regex crate)。
pub(crate) fn redact_secrets(input: &str) -> String {
    fn is_tok(c: char) -> bool {
        c.is_ascii_alphanumeric()
            || c == '_'
            || c == '-'
            || c == '.'
            || c == '+'
            || c == '/'
            || c == '='
    }
    let chars: Vec<char> = input.chars().collect();
    let lower: Vec<char> = input.to_lowercase().chars().collect();
    let n = chars.len();
    let mut out = String::with_capacity(n);
    let mut i = 0usize;
    let starts_with = |pos: usize, pat: &str| -> bool {
        let p: Vec<char> = pat.chars().collect();
        pos + p.len() <= n && lower[pos..pos + p.len()] == p[..]
    };
    while i < n {
        // sk-XXXXXXXX…(≥8 位密钥体)
        if starts_with(i, "sk-") {
            let mut j = i + 3;
            while j < n && is_tok(chars[j]) {
                j += 1;
            }
            if j - (i + 3) >= 8 {
                out.push_str("sk-***");
                i = j;
                continue;
            }
        }
        // Bearer <token>
        if starts_with(i, "bearer ") {
            out.extend(chars[i..i + 7].iter());
            let mut j = i + 7;
            while j < n && chars[j] == ' ' {
                j += 1;
            }
            let start = j;
            while j < n && is_tok(chars[j]) {
                j += 1;
            }
            if j > start {
                out.push_str("***");
                i = j;
                continue;
            }
            i = start;
            continue;
        }
        // api_key / apikey / api-key 后接 = : 引号 空格 再接值
        let key_hit = ["api_key", "apikey", "api-key"]
            .iter()
            .find(|k| starts_with(i, k))
            .map(|k| k.len());
        if let Some(klen) = key_hit {
            out.extend(chars[i..i + klen].iter());
            let mut j = i + klen;
            while j < n
                && (chars[j] == ' '
                    || chars[j] == '='
                    || chars[j] == ':'
                    || chars[j] == '"'
                    || chars[j] == '\'')
            {
                out.push(chars[j]);
                j += 1;
            }
            let start = j;
            while j < n && is_tok(chars[j]) {
                j += 1;
            }
            if j - start >= 6 {
                out.push_str("***");
                i = j;
                continue;
            }
            i = start;
            continue;
        }
        out.push(chars[i]);
        i += 1;
    }
    out
}

pub(crate) fn redact_lines(lines: Vec<String>) -> Vec<String> {
    lines.into_iter().map(|l| redact_secrets(&l)).collect()
}

fn collect_diagnostics_payload(app: &AppHandle) -> Result<DiagnosticsPayload> {
    let paths = resolve_runtime_paths(app)?;
    ensure_dir(&paths.logs_dir)?;
    let mut latest_log = None;
    let mut latest_mtime = UNIX_EPOCH;
    for entry in fs::read_dir(&paths.logs_dir)? {
        let entry = entry?;
        let path = entry.path();
        if path.extension().and_then(|value| value.to_str()) != Some("log") {
            continue;
        }
        let modified = entry
            .metadata()
            .and_then(|meta| meta.modified())
            .unwrap_or(UNIX_EPOCH);
        if modified >= latest_mtime {
            latest_mtime = modified;
            latest_log = Some(path);
        }
    }
    let log_path = latest_log.unwrap_or_else(|| paths.logs_dir.join("update-installer.log"));
    let lines = fs::read_to_string(&log_path)
        .unwrap_or_else(|_| "暂无日志，应用会在首次启动和更新时逐步写入这里。".to_string())
        .lines()
        .map(|line| line.to_string())
        .collect::<Vec<_>>();
    let lines = if lines.len() > 200 {
        lines[lines.len() - 200..].to_vec()
    } else {
        lines
    };
    // 启动账本尾部(本次 run 优先;未初始化时回落 logs 下最新的账本文件)
    let ledger_path = ledger_env().map(|(_, file)| file).or_else(|| {
        let mut newest: Option<(SystemTime, PathBuf)> = None;
        if let Ok(entries) = fs::read_dir(&paths.logs_dir) {
            for entry in entries.flatten() {
                let candidate = entry.path().join("horosa-startup-ledger.jsonl");
                if let Ok(meta) = fs::metadata(&candidate) {
                    let modified = meta.modified().unwrap_or(UNIX_EPOCH);
                    if newest.as_ref().map(|(t, _)| modified > *t).unwrap_or(true) {
                        newest = Some((modified, candidate));
                    }
                }
            }
        }
        newest.map(|(_, p)| p)
    });
    let ledger_lines = ledger_path
        .and_then(|p| fs::read_to_string(p).ok())
        .map(|text| {
            let all: Vec<String> = text.lines().map(|l| l.to_string()).collect();
            if all.len() > 100 {
                all[all.len() - 100..].to_vec()
            } else {
                all
            }
        })
        .unwrap_or_default();
    // 耐久更新台账尾 50 行
    let update_history_lines = update_history_path(app)
        .and_then(|p| fs::read_to_string(p).ok())
        .map(|text| {
            let all: Vec<String> = text.lines().map(|l| l.to_string()).collect();
            if all.len() > 50 {
                all[all.len() - 50..].to_vec()
            } else {
                all
            }
        })
        .unwrap_or_default();
    let lines = redact_lines(lines);
    let ledger_lines = redact_lines(ledger_lines);
    let update_history_lines = redact_lines(update_history_lines);
    Ok(DiagnosticsPayload {
        log_path: log_path.to_string_lossy().to_string(),
        app_data_dir: paths.app_data_dir.to_string_lossy().to_string(),
        runtime_dir: paths.runtime_dir.to_string_lossy().to_string(),
        lines,
        assets: build_asset_review_payload(
            app,
            AssetReviewMode::Install,
            current_app_version(),
            local_runtime_version(app),
        )?
        .items,
        updated_at: unix_ts(),
        ledger_lines,
        update_history_lines,
        shared_runtime_warning: inspect_shared_tree().warning().0,
    })
}

// 用 ditto 打 zip(全仓 Command 惯例;比 zip crate 写侧对 xattr/资源叉更稳)
pub(crate) fn zip_dir_with_ditto(src: &Path, out: &Path) -> Result<()> {
    let status = Command::new("/usr/bin/ditto")
        .arg("-c")
        .arg("-k")
        .arg("--sequesterRsrc")
        .arg(src)
        .arg(out)
        .stdout(Stdio::null())
        .stderr(Stdio::null())
        .status()
        .context("spawn ditto")?;
    if !status.success() {
        return Err(anyhow!("ditto 打包失败: {}", out.display()));
    }
    Ok(())
}

// 一键导出诊断包:logs 全目录(既有留存策略控体积)+关键状态文件+系统信息
// → ~/Desktop/<app>-诊断-<ts>.zip(桌面缺失退回数据目录),并 Finder 定位。
// 非技术用户排障从「教对方翻目录」变成「发一个 zip」。
// 诊断包 Java 日志选取器(纯函数可测):按 mtime 降序拣最新文件,总量 ≤ cap;
// 超预算的大文件跳过继续拣小的(宁可多收几份小日志,不为一份巨型日志放弃其余)。
pub(crate) fn select_recent_files_by_mtime(root: &Path, cap_bytes: u64) -> Vec<PathBuf> {
    let mut files: Vec<(SystemTime, u64, PathBuf)> = WalkDir::new(root)
        .into_iter()
        .flatten()
        .filter(|e| e.file_type().is_file())
        .filter_map(|e| {
            let md = e.metadata().ok()?;
            Some((md.modified().ok()?, md.len(), e.into_path()))
        })
        .collect();
    files.sort_by(|a, b| b.0.cmp(&a.0));
    let mut total = 0u64;
    let mut out = Vec::new();
    for (_, len, path) in files {
        if total.saturating_add(len) > cap_bytes {
            continue;
        }
        total += len;
        out.push(path);
    }
    out
}

// 旧运行时兜底:修复前的 Java 日志器拿 log4j2 basedir 的原样串拼路径,活文件落到
// 「相对进程 CWD 的字面目录」,目录名就是这两个原样串;CWD 视启动路径为 Horosa-Web /
// boot-exploded / bundle。用户机若仍跑旧包,诊断包得把这些目录也收进来,否则活日志全缺。
const LEGACY_JAVA_LOG_LITERALS: [&str; 2] = ["${env:HOME:-${sys:user.home}}", "${env:HOME}"];
const LEGACY_JAVA_LOG_CWD_SUBDIRS: [&str; 3] = [
    "Horosa-Web",
    "runtime/mac/bundle/boot-exploded",
    "runtime/mac/bundle",
];

/// 旧运行时字面目录里的 Java 日志根(存在的才算;跨 runtime 根去重,保持扫描顺序)。
fn legacy_java_log_roots(runtime_dirs: &[PathBuf]) -> Vec<PathBuf> {
    let mut out: Vec<PathBuf> = Vec::new();
    for base in runtime_dirs {
        for sub in LEGACY_JAVA_LOG_CWD_SUBDIRS {
            for lit in LEGACY_JAVA_LOG_LITERALS {
                let root = base
                    .join(sub)
                    .join(lit)
                    .join(".horosa-logs")
                    .join("astrostudyboot");
                if root.is_dir() && !out.contains(&root) {
                    out.push(root);
                }
            }
        }
    }
    out
}

/// 把旧运行时字面目录里的 Java 日志收进 staging/java-logs-legacy/<序号>/(每个根按 mtime 取最新
/// ≤ cap,保持相对目录),并写 legacy-roots.txt 记录序号→来源目录;无命中返回 None 且不建目录。
pub(crate) fn export_legacy_java_logs(
    runtime_dirs: &[PathBuf],
    staging: &Path,
    cap_bytes: u64,
) -> Option<PathBuf> {
    let roots = legacy_java_log_roots(runtime_dirs);
    if roots.is_empty() {
        return None;
    }
    let dest_root = staging.join("java-logs-legacy");
    let mut index = String::new();
    for (idx, root) in roots.iter().enumerate() {
        let bucket = dest_root.join((idx + 1).to_string());
        index.push_str(&format!("{}\t{}\n", idx + 1, root.display()));
        for src in select_recent_files_by_mtime(root, cap_bytes) {
            if let Ok(rel) = src.strip_prefix(root) {
                let dest = bucket.join(rel);
                if let Some(parent) = dest.parent() {
                    let _ = fs::create_dir_all(parent);
                }
                let _ = fs::copy(&src, &dest);
            }
        }
    }
    let _ = fs::create_dir_all(&dest_root);
    let _ = fs::write(dest_root.join("legacy-roots.txt"), index);
    Some(dest_root)
}

#[tauri::command]
pub(crate) fn export_diagnostics_bundle(app: AppHandle) -> std::result::Result<String, String> {
    (|| -> Result<String> {
        let data_dir = app.path().app_data_dir().context("app data dir")?;
        let staging = tmp_download_path(APP_NAME, "diag-bundle");
        ensure_dir(&staging)?;
        let logs_src = data_dir.join("logs");
        if logs_src.exists() {
            clone_dir_fast(&logs_src, &staging.join("logs"))?;
        }
        for name in [
            "launch-health.json",
            "staged-update.json",
            "last-update-check.json",
        ] {
            let src = data_dir.join(name);
            if src.exists() {
                let _ = fs::copy(&src, staging.join(name));
            }
        }
        let manifest = shared_runtime_dir().join("runtime-manifest.json");
        if manifest.exists() {
            let _ = fs::copy(&manifest, staging.join("runtime-manifest.json"));
        }
        // Java 结构化日志:log4j2 落 ~/.horosa-logs/astrostudyboot(yyyy/MM/dd 滚动),
        // 不在 app_data/logs 内 —— 此前诊断包只有重定向 stdout 的 JAVA_LOG,spring/sql
        // 滚动日志全缺。按 mtime 取最新 ≤20MB 保持相对目录进 java-logs/。
        if let Ok(home_dir) = std::env::var("HOME").map(PathBuf::from) {
            let java_logs_root = home_dir.join(".horosa-logs").join("astrostudyboot");
            if java_logs_root.exists() {
                let picked = select_recent_files_by_mtime(&java_logs_root, 20 * 1024 * 1024);
                for src in picked {
                    if let Ok(rel) = src.strip_prefix(&java_logs_root) {
                        let dest = staging.join("java-logs").join(rel);
                        if let Some(parent) = dest.parent() {
                            let _ = fs::create_dir_all(parent);
                        }
                        let _ = fs::copy(&src, &dest);
                    }
                }
            }
        }
        // 旧运行时字面目录兜底(见 export_legacy_java_logs):共享/用户两处 runtime 根都扫。
        let mut legacy_bases: Vec<PathBuf> = vec![shared_runtime_dir()];
        if let Ok(user_dir) = user_runtime_dir(&app) {
            if !legacy_bases.contains(&user_dir) {
                legacy_bases.push(user_dir);
            }
        }
        let _ = export_legacy_java_logs(&legacy_bases, &staging, 10 * 1024 * 1024);
        let sw = Command::new("/usr/bin/sw_vers")
            .output()
            .map(|o| String::from_utf8_lossy(&o.stdout).to_string())
            .unwrap_or_default();
        let info = format!(
            "app={}\nshellVersion={}\nlocalRuntime={}\n{}",
            APP_NAME,
            env!("CARGO_PKG_VERSION"),
            local_runtime_version(&app).unwrap_or_default(),
            sw
        );
        fs::write(staging.join("system-info.txt"), info)?;
        let ts = SystemTime::now()
            .duration_since(UNIX_EPOCH)
            .map(|d| d.as_secs())
            .unwrap_or(0);
        let home = std::env::var("HOME")
            .map(PathBuf::from)
            .unwrap_or_else(|_| data_dir.clone());
        let desktop = home.join("Desktop");
        let out_dir = if desktop.exists() { desktop } else { data_dir };
        let out = out_dir.join(format!("{}-诊断-{}.zip", APP_NAME, ts));
        zip_dir_with_ditto(&staging, &out)?;
        let _ = remove_dir_if_exists(&staging);
        let _ = Command::new("/usr/bin/open")
            .arg("-R")
            .arg(&out)
            .stdout(Stdio::null())
            .stderr(Stdio::null())
            .status();
        Ok(out.display().to_string())
    })()
    .map_err(|e| format!("{e:#}"))
}

#[tauri::command]
pub(crate) fn read_diagnostics_snapshot(
    app: AppHandle,
) -> std::result::Result<DiagnosticsPayload, String> {
    collect_diagnostics_payload(&app).map_err(|err| format!("{err:#}"))
}
