# MiCAR Register Observatory

A living dashboard of the **ESMA interim MiCAR register**. Every Monday a scheduled job pulls the public register exports (crypto-asset white papers under Titles II–IV, authorised CASPs, non-compliant entities), diffs them against the last snapshot, and rewrites the dashboard below: new filings, changed entries, withdrawals, and how many white papers are published in a machine-readable format.

The register is public by law — Art. 109 Abs. 1 VO (EU) 2023/1114 (MiCAR) requires ESMA to publish white papers and authorisations in a machine-readable register. This repository makes the register's weekly movement visible: what appeared, what changed, what disappeared.

## Dashboard

<!-- dashboard:start -->
**Register snapshot: 2026-07-20** (refreshed weekly from the public ESMA interim MiCAR register)

### Register totals

| Register | Entries | Source status |
| --- | ---: | --- |
| [White papers — other crypto-assets (Title II)](https://www.esma.europa.eu/sites/default/files/2024-12/OTHER.csv) | 926 | ok |
| [White papers — e-money tokens (Title IV)](https://www.esma.europa.eu/sites/default/files/2024-12/EMTWP.csv) | 41 | ok |
| [White papers — asset-referenced tokens (Title III)](https://www.esma.europa.eu/sites/default/files/2024-12/ARTZZ.csv) | 0 | ok |
| [Authorised crypto-asset service providers (CASPs)](https://www.esma.europa.eu/sites/default/files/2024-12/CASPS.csv) | 297 | ok |
| [Non-compliant entities flagged by NCAs](https://www.esma.europa.eu/sites/default/files/2024-12/NCASP.csv) | 164 | ok |

### White paper format coverage

Classified by link shape only; a format is a deep-lint candidate, not a verified fact, until the document is fetched.

| Linked format | Count | Deep-lint candidate |
| --- | ---: | --- |
| Unspecified (landing page or bare domain) | 592 | no |
| PDF | 254 | no |
| XHTML / HTML | 120 | yes |
| No link in register | 1 | no |

### Home Member States (white papers)

| Member State | White papers |
| --- | ---: |
| IE | 344 |
| MT | 162 |
| DE | 146 |
| NL | 77 |
| LI | 72 |
| LU | 54 |
| FR | 34 |
| LV | 14 |
| AT | 9 |
| FI | 9 |
| ...and 11 more | |

### Changes in this snapshot (2026-07-20)

| Change | Register | Entity | MS | Link |
| --- | --- | --- | --- | --- |
| added | other-wp | Crypto Risk Metrics GmbH | DE | [https://white-paper.crypto-risk-metrics.com/en/official-t...](https://white-paper.crypto-risk-metrics.com/en/official-trump-ffg-ljdpgnxxk/index.html) |
| added | other-wp | Crypto Risk Metrics GmbH | DE | [https://white-paper.crypto-risk-metrics.com/en/pepe-ffg-j...](https://white-paper.crypto-risk-metrics.com/en/pepe-ffg-j41r6pf81/index.html) |
| added | other-wp | Injective Foundation | DK | [https://injective.com/research](https://injective.com/research) |
| added | other-wp | SBorg SA | FR | [https://swissborg.com](https://swissborg.com) |
| added | other-wp | TCG-VAULT | FR | [https://www.tcg-vault.io/livre-blanc-mica](https://www.tcg-vault.io/livre-blanc-mica) |
| added | other-wp | Axon Tech Ltd. | IE | [https://paper.chainopera.ai](https://paper.chainopera.ai) |
| added | other-wp | ICON Foundation | IE | [https://www.icon.foundation/publications/soda-mica-whitep...](https://www.icon.foundation/publications/soda-mica-whitepaper/soda-mica-whitepaper-3532007.xhtml) |
| added | other-wp | Wojak CTO LLC | IE | [https://wojakcto.com/whitepaper](https://wojakcto.com/whitepaper) |
| added | other-wp | Grove (BVI) Ltd. | IE | [grove.micarwhitepapers.eu](https://grove.micarwhitepapers.eu) |
| added | other-wp | New Frame Limited | LU | [https://checkmate.foundation/MiCA Whitepaper - Checkmate ...](https://checkmate.foundation/MiCA Whitepaper - Checkmate - CHECK.xhtml) |
| changed | other-wp | BlockBen SIA | LV | [https://blockben.com/en/products/ebso](https://blockben.com/en/products/ebso) |
| added | other-wp | Based Foundation | MT | [https://my.okx.com/whitepaper/based-based.xhtml](https://my.okx.com/whitepaper/based-based.xhtml) |
| added | other-wp | Open Oracle Association | MT | [https://www.seda.xyz/whitepaper](https://www.seda.xyz/whitepaper) |
| added | other-wp | Opentensor Foundation | MT | [https://my.okx.com/whitepaper/bittensor-tao.xhtml](https://my.okx.com/whitepaper/bittensor-tao.xhtml) |
| changed | other-wp | TownSquare Services Ltd. | NL | [https://townsquare.micarwhitepapers.eu](https://townsquare.micarwhitepapers.eu) |
| added | other-wp | Dac Labs Sagl | NL | [https://dact.micarwhitepapers.eu/](https://dact.micarwhitepapers.eu/) |
| added | other-wp | Genius Foundation | NL | [https://www.tradegenius.com/micaeucompliance](https://www.tradegenius.com/micaeucompliance) |
| added | other-wp | Ethos Foundation | NL | [https://ethos.micarwhitepapers.eu/](https://ethos.micarwhitepapers.eu/) |
| removed | other-wp | Crypto Risk Metrics GmbH | DE | [https://crypto-risk-metrics.com/en/white-paper-official-t...](https://crypto-risk-metrics.com/en/white-paper-official-trump-ffg-ljdpgnxxk/) |
| removed | other-wp | Injective Foundation | DK | [https://injective.com/](https://injective.com/) |
| added | casps | OSL EU GmbH | AT |  |
| added | casps | Brilliantscope Trading Limited | CY |  |
| added | casps | Volksbank Schwarzwald-Donau-Neckar eG | DE |  |
| added | casps | Raiffeisebank Auerbach-Freihung eG | DE |  |
| added | casps | IQANA TECHNOLOGIES S.L. | ES |  |
| ...and 13 more (see `data/changelog.jsonl`) | | | | |
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
