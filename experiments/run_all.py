"""Every strategy x every demand level x many seeds -> results/results.csv"""
import csv
import time

import numpy as np

from sim.city import make_grid_city
from sim.demand import generate_orders, pick_hotspots
from sim.fleet import make_couriers
from sim.metrics import compute_metrics
from sim.simulator import run_simulation
from strategies.batching import BatchedHungarian
from strategies.greedy import Greedy, NearestOrderGreedy
from strategies.hungarian import Hungarian

SHIFT = 2 * 3600
N_COURIERS = 20
N_HOTSPOTS = 5
SEEDS = range(20)
DEMAND = {"quiet": 40, "normal": 60, "busy": 90, "rush": 120}   # orders/hour
STRATEGIES = [
    Greedy(),
    NearestOrderGreedy(),
    Hungarian(),
    BatchedHungarian(30),
    BatchedHungarian(60),
    BatchedHungarian(120),
]
OUT = "results/results.csv"


def main() -> None:
    city = make_grid_city()          # one city, so the distance cache is shared
    rows = []
    start = time.time()
    for level, per_hour in DEMAND.items():
        for seed in SEEDS:
            rng = np.random.default_rng(seed)
            hotspots = pick_hotspots(city, N_HOTSPOTS, rng)
            orders = generate_orders(city, hotspots, per_hour, SHIFT, rng)
            couriers = make_couriers(city, N_COURIERS, rng)
            for strategy in STRATEGIES:
                res = run_simulation(city, couriers, orders, strategy, SHIFT)
                rows.append({"demand": level, "orders_per_hour": per_hour,
                             "seed": seed, "strategy": strategy.name,
                             **compute_metrics(res)})
        print(f"{level:<7} done  ({time.time() - start:.0f}s elapsed)")

    with open(OUT, "w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=rows[0].keys())
        writer.writeheader()
        writer.writerows(rows)
    print(f"wrote {len(rows)} rows to {OUT}")


if __name__ == "__main__":
    main()
