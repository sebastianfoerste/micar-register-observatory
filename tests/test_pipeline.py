import argparse
import shutil
from pathlib import Path

from observatory.__main__ import cmd_refresh
from observatory.render import DASHBOARD_END, DASHBOARD_START
from observatory.store import read_changelog

FIXTURES = Path(__file__).parent / "fixtures"


def args_for(tmp_path: Path, date: str, fixtures: Path) -> argparse.Namespace:
    return argparse.Namespace(
        data_dir=str(tmp_path / "data"),
        readme=str(tmp_path / "README.md"),
        feed=str(tmp_path / "docs" / "feed.json"),
        date=date,
        fixtures=str(fixtures),
    )


def seed_readme(tmp_path: Path) -> None:
    (tmp_path / "README.md").write_text(
        f"# head\n\n{DASHBOARD_START}\n{DASHBOARD_END}\n\ntail\n", encoding="utf-8"
    )


def test_refresh_twice_renders_dashboard_and_changelog(tmp_path: Path) -> None:
    seed_readme(tmp_path)
    (tmp_path / "data").mkdir()

    assert cmd_refresh(args_for(tmp_path, "2026-07-07", FIXTURES)) == 0
    readme = (tmp_path / "README.md").read_text(encoding="utf-8")
    assert "Register snapshot: 2026-07-07" in readme
    assert "baseline established" in readme
    assert readme.startswith("# head")
    assert readme.rstrip().endswith("tail")

    # Second run against edited fixtures: one new row in other-wp.
    edited = tmp_path / "fixtures2"
    shutil.copytree(FIXTURES, edited)
    with (edited / "other-wp.csv").open("a", encoding="utf-8") as handle:
        handle.write(
            "Malta Financial Services Authority (MFSA),MT,New Issuer Ltd,"
            "529900NEWISSUER00001,MT,,,MT,,,https://new.example/wp.pdf,,01/07/2026\n"
        )

    assert cmd_refresh(args_for(tmp_path, "2026-07-14", edited)) == 0
    readme = (tmp_path / "README.md").read_text(encoding="utf-8")
    assert "Register snapshot: 2026-07-14" in readme
    assert "New Issuer Ltd" in readme

    changes = read_changelog(tmp_path / "data")
    assert any(c.change == "added" and c.entity_name == "New Issuer Ltd" for c in changes)
    assert (tmp_path / "docs" / "feed.json").exists()
    assert (tmp_path / "data" / "snapshots" / "2026-07-14.json").exists()
