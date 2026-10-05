# MiCAR Register Observatory

A living dashboard of the **ESMA interim MiCAR register**. Every Monday a scheduled job pulls the public register exports (crypto-asset white papers under Titles II–IV, authorised CASPs, non-compliant entities), diffs them against the last snapshot, and rewrites the dashboard below: new filings, changed entries, withdrawals, and how many white papers are published in a machine-readable format.

The register is public by law — Art. 109 Abs. 1 VO (EU) 2023/1114 (MiCAR) requires ESMA to publish white papers and authorisations in a machine-readable register. This repository makes the register's weekly movement visible: what appeared, what changed, what disappeared.

## Dashboard

<!-- dashboard:start -->
**Register snapshot: 2026-10-05** (refreshed weekly from the public ESMA interim MiCAR register)

### Register totals

| Register | Entries | Source status |
| --- | ---: | --- |
| [White papers — other crypto-assets (Title II)](https://www.esma.europa.eu/sites/default/files/2024-12/OTHER.csv) | 1028 | ok |
| [White papers — e-money tokens (Title IV)](https://www.esma.europa.eu/sites/default/files/2024-12/EMTWP.csv) | 50 | ok |
| [White papers — asset-referenced tokens (Title III)](https://www.esma.europa.eu/sites/default/files/2024-12/ARTZZ.csv) | 0 | ok |
| [Authorised crypto-asset service providers (CASPs)](https://www.esma.europa.eu/sites/default/files/2024-12/CASPS.csv) | 364 | ok |
| [Non-compliant entities flagged by NCAs](https://www.esma.europa.eu/sites/default/files/2024-12/NCASP.csv) | 173 | ok |

### White paper format coverage

Classified by link shape only; a format is a deep-lint candidate, not a verified fact, until the document is fetched.

| Linked format | Count | Deep-lint candidate |
| --- | ---: | --- |
| Unspecified (landing page or bare domain) | 648 | no |
| PDF | 264 | no |
| XHTML / HTML | 165 | yes |
| No link in register | 1 | no |

### Home Member States (white papers)

| Member State | White papers |
| --- | ---: |
| IE | 389 |
| MT | 171 |
| DE | 166 |
| NL | 90 |
| LI | 73 |
| LU | 59 |
| FR | 35 |
| LV | 15 |
| AT | 10 |
| FI | 10 |
| ...and 16 more | |

### Changes in this snapshot (2026-10-05)

| Change | Register | Entity | MS | Link |
| --- | --- | --- | --- | --- |
| added | other-wp | Crypto Risk Metrics GmbH | DE | [https://white-paper.crypto-risk-metrics.com/en/flow-ffg-6...](https://white-paper.crypto-risk-metrics.com/en/flow-ffg-6t49bcsxz/index.html) |
| added | other-wp | Crypto Risk Metrics GmbH | DE | [https://white-paper.crypto-risk-metrics.com/en/hyperliqui...](https://white-paper.crypto-risk-metrics.com/en/hyperliquid-ffg-hltpnvxn0/index.html) |
| added | other-wp | Crypto Risk Metrics GmbH | DE | [https://white-paper.crypto-risk-metrics.com/en/mamo-ffg-4...](https://white-paper.crypto-risk-metrics.com/en/mamo-ffg-4wxhprnh8/index.html) |
| added | other-wp | Crypto Risk Metrics GmbH | DE | [https://white-paper.crypto-risk-metrics.com/en/dydx-ffg-1...](https://white-paper.crypto-risk-metrics.com/en/dydx-ffg-1hzhk551m/index.html) |
| added | other-wp | Crypto Risk Metrics GmbH | DE | [https://white-paper.crypto-risk-metrics.com/en/mantle-ffg...](https://white-paper.crypto-risk-metrics.com/en/mantle-ffg-qh1gf1j5h/index.html) |
| added | other-wp | Crypto Risk Metrics GmbH | DE | [https://white-paper.crypto-risk-metrics.com/en/useless-co...](https://white-paper.crypto-risk-metrics.com/en/useless-coin-ffg-8hbmrv08q/index.html) |
| added | other-wp | Gotchi Labs Ltd | IE | [https://whitepaper.sleepagotchi.com/](https://whitepaper.sleepagotchi.com/) |
| added | other-wp | Provable GmbH | IE | [https://www.aleo.org/provablepaper/](https://www.aleo.org/provablepaper/) |
| added | other-wp | Reasoon Limited | IE | [https://dgb.eunice.ai/mica_whitepaper](https://dgb.eunice.ai/mica_whitepaper) |
| added | other-wp | Katana Token DeployCo Ltd | IE | [https://docs.katana.network/files/kat_whitepaper_admissio...](https://docs.katana.network/files/kat_whitepaper_admission_to_trading.xhtml) |
| added | other-wp | Katana Token DeployCo Ltd | IE | [https://docs.katana.network/files/kat_whitepaper_offering...](https://docs.katana.network/files/kat_whitepaper_offering.xhtml) |
| added | other-wp | Polygon Labs Services (Switzerland) AG | IE | [https://polygon.technology/papers/pol-micar-whitepaper-v2...](https://polygon.technology/papers/pol-micar-whitepaper-v2.xhtml) |
| added | other-wp | HATX Technologies Kft. | HU | [https://hempaccessglobal.com](https://hempaccessglobal.com) |
| changed | other-wp | xMoney Labs AG | LI | [http://www.xmoney.com/legal/white-paper-xmn-3-0---xmoney-...](http://www.xmoney.com/legal/white-paper-xmn-3-0---xmoney-token) |
| added | other-wp | Haven Holding AG | LI | [https://havtoken.com/havenex-whitepaper.pdf](https://havtoken.com/havenex-whitepaper.pdf) |
| added | other-wp | SUN AG | LI | [https://minimeal.com/en/pages/soil](https://minimeal.com/en/pages/soil) |
| added | other-wp | Fan Token Management AG | MT | [https://www.socios.com/legal-hub/whitepaper/pmo-whitepaper/](https://www.socios.com/legal-hub/whitepaper/pmo-whitepaper/) |
| changed | other-wp | CANOPY NETWORK CORP. | NL | [https://canopy.micarwhitepapers.eu](https://canopy.micarwhitepapers.eu) |
| changed | other-wp | Asimov Ltd | NL | [https://genlayer.micarwhitepapers.eu](https://genlayer.micarwhitepapers.eu) |
| added | other-wp | Saffron Finance Limited | NL | [https://saffron.micarwhitepapers.eu](https://saffron.micarwhitepapers.eu) |
| removed | other-wp | Haven Holding AG | LI | [www.havenex.com](https://www.havenex.com) |
| added | emt-wp | Aplauz NL B.V. | NL | [https://www.weur.io](https://www.weur.io) |
| changed | casps | J2TX Ltd | CY |  |
| changed | casps | TRIA BRIDGE LIMITED (ex Tokenomica Bridge Ltd) | CY |  |
| added | casps | VR Bank zwischen den Meeren eG | DE |  |
| ...and 2 more (see `data/changelog.jsonl`) | | | | |
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
