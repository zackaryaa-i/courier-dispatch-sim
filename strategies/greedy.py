"""Greedy: oldest order first, each to the nearest still-free idle courier."""
from sim.city import City
from sim.entities import Courier, Order
from strategies.base import Assignment


class Greedy:
    name = "greedy"

    def assign(
        self, now: float, idle: list[Courier], waiting: list[Order], city: City
    ) -> list[Assignment]:
        free = list(idle)
        result: list[Assignment] = []
        for order in sorted(waiting, key=lambda o: o.created_at):
            if not free:
                break
            best = min(free, key=lambda c: (city.travel_time(c.node, order.pickup), c.id))
            result.append((best, order))
            free.remove(best)
        return result
