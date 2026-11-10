"""Paired comparison: each strategy minus Hungarian, seed by seed."""
import csv
import sys
from collections import defaultdict

import numpy as np
from scipy import stats

IN = "results/results.csv"
BASELINE = "hungarian"
DEMAND_ORDER = ["quiet", "normal", "busy", "rush"]


def main(metric: str) -> None:
    with open(IN) as f:
        rows = list(csv.DictReader(f))
    value = defaultdict(dict)   # (demand, strategy) -> {seed: value}
    for r in rows:
        value[(r["demand"], r["strategy"])][r["seed"]] = float(r[metric])
    strategies = [s for s in dict.fromkeys(r["strategy"] for r in rows) if s != BASELINE]

    print(f"metric: {metric}   (positive = worse than {BASELINE}, if lower is better)\n")
    print(f"{'demand':<7} {'strategy':<15} {'mean diff':>9}   {'95% CI':<17} {'worse on':>9}")
    for d in DEMAND_ORDER:
        base = value[(d, BASELINE)]
        for s in strategies:
            other = value[(d, s)]
            diffs = np.array([other[k] - base[k] for k in base])
            n, mean, sd = len(diffs), diffs.mean(), diffs.std(ddof=1)
            half = stats.t.ppf(0.975, n - 1) * sd / np.sqrt(n)
            worse = int((diffs > 0).sum())
            print(f"{d:<7} {s:<15} {mean:+9.2f}   [{mean - half:+6.2f}, {mean + half:+6.2f}] {worse:>5}/{n}")
        print()


if __name__ == "__main__":
    main(sys.argv[1] if len(sys.argv) > 1 else "mean_delivery_min")
