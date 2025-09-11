import time

from prefect import flow, task

from cstar.orchestration.models import Step
from cstar.orchestration.orchestrator import Launcher, Task, TaskStatus


@task
def poll_status() -> TaskStatus:
    """Run a status check until the monitored task is complete."""
    print("mock - status polling starting")
    time.sleep(20)

    step: Step | Task | None = None

    if not step:
        msg = "Unable to poll status. No step/task was loaded."
        raise RuntimeError(msg)

    launcher = Launcher()
    status = launcher.report(step)

    if status < TaskStatus.Active:
        msg = f"Awaiting task completion. Current status is: {status}"
        raise RuntimeError(msg)

    print("mock - status polling complete")
    return status


@flow
def run_flow() -> None:
    """Execute a status check workflow."""
    print("mock - status check flow starting")
    t0 = poll_status.submit()
    status = t0.wait()
    print(f"mock - status check flow complete: {status}")


if __name__ == "__main__":
    """Execute the flow to monitor a task."""
    run_flow()
