import os
import typing as t
from functools import singledispatchmethod
from pathlib import Path

from prefect import flow, task

from cstar.orchestration.models import TaskStatus
from cstar.orchestration.orchestrator import (
    Launcher,
    ProcessHandle,
    SlurmLauncher,
    Task,
)
from cstar.orchestration.tasks.core import CstarIncompleteError
from cstar.orchestration.tasks.request import (
    CheckProcessStatusRequest,
    CheckSlurmStatusRequest,
    CheckStatusRequest,
)
from cstar.orchestration.tasks.response import (
    CheckSlurmStatusResponse,
    CheckStatusResponse,
)


def get_local_launcher() -> Launcher:
    """Instantiate a local launcher.

    Returns
    -------
    Launcher
    """
    return Launcher()


def get_slurm_launcher(job_id: str) -> SlurmLauncher:
    """Instantiate a SLURM launcher.

    Parameters
    ----------
    job_id : str
        The allocation ID the launcher will use

    Returns
    -------
    SlurmLauncher
    """
    return SlurmLauncher(job_id)


class StatusCheckHandler:
    """Executes status check requests."""

    @singledispatchmethod
    async def handle(self, request: CheckStatusRequest) -> CheckStatusResponse:
        """Handle check status requests.

        Parameters
        ----------
        request : CheckStatusRequest
            Request specifying a workplan to perform a status check on

        Returns
        -------
        CheckStatusResponse
        """
        print(
            f"Status check could not be routed to a handler: {request.model_dump_json()}"
        )
        return CheckStatusResponse(
            category=request.category,
            status=TaskStatus.Unknown,
            request_id=request.request_id,
        )

    @handle.register(CheckProcessStatusRequest)
    async def _(self, request: CheckProcessStatusRequest) -> CheckStatusResponse:
        """Handle a request for a status update for a task executed locally.

        Parameters
        ----------
        request : CheckProcessStatusRequest
            Request specifying a local process to perform a status check on

        Returns
        -------
        CheckStatusResponse
        """
        self.launcher = get_local_launcher()

        task = Task(
            source=ProcessHandle(
                pid=request.pid,
                created_on=request.create_date,
                name=request.task_name,
                key=request.task_id,
            )
        )

        status = await self.launcher.query_single(task)

        return CheckStatusResponse(
            category=request.category,
            status=status,
            request_id=request.request_id,
        )

    @handle.register(CheckSlurmStatusRequest)
    async def _(self, request: CheckSlurmStatusRequest) -> CheckStatusResponse:
        """Handle a request for a status update for a task executed by SLURM.

        Parameters
        ----------
        request : CheckSlurmStatusRequest
            Request specifying a SLURM job to check status on

        Returns
        -------
        CheckStatusResponse
        """
        self.launcher = get_slurm_launcher(request.job_id)

        status = await self.launcher.query_single(
            task_id=request.task_name,  # something is wrong w/task id / name usage. need to remove task_id and just see how this works without the uuid
        )

        return CheckSlurmStatusResponse(
            category=request.category,
            status=status,
            request_id=request.request_id,
            job_id=request.job_id,
            task_id=request.task_id,
            name=request.task_name,
        )


async def retry_handler(task, task_run, state) -> bool:
    """
    Retry the status check task until it reaches any terminal state.

    Terminal states include:
    - Done
    - Aborted
    - Failed
    """
    try:
        # TODO: determine if i can see that I've reached the end of my retries
        # and return the actual value (likely active)
        task_result = await state.result()
        status = t.cast(TaskStatus, task_result)
        return status < TaskStatus.Done
    except CstarIncompleteError as ex:
        print(ex)
        return True

    return False


# TODO: consider retry_delay_seconds=exponential_backoff(backoff_factor=2)
# @materialize("file://status-jobid-taskid.txt")
@task(
    retries=10,
    retry_delay_seconds=5,
    retry_condition_fn=retry_handler,
)
async def check_status(request: CheckStatusRequest) -> TaskStatus:
    """Submit a blocking request to retrieve the status of all tasks.

    Parameters
    ----------
    request : CheckStatusRequest
        Request specifying details of a task to perform a status check for

    Returns
    -------
    TaskStatus
    """
    if not request.task_name:
        raise ValueError("Cannot check status without a task id.")

    handler = StatusCheckHandler()
    response = await handler.handle(request)

    print(f"Current status of task: {request.task_name} is status: {response.status}")

    status = response.status

    if status > TaskStatus.Active:
        # find a prefect-y way to set this
        asset_root = Path(request.asset_root) if request.asset_root else Path.cwd()
        asset_path = asset_root / f"status-{request.request_id}"

        with asset_path.open("w", encoding="utf-8") as fp:
            fp.write(str(status))
    else:
        msg = f"Status check for task `{request.task_name}` is not complete: `{status}`"
        raise CstarIncompleteError(status, msg)

    return status


@flow(log_prints=True)
async def handle_request(request: CheckStatusRequest) -> dict[str, TaskStatus]:
    """Execute a status check workflow that succeeds only when the task is done.

    Parameters
    ----------
    request : CheckStatusRequest
        The request to handle

    Returns
    -------
    dict[str, TaskStatus]:
        Mapping of task ID to task status.
    """
    print("Job status flow starting")

    try:
        status = await check_status(request)
    except CstarIncompleteError as ex:
        print(f"Status check did not complete. Task status is: {ex.status}")
        return {request.task_name: ex.status}

    print(f"Job status flow complete: {status}")

    return {request.task_name: status}


if __name__ == "__main__":
    """Execute the flow to submit a job to SLURM."""
    job_id = os.environ.get("SLURM_JOB_ID", "")
    task_id = os.environ.get("TASK_ID", "")  # TODO: fix this nonsense
    task_name = os.environ.get("TASK_NAME", "")  # TODO: fix this empty value

    request = CheckSlurmStatusRequest(
        task_name=task_name, job_id=job_id, task_id=task_id
    )
    status_results = handle_request(request)

    print(f"Status check result: {status_results}")
