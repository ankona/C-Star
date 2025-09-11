from pydantic import BaseModel, DirectoryPath, Field, FilePath

from cstar.orchestration.models import TaskStatus


class Response(BaseModel):
    """Common response attributes."""

    request_id: str = Field(frozen=True)
    """Unique identifier of the source request."""


class PlanWorkplanResponse(Response):
    """Describe the result of a planning attempt."""

    plan_path: FilePath
    """The output location for the generated plan graph."""


class RunWorkplanResponse(Response):
    """Describe the result of a workplan execution attempt."""

    output_dir: DirectoryPath
    """The directory where workplan outputs are stored."""

    status: TaskStatus
    """Current status of the workplan upon handling of the request."""


class ValidateWorkplanResponse(Response):
    """Describe the success or failue of validation."""

    success: bool
    """Flag indicating the success/failure of the validation."""

    error: str
    """Validation errors causing a failure."""


class ValidateBlueprintResponse(Response):
    """Describe the success or failue of validation."""

    success: bool
    """Flag indicating the success/failure of the validation."""

    error: str
    """Validation errors causing a failure."""


class CheckStatusResponse(Response):
    """Common response attributes for a status check request."""

    category: str
    """The category of the target that was checked."""

    status: TaskStatus
    """The status of the target."""


class CheckSlurmStatusResponse(CheckStatusResponse):
    """Common response attributes for a status check request."""

    category: str = "slurm"
    """The category of the target that was checked."""

    job_id: str
    """The SLURM job id."""

    task_id: str
    """The SLURM task id."""

    name: str
    """The SLURM task name."""


class PrepareComputeResponse(Response):
    """Common response attributes for a resource allocation request."""

    category: str = "unknown"
    """The category of the resources that were allocated."""

    status: TaskStatus
    """The status of the request."""


class PrepareSlurmComputeResponse(PrepareComputeResponse):
    """SLURM-specific resource allocation response."""

    category: str = "SLURM"
    """The category of the resources that were allocated."""

    job_id: str
    """The allocation identifier."""
