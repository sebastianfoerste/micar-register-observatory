"""The suite runs offline: a refresh under test never fetches ESMA's MiCA page.

Tests that drive the refresh without fixtures replace fetch_export themselves;
the page fetch for the source monitor is replaced here, for every test, by an
answer that says it was not fetched. Tests of the page path replace it again.
"""

import pytest

import observatory.__main__ as cli


@pytest.fixture(autouse=True)
def _no_page_fetch(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(cli, "fetch_page", lambda archive=True: OSError("offline test run"))
