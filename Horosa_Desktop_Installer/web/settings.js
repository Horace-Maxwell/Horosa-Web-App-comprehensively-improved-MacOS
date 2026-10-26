(function () {
  const controls = {
    autoCheckUpdates: document.getElementById('autoCheckUpdates'),
    showStatusNotifications: document.getElementById('showStatusNotifications'),
    compactLauncherLayout: document.getElementById('compactLauncherLayout'),
    enableExperimentalFeatures: document.getElementById('enableExperimentalFeatures'),
    alwaysReviewBeforeReplace: document.getElementById('alwaysReviewBeforeReplace')
  };
  const runtimeVersion = document.getElementById('runtimeVersion');
  const appDataDir = document.getElementById('appDataDir');
  const sharedWarn = document.getElementById('sharedRuntimeWarning');
  const sealSharedBtn = document.getElementById('sealSharedBtn');
  const logsDir = document.getElementById('logsDir');
  const appVersion = document.getElementById('appVersion');
  const supportedArch = document.getElementById('supportedArch');
  const statusToast = document.getElementById('statusToast');
  const saveBtn = document.getElementById('saveBtn');

  // 壳层报错 → 一句看得懂的中文(shell_errors.js,页面先于本文件载入)
  function errorText(error) {
    return window.HorosaShellErrors.plain(error);
  }

  const invoke = window.HorosaShellBridge.invoke;

  function showToast(message) {
    statusToast.textContent = message;
    statusToast.classList.remove('hidden');
    clearTimeout(showToast._timer);
    showToast._timer = setTimeout(() => statusToast.classList.add('hidden'), 1800);
  }

  async function loadPayload() {
    const payload = await invoke('load_preferences_payload');
    controls.autoCheckUpdates.checked = Boolean(payload.preferences.autoCheckUpdates);
    controls.showStatusNotifications.checked = Boolean(payload.preferences.showStatusNotifications);
    controls.compactLauncherLayout.checked = Boolean(payload.preferences.compactLauncherLayout);
    controls.enableExperimentalFeatures.checked = Boolean(
      payload.preferences.enableExperimentalFeatures
    );
    controls.alwaysReviewBeforeReplace.checked = Boolean(
      payload.preferences.alwaysReviewBeforeReplace
    );
    runtimeVersion.textContent = payload.runtimeVersion || '尚未检测到';
    // 共享运行环境权限:早先安装包留下所有账户可写的旧树 → 一行提示(不弹窗)。别的账户名下的要用完整安装包更新一次;
    // 归本账户的给「收紧共享权限」按钮 —— 读本页不改任何权限,用户点了才在后台收紧
    showSharedWarning(payload);
    appDataDir.textContent = payload.appDataDir;
    logsDir.textContent = payload.logsDir;
    appVersion.textContent = `星阙 ${payload.appVersion}`;
    supportedArch.textContent = `目标架构 ${payload.supportedArch}`;
  }

  function showSharedWarning(payload) {
    sharedWarn.textContent = payload.sharedRuntimeWarning || '';
    sharedWarn.classList.toggle('hidden', !payload.sharedRuntimeWarning);
    sealSharedBtn.classList.toggle('hidden', !payload.sharedRuntimeFixable);
  }

  async function sealShared() {
    sealSharedBtn.disabled = true;
    try {
      const out = await invoke('seal_shared_runtime_permissions_command');
      showSharedWarning(out || {});
      showToast(out && out.sharedRuntimeWarning ? '还有没收紧的地方,见提示' : '共享权限已收紧');
    } finally {
      sealSharedBtn.disabled = false;
    }
  }

  async function savePayload() {
    await invoke('save_preferences_command', {
      preferences: {
        autoCheckUpdates: controls.autoCheckUpdates.checked,
        showStatusNotifications: controls.showStatusNotifications.checked,
        compactLauncherLayout: controls.compactLauncherLayout.checked,
        enableExperimentalFeatures: controls.enableExperimentalFeatures.checked,
        alwaysReviewBeforeReplace: controls.alwaysReviewBeforeReplace.checked
      }
    });
    showToast('偏好设置已保存');
  }

  function bind(id, fn) {
    document.getElementById(id).addEventListener('click', async () => {
      try {
        await fn();
      } catch (error) {
        showToast(errorText(error));
      }
    });
  }

  saveBtn.addEventListener('click', savePayload);
  bind('sealSharedBtn', sealShared);
  bind('openRuntimeBtn', () => invoke('reveal_special_path', { kind: 'runtime' }));
  bind('repairRuntimeBtn', () => invoke('trigger_runtime_repair_command'));
  bind('checkUpdatesBtn', () => invoke('trigger_update_check_command'));
  bind('openDataBtn', () => invoke('reveal_special_path', { kind: 'data' }));
  bind('openLogsBtn', () => invoke('reveal_special_path', { kind: 'logs' }));
  bind('openDiagnosticsBtn', () => invoke('open_diagnostics_window_command'));
  bind('openLoginItemsBtn', () => invoke('open_login_items_settings_command'));

  loadPayload().catch((error) => showToast(errorText(error)));
})();
