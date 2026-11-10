"""Optimal one-round matching: minimise total courier-to-pickup time."""
import numpy as np
from scipy.optimize import linear_sum_assignment

from sim.city import City
from sim.entities import Courier, Order
from strategies.base import Assignment


class Hungarian:
    name = "hungarian"

    def assign(
        self, now: float, idle: list[Courier], waiting: list[Order], city: City
    ) -> list[Assignment]:
        cost = np.array(
            [[city.travel_time(c.node, o.pickup) for o in waiting] for c in idle]
        )
        rows, cols = linear_sum_assignment(cost)
        return [(idle[r], waiting[c]) for r, c in zip(rows, cols)]
