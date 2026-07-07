# 网页版一键启动链(Web Local Launch)参考

> 从源码把星阙跑成「本地网页版」的完整入口地图与可调项。桌面 `.pkg` 用户无需阅读本文。
> 制度化:本链全家族由 `release_preflight.sh` 的 **[96]** 哨兵守护(语法/pid 约定跨文件一致/禁 lsof 全表扫描/文档在位)——任何改动启停约定必须保 [96] 绿(见 `Horosa-Web/AGENTS.md`)。

## 家族文件与角色

| 文件 | 角色 |
|---|---|
| `Horosa_OneClick_Mac.command`(根) | **启动入口**:项目完整性检查 → 有产物且不过期 → 快路径直启;否则走自动部署 |
| `Horosa_Stop_Mac.command`(根) | **停止入口**:回收全部端口实例(指纹校验,绝不误伤其它软件) |
| `tools/mac/Horosa_Local.command` | 快路径:运行时探测 → 端口预检(被占自动换口)→ 起 Java/Python/网页服务 → 开浏览器 |
| `scripts/mac/bootstrap_and_run.sh` | 首次部署:工具链(JDK17/Node/Maven/Python,官方源+大陆镜像回退)→ 构建 → 转快路径 |
| `Horosa-Web/start_horosa_local.sh` | 服务层启动(与桌面 app 共用;pid 文件带端口后缀=会话隔离) |
| `Horosa-Web/stop_horosa_local.sh` | 服务层停止(杀前进程指纹校验;`HOROSA_STOP_ALL=1` 扫全实例) |

## 常用可调项(环境变量)

| 变量 | 默认 | 说明 |
|---|---|---|
| `HOROSA_WEB_PORT` / `HOROSA_SERVER_PORT` / `HOROSA_CHART_PORT` | 8000 / 9999 / 8899 | 网页/Java/Python 端口;被占自动换 18000/19999/18899 起的空闲口 |
| `HOROSA_NO_BROWSER` | 0 | =1 只起服务打印 URL,不开浏览器(自检/远程用) |
| `HOROSA_KEEP_SERVICES_RUNNING` | 1 | =1 关网页后服务常驻(再次双击秒开);=0 关窗即停 |
| `HOROSA_FORCE_UI_BUILD` | 0 | =1 忽略产物强制重建前端 |
| `HOROSA_SKIP_DB_SETUP` | 1 | Mongo/Redis 为可选依赖默认不装;=0 显式安装并启动 |
| `HOROSA_SKIP_TOOLCHAIN_INSTALL` / `HOROSA_SKIP_BUILD` / `HOROSA_SKIP_LAUNCH` | 0 | 部署脚本分段开关 |
| `HOROSA_JDK17_URL` / `HOROSA_NODE_URL` / `HOROSA_MAVEN_URL` / `HOROSA_PYTHON_URL` | 内置(官方→TUNA/npmmirror 回退) | 自定义下载源,设了就只用你的 |
| `HOROSA_ALLOW_SYSTEM_PYTHON` | 0 | =1 允许回退系统 Python(默认只认项目内运行时,保证与桌面包一致) |
| `HOROSA_STOP_ALL` | 0 | stop 脚本 =1 时回收所有端口实例(Stop 入口即此模式) |

## 排障三条

1. **双击没反应/提示身份不明**:zip 下载丢了执行位与来源标记——`chmod +x *.command tools/mac/*.command scripts/mac/*.sh`,再右键文件 → 打开;`git clone` 获取则天然无此问题。
2. **提示端口被占**:正常会自动换口;若确有异物占用备用口,`lsof -nP -iTCP:<口> -sTCP:LISTEN` 查明后释放,或用 `HOROSA_*_PORT` 指定新口。
3. **服务起没起/日志在哪**:诊断日志 `diagnostics/horosa-run-issues.log`(根目录),各服务原始日志 `Horosa-Web/.horosa-local-logs/<时间戳>/`;一键回收所有服务用 `Horosa_Stop_Mac.command`。
