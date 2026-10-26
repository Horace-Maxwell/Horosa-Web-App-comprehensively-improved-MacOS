//! 更新清单、发布信息与更新计划,校验和与网络客户端。

use super::*;

#[derive(Debug, Deserialize)]
pub(crate) struct GithubRelease {
    tag_name: String,
    html_url: Option<String>,
    pub(crate) body: Option<String>,
    pub(crate) assets: Vec<GithubAsset>,
}

#[derive(Debug, Deserialize)]
pub(crate) struct GithubAsset {
    pub(crate) name: String,
    browser_download_url: String,
    // GitHub API 恒带 size(字节);容缺以防字段变动。
    // 起 API 回退不再直接组装下载 plan(改为取回 manifest asset,或降级 notify-only),
    // 故本字段当前无消费点;保留以备将来(如发布页展示体积)。
    #[allow(dead_code)]
    #[serde(default)]
    pub(crate) size: Option<u64>,
}

#[allow(dead_code)]
#[derive(Debug, Deserialize)]
pub(crate) struct UpdateManifest {
    pub(crate) version: String,
    pub(crate) tag: Option<String>,
    pub(crate) notes: Option<String>,
    #[serde(rename = "platforms")]
    platforms: HashMap<String, UpdatePlatform>,
}

#[allow(dead_code)]
#[derive(Debug, Deserialize)]
pub(crate) struct UpdatePlatform {
    #[serde(rename = "appUrl")]
    pub(crate) app_url: String,
    #[serde(rename = "dmgUrl")]
    dmg_url: Option<String>,
    #[serde(rename = "pkgUrl")]
    pkg_url: Option<String>,
    #[serde(rename = "runtimeUrl")]
    pub(crate) runtime_url: Option<String>,
    #[serde(rename = "runtimeVersion")]
    pub(crate) runtime_version: Option<String>,
    #[serde(rename = "appSha256")]
    pub(crate) app_sha256: Option<String>,
    #[serde(rename = "pkgSha256")]
    pkg_sha256: Option<String>,
    #[serde(rename = "runtimeSha256")]
    pub(crate) runtime_sha256: Option<String>,
    // manifest v2 增量部件(缺省 = 老 manifest,自动全量)
    #[serde(default)]
    pub(crate) components: Option<Vec<ManifestComponent>>,
    #[serde(default, rename = "componentsLockUrl")]
    pub(crate) components_lock_url: Option<String>,
    #[serde(default, rename = "componentsLockSha256")]
    pub(crate) components_lock_sha256: Option<String>,
    // 进度可视化 v2:资产体积(「提前显示要下多大」的数据源;老 manifest 缺省 None → 前端退化「大小待定」)
    #[serde(default, rename = "appSizeBytes")]
    pub(crate) app_size_bytes: Option<u64>,
    #[serde(default, rename = "pkgSizeBytes")]
    pkg_size_bytes: Option<u64>,
    #[serde(default, rename = "runtimeSizeBytes")]
    pub(crate) runtime_size_bytes: Option<u64>,
    // manifest 级逃生阀:显式 true 才允许把 runtime 退到更旧版本
    // (全网退版应急剧本见 INCREMENTAL_UPDATE_SOP §4.3);缺省 None=false=单调防降级。
    #[serde(default, rename = "allowDowngrade")]
    pub(crate) allow_downgrade: Option<bool>,
}

// manifest v2 的部件条目:客户端 diff(name+sha256)与下载(url)所需;应用细节
// (paths/files/preserve)在 components-lock.json asset 里,经 lockSha256 保真。
#[derive(Debug, Clone, Serialize, Deserialize)]
pub(crate) struct ManifestComponent {
    pub(crate) name: String,
    #[serde(rename = "type")]
    pub(crate) kind: String, // "tree" | "files"
    pub(crate) sha256: String,
    #[serde(default)]
    pub(crate) size: Option<u64>,
    pub(crate) file: String,
    pub(crate) url: String,
}

#[derive(Debug, Clone)]
pub(crate) struct UpdatePlan {
    pub(crate) latest_version: Version,
    pub(crate) notes: String,
    pub(crate) repo_url: String,
    pub(crate) release_url: String,
    pub(crate) app_url: String,
    pub(crate) app_sha256: Option<String>,
    pub(crate) runtime_url: Option<String>,
    pub(crate) runtime_version: Option<String>,
    pub(crate) runtime_sha256: Option<String>,
    // manifest v2 增量部件;GithubApi 回退源恒 None(天然全量)
    pub(crate) components: Option<Vec<ManifestComponent>>,
    pub(crate) components_lock_url: Option<String>,
    pub(crate) components_lock_sha256: Option<String>,
    // 进度可视化 v2:资产体积(GithubApi 回退源恒 None → 前端退化)
    pub(crate) app_size_bytes: Option<u64>,
    pub(crate) runtime_size_bytes: Option<u64>,
    // manifest allowDowngrade 透传(GithubApi 回退源恒 false)
    pub(crate) allow_downgrade: bool,
    pub(crate) source: UpdateSource,
    /// 只通知不安装:主 manifest 与 manifest asset 双双不可得 → 无 sha 可校验。
    /// 信任模型 = HTTPS + sha256;缺 sha 绝不自动下载安装,只引导去发布页。
    pub(crate) notify_only: bool,
    /// 只能走完整安装包的原因(早先安装包留下所有账户可写的共享运行环境:App 内更新收不动权限)。Some ⇒ notify_only。
    /// 存结构化发现、不存成句:话在显示那一刻按界面简繁取(原生对话框随档)
    pub(crate) full_pkg_reason: Option<ForeignSharedTree>,
}

impl UpdatePlan {
    /// 只通知不自动下载时给用户看的那句(原因不同,话不同;按当前界面简繁档)
    pub(crate) fn notify_only_message(&self) -> String {
        self.notify_only_message_in(shell_script_is_hant())
    }

    pub(crate) fn notify_only_message_in(&self, hant: bool) -> String {
        match &self.full_pkg_reason {
            Some(reason) => fill_placeholders(
                &shell_text_in("update.notify_only.full_pkg", hant),
                &[("reason", reason.message_in(hant).as_str())],
            ),
            None => shell_text_in("update.notify_only.no_manifest", hant),
        }
    }
}

/// 共享运行环境权限的更新策略:有「别的账户所有、所有账户可写」的旧树 ⇒ 这一次只通知、引导用完整安装包
pub(crate) fn apply_shared_tree_policy(plan: &mut UpdatePlan, finding: Option<ForeignSharedTree>) {
    if let Some(reason) = finding {
        plan.notify_only = true;
        plan.full_pkg_reason = Some(reason);
    }
}

#[derive(Debug, Clone, Copy, PartialEq, Eq)]
pub(crate) enum UpdateSource {
    Manifest,
    /// 主 manifest URL 不可达(5xx/CDN 故障),但经 GitHub API 定位到 release 里的
    /// manifest asset 并取回 —— 完整 sha/部件信息俱在,与 Manifest 同等可信。
    ManifestViaApi,
    GithubApi,
}

// 本地假 release 全链路验证入口:仅 `--features update-url-override` 的
// 开发构建才编译此代码路径;发布二进制无此分支 → 出站仅 GitHub 铁律不破。
// verify_update_experience_local.sh 用 HOROSA_UPDATE_BASE_OVERRIDE=http://127.0.0.1:PORT
// 把 manifest/runtime/资产全部指到本地 python http.server。
#[cfg(feature = "update-url-override")]
fn update_base_override() -> Option<String> {
    std::env::var("HOROSA_UPDATE_BASE_OVERRIDE")
        .ok()
        .filter(|v| !v.trim().is_empty())
}

#[cfg(not(feature = "update-url-override"))]
fn update_base_override() -> Option<String> {
    None
}

pub(crate) fn expected_runtime_url(config: &ReleaseConfig) -> String {
    if let Some(base) = update_base_override() {
        return format!(
            "{}/{}",
            base.trim_end_matches('/'),
            config.runtime_asset_name
        );
    }
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
    if let Some(base) = update_base_override() {
        return format!(
            "{}/{}",
            base.trim_end_matches('/'),
            config.update_manifest_name
        );
    }
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

pub(crate) fn unix_ts() -> u64 {
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

pub(crate) fn build_github_client(timeout_secs: u64) -> Result<Client> {
    Client::builder()
        .timeout(Duration::from_secs(timeout_secs))
        .build()
        .context("build http client")
}

pub(crate) fn sha256_digest(path: &Path) -> Result<String> {
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

pub(crate) fn verify_sha256(path: &Path, expected: Option<&str>, label: &str) -> Result<()> {
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

// manifest 获取(签名制度已于 2026-07-04 应用户决定取消——信任模型回到
// HTTPS + GitHub 账号 + 资产 sha256;签名制度已取消):
// Fetched=清单可用;Absent=不存在/网络失败/JSON 异常 → 允许走 GitHub API fallback。
pub(crate) enum ManifestFetch {
    Fetched(UpdateManifest),
    Absent,
}

pub(crate) fn fetch_update_manifest(client: &Client, manifest_url: &str) -> ManifestFetch {
    let Ok(response) = client
        .get(manifest_url)
        .header("User-Agent", "HorosaDesktop")
        .header("Cache-Control", "no-cache")
        .header("Pragma", "no-cache")
        .send()
    else {
        return ManifestFetch::Absent;
    };
    if !response.status().is_success() {
        return ManifestFetch::Absent;
    }
    let Ok(manifest_bytes) = response.bytes() else {
        return ManifestFetch::Absent;
    };
    match serde_json::from_slice::<UpdateManifest>(&manifest_bytes) {
        Ok(manifest) => ManifestFetch::Fetched(manifest),
        Err(_) => ManifestFetch::Absent,
    }
}

// manifest → plan 的纯映射(可测;主通道与 API-asset 回退通道共用,零手抄分叉)。
pub(crate) fn plan_from_manifest(
    manifest: UpdateManifest,
    config: &ReleaseConfig,
    platform_key: &str,
    source: UpdateSource,
) -> Option<UpdatePlan> {
    let platform = manifest.platforms.get(platform_key)?;
    let latest = Version::parse(manifest.version.trim()).ok()?;
    let repo_url = format!(
        "https://github.com/{}/{}",
        config.repo_owner, config.repo_name
    );
    let release_tag = manifest
        .tag
        .clone()
        .unwrap_or_else(|| format!("{}{}", config.release_tag_prefix, latest));
    let release_url = format!("{}/releases/tag/{}", repo_url, release_tag);
    Some(UpdatePlan {
        latest_version: latest,
        notes: manifest
            .notes
            .clone()
            .unwrap_or_else(|| "See GitHub release notes.".to_string()),
        repo_url,
        release_url,
        app_url: platform.app_url.clone(),
        app_sha256: normalize_checksum(platform.app_sha256.clone()),
        runtime_url: platform.runtime_url.clone(),
        runtime_version: platform.runtime_version.clone(),
        runtime_sha256: normalize_checksum(platform.runtime_sha256.clone()),
        components: platform.components.clone(),
        components_lock_url: platform.components_lock_url.clone(),
        components_lock_sha256: normalize_checksum(platform.components_lock_sha256.clone()),
        app_size_bytes: platform.app_size_bytes,
        runtime_size_bytes: platform.runtime_size_bytes,
        allow_downgrade: platform.allow_downgrade.unwrap_or(false),
        source,
        notify_only: false,
        full_pkg_reason: None,
    })
}

fn api_manifest_fetch_enabled() -> bool {
    std::env::var("HOROSA_UPDATE_API_MANIFEST_FETCH")
        .map(|v| v != "0")
        .unwrap_or(true)
}

// API 回退时,先在 release assets 里找 manifest 资产并取回真 manifest
// (horosa-latest.json 本身就是 release 的一个 asset,发布脚本随包上传)。
pub(crate) fn fetch_manifest_via_release_asset(
    client: &Client,
    release: &GithubRelease,
    manifest_name: &str,
) -> Option<UpdateManifest> {
    if !api_manifest_fetch_enabled() {
        return None;
    }
    let asset = release.assets.iter().find(|a| a.name == manifest_name)?;
    match fetch_update_manifest(client, &cache_busted_url(&asset.browser_download_url)) {
        ManifestFetch::Fetched(manifest) => Some(manifest),
        ManifestFetch::Absent => None,
    }
}

pub(crate) fn resolve_update_plan(client: &Client, app: &AppHandle) -> Result<UpdatePlan> {
    let mut plan = resolve_update_plan_from_sources(client, app)?;
    apply_shared_tree_policy(&mut plan, legacy_open_shared_tree());
    Ok(plan)
}

fn resolve_update_plan_from_sources(client: &Client, app: &AppHandle) -> Result<UpdatePlan> {
    let config = load_release_config(app)?;
    let platform_key = current_platform_key();

    let manifest_url = cache_busted_url(&update_manifest_url(&config));
    if let ManifestFetch::Fetched(manifest) = fetch_update_manifest(client, &manifest_url) {
        if let Some(plan) =
            plan_from_manifest(manifest, &config, platform_key, UpdateSource::Manifest)
        {
            return Ok(plan);
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

    // 一级回退:经 API 定位 manifest asset → 取回真 manifest → 走含 sha 的正常通道。
    if let Some(manifest) =
        fetch_manifest_via_release_asset(client, &release, &config.update_manifest_name)
    {
        if let Some(plan) = plan_from_manifest(
            manifest,
            &config,
            platform_key,
            UpdateSource::ManifestViaApi,
        ) {
            ledger_mark(
                "rust.update_manifest_via_api",
                Some(serde_json::json!({ "tag": release.tag_name })),
            );
            return Ok(plan);
        }
    }

    // 二级降级:manifest 与其 asset 双双不可得 → notify-only。
    // 绝不再无 sha 自动下载安装(旧行为的安全洞):只把版本/发布页告诉用户。
    let latest = parse_version(&release.tag_name)?;
    let repo_url = format!(
        "https://github.com/{}/{}",
        config.repo_owner, config.repo_name
    );
    ledger_mark(
        "rust.update_notify_only",
        Some(serde_json::json!({ "tag": release.tag_name })),
    );
    Ok(UpdatePlan {
        latest_version: latest,
        notes: release.body.unwrap_or_default(),
        repo_url: repo_url.clone(),
        release_url: release
            .html_url
            .clone()
            .unwrap_or_else(|| format!("{}/releases/tag/{}", repo_url, release.tag_name)),
        app_url: String::new(),
        app_sha256: None,
        runtime_url: None,
        runtime_version: None,
        runtime_sha256: None,
        components: None,
        components_lock_url: None,
        components_lock_sha256: None,
        app_size_bytes: None,
        runtime_size_bytes: None,
        allow_downgrade: false,
        source: UpdateSource::GithubApi,
        notify_only: true,
        full_pkg_reason: None,
    })
}
