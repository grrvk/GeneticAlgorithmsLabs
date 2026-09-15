import matplotlib.pyplot as plt
from matplotlib.lines import Line2D

import cities as cities_mod
import ga

SEED = 42


def main() -> None:
    city_list = cities_mod.generate_cities(seed=SEED)
    result = ga.run(city_list, seed=SEED)

    print(f"Generations run: {result.generations_run}")
    print(f"Best distance:   {result.best_distance:.4f}")
    print(f"Best tour:       {result.best_tour}")

    plt.figure(figsize=(8, 5))
    plt.plot(result.history_best_distance, label="Best distance")
    plt.plot(result.history_avg_distance, label="Average distance", alpha=0.7)
    plt.xlabel("Generation")
    plt.ylabel("Tour distance")
    plt.title("GA Convergence — TSP")
    plt.legend()
    plt.tight_layout()
    plt.savefig("convergence.png", dpi=150)
    print("Saved convergence plot to convergence.png")

    tour = result.best_tour
    route_xs = [city_list[i][0] for i in tour] + [city_list[tour[0]][0]]
    route_ys = [city_list[i][1] for i in tour] + [city_list[tour[0]][1]]
    all_xs = [x for x, _ in city_list]
    all_ys = [y for _, y in city_list]
    n = len(city_list)

    plt.figure(figsize=(6, 6))

    for i in range(n):
        for j in range(i + 1, n):
            xi, yi = city_list[i]
            xj, yj = city_list[j]
            plt.plot([xi, xj], [yi, yj], color="lightgray", linewidth=0.6, zorder=1)

    plt.plot(route_xs, route_ys, "-", color="tab:green", linewidth=2.5, zorder=2)
    plt.scatter(all_xs, all_ys, color="tab:blue", zorder=3)
    plt.scatter(
        [city_list[tour[0]][0]],
        [city_list[tour[0]][1]],
        color="tab:red",
        marker="*",
        s=200,
        zorder=4,
    )
    for idx, (x, y) in enumerate(city_list):
        plt.annotate(str(idx), (x, y), textcoords="offset points", xytext=(4, 4), fontsize=8)

    legend_elements = [
        Line2D([0], [0], color="lightgray", linewidth=1.5, label="All possible connections"),
        Line2D([0], [0], color="tab:green", linewidth=2.5, label="Chosen route"),
        Line2D([0], [0], marker="o", color="none", markerfacecolor="tab:blue", markersize=8, label="Cities"),
        Line2D([0], [0], marker="*", color="none", markerfacecolor="tab:red", markersize=14, label="Start"),
    ]
    plt.legend(handles=legend_elements, loc="upper left", bbox_to_anchor=(1.02, 1), borderaxespad=0)
    plt.title(f"All Connections vs. Chosen Route (distance = {result.best_distance:.2f})")
    plt.xlabel("x")
    plt.ylabel("y")
    plt.tight_layout()
    plt.savefig("best_route.png", dpi=150, bbox_inches="tight")
    print("Saved best route plot to best_route.png")


if __name__ == "__main__":
    main()
