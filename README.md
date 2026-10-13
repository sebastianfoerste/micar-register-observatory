# MiCAR Register Observatory

A living dashboard of the **ESMA interim MiCAR register**. Every Monday a scheduled job pulls the public register exports (crypto-asset white papers under Titles II–IV, authorised CASPs, non-compliant entities), diffs them against the last snapshot, and rewrites the dashboard below: new filings, changed entries, withdrawals, and which file formats the white-paper links point to, judged by the URL alone.

The register is public by law: Art. 109 VO (EU) 2023/1114 (MiCAR) requires ESMA to establish a public register of crypto-asset white papers, of issuers of asset-referenced and e-money tokens, and of crypto-asset service providers. The duty to make each white paper available in a machine-readable format sits in the white-paper provisions, Art. 6(10), 19(9) and 51(9) MiCAR, with the forms, formats and templates set by Commission Implementing Regulation (EU) 2024/2984. This repository makes the register's weekly movement visible: what appeared, what changed, what disappeared.

## Dashboard

<!-- dashboard:start -->
**Register snapshot: 2026-10-12** (refreshed weekly from the public ESMA interim MiCAR register)

### Register totals

| Register | Entries | Source status |
| --- | ---: | --- |
| [White papers — other crypto-assets (Title II)](https://www.esma.europa.eu/sites/default/files/2024-12/OTHER.csv) | 1040 | ok |
| [White papers — e-money tokens (Title IV)](https://www.esma.europa.eu/sites/default/files/2024-12/EMTWP.csv) | 50 | ok |
| [White papers — asset-referenced tokens (Title III)](https://www.esma.europa.eu/sites/default/files/2024-12/ARTZZ.csv) | 0 | ok |
| [Authorised crypto-asset service providers (CASPs)](https://www.esma.europa.eu/sites/default/files/2024-12/CASPS.csv) | 370 | ok |
| [Non-compliant entities flagged by NCAs](https://www.esma.europa.eu/sites/default/files/2024-12/NCASP.csv) | 173 | ok |

### White paper format coverage

Classified by link shape only; a format is a deep-lint candidate, not a verified fact, until the document is fetched.

| Linked format | Count | Deep-lint candidate |
| --- | ---: | --- |
| No recognised file extension (bare domain, landing page or other page) | 653 | no |
| PDF | 264 | no |
| XHTML / HTML | 171 | yes |
| No link in register | 2 | no |

### Home Member States (white papers)

| Member State | White papers |
| --- | ---: |
| IE | 394 |
| MT | 173 |
| DE | 170 |
| NL | 90 |
| LI | 73 |
| LU | 59 |
| FR | 35 |
| LV | 15 |
| AT | 10 |
| FI | 10 |
| ...and 16 more | |

### Changes in this snapshot (2026-10-12)

| Change | Register | Entity | MS | Link |
| --- | --- | --- | --- | --- |
| added | other-wp | Crypto Risk Metrics GmbH | DE | [https://white-paper.crypto-risk-metrics.com/en/blue-chip-...](https://white-paper.crypto-risk-metrics.com/en/blue-chip-ffg-3bkz1tqdx/index.html) |
| added | other-wp | Crypto Risk Metrics GmbH | DE | [https://white-paper.crypto-risk-metrics.com/en/researchco...](https://white-paper.crypto-risk-metrics.com/en/researchcoin-ffg-fdqm0jpzp/index.html) |
| added | other-wp | Crypto Risk Metrics GmbH | DE | [https://white-paper.crypto-risk-metrics.com/en/treehouse-...](https://white-paper.crypto-risk-metrics.com/en/treehouse-ffg-7pq1242p3/index.html) |
| added | other-wp | Crypto Risk Metrics GmbH | DE | [https://white-paper.crypto-risk-metrics.com/en/euler-ffg-...](https://white-paper.crypto-risk-metrics.com/en/euler-ffg-bjsllnx42/index.html) |
| added | other-wp | Axenor Holdings OÜ | EE | [https://crypto-holdings.io/](https://crypto-holdings.io/) |
| added | other-wp | COMPANY ZERO LLC | IE | [https://decred.org/micar-whitepaper](https://decred.org/micar-whitepaper) |
| added | other-wp | Open Protocol Labs Ltd | IE |  |
| added | other-wp | Primary Creative Limited | IE | [https://www.cityprotocol.co/mica_whitepaper](https://www.cityprotocol.co/mica_whitepaper) |
| added | other-wp | Axis Robotics Limited | IE | [https://axisrobotics.ai/mica_whitepaper](https://axisrobotics.ai/mica_whitepaper) |
| changed | other-wp | Acurast Association | LV | [https://docsend.com/view/vxyaenm9z2mfghg9](https://docsend.com/view/vxyaenm9z2mfghg9) |
| changed | other-wp | EquationX Ltd. | LV | [https://pell.network/pdf/pell-network-whitepaper-v1.0.pdf](https://pell.network/pdf/pell-network-whitepaper-v1.0.pdf) |
| changed | other-wp | MYX Technology Limited | LV | [https://myxfinance.gitbook.io/myx/protocol/compliance](https://myxfinance.gitbook.io/myx/protocol/compliance) |
| changed | other-wp | Propy Inc | LV | [https://propy.com/browse/wp-content/uploads/Propy-MiCA-Wh...](https://propy.com/browse/wp-content/uploads/Propy-MiCA-WhitePaper-2025.pdf) |
| changed | other-wp | Not Multiverse Ltd | LV | [https://almanak.co/almanak-mica-wp.pdf](https://almanak.co/almanak-mica-wp.pdf) |
| changed | other-wp | Zee World Association | LV | [https://cdn.forest.inc/docs/whitepaper.pdf](https://cdn.forest.inc/docs/whitepaper.pdf) |
| changed | other-wp | BlockBen SIA | LV | [https://crowdedhero.com/legal/crowdx_whitepaper](https://crowdedhero.com/legal/crowdx_whitepaper) |
| changed | other-wp | BlockBen SIA | LV | [https://data.blockben.com/whitepaper/docs.html](https://data.blockben.com/whitepaper/docs.html) |
| changed | other-wp | BlockBen SIA | LV | [https://blockben.com/en/products/holoverz](https://blockben.com/en/products/holoverz) |
| changed | other-wp | BlockBen SIA | LV | [https://vendomatiq.com/tico/whitepaper.pdf](https://vendomatiq.com/tico/whitepaper.pdf) |
| changed | other-wp | Comet Technologies Ltd. | LV | [https://gitbook.zignaly.com/white-paper](https://gitbook.zignaly.com/white-paper) |
| changed | other-wp | Gen6 USA LLC | LV | [https://gen6.me/filez/mica_full.html](https://gen6.me/filez/mica_full.html) |
| changed | other-wp | Linear Intent Technologies Ltd. | LV | [https://www.oroswap.org/whitepaper](https://www.oroswap.org/whitepaper) |
| added | other-wp | Virtuals Protocol | MT | [https://my.okx.com/whitepaper/aixbt-aixbt.xhtml](https://my.okx.com/whitepaper/aixbt-aixbt.xhtml) |
| added | other-wp | Pons Labs LLC | MT | [https://www.ponsfamily.com/mica](https://www.ponsfamily.com/mica) |
| changed | other-wp | NativeArc EOOD | BG | [https://nx0.ai](https://nx0.ai) |
| ...and 12 more (see `data/changelog.jsonl`) | | | | |
<!-- dashboard:end -->

## Quarterly report: The State of the MiCAR Register

A quarterly data report built from these snapshots. It answers one question with numbers instead of anecdote: how many white papers on the register link to a structured document rather than to a PDF or a landing page? MiCAR requires white papers to be made available in a machine-readable format (Art. 6(10), 19(9) and 51(9)); the report measures a URL-based proxy for that, not compliance.

Latest edition: **[editions/2026-Q3.md](editions/2026-Q3.md)**

| Edition | Snapshot | Headline |
| --- | --- | --- |
| [2026-Q3](editions/2026-Q3.md) | 2026-09-21 | 13.8% of white-paper links point to an XHTML/HTML file (URL proxy; iXBRL not verified); 61.1% landing-page only |

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
