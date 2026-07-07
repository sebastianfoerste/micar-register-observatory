# Methodology

## Sources

The ESMA interim MiCA register, published as CSV exports at stable URLs and updated in place (the `2024-12` path segment is part of the URL, not a data date; freshness comes from the HTTP `Last-Modified` header):

| Register | Export |
| --- | --- |
| White papers — other crypto-assets (Title II) | <https://www.esma.europa.eu/sites/default/files/2024-12/OTHER.csv> |
| White papers — e-money tokens (Title IV) | <https://www.esma.europa.eu/sites/default/files/2024-12/EMTWP.csv> |
| White papers — asset-referenced tokens (Title III) | <https://www.esma.europa.eu/sites/default/files/2024-12/ARTZZ.csv> |
| Authorised CASPs | <https://www.esma.europa.eu/sites/default/files/2024-12/CASPS.csv> |
| Non-compliant entities | <https://www.esma.europa.eu/sites/default/files/2024-12/NCASP.csv> |

Field semantics: ESMA's own [field description CSV](https://www.esma.europa.eu/sites/default/files/2024-12/Description_of_the_fields_in_the_interim_MiCA_register.csv). Legal basis for publication: Art. 109 VO (EU) 2023/1114 (MiCAR).

## Normalization

Each row is reduced to: competent authority, home Member State, entity name, LEI, white paper URL, register last-update date, plus a hash of the full raw row. The entry identity is `sha256(register | LEI-or-name | wp_url)`, so an entry keeps its identity across snapshots as long as its LEI (or name) and white paper URL are stable. A change to any other field surfaces as a `changed` record via the row hash.

## Change detection

Weekly snapshots are diffed register by register:

- `added` — entry identity present now, absent before.
- `changed` — same identity, different row content.
- `removed` — entry identity no longer in the export. This includes withdrawals, upstream corrections, and identity-affecting edits (an issuer changing its white paper URL appears as `removed` + `added`).
- `baseline` — first observation of a register; the initial population is not reported as hundreds of "added" rows.

The full history is `data/changelog.jsonl`; dated snapshots live under `data/snapshots/`.

## Format coverage

White paper links are classified by URL shape: `.xhtml`/`.html`/`.htm`, `.json`, `.docx` (parseable by [micar-whitepaper-linter](https://github.com/sebastianfoerste/micar-whitepaper-linter)), `.pdf`, or `unspecified` for bare domains and landing pages. The observatory does not crawl issuer sites; a class is a candidate until the document is fetched. Many register rows link a landing page rather than the document itself — that gap is itself a finding about register quality.

## Review gate for findings

Deterministic lint findings about individual, named issuers are not published automatically. The pipeline that produces such findings (rule, extracted evidence, source URL) requires a human legal review verdict per finding before anything is stated about a named party. Rationale: a deterministic rule flags candidate gaps in extracted text; extraction artifacts exist (e.g. populated "N/A" table cells misread as missing disclosures), and asserting a disclosure gap against a named issuer without review would be a wrong factual claim, public source or not.

## Known limitations

- The observatory sees what ESMA exports. Upstream corrections, deletions, and re-keyed rows appear as register changes even when nothing changed at the issuer.
- ESMA may change export URLs or column layouts; a failed source is reported in the dashboard's source-status column and never fails the whole run silently.
- Format classification is a heuristic on the link, not the served content type.
- The interim register may be superseded by ESMA's final register infrastructure; sources are pinned in `src/observatory/config.py` and are the single place to update.
