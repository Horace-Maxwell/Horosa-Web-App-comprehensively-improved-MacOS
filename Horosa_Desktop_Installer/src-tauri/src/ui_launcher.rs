//! 启动页:状态载荷、覆盖层渲染与各类启动事件。

use super::*;

#[derive(Debug, Clone, Copy, Serialize, Deserialize, PartialEq, Eq)]
#[serde(rename_all = "snake_case")]
pub(crate) enum LauncherStateKind {
    LaunchReady,
    OfflineReady,
    OfflineReview,
    OfflineRepairRequired,
    RepairInProgress,
    UpdateReview,
    UpdateInProgress,
}

#[derive(Debug, Clone, Copy, Serialize, Deserialize, PartialEq, Eq)]
#[serde(rename_all = "snake_case")]
enum RecoveryKind {
    OfflineReinstallRequired,
    RepairAvailable,
    GenericFailure,
}

#[derive(Debug, Clone, Copy, Serialize, Deserialize, PartialEq, Eq)]
#[serde(rename_all = "snake_case")]
pub(crate) enum LauncherActionKind {
    ReinstallOfflinePackage,
    OpenDiagnostics,
    RevealData,
    RevealRuntime,
}

#[derive(Debug, Clone, Serialize, Deserialize)]
#[serde(rename_all = "camelCase")]
pub(crate) struct LauncherStatePayload {
    pub(crate) kind: LauncherStateKind,
    badge: String,
    pub(crate) title: String,
    pub(crate) summary: String,
    pub(crate) detail: String,
    recommendation: Option<String>,
    install_source: Option<InstallSource>,
    recovery_kind: Option<RecoveryKind>,
    primary_action: Option<LauncherActionKind>,
    secondary_actions: Vec<LauncherActionKind>,
    raw_error: Option<String>,
}

pub(crate) fn build_offline_ready_state(config: &ReleaseConfig) -> LauncherStatePayload {
    LauncherStatePayload {
        kind: LauncherStateKind::OfflineReady,
        badge: "离线安装已完成".to_string(),
        title: "这台 Mac 已准备好，可直接打开使用".to_string(),
        summary: "当前离线安装来源已经把所需本机组件准备到位，本次不会联网下载。".to_string(),
        detail: format!(
            "当前安装来源：{}。本机组件版本 {} 已可直接使用；如需修复，请重新安装离线包。",
            source_label(InstallSource::PkgOffline),
            config.runtime_version
        ),
        recommendation: Some(
            "后续日常打开会直接进入主界面，只有在你主动修复或更新时才会继续处理。".to_string(),
        ),
        install_source: Some(InstallSource::PkgOffline),
        recovery_kind: None,
        primary_action: None,
        secondary_actions: vec![
            LauncherActionKind::RevealRuntime,
            LauncherActionKind::RevealData,
        ],
        raw_error: None,
    }
}

pub(crate) fn build_offline_review_state(mode: AssetReviewMode) -> LauncherStatePayload {
    LauncherStatePayload {
        kind: LauncherStateKind::OfflineReview,
        badge: mode.title().to_string(),
        title: "已发现本机已有内容，请决定这次要替换哪些项目".to_string(),
        summary: "这次不会自动覆盖已有资产，只有你勾选为“替换”的内容才会被处理。".to_string(),
        detail: "离线路径下会尽量复用已经可用的本机组件，不会因为审查而自动转为联网准备。"
            .to_string(),
        recommendation: Some("如果这台 Mac 已经能正常使用，通常保留可复用内容就够了。".to_string()),
        install_source: Some(InstallSource::PkgOffline),
        recovery_kind: None,
        primary_action: None,
        secondary_actions: vec![
            LauncherActionKind::OpenDiagnostics,
            LauncherActionKind::RevealRuntime,
        ],
        raw_error: None,
    }
}

pub(crate) fn build_repair_in_progress_state() -> LauncherStatePayload {
    LauncherStatePayload {
        kind: LauncherStateKind::RepairInProgress,
        badge: "组件修复".to_string(),
        title: "正在整理并恢复本机组件".to_string(),
        summary: "星阙 会尽量保留当前数据，并在准备完成后自动回到主界面。".to_string(),
        detail: "技术细节和完整日志仍然可用，但会退到第二层，避免打断当前恢复流程。".to_string(),
        recommendation: None,
        install_source: None,
        recovery_kind: None,
        primary_action: None,
        secondary_actions: vec![],
        raw_error: None,
    }
}

pub(crate) fn build_update_review_state() -> LauncherStatePayload {
    LauncherStatePayload {
        kind: LauncherStateKind::UpdateReview,
        badge: "发现更新".to_string(),
        title: "已获取新版本信息，等待你确认是否开始更新".to_string(),
        summary: "这一步只负责检查和展示结果；只有你明确确认后，才会开始下载与替换。".to_string(),
        detail: "如果你选择稍后再说，本次不会下载任何资产，也不会替换当前 app 或本机组件。"
            .to_string(),
        recommendation: Some("确认开始后，星阙 才会进入下载、校验与重开流程。".to_string()),
        install_source: None,
        recovery_kind: None,
        primary_action: None,
        secondary_actions: vec![],
        raw_error: None,
    }
}

pub(crate) fn build_update_in_progress_state() -> LauncherStatePayload {
    LauncherStatePayload {
        kind: LauncherStateKind::UpdateInProgress,
        badge: "版本更新".to_string(),
        title: "正在准备新版本并保持当前数据不变".to_string(),
        summary: "下载、校验和替换都会在 app 内完成，准备好后会自动重开。".to_string(),
        detail: "只有被确认要替换的 app 或本机组件会参与这次更新。".to_string(),
        recommendation: None,
        install_source: None,
        recovery_kind: None,
        primary_action: None,
        secondary_actions: vec![],
        raw_error: None,
    }
}

fn build_generic_launcher_error(raw_error: &str) -> LauncherStatePayload {
    LauncherStatePayload {
        kind: LauncherStateKind::RepairInProgress,
        badge: "需要处理".to_string(),
        title: "这次准备没有按预期完成".to_string(),
        summary: "星阙 还没有准备好，但当前数据和诊断入口都已经保留。".to_string(),
        detail: "你可以先查看诊断信息，必要时再重新准备本机组件。".to_string(),
        recommendation: Some(
            "如果这是首次启动或刚完成更新，先查看诊断中心通常会更稳妥。".to_string(),
        ),
        install_source: None,
        recovery_kind: Some(RecoveryKind::GenericFailure),
        primary_action: Some(LauncherActionKind::OpenDiagnostics),
        secondary_actions: vec![
            LauncherActionKind::RevealData,
            LauncherActionKind::RevealRuntime,
        ],
        raw_error: Some(raw_error.to_string()),
    }
}

fn build_offline_repair_required_state(
    config: &ReleaseConfig,
    raw_error: &str,
) -> LauncherStatePayload {
    LauncherStatePayload {
        kind: LauncherStateKind::OfflineRepairRequired,
        badge: "离线修复".to_string(),
        title: "本机组件不完整，当前无法继续打开 星阙".to_string(),
        summary: "这台 Mac 之前通过离线安装包完成准备，但当前共享本机组件缺失、损坏或版本不完整。"
            .to_string(),
        detail: format!(
            "请优先重新运行 {}。重新安装会把离线路径需要的本机组件重新接管到位。",
            config.desktop_offline_pkg_name
        ),
        recommendation: Some(
            "重新安装离线包是首选恢复方式；诊断中心和 Finder 入口仍然保留给你排查。".to_string(),
        ),
        install_source: Some(InstallSource::PkgOffline),
        recovery_kind: Some(RecoveryKind::OfflineReinstallRequired),
        primary_action: Some(LauncherActionKind::ReinstallOfflinePackage),
        secondary_actions: vec![
            LauncherActionKind::OpenDiagnostics,
            LauncherActionKind::RevealRuntime,
            LauncherActionKind::RevealData,
        ],
        raw_error: Some(raw_error.to_string()),
    }
}

pub(crate) fn build_launcher_error_payload(
    app: &AppHandle,
    error: &anyhow::Error,
) -> LauncherStatePayload {
    let raw_error = format!("{error:#}");
    let mut payload = 'built: {
        if let Ok(config) = load_release_config(app) {
            if current_install_source(&config) == Some(InstallSource::PkgOffline)
                && !shared_runtime_matches_expected(&config.runtime_version)
                && !user_runtime_matches_expected(app, &config.runtime_version).unwrap_or(false)
            {
                break 'built build_offline_repair_required_state(&config, &raw_error);
            }
        }
        build_generic_launcher_error(&raw_error)
    };
    // 全球用户自助:失败面必须给出日志的确切路径(菜单「打开日志」不一定被发现;
    // 远程求助时用户只要把这个目录打包发来即可定位)。
    if let Ok(dir) = app.path().app_data_dir() {
        payload.detail = format!(
            "{}\n诊断日志目录:{}(菜单栏「打开日志」可直达)",
            payload.detail,
            dir.join("logs").display()
        );
    }
    payload
}

fn escape_js(text: &str) -> String {
    serde_json::to_string(text).unwrap_or_else(|_| "\"\"".to_string())
}

fn overlay_json(value: Option<&str>) -> String {
    value.map(escape_js).unwrap_or_else(|| "null".to_string())
}

fn overlay_bool_json(value: Option<bool>) -> String {
    match value {
        Some(true) => "true".to_string(),
        Some(false) => "false".to_string(),
        None => "null".to_string(),
    }
}

fn emit_overlay(
    window: &WebviewWindow,
    mode: Option<&str>,
    pct: Option<u8>,
    message: Option<&str>,
    error: Option<&str>,
    ready: bool,
    indeterminate: Option<bool>,
) {
    let mode = overlay_json(mode);
    let message = overlay_json(message);
    let error = overlay_json(error);
    let pct = pct
        .map(|value| value.to_string())
        .unwrap_or_else(|| "null".to_string());
    let ready = if ready { "true" } else { "false" };
    let indeterminate = overlay_bool_json(indeterminate);
    let _ = window.eval(&format!(
        r#"
(function () {{
  if (!window.__horosaInlineProgress) {{
    window.__horosaInlineProgress = (function () {{
      const STYLE_ID = 'horosa-inline-progress-style';
      const CARD_ID = 'horosa-inline-progress';
      let hideTimer = null;
      let lastMode = 'launch';
      let lastPct = 0;
      let lastIndeterminate = false;

      function isLauncherPage() {{
        return !!document.querySelector('.launcher-shell');
      }}

      function injectStyle() {{
        if (document.getElementById(STYLE_ID)) return;
        const style = document.createElement('style');
        style.id = STYLE_ID;
        style.textContent = `
          #${{CARD_ID}} {{
            position: fixed;
            top: 18px;
            right: 18px;
            width: min(420px, calc(100vw - 48px));
            z-index: 2147483646;
            padding: 20px 22px 18px;
            border-radius: 18px;
            border: 1px solid rgba(22, 32, 45, 0.08);
            background:
              linear-gradient(180deg, rgba(255,255,255,0.96), rgba(245,248,252,0.92)),
              linear-gradient(135deg, rgba(25,118,210,0.08), rgba(255,255,255,0));
            box-shadow: 0 18px 48px rgba(21, 31, 44, 0.16);
            backdrop-filter: blur(16px);
            color: #182231;
            transform: translateY(-10px) scale(0.96);
            opacity: 0;
            pointer-events: none;
            transition: opacity 180ms ease, transform 180ms ease;
            font-family: "SF Pro Display", "PingFang SC", "Helvetica Neue", sans-serif;
          }}
          #${{CARD_ID}}.is-visible {{
            opacity: 1;
            transform: translateY(0) scale(1);
          }}
          #${{CARD_ID}}[data-tone="update"] {{
            background:
              linear-gradient(180deg, rgba(255,255,255,0.97), rgba(241,251,247,0.93)),
              linear-gradient(135deg, rgba(14,127,99,0.12), rgba(255,255,255,0));
          }}
          #${{CARD_ID}}[data-tone="install"],
          #${{CARD_ID}}[data-tone="repair"] {{
            background:
              linear-gradient(180deg, rgba(255,255,255,0.97), rgba(252,247,239,0.93)),
              linear-gradient(135deg, rgba(179,105,18,0.14), rgba(255,255,255,0));
          }}
          #${{CARD_ID}}[data-tone="error"] {{
            background:
              linear-gradient(180deg, rgba(255,250,248,0.98), rgba(255,244,239,0.95)),
              linear-gradient(135deg, rgba(182,72,38,0.16), rgba(255,255,255,0));
          }}
          #${{CARD_ID}} .hip-head {{
            display: flex;
            align-items: flex-start;
            justify-content: space-between;
            gap: 12px;
          }}
          #${{CARD_ID}} .hip-badge {{
            display: inline-flex;
            align-items: center;
            gap: 8px;
            padding: 7px 10px;
            border-radius: 999px;
            background: rgba(14, 91, 216, 0.08);
            color: #0f5cd5;
            font-size: 12px;
            font-weight: 700;
            letter-spacing: 0;
          }}
          #${{CARD_ID}}[data-tone="update"] .hip-badge {{
            background: rgba(14,127,99,0.12);
            color: #0e7f63;
          }}
          #${{CARD_ID}}[data-tone="install"] .hip-badge,
          #${{CARD_ID}}[data-tone="repair"] .hip-badge {{
            background: rgba(179,105,18,0.12);
            color: #aa6517;
          }}
          #${{CARD_ID}}[data-tone="error"] .hip-badge {{
            background: rgba(182,72,38,0.12);
            color: #b64826;
          }}
          #${{CARD_ID}} .hip-dot {{
            width: 8px;
            height: 8px;
            border-radius: 999px;
            background: currentColor;
            box-shadow: 0 0 0 5px rgba(14, 91, 216, 0.08);
          }}
          #${{CARD_ID}} .hip-title {{
            margin-top: 12px;
            font-size: 19px;
            font-weight: 700;
            letter-spacing: 0;
            line-height: 1.35;
          }}
          #${{CARD_ID}} .hip-copy {{
            margin-top: 6px;
            color: #5b6878;
            font-size: 13px;
            line-height: 1.65;
          }}
          #${{CARD_ID}} .hip-metrics {{
            margin-top: 12px;
            display: flex;
            align-items: center;
            justify-content: space-between;
            gap: 12px;
          }}
          #${{CARD_ID}} .hip-percent {{
            font-size: 26px;
            font-weight: 700;
            letter-spacing: 0;
          }}
          #${{CARD_ID}} .hip-phase {{
            color: #6f7c8d;
            font-size: 12px;
            font-weight: 700;
            letter-spacing: 0;
            text-transform: uppercase;
          }}
          #${{CARD_ID}} .hip-track {{
            margin-top: 10px;
            height: 10px;
            border-radius: 999px;
            overflow: hidden;
            background: rgba(20,31,44,0.08);
          }}
          #${{CARD_ID}} .hip-fill {{
            width: 0%;
            height: 100%;
            border-radius: inherit;
            background: linear-gradient(90deg, #0f5cd5 0%, #67a0ff 58%, #bfe0ff 100%);
            transition: width 180ms ease;
          }}
          #${{CARD_ID}}[data-indeterminate="true"] .hip-fill {{
            width: 38%;
            animation: horosa-inline-progress-sweep 1.2s linear infinite;
          }}
          #${{CARD_ID}}[data-tone="update"] .hip-fill {{
            background: linear-gradient(90deg, #0e7f63 0%, #45c7a0 58%, #c2f0df 100%);
          }}
          #${{CARD_ID}}[data-tone="install"] .hip-fill,
          #${{CARD_ID}}[data-tone="repair"] .hip-fill {{
            background: linear-gradient(90deg, #b36912 0%, #f0b34d 62%, #f8dca3 100%);
          }}
          #${{CARD_ID}}[data-tone="error"] .hip-fill {{
            background: linear-gradient(90deg, #b64826 0%, #ea8a66 64%, #f4c3b0 100%);
          }}
          @keyframes horosa-inline-progress-sweep {{
            0% {{
              transform: translateX(-130%);
            }}
            100% {{
              transform: translateX(310%);
            }}
          }}
        `;
        document.head.appendChild(style);
      }}

      function ensureCard() {{
        if (isLauncherPage()) return null;
        injectStyle();
        let card = document.getElementById(CARD_ID);
        if (card) return card;
        card = document.createElement('section');
        card.id = CARD_ID;
        card.innerHTML = `
          <div class="hip-head">
            <span class="hip-badge"><span class="hip-dot"></span><span class="hip-badge-text">更新进行中</span></span>
            <span class="hip-phase">准备中</span>
          </div>
          <div class="hip-title">正在处理更新事务</div>
          <div class="hip-copy">正在准备下载与替换，不需要额外操作。</div>
          <div class="hip-metrics">
            <div class="hip-percent">0%</div>
            <div class="hip-step">下载资产</div>
          </div>
          <div class="hip-track"><div class="hip-fill"></div></div>
        `;
        document.body.appendChild(card);
        return card;
      }}

      function shouldShow(mode, text, hasError) {{
        if (hasError) return true;
        if (mode === 'update') return true;
        return /下载|更新|替换应用|运行环境更新|本机组件更新|安装运行环境|安装本机组件|解压运行环境|解压本机组件|准备本机组件|部署本机组件|校验/.test(text || '');
      }}

      function tone(mode, hasError) {{
        if (hasError) return 'error';
        if (mode === 'update' || mode === 'install' || mode === 'repair') return mode;
        return 'update';
      }}

      function titleFor(mode, hasError) {{
        if (hasError) return '更新未完成';
        if (mode === 'install') return '正在准备本机组件';
        if (mode === 'repair') return '正在修复本机组件';
        return '正在下载并安装更新';
      }}

      function badgeFor(mode, hasError) {{
        if (hasError) return '需要处理';
        if (mode === 'install') return '首次准备';
        if (mode === 'repair') return '组件修复';
        return '更新进行中';
      }}

      function stepFor(text, ready, indeterminate) {{
        if (ready) return '即将完成';
        if (indeterminate && /下载|接收/.test(text || '')) return '接收资产';
        if (/校验/.test(text || '')) return '校验资产';
        if (/替换应用|重开/.test(text || '')) return '替换应用';
        if (/解压|切换|部署本机组件/.test(text || '')) return '部署组件';
        if (/运行环境更新|本机组件更新|运行环境|本机组件/.test(text || '')) return '准备组件';
        return '下载资产';
      }}

      function phaseFor(pct, text, ready, indeterminate) {{
        if (ready || pct >= 96) return '即将完成';
        if (indeterminate && /下载|接收/.test(text || '')) return '接收中';
        if (/替换应用|重开/.test(text || '') || pct >= 88) return '替换与重开';
        if (/运行环境|本机组件/.test(text || '') || pct >= 56) return '组件事务';
        if (/下载/.test(text || '') || pct >= 10) return '下载中';
        return '准备中';
      }}

      function show(card) {{
        if (hideTimer) {{
          clearTimeout(hideTimer);
          hideTimer = null;
        }}
        card.classList.add('is-visible');
      }}

      function hideSoon(card) {{
        if (hideTimer) clearTimeout(hideTimer);
        hideTimer = setTimeout(() => {{
          card.classList.remove('is-visible');
        }}, 1800);
      }}

      function setState(payload) {{
        const mode = payload.mode || lastMode;
        const text = payload.error || payload.message || '';
        const hasError = !!payload.error;
        const ready = !!payload.ready;
        const indeterminate = payload.indeterminate == null ? lastIndeterminate : !!payload.indeterminate;
        lastMode = mode;
        const card = ensureCard();
        if (!card) return;
        if (!shouldShow(mode, text, hasError)) {{
          if (!ready) card.classList.remove('is-visible');
          return;
        }}
        card.dataset.tone = tone(mode, hasError);
        card.dataset.indeterminate = indeterminate ? 'true' : 'false';
        card.querySelector('.hip-badge-text').textContent = badgeFor(mode, hasError);
        card.querySelector('.hip-title').textContent = titleFor(mode, hasError);
        card.querySelector('.hip-copy').textContent = text || '正在处理下载与安装事务。';
        const pct = payload.pct == null ? lastPct : Math.max(0, Math.min(100, Number(payload.pct) || 0));
        lastPct = pct;
        lastIndeterminate = indeterminate;
        card.querySelector('.hip-percent').textContent = indeterminate ? '接收中' : `${{Math.round(pct)}}%`;
        card.querySelector('.hip-phase').textContent = phaseFor(pct, text, ready, indeterminate);
        card.querySelector('.hip-step').textContent = stepFor(text, ready, indeterminate);
        if (!indeterminate) {{
          card.querySelector('.hip-fill').style.width = `${{pct}}%`;
        }}
        show(card);
        if (ready && !hasError) {{
          card.querySelector('.hip-copy').textContent = '更新准备完成，正在切回新版本。';
          hideSoon(card);
        }}
      }}

      return {{ setState }};
    }})();
  }}
  window.__horosaInlineProgress.setState({{
    mode: {mode},
    pct: {pct},
    message: {message},
    error: {error},
    ready: {ready},
    indeterminate: {indeterminate}
  }});
}})();
"#,
    ));
}

pub(crate) fn emit_status(window: &WebviewWindow, message: &str) {
    let raw_message = message;
    let message = escape_js(message);
    let _ = window.eval(&format!(
        "window.__horosaPendingStatusLines = window.__horosaPendingStatusLines || []; \
window.__horosaPendingStatusLines.push({message}); \
if (window.__horosaStatus) {{ window.__horosaStatus({message}); }}",
    ));
    emit_overlay(window, None, None, Some(raw_message), None, false, None);
}

pub(crate) fn emit_progress(window: &WebviewWindow, pct: u8, message: &str) {
    let raw_message = message;
    let message = escape_js(message);
    let _ = window.eval(&format!(
        "window.__horosaPendingProgress = {{ pct: {}, message: {}, indeterminate: false }}; \
if (window.__horosaProgress) {{ window.__horosaProgress({}, {}, false); }}",
        pct, message, pct, message
    ));
    emit_overlay(
        window,
        None,
        Some(pct),
        Some(raw_message),
        None,
        false,
        Some(false),
    );
}

pub(crate) fn emit_indeterminate_progress(window: &WebviewWindow, pct: u8, message: &str) {
    let raw_message = message;
    let message = escape_js(message);
    let _ = window.eval(&format!(
        "window.__horosaPendingProgress = {{ pct: {}, message: {}, indeterminate: true }}; \
if (window.__horosaProgress) {{ window.__horosaProgress({}, {}, true); }}",
        pct, message, pct, message
    ));
    emit_overlay(
        window,
        None,
        Some(pct),
        Some(raw_message),
        None,
        false,
        Some(true),
    );
}

pub(crate) fn emit_mode(window: &WebviewWindow, mode: &str) {
    let raw_mode = mode;
    let mode = escape_js(mode);
    let _ = window.eval(&format!(
        "window.__horosaPendingMode = {mode}; \
if (window.__horosaMode) {{ window.__horosaMode({mode}); }}",
    ));
    emit_overlay(window, Some(raw_mode), None, None, None, false, None);
}

pub(crate) fn emit_ready(window: &WebviewWindow, url: &str) {
    // 🔴 壳缩放经 URL query 确定性送达页面:随导航天然到达正确 document/origin。
    // (初始 document 上 eval 写的 localStorage 键分 origin,页面读不到——真机实锤。)
    let zoom = window
        .app_handle()
        .try_state::<AppState>()
        .and_then(|s| s.zoom_level.lock().ok().map(|z| *z))
        .unwrap_or(DEFAULT_ZOOM);
    let sep = if url.contains('?') { '&' } else { '?' };
    let url = format!("{url}{sep}shellZoom={zoom}");
    let url = escape_js(&url);
    let _ = window.eval(&format!(
        "window.__horosaPendingReadyUrl = {url}; \
if (window.__horosaReady) {{ window.__horosaReady({url}); }} else {{ window.location.replace({url}); }}",
    ));
    emit_overlay(
        window,
        None,
        Some(100),
        Some("已准备就绪，正在进入主界面…"),
        None,
        true,
        Some(false),
    );
}

pub(crate) fn emit_launcher_state(window: &WebviewWindow, payload: &LauncherStatePayload) {
    let json = serde_json::to_string(payload).unwrap_or_else(|_| "null".to_string());
    let _ = window.eval(&format!(
        "window.__horosaPendingStatePayload = {json}; \
if (window.__horosaState) {{ window.__horosaState({json}); }}"
    ));
}

pub(crate) fn emit_launcher_error(window: &WebviewWindow, payload: &LauncherStatePayload) {
    let json = serde_json::to_string(payload).unwrap_or_else(|_| "null".to_string());
    let overlay_message = payload
        .recommendation
        .as_deref()
        .or(Some(payload.summary.as_str()));
    let _ = window.eval(&format!(
        "window.__horosaPendingStatePayload = {json}; \
window.__horosaPendingError = {json}; \
if (window.__horosaState) {{ window.__horosaState({json}); }} \
if (window.__horosaError) {{ window.__horosaError({json}); }}"
    ));
    emit_overlay(
        window,
        Some("error"),
        None,
        None,
        overlay_message,
        false,
        Some(false),
    );
}

pub(crate) fn emit_asset_review(window: &WebviewWindow, payload: &AssetReviewPayload) {
    let json = serde_json::to_string(payload).unwrap_or_else(|_| "null".to_string());
    let _ = window.eval(&format!(
        "window.__horosaPendingReviewPayload = {json}; \
if (window.__horosaPresentReview) {{ window.__horosaPresentReview({json}); }}"
    ));
}

pub(crate) fn clear_asset_review(window: &WebviewWindow) {
    let _ = window.eval(
        "window.__horosaPendingReviewPayload = null; \
if (window.__horosaClearReview) { window.__horosaClearReview(); }",
    );
}

#[tauri::command]
pub(crate) fn perform_launcher_action(
    app: AppHandle,
    action: LauncherActionKind,
) -> std::result::Result<(), String> {
    match action {
        LauncherActionKind::ReinstallOfflinePackage => {
            open_offline_reinstall_flow(&app).map_err(|err| format!("{err:#}"))
        }
        LauncherActionKind::OpenDiagnostics => {
            open_diagnostics_window(&app).map_err(|err| format!("{err:#}"))
        }
        LauncherActionKind::RevealData => reveal_special_path(app, "data".to_string()),
        LauncherActionKind::RevealRuntime => reveal_special_path(app, "runtime".to_string()),
    }
}
