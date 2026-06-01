# Contributing to Horosa

中文说明：[CONTRIBUTING_ZH.md](CONTRIBUTING_ZH.md)

Thanks for helping improve Horosa. This repository is being prepared for a formal open-source release, but it already behaves like a real product repository: a shared web/app frontend, local Java and Python services, a desktop shell, AIAnalysis, local-first storage, release automation, and regression scripts all live together here.

Good contributions keep that system understandable, verifiable, and safe to ship.

## Ways To Contribute

- report a reproducible bug
- improve docs, architecture notes, or release guidance
- add tests or stabilize an existing workflow
- improve AIAnalysis behavior, provider compatibility, or recovery flows
- improve build, packaging, or diagnostics without weakening user safety

## Working Principles

- Prefer local-first and file-first behavior unless the product clearly requires a network dependency.
- Prefer additive, reviewable, reversible changes over sweeping rewrites.
- Keep web and app behavior aligned unless a platform-specific difference is intentional and documented.
- If a change touches AI prompts, schemas, provider contracts, exports, backups, storage, or migrations, document the contract change in the pull request.
- Do not fabricate release status, benchmarks, compatibility claims, or security guarantees.

## What To Read First

- [README.md](README.md)
- [README_EN.md](README_EN.md)
- [README_ZH.md](README_ZH.md)
- [PROJECT_STRUCTURE.md](PROJECT_STRUCTURE.md)
- [Horosa_Desktop_Installer/README.md](Horosa_Desktop_Installer/README.md)

## Local Setup

### Frontend

```bash
cd Horosa-Web/astrostudyui
npm ci
npm test -- --runInBand
npm run build
npm run build:file
```

### Backend

```bash
cd Horosa-Web/astrostudysrv/boundless
mvn test -DskipTests=false

cd ../astrostudy
mvn test -DskipTests=false
```

If Maven dependencies are missing in a clean environment, install the internal dependency chain first:

```bash
cd Horosa-Web/astrostudysrv/boundless && mvn -DskipTests install
cd ../basecomm && mvn -DskipTests install
cd ../image && mvn -DskipTests install
cd ../astrostudy && mvn test -DskipTests=false
```

### Full Local Runtime

```bash
cd Horosa-Web
./start_horosa_local.sh
./verify_horosa_local.sh
./stop_horosa_local.sh
```

### Desktop Shell

```bash
cd Horosa_Desktop_Installer
cargo check --manifest-path src-tauri/Cargo.toml
cargo test --manifest-path src-tauri/Cargo.toml
./scripts/verify_desktop_packaging.sh
```

## Before You Start A Larger Change

Read the relevant surface first:

- AIAnalysis UI or behavior:
  - `Horosa-Web/astrostudyui/src/components/aianalysis/`
  - `Horosa-Web/astrostudyui/src/utils/aiAnalysis*.js`
- AI provider or extraction behavior:
  - `Horosa-Web/astrostudyui/src/services/aianalysis.js`
  - `Horosa-Web/astrostudyui/src/utils/aiAnalysis*.js`
  - `Horosa-Web/astrostudysrv/astrostudy/src/main/java/spacex/astrostudy/service/AIAnalysis*.java`
- runtime / packaging:
  - `Horosa_Desktop_Installer/`
  - `Horosa_Desktop_Installer/README.md`

## Change Expectations

### For Code Changes

- explain the user-facing effect, not just the file diff
- add or update tests when logic changes
- keep error messages actionable
- preserve backward compatibility for stored data, export formats, and provider ids when practical

### For UI Changes

- include screenshots when practical
- confirm scroll behavior, empty states, and modal overflow
- confirm the same user flow still works in both web and app modes

### For AIAnalysis Changes

Call out whether your change affects:

- layout and scroll behavior
- provider presets or protocol-family mapping
- stream event handling
- IndexedDB stores or schema version
- prompt layering and clipping
- RAG thresholds, chunking, or embedding behavior
- export / backup format
- desktop import / export bridge behavior

## Pull Request Checklist

- [ ] Relevant tests were run locally.
- [ ] `git diff --check` passes.
- [ ] Secrets, local paths, and temporary files were scrubbed.
- [ ] Docs were updated if the workflow, contract, or developer entry changed.
- [ ] Screenshots were attached for meaningful UI changes.
- [ ] Any AIAnalysis contract change is explicitly described.

## Sensitive Areas

Extra care is expected when changing:

- `Horosa-Web/astrostudyui/src/components/aianalysis/`
- `Horosa-Web/astrostudyui/src/utils/aiAnalysis*`
- `Horosa-Web/astrostudysrv/astrostudy/src/main/java/spacex/astrostudy/service/AIAnalysis*`
- `Horosa-Web/astrostudysrv/boundless/`
- `Horosa_Desktop_Installer/src-tauri/`

Changes in these areas should include at least one of:

- automated tests
- browser flow verification
- desktop verification
- migration notes

## Security And Privacy

- Do not commit API keys, internal tokens, or machine-specific credentials.
- Do not commit local runtime state, generated installers, private screenshots, or diagnostic logs.
- Do not include private charts or identifiable user data in tests, fixtures, screenshots, or bug reports.
- Route sensitive security findings through [SECURITY.md](SECURITY.md), not public issues.

## Licensing Note

Horosa is now on an explicit AGPL-3.0 open-source release track. The repository-level license is [AGPL-3.0](LICENSE). This change is aligned with the public release stack that integrates Swiss Ephemeris / `pyswisseph`. Third-party subdirectories may continue to carry their own original upstream notices, so do not overwrite those files when preparing contributions.
