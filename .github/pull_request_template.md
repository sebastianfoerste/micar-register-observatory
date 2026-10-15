## What and why

<!-- What does this change, and why? Link the issue if there is one. -->

## Checklist

- [ ] `make check` passes (ruff, mypy and the offline tests).
- [ ] Schema changes only add fields and `contracts/` is updated. (`eu-reg-mcp` reads `data/latest.json` and `data/changelog.jsonl` from `main`.)
- [ ] No hand edits to recorded history (`data/snapshots/`, `data/latest.json`, `data/changelog.jsonl`, `data/quarantine/`) or to generated files.
- [ ] No assessment of any named issuer or service provider in code, data, tests, fixtures or this description; fixtures use synthetic names.
- [ ] Public claims changed (README text, `editions/`, `docs/methodology.md`, the claim ledger)? Then this needs the maintainer's legal review before merge.
