// 🔴 [布局密度·2026-08-25] CSS 媒体查询在 CSS zoom 下**看不见真实可用空间**。
// 实测:窗口 1180×760、zoom=1.8 时,matchMedia('(max-height:720px)') 仍为 false
// (它按视口 rect 域 1180×760 评估),而实际布局空间只剩 656×422 —— 断点永不触发,
// 内容被挤爆也不会切紧凑布局。故改用 JS 实测布局空间,挂 data-density 给 CSS 用。
(function(){
  var LAST = '';
  // 🔴 2026-08-27 根修:直接量布局空间,不再「物理读数 ÷ 缩放」。
  // 旧写法拿 rect 探针当缩放值去除 clientWidth/Height,而旧 MacBook(Safari 26.2)上
  // rect 根本不反映 zoom、探针恒测得 1 ⇒ 等于没除 ⇒ 密度档判错(高缩放下该切 micro
  // 却仍按 normal 排,内容挤爆)。主应用同一处错误造成了工作区底部死带。
  // 正解是不去问缩放:position:fixed;inset:0 的 offsetWidth/offsetHeight 就是布局空间,
  // 任何 zoom 语义下都直接成立。实测(物理 720):0.7→1029 / 0.8→900 / 1.8→400 = 720/z。
  function layoutSpace(){
    try {
      if (!document.body) return null;
      var probe = document.createElement('div');
      probe.setAttribute('aria-hidden', 'true');
      probe.style.cssText = 'position:fixed;left:0;top:0;right:0;bottom:0;visibility:hidden;pointer-events:none';
      document.body.appendChild(probe);
      var w = probe.offsetWidth, h = probe.offsetHeight;
      document.body.removeChild(probe);
      if (w > 0 && h > 0) return { w: w, h: h };
    } catch (e) {}
    return null;
  }
  function apply(){
    try {
      if (!document.body) return;
      var d = document.documentElement;
      var sp = layoutSpace();
      // 量不到时退物理读数:缩放≠1 会偏保守(更早切紧凑),但绝不会排爆版面。
      var w = sp ? sp.w : d.clientWidth, h = sp ? sp.h : d.clientHeight;
      // 阀值按实测定:1180×760 窗口在 1.5 倍缩放下布局高 507px,刚好卡在 500 外而走不到 micro,
      // 侧栏就差那一点放不下 —— 提到 530 后 0.7–1.8 全 12 档均无需滚动。
      var mode = (h < 530 || w < 800) ? 'micro' : ((h < 640 || w < 1000) ? 'compact' : 'normal');
      if (mode !== LAST) { d.setAttribute('data-density', mode); LAST = mode; }
    } catch (e) {}
  }
  if (document.body) apply(); else document.addEventListener('DOMContentLoaded', apply);
  window.addEventListener('resize', apply);
  // 壳改缩放后会 dispatch resize,但 zoom 应用与 resize 可能同帧,补一次延迟兜底。
  window.addEventListener('resize', function(){ setTimeout(apply, 50); });
  window.__HOROSA_APPLY_DENSITY = apply;
})();

(function () {
  const progressFill = document.getElementById('progressFill');
  const progressTrack = progressFill?.parentElement || null;
  const progressText = document.getElementById('progressText');
  const progressPct = document.getElementById('progressPct');
  const sessionInline = document.getElementById('sessionInline');
  const phaseLabel = document.getElementById('phaseLabel');
  const statusLog = document.getElementById('statusLog');
  const stepItems = Array.from(document.querySelectorAll('[data-step]'));
  const heroBadgePrimary = document.getElementById('heroBadgePrimary');
  const heroBadgeSecondary = document.getElementById('heroBadgeSecondary');
  const heroBadgeTertiary = document.getElementById('heroBadgeTertiary');
  const heroModeTag = document.getElementById('heroModeTag');
  const heroModeHint = document.getElementById('heroModeHint');
  const heroTitle = document.getElementById('heroTitle');
  const heroCopy = document.getElementById('heroCopy');
  const sceneTitle = document.getElementById('sceneTitle');
  const sceneCopy = document.getElementById('sceneCopy');
  const summarySessionType = document.getElementById('summarySessionType');
  const summaryRuntimeStrategy = document.getElementById('summaryRuntimeStrategy');
  const summaryThirdLabel = document.getElementById('summaryThirdLabel');
  const summaryBackendMode = document.getElementById('summaryBackendMode');
  const summaryOutcome = document.getElementById('summaryOutcome');
  const progressSubtitle = document.getElementById('progressSubtitle');
  const primaryCtaBtn = document.getElementById('primaryCtaBtn');
  const primaryCtaLabel = document.getElementById('primaryCtaLabel');
  const diagnosticDot = document.getElementById('diagnosticDot');
  const milestones = Array.from(document.querySelectorAll('[data-milestone]'));
  const phaseItems = Array.from(document.querySelectorAll('[data-phase-step]'));
  const openPreferencesBtn = document.getElementById('openPreferencesBtn');
  const openDiagnosticsBtn = document.getElementById('openDiagnosticsBtn');
  const openDataBtn = document.getElementById('openDataBtn');
  const openRuntimeBtn = document.getElementById('openRuntimeBtn');
  const retryBtn = document.getElementById('retryBtn');
  const retryActionTitle = document.getElementById('retryActionTitle');
  const retryActionCopy = document.getElementById('retryActionCopy');
  const toggleLogBtn = document.getElementById('toggleLogBtn');
  const logSummaryNote = document.getElementById('logSummaryNote');
  const assetReviewPanel = document.getElementById('assetReviewPanel');
  const reviewIntro = document.getElementById('reviewIntro');
  const reviewBlocking = document.getElementById('reviewBlocking');
  const reviewItems = document.getElementById('reviewItems');
  const reviewContinueBtn = document.getElementById('reviewContinueBtn');
  const reviewCancelBtn = document.getElementById('reviewCancelBtn');
  const statePanel = document.getElementById('statePanel');
  const stateBadge = document.getElementById('stateBadge');
  const stateInstallSource = document.getElementById('stateInstallSource');
  const stateTitle = document.getElementById('stateTitle');
  const stateSummary = document.getElementById('stateSummary');
  const stateDetail = document.getElementById('stateDetail');
  const stateRecommendation = document.getElementById('stateRecommendation');
  const recoveryPanel = document.getElementById('recoveryPanel');
  const recoveryBadge = document.getElementById('recoveryBadge');
  const recoveryInstallSource = document.getElementById('recoveryInstallSource');
  const recoveryTitle = document.getElementById('recoveryTitle');
  const recoverySummary = document.getElementById('recoverySummary');
  const recoveryDetail = document.getElementById('recoveryDetail');
  const recoveryRecommendation = document.getElementById('recoveryRecommendation');
  const recoveryPrimaryBtn = document.getElementById('recoveryPrimaryBtn');
  const recoverySecondaryActions = document.getElementById('recoverySecondaryActions');
  const recoveryDetails = document.getElementById('recoveryDetails');
  const recoveryRawError = document.getElementById('recoveryRawError');
  const guardKeyOne = document.getElementById('guardKeyOne');
  const guardValueOne = document.getElementById('guardValueOne');
  const guardKeyTwo = document.getElementById('guardKeyTwo');
  const guardValueTwo = document.getElementById('guardValueTwo');
  const guardKeyThree = document.getElementById('guardKeyThree');
  const guardValueThree = document.getElementById('guardValueThree');
  const guardKeyFour = document.getElementById('guardKeyFour');
  const guardValueFour = document.getElementById('guardValueFour');
  const footerNote = document.getElementById('footerNote');
  const lines = [];
  let currentMode = 'launch';
  let currentReviewPayload = null;
  let currentReviewDecisions = {};
  let currentStatePayload = null;
  let hasExplicitState = false;
  let currentErrorPayload = null;
  let showFullLog = false;
  let retryActionKind = 'repair_runtime';
  let progressIsIndeterminate = false;
  const APP_VERSION = '3.9.5';
  let currentTone = 'launch';

  async function invoke(cmd, args) {
    if (window.__TAURI__?.core?.invoke) {
      return window.__TAURI__.core.invoke(cmd, args);
    }
    if (window.__TAURI_INTERNALS__?.invoke) {
      return window.__TAURI_INTERNALS__.invoke(cmd, args);
    }
    throw new Error('无法连接桌面程序，请重新打开星阙后重试');
  }

  function escapeHtml(value) {
    return String(value ?? '')
      .replace(/&/g, '&amp;')
      .replace(/</g, '&lt;')
      .replace(/>/g, '&gt;')
      .replace(/"/g, '&quot;')
      .replace(/'/g, '&#39;');
  }

  function nowTime(offsetSeconds = 0) {
    const date = new Date(Date.now() + offsetSeconds * 1000);
    return date.toLocaleTimeString('zh-CN', {
      hour12: false,
      hour: '2-digit',
      minute: '2-digit',
      second: '2-digit'
    });
  }

  function setProgressNumber(value) {
    if (!progressPct) return;
    if (String(value) === '接收中') {
      progressPct.textContent = '接收中';
      return;
    }
    const clamped = Math.max(0, Math.min(100, Number(value) || 0));
    progressPct.innerHTML = `${Math.round(clamped)}<span class="pct-sign">%</span>`;
  }

  function setProgressCopy(prefix, emphasis, suffix = '') {
    if (!progressSubtitle) return;
    const parts = [];
    if (prefix) parts.push(escapeHtml(prefix));
    if (emphasis) parts.push(`<span>${escapeHtml(emphasis)}</span>`);
    if (suffix) parts.push(escapeHtml(suffix));
    progressSubtitle.innerHTML = parts.join(' · ');
  }

  function statusIcon(kind) {
    if (kind === 'ready') return '<svg aria-hidden="true"><use href="#xq-check"></use></svg>';
    if (kind === 'failed') return '<svg aria-hidden="true"><use href="#xq-x"></use></svg>';
    return '<span class="status-dot" aria-hidden="true"></span>';
  }

  function setStatusPill(kind, label) {
    if (!heroBadgeTertiary) return;
    heroBadgeTertiary.className = `progress-status hero-badge hero-badge--${kind}`;
    heroBadgeTertiary.innerHTML = `${statusIcon(kind)}${escapeHtml(label)}`;
  }

  function setPrimaryCta(visible, label) {
    if (!primaryCtaBtn || !primaryCtaLabel) return;
    primaryCtaLabel.textContent = label || '进入主界面';
    primaryCtaBtn.classList.toggle('hidden', !visible);
  }

  function applyLauncherTone(tone) {
    currentTone = tone || 'launch';
    document.body.dataset.launcherTone = currentTone;
    diagnosticDot?.classList.toggle('hidden', currentTone !== 'error');
    if (toggleLogBtn) {
      toggleLogBtn.textContent = currentTone === 'error' ? '展开错误' : '展开详情';
    }
    if (currentTone === 'ready') {
      setStatusPill('ready', '已就绪');
      setPrimaryCta(true, '进入主界面');
    } else if (currentTone === 'error') {
      setStatusPill('failed', '未完成');
      setPrimaryCta(true, '重建 Runtime');
    } else {
      setStatusPill('live', '进行中');
      setPrimaryCta(false, '进入主界面');
    }
  }

  const MODE_CONFIG = {
    launch: {
      tag: '日常启动',
      hint: '复用本机组件',
      title: '正在检查本机环境',
      copy: '完成后将自动进入主界面，无需手动操作',
      sceneTitle: '正在检查本机环境',
      sceneCopy: '完成后将自动进入主界面，无需手动操作',
      summarySessionType: '日常启动',
      summaryRuntimeStrategy: '复用本机组件',
      summaryBackendMode: '后台启动',
      summaryOutcome: '待进入主界面',
      sessionInline: '日常启动',
      phases: ['安装检查', '本机组件', '后台服务', '主界面'],
      badges: ['日常启动', '复用本机组件', 'LIVE']
    },
    offline: {
      tag: '离线安装',
      hint: '本次不会联网下载',
      title: '离线安装已完成',
      copy: '本次未联网，所有组件来自离线包；下次打开将直接进入主界面',
      sceneTitle: '离线安装已完成',
      sceneCopy: '本次未联网，所有组件来自离线包；下次打开将直接进入主界面',
      summarySessionType: '离线安装完成',
      summaryRuntimeStrategy: '来自离线包的本机组件',
      summaryBackendMode: '下次启动直接复用',
      summaryOutcome: '已完成',
      sessionInline: '离线安装已完成',
      phases: ['安装检查', '本机组件', '后台服务', '完成'],
      badges: ['离线安装', '离线包已校验', '已就绪']
    },
    install: {
      tag: '首次准备',
      hint: '部署本机组件',
      title: '准备本机组件',
      copy: '校验离线包 · 写入本机组件 · 启动服务',
      sceneTitle: '首次准备',
      sceneCopy: '正在部署排盘所需的本机组件。',
      summarySessionType: '首次准备',
      summaryRuntimeStrategy: '部署并校验组件',
      summaryBackendMode: '部署后启动',
      summaryOutcome: '进入主界面',
      sessionInline: '首次准备',
      phases: ['检查安装', '部署组件', '启动服务', '进入主界面']
    },
    repair: {
      tag: '组件修复',
      hint: '重建本机组件',
      title: '修复本机组件',
      copy: '清理异常标记 · 重建本机组件 · 保留个人数据',
      sceneTitle: '本机组件修复',
      sceneCopy: '只处理损坏或不完整组件。',
      summarySessionType: '组件修复',
      summaryRuntimeStrategy: '重建异常组件',
      summaryBackendMode: '修复后启动',
      summaryOutcome: '返回主界面',
      sessionInline: '组件修复',
      phases: ['检查安装', '修复组件', '启动服务', '进入主界面']
    },
    update: {
      tag: '版本更新',
      hint: '下载并重开',
      title: '更新星阙',
      copy: '下载 · 校验 · 替换程序 · 重新打开',
      sceneTitle: '应用更新',
      sceneCopy: '按更新清单替换程序与组件。',
      summarySessionType: '版本更新',
      summaryRuntimeStrategy: '按更新清单校验',
      summaryBackendMode: '替换后重开',
      summaryOutcome: '进入新版本',
      sessionInline: '版本更新',
      phases: ['准备更新', '下载资产', '替换应用', '重开星阙']
    },
    error: {
      tag: '需要处理',
      hint: '等待恢复动作',
      title: '启动中断',
      copy: '查看诊断 · 保留日志 · 执行恢复',
      sceneTitle: '需要处理',
      sceneCopy: '优先显示可执行恢复动作。',
      summarySessionType: '流程中断',
      summaryRuntimeStrategy: '保留现场',
      summaryBackendMode: '服务未就绪',
      summaryOutcome: '恢复后重试',
      sessionInline: '需要处理',
      phases: ['检查安装', '流程中断', '等待恢复', '等待重试']
    }
  };

  const ACTION_LABELS = {
    reinstall_offline_package: '重新安装离线包',
    open_diagnostics: '打开诊断中心',
    reveal_data: '显示数据目录',
    reveal_runtime: '显示本机组件'
  };

  function sourceLabel(source) {
    return (
      {
        pkg_offline: '当前安装来源：离线安装包',
        pkg_online: '当前安装来源：在线安装包',
        dmg_online: '当前安装来源：DMG 安装'
      }[source] || ''
    );
  }

  function runtimeVersionForPayload(payload) {
    const direct = payload?.runtimeVersion || payload?.runtime_version || payload?.version;
    if (direct) return String(direct);
    const sourceText = [payload?.detail, payload?.summary, payload?.rawError].filter(Boolean).join(' ');
    const match = sourceText.match(/(?:runtime|本机组件|版本)\s*(?:version|版本)?\s*([0-9]+\.[0-9]+\.[0-9]+(?:[-\w.]*)?)/i);
    return match?.[1] || APP_VERSION;
  }

  function toTitleCase(value) {
    const map = {
      installed_app: '已安装 App',
      shared_runtime: '共享本机组件',
      user_runtime: '当前用户本机组件',
      pending_marker: '待处理安装标记',
      cached_runtime_archive: '本机组件缓存',
      cached_app_update: 'App 更新缓存',
      healthy: '可复用',
      outdated: '版本旧',
      broken: '损坏或不完整',
      pending: '待处理',
      cache_only: '待清理缓存'
    };
    return map[value] || value;
  }

  function modeToLabel(mode) {
    return (
      {
        install: '安装审查',
        repair: '修复审查',
        update: '更新审查'
      }[mode] || '安装审查'
    );
  }

  function fallbackStateForMode(mode) {
    switch (mode) {
      case 'install':
        return {
          kind: 'launch_ready',
          badge: '首次准备',
          title: '部署本机组件',
          summary: '排盘所需组件将写入本机共享位置。',
          detail: '完成后启动后台服务与排盘引擎。',
          recommendation: null,
          installSource: null
        };
      case 'repair':
        return {
          kind: 'repair_in_progress',
          badge: '组件修复',
          title: '重建异常组件',
          summary: '保留用户数据与日志。',
          detail: '只替换损坏或不完整的组件内容。',
          recommendation: null,
          installSource: null
        };
      case 'update':
        return {
          kind: 'update_in_progress',
          badge: '版本更新',
          title: '按更新清单更新',
          summary: '下载、校验、替换、重开。',
          detail: '用户数据不参与替换。',
          recommendation: null,
          installSource: null
        };
      case 'offline':
        return {
          kind: 'offline_ready',
          badge: '已就绪',
          title: '离线安装已完成',
          summary: '本次未联网，所有组件来自离线包；下次打开将直接进入主界面',
          detail: '当前步骤：—',
          recommendation: null,
          installSource: 'pkg_offline'
        };
      default:
        return {
          kind: 'launch_checking',
          badge: '日常启动',
          title: '正在检查本机环境',
          summary: '完成后将自动进入主界面，无需手动操作',
          detail: '当前步骤：检查 程序签名',
          recommendation: null,
          installSource: null
        };
    }
  }

  function defaultSupportContentForMode(mode) {
    switch (mode) {
      case 'install':
        return {
          modeTag: '首次准备',
          modeHint: '仅在需要时准备本机组件',
          brandTitle: '正在为这台 Mac 准备 星阙',
          brandCopy: '首次准备会在程序内安静完成，无需你了解任何内部细节。',
          sceneTitleText: '首次准备',
          sceneCopyText: '如果本机缺少所需内容，星阙会自动完成准备、校验与切换。',
          sessionInlineText: '首次准备',
          summarySessionTypeText: '首次准备',
          summaryRuntimeStrategyText: '按需准备并接管本机组件',
          summaryBackendModeText: '准备完成后自动启动所需服务',
          summaryOutcomeText: '直接进入主界面',
          heroBadges: ['首次准备在程序内完成', '只在需要时准备组件', '普通用户无需手工处理'],
          guards: [
            ['准备方式', '只有确认需要的内容才会被准备或替换。'],
            ['安装审查', '先看清这次会处理什么，再决定是否继续。'],
            ['技术细节', '过程摘要默认收起，避免技术信息抢占主视图。'],
            ['数据目录', '用户数据与运行日志不会在准备时被删除。']
          ],
          footer: '首次准备会尽量贴近标准的 Mac 应用体验，而不是工程安装器。',
          retry: {
            title: '重装本机组件',
            copy: '当组件损坏或准备不完整时，重新准备本机组件',
            action: 'repair_runtime'
          }
        };
      case 'repair':
        return {
          modeTag: '组件修复',
          modeHint: '保留当前数据，重新整理本机组件',
          brandTitle: '正在恢复这台 Mac 上的 星阙',
          brandCopy: '当前流程会优先保留数据和诊断入口，把修复动作集中在 app 内完成。',
          sceneTitleText: '本机组件修复',
          sceneCopyText: '修复会先整理已安装内容，再按需替换真正需要重建的部分。',
          sessionInlineText: '组件修复',
          summarySessionTypeText: '组件修复',
          summaryRuntimeStrategyText: '尽量保留可复用内容，仅重建需要修复的部分',
          summaryBackendModeText: '修复完成后自动启动所需服务',
          summaryOutcomeText: '完成后返回主界面',
          heroBadges: ['修复在程序内完成', '日志与诊断入口已保留', '修复后自动回到主界面'],
          guards: [
            ['首选动作', '主界面会优先显示下一步建议，而不是直接铺满原始错误。'],
            ['安装审查', '只有你明确勾选替换的项目才会被处理。'],
            ['已安装内容', '可随时在 Finder 查看数据目录与本机组件位置。'],
            ['数据安全', '修复不会主动删除用户数据。']
          ],
          footer: '修复流程会优先展示恢复动作，把技术细节放回第二层。',
          retry: {
            title: '重装本机组件',
            copy: '当组件损坏或更新不完整时，重新准备本机组件',
            action: 'repair_runtime'
          }
        };
      case 'update':
        return {
          modeTag: '版本更新',
          modeHint: '下载、校验并自动重开',
          brandTitle: '正在更新 星阙',
          brandCopy: '新版本会先完成下载和校验，再替换应用并自动重开，不需要额外操作。',
          sceneTitleText: '应用更新',
          sceneCopyText: '更新过程会尽量保持安静，只在确实需要替换的内容上继续处理。',
          sessionInlineText: '版本更新',
          summarySessionTypeText: '版本更新',
          summaryRuntimeStrategyText: '按清单校验并替换本次更新资产',
          summaryBackendModeText: '替换成功后自动重开',
          summaryOutcomeText: '自动进入新版本',
          heroBadges: ['后台下载与校验', '替换完成后自动重开', '当前数据保持不变'],
          guards: [
            ['应用更新', '先替换 `.app`，再回到新的 星阙。'],
            ['更新审查', '开始下载前先确认这次要替换哪些项目。'],
            ['技术细节', '完整日志仍然保留，但默认不会压过当前状态。'],
            ['数据目录', '用户数据与运行日志不会在更新时被删除。']
          ],
          footer: '更新流程会更像正式 Mac app：下载、校验、替换和重开都在 app 内完成。',
          retry: {
            title: '重装本机组件',
            copy: '如果更新后本机组件不完整，可重新准备本机组件',
            action: 'repair_runtime'
          }
        };
      case 'update_review':
        return {
          modeTag: '版本更新',
          modeHint: '先检查，再由你决定是否继续',
          brandTitle: '已发现可用更新，等待你确认',
          brandCopy: '这次先只展示更新结果，不会立刻开始下载；只有你明确确认后，才会进入下载、校验和替换流程。',
          sceneTitleText: '更新待确认',
          sceneCopyText: '当前版本会保持不动，直到你明确选择继续本次更新。',
          sessionInlineText: '等待确认更新',
          summarySessionTypeText: '更新待确认',
          summaryRuntimeStrategyText: '先比对版本与更新摘要，再由你决定是否开始替换',
          summaryBackendModeText: '确认之前不会开始下载或重开',
          summaryOutcomeText: '确认后才进入更新事务',
          heroBadges: ['先检查结果再决定', '确认前不会开始下载', '当前版本保持不变'],
          guards: [
            ['更新入口', '“检查更新”现在默认只是检查，不会直接开始下载。'],
            ['用户确认', '只有你明确选择继续时，才会进入更新事务。'],
            ['当前状态', '在你确认之前，当前 app 和本机组件都不会被替换。'],
            ['后续动作', '一旦确认继续，下载、校验、替换和重开会作为同一笔事务执行。']
          ],
          footer: '更新检查已经改成两阶段：先展示结果，再由你手动决定要不要开始更新。',
          retry: {
            title: '重新检查更新',
            copy: '如果你暂缓了本次更新，稍后可以再重新检查',
            action: 'repair_runtime'
          }
        };
      case 'error':
        return {
          modeTag: '需要处理',
          modeHint: '恢复动作优先，技术细节后置',
          brandTitle: '星阙 还没有准备完成',
          brandCopy: '当前流程没有顺利完成。主界面会先告诉你下一步该做什么，再决定是否查看技术细节。',
          sceneTitleText: '需要处理',
          sceneCopyText: '主视图优先给出恢复动作，完整日志和原始错误会退到第二层。',
          sessionInlineText: '需要处理',
          summarySessionTypeText: '流程中断',
          summaryRuntimeStrategyText: '保留当前状态，等待你决定下一步',
          summaryBackendModeText: '后台服务尚未完全就绪',
          summaryOutcomeText: '处理完成后再重试',
          heroBadges: ['恢复动作优先', '诊断入口仍然保留', '数据与日志已保留'],
          guards: [
            ['首选恢复', '先按推荐动作继续，技术细节可以稍后再看。'],
            ['诊断中心', '需要排查时再展开完整日志和原始错误。'],
            ['已安装内容', 'Finder 入口仍然保留，方便你核对当前位置。'],
            ['数据安全', '当前数据和日志都没有被清掉。']
          ],
          footer: '启动页会先展示恢复动作，再把工程细节收回第二层。',
          retry: {
            title: '重装本机组件',
            copy: '如果需要重新准备本机组件，可从这里开始',
            action: 'repair_runtime'
          }
        };
      default:
        return {
          modeTag: '日常启动',
          modeHint: '复用本机组件',
          brandTitle: '正在检查本机环境',
          brandCopy: '完成后将自动进入主界面，无需手动操作',
          sceneTitleText: '正在检查本机环境',
          sceneCopyText: '完成后将自动进入主界面，无需手动操作',
          sessionInlineText: '日常启动',
          summarySessionTypeText: '日常启动',
          summaryRuntimeStrategyText: '复用本机组件',
          summaryBackendModeText: '后台服务待启动',
          summaryOutcomeText: '待进入主界面',
          heroBadges: ['日常启动', '复用本机组件', 'LIVE'],
          guards: [
            ['程序本体', '签名校验后替换。'],
            ['本机组件', '损坏或版本不符才重建。'],
            ['运行日志', '失败时保留。'],
            ['个人数据', '更新不删除用户数据。']
          ],
          footer: '窗口大小会随上次关闭状态恢复。',
          retry: {
            title: '重装本机组件',
            copy: '当组件损坏或更新不完整时，重新准备本机组件',
            action: 'repair_runtime'
          }
        };
    }
  }

  function supportContentForPayload(payload) {
    const modeDefaults = defaultSupportContentForMode(currentMode);
    switch (payload?.kind) {
      case 'offline_ready':
        return {
          ...modeDefaults,
          modeTag: '离线安装',
          modeHint: '离线包已校验',
          brandTitle: '离线安装已完成',
          brandCopy: '本次未联网，所有组件来自离线包；下次打开将直接进入主界面',
          sceneTitleText: '离线安装已完成',
          sceneCopyText: '本次未联网，所有组件来自离线包；下次打开将直接进入主界面',
          sessionInlineText: '离线安装已完成',
          summarySessionTypeText: '离线安装完成',
          summaryRuntimeStrategyText: '来自离线包的本机组件',
          summaryBackendModeText: '下次启动直接复用',
          summaryOutcomeText: '已完成',
          heroBadges: ['离线安装', '离线包已校验', '已就绪'],
          guards: [
            ['程序本体', '签名校验后替换。'],
            ['本机组件', '离线包组件已校验。'],
            ['运行日志', '失败时保留。'],
            ['个人数据', '安装更新不删除用户数据。']
          ],
          footer: '离线安装完成后，下次打开会直接复用本机组件并进入主界面。',
          retry: {
            title: '重新安装离线包',
            copy: '用离线包重装一次',
            action: 'reinstall_offline_package'
          }
        };
      case 'offline_review':
        return {
          ...modeDefaults,
          modeTag: '离线安装',
          modeHint: '先确认再替换',
          brandTitle: '请确认这次要替换的内容',
          brandCopy: '这台 Mac 已经有相关内容；离线路径下只会处理你明确勾选为替换的项目。',
          sceneTitleText: '离线安装审查',
          sceneCopyText: '已发现本机已有内容，继续前请先确认这次真正要替换哪些项目。',
          sessionInlineText: '等待安装审查',
          summarySessionTypeText: '离线路径审查',
          summaryRuntimeStrategyText: '尽量复用已可用内容，只替换你勾选的项目',
          summaryBackendModeText: '确认后再继续后续处理',
          summaryOutcomeText: '审查完成后自动继续',
          heroBadges: ['离线安装来源', '先确认再替换', '不会自动联网准备'],
          guards: [
            ['安装审查', '只有勾选为“替换”的内容才会被处理。'],
            ['离线路径', '即使继续审查，也不会自动转成联网准备。'],
            ['已安装内容', '共享本机组件、当前用户内容和缓存都会先列出来。'],
            ['恢复入口', '如需彻底重新接管，也可以直接重新安装离线包。']
          ],
          footer: '离线路径下的安装审查会优先复用可用内容，不会因为发现旧资产就自动联网。',
          retry: {
            title: '重新安装离线包',
            copy: '如果你想直接重新接管离线路径，可以重新运行离线安装包',
            action: 'reinstall_offline_package'
          }
        };
      case 'update_review':
        return {
          ...defaultSupportContentForMode('update_review')
        };
      case 'offline_repair_required':
        return {
          ...defaultSupportContentForMode('error'),
          modeTag: '离线路径修复',
          modeHint: '首选重新安装离线包',
          brandTitle: '需要重新安装离线包',
          brandCopy: '当前共享本机组件不完整。建议直接重新运行离线安装包，而不是转成联网修复。',
          sceneTitleText: '离线修复',
          sceneCopyText: '主界面会把恢复动作放在最前面，诊断中心和技术细节保留在第二层。',
          sessionInlineText: '离线路径需要修复',
          summarySessionTypeText: '离线路径修复',
          summaryRuntimeStrategyText: '优先重新接管离线安装已放置的本机组件',
          summaryBackendModeText: '当前不会转为联网准备',
          summaryOutcomeText: '重新安装后再进入主界面',
          heroBadges: ['离线路径需要修复', '首选重新安装离线包', '诊断信息已保留'],
          guards: [
            ['首选恢复', '重新安装离线包是最稳妥的恢复方式。'],
            ['诊断中心', '如需排查，可以再展开日志和原始错误。'],
            ['已安装内容', 'Finder 入口仍然保留，方便你确认 app 与本机组件位置。'],
            ['联网策略', '当前不会自动转去联网下载，也不会把在线修复当作首选路径。']
          ],
          footer: '离线路径损坏时，启动页会优先引导你重新安装离线包，而不是把你带回工程修复流程。',
          retry: {
            title: '重新安装离线包',
            copy: '重新运行离线安装包，重新接管共享本机组件',
            action: 'reinstall_offline_package'
          }
        };
      default:
        return modeDefaults;
    }
  }

  function compactSupportContent(content, payload) {
    const key = payload?.kind || currentMode;
    const commonGuards = [
      ['程序本体', '签名校验后替换。'],
      ['本机组件', '损坏或版本不符才重建。'],
      ['运行日志', '失败时保留。'],
      ['个人数据', '更新不删除用户数据。']
    ];
    const variants = {
      launch: {
        tone: 'launch',
        modeTag: '日常启动',
        modeHint: '复用本机组件',
        brandTitle: '检查本机环境',
        brandCopy: '完成后自动进入主界面',
        sceneTitleText: '正在检查本机环境',
        sceneCopyText: '完成后将自动进入主界面，无需手动操作',
        sessionInlineText: '日常启动',
        summarySessionTypeText: '日常启动',
        summaryRuntimeStrategyText: '复用本机组件',
        summaryThirdLabelText: '预计',
        summaryBackendModeText: '~ 4s',
        summaryOutcomeText: '待进入主界面',
        heroBadges: ['日常启动', '复用本机组件', 'LIVE'],
        statusLabel: '进行中',
        progressPrefix: '当前步骤',
        progressEmphasis: '检查 程序签名',
        progressSuffix: '',
        primaryCtaLabel: '进入主界面',
        guards: commonGuards,
        footer: '窗口大小会随上次关闭状态恢复。',
        retry: { title: '重装组件', copy: '修复本机组件', action: 'repair_runtime' }
      },
      launch_ready: {
        tone: 'ready',
        modeTag: '日常启动',
        modeHint: '复用本机组件',
        brandTitle: '已完成启动检查',
        brandCopy: '正在进入主界面。',
        sceneTitleText: '已完成启动检查',
        sceneCopyText: 'App、本机组件和后台服务均已完成检查。',
        sessionInlineText: '日常启动',
        summarySessionTypeText: '日常启动',
        summaryRuntimeStrategyText: '复用本机组件',
        summaryThirdLabelText: '结果',
        summaryBackendModeText: '已就绪',
        summaryOutcomeText: '准备进入主界面',
        heroBadges: ['日常启动', '复用本机组件', '已就绪'],
        statusLabel: '已就绪',
        progressPrefix: '启动检查已完成',
        progressEmphasis: '正在进入主界面',
        progressSuffix: '',
        primaryCtaLabel: '进入主界面',
        guards: commonGuards,
        footer: '窗口大小会随上次关闭状态恢复。',
        retry: { title: '重装组件', copy: '修复本机组件', action: 'repair_runtime' }
      },
      install: {
        modeTag: '首次准备',
        modeHint: '部署本机组件',
        brandTitle: '准备本机组件',
        brandCopy: '校验离线包 · 写入共享 runtime · 启动服务',
        sceneTitleText: '首次准备',
        sceneCopyText: '部署 runtime、jar、python。',
        sessionInlineText: '首次准备',
        summarySessionTypeText: '首次准备',
        summaryRuntimeStrategyText: '部署并校验 runtime',
        summaryBackendModeText: '部署后启动',
        summaryOutcomeText: '进入主界面',
        heroBadges: ['离线包', '共享组件', '无需命令行'],
        guards: commonGuards,
        footer: '离线包内置 runtime，安装后可无网启动。',
        retry: { title: '重装组件', copy: '修复本机组件', action: 'repair_runtime' }
      },
      repair: {
        modeTag: '组件修复',
        modeHint: '重建 runtime',
        brandTitle: '修复本机组件',
        brandCopy: '清理异常标记 · 重建 runtime · 保留数据',
        sceneTitleText: '组件修复',
        sceneCopyText: '只处理损坏或不完整组件。',
        sessionInlineText: '组件修复',
        summarySessionTypeText: '组件修复',
        summaryRuntimeStrategyText: '重建异常组件',
        summaryBackendModeText: '修复后启动',
        summaryOutcomeText: '返回主界面',
        heroBadges: ['修复', '保留数据', '保留日志'],
        guards: commonGuards,
        footer: '修复不删除用户数据。',
        retry: { title: '重装组件', copy: '修复本机组件', action: 'repair_runtime' }
      },
      update: {
        modeTag: '版本更新',
        modeHint: '下载并重开',
        brandTitle: '更新星阙',
        brandCopy: '下载 · 校验 · 替换程序 · 重新打开',
        sceneTitleText: '应用更新',
        sceneCopyText: '按更新清单替换程序与组件。',
        sessionInlineText: '版本更新',
        summarySessionTypeText: '版本更新',
        summaryRuntimeStrategyText: '按更新清单校验',
        summaryBackendModeText: '替换后重开',
        summaryOutcomeText: '进入新版本',
        heroBadges: ['更新清单', '签名校验', '重新启动'],
        guards: commonGuards,
        footer: '更新只替换清单资产。',
        retry: { title: '重装组件', copy: '修复本机组件', action: 'repair_runtime' }
      },
      error: {
        tone: 'error',
        modeTag: 'Needs attention',
        modeHint: '需要重建',
        brandTitle: '组件校验未通过',
        brandCopy: '本机组件损坏或不完整，重建一次即可恢复，个人数据不受影响',
        sceneTitleText: '需要处理',
        sceneCopyText: '优先显示可执行恢复动作。',
        sessionInlineText: '需要处理',
        summarySessionTypeText: '日常启动',
        summaryRuntimeStrategyText: 'Runtime 异常',
        summaryThirdLabelText: '结果',
        summaryBackendModeText: '等待修复',
        summaryOutcomeText: '恢复后重试',
        heroBadges: ['出错', '本机组件', '未完成'],
        statusLabel: '未完成',
        progressPrefix: '本机组件',
        progressEmphasis: 'runtime jar 哈希不符',
        progressSuffix: 'pipeline 已暂停',
        primaryCtaLabel: '重建 Runtime',
        guards: commonGuards,
        footer: '日志已保留 · 重建不会影响用户数据',
        retry: { title: '重装组件', copy: '修复本机组件', action: 'repair_runtime' }
      },
      offline_ready: {
        tone: 'ready',
        modeTag: '离线安装',
        modeHint: '未联网',
        brandTitle: '已就绪',
        brandCopy: '组件均来自离线包，下次打开直接进入主界面',
        sceneTitleText: '离线安装已完成',
        sceneCopyText: '本次未联网，所有组件来自离线包；下次打开将直接进入主界面',
        sessionInlineText: '离线安装已完成',
        summarySessionTypeText: '离线安装',
        summaryRuntimeStrategyText: '复用本机组件',
        summaryThirdLabelText: '来源',
        summaryBackendModeText: `pkg ${APP_VERSION}`,
        summaryOutcomeText: '已完成',
        heroBadges: ['离线安装', '离线包已校验', '已就绪'],
        statusLabel: '已就绪',
        progressPrefix: '离线安装已完成',
        progressEmphasis: `组件 ${APP_VERSION}`,
        progressSuffix: '下次打开直接进入',
        primaryCtaLabel: '进入主界面',
        guards: commonGuards,
        footer: '离线安装包已自带全部组件 · 窗口大小会沿用上次关闭时的状态',
        retry: { title: '重新安装离线包', copy: '用离线包重装一次', action: 'reinstall_offline_package' }
      },
      offline_review: {
        modeTag: '安装审查',
        modeHint: '先确认再替换',
        brandTitle: '选择替换项',
        brandCopy: '逐项选择替换或保留，确认后再开始',
        sceneTitleText: '离线安装审查',
        sceneCopyText: '只处理勾选为替换的资产。',
        sessionInlineText: '等待审查',
        summarySessionTypeText: '离线审查',
        summaryRuntimeStrategyText: '保留可复用资产',
        summaryBackendModeText: '确认后继续',
        summaryOutcomeText: '按选择执行',
        heroBadges: ['Review', 'Replace', 'Keep'],
        guards: commonGuards,
        footer: '未勾选资产保持不动。',
        retry: { title: '重新安装离线包', copy: 'run offline pkg', action: 'reinstall_offline_package' }
      },
      offline_repair_required: {
        tone: 'error',
        modeTag: 'Needs attention',
        modeHint: '需要重建',
        brandTitle: '组件校验未通过',
        brandCopy: '本机组件损坏或不完整，重建一次即可恢复，个人数据不受影响',
        sceneTitleText: '离线修复',
        sceneCopyText: '首选重新运行离线安装包。',
        sessionInlineText: '需要修复',
        summarySessionTypeText: '离线安装',
        summaryRuntimeStrategyText: 'Runtime 异常',
        summaryThirdLabelText: '结果',
        summaryBackendModeText: '等待修复',
        summaryOutcomeText: '重装后启动',
        heroBadges: ['离线修复', '本机组件', '未完成'],
        statusLabel: '未完成',
        progressPrefix: '本机组件',
        progressEmphasis: 'runtime jar 哈希不符',
        progressSuffix: 'pipeline 已暂停',
        primaryCtaLabel: '重建 Runtime',
        guards: commonGuards,
        footer: '日志已保留 · 重建不会影响用户数据',
        retry: { title: '重新安装离线包', copy: 'run offline pkg', action: 'reinstall_offline_package' }
      },
      update_review: {
        modeTag: '更新确认',
        modeHint: '确认后下载',
        brandTitle: '发现新版本',
        brandCopy: '已比对更新清单，确认后开始替换',
        sceneTitleText: '更新待确认',
        sceneCopyText: '确认前不下载、不替换、不重开。',
        sessionInlineText: '等待确认',
        summarySessionTypeText: '更新确认',
        summaryRuntimeStrategyText: '比对更新清单',
        summaryBackendModeText: '确认后执行',
        summaryOutcomeText: '进入更新事务',
        heroBadges: ['Check only', 'Confirm', 'Update'],
        guards: commonGuards,
        footer: '检查更新不再自动替换。',
        retry: { title: '重新检查更新', copy: '重新比对更新清单', action: 'repair_runtime' }
      }
    };
    return { ...content, ...(variants[key] || variants[currentMode] || variants.launch) };
  }

  function applySupportContent(payload) {
    const content = compactSupportContent(supportContentForPayload(payload), payload);
    if (payload?.kind === 'offline_ready') {
      const runtimeVersion = runtimeVersionForPayload(payload);
      content.summaryBackendModeText = `pkg ${runtimeVersion}`;
      content.progressEmphasis = `runtime ${runtimeVersion}`;
    }
    const inferredTone =
      content.tone ||
      (payload?.kind === 'offline_ready' || payload?.kind === 'launch_ready'
        ? 'ready'
        : payload?.kind === 'offline_repair_required' || payload?.recoveryKind || currentMode === 'error'
          ? 'error'
          : 'launch');
    applyLauncherTone(inferredTone);
    heroModeTag.innerHTML = `<span class="mode-dot mode-dot--live"></span>${escapeHtml(content.modeTag)}`;
    heroModeHint.textContent = content.modeHint;
    heroTitle.textContent = content.brandTitle;
    heroCopy.textContent = content.brandCopy;
    sceneTitle.textContent = content.sceneTitleText;
    sceneCopy.textContent = content.sceneCopyText;
    sessionInline.textContent = content.sessionInlineText;
    summarySessionType.textContent = content.summarySessionTypeText;
    summaryRuntimeStrategy.textContent = content.summaryRuntimeStrategyText;
    if (summaryThirdLabel) summaryThirdLabel.textContent = content.summaryThirdLabelText || '预计';
    summaryBackendMode.textContent = content.summaryBackendModeText;
    summaryOutcome.textContent = content.summaryOutcomeText;
    heroBadgePrimary.textContent = content.heroBadges[0];
    heroBadgeSecondary.textContent = content.heroBadges[1];
    if (inferredTone === 'ready') {
      setStatusPill('ready', content.statusLabel || content.heroBadges[2] || '已就绪');
    } else if (inferredTone === 'error') {
      setStatusPill('failed', content.statusLabel || content.heroBadges[2] || '未完成');
    } else {
      setStatusPill('live', content.statusLabel || content.heroBadges[2] || '进行中');
    }
    setPrimaryCta(inferredTone !== 'launch', content.primaryCtaLabel);
    if (content.progressPrefix || content.progressEmphasis || content.progressSuffix) {
      setProgressCopy(content.progressPrefix, content.progressEmphasis, content.progressSuffix);
    }
    guardKeyOne.textContent = content.guards[0][0];
    guardValueOne.textContent = content.guards[0][1];
    guardKeyTwo.textContent = content.guards[1][0];
    guardValueTwo.textContent = content.guards[1][1];
    guardKeyThree.textContent = content.guards[2][0];
    guardValueThree.textContent = content.guards[2][1];
    guardKeyFour.textContent = content.guards[3][0];
    guardValueFour.textContent = content.guards[3][1];
    footerNote.textContent = content.footer;
    retryActionTitle.textContent = content.retry.title;
    retryActionCopy.textContent = content.retry.copy;
    retryActionKind = content.retry.action;
    retryBtn.classList.toggle('action-card--secondary', retryActionKind === 'reinstall_offline_package');
    renderLog();
  }

  function preferredModeForState(payload) {
    switch (payload?.kind) {
      case 'offline_ready':
        return 'offline';
      case 'launch_ready':
        return 'launch';
      case 'offline_repair_required':
        return 'error';
      case 'repair_in_progress':
        return 'repair';
      case 'update_review':
      case 'update_in_progress':
        return 'update';
      default:
        return null;
    }
  }

  function inferLogLevel(message) {
    const text = String(message || '').toLowerCase();
    if (/错误|失败|未通过|不符|损坏|error|failed|mismatch|invalid/.test(text)) return 'error';
    if (/警告|warn|偏好读取失败/.test(text)) return 'warn';
    if (/完成|就绪|通过|ok|ready|成功/.test(text)) return 'ok';
    return 'info';
  }

  function normalizeLogEntry(entry) {
    if (entry && typeof entry === 'object') {
      return {
        time: entry.time || nowTime(),
        level: entry.level || inferLogLevel(entry.message),
        message: entry.message || ''
      };
    }
    return {
      time: nowTime(),
      level: inferLogLevel(entry),
      message: String(entry || '')
    };
  }

  function defaultLogEntries() {
    if (currentTone === 'ready') {
      return [
        { time: nowTime(-32), level: 'info', message: '离线包校验通过' },
        { time: nowTime(-16), level: 'ok', message: '本机组件全部就位' },
        { time: nowTime(-1), level: 'ok', message: '后台服务启动完成' }
      ];
    }
    if (currentTone === 'error') {
      return [
        { time: nowTime(-3), level: 'info', message: '启动页已加载' },
        { time: nowTime(-1), level: 'info', message: '开始校验本机组件' },
        { time: nowTime(), level: 'error', message: 'runtime jar 哈希不符' }
      ];
    }
    return [
      { time: nowTime(-2), level: 'info', message: '启动页已加载' },
      { time: nowTime(-1), level: 'info', message: '校验 程序签名' },
      { time: nowTime(), level: 'info', message: '准备检查本机组件' }
    ];
  }

  function renderLog() {
    if (!statusLog) return;
    document.body.classList.toggle('show-full-log', showFullLog);
    const recordedEntries = lines.map(normalizeLogEntry);
    const entries =
      recordedEntries.length >= 3
        ? recordedEntries
        : [...defaultLogEntries().slice(0, Math.max(0, 3 - recordedEntries.length)), ...recordedEntries];
    const visibleEntries = showFullLog ? entries : entries.slice(-8);
    statusLog.innerHTML = visibleEntries
      .map((entry) => {
        const level = entry.level || 'info';
        return `
          <div class="log-row ${level === 'error' ? 'log-row--error' : ''}">
            <span class="log-time">${escapeHtml(entry.time)}</span>
            <span class="log-level log-level--${escapeHtml(level)}">${escapeHtml(level)}</span>
            <span class="log-message">${escapeHtml(entry.message)}</span>
          </div>
        `;
      })
      .join('');
    statusLog.scrollTop = statusLog.scrollHeight;
    const hiddenCount = Math.max(0, entries.length - visibleEntries.length);
    if (toggleLogBtn) {
      toggleLogBtn.textContent = showFullLog
        ? currentTone === 'error'
          ? '收起错误'
          : '收起详情'
        : currentTone === 'error'
          ? '展开错误'
          : '展开详情';
      toggleLogBtn.disabled = entries.length <= 8;
    }
    if (logSummaryNote) {
      logSummaryNote.textContent = showFullLog
        ? '完整日志'
        : hiddenCount > 0
          ? `最近 8 条 / 已收起 ${hiddenCount} 条`
          : `最近 ${visibleEntries.length} 条`;
    }
  }

  function pushLine(line) {
    lines.push(normalizeLogEntry(line));
    while (lines.length > 40) lines.shift();
    renderLog();
  }

  function renderBlockingIssues(issues) {
    if (!issues?.length) {
      reviewBlocking.classList.add('hidden');
      reviewBlocking.innerHTML = '';
      return;
    }
    reviewBlocking.classList.remove('hidden');
    reviewBlocking.innerHTML = issues
      .map((issue) => `<div class="review-blocking-item">${issue}</div>`)
      .join('');
  }

  function collectReviewDecisions() {
    return Array.from(reviewItems.querySelectorAll('[data-review-kind]')).reduce((acc, input) => {
      acc[input.dataset.reviewKind] = input.checked ? 'replace' : 'keep';
      return acc;
    }, {});
  }

  function renderReviewItems(payload) {
    reviewItems.innerHTML = '';
    payload.items.forEach((item) => {
      const row = document.createElement('label');
      row.className = 'review-item';
      const selected = (currentReviewDecisions[item.kind] || payload.defaultSelections[item.kind]) === 'replace';
      row.innerHTML = `
        <div class="review-item-main">
          <div class="review-item-topline">
            <div class="review-item-title">${item.label}</div>
            <div class="review-item-badges">
              <span class="review-badge review-badge--state">${toTitleCase(item.state)}</span>
              ${item.replaceRecommended ? '<span class="review-badge review-badge--accent">推荐替换</span>' : '<span class="review-badge">建议保留</span>'}
              ${item.requiresAdmin ? '<span class="review-badge">需要管理员</span>' : ''}
            </div>
          </div>
          <div class="review-item-copy">${item.details}</div>
          <pre class="review-item-path">${item.path}</pre>
        </div>
        <div class="review-item-choice">
          <span>替换</span>
          <input type="checkbox" data-review-kind="${item.kind}" ${selected ? 'checked' : ''} />
        </div>
      `;
      reviewItems.appendChild(row);
    });
    reviewItems.querySelectorAll('[data-review-kind]').forEach((input) => {
      input.addEventListener('change', () => {
        currentReviewDecisions = collectReviewDecisions();
      });
    });
    currentReviewDecisions = collectReviewDecisions();
  }

  function hideRecoveryPanel() {
    currentErrorPayload = null;
    recoveryPanel.classList.add('hidden');
    delete recoveryPanel.dataset.stateKind;
    recoveryPrimaryBtn.classList.add('hidden');
    recoverySecondaryActions.innerHTML = '';
    recoveryRecommendation.classList.add('hidden');
    recoveryInstallSource.classList.add('hidden');
    recoveryRawError.textContent = '当前没有额外技术细节。';
    recoveryDetails.open = false;
  }

  function renderStatePanel(payload, { explicit = false } = {}) {
    currentStatePayload = payload;
    hasExplicitState = explicit;
    statePanel.classList.remove('hidden');
    statePanel.dataset.stateKind = payload.kind || '';
    stateBadge.textContent = payload.badge || MODE_CONFIG[currentMode]?.tag || '状态';
    stateTitle.textContent = payload.title || '这台 Mac 会在准备完成后自动进入主界面';
    stateSummary.textContent = payload.summary || '';
    stateDetail.textContent = payload.detail || '';
    if (payload.installSource) {
      stateInstallSource.textContent = sourceLabel(payload.installSource);
      stateInstallSource.classList.remove('hidden');
    } else {
      stateInstallSource.classList.add('hidden');
      stateInstallSource.textContent = '';
    }
    if (payload.recommendation) {
      stateRecommendation.textContent = payload.recommendation;
      stateRecommendation.classList.remove('hidden');
    } else {
      stateRecommendation.classList.add('hidden');
      stateRecommendation.textContent = '';
    }
  }

  async function runLauncherAction(action) {
    if (!action) return;
    await invoke('perform_launcher_action', { action });
  }

  function renderRecoveryPanel(payload) {
    currentErrorPayload = payload;
    recoveryPanel.classList.remove('hidden');
    recoveryPanel.dataset.stateKind = payload.kind || '';
    recoveryBadge.textContent = payload.badge || '需要处理';
    recoveryTitle.textContent = payload.title || '这次准备没有按预期完成';
    recoverySummary.textContent = payload.summary || '';
    recoveryDetail.textContent = payload.detail || '';
    if (payload.installSource) {
      recoveryInstallSource.textContent = sourceLabel(payload.installSource);
      recoveryInstallSource.classList.remove('hidden');
    } else {
      recoveryInstallSource.classList.add('hidden');
      recoveryInstallSource.textContent = '';
    }
    if (payload.recommendation) {
      recoveryRecommendation.textContent = payload.recommendation;
      recoveryRecommendation.classList.remove('hidden');
    } else {
      recoveryRecommendation.classList.add('hidden');
      recoveryRecommendation.textContent = '';
    }
    if (payload.primaryAction) {
      recoveryPrimaryBtn.textContent = ACTION_LABELS[payload.primaryAction] || '继续处理';
      recoveryPrimaryBtn.classList.remove('hidden');
      recoveryPrimaryBtn.onclick = () => runLauncherAction(payload.primaryAction);
    } else {
      recoveryPrimaryBtn.classList.add('hidden');
      recoveryPrimaryBtn.onclick = null;
    }
    recoverySecondaryActions.innerHTML = '';
    (payload.secondaryActions || []).forEach((action) => {
      const button = document.createElement('button');
      button.className = 'toolbar-button toolbar-button--ghost';
      button.textContent = ACTION_LABELS[action] || action;
      button.addEventListener('click', () => {
        runLauncherAction(action);
      });
      recoverySecondaryActions.appendChild(button);
    });
    recoveryRawError.textContent = payload.rawError || '当前没有额外技术细节。';
  }

  function setLauncherState(payload) {
    if (!payload) {
      const fallback = fallbackStateForMode(currentMode);
      renderStatePanel(fallback, { explicit: false });
      applySupportContent(fallback);
      return;
    }
    if (payload.kind === 'offline_ready') {
      payload = {
        ...payload,
        badge: '已就绪',
        title: '离线安装已完成',
        summary: '本次未联网，所有组件来自离线包；下次打开将直接进入主界面',
        detail: '当前步骤：—',
        recommendation: null,
        installSource: payload.installSource || 'pkg_offline'
      };
    }
    const preferredMode = preferredModeForState(payload);
    if (preferredMode) {
      const previousExplicit = hasExplicitState;
      hasExplicitState = false;
      applyMode(preferredMode);
      hasExplicitState = previousExplicit;
    }
    currentStatePayload = payload;
    if (payload.kind === 'offline_repair_required' || payload.recoveryKind) {
      applyMode('error');
      renderStatePanel(payload, { explicit: true });
      currentErrorPayload = payload;
      hideRecoveryPanel();
      applySupportContent(payload);
      setProgress(26, payload.rawError || payload.detail || 'runtime jar 哈希不符');
      return;
    }
    hideRecoveryPanel();
    renderStatePanel(payload, { explicit: true });
    applySupportContent(payload);
    if (payload.kind === 'offline_ready') {
      setProgress(100, '—');
    } else if (payload.kind === 'launch_ready') {
      setProgress(100, payload.currentStep || '准备进入主界面');
    }
  }

  function presentReview(payload) {
    currentReviewPayload = payload;
    currentReviewDecisions = { ...(payload.defaultSelections || {}) };
    assetReviewPanel.classList.remove('hidden');
    reviewIntro.textContent = `${modeToLabel(payload.mode)}已就绪。勾选你想替换的资产，未勾选的内容会尽量保留。`;
    reviewCancelBtn.textContent = payload.mode === 'update' ? '稍后再说' : '取消';
    reviewContinueBtn.textContent = payload.mode === 'update' ? '开始更新' : '继续';
    renderBlockingIssues(payload.blockingIssues || []);
    renderReviewItems(payload);
    applyMode(payload.mode);
    setProgress(12, `等待你确认${modeToLabel(payload.mode)}`);
    pushLine(`已打开${modeToLabel(payload.mode)}，等待你确认要替换的资产。`);
  }

  function clearReview() {
    currentReviewPayload = null;
    currentReviewDecisions = {};
    assetReviewPanel.classList.add('hidden');
    reviewItems.innerHTML = '';
    reviewCancelBtn.textContent = '取消';
    reviewContinueBtn.textContent = '继续';
    renderBlockingIssues([]);
  }

  function resolvePhase(pct) {
    const phases = MODE_CONFIG[currentMode]?.phases || MODE_CONFIG.launch.phases;
    if (pct >= 100) return { step: 4, label: currentMode === 'offline' ? '完成' : '完成', complete: true };
    if (pct >= 90) return { step: 4, label: phases[3], complete: false };
    if (pct >= 65) return { step: 3, label: phases[2] };
    if (pct >= 25) return { step: 2, label: phases[1] };
    return { step: 1, label: phases[0] };
  }

  function renderSteps(activeStep, completeAll = false, failedStep = null) {
    stepItems.forEach((item) => {
      const step = Number(item.dataset.step || 0);
      const isFailed = failedStep === step;
      const isComplete = completeAll || (!failedStep && step < activeStep) || (failedStep && step < failedStep);
      const isActive = !completeAll && !failedStep && step === activeStep;
      const isHighlight = completeAll && step === 4;
      item.classList.toggle('is-active', isActive);
      item.classList.toggle('is-complete', isComplete);
      item.classList.toggle('is-failed', isFailed);
      item.classList.toggle('is-highlight', isHighlight);
      const marker = item.querySelector('.step-marker');
      if (marker) {
        if (isComplete || isHighlight) {
          marker.innerHTML = '<svg aria-hidden="true"><use href="#xq-check"></use></svg>';
        } else if (isFailed) {
          marker.innerHTML = '<svg aria-hidden="true"><use href="#xq-x"></use></svg>';
        } else {
          marker.innerHTML = '';
        }
      }
      const desc = item.querySelector('.step-desc');
      if (desc) {
        if (completeAll) {
          desc.textContent = step === 4 ? 'handoff 就绪' : '已完成';
        } else if (isFailed) {
          desc.textContent = 'jar hash mismatch';
        } else if (isComplete) {
          desc.textContent = '已完成';
        } else if (isActive) {
          desc.textContent = '进行中';
        } else if (failedStep && step > failedStep) {
          desc.textContent = '未执行';
        } else {
          desc.textContent = '等待';
        }
      }
    });
  }

  function renderMilestones(pct, failedStep = null, completeAll = false) {
    milestones.forEach((item) => {
      const step = Number(item.dataset.milestone || 0);
      const complete = completeAll || (!failedStep && pct >= [0, 33, 66, 100][step - 1]) || (failedStep && step < failedStep);
      item.classList.toggle('is-complete', complete);
      item.classList.toggle('is-active', !completeAll && !failedStep && step === resolvePhase(pct).step);
      item.classList.toggle('is-failed', failedStep === step);
    });
    phaseItems.forEach((item) => {
      const step = Number(item.dataset.phaseStep || 0);
      const complete = completeAll || (!failedStep && pct >= [0, 33, 66, 100][step - 1]) || (failedStep && step < failedStep);
      item.classList.toggle('is-complete', complete);
      item.classList.toggle('is-active', !completeAll && !failedStep && step === resolvePhase(pct).step);
      item.classList.toggle('is-failed', failedStep === step);
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
    const currentPct = Number(progressPct.textContent.replace('%', '')) || 0;
    const phase = resolvePhase(currentPct);
    phaseLabel.textContent = progressIsIndeterminate
      ? '接收中'
      : phase.label;
    renderSteps(phase.step, Boolean(phase.complete));
    applySupportContent(currentStatePayload && hasExplicitState ? currentStatePayload : fallbackStateForMode(nextMode));
    if (!hasExplicitState) {
      renderStatePanel(fallbackStateForMode(nextMode), { explicit: false });
    }
  }

  function inferMode(message) {
    const text = String(message || '');
    if (!text) return null;
    if (hasExplicitState && currentStatePayload?.kind === 'offline_repair_required') {
      return 'error';
    }
    if (
      hasExplicitState &&
      currentStatePayload?.kind === 'offline_ready' &&
      /离线安装|本次不会联网下载|Trusted pkg|Ready/.test(text)
    ) {
      return 'offline';
    }
    if (/更新|替换应用|重开/.test(text)) return 'update';
    if (/修复|重装/.test(text)) return 'repair';
    if (
      /下载运行环境|准备安装运行环境|解压运行环境|运行环境安装完成|准备本机组件|部署本机组件|本机组件已准备完成|离线安装已自带完整本机组件/.test(
        text
      )
    ) {
      return currentMode === 'repair' ? 'repair' : 'install';
    }
    if (/检测到运行环境|检测到本机组件|正在检查安装配置|启动本地服务|本地服务已就绪/.test(text)) {
      return currentMode === 'update' ? 'update' : currentMode === 'repair' ? 'repair' : 'launch';
    }
    return null;
  }

  function setProgress(pct, text, options = {}) {
    const indeterminate = Boolean(options.indeterminate);
    const numericPct = Number(pct);
    const basePct = Number(progressPct.textContent.replace('%', '')) || 0;
    const clamped = Number.isFinite(numericPct)
      ? Math.max(0, Math.min(100, numericPct))
      : basePct;
    const inferredMode = inferMode(text);
    if (inferredMode) applyMode(inferredMode);
    const phase = resolvePhase(clamped);
    const failedStep = currentTone === 'error' ? 2 : null;
    // indeterminate=正在等本地服务就绪(心跳每秒刷新此态)。此刻服务尚未真就绪,绝不能把流水线全标完成
    // 或亮 Ready —— 否则用户看到「全绿+✓Ready+进入主界面」却进不去(真就绪只经 __horosaReady 的
    // 非 indeterminate setProgress(100) 路径)。故 indeterminate 时强制「进行中」展示。
    const completeAll = !indeterminate && (currentTone === 'ready' || Boolean(phase.complete));
    if (indeterminate && currentTone !== 'error') {
      setStatusPill('live', '启动中');
    }
    progressIsIndeterminate = indeterminate;
    if (progressTrack) {
      progressTrack.classList.toggle('is-indeterminate', indeterminate);
    }
    progressFill.style.width = indeterminate ? '38%' : `${clamped}%`;
    setProgressNumber(indeterminate ? '接收中' : clamped);
    phaseLabel.textContent = indeterminate ? '接收中' : phase.label;
    renderSteps(failedStep || phase.step, completeAll, failedStep);
    renderMilestones(clamped, failedStep, completeAll);
    if (currentTone === 'ready' && clamped >= 100) {
      const runtimeVersion = runtimeVersionForPayload(currentStatePayload);
      setProgressCopy('离线安装已完成', currentMode === 'offline' ? `runtime ${runtimeVersion}` : text || '准备进入主界面', currentMode === 'offline' ? '下次打开直接进入' : '');
    } else if (currentTone === 'error') {
      const message = text && text !== '这次准备没有按预期完成' ? text : 'runtime jar 哈希不符';
      setProgressCopy('本机组件', message, 'pipeline 已暂停');
    } else if (text) {
      progressText.textContent = text;
      setProgressCopy('当前步骤', text, '');
    } else if (!indeterminate && clamped >= 100 && currentMode === 'offline') {
      const runtimeVersion = runtimeVersionForPayload(currentStatePayload);
      setProgressCopy('离线安装已完成', `runtime ${runtimeVersion}`, '下次打开直接进入');
    }
  }

  function bindAction(button, handler) {
    if (!button) return;
    button.addEventListener('click', async () => {
      try {
        await handler();
      } catch (error) {
        pushLine(`操作失败：${error.message || error}`);
      }
    });
  }

  async function bootstrapPreferences() {
    try {
      const payload = await invoke('load_preferences_payload');
      document.body.classList.toggle(
        'compact-layout',
        Boolean(payload?.preferences?.compactLauncherLayout)
      );
    } catch (error) {
      if (window.__TAURI__ || window.__TAURI_INTERNALS__) {
        pushLine({ level: 'warn', message: '无法读取偏好设置，继续使用默认布局。' });
      }
    }
  }

  window.__horosaMode = function (mode) {
    applyMode(mode);
  };

  window.__horosaState = function (payload) {
    setLauncherState(payload);
  };

  window.__horosaStatus = function (message) {
    const inferredMode = inferMode(message);
    if (inferredMode) applyMode(inferredMode);
    pushLine(message);
  };

  window.__horosaProgress = function (pct, message, indeterminate) {
    setProgress(pct, message, { indeterminate: Boolean(indeterminate) });
    if (message) pushLine(message);
  };

  window.__horosaError = function (payload) {
    const normalized =
      typeof payload === 'string'
        ? {
            badge: '需要处理',
            title: '这次准备没有按预期完成',
            summary: '星阙 还没有准备好，但当前数据和诊断入口都已经保留。',
            detail: '你可以先查看诊断信息，必要时再重新准备本机组件。',
            recommendation: '完整错误已经放到技术细节里，避免直接打断当前恢复流程。',
            recoveryKind: 'generic_failure',
            primaryAction: 'open_diagnostics',
            secondaryActions: ['reveal_data', 'reveal_runtime'],
            rawError: payload
          }
        : payload;
    applyMode('error');
    setLauncherState(normalized);
    pushLine({
      level: 'error',
      message: normalized.rawError || normalized.detail || normalized.summary || normalized.title || '需要处理'
    });
  };

  window.__horosaReady = function (url) {
    currentErrorPayload = null;
    hideRecoveryPanel();
    currentStatePayload = null;
    hasExplicitState = false;
    applyMode('launch');
    setProgress(100, '准备进入主界面');
    const readyPayload = {
      kind: 'launch_ready',
      badge: '已就绪',
      title: '已准备进入主界面',
      summary: 'App、本机组件和后台服务均已完成检查。',
      detail: '正在切换到主界面。',
      recommendation: null,
      installSource: null
    };
    renderStatePanel(readyPayload, { explicit: false });
    applySupportContent(readyPayload);
    pushLine('星阙 已准备完成，正在进入主界面…');
    setTimeout(() => {
      window.location.replace(url);
    }, 450);
  };

  window.__horosaPresentReview = function (payload) {
    presentReview(payload);
  };

  window.__horosaClearReview = function () {
    clearReview();
  };

  function replayPendingState() {
    if (window.__horosaPendingStatePayload) {
      window.__horosaState(window.__horosaPendingStatePayload);
    }
    if (window.__horosaPendingReviewPayload) {
      window.__horosaPresentReview(window.__horosaPendingReviewPayload);
    }
    if (window.__horosaPendingMode) {
      window.__horosaMode(window.__horosaPendingMode);
    }
    if (window.__horosaPendingProgress) {
      window.__horosaProgress(
        window.__horosaPendingProgress.pct,
        window.__horosaPendingProgress.message,
        window.__horosaPendingProgress.indeterminate
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

  bindAction(openPreferencesBtn, () => invoke('open_preferences_window_command'));
  bindAction(openDiagnosticsBtn, () => invoke('open_diagnostics_window_command'));
  bindAction(openDataBtn, () => invoke('reveal_special_path', { kind: 'data' }));
  bindAction(openRuntimeBtn, () => invoke('reveal_special_path', { kind: 'runtime' }));
  bindAction(primaryCtaBtn, () => {
    if (currentTone === 'error') {
      if (retryActionKind === 'reinstall_offline_package') {
        return runLauncherAction('reinstall_offline_package');
      }
      return invoke('trigger_runtime_repair_command');
    }
    if (window.__horosaPendingReadyUrl) {
      window.location.replace(window.__horosaPendingReadyUrl);
      return Promise.resolve();
    }
    pushLine({ level: 'ok', message: '主界面切换已就绪' });
    return Promise.resolve();
  });
  bindAction(retryBtn, () => {
    if (retryActionKind === 'reinstall_offline_package') {
      return runLauncherAction('reinstall_offline_package');
    }
    return invoke('trigger_runtime_repair_command');
  });
  bindAction(toggleLogBtn, async () => {
    showFullLog = !showFullLog;
    renderLog();
  });
  bindAction(reviewCancelBtn, () =>
    invoke('commit_asset_review', {
      request: {
        mode: currentReviewPayload?.mode,
        decisions: currentReviewDecisions,
        cancelled: true
      }
    })
  );
  bindAction(reviewContinueBtn, async () => {
    if (!currentReviewPayload) return;
    const result = await invoke('commit_asset_review', {
      request: {
        mode: currentReviewPayload.mode,
        decisions: currentReviewDecisions,
        cancelled: false
      }
    });
    renderBlockingIssues(result?.blockingIssues || []);
    if (result?.allowed) {
      pushLine('安装审查已确认，正在继续执行。');
    }
  });

  applyMode('launch');
  setProgress(8, '检查 程序签名');
  renderLog();
  bootstrapPreferences();
  replayPendingState();
})();
