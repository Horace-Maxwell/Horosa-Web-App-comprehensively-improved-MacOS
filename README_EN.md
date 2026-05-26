<div align="center">

[简体中文](README_ZH.md) · English

<img src="Horosa_Desktop_Installer/assets/icon-source.png" alt="Horosa" width="128" />

# Horosa

**Western astrology and Chinese metaphysics, in one native macOS workstation**

[![Version](https://img.shields.io/badge/version-2.1.4%20beta-b45309?style=flat-square)](https://github.com/Horace-Maxwell/Horosa-Web-App-comprehensively-improved-MacOS/releases/tag/v2.1.4)
[![License](https://img.shields.io/badge/license-AGPL--3.0-dc2626?style=flat-square)](LICENSE)
[![macOS](https://img.shields.io/badge/macOS%2012+-Apple%20Silicon-111111?style=flat-square&logo=apple&logoColor=white)](https://github.com/Horace-Maxwell/Horosa-Web-App-comprehensively-improved-MacOS/releases/tag/v2.1.4)
[![Signed & Notarized](https://img.shields.io/badge/Developer%20ID-signed%20%26%20notarized-1f6feb?style=flat-square)](https://github.com/Horace-Maxwell/Horosa-Web-App-comprehensively-improved-MacOS/releases/tag/v2.1.4)
[![CI](https://img.shields.io/github/actions/workflow/status/Horace-Maxwell/Horosa-Web-App-comprehensively-improved-MacOS/ci.yml?branch=main&style=flat-square&label=CI)](https://github.com/Horace-Maxwell/Horosa-Web-App-comprehensively-improved-MacOS/actions/workflows/ci.yml)
[![Stars](https://img.shields.io/github/stars/Horace-Maxwell/Horosa-Web-App-comprehensively-improved-MacOS?style=flat-square)](https://github.com/Horace-Maxwell/Horosa-Web-App-comprehensively-improved-MacOS/stargazers)

[Download](https://github.com/Horace-Maxwell/Horosa-Web-App-comprehensively-improved-MacOS/releases/download/v2.1.4/Horosa-Installer-macos-arm64-offline.pkg) ·
[Portal](README.md) ·
[中文说明](README_ZH.md) ·
[All Releases](https://github.com/Horace-Maxwell/Horosa-Web-App-comprehensively-improved-MacOS/releases)

</div>

---

## What Horosa Is

Horosa is a desktop workstation for traditional cosmology. Western astrology—natal reading, the full timing chain, and relationship work—sits beside Chinese systems like Bazi, Ziwei, Qimen, Liuren, and Taiyi, all inside one native macOS application. The point is that you stop juggling a dozen single-purpose web tools, and you never hand-assemble the Python, Java, and ephemeris pieces underneath. You download a signed, notarized, offline installer and open a finished app.

This repository is the macOS delivery of that app: the application source, the shared runtime, the Tauri desktop shell, and the publishing flow that turns all of it into a single `.pkg`.

## Download

Regular users should go straight to the offline installer and open Horosa like any other macOS app.

**[⬇︎ Horosa-Installer-macos-arm64-offline.pkg](https://github.com/Horace-Maxwell/Horosa-Web-App-comprehensively-improved-MacOS/releases/download/v2.1.4/Horosa-Installer-macos-arm64-offline.pkg)**

Best for:

- Apple Silicon Macs on macOS 12 or later
- weak-network or fully offline environments
- a first install, or forwarding the package to someone else
- anyone who wants the first launch to work without a separate runtime download

You do not need to install Python or Java yourself—the runtime ships inside the package. Updates replace the program and the shared runtime; they are not designed to touch your saved charts and cases.

## Screenshots

<div align="center">
<img src="docs/assets/screenshots/horosa-astrology-workspace.png" alt="Astrology workspace" width="900" />
<p><em>Astrology workspace — chart controls on the left, the wheel canvas in the center, and detail tabs (info, aspects, planets, classical, patterns) on the right.</em></p>

<img src="docs/assets/screenshots/horosa-sanshi-workspace.png" alt="Sanshi workspace" width="900" />
<p><em>Sanshi workspace — setup panel, the nine-palace plate, and overview tabs all visible at once.</em></p>

<img src="docs/assets/screenshots/horosa-navigation-overlay.png" alt="Navigation overlay" width="900" />
<p><em>The command overlay groups charts, Yi & Sanshi, and tools, with search and recents for fast switching.</em></p>
</div>

## What's Inside

The navigation organizes everything under three groups: **命** (charts & timing), **卜** (divination), and **工具** (tools). What follows is what each group actually ships—module names map directly to the in-app tabs.

### Charts & Timing (命)

The strength here is continuity: you can read a natal chart, walk it forward through time, and bring in a second person, without leaving the same surface.

- **Astrology (占星)** — natal chart plus a real-time 3D chart (Babylon.js), with multiple house systems and classical/modern planet sets
- **Timing (星运)** — primary directions, zodiacal releasing, firdaria, profection, solar arc, solar and lunar returns, decennials, progressions, and an ephemeris
- **Relationship (合盘)** — compare, composite, synastry, time-space midpoint, and Marks charts
- **Specialty (辅盘)** — Hellenistic (bounds and lots), quantitative / midpoint trees (Hamburg / Uranian), astrocartography with interactive maps, and a harmonic lab
- **Vedic (印占)** — North, South, and East Indian charts on the sidereal zodiac
- **Qizheng (七政)** — Qizheng Siyu
- **Bazi (八字) · Ziwei (紫微)** — four-pillar charting, and Purple Star including the Sihua chart
- **Numerology & more (数算 · 其他)** — Shaozi, Tieban, Yanqin and related numeric methods

### Divination (卜)

Yi and Sanshi go past standalone tabs into a genuinely integrated surface.

- **Sanshi United (三式)** — Qimen, Taiyi, and Liuren brought together: overview, Taiyi, shensha, Liuren, major patterns, sub-patterns, references, and the eight palaces
- **Qimen (遁甲) · Liuren (六壬) · Taiyi (太乙)** — each of the three formulae also as its own standalone surface
- **Liuyao (六爻) · Jieqi (分至) · Feng Shui (风水)** — najia hexagram casting, solar-term charts, and Feng Shui tools
- **More (其他)** — Suzhao, Jinkou, Tongshefa, Huangji Jingshi, Wuzhao, Taixuan, Jingjue, and Shenyishu

### Tools (工具)

- **AI Analysis (AI 分析)** — connects to OpenAI, Anthropic, Gemini, Ollama, OpenRouter, or a custom endpoint; supports streaming chat, conversation history, a materials library with vector retrieval, and structured export grouped by technique and tab
- **Planetarium (天文馆)** — a real-time 3D sky view built on Babylon.js
- **Almanac (黄历)** — lunar calendar, solar terms, and date selection
- **References (辅助)** — gua-symbol classes, the twelve palaces, and quick rule lookups

Charts and cases save locally with tags, snapshots, and raw backend payloads. Everything supports JSON import/export and restores its full state when you reopen it.

## New in v2.1.4 beta

This release is a focused, thorough AI Analysis fix for provider compatibility and error handling.

- **OpenAI reasoning models work** — `gpt-5.x` / `o1` / `o3` / `o4` previously returned only "模型未返回可用内容"; the request now omits `temperature` and uses `max_completion_tokens` for these families, so they reply normally. Existing models like `gpt-4.1` are unchanged.
- **Real upstream errors are surfaced** — provider failures (unsupported parameters, 401/404, etc.) are no longer swallowed into a generic message; the actual reason is shown so you can fix the configuration.
- **Credentials no longer leak** — on a failed request, sensitive headers (`Authorization`, `x-api-key`, `LocalIp`) are redacted from error messages and logs, and `?key=` query strings are stripped from logged URLs.

The notarized offline `.pkg`, app zip, runtime archive, and manifest are aligned to `2.1.4 / 2.1.4-runtime1`. Full log on the [v2.1.4 release page](https://github.com/Horace-Maxwell/Horosa-Web-App-comprehensively-improved-MacOS/releases/tag/v2.1.4).

## Under the Hood

- **Frontend** — React 17 + Umi 3 + TypeScript with Ant Design; D3 for chart drawing, Babylon.js / Three.js for 3D, Plotly for astrocartography maps, and Monaco for editing AI-export templates
- **Backend** — Java 17 / Spring Boot 2.7 hosts the core astrology and Chinese-method services; a Python 3.9 service layer wraps Swiss Ephemeris (`pyswisseph`) and the vendored kentang2017 traditional-method engines
- **Desktop shell** — Tauri 2 (Rust), Developer ID signed and Apple notarized, with the offline runtime bundled and an in-app update path
- **Distribution** — an offline `.pkg` targeting Apple Silicon (`arm64`) on macOS 12+

Continuous integration builds and tests all three layers—frontend (Node 20), backend (Java 17 / Maven), and the Rust desktop shell—on every push.

## FAQ

**Do I need to clone the repo to use Horosa?**
No. Download the offline installer from the latest release.

**Do I need to install Python or Java myself?**
No. The offline install path carries the required runtime for you.

**Why are there other files in the release?**
The installer, updater, notarization flow, and runtime publishing pipeline need them. For end users, the offline `.pkg` is the only thing that matters.

**Will updates remove my data?**
No. App replacement and runtime switching update the program and shared runtime; they are not designed to erase your saved charts and cases.

## For Maintainers

Start from the entry point that matches your goal:

- public-facing layout and bilingual portal: [README.md](README.md)
- the full Chinese guide: [README_ZH.md](README_ZH.md)
- installer internals and publishing flow: [Horosa_Desktop_Installer/README.md](Horosa_Desktop_Installer/README.md)
- a Windows port and release gate: [Windows porting checklist](docs/windows-porting-and-release-checklist.md)
- third-party licensing: [THIRD_PARTY_NOTICES.md](THIRD_PARTY_NOTICES.md)
- application source: `Horosa-Web/` — frontend in `astrostudyui`, backends in `astrostudysrv` and `astropy`, vendored engines in `vendor`
- shared runtime and diagnostics: `runtime/` and `diagnostics/`

## Acknowledgements

The lineage matters. Horosa was originally created by **郑大哥**, with auxiliary design work by **荀爽 (Herakleios, 爽哥)**, who released the App and Web versions that made later study, maintenance, and extension possible. This macOS edition builds on that groundwork—adding the delivery layer, runtime packaging, integration, and a great deal of polish—and it would not exist without them. Thanks, too, to everyone who keeps testing, reporting, and fixing things to make Horosa more complete.

Special thanks to [kentang2017](https://github.com/kentang2017), whose long-running, openly shared Python projects power several of Horosa's calculation engines. Upstream projects identified as MIT-licensed are documented in [`THIRD_PARTY_NOTICES.md`](THIRD_PARTY_NOTICES.md) alongside their vendored license texts; projects without an explicit open-source license are listed separately, so no license is assumed where none was declared.
