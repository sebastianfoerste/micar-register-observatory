#!/usr/bin/env bash
# Refresh the register from this machine and push the result.
#
# For a machine that ESMA's CDN answers: GitHub-hosted runners have been refused
# with a CloudFront 403 since 2026-10-26 (docs/refresh-from-box.md). Safe to run
# from cron or a routine, as often as you like: it takes a lock, refuses to touch
# a clone with local changes, pulls the branch fast-forward only, runs the
# refresh (which records nothing when an export was fetched this week), then the
# freshness and contract gates, commits when the refresh recorded something, and
# pushes whatever the branch has that origin lacks (a commit whose push failed
# last time is pushed now). Git authenticates the push with whatever it already
# uses for this clone (a credential helper); nothing is read, stored or printed
# here.
#
# Usage: scripts/refresh_from_box.sh [--no-push] [refresh options...]
#   --no-push   do everything but push; the commit stays local
#   other arguments go to `python -m observatory refresh`
#   (for example --force, --no-archive or --date YYYY-MM-DD)
# Environment:
#   OBSERVATORY_BRANCH  the branch to refresh and push (default: main)
#   OBSERVATORY_PYTHON  the interpreter to use (default: `uv run python` after
#                       `uv sync --locked --extra dev`; uv is also looked for
#                       in ~/.local/bin and ~/.cargo/bin)
# Needs: a git identity (user.name, user.email) and a way for git to push.
# Exit status: 0 when nothing needed doing or the push succeeded; otherwise the
# failing command's status, with the reason on stderr. A refresh or a gate that
# fails leaves its files in the working tree for inspection, and the next run
# refuses to start until they are discarded
# (git checkout -- . && git clean -fd data digests) or committed by hand.

set -euo pipefail

script="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)/$(basename "${BASH_SOURCE[0]}")"
root="$(cd "$(dirname "$script")/.." && pwd)"
cd "$root"
branch="${OBSERVATORY_BRANCH:-main}"
push=1
refresh_args=()
while (($#)); do
  case "$1" in
    --no-push) push=0 ;;
    -h | --help)
      sed -n '2,/^$/p' "$script" | sed -e 's/^# \{0,1\}//'
      exit 0
      ;;
    *) refresh_args+=("$1") ;;
  esac
  shift
done

say() { printf '%s refresh_from_box: %s\n' "$(date -u +%Y-%m-%dT%H:%M:%SZ)" "$*"; }
fail() {
  say "$*" >&2
  exit 1
}

# Never wait for a password: a routine has nobody to type one.
export GIT_TERMINAL_PROMPT=0

# One run at a time. The lock lives in the git directory, which is never
# committed. Without flock (macOS), a lock directory holds the holder's PID; a
# holder that is gone left a stale lock, which is taken over.
lock="$(git rev-parse --git-dir)/refresh_from_box.lock"
if command -v flock >/dev/null 2>&1; then
  exec 9>"$lock"
  if ! flock -n 9; then
    say "another run holds the lock; nothing done"
    exit 0
  fi
else
  if ! mkdir "$lock.d" 2>/dev/null; then
    holder="$(cat "$lock.d/pid" 2>/dev/null || true)"
    if [[ -n "$holder" ]] && kill -0 "$holder" 2>/dev/null; then
      say "another run (pid $holder) holds the lock; nothing done"
      exit 0
    fi
    rm -rf "$lock.d" && mkdir "$lock.d"
  fi
  echo $$ >"$lock.d/pid"
  trap 'rm -rf "$lock.d"' EXIT
fi

current="$(git rev-parse --abbrev-ref HEAD)"
[[ "$current" == "$branch" ]] || fail "$current is checked out; this script refreshes $branch only"
[[ -z "$(git status --porcelain)" ]] || fail "the working tree has local changes; commit or discard them first"
git var GIT_COMMITTER_IDENT >/dev/null 2>&1 ||
  fail "git has no identity here; set user.name and user.email before the refresh can commit"

say "updating $branch from origin"
git fetch --quiet origin "$branch"
git merge --ff-only --quiet "origin/$branch" ||
  fail "$branch and origin/$branch have diverged; reconcile them by hand first"

if [[ -n "${OBSERVATORY_PYTHON:-}" ]]; then
  read -r -a python <<<"$OBSERVATORY_PYTHON"
else
  command -v uv >/dev/null 2>&1 || PATH="$HOME/.local/bin:$HOME/.cargo/bin:$PATH"
  command -v uv >/dev/null 2>&1 || fail "uv is not on PATH; install it or set OBSERVATORY_PYTHON"
  uv sync --locked --extra dev --quiet
  python=(uv run python)
fi

say "refreshing the register"
"${python[@]}" -m observatory refresh ${refresh_args[@]+"${refresh_args[@]}"}

if [[ -n "$(git status --porcelain)" ]]; then
  say "running the freshness and contract gates"
  "${python[@]}" scripts/check_snapshot_freshness.py
  "${python[@]}" -m pytest -q tests/test_contract.py

  git add data README.md docs/feed.json docs/changes.atom digests
  if git diff --cached --quiet; then
    say "no register changes"
  else
    git commit --quiet -m "chore: weekly register refresh" \
      -m "Fetched outside GitHub Actions, whose runners ESMA's CDN refuses (docs/refresh-from-box.md)."
    say "committed $(git rev-parse --short HEAD) on $branch"
  fi
else
  say "nothing recorded; nothing to commit"
fi

ahead="$(git rev-list --count "origin/$branch..HEAD")"
if ((ahead == 0)); then
  say "origin/$branch has everything; nothing to push"
elif ((push)); then
  git push --quiet origin "$branch"
  say "pushed $ahead commit(s) to origin/$branch"
else
  say "--no-push: $ahead commit(s) stay local"
fi
