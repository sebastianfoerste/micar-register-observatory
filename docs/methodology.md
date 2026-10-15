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

Every row keeps all of its ESMA columns verbatim (`fields`). Next to them sit typed fields that are mechanical normalizations of those columns: ISO dates (authorisation, withdrawal, offer start, decision), the CASP services as letters a–j (read from the service text, because some letter prefixes in the export contradict it), service and offer countries, the DTI FFG and DTIs, the CASP named on Title II records, the non-compliant entity's stated reason, and comments. `last_update` reads each register's own last-update column (`wp_lastupdate`, `ac_lastupdate`, `ae_lastupdate`). Header lines repeated inside an export are skipped; snapshots written before these fields existed stored them as entries, and the diff and the dashboard ignore them. Snapshots up to 2026-10-12 hold only the core fields.

The entry identity is `entry_id = sha256(register | LEI-or-name | wp_url)`, unchanged since the first snapshot, so an entry keeps its identity as long as its LEI (or name) and white paper URL are stable. It is not unique: a CASP with a second authorisation row, or an issuer with several tokens behind one URL, shares its `entry_id` with its other rows. In the 2026-10-12 snapshot 1,631 rows had 1,597 distinct entry identities. `row_key` adds what tells such rows apart: the DTI FFG, the DTIs and the CASP's LEI for white papers, the authorisation date for CASPs, and the decision date for non-compliant entities. `row_hash` hashes the full raw row, so a change to any column surfaces as `changed`.

Counts distinguish rows from entities. An entity is a distinct LEI, or a name where a row has none; on 2026-10-12 the CASP export had 370 rows for 367 firms.

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

### Quarantine

An export is set aside instead of recorded when one of its registers lost more than 10% of its rows, and at least 10 rows, since the last recorded snapshot (`MAX_WEEKLY_SHRINK` and `MIN_SHRINK_ROWS` in `src/observatory/config.py`). It is kept as `data/quarantine/<date>.json`, in the snapshot format. `data/latest.json`, the dated snapshots and the changelog stay as they were, and the dashboard and `docs/feed.json` (`quarantine`) say which export was set aside and why. When the next export shows the same register just as far below the last recorded snapshot, the drop is recorded: its rows become `missing` and, if they stay absent, `removed` a week later. A maintainer who has confirmed a drop can record it at once with `python -m observatory refresh --accept-shrink`.

The rule exists because the Title II export fell from 941 to 783 rows on 2026-08-03 and was back within two weeks; recorded as it was, that one export produced 250 removal records. Replayed over the committed snapshots, the rule sets aside that export and no other.

## Format coverage

White paper links are classified by URL shape: `.xhtml`/`.html`/`.htm`, `.json`, `.docx` (parseable by [micar-whitepaper-linter](https://github.com/sebastianfoerste/micar-whitepaper-linter)), `.pdf`, or `unspecified` for bare domains and landing pages. The observatory does not crawl issuer sites; a class is a candidate until the document is fetched. Many register rows link a landing page rather than the document itself — that gap is itself a finding about register quality.

## Review gate for findings

Deterministic lint findings about individual, named issuers are not published automatically. The pipeline that produces such findings (rule, extracted evidence, source URL) requires a human legal review verdict per finding before anything is stated about a named party. Rationale: a deterministic rule flags candidate gaps in extracted text; extraction artifacts exist (e.g. populated "N/A" table cells misread as missing disclosures), and asserting a disclosure gap against a named issuer without review would be a wrong factual claim, public source or not.

## Known limitations

- The observatory sees what ESMA exports. Upstream corrections, deletions, and re-keyed rows appear as register changes even when nothing changed at the issuer.
- ESMA may change export URLs or column layouts. A source that fails to download, lacks a required column or falls below its row floor stops the refresh, and the last good snapshot stays in place; added or dropped columns are reported as a source change without stopping it.
- Format classification is a heuristic on the link, not the served content type.
- The interim register may be superseded by ESMA's final register infrastructure; sources are pinned in `src/observatory/config.py` and are the single place to update.
