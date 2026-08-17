# MiCAR Register Observatory

A living dashboard of the **ESMA interim MiCAR register**. Every Monday a scheduled job pulls the public register exports (crypto-asset white papers under Titles II–IV, authorised CASPs, non-compliant entities), diffs them against the last snapshot, and rewrites the dashboard below: new filings, changed entries, withdrawals, and how many white papers are published in a machine-readable format.

The register is public by law — Art. 109 Abs. 1 VO (EU) 2023/1114 (MiCAR) requires ESMA to publish white papers and authorisations in a machine-readable register. This repository makes the register's weekly movement visible: what appeared, what changed, what disappeared.

## Dashboard

<!-- dashboard:start -->
**Register snapshot: 2026-08-17** (refreshed weekly from the public ESMA interim MiCAR register)

### Register totals

| Register | Entries | Source status |
| --- | ---: | --- |
| [White papers — other crypto-assets (Title II)](https://www.esma.europa.eu/sites/default/files/2024-12/OTHER.csv) | 960 | ok |
| [White papers — e-money tokens (Title IV)](https://www.esma.europa.eu/sites/default/files/2024-12/EMTWP.csv) | 43 | ok |
| [White papers — asset-referenced tokens (Title III)](https://www.esma.europa.eu/sites/default/files/2024-12/ARTZZ.csv) | 0 | ok |
| [Authorised crypto-asset service providers (CASPs)](https://www.esma.europa.eu/sites/default/files/2024-12/CASPS.csv) | 329 | ok |
| [Non-compliant entities flagged by NCAs](https://www.esma.europa.eu/sites/default/files/2024-12/NCASP.csv) | 167 | ok |

### White paper format coverage

Classified by link shape only; a format is a deep-lint candidate, not a verified fact, until the document is fetched.

| Linked format | Count | Deep-lint candidate |
| --- | ---: | --- |
| Unspecified (landing page or bare domain) | 617 | no |
| PDF | 256 | no |
| XHTML / HTML | 129 | yes |
| No link in register | 1 | no |

### Home Member States (white papers)

| Member State | White papers |
| --- | ---: |
| IE | 362 |
| MT | 163 |
| DE | 150 |
| NL | 84 |
| LI | 72 |
| LU | 55 |
| FR | 34 |
| LV | 14 |
| FI | 10 |
| AT | 9 |
| ...and 13 more | |

### Changes in this snapshot (2026-08-17)

| Change | Register | Entity | MS | Link |
| --- | --- | --- | --- | --- |
| added | other-wp | SKYGATE Network GmbH | AT | [WWW.SKYGATETOKEN.AT](https://WWW.SKYGATETOKEN.AT) |
| changed | other-wp | DGRX Sales GmbH | AT | [WWW.DESERTGREENER.IO](https://WWW.DESERTGREENER.IO) |
| added | other-wp | Bitpanda GmbH | AT | [VISION.NOW](https://VISION.NOW) |
| added | other-wp | ATEG Capital FlexCo | AT | [https://ateg-capital.com](https://ateg-capital.com) |
| changed | other-wp | SC STEELCOIN GmbH | AT | [https://steelcoin.com/](https://steelcoin.com/) |
| changed | other-wp | ELEVEN ELEVEN MANAGEMENT LIMITED | AT | [https://1111-management.com/](https://1111-management.com/) |
| added | other-wp | ZKsync Association - Ein Verein zur Foerderung des digitalen Oekosystems ZKsync e.V. | AT | [zknation.io](https://zknation.io) |
| added | other-wp | StarkWare Industries Ltd | AT | [https://starkware.co/](https://starkware.co/) |
| added | other-wp | Biogena GmbH & Co KG | AT | [www.biogena.com/biox](https://www.biogena.com/biox) |
| added | other-wp | MOJO Sales GmbH | Austria | [https://mojomarketplace.io](https://mojomarketplace.io) |
| added | other-wp | $OTHER | CY | [https://whitepaper.anotherapp.io/](https://whitepaper.anotherapp.io/) |
| added | other-wp | EVO22 technologies s.r.o. | CZ | [https://evo22.tech/EVAcoinWhitePaper.xhtml](https://evo22.tech/EVAcoinWhitePaper.xhtml) |
| added | other-wp | Crypto Risk Metrics GmbH | DE | [https://white-paper.crypto-risk-metrics.com/en/official-t...](https://white-paper.crypto-risk-metrics.com/en/official-trump-ffg-ljdpgnxxk/index.html) |
| changed | other-wp | OneFootball Capital GmbH | DE | [https://promo.onefootball.com/legal/whitepaper](https://promo.onefootball.com/legal/whitepaper) |
| changed | other-wp | XGR.Network GmbH | DE | [https://xgr.network/whitepaper/](https://xgr.network/whitepaper/) |
| changed | other-wp | WYND Capital GmbH /MD Capital GmbH | DE | [https://wynd.group/](https://wynd.group/) |
| changed | other-wp | Hassan Systems GmbH | DE | [https://getlea.org/](https://getlea.org/) |
| changed | other-wp | Crypto Risk Metrics GmbH | DE | [https://white-paper.crypto-risk-metrics.com/en/doodles-ff...](https://white-paper.crypto-risk-metrics.com/en/doodles-ffg-kf6rx3lr1/index.html) |
| added | other-wp | Crypto Risk Metrics GmbH | DE | [https://white-paper.crypto-risk-metrics.com/en/kyber-netw...](https://white-paper.crypto-risk-metrics.com/en/kyber-network-crystal-v2-ffg-l0dzsblvz/index.html) |
| added | other-wp | Crypto Risk Metrics GmbH | DE | [https://white-paper.crypto-risk-metrics.com/en/plume-ffg-...](https://white-paper.crypto-risk-metrics.com/en/plume-ffg-frzqzj7bl/index.html) |
| added | other-wp | Crypto Risk Metrics GmbH | DE | [https://white-paper.crypto-risk-metrics.com/en/humidifi-t...](https://white-paper.crypto-risk-metrics.com/en/humidifi-token-ffg-tcjp479h2/index.html) |
| added | other-wp | Crypto Risk Metrics GmbH | DE | [https://white-paper.crypto-risk-metrics.com/en/arbitrum-f...](https://white-paper.crypto-risk-metrics.com/en/arbitrum-ffg-44tp35hf9/index.html) |
| added | other-wp | Crypto Risk Metrics GmbH | DE | [https://white-paper.crypto-risk-metrics.com/en/opinion-ff...](https://white-paper.crypto-risk-metrics.com/en/opinion-ffg-g8n7hj69s/index.html) |
| added | other-wp | Heldfor GmbH | DE | [N/A](https://N/A) |
| added | other-wp | Crypto Risk Metrics GmbH | DE | [https://white-paper.crypto-risk-metrics.com/en/renzo-ffg-...](https://white-paper.crypto-risk-metrics.com/en/renzo-ffg-3spxmrfnc/index.html) |
| ...and 335 more (see `data/changelog.jsonl`) | | | | |
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
