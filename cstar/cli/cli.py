import argparse
import asyncio
import sys
from argparse import ArgumentParser, Namespace

from cstar.cli.command import (
    CheckBlueprintCommand,
    CheckWorkplanCommand,
    Command,
    RunBlueprintCommand,
    RunWorkplanCommand,
)
from cstar.cli.handler import handle_command


def as_command(args: Namespace) -> Command:
    """Convert the raw arguments into a command.

    Parameters
    ----------
    args : Namespace
        Arguments parsed from the command line

    Returns
    -------
    Command
        A command populated from the raw arguments.
    """
    parameters = vars(args)
    factory = parameters.pop("factory")

    command = factory(**parameters)

    # print(f"Parsed model: {command.model_dump_json()}")
    return command


def build_blueprint_subparser(subparsers: argparse._SubParsersAction) -> None:
    """Add a parser for the `blueprint` command and any nested actions.

    Parameters
    ----------
    subparsers : ArgumentParser
        The subparser to add commands to
    """
    blueprint_parser = subparsers.add_parser(
        "blueprint",
        help="Create and execute custom blueprints",
    )

    bp_subparsers = blueprint_parser.add_subparsers(
        help="Workplan actions",
        required=True,
        dest="action",
    )

    bp_run_parser = bp_subparsers.add_parser("run")
    bp_run_parser.add_argument(
        "-p",
        "--path",
        help="Path to a blueprint",
        required=True,
    )
    bp_run_parser.set_defaults(factory=RunBlueprintCommand)

    bp_check_parser = bp_subparsers.add_parser("check")
    bp_check_parser.add_argument(
        "-p",
        "--path",
        help="Path to a blueprint",
        required=True,
    )
    bp_check_parser.set_defaults(factory=CheckBlueprintCommand)


def build_workplan_subparser(subparsers: argparse._SubParsersAction) -> None:
    """Add a parser for the `workplace` command and any nested actions.

    Parameters
    ----------
    subparsers : ArgumentParser
        The subparser to add commands to
    """
    workplan_parser = subparsers.add_parser(
        "workplan",
        help="Create and execute custom workplans",
    )

    wp_subparsers = workplan_parser.add_subparsers(
        help="Workplan actions",
        required=True,
        dest="action",
    )

    wp_run_parser = wp_subparsers.add_parser("run")
    wp_run_parser.add_argument(
        "-p",
        "--path",
        help="Path to a workplan",
        required=True,
    )
    wp_run_parser.set_defaults(factory=RunWorkplanCommand)

    wp_check_parser = wp_subparsers.add_parser("check")
    wp_check_parser.add_argument(
        "-p",
        "--path",
        help="Path to a workplan",
        required=True,
    )
    wp_check_parser.set_defaults(factory=CheckWorkplanCommand)


def build_parser() -> ArgumentParser:
    """Configure the CLI argument parser.

    Returns
    -------
    ArgumentParser
        The parser
    """
    parser = ArgumentParser("cstar")

    subparsers = parser.add_subparsers(
        title="command",
        help="Available commands",
        required=True,
        dest="command",
    )
    _ = subparsers.add_parser("usage", help="Learn how to use this tool")

    build_workplan_subparser(subparsers)
    build_blueprint_subparser(subparsers)

    return parser


def main() -> None:
    """Parse arguments passed to the CLI and trigger the associated request handlers."""
    args = sys.argv[1:]

    parser = build_parser()
    ns = parser.parse_args(args)

    command = as_command(ns)
    asyncio.run(handle_command(command))


if __name__ == "__main__":
    main()
