import re
import typing as t
from pathlib import Path

import matplotlib.pyplot as plt
import networkx as nx

from cstar.orchestration.models import Step, WorkPlan

# def slugify(value: str) -> str:
#     """Collapse and replace whitespace characters."""
#     stripped = value.strip()
#     return re.sub(r"\s+", "-", value.strip())


_T = t.TypeVar("_T")


class Slugged(t.Generic[_T]):
    value: _T
    """The wrapped entity."""

    attribute: str | None
    """The attribute name to convert to a slug.

    If no attribute is passed, the original item is used to generate the slug.
    """

    def __init__(self, other: _T, attribute: str | None = None) -> None:
        self.value = other
        self.attribute = attribute

    @property
    def slug(self) -> str:
        original = getattr(self.value, self.attribute) if self.attribute else self.value
        return re.sub(r"\s+", "-", str(original).lower().strip())

    @property
    def source(self) -> _T:
        return self.value


class Orchestrator:
    """Converts workplans into task graphs and manages their execution."""

    plan: WorkPlan

    graph: nx.DiGraph
    """The task graph to be executed."""

    step_map: dict[str, Step]
    """Maps the step slugs to step information."""

    dep_map: dict[str, list[str]]
    """Maps the step slugs to the dependency slugs."""

    name_map: dict[str, str]
    """Maps the step slugs to original names."""

    START_NODE: t.ClassVar[t.Literal["_cstar_start_node"]] = "_cstar_start_node"
    """Fixed name for task graph entrypoint."""

    @classmethod
    def _add_start_node(cls, graph: nx.DiGraph) -> nx.DiGraph:
        # find all steps with no dependencies, allowing immediate start
        graph = t.cast("nx.DiGraph", graph.copy())

        start_edges = [
            (cls.START_NODE, slug)
            for slug in graph.nodes()
            if graph.in_degree(slug) == 0
        ]

        # Add the start node with edges to all independent steps
        graph.add_edges_from(start_edges)

        return graph

    def _plan_to_graph(self) -> nx.DiGraph:
        # any node without a dependency can run immediately
        # start_edges = [
        #     (Orchestrator.START_NODE, slug) for slug, deps in self.dep_map if not deps
        # ]

        graph = nx.DiGraph(self.dep_map, name=self.plan.name)

        # find all steps with no dependencies, allowing immediate start
        start_edges = [
            (Orchestrator.START_NODE, slug)
            for slug in self.graph.nodes()
            if self.graph.in_degree(slug) == 0
        ]

        # Add the start node with edges to all independent steps
        graph.add_edges_from(start_edges)

        return graph

    def __init__(
        self, plan: WorkPlan | None = None, graph: nx.DiGraph | None = None
    ) -> None:
        if plan:
            self.plan = plan

        if plan and not graph:
            slugged = [Slugged(step, "name") for step in plan.steps]
            self.step_map = {step.slug: step.value for step in slugged}
            self.dep_map = {
                step.slug: [Slugged(dep).slug for dep in step.value.depends_on]
                for step in slugged
            }
            self.name_map = {step.slug: step.value.name for step in slugged}
            self.graph = self._plan_to_graph()

        if graph:
            self.step_map = {n: n for n in graph.nodes()}
            self.dep_map = {n: graph.out_edges(n) for n in graph.nodes()}
            self.name_map = {n: n for n in graph.nodes()}
            self.name_map[self.START_NODE] = "start"

            self._og = graph
            self.graph = Orchestrator._add_start_node(graph)

    def render(self, image_directory: Path) -> Path:
        """Render the graph to a file."""
        plt.cla()
        plt.clf()
        pos = nx.bfs_layout(self.graph, self.START_NODE)
        # pos = nx.kamada_kawai_layout(self.graph)  # pretty good
        # pos = nx.spring_layout(self.graph) # barf? adjust weight?
        # pos = nx.shell_layout(self.graph) # not bad
        # pos = nx.circular_layout(self.graph) # not bad
        # pos = nx.planar_layout(self.graph, scale=-1)  # meh
        # pos = nx.spiral_layout(self.graph) # weird
        # pos = nx.random_layout(self.graph)  # trash
        # pos = nx.spectral_layout(self.graph) # bad
        # pos = nx.multipartite_layout(self.graph, "color") # breaks
        # pos = nx.fruchterman_reingold_layout(self.graph) # nope

        self.graph.nodes[Orchestrator.START_NODE]["color"] = "green"

        terminal_nodes = [
            n for n in self.graph.nodes() if self.graph.out_degree(n) == 0
        ]
        for n in terminal_nodes:
            self.graph.nodes[n]["color"] = "red"

        for node, node_data in self.graph.nodes(data=True):
            if not node_data.get("color", None):
                node_data["color"] = "#1f78b4"

        node_colors = [
            node_data["color"] for _, node_data in self.graph.nodes(data=True)
        ]

        nx.draw(
            self.graph,
            node_color=node_colors,
            pos=pos,
            with_labels=False,
            node_size=2000,
        )
        nx.draw_networkx_labels(
            self.graph,
            pos,
            self.name_map,
            clip_on=False,
            font_size=8,
        )

        write_to = image_directory / f"{Slugged(self.plan.name).slug}.png"
        plt.savefig(write_to, bbox_inches="tight", dpi=300)

        return write_to
