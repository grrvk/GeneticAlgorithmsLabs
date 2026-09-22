from __future__ import annotations

import heapq

from graph import Graph


def dijkstra(graph: Graph, source: int) -> tuple[dict[int, float], dict[int, int | None]]:
    dist: dict[int, float] = {source: 0.0}
    prev: dict[int, int | None] = {source: None}
    visited: set[int] = set()
    queue: list[tuple[float, int]] = [(0.0, source)]

    while queue:
        d, u = heapq.heappop(queue)
        if u in visited:
            continue
        visited.add(u)

        for v, weight in graph.neighbors(u).items():
            if d + weight < dist.get(v, float("inf")):
                dist[v] = d + weight
                prev[v] = u
                heapq.heappush(queue, (dist[v], v))

    return dist, prev


def reconstruct_path(prev: dict[int, int | None], source: int, target: int) -> list[int]:
    path = [target]
    while path[-1] != source:
        parent = prev[path[-1]]
        if parent is None:
            raise ValueError(f"no path from {source} to {target}")
        path.append(parent)
    path.reverse()
    return path
