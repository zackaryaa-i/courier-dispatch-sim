"""Orders and couriers: plain data holders, no simulation logic."""
from dataclasses import dataclass
from enum import Enum


class Status(Enum):
    IDLE = "idle"
    TO_PICKUP = "to_pickup"
    TO_DROPOFF = "to_dropoff"


@dataclass
class Order:
    id: int
    created_at: float          # seconds since shift start
    pickup: int                # restaurant node
    dropoff: int               # home node
    courier_id: int | None = None
    assigned_at: float | None = None
    picked_up_at: float | None = None
    delivered_at: float | None = None


@dataclass
class Courier:
    id: int
    node: int                  # where the courier is (or last was)
    status: Status = Status.IDLE
    order: Order | None = None
    leg_ends_at: float = 0.0   # time the current trip leg finishes
    idle_seconds: float = 0.0
    delivered: int = 0
