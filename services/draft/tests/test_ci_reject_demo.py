"""Regression test for the protected-branch rejection demonstration."""
from draft.cli import main


def test_version_returns_success_exit_code():
    assert main(["version"]) == 0
