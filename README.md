# MiCAR Register Observatory

A living dashboard of the **ESMA interim MiCAR register**. Every Monday a scheduled job pulls the public register exports (crypto-asset white papers under Titles II–IV, authorised CASPs, non-compliant entities), diffs them against the last snapshot, and rewrites the dashboard below: new filings, changed entries, withdrawals, and how many white papers are published in a machine-readable format.

The register is public by law — Art. 109 Abs. 1 VO (EU) 2023/1114 (MiCAR) requires ESMA to publish white papers and authorisations in a machine-readable register. This repository makes the register's weekly movement visible: what appeared, what changed, what disappeared.

## Dashboard

<!-- dashboard:start -->
**Register snapshot: 2026-09-21** (refreshed weekly from the public ESMA interim MiCAR register)

### Register totals

| Register | Entries | Source status |
| --- | ---: | --- |
| [White papers — other crypto-assets (Title II)](https://www.esma.europa.eu/sites/default/files/2024-12/OTHER.csv) | 998 | ok |
| [White papers — e-money tokens (Title IV)](https://www.esma.europa.eu/sites/default/files/2024-12/EMTWP.csv) | 49 | ok |
| [White papers — asset-referenced tokens (Title III)](https://www.esma.europa.eu/sites/default/files/2024-12/ARTZZ.csv) | 0 | ok |
| [Authorised crypto-asset service providers (CASPs)](https://www.esma.europa.eu/sites/default/files/2024-12/CASPS.csv) | 352 | ok |
| [Non-compliant entities flagged by NCAs](https://www.esma.europa.eu/sites/default/files/2024-12/NCASP.csv) | 174 | ok |

### White paper format coverage

Classified by link shape only; a format is a deep-lint candidate, not a verified fact, until the document is fetched.

| Linked format | Count | Deep-lint candidate |
| --- | ---: | --- |
| Unspecified (landing page or bare domain) | 640 | no |
| PDF | 262 | no |
| XHTML / HTML | 144 | yes |
| No link in register | 1 | no |

### Home Member States (white papers)

| Member State | White papers |
| --- | ---: |
| IE | 377 |
| MT | 167 |
| DE | 156 |
| NL | 88 |
| LI | 72 |
| LU | 59 |
| FR | 35 |
| LV | 14 |
| AT | 10 |
| FI | 10 |
| ...and 15 more | |

### Changes in this snapshot (2026-09-21)

| Change | Register | Entity | MS | Link |
| --- | --- | --- | --- | --- |
| added | other-wp | Alphamind OÜ | EE | [https://alphamind.xyz](https://alphamind.xyz) |
| added | other-wp | Playnance OÜ | EE | [https://www.playnance.com/Annex%202.%20Whitepaper%20Draft...](https://www.playnance.com/Annex%202.%20Whitepaper%20Draft.xhtml) |
| added | other-wp | Standard Technologies Pte. Ltd. | IE | [awe.micarwhitepapers.eu](https://awe.micarwhitepapers.eu) |
| added | other-wp | Puple AI Inc. | IE | [https://memecore.com/micar-whitepaper](https://memecore.com/micar-whitepaper) |
| added | other-wp | LN Technology (TIV) Limited | IE | [https://cdn.prod.website-files.com/67ea875e6d5ae597a69440...](https://cdn.prod.website-files.com/67ea875e6d5ae597a69440a1/6a58d844e9e059c09c086474_KAIO_MiCA_WhitePaper_4_21_2026.pdf) |
| added | other-wp | BLOCKv Foundation, to be renamed Dual Foundation | IE | [www.dual.org/mica](https://www.dual.org/mica) |
| changed | other-wp | Fuse Crypto Limited | LU | [https://www.fuseenergy.com/mica-whitepaper](https://www.fuseenergy.com/mica-whitepaper) |
| added | other-wp | Bitstamp Europe S.A. | LU | [https://assets.bitstamp.net/docs/whitepaper/PONS_2026_08_...](https://assets.bitstamp.net/docs/whitepaper/PONS_2026_08_31.xhtml) |
| added | other-wp | Bitstamp Europe S.A. | LU | [https://assets.bitstamp.net/docs/whitepaper/BILL_2026_09_...](https://assets.bitstamp.net/docs/whitepaper/BILL_2026_09_03.xhtml) |
| added | other-wp | Nillion Association | MT | [https://nillion.com/legal/mica/whitepaper/](https://nillion.com/legal/mica/whitepaper/) |
| added | other-wp | Elliot Technologies, Inc | MT | [https://my.okx.com/whitepaper/lighter-lit.xhtml](https://my.okx.com/whitepaper/lighter-lit.xhtml) |
| changed | emt-wp | AllUnity GmbH | DE | [https://allunity.com/whitepaper](https://allunity.com/whitepaper) |
| added | emt-wp | BISON BANK, S.A. | PT | [https://bisonbank.com/wp-content/uploads/2026/04/Bison-Ba...](https://bisonbank.com/wp-content/uploads/2026/04/Bison-Bank-EUB-White-Paper_20260312-1.pdf) |
| added | casps | FF Digital EOOD | BG |  |
| changed | casps | Deutsche WertpapierService Bank AG | DE |  |
| changed | casps | DLT Securities GmbH | DE |  |
| added | casps | Volksbank Olpe-Wenden-Drolshagen eG | DE |  |
| added | casps | Deutsche Bank Aktiengesellschaft | DE |  |
| added | casps | Raiffeisenbank Goldener Steig-Dreisessel eG | DE |  |
| added | casps | Vereinigte VR Bank eG | DE |  |
| added | casps | Vereinigte Volksbank Raiffeisenbank eG, Reinheim | DE |  |
| changed | casps | Januar ApS | DK |  |
| changed | casps | SOCIETE GENERALE - FORGE | FR |  |
| changed | casps | RCUBE ASSET MANAGEMENT | FR |  |
| changed | casps | LEONOD SARL | FR |  |
| ...and 9 more (see `data/changelog.jsonl`) | | | | |
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
