<div align="center">

# 星阙 Horosa for macOS

### A native Horosa desktop release for Apple Silicon, offline-ready installation, and notarized delivery

[![Latest Release](https://img.shields.io/github/v/release/Horace-Maxwell/Horosa-Web-App-comprehensively-improved-MacOS?display_name=tag&sort=semver)](https://github.com/Horace-Maxwell/Horosa-Web-App-comprehensively-improved-MacOS/releases/latest)
[![Platform](https://img.shields.io/badge/platform-macOS%2012%2B%20%7C%20Apple%20Silicon-black)](https://github.com/Horace-Maxwell/Horosa-Web-App-comprehensively-improved-MacOS/releases/latest)
[![Distribution](https://img.shields.io/badge/distribution-Developer%20ID%20%26%20Notarized-1f6feb)](https://github.com/Horace-Maxwell/Horosa-Web-App-comprehensively-improved-MacOS/releases/latest)
[![Primary Download](https://img.shields.io/badge/download-offline%20pkg%20zip-2ea043)](https://github.com/Horace-Maxwell/Horosa-Web-App-comprehensively-improved-MacOS/releases/latest/download/Horosa-Installer-macos-arm64-offline-pkg.zip)

[中文文档](README_ZH.md) | [English Guide](README_EN.md) | [Latest Release](https://github.com/Horace-Maxwell/Horosa-Web-App-comprehensively-improved-MacOS/releases/latest) | [版本说明](docs/releases/v1.1.7-zh.md) | [Release Notes](docs/releases/v1.1.7-en.md)

</div>

## Start Here / 先看这里

- End users: download [`Horosa-Installer-macos-arm64-offline-pkg.zip`](https://github.com/Horace-Maxwell/Horosa-Web-App-comprehensively-improved-MacOS/releases/latest/download/Horosa-Installer-macos-arm64-offline-pkg.zip).
- 普通用户：直接下载 `Horosa-Installer-macos-arm64-offline-pkg.zip`，解压后运行里面的 `.pkg`。
- Developers and maintainers: start with [README_EN.md](README_EN.md) or [README_ZH.md](README_ZH.md).
- 开发者与维护者：请阅读完整中英文文档，不要只看 release 资产名猜流程。

## Preview

| Main Workspace | Chart Verification Snapshot |
| --- | --- |
| ![Horosa Main Workspace](runtime/release_checks/browser_horosa_master_check_release.png) | ![Horosa Chart Snapshot](runtime/mastercheck_jieqi_entries.png) |

## Why This Repository Exists / 这个仓库的定位

- Deliver a polished macOS app experience for Horosa, not just source code.
- 提供面向真实用户的 macOS 分发链路，而不只是工程目录。
- Keep one public download recommendation: the offline `.pkg zip`.
- 保持唯一公开推荐下载入口，避免普通用户在多个内部资产之间迷路。
- Support native app updates, runtime switching, and shared runtime repair paths.
- 兼顾应用内更新、共享运行时切换和离线恢复。

## Recommended Download / 推荐下载

- Public install entry: `Horosa-Installer-macos-arm64-offline-pkg.zip`
- 当前公开安装入口：`Horosa-Installer-macos-arm64-offline-pkg.zip`
- Best for: China mainland, weak network, offline forwarding, and first-time users.
- 适合：中国大陆、弱网、离线转发、第一次安装的普通用户。

Other release assets remain available for the installer and updater, but they are not the file an ordinary user should pick manually.

其余 release 资产继续保留给安装器和自动更新器使用，不应作为普通用户的手动选择入口。

## Documentation / 文档导航

- [README_ZH.md](README_ZH.md): 中文完整说明，包含安装、升级、FAQ 与开发者入口。
- [README_EN.md](README_EN.md): Full English guide for installation, upgrades, FAQ, and developer entrypoints.
- [docs/releases/v1.1.7-zh.md](docs/releases/v1.1.7-zh.md): 当前 macOS 最新版本中文说明。
- [docs/releases/v1.1.7-en.md](docs/releases/v1.1.7-en.md): Current macOS release notes in English.
- [Horosa_Desktop_Installer/README.md](Horosa_Desktop_Installer/README.md): Internal installer and publishing workflow.

<details>
<summary><strong>Developer Entry / 开发者入口</strong></summary>

- Root app launcher: `Horosa_OneClick_Mac.command`
- Desktop installer project: `Horosa_Desktop_Installer/`
- Shared runtime and diagnostics: `runtime/` and `diagnostics/`
- Public release publish flow: `Horosa_Desktop_Installer/scripts/publish_github_release.sh`

</details>
