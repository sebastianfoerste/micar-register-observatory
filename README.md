# MiCAR Register Observatory

A living dashboard of the **ESMA interim MiCAR register**. Every Monday a scheduled job pulls the public register exports (crypto-asset white papers under Titles II to IV, authorised CASPs, non-compliant entities), diffs them against the last snapshot, and rewrites the dashboard below: new filings, changed entries, withdrawals, and how many white papers are published in a machine-readable format.

The register is public by law. Art. 109 Abs. 1 VO (EU) 2023/1114 (MiCAR) requires ESMA to publish white papers and authorisations in a machine-readable register. This repository makes the register's weekly movement visible: what appeared, what changed, what disappeared.

## Dashboard

<!-- dashboard:start -->
**Register snapshot: 2026-07-27** (refreshed weekly from the public ESMA interim MiCAR register)

### Register totals

| Register | Entries | Source status |
| --- | ---: | --- |
| [White papers - other crypto-assets (Title II)](https://www.esma.europa.eu/sites/default/files/2024-12/OTHER.csv) | 941 | ok |
| [White papers - e-money tokens (Title IV)](https://www.esma.europa.eu/sites/default/files/2024-12/EMTWP.csv) | 41 | ok |
| [White papers - asset-referenced tokens (Title III)](https://www.esma.europa.eu/sites/default/files/2024-12/ARTZZ.csv) | 0 | ok |
| [Authorised crypto-asset service providers (CASPs)](https://www.esma.europa.eu/sites/default/files/2024-12/CASPS.csv) | 312 | ok |
| [Non-compliant entities flagged by NCAs](https://www.esma.europa.eu/sites/default/files/2024-12/NCASP.csv) | 164 | ok |

### White paper format coverage

Classified by link shape only; a format is a deep-lint candidate, not a verified fact, until the document is fetched.

| Linked format | Count | Deep-lint candidate |
| --- | ---: | --- |
| Unspecified (landing page or bare domain) | 604 | no |
| PDF | 254 | no |
| XHTML / HTML | 123 | yes |
| No link in register | 1 | no |

### Register signal room

Movement and integrity signals are deterministic review prompts. They are not findings about a named entity or authority.

**Status: REVIEW_REQUIRED**

| Register | Signal | Added | Changed | Removed | Churn |
| --- | --- | ---: | ---: | ---: | ---: |
| other-wp | review | 16 | 0 | 2 | 1.9% |
| emt-wp | review | 0 | 1 | 0 | 2.4% |
| art-wp | stable | 0 | 0 | 0 | 0.0% |
| casps | review | 16 | 16 | 1 | 11.1% |
| ncasp | review | 0 | 0 | 0 | 0.0% |

- Top home Member State share: IE (35.9%)
- Deep-lint candidates by URL shape: 123/982 (12.5%)
- Signal proof: `0a5478c503c7e02e57365f67a74b081b2a6bb80e45009bacf426ad6686d9ace6`

#### Recent movement context

| Snapshot | Added | Changed | Removed | Total movement |
| --- | ---: | ---: | ---: | ---: |
| 2026-07-07 | 0 | 0 | 0 | 0 |
| 2026-07-13 | 0 | 0 | 0 | 0 |
| 2026-07-20 | 32 | 4 | 2 | 38 |
| 2026-07-27 | 32 | 17 | 3 | 52 |

Current movement is `increased` versus the prior available snapshot. Counts describe register-row movement only.

### Home Member States (white papers)

| Member State | White papers |
| --- | ---: |
| IE | 353 |
| MT | 161 |
| DE | 150 |
| NL | 80 |
| LI | 72 |
| LU | 54 |
| FR | 34 |
| LV | 14 |
| AT | 9 |
| FI | 9 |
| ...and 11 more | |

### Changes in this snapshot (2026-07-27)

| Change | Register | Entity | MS | Link |
| --- | --- | --- | --- | --- |
| added | other-wp | Crypto Risk Metrics GmbH | DE | [https://white-paper.crypto-risk-metrics.com/en/polkadot-d...](https://white-paper.crypto-risk-metrics.com/en/polkadot-dot-ffg-sgd9nltrg/index.html) |
| added | other-wp | Crypto Risk Metrics GmbH | DE | [https://white-paper.crypto-risk-metrics.com/en/graph-toke...](https://white-paper.crypto-risk-metrics.com/en/graph-token-ffg-vmqpvh41w/index.html) |
| added | other-wp | Crypto Risk Metrics GmbH | DE | [https://white-paper.crypto-risk-metrics.com/en/injective-...](https://white-paper.crypto-risk-metrics.com/en/injective-token-ffg-92m9b0dz7/index.html) |
| added | other-wp | VerifiedX LLC | IE | [https://docs.verifiedx.io/docs/documents/mica-whitepaper](https://docs.verifiedx.io/docs/documents/mica-whitepaper) |
| added | other-wp | EarthX Ltd | IE | [https://docs.o1.exchange/token/mica-whitepaper](https://docs.o1.exchange/token/mica-whitepaper) |
| added | other-wp | RWAX Holdings Limited | IE | [https://multipli.fi/legal/micapaper](https://multipli.fi/legal/micapaper) |
| added | other-wp | Stronghold Anchor Limited | IE | [https://stronghold.co/shx-mica-whitepaper.pdf](https://stronghold.co/shx-mica-whitepaper.pdf) |
| added | other-wp | Bitcoin HT, LLC | IE | [https://bitcoin.org.ht/mica-white-paper/](https://bitcoin.org.ht/mica-white-paper/) |
| added | other-wp | Fanpla Inc | IE | [https://fanpla.ch/whitepaper/](https://fanpla.ch/whitepaper/) |
| added | other-wp | Discovery (BVI) Limited | IE | [dscvr.one/whitepaper](https://dscvr.one/whitepaper) |
| added | other-wp | StorX Foundation | IE | [https://storx.tech/pdf/MICA-Whitepaper/](https://storx.tech/pdf/MICA-Whitepaper/) |
| added | other-wp | Cygnus Information Limited | IE | [https://www.cygnus.finance/micar-whitepaper](https://www.cygnus.finance/micar-whitepaper) |
| added | other-wp | Nillion Association | MT | [https://nillion.com/legal/mica/whitepaper/](https://nillion.com/legal/mica/whitepaper/) |
| added | other-wp | Dapp OS Technology Pte. Ltd | NL | [https://dappos.com/mica-white-paper](https://dappos.com/mica-white-paper) |
| added | other-wp | GEODAO FOUNDATION PTE. LTD. | NL | [https://geodnet.micarwhitepaper.eu](https://geodnet.micarwhitepaper.eu) |
| added | other-wp | ProtoWardo Ltd. | NL | [https://runhalo.xyz/halo/micar-whitepaper](https://runhalo.xyz/halo/micar-whitepaper) |
| removed | other-wp | Nillion Association | MT | [https://nillion.com/wp-content/uploads/mica.html](https://nillion.com/wp-content/uploads/mica.html) |
| removed | other-wp | Buck Assets Ltd | MT | [https://staging.buck.foundation/documents/20251216_BuckTo...](https://staging.buck.foundation/documents/20251216_BuckToken_MiCAWhitepaper_V2.pdf) |
| changed | emt-wp | Circle Internet Financial Europe SAS | FR | [https://www.circle.com/fr/legal/mica-usdc-whitepaper](https://www.circle.com/fr/legal/mica-usdc-whitepaper) |
| added | casps | BNY SA/NV | BE |  |
| added | casps | Belayer ООD | BG |  |
| added | casps | Altcoins BG EООD | BG |  |
| added | casps | Digital Assist OOD | BG |  |
| changed | casps | S.K. DASK KRYPTO LTD | CY |  |
| changed | casps | Ronin EM Ltd | CY |  |
| ...and 27 more (see `data/changelog.jsonl`) | | | | |
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

- **New, changed, and removed register entries** per weekly snapshot, including white paper withdrawals, which the register itself does not announce.
- **Format coverage**: how many linked white papers are XHTML/HTML, JSON, or DOCX (candidates for deterministic linting with [micar-whitepaper-linter](https://github.com/sebastianfoerste/micar-whitepaper-linter)) versus PDF or a bare landing-page domain. Classification is by link shape only and is marked as candidate, not verified, until a document is fetched.
- **Machine-readable feed**: `docs/feed.json` carries the current totals and recent changes for anyone building on top.
- **Register signal room**: [`docs/signals.json`](docs/signals.json) records source failures,
  duplicate IDs, removal and churn thresholds, home-state concentration, and
  deep-lint candidate coverage with an input-bound SHA-256 proof. A recent
  movement window separates one-week noise from the available multi-snapshot
  context. Signals remain review prompts and do not make findings about named
  entities.

Deep-lint findings on individual white papers are deliberately **not** auto-published here. Rule findings against named issuers go through human legal review first; the review-gated study lives in the [linter repository](https://github.com/sebastianfoerste/micar-whitepaper-linter). A flag from a deterministic rule is a candidate gap in extracted text, not a confirmed deficiency by the named issuer.

## Method and limits

See [docs/methodology.md](docs/methodology.md) for sources, normalization, change detection, and known limitations. Two that matter most: the observatory reflects the register exports as published (upstream corrections appear as "changed" entries), and format classification is a URL-shape heuristic until documents are fetched.

## Legal

The underlying data is ESMA's public register. This repository records factual observations about that register; it contains no legal assessment of any issuer or service provider and is not legal advice. Code is MIT-licensed.
