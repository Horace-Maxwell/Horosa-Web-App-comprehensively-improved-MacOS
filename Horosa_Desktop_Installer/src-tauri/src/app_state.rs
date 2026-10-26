//! 进程级共享状态 AppState 及其缺省值。

use super::*;

pub(crate) struct AppState {
    pub(crate) session: Mutex<Option<RuntimeSession>>,
    pub(crate) web_shutdown: Mutex<Option<Arc<AtomicBool>>>,
    pub(crate) zoom_level: Mutex<f64>,
    pub(crate) review: AssetReviewCoordinator,
    pub(crate) window_state_persistence_ready: AtomicBool,
    // v2.2.1 非阻塞软件内升级:后台下载完成后暂存,等用户主动点「重启更新」时消费。
    pub(crate) staged_update: Mutex<Option<StagedUpdate>>,
    // 修复(更新后卡顿)C①:更新完成通知文本。runtime_bootstrap 开头对 update-complete 标记
    // 「读取即消费」(解析后立刻删除磁盘标记),把通知缓存于此;本次首启成功后再弹窗。
    // 失败时磁盘标记已删 → 下次启动不会再误走 300s 全量慢路径(杜绝「次次都慢」)。
    pub(crate) pending_update_notice: Mutex<Option<String>>,
}

// v2.2.1 后台已下载并校验完成、等待用户重启安装的更新。
// 增补 Serialize/Deserialize:下载完成即落盘 staged-update.json,进程被杀/
// 用户退出后下次启动逐资产重验 sha 直接恢复「已就绪」态,免重下几百 MB。
// 全字段 #[serde(default)]:老档新壳向前兼容(缺字段=默认,恢复门自会因资产/版本不符弃档)。
#[derive(Clone, Serialize, Deserialize)]
pub(crate) struct StagedUpdate {
    #[serde(default)]
    pub(crate) zip_path: Option<PathBuf>,
    #[serde(default)]
    pub(crate) runtime_archive_path: Option<PathBuf>,
    #[serde(default)]
    pub(crate) runtime_roots: Vec<PathBuf>,
    #[serde(default)]
    pub(crate) runtime_version: Option<String>,
    #[serde(default)]
    pub(crate) target_version: String,
    #[serde(default)]
    pub(crate) app_should_update: bool,
    #[serde(default)]
    pub(crate) runtime_should_update: bool,
    // 增量部件更新(下载校验完毕):Some = 应用阶段走部件手术;None = 全量 tar。
    #[serde(default)]
    pub(crate) staged_components: Option<StagedComponents>,
}

// 已下载校验完成的增量部件集:new_lock 是新版 components-lock.json 全文(paths/files/
// preserve 应用细节的真值源),archives 只含 sha 有变化的部件。
#[derive(Clone, Serialize, Deserialize)]
pub(crate) struct StagedComponents {
    #[serde(default)]
    pub(crate) archives: Vec<(ManifestComponent, PathBuf)>,
    #[serde(default)]
    pub(crate) new_lock_json: serde_json::Value,
    #[serde(default)]
    pub(crate) new_lock_text: String,
}

impl Default for AppState {
    fn default() -> Self {
        Self {
            session: Mutex::new(None),
            web_shutdown: Mutex::new(None),
            zoom_level: Mutex::new(DEFAULT_ZOOM),
            review: AssetReviewCoordinator::default(),
            window_state_persistence_ready: AtomicBool::new(false),
            staged_update: Mutex::new(None),
            pending_update_notice: Mutex::new(None),
        }
    }
}
