# Windows Codex AGPL Sync Guide

This file is for the Windows-side Codex only.

The Windows repository must mirror the license correction already applied on the macOS repository. Do not treat this as an optional documentation cleanup. Treat it as a release-blocking compliance update.

Target repository:

- `https://github.com/Horace-Maxwell/Horosa-Web-App-comprehensively-improved-Windows.git`

Target branch and release:

- update `main`
- keep the public release version at `v1.2.0`
- do not invent a new version just for the license correction

## Why this change is required

The public Horosa release stack integrates Swiss Ephemeris / `pyswisseph`. That dependency family is not compatible with a repository-level MIT claim in the way the project is currently shipped and published.

Because of that, the Windows repository must switch its repository-level public license from MIT to AGPL-3.0 as well.

## Required file changes

The Windows-side Codex should update all project-owned license metadata and release-facing docs that currently say MIT.

At minimum, update these if they exist in the Windows repo:

- root `LICENSE`
- root `README.md`
- root `README_EN.md`
- root `README_ZH.md`
- root `CONTRIBUTING.md`
- root `CONTRIBUTING_ZH.md`
- root `CITATION.cff`
- app/package metadata such as `package.json`
- Python package metadata such as `setup.py`
- desktop installer metadata if a separate package manifest exists

## Exact policy to apply

Use this repository-level policy:

- public repository license: `AGPL-3.0`
- package metadata SPDX string: `AGPL-3.0-only`

That means:

- `LICENSE` should contain the full GNU Affero General Public License v3 text
- README license badges should say `AGPL-3.0`
- package manifests should use `AGPL-3.0-only`
- citation metadata should use `AGPL-3.0-only`

## README requirements

Do not rewrite the whole README.

Keep the existing structure and project story intact.

Only make the minimum licensing sync needed:

1. Replace the top license badge from MIT to AGPL-3.0.
2. Add a short licensing note near the top release summary section.
3. State clearly that:
   - the public repository is now under AGPL-3.0
   - the reason is Swiss Ephemeris / `pyswisseph` integration
   - third-party subdirectories may keep their own upstream notices

Recommended wording:

> Licensing note: the public repository is now distributed under AGPL-3.0 because the released stack integrates Swiss Ephemeris / `pyswisseph`. Third-party subdirectories keep their own upstream notices.

If the repo is bilingual, mirror this note in Chinese.

## CONTRIBUTING requirements

Update the licensing section so contributors understand:

- the repository-level license is AGPL-3.0
- this is tied to the public release stack and dependency reality
- they must not overwrite third-party upstream license files

## What must NOT be changed

Do not mass-rewrite third-party or upstream submodules just because the repository-level license changed.

Examples of files that should usually be left alone:

- vendored upstream `LICENSE` files
- third-party `setup.py` metadata from upstream projects
- dependency lockfiles
- archived reference modules copied from other projects

Rule:

- change project-owned release-facing metadata
- do not rewrite upstream notices inside third-party code

## Release and GitHub sync steps

After the Windows-side Codex applies the license changes:

1. run the repository tests that already exist
2. confirm the README license badge and wording are correct
3. confirm no third-party license files were unintentionally changed
4. commit to `main`
5. push `main`
6. update the GitHub Release `v1.2.0` in the Windows repository if that release already exists
7. keep the release version name as `v1.2.0`

Do not create `v1.2.1` just for this sync unless the founder explicitly asks for it.

## Release asset rules

Do not upload unnecessary large reproducible files to Git.

Do not commit:

- build outputs
- `dist/`
- `target/`
- `node_modules/`
- caches
- logs
- local runtimes
- generated screenshots that are not intentionally curated repo assets
- temporary archives

Do keep only the files that belong in source control:

- source code
- installer scripts
- release automation scripts
- curated README screenshots if the Windows repo already tracks them intentionally
- required runtime metadata
- documentation

## Final verification checklist

Before pushing, the Windows-side Codex must confirm all of the following:

- root `LICENSE` is AGPL-3.0 text
- README badge says AGPL-3.0
- README top section includes the licensing note
- `CONTRIBUTING` no longer says MIT
- `CITATION.cff` no longer says MIT
- package metadata no longer says MIT
- no accidental changes were made to third-party upstream license files
- working tree does not contain large generated garbage
- `main` is updated
- GitHub Release `v1.2.0` still exists and matches the current public line

## Non-negotiable rule

The Windows repository must end up telling the same licensing story as the macOS repository:

- repository-level public license: AGPL-3.0
- release line remains `v1.2.0`
- documentation stays stable
- only the minimum necessary release-facing files are changed
