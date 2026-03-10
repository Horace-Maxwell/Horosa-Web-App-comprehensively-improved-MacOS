(function () {
  const progressFill = document.getElementById('progressFill');
  const progressText = document.getElementById('progressText');
  const progressPct = document.getElementById('progressPct');
  const progressInline = document.getElementById('progressInline');
  const phaseLabel = document.getElementById('phaseLabel');
  const statusLog = document.getElementById('statusLog');
  const errorBox = document.getElementById('errorBox');
  const stepItems = Array.from(document.querySelectorAll('[data-step]'));
  const lines = [];

  function pushLine(line) {
    lines.push(line);
    while (lines.length > 18) lines.shift();
    statusLog.textContent = lines.join('\n');
    statusLog.scrollTop = statusLog.scrollHeight;
  }

  function resolvePhase(pct) {
    if (pct >= 90) return { step: 4, label: '即将进入 Horosa' };
    if (pct >= 65) return { step: 3, label: '正在启动服务' };
    if (pct >= 25) return { step: 2, label: '正在部署 Runtime' };
    return { step: 1, label: '正在验证环境' };
  }

  function renderSteps(activeStep) {
    stepItems.forEach((item) => {
      const step = Number(item.dataset.step || 0);
      item.classList.toggle('is-active', step === activeStep);
      item.classList.toggle('is-complete', step < activeStep);
    });
  }

  function setProgress(pct, text) {
    const clamped = Math.max(0, Math.min(100, Number(pct) || 0));
    const phase = resolvePhase(clamped);
    progressFill.style.width = `${clamped}%`;
    progressPct.textContent = `${Math.round(clamped)}%`;
    phaseLabel.textContent = phase.label;
    renderSteps(phase.step);
    if (text) {
      progressText.textContent = text;
      progressInline.textContent = text;
    }
  }

  window.__horosaStatus = function (message) {
    pushLine(message);
  };

  window.__horosaProgress = function (pct, message) {
    setProgress(pct, message);
    if (message) pushLine(message);
  };

  window.__horosaError = function (message) {
    errorBox.classList.remove('hidden');
    errorBox.textContent = message;
    pushLine(`错误: ${message}`);
  };

  window.__horosaReady = function (url) {
    setProgress(100, '初始化完成，正在进入 Horosa');
    pushLine('安装与初始化完成，正在打开星阙主界面…');
    setTimeout(() => {
      window.location.replace(url);
    }, 500);
  };

  setProgress(0, '等待初始化…');
  pushLine('星阙安装器界面已加载。');
})();
