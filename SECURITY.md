# Security Policy

## Scope

This repository runs a scheduled pipeline that downloads the public ESMA interim MiCAR register, commits snapshots to `main` and publishes derived files. Security issues in scope include:

- the pipeline code in `src/` and `scripts/`;
- the GitHub Actions workflows, in particular the refresh job that holds write access to `main`;
- anything that could let a crafted register file or a third party alter the recorded history (`data/`) or inject content into the published files (README dashboard, `docs/`, feeds and exports);
- the supply chain: pinned actions and locked dependencies.

Errors in ESMA's register content are not security issues. Please report them with the data error issue template.

## Required Controls

1. Never commit credentials or tokens; the workflows use the built-in `GITHUB_TOKEN` with least-privilege permissions.
2. Keep third-party actions pinned to full commit SHAs.
3. Treat every register value as untrusted text: escape it in HTML, Markdown, XML and CSV output.
4. Do not hand-edit recorded history under `data/`.

## Reporting

Report suspected vulnerabilities privately through the maintainer's GitHub profile contact details. Include the affected path, impact and reproduction steps. Do not open public issues for suspected vulnerabilities or credential leaks.

Only the `main` branch is supported.
