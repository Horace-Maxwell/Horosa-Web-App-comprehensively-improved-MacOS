# Horosa Web + App（GitHub 可上传版）

更新时间：2026-02-20

目标：这个仓库上传到 GitHub 后，在任意一台 Mac 上都可以通过一次点击完成依赖准备、构建并启动当前功能。

## Mac 一键部署（推荐入口）

1. 下载/克隆仓库后，双击：
   - `Horosa_OneClick_Mac.command`
2. 首次运行会自动完成：
   - 安装或检测 Homebrew
   - 安装运行依赖（Java 17、Maven、Node、Python）
   - 创建 Python 虚拟环境并安装 `cherrypy/jsonpickle/pyswisseph`
   - 构建前端 `dist-file`
   - 构建 Java 后端 `astrostudyboot.jar`（含依赖模块）
   - 尝试启动本地 Redis / MongoDB（用于完整功能）
   - 自动调用 `Horosa_Local.command` 打开本地页面
3. 首次构建时间可能较长（与网络和机器性能相关），后续启动会快很多。
4. 首次运行需要联网下载依赖（Homebrew / npm / Maven / pip）。

## 常用脚本

- `Horosa_OneClick_Mac.command`：Mac 首次部署 + 启动（推荐）
- `Horosa_Local.command`：直接启动（适合依赖已准备完成后）
- `Prepare_Runtime_Mac.command`：打离线 runtime 包（不建议提交 GitHub）
- `scripts/repo/clean_for_github.sh`：清理本地生成物，准备上传 GitHub

可选环境变量（调试用）：
- `HOROSA_SKIP_DB_SETUP=1`：跳过 Redis/MongoDB 自动安装与启动
- `HOROSA_SKIP_BUILD=1`：跳过前后端构建（需已有构建产物）
- `HOROSA_SKIP_TOOLCHAIN_INSTALL=1`：跳过 Homebrew/工具链安装
- `HOROSA_SKIP_LAUNCH=1`：只做预检和构建，不自动启动页面

## 上传 GitHub 前建议流程

1. 执行清理脚本：
   - `./scripts/repo/clean_for_github.sh`
2. 检查以下目录没有被提交：
   - `Horosa-Web/astrostudyui/node_modules`
   - `Horosa-Web/**/target`
   - `runtime/mac/java`、`runtime/mac/python`
   - `Horosa-Web/.horosa-local-logs`
3. 再执行 `git add .` / `git commit` / `git push`

> 已通过 `.gitignore` 默认屏蔽本地运行时和构建产物，避免把数 GB 临时文件推到 GitHub。

## 端口与服务

- 前端静态页：`8000`（可用 `HOROSA_WEB_PORT` 覆盖）
- Java 后端：`9999`
- Python 图表服务：`8899`
- Redis（可选/推荐）：`6379`
- MongoDB（可选/推荐）：`27017`

## 目录定位

- 前端源码：`Horosa-Web/astrostudyui/src/`
- Java 后端源码：`Horosa-Web/astrostudysrv/`
- Python 图表服务：`Horosa-Web/astropy/websrv/webchartsrv.py`
- 一键脚本：`scripts/mac/bootstrap_and_run.sh`
- Python 依赖清单：`scripts/requirements/mac-python.txt`

## 常见问题

- `java 17+ is required`：
  - 运行 `Horosa_OneClick_Mac.command` 自动安装，或手动安装 JDK 17+。
- `python runtime cannot import cherrypy`：
  - 重新运行 `Horosa_OneClick_Mac.command`，会重建 venv 并补依赖。
- `services did not become ready in time (need both 8899 and 9999)`：
  - 检查 8899/9999 是否被占用；查看 `Horosa-Web/.horosa-local-logs/` 日志。
