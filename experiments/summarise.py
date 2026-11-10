"""results CSV -> mean ± sd per (demand, strategy) -> markdown table."""
import csv
import sys
from collections import defaultdict

import numpy as np

DEMAND_ORDER = ["quiet", "normal", "busy", "rush", "peak"]
COLS = [  # (csv column, header, decimals)
    ("mean_delivery_min", "mean delivery (min)", 1),
    ("p90_delivery_min", "p90 (min)", 1),
    ("max_delivery_min", "max (min)", 1),
    ("mean_wait_to_assign_min", "wait to assign (min)", 2),
    ("waiting_at_shift_end", "backlog at end", 1),
    ("courier_idle_pct", "idle %", 1),
    ("orders_per_courier_gini", "Gini", 2),
]


def main(suffix: str) -> None:
    tag = f"_{suffix}" if suffix else ""
    src, out = f"results/results{tag}.csv", f"results/summary{tag}.md"
    with open(src) as f:
        rows = list(csv.DictReader(f))
    groups = defaultdict(list)
    for r in rows:
        groups[(r["demand"], r["strategy"])].append(r)
    strategies = list(dict.fromkeys(r["strategy"] for r in rows))  # keeps run order
    levels = [d for d in DEMAND_ORDER if any(r["demand"] == d for r in rows)]
    n_seeds = len(groups[(levels[0], strategies[0])])

    lines = [
        f"Mean ± standard deviation across {n_seeds} seeds.",
        "",
        "| demand | strategy | " + " | ".join(h for _, h, _ in COLS) + " |",
        "|" + "---|" * (len(COLS) + 2),
    ]
    for d in levels:
        for s in strategies:
            g = groups[(d, s)]
            cells = []
            for key, _, dp in COLS:
                v = np.array([float(r[key]) for r in g])
                cells.append(f"{v.mean():.{dp}f} ± {v.std(ddof=1):.{dp}f}")
            lines.append(f"| {d} | {s} | " + " | ".join(cells) + " |")

    text = "\n".join(lines)
    with open(out, "w") as f:
        f.write(text + "\n")
    print(text)


if __name__ == "__main__":
    main(sys.argv[1] if len(sys.argv) > 1 else "")
