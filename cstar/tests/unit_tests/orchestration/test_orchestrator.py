from pathlib import Path
from unittest.mock import MagicMock

import networkx as nx

from cstar.orchestration.models import WorkPlan
from cstar.orchestration.orchestrator import Orchestrator, Slugged


def test_build_graph(tmp_path: Path) -> None:
    """Verify that the orchestrator renders an image correctly."""
    # raw_data = {1: [2, 3, 4], 2: [1, 4], 4: [5, 6]}

    raw_data = {
        "task-1": [],
        "task-2": [],
        "task-3": [],
        "task-4": [],
        "task-5": ["task-3", "task-4"],
        "task-6": ["task-1", "task-2", "task-5"],
        "task-7": ["task-5"],
    }

    edges: list[tuple[int | str, int | str]] = []
    for key, predecessor_list in raw_data.items():
        edges.extend((predecessor, key) for predecessor in predecessor_list)

    name_slug = Slugged("test-graph")

    graph = nx.DiGraph(edges, name=name_slug.slug)

    mock_plan = MagicMock(spec=WorkPlan)
    mock_plan.configure_mock(name="mock plan")

    orchestrator = Orchestrator(plan=mock_plan, graph=graph)

    image_path = orchestrator.render(Path())  # tmp_path)

    assert image_path.exists()
