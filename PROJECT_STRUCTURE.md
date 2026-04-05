# Horosa 项目结构（按当前仓库实际情况细化整理）

更新时间：2026-04-01

## 0. 说明与边界

本文档基于当前仓库实际目录扫描结果整理，不按旧版上传说明推测。

本次整理的边界如下：

- 纳入当前根目录下真实存在、且和 Horosa 主工程/桌面交付/验证/文档有关的目录与文件。
- 明确忽略 `Horosa_Native_macOS/` 与 `Horosa-Windows-Docs/` 两个目录，不把它们写入结构主线。
- 对构建产物、日志、缓存、runtime 目录会说明用途与已存在的关键内容，但不展开所有二进制文件细节。

## 1. 根目录全貌

### 1.1 当前根目录实际可见内容

根目录当前可见的主要条目包括：

- `.git/`
- `.gitignore`
- `.horosa-cache/`
- `.runtime/`
- `CertificateSigningRequest.certSigningRequest`
- `CertificateSigningRequest2.certSigningRequest`
- `Horosa-Web/`
- `Horosa_Desktop_Installer/`
- `Horosa_OneClick_Mac.command`
- `PROJECT_STRUCTURE.md`
- `README.md`
- `README_ZH.md`
- `README_EN.md`
- `UPGRADE_LOG.md`
- `default.profraw`
- `developerID_application.cer`
- `developerID_installer.cer`
- `diagnostics/`
- `modules/`
- `runtime/`
- `scripts/`
- `tools/`
- `主限法推演/`

额外说明：

- 根目录还存在 `.DS_Store` 这类 macOS 元数据文件，不属于业务结构。
- `.git/` 是仓库元数据目录，不属于产品代码结构本体。

### 1.2 根目录主线划分

如果从维护角度看，这个仓库现在实际上由 6 条主线组成：

1. `Horosa-Web/`
   Horosa 主业务工程，包含前端、Java 后端、Python 图表/算法服务。
2. `Horosa_Desktop_Installer/`
   macOS 桌面安装器、Tauri 壳、打包/签名/发布链路。
3. `scripts/` 和 `tools/`
   仓库级脚本、本地启动入口、浏览器验收与主限法专项校验。
4. `runtime/`
   运行时包、验证样本、主限法反推结果、发布验收结果。
5. `diagnostics/`、`README*.md`、根目录治理文件
   面向用户与维护者的说明、社区规范、许可证与诊断记录。
6. `modules/` 与 `主限法推演/`
   扩展参考实现、主限法专门文档与逆向记录。

### 1.3 根目录关键文件

- `Horosa_OneClick_Mac.command`
  根目录 Mac 一键入口。
- `README.md`
  总入口说明。
- `README_ZH.md`
  中文版产品/发布说明，当前重点已经明显转向 macOS 桌面正式分发。
- `README_EN.md`
  英文版说明。
- `UPGRADE_LOG.md`
  升级与变更记录。
- `PROJECT_STRUCTURE.md`
  当前这份结构说明。
- `default.profraw`
  本地性能/覆盖率相关残留产物，不是业务代码。
- `CertificateSigningRequest*.certSigningRequest`
  Apple 证书申请文件。
- `developerID_application.cer`
  Developer ID Application 证书文件。
- `developerID_installer.cer`
  Developer ID Installer 证书文件。

### 1.4 根目录本地运行痕迹

- `.horosa-cache/`
  根级缓存目录，当前看到的是 `paramhash/` 相关缓存。
- `.runtime/`
  本地运行时与虚拟环境目录，当前可见：
  - `.runtime/mac/`
  - `.runtime/mac/m2/`
  - `.runtime/mac/venv/`

## 2. 主业务工程：`Horosa-Web/`

这是 Horosa 的主业务代码区，也是桌面应用真正加载和调用的业务主体。

### 2.1 `Horosa-Web/` 的一级内容

当前在 `Horosa-Web/` 下可见的主要条目：

- `${env:HOME}/`
- `.horosa-browser-profile/`
- `.horosa-cache/`
- `.horosa-local-logs/`
- `.horosa_java.pid`
- `.horosa_py.pid`
- `.horosa_web.pid`
- `astropy/`
- `astrostudysrv/`
- `astrostudyui/`
- `flatlib-ctrad2/`
- `scripts/`
- `start_horosa_local.sh`
- `stop_horosa_local.sh`
- `verify_horosa_local.sh`

### 2.2 `Horosa-Web/` 的角色划分

- `astrostudyui/`
  Umi + React 前端。
- `astrostudysrv/`
  Java Maven 多模块后端。
- `astropy/`
  Python 图表、推运、历法、主限法等算法与服务接口。
- `flatlib-ctrad2/`
  内置/修改版 Python 占星依赖库，给 Horosa 的图表与推运能力提供底层支持。
- `scripts/repairEmbeddedPythonRuntime.py`
  主工程内部用于修复嵌入式 Python runtime 的脚本。

### 2.3 前端：`Horosa-Web/astrostudyui/`

#### 2.3.1 顶层文件与目录

`astrostudyui/` 当前可见的顶层内容包括：

- `.gitignore`
- `.tmp_ai_export_matrix_check.js`
- `.tmp_decode_response.js`
- `.tmp_encode_request.js`
- `.tmp_horosa_perf_check.js`
- `.tmp_horosa_verify.js`
- `.tmp_sanshi_calc_debug.mjs`
- `.umirc.js`
- `dist/`
- `dist-file/`
- `node_modules/`
- `package-lock.json`
- `package.json`
- `public/`
- `scripts/`
- `src/`

其中：

- `package.json`
  当前前端脚本包括：
  - `start`
  - `build`
  - `build:file`
  - `postinstall`
  - `prettier`
  - `test`
  - `test:coverage`
- `.umirc.js`
  Umi 项目配置入口。
- `dist/`
  常规前端构建产物。
- `dist-file/`
  用于桌面 runtime 打包的前端产物目录。
- `node_modules/`
  前端依赖目录。
- `.tmp_*`
  当前仓库里保留的调试/校验临时脚本。

#### 2.3.2 `astrostudyui/scripts/`

前端自己的脚本目录当前包含：

- `patch_quill_domnodeinserted.js`
  安装后补丁脚本。
- `verifyHorosaPerformanceRuntime.js`
  前端 runtime 性能校验。
- `verifyHorosaRuntimeFull.js`
  前端 runtime 全量校验。
- `verifyPrimaryDirectionRuntime.js`
  主限法 runtime 校验。
- `warmHorosaRuntime.js`
  runtime 预热脚本。

#### 2.3.3 `astrostudyui/src/` 主结构

`src/` 下当前可见的主要目录：

- `.umi/`
- `.umi-production/`
- `assets/`
- `components/`
- `constants/`
- `css/`
- `data/`
- `layouts/`
- `models/`
- `msg/`
- `pages/`
- `services/`
- `utils/`

其中：

- `.umi/`、`.umi-production/`
  Umi 自动生成目录，不是手写业务源码主入口。
- `components/`
  业务 UI 最核心目录。
- `models/`
  状态管理。
- `services/`
  接口请求层。
- `utils/`
  公共工具、缓存、AI 导出、主限法同步等。

#### 2.3.4 `astrostudyui/src/layouts/`

当前文件：

- `layouts/app.js`
- `layouts/app.less`
- `layouts/index.js`

这是前端整体布局入口层。

补充职责：

- `layouts/index.js`
  用 `antd` 的 `ConfigProvider` 注入中文 locale，设置 `moment` 为中文环境，并把全局 state 写入 `storageutil`。
- `layouts/app.js`
  是更外层的应用壳，负责包住页面级内容。

#### 2.3.5 `astrostudyui/src/pages/`

当前文件：

- `pages/404.js`
- `pages/document.ejs`
- `pages/index.js`
- `pages/index.less`

这是页面级入口与模板层。

补充职责：

- `pages/index.js`
  是实际主工作台入口，当前集中挂载了绝大多数业务模块，并通过左侧 Tabs 在单页内切换。
- `pages/document.ejs`
  页面模板。
- `pages/index.less`
  主页面样式。

`pages/index.js` 当前直接挂载的主工作台 Tab 为：

- `astrochart`：星盘
- `astrochart3D`：三维盘
- `direction`：推运盘
- `germanytech`：量化盘
- `relativechart`：关系盘
- `jieqichart`：节气盘
- `locastro`：星体地图
- `guolao`：七政四余
- `hellenastro`：希腊星术
- `indiachart`：印度律盘
- `cntradition`：八字紫微
- `cnyibu`：易与三式
- `calendar`：万年历
- `otherbu`：西洋游戏
- `astroreader`：书籍阅读
- `liveplayer`：星阙直播
- `admintools`：管理工具
- `fengshui`：风水
- `sanshiunited`：三式合一

主要 Tab 与组件映射关系为：

- `astrochart` -> `AstroChartMain`
- `astrochart3D` -> `AstroChartMain3D`
- `direction` -> `AstroDirectMain`
- `germanytech` -> `AstroGermany`
- `relativechart` -> `AstroRelative`
- `jieqichart` -> `JieQiChartsMain`
- `locastro` -> `LocAstroMain`
- `guolao` -> `GuoLaoChartMain`
- `hellenastro` -> `HellenAstroMain`
- `indiachart` -> `IndiaChartMain`
- `cntradition` -> `CnTraditionMain`
- `cnyibu` -> `CnYiBuMain`
- `calendar` -> `CalendarMain`
- `otherbu` -> `OtherBuMain`
- `astroreader` -> `BookMain`
- `liveplayer` -> `MediaMain`
- `admintools` -> `AdminToolsMain`
- `fengshui` -> `FengShuiMain`
- `sanshiunited` -> `SanShiUnitedMain`

`pages/index.js` 还承担了一些关键页面级协调逻辑：

- 根据当前 tab 调用 `predictHook`
- 在未确认时间编辑时延迟触发 `astro/fetchByFields`
- 管理主抽屉的开关
- 协调 chart/case/login/register 等多个表单组件

前端“抽屉层”当前由 `astro` model 统一管理，已知 drawer key 包括：

- `query`
- `selectplanet`
- `selectchartdisplay`
- `selectasp`
- `register`
- `login`
- `resetpwd`
- `changepwd`
- `changeparams`
- `chartlist`
- `chartedit`
- `chartadd`
- `caselist`
- `caseedit`
- `caseadd`
- `chartdeeplearn`
- `memo`
- `chartsgps`
- `commtools`
- `homepage`

#### 2.3.6 `astrostudyui/src/constants/`

当前文件：

- `AstroColor0.js`
- `AstroColor1.js`
- `AstroColor2.js`
- `AstroColor3.js`
- `AstroColor4.js`
- `AstroColor5.js`
- `AstroColor6.js`
- `AstroColor7.js`
- `AstroColor8.js`
- `AstroConst.js`
- `AstroText.js`
- `ReaderConst.js`
- `ZWColor.js`
- `ZWConst.js`
- `ZWText.js`

这一层主要承载：

- 西占图面颜色与常量
- 紫微相关常量与颜色
- 阅读器相关常量

#### 2.3.7 `astrostudyui/src/css/`

当前文件：

- `styles.less`

#### 2.3.8 `astrostudyui/src/data/`

当前可见数据文件：

- `data/deeplearn/10000.json`
- `data/deeplearn/20000.json`
- `data/deeplearn/30000.json`
- `data/deeplearn/40000.json`

这部分与前端深度学习展示/统计有关。

##### 补充：`astrostudyui/public/`、`src/assets/`、`src/msg/`

`public/` 当前实际内容：

- `public/fengshui/`
  - `app.js`
  - `index.html`
  - `styles.css`
- `public/gltf/draco/`
  - `draco_decoder.js`
  - `draco_decoder.wasm`
  - `draco_wasm_wrapper.js`

这说明前端除了普通静态资源外，还内置了：

- 一个单独的风水静态页面资源集
- 3D 图形相关的 Draco 解码资源

`src/assets/` 当前实际内容：

- 图像资源：
  - `beian.png`
  - `blogo.jpg`
  - `mlogo.jpg`
  - `sealed.png`
  - `slogo.jpg`
- 字体与字形资源：
  - `morinus-webfont.ttf`
  - `morinus-webfont.woff`
  - `morinus-webfont.woff2`
  - `ywastro.ttf`
  - `ywastro.woff`
  - `ywastro.woff2`
  - `ywastrochart.ttf`
  - `ywastrochart.woff`
  - `ywastrochart.woff2`
- 字体描述/字形映射：
  - `helvetica.json`
  - `ywastro.json`
  - `ywastrochart.json`
- 多媒体兼容资源：
  - `video-js.swf`

`src/msg/` 当前实际文件：

- `bazimsg.js`
- `errmsg.js`
- `msg.js`
- `stat.js`
- `types.js`

这层主要是页面消息、错误提示、统计/类型文案。

#### 2.3.9 `astrostudyui/src/models/`

当前文件：

- `models/app.js`
- `models/astro.js`
- `models/rules.js`
- `models/user.js`
- `models/websock.js`

角色划分：

- `app.js`
  全局应用级状态。
- `astro.js`
  占星/排盘主状态。
- `rules.js`
  规则类状态。
- `user.js`
  用户、命盘/事盘管理状态。
- `websock.js`
  WebSocket 状态。

补充：

- 当前 `models/` 只有 5 个文件，说明前端状态模型比较集中，核心状态主要落在 `app / astro / user / rules / websock` 五类。
- `models/app.js`
  当前主要管理：
  - loading / loadingText / refresh
  - 图面显示选项：`chartDisplay`、`planetDisplay`、`lotsDisplay`
  - 主题与配色：`colorTheme`
  - 主限法显示与方法：`showPdBounds`、`pdMethod`、`pdTimeKey`
  - 登录/注册表单 fields
  - 全局配置写入 `localStorage(GlobalSetupKey)`
- `models/astro.js`
  当前主要管理：
  - 主工作台高度
  - 当前 `chartObj`
  - 所有抽屉显隐状态
  - 当前主 tab 与当前 sub tab
  - 起盘 fields
  - `predictHook`
  - AI 快照与 deeplearn 相关状态
  并且默认 fields 中就已经内置：
  - 本命起盘参数
  - 主限法参数：`showPdBounds`、`pdtype`、`pdMethod`、`pdTimeKey`、`pdaspects`
  - 八字/节气/南北盘等中式参数
- `models/user.js`
  当前主要管理：
  - token / userInfo / admin
  - 命盘分页列表
  - 事盘分页列表
  - 书架与当前书籍
  - 修改密码表单
  - 当前 chart / 当前 case fields
  - 本地命盘与本地事盘分页访问

- `models/rules.js`
  当前非常聚焦，主要就是拉取并缓存 `ziwei` 规则数据。
- `models/websock.js`
  当前也非常轻，主要封装：
  - `send`
  - `setCmd`
  - `setup` 时是否自动连接 `globalWS`

从 effects 名称看，当前各 model 的主要动作如下：

- `app`
  - `fetchImgToken`
  - `login`
  - `register`
  - `resetPwd`
  - `checkUser`
  - `checkOnlyUser`
  - `logout`
  - `menuClick`
  - `getSysTime`
  - `beginRefresh`
  - `endRefresh`
- `astro`
  - `closeDrawer`
  - `openDrawer`
  - `fetch`
  - `fetchByChartData`
  - `fetchByFields`
  - `doHook`
  - `nowChart`
  - `setHomePage`
  - `fetchFateEvents`
  - `deeplearn`
- `user`
  - `newCurrentChart`
  - `setCurrentChart`
  - `newCurrentCase`
  - `setCurrentCase`
  - `fetchCases`
  - `searchCases`
  - `addCase`
  - `updateCase`
  - `deleteCase`
  - `applyCase`
  - `searchCharts`
  - `fetchCharts`
  - `addChart`
  - `updateChart`
  - `saveMemo`
  - `deleteChart`
  - `changePwd`
  - `changeParams`
  - `listBooks`
  - `deleteBook`
  - `removeBook`
  - `updateBook`
  - `readBook`

这说明当前前端状态不是按“页面一个 model”拆的，而是按“全局配置 / 排盘主状态 / 用户数据 / 规则 / WebSocket”集中管理。

再往下看一层，`models/astro.js` 里 `newEmptyFields()` 初始化的核心字段已经可以视为“前端统一起盘参数总表”，当前明确包括：

- 基础身份字段：
  - `cid`
  - `name`
  - `pos`
  - `group`
- 时间地理字段：
  - `ad`
  - `date`
  - `time`
  - `zone`
  - `lat`
  - `lon`
  - `gpsLat`
  - `gpsLon`
- 西占排盘参数：
  - `hsys`
  - `zodiacal`
  - `tradition`
  - `strongRecption`
  - `simpleAsp`
  - `virtualPointReceiveAsp`
  - `doubingSu28`
  - `houseStartMode`
- 推运/主限法参数：
  - `predictive`
  - `showPdBounds`
  - `pdtype`
  - `pdMethod`
  - `pdTimeKey`
  - `pdaspects`
- 时间算法与中式附加参数：
  - `timeAlg`
  - `phaseType`
  - `godKeyPos`
  - `after23NewDay`
  - `adjustJieqi`
  - `gender`
  - `southchart`
- 各技术 memo 字段：
  - `memoZiWei`
  - `memoBaZi`
  - `memoAstro`
  - `memo74`
  - `memoGua`
  - `memoLiuReng`
  - `memoQiMeng`
  - `memoSuZhan`

`fieldsToParams(...)` 真正向排盘/推运接口发送的参数主集则收敛为：

- `cid`
- `ad`
- `date`
- `time`
- `zone`
- `lat`
- `lon`
- `gpsLat`
- `gpsLon`
- `hsys`
- `southchart`
- `zodiacal`
- `tradition`
- `doubingSu28`
- `strongRecption`
- `simpleAsp`
- `virtualPointReceiveAsp`
- `predictive`
- `showPdBounds`
- `pdtype`
- `pdMethod`
- `pdTimeKey`
- `pdaspects`
- `name`
- `pos`
- `group`

这说明：

- `astro` model 既管理 UI 抽屉状态，也管理一整套“可跨西占/中式/推运共用”的统一参数对象。
- memo 字段虽然挂在同一组 `fields` 里，但更接近用户数据和导出上下文，不是每次排盘计算都必需的纯算法参数。

#### 2.3.10 `astrostudyui/src/services/`

当前文件：

- `services/app.js`
- `services/astro.js`
- `services/rules.js`
- `services/user.js`

这是前端与后端接口的主要封装层。

补充接口职责：

- `services/astro.js`
  当前直接可见的接口函数包括：
  - `fetchChart`
  - `fetchAllowedCharts`
  - `fetchFateEvents`
  - `dlTrain`
其中 `fetchChart` 自带前端内存缓存和 inflight 去重。
- `services/user.js`
  当前直接可见的接口函数包括：
  - 用户参数与密码：
    - `changepwd`
    - `changeparams`
    - `checkUser`
  - 命盘管理：
    - `getUserCharts`
    - `addChart`
    - `updateChart`
    - `saveMemo`
    - `deleteChart`
    - `importChart`
    - `exportChart`
  - 书籍阅读器：
    - `listBooks`
    - `allBooks`
    - `getChapter`
    - `updateBook`
    - `deleteBook`
    - `removeBook`
    - `readprogress`

这说明前端 service 层虽然文件数少，但一头连排盘后端，一头连用户数据和阅读器后端。

对应的已知接口路径包括：

- `services/astro.js`
  - `/chart`
  - `/allowedcharts`
  - `/deeplearn/fateevents`
  - `/deeplearn/train`
- `services/user.js`
  - `/user/changepwd`
  - `/user/changeparams`
  - `/user/check`
  - `/user/charts`
  - `/user/charts/add`
  - `/user/charts/update`
  - `/user/charts/memo`
  - `/user/charts/delete`
  - `/user/charts/import`
  - `/user/charts/export`
  - `/astroreader/listbooks`
  - `/astroreader/allbooks`
  - `/astroreader/getchapter`
  - `/astroreader/updatebook`
  - `/astroreader/deletebook`
  - `/astroreader/removebook`
  - `/astroreader/readprogress`

如果进一步落到“函数 -> 路由 -> 后端 controller”的粒度，当前可以明确对应为：

- `services/app.js`
  - `getImgToken()` -> `/common/imgToken` -> `astrostudy/controller/TokenController.java`
  - `login()` -> `/user/login` -> `astrostudy/controller/LoginController.java`
  - `register()` -> `/user/register` -> `astrostudy/controller/RegisterController.java`
  - `resetpwd()` -> `/user/resetpwd` -> `astrostudy/controller/ResetPwdController.java`
  - `checkUser()` -> `/user/check` -> `astrostudy/controller/UserCheckLoginController.java`
  - `logout()` -> `/user/logout` -> `astrostudy/controller/LoginController.java`
  - `systime()` -> `/common/time` -> `basecomm/controller/SystemController.java`
- `services/astro.js`
  - `fetchChart()` -> `/chart` -> `astrostudycn/controller/ChartController.java`
  - `fetchAllowedCharts()` -> `/allowedcharts` -> `astrostudy/controller/AllowedChartController.java`
  - `fetchFateEvents()` -> `/deeplearn/fateevents` -> `astrodeeplearn/controller/DeepLearnController.java`
  - `dlTrain()` -> `/deeplearn/train` -> `astrodeeplearn/controller/DeepLearnController.java`
- `services/rules.js`
  - `ziweirules()` -> `/ziwei/rules` -> `astrostudycn/controller/ZiWeiController.java`
- `services/user.js`
  - `changepwd()` -> `/user/changepwd` -> `astrostudy/controller/UserInfoController.java`
  - `changeparams()` -> `/user/changeparams` -> `astrostudy/controller/UserInfoController.java`
  - `checkUser()` -> `/user/check` -> `astrostudy/controller/UserCheckLoginController.java`
  - `getUserCharts()` -> `/user/charts` -> `astrostudy/controller/UserChartsController.java`
  - `addChart()` -> `/user/charts/add` -> `astrostudy/controller/UserChartsController.java`
  - `updateChart()` -> `/user/charts/update` -> `astrostudy/controller/UserChartsController.java`
  - `saveMemo()` -> `/user/charts/memo` -> `astrostudy/controller/UserChartsController.java`
  - `deleteChart()` -> `/user/charts/delete` -> `astrostudy/controller/UserChartsController.java`
  - `importChart()` -> `/user/charts/import` -> `astrostudy/controller/UserDataTransferController.java`
  - `exportChart()` -> `/user/charts/export` -> `astrostudy/controller/UserDataTransferController.java`
  - `listBooks()` -> `/astroreader/listbooks` -> `astroreader/controller/ReaderController.java`
  - `allBooks()` -> `/astroreader/allbooks` -> `astroreader/controller/ReaderController.java`
  - `getChapter()` -> `/astroreader/getchapter` -> `astroreader/controller/ReaderController.java`
  - `updateBook()` -> `/astroreader/updatebook` -> `astroreader/controller/ReaderController.java`
  - `deleteBook()` -> `/astroreader/deletebook` -> `astroreader/controller/ReaderController.java`
  - `removeBook()` -> `/astroreader/removebook` -> `astroreader/controller/ReaderController.java`
  - `readprogress()` -> `/astroreader/readprogress` -> `astroreader/controller/ReaderController.java`

更细一点，当前前端并不是所有接口都先包进 `services/`，很多业务组件直接请求后端。按“页面/组件 -> 路由 -> 后端落点”整理如下：

- 西占推运与主限法链：
  - `components/astro/AstroSolarReturn.js` -> `/predict/solarreturn`
  - `components/astro/AstroLunarReturn.js` -> `/predict/lunarreturn`
  - `components/astro/AstroGivenYear.js` -> `/predict/givenyear`
  - `components/astro/AstroProfection.js` -> `/predict/profection`
  - `components/astro/AstroSolarArc.js` -> `/predict/solararc`
  - `components/astro/AstroZR.js` -> `/predict/zr`
  - `components/astro/AstroPrimaryDirectionChart.js` -> `/predict/pd`、`/predict/pdchart`
  - `components/direction/AstroDirectMain.js` -> `/predict/pd`
  - `components/dice/DiceMain.js` -> `/predict/dice`
  - Java 落点：`astrostudy/controller/PredictiveController.java`
  - Python 对应挂载：`astropy/websrv/predictsrv.py`，由 `webchartsrv.py` 挂到 `/predict`
- 西占其它直连：
  - `components/acg/AstroAcg.js` -> `/location/acg` -> `astrostudy/controller/AcgController.java`
  - `components/germany/AstroMidpoint.js` -> `/germany/midpoint` -> `astrostudy/controller/GermanyTechController.java`
  - `components/astro/AstroRelative.js` -> `/modern/relative` -> `astrostudy/controller/ModernChartController.java`
  - `components/astro/IndiaChart.js` -> `/india/chart` -> `astrostudy/controller/IndiaChartController.java`
  - `components/comp/DateTime.js` -> `/jdn/date` -> `astrostudy/controller/JdnController.java`
- 中式排盘与历法链：
  - `components/cntradition/BaZi.js` -> `/bazi/direct` -> `astrostudycn/controller/PaiBaZiController.java`
  - `components/ziwei/ZiWeiMain.js` -> `/ziwei/birth`、`/ziwei/rules` -> `astrostudycn/controller/ZiWeiController.java`
  - `components/calendar/NongLiMain.js` -> `/calendar/month` -> `astrostudycn/controller/CalendarController.java`
  - `utils/preciseCalcBridge.js` -> `/nongli/time`、`/jieqi/year` -> `astrostudycn/controller/NongliController.java`、`astrostudycn/controller/JieQiController.java`
- 易卦、六壬、三式链：
  - `components/calendar/NongLiMain.js` -> `/gua/desc` -> `astrostudycn/controller/GuaController.java`
  - `components/gua/MeiyiGuaSym.js` -> `/gua/meiyi`
  - `components/gua/DoubleMeiyiGuaSym.js` -> `/gua/desc`、`/gua/meiyi`
  - `components/guazhan/GuaZhanMain.js` -> `/gua/desc`
  - `components/lrzhan/LiuRengMain.js` -> `/liureng/gods`、`/liureng/runyear` -> `astrostudycn/controller/LiuRengController.java`
  - `components/jinkou/JinKouMain.js` -> `/liureng/gods`、`/liureng/runyear` -> `astrostudycn/controller/LiuRengController.java`
- 小工具与公共计算链：
  - `components/commtools/Azimuth.js` -> `/calc/azimuth` -> `astrostudy/controller/CalcController.java`
  - `components/commtools/CoordTrans.js` -> `/calc/cotrans` -> `astrostudy/controller/CalcController.java`
  - `components/commtools/Calculator.js` -> `/calc/calculate`、`/calc/formula` -> `astrostudy/controller/CalcController.java`
  - `components/commtools/NaYing.js` -> `/common/naying` -> `astrostudy/controller/CommController.java`
  - `components/commtools/InverseBazi.js` -> `/common/inversebazi`、`/bazi/direct`
  - `components/commtools/CuanGong12Desc.js` -> `/common/gong12gods`
  - `components/commtools/CuanGong12Query.js` -> `/common/gong12`
  - `components/commtools/BaziPithy.js` -> `/common/pithy`
  - `components/commtools/BaziPattern.js` -> `/bazi/pattern`、`/bazi/pattern/update` -> `astrostudycn/controller/BaZiPatternController.java`
- 统计、阅读、多媒体链：
  - `components/statis/Statis.js` -> `/statis/count`、`/statis/chartsgps` -> `astrostudy/controller/StatisticController.java`
  - `components/reader/*` -> `/astroreader/upload`、`/astroreader/getchapter`、`/astroreader/tts`、`/astroreader/exportbook` 等 -> `astroreader/controller/ReaderController.java`、`astroreader/controller/TTSController.java`
  - `components/multimedia/*` -> `/astroreader/flvurl`、`/astroreader/restartlive`、`/astroreader/livepublishpath`、`/live/getstreams`、`/live/playpath` -> `astroreader/controller/FlvUrlController.java`、`astroreader/controller/RtmpController.java`

因此前端调用链实际上分为两层：

- 一层是规范化的 `services/*.js`
- 一层是大量组件内嵌的“直连路由调用”

维护接口时，不能只检查 `services/`，还要同时搜索组件里的 `request(\`${ServerRoot}/...\`)`。

#### 2.3.11 `astrostudyui/src/utils/`

当前文件：

- `WebSock.js`
- `aiExport.js`
- `astroAiSnapshot.js`
- `bytes.js`
- `constants.js`
- `decennials.js`
- `gps.js`
- `helper.js`
- `localCalcCache.js`
- `localNongliAdapter.js`
- `localcases.js`
- `localcharts.js`
- `localdeeplearn.js`
- `moduleAiSnapshot.js`
- `planetHouseInfo.js`
- `preciseCalcBridge.js`
- `predictiveAiSnapshot.js`
- `primaryDirectionSync.js`
- `request.js`
- `rsahelper.js`
- `storageutil.js`
- `wshelper.js`

测试文件：

- `utils/__tests__/decennials.test.js`
- `utils/__tests__/primaryDirectionSync.test.js`

其中当前最值得维护时优先注意的文件包括：

- `aiExport.js`
  AI 导出总入口。
- `decennials.js`
  十年大运计算核心。
- `primaryDirectionSync.js`
  主限法盘/主限法表格同步逻辑。
- `preciseCalcBridge.js`
  精确计算桥接。
- `request.js`
  统一请求封装。
- `constants.js`
  前端本地/线上服务地址相关逻辑。
- `localcases.js`、`localcharts.js`
  本地命盘/事盘存储映射。

补充职责：

- `primaryDirectionSync.js`
  当前显式定义了：
  - `PD_SYNC_REV = 'pd_method_sync_v6'`
  - 默认主限法方法 `astroapp_alchabitius`
  - 默认时间键 `Ptolemy`
  - 允许同步的推运子页集合
  并提供 `mergePrimaryDirectionChartObj(...)`，把主限法表格行、方法、时间键和盘面参数合并进统一 `chartObj`。
- `aiExport.js`
  是一个很重的总控文件，当前集中维护：
  - 技法识别表
  - AI 导出 section 预设
  - 中西术语替换表
  - 节气盘拆分导出规则
  - 主限法、六壬、遁甲、三式合一等模块的导出配置
- `request.js`
  所有前端请求最终都会走这里。
- `storageutil.js`
  负责全局状态与本地存储桥接。
- `localCalcCache.js`
  本地计算缓存。
- `astroAiSnapshot.js` / `moduleAiSnapshot.js` / `predictiveAiSnapshot.js`
  快照导出三层体系。

按文件数量看，当前：

- `utils/` 共有 24 个文件
- `services/` 共有 4 个文件
- `models/` 共有 5 个文件

`utils/constants.js` 当前还承载了部署层事实：

- 本地模式下，`ServerRoot` 会优先按：
  1. 页面 `srv` 查询参数
  2. 页面端口 `webPort + 1999`
  3. `localStorage.horosaLocalServerRoot`
  来推导后端地址
- 本地默认回退后端地址：`http://127.0.0.1:9999`
- 线上后端地址：`https://srv.horosa.com`
- 线上移动端：`https://mobileweb.horosa.com`
- 线上 3D 服务：`https://chart3d.horosa.com`
- WebSocket：`ws://www.horosa.com:26900/ws`
- RTMP 推流：`https://rtmpush.horosa.com`
- RTMP 播流：`https://rtmp.horosa.com`

`utils/request.js` 当前除了请求本身，还负责：

- 统一 loading 管理
- 本地 token 读取与清理
- “需要重新登录”判定与节流弹错
- 错误码翻译
- 请求签名
- RSA 加密/解密桥接
- `fetch cache` 选项兼容处理

如果从“浏览器侧状态落盘”来看，`utils/` 和部分组件还共同维护了一批固定 key，当前已知的重要键如下：

- 全局配置与登录键：
  - `globalSetup`
    - 来源：`utils/constants.js`、`models/app.js`
    - 内容：`chartDisplay / planetDisplay / lotsDisplay / colorTheme / showPdBounds / pdMethod / pdTimeKey / showPlanetHouseInfo / showAstroMeaning / showOnlyRulExaltReception`
  - `Token`
    - 来源：`models/app.js`、`utils/request.js`
    - 用途：登录态 token
  - `LoginId`
    - 来源：`models/app.js`
    - 用途：记住登录账号
  - `pchomepage`
    - 来源：`utils/constants.js`、`components/HomePageSetup.js`、`models/app.js`
    - 用途：首页/默认模块选择
  - `horosaLocalServerRoot`
    - 来源：`utils/constants.js`
    - 用途：本地桌面/localhost 模式下缓存推导出的后端根地址
- AI 导出与快照键：
  - `horosa.ai.export.settings.v1`
    - 来源：`utils/aiExport.js`
    - 用途：AI 导出 section 选择、planet info 开关、占星释义开关
  - `horosa.ai.snapshot.astro.v1`
    - 来源：`utils/astroAiSnapshot.js`
    - 用途：当前西占盘统一 AI 快照
  - `horosa.ai.snapshot.module.v1.<moduleName>`
    - 来源：`utils/moduleAiSnapshot.js`
    - 用途：六壬、遁甲、风水、三式合一等模块级 AI 快照
- 本地命盘/事盘与算法缓存键：
  - `horosa.localCharts.v1`
    - 来源：`utils/localcharts.js`
    - 用途：本地命盘库
  - `horosa.localCases.v1`
    - 来源：`utils/localcases.js`
    - 用途：本地事盘库
  - `horosa.localcalc.nongli.v1`
  - `horosa.localcalc.jieqi.v2`
  - `horosa.localcalc.jieqiYear.v1`
  - `horosa.localcalc.birthGanzhi.v1`
  - `horosa.localcalc.liureng.runyear.v1`
    - 来源：`utils/localCalcCache.js`
    - 用途：农历、节气、八字干支、六壬流年等本地计算缓存
- 阅读器键：
  - `readerTheme`
  - `readerFontSize`
  - `chapterScrollTop`
  - `readerBook`
  - `TTSOpt`
    - 来源：`constants/ReaderConst.js`、`components/reader/BookReader.js`
    - 用途：阅读主题、字号、滚动位置、当前书籍、TTS 参数
- 前端模块偏好键：
  - `aspects`
    - 来源：`constants/AstroConst.js`、`components/astro/AspSelector.js`
    - 用途：相位显示选择
  - `ziweiTips`
  - `ziweiChartType`
    - 来源：`components/ziwei/*`
    - 用途：紫微提示与盘型偏好
  - `liurengChartType`
    - 来源：`components/lrzhan/LiuRengInput.js`
    - 用途：六壬盘型偏好
  - `suzhanChartType`
  - `suzhanChartShape`
  - `suzhanHouseStartMode`
    - 来源：`components/suzhan/*`、`components/guolao/*`
    - 用途：宿盘与过老盘显示偏好
  - `commtoolstab`
    - 来源：`components/commtools/CommToolsMain.js`
    - 用途：小工具当前 tab
  - `qimenShowPatternInterpretation`
    - 来源：`components/dunjia/DunJiaMain.js`
    - 用途：是否显示奇门格局解读
  - `baziopt`
    - 来源：`components/cntradition/BaZi.js`
    - 用途：八字显示选项
  - `baziPattern`
    - 来源：`components/commtools/BaziPattern.js`
    - 用途：八字格局分析输入缓存
  - `baziInverse`
    - 来源：`components/commtools/InverseBazi.js`
    - 用途：反推八字输入缓存
  - `guaData`
    - 来源：`components/gua/GuaSymDesc.js`
    - 用途：卦象说明缓存
  - `CalculatorFormula`
    - 来源：`components/commtools/Calculator.js`
    - 用途：公式计算器缓存
  - `horosa3dModelUnavailableAt`
    - 来源：`components/astro3d/Astro3D.js`
    - 用途：3D 模型不可用时间戳，写入 local/session storage 双份

除了 `localStorage/sessionStorage`，当前还存在几类运行时全局变量：

- `window.__horosa_astro_ai_snapshot`
  - 来源：`utils/astroAiSnapshot.js`
  - 用途：西占快照内存态
- `window.__horosa_module_ai_snapshot_map`
  - 来源：`utils/moduleAiSnapshot.js`
  - 用途：模块快照全局 map
- `window.__horosa_liureng_snapshot_text`
  - 来源：`components/lrzhan/LiuRengMain.js`
- `window.__horosa_qimen_snapshot_text`
  - 来源：`components/dunjia/DunJiaMain.js`
- `window.__horosa_fengshui_snapshot_text`
  - 来源：`components/fengshui/FengShuiMain.js`
- `window.horosaDesktop`
  - 来源：桌面壳注入桥接
  - 用途：前端导出 diagnostics、与桌面容器交互

模块快照刷新当前通过统一 DOM 事件驱动：

- 事件名：`horosa:refresh-module-snapshot`
- 监听者已知包括：
  - `direction/AstroDirectMain.js`
  - `germany/AstroMidpoint.js`
  - `sanshi/SanShiUnitedMain.js`
  - `lrzhan/LiuRengMain.js`
  - `dunjia/DunJiaMain.js`
  - `fengshui/FengShuiMain.js`
  - `astro/AstroRelative.js`
  - `astro/AstroPrimaryDirectionChart.js`

这一层很重要，因为它说明 Horosa 前端并不只是“请求接口 + 渲染页面”，而是已经形成：

- `store(model)` 状态层
- `request/service` 接口层
- `localStorage` 持久层
- `window/global event` 会话层
- `AI snapshot` 导出层

五层叠加结构。

#### 2.3.12 `astrostudyui/src/components/` 总览

这是前端最重的目录。当前实际存在的组件子目录有：

- `acg/`
- `admintools/`
- `amap/`
- `astro/`
- `astro3d/`
- `calendar/`
- `cntradition/`
- `cnyibu/`
- `commtools/`
- `comp/`
- `deeplearn/`
- `dice/`
- `direction/`
- `dunjia/`
- `fengshui/`
- `germany/`
- `graph/`
- `gua/`
- `guazhan/`
- `guolao/`
- `hellenastro/`
- `homepage/`
- `jieqi/`
- `jinkou/`
- `liureng/`
- `loc/`
- `logqry/`
- `lrzhan/`
- `multimedia/`
- `otherbu/`
- `reader/`
- `relative/`
- `ruleziwei/`
- `sanshi/`
- `statis/`
- `su28/`
- `suzhan/`
- `szbagua/`
- `szdunjia/`
- `szfangwei/`
- `szfengye/`
- `sznixiang/`
- `szsign/`
- `sztaiyi/`
- `taiyi/`
- `tongshefa/`
- `user/`
- `ziwei/`

此外，`components/` 根级还有：

- `HomePageSetup.js`
- `RichEditor.js`

按目录文件数量看，当前最重的前端模块是：

- `astro/`：38 个文件
- `su28/`：33 个文件
- `cntradition/`：17 个文件
- `user/`：16 个文件
- `commtools/`：12 个文件
- `liureng/`：12 个文件
- `ziwei/`：12 个文件

中等体量模块包括：

- `comp/`：10 个文件
- `graph/`：8 个文件
- `relative/`：8 个文件
- `amap/`：7 个文件
- `jinkou/`：7 个文件
- `lrzhan/`：7 个文件
- `multimedia/`：7 个文件
- `dunjia/`：6 个文件
- `reader/`：6 个文件
- `ruleziwei/`：6 个文件
- `suzhan/`：6 个文件

这说明：

- `astro/` 仍然是前端第一核心域
- `su28/`、`cntradition/`、`liureng/`、`ziwei/` 这些中式模块也已经非常成体系
- `user/` 与 `commtools/` 不是附属，而是完整的支撑子系统

#### 2.3.13 `components/astro/`

这是西占、推运、主限法的核心组件目录。当前文件包括：

- `AspSelector.js`
- `AstroAspect.js`
- `AstroChart.js`
- `AstroChartCircle.js`
- `AstroChartMain.js`
- `AstroDecennials.js`
- `AstroDirectionForm.js`
- `AstroDoubleChart.js`
- `AstroDoubleChartMain.js`
- `AstroFirdaria.js`
- `AstroFormComp.js`
- `AstroGivenYear.js`
- `AstroHelper.js`
- `AstroInfo.js`
- `AstroLots.js`
- `AstroLunarReturn.js`
- `AstroMeaningData.js`
- `AstroMeaningPopover.js`
- `AstroPlanet.js`
- `AstroPredictPlanetSign.js`
- `AstroPrimaryDirection.js`
- `AstroPrimaryDirectionChart.js`
- `AstroProfection.js`
- `AstroRelative.js`
- `AstroSolarArc.js`
- `AstroSolarReturn.js`
- `AstroZR.js`
- `ChartDisplaySelector.js`
- `ChartSearchModal.js`
- `IndiaChart.js`
- `IndiaChartMain.js`
- `LatInput.js`
- `LonInput.js`
- `PlanetSelector.js`
- `PlusMinusTime.js`
- `ZodiacalRelease.js`

这组文件基本覆盖：

- 本命盘/星盘主界面
- 双盘与关系盘
- 主限法
- 十年大运
- 法达
- 小限/流年/返照/太阳弧
- 印度律盘
- 图面配置与搜索

其中在主工作台里承担“一级页面”的核心组件主要是：

- `AstroChartMain`
  星盘主页面
- `AstroChartMain3D`
  三维盘主页面
- `AstroRelative`
  关系盘入口
- `IndiaChartMain`
  印度律盘入口
- `AstroPrimaryDirection`
  主/界限法表格页
- `AstroPrimaryDirectionChart`
  主限法盘页
- `AstroZR`
  黄道星释页
- `AstroFirdaria`
  法达星限页
- `AstroProfection`
  小限法页
- `AstroSolarArc`
  太阳弧页
- `AstroSolarReturn`
  太阳返照页
- `AstroLunarReturn`
  月亮返照页
- `AstroGivenYear`
  流年法页
- `AstroDecennials`
  十年大运页

#### 2.3.14 `components/jinkou/`

当前文件：

- `JinKouCalc.js`
- `JinKouCalc.test.js`
- `JinKouChart.js`
- `JinKouMain.js`
- `JinKouMain.test.js`
- `JinKouPanChart.js`
- `JinKouState.js`

这是金口诀页面、计算、盘面和回归测试的完整组合。

#### 2.3.15 `components/lrzhan/`

当前文件：

- `LiuRengBirthInput.js`
- `LiuRengChart.js`
- `LiuRengInput.js`
- `LiuRengMain.js`
- `RengChart.js`

这是当前主用六壬“战盘/格局参考”页面实现。

#### 2.3.16 `components/liureng/`

当前文件：

- `ChuangChart.js`
- `ChuangChart.test.js`
- `GodChart.js`
- `KeChart.js`
- `LRChart.js`
- `LRCircleChart.js`
- `LRCommChart.js`
- `LRConst.js`
- `LRInnerChart.js`
- `LRPanStyle.js`
- `LRShenJiangDoc.js`
- `LRZhangSheng.js`

这组文件更偏六壬基础盘、图形化组件与文档说明层。

#### 2.3.17 `components/dunjia/`

当前文件：

- `DunJiaBaGongRules.js`
- `DunJiaCalc.js`
- `DunJiaMain.js`
- `QimenXiangDoc.js`

这是遁甲页面、八宫规则、快照与说明文档核心。

#### 2.3.18 `components/taiyi/`

当前文件：

- `TaiYiCalc.js`
- `TaiYiMain.js`

#### 2.3.19 `components/tongshefa/`

当前文件：

- `TongSheFaMain.js`

#### 2.3.20 `components/sanshi/`

当前文件：

- `SanShiUnitedMain.js`

这是三式合一的综合工作面。

#### 2.3.21 `components/cntradition/`

当前文件：

- `BaZi.js`
- `BaZiZhangSheng.js`
- `CnTraditionInput.js`
- `CnTraditionMain.js`
- `FourZhu.js`
- `FourZhuGuaDesc.js`
- `GanHeCong.js`
- `Gods.js`
- `MDSDirect.js`
- `MDSYear.js`
- `MainDirection.js`
- `MainDirectionSimple.js`
- `PaiBaZi.js`
- `SmallDirection.js`
- `Zhu.js`
- `ZhuMing12.js`
- `ZiHeCong.js`

这是八字、四柱、命运方向等中式传统体系页面。

`CnTraditionMain.js` 当前把“八字紫微”一级页拆成 5 个右侧 Tab：

- `bazi`：八字
- `ziwei`：紫微斗数
- `guasym`：八卦类象
- `cuangong12`：十二串宫
- `pithy`：八字规则

#### 2.3.22 `components/ziwei/` 与 `components/ruleziwei/`

`ziwei/` 当前文件：

- `ZWCenterHouse.js`
- `ZWChart.js`
- `ZWCommHouse.js`
- `ZWHouse.js`
- `ZWHouseSangHe.js`
- `ZWIndicator.js`
- `ZiWeiChart.js`
- `ZiWeiHelper.js`
- `ZiWeiHouse.js`
- `ZiWeiInput.js`
- `ZiWeiJiangStar.js`
- `ZiWeiMain.js`

`ruleziwei/` 当前文件：

- `RuleHouses.js`
- `RuleHuaDesc.js`
- `RuleSihua.js`
- `RuleStars.js`
- `ZWIndication.js`
- `ZWRuleMain.js`

前者是紫微排盘与界面，后者是规则说明与判读材料。

#### 2.3.23 `components/relative/`

当前文件：

- `AntisciaInfo.js`
- `AspectInfo.js`
- `AstroCompare.js`
- `AstroComposite.js`
- `AstroMarks.js`
- `AstroSynastry.js`
- `AstroTimeSpace.js`
- `MidpointInfo.js`

这是关系盘与中点相关模块。

#### 2.3.24 `components/astro3d/`

当前文件：

- `Astro3D.js`
- `AstroChart3D.js`
- `AstroChartMain3D.js`
- `TextSprite.js`

#### 2.3.25 `components/acg/`、`components/amap/`、`components/germany/`

`acg/` 当前文件：

- `AcgHelper.js`
- `AstroAcg.js`
- `AstroLinesSelector.js`

`amap/` 当前文件：

- `ACG.js`
- `GeoCoord.js`
- `GeoCoordModal.js`
- `GeoCoordSelector.js`
- `MapV2.js`
- `PointsCluster.js`
- `amapUIHelper.js`

`germany/` 当前文件：

- `AspectToMidpoint.js`
- `AstroGermany.js`
- `AstroMidpoint.js`
- `Midpoint.js`
- `MidpointMain.js`

这三组对应地图、ACG、德国学派中点等专门模块。

#### 2.3.26 `components/calendar/` 与 `components/jieqi/`

`calendar/` 当前文件：

- `CalendarMain.js`
- `NongLi.js`
- `NongLiDate.js`
- `NongLiMain.js`

`jieqi/` 当前文件：

- `JieQiChart.js`
- `JieQiChartsMain.js`

#### 2.3.27 `components/gua/` 与 `components/guazhan/`

`gua/` 当前文件：

- `DoubleMeiyiGuaSym.js`
- `Gua.js`
- `Gua3.js`
- `GuaChart.js`
- `GuaChartDiv.js`
- `GuaConst.js`
- `GuaSym.js`
- `GuaSymDesc.js`
- `MeiyiGuaSym.js`
- `YangYao.js`
- `Yao.js`
- `YinYao.js`

`guazhan/` 当前文件：

- `GZChart.js`
- `GuaDesc.js`
- `GuaZhanChart.js`
- `GuaZhanInput.js`
- `GuaZhanMain.js`

#### 2.3.28 `components/guolao/`

当前文件：

- `GLChart.js`
- `GLSZSignChart.js`
- `GuoLaoChart.js`
- `GuoLaoChartMain.js`
- `GuoLaoInput.js`
- `GuoLaoNatalChart.js`

#### 2.3.29 `components/su28/` 与 `components/suzhan/`

`su28/` 当前文件非常细，包含：

- `HouseSu.js`
- `HouseSu0.js` 到 `HouseSu27.js`
- `HouseSuCenter.js`
- `Su28Chart.js`
- `Su28ChartCircle.js`
- `Su28Helper.js`

`suzhan/` 当前文件：

- `SZChart.js`
- `SZChartComm.js`
- `SZConst.js`
- `SuZhanChart.js`
- `SuZhanInput.js`
- `SuZhanMain.js`

#### 2.3.30 `components/sz*` 系列

这些目录是三式相关子盘组件：

- `szbagua/`
  - `SZBaGuaChart.js`
  - `SZBaGuaChartCircle.js`
- `szdunjia/`
  - `SZDunJiaChart.js`
  - `SZDunJiaChartCircle.js`
- `szfangwei/`
  - `SZFangWeiChart.js`
  - `SZFangWeiChartCircle.js`
- `szfengye/`
  - `SZFengYeChart.js`
  - `SZFengYeChartCircle.js`
- `sznixiang/`
  - `SZNiXiangChart.js`
  - `SZNiXiangChartCircle.js`
- `szsign/`
  - `SZSignChart.js`
  - `SZSignChartCircle.js`
- `sztaiyi/`
  - `SZTaiYiChart.js`
  - `SZTaiYiChartCircle.js`

#### 2.3.31 其他前端组件目录

- `admintools/`
  - `AdminToolsMain.js`
  - `BackupTool.js`
- `commtools/`
  - `Azimuth.js`
  - `BaziPattern.js`
  - `BaziPithy.js`
  - `Calculator.js`
  - `CommToolsMain.js`
  - `CoordTrans.js`
  - `CuanGong12.js`
  - `CuanGong12Desc.js`
  - `CuanGong12Query.js`
  - `DateCalc.js`
  - `InverseBazi.js`
  - `NaYing.js`
- `comp/`
  - `ChartFormData.js`
  - `ChartMemo.js`
  - `CompHelper.js`
  - `ConfirmSwitch.js`
  - `DateTime.js`
  - `DateTimeInfo.js`
  - `DateTimeSelector.js`
  - `EditableTags.js`
  - `ImgToken.js`
  - `TipsBoard.js`
- `deeplearn/`
  - `DLFeature.js`
  - `DLStatis.js`
- `dice/`
  - `DiceMain.js`
- `direction/`
  - `AstroDirectMain.js`
- `fengshui/`
  - `FengShuiMain.js`
- `graph/`
  - `D3Arrow.js`
  - `D3BaseCircle.js`
  - `D3Circle.js`
  - `D3DegreeInnerLine.js`
  - `D3DegreeOuterLine.js`
  - `GraphHelper.js`
  - `TextTable.js`
- `hellenastro/`
  - `AstroChart13.js`
  - `HellenAstroMain.js`
- `homepage/`
  - `PageFooter.js`
  - `PageHeader.js`
- `loc/`
  - `LocAstroMain.js`
- `logqry/`
  - `LogQryDetail.js`
  - `LogQryList.js`
  - `LogQryMain.js`
- `multimedia/`
  - `LiveMgmt.js`
  - `LivePlayer.js`
  - `LiveStreamsModal.js`
  - `MediaMain.js`
  - `MediaPlayer.js`
  - `RtspPlayer.js`
  - `StreamPlayer.js`
- `otherbu/`
  - `OtherBuMain.js`
- `reader/`
  - `BookList.js`
  - `BookMain.js`
  - `BookReader.js`
  - `BookUpload.js`
  - `MyBookList.js`
  - `ReaderTTS.js`
- `statis/`
  - `Statis.js`
- `user/`
  - `CaseAddFormComp.js`
  - `CaseData.js`
  - `CaseEditFormComp.js`
  - `CaseList.js`
  - `ChangeParamsFormComp.js`
  - `ChangePwdForm.js`
  - `ChartAddFormComp.js`
  - `ChartData.js`
  - `ChartEditFormComp.js`
  - `ChartList.js`
  - `ChartsGps.js`
  - `LoginForm.js`
  - `RegisterForm.js`
  - `ResetPwdForm.js`
  - `UploadChartsModal.js`
  - `UserMgmt.js`

补充几个承担“组合页入口”的组件：

- `direction/AstroDirectMain.js`
  当前把“推运盘”拆成 10 个二级 Tab：
  - `primarydirect`：主/界限法
  - `primarydirchart`：主限法盘
  - `zodialrelease`：黄道星释
  - `firdaria`：法达星限
  - `profection`：小限法
  - `solararc`：太阳弧
  - `solarreturn`：太阳返照
  - `lunarreturn`：月亮返照
  - `givenyear`：流年法
  - `decennials`：十年大运
- `cnyibu/CnYiBuMain.js`
  当前把“易与三式”拆成 7 个二级 Tab：
  - `suzhan`：宿盘
  - `guazhan`：易卦
  - `liureng`：六壬
  - `jinkou`：金口诀
  - `dunjia`：遁甲
  - `taiyi`：太乙
  - `tongshefa`：统摄法
- `otherbu/OtherBuMain.js`
  当前可见二级页只有：
  - `touzi`：星盘骰子
- `sanshi/SanShiUnitedMain.js`
  当前把“三式合一”拆成一级 Tab：
  - `overview`：概览
  - `taiyi`：太乙
  - `shensha`：神煞
  - `liureng`：六壬
  - `bagong`：八宫
  其中 `liureng` 页内部又有第二层 Tab：
  - `dage`：大格
  - `xiaoju`：小局
  - `reference`：参考
  - `overview`：概览

`homepage/PageHeader.js` 不是简单 logo 条，而是前端顶层工作台控制条，当前实际负责：

- 菜单点击分发
- 主题切换
- AI 导出
- AI 导出设置弹窗
- 新命盘
- 打开各类抽屉
- 若存在桌面桥，还可触发 diagnostics 导出

从当前 JSX 看，顶部工具条直接暴露的按钮/入口包括：

- `公众号`
- `首页`
- `批注`
- 主题选择器
- `小工具`
- `星盘组件`
- `行星选择`
- `相位选择`
- `新命盘`
- `AI导出`
- `AI导出设置`
- `导出诊断报告`（仅桌面桥可用）
- 查询图标入口
- 右上角用户/管理下拉菜单

右上角用户菜单当前分两套：

- 未登录/管理态：
  - `chartlist`
  - `caselist`
  - `chartadd`
- 已登录用户态：
  - `chartlist`
  - `caselist`
  - `chartsgps`
  - `chartadd`
  - `changeparams`
  - `changepwd`
  - `logout`

`app/menuClick` 的当前行为也很直接：

- 如果 key 是 `logout`，走 `app/logout`
- 其他 key 一律转给 `astro/openDrawer`

把 `PageHeader` 再拆细一层，可以得到一张“顶栏入口 -> dispatch -> drawer/动作”映射：

- `首页`
  - 触发：`openDrawer('homepage')`
  - 结果：打开首页设置/首页入口抽屉
- `小工具`
  - 触发：`openDrawer('commtools')`
  - 结果：打开小工具抽屉
- `星盘组件`
  - 触发：`openDrawer('selectchartdisplay')`
  - 结果：打开图面显示选择抽屉
- `行星选择`
  - 触发：`openDrawer('selectplanet')`
  - 结果：打开行星显示抽屉
- `相位选择`
  - 触发：`openDrawer('selectasp')`
  - 结果：打开相位选择抽屉
- `新命盘`
  - 触发：`astro/nowChart`
  - 结果：直接生成当前时刻命盘，不走 drawer
- `AI导出`
  - 触发：`runAIExport(key)`
  - 结果：走 `utils/aiExport.js` 导出链路
- `AI导出设置`
  - 触发：`openAIExportSettings()`
  - 结果：弹出 AI 导出 section 配置 Modal
- `导出诊断报告`
  - 条件：`window.horosaDesktop.exportDiagnostics` 可用
  - 结果：收集当前 URL、UA、AI 快照、本地模块快照后交给桌面壳导出
- 查询图标
  - 触发：`openDrawer('query')`
  - 结果：打开查询抽屉
- 用户下拉菜单各 key
  - `chartlist / caselist / chartsgps / chartadd / changeparams / changepwd`
  - 统一经 `app/menuClick` 再转到 `astro/openDrawer`
  - `logout`
    - 单独走 `app/logout`

因此 `PageHeader.js` 实际上已经是一个“全局命令面板”，不是单纯的视觉顶栏。

### 2.4 Java 后端：`Horosa-Web/astrostudysrv/`

这是 Maven 多模块工程。当前可见的模块有：

- `astrodeeplearn/`
- `astroesp/`
- `astroreader/`
- `astrostudy/`
- `astrostudyboot/`
- `astrostudycn/`
- `astrostudytest/`
- `astroswisseph/`
- `basecomm/`
- `boundless/`
- `image/`
- `iot/`
- `media/`
- `medialib/`

每个模块目前基本都带有 `pom.xml`，多数还带 `src/`、`target/`、`.settings/`。

按 `src/` 下文件数量粗看，当前重量级模块大致是：

- `boundless/`：约 540 个文件
- `astrostudycn/`：约 130 个文件
- `astrostudy/`：约 86 个文件
- `astrostudyboot/`：约 56 个文件
- `basecomm/`：约 41 个文件
- `iot/`：约 34 个文件
- `astrostudytest/`：约 34 个文件
- `image/`：约 22 个文件

这也说明后端真正的核心并不只是一层 controller，而是：

- `astrostudy + astrostudycn`
  承担业务逻辑
- `astrostudyboot`
  承担启动与装配
- `basecomm + boundless`
  承担公共基础能力
- `image/iot/media`
  作为历史能力与扩展能力保留在工程里

#### 2.4.1 `astrostudyboot/`

- `astrostudyboot/pom.xml`
- `astrostudyboot/src/main/java/spacex/astrostudyboot/AstroStudyProgram.java`

这是整个 Java 服务的启动入口模块。

补充：

- 从目录规模看，`astrostudyboot` 不是单文件壳模块，它本身在 `src/` 下约有 56 个文件，说明里面除了启动入口，应该还承载了较多资源、配置或装配逻辑。

#### 2.4.2 `astrostudy/`

这是西占与通用业务主模块。当前从源码上能直接看到的主要层次有：

- `constants/`
  - `AstroObjects.java`
  - `AstroPrivilege.java`
  - `ClientApp.java`
  - `FiveElement.java`
  - `MemoType.java`
  - `Phase.java`
  - `PhaseType.java`
  - `Polarity.java`
  - `StemBranch.java`
  - `ganjizi.json`
  - `ganzipos.json`
- `controller/`
  - `AcgController.java`
  - `AllowedChartController.java`
  - `BackupMgmtController.java`
  - `CalcController.java`
  - `CommController.java`
  - `GermanyTechController.java`
  - `IndiaChartController.java`
  - `JdnController.java`
  - `LoginController.java`
  - `ModernChartController.java`
  - `PredictiveController.java`
  - `RegisterController.java`
  - `ResetPwdController.java`
  - `StatisticController.java`
  - `ThirdAppClientController.java`
  - `TokenController.java`
  - `TransLogController.java`
  - `UserChartsController.java`
  - `UserCheckLoginController.java`
  - `UserDataTransferController.java`
  - `UserInfoController.java`
  - `UserMgmtController.java`
- `helper/`
  - `AstroCacheHelper.java`
  - `AstroHelper.java`
  - `BaZiHelper.java`
  - `BaZiPithyHelper.java`
  - `CacheHelper.java`
  - `ClientAppHelper.java`
  - `GanZiRelativeHelper.java`
  - `GodsHelper.java`
  - `Gong12Helper.java`
  - `JdnHelper.java`
  - `JieqiChef.json`
  - `MongoTransLogTask.java`
  - `NongliHelper.java`
  - `ParamHashCacheHelper.java`
  - `PrivilegeHelper.java`
  - `QiMengHelper.java`
  - `ReqCheckRsaHelper.java`
  - `ReqSignHelper.java`
  - `RsaParamHelper.java`
  - `StatisticHelper.java`
  - `TiaoHouHelper.java`
  - `TransGroupHelper.java`
  - `WuXingPhaseHelper.java`
  - `bazipithy.json`
  - `ganzirelative.json`
  - `gods.json`
  - `gong12.json`
  - `gong12Su.json`
  - `taisui.json`
  - `tiaohou.json`
  - `wuxingphase.json`
  - `五行精纪.json`
  - `predict/PlanetSignPredictHelper.java`
- `interceptor/`
  - `CommInterceptor.java`
  - `PermissionInterceptor.java`
  - `UserTokenInterceptor.java`
- `model/`
  - `AstroChart.java`
  - `AstroUser.java`
  - `FourColumns.java`
  - `GanZi.java`
  - `GanZiCell.java`
  - `NongLi.java`
  - `RealSunTimeOffset.java`
  - `godrule/GodRule.java`
  - `godrule/GodRuleByJiaZi.java`
  - `godrule/GodRuleByNaYing.java`
  - `godrule/GodRuleByPhase.java`
  - `godrule/GodRuleByRiZhu.java`
  - `godrule/GuoLaoGods.java`
  - `godrule/GuoLaoZiGods.java`
- `service/`
  - `UserService.java`

路由域从 controller 上看，`astrostudy` 这层主要承接以下 URL 空间：

- `/location/*`
  ACG / 地理相关
- `/common/*`
  token、公共工具、清缓存等
- `/germany/*`
  德国学派 / midpoint
- `/clientapp/*`
  第三方 client app 管理
- `/jdn/*`
  JDN 工具
- `/user/*`
  登录、登出、用户检查、命盘、导入导出、参数修改
- `/usermgmt/*`
  后台用户管理
- `/predict/*`
  推运与主限法
- `/allowedcharts`
- `/statis/*`
- `/modern/*`
- `/calc/*`
- `/bak/*`
- `/log/*`
- `/india/*`

其中和当前前端直接强相关的，主要是：

- `/user/*`
- `/predict/*`
- `/calc/*`
- `/common/*`
- `/statis/*`
- `/allowedcharts`
- `/modern/relative`
- `/location/acg`
- `/germany/midpoint`
- `/india/chart`

#### 2.4.3 `astrostudycn/`

这是中式术数后端主模块。当前可见的主要层次：

- `constants/`
  - `BaZiGender.java`
  - `BaziPattern.java`
  - `TimeZiAlg.java`
  - `YueJiangType.java`
  - `ZiWeiStarType.java`
- `controller/`
  - `BaZiBirthController.java`
  - `BaZiPatternController.java`
  - `CalendarController.java`
  - `ChartController.java`
  - `GuaController.java`
  - `JieQiController.java`
  - `LiuRengController.java`
  - `NongliController.java`
  - `PaiBaZiController.java`
  - `QueryChartController.java`
  - `ZiWeiController.java`
- `helper/`
  - `BaZiComposeHelper.java`
  - `BaZiPredictHelper.java`
  - `CalendarHelper.java`
  - `GuaHelper.java`
  - `JieQiHelper.java`
  - `LiuRengHelper.java`
  - `SeasonHelper.java`
  - `YueJiangHelper.java`
  - `ZWRulesHelper.java`
  - `ZiWeiHelper.java`
  - `bazicompose.json`
  - `bazipred.json`
  - `gua.json`
  - `liureng.json`
  - `nayin.json`
  - `nayinsym.json`
  - `season.json`
  - `yuejiang.json`
  - `ziweidou.json`
  - `ziweihuolin.json`
  - `ziweijiang.json`
  - `ziweimonth.json`
  - `ziweisihua.json`
  - `ziweismallstars.json`
  - `ziweistarlight.json`
  - `ziweistarsmain.json`
  - `ziweitimezi.json`
  - `ziweixiaoxian.json`
  - `ziweiyeargan.json`
  - `ziweiyearzi.json`
  - `ziweizu.json`
  - `zwrules.json`
  - `zwrulesihua.json`
- `model/`
  - `BaZi.java`
  - `BaZiDirect.java`
  - `FateDirect.java`
  - `LiuReng.java`
  - `OnlyFourColumns.java`
  - `SmallFateDirect.java`
  - `ZiWeiChart.java`
  - `ZiWeiHouse.java`
  - `ZiWeiStar.java`

路由域从 controller 上看，`astrostudycn` 主要承接：

- `/chart`
- `/chart13`
- `/bazi/*`
- `/calendar/*`
- `/gua/*`
- `/jieqi/*`
- `/liureng/*`
- `/nongli/*`
- `/qry/*`
- `/ziwei/*`

其中对应当前前端的重点关系是：

- 星盘主页面：`/chart`、`/chart13`
- 八字紫微：`/bazi/*`、`/ziwei/*`
- 节气盘与万年历：`/jieqi/*`、`/calendar/*`、`/nongli/*`
- 易卦与六壬：`/gua/*`、`/liureng/*`

#### 2.4.4 `astrodeeplearn/`

当前可见内容：

- `controller/DeepLearnController.java`
- `controller/StatisDeepLearnController.java`
- `helper/DeepLearnHelper.java`
- `helper/10000.json`
- `helper/20000.json`
- `helper/30000.json`
- `helper/40000.json`

#### 2.4.5 `astroreader/`

当前可见内容：

- `controller/FlvUrlController.java`
- `controller/MediaController.java`
- `controller/ReaderController.java`
- `controller/RtmpController.java`
- `controller/TTSController.java`
- `helper/FlvUrlHelper.java`
- `helper/ReaderHelper.java`
- `helper/RtmpHelper.java`

这部分和阅读器、媒体、流媒体/TTS 有关。

对应路由域：

- `/astroreader/*`
  图书上传、列书、章节、TTS、直播地址等
- `/astromedia`
- `/live/*`

#### 2.4.6 `astroesp/`

当前可见内容：

- `controller/DoorLockController.java`

#### 2.4.7 `astrostudytest/`

这是 Java 侧测试/工具模块，当前可见文件：

- `AstroStudyTest.java`
- `BaziBirthTest.java`
- `ChartsGpsTest.java`
- `ClearQueryCache.java`
- `DoorTest.java`
- `HostIdTest.java`
- `HttpClientTest.java`
- `JieqiYearTest.java`
- `MemoTest.java`
- `QryChartTest.java`
- `ReaderTest.java`
- `RtspPushTest.java`
- `TSSTest.java`
- `ZiWeiChartTest.java`

#### 2.4.8 `basecomm/`

这是公共基础通信/鉴权/WebSocket 支撑模块。当前可见内容包括：

- `constants/`
  - `AlertTag.java`
  - `AlertType.java`
  - `ClientApp.java`
  - `ClientChannel.java`
  - `ControlTag.java`
  - `CustomerState.java`
  - `CustomerType.java`
  - `DataSourceType.java`
  - `ErrorMetrics.java`
  - `FieldBusProtocol.java`
  - `FuncTrans.java`
  - `IotTag.java`
  - `RegisterType.java`
  - `SexType.java`
  - `TransGroup.java`
  - `TransLogField.java`
  - `UserState.java`
- `controller/`
  - `AuthController.java`
  - `SystemController.java`
- `helper/`
  - `CustConfHelper.java`
  - `CypherHelper.java`
  - `HttpHelper.java`
  - `IotDataTreatHelper.java`
  - `MqttHelper.java`
  - `NotificationHelper.java`
- `im/`
  - `IMAccount.java`
  - `TLSSigAPIv2.java`
  - `TengXunErrCode.json`
  - `TengXunIM.java`
  - `ThirdPartIM.java`
  - `WangYiErrCode.json`
  - `WangYiIM.java`
- `interceptor/RootFilter.java`
- `model/`
  - `AppInfo.java`
  - `BaiduIotConfig.java`
  - `BemCloudConfig.java`
  - `FieldBus.java`
  - `MqttConfig.java`
- `ws/`
  - `command/WebSocketCmd.java`
  - `packet/WebSocketPacketIds.java`
  - `process/WebSocketDatagramCommProcess.java`

对应路由域：

- `/auth/*`
- `/common/time`
- `/common/tm`
- `/common/tmdetail`
- `/common/hostid`
- `/common/hid`
- `/common/hidmd5`
- `/common/ver`
- `/common/prevmonth`

#### 2.4.9 `boundless/`

这是更底层的公共库模块。当前直接可见的代表性内容有：

- `META-INF/MANIFEST.MF`
- `META-INF/ace-tags.tld`
- `META-INF/bwu-tags.tld`
- `META-INF/services/org.web3j.abi.spi.FunctionReturnDecoderProvider`
- `META-INF/spring-devtools.properties`
- `boundless/annotation/Comp.java`

#### 2.4.10 `image/`

图像处理模块。当前可见内容：

- `boundless/utility/img/CustomOpenCV.java`
- `boundless/utility/img/GMUtility.java`
- `boundless/utility/img/GifImage.java`
- `boundless/utility/img/GifUtility.java`
- `boundless/utility/img/ImageFilter.java`
- `boundless/utility/img/ImageFrame.java`
- `boundless/utility/img/ImageUtility.java`
- `boundless/utility/img/JPGUtility.java`
- `boundless/utility/img/PNGUtility.java`
- `boundless/utility/img/PngOptimization.java`
- `boundless/utility/img/ZipImgUtility.java`
- `boundless/web/help/ImageTokenGenerator.java`
- `org/pngquant/Image.java`
- `org/pngquant/LiqObject.java`
- `org/pngquant/PngQuant.java`
- `org/pngquant/PngQuantException.java`
- `org/pngquant/Result.java`
- `org/pngquant/libimagequant.a`
- `org/pngquant/libimagequant.jnilib`
- `spacex/basecomm/controller/ImageTestController.java`

#### 2.4.11 `iot/`

IoT/串口/现场总线相关模块。当前可见内容：

- `boundless/net/bacnet/BacnetCollector.java`
- `boundless/net/bacnet/BacnetLocalDeviceFactory.java`
- `boundless/net/bacnet/DefaultDeviceEventAdapter.java`
- `boundless/net/modbus/ModbusCollector.java`
- `boundless/net/opc/OpcCollector.java`
- `boundless/net/opc/OpcItem.java`
- `boundless/net/opcua/OpcUaCollector.java`
- `boundless/rxtx/SerialParameter.java`
- `boundless/rxtx/SerialUtility.java`
- `boundless/types/message/SmsAt.java`
- `gnu/io/*`
  这里包含一整套 RXTX 串口相关 Java 类和多平台动态库：
  - `CommDriver.java`
  - `CommPort.java`
  - `CommPortIdentifier.java`
  - `RXTXPort.java`
  - `SerialPort.java`
  - `librxtxSerial-amd64.dll`
  - `librxtxSerial-amd64.so`
  - `librxtxSerial-x86_64.jnilib`
  等
- `name/prokop/bart/rxtx/*`
- `spacex/basecomm/controller/IotTestController.java`

#### 2.4.12 `media/`

媒体模块当前可见内容：

- `boundless/utility/sound/SoundUtility.java`
- `spacex/basecomm/controller/XunFeiController.java`
- `spacex/basecomm/helper/XunFeiHelper.java`

#### 2.4.13 其余模块

- `astroswisseph/`
  当前看到 `pom.xml`，说明它作为依赖/桥接模块保留在工程中。
- `medialib/`
  当前看到 `pom.xml`，作为媒体库模块存在。

从职责上看，Java 后端当前可以粗分成 5 层：

1. 启动层：
   `astrostudyboot`
2. 西占与通用业务层：
   `astrostudy`
3. 中式术数业务层：
   `astrostudycn`
4. 阅读/深度学习/媒体扩展层：
   `astroreader`、`astrodeeplearn`、`astroesp`、`image`、`media`
5. 公共基础层：
   `basecomm`、`boundless`、`iot`

### 2.5 Python 图表与算法服务：`Horosa-Web/astropy/`

#### 2.5.1 顶层内容

当前顶层文件：

- `.gitignore`
- `README.md`
- `__init__.py`
- `requirements.txt`
- `setup.py`
- `astrostudy/`
- `websrv/`

#### 2.5.2 `astropy/astrostudy/`

这是算法主体，当前实际可见的主要文件包括：

- `firdaria.py`
- `helper.py`
- `perchart.py`
- `perpredict.py`
- `signasctime.py`
- `solararc.py`
- `termdirection.py`
- `thirteenthchart.py`
- `zreleasing.py`

子目录：

- `acg/`
  - `ACGraph.py`
- `germany/`
  - `midpoint.py`
- `guostarsect/`
  - `guo74.py`
  - `guostarsect.py`
  - `guotables.py`
- `india/`
  - `chart2.py`
  - `chart3.py`
  - `chart4.py`
  - `chart5.py`
  - `chart6.py`
  - `chart7.py`
  - `chart8.py`
  - `chart9.py`
  - `chart10.py`
  - `chart11.py`
  - `chart12.py`
  - `chart16.py`
  - `chart20.py`
  - `chart24.py`
  - `chart27.py`
  - `chart30.py`
  - `chart40.py`
  - `chart45.py`
  - `chart60.py`
- `jieqi/`
  - `BirthJieQi.py`
  - `NongLi.py`
  - `TimeDecider.py`
  - `YearJieQi.py`
  - `jieqiconst.py`
  - `realsuntime.py`
- `modern/`
  - `chartcomp.py`
  - `chartcomposite.py`
  - `chartmarks.py`
  - `chartsynastry.py`
  - `charttmspace.py`
- `models/`
  当前保留多组主限法相关模型文件：
  - `astroapp_pd_asc_case_corr_et_v1.joblib`
  - `astroapp_pd_asc_case_corr_et_v1.json`
  - `astroapp_pd_virtual_body_corr_sun_v1.joblib`
  - `astroapp_pd_virtual_body_corr_moon_v1.joblib`
  - `astroapp_pd_virtual_body_corr_mercury_v1.joblib`
  - `astroapp_pd_virtual_body_corr_venus_v1.joblib`
  - `astroapp_pd_virtual_body_corr_mars_v1.joblib`
  - `astroapp_pd_virtual_body_corr_jupiter_v1.joblib`
  - `astroapp_pd_virtual_body_corr_saturn_v1.joblib`
  - `astroapp_pd_virtual_body_corr_uranus_v1.joblib`
  - `astroapp_pd_virtual_body_corr_neptune_v1.joblib`
  - `astroapp_pd_virtual_body_corr_pluto_v1.joblib`

#### 2.5.3 `astropy/websrv/`

这是 Python 服务接口层。当前实际文件：

- `helper.py`
- `webacgsrv.py`
- `webcalc.py`
- `webchartsrv.py`
- `webgermanysrv.py`
- `webindiasrv.py`
- `webjdn.py`
- `webjieqisrv.py`
- `webmodernsrv.py`
- `webpredictsrv.py`

这里的核心角色基本是：

- 图表服务入口
- 推运/主限法服务入口
- 节气与历法服务入口
- ACG、德国学派、现代关系盘等专门服务入口

更细一点看：

- `webchartsrv.py`
  星盘图表主服务入口。
- `webpredictsrv.py`
  推运/主限法相关服务入口。
- `webjieqisrv.py`
  节气与历法服务。
- `webacgsrv.py`
  ACG 服务。
- `webgermanysrv.py`
  德国学派/量化盘服务。
- `webindiasrv.py`
  印度律盘服务。
- `webmodernsrv.py`
  现代关系盘服务。
- `webjdn.py`
  JDN/历法辅助接口。
- `webcalc.py`
  计算辅助入口。

按文件数量看：

- `astropy/astrostudy/` 约有 112 个文件
- `astropy/websrv/` 约有 22 个文件

更关键的是，`webchartsrv.py` 当前已经清楚写出了 CherryPy 挂载关系：

- `/` -> `WebChartSrv()`
- `/predict` -> `PredictSrv()`
- `/india` -> `IndiaAstroSrv()`
- `/modern` -> `ModernAstroSrv()`
- `/germany` -> `GermanyAstroSrv()`
- `/jieqi` -> `JieQiSrv()`
- `/jdn` -> `WebJdnSrv()`
- `/calc` -> `WebCalcSrv()`
- `/location` -> `AcgSrv()`

这和 Java 侧的 URL 空间是有明显镜像关系的，也解释了为什么前端会同时命中 Python 图表服务和 Java 后端。

从暴露方法看，各 Python 服务对象当前至少提供：

- `WebChartSrv`
  - `index`
  - `chart13`
- `PredictSrv`
  - `solarreturn`
  - `lunarreturn`
  - `givenyear`
  - `profection`
  - `solararc`
  - `pd`
  - `pdchart`
  - `td`
  - `zr`
  - `dice`
- `IndiaAstroSrv`
  - `chart`
- `ModernAstroSrv`
  - `relative`
- `GermanyAstroSrv`
  - `midpoint`
- `JieQiSrv`
  - `year`
  - `birth`
  - `nongli`
- `WebJdnSrv`
  - `num`
  - `date`
- `WebCalcSrv`
  - `azimuth`
  - `cotrans`
- `AcgSrv`
  - `acg`

`webchartsrv.py` 还额外承担了几个关键职责：

- 启动时做主限法 warmup
- 把 `flatlib-ctrad2` 加进 `sys.path`
- 统一设置跨域响应
- 从环境变量 `HOROSA_CHART_PORT` 读取端口，默认 `8899`

### 2.6 内置 Python 占星依赖：`Horosa-Web/flatlib-ctrad2/`

顶层当前可见内容：

- `.gitignore`
- `LICENSE`
- `MANIFEST.in`
- `README.md`
- `README.rst`
- `contrib/`
- `flatlib/`
- `recipes/`
- `requirements.txt`
- `scripts/`
- `setup.py`
- `tests/`

重点内容：

- `contrib/topical_almuten.py`
- `flatlib/`
  当前可见核心文件和子目录：
  - `angle.py`
  - `aspects.py`
  - `chart.py`
  - `const.py`
  - `datetime.py`
  - `geopos.py`
  - `lists.py`
  - `object.py`
  - `props.py`
  - `utils.py`
  - `dignities/`
  - `ephem/`
  - `predictives/`
  - `protocols/`
  - `resources/`
  - `tools/`
- `recipes/`
  包含大量推运/占星配方脚本：
  - `primarydirections.py`
  - `profections.py`
  - `solarreturn.py`
  - `solaryears.py`
  - `temperament.py`
  - `arabicparts.py`
  - `accidentaldignities.py`
  等
- `scripts/`
  - `build.py`
  - `clean.py`
  - `utils.py`
- `tests/`
  - `test_angles.py`
  - `test_chart.py`
  - `testchart.py`

### 2.7 主工程内脚本与运行痕迹

#### 2.7.1 主工程根脚本

- `start_horosa_local.sh`
  本地启动入口。
- `stop_horosa_local.sh`
  本地停止入口。
- `verify_horosa_local.sh`
  主工程内总自检入口。
- `scripts/repairEmbeddedPythonRuntime.py`
  修复嵌入式 Python runtime。

补充职责：

- `start_horosa_local.sh`
  当前负责：
  - 创建本地日志目录
  - 选择 Python/Java 可执行文件
  - 检查并清理陈旧 PID 文件
  - 启动 Python 图表服务与 Java 后端
  - 预热 runtime 路由
  - 必要时修复 embedded Python runtime
- `verify_horosa_local.sh`
  当前负责串起：
  - 前端 `node .tmp_horosa_verify.js`
  - 前端主限法 runtime 校验
  - 前端性能校验
  - 前端全量 runtime 校验
  - Python 主限法集成校验
  - Python 全量集成校验
  - 多个 Playwright 浏览器验收脚本

这两个脚本当前的默认端口约定是：

- 图表服务：`8899`
- Java 后端：`9999`
- 前端静态页：`8000`

相关环境变量包括：

- `HOROSA_CHART_PORT`
- `HOROSA_SERVER_PORT`
- `HOROSA_WEB_PORT`
- `HOROSA_SERVER_ROOT`
- `HOROSA_SKIP_UI_BUILD`
- `HOROSA_SKIP_RUNTIME_WARMUP`
- `HOROSA_STARTUP_TIMEOUT`

#### 2.7.2 主工程内部运行痕迹

- `.horosa-local-logs/`
  当前已有多次启动记录：
  - `20260317_151149/`
  - `20260317_153406/`
  - `20260317_170446/`
  - `20260317_173218/`
  - `20260317_180903/`
  - `20260318_193109/`
  - `20260323_172308/`

每个日志目录当前都能看到：

- `astropy.log`
- `astrostudyboot.log`
- `runtime-warmup.log`

- `.horosa-cache/paramhash/`
  主工程内部参数哈希缓存。
- `.horosa_java.pid`
- `.horosa_py.pid`
- `.horosa_web.pid`
  本地服务 PID 文件。
- `.horosa-browser-profile/`
  浏览器自动化 profile。
- `${env:HOME}/.horosa-logs/astrostudyboot/2026/`
  当前仓库内还存在一个 `${env:HOME}` 字面目录，里面保留了日志路径痕迹，属于运行期遗留结构。

## 3. macOS 桌面安装器：`Horosa_Desktop_Installer/`

这是独立于主业务工程的桌面分发工程。

### 3.1 顶层内容

当前一级条目包括：

- `README.md`
- `assets/`
- `build/`
- `config/`
- `dist/`
- `distribution-support/`
- `installer-scripts/`
- `node_modules/`
- `package-lock.json`
- `package.json`
- `scripts/`
- `src-tauri/`
- `web/`

其中 `package.json` 当前版本为 `1.1.7`。

### 3.2 `src-tauri/`

当前可见内容：

- `Cargo.lock`
- `Cargo.toml`
- `build.rs`
- `gen/`
- `icons/`
- `src/`
- `target/`
- `target-user/`
- `tauri.conf.json`

关键入口：

- `src-tauri/src/main.rs`
  当前桌面壳唯一 Rust 主入口。

补充：

- `src-tauri/icons/` 当前实际包含：
  - `icon.png`
  - `icon-1024.png`
  - `icon.icns`
  - `Horosa.iconset/`
    - `icon_16x16.png`
    - `icon_16x16@2x.png`
    - `icon_32x32.png`
    - `icon_32x32@2x.png`
    - `icon_128x128.png`
    - `icon_128x128@2x.png`
    - `icon_256x256.png`
    - `icon_256x256@2x.png`
    - `icon_512x512.png`
    - `icon_512x512@2x.png`
- `src-tauri/gen/schemas/` 当前包含：
  - `acl-manifests.json`
  - `capabilities.json`
  - `desktop-schema.json`
  - `macOS-schema.json`

从 `main.rs` 的常量、结构体和状态定义来看，桌面壳当前集中承载：

- 主窗口、设置窗口、诊断窗口
- 菜单命令与缩放控制
- runtime 路径与运行会话管理
- 本地 frontend/backend 端口管理
- Release 配置、更新清单、GitHub Release API 解析
- 应用更新与 runtime 更新事务
- 安装来源识别
- 启动页状态机、修复态、离线重装态
- 偏好设置与窗口状态持久化

当前窗口标签是：

- `main`
- `preferences`
- `diagnostics`

当前 launcher 状态枚举是：

- `LaunchReady`
- `OfflineReady`
- `OfflineReview`
- `OfflineRepairRequired`
- `RepairInProgress`
- `UpdateReview`
- `UpdateInProgress`

当前恢复类型枚举是：

- `OfflineReinstallRequired`
- `RepairAvailable`
- `GenericFailure`

当前 launcher 动作枚举是：

- `ReinstallOfflinePackage`
- `OpenDiagnostics`
- `RevealData`
- `RevealRuntime`

当前菜单命令 id 包括：

- `check_updates`
- `reinstall_runtime`
- `open_preferences`
- `show_main_window`
- `show_diagnostics`
- `open_logs`
- `open_data`
- `open_runtime`
- `reload_main`
- `open_releases`
- `zoom_in`
- `zoom_out`
- `zoom_reset`

从 `build_menu(...)` 看，当前菜单栏结构至少包括：

- App 菜单：
  - About
  - 偏好设置
  - 检查更新
  - 重装本机组件
  - services / hide / quit 等系统项
- 文件：
  - 显示主窗口
  - 诊断中心
  - 在 Finder 中显示本机组件
  - 在 Finder 中显示日志
  - 在 Finder 中显示数据目录
- 编辑：
  - undo / redo / cut / copy / paste / select all
- 视图：
  - 重新载入主界面
  - 放大
  - 缩小
  - 实际大小
  - fullscreen / maximize
- 窗口：
  - minimize / maximize / close

### 3.3 `web/`

当前文件：

- `app.js`
- `diagnostics.css`
- `diagnostics.html`
- `diagnostics.js`
- `index.html`
- `settings.css`
- `settings.html`
- `settings.js`
- `style.css`

这是桌面初始化页、诊断页、设置页对应的前端资源。

### 3.4 `config/`

当前文件：

- `release_config.json`
- `release_notes.md`

角色：

- `release_config.json`
  GitHub Release / runtime / 分发配置。
- `release_notes.md`
  发布说明正文来源。

`release_config.json` 当前的实际配置值是：

- `repoOwner`: `Horace-Maxwell`
- `repoName`: `Horosa-Web-App-comprehensively-improved-MacOS`
- `runtimeVersion`: `1.1.7-runtime1`
- `runtimeAssetName`: `horosa-runtime-macos-arm64.tar.gz`
- `desktopAssetName`: `Horosa-Desktop-macos-arm64.zip`
- `desktopPkgName`: `Horosa-Installer-macos-arm64.pkg`
- `desktopPkgZipName`: `Horosa-Installer-macos-arm64-pkg.zip`
- `desktopOfflinePkgName`: `Horosa-Installer-macos-arm64-offline.pkg`
- `desktopOfflinePkgZipName`: `Horosa-Installer-macos-arm64-offline-pkg.zip`
- `updateManifestName`: `horosa-latest.json`
- `primaryDownload`: `Horosa-Installer-macos-arm64-offline.pkg`
- `supportedArch`: `arm64`
- `releaseTagPrefix`: `v`
- `appName`: `星阙`

### 3.5 `scripts/`

当前文件：

- `ad_hoc_sign_app.sh`
- `build_desktop_release.sh`
- `check_apple_signing_prereqs.sh`
- `generate_icon.sh`
- `package_runtime_payload.sh`
- `publish_github_release.sh`
- `sign_runtime_payload.py`
- `verify_desktop_packaging.sh`
- `verify_github_release_end_to_end.sh`
- `verify_public_distribution_readiness.sh`

另外还有：

- `scripts/__pycache__/sign_runtime_payload.cpython-312.pyc`

更细一点看，当前关键脚本职责已经形成完整发布流水线：

- `build_desktop_release.sh`
  负责：
  - 读取 `package.json` 与 `config/release_config.json`
  - 检查 Developer ID / notarytool 配置
  - 生成 icon
  - 打包 runtime payload
  - 构建 Tauri app bundle
  - 渲染 offline `postinstall`
  - 生成 `.pkg`、`.zip`、`horosa-latest.json`
- `publish_github_release.sh`
  负责：
  - 校验 release 资产齐全
  - 校验 `horosa-latest.json` 中版本、URL、SHA-256 与本地产物一致
  - 拼装中英双语 release 正文
  - 上传 app/runtime/manifest 资产到 GitHub Release
- `verify_desktop_packaging.sh`
  本地桌面打包验收总入口。
- `verify_github_release_end_to_end.sh`
  公开 release 下载后的端到端验证。
- `verify_public_distribution_readiness.sh`
  面向正式外部分发的签名/公证准备检查。
- `package_runtime_payload.sh`
  运行时 bundle 打包。
- `ad_hoc_sign_app.sh`
  本地 ad-hoc 签名。
- `check_apple_signing_prereqs.sh`
  Apple 证书与 notary 前置检查。
- `generate_icon.sh`
  图标生成。
- `sign_runtime_payload.py`
  runtime 归档签名辅助。

这些脚本当前显式涉及的关键环境变量包括：

- 构建/签名链：
  - `APPLE_SIGNING_IDENTITY`
  - `APPLE_INSTALLER_IDENTITY`
  - `APPLE_ENTITLEMENTS_PATH`
  - `APPLE_SIGNING_KEYCHAIN`
  - `NOTARYTOOL_KEYCHAIN_PROFILE`
  - `HOROSA_PUBLIC_DISTRIBUTION`
- runtime 上传控制：
  - `HOROSA_FORCE_RUNTIME_UPLOAD`
- 发布校验控制：
  - `HOROSA_SKIP_VERIFY`
  - `HOROSA_REQUIRE_SIGNED_PUBLIC_RELEASE`
  - `GITHUB_TOKEN`
- 打包验收时注入到 runtime 的变量：
  - `HOROSA_CHART_PORT`
  - `HOROSA_SERVER_PORT`
  - `HOROSA_SKIP_UI_BUILD`
  - `HOROSA_SKIP_RUNTIME_WARMUP`
  - `HOROSA_STARTUP_TIMEOUT`
  - `HOROSA_PYTHON`
  - `HOROSA_JAVA_BIN`
  - `HOROSA_LOG_ROOT`
  - `HOROSA_DIAG_DIR`
  - `HOROSA_RUNTIME_URL`
  - `HOROSA_RUNTIME_SHARED_ROOT`
  - `HOROSA_APP_PATH`

### 3.6 `distribution-support/`

当前文件：

- `UNSIGNED_INSTALL_GUIDE.template`
- `unsigned_install_helper.template`

### 3.7 `installer-scripts/`

当前文件：

- `postinstall.template`

### 3.8 `assets/`

当前文件：

- `icon-base.png`
- `icon-template.svg`

### 3.9 `build/`

这是安装器构建中间产物区。当前已存在的子目录/文件包括：

- `delivery-bundle-offline/`
  - `Horosa-Installer-macos-arm64-offline.pkg`
  - `Open-XingQue-Unsigned.command`
  - `UNSIGNED_INSTALL_GUIDE.txt`
- `distribution-support-rendered-offline/`
  - `Open-XingQue-Unsigned.command`
  - `UNSIGNED_INSTALL_GUIDE.txt`
- `github-release-e2e/`
  - `app-unzip/`
  - `downloads/`
  - `release.env`
- `installer-scripts-rendered-offline/`
  - `horosa-runtime-macos-arm64.tar.gz`
  - `postinstall`
- `notary/`
  - `星阙.notary.zip`
- `pkg/`
  - `desktop-offline.component.pkg`
- `pkg-root/`
  - `Applications/`
  - `component.plist`
- `release-ui-check-v1.0.16/`
  - `target/`
- `release-ui-check-v1.0.17/`
  - `target/`
- `runtime/`
  - `runtime-payload/`

按文件数量看，`Horosa_Desktop_Installer/build/` 当前约有 3363 个文件，已经是完整的发布中间工位，而不只是简单的临时目录。

### 3.10 `dist/`

这是当前已经生成的发布产物目录。当前文件：

- `Horosa-Desktop-macos-arm64.zip`
- `Horosa-Installer-macos-arm64-offline.pkg`
- `horosa-latest.json`
- `horosa-runtime-macos-arm64.tar.gz`

`dist/` 当前虽然只有 4 个文件，但它们分别对应：

- app zip 分发包
- 离线 pkg 安装包
- 自动更新 manifest
- 独立 runtime 归档

## 4. 仓库级脚本：`scripts/`

这是超出单个子工程的仓库级自动化脚本区。

### 4.1 当前脚本总表

当前文件包括：

- `browser_horosa_final_layout_check.py`
- `browser_horosa_jinkou_regression_check.py`
- `browser_horosa_master_check.py`
- `browser_horosa_toolbar_management_check.py`
- `browser_outer_shell_scroll_check.py`
- `browser_primary_direction_chart_guangde_check.py`
- `browser_toolbar_deep_state_check.py`
- `browser_topbar_full_enumeration_check.py`
- `check_horosa_full_integration.py`
- `check_local_ephemeris_precision.py`
- `check_primary_direction_astroapp_integration.py`
- `compare_pd_backend_rows.py`
- `mac/bootstrap_and_run.sh`
- `mac/self_check_horosa.sh`
- `primary_directions_reverse/auto_collect_astroapp_pd.py`
- `repo/clean_for_github.sh`
- `requirements/mac-python.txt`
- `train_astroapp_asc_case_correction.py`
- `train_astroapp_virtual_body_corrections.py`

### 4.2 脚本分组

#### 4.2.1 启动与自检

- `mac/bootstrap_and_run.sh`
- `mac/self_check_horosa.sh`

#### 4.2.2 浏览器级验收

- `browser_horosa_master_check.py`
  主功能总巡检。
- `browser_horosa_toolbar_management_check.py`
  顶部菜单、管理、选择器深巡检。
- `browser_horosa_final_layout_check.py`
  最终布局巡检。
- `browser_horosa_jinkou_regression_check.py`
  金口诀专项回归。
- `browser_primary_direction_chart_guangde_check.py`
  主限法盘 Guangde 专项浏览器验收。
- `browser_outer_shell_scroll_check.py`
  外层壳滚动检查。
- `browser_toolbar_deep_state_check.py`
  工具栏深状态检查。
- `browser_topbar_full_enumeration_check.py`
  顶栏全枚举检查。

#### 4.2.3 主限法验证与比对

- `check_primary_direction_astroapp_integration.py`
- `compare_pd_backend_rows.py`
- `train_astroapp_asc_case_correction.py`
- `train_astroapp_virtual_body_corrections.py`
- `primary_directions_reverse/auto_collect_astroapp_pd.py`

#### 4.2.4 整体与精度检查

- `check_horosa_full_integration.py`
- `check_local_ephemeris_precision.py`

#### 4.2.5 仓库清理与依赖

- `repo/clean_for_github.sh`
- `requirements/mac-python.txt`

## 5. 本地工具入口：`tools/`

当前 `tools/` 下只看到 Mac 侧工具：

- `tools/mac/Horosa_Local.command`
- `tools/mac/Horosa_SelfCheck_Mac.command`
- `tools/mac/Prepare_Runtime_Mac.command`

对应角色分别是：

- 本地快速启动
- 本地一键自检
- 准备 Mac runtime

## 6. runtime：运行时、验证产物、主限法反推样本

这是当前仓库里“最像运行工位痕迹”的目录，内容非常实。

按文件数量粗看：

- `runtime/` 总计约 14839 个文件
- `runtime/mac/bundle/` 约 174 个文件
- `runtime/mac/java/` 约 573 个文件
- `runtime/mac/python/` 约 11845 个文件

这说明 `runtime/` 不是单纯报告目录，而是“验证报告 + 完整运行时镜像 + 主限法数据样本”的混合工作目录。

### 6.1 `runtime/` 根级文件

当前根级已存在：

- `README.md`
- `browser_ai_export_release_check.json`
- `browser_horosa_jinkou_regression_check.json`
- `browser_horosa_jinkou_regression_check.png`
- `browser_horosa_master_check.json`
- `browser_horosa_master_check.png`
- `browser_horosa_toolbar_management_check.json`
- `browser_horosa_toolbar_management_check.png`
- `browser_meaning_overlay_viewport_check.json`
- `browser_outer_shell_scroll_check.json`
- `browser_star_long_tooltip_check.json`
- `browser_star_long_tooltip_check.png`
- `browser_star_tooltip_viewport_check.json`
- `browser_star_tooltip_viewport_check.png`
- `browser_toolbar_deep_state_check.json`
- `browser_topbar_full_enumeration_check.json`
- `final_layout_master_check.json`
- `glyph_spacing_metrics.json`
- `guangde_primarydirchart_browser.png`
- `guangde_primarydirchart_browser_check.json`
- `guangde_primarydirect_browser_table.png`
- `horosa_runtime_perf_check.json`
- `layout_footer_menu_metrics.json`
- `layout_revert_metrics.json`
- `mastercheck_global_shell.png`
- `mastercheck_guolao_compact.png`
- `mastercheck_jieqi_entries.png`
- `mastercheck_sanshi_compact.png`
- `mastercheck_sanshi_std.png`
- `mastercheck_solararc_compact.png`
- `mastercheck_solararc_std.png`
- `mastercheck_suzhan_compact.png`
- `resize_layout_audit.json`
- `resize_layout_audit_postfix.json`
- `responsive_layout_audit.json`

### 6.2 `runtime/mac/`

这是桌面运行时包的落地目录。当前包含：

- `bundle/`
- `java/`
- `python/`

三者的关系是：

- `bundle/`
  Horosa 自己的前端构建产物与后端 Jar。
- `java/`
  桌面版自带 Java runtime。
- `python/`
  桌面版自带 Python runtime。

#### 6.2.1 `runtime/mac/bundle/`

当前可见内容：

- `${env:HOME}/.horosa-logs/`
- `astrostudyboot.jar`
- `dist-file/`

其中 `dist-file/` 当前已包含：

- `index.html`
- `umi.60725577.css`
- `umi.eb11ec94.js`
- `static/`
- `gltf/`
- `fengshui/`

说明：

- 这里是真正被桌面端加载的前端构建产物和后端启动 Jar 组合。

#### 6.2.2 `runtime/mac/java/`

这是打包进桌面版的 Java runtime。当前能直接看到：

- `bin/`
  包含 `java`、`jar`、`javac`、`jpackage` 等二进制。
- `conf/`
- `demo/`
- `include/`
- `jmods/`
- `legal/`
- `lib/`
- `man/`
- `DISCLAIMER`
- `Welcome.html`
- `readme.txt`
- `release`

这表明仓库里当前保留的是一套完整 JDK/JRE 级 runtime，而不是只保留最小二进制。

进一步说，这也解释了为什么 `runtime/mac/java/` 体量不小：这里不是“瘦身后的最小 Java”，而是保留了 `jmods`、`include`、`demo`、`man` 等较完整结构。

#### 6.2.3 `runtime/mac/python/`

这是打包进桌面版的 Python runtime。当前能直接看到：

- `Headers`
- `Python`
- `Resources/`
  - `English.lproj`
  - `Info.plist`
  - `Python.app`
- `_CodeSignature/`
- `bin/`
  - `python3`
  - `python3.12`
  - `pip3`
  - `idle3`
  - `pydoc3`
  等
- `etc/openssl/`
- `include/python3.12/`
- `lib/`
  - `libpython3.12.dylib`
  - `libcrypto*.dylib`
  - `libssl*.dylib`
  - `python3.12/`
  - `pkgconfig/`
  - `sqlite3.40.0/`
  - `tcl8.6/`
  - `tk8.6/`
  等
- `share/doc/`
- `share/man/`

这同样说明 `runtime/mac/python/` 保留的是一套可独立工作的 `Python.framework` 级 runtime，而不是只有一个 `python3` 可执行文件。

### 6.3 `runtime/pd_auto/`

当前可见内容：

- `debug_guangde_case/`
- `debug_guangde_run/`
- `plan_geo_current540_v1.csv`
- `run_geo_current540_v1/`

### 6.4 `runtime/pd_reverse/`

这是主限法反推与比对结果目录。当前文件：

- `browser_pd_batch_verify_500.json`
- `browser_pd_batch_verify_combined_summary.json`
- `browser_pd_batch_verify_reserve.json`
- `browser_pd_retry_failed.json`
- `browser_pd_retry_fresh_page.json`
- `debug_guangde_exact_rows.csv`
- `debug_guangde_exact_summary.json`
- `shared_core_geo_current120_v2_exact_summary.json`
- `shared_core_geo_current540_full_exact_rows.csv`
- `shared_core_geo_current540_full_exact_summary.json`
- `shared_core_geo_current540_s100_exact_rows_bodycorr.csv`
- `shared_core_geo_current540_s100_exact_summary_bodycorr.json`
- `stability_production_summary.json`
- `virtual_only_geo_current540_fullfit_summary.json`

### 6.5 `runtime/release-ai-export-downloads/`

当前文件：

- `horosa_星盘_20260312_165542.txt`
- `horosa_星盘_20260312_165544.doc`

### 6.6 `runtime/release-browser-self-check-20260311-163153/`

当前文件：

- `browser_horosa_master_check.log`
- `web.log`

### 6.7 `runtime/release_checks/`

当前可见内容：

- `browser_horosa_master_check_release.json`
- `browser_horosa_master_check_release.png`
- `final_layout_master_check_release.json`
- `v1.0.20/`

## 7. 文档与诊断

### 7.1 已移除的 `docs/`

该目录曾承载截图、发布说明和技术文档，但当前主仓库已经移除。

对应信息现在分散到：

- 根目录 `README*.md`
- `Horosa_Desktop_Installer/README.md`
- `PROJECT_STRUCTURE.md`
- GitHub Releases 页面正文

### 7.2 `diagnostics/`

当前结构：

- `.gitkeep`
- `README.md`
- `horosa-run-issues.log`

角色：

- `README.md`
  说明如何查看/使用诊断信息。
- `horosa-run-issues.log`
  桌面运行问题日志。

## 8. 扩展模块与参考工程：`modules/`

### 8.1 `modules/fengshui/naqi/`

当前内容：

- `README.md`
- `app.js`
- `index.html`
- `styles.css`
- `naqi-tauri/`

`naqi-tauri/` 当前又是一个独立的小 Tauri 工程，包含：

- `README.md`
- `package-lock.json`
- `package.json`
- `src/`
  - `app.js`
  - `index.html`
  - `styles.css`
- `src-tauri/`
  - `Cargo.lock`
  - `Cargo.toml`
  - `build.rs`
  - `gen/`
  - `icons/`
  - `src/`
  - `tauri.conf.json`

### 8.2 `modules/reference/kintaiyi-master/`

这是一个内容很多的参考工程。当前可见的关键结构：

- `.streamlit/config.toml`
- `README.md`
- `app.py`
- `cerebras_client.py`
- `chart.py`
- `config.py`
- `data.pkl`
- `disaster.md`
- `example.json`
- `example.md`
- `guji.md`
- `history.pkl`
- `historytext.py`
- `icon.jpg`
- `icon.png`
- `instruction.md`
- `jieqi.py`
- `kinliuren.py`
- `kintaiyi.py`
- `requirements.txt`
- `ruler.py`
- `system_prompts.json`
- `taiyi_life_dict.py`
- `taiyidict.py`
- `taiyimishu.py`
- `tutorial.md`
- `update.md`

此外还有两个体量很大的 SVG 资源目录：

- `kook/`
  当前包含：
  - `typan.svg`
  - `yang1.svg` 到 `yang72.svg`
  - `yin1.svg` 到 `yin72.svg`
- `tykook/`
  当前同样包含：
  - `typan.svg`
  - `yang1.svg` 到 `yang72.svg`
  - `yin1.svg` 到 `yin72.svg`

以及图片目录：

- `pic/`
  当前包含多张示意图与二维码图片。

### 8.3 `modules/reference/xuan-utils-pro-master/`

当前结构比较标准：

- `.gitignore`
- `LICENSE`
- `README.md`
- `pom.xml`
- `src/main/java/`
- `src/test/java/`

这是一个 Java 参考工具库。

### 8.4 `modules/reference/zhong-zhou-zi-wei-dou-shu-2/`

这是一个前端参考工程。当前结构：

- `.gitignore`
- `App.tsx`
- `README.md`
- `components/`
  - `Astrolabe.tsx`
  - `InputForm.tsx`
  - `PalaceCard.tsx`
  - `SettingsModal.tsx`
- `index.html`
- `index.tsx`
- `manifest.json`
- `metadata.json`
- `package.json`
- `services/`
  - `lunarService.ts`
  - `ziweiMath.ts`
- `standalone.html`
- `sw.js`
- `tsconfig.json`
- `types.ts`
- `vite.config.ts`

## 9. 主限法专门文档：`主限法推演/`

当前目录内容：

- `ASTROAPP_ALCHABITIUS_PTOLEMY_REVERSE_ENGINEERING_FULL_PROCESS.md`
- `ASTROAPP_ALCHABITIUS_PTOLEMY_REVERSE_ENGINEERING_PUBLIC_EDITION.md`
- `PRIMARY_DIRECTION_ASTROAPP_ALCHABITIUS_MATH_FLOW.md`
- `PRIMARY_DIRECTION_ASTROAPP_ALCHABITIUS_REPLICATION.md`
- `PROJECT_STRUCTURE.md`
- `README.md`
- `UPGRADE_LOG.md`
- `runtime_README.md`
- `主限法盘实现原理与算法说明.md`

这部分已经构成一个相对独立的“主限法研究文档子仓”。

## 10. 维护时最该先看的路径

### 10.1 改前端页面/交互

- `Horosa-Web/astrostudyui/src/components/`
- `Horosa-Web/astrostudyui/src/models/`
- `Horosa-Web/astrostudyui/src/services/`
- `Horosa-Web/astrostudyui/src/utils/`

### 10.2 改主限法/推运/图表算法

- `Horosa-Web/astrostudyui/src/components/astro/`
- `Horosa-Web/astrostudyui/src/utils/primaryDirectionSync.js`
- `Horosa-Web/astrostudyui/src/utils/decennials.js`
- `Horosa-Web/astropy/astrostudy/`
- `Horosa-Web/astropy/websrv/webpredictsrv.py`
- `runtime/pd_auto/`
- `runtime/pd_reverse/`
- `主限法推演/`

### 10.3 改 Java 后端接口

- `Horosa-Web/astrostudysrv/astrostudyboot/`
- `Horosa-Web/astrostudysrv/astrostudy/`
- `Horosa-Web/astrostudysrv/astrostudycn/`
- `Horosa-Web/astrostudysrv/basecomm/`

### 10.4 改桌面安装器/发布链路

- `Horosa_Desktop_Installer/src-tauri/`
- `Horosa_Desktop_Installer/web/`
- `Horosa_Desktop_Installer/config/`
- `Horosa_Desktop_Installer/scripts/`
- `Horosa_Desktop_Installer/build/`
- `Horosa_Desktop_Installer/dist/`
- `runtime/mac/`

### 10.5 看运行日志与诊断

- `Horosa-Web/.horosa-local-logs/`
- `diagnostics/`
- `runtime/`
- `Horosa-Web/${env:HOME}/.horosa-logs/`
- `runtime/release-browser-self-check-20260311-163153/`

## 11. 当前仓库结构的现实特征

从实际目录看，这个仓库现在已经不是单一“Web 项目”，而是以下几部分叠在一起：

- 一套完整的占星/术数主业务工程
- 一套独立的 macOS 桌面交付工程
- 一套浏览器级验收与发布验收体系
- 一套主限法反推、训练、比对与研究资料体系
- 一批运行时与发布产物直接保留在仓库中

换句话说，当前仓库的真实重心已经是：

- `Horosa-Web/` 负责“业务能力”
- `Horosa_Desktop_Installer/` 负责“桌面交付”
- `scripts/` + `runtime/` + `主限法推演/` 负责“验证、反推、研究与发布闭环”

## 12. 本文档明确忽略的目录

按你的要求，本结构说明不展开以下两个目录：

- `Horosa_Native_macOS/`
- `Horosa-Windows-Docs/`
