import textwrap

import pytest

from cstar.base.discretization import Discretization


@pytest.fixture
def roms_discretization() -> Discretization:
    """Create a ROMSDiscretization instance with fixed parameters for testing."""
    return Discretization(time_step=3, n_procs_x=2, n_procs_y=123)


@pytest.mark.parametrize(
    ("timestep", "xprocs", "yprocs"),
    [(1, 2, 3), (4, 5, 6), (2, 4, 5)],
)
def test_init(timestep: int, xprocs: int, yprocs: int) -> None:
    """Test the attributes were set correctly."""
    d = Discretization(timestep, xprocs, yprocs)

    assert d.time_step == timestep
    assert d.n_procs_tot / xprocs == yprocs


def test_defaults() -> None:
    """Test defaults are set correctly when not provided."""
    roms_discretization = Discretization(time_step=3)
    assert roms_discretization.n_procs_x == 1
    assert roms_discretization.n_procs_y == 1


def test_n_procs_tot(roms_discretization: Discretization) -> None:
    """Test the n_procs_tot property correctly multiplies n_procs_x and n_procs_y."""
    assert roms_discretization.n_procs_tot == 2 * 123


def test_repr(roms_discretization: Discretization) -> None:
    """Test the repr representation is correct."""
    expected_repr = "Discretization(time_step=3, n_procs_x=2, n_procs_y=123)"
    assert repr(roms_discretization) == expected_repr


def test_str(roms_discretization: Discretization) -> None:
    """Test the string representation is correct."""
    expected_str = textwrap.dedent(
        """\
        Discretization
        --------------
        time_step: 3s
        n_procs_x: 2 (Number of x-direction processors)
        n_procs_y: 123 (Number of y-direction processors)
        """,
    )

    assert expected_str == str(roms_discretization)
