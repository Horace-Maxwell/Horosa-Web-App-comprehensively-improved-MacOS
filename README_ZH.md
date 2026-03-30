<div align="center">

# 星阙 Horosa for macOS

### 面向 Apple Silicon 的 Horosa 原生桌面发布仓库

[![Latest Release](https://img.shields.io/github/v/release/Horace-Maxwell/Horosa-Web-App-comprehensively-improved-MacOS?display_name=tag&sort=semver)](https://github.com/Horace-Maxwell/Horosa-Web-App-comprehensively-improved-MacOS/releases/latest)
[![Platform](https://img.shields.io/badge/platform-macOS%2012%2B%20%7C%20Apple%20Silicon-black)](https://github.com/Horace-Maxwell/Horosa-Web-App-comprehensively-improved-MacOS/releases/latest)
[![Distribution](https://img.shields.io/badge/distribution-Developer%20ID%20%26%20Notarized-1f6feb)](https://github.com/Horace-Maxwell/Horosa-Web-App-comprehensively-improved-MacOS/releases/latest)

[入口页](README.md) | [English](README_EN.md) | [最新 Release](https://github.com/Horace-Maxwell/Horosa-Web-App-comprehensively-improved-MacOS/releases/latest)

</div>

## Horosa / 星阙是什么

星阙是 Horosa 在 macOS 上的正式桌面分发形态。这个仓库既承担公开安装入口，也承担桌面安装器、更新清单、运行时打包与发布链路的维护。

如果你只是想安装使用，不需要理解源码结构，也不需要自己准备 Python、Java、Node。你只需要下载 release 里的离线安装包。

## 为什么 Horosa 不只是单一排盘器

Horosa 在 macOS 上展示出来的，不是一个“只能算一个盘”的轻工具，而是一个把多套术数工作面收进同一桌面工作站的产品形态。你可以在同一套界面里连续切换本命盘、推运、关系盘、节气盘、地理占星、中国传统术数、易与三式，以及三式合一等更重的分析场景。

这一点对 GitHub 首页很重要，因为这个仓库虽然承担桌面分发，但它真正交付出去的不是一个安装器壳，而是一套已经实现了大量玄学功能的桌面工作站。

## 普通用户下载哪个

请直接使用：

- [Horosa-Installer-macos-arm64-offline.pkg](https://github.com/Horace-Maxwell/Horosa-Web-App-comprehensively-improved-MacOS/releases/latest/download/Horosa-Installer-macos-arm64-offline.pkg)

它是当前唯一推荐给普通用户的公开下载入口，适合：

- 第一次安装 Horosa
- 中国大陆或弱网环境
- 需要把安装包转发给别人
- 不希望在安装后再额外联网准备本机组件

不推荐普通用户自己挑选其他 `.pkg`、`.zip`、`runtime`、`manifest` 资产。那些文件依然保留在 release 里，但它们主要是给安装器、自动更新器和维护流程使用的。

## 安装体验

推荐安装步骤：

1. 下载 `Horosa-Installer-macos-arm64-offline.pkg`
2. 双击 `.pkg` 开始安装
3. 安装完成后从 `/Applications/星阙.app` 打开
4. 如果系统提示安全确认，请在“系统设置 -> 隐私与安全性”中放行

当前分发特点：

- 面向 Apple Silicon (`arm64`)
- 采用 Developer ID 签名与 Apple notarization
- 离线路径内置运行时，本机组件安装完成后即可直接打开
- 应用内提供更新入口，不要求用户重新手动找包

## 你会在 Horosa 里实际看到什么

- 星盘、本命盘与三维盘共同构成日常主工作面，不是只有单一平面盘。
- 推运盘已经包含主/界限法、主限法盘、黄道星释、法达、小限、太阳弧、太阳返照、月亮返照、流年法与十年大运。
- 关系盘不是单一比较页，而是比较盘、组合盘、影响盘、时空中点盘、马克斯盘五路并行。
- 节气盘、星体地图、七政四余、希腊星术、印度律盘、量化盘这些更细分的模块都已经在同一产品面里落地。
- 中国传统部分不止八字，还包括紫微斗数、八卦类象、十二串宫、八字规则、万年历与风水。
- 易与三式里已经有宿盘、易卦、六壬、金口诀、遁甲、太乙、统摄法。
- 三式合一不是挂名入口，而是已经做成带概览、太乙、神煞、六壬、大格、小局、参考、八宫的综合工作区。
- 桌面工作流层还提供星盘配置、相位选择、行星选择、星盘组件、小工具、AI 导出与 AI 导出设置。

## 你会得到什么

- 原生 `.app`，默认安装到 `/Applications/星阙.app`
- 共享运行时目录，用于 Horosa 的 Python / Java 运行组件
- 固定 manifest 驱动的应用内更新能力
- 安装、修复、更新三条路径统一的“安装审查”体验

换句话说，这个仓库的目标不是“让你自己搭环境”，而是“让 Horosa 在 Mac 上像一个完整成品一样被下载、安装、更新和恢复”。

## 为什么只推荐离线 `.pkg`

当前公开分发策略刻意收敛到一个用户入口：

- `Horosa-Installer-macos-arm64-offline.pkg`

这样做是为了避免 GitHub Release 页面变成“很多资产都能点，但大多数人根本不知道该下哪个”的状态。离线 `.pkg` 的好处是：

- 安装包含义最清晰
- 支持标准 macOS 安装路径
- 首次打开不再依赖临时联网下载运行时
- 更接近标准桌面软件的交付体验

## 截图预览

<div align="center">
  <p><strong>Main Workspace / 主界面工作区</strong></p>
  <img src="docs/assets/screenshots/main-workspace.png" alt="Horosa Main Workspace" width="1200" />
  <p><em>这是 Horosa 在 macOS 正式版中的核心桌面工作区，用来承载盘面浏览、参数控制与日常解读。</em></p>
</div>

<div align="center">
  <p><strong>Sanshi Workspace / 三式合一工作区</strong></p>
  <img src="docs/assets/screenshots/sanshi-workspace.png" alt="Horosa Sanshi Workspace" width="960" />
  <p><em>这里展示的是更偏高级功能的一面，用于体现三式合一与更深层的工具化分析场景。</em></p>
</div>

这些截图目前来自已验收的真实产物检查流程，能反映当前桌面交付链路下的实际 UI 状态。

## 已实现功能矩阵

### 西方与全球占星

- 星盘、本命盘、三维盘构成主盘面
- 推运盘覆盖主/界限法、主限法盘、黄道星释、法达、小限、太阳弧、太阳返照、月亮返照、流年法、十年大运
- 关系盘覆盖比较盘、组合盘、影响盘、时空中点盘、马克斯盘
- 节气盘、星体地图、七政四余、希腊星术、印度律盘、量化盘已经并入桌面产品

### 中国传统与术数

- 八字、紫微斗数、八卦类象、十二串宫、八字规则都已有独立入口
- 易与三式已经整合宿盘、易卦、六壬、金口诀、遁甲、太乙、统摄法
- 三式合一已经形成完整综合面，包含概览、太乙、神煞、六壬、大格、小局、参考、八宫，以及奇门吉格、凶格、演卦等说明
- 万年历与风水不是附属脚本，而是桌面产品内的正式模块

## 分析与导出工作流

Horosa 的价值不只在“能起盘”，还在于它把不同传统与不同阅读深度收进同一工作面。用户可以从本命盘切到推运，再切到关系盘、中国术数或三式合一，而不需要换一套完全不同的工具。

这套工作流里，已经做出来的桌面级控制包括：

- 星盘配置
- 相位选择
- 行星选择
- 星盘组件
- 小工具
- AI 导出
- AI 导出设置

主题体系也已经存在，但这里把它作为工作区可定制能力轻描淡写带过，而不是当作主卖点。

## 最新版本文档

- [v1.1.7 中文版本说明](docs/releases/v1.1.7-zh.md)
- [v1.1.7 English Release Notes](docs/releases/v1.1.7-en.md)

后续版本会继续沿用同样的双语版本文档结构。

## 常见问题

### 我只是普通用户，需要克隆仓库吗

不需要。直接下载 release 里的离线 `.pkg` 即可。

### 安装完成后还要自己装 Python / Java 吗

不需要。公开推荐的离线路径已经把运行所需内容纳入安装流程。

### 为什么 release 里还有别的文件

因为自动更新器、安装器、公证与运行时发布仍然需要这些资产。但对普通用户来说，真正要点的只有离线 `.pkg`。

### 更新时会不会删掉我的用户数据

不会。应用更新与运行时切换的目标是替换程序和共享组件，不是清空你的使用数据。

## 开发者入口

如果你是维护者或开发者，建议按这个顺序进入：

- 根目录产品入口说明：[README.md](README.md)
- 英文文档：[README_EN.md](README_EN.md)
- 安装器内部说明：[Horosa_Desktop_Installer/README.md](Horosa_Desktop_Installer/README.md)
- 当前版本 release 文档源：[docs/releases/v1.1.7-zh.md](docs/releases/v1.1.7-zh.md)

日常相关目录：

- `Horosa_Desktop_Installer/`：桌面安装器、签名、公证、发布脚本
- `Horosa-Web/`：业务源码与前端/后端主工程
- `runtime/`：共享运行时与验收相关产物
- `diagnostics/`：诊断与运行问题记录
