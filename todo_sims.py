"""
todo_sims.py
Extracted and cleaned simulation code from Todo.md.

Simulates the full Quantum → Nonlinear Attractor → Chaotic hierarchy
from the Unified Geometric System (UnifiedGeometricSystem class).

The single control parameter Λ governs all three regimes:
  Λ < 0.5   → Linear quantum (harmonic oscillator)
  0.5–5.0   → Nonlinear attractor (self-trapped blobs)
  Λ > 5.0   → Chaotic (Lorenz-like folding dynamics)

Run all:      python todo_sims.py
Run one:      python todo_sims.py --sim quantum_to_chaos
List all:     python todo_sims.py --list
"""

import argparse
import os
import warnings
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from scipy.integrate import solve_ivp
from scipy.sparse import diags

warnings.filterwarnings("ignore")

PLOT_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "plots")
os.makedirs(PLOT_DIR, exist_ok=True)

REGISTRY: dict = {}


def sim(name: str, title: str):
    def decorator(fn):
        REGISTRY[name] = {"fn": fn, "title": title}
        return fn
    return decorator


def savefig(name: str, fig=None):
    path = os.path.join(PLOT_DIR, f"{name}.png")
    (fig or plt).savefig(path, dpi=150, bbox_inches="tight")
    plt.close("all")
    print(f"  saved → plots/{name}.png")


# ─────────────────────────────────────────────────────────────
# CORE CLASS: UnifiedGeometricSystem
# ─────────────────────────────────────────────────────────────

class UnifiedGeometricSystem:
    """
    Simulates the full hierarchy from Todo.md:
      Quantum Harmonic Oscillator → Q-dominant attractors → Chaotic regime

    The master action:
      S[g, ψ, A] = ∫ √g [ ħ²/2m |∇ψ|² + ½ R ψ² + V(ψ) + L_transport ] d²x

    Control parameter Λ = |∇·v| <ψ²> / |<ħ²/2m ∇²ψ>|
    """

    def __init__(
        self,
        N=128,
        L=10.0,
        hbar2_over_2m=0.5,
        omega=1.0,
        alpha=-0.1,
        beta=0.5,
        D=0.1,
        transport_type="harmonic",
    ):
        self.N = N
        self.L = L
        self.x = np.linspace(-L, L, N)
        self.dx = self.x[1] - self.x[0]

        self.hbar2_over_2m = hbar2_over_2m
        self.omega = omega
        self.alpha = alpha
        self.beta = beta
        self.D = D
        self.transport_type = transport_type

        self._build_operators()
        self.psi = self._initialize_gaussian()
        self.t = 0.0
        self.history = []
        self.Lambda = 0.0

    def _build_operators(self):
        N, dx = self.N, self.dx
        # Second derivative (finite difference)
        main = -2.0 / dx**2 * np.ones(N)
        off  =  1.0 / dx**2 * np.ones(N - 1)
        self.D2 = diags([off, main, off], [-1, 0, 1]).toarray()
        # First derivative (centered)
        off1 = 0.5 / dx * np.ones(N - 1)
        self.D1 = diags([-off1, np.zeros(N), off1], [-1, 0, 1]).toarray()
        # Transport velocity field
        if self.transport_type == "harmonic":
            self.v = -self.omega * self.x
            self.div_v = -self.omega * np.ones(N)
        elif self.transport_type == "lorenz_like":
            sigma, rho, b = 10.0, 28.0, 8.0 / 3.0
            # Project Lorenz onto 1D using x-component of the flow
            self.v = sigma * (np.sin(self.x) - self.x)
            self.div_v = sigma * (np.cos(self.x) - 1.0)
        else:
            self.v = -self.omega * self.x
            self.div_v = -self.omega * np.ones(N)

    def _initialize_gaussian(self):
        psi = np.exp(-self.x**2 / 2.0)
        return psi / np.sqrt(np.sum(psi**2) * self.dx)

    def _compute_Q(self, psi):
        """Curvature term Q(ψ) = -ħ²/2m · ∇²ψ / ψ"""
        psi_safe = np.where(np.abs(psi) > 1e-12, psi, 1e-12)
        lap_psi = self.D2 @ psi
        return -self.hbar2_over_2m * lap_psi / psi_safe

    def _compute_metric(self, psi):
        """Conformal factor Ω² = 1 + α ψ²"""
        return 1.0 + self.alpha * psi**2

    def compute_Lambda(self):
        """Λ = 2ω <ψ²> / |<ħ²/2m ψ''>|  (evaluated at density peak)"""
        psi_sq = self.psi**2
        peak_idx = np.argmax(psi_sq)
        psi_peak = np.abs(self.psi[peak_idx])
        lap_psi = self.D2 @ self.psi
        kinetic_peak = np.abs(self.hbar2_over_2m * lap_psi[peak_idx])
        transport_peak = np.abs(self.div_v[peak_idx]) * psi_sq[peak_idx]
        return transport_peak / (kinetic_peak / (psi_peak + 1e-12) + 1e-12)

    def _rhs(self, psi):
        """RHS of the coupled PDE:
        ∂ψ/∂t = -v·∇ψ - ½(∇·v)ψ + D∇²ψ - β/2α ψ(1 + αψ²)
        """
        grad_psi = self.D1 @ psi
        lap_psi  = self.D2 @ psi
        # Transport
        transport = -self.v * grad_psi - 0.5 * self.div_v * psi
        # Diffusion
        diffusion = self.D * lap_psi
        # Ricci flow / reaction term
        if abs(self.alpha) > 1e-10:
            reaction = -(self.beta / (2 * self.alpha)) * psi * (1 + self.alpha * psi**2)
        else:
            reaction = np.zeros_like(psi)
        return transport + diffusion + reaction

    def run_simulation(self, n_steps=300, dt=0.005, method="ricci_flow"):
        # Adaptive dt: ensure diffusion stability D*dt/dx^2 < 0.4
        dt_stable = 0.4 * self.dx**2 / max(self.D, 1e-6)
        dt = min(dt, dt_stable)
        self.history = []
        for step in range(n_steps + 1):
            # Record
            if step % max(1, n_steps // 200) == 0:
                self.Lambda = self.compute_Lambda()
                self.history.append({
                    "t":      self.t,
                    "psi":    self.psi.copy(),
                    "psi_sq": self.psi**2,
                    "metric": self._compute_metric(self.psi),
                    "Lambda": self.Lambda,
                })
            # RK4 step for stability
            k1 = self._rhs(self.psi)
            k2 = self._rhs(self.psi + 0.5 * dt * k1)
            k3 = self._rhs(self.psi + 0.5 * dt * k2)
            k4 = self._rhs(self.psi + dt * k3)
            self.psi = self.psi + (dt / 6.0) * (k1 + 2*k2 + 2*k3 + k4)
            # Clip and renormalize
            self.psi = np.clip(self.psi, -1e4, 1e4)
            norm = np.sqrt(np.sum(self.psi**2) * self.dx)
            if norm > 1e-12:
                self.psi /= norm
            self.t += dt

    def solve_lorenz_trajectory(self, n_steps=5000, dt=0.01):
        """Integrate the classic Lorenz ODE for reference."""
        sigma, rho, b = 10.0, 28.0, 8.0 / 3.0

        def lorenz(t, state):
            x, y, z = state
            return [sigma * (y - x), x * (rho - z) - y, x * y - b * z]

        sol = solve_ivp(
            lorenz,
            [0, n_steps * dt],
            [1.0, 0.0, 0.0],
            t_eval=np.linspace(0, n_steps * dt, n_steps),
            method="RK45",
            rtol=1e-8,
        )
        return sol.y.T  # shape (n_steps, 3)

    def analyze_transition(self):
        lambdas = np.array([h["Lambda"] for h in self.history])
        dt_hist = self.history[1]["t"] - self.history[0]["t"] if len(self.history) > 1 else 0
        return {
            "final_Lambda":      lambdas[-1],
            "time_in_linear":    np.sum(lambdas < 0.5) * dt_hist,
            "time_in_nonlinear": np.sum((lambdas >= 0.5) & (lambdas < 5.0)) * dt_hist,
            "time_in_chaotic":   np.sum(lambdas >= 5.0) * dt_hist,
            "attractor_type":    ("chaotic" if lambdas[-1] > 5.0
                                  else "nonlinear" if lambdas[-1] > 0.5
                                  else "linear"),
        }


# ─────────────────────────────────────────────────────────────
# SIM 1: QUANTUM-TO-CHAOS TRANSITION
# ─────────────────────────────────────────────────────────────

@sim("quantum_to_chaos",
     "Full Hierarchy: Quantum HO → Nonlinear Attractor → Chaotic Regime")
def sim_quantum_to_chaos():
    """
    Runs three systems at different coupling strengths and plots:
    - Λ evolution over time for each regime
    - Density evolution in each regime
    - Effective metric (geometry) at final time
    - Lorenz attractor reference
    """
    N, L = 128, 8.0

    configs = {
        "Linear (Quantum HO)": dict(
            alpha=0.01, beta=0.01, hbar2_over_2m=1.0, omega=1.0, D=0.8,
            transport_type="harmonic"),
        "Nonlinear Attractor": dict(
            alpha=-0.3, beta=0.3, hbar2_over_2m=0.5, omega=1.0, D=0.15,
            transport_type="harmonic"),
        "Chaotic (Lorenz-like)": dict(
            alpha=-2.0, beta=2.0, hbar2_over_2m=0.1, omega=1.5, D=0.01,
            transport_type="lorenz_like"),
    }
    colors = {
        "Linear (Quantum HO)":    "royalblue",
        "Nonlinear Attractor":    "darkorange",
        "Chaotic (Lorenz-like)":  "crimson",
    }

    print("  Running three coupled systems (this takes ~30s)...")
    results = {}
    for name, cfg in configs.items():
        sys = UnifiedGeometricSystem(N=N, L=L, **cfg)
        sys.run_simulation(n_steps=300, dt=0.005)
        analysis = sys.analyze_transition()
        results[name] = {"system": sys, "analysis": analysis}
        print(f"    {name}: Λ_final={analysis['final_Lambda']:.3f}  "
              f"type={analysis['attractor_type']}")

    # Lorenz trajectory
    lorenz_ref = UnifiedGeometricSystem(N=N, L=L)
    lorenz_traj = lorenz_ref.solve_lorenz_trajectory(n_steps=5000)

    fig = plt.figure(figsize=(16, 12))
    fig.suptitle("Quantum-to-Chaos Transition: One System, Three Regimes",
                 fontsize=14, fontweight="bold")

    # 1. Lambda evolution
    ax1 = fig.add_subplot(2, 3, 1)
    for name, res in results.items():
        lambdas = [h["Lambda"] for h in res["system"].history]
        times   = [h["t"]      for h in res["system"].history]
        ax1.semilogy(times, np.maximum(lambdas, 1e-4), color=colors[name],
                     label=name, linewidth=2)
    ax1.axhline(0.5, color="gray", linestyle="--", alpha=0.6, label="Linear/NL boundary")
    ax1.axhline(5.0, color="gray", linestyle=":",  alpha=0.6, label="Chaotic threshold")
    ax1.fill_between([0, 1.5], 1e-4, 0.5, alpha=0.07, color="royalblue")
    ax1.fill_between([0, 1.5], 0.5,  5.0, alpha=0.07, color="darkorange")
    ax1.fill_between([0, 1.5], 5.0,  1e3, alpha=0.07, color="crimson")
    ax1.set_xlabel("Time"); ax1.set_ylabel("Λ (control parameter)")
    ax1.set_title("Control Parameter Λ Over Time")
    ax1.legend(fontsize=7); ax1.grid(alpha=0.3)

    # 2–4. Density evolution per regime
    for col, (name, res) in enumerate(results.items(), start=2):
        ax = fig.add_subplot(2, 3, col)
        sys = res["system"]
        n_hist = len(sys.history)
        steps = [0, n_hist // 4, n_hist // 2, -1]
        for i, step in enumerate(steps):
            h = sys.history[step]
            ax.plot(sys.x, h["psi_sq"], linewidth=1.8,
                    alpha=0.3 + 0.7 * i / 3,
                    color=colors[name],
                    label=f"t={h['t']:.1f}")
        ax.set_xlabel("x"); ax.set_ylabel("|ψ|²")
        ax.set_title(name); ax.legend(fontsize=7); ax.grid(alpha=0.3)

    # 5. Effective metric at final time
    ax5 = fig.add_subplot(2, 3, 5)
    for name, res in results.items():
        metric = res["system"].history[-1]["metric"]
        ax5.plot(res["system"].x, metric, color=colors[name],
                 linewidth=2, label=name)
    ax5.axhline(1.0, color="black", linestyle="--", alpha=0.5, label="Flat (Ω²=1)")
    ax5.axhline(0.0, color="red",   linestyle=":",  alpha=0.5, label="Degenerate")
    ax5.set_xlabel("x"); ax5.set_ylabel("Ω² (conformal factor)")
    ax5.set_title("Effective Geometry at Final Time")
    ax5.legend(fontsize=7); ax5.grid(alpha=0.3)

    # 6. Lorenz attractor reference
    ax6 = fig.add_subplot(2, 3, 6, projection="3d")
    ax6.plot(lorenz_traj[:, 0], lorenz_traj[:, 1], lorenz_traj[:, 2],
             color="purple", linewidth=0.4, alpha=0.6)
    ax6.set_xlabel("X"); ax6.set_ylabel("Y"); ax6.set_zlabel("Z")
    ax6.set_title("Lorenz Attractor (Reference)")

    plt.tight_layout()
    savefig("quantum_to_chaos", fig)


# ─────────────────────────────────────────────────────────────
# SIM 2: PHASE DIAGRAM (α vs Λ)
# ─────────────────────────────────────────────────────────────

@sim("phase_diagram",
     "Phase Diagram: Metric Coupling α vs Control Parameter Λ")
def sim_phase_diagram():
    """
    Sweeps α from -3 to +3 and measures the final Λ for each,
    revealing the three-regime phase structure.
    """
    print("  Sweeping α (100 points × 50 steps each)...")
    alpha_vals = np.linspace(-3, 3, 60)
    Lambda_vals = []
    for alpha in alpha_vals:
        sys = UnifiedGeometricSystem(
            N=64, L=5.0, alpha=alpha, beta=abs(alpha) + 0.1,
            hbar2_over_2m=0.5, omega=1.0, D=0.1)
        sys.run_simulation(n_steps=50, dt=0.01)
        Lambda_vals.append(sys.compute_Lambda())
    Lambda_vals = np.array(Lambda_vals)

    fig, axes = plt.subplots(1, 2, figsize=(13, 5))
    fig.suptitle("Phase Diagram: Metric Coupling α → Dynamical Regime",
                 fontsize=13, fontweight="bold")

    ax = axes[0]
    ax.plot(alpha_vals, Lambda_vals, linewidth=2.5, color="darkblue")
    ax.axhline(0.5, color="green", linestyle="--", linewidth=1.5,
               label="Linear / Nonlinear boundary (Λ=0.5)")
    ax.axhline(5.0, color="red",   linestyle="--", linewidth=1.5,
               label="Chaotic threshold (Λ=5.0)")
    ax.fill_between(alpha_vals, 0,   0.5,
                    alpha=0.12, color="royalblue",  label="Linear quantum regime")
    ax.fill_between(alpha_vals, 0.5, 5.0,
                    alpha=0.12, color="darkorange",  label="Nonlinear attractor regime")
    ax.fill_between(alpha_vals, 5.0, np.maximum(Lambda_vals, 5.0) * 1.2,
                    alpha=0.12, color="crimson",     label="Chaotic regime")
    ax.set_xlabel("α (metric coupling)"); ax.set_ylabel("Λ (control parameter)")
    ax.set_title("Λ vs α: The Three-Regime Phase Diagram")
    ax.legend(fontsize=8); ax.grid(alpha=0.3)
    ax.set_yscale("log")
    ax.set_ylim(1e-3, max(Lambda_vals) * 2)

    # Regime classification bar
    ax2 = axes[1]
    regime_colors = []
    for lam in Lambda_vals:
        if lam < 0.5:
            regime_colors.append("royalblue")
        elif lam < 5.0:
            regime_colors.append("darkorange")
        else:
            regime_colors.append("crimson")
    ax2.bar(alpha_vals, Lambda_vals, width=(alpha_vals[1] - alpha_vals[0]),
            color=regime_colors, alpha=0.8, edgecolor="none")
    ax2.axhline(0.5, color="green", linestyle="--", linewidth=1.5)
    ax2.axhline(5.0, color="red",   linestyle="--", linewidth=1.5)
    from matplotlib.patches import Patch
    legend_elements = [
        Patch(facecolor="royalblue",  label="Linear quantum"),
        Patch(facecolor="darkorange", label="Nonlinear attractor"),
        Patch(facecolor="crimson",    label="Chaotic"),
    ]
    ax2.legend(handles=legend_elements, fontsize=9)
    ax2.set_xlabel("α (metric coupling)"); ax2.set_ylabel("Λ")
    ax2.set_title("Regime Classification by α")
    ax2.set_yscale("log"); ax2.grid(alpha=0.3)
    ax2.set_ylim(1e-3, max(Lambda_vals) * 2)

    savefig("phase_diagram", fig)


# ─────────────────────────────────────────────────────────────
# SIM 3: LORENZ-PDE ISOMORPHISM
# ─────────────────────────────────────────────────────────────

@sim("lorenz_pde_isomorphism",
     "Lorenz–PDE Isomorphism: Structural Equivalence Visualization")
def sim_lorenz_pde_isomorphism():
    """
    Side-by-side comparison of:
    - Lorenz attractor (classic ODE)
    - PDE density in chaotic regime
    - Perron-Frobenius spectrum comparison
    """
    # Lorenz trajectory
    sigma, rho, b = 10.0, 28.0, 8.0 / 3.0

    def lorenz_ode(t, state):
        x, y, z = state
        return [sigma * (y - x), x * (rho - z) - y, x * y - b * z]

    sol = solve_ivp(lorenz_ode, [0, 50], [1.0, 0.0, 0.0],
                    t_eval=np.linspace(0, 50, 8000), method="RK45", rtol=1e-8)
    traj = sol.y.T

    # PDE in chaotic regime
    sys_chaos = UnifiedGeometricSystem(
        N=128, L=8.0, alpha=-2.0, beta=2.0,
        hbar2_over_2m=0.1, omega=1.5, D=0.01,
        transport_type="lorenz_like")
    sys_chaos.run_simulation(n_steps=400, dt=0.005)

    fig = plt.figure(figsize=(16, 10))
    fig.suptitle("Lorenz–PDE Isomorphism: Two Systems, One Structure",
                 fontsize=13, fontweight="bold")

    # Lorenz 3D
    ax1 = fig.add_subplot(2, 3, 1, projection="3d")
    ax1.plot(traj[:, 0], traj[:, 1], traj[:, 2],
             color="purple", linewidth=0.4, alpha=0.7)
    ax1.set_xlabel("X"); ax1.set_ylabel("Y"); ax1.set_zlabel("Z")
    ax1.set_title("Lorenz Attractor (ODE)")

    # Lorenz X-Y projection
    ax2 = fig.add_subplot(2, 3, 2)
    ax2.plot(traj[:, 0], traj[:, 1], color="purple", linewidth=0.3, alpha=0.5)
    ax2.set_xlabel("X"); ax2.set_ylabel("Y")
    ax2.set_title("Lorenz X-Y Projection (Möbius-like twist)")
    ax2.grid(alpha=0.3)

    # Lorenz X time series
    ax3 = fig.add_subplot(2, 3, 3)
    ax3.plot(sol.t[:2000], traj[:2000, 0], color="purple", linewidth=0.8)
    ax3.set_xlabel("t"); ax3.set_ylabel("X(t)")
    ax3.set_title("Lorenz X(t): Sensitive Dependence")
    ax3.grid(alpha=0.3)

    # PDE density evolution (chaotic)
    ax4 = fig.add_subplot(2, 3, 4)
    n_hist = len(sys_chaos.history)
    for i, step in enumerate([0, n_hist // 4, n_hist // 2, -1]):
        h = sys_chaos.history[step]
        ax4.plot(sys_chaos.x, h["psi_sq"], linewidth=1.5,
                 alpha=0.3 + 0.7 * i / 3, label=f"t={h['t']:.2f}")
    ax4.set_xlabel("x"); ax4.set_ylabel("|ψ|²")
    ax4.set_title("PDE Density (Chaotic Regime)")
    ax4.legend(fontsize=7); ax4.grid(alpha=0.3)

    # PDE metric evolution (chaotic)
    ax5 = fig.add_subplot(2, 3, 5)
    for i, step in enumerate([0, n_hist // 4, n_hist // 2, -1]):
        h = sys_chaos.history[step]
        ax5.plot(sys_chaos.x, h["metric"], linewidth=1.5,
                 alpha=0.3 + 0.7 * i / 3, label=f"t={h['t']:.2f}")
    ax5.axhline(1.0, color="gray", linestyle="--", alpha=0.5, label="Flat")
    ax5.axhline(0.0, color="red",  linestyle=":",  alpha=0.5, label="Degenerate")
    ax5.set_xlabel("x"); ax5.set_ylabel("Ω²(x,t)")
    ax5.set_title("Effective Metric (Chaotic Regime)")
    ax5.legend(fontsize=7); ax5.grid(alpha=0.3)

    # Correspondence table
    ax6 = fig.add_subplot(2, 3, 6)
    ax6.axis("off")
    table_data = [
        ["PDE Term",                "Lorenz ODE",           "Role"],
        ["Transport ∇·(vP)",        "σ(y-x), x(ρ-z)-y",    "Deterministic drift"],
        ["Diffusion D∇²P",          "-βz term",             "Damping / relaxation"],
        ["Curvature Q(P)",          "xy nonlinearity",      "Self-reinforcing fold"],
        ["Normalization ∫P=1",      "Bounded attractor",    "Global confinement"],
        ["Bifurcation Λ~1",         "Hopf at ρ=1",          "Loss of fixed point"],
        ["Attractor landscape",     "Strange attractor",    "Geometric invariant"],
    ]
    col_widths = [0.38, 0.35, 0.27]
    y_pos = 0.95
    for row in table_data:
        x_pos = 0.02
        bold = (row == table_data[0])
        for cell, w in zip(row, col_widths):
            ax6.text(x_pos, y_pos, cell, transform=ax6.transAxes,
                     fontsize=8, fontweight="bold" if bold else "normal",
                     verticalalignment="top",
                     bbox=dict(boxstyle="round,pad=0.2",
                               facecolor="lightcyan" if bold else "white",
                               alpha=0.8) if bold else None)
            x_pos += w
        y_pos -= 0.13
    ax6.set_title("Structural Isomorphism Table", fontsize=10, fontweight="bold")

    plt.tight_layout()
    savefig("lorenz_pde_isomorphism", fig)


# ─────────────────────────────────────────────────────────────
# SIM 4: UNIFIED ACTION — REGIME TRANSITIONS
# ─────────────────────────────────────────────────────────────

@sim("unified_action_regimes",
     "Unified Action Functional: Density Bifurcation Across Regimes")
def sim_unified_action_regimes():
    """
    Sweeps Λ continuously and shows how the density profile
    bifurcates from Gaussian → multi-peak → chaotic.
    """
    print("  Sweeping coupling strength (12 systems)...")
    N, L = 128, 8.0
    # Vary alpha to sweep Λ
    alpha_sweep = [-0.05, -0.1, -0.2, -0.4, -0.6, -0.8,
                   -1.0,  -1.2, -1.5, -1.8, -2.2, -3.0]
    beta_sweep  = [abs(a) * 0.5 for a in alpha_sweep]

    fig, axes = plt.subplots(3, 4, figsize=(16, 11))
    fig.suptitle("Unified Action: Density Bifurcation as Λ Increases",
                 fontsize=13, fontweight="bold")

    for idx, (alpha, beta) in enumerate(zip(alpha_sweep, beta_sweep)):
        row, col = divmod(idx, 4)
        ax = axes[row, col]
        sys = UnifiedGeometricSystem(
            N=N, L=L, alpha=alpha, beta=beta,
            hbar2_over_2m=0.5, omega=1.0, D=0.1)
        sys.run_simulation(n_steps=200, dt=0.005)
        Lambda_final = sys.compute_Lambda()

        # Color by regime
        if Lambda_final < 0.5:
            color = "royalblue"
            regime = "Linear"
        elif Lambda_final < 5.0:
            color = "darkorange"
            regime = "Nonlinear"
        else:
            color = "crimson"
            regime = "Chaotic"

        # Initial vs final density
        ax.fill_between(sys.x, sys.history[0]["psi_sq"],
                        alpha=0.2, color="gray", label="t=0")
        ax.plot(sys.x, sys.history[-1]["psi_sq"],
                color=color, linewidth=2, label=f"t_final")
        ax.set_title(f"α={alpha:.2f}  Λ={Lambda_final:.2f}\n[{regime}]",
                     fontsize=8)
        ax.set_xlabel("x", fontsize=7); ax.set_ylabel("|ψ|²", fontsize=7)
        ax.tick_params(labelsize=6); ax.grid(alpha=0.3)
        ax.set_xlim(-L, L)

    plt.tight_layout()
    savefig("unified_action_regimes", fig)


# ─────────────────────────────────────────────────────────────
# RUNNER
# ─────────────────────────────────────────────────────────────

def run_all():
    print(f"\nRunning {len(REGISTRY)} Todo simulations → plots/\n")
    for name, meta in REGISTRY.items():
        print(f"[{name}]")
        print(f"  {meta['title']}")
        meta["fn"]()
    print(f"\nDone. {len(REGISTRY)} plots saved to {PLOT_DIR}/")


def list_sims():
    print(f"\n{'Name':<35} Title")
    print("-" * 80)
    for name, meta in REGISTRY.items():
        print(f"{name:<35} {meta['title']}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Todo.md Simulations")
    parser.add_argument("--sim",  type=str, default=None,
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
