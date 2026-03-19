# Horosa Desktop Installer

这是 Horosa 的独立 macOS 桌面安装器工程，和主业务代码隔离。

## 普通用户下载入口

如果你要告诉别人“去哪里下载一键安装包”，优先给这三个地址：

- Release 页面：
  [https://github.com/Horace-Maxwell/Horosa-Web-App-comprehensively-improved-MacOS/releases/latest](https://github.com/Horace-Maxwell/Horosa-Web-App-comprehensively-improved-MacOS/releases/latest)
- Mac 下载（推荐，Apple Silicon）：
  [Horosa-Desktop-macos-arm64.dmg](https://github.com/Horace-Maxwell/Horosa-Web-App-comprehensively-improved-MacOS/releases/latest/download/Horosa-Desktop-macos-arm64.dmg)
- 离线安装包（弱网 / 转手分发）：
  [Horosa-Installer-macos-arm64-offline-pkg.zip](https://github.com/Horace-Maxwell/Horosa-Web-App-comprehensively-improved-MacOS/releases/latest/download/Horosa-Installer-macos-arm64-offline-pkg.zip)

普通用户不要自己猜文件名，按场景下载：

- `Horosa-Desktop-macos-arm64.dmg`
  - 适合：绝大多数普通 Mac 用户
  - 特点：标准 DMG 安装路径，拖入 `Applications` 后直接打开；如果缺少运行环境，会在 app 内自动准备
- `Horosa-Installer-macos-arm64-offline-pkg.zip`
  - 适合：中国大陆、弱网、离线拷给别人安装
  - 特点：包更大，但本机组件已内置，安装后可直接打开使用

下载后步骤要说明清楚：

1. 推荐方式：下载 `Horosa-Desktop-macos-arm64.dmg`，打开 DMG，把 `星阙.app` 拖入 `Applications`
2. 从 `/Applications/星阙.app` 启动
3. 如果检测到这台 Mac 上已有 app、本机组件或旧缓存，先在 app 内完成“安装审查”，手动勾选这次要替换的资产
4. 如果是首次准备运行环境，等待 app 内完成初始化
5. 如果你下载的是离线安装包，再解压 zip 并运行其中的 `.pkg`；离线安装完成后必须可直接打开，不再走联网准备
6. `Open-XingQue-Unsigned.command` 只在系统拦截时作为兜底，不再是默认第一步

其他 release 资产都不是给普通用户手动挑选的，应该放在说明后面，不要放在最前面干扰他们。

目标：

- 交付标准 `DMG + .app` 主安装路径，同时保留离线 `.pkg` 作为弱网兜底。
- 首次启动允许在 app 内联网准备 runtime，减少首包体积。
- 日常启动使用原生 `.app`，内置浏览窗口，不弹 Terminal。
- 菜单栏提供“检查更新”，支持自动下载、校验、替换、重开。
- 如果应用安装在 `/Applications`，应用内更新会按 macOS 标准弹出管理员密码框来完成替换。
- 更新过程不删除用户数据。

## 目录

- `src-tauri/`: 原生桌面壳、更新器、后台启动管理
- `web/`: 首次初始化、修复、更新事务显示页
- `config/release_config.json`: GitHub Release 与运行时资产配置
- `installer-scripts/postinstall.template`: `.pkg` 安装后下载 runtime 的脚本模板
- `scripts/package_runtime_payload.sh`: 打包 runtime payload
- `scripts/build_desktop_release.sh`: 构建 `.app`、`.dmg`、`.pkg`、`horosa-latest.json`
- `scripts/verify_desktop_packaging.sh`: 一键验收脚本
- `scripts/generate_icon.sh`: 生成圆角白底黑字“星阙”图标

## 安装模型

用户侧现在主要认两个文件：

- `Horosa-Desktop-macos-arm64.dmg`
- `Horosa-Installer-macos-arm64-offline-pkg.zip`

Release 页面建议使用中英文双语提示，明确告诉普通用户：

- 普通 Mac 用户：下载 `DMG`
- 中国大陆、弱网、离线转发给别人：下载离线 `.pkg zip`

推荐路径：

1. 打开 `DMG`
2. 拖入 `Applications`
3. 双击 `/Applications/星阙.app`
4. 如果缺少运行环境，app 内自动准备

离线路径：

1. 解压 `Horosa-Installer-macos-arm64-offline-pkg.zip`
2. `.pkg` 把 `星阙.app` 安装到 `/Applications`
3. `postinstall` 优先使用包内自带 runtime 归档，不再依赖额外下载

如果首次启动阶段网络不通、Release 资产尚未上传或 runtime 下载校验失败，app 会保留日志并提示重试，不要求用户自己修脚本。

首次打开 `星阙.app` 后：

1. 原生窗口展示正式安装/初始化页
2. 所有安装、修复、更新都会先进入“安装审查”，列出 app、本机组件和缓存等已安装资产
3. 优先复用 `/Users/Shared/Horosa/runtime/current`；如果没有共享 runtime，就在用户态目录完成下载与安装
4. 只有被勾选为“替换”的资产才会被处理，未勾选的内容会尽量保留
5. 后台启动 Python / Java 服务
6. 内置 WebView 自动切到星阙主界面

离线 `.pkg` 例外：

1. `postinstall` 会直接确保共享本机组件可用
2. 首次打开时不再回退到联网下载本机组件
3. 如果离线安装结果损坏，app 只会提示重新安装离线包，不会偷偷转为联网修复
4. 启动页会把恢复动作放在主视图里，日志和原始错误默认退到第二层
5. 离线安装完整可用时，主视图会直接显示“已准备好，可直接打开使用”，不再让工程术语主导页面

正常流程下用户不会看到 Terminal。

## 更新模型

更新入口：`Horosa -> 检查更新`

更新策略：

- 优先读取固定清单 `horosa-latest.json`
- 清单里记录当前最新版本、平台对应的 `.zip` / `.pkg` / runtime URL 与 SHA-256
- 开始下载前先显示“安装审查”，列出本次将要替换的 app、本机组件和缓存
- 客户端下载后先做 SHA-256 校验，再执行替换
- `.app` 替换采用备份旧包再写入新包的方式，失败自动回滚
- 当目标应用位于 `/Applications` 时，更新阶段会请求 macOS 管理员授权，然后再完成替换与重开
- runtime 切换采用 `current -> previous -> current` 事务式切换，失败自动回滚
- 替换完成后自动重开到原 `.app` 位置

数据保留策略：

- 应用更新只替换 `.app`
- runtime 更新会按审查结果只替换被勾选的共享或用户态本机组件
- 用户数据目录不会被删除

## 如何确保 GitHub 每次更新都能被客户端准确抓到

这套方案依赖固定 manifest，而不是只靠“最新 release 的某个随机资产名”。发布时必须保持以下规则：

1. 三个版本号始终一致：`package.json`、`src-tauri/Cargo.toml`、`src-tauri/tauri.conf.json`
2. Git tag 使用严格递增的 semver，例如 `v1.0.0`
3. 对外下载安装需要明确分流：
   - 主入口：`Horosa-Desktop-macos-arm64.dmg`
   - 离线入口：`Horosa-Installer-macos-arm64-offline-pkg.zip`
4. 发布资产必须至少同时上传：
   - `Horosa-Desktop-macos-arm64.dmg`
   - `Horosa-Desktop-macos-arm64.zip`
   - `Horosa-Installer-macos-arm64.pkg`
   - `Horosa-Installer-macos-arm64-pkg.zip`
   - `Horosa-Installer-macos-arm64-offline.pkg`
   - `Horosa-Installer-macos-arm64-offline-pkg.zip`
   - `horosa-latest.json`
   - runtime 独立 release 中的 `horosa-runtime-macos-arm64.tar.gz`
5. `horosa-latest.json` 必须指向同一 tag 下的版本化资产 URL
6. Release 需要是正式版 latest，不要把预发布误当最新稳定版
7. 发布前必须跑 `scripts/verify_desktop_packaging.sh`

普通用户不需要理解其他资产，只需要在 `DMG` 和离线 `.pkg zip` 之间选对入口。其余 release 资产继续保留给安装器与自动更新器使用。

只要这几条不破，客户端就会优先抓到固定 manifest，再按 manifest 中的准确 URL 和哈希完成更新。

## 本地构建与验收

```bash
cd /Users/horacedong/Desktop/Horosa-Primary Direction Trial/Horosa_Desktop_Installer
./scripts/build_desktop_release.sh
./scripts/verify_desktop_packaging.sh
```

发布到 GitHub Release：

```bash
cd /Users/horacedong/Desktop/Horosa-Primary Direction Trial/Horosa_Desktop_Installer
./scripts/publish_github_release.sh
```

这个脚本会：

- 先跑一遍本地验收
- 创建或更新当前版本对应的 GitHub Release
- 覆盖上传 DMG、PKG、离线 PKG、更新 zip、manifest 等发布资产
- 轮询校验 `releases/latest/download/horosa-latest.json`
- 确认客户端更新入口可以抓到当前版本

验收脚本会检查：

- Rust 项目 `cargo fmt --check` 与 `cargo check`
- runtime payload、`.dmg`、`.zip`、`.pkg`、`horosa-latest.json` 是否成功生成
- 对外交付 zip 是否能正常解压出 `.pkg`
- 版本号是否同步
- manifest 中的平台、URL、SHA-256 是否完整
- `.pkg` 的 `postinstall` 是否能下载并部署 shared runtime
- shared runtime 是否能真实拉起 Horosa 后端服务

## 当前产物

默认输出目录：`dist/`

- `Horosa-Desktop-macos-arm64.dmg`
- `Horosa-Desktop-macos-arm64.zip`
- `Horosa-Installer-macos-arm64.pkg`
- `Horosa-Installer-macos-arm64-pkg.zip`
- `Horosa-Installer-macos-arm64-offline.pkg`
- `Horosa-Installer-macos-arm64-offline-pkg.zip`
- `horosa-runtime-macos-arm64.tar.gz`
- `horosa-latest.json`

## 说明

如果需要在其他 mac 上零安全提示分发，还需要进一步接入 Apple Developer ID 签名与 notarization。当前这套工程已经解决了“损坏 app / 直跑 app / 终端弹出 / 更新不稳 / 数据丢失”这些产品侧问题，但不代替苹果官方签名体系。
