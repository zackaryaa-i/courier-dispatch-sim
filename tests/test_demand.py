import numpy as np

from sim.city import make_grid_city
from sim.demand import generate_orders, pick_hotspots
from sim.entities import Status
from sim.fleet import make_couriers

SHIFT = 2 * 3600


def make_orders(seed, per_hour=120):
    city = make_grid_city()
    rng = np.random.default_rng(seed)
    hotspots = pick_hotspots(city, 5, rng)
    return hotspots, generate_orders(city, hotspots, per_hour, SHIFT, rng)


def test_same_seed_gives_same_orders():
    assert make_orders(42)[1] == make_orders(42)[1]


def test_different_seed_gives_different_orders():
    assert make_orders(1)[1] != make_orders(2)[1]


def test_orders_are_in_time_order_within_shift():
    _, orders = make_orders(0)
    times = [o.created_at for o in orders]
    assert times == sorted(times)
    assert 0 < times[0] and times[-1] < SHIFT


def test_pickups_at_hotspots_and_dropoff_differs():
    hotspots, orders = make_orders(0)
    for o in orders:
        assert o.pickup in hotspots
        assert o.dropoff != o.pickup


def test_order_count_matches_rate():
    # 120/h for 2h -> expect 240; Poisson sd ~15.5, so 180-300 is very safe
    _, orders = make_orders(0, per_hour=120)
    assert 180 <= len(orders) <= 300


def test_couriers_start_idle():
    city = make_grid_city()
    couriers = make_couriers(city, 10, np.random.default_rng(0))
    assert len(couriers) == 10
    assert all(c.status is Status.IDLE for c in couriers)
