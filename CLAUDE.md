# CLAUDE.md

Guide for Claude (or any agent) working in this repo. Keep it short; read the full
files when you need detail.

## What this repo is

A SymPy + NetworkX "physics playground" that treats physical equations as nodes
in a single morphism graph. You can walk from classical to quantum to chaotic to
biological regimes via continuous mathematical transformations.

This is the **physics layer** of a two-repo system. The companion **silicon
compilation layer** lives at
<https://github.com/JinnZ2/Geometric-to-Binary-Computational-Bridge>.
The binding contract is the `SiliconState` object (see `.fieldlink.json`).

## Architecture

Three pillars:

1. `physics_playground.py` — `EquationRegistry` (90 equations across 23 domains),
   `PhysicsEquation` dataclass, `PhysicsDomain` enum, `PropellerTransform`
   (classical → Fokker-Planck → Madelung → Schrödinger), and the top-level
   `PhysicsPlayground` facade.
2. `graph.py` — `EquationGraph` / `build_morphism_graph()`. 112 weighted directed
   edges. Weights combine dimensional inconsistency, constraint violation, and
   domain distance. The graph is **weakly connected** (enforced by tests).
3. Sim modules — numerical realizations of the symbolic math. Five modules,
   56 simulations total, all saving PNGs into `plots/`.

## The sim module contract

Every sim module (`sims.py`, `workon_sims.py`, `todo_sims.py`, `addon_sims.py`,
`connections_sims.py`) exposes:

- `REGISTRY: dict[str, {"fn": Callable, "title": str, ...}]` — populated via a
  `@sim(name, title)` decorator at import time.
- `run_all()` — iterates REGISTRY and runs every sim. **Required** for
  `run_all_sims.py --module <name>` to work. If you add a new sim module,
  add both a `REGISTRY` and a `run_all()`.
- `PLOT_DIR` — resolved relative to the module file, not CWD.

`run_all_sims.py` is the unified entry point. Its `MODULES` list must include
every sim module; `load_registry()` iterates it.

## Counts that should stay consistent

Drift between these numbers and the code has bitten this repo before. If you
change equations, sims, or edges, update everything in this list:

| Claim | Value | Source of truth |
|---|---|---|
| Equations | 90 | `EquationRegistry._equations` |
| Domains | 23 | `PhysicsDomain` enum values actually used |
| Morphism edges | 112 | `build_morphism_graph().G.number_of_edges()` |
| Total sims | 56 | sum of `len(REGISTRY)` across 5 sim modules |
| Sim split | 26 + 9 + 4 + 5 + 12 | sims / workon / todo / addon / connections |

References to these numbers appear in `README.md`, `EXPLAINER.md`,
`run_all_sims.py` docstring, and `tests/test_registry.py` (as lower bounds).
Prefer lower-bound assertions in tests (`>= 90`, `>= 110`) over exact equality
so adding equations doesn't break CI unnecessarily.

## Conventions

- Matplotlib uses the `Agg` backend in every sim module (no display required).
- Plots are written to `plots/` with the sim `name` as filename.
- New equations: add to `EquationRegistry._register_all()` in
  `physics_playground.py`, then add at least one incoming and one outgoing
  morphism edge in `graph.py` (the `test_no_isolated_nodes` test enforces this).
- New morphisms: ensure dimensional/constraint weights are non-negative
  (`test_edge_weights_are_non_negative`).

## Running things

```bash
pip install -r requirements.txt
pytest tests/ -v                       # smoke tests (registry + graph + playground)
python run_all_sims.py --list          # enumerate all 56 sims
python run_all_sims.py --sim lorenz    # run one
python run_all_sims.py                 # run everything (slow; ~54 plots)
python physics_playground.py           # interactive REPL-style demo
```

## Field link to the Bridge repo

- `.fieldlink.json` — machine-readable manifest (v1.2 schema, matches the Bridge
  repo's format).
- `connections_sims.py` + `Connections_Explainer.md` — the silicon phase-space
  model: 4D behavioral manifold `S = (n, d, ℓ, κ)`, softmax regime blending,
  rigorous geometry→silicon mapping, and feedback closure.
- The `SiliconState` vector is the hand-off: this repo produces it from a
  geometry field; the Bridge repo consumes it to emit binary and modify the
  substrate.

When touching the silicon layer, keep the two repos in sync — the Bridge repo's
`Silicon/Connections.md` is the canonical spec.
