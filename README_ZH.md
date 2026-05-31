<div align="center">

简体中文 · [English](README_EN.md)

<img src="Horosa_Desktop_Installer/assets/icon-source.png" alt="星阙 Horosa" width="128" />

# 星阙 Horosa

**把占星与中国术数，收进一个原生 macOS 工作站**

[![Version](https://img.shields.io/badge/version-2.5.0%20beta-b45309?style=flat-square)](https://github.com/Horace-Maxwell/Horosa-Web-App-comprehensively-improved-MacOS/releases/tag/v2.5.0)
[![License](https://img.shields.io/badge/license-AGPL--3.0-dc2626?style=flat-square)](LICENSE)
[![macOS](https://img.shields.io/badge/macOS%2012+-Apple%20Silicon-111111?style=flat-square&logo=apple&logoColor=white)](https://github.com/Horace-Maxwell/Horosa-Web-App-comprehensively-improved-MacOS/releases/tag/v2.5.0)
[![Signed & Notarized](https://img.shields.io/badge/Developer%20ID-signed%20%26%20notarized-1f6feb?style=flat-square)](https://github.com/Horace-Maxwell/Horosa-Web-App-comprehensively-improved-MacOS/releases/tag/v2.5.0)
[![CI](https://img.shields.io/github/actions/workflow/status/Horace-Maxwell/Horosa-Web-App-comprehensively-improved-MacOS/ci.yml?branch=main&style=flat-square&label=CI)](https://github.com/Horace-Maxwell/Horosa-Web-App-comprehensively-improved-MacOS/actions/workflows/ci.yml)
[![Stars](https://img.shields.io/github/stars/Horace-Maxwell/Horosa-Web-App-comprehensively-improved-MacOS?style=flat-square)](https://github.com/Horace-Maxwell/Horosa-Web-App-comprehensively-improved-MacOS/stargazers)

[下载安装包](https://github.com/Horace-Maxwell/Horosa-Web-App-comprehensively-improved-MacOS/releases/download/v2.5.0/Horosa-Installer-macos-arm64-offline.pkg) ·
[入口页](README.md) ·
[English Guide](README_EN.md) ·
[所有版本](https://github.com/Horace-Maxwell/Horosa-Web-App-comprehensively-improved-MacOS/releases)

</div>

---

## 星阙是什么

星阙 Horosa 是一套桌面端的玄学工作站。西方占星的本命、推运、关系盘，连同八字、紫微、奇门、六壬、太乙这些中国传统术数，被放进同一个原生 macOS 应用里。它要解决的事其实很朴素：不必在十几个网页排盘器之间来回切，也不必自己拼装底层的 Python、Java 与历表运行时——你下载一个签名、公证、离线的安装包，打开的就是一个成品。

这个仓库承担的是 macOS 这一侧的交付：应用源码、共享运行时、Tauri 桌面外壳，以及把这一切打成单个 `.pkg` 的发布链路。

## 下载

普通用户直接下载离线安装包，像任何 macOS 软件一样安装、打开即可。

**[⬇︎ Horosa-Installer-macos-arm64-offline.pkg](https://github.com/Horace-Maxwell/Horosa-Web-App-comprehensively-improved-MacOS/releases/download/v2.5.0/Horosa-Installer-macos-arm64-offline.pkg)**

适合场景：

- Apple Silicon、macOS 12 及以上
- 弱网或完全离线的环境
- 第一次安装，或者要把安装包转发给别人
- 希望首次打开就能用，不再额外联网拉运行时

无需自备 Python 或 Java，运行时已随包交付。更新只替换程序与共享运行时，不会动你已经保存的命例与事盘数据。

## 截图

<div align="center">
<img src="docs/assets/screenshots/horosa-astrology-workspace.png" alt="占星工作区" width="900" />
<p><em>占星工作区 —— 左侧起盘参数，中间图盘画布，右侧信息 / 相位 / 行星 / 古典 / 格局页签。</em></p>

<img src="docs/assets/screenshots/horosa-sanshi-workspace.png" alt="三式工作区" width="900" />
<p><em>三式工作区 —— 起盘参数、九宫盘面、概览 / 太乙 / 神煞 / 六壬 / 八宫页签同屏呈现。</em></p>

<img src="docs/assets/screenshots/horosa-navigation-overlay.png" alt="导航弹层" width="900" />
<p><em>导航弹层 —— 命盘推运、易与三式、工具工作台分组，支持搜索与最近使用。</em></p>
</div>

## 功能总览

导航把所有模块归为三组：**命**（命盘与推运）、**卜**（易与三式）、**工具**。下面列的，是各组里真正能用的内容——名字与应用里的页签一一对应。

### 命 · 命盘与推运

这一层的强项是连贯：能读本命、把它沿时间推开、再带进第二个人，全程不离开同一个工作面。

- **占星** —— 本命盘与三维盘（Babylon.js 实时 3D），多种宫位制、古典 / 现代行星集
- **星运** —— 主限法、黄道星释、法达、小限、太阳弧、太阳 / 太阴返照、十年法、推运、星历
- **合盘** —— 比较盘、组合盘、影响盘、时空中点盘、马克斯盘
- **辅盘** —— 希腊星术（界限 / 阿拉伯点）、量化盘 / 中点树（汉堡学派）、星体地图（占星地理定位）、调波盘
- **印占** —— 北 / 南 / 东印度盘，恒星黄道
- **七政** —— 七政四余
- **八字 · 紫微** —— 四柱排盘；紫微斗数含四化盘
- **数算 · 其他** —— 邵子神数、铁板神数、演禽等数术方法

### 卜 · 易与三式

易与三式不止是几个独立页签，三式合一已经做成一个真正能工作的整合面。

- **三式（合一）** —— 奇门、太乙、六壬整合呈现：概览、太乙、神煞、六壬、大格、小局、参考、八宫
- **遁甲 · 六壬 · 太乙** —— 三式各自的独立排盘入口
- **六爻 · 分至 · 风水** —— 纳甲六爻、节气盘、风水工具
- **其他** —— 宿盘、金口诀、统摄法、皇极经世、五兆、太玄、荆诀、神易数

### 工具 · 工具工作台

- **AI 分析** —— 可接入 OpenAI / Anthropic / Gemini / Ollama / OpenRouter / 自定义端点；支持流式对话、历史记录、资料库（向量检索），以及按技法 / 页签结构化导出
- **天文馆** —— 基于 Babylon.js 的实时三维天象
- **黄历** —— 农历、节气与择日
- **辅助** —— 八卦类象、十二宫、规则速查

命盘与事盘都能本地保存：带标签、快照与后端原始结构化数据，可 JSON 导入导出，重开后恢复现场。

## v2.5.0 beta 更新

这一版是一次较大的功能补全 + 启动稳健化。

- **西占推运补全** —— 波斯向运双圈、行星弧、Vedic 推进、Jayne 赤纬向运、行星年龄、真 129 年法、Balbillus(以 core 盘校准);新增「福点整宫制」、相位美化、映点/反映点恢复。
- **时区/夏令时(DST)自动校正** —— 三处表单按经纬度离线求 IANA 时区并自动校正夏令时。
- **金口诀解读层** —— 神煞判语、四位生克、应期、分类用神、刑冲合害破、太玄数。
- **七政四余(Moira 还原度)** —— 28 宿环、显示选项、多 tab、大限、神煞判语。
- **紫微斗数·运限深化** —— 新增「运限」「格局」两 Tab:八字大运式级联运限(大限▸流年▸流月▸流日▸流时,流年/小限同级)、多层四化卡叠加、格局自动识别。
- **六壬·起课法增强(Phase4)** —— 七政接入 + 起课法(八客/四柱对齐/选时/演数)、换将(中气/节气)、分昼夜。
- **启动机制稳健化** —— 端口被占自动回收自家僵尸 / 换口重试、卡死后端精准回收(不误杀)、就绪前预热排盘服务、排盘自动重试、断线非阻塞重连横幅;根治「端口被占用用不了 / 打开后显示后端未启动」。

公证离线 `.pkg`、app zip、runtime 包与 manifest 已统一对齐到 `2.5.0 / 2.5.0-runtime1`。完整改动见 [v2.5.0 Release](https://github.com/Horace-Maxwell/Horosa-Web-App-comprehensively-improved-MacOS/releases/tag/v2.5.0)。

## 技术构成

- **前端** —— React 17 + Umi 3 + TypeScript，Ant Design；D3 绘盘，Babylon.js / Three.js 三维，Plotly 星体地图，Monaco 编辑 AI 导出模板
- **后端** —— Java 17 / Spring Boot 2.7 承载占星与中国术数核心服务；Python 3.9 服务层封装 Swiss Ephemeris（`pyswisseph`）与 vendored 的 kentang2017 传统术数引擎
- **桌面壳** —— Tauri 2（Rust）原生外壳，Developer ID 签名 + Apple 公证，离线运行时随包交付，应用内更新
- **发布** —— 面向 Apple Silicon（`arm64`）、macOS 12+ 的离线 `.pkg`

持续集成（CI）在每次推送时构建并测试三层：前端（Node 20）、后端（Java 17 / Maven）与 Rust 桌面外壳。

## 常见问题

**我只是普通用户，需要克隆仓库吗？**
不需要。直接在最新 release 里下载离线 `.pkg` 即可。

**安装完还要自己装 Python 或 Java 吗？**
不需要。离线安装路径已经把运行所需内容纳入流程。

**为什么 release 里还有别的文件？**
自动更新器、安装器、公证与运行时发布链路需要它们。对普通用户来说，真正要点的只有离线 `.pkg`。

**更新时会删掉我的数据吗？**
不会。应用更新与运行时切换替换的是程序与共享运行时，不会清空你保存的命例与事盘。

## 开发者入口

按你的目标选择入口：

- 想理解产品首页与用户入口：[README.md](README.md)
- 想看英文完整说明：[README_EN.md](README_EN.md)
- 想理解安装器与发布链路：[Horosa_Desktop_Installer/README.md](Horosa_Desktop_Installer/README.md)
- 想规划 Windows 复刻与发布验收：[Windows 复刻与发布自检指南](docs/windows-porting-and-release-checklist.md)
- 想知道每次 macOS 发布后 Windows 端要同步什么：[Windows 同步交接台账](docs/windows-sync-handoff.md)
- 想确认第三方许可证：[THIRD_PARTY_NOTICES.md](THIRD_PARTY_NOTICES.md)
- 应用源码：`Horosa-Web/` —— 前端 `astrostudyui`，后端 `astrostudysrv` / `astropy`，引擎 `vendor`
- 共享运行时与诊断：`runtime/` 与 `diagnostics/`

## 致谢

星阙的源流不能忘。最早的星阙 Horosa 由**郑大哥**一手创建，**荀爽（Herakleios，爽哥）**参与辅助设计，并把相关 App 与 Web 公开出来，后来者才有得研究、学习与延展。这个 macOS 版本的继续整理与发布，正是建立在他们已经搭起的星阙体系、术数工作流与公开分享精神之上——补的是 macOS 交付、运行时打包、功能整合与体验改良。没有他们，就没有今天这一版。也感谢每一位持续测试、反馈、修复，推动星阙变得更完整的人。

特别感谢 [kentang2017](https://github.com/kentang2017) 长期公开的传统术数 Python 项目。星阙接入或适配了其中多项计算引擎——已声明为 MIT 的上游项目在 [`THIRD_PARTY_NOTICES.md`](THIRD_PARTY_NOTICES.md) 与对应 vendored 目录中保留许可证说明；未找到明确开源声明的项目则单独标注，避免在没有声明的地方擅自假定许可证。
