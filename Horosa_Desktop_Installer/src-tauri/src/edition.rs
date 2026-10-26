//! 构建身份:应用名 / 标识 / 更新仓库坐标,以及改名构建的数据隔离与迁移。

// ⚠️ 本仓身份三常量必须与 tauri.conf/release_config 一致:
// APP_NAME 用于 /Applications 定位、更新解压路径、窗口标题;APP_IDENTIFIER 用于 defaults 偏好域清理;
// DEFAULT_REPO_NAME 是读不到打包配置时的更新兜底源。任何一个配错取值,
// 就会去碰其它构建的安装位/偏好域/更新通道(串台事故)。
pub(crate) const APP_NAME: &str = "星阙";
pub(crate) const APP_IDENTIFIER: &str = "com.horacedong.horosa";

pub(crate) const DEFAULT_REPO_OWNER: &str = "Horace-Maxwell";
pub(crate) const DEFAULT_REPO_NAME: &str = "Horosa-Web-App-comprehensively-improved-MacOS";
