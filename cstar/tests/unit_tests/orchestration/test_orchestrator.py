from pathlib import Path
from unittest.mock import MagicMock

import networkx as nx
import pytest

from cstar.orchestration.models import Workplan
from cstar.orchestration.orchestrator import GraphPlanner, SerialPlanner


@pytest.fixture
def test_graph() -> nx.DiGraph:
    dependency_map = {
        "task-1": [],
        "task-2": [],
        "task-3": [],
        "task-4": [],
        "task-5": ["task-3", "task-4"],
        "task-6": ["task-1", "task-2", "task-5"],
        "task-7": ["task-5"],
    }

    edges: list[tuple[int | str, int | str]] = []
    for key, predecessor_list in dependency_map.items():
        edges.extend((predecessor, key) for predecessor in predecessor_list)

    return nx.DiGraph(edges, name="test-graph")


def test_build_graph(tmp_path: Path, test_graph: nx.DiGraph) -> None:
    """Verify that the orchestrator renders an image correctly."""
    mock_plan = MagicMock(spec=Workplan)
    mock_plan.configure_mock(name="mock plan")

    planner = GraphPlanner(workplan=mock_plan, graph=test_graph)

    image_path = planner.render(tmp_path)

    assert image_path.exists()


def test_serial_planner(tmp_path: Path, test_graph: nx.DiGraph) -> None:
    """Verify that a serialized plan is produced."""
    mock_plan = MagicMock(spec=Workplan)
    mock_plan.configure_mock(name="mock plan")

    if True:
        tmp_path = Path()
    planner = SerialPlanner(workplan=mock_plan, graph=test_graph, artifact_dir=tmp_path)

    # should be one item in the plan for every node and must omit the start node
    assert planner.plan == [
        "task-1",
        "task-2",
        "task-3",
        "task-4",
        "task-6",
        "task-5",
        "task-7",
    ]
