<div align="center">

简体中文 | [English](README_EN.md)

# 星阙 Horosa for macOS

### A desktop metaphysics workstation for Apple Silicon
### 面向 Apple Silicon 的桌面玄学工作站

[![Version](https://img.shields.io/badge/version-v2.0.1%20beta-b45309)](https://github.com/Horace-Maxwell/Horosa-Web-App-comprehensively-improved-MacOS/releases/tag/v2.0.1)
[![License](https://img.shields.io/badge/license-AGPL--3.0-dc2626)](LICENSE)
[![GitHub Repo stars](https://img.shields.io/github/stars/Horace-Maxwell/Horosa-Web-App-comprehensively-improved-MacOS?style=flat)](https://github.com/Horace-Maxwell/Horosa-Web-App-comprehensively-improved-MacOS/stargazers)
[![Platform](https://img.shields.io/badge/platform-macOS%2012%2B%20%7C%20Apple%20Silicon-black)](https://github.com/Horace-Maxwell/Horosa-Web-App-comprehensively-improved-MacOS/releases/tag/v2.0.1)
[![Distribution](https://img.shields.io/badge/distribution-Developer%20ID%20%2B%20Notarized-1f6feb)](https://github.com/Horace-Maxwell/Horosa-Web-App-comprehensively-improved-MacOS/releases/tag/v2.0.1)
[![Primary Download](https://img.shields.io/badge/download-offline%20pkg-2ea043)](https://github.com/Horace-Maxwell/Horosa-Web-App-comprehensively-improved-MacOS/releases/download/v2.0.1/Horosa-Installer-macos-arm64-offline.pkg)
[![CI](https://img.shields.io/github/actions/workflow/status/Horace-Maxwell/Horosa-Web-App-comprehensively-improved-MacOS/ci.yml?branch=main&label=CI)](https://github.com/Horace-Maxwell/Horosa-Web-App-comprehensively-improved-MacOS/actions/workflows/ci.yml)
[![GitHub Discussions](https://img.shields.io/badge/discussions-open-7c3aed)](https://github.com/Horace-Maxwell/Horosa-Web-App-comprehensively-improved-MacOS/discussions)
[![AIAnalysis](https://img.shields.io/badge/AIAnalysis-streaming%20%7C%20history%20%7C%20materials-0f766e)](https://github.com/Horace-Maxwell/Horosa-Web-App-comprehensively-improved-MacOS/releases/tag/v2.0.1)
[![Runtime](https://img.shields.io/badge/runtime-2.0.1--runtime1-2563eb)](https://github.com/Horace-Maxwell/Horosa-Web-App-comprehensively-improved-MacOS/releases/tag/v2.0.1-runtime1)
[![Security](https://img.shields.io/badge/security-policy-dc2626)](SECURITY.md)
[![Support](https://img.shields.io/badge/support-discussions%20%26%20email-4b5563)](SUPPORT.md)
[![Citation](https://img.shields.io/badge/citation-CFF-a855f7)](CITATION.cff)
[![Contributing](https://img.shields.io/badge/contributing-guide-0891b2)](CONTRIBUTING.md)

[![GitHub Repository](https://img.shields.io/badge/GitHub-Repository-3f3f46?logo=github&logoColor=white&labelColor=52525b)](https://github.com/Horace-Maxwell/Horosa-Web-App-comprehensively-improved-MacOS)
[![GitHub Releases](https://img.shields.io/badge/GitHub-Releases-1d4ed8?logo=github&logoColor=white&labelColor=52525b)](https://github.com/Horace-Maxwell/Horosa-Web-App-comprehensively-improved-MacOS/releases)
[![Read In English](https://img.shields.io/badge/Read%20In-English-0f766e?labelColor=52525b)](README_EN.md)
[![查看中文版](https://img.shields.io/badge/查看-中文版-0f766e?labelColor=52525b)](README_ZH.md)

[中文完整版](README_ZH.md) | [English Guide](README_EN.md) | [v2.0.1 Beta](https://github.com/Horace-Maxwell/Horosa-Web-App-comprehensively-improved-MacOS/releases/tag/v2.0.1) | [All Releases](https://github.com/Horace-Maxwell/Horosa-Web-App-comprehensively-improved-MacOS/releases)

<p>Horosa on macOS is delivered as a signed, notarized, offline-ready desktop product for cross-tradition analysis.</p>
<p>macOS 版 Horosa 以签名、公证、离线可安装的正式桌面产品形态交付，用来承载跨传统的术数分析工作流。</p>
<p><strong>Current release train / 当前发布线：v2.0.1 beta</strong></p>
<p><strong>Release focus / 本次重点：</strong><code>v2.0.1 beta</code> keeps the 2.0 desktop delivery track and fixes Qimen Dunjia backend parity with the Horosa mobile algorithm, especially Ju selection and Tianpan stems.</p>
<p><strong>Licensing note / 许可证说明：</strong>the public repository now ships under <code>AGPL-3.0</code> because the released stack integrates Swiss Ephemeris / <code>pyswisseph</code>; upstream third-party subdirectories keep their own original notices.</p>

</div>

## Start Here / 先看这里

<table>
  <tr>
    <td width="50%">
      <strong>English</strong><br /><br />
      End users should download the offline installer and open Horosa like a finished macOS app.<br />
      <a href="https://github.com/Horace-Maxwell/Horosa-Web-App-comprehensively-improved-MacOS/releases/download/v2.0.1/Horosa-Installer-macos-arm64-offline.pkg"><strong>Download the offline .pkg</strong></a>
    </td>
    <td width="50%">
      <strong>中文</strong><br /><br />
      普通用户请直接下载离线安装包，像标准 macOS 桌面软件一样安装和打开 Horosa。<br />
      <a href="https://github.com/Horace-Maxwell/Horosa-Web-App-comprehensively-improved-MacOS/releases/download/v2.0.1/Horosa-Installer-macos-arm64-offline.pkg"><strong>下载离线 .pkg</strong></a>
    </td>
  </tr>
  <tr>
    <td width="50%">
      Maintainers should start from the bilingual guides and the current GitHub Release page instead of guessing from asset names.
    </td>
    <td width="50%">
      维护者请从双语说明和当前 GitHub Release 页面进入，不要只靠 release 资产名反推结构。
    </td>
  </tr>
</table>

## Preview / 截图预览

<div align="center">
  <p><strong>Astrology Workspace / 占星工作区</strong></p>
  <img src="docs/assets/screenshots/horosa-astrology-workspace.png" alt="Horosa astrology workspace" width="1200" />
  <p><em>A three-column astrology workspace with chart controls, a large wheel canvas, detail tabs, and quick actions.</em></p>
  <p><em>三栏占星工作区：左侧命盘设置，中间图盘画布，右侧信息页签，底部保留常用功能。</em></p>
</div>

<div align="center">
  <p><strong>Sanshi Workspace / 三式工作区</strong></p>
  <img src="docs/assets/screenshots/horosa-sanshi-workspace.png" alt="Horosa Sanshi workspace" width="1200" />
  <p><em>The Sanshi surface keeps the plate, setup panel, overview tabs, and quick-function rail visible in one desktop view.</em></p>
  <p><em>三式工作区把起盘参数、盘面、概要页签和快捷功能放在同一桌面视图里。</em></p>
</div>

<div align="center">
  <p><strong>Navigation Overlay / 导航弹层</strong></p>
  <img src="docs/assets/screenshots/horosa-navigation-overlay.png" alt="Horosa navigation overlay" width="1200" />
  <p><em>The dark command overlay groups astrology, Yi/Sanshi, workbench tools, and recent modules for fast switching.</em></p>
  <p><em>深色导航弹层按命盘推运、易与三式、工具工作台和最近使用分组，方便快速切换模块。</em></p>
</div>

## At A Glance / 一眼看懂

<table>
  <tr>
    <td width="50%">
      <strong>English</strong><br /><br />
      Horosa combines Western astrology, timing systems, relationship charts, Chinese traditional methods, Yi and Sanshi workflows, Feng Shui, and AI-oriented export controls inside one desktop surface.
    </td>
    <td width="50%">
      <strong>中文</strong><br /><br />
      Horosa 把西方占星、推运体系、关系盘、中国传统术数、易与三式、风水与 AI 导出控制整合进同一个桌面工作面。
    </td>
  </tr>
  <tr>
    <td width="50%">
      The macOS delivery is already shaped as a real desktop release: Developer ID signing, Apple notarization, offline install, update delivery, and a clear public download path.
    </td>
    <td width="50%">
      macOS 交付已经具备正式桌面产品的基本形态：Developer ID 签名、Apple 公证、离线安装、更新交付，以及明确的公开下载入口。
    </td>
  </tr>
</table>

## Signature Workflows / 代表性工作流

### Natal To Timing / 从本命到时运

English: Start from natal and 3D chart reading, then move into primary directions, zodiacal releasing, firdaria, profection, solar arc, returns, and annual methods without leaving the same desktop product.

中文：从本命盘和三维盘进入，再继续切到主/界限法、黄道星释、法达、小限、太阳弧、返照与流年法，不需要离开同一个桌面产品。

### Relationship Analysis / 关系分析

English: The relationship layer already includes compare, composite, synastry, time-space midpoint, and Marks charts as parallel ways to inspect the same relationship.

中文：关系分析层已经覆盖比较盘、组合盘、影响盘、时空中点盘与马克斯盘，用不同结构切同一段关系。

### Chinese Traditional Stack / 中国传统术数栈

English: Bazi, Ziwei, calendar, Feng Shui, and supporting references already live in the same workspace, so the product feels like a broader traditional stack rather than a single-method tool.

中文：八字、紫微斗数、万年历、风水和配套参考入口已经进入同一工作面，所以它更像一整套中国传统术数栈，而不是某一术的单点工具。

### Yi And Sanshi Depth / 易与三式纵深

English: Yi and Sanshi go beyond standalone tabs through Su Zhan, Yi Gua, Liu Ren, Jin Kou, Dun Jia, Tai Yi, Tong She Fa, and a deeper Sanshi United surface.

中文：易与三式不只是单术入口，还包含宿盘、易卦、六壬、金口诀、遁甲、太乙、统摄法，以及更深的三式合一综合工作区。

## Capability Matrix / 功能矩阵

### Western Astrology / 西方占星

English: A continuous chain from natal reading to timing and relationship work.

中文：从本命阅读到推运、关系分析的连续链路。

- Natal chart and 3D chart / 星盘、本命盘、三维盘
- Timing stack including primary directions, returns, solar arc, and annual methods / 覆盖主限、返照、太阳弧与流年法的推运栈
- Compare, composite, synastry, time-space midpoint, and Marks charts / 比较盘、组合盘、影响盘、时空中点盘、马克斯盘

### Global And Specialty Modules / 全球与专门模块

English: A broader surface than the default desktop astrology stack.

中文：比常见桌面占星软件更宽的专门模块面。

- Jieqi charts / 节气盘
- Astrocartography and planetary maps / 星体地图与地理占星
- Qizheng Siyu, Hellenistic, Indian, and quantitative views / 七政四余、希腊星术、印度律盘、量化盘

### Chinese Traditional And Divination / 中国传统与术数

English: A structured traditional system rather than a decorative side module.

中文：系统化组织的传统术数层，而不是点缀式附属模块。

- Bazi, Ziwei, gua-symbol references, twelve-palace tools, and rule references / 八字、紫微斗数、八卦类象、十二串宫、规则参考
- Calendar and Feng Shui as first-class modules / 万年历与风水作为正式模块
- Yi and Sanshi modules across standalone and integrated surfaces / 易与三式兼具单术入口与整合面

### Desktop Workflow / 桌面工作流

English: Controls for shaping, filtering, inspecting, and exporting analysis sessions.

中文：围绕分析、筛选、检查与导出的桌面控制层。

- Chart configuration, aspect selection, planet selection / 星盘配置、相位选择、行星选择
- Chart components and utility tools / 星盘组件与小工具
- AI export and AI export settings / AI 导出与 AI 导出设置

## New In v2.0.1 / v2.0.1 新增重点

<table>
  <tr>
    <td width="50%">
      <strong>English</strong><br /><br />
      <code>v2.0.1 beta</code> is a focused beta update for the 2.0 desktop train: it realigns the Qimen Dunjia backend with the Horosa mobile algorithm while keeping the signed offline installer and runtime manifest path intact.
    </td>
    <td width="50%">
      <strong>中文</strong><br /><br />
      <code>v2.0.1 beta</code> 是 2.0 桌面发布线的聚焦修复版：奇门遁甲后端重新对齐 Horosa 手机版算法，同时继续保留签名离线安装包与 runtime manifest 链路。
    </td>
  </tr>
  <tr>
    <td width="50%">
      - Qimen Dunjia Ju selection now matches the Horosa mobile API for both Chaibu and Zhirun modes<br />
      - Zhirun keeps its own section logic while using the current chart day pillar for Sanyuan<br />
      - Tianpan stems, Dipan stems, doors, stars, Ju text, and Fu/Shi were checked against 300 Chabu + 300 Zhirun real mobile-API cases<br />
      - local fallback now follows exact solar-term transition times and keeps Zi-hour day switching at the mobile-compatible default<br />
      - desktop Eight Gods labels intentionally retain the established <code>虎 / 玄</code> display preference<br />
      - notarized offline <code>.pkg</code>, app zip, runtime archive, and manifest are aligned as <code>2.0.1 / 2.0.1-runtime1</code>
    </td>
    <td width="50%">
      - 奇门遁甲拆补与置润的起局结果对齐 Horosa 手机版 API<br />
      - 置润保留自己的节气段逻辑，但三元改按当前盘日柱判定<br />
      - 天盘干、地盘干、八门、九星、局数、值符值使已用 300 个拆补 + 300 个置润真实手机版 API 案例对照<br />
      - 本地兜底历法按准确交节时分判断节气，晚子时默认保持手机版兼容口径<br />
      - 桌面端八神显示有意保留既有 <code>虎 / 玄</code> 口径<br />
      - 公证离线 <code>.pkg</code>、app zip、runtime 包与 manifest 统一对齐到 <code>2.0.1 / 2.0.1-runtime1</code>
    </td>
  </tr>
</table>

## Get Started / 下载与文档导航

<table>
  <tr>
    <td width="50%">
      <strong>English</strong><br /><br />
      Public install entry: <code>Horosa-Installer-macos-arm64-offline.pkg</code><br />
      Best for Apple Silicon users, weak-network environments, offline forwarding, and first-time installs.<br /><br />
      <a href="https://github.com/Horace-Maxwell/Horosa-Web-App-comprehensively-improved-MacOS/releases/download/v2.0.1/Horosa-Installer-macos-arm64-offline.pkg"><strong>Open download</strong></a>
    </td>
    <td width="50%">
      <strong>中文</strong><br /><br />
      公开安装入口：<code>Horosa-Installer-macos-arm64-offline.pkg</code><br />
      适合 Apple Silicon、弱网环境、离线转发和第一次安装的普通用户。<br /><br />
      <a href="https://github.com/Horace-Maxwell/Horosa-Web-App-comprehensively-improved-MacOS/releases/download/v2.0.1/Horosa-Installer-macos-arm64-offline.pkg"><strong>打开下载</strong></a>
    </td>
  </tr>
</table>

## Documentation / 文档导航

<table>
  <tr>
    <td width="50%">
      <strong>English</strong><br /><br />
      <a href="README_EN.md">README_EN.md</a>: full English guide<br />
      <a href="README_ZH.md">README_ZH.md</a>: Chinese full guide<br />
      <a href="https://github.com/Horace-Maxwell/Horosa-Web-App-comprehensively-improved-MacOS/releases/tag/v2.0.1">v2.0.1 release page</a><br />
      <a href="https://github.com/Horace-Maxwell/Horosa-Web-App-comprehensively-improved-MacOS/releases">All releases</a><br />
      <a href="Horosa_Desktop_Installer/README.md">Installer internals</a>
    </td>
    <td width="50%">
      <strong>中文</strong><br /><br />
      <a href="README_ZH.md">README_ZH.md</a>：中文完整说明<br />
      <a href="README_EN.md">README_EN.md</a>：英文完整说明<br />
      <a href="https://github.com/Horace-Maxwell/Horosa-Web-App-comprehensively-improved-MacOS/releases/tag/v2.0.1">v2.0.1 版本页面</a><br />
      <a href="https://github.com/Horace-Maxwell/Horosa-Web-App-comprehensively-improved-MacOS/releases">所有 Release</a><br />
      <a href="Horosa_Desktop_Installer/README.md">安装器内部说明</a>
    </td>
  </tr>
</table>

<details>
<summary><strong>Developer Entry / 开发者入口</strong></summary>

<table>
  <tr>
    <td width="50%">
      <strong>English</strong><br /><br />
      Understand the public-facing repository layout: <a href="README.md">README.md</a><br />
      Inspect installer internals and publishing flow: <a href="Horosa_Desktop_Installer/README.md">Horosa_Desktop_Installer/README.md</a><br />
      Read the current beta release page: <a href="https://github.com/Horace-Maxwell/Horosa-Web-App-comprehensively-improved-MacOS/releases/tag/v2.0.1">v2.0.1 Beta</a><br />
      Enter the application source tree: <code>Horosa-Web/</code><br />
      Inspect runtime and diagnostics: <code>runtime/</code>, <code>diagnostics/</code>
    </td>
    <td width="50%">
      <strong>中文</strong><br /><br />
      理解首页与用户入口：<a href="README.md">README.md</a><br />
      查看安装器与发布链路：<a href="Horosa_Desktop_Installer/README.md">Horosa_Desktop_Installer/README.md</a><br />
      阅读当前版本页面：<a href="https://github.com/Horace-Maxwell/Horosa-Web-App-comprehensively-improved-MacOS/releases/tag/v2.0.1">v2.0.1</a><br />
      进入主工程源码：<code>Horosa-Web/</code><br />
      查看运行时与诊断：<code>runtime/</code>、<code>diagnostics/</code>
    </td>
  </tr>
</table>

</details>

## Acknowledgements / 致谢

本项目为参考星阙 Horosa-荀爽（Herakleios）所发布的星阙 App 和 Web，并在 macOS 交付、运行时打包、功能整合与使用体验上继续改良制作。源流不可忘：星阙 Horosa 最早由郑大哥一手创建，荀爽（Herakleios）曾参与辅助设计，并将相关 App 与 Web 版本公开出来供后来者研究、学习与延展。

请不要忘记爽哥和郑大哥的贡献。这个 macOS 版本的继续整理与发布，建立在前人已经搭起的星阙体系、术数工作流和公开分享精神之上。也感谢所有持续测试、反馈、修复和推动 Horosa 变得更完整的人。

This macOS edition is an improved distribution and integration work based on the Horosa App and Web released by Horosa-荀爽（Herakleios）. The lineage matters: Horosa was originally created by 郑大哥, with auxiliary design work from 荀爽（Herakleios）, and their public release made later study, maintenance, and extension possible.

Please do not forget the contributions of 爽哥 and 郑大哥. This repository continues from their groundwork with respect, gratitude, and the hope that Horosa can remain useful to more people over time.
