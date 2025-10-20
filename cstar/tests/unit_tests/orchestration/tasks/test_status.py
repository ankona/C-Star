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
    uid = uuid.uuid1()

    mock_step = mock.MagicMock(spec=Step)
    step_name = f"mock-step-name-{uid}"
    mock_step.task_id = str(uid)
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
async def test_status_flow_fail(tmp_path: Path, mock_task: Task) -> None:
    """Verify that the status flow fails if the task is still in progress."""
    launcher = Launcher()
    base = status.check_status
    task_fn = base.with_options(
        retries=10,
        retry_delay_seconds=0.1,
        persist_result=False,
        refresh_cache=True,  # ignore the cache for duration of the test
    )

    # warning: not putting task_id into this...
    # item_result = f"{mock_task.name},{TaskStatus.Active},{mock_task.name}"
    # mock_sacct_resp = f"X,Y,Z\n{item_result}\nP,Q,R\n"

    with (
        mock.patch(
            "cstar.orchestration.tasks.status.get_slurm_launcher",
            return_value=launcher,
            # inject a launcher that has the task to look up for status
        ),
        mock.patch(
            "cstar.orchestration.orchestrator.Launcher._create_task",
            return_value=mock_task,
            # returning a task that will not start a new process
        ),
        # mock.patch(
        #     "cstar.orchestration.orchestrator._run_cmd",
        #     return_value=mock_sacct_resp,
        #     # returning a task that will not start a new process
        # ),
        mock.patch(
            "cstar.orchestration.orchestrator.Launcher._query_status",
            return_value={mock_task.source.name: TaskStatus.Active},
            # the task will never appear complete
            # TODO: should this be name or task_id
        ),
        mock.patch.object(status, "check_status", task_fn),
    ):
        # prepare launcher internal state
        launcher.launch([t.cast(Step, mock_task.source)])

        request = CheckSlurmStatusRequest(
            task_name=mock_task.name,
            job_id="mock-job-id",
            task_id=str(
                mock_task.task_id
            ),  # todo: slurm task id is a string here but uuid inside.
            asset_root=tmp_path.as_posix(),
            # TODO (cont'd) did i just want to re-use name and avoid direct use of tid?
        )
        results = await status.handle_request(request)
        result = results[request.task_name]

    assert result == TaskStatus.Active


# @pytest.mark.usefixtures("prefect_server")
async def test_status_task_retry(tmp_path: Path, mock_task: Task) -> None:
    """Verify that the status task retries until the task is done."""
    launcher = Launcher()

    # item_result = f"{mock_task.task_id},{TaskStatus.Active},{mock_task.name}"
    # mock_sacct_resp = f"X,Y,Z\n{item_result}\nP,Q,R\n"
    # mock_create_task = mock.AsyncMock(side_effect=mock_task)

    with (
        mock.patch(
            "cstar.orchestration.tasks.status.get_local_launcher",
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
            "cstar.orchestration.tasks.status.get_slurm_launcher",
            return_value=launcher,
            # inject a launcher that has the task to look up for status
        ),
        # mock.patch(
        #     "cstar.orchestration.orchestrator._run_cmd",
        #     # "cstar.base.utils._run_cmd",
        #     return_value=mock_sacct_resp,
        #     # mock calling into SLURM
        # ),
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
        # mock.patch.object(status, "check_status", task_fn),
    ):
        request = CheckSlurmStatusRequest(
            task_name=mock_task.name,
            job_id="mock-job-id",
            task_id=mock_task.name,
            asset_root=tmp_path.as_posix(),
        )
        # result = await status.check_status(request)
        result = await task_fn(request)
        assert result == TaskStatus.Done

    assert result == TaskStatus.Done


@pytest.mark.asyncio
async def test_status_flow_retry(tmp_path: Path, mock_task: Task) -> None:
    """Verify that the status flow succeeds when the status task must retry."""
    launcher = Launcher()  # TODO: should use slurm launcher

    # item_result = f"{mock_task.task_id},{TaskStatus.Active},{mock_task.name}"
    # mock_sacct_resp = f"X,Y,Z\n{item_result}\nP,Q,R\n"

    with (
        # mock.patch(
        #     "cstar.orchestration.tasks.status.get_local_launcher",
        #     return_value=launcher,
        #     # inject a launcher that has the task to look up for status
        # ),
        mock.patch(
            "cstar.orchestration.tasks.status.get_slurm_launcher",
            return_value=launcher,
            # inject a launcher that has the task to look up for status
        ),
        mock.patch(
            "cstar.orchestration.orchestrator.Launcher._create_task",
            return_value=mock_task,
            # returning a task that will not start a new process
        ),
        # mock.patch(
        #     "cstar.orchestration.orchestrator._run_cmd",
        #     return_value=mock_sacct_resp,
        #     # returning a task that will not start a new process
        # ),
        mock.patch.object(
            # mock status query to avoid starting a reaal external process
            # "cstar.orchestration.orchestrator.Launcher._query_status",
            launcher,
            "_query_status",
            side_effect=[
                {mock_task.source.name: TaskStatus.Active},
                {mock_task.source.name: TaskStatus.Active},
                {mock_task.source.name: TaskStatus.Done},
            ],
        ),
        mock.patch(
            "cstar.orchestration.tasks.status.get_slurm_launcher",
            return_value=launcher,
            # inject a launcher that has the task to look up for status
        ),
    ):
        # prepare launcher internal state
        launcher.launch([t.cast(Step, mock_task.source)])

        # ensure a broken test completes
        task_fn = status.check_status.with_options(
            retry_delay_seconds=0.1,
            persist_result=False,
            retries=10,
            # refresh_cache=True,  # ignore the cache for duration of the test
            cache_result_in_memory=False,
        )

        request = CheckSlurmStatusRequest(
            # again... name here is re-used poorly
            task_name=mock_task.name,
            job_id="mock-job-id",
            task_id=mock_task.name,
            asset_root=tmp_path.as_posix(),
        )
        with mock.patch.object(status, "check_status", task_fn):
            result = await task_fn(request)

    assert result == TaskStatus.Done
