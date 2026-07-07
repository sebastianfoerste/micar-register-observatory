# MiCAR Register Observatory

A living dashboard of the **ESMA interim MiCAR register**. Every Monday a scheduled job pulls the public register exports (crypto-asset white papers under Titles II–IV, authorised CASPs, non-compliant entities), diffs them against the last snapshot, and rewrites the dashboard below: new filings, changed entries, withdrawals, and how many white papers are published in a machine-readable format.

The register is public by law — Art. 109 Abs. 1 VO (EU) 2023/1114 (MiCAR) requires ESMA to publish white papers and authorisations in a machine-readable register. This repository makes the register's weekly movement visible: what appeared, what changed, what disappeared.

## Dashboard

<!-- dashboard:start -->
**Register snapshot: 2026-07-07** (refreshed weekly from the public ESMA interim MiCAR register)

### Register totals

| Register | Entries | Source status |
| --- | ---: | --- |
| [White papers — other crypto-assets (Title II)](https://www.esma.europa.eu/sites/default/files/2024-12/OTHER.csv) | 912 | ok |
| [White papers — e-money tokens (Title IV)](https://www.esma.europa.eu/sites/default/files/2024-12/EMTWP.csv) | 41 | ok |
| [White papers — asset-referenced tokens (Title III)](https://www.esma.europa.eu/sites/default/files/2024-12/ARTZZ.csv) | 0 | ok |
| [Authorised crypto-asset service providers (CASPs)](https://www.esma.europa.eu/sites/default/files/2024-12/CASPS.csv) | 283 | ok |
| [Non-compliant entities flagged by NCAs](https://www.esma.europa.eu/sites/default/files/2024-12/NCASP.csv) | 162 | ok |

### White paper format coverage

Classified by link shape only; a format is a deep-lint candidate, not a verified fact, until the document is fetched.

| Linked format | Count | Deep-lint candidate |
| --- | ---: | --- |
| Unspecified (landing page or bare domain) | 584 | no |
| PDF | 254 | no |
| XHTML / HTML | 114 | yes |
| No link in register | 1 | no |

### Home Member States (white papers)

| Member State | White papers |
| --- | ---: |
| IE | 340 |
| MT | 159 |
| DE | 145 |
| NL | 74 |
| LI | 72 |
| LU | 53 |
| FR | 32 |
| LV | 14 |
| AT | 9 |
| FI | 9 |
| ...and 11 more | |

### Changes in this snapshot (2026-07-07)

- `other-wp`: baseline established with 912 entries.
- `emt-wp`: baseline established with 41 entries.
- `art-wp`: baseline established with 0 entries.
- `casps`: baseline established with 283 entries.
- `ncasp`: baseline established with 162 entries.
<!-- dashboard:end -->

## Run it

```bash
git clone https://github.com/sebastianfoerste/micar-register-observatory
cd micar-register-observatory
make install && make test
make refresh
```

`make refresh` fetches the five register CSVs from esma.europa.eu, writes a dated snapshot under `data/snapshots/`, appends changes to `data/changelog.jsonl`, and regenerates this README and `docs/feed.json`. The test suite runs offline against committed fixtures.

## What this tracks

- **New, changed, and removed register entries** per weekly snapshot — including white paper withdrawals, which the register itself does not announce.
- **Format coverage**: how many linked white papers are XHTML/HTML, JSON, or DOCX (candidates for deterministic linting with [micar-whitepaper-linter](https://github.com/sebastianfoerste/micar-whitepaper-linter)) versus PDF or a bare landing-page domain. Classification is by link shape only and is marked as candidate, not verified, until a document is fetched.
- **Machine-readable feed**: `docs/feed.json` carries the current totals and recent changes for anyone building on top.

Deep-lint findings on individual white papers are deliberately **not** auto-published here. Rule findings against named issuers go through human legal review first; the review-gated study lives in the [linter repository](https://github.com/sebastianfoerste/micar-whitepaper-linter). A flag from a deterministic rule is a candidate gap in extracted text, not a confirmed deficiency by the named issuer.

## Method and limits

See [docs/methodology.md](docs/methodology.md) for sources, normalization, change detection, and known limitations. Two that matter most: the observatory reflects the register exports as published (upstream corrections appear as "changed" entries), and format classification is a URL-shape heuristic until documents are fetched.

## Legal

The underlying data is ESMA's public register. This repository records factual observations about that register; it contains no legal assessment of any issuer or service provider and is not legal advice. Code is MIT-licensed.
