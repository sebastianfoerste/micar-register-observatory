"""Invariants of the weekly refresh workflow that the monitor's guarantees rest on.

The repository has no YAML parser, so jobs are split by indentation: a job is a
two-space key under `jobs:`, its permissions are the four-space `permissions:`
block. Enough for this file's layout; the test fails loudly if that changes.
"""

from __future__ import annotations

import re
from pathlib import Path

from observatory.monitor import FINGERPRINT_MARKER, Outcome

ROOT = Path(__file__).resolve().parents[1]
WORKFLOW = ROOT / ".github" / "workflows" / "refresh.yml"
TEXT = WORKFLOW.read_text(encoding="utf-8")
ISSUE_JOBS = {"source-monitor-issue", "eu-reg-mcp-fresh-install-issue"}


def _jobs() -> dict[str, str]:
    """Each job's text without comment lines, which describe rather than run."""
    body = TEXT.split("\njobs:\n", 1)[1]
    body = "".join(
        line for line in body.splitlines(keepends=True) if not line.lstrip().startswith("#")
    )
    parts = re.split(r"^  ([a-z0-9-]+):\n", body, flags=re.MULTILINE)
    return {parts[i]: parts[i + 1] for i in range(1, len(parts), 2)}


def _permissions(job: str) -> dict[str, str]:
    if re.search(r"^    permissions: \{\}$", job, re.MULTILINE):
        return {}
    match = re.search(r"^    permissions:\n((?:      [a-z-]+: [a-z]+\n)+)", job, re.MULTILINE)
    assert match, "every job declares its permissions"
    return dict(line.strip().split(": ") for line in match.group(1).splitlines())


JOBS = _jobs()


def test_layout_is_what_the_parser_expects():
    assert set(JOBS) == {"test", "refresh", "eu-reg-mcp-fresh-install"} | ISSUE_JOBS
    assert re.search(r"^permissions: \{\}$", TEXT, re.MULTILINE)
    for name, job in JOBS.items():
        assert re.search(r"^    timeout-minutes: \d+$", job, re.MULTILINE), name


def test_refresh_job_leaves_room_for_the_monitor_page_fetch():
    # In a week when ESMA refuses and archive.org rate-limits, the MiCA page fetch adds
    # about two minutes to the exports' fetches; a job timeout would lose the snapshot.
    minutes = re.search(r"^    timeout-minutes: (\d+)$", JOBS["refresh"], re.MULTILINE)
    assert minutes and int(minutes.group(1)) >= 20


def test_every_action_is_pinned_to_a_commit():
    for name, job in JOBS.items():
        for ref in re.findall(r"uses: (\S+)", job):
            assert re.fullmatch(r"[\w.-]+/[\w.-]+@[0-9a-f]{40}", ref), (name, ref)


def test_only_the_jobs_that_file_issues_may_write_issues():
    for name, job in JOBS.items():
        permissions = _permissions(job)
        if "gh issue" in job:
            assert name in ISSUE_JOBS
            assert permissions == {"issues": "write"}, name
            # No action, checkout or Python tooling runs with that token.
            assert "uses:" not in job, name
            assert not re.search(r"^\s+(?:- run: )?(?:uvx?|uv|pip|python)\b", job, re.MULTILINE), (
                name
            )
        else:
            assert "issues" not in permissions, name
    assert _permissions(JOBS["refresh"]) == {"contents": "write"}
    assert _permissions(JOBS["test"]) == {"contents": "read"}


def test_the_monitor_runs_inside_the_refresh_and_cannot_stop_it():
    job = JOBS["refresh"]
    # No separate monitor step that could fail before the refresh: the refresh
    # itself checks the bytes it used and hands the report on.
    assert "observatory monitor" not in job
    step = re.search(r"- name: Refresh.*?\n        id: refresh\n        run: (.+)\n", job)
    assert step and "-m observatory refresh --monitor-report" in step.group(1)
    assert job.index("observatory refresh") < job.index("git push")
    for output in ("monitor", "fingerprint", "report"):
        assert f"{output}: ${{{{ steps.refresh.outputs.{output} }}}}" in job
    # Only the failure annotation runs on failure; nothing in the job is skipped
    # or forgiven by the monitor's outcome.
    assert job.count("if:") == 1 and "if: failure()" in job
    assert "continue-on-error" not in job


def test_the_monitor_issue_follows_issue_and_unknown_outcomes_only():
    job = JOBS["source-monitor-issue"]
    condition = re.search(r"^    if: (.+)$", job, re.MULTILINE)
    assert condition
    # always(): a refresh that failed after the monitor reported still files it.
    assert condition.group(1).startswith("always() && ")
    named = set(re.findall(r"needs\.refresh\.outputs\.monitor == '([a-z]+)'", condition.group(1)))
    assert named == {Outcome.ISSUE.value, Outcome.UNKNOWN.value}
    assert Outcome.OK.value not in named and "skipped" not in named


def test_the_install_check_runs_without_any_token_scope_and_blocks_nothing():
    job = JOBS["eu-reg-mcp-fresh-install"]
    assert _permissions(job) == {}
    assert "actions/checkout" not in job
    assert "enable-cache: false" in job
    assert "--isolated" in job and "--no-cache" in job and "--overrides" in job
    # The override file names mcp without a bound: the newest release installs.
    assert "printf 'mcp\\n'" in job
    # A failed install is recorded as a result, never as a failed step.
    assert re.search(r"^\s+result=fail$", job, re.MULTILINE)
    for name, other in JOBS.items():
        if name != "eu-reg-mcp-fresh-install-issue":
            assert "needs: eu-reg-mcp-fresh-install" not in other, name
    # The evening fallback slot does not repeat the morning's check.
    assert "github.event.schedule == '17 6 * * 1'" in job
    assert '- cron: "17 6 * * 1"' in TEXT


def test_issue_jobs_never_open_a_duplicate():
    markers = {
        "source-monitor-issue": FINGERPRINT_MARKER,
        "eu-reg-mcp-fresh-install-issue": "fresh-install-key",
    }
    for name in ISSUE_JOBS:
        job = JOBS[name]
        # Explicit bash runs with pipefail, so a failed gh call stops the step.
        assert "defaults:\n      run:\n        shell: bash" in job, name
        lookup = re.search(r'number="\$\(gh issue list.*?\)"\n', job, re.DOTALL)
        assert lookup, name
        assert "|" not in lookup.group(0).split("--jq", 1)[0], name
        assert "--state open" in lookup.group(0), name
        # The key is checked before it is trusted, and the last key posted by
        # this workflow decides whether anything new is said.
        assert re.search(r'\[\[ "\$(?:FINGERPRINT|KEY)" =~ \^\[0-9a-f\]\{16\}\$ \]\]', job), name
        assert f"{markers[name]}: [0-9a-f]{{16}}" in job, name
        assert job.count('select(.user.login == "github-actions[bot]")') == 2, name
        assert 'if [ "$last" = ' in job, name
        assert job.index("gh issue create") < job.index("gh issue comment"), name


def test_each_posted_body_carries_the_marker_its_issue_job_reads():
    # The monitor's report ends with the marker (test_monitor checks the
    # rendering); the install job's body adds its own.
    assert FINGERPRINT_MARKER == "monitor-fingerprint"
    assert '"$REPORT"' in JOBS["source-monitor-issue"]
    assert "<!-- fresh-install-key: $KEY -->" in JOBS["eu-reg-mcp-fresh-install-issue"]


def test_untrusted_text_reaches_scripts_only_through_the_environment():
    # Report text and install logs come from ESMA's files and from PyPI
    # packages: they are passed as env values, never pasted into a script.
    for name, job in JOBS.items():
        for line in job.splitlines():
            if "outputs.report" in line or "outputs.log" in line:
                assert re.match(r"\s+(?:REPORT|LOG|report|log): \$\{\{", line), (name, line)


def test_runs_do_not_overlap():
    assert re.search(
        r"^concurrency:\n  group: data-writes\n  cancel-in-progress: false$", TEXT, re.MULTILINE
    )
