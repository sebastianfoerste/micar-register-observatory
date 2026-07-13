# Methodology

## Research question

The observatory separates two questions that require different evidence:

1. What does the ESMA interim register record, and how does that record change over time?
2. What content is actually served by the white-paper link recorded in each row?

A URL ending in `.xhtml` is evidence about a register field. It is not evidence that the server returns an XHTML or Inline XBRL document. All outputs preserve that distinction.

## Legal and technical frame

[MiCAR Articles 6(10), 19(9), and 51(9)](https://eur-lex.europa.eu/eli/reg/2023/1114/oj) require the relevant crypto-asset white papers to be made available in a machine-readable format. [Commission Implementing Regulation (EU) 2024/2984](https://eur-lex.europa.eu/legal-content/EN/TXT/?uri=CELEX:32024R2984) specifies XHTML with Inline XBRL 1.1 and applies from 23 December 2025. MiCAR Article 109 establishes ESMA's public register and describes the information it contains.

The verifier detects technical characteristics. It does not determine whether a document is legally in scope, whether an exception applies, whether the taxonomy is correct, or whether the white paper complies with MiCAR.

## Register sources

The ESMA interim MiCAR register is published as CSV exports at stable URLs and updated in place. The `2024-12` path segment is part of the URL, not a statement that the data is from December 2024.

| Register | Export |
| --- | --- |
| White papers - other crypto-assets (Title II) | <https://www.esma.europa.eu/sites/default/files/2024-12/OTHER.csv> |
| White papers - e-money tokens (Title IV) | <https://www.esma.europa.eu/sites/default/files/2024-12/EMTWP.csv> |
| White papers - asset-referenced tokens (Title III) | <https://www.esma.europa.eu/sites/default/files/2024-12/ARTZZ.csv> |
| Authorised CASPs | <https://www.esma.europa.eu/sites/default/files/2024-12/CASPS.csv> |
| Non-compliant entities | <https://www.esma.europa.eu/sites/default/files/2024-12/NCASP.csv> |

Field semantics come from ESMA's [field-description CSV](https://www.esma.europa.eu/sites/default/files/2024-12/Description_of_the_fields_in_the_interim_MiCA_register.csv).

## Normalization and identity

Each row is reduced to competent authority, home Member State, entity name, LEI, white-paper URL, register last-update date, URL-shape class, and a hash of the full raw row.

Entry identity is `sha256(register | LEI-or-name | wp_url)`, truncated to 16 hexadecimal characters. An entry keeps its identity while its LEI or fallback name and white-paper URL remain stable. Any change in the normalized raw row is observable through `row_hash`.

## Change detection

Weekly snapshots are diffed register by register:

- `added`: identity present now and absent before.
- `changed`: same identity and a different source-row hash.
- `removed`: identity no longer present. This can reflect a withdrawal, correction, deletion, or identity-affecting edit; the observatory does not choose among those explanations without further evidence.
- `baseline`: first observation of a register. Initial rows are not misreported as newly added.

The current snapshot is `data/latest.json`, dated snapshots are under `data/snapshots/`, and the append-only change history is `data/changelog.jsonl`.

## Register-link classification

The first layer classifies only the string in `wp_url`:

- `.xhtml`, `.html`, or `.htm`
- `.json`
- `.docx`
- `.pdf`
- `unspecified` for other paths, landing pages, or bare domains
- `none` when the register row has no link

This is a crawl-planning variable. It must be labelled `register-link class`, `URL-shape class`, or `candidate`. It must not be labelled a verified document format or used as the numerator of a document-format adoption rate.

## Content verification

`python -m observatory verify-content` groups linked register rows by normalized request target, fetches each unique target once per run, and copies the resulting evidence to every row that shares it. The default batch is 25 unique targets; `--limit 0` processes every remaining target. Failed targets can be retried with `--retry-failures`.

For each target the verifier records:

- UTC verification timestamp
- requested and final URL after redirects
- HTTP status
- raw and normalized declared Content-Type
- declared Content-Length, when available
- bytes inspected and whether the response exceeded the ceiling
- SHA-256 of the complete response, but only when it was not truncated
- detected format and detection basis
- whether Inline XBRL markers were observed
- bounded error text when the request failed

The detection order is deterministic:

1. PDF magic bytes
2. ZIP structure, including `word/document.xml` for DOCX
3. successful JSON parse
4. XML or HTML markup signature
5. Inline XBRL element, namespace, or specification markers within the inspected markup
6. `unknown`

Declared MIME type and filename extension are retained as evidence but are never allowed to override the byte-level result. Inline XBRL marker detection establishes that the response appears to contain Inline XBRL markup; it does not validate the instance document, taxonomy, facts, signatures, or legal compliance.

## Coverage and denominators

The dashboard reports both:

- **linked register rows**, because the register can repeat the same target; and
- **unique link targets**, because this is the number of distinct network resources fetched.

Outcome and verified-format counts use unique targets. Register totals and link-shape classes use register rows. Every reported share must name its denominator and the snapshot date. Coverage, failure rate, and `too_large` count must accompany any interpretation of verified-format results.

## Network and reproducibility safeguards

- Only HTTP and HTTPS targets without embedded user credentials are accepted.
- Hostnames are resolved before fetching; any non-public address causes rejection.
- Redirect targets are checked under the same rule.
- The default per-request timeout is 30 seconds.
- The default response ceiling is 25 MiB. A larger response is marked `too_large`, and no complete-response hash is recorded.
- Requests run sequentially with a configurable inter-request delay.
- The scheduled workflow processes a bounded batch and commits the updated snapshot, dashboard, and feed only after the test suite passes.
- Content evidence survives a weekly register refresh only when `entry_id` and `row_hash` are unchanged. A changed source row returns to `not_checked`.

These controls reduce risk and make the evidence auditable. They do not eliminate DNS rebinding, server-side content negotiation, geolocation differences, transient failures, or content changes after verification.

## Prohibited inferences

The repository does not support claims that:

- a URL-shape class is the served document format;
- a PDF-shaped link proves a non-machine-readable white paper;
- an Inline XBRL marker proves a valid or compliant Inline XBRL instance;
- a missing, unreachable, redirected, or unknown response proves issuer non-compliance;
- a `removed` register row is necessarily a withdrawal;
- a partial audit estimates the full-register adoption rate without an explicit sampling design and uncertainty analysis;
- repeated register rows are independent issuer observations.

## Review gate for named findings

Deterministic lint findings about individual named issuers are not published automatically. The separate linter study requires a human legal-review verdict for each candidate finding before publication. Extraction artifacts, applicability questions, and valid `not applicable` disclosures can all produce false positives.

## Known limitations

- The observatory reflects the exports as ESMA publishes them. Upstream corrections and re-keyed rows can appear as changes.
- ESMA may change URLs or column layouts. A failed source is shown in the source-status column and does not silently produce an empty register.
- One URL may serve different bytes by time, location, headers, cookies, or client. The timestamp, final URL, and hash identify only the observed response.
- The interim register may be superseded. Source definitions are centralized in `src/observatory/config.py`.
