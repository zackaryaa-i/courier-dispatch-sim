"""Order generation: Poisson arrivals, pickups at restaurant hotspots."""
import numpy as np

from sim.city import City
from sim.entities import Order


def pick_hotspots(city: City, n: int, rng: np.random.Generator) -> list[int]:
    """Choose n distinct junctions to act as restaurant clusters."""
    return [int(x) for x in rng.choice(city.nodes, size=n, replace=False)]


def generate_orders(
    city: City,
    hotspots: list[int],
    orders_per_hour: float,
    shift_seconds: float,
    rng: np.random.Generator,
) -> list[Order]:
    """All orders for one shift, in time order."""
    rate = orders_per_hour / 3600.0          # orders per second
    orders: list[Order] = []
    t = 0.0
    while True:
        t += rng.exponential(1.0 / rate)     # gap until the next order
        if t >= shift_seconds:
            break
        pickup = int(rng.choice(hotspots))
        dropoff = int(rng.choice(city.nodes))
        while dropoff == pickup:
            dropoff = int(rng.choice(city.nodes))
        orders.append(Order(id=len(orders), created_at=t, pickup=pickup, dropoff=dropoff))
    return orders
