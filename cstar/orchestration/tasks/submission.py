import os
import time

from prefect import flow, task

from cstar.orchestration.models import Step
from cstar.orchestration.orchestrator import Launcher, SlurmLauncher, Task, TaskStatus


@task
async def submit_slurm_job(step: Step | None = None) -> dict[str, Task]:
    """Submit a job to the SLURM system."""
    print("SLURM submission starting")
    time.sleep(20)

    if not step:
        msg = "Unable to poll status. No step was loaded."
        raise RuntimeError(msg)

    job_id = os.getenv("SLURM_JOB_ID")

    launcher = SlurmLauncher(job_id=job_id)
    tasks = launcher.launch([step])

    # SLURM should start running the job and return a 0.
    # NOTE: the launcher should hide all the slurm-specific junk

    for t in tasks.values():
        if t.status < TaskStatus.Active:
            msg = f"Unable to start task: {task.name}"
            raise RuntimeError(msg)

    print("SLURM submission complete")
    return tasks


@task
async def submit_local_job(step: Step) -> dict[str, Task]:
    """Run a local process."""
    print("Local submission starting")
    time.sleep(20)

    if not step:
        msg = "Unable to poll status. No step was loaded."
        raise RuntimeError(msg)

    launcher = Launcher()
    tasks = launcher.launch([step])

    # NOTE: the launcher should hide all the local-specific junk

    for t in tasks.values():
        if t.status < TaskStatus.Active:
            msg = f"Unable to start task: {task.name}"
            raise RuntimeError(msg)

    print("Local submission complete")
    return tasks


@flow
async def run_flow() -> None:
    """Execute a status check workflow."""
    print("Job submission flow starting")
    t0 = await submit_slurm_job()
    launched_tasks = t0.wait()
    print(f"Job submission flow complete: {launched_tasks}")


if __name__ == "__main__":
    """Execute the flow to submit a job to SLURM."""
    run_flow()
