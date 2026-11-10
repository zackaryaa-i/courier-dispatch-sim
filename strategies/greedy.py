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


class NearestOrderGreedy:
    """Control: each free courier (by id) takes the nearest waiting order.

    Same one-at-a-time logic as Greedy, but the courier picks the order
    rather than the order picking the courier. Used to test whether
    Hungarian's win comes from matching or just from serving nearby orders.
    """
    name = "greedy_nearest"

    def assign(
        self, now: float, idle: list[Courier], waiting: list[Order], city: City
    ) -> list[Assignment]:
        left = list(waiting)
        result: list[Assignment] = []
        for courier in sorted(idle, key=lambda c: c.id):
            if not left:
                break
            best = min(left, key=lambda o: (city.travel_time(courier.node, o.pickup), o.id))
            result.append((courier, best))
            left.remove(best)
        return result
