# Contributing

Thanks for helping keep the register's memory accurate. The most useful contributions are reports of data errors and of changes to ESMA's source files; code changes are welcome too.

## The review-gate rule

This repository records facts about a public register. It makes **no assessment of any named issuer, offeror or crypto-asset service provider**, and contributions must keep it that way:

- Do not add statements that a named entity is non-compliant, deficient, unlawful or otherwise assessed: not in code, data, tests, fixtures, issues, pull request descriptions or commit messages.
- Findings about named entities (for example, white paper lint results) are only published after a human legal review of each finding. That review-gated work lives in the [micar-whitepaper-linter](https://github.com/sebastianfoerste/micar-whitepaper-linter) repository, not here.
- New test fixtures use synthetic names and LEIs.
- Changes to public claims (the README text, `editions/`, `docs/methodology.md`, `docs/regulatory-claim-ledger.md`) need the maintainer's legal review before merge. Say so in the pull request.

## Reporting a data error

Open a [data error](https://github.com/sebastianfoerste/micar-register-observatory/issues/new?template=data-error.yml) issue when the observatory's snapshot, changelog, exports or dashboard does not match what ESMA published. Quote the ESMA row and give the snapshot date and the `entry_id`, LEI or DTI.

If ESMA's own file is wrong, the correction has to come from ESMA or the national competent authority. The observatory records it once it appears in the export.

## Reporting a source change

ESMA announced that the interim CSV register would be replaced by its IT systems; until then the files can move, gain or lose columns, or change format. Open a [source change](https://github.com/sebastianfoerste/micar-register-observatory/issues/new?template=source-change.yml) issue when that happens. The refresh fails closed on missing columns and on suspicious row counts, so a failed weekly run is often the first sign.

## Data rules

- **Never hand-edit recorded history**: `data/snapshots/`, `data/latest.json`, `data/changelog.jsonl`, `data/quarantine/` and `data/raw/` are written by the pipeline only.
- **Generated files are regenerated, not edited**: the README dashboard block, `docs/feed.json`, `docs/changes.atom`, `data/exports/` and `digests/` come from `make render` or the weekly refresh, and the data section of an edition and `docs/index.html` from `make report`.
- **Schema changes only add fields.** [eu-reg-mcp](https://github.com/sebastianfoerste/eu-reg-mcp) reads `data/latest.json` and `data/changelog.jsonl` from `main`. Never remove or rename a field or change its meaning; update `contracts/` and `docs/data-dictionary.md` in the same pull request. `tests/test_contract.py` fails when a field the code writes is missing from the contracts.

## Development

```bash
make install     # uv sync --extra dev
make check       # ruff, mypy and the offline test suite
```

The test suite runs offline against the fixtures in `tests/fixtures/`. They carry ESMA's real column headers with synthetic rows. `make refresh` fetches the live register and rewrites `data/`, so only run it when you mean to.

Keep commits small and focused, with plain messages that say what changed and why.
