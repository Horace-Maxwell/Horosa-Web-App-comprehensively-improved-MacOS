# Horosa Desktop Installer

这是 Horosa 的独立 macOS 桌面安装器工程，和主业务代码隔离。

## 普通用户下载入口

如果你要告诉别人“去哪里下载一键安装包”，优先给这两个地址：

- Release 页面：
  [https://github.com/Horace-Maxwell/Horosa-Web-App-comprehensively-improved-MacOS/releases/latest](https://github.com/Horace-Maxwell/Horosa-Web-App-comprehensively-improved-MacOS/releases/latest)
- 离线安装包（弱网 / 转手分发）：
  [Horosa-Installer-macos-arm64-offline.pkg](https://github.com/Horace-Maxwell/Horosa-Web-App-comprehensively-improved-MacOS/releases/latest/download/Horosa-Installer-macos-arm64-offline.pkg)

普通用户不要自己猜文件名，直接下载：

- `Horosa-Installer-macos-arm64-offline.pkg`
  - 适合：所有普通用户，尤其是中国大陆、弱网、离线拷给别人安装
  - 特点：已签名、已公证、安装后可直接打开使用

下载后步骤要说明清楚：

1. 下载 `Horosa-Installer-macos-arm64-offline.pkg`
2. 双击 `.pkg` 开始安装
3. 从 `/Applications/星阙.app` 启动
4. 如果检测到这台 Mac 上已有 app、本机组件或旧缓存，先在 app 内完成“安装审查”，手动勾选这次要替换的资产
5. 离线安装完成后必须可直接打开，不再走联网准备
6. 如果系统提示安全确认，按标准 macOS 路径在“系统设置 -> 隐私与安全性”中放行

其他 release 资产都不是给普通用户手动挑选的，应该放在说明后面，不要放在最前面干扰他们。`DMG` 公开入口已取消，不再继续分发。

目标：

- 交付离线 `.pkg` 作为唯一公开安装入口。
- 日常启动使用原生 `.app`，内置浏览窗口，不弹 Terminal。
- 菜单栏提供“检查更新”，支持自动下载、校验、替换、重开。
- 如果应用安装在 `/Applications`，应用内更新会按 macOS 标准弹出管理员密码框来完成替换。
- 更新过程不删除用户数据。

## 目录

- `src-tauri/`: 原生桌面壳、更新器、后台启动管理
- `web/`: 首次初始化、修复、更新事务显示页
- `config/release_config.json`: GitHub Release 与运行时资产配置
- `config/release_notes.md`: GitHub Release 正文模板说明
- `installer-scripts/postinstall.template`: `.pkg` 安装后下载 runtime 的脚本模板
- `scripts/package_runtime_payload.sh`: 打包 runtime payload
- `scripts/build_desktop_release.sh`: 构建 `.app zip`、离线 `.pkg`、`horosa-latest.json`
- `scripts/verify_desktop_packaging.sh`: 一键验收脚本
- `scripts/generate_icon.sh`: 从透明圆角星空图标源生成 macOS app icon、iconset 与 icns

## 安装模型

用户侧现在只认一个文件：

- `Horosa-Installer-macos-arm64-offline.pkg`

Release 页面建议使用中英文双语提示，明确告诉普通用户：

- 普通用户：下载离线 `.pkg`
- 中国大陆、弱网、离线转发给别人：同样下载离线 `.pkg`

离线路径：

1. 双击 `Horosa-Installer-macos-arm64-offline.pkg`
2. `.pkg` 把 `星阙.app` 安装到 `/Applications`
3. `postinstall` 优先使用包内自带 runtime 归档，不再依赖额外下载

如果首次启动阶段网络不通、Release 资产尚未上传或 runtime 下载校验失败，app 会保留日志并提示重试，不要求用户自己修脚本。

首次打开 `星阙.app` 后：

1. 原生窗口展示正式安装/初始化页
2. 所有安装、修复、更新都会先进入“安装审查”，列出 app、本机组件和缓存等已安装资产
3. 优先复用 `/Users/Shared/Horosa/runtime/current`；离线路径下不再回退到联网准备
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
3. 对外下载安装只保留一个公开入口：
   - 主入口：`Horosa-Installer-macos-arm64-offline.pkg`
4. 发布资产必须至少同时上传：
   - `Horosa-Desktop-macos-arm64.zip`
   - `Horosa-Installer-macos-arm64-offline.pkg`
   - `horosa-latest.json`
   - runtime 独立 release 中的 `horosa-runtime-macos-arm64.tar.gz`
5. `horosa-latest.json` 必须指向同一 tag 下的版本化资产 URL
6. Release 需要是正式版 latest，不要把预发布误当最新稳定版
7. 发布前必须跑 `HOROSA_DESKTOP_SKIP_REBUILD=1 scripts/verify_desktop_packaging.sh`，避免验收阶段重复触发 Apple 签名与公证

普通用户不需要理解其他资产，只需要下载离线 `.pkg`。轻量在线 `.pkg` 与 `DMG` 公开入口都已取消；其余 release 资产继续保留给安装器与自动更新器使用。

只要这几条不破，客户端就会优先抓到固定 manifest，再按 manifest 中的准确 URL 和哈希完成更新。

## Apple Developer 正式分发准备

如果要把这套离线 `.pkg` 作为面向陌生用户的正式外部分发包，先准备好 Apple Developer 材料：

- `Developer ID Application`
- `Developer ID Installer`
- `notarytool` keychain profile（默认约定为 `horosa-notary`）

先在发布机执行：

```bash
cd /Users/horacedong/Desktop/Horosa-Primary Direction Trial/Horosa_Desktop_Installer
./scripts/check_apple_signing_prereqs.sh
```

脚本会只读检查：

- 当前用户 keychain 中是否存在唯一可用的 `Developer ID Application`
- 当前用户 keychain 中是否存在唯一可用的 `Developer ID Installer`
- `xcrun notarytool` 是否能通过 `horosa-notary` 连到 Apple notarization 服务

如果三项都通过，就可以进入正式外部分发模式。默认会优先自动识别本机可用的 `Developer ID` 身份，并使用 `horosa-notary` profile；如果你的机器上未来存在多张同类证书，优先直接复制 `check_apple_signing_prereqs.sh` 打印出来的 `export` 行。手动导出时也可以显式指定这三个环境变量：

```bash
export APPLE_SIGNING_IDENTITY="Developer ID Application: Your Name (TEAMID)"
export APPLE_INSTALLER_IDENTITY="Developer ID Installer: Your Name (TEAMID)"
export NOTARYTOOL_KEYCHAIN_PROFILE="horosa-notary"
```

## 本地构建与验收

```bash
cd /Users/horacedong/Desktop/Horosa-Primary Direction Trial/Horosa_Desktop_Installer
./scripts/build_desktop_release.sh
./scripts/verify_desktop_packaging.sh
```

启动页与窗口状态也必须作为桌面交付的一部分检查：

- 启动控制台只保留一套 Daily / Offline Ready / Failed 共用骨架，真实进度仍然由后端 `__horosaProgress(pct, message, indeterminate)` 实时驱动，不允许只写死几个展示状态
- Daily、Offline Ready、Failed 三种语义状态必须同时检查进度数字、状态 chip、Pipeline、日志、CTA 与标题文案是否自洽
- 错误态不能再弹出旧的大恢复面板遮住主进度区，恢复动作应回到同一页面内的绿色主 CTA、日志和诊断入口
- 启动页必须统一使用最终星阙 icon，不能混用临时 SVG 或旧图标
- 窗口大小恢复必须采样首个可见窗口帧，不能只看最后结果；如果出现先大后小或大小跳动，发布直接阻断

可直接运行：

```bash
python3 scripts/verify_launcher_console_states.py
```

正式外部分发构建：

```bash
cd /Users/horacedong/Desktop/Horosa-Primary Direction Trial/Horosa_Desktop_Installer
HOROSA_PUBLIC_DISTRIBUTION=1 ./scripts/build_desktop_release.sh
HOROSA_DESKTOP_SKIP_REBUILD=1 ./scripts/verify_desktop_packaging.sh
./scripts/verify_public_distribution_readiness.sh
```

第一条构建命令是唯一会触发 Apple 正式签名、公证与 staple 的步骤。后两条只复用已经生成的产物做验收，不再重新构建，也不再重新提交 notarization。

正式构建会做额外动作：

- `.app` 使用 `Developer ID Application` + hardened runtime + timestamp 签名
- 离线 `.pkg` 使用 `Developer ID Installer` 签名
- 对 `星阙.app` 与 `Horosa-Installer-macos-arm64-offline.pkg` 分别提交 notarization
- 对二者分别 `staple`
- 在 `.app` 完成 `staple` 后再生成 `Horosa-Desktop-macos-arm64.zip`

发布到 GitHub Release 前，不再需要准备仓库内的版本说明文件。
发布脚本会直接根据当前版本号、安装入口、自动更新资产和内置双语模板生成 GitHub Release 页面正文。

发布到 GitHub Release：

```bash
cd /Users/horacedong/Desktop/Horosa-Primary Direction Trial/Horosa_Desktop_Installer
./scripts/publish_github_release.sh
```

正式外部分发发布：

```bash
cd /Users/horacedong/Desktop/Horosa-Primary Direction Trial/Horosa_Desktop_Installer
HOROSA_PUBLIC_DISTRIBUTION=1 ./scripts/publish_github_release.sh
```

这个脚本会：

- 先以 `HOROSA_DESKTOP_SKIP_REBUILD=1` 跑一遍本地验收，复用已签名、公证、staple 的现有产物
- 创建或更新当前版本对应的 GitHub Release
- 覆盖上传离线 PKG、桌面 app zip、manifest 和 runtime 等发布资产
- 轮询校验 `releases/latest/download/horosa-latest.json`
- 确认客户端更新入口可以抓到当前版本

验收脚本会检查：

- Rust 项目 `cargo fmt --check` 与 `cargo check`
- runtime payload、`.zip`、`.pkg`、`horosa-latest.json` 是否成功生成
- 版本号是否同步
- manifest 中的平台、URL、SHA-256 是否完整
- 离线 `.pkg` 是否能把 bundled runtime 正确部署到 shared runtime
- shared runtime 是否能真实拉起 Horosa 后端服务
- kentang/kin 新技法全量 smoke 后，普通命盘接口仍必须成功，防止 Swiss Ephemeris 全局路径被新技法污染后退化成 `param error`

## 当前产物

默认输出目录：`dist/`

- `Horosa-Desktop-macos-arm64.zip`
- `Horosa-Installer-macos-arm64-offline.pkg`
- `horosa-runtime-macos-arm64.tar.gz`
- `horosa-latest.json`

## 说明

这套工程现在支持两种模式：

- 默认模式：ad-hoc 本地构建，适合开发和自测
- `HOROSA_PUBLIC_DISTRIBUTION=1`：Developer ID 签名 + notarization，适合正式对外分发

正式分发前，务必通过：

- `./scripts/check_apple_signing_prereqs.sh`
- `./scripts/verify_desktop_packaging.sh`
- `./scripts/verify_public_distribution_readiness.sh`
