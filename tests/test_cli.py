import subprocess
import sys
from importlib.metadata import entry_points


def test_console_scripts_point_at_the_cli_entry_points() -> None:
    scripts = {ep.name: ep for ep in entry_points(group="console_scripts")}
    assert scripts["micar-observatory"].value == "observatory.__main__:main"
    assert scripts["micar-report"].value == "report.__main__:main"
    assert callable(scripts["micar-observatory"].load())
    assert callable(scripts["micar-report"].load())


def test_module_cli_prints_help() -> None:
    result = subprocess.run(
        [sys.executable, "-m", "observatory", "--help"],
        capture_output=True,
        text=True,
        check=True,
    )
    assert "refresh" in result.stdout and "render" in result.stdout
