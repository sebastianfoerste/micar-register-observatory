# MiCAR Register Observatory

A living dashboard of the **ESMA interim MiCAR register**. Every Monday a scheduled job pulls the public register exports (crypto-asset white papers under Titles II–IV, authorised CASPs, non-compliant entities), diffs them against the last snapshot, and rewrites the dashboard below: new filings, changed entries, entries no longer listed (in records after the 2026-10-12 snapshot, counted as removed only after two consecutive absences), and which file formats the white-paper links point to, judged by the URL alone.

The register is public by law. Art. 109(1) of Regulation (EU) 2023/1114 (MiCAR) requires ESMA to establish a register of crypto-asset white papers, of issuers of asset-referenced tokens and e-money tokens, and of crypto-asset service providers; the register must be publicly available on ESMA's website and updated on a regular basis. Art. 110 MiCAR adds a register of entities that provide crypto-asset services in violation of Art. 59 or 61 (the non-compliant entities), publicly available on ESMA's website in a machine-readable format. Within Art. 109, machine-readability enters through the regulatory technical standards under Art. 109(8): Commission Delegated Regulation (EU) 2025/421, which applies from 23 December 2025, specifies the data for classifying white papers in the register and the arrangements that make this data machine-readable. The duty to make each white paper itself available in a machine-readable format sits in the white-paper provisions, Art. 6(10), 19(9) and 51(9) MiCAR, with the forms, formats and templates set by Commission Implementing Regulation (EU) 2024/2984, which also applies from 23 December 2025. From 10 January 2030, Art. 110a(4) MiCAR, inserted by Regulation (EU) 2023/2869, makes the information in both registers accessible on the European single access point (ESAP), in a machine-readable format and with ESMA as the collection body. The [regulatory claim ledger](docs/regulatory-claim-ledger.md) records each pinpoint, checked against the [source snapshots](sources/README.md).

This repository makes the register's weekly movement visible: what appeared, what changed, what disappeared.

## Dashboard

<!-- dashboard:start -->
**Register snapshot: 2026-11-16** (refreshed weekly from the public ESMA interim MiCAR register)

### Register totals

| Register | Rows | Entities | Source status |
| --- | ---: | ---: | --- |
| [White papers — other crypto-assets (Title II)](https://www.esma.europa.eu/sites/default/files/2024-12/OTHER.csv) | 1077 | 672 | ok (file modified 2026-11-11) |
| [Issuers of e-money tokens (Title IV)](https://www.esma.europa.eu/sites/default/files/2024-12/EMTWP.csv) | 51 | 26 | ok (file modified 2026-11-11) |
| [Issuers of asset-referenced tokens (Title III)](https://www.esma.europa.eu/sites/default/files/2024-12/ARTZZ.csv) | 0 | 0 | ok (file modified 2025-02-14) |
| [Authorised crypto-asset service providers (CASPs)](https://www.esma.europa.eu/sites/default/files/2024-12/CASPS.csv) | 407 | 404 | ok (file modified 2026-11-11) |
| [Non-compliant entities flagged by NCAs](https://www.esma.europa.eu/sites/default/files/2024-12/NCASP.csv) | 216 | 213 | ok (file modified 2026-11-11) |

Rows are lines of the register export; entities are distinct LEIs, or names where a row has none. One entity can have several rows: several white papers, or a second CASP authorisation.

CASP register: 404 firms in 407 rows, 2 of them with a withdrawal date (`ac_authorisationEndDate`).

### White paper format coverage

Classified by link shape only; a format is a deep-lint candidate, not a verified fact, until the document is fetched.

| Linked format | Count | Deep-lint candidate |
| --- | ---: | --- |
| No recognised file extension (bare domain, landing page or other page) | 676 | no |
| PDF | 265 | no |
| XHTML / HTML | 183 | yes |
| No link in register | 4 | no |

### Home Member States (white papers)

| Member State | White papers |
| --- | ---: |
| IE | 408 |
| DE | 177 |
| MT | 176 |
| NL | 98 |
| LI | 74 |
| LU | 60 |
| FR | 40 |
| LV | 15 |
| AT | 10 |
| FI | 10 |
| ...and 15 more | |

### Changes in this snapshot (2026-11-16)

| Change | Register | Entity | MS | Link |
| --- | --- | --- | --- | --- |
| added | other-wp | Teroxx Rewards Ltd | CY | [https://abloxx.com/en](https://abloxx.com/en) |
| changed | other-wp | Number Go Up Technologies | FI | [https://www.ngut.eu/whitepapers/SWAN.html](https://www.ngut.eu/whitepapers/SWAN.html) |
| added | other-wp | IBRL BVI Ltd | FI | [https://doublezero.xyz/whitepaper-mica.pdfac](https://doublezero.xyz/whitepaper-mica.pdfac) |
| changed | other-wp | Gevulot Oy | FI | [https://zkcloud.com/whitepaper](https://zkcloud.com/whitepaper) |
| added | other-wp | InvestTWLGF Oy | FI | [https://twlgf.com/twlgf-crypto-asset-description/](https://twlgf.com/twlgf-crypto-asset-description/) |
| changed | other-wp | Investlitiumlic Oy | FI | [https://www.litiumlic.com/litiumlic-kryptovaran-kuvaus-li...](https://www.litiumlic.com/litiumlic-kryptovaran-kuvaus-litiumlic-crypto-asset-description/) |
| added | other-wp | Knowledge Process SA | FR | [https://kno.academy/whitepaper](https://kno.academy/whitepaper) |
| added | other-wp | SELF Technology Limited | IE | [https://docs.self.app/micawhitepaper](https://docs.self.app/micawhitepaper) |
| added | other-wp | BitUtility S.A. | IE | [bitutility.micarwhitepapers.eu](https://bitutility.micarwhitepapers.eu) |
| added | other-wp | Strato Foundation | IE | [https://strato.nexus/mica](https://strato.nexus/mica) |
| added | other-wp | Bera Chain Foundation | MT | [https://my.okx.com/whitepaper/berachain-bera.xhtml](https://my.okx.com/whitepaper/berachain-bera.xhtml) |
| added | other-wp | Layer 69 Inc. | MT | [https://docs.dogeos.com/token](https://docs.dogeos.com/token) |
| added | other-wp | Kor Technologies Issuer Inc. | MT | [https://www.korprotocol.io/mica](https://www.korprotocol.io/mica) |
| added | other-wp | Bright Signal Invest AS | NO | [https://disclosuretoken.com](https://disclosuretoken.com) |
| missing | other-wp | Abloxx Token Ltd. | CY | [https://abloxx.com/en](https://abloxx.com/en) |
| missing | other-wp | Planck Network ($PLANCK) | CY | [https://plancknetwork.com/whitepaper.pdf](https://plancknetwork.com/whitepaper.pdf) |
| missing | other-wp | Punta Parana Foundation | FI | [https://doublezero.xyz/whitepaper-mica.pdf](https://doublezero.xyz/whitepaper-mica.pdf) |
| missing | other-wp | InvestTWLGF Oy | FI | [https://twlgf.com/twlgf-kryptovaran-kuvaus-twlgf-crypto-a...](https://twlgf.com/twlgf-kryptovaran-kuvaus-twlgf-crypto-asset-description/) |
| missing | other-wp | Bright Signal Invest AS | NO | [https://brightsignal.no](https://brightsignal.no) |
| removed | other-wp | Yellow Token | IE | [https://docs.yellow.org/assets/YELLOW\_MiCA\_White\_Paper\_v....](https://docs.yellow.org/assets/YELLOW_MiCA_White_Paper_v.1.2.pdf) |
| removed | other-wp | FUN | IE | [https://docs.sport.fun/usdfun-token/mica-whitepaper](https://docs.sport.fun/usdfun-token/mica-whitepaper) |
| removed | other-wp | GOATED | IE | [https://www.goat.network/micar-white-paper](https://www.goat.network/micar-white-paper) |
| removed | other-wp | Keeta | IE | [https://keeta.com/MiCA\_Whitepaper.pdf](https://keeta.com/MiCA_Whitepaper.pdf) |
| removed | other-wp | $ROAM | IE | [https://weroam.xyz/roam\_micar\_whitepaper](https://weroam.xyz/roam_micar_whitepaper) |
| removed | other-wp | ATH | IE | [https://docs.aethir.com/whitepaper](https://docs.aethir.com/whitepaper) |
| ...and 91 more (see `data/changelog.jsonl`) | | | | |

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

- **New, changed, missing, removed and restored register entries** per weekly snapshot. A row is `missing` the first time an export does not list it, `removed` once it is absent from two consecutive exports, and `restored` if it is listed again. Records up to the 2026-10-12 snapshot (record version 1) used `removed` for a first absence and `added` for a relisting; see [docs/methodology.md](docs/methodology.md#change-detection). A removal can be a withdrawal, an upstream correction or a changed white-paper URL; the export does not say which.
- **Format coverage**: how many linked white papers are XHTML/HTML, JSON, or DOCX (candidates for deterministic linting with [micar-whitepaper-linter](https://github.com/sebastianfoerste/micar-whitepaper-linter)) versus PDF or a URL with no recognised file extension (a bare domain, a landing page, or a document served without one). Classification is by link shape only and is marked as candidate, not verified, until a document is fetched.
- **Machine-readable feed**: `docs/feed.json` carries the current totals and recent changes for anyone building on top.

Deep-lint findings on individual white papers are deliberately **not** auto-published here. Rule findings against named issuers go through human legal review first; the review-gated study lives in the [linter repository](https://github.com/sebastianfoerste/micar-whitepaper-linter). A flag from a deterministic rule is a candidate gap in extracted text, not a confirmed deficiency by the named issuer.

## Method and limits

See [docs/methodology.md](docs/methodology.md) for sources, normalization, change detection, and known limitations. Two that matter most: the observatory reflects the register exports as published (upstream corrections appear as "changed" entries), and format classification is a URL-shape heuristic until documents are fetched.

## Data notice

Source: European Securities and Markets Authority (ESMA), interim MiCA register. The dashboard, `data/`, `docs/feed.json`, the digests and the editions republish that register in transformed form, so ESMA's [legal notice](https://www.esma.europa.eu/legal-notice) requires this disclaimer: This document has been drafted using material downloaded from ESMA’s website. ESMA does not endorse this publication and in no way is liable for copyright or other intellectual property rights infringements nor for any damages caused to third parties through this publication.

The MIT licence covers the code and its documentation files. The observatory's own prose in `editions/` and `docs/` is also licensed under [CC BY 4.0](https://creativecommons.org/licenses/by/4.0/). No licence is granted for the register data. [DATA_NOTICE.md](DATA_NOTICE.md) quotes ESMA's legal notice with its URL and retrieval date and sets out what each licence covers.

## Legal

The underlying data is ESMA's public register. This repository records factual observations about that register; it contains no legal assessment of any issuer or service provider and is not legal advice. Code is MIT-licensed; that licence does not extend to the register data or to the prose (see [Data notice](#data-notice)).
