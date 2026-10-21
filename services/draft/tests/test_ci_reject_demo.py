"""Deliberately wrong oracle for a protected-branch rejection demonstration."""
from draft.cli import main


def test_intentionally_wrong_version_exit_code():
    assert main(["version"]) == 1, "Intentional teaching fault: version actually returns zero"
