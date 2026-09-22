from __future__ import annotations

import random
from dataclasses import dataclass, field


@dataclass
class Graph:
    adjacency: dict[int, dict[int, float]] = field(default_factory=dict)

    def add_edge(self, u: int, v: int, weight: float) -> None:
        self.adjacency.setdefault(u, {})[v] = weight
        self.adjacency.setdefault(v, {})[u] = weight

    def nodes(self) -> list[int]:
        return list(self.adjacency.keys())

    def neighbors(self, node: int) -> dict[int, float]:
        return self.adjacency[node]

    def edge_cost(self, u: int, v: int) -> float:
        return self.adjacency[u][v]


def build_graph(edges: list[tuple[int, int, float]]) -> Graph:
    graph = Graph()
    for u, v, weight in edges:
        graph.add_edge(u, v, weight)
    return graph


def generate_random_graph(
    num_nodes: int, extra_edges: int, weight_range: tuple[int, int], seed: int
) -> Graph:
    rng = random.Random(seed)
    graph = Graph()

    nodes = list(range(1, num_nodes + 1))
    for i in range(2, num_nodes + 1):
        j = rng.randint(1, i - 1)
        graph.add_edge(i, j, rng.randint(*weight_range))

    added = 0
    attempts = 0
    while added < extra_edges and attempts < extra_edges * 20:
        attempts += 1
        u, v = rng.sample(nodes, 2)
        if v in graph.adjacency.get(u, {}):
            continue
        graph.add_edge(u, v, rng.randint(*weight_range))
        added += 1

    return graph


SOURCE = 1
DEMO_GRAPH = generate_random_graph(num_nodes=14, extra_edges=14, weight_range=(1, 15), seed=9)
