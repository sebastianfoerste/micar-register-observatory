# MiCAR Register Observatory

A living dashboard of the **ESMA interim MiCAR register**. Every Monday a scheduled job pulls the public register exports (crypto-asset white papers under Titles II–IV, authorised CASPs, non-compliant entities), diffs them against the last snapshot, and rewrites the dashboard below: new filings, changed entries, withdrawals, and how many white papers are published in a machine-readable format.

The register is public by law — Art. 109 Abs. 1 VO (EU) 2023/1114 (MiCAR) requires ESMA to publish white papers and authorisations in a machine-readable register. This repository makes the register's weekly movement visible: what appeared, what changed, what disappeared.

## Dashboard

<!-- dashboard:start -->
**Register snapshot: 2026-09-28** (refreshed weekly from the public ESMA interim MiCAR register)

### Register totals

| Register | Entries | Source status |
| --- | ---: | --- |
| [White papers — other crypto-assets (Title II)](https://www.esma.europa.eu/sites/default/files/2024-12/OTHER.csv) | 1012 | ok |
| [White papers — e-money tokens (Title IV)](https://www.esma.europa.eu/sites/default/files/2024-12/EMTWP.csv) | 49 | ok |
| [White papers — asset-referenced tokens (Title III)](https://www.esma.europa.eu/sites/default/files/2024-12/ARTZZ.csv) | 0 | ok |
| [Authorised crypto-asset service providers (CASPs)](https://www.esma.europa.eu/sites/default/files/2024-12/CASPS.csv) | 362 | ok |
| [Non-compliant entities flagged by NCAs](https://www.esma.europa.eu/sites/default/files/2024-12/NCASP.csv) | 173 | ok |

### White paper format coverage

Classified by link shape only; a format is a deep-lint candidate, not a verified fact, until the document is fetched.

| Linked format | Count | Deep-lint candidate |
| --- | ---: | --- |
| Unspecified (landing page or bare domain) | 641 | no |
| PDF | 263 | no |
| XHTML / HTML | 156 | yes |
| No link in register | 1 | no |

### Home Member States (white papers)

| Member State | White papers |
| --- | ---: |
| IE | 383 |
| MT | 170 |
| DE | 160 |
| NL | 88 |
| LI | 72 |
| LU | 59 |
| FR | 35 |
| LV | 15 |
| AT | 10 |
| FI | 10 |
| ...and 15 more | |

### Changes in this snapshot (2026-09-28)

| Change | Register | Entity | MS | Link |
| --- | --- | --- | --- | --- |
| added | other-wp | Nimiq Network Ltd. | DE | [https://www.nimiq.com/mica-whitepaper.pdf](https://www.nimiq.com/mica-whitepaper.pdf) |
| added | other-wp | Crypto Risk Metrics GmbH | DE | [https://white-paper.crypto-risk-metrics.com/en/spark-ffg-...](https://white-paper.crypto-risk-metrics.com/en/spark-ffg-gs4h3vsb1/index.html) |
| added | other-wp | Crypto Risk Metrics GmbH | DE | [https://white-paper.crypto-risk-metrics.com/en/horizen-ff...](https://white-paper.crypto-risk-metrics.com/en/horizen-ffg-t9ql1zt5d/index.html) |
| added | other-wp | Crypto Risk Metrics GmbH | DE | [https://white-paper.crypto-risk-metrics.com/de/cronos-ffg...](https://white-paper.crypto-risk-metrics.com/de/cronos-ffg-gwm30mlw3/index.html) |
| added | other-wp | Leondra GmbH | DE | [https://www.leondrino.com/xleopre-de/](https://www.leondrino.com/xleopre-de/) |
| added | other-wp | Crypto Risk Metrics GmbH | DE | [https://white-paper.crypto-risk-metrics.com/en/basecat-ff...](https://white-paper.crypto-risk-metrics.com/en/basecat-ffg-k547p69jx/index.html) |
| added | other-wp | Crypto Risk Metrics GmbH | DE | [https://white-paper.crypto-risk-metrics.com/en/grass-ffg-...](https://white-paper.crypto-risk-metrics.com/en/grass-ffg-mncr2mkhp/index.html) |
| added | other-wp | Crypto Risk Metrics GmbH | DE | [https://white-paper.crypto-risk-metrics.com/en/debtrelief...](https://white-paper.crypto-risk-metrics.com/en/debtreliefbot-ffg-7xlw38nzt/index.html) |
| added | other-wp | Crypto Risk Metrics GmbH | DE | [https://white-paper.crypto-risk-metrics.com/en/pudgy-peng...](https://white-paper.crypto-risk-metrics.com/en/pudgy-penguins-ffg-13jbpt88t/index.html) |
| added | other-wp | Crypto Risk Metrics GmbH | DE | [https://white-paper.crypto-risk-metrics.com/en/kava-ffg-2...](https://white-paper.crypto-risk-metrics.com/en/kava-ffg-2hzxzqlkx/index.html) |
| added | other-wp | Crypto Risk Metrics GmbH | DE | [https://white-paper.crypto-risk-metrics.com/en/world-libe...](https://white-paper.crypto-risk-metrics.com/en/world-liberty-financial-ffg-3xvwcvfsx/index.html) |
| added | other-wp | Resonance Foundation | IE | [https://docs.doppler.finance/legal/mica-whitepaper](https://docs.doppler.finance/legal/mica-whitepaper) |
| added | other-wp | Collector Crypt Foundation | IE | [https://collectorcrypt.com/micar.html](https://collectorcrypt.com/micar.html) |
| added | other-wp | IO TRADE LAB LIMITED | IE | [https://iotrader.io/whitepaper.html](https://iotrader.io/whitepaper.html) |
| added | other-wp | Public Goods Labs Ltd. | IE | [https://home.pheasant.network/mica-whitepaper-attr](https://home.pheasant.network/mica-whitepaper-attr) |
| added | other-wp | Public Goods Labs Ltd. | IE | [https://home.pheasant.network/mica-whitepaper-otpc](https://home.pheasant.network/mica-whitepaper-otpc) |
| added | other-wp | Zama Switzerland AG | IE | [https://docs.zama.ai/protocol/mica](https://docs.zama.ai/protocol/mica) |
| added | other-wp | Linear Intent Technologies Ltd. | LV | [https://www.oroswap.org/whitepaper](https://www.oroswap.org/whitepaper) |
| added | other-wp | Fan Token Management AG | MT | [https://www.socios.com/legal-hub/whitepaper/dojo-whitepaper/](https://www.socios.com/legal-hub/whitepaper/dojo-whitepaper/) |
| added | other-wp | Fan Token Management AG | MT | [https://www.socios.com/legal-hub/whitepaper/om-whitepaper/](https://www.socios.com/legal-hub/whitepaper/om-whitepaper/) |
| added | other-wp | SB (BVI) Ltd | MT | [https://storage.googleapis.com/exponential-science-projec...](https://storage.googleapis.com/exponential-science-project1.appspot.com/IXBRL/STONKBROKER%20-%2009-09-2026/STONKBROKER-viewer.xhtml) |
| removed | other-wp | Crypto Risk Metrics GmbH | DE | [https://crypto-risk-metrics.com/en/white-paper-pudgy-peng...](https://crypto-risk-metrics.com/en/white-paper-pudgy-penguins-ffg-13jbpt88t/) |
| removed | other-wp | Crypto Risk Metrics GmbH | DE | [https://crypto-risk-metrics.com/en/white-paper-horizen-ff...](https://crypto-risk-metrics.com/en/white-paper-horizen-ffg-T9QL1ZT5D/) |
| removed | other-wp | Crypto Risk Metrics GmbH | DE | [https://crypto-risk-metrics.com/en/white-paper-spark-ffg-...](https://crypto-risk-metrics.com/en/white-paper-spark-ffg-gs4h3vsb1/) |
| removed | other-wp | Crypto Risk Metrics GmbH | DE | [https://www.crypto-risk-metrics.com/en/white-paper-cronos...](https://www.crypto-risk-metrics.com/en/white-paper-cronos-ffg-gwm30mlw3/) |
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
