# MiCAR Register Observatory

A living dashboard of the **ESMA interim MiCAR register**. Every Monday a scheduled job pulls the public register exports (crypto-asset white papers under Titles II–IV, authorised CASPs, non-compliant entities), diffs them against the last snapshot, and rewrites the dashboard below: new filings, changed entries, withdrawals, and how many white papers are published in a machine-readable format.

The register is public by law — Art. 109 Abs. 1 VO (EU) 2023/1114 (MiCAR) requires ESMA to publish white papers and authorisations in a machine-readable register. This repository makes the register's weekly movement visible: what appeared, what changed, what disappeared.

## Dashboard

<!-- dashboard:start -->
**Register snapshot: 2026-08-03** (refreshed weekly from the public ESMA interim MiCAR register)

### Register totals

| Register | Entries | Source status |
| --- | ---: | --- |
| [White papers — other crypto-assets (Title II)](https://www.esma.europa.eu/sites/default/files/2024-12/OTHER.csv) | 783 | ok |
| [White papers — e-money tokens (Title IV)](https://www.esma.europa.eu/sites/default/files/2024-12/EMTWP.csv) | 41 | ok |
| [White papers — asset-referenced tokens (Title III)](https://www.esma.europa.eu/sites/default/files/2024-12/ARTZZ.csv) | 0 | ok |
| [Authorised crypto-asset service providers (CASPs)](https://www.esma.europa.eu/sites/default/files/2024-12/CASPS.csv) | 323 | ok |
| [Non-compliant entities flagged by NCAs](https://www.esma.europa.eu/sites/default/files/2024-12/NCASP.csv) | 167 | ok |

### White paper format coverage

Classified by link shape only; a format is a deep-lint candidate, not a verified fact, until the document is fetched.

| Linked format | Count | Deep-lint candidate |
| --- | ---: | --- |
| Unspecified (landing page or bare domain) | 524 | no |
| PDF | 246 | no |
| XHTML / HTML | 52 | yes |
| No link in register | 2 | no |

### Home Member States (white papers)

| Member State | White papers |
| --- | ---: |
| IE | 298 |
| MT | 149 |
| DE | 111 |
| LI | 71 |
| NL | 63 |
| LU | 37 |
| FR | 28 |
| LV | 11 |
| AT | 9 |
| FI | 9 |
| ...and 9 more | |

### Changes in this snapshot (2026-08-03)

| Change | Register | Entity | MS | Link |
| --- | --- | --- | --- | --- |
| added | other-wp | Skygate Network GmbH | AT | [https://www.skygatetoken.at/wp-content/uploads/2025/01/WH...](https://www.skygatetoken.at/wp-content/uploads/2025/01/WHITEPAPER-SKYGATE-MiCAR-Version-1-18.01.25-EN-DE.pdf) |
| changed | other-wp | DGRX Sales GmbH | AT | [www.desertgreener.io](https://www.desertgreener.io) |
| added | other-wp | ATEG Capital FlexCo | AT | [https://ateg-capital.com/whitepaper/](https://ateg-capital.com/whitepaper/) |
| changed | other-wp | SC Steelcoin GmbH | AT | [https://steelcoin.com/](https://steelcoin.com/) |
| added | other-wp | VISION web 3 Stiftung | AT | [http://vision.now/](http://vision.now/) |
| added | other-wp | ZKsync Association - Ein Verein zur Foerderung des digitalen Oekosystems ZKsync e.V. | AT | [https://docs.zknation.io/legal/zk-token-mica-white-paper](https://docs.zknation.io/legal/zk-token-mica-white-paper) |
| added | other-wp | Tzolkin GmbH | AT | [https://starkware.co/](https://starkware.co/) |
| changed | other-wp | ELEVEN ELEVEN MANAGEMENT LIMITED | AT | [https://1111-management.com/](https://1111-management.com/) |
| added | other-wp | Biogena GmbH & Co KG | AT | [https://www.biogena.com/biox](https://www.biogena.com/biox) |
| added | other-wp | Crypto Risk Metrics GmbH | DE | [https://crypto-risk-metrics.com/en/white-paper-official-t...](https://crypto-risk-metrics.com/en/white-paper-official-trump-ffg-ljdpgnxxk/) |
| changed | other-wp | OneFootball Capital GmbH | DE | [https://promo.onefootball.com/legal/whitepaper](https://promo.onefootball.com/legal/whitepaper) |
| changed | other-wp | XGR.Network GmbH | DE | [https://xgr.network/whitepaper/](https://xgr.network/whitepaper/) |
| changed | other-wp | WYND Capital GmbH /MD Capital GmbH | DE | [https://wynd.group/](https://wynd.group/) |
| changed | other-wp | Hassan Systems GmbH | DE | [https://getlea.org/](https://getlea.org/) |
| changed | other-wp | Crypto Risk Metrics GmbH | DE | [https://white-paper.crypto-risk-metrics.com/en/doodles-ff...](https://white-paper.crypto-risk-metrics.com/en/doodles-ffg-kf6rx3lr1/index.html) |
| added | other-wp | Crypto Risk Metrics GmbH | DE | [white-paper.crypto-risk-metrics.com/en/kyber-network-crys...](https://white-paper.crypto-risk-metrics.com/en/kyber-network-crystal-v2-ffg-l0dzsblvz/index.html) |
| added | other-wp | Crypto Risk Metrics GmbH | DE | [white-paper.crypto-risk-metrics.com/en/plume-ffg-frzqzj7b...](https://white-paper.crypto-risk-metrics.com/en/plume-ffg-frzqzj7bl/index.html) |
| added | other-wp | Leondra GmbH, Berlin | DE | [https://www.leondrino.de](https://www.leondrino.de) |
| changed | other-wp | BB Trade Estonia OÜ | EE | [https://assets.znd.co/tmpl-token/en/whitepaper.pdf](https://assets.znd.co/tmpl-token/en/whitepaper.pdf) |
| added | other-wp | DELOREAN TECHNOLOGIES GLOBAL, INC. | ES | [https://ws.onehub.com/secure_share/336eogep
https://ws.o...](https://ws.onehub.com/secure_share/336eogep
https://ws.onehub.com/secure_share/1d8l6646) |
| added | other-wp | BILLIONS | ES | [https://billions.network/terms-and-conditions
https://dr...](https://billions.network/terms-and-conditions
https://drive.google.com/file/d/1rYP9Pux9j-8udFvehbBGVKsfH6UktxdL/view?usp=sharing) |
| added | other-wp | CheerBitcoin SASU | FR | [https://drive.google.com/file/d/1IrTRXdr4w8HKdfKBxHZHMJDh...](https://drive.google.com/file/d/1IrTRXdr4w8HKdfKBxHZHMJDhBTDyFysM/view?usp=sharing

https://drive.google.com/file/d/11oWkYWhXIZTSVMDCVV2pC3wDeFTJz3QZ/view?usp=sharing) |
| added | other-wp | CheerBitcoin SASU | FR | [https://drive.google.com/file/d/1DUmluyeGiuYCtPGvwXs_5Gkd...](https://drive.google.com/file/d/1DUmluyeGiuYCtPGvwXs_5Gkdd_NrTAFj/view?usp=drive_link

https://drive.google.com/file/d/1jyCln0cYYT47PdF6oufM_PlMfdRHaHWF/view?usp=drive_link) |
| changed | other-wp | InFlux Technologies Limited | IE | [https://assets-cms.kraken.com/files/51n36hrp/facade/58054...](https://assets-cms.kraken.com/files/51n36hrp/facade/58054248c9b6c4d11df0f30a912bfd098e677fdc.pdf?_gl=1*y154rm*_gcl_au*MTcxOTgwMTU0NC4xNzUwMDk4MDIx*_ga*MTc4ODAyNDUxNC4xNzUwMDk4MDIx*_ga_5MVYWBPCBE*czE3NTI2ODY0MDIkbzE2JGcxJHQxNzUyNjkwMTAzJGoyNiRsMCRoMA..) |
| added | other-wp |  | IE | [https://assets-cms.kraken.com/files/51n36hrp/facade/b2d36...](https://assets-cms.kraken.com/files/51n36hrp/facade/b2d36cdfaf04d6125a97ea8b076a8cbd9b05de59.pdf?_gl=1*19oo0jw*_gcl_au*MTcxOTgwMTU0NC4xNzUwMDk4MDIx*_ga*MTc4ODAyNDUxNC4xNzUwMDk4MDIx*_ga_5MVYWBPCBE*czE3NTM4MDM0ODAkbzI4JGcxJHQxNzUzODA0MDA2JGo1OSRsMCRoMA..) |
| ...and 416 more (see `data/changelog.jsonl`) | | | | |
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
