# MiCAR Register Observatory

A living dashboard of the **ESMA interim MiCAR register**. Every Monday a scheduled job pulls the public register exports (crypto-asset white papers under Titles II–IV, authorised CASPs, non-compliant entities), diffs them against the last snapshot, and rewrites the dashboard below: new filings, changed entries, withdrawals, and how many white papers are published in a machine-readable format.

The register is public by law — Art. 109 Abs. 1 VO (EU) 2023/1114 (MiCAR) requires ESMA to publish white papers and authorisations in a machine-readable register. This repository makes the register's weekly movement visible: what appeared, what changed, what disappeared.

## Dashboard

<!-- dashboard:start -->
**Register snapshot: 2026-09-14** (refreshed weekly from the public ESMA interim MiCAR register)

### Register totals

| Register | Entries | Source status |
| --- | ---: | --- |
| [White papers — other crypto-assets (Title II)](https://www.esma.europa.eu/sites/default/files/2024-12/OTHER.csv) | 988 | ok |
| [White papers — e-money tokens (Title IV)](https://www.esma.europa.eu/sites/default/files/2024-12/EMTWP.csv) | 47 | ok |
| [White papers — asset-referenced tokens (Title III)](https://www.esma.europa.eu/sites/default/files/2024-12/ARTZZ.csv) | 0 | ok |
| [Authorised crypto-asset service providers (CASPs)](https://www.esma.europa.eu/sites/default/files/2024-12/CASPS.csv) | 346 | ok |
| [Non-compliant entities flagged by NCAs](https://www.esma.europa.eu/sites/default/files/2024-12/NCASP.csv) | 167 | ok |

### White paper format coverage

Classified by link shape only; a format is a deep-lint candidate, not a verified fact, until the document is fetched.

| Linked format | Count | Deep-lint candidate |
| --- | ---: | --- |
| Unspecified (landing page or bare domain) | 634 | no |
| PDF | 260 | no |
| XHTML / HTML | 140 | yes |
| No link in register | 1 | no |

### Home Member States (white papers)

| Member State | White papers |
| --- | ---: |
| IE | 373 |
| MT | 165 |
| DE | 155 |
| NL | 88 |
| LI | 72 |
| LU | 57 |
| FR | 35 |
| LV | 14 |
| AT | 10 |
| FI | 10 |
| ...and 15 more | |

### Changes in this snapshot (2026-09-14)

| Change | Register | Entity | MS | Link |
| --- | --- | --- | --- | --- |
| changed | other-wp | Obol Association | FR | [https://drive.google.com/file/d/1hTtnmVZkGxhJ8xYAS4PE6Q6t...](https://drive.google.com/file/d/1hTtnmVZkGxhJ8xYAS4PE6Q6tru9kKFW4/view?usp=sharing) |
| changed | other-wp | NAEST | FR | [https://naest.gitbook.io/wp-fr](https://naest.gitbook.io/wp-fr) |
| added | other-wp | Not applicable: Issuer of ANITA is not identified; 
Moonlabs, as applicant, is notifying admission to 
trading on its behalf pursuant to Article 4 of MiCA | FR | [https://anita.ink/micawp](https://anita.ink/micawp) |
| added | other-wp | Th QAIT Association | FR | [https://www.qait.ch](https://www.qait.ch) |
| added | other-wp | Fogo 1 Foundation | IE | [https://api.fogo.io/mica-whitepaper.pdf](https://api.fogo.io/mica-whitepaper.pdf) |
| added | other-wp | NewTendermint, LLC | IE | [https://github.com/gnolang/gno/blob/master/docs/gnoland-w...](https://github.com/gnolang/gno/blob/master/docs/gnoland-whitepaper.pdf) |
| added | other-wp | METANIAGAMES LIMITED | IE | [https://whitepaper.metania.games/](https://whitepaper.metania.games/) |
| added | other-wp | Bluwhale Foundation | IE | [https://profile.bluwhale.com/mica](https://profile.bluwhale.com/mica) |
| added | other-wp | Solana Mobile Inc. | IE | [https://solanamobile.com/mica-whitepaper](https://solanamobile.com/mica-whitepaper) |
| added | other-wp | Gradient Global Limited | IE | [https://docs.ts.finance/resources/tmx-token-white-paper-m...](https://docs.ts.finance/resources/tmx-token-white-paper-mica-title-ii) |
| added | other-wp | NeuraAI Ltd. | IE | [neura.micarwhitepapers.eu](https://neura.micarwhitepapers.eu) |
| added | other-wp | VINU LTD | IE | [https://nyks.tech/mica/nyks-mica-white-paper-en.xhtml](https://nyks.tech/mica/nyks-mica-white-paper-en.xhtml) |
| added | other-wp | ae_lei_name | ae_homeMemberState | [wp_url](https://wp_url) |
| changed | other-wp | Acurast Association | LV | [https://docsend.com/view/vxyaenm9z2mfghg9](https://docsend.com/view/vxyaenm9z2mfghg9) |
| changed | other-wp | EquationX Ltd. | LV | [https://pell.network/pdf/pell-network-whitepaper-v1.0.pdf](https://pell.network/pdf/pell-network-whitepaper-v1.0.pdf) |
| changed | other-wp | MYX Technology Limited | LV | [https://myxfinance.gitbook.io/myx/protocol/compliance](https://myxfinance.gitbook.io/myx/protocol/compliance) |
| changed | other-wp | Propy Inc | LV | [https://propy.com/browse/wp-content/uploads/Propy-MiCA-Wh...](https://propy.com/browse/wp-content/uploads/Propy-MiCA-WhitePaper-2025.pdf) |
| changed | other-wp | Not Multiverse Ltd | LV | [https://almanak.co/almanak-mica-wp.pdf](https://almanak.co/almanak-mica-wp.pdf) |
| changed | other-wp | Zee World Association | LV | [https://cdn.forest.inc/docs/whitepaper.pdf](https://cdn.forest.inc/docs/whitepaper.pdf) |
| changed | other-wp | BlockBen SIA | LV | [https://crowdedhero.com/legal/crowdx_whitepaper](https://crowdedhero.com/legal/crowdx_whitepaper) |
| added | other-wp | BlockBen SIA | LV | [https://data.blockben.com/whitepaper/docs.html](https://data.blockben.com/whitepaper/docs.html) |
| changed | other-wp | BlockBen SIA | LV | [https://blockben.com/en/products/holoverz](https://blockben.com/en/products/holoverz) |
| changed | other-wp | BlockBen SIA | LV | [https://vendomatiq.com/tico/whitepaper.pdf](https://vendomatiq.com/tico/whitepaper.pdf) |
| changed | other-wp | Comet Technologies Ltd. | LV | [https://gitbook.zignaly.com/white-paper](https://gitbook.zignaly.com/white-paper) |
| changed | other-wp | Gen6 USA LLC | LV | [https://gen6.me/filez/mica_full.html](https://gen6.me/filez/mica_full.html) |
| ...and 185 more (see `data/changelog.jsonl`) | | | | |
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
