(function () {
  const progressFill = document.getElementById('progressFill');
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
      hint: '快速检查并进入主界面',
      title: '正在准备 星阙',
      copy: '日常打开时会优先复用已经准备好的本机组件，并在后台启动服务后直接进入主界面。',
      sceneTitle: '日常启动',
      sceneCopy: '如果这台 Mac 已经准备好所需组件，你只会看到很短暂的检查过程。',
      summarySessionType: '日常启动',
      summaryRuntimeStrategy: '优先复用已有组件',
      summaryBackendMode: '已就绪后自动启动本地服务',
      summaryOutcome: '自动进入主界面',
      sessionInline: '日常启动',
      phases: ['正在检查安装状态', '正在确认本机组件', '正在启动后台服务', '正在进入主界面']
    },
    install: {
      tag: '首次准备',
      hint: '准备并接管本机组件',
      title: '正在为这台 Mac 准备 星阙',
      copy: '当前机器还没有完整组件，星阙 会在 app 内完成准备、校验和切换，然后自动进入主界面。',
      sceneTitle: '首次准备',
      sceneCopy: '首次准备会在 app 内完成，不需要手工运行脚本或理解内部资产。',
      summarySessionType: '首次准备',
      summaryRuntimeStrategy: '按需准备、校验并切换组件',
      summaryBackendMode: '准备完成后自动启动后台服务',
      summaryOutcome: '完成后直接进入主界面',
      sessionInline: '首次准备',
      phases: ['正在检查安装状态', '正在准备与部署组件', '正在启动后台服务', '正在进入主界面']
    },
    repair: {
      tag: '组件修复',
      hint: '重新准备本机组件',
      title: '正在修复 星阙 本机组件',
      copy: '检测到当前组件需要重新整理、替换或手动修复。完成后会自动重新启动并返回主界面。',
      sceneTitle: '本机组件修复',
      sceneCopy: '会先整理现有组件，再按需重新准备新的本机组件。',
      summarySessionType: '组件修复',
      summaryRuntimeStrategy: '清理异常内容并按需重建',
      summaryBackendMode: '修复后重新启动后台服务',
      summaryOutcome: '修复完成后返回主界面',
      sessionInline: '组件修复',
      phases: ['正在检查安装状态', '正在修复本机组件', '正在启动后台服务', '正在进入主界面']
    },
    update: {
      tag: '版本更新',
      hint: '下载并重开新版本',
      title: '正在更新 星阙',
      copy: '新版本会先完成下载和校验，再替换应用、按需更新本机组件，并自动重开回到新的星阙。',
      sceneTitle: '应用更新',
      sceneCopy: '下载与替换都在 app 内完成，用户看到的是更接近标准 Mac app 的更新流程。',
      summarySessionType: '版本更新',
      summaryRuntimeStrategy: '按清单下载并校验更新资产',
      summaryBackendMode: '替换成功后自动重开',
      summaryOutcome: '自动进入新版本',
      sessionInline: '版本更新',
      phases: ['正在准备更新', '正在下载更新资产', '正在替换应用', '正在重开 星阙']
    },
    error: {
      tag: '需要处理',
      hint: '恢复动作优先，技术细节后置',
      title: '星阙 还没有准备完成',
      copy: '当前流程没有顺利完成。你可以先走推荐恢复动作，再按需要查看诊断信息。',
      sceneTitle: '需要处理',
      sceneCopy: '主界面会优先告诉你下一步该做什么，完整细节会放到第二层。',
      summarySessionType: '流程中断',
      summaryRuntimeStrategy: '保留当前状态，等待你决定下一步',
      summaryBackendMode: '后台服务尚未完全就绪',
      summaryOutcome: '处理完成后再重试',
      sessionInline: '需要处理',
      phases: ['正在检查安装状态', '处理中断', '等待修复', '等待重试']
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
          title: '首次准备会在 app 内完成',
          summary: '这一步会尽量保持安静，只在需要时准备本机组件并自动继续。',
          detail: '普通用户不需要理解内部资产、脚本或缓存结构。',
          recommendation: null,
          installSource: null
        };
      case 'repair':
        return {
          kind: 'repair_in_progress',
          badge: '组件修复',
          title: '正在整理并恢复本机组件',
          summary: '会优先保留当前数据，并在准备完成后自动回到主界面。',
          detail: '完整日志仍然保留，但不会再主导当前页面。',
          recommendation: null,
          installSource: null
        };
      case 'update':
        return {
          kind: 'update_in_progress',
          badge: '版本更新',
          title: '正在准备新版本并保持当前数据不变',
          summary: '下载、校验和替换都在 app 内完成，准备好后会自动重开。',
          detail: '只有已确认需要替换的资产会参与本次更新。',
          recommendation: null,
          installSource: null
        };
      default:
        return {
          kind: 'launch_ready',
          badge: '启动中心',
          title: '这台 Mac 会在准备完成后自动进入主界面',
          summary: '日常打开会优先复用已经准备好的内容，只有在首次准备、修复或更新时才会延伸为完整流程。',
          detail: '默认会把技术细节收在第二层，先让你看见当前状态和下一步动作。',
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

  function applySupportContent(payload) {
    const content = supportContentForPayload(payload);
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
      case 'update_in_progress':
        return 'update';
      default:
        return null;
    }
  }

  function renderLog() {
    const visibleLines = showFullLog ? lines : lines.slice(-8);
    statusLog.textContent = visibleLines.length ? visibleLines.join('\n') : '等待星阙初始化…';
    statusLog.scrollTop = statusLog.scrollHeight;
    const hiddenCount = Math.max(0, lines.length - visibleLines.length);
    if (toggleLogBtn) {
      toggleLogBtn.textContent = showFullLog ? '收起详细过程' : '展开详细过程';
      toggleLogBtn.disabled = lines.length <= 8;
    }
    if (logSummaryNote) {
      logSummaryNote.textContent = showFullLog
        ? '当前正在显示完整过程与历史记录。'
        : hiddenCount > 0
          ? `当前只显示最近 8 条摘要，另外还有 ${hiddenCount} 条详细记录已收起。`
          : '当前只显示摘要；完整技术细节会在需要时展开。';
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
    phaseLabel.textContent = resolvePhase(Number(progressPct.textContent.replace('%', '')) || 0).label;
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

  window.__horosaProgress = function (pct, message) {
    setProgress(pct, message);
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
  pushLine('星阙启动中心已加载。');
  bootstrapPreferences();
  replayPendingState();
})();
