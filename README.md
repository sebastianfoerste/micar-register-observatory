# MiCAR Register Observatory

Weekly snapshots and diffs of the **ESMA interim MiCAR register**. Every Monday a scheduled job downloads ESMA's five public CSV exports (white papers under Titles II–IV, authorised CASPs, non-compliant entities), records a dated snapshot, diffs it against the previous one and regenerates the published files. ESMA publishes the register under Art. 109 and 110 of Regulation (EU) 2023/1114 (MiCAR); this repository keeps its history.

## Dashboard

<!-- dashboard:start -->
**Register snapshot: 2026-10-19** (weekly, from the public ESMA interim MiCAR register). Rows/entities: Title II white papers 1049/657, EMT white papers 50/25, ART white papers 0/0, CASPs 378/375, non-compliant entities 178/175.

Changes: 32 added, 367 changed, 8 missing.

Full tables: [DASHBOARD.md](DASHBOARD.md); every change in prose: [digests/](digests/).
<!-- dashboard:end -->

## Quarterly report: The State of the MiCAR Register

Built from one committed snapshot, so its numbers are reproducible from a commit. The narrative is human-authored; `make report` generates the tables between the `data:start` / `data:end` markers and `docs/index.html`.

| Edition | Snapshot | Headline |
| --- | --- | --- |
| [2026-Q3](editions/2026-Q3.md) | 2026-09-21 | 13.8% of white papers machine-readable; 61.1% landing-page only |

## Run it

```bash
make install && make test    # uv; the suite runs offline against committed fixtures
make refresh                 # fetch ESMA, record a snapshot, regenerate the published files
make freshness               # fail when data/latest.json is incomplete or older than 14 days
uv run python -m observatory asof --lei <LEI> --date 2026-09-01
```

## Use the data

Everything is a plain file on `main`: `data/exports/*.csv`, `data/latest.json`, `data/changelog.jsonl`, `docs/feed.json`, `docs/changes.atom` and `digests/`. See [docs/using-the-data.md](docs/using-the-data.md), the [data dictionary](docs/data-dictionary.md), the [methodology](docs/methodology.md) and [CITATION.cff](CITATION.cff).

Link formats are classified by URL shape only, as candidates until a document is fetched. Findings about named issuers are not published here; they go through human legal review in [micar-whitepaper-linter](https://github.com/sebastianfoerste/micar-whitepaper-linter).

## Legal

The data is ESMA's register as exported each week; upstream corrections appear as changes. This repository records factual observations about a public register, contains no legal assessment of any issuer or service provider and is not legal advice. Code is MIT-licensed.
