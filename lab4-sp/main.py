import math

import matplotlib.pyplot as plt
from matplotlib.lines import Line2D

import ga
from dijkstra import dijkstra
from graph import DEMO_GRAPH, SOURCE, Graph

SEED = 42
VARIANT_COLORS = ["tab:orange", "tab:purple", "tab:green", "tab:brown", "tab:pink"]


def _layout(graph: Graph, source: int) -> dict[int, tuple[float, float]]:
    others = sorted(n for n in graph.nodes() if n != source)
    positions = {source: (0.0, 0.0)}
    radius = 5.0
    for i, node in enumerate(others):
        angle = 2 * math.pi * i / len(others)
        positions[node] = (radius * math.cos(angle), radius * math.sin(angle))
    return positions


def _add_legend(ax, legend_elements: list[Line2D]) -> None:
    ax.legend(
        handles=legend_elements, loc="upper left", bbox_to_anchor=(1.0, 1.0),
        borderaxespad=0, fontsize=8, markerscale=0.8, handlelength=1.5, labelspacing=0.4,
    )


def _draw_background(ax, graph: Graph, positions: dict[int, tuple[float, float]]) -> None:
    drawn: set[frozenset[int]] = set()
    for u in graph.nodes():
        for v in graph.neighbors(u):
            key = frozenset((u, v))
            if key in drawn:
                continue
            drawn.add(key)
            x1, y1 = positions[u]
            x2, y2 = positions[v]
            ax.plot([x1, x2], [y1, y2], color="lightgray", linewidth=0.8, zorder=1)


def _draw_nodes(ax, positions: dict[int, tuple[float, float]], source: int) -> None:
    xs = [x for x, _ in positions.values()]
    ys = [y for _, y in positions.values()]
    ax.scatter(xs, ys, color="tab:blue", zorder=3, s=80)

    sx, sy = positions[source]
    ax.scatter([sx], [sy], color="tab:red", marker="*", s=220, zorder=4)

    for node, (x, y) in positions.items():
        ax.annotate(
            str(node), (x, y), textcoords="offset points", xytext=(6, 6),
            fontsize=9, fontweight="bold", zorder=5,
        )


def _draw_edges(ax, graph: Graph, positions, edges, color, linewidth=2.5, linestyle="-") -> None:
    for u, v in edges:
        x1, y1 = positions[u]
        x2, y2 = positions[v]
        ax.plot([x1, x2], [y1, y2], color=color, linewidth=linewidth, linestyle=linestyle, zorder=2)

        mx, my = (x1 + x2) / 2, (y1 + y2) / 2
        ax.annotate(
            str(graph.edge_cost(u, v)), (mx, my), fontsize=8, color=color, fontweight="bold",
            ha="center", va="center", zorder=6,
            bbox=dict(boxstyle="round,pad=0.15", fc="white", ec="none", alpha=0.85),
        )


def _tree_edges(tree: dict[int, int]) -> set[tuple[int, int]]:
    return {(parent, v) for v, parent in tree.items()}


def _tree_diff_summary(graph: Graph, source: int, distinct_trees: list[dict[int, int]]) -> str:
    edge_sets = [_tree_edges(tree) for tree in distinct_trees]
    common = set.intersection(*edge_sets)

    lines = []
    for i, (tree, edges) in enumerate(zip(distinct_trees, edge_sets)):
        variant_only = sorted(edges - common)
        if not variant_only:
            continue
        distances = ga.tree_distances(graph, source, tree)
        parts = [
            f"{u}→{v} (w={graph.edge_cost(u, v):g}, dist({v})={distances[v]:g})"
            for u, v in variant_only
        ]
        lines.append(f"Tree #{i + 1} differs at: " + ", ".join(parts))

    total_cost = ga.tree_cost(graph, source, distinct_trees[0])
    lines.append(f"All {len(distinct_trees)} trees total the same cost: {total_cost:g}")
    return "\n".join(lines)


def plot_dijkstra_tree(graph: Graph, source: int, prev: dict[int, int | None]) -> None:
    positions = _layout(graph, source)
    tree_edges = {(parent, v) for v, parent in prev.items() if parent is not None}

    fig, ax = plt.subplots(figsize=(10, 10))
    _draw_background(ax, graph, positions)
    _draw_edges(ax, graph, positions, tree_edges, color="tab:blue")
    _draw_nodes(ax, positions, source)

    legend_elements = [
        Line2D([0], [0], color="lightgray", linewidth=1.5, label="All edges"),
        Line2D([0], [0], color="tab:blue", linewidth=2.5, label="Dijkstra shortest-path tree"),
        Line2D([0], [0], marker="*", color="none", markerfacecolor="tab:red", markersize=14, label="Source"),
    ]
    _add_legend(ax, legend_elements)
    ax.set_title("Dijkstra shortest-path tree")
    ax.set_aspect("equal")
    ax.axis("off")
    fig.tight_layout()
    fig.savefig("dijkstra_tree.png", dpi=150, bbox_inches="tight")
    plt.close(fig)


def plot_ga_trees(graph: Graph, source: int, distinct_trees: list[dict[int, int]]) -> None:
    positions = _layout(graph, source)
    edge_sets = [_tree_edges(tree) for tree in distinct_trees]
    common = set.intersection(*edge_sets) if edge_sets else set()

    fig, ax = plt.subplots(figsize=(10, 10))
    _draw_background(ax, graph, positions)

    if len(distinct_trees) <= 1:
        # Only one optimal tree found — style it exactly like the Dijkstra plot.
        _draw_edges(ax, graph, positions, common, color="tab:blue")
        legend_elements = [
            Line2D([0], [0], color="lightgray", linewidth=1.5, label="All edges"),
            Line2D([0], [0], color="tab:blue", linewidth=2.5, label="GA shortest-path tree"),
        ]
        title = "GA shortest-path tree"
    else:
        _draw_edges(ax, graph, positions, common, color="black", linewidth=2.5)
        legend_elements = [
            Line2D([0], [0], color="lightgray", linewidth=1.5, label="All edges"),
            Line2D([0], [0], color="black", linewidth=2.5, label="Common to all GA-optimal trees"),
        ]
        for i, edges in enumerate(edge_sets):
            variant_only = edges - common
            if not variant_only:
                continue
            color = VARIANT_COLORS[i % len(VARIANT_COLORS)]
            _draw_edges(ax, graph, positions, variant_only, color=color, linestyle="--")
            legend_elements.append(
                Line2D([0], [0], color=color, linewidth=2.5, linestyle="--", label=f"GA-optimal tree #{i + 1}")
            )
        title = f"GA-found optimal shortest-path tree(s) — {len(distinct_trees)} found"

    legend_elements.append(
        Line2D([0], [0], marker="*", color="none", markerfacecolor="tab:red", markersize=14, label="Source")
    )
    _draw_nodes(ax, positions, source)

    _add_legend(ax, legend_elements)
    ax.set_title(title)
    ax.set_aspect("equal")
    ax.axis("off")

    if len(distinct_trees) > 1:
        summary = _tree_diff_summary(graph, source, distinct_trees)
        min_y = min(y for _, y in positions.values())
        text_y = min_y - 0.6
        ax.text(0, text_y, summary, ha="center", va="top", fontsize=9)

    fig.tight_layout()
    fig.savefig("ga_trees.png", dpi=150, bbox_inches="tight")
    plt.close(fig)


def main() -> None:
    dijkstra_dist, prev = dijkstra(DEMO_GRAPH, SOURCE)
    result = ga.run(DEMO_GRAPH, SOURCE, seed=SEED)

    print(f"Generations run: {result.generations_run}")
    print(f"Best total cost: {result.best_cost:.4f}")
    print()
    print(f"{'Vertex':>6} | {'Dijkstra':>10} | {'GA':>10} | {'Gap %':>8}")
    print("-" * 42)

    targets = sorted(v for v in dijkstra_dist if v != SOURCE)
    total_dijkstra = 0.0
    for v in targets:
        d_dist = dijkstra_dist[v]
        ga_dist = result.best_distances[v]
        gap = (ga_dist - d_dist) / d_dist * 100 if d_dist > 0 else 0.0
        total_dijkstra += d_dist
        print(f"{v:>6} | {d_dist:>10.2f} | {ga_dist:>10.2f} | {gap:>7.2f}%")

    print("-" * 42)
    total_gap = (result.best_cost - total_dijkstra) / total_dijkstra * 100
    print(f"{'total':>6} | {total_dijkstra:>10.2f} | {result.best_cost:>10.2f} | {total_gap:>7.2f}%")

    plt.figure(figsize=(8, 5))
    plt.plot(result.history_best_cost, label="Best total cost")
    plt.plot(result.history_avg_cost, label="Average total cost", alpha=0.7)
    plt.xlabel("Generation")
    plt.ylabel("Total tree cost")
    plt.title("GA Convergence — Shortest Path Tree")
    plt.legend()
    plt.tight_layout()
    plt.savefig("convergence.png", dpi=150)
    print("\nSaved convergence plot to convergence.png")

    distinct_trees = ga.distinct_optimal_trees(
        DEMO_GRAPH, SOURCE, result.final_population, result.best_cost
    )
    print(f"Distinct GA-optimal trees in final population: {len(distinct_trees)}")

    plot_dijkstra_tree(DEMO_GRAPH, SOURCE, prev)
    print("Saved Dijkstra tree plot to dijkstra_tree.png")

    plot_ga_trees(DEMO_GRAPH, SOURCE, distinct_trees)
    print("Saved GA tree(s) plot to ga_trees.png")


if __name__ == "__main__":
    main()
