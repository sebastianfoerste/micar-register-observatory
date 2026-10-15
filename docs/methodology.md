# Methodology

## Sources

The ESMA interim MiCAR register, published as CSV exports at stable URLs and updated in place (the `2024-12` path segment is part of the URL, not a data date; freshness comes from the HTTP `Last-Modified` header):

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

Weekly snapshots are diffed register by register. Rows are compared within each entry identity as a multiset, because several rows can share one identity (a firm with two authorisations, an issuer with several tokens behind one URL): identical rows pair first, then rows with the same `row_key`, then the most similar rows. Every row of both exports is accounted for.

- `added` — a row that the previous export did not list and that is not a row coming back.
- `changed` — a row paired with a previous row whose content differs. The record lists each ESMA column that differs with its old and new value (`changed_fields`) and mechanical labels such as `withdrawal_date_recorded` or `services_added` (`subtypes`).
- `missing` — a row of the previous export that this export does not list. A first absence is not reported as a removal: the export has dropped hundreds of rows for a week and listed them again.
- `removed` — a row absent from two consecutive exports. It can be a withdrawal, an upstream correction, or an identity-affecting edit (an issuer changing its white paper URL appears as `missing`, then `removed`, plus `added`); the export does not say which.
- `restored` — a row listed again after it was `missing` or `removed`. Only as many rows of an entry identity are restored as left it.
- `baseline` — first observation of a register; the initial population is not reported as hundreds of "added" rows.

Each record carries `record_version`. Records without it (version 1, every record up to the 2026-10-12 snapshot) were written by the earlier diff, which compared one row per entry identity, used `removed` for a first absence and `added` for a row that came back. Recorded history is never rewritten; version 2 code reads both.

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
