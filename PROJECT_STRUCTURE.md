# Horosa 项目结构

> 更新时间：2026-05-24
> 口径：本文档以 **Git 跟踪的文件**（`git ls-files`）为准，即真正会提交到 GitHub 的内容；本地产物、缓存、运行时包等被 `.gitignore` 排除的内容不计入结构主线，仅在第 11 节统一说明。当前受跟踪文件约 **3,192** 个。

## 0. 说明与边界

- **只写仓库里真实存在、且会进入 GitHub 的内容。** 旧版文档是按本地磁盘扫描整理的，混入了大量被忽略或已删除的目录（`runtime/` 全量产物、`主限法推演/`、`dist/`、`node_modules/`、`target/`、PID、证书、临时脚本等）。本次重写已据 Git 实际跟踪结果重新梳理。
- **不展开二进制与海量资源的逐文件清单。** 历表资源、图片、xlsx、字典 JSON 这类大批量文件只说明用途与所在目录。
- **占位目录单独标注。** `runtime/` 与 `diagnostics/` 出于体积与隐私原因只提交 `README`（及 `.gitkeep`），实际产物不入库。

## 1. 顶层总览

### 1.1 提交到 GitHub 的目录树（一级）

```
.
├── Horosa-Web/                  # 主业务工程（前端 + Java 后端 + Python 算法 + 占星依赖 + 第三方引擎）
├── Horosa_Desktop_Installer/    # macOS 桌面安装器、Tauri 壳、打包/签名/公证/发布链路
├── modules/                     # 扩展参考工程与风水纳气模块（独立于主工程）
├── scripts/                     # 仓库级校验、浏览器验收、主限法反推与训练脚本
├── tools/mac/                   # 面向用户的一键 .command 入口
├── docs/                        # 截图、Windows 复刻清单、世界玄学总规划
├── runtime/                     # 仅占位 README（离线运行时产物不入库）
├── diagnostics/                 # 仅占位 README + .gitkeep（诊断输出不入库）
├── .github/                     # CI、Issue/PR 模板
├── README.md / README_EN.md / README_ZH.md
├── PROJECT_STRUCTURE.md         # 本文档
├── UPGRADE_LOG.md               # 升级与变更记录
├── THIRD_PARTY_NOTICES.md       # 第三方（kentang2017 等）许可证声明
├── LICENSE                      # AGPL-3.0
├── CITATION.cff                 # 引用元数据
├── CONTRIBUTING(.md/_ZH) · CODE_OF_CONDUCT(.md/_ZH) · SECURITY(.md/_ZH) · SUPPORT(.md/_ZH)
├── CODEOWNERS
├── Horosa_OneClick_Mac.command  # 根目录 Mac 一键入口
└── .gitignore · .gitattributes · .editorconfig
```

### 1.2 维护主线

仓库实际由五条主线构成，其余目录都是围绕它们的支撑：

1. **`Horosa-Web/`** —— 产品本体。占全部受跟踪文件的绝大多数（约 2,643 个），桌面应用最终加载的就是这里。
2. **`Horosa_Desktop_Installer/`** —— 把主工程打成签名、公证、离线 `.pkg` 的交付层（Tauri + Rust + 发布脚本）。
3. **`scripts/` + `tools/`** —— 仓库级校验 / 浏览器验收 / 主限法专项，以及给用户的一键入口。
4. **`docs/` + 根治理文件** —— 说明、社区规范、许可、规划文档。
5. **`modules/`** —— 与主工程平行的参考实现与风水模块。

### 1.3 根目录文件分类

| 类别 | 文件 |
| --- | --- |
| 产品说明 | `README.md`（双语入口）、`README_ZH.md`、`README_EN.md` |
| 工程文档 | `PROJECT_STRUCTURE.md`、`UPGRADE_LOG.md` |
| 许可与引用 | `LICENSE`（AGPL-3.0）、`THIRD_PARTY_NOTICES.md`、`CITATION.cff` |
| 社区治理 | `CONTRIBUTING(.md/_ZH)`、`CODE_OF_CONDUCT(.md/_ZH)`、`SECURITY(.md/_ZH)`、`SUPPORT(.md/_ZH)`、`CODEOWNERS` |
| 入口脚本 | `Horosa_OneClick_Mac.command` |
| 仓库配置 | `.gitignore`、`.gitattributes`、`.editorconfig` |

> 注：`developerID_*.cer`、`*.certSigningRequest`、`default.profraw`、`.DS_Store` 等存在于本地磁盘但被 `.gitignore` 排除，**不在 GitHub 仓库内**。

## 2. 主业务工程：`Horosa-Web/`

### 2.1 一级构成

| 子工程 | 跟踪文件量级 | 角色 |
| --- | --- | --- |
| `astrostudyui/` | ~490 | Umi 3 + React 17 + TypeScript 前端 |
| `astrostudysrv/` | ~1,074 | Java 17 / Spring Boot 2.7 多模块后端 |
| `astropy/` | ~109 | Python 3.9 图表 / 推运 / 历法算法与 HTTP 服务层 |
| `flatlib-ctrad2/` | ~234 | 改写版 flatlib 占星依赖库（含历表资源） |
| `vendor/` | ~737 | vendored 的 kentang2017 传统术数计算引擎 |
| `scripts/` | 1 | `repairEmbeddedPythonRuntime.py`（修复嵌入式 Python runtime） |
| `docs/` | 1 | 主工程内说明 |

启动 / 停止 / 自检脚本位于 `Horosa-Web/` 根：`start_horosa_local.sh`、`stop_horosa_local.sh`、`verify_horosa_local.sh`。

### 2.2 前端：`astrostudyui/`

顶层：`package.json`、`package-lock.json`、`.umirc.js`（Umi 配置）、`public/`、`scripts/`、`src/`、`.gitignore`。
脚本入口（`package.json`）：`start` / `build` / `build:file` / `postinstall` / `prettier` / `test` / `test:coverage` / `planetarium:perf`。

`src/` 划分：

| 目录 | 文件量级 | 说明 |
| --- | --- | --- |
| `components/` | ~349 | 全部功能模块组件（详见下表） |
| `utils/` | ~50 | 通用工具，含 AI 导出上下文 `aiAnalysisContext.js` 等 |
| `assets/` | ~18 | 前端静态资源 |
| `constants/` | ~15 | 常量定义 |
| `services/` | 7 | 后端接口封装 |
| `msg/` | 5 | 文案 / 消息 |
| `models/` | 5 | dva 数据流模型 |
| `pages/` | 4 | 页面入口（`index.js` 含导航配置 `navigationPages`） |
| `data/` | 4 | 内置数据 |
| `layouts/` | 3 | 布局 |
| `integrations/` | 2 | 桌面 / 外部集成桥接 |
| 其他 | — | `app.js`、`dva.js`、`global.js`、`global.css`、`renderers/`、`css/` |

`scripts/`（前端自有）：`patch_quill_domnodeinserted.js`、`warmHorosaRuntime.js`、`verifyHorosaRuntimeFull.js`、`verifyHorosaPerformanceRuntime.js`、`verifyPrimaryDirectionRuntime.js`、`planetariumPerfSmoke.js`。

#### 2.2.1 `components/` 功能分组

组件目录直接对应应用导航的三组（命 / 卜 / 工具）与若干基础设施：

**命 · 命盘与推运**

| 目录 | 模块 |
| --- | --- |
| `astro/` (46) | 西方占星本命盘核心 |
| `direction/` (2) | 星运 / 推运（主限法、黄道星释、法达、小限、太阳弧、返照等入口） |
| `relative/` (9)、`comp/` (11) | 合盘：比较 / 组合 / 影响 / 时空中点 / 马克斯 |
| `auxchart/` (2)、`germany/` (5)、`hellenastro/` (2) | 辅盘 / 量化盘（汉堡学派）/ 希腊星术 |
| `astro3d/` (5) | 三维盘 |
| `loc/` (1)、`acg/` (3)、`amap/` (7) | 星体地图 / 占星地理定位（含高德地图） |
| `guolao/` (14) | 七政四余（果老星宗） |
| `ziwei/` (12)、`ruleziwei/` (6) | 紫微斗数与规则 |
| `su28/` (33)、`suzhan/` (6) | 二十八宿 / 宿度 / 宿占 |
| `shusuan/` (1)、`yanqin/` (1)、`kinastro/` (1) | 数算 / 演禽 / kinastro 多系统接入 |
| `mingother/` (1) | 命盘组「其他」 |

**卜 · 易与三式**

| 目录 | 模块 |
| --- | --- |
| `sanshi/` (4) | 三式合一综合面 |
| `sz*`（`sztaiyi`/`szdunjia`/`szbagua`/`szsign`/`sznixiang`/`szfengye`/`szfangwei`，各 ~2） | 三式合一下的子盘 |
| `taiyi/` (3)、`sztaiyi/` | 太乙 |
| `dunjia/` (6) | 奇门遁甲 |
| `liureng/` (13)、`lrzhan/` (7) | 六壬（引擎 + 独立占断面） |
| `guazhan/` (5)、`gua/` (12) | 六爻 / 卦 |
| `jieqi/` (3) | 分至 / 节气盘 |
| `fengshui/` (1) | 风水 |
| `jinkou/` (7)、`tongshefa/` (1)、`huangji/` (1)、`wuzhao/` (1)、`taixuan/` (1)、`jingjue/` (1)、`shenyishu/` (1)、`dice/` (1) | 卜组「其他」：金口诀、统摄法、皇极经世、五兆、太玄、荆诀、神易数、起卦工具 |
| `cnyibu/` (1)、`otherbu/` (1) | 卜组聚合入口 |

**工具 · 工具工作台**

| 目录 | 模块 |
| --- | --- |
| `aianalysis/` (3) | AI 分析：多模型接入、流式、历史、资料库、结构化导出 |
| `planetarium/` (3) | 天文馆（Babylon.js 实时三维） |
| `calendar/` (3) | 黄历 |
| `cntradition/` (21) | 辅助参考（八卦类象、十二宫、规则速查） |

**基础设施 / 通用**

`commtools/` (12)、`graph/` (8)、`xq-ui/` (2)、`xq-icons/` (1)、`homepage/` (4)、`user/` (16)、`reader/` (6)、`multimedia/` (7)、`logqry/` (3)、`statis/` (1)、`deeplearn/` (2)、`admintools/` (2)，以及散件 `RichEditor.js`、`HomePageSetup.js`。

### 2.3 Java 后端：`astrostudysrv/`（Maven 多模块）

| 模块 | 量级 | 职责 |
| --- | --- | --- |
| `boundless/` | ~547 | 平台底座 / Web 框架基础（心跳、根路由、WebSocket、Spring 装配） |
| `astrostudycn/` | ~141 | 中国术数服务：八字（`BaZiBirth`/`PaiBaZi`/`BaZiPattern`）、紫微（`ZiWei`）、六壬（`LiuReng`）、卦（`Gua`）、节气（`JieQi`）、七政（`QizhengMoira`）、黄历（`Calendar`/`Nongli`）、天文馆（`Planetarium`）、命盘管理（`Chart`/`QueryChart`） |
| `astrostudy/` | ~99 | 西方占星核心与账户体系：计算（`Calc`/`AstroExtra`/`Predictive`/`ModernChart`/`IndiaChart`/`GermanyTech`/`Acg`/`Jdn`）、用户/登录/注册/Token、AI 分析（`AIAnalysis`）、统计（`Statistic`）、备份与数据迁移（`BackupMgmt`/`UserDataTransfer`） |
| `astrostudyboot/` | ~63 | Spring Boot 启动模块与 `resources/`（数据、配置） |
| `basecomm/` | ~51 | 鉴权与系统（`Auth`/`System`） |
| `iot/` | ~41 | 串口 / IoT（`name.prokop.bart.rxtx`） |
| `astrostudytest/` | ~41 | 后端测试 |
| `image/` | ~29 | 图像处理 |
| `astroreader/` | ~15 | 阅读 / 媒体 / 推流 / TTS（`Reader`/`Media`/`FlvUrl`/`Rtmp`/`TTS`） |
| `astrodeeplearn/` | ~14 | 深度学习 / 统计学习（`DeepLearn`/`StatisDeepLearn`） |
| `media/` (10)、`medialib/` (7) | — | 媒体库支撑 |
| `astroesp/` | ~8 | ESP / IoT 门锁（`DoorLock`） |
| `astroswisseph/` | ~7 | Swiss Ephemeris 适配 |

> CI（`.github/workflows/ci.yml`）实际编译并测试 `boundless`、`basecomm`、`image`、`astrostudy`。

### 2.4 Python 算法与服务：`astropy/`

- **`websrv/`（~34）** —— HTTP 服务层，每个 `web*srv.py` 对应一类算法接口：
  `webpredictsrv`（推运 / 主限法）、`webchartsrv` / `webcalc` / `webastroextrasrv`（图表与扩展）、`webmodernsrv`、`webindiasrv`（印度）、`webgermanysrv`（量化 / 中点）、`webjieqisrv`（节气）、`webqimensrv`（奇门）、`webtaiyisrv`（太乙）、`webjinkousrv`（金口诀）、`webwuzhaosrv`（五兆）、`webtaixuansrv`（太玄）、`webjingjuesrv`（荆诀）、`webshenyishusrv`（神易数）、`webshaozisrv` / `webtiebansrv`（邵子 / 铁板）、`webwangjisrv`（皇极经世）、`webqizhengkinsrv`（七政）、`webcetiansrv` / `webchunzisrv` / `webxianqinsrv` / `webfendjingsrv` / `webbeijisrv` / `webnanjisrv`（专门方法）、`webacgsrv`（占星地图）、`webplanetariumsrv`（天文馆）；另有 `registry.py` / `helper.py` / `kinastro_common.py` / `webjdn.py` 等公共件。
- **`astrostudy/`（~68）** —— 算法实现：`india/`（24，印度盘）、`models/`（12）、`jieqi/`（7）、`modern/`（6）、`guostarsect/`（4，七政）、`germany/`（2）、`acg/`（2），以及推运算法散件 `zreleasing.py`、`solararc.py`、`firdaria.py`、`termdirection.py`、`perpredict.py`、`perchart.py`、`thirteenthchart.py`、`signasctime.py`、`astroextra.py`。
- **`resources/`（2）** —— 资源文件。

### 2.5 占星依赖：`flatlib-ctrad2/`

改写版 flatlib（ctrad2 分支）。`flatlib/` 核心：`chart.py`、`object.py`、`aspects.py`、`datetime.py`、`geopos.py`、`angle.py`、`const.py`、`lists.py`、`props.py`、`utils.py`，子目录 `ephem/`、`dignities/`、`predictives/`、`protocols/`、`tools/`，以及最大的 `resources/`（~158，星历 / 数据资源）。仓库内另含 `recipes/`（16）、`docs/`（14）、`tests/`（3）、`scripts/`（3）、`contrib/`、`setup.py`、`requirements.txt`、`README.rst`。

### 2.6 第三方计算引擎：`vendor/`

vendored 的 [kentang2017](https://github.com/kentang2017) 传统术数 Python 项目，各自保留上游 `LICENSE` 或在 `THIRD_PARTY_NOTICES.md` 单独标注：

| 目录 | 量级 | 术数 | 许可 |
| --- | --- | --- | --- |
| `kinastro/` | ~604 | 多系统（邵子 / 铁板 / 演禽 / 七政四余 等合集） | MIT |
| `kinwangji/` | ~33 | 皇极经世 | MIT |
| `kinjinkou/` | ~21 | 金口诀 | MIT |
| `kintaiyi/` | ~20 | 太乙神数 | MIT |
| `kinwuzhao/` | ~18 | 五兆卜法 | MIT |
| `kinqimen/` | ~16 | 奇门遁甲 | MIT |
| `taixuanshifa/` | ~9 | 太玄筮法 | 未声明（单独标注） |
| `jingjue/` | ~8 | 荆诀 | 未声明（单独标注） |
| `shenyishu/` | ~7 | 神易数兵占 | 未声明（单独标注） |

顶层另有 `vendor/README.md`。

## 3. macOS 桌面安装器：`Horosa_Desktop_Installer/`

| 目录 / 文件 | 说明 |
| --- | --- |
| `src-tauri/` | Tauri 2 + Rust 原生壳：`src/main.rs`、`Cargo.toml`/`Cargo.lock`、`build.rs`、`tauri.conf.json`、`gen/schemas/`（ACL / capabilities / schema）、`icons/`（`icon.icns` / `icon.png` / `icon-1024.png`） |
| `web/` | 安装器与启动控制台前端：`index.html`、`app.js`、`style.css`、`diagnostics.{html,css,js}`、`settings.{html,css,js}`、`horosa-icon.png` |
| `scripts/` | 构建 / 签名 / 公证 / 发布 / 校验（13 个）：`build_desktop_release.sh`、`package_runtime_payload.sh`、`sign_runtime_payload.py`、`ad_hoc_sign_app.sh`、`check_apple_signing_prereqs.sh`、`publish_github_release.sh`、`verify_desktop_packaging.sh`、`verify_github_release_end_to_end.sh`、`verify_kentang_runtime_endpoints.py`、`verify_launcher_console_states.py`、`verify_public_distribution_readiness.sh`、`generate_icon.sh`、`verify_icon_alpha.py` |
| `config/` | `release_config.json`、`release_notes.md` |
| `distribution-support/` | 未签名安装引导模板：`UNSIGNED_INSTALL_GUIDE.template`、`unsigned_install_helper.template` |
| `installer-scripts/` | `postinstall.template`（pkg 安装后脚本模板） |
| `assets/` | `icon-source.png`（README 与应用使用的图标）、`icon-template.svg` |
| 根文件 | `package.json`、`package-lock.json`、`README.md`（安装器内部说明） |

> 构建产物 `build/`、`dist/`、`src-tauri/target*/`、生成的 `*.iconset/` 与 `icon-base.png` 均被 `.gitignore` 排除。

## 4. 仓库级脚本：`scripts/`

| 分组 | 文件 |
| --- | --- |
| 浏览器验收（Playwright） | `browser_horosa_master_check.py`、`browser_horosa_aianalysis_check.py`、`browser_horosa_final_layout_check.py`、`browser_horosa_jinkou_regression_check.py`、`browser_horosa_toolbar_management_check.py`、`browser_outer_shell_scroll_check.py`、`browser_primary_direction_chart_guangde_check.py`、`browser_toolbar_deep_state_check.py`、`browser_topbar_full_enumeration_check.py` |
| 集成与精度校验 | `check_horosa_full_integration.py`、`check_india_jyotish_engine.py`、`check_local_ephemeris_precision.py`、`compare_pd_backend_rows.py` |
| Mac 引导 | `mac/bootstrap_and_run.sh`、`mac/self_check_horosa.sh` |
| 仓库维护 | `repo/clean_for_github.sh`（提交前清理） |
| 依赖 | `requirements/mac-python.txt` |

## 5. 本地入口：`tools/mac/`

`Horosa_Local.command`（本地启动）、`Horosa_SelfCheck_Mac.command`（自检）、`Prepare_Runtime_Mac.command`（准备运行时）。

## 6. 文档：`docs/`

- `assets/screenshots/` —— 三张 README 截图（占星工作区 / 三式工作区 / 导航弹层）。
- `windows-porting-and-release-checklist.md` —— Windows 复刻与发布自检清单。
- `arm64-native-libs-hardening.md` —— Apple Silicon 上 x86_64-only JNI 原生库的失败路径加固记录。
- `world-metaphysics-masterplan/` —— 世界玄学总规划（11 篇）：`00` 应用审计与差距图、`01` 玄学分类法、`02` 占星天文引擎、`03` 中国玄学体系、`04` 印度与全球体系、`05` 占卜 / 牌 / 数字学与身心术、`06` 产品与架构路线图、`07` 研究验证框架、`08` 实现库索引、`09` 源注，外加 `README.md`。

## 7. 占位目录：`runtime/` 与 `diagnostics/`

二者均**仅提交占位文件**，真实内容不入库：

- `runtime/` —— 仅 `runtime/README.md`。离线运行时包、验证样本、主限法反推结果等本地产物由 `.gitignore` 的 `runtime/*`（保留 `!runtime/README.md`）排除。
- `diagnostics/` —— 仅 `diagnostics/.gitkeep` 与 `diagnostics/README.md`。诊断日志由 `diagnostics/*`（保留 README 与 gitkeep）排除。

## 8. 扩展参考工程：`modules/`

与主工程平行，作为参考实现与素材：

| 目录 | 量级 | 说明 |
| --- | --- | --- |
| `reference/kintaiyi-master/` | ~323 | 太乙参考工程（含 `pic/` 图片素材） |
| `reference/xuan-utils-pro-master/` | ~55 | 玄学工具参考库 |
| `reference/zhong-zhou-zi-wei-dou-shu-2/` | ~19 | 中州派紫微斗数参考 |
| `fengshui/naqi/` | ~33 | 风水纳气模块 |

## 9. CI 与仓库治理：`.github/`

- `workflows/ci.yml` —— 三层 CI：前端（Node 20，`npm test` + `build:file`）、后端（Java 17 / Maven，测试 `boundless`/`astrostudy` 等）、桌面壳（macOS runner，`cargo fmt --check` / `cargo check` / runtime 更新测试）。
- `ISSUE_TEMPLATE/`（`bug_report.yml`、`feature_request.yml`、`config.yml`）、`PULL_REQUEST_TEMPLATE.md`。

## 10. 维护者快速索引

| 想改什么 | 先看哪里 |
| --- | --- |
| 前端页面 / 交互 / 导航 | `Horosa-Web/astrostudyui/src/pages/index.js`（导航配置）、`src/components/<模块>/` |
| 主限法 / 推运 / 图表算法 | `Horosa-Web/astropy/astrostudy/`（算法）、`astropy/websrv/webpredictsrv.py`（接口）、`flatlib-ctrad2/flatlib/predictives/` |
| 传统术数引擎 | `Horosa-Web/vendor/<kin*>`（计算）+ `astropy/websrv/web<术>srv.py`（接入） |
| Java 后端接口 | `Horosa-Web/astrostudysrv/astrostudy`（西占 / 账户）、`astrostudycn`（中国术数）、`basecomm`（鉴权） |
| AI 分析 / 导出 | `src/components/aianalysis/`、`src/utils/aiAnalysisContext.js`、`astrostudysrv/.../AIAnalysisController.java` |
| 桌面安装器 / 发布 | `Horosa_Desktop_Installer/src-tauri/`、`Horosa_Desktop_Installer/scripts/`、`config/release_config.json` |
| 版本 / 发布对齐 | `Horosa_Desktop_Installer/config/release_config.json`、`tauri.conf.json`、各 `package.json`、`CITATION.cff` |

## 11. 提交边界（`.gitignore` 摘要）

以下内容**存在于本地开发环境但不会进入 GitHub**：

- **前端构建** —— `node_modules/`、`.umi/`、`.umi-production/`、`astrostudyui/dist/`、`astrostudyui/dist-file/`、`.tmp_horosa_*.js`、`.cache/`。
- **Java 构建** —— `target/`、`.mvn/`、`*.class`。
- **Python 缓存** —— `__pycache__/`、`*.pyc`、`.venv/`、`.pytest_cache/`、`.mypy_cache/`。
- **桌面安装器产物** —— `Horosa_Desktop_Installer/build/`、`dist/`、`src-tauri/target*/`、生成的 `*.iconset/`、`icon-base.png`。
- **运行时与本地状态** —— `runtime/*`（保留 README）、`.runtime/`、`.horosa-cache/`、`Horosa-Web/.horosa-local-logs*/`、`.horosa-browser-profile*/`、`*.pid`、`Horosa-Web/${env:HOME}/` 与 `${sys:user.home}/` 占位目录。
- **诊断** —— `diagnostics/*`（保留 README 与 `.gitkeep`）。
- **机密 / 证书** —— `developerID_*.cer`、`*.certSigningRequest`。
- **杂项** —— `.DS_Store`、`*.log`、`*.tmp`、`default.profraw`、IDE 目录（`.vscode/`、`.idea/`）。

> 维护本文档时，请始终以 `git ls-files` 为准重新核对，避免再次把本地产物写进结构主线。
