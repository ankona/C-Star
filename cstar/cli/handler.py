from functools import singledispatch

from cstar.cli.command import (
    CheckBlueprintCommand,
    CheckWorkplanCommand,
    Command,
    PlanWorkplanCommand,
    RunBlueprintCommand,
    RunWorkplanCommand,
)
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
