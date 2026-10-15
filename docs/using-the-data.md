# Using the data

Everything the observatory records is a plain file on `main`, refreshed every Monday. You do not need to run any Python to use it: download a CSV, point pandas or DuckDB at a URL, or subscribe to the Atom feed. Field meanings are in the [data dictionary](data-dictionary.md); how rows are matched and changes detected is in the [methodology](methodology.md).

## The files

All paths are relative to `https://raw.githubusercontent.com/sebastianfoerste/micar-register-observatory/main/`.

| File | What it holds |
| --- | --- |
| `data/exports/casps.csv` | The CASP register in the latest snapshot: one line per register row, with authorisation and withdrawal dates, services (letters a–j) and the Member States the services are provided in. |
| `data/exports/ncasp.csv` | The register of non-compliant entities in the latest snapshot, with the authority's decision date and stated reason. |
| `data/exports/whitepapers.csv` | The three white paper registers (Title II, e-money tokens, asset-referenced tokens) in the latest snapshot, with DTIs, offer countries and the white paper link. |
| `data/exports/changes.csv` | Every change record since 7 July 2026, one per line: added, changed, missing, removed, restored. |
| `data/changelog.jsonl` | The same records as JSON lines, with the old and new value of every changed column. |
| `data/latest.json` | The latest snapshot of all five registers, with every ESMA column of every row (`fields`). |
| `data/snapshots/YYYY-MM-DD.json` | Every weekly snapshot since 7 July 2026, in the same format. |
| `data/raw/YYYY-MM-DD/` | From October 2026: ESMA's exports exactly as downloaded, gzipped, with a manifest of their SHA-256 and HTTP `Last-Modified` header. |
| `docs/feed.json` | Current totals per register and the last 200 change records. |
| `docs/changes.atom` | An Atom feed with one entry per weekly snapshot. |
| `digests/YYYY-MM-DD.md` | A readable note of each week's changes. |

The CSV files are UTF-8 with a header line. Lists are joined with `|` (as in ESMA's own exports) and dates are ISO (`YYYY-MM-DD`); an empty cell means the register gives no value. The exports carry the typed fields only; ESMA's verbatim columns are in the snapshot JSON. Snapshots up to 2026-10-12 kept only the core columns, so dates, services and countries are filled from the first refresh after that.

## In 30 seconds

```bash
BASE=https://raw.githubusercontent.com/sebastianfoerste/micar-register-observatory/main
curl -sSO "$BASE/data/exports/casps.csv"
curl -sS "$BASE/docs/feed.json" | python3 -m json.tool | head -40
```

## pandas

Read every column as text so that LEIs, codes and empty cells stay as they are:

```python
import pandas as pd

BASE = "https://raw.githubusercontent.com/sebastianfoerste/micar-register-observatory/main"
casps = pd.read_csv(f"{BASE}/data/exports/casps.csv", dtype=str, keep_default_na=False)

# Firms, not rows: one firm can have several rows.
firms = casps.lei.where(casps.lei != "", "name:" + casps.entity_name.str.lower())
print(len(casps), "rows,", firms.nunique(), "firms")

# Rows that list custody (service a) and Italy among the service countries.
services = casps.services.str.split("|")
countries = casps.service_countries.str.split("|")
casps[services.apply(lambda s: "a" in s) & countries.apply(lambda c: "IT" in c)]

# Rows with a withdrawal date recorded by ESMA.
casps[casps.withdrawal_date != ""][["entity_name", "withdrawal_date"]]

# What changed in the latest snapshot.
changes = pd.read_csv(f"{BASE}/data/exports/changes.csv", dtype=str, keep_default_na=False)
latest = changes[changes.snapshot_date == changes.snapshot_date.max()]
latest.groupby(["register", "change"]).size()

# Old and new values of each changed column, from the changelog.
log = pd.read_json(f"{BASE}/data/changelog.jsonl", lines=True, dtype=False)
fields = log[log.change == "changed"].explode("changed_fields").dropna(subset=["changed_fields"])
fields = fields.join(pd.json_normalize(fields.changed_fields.tolist()).set_index(fields.index))
fields[["snapshot_date", "entity_name", "field", "old", "new"]]
```

## DuckDB

DuckDB reads the files straight from their URLs:

```sql
-- Rows and firms per home Member State.
SELECT member_state,
       count(*) AS rows,
       count(DISTINCT coalesce(nullif(lei, ''), 'name:' || lower(entity_name))) AS firms
FROM read_csv('https://raw.githubusercontent.com/sebastianfoerste/micar-register-observatory/main/data/exports/casps.csv', all_varchar = true)
GROUP BY member_state
ORDER BY firms DESC;

-- Rows that list custody (service a) and Italy among the service countries.
SELECT entity_name, member_state, services, service_countries
FROM read_csv('https://raw.githubusercontent.com/sebastianfoerste/micar-register-observatory/main/data/exports/casps.csv', all_varchar = true)
WHERE list_contains(string_split(services, '|'), 'a')
  AND list_contains(string_split(service_countries, '|'), 'IT');

-- Old and new values of every changed column.
SELECT snapshot_date, entity_name, unnest(changed_fields, recursive := true)
FROM read_json('https://raw.githubusercontent.com/sebastianfoerste/micar-register-observatory/main/data/changelog.jsonl', format = 'newline_delimited')
WHERE change = 'changed' AND record_version = 2;
```

## Questions about one firm on one date

With a clone of the repository, `asof` answers what the register listed for a firm on a date, from the recorded snapshots and the changelog:

```bash
git clone https://github.com/sebastianfoerste/micar-register-observatory
cd micar-register-observatory
uv sync
uv run python -m observatory asof --lei <LEI> --date 2026-09-01
uv run python -m observatory asof --name "<part of the name>" --register casps --json
```

The answer is the last snapshot recorded on or before the date, the registers that did not list the firm, and its change records up to then. It is the weekly export as the observatory fetched it, not ESMA's register on that exact day.

## Following the changes

- Subscribe to `https://raw.githubusercontent.com/sebastianfoerste/micar-register-observatory/main/docs/changes.atom` in a feed reader: one entry per weekly snapshot, linking to its digest.
- `digests/YYYY-MM-DD.md` lists every change of a week, with old and new values of changed columns.
- `docs/feed.json` says when an export was set aside after a sharp drop in rows (`quarantine`); the totals then stay at the last recorded snapshot.
- AI agents can query the same data through [eu-reg-mcp](https://github.com/sebastianfoerste/eu-reg-mcp).

## Before you rely on it

- The data is ESMA's interim MiCAR register as exported on the day of each weekly refresh. It is not a copy of ESMA's register at any other moment, and the observatory does not correct it: an error in ESMA's file is an error here.
- A `missing` row is not in one export; a `removed` row is not in two consecutive exports. Neither says why a row left: it can be a withdrawal, an upstream correction or a changed white paper link. ESMA's own withdrawal date is in `withdrawal_date`.
- The typed fields are mechanical readings of ESMA's columns (see the [data dictionary](data-dictionary.md)); the verbatim values are in the snapshot JSON.
- Values are verbatim. If you open a CSV in a spreadsheet, import every column as text so that codes, LEIs and dates keep their form.
- The observatory makes no assessment of any named issuer, offeror or crypto-asset service provider.

To cite the dataset, see [CITATION.cff](../CITATION.cff).
