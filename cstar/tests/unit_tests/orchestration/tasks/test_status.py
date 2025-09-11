import typing as t
import uuid
from pathlib import Path
from unittest import mock

import pytest

from cstar.orchestration.models import Application
from cstar.orchestration.orchestrator import Launcher, Step, Task, TaskStatus
from cstar.orchestration.tasks import status
from cstar.orchestration.tasks.request import CheckSlurmStatusRequest


@pytest.fixture
def fake_sacct_result() -> str:
    """Produce faked output from a call to the SLURM `sacct` command."""
    return "abc"


@pytest.fixture
def mock_step() -> Step:
    mock_step = mock.MagicMock(spec=Step)

    step_name = f"mock-step-name-{uuid.uuid4()}"
    mock_step.name = step_name
    mock_step.application = Application.SLEEP
    mock_step.blueprint = Path() / "blueprint.yaml"
    mock_step.depends_on = []

    return mock_step


@pytest.fixture
def mock_task(mock_step: Step) -> t.Generator[Task]:
    # mock_step = mock.MagicMock(spec=Task)
    task = Task(source=mock_step)

    with mock.patch.object(task, "query", new=None):
        yield task


# @pytest.mark.usefixtures("prefect_server")
@pytest.mark.asyncio
async def test_status_flow_fail(mock_task: Task) -> None:
    """Verify that the status flow fails if the task is still in progress."""
    launcher = Launcher()
    base = status.check_status
    task_fn = base.with_options(
        retries=10,
        retry_delay_seconds=0.1,
        persist_result=False,
        refresh_cache=True,  # ignore the cache for duration of the test
    )

    with (
        mock.patch(
            "cstar.orchestration.tasks.status.get_launcher",
            return_value=launcher,
            # inject a launcher that has the task to look up for status
        ),
        mock.patch(
            "cstar.orchestration.orchestrator.Launcher._create_task",
            return_value=mock_task,
            # returning a task that will not start a new process
        ),
    ):
        # prepare launcher internal state
        launcher.launch([t.cast(Step, mock_task.source)])

    with (
        mock.patch(
            "cstar.orchestration.orchestrator.Launcher._query_status",
            return_value={mock_task.source.name: TaskStatus.Active},
            # the task will never appear complete
        ),
        mock.patch.object(status, "check_status", task_fn),
    ):
        request = CheckSlurmStatusRequest(
            name=mock_task.name,
            job_id="mock-job-id",
            task_id=str(
                mock_task.task_id
            ),  # todo: slurm task id is just a string, not a UUID, fix....
        )
        result = await status.handle_request(request)

    assert result == TaskStatus.Active


# @pytest.mark.usefixtures("prefect_server")
async def test_status_task_retry(mock_task: Task) -> None:
    """Verify that the status task retries until the task is done."""
    launcher = Launcher()

    with (
        mock.patch(
            "cstar.orchestration.tasks.status.get_launcher",
            return_value=launcher,
            # inject a launcher that has the task to look up for status
        ),
        mock.patch(
            "cstar.orchestration.orchestrator.Launcher._create_task",
            return_value=mock_task,
            # returning a task that will not start a new process
        ),
    ):
        # prepare launcher internal state
        launcher.launch([t.cast(Step, mock_task.source)])

    base = status.check_status
    task_fn = base.with_options(
        retry_delay_seconds=0.1,
        persist_result=False,
        refresh_cache=True,  # ignore the cache for duration of the test
    )

    # report task completion on the second retry
    with (
        mock.patch(
            # mock status query to avoid starting a reaal external process
            "cstar.orchestration.orchestrator.Launcher._query_status",
            side_effect=[
                {mock_task.source.name: TaskStatus.Active},
                {mock_task.source.name: TaskStatus.Active},
                {mock_task.source.name: TaskStatus.Active},
                {mock_task.source.name: TaskStatus.Active},
                {mock_task.source.name: TaskStatus.Active},
                {mock_task.source.name: TaskStatus.Done},
            ],
        ),
        mock.patch.object(status, "check_status", task_fn),
    ):
        result = await status.check_status(job_id="mock-job-id", task_id=mock_task.name)
        assert result == TaskStatus.Done

    assert result == TaskStatus.Done


@pytest.mark.asyncio
async def test_status_flow_retry(mock_task: Task) -> None:
    """Verify that the status flow succeeds when the status task must retry."""
    launcher = Launcher()

    with (
        mock.patch(
            "cstar.orchestration.tasks.status.get_launcher",
            return_value=launcher,
            # inject a launcher that has the task to look up for status
        ),
        mock.patch(
            "cstar.orchestration.orchestrator.Launcher._create_task",
            return_value=mock_task,
            # returning a task that will not start a new process
        ),
    ):
        # prepare launcher internal state
        launcher.launch([t.cast(Step, mock_task.source)])

    # report task completion on the second retry
    with mock.patch(
        # mock status query to avoid starting a reaal external process
        "cstar.orchestration.orchestrator.Launcher._query_status",
        side_effect=[
            {mock_task.source.name: TaskStatus.Active},
            {mock_task.source.name: TaskStatus.Active},
            {mock_task.source.name: TaskStatus.Done},
        ],
    ):
        base = status.handle_request
        task_fn = base.with_options(
            retry_delay_seconds=0.1,
            persist_result=False,
            refresh_cache=True,  # ignore the cache for duration of the test
        )

        with mock.patch.object(status, "check_status", task_fn):
            result = await status.handle_request.with_options(
                cache_result_in_memory=False
            )(job_id="mock-job-id", task_id=mock_task.name)

    assert result == TaskStatus.Done
