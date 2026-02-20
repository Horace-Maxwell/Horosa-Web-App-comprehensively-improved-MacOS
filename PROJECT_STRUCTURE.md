# Horosa Web 项目结构（GitHub 上传版）

更新时间：2026-02-20

## 1) 根目录（入口）

- `Horosa_OneClick_Mac.command`：Mac 一键部署+启动主入口
- `Horosa_Local.command`：已安装依赖后的快速启动入口
- `Horosa_Local_Windows.bat` / `Horosa_Local_Windows.ps1`：Windows 启动入口
- `Prepare_Runtime_Mac.command` / `Prepare_Runtime_Windows.*`：离线 runtime 打包脚本
- `README.md`：部署和上传说明
- `PROJECT_STRUCTURE.md`：目录结构说明（本文件）

## 2) 主业务代码

- `Horosa-Web/`

### 2.1 前端（Umi/React）

- `Horosa-Web/astrostudyui/src/`：前端业务源码
- `Horosa-Web/astrostudyui/public/`：静态资源
- `Horosa-Web/astrostudyui/dist-file/`：构建产物（GitHub 版默认不提交）
- `Horosa-Web/astrostudyui/node_modules/`：依赖目录（不提交）

### 2.2 Java 后端（Maven 多模块）

- `Horosa-Web/astrostudysrv/`
  - 关键模块：`boundless`、`basecomm`、`image`、`astrostudy`、`astrostudycn`、`astroreader`、`astrodeeplearn`、`astroesp`、`astrostudyboot`
  - 启动 Jar：`Horosa-Web/astrostudysrv/astrostudyboot/target/astrostudyboot.jar`（构建产物，不提交）

### 2.3 Python 图表服务

- `Horosa-Web/astropy/astrostudy/`：算法实现
- `Horosa-Web/astropy/websrv/`：服务入口
- 主入口：`Horosa-Web/astropy/websrv/webchartsrv.py`

### 2.4 本地运行脚本（主工程内）

- `Horosa-Web/start_horosa_local.sh`
- `Horosa-Web/stop_horosa_local.sh`
- `Horosa-Web/verify_horosa_local.sh`

## 3) 自动化脚本（新增整理）

- `scripts/mac/bootstrap_and_run.sh`
  - Mac 首次自动安装依赖、构建、启动的核心脚本
- `scripts/requirements/mac-python.txt`
  - Mac Python 依赖清单
- `scripts/repo/clean_for_github.sh`
  - 清理 node_modules/target/runtime/logs，准备上传 GitHub

## 4) runtime 与缓存目录

- `runtime/README.md`：runtime 说明
- `runtime/*`：离线打包产物目录（默认不提交）
- `.runtime/`：一键脚本生成的本地 Python venv（默认不提交）

## 5) modules（扩展参考资料）

- `modules/fengshui/naqi/`
- `modules/reference/kintaiyi-master/`
- `modules/reference/xuan-utils-pro-master/`
- `modules/reference/zhong-zhou-zi-wei-dou-shu-2/`

## 6) 建议检索路径

- 改前端页面：`Horosa-Web/astrostudyui/src/components/`
- 改前端模型：`Horosa-Web/astrostudyui/src/models/`
- 改后端接口：`Horosa-Web/astrostudysrv/astrostudyboot/`
- 改 Python 服务：`Horosa-Web/astropy/websrv/`
- 排查启动日志：`Horosa-Web/.horosa-local-logs/`
