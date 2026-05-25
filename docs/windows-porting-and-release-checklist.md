# 星阙 Windows 复刻与发布自检指南

最后更新：2026-05-24

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

Windows 复刻时要把这条经验直接放进 harness：

- 每次新增或升级 JNI / DLL / `.pyd` / native JAR，都要列出 `x64`、`arm64`、Windows 版本、VC runtime 依赖和失败路径。
- 不要在静态初始化块里把可选 native load 失败重新抛出。错误架构、缺 DLL、缺依赖时通常是 `UnsatisfiedLinkError` / `Error` 或平台异常，不是普通 `Exception`；可选能力要 `catch(Throwable)` 后设置 availability flag，再由调用方降级。
- 如果某条 native 路径不是核心功能，例如 PNG 调色板压缩、OpenCV 文本检测、IoT 串口，要明确 fallback：写原图、跳过分析、提示该平台不可用，而不是让 app 崩。
- 如果某个 native 依赖当前是死代码，也要把“调用方追踪为零”的证据写进文档。未来一旦接入业务，必须重新评估，而不能沿用旧结论。
- Windows 打包前要跑一遍 native 清单检查，等价于 macOS 的 `find ... '*.jnilib' '*.dylib' '*.so' + lipo -archs`。Windows 可用 `dumpbin /headers`、`sigcheck`、PowerShell 读取 PE machine type，至少确认目标架构和缺失 DLL。
- 构建 / 安装自检不能只跑 `java -version` 或 Python import。发布 gate 必须真正启动安装后的 runtime，打 `/common/time`、chart health、kentang/kin 端点和多时间 `/chart`，这样才能抓到“启动后才加载”的 native 问题。

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

这次还暴露了一个 harness 自身易错点：发布验收脚本里 `python3` 不一定是有 Playwright 的 Python。Windows 版不要假设全局 `python` 正确，应支持：

- `HOROSA_PLAYWRIGHT_PYTHON` 或等价环境变量显式指定。
- 自动探测项目虚拟环境、工具链 Python、系统 Python，只有能 `import playwright` 的候选才可用于 UI harness。
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

4. 启动安装后的 runtime，不是开发 checkout。
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
