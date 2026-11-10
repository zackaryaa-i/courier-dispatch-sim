"""Every strategy x every demand level x many seeds -> CSV."""
import csv
import time

import numpy as np

from sim.city import City, make_grid_city
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
SEEDS = range(100)
DEMAND = {"quiet": 40, "normal": 60, "busy": 90, "rush": 120}   # orders/hour
STRATEGIES = [
    Greedy(),
    NearestOrderGreedy(),
    Hungarian(),
    BatchedHungarian(30),
    BatchedHungarian(60),
    BatchedHungarian(120),
]


def run_experiment(city: City, demand: dict[str, int], out: str) -> None:
    rows = []
    start = time.time()
    for level, per_hour in demand.items():
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

    with open(out, "w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=rows[0].keys())
        writer.writeheader()
        writer.writerows(rows)
    print(f"wrote {len(rows)} rows to {out}")


if __name__ == "__main__":
    run_experiment(make_grid_city(), DEMAND, "results/results.csv")
