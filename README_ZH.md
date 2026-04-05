<div align="center">

# 星阙 Horosa for macOS

### 面向 Apple Silicon 的桌面玄学工作站，以签名离线安装包和正式公证链路交付

[![Latest Release](https://img.shields.io/github/v/release/Horace-Maxwell/Horosa-Web-App-comprehensively-improved-MacOS?display_name=tag&sort=semver)](https://github.com/Horace-Maxwell/Horosa-Web-App-comprehensively-improved-MacOS/releases/latest)
[![Platform](https://img.shields.io/badge/platform-macOS%2012%2B%20%7C%20Apple%20Silicon-black)](https://github.com/Horace-Maxwell/Horosa-Web-App-comprehensively-improved-MacOS/releases/latest)
[![Distribution](https://img.shields.io/badge/distribution-Developer%20ID%20%2B%20Notarized-1f6feb)](https://github.com/Horace-Maxwell/Horosa-Web-App-comprehensively-improved-MacOS/releases/latest)
[![Primary Download](https://img.shields.io/badge/download-offline%20pkg-2ea043)](https://github.com/Horace-Maxwell/Horosa-Web-App-comprehensively-improved-MacOS/releases/latest/download/Horosa-Installer-macos-arm64-offline.pkg)

[入口页](README.md) | [英文说明](README_EN.md) | [最新 Release](https://github.com/Horace-Maxwell/Horosa-Web-App-comprehensively-improved-MacOS/releases/latest)

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
      通过同一仓库继续理解发布链路、版本文档、桌面安装器和共享运行时的组织方式。
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

仓库里不再直接提交 README 截图资产，这样源码树更干净，也方便以后把展示素材和正式发布节奏分开。

建议下一轮补拍并用于 GitHub Release 或仓库首页展示的素材：

- 主界面工作区
- 三式合一工作区
- AIAnalysis 的分析 / 历史 / 资料 / 设置
- 桌面安装审查与更新流程

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

## 当前版本

- 当前发布线目标：`v1.2.0`
- 当前版本页面：[GitHub Release v1.2.0](https://github.com/Horace-Maxwell/Horosa-Web-App-comprehensively-improved-MacOS/releases/tag/v1.2.0)
- 所有版本历史：[All Releases](https://github.com/Horace-Maxwell/Horosa-Web-App-comprehensively-improved-MacOS/releases)

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

---

## 仓库补充说明

上面的内容保留为原来的发布导向说明。下面这部分会把 Horosa 按“正式开源软件仓库”的标准重新说明，包括产品定位、架构边界、本地优先原则、验证方式，以及未来公开协作所需的仓库界面与文档面。

## 关键特性

- 横跨西方占星与中国传统术数的多工作面体系
- `AIAnalysis` 已包含流式输出、本地优先历史、资料、模版、组合、备份与 provider 诊断
- Web 与 App 共用同一套主前端，但能分别做运行态验证
- 带 notarization 与离线安装链路的 macOS 桌面壳
- 有真实回归脚本来验证产品行为和交付质量

## 为什么 Horosa 不只是一个排盘器

Horosa 不是单纯起盘工具，也不是单纯安装器。它把完整工作会话当成产品本身：排盘、阅读、AI 辅助推理、导出、恢复、桌面交付，都属于同一套系统。

## 架构概览

- 前端：[`Horosa-Web/astrostudyui/`](Horosa-Web/astrostudyui)
- 本地服务：[`Horosa-Web/astrostudysrv/`](Horosa-Web/astrostudysrv) 和 [`Horosa-Web/astropy/`](Horosa-Web/astropy)
- 桌面壳与安装器：[`Horosa_Desktop_Installer/`](Horosa_Desktop_Installer)
- 仓库结构总览：[PROJECT_STRUCTURE.md](PROJECT_STRUCTURE.md)
- 桌面交付内部说明：[Horosa_Desktop_Installer/README.md](Horosa_Desktop_Installer/README.md)

## 本地优先 / 文件优先

- provider key 默认留在本地
- AIAnalysis 的资料、模版、组合、历史和备份以本地持久化为核心
- 导出与恢复是正式功能，不是附属功能
- 即使网络不稳定，产品仍应保持可用

## 截图与占位

当前仓库不再提交 README 截图二进制。

后续建议补拍：

- 主界面工作区
- 三式合一工作区
- AI分析五个右侧 Tab
- 桌面安装审查 / 更新流程

## 快速开始

### 本地 Web 运行态

```bash
cd Horosa-Web/astrostudyui
npm ci
npm test -- --runInBand
npm run build:file

cd ../..
cd Horosa-Web
./start_horosa_local.sh
./verify_horosa_local.sh
```

### 桌面端打包验证

```bash
cd Horosa_Desktop_Installer
./scripts/verify_desktop_packaging.sh
```

## 配置说明

### 工作区初始化

- 启动本地服务：[`Horosa-Web/start_horosa_local.sh`](Horosa-Web/start_horosa_local.sh)
- 验证本地运行态：[`Horosa-Web/verify_horosa_local.sh`](Horosa-Web/verify_horosa_local.sh)
- 停止本地服务：[`Horosa-Web/stop_horosa_local.sh`](Horosa-Web/stop_horosa_local.sh)

### Provider 配置

`AIAnalysis` 目前支持：

- OpenAI
- DeepSeek
- Anthropic
- Gemini
- OpenRouter
- Ollama
- Moonshot / Kimi
- 智谱 AI
- 硅基流动
- Groq
- xAI
- 自定义 OpenAI 兼容接口

实现入口可优先参考：

- [PROJECT_STRUCTURE.md](PROJECT_STRUCTURE.md)
- [Horosa_Desktop_Installer/README.md](Horosa_Desktop_Installer/README.md)
- `Horosa-Web/astrostudyui/src/components/aianalysis/`

## 如何跑测试

```bash
cd Horosa-Web/astrostudyui && npm test -- --runInBand
cd Horosa-Web/astrostudyui && npm run build:file
cd Horosa-Web/astrostudysrv/boundless && mvn test -DskipTests=false
cd Horosa-Web/astrostudysrv/astrostudy && mvn test -DskipTests=false
cd Horosa_Desktop_Installer && cargo test --manifest-path src-tauri/Cargo.toml runtime_update_command_
cd Horosa_Desktop_Installer && ./scripts/verify_desktop_packaging.sh
```

## 演示流程

1. 启动本地 Horosa 运行态。
2. 先确认主工作区和旧模块仍然正常。
3. 打开 `AIAnalysis`。
4. 选择 provider 预设与模型。
5. 选择案例，挂载资料或应用组合。
6. 发起一次流式分析。
7. 搜索历史、导出对话，并测试备份恢复。

## 路线图

- 完成首次公开 push 前的最后一轮 secrets 与路径清理
- 补拍更完整的 AIAnalysis 截图
- 开启 GitHub 侧的 security、branch protection 与 Discussions / issue 配置

## 当前限制

- 部分 legacy 文件仍需要公开前专项清理
- GitHub 仓库设置层面的 Discussions、私密漏洞报告与分支保护仍需要在正式发布时实际启用
- 后端模块依赖顺序仍比理想状态更手工一些

## 贡献

- [CONTRIBUTING.md](CONTRIBUTING.md)
- [CONTRIBUTING_ZH.md](CONTRIBUTING_ZH.md)

## 安全

- [SECURITY_ZH.md](SECURITY_ZH.md)
- [Horosa_Desktop_Installer/README.md](Horosa_Desktop_Installer/README.md)

## 许可证

本仓库源码现采用 MIT License，详见 [LICENSE](LICENSE)。

## 社区与发布准备

- [CODE_OF_CONDUCT_ZH.md](CODE_OF_CONDUCT_ZH.md)
- [SUPPORT_ZH.md](SUPPORT_ZH.md)
- [CITATION.cff](CITATION.cff)
- [PROJECT_STRUCTURE.md](PROJECT_STRUCTURE.md)
- [Horosa_Desktop_Installer/README.md](Horosa_Desktop_Installer/README.md)
