# Level 6 Explainer: Modern Mathematical Models

*(Plain-language companion to `modern_sims.py` — the same style as
`WorkOn_Explainer.md`, `Todo_Explainer.md`, `Addon_Explainer.md`,
`Connections_Explainer.md`.)*

Levels 1–5 built a ladder: classical physics → quantum → chaos → geometry of
geometries → silicon. Level 6 asks a different question: **what new
mathematics has appeared in the last decade or two, and does it also live on
the same continuous geometric space?** Each sim below takes one modern
framework and shows it doing real work, numerically, in under a second to a
few seconds.

---

## 1. `koopman_dmd` — Nonlinear dynamics is secretly linear
The Koopman operator idea: any nonlinear flow becomes a *linear* operator if
you lift it into the (infinite-dimensional) space of observables. Dynamic Mode
Decomposition is the practical finite-rank version. We sample trajectories of
the Van der Pol oscillator, build the best-fit linear operator, and
reconstruct the nonlinear oscillation from 6 eigenmodes. Nonlinear physics,
linear algebra.

## 2. `wasserstein_jko` — Diffusion is geometry on probability space
The Jordan–Kinderlehrer–Otto theorem (1998, the seed of modern optimal
transport theory): the heat equation is the *steepest descent of entropy* in
the Wasserstein metric — the metric that measures the cost of moving one
pile of probability onto another. We step a bimodal distribution forward with
entropic transport steps and watch it melt into a Gaussian with linearly
growing variance, exactly as W2-gradient-flow theory demands.

## 3. `fisher_rao_flow` — Statistics is hyperbolic geometry
Information geometry: treat every probability distribution as a point, with
distances measured by the Fisher information. For 1D Gaussians parameterized
by (μ, σ), this space turns out to be the Poincaré half-plane — constant
negative curvature. The shortest path between two Gaussians is a semicircle,
not a straight line. We compute it and walk the distributions along it.

## 4. `persistent_homology` — The shape of data, without coordinates
Topological data analysis replaces coordinates with *shape that survives at
every scale*. We subsample the Lorenz attractor (Level 3's old friend), grow
ε-balls around the points, and count holes (β₁). Two loops persist across a
wide range of scales: the attractor's two wings. Topology recovers the
structure that the ODE equations hide.

## 5. `pt_symmetric_dimer` — Physics with non-Hermitian matrices
Quantum mechanics demanded Hermitian Hamiltonians for a century. Modern
non-Hermitian physics drops that: with balanced gain and loss, eigenvalues
stay real until they *coalesce at an exceptional point* — a square-root
branch point. Loop around it in parameter space and the eigenstates swap
sheets, like walking around a Riemann surface. No Hermitian system can do
this.

## 6. `mps_compression` — Entanglement is the compression limit
A 10-qubit state needs 1024 amplitudes — until you notice its entanglement
entropy is only ~0.55 bits. Matrix product states (the 1D tensor network)
exploit this: truncate the bond dimension χ and fidelity stays ≈1 because the
Schmidt spectrum decays fast. We diagonalize the transverse-field Ising
ground state and show exactly how little of the Hilbert space physics
actually uses.

## 7. `symplectic_vs_rk4` — Respect the geometry and the numbers behave
Geometric numerical integration: the flow of a Hamiltonian system preserves a
2-form (the symplectic structure). Integrators that preserve it (Verlet) have
energy errors that stay *bounded forever*; general-purpose RK4 drifts
secularly. On the Kepler problem, 30 000 steps later the difference is
orders of magnitude — on an eccentric Kepler orbit RK4's energy drifts by
6% while Verlet's stays at 10⁻⁴. Structure preservation is not aesthetic, it
is numerical accuracy.

## 8. `fractional_diffusion` — Derivatives don't have to be integers
Fractional calculus replaces −Δ by (−Δ)^(α/2). The heat kernel becomes a Lévy
stable law with heavy tails; the mean-squared displacement scales as
t^(2/α) instead of t — superdiffusion, the math behind anomalous transport
in plasmas, biology, and finance. Solved spectrally in a few FFTs.

## 9. `fluctuation_theorem` — The second law is a statistical statement
Stochastic thermodynamics' central result: for a driven microscopic system,
P(+Σ)/P(−Σ) = exp(Σ/k_B). Entropy *can* decrease — just exponentially
rarely. We drag a Brownian particle with a moving harmonic trap 40 000
times, build the entropy-production histogram, and measure the log-ratio
slope: ≈ 0.95 against theory's 1.00.

## 10. `clifford_rotor` — Rotations without matrices or gimbal lock
Geometric algebra Cl(3) represents rotation as a rotor R = exp(−Bθ/2), where
B is the *plane* of rotation (a bivector) — no axis picking, no singularities.
We integrate the torque-free asymmetric top by rotor multiplication alone and
the Dzhanibekov flip (intermediate-axis instability) emerges on its own.

## 11. `sinkhorn_ot` — The transport plan between two worlds
Entropic optimal transport: soften the Monge problem with an entropy term and
it becomes solvable by alternating row/column scaling (Sinkhorn). As
ε → 0 the coupling matrix concentrates onto the deterministic transport map.
This is the workhorse behind modern distribution matching — and it is the
discrete cousin of the Wasserstein flow in sim 2.

## 12. `fourier_neural_op` — Learning operators, not functions
The Fourier Neural Operator learns maps *between function spaces* by
multiplying the low Fourier modes with a learned tensor. We solve viscous
Burgers pseudo-spectrally and show why the architecture works: Burgers'
dynamics dumps virtually all energy into the first handful of modes, so an
8-mode spectral layer captures the map to ~percent accuracy. Neural PDE
solvers are spectral methods wearing a learning costume.

---

## How this plugs into the repo

- **Same sim-module contract:** a `@sim(name, title)` decorator populates
  `REGISTRY` at import time and `run_all()` executes it — identical to
  `sims.py`, `workon_sims.py`, `todo_sims.py`, `addon_sims.py` and
  `connections_sims.py`. `modern_sims` is registered in `run_all_sims.py`'s
  `MODULES` list, so it is driven by the unified entry point like every other
  level. (`MODERN_SIMS`, a plain `name → callable` view of `REGISTRY`, is kept
  as a back-compat alias.)
- **Claims:** `modern_claims.json` holds one `CLAIM_SCHEMA.py`-style entry per
  sim, each stated as `dX/dt under scope`. Every claim carries an **anchor** —
  the registry equation it extends — and the **morphism** that would carry the
  anchor to it:

  | claim | anchor equation | morphism |
  |---|---|---|
  | `koopman_lift` | `van_der_pol` | `nonlinear_to_linear_observable_lift` |
  | `wasserstein_heat_flow` | `ficks_second_law` | `diffusion_as_W2_gradient_flow` |
  | `fisher_rao_hyperbolic` | `kl_divergence` | `information_to_geometry` |
  | `tda_lorenz` | `lorenz_x` | `dynamics_to_topology` |
  | `exceptional_point` | `schrodinger_free` | `hermitian_to_nonhermitian` |
  | `mps_entanglement_bound` | `schrodinger_free` | `hilbert_space_to_tensor_network` |
  | `symplectic_preservation` | `energy_conservation` | `continuous_geometry_to_discrete_geometry` |
  | `fractional_superdiffusion` | `ficks_second_law` | `integer_to_fractional_laplacian` |
  | `detailed_fluctuation_theorem` | `second_law_entropy` | `macroscopic_law_to_microscopic_symmetry` |
  | `rotor_rigid_body` | `newton_2` | `matrix_to_geometric_algebra` |
  | `sinkhorn_convergence` | `kl_divergence` | `continuous_OT_to_entropic_OT` |
  | `fno_spectral_learning` | `navier_stokes_1d` | `pde_to_learned_operator` |

- **Not yet in the graph:** these 12 frameworks are *candidate* registry nodes,
  not registered ones. Promoting one means adding the target equation to
  `EquationRegistry._register_all()` in `physics_playground.py` and the
  `anchor → target` edge to `graph.py`. Until then
  `tests/test_modern_claims.py` guarantees at least that every anchor resolves
  against the live registry, so the claims cannot dangle.

Run:
```bash
python modern_sims.py                          # all 12
python modern_sims.py --list
python modern_sims.py --sim fluctuation_theorem
python run_all_sims.py --module modern_sims    # same, via the unified runner
pytest tests/test_modern_sims.py tests/test_modern_claims.py -v
```
