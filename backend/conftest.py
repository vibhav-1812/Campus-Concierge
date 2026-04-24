"""Pytest configuration: echo a line to the terminal when each test passes."""

from __future__ import annotations

import pytest


@pytest.hookimpl(hookwrapper=True)
def pytest_runtest_makereport(item: pytest.Item, call):
    outcome = yield
    rep = outcome.get_result()
    if rep.when == "call" and rep.passed:
        term = item.config.pluginmanager.get_plugin("terminalreporter")
        if term is not None:
            term.write_line(f"  [OK] {item.nodeid} - test successfully passed")
