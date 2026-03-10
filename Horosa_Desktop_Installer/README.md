# Horosa Desktop Installer

这是 Horosa 的独立 macOS 桌面安装器工程，和主业务代码隔离。

## 普通用户下载入口

如果你要告诉别人“去哪里下载一键安装包”，优先给这两个地址：

- Release 页面：
  [https://github.com/Horace-Maxwell/Horosa-Web-App-comprehensively-improved-MacOS/releases/latest](https://github.com/Horace-Maxwell/Horosa-Web-App-comprehensively-improved-MacOS/releases/latest)
- 一键安装包直链：
  [Horosa-Installer-macos-universal-pkg.zip](https://github.com/Horace-Maxwell/Horosa-Web-App-comprehensively-improved-MacOS/releases/latest/download/Horosa-Installer-macos-universal-pkg.zip)

普通用户只需要下载：

- `Horosa-Installer-macos-universal-pkg.zip`

下载后步骤要说明清楚：

1. 解压 zip
2. 先运行 `Open-XingQue-Unsigned.command`
3. 如仍被拦截，再右键打开 `Horosa-Installer-macos-universal.pkg`
4. 安装完成后，从 `/Applications/星阙.app` 启动

其他 release 资产都不是给普通用户手动挑选的，应该放在说明后面，不要放在最前面干扰他们。

目标：

- 交付真实 `.pkg` 安装器，而不是“解压即运行”的半安装态。
- 首次安装允许联网下载 runtime 大包，减少首包体积。
- 日常启动使用原生 `.app`，内置浏览窗口，不弹 Terminal。
- 菜单栏提供“检查更新”，支持自动下载、校验、替换、重开。
- 更新过程不删除用户数据。

## 目录

- `src-tauri/`: 原生桌面壳、更新器、后台启动管理
- `web/`: 首次初始化、修复、更新事务显示页
- `config/release_config.json`: GitHub Release 与运行时资产配置
- `installer-scripts/postinstall.template`: `.pkg` 安装后下载 runtime 的脚本模板
- `scripts/package_runtime_payload.sh`: 打包 runtime payload
- `scripts/build_desktop_release.sh`: 构建 `.app`、`.pkg`、`horosa-latest.json`
- `scripts/verify_desktop_packaging.sh`: 一键验收脚本
- `scripts/generate_icon.sh`: 生成圆角白底黑字“星阙”图标

## 安装模型

用户侧只需要认一个文件：`Horosa-Installer-macos-universal-pkg.zip`。

Release 页面建议使用中英文双语提示，明确告诉普通用户只下载这一个 zip。

用户下载并解压它，然后优先运行其中的 `Open-XingQue-Unsigned.command`；如果系统仍拦截，再对 `Horosa-Installer-macos-universal.pkg` 右键打开。

安装器做两段事：

1. `.pkg` 把 `星阙.app` 安装到 `/Applications`
2. `postinstall` 优先从 GitHub Release 下载 runtime payload 到 `/Users/Shared/Horosa/runtime/current`

如果安装阶段网络不通、Release 资产尚未上传、或 runtime 下载校验失败，`.pkg` 不会再整体安装失败；它会写入待补装标记，随后由首次启动继续完成 runtime 安装。

首次打开 `星阙.app` 后：

1. 原生窗口展示正式安装/初始化页
2. 优先复用 `/Users/Shared/Horosa/runtime/current`
3. 后台启动 Python / Java 服务
4. 内置 WebView 自动切到星阙主界面

正常流程下用户不会看到 Terminal。

## 更新模型

更新入口：`Horosa -> 检查更新`

更新策略：

- 优先读取固定清单 `horosa-latest.json`
- 清单里记录当前最新版本、平台对应的 `.zip` / `.pkg` / runtime URL 与 SHA-256
- 客户端下载后先做 SHA-256 校验，再执行替换
- `.app` 替换采用备份旧包再写入新包的方式，失败自动回滚
- runtime 切换采用 `current -> previous -> current` 事务式切换，失败自动回滚
- 替换完成后自动重开到原 `.app` 位置

数据保留策略：

- 应用更新只替换 `.app`
- runtime 更新只替换 `/Users/Shared/Horosa/runtime/current`
- 用户数据目录不会被删除

## 如何确保 GitHub 每次更新都能被客户端准确抓到

这套方案依赖固定 manifest，而不是只靠“最新 release 的某个随机资产名”。发布时必须保持以下规则：

1. 三个版本号始终一致：`package.json`、`src-tauri/Cargo.toml`、`src-tauri/tauri.conf.json`
2. Git tag 使用严格递增的 semver，例如 `v1.0.0`
3. 对外下载安装只主推 `Horosa-Installer-macos-universal-pkg.zip`
4. 发布资产必须同时上传五个文件：
   - `Horosa-Installer-macos-universal-pkg.zip`
   - `Horosa-Installer-macos-universal.pkg`
   - `Horosa-Desktop-macos-universal.zip`
   - `horosa-runtime-macos-universal.tar.gz`
   - `horosa-latest.json`
5. `horosa-latest.json` 必须指向同一 tag 下的版本化资产 URL
6. Release 需要是正式版 latest，不要把预发布误当最新稳定版
7. 发布前必须跑 `scripts/verify_desktop_packaging.sh`

普通用户不需要理解其他资产，只需要下载这一个 zip。其余 release 资产继续保留给安装器与自动更新器使用。

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
- 覆盖上传 5 个发布资产
- 轮询校验 `releases/latest/download/horosa-latest.json`
- 确认客户端更新入口可以抓到当前版本

验收脚本会检查：

- Rust 项目 `cargo fmt --check` 与 `cargo check`
- runtime payload、`.zip`、`.pkg`、`horosa-latest.json` 是否成功生成
- 对外交付 zip 是否能正常解压出 `.pkg`
- 版本号是否同步
- manifest 中的平台、URL、SHA-256 是否完整
- `.pkg` 的 `postinstall` 是否能下载并部署 shared runtime
- shared runtime 是否能真实拉起 Horosa 后端服务

## 当前产物

默认输出目录：`dist/`

- `Horosa-Installer-macos-universal.pkg`
- `Horosa-Installer-macos-universal-pkg.zip`
- `Horosa-Desktop-macos-universal.zip`
- `horosa-runtime-macos-universal.tar.gz`
- `horosa-latest.json`

## 说明

如果需要在其他 mac 上零安全提示分发，还需要进一步接入 Apple Developer ID 签名与 notarization。当前这套工程已经解决了“损坏 app / 直跑 app / 终端弹出 / 更新不稳 / 数据丢失”这些产品侧问题，但不代替苹果官方签名体系。
