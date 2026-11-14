# Runbook: ESMA moves or changes a register file

**Rule.** When ESMA moves or changes a file the observatory reads, the owner of this repository updates the source within one week of the monitor's issue, source-first: every URL, column name and date in the fix comes from a page or file retrieved from ESMA and snapshotted in [`sources/`](../sources/README.md), never from a search result, a mirror or memory.

## What the monitor checks

The source monitor ([`src/observatory/monitor.py`](../src/observatory/monitor.py)) runs inside every weekly refresh that fetches. It does not download anything of its own. It checks the bytes the refresh actually used and records where they came from:

- **ESMA**, when ESMA's CDN answered the runner;
- **the Wayback Machine's copy**, with its capture time and what ESMA answered, when ESMA refused the runner and the archive had a copy at most three days old (`MAX_ARCHIVE_AGE_DAYS`; see [refresh-from-box.md](refresh-from-box.md)). ESMA's CDN has refused GitHub-hosted runners at times since 26 October 2026.

ESMA's MiCA page is read the same way, ESMA first and then a recent archived copy. On those bytes the monitor runs the hard checks: content type `text/csv` (or `text/html` for the page), UTF-8, the CSV header against `columns` in [`config.py`](../src/observatory/config.py), the row count against the source's floor, and on the page a "Last update" line and a link to every configured export. It then compares each source with its previous observation in `data/source-monitor.json` and classifies every difference. The rules were set on 10 November 2026:

| Difference | Decision |
| --- | --- |
| The final URL moved; a configured export is no longer linked on ESMA's MiCA page; the header changed; a charset other than UTF-8 | issue |
| The rows dropped by more than max(5, 10 % of the previous count), or fell to 0 | issue |
| `last_modified`, `last_update_line`, `content_length`, any growth, a smaller drop | log |
| ESMA refused the download and the archive's copy was used | log |

A refusal by ESMA is a logged state, never a finding: the refresh goes on with the archive's copy. The monitor never changes the refresh's exit status or what the refresh records. A refresh that cannot get an export from ESMA or the archive still fails closed and records nothing.

## What triggers this runbook

The weekly `refresh` workflow opens the issue **"ESMA source monitor: findings to review"** when the monitor's outcome is:

- **ISSUE**: a hard check failed or a difference was classified as an issue. The refresh itself ran; whether it recorded the export was decided by its own checks (required columns, row floors, the quarantine for sharp drops).
- **UNKNOWN**: nothing calls for an issue, but at least one source could not be read from ESMA or from a recent archived copy, so its checks did not run. An unobserved source is never counted as a pass. If it was an export, the refresh failed that week; record it from a machine ESMA answers with `scripts/refresh_from_box.sh` ([refresh-from-box.md](refresh-from-box.md)). UNKNOWN is also the outcome when the monitor itself failed, for example on a `data/source-monitor.json` left with a merge conflict: the report says so and names the error, the refresh still records the export, and the file is left as it was. Restore the file from the last good commit, or delete it and record a new one as in step 7.

The issue stays open until the owner closes it. Later runs comment on it only when the findings, or the set of unobserved sources, differ from the last report the workflow posted; an unchanged finding is not repeated week after week. Each report ends with a `monitor-fingerprint` comment that the workflow compares.

An announcement by ESMA triggers the same steps without waiting for the monitor. ESMA's MiCA page (snapshots of 14 October and 14 November 2026) says the interim register will be available as CSV files "until mid-2026" before it is "formally integrated into ESMA’s IT systems".

## Steps

1. **Read the report** in the issue. "Sources used" says whether each file came from ESMA or the Wayback Machine, with the capture time and ESMA's answer; "Checks" and "Differences" name what failed or changed. A finding on archived bytes reflects the file as captured, which may be up to three days older than ESMA's current file.
2. **Find the current source on ESMA's site.** Start from ESMA's [MiCA page](https://www.esma.europa.eu/esmas-activities/digital-finance-and-innovation/markets-crypto-assets-regulation-mica) and its Databases and Registers page. Fetch the new file and ESMA's field description file from a machine ESMA answers.
3. **Snapshot before changing code.** Add the page and the field description to `sources/esma/<retrieval date>/`, and record URL, retrieval time, SHA-256 and the new header row in [`sources/README.md`](../sources/README.md). Keep the old snapshots.
4. **Update the configuration from the snapshot.** In [`src/observatory/config.py`](../src/observatory/config.py), change `BASE_URL`, `filename`, `columns` or `min_rows` as the snapshot shows. If a column was added, removed or renamed, check `REQUIRED_COLUMNS` and `WHITEPAPER_COLUMNS` in the same file, and the names `normalize.py` reads, against the field description. Every column feeds the row hash, so a header change marks every entry of that file as `changed` in the next refresh; record that in [`methodology.md`](methodology.md) before merging.
5. **Update the tests and documents.** `tests/test_config.py` compares the configured columns with `sources/README.md` and the field description; update the fixture headers in `tests/fixtures/`. Update the source table in [`methodology.md`](methodology.md) and any README links.
6. **Verify.** Run `make check`, then, from a machine ESMA answers, `uv run python -m observatory monitor --no-archive --state "$(mktemp -d)/source-monitor.json"`. With no earlier observation to compare against, the command exits 0 exactly when every source is observed and every check passes on ESMA's own bytes. `make monitor` compares with `data/source-monitor.json` instead and reports the change itself as a difference; neither command writes anything without `--save`.
7. **Reset the baseline when the refresh failed that week.** A refresh that failed saves no observation, so `data/source-monitor.json` still shows the old source and the next refresh would report the same change once more. In that case run `uv run python -m observatory monitor --no-archive --save` from a machine ESMA answers after the fix, and commit `data/source-monitor.json` in the fix's pull request. If the refresh of that week succeeded, the file already holds the new observation; leave it alone.
8. **Ship.** Open a pull request with the snapshot, the configuration change and the test results. After the merge, run the refresh workflow by hand (Actions, "refresh", "Run workflow") and close the issue with a link to the pull request.
9. **Check what depends on the data.** eu-reg-mcp reads `data/latest.json` and `data/changelog.jsonl` from this repository's `main` branch. After a schema change, run its parser tests against the new snapshot.

If the fix cannot land within the week, add a dated line at the top of the README saying the register data is stale since the last good snapshot, and keep the issue open.

## The eu-reg-mcp fresh-install issue

The same workflow, in its Monday-morning run, installs the newest eu-reg-mcp release from PyPI in a fresh, isolated environment, as `uvx eu-reg-mcp` would, with an override that lifts eu-reg-mcp's own bound on `mcp`, so the newest `mcp` is installed. It then imports `eu_reg_mcp.server`. The job holds no token scope, blocks nothing and writes its result and the installed versions to the job summary. When the import fails, a separate job opens **"eu-reg-mcp fresh install with the newest mcp fails"**, or comments on it when the result or the installed versions changed since its last comment.

On 14 November 2026 the check failed locally: eu-reg-mcp 0.1.2 with mcp 2.3.0 cannot import `mcp.server.fastmcp`, which mcp 2.x renamed. The failure is expected until a release of eu-reg-mcp ported to mcp 2.x is on PyPI; close the issue when the check passes.
