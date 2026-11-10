"""Turn a finished simulation into a flat dict of numbers."""
import numpy as np

from sim.simulator import SimResult


def gini(values: list[float]) -> float:
    """0 = perfectly equal, towards 1 = one person has everything."""
    x = np.sort(np.asarray(values, dtype=float))
    n, total = len(x), x.sum()
    if n == 0 or total == 0:
        return 0.0
    ranks = np.arange(1, n + 1)
    return float(2 * np.sum(ranks * x) / (n * total) - (n + 1) / n)


def compute_metrics(res: SimResult) -> dict[str, float]:
    done = [o for o in res.orders if o.delivered_at is not None]
    delivery = np.array([o.delivered_at - o.created_at for o in done]) / 60
    to_assign = np.array([o.assigned_at - o.created_at for o in done]) / 60
    per_courier = [c.delivered for c in res.couriers]
    idle_pct = [100 * c.idle_seconds / res.shift_seconds for c in res.couriers]

    return {
        "orders": len(res.orders),
        "delivered": len(done),
        "undelivered": len(res.orders) - len(done),
        "waiting_at_shift_end": res.waiting_at_shift_end,
        "mean_delivery_min": float(delivery.mean()),
        "p90_delivery_min": float(np.percentile(delivery, 90)),
        "max_delivery_min": float(delivery.max()),
        "mean_wait_to_assign_min": float(to_assign.mean()),
        "courier_idle_pct": float(np.mean(idle_pct)),
        "orders_per_courier_mean": float(np.mean(per_courier)),
        "orders_per_courier_min": int(np.min(per_courier)),
        "orders_per_courier_max": int(np.max(per_courier)),
        "orders_per_courier_gini": gini(per_courier),
    }
