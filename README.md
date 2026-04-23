# Geometric to Binary: A Physics Playground

This repository is an experimental symbolic and numerical playground designed to explore the mathematical structure connecting different domains of physics. 

It treats physical equations not as isolated laws, but as **nodes in a continuous geometric space**. By applying mathematical "morphisms" (like the Madelung transform or the Fokker-Planck diffusion limit), you can continuously deform a classical system into a quantum one, or a quantum system into a chaotic strange attractor.

---

## 🏗️ Core Architecture

The codebase is built on three pillars:

1. **`EquationRegistry`** (`physics_playground.py`)
   A symbolic database of **90 equations** spanning **23 physics domains** (Classical Mechanics, Quantum, General Relativity, Chaos, Cosmology, Biology, etc.). Each equation is stored as a computable SymPy expression.

2. **`EquationGraph`** (`graph.py`)
   A fully connected, weighted, directed graph of **112 morphisms**. The graph allows you to find the "shortest conceptual path" between any two equations in physics, weighting paths by dimensional consistency and domain distance.

3. **`PhysicsPlayground`** (`physics_playground.py`)
   The interactive interface. Use `playground.morph(eq1, eq2)` to discover the transformation path between two disparate physical systems, or `playground.creative_mix()` to algebraically fuse them.

---

## 🚀 Quickstart

**1. Install dependencies:**
```bash
pip install -r requirements.txt
```

**2. Run the interactive playground:**
```bash
python physics_playground.py
```

**3. Run all simulations:**
```bash
python run_all_sims.py --list    # List all 44 simulations
python run_all_sims.py           # Run everything (saves to plots/)
```

---

## 🧪 The Simulation Hierarchy

The repo includes 44 numerical simulations that prove the math works. They are split across four conceptual levels:

### 1. Domain Physics (`sims.py` — 26 sims)
Standard numerical simulations of the 90 registry equations. Covers everything from quantum tunneling and Schwarzschild orbits to the Lotka-Volterra predator-prey dynamics and Turing pattern formation.

### 2. The Madelung / Ricci Flow Level (`workon_sims.py` — 9 sims)
Explores how adding a "curvature feedback" term to classical diffusion *forces* quantum mechanics to appear. Shows how this feedback eventually shatters the quantum spectrum, leading to self-trapped solitons and Ricci flow curvature islands.
*(Read the plain-language guide: [`WorkOn_Explainer.md`](WorkOn_Explainer.md))*

### 3. The Quantum-to-Chaos Level (`todo_sims.py` — 4 sims)
Proves the **Lorenz-PDE Isomorphism**: the quantum fluid equation and the Lorenz chaos equations share the exact same mathematical structure. Shows how a single Unified Action Functional produces quantum, soliton, and chaotic regimes just by turning one dial ($\Lambda$).
*(Read the plain-language guide: [`Todo_Explainer.md`](Todo_Explainer.md))*

### 4. The Metric Bundle Level (`addon_sims.py` — 5 sims)
Scales the theory up to a "Geometry of Geometries." Simulates the 4D Phase Diagram of Physics, the DeWitt supermetric distance between different universes, entanglement as geometric curvature, and signature transitions as topological holonomies.
*(Read the plain-language guide: [`Addon_Explainer.md`](Addon_Explainer.md))*

---

## 🧬 Example: Morphing Across Domains

You can use the graph to find paths between completely unrelated fields of science.

```python
from physics_playground import PhysicsPlayground

pg = PhysicsPlayground()
result = pg.morph('harmonic_oscillator', 'klein_gordon')

for step in result['steps']:
    print(f"{step['from']} → {step['to']}: {step['morphism']}")
```

**Output:**
```text
harmonic_oscillator → ficks_second_law: classical_to_diffusion_morph
ficks_second_law → continuity_1d: diffusion_to_fokker_planck
continuity_1d → schrodinger_free: continuity_to_schrodinger_madelung
schrodinger_free → klein_gordon: schrodinger_to_klein_gordon
```

---

## ✅ Running Tests

The repo includes a full `pytest` suite that verifies registry completeness, graph connectivity, and symbolic morphing.

```bash
pytest tests/ -v
```

---

*This project is an open-ended exploration of the mathematical unity of physics. Pull requests for new equations, morphisms, or simulations are welcome.*
