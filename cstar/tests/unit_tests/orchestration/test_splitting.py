import uuid
from datetime import datetime

import pytest

from cstar.orchestration.models import Application
from cstar.orchestration.transforms import (
    RomsMarblTimeSplitter,
    get_time_slices,
    get_transform,
)


def test_time_splitting():
    """Verify that the time splitting function honors the start and end dates.

    Ensures that no assumptions are made about the 1st and last days of the month.
    """
    start_date = datetime(2025, 1, 1)
    end_date = datetime(2025, 12, 31)

    time_slices = get_time_slices(start_date, end_date)
    assert len(time_slices) == 12
    assert time_slices[0][0] == start_date
    assert time_slices[-1][1] == end_date

    for i, (curr_start, curr_end) in enumerate(reversed(time_slices[1:-1])):
        assert curr_start < curr_end, (
            "Splitter may have produced reversed time boundaries"
        )

        assert curr_start == datetime(curr_end.year, curr_end.month - 1, 1)


@pytest.mark.parametrize(
    "application",
    [
        "roms_marbl",
        Application.ROMS_MARBL.value,
    ],
)
def test_roms_marbl_transform_registry(application: str):
    """Verify that the transform registry returns the expected transform."""
    transform = get_transform(application)

    assert transform is not None
    assert isinstance(transform, RomsMarblTimeSplitter)


@pytest.mark.parametrize(
    "application",
    ["sleep", Application.SLEEP.value, f"unknown-{uuid.uuid4()}"],
)
def test_sleep_transform_registry(application: str):
    """Verify that the transform registry returns no transforms for sleep or unknown applications.

    Confirm that querying the registry does not raise an exception.
    """
    transform = get_transform(application)

    assert not transform


@pytest.mark.parametrize(
    "application",
    [
        Application.ROMS_MARBL.value,
    ],
)
def test_roms_marbl_splitter(application: str):
    """Verify that the transform registry returns the expected transform."""
    transform = get_transform(application)

    assert transform is not None
    assert isinstance(transform, RomsMarblTimeSplitter)
