# Security Policy

中文说明：[SECURITY_ZH.md](SECURITY_ZH.md)

This repository is being prepared for a formal open-source release. In line with GitHub’s security-policy guidance, this file explains what is in scope and how vulnerabilities should be reported.

## Supported Scope

Security reports are especially relevant for:

- provider API key handling
- local runtime update and switching flows
- installer integrity and desktop bootstrap behavior
- AIAnalysis backup, restore, export, and local persistence
- request signing, sensitive error output, and log redaction
- desktop bridge file import / export paths

## Supported Versions

The current intended support window is:

- the current default branch
- the active `1.2.x` work line
- the latest public release line, once the repository is published

Older private snapshots, personal forks, and heavily modified local builds may be handled on a best-effort basis only.

## Reporting A Vulnerability

Do **not** open a public issue for:

- API key leakage
- installer bypass or runtime tampering
- local data exfiltration
- credential exposure in logs or exports
- code execution concerns

### Preferred Path After Public Launch

Once the public repository is live, the recommended path is:

1. GitHub private vulnerability reporting, enabled in repository settings
2. A dedicated security contact

Current security contact:

- Security email: `maxwelldhx@gmail.com`

### Current Local / Pre-Public Path

Until the repository is fully published with public security settings:

- keep the report private
- prepare a sanitized local report
- include only the minimum data needed to reproduce the issue

Please include:

- affected version, branch, or runtime line
- whether the issue reproduces in web, app, or both
- precise reproduction steps
- impact assessment
- sanitized logs, screenshots, or backup snippets

## Handling Expectations

- sensitive reports should remain private until a fix is available
- public changelogs should avoid detailed exploit instructions before patch release
- any discovered credentials or secrets should be rotated or removed before public publication
- fixes that change storage, exports, provider contracts, or runtime behavior should be documented clearly

## Related Files

- [SUPPORT.md](SUPPORT.md)
- [README.md](README.md)
- [Horosa_Desktop_Installer/README.md](Horosa_Desktop_Installer/README.md)
