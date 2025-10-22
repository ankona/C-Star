import argparse
import json
import textwrap
import typing as t
from pathlib import Path

from cstar.cli.core import PathConverterAction, RegistryResult, cli_activity
from cstar.orchestration.models import RomsMarblBlueprint, Workplan
from cstar.system.manager import cstar_sysmgr as system_mgr


def handle(ns: argparse.Namespace) -> None:
    """The action handler for the workplan-template action."""
    template = ns.command
    path = ns.path

    if path and not path.exists():
        raise ValueError(f"The specified directory does not exist: {path}")

    delimiter = "*" * 80
    tpl_name = f"{template}.yaml"
    schema_name = f"{template}-schema.yaml"
    tpl_source_path = system_mgr.environment.template_root / tpl_name

    if not tpl_source_path.exists():
        raise ValueError(f"Unable to read template file from `{tpl_source_path}`.")

    schema_path: Path | None = None
    template_path: Path | None = None

    if path is not None:
        path.mkdir(parents=True, exist_ok=True)
        template_path = path / tpl_name
        schema_path = path / schema_name

    if template == "workplan":
        schema = json.dumps(Workplan.model_json_schema(), indent=4)
    else:
        schema = json.dumps(RomsMarblBlueprint.model_json_schema(), indent=4)

    if schema_path:
        schema_ref = f"# yaml-language-server: $schema=file://{schema_path}"
    else:
        schema_ref = "# yaml-language-server: $schema=<schema-uri>"

    tpl = tpl_source_path.read_text(encoding="utf-8")
    template_lines = tpl.split("\n")
    template_lines[0] = schema_ref
    tpl = "\n".join(template_lines)

    if template_path and schema_path:
        schema_path.write_text(schema, encoding="utf-8")
        template_path.write_text(tpl, encoding="utf-8")

        message = textwrap.dedent(
            f"""\
            {template} schema written to: {schema_path}
            {template} template written to: {template_path}
            """
        )
    else:
        message = textwrap.dedent(
            f"""\
            {delimiter}
            * {template} schema
            {delimiter}
            {schema}

            {delimiter}
            * {template} template
            {delimiter}
            {tpl}
            """
        )
    print(message)


@cli_activity
def create_action() -> RegistryResult:
    """Integrate the workplan-template command into the CLI."""
    command: t.Literal["workplan"] = "workplan"
    action: t.Literal["template"] = "template"

    def _fn(sp: argparse._SubParsersAction) -> argparse.ArgumentParser:
        """Add a parser for the command: `cstar workplan template -o ouput/directory`"""
        parser: argparse.ArgumentParser = sp.add_parser(
            action,
            help="Generate an empty workplan.",
            description="Generate an empty workplan.",
        )
        parser.add_argument(
            "-o",
            "--output",
            dest="path",
            help=(
                "Output path for the workplan. If not provided, "
                "the template is written to stdout."
            ),
            required=False,
            action=PathConverterAction,
        )
        parser.set_defaults(template=action)
        parser.set_defaults(handler=handle)
        return parser

    return (command, action), _fn
