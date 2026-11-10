"""Courier fleet setup."""
import numpy as np

from sim.city import City
from sim.entities import Courier


def make_couriers(city: City, n: int, rng: np.random.Generator) -> list[Courier]:
    """n idle couriers at random junctions."""
    starts = rng.choice(city.nodes, size=n, replace=True)
    return [Courier(id=i, node=int(node)) for i, node in enumerate(starts)]
