# MiCAR Register Observatory

A living dashboard of the **ESMA interim MiCAR register**. Every Monday a scheduled job pulls the public register exports (crypto-asset white papers under Titles II–IV, authorised CASPs, non-compliant entities), diffs them against the last snapshot, and rewrites the dashboard below: new filings, changed entries, entries no longer listed (in records after the 2026-10-12 snapshot, counted as removed only after two consecutive absences), and which file formats the white-paper links point to, judged by the URL alone.

The register is public by law: Art. 109 VO (EU) 2023/1114 (MiCAR) requires ESMA to establish a public register of crypto-asset white papers, of issuers of asset-referenced and e-money tokens, and of crypto-asset service providers, and Art. 110 MiCAR a register of entities that provide crypto-asset services in violation of Art. 59 or 61 (the non-compliant entities). The duty to make each white paper available in a machine-readable format sits in the white-paper provisions, Art. 6(10), 19(9) and 51(9) MiCAR, with the forms, formats and templates set by Commission Implementing Regulation (EU) 2024/2984, which applies from 23 December 2025. This repository makes the register's weekly movement visible: what appeared, what changed, what disappeared.

## Dashboard

<!-- dashboard:start -->
**Register snapshot: 2026-10-19** (refreshed weekly from the public ESMA interim MiCAR register)

### Register totals

| Register | Rows | Entities | Source status |
| --- | ---: | ---: | --- |
| [White papers — other crypto-assets (Title II)](https://www.esma.europa.eu/sites/default/files/2024-12/OTHER.csv) | 1049 | 657 | ok (file modified 2026-10-16) |
| [White papers — e-money tokens (Title IV)](https://www.esma.europa.eu/sites/default/files/2024-12/EMTWP.csv) | 50 | 25 | ok (file modified 2026-10-16) |
| [White papers — asset-referenced tokens (Title III)](https://www.esma.europa.eu/sites/default/files/2024-12/ARTZZ.csv) | 0 | 0 | ok (file modified 2025-02-14) |
| [Authorised crypto-asset service providers (CASPs)](https://www.esma.europa.eu/sites/default/files/2024-12/CASPS.csv) | 378 | 375 | ok (file modified 2026-10-16) |
| [Non-compliant entities flagged by NCAs](https://www.esma.europa.eu/sites/default/files/2024-12/NCASP.csv) | 178 | 175 | ok (file modified 2026-10-16) |

Rows are lines of the register export; entities are distinct LEIs, or names where a row has none. One entity can have several rows: several white papers, or a second CASP authorisation.

CASP register: 375 firms in 378 rows, 2 of them with a withdrawal date (`ac_authorisationEndDate`).

### White paper format coverage

Classified by link shape only; a format is a deep-lint candidate, not a verified fact, until the document is fetched.

| Linked format | Count | Deep-lint candidate |
| --- | ---: | --- |
| No recognised file extension (bare domain, landing page or other page) | 660 | no |
| PDF | 264 | no |
| XHTML / HTML | 173 | yes |
| No link in register | 2 | no |

### Home Member States (white papers)

| Member State | White papers |
| --- | ---: |
| IE | 398 |
| MT | 173 |
| DE | 170 |
| NL | 92 |
| LI | 73 |
| LU | 59 |
| FR | 38 |
| LV | 15 |
| AT | 10 |
| FI | 10 |
| ...and 17 more | |

### Changes in this snapshot (2026-10-19)

| Change | Register | Entity | MS | Link |
| --- | --- | --- | --- | --- |
| added | other-wp | Abloxx Token Ltd. | CY | [https://abloxx.com/en](https://abloxx.com/en) |
| added | other-wp | Falu Brick Commerce Limited | CY | [https://xyo.network/papers/mica-white-paper\]](https://xyo.network/papers/mica-white-paper%5D) |
| changed | other-wp | Planck Network ($PLANCK) | CYPRUS | [https://plancknetwork.com/whitepaper.pdf](https://plancknetwork.com/whitepaper.pdf) |
| added | other-wp | Extended Ecosystem Limited | CY | [https://token.extended.exchange/whitepaper](https://token.extended.exchange/whitepaper) |
| added | other-wp | Crypto Risk Metrics GmbH | DE | [https://white-paper.crypto-risk-metrics.com/en/bankrcoin-...](https://white-paper.crypto-risk-metrics.com/en/bankrcoin-ffg-6xspzjjtx/index.html) |
| changed | other-wp | Th QAIT Association | FR | [https://www.qait.ch](https://www.qait.ch) |
| added | other-wp | TCG-VAULT | FR | [https://www.tcg-vault.io/livre-blanc-mica](https://www.tcg-vault.io/livre-blanc-mica) |
| added | other-wp | TCG-VAULT | FR | [https://www.tcg-vault.io/livre-blanc-mica](https://www.tcg-vault.io/livre-blanc-mica) |
| added | other-wp | TCG-VAULT | FR | [https://www.tcg-vault.io/livre-blanc-mica](https://www.tcg-vault.io/livre-blanc-mica) |
| added | other-wp | TCG-VAULT | FRANCE | [https://www.tcg-vault.io/livre-blanc-mica](https://www.tcg-vault.io/livre-blanc-mica) |
| added | other-wp | Beldex International Foundation | IE | [https://www.beldex.io/BDX\_MiCA\_Whitepaper\_V2.0.xhtml](https://www.beldex.io/BDX_MiCA_Whitepaper_V2.0.xhtml) |
| added | other-wp | OD3 (BVI) Ltd | IE | [www.bluff.com/whitepaper](https://www.bluff.com/whitepaper) |
| added | other-wp | Tria Labs Limited | IE | [https://www.tria.so/legal/micar](https://www.tria.so/legal/micar) |
| added | other-wp | AlloX Ltd | IE | [https://www.allox.ai/micar-whitepaper](https://www.allox.ai/micar-whitepaper) |
| added | other-wp | Hibachi PTE Ltd | NL | [https://hibachi.micarwhitepapers.eu](https://hibachi.micarwhitepapers.eu) |
| added | other-wp | Crispy Holdings Ltd | NL | [https://tendies.micarwhitepapers.eu](https://tendies.micarwhitepapers.eu) |
| missing | other-wp | Abloxx Token Ltd. | CY | [https://abloxx.com/en/details](https://abloxx.com/en/details) |
| missing | other-wp | Falu Brick Commerce Limited | CY | [https://xyo.network/papers/mica-white-paper](https://xyo.network/papers/mica-white-paper) |
| missing | other-wp | Crypto Risk Metrics GmbH | DE | [https://crypto-risk-metrics.com/en/white-paper-bankrcoin-...](https://crypto-risk-metrics.com/en/white-paper-bankrcoin-ffg-6xspzjjtx/) |
| changed | casps | Bitpanda GmbH | AT |  |
| changed | casps | Bybit EU GmbH | AT |  |
| changed | casps | Cryptonow GmbH | AT |  |
| changed | casps | AMINA (Austria) AG | AT |  |
| changed | casps | FIOR Digital GmbH | AT |  |
| changed | casps | KuCoin EU Exchange GmbH | AT |  |
| ...and 382 more (see `data/changelog.jsonl`) | | | | |

`missing`: not in this export for the first time. `removed`: not in two consecutive exports. `restored`: listed again after an absence.
<!-- dashboard:end -->

## Quarterly report: The State of the MiCAR Register

A quarterly data report built from these snapshots. It answers one question with numbers instead of anecdote: how many white-paper links on the register end in an XHTML/HTML, JSON or DOCX file extension, rather than pointing to a PDF or to a URL with no recognised file extension? MiCAR requires white papers to be made available in a machine-readable format (Art. 6(10), 19(9) and 51(9)); the report measures a URL-based proxy for that, not compliance.

Latest edition: **[editions/2026-Q3.md](editions/2026-Q3.md)**

| Edition | Snapshot | Headline |
| --- | --- | --- |
| [2026-Q3](editions/2026-Q3.md) | 2026-09-21 | 13.8% of white papers link to a URL ending in .xhtml/.html/.htm, .json or .docx (URL proxy; iXBRL not verified); 61.1% link a URL with no recognised file extension |

Each edition is built from one dated snapshot committed in `data/snapshots/`, so its numbers are reproducible from a commit. The narrative in each edition is human-authored; the tables between the `data:start` / `data:end` markers are generated by `make report`, which also writes `docs/index.html`. `make report` builds the newest file in `editions/` and is meant for a new quarter's edition: while that file's data section is empty, it is filled from `data/latest.json`. Once an edition's data section records a snapshot date, `make report` rebuilds it from that dated snapshot, so its numbers do not move; `uv run python -m report build --use-latest` refills it from `data/latest.json` instead. To rebuild an existing edition, including 2026-Q3, from its own snapshot: `uv run python -m report build --edition 2026-Q3 --fixture data/snapshots/2026-09-21.json`. `docs/index.html` is the newest edition's page, so a build rewrites it only when the edition it builds is the newest. The tests check every edition whose data section is filled against the snapshot named in its row of the table above (`tests/test_editions.py`), and the weekly refresh runs those tests before it fetches, so add a new edition's row, with the snapshot date of `data/latest.json`, before its data section is filled. The report states facts about a public register and makes no assessment of any named issuer. It moved here on 25 September 2026 from the separate `state-of-the-micar-register` repository.

## Run it

```bash
git clone https://github.com/sebastianfoerste/micar-register-observatory
cd micar-register-observatory
make install && make test
make refresh
```

`make refresh` fetches the five register CSVs from esma.europa.eu, writes a dated snapshot under `data/snapshots/`, appends changes to `data/changelog.jsonl`, and regenerates this README and `docs/feed.json`. `make report` fills a new quarter's edition (the newest file in `editions/`) from `data/latest.json`, and rebuilds an edition that already records a snapshot from that snapshot. `make freshness` fails closed when `data/latest.json` is missing a register partition, records a failed fetch, or is older than 14 days; the snapshot contract is `contracts/micar-register.snapshot.v1.schema.json`. The test suite runs offline against committed fixtures.

## What this tracks

- **New, changed, missing, removed and restored register entries** per weekly snapshot. A row is `missing` the first time an export does not list it, `removed` once it is absent from two consecutive exports, and `restored` if it is listed again. Records up to the 2026-10-12 snapshot (record version 1, which includes every `removed` record so far) used `removed` for a first absence and `added` for a relisting; see [docs/methodology.md](docs/methodology.md#change-detection). A removal can be a withdrawal, an upstream correction or a changed white-paper URL; the export does not say which.
- **Format coverage**: how many linked white papers are XHTML/HTML, JSON, or DOCX (candidates for deterministic linting with [micar-whitepaper-linter](https://github.com/sebastianfoerste/micar-whitepaper-linter)) versus PDF or a URL with no recognised file extension (a bare domain, a landing page, or a document served without one). Classification is by link shape only and is marked as candidate, not verified, until a document is fetched.
- **Machine-readable feed**: `docs/feed.json` carries the current totals and recent changes for anyone building on top.

Deep-lint findings on individual white papers are deliberately **not** auto-published here. Rule findings against named issuers go through human legal review first; the review-gated study lives in the [linter repository](https://github.com/sebastianfoerste/micar-whitepaper-linter). A flag from a deterministic rule is a candidate gap in extracted text, not a confirmed deficiency by the named issuer.

## Method and limits

See [docs/methodology.md](docs/methodology.md) for sources, normalization, change detection, and known limitations. Two that matter most: the observatory reflects the register exports as published (upstream corrections appear as "changed" entries), and format classification is a URL-shape heuristic until documents are fetched.

## Legal

The underlying data is ESMA's public register. This repository records factual observations about that register; it contains no legal assessment of any issuer or service provider and is not legal advice. Code is MIT-licensed.
