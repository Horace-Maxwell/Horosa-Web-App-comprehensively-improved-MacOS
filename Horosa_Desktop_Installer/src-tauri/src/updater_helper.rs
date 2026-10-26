//! 更新 helper 脚本、替换应用、搬到「应用程序」、交给新版与互换命令。

use super::*;

pub(crate) fn replace_app_bundle(source: &Path, target: &Path) -> Result<()> {
    if source == target {
        return Ok(());
    }
    let backup = target.with_extension("app.previous");
    let command = format!(
        "set -euo pipefail\nTARGET={target}\nSOURCE={source}\nBACKUP={backup}\nrm -rf \"${{BACKUP}}\"\nif [ -d \"${{TARGET}}\" ]; then mv \"${{TARGET}}\" \"${{BACKUP}}\"; fi\nif /usr/bin/ditto \"${{SOURCE}}\" \"${{TARGET}}\"; then\n  rm -rf \"${{BACKUP}}\"\n  /usr/bin/xattr -dr com.apple.quarantine \"${{TARGET}}\" >/dev/null 2>&1 || true\nelse\n  rm -rf \"${{TARGET}}\"\n  if [ -d \"${{BACKUP}}\" ]; then mv \"${{BACKUP}}\" \"${{TARGET}}\" || true; fi\n  exit 1\nfi\n",
        target = shell_quote(target),
        source = shell_quote(source),
        backup = shell_quote(&backup)
    );
    if target_requires_admin_update(target) {
        let status = Command::new("/usr/bin/osascript")
            .arg("-e")
            .arg(format!(
                "do shell script {} with administrator privileges",
                applescript_quote_text(&format!("/bin/bash -lc {}", shell_quote_text(&command)))
            ))
            .status()
            .context("replace installed app with admin")?;
        if !status.success() {
            return Err(anyhow!("app replace command exited with {}", status));
        }
    } else {
        let status = Command::new("/bin/bash")
            .arg("-lc")
            .arg(command)
            .status()
            .context("replace installed app")?;
        if !status.success() {
            return Err(anyhow!("app replace command exited with {}", status));
        }
    }
    Ok(())
}

pub(crate) fn current_app_version() -> Option<Version> {
    Version::parse(env!("CARGO_PKG_VERSION")).ok()
}

pub(crate) fn should_handoff_to_installed_app(
    current_bundle: &Path,
    target_bundle: &Path,
    current_version: Option<&Version>,
    target_version: Option<&Version>,
) -> bool {
    if current_bundle == target_bundle {
        return false;
    }
    match (current_version, target_version) {
        (_, None) => false,
        (Some(current), Some(target)) => target > current,
        (None, Some(_)) => true,
    }
}

pub(crate) fn app_version_from_bundle(path: &Path) -> Option<Version> {
    let plist = path.join("Contents/Info.plist");
    if !plist.exists() {
        return None;
    }
    let output = Command::new("/usr/bin/plutil")
        .arg("-extract")
        .arg("CFBundleShortVersionString")
        .arg("raw")
        .arg("-o")
        .arg("-")
        .arg(&plist)
        .output()
        .ok()?;
    if !output.status.success() {
        return None;
    }
    let value = String::from_utf8(output.stdout).ok()?;
    Version::parse(value.trim()).ok()
}

pub(crate) fn shell_quote(path: &Path) -> String {
    shell_quote_text(&path.to_string_lossy())
}

pub(crate) fn shell_quote_text(text: &str) -> String {
    format!("\"{}\"", text.replace('"', "\\\""))
}

pub(crate) fn applescript_quote_text(text: &str) -> String {
    format!("\"{}\"", text.replace('\\', "\\\\").replace('"', "\\\""))
}

/// 先读环境变量(非空才算),再问 `/usr/bin/id <flag>`,都拿不到用缺省值。
pub(crate) fn env_or_id(var: &str, id_flag: &str, fallback: &str) -> String {
    std::env::var(var)
        .ok()
        .filter(|value| !value.trim().is_empty())
        .unwrap_or_else(|| {
            Command::new("/usr/bin/id")
                .arg(id_flag)
                .output()
                .ok()
                .and_then(|output| String::from_utf8(output.stdout).ok())
                .map(|value| value.trim().to_string())
                .filter(|value| !value.is_empty())
                .unwrap_or_else(|| fallback.to_string())
        })
}

pub(crate) fn current_uid_string() -> String {
    env_or_id("UID", "-u", "0")
}

pub(crate) fn current_user_string() -> String {
    env_or_id("USER", "-un", "unknown")
}

fn update_helper_log_path(app: &AppHandle, extract_root: &Path) -> PathBuf {
    let logs_dir = app
        .path()
        .app_data_dir()
        .map(|path| path.join("logs"))
        .unwrap_or_else(|_| extract_root.to_path_buf());
    let _ = ensure_dir(&logs_dir);
    logs_dir.join("update-installer.log")
}

pub(crate) fn target_requires_admin_update(target_app: &Path) -> bool {
    #[cfg(target_os = "macos")]
    {
        target_app.starts_with(Path::new("/Applications"))
    }
    #[cfg(not(target_os = "macos"))]
    {
        let _ = target_app;
        false
    }
}

pub(crate) fn app_bundle_path() -> Option<PathBuf> {
    let exe = std::env::current_exe().ok()?;
    for ancestor in exe.ancestors() {
        if ancestor.extension().and_then(|s| s.to_str()) == Some("app") {
            return Some(ancestor.to_path_buf());
        }
    }
    None
}

// 把当前 .app 拷入 /Applications 固定安装位并重开(Translocation 只读挂载
// 点/桌面/下载目录直跑的用户,自更新链路找不到真实 App 路径——搬到固定位一劳永逸)。
// 成功即 exit(0) 交棒新副本;返回非空字符串=无需动作的说明文案。
pub(crate) fn relocate_app_to_applications(app: &AppHandle) -> Result<String> {
    // 返回的说明与错误都整段显示在原生对话框里(main.rs 菜单「移入应用程序」):文案经 shell_text 随界面简繁
    let bundle = app_bundle_path().with_context(|| shell_text("dlg.relocate.not_in_bundle"))?;
    let dest = installed_app_target_path();
    if bundle == dest {
        return Ok(shell_text("dlg.relocate.already"));
    }
    if dest.exists() {
        return Err(anyhow!(
            "{}",
            shell_text_fmt(
                "dlg.relocate.exists",
                &[("path", &dest.display().to_string())]
            )
        ));
    }
    let copied = Command::new("/usr/bin/ditto")
        .arg(&bundle)
        .arg(&dest)
        .stdout(Stdio::null())
        .stderr(Stdio::null())
        .status()
        .map(|s| s.success())
        .unwrap_or(false);
    if !copied {
        return Err(anyhow!("{}", shell_text("dlg.relocate.copy_failed")));
    }
    let _ = Command::new("/usr/bin/xattr")
        .arg("-dr")
        .arg("com.apple.quarantine")
        .arg(&dest)
        .stdout(Stdio::null())
        .stderr(Stdio::null())
        .status();
    Command::new("/usr/bin/open")
        .arg("-n")
        .arg(&dest)
        .spawn()
        .with_context(|| shell_text("dlg.relocate.open_failed"))?;
    app.exit(0);
    Ok(String::new())
}

pub(crate) fn handoff_to_newer_installed_app(app: &AppHandle) -> Result<bool> {
    let Some(current_bundle) = app_bundle_path() else {
        return Ok(false);
    };
    let target_bundle = installed_app_target_path();
    if !target_bundle.exists() {
        return Ok(false);
    }

    let current_version = app_version_from_bundle(&current_bundle).or_else(current_app_version);
    let target_version = app_version_from_bundle(&target_bundle);
    if !should_handoff_to_installed_app(
        &current_bundle,
        &target_bundle,
        current_version.as_ref(),
        target_version.as_ref(),
    ) {
        return Ok(false);
    }

    Command::new("open")
        .arg("-na")
        .arg(&target_bundle)
        .stdout(Stdio::null())
        .stderr(Stdio::null())
        .spawn()
        .with_context(|| format!("handoff to installed app {}", target_bundle.display()))?;
    app.exit(0);
    Ok(true)
}

// helper runtime 新协议开关:=0 时生成端回退旧模板(两段 mv,定义即执行)。
// 仅排障/对照用;发布环境勿设。
pub(crate) fn helper_runtime_swap_enabled() -> bool {
    std::env::var("HOROSA_HELPER_RUNTIME_SWAP")
        .map(|v| v != "0")
        .unwrap_or(true)
}

// 新协议:只生成**函数定义**(不立即执行),由模板底部 run_runtime_installs 在
// wait_for_old_app_exit 与 install_app 之后统一调用。手术本体 = TARGET 新二进制的
// --horosa-runtime-swap → extract_runtime_archive_with 同一协议(renamex 原子互换 +
// previous 保留到首次 ready + 版本闸 + 磁盘预检);失败 return 1(绝不 exit 杀 helper),
// 失败臂由模板层处理:重开新 app + exit 73,不写完成标记(铁律14)。
// 成功后整棵根 chown 归还发起更新的账户(admin 更新时 root 跑 helper,防 root-owned 锁死后续用户态更新);
// 共享根同样归还 —— 共享运行环境只给安装 / 更新它的账户写,其他账户只读(权限由 --horosa-runtime-swap 落树后收好)。
pub(crate) fn build_single_runtime_update_command(
    runtime_root: &Path,
    archive_path: &Path,
    runtime_version: Option<&str>,
    index: usize,
) -> String {
    format!(
        "install_runtime_{index}() {{\n  RUNTIME_ROOT={runtime_root}\n  if ! \"${{TARGET}}/Contents/MacOS/${{EXEC_NAME}}\" --horosa-runtime-swap \"${{RUNTIME_ROOT}}\" {archive} {runtime_version}; then\n    echo \"[runtime] swap failed for ${{RUNTIME_ROOT}}\"\n    return 1\n  fi\n  if [ -n \"${{USER_UID:-}}\" ]; then /usr/sbin/chown -R \"${{USER_UID}}\" \"${{RUNTIME_ROOT}}\" >/dev/null 2>&1 || true; fi\n  return 0\n}}\n",
        index = index,
        runtime_root = shell_quote(runtime_root),
        archive = shell_quote(archive_path),
        runtime_version = shell_quote_text(runtime_version.unwrap_or(""))
    )
}

// 旧协议原样保留(HOROSA_HELPER_RUNTIME_SWAP=0 的逃生阀)。已知病:两段 mv 非原子、
// 成功即删 previous(无回滚资本)、定义即执行(先于 wait_for_old_app_exit)、失败臂 exit 杀 helper。
// 仅作对照/排障,发布环境勿关新协议。
pub(crate) fn build_single_runtime_update_command_legacy(
    runtime_root: &Path,
    archive_path: &Path,
    runtime_version: Option<&str>,
    index: usize,
) -> String {
    format!(
        "install_runtime_{index}() {{\nRUNTIME_ROOT={runtime_root}\nWORK_ROOT=\"${{RUNTIME_ROOT}}/_update\"\nPREVIOUS_ROOT=\"${{RUNTIME_ROOT}}/previous\"\nEXPECTED_RUNTIME_VERSION={runtime_version}\nmkdir -p \"${{RUNTIME_ROOT}}\"\nrm -rf \"${{WORK_ROOT}}\"\nmkdir -p \"${{WORK_ROOT}}\"\nCOPYFILE_DISABLE=1 COPY_EXTENDED_ATTRIBUTES_DISABLE=1 /usr/bin/tar -xzf {archive} -C \"${{WORK_ROOT}}\"\nif [ ! -f \"${{WORK_ROOT}}/runtime-payload/runtime-manifest.json\" ]; then\n  echo \"runtime manifest missing after extract\" >&2\n  exit 1\nfi\nACTUAL_RUNTIME_VERSION=\"$(/usr/bin/plutil -extract version raw -o - \"${{WORK_ROOT}}/runtime-payload/runtime-manifest.json\" 2>/dev/null || true)\"\nif [ -n \"${{EXPECTED_RUNTIME_VERSION}}\" ] && [ \"${{ACTUAL_RUNTIME_VERSION}}\" != \"${{EXPECTED_RUNTIME_VERSION}}\" ]; then\n  echo \"runtime version mismatch: ${{ACTUAL_RUNTIME_VERSION}} != ${{EXPECTED_RUNTIME_VERSION}}\" >&2\n  exit 1\nfi\nrm -rf \"${{PREVIOUS_ROOT}}\"\nHAD_RUNTIME=0\nif [ -d \"${{RUNTIME_ROOT}}/current\" ]; then\n  mv \"${{RUNTIME_ROOT}}/current\" \"${{PREVIOUS_ROOT}}\"\n  HAD_RUNTIME=1\nfi\nif mv \"${{WORK_ROOT}}/runtime-payload\" \"${{RUNTIME_ROOT}}/current\"; then\n  rm -rf \"${{WORK_ROOT}}\" \"${{PREVIOUS_ROOT}}\"\n  /usr/bin/xattr -dr com.apple.quarantine \"${{RUNTIME_ROOT}}/current\" >/dev/null 2>&1 || true\n  if [ -n \"${{USER_UID:-}}\" ]; then /usr/sbin/chown -R \"${{USER_UID}}\" \"${{RUNTIME_ROOT}}\" >/dev/null 2>&1 || true; fi\n  case \"${{RUNTIME_ROOT}}\" in /Users/Shared/*) /bin/chmod -R u+rwX,go+rX,go-w \"${{RUNTIME_ROOT}}/current\" >/dev/null 2>&1 || true ;; esac\nelse\n  rm -rf \"${{RUNTIME_ROOT}}/current\"\n  if [ \"${{HAD_RUNTIME}}\" = \"1\" ] && [ -d \"${{PREVIOUS_ROOT}}\" ]; then\n    mv \"${{PREVIOUS_ROOT}}\" \"${{RUNTIME_ROOT}}/current\"\n  fi\n  exit 1\nfi\n}}\ninstall_runtime_{index}\n",
        index = index,
        runtime_root = shell_quote(runtime_root),
        archive = shell_quote(archive_path),
        runtime_version = shell_quote_text(runtime_version.unwrap_or(""))
    )
}

/// 更新助手收尾时把共享运行环境的权限收好(不论这次换没换运行环境):读 / 执行对所有账户放开、写只留属主。
/// 早先版本的安装包把整棵共享树留成 root 所有且所有账户可写 —— 应用装在「应用程序」里时助手以 root 身份跑,
/// 这时把仍归 root 的共享树交给发起更新的账户(已经归某个账户的不改属主);非 root 身份只能收自己名下的文件。
pub(crate) fn build_shared_runtime_seal_command(shared_root: &Path) -> String {
    format!(
        "seal_shared_runtime() {{\n  SHARED_SEAL_ROOT={root}\n  [ -d \"${{SHARED_SEAL_ROOT}}/runtime\" ] || return 0\n  if [ \"$(/usr/bin/id -u)\" = \"0\" ] && [ -n \"${{USER_UID:-}}\" ] && [ \"$(/usr/bin/stat -f%u \"${{SHARED_SEAL_ROOT}}/runtime\" 2>/dev/null || echo 0)\" = \"0\" ]; then\n    /usr/sbin/chown -R \"${{USER_UID}}\" \"${{SHARED_SEAL_ROOT}}\" >/dev/null 2>&1 || true\n  fi\n  /bin/chmod -R {mode} \"${{SHARED_SEAL_ROOT}}\" >/dev/null 2>&1 || true\n  return 0\n}}\n",
        root = shell_quote(shared_root),
        mode = SHARED_TREE_CHMOD,
    )
}

pub(crate) fn build_runtime_update_command(
    runtime_roots: &[PathBuf],
    archive_path: &Path,
    runtime_version: Option<&str>,
) -> String {
    if runtime_roots.is_empty() {
        return String::new();
    }
    if !helper_runtime_swap_enabled() {
        return runtime_roots
            .iter()
            .enumerate()
            .map(|(index, root)| {
                build_single_runtime_update_command_legacy(
                    root,
                    archive_path,
                    runtime_version,
                    index,
                )
            })
            .collect::<Vec<_>>()
            .join("\n");
    }
    let defs = runtime_roots
        .iter()
        .enumerate()
        .map(|(index, root)| {
            build_single_runtime_update_command(root, archive_path, runtime_version, index)
        })
        .collect::<Vec<_>>()
        .join("\n");
    let calls = (0..runtime_roots.len())
        .map(|index| format!("  install_runtime_{index} || return 1"))
        .collect::<Vec<_>>()
        .join("\n");
    format!("{defs}\nrun_runtime_installs() {{\n{calls}\n  return 0\n}}\n")
}

pub(crate) fn build_update_helper_script(
    update_log: &Path,
    completion_marker: &Path,
    target_app: &Path,
    app_src: &Path,
    current_uid: &str,
    current_user: &str,
    current_pid: &str,
    executable_name: &str,
    target_version: &str,
    runtime_version: Option<&str>,
    runtime_cmd: &str,
) -> String {
    format!(
        "#!/bin/bash\nset -euo pipefail\nLOG={log}\nMARKER={marker}\nTARGET={target}\nSRC={src}\nUSER_UID={user_uid}\nUSER_NAME={user_name}\nOLD_PID={old_pid}\nEXEC_NAME={exec_name}\nEXPECTED_VERSION={target_version}\nEXPECTED_RUNTIME_VERSION={runtime_version}\nAPP_DISPLAY_NAME=\"$(/usr/bin/basename \"${{TARGET}}\" .app)\"\nmkdir -p \"$(dirname \"${{LOG}}\")\"\nmkdir -p \"$(dirname \"${{MARKER}}\")\"\nexec >> \"${{LOG}}\" 2>&1\necho \"===== update helper start $(date '+%Y-%m-%d %H:%M:%S') =====\"\necho \"uid=$(/usr/bin/id -u) user=$(/usr/bin/id -un)\"\necho \"target=${{TARGET}}\"\necho \"src=${{SRC}}\"\nwait_for_old_app_exit() {{\n  if [ -z \"${{OLD_PID}}\" ] || [ \"${{OLD_PID}}\" = \"0\" ]; then\n    return 0\n  fi\n  for attempt in $(/usr/bin/seq 1 60); do\n    if ! /bin/kill -0 \"${{OLD_PID}}\" >/dev/null 2>&1; then\n      echo \"[app] old process exited\"\n      return 0\n    fi\n    sleep 1\n  done\n  echo \"[app] old process still running after wait window\"\n  return 0\n}}\nrun_runtime_installs() {{\n  return 0\n}}\nseal_shared_runtime() {{\n  return 0\n}}\n{runtime_cmd}mark_update_complete() {{\n  local relaunch_status=\"${{1:-pending_manual}}\"\n  MARKER_DIR=\"$(dirname \"${{MARKER}}\")\"\n  /bin/mkdir -p \"${{MARKER_DIR}}\"\n  /usr/sbin/chown \"${{USER_UID}}\" \"${{MARKER_DIR}}\" >/dev/null 2>&1 || true\n  /bin/cat > \"${{MARKER}}\" <<EOF\nversion=${{EXPECTED_VERSION}}\nruntime_version=${{EXPECTED_RUNTIME_VERSION}}\ninstalled_at=$(/bin/date '+%Y-%m-%d %H:%M:%S')\nrelaunch_status=${{relaunch_status}}\nEOF\n  /usr/sbin/chown \"${{USER_UID}}\" \"${{MARKER}}\" >/dev/null 2>&1 || true\n}}\nis_target_running() {{\n  if [ -z \"${{EXEC_NAME}}\" ]; then\n    return 1\n  fi\n  /usr/bin/pgrep -f \"${{TARGET}}/Contents/MacOS/${{EXEC_NAME}}\" >/dev/null 2>&1\n}}\nwait_for_stable_relaunch() {{\n  local appeared=0\n  for wait_step in $(/usr/bin/seq 1 25); do\n    if is_target_running; then\n      appeared=1\n      break\n    fi\n    sleep 1\n  done\n  if [ \"${{appeared}}\" != \"1\" ]; then\n    echo \"[open] process never appeared\"\n    return 1\n  fi\n  for stable_step in $(/usr/bin/seq 1 10); do\n    if ! is_target_running; then\n      echo \"[open] process exited before becoming stable\"\n      return 1\n    fi\n    sleep 1\n  done\n  return 0\n}}\nactivate_app_once() {{\n  if [ -z \"${{APP_DISPLAY_NAME}}\" ]; then\n    return 0\n  fi\n  if [ \"$(/usr/bin/id -u)\" = \"${{USER_UID}}\" ]; then\n    /usr/bin/osascript -e \"tell application \\\"${{APP_DISPLAY_NAME}}\\\" to activate\" >/dev/null 2>&1 || true\n    return 0\n  fi\n  /bin/launchctl asuser \"${{USER_UID}}\" /usr/bin/osascript -e \"tell application \\\"${{APP_DISPLAY_NAME}}\\\" to activate\" >/dev/null 2>&1 || true\n}}\nopen_app_once() {{\n  if [ \"$(/usr/bin/id -u)\" = \"${{USER_UID}}\" ]; then\n    /usr/bin/open -n \"${{TARGET}}\"\n    activate_app_once\n    return 0\n  fi\n  if /bin/launchctl asuser \"${{USER_UID}}\" /usr/bin/open -n \"${{TARGET}}\"; then\n    activate_app_once\n    return 0\n  fi\n  if /usr/bin/sudo -u \"${{USER_NAME}}\" /usr/bin/open -n \"${{TARGET}}\"; then\n    activate_app_once\n    return 0\n  fi\n  /usr/bin/open -n \"${{TARGET}}\"\n  activate_app_once\n}}\nopen_app() {{\n  for attempt in $(/usr/bin/seq 1 8); do\n    echo \"[open] attempt ${{attempt}}\"\n    open_app_once || true\n    if wait_for_stable_relaunch; then\n      activate_app_once\n      echo \"[open] relaunch confirmed\"\n      mark_update_complete \"auto_relaunch_confirmed\"\n      return 0\n    fi\n    sleep 2\n  done\n  echo \"[open] relaunch not confirmed after retries\"\n  return 1\n}}\ninstall_app() {{\n  BACKUP_TARGET=\"${{TARGET}}.previous\"\n  STAGE_TARGET=\"${{TARGET%.app}}.update-stage.app\"\n  SRC_KB=\"$(/usr/bin/du -sk \"${{SRC}}\" 2>/dev/null | /usr/bin/awk '{{print $1}}')\"\n  AVAIL_KB=\"$(/bin/df -k \"$(dirname \"${{TARGET}}\")\" 2>/dev/null | /usr/bin/awk 'NR==2 {{print $4}}')\"\n  if [ -n \"${{SRC_KB}}\" ] && [ -n \"${{AVAIL_KB}}\" ] && [ \"${{AVAIL_KB}}\" -lt $((SRC_KB * 2)) ]; then\n    echo \"[app] insufficient disk space: need ~$((SRC_KB * 2))KB, avail ${{AVAIL_KB}}KB\"\n    return 1\n  fi\n  rm -rf \"${{STAGE_TARGET}}\"\n  for attempt in $(/usr/bin/seq 1 45); do\n    echo \"[app] attempt ${{attempt}}\"\n    if [ ! -d \"${{STAGE_TARGET}}\" ]; then\n      if ! /usr/bin/ditto \"${{SRC}}\" \"${{STAGE_TARGET}}\"; then\n        echo \"[app] stage ditto failed on attempt ${{attempt}}\"\n        rm -rf \"${{STAGE_TARGET}}\"\n        sleep 1\n        continue\n      fi\n      /usr/bin/xattr -dr com.apple.quarantine \"${{STAGE_TARGET}}\" >/dev/null 2>&1 || true\n    fi\n    if [ -d \"${{TARGET}}\" ]; then\n      if \"${{STAGE_TARGET}}/Contents/MacOS/${{EXEC_NAME}}\" --horosa-atomic-swap \"${{STAGE_TARGET}}\" \"${{TARGET}}\" >/dev/null 2>&1; then\n        echo \"[app] atomic swap succeeded\"\n        rm -rf \"${{BACKUP_TARGET}}\"\n        mv \"${{STAGE_TARGET}}\" \"${{BACKUP_TARGET}}\" 2>/dev/null || rm -rf \"${{STAGE_TARGET}}\"\n        return 0\n      fi\n      echo \"[app] atomic swap unavailable, fallback to mv pair\"\n      rm -rf \"${{BACKUP_TARGET}}\"\n      if ! mv \"${{TARGET}}\" \"${{BACKUP_TARGET}}\"; then\n        echo \"[app] mv failed on attempt ${{attempt}}\"\n        /bin/ls -ld \"${{TARGET}}\" >/dev/null 2>&1 && /bin/ls -ld \"${{TARGET}}\"\n        sleep 1\n        continue\n      fi\n      if mv \"${{STAGE_TARGET}}\" \"${{TARGET}}\"; then\n        rm -rf \"${{BACKUP_TARGET}}\"\n        echo \"[app] install succeeded (mv fallback)\"\n        return 0\n      fi\n      echo \"[app] stage mv failed; restoring previous\"\n      if [ -d \"${{BACKUP_TARGET}}\" ]; then\n        mv \"${{BACKUP_TARGET}}\" \"${{TARGET}}\" || true\n      fi\n      sleep 1\n      continue\n    fi\n    if mv \"${{STAGE_TARGET}}\" \"${{TARGET}}\"; then\n      echo \"[app] install succeeded (fresh)\"\n      return 0\n    fi\n    echo \"[app] fresh mv failed on attempt ${{attempt}}\"\n    sleep 1\n  done\n  echo \"[app] install failed after retries\"\n  rm -rf \"${{STAGE_TARGET}}\"\n  return 1\n}}\nwait_for_old_app_exit\nif ! install_app; then\n  echo \"[app] install failed; reopening previous app\"\n  for reopen_attempt in $(/usr/bin/seq 1 3); do\n    open_app_once || true\n    if wait_for_stable_relaunch; then\n      echo \"[open] previous app reopened\"\n      break\n    fi\n  done\n  exit 71\nfi\nsleep 1\nif ! run_runtime_installs; then\n  echo \"[runtime] runtime install failed; reopening app without completion marker\"\n  for reopen_attempt in $(/usr/bin/seq 1 3); do\n    open_app_once || true\n    if wait_for_stable_relaunch; then\n      echo \"[open] app reopened after runtime failure\"\n      break\n    fi\n  done\n  exit 73\nfi\nseal_shared_runtime || true\nmark_update_complete \"pending_manual\"\nif ! open_app; then\n  echo \"[open] automatic relaunch could not be confirmed; waiting for manual reopen\"\n  exit 72\nfi\necho \"===== update helper success $(date '+%Y-%m-%d %H:%M:%S') =====\"\n",
        log = shell_quote(update_log),
        marker = shell_quote(completion_marker),
        runtime_cmd = runtime_cmd,
        target = shell_quote(target_app),
        src = shell_quote(app_src),
        user_uid = shell_quote_text(current_uid),
        user_name = shell_quote_text(current_user),
        old_pid = shell_quote_text(current_pid),
        exec_name = shell_quote_text(executable_name),
        target_version = shell_quote_text(target_version),
        runtime_version = shell_quote_text(runtime_version.unwrap_or(""))
    )
}

pub(crate) fn install_downloaded_app(
    app: AppHandle,
    zip_path: &Path,
    runtime_archive: Option<&Path>,
    runtime_roots: &[PathBuf],
    runtime_version: Option<&str>,
    target_version: &str,
) -> Result<()> {
    let extract_root = tmp_download_path(APP_NAME, "app-update");
    ensure_dir(&extract_root)?;
    let file = File::open(zip_path)?;
    let mut archive = ZipArchive::new(file)?;
    archive.extract(&extract_root)?;

    let mut app_src = None;
    for entry in fs::read_dir(&extract_root)? {
        let entry = entry?;
        let path = entry.path();
        if path.extension().and_then(|s| s.to_str()) == Some("app") {
            app_src = Some(path);
            break;
        }
    }
    let app_src = app_src.context("updated app bundle not found in zip")?;
    let target_app = app_bundle_path().context("current app bundle path not found")?;
    let update_log = update_helper_log_path(&app, &extract_root);
    let completion_marker = update_complete_marker_path(&app)?;
    let helper = extract_root.join("install_update.sh");
    let current_uid = current_uid_string();
    let current_user = current_user_string();
    let current_pid = std::process::id().to_string();
    let executable_name = std::env::current_exe()
        .ok()
        .and_then(|path| {
            path.file_name()
                .map(|name| name.to_string_lossy().to_string())
        })
        .unwrap_or_else(|| "horosa-desktop-installer".to_string());
    let requires_admin = target_requires_admin_update(&target_app);
    let runtime_cmd = if let Some(archive_path) = runtime_archive {
        build_runtime_update_command(runtime_roots, archive_path, runtime_version)
    } else {
        String::new()
    } + &build_shared_runtime_seal_command(&shared_assets_root());
    let script = build_update_helper_script(
        &update_log,
        &completion_marker,
        &target_app,
        &app_src,
        &current_uid,
        &current_user,
        &current_pid,
        &executable_name,
        target_version,
        runtime_version,
        &runtime_cmd,
    );
    fs::write(&helper, script)?;
    #[cfg(unix)]
    {
        use std::os::unix::fs::PermissionsExt;
        let mut perms = fs::metadata(&helper)?.permissions();
        perms.set_mode(0o755);
        fs::set_permissions(&helper, perms)?;
    }
    if requires_admin {
        let command = format!("/bin/bash {}", shell_quote(&helper));
        Command::new("/usr/bin/osascript")
            .arg("-e")
            .arg(format!(
                "do shell script {} with administrator privileges",
                applescript_quote_text(&command)
            ))
            .stdout(Stdio::null())
            .stderr(Stdio::null())
            .spawn()?;
    } else {
        Command::new("/bin/bash")
            .arg(&helper)
            .stdout(Stdio::null())
            .stderr(Stdio::null())
            .spawn()?;
    }
    app.exit(0);
    Ok(())
}

// swap CLI 本体(纯函数可测):0=互换成功;2=不可用/入参不齐(调用方走 mv 回退);
// 1=真实错误(同样回退)。helper 借主二进制做 renamex_np——不新增 Mach-O 进签名面。
pub(crate) fn run_swap_cli(a: &Path, b: &Path) -> i32 {
    if !a.exists() || !b.exists() {
        eprintln!(
            "[swap-cli] 两侧路径必须都存在: {} / {}",
            a.display(),
            b.display()
        );
        return 2;
    }
    match atomic_swap_dirs(a, b) {
        Ok(true) => 0,
        Ok(false) => 2,
        Err(err) => {
            eprintln!("[swap-cli] {err:#}");
            1
        }
    }
}

// 隐藏 CLI:update helper 借「新版 app 自己的二进制」做全量 runtime 对换——
// 与进程内 extract_runtime_archive_with 完全同一协议(磁盘预检 + _extract 暂存 +
// 版本闸 + renamex 原子互换 + previous 保留到首次 ready)。stdout/stderr 由 helper
// 的 exec >> LOG 收进 update.log。exit: 0=成功 / 1=手术失败(current 未动或已回滚,
// 半成品已清或留给撕裂探测) / 2=入参不可用。
pub(crate) fn run_runtime_swap_cli(root: &Path, archive: &Path, expected_version: &str) -> i32 {
    if !archive.is_file() {
        eprintln!("[runtime-swap] archive 不存在: {}", archive.display());
        return 2;
    }
    if let Err(err) = ensure_dir(root) {
        eprintln!(
            "[runtime-swap] runtime 根不可用 {}: {err:#}",
            root.display()
        );
        return 2;
    }
    let expected = expected_version.trim();
    let expected = if expected.is_empty() {
        None
    } else {
        Some(expected)
    };
    match extract_runtime_archive_with(archive, root, None, expected) {
        Ok(()) => {
            let _ = clear_runtime_pending_marker(&root.join("current"));
            let say_swap = |msg: &str| println!("[runtime-swap] {}", msg);
            native_prewarm_after_runtime_update(&root.join("current"), &say_swap, "runtime-swap");
            println!("[runtime-swap] promoted new runtime at {}", root.display());
            0
        }
        Err(err) => {
            eprintln!("[runtime-swap] {err:#}");
            1
        }
    }
}
