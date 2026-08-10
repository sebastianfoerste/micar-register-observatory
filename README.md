# MiCAR Register Observatory

A living dashboard of the **ESMA interim MiCAR register**. Every Monday a scheduled job pulls the public register exports (crypto-asset white papers under Titles II–IV, authorised CASPs, non-compliant entities), diffs them against the last snapshot, and rewrites the dashboard below: new filings, changed entries, withdrawals, and how many white papers are published in a machine-readable format.

The register is public by law — Art. 109 Abs. 1 VO (EU) 2023/1114 (MiCAR) requires ESMA to publish white papers and authorisations in a machine-readable register. This repository makes the register's weekly movement visible: what appeared, what changed, what disappeared.

## Dashboard

<!-- dashboard:start -->
**Register snapshot: 2026-08-10** (refreshed weekly from the public ESMA interim MiCAR register)

### Register totals

| Register | Entries | Source status |
| --- | ---: | --- |
| [White papers — other crypto-assets (Title II)](https://www.esma.europa.eu/sites/default/files/2024-12/OTHER.csv) | 872 | ok |
| [White papers — e-money tokens (Title IV)](https://www.esma.europa.eu/sites/default/files/2024-12/EMTWP.csv) | 42 | ok |
| [White papers — asset-referenced tokens (Title III)](https://www.esma.europa.eu/sites/default/files/2024-12/ARTZZ.csv) | 0 | ok |
| [Authorised crypto-asset service providers (CASPs)](https://www.esma.europa.eu/sites/default/files/2024-12/CASPS.csv) | 329 | ok |
| [Non-compliant entities flagged by NCAs](https://www.esma.europa.eu/sites/default/files/2024-12/NCASP.csv) | 167 | ok |

### White paper format coverage

Classified by link shape only; a format is a deep-lint candidate, not a verified fact, until the document is fetched.

| Linked format | Count | Deep-lint candidate |
| --- | ---: | --- |
| Unspecified (landing page or bare domain) | 588 | no |
| PDF | 256 | no |
| XHTML / HTML | 68 | yes |
| No link in register | 2 | no |

### Home Member States (white papers)

| Member State | White papers |
| --- | ---: |
| IE | 361 |
| MT | 149 |
| DE | 111 |
| NL | 84 |
| LI | 71 |
| LU | 38 |
| FR | 28 |
| LV | 14 |
| AT | 9 |
| FI | 9 |
| ...and 9 more | |

### Changes in this snapshot (2026-08-10)

| Change | Register | Entity | MS | Link |
| --- | --- | --- | --- | --- |
| added | other-wp | KUBE ECOSYSTEM S.L. | ES | [https://www.kubecoin.org/](https://www.kubecoin.org/) |
| added | other-wp | COOL EARTH COIN, S.A. | ES | [www.coolearthcoin.com](https://www.coolearthcoin.com) |
| changed | other-wp | MiCA Crypto Alliance Opco Limited | IE | [http://www.micacryptoalliance.com/reports/lion-mica-white...](http://www.micacryptoalliance.com/reports/lion-mica-white-paper) |
| changed | other-wp | Rails ServicesCo (BVI) Ltd. | IE | [https://rails.xyz/mica-whitepaper](https://rails.xyz/mica-whitepaper) |
| added | other-wp | KulaDAO Foundation Limited | IE | [https://cdn.prod.website-files.com/67cd88c9c7cb5a25c8bf89...](https://cdn.prod.website-files.com/67cd88c9c7cb5a25c8bf89be/6998496139debbabce1f2aa0_Kula%20__%20MiCA%20White%20Paper.pdf) |
| added | other-wp | ALLORA FOUNDATION | IE | [https://research.assets.allora.network/allora.mica](https://research.assets.allora.network/allora.mica) |
| added | other-wp | Hexagon Foundation Ltd. | IE | [https://wingbits.com/assets/documents/wingbits-white-pape...](https://wingbits.com/assets/documents/wingbits-white-paper.pdf?_gl=1*6dyayj*_up*MQ..*_ga*MjAxOTA3NjgwMC4xNzc0MDE3OTE4*_ga_WM2P6S7YY0*czE3NzQwMTc5MTgkbzEkZzAkdDE3NzQwMTc5MTgkajYwJGwwJGgw) |
| added | other-wp | Birbish Limited | IE | [https://moonbirds.com/mica](https://moonbirds.com/mica) |
| added | other-wp | DuckChain Foundation | IE | [https://duckchain.io/micar/DuckChain_MiCAR_WP.html](https://duckchain.io/micar/DuckChain_MiCAR_WP.html) |
| added | other-wp | PepeCoin Co. | IE | [https://www.pepecoin.io/mica/pepecoin-mica-whitepaper.xhtml](https://www.pepecoin.io/mica/pepecoin-mica-whitepaper.xhtml) |
| added | other-wp | ETHGas Ltd. | IE | [https://www.ethgas.com/mica-whitepaper](https://www.ethgas.com/mica-whitepaper) |
| added | other-wp | Tea Association | IE | [https://docs.tea.xyz/staging/qovCbhhrNAC2BmXR97Rg/tea-net...](https://docs.tea.xyz/staging/qovCbhhrNAC2BmXR97Rg/tea-network-micar-whitepaper) |
| added | other-wp | Beldex International Foundation | IE | [https://www.beldex.io/BDX_MiCA_Whitepaper.xhtml](https://www.beldex.io/BDX_MiCA_Whitepaper.xhtml) |
| added | other-wp | VX Eight Ltd. | IE | [https://vibe.infiniteuniverse.xyz/MiCAWhitepaper.xhtml](https://vibe.infiniteuniverse.xyz/MiCAWhitepaper.xhtml) |
| added | other-wp | VeChain Foundation San Marino S.R.L. | IE | [https://files.vebetter.com/vebetterdaocontainer/B3TR-Whit...](https://files.vebetter.com/vebetterdaocontainer/B3TR-White-Paper-MICAR.pdf) |
| added | other-wp | Luminary Digital Ltd | IE | [https://cdn.prod.website-files.com/69b1cc4ec2add76ed52e5b...](https://cdn.prod.website-files.com/69b1cc4ec2add76ed52e5bb2/69b1cc4ec2add76ed52e6381_3aa93988804faabf596e8e5541f55819_LumiTokenWP.pdf) |
| added | other-wp | Reppo Foundation | IE | [https://reppo-labs-xyz.gitbook.io/reppo-labs/whitepaper](https://reppo-labs-xyz.gitbook.io/reppo-labs/whitepaper) |
| added | other-wp | Bluefin Holdings Limited | IE | [http://bluefin.io/foundation/mica-whitepaper](http://bluefin.io/foundation/mica-whitepaper) |
| added | other-wp | Amnis AI Inc. | IE | [https://docs.amnis.finance/mica](https://docs.amnis.finance/mica) |
| added | other-wp | SYNAPSE LABS INC | IE | [https://docs.into.space/en/resources/micar-whitepaper](https://docs.into.space/en/resources/micar-whitepaper) |
| added | other-wp | Rain Foundation | IE | [https://whitepaper.rain.one/](https://whitepaper.rain.one/) |
| added | other-wp | NESA LABS INC | IE | [https://nesa.ai/micar-whitepaper](https://nesa.ai/micar-whitepaper) |
| added | other-wp | edgeX DAO Limited | IE | [https://www.edgex.exchange/mica_whitepaper](https://www.edgex.exchange/mica_whitepaper) |
| added | other-wp | Neo Global Development Ltd | IE | [https://x.neo.org/mica/neo-whitepaper](https://x.neo.org/mica/neo-whitepaper) |
| added | other-wp | Neo Global Development Ltd | IE | [https://x.neo.org/mica/gas-whitepaper](https://x.neo.org/mica/gas-whitepaper) |
| ...and 113 more (see `data/changelog.jsonl`) | | | | |
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
