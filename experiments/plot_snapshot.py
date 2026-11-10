"""Map frame: couriers and waiting orders at one moment of an overloaded shift.

Usage: python -m experiments.plot_snapshot [grid|dubai_marina|istanbul_kadikoy] [orders_per_hour]
"""
import sys

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import networkx as nx
import numpy as np

from sim.city import City, make_grid_city
from sim.demand import generate_orders, pick_hotspots
from sim.entities import Courier, Status
from sim.fleet import make_couriers
from sim.simulator import run_simulation
from strategies.hungarian import Hungarian

SEED, N_COURIERS = 0, 20
SNAPSHOT_AT = 90 * 60            # 90 minutes into the shift
INK, MUTED, STREET = "#1f1f1e", "#6b6a64", "#e5e4df"
COLOURS = {Status.IDLE: "#2a78d6", Status.TO_PICKUP: "#eb6834", Status.TO_DROPOFF: "#1baf7a"}
LABELS = {Status.IDLE: "Courier: idle", Status.TO_PICKUP: "Courier: to restaurant",
          Status.TO_DROPOFF: "Courier: delivering"}


def positions(city: City) -> dict[int, np.ndarray]:
    """Node -> (x, y) in km, shifted so the map starts at (0, 0)."""
    xs = np.array([city.graph.nodes[n]["x"] for n in city.nodes])
    ys = np.array([city.graph.nodes[n]["y"] for n in city.nodes])
    return {n: np.array([(x - xs.min()), (y - ys.min())]) / 1000
            for n, x, y in zip(city.nodes, xs, ys)}


def edge_length(city: City, a: int, b: int) -> float:
    """Shortest parallel edge a->b (osmnx graphs can have several)."""
    data = city.graph[a][b]
    if city.graph.is_multigraph():
        return min(d["length"] for d in data.values())
    return data["length"]


def courier_route(city: City, pos: dict, c: Courier, now: float) -> list[np.ndarray]:
    """Current position followed by the street corners still to drive through."""
    if c.status is Status.IDLE:
        return [pos[c.node]]
    target = c.order.pickup if c.status is Status.TO_PICKUP else c.order.dropoff
    duration = city.travel_time(c.node, target)
    if duration == 0:
        return [pos[target]]
    frac = min(1.0, max(0.0, 1 - (c.leg_ends_at - now) / duration))
    walk = frac * city.distance(c.node, target)
    path = nx.shortest_path(city.graph, c.node, target, weight="length")
    for i, (a, b) in enumerate(zip(path, path[1:])):
        length = edge_length(city, a, b)
        if walk <= length:
            here = pos[a] + (walk / length) * (pos[b] - pos[a])
            return [here] + [pos[n] for n in path[i + 1:]]
        walk -= length
    return [pos[target]]


def main() -> None:
    name = sys.argv[1] if len(sys.argv) > 1 else "dubai_marina"
    per_hour = int(sys.argv[2]) if len(sys.argv) > 2 else (120 if name == "grid" else 150)
    if name == "grid":
        city, title_city = make_grid_city(), "grid city"
    else:
        from sim.real_city import load_real_city
        city, title_city = load_real_city(name), {"istanbul_kadikoy": "Istanbul Kadıköy"}.get(name, name.replace("_", " ").title())

    rng = np.random.default_rng(SEED)
    hotspots = pick_hotspots(city, 5, rng)
    orders = generate_orders(city, hotspots, per_hour, 2 * 3600, rng)
    couriers = make_couriers(city, N_COURIERS, rng)
    res = run_simulation(city, couriers, orders, Hungarian(), SNAPSHOT_AT, drain_seconds=0)
    waiting = [o for o in res.orders if o.created_at <= SNAPSHOT_AT and o.courier_id is None]
    pos = positions(city)

    fig, ax = plt.subplots(figsize=(7, 7.6), dpi=200)
    for u, v in city.graph.edges():
        ax.plot([pos[u][0], pos[v][0]], [pos[u][1], pos[v][1]], color=STREET, lw=1, zorder=1)

    for o in waiting:
        ax.scatter(*pos[o.dropoff], s=45, facecolor="none", edgecolor="#eda100", lw=1.8, zorder=3)
    for c in res.couriers:
        route = np.array(courier_route(city, pos, c, SNAPSHOT_AT))
        if len(route) > 1:
            ax.plot(route[:, 0], route[:, 1], color=COLOURS[c.status], lw=1.5, ls=":", zorder=2)
        ax.scatter(*route[0], s=70, color=COLOURS[c.status], edgecolor="white", lw=1.5, zorder=4)
    for h in hotspots:
        ax.scatter(*pos[h], s=110, marker="s", color=INK, edgecolor="white", lw=1.5, zorder=5)

    handles = [plt.Line2D([], [], marker="o", ls="", ms=8, color=COLOURS[s], label=LABELS[s])
               for s in COLOURS]
    handles += [
        plt.Line2D([], [], marker="o", ls="", ms=7, markerfacecolor="none",
                   markeredgecolor="#eda100", markeredgewidth=1.8,
                   label=f"Waiting order, at its home ({len(waiting)})"),
        plt.Line2D([], [], marker="s", ls="", ms=9, color=INK, label="Restaurant hotspot"),
    ]
    ax.legend(handles=handles, loc="upper center", bbox_to_anchor=(0.5, -0.03),
              ncol=3, frameon=False, fontsize=8, labelcolor=INK)
    ax.set_title(f"Minute {SNAPSHOT_AT // 60} of an overloaded shift, {title_city}\n"
                 f"{per_hour} orders/h, {N_COURIERS} couriers, Hungarian matching.\n"
                 f"Axes in km; dotted = remaining route.",
                 loc="left", color=INK, fontsize=10)
    ax.set_aspect("equal")
    ax.tick_params(colors=MUTED)
    for side in ax.spines.values():
        side.set_visible(False)

    out = f"results/snapshot_{name}.png"
    fig.tight_layout()
    fig.savefig(out)
    print(f"saved {out}: {len(waiting)} waiting orders, "
          f"{sum(c.status is Status.IDLE for c in res.couriers)} idle couriers")


if __name__ == "__main__":
    main()
