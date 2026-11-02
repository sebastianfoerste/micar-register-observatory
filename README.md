# MiCAR Register Observatory

A living dashboard of the **ESMA interim MiCAR register**. Every Monday a scheduled job pulls the public register exports (crypto-asset white papers under Titles II–IV, authorised CASPs, non-compliant entities), diffs them against the last snapshot, and rewrites the dashboard below: new filings, changed entries, withdrawals, and how many white papers are published in a machine-readable format.

The register is public by law — Art. 109 Abs. 1 VO (EU) 2023/1114 (MiCAR) requires ESMA to publish white papers and authorisations in a machine-readable register. This repository makes the register's weekly movement visible: what appeared, what changed, what disappeared.

## Dashboard

<!-- dashboard:start -->
**Register snapshot: 2026-11-02** (refreshed weekly from the public ESMA interim MiCAR register)

### Register totals

| Register | Rows | Entities | Source status |
| --- | ---: | ---: | --- |
| [White papers — other crypto-assets (Title II)](https://www.esma.europa.eu/sites/default/files/2024-12/OTHER.csv) | 1062 | 664 | ok (file modified 2026-10-30) |
| [White papers — e-money tokens (Title IV)](https://www.esma.europa.eu/sites/default/files/2024-12/EMTWP.csv) | 50 | 25 | ok (file modified 2026-10-30) |
| [White papers — asset-referenced tokens (Title III)](https://www.esma.europa.eu/sites/default/files/2024-12/ARTZZ.csv) | 0 | 0 | ok (file modified 2025-02-14) |
| [Authorised crypto-asset service providers (CASPs)](https://www.esma.europa.eu/sites/default/files/2024-12/CASPS.csv) | 392 | 389 | ok (file modified 2026-10-30) |
| [Non-compliant entities flagged by NCAs](https://www.esma.europa.eu/sites/default/files/2024-12/NCASP.csv) | 188 | 185 | ok (file modified 2026-10-30) |

Rows are lines of the register export; entities are distinct LEIs, or names where a row has none. One entity can have several rows: several white papers, or a second CASP authorisation.

CASP register: 389 firms in 392 rows, 2 of them with a withdrawal date (`ac_authorisationEndDate`).

### White paper format coverage

Classified by link shape only; a format is a deep-lint candidate, not a verified fact, until the document is fetched.

| Linked format | Count | Deep-lint candidate |
| --- | ---: | --- |
| Unspecified (landing page or bare domain) | 665 | no |
| PDF | 265 | no |
| XHTML / HTML | 179 | yes |
| No link in register | 3 | no |

### Home Member States (white papers)

| Member State | White papers |
| --- | ---: |
| IE | 398 |
| DE | 175 |
| MT | 173 |
| NL | 97 |
| LI | 74 |
| LU | 60 |
| FR | 39 |
| LV | 15 |
| AT | 10 |
| FI | 10 |
| ...and 15 more | |

### Changes in this snapshot (2026-11-02)

| Change | Register | Entity | MS | Link |
| --- | --- | --- | --- | --- |
| changed | other-wp | SC STEELCOIN GmbH | AT | [https://steelcoin.com/](https://steelcoin.com/) |
| changed | other-wp | Biogena GmbH & Co KG | AT | [www.biogena.com/biox](https://www.biogena.com/biox) |
| changed | other-wp | Planck Network ($PLANCK) | CY | [https://plancknetwork.com/whitepaper.pdf](https://plancknetwork.com/whitepaper.pdf) |
| added | other-wp | Crypto Risk Metrics GmbH | DE | [https://white-paper.crypto-risk-metrics.com/en/spx6900-ff...](https://white-paper.crypto-risk-metrics.com/en/spx6900-ffg-v9fvrlgkc/index.html) |
| added | other-wp | Crypto Risk Metrics GmbH | DE | [https://white-paper.crypto-risk-metrics.com/en/noice-ffg-...](https://white-paper.crypto-risk-metrics.com/en/noice-ffg-z53wmgjqx/index.html) |
| added | other-wp | Crypto Risk Metrics GmbH | DE | [https://white-paper.crypto-risk-metrics.com/en/dolomite-f...](https://white-paper.crypto-risk-metrics.com/en/dolomite-ffg-g6qfn3z7f/index.html) |
| added | other-wp | Crypto Risk Metrics GmbH | DE | [https://white-paper.crypto-risk-metrics.com/en/worldcoin-...](https://white-paper.crypto-risk-metrics.com/en/worldcoin-ffg-bjd0tz8v1/index.html) |
| added | other-wp | Crypto Risk Metrics GmbH | DE | [https://white-paper.crypto-risk-metrics.com/en/pancakeswa...](https://white-paper.crypto-risk-metrics.com/en/pancakeswap-ffg-lz3v3z6fd/index.html) |
| changed | other-wp | TCG-VAULT | FR | [https://www.tcg-vault.io/livre-blanc-mica](https://www.tcg-vault.io/livre-blanc-mica) |
| added | other-wp | AmericanFortress Ltd. | LI | [https://americanfortress.io/documents/AmericanFortress-Mi...](https://americanfortress.io/documents/AmericanFortress-MiCA-Whitepaper.pdf) |
| added | other-wp | Bitstamp Europe S.A. | LU | [https://assets.bitstamp.net/docs/whitepaper/EIGEN\_2026\_10...](https://assets.bitstamp.net/docs/whitepaper/EIGEN_2026_10_21.xhtml) |
| changed | other-wp | ProtoWardo Ltd | NL | [https://docs.wardenprotocol.org/ward/micar-whitepaper](https://docs.wardenprotocol.org/ward/micar-whitepaper) |
| changed | other-wp | Cetus Technology Limited | NL | [https://cetus.micarwhitepapers.eu](https://cetus.micarwhitepapers.eu) |
| added | other-wp | Derive Subsidiary (BVI) Ltd | NL | [https://derive.micarwhitepapers.eu](https://derive.micarwhitepapers.eu) |
| added | other-wp | Aeon 1731 LLC | NL | [https://chump.micarwhitepapers.eu](https://chump.micarwhitepapers.eu) |
| added | other-wp | Zebec Holdings | NL | [https://zebec.io/compliance](https://zebec.io/compliance) |
| added | other-wp | Aggro Axe Ltd. | NL | [https://cambria.micarwhitepapers.eu](https://cambria.micarwhitepapers.eu) |
| added | other-wp | Saturn Holdings (BVI) Limited | NL | [https://whitepaper.saturn-holdings.com](https://whitepaper.saturn-holdings.com) |
| changed | other-wp | Dog Planet AS | NO | [https://www.dogplanet.no/](https://www.dogplanet.no/) |
| changed | other-wp | PALM Token | NO | [http://www.palmeconomy.io](http://www.palmeconomy.io) |
| changed | other-wp | Aprikos Venture AS | NO | [https://venturetoken.io/](https://venturetoken.io/) |
| added | other-wp | Bright Signal Invest AS | NO |  |
| removed | other-wp | Abloxx Token Ltd. | CY | [https://abloxx.com/en/details](https://abloxx.com/en/details) |
| removed | other-wp | Falu Brick Commerce Limited | CY | [https://xyo.network/papers/mica-white-paper](https://xyo.network/papers/mica-white-paper) |
| removed | other-wp | Crypto Risk Metrics GmbH | DE | [https://crypto-risk-metrics.com/en/white-paper-bankrcoin-...](https://crypto-risk-metrics.com/en/white-paper-bankrcoin-ffg-6xspzjjtx/) |
| ...and 107 more (see `data/changelog.jsonl`) | | | | |

`missing`: not in this export for the first time. `removed`: not in two consecutive exports. `restored`: listed again after an absence.
<!-- dashboard:end -->

## Quarterly report: The State of the MiCAR Register

A quarterly data report built from these snapshots. It answers one question with numbers instead of anecdote: how much of the MiCAR register is actually the structured, machine-readable disclosure that Article 109 intends?

Latest edition: **[editions/2026-Q3.md](editions/2026-Q3.md)** · shareable page: **<https://sebastianfoerste.github.io/micar-register-observatory/>**

| Edition | Snapshot | Headline |
| --- | --- | --- |
| [2026-Q3](editions/2026-Q3.md) | 2026-09-21 | 13.8% of white papers machine-readable; 61.1% landing-page only |

Each edition is built from one dated snapshot committed in `data/`, so its numbers are reproducible from a commit. The narrative in each edition is human-authored; the tables between the `data:start` / `data:end` markers are generated by `make report`, which also writes `docs/index.html`. The report states facts about a public register and makes no assessment of any named issuer. It moved here on 25 September 2026 from the separate `state-of-the-micar-register` repository.

## Run it

```bash
git clone https://github.com/sebastianfoerste/micar-register-observatory
cd micar-register-observatory
make install && make test
make refresh
```

`make refresh` fetches the five register CSVs from esma.europa.eu, writes a dated snapshot under `data/snapshots/`, appends changes to `data/changelog.jsonl`, and regenerates this README and `docs/feed.json`. `make report` regenerates the latest edition's data section from `data/latest.json`. `make freshness` fails closed when that snapshot is missing a register partition, records a failed fetch, or is older than 14 days; the snapshot contract is `contracts/micar-register.snapshot.v1.schema.json`. The test suite runs offline against committed fixtures.

## What this tracks

- **New, changed, and removed register entries** per weekly snapshot — including white paper withdrawals, which the register itself does not announce.
- **Format coverage**: how many linked white papers are XHTML/HTML, JSON, or DOCX (candidates for deterministic linting with [micar-whitepaper-linter](https://github.com/sebastianfoerste/micar-whitepaper-linter)) versus PDF or a bare landing-page domain. Classification is by link shape only and is marked as candidate, not verified, until a document is fetched.
- **Machine-readable feed**: `docs/feed.json` carries the current totals and recent changes for anyone building on top.

Deep-lint findings on individual white papers are deliberately **not** auto-published here. Rule findings against named issuers go through human legal review first; the review-gated study lives in the [linter repository](https://github.com/sebastianfoerste/micar-whitepaper-linter). A flag from a deterministic rule is a candidate gap in extracted text, not a confirmed deficiency by the named issuer.

## Method and limits

See [docs/methodology.md](docs/methodology.md) for sources, normalization, change detection, and known limitations. Two that matter most: the observatory reflects the register exports as published (upstream corrections appear as "changed" entries), and format classification is a URL-shape heuristic until documents are fetched.

## Legal

The underlying data is ESMA's public register. This repository records factual observations about that register; it contains no legal assessment of any issuer or service provider and is not legal advice. Code is MIT-licensed.
