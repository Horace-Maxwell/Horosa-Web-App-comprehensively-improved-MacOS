# 星阙 Windows 复刻与发布自检指南

最后更新：2026-05-24

这份文档用于把当前 macOS 版星阙完整复刻到 Windows。重点不是照搬 macOS 的脚本，而是记录这几轮已经暴露过的错误、易漏点和必须进入 Windows 工作流的自检门槛。

Windows 版的目标很简单：用户安装后，所有命法、卜法、管理命盘、管理事盘、AI 导出、窗口与设置持久化都能稳定使用；关闭、重开、升级版本后不丢数据；发布包下载回来以后仍然能逐项通过机器检查。

## 总原则

- 以“安装后的 Windows App”为准，不以开发服务器为准。
- 不要只验证首页能打开，要验证每一个技法端点、每一个管理数据往返、每一个 AI 导出设置分组。
- 不要把 macOS 路径、命令、权限模型硬搬到 Windows。路径、服务启动、安装目录、签名、更新替换都要按 Windows 重新实现。
- 任何新增技法、tab、AI 导出分段、管理字段，都必须同时更新：前端入口、后端/本机服务、结构化快照、AI 导出设置、持久化导入导出、自检脚本。
- 发布前本地安装包要过一遍；发布后从 GitHub 或正式渠道把安装包下载回来，还要再过一遍。

## 推荐 Windows 目录模型

不要把可写数据放进 `Program Files`。Windows 版建议分三层：

- App 安装目录：只放只读程序文件，例如 `C:\Program Files\Horosa\星阙` 或安装器选择的目录。
- 机器级共享 runtime：放离线包随附的 Python、Java、Horosa-Web runtime，例如 `%ProgramData%\Horosa\runtime\current`。
- 用户级数据与缓存：放用户设置、窗口状态、下载缓存、日志、WebView 数据，例如 `%APPDATA%\Horosa` 或 `%LOCALAPPDATA%\Horosa`。

关键点：

- App identifier / WebView profile 必须稳定。否则 WebView2 的 localStorage、IndexedDB、AI 设置、命盘/事盘本地库会在升级后像“换了一个 app”一样丢失。
- 离线安装包可以写 `%ProgramData%`，普通 app 运行时优先读共享 runtime，必要时回退到用户级 runtime。
- 所有路径都要支持中文 app 名、空格、非 ASCII 用户名、OneDrive 用户目录、长路径。PowerShell 和 Rust/Node/Python 都必须全程 quote 路径。

## Windows runtime 必须带上的东西

macOS 版这次最大的问题之一，是“开发环境能用，安装包里缺了东西”。Windows 打包时必须显式列清单，不要靠隐式目录存在。

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
- 所有 vendor/kinastro 数据目录、解释文本、星历相关数据
- Swiss Ephemeris / flatlib 所需资源，尤其 `flatlib/resources/swefiles`

Windows 版不要继续使用 `runtime/mac/...` 这种目录命名。建议使用：

```text
runtime/windows/python/python.exe
runtime/windows/java/bin/java.exe
runtime/windows/bundle/astrostudyboot.jar
Horosa-Web/start_horosa_local.ps1
Horosa-Web/stop_horosa_local.ps1
```

## 启动服务时最容易漏的点

Windows 启动脚本需要完成 macOS `start_horosa_local.sh` 的等价职责：

- 选择空闲端口：一个给 Python chart/kentang 服务，一个给 Java backend。
- 设置 `PYTHONNOUSERSITE=1`，避免用户系统 Python 污染嵌入 Python。
- 设置 `PYTHONPATH`，必须同时包含：

```text
<runtime>\Horosa-Web\flatlib-ctrad2
<runtime>\Horosa-Web\astropy
```

- 启动 Python chart/kentang 服务。
- 启动 Java backend。
- 等待 `/chart` 和 signed backend `/common/time` 可访问。
- 写 pid 或 process handle，关闭时可靠清理。
- 输出日志到用户可访问目录，不要只写安装目录。

曾经踩过的坑：

- `PYTHONPATH` 只包含 `astropy`，安装包里命法会找不到 `flatlib` 或行为不稳定。
- 前端只拿到 `srv`，新加入的 kentang/kin 技法没有拿到 chart 服务端口，导致安装包内所有新功能都打到错误端口。
- `qizhengkin` / kinastro 使用 `pyswisseph` 后可能改掉全局 Swiss Ephemeris path，导致后面的 `/chart` 报错。自检必须先跑 kentang/kin 技法，再跑普通 `/chart` 和完整 backend smoke，才能抓到这种共享进程污染。

## 前端服务地址规则

Windows app 打开前端时，URL 必须带这些 query：

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
- `chartSrv` 给 `/chart` 和占星计算相关服务。
- `kentangSrv` 给太乙、金口诀、奇门、五兆、太玄、镜诀、神易数、kinastro 等所有 kentang/kin 路由。
- 前端 `KENTANG_SERVICE_CONFIG` 每加一个模块，都有 path、queryKeys、默认本地端口、测试覆盖。

## 当前必须 smoke 的 kentang/kin 路由

Windows 版必须移植并运行 macOS 版的 `verify_kentang_runtime_endpoints.py` 思路。当前至少覆盖以下 17 个 `/pan` 端点：

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
- 这些端点跑完后，再跑 `/chart` 和完整 backend smoke。

新增任何 kentang/kin 技法时，第一件事就是把它加入这个清单。没有进清单，就不允许发布。

## 管理命盘 / 管理事盘不能丢字段

Windows 版必须完整保留 localStorage 管理逻辑，并验证关闭重开、升级版本后数据还在。

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
- qizhengkin、shaozi、tieban、fendjing、beiji、nanji、chunzi、xianqin、cetian 等 kinastro 技法不能回退到普通 guolao 或 generic。
- 金口诀不能回退到六壬；太阳弧不能导成主限法；当前激活页面是什么，导出就必须是什么。
- 旧 AI 导出设置版本升级后，新增分段不能被旧设置过滤掉。

建议 Windows 必跑：

```bash
cd Horosa-Web/astrostudyui
npm test -- --runInBand src/utils/__tests__/aiExport.test.js src/utils/__tests__/aiAnalysisContext.test.js src/utils/__tests__/aiAnalysisSelection.test.js
```

还要跑 app 侧 AI 分析自检：

```bash
python3 scripts/browser_horosa_aianalysis_check.py
```

当前 macOS 版的期望规模是：

- chart techniques: `28`
- case techniques: `8`

如果 Windows 版数量不同，必须写明是产品范围变化；否则视为遗漏。

## 窗口大小和用户设置持久化

这次已经补过窗口大小持久化，Windows 版要保留同样能力。

Windows 实现要点：

- 保存 main、preferences、diagnostics 三类窗口状态。
- 保存逻辑坐标，不直接保存物理像素，否则高 DPI 屏幕会出错。
- 记录 `stateVersion` 和 `coordinateSpace`，给以后迁移用。
- 恢复窗口时要检查当前显示器尺寸，避免窗口跑到屏幕外。
- 最大化状态要单独保存。
- 关闭窗口、app 退出、更新前都要 persist 一次。

持久化文件建议放在 app config dir，不要放在安装目录。Windows 上通常会落到 `%APPDATA%` 或 `%LOCALAPPDATA%` 的 app config 路径。

## Windows 图标不能是假圆角

macOS 版曾经出现过“看上去圆角，但实际上是正方形背景加圆角边框”的问题。Windows 版必须检查 `.ico` 里的 alpha。

要求：

- 源图必须是透明背景 PNG。
- 1024 或最大源图四角 alpha 必须接近 0。
- `.ico` 内至少包含 256x256 PNG layer，并保留 alpha。
- 不要把图标烘焙成白底或黑底正方形。
- 安装包、开始菜单、任务栏、卸载器图标都要用同一套透明资产。

建议把 macOS `verify_icon_alpha.py` 改成 Windows 版：

- 输入源 PNG 和生成的 `.ico`。
- 解析 PNG layer 或用 Pillow 读取 `.ico` 最大帧。
- 断言四角 alpha <= 8，中心 alpha >= 240。

## Windows 安装包/更新包要包含的新东西

Windows 不能只打前端 app。必须同时准备：

- 桌面 app 本体，例如 Tauri 生成的 `.exe`、MSI 或 NSIS installer。
- 离线 runtime 包，例如 `horosa-runtime-windows-x64.zip`。
- 离线安装包，把 runtime 包嵌入 installer，而不是首次启动再下载。
- `horosa-latest.json`，包含 Windows platform entry。
- SHA256 校验值。
- Windows 代码签名和 timestamp。
- 第三方 license / notices。

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
      "runtimeVersion": "2.1.0-runtime1"
    }
  }
}
```

如果未来要支持 arm64 Windows，再单独加 `windows-aarch64`，不要混用 x64 runtime。

## Windows 不能照搬的 macOS 细节

这些要全部替换：

- `/Applications/*.app` -> Windows install dir。
- `/Users/Shared/Horosa` -> `%ProgramData%\Horosa` 或用户级 fallback。
- `bash` -> PowerShell 或 Rust 原生启动逻辑。
- `open` -> `Start-Process` 或 Rust `open` crate/Windows API。
- `lsof` -> PowerShell `Get-NetTCPConnection` 或 Rust 端口探测。
- `ditto`、`pkgutil`、`plutil` -> Windows 安装器/zip/MSI 检查工具。
- `codesign`、`spctl`、`xcrun notarytool` -> Windows Authenticode 签名、timestamp、SmartScreen 友好签名流程。
- `sips`、`.icns` -> `.ico` 生成与 alpha 检查。
- `tar --disable-copyfile`、`.DS_Store`、xattr 清理 -> Windows zip/7z/PowerShell 压缩，另行过滤 `.git`、`__pycache__`、测试缓存、临时文件。

## Windows 特别容易出问题的地方

- WebView2 数据目录变化导致 localStorage 全丢。
- 安装器覆盖 app 时，旧 exe 仍在运行，Windows 文件锁导致替换失败。
- 嵌入 Python 找到用户机器的 site-packages，结果开发者电脑正常、用户电脑崩。
- `pyswisseph` wheel / DLL 缺失，或者 Swiss Ephemeris 数据路径被其他模块改掉。
- Java backend 需要的 jar 没进 runtime，开发环境用 target 文件，安装包里没有。
- 杀毒软件拦截未签名 exe、脚本或嵌入 runtime。
- PowerShell 默认编码或 cmd 输出导致中文路径/中文日志乱码。
- 防火墙弹窗阻断本地服务。原则上只监听 `127.0.0.1`，不要监听 `0.0.0.0`。
- 端口固定导致冲突。Windows 版也要随机挑空闲端口，并把端口注入 URL。
- `tzdata` 缺失。Windows 上 Python `zoneinfo` 很容易因为没有系统 IANA 数据而失败，必须随 Python 环境带 `tzdata` 或做兼容。
- 路径长度超过 260。打包和运行都要启用长路径友好的实现，至少不要手写短路径假设。

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
& "$RuntimeRoot\runtime\windows\python\python.exe" -c "import cherrypy,jsonpickle,swisseph; import websrv.webchartsrv; import websrv.webqizhengkinsrv; print('ok')"
```

4. 启动安装后的 runtime，不是开发 checkout。

5. 先跑 kentang/kin 17 个端点。

6. 再跑 `/chart`。

7. 再跑 signed backend `/common/time`。

8. 再跑完整 backend runtime smoke：

```bash
HOROSA_SERVER_ROOT=http://127.0.0.1:<backendPort> node Horosa-Web/astrostudyui/scripts/verifyHorosaRuntimeFull.js
```

9. 跑 AIAnalysis app 侧自检。

10. 跑管理命盘/管理事盘真实关闭重开测试。

11. 检查 icon alpha。

12. 检查安装包签名、SHA256、manifest Windows platform 字段。

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
- 跑 `/chart`。
- 跑 Java backend smoke。
- 跑 AIAnalysis 自检。
- 关闭再打开，确认窗口大小与用户设置恢复。
- 新增命盘/事盘、导出 JSON、删除、导入、再打开，确认不丢。

发布总结里必须写明这些检查是否通过。只要有一项没跑，不能写“全面完成”。

## 给 Windows 开发的最小验收矩阵

| 类别 | 必须证明 |
|---|---|
| 服务启动 | Python chart/kentang 和 Java backend 从安装后的 runtime 启动 |
| 服务注入 | 前端 URL 同时带 `srv`、`chartSrv`、`kentangSrv` |
| 新技法 | 17 个 kentang/kin `/pan` 端点全部返回结构化 `Result` |
| 传统命盘 | `/chart` 和完整 backend smoke 通过 |
| 管理命盘 | 所有 chart family 可新增、编辑、搜索、导出、导入、删除、关闭重开不丢 |
| 管理事盘 | 所有 case type 可新增、编辑、搜索、导出、导入、删除、关闭重开不丢 |
| AI 导出 | 每个技法有结构化 snapshot key 和可选分段，不串台、不空白 |
| AI 分析 | 当前 chart/case technique 数量符合预期，单选技法只挂载单选上下文 |
| 用户设置 | AI 导出设置、主题/偏好、窗口大小关闭重开后恢复 |
| 图标 | `.ico` 真透明圆角，四角 alpha 为透明 |
| 升级 | 旧版本数据、设置、runtime 缓存不被覆盖或误删 |
| 发布包 | 正式下载回来的包通过同一套检查 |

## 新增技法时的提交检查清单

每加一个命法或卜法，都必须逐项回答：

- 前端 tab/入口有吗？
- 本机服务 endpoint 有吗？
- Windows runtime payload 会把相关 Python/vendor/data 文件带进去吗？
- `PYTHONPATH` 能找到它吗？
- 如果使用 `pyswisseph`，是否会污染全局 ephemeris path？
- 管理命盘或管理事盘能保存它吗？
- 导入旧备份能识别它吗？
- `payload` 里隐藏字段会不会在编辑时丢失？
- AI 导出有结构化 snapshot key 吗？
- AI 导出设置有合适的分段吗？
- 旧 AI 导出设置迁移后会包含新增分段吗？
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

