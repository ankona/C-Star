from pathlib import Path
from unittest import mock

import pytest

from cstar.orchestration.orchestrator import Application, Launcher, Step, TaskStatus


def test_launcher_init() -> None:
    """Verify the default initialization is valid and the task list is empty."""
    launcher = Launcher()

    assert not launcher.tasks


@pytest.mark.parametrize(
    "num_tasks",
    [
        1,
        2,
        4,
    ],
)
def test_launcher_launch(tmp_path: Path, num_tasks: int) -> None:
    """Verify a task is launched correctly."""
    launcher = Launcher()

    blueprint_path = tmp_path / "blueprint.yaml"
    blueprint_path.touch()

    steps = [
        Step(
            name=f"test-step-{i}",
            application=Application.SLEEP,
            blueprint=blueprint_path,
        )
        for i in range(num_tasks)
    ]

    tasks = launcher.launch(steps)

    # confirm the correct number of tasks are returned
    assert len(tasks) == num_tasks

    # confirm the launcher tracked the tasks
    assert set(name for name in launcher.tasks) == set(s.name for s in steps)

    # confirm the launcher launched the tasks
    for task in tasks.values():
        assert task.status > TaskStatus.Ready


def test_launcher_report_unstarted(tmp_path: Path) -> None:
    """Verify that task status is reported correctly when the task is not launched."""
    launcher = Launcher()

    blueprint_path = tmp_path / "blueprint.yaml"
    blueprint_path.touch()

    step = Step(
        name="test-step",
        application=Application.SLEEP,
        blueprint=blueprint_path,
    )

    status = launcher.report(step)
    assert status == TaskStatus.Unknown


def test_launcher_reportall_unknown(tmp_path: Path) -> None:
    """Verify that task status is reported correctly for an unknown task."""
    launcher = Launcher()

    blueprint_path = tmp_path / "blueprint.yaml"
    blueprint_path.touch()

    step = Step(
        name="test-step",
        application=Application.SLEEP,
        blueprint=blueprint_path,
    )

    statuses = launcher.report_all([step])

    # confirm a status is returned for the unknown item
    assert statuses

    status = statuses[step.name]
    assert status == TaskStatus.Unknown


def test_launcher_reportall_mixed_inputs(tmp_path: Path) -> None:
    """Verify that task status is reported correctly when known and unknown
    task updates are requested.
    """
    launcher = Launcher()

    blueprint_path = tmp_path / "blueprint.yaml"
    blueprint_path.touch()

    step1 = Step(
        name="test-step-1",
        application=Application.SLEEP,
        blueprint=blueprint_path,
    )

    with mock.patch(
        "cstar.orchestration.orchestrator.StepToCommandAdapter.adapt",
        new=lambda x: ["sleep", "0.01"],
    ):
        tasks = launcher.launch([step1])
        assert step1.name in tasks

    step2 = Step(
        name="test-step-2",
        application=Application.SLEEP,
        blueprint=blueprint_path,
    )

    statuses = launcher.report_all([step1, step2])

    # confirm a status is returned for both known & unknown items
    assert statuses[step1.name] >= TaskStatus.Active
    assert statuses[step2.name] == TaskStatus.Unknown


def test_task_update_status(tmp_path: Path) -> None:
    """Verify that task status is updated correctly."""
    launcher = Launcher()

    blueprint_path = tmp_path / "blueprint.yaml"
    blueprint_path.touch()

    step = Step(
        name="test-step",
        application=Application.SLEEP,
        blueprint=blueprint_path,
    )

    with mock.patch(
        "cstar.orchestration.orchestrator.StepToCommandAdapter.adapt",
        new=lambda x: ["sleep", "0.01"],
    ):
        tasks = launcher.launch([step])

    task = tasks[step.name]
    status_launched = task.status

    statuses_reported = launcher.report_all([task])
    status_reported = statuses_reported[task.name]

    # confirm the task was started
    assert status_launched == status_reported
    assert status_launched == TaskStatus.Active

    # confirm status is retrieved after launcher updates tracking information
    with mock.patch(
        "cstar.orchestration.orchestrator.Launcher._query_status",
        return_value={step.name: TaskStatus.Done},
    ):
        launcher.update()

    status_reported = launcher.report(task)

    # confirm the task was started
    assert status_launched != status_reported
    assert status_reported == TaskStatus.Done
