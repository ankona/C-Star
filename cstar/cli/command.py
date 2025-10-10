import os
import typing as t
from pathlib import Path

from pydantic import BaseModel, Field, FilePath, field_validator


class Command(BaseModel):
    """Core command API."""

    command: str
    """The command group being executed.

    Used as a discriminator field.
    """

    action: str
    """The action being performed."""

    use_workflow: bool = Field(False, init=False)
    """Set to `True` to execute the command from within a workflow."""

    def model_post_init(self, _context: t.Any) -> None:
        """Configure cross-cutting command behaviors."""
        self.use_workflow = os.environ.get("CSTAR_ENABLE_WORKFLOW", "0") == "1"


class UsageCommand(Command):
    """A command used to trigger display of CLI usage information."""

    command: t.Literal["usage"] = "usage"


class RunWorkplanCommand(Command):
    """A command used to trigger execution of a workplan."""

    action: t.Literal["run"] = "run"

    path: FilePath
    """Path to a YAML or JSON document containing a serialized workplan."""

    @field_validator("path", mode="after")
    @classmethod
    def expand_path(cls, value: FilePath) -> Path:
        """Expand the path provided by the user after validating it is non-empty and exists."""
        return Path(value).expanduser().resolve()


class CheckWorkplanCommand(Command):
    """A command used to trigger execution of workplan validation."""

    action: t.Literal["check"] = "check"

    path: FilePath
    """Path to a YAML or JSON document containing a serialized workplan."""

    @field_validator("path", mode="after")
    @classmethod
    def expand_path(cls, value: FilePath) -> Path:
        """Expand the path provided by the user after validating it is non-empty and exists."""
        return Path(value).expanduser().resolve()


class RunBlueprintCommand(Command):
    """A command used to trigger execution of a blueprint."""

    action: t.Literal["run"] = "run"

    path: FilePath
    """Path to a YAML or JSON document containing a serialized blueprint."""

    @field_validator("path", mode="after")
    @classmethod
    def expand_path(cls, value: FilePath) -> Path:
        """Expand the path provided by the user after validating it is non-empty and exists."""
        return Path(value).expanduser().resolve()


class CheckBlueprintCommand(Command):
    """A command used to trigger execution of blueprint validation."""

    action: t.Literal["check"] = "check"

    path: FilePath
    """Path to a YAML or JSON document containing a serialized blueprint."""

    @field_validator("path", mode="after")
    @classmethod
    def expand_path(cls, value: FilePath) -> Path:
        """Expand the path provided by the user after validating it is non-empty and exists."""
        return Path(value).expanduser().resolve()
