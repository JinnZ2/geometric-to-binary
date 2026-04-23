"""
sims.py
Numerical simulations for the Geometric-to-Binary equation registry.

Each simulation corresponds to one or more equations in physics_playground.py.
All simulations produce matplotlib figures saved to the /plots/ directory.

Run all:   python sims.py
Run one:   python sims.py --sim lorenz
List all:  python sims.py --list
"""

import argparse
import os
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import matplotlib.gridspec as gridspec
from matplotlib.colors import LogNorm
from scipy.integrate import solve_ivp, odeint
from scipy.fft import fft, fftfreq

PLOT_DIR = os.path.join(os.path.dirname(__file__), "plots")
os.makedirs(PLOT_DIR, exist_ok=True)

# ─────────────────────────────────────────────────────────────
# HELPERS
# ─────────────────────────────────────────────────────────────

def savefig(name: str, fig=None):
    path = os.path.join(PLOT_DIR, f"{name}.png")
    (fig or plt).savefig(path, dpi=150, bbox_inches="tight")
    plt.close("all")
    print(f"  saved → plots/{name}.png")


REGISTRY: dict = {}

def sim(name: str, title: str, domains: list):
    """Decorator to register a simulation."""
    def decorator(fn):
        REGISTRY[name] = {"fn": fn, "title": title, "domains": domains}
        return fn
    return decorator


# ─────────────────────────────────────────────────────────────
# 1. CLASSICAL MECHANICS
# ─────────────────────────────────────────────────────────────

@sim("harmonic_oscillator", "Harmonic Oscillator — Phase Portrait & Time Series",
     ["classical_mechanics"])
def sim_harmonic_oscillator():
    """
    Equations: harmonic_oscillator, energy_conservation
    x'' + omega^2 x = 0
    """
    omega = 2 * np.pi  # 1 Hz
    t = np.linspace(0, 4, 1000)

    fig, axes = plt.subplots(1, 3, figsize=(15, 4))
    fig.suptitle("Harmonic Oscillator", fontsize=14, fontweight="bold")

    for ax, (x0, v0, label) in zip(axes, [
        (1.0, 0.0, "x₀=1, v₀=0"),
        (0.5, 1.5, "x₀=0.5, v₀=1.5"),
        (0.0, 2.0, "x₀=0, v₀=2"),
    ]):
        x = x0 * np.cos(omega * t) + (v0 / omega) * np.sin(omega * t)
        v = -x0 * omega * np.sin(omega * t) + v0 * np.cos(omega * t)
        ax.plot(t, x, label="position x(t)")
        ax.plot(t, v, label="velocity v(t)", linestyle="--")
        ax.set_title(label)
        ax.set_xlabel("time (s)")
        ax.legend(fontsize=8)
        ax.grid(alpha=0.3)

    savefig("harmonic_oscillator", fig)


@sim("pendulum", "Nonlinear Pendulum — Small vs Large Angle",
     ["classical_mechanics"])
def sim_pendulum():
    """
    Equations: newton_2 applied to pendulum
    theta'' + (g/L) sin(theta) = 0
    """
    g, L = 9.81, 1.0
    omega0_sq = g / L

    def pendulum_ode(t, y):
        theta, omega = y
        return [omega, -omega0_sq * np.sin(theta)]

    t_span = (0, 10)
    t_eval = np.linspace(*t_span, 2000)

    fig, axes = plt.subplots(1, 2, figsize=(13, 5))
    fig.suptitle("Nonlinear Pendulum", fontsize=14, fontweight="bold")

    colors = plt.cm.viridis(np.linspace(0.1, 0.9, 5))
    angles = [5, 30, 60, 90, 150]

    for theta0_deg, color in zip(angles, colors):
        theta0 = np.radians(theta0_deg)
        sol = solve_ivp(pendulum_ode, t_span, [theta0, 0], t_eval=t_eval, rtol=1e-9)
        axes[0].plot(sol.t, np.degrees(sol.y[0]), label=f"θ₀={theta0_deg}°", color=color)
        axes[1].plot(np.degrees(sol.y[0]), sol.y[1], color=color, alpha=0.8)

    axes[0].set_xlabel("time (s)"); axes[0].set_ylabel("θ (degrees)")
    axes[0].set_title("Time Series"); axes[0].legend(fontsize=8); axes[0].grid(alpha=0.3)
    axes[1].set_xlabel("θ (degrees)"); axes[1].set_ylabel("ω (rad/s)")
    axes[1].set_title("Phase Portrait"); axes[1].grid(alpha=0.3)

    savefig("pendulum", fig)


# ─────────────────────────────────────────────────────────────
# 2. ELECTROMAGNETISM
# ─────────────────────────────────────────────────────────────

@sim("wave_propagation", "Electromagnetic Wave Propagation",
     ["electromagnetism"])
def sim_wave_propagation():
    """
    Equation: wave_equation_1d
    E(x,t) = E0 * cos(kx - omega*t)
    """
    c = 3e8
    freq = 1e9  # 1 GHz
    omega = 2 * np.pi * freq
    k = omega / c
    lam = c / freq

    x = np.linspace(0, 3 * lam, 500)
    t_vals = np.linspace(0, 2 / freq, 6)

    fig, axes = plt.subplots(1, 2, figsize=(13, 5))
    fig.suptitle("EM Wave Propagation (1 GHz)", fontsize=14, fontweight="bold")

    colors = plt.cm.plasma(np.linspace(0.1, 0.9, len(t_vals)))
    for t_val, color in zip(t_vals, colors):
        E = np.cos(k * x - omega * t_val)
        axes[0].plot(x / lam, E, color=color, alpha=0.8,
                     label=f"t={t_val * freq:.2f}/f")

    axes[0].set_xlabel("x / λ"); axes[0].set_ylabel("E (normalized)")
    axes[0].set_title("Snapshots in Time"); axes[0].legend(fontsize=7)
    axes[0].grid(alpha=0.3)

    # Poynting vector magnitude (E × B, proportional to E^2)
    x_fine = np.linspace(0, 3 * lam, 300)
    t_fine = np.linspace(0, 2 / freq, 300)
    X, T = np.meshgrid(x_fine / lam, t_fine * freq)
    S = np.cos(2 * np.pi * X - 2 * np.pi * T) ** 2
    im = axes[1].contourf(X, T, S, levels=50, cmap="inferno")
    fig.colorbar(im, ax=axes[1], label="|S| (normalized)")
    axes[1].set_xlabel("x / λ"); axes[1].set_ylabel("t × f")
    axes[1].set_title("Poynting Flux Density")

    savefig("wave_propagation", fig)


# ─────────────────────────────────────────────────────────────
# 3. QUANTUM MECHANICS
# ─────────────────────────────────────────────────────────────

@sim("quantum_particle_in_box", "Quantum Particle in a Box — Wavefunctions & Energies",
     ["quantum"])
def sim_quantum_pib():
    """
    Equations: schrodinger_free, qho_energy_levels
    ψ_n(x) = sqrt(2/L) sin(nπx/L),  E_n = n²π²ℏ²/(2mL²)
    """
    L = 1.0
    hbar = 1.0
    m = 1.0
    x = np.linspace(0, L, 500)

    fig, axes = plt.subplots(1, 2, figsize=(13, 5))
    fig.suptitle("Particle in a Box (ℏ=m=L=1)", fontsize=14, fontweight="bold")

    colors = plt.cm.tab10(np.linspace(0, 1, 6))
    for n, color in zip(range(1, 7), colors):
        psi = np.sqrt(2 / L) * np.sin(n * np.pi * x / L)
        E_n = (n ** 2 * np.pi ** 2 * hbar ** 2) / (2 * m * L ** 2)
        axes[0].plot(x, psi + E_n, color=color, label=f"n={n}, E={E_n:.1f}")
        axes[0].axhline(E_n, color=color, linestyle=":", alpha=0.5)
        axes[1].plot(x, psi ** 2, color=color, label=f"n={n}")

    axes[0].set_xlabel("x"); axes[0].set_ylabel("ψ_n(x) + E_n (offset)")
    axes[0].set_title("Wavefunctions (offset by energy)"); axes[0].legend(fontsize=7)
    axes[0].grid(alpha=0.3)
    axes[1].set_xlabel("x"); axes[1].set_ylabel("|ψ_n(x)|²")
    axes[1].set_title("Probability Densities"); axes[1].legend(fontsize=7)
    axes[1].grid(alpha=0.3)

    savefig("quantum_particle_in_box", fig)


@sim("quantum_tunneling", "Quantum Tunneling Through a Barrier",
     ["quantum"])
def sim_quantum_tunneling():
    """
    Equation: schrodinger_free
    Transmission coefficient T vs E/V0 for a rectangular barrier.
    """
    hbar = 1.0
    m = 1.0
    V0 = 10.0
    a = 1.0  # barrier width

    E_vals = np.linspace(0.01, 20, 2000)
    T = np.zeros_like(E_vals)

    for i, E in enumerate(E_vals):
        if E < V0:
            kappa = np.sqrt(2 * m * (V0 - E)) / hbar
            denom = 1 + (V0 ** 2 * np.sinh(kappa * a) ** 2) / (4 * E * (V0 - E))
            T[i] = 1.0 / denom
        else:
            k1 = np.sqrt(2 * m * E) / hbar
            k2 = np.sqrt(2 * m * (E - V0)) / hbar
            denom = 1 + ((k1 ** 2 - k2 ** 2) ** 2 * np.sin(k2 * a) ** 2) / (4 * k1 ** 2 * k2 ** 2)
            T[i] = 1.0 / denom

    fig, ax = plt.subplots(figsize=(9, 5))
    ax.plot(E_vals / V0, T, color="royalblue", linewidth=1.5)
    ax.axvline(1.0, color="red", linestyle="--", label="E = V₀ (barrier top)")
    ax.fill_between(E_vals / V0, T, where=(E_vals < V0), alpha=0.15, color="orange",
                    label="Classically forbidden region")
    ax.set_xlabel("E / V₀"); ax.set_ylabel("Transmission coefficient T")
    ax.set_title("Quantum Tunneling — Rectangular Barrier", fontweight="bold")
    ax.legend(); ax.grid(alpha=0.3)
    savefig("quantum_tunneling", fig)


# ─────────────────────────────────────────────────────────────
# 4. THERMODYNAMICS & STATISTICAL MECHANICS
# ─────────────────────────────────────────────────────────────

@sim("maxwell_boltzmann", "Maxwell-Boltzmann Speed Distribution",
     ["statistical", "thermodynamics"])
def sim_maxwell_boltzmann():
    """
    Equations: maxwell_boltzmann_speed, boltzmann_factor
    f(v) = 4π n (m/2πkT)^(3/2) v^2 exp(-mv^2/2kT)
    """
    kB = 1.38e-23
    m_H2 = 2 * 1.67e-27   # hydrogen
    m_N2 = 28 * 1.67e-27  # nitrogen
    m_Ar = 40 * 1.67e-27  # argon

    v = np.linspace(0, 3000, 2000)
    temps = [100, 300, 1000]

    fig, axes = plt.subplots(1, 2, figsize=(13, 5))
    fig.suptitle("Maxwell-Boltzmann Speed Distribution", fontsize=14, fontweight="bold")

    for T, ls in zip(temps, ["-", "--", ":"]):
        for mass, label, color in [(m_H2, "H₂", "steelblue"),
                                    (m_N2, "N₂", "darkorange"),
                                    (m_Ar, "Ar", "green")]:
            f = 4 * np.pi * (mass / (2 * np.pi * kB * T)) ** 1.5 * v ** 2 * np.exp(
                -mass * v ** 2 / (2 * kB * T))
            axes[0].plot(v, f, color=color, linestyle=ls,
                         label=f"{label} T={T}K" if T == 300 else None)

    axes[0].set_xlabel("Speed v (m/s)"); axes[0].set_ylabel("f(v)")
    axes[0].set_title("By Gas Species (solid=100K, dashed=300K, dotted=1000K)")
    axes[0].legend(fontsize=7); axes[0].grid(alpha=0.3)

    # Boltzmann factor vs energy
    E_vals = np.linspace(0, 0.5, 500)  # eV
    for T, color in [(300, "steelblue"), (1000, "darkorange"), (5000, "crimson")]:
        beta = 1 / (kB * T / 1.6e-19)  # in eV^-1
        axes[1].plot(E_vals, np.exp(-beta * E_vals),
                     label=f"T={T} K", color=color)

    axes[1].set_xlabel("Energy (eV)"); axes[1].set_ylabel("Boltzmann factor exp(-E/kT)")
    axes[1].set_title("Boltzmann Factor vs Energy"); axes[1].legend()
    axes[1].grid(alpha=0.3)

    savefig("maxwell_boltzmann", fig)


# ─────────────────────────────────────────────────────────────
# 5. FLUID DYNAMICS
# ─────────────────────────────────────────────────────────────

@sim("fluid_flow", "Fluid Flow — Velocity Profiles & Bernoulli",
     ["fluid_dynamics"])
def sim_fluid_flow():
    """
    Equations: navier_stokes_1d (Poiseuille), bernoulli
    Poiseuille: v(r) = (P1-P2)/(4μL) * (R^2 - r^2)
    Bernoulli:  P + ½ρv² + ρgh = const
    """
    fig, axes = plt.subplots(1, 2, figsize=(13, 5))
    fig.suptitle("Fluid Dynamics", fontsize=14, fontweight="bold")

    # Poiseuille flow
    R = 1.0
    r = np.linspace(-R, R, 500)
    dP_over_4muL = 1.0  # normalized
    for factor, label, color in [(1.0, "ΔP=1", "steelblue"),
                                   (2.0, "ΔP=2", "darkorange"),
                                   (4.0, "ΔP=4", "green")]:
        v = factor * dP_over_4muL * (R ** 2 - r ** 2)
        axes[0].plot(v, r, color=color, label=label)
    axes[0].set_xlabel("Velocity v(r)"); axes[0].set_ylabel("Radial position r")
    axes[0].set_title("Poiseuille Flow (pipe cross-section)")
    axes[0].legend(); axes[0].grid(alpha=0.3)

    # Bernoulli — pipe narrowing
    A1 = np.linspace(1.0, 0.2, 200)  # cross-sectional area
    rho = 1000.0  # water
    v1 = 1.0
    v2 = v1 / A1  # continuity: A1*v1 = A2*v2
    P1 = 1e5  # Pa
    P2 = P1 + 0.5 * rho * (v1 ** 2 - v2 ** 2)

    axes[1].plot(A1, P2 / 1e3, color="royalblue", label="Pressure P₂ (kPa)")
    axes[1].plot(A1, v2, color="crimson", linestyle="--", label="Velocity v₂ (m/s)")
    axes[1].set_xlabel("Pipe area A₂ (normalized)")
    axes[1].set_title("Bernoulli: Pressure vs Velocity Trade-off")
    axes[1].legend(); axes[1].grid(alpha=0.3)

    savefig("fluid_flow", fig)


# ─────────────────────────────────────────────────────────────
# 6. SPECIAL RELATIVITY
# ─────────────────────────────────────────────────────────────

@sim("special_relativity", "Special Relativity — Lorentz Factor & Mass-Energy",
     ["relativity"])
def sim_special_relativity():
    """
    Equations: lorentz_factor, relativistic_momentum, mass_energy_equivalence
    γ = 1/sqrt(1 - v²/c²),  E = γmc²
    """
    c = 1.0  # natural units
    beta = np.linspace(0, 0.9999, 2000)
    gamma = 1 / np.sqrt(1 - beta ** 2)

    fig, axes = plt.subplots(1, 2, figsize=(13, 5))
    fig.suptitle("Special Relativity", fontsize=14, fontweight="bold")

    axes[0].plot(beta, gamma, color="royalblue", linewidth=2)
    axes[0].axhline(1, color="gray", linestyle=":", alpha=0.5)
    for b_mark in [0.5, 0.9, 0.99]:
        g_mark = 1 / np.sqrt(1 - b_mark ** 2)
        axes[0].annotate(f"β={b_mark}\nγ={g_mark:.1f}",
                         xy=(b_mark, g_mark), xytext=(b_mark - 0.15, g_mark + 2),
                         arrowprops=dict(arrowstyle="->", color="gray"),
                         fontsize=8)
    axes[0].set_xlabel("β = v/c"); axes[0].set_ylabel("Lorentz factor γ")
    axes[0].set_title("Lorentz Factor"); axes[0].grid(alpha=0.3)
    axes[0].set_ylim(0, 25)

    # Relativistic vs classical kinetic energy
    m = 1.0
    KE_classical = 0.5 * m * (beta * c) ** 2
    KE_relativistic = (gamma - 1) * m * c ** 2
    axes[1].plot(beta, KE_classical, label="Classical ½mv²", color="darkorange",
                 linestyle="--")
    axes[1].plot(beta, KE_relativistic, label="Relativistic (γ-1)mc²",
                 color="royalblue")
    axes[1].set_xlabel("β = v/c"); axes[1].set_ylabel("Kinetic Energy (mc² units)")
    axes[1].set_title("Classical vs Relativistic KE"); axes[1].legend()
    axes[1].grid(alpha=0.3)

    savefig("special_relativity", fig)


# ─────────────────────────────────────────────────────────────
# 7. GENERAL RELATIVITY
# ─────────────────────────────────────────────────────────────

@sim("schwarzschild", "Schwarzschild Metric — Gravitational Time Dilation & Light Bending",
     ["general_relativity"])
def sim_schwarzschild():
    """
    Equations: schwarzschild_metric_tt, geodesic_equation
    g_tt = 1 - r_s/r,  time dilation: dt_proper = sqrt(1 - r_s/r) dt
    """
    fig, axes = plt.subplots(1, 2, figsize=(13, 5))
    fig.suptitle("Schwarzschild Spacetime", fontsize=14, fontweight="bold")

    r_s = 1.0  # Schwarzschild radius (units where r_s=1)
    r = np.linspace(1.01, 20, 2000)
    g_tt = 1 - r_s / r
    time_dilation = np.sqrt(g_tt)

    axes[0].plot(r / r_s, time_dilation, color="royalblue", linewidth=2)
    axes[0].axhline(1.0, color="gray", linestyle=":", alpha=0.5, label="Flat spacetime")
    axes[0].axvline(1.0, color="red", linestyle="--", alpha=0.7, label="Event horizon r=r_s")
    axes[0].fill_between(r / r_s, 0, time_dilation, alpha=0.1, color="royalblue")
    axes[0].set_xlabel("r / r_s"); axes[0].set_ylabel("√(1 - r_s/r)")
    axes[0].set_title("Gravitational Time Dilation"); axes[0].legend()
    axes[0].set_ylim(0, 1.1); axes[0].grid(alpha=0.3)

    # Effective potential for orbital motion
    L = 3.5  # angular momentum (units where r_s=1, c=1)
    V_eff = -r_s / (2 * r) + L ** 2 / (2 * r ** 2) - r_s * L ** 2 / (2 * r ** 3)
    axes[1].plot(r / r_s, V_eff, color="darkorange", linewidth=2)
    axes[1].axhline(0, color="gray", linestyle=":", alpha=0.5)
    axes[1].axvline(1.0, color="red", linestyle="--", alpha=0.7, label="Event horizon")
    axes[1].set_xlabel("r / r_s"); axes[1].set_ylabel("V_eff")
    axes[1].set_title("Effective Orbital Potential (L=3.5)")
    axes[1].set_ylim(-0.1, 0.05); axes[1].legend(); axes[1].grid(alpha=0.3)

    savefig("schwarzschild", fig)


# ─────────────────────────────────────────────────────────────
# 8. NONLINEAR DYNAMICS / CHAOS
# ─────────────────────────────────────────────────────────────

@sim("lorenz", "Lorenz Attractor — Deterministic Chaos",
     ["nonlinear_dynamics"])
def sim_lorenz():
    """
    Equations: lorenz_x, lyapunov_exponent
    dx/dt = σ(y-x), dy/dt = x(ρ-z)-y, dz/dt = xy - βz
    """
    sigma, rho, beta = 10.0, 28.0, 8 / 3

    def lorenz(t, state):
        x, y, z = state
        return [sigma * (y - x), x * (rho - z) - y, x * y - beta * z]

    t_span = (0, 50)
    t_eval = np.linspace(*t_span, 20000)
    sol = solve_ivp(lorenz, t_span, [1.0, 1.0, 1.0], t_eval=t_eval,
                    rtol=1e-10, atol=1e-12)

    fig = plt.figure(figsize=(15, 5))
    fig.suptitle("Lorenz Attractor (σ=10, ρ=28, β=8/3)", fontsize=14, fontweight="bold")

    ax3d = fig.add_subplot(131, projection="3d")
    ax3d.plot(sol.y[0], sol.y[1], sol.y[2], lw=0.3, color="royalblue", alpha=0.7)
    ax3d.set_xlabel("X"); ax3d.set_ylabel("Y"); ax3d.set_zlabel("Z")
    ax3d.set_title("3D Attractor")

    ax_xy = fig.add_subplot(132)
    ax_xy.plot(sol.y[0], sol.y[1], lw=0.2, color="darkorange", alpha=0.6)
    ax_xy.set_xlabel("X"); ax_xy.set_ylabel("Y"); ax_xy.set_title("X-Y Projection")
    ax_xy.grid(alpha=0.3)

    ax_t = fig.add_subplot(133)
    ax_t.plot(sol.t[:3000], sol.y[0][:3000], lw=0.8, color="crimson")
    ax_t.set_xlabel("time"); ax_t.set_ylabel("X(t)")
    ax_t.set_title("X(t) — Sensitive Dependence"); ax_t.grid(alpha=0.3)

    plt.tight_layout()
    savefig("lorenz", fig)


@sim("logistic_map", "Logistic Map — Bifurcation Diagram",
     ["nonlinear_dynamics", "population_dynamics"])
def sim_logistic_map():
    """
    Equations: logistic_map, logistic_growth
    x_{n+1} = r * x_n * (1 - x_n)
    """
    r_vals = np.linspace(2.5, 4.0, 2000)
    n_iter = 1000
    n_last = 200

    fig, axes = plt.subplots(1, 2, figsize=(14, 5))
    fig.suptitle("Logistic Map", fontsize=14, fontweight="bold")

    # Bifurcation diagram
    x = 0.5 * np.ones_like(r_vals)
    for _ in range(n_iter):
        x = r_vals * x * (1 - x)
    xs = []
    for _ in range(n_last):
        x = r_vals * x * (1 - x)
        xs.append(x.copy())
    xs = np.array(xs)

    axes[0].scatter(np.tile(r_vals, n_last), xs.ravel(),
                    s=0.02, color="royalblue", alpha=0.3)
    axes[0].set_xlabel("r"); axes[0].set_ylabel("x (long-run)")
    axes[0].set_title("Bifurcation Diagram"); axes[0].grid(alpha=0.2)

    # Time series for different r
    t = np.arange(60)
    for r_val, color in [(2.8, "green"), (3.2, "darkorange"),
                          (3.5, "royalblue"), (3.9, "crimson")]:
        x_ts = [0.5]
        for _ in t[1:]:
            x_ts.append(r_val * x_ts[-1] * (1 - x_ts[-1]))
        axes[1].plot(t, x_ts, label=f"r={r_val}", color=color, marker="o",
                     markersize=2, linewidth=1)

    axes[1].set_xlabel("iteration n"); axes[1].set_ylabel("x_n")
    axes[1].set_title("Time Series for Various r"); axes[1].legend()
    axes[1].grid(alpha=0.3)

    savefig("logistic_map", fig)


# ─────────────────────────────────────────────────────────────
# 9. ACOUSTICS
# ─────────────────────────────────────────────────────────────

@sim("acoustics", "Acoustic Wave — Fourier Decomposition & Doppler Effect",
     ["acoustics"])
def sim_acoustics():
    """
    Equations: acoustic_wave_equation, doppler_effect
    """
    fig, axes = plt.subplots(1, 2, figsize=(13, 5))
    fig.suptitle("Acoustics", fontsize=14, fontweight="bold")

    # Fourier decomposition of a square wave
    t = np.linspace(0, 2, 2000)
    f0 = 2.0
    signal = np.zeros_like(t)
    for n in range(1, 20, 2):  # odd harmonics
        signal += (4 / (np.pi * n)) * np.sin(2 * np.pi * n * f0 * t)

    axes[0].plot(t, signal, color="royalblue", linewidth=1.5, label="Fourier sum (19 terms)")
    axes[0].plot(t, np.sign(np.sin(2 * np.pi * f0 * t)), color="gray",
                 linestyle="--", alpha=0.5, label="Ideal square wave")
    axes[0].set_xlabel("time (s)"); axes[0].set_ylabel("Amplitude")
    axes[0].set_title("Fourier Decomposition of Square Wave")
    axes[0].legend(fontsize=8); axes[0].grid(alpha=0.3)

    # Doppler effect
    c_sound = 343.0  # m/s
    f_source = 440.0  # Hz (A4)
    v_source = np.linspace(-300, 300, 1000)
    f_obs_approach = f_source * c_sound / (c_sound - v_source)
    f_obs_recede   = f_source * c_sound / (c_sound + v_source)

    axes[1].plot(v_source, f_obs_approach, color="crimson", label="Observer stationary, source approaching")
    axes[1].axhline(f_source, color="gray", linestyle="--", label=f"Source freq {f_source} Hz")
    axes[1].axvline(0, color="gray", linestyle=":", alpha=0.5)
    axes[1].set_xlabel("Source velocity (m/s)"); axes[1].set_ylabel("Observed frequency (Hz)")
    axes[1].set_title("Doppler Effect (A4 = 440 Hz)")
    axes[1].legend(fontsize=8); axes[1].grid(alpha=0.3)
    axes[1].set_ylim(0, 2000)

    savefig("acoustics", fig)


# ─────────────────────────────────────────────────────────────
# 10. BIOPHYSICS
# ─────────────────────────────────────────────────────────────

@sim("diffusion", "Diffusion — Fick's Laws & Concentration Profiles",
     ["biophysics"])
def sim_diffusion():
    """
    Equations: ficks_first_law, ficks_second_law
    C(x,t) = C0 / sqrt(4πDt) * exp(-x^2 / 4Dt)
    """
    D = 1.0
    x = np.linspace(-10, 10, 500)
    t_vals = [0.1, 0.5, 1.0, 2.0, 5.0]

    fig, axes = plt.subplots(1, 2, figsize=(13, 5))
    fig.suptitle("Diffusion (Fick's Laws)", fontsize=14, fontweight="bold")

    colors = plt.cm.cool(np.linspace(0.1, 0.9, len(t_vals)))
    for t_val, color in zip(t_vals, colors):
        C = 1 / np.sqrt(4 * np.pi * D * t_val) * np.exp(-x ** 2 / (4 * D * t_val))
        axes[0].plot(x, C, color=color, label=f"t={t_val}")

    axes[0].set_xlabel("x"); axes[0].set_ylabel("C(x,t)")
    axes[0].set_title("Concentration Profile Spreading Over Time")
    axes[0].legend(fontsize=8); axes[0].grid(alpha=0.3)

    # Flux J = -D dC/dx
    t_fixed = 1.0
    C_fixed = 1 / np.sqrt(4 * np.pi * D * t_fixed) * np.exp(-x ** 2 / (4 * D * t_fixed))
    J = -D * np.gradient(C_fixed, x)
    axes[1].plot(x, C_fixed, color="royalblue", label="C(x,t=1)")
    axes[1].plot(x, J, color="crimson", linestyle="--", label="Flux J = -D dC/dx")
    axes[1].axhline(0, color="gray", linestyle=":", alpha=0.5)
    axes[1].set_xlabel("x"); axes[1].set_title("Concentration & Flux at t=1")
    axes[1].legend(); axes[1].grid(alpha=0.3)

    savefig("diffusion", fig)


# ─────────────────────────────────────────────────────────────
# 11. INFORMATION THEORY
# ─────────────────────────────────────────────────────────────

@sim("information_theory", "Shannon Entropy & Channel Capacity",
     ["information_theory"])
def sim_information_theory():
    """
    Equations: shannon_entropy, shannon_capacity, kl_divergence
    """
    fig, axes = plt.subplots(1, 2, figsize=(13, 5))
    fig.suptitle("Information Theory", fontsize=14, fontweight="bold")

    # Binary entropy H(p)
    p = np.linspace(0.001, 0.999, 1000)
    H = -(p * np.log2(p) + (1 - p) * np.log2(1 - p))
    axes[0].plot(p, H, color="royalblue", linewidth=2)
    axes[0].axvline(0.5, color="gray", linestyle="--", alpha=0.5, label="p=0.5 (max entropy)")
    axes[0].set_xlabel("Probability p"); axes[0].set_ylabel("H(p) bits")
    axes[0].set_title("Binary Shannon Entropy H(p)"); axes[0].legend()
    axes[0].grid(alpha=0.3)

    # Shannon capacity C = B log2(1 + SNR)
    SNR_dB = np.linspace(0, 40, 500)
    SNR = 10 ** (SNR_dB / 10)
    B = 1.0  # normalized bandwidth
    C = B * np.log2(1 + SNR)
    axes[1].plot(SNR_dB, C, color="darkorange", linewidth=2)
    axes[1].set_xlabel("SNR (dB)"); axes[1].set_ylabel("Channel Capacity C (bits/s/Hz)")
    axes[1].set_title("Shannon-Hartley Channel Capacity"); axes[1].grid(alpha=0.3)

    savefig("information_theory", fig)


# ─────────────────────────────────────────────────────────────
# 12. COSMOLOGY
# ─────────────────────────────────────────────────────────────

@sim("cosmology", "Friedmann Equations — Cosmic Expansion",
     ["cosmology"])
def sim_cosmology():
    """
    Equations: friedmann_first, hubble_parameter, dark_energy_eos
    (ȧ/a)² = (8πG/3)ρ  for matter + radiation + dark energy
    """
    # Dimensionless Friedmann equation
    # H(z)/H0 = sqrt(Omega_m(1+z)^3 + Omega_r(1+z)^4 + Omega_Lambda)
    H0 = 70.0  # km/s/Mpc
    Omega_m = 0.3
    Omega_r = 9e-5
    Omega_L = 0.7

    z = np.linspace(0, 10, 1000)
    H_over_H0 = np.sqrt(Omega_m * (1 + z) ** 3 + Omega_r * (1 + z) ** 4 + Omega_L)

    fig, axes = plt.subplots(1, 2, figsize=(13, 5))
    fig.suptitle("Friedmann Cosmology (ΛCDM)", fontsize=14, fontweight="bold")

    axes[0].plot(z, H_over_H0, color="royalblue", linewidth=2, label="ΛCDM")
    # Matter-only
    axes[0].plot(z, np.sqrt(Omega_m * (1 + z) ** 3), color="darkorange",
                 linestyle="--", label="Matter only")
    # Dark energy only
    axes[0].plot(z, np.full_like(z, np.sqrt(Omega_L)), color="green",
                 linestyle=":", label="Λ only")
    axes[0].set_xlabel("Redshift z"); axes[0].set_ylabel("H(z)/H₀")
    axes[0].set_title("Hubble Parameter vs Redshift"); axes[0].legend()
    axes[0].grid(alpha=0.3)

    # Scale factor a(t) — simple Euler integration (avoids overflow near a=0)
    dt_cosmo = 0.005
    t_cosmo = [0.01]
    a_cosmo = [0.05]
    while t_cosmo[-1] < 30:
        a_c = a_cosmo[-1]
        if a_c < 1e-2:
            rho = Omega_m / max(a_c, 1e-2) ** 3 + Omega_L
        else:
            rho = Omega_m / a_c ** 3 + Omega_L
        dadt = H0 * a_c * np.sqrt(max(rho, 0))
        a_cosmo.append(a_c + dt_cosmo * dadt)
        t_cosmo.append(t_cosmo[-1] + dt_cosmo)
    t_cosmo = np.array(t_cosmo)
    a_cosmo = np.array(a_cosmo)

    axes[1].plot(t_cosmo, a_cosmo, color="royalblue", linewidth=2)
    axes[1].axhline(1.0, color="gray", linestyle="--", alpha=0.5, label="Today (a=1)")
    axes[1].set_xlabel("Time (Gyr, normalized)"); axes[1].set_ylabel("Scale factor a(t)")
    axes[1].set_title("Cosmic Scale Factor Evolution"); axes[1].legend()
    axes[1].grid(alpha=0.3)

    savefig("cosmology", fig)


# ─────────────────────────────────────────────────────────────
# 13. POPULATION DYNAMICS
# ─────────────────────────────────────────────────────────────

@sim("lotka_volterra", "Lotka-Volterra Predator-Prey Dynamics",
     ["population_dynamics"])
def sim_lotka_volterra():
    """
    Equations: lotka_volterra_prey, lotka_volterra_predator
    dX/dt = αX - βXY
    dY/dt = δXY - γY
    """
    alpha, beta, delta, gamma = 1.0, 0.1, 0.075, 1.5

    def lv(t, state):
        X, Y = state
        return [alpha * X - beta * X * Y,
                delta * X * Y - gamma * Y]

    t_span = (0, 30)
    t_eval = np.linspace(*t_span, 3000)
    sol = solve_ivp(lv, t_span, [10.0, 5.0], t_eval=t_eval, rtol=1e-9)

    fig, axes = plt.subplots(1, 2, figsize=(13, 5))
    fig.suptitle("Lotka-Volterra Predator-Prey", fontsize=14, fontweight="bold")

    axes[0].plot(sol.t, sol.y[0], color="royalblue", label="Prey X(t)")
    axes[0].plot(sol.t, sol.y[1], color="crimson", label="Predator Y(t)")
    axes[0].set_xlabel("time"); axes[0].set_ylabel("Population")
    axes[0].set_title("Population Time Series"); axes[0].legend()
    axes[0].grid(alpha=0.3)

    axes[1].plot(sol.y[0], sol.y[1], color="darkorange", linewidth=1.0)
    axes[1].plot(*sol.y[:, 0], "go", markersize=8, label="Start")
    axes[1].set_xlabel("Prey X"); axes[1].set_ylabel("Predator Y")
    axes[1].set_title("Phase Portrait (Closed Orbits)"); axes[1].legend()
    axes[1].grid(alpha=0.3)

    savefig("lotka_volterra", fig)


@sim("replicator", "Replicator Equation — Evolutionary Game Theory",
     ["population_dynamics"])
def sim_replicator():
    """
    Equations: replicator_equation
    Rock-Paper-Scissors payoff matrix.
    ẋ_i = x_i(f_i - f̄)
    """
    # Rock-Paper-Scissors payoff matrix
    A = np.array([[0, -1, 1],
                  [1,  0, -1],
                  [-1, 1,  0]])

    def replicator(t, x):
        f = A @ x
        f_bar = x @ f
        return x * (f - f_bar)

    t_span = (0, 50)
    t_eval = np.linspace(*t_span, 5000)

    fig, axes = plt.subplots(1, 2, figsize=(13, 5))
    fig.suptitle("Replicator Dynamics — Rock-Paper-Scissors", fontsize=14, fontweight="bold")

    # Multiple initial conditions
    np.random.seed(42)
    for _ in range(8):
        x0 = np.random.dirichlet([1, 1, 1])
        sol = solve_ivp(replicator, t_span, x0, t_eval=t_eval, rtol=1e-9)
        axes[0].plot(sol.t, sol.y[0], alpha=0.5, color="royalblue", linewidth=0.8)
        axes[0].plot(sol.t, sol.y[1], alpha=0.5, color="crimson", linewidth=0.8)
        axes[0].plot(sol.t, sol.y[2], alpha=0.5, color="green", linewidth=0.8)

    axes[0].set_xlabel("time"); axes[0].set_ylabel("Strategy frequency")
    axes[0].set_title("Strategy Frequencies Over Time")
    from matplotlib.lines import Line2D
    axes[0].legend(handles=[
        Line2D([0], [0], color="royalblue", label="Rock"),
        Line2D([0], [0], color="crimson",   label="Paper"),
        Line2D([0], [0], color="green",     label="Scissors"),
    ], fontsize=8)
    axes[0].grid(alpha=0.3)

    # Simplex trajectory
    # Project 3-simplex to 2D
    def to_2d(x):
        e1 = np.array([0, 0])
        e2 = np.array([1, 0])
        e3 = np.array([0.5, np.sqrt(3) / 2])
        return x[0] * e1 + x[1] * e2 + x[2] * e3

    x0 = np.array([0.6, 0.2, 0.2])
    sol = solve_ivp(replicator, t_span, x0, t_eval=t_eval, rtol=1e-9)
    pts = np.array([to_2d(sol.y[:, i]) for i in range(sol.y.shape[1])])
    axes[1].plot(pts[:, 0], pts[:, 1], color="darkorange", linewidth=0.8, alpha=0.8)
    axes[1].plot(*to_2d(x0), "go", markersize=8, label="Start")
    # Draw simplex edges
    corners = np.array([[0, 0], [1, 0], [0.5, np.sqrt(3) / 2], [0, 0]])
    axes[1].plot(corners[:, 0], corners[:, 1], "k-", linewidth=1.5)
    axes[1].text(-0.05, -0.05, "Rock", fontsize=9)
    axes[1].text(1.0, -0.05, "Paper", fontsize=9)
    axes[1].text(0.45, np.sqrt(3) / 2 + 0.03, "Scissors", fontsize=9)
    axes[1].set_aspect("equal"); axes[1].axis("off")
    axes[1].set_title("Simplex Trajectory"); axes[1].legend()

    savefig("replicator", fig)


@sim("wright_fisher", "Wright-Fisher Genetic Drift",
     ["population_dynamics"])
def sim_wright_fisher():
    """
    Equations: wright_fisher_drift
    Stochastic simulation of allele frequency drift.
    """
    np.random.seed(0)
    N_e_vals = [20, 100, 500]
    p0 = 0.5
    n_gen = 200
    n_traj = 30

    fig, axes = plt.subplots(1, 3, figsize=(15, 4))
    fig.suptitle("Wright-Fisher Genetic Drift", fontsize=14, fontweight="bold")

    for ax, N_e in zip(axes, N_e_vals):
        for _ in range(n_traj):
            p = p0
            traj = [p]
            for _ in range(n_gen):
                p = np.random.binomial(2 * N_e, p) / (2 * N_e)
                traj.append(p)
                if p == 0 or p == 1:
                    traj += [p] * (n_gen - len(traj) + 1)
                    break
            ax.plot(traj, alpha=0.4, linewidth=0.8)
        ax.axhline(0.5, color="gray", linestyle="--", alpha=0.5)
        ax.set_title(f"N_e = {N_e}")
        ax.set_xlabel("Generation"); ax.set_ylabel("Allele frequency p")
        ax.set_ylim(0, 1); ax.grid(alpha=0.3)

    savefig("wright_fisher", fig)


# ─────────────────────────────────────────────────────────────
# 14. NEUROSCIENCE
# ─────────────────────────────────────────────────────────────

@sim("fitzhugh_nagumo", "FitzHugh-Nagumo Neuron Model",
     ["neuroscience"])
def sim_fitzhugh_nagumo():
    """
    Equations: fitzhugh_nagumo_v, fitzhugh_nagumo_w
    dv/dt = v - v³/3 - w + I_ext
    dw/dt = (1/τ)(v + a - bw)
    """
    a, b, tau = 0.7, 0.8, 12.5

    def fn_ode(t, state, I_ext):
        v, w = state
        dv = v - v ** 3 / 3 - w + I_ext
        dw = (1 / tau) * (v + a - b * w)
        return [dv, dw]

    t_span = (0, 200)
    t_eval = np.linspace(*t_span, 5000)

    fig, axes = plt.subplots(1, 2, figsize=(13, 5))
    fig.suptitle("FitzHugh-Nagumo Neuron Model", fontsize=14, fontweight="bold")

    for I_ext, color, label in [(0.3, "steelblue", "I=0.3 (sub-threshold)"),
                                  (0.5, "darkorange", "I=0.5 (near threshold)"),
                                  (1.0, "crimson", "I=1.0 (spiking)")]:
        sol = solve_ivp(fn_ode, t_span, [-1.0, -0.5], t_eval=t_eval,
                        args=(I_ext,), rtol=1e-8)
        axes[0].plot(sol.t, sol.y[0], color=color, label=label, linewidth=1)
        axes[1].plot(sol.y[0], sol.y[1], color=color, alpha=0.8, linewidth=0.8)

    axes[0].set_xlabel("time"); axes[0].set_ylabel("v (membrane potential)")
    axes[0].set_title("Membrane Potential vs Time"); axes[0].legend(fontsize=8)
    axes[0].grid(alpha=0.3)
    axes[1].set_xlabel("v"); axes[1].set_ylabel("w (recovery)")
    axes[1].set_title("Phase Portrait"); axes[1].grid(alpha=0.3)

    savefig("fitzhugh_nagumo", fig)


@sim("cable_equation", "Cable Equation — Dendritic Signal Propagation",
     ["neuroscience"])
def sim_cable_equation():
    """
    Equations: cable_equation
    τ dV/dt = λ² d²V/dx² - V + V_input(x,t)
    """
    # PDE via finite differences
    L = 10.0
    T = 20.0
    nx = 200
    nt = 8000   # smaller dt for stability
    dx = L / nx
    dt = T / nt
    lam2 = 2.0  # λ²
    tau_m = 1.0

    r = lam2 * dt / (tau_m * dx ** 2)  # must be < 0.5 for stability
    V = np.zeros((nt, nx))

    # Inject current at soma (x=0) as a brief pulse
    pulse_steps = int(50 * nt / 2000)
    V[:pulse_steps, 0] = 1.0

    for i in range(1, nt):
        V[i, 1:-1] = np.clip(
            V[i-1, 1:-1]
            + r * (V[i-1, 2:] - 2*V[i-1, 1:-1] + V[i-1, :-2])
            - (dt / tau_m) * V[i-1, 1:-1],
            -10, 10)
        V[i, 0] = V[i-1, 0] if i < pulse_steps else 0.0
        V[i, -1] = 0.0

    x = np.linspace(0, L, nx)
    t = np.linspace(0, T, nt)

    fig, axes = plt.subplots(1, 2, figsize=(13, 5))
    fig.suptitle("Cable Equation — Dendritic Propagation", fontsize=14, fontweight="bold")

    V_plot = np.nan_to_num(V, nan=0.0, posinf=0.0, neginf=0.0)
    im = axes[0].imshow(V_plot, aspect="auto", origin="lower", cmap="hot",
                        extent=[0, L, 0, T])
    fig.colorbar(im, ax=axes[0], label="V(x,t)")
    axes[0].set_xlabel("Position x (space constant units)")
    axes[0].set_ylabel("Time t (membrane time constant units)")
    axes[0].set_title("Voltage Propagation Heatmap")

    step_scale = nt // 2000
    for t_idx, color in [(50*step_scale, "royalblue"), (100*step_scale, "darkorange"),
                          (200*step_scale, "crimson"), (400*step_scale, "green")]:
        axes[1].plot(x, V_plot[t_idx], color=color, label=f"t={t[t_idx]:.1f}")
    axes[1].set_xlabel("Position x"); axes[1].set_ylabel("V(x)")
    axes[1].set_title("Voltage Profile at Different Times")
    axes[1].legend(fontsize=8); axes[1].grid(alpha=0.3)

    savefig("cable_equation", fig)


# ─────────────────────────────────────────────────────────────
# 15. MOLECULAR BIOLOGY
# ─────────────────────────────────────────────────────────────

@sim("hill_arrhenius", "Hill Equation & Arrhenius Rate Law",
     ["molecular_biology"])
def sim_hill_arrhenius():
    """
    Equations: hill_equation, arrhenius
    θ = [L]^n / (Kd^n + [L]^n)
    k = A exp(-Ea/RT)
    """
    fig, axes = plt.subplots(1, 2, figsize=(13, 5))
    fig.suptitle("Molecular Biology: Binding & Kinetics", fontsize=14, fontweight="bold")

    # Hill equation
    L = np.logspace(-3, 3, 500)
    Kd = 1.0
    for n, color in [(0.5, "steelblue"), (1.0, "darkorange"),
                      (2.0, "crimson"), (4.0, "green"), (8.0, "purple")]:
        theta = L ** n / (Kd ** n + L ** n)
        axes[0].semilogx(L, theta, color=color, label=f"n={n}")
    axes[0].axvline(Kd, color="gray", linestyle="--", alpha=0.5, label="[L]=Kd")
    axes[0].axhline(0.5, color="gray", linestyle=":", alpha=0.5)
    axes[0].set_xlabel("[L] (ligand concentration)"); axes[0].set_ylabel("θ (occupancy)")
    axes[0].set_title("Hill Equation — Cooperative Binding")
    axes[0].legend(fontsize=8); axes[0].grid(alpha=0.3)

    # Arrhenius — note the Fermi-Dirac analogy
    kB = 8.617e-5  # eV/K
    T_vals = np.linspace(200, 1000, 500)
    Ea_vals = [0.3, 0.5, 0.8, 1.2]  # eV
    for Ea, color in zip(Ea_vals, ["steelblue", "darkorange", "crimson", "green"]):
        k = np.exp(-Ea / (kB * T_vals))
        axes[1].semilogy(1000 / T_vals, k, color=color, label=f"Ea={Ea} eV")
    axes[1].set_xlabel("1000/T (K⁻¹)"); axes[1].set_ylabel("Rate constant k (normalized)")
    axes[1].set_title("Arrhenius Plot (log k vs 1/T)")
    axes[1].legend(fontsize=8); axes[1].grid(alpha=0.3)

    savefig("hill_arrhenius", fig)


@sim("turing_patterns", "Turing Reaction-Diffusion — Pattern Formation",
     ["molecular_biology"])
def sim_turing_patterns():
    """
    Equations: turing_activator, turing_inhibitor
    Schnakenberg model:
    du/dt = Du * d²u/dx² + a - u + u²v
    dv/dt = Dv * d²v/dx² + b - u²v
    """
    # Schnakenberg parameters
    a, b = 0.1, 0.9
    Du, Dv = 1.0, 40.0
    L = 100
    nx = 256
    T = 2000
    dt = 0.5
    dx = L / nx

    u = np.ones(nx) * (a + b) + 0.01 * np.random.randn(nx)
    v = np.ones(nx) * (b / (a + b) ** 2) + 0.01 * np.random.randn(nx)

    ru = Du * dt / dx ** 2
    rv = Dv * dt / dx ** 2

    snapshots = []
    for step in range(int(T / dt)):
        u_new = (u + dt * (a - u + u**2 * v)
                 + ru * (np.roll(u, 1) - 2*u + np.roll(u, -1)))
        v_new = (v + dt * (b - u**2 * v)
                 + rv * (np.roll(v, 1) - 2*v + np.roll(v, -1)))
        u, v = u_new, v_new
        if step % int(T / dt / 5) == 0:
            snapshots.append((step * dt, u.copy(), v.copy()))

    fig, axes = plt.subplots(2, len(snapshots), figsize=(15, 5))
    fig.suptitle("Turing Pattern Formation (Schnakenberg Model)", fontsize=14, fontweight="bold")

    x = np.linspace(0, L, nx)
    for col, (t_val, u_snap, v_snap) in enumerate(snapshots):
        axes[0, col].plot(x, u_snap, color="royalblue", linewidth=1)
        axes[0, col].set_title(f"t={t_val:.0f}")
        axes[0, col].set_ylim(0, 4)
        if col == 0:
            axes[0, col].set_ylabel("u (activator)")
        axes[1, col].plot(x, v_snap, color="crimson", linewidth=1)
        axes[1, col].set_ylim(0, 1.5)
        if col == 0:
            axes[1, col].set_ylabel("v (inhibitor)")
        axes[1, col].set_xlabel("x")

    plt.tight_layout()
    savefig("turing_patterns", fig)


# ─────────────────────────────────────────────────────────────
# 16. ECOLOGY & SYSTEMS BIOLOGY
# ─────────────────────────────────────────────────────────────

@sim("fisher_kpp", "Fisher-KPP Traveling Wave",
     ["ecology_systems"])
def sim_fisher_kpp():
    """
    Equations: fisher_kpp
    du/dt = D d²u/dx² + ru(1-u)
    Traveling wave solution: u(x,t) = f(x - ct)
    """
    D = 1.0
    r = 1.0
    L = 100.0
    nx = 400
    T = 60
    dt = 0.05
    dx = L / nx

    u = np.zeros(nx)
    u[:20] = 1.0  # initial front

    rD = D * dt / dx ** 2

    snapshots = []
    for step in range(int(T / dt)):
        u_new = (u + dt * r * u * (1 - u)
                 + rD * (np.roll(u, 1) - 2*u + np.roll(u, -1)))
        u_new[0] = 1.0; u_new[-1] = 0.0
        u = np.clip(u_new, 0, 1)
        if step % int(T / dt / 6) == 0:
            snapshots.append((step * dt, u.copy()))

    x = np.linspace(0, L, nx)
    fig, axes = plt.subplots(1, 2, figsize=(13, 5))
    fig.suptitle("Fisher-KPP Traveling Wave", fontsize=14, fontweight="bold")

    colors = plt.cm.viridis(np.linspace(0.1, 0.9, len(snapshots)))
    for (t_val, u_snap), color in zip(snapshots, colors):
        axes[0].plot(x, u_snap, color=color, label=f"t={t_val:.0f}")
    axes[0].set_xlabel("x"); axes[0].set_ylabel("u(x,t)")
    axes[0].set_title("Wave Front Propagation"); axes[0].legend(fontsize=8)
    axes[0].grid(alpha=0.3)

    # Theoretical wave speed c = 2*sqrt(D*r)
    c_theory = 2 * np.sqrt(D * r)
    axes[1].text(0.5, 0.6, f"Theoretical wave speed:\nc = 2√(Dr) = {c_theory:.2f}",
                 transform=axes[1].transAxes, fontsize=13, ha="center",
                 bbox=dict(boxstyle="round", facecolor="lightyellow", alpha=0.8))
    axes[1].text(0.5, 0.35, "Bridges:\nFick's 2nd Law (D∇²u)\n+ Logistic Growth (ru(1-u))",
                 transform=axes[1].transAxes, fontsize=11, ha="center",
                 bbox=dict(boxstyle="round", facecolor="lightblue", alpha=0.8))
    axes[1].axis("off"); axes[1].set_title("Equation Structure")

    savefig("fisher_kpp", fig)


@sim("sir_epidemic", "SIR Epidemic Model",
     ["ecology_systems"])
def sim_sir_epidemic():
    """
    Equations: sir_susceptible, sir_infected
    dS/dt = -βSI,  dI/dt = βSI - γI,  dR/dt = γI
    """
    def sir(t, y, beta, gamma):
        S, I, R = y
        N = S + I + R
        return [-beta * S * I / N,
                 beta * S * I / N - gamma * I,
                 gamma * I]

    t_span = (0, 160)
    t_eval = np.linspace(*t_span, 2000)
    N0 = 1000.0

    fig, axes = plt.subplots(1, 2, figsize=(13, 5))
    fig.suptitle("SIR Epidemic Model", fontsize=14, fontweight="bold")

    # Vary R0 = beta/gamma
    gamma = 0.1
    for R0, color in [(1.5, "steelblue"), (2.5, "darkorange"),
                       (4.0, "crimson"), (8.0, "purple")]:
        beta = R0 * gamma
        sol = solve_ivp(sir, t_span, [N0 - 1, 1, 0], t_eval=t_eval,
                        args=(beta, gamma), rtol=1e-9)
        axes[0].plot(sol.t, sol.y[1] / N0 * 100, color=color, label=f"R₀={R0}")

    axes[0].set_xlabel("Days"); axes[0].set_ylabel("Infected (%)")
    axes[0].set_title("Epidemic Curves for Different R₀"); axes[0].legend()
    axes[0].grid(alpha=0.3)

    # Phase portrait S vs I for R0=2.5
    beta = 2.5 * gamma
    sol = solve_ivp(sir, t_span, [N0 - 1, 1, 0], t_eval=t_eval,
                    args=(beta, gamma), rtol=1e-9)
    axes[1].plot(sol.y[0] / N0, sol.y[1] / N0, color="darkorange", linewidth=1.5)
    axes[1].plot(sol.y[0, 0] / N0, sol.y[1, 0] / N0, "go", markersize=8, label="Start")
    axes[1].plot(sol.y[0, -1] / N0, sol.y[1, -1] / N0, "rs", markersize=8, label="End")
    axes[1].set_xlabel("S/N (susceptible fraction)"); axes[1].set_ylabel("I/N (infected fraction)")
    axes[1].set_title("Phase Portrait (R₀=2.5)"); axes[1].legend()
    axes[1].grid(alpha=0.3)

    savefig("sir_epidemic", fig)


@sim("allometric", "Allometric Scaling — Kleiber's Law",
     ["ecology_systems"])
def sim_allometric():
    """
    Equations: allometric_scaling
    B = B0 * M^(3/4)
    """
    # Real data (approximate)
    organisms = {
        "Mouse":      (0.02,   0.003),
        "Rat":        (0.3,    0.02),
        "Cat":        (3.0,    0.1),
        "Dog":        (20.0,   0.5),
        "Human":      (70.0,   1.3),
        "Horse":      (450.0,  5.0),
        "Elephant":   (3000.0, 18.0),
        "Blue Whale": (100000.0, 200.0),
    }

    M_vals = np.logspace(-3, 6, 500)
    B0 = 0.018  # fitted constant (kcal/day/g^0.75)
    B_theory = B0 * M_vals ** 0.75

    fig, ax = plt.subplots(figsize=(9, 6))
    ax.loglog(M_vals, B_theory, color="royalblue", linewidth=2,
              label="B = B₀ M^(3/4) (Kleiber's law)")

    for name, (M, B) in organisms.items():
        ax.loglog(M, B, "o", markersize=8, color="crimson")
        ax.annotate(name, (M, B), textcoords="offset points",
                    xytext=(5, 3), fontsize=7)

    ax.set_xlabel("Body mass M (kg)"); ax.set_ylabel("Metabolic rate B (kW, normalized)")
    ax.set_title("Kleiber's Allometric Scaling Law: B ∝ M^(3/4)", fontweight="bold")
    ax.legend(); ax.grid(alpha=0.3, which="both")

    savefig("allometric", fig)


# ─────────────────────────────────────────────────────────────
# 17. CROSS-DOMAIN: MORPHISM SHOWCASE
# ─────────────────────────────────────────────────────────────

@sim("morphism_showcase", "Cross-Domain Morphism Showcase",
     ["quantum", "biophysics", "population_dynamics", "molecular_biology"])
def sim_morphism_showcase():
    """
    Side-by-side comparison of mathematically identical equations
    from different domains:
    1. Fermi-Dirac ↔ Hill equation
    2. Logistic growth ↔ Logistic map
    3. Diffusion (Fick) ↔ Wright-Fisher ↔ Schrödinger
    """
    fig = plt.figure(figsize=(15, 10))
    fig.suptitle("Cross-Domain Morphism Showcase\n"
                 "Same Mathematics, Different Physics",
                 fontsize=14, fontweight="bold")
    gs = gridspec.GridSpec(2, 3, figure=fig, hspace=0.45, wspace=0.35)

    # --- Panel 1: Fermi-Dirac ↔ Hill equation ---
    ax1 = fig.add_subplot(gs[0, 0])
    E = np.linspace(-5, 5, 500)
    mu, kT = 0.0, 1.0
    fd = 1 / (np.exp((E - mu) / kT) + 1)
    ax1.plot(E, fd, color="royalblue", linewidth=2, label="Fermi-Dirac f(E)")

    L = np.logspace(-1, 1, 500)
    Kd, n = 1.0, 1.0
    hill = L ** n / (Kd ** n + L ** n)
    ax1.plot(np.log10(L) * 2, hill, color="crimson", linestyle="--",
             linewidth=2, label="Hill θ([L]), n=1")
    ax1.set_title("Fermi-Dirac ↔ Hill Equation\n(same math, different physics)")
    ax1.legend(fontsize=8); ax1.grid(alpha=0.3)
    ax1.set_xlabel("E (or log[L])"); ax1.set_ylabel("Occupancy probability")

    # --- Panel 2: Logistic ODE ↔ Logistic map ---
    ax2 = fig.add_subplot(gs[0, 1])
    t = np.linspace(0, 10, 500)
    r, K = 1.0, 1.0
    N_ode = K / (1 + (K - 0.1) / 0.1 * np.exp(-r * t))
    ax2.plot(t, N_ode, color="royalblue", linewidth=2, label="Logistic ODE N(t)")

    # Discrete logistic map (r=2.8 → stable fixed point)
    r_map = 2.8
    x_map = [0.1]
    for _ in range(50):
        x_map.append(r_map * x_map[-1] * (1 - x_map[-1]))
    t_map = np.linspace(0, 10, 51)
    ax2.plot(t_map, x_map, color="crimson", linestyle="--",
             linewidth=1.5, marker="o", markersize=2, label="Logistic map (r=2.8)")
    ax2.set_title("Logistic ODE ↔ Logistic Map\n(continuous vs discrete)")
    ax2.legend(fontsize=8); ax2.grid(alpha=0.3)
    ax2.set_xlabel("time / generation"); ax2.set_ylabel("Population (normalized)")

    # --- Panel 3: Arrhenius ↔ Boltzmann factor ---
    ax3 = fig.add_subplot(gs[0, 2])
    kB = 1.0
    T_range = np.linspace(0.5, 5, 500)
    for Ea, color, label in [(1.0, "royalblue", "Arrhenius k∝exp(-Ea/kT)"),
                               (2.0, "crimson",   "Ea=2"),
                               (0.5, "green",     "Ea=0.5")]:
        ax3.plot(T_range, np.exp(-Ea / (kB * T_range)), color=color, label=label)
    ax3.set_title("Arrhenius ↔ Boltzmann Factor\n(reaction rate = thermal probability)")
    ax3.legend(fontsize=8); ax3.grid(alpha=0.3)
    ax3.set_xlabel("Temperature T (kB=1)"); ax3.set_ylabel("Rate / probability")

    # --- Panel 4: Diffusion ↔ Wright-Fisher ↔ Schrödinger ---
    ax4 = fig.add_subplot(gs[1, :])
    x = np.linspace(-5, 5, 500)
    t_vals = [0.2, 0.5, 1.0, 2.0]
    colors = plt.cm.cool(np.linspace(0.1, 0.9, len(t_vals)))

    for t_val, color in zip(t_vals, colors):
        # All three are Gaussian spreading (same Green's function)
        G = 1 / np.sqrt(4 * np.pi * t_val) * np.exp(-x ** 2 / (4 * t_val))
        ax4.plot(x, G, color=color, linewidth=1.5, label=f"t={t_val}")

    ax4.set_title(
        "Shared Green's Function: Fick's Diffusion = Wright-Fisher Drift = Free Schrödinger\n"
        "G(x,t) = (4πt)^(-1/2) exp(-x²/4t)   [all three equations have this solution]",
        fontsize=10)
    ax4.set_xlabel("x (position / allele frequency / probability amplitude)")
    ax4.set_ylabel("G(x,t)")
    ax4.legend(fontsize=9); ax4.grid(alpha=0.3)

    savefig("morphism_showcase", fig)


# ─────────────────────────────────────────────────────────────
# RUNNER
# ─────────────────────────────────────────────────────────────

def run_all():
    print(f"\nRunning {len(REGISTRY)} simulations → plots/\n")
    for name, meta in REGISTRY.items():
        print(f"[{name}]  {meta['title']}")
        meta["fn"]()
    print(f"\nDone. {len(REGISTRY)} plots saved to {PLOT_DIR}/")


def list_sims():
    print(f"\n{'Name':<30} {'Domains':<40} Title")
    print("-" * 100)
    for name, meta in REGISTRY.items():
        domains = ", ".join(meta["domains"])
        print(f"{name:<30} {domains:<40} {meta['title']}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Geometric-to-Binary Simulations")
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
