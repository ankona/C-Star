# from unittest import mock

import pytest

from cstar.cli.cli import build_parser


@pytest.fixture
def all_commands() -> list[str]:
    return ["workplan"]


@pytest.fixture
def workplan_actions() -> list[str]:
    return ["run"]


def test_cli_parse_empty(
    all_commands: list[str],
    capsys: pytest.CaptureFixture[str],
) -> None:
    """Verify that an empty parameter set results in an error.

    Parameters
    ----------
    all_commands : list[str]
        The top-level commands expected to be supported.
    capsys : CaptureFixture[str]
        Captures output to stdout and stderr
    """
    parser = build_parser()

    with pytest.raises(SystemExit):
        parser.parse_args([])

    output = " ".join(capsys.readouterr())

    # confirm the parser doesn't see a valid command
    assert "arguments are required" in output

    # confirm the top level commands are enumerated
    for cmd in all_commands:
        assert cmd in output


def test_cli_workplan_no_action(
    workplan_actions: list[str],
    capsys: pytest.CaptureFixture[str],
) -> None:
    """Verify that the workplan command requires an action to be specified.

    Parameters
    ----------
    workplan_actions: list[str]
        The command-specific actions expected to be supported.
    capsys : CaptureFixture[str]
        Captures output to stdout and stderr

    """
    parser = build_parser()

    with pytest.raises(SystemExit):
        _ = parser.parse_args(["workplan"])

    output = " ".join(capsys.readouterr())

    # confirm the parser doesn't see a valid action
    assert "arguments are required" in output

    # confirm the actions are enumerated
    for cmd in workplan_actions:
        assert cmd in output


@pytest.mark.parametrize(
    "args",
    [
        ["workplan", "run"],
    ],
)
def test_cli_workplan_run_no_path(
    args: list[str],
    capsys: pytest.CaptureFixture[str],
) -> None:
    """Verify that the workplan run action requires a path.

    Parameters
    ----------
    workplan_actions: list[str]
        The command-specific actions expected to be supported.
    capsys : CaptureFixture[str]
        Captures output to stdout and stderr

    """
    parser = build_parser()

    # Sample output
    # FAILED cstar/tests/unit_tests/cli/test_cli.py::test_cli_workplan_run_no_path[args1] -
    # AssertionError: assert 'arguments are required' in ' usage: cstar workplan run [-h]

    with pytest.raises(SystemExit):
        _ = parser.parse_args(args)

    output = " ".join(capsys.readouterr())

    # confirm the parser requires a path
    assert "arguments are required" in output or "expected one argument" in output
    assert "path" in output


def test_cli_workplan_run_ok(
    capsys: pytest.CaptureFixture[str],
) -> None:
    """Verify that the workplan run action succeeds with any path provided.
    Parameters
    ----------
    workplan_actions: list[str]
        The command-specific actions expected to be supported.
    capsys : CaptureFixture[str]
        Captures output to stdout and stderr

    """
    parser = build_parser()

    exp_path = "missing.yaml"
    args = parser.parse_args(["workplan", "run", exp_path])

    # confirm that the input value is set in the args
    assert args.path == exp_path
