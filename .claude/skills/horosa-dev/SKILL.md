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
   and rerun the builds one at a time. Cache deletion is intentionally not auto-approved by the harness; ask before
   using destructive cleanup commands.
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
9. **八字盘走前端本地计算，不是后端 (a bazi display fix must touch the frontend).** The 八字 chart is rendered
   from a local JS calc — `utils/baziLunarLocal.js` → `buildLocalBaziResult` (lunar-javascript based), called by
   `cntradition/BaZi.js` `fetchBaziCached`/`fetchBaziDirectCached`. The Java backend `/bazi/birth`
   (`astrostudycn` `BaZi.java` / `BaZiDirect`) is **only an edge-case fallback** when the local calc throws.
   So fixing what the bazi chart *displays* means changing `baziLunarLocal.js` (and the display components),
   not just the backend. **Time-display contract** (mirrored in both the local calc and `BaZi.java`):
   `nongli.clockTime` = raw input / clock time (stable); `nongli.solarTime` = apparent solar time
   (longitude + equation-of-time corrected, **independent of `timeAlg`**); `nongli.birth` = the pillar calc
   basis (changes with `timeAlg`). Any time row that reads `nongli.birth` will "jump" when the user toggles
   时间算法 — read `clockTime`/`solarTime` instead. Off the +08:00 (120°E) meridian, `solarTime` ≠ `clockTime`.
   The 4 display sites are `cntradition/{PaiBaZi,BaZiAppInfoPanel,BaZiLegacyView,BaZi}.js`. Full detail +
   multi-longitude verification: `docs/bazi-time-display-fix.md`.

## Commands

```bash
# Frontend production build (the definitive compile check; ~30s)
cd Horosa-Web/astrostudyui
npm run build
npm run build:file
cd ../..

# Claude harness sanity checks
python3 -m json.tool .claude/settings.json >/dev/null
python3 -m json.tool .claude/settings.local.json >/dev/null
python3 -m json.tool .claude/launch.json >/dev/null
test -x runtime/mac/python/bin/python3
runtime/mac/python/bin/python3 -c 'import cn2an, kerykeion, sxtwl, cnlunar; print("embedded python ok")'

# Syntax-only parse check of edited JS (fast, no full build)
cd Horosa-Web/astrostudyui
node -e 'const p=require("@babel/parser");const fs=require("fs");
["src/utils/aiAnalysisContext.js"].forEach(f=>{p.parse(fs.readFileSync(f,"utf8"),{sourceType:"module",
plugins:["jsx","classProperties","objectRestSpread","optionalChaining","nullishCoalescingOperator","dynamicImport"]});console.log("OK",f);});'

# Focused automated tests for the current AI分析/kentang harness surface
npm test -- --runInBand src/utils/__tests__/aiAnalysisContext.test.js
npm test -- --runInBand src/integrations/kentang/__tests__/serviceRoot.test.js src/utils/__tests__/aiAnalysisSelection.test.js
cd ../..

# Local full stack (Java :9999 + Python :8899); HOROSA_PYTHON preset via settings.local.json
cd Horosa-Web
HOROSA_SKIP_UI_BUILD=1 ./start_horosa_local.sh                      # starts services then exits
./stop_horosa_local.sh                                              # stop them
lsof -nP -iTCP:9999 -sTCP:LISTEN && lsof -nP -iTCP:8899 -sTCP:LISTEN # confirm up

# Clean-env local startup smoke: proves the launcher finds runtime/mac/python by itself.
env -u HOROSA_PYTHON -u PYTHONPATH HOROSA_SKIP_UI_BUILD=1 ./start_horosa_local.sh
./stop_horosa_local.sh
cd ..

# Browser AI分析 smoke (writes runtime/browser_horosa_aianalysis_check.json)
python3 scripts/browser_horosa_aianalysis_check.py

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
2. **Focused tests green:** run the AIAnalysis context tests and kentang service-root tests above. The kentang
   local test must expect `:9999` → `:8899`, not legacy per-engine ports.
3. **Harness green:** JSON parse `.claude/settings.json`, `.claude/settings.local.json`, and `.claude/launch.json`;
   verify `.claude/settings.local.json` is ignored by git and its `HOROSA_PYTHON` points at an existing embedded
   runtime interpreter.
4. **Bring up the stack:** start backend (above), confirm `:9999` + `:8899` listen. Start preview `horosa-ui`.
5. **Point the preview at the backend:** via `preview_eval`, set `localStorage.horosaLocalServerRoot` +
   `…Mode='manual'`, reload; switch to the AI分析 view.
6. **Seed a known chart** (so birth data is controlled) into `localStorage['horosa.localCharts.v1']` (JSON array;
   record needs `cid,name,birth:'YYYY-MM-DD HH:mm:ss',zone,lat,lon,gpsLat,gpsLon,gender,group:'[]',updateTime`).
   Click 刷新案例.
7. **Select the chart + techniques.** Read the mounted panels via `preview_eval` over `.ant-collapse-item`
   (header = title+status+signature; expand to read `.ant-collapse-content-box`). **Assert every technique's
   signature matches the seeded birth date — this is the no-串盘 check.** Confirm non-empty content + "已就绪".
   For the current chart side this means the 9 wired techniques:
   `astrochart`, `indiachart`, `bazi`, `ziwei`, `firdaria`, `primarydirect`, `guolao`, `suzhan`, `germany`.
8. **事盘 check:** a 六爻 case shows its卦; adding 奇门 shows "缺失"; never a fresh re-cast.
9. **Markdown check:** assistant messages render through `marked` + `DOMPurify`; verify `<strong>/<h*>/<ul>/<table>`
   appear and there are **zero literal `**`** markers in the rendered report. Do not remove sanitize.
10. **Layout check:** 系统提示 sits in the right column above 挂载上下文; the toolbar buttons (刷新案例/新对话/…)
   sit at the bottom-left of 发送分析.

## Release to GitHub

This is a **manual, macOS-signed** pipeline (no CI auto-release on tag). Full ordered runbook + checklists are in
`docs/ai-analysis-context-and-markdown.md` (§ Release runbook). Summary:

1. Bump version in lockstep: `Horosa_Desktop_Installer/{package.json, src-tauri/Cargo.toml, src-tauri/tauri.conf.json}`
   + `CITATION.cff`; bump `Horosa_Desktop_Installer/config/release_config.json` `runtimeVersion` (`-runtime<N>`,
   reset to `-runtime1` on app bump). Append a `UPGRADE_LOG.md` entry.
2. Run the pre-release gates: harness JSON, focused tests, clean sequential `npm run build` then `npm run build:file`,
   browser AIAnalysis smoke, clean-env local startup smoke.
3. `git commit -m "release: prepare vX.Y.Z beta"` and push `main` after validation, unless the user explicitly asks
   for an earlier main push.
4. `cd Horosa_Desktop_Installer && ./scripts/check_apple_signing_prereqs.sh`.
5. `HOROSA_PUBLIC_DISTRIBUTION=1 ./scripts/build_desktop_release.sh` (the single build + sign + notarize + staple step).
6. `HOROSA_DESKTOP_SKIP_REBUILD=1 ./scripts/verify_desktop_packaging.sh`,
   `./scripts/verify_runtime_backend_boot.sh --timeout 300`, and
   `./scripts/verify_public_distribution_readiness.sh`.
   - **Gotcha:** `verify_desktop_packaging.sh` hard-exits (`exit 1`) unless it finds a python with Playwright
     installed — it drives a headless chromium for the launcher console-state check. None of the default pythons
     ship it. Make a throwaway venv (`python3 -m venv /tmp/pw && /tmp/pw/bin/pip install playwright &&
     /tmp/pw/bin/python -m playwright install chromium`) and pass `HOROSA_PLAYWRIGHT_PYTHON=/tmp/pw/bin/python`.
     The other two gates need no Playwright.
7. `HOROSA_PUBLIC_DISTRIBUTION=1 ./scripts/publish_github_release.sh` (needs `GITHUB_TOKEN` **or** a working
   `git credential` for github.com; uploads existing assets and creates/updates both the app tag/release and runtime
   tag/release). Do **not** manually `git tag` afterward unless this script explicitly failed before creating tags.
   - Publish **re-runs** `verify_desktop_packaging.sh` (so it needs Playwright again) unless you pass
     `HOROSA_SKIP_VERIFY=1`. Safe to skip only when you just ran that gate on the same unmodified `dist/` bytes;
     `HOROSA_PUBLIC_DISTRIBUTION=1` still enforces the fast signed-readiness check before upload.
   - A brand-new `-runtimeN` tag uploads cleanly. `HOROSA_FORCE_RUNTIME_UPLOAD=1` is only needed when the
     `release_config.json` runtime tag already exists remotely **and** its payload sha changed.
8. Post-publish verification is mandatory:
   `git ls-remote --heads --tags origin main refs/tags/vX.Y.Z refs/tags/vX.Y.Z-runtimeN`,
   `gh release view vX.Y.Z`, `gh release view vX.Y.Z-runtimeN`, fetch the latest
   `horosa-latest.json`, then run `./scripts/verify_github_release_end_to_end.sh`.

Build/sign/publish/push are consequential and deliberately NOT auto-approved in `.claude/settings.json` — confirm
with the user before running them. Never `git push --force` to main.
