from pathlib import Path

import networkx as nx
import numpy as np
import pytest

from sim.demand import generate_orders, pick_hotspots
from sim.fleet import make_couriers
from sim.simulator import run_simulation
from strategies.hungarian import Hungarian

CACHED = Path("cache/dubai_marina_1500m.graphml")
pytestmark = pytest.mark.skipif(not CACHED.exists(), reason="Dubai map not downloaded")


@pytest.fixture(scope="module")
def city():
    from sim.real_city import load_real_city
    return load_real_city("dubai_marina")


def test_every_junction_can_reach_every_other(city):
    assert nx.is_strongly_connected(city.graph)


def test_travel_times_finite_and_non_negative(city):
    rng = np.random.default_rng(0)
    for a, b in rng.choice(city.nodes, size=(200, 2)):
        t = city.travel_time(int(a), int(b))
        assert 0 <= t < float("inf")


def test_short_overloaded_shift_runs_cleanly(city):
    rng = np.random.default_rng(0)
    hotspots = pick_hotspots(city, 5, rng)
    orders = generate_orders(city, hotspots, 150, 1800, rng)
    couriers = make_couriers(city, 20, rng)
    res = run_simulation(city, couriers, orders, Hungarian(), 1800)
    for o in res.orders:
        if o.delivered_at is not None:
            assert o.created_at <= o.assigned_at <= o.picked_up_at <= o.delivered_at
