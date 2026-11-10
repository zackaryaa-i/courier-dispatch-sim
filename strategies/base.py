"""The common interface every dispatch strategy follows."""
from typing import Protocol

from sim.city import City
from sim.entities import Courier, Order

Assignment = tuple[Courier, Order]


class Strategy(Protocol):
    name: str

    def assign(
        self, now: float, idle: list[Courier], waiting: list[Order], city: City
    ) -> list[Assignment]:
        """Decide which idle courier takes which waiting order (may be none)."""
        ...
