from pathlib import Path

from prefect import flow

from cstar.orchestration.models import TaskStatus, Workplan

# from cstar.orchestration.orchestrator import Orchestrator, PrefectLauncher
# from cstar.orchestration.planning import GraphPlanner
from cstar.orchestration.planning import GraphPlanner
from cstar.orchestration.serialization import deserialize
from cstar.orchestration.tasks.plan import validate_workplan
from cstar.orchestration.tasks.request import (
    RunWorkplanRequest,
    ValidateWorkplanRequest,
)
from cstar.orchestration.tasks.response import RunWorkplanResponse

ACTION_NAME = "run workplan"


async def run_workplan(
    request: RunWorkplanRequest,
) -> RunWorkplanResponse:
    """Execute a workplan.

    Parameters
    ----------
    request: RunWorkplanRequest
        Request specifying a workplan to execute

    Returns
    -------
    RunWorkplanResponse
    """
    print(f"{ACTION_NAME.capitalize()} action is starting")

    validation_resp = await validate_workplan(
        ValidateWorkplanRequest(path=request.path)
    )
    if not validation_resp.success:
        raise ValueError(f"Invalid workplan found at `{request.path}`")

    # prep_request = PrepareSlurmComputeRequest()
    # prep_resp = await run_get_allocation_flow(prep_request)
    # slurm_resp = t.cast(PrepareSlurmComputeResponse, prep_resp)
    #
    # if not slurm_resp.job_id:
    #     raise RuntimeError("Unable to complete resource allocation")

    try:
        if workplan := deserialize(request.path, Workplan):
            ...
            _ = GraphPlanner(workplan)
            # # launcher = SlurmLauncher(job_id=slurm_resp.job_id)
            # launcher = PrefectLauncher()  # isn't this circular...
            # # consider
            # orchestrator = Orchestrator(planner, launcher)
            #
            # orchestrator.schedule()
        else:
            print(f"The workplan at `{request.path}` could not be loaded")

    except ValueError as ex:
        print(f"Error occurred: {ex}")

    response = RunWorkplanResponse(
        request_id=request.request_id,
        output_dir=Path.cwd(),  # TODO: what should this response contain?
        status=TaskStatus.Unknown,  # TODO: need to get this from orch/launcher
    )

    print(f"{ACTION_NAME.capitalize()} action is complete: {response}")
    return response


@flow(log_prints=True)
async def run_workplan_flow(
    request: RunWorkplanRequest,
) -> RunWorkplanResponse:
    """Execution a workplan within a flow.

    Parameters
    ----------
    request: RunWorkplanRequest
        Request specifying a workplan to plan

    Returns
    -------
    RunWorkplanResponse
    """
    print(f"{ACTION_NAME.capitalize()} flow is starting")

    response = await run_workplan(request)

    print(f"{ACTION_NAME.capitalize()} flow is complete: {response}")
    return response


# async def main() -> None:
#     """Execute the run-workplan flow using arguments passed via environment variables.
#
#     Required Environment Variables:
#     - CSTAR_WORKPLAN_PATH
#     """
#     print(f"{ACTION_NAME.capitalize()} main is starting")
#
#     path = os.getenv("CSTAR_WORKPLAN_PATH", "")
#
#     request = ValidateWorkplanRequest(path=Path(path))
#     validation_result = await run_validate_workplan_flow(request)
#
#     print(f"{ACTION_NAME.capitalize()} main is complete: {validation_result}")
#
#
# if __name__ == "__main__":
#     """Execute a validation flow."""
#     asyncio.run(main())
