"""Map frame: couriers and waiting orders at one moment of a rush-hour shift."""
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

SEED, ORDERS_PER_HOUR, N_COURIERS = 0, 120, 20
SNAPSHOT_AT = 90 * 60            # 90 minutes into the shift
OUT = "results/snapshot.png"
INK, MUTED, STREET = "#1f1f1e", "#6b6a64", "#e5e4df"
COLOURS = {Status.IDLE: "#2a78d6", Status.TO_PICKUP: "#eb6834", Status.TO_DROPOFF: "#1baf7a"}
LABELS = {Status.IDLE: "Courier: idle", Status.TO_PICKUP: "Courier: to restaurant",
          Status.TO_DROPOFF: "Courier: delivering"}


def node_xy(city: City, n: int) -> np.ndarray:
    return np.array([city.graph.nodes[n]["x"], city.graph.nodes[n]["y"]]) / 1000  # km


def courier_route(city: City, c: Courier, now: float) -> list[np.ndarray]:
    """Current position followed by the street corners still to drive through."""
    if c.status is Status.IDLE:
        return [node_xy(city, c.node)]
    target = c.order.pickup if c.status is Status.TO_PICKUP else c.order.dropoff
    duration = city.travel_time(c.node, target)
    if duration == 0:
        return [node_xy(city, target)]
    frac = min(1.0, max(0.0, 1 - (c.leg_ends_at - now) / duration))
    walk = frac * city.distance(c.node, target)
    path = nx.shortest_path(city.graph, c.node, target, weight="length")
    for i, (a, b) in enumerate(zip(path, path[1:])):
        length = city.graph.edges[a, b]["length"]
        if walk <= length:
            pos = node_xy(city, a) + (walk / length) * (node_xy(city, b) - node_xy(city, a))
            return [pos] + [node_xy(city, n) for n in path[i + 1:]]
        walk -= length
    return [node_xy(city, target)]


def main() -> None:
    city = make_grid_city()
    rng = np.random.default_rng(SEED)
    hotspots = pick_hotspots(city, 5, rng)
    orders = generate_orders(city, hotspots, ORDERS_PER_HOUR, 2 * 3600, rng)
    couriers = make_couriers(city, N_COURIERS, rng)

    # A "shift" ending at the snapshot time, with no drain, freezes the state there.
    res = run_simulation(city, couriers, orders, Hungarian(), SNAPSHOT_AT, drain_seconds=0)
    waiting = [o for o in res.orders if o.created_at <= SNAPSHOT_AT and o.courier_id is None]

    fig, ax = plt.subplots(figsize=(7, 7.6), dpi=200)
    for u, v in city.graph.edges:
        (x1, y1), (x2, y2) = node_xy(city, u), node_xy(city, v)
        ax.plot([x1, x2], [y1, y2], color=STREET, lw=1, zorder=1)

    for o in waiting:
        ax.scatter(*node_xy(city, o.dropoff), s=45, facecolor="none",
                   edgecolor="#eda100", lw=1.8, zorder=3)

    for c in res.couriers:
        route = np.array(courier_route(city, c, SNAPSHOT_AT))
        if len(route) > 1:
            ax.plot(route[:, 0], route[:, 1], color=COLOURS[c.status], lw=1.5,
                    ls=":", zorder=2)
        ax.scatter(*route[0], s=70, color=COLOURS[c.status], edgecolor="white", lw=1.5, zorder=4)

    for h in hotspots:
        ax.scatter(*node_xy(city, h), s=110, marker="s", color=INK, edgecolor="white", lw=1.5, zorder=5)

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
    ax.set_title(f"Minute {SNAPSHOT_AT // 60} of a rush-hour shift\n"
                 f"{ORDERS_PER_HOUR} orders/h, {N_COURIERS} couriers, Hungarian matching. "
                 f"Axes in km; dotted = remaining route.",
                 loc="left", color=INK, fontsize=10)
    ax.set_aspect("equal")
    ax.tick_params(colors=MUTED)
    for side in ax.spines.values():
        side.set_visible(False)

    fig.tight_layout()
    fig.savefig(OUT)
    print(f"saved {OUT}: {len(waiting)} waiting orders, "
          f"{sum(c.status is Status.IDLE for c in res.couriers)} idle couriers")


if __name__ == "__main__":
    main()
