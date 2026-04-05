<div align="center">

# 星阙 Horosa for macOS

### 面向 Apple Silicon 的桌面玄学工作站，以签名离线安装包和正式公证链路交付

[![Latest Release](https://img.shields.io/github/v/release/Horace-Maxwell/Horosa-Web-App-comprehensively-improved-MacOS?display_name=tag&sort=semver)](https://github.com/Horace-Maxwell/Horosa-Web-App-comprehensively-improved-MacOS/releases/latest)
[![License](https://img.shields.io/badge/license-MIT-2ea043)](LICENSE)
[![GitHub Repo stars](https://img.shields.io/github/stars/Horace-Maxwell/Horosa-Web-App-comprehensively-improved-MacOS?style=flat)](https://github.com/Horace-Maxwell/Horosa-Web-App-comprehensively-improved-MacOS/stargazers)
[![Platform](https://img.shields.io/badge/platform-macOS%2012%2B%20%7C%20Apple%20Silicon-black)](https://github.com/Horace-Maxwell/Horosa-Web-App-comprehensively-improved-MacOS/releases/latest)
[![Distribution](https://img.shields.io/badge/distribution-Developer%20ID%20%2B%20Notarized-1f6feb)](https://github.com/Horace-Maxwell/Horosa-Web-App-comprehensively-improved-MacOS/releases/latest)
[![Primary Download](https://img.shields.io/badge/download-offline%20pkg-2ea043)](https://github.com/Horace-Maxwell/Horosa-Web-App-comprehensively-improved-MacOS/releases/latest/download/Horosa-Installer-macos-arm64-offline.pkg)

[入口页](README.md) | [英文说明](README_EN.md) | [最新 Release](https://github.com/Horace-Maxwell/Horosa-Web-App-comprehensively-improved-MacOS/releases/latest)

**当前版本：** `v1.2.0`

</div>

## 为什么 Horosa 与普通排盘器不同

这个仓库虽然承担的是 macOS 桌面分发层，但它交付出去的并不是一个单薄的安装器壳，而是一套已经相当成形的桌面玄学工作站。Horosa 在这里呈现出来的，是一个把西方占星、关系盘、推运体系、中国传统术数、易与三式、风水与 AI 导出工作流收进同一桌面工作面的产品。

这个 README 要表达的重点不只是“下载哪个包”，而是让人清楚看见：Horosa 已经是一个功能密度很高、层次很深的桌面研究工具，而不是只有几张图盘的轻量应用。

## 你可以直接拿它做什么

<table>
  <tr>
    <td width="50%">
      <strong>普通用户</strong><br />
      直接下载离线 <code>.pkg</code>，安装后就能像正常 macOS 桌面软件一样打开和使用 Horosa。
    </td>
    <td width="50%">
      <strong>维护者</strong><br />
      通过同一仓库继续理解发布链路、GitHub Release 页面、桌面安装器和共享运行时的组织方式。
    </td>
  </tr>
</table>

推荐入口：

- [Horosa-Installer-macos-arm64-offline.pkg](https://github.com/Horace-Maxwell/Horosa-Web-App-comprehensively-improved-MacOS/releases/latest/download/Horosa-Installer-macos-arm64-offline.pkg)

适合场景：

- 第一次安装 Horosa
- 中国大陆或弱网环境
- 需要把安装包转发给别人
- 希望首次打开不再额外联网拉运行时

## 截图预览

<div align="center">
  <p><strong>Main Workspace / 主界面工作区</strong></p>
  <img src="docs/assets/screenshots/main-workspace.png" alt="Horosa Main Workspace" width="1200" />
  <p><em>Horosa 在 macOS 正式版中的核心工作区，用来承载盘面浏览、参数控制与日常解读。</em></p>
</div>

<div align="center">
  <p><strong>Sanshi Workspace / 三式合一工作区</strong></p>
  <img src="docs/assets/screenshots/sanshi-workspace.png" alt="Horosa Sanshi Workspace" width="960" />
  <p><em>更偏高级功能的一面，用于体现三式合一与更深层的工具化分析场景。</em></p>
</div>

## 代表性工作流

### 本命到时运

Horosa 已经把从本命盘阅读到推运体系的链路接成一体。你可以从本命盘和三维盘进入，再继续切到主/界限法、黄道星释、法达、小限、太阳弧、返照与流年法。

它不是把一堆方法名硬塞到菜单里，而是把“如何从本命走向时间展开”做成一条连续工作流。

### 关系分析

关系分析层不是单一的比较盘页面，而是比较盘、组合盘、影响盘、时空中点盘、马克斯盘并行存在。它更像一组围绕同一段关系的不同分析透镜，而不是单一算法结果页。

### 中国传统术数栈

八字、紫微斗数、八卦类象、十二串宫、万年历与风水已经被放进同一桌面工作面中，所以 Horosa 呈现出来的是一整套中国传统术数栈，而不是只做了某一术的子集。

### 易与三式纵深

易与三式这部分既有单术入口，也有更深的整合分析。宿盘、易卦、六壬、金口诀、遁甲、太乙、统摄法之外，三式合一已经形成一个真正能工作的综合面。

## 已实现功能矩阵

### 西方占星

这一层的强项不只是“能起盘”，而是从本命到推运再到关系分析的完整链路。

- 星盘、本命盘、三维盘构成主盘面
- 推运盘覆盖主/界限法、黄道星释、法达、小限、太阳弧、返照与流年法
- 关系盘覆盖比较盘、组合盘、影响盘、时空中点盘、马克斯盘

### 全球与专门模块

Horosa 不只停留在常见西占模块，而是把更多专门工作面接进了同一产品。

- 节气盘
- 星体地图
- 七政四余
- 希腊星术
- 印度律盘
- 量化盘

### 中国传统体系

中国传统部分走的是系统化入口，而不是单点拼装。

- 八字、紫微斗数、八卦类象、十二串宫、规则参考
- 万年历与风水作为正式模块，而不是附属脚本
- 同一桌面环境下可以连续切换不同传统

### 易与三式

这一层的纵深来自“从单术到整合面”的连续组织。

- 宿盘、易卦、六壬、金口诀、遁甲、太乙、统摄法
- 三式合一已经覆盖概览、太乙、神煞、六壬、大格、小局、参考、八宫
- 多种说明性内容已经进入综合工作区，而不是只停留在占位页

### 工具与导出工作流

Horosa 的价值不只在计算，还在把研究流程做成可操作的桌面工作面。

- 星盘配置
- 相位选择
- 行星选择
- 星盘组件
- 小工具
- AI 导出
- AI 导出设置

## 桌面交付体验

macOS 这边强调的是正式桌面交付，而不是“把网页勉强包起来”。当前分发特点是：

- 面向 Apple Silicon (`arm64`)
- 采用 Developer ID 签名与 Apple 公证
- 离线路径内置运行时，本机组件安装完成后即可直接打开
- 应用内提供更新入口，不要求用户重新手动找包

换句话说，这个仓库的目标不是“让你自己搭环境”，而是“让 Horosa 在 Mac 上像一个完整成品一样被下载、安装、更新和恢复”。

## 最新版本

- [GitHub Release v1.2.0](https://github.com/Horace-Maxwell/Horosa-Web-App-comprehensively-improved-MacOS/releases/tag/v1.2.0)
- [所有 Release](https://github.com/Horace-Maxwell/Horosa-Web-App-comprehensively-improved-MacOS/releases)

## 常见问题

### 我只是普通用户，需要克隆仓库吗

不需要。直接下载 release 里的离线 `.pkg` 即可。

### 安装完成后还要自己装 Python 或 Java 吗

不需要。公开推荐的离线路径已经把运行所需内容纳入安装流程。

### 为什么 release 里还有别的文件

因为自动更新器、安装器、公证与运行时发布仍然需要这些资产。但对普通用户来说，真正要点的只有离线 `.pkg`。

### 更新时会不会删掉我的用户数据

不会。应用更新与运行时切换的目标是替换程序和共享组件，不是清空你的使用数据。

## 开发者入口

如果你是维护者或开发者，建议按这个路径进入：

- 想理解产品首页与用户入口：先看 [README.md](README.md)
- 想看英文完整说明：看 [README_EN.md](README_EN.md)
- 想理解安装器与发布链路：看 [Horosa_Desktop_Installer/README.md](Horosa_Desktop_Installer/README.md)
- 想看当前版本页面：看 [GitHub Release v1.2.0](https://github.com/Horace-Maxwell/Horosa-Web-App-comprehensively-improved-MacOS/releases/tag/v1.2.0)
- 想进入主工程：看 `Horosa-Web/`
- 想看共享运行时与诊断：看 `runtime/` 与 `diagnostics/`
