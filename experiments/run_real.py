"""Rerun the full experiment on a real street network."""
import sys

from experiments.run_all import DEMAND, run_experiment
from sim.real_city import load_real_city

name = sys.argv[1] if len(sys.argv) > 1 else "dubai_marina"
demand = {**DEMAND, "peak": 150}      # real city has more capacity, so add an overload level
run_experiment(load_real_city(name), demand, f"results/results_{name}.csv")
