from __future__ import annotations

import random
from dataclasses import dataclass, field

BOUNDS = (-20.0, 20.0)
BITS_PER_VAR = 16
NUM_VARS = 4
CHROMOSOME_LENGTH = BITS_PER_VAR * NUM_VARS
MAX_UINT = 2**BITS_PER_VAR - 1

POPULATION_SIZE = 40
MAX_GENERATIONS = 300
TOURNAMENT_SIZE = 2
CROSSOVER_RATE = 0.8
MUTATION_RATE = 0.3 / CHROMOSOME_LENGTH
ELITE_COUNT = 1
STALL_GENERATIONS = 50


@dataclass
class RunResult:
    best_chromosome: str
    best_values: tuple[float, float, float, float]
    best_fitness: float
    history_best: list[float] = field(default_factory=list)
    history_avg: list[float] = field(default_factory=list)
    generations_run: int = 0


def f(w: float, x: float, y: float, z: float) -> float:
    return w**3 + x**2 - y**2 - z**2 + 2 * y * z - 3 * w * x + w * z - x * y + 2


def decode(chromosome: str) -> tuple[float, float, float, float]:
    lo, hi = BOUNDS
    values = []
    for i in range(NUM_VARS):
        gene = chromosome[i * BITS_PER_VAR : (i + 1) * BITS_PER_VAR]
        raw = int(gene, 2)
        values.append(lo + raw / MAX_UINT * (hi - lo))
    return tuple(values)


def encode(values: tuple[float, float, float, float]) -> str:
    lo, hi = BOUNDS
    genes = []
    for v in values:
        raw = round((v - lo) / (hi - lo) * MAX_UINT)
        raw = min(max(raw, 0), MAX_UINT)
        genes.append(format(raw, f"0{BITS_PER_VAR}b"))
    return "".join(genes)


def fitness(chromosome: str) -> float:
    return f(*decode(chromosome))


def random_chromosome() -> str:
    return "".join(random.choice("01") for _ in range(CHROMOSOME_LENGTH))


def tournament_select(population: list[str], fitnesses: list[float]) -> str:
    contenders = random.sample(range(len(population)), TOURNAMENT_SIZE)
    winner = max(contenders, key=lambda i: fitnesses[i])
    return population[winner]


def crossover(parent1: str, parent2: str) -> tuple[str, str]:
    if random.random() > CROSSOVER_RATE:
        return parent1, parent2
    point = random.randint(1, CHROMOSOME_LENGTH - 1)
    child1 = parent1[:point] + parent2[point:]
    child2 = parent2[:point] + parent1[point:]
    return child1, child2


def mutate(chromosome: str) -> str:
    bits = list(chromosome)
    for i in range(len(bits)):
        if random.random() < MUTATION_RATE:
            bits[i] = "1" if bits[i] == "0" else "0"
    return "".join(bits)


def run(seed: int | None = None) -> RunResult:
    if seed is not None:
        random.seed(seed)

    population = [random_chromosome() for _ in range(POPULATION_SIZE)]
    history_best: list[float] = []
    history_avg: list[float] = []

    best_chromosome = None
    best_fit = float("-inf")
    stall = 0
    generation = 0

    for generation in range(1, MAX_GENERATIONS + 1):
        fitnesses = [fitness(c) for c in population]

        gen_best_idx = max(range(len(population)), key=lambda i: fitnesses[i])
        gen_best_fit = fitnesses[gen_best_idx]
        history_best.append(gen_best_fit)
        history_avg.append(sum(fitnesses) / len(fitnesses))

        if gen_best_fit > best_fit:
            best_fit = gen_best_fit
            best_chromosome = population[gen_best_idx]
            stall = 0
        else:
            stall += 1

        if stall >= STALL_GENERATIONS:
            break

        ranked = sorted(range(len(population)), key=lambda i: fitnesses[i], reverse=True)
        elites = [population[i] for i in ranked[:ELITE_COUNT]]

        next_population = list(elites)
        while len(next_population) < POPULATION_SIZE:
            parent1 = tournament_select(population, fitnesses)
            parent2 = tournament_select(population, fitnesses)
            child1, child2 = crossover(parent1, parent2)
            next_population.append(mutate(child1))
            if len(next_population) < POPULATION_SIZE:
                next_population.append(mutate(child2))

        population = next_population

    assert best_chromosome is not None
    return RunResult(
        best_chromosome=best_chromosome,
        best_values=decode(best_chromosome),
        best_fitness=best_fit,
        history_best=history_best,
        history_avg=history_avg,
        generations_run=generation,
    )
