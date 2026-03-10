(function () {
  const progressFill = document.getElementById('progressFill');
  const progressText = document.getElementById('progressText');
  const progressPct = document.getElementById('progressPct');
  const sessionInline = document.getElementById('sessionInline');
  const phaseLabel = document.getElementById('phaseLabel');
  const statusLog = document.getElementById('statusLog');
  const errorBox = document.getElementById('errorBox');
  const stepItems = Array.from(document.querySelectorAll('[data-step]'));
  const heroModeTag = document.getElementById('heroModeTag');
  const heroModeHint = document.getElementById('heroModeHint');
  const heroTitle = document.getElementById('heroTitle');
  const heroCopy = document.getElementById('heroCopy');
  const sceneTitle = document.getElementById('sceneTitle');
  const sceneCopy = document.getElementById('sceneCopy');
  const summarySessionType = document.getElementById('summarySessionType');
  const summaryRuntimeStrategy = document.getElementById('summaryRuntimeStrategy');
  const summaryBackendMode = document.getElementById('summaryBackendMode');
  const summaryOutcome = document.getElementById('summaryOutcome');
  const lines = [];
  let currentMode = 'launch';

  const MODE_CONFIG = {
    launch: {
      tag: '日常启动',
      hint: 'Runtime 快速自检',
      title: '正在启动 星阙',
      copy: '当前窗口只会短暂停留，用于检查现有 Runtime、后台拉起 Python / Java 服务，并在准备完成后自动进入星阙主界面。',
      sceneTitle: '日常启动',
      sceneCopy: '复用已安装 Runtime，只做快速校验与后台服务启动。',
      summarySessionType: '日常启动',
      summaryRuntimeStrategy: '优先复用现有 Runtime',
      summaryBackendMode: '隐藏式 Python / Java 服务',
      summaryOutcome: '准备完成后自动进入星阙主界面',
      sessionInline: '日常启动',
      phases: ['正在验证环境', '正在核对 Runtime', '正在启动服务', '即将进入 星阙']
    },
    install: {
      tag: '首次准备',
      hint: '下载并部署 Runtime',
      title: '正在准备 星阙 Runtime',
      copy: '当前机器缺少可用 Runtime，正在完成首次准备或完整重建。下载、校验与切换完成后会自动进入星阙主界面。',
      sceneTitle: 'Runtime 部署',
      sceneCopy: '需要下载并切换新的 Runtime payload，然后再启动本地服务。',
      summarySessionType: '首次准备 / 全量部署',
      summaryRuntimeStrategy: '下载、校验并切换新 Runtime',
      summaryBackendMode: '后台拉起 Python / Java 服务',
      summaryOutcome: '部署完成后自动进入星阙主界面',
      sessionInline: '首次准备',
      phases: ['正在验证环境', '正在部署 Runtime', '正在启动服务', '即将进入 星阙']
    },
    repair: {
      tag: '运行时修复',
      hint: '清理并重建 Runtime',
      title: '正在修复 星阙 Runtime',
      copy: '检测到 Runtime 需要重新整理、替换或手动重装，当前会先完成修复，再重新拉起星阙后台服务。',
      sceneTitle: 'Runtime 修复',
      sceneCopy: '会先清理现有 Runtime，再按需要重建或重新部署。',
      summarySessionType: 'Runtime 修复',
      summaryRuntimeStrategy: '清理异常文件并按需重新部署',
      summaryBackendMode: '修复完成后重启后台服务',
      summaryOutcome: '修复完成后自动返回星阙主界面',
      sessionInline: '运行时修复',
      phases: ['正在验证环境', '正在修复 Runtime', '正在启动服务', '即将进入 星阙']
    },
    update: {
      tag: '版本更新',
      hint: '替换应用并重开',
      title: '正在更新 星阙',
      copy: '当前会下载新的桌面壳与必要的 Runtime 资产，完成校验、替换与重开后回到新的星阙版本。',
      sceneTitle: '应用更新',
      sceneCopy: '会先完成下载与校验，再替换应用并自动重开。',
      summarySessionType: '桌面更新',
      summaryRuntimeStrategy: '按清单下载更新资产',
      summaryBackendMode: '更新后自动重开并恢复主界面',
      summaryOutcome: '替换成功后自动进入新版本',
      sessionInline: '版本更新',
      phases: ['正在准备更新', '正在下载资产', '正在替换应用', '即将重开 星阙']
    },
    error: {
      tag: '启动异常',
      hint: '需要人工处理',
      title: '星阙 启动未完成',
      copy: '当前会话未能顺利完成。下方日志会保留最近的诊断信息，便于直接定位启动、Runtime 或更新链路的问题。',
      sceneTitle: '启动异常',
      sceneCopy: '请优先查看实时日志与错误区域里的具体失败原因。',
      summarySessionType: '异常中断',
      summaryRuntimeStrategy: '需要查看日志并决定是否修复或重试',
      summaryBackendMode: '后台服务未完成就绪',
      summaryOutcome: '处理问题后再重新启动星阙',
      sessionInline: '启动异常',
      phases: ['正在验证环境', '处理中断', '等待处理', '等待重试']
    }
  };

  function pushLine(line) {
    lines.push(line);
    while (lines.length > 18) lines.shift();
    statusLog.textContent = lines.join('\n');
    statusLog.scrollTop = statusLog.scrollHeight;
  }

  function resolvePhase(pct) {
    const phases = MODE_CONFIG[currentMode]?.phases || MODE_CONFIG.launch.phases;
    if (pct >= 90) return { step: 4, label: phases[3] };
    if (pct >= 65) return { step: 3, label: phases[2] };
    if (pct >= 25) return { step: 2, label: phases[1] };
    return { step: 1, label: phases[0] };
  }

  function renderSteps(activeStep) {
    stepItems.forEach((item) => {
      const step = Number(item.dataset.step || 0);
      item.classList.toggle('is-active', step === activeStep);
      item.classList.toggle('is-complete', step < activeStep);
    });
  }

  function applyMode(mode) {
    const nextMode = MODE_CONFIG[mode] ? mode : 'launch';
    const config = MODE_CONFIG[nextMode];
    currentMode = nextMode;
    document.body.dataset.mode = nextMode;
    heroModeTag.textContent = config.tag;
    heroModeHint.textContent = config.hint;
    heroTitle.textContent = config.title;
    heroCopy.textContent = config.copy;
    sceneTitle.textContent = config.sceneTitle;
    sceneCopy.textContent = config.sceneCopy;
    summarySessionType.textContent = config.summarySessionType;
    summaryRuntimeStrategy.textContent = config.summaryRuntimeStrategy;
    summaryBackendMode.textContent = config.summaryBackendMode;
    summaryOutcome.textContent = config.summaryOutcome;
    sessionInline.textContent = config.sessionInline;
    phaseLabel.textContent = resolvePhase(Number(progressPct.textContent.replace('%', '')) || 0).label;
  }

  function inferMode(message) {
    const text = String(message || '');
    if (!text) return null;
    if (/下载桌面更新包|运行环境更新|替换应用并重开|更新下载完成/.test(text)) {
      return 'update';
    }
    if (/重新部署|修复/.test(text)) {
      return 'repair';
    }
    if (/下载运行环境|准备安装运行环境|解压运行环境|运行环境安装完成/.test(text)) {
      return currentMode === 'repair' ? 'repair' : 'install';
    }
    if (/检测到运行环境 .*已存在|正在检查安装配置|启动本地服务|本地服务已就绪/.test(text)) {
      return currentMode === 'update' ? 'update' : currentMode === 'repair' ? 'repair' : 'launch';
    }
    return null;
  }

  function setProgress(pct, text) {
    const clamped = Math.max(0, Math.min(100, Number(pct) || 0));
    const inferredMode = inferMode(text);
    if (inferredMode) applyMode(inferredMode);
    const phase = resolvePhase(clamped);
    progressFill.style.width = `${clamped}%`;
    progressPct.textContent = `${Math.round(clamped)}%`;
    phaseLabel.textContent = phase.label;
    renderSteps(phase.step);
    if (text) {
      progressText.textContent = text;
    }
  }

  window.__horosaMode = function (mode) {
    applyMode(mode);
  };

  window.__horosaStatus = function (message) {
    const inferredMode = inferMode(message);
    if (inferredMode) applyMode(inferredMode);
    pushLine(message);
  };

  window.__horosaProgress = function (pct, message) {
    setProgress(pct, message);
    if (message) pushLine(message);
  };

  window.__horosaError = function (message) {
    applyMode('error');
    errorBox.classList.remove('hidden');
    errorBox.textContent = message;
    pushLine(`错误: ${message}`);
  };

  window.__horosaReady = function (url) {
    setProgress(100, '星阙 已准备完成');
    pushLine('星阙 启动完成，正在打开主界面…');
    setTimeout(() => {
      window.location.replace(url);
    }, 500);
  };

  function replayPendingState() {
    if (window.__horosaPendingMode) {
      window.__horosaMode(window.__horosaPendingMode);
    }
    if (window.__horosaPendingProgress) {
      window.__horosaProgress(
        window.__horosaPendingProgress.pct,
        window.__horosaPendingProgress.message
      );
    }
    if (Array.isArray(window.__horosaPendingStatusLines)) {
      window.__horosaPendingStatusLines.forEach((line) => {
        window.__horosaStatus(line);
      });
      window.__horosaPendingStatusLines = [];
    }
    if (window.__horosaPendingError) {
      window.__horosaError(window.__horosaPendingError);
      return;
    }
    if (window.__horosaPendingReadyUrl) {
      window.__horosaReady(window.__horosaPendingReadyUrl);
    }
  }

  applyMode('launch');
  setProgress(0, '等待初始化…');
  pushLine('星阙启动页已加载。');
  replayPendingState();
})();
