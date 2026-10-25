# Data dictionary

The files the observatory publishes, and what each field means. Fields are only ever added, never renamed, removed or redefined: [eu-reg-mcp](https://github.com/sebastianfoerste/eu-reg-mcp) and other consumers read these files from `main`. The JSON Schemas in [`contracts/`](../contracts/) are checked by the test suite against the committed data and against the pipeline's own output.

ESMA's meaning of each source column is in its [field description file](https://www.esma.europa.eu/sites/default/files/2024-12/Description_of_the_fields_in_the_interim_MiCA_register.csv). How rows are matched and changes detected is in [methodology.md](methodology.md).

## Files

| File | Content | Contract |
| --- | --- | --- |
| `data/latest.json` | The latest recorded snapshot of all five registers. | [snapshot v1](../contracts/micar-register.snapshot.v1.schema.json); [v2](../contracts/micar-register.snapshot.v2.schema.json) from October 2026 |
| `data/snapshots/YYYY-MM-DD.json` | Every recorded snapshot, one per weekly refresh since 2026-07-07. | as `latest.json` |
| `data/quarantine/YYYY-MM-DD.json` | An export set aside after a sharp drop in rows; it is not part of the recorded history (see [methodology](methodology.md#quarantine)). | as `latest.json` |
| `data/raw/YYYY-MM-DD/` | From October 2026: the five exports of a refresh as downloaded, gzipped (`<slug>.csv.gz`), with `manifest.json` (below). Kept for recorded and quarantined exports alike. | [raw manifest v1](../contracts/raw-manifest.v1.schema.json) |
| `data/changelog.jsonl` | One change record per line, oldest first. | [changelog v1](../contracts/changelog.v1.schema.json), one record per line |
| `docs/feed.json` | Current totals and the last 200 change records. | [feed v1](../contracts/feed.v1.schema.json) |
| `data/exports/{casps,ncasp,whitepapers,changes}.csv` | From October 2026: the latest snapshot's rows and every change record as flat CSV (below). | [exports v1](../contracts/exports.v1.schema.json) |
| `docs/changes.atom` | From October 2026: an Atom feed with one entry per recorded snapshot, newest first (the last 52), linking to its digest. | [Atom (RFC 4287)](https://www.rfc-editor.org/rfc/rfc4287) |
| `digests/YYYY-MM-DD.md` | From October 2026: a readable note of each recorded snapshot's changes. A digest is written once; only the latest is rewritten. | |

Snapshots written before October 2026 carry the v1 fields only; snapshots written from then on carry the v2 fields as well, and remain valid v1 snapshots.

## Snapshot

| Field | Meaning |
| --- | --- |
| `snapshot_date` | Date of the weekly refresh (YYYY-MM-DD). It is the date the export was fetched, not the date ESMA last changed it. |
| `registers` | One object per register, in the order other-wp, emt-wp, art-wp, casps, ncasp. |

### Register

| Field | Since | Meaning |
| --- | --- | --- |
| `slug` | v1 | `other-wp` (Title II white papers, `OTHER.csv`), `emt-wp` (e-money tokens, `EMTWP.csv`), `art-wp` (asset-referenced tokens, `ARTZZ.csv`), `casps` (authorised CASPs, `CASPS.csv`), `ncasp` (non-compliant entities, `NCASP.csv`). |
| `title` | v1 | Human-readable register name. |
| `kind` | v1 | `whitepaper` or `entity`. |
| `source_url` | v1 | The ESMA export the rows come from. |
| `fetched` | v1 | Whether the export was downloaded and parsed. A recorded snapshot always has `true` for every register: the refresh stops when one fails. |
| `fetch_error` | v1 | The error when `fetched` is false. |
| `entries` | v1 | The register's rows, in the export's order. |
| `columns` | v2 | The export's header, in ESMA's order. |
| `source_last_modified` | v2 | The HTTP `Last-Modified` header of the downloaded export, verbatim (for example `Tue, 07 Oct 2026 09:12:44 GMT`): when ESMA last replaced the file. `""` when the server sent none. |
| `source_sha256` | v2 | SHA-256 of the downloaded bytes; the same bytes are archived under `data/raw/<snapshot_date>/`. |

### Entry (one row of an export)

Typed fields are mechanical normalizations of the verbatim columns in `fields`. The v1 fields and `comments` are verbatim. The other typed text fields are `""` when the column is blank or holds a placeholder such as `-`, `n/a` or `Not applicable`, and dates are `""` when blank or not a valid date.

| Field | Since | Type | Meaning | Source column |
| --- | --- | --- | --- | --- |
| `entry_id` | v1 | 16 hex chars | Entry identity: the first 16 hex characters of SHA-256 over `register \| LEI-or-name \| wp_url`, lower-cased. Stable since 2026-07-07. **Not unique**: a firm with two authorisation rows, or an issuer with several tokens behind one URL, shares it with its other rows. | |
| `register_slug` | v1 | string | The register's `slug`. | |
| `authority` | v1 | string | National competent authority, verbatim. | `ae_competentAuthority` |
| `member_state` | v1 | string | Home Member State, two letters. | `ae_homeMemberState` |
| `entity_name` | v1 | string | Issuer, offeror, CASP or non-compliant entity, verbatim. | `ae_lei_name` |
| `lei` | v1 | string | Legal Entity Identifier as exported (can be blank). | `ae_lei` |
| `wp_url` | v1 | string | White paper link, verbatim; `""` for entity registers. ESMA's EMT export uses the codes `EMT_NO_WP` and `EMT_CRIN` here when there is no white paper. Some values hold several URLs or text. | `wp_url` |
| `last_update` | v1 | string | The register's own last-update date, verbatim (DD/MM/YYYY). Blank for every CASP and non-compliant entity row in snapshots before October 2026, which read the white paper column only. | `wp_lastupdate`, `ac_lastupdate` (casps), `ae_lastupdate` (ncasp) |
| `format_class` | v1 | string | Link shape of `wp_url`: `xhtml/html`, `json`, `docx`, `pdf`, `unspecified` (no recognised file extension), `none` (no link); `n/a` for entity registers. A URL heuristic, not a check of the document. | `wp_url` |
| `row_hash` | v1 | 16 hex chars | SHA-256 over every column of the row (sorted `name=value` pairs, values trimmed). Any change to any column changes it. | all |
| `row_key` | v2 | 16 hex chars | Row identity within an `entry_id`: adds the DTI FFG, the DTIs and the CASP's LEI for white papers, the authorisation date for CASPs, the decision date for non-compliant entities. Rows can still share it. | |
| `fields` | v2 | object | Every column of the row, verbatim (surrounding whitespace removed). | all |
| `commercial_name` | v2 | string | Commercial or trading name. | `ae_commercial_name` |
| `website` | v2 | string | Website, verbatim (can hold several, separated by `\|`). | `ae_website` |
| `authorisation_date` | v2 | ISO date | Date of the authorisation (CASPs; EMT and ART issuers). | `ac_authorisationNotificationDate` |
| `withdrawal_date` | v2 | ISO date | Date of the withdrawal, where ESMA records one (CASPs; EMT and ART issuers). | `ac_authorisationEndDate` |
| `offer_start_date` | v2 | ISO date | Starting date, or intended starting date, of the offer to the public or the admission to trading (EMT and ART white papers). | `wp_authorisationNotificationDate` |
| `decision_date` | v2 | ISO date | The authority's decision date (non-compliant entities). | `ae_decision_date` |
| `services` | v2 | list of letters | CASP services, as the letters of the [table below](#crypto-asset-services). Read from the service text, because some letter prefixes in the export contradict it. | `ac_serviceCode` |
| `service_countries` | v2 | list of codes | Member States where the CASP intends to provide the services, sorted and unique. | `ac_serviceCode_cou` |
| `offer_countries` | v2 | list of codes | Member States of the offer to the public or admission to trading (white papers), sorted and unique. | `ae_offerCode_cou` (Title II), `wp_url_cou` (ART) |
| `dti_ffg` | v2 | string | Functionally fungible group DTI (ISO 24165), upper-case. | `ae_DTI_FFG` |
| `dti` | v2 | list of strings | Digital Token Identifiers (ISO 24165), upper-case, sorted and unique. | `ae_DTI` |
| `casp_name` | v2 | string | Title II: the CASP named on the white paper record. | `ae_lei_name_casp` |
| `casp_lei` | v2 | string | Title II: that CASP's LEI. | `ae_lei_casp` |
| `reason` | v2 | string | Non-compliant entities: the authority's stated reason, verbatim. | `ae_reason` |
| `comments` | v2 | string | ESMA's comment on the row, verbatim. | `wp_comments`, `ac_comments` (casps), `ae_comments` (ncasp) |
| `modification_noted` | v2 | boolean | White papers: the comment starts with a modification marker (`wp update`, `Updated WP`, `Modification`, `Modified`, `Art.12 Mod`). Comments that say so in other words are missed, so counts of the flag are a lower bound. Always false for entity registers. | `wp_comments` |

Columns without a typed field (for example `ae_address`, `ae_website_platform`, `ae_exemption48_4`, `ae_infrigment`) are in `fields`.

### Crypto-asset services

`services` uses the letters of the list of crypto-asset services in Art. 3(1)(16) MiCAR, which ESMA's CASP export also uses:

| Letter | Service |
| --- | --- |
| a | providing custody and administration of crypto-assets on behalf of clients |
| b | operation of a trading platform for crypto-assets |
| c | exchange of crypto-assets for funds |
| d | exchange of crypto-assets for other crypto-assets |
| e | execution of orders for crypto-assets on behalf of clients |
| f | placing of crypto-assets |
| g | reception and transmission of orders for crypto-assets on behalf of clients |
| h | providing advice on crypto-assets |
| i | providing portfolio management on crypto-assets |
| j | providing transfer services for crypto-assets on behalf of clients |

### Counting rows and entities

A register's rows are its `entries`, minus repeated header lines that the snapshots from 2026-09-14 to 2026-10-12 stored as entries (an entry whose `authority`, `entity_name` and `lei` are the column names `ae_competentAuthority`, `ae_lei_name` and `ae_lei`). An entity is a distinct upper-cased `lei`, or a distinct lower-cased `entity_name` for rows without one.

## Change record (`data/changelog.jsonl`)

| Field | Since | Meaning |
| --- | --- | --- |
| `snapshot_date` | v1 | The snapshot whose diff wrote the record. |
| `register_slug` | v1 | The register. |
| `change` | v1 | `added`, `changed`, `missing`, `removed`, `restored` or `baseline` (see below). |
| `entry_id` | v1 | The row's `entry_id`; `-` on `baseline` records. |
| `entity_name` | v1 | The row's `entity_name`; `-` on `baseline` records. |
| `member_state` | v1 | The row's `member_state`; `-` on `baseline` records. |
| `wp_url` | v1 | The row's `wp_url`. |
| `detail` | v1 | A sentence about the change; for `changed` records it names the columns that differ. |
| `record_version` | v2 | `2` for records written from October 2026; `1` (or absent) before. |
| `lei` | v2 | The row's `lei`. |
| `row_key` | v2 | The row's `row_key`. |
| `row_hash` | v2 | The row's `row_hash`: of the new row for `added`, `changed` and `restored`, of the row last seen for `missing` and `removed`. |
| `subtypes` | v2 | Mechanical labels, below. |
| `changed_fields` | v2 | `changed` only: each ESMA column whose value differs, as `{"field", "old", "new"}`. Empty when the previous snapshot predates `fields`. |

### Change kinds

| `change` | Version 2 meaning (records from October 2026) | Version 1 meaning (records up to 2026-10-12) |
| --- | --- | --- |
| `added` | A row the previous export did not list, and not a row coming back. | A row whose `entry_id` was not in the previous export, including rows coming back. |
| `changed` | A row paired with a previous row whose content differs. | Same, but only one row per `entry_id` was compared. |
| `missing` | A row of the previous export that this export does not list, for the first time. | Not used. |
| `removed` | A row absent from two consecutive exports. | A row absent from one export: a first absence. |
| `restored` | A row listed again after it was `missing` or `removed`. | Not used. |
| `baseline` | First observation of a register; `detail` gives the number of rows. | Same. |

A `removed` row can be a withdrawal, an upstream correction or a changed identity (a new white paper URL gives `removed` plus `added`); the export does not say which. ESMA's own withdrawal date is the `withdrawal_date_recorded` subtype.

### Subtypes

Written on `changed` records, re-read from the verbatim columns of the old and new row; `modification_noted` is also written on `added` records. New labels may be added.

| Subtype | When |
| --- | --- |
| `withdrawal_date_recorded` | `ac_authorisationEndDate` now holds a date and was blank. |
| `withdrawal_date_cleared` | It held a date and is now blank. |
| `withdrawal_date_changed` | It holds a different date. |
| `services_added`, `services_removed` | The CASP services (letters) gained or lost a service. |
| `service_countries_added`, `service_countries_removed` | The CASP's Member States gained or lost a country. |
| `offer_countries_added`, `offer_countries_removed` | A white paper's offer countries gained or lost a country. |
| `last_update_changed` | The register's last-update date differs. |
| `comments_changed` | ESMA's comment differs. |
| `modification_noted` | A white paper comment now starts with a modification marker (see `modification_noted` above); on an `added` record, the new row's comment does. |

## Feed (`docs/feed.json`)

| Field | Meaning |
| --- | --- |
| `snapshot_date` | The snapshot the totals describe. |
| `quarantine` | Added October 2026. `null`, or the export set aside after `snapshot_date`: `{"snapshot_date", "shrinks": [{"slug", "before", "after"}]}` with the row counts that triggered it. |
| `registers` | Per register: `slug`, `title`, `entries` (rows), `entities` (added October 2026), `fetched` and `source_last_modified` (added October 2026; as in the snapshot). |
| `recent_changes` | The last 200 change records of `data/changelog.jsonl`, oldest first. |

## CSV exports (`data/exports/`)

UTF-8, comma-separated, with a header line; columns are only ever added at the end. Every cell is a typed field of the snapshot or the change record, with these differences:

- `register` is the `register_slug`.
- Lists (`services`, `service_countries`, `offer_countries`, `dti`, `subtypes`) are joined with `|`; an empty cell is an empty list.
- `last_update` is an ISO date (the JSON keeps ESMA's DD/MM/YYYY); `""` when blank or not a date.
- `modification_noted` is `true` or `false`, and empty for rows of a snapshot written before the field existed.
- In `changes.csv`, `changed_fields` lists the names of the changed ESMA columns; their old and new values are in `data/changelog.jsonl`.

| File | Rows | Columns |
| --- | --- | --- |
| `casps.csv` | The CASP register's rows in the latest snapshot. | `snapshot_date`, `register`, `entry_id`, `row_key`, `lei`, `entity_name`, `commercial_name`, `authority`, `member_state`, `authorisation_date`, `withdrawal_date`, `services`, `service_countries`, `website`, `comments`, `last_update` |
| `ncasp.csv` | The rows of the register of non-compliant entities. | `snapshot_date`, `register`, `entry_id`, `row_key`, `lei`, `entity_name`, `commercial_name`, `authority`, `member_state`, `decision_date`, `reason`, `website`, `comments`, `last_update` |
| `whitepapers.csv` | The rows of the three white paper registers, in the order other-wp, emt-wp, art-wp. | `snapshot_date`, `register`, `entry_id`, `row_key`, `lei`, `entity_name`, `commercial_name`, `authority`, `member_state`, `wp_url`, `format_class`, `dti_ffg`, `dti`, `offer_countries`, `offer_start_date`, `authorisation_date`, `withdrawal_date`, `casp_name`, `casp_lei`, `modification_noted`, `comments`, `last_update` |
| `changes.csv` | Every line of `data/changelog.jsonl`, oldest first. | `snapshot_date`, `register`, `change`, `entry_id`, `lei`, `entity_name`, `member_state`, `wp_url`, `subtypes`, `changed_fields`, `detail`, `record_version`, `row_key`, `row_hash` |

## Raw export manifest (`data/raw/YYYY-MM-DD/manifest.json`)

| Field | Meaning |
| --- | --- |
| `snapshot_date` | The refresh the exports belong to. |
| `recorded_as` | `snapshot` when the exports became `data/snapshots/<snapshot_date>.json`, `quarantine` when they were set aside as `data/quarantine/<snapshot_date>.json`. |
| `files` | One object per export: `slug`; `file`, the gzipped export next to the manifest; `url`, where it was downloaded; `sha256` and `bytes`, of the bytes as downloaded, before compression; `last_modified`, the HTTP `Last-Modified` header verbatim (`""` when the server sent none); `retrieved_at`, when the download finished (UTC, `YYYY-MM-DDTHH:MM:SSZ`). |

`gunzip -c data/raw/<date>/casps.csv.gz | sha256sum` gives the manifest's `sha256`, and the snapshot's `source_sha256` for that register.
