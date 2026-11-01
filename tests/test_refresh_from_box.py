"""scripts/refresh_from_box.sh against a local bare "origin": it commits and
pushes a recorded refresh, does nothing twice, and refuses a dirty clone."""

import datetime
import os
import subprocess
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "scripts" / "refresh_from_box.sh"
FIXTURES = ROOT / "tests" / "fixtures"
TODAY = datetime.date.today().isoformat()
IDENTITY = {
    "GIT_AUTHOR_NAME": "Refresh test",
    "GIT_AUTHOR_EMAIL": "refresh-test@example.invalid",
    "GIT_COMMITTER_NAME": "Refresh test",
    "GIT_COMMITTER_EMAIL": "refresh-test@example.invalid",
}


def git(*args: str, cwd: Path) -> str:
    result = subprocess.run(
        ["git", *args], cwd=cwd, check=True, capture_output=True, text=True, env=environment()
    )
    return result.stdout.strip()


def environment() -> dict[str, str]:
    env = {**os.environ, **IDENTITY, "OBSERVATORY_PYTHON": sys.executable}
    env.pop("OBSERVATORY_BRANCH", None)
    return env


@pytest.fixture
def clone(tmp_path: Path) -> Path:
    """A clone, on main, of a bare origin holding this repository's files
    except data/: the first refresh establishes a baseline from the fixtures."""
    work = tmp_path / "work"
    work.mkdir()
    listed = subprocess.run(
        ["git", "ls-files", "--cached", "--others", "--exclude-standard"],
        cwd=ROOT, check=True, capture_output=True, text=True,
    ).stdout.splitlines()
    for name in listed:
        source = ROOT / name
        if name.startswith("data/") or not source.is_file():
            continue
        target = work / name
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_bytes(source.read_bytes())
    git("init", "-q", "-b", "main", cwd=work)
    git("add", "-A", cwd=work)
    git("commit", "-q", "-m", "repository without data", cwd=work)
    origin = tmp_path / "origin.git"
    git("clone", "-q", "--bare", str(work), str(origin), cwd=tmp_path)
    clone = tmp_path / "clone"
    git("clone", "-q", str(origin), str(clone), cwd=tmp_path)
    return clone


def run(clone: Path, *args: str) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        ["bash", str(clone / "scripts" / "refresh_from_box.sh"), *args],
        cwd=clone, capture_output=True, text=True, env=environment(),
    )


def origin_main(clone: Path) -> str:
    return git("ls-remote", "origin", "refs/heads/main", cwd=clone).split()[0]


def test_a_recorded_refresh_is_committed_and_pushed_once(clone: Path) -> None:
    before = origin_main(clone)
    result = run(clone, "--fixtures", str(FIXTURES), "--date", TODAY)
    assert result.returncode == 0, result.stdout + result.stderr
    assert "pushed to origin/main" in result.stdout
    assert "freshness gate passed" in result.stdout
    head = git("rev-parse", "HEAD", cwd=clone)
    assert origin_main(clone) == head != before
    assert git("log", "-1", "--format=%s", cwd=clone) == "chore: weekly register refresh"
    committed = git("show", "--stat", "--format=", "HEAD", cwd=clone)
    assert "data/latest.json" in committed and f"data/snapshots/{TODAY}.json" in committed
    assert git("status", "--porcelain", cwd=clone) == ""

    # Run again: the export was fetched this week, so nothing is recorded or pushed.
    again = run(clone, "--fixtures", str(FIXTURES), "--date", TODAY)
    assert again.returncode == 0, again.stdout + again.stderr
    assert "nothing recorded; nothing to commit" in again.stdout
    assert origin_main(clone) == head


def test_no_push_keeps_the_commit_local(clone: Path) -> None:
    before = origin_main(clone)
    result = run(clone, "--no-push", "--fixtures", str(FIXTURES), "--date", TODAY)
    assert result.returncode == 0, result.stdout + result.stderr
    assert "--no-push: the commit stays local" in result.stdout
    assert git("rev-parse", "HEAD", cwd=clone) != before
    assert origin_main(clone) == before


def test_a_clone_with_local_changes_or_on_another_branch_is_refused(clone: Path) -> None:
    before = origin_main(clone)
    (clone / "README.md").write_text("edited\n", encoding="utf-8")
    result = run(clone, "--fixtures", str(FIXTURES), "--date", TODAY)
    assert result.returncode == 1
    assert "the working tree has local changes" in result.stderr
    git("checkout", "-q", "--", "README.md", cwd=clone)

    git("checkout", "-q", "-b", "scratch", cwd=clone)
    result = run(clone, "--fixtures", str(FIXTURES), "--date", TODAY)
    assert result.returncode == 1
    assert "scratch is checked out; this script refreshes main only" in result.stderr
    assert origin_main(clone) == before
    assert not (clone / "data" / "latest.json").exists()


def test_help_describes_the_options() -> None:
    result = subprocess.run(["bash", str(SCRIPT), "--help"], capture_output=True, text=True)
    assert result.returncode == 0
    assert "--no-push" in result.stdout and "OBSERVATORY_BRANCH" in result.stdout
