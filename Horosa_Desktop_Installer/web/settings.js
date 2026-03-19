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
  const logsDir = document.getElementById('logsDir');
  const appVersion = document.getElementById('appVersion');
  const supportedArch = document.getElementById('supportedArch');
  const statusToast = document.getElementById('statusToast');
  const saveBtn = document.getElementById('saveBtn');

  async function invoke(cmd, args) {
    if (window.__TAURI__?.core?.invoke) {
      return window.__TAURI__.core.invoke(cmd, args);
    }
    if (window.__TAURI_INTERNALS__?.invoke) {
      return window.__TAURI_INTERNALS__.invoke(cmd, args);
    }
    throw new Error('Tauri invoke bridge unavailable');
  }

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
    appDataDir.textContent = payload.appDataDir;
    logsDir.textContent = payload.logsDir;
    appVersion.textContent = `星阙 ${payload.appVersion}`;
    supportedArch.textContent = `目标架构 ${payload.supportedArch}`;
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
    const el = document.getElementById(id);
    if (!el) return;
    el.addEventListener('click', async () => {
      try {
        await fn();
      } catch (error) {
        showToast(error.message || String(error));
      }
    });
  }

  saveBtn.addEventListener('click', savePayload);
  bind('openRuntimeBtn', () => invoke('reveal_special_path', { kind: 'runtime' }));
  bind('repairRuntimeBtn', () => invoke('trigger_runtime_repair_command'));
  bind('checkUpdatesBtn', () => invoke('trigger_update_check_command'));
  bind('openDataBtn', () => invoke('reveal_special_path', { kind: 'data' }));
  bind('openLogsBtn', () => invoke('reveal_special_path', { kind: 'logs' }));
  bind('openDiagnosticsBtn', () => invoke('open_diagnostics_window_command'));
  bind('openLoginItemsBtn', () => invoke('open_login_items_settings_command'));

  loadPayload().catch((error) => showToast(error.message || String(error)));
})();
