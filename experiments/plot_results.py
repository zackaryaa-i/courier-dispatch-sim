"""Chart: mean delivery time vs demand level, one line per strategy."""
import csv
from collections import defaultdict

import matplotlib
matplotlib.use("Agg")                     # draw to file, no window
import matplotlib.pyplot as plt
import numpy as np
from scipy import stats

IN = "results/results.csv"
OUT = "results/delivery_vs_demand.png"
SERIES = [  # (strategy, label, colour) - fixed order, colourblind-checked palette
    ("greedy", "Greedy (oldest order first)", "#2a78d6"),
    ("greedy_nearest", "Greedy (nearest order first)", "#eb6834"),
    ("hungarian", "Hungarian matching", "#1baf7a"),
    ("batch_60s", "Hungarian, 60 s batches", "#eda100"),
]
INK, MUTED, GRID = "#1f1f1e", "#6b6a64", "#e5e4df"


def load():
    with open(IN) as f:
        rows = list(csv.DictReader(f))
    by = defaultdict(list)   # (strategy, orders_per_hour) -> values
    for r in rows:
        by[(r["strategy"], int(r["orders_per_hour"]))].append(float(r["mean_delivery_min"]))
    levels = sorted({int(r["orders_per_hour"]) for r in rows})
    return by, levels


def mean_ci(v):
    v = np.asarray(v)
    half = stats.t.ppf(0.975, len(v) - 1) * v.std(ddof=1) / np.sqrt(len(v))
    return v.mean(), half


def main() -> None:
    by, levels = load()
    fig, ax = plt.subplots(figsize=(8, 5), dpi=200)

    for key, label, colour in SERIES:
        stats_ = [mean_ci(by[(key, x)]) for x in levels]
        means = np.array([m for m, _ in stats_])
        halves = np.array([h for _, h in stats_])
        ax.fill_between(levels, means - halves, means + halves, color=colour, alpha=0.15, lw=0)
        ax.plot(levels, means, color=colour, lw=2, marker="o", ms=6,
                markeredgecolor="white", markeredgewidth=1.5, label=label)

    ax.axvline(92, color=MUTED, lw=1, ls="--")
    ax.text(93, ax.get_ylim()[1] * 0.97, "≈ fleet capacity", color=MUTED, fontsize=9, va="top")

    ax.set_xticks(levels)
    ax.set_xlabel("Demand (orders per hour, 20 couriers)", color=INK)
    ax.set_ylabel("Mean delivery time (min)", color=INK)
    ax.set_title("Oldest-first dispatch collapses as demand nears fleet capacity",
                 loc="left", color=INK, fontsize=12, pad=22)
    ax.text(0, 1.02, "Grid city, 2-hour shift, 100 seeds per point. Shaded band = 95% CI.",
            transform=ax.transAxes, color=MUTED, fontsize=9)
    ax.grid(axis="y", color=GRID, lw=1)
    ax.set_axisbelow(True)
    for side in ["top", "right"]:
        ax.spines[side].set_visible(False)
    for side in ["left", "bottom"]:
        ax.spines[side].set_color(GRID)
    ax.tick_params(colors=MUTED)
    ax.legend(frameon=False, loc="upper left", fontsize=9, labelcolor=INK)

    fig.tight_layout()
    fig.savefig(OUT)
    print(f"saved {OUT}")


if __name__ == "__main__":
    main()
