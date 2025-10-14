from functools import singledispatchmethod
from pathlib import Path

from prefect import flow, task

from cstar.orchestration.models import TaskStatus
from cstar.orchestration.orchestrator import Launcher, SlurmLauncher
from cstar.orchestration.tasks.core import CstarAllocationError
from cstar.orchestration.tasks.request import (
    PrepareComputeRequest,
    PrepareLocalComputeRequest,
    PrepareSlurmComputeRequest,
)
from cstar.orchestration.tasks.response import (
    PrepareComputeResponse,
    PrepareSlurmComputeResponse,
)


def get_local_launcher() -> Launcher:
    """Instantiate a local launcher.

    Returns
    -------
    Launcher
    """
    return Launcher()


def get_slurm_launcher() -> SlurmLauncher:
    """Instantiate a SLURM launcher.

    Returns
    -------
    SlurmLauncher
    """
    return SlurmLauncher()


class ResourceAllocationHandler:
    """Executes resource preparation requests."""

    @singledispatchmethod
    def handle(self, request: PrepareComputeRequest) -> PrepareComputeResponse:
        """Process prepare-compute requests.

        Parameters
        ----------
        request: PrepareComputeRequest
            Request specifying compute environment characteristics

        Returns
        -------
        PrepareComputeResponse
        """
        print(
            f"Status check could not be routed to a handler: {request.model_dump_json()}"
        )
        return PrepareComputeResponse(
            category=request.category,
            status=TaskStatus.Unknown,
        )

    @handle.register(PrepareLocalComputeRequest)
    def _(self, request: PrepareLocalComputeRequest) -> PrepareComputeResponse:
        """Handle a request for a status update for a task executed locally.

        Parameters
        ----------
        request: PrepareLocalComputeRequest
            Request specifying compute environment characteristics

        Returns
        -------
        PrepareComputeResponse
        """
        launcher = Launcher()
        launcher.allocate()

        # TODO: determine if anything needs to exist for local or if this is just trash
        return PrepareComputeResponse(
            category=request.category,
            status=TaskStatus.Done,
        )

    @handle.register(PrepareSlurmComputeRequest)
    def _(self, request: PrepareSlurmComputeRequest) -> PrepareComputeResponse:
        """Handle a request for a status update for a task executed by SLURM.

        Parameters
        ----------
        request: PrepareSlurmComputeRequest
            Request specifying SLURM compute environment characteristics

        Returns
        -------
        PrepareComputeResponse
        """
        launcher = SlurmLauncher()
        job_id = launcher.allocate()  # TODO: configure from request

        return PrepareSlurmComputeResponse(
            category=request.category,
            status=TaskStatus.Done,
            job_id=job_id,
            request_id=request.request_id,
        )


# @materialize("file://allocate-{run_key}.txt")
@task(
    retries=5,
    retry_delay_seconds=[2, 4, 8, 16, 32],
)
async def allocate_resources() -> TaskStatus:
    """Submit a blocking request to perform required resource allocation(s).

    Returns
    -------
    TaskStatus
    """
    # if not task_id:
    #     raise ValueError("Cannot allocate resources without resource specification.")

    handler = ResourceAllocationHandler()
    response = handler.handle()
    print(f"Result of resource allocation is: {response}")

    run_key = "run-key"  # TODO: what is this?
    status = response.status

    if status > TaskStatus.Active:
        asset_path = Path(f"allocate-{run_key}.txt")

        with asset_path.open("w", encoding="utf-8") as fp:
            fp.write(response.model_dump_json())
    else:
        msg = f"Resource allocation is not complete: `{status}`"
        raise CstarAllocationError(status, msg)

    return status


@flow(log_prints=True)
async def run_flow() -> TaskStatus:
    """Execute a resource allocation workflow.

    Returns
    -------
    TaskStatus
    """
    print("Resource allocation flow starting")

    try:
        status = await allocate_resources()
    except CstarAllocationError as ex:
        print(f"Resource allocation did not complete. Exception is: {ex}")
        status = TaskStatus.Failed

    print(f"Resource allocation flow complete: {status}")
    return status


if __name__ == "__main__":
    """Execute the flow to allocate job resources."""
    run_flow()
