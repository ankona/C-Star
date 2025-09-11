from prefect import flow

from cstar.cli.command import CheckBlueprintCommand
from cstar.orchestration.models import RomsMarblBlueprint
from cstar.orchestration.serialization import deserialize
from cstar.orchestration.tasks.response import ValidateBlueprintResponse

ACTION_NAME = "validate blueprint"


async def validate_blueprint(
    request: CheckBlueprintCommand,
) -> ValidateBlueprintResponse:
    """Validate a blueprint.

    Parameters
    ----------
    request: ValidateBlueprintRequest
        Request specifying a blueprint to validate

    Returns
    -------
    ValidateBlueprintResponse
    """
    print(f"{ACTION_NAME.capitalize()} action is starting")
    is_valid = False
    error_msg = ""

    try:
        if _ := deserialize(request.path, RomsMarblBlueprint):
            is_valid = True
    except ValueError as ex:
        error_msg = str(ex)

    response = ValidateBlueprintResponse(
        request_id=request.request_id,
        success=is_valid,
        error=error_msg,
    )

    print(f"{ACTION_NAME.capitalize()} action is complete: {response}")
    return response


@flow(log_prints=True)
async def run_validate_blueprint_flow(
    request: CheckBlueprintCommand,
) -> ValidateBlueprintResponse:
    """Validate a blueprint within a flow.

    Parameters
    ----------
    request: ValidateBlueprintRequest
        Request specifying a blueprint to validate

    Returns
    -------
    ValidateBlueprintResponse
    """
    print(f"{ACTION_NAME.capitalize()} flow is starting")

    response = await validate_blueprint(request)

    print(f"{ACTION_NAME.capitalize()} flow is complete: {response}")
    return response


# async def main() -> None:
#     """Execute the validation flow using arguments passed via environment variables.
#
#     Required Environment Variables:
#     - CSTAR_BLUEPRINT_PATH
#     """
#     print(f"{ACTION_NAME.capitalize()} main is starting")
#
#     path = os.environ.get("CSTAR_BLUEPRINT_PATH", "")
#
#     request = ValidateBlueprintRequest(path=Path(path))
#     validation_result = await run_validate_blueprint_flow(request)
#
#     print(f"{ACTION_NAME.capitalize()} main is complete: {validation_result}")
#
#
# if __name__ == "__main__":
#     """Execute a validation flow."""
#     asyncio.run(main())
