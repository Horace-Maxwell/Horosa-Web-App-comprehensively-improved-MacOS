---
name: horosa-dev
description: >-
  Horosa (星阙) project dev, verification & release operations. Use when building/previewing/running the local
  stack, doing end-to-end verification, releasing to GitHub, or working on the "AI分析" feature — especially
  per-technique context mounting (命盘/事盘 snapshots), adding/modifying an astrology technique, or the chat
  Markdown rendering. Covers build/preview/backend commands (incl. the embedded-Python gotcha), the headless
  technique-recompute architecture, the live verification procedure, and the macOS desktop release runbook.
---

# Horosa dev / verify / release

Horosa (星阙) is a macOS desktop astrology app. Repo root holds five maintenance lines; the product itself is
`Horosa-Web/` (Umi3 + React 17 frontend `astrostudyui/`, Java Spring Boot backend `astrostudysrv/`, Python
chart service `astropy/`). The desktop shell + release pipeline live in `Horosa_Desktop_Installer/` (Tauri).

For the full change history and the detailed release runbook, read
`docs/ai-analysis-context-and-markdown.md`. This skill is the quick operational guide.

## Critical gotchas (read first)

1. **Embedded Python, not the venv (now auto-handled by the launcher).** `runtime/mac/python/bin/python3` (note:
   `runtime/`, not `.runtime/`) is the complete embedded interpreter with every chart dep. The old
   `.runtime/mac/venv/bin/python3` is a broken symlink into miniconda *base* missing `cn2an`/`sxtwl`/`cnlunar`,
   which crashed the Python service (`:8899`) on boot. `start_horosa_local.sh` was fixed to (a) prefer the
   embedded runtime, and (b) reject any python whose readiness check is missing those load-bearing deps — so a
   plain `./start_horosa_local.sh` now self-resolves the right interpreter. `.claude/settings.local.json` still
   sets `HOROSA_PYTHON` as an explicit override (optional now). If the launcher prints "python runtime not ready",
   the chosen interpreter lacks a chart dep — install it or point `HOROSA_PYTHON` at the embedded runtime.
2. **Build needs the legacy OpenSSL flag.** `npm run build` / `npm run start` already export
   `NODE_OPTIONS=--openssl-legacy-provider` (umi3 on modern Node). If you invoke `umi`/webpack directly, set it.
3. **Backend ports are derived.** Frontend `ServerRoot` (`astrostudyui/src/utils/constants.js`) for localhost =
   `http://127.0.0.1:<pagePort + 1999>`. Dev server on `:8000` → backend `:9999` (Java) + `:8899` (Python).
   In a fresh preview browser you can force it: set `localStorage.horosaLocalServerRoot='http://127.0.0.1:9999'`
   and `horosaLocalServerRootMode='manual'`, then reload (or append `?srv=http://127.0.0.1:9999`).
4. **`umi` is not on PATH.** Build via `npm run build` (or `npx umi build`), never a bare `umi`.
5. **No ESLint gate** in the build, so unused vars won't fail CI — keep code clean yourself. (There are some
   intentionally-retained-but-unused 事盘 time-recompute helpers in `aiAnalysisContext.js`; safe to prune later.)
6. **Umi builds are sequential.** Do not run `npm run build` and `npm run build:file` in parallel; both write
   `src/.umi-production` and can corrupt generated files. If generated syntax errors appear there, clear the cache
   and rerun the builds one at a time.
7. **Claude harness JSON is part of the project.** `settings.json`, `settings.local.json`, and `launch.json` must
   parse before handoff. `settings.local.json` stays ignored because it contains absolute machine paths.
8. **Kentang/kin engines (奇门/太乙/金口/三式合一/术数) live on the chart service, not separate ports.** They're
   mounted onto the single Python chart service (`CHART_PORT`, default `:8899`) by
   `astropy/websrv/webchartsrv.py` → `mount_kentang_services`, and the release verifier
   `verify_kentang_runtime_endpoints.py --root http://127.0.0.1:${CHART_PORT}` checks them there. Two things had
   to be true for them to work locally: (a) `vendor/` on the Python path (now in `start_horosa_local.sh`
   `PYTHONPATH_ASTRO`) so `import kinqimen` etc. succeed; (b) the frontend resolving local kentang to the chart
   port — `integrations/kentang/serviceRoot.js` now maps a local `:9999` backend to `:8899` (the per-engine
   `defaultLocalPort` 8898/8895/… in `KENTANG_SERVICE_CONFIG` are legacy and were the cause of the
   `sanshi.qimen.kinqimen_unavailable` error). If a kentang technique shows "unavailable" locally, verify
   `curl -s -XPOST http://127.0.0.1:8899/qimen/pan -d '{...}'` returns `"source":"kinqimen"`, then check the
   frontend resolved to 8899 (not 8898). Production (`srv.horosa.com`) is unaffected — same host routes by path.

## Commands

```bash
# Frontend production build (the definitive compile check; ~30s)
cd Horosa-Web/astrostudyui && npm run build
cd Horosa-Web/astrostudyui && npm run build:file

# Claude harness sanity checks
python3 -m json.tool .claude/settings.json >/dev/null
python3 -m json.tool .claude/settings.local.json >/dev/null
python3 -m json.tool .claude/launch.json >/dev/null
test -x "$(python3 - <<'PY'
import json
print(json.load(open(".claude/settings.local.json"))["env"]["HOROSA_PYTHON"])
PY
)"

# Syntax-only parse check of edited JS (fast, no full build)
cd Horosa-Web/astrostudyui && node -e 'const p=require("@babel/parser");const fs=require("fs");
["src/utils/aiAnalysisContext.js"].forEach(f=>{p.parse(fs.readFileSync(f,"utf8"),{sourceType:"module",
plugins:["jsx","classProperties","objectRestSpread","optionalChaining","nullishCoalescingOperator","dynamicImport"]});console.log("OK",f);});'

# Local full stack (Java :9999 + Python :8899); HOROSA_PYTHON preset via settings.local.json
cd Horosa-Web && HOROSA_SKIP_UI_BUILD=1 ./start_horosa_local.sh     # starts services then exits
cd Horosa-Web && ./stop_horosa_local.sh                             # stop them
lsof -nP -iTCP:9999 -sTCP:LISTEN && lsof -nP -iTCP:8899 -sTCP:LISTEN # confirm up

# In-app preview (dev server). Config: .claude/launch.json → name "horosa-ui" on :8000
# Use the Claude Preview MCP tools: preview_start{name:"horosa-ui"}, preview_screenshot, preview_eval, preview_logs.
```

## AI分析 context-mounting architecture

The chat mounts a structured-text "snapshot" per selected technique into the right-side "本轮挂载上下文" panel,
then `buildPromptContext` layers it for the LLM. Core: `Horosa-Web/astrostudyui/src/utils/aiAnalysisContext.js`;
UI: `src/components/aianalysis/AIAnalysisMain.js` (+ `.less`).

**Two opposite rules, branched by `source.sourceType` in `buildTechniqueContext()`:**

- **命盘 (chart)** → recompute every selected technique from the chart's stored *birth data*.
  `regenerateChartTechniqueSnapshot(record, key)` dispatches per technique; for chart-derived ones it fetches via
  `fetchChartResultForRecord(record, {includePrimaryDirection})`.
- **事盘 (case / divination)** → mount ONLY the technique it was cast with, from the case's own stored `payload`.
  **Never recompute from time** (a cast = a one-time coin/dice/manual draw). Selecting a technique the cast
  doesn't have → "缺失". The time-based `regenerateCaseTechniqueSnapshot` path is intentionally NOT called.

**Hard invariant — never mount the wrong chart/cast.** `pickSnapshotCandidate()` drops any candidate whose
`compatible === false` (birth/cast signature mismatch via `isSnapshotMetaCompatible`). A stale global module
cache (`horosa.ai.snapshot.module.v1.<module>`) can never leak into a different chart. If you touch candidate
selection, preserve this filter.

**Wired chart techniques** (recompute from birth): `astrochart` (via `buildChartContext`), `bazi`, `ziwei`,
`indiachart`, `firdaria`, `primarydirect`, `guolao`, `suzhan`, `germany`. Each component exports a headless
builder (`buildBaziSnapshotForParams`, `buildZiweiSnapshotForParams`, `buildIndiaSnapshotForFields`,
`buildFirdariaSnapshotText`/`buildPrimaryDirectSnapshotText`, `buildGuolaoSnapshotForFields`,
`buildSuzhanSnapshotText`, `buildGermanySnapshotForFields`).

**Not wired (safe fallback only):** profection / solararc / solar-/lunar-return / givenyear (need a target
date), jieqi, and the DOM-/iframe-bound ones (primarydirchart, zodialrelease, decennials, cntradition,
fengshui). **Never recomputable:** `otherbu` (random dice) and `relative` (needs two charts). All of these show
correct cached data or "缺失" — never wrong data.

### How to add a technique (headless recompute)

1. In the technique's component, `export` a headless builder that takes the chart's form `fields` (or derived
   params), does its own fetch, and returns snapshot text. Reuse the existing `genParams`/`fieldsToParams` and the
   existing `buildXxxSnapshotText`. `planetDisplay = null` ⇒ shows the full traditional star set.
2. Import it in `aiAnalysisContext.js` and add a `case` to `regenerateChartTechniqueSnapshot`.
3. For settings, prefer the user's stored prefs (e.g. 七政四余 reads `getStoredGuolao*`) or sensible code defaults.
4. Parse-check, build, then verify live (below). Watch for circular imports (these components must not import
   `aiAnalysisContext`).

### Chat Markdown rendering

Assistant messages render through `renderMarkdownToHtml()` (marked@4 → DOMPurify@2 sanitize → `.markdownBody`).
User messages stay plain (`.messageText`, pre-wrap). Keep the DOMPurify sanitize step — it guards against
malicious HTML from the model. Styling lives in `.markdownBody` rules in `AIAnalysisMain.less`.

## Acceptance / verification procedure (do this for AI分析 changes)

Compile is necessary but NOT sufficient — verify behavior in the running app.

1. **Build green:** `npm run build` exits 0.
   If you are preparing a release, also run `npm run build:file` after `npm run build`, sequentially.
2. **Bring up the stack:** start backend (above), confirm `:9999` + `:8899` listen. Start preview `horosa-ui`.
3. **Point the preview at the backend:** via `preview_eval`, set `localStorage.horosaLocalServerRoot` +
   `…Mode='manual'`, reload; switch to the AI分析 view.
4. **Seed a known chart** (so birth data is controlled) into `localStorage['horosa.localCharts.v1']` (JSON array;
   record needs `cid,name,birth:'YYYY-MM-DD HH:mm:ss',zone,lat,lon,gpsLat,gpsLon,gender,group:'[]',updateTime`).
   Click 刷新案例.
5. **Select the chart + techniques.** Read the mounted panels via `preview_eval` over `.ant-collapse-item`
   (header = title+status+signature; expand to read `.ant-collapse-content-box`). **Assert every technique's
   signature matches the seeded birth date — this is the no-串盘 check.** Confirm non-empty content + "已就绪".
   For the current chart side this means the 9 wired techniques:
   `astrochart`, `indiachart`, `bazi`, `ziwei`, `firdaria`, `primarydirect`, `guolao`, `suzhan`, `germany`.
6. **事盘 check:** a 六爻 case shows its卦; adding 奇门 shows "缺失"; never a fresh re-cast.
7. **Markdown check:** assistant messages render through `marked` + `DOMPurify`; verify `<strong>/<h*>/<ul>/<table>`
   appear and there are **zero literal `**`** markers in the rendered report. Do not remove sanitize.
8. **Layout check:** 系统提示 sits in the right column above 挂载上下文; the toolbar buttons (刷新案例/新对话/…)
   sit at the bottom-left of 发送分析.

## Release to GitHub

This is a **manual, macOS-signed** pipeline (no CI auto-release on tag). Full ordered runbook + checklists are in
`docs/ai-analysis-context-and-markdown.md` (§ Release runbook). Summary:

1. Bump version in lockstep: `Horosa_Desktop_Installer/{package.json, src-tauri/Cargo.toml, src-tauri/tauri.conf.json}`
   + `CITATION.cff`; bump `Horosa_Desktop_Installer/config/release_config.json` `runtimeVersion` (`-runtime<N>`,
   reset to `-runtime1` on app bump). Append a `UPGRADE_LOG.md` entry.
2. `git commit -m "release: prepare vX.Y.Z beta"`.
3. `cd Horosa_Desktop_Installer && ./scripts/check_apple_signing_prereqs.sh`.
4. `HOROSA_PUBLIC_DISTRIBUTION=1 ./scripts/build_desktop_release.sh` (build + sign + notarize + staple).
5. `HOROSA_DESKTOP_SKIP_REBUILD=1 ./scripts/verify_desktop_packaging.sh` and
   `./scripts/verify_runtime_backend_boot.sh`.
6. `./scripts/verify_public_distribution_readiness.sh`.
7. `./scripts/publish_github_release.sh` (needs `GITHUB_TOKEN`; creates/updates the release + uploads assets).
8. Tag after the release is confirmed: `git tag vX.Y.Z && git push origin vX.Y.Z`.

Build/sign/publish/push are consequential and deliberately NOT auto-approved in `.claude/settings.json` — confirm
with the user before running them. Never `git push --force` to main.
