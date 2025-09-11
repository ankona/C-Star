import uuid

from pydantic import BaseModel, Field

from cstar.base.exceptions import CstarError
from cstar.orchestration.models import TaskStatus


class Request(BaseModel):
    """Common request attributes."""

    request_id: uuid.UUID = Field(default_factory=uuid.uuid4, frozen=True)
    """Unique identifier of the request."""


class Response(BaseModel):
    """Common response attributes."""

    request_id: uuid.UUID = Field(default_factory=uuid.uuid4, frozen=True)
    """Unique identifier of the source request."""


class CstarIncompleteError(CstarError):
    """Error raised when a task is active when task results are requested."""

    status: TaskStatus
    """The current status of an incomplete task."""

    def __init__(self, status: TaskStatus, *args) -> None:
        """Initialize the error instance."""
        super().__init__(*args)
        self.status = status


class CstarAllocationError(CstarError):
    """Error raised when resource allocation fails."""
