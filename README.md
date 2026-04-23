# Geometric to Binary Physics Playground

A symbolic sandbox for mixing, matching, and morphing physics equations. Built on SymPy, this repository explores the "geometric to binary" style of experimental physics modeling.

## Overview

This project provides a framework for:
- **Symbolic Manipulation**: Define, manipulate, and solve equations symbolically across 18 equations spanning 12+ physics domains.
- **Creative Equation Mixing**: Apply "propeller" transforms (e.g., adding Fokker-Planck stochastic terms to classical deterministic equations) to bridge domains.
- **Equation Graph Navigation**: Treat equations as nodes and morphisms as edges in a directed graph, enabling the discovery of shortest paths between domains and multi-path retention.

## Features

- **EquationRegistry**: A central database of 18 physics equations across 12 domains.
- **PropellerTransform**: Implements creative mappings, such as the MIT droplet paper trick (Classical Diffusion + Memory Term = Quantum-like Behavior).
- **EquationGraph**: Navigates the state space of equations, finding minimum-deviation transformation chains.

## Registered Equations

| Name | Domain | Description |
|---|---|---|
| `newton_2` | Classical Mechanics | Newton's Second Law |
| `harmonic_oscillator` | Classical Mechanics | Spring-mass oscillator |
| `schrodinger_free` | Quantum | Time-dependent Schrödinger (1D free particle) |
| `boltzmann_factor` | Statistical | Boltzmann probability weight |
| `continuity_1d` | Fluid Dynamics | 1D mass continuity equation |
| `wave_equation_1d` | Electromagnetism | Classical 1D wave equation |
| `einstein_field_equation` | General Relativity | Einstein field equations with cosmological constant |
| `plasma_frequency` | Plasma Physics | Electron plasma oscillation frequency |
| `snells_law` | Optics | Snell's law of refraction |
| `drude_conductivity` | Condensed Matter | Drude model electrical conductivity |
| `radioactive_decay` | Nuclear Physics | First-order radioactive decay |
| `hydrostatic_equilibrium` | Astrophysics | Stellar pressure-gravity balance |
| `logistic_map` | Nonlinear Dynamics | Discrete chaotic logistic map |
| `acoustic_impedance` | Acoustics | Acoustic impedance relation |
| `ficks_first_law` | Biophysics | Fick's first law of diffusion |
| `shannon_entropy` | Information Theory | Shannon information entropy |
| `hubble_parameter` | Cosmology | Hubble parameter from scale factor |
| `klein_gordon` | High Energy / String | 1D Klein-Gordon scalar field equation |

## Setup

### Requirements
- Python 3.8+
- SymPy
- NetworkX

### Installation
```bash
pip install sympy networkx
```

## Usage

Run the main playground script to see a demonstration of cross-domain equation mixing:

```bash
python physics_playground.py
```

### Interactive Example

You can also use the playground interactively in a Python REPL or Jupyter Notebook:

```python
from physics_playground import PhysicsPlayground

playground = PhysicsPlayground()

# Get information about a registered equation
print(playground.info("harmonic_oscillator"))

# Apply a creative transformation (e.g., MIT Droplet Style morph)
morphed_eq = playground.creative_mix("harmonic_oscillator", operation="morph")
print(morphed_eq)
```

## Architecture Concepts

1. **Symbolic Flexibility**: High freedom in mixing equations.
2. **Constraint Enforcement**: (Planned) Enforce invariants and dimensional consistency.
3. **Graph Space**: Move from isolated equations to a navigable phase space of transformations.

## Future Extensions

- **Action -> Phase Transform**: Map classical mechanics into quantum phase space.
- **Madelung Transform**: Connect fluid dynamics to quantum mechanics.
- **Dimensional Consistency Filter**: Prevent invalid domain mixing by checking units.
- **Geometry Layer**: Project symbolic fields into discretized spatial structures (voxels, point clouds).
