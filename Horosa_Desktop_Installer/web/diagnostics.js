(function () {
  const logPath = document.getElementById('logPath');
  const appDataDir = document.getElementById('appDataDir');
  const runtimeDir = document.getElementById('runtimeDir');
  const logOutput = document.getElementById('logOutput');
  const assetList = document.getElementById('assetList');
  const ledgerOutput = document.getElementById('ledgerOutput');
  const updateHistoryOutput = document.getElementById('updateHistoryOutput');

  // [U-G] 更新台账 JSONL → 人可读:「时间 事件 详情」;解析失败原样展示。
  function renderUpdateHistory(lines) {
    if (!lines || !lines.length) {
      return '暂无更新历史(完成一次更新后生成)。';
    }
    return lines
      .map((line) => {
        try {
          const row = JSON.parse(line);
          const when = row.ts ? new Date(row.ts).toLocaleString() : '';
          const rest = Object.entries(row)
            .filter(([k]) => k !== 'ts' && k !== 'event' && k !== 'shellVersion')
            .map(([k, v]) => `${k}=${v}`)
            .join(' ');
          return `${when}  ${String(row.event || '').padEnd(20)} ${rest}`;
        } catch (e) {
          return line;
        }
      })
      .join('\n');
  }

  // 启动账本 JSONL → 人可读分段表:「layer seg  t=…ms (ms=…)」,解析失败的行原样展示。
  function renderLedger(lines) {
    if (!lines || !lines.length) {
      return '暂无账本数据(完成一次启动后生成)。';
    }
    return lines
      .map((line) => {
        try {
          const row = JSON.parse(line);
          const t = row.t_ms != null ? `t=${row.t_ms}ms` : '';
          const ms = row.ms != null ? ` 段耗时=${row.ms}ms` : '';
          const extra = row.extra ? ` ${JSON.stringify(row.extra)}` : '';
          return `${String(row.layer || '').padEnd(4)} ${String(row.seg || '').padEnd(24)} ${t}${ms}${extra}`;
        } catch (e) {
          return line;
        }
      })
      .join('\n');
  }

  async function invoke(cmd, args) {
    if (window.__TAURI__?.core?.invoke) {
      return window.__TAURI__.core.invoke(cmd, args);
    }
    if (window.__TAURI_INTERNALS__?.invoke) {
      return window.__TAURI_INTERNALS__.invoke(cmd, args);
    }
    throw new Error('无法连接桌面程序，请重新打开星阙后重试');
  }

  async function refresh() {
    const payload = await invoke('read_diagnostics_snapshot');
    logPath.textContent = payload.logPath;
    appDataDir.textContent = payload.appDataDir;
    runtimeDir.textContent = payload.runtimeDir;
    logOutput.textContent = payload.lines.join('\n');
    if (ledgerOutput) {
      ledgerOutput.textContent = renderLedger(payload.ledgerLines);
    }
    if (updateHistoryOutput) {
      updateHistoryOutput.textContent = renderUpdateHistory(payload.updateHistoryLines);
    }
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

  // [U-G] 一键诊断包:壳收集 logs/台账/状态文件/系统信息 → 桌面 zip + Finder 定位
  const exportBtn = document.getElementById('exportBundleBtn');
  if (exportBtn) {
    exportBtn.addEventListener('click', () => {
      exportBtn.disabled = true;
      exportBtn.textContent = '正在打包…';
      invoke('export_diagnostics_bundle')
        .then((path) => {
          exportBtn.textContent = '已导出到桌面';
          logOutput.textContent = `诊断包已生成：\n${path}`;
        })
        .catch((error) => {
          exportBtn.textContent = '导出诊断包';
          logOutput.textContent = error.message || String(error);
        })
        .finally(() => {
          setTimeout(() => {
            exportBtn.disabled = false;
            exportBtn.textContent = '导出诊断包';
          }, 4000);
        });
    });
  }

  refresh().catch((error) => {
    logOutput.textContent = error.message || String(error);
  });
  setInterval(() => {
    refresh().catch(() => {});
  }, 4000);
})();

// ── 版面与缩放读数 ────────────────────────────────────────────────────────
// 由来(2026-08-27):旧机缩放档下全站底部一大条死带,而我们手上只有用户拍的照片,
// 只能靠量比例反推病因,来回折腾多轮。把关键读数直接摆在诊断页上,下次一屏截图即定谳。
//
// 三种引擎行为(真机实证):
//   跟随   rect 读数跟着缩放走(新系统 / Chromium)
//   不跟随 画面缩放了但读数不跟(旧 MacBook 实测)—— 历史上按读数换算版面就会算错
//   未缩放 声明了缩放但画面没缩放
// 现行代码两种都不依赖(改为直接量容器),此处读数仅供排障与回归取证。
(function () {
  function measure() {
    var d = document.documentElement;
    var declared = 1;
    try { var z = parseFloat(d.style.zoom); if (z > 0) declared = z; } catch (e) {}
    try {
      if (declared === 1) {
        var s = window.localStorage.getItem('horosa.shell.zoom');
        var sz = parseFloat(s);
        if (sz > 0) declared = sz;
      }
    } catch (e) {}

    var probe = document.createElement('div');
    probe.setAttribute('aria-hidden', 'true');
    probe.style.cssText = 'position:absolute;left:0;top:0;width:1000px;height:0;visibility:hidden;pointer-events:none';
    document.body.appendChild(probe);
    var rectScale = probe.getBoundingClientRect().width / 1000;
    document.body.removeChild(probe);

    var fx = document.createElement('div');
    fx.setAttribute('aria-hidden', 'true');
    fx.style.cssText = 'position:fixed;left:0;top:0;right:0;bottom:0;visibility:hidden;pointer-events:none';
    document.body.appendChild(fx);
    var lw = fx.offsetWidth, lh = fx.offsetHeight;
    document.body.removeChild(fx);

    var grew = (lh > 0 && window.innerHeight > 0) ? (lh / window.innerHeight) : 1;
    var engine;
    if (declared === 1) {
      engine = '未缩放档(读数无差异)';
    } else if (Math.abs(grew - 1 / declared) > 0.08) {
      engine = '未缩放 — 声明了缩放但画面没缩放';
    } else if (Math.abs(rectScale - declared) < 0.03) {
      engine = '跟随 — 读数随缩放变化';
    } else {
      engine = '不跟随 — 画面已缩放但读数不变';
    }
    return { declared: declared, layoutW: lw, layoutH: lh, engine: engine };
  }

  function paint() {
    try {
      var m = measure();
      var set = function (id, txt) {
        var el = document.getElementById(id);
        if (el) { el.textContent = txt; }
      };
      set('zoomDeclared', Math.round(m.declared * 100) + '%');
      set('zoomLayout', (m.layoutW || '?') + ' × ' + (m.layoutH || '?') + ' 点'
        + '(窗口 ' + window.innerWidth + ' × ' + window.innerHeight + ')');
      set('zoomEngine', m.engine);
    } catch (e) {}
  }

  if (document.body) { paint(); } else { document.addEventListener('DOMContentLoaded', paint); }
  window.addEventListener('resize', function () { setTimeout(paint, 60); });
  var rb = document.getElementById('refreshBtn');
  if (rb) { rb.addEventListener('click', function () { setTimeout(paint, 60); }); }
})();
