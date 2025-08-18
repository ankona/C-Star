import logging
import textwrap

import pytest

from cstar.base.discretization import Discretization


@pytest.fixture
def discretization() -> Discretization:
    """Create a Discretization instance with fixed parameters for testing."""
    return Discretization(time_step=3)


def test_init(discretization, log: logging.Logger):
    """Test the attributes were set correctly."""
    assert discretization.time_step == 3


def test_str(discretization: Discretization) -> None:
    """Test the string representation is correct."""
    expected_str = textwrap.dedent(
        """\
        Discretization
        --------------
        time_step: 3s
        n_procs_x: 1 (Number of x-direction processors)
        n_procs_y: 1 (Number of y-direction processors)
        """,
    )

    assert str(discretization) == expected_str


def test_repr(discretization: Discretization) -> None:
    """Test the repr representation is correct."""
    expected_repr = """Discretization(time_step=3)"""

    assert repr(discretization) == expected_repr
