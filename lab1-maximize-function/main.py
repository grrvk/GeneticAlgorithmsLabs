import matplotlib.pyplot as plt

import ga


def main() -> None:
    result = ga.run()
    w, x, y, z = result.best_values

    print(f"Generations run: {result.generations_run}")
    print(f"Best solution:   w={w:.4f}, x={x:.4f}, y={y:.4f}, z={z:.4f}")
    print(f"Best f value:    {result.best_fitness:.4f}")

    plt.figure(figsize=(8, 5))
    plt.plot(result.history_best, label="Best fitness")
    plt.plot(result.history_avg, label="Average fitness", alpha=0.7)
    plt.xlabel("Generation")
    plt.ylabel("Fitness (f value)")
    plt.title("GA Convergence — Maximizing f(w, x, y, z)")
    plt.legend()
    plt.tight_layout()
    plt.savefig("convergence.png", dpi=150)
    print("Saved convergence plot to convergence.png")


if __name__ == "__main__":
    main()
