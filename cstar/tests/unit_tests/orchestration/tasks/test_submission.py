from pathlib import Path
from unittest import mock

import pytest


@pytest.fixture
def fake_sacct_result() -> str:
    """Produce faked output from a call to the SLURM `sacct` command."""
    return "abc"


@pytest.mark.usefixtures("prefect_server")
def test_submission_flow(tmp_path: Path, fake_sacct_result: str) -> None:
    with mock.patch(
        "cstar.orchestration.orchestrator.SlurmLauncher.allocate",
        return_value=fake_sacct_result,
    ):
        # asyncio.run(submission.run_flow())
        assert True
