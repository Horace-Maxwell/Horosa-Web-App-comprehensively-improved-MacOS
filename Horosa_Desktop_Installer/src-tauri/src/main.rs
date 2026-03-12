#![cfg_attr(not(debug_assertions), windows_subsystem = "windows")]

use anyhow::{anyhow, Context, Result};
use flate2::read::GzDecoder;
use mime_guess::from_path;
use reqwest::blocking::Client;
use rfd::{MessageButtons, MessageDialog, MessageDialogResult, MessageLevel};
use semver::Version;
use serde::Deserialize;
use sha2::{Digest, Sha256};
use std::collections::HashMap;
use std::fs::{self, File};
use std::io::{Read, Write};
use std::net::{SocketAddr, TcpListener};
use std::path::{Path, PathBuf};
use std::process::{Command, Stdio};
use std::sync::atomic::{AtomicBool, Ordering};
use std::sync::{Arc, Mutex};
use std::thread;
use std::time::{Duration, SystemTime, UNIX_EPOCH};
use tar::Archive;
use tauri::menu::{Menu, MenuItem, PredefinedMenuItem, Submenu};
use tauri::{AppHandle, Manager, RunEvent, Runtime, WebviewWindow};
use tiny_http::{Header, Method, Response, Server, StatusCode};
use zip::ZipArchive;

const APP_NAME: &str = "星阙";
const MENU_CHECK_UPDATES: &str = "check_updates";
const MENU_REINSTALL_RUNTIME: &str = "reinstall_runtime";
const MENU_OPEN_LOGS: &str = "open_logs";
const MENU_OPEN_DATA: &str = "open_data";
const MENU_ZOOM_IN: &str = "zoom_in";
const MENU_ZOOM_OUT: &str = "zoom_out";
const MENU_ZOOM_RESET: &str = "zoom_reset";
const DEFAULT_ZOOM: f64 = 1.0;
const MIN_ZOOM: f64 = 0.7;
const MAX_ZOOM: f64 = 1.8;
const ZOOM_STEP: f64 = 0.1;
const DEFAULT_REPO_OWNER: &str = "Horace-Maxwell";
const DEFAULT_REPO_NAME: &str = "Horosa-Web-App-comprehensively-improved-MacOS";
const DEFAULT_RUNTIME_ASSET_NAME: &str = "horosa-runtime-macos-universal.tar.gz";
const DEFAULT_DESKTOP_ASSET_NAME: &str = "Horosa-Desktop-macos-universal.zip";
const DEFAULT_DESKTOP_PKG_NAME: &str = "Horosa-Installer-macos-universal.pkg";
const DEFAULT_DESKTOP_PKG_ZIP_NAME: &str = "Horosa-Installer-macos-universal-pkg.zip";
const DEFAULT_UPDATE_MANIFEST_NAME: &str = "horosa-latest.json";
const DEFAULT_RELEASE_TAG_PREFIX: &str = "v";
const DOWNLOAD_MAX_ATTEMPTS: usize = 4;
const DEFAULT_FRONTEND_PORT: u16 = 38991;

#[allow(dead_code)]
#[derive(Debug, Clone, Deserialize)]
struct ReleaseConfig {
    #[serde(rename = "repoOwner")]
    repo_owner: String,
    #[serde(rename = "repoName")]
    repo_name: String,
    #[serde(rename = "runtimeVersion")]
    runtime_version: String,
    #[serde(rename = "runtimeAssetName")]
    runtime_asset_name: String,
    #[serde(rename = "desktopAssetName")]
    desktop_asset_name: String,
    #[serde(rename = "desktopPkgName")]
    desktop_pkg_name: String,
    #[serde(rename = "desktopPkgZipName")]
    desktop_pkg_zip_name: String,
    #[serde(rename = "updateManifestName")]
    update_manifest_name: String,
    #[serde(rename = "releaseTagPrefix")]
    release_tag_prefix: String,
    #[serde(rename = "appName")]
    app_name: String,
}

#[derive(Debug, Deserialize)]
struct GithubRelease {
    tag_name: String,
    html_url: Option<String>,
    body: Option<String>,
    assets: Vec<GithubAsset>,
}

#[derive(Debug, Deserialize)]
struct GithubAsset {
    name: String,
    browser_download_url: String,
}

#[allow(dead_code)]
#[derive(Debug, Deserialize)]
struct UpdateManifest {
    version: String,
    tag: Option<String>,
    notes: Option<String>,
    #[serde(rename = "platforms")]
    platforms: HashMap<String, UpdatePlatform>,
}

#[allow(dead_code)]
#[derive(Debug, Deserialize)]
struct UpdatePlatform {
    #[serde(rename = "appUrl")]
    app_url: String,
    #[serde(rename = "pkgUrl")]
    pkg_url: Option<String>,
    #[serde(rename = "runtimeUrl")]
    runtime_url: Option<String>,
    #[serde(rename = "runtimeVersion")]
    runtime_version: Option<String>,
    #[serde(rename = "appSha256")]
    app_sha256: Option<String>,
    #[serde(rename = "pkgSha256")]
    pkg_sha256: Option<String>,
    #[serde(rename = "runtimeSha256")]
    runtime_sha256: Option<String>,
}

#[derive(Debug, Clone)]
struct UpdatePlan {
    latest_version: Version,
    notes: String,
    repo_url: String,
    release_url: String,
    app_url: String,
    app_sha256: Option<String>,
    runtime_url: Option<String>,
    runtime_version: Option<String>,
    runtime_sha256: Option<String>,
    source: UpdateSource,
}

#[derive(Debug, Clone, Copy, PartialEq, Eq)]
enum UpdateSource {
    Manifest,
    GithubApi,
}

#[derive(Debug, Clone, Deserialize)]
struct RuntimeManifest {
    version: String,
    built_at: String,
}

#[derive(Debug, Clone)]
struct RuntimePaths {
    app_data_dir: PathBuf,
    runtime_dir: PathBuf,
    logs_dir: PathBuf,
    frontend_dir: PathBuf,
    start_script: PathBuf,
    stop_script: PathBuf,
    manifest_path: PathBuf,
}

#[derive(Debug, Clone)]
struct RuntimeSession {
    paths: RuntimePaths,
    backend_port: u16,
    web_port: u16,
}

struct AppState {
    session: Mutex<Option<RuntimeSession>>,
    web_shutdown: Mutex<Option<Arc<AtomicBool>>>,
    zoom_level: Mutex<f64>,
}

fn fallback_release_config(app: &AppHandle) -> ReleaseConfig {
    ReleaseConfig {
        repo_owner: DEFAULT_REPO_OWNER.to_string(),
        repo_name: DEFAULT_REPO_NAME.to_string(),
        runtime_version: app.package_info().version.to_string(),
        runtime_asset_name: DEFAULT_RUNTIME_ASSET_NAME.to_string(),
        desktop_asset_name: DEFAULT_DESKTOP_ASSET_NAME.to_string(),
        desktop_pkg_name: DEFAULT_DESKTOP_PKG_NAME.to_string(),
        desktop_pkg_zip_name: DEFAULT_DESKTOP_PKG_ZIP_NAME.to_string(),
        update_manifest_name: DEFAULT_UPDATE_MANIFEST_NAME.to_string(),
        release_tag_prefix: DEFAULT_RELEASE_TAG_PREFIX.to_string(),
        app_name: APP_NAME.to_string(),
    }
}

impl Default for AppState {
    fn default() -> Self {
        Self {
            session: Mutex::new(None),
            web_shutdown: Mutex::new(None),
            zoom_level: Mutex::new(DEFAULT_ZOOM),
        }
    }
}

fn escape_js(text: &str) -> String {
    serde_json::to_string(text).unwrap_or_else(|_| "\"\"".to_string())
}

fn overlay_json(value: Option<&str>) -> String {
    value.map(escape_js).unwrap_or_else(|| "null".to_string())
}

fn emit_overlay(
    window: &WebviewWindow,
    mode: Option<&str>,
    pct: Option<u8>,
    message: Option<&str>,
    error: Option<&str>,
    ready: bool,
) {
    let mode = overlay_json(mode);
    let message = overlay_json(message);
    let error = overlay_json(error);
    let pct = pct
        .map(|value| value.to_string())
        .unwrap_or_else(|| "null".to_string());
    let ready = if ready { "true" } else { "false" };
    let _ = window.eval(&format!(
        r#"
(function () {{
  if (!window.__horosaInlineProgress) {{
    window.__horosaInlineProgress = (function () {{
      const STYLE_ID = 'horosa-inline-progress-style';
      const CARD_ID = 'horosa-inline-progress';
      let hideTimer = null;
      let lastMode = 'launch';

      function isLauncherPage() {{
        return !!document.querySelector('.installer-shell');
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
            width: min(360px, calc(100vw - 28px));
            z-index: 2147483646;
            padding: 16px 16px 14px;
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
            letter-spacing: 0.05em;
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
            letter-spacing: -0.03em;
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
            letter-spacing: -0.04em;
          }}
          #${{CARD_ID}} .hip-phase {{
            color: #6f7c8d;
            font-size: 12px;
            font-weight: 700;
            letter-spacing: 0.06em;
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
        return /下载|更新|替换应用|运行环境更新|安装运行环境|解压运行环境|校验/.test(text || '');
      }}

      function tone(mode, hasError) {{
        if (hasError) return 'error';
        if (mode === 'update' || mode === 'install' || mode === 'repair') return mode;
        return 'update';
      }}

      function titleFor(mode, hasError) {{
        if (hasError) return '更新未完成';
        if (mode === 'install') return '正在准备运行环境';
        if (mode === 'repair') return '正在修复运行环境';
        return '正在下载并安装更新';
      }}

      function badgeFor(mode, hasError) {{
        if (hasError) return '需要处理';
        if (mode === 'install') return '首次准备';
        if (mode === 'repair') return '运行时修复';
        return '更新进行中';
      }}

      function stepFor(text, ready) {{
        if (ready) return '即将完成';
        if (/校验/.test(text || '')) return '校验资产';
        if (/替换应用|重开/.test(text || '')) return '替换应用';
        if (/解压|切换/.test(text || '')) return '部署 Runtime';
        if (/运行环境更新|运行环境/.test(text || '')) return '下载 Runtime';
        return '下载资产';
      }}

      function phaseFor(pct, text, ready) {{
        if (ready || pct >= 96) return '即将完成';
        if (/替换应用|重开/.test(text || '') || pct >= 88) return '替换与重开';
        if (/运行环境/.test(text || '') || pct >= 56) return 'Runtime 事务';
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
        lastMode = mode;
        const card = ensureCard();
        if (!card) return;
        if (!shouldShow(mode, text, hasError)) {{
          if (!ready) card.classList.remove('is-visible');
          return;
        }}
        card.dataset.tone = tone(mode, hasError);
        card.querySelector('.hip-badge-text').textContent = badgeFor(mode, hasError);
        card.querySelector('.hip-title').textContent = titleFor(mode, hasError);
        card.querySelector('.hip-copy').textContent = text || '正在处理下载与安装事务。';
        const pct = payload.pct == null ? 0 : Math.max(0, Math.min(100, Number(payload.pct) || 0));
        card.querySelector('.hip-percent').textContent = `${{Math.round(pct)}}%`;
        card.querySelector('.hip-phase').textContent = phaseFor(pct, text, ready);
        card.querySelector('.hip-step').textContent = stepFor(text, ready);
        card.querySelector('.hip-fill').style.width = `${{pct}}%`;
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
    ready: {ready}
  }});
}})();
"#,
    ));
}

fn emit_status(window: &WebviewWindow, message: &str) {
    let raw_message = message;
    let message = escape_js(message);
    let _ = window.eval(&format!(
        "window.__horosaPendingStatusLines = window.__horosaPendingStatusLines || []; \
window.__horosaPendingStatusLines.push({message}); \
if (window.__horosaStatus) {{ window.__horosaStatus({message}); }}",
    ));
    emit_overlay(window, None, None, Some(raw_message), None, false);
}

fn emit_progress(window: &WebviewWindow, pct: u8, message: &str) {
    let raw_message = message;
    let message = escape_js(message);
    let _ = window.eval(&format!(
        "window.__horosaPendingProgress = {{ pct: {}, message: {} }}; \
if (window.__horosaProgress) {{ window.__horosaProgress({}, {}); }}",
        pct, message, pct, message
    ));
    emit_overlay(window, None, Some(pct), Some(raw_message), None, false);
}

fn emit_error(window: &WebviewWindow, message: &str) {
    let raw_message = message;
    let message = escape_js(message);
    let _ = window.eval(&format!(
        "window.__horosaPendingError = {message}; \
if (window.__horosaError) {{ window.__horosaError({message}); }}",
    ));
    emit_overlay(window, Some("error"), None, None, Some(raw_message), false);
}

fn emit_mode(window: &WebviewWindow, mode: &str) {
    let raw_mode = mode;
    let mode = escape_js(mode);
    let _ = window.eval(&format!(
        "window.__horosaPendingMode = {mode}; \
if (window.__horosaMode) {{ window.__horosaMode({mode}); }}",
    ));
    emit_overlay(window, Some(raw_mode), None, None, None, false);
}

fn emit_ready(window: &WebviewWindow, url: &str) {
    let url = escape_js(url);
    let _ = window.eval(&format!(
        "window.__horosaPendingReadyUrl = {url}; \
if (window.__horosaReady) {{ window.__horosaReady({url}); }} else {{ window.location.replace({url}); }}",
    ));
    emit_overlay(
        window,
        None,
        Some(100),
        Some("更新准备完成，正在切回新版本。"),
        None,
        true,
    );
}

fn build_menu<R: Runtime>(app: &tauri::AppHandle<R>) -> tauri::Result<Menu<R>> {
    let check_updates = MenuItem::with_id(
        app,
        MENU_CHECK_UPDATES,
        "检查更新",
        true,
        Some("CmdOrCtrl+U"),
    )?;
    let reinstall_runtime = MenuItem::with_id(
        app,
        MENU_REINSTALL_RUNTIME,
        "重新安装运行环境",
        true,
        None::<&str>,
    )?;
    let open_logs = MenuItem::with_id(app, MENU_OPEN_LOGS, "打开日志目录", true, None::<&str>)?;
    let open_data = MenuItem::with_id(app, MENU_OPEN_DATA, "打开运行目录", true, None::<&str>)?;
    let zoom_in = MenuItem::with_id(app, MENU_ZOOM_IN, "放大", true, Some("CmdOrCtrl+="))?;
    let zoom_out = MenuItem::with_id(app, MENU_ZOOM_OUT, "缩小", true, Some("CmdOrCtrl+-"))?;
    let zoom_reset =
        MenuItem::with_id(app, MENU_ZOOM_RESET, "实际大小", true, Some("CmdOrCtrl+0"))?;

    let app_menu = Submenu::with_items(
        app,
        APP_NAME,
        true,
        &[
            &PredefinedMenuItem::about(app, None, None)?,
            &PredefinedMenuItem::separator(app)?,
            &check_updates,
            &reinstall_runtime,
            &PredefinedMenuItem::separator(app)?,
            &PredefinedMenuItem::services(app, None)?,
            &PredefinedMenuItem::separator(app)?,
            &PredefinedMenuItem::hide(app, None)?,
            &PredefinedMenuItem::hide_others(app, None)?,
            &PredefinedMenuItem::show_all(app, None)?,
            &PredefinedMenuItem::separator(app)?,
            &PredefinedMenuItem::quit(app, None)?,
        ],
    )?;

    let file_menu = Submenu::with_items(
        app,
        "文件",
        true,
        &[
            &open_logs,
            &open_data,
            &PredefinedMenuItem::separator(app)?,
            &PredefinedMenuItem::close_window(app, None)?,
        ],
    )?;

    let edit_menu = Submenu::with_items(
        app,
        "编辑",
        true,
        &[
            &PredefinedMenuItem::undo(app, None)?,
            &PredefinedMenuItem::redo(app, None)?,
            &PredefinedMenuItem::separator(app)?,
            &PredefinedMenuItem::cut(app, None)?,
            &PredefinedMenuItem::copy(app, None)?,
            &PredefinedMenuItem::paste(app, None)?,
            &PredefinedMenuItem::select_all(app, None)?,
        ],
    )?;

    let view_menu = Submenu::with_items(
        app,
        "视图",
        true,
        &[
            &zoom_in,
            &zoom_out,
            &zoom_reset,
            &PredefinedMenuItem::separator(app)?,
            &PredefinedMenuItem::fullscreen(app, None)?,
            &PredefinedMenuItem::maximize(app, None)?,
        ],
    )?;

    let window_menu = Submenu::with_items(
        app,
        "窗口",
        true,
        &[
            &PredefinedMenuItem::minimize(app, None)?,
            &PredefinedMenuItem::maximize(app, None)?,
            &PredefinedMenuItem::separator(app)?,
            &PredefinedMenuItem::close_window(app, None)?,
        ],
    )?;

    Menu::with_items(
        app,
        &[&app_menu, &file_menu, &edit_menu, &view_menu, &window_menu],
    )
}

fn load_release_config(app: &AppHandle) -> Result<ReleaseConfig> {
    let resource_dir = app.path().resource_dir().context("missing resource dir")?;
    let candidates = [
        resource_dir.join("_up_/config/release_config.json"),
        resource_dir.join("config/release_config.json"),
        PathBuf::from(env!("CARGO_MANIFEST_DIR")).join("../config/release_config.json"),
    ];
    let mut parse_errors = Vec::new();
    for path in candidates {
        if path.exists() {
            match fs::read_to_string(&path) {
                Ok(data) => match serde_json::from_str::<ReleaseConfig>(&data) {
                    Ok(mut config) => {
                        let runtime_version = config.runtime_version.trim().to_string();
                        if runtime_version.is_empty()
                            || runtime_version.eq_ignore_ascii_case("auto")
                            || runtime_version.eq_ignore_ascii_case("same-as-app")
                        {
                            config.runtime_version = app.package_info().version.to_string();
                        }
                        return Ok(config);
                    }
                    Err(err) => {
                        parse_errors.push(format!("{}: {}", path.display(), err));
                    }
                },
                Err(err) => {
                    parse_errors.push(format!("{}: {}", path.display(), err));
                }
            }
        }
    }
    let fallback = fallback_release_config(app);
    if parse_errors.is_empty() {
        eprintln!(
            "release_config.json not found in bundle resources, using embedded defaults for {}/{}",
            fallback.repo_owner, fallback.repo_name
        );
    } else {
        eprintln!(
            "release_config.json unavailable, using embedded defaults for {}/{}; details: {}",
            fallback.repo_owner,
            fallback.repo_name,
            parse_errors.join(" | ")
        );
    }
    Ok(fallback)
}

fn runtime_paths_for_dir(app_data_dir: PathBuf, runtime_dir: PathBuf) -> RuntimePaths {
    let logs_dir = app_data_dir.join("logs");
    let frontend_dir = runtime_dir.join("Horosa-Web/astrostudyui/dist-file");
    let start_script = runtime_dir.join("Horosa-Web/start_horosa_local.sh");
    let stop_script = runtime_dir.join("Horosa-Web/stop_horosa_local.sh");
    let manifest_path = runtime_dir.join("runtime-manifest.json");
    RuntimePaths {
        app_data_dir,
        runtime_dir,
        logs_dir,
        frontend_dir,
        start_script,
        stop_script,
        manifest_path,
    }
}

fn shared_runtime_dir() -> PathBuf {
    std::env::var_os("HOROSA_SHARED_RUNTIME_DIR")
        .map(PathBuf::from)
        .unwrap_or_else(|| PathBuf::from("/Users/Shared/Horosa/runtime/current"))
}

fn runtime_dir_has_required_files(runtime_dir: &Path) -> bool {
    runtime_dir.join("runtime-manifest.json").exists()
        && runtime_dir
            .join("Horosa-Web/start_horosa_local.sh")
            .exists()
        && runtime_dir
            .join("Horosa-Web/astrostudyui/dist-file/index.html")
            .exists()
}

fn runtime_python_bin(runtime_dir: &Path) -> PathBuf {
    runtime_dir.join("runtime/mac/python/bin/python3")
}

fn is_runtime_metadata_junk(name: &str) -> bool {
    name == ".DS_Store" || name.starts_with("._")
}

fn cleanup_runtime_metadata(root: &Path) -> Result<u64> {
    if !root.exists() {
        return Ok(0);
    }
    let mut removed = 0u64;
    let mut stack = vec![root.to_path_buf()];
    while let Some(dir) = stack.pop() {
        let entries = fs::read_dir(&dir).with_context(|| format!("read_dir {}", dir.display()))?;
        for entry in entries {
            let entry = entry?;
            let path = entry.path();
            let file_type = entry.file_type()?;
            let name = entry.file_name();
            let name = name.to_string_lossy();
            if is_runtime_metadata_junk(&name) {
                if file_type.is_dir() {
                    fs::remove_dir_all(&path)?;
                } else {
                    fs::remove_file(&path)?;
                }
                removed += 1;
                continue;
            }
            if file_type.is_dir() {
                stack.push(path);
            }
        }
    }
    Ok(removed)
}

fn runtime_python_ready(runtime_dir: &Path) -> bool {
    let python_bin = runtime_python_bin(runtime_dir);
    if !python_bin.exists() {
        return false;
    }
    Command::new(&python_bin)
        .arg("-c")
        .arg(
            "import importlib.util as iu; mods=('cherrypy','jsonpickle','swisseph'); missing=[m for m in mods if iu.find_spec(m) is None]; raise SystemExit(1 if missing else 0)",
        )
        .env("PYTHONNOUSERSITE", "1")
        .stdout(Stdio::null())
        .stderr(Stdio::null())
        .status()
        .map(|status| status.success())
        .unwrap_or(false)
}

fn prepare_runtime_dir(runtime_dir: &Path) -> Result<()> {
    let _ = cleanup_runtime_metadata(runtime_dir)?;
    Ok(())
}

fn runtime_dir_is_usable(runtime_dir: &Path) -> bool {
    if !runtime_dir_has_required_files(runtime_dir) {
        return false;
    }
    prepare_runtime_dir(runtime_dir).is_ok() && runtime_python_ready(runtime_dir)
}

fn resolve_runtime_paths(app: &AppHandle) -> Result<RuntimePaths> {
    let app_data_dir = app.path().app_data_dir().context("missing app_data_dir")?;
    let user_runtime_dir = app_data_dir.join("runtime/current");
    if runtime_dir_is_usable(&user_runtime_dir) {
        return Ok(runtime_paths_for_dir(app_data_dir, user_runtime_dir));
    }

    let shared_runtime = shared_runtime_dir();
    if runtime_dir_is_usable(&shared_runtime) {
        return Ok(runtime_paths_for_dir(app_data_dir, shared_runtime));
    }

    Ok(runtime_paths_for_dir(app_data_dir, user_runtime_dir))
}

fn read_runtime_manifest(paths: &RuntimePaths) -> Option<RuntimeManifest> {
    let data = fs::read_to_string(&paths.manifest_path).ok()?;
    serde_json::from_str(&data).ok()
}

fn expected_runtime_url(config: &ReleaseConfig) -> String {
    format!(
        "https://github.com/{}/{}/releases/download/{}{}/{}",
        config.repo_owner,
        config.repo_name,
        config.release_tag_prefix,
        config.runtime_version,
        config.runtime_asset_name
    )
}

fn update_manifest_url(config: &ReleaseConfig) -> String {
    format!(
        "https://github.com/{}/{}/releases/latest/download/{}",
        config.repo_owner, config.repo_name, config.update_manifest_name
    )
}

fn current_platform_key() -> &'static str {
    match std::env::consts::ARCH {
        "aarch64" | "arm64" => "darwin-aarch64",
        _ => "darwin-x86_64",
    }
}

fn local_runtime_version(app: &AppHandle) -> Option<String> {
    let paths = resolve_runtime_paths(app).ok()?;
    read_runtime_manifest(&paths).map(|m| m.version)
}

fn unix_ts() -> u64 {
    SystemTime::now()
        .duration_since(UNIX_EPOCH)
        .unwrap_or_else(|_| Duration::from_secs(0))
        .as_secs()
}

fn cache_busted_url(url: &str) -> String {
    let separator = if url.contains('?') { '&' } else { '?' };
    format!("{url}{separator}ts={}", unix_ts())
}

fn normalize_checksum(value: Option<String>) -> Option<String> {
    value
        .map(|text| text.trim().to_ascii_lowercase())
        .filter(|text| !text.is_empty())
}

fn build_github_client(timeout_secs: u64) -> Result<Client> {
    Client::builder()
        .timeout(Duration::from_secs(timeout_secs))
        .build()
        .context("build http client")
}

fn sha256_digest(path: &Path) -> Result<String> {
    let mut file = File::open(path).with_context(|| format!("open {}", path.display()))?;
    let mut hasher = Sha256::new();
    let mut buffer = [0u8; 64 * 1024];
    loop {
        let read = file.read(&mut buffer)?;
        if read == 0 {
            break;
        }
        hasher.update(&buffer[..read]);
    }
    Ok(format!("{:x}", hasher.finalize()))
}

fn verify_sha256(path: &Path, expected: Option<&str>, label: &str) -> Result<()> {
    let Some(expected) = expected.map(|value| value.trim().to_ascii_lowercase()) else {
        return Ok(());
    };
    if expected.is_empty() {
        return Ok(());
    }
    let actual = sha256_digest(path)?;
    if actual != expected {
        return Err(anyhow!(
            "{} 校验失败: expected {}, got {}",
            label,
            expected,
            actual
        ));
    }
    Ok(())
}

fn resolve_update_plan(client: &Client, app: &AppHandle) -> Result<UpdatePlan> {
    let config = load_release_config(app)?;
    let platform_key = current_platform_key();

    let manifest_url = cache_busted_url(&update_manifest_url(&config));
    if let Ok(response) = client
        .get(&manifest_url)
        .header("User-Agent", "HorosaDesktop")
        .header("Cache-Control", "no-cache")
        .header("Pragma", "no-cache")
        .send()
    {
        if response.status().is_success() {
            if let Ok(manifest) = response.json::<UpdateManifest>() {
                if let Some(platform) = manifest.platforms.get(platform_key) {
                    let latest = Version::parse(manifest.version.trim())?;
                    let repo_url = format!(
                        "https://github.com/{}/{}",
                        config.repo_owner, config.repo_name
                    );
                    let release_tag = manifest
                        .tag
                        .clone()
                        .unwrap_or_else(|| format!("{}{}", config.release_tag_prefix, latest));
                    let release_url = format!("{}/releases/tag/{}", repo_url, release_tag);
                    return Ok(UpdatePlan {
                        latest_version: latest,
                        notes: manifest
                            .notes
                            .unwrap_or_else(|| "See GitHub release notes.".to_string()),
                        repo_url,
                        release_url,
                        app_url: platform.app_url.clone(),
                        app_sha256: normalize_checksum(platform.app_sha256.clone()),
                        runtime_url: platform.runtime_url.clone(),
                        runtime_version: platform.runtime_version.clone(),
                        runtime_sha256: normalize_checksum(platform.runtime_sha256.clone()),
                        source: UpdateSource::Manifest,
                    });
                }
            }
        }
    }

    let api = format!(
        "https://api.github.com/repos/{}/{}/releases/latest",
        config.repo_owner, config.repo_name
    );
    let release = client
        .get(&api)
        .header("User-Agent", "HorosaDesktop")
        .header("Cache-Control", "no-cache")
        .header("Pragma", "no-cache")
        .send()?
        .error_for_status()?
        .json::<GithubRelease>()?;
    let latest = parse_version(&release.tag_name)?;
    let repo_url = format!(
        "https://github.com/{}/{}",
        config.repo_owner, config.repo_name
    );
    let asset = release
        .assets
        .iter()
        .find(|asset| asset.name == config.desktop_asset_name)
        .ok_or_else(|| anyhow!("desktop asset {} not found", config.desktop_asset_name))?;
    let runtime_asset = release
        .assets
        .iter()
        .find(|asset| asset.name == config.runtime_asset_name);
    Ok(UpdatePlan {
        latest_version: latest.clone(),
        notes: release.body.unwrap_or_default(),
        repo_url: repo_url.clone(),
        release_url: release
            .html_url
            .clone()
            .unwrap_or_else(|| format!("{}/releases/tag/{}", repo_url, release.tag_name)),
        app_url: asset.browser_download_url.clone(),
        app_sha256: None,
        runtime_url: runtime_asset.map(|asset| asset.browser_download_url.clone()),
        runtime_version: runtime_asset.map(|_| latest.to_string()),
        runtime_sha256: None,
        source: UpdateSource::GithubApi,
    })
}

fn ensure_dir(path: &Path) -> Result<()> {
    fs::create_dir_all(path).with_context(|| format!("mkdir -p {}", path.display()))
}

fn tmp_download_path(app_name: &str, suffix: &str) -> PathBuf {
    let ts = SystemTime::now()
        .duration_since(UNIX_EPOCH)
        .unwrap_or_else(|_| Duration::from_secs(0))
        .as_secs();
    std::env::temp_dir().join(format!("{}-{}-{}", app_name, ts, suffix))
}

fn download_with_progress(
    window: &WebviewWindow,
    url: &str,
    dest: &Path,
    start_pct: u8,
    end_pct: u8,
    label: &str,
) -> Result<()> {
    let mut last_err = None;
    for attempt in 1..=DOWNLOAD_MAX_ATTEMPTS {
        if attempt > 1 {
            let retry_msg = format!(
                "{} 失败，正在重试（{}/{}）…",
                label, attempt, DOWNLOAD_MAX_ATTEMPTS
            );
            emit_status(window, &retry_msg);
            emit_progress(window, start_pct, &retry_msg);
            thread::sleep(Duration::from_secs((attempt as u64 - 1) * 2));
        }
        match download_with_progress_once(window, url, dest, start_pct, end_pct, label) {
            Ok(()) => return Ok(()),
            Err(err) => {
                last_err = Some(err);
                let _ = fs::remove_file(dest);
            }
        }
    }
    let err = last_err.unwrap_or_else(|| anyhow!("download failed without error detail"));
    Err(wrap_download_error(label, url, err))
}

fn download_with_progress_once(
    window: &WebviewWindow,
    url: &str,
    dest: &Path,
    start_pct: u8,
    end_pct: u8,
    label: &str,
) -> Result<()> {
    let client = build_github_client(900)?;
    let mut response = client
        .get(url)
        .header("User-Agent", "HorosaDesktop")
        .header("Cache-Control", "no-cache")
        .header("Pragma", "no-cache")
        .send()
        .with_context(|| format!("download {}", url))?;
    if !response.status().is_success() {
        return Err(anyhow!("download failed: {} -> {}", url, response.status()));
    }
    if let Some(parent) = dest.parent() {
        ensure_dir(parent)?;
    }
    let total = response.content_length().unwrap_or(0);
    let mut file = File::create(dest)?;
    let mut downloaded: u64 = 0;
    let mut buffer = [0u8; 64 * 1024];
    loop {
        let read = response.read(&mut buffer)?;
        if read == 0 {
            break;
        }
        file.write_all(&buffer[..read])?;
        downloaded += read as u64;
        if total > 0 {
            let ratio = downloaded as f64 / total as f64;
            let span = end_pct.saturating_sub(start_pct) as f64;
            let pct = start_pct as f64 + span * ratio;
            emit_progress(window, pct.round() as u8, label);
        }
    }
    emit_progress(window, end_pct, label);
    Ok(())
}

fn wrap_download_error(label: &str, url: &str, err: anyhow::Error) -> anyhow::Error {
    let details = format!("{err:#}");
    let lower = details.to_ascii_lowercase();
    let summary = if lower.contains("tls handshake eof") {
        format!(
            "{}失败：已自动重试 {} 次，但和 GitHub 建立安全连接时仍被中断。请稍后重试，或切换更稳定的网络后再试。",
            label, DOWNLOAD_MAX_ATTEMPTS
        )
    } else if lower.contains("timed out") || lower.contains("timeout") {
        format!(
            "{}失败：已自动重试 {} 次，但下载仍然超时。请稍后重试，或切换更稳定的网络后再试。",
            label, DOWNLOAD_MAX_ATTEMPTS
        )
    } else if lower.contains("dns")
        || lower.contains("failed to lookup")
        || lower.contains("name or service not known")
        || lower.contains("nodename nor servname")
    {
        format!(
            "{}失败：已自动重试 {} 次，但当前网络无法稳定解析 GitHub 地址。请检查网络或代理设置后再试。",
            label, DOWNLOAD_MAX_ATTEMPTS
        )
    } else {
        format!(
            "{}失败：已自动重试 {} 次仍未完成。请稍后重试；如果反复失败，请优先检查当前网络是否能访问 GitHub。",
            label, DOWNLOAD_MAX_ATTEMPTS
        )
    };
    anyhow!("{summary}\n下载地址: {url}\n原始错误: {details}")
}

fn remove_dir_if_exists(path: &Path) -> Result<()> {
    if path.exists() {
        fs::remove_dir_all(path)?;
    }
    Ok(())
}

fn extract_runtime_archive(archive_path: &Path, dest_root: &Path) -> Result<()> {
    let extract_root = dest_root.join("_extract");
    remove_dir_if_exists(&extract_root)?;
    ensure_dir(&extract_root)?;
    let tar_gz = File::open(archive_path)?;
    let decoder = GzDecoder::new(tar_gz);
    let mut archive = Archive::new(decoder);
    archive.unpack(&extract_root)?;

    let extracted_runtime = extract_root.join("runtime-payload");
    if !extracted_runtime.exists() {
        return Err(anyhow!("runtime-payload folder missing inside archive"));
    }

    let final_runtime = dest_root.join("current");
    let backup_runtime = dest_root.join("previous");
    let had_previous = final_runtime.exists();
    if final_runtime.exists() {
        remove_dir_if_exists(&backup_runtime)?;
        fs::rename(&final_runtime, &backup_runtime)?;
    }
    if let Err(err) = fs::rename(&extracted_runtime, &final_runtime) {
        if had_previous && backup_runtime.exists() {
            let _ = fs::rename(&backup_runtime, &final_runtime);
        }
        return Err(err.into());
    }
    prepare_runtime_dir(&final_runtime)?;
    remove_dir_if_exists(&backup_runtime)?;
    remove_dir_if_exists(&extract_root)?;
    Ok(())
}

fn ensure_runtime_installed(
    app: &AppHandle,
    window: &WebviewWindow,
    force: bool,
) -> Result<RuntimePaths> {
    let config = load_release_config(app)?;
    let paths = resolve_runtime_paths(app)?;
    ensure_dir(&paths.app_data_dir)?;
    ensure_dir(&paths.logs_dir)?;

    let current = read_runtime_manifest(&paths);
    let already_ok = current
        .as_ref()
        .map(|m| m.version == config.runtime_version)
        .unwrap_or(false)
        && runtime_dir_is_usable(&paths.runtime_dir);

    if already_ok && !force {
        emit_mode(window, "launch");
        emit_progress(
            window,
            36,
            &format!("检测到运行环境 {} 已存在", config.runtime_version),
        );
        if let Some(m) = current {
            emit_status(
                window,
                &format!("当前运行环境版本: {} ({})", m.version, m.built_at),
            );
        }
        return Ok(paths);
    }

    if force {
        emit_mode(window, "repair");
    } else if current.is_some() || runtime_dir_has_required_files(&paths.runtime_dir) {
        emit_mode(window, "repair");
    } else {
        emit_mode(window, "install");
    }
    emit_status(window, "开始下载 星阙 运行环境…");
    emit_progress(window, 6, "准备安装运行环境");
    let archive_path = tmp_download_path(&config.app_name, "runtime.tar.gz");
    let runtime_url = expected_runtime_url(&config);
    download_with_progress(window, &runtime_url, &archive_path, 8, 56, "下载运行环境")?;
    emit_status(window, "下载完成，正在解压运行环境…");
    emit_progress(window, 62, "解压运行环境");
    let runtime_root = paths.app_data_dir.join("runtime");
    ensure_dir(&runtime_root)?;
    extract_runtime_archive(&archive_path, &runtime_root)?;
    let _ = fs::remove_file(&archive_path);
    emit_progress(window, 74, "运行环境安装完成");
    Ok(resolve_runtime_paths(app)?)
}

fn choose_free_port() -> Result<u16> {
    let listener = TcpListener::bind("127.0.0.1:0")?;
    let port = listener.local_addr()?.port();
    drop(listener);
    Ok(port)
}

fn choose_port_with_preference(preferred_port: u16) -> Result<u16> {
    match TcpListener::bind(("127.0.0.1", preferred_port)) {
        Ok(listener) => {
            let port = listener.local_addr()?.port();
            drop(listener);
            Ok(port)
        }
        Err(_) => choose_free_port(),
    }
}

fn start_static_server(
    frontend_dir: PathBuf,
    port: u16,
    shutdown: Arc<AtomicBool>,
) -> Result<thread::JoinHandle<()>> {
    let addr = SocketAddr::from(([127, 0, 0, 1], port));
    let server = Server::http(addr).map_err(|e| anyhow!(e.to_string()))?;
    let handle = thread::spawn(move || {
        while !shutdown.load(Ordering::Relaxed) {
            let request = match server.recv_timeout(Duration::from_millis(250)) {
                Ok(Some(req)) => req,
                Ok(None) => continue,
                Err(_) => continue,
            };
            if request.method() != &Method::Get && request.method() != &Method::Head {
                let _ = request.respond(Response::empty(StatusCode(405)));
                continue;
            }
            let url = request.url().split('?').next().unwrap_or("/");
            let rel = if url == "/" {
                "index.html".to_string()
            } else {
                url.trim_start_matches('/').to_string()
            };
            let mut target = frontend_dir.join(&rel);
            if !target.exists() {
                target = frontend_dir.join("index.html");
            }
            match fs::read(&target) {
                Ok(bytes) => {
                    let mime = from_path(&target).first_or_octet_stream().to_string();
                    let response = Response::from_data(bytes).with_header(
                        Header::from_bytes(&b"Content-Type"[..], mime.as_bytes()).unwrap(),
                    );
                    let _ = request.respond(response);
                }
                Err(_) => {
                    let _ = request.respond(Response::empty(StatusCode(404)));
                }
            }
        }
    });
    Ok(handle)
}

fn stop_runtime(paths: &RuntimePaths) {
    if !paths.stop_script.exists() {
        return;
    }
    let _ = Command::new("/bin/bash")
        .arg(&paths.stop_script)
        .current_dir(paths.runtime_dir.join("Horosa-Web"))
        .stdout(Stdio::null())
        .stderr(Stdio::null())
        .status();
}

fn start_runtime(
    paths: &RuntimePaths,
    window: &WebviewWindow,
    backend_port: u16,
    chart_port: u16,
) -> Result<()> {
    ensure_dir(&paths.logs_dir)?;
    prepare_runtime_dir(&paths.runtime_dir)?;
    stop_runtime(paths);
    emit_status(window, "正在后台启动 星阙 Python / Java 服务…");
    emit_progress(window, 82, "启动本地服务");

    let python_bin = runtime_python_bin(&paths.runtime_dir);
    let java_bin = paths.runtime_dir.join("runtime/mac/java/bin/java");
    let output = Command::new("/bin/bash")
        .arg(&paths.start_script)
        .current_dir(paths.runtime_dir.join("Horosa-Web"))
        .env("HOROSA_SKIP_UI_BUILD", "1")
        .env("HOROSA_PYTHON", python_bin)
        .env("HOROSA_JAVA_BIN", java_bin)
        .env("HOROSA_SERVER_PORT", backend_port.to_string())
        .env("HOROSA_CHART_PORT", chart_port.to_string())
        .env(
            "HOROSA_LOG_ROOT",
            paths.logs_dir.to_string_lossy().to_string(),
        )
        .env(
            "HOROSA_DIAG_DIR",
            paths.logs_dir.to_string_lossy().to_string(),
        )
        .output()
        .context("launch start_horosa_local.sh")?;
    if !output.status.success() {
        let stdout = String::from_utf8_lossy(&output.stdout);
        let stderr = String::from_utf8_lossy(&output.stderr);
        return Err(anyhow!(
            "星阙 backend start failed\nstdout:\n{}\nstderr:\n{}",
            stdout,
            stderr
        ));
    }
    emit_progress(window, 92, "本地服务已就绪");
    Ok(())
}

fn frontend_url(web_port: u16, backend_port: u16) -> String {
    let root = format!("http://127.0.0.1:{}", backend_port);
    format!(
        "http://127.0.0.1:{}/index.html?srv={}&v={}",
        web_port,
        urlencoding::encode(&root),
        unix_ts()
    )
}

fn open_path(path: &Path) {
    let _ = Command::new("open").arg(path).spawn();
}

fn clamp_zoom_level(value: f64) -> f64 {
    value.clamp(MIN_ZOOM, MAX_ZOOM)
}

fn set_window_zoom(app: &AppHandle, zoom: f64) -> Result<()> {
    let clamped = clamp_zoom_level(zoom);
    let window = app
        .get_webview_window("main")
        .context("main window missing for zoom")?;
    window.set_zoom(clamped)?;
    if let Some(state) = app.try_state::<AppState>() {
        if let Ok(mut slot) = state.zoom_level.lock() {
            *slot = clamped;
        }
    }
    Ok(())
}

fn adjust_window_zoom(app: &AppHandle, delta: f64) -> Result<()> {
    let current = if let Some(state) = app.try_state::<AppState>() {
        if let Ok(slot) = state.zoom_level.lock() {
            *slot
        } else {
            DEFAULT_ZOOM
        }
    } else {
        DEFAULT_ZOOM
    };
    set_window_zoom(app, current + delta)
}

fn shell_quote(path: &Path) -> String {
    let txt = path.to_string_lossy().replace('"', "\\\"");
    format!("\"{}\"", txt)
}

fn shell_quote_text(text: &str) -> String {
    format!("\"{}\"", text.replace('"', "\\\""))
}

fn applescript_quote_text(text: &str) -> String {
    format!("\"{}\"", text.replace('\\', "\\\\").replace('"', "\\\""))
}

fn current_uid_string() -> String {
    std::env::var("UID")
        .ok()
        .filter(|value| !value.trim().is_empty())
        .unwrap_or_else(|| {
            Command::new("/usr/bin/id")
                .arg("-u")
                .output()
                .ok()
                .and_then(|output| String::from_utf8(output.stdout).ok())
                .map(|value| value.trim().to_string())
                .filter(|value| !value.is_empty())
                .unwrap_or_else(|| "0".to_string())
        })
}

fn current_user_string() -> String {
    std::env::var("USER")
        .ok()
        .filter(|value| !value.trim().is_empty())
        .unwrap_or_else(|| {
            Command::new("/usr/bin/id")
                .arg("-un")
                .output()
                .ok()
                .and_then(|output| String::from_utf8(output.stdout).ok())
                .map(|value| value.trim().to_string())
                .filter(|value| !value.is_empty())
                .unwrap_or_else(|| "unknown".to_string())
        })
}

fn update_helper_log_path(app: &AppHandle, extract_root: &Path) -> PathBuf {
    let logs_dir = app
        .path()
        .app_data_dir()
        .map(|path| path.join("logs"))
        .unwrap_or_else(|_| extract_root.to_path_buf());
    let _ = ensure_dir(&logs_dir);
    logs_dir.join("update-installer.log")
}

fn target_requires_admin_update(target_app: &Path) -> bool {
    #[cfg(target_os = "macos")]
    {
        target_app.starts_with(Path::new("/Applications"))
    }
    #[cfg(not(target_os = "macos"))]
    {
        let _ = target_app;
        false
    }
}

fn app_bundle_path() -> Option<PathBuf> {
    let exe = std::env::current_exe().ok()?;
    for ancestor in exe.ancestors() {
        if ancestor.extension().and_then(|s| s.to_str()) == Some("app") {
            return Some(ancestor.to_path_buf());
        }
    }
    None
}

fn install_downloaded_app(
    app: AppHandle,
    zip_path: &Path,
    runtime_archive: Option<&Path>,
    runtime_version: Option<&str>,
) -> Result<()> {
    let extract_root = tmp_download_path(APP_NAME, "app-update");
    ensure_dir(&extract_root)?;
    let file = File::open(zip_path)?;
    let mut archive = ZipArchive::new(file)?;
    archive.extract(&extract_root)?;

    let mut app_src = None;
    for entry in fs::read_dir(&extract_root)? {
        let entry = entry?;
        let path = entry.path();
        if path.extension().and_then(|s| s.to_str()) == Some("app") {
            app_src = Some(path);
            break;
        }
    }
    let app_src = app_src.context("updated app bundle not found in zip")?;
    let target_app = app_bundle_path().context("current app bundle path not found")?;
    let update_log = update_helper_log_path(&app, &extract_root);
    let helper = extract_root.join("install_update.sh");
    let current_uid = current_uid_string();
    let current_user = current_user_string();
    let requires_admin = target_requires_admin_update(&target_app);
    let shared_runtime_root = shared_runtime_dir()
        .parent()
        .map(Path::to_path_buf)
        .unwrap_or_else(|| PathBuf::from("/Users/Shared/Horosa/runtime"));
    let runtime_cmd = if let Some(archive_path) = runtime_archive {
        format!(
            "install_runtime() {{\nRUNTIME_ROOT={runtime_root}\nWORK_ROOT=\"${{RUNTIME_ROOT}}/_update\"\nPREVIOUS_ROOT=\"${{RUNTIME_ROOT}}/previous\"\nEXPECTED_RUNTIME_VERSION={runtime_version}\nmkdir -p \"${{RUNTIME_ROOT}}\"\nrm -rf \"${{WORK_ROOT}}\"\nmkdir -p \"${{WORK_ROOT}}\"\n/usr/bin/tar -xzf {archive} -C \"${{WORK_ROOT}}\"\nif [ ! -f \"${{WORK_ROOT}}/runtime-payload/runtime-manifest.json\" ]; then\n  echo \"runtime manifest missing after extract\" >&2\n  exit 1\nfi\nACTUAL_RUNTIME_VERSION=$(/usr/bin/python3 - <<'PY'\nimport json, pathlib\npath = pathlib.Path(r\"${{WORK_ROOT}}/runtime-payload/runtime-manifest.json\")\nprint(json.loads(path.read_text()).get(\"version\", \"\"))\nPY\n)\nif [ -n \"${{EXPECTED_RUNTIME_VERSION}}\" ] && [ \"${{ACTUAL_RUNTIME_VERSION}}\" != \"${{EXPECTED_RUNTIME_VERSION}}\" ]; then\n  echo \"runtime version mismatch: ${{ACTUAL_RUNTIME_VERSION}} != ${{EXPECTED_RUNTIME_VERSION}}\" >&2\n  exit 1\nfi\nrm -rf \"${{PREVIOUS_ROOT}}\"\nHAD_RUNTIME=0\nif [ -d \"${{RUNTIME_ROOT}}/current\" ]; then\n  mv \"${{RUNTIME_ROOT}}/current\" \"${{PREVIOUS_ROOT}}\"\n  HAD_RUNTIME=1\nfi\nif mv \"${{WORK_ROOT}}/runtime-payload\" \"${{RUNTIME_ROOT}}/current\"; then\n  rm -rf \"${{WORK_ROOT}}\" \"${{PREVIOUS_ROOT}}\"\n  /usr/bin/xattr -dr com.apple.quarantine \"${{RUNTIME_ROOT}}/current\" >/dev/null 2>&1 || true\nelse\n  rm -rf \"${{RUNTIME_ROOT}}/current\"\n  if [ \"${{HAD_RUNTIME}}\" = \"1\" ] && [ -d \"${{PREVIOUS_ROOT}}\" ]; then\n    mv \"${{PREVIOUS_ROOT}}\" \"${{RUNTIME_ROOT}}/current\"\n  fi\n  exit 1\nfi\n}}\ninstall_runtime\n",
            runtime_root = shell_quote(&shared_runtime_root),
            archive = shell_quote(archive_path),
            runtime_version = shell_quote_text(runtime_version.unwrap_or(""))
        )
    } else {
        String::new()
    };
    let script = format!(
        "#!/bin/bash\nset -euo pipefail\nLOG={log}\nmkdir -p \"$(dirname \"${{LOG}}\")\"\nexec >> \"${{LOG}}\" 2>&1\necho \"===== update helper start $(date '+%Y-%m-%d %H:%M:%S') =====\"\necho \"uid=$(/usr/bin/id -u) user=$(/usr/bin/id -un)\"\necho \"target={target}\"\necho \"src={src}\"\nsleep 2\n{runtime_cmd}open_app() {{\nTARGET={target}\nUSER_UID={user_uid}\nUSER_NAME={user_name}\nif [ \"$(/usr/bin/id -u)\" = \"${{USER_UID}}\" ]; then\n  /usr/bin/open \"${{TARGET}}\"\n  return 0\nfi\nif /bin/launchctl asuser \"${{USER_UID}}\" /usr/bin/open \"${{TARGET}}\"; then\n  return 0\nfi\nif /usr/bin/sudo -u \"${{USER_NAME}}\" /usr/bin/open \"${{TARGET}}\"; then\n  return 0\nfi\n/usr/bin/open \"${{TARGET}}\"\n}}\ninstall_app() {{\nTARGET={target}\nSRC={src}\nBACKUP_TARGET=\"${{TARGET}}.previous\"\nfor attempt in $(/usr/bin/seq 1 45); do\n  echo \"[app] attempt ${{attempt}}\"\n  rm -rf \"${{BACKUP_TARGET}}\"\n  HAD_TARGET=0\n  if [ -d \"${{TARGET}}\" ]; then\n    if mv \"${{TARGET}}\" \"${{BACKUP_TARGET}}\"; then\n      HAD_TARGET=1\n    else\n      echo \"[app] mv failed on attempt ${{attempt}}\"\n      /bin/ls -ld \"${{TARGET}}\" >/dev/null 2>&1 && /bin/ls -ld \"${{TARGET}}\"\n      sleep 1\n      continue\n    fi\n  fi\n  if /usr/bin/ditto \"${{SRC}}\" \"${{TARGET}}\"; then\n    rm -rf \"${{BACKUP_TARGET}}\"\n    /usr/bin/xattr -dr com.apple.quarantine \"${{TARGET}}\" >/dev/null 2>&1 || true\n    echo \"[app] install succeeded\"\n    return 0\n  fi\n  echo \"[app] ditto failed on attempt ${{attempt}}\"\n  rm -rf \"${{TARGET}}\"\n  if [ \"${{HAD_TARGET}}\" = \"1\" ] && [ -d \"${{BACKUP_TARGET}}\" ]; then\n    mv \"${{BACKUP_TARGET}}\" \"${{TARGET}}\" || true\n  fi\n  sleep 1\ndone\necho \"[app] install failed after retries\"\nreturn 1\n}}\ninstall_app\nopen_app\necho \"===== update helper success $(date '+%Y-%m-%d %H:%M:%S') =====\"\n",
        log = shell_quote(&update_log),
        runtime_cmd = runtime_cmd,
        target = shell_quote(&target_app),
        src = shell_quote(&app_src),
        user_uid = shell_quote_text(&current_uid),
        user_name = shell_quote_text(&current_user)
    );
    fs::write(&helper, script)?;
    #[cfg(unix)]
    {
        use std::os::unix::fs::PermissionsExt;
        let mut perms = fs::metadata(&helper)?.permissions();
        perms.set_mode(0o755);
        fs::set_permissions(&helper, perms)?;
    }
    if requires_admin {
        let command = format!("/bin/bash {}", shell_quote(&helper));
        Command::new("/usr/bin/osascript")
            .arg("-e")
            .arg(format!(
                "do shell script {} with administrator privileges",
                applescript_quote_text(&command)
            ))
            .stdout(Stdio::null())
            .stderr(Stdio::null())
            .spawn()?;
    } else {
        Command::new("/bin/bash")
            .arg(&helper)
            .stdout(Stdio::null())
            .stderr(Stdio::null())
            .spawn()?;
    }
    app.exit(0);
    Ok(())
}

fn parse_version(tag: &str) -> Result<Version> {
    let trimmed = tag.trim().trim_start_matches('v');
    Version::parse(trimmed).with_context(|| format!("parse version: {}", tag))
}

fn normalize_update_notes(notes: &str) -> String {
    let normalized = notes
        .replace(
            "
", "
",
        )
        .trim()
        .to_string();
    if normalized.is_empty() {
        return "暂无更新说明。".to_string();
    }
    let max_chars = 3200;
    let char_count = normalized.chars().count();
    if char_count <= max_chars {
        return normalized;
    }
    let trimmed: String = normalized.chars().take(max_chars).collect();
    format!(
        "{}

[更新说明较长，已截断显示。完整内容请查看 GitHub Release。]",
        trimmed.trim_end()
    )
}

fn strip_markdown_prefix(line: &str) -> &str {
    line.trim()
        .trim_start_matches('#')
        .trim_start_matches('-')
        .trim_start_matches('*')
        .trim_start_matches(char::is_numeric)
        .trim_start_matches('.')
        .trim_start_matches(')')
        .trim()
}

fn summarize_update_notes(notes: &str) -> String {
    let normalized = normalize_update_notes(notes);
    if normalized == "暂无更新说明。" {
        return normalized;
    }
    let mut items = Vec::new();
    for line in normalized.lines() {
        let clean = strip_markdown_prefix(line);
        if clean.is_empty() {
            continue;
        }
        items.push(clean.to_string());
        if items.len() >= 4 {
            break;
        }
    }
    if items.is_empty() {
        return "暂无可提炼的更新摘要。".to_string();
    }
    items.join(
        "
",
    )
}

fn format_runtime_status(local_runtime: Option<&str>, remote_runtime: Option<&str>) -> String {
    match (local_runtime, remote_runtime) {
        (Some(local), Some(remote)) if local.trim() == remote.trim() => {
            format!("{} (已是最新)", local.trim())
        }
        (Some(local), Some(remote)) => format!("{} -> {}", local.trim(), remote.trim()),
        (None, Some(remote)) => format!("未安装 -> {}", remote.trim()),
        (Some(local), None) if !local.trim().is_empty() => {
            format!("{} (远端未声明版本)", local.trim())
        }
        _ => "unknown".to_string(),
    }
}

fn format_update_check_dialog(
    current: &Version,
    latest: &Version,
    local_runtime: Option<&str>,
    remote_runtime: Option<&str>,
    runtime_needs_update: bool,
    source: UpdateSource,
    notes: &str,
    repo_url: &str,
    release_url: &str,
) -> String {
    let status = if latest > current {
        "发现可用更新"
    } else if runtime_needs_update {
        "应用已是最新，运行环境可更新"
    } else if latest == current {
        "已是最新版本"
    } else {
        "当前版本高于远端版本"
    };
    let update_source = match source {
        UpdateSource::Manifest => "固定更新清单",
        UpdateSource::GithubApi => "GitHub Releases 回退通道",
    };
    let summary = summarize_update_notes(notes);
    let changelog = normalize_update_notes(notes);
    format!(
        "检查结果
{}

当前版本
{}

新版本号
{}

运行环境
{}

更新来源
{}

更新摘要
{}

完整 Changelog
{}

GitHub 仓库
{}

Release 页面
{}",
        status,
        current,
        latest,
        format_runtime_status(local_runtime, remote_runtime),
        update_source,
        summary,
        changelog,
        repo_url,
        release_url
    )
}

fn check_for_updates(app: AppHandle) -> Result<()> {
    let client = build_github_client(90)?;
    let plan = resolve_update_plan(&client, &app)?;
    let current = Version::parse(env!("CARGO_PKG_VERSION"))?;
    let local_runtime = local_runtime_version(&app);
    let runtime_needs_update = match (&plan.runtime_version, &local_runtime) {
        (Some(remote), Some(local)) => remote.trim() != local.trim(),
        (Some(_), None) => true,
        _ => false,
    };
    let admin_update_notice = app_bundle_path()
        .filter(|path| target_requires_admin_update(path))
        .map(|_| {
            "\n\n由于当前应用安装在 /Applications，macOS 接下来会要求管理员密码来完成应用替换。"
                .to_string()
        })
        .unwrap_or_default();
    let summary = format_update_check_dialog(
        &current,
        &plan.latest_version,
        local_runtime.as_deref(),
        plan.runtime_version.as_deref(),
        runtime_needs_update,
        plan.source,
        &plan.notes,
        &plan.repo_url,
        &plan.release_url,
    );
    if plan.latest_version <= current && !runtime_needs_update {
        MessageDialog::new()
            .set_level(MessageLevel::Info)
            .set_title("更新检查结果")
            .set_description(summary)
            .set_buttons(MessageButtons::Ok)
            .show();
        return Ok(());
    }

    let runtime_msg = if runtime_needs_update {
        match (&local_runtime, &plan.runtime_version) {
            (Some(local), Some(remote)) => format!(
                "
运行环境也会从 {} 更新到 {}。",
                local, remote
            ),
            (None, Some(remote)) => format!(
                "
运行环境会安装到版本 {}。",
                remote
            ),
            _ => "
运行环境也会一起更新。"
                .to_string(),
        }
    } else {
        "".to_string()
    };
    if plan.source == UpdateSource::Manifest
        && plan.latest_version > current
        && plan.app_sha256.is_none()
    {
        return Err(anyhow!("更新清单缺少桌面包 sha256，已停止自动更新"));
    }
    if plan.source == UpdateSource::Manifest
        && runtime_needs_update
        && plan.runtime_sha256.is_none()
    {
        return Err(anyhow!("更新清单缺少运行环境 sha256，已停止自动更新"));
    }
    let confirmed = MessageDialog::new()
        .set_level(MessageLevel::Info)
        .set_title("更新检查结果")
        .set_description(format!(
            "{}{}{}

是否立即更新
是：下载并在退出后自动替换、更新运行环境并重开
否：先关闭本窗口，稍后再更新",
            summary, runtime_msg, admin_update_notice
        ))
        .set_buttons(MessageButtons::YesNo)
        .show();
    if confirmed != MessageDialogResult::Yes {
        return Ok(());
    }

    let zip_path = tmp_download_path(APP_NAME, "desktop-update.zip");
    if let Some(window) = app.get_webview_window("main") {
        emit_mode(&window, "update");
        emit_progress(&window, 4, "准备下载更新资产");
        emit_status(&window, "正在下载桌面更新包…");
        download_with_progress(&window, &plan.app_url, &zip_path, 10, 52, "下载桌面更新包")?;
        emit_status(&window, "桌面更新包下载完成，正在校验…");
    } else {
        let client = build_github_client(900)?;
        let mut response = client.get(&plan.app_url).send()?.error_for_status()?;
        let mut file = File::create(&zip_path)?;
        std::io::copy(&mut response, &mut file)?;
    }
    verify_sha256(&zip_path, plan.app_sha256.as_deref(), "桌面更新包")?;

    let mut runtime_archive_path = None;
    if runtime_needs_update {
        if let Some(runtime_url) = plan.runtime_url.as_ref() {
            let runtime_path = tmp_download_path(APP_NAME, "runtime-update.tar.gz");
            if let Some(window) = app.get_webview_window("main") {
                emit_status(&window, "正在下载运行环境更新…");
                download_with_progress(
                    &window,
                    runtime_url,
                    &runtime_path,
                    56,
                    88,
                    "下载运行环境更新",
                )?;
                emit_status(&window, "运行环境更新下载完成，正在校验…");
            } else {
                let client = build_github_client(900)?;
                let mut response = client.get(runtime_url).send()?.error_for_status()?;
                let mut file = File::create(&runtime_path)?;
                std::io::copy(&mut response, &mut file)?;
            }
            verify_sha256(
                &runtime_path,
                plan.runtime_sha256.as_deref(),
                "运行环境更新包",
            )?;
            if let Some(window) = app.get_webview_window("main") {
                emit_progress(&window, 90, "运行环境更新已校验");
            }
            runtime_archive_path = Some(runtime_path);
        }
    }

    if let Some(window) = app.get_webview_window("main") {
        emit_status(&window, "更新下载完成，准备替换应用并重开…");
        emit_progress(&window, 94, "替换应用并重开");
    }
    install_downloaded_app(
        app,
        &zip_path,
        runtime_archive_path.as_deref(),
        plan.runtime_version.as_deref(),
    )?;
    Ok(())
}

fn trigger_reinstall(app: AppHandle) {
    if let Some(window) = app.get_webview_window("main") {
        let win = window.clone();
        let app_handle = app.clone();
        thread::spawn(
            move || match runtime_bootstrap(app_handle.clone(), win.clone(), true) {
                Ok(session) => {
                    if let Some(state) = app_handle.try_state::<AppState>() {
                        if let Ok(mut slot) = state.session.lock() {
                            *slot = Some(session.clone());
                        }
                    }
                    emit_ready(&win, &frontend_url(session.web_port, session.backend_port));
                }
                Err(err) => emit_error(&win, &format!("重新安装失败: {err:#}")),
            },
        );
    }
}

fn cleanup_state(app: &AppHandle) {
    if let Some(state) = app.try_state::<AppState>() {
        if let Ok(mut shutdown) = state.web_shutdown.lock() {
            if let Some(flag) = shutdown.take() {
                flag.store(true, Ordering::Relaxed);
            }
        }
        if let Ok(session_slot) = state.session.lock() {
            if let Some(session) = session_slot.as_ref() {
                stop_runtime(&session.paths);
            }
        }
    }
}

fn runtime_bootstrap(
    app: AppHandle,
    window: WebviewWindow,
    force_runtime_install: bool,
) -> Result<RuntimeSession> {
    emit_mode(
        &window,
        if force_runtime_install {
            "repair"
        } else {
            "launch"
        },
    );
    emit_status(&window, "正在检查安装配置…");
    let paths = ensure_runtime_installed(&app, &window, force_runtime_install)?;
    let web_port = choose_port_with_preference(DEFAULT_FRONTEND_PORT)?;
    let backend_port = choose_free_port()?;
    let chart_port = choose_free_port()?;

    let shutdown = Arc::new(AtomicBool::new(false));
    let _server_handle =
        start_static_server(paths.frontend_dir.clone(), web_port, shutdown.clone())?;
    if let Some(state) = app.try_state::<AppState>() {
        if let Ok(mut slot) = state.web_shutdown.lock() {
            *slot = Some(shutdown);
        }
    }

    start_runtime(&paths, &window, backend_port, chart_port)?;
    emit_progress(&window, 100, "星阙 已准备完成");
    Ok(RuntimeSession {
        paths,
        backend_port,
        web_port,
    })
}

fn main() {
    tauri::Builder::default()
        .manage(AppState::default())
        .menu(build_menu)
        .setup(|app| {
            let app_handle = app.handle().clone();
            let window = app
                .get_webview_window("main")
                .context("main window missing")?
                .clone();
            set_window_zoom(&app_handle, DEFAULT_ZOOM)?;
            thread::spawn(move || {
                match runtime_bootstrap(app_handle.clone(), window.clone(), false) {
                    Ok(session) => {
                        if let Some(state) = app_handle.try_state::<AppState>() {
                            if let Ok(mut slot) = state.session.lock() {
                                *slot = Some(session.clone());
                            }
                        }
                        emit_ready(
                            &window,
                            &frontend_url(session.web_port, session.backend_port),
                        );
                    }
                    Err(err) => emit_error(&window, &format!("星阙 初始化失败:\n{err:#}")),
                }
            });
            Ok(())
        })
        .on_menu_event(|app, event| {
            let id = event.id();
            if id == MENU_CHECK_UPDATES {
                let app_handle = app.clone();
                thread::spawn(move || {
                    if let Err(err) = check_for_updates(app_handle.clone()) {
                        MessageDialog::new()
                            .set_level(MessageLevel::Error)
                            .set_title("检查更新失败")
                            .set_description(format!("{err:#}"))
                            .set_buttons(MessageButtons::Ok)
                            .show();
                    }
                });
            } else if id == MENU_REINSTALL_RUNTIME {
                trigger_reinstall(app.clone());
            } else if id == MENU_OPEN_LOGS {
                if let Ok(paths) = resolve_runtime_paths(app) {
                    let _ = ensure_dir(&paths.logs_dir);
                    open_path(&paths.logs_dir);
                }
            } else if id == MENU_OPEN_DATA {
                if let Ok(paths) = resolve_runtime_paths(app) {
                    let _ = ensure_dir(&paths.app_data_dir);
                    open_path(&paths.app_data_dir);
                }
            } else if id == MENU_ZOOM_IN {
                let _ = adjust_window_zoom(app, ZOOM_STEP);
            } else if id == MENU_ZOOM_OUT {
                let _ = adjust_window_zoom(app, -ZOOM_STEP);
            } else if id == MENU_ZOOM_RESET {
                let _ = set_window_zoom(app, DEFAULT_ZOOM);
            }
        })
        .build(tauri::generate_context!())
        .expect("error while running 星阙 desktop shell")
        .run(|app, event| {
            if let RunEvent::ExitRequested { .. } = event {
                cleanup_state(app);
            }
        });
}
