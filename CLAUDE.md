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
3. Sim modules — numerical realizations of the symbolic math. Six modules,
   68 simulations total, all saving PNGs into `plots/`.

## The sim module contract

Every sim module (`sims.py`, `workon_sims.py`, `todo_sims.py`, `addon_sims.py`,
`connections_sims.py`, `modern_sims.py`) exposes:

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
| Total sims | 68 | sum of `len(REGISTRY)` across 6 sim modules |
| Sim split | 26 + 9 + 4 + 5 + 12 + 12 | sims / workon / todo / addon / connections / modern |

References to these numbers appear in `README.md`, `EXPLAINER.md`,
`run_all_sims.py` docstring, and `tests/test_registry.py` (as lower bounds).
`tests/test_doc_consistency.py` fails the build on drift, so run it after any
count change.
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
- `sketches/` holds design sketches that do not run and are not imported by
  anything. Do not wire them into the tested surface without finishing them
  first — see `sketches/README.md` for the promotion criteria.
- Explainer markdown stays at the repo root. `.fieldlink.json` exports
  `Connections_Explainer.md` by root-relative path as part of the Bridge-repo
  contract, so moving those files breaks the field link.

## Running things

```bash
pip install -r requirements.txt
pytest tests/ -v                       # smoke tests (registry + graph + playground)
python run_all_sims.py --list          # enumerate all 68 sims
python run_all_sims.py --sim lorenz    # run one
python run_all_sims.py                 # run everything (slow; 68 plots, ~100s)
python run_all_sims.py --module modern_sims   # run one level
python physics_playground.py           # interactive REPL-style demo
```

## Compressed claim format (token-minimal AI reader interface)

The repo carries the canonical `.claims` surface:

- `CLAIM_SCHEMA.py` — schema source, verbatim from `JinnZ2/experiments`. Drop-in
  identical across the JinnZ2 ecosystem.
- `CLAIM_TABLE.json` — repo-level lookup (deduped rates / bounds / cond / rel /
  fail / meas).
- `.claims` — pipe-delimited, one claim per registered equation
  (`id|rate|bounds|cond|rel|fail|meas|cyc`).
- `generate_claims.py` — deterministic generator. Re-run after registry
  changes; the `test_regenerator_is_deterministic` test enforces no drift.

`tests/test_claims.py` checks one-claim-per-equation, table integrity,
round-trip parsing, and binary codec via `encode_claim`/`decode_claim`.
The `rate` extractor sanitizes any literal `|` or `,` so the format stays
parseable as the registry grows.

`modern_claims.json` is a separate, hand-written surface covering `modern_sims.py`
(Level 6). Nothing regenerates it. Its 12 entries are *candidate* registry nodes rather
than registered equations, so each carries an `anchor` (the registry equation
it extends) and a `morphism` (the transformation that would reach it).
`tests/test_modern_claims.py` pins it to both registries: one claim per sim in
`modern_sims.REGISTRY`, and every `anchor` resolving against
`EquationRegistry`. Promoting a claim means registering the target equation in
`physics_playground.py` and adding the `anchor → target` edge in `graph.py` —
which also moves the equation/morphism counts above.

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

<!-- clone-refspec-note v1.1 -->
## Cloning and pushing
Shallow clones are single-branch by default.
Before pushing any branch other than the default
branch, run:

    git config remote.origin.fetch '+refs/heads/*:refs/remotes/origin/*'
    git fetch --depth 1

Or clone with: git clone --depth 1 --no-single-branch <url>
Without this, the first push of a new branch
fails the tracking-ref check even when the
commit landed.
<!-- /clone-refspec-note v1.1 -->
