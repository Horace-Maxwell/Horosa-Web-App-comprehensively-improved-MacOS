<div align="center">

# Horosa for macOS

### The native Apple Silicon release channel for Horosa, with offline install and notarized delivery

[![Latest Release](https://img.shields.io/github/v/release/Horace-Maxwell/Horosa-Web-App-comprehensively-improved-MacOS?display_name=tag&sort=semver)](https://github.com/Horace-Maxwell/Horosa-Web-App-comprehensively-improved-MacOS/releases/latest)
[![Platform](https://img.shields.io/badge/platform-macOS%2012%2B%20%7C%20Apple%20Silicon-black)](https://github.com/Horace-Maxwell/Horosa-Web-App-comprehensively-improved-MacOS/releases/latest)
[![Distribution](https://img.shields.io/badge/distribution-Developer%20ID%20%26%20Notarized-1f6feb)](https://github.com/Horace-Maxwell/Horosa-Web-App-comprehensively-improved-MacOS/releases/latest)

[Portal](README.md) | [中文](README_ZH.md) | [Latest Release](https://github.com/Horace-Maxwell/Horosa-Web-App-comprehensively-improved-MacOS/releases/latest)

</div>

## What Horosa for macOS Is

This repository is the public-facing macOS distribution channel for Horosa. It does more than store source code: it also carries the desktop installer project, runtime packaging flow, update manifest, and the GitHub release surface that ordinary users actually see.

If you are here only to install Horosa, you do not need to clone the repo or assemble the runtime by hand. The intended user path is the offline installer package.

## Why Horosa Is More Than a Single Chart Viewer

What ships through this repository is not a thin desktop shell around one chart. Horosa on macOS already behaves like a metaphysics workstation: a shared desktop surface where Western astrology, timing systems, relationship analysis, Chinese traditional methods, Yi and Sanshi workflows, Feng Shui, and export-oriented reading live inside one product.

That distinction matters on GitHub. This repository certainly carries the release pipeline, but the thing it ultimately delivers is a feature-dense desktop analysis environment rather than a packaging wrapper with a logo.

## What End Users Should Download

Use this file:

- [Horosa-Installer-macos-arm64-offline.pkg](https://github.com/Horace-Maxwell/Horosa-Web-App-comprehensively-improved-MacOS/releases/latest/download/Horosa-Installer-macos-arm64-offline.pkg)

It is the only public download we recommend to regular users. It is the right choice for:

- first-time installation
- mainland China or weak-network environments
- forwarding the installer to another machine or another person
- users who want an install that is ready to open without a follow-up runtime download

Other release assets stay in the release because the installer, updater, and publishing flow still depend on them. They are not the file an ordinary user should choose manually.

## Installation Experience

Recommended steps:

1. Download `Horosa-Installer-macos-arm64-offline.pkg`
2. Double-click the `.pkg` to start installation
3. Open `/Applications/星阙.app`
4. If macOS asks for confirmation, allow it in System Settings -> Privacy & Security

Distribution profile:

- Apple Silicon (`arm64`)
- Developer ID signed
- notarized by Apple
- offline runtime path included in the install flow
- native in-app update path for future releases

## What You Will Actually See in Horosa

- A primary workspace built around natal charting and a dedicated 3D chart view, not just a single flat chart.
- A timing stack that already includes primary directions, a primary direction chart, zodiacal releasing, firdaria, profection, solar arc, solar return, lunar return, annual methods, and decennials.
- A relationship layer with compare, composite, synastry, time-space midpoint, and Marks charts.
- Broader astrology modules including Jieqi charts, astrocartography, Qizheng Siyu, Hellenistic, Indian, and quantitative views.
- Chinese traditional modules including Bazi, Ziwei, gua-symbol references, twelve-palace tools, Bazi rule references, calendar, and Feng Shui.
- An Yi and Sanshi stack covering Su Zhan, Yi Gua, Liu Ren, Jin Kou, Dun Jia, Tai Yi, and Tong She Fa.
- A Sanshi United workspace that already goes beyond a placeholder tab, with overview, Tai Yi, shensha, Liu Ren, major patterns, sub-patterns, references, and Bagong details.
- Workspace-level controls for chart configuration, aspect selection, planet selection, chart components, utilities, AI export, and AI export settings.

## What This Delivery Gives You

- a native `.app` installed to `/Applications`
- a shared runtime managed for Horosa's Python and Java services
- manifest-driven update delivery
- one consistent review flow for install, repair, and update decisions

The goal is not “here is a codebase, please build it yourself.” The goal is “Horosa should feel like a polished desktop product on macOS.”

## Why the Offline `.pkg` Is the Primary Entry

We deliberately keep one public recommendation:

- `Horosa-Installer-macos-arm64-offline.pkg`

That keeps the GitHub release surface understandable. Instead of asking a normal user to interpret multiple `.pkg`, `.zip`, runtime, and manifest assets, we point them to one signed and notarized installer that matches the real install experience.

Benefits:

- clearer installation guidance
- better aligned with the standard macOS install path
- no hidden “download the runtime later” dependency on first open
- closer to the way polished desktop software is normally delivered

## Preview

<div align="center">
  <p><strong>Main Workspace</strong></p>
  <img src="docs/assets/screenshots/main-workspace.png" alt="Horosa Main Workspace" width="1200" />
  <p><em>The primary Horosa workspace in the notarized macOS release, designed for chart reading, controls, and everyday desktop use.</em></p>
</div>

<div align="center">
  <p><strong>Sanshi Workspace</strong></p>
  <img src="docs/assets/screenshots/sanshi-workspace.png" alt="Horosa Sanshi Workspace" width="960" />
  <p><em>A more advanced view that spotlights Sanshi workflows and deeper tool-driven analysis inside the same desktop product.</em></p>
</div>

These images currently come from verified release-check artifacts and reflect the UI that ships through the desktop delivery pipeline.

## Implemented Disciplines

### Western and global astrology

- Natal chart, 3D chart, and everyday chart-reading workspace
- Predictive stack: primary directions, primary direction chart, zodiacal releasing, firdaria, profection, solar arc, solar return, lunar return, annual methods, and decennials
- Relationship charts: compare, composite, synastry, time-space midpoint, and Marks
- Jieqi charts, astrocartography, Qizheng Siyu, Hellenistic, Indian, and quantitative modules

### Chinese traditional and divination systems

- Bazi, Ziwei, gua-symbol references, twelve-palace tools, and Bazi rule references
- Yi and Sanshi modules: Su Zhan, Yi Gua, Liu Ren, Jin Kou, Dun Jia, Tai Yi, and Tong She Fa
- Sanshi United as an integrated surface with overview, Tai Yi, shensha, Liu Ren, pattern references, and Bagong interpretation details
- Calendar and Feng Shui as first-class desktop modules rather than side utilities

## Research Workflow

Horosa is built as a cross-tradition analysis surface. The intended experience is that a user can move from chart reading to timing, from relationship comparison to Chinese methods, and from calculation to export-oriented interpretation without leaving the same desktop product.

The current workflow surface already includes:

- chart configuration
- aspect selection
- planet selection
- chart components
- utility tools
- AI export
- AI export settings

Themes already exist as part of the workspace system, but they stay a supporting customization detail rather than the headline feature.

## Latest Release Docs

- [v1.1.7 Release Notes (English)](docs/releases/v1.1.7-en.md)
- [v1.1.7 中文版本说明](docs/releases/v1.1.7-zh.md)

Future releases will keep the same bilingual, versioned structure.

## FAQ

### Do I need to clone the repo to use Horosa

No. Regular users should go straight to the latest release and download the offline installer package.

### Do I need to install Python or Java myself

No. The public offline install path is designed to carry the required runtime setup for you.

### Why are there other files in the release

Because the installer, updater, notarization flow, and runtime publishing pipeline still need them. They are internal support assets, not the public recommendation.

### Will updates remove my user data

No. App replacement and runtime switching are designed to update the program and shared runtime, not erase user data.

## Developer Entry

If you maintain or build this stack, start here:

- [README.md](README.md): repository portal
- [README_ZH.md](README_ZH.md): full Chinese guide
- [Horosa_Desktop_Installer/README.md](Horosa_Desktop_Installer/README.md): installer internals and publishing flow
- [docs/releases/v1.1.7-en.md](docs/releases/v1.1.7-en.md): current version release document source

Key directories:

- `Horosa_Desktop_Installer/`: installer, signing, notarization, publish scripts
- `Horosa-Web/`: application source
- `runtime/`: shared runtime and verification artifacts
- `diagnostics/`: diagnostics and issue logs
