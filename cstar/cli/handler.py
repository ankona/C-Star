import json
from functools import singledispatch
from pathlib import Path

from cstar.cli.command import (
    CheckBlueprintCommand,
    CheckWorkplanCommand,
    Command,
    GenerateTemplateCommand,
    PlanWorkplanCommand,
    RunBlueprintCommand,
    RunWorkplanCommand,
)
from cstar.orchestration.models import RomsMarblBlueprint, TaskStatus, Workplan
from cstar.orchestration.tasks.blueprint import (
    run_validate_blueprint_flow,
    validate_blueprint,
)
from cstar.orchestration.tasks.plan import (
    run_plan_workplan_flow,
    run_validate_workplan_flow,
    validate_workplan,
)
from cstar.orchestration.tasks.request import (
    PlanWorkplanRequest,
    ValidateBlueprintRequest,
    ValidateWorkplanRequest,
)
from cstar.system.manager import CStarSystemManager


@singledispatch
async def handle_command(command: Command) -> None:
    """Process commands received from the CLI.

    Parameters
    ----------
    command : Command
        The command to process
    """
    msg = f"Command `{command.command}::{command.action}` has no registered handler."

    raise NotImplementedError(msg)


@handle_command.register(CheckWorkplanCommand)
async def _(command: CheckWorkplanCommand) -> None:
    """Process `CheckWorkplanCommand` commands receieved from the CLI.

    Parameters
    ----------
    command : CheckWorkplanCommand
        The command to process
    """
    request = ValidateWorkplanRequest(path=command.path)

    action_fn = validate_workplan
    if command.use_workflow:
        action_fn = run_validate_workplan_flow

    result = await action_fn(request)

    if result.success:
        print(f"Workplan in `{command.path}` passed validation")
    else:
        print(f"Workplan in `{command.path}` failed validation:\n - {result.error}")


@handle_command.register(PlanWorkplanCommand)
async def _(command: PlanWorkplanCommand) -> None:
    """Process `PlanWorkplanCommand` commands receieved from the CLI.

    Parameters
    ----------
    command : PlanWorkplanCommand
        The command to process
    """
    request = PlanWorkplanRequest(
        path=command.path,
        output_dir=command.output_dir,
    )

    response = await run_plan_workplan_flow(request)

    print(f"Review the execution plan here: {response.plan_path}")


@handle_command.register(GenerateTemplateCommand)
async def _(command: GenerateTemplateCommand) -> None:
    """Process `GenerateTemplateCommand` commands receieved from the CLI.

    Parameters
    ----------
    command : GenerateTemplateCommand
        The command to process
    """
    system_mgr = CStarSystemManager()
    tpl_name = f"{command.template}.yaml"
    schema_name = f"{command.template}-schema.yaml"
    tpl_source_path = system_mgr.environment.template_root / tpl_name

    if not tpl_source_path.exists():
        print(f"Unable to read template file from `{tpl_source_path}`.")

    schema_path: Path | None = None
    template_path: Path | None = None

    if command.path is not None:
        command.path.mkdir(parents=True, exist_ok=True)
        template_path = command.path / tpl_name
        schema_path = command.path / schema_name

    if command.template == "workplan":
        schema = json.dumps(Workplan.model_json_schema(), indent=4)
    else:
        schema = json.dumps(RomsMarblBlueprint.model_json_schema(), indent=4)

    if schema_path:
        schema_ref = f"# yaml-language-server: $schema=file://{schema_path}"
    else:
        schema_ref = "# yaml-language-server: $schema=<schema-uri>"

    template = tpl_source_path.read_text(encoding="utf-8")
    template_lines = template.split("\n")
    template_lines[0] = schema_ref
    template = "\n".join(template_lines)

    if template_path and schema_path:
        schema_path.write_text(schema, encoding="utf-8")
        template_path.write_text(template, encoding="utf-8")

        print(f"{command.template} schema written to `{schema_path}`")
        print(f"{command.template} template written to `{template_path}`")
    else:
        delimiter = "*" * 80

        print(delimiter)
        print(f"* {command.template} schema")
        print(delimiter)
        print(f"{schema}\n")

        print(delimiter)
        print(f"* {command.template} template")
        print(delimiter)
        print(f"{template}\n\n")



@handle_command.register(RunWorkplanCommand)
async def _(command: RunWorkplanCommand) -> None:
    """Process `RunWorkplanCommand` commands receieved from the CLI.

    Parameters
    ----------
    command : RunWorkplanCommand
        The command to process
    """
    print(f"MOCK - handling {command}")


@handle_command.register(CheckBlueprintCommand)
async def _(command: CheckBlueprintCommand) -> None:
    """Process `CheckWorkplanCommand` commands receieved from the CLI.

    Parameters
    ----------
    command : CheckBlueprintCommand
        The command to process
    """
    request = ValidateBlueprintRequest(path=command.path)

    if command.use_workflow:
        action = run_validate_blueprint_flow
    else:
        action = validate_blueprint

    result = await action(request)

    if not result.success:
        print(f"Workplan in `{command.path}` failed validation:\n - {result.error}")
    else:
        print(f"Workplan in `{command.path}` passes validation")


@handle_command.register(RunBlueprintCommand)
async def _(command: RunBlueprintCommand) -> None:
    """Process `RunBlueprintCommand` commands receieved from the CLI.

    Parameters
    ----------
    command : RunBlueprintCommand
        The command to process
    """
    print(f"MOCK - handling {command}")
