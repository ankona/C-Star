import uuid

from pydantic import BaseModel, Field

from cstar.orchestration.models import TaskStatus


class Response(BaseModel):
    """Common response attributes."""

    request_id: uuid.UUID = Field(default_factory=uuid.uuid4, frozen=True)
    """Unique identifier of the source request."""


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
