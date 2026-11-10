import numpy as np
import pytest

from sim.city import make_grid_city
from sim.demand import generate_orders, pick_hotspots
from sim.fleet import make_couriers
from sim.metrics import compute_metrics, gini
from sim.simulator import run_simulation
from strategies.greedy import Greedy
from strategies.hungarian import Hungarian

SHIFT = 3600


def scenario(seed=0, per_hour=60, n_couriers=15):
    city = make_grid_city()
    rng = np.random.default_rng(seed)
    hotspots = pick_hotspots(city, 5, rng)
    orders = generate_orders(city, hotspots, per_hour, SHIFT, rng)
    couriers = make_couriers(city, n_couriers, rng)
    return city, couriers, orders


def test_gini_equal_is_zero():
    assert gini([5, 5, 5, 5]) == 0


def test_gini_one_does_everything():
    # for n=4 the maximum possible Gini is (n-1)/n = 0.75
    assert gini([0, 0, 0, 10]) == pytest.approx(0.75)


def test_timestamps_are_in_order():
    city, couriers, orders = scenario()
    res = run_simulation(city, couriers, orders, Greedy(), SHIFT)
    for o in res.orders:
        if o.delivered_at is not None:
            assert o.created_at <= o.assigned_at <= o.picked_up_at <= o.delivered_at


def test_courier_counts_add_up():
    city, couriers, orders = scenario()
    res = run_simulation(city, couriers, orders, Hungarian(), SHIFT)
    m = compute_metrics(res)
    assert sum(c.delivered for c in res.couriers) == m["delivered"]
    assert m["delivered"] + m["undelivered"] == m["orders"]


def test_simulation_is_repeatable():
    city, couriers, orders = scenario(seed=7)
    a = compute_metrics(run_simulation(city, couriers, orders, Greedy(), SHIFT))
    b = compute_metrics(run_simulation(city, couriers, orders, Greedy(), SHIFT))
    assert a == b


def test_simulation_does_not_mutate_inputs():
    city, couriers, orders = scenario()
    run_simulation(city, couriers, orders, Greedy(), SHIFT)
    assert all(o.delivered_at is None for o in orders)


class DoubleBooker:
    """A broken strategy: gives every waiting order to the same courier."""
    name = "broken"

    def assign(self, now, idle, waiting, city):
        return [(idle[0], o) for o in waiting]


def test_invalid_assignment_is_rejected():
    city, couriers, orders = scenario(per_hour=600)   # busy, so >1 order waits
    with pytest.raises(ValueError):
        run_simulation(city, couriers, orders, DoubleBooker(), SHIFT)
