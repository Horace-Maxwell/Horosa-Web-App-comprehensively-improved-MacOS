<div align="center">

简体中文 · [English](README_EN.md)

<img src="Horosa_Desktop_Installer/assets/icon-source.png" alt="星阙 Horosa" width="128" />

# 星阙 Horosa

**把占星与中国术数，收进一个原生 macOS 工作站**<br />
*Western astrology and Chinese metaphysics, in one native macOS workstation*

[![Version](https://img.shields.io/badge/version-2.1.1%20beta-b45309?style=flat-square)](https://github.com/Horace-Maxwell/Horosa-Web-App-comprehensively-improved-MacOS/releases/tag/v2.1.1)
[![License](https://img.shields.io/badge/license-AGPL--3.0-dc2626?style=flat-square)](LICENSE)
[![macOS](https://img.shields.io/badge/macOS%2012+-Apple%20Silicon-111111?style=flat-square&logo=apple&logoColor=white)](https://github.com/Horace-Maxwell/Horosa-Web-App-comprehensively-improved-MacOS/releases/tag/v2.1.1)
[![Signed & Notarized](https://img.shields.io/badge/Developer%20ID-signed%20%26%20notarized-1f6feb?style=flat-square)](https://github.com/Horace-Maxwell/Horosa-Web-App-comprehensively-improved-MacOS/releases/tag/v2.1.1)
[![CI](https://img.shields.io/github/actions/workflow/status/Horace-Maxwell/Horosa-Web-App-comprehensively-improved-MacOS/ci.yml?branch=main&style=flat-square&label=CI)](https://github.com/Horace-Maxwell/Horosa-Web-App-comprehensively-improved-MacOS/actions/workflows/ci.yml)
[![Stars](https://img.shields.io/github/stars/Horace-Maxwell/Horosa-Web-App-comprehensively-improved-MacOS?style=flat-square)](https://github.com/Horace-Maxwell/Horosa-Web-App-comprehensively-improved-MacOS/stargazers)

[下载安装包](https://github.com/Horace-Maxwell/Horosa-Web-App-comprehensively-improved-MacOS/releases/download/v2.1.1/Horosa-Installer-macos-arm64-offline.pkg) ·
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

**[⬇︎ Horosa-Installer-macos-arm64-offline.pkg](https://github.com/Horace-Maxwell/Horosa-Web-App-comprehensively-improved-MacOS/releases/download/v2.1.1/Horosa-Installer-macos-arm64-offline.pkg)**

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

## 本次更新 · What's New in v2.1.1 beta

这一版把一批新接入的传统命法 / 卜法做成了可以长期使用的状态，而不只是“能跑”：

- **更宽的传统术数后端**：新增并规范太乙、金口诀、皇极经世、五兆、太玄、荆诀、神易数、Kin Astro、七政、奇门等引擎。
- **三式合一口径固定**：奇门与太乙走 kentang2017 后端，六壬保留本地实现；移除后端不支持的月家奇门，不再静默回退旧算法。
- **数据管理补全**：命盘 / 事盘保留新技法输入、标签、快照、后端结构化数据与 JSON 导入导出。
- **AI 导出结构化**：直接读取后端结构化数据，按技法 / 页签提供可勾选的导出分段。
- **Apple Silicon 原生库加固**：x86_64-only 的 libimagequant / OpenCV / RXTX 失败路径改为干净降级；普通安装启动、二维码/验证码、纯 Java PNG 压缩与核心排盘路径不受影响。
- **状态持久化**：用户设置、窗口大小在关闭、重开与版本更新后保留。
- **桌面体验打磨**：统一的启动控制台（Daily / Offline Ready / Failed）、修正重开时的窗口尺寸跳动、紫微四化盘隐藏亮度标签、全局明暗主题再校对。

完整改动见 [v2.1.1 Release](https://github.com/Horace-Maxwell/Horosa-Web-App-comprehensively-improved-MacOS/releases/tag/v2.1.1)（离线 `.pkg`、app zip、runtime 包与 manifest 对齐到 `2.1.1 / 2.1.1-runtime1`）。

> This release turns a batch of newly wired traditional methods into something durable rather than merely runnable, and adds Apple-Silicon hardening for optional x86_64-only native image/serial libraries. See the [v2.1.1 release](https://github.com/Horace-Maxwell/Horosa-Web-App-comprehensively-improved-MacOS/releases/tag/v2.1.1) for the full log.

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
