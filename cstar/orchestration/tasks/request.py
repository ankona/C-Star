import typing as t
import uuid

from pydantic import BaseModel, Field


class Request(BaseModel):
    request_id: uuid.UUID = Field(default_factory=uuid.uuid4, frozen=True, init=False)
    """Unique identifier of a request."""


class CheckStatusRequest(Request):
    """Request the execution of a status check for a target process."""

    category: t.ClassVar[str]
    """The category identifying how the job was run."""

    name: str
    """User-defined name for a task."""


class CheckProcessStatusRequest(CheckStatusRequest):
    """Request the execution of a status check for a local process."""

    category: t.ClassVar[str] = "process"

    pid: int
    """The process identifier to check."""

    create_date: int
    """The process creation date."""

    task_id: uuid.UUID
    """The task ID that created the process."""


class CheckSlurmStatusRequest(CheckStatusRequest):
    """Request the execution of a status check for a SLURM process."""

    category: t.ClassVar[str] = "slurm"

    job_id: str
    """The SLURM allocation identifier."""

    task_id: str
    """The identifier provided by SLURM for the task.

    May be provided in place of a user-provided task name."""


class PrepareComputeRequest(Request):
    """Request the creation of compute resources required to execute work."""

    category: t.ClassVar[str]
    """The category identifying how the job was run."""


class PrepareLocalComputeRequest(PrepareComputeRequest):
    """Create a process host to monitor local tasks.

    NOTE: potential garbage... would stand in the place of a per-job proxy.
    """

    category: t.ClassVar[str] = "process"


class PrepareSlurmComputeRequest(PrepareComputeRequest):
    """Request the creation of compute resources from a SLURM cluster."""

    category: t.ClassVar[str] = "slurm"

    # TODO: must specify allocation attributes
