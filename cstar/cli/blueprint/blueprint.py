import argparse
import typing as t

from pydantic import BaseModel

from cstar.cli.core import RegistryResult, cli_activity


class Command(BaseModel):
    command: str
    action: str


@cli_activity
def create_command_root() -> RegistryResult:
    """Create the root subparser for blueprint commands."""
    command: t.Literal["blueprint"] = "blueprint"

    def _fn(sp: argparse._SubParsersAction) -> argparse._SubParsersAction:
        """Add a subparser to house actions for the command: `cstar blueprint`"""
        parser = sp.add_parser(
            command,
            help="Create and execute custom blueprints",
            description="Create and execute custom blueprints",
        )

        subparsers = parser.add_subparsers(
            help="Blueprint actions",
            required=True,
            dest="action",
        )
        return subparsers

    return (command, None), _fn
