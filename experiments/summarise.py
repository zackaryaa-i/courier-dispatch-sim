"""results/results.csv -> mean ± sd per (demand, strategy) -> results/summary.md"""
import csv
from collections import defaultdict

import numpy as np

IN, OUT = "results/results.csv", "results/summary.md"
DEMAND_ORDER = ["quiet", "normal", "busy", "rush"]
COLS = [  # (csv column, header, decimals)
    ("mean_delivery_min", "mean delivery (min)", 1),
    ("p90_delivery_min", "p90 (min)", 1),
    ("max_delivery_min", "max (min)", 1),
    ("mean_wait_to_assign_min", "wait to assign (min)", 2),
    ("waiting_at_shift_end", "backlog at end", 1),
    ("courier_idle_pct", "idle %", 1),
    ("orders_per_courier_gini", "Gini", 2),
]


def main() -> None:
    with open(IN) as f:
        rows = list(csv.DictReader(f))
    groups = defaultdict(list)
    for r in rows:
        groups[(r["demand"], r["strategy"])].append(r)
    strategies = list(dict.fromkeys(r["strategy"] for r in rows))  # keeps run order
    n_seeds = len(groups[(rows[0]["demand"], rows[0]["strategy"])])

    lines = [
        f"Mean ± standard deviation across {n_seeds} seeds.",
        "",
        "| demand | strategy | " + " | ".join(h for _, h, _ in COLS) + " |",
        "|" + "---|" * (len(COLS) + 2),
    ]
    for d in DEMAND_ORDER:
        for s in strategies:
            g = groups[(d, s)]
            cells = []
            for key, _, dp in COLS:
                v = np.array([float(r[key]) for r in g])
                cells.append(f"{v.mean():.{dp}f} ± {v.std(ddof=1):.{dp}f}")
            lines.append(f"| {d} | {s} | " + " | ".join(cells) + " |")

    text = "\n".join(lines)
    with open(OUT, "w") as f:
        f.write(text + "\n")
    print(text)


if __name__ == "__main__":
    main()
