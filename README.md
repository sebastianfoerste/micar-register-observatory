# MiCAR Register Observatory

A living dashboard of the **ESMA interim MiCAR register**. Every Monday a scheduled job pulls the public register exports (crypto-asset white papers under Titles II–IV, authorised CASPs, non-compliant entities), diffs them against the last snapshot, and rewrites the dashboard below: new filings, changed entries, withdrawals, and how many white papers are published in a machine-readable format.

The register is public by law — Art. 109 Abs. 1 VO (EU) 2023/1114 (MiCAR) requires ESMA to publish white papers and authorisations in a machine-readable register. This repository makes the register's weekly movement visible: what appeared, what changed, what disappeared.

## Dashboard

<!-- dashboard:start -->
**Register snapshot: 2026-08-24** (refreshed weekly from the public ESMA interim MiCAR register)

### Register totals

| Register | Entries | Source status |
| --- | ---: | --- |
| [White papers — other crypto-assets (Title II)](https://www.esma.europa.eu/sites/default/files/2024-12/OTHER.csv) | 973 | ok |
| [White papers — e-money tokens (Title IV)](https://www.esma.europa.eu/sites/default/files/2024-12/EMTWP.csv) | 43 | ok |
| [White papers — asset-referenced tokens (Title III)](https://www.esma.europa.eu/sites/default/files/2024-12/ARTZZ.csv) | 0 | ok |
| [Authorised crypto-asset service providers (CASPs)](https://www.esma.europa.eu/sites/default/files/2024-12/CASPS.csv) | 335 | ok |
| [Non-compliant entities flagged by NCAs](https://www.esma.europa.eu/sites/default/files/2024-12/NCASP.csv) | 167 | ok |

### White paper format coverage

Classified by link shape only; a format is a deep-lint candidate, not a verified fact, until the document is fetched.

| Linked format | Count | Deep-lint candidate |
| --- | ---: | --- |
| Unspecified (landing page or bare domain) | 621 | no |
| PDF | 256 | no |
| XHTML / HTML | 138 | yes |
| No link in register | 1 | no |

### Home Member States (white papers)

| Member State | White papers |
| --- | ---: |
| IE | 365 |
| MT | 165 |
| DE | 154 |
| NL | 86 |
| LI | 72 |
| LU | 55 |
| FR | 34 |
| LV | 14 |
| AT | 10 |
| FI | 10 |
| ...and 12 more | |

### Changes in this snapshot (2026-08-24)

| Change | Register | Entity | MS | Link |
| --- | --- | --- | --- | --- |
| added | other-wp | Bitpanda GmbH | AT | [https://www.bitpanda.com/en/legal/vsn-white-paper](https://www.bitpanda.com/en/legal/vsn-white-paper) |
| changed | other-wp | MOJO Sales GmbH | AT | [https://mojomarketplace.io](https://mojomarketplace.io) |
| added | other-wp | Heldfor GmbH | DE | [https://www.heldfor.com/whitepaper](https://www.heldfor.com/whitepaper) |
| added | other-wp | Crypto Risk Metrics GmbH | DE | [https://white-paper.crypto-risk-metrics.com/en/floki-ffg-...](https://white-paper.crypto-risk-metrics.com/en/floki-ffg-r1xc4hqt5/index.html) |
| added | other-wp | Crypto Risk Metrics GmbH | DE | [https://white-paper.crypto-risk-metrics.com/en/gram-ffg-k...](https://white-paper.crypto-risk-metrics.com/en/gram-ffg-kk12jmbtx/index.html) |
| added | other-wp | Nimiq Network Ltd. | DE | [https://www.nimiq.com/](https://www.nimiq.com/) |
| added | other-wp | Crypto Risk Metrics GmbH | DE | [https://white-paper.crypto-risk-metrics.com/en/diem-ffg-z...](https://white-paper.crypto-risk-metrics.com/en/diem-ffg-zffjtq357/index.html) |
| added | other-wp | Crypto Risk Metrics GmbH | DE | [https://white-paper.crypto-risk-metrics.com/en/venice-tok...](https://white-paper.crypto-risk-metrics.com/en/venice-token-ffg-p0sd47m0w/index.html) |
| added | other-wp | Crypto Risk Metrics GmbH | DE | [https://white-paper.crypto-risk-metrics.com/en/b3-ffg-bpl...](https://white-paper.crypto-risk-metrics.com/en/b3-ffg-bplsknpd9/index.html) |
| added | other-wp | Crypto Risk Metrics GmbH | DE | [https://white-paper.crypto-risk-metrics.com/en/ai16z-ffg-...](https://white-paper.crypto-risk-metrics.com/en/ai16z-ffg-8sqn5vkwh/index.html) |
| added | other-wp | Crypto Risk Metrics GmbH | DE | [https://white-paper.crypto-risk-metrics.com/en/pumpfun-ff...](https://white-paper.crypto-risk-metrics.com/en/pumpfun-ffg-c2f189jnl/index.html) |
| added | other-wp | Crypto Risk Metrics GmbH | DE | [https://white-paper.crypto-risk-metrics.com/en/peanut-the...](https://white-paper.crypto-risk-metrics.com/en/peanut-the-squirrel-ffg-75d0kj7wn/index.html) |
| added | other-wp | VERA POWER LTD | IE | [https://www.upsmartytoken.com/whitepaper](https://www.upsmartytoken.com/whitepaper) |
| added | other-wp | OGF (BVI) Ltd. | IE | [https://contents.crosstoken.io/white-paper/260713_WhitePa...](https://contents.crosstoken.io/white-paper/260713_WhitePaper_ONE_Token_OGF_BVI_Ltd_VG_EN_ID_3557280.xhtml) |
| added | other-wp | DAWN Foundation | IE | [http://dawninternet.com/micawhitepaper](http://dawninternet.com/micawhitepaper) |
| added | other-wp | Midnight TGE Ltd. | MT | [https://www.midnight.gd/night-mica-white-paper](https://www.midnight.gd/night-mica-white-paper) |
| added | other-wp | QuantID Systems Inc | MT | [https://api.s.technology/wp-content/uploads/2026/08/White...](https://api.s.technology/wp-content/uploads/2026/08/WhitePaper-RWS-Token_v8.xhtml) |
| added | other-wp | Wandilla Holdings Limited | NL | [https://verona.micarwhitepapers.eu](https://verona.micarwhitepapers.eu) |
| added | other-wp | The Interfold Foundation | NL | [https://interfold.micarwhitepapers.eu](https://interfold.micarwhitepapers.eu) |
| added | other-wp | Tread Foundry Ltd. | NL | [https://tread.micarwhitepapers.eu](https://tread.micarwhitepapers.eu) |
| added | other-wp | Orbital Line Limited | NL | [https://grvt.micarwhitepapers.eu](https://grvt.micarwhitepapers.eu) |
| added | other-wp | Odyssey Foundation | NL | [https://odyssey.micarwhitepapers.eu](https://odyssey.micarwhitepapers.eu) |
| changed | other-wp | Dog Planet AS | NO | [https://www.dogplanet.no/](https://www.dogplanet.no/) |
| added | other-wp | PALM Token | NO | [http://www.palmeconomy.io](http://www.palmeconomy.io) |
| added | other-wp | Aprikos Venture AS | NO | [https://venturetoken.io/](https://venturetoken.io/) |
| ...and 23 more (see `data/changelog.jsonl`) | | | | |
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
