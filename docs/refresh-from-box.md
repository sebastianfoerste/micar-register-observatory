# Refreshing from a machine of your own

Since 2026-10-26 the scheduled `refresh` workflow has not been able to download
the ESMA exports: every GitHub-hosted runner gets a CloudFront "Request blocked"
403 at the CDN edge in front of esma.europa.eu, before the request reaches
ESMA's server (the 2026-10-26 run, and the same 403 page that archive.org's
crawler received on 2026-10-22). The same URLs answer 200 from other networks.
The block is not about the request: the observatory identifies itself
(`User-Agent: micar-register-observatory/0.1 (+repository URL)`), ESMA's
robots.txt does not exclude the files, and ESMA's legal notice authorises
reproduction with the source acknowledged. Nothing here works around the block;
the refresh runs where ESMA answers, or uses a public archive of the file.

Two things keep the register's memory going:

1. **The archive fallback** (built into `python -m observatory refresh`). When
   ESMA refuses or fails for every attempt, the refresh takes the newest copy of
   the export from the Internet Archive's Wayback Machine, provided it was
   captured within the last 3 days (`MAX_ARCHIVE_AGE_DAYS`), and records where
   the bytes came from: `fetched_from` and `archived_at` in the snapshot and the
   feed, `url` and `archived_at` in the raw manifest, and "archived copy from the
   Wayback Machine, captured YYYY-MM-DD" in the dashboard. A 404 from ESMA is not
   papered over: it means the file moved. `--no-archive` fails instead. The
   Wayback Machine has captured the five files about daily since 2026-10-29;
   those captures are made by others, so they may stop.
2. **A refresh from a machine that ESMA answers**, with
   `scripts/refresh_from_box.sh`, which is what the rest of this page is about.

## What the script does

In a clone of this repository on `main`, `scripts/refresh_from_box.sh`:

- takes a lock, so two runs cannot overlap (`flock` where it exists, a lock
  directory with the holder's PID elsewhere);
- refuses to run when the clone has local changes, another branch checked out,
  or no git identity (`user.name`, `user.email`) to commit with;
- fetches `origin/main` and fast-forwards to it (never merges, never rebases);
- installs the locked dependencies (`uv sync --locked --extra dev`) and runs
  `python -m observatory refresh`, which fetches nothing when an export was
  already recorded or quarantined in the last five days;
- when the refresh recorded something, runs the same gates as the workflow
  (`scripts/check_snapshot_freshness.py`, `pytest tests/test_contract.py`) and
  commits the same files the workflow commits (`data`, `README.md`,
  `docs/feed.json`, `docs/changes.atom`, `digests`) as
  `chore: weekly register refresh`;
- pushes, with a plain `git push`, whatever the branch has that origin lacks,
  so a commit whose push failed last week goes out this week.

It never reads, stores or prints credentials: git uses whatever credential
helper the clone already has (`gh auth setup-git`, your OS keychain).
`GIT_TERMINAL_PROMPT=0` makes sure a routine never waits for a password. Extra
arguments go to the refresh (`--force`, `--no-archive`, `--date`); `--no-push`
keeps the commit local, for a dry run.

If the refresh or a gate fails, nothing is committed and the files it wrote
stay in the working tree so that you can look at them; the next run refuses to
start until they are discarded (`git checkout -- . && git clean -fd data
digests`) or committed by hand. The exit status is then the failing command's.

## Setting it up

```bash
git clone https://github.com/sebastianfoerste/micar-register-observatory ~/micar-register-observatory
cd ~/micar-register-observatory
gh auth setup-git            # or any other credential helper that can push
scripts/refresh_from_box.sh --no-push   # dry run: fetches, records, commits locally
git log -1 --stat && git reset --hard origin/main   # look, then drop the dry run
```

Schedule it for **Monday 06:00 UTC**, before the workflow's first slot (06:17
UTC, which GitHub delivers hours late anyway). ESMA has replaced the files on
Fridays around 11:30 UTC. Whichever of the two records the week's export first
wins; the other then fetches nothing. With cron:

```
PATH=/usr/local/bin:/usr/bin:/bin
0 6 * * 1  cd $HOME/micar-register-observatory && scripts/refresh_from_box.sh >> $HOME/micar-refresh.log 2>&1
```

(cron's default PATH is short; the script also looks for `uv` in `~/.local/bin`
and `~/.cargo/bin`, where uv's installer puts it.)

With a systemd user timer (`~/.config/systemd/user/micar-refresh.service` and
`.timer`, then `systemctl --user enable --now micar-refresh.timer` and
`loginctl enable-linger $USER` so that it runs while you are logged out):

```ini
[Unit]
Description=MiCAR register refresh from this machine
[Service]
Type=oneshot
WorkingDirectory=%h/micar-register-observatory
Environment=PATH=%h/.local/bin:/usr/local/bin:/usr/bin:/bin
ExecStart=%h/micar-register-observatory/scripts/refresh_from_box.sh
```

```ini
[Unit]
Description=Weekly MiCAR register refresh
[Timer]
OnCalendar=Mon *-*-* 06:00:00 UTC
Persistent=true
[Install]
WantedBy=timers.target
```

Any other routine runner works the same way: working directory the clone,
command `scripts/refresh_from_box.sh`, once a week. Running it more often is
harmless: the refresh records nothing within five days of the last export.

## Checking that it worked

`git log --format='%h %ad %s' --date=short -3 origin/main` shows the refresh
commits; the dashboard's "Register snapshot" date and the source status column
in the README say which export each register came from. The workflow keeps
running on its schedule and succeeds whenever ESMA answers a runner again, in
which case this routine simply finds nothing left to do.
