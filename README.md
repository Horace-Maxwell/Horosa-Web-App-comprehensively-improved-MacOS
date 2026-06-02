<div align="center">

简体中文 · [English](README_EN.md)

<img src="Horosa_Desktop_Installer/assets/icon-source.png" alt="星阙 Horosa" width="128" />

# 星阙 Horosa

**把占星与中国术数，收进一个原生 macOS 工作站**<br />
*Western astrology and Chinese metaphysics, in one native macOS workstation*

[![Version](https://img.shields.io/badge/version-2.5.2-2ea043?style=flat-square)](https://github.com/Horace-Maxwell/Horosa-Web-App-comprehensively-improved-MacOS/releases/tag/v2.5.2)
[![License](https://img.shields.io/badge/license-AGPL--3.0-dc2626?style=flat-square)](LICENSE)
[![macOS](https://img.shields.io/badge/macOS%2012+-Apple%20Silicon-111111?style=flat-square&logo=apple&logoColor=white)](https://github.com/Horace-Maxwell/Horosa-Web-App-comprehensively-improved-MacOS/releases/tag/v2.5.2)
[![Signed & Notarized](https://img.shields.io/badge/Developer%20ID-signed%20%26%20notarized-1f6feb?style=flat-square)](https://github.com/Horace-Maxwell/Horosa-Web-App-comprehensively-improved-MacOS/releases/tag/v2.5.2)

[下载安装包](https://github.com/Horace-Maxwell/Horosa-Web-App-comprehensively-improved-MacOS/releases/download/v2.5.2/Horosa-Installer-macos-arm64-offline.pkg) ·
[完整中文说明](README_ZH.md) ·
[English Guide](README_EN.md) ·
[所有版本](https://github.com/Horace-Maxwell/Horosa-Web-App-comprehensively-improved-MacOS/releases)

</div>

---

星阙 Horosa 是一套桌面端的玄学工作站。西方占星的本命、推运、关系盘，连同八字、紫微、奇门、六壬、太乙这些中国传统术数，被放进同一个原生 macOS 应用里——不必在十几个网页排盘器之间来回切换，也不必自己拼装 Python、Java 与历表运行时。它以 Developer ID 签名、Apple 公证、离线 `.pkg` 的形式交付，下载即用。

> Horosa is a desktop workstation for traditional cosmology. Western natal, timing, and relationship astrology sit beside Chinese systems—Bazi, Ziwei, Qimen, Liuren, Taiyi—inside one native macOS app, so you stop juggling a dozen web tools and never hand-assemble a Python/Java/ephemeris runtime yourself. It ships as a Developer-ID-signed, Apple-notarized, offline `.pkg`.

## 下载 · Download

普通用户直接下载离线安装包，像任何 macOS 软件一样安装打开即可。无需自备 Python 或 Java，运行时已随包交付；更新只替换程序与共享组件，不会清空你的命例数据。

> Regular users grab the offline installer and open it like any finished macOS app. No Python or Java to install yourself—the runtime ships inside the package—and updates replace the program and shared runtime without wiping your saved charts.

**[⬇︎ Horosa-Installer-macos-arm64-offline.pkg](https://github.com/Horace-Maxwell/Horosa-Web-App-comprehensively-improved-MacOS/releases/download/v2.5.2/Horosa-Installer-macos-arm64-offline.pkg)**

适合：Apple Silicon · 弱网 / 离线环境 · 首次安装 · 转发给他人。

## 截图 · Screenshots

<div align="center">
<img src="docs/assets/screenshots/horosa-astrology-workspace.png" alt="Astrology workspace" width="900" />
<p><em>占星工作区 — 左侧起盘参数，中间图盘画布，右侧信息 / 相位 / 行星 / 古典 / 格局页签。</em><br /><em>Astrology workspace — chart controls on the left, the wheel in the center, detail tabs on the right.</em></p>

<img src="docs/assets/screenshots/horosa-sanshi-workspace.png" alt="Sanshi workspace" width="900" />
<p><em>三式工作区 — 起盘参数、九宫盘面、概览 / 太乙 / 神煞 / 六壬 / 八宫页签同屏。</em><br /><em>Sanshi workspace — setup, the nine-palace plate, and overview tabs in one view.</em></p>

<img src="docs/assets/screenshots/horosa-navigation-overlay.png" alt="Navigation overlay" width="900" />
<p><em>导航弹层 — 命盘推运、易与三式、工具工作台分组，支持搜索与最近使用。</em><br /><em>Command overlay — charts, Yi & Sanshi, and tools, with search and recents.</em></p>
</div>

## 功能总览 · What's Inside

导航把所有模块归为三组：**命**（命盘与推运）、**卜**（易与三式）、**工具**。下面是各组里实际可用的内容。

> Everything lives under three groups: **命** charts & timing, **卜** divination, and **工具** tools. Here is what each one actually ships.

### 命 · Charts & Timing

| 模块 | 说明 |
| --- | --- |
| **占星 Astrology** | 本命盘与三维盘（Babylon.js 实时 3D），多种宫位制与古典 / 现代行星集 |
| **星运 Timing** | 主限法（Primary Directions）、黄道星释（Zodiacal Releasing）、法达（Firdaria）、小限（Profection）、太阳弧（Solar Arc）、太阳 / 太阴返照、十年法、推运、星历 |
| **合盘 Relationship** | 比较盘、组合盘、影响盘、时空中点盘、马克斯盘 |
| **辅盘 Specialty** | 希腊星术（界限 / 阿拉伯点）、量化盘 / 中点树（汉堡学派）、星体地图（占星地理定位）、调波盘 |
| **印占 Vedic** | 北 / 南 / 东印度盘，恒星黄道 |
| **七政 Qizheng** | 七政四余 |
| **八字 Bazi · 紫微 Ziwei** | 四柱排盘；紫微斗数含四化盘 |
| **数算 · 其他** | 邵子神数、铁板神数、演禽等数术方法 |

### 卜 · Divination

| 模块 | 说明 |
| --- | --- |
| **三式 Sanshi United** | 奇门、太乙、六壬整合面：概览、太乙、神煞、六壬、大格、小局、参考、八宫 |
| **遁甲 Qimen · 六壬 Liuren · 太乙 Taiyi** | 三式各自的独立排盘入口 |
| **六爻 Liuyao · 分至 Jieqi · 风水 Feng Shui** | 纳甲六爻、节气盘、风水工具 |
| **其他 More** | 宿盘、金口诀、统摄法、皇极经世、五兆、太玄、荆诀、神易数 |

### 工具 · Tools

| 模块 | 说明 |
| --- | --- |
| **AI 分析 AI Analysis** | 接入 OpenAI / Anthropic / Gemini / Ollama / OpenRouter / 自定义端点；支持流式对话、历史记录、资料库（向量检索）、按技法 / 页签结构化导出 |
| **天文馆 Planetarium** | Babylon.js 实时三维天象 |
| **黄历 Almanac** | 农历 / 节气 / 择日 |
| **辅助 References** | 八卦类象、十二宫、规则速查 |

命盘与事盘都能本地保存：带标签、快照、后端原始数据，可 JSON 导入导出，重开后恢复现场。

> Charts and cases save locally—tags, snapshots, raw backend payloads, JSON import/export, and full restore on reopen.

## 本次更新 · What's New in v2.5.2 beta

这一版聚焦量化盘(汉堡学派)新技法、主限法新选项、AI 模型解耦与本地推理上下文,以及主限法盘的天文修正:

- **新增「90°中点盘」技法**(辅盘 → 量化盘)—— 折叠盘与多环模数盘双形态、三层叠盘(本命 / 行运 / 太阳弧)、八虚星(Cu / Ha / Ze / Kr / Ap / Ad / Vu / Po)、谐波盘基 H1..H512、可拖动的红色指针即时输出星体 / 中点 / 行星图读数与中点树。行运 / 太阳弧时刻与地点可独立调节,本命环锁定为最内圈。
- **主限法表格新增 Naibod 度数换算选项** —— 既有 Ptolemy / Alcabitius 链路完全不变;选 Naibod 时表格按 0.9856473 缩放日期、盘投射同步缩放、converse 复用同一参数链。同时修复主限法盘 ASC / MC / DESC / IC 四角赤纬(原误以地理纬度作黄纬,赤纬偏差被根治)。
- **AI 分析:聊天 / 嵌入模型解耦 + 高级参数** —— 顶栏可独立指定聊天与嵌入模型,「参数」抽屉提供思考档位 / temperature / top_p;Ollama 改走原生 `/api/chat` 与 `/api/embed`,`num_ctx` 等真正生效,长玄学上下文不再默认 4096 截断(#15)。
- **大六壬 / 三式合一 AI 挂载修复 + 六爻接入时间起卦白名单** —— 六爻仍守「永不按时间重算已存卦」铁律,新增的时间入口仅为新时点起卦。
- **量化盘 AI 四同步** —— AI 导出预设、导出设置版本、AI 分析挂载、命盘 / 事盘储存全部接入 90°中点盘段。

完整改动见 [v2.5.2 Release](https://github.com/Horace-Maxwell/Horosa-Web-App-comprehensively-improved-MacOS/releases/tag/v2.5.2)(离线 `.pkg`、app zip、runtime 包与 manifest 对齐到 `2.5.2 / 2.5.2-runtime1`)。

> v2.5.2 ships the 90°-dial (Hamburg-school) technique with eight hypothetical points and harmonic bases H1..H512, adds Naibod to the primary-direction table (keeping the verified Ptolemy / Alcabitius paths byte-identical), fixes the four-angle declination bug in the primary-direction chart, decouples chat / embedding models in the AI panel with a thinking-level / temperature / top-p drawer, switches Ollama to native `/api/chat` and `/api/embed` so `num_ctx` actually applies (long astrology context no longer truncates at 4096, #15), repairs the AI snapshot mount for Da-Liu-Ren and the unified three-style chart, and propagates the new dial section through all four AI surfaces (export, export settings, analysis mount, chart/event storage). See the [v2.5.2 release](https://github.com/Horace-Maxwell/Horosa-Web-App-comprehensively-improved-MacOS/releases/tag/v2.5.2) for the full log.

## 技术构成 · Under the Hood

- **前端 Frontend** — React 17 + Umi 3 + TypeScript，Ant Design；D3 绘盘，Babylon.js / Three.js 三维，Plotly 星体地图，Monaco 编辑 AI 导出模板。
- **后端 Backend** — Java 17 / Spring Boot 2.7 承载占星与中国术数核心服务；Python 3.9 服务层封装 Swiss Ephemeris（`pyswisseph`）与 vendored 的 kentang2017 传统术数引擎。
- **桌面壳 Desktop** — Tauri 2（Rust）原生外壳，Developer ID 签名 + Apple 公证，离线运行时随包交付，应用内更新。
- **发布 Distribution** — 面向 Apple Silicon（`arm64`）、macOS 12+ 的离线 `.pkg`。

## 文档 · Documentation

- [README_ZH.md](README_ZH.md) — 中文完整说明
- [README_EN.md](README_EN.md) — Full English guide
- [Horosa_Desktop_Installer/README.md](Horosa_Desktop_Installer/README.md) — 安装器与发布链路 / installer internals
- [docs/windows-porting-and-release-checklist.md](docs/windows-porting-and-release-checklist.md) — Windows 复刻与发布自检 / Windows porting checklist
- [THIRD_PARTY_NOTICES.md](THIRD_PARTY_NOTICES.md) · [SECURITY.md](SECURITY.md) · [CONTRIBUTING.md](CONTRIBUTING.md) · [CITATION.cff](CITATION.cff)
- 源码 / source: `Horosa-Web/`（前端 `astrostudyui`，后端 `astrostudysrv` / `astropy`，引擎 `vendor`）

## 致谢 · Acknowledgements

星阙的源流不能忘。最早的星阙 Horosa 由**郑大哥**一手创建，**荀爽（Herakleios，爽哥）**参与辅助设计，并把相关 App 与 Web 公开出来，后来者才有得研究、学习与延展。本项目正是在他们搭好的星阙体系、术数工作流与公开分享精神之上，继续做 macOS 交付、运行时打包、功能整合与体验改良。也感谢每一位持续测试、反馈、修复，推动 Horosa 变得更完整的人。

特别感谢 [kentang2017](https://github.com/kentang2017) 长期公开的传统术数 Python 项目。Horosa 接入或适配了其中多项计算引擎——已声明 MIT 的上游在 [`THIRD_PARTY_NOTICES.md`](THIRD_PARTY_NOTICES.md) 与对应 vendored 目录保留许可证；未找到明确开源声明的项目则单独标注，避免混同。

> The lineage matters. Horosa was originally created by **郑大哥**, with auxiliary design by **荀爽 (Herakleios)**, who released the App and Web that made later study and extension possible. This edition builds on that groundwork—adding macOS delivery, runtime packaging, integration, and polish—with gratitude to them and to everyone who keeps testing and fixing along the way. Special thanks to [kentang2017](https://github.com/kentang2017), whose openly shared Python projects power several of Horosa's calculation engines; licensing for each is recorded in [`THIRD_PARTY_NOTICES.md`](THIRD_PARTY_NOTICES.md).
