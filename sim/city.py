"""City model: a street graph plus cached travel-time lookups."""
import networkx as nx


class City:
    def __init__(self, graph: nx.Graph, speed_mps: float):
        self.graph = graph
        self.speed_mps = speed_mps
        self.nodes = list(graph.nodes)
        self._dist_cache: dict[int, dict[int, float]] = {}

    def distances_from(self, source: int) -> dict[int, float]:
        """Shortest road distance (metres) from source to every node, cached."""
        if source not in self._dist_cache:
            self._dist_cache[source] = nx.single_source_dijkstra_path_length(
                self.graph, source, weight="length"
            )
        return self._dist_cache[source]

    def distance(self, a: int, b: int) -> float:
        return self.distances_from(a)[b]

    def travel_time(self, a: int, b: int) -> float:
        """Seconds to drive from a to b."""
        return self.distance(a, b) / self.speed_mps


def make_grid_city(size: int = 20, block_m: float = 200.0, speed_mps: float = 5.0) -> City:
    """A size x size grid of streets, block_m metres between junctions."""
    g = nx.grid_2d_graph(size, size)
    g = nx.convert_node_labels_to_integers(g, label_attribute="grid_xy")
    for u, v in g.edges:
        g.edges[u, v]["length"] = block_m
    for n in g.nodes:
        gx, gy = g.nodes[n]["grid_xy"]
        g.nodes[n]["x"] = gx * block_m
        g.nodes[n]["y"] = gy * block_m
    return City(g, speed_mps)
