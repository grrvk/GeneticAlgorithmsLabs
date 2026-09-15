from __future__ import annotations

import random
from collections.abc import Callable
from dataclasses import dataclass, field

from cities import Point, tour_length

POPULATION_SIZE = 100
OFFSPRING_SIZE = 100
MAX_GENERATIONS = 300
CROSSOVER_RATE = 0.9
MUTATION_RATE = 0.2
STALL_GENERATIONS = 50


def random_tour(num_cities: int, rng: random.Random) -> list[int]:
    return rng.sample(range(num_cities), num_cities)


def fitness(tour: list[int], cities: list[Point]) -> float:
    return 1.0 / tour_length(tour, cities)


def roulette_select(population: list[list[int]], fitnesses: list[float], rng: random.Random) -> list[int]:
    return list(rng.choices(population, weights=fitnesses, k=1)[0])


def order_crossover(
    parent1: list[int], parent2: list[int], rng: random.Random
) -> tuple[list[int], list[int]]:
    if rng.random() > CROSSOVER_RATE:
        return list(parent1), list(parent2)

    n = len(parent1)
    i, j = sorted(rng.sample(range(n), 2))

    segment1 = set(parent1[i : j + 1])
    child1 = list(parent1)
    child1[i : j + 1] = [city for city in parent2 if city in segment1]

    segment2 = set(parent2[i : j + 1])
    child2 = list(parent2)
    child2[i : j + 1] = [city for city in parent1 if city in segment2]

    return child1, child2


def mutate_adjacent_swap(tour: list[int], mutation_rate: float, rng: random.Random) -> list[int]:
    tour = list(tour)
    if rng.random() < mutation_rate:
        n = len(tour)
        i = rng.randrange(n)
        j = (i + 1) % n
        tour[i], tour[j] = tour[j], tour[i]
    return tour


def mutate_random_swap(tour: list[int], mutation_rate: float, rng: random.Random) -> list[int]:
    tour = list(tour)
    if rng.random() < mutation_rate:
        i, j = rng.sample(range(len(tour)), 2)
        tour[i], tour[j] = tour[j], tour[i]
    return tour


def mutate_inversion(tour: list[int], mutation_rate: float, rng: random.Random) -> list[int]:
    tour = list(tour)
    if rng.random() < mutation_rate:
        i, j = sorted(rng.sample(range(len(tour)), 2))
        tour[i : j + 1] = reversed(tour[i : j + 1])
    return tour


MutationFn = Callable[[list[int], float, random.Random], list[int]]


@dataclass
class RunResult:
    best_tour: list[int]
    best_distance: float
    best_fitness: float
    history_best_distance: list[float] = field(default_factory=list)
    history_avg_distance: list[float] = field(default_factory=list)
    generations_run: int = 0


def run(
    cities: list[Point],
    seed: int | None = None,
    mutation_fn: MutationFn = mutate_inversion,
    mutation_rate: float = MUTATION_RATE,
    population_size: int = POPULATION_SIZE,
    offspring_size: int = OFFSPRING_SIZE,
    max_generations: int = MAX_GENERATIONS,
    stall_generations: int = STALL_GENERATIONS,
) -> RunResult:
    rng = random.Random(seed)
    num_cities = len(cities)

    population = [random_tour(num_cities, rng) for _ in range(population_size)]

    history_best_distance: list[float] = []
    history_avg_distance: list[float] = []

    best_tour: list[int] | None = None
    best_distance = float("inf")
    stall = 0
    generation = 0

    for generation in range(1, max_generations + 1):
        distances = [tour_length(tour, cities) for tour in population]
        fitnesses = [1.0 / d for d in distances]

        gen_best_idx = min(range(len(population)), key=lambda i: distances[i])
        gen_best_distance = distances[gen_best_idx]
        history_best_distance.append(gen_best_distance)
        history_avg_distance.append(sum(distances) / len(distances))

        if gen_best_distance < best_distance:
            best_distance = gen_best_distance
            best_tour = population[gen_best_idx]
            stall = 0
        else:
            stall += 1

        if stall >= stall_generations:
            break

        offspring: list[list[int]] = []
        while len(offspring) < offspring_size:
            parent1 = roulette_select(population, fitnesses, rng)
            parent2 = roulette_select(population, fitnesses, rng)
            child1, child2 = order_crossover(parent1, parent2, rng)
            child1 = mutation_fn(child1, mutation_rate, rng)
            child2 = mutation_fn(child2, mutation_rate, rng)
            offspring.append(child1)
            if len(offspring) < offspring_size:
                offspring.append(child2)

        offspring_distances = [tour_length(tour, cities) for tour in offspring]

        combined = population + offspring
        combined_distances = distances + offspring_distances
        ranked = sorted(range(len(combined)), key=lambda i: combined_distances[i])
        population = [combined[i] for i in ranked[:population_size]]

    assert best_tour is not None
    return RunResult(
        best_tour=best_tour,
        best_distance=best_distance,
        best_fitness=1.0 / best_distance,
        history_best_distance=history_best_distance,
        history_avg_distance=history_avg_distance,
        generations_run=generation,
    )
