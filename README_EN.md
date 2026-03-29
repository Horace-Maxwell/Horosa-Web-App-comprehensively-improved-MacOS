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

## What End Users Should Download

Use this file:

- [Horosa-Installer-macos-arm64-offline-pkg.zip](https://github.com/Horace-Maxwell/Horosa-Web-App-comprehensively-improved-MacOS/releases/latest/download/Horosa-Installer-macos-arm64-offline-pkg.zip)

It is the only public download we recommend to regular users. It is the right choice for:

- first-time installation
- mainland China or weak-network environments
- forwarding the installer to another machine or another person
- users who want an install that is ready to open without a follow-up runtime download

Other release assets stay in the release because the installer, updater, and publishing flow still depend on them. They are not the file an ordinary user should choose manually.

## Installation Experience

Recommended steps:

1. Download `Horosa-Installer-macos-arm64-offline-pkg.zip`
2. Extract the zip
3. Run the `.pkg` inside
4. Open `/Applications/星阙.app`
5. If macOS still blocks the app, use `Open-XingQue-Unsigned.command` from the same folder as a fallback

Distribution profile:

- Apple Silicon (`arm64`)
- Developer ID signed
- notarized by Apple
- offline runtime path included in the install flow
- native in-app update path for future releases

## What This Delivery Gives You

- a native `.app` installed to `/Applications`
- a shared runtime managed for Horosa's Python and Java services
- manifest-driven update delivery
- one consistent review flow for install, repair, and update decisions

The goal is not “here is a codebase, please build it yourself.” The goal is “Horosa should feel like a polished desktop product on macOS.”

## Why the Offline `.pkg zip` Is the Primary Entry

We deliberately keep one public recommendation:

- `Horosa-Installer-macos-arm64-offline-pkg.zip`

That keeps the GitHub release surface understandable. Instead of asking a normal user to interpret multiple `.pkg`, `.zip`, runtime, and manifest assets, we point them to one download that matches the real install experience.

Benefits:

- clearer installation guidance
- better for weak networks and offline forwarding
- no hidden “download the runtime later” dependency on first open
- closer to the way polished desktop software is normally delivered

## Preview

| Main Workspace | Chart Verification Snapshot |
| --- | --- |
| ![Horosa Main Workspace](runtime/release_checks/browser_horosa_master_check_release.png) | ![Horosa Chart Snapshot](runtime/mastercheck_jieqi_entries.png) |

These images currently come from verified release-check artifacts and reflect the UI that ships through the desktop delivery pipeline.

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
