"""Compare strategies on one seed at two demand levels."""
import numpy as np

from sim.city import make_grid_city
from sim.demand import generate_orders, pick_hotspots
from sim.fleet import make_couriers
from sim.simulator import run_simulation
from strategies.greedy import Greedy
from strategies.hungarian import Hungarian

SEED = 0
SHIFT = 2 * 3600
N_COURIERS = 20
STRATEGIES = [Greedy(), Hungarian()]


def summarise(res):
    done = [o for o in res.orders if o.delivered_at is not None]
    times = [(o.delivered_at - o.created_at) / 60 for o in done]
    idle = [100 * c.idle_seconds / res.shift_seconds for c in res.couriers]
    return (f"mean {np.mean(times):5.1f} min | p90 {np.percentile(times, 90):5.1f} min"
            f" | waiting@end {res.waiting_at_shift_end:3d} | idle {np.mean(idle):4.1f}%")


for orders_per_hour in [60, 120]:
    city = make_grid_city()
    rng = np.random.default_rng(SEED)
    hotspots = pick_hotspots(city, 5, rng)
    orders = generate_orders(city, hotspots, orders_per_hour, SHIFT, rng)
    couriers = make_couriers(city, N_COURIERS, rng)

    print(f"\n{orders_per_hour} orders/hour ({len(orders)} orders)")
    for strategy in STRATEGIES:
        res = run_simulation(city, couriers, orders, strategy, SHIFT)
        print(f"  {strategy.name:<10} {summarise(res)}")
