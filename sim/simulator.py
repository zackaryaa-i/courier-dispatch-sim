"""Time-step simulation of one courier shift."""
import copy
from dataclasses import dataclass

from sim.city import City
from sim.entities import Courier, Order, Status
from strategies.base import Assignment, Strategy


@dataclass
class SimResult:
    orders: list[Order]
    couriers: list[Courier]
    shift_seconds: float
    waiting_at_shift_end: int


def _advance_courier(c: Courier, now: float, city: City) -> None:
    """Finish any trip legs that have ended by `now`."""
    while c.status is not Status.IDLE and c.leg_ends_at <= now:
        order = c.order
        if c.status is Status.TO_PICKUP:
            c.node = order.pickup
            order.picked_up_at = c.leg_ends_at
            c.status = Status.TO_DROPOFF
            c.leg_ends_at += city.travel_time(order.pickup, order.dropoff)
        else:
            c.node = order.dropoff
            order.delivered_at = c.leg_ends_at
            c.delivered += 1
            c.status = Status.IDLE
            c.order = None


def _apply_assignments(
    assignments: list[Assignment], now: float, waiting: list[Order], city: City
) -> None:
    """Check the strategy's choices are legal, then start each courier moving."""
    waiting_ids = {o.id for o in waiting}
    used_couriers, used_orders = set(), set()
    for c, o in assignments:
        if c.status is not Status.IDLE or c.id in used_couriers:
            raise ValueError(f"courier {c.id} is not free")
        if o.id not in waiting_ids or o.id in used_orders:
            raise ValueError(f"order {o.id} is not waiting")
        used_couriers.add(c.id)
        used_orders.add(o.id)

        o.courier_id = c.id
        o.assigned_at = now
        c.order = o
        c.status = Status.TO_PICKUP
        c.leg_ends_at = now + city.travel_time(c.node, o.pickup)
    waiting[:] = [o for o in waiting if o.id not in used_orders]


def run_simulation(
    city: City,
    couriers: list[Courier],
    orders: list[Order],
    strategy: Strategy,
    shift_seconds: float,
    dt: float = 10.0,
    drain_seconds: float = 3600.0,
) -> SimResult:
    couriers = copy.deepcopy(couriers)   # never mutate the caller's objects
    orders = copy.deepcopy(orders)
    waiting: list[Order] = []
    next_order = 0
    waiting_at_shift_end = 0
    t = 0.0

    while t <= shift_seconds + drain_seconds:
        # 1. couriers finish trip legs
        for c in couriers:
            _advance_courier(c, t, city)

        # 2. new orders arrive
        while next_order < len(orders) and orders[next_order].created_at <= t:
            waiting.append(orders[next_order])
            next_order += 1

        # 3. strategy assigns
        idle = [c for c in couriers if c.status is Status.IDLE]
        if idle and waiting:
            chosen = strategy.assign(t, idle, list(waiting), city)
            _apply_assignments(chosen, t, waiting, city)

        # 4. bookkeeping (idle time only counts during the shift)
        if t < shift_seconds:
            for c in couriers:
                if c.status is Status.IDLE:
                    c.idle_seconds += dt
        if t == shift_seconds:
            waiting_at_shift_end = len(waiting)

        # 5. stop early once the shift is over and everything is delivered
        if t >= shift_seconds and all(o.delivered_at is not None for o in orders):
            break
        t += dt

    return SimResult(orders, couriers, shift_seconds, waiting_at_shift_end)
