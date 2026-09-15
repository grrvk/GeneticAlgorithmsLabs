from __future__ import annotations

import random

DEFAULT_NUM_CITIES = 10
DEFAULT_SEED = 42
DEFAULT_BOUNDS = (0.0, 100.0)

Point = tuple[float, float]


def generate_cities(
    num_cities: int = DEFAULT_NUM_CITIES,
    seed: int = DEFAULT_SEED,
    bounds: tuple[float, float] = DEFAULT_BOUNDS,
) -> list[Point]:
    rng = random.Random(seed)
    lo, hi = bounds
    return [(rng.uniform(lo, hi), rng.uniform(lo, hi)) for _ in range(num_cities)]


def distance(a: Point, b: Point) -> float:
    return ((a[0] - b[0]) ** 2 + (a[1] - b[1]) ** 2) ** 0.5


def tour_length(tour: list[int], cities: list[Point]) -> float:
    total = 0.0
    n = len(tour)
    for i in range(n):
        total += distance(cities[tour[i]], cities[tour[(i + 1) % n]])
    return total
