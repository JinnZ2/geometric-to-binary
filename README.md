# Geometric to Binary — Physics Playground

A symbolic sandbox for mixing, matching, and morphing physics equations across 19 domains. Built on SymPy and NetworkX, this repository implements the "geometric to binary" vision: a navigable state space where equations are nodes, transformations are weighted edges, and every cross-domain analogy is a traversable path.

---

## Architecture

```
EquationRegistry          EquationGraph
─────────────────         ──────────────────────────────────────
PhysicsEquation ──────►  node (equation name)
  .name                    .domain
  .domain                  .description
  .symbolic_expr           .latex
  .latex
  .description         Morphism ──────────────────────────────►  edge
                         .name                weight = α·dim + β·con + γ·dist
                         .source_eq / .target_eq
                         .description
                         .invariants_preserved
```

**Weight formula** for each directed edge:

```
w = α·dimensional_inconsistency + β·constraint_violation + γ·domain_distance
    (α=0.4)                        (β=0.3)                  (γ=0.3, scale 0–3)
```

Lower weight = more natural / physically motivated transformation.

---

## Registry: 73 Equations across 19 Domains

| Domain | Equations |
|---|---|
| **Classical Mechanics** | `newton_2`, `harmonic_oscillator`, `lagrangian_free_particle`, `euler_lagrange`, `energy_conservation` |
| **Electromagnetism** | `wave_equation_1d`, `coulombs_law`, `faradays_law`, `poynting_vector` |
| **Quantum Mechanics** | `schrodinger_free`, `probability_current`, `heisenberg_uncertainty`, `qho_energy_levels`, `de_broglie` |
| **Thermodynamics** | `first_law_thermo`, `second_law_entropy`, `ideal_gas_law`, `boltzmann_entropy` |
| **Fluid Dynamics** | `continuity_1d`, `euler_momentum_1d`, `navier_stokes_1d`, `bernoulli` |
| **Statistical Mechanics** | `boltzmann_factor`, `partition_function`, `maxwell_boltzmann_speed` |
| **Special Relativity** | `mass_energy_equivalence`, `lorentz_factor`, `relativistic_momentum`, `spacetime_interval` |
| **General Relativity** | `einstein_field_equation`, `schwarzschild_metric_tt`, `geodesic_equation` |
| **Plasma Physics** | `plasma_frequency`, `debye_length`, `vlasov_1d` |
| **Optics** | `snells_law`, `thin_lens`, `paraxial_helmholtz`, `rayleigh_criterion` |
| **Condensed Matter** | `drude_conductivity`, `bloch_dispersion_1d`, `bcs_gap_equation`, `fermi_dirac` |
| **Nuclear Physics** | `radioactive_decay`, `semf_binding_energy`, `yukawa_potential` |
| **Astrophysics** | `hydrostatic_equilibrium`, `stellar_mass_continuity`, `virial_theorem`, `jeans_mass` |
| **Nonlinear Dynamics** | `logistic_map`, `lorenz_x`, `van_der_pol`, `lyapunov_exponent` |
| **Acoustics** | `acoustic_impedance`, `acoustic_wave_equation`, `doppler_effect` |
| **Biophysics** | `ficks_first_law`, `ficks_second_law`, `michaelis_menten`, `hodgkin_huxley_membrane` |
| **Information Theory** | `shannon_entropy`, `shannon_capacity`, `landauer_principle`, `kl_divergence` |
| **Cosmology** | `hubble_parameter`, `friedmann_first`, `dark_energy_eos`, `redshift_scale_factor` |
| **High Energy / String** | `klein_gordon`, `nambu_goto_action`, `dirac_1d`, `rg_beta_function` |

---

## Graph: 68 Morphism Edges

Key cross-domain bridges include:

| Morphism | Source → Target | Physical Meaning |
|---|---|---|
| `continuity_to_schrodinger_madelung` | `continuity_1d` → `schrodinger_free` | Madelung transform: fluid ↔ quantum |
| `classical_to_diffusion_morph` | `harmonic_oscillator` → `ficks_second_law` | Propeller morph (MIT droplet style) |
| `yukawa_to_klein_gordon` | `yukawa_potential` → `klein_gordon` | Static solution of massive scalar field |
| `optics_to_quantum` | `paraxial_helmholtz` → `schrodinger_free` | Paraxial wave ↔ Schrödinger (z↔t analogy) |
| `chaos_to_information` | `lyapunov_exponent` → `shannon_entropy` | Kolmogorov-Sinai entropy from chaos |
| `gr_to_cosmology` | `einstein_field_equation` → `friedmann_first` | FLRW ansatz applied to Einstein equations |
| `thermo_to_information` | `boltzmann_entropy` → `shannon_entropy` | Thermodynamic ↔ information entropy |
| `dirac_to_schrodinger` | `dirac_1d` → `schrodinger_free` | Non-relativistic limit of Dirac |
| `vlasov_to_fluid` | `vlasov_1d` → `continuity_1d` | Velocity moments of Vlasov → fluid |
| `landauer_to_thermo` | `landauer_principle` → `boltzmann_entropy` | Bit erasure ↔ thermodynamic entropy |

---

## Setup

### Requirements

```bash
pip install sympy networkx
```

### Run the playground

```bash
python physics_playground.py
```

### Run the graph

```bash
python graph.py
```

---

## Usage Examples

```python
from physics_playground import PhysicsPlayground
from graph import build_morphism_graph, EquationRegistry

# --- Registry ---
playground = PhysicsPlayground()
print(playground.info("klein_gordon"))

# Propeller morph: classical → quantum-diffusion
morphed = playground.creative_mix("harmonic_oscillator", operation="morph")

# Cross-domain algebraic mix
mixed = playground.registry.mix("continuity_1d", "schrodinger_free", "add")

# --- Graph ---
registry = EquationRegistry()
graph    = build_morphism_graph(registry)

# Shortest path between two equations
path = graph.path("harmonic_oscillator", "klein_gordon")
print(" → ".join(path))

# All transformation routes (cutoff = 4 hops)
for p in graph.all_paths("continuity_1d", "schrodinger_free", cutoff=4):
    print(" → ".join(p))

# Everything reachable from a starting equation
print(graph.reachable_from("harmonic_oscillator"))

# Equations in a specific domain
print(graph.domain_cluster(PhysicsDomain.QUANTUM))
```

---

## Planned Extensions

1. **Geometry Layer**: `sympy.Expr` → `lambdify` → NumPy field → voxel / point cloud (the "geometric → binary" bridge).
2. **Madelung Transform**: Full symbolic implementation connecting `continuity_1d` + `euler_momentum_1d` ↔ `schrodinger_free`.
3. **Action → Phase**: Map `lagrangian_free_particle` → quantum phase via `ψ = exp(iS/ħ)`.
4. **Dimensional Consistency Filter**: Attach SI dimensions to symbols; reject or flag invalid mixes.
5. **Jupyter Frontend**: Interactive sliders for parameters with live LaTeX rendering.
6. **Graph Embedding**: Embed the equation graph into a continuous vector space; treat morphisms as flows.
