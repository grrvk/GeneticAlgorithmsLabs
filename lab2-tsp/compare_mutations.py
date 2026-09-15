import cities as cities_mod
import ga

SEED = 42

OPERATORS = {
    "adjacent swap": ga.mutate_adjacent_swap,
    "random swap": ga.mutate_random_swap,
    "inversion": ga.mutate_inversion,
}


def main() -> None:
    city_list = cities_mod.generate_cities(seed=SEED)

    print(f"{'operator':<15} {'best distance':>15} {'generations':>13}")
    for name, mutation_fn in OPERATORS.items():
        result = ga.run(city_list, seed=SEED, mutation_fn=mutation_fn)
        print(f"{name:<15} {result.best_distance:>15.4f} {result.generations_run:>13}")


if __name__ == "__main__":
    main()
