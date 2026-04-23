"""
run_all_sims.py
Unified entry point for all simulations in the geometric-to-binary repo.

Runs all 44 simulations across the four sim modules and saves every plot
to the plots/ directory.

Usage
-----
    python run_all_sims.py              # run all 44 simulations
    python run_all_sims.py --list       # list all available simulations
    python run_all_sims.py --module sims            # run one module
    python run_all_sims.py --sim lorenz             # run one simulation by name
    python run_all_sims.py --module workon_sims     # run WorkOn module only

Modules
-------
    sims           — 26 sims: core physics domains (classical → biology)
    workon_sims    —  9 sims: Madelung / Ricci flow / Liouville string theory
    todo_sims      —  4 sims: Lorenz-PDE isomorphism / unified action regimes
    addon_sims     —  5 sims: 4D phase diagram / DeWitt metric / entanglement
"""

import argparse
import importlib
import sys
import os
import time

# ── Sim modules in conceptual order ──────────────────────────────────────────
MODULES = [
    ("sims",        "Core physics domain simulations (26)"),
    ("workon_sims", "Madelung → Ricci flow → Liouville string theory (9)"),
    ("todo_sims",   "Lorenz-PDE isomorphism / unified action regimes (4)"),
    ("addon_sims",  "4D phase diagram / DeWitt metric / entanglement (5)"),
]


def load_registry() -> dict:
    """Load all sim registries from all modules."""
    registry = {}
    for mod_name, _ in MODULES:
        mod = importlib.import_module(mod_name)
        for sim_name, meta in mod.REGISTRY.items():
            registry[sim_name] = {"module": mod_name, **meta}
    return registry


def run_all(registry: dict):
    total = len(registry)
    print(f"\n{'='*65}")
    print(f"  geometric-to-binary  |  Running all {total} simulations")
    print(f"  Output directory: plots/")
    print(f"{'='*65}\n")

    t0 = time.time()
    passed = 0
    failed = []

    for i, (name, meta) in enumerate(registry.items(), 1):
        print(f"[{i:02d}/{total}] {name}  ({meta['module']})")
        print(f"       {meta['title']}")
        try:
            meta["fn"]()
            passed += 1
        except Exception as exc:
            print(f"  *** FAILED: {exc}")
            failed.append((name, str(exc)))

    elapsed = time.time() - t0
    print(f"\n{'='*65}")
    print(f"  Completed {passed}/{total} simulations in {elapsed:.1f}s")
    if failed:
        print(f"  Failed ({len(failed)}):")
        for name, err in failed:
            print(f"    - {name}: {err}")
    plot_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "plots")
    plots = sorted(os.listdir(plot_dir))
    print(f"  Plots saved: {len(plots)} files in plots/")
    print(f"{'='*65}\n")


def list_all(registry: dict):
    print(f"\n{'Module':<18} {'Name':<35} Title")
    print("-" * 90)
    current_mod = None
    for name, meta in registry.items():
        if meta["module"] != current_mod:
            current_mod = meta["module"]
            print()
        print(f"{meta['module']:<18} {name:<35} {meta['title']}")
    print()


def run_module(mod_name: str):
    mod = importlib.import_module(mod_name)
    mod.run_all()


def run_sim(name: str, registry: dict):
    if name not in registry:
        print(f"Unknown simulation '{name}'. Use --list to see all.")
        sys.exit(1)
    meta = registry[name]
    print(f"Running [{name}] from {meta['module']}")
    print(f"  {meta['title']}")
    meta["fn"]()


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Run geometric-to-binary simulations",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=__doc__,
    )
    parser.add_argument("--list",   action="store_true",
                        help="List all available simulations")
    parser.add_argument("--module", type=str, default=None,
                        choices=[m for m, _ in MODULES],
                        help="Run all simulations in one module")
    parser.add_argument("--sim",    type=str, default=None,
                        help="Run a single simulation by name")
    args = parser.parse_args()

    # Add repo dir to path so imports work from any CWD
    sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

    registry = load_registry()

    if args.list:
        list_all(registry)
    elif args.module:
        run_module(args.module)
    elif args.sim:
        run_sim(args.sim, registry)
    else:
        run_all(registry)
