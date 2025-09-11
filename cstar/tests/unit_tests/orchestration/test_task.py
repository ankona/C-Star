import time
import unittest.mock as mock
from pathlib import Path

from cstar.orchestration.models import (
    Application,
    Workplan,
)
from cstar.orchestration.orchestrator import (
    Step,
    Task,
    TaskStatus,
)


def test_task_start(tmp_path: Path) -> None:
    """Verify that a task can be started."""
    mock_plan = mock.MagicMock(spec=Workplan)
    mock_plan.configure_mock(name="mock plan")

    blueprint_path = tmp_path / Path("blueprint.yaml")
    blueprint_path.touch()

    step = Step(
        name="test-step", application=Application.SLEEP, blueprint=blueprint_path
    )
    task = Task(source=step)

    assert task.create_time is None
    assert task.status == TaskStatus.Waiting
    assert task.pid is None
    assert task.rc is None
    assert task.task_id is not None

    tid = task.task_id
    task.start()

    pid = task.pid

    assert task.create_time is not None and task.create_time > 0
    assert task.status == TaskStatus.Active
    assert pid is not None and pid > 0
    # assert task.rc is not None  # task may not have finished yet

    while task.rc is None:
        time.sleep(0.1)  # wait for task to complete

    assert task.rc == 0
    # todo: the status update isn't done in the task. it breaks launcher tests.
    # - determine where to put it and update this test.

    # assert task.status == TaskStatus.Done
    assert task.pid == pid  # PID should not change
    assert len(task.cmd) > 0
    assert task.task_id == tid  # task ID should not change


def test_task_stop(tmp_path: Path) -> None:
    """Verify that a task can be stopped."""
    mock_plan = mock.MagicMock(spec=Workplan)
    mock_plan.configure_mock(name="mock plan")

    blueprint_path = tmp_path / Path("blueprint.yaml")
    blueprint_path.touch()

    step = Step(
        name="test-step", application=Application.SLEEP, blueprint=blueprint_path
    )
    task = Task(source=step)

    assert task.create_time is None
    assert task.status == TaskStatus.Waiting
    assert task.pid is None
    assert task.rc is None
    assert task.task_id is not None

    with mock.patch(
        "cstar.orchestration.orchestrator.StepToCommandAdapter.find_executable",
        new=lambda cls_: "sleep 30",
    ):
        # tid = task.task_id
        task.start()

    pid = task.pid

    time.sleep(0.05)  # let task start up

    assert task.create_time is not None and task.create_time > 0
    assert task.status == TaskStatus.Active
    assert pid is not None and pid > 0
    assert task.rc is None

    task.cancel()
    time.sleep(0.05)  # let task stop

    assert task.rc != 0  # should be non-zero since we killed it
    assert task.status == TaskStatus.Aborted, f"Expected Aborted, got {task.status}"


def test_task_stop_late(tmp_path: Path) -> None:
    """Verify that calling stop on a task that has completed does not fail."""
    mock_plan = mock.MagicMock(spec=Workplan)
    mock_plan.configure_mock(name="mock plan")

    blueprint_path = tmp_path / Path("blueprint.yaml")
    blueprint_path.touch()

    step = Step(
        name="test-step", application=Application.SLEEP, blueprint=blueprint_path
    )
    task = Task(source=step)

    with mock.patch(
        "cstar.orchestration.orchestrator.StepToCommandAdapter.find_executable",
        new=lambda cls_: "sleep 0.01",
    ):
        # tid = task.task_id
        task.start()

    pid = task.pid

    time.sleep(0.1)  # let task complete
    task.cancel()  # should exit early

    assert task.create_time is not None and task.create_time > 0
    assert task.status == TaskStatus.Done
    assert pid is not None and pid > 0
    assert task.rc == 0  # should be zero since we killed it late
