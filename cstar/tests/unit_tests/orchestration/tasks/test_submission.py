import asyncio
from unittest import mock

import pytest

from cstar.orchestration.tasks import submission


@pytest.fixture
def fake_sacct_result() -> str:
    """Produce faked output from a call to the SLURM `sacct` command."""
    return "abc"


@pytest.mark.usefixtures("prefect_server")
def test_submission_flow(fake_sacct_result: str) -> None:
    with mock.patch("cstar.orchestration.xxxxx", new=fake_sacct_result):
        asyncio.run(submission.run_flow())
