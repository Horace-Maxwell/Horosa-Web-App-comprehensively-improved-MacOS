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
  const summaryBackendMode = document.getElementById('summaryBackendMode');
  const summaryOutcome = document.getElementById('summaryOutcome');
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

  async function invoke(cmd, args) {
    if (window.__TAURI__?.core?.invoke) {
      return window.__TAURI__.core.invoke(cmd, args);
    }
    if (window.__TAURI_INTERNALS__?.invoke) {
      return window.__TAURI_INTERNALS__.invoke(cmd, args);
    }
    throw new Error('Tauri invoke bridge unavailable');
  }

  const MODE_CONFIG = {
    launch: {
      tag: '日常启动',
      hint: '复用本机组件',
      title: '星阙 启动中',
      copy: 'App 2.0.0 / runtime1 / arm64',
      sceneTitle: '日常启动',
      sceneCopy: '检查 app、runtime、backend、chartpy。',
      summarySessionType: '日常启动',
      summaryRuntimeStrategy: '复用现有 runtime',
      summaryBackendMode: '后台启动',
      summaryOutcome: '进入主界面',
      sessionInline: '日常启动',
      phases: ['检查安装', '确认组件', '启动服务', '进入主界面']
    },
    install: {
      tag: '首次准备',
      hint: '部署 runtime',
      title: '准备本机组件',
      copy: '校验离线包 · 写入共享 runtime · 启动服务',
      sceneTitle: '首次准备',
      sceneCopy: '部署 runtime、jar、python。',
      summarySessionType: '首次准备',
      summaryRuntimeStrategy: '部署并校验 runtime',
      summaryBackendMode: '部署后启动',
      summaryOutcome: '进入主界面',
      sessionInline: '首次准备',
      phases: ['检查安装', '部署组件', '启动服务', '进入主界面']
    },
    repair: {
      tag: '组件修复',
      hint: '重建 runtime',
      title: '修复本机组件',
      copy: '清理异常标记 · 重建 runtime · 保留数据',
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
      copy: '下载 · 校验 · 替换 app · 重开',
      sceneTitle: '应用更新',
      sceneCopy: '按 manifest 替换 app/runtime。',
      summarySessionType: '版本更新',
      summaryRuntimeStrategy: '按 manifest 校验',
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
          summary: 'runtime、jar、python 将写入共享位置。',
          detail: '完成后启动 backend 与 chartpy。',
          recommendation: null,
          installSource: null
        };
      case 'repair':
        return {
          kind: 'repair_in_progress',
          badge: '组件修复',
          title: '重建异常组件',
          summary: '保留用户数据与日志。',
          detail: '只替换损坏或不完整的 runtime 内容。',
          recommendation: null,
          installSource: null
        };
      case 'update':
        return {
          kind: 'update_in_progress',
          badge: '版本更新',
          title: '按 manifest 更新',
          summary: '下载、校验、替换、重开。',
          detail: '用户数据不参与替换。',
          recommendation: null,
          installSource: null
        };
      default:
        return {
          kind: 'launch_ready',
          badge: '启动中心',
          title: '准备进入主界面',
          summary: '等待 runtime 检查结果。',
          detail: '服务未就绪前不会切换窗口。',
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
          brandCopy: '首次准备会在 app 内安静完成，不需要你理解脚本、缓存或内部资产。',
          sceneTitleText: '首次准备',
          sceneCopyText: '如果当前机器缺少所需内容，星阙 会在 app 内完成准备、校验和切换。',
          sessionInlineText: '首次准备',
          summarySessionTypeText: '首次准备',
          summaryRuntimeStrategyText: '按需准备并接管本机组件',
          summaryBackendModeText: '准备完成后自动启动所需服务',
          summaryOutcomeText: '直接进入主界面',
          heroBadges: ['首次准备在 app 内完成', '只在需要时准备组件', '普通用户无需手工处理'],
          guards: [
            ['准备方式', '只有确认需要的内容才会被准备或替换。'],
            ['安装审查', '先看清这次会处理什么，再决定是否继续。'],
            ['技术细节', '过程摘要默认收起，避免技术信息抢占主视图。'],
            ['数据目录', '用户数据与运行日志不会在准备时被删除。']
          ],
          footer: '星阙 会尽量把首次准备表现成标准 Mac app 流程，而不是工程安装器。',
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
          heroBadges: ['修复动作在 app 内完成', '日志与诊断入口已保留', '修复后自动回到主界面'],
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
          modeHint: '快速检查并进入主界面',
          brandTitle: '正在准备 星阙',
          brandCopy: '日常打开会优先复用已经准备好的本机组件，并在后台启动所需服务后直接进入主界面。',
          sceneTitleText: '日常启动',
          sceneCopyText: '如果这台 Mac 已经准备好所需内容，你只会看到短暂的检查过程。',
          sessionInlineText: '日常启动',
          summarySessionTypeText: '日常启动',
          summaryRuntimeStrategyText: '优先复用已有组件',
          summaryBackendModeText: '已就绪后自动启动所需服务',
          summaryOutcomeText: '自动进入主界面',
          heroBadges: ['DMG 主入口', '首次准备在 app 内完成', '后台更新与重开'],
          guards: [
            ['应用更新', '下载完成后先替换 `.app`，再自动重开。'],
            ['安装审查', '先列出已安装内容，再由你决定这次要替换哪些资产。'],
            ['启动方式', '日常打开会优先复用已准备好的内容，尽量减少打扰。'],
            ['数据目录', '用户数据与运行日志不会在更新时被删除。']
          ],
          footer: '星阙 现在会优先表现成一个标准的 Mac app：主入口是 DMG，首次准备在 app 内完成，遇到异常时提供 Finder、日志和重试入口。',
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
          modeHint: '本次不会联网下载',
          brandTitle: '这台 Mac 已准备好',
          brandCopy: '离线安装已经把所需本机组件准备到位，日常打开会直接进入主界面。',
          sceneTitleText: '离线安装已完成',
          sceneCopyText: '当前机器已经准备好所需内容；如果只是日常打开，你只会看到短暂检查。',
          sessionInlineText: '可直接使用',
          summarySessionTypeText: '离线安装完成',
          summaryRuntimeStrategyText: '复用离线安装已准备好的本机组件',
          summaryBackendModeText: '已就绪后自动启动所需服务',
          summaryOutcomeText: '直接进入主界面',
          heroBadges: ['离线安装已完成', '本次不会联网下载', '可直接打开使用'],
          guards: [
            ['首选恢复', '如果后续发现本机组件损坏，请直接重新安装离线包。'],
            ['本机组件', '离线安装包已经把需要的内容准备到共享位置。'],
            ['已安装内容', '你仍然可以在 Finder 查看数据目录和本机组件位置。'],
            ['数据安全', '用户数据和日志不会因为离线路径而被额外清理。']
          ],
          footer: '离线路径已经准备完成，日常打开会直接进入主界面；如需修复，请重新安装离线包。',
          retry: {
            title: '重新安装离线包',
            copy: '当离线路径损坏或需要重新接管时，重新运行离线安装包',
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
      ['App', '签名校验后替换。'],
      ['Runtime', '损坏或版本不符才重建。'],
      ['Logs', '失败时保留。'],
      ['Data', '更新不删除用户数据。']
    ];
    const variants = {
      launch: {
        modeTag: '日常启动',
        modeHint: '复用本机组件',
        brandTitle: '星阙 启动中',
          brandCopy: 'App 2.0.0 / runtime1 / arm64',
        sceneTitleText: '日常启动',
        sceneCopyText: '检查 app、runtime、backend、chartpy。',
        sessionInlineText: '日常启动',
        summarySessionTypeText: '日常启动',
        summaryRuntimeStrategyText: '复用现有 runtime',
        summaryBackendModeText: '后台启动',
        summaryOutcomeText: '进入主界面',
        heroBadges: ['DMG', 'Runtime', 'Backend'],
        guards: commonGuards,
        footer: '窗口大小会随上次关闭状态恢复。',
        retry: { title: '重装组件', copy: 'repair runtime', action: 'repair_runtime' }
      },
      install: {
        modeTag: '首次准备',
        modeHint: '部署 runtime',
        brandTitle: '准备本机组件',
        brandCopy: '校验离线包 · 写入共享 runtime · 启动服务',
        sceneTitleText: '首次准备',
        sceneCopyText: '部署 runtime、jar、python。',
        sessionInlineText: '首次准备',
        summarySessionTypeText: '首次准备',
        summaryRuntimeStrategyText: '部署并校验 runtime',
        summaryBackendModeText: '部署后启动',
        summaryOutcomeText: '进入主界面',
        heroBadges: ['Offline pkg', 'Shared runtime', 'No terminal'],
        guards: commonGuards,
        footer: '离线包内置 runtime，安装后可无网启动。',
        retry: { title: '重装组件', copy: 'repair runtime', action: 'repair_runtime' }
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
        heroBadges: ['Repair', 'Keep data', 'Keep logs'],
        guards: commonGuards,
        footer: '修复不删除用户数据。',
        retry: { title: '重装组件', copy: 'repair runtime', action: 'repair_runtime' }
      },
      update: {
        modeTag: '版本更新',
        modeHint: '下载并重开',
        brandTitle: '更新星阙',
        brandCopy: '下载 · 校验 · 替换 app · 重开',
        sceneTitleText: '应用更新',
        sceneCopyText: '按 manifest 替换 app/runtime。',
        sessionInlineText: '版本更新',
        summarySessionTypeText: '版本更新',
        summaryRuntimeStrategyText: 'manifest 校验',
        summaryBackendModeText: '替换后重开',
        summaryOutcomeText: '进入新版本',
        heroBadges: ['Manifest', 'Signature', 'Restart'],
        guards: commonGuards,
        footer: '更新只替换清单资产。',
        retry: { title: '重装组件', copy: 'repair runtime', action: 'repair_runtime' }
      },
      error: {
        modeTag: '需要处理',
        modeHint: '等待恢复动作',
        brandTitle: '启动中断',
        brandCopy: '查看诊断 · 保留日志 · 执行恢复',
        sceneTitleText: '需要处理',
        sceneCopyText: '优先显示可执行恢复动作。',
        sessionInlineText: '需要处理',
        summarySessionTypeText: '流程中断',
        summaryRuntimeStrategyText: '保留现场',
        summaryBackendModeText: '服务未就绪',
        summaryOutcomeText: '恢复后重试',
        heroBadges: ['Diagnostics', 'Logs', 'Recover'],
        guards: commonGuards,
        footer: '错误详情保留在诊断中心。',
        retry: { title: '重装组件', copy: 'repair runtime', action: 'repair_runtime' }
      },
      offline_ready: {
        modeTag: '离线安装',
        modeHint: '无网可用',
        brandTitle: '离线包已就绪',
        brandCopy: 'App · Shared runtime · Local services',
        sceneTitleText: '离线安装完成',
        sceneCopyText: '复用离线包内置 runtime。',
        sessionInlineText: '可直接使用',
        summarySessionTypeText: '离线安装',
        summaryRuntimeStrategyText: '复用共享 runtime',
        summaryBackendModeText: '后台启动',
        summaryOutcomeText: '进入主界面',
        heroBadges: ['Offline', 'Trusted pkg', 'Ready'],
        guards: commonGuards,
        footer: '离线安装包已包含 runtime。',
        retry: { title: '重新安装离线包', copy: 'run offline pkg', action: 'reinstall_offline_package' }
      },
      offline_review: {
        modeTag: '安装审查',
        modeHint: '先确认再替换',
        brandTitle: '选择替换项',
        brandCopy: 'replace / keep · app · runtime · cache',
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
        modeTag: '离线修复',
        modeHint: '重装离线包',
        brandTitle: '离线 runtime 损坏',
        brandCopy: '重新安装 pkg · 重建共享 runtime',
        sceneTitleText: '离线修复',
        sceneCopyText: '首选重新运行离线安装包。',
        sessionInlineText: '需要修复',
        summarySessionTypeText: '离线修复',
        summaryRuntimeStrategyText: '重新接管 runtime',
        summaryBackendModeText: '等待恢复',
        summaryOutcomeText: '重装后启动',
        heroBadges: ['Offline repair', 'Reinstall pkg', 'Keep data'],
        guards: commonGuards,
        footer: '建议重新安装离线包。',
        retry: { title: '重新安装离线包', copy: 'run offline pkg', action: 'reinstall_offline_package' }
      },
      update_review: {
        modeTag: '更新确认',
        modeHint: '确认后下载',
        brandTitle: '发现新版本',
        brandCopy: 'manifest 已比对 · 等待确认',
        sceneTitleText: '更新待确认',
        sceneCopyText: '确认前不下载、不替换、不重开。',
        sessionInlineText: '等待确认',
        summarySessionTypeText: '更新确认',
        summaryRuntimeStrategyText: '比对 manifest',
        summaryBackendModeText: '确认后执行',
        summaryOutcomeText: '进入更新事务',
        heroBadges: ['Check only', 'Confirm', 'Update'],
        guards: commonGuards,
        footer: '检查更新不再自动替换。',
        retry: { title: '重新检查更新', copy: 'check manifest', action: 'repair_runtime' }
      }
    };
    return { ...content, ...(variants[key] || variants[currentMode] || variants.launch) };
  }

  function applySupportContent(payload) {
    const content = compactSupportContent(supportContentForPayload(payload), payload);
    heroModeTag.textContent = content.modeTag;
    heroModeHint.textContent = content.modeHint;
    heroTitle.textContent = content.brandTitle;
    heroCopy.textContent = content.brandCopy;
    sceneTitle.textContent = content.sceneTitleText;
    sceneCopy.textContent = content.sceneCopyText;
    sessionInline.textContent = content.sessionInlineText;
    summarySessionType.textContent = content.summarySessionTypeText;
    summaryRuntimeStrategy.textContent = content.summaryRuntimeStrategyText;
    summaryBackendMode.textContent = content.summaryBackendModeText;
    summaryOutcome.textContent = content.summaryOutcomeText;
    heroBadgePrimary.textContent = content.heroBadges[0];
    heroBadgeSecondary.textContent = content.heroBadges[1];
    heroBadgeTertiary.textContent = content.heroBadges[2];
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
    retryBtn.classList.toggle('action-card--accent', retryActionKind === 'reinstall_offline_package');
  }

  function preferredModeForState(payload) {
    switch (payload?.kind) {
      case 'offline_ready':
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

  function renderLog() {
    document.body.classList.toggle('show-full-log', showFullLog);
    const visibleLines = showFullLog ? lines : lines.slice(-8);
    statusLog.textContent = visibleLines.length ? visibleLines.join('\n') : '等待初始化...';
    statusLog.scrollTop = statusLog.scrollHeight;
    const hiddenCount = Math.max(0, lines.length - visibleLines.length);
    if (toggleLogBtn) {
      toggleLogBtn.textContent = showFullLog ? '收起详细过程' : '展开详细过程';
      toggleLogBtn.disabled = lines.length <= 8;
    }
    if (logSummaryNote) {
      logSummaryNote.textContent = showFullLog
        ? '完整日志'
        : hiddenCount > 0
          ? `最近 8 条 / 已收起 ${hiddenCount} 条`
          : '最近事件';
    }
  }

  function pushLine(line) {
    lines.push(line);
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
    stateBadge.textContent = payload.badge || '启动中心';
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
      renderRecoveryPanel(payload);
      applySupportContent(payload);
      return;
    }
    hideRecoveryPanel();
    renderStatePanel(payload, { explicit: true });
    applySupportContent(payload);
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
    phaseLabel.textContent = progressIsIndeterminate
      ? '接收中'
      : resolvePhase(Number(progressPct.textContent.replace('%', '')) || 0).label;
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
      /离线安装|本次不会联网下载|可直接打开使用/.test(text)
    ) {
      return 'launch';
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
    progressIsIndeterminate = indeterminate;
    if (progressTrack) {
      progressTrack.classList.toggle('is-indeterminate', indeterminate);
    }
    progressFill.style.width = indeterminate ? '38%' : `${clamped}%`;
    progressPct.textContent = indeterminate ? '接收中' : `${Math.round(clamped)}%`;
    phaseLabel.textContent = indeterminate ? '接收中' : phase.label;
    renderSteps(phase.step);
    if (text) {
      progressText.textContent = text;
    }
  }

  function bindAction(button, handler) {
    if (!button) return;
    button.addEventListener('click', async () => {
      try {
        await handler();
      } catch (error) {
        pushLine(`操作失败: ${error.message || error}`);
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
      pushLine('无法读取偏好设置，继续使用默认布局。');
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
    pushLine(`错误: ${normalized.title || normalized.summary || '需要处理'}`);
  };

  window.__horosaReady = function (url) {
    currentErrorPayload = null;
    hideRecoveryPanel();
    currentStatePayload = null;
    hasExplicitState = false;
    applyMode('launch');
    setProgress(100, '星阙 已准备完成');
    renderStatePanel(fallbackStateForMode('launch'), { explicit: false });
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
  setProgress(0, '等待初始化…');
  renderLog();
    pushLine('启动页已加载。');
  bootstrapPreferences();
  replayPendingState();
})();
