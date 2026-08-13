# The Quantum-to-Chaos Pipeline: A Plain-Language Guide

*(Plain-language companion to [`todo_sims.py`](todo_sims.py).)*

> `Todo.md`, the source document this translates, was extracted into
> `todo_sims.py` + this file and removed from the repo in commit `ec31bea`.
> It is recoverable with `git show ec31bea^:Todo.md`.

---

## What is this document?

The `Todo.md` file explores a profound mathematical connection between two fields of physics that usually have nothing to do with each other: **Quantum Mechanics** (the physics of the very small) and **Chaos Theory** (the physics of unpredictable, macroscopic systems like weather).

It proves that the equations governing a quantum harmonic oscillator and the equations governing the chaotic Lorenz attractor are actually **the exact same mathematical structure**, just operating in different regimes of a single "control parameter."

Here is a breakdown of the core concepts explained in plain English.

---

## 1. The Equivalence Map (Quantum = Chaos)

Imagine a quantum particle trapped in a bowl (a harmonic oscillator). Now imagine the famous "butterfly wings" of the Lorenz strange attractor from chaos theory. 

The document shows a structural isomorphism (a perfect mathematical mapping) between the two:
- **Deterministic Drift:** The classical transport in the quantum fluid maps exactly to the stretching forces in the Lorenz system.
- **Diffusion:** The quantum probability spreading maps to the damping/relaxation in the Lorenz system.
- **Curvature Feedback (The Q-term):** The term that makes quantum mechanics "quantum" maps exactly to the nonlinear $xy$ feedback term in the Lorenz equations.

**The Takeaway:** The Lorenz strange attractor is just what a quantum wavefunction looks like when its internal curvature feedback becomes overwhelmingly strong.

---

## 2. Stretching, Folding, and Curvature

Chaos theory is built on two actions: **stretching** (pulling trajectories apart so they become unpredictable) and **folding** (bending them back so they don't fly off to infinity). 

In our quantum fluid PDE, the same things are happening:
- The classical velocity field **stretches** the probability density.
- The quantum curvature term (the Q-term) acts as the **folding** mechanism. It takes the probability density that wants to spread out and forcefully bends it back on itself, trapping it in localized blobs.

**The Takeaway:** The "quantumness" of a particle (its tendency to exist in discrete, localized states rather than spreading out forever) is mathematically identical to the folding mechanism that creates a chaotic strange attractor.

---

## 3. The Unified Action Functional

All of this is driven by a single "Master Equation" (an action functional). Depending on the strength of a single dial—the control parameter $\Lambda$—this master equation produces three completely different universes:

### Regime 1: Linear Quantum ($\Lambda < 0.5$)
When the curvature feedback is weak, the system behaves exactly like a textbook quantum harmonic oscillator. You get smooth, Gaussian probability densities and evenly spaced, discrete energy levels. Space is flat.

### Regime 2: Nonlinear Attractor ($0.5 < \Lambda < 5.0$)
When you turn up the feedback, the quantum spectrum shatters. The Gaussian probability density splits into multiple distinct peaks (a bifurcation). The system starts digging its own gravitational wells. Space begins to curve locally.

### Regime 3: Chaotic Attractor ($\Lambda > 5.0$)
When the feedback is pushed to the extreme, the localized blobs become unstable. The probability density is violently stretched and folded, tracing out complex, non-repeating geometric shapes in phase space. Space itself (the effective metric) fluctuates wildly and degenerates. 

**The Takeaway:** Quantum mechanics, nonlinear solitons, and chaotic strange attractors are not different phenomena. They are just weak, medium, and strong settings on the exact same geometric dial.

---

## Where this lives in the repo

The Master Equation above is simulated by **[`todo_sims.py`](todo_sims.py)**
(Level 3, 4 sims), which plots the transition across all three regimes: the
smooth quantum state, the bifurcating nonlinear blobs, the chaotic density
fluctuations, and a phase diagram showing exactly where the boundaries between
Quantum, Soliton and Chaos fall.

```bash
python run_all_sims.py --module todo_sims   # all of them
python todo_sims.py --list                  # enumerate
```
