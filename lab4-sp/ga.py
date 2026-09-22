from __future__ import annotations

import random
from dataclasses import dataclass, field

from graph import Graph

POPULATION_SIZE = 60
OFFSPRING_SIZE = 60
MAX_GENERATIONS = 200
CROSSOVER_RATE = 0.9
MUTATION_RATE = 0.2
STALL_GENERATIONS = 30

Tree = dict[int, int]


def _in_tree(source: int, tree: Tree, node: int) -> bool:
    return node == source or node in tree


def _frontier(graph: Graph, source: int, tree: Tree, remaining: set[int]) -> list[int]:
    return [v for v in remaining if any(_in_tree(source, tree, u) for u in graph.neighbors(v))]


def _add_random_frontier_vertex(
    graph: Graph, source: int, tree: Tree, remaining: set[int], rng: random.Random
) -> bool:
    frontier = _frontier(graph, source, tree, remaining)
    if not frontier:
        return False

    v = rng.choice(frontier)
    candidates = [u for u in graph.neighbors(v) if _in_tree(source, tree, u)]
    tree[v] = rng.choice(candidates)
    remaining.discard(v)
    return True


def build_tree(graph: Graph, source: int, rng: random.Random) -> Tree:
    tree: Tree = {}
    remaining = set(graph.nodes()) - {source}
    while remaining:
        if not _add_random_frontier_vertex(graph, source, tree, remaining, rng):
            break
    return tree


def tree_distances(graph: Graph, source: int, tree: Tree) -> dict[int, float]:
    children: dict[int, list[int]] = {}
    for v, parent in tree.items():
        children.setdefault(parent, []).append(v)

    dist = {source: 0.0}
    order = [source]
    i = 0
    while i < len(order):
        u = order[i]
        i += 1
        for v in children.get(u, []):
            dist[v] = dist[u] + graph.edge_cost(u, v)
            order.append(v)
    return dist


def tree_cost(graph: Graph, source: int, tree: Tree) -> float:
    distances = tree_distances(graph, source, tree)
    return sum(distances[v] for v in tree)


def fitness(graph: Graph, source: int, tree: Tree) -> float:
    return 1.0 / tree_cost(graph, source, tree)


def roulette_select(population: list[Tree], fitnesses: list[float], rng: random.Random) -> Tree:
    return dict(rng.choices(population, weights=fitnesses, k=1)[0])


def _crossover_child(
    graph: Graph,
    source: int,
    parent1: Tree,
    parent2: Tree,
    dist1: dict[int, float],
    dist2: dict[int, float],
    rng: random.Random,
) -> Tree:
    remaining = set(parent1) | set(parent2)

    preferred: dict[int, Tree] = {}
    for v in remaining:
        d1 = dist1.get(v)
        d2 = dist2.get(v)
        if d1 is None:
            preferred[v] = parent2
        elif d2 is None:
            preferred[v] = parent1
        else:
            total = d1 + d2
            p1_probability = d2 / total if total > 0 else 0.5
            preferred[v] = parent1 if rng.random() < p1_probability else parent2

    tree: Tree = {}
    while remaining:
        added_any = False
        for v in list(remaining):
            u = preferred[v].get(v)
            if u is not None and _in_tree(source, tree, u):
                tree[v] = u
                remaining.discard(v)
                added_any = True

        if not added_any:
            if not _add_random_frontier_vertex(graph, source, tree, remaining, rng):
                break

    return tree


def crossover(
    graph: Graph, source: int, parent1: Tree, parent2: Tree, rng: random.Random
) -> tuple[Tree, Tree]:
    if rng.random() > CROSSOVER_RATE:
        return dict(parent1), dict(parent2)

    dist1 = tree_distances(graph, source, parent1)
    dist2 = tree_distances(graph, source, parent2)
    child1 = _crossover_child(graph, source, parent1, parent2, dist1, dist2, rng)
    child2 = _crossover_child(graph, source, parent1, parent2, dist1, dist2, rng)
    return child1, child2


def _drop_subtree(tree: Tree, remaining: set[int], victim: int) -> None:
    children: dict[int, list[int]] = {}
    for v, parent in tree.items():
        children.setdefault(parent, []).append(v)

    stack = [victim]
    while stack:
        v = stack.pop()
        tree.pop(v, None)
        remaining.add(v)
        stack.extend(children.get(v, []))


def mutate(graph: Graph, source: int, tree: Tree, rng: random.Random) -> Tree:
    if rng.random() >= MUTATION_RATE or not tree:
        return dict(tree)

    mutated = dict(tree)
    remaining: set[int] = set()
    victim = rng.choice(list(mutated.keys()))
    _drop_subtree(mutated, remaining, victim)

    while remaining:
        if not _add_random_frontier_vertex(graph, source, mutated, remaining, rng):
            break

    return mutated


@dataclass
class RunResult:
    best_tree: Tree
    best_cost: float
    best_distances: dict[int, float]
    best_fitness: float
    history_best_cost: list[float] = field(default_factory=list)
    history_avg_cost: list[float] = field(default_factory=list)
    generations_run: int = 0
    final_population: list[Tree] = field(default_factory=list)


def run(
    graph: Graph,
    source: int,
    seed: int | None = None,
    population_size: int = POPULATION_SIZE,
    offspring_size: int = OFFSPRING_SIZE,
    max_generations: int = MAX_GENERATIONS,
    stall_generations: int = STALL_GENERATIONS,
) -> RunResult:
    rng = random.Random(seed)

    population = [build_tree(graph, source, rng) for _ in range(population_size)]

    history_best_cost: list[float] = []
    history_avg_cost: list[float] = []

    best_tree: Tree | None = None
    best_cost = float("inf")
    stall = 0
    generation = 0

    for generation in range(1, max_generations + 1):
        costs = [tree_cost(graph, source, tree) for tree in population]
        fitnesses = [1.0 / c for c in costs]

        gen_best_idx = min(range(len(population)), key=lambda i: costs[i])
        gen_best_cost = costs[gen_best_idx]
        history_best_cost.append(gen_best_cost)
        history_avg_cost.append(sum(costs) / len(costs))

        if gen_best_cost < best_cost:
            best_cost = gen_best_cost
            best_tree = population[gen_best_idx]
            stall = 0
        else:
            stall += 1

        if stall >= stall_generations:
            break

        offspring: list[Tree] = []
        while len(offspring) < offspring_size:
            parent1 = roulette_select(population, fitnesses, rng)
            parent2 = roulette_select(population, fitnesses, rng)
            child1, child2 = crossover(graph, source, parent1, parent2, rng)
            child1 = mutate(graph, source, child1, rng)
            child2 = mutate(graph, source, child2, rng)
            offspring.append(child1)
            if len(offspring) < offspring_size:
                offspring.append(child2)

        offspring_costs = [tree_cost(graph, source, tree) for tree in offspring]

        combined = population + offspring
        combined_costs = costs + offspring_costs
        ranked = sorted(range(len(combined)), key=lambda i: combined_costs[i])
        population = [combined[i] for i in ranked[:population_size]]

    assert best_tree is not None
    return RunResult(
        best_tree=best_tree,
        best_cost=best_cost,
        best_distances=tree_distances(graph, source, best_tree),
        best_fitness=1.0 / best_cost,
        history_best_cost=history_best_cost,
        history_avg_cost=history_avg_cost,
        generations_run=generation,
        final_population=population,
    )


def distinct_optimal_trees(
    graph: Graph, source: int, population: list[Tree], best_cost: float, tolerance: float = 1e-9
) -> list[Tree]:
    seen: set[tuple[tuple[int, int], ...]] = set()
    distinct: list[Tree] = []
    for tree in population:
        if abs(tree_cost(graph, source, tree) - best_cost) > tolerance:
            continue
        key = tuple(sorted(tree.items()))
        if key not in seen:
            seen.add(key)
            distinct.append(tree)
    return distinct
