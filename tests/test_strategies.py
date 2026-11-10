import numpy as np

from sim.city import make_grid_city
from sim.entities import Order
from sim.fleet import make_couriers
from strategies.greedy import Greedy, NearestOrderGreedy
from strategies.hungarian import Hungarian


def total_cost(city, assignments):
    return sum(city.travel_time(c.node, o.pickup) for c, o in assignments)


def test_hungarian_never_beaten_in_a_single_round():
    city = make_grid_city()
    for seed in range(50):
        rng = np.random.default_rng(seed)
        n_couriers, n_orders = rng.integers(1, 8, size=2)
        couriers = make_couriers(city, int(n_couriers), rng)
        orders = [Order(id=i, created_at=0.0, pickup=int(rng.choice(city.nodes)),
                        dropoff=int(rng.choice(city.nodes))) for i in range(n_orders)]
        h = Hungarian().assign(0, couriers, orders, city)
        assert len(h) == min(n_couriers, n_orders)
        for other in (Greedy(), NearestOrderGreedy()):
            o = other.assign(0, couriers, orders, city)
            assert total_cost(city, h) <= total_cost(city, o) + 1e-9
