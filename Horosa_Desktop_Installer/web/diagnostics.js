(function () {
  const logPath = document.getElementById('logPath');
  const appDataDir = document.getElementById('appDataDir');
  const runtimeDir = document.getElementById('runtimeDir');
  const logOutput = document.getElementById('logOutput');
  const assetList = document.getElementById('assetList');

  async function invoke(cmd, args) {
    if (window.__TAURI__?.core?.invoke) {
      return window.__TAURI__.core.invoke(cmd, args);
    }
    if (window.__TAURI_INTERNALS__?.invoke) {
      return window.__TAURI_INTERNALS__.invoke(cmd, args);
    }
    throw new Error('Tauri invoke bridge unavailable');
  }

  async function refresh() {
    const payload = await invoke('read_diagnostics_snapshot');
    logPath.textContent = payload.logPath;
    appDataDir.textContent = payload.appDataDir;
    runtimeDir.textContent = payload.runtimeDir;
    logOutput.textContent = payload.lines.join('\n');
    assetList.innerHTML = (payload.assets || [])
      .map(
        (item) => `
          <div class="asset-row">
            <div class="asset-row-top">
              <div class="asset-row-title">${item.label}</div>
              <div class="asset-row-state">${item.state}</div>
            </div>
            <div class="asset-row-copy">${item.details}</div>
            <pre class="asset-row-path">${item.path}</pre>
          </div>
        `
      )
      .join('') || '当前未检测到需要审查的资产。';
  }

  document.getElementById('refreshBtn').addEventListener('click', () => {
    refresh().catch((error) => {
      logOutput.textContent = error.message || String(error);
    });
  });

  document.getElementById('openLogsBtn').addEventListener('click', () => {
    invoke('reveal_special_path', { kind: 'logs' }).catch((error) => {
      logOutput.textContent = error.message || String(error);
    });
  });

  refresh().catch((error) => {
    logOutput.textContent = error.message || String(error);
  });
  setInterval(() => {
    refresh().catch(() => {});
  }, 4000);
})();
