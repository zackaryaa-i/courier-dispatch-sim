"""Real street networks from OpenStreetMap, cached to disk."""
from pathlib import Path

import networkx as nx
import osmnx as ox

from sim.city import City

PLACES = {  # name -> (lat, lon) of the centre point
    "dubai_marina": (25.0805, 55.1403),
    "istanbul_kadikoy": (40.9903, 29.0290),
}
CACHE = Path("cache")


def load_real_city(name: str, radius_m: int = 1500, speed_mps: float = 5.0) -> City:
    path = CACHE / f"{name}_{radius_m}m.graphml"
    if path.exists():
        g = ox.load_graphml(path)
    else:
        print(f"downloading {name} from OpenStreetMap (first time only)...")
        g = ox.graph_from_point(PLACES[name], dist=radius_m, network_type="drive")
        g = ox.project_graph(g)                               # lat/lon -> metres
        biggest = max(nx.strongly_connected_components(g), key=len)
        g = g.subgraph(biggest).copy()
        CACHE.mkdir(exist_ok=True)
        ox.save_graphml(g, path)
    g = nx.convert_node_labels_to_integers(g)
    return City(g, speed_mps)
