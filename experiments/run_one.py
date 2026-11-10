"""Run one shift with one strategy and print a quick summary."""
import numpy as np

from sim.city import make_grid_city
from sim.demand import generate_orders, pick_hotspots
from sim.fleet import make_couriers
from sim.simulator import run_simulation
from strategies.greedy import Greedy

SEED = 0
SHIFT = 2 * 3600
ORDERS_PER_HOUR = 60
N_COURIERS = 20

city = make_grid_city()
rng = np.random.default_rng(SEED)
hotspots = pick_hotspots(city, 5, rng)
orders = generate_orders(city, hotspots, ORDERS_PER_HOUR, SHIFT, rng)
couriers = make_couriers(city, N_COURIERS, rng)

res = run_simulation(city, couriers, orders, Greedy(), SHIFT)

done = [o for o in res.orders if o.delivered_at is not None]
times = [(o.delivered_at - o.created_at) / 60 for o in done]
idle_pct = [100 * c.idle_seconds / SHIFT for c in res.couriers]

print(f"orders:              {len(res.orders)}")
print(f"delivered:           {len(done)}")
print(f"mean delivery (min): {np.mean(times):.1f}")
print(f"waiting at shift end:{res.waiting_at_shift_end:>4}")
print(f"mean courier idle %: {np.mean(idle_pct):.1f}")
