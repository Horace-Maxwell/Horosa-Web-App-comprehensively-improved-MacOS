# Horosa Web + App（GitHub 可上传版）

更新时间：2026-03-09

这个仓库现在同时承担两件事：

- 普通用户下载并安装 `星阙`
- 开发者查看源码、构建、调试和发布

如果你只是想安装使用，请先看最前面的“下载安装”部分，后面的源码和构建说明都可以先跳过。

## 下载一键安装包

普通用户不要先克隆仓库，也不用自己找脚本。

请直接去这里下载：

- Release 页面：
  [https://github.com/Horace-Maxwell/Horosa-Web-App-comprehensively-improved-MacOS/releases/latest](https://github.com/Horace-Maxwell/Horosa-Web-App-comprehensively-improved-MacOS/releases/latest)
- Mac 下载（推荐，Apple Silicon）：
  [Horosa-Desktop-macos-arm64.dmg](https://github.com/Horace-Maxwell/Horosa-Web-App-comprehensively-improved-MacOS/releases/latest/download/Horosa-Desktop-macos-arm64.dmg)
- 离线安装包（弱网 / 转手安装）：
  [Horosa-Installer-macos-arm64-offline-pkg.zip](https://github.com/Horace-Maxwell/Horosa-Web-App-comprehensively-improved-MacOS/releases/latest/download/Horosa-Installer-macos-arm64-offline-pkg.zip)

请按场景下载：

- `Horosa-Desktop-macos-arm64.dmg`
  - 适合：绝大多数普通 Mac 用户
  - 特点：标准 DMG 安装路径，拖入 `Applications` 后直接打开；如果需要首次准备运行环境，会在 app 内自动完成
- `Horosa-Installer-macos-arm64-offline-pkg.zip`
  - 适合：中国大陆、弱网、离线转发给别人安装
  - 特点：zip 内自带离线 `.pkg`，本机组件已内置，安装后可直接打开使用

其他 `.pkg`、`.zip`、`runtime`、`manifest` 文件都是安装器或自动更新器内部使用的支持资产，普通用户不用单独处理。

## 安装步骤

推荐安装方式：

1. 下载 `Horosa-Desktop-macos-arm64.dmg`
2. 打开 DMG
3. 把 `星阙.app` 拖入 `Applications`
4. 从 `/Applications/星阙.app` 打开
5. 如果检测到这台 Mac 上已有 app、本机组件或旧缓存，先在 app 内完成“安装审查”，手动勾选这次要替换的资产
6. 如果是首次准备运行环境，等待 app 内完成初始化

离线安装方式：

1. 下载 `Horosa-Installer-macos-arm64-offline-pkg.zip`
2. 解压 zip
3. 双击里面的 `.pkg`
4. 如果 macOS 仍拦截，再运行同目录 `Open-XingQue-Unsigned.command` 作为兜底
5. 安装完成后，从 `/Applications/星阙.app` 打开；离线包会把所需本机组件一起装好，不会在首启时再去联网下载

说明：

- 当前短期仍未接入 Developer ID / notarization，所以第一次安装或第一次打开时，系统可能会要求你确认放行
- 如果后续你在应用内点“检查更新”，而应用安装在 `/Applications`，macOS 也会按标准再要求一次管理员密码来完成替换
- `Open-XingQue-Unsigned.command` 现在只作为兜底，不再是默认安装步骤
- 正常用户不需要打开 Terminal，也不需要自己安装 Python、Java、Node
- DMG 路线会优先表现成标准 Mac app：双击 app 直接开窗口，首次准备在 app 内完成
- 安装、修复、更新都会先显示“安装审查”，列出这次将处理的已安装资产
- 离线 `.pkg` 已经把运行所需组件带在安装包里，安装完成后应可直接打开使用，不再把联网下载当兜底
- 如果离线路径损坏，启动页会优先显示“重新安装离线包”恢复卡片，技术细节默认收在第二层
- 离线安装完成后，启动页会用“已准备好，可直接打开使用”的语气展示状态，不再把日志或工程术语放到主视图中心

## 只有在你想看源码时，才继续往下看

## 最简单的用法

如果你是开发者，想把源码仓库直接跑起来，只看这一段就够了：

1. 下载或克隆这个仓库。
2. 双击 `Horosa_OneClick_Mac.command`。
3. 等待脚本完成安装、构建和启动。
4. 浏览器会自动打开本地页面。

说明：
- 第一次运行需要联网下载依赖。
- 第一次会比较慢，后面再启动会快很多。
- 如果你只是普通用户，不要走这个源码入口，优先去上面的 Release 下载一键安装包。

## 根目录现在只保留一个入口

为了避免误操作，根目录现在只保留：

- `Horosa_OneClick_Mac.command`
  - 这是唯一推荐双击的文件。
  - 如果之前已经准备过依赖和构建产物，它会直接启动。
  - 如果当前机器还没准备好，它会自动补齐依赖、构建并启动。

其余 Mac 工具已经移动到：

- `tools/mac/`

## 按场景操作

### 1. 第一次在这台 Mac 上运行

双击：

- `Horosa_OneClick_Mac.command`

它会尽量自动完成这些事：

- 检测或安装 Homebrew
- 准备 Java 17、Node、Python
- 安装 Python 依赖
- 构建前端 `dist-file`
- 构建后端 `astrostudyboot.jar`
- 尝试启动 Redis / MongoDB（完整功能需要）
- 自动打开本地页面

### 2. 之前已经跑过，现在只想再打开

还是双击：

- `Horosa_OneClick_Mac.command`

当前版本会先检查本地是否已经准备好；如果已经准备好，就直接打开，不再重复走完整部署。
如果源码比现有 `dist-file` 或 `astrostudyboot.jar` 更新，它会自动切回重建流程，不会继续偷用旧构建产物。

### 3. 启动后，想确认项目是不是正常

双击：

- `tools/mac/Horosa_SelfCheck_Mac.command`

它会自动检查：

- 页面和接口是否能打开
- `8899` 和 `9999` 是否正常工作
- 主限法相关接口和前端展示是否一致
- `主限法盘` 是否能在浏览器里按当前时间正确更新外圈双盘

### 4. 准备上传 GitHub

先执行：

```bash
./scripts/repo/clean_for_github.sh
```

然后再做 `git add`、`git commit`、`git push`。

这个清理步骤的目的是避免把本地运行时、构建产物和日志一起传上去。

## 先记住这几个事实

- 默认端口：
  - 前端 `8000`
  - Python 服务 `8899`
  - Java 后端 `9999`
- 如果默认端口被占用，脚本会自动换到空闲端口。
- 一旦脚本为你打开了新页面，请优先使用那个新页面，不要继续用旧标签页。
- 运行日志默认会写到 `diagnostics/horosa-run-issues.log`。

## 常见问题

### `java 17+ is required`

重新运行：

- `Horosa_OneClick_Mac.command`

脚本会优先尝试自动安装；如果 Homebrew 不可用，也会尝试项目内直连方案。

### `python runtime cannot import cherrypy`

重新运行：

- `Horosa_OneClick_Mac.command`

它会重新补齐 Python 依赖和虚拟环境。  
当前版本如果检测到 `.runtime/mac/venv` 已损坏、迁移后 shebang 失效，或者旧 `pip` 指向了错误路径，也会自动删除后重建，不需要手工修 venv。

### `node 18+ is required`

重新运行：

- `Horosa_OneClick_Mac.command`

### 页面提示 `127.0.0.1:8899` 或本地服务未就绪

通常先做这两步：

1. 关闭旧的 Horosa 页面标签页。
2. 重新双击 `Horosa_OneClick_Mac.command`。

原因通常不是“功能本身坏了”，而是页面还连着旧端口、旧副本，或者服务已经停止。

### 主限法表格看起来不像当前方法

如果你刚切换了：

- `Core-Alchabitius`
- `Horosa原方法`

但浏览器里表格仍像旧结果，当前版本会在 `重新计算` 时自动把 `/chart` 的主限法 rows 与 `/predict/pd` 强制对齐。  
也就是说，只要重新计算成功，用户看到的主限法表格就应当和当前后端分支一致，不再允许出现“页面显示一种方法、后端实际跑另一种方法”的情况。

### 启动很慢，提示服务超时

可以重试，并在终端环境里加大等待时间：

```bash
HOROSA_STARTUP_TIMEOUT=300 ./Horosa_OneClick_Mac.command
```

如果还是失败，再看：

- `diagnostics/horosa-run-issues.log`
- `Horosa-Web/.horosa-local-logs/`

### 同一台机器开了多个 Horosa 副本

当前版本会尽量自动避开已占用端口。  
但你仍然应该使用启动脚本刚刚打开的那个页面，因为它会带上当前副本对应的后端地址。

## 高级指令

下面这些内容是给需要调试、打包或特殊部署的人看的。普通使用可以跳过。

### 高级脚本

- `tools/mac/Horosa_Local.command`
  - 高级手动启动入口。
  - 更适合开发或排查问题时单独使用。
- `tools/mac/Horosa_SelfCheck_Mac.command`
  - 本地一键自检入口。
- `tools/mac/Prepare_Runtime_Mac.command`
  - 用来准备离线 runtime 包。
  - 更适合打包或迁移，不建议日常使用，也不建议直接提交到 GitHub。

### 常用环境变量

- `HOROSA_SKIP_DB_SETUP=1`
  - 跳过 Redis / MongoDB 自动安装与启动。
- `HOROSA_SKIP_BUILD=1`
  - 跳过前后端构建，前提是你已经有现成构建产物。
- `HOROSA_SKIP_TOOLCHAIN_INSTALL=1`
  - 跳过 Homebrew 和工具链安装。
- `HOROSA_SKIP_LAUNCH=1`
  - 只做预检和构建，不自动打开页面。
- `HOROSA_STARTUP_TIMEOUT=300`
  - 把启动等待时间改成 300 秒，适合慢机器首启。
- `HOROSA_SELF_CHECK_STOP_AT_END=1`
  - 让 `tools/mac/Horosa_SelfCheck_Mac.command` 在检查结束后自动关闭本次拉起的服务。
- `HOROSA_KEEP_SERVICES_RUNNING=0`
  - 只有在你明确希望关闭启动窗口后自动停服务时才使用。
- `HOROSA_DIAG_FILE=<path>`
  - 自定义诊断日志文件路径。
- `HOROSA_DIAG_DIR=<path>`
  - 自定义诊断目录。

### 自定义下载源或版本

如果你的网络环境特殊，也可以手动指定下载地址或版本：

- `HOROSA_JDK17_URL=<url>`
- `HOROSA_NODE_VERSION=<version>`
- `HOROSA_NODE_URL=<url>`
- `HOROSA_PYTHON_URL=<url>`
- `HOROSA_MAVEN_VERSION=<version>`
- `HOROSA_MAVEN_URL=<url>`

### 浏览器级巡检

如果你的机器上已经有带 Playwright 的 Python，`tools/mac/Horosa_SelfCheck_Mac.command` 还会继续做一轮浏览器级检查。  
也可以手动指定 Python：

```bash
HOROSA_BROWSER_CHECK_PYTHON=/path/to/python ./tools/mac/Horosa_SelfCheck_Mac.command
```

检查结果会写到：

- `runtime/browser_horosa_master_check.json`

## 目录定位

- 前端源码：`Horosa-Web/astrostudyui/src/`
- Java 后端源码：`Horosa-Web/astrostudysrv/`
- Python 图表服务：`Horosa-Web/astropy/websrv/webchartsrv.py`
- 一键脚本：`scripts/mac/bootstrap_and_run.sh`
- 自检脚本：`scripts/mac/self_check_horosa.sh`
- Python 依赖清单：`scripts/requirements/mac-python.txt`
- Windows Codex 主限法盘复现包：`WINDOWS_CODEX_PRIMARY_DIRECTION_CHART_REPRO_KIT/`
