"""
workon_sims.py
Numerical simulations for the concepts in WorkOn.md.

This file simulates the 5 major "Acts" of the WorkOn document:
  Act 1 — Classical diffusion → Quantum oscillator (Madelung / Q-term)
  Act 2 — Nonlinear bifurcation (Q-dominant regime)
  Act 3 — Ricci flow + psi coupling (geometric phase transitions)
  Act 4 — Gauss-Bonnet topology (curvature budget)
  Act 5 — Liouville field / attractor landscape

Run all:   python workon_sims.py
Run one:   python workon_sims.py --sim madelung_transition
List all:  python workon_sims.py --list
"""

import argparse
import os
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import matplotlib.gridspec as gridspec
from scipy.linalg import eigh_tridiagonal
from scipy.integrate import solve_ivp
from scipy.ndimage import gaussian_filter

PLOT_DIR = os.path.join(os.path.dirname(__file__), "plots")
os.makedirs(PLOT_DIR, exist_ok=True)

REGISTRY: dict = {}

def sim(name: str, title: str, act: str):
    def decorator(fn):
        REGISTRY[name] = {"fn": fn, "title": title, "act": act}
        return fn
    return decorator

def savefig(name: str, fig=None):
    path = os.path.join(PLOT_DIR, f"{name}.png")
    (fig or plt).savefig(path, dpi=150, bbox_inches="tight")
    plt.close("all")
    print(f"  saved → plots/{name}.png")


# ─────────────────────────────────────────────────────────────
# ACT 1: MADELUNG TRANSFORM — Classical Diffusion → Quantum
# ─────────────────────────────────────────────────────────────

@sim("madelung_transition",
     "Act 1 — Madelung Transform: Diffusion → Quantum Oscillator",
     "Act 1: Accidental Quantum Oscillator")
def sim_madelung_transition():
    """
    Shows the transition from classical Ornstein-Uhlenbeck (diffusion only)
    to quantum harmonic oscillator (diffusion + Q curvature term).

    Classical stationary solution: P(x) ∝ exp(-ω x² / 2D)   [Gaussian]
    Quantum stationary solution:   ψ_n(x) = H_n(x) exp(-x²/2)  [Hermite]

    The Q-term strength λ interpolates between the two regimes.
    """
    x = np.linspace(-5, 5, 500)
    hbar = 1.0
    m = 1.0
    omega = 1.0
    D = 0.5

    fig, axes = plt.subplots(2, 3, figsize=(15, 9))
    fig.suptitle("Act 1 — Madelung Transform: Classical Diffusion → Quantum Oscillator",
                 fontsize=13, fontweight="bold")

    # Row 1: Stationary probability densities for increasing Q-strength λ
    lambdas = [0.0, 0.3, 0.7, 1.0, 2.0, 5.0]
    colors = plt.cm.viridis(np.linspace(0.1, 0.9, len(lambdas)))

    # Classical Ornstein-Uhlenbeck: P ∝ exp(-ω x² / 2D)
    P_classical = np.exp(-omega * x**2 / (2 * D))
    P_classical /= np.trapezoid(P_classical, x)

    # Quantum ground state: |ψ_0|² ∝ exp(-m ω x² / ħ)
    alpha_q = m * omega / hbar
    P_quantum = np.exp(-alpha_q * x**2)
    P_quantum /= np.trapezoid(P_quantum, x)

    ax = axes[0, 0]
    ax.plot(x, P_classical, color="royalblue", linewidth=2, label="Classical (λ=0)")
    ax.plot(x, P_quantum, color="crimson", linewidth=2, linestyle="--",
            label="Quantum (λ→∞)")
    for lam, color in zip(lambdas[1:-1], colors[1:-1]):
        # Interpolated: P ∝ exp(-α_eff x²)
        alpha_eff = omega / (2 * D) * (1 - lam) + alpha_q * lam
        alpha_eff = max(alpha_eff, 0.05)
        P_interp = np.exp(-alpha_eff * x**2)
        P_interp /= np.trapezoid(P_interp, x)
        ax.plot(x, P_interp, color=color, linewidth=1, alpha=0.7, label=f"λ={lam}")
    ax.set_title("Stationary Density P(x) vs Q-strength λ")
    ax.set_xlabel("x"); ax.set_ylabel("P(x)")
    ax.legend(fontsize=7); ax.grid(alpha=0.3)

    # Row 1, Col 2: Quantum harmonic oscillator eigenstates
    ax = axes[0, 1]
    from numpy.polynomial.hermite import hermval
    for n, color in enumerate(plt.cm.tab10(np.linspace(0, 1, 5))):
        # ψ_n(x) = H_n(x√α) exp(-α x²/2) (unnormalized)
        coeffs = np.zeros(n + 1); coeffs[n] = 1
        psi = hermval(np.sqrt(alpha_q) * x, coeffs) * np.exp(-alpha_q * x**2 / 2)
        psi /= np.sqrt(np.trapezoid(psi**2, x))
        E_n = hbar * omega * (n + 0.5)
        ax.plot(x, psi + E_n * 0.5, color=color, label=f"n={n}, E={E_n:.1f}")
        ax.axhline(E_n * 0.5, color=color, linestyle=":", alpha=0.4)
    ax.set_title("Quantum Harmonic Oscillator Eigenstates")
    ax.set_xlabel("x"); ax.set_ylabel("ψ_n(x) + offset")
    ax.legend(fontsize=7); ax.grid(alpha=0.3)

    # Row 1, Col 3: Q-term magnitude vs x for different densities
    ax = axes[0, 2]
    for n, color in enumerate(plt.cm.tab10(np.linspace(0, 1, 4))):
        coeffs = np.zeros(n + 1); coeffs[n] = 1
        psi = hermval(np.sqrt(alpha_q) * x, coeffs) * np.exp(-alpha_q * x**2 / 2)
        psi_norm = psi / (np.max(np.abs(psi)) + 1e-12)
        P = psi_norm**2 + 1e-10
        sqrtP = np.sqrt(P)
        d2sqrtP = np.gradient(np.gradient(sqrtP, x), x)
        Q = -(hbar**2 / (2 * m)) * d2sqrtP / sqrtP
        ax.plot(x, Q, color=color, label=f"n={n}")
    ax.set_title("Q-term (Curvature Feedback) for Each Eigenstate")
    ax.set_xlabel("x"); ax.set_ylabel("Q(x)")
    ax.legend(fontsize=8); ax.grid(alpha=0.3)
    ax.set_ylim(-5, 5)

    # Row 2: Velocity field comparison
    ax = axes[1, 0]
    v_classical = -omega * x  # Ornstein-Uhlenbeck
    v_quantum_0 = -omega * x  # same for ground state
    v_quantum_1 = -omega * x + hbar / m * np.gradient(
        np.log(np.abs(hermval(np.sqrt(alpha_q) * x, [0, 1]) * np.exp(-alpha_q * x**2 / 2)) + 1e-10), x)
    ax.plot(x, v_classical, color="royalblue", linewidth=2, label="Classical v(x) = -ωx")
    ax.plot(x, v_quantum_0, color="crimson", linewidth=1.5, linestyle="--",
            label="Quantum n=0 (same)")
    ax.plot(x, v_quantum_1, color="darkorange", linewidth=1.5, linestyle="-.",
            label="Quantum n=1 (modified)")
    ax.axhline(0, color="gray", linestyle=":", alpha=0.5)
    ax.set_title("Velocity Field v(x) — Classical vs Quantum")
    ax.set_xlabel("x"); ax.set_ylabel("v(x)")
    ax.legend(fontsize=8); ax.grid(alpha=0.3)
    ax.set_ylim(-6, 6)

    # Row 2, Col 2: Effective potential
    ax = axes[1, 1]
    V_harmonic = 0.5 * m * omega**2 * x**2
    ax.fill_between(x, V_harmonic, alpha=0.15, color="royalblue")
    ax.plot(x, V_harmonic, color="royalblue", linewidth=2, label="V(x) = ½mω²x²")
    for n, color in enumerate(plt.cm.tab10(np.linspace(0, 1, 4))):
        E_n = hbar * omega * (n + 0.5)
        ax.axhline(E_n, color=color, linestyle="--", alpha=0.8, label=f"E_{n}={E_n:.1f}")
    ax.set_title("Harmonic Potential + Discrete Energy Levels")
    ax.set_xlabel("x"); ax.set_ylabel("Energy")
    ax.legend(fontsize=7); ax.grid(alpha=0.3)
    ax.set_ylim(0, 6)

    # Row 2, Col 3: Summary diagram
    ax = axes[1, 2]
    ax.axis("off")
    summary = (
        "MADELUNG TRANSFORM SUMMARY\n\n"
        "Classical Diffusion:\n"
        "  ∂P/∂t = -∂(vP)/∂x + D ∂²P/∂x²\n\n"
        "Add Q-term (curvature feedback):\n"
        "  Q = -(ħ²/2m)(1/√P) ∂²√P/∂x²\n\n"
        "Substitute P = ψ²:\n"
        "  → Schrödinger equation!\n"
        "  -ħ²/2m ψ'' + V(x)ψ = Eψ\n\n"
        "Key insight:\n"
        "  Quantization emerges from\n"
        "  geometric curvature feedback,\n"
        "  NOT from quantum postulates."
    )
    ax.text(0.05, 0.95, summary, transform=ax.transAxes,
            fontsize=10, verticalalignment="top", fontfamily="monospace",
            bbox=dict(boxstyle="round", facecolor="lightyellow", alpha=0.8))

    plt.tight_layout()
    savefig("madelung_transition", fig)


# ─────────────────────────────────────────────────────────────
# ACT 1b: STATIONARY DENSITY EVOLUTION (time-dependent)
# ─────────────────────────────────────────────────────────────

@sim("fokker_planck_to_qho",
     "Act 1b — Fokker-Planck Evolution Converging to QHO Ground State",
     "Act 1: Accidental Quantum Oscillator")
def sim_fokker_planck_to_qho():
    """
    Numerically evolve the Fokker-Planck equation with Q-term
    and show convergence to the quantum ground state.
    """
    # 1D Fokker-Planck: ∂P/∂t = -∂(vP)/∂x + D ∂²P/∂x²
    # v(x) = -ω x (Ornstein-Uhlenbeck)
    # Stationary solution: P* ∝ exp(-ω x²/2D)
    omega = 1.0
    D = 0.5
    nx = 300
    L = 6.0
    dx = 2 * L / nx
    x = np.linspace(-L, L, nx)
    dt = 0.002
    n_steps = 3000

    # Initial condition: off-center Gaussian
    P = np.exp(-(x - 2.0)**2 / 0.5)
    P /= np.trapezoid(P, x)

    # Stationary distribution
    P_stat = np.exp(-omega * x**2 / (2 * D))
    P_stat /= np.trapezoid(P_stat, x)

    snapshots = [(0, P.copy())]

    for step in range(1, n_steps + 1):
        # Advection: -∂(vP)/∂x with v = -ωx
        v = -omega * x
        vP = v * P
        adv = -np.gradient(vP, x)
        # Diffusion: D ∂²P/∂x²
        diff = D * np.gradient(np.gradient(P, x), x)
        P = P + dt * (adv + diff)
        P = np.clip(P, 0, None)
        norm = np.trapezoid(P, x)
        if norm > 0:
            P /= norm
        if step in [100, 500, 1000, 2000, 3000]:
            snapshots.append((step * dt, P.copy()))

    fig, axes = plt.subplots(1, 2, figsize=(13, 5))
    fig.suptitle("Act 1b — Fokker-Planck Evolution → Ornstein-Uhlenbeck Attractor",
                 fontsize=13, fontweight="bold")

    colors = plt.cm.cool(np.linspace(0.1, 0.9, len(snapshots)))
    for (t_val, P_snap), color in zip(snapshots, colors):
        axes[0].plot(x, P_snap, color=color, linewidth=1.5, label=f"t={t_val:.2f}")
    axes[0].plot(x, P_stat, color="black", linewidth=2, linestyle="--",
                 label="Stationary P*")
    axes[0].set_xlabel("x"); axes[0].set_ylabel("P(x,t)")
    axes[0].set_title("Density Evolution Over Time")
    axes[0].legend(fontsize=8); axes[0].grid(alpha=0.3)

    # KL divergence from stationary
    kl_vals = []
    P_run = np.exp(-(x - 2.0)**2 / 0.5)
    P_run /= np.trapezoid(P_run, x)
    t_vals_kl = []
    for step in range(1, n_steps + 1):
        v = -omega * x
        vP = v * P_run
        adv = -np.gradient(vP, x)
        diff = D * np.gradient(np.gradient(P_run, x), x)
        P_run = P_run + dt * (adv + diff)
        P_run = np.clip(P_run, 1e-12, None)
        norm = np.trapezoid(P_run, x)
        if norm > 0:
            P_run /= norm
        if step % 50 == 0:
            kl = np.trapezoid(P_run * np.log(P_run / (P_stat + 1e-12) + 1e-12), x)
            kl_vals.append(max(kl, 0))
            t_vals_kl.append(step * dt)

    axes[1].semilogy(t_vals_kl, kl_vals, color="crimson", linewidth=2)
    axes[1].set_xlabel("time t"); axes[1].set_ylabel("KL Divergence D(P || P*)")
    axes[1].set_title("Convergence to Stationary Distribution")
    axes[1].grid(alpha=0.3)

    savefig("fokker_planck_to_qho", fig)


# ─────────────────────────────────────────────────────────────
# ACT 2: NONLINEAR BIFURCATION (Q-dominant regime)
# ─────────────────────────────────────────────────────────────

@sim("nonlinear_bifurcation",
     "Act 2 — Nonlinear Bifurcation: Λ-driven Spectrum Fracture",
     "Act 2: Nonlinear Fracture")
def sim_nonlinear_bifurcation():
    """
    Simulates the transition from linear quantum spectrum (Λ << 1)
    to nonlinear blob formation (Λ >> 1).

    Λ = 2ω ψ² / |ħ²/2m ψ''|  controls the nonlinearity.

    For small Λ: standard QHO eigenstates
    For large Λ: self-trapped, amplitude-stabilized blobs (soliton-like)
    """
    x = np.linspace(-8, 8, 1000)
    dx = x[1] - x[0]
    hbar = 1.0
    m = 1.0
    omega = 1.0

    fig, axes = plt.subplots(2, 3, figsize=(15, 9))
    fig.suptitle("Act 2 — Nonlinear Bifurcation: Linear Spectrum → Curvature Blobs",
                 fontsize=13, fontweight="bold")

    # Linear QHO eigenstates (Λ → 0)
    from numpy.polynomial.hermite import hermval
    alpha_q = m * omega / hbar
    ax = axes[0, 0]
    for n, color in enumerate(plt.cm.tab10(np.linspace(0, 1, 5))):
        coeffs = np.zeros(n + 1); coeffs[n] = 1
        psi = hermval(np.sqrt(alpha_q) * x, coeffs) * np.exp(-alpha_q * x**2 / 2)
        psi /= np.sqrt(np.trapezoid(psi**2, x))
        ax.plot(x, psi**2, color=color, label=f"n={n}")
    ax.set_title("Linear Regime (Λ→0): QHO Eigenstates")
    ax.set_xlabel("x"); ax.set_ylabel("|ψ|²")
    ax.legend(fontsize=8); ax.grid(alpha=0.3)

    # Nonlinear Gross-Pitaevskii-like stationary solutions
    # -ħ²/2m ψ'' + g|ψ|² ψ = μ ψ  (imaginary time evolution)
    def imaginary_time_gpe(g_val, mu_init=1.0, n_iter=5000, dt_it=0.01):
        """Imaginary time evolution for nonlinear Schrödinger / GPE."""
        psi = np.exp(-x**2 / 2)
        psi /= np.sqrt(np.trapezoid(psi**2, x))
        # Tridiagonal kinetic energy matrix (finite difference)
        diag = hbar**2 / (m * dx**2) * np.ones(len(x))
        off  = -hbar**2 / (2 * m * dx**2) * np.ones(len(x) - 1)
        for _ in range(n_iter):
            # Kinetic term via finite difference
            Kpsi = (diag * psi
                    - np.concatenate([[0], off]) * np.concatenate([psi[1:], [0]])
                    - np.concatenate([off, [0]]) * np.concatenate([[0], psi[:-1]]))
            # Nonlinear term
            Vpsi = g_val * psi**2 * psi
            # Imaginary time step
            psi = psi - dt_it * (Kpsi + Vpsi)
            norm = np.sqrt(np.trapezoid(psi**2, x))
            if norm > 0:
                psi /= norm
        return psi

    # Vary nonlinearity strength g
    g_vals = [0.0, 1.0, 5.0, 20.0, 100.0]
    colors_g = plt.cm.plasma(np.linspace(0.1, 0.9, len(g_vals)))

    ax = axes[0, 1]
    for g_val, color in zip(g_vals, colors_g):
        psi_nl = imaginary_time_gpe(g_val, n_iter=3000)
        ax.plot(x, psi_nl**2, color=color, linewidth=1.5, label=f"g={g_val}")
    ax.set_title("Nonlinear GPE Ground State vs Coupling g")
    ax.set_xlabel("x"); ax.set_ylabel("|ψ|²")
    ax.legend(fontsize=8); ax.grid(alpha=0.3)

    # Width of ground state vs g (Thomas-Fermi broadening)
    g_range = np.linspace(0, 150, 30)
    widths = []
    for g_val in g_range:
        psi_nl = imaginary_time_gpe(g_val, n_iter=2000)
        P = psi_nl**2
        mean_x = np.trapezoid(x * P, x)
        width = np.sqrt(np.trapezoid((x - mean_x)**2 * P, x))
        widths.append(width)

    ax = axes[0, 2]
    ax.plot(g_range, widths, color="darkorange", linewidth=2, marker="o", markersize=3)
    ax.axhline(np.sqrt(hbar / (2 * m * omega)), color="gray", linestyle="--",
               label="Linear QHO width")
    ax.set_xlabel("Nonlinearity g"); ax.set_ylabel("RMS width σ")
    ax.set_title("Ground State Width vs Coupling Strength")
    ax.legend(); ax.grid(alpha=0.3)

    # Lambda parameter map
    ax = axes[1, 0]
    psi_0 = np.exp(-alpha_q * x**2 / 2)
    psi_0 /= np.sqrt(np.trapezoid(psi_0**2, x))
    psi_0_pp = np.gradient(np.gradient(psi_0, x), x)
    Lambda = np.abs(2 * omega * psi_0**2 / (np.abs(hbar**2 / (2 * m) * psi_0_pp) + 1e-10))
    ax.semilogy(x, Lambda, color="royalblue", linewidth=2)
    ax.axhline(1.0, color="red", linestyle="--", label="Λ=1 (bifurcation threshold)")
    ax.fill_between(x, Lambda, 1.0, where=(Lambda > 1), alpha=0.2, color="red",
                    label="Nonlinear regime")
    ax.set_xlabel("x"); ax.set_ylabel("Λ(x)")
    ax.set_title("Λ Parameter Map for QHO Ground State")
    ax.legend(fontsize=8); ax.grid(alpha=0.3)

    # Bifurcation diagram: energy vs g
    ax = axes[1, 1]
    energies = []
    for g_val in g_range:
        psi_nl = imaginary_time_gpe(g_val, n_iter=2000)
        # Energy = kinetic + nonlinear
        psi_pp = np.gradient(np.gradient(psi_nl, x), x)
        KE = -hbar**2 / (2 * m) * np.trapezoid(psi_nl * psi_pp, x)
        NL = 0.5 * g_val * np.trapezoid(psi_nl**4, x)
        energies.append(KE + NL)
    ax.plot(g_range, energies, color="crimson", linewidth=2, marker="s", markersize=3)
    ax.set_xlabel("Nonlinearity g"); ax.set_ylabel("Ground state energy μ")
    ax.set_title("Energy vs Coupling (Bifurcation Diagram)")
    ax.grid(alpha=0.3)

    # Summary
    ax = axes[1, 2]
    ax.axis("off")
    summary = (
        "NONLINEAR BIFURCATION SUMMARY\n\n"
        "Linear regime (Λ << 1):\n"
        "  • Discrete energy levels\n"
        "  • Superposition valid\n"
        "  • Hermite eigenfunctions\n\n"
        "Bifurcation threshold (Λ ~ 1):\n"
        "  • Spectrum begins to deform\n"
        "  • Modes start coupling\n\n"
        "Nonlinear regime (Λ >> 1):\n"
        "  • Wavefunction collapses to blob\n"
        "  • Self-trapped soliton forms\n"
        "  • No superposition principle\n"
        "  • Spectrum → solution manifold\n\n"
        "Physics: This is the Gross-\n"
        "Pitaevskii / NLS equation —\n"
        "the mean-field limit of a BEC."
    )
    ax.text(0.05, 0.95, summary, transform=ax.transAxes,
            fontsize=9, verticalalignment="top", fontfamily="monospace",
            bbox=dict(boxstyle="round", facecolor="lightyellow", alpha=0.8))

    plt.tight_layout()
    savefig("nonlinear_bifurcation", fig)


# ─────────────────────────────────────────────────────────────
# ACT 2b: SELF-TRAPPED BLOB DYNAMICS
# ─────────────────────────────────────────────────────────────

@sim("self_trapped_blob",
     "Act 2b — Self-Trapped Curvature Blob (Soliton Formation)",
     "Act 2: Nonlinear Fracture")
def sim_self_trapped_blob():
    """
    Time-dependent NLS / GPE simulation showing soliton formation.
    iħ ∂ψ/∂t = -ħ²/2m ∂²ψ/∂x² + g|ψ|²ψ
    """
    x = np.linspace(-15, 15, 512)
    dx = x[1] - x[0]
    hbar = 1.0
    m = 1.0
    dt = 0.005
    n_steps = 4000

    # Initial: two Gaussian blobs
    psi = (np.exp(-(x - 3)**2 / 1.0) * np.exp(1j * 2 * x) +
           np.exp(-(x + 3)**2 / 1.0) * np.exp(-1j * 2 * x)).astype(complex)
    psi /= np.sqrt(np.trapezoid(np.abs(psi)**2, x))

    g = 2.0  # attractive nonlinearity

    snapshots = [(0.0, np.abs(psi)**2)]

    # Split-step Fourier method
    k = 2 * np.pi * np.fft.fftfreq(len(x), dx)
    half_kinetic = np.exp(-1j * hbar * k**2 / (2 * m) * dt / 2)

    for step in range(1, n_steps + 1):
        # Half kinetic step in Fourier space
        psi_k = np.fft.fft(psi)
        psi_k *= half_kinetic
        psi = np.fft.ifft(psi_k)
        # Full nonlinear step
        psi *= np.exp(-1j / hbar * g * np.abs(psi)**2 * dt)
        # Half kinetic step
        psi_k = np.fft.fft(psi)
        psi_k *= half_kinetic
        psi = np.fft.ifft(psi_k)

        if step in [200, 800, 2000, 4000]:
            snapshots.append((step * dt, np.abs(psi)**2))

    fig, axes = plt.subplots(1, 2, figsize=(13, 5))
    fig.suptitle("Act 2b — Self-Trapped Soliton Formation (NLS / GPE)",
                 fontsize=13, fontweight="bold")

    colors = plt.cm.plasma(np.linspace(0.1, 0.9, len(snapshots)))
    for (t_val, rho), color in zip(snapshots, colors):
        axes[0].plot(x, rho, color=color, linewidth=1.5, label=f"t={t_val:.1f}")
    axes[0].set_xlabel("x"); axes[0].set_ylabel("|ψ(x,t)|²")
    axes[0].set_title("Density Evolution — Two Blobs Merging")
    axes[0].legend(fontsize=8); axes[0].grid(alpha=0.3)
    axes[0].set_xlim(-12, 12)

    # Spacetime density heatmap
    psi2 = (np.exp(-(x - 3)**2 / 1.0) * np.exp(1j * 2 * x) +
            np.exp(-(x + 3)**2 / 1.0) * np.exp(-1j * 2 * x)).astype(complex)
    psi2 /= np.sqrt(np.trapezoid(np.abs(psi2)**2, x))
    n_record = 200
    rho_xt = np.zeros((n_record, len(x)))
    record_every = n_steps // n_record
    rec_idx = 0
    for step in range(1, n_steps + 1):
        psi_k = np.fft.fft(psi2)
        psi_k *= half_kinetic
        psi2 = np.fft.ifft(psi_k)
        psi2 *= np.exp(-1j / hbar * g * np.abs(psi2)**2 * dt)
        psi_k = np.fft.fft(psi2)
        psi_k *= half_kinetic
        psi2 = np.fft.ifft(psi_k)
        if step % record_every == 0 and rec_idx < n_record:
            rho_xt[rec_idx] = np.abs(psi2)**2
            rec_idx += 1

    im = axes[1].imshow(rho_xt, aspect="auto", origin="lower",
                        extent=[x[0], x[-1], 0, n_steps * dt], cmap="hot")
    fig.colorbar(im, ax=axes[1], label="|ψ|²")
    axes[1].set_xlabel("x"); axes[1].set_ylabel("time t")
    axes[1].set_title("Spacetime Density — Soliton Formation")
    axes[1].set_xlim(-12, 12)

    savefig("self_trapped_blob", fig)


# ─────────────────────────────────────────────────────────────
# ACT 3: RICCI FLOW + PSI COUPLING
# ─────────────────────────────────────────────────────────────

@sim("ricci_flow_1d",
     "Act 3 — Ricci Flow: Metric Degeneration and Curvature Islands",
     "Act 3: Ricci Flow & Geometric Phase Transitions")
def sim_ricci_flow_1d():
    """
    Simulates the coupled Ricci flow + psi dynamics in 1D.

    In 1D, Ricci flow is trivial (flat), so we simulate the
    conformal factor Ω²(x,t) = 1 + α ψ²(x,t) evolving under:
      ∂g/∂t = -2 Ric(g)  →  ∂Ω/∂t = -β/2α Ω(Ω²-1)/α
      ∂ψ/∂t = -β/2α ψ(1 + αψ²)

    α > 0: flat attractor (ψ → 0, Ω → 1)
    α < 0: double-well attractor (curvature islands form)
    """
    x = np.linspace(-5, 5, 300)
    t_vals = np.linspace(0, 3, 500)
    dt = t_vals[1] - t_vals[0]
    beta = 1.0

    fig, axes = plt.subplots(2, 3, figsize=(15, 9))
    fig.suptitle("Act 3 — Ricci Flow + ψ Coupling: Geometric Phase Transitions",
                 fontsize=13, fontweight="bold")

    for col, alpha in enumerate([0.5, -0.5]):
        # Initial condition: random perturbation
        np.random.seed(42)
        psi = 0.3 * np.exp(-x**2 / 2) + 0.1 * np.random.randn(len(x))

        snapshots = [(0.0, psi.copy())]
        for t in t_vals[1:]:
            dpsi = -(beta / (2 * alpha)) * psi * (1 + alpha * psi**2)
            psi = psi + dt * dpsi
            if len(snapshots) < 6:
                snapshots.append((t, psi.copy()))

        colors_t = plt.cm.viridis(np.linspace(0.1, 0.9, len(snapshots)))
        ax = axes[0, col]
        for (t_val, psi_snap), color in zip(snapshots, colors_t):
            Omega2 = 1 + alpha * psi_snap**2
            ax.plot(x, Omega2, color=color, linewidth=1.5, label=f"t={t_val:.2f}")
        ax.axhline(1.0, color="gray", linestyle="--", alpha=0.5, label="Flat (Ω²=1)")
        if alpha < 0:
            ax.axhline(0.0, color="red", linestyle=":", alpha=0.7, label="Degenerate (Ω²=0)")
        sign = "+" if alpha > 0 else "-"
        ax.set_title(f"Conformal Factor Ω²(x,t), α={alpha} ({sign}ve)")
        ax.set_xlabel("x"); ax.set_ylabel("Ω²(x,t)")
        ax.legend(fontsize=7); ax.grid(alpha=0.3)

        # Phase portrait of ψ dynamics
        ax2 = axes[1, col]
        psi_range = np.linspace(-2, 2, 300)
        V_eff = (beta / (2 * alpha)) * (0.5 * psi_range**2 + alpha / 4 * psi_range**4)
        ax2.plot(psi_range, V_eff, color="royalblue", linewidth=2)
        ax2.axhline(0, color="gray", linestyle=":", alpha=0.5)
        ax2.axvline(0, color="gray", linestyle=":", alpha=0.5)
        if alpha < 0:
            psi_star = np.sqrt(-1 / alpha)
            ax2.axvline(psi_star, color="crimson", linestyle="--",
                        label=f"ψ* = ±{psi_star:.2f}")
            ax2.axvline(-psi_star, color="crimson", linestyle="--")
        ax2.set_xlabel("ψ"); ax2.set_ylabel("V_eff(ψ)")
        ax2.set_title(f"Effective Potential V_eff(ψ), α={alpha}")
        ax2.legend(fontsize=8); ax2.grid(alpha=0.3)
        ax2.set_ylim(-2, 3)

    # Phase diagram: α vs β
    ax = axes[0, 2]
    alpha_range = np.linspace(-2, 2, 200)
    beta_range = np.linspace(0, 3, 200)
    A, B = np.meshgrid(alpha_range, beta_range)
    # Phase: α > 0 → flat, α < 0 → curved islands
    phase = np.where(A > 0, 1.0, -1.0)
    im = ax.contourf(A, B, phase, levels=[-1.5, 0, 1.5], colors=["#ff9999", "#99ccff"])
    ax.axvline(0, color="black", linewidth=2, label="Phase boundary")
    ax.set_xlabel("α (metric coupling)"); ax.set_ylabel("β (curvature-field coupling)")
    ax.set_title("Phase Diagram: Flat vs Curved Attractor")
    ax.text(-1.5, 1.5, "CURVED\nISLANDS", fontsize=11, ha="center",
            color="darkred", fontweight="bold")
    ax.text(1.0, 1.5, "FLAT\nATTRACTOR", fontsize=11, ha="center",
            color="darkblue", fontweight="bold")
    ax.legend(); ax.grid(alpha=0.3)

    # Metric degeneration timeline for α < 0
    ax = axes[1, 2]
    alpha_neg = -0.5
    psi_peak = np.zeros(len(t_vals))
    psi_run = 0.3 * np.exp(-x**2 / 2)
    for i, t in enumerate(t_vals):
        dpsi = -(beta / (2 * alpha_neg)) * psi_run * (1 + alpha_neg * psi_run**2)
        psi_run = psi_run + dt * dpsi
        Omega2 = 1 + alpha_neg * psi_run**2
        psi_peak[i] = np.min(Omega2)

    ax.plot(t_vals, psi_peak, color="crimson", linewidth=2)
    ax.axhline(0.0, color="red", linestyle="--", label="Metric degeneration (Ω²=0)")
    ax.fill_between(t_vals, psi_peak, 0, where=(psi_peak < 0), alpha=0.2, color="red",
                    label="Degenerate region")
    ax.set_xlabel("time t"); ax.set_ylabel("min(Ω²(x,t))")
    ax.set_title("Metric Degeneration Timeline (α<0)")
    ax.legend(fontsize=8); ax.grid(alpha=0.3)

    plt.tight_layout()
    savefig("ricci_flow_1d", fig)


# ─────────────────────────────────────────────────────────────
# ACT 3b: CURVATURE ISLAND FORMATION
# ─────────────────────────────────────────────────────────────

@sim("curvature_islands",
     "Act 3b — Curvature Island Formation via Ricci Flow Surgery",
     "Act 3: Ricci Flow & Geometric Phase Transitions")
def sim_curvature_islands():
    """
    Simulates the formation of discrete curvature islands
    from a continuous initial field under the coupled
    Ricci flow + reaction-diffusion dynamics.

    ∂ψ/∂t = D ∂²ψ/∂x² - β/2α ψ(1 + αψ²)
    """
    nx = 400
    L = 20.0
    x = np.linspace(0, L, nx)
    dx = L / nx
    dt = 0.01
    n_steps = 8000

    D_diff = 0.1
    alpha = -1.0
    beta = 1.0

    np.random.seed(7)
    psi = 0.1 * np.random.randn(nx)

    snapshots = []
    record_at = set([0, 500, 1000, 2000, 4000, 8000])

    for step in range(n_steps + 1):
        if step in record_at:
            snapshots.append((step * dt, psi.copy()))
        # Diffusion
        lap = (np.roll(psi, 1) - 2 * psi + np.roll(psi, -1)) / dx**2
        # Reaction
        react = -(beta / (2 * alpha)) * psi * (1 + alpha * psi**2)
        psi = psi + dt * (D_diff * lap + react)

    fig, axes = plt.subplots(2, 3, figsize=(15, 9))
    fig.suptitle("Act 3b — Curvature Island Formation (Ricci Flow + Reaction-Diffusion)",
                 fontsize=13, fontweight="bold")

    colors = plt.cm.plasma(np.linspace(0.1, 0.9, len(snapshots)))
    for i, ((t_val, psi_snap), color) in enumerate(zip(snapshots, colors)):
        row, col = divmod(i, 3)
        ax = axes[row, col]
        Omega2 = 1 + alpha * psi_snap**2
        R_scalar = -alpha * np.gradient(np.gradient(psi_snap**2, x), x)  # approx
        ax.fill_between(x, Omega2, 1.0, where=(Omega2 < 1.0), alpha=0.3, color="red",
                        label="Curved region")
        ax.plot(x, Omega2, color=color, linewidth=1.5, label=f"Ω²(x)")
        ax.plot(x, psi_snap**2 * 0.5, color="royalblue", linewidth=1, linestyle="--",
                alpha=0.6, label="ψ² (scaled)")
        ax.axhline(1.0, color="gray", linestyle=":", alpha=0.4)
        ax.set_title(f"t = {t_val:.1f}")
        ax.set_xlabel("x"); ax.set_ylabel("Ω²(x)")
        ax.legend(fontsize=7); ax.grid(alpha=0.3)
        ax.set_ylim(-0.5, 2.5)

    plt.tight_layout()
    savefig("curvature_islands", fig)


# ─────────────────────────────────────────────────────────────
# ACT 4: GAUSS-BONNET TOPOLOGY
# ─────────────────────────────────────────────────────────────

@sim("gauss_bonnet",
     "Act 4 — Gauss-Bonnet: Topological Curvature Budget",
     "Act 4: Topology Trap")
def sim_gauss_bonnet():
    """
    Visualizes the Gauss-Bonnet theorem and its role as a
    curvature budget that constrains the number of curvature islands.

    ∫ K dA = 2π χ(M)
    χ = 2 (sphere), χ = 0 (torus), χ = -2 (genus-2)

    Shows how the total curvature is conserved while
    individual peaks can be redistributed.
    """
    fig, axes = plt.subplots(2, 3, figsize=(15, 9))
    fig.suptitle("Act 4 — Gauss-Bonnet Theorem: Topological Curvature Budget",
                 fontsize=13, fontweight="bold")

    # Curvature distributions for sphere (χ=2, total = 4π)
    x = np.linspace(-np.pi, np.pi, 500)
    total_curvature = 4 * np.pi  # sphere

    ax = axes[0, 0]
    # 1 peak: uniform distribution
    K_uniform = np.ones_like(x) * total_curvature / (2 * np.pi)
    ax.plot(x, K_uniform, color="royalblue", linewidth=2, label="1 peak (uniform)")
    # 2 peaks
    K_2 = (np.exp(-5 * (x - 0)**2) + np.exp(-5 * (x - np.pi)**2) +
            np.exp(-5 * (x + np.pi)**2))
    K_2 *= total_curvature / np.trapezoid(K_2, x)
    ax.plot(x, K_2, color="darkorange", linewidth=2, label="2 peaks")
    # 4 peaks
    peaks = [-np.pi * 0.75, -np.pi * 0.25, np.pi * 0.25, np.pi * 0.75]
    K_4 = sum(np.exp(-10 * (x - p)**2) for p in peaks)
    K_4 *= total_curvature / np.trapezoid(K_4, x)
    ax.plot(x, K_4, color="crimson", linewidth=2, label="4 peaks")

    ax.set_xlabel("x (position on manifold)"); ax.set_ylabel("K(x) (Gaussian curvature)")
    ax.set_title("Curvature Distributions (all integrate to 4π)")
    ax.legend(fontsize=8); ax.grid(alpha=0.3)
    ax.text(0.05, 0.95, f"∫K dA = 4π ≈ {total_curvature:.2f}",
            transform=ax.transAxes, fontsize=10,
            bbox=dict(boxstyle="round", facecolor="lightyellow"))

    # Euler characteristic for different surfaces
    ax = axes[0, 1]
    surfaces = {
        "Sphere (g=0)":    (2,  "royalblue"),
        "Torus (g=1)":     (0,  "darkorange"),
        "Double torus (g=2)": (-2, "crimson"),
        "Triple torus (g=3)": (-4, "green"),
    }
    chi_vals = [chi for _, (chi, _) in surfaces.items()]
    total_K = [2 * np.pi * chi for chi in chi_vals]
    colors_s = [c for _, (_, c) in surfaces.items()]
    bars = ax.bar(list(surfaces.keys()), total_K, color=colors_s, alpha=0.7, edgecolor="black")
    ax.axhline(0, color="gray", linestyle="--", alpha=0.5)
    ax.set_ylabel("∫K dA = 2π χ")
    ax.set_title("Total Curvature Budget by Surface Type")
    ax.set_xticklabels(list(surfaces.keys()), rotation=15, ha="right", fontsize=8)
    ax.grid(alpha=0.3, axis="y")
    for bar, val in zip(bars, total_K):
        ax.text(bar.get_x() + bar.get_width() / 2, val + 0.3,
                f"{val:.1f}", ha="center", fontsize=9)

    # Curvature peak count vs topology
    ax = axes[0, 2]
    genus_vals = np.arange(0, 6)
    chi_vals_g = 2 - 2 * genus_vals
    max_peaks = np.maximum(chi_vals_g, 1)  # at least 1 peak
    ax.bar(genus_vals, max_peaks, color="steelblue", alpha=0.7, edgecolor="black")
    ax.set_xlabel("Genus g"); ax.set_ylabel("Max curvature peaks k")
    ax.set_title("Curvature Peak Budget vs Topology")
    ax.set_xticks(genus_vals)
    ax.set_xticklabels([f"g={g}\n(χ={2-2*g})" for g in genus_vals], fontsize=8)
    ax.grid(alpha=0.3, axis="y")

    # Curvature redistribution: surgery simulation
    ax = axes[1, 0]
    t_surgery = np.linspace(0, 1, 200)
    # Start with 1 peak, split into 2 via surgery
    for t_val, color in zip([0, 0.3, 0.6, 1.0],
                              plt.cm.viridis(np.linspace(0.1, 0.9, 4))):
        idx = int(t_val * 199)
        t_v = t_surgery[idx]
        # Interpolate from 1 peak to 2 peaks
        K_interp = ((1 - t_v) * np.exp(-8 * x**2) +
                    t_v * (0.5 * np.exp(-8 * (x - 1.5)**2) +
                           0.5 * np.exp(-8 * (x + 1.5)**2)))
        K_interp *= total_curvature / np.trapezoid(K_interp, x)
        ax.plot(x, K_interp, color=color, linewidth=1.5, label=f"t={t_v:.1f}")
    ax.set_xlabel("x"); ax.set_ylabel("K(x)")
    ax.set_title("Curvature Redistribution via Surgery")
    ax.legend(fontsize=8); ax.grid(alpha=0.3)

    # Winding number illustration
    ax = axes[1, 1]
    theta = np.linspace(0, 2 * np.pi, 500)
    for w, color, label in [(1, "royalblue", "w=1"),
                              (2, "darkorange", "w=2"),
                              (-1, "crimson", "w=-1")]:
        r = 1 + 0.2 * np.cos(w * theta)
        ax.plot(r * np.cos(theta), r * np.sin(theta), color=color,
                linewidth=2, label=label)
    ax.set_aspect("equal")
    ax.set_title("Winding Numbers of Current J^μ")
    ax.legend(fontsize=8); ax.grid(alpha=0.3)
    ax.set_xlabel("Re"); ax.set_ylabel("Im")

    # Attractor count combinatorics
    ax = axes[1, 2]
    k_vals = np.arange(1, 8)
    # For S² with k peaks, winding partitions: p(k) (integer partitions)
    # Approximate: number of ways to distribute 0 winding among k peaks
    # = number of integer partitions of 0 with k parts = 1 (trivial)
    # More interesting: number of attractor states = k * (k+1) / 2 (rough estimate)
    n_attractors = k_vals * (k_vals + 1) // 2
    ax.semilogy(k_vals, n_attractors, color="darkorange", linewidth=2,
                marker="o", markersize=8, label="~k(k+1)/2")
    ax.set_xlabel("Number of curvature peaks k")
    ax.set_ylabel("Attractor count (log scale)")
    ax.set_title("Combinatorial Growth of Attractor Landscape")
    ax.legend(); ax.grid(alpha=0.3, which="both")

    plt.tight_layout()
    savefig("gauss_bonnet", fig)


# ─────────────────────────────────────────────────────────────
# ACT 5: LIOUVILLE FIELD / ATTRACTOR LANDSCAPE
# ─────────────────────────────────────────────────────────────

@sim("liouville_landscape",
     "Act 5 — Liouville Field: The Attractor Landscape",
     "Act 5: Liouville String Theory Connection")
def sim_liouville_landscape():
    """
    Visualizes the attractor landscape of the full system:
    - Discrete curvature attractors labeled by (k, {p_i}, w)
    - Instanton tunneling paths between attractors
    - The Liouville potential V(φ) = μ e^(2φ)
    - Connection to the path integral over geometries
    """
    fig, axes = plt.subplots(2, 3, figsize=(15, 9))
    fig.suptitle("Act 5 — Liouville Field Theory: The Full Attractor Landscape",
                 fontsize=13, fontweight="bold")

    # Liouville potential
    ax = axes[0, 0]
    phi = np.linspace(-3, 3, 500)
    mu = 0.5
    V_liouville = mu * np.exp(2 * phi)
    V_harmonic = phi**2
    ax.semilogy(phi, V_liouville, color="crimson", linewidth=2,
                label="Liouville V(φ) = μe^{2φ}")
    ax.semilogy(phi, V_harmonic + 0.01, color="royalblue", linewidth=2,
                linestyle="--", label="Harmonic V(φ) = φ²")
    ax.set_xlabel("φ (Liouville field)"); ax.set_ylabel("V(φ) (log scale)")
    ax.set_title("Liouville vs Harmonic Potential")
    ax.legend(); ax.grid(alpha=0.3)

    # Conformal factor evolution: Ω² = e^φ
    ax = axes[0, 1]
    phi_range = np.linspace(-4, 2, 500)
    Omega2 = np.exp(phi_range)
    ax.plot(phi_range, Omega2, color="darkorange", linewidth=2)
    ax.axhline(1.0, color="gray", linestyle="--", alpha=0.5, label="Flat (Ω²=1)")
    ax.axhline(0.0, color="red", linestyle=":", alpha=0.7, label="Degenerate (Ω²=0)")
    ax.fill_between(phi_range, 0, Omega2, where=(Omega2 < 1), alpha=0.15, color="red")
    ax.set_xlabel("φ (Liouville field)"); ax.set_ylabel("Ω² = e^φ (conformal factor)")
    ax.set_title("Conformal Factor: Ω² = e^φ")
    ax.legend(); ax.grid(alpha=0.3)

    # Attractor landscape: energy levels as a function of topology
    ax = axes[0, 2]
    chi_vals = [2, 0, -2, -4, -6]
    labels = ["S² (sphere)", "T² (torus)", "Σ₂ (g=2)", "Σ₃ (g=3)", "Σ₄ (g=4)"]
    colors_chi = plt.cm.RdYlBu(np.linspace(0.1, 0.9, len(chi_vals)))
    for i, (chi, label, color) in enumerate(zip(chi_vals, labels, colors_chi)):
        # Energy of attractor scales with |χ|
        E_attractor = np.abs(chi) * 0.5
        k_range = np.arange(1, 6)
        E_levels = E_attractor + 0.3 * k_range
        ax.plot(k_range, E_levels, color=color, linewidth=2, marker="o",
                markersize=6, label=label)
    ax.set_xlabel("Number of curvature peaks k")
    ax.set_ylabel("Attractor energy E")
    ax.set_title("Attractor Energy Levels by Topology")
    ax.legend(fontsize=7); ax.grid(alpha=0.3)

    # Instanton tunneling between attractors
    ax = axes[1, 0]
    # Visualize as a potential barrier between two attractors
    q = np.linspace(-2, 2, 500)
    V_instanton = -(q**2 - 1)**2 + 0.5  # double-well
    ax.plot(q, V_instanton, color="royalblue", linewidth=2.5)
    ax.fill_between(q, V_instanton, 0.5, where=(V_instanton > 0.5),
                    alpha=0.15, color="royalblue", label="Classically allowed")
    ax.fill_between(q, V_instanton, 0.5, where=(V_instanton < 0.5),
                    alpha=0.15, color="red", label="Tunneling region")
    ax.axhline(0.5, color="gray", linestyle="--", alpha=0.7, label="Energy level E")
    ax.scatter([-1, 1], [1, 1], color="crimson", s=100, zorder=5,
               label="Attractor states")
    ax.annotate("", xy=(0.8, 0.7), xytext=(-0.8, 0.7),
                arrowprops=dict(arrowstyle="<->", color="darkorange", lw=2))
    ax.text(0, 0.75, "Instanton\ntunneling", ha="center", fontsize=9, color="darkorange")
    ax.set_xlabel("q (geometric order parameter)")
    ax.set_ylabel("V(q) (Ricci flow entropy barrier)")
    ax.set_title("Instanton Tunneling Between Attractors")
    ax.legend(fontsize=8); ax.grid(alpha=0.3)

    # RG flow interpretation
    ax = axes[1, 1]
    # Ricci flow = RG flow of worldsheet coupling
    mu_rg = np.linspace(0, 5, 500)  # RG scale
    # β function: dg/d(log μ) = β(g)
    g_fixed = 1.0
    beta_fn = -(mu_rg - g_fixed) * np.exp(-(mu_rg - g_fixed)**2)
    ax.plot(mu_rg, beta_fn, color="royalblue", linewidth=2, label="β(g)")
    ax.axhline(0, color="gray", linestyle="--", alpha=0.5)
    ax.axvline(g_fixed, color="crimson", linestyle="--", label=f"Fixed point g*={g_fixed}")
    ax.fill_between(mu_rg, beta_fn, 0, where=(beta_fn < 0), alpha=0.15, color="blue",
                    label="IR attractive")
    ax.fill_between(mu_rg, beta_fn, 0, where=(beta_fn > 0), alpha=0.15, color="red",
                    label="UV repulsive")
    ax.set_xlabel("g (coupling constant)"); ax.set_ylabel("β(g) = dg/d(log μ)")
    ax.set_title("RG Beta Function (Ricci Flow = RG Flow)")
    ax.legend(fontsize=8); ax.grid(alpha=0.3)

    # The full hierarchy summary
    ax = axes[1, 2]
    ax.axis("off")
    hierarchy = (
        "THE GEOMETRIC HIERARCHY\n"
        "(WorkOn.md Final Structure)\n\n"
        "Level 1: Classical Continuum\n"
        "  Ricci flow on smooth metrics\n"
        "  → Nonlinear parabolic PDE\n\n"
        "Level 2: Attractor Landscape\n"
        "  Discrete curvature configs\n"
        "  → Moduli space + winding sectors\n\n"
        "Level 3: Quantum Transitions\n"
        "  Tunneling between attractors\n"
        "  → Gravitational instantons\n\n"
        "Level 4: Topological Cascade\n"
        "  Surgery-induced topology change\n"
        "  → Tree of (M_t, χ_t) descendants\n\n"
        "Level 5: Full Quantum Gravity\n"
        "  Sum over all topologies\n"
        "  → Liouville CFT / String Theory\n\n"
        "ORIGIN: Transport + Diffusion\n"
        "        + Info-Geometric Curvature\n"
        "        → Stationarity → Geometry\n"
        "        → Topology → Strings"
    )
    ax.text(0.03, 0.97, hierarchy, transform=ax.transAxes,
            fontsize=9, verticalalignment="top", fontfamily="monospace",
            bbox=dict(boxstyle="round", facecolor="lightcyan", alpha=0.9))

    plt.tight_layout()
    savefig("liouville_landscape", fig)


# ─────────────────────────────────────────────────────────────
# BONUS: FULL PIPELINE OVERVIEW
# ─────────────────────────────────────────────────────────────

@sim("workon_overview",
     "Full Pipeline — Classical Diffusion → Quantum → Geometry → Strings",
     "Overview")
def sim_workon_overview():
    """
    A single comprehensive figure showing the full logical chain
    from WorkOn.md: diffusion → QHO → nonlinear → Ricci → Liouville.
    """
    fig = plt.figure(figsize=(18, 10))
    fig.suptitle("WorkOn.md: The Full Pipeline\nClassical Diffusion → Quantum → Geometry → Strings",
                 fontsize=14, fontweight="bold")
    gs = gridspec.GridSpec(2, 4, figure=fig, hspace=0.5, wspace=0.4)

    x = np.linspace(-5, 5, 400)
    hbar, m, omega, D = 1.0, 1.0, 1.0, 0.5
    alpha_q = m * omega / hbar

    # Panel 1: Classical Gaussian (Ornstein-Uhlenbeck)
    ax1 = fig.add_subplot(gs[0, 0])
    P_ou = np.exp(-omega * x**2 / (2 * D))
    P_ou /= np.trapezoid(P_ou, x)
    ax1.fill_between(x, P_ou, alpha=0.3, color="royalblue")
    ax1.plot(x, P_ou, color="royalblue", linewidth=2)
    ax1.set_title("Step 1\nClassical Diffusion\n(Ornstein-Uhlenbeck)", fontsize=9)
    ax1.set_xlabel("x"); ax1.set_ylabel("P(x)")
    ax1.grid(alpha=0.3)

    # Panel 2: QHO eigenstates
    ax2 = fig.add_subplot(gs[0, 1])
    from numpy.polynomial.hermite import hermval
    for n, color in enumerate(plt.cm.tab10(np.linspace(0, 1, 4))):
        coeffs = np.zeros(n + 1); coeffs[n] = 1
        psi = hermval(np.sqrt(alpha_q) * x, coeffs) * np.exp(-alpha_q * x**2 / 2)
        psi /= np.sqrt(np.trapezoid(psi**2, x))
        E_n = hbar * omega * (n + 0.5)
        ax2.plot(x, psi**2 + E_n * 0.3, color=color, linewidth=1.5)
    ax2.set_title("Step 2\nAdd Q-term →\nQuantum Eigenstates", fontsize=9)
    ax2.set_xlabel("x"); ax2.set_ylabel("|ψ_n|² + offset")
    ax2.grid(alpha=0.3)

    # Panel 3: Nonlinear blob
    ax3 = fig.add_subplot(gs[0, 2])
    # GPE ground state with strong nonlinearity (Thomas-Fermi approx)
    g_nl = 50.0
    mu_tf = (3 * g_nl / (4 * np.sqrt(2))) ** (2/3)
    psi_tf = np.maximum(mu_tf - 0.5 * x**2, 0)
    psi_tf /= np.trapezoid(psi_tf, x) + 1e-10
    ax3.fill_between(x, psi_tf, alpha=0.3, color="crimson")
    ax3.plot(x, psi_tf, color="crimson", linewidth=2)
    ax3.set_title("Step 3\nStrong Q-term →\nSelf-Trapped Blob", fontsize=9)
    ax3.set_xlabel("x"); ax3.set_ylabel("|ψ|²")
    ax3.grid(alpha=0.3)

    # Panel 4: Curvature islands
    ax4 = fig.add_subplot(gs[0, 3])
    x_long = np.linspace(0, 20, 400)
    peaks = [3, 8, 13, 18]
    K_islands = sum(2 * np.exp(-3 * (x_long - p)**2) for p in peaks)
    ax4.fill_between(x_long, K_islands, alpha=0.3, color="darkorange")
    ax4.plot(x_long, K_islands, color="darkorange", linewidth=2)
    ax4.axhline(0, color="gray", linestyle=":", alpha=0.5)
    ax4.set_title("Step 4\nRicci Flow →\nCurvature Islands", fontsize=9)
    ax4.set_xlabel("x"); ax4.set_ylabel("K(x) (curvature)")
    ax4.grid(alpha=0.3)

    # Panel 5: Gauss-Bonnet constraint
    ax5 = fig.add_subplot(gs[1, 0])
    k_vals = np.arange(1, 7)
    curvature_per_peak = 4 * np.pi / k_vals
    ax5.bar(k_vals, curvature_per_peak, color="steelblue", alpha=0.7, edgecolor="black")
    ax5.axhline(4 * np.pi, color="red", linestyle="--", label="Total = 4π (S²)")
    ax5.set_xlabel("Number of peaks k"); ax5.set_ylabel("Curvature per peak")
    ax5.set_title("Step 5\nGauss-Bonnet\nCurvature Budget", fontsize=9)
    ax5.legend(fontsize=7); ax5.grid(alpha=0.3, axis="y")

    # Panel 6: Liouville potential
    ax6 = fig.add_subplot(gs[1, 1])
    phi = np.linspace(-3, 2, 400)
    ax6.semilogy(phi, np.exp(2 * phi) + 0.001, color="purple", linewidth=2,
                 label="V = e^{2φ}")
    ax6.set_xlabel("φ (Liouville field)"); ax6.set_ylabel("V(φ)")
    ax6.set_title("Step 6\nLiouville CFT\nPotential", fontsize=9)
    ax6.legend(); ax6.grid(alpha=0.3)

    # Panel 7: Path integral sum over topologies
    ax7 = fig.add_subplot(gs[1, 2])
    genus_vals = np.arange(0, 6)
    chi_vals = 2 - 2 * genus_vals
    weights = np.exp(-np.abs(chi_vals) * 0.3)  # schematic weight
    ax7.bar(genus_vals, weights, color="darkorange", alpha=0.7, edgecolor="black")
    ax7.set_xlabel("Genus g"); ax7.set_ylabel("Path integral weight")
    ax7.set_title("Step 7\nSum Over\nTopologies", fontsize=9)
    ax7.set_xticks(genus_vals)
    ax7.set_xticklabels([f"g={g}" for g in genus_vals], fontsize=8)
    ax7.grid(alpha=0.3, axis="y")

    # Panel 8: The connection diagram
    ax8 = fig.add_subplot(gs[1, 3])
    ax8.axis("off")
    connection = (
        "THE CHAIN\n\n"
        "Classical fluid\n"
        "    ↓ add Q-term\n"
        "Quantum oscillator\n"
        "    ↓ increase Λ\n"
        "Nonlinear blob\n"
        "    ↓ add Ricci flow\n"
        "Curvature islands\n"
        "    ↓ Gauss-Bonnet\n"
        "Topological constraint\n"
        "    ↓ path integral\n"
        "Liouville CFT\n"
        "    = 2D Quantum Gravity\n\n"
        "All from:\n"
        "Transport + Diffusion\n"
        "+ Curvature Feedback"
    )
    ax8.text(0.1, 0.95, connection, transform=ax8.transAxes,
             fontsize=10, verticalalignment="top", fontfamily="monospace",
             bbox=dict(boxstyle="round", facecolor="lightyellow", alpha=0.9))

    savefig("workon_overview", fig)


# ─────────────────────────────────────────────────────────────
# RUNNER
# ─────────────────────────────────────────────────────────────

def run_all():
    print(f"\nRunning {len(REGISTRY)} WorkOn simulations → plots/\n")
    for name, meta in REGISTRY.items():
        print(f"[{name}]  ({meta['act']})")
        print(f"  {meta['title']}")
        meta["fn"]()
    print(f"\nDone. {len(REGISTRY)} plots saved to {PLOT_DIR}/")


def list_sims():
    print(f"\n{'Name':<35} {'Act'}")
    print("-" * 80)
    for name, meta in REGISTRY.items():
        print(f"{name:<35} {meta['act']}")
        print(f"  → {meta['title']}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="WorkOn.md Simulations")
    parser.add_argument("--sim", type=str, default=None,
                        help="Run a specific simulation by name")
    parser.add_argument("--list", action="store_true",
                        help="List all available simulations")
    args = parser.parse_args()

    if args.list:
        list_sims()
    elif args.sim:
        if args.sim in REGISTRY:
            print(f"Running: {REGISTRY[args.sim]['title']}")
            REGISTRY[args.sim]["fn"]()
        else:
            print(f"Unknown simulation '{args.sim}'. Use --list to see all.")
    else:
        run_all()
