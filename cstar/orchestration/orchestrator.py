import dataclasses
import itertools
import subprocess
import typing as t
import uuid
from abc import ABC, abstractmethod
from collections import defaultdict
from functools import singledispatchmethod
from pathlib import Path
from subprocess import Popen, SubprocessError

import psutil
from pydantic import BaseModel, Field

from cstar.base.utils import _run_cmd
from cstar.orchestration.models import Application, Step, TaskStatus
from cstar.orchestration.planning import Planner

# from cstar.orchestration.tasks.allocation import run_get_allocation_flow
# from cstar.orchestration.tasks.request import (
#     CheckSlurmStatusRequest,
#     PrepareSlurmComputeRequest,
# )
# from cstar.orchestration.tasks.status import handle_request as handle_status_request
from cstar.orchestration.utils import slugify


class ProcessHandle(BaseModel):
    pid: int
    """Process identifier."""
    created_on: int
    """Creation date of the process.

    Used to disambiguate terminated processes in the event of a re-used PID."""

    name: str

    key: uuid.UUID
    """Key identifying the task responsible for starting the process."""


class Task:
    """Track execution status of a `Workplan` step."""

    source: Step | ProcessHandle
    status: TaskStatus
    # rc: int | None = Field(default=None, init=False)
    process: Popen | None = None  # Field(default=None, init=False)
    # pid: int = Field(default=0, init=False)
    state_bag: dict[str, str]
    task_id: uuid.UUID

    CMD: t.ClassVar[str] = "_Cmd"
    PID: t.ClassVar[str] = "_ProcessIdentifier"
    CREATE_TIME: t.ClassVar[str] = "_CreateTime"
    RC: t.ClassVar[str] = "_ReturnCode"

    def __init__(self, *, source: Step | ProcessHandle) -> None:
        """Initialize the task instance."""
        self.source = source
        self.status = TaskStatus.Waiting
        self.process = None
        self.state_bag = {}

        if isinstance(source, Step):
            self.task_id = uuid.uuid1()
        elif isinstance(source, ProcessHandle):
            self._from_handle(source)

    def _from_handle(self, handle: ProcessHandle) -> psutil.Process:
        process = psutil.Process(handle.pid)
        # TODO: get rid of this and use prefect as proxy
        # if process.create_time != handle.created_on:
        #     msg = "PID has been re-used. Unable to determine return code."
        #     raise RuntimeError(msg)
        #     # todo: handle this gracefully later...

        # self.process = process
        self.task_id = handle.key
        self.create_time = handle.created_on
        self.pid = handle.pid

        return process

    @property
    def name(self) -> str:
        """Wrap the step name to simplify task management for an orchestrator.

        NOTE: why bother with a `Named` protocol now...
        """
        return self.source.name

    @property
    def create_time(self) -> float | None:
        if t := self.state_bag.get(Task.CREATE_TIME, None):
            return float(t)
        return None

    @create_time.setter
    def create_time(self, value: float) -> None:
        self.state_bag[Task.CREATE_TIME] = str(value)

    @property
    def cmd(self) -> list[str] | None:
        if cmd_ := self.state_bag.get(Task.CMD, None):
            return cmd_.split(" ")
        return None

    @cmd.setter
    def cmd(self, value: list[str]) -> None:
        self.state_bag[Task.CMD] = " ".join(value)

    @property
    def pid(self) -> int | None:
        if pid_ := self.state_bag.get(Task.PID, None):
            return int(pid_)
        return None

    @pid.setter
    def pid(self, value: int) -> None:
        self.state_bag[Task.PID] = str(value)

    @property
    def rc(self) -> int | None:
        if rc_ := self.state_bag.get(Task.RC, None):
            return int(rc_)

        if self.process and (self.process.returncode is None):
            rc = self.process.returncode
            if rc is not None:
                self.state_bag[Task.RC] = str(rc)

        rc = self.state_bag.get(Task.RC, None)
        return rc if rc is None else int(rc)

    @rc.setter
    def rc(self, value: int) -> None:
        self.state_bag[Task.RC] = str(value)

    def start(self) -> None:
        self.status = TaskStatus.Ready
        if isinstance(self.source, ProcessHandle):
            msg = "This process was started remotely."
            raise RuntimeError(msg)

        cmd = StepToCommandAdapter.adapt(self.source)

        try:
            log_path = Path() / f"{slugify(self.name)}.log"
            fp = log_path.open("+a", encoding="utf-8")

            self.cmd = cmd
            self.process = Popen(
                cmd,
                text=True,
                stdout=fp,
                stderr=subprocess.STDOUT,
                close_fds=True,
            )
            self.pid = self.process.pid

            if details := psutil.Process(self.pid):
                self.create_time = details.create_time()

                msg = (
                    f"Process `{self.pid}` started at `{self.create_time}` "
                    f"with cmd: `{self.cmd}`"
                )
                print(msg)

            self.status = TaskStatus.Active
        except SubprocessError as ex:
            self.status = TaskStatus.Failed
            print(ex)

    def cancel(self) -> None:
        """Cancel the task if it is running."""
        if not self.pid or self.process is None:
            msg = f"No process to stop for task `{self.name}`"
            print(msg)
            return

        if self.process.returncode is not None:
            msg = f"Process `{self.pid}` already stopped."
            print(msg)
            return

        self.query()

        try:
            proc = psutil.Process(self.pid)

            if proc.create_time() != self.create_time:
                # TODO: consider proxying local processes to record the status
                self.status = TaskStatus.Done
                msg = f"Process `{self.pid}` has been recycled, not stopping."
                print(msg)

            for child in proc.children(recursive=True):
                child.kill()
            proc.kill()

            self.process.wait(timeout=1)
            self.query()

            if self.rc is not None and self.rc == 0:
                msg = f"Process `{self.pid}` completed before it was stopped."
                print(msg)
                return

            self.status = TaskStatus.Aborted

            msg = f"Process `{self.pid}` stopped with rc: `{self.rc}`"
            print(msg)
        except psutil.NoSuchProcess:
            # process stopped before we could kill it...
            self.query()
            msg = f"Process `{self.pid}` already stopped with rc: `{self.rc}`"
            print(msg)
        except Exception as ex:
            print(ex)

    def query(self) -> TaskStatus:
        # consider creating a PID-watcher process...
        if not self.pid or not self.process or self.process.returncode is None:
            return self.status

        self.process.poll()
        if self.process.returncode is not None:
            self.rc = self.process.returncode

        if self.process.returncode == 0:
            self.status = TaskStatus.Done
        else:
            self.status = TaskStatus.Failed

        return self.status

    # @property
    # def return_code(self) -> int | None:
    #     """The return code for the process executed for the task.

    #     Returns `None` until the process has completed.
    #     """
    #     if self.status <= TaskStatus.Active or self.process is None:
    #         return None  # temp until done testing...
    #     return self.process.returncode


class FailTask(Task):
    """A task that forces a failure status to be set. Likely unnecessary."""

    status: TaskStatus = Field(default=TaskStatus.Failed, init=False, frozen=True)
    exception: str | None = None

    def __init__(
        self, *, source: Step | ProcessHandle, exception: str | None = None
    ) -> None:
        """Initialize the task instance."""
        super().__init__(source=source)
        self.exception = exception


# class LocalTask:
#     """Track execution status of a locally executing `Workplan` step."""
#     process: Popen | None = None
#     def run(self) -> None:
#         _run_cmd()


# @dataclass
# class StatusCheck:
#     status: TaskStatus
#     task_id:


class CommandParameterizer:
    """An application-specific command generator.

    Brainstorming... may be useful for formatting parameters in a specific way
    for each application type (added category as discriminated union key), or
    to enable setting env vars cleanly before a command...

    ...maybe useful to pass a bunch of kwargs through and let an app-specific
    subclass choose which ones to use to avoid "unknown parameter" errors?

    ...or it may be worthless.
    """

    # maybe make this constant ClassVar per subclass?
    category: Application  # = Field(frozen=True)
    """The application category."""

    executable: str  # = Field(frozen=True)
    """Executable command to parameterize."""

    parameters: tuple[tuple[str, str | float | list[str] | list[float]], ...] = Field(
        frozen=True,
    )
    """Parameters for executing the application."""

    ignored: set[str]
    """Track the parameters that were not used."""

    include: set[str]
    """Parameter enabling white-listing of inputs."""

    env_include: set[str]
    """Parameter enabling white-listing of env vars."""

    env: tuple[tuple[str, str | float | list[str] | list[float]], ...] = Field(
        frozen=True,
    )

    def __init__(
        self,
        category: Application,
        executable: str,
        include: set[str],
        env_include: set[str],
        **kwargs: str | float | list[str] | list[float],
    ) -> None:
        """Configure the instance with parameters necessary to execute."""
        self.category = category
        self.executable = executable
        self.include = include
        self.env_include = env_include
        self.parameters = tuple((k, v) for k, v in kwargs.items() if k in include)
        self.env = tuple((k, v) for k, v in kwargs.items() if k in env_include)

        consumed: set[str] = (include or set()) | (env_include or set())
        self.ignored = {k for k in kwargs if k not in consumed} if consumed else set()

    def _executable(self, *, expand: bool = False) -> str:
        """Determine the executable to be used."""
        if not expand:
            return self.executable

        return f"$(which {self.executable})"

    def generate(self) -> list[str]:
        env = [f"{k}={v}" for k, v in self.env]
        exe = self._executable().split(" ")  # so i can use `sleep 30` for testing
        params = [str(x) for x in itertools.chain.from_iterable(self.parameters)]

        cmd: list[str] = [*env, *exe, *params]
        print(f"Generated cmd: {' '.join(cmd)}")
        return cmd


class StepToCommandAdapter:
    """Adapt a step into the form of a single command for process execution."""

    @classmethod
    def find_executable(cls, application: str) -> str:
        """Locate an executable for the application."""
        if application == Application.SLEEP:
            return "sleep 2"  # TODO: remove after testing
        return "oh-no-you-dont"

    @classmethod
    def adapt(cls, step: Step) -> list[str]:
        """Adapt the step to a list of strings that can be used to start a process."""
        if step.application not in Application:
            msg = "An invalid application was specified"
            raise ValueError(msg)

        app = Application(step.application)

        parameterizer = CommandParameterizer(
            category=app,
            executable=StepToCommandAdapter.find_executable(app),
            include=set(),
            env_include=set(),
            **step.compute_overrides,
            **step.blueprint_overrides,
        )

        return parameterizer.generate()


class Launcher:
    """Launch and monitor local processes."""

    tasks: dict[str, Task]

    def __init__(self) -> None:
        """Initialize the launcher instance."""
        self.tasks: dict[str, Task] = {}
        """Task lookup for all tasks being managed by the launcher instance."""

        self.check_counts: dict[str, int] = defaultdict(lambda: 0)  # TODO: clean up
        """Temporary way to cause mocked tasks to have a short lifespan."""

    def allocate(self) -> str:
        """Allocate launcher-specific resources."""
        # TODO: this probably needs to return something better than a string...
        return "ok"

    @classmethod
    def _create_task(cls, step: Step) -> Task:
        """Placeholder so I can inject return codes until tasks are really started."""
        task = Task(source=step)

        print(task.name)
        print(task.status)
        print(step.name)
        print(step.application)
        print(step.blueprint)
        print(step.depends_on)
        print(step.blueprint_overrides)
        print(step.compute_overrides)
        print(step.workflow_overrides)

        task.start()

        return task

    def add_monitored(self, target: Step | Task) -> bool:
        """Add the target to the set of monitored items."""
        if target.name in self.tasks:
            return True

        working = target if isinstance(target, Task) else Task(source=target)
        self.tasks[working.name] = working
        return True

    def launch(self, steps: list[Step]) -> dict[str, Task]:
        """Launch a task process for the supplied steps and add each new task to
        the tracking container.
        """
        tasks: dict[str, Task] = {}

        for step in steps:
            # TODO: actually start a task...
            task = Launcher._create_task(step)
            tasks[step.name] = task

            task.status = TaskStatus.Failed if task.rc else TaskStatus.Active

        self.tasks.update(tasks)

        return tasks

    def report(self, item: Step | Task) -> TaskStatus:
        """Report the current status of a step (or task).

        Parameters
        ----------
        item : Step or Task
            The `Step` or `Task` instance to report on.
        """
        stats = self.report_all([item])
        return stats[item.name]

    def report_all(self, items: list[Step | Task]) -> dict[str, TaskStatus]:
        """Report the current status of a step (or task).

        Parameters
        ----------
        item : Step or Task
            The `Step` or `Task` instance to report on.
        """
        state_transition_threshold = 4  # test-only: query a few times before transition

        # names = {t.name for t in items}
        statuses: dict[str, TaskStatus] = {
            task.name: (
                (
                    self.tasks[task.name].status
                    if self.check_counts[task.name] < state_transition_threshold
                    else TaskStatus.Done
                )
                if task.name in self.tasks
                else TaskStatus.Unknown
            )
            for task in items
        }

        # test-only: auto-transition using number of checks done on each task.
        for k in self.tasks:
            self.check_counts[k] += 1

        return statuses

    @property
    def active_tasks(self) -> tuple[str, ...]:
        """Retrieve ID's for all tracked tasks that have not yet completed."""
        return tuple(
            name for name in self.tasks if self.tasks[name].status < TaskStatus.Done
        )

    async def update(self) -> None:
        """Retrieve the current status for all managed tasks and update the
        task instance where necessary.
        """
        check_on = self.active_tasks

        # # find any tasks that can be moved out of the actively checked set
        # movable = [
        #     task for task in self.tasks.values() if task.status > TaskStatus.Active
        # ]

        latest_status = await self._query_status(check_on)

        for name in check_on:
            task = self.tasks[name]
            task.status = latest_status[name]

    # @abc.abstractmethod
    async def _query_status(self, task_ids: t.Sequence[str]) -> dict[str, TaskStatus]:
        """Must override method for launcher implementations..."""
        results: dict[str, TaskStatus] = {
            # default results to the current status for known tasks
            name: self.tasks[name].status if name in self.tasks else TaskStatus.Unknown
            for name in task_ids
        }

        for name in task_ids:
            task = self.tasks.get(name, None)
            if not task:
                continue
                # raise RuntimeError(f"Requesting status for untracked task: {name}")

            if task.rc is None:
                status = task.status
            elif not task.rc:
                status = TaskStatus.Done
            else:
                # non-null, non-zero return code found
                status = TaskStatus.Failed

            results[name] = status

        return results

    async def query(
        self, tasks: list[Task] | None = None, task_ids: t.Sequence[str] | None = None
    ) -> dict[str, TaskStatus]:
        """Retrieve mapping containing the status of tracked tasks."""
        all_task_ids: list[str] = list(task_ids or [])

        if tasks:
            all_task_ids.extend(t.name for t in tasks)

        return await self._query_status(all_task_ids)

    async def query_single(
        self, task: Task | None = None, task_id: str | None = None
    ) -> TaskStatus:
        """Retrieve the status of a tracked task."""
        if task and task.name not in self.tasks:
            self.add_monitored(task)

        # TODO: ensure only one value is passed... or, alternatively...
        # TODO: get rid of task_id parameter completely after add the SlurmHandle
        # for converting a request into a checkable SlurmTask
        tid = task.name if task else task_id
        if not tid:
            raise RuntimeError("A task or task ID is required to query.")

        statuses = await self._query_status([tid])
        return statuses[tid]


@dataclasses.dataclass
class JobStatus(ABC):
    state: TaskStatus

    @property
    @abstractmethod
    def is_terminated(self) -> bool: ...

    @property
    @abstractmethod
    def is_running(self) -> bool: ...

    @staticmethod
    @abstractmethod
    def map_status(state: str) -> TaskStatus: ...

    @staticmethod
    @abstractmethod
    def from_raw(state: str) -> "JobStatus": ...


@dataclasses.dataclass
class SlurmJobStatus(JobStatus):
    state: TaskStatus

    @property
    @t.override
    def is_terminated(self) -> bool:
        """Returns `True` if the job has completed."""
        return self.state in {
            TaskStatus.Done,
            TaskStatus.Aborted,
            TaskStatus.Failed,
        }

    @property
    @t.override
    def is_running(self) -> bool:
        """Returns `True` if the job has not yet completed."""
        return self.state in {
            TaskStatus.Waiting,
            TaskStatus.Active,
        }

    @t.override
    @staticmethod
    def map_status(raw_status: str) -> TaskStatus:
        """Map raw output from sacct to the TaskStatus enum.

        Return TaskStatus.UNKNOWN if state cannot be mapped.

        Raises
        ------
        ValueError
            If an empty `raw_state` is provided
        """
        if not raw_status or not raw_status.strip():
            raise ValueError("Unable to map an empty raw status")

        sacct_status_map: dict[str, TaskStatus] = defaultdict(
            lambda: TaskStatus.Unknown
        )
        sacct_status_map.update(
            {
                "PENDING": TaskStatus.Waiting,
                "RUNNING": TaskStatus.Active,
                "COMPLETED": TaskStatus.Done,
                "CANCELLED": TaskStatus.Aborted,
                "FAILED": TaskStatus.Failed,
            }
        )
        key = raw_status.upper()
        return sacct_status_map[key]

    @t.override
    @staticmethod
    def from_raw(raw_state: str) -> "SlurmJobStatus":
        """Convert the raw output of a call to `sacct` into a `SlurmJobStatus` instance.

        Raises
        ------
        ValueError
            If an empty `raw_state` is provided
        """
        if not raw_state or not raw_state.strip():
            raise ValueError("Unable to convert empty raw state")

        status = SlurmJobStatus.map_status(raw_state)
        return SlurmJobStatus(status)


class SlurmLauncher(Launcher):
    """Manage tasks with the SLURM workload manager."""

    job_id: str | None

    def __init__(self, job_id: str | None = None) -> None:
        self.job_id = job_id  # if job_id else self.allocate()
        # TODO: solve for non-pre-allocated compute

    def allocate(self) -> str:
        """Create a SLURM allocation.

        Returns
        -------
        str : The SLURM job ID
        """
        # TODO: get an allocation...
        self.job_id = "mock-slurm-job-id"
        return self.job_id

    async def _retrieve_status(
        self,
        # log: logging.Logger,
        task_id: str | None = None,
        task_name: str | None = None,
    ) -> list[tuple[str, str, str]]:
        """Query SLURM for the status of a job or task.

        Parameters
        ----------
        slurm_job_id : str
            The ID of the main job

        Returns
        -------
        status_lines: list[tuple[str, str, str]]
            Output of the query; tuples containing [job-id, job-status, job-name]

        Raises
        ------
        ValueError
            If an invalid `slurm_job_id` is provided
        """
        if not self.job_id or not self.job_id.strip():
            raise ValueError("Invalid slurm_job_id provided")

        slurm_job_id = self.job_id.strip() if self.job_id else ""
        task_id = task_id.strip() if task_id else ""
        task_name = task_name.strip() if task_name else ""

        sacct_cmd = (
            f"sacct -j {slurm_job_id} "
            "--format=JobID,State,JobName --noheader -P --delimiter=,"
        )
        stdout = _run_cmd(
            sacct_cmd,
            msg_err=f"Failed to retrieve job status using {sacct_cmd}.",
            raise_on_error=True,
        )

        # remove empties and filter to lines containing (job-id, status, job-name) tuple
        status_lines = (x.strip().split(",") for x in stdout.split("\n") if x.strip())
        status_data = filter(lambda x: len(x) == 3, status_lines)
        status_tuples = list(map(lambda x: (x[0], x[1], x[2]), status_data))

        if not status_tuples:
            # log.debug(f"No status results for job {slurm_job_id} found")
            print(f"No status results for job {slurm_job_id} found")

        return status_tuples

    @t.override
    async def _query_status(
        self, task_ids: t.Sequence[str] | None = None
    ) -> dict[str, TaskStatus]:
        """Query the workload manager for current task statuses for the current
        allocation (job id).

        Parameters
        ----------
        tasks : (optional) list of Task
            Results are filtered to include the supplied tasks, when present.
        """
        status_lines = await self._retrieve_status()
        results: dict[str, TaskStatus] = {}

        for _jid, raw_status, job_name in status_lines:
            # result = self._convert_status_line(line)
            status = SlurmJobStatus.map_status(raw_status)
            results[job_name] = status

        if task_ids:
            results = {task_id: results[task_id] for task_id in task_ids}

        return results

    async def query(
        self, tasks: list[Task] | None = None, task_ids: t.Sequence[str] | None = None
    ) -> dict[str, TaskStatus]:
        # def query(self, task_ids: list[str] | None = None) -> dict[str, TaskStatus]:
        """Retrieve status for all tasks in the job."""
        status_map = await self._query_status(task_ids)
        if not status_map:
            print(f"No status results found for the job: {self.job_id}")

        return status_map


# class PrefectLauncher(Launcher):
#     """Manage tasks managed by prefect."""
#
#     def __init__(self) -> None:
#         self.job_id = ""
#
#     def allocate(self) -> str:
#         """Create a SLURM allocation.
#
#         Returns
#         -------
#         str : The SLURM job ID
#         """
#         # TODO: get an allocation...
#         self.job_id = "mock-slurm-job-id"
#
#         compute_req = PrepareSlurmComputeRequest()  # todo: populate
#         alloc_resp = run_get_allocation_flow(compute_req)
#         slurm_alloc_resp = t.cast(PrepareSlurmComputeResponse, alloc_resp)
#         self.job_id = slurm_alloc_resp.job_id
#         # todo: must be able to use pre-existing job id...
#
#         return self.job_id
#
#     @classmethod
#     def _create_task(cls, step: Step) -> Task:
#         """Placeholder so i can inject return codes until tasks are really started."""
#         task = Task(source=step)
#
#         # prefect task are alllllll blueprints
#         # worker_task = WorkerTask(step.blueprint)
#         # worker_task.start()
#
#         # scott notes
#         # - only two prefect tasks are submit to: (submit a blueprint) slurm, check job status
#         # - orchestration around it to get status, plan, etc
#         # - job a, job b
#         #   separate allocations / compute reservations
#         #  - i am not sure i can can create slurm deps betweewn alocations
#         #  DB - register tasks
#         #  - research
#         #    - can we schedule future jobs
#
#         # print(task.name)
#         # print(task.status)
#         # print(step.name)
#         # print(step.application)
#         # print(step.blueprint)
#         # print(step.depends_on)
#         # print(step.blueprint_overrides)
#         # print(step.compute_overrides)
#         # print(step.workflow_overrides)
#         #
#         # task.start()
#
#         # TODO: execute the task itself via prefect flow
#
#         # TODO: execute the monitoring task via prefect flow
#
#         return task
#
#     async def _retrieve_status(
#         self,
#         task_name: str,
#         task_id: str | None = None,
#     ) -> list[tuple[str, str, str]]:
#         """Query SLURM for the status of a job or task.
#
#         Parameters
#         ----------
#         slurm_job_id : str
#             The ID of the main job
#
#         Returns
#         -------
#         status_lines: list[tuple[str, str, str]]
#             Output of the query; tuples containing [job-id, job-status, job-name]
#
#         Raises
#         ------
#         ValueError
#             If an invalid `slurm_job_id` is provided
#         """
#         if not self.job_id or not self.job_id.strip():
#             raise ValueError("Invalid slurm_job_id provided")
#
#         request = CheckSlurmStatusRequest(
#             task_name=task_name,
#             job_id=self.job_id,
#             task_id=task_id or "",
#         )
#         status_resp = await handle_status_request(request)
#         status = status_resp.get(task_name)
#
#         # todo: determine if i need task id to be non-nullable...
#         return [(task_id or "", str(status), task_name)]
#
#     @t.override
#     async def _query_status(
#         self, task_ids: t.Sequence[str] | None = None
#     ) -> dict[str, TaskStatus]:
#         """Query the workload manager for current task statuses for the current
#         allocation (job id).
#
#         Parameters
#         ----------
#         tasks : (optional) list of Task
#             Results are filtered to include the supplied tasks, when present.
#         """
#         # todo: create a batch retrieve status to avoid the null name/taskid type issues
#         if not task_ids:
#             # this should not remain after creating batch retrieve.
#             return {}
#
#         status_checks = [self._retrieve_status(name) for name in task_ids]
#         status_lines = await asyncio.gather(*status_checks)
#
#         results: dict[str, TaskStatus] = {}
#
#         for _jid, raw_status, job_name in itertools.chain.from_iterable(status_lines):
#             status = SlurmJobStatus.map_status(raw_status)
#             results[job_name] = status
#
#         if task_ids:
#             results = {task_id: results[task_id] for task_id in task_ids}
#
#         return results
#
#     async def query(
#         self, tasks: list[Task] | None = None, task_ids: t.Sequence[str] | None = None
#     ) -> dict[str, TaskStatus]:
#         # def query(self, task_ids: list[str] | None = None) -> dict[str, TaskStatus]:
#         """Retrieve status for all tasks in the job."""
#         status_map = await self._query_status(task_ids)
#         if not status_map:
#             print(f"No status results found for the job: {self.job_id}")
#
#         return status_map
#
#
# # class LocalLauncher(Launcher):
# #     """Manage tasks running on local processes."""
#
# #     def _query_status(self, tasks: t.Sequence[str]) -> None:
# #         """Must override method for launcher implementations..."""
# #         # slurm might...
# #         # sacct -j job_id
# #         # statuses = self.parse(t.name) for t in tasks
# #         # map(t.update, statuses)
#
#
# # class SuperfacLauncher(Launcher):
# #     """Manage tasks with the Superfacility API."""
#
# #     def _query_status(self, tasks: t.Sequence[str]) -> None:
# #         """Must override method for launcher implementations..."""
# #         # slurm might...
# #         # sacct -j job_id
# #         # statuses = self.parse(t.name) for t in tasks
# #         # map(t.update, statuses)
#


class Orchestrator:
    """Manage the execution of a planned set of tasks."""

    SLEEP_DURATION: t.ClassVar[float] = 10
    """Wait time between each state query."""

    planner: Planner
    """The planner determining the order of step execution."""

    launcher: Launcher
    """The launcher used to interact with executing tasks."""

    task_lookup: dict[str, Task]
    """Map for direct task retrieval."""

    task_archive: dict[str, Task]
    """Map for direct task retrieval of completed tasks."""

    def __init__(self, planner: Planner, launcher: Launcher) -> None:
        """Prepare the orchestrator to execute a plan.

        Parameters
        ----------
        planner: Planner
            The planner used to prioritize step execution.
        launcher : Launcher
            The launcher used to execute steps.
        """
        self.planner = planner
        self.launcher = launcher
        self.task_lookup = {}
        self.task_archive = {}

    def _start(self, step: Step) -> Task:
        """Use a launcher to trigger step execution.

        Parameters
        ----------
        step : Step
            The step to start

        Returns
        -------
        Task
            Metadata about the process used to enable monitoring progress
        """
        task: Task | None = None

        try:
            tasks = self.launcher.launch([step])
            self.task_lookup[step.name] = tasks[step.name]
        except RuntimeError as ex:
            task = FailTask(source=step, exception=str(ex))
            print(ex)  # logger...

        if not task:
            msg = f"Starting task `{step.name}` failed."
            raise RuntimeError(msg)

        if task.status > TaskStatus.Active:
            self.task_archive[step.name] = task
            msg = f"Unable to launch task for step `{step.name}`"
            raise RuntimeError(msg)

        return task

    @singledispatchmethod
    def run_step(self, step: Step) -> TaskStatus:
        """Trigger execution of a step with the launcher.

        Parameters
        ----------
        step: Step
            The step specifying the executable criteria.

        Returns
        -------
        TaskStatus
            The current status of the newly executed task
        """
        if step.name not in self.task_lookup:
            # status = self.launcher.report(step)
            # if status == TaskStatus.Unknown:
            # launcher has seen this step before.
            # continue
            task = self._start(step)
            return task.status

        task = self.task_lookup[step.name]
        current_status = self.launcher.report(step)

        if task.status != current_status:
            print(f"Task status changed from {task.status} to {current_status}")
            self.task_lookup[step.name].status = current_status

        if current_status > TaskStatus.Active:
            self.planner.remove(step)
            self.task_archive[task.source.name] = self.task_lookup.pop(task.source.name)

        return current_status

    @run_step.register(int)
    def _run_step_int(self, index: int) -> TaskStatus:
        """Execute a specific step from the plan.

        Parameters
        ----------
        index : int
            The index of the step to be executed

        Returns
        -------
        TaskStatus
            The current status of the newly executed task
        """
        # if the SLURM task creates tasks to monitor progress, use original steps.
        steps = self.planner.workplan.steps

        # if using dynamic step generation for monitoring...
        # plan = self.planner.plan()

        if index > len(steps):
            msg = f"Step index is out of range. Index must be less than {len(steps)}"
            raise IndexError(msg)

        step = steps[index]
        return self.run_step(step)

    def schedule(self) -> None:
        """Trigger execution of all steps in the plan."""
        while step := next(self.planner):
            # iterate through all the steps and schedule them
            self.run_step(step)
            # time.sleep(Orchestrator.SLEEP_DURATION)
