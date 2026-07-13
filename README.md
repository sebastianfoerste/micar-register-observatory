# MiCAR Register Observatory

A reproducible monitor of the **ESMA interim MiCAR register**. A scheduled job pulls the public register exports, normalizes and diffs every row, and publishes a machine-readable change feed. A separate verification pipeline inspects the bytes served by white-paper links and records hash-based evidence without treating a URL suffix or HTTP header as proof of document format.

The distinction matters. The register tells us which URL was filed. Only a bounded fetch can tell us what that URL actually serves. This repository keeps those two observations separate.

MiCAR Article 109 requires ESMA to maintain the public register. The legal requirements governing white-paper machine readability sit in the relevant white-paper provisions and implementing technical standards; the observatory reports technical observations and does not make compliance findings.

## Dashboard

<!-- dashboard:start -->
**Register snapshot: 2026-07-13** (refreshed weekly from the public ESMA interim MiCAR register)

### Register totals

| Register | Entries | Source status |
| --- | ---: | --- |
| [White papers - other crypto-assets (Title II)](https://www.esma.europa.eu/sites/default/files/2024-12/OTHER.csv) | 912 | ok |
| [White papers - e-money tokens (Title IV)](https://www.esma.europa.eu/sites/default/files/2024-12/EMTWP.csv) | 41 | ok |
| [White papers - asset-referenced tokens (Title III)](https://www.esma.europa.eu/sites/default/files/2024-12/ARTZZ.csv) | 0 | ok |
| [Authorised crypto-asset service providers (CASPs)](https://www.esma.europa.eu/sites/default/files/2024-12/CASPS.csv) | 283 | ok |
| [Non-compliant entities flagged by NCAs](https://www.esma.europa.eu/sites/default/files/2024-12/NCASP.csv) | 162 | ok |

### White-paper register-link coverage

These classes describe the URL recorded by ESMA, not the bytes served by that URL. They identify crawl candidates and must not be reported as document-format prevalence.

| Register-link class | Count | Deep-lint candidate |
| --- | ---: | --- |
| Unspecified (landing page or bare domain) | 584 | no |
| PDF-shaped link | 254 | no |
| XHTML / HTML-shaped link | 114 | yes |
| No link in register | 1 | no |

### Content verification

Byte-level checks use bounded downloads, redirects, response metadata, file signatures, ZIP structure, JSON parsing, markup signatures, and Inline XBRL namespace or element markers. URL suffixes and declared Content-Type are not accepted as proof.

**Checked: 0/924 unique link targets (0.0%), covering 0/952 linked register rows.**

| Outcome | Count |
| --- | ---: |
| Complete response with SHA-256 | 0 |
| Exceeded byte limit | 0 |
| Fetch or HTTP failure | 0 |
| Verified Inline XBRL document | 0 |

No linked documents have been content-verified in the committed snapshot yet. Run `python -m observatory verify-content --limit 25` to create the first auditable batch.

### Home Member States (white papers)

| Member State | White papers |
| --- | ---: |
| IE | 340 |
| MT | 159 |
| DE | 145 |
| NL | 74 |
| LI | 72 |
| LU | 53 |
| FR | 32 |
| LV | 14 |
| AT | 9 |
| FI | 9 |
| ...and 11 more | |

### Changes in this snapshot (2026-07-13)

No register changes since the previous snapshot.
<!-- dashboard:end -->

## Reproduce it

```bash
git clone https://github.com/sebastianfoerste/micar-register-observatory
cd micar-register-observatory
make install && make test
make refresh

# Verify the next 25 unchecked white-paper URLs.
python -m observatory verify-content --limit 25

# Verify every remaining URL and retry earlier failures.
python -m observatory verify-content --limit 0 --retry-failures
```

`make refresh` fetches the five register CSVs, writes a dated snapshot under `data/snapshots/`, appends changes to `data/changelog.jsonl`, and regenerates this README and `docs/feed.json`. Content evidence is retained across refreshes only when the source row is unchanged. A changed row returns to `not_checked`.

The content verifier is intentionally bounded. It accepts only public HTTP(S) destinations, rejects user credentials and non-public resolved IP addresses, rechecks redirect targets, applies a per-request timeout and 25 MiB byte ceiling, and records a complete-content SHA-256 only when the response was not truncated.

## What this tracks

- **Register movement:** added, changed, and removed rows per weekly snapshot. Removal is an observation about the export, not automatically a legal withdrawal.
- **Register-link classes:** URL-shape candidates such as `.xhtml`, `.pdf`, and landing pages. These are navigation metadata, not verified formats.
- **Content evidence:** requested and final URLs, verification timestamp, HTTP status, declared Content-Type and length, bytes inspected, truncation state, complete-response SHA-256, detected format, detection basis, and Inline XBRL markers.
- **Machine-readable feed:** `docs/feed.json` carries register totals, link-shape counts, content-verification coverage, and recent changes.

Deterministic lint flags about individual white papers are deliberately not auto-published here. Named-issuer findings require human legal review in the [MiCAR white-paper linter study](https://github.com/sebastianfoerste/micar-whitepaper-linter). A rule flag is a candidate gap in extracted text, not a confirmed deficiency.

## Method and limits

See [docs/methodology.md](docs/methodology.md) for source definitions, normalization, change detection, content-verification rules, and prohibited inferences. In particular, do not infer document-format prevalence from register-link shapes, and do not generalize verified-format shares until the content audit has stated coverage, failure rates, and a reproducible denominator.

## Legal

The underlying data is ESMA's public register. This repository records factual, reproducible observations about that register; it contains no legal assessment of any issuer or service provider and is not legal advice. Code is MIT-licensed.
