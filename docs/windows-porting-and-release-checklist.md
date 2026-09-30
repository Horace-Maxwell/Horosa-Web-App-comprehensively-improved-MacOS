# 星阙 Windows 复刻与发布自检指南

最后更新：2026-09-26

这份文档用于把当前 macOS 版星阙完整复刻到 Windows。重点不是照搬 macOS 的脚本，而是把这几轮已经暴露过的错误、易漏点和必须进入 Windows 工作流的自检门槛固定下来。

Windows 版的目标很简单：用户在一台全新 Windows 电脑上安装后，所有命法、卜法、管理命盘、管理事盘、AI 导出、窗口与设置持久化都能稳定使用；关闭、重开、升级版本后不丢数据；发布包从正式渠道下载回来以后仍然能逐项通过机器检查。

## 总原则

- 以“安装后的 Windows App”为准，不以开发服务器为准。
- 以“全新电脑 / 干净 VM / 空白 `%ProgramData%` 和 `%APPDATA%`”为准，不以开发者电脑为准。
- 不要只验证首页能打开，要验证每一个技法端点、每一个管理数据往返、每一个 AI 导出设置分组。
- 不要把 macOS 路径、命令、权限模型硬搬到 Windows。路径、服务启动、安装目录、签名、更新替换都要按 Windows 重新实现。
- 任何新增技法、tab、AI 导出分段、管理字段，都必须同时更新：前端入口、后端/本机服务、结构化快照、AI 导出设置、持久化导入导出、自检脚本。
- 发布前本地安装包要过一遍；发布后从 GitHub 或正式渠道把安装包下载回来，还要再过一遍。
- 任何用户可见的 `param error`、空白导出、导入丢字段、重开丢设置，都要当 release blocker。

## 推荐 Windows 目录模型

不要把可写数据放进 `Program Files`。Windows 版建议分三层：

- App 安装目录：只放只读程序文件，例如 `C:\Program Files\Horosa\星阙` 或安装器选择的目录。
- 机器级共享 runtime：放离线包随附的 Python、Java、Horosa-Web runtime，例如 `%ProgramData%\Horosa\runtime\current`。
- 用户级数据与缓存：放用户设置、窗口状态、下载缓存、日志、WebView 数据，例如 `%APPDATA%\Horosa` 或 `%LOCALAPPDATA%\Horosa`。

关键点：

- App identifier / WebView profile 必须稳定。否则 WebView2 的 localStorage、IndexedDB、AI 设置、命盘/事盘本地库会在升级后像“换了一个 app”一样丢失。
- 离线安装包可以写 `%ProgramData%`，普通 app 运行时优先读共享 runtime，必要时回退到用户级 runtime。
- 所有路径都要支持中文 app 名、空格、非 ASCII 用户名、OneDrive 用户目录、长路径。PowerShell、Rust、Node、Python 都必须全程 quote 路径。
- Windows 要显式处理 UAC：写 `%ProgramData%` 和 `Program Files` 的动作属于安装器/管理员流程；普通 app 运行时不能假设有管理员权限。

## Windows runtime 必须带上的东西

macOS 版曾经出现过“开发环境能用，安装包里缺了东西”。Windows 打包时必须显式列清单，不要靠隐式目录存在。

必须进入 Windows runtime payload：

- `Horosa-Web/astrostudyui/dist-file`
- `Horosa-Web/astropy/__init__.py`
- `Horosa-Web/astropy/astrostudy`
- `Horosa-Web/astropy/websrv`
- `Horosa-Web/flatlib-ctrad2/flatlib`
- `Horosa-Web/flatlib-ctrad2/LICENSE`
- `Horosa-Web/vendor`
- `Horosa-Web/scripts/repairEmbeddedPythonRuntime.py` 的 Windows 等价能力，或明确不需要修复时的替代检查
- `Horosa-Web/astrostudyui/scripts/warmHorosaRuntime.js`
- `runtime/windows/python`，包含 Python 可执行文件、DLL、`site-packages`
- `runtime/windows/java`，建议 Java 17 jlink runtime 或完整 JRE
- `runtime/windows/bundle/astrostudyboot.jar`
- `THIRD_PARTY_NOTICES.md`
- 所有 vendor / kinastro 数据目录、解释文本、星历相关数据
- Swiss Ephemeris / flatlib 所需资源，尤其 `flatlib/resources/swefiles`
- Windows 上 Python `zoneinfo` 需要的 `tzdata`，不能依赖系统自带 IANA 数据

Windows 版不要继续使用 `runtime/mac/...` 目录命名。建议使用：

```text
runtime/windows/python/python.exe
runtime/windows/java/bin/java.exe
runtime/windows/bundle/astrostudyboot.jar
Horosa-Web/start_horosa_local.ps1
Horosa-Web/stop_horosa_local.ps1
```

## 原生库与 CPU 架构不能只靠启动通过

macOS 2.1.1 的 Risk 1 复盘见 [`arm64-native-libs-hardening.md`](arm64-native-libs-hardening.md)。当时发现 Java 后端里有几个 x86_64-only JNI 原生库：`libimagequant`、OpenCV 3.4.2、RXTX 串口。它们不影响普通启动，但如果失败路径写错，可能在某个功能被点到时把类初始化污染成 `ExceptionInInitializerError`。

Windows 复刻时要把这条经验直接放进开发检查清单：

- 每次新增或升级 JNI / DLL / `.pyd` / native JAR，都要列出 `x64`、`arm64`、Windows 版本、VC runtime 依赖和失败路径。
- 不要在静态初始化块里把可选 native load 失败重新抛出。错误架构、缺 DLL、缺依赖时通常是 `UnsatisfiedLinkError` / `Error` 或平台异常，不是普通 `Exception`；可选能力要 `catch(Throwable)` 后设置 availability flag，再由调用方降级。
- 如果某条 native 路径不是核心功能，例如 PNG 调色板压缩、OpenCV 文本检测、IoT 串口，要明确 fallback：写原图、跳过分析、提示该平台不可用，而不是让 app 崩。
- 如果某个 native 依赖当前是死代码，也要把“调用方追踪为零”的证据写进文档。未来一旦接入业务，必须重新评估，而不能沿用旧结论。
- Windows 打包前要跑一遍 native 清单检查，等价于 macOS 的 `find ... '*.jnilib' '*.dylib' '*.so' + lipo -archs`。Windows 可用 `dumpbin /headers`、`sigcheck`、PowerShell 读取 PE machine type，至少确认目标架构和缺失 DLL。
- 构建 / 安装自检不能只跑 `java -version` 或 Python import。发布 gate 必须真正启动安装后的 runtime，打 `/common/time`、chart health、kentang/kin 端点和多时间 `/chart`，这样才能抓到“启动后才加载”的 native 问题。
- macOS 现在用 `Horosa_Desktop_Installer/scripts/verify_runtime_backend_boot.sh` 作为独立兜底脚本：解压打好的 runtime、强制使用内置 Java/Python、等待 chart `/` 与 backend `/common/time` 健康，再可选跑 kentang 端点。Windows 版要做等价的 `verify_runtime_backend_boot_windows.ps1`，不要把这一步混进普通打包脚本里；它应该作为发布前 gate 单独运行，失败就阻止发布。

## 启动服务时最容易漏的点

Windows 启动脚本需要完成 macOS `start_horosa_local.sh` 的等价职责：

- 选择空闲端口：一个给 Python chart / kentang 服务，一个给 Java backend。
- 设置 `PYTHONNOUSERSITE=1`，避免用户系统 Python 污染嵌入 Python。
- 设置 `PYTHONPATH`，必须同时包含：

```text
<runtime>\Horosa-Web\flatlib-ctrad2
<runtime>\Horosa-Web\astropy
```

- 启动 Python chart/kentang 服务。
- 启动 Java backend。
- 等待 chart 服务 `/` 和 signed backend `/common/time` 可访问。
- 写 pid 或 process handle，关闭时可靠清理。
- 输出日志到用户可访问目录，不要只写安装目录。
- 所有服务只监听 `127.0.0.1`，不要监听 `0.0.0.0`。

曾经踩过的坑：

- `PYTHONPATH` 只包含 `astropy`，安装包里命法会找不到 `flatlib` 或行为不稳定。
- 前端只拿到 `srv`，新加入的 kentang/kin 技法没有拿到 chart 服务端口，导致安装包内新功能打到错误端口。
- `qizhengkin` / kinastro 使用 `pyswisseph` 后可能改掉全局 Swiss Ephemeris path，导致后面的普通命盘 `/chart` 报 `param error`。
- 不能只测一个时间。必须用多个日期、时间、时区回打普通命盘，避免某一个 timestamp 碰巧没暴露问题。
- 不能只测开发 checkout。必须从安装后的 runtime 启动服务。

## `param error` 与 Swiss Ephemeris 全局污染

macOS 2.1.0 最危险的一次问题是：安装包里所有功能使用时都显示 `param error`。最终根因不是前端参数，而是同一个 Python 服务进程里，某些 kinastro 模块调用 `swisseph.set_ephe_path("")`，把 Swiss Ephemeris path 清空了。后续普通命盘再调用时找不到 `seas_18.se1` 等 ephemeris 文件，于是被后端包装成 `param error`。

Windows 版必须照这个经验处理：

- `flatlib/resources/swefiles` 必须进入 runtime。
- Windows 的 flatlib / swisseph 初始化层要防止空 path 重置，等价于 macOS 当前的 guard：空 path 时回到 `HOROSA_SWISSEPH_PATH`、已激活路径或 packaged `swefiles`。
- 自检顺序必须是：先跑所有 kentang/kin 端点，再跑普通命盘 `/chart`，最后跑完整 backend smoke。
- 普通命盘回归必须至少包含现代时间、过去时间、未来时间、东八区和 UTC-8/西区时间。
- 任何 `param error` 都不能先归因给用户输入。先查 runtime payload、Swiss Ephemeris path、`PYTHONPATH`、端口注入和共享进程污染。

建议 Windows smoke 的普通命盘样例至少包括：

```text
2026-05-24 09:30:00 +08 Shanghai
2023-05-24 08:41:55 +08 Fuzhou
2027-05-24 20:41:55 +08 Fuzhou
1994-01-17 23:15:00 -08 Los Angeles
```

## 前端服务地址规则

Windows app 打开前端时，URL 必须动态注入这些 query：

```text
srv=<Java backend root>
chartSrv=<Python chart service root>
kentangSrv=<Python chart service root>
v=<cache bust timestamp/version>
```

例如：

```text
http://127.0.0.1:<webPort>/index.html?srv=http%3A%2F%2F127.0.0.1%3A<backendPort>&chartSrv=http%3A%2F%2F127.0.0.1%3A<chartPort>&kentangSrv=http%3A%2F%2F127.0.0.1%3A<chartPort>&v=<ts>
```

必须确认：

- `srv` 只给 Java backend。
- `chartSrv` 给普通星盘和占星计算相关服务。
- `kentangSrv` 给太乙、金口诀、奇门、五兆、太玄、荆诀、神易数、Kin Astro 等所有 kentang/kin 路由。
- 三式合一的路由口径必须单独自检：奇门、太乙走 kentang2017 后端，六壬不走 kentang 后端，继续使用现有本地六壬实现。
- 如果某个技法选项没有对应后端，例如当前 Ken 奇门没有月家完整盘，不要在 UI 中保留它并静默回退旧算法；应从相关页面下拉项移除，旧保存数据打开时归一到受支持的后端口径。
- 前端 `KENTANG_SERVICE_CONFIG` 每加一个模块，都有 path、queryKeys、默认本地端口、测试覆盖。
- 开发时浏览器地址栏里残留的旧 `taiyiSrv`、`jinkouSrv`、固定端口不能当作发布包真相；打包 app 必须由 launcher 注入当前实际端口。

## 当前必须 smoke 的 kentang/kin 路由

Windows 版必须移植并运行 macOS 版 `verify_kentang_runtime_endpoints.py` 的思路。当前至少覆盖以下 17 个 `/pan` 端点：

```text
/taiyi/pan
/jinkou/pan
/qimen/pan
/wangji/pan
/wuzhao/pan
/taixuan/pan
/jingjue/pan
/shenyishu/pan
/shaozi/pan
/tieban/pan
/fendjing/pan
/beiji/pan
/nanji/pan
/chunzi/pan
/xianqin/pan
/cetian/pan
/qizhengkin/pan
```

验收标准：

- HTTP 状态不是 5xx。
- JSON 可解析。
- `ResultCode` 为 `0` 或 `"0"`。
- `Result` 存在，且不是空字符串。
- 这些端点跑完后，再跑普通 `/chart` 多时间点回归和完整 backend smoke。

新增任何 kentang/kin 技法时，第一件事就是把它加入这个清单。没有进清单，就不允许发布。

## 管理命盘 / 管理事盘不能丢字段

Windows 版必须完整保留 localStorage / IndexedDB 管理逻辑，并验证关闭重开、升级版本后数据还在。

命盘管理至少覆盖这些 chart family：

```text
astrochart
indiachart
bazi
ziwei
guolao
qizhengkin
shaozi
tieban
fendjing
beiji
nanji
chunzi
xianqin
cetian
germany
jieqi
```

事盘管理至少覆盖这些 case type：

```text
liuyao
liureng
taiyi
qimen
sanshiunited
suzhan
jinkou
tongshefa
huangji
wuzhao
taixuan
jingjue
shenyishu
```

必须验证：

- 新增、编辑、删除、搜索、分页都正常。
- 导出 JSON 后清空本地数据，再导入，字段完整恢复。
- `payload` 不被覆盖或丢 hidden data。
- `sourceModule`、`chartType`、`caseType` 不被折叠成默认类型。
- `creator === "local"` 的导入记录仍可编辑和删除，不要只依赖 `local-` id 前缀。
- `gpsLat=0`、`gpsLon=0` 不能被当作空值丢掉。
- `memo74`、`memoZiWei`、`doubingSu28`、`gender`、`zone`、`lat`、`lon`、`pos`、`updateTime` 等字段都要 round-trip。
- 旧备份只有 `sourceModule` 时，能推断正确类型。
- 未来未知 module 不要被强行归类成六爻或普通星盘。

建议把这些测试作为 Windows release 必跑：

```bash
cd Horosa-Web/astrostudyui
npm test -- --runInBand src/utils/__tests__/localStorageManagement.test.js
```

Windows 手工验证还要做一次真实 WebView2 关闭重开：

1. 新增一个命盘，选新加入的命法，例如 `qizhengkin` 或 `cetian`。
2. 新增一个事盘，选新加入的卜法，例如 `wuzhao` 或 `shenyishu`。
3. 关闭 app。
4. 重新打开 app。
5. 进入管理命盘/事盘，确认记录仍在，点击进入后回到正确技法页面。
6. 导出本地 JSON，删除记录，导入 JSON，再确认能恢复。

## AI 导出不能从 DOM 硬抓

AI 导出必须优先走结构化快照，不要靠当前页面 DOM 文本复制。DOM 只适合兜底，不适合发布标准。

Windows 版复刻时要确认：

- 每个技法都在 `AI_EXPORT_TECHNIQUES` 中有 key、label、设置项。
- 每个技法都有 `AI_EXPORT_PRESET_SECTIONS`，用户可以选择导出或不导出对应分段。
- 新技法都有结构化 snapshot key，不允许导出空白或串台。
- 每个 tab 的导出 key 能区分当前 tab，例如节气盘春分/夏至/秋分/冬至不能互相混。
- `qizhengkin`、`shaozi`、`tieban`、`fendjing`、`beiji`、`nanji`、`chunzi`、`xianqin`、`cetian` 等 kinastro 技法不能回退到普通 `guolao` 或 generic。
- 金口诀不能回退到六壬；太阳弧不能导成主限法；当前激活页面是什么，导出就必须是什么。
- 旧 AI 导出设置版本升级后，新增分段不能被旧设置过滤掉。

建议 Windows 必跑：

```bash
cd Horosa-Web/astrostudyui
npm test -- --runInBand \
  src/utils/__tests__/aiExport.test.js \
  src/utils/__tests__/aiAnalysisContext.test.js \
  src/utils/__tests__/aiAnalysisSelection.test.js
```

还要跑 app 侧 AI 分析自检：

```bash
python3 scripts/browser_horosa_aianalysis_check.py
```

当前 macOS 版的期望规模是：

- chart techniques: `28`
- case techniques: `8`

如果 Windows 版数量不同，必须写明是产品范围变化；否则视为遗漏。

## 启动控制台必须实时自洽

macOS 2.1.0 后期重做过启动页。这里最容易犯的错不是“好不好看”，而是信息不真实：进度还是 8%，页面却写“已完成”；或者错误态还显示 Ready；或者只做了几个静态 mock，真实启动进度完全不更新。

Windows 版必须按真实启动状态驱动 UI：

- 进度百分比、阶段、主标题、pipeline 勾选/转圈/叉号、右上状态 chip 必须五者一致。
- 8% 左右只能表示刚开始检查；100% 且所有步骤成功后才允许出现 Ready、已完成、进入主界面。
- 错误态要停在失败步骤，后续步骤灰态，不要继续显示 Live。
- “重建/修复 Runtime” 是积极修复动作，用品牌色；红色只表达失败状态，不要把普通重装按钮做成危险色。
- 启动页必须使用最终 app icon，同一套透明圆角资产，不要临时 SVG、旧白底黑字或两个图标混用。
- 进度要能接受任意实际值，例如 8%、26%、42%、73%、100%，不能只支持设计稿里列出的两三个状态。

建议把 macOS 当前 `verify_launcher_console_states.py` 的思路移植到 Windows：

- 用 Playwright 打开启动控制台 HTML。
- 分别注入 Daily Launch、动态中间进度、Offline Ready、Runtime Failed。
- 断言文案、chip、CTA、pipeline class、milestone、日志、icon 数量、旧恢复面板隐藏、无横向/纵向溢出。
- 截图保留到 release artifacts，方便看字体是否挤压。

这次还暴露了一个验收脚本自身易错点：发布验收脚本里 `python3` 不一定是有 Playwright 的 Python。Windows 版不要假设全局 `python` 正确，应支持：

- `HOROSA_PLAYWRIGHT_PYTHON` 或等价环境变量显式指定。
- 自动探测项目虚拟环境、工具链 Python、系统 Python，只有能 `import playwright` 的候选才可用于 UI 自动化验收。
- 如果找不到，不要跳过启动页检查；直接让 release gate 失败并提示安装/指定 Playwright Python。

## 窗口大小和用户设置持久化

macOS 版后面补过窗口大小持久化，但真正的坑是“先跳到默认大小，再跳回保存大小”。Windows 版要避免这个问题。

Windows 实现要点：

- 保存 main、preferences、diagnostics 三类窗口状态。
- 保存逻辑坐标，不直接保存物理像素，否则高 DPI 屏幕会出错。
- 记录 `stateVersion` 和 `coordinateSpace`，给以后迁移用。
- 恢复窗口时要检查当前显示器尺寸，避免窗口跑到屏幕外。
- 最大化状态要单独保存，但不能让过期的最大化标记覆盖用户最后缩小后的真实宽高。macOS 版这次的补丁就是：如果系统还报告 maximized，但记录到的窗口 bounds 已经明显小于显示器，就按非最大化保存。
- 关闭窗口、app 退出、更新前都要 persist 一次。
- 主窗口必须隐藏创建，先应用保存的 size/position/maximized，再 show/focus。
- 如果“隐藏创建后再 set_size”仍然出现先大后小，就不要在静态配置里预建默认主窗口；应在 native 启动代码里读取窗口状态，把保存尺寸直接作为 window builder 的初始尺寸，再 show。
- 启动早期的 `Moved` / `Resized` 事件可能不是用户操作，而是窗口管理器初始化噪声。macOS 版最终做法是在首次 show 后延迟打开窗口状态写回，避免默认尺寸或中间位置污染 `window-state.json`。
- 不要依赖前端 `resizeTo()` 作为 packaged app 的窗口恢复方案；Windows launcher / Tauri / native shell 必须在窗口显示前恢复。
- packaged app 里要让 native shell 成为唯一窗口尺寸控制者。macOS 版最终还在 WebView document-start 注入脚本，锁住 `resizeTo` / `resizeBy` / `moveTo` / `moveBy`，避免前端浏览器版窗口记忆逻辑在页面加载后又抢一次尺寸。
- macOS 版还关闭了系统级 `ApplePersistenceIgnoreState`，并清掉旧 SwiftUI 版本留下的 `NSWindow Frame main-workspace` / `NSSplitView Subview Frames main-workspace`。Windows 复刻时也要检查是否有系统/框架自己的 window restore、window placement 或 registry/AppData frame 缓存会和 Horosa 自己的 `window-state.json` 打架。

持久化文件建议放在 app config dir，不要放在安装目录。Windows 上通常会落到 `%APPDATA%` 或 `%LOCALAPPDATA%` 的 app config 路径。

验证方式：

- 写入一个测试窗口状态，例如 `1180x760 at 120,120`。
- 同时故意写入一个系统/框架层的旧大窗口记录，用来模拟“会先大一下”的真实现场。
- 启动 packaged app。
- 用 UI automation 轮询窗口 bounds。
- 期望第一次可见窗口就是保存尺寸，不能先出现默认尺寸。
- 再测一次：最大化或接近全屏打开，手动缩小窗口，关闭 app，重新打开。期望直接恢复缩小后的 bounds，不能又被 `isMaximized=true` 拉回全屏。

## Windows 图标不能是假圆角

macOS 版曾经出现过“看上去圆角，但实际上是正方形背景加圆角边框”的问题；也出现过视觉上比其他 app 大一圈的问题。Windows 版必须检查 `.ico` 的 alpha 和视觉占位。

要求：

- 源图必须是透明背景 PNG。
- 1024 或最大源图四角 alpha 必须接近 0。
- `.ico` 内至少包含 256x256 PNG layer，并保留 alpha。
- 不要把图标烘焙成白底或黑底正方形。
- 图标内部主体要留足边距，避免开始菜单/任务栏里视觉上比其他软件大一圈。
- 安装包、开始菜单、任务栏、卸载器图标都要用同一套透明资产。

建议把 macOS `verify_icon_alpha.py` 改成 Windows 版：

- 输入源 PNG 和生成的 `.ico`。
- 解析 PNG layer 或用 Pillow 读取 `.ico` 最大帧。
- 断言四角 alpha <= 8，中心 alpha >= 240。
- 额外计算非透明 alpha bounding box，确认主体没有贴边。

## Windows 安装包/更新包要包含的新东西

Windows 不能只打前端 app。必须同时准备：

- 桌面 app 本体，例如 Tauri 生成的 `.exe`、MSI 或 NSIS installer。
- 离线 runtime 包，例如 `horosa-runtime-windows-x64.zip`。
- 离线安装包，把 runtime 包嵌入 installer，而不是首次启动再下载。
- `horosa-latest.json`，包含 Windows platform entry。
- SHA256 校验值。
- Windows 代码签名和 timestamp。
- 第三方 license / notices。
- WebView2 Runtime 处理策略：检测系统 WebView2、引导安装 Evergreen Runtime，或使用合规的固定 runtime。

建议 manifest 结构新增类似：

```json
{
  "platforms": {
    "windows-x86_64": {
      "appUrl": "...",
      "pkgUrl": "...",
      "runtimeUrl": "...",
      "appSha256": "...",
      "pkgSha256": "...",
      "runtimeSha256": "...",
      "runtimeVersion": "2.1.0-runtime5"
    }
  }
}
```

如果未来要支持 arm64 Windows，再单独加 `windows-aarch64`，不要混用 x64 runtime。

## Runtime 版本号不能同名覆盖

这次 macOS 修复后还有一个很重要的发布教训：如果 packaged runtime 代码变了，不要只覆盖同名 runtime 资产。已经安装过旧 runtime 的机器可能因为 manifest 的 `runtimeVersion` 没变而继续复用旧缓存，用户仍然会看到旧 bug。

Windows 版规则：

- App 版本可以仍是 `2.1.0`，但 runtime 内容变了就要 bump runtime tag，例如 `2.1.0-runtime3` -> `2.1.0-runtime5`。
- 如果只修桌面壳窗口、图标、菜单等 native shell 问题，不要重发 runtime。macOS 版为此加入了 `HOROSA_REUSE_REMOTE_RUNTIME=1`，从既有 runtime release 下载 asset 后只重打 app/pkg。
- manifest 的 `runtimeVersion`、`runtimeUrl`、`runtimeSha256` 必须同步更新。
- 安装器、修复流程、自动更新流程都必须比较 runtime manifest version；不匹配就替换 runtime。
- 发布脚本如果发现 runtime hash 变了但 runtimeVersion 没变，必须失败。
- 发布总结必须写明 app tag 和 runtime tag。

## macOS 2.1.0 最终发布复盘要带到 Windows

这次 macOS 2.1.0 最终发布已经证明：本地构建通过不等于发布包可靠，GitHub 上的最终资产也必须被下载回来重验。Windows 复刻时要把这些规则直接写进 release gate。

- App release 名称可以写 `v2.1.0 Beta`，但产品要求“不要放到 prerelease”时，GitHub release 的 `prerelease` 必须是 `false`。不要把名称里的 Beta 和 GitHub prerelease 状态混为一谈。
- App release 和 runtime release 是两条线。macOS 最终是 app tag `v2.1.0`，runtime tag `v2.1.0-runtime5`；Windows 也要在发布总结里分别写清楚 app tag、runtime tag、manifest version、runtimeVersion。
- 只要 frontend/backend/runtime payload 变了，旧 runtime asset 就视为过期。macOS 后期因为奇门/太乙/三式合一路由、启动页、runtime 文件和前端图盘渲染变化，必须持续 bump runtime tag；Windows 不允许继续复用旧 runtime 版本号。
- 如果最后阶段只修 native shell，例如窗口大小恢复、图标、安装器 UI，可以复用远端 runtime；但必须在 manifest 和安装器里证明 runtime hash 没变。
- 奇门遁甲单页和三式合一中的奇门必须走 kentang2017 / Ken 后端；太乙也走 Ken 后端；六壬不走 Ken 后端。这个边界要有单元测试和安装包 smoke，不要靠人工记忆。
- 如果 Ken 后端没有某个排盘选项，例如当前没有可用的月家奇门完整盘，Windows UI 也必须从奇门单页和三式合一里移除该选项；旧保存数据遇到 `paiPanType: 1` 时归一到受支持选项，不能静默回退旧算法。
- 任何“计算源：xxx”这类对用户无意义的实现细节不要出现在正式 UI 或 AI 导出内容里，除非它是用户决策所必需的信息。
- 八字新星阙 UI 的细盘上半区内容溢出时必须能独立纵向滚动；下方大运、流年、流月、流日区域保持固定。Windows WebView 验收时还要确认细盘可见文字栈没有 `filter`、`backdrop-filter`、`transform` 或 `zoom` 造成发糊。
- 紫微斗数四化盘不显示星体亮度，避免亮度字和四化标记/星名重叠；但策天飞星、先秦等借用 kinastro 图盘的页面仍然要保留亮度显示。
- 发布后回下载 e2e 必须至少证明：manifest SHA 与下载文件一致、installer/app/runtime 可展开、icon alpha 仍是真透明、runtime 能启动、17 个 kentang/kin 端点通过、普通 `/chart` 多时间点通过、Java `/common/time` 通过、管理命盘/事盘和 AI 导出测试通过。
- 任何 late steer 改动了后端路由、runtime payload、数据结构、AI 导出结构或管理数据字段，都要把已构建/已签名/已上传的旧资产视为 stale，重新构建、重新验、重新上传覆盖 release。

## Windows 不能照搬的 macOS 细节

这些要全部替换：

- `/Applications/*.app` -> Windows install dir。
- `/Users/Shared/Horosa` -> `%ProgramData%\Horosa` 或用户级 fallback。
- `bash` -> PowerShell 或 Rust 原生启动逻辑。
- `open` -> `Start-Process` 或 Rust `open` crate / Windows API。
- `lsof` -> PowerShell `Get-NetTCPConnection` 或 Rust 端口探测。
- `ditto`、`pkgutil`、`plutil` -> Windows 安装器 / zip / MSI 检查工具。
- `codesign`、`spctl`、`xcrun notarytool` -> Windows Authenticode 签名、timestamp、SmartScreen 友好签名流程。
- `sips`、`.icns` -> `.ico` 生成与 alpha 检查。
- `tar --disable-copyfile`、`.DS_Store`、xattr 清理 -> Windows zip/7z/PowerShell 压缩，另行过滤 `.git`、`__pycache__`、测试缓存、临时文件。

## Windows 特别容易出问题的地方

- WebView2 数据目录变化导致 localStorage / IndexedDB 全丢。
- 安装器覆盖 app 时，旧 exe 仍在运行，Windows 文件锁导致替换失败。
- 嵌入 Python 找到用户机器的 site-packages，结果开发者电脑正常、用户电脑崩。
- `pyswisseph` wheel / DLL 缺失，或者 Swiss Ephemeris 数据路径被其他模块改掉。
- Java backend 需要的 jar 没进 runtime，开发环境用 target 文件，安装包里没有。
- 杀毒软件拦截未签名 exe、脚本或嵌入 runtime。
- PowerShell 默认编码或 cmd 输出导致中文路径/中文日志乱码。
- 防火墙弹窗阻断本地服务。原则上只监听 `127.0.0.1`。
- 端口固定导致冲突。Windows 版也要随机挑空闲端口，并把端口注入 URL。
- `tzdata` 缺失。Windows 上 Python `zoneinfo` 很容易因为没有系统 IANA 数据而失败。
- 路径长度超过 260。打包和运行都要启用长路径友好的实现，至少不要手写短路径假设。
- 旧 runtime 安装源标记、pending marker、缓存归档没有清理，导致安装器误判“已经可用”。
- Beta 文字和 GitHub prerelease 是两件事。可以在 release note 写 beta，但如果产品要求不是 prerelease，就不要把 GitHub release 标成 prerelease。

## Windows 发布前自检顺序

建议每个 Windows release 都按这个顺序跑。顺序不要随便改，因为有些 bug 只有前面污染后面时才出现。

1. 前端单元测试：

```bash
cd Horosa-Web/astrostudyui
npm test -- --runInBand \
  src/integrations/kentang/__tests__/serviceRoot.test.js \
  src/utils/__tests__/localStorageManagement.test.js \
  src/utils/__tests__/aiExport.test.js \
  src/utils/__tests__/aiAnalysisContext.test.js \
  src/utils/__tests__/aiAnalysisSelection.test.js
```

2. 前端构建：

```bash
npm run build
npm run build:file
```

3. Windows runtime import check。等价伪命令：

```powershell
$env:PYTHONNOUSERSITE = "1"
$env:PYTHONPATH = "$RuntimeRoot\Horosa-Web\flatlib-ctrad2;$RuntimeRoot\Horosa-Web\astropy"
& "$RuntimeRoot\runtime\windows\python\python.exe" -c "import cherrypy,jsonpickle,swisseph; import websrv.webchartsrv; print('ok')"
```

4. 启动安装后的 runtime，不是开发 checkout。Windows 应提供等价于 macOS `verify_runtime_backend_boot.sh` 的独立脚本：从最终 runtime zip / 安装目录启动，强制使用 bundled Java/Python，等待 chart health 与 `/common/time`，并负责关停与日志保留。
5. 先跑 kentang/kin 17 个端点。
6. 再跑普通 `/chart` 多日期、多时间、多时区回归。
7. 单独验证奇门/太乙/六壬边界：奇门和太乙走 Ken 后端，六壬继续走本地实现；奇门单页和三式合一都不能出现无后端支撑的月家奇门选项。
8. 再跑 signed backend `/common/time`。
9. 再跑完整 backend runtime smoke：

```bash
HOROSA_SERVER_ROOT=http://127.0.0.1:<backendPort> node Horosa-Web/astrostudyui/scripts/verifyHorosaRuntimeFull.js
```

10. 跑 AIAnalysis app 侧自检。
11. 跑管理命盘/管理事盘真实关闭重开测试。
12. 检查 icon alpha 和主体边距。
13. 检查安装包签名、timestamp、SHA256、manifest Windows platform 字段。
14. 在干净 VM 上模拟全新安装：无开发 checkout、无系统 Python/Java 依赖、空白 `%ProgramData%\Horosa` 和 `%APPDATA%\Horosa`。

## Windows 发布后回下载自检

发布后必须从正式 release 下载回来验证，不要只验证本地 dist。

最少要做：

- 下载 `horosa-latest.json`。
- 下载 Windows installer。
- 下载 app zip 或 installer 内 app payload。
- 下载 runtime zip。
- 用 manifest 里的 SHA256 逐个比对。
- 静默安装到临时目录或干净 VM。
- 展开/安装后检查 app version 等于 manifest version。
- 检查 runtime version 等于 manifest runtimeVersion。
- 启动 app 或 runtime。
- 跑 17 个 kentang/kin 端点。
- 跑普通 `/chart` 多时间点回归。
- 跑 Java backend smoke。
- 跑 AIAnalysis 自检。
- 关闭再打开，确认窗口大小与用户设置恢复且不跳尺寸；还要测最大化后缩小再重开的路径。
- 新增命盘/事盘、导出 JSON、删除、导入、再打开，确认不丢。
- 确认 release 是 draft/prerelease 状态符合产品要求。
- 如果 release 名称包含 Beta，但产品要求正式可见，GitHub API 里 `prerelease` 仍必须是 `false`。
- 如果重新上传覆盖同一个 app tag，必须再次下载最新 assets，不要复用本地旧下载缓存。

发布总结里必须写明这些检查是否通过。只要有一项没跑，不能写“全面完成”。

## 给 Windows 开发的最小验收矩阵

| 类别 | 必须证明 |
|---|---|
| 服务启动 | Python chart/kentang 和 Java backend 从安装后的 runtime 启动 |
| 服务注入 | 前端 URL 同时带 `srv`、`chartSrv`、`kentangSrv` |
| 新技法 | 17 个 kentang/kin `/pan` 端点全部返回结构化 `Result` |
| 传统命盘 | `/chart` 多时间点和完整 backend smoke 通过 |
| 管理命盘 | 所有 chart family 可新增、编辑、搜索、导出、导入、删除、关闭重开不丢 |
| 管理事盘 | 所有 case type 可新增、编辑、搜索、导出、导入、删除、关闭重开不丢 |
| AI 导出 | 每个技法有结构化 snapshot key 和可选分段，不串台、不空白 |
| AI 分析 | 当前 chart/case technique 数量符合预期，单选技法只挂载单选上下文 |
| 用户设置 | AI 导出设置、主题/偏好、窗口大小关闭重开后恢复 |
| 图标 | `.ico` 真透明圆角，四角 alpha 为透明，主体不贴边 |
| 升级 | 旧版本数据、设置、runtime 缓存不被覆盖或误删 |
| Runtime 版本 | runtime 内容变更时 tag 和 manifest version 一起变 |
| 发布包 | 正式下载回来的包通过同一套检查 |

## 新增技法时的提交检查清单

每加一个命法或卜法，都必须逐项回答：

- 前端 tab/入口有吗？
- 本机服务 endpoint 有吗？
- 用户可选项都有 endpoint 或本地实现支撑吗？没有支撑的选项是否已从所有相关页面移除？
- Windows runtime payload 会把相关 Python/vendor/data 文件带进去吗？
- `PYTHONPATH` 能找到它吗？
- 如果使用 `pyswisseph`，是否会污染全局 ephemeris path？
- 管理命盘或管理事盘能保存它吗？
- 导入旧备份能识别它吗？
- `payload` 里隐藏字段会不会在编辑时丢失？
- AI 导出有结构化 snapshot key 吗？
- AI 导出设置有合适的分段吗？
- 旧 AI 导出设置迁移后会包含新增分段吗？
- 单页、三式合一、管理入口、AI 导出、保存数据里的技法口径是否完全一致？
- 安装包后 smoke 覆盖它了吗？
- 发布后回下载 e2e 覆盖它了吗？
- 第三方代码 license 和致谢写了吗？

其中任何一个答案是“不确定”，就不要发布。

## license 与第三方代码

Windows 包必须随包保留第三方 license/notice，不要只放在 GitHub README。

特别注意：

- `flatlib-ctrad2` 的 LICENSE 要随 runtime。
- `Horosa-Web/vendor` 中所有第三方项目要保留原 license。
- 使用 kentang2017 相关代码的地方要标明 MIT license，并在 README 致谢中保留 kentang2017。
- `THIRD_PARTY_NOTICES.md` 要进入 runtime payload。
- Swiss Ephemeris / `pyswisseph` 涉及 AGPL/商业授权边界，Windows 包也必须保留相应 license 说明。

## Windows 文档与脚本建议

建议新建 Windows 专属目录，不要把 macOS 脚本继续改到满是条件分支：

```text
Horosa_Windows_Installer/
  config/release_config.windows.json
  scripts/package_runtime_payload_windows.ps1
  scripts/build_desktop_release_windows.ps1
  scripts/verify_desktop_packaging_windows.ps1
  scripts/verify_github_release_end_to_end_windows.ps1
  scripts/verify_icon_alpha_windows.py
  scripts/verify_kentang_runtime_endpoints.py
```

可以复用的思路：

- manifest 版本对齐检查。
- runtime import check。
- kentang/kin endpoint smoke。
- 多时间点普通命盘回归。
- GitHub release 回下载 e2e。
- icon alpha 检查。
- AIAnalysis 与管理数据单元测试。

不要复用的实现细节：

- macOS pkg/postinstall。
- Apple notarization。
- `/Users/Shared`。
- `.app` bundle layout。
- `.icns` 检查方式。

## 最后一条硬规则

Windows 版完成的定义不是“能打开”，而是：

安装后的 app，在干净 Windows 机器上，不联网也能打开；所有已加入的命法和卜法都能起盘；管理命盘/管理事盘不会丢任何必要信息；AI 导出能按当前页面和当前 tab 输出完整结构化内容；关闭重开和版本升级后用户数据仍在；正式发布包下载回来后仍然通过同一套自检。

## v3.10.0 同步要点(Mac 已落地,Windows 按此对齐)

### AI 流式超时三层语义(修 Windows issue #77)
- `services/aianalysis.js`:空闲看门狗 STALL 默认 90s→**180s**(仅 delta/reasoning 产出事件续命,心跳不续);流总时长上限 MAX 默认 300s→**1800s**(此前 5 分钟硬顶会掐断深思模型的正常长回答)。两默认可被 `providerOptions.streamStallMs / streamMaxStreamMs` 覆盖(毫秒,1s 下限)。
- 设置面板:新增「流式空闲上限(秒)」「流式总时长上限(秒)」两参数;「请求超时(毫秒)」说明改为「仅作用于非流式请求(测试连接/拉模型/取材料)」。
- Java 代理 `AIAnalysisProxyService`:流式请求不再把 requestTimeoutMs 设为 HttpRequest 总时限;providerOptions 剥离清单加 `streamStallMs`/`streamMaxStreamMs`(不下发上游)。
- 契约测试 `services/__tests__/aiStreamWatchdog.test.js` 六例可直接移植。

### 紫微挂载设置(修 Windows issue #76)
- 紫微 AI 挂载设置的传本/排盘开关(含紫云太岁入卦、太岁关系人)补齐 globalCurrent 基线锚——挂载设置真实生效、与主页左栏设置及跨命盘完全隔离。对应 `techniqueMountSettings.js` 紫微段 30 键。

### 真太阳时精度
- `baziLunarLocal.js` 均时差换 NOAA/Meeus 高精度式(旧教科书简式误差 ±1-2 分钟,时辰边界附近会与后端引擎判到不同时辰);经度缺失时回退 gpsLon 并告警,不再静默按钟表时。

### 择日十技法
- Mac 版择日页本版扩至十技法(新增黄历/八字/太乙/紫微/六壬/三式合一/七政/印度择时),前端实现全在 `src/divination/zeri/` 与 `src/components/zeri/`,七政/印度另有 Python 端点 `/qizhengelectionscan` `/indiaelectionscan`。Windows 侧如跟进,以本仓这批文件为准整体移植(判定与主盘同源零第二实现,带全套 jest/pytest 金标)。

## v3.11.0 同步要点(Mac 已落地,Windows 按此对齐)

### 版本 lockstep
- `Horosa_Desktop_Installer/{package.json, src-tauri/Cargo.toml, src-tauri/Cargo.lock, src-tauri/tauri.conf.json, web/app.js(APP_VERSION), config/release_config.json(runtimeVersion=3.11.0-runtime1), scripts/verify_launcher_console_states.py}`、`basecomm RuntimeWire.RUNTIME_VERSION`(改后重建 jar)、三主 README、`CITATION.cff`、`config/release_notes/3.11.0.md`、`UPGRADE_LOG.md`。

### 共享 Java(自 v3.10.0)
- `AIAnalysisController / AIAnalysisMaterialService / AIAnalysisProxyService / AIToolCallSupport / AIWebFetchService(新) / AIWebSearchService(新) / OutboundUrlGuard(新)`;`boundless AppLoggers`(日志落点根修);`boundless/pom.xml` log4j 2.14.1→2.17.2。单测:`astrostudy` 9 个测试类(含工具调用翻译/网页读取/联网检索/出站守卫/缓存断点)可直接移植。

### 共享桌面壳逻辑
- MCP 本机服务 v2(资源/提示/事件流/会话;2026-07-28 修订双纪元)、外部 MCP 客户端(HTTP/stdio,只读准入)、调度心跳(60s,缺省关)、桌面通知(限流去重)、令牌桶限流跟随页面设置。Mac 实现在 `src-tauri/src/{mcp_server,mcp_stdio,mcp_client,main}.rs`;Electron 端按同名命令表复刻(命令清单见 `docs/AI_AGENT_RUNTIME.md`)。

### 共享 Python
- `websrv/webchunzisrv.py`(蠢子数 auto 档以 sxtwl 真算农历月日)、`websrv/webtaiyisrv.py`(博弈分析缺依赖时降级回传)、`vendor/kintaiyi/src/kintaiyi/game_theory.py`(缺 scipy 走纯 numpy 两阶段单纯形 linprog)+ `astropy/tests/test_taiyi_game_theory_{degrade,lp_fallback}.py`。

### 共享前端 · 缩放与版面(本版追加)
- **适用前提**:壳缩放走根元素 CSS `zoom`。Chromium 系内核与新版系统 WebView 同为「rect 反映缩放」语义,下列缺陷在两端同样存在(浮层错位只在「以非 100% 档启动 → 应用内调回 100%」时出现);壳若改用原生页面缩放,换域件全部按实测比值退化为恒等,可原样搬。
- **构建期**:`astrostudyui/scripts/patch-dom-align-zoom.js` 升 v3(`build` / `build:file` 前自动执行,给 `node_modules/dom-align` 两份产物打补丁);打包前确认产物含 `horosa:dom-align-zoom v3`。
- **新文件**:`components/comp/DragModal.js`(取代第三方可拖动对话框)+ `components/comp/__tests__/dragModalZoom.test.js`、`utils/__tests__/zoomDomainPointerHelpers.test.js`、`Horosa_Desktop_Installer/scripts/{audit_popup_geometry.py,popup_geometry.tpl.js}`(浮层几何行为闸,headless,两种缩放语义)。
- **改动**:`utils/zoomDomain.js`(运行期缩放真值只读根元素内联 zoom;`fixedPopupFrame` / `pointerToLocal` / `pointerLocalRatio`;视口系数直接量;SVG `getScreenCTM` 与 `MouseEvent.offsetX/Y` 一致性垫片,一致内核自动不生效,回退键 `horosa.compat.svgCtmZoom` / `horosa.compat.offsetXYZoom`)、`utils/shellZoom.js`(`resolveBootstrapZoom`)、`global.js`、`components/xq-ui/styles.less`(折叠节行 `minmax(0, 1fr)`)、`components/sanshi/SanShiUnitedMain.less`(内层盒不自滚)、手写浮层 / 自绘画布 19 处(玄史 / 七政 / 印占大运浮动面板 / 天文馆 / 择日三浮窗 / 占星地图 / 图形星历 / 3D 盘 / 风水画布)、「窗口高 − 固定数」估高的叶子第二批(紫微资料参考 / 占星地图 / 统摄法 / 塔罗 / 八字 / 择日黄历 / 卜卦盘定盘)。
- **样式(`layouts/app.less`,各端自有副本,按条对齐)**:三式底栏行高 ≡ 栏高 + 三栏栅格显式行 `minmax(0, 1fr)`;辅助页 Tabs 内容链定高 + 子页纵滚;塔罗页根纵向 flex;宫格 `minmax(min-content, 1fr)` + 宿主滚;存储键注册表登记两个回退键(设备本地、不进备份)。
- **验证**:同名 jest 守卫(`zoomDomainPointerHelpers` / `popupAlignStaticGuard` / `popupAlignZoomGuard` / `dragModalZoom` / `layoutDomainStaticGuard`)+ `python3 Horosa_Desktop_Installer/scripts/audit_popup_geometry.py --quick`。零 Java / Python / 壳改动,不必重编 jar。

### 共享前端
- AI 助手全套:`src/utils/aiAgent/**`、`src/utils/aiChat/**`、`src/utils/aiTools/**`、`src/components/aianalysis/**`(含「进阶」页签);挂载链 `src/utils/{aiAnalysisContext,techniqueMountSettings,aiExport}.js`;择日宿主 `src/components/zeri/**`;时间录入 `src/utils/quickDateTimeDigits.js` + `src/components/common/QuickTimeField*`;五兆/推运/印占/七政演禽/蠢子数各页与工具函数。对应测试全部在 `src/utils/__tests__/` 与各组件 `__tests__/`。
- 存储:IndexedDB 升版(新增任务/通知/自动化规则/集成档案四店)与新增 localStorage 键全部登记在 `storageKeyRegistry.js` / `techniqueOnboardingContract.js`,Windows 端注册表须同步。

## v3.11.1 同步要点(Mac 已落地,Windows 按此对齐)

### 版本 lockstep
- 同 v3.11.0 的清单,版本 `3.11.1` / `runtimeVersion` = `3.11.1-runtime1`;`RuntimeWire.RUNTIME_VERSION` 同步(改后重建后端 jar)。

### 共享前端 · 盘面随界面主题重画
- 单源 `src/utils/appearance.js`(`applyAppearanceToDocument`:调色板先切换 → 根属性 → 广播 `horosa:appearance-applied`;`subscribeAppearance` / `syncChartPalette` / `chartColorThemeFor`)+ `src/utils/chartDrawGuard.js` 的 `watchChartAppearance(redraw)`;各盘面宿主(占星单盘 / 双盘 / 三维、紫微、宿盘、二十八宿、七政、六壬、卦、卦占、金口诀、汉堡学派各盘、玄史地图、占星地图)在 `componentDidMount` 订阅、unmount 卸;`components/suzhan/SZConst.js`、`components/su28/Su28Helper.js` 与各绘图类里固化的调色板改为访问时求值(getter);`AstroChart` / `JinKouChart` 的主题回调改为重渲染;`layouts/app.js` / `pages/index.js` 只调 `syncChartPalette(resolvedAppearance)`;主题按钮带 `data-appearance-toggle="1"`。
- **Windows 需要做什么**:同步上述共享件;若 Electron 端有自己的主题切换入口,必须经 `applyAppearanceToDocument`(顺序不可倒,先广播后换调色板会重画一遍旧色),不要直接改 `data-horosa-appearance`;新增任何 d3 / canvas 盘面照 `watchChartAppearance` 接线,不要私写属性观察器;跑 jest `chartThemeFollow.contract`(宿主普查 + 调色板只在单源切换 + 零模块级 / 零实例字段调色板固化 + render 读调色板的回调必重渲染)。巡检判据:切明暗后每个盘面的底色与墨色明度、对比度都要跟主题(暗底深墨 / 亮底淡墨都算没跟)。

### 共享前端 · 排盘设置
- 「新盘种子」:`src/utils/newChartSeeds.js`(种子表 / `newChartSeedValue` / `recordNewChartSeeds` / `resetNewChartSeedKeysToInternalDefaults` / `newChartSeedExtraEntries`)、`models/astro.js`(`newEmptyFields` 读种子)、`utils/recordFieldsRestore.js`(载入记录复位种子键;捕获按内建默认判非默认)、各页亲手改动入口(占星主页 / 八字 / 紫微 / 三式 / 宿盘 / 印占 / 主限法 / 全局设置「时间算法(新命盘的缺省)」)、存储键 `horosa.chart.newChartSeeds.v1`(登记 `storageKeyRegistry.js`);合同测试 `utils/__tests__/newChartSeeds.test.js`;帮助手册七处。语义:新盘按种子、载入记录按记录、缺键回内建默认、存盘捕获按内建默认判非默认。
- 保留机制遗留:七政「报时星 / 罗计取法 / 月孛取法 / 身宫法」首开补空只在非择日内嵌实例、载入了记录不播;铁板「大运步数」限整数;遁甲程序同步性别不写入保留设置;地占后端流派档起盘前显示中文名。

### 安装器 / 发布链
- 安装器同版本号再比部件锁(`components-lock.json`)内容身份,相同才保留、不同走替换路径;发布脚本的部件复用基线在建 release 之前经认证 API 取上一版正式清单,新版以草稿建、顺序 runtime → 部件 → 安装包 → 清单最后再转正。Windows 安装器 / 发布脚本按同样语义对齐。

## v3.11.2 同步要点(Mac 已落地,Windows 按此对齐)

### 版本 lockstep
- 同 v3.11.0 的清单,版本 `3.11.2` / `runtimeVersion` = `3.11.2-runtime1`;`RuntimeWire.RUNTIME_VERSION` 同步(改后重建后端 jar)。

### 缩放上限 / 设置项 / 天象库日期 / 日志脱敏
- 缩放上限随窗口宽度封顶:上限 = 「窗口逻辑宽 ÷ 1000」取 0.1 档再夹进 [0.7, 1.8](1440 → 1.4、1728 → 1.7、3008 → 1.8、1180 → 1.1);超限的放大停在上限并调用页面钩子 `window.__HOROSA_SHELL_ZOOM_CAPPED(上限, 窗口宽)`(`layouts/app.js` 提示原因);窗口变窄后当前档超限即降到上限。**Windows 需要做什么**:Electron 端的缩放入口按同一公式封顶并调用同一钩子。
- AI 助手设置面移除无作用的「配色主题」项(`utils/aiTools/settingsFacets.js`)。
- 六爻「正月初一定年」联机:`utils/preciseCalcBridge.js` 联机结果缺 `yearGZByLunar` 时按本地历法补键(与离线回落同源)。
- 玄学史天象库:`astropy/astrostudy/xuanshi/data/public_data.sqlite` 重新生成(84 条年号 / 干支日期按年号年 + 农历月 + 干支日重推;`julian_date` 列整列置空,`modern_date` 即史料所载的儒略历日期),`astrostudy/xuanshi/celestial.py` 同步;前端 `components/xuanshi/xuanshiDate.js` / `XuanShiCelestial.js` / `XuanShiEvents.js` 的「排此日」提示行改历前一律标「儒略历 … 起盘」;测试 `tests/test_xuanshi_celestial_era_date_consistency.py`。**Windows 需要做什么**:数据库文件整体替换(逐字节相同),连同上述引擎与前端文件同步。
- 交易日志:`astrostudyboot/src/main/resources/conf/log/excludelogtrans.json` 整组排除 `/aianalysis/*` 各端点,`conf/properties/log.properties` 的脱敏参数表加入 apiKey / authorization / token 等密钥类参数;同步后重建 jar。

### Windows 独有补丁撤回 · 高纬度偕日升 / 没搜索限界(台账 PY-22)
- 现象:该补丁会丢「晨星初现 / 昏星初没」标签(`phasisEvent`)。按同一逻辑做覆盖边界的差分:真实偕日事件前后 ±7 天(含边界)× 16 个纬度 × 五星共 22834 例,不一致 687 例,全是「昏星初没」→ 空(以水星为主,中高纬度);1900–2100 随机 2400 例中 3 例。
- 原因:
  - `flag |= HELFLAG_SEARCH_1_PERIOD` 之后,偕日升在首个会合周期里搜不到会抛错;外层 try 包着「偕日升 → 偕日没」整个循环,于是整个函数中止,偕日没根本没查。原逻辑在这里是「搜到远处事件 → 丢弃 → 继续查偕日没」。
  - `_phasisWindowFeasible` 给 `swisseph.azalt` 传 2 元组,在 pyswisseph 2.10.03 上恒抛 TypeError(需要至少 3 个数),被 except 兜成「可行」,预筛从未生效。若修好这一层会误删真事件:Swiss Ephemeris 的模型里存在太阳在地平上 30° 以上的金星事件。
  - north-hi 金标「字节不变」只因为那张盘的偕日没本来就搜不到;8.4 s → 0.2 s 的提速几乎全部来自上面的错误中止。
- 严格等价的写法(每类事件先做首周期搜索,只有「偕日升首周期无事件、偕日没落在 ±7 天内」这一支补跑无界搜索)在同样的样本上零差异,但没有提速:慢的是偕日没搜索本身,带不带首周期标志都约 3.5 s。
- **Windows 需要做什么**:撤回该补丁(`windows-adaptations/patches/astropy__perchart.chartMemo.py.patch` 现只含这一段,可整份删除),`_phasis_event` 回到与 Mac 相同的写法;删掉 `HOROSA_PHASIS_BOUNDED` 开关与 `horosa_phasis_bounded_v1` / `_phasisWindowFeasible` 锚,同步 `MARKER_INVENTORY.json` / `HARNESS_MANIFEST.md`;台账 PY-22 改为「已撤回(改输出)」。north-hi 金标输出不变,整盘耗时回到约 8 秒(与 Mac 相同)。

### Windows 独有补丁作废 · 皇极经世典籍按需 / 玄学史长文本按需(台账 PY-6 / PY-7)
- 上游已实现这两项,接口与 Windows 版不同:
  - 皇极经世:`/wangji/pan` 只有请求带 `slimClassics: 1` 时才省正文,并在 `classics` 里标 `contentOmitted: true`;不带标记照旧全文。新只读端点 `/wangji/classic` 回与旧盘完全相同的 `classics` 对象(`meta` / `selectedKey` / `sections`)。前端 `HuangJiMain.js` 按典籍键缓存正文,逐节核对(典籍键 / 节数 / level / title)后合并,合并结果与旧盘逐字节相同;对不齐或取数失败回退一次不带标记的全文盘;起盘、无头快照、草稿预取三处接线,存档还原只合并、不重新起盘。开关 `horosa.perf.wangjiClassicsOnDemand`(前端)、`HOROSA_WANGJI_SECTIONS_CACHE`(后端典籍解析缓存)。
  - 玄学史:`celestial.microchronology` 新增可选 `limit`(缺省全量,星象大典年代下钻照旧),列表查询不取长文本列,下发行按 rowid 回贴正文(event_id 在该表不唯一,不要按 event_id 取正文),统计仍按全部命中行,结果按参数缓存(`HOROSA_XUANSHI_MICRO_MEMO`)。天象微年表页传 `limit: 300`,「仅显示前 300 条」提示按总数判断。开关 `horosa.perf.xuanshiMicroLimit`。
- **Windows 需要做什么**:`windows-adaptations/patches` 里 PY-6 / PY-7 相关补丁(webwangjisrv / webxuanshisrv / celestial / HuangJiMain / XuanShiMicro / services/xuanshi)中「典籍按需 / 长文本按需」的改动段作废,以上游为准;`microchronology_detail`(按 event_id 取正文)不再需要。同一补丁里的其它改动(如右栏子页冻结、面板就绪打点、步进预取)照旧保留,在新上游上重新生成补丁。台账 PY-6 / PY-7 改 upstreamed。

### 共享 Java(同步后重建后端 jar)
- 响应主体表保序:`boundless` 的 `TransData` 改用保持插入顺序的表,同一请求的顶层字段顺序固定为生成顺序(此前随工作线程的表容量历史变化,内容相同而字节不同)。开关 `HOROSA_JAVA_ORDERED_RESPONSE=0` / `-Dhorosa.response.ordered=false` 回旧。
- 组件扫描出的控制器与服务补上延迟初始化,并在就绪后后台预创建(`LazyInitXmlScanPostProcessor`,开关 `HOROSA_JAVA_XML_SCAN_LAZY` / `HOROSA_JAVA_LAZY_PREWARM`);通配组件扫描挪到条件装配(`HOROSA_JAVA_LEGACY_BROAD_SCAN`);`AIAnalysisMaterialService` 显式启动时创建(其静态块设置进程级表格解析阈值)。
- 跨源请求头白名单含 `X-Horosa-Crypto` / `X-Horosa-Priority`;响应加解密 v2(请求头能力协商,会话钥 AES-GCM;旧客户端照旧 RSA 信封;`-Dwebencrypt.v2=false` 回旧)。
- 八字时间算法口径(`astrostudycn`:`TimeZiAlg.calcBasis`、`BaZi.setup`,`/bazi/birth` `/bazi/direct` `/liureng/gods` `/jieqi/year` 缓存键):「春分定卯时」一律按「直接时间」算(此前按平移后的时刻判换日,多数时辰出生日柱前错一天);「直接时间」偏移清零,年柱 / 月柱 / 交节距离都按所填钟表时刻(此前沿用计算服务的卯时偏移,交节后约 1–3 小时内起盘报节气窗不够)。真太阳时 / 平太阳时结果不变。测试 `BaZiTimeAlgBasisTest`(需计算服务在线)。
- 八字年柱按立春本身判定(`astrostudy`:`BaZiHelper.getYearColumn` / `findLichun`;`astrostudycn`:`BaZi`):一、二月出生与节气窗里的立春(`ord == 0` 的节)比较,不再按固定下标(节气窗在生辰前补项后,二月立春前出生会被判成下一年);儒略历年份立春落在一月下旬时一月立春后出生算当年;不再「换算跨立春另进一年」。真太阳时 / 平太阳时换算后跨回交节前、落出按钟表时刻取的节气窗时,按换算后时刻重取窗口(`locateBirthJie`),不再报「节气窗不够」。节气年表缓存代次 `jieqi_year_bazi_v6`。测试 `BaZiLichunWindowTest`(需计算服务在线)。
- 经纬度串解析(`boundless`:`PositionUtility.convertLonStrToDegree / convertLatStrToDegree` → `parseDegreeMinute`):「度 + 方位字母 + 分」按度 + 分 / 60(此前误作度 + 1 / 分,118e27 → 118.037°,Java 真太阳时 / 平太阳时偏移最多差约 4 分钟;一位数分钟另被乘 10)。日柱(`astrostudycn`:`BaZi`)按换算后的出生时刻取,不再另减一天(偏移 ≥ 约 2 小时的地点子时出生此前日柱前错一天)。节气年表缓存代次 `jieqi_year_bazi_v7`。测试 `PositionUtilityDegreeMinuteTest`、`RealSunTimeOffsetTest`、`BaZiSolarDayPillarTest`。boundless 改动后需重装全部依赖它的模块再重建 jar。
- 八字南半球月令(`astrostudycn`:`BaZi.southMonthFlip` 缺省 false、`setSouthMonthFlip`;`/bazi/birth`、`/bazi/direct` 读请求参数 `southMonth`(chong / none,进缓存键);`JieQiController` 两处显式 `setSouthMonthFlip(true)`)。此前南纬一律对冲。测试 `BaZiSouthMonthTest`。
- 八字大运岁 / 小运年份跨公元纪元(`astrostudycn`:`BaZi.historicalYearDiff` / `addHistoricalYears`;`BaZiDirect`、`OnlyFourColumns` 起运岁,`BaZiDirect` 小运年份):公元前出生、起运落在公元后的盘,此前起运岁多一岁、小运年份出现不存在的 0 年;公元年份逐字节不变。测试 `BaZiEraBoundaryTest`。
- 时刻串秒进位(`boundless`:`DateTimeUtility.getTimePartsFromJdnTime` / `getDateFromJdn`):秒四舍五入到 60 时逐级进位(秒 → 分 → 时 → 日,进到 24:00:00 时日期同步进一天);此前约 1% 的换算时刻显示为 `xx:xx:60`,整点时按字符串取小时判时辰会判早一个。只有原本出 `:60` 的输出变化,起运用的节前 / 节后秒数不变。
- 八字类附带的农历随时间算法(`astrostudycn`:`BaZi.alignNongliWithTimeAlg`):选直接时间 / 平太阳时时,农历日期、节后天数、人元司令、农历日时干支按所选算法的时刻取;真太阳时档不变;`nongli.birth` / `solarTime` 仍给真太阳时。
- 农历按北京时间编算的农历表查(`astrostudy`:`NongliHelper`):整年朔日表固定取东八区那份,按出生地日期查;月末换月在东八区以外只比日历日期;东八区以外的「朔」时刻加注「(北京时间)」。东八区输出不变。
- 缓存代次:节气 / 农历请求的 `_v` 由 w4 升 w5(`AstroHelper` / `BaZiHelper`),农历年表缓存键尾 ` w5`(`AstroCacheHelper`),`/jieqi/year` 年缓存 `jieqi_year_bazi_v8`;`/bazi/birth` `/bazi/direct` `/liureng/gods` `/liureng/runyear` `/chart13` `/chart12` 的结果缓存键加 `_calRev`(`NongliHelper.CALENDAR_CACHE_REV`,只进缓存键,不发给排盘引擎)。
- 农历置闰随 Python 修正再升一格缓存代次:农历月表请求 `_v` w6(`AstroHelper.getNongliMonth`;节气请求仍 w5),农历年表缓存键尾 ` w6`(`AstroCacheHelper`),`jieqi_year_bazi_v9`,`CALENDAR_CACHE_REV` = `cal3`。
- **Windows 需要做什么**:同步 Java 源码后重建 jar。Windows 自有的 Java 补丁(日志行尾调用点按需 / 磁盘缓存 JSON 归一 / 缓存目录与 comm 缓存先读 -D / 农历按日持久化开关)以上游为准,台账 JV-3 / 5 / 6 / 8 / 9 / 10 改 upstreamed;启动期八字 / 农历预热与上游 `StartupLedgerListener` 的「此刻」样本二选一,不要重复预热。

### 共享 Python
- 星历路径短路、纯 JSON 快径(`websrv/fastjson.py`,允许名单含 flatlib 对象)、相位请求级缓存(`HOROSA_EPHE_PATH_FASTPATH` / `HOROSA_FAST_JSON_ENCODE` / `HOROSA_ASPECT_MEMO`);奇门热路径、kin 系常量、显示层繁简替换单遍、印占瑜伽输出有序;请求优先级车道(预取请求带 `X-Horosa-Priority: prefetch`,`HOROSA_PRIORITY_LANE`)。
- 玄学史天象库载入时逐行解析年号:候选年号按首字分桶(桶内保持原表序),命中集与「等长先到先得」不变,结果与全表逐个比对逐值相同;天象库冷载入约 318 → 225 ms。开关 `HOROSA_XUANSHI_ERA_INDEX=0` 回全表比对。
- 生辰节气(`/jieqi/birth`,每张新盘都会调)的节气求解与卯时基准盘不再每步建整张默认盘:与节气年表 / 农历同一开关 `HOROSA_JIEQI_FAST_APPROACH`,节气求解直取太阳位置、基准盘用太阳瘦盘;单次约 6.1 → 0.5 ms,输出逐字节相同。
- 响应 JSON 快径扩到全部服务:`webchartsrv` 载入时把真 `jsonpickle.encode` 换成同判据、同回退的快径版(`websrv/fastjson.install_global`;子开关 `HOROSA_FAST_JSON_GLOBAL=0` 只留主排盘 / 推运两处)。印度盘约 30 → 19 ms、占星地图约 147 → 67 ms,输出逐字节相同。快径 shim 的 `unpicklable` 缺省改为与 jsonpickle 一致(True)。
- 蠢子数诗词库按进程只建一次(`HOROSA_CHUNZI_DB_MEMO`),`/chunzi/pan` 约 19 → 7 ms。
- 玄学史人物关系图节点顺序固定为「共现权重降序、同权按人名」(原随进程哈希种子变,每次启动输出与布局不同)。
- 生辰节气卯时上升求解的牛顿迭代加上限(`_ASC_APPROACH_MAX_ITER` = 5 万步,最坏约 1.4 s):「按黄经」(`byLon=1`)在 |纬度| ≳ 50° 可永不收敛,此前请求不返回、线程空转;超限退到按赤经并在结果里加 `maoFallback: "byRA"`(按赤经也不收敛时不做卯时校正,`"none"`)。收敛的输入结果不变。
- 铁板神数诗词库 / 足本条文库按进程只载一次,分类检索改查载入时建好的索引(`HOROSA_TIEBAN_DB_MEMO`;vendor `kinastro/astro/tieban/tieban_calculator.py`),`/tieban/pan` 约 15.5 → 3.7 ms,输出不变。
- 星历表等端点请求内黄经 memo(`astroextra.swe_lon`,键 = 天体 / 时刻 / 中心 / 站心坐标;`webchartsrv` 请求工具按服务前缀开启、请求结束清空;`HOROSA_SWE_LON_MEMO`),星历表约 29.6 → 22.6 ms,输出不变。
- 主排盘两处等价提速:恒星批 LRU 存入 / 命中由整批 deepcopy 改快克隆(`flatlib/ephem/ephem._cloneStarList`,`HOROSA_STAR_LRU_FASTCLONE`);JSON 快径预扫改迭代实现(`fastjson._fast_shape_ok_iter`,`HOROSA_FAST_JSON_ITER_SCAN`)。主排盘约 15.7 → 15.0 ms,输出不变。
- 交节时刻按节气黄经精确求解(`astrostudy/jieqi/BirthJieQi.py` / `YearJieQi.py`:此前求解目标多加 1/7200 度,交节系统性晚约 12 秒);节气时刻的显示串经 `jieqiconst.cnTimeRounded` 四舍五入到秒(此前截秒)。
- 农历置闰按日期定冬至所在月(`astrostudy/jieqi/NongLi.py` `setupMonth`:朔日的日期不晚于冬至的日期即为十一月,与判中气同一口径;此前按时刻取朔再「非 12 月起就后挪一个月」,冬至落在所在月最后一两天时错挪,2033 年误成闰七月、1642 / 2128 年误成闰九月、1813 / 2185 年多出闰八月)。测试 `tests/test_nongli_leap_month.py`。
- **Windows 需要做什么**:同步 Python 文件;Windows 原创的同名开关项(PY-1 / 2 / 3 / 4 / 5 / 9 / 18 / 19 / 20 / 21)台账改 upstreamed,回流时以 Mac 版为准。玄学史门后预热(PY-13)与择日扫描预装挪到门后(PY-23)上游不收(Mac 上冷装载只有几毫秒到几百毫秒,预热还要常驻约百兆事件缓存),Windows 按自身冷导入耗时自行保留。

### 共享前端
- 八字本地引擎按出生绝对时刻换月(`utils/baziLunarLocal.js`:`absoluteTimeLunar` / `shiftSolarMinutes`,非东八区年 / 月 / 交节取自折成北京时间的农历,日 / 时仍按当地钟表;东八区逐字节不变)与「南半球月令」(`flipMonthPillar` / `isSouthLatitude`,核心缓存键含 `southMonth`;八字左栏新下拉、`BaZi.js` 进请求参数与改后重排、AI 挂载盘法组与 `buildChartBaziParams` 转发、南纬快照标注、帮助文档一卡)。AI 挂载 / 快照「春分定卯时」文案注明同直接时间。测试 `baziAbsoluteTimeJie`、`baziSouthMonth`。
- 八字岁数 / 年份口径(`components/cntradition/baziAgeText.js` 岁数显示单源;`BaZi.js` `alignJavaBaziAges` 在 `/bazi/birth`、`/bazi/direct` 回退结果入口对齐为虚岁;旧版界面 `BaZiLegacyView` / `MainDirection` / `MainDirectionSimple` / `MDSDirect` / `MDSYear` / `SmallDirection` 随「年龄」档,「上运时间」取首步大运岁数;AI 快照「流年行运概略」起始年龄随档;`utils/dateStrSafe.js` `addDisplayYears` / `displayYearDiff`,行运面板 / 细盘 / 旧版 / 快照年份跨公元纪元不出 0 年)。测试 `baziAgeYearConvention`。
- 一次改动只重算一次(`utils/singleTrigger.js`,13 处接线,`horosa.perf.singleTrigger`);玄学史「故事专题」首次打开卡在「载入…」、神数正传切换流派后条文不再载入两处修复;AI 分析挂载「小限粒度 / 小限起点」对命盘生效;黄历九星值日与时辰宜忌改为用到时才计算(`horosa.perf.huangliLazyDetail`);预载 / 预热按本机使用频次排序(`horosa.perf.usageOrderedPreload`);温启直接显示上次的盘(`horosa.perf.bootChartRestore`,恢复在 `checkUser` 里二选一);稳定 React key。
- 共用工具 `utils/beijingTimeShift.js`(`parseZoneHours` / `bjShiftMinutes` / `shiftSolarMinutes`,从 `baziLunarLocal.js` 原样抽出,八字引擎改为引用)。
- 本地节气种子按时区折成当地钟表(`utils/localNongliAdapter.js` `buildLocalJieqiYearSeed(year, zone)`:交节时刻与交节日干支按当地钟表 / 日期),奇门当前节气、节气页离线回退、奇门择日扫描、AI 挂载共用;东八区与缺时区不变。
- 河洛出生节气单源 `utils/heluoLocal.js` `heluoSolarTermOfDate(dateStr, zone, quHuaGong)`:页面 `HeLuoMain.solarTerm` 与挂载 `aiAnalysisContext.heluoSolarTermForDate` 同调;非东八区按节气的当地日期比(东八区原路径不变)。`DunJiaCalc` 新增仅供单测的 `__testing__` 导出。
- 帮助文档:八字「算法与口径」、紫微「时间 / 地点」、黄历「农历」补阴历口径与两条算法路径的差异说明。
- 六爻间爻按世应位置取(`components/gua/LiuYaoConst.js` `jianYaoPositions` / `jianYaoSpanText` / `JIANYAO_ROLE` / `JIANYAO_DONG_NOTE`;`liuyaoFacade.js` 逐爻带旺衰、动静、空破与对世对应的冲合生克;`LiuYaoBoard.js` 概览卡片、`liuyaoSnapshotEx.js` AI 快照同一串标签;`GuazhanHelpDoc.js` 四处):间爻 = 世应中间两爻(世应在初四取二三、二五取三四、三上取四五),此前固定取三、四爻,64 卦中 48 卦把世爻或应爻本身算进间爻。测试 `components/guazhan/__tests__/liuyaoJianYao.test.js`。
- **Windows 需要做什么**:同步前端文件;Windows 的温启恢复补丁(`src__models__app.bootChartRestore`)作废,以上游 `models/app.js` / `models/astro.js` 为准。

### Electron 壳侧
- 前端启动分段计时经桌面桥命令 `web_ledger_mark_command` 上报:Electron 可提供同名 IPC,或依赖 `invokeDesktopCommand` 在壳无此命令时的空操作(已内建)。
- 后端就绪确认:壳在后端就绪时派发 `horosa:backend-confirmed` 并置 `window.__horosaBackendConfirmed`,前端就绪门立即放行。
- 更新后首次启动提前进界面:前端 `bootContext()` 读 URL 参数 `early` / `firstLaunch` / `boot`;Electron 在加载地址上带同名参数即可复用「已用时 / 更新已完成」的启动页文案。
- 启动器 JVM 旗标(可选对齐):`-XX:-UsePerfData`、`-Dlog4j2.disableJmx=true`、`-Dspring.mvc.servlet.load-on-startup=1`、`-Dorg.springframework.boot.logging.LoggingSystem=none`、`-XX:+DisableExplicitGC`、`-Dcachehelper.needcache=false`。

### 更新后缓存版本闸 / 温启与请求 / 会话钥清理
- 壳(`main.rs`):运行时版本号(manifest.version)在**第一次导航之前**记下,早导航 URL 与收尾 ready 都带 `rv=`;init 脚本 `__horosaReady` 的同参判定键加 `rv`(不一致整页重载)。此前壳在第一次导航时不带 `rv`,前端结果缓存信封恒为 `net-v1`,更新后 24 h 内同参数的盘可能回放旧版本结果。「重启后端 / 修复运行时」单飞:启动 / 修复 / 更新引导进行中拒绝并发第二条(`trigger_runtime_repair_command` 返回错误,菜单项静默);启动账本整行一次写入,页面上报的附加字段序列化超过 4 KB 只记长度。**Windows 需要做什么**:Electron 壳在第一次加载前就带上 `rv`,收尾 ready 比对 `rv`;修复入口单飞。
- 前端:`utils/chartFetch.js` 直连排盘服务先过就绪门(温启恢复到卜类 / 玄学史等页时首批请求不再打到未起的端口);`utils/request.js` 预取优先级头在去重分流之前打上(此前可去重端点永不带头);`models/astro.js` 温启恢复按最终生效的 fields 重算请求参数、有变按新参数重取;`models/app.js` 恢复的子页签经 `constants/SubTabRegistry.restoredSubTab` 校验,恢复兜底计时从后端可达起算;`utils/backendBootGate.js` 更新后首启兜底放行 900 s(= 启动脚本就绪总上限);`utils/rsahelper.js` v2 解密失败统一 `code: 'crypto.v2'`,请求层提示「解密失败、已切兼容模式」,不再当端口占用去再协商。
- Java:`RequestHeaderInterceptor` 改为 `AsyncHandlerInterceptor`,会话钥在 `afterCompletion` 写完响应体后与 `afterConcurrentHandlingStarted` 时清除(测试 `ResponseCryptoTest`);`ChartController` 的 `/chart` 结果缓存键加 `_calRev`;`log.properties` 脱敏表加 `Token` / `AccessToken`;`StartupLedgerListener` 延迟 bean 预热失败记入启动账本与标准错误。同步后重建 jar。
- Python:`flatlib/ephem/swe.py` 外部重设星历路径时作废 JPL 文件追踪(JPL 模式下随后重设 JPL 文件);`websrv/fastjson.py` 非有限浮点字典键回退真 jsonpickle;`astrostudy/perchart.py` 古典临界区异常回滚覆盖 `BaseException`(相位缓存作用域必关)。

## v3.11.3 同步要点(Mac 已落地,Windows 按此对齐)

### 版本 lockstep
- 同 v3.11.0 的清单,版本 `3.11.3` / `runtimeVersion` = `3.11.3-runtime1`;`RuntimeWire.RUNTIME_VERSION` 同步(改后重建后端 jar)。

### 共享 Java(同步后重建后端 jar)
- `boundless/spring/help/TransLogRules.java`(新):交易日志排除表 / 白名单载入统一小写、查询不分大小写(`TransLogMongoHelper.shouldSkipTransLog`;路径匹配不区分大小写时不同写法曾绕过排除表);`TransData` 删参改为不分大小写(`removeParamsIgnoreCase`)。单测 `TransLogRulesTest`。
- `astrostudy/helper/ParamHashPersistPolicy.java`(新):冷路径结果「往返成纯 Map」的回退开关,`-Dparamhash.persistable=false` 回旧口;`ParamHashCacheHelper` 经它调用。单测 `ParamHashPersistPolicyTest`。

### 共享前端
- `utils/backendBootGate.js`:读完启动上下文即 `history.replaceState` 摘掉 `firstLaunch` / `boot`(Electron 壳若也经 URL 送这两个参数,行为同 Mac:手动刷新不再重演「更新已完成」文案与首启兜底;`early` 与服务根参数保留)。jest `backendBootGate.test.js`。
- `pages/index.js`:出盘后切换页签也重落温启快照(页签 = 上次停留而不是上次出盘)。jest `bootChartRestore.test.js`。

### Python 引擎
- `astrostudy/xuanshi/db.py`:只读打开加 `immutable=1`;打包不再携带 `editorial.sqlite-shm / -wal / -journal`(Windows 打包同样剥离;两处必须一起改 —— 不带 immutable 的 WAL 库在不可写目录连只读都打不开)。pytest `tests/test_xuanshi_db_immutable_readonly.py`。
- 排盘服务分级门(`websrv/webchartsrv.py`):核心段装完即开核心门,不经卜类挂载点的请求在核心门后最多再等 `HOROSA_PY_CORE_GATE_GRACE_MS`(缺省 1500 ms)就放行,卜类挂载点仍等全门;`HOROSA_PY_TIERED_GATE=0` 回单门。随共享 Python 自动到位,Windows 冷启同样受益;同步后跑一次 `tests/test_startup_gate_tiers.py`。

### macOS 独有(Windows 无对应动作)
- 安装 / 更新后原生库首次加载预检(`config/native_prewarm_priority.json`、`installer-scripts/postinstall.template`、壳子命令 `--horosa-native-prewarm`)、增量更新暂存槽硬链接搭 + 换完即预检(Windows 的差分更新按文件树下载、不走整棵克隆)、签名缓存自动种子与稳定部件对拍(`prepare_sign_seed.py` / `verify_stable_parts_headers.py`)。
