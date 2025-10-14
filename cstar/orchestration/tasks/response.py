import uuid

from pydantic import BaseModel, Field, FilePath

from cstar.orchestration.models import TaskStatus


class Response(BaseModel):
    """Common response attributes."""

    request_id: uuid.UUID = Field(default_factory=uuid.uuid4, frozen=True)
    """Unique identifier of the source request."""


class PlanWorkplanResponse(Response):
    """Describe the result of a planning attempt."""

    plan_path: FilePath
    """The output location for the generated plan graph."""


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


class PrepareComputeResponse(Response):
    """Common response attributes for a resource allocation request."""

    category: str = "unknown"
    """The category of the resources that were allocated."""

    status: TaskStatus
    """The status of the request."""


class PrepareSlurmComputeResponse(PrepareComputeResponse):
    """SLURM-specific resource allocation response."""

    category: str
    """The category of the resources that were allocated."""

    job_id: str
    """The allocation identifier."""
