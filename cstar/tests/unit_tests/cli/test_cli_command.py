# from pathlib import Path
#
# import pytest
# from pydantic import ValidationError
#
# from cstar.cli.cli import (
#     # CheckWorkplanCommand,
#     # RunWorkplanCommand,
#     # as_command,
#     # build_parser,
# )
#
#
# def test_cli_command_wp_run_bad_path() -> None:
#     """Verify that the workplan run command only accepts valid paths."""
#     parser = build_parser()
#     exp_path = "missing.yaml"
#     args = parser.parse_args(["workplan", "run", exp_path])
#
#     with pytest.raises(ValidationError) as ex:
#         _ = as_command(args)
#
#     # confirm that the path is not accepted
#     assert "path" in str(ex.value)
#
#
# def test_cli_command_wp_check_bad_path() -> None:
#     """Verify that the workplan check command only accepts valid paths."""
#     parser = build_parser()
#     exp_path = "missing.yaml"
#     args = parser.parse_args(["workplan", "check", exp_path])
#
#     with pytest.raises(ValidationError) as ex:
#         _ = as_command(args)
#
#     # confirm that the path is not accepted
#     assert "path" in str(ex.value)
#
#
# def test_cli_command_wp_run(
#     tmp_path: Path,
# ) -> None:
#     """Verify that the run workplan action is parsed into a command.
#
#     Parameters
#     ----------
#     tmp_path : Path
#         A temporary path to store test outputs
#     """
#     parser = build_parser()
#     exp_path = tmp_path / "empty-wp.yaml"
#     exp_path.touch()
#
#     args = parser.parse_args(["workplan", "run", str(exp_path)])
#
#     cmd = as_command(args)
#
#     # confirm that the command is parsed
#     assert isinstance(cmd, RunWorkplanCommand)
#
#
# def test_cli_command_wp_check(
#     tmp_path: Path,
# ) -> None:
#     """Verify that the check workplan action is parsed into a command.
#
#     Parameters
#     ----------
#     tmp_path : Path
#         A temporary path to store test outputs
#
#     """
#     parser = build_parser()
#
#     exp_path = tmp_path / "empty-wp.yaml"
#     exp_path.touch()
#
#     args = parser.parse_args(["workplan", "check", str(exp_path)])
#
#     cmd = as_command(args)
#
#     # confirm that the command is parsed
#     assert isinstance(cmd, CheckWorkplanCommand)
