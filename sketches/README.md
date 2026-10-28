# sketches/

Design sketches. **Nothing in here is imported by the tested surface of the
repo**, and nothing in here is expected to run end-to-end — these are notes in
Python syntax: function signatures, docstrings, and control flow written down
before (or instead of) the working implementation.

They live here rather than at the repo root so that the root stays a list of
things that actually run: the three pillars, the six sim modules, the claims
surface, and the field-link manifest.

---

## `geometry_bridge/`

Four files sketching the loop **geometry → physics → silicon → geometry**:

| File | Sketches |
|---|---|
| `geometry_to_physics.py` | mapping geometric stack layers onto `PhysicsDomain` |
| `distortion_to_morphism.py` | mapping a distortion signal onto a named morphism |
| `healing_as_morphism.py` | applying a morphism to repair a distorted geometry |
| `silicon_closure.py` | closing the loop back from `SiliconState` to geometry |

**These are superseded.** The working implementation of all four is
[`geometry_to_physics_bridge.py`](../geometry_to_physics_bridge.py) at the repo
root, which imports cleanly (falling back to stubs when the external
`geometric_stack` module is absent) and implements
`map_distortion_to_morphism`, `_geometry_to_physics`, the healing pass, and the
silicon closure loop as real methods. They are kept for the design intent the
docstrings carry, which the implementation does not restate.

`geometry_to_physics.py` also imports `geometric_stack`, which lives in a
different repository — it will not import here.

## `falsifiable_experiment/`

A four-file sketch of a falsifiable experiment comparing **linear sequence
processing against geometric (stack-based) processing**: does geometric
processing detect and correct a distortion faster, and where is the phase
boundary between the two regimes?

| File | Sketches |
|---|---|
| `line_vs_geometry.py` | `LinearSystem` / `GeometricSystem` and the distortion-detection task |
| `phase_boundary.py` | scanning information density to find the linear/geometric crossover |
| `evaluate_assumptions.py` | scoring the mapping, protocol, process and assumption choices |
| `run_experiment.py` | the 100-trial timing harness over both systems |

Incomplete as written: `run_experiment.py` calls `generate_data_with_distortion`
and `GeometricSystem`, neither of which is defined or imported in this
directory. Wiring these four together into a runnable experiment is open work.

---

## Promoting a sketch

A sketch graduates out of this directory when it (a) imports and runs, (b) has
a test under `tests/`, and (c) is reachable from something a reader would
find — a sim module's `REGISTRY`, or a section in `README.md`. If it produces
plots, follow the sim module contract in [`CLAUDE.md`](../CLAUDE.md) so
`run_all_sims.py` can drive it.

## `light_exchange_switch.md`

Note 2026-10-28: a one-file sketch of the two axes (`J_inter`, `C`) a
light-switched magnetic topological material would add to `SiliconState`,
occasioned by an ACS Nano 2026 prediction for MnBi2Te4. Not wired: C is an
integer, so the step is a gap closing rather than a continuous morphism, and
the companion Bridge repo reads the switch as not transferring to Si
(`Silicon/topological_switch_bounds.py`, TSW-1..6).
