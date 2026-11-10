"""Batching: hold orders, then run optimal matching every `interval` seconds."""
from sim.city import City
from sim.entities import Courier, Order
from strategies.base import Assignment
from strategies.hungarian import Hungarian


class BatchedHungarian:
    def __init__(self, interval: int):
        self.interval = interval
        self.name = f"batch_{interval}s"
        self._matcher = Hungarian()

    def assign(
        self, now: float, idle: list[Courier], waiting: list[Order], city: City
    ) -> list[Assignment]:
        if now % self.interval != 0:
            return []                      # not a batch moment: let orders wait
        return self._matcher.assign(now, idle, waiting, city)
