import asyncio
import os
from pathlib import Path

from prefect import flow

from cstar.orchestration.orchestrator import Workplan
from cstar.orchestration.serialization import deserialize
from cstar.orchestration.tasks.request import ValidateWorkplanRequest
from cstar.orchestration.tasks.response import ValidateWorkplanResponse

ACTION_NAME = "validate workplan"


async def validate_workplan(
    request: ValidateWorkplanRequest,
) -> ValidateWorkplanResponse:
    """Validate a workplan."""
    print(f"{ACTION_NAME.capitalize()} action is starting")
    is_valid = False
    error_msg = ""

    try:
        if _ := deserialize(request.path, Workplan):
            # Workplan.model_validate(workplan)
            is_valid = True
    except ValueError as ex:
        error_msg = str(ex)

    response = ValidateWorkplanResponse(
        request_id=request.request_id,
        success=is_valid,
        error=error_msg,
    )

    print(f"{ACTION_NAME.capitalize()} action is complete: {response}")
    return response


@flow(log_prints=True)
async def run_validate_workplan_flow(
    request: ValidateWorkplanRequest,
) -> ValidateWorkplanResponse:
    """Validate a workplan within a flow."""
    print(f"{ACTION_NAME.capitalize()} flow is starting")

    # validation_task = task(validate_workplan, log_prints=True)
    # response = await validation_task(request)

    response = await validate_workplan(request)

    print(f"{ACTION_NAME.capitalize()} flow is complete: {response}")
    return response


async def main() -> None:
    """Execute the validation flow using arguments passed via environment variables.

    Required Environment Variables:
    - CSTAR_WORKPLAN_PATH
    """
    print(f"{ACTION_NAME.capitalize()} main is starting")

    path = os.environ.get("CSTAR_WORKPLAN_PATH", "")

    request = ValidateWorkplanRequest(path=Path(path))
    validation_result = await run_validate_workplan_flow(request)

    print(f"{ACTION_NAME.capitalize()} main is complete: {validation_result}")


if __name__ == "__main__":
    """Execute a validation flow."""
    asyncio.run(main())
