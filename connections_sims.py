"""
connections_sims.py
Simulations for the Silicon Phase-Space Framework (Connections.md).

Concepts covered:
  1. silicon_phase_diagram    — 4D state space S=(n,d,ℓ,κ) and attractor basins
  2. phase_transitions        — Band-gap collapse, dimensional quantization, decoherence surfaces
  3. silicon_manifold_flow    — dS/dt dynamics: relaxation, driving, aging trajectories
  4. fabrication_trajectories — Control paths through S-space for CMOS, photonic, quantum devices
  5. geometry_to_binary       — Full pipeline: geometry field → S → graph → bits → layout
  6. basin_stability          — Stability margins, noise sensitivity, and failure modes

Usage
-----
    python connections_sims.py              # run all 6
    python connections_sims.py --sim silicon_phase_diagram
    python connections_sims.py --list
"""

import argparse
import os
import warnings
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
from matplotlib.colors import Normalize
from matplotlib.cm import ScalarMappable
import networkx as nx

warnings.filterwarnings("ignore")

PLOT_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "plots")
os.makedirs(PLOT_DIR, exist_ok=True)

REGISTRY = {}


def sim(name, title):
    def decorator(fn):
        REGISTRY[name] = {"fn": fn, "title": title}
        return fn
    return decorator


def savefig(name):
    path = os.path.join(PLOT_DIR, f"{name}.png")
    plt.savefig(path, dpi=120, bbox_inches="tight")
    plt.close()
    print(f"  Saved: {path}")


# ─────────────────────────────────────────────────────────────────────────────
# SiliconState model (extracted from Connections.md)
# ─────────────────────────────────────────────────────────────────────────────

class SiliconState:
    """Silicon phase-space representation: S = (n, d, ℓ, κ)."""

    def __init__(self, n, d, l, k):
        self.n = n   # carrier density
        self.d = d   # defect density [0,1]
        self.l = l   # effective dimensionality [0,3]
        self.k = k   # coupling dict: electrical, optical, thermal

    def regime(self):
        if self.l <= 0.5:
            return "quantum_confinement"
        if self.d > 0.7:
            return "defect_dominated"
        if self.n > 1e19:
            return "metallic_breakdown"
        if self.k.get("optical", 0) > self.k.get("electrical", 0):
            return "photonic_transport"
        return "semiconductor"

    def stability(self):
        return np.exp(-self.d) * (1.0 / (1.0 + abs(self.n - 1e17) / 1e17))

    def bandgap(self):
        """Approximate effective bandgap (eV) as function of n and d."""
        Eg0 = 1.12  # silicon bandgap at 300K (eV)
        # Bandgap narrowing with doping (empirical)
        dEg_n = 3.5e-8 * (self.n / 1e18) ** 0.5 if self.n > 1e17 else 0
        # Defect-induced gap states
        dEg_d = 0.5 * self.d
        return max(0.0, Eg0 - dEg_n - dEg_d)


def geometry_to_silicon(field):
    """Maps a 2D geometry field to a SiliconState."""
    n = float(np.mean(np.abs(field))) * 1e18
    d = float(np.clip(np.var(field), 0, 1))
    l = float(np.clip(3.0 / (1.0 + np.std(field)), 0, 3))
    k = {
        "electrical": float(np.mean(np.abs(np.gradient(field)[0]))),
        "optical":    float(np.std(field)),
        "thermal":    float(np.mean(field ** 2)),
    }
    return SiliconState(n=n, d=d, l=l, k=k)


def silicon_to_graph(S, n_nodes=8):
    """Converts SiliconState into a weighted computational graph."""
    G = nx.Graph()
    regime = S.regime()
    for i in range(n_nodes):
        G.add_node(i, activity=S.n * (1 - S.d) * 1e-17, mode=regime)
    kw = ["electrical", "optical", "thermal"]
    kv = [S.k.get(k, 0) for k in kw]
    for i in range(n_nodes):
        for j in range(i + 1, n_nodes):
            w = kv[0] * 0.4 + kv[1] * 0.3 + kv[2] * 0.3
            G.add_edge(i, j, weight=w)
    return G


def graph_to_binary(G, S):
    """Converts weighted graph into binary logic bits."""
    regime = S.regime()
    bits = []
    for node, data in G.nodes(data=True):
        a = data["activity"]
        if regime == "quantum_confinement":
            bit = 1 if np.sin(a * np.pi) > 0 else 0
        elif regime == "defect_dominated":
            bit = 0 if a < 0.5 else int(np.random.rand() > 0.5)
        elif regime == "photonic_transport":
            bit = int(a * 10) % 2
        else:
            bit = 1 if a > 0.5 else 0
        bits.append(bit)
    return bits


# ─────────────────────────────────────────────────────────────────────────────
# Simulation 1: Silicon Phase Diagram
# ─────────────────────────────────────────────────────────────────────────────

@sim("silicon_phase_diagram",
     "Silicon Phase Diagram — Attractor Basins in S-Space")
def silicon_phase_diagram():
    fig, axes = plt.subplots(2, 3, figsize=(16, 10))
    fig.suptitle("Silicon Phase-Space S = (n, d, ℓ, κ)\nAttractor Basins", fontsize=14)

    REGIME_COLORS = {
        "semiconductor":      "#2196F3",
        "metallic_breakdown": "#F44336",
        "quantum_confinement":"#9C27B0",
        "photonic_transport": "#4CAF50",
        "defect_dominated":   "#FF9800",
    }

    # Panel 1: n vs d phase map (ℓ=3, κ_elec dominant)
    ax = axes[0, 0]
    n_vals = np.logspace(14, 21, 80)
    d_vals = np.linspace(0, 1, 80)
    Z = np.zeros((80, 80), dtype=int)
    regime_list = list(REGIME_COLORS.keys())
    for i, d in enumerate(d_vals):
        for j, n in enumerate(n_vals):
            S = SiliconState(n=n, d=d, l=3.0,
                             k={"electrical": 1.0, "optical": 0.2, "thermal": 0.3})
            Z[i, j] = regime_list.index(S.regime())
    cmap = matplotlib.colors.ListedColormap(list(REGIME_COLORS.values()))
    ax.contourf(np.log10(n_vals), d_vals, Z, levels=[-0.5, 0.5, 1.5, 2.5, 3.5, 4.5],
                cmap=cmap, alpha=0.85)
    ax.set_xlabel("log₁₀(n) [cm⁻³]")
    ax.set_ylabel("Defect density d")
    ax.set_title("n–d Phase Map (ℓ=3)")
    patches = [mpatches.Patch(color=c, label=r) for r, c in REGIME_COLORS.items()]
    ax.legend(handles=patches, fontsize=7, loc="upper left")

    # Panel 2: n vs ℓ phase map (d=0.1, κ_elec dominant)
    ax = axes[0, 1]
    l_vals = np.linspace(0, 3, 80)
    Z2 = np.zeros((80, 80), dtype=int)
    for i, l in enumerate(l_vals):
        for j, n in enumerate(n_vals):
            S = SiliconState(n=n, d=0.1, l=l,
                             k={"electrical": 1.0, "optical": 0.2, "thermal": 0.3})
            Z2[i, j] = regime_list.index(S.regime())
    ax.contourf(np.log10(n_vals), l_vals, Z2, levels=[-0.5, 0.5, 1.5, 2.5, 3.5, 4.5],
                cmap=cmap, alpha=0.85)
    ax.set_xlabel("log₁₀(n) [cm⁻³]")
    ax.set_ylabel("Effective dimensionality ℓ")
    ax.set_title("n–ℓ Phase Map (d=0.1)")

    # Panel 3: κ_optical vs κ_electrical phase map
    ax = axes[0, 2]
    k_vals = np.linspace(0, 2, 80)
    Z3 = np.zeros((80, 80), dtype=int)
    for i, ko in enumerate(k_vals):
        for j, ke in enumerate(k_vals):
            S = SiliconState(n=1e17, d=0.1, l=2.5,
                             k={"electrical": ke, "optical": ko, "thermal": 0.3})
            Z3[i, j] = regime_list.index(S.regime())
    ax.contourf(k_vals, k_vals, Z3, levels=[-0.5, 0.5, 1.5, 2.5, 3.5, 4.5],
                cmap=cmap, alpha=0.85)
    ax.set_xlabel("κ_electrical")
    ax.set_ylabel("κ_optical")
    ax.set_title("Coupling Phase Map")
    ax.plot([0, 2], [0, 2], "k--", lw=1, label="κ_opt = κ_elec")
    ax.legend(fontsize=8)

    # Panel 4: Bandgap surface
    ax = axes[1, 0]
    n_bg = np.logspace(14, 21, 100)
    d_bg = np.linspace(0, 1, 100)
    NN, DD = np.meshgrid(n_bg, d_bg)
    Eg = np.vectorize(lambda n, d: SiliconState(n=n, d=d, l=3,
                      k={"electrical": 1, "optical": 0, "thermal": 0}).bandgap())(NN, DD)
    cf = ax.contourf(np.log10(n_bg), d_bg, Eg, levels=20, cmap="RdYlGn")
    plt.colorbar(cf, ax=ax, label="Bandgap (eV)")
    ax.contour(np.log10(n_bg), d_bg, Eg, levels=[0.0], colors="red", linewidths=2)
    ax.set_xlabel("log₁₀(n) [cm⁻³]")
    ax.set_ylabel("Defect density d")
    ax.set_title("Bandgap Surface (red = gap closure)")

    # Panel 5: Stability landscape
    ax = axes[1, 1]
    stab = np.vectorize(lambda n, d: SiliconState(n=n, d=d, l=3,
                        k={"electrical": 1, "optical": 0, "thermal": 0}).stability())(NN, DD)
    cf2 = ax.contourf(np.log10(n_bg), d_bg, stab, levels=20, cmap="Blues")
    plt.colorbar(cf2, ax=ax, label="Stability metric")
    ax.set_xlabel("log₁₀(n) [cm⁻³]")
    ax.set_ylabel("Defect density d")
    ax.set_title("Stability Landscape")
    # Mark CMOS basin
    ax.annotate("CMOS\nbasin", xy=(17, 0.1), fontsize=9, color="white",
                ha="center", fontweight="bold")

    # Panel 6: Regime summary table
    ax = axes[1, 2]
    ax.axis("off")
    table_data = [
        ["Regime", "n [cm⁻³]", "d", "ℓ", "κ dominant"],
        ["Semiconductor", "10¹⁴–10¹⁸", "< 0.3", "3", "Electrical"],
        ["Metallic", "> 10¹⁹", "any", "3", "Electrical"],
        ["Quantum", "any", "< 0.3", "0–1", "Electrical"],
        ["Photonic", "any", "< 0.3", "2–3", "Optical > Elec"],
        ["Defect", "any", "> 0.7", "any", "Surface"],
    ]
    tbl = ax.table(cellText=table_data[1:], colLabels=table_data[0],
                   loc="center", cellLoc="center")
    tbl.auto_set_font_size(False)
    tbl.set_fontsize(8)
    tbl.scale(1, 1.6)
    ax.set_title("Phase Regime Summary", pad=20)

    plt.tight_layout()
    savefig("silicon_phase_diagram")


# ─────────────────────────────────────────────────────────────────────────────
# Simulation 2: Phase Transition Surfaces
# ─────────────────────────────────────────────────────────────────────────────

@sim("phase_transitions",
     "Phase Transition Surfaces — Band-Gap Collapse, Quantization, Decoherence")
def phase_transitions():
    fig, axes = plt.subplots(2, 2, figsize=(13, 10))
    fig.suptitle("Silicon Phase Transition Surfaces", fontsize=14)

    # Panel 1: Band structure collapse E_g(n,d) = 0
    ax = axes[0, 0]
    n_vals = np.logspace(15, 21, 200)
    d_vals = np.linspace(0, 1, 200)
    NN, DD = np.meshgrid(n_vals, d_vals)
    Eg = np.vectorize(lambda n, d: SiliconState(n=n, d=d, l=3,
                      k={"electrical": 1, "optical": 0, "thermal": 0}).bandgap())(NN, DD)
    cf = ax.contourf(np.log10(n_vals), d_vals, Eg, levels=30, cmap="RdYlGn_r")
    plt.colorbar(cf, ax=ax, label="Eg (eV)")
    cs = ax.contour(np.log10(n_vals), d_vals, Eg, levels=[0.0], colors="white", linewidths=2.5)
    ax.clabel(cs, fmt="Eg=0 (collapse)", fontsize=9, colors="white")
    ax.set_xlabel("log₁₀(n) [cm⁻³]")
    ax.set_ylabel("Defect density d")
    ax.set_title("1. Band Structure Collapse Surface\nE_g(n,d) = 0")
    ax.text(15.5, 0.85, "Metallic\nregime", color="white", fontsize=9)
    ax.text(15.5, 0.15, "Semiconductor\nregime", color="black", fontsize=9)

    # Panel 2: Dimensional quantization surface ℓ ≲ λ_F
    ax = axes[0, 1]
    # Fermi wavelength λ_F = (2π / (3π²n))^(1/3)
    n_q = np.logspace(14, 21, 300)
    lambda_F = (2 * np.pi / (3 * np.pi**2 * n_q)) ** (1/3) * 1e9  # in nm
    l_confinement = np.linspace(0, 100, 300)  # nm
    ax.fill_between(np.log10(n_q), 0, lambda_F, alpha=0.3, color="purple",
                    label="Quantum confinement zone\n(ℓ < λ_F)")
    ax.fill_between(np.log10(n_q), lambda_F, 100, alpha=0.15, color="blue",
                    label="Classical zone\n(ℓ > λ_F)")
    ax.plot(np.log10(n_q), lambda_F, "purple", lw=2.5, label="λ_F (Fermi wavelength)")
    ax.axhline(y=10, color="orange", ls="--", lw=1.5, label="10 nm (FinFET gate)")
    ax.axhline(y=2, color="red", ls="--", lw=1.5, label="2 nm (quantum dot)")
    ax.set_xlabel("log₁₀(n) [cm⁻³]")
    ax.set_ylabel("Confinement length ℓ (nm)")
    ax.set_title("2. Dimensional Quantization Surface\nℓ ≲ λ_F")
    ax.set_ylim(0, 50)
    ax.legend(fontsize=8)

    # Panel 3: Decoherence boundary κ_thermal >> κ_coherent
    ax = axes[1, 0]
    k_thermal = np.linspace(0, 3, 200)
    k_coherent = np.linspace(0, 3, 200)
    KT, KC = np.meshgrid(k_thermal, k_coherent)
    ratio = KT / (KC + 0.01)
    cf3 = ax.contourf(k_thermal, k_coherent, ratio, levels=30, cmap="hot_r")
    plt.colorbar(cf3, ax=ax, label="κ_thermal / κ_coherent")
    ax.contour(k_thermal, k_coherent, ratio, levels=[1.0], colors="cyan", linewidths=2.5)
    ax.plot([0, 3], [0, 3], "cyan", lw=2.5, label="Decoherence boundary\n(ratio = 1)")
    ax.fill_between([0, 3], [0, 3], [3, 3], alpha=0.1, color="cyan")
    ax.text(0.5, 2.2, "Quantum → Classical\n(thermal dominates)", color="cyan", fontsize=9)
    ax.text(1.8, 0.3, "Coherent regime", color="white", fontsize=9)
    ax.set_xlabel("κ_thermal")
    ax.set_ylabel("κ_coherent")
    ax.set_title("3. Decoherence Boundary\nκ_thermal ≫ κ_coherent")
    ax.legend(fontsize=8)

    # Panel 4: All three surfaces in a unified view
    ax = axes[1, 1]
    ax.axis("off")
    summary = [
        ["Surface", "Condition", "Transition"],
        ["Band collapse", "E_g(n,d) = 0", "Semiconductor → Metal"],
        ["Quantization", "ℓ ≲ λ_F", "Classical → Quantum"],
        ["Decoherence", "κ_th ≫ κ_coh", "Quantum → Classical"],
    ]
    tbl = ax.table(cellText=summary[1:], colLabels=summary[0],
                   loc="center", cellLoc="center")
    tbl.auto_set_font_size(False)
    tbl.set_fontsize(10)
    tbl.scale(1.2, 2.0)
    ax.set_title("Phase Transition Summary", pad=20)
    ax.text(0.5, 0.08,
            "Each surface is a genuine bifurcation:\n"
            "crossing it changes the topology of the system's physics.",
            ha="center", va="center", transform=ax.transAxes,
            fontsize=9, style="italic",
            bbox=dict(boxstyle="round", facecolor="lightyellow", alpha=0.8))

    plt.tight_layout()
    savefig("phase_transitions")


# ─────────────────────────────────────────────────────────────────────────────
# Simulation 3: Silicon Manifold Flow dS/dt
# ─────────────────────────────────────────────────────────────────────────────

@sim("silicon_manifold_flow",
     "Silicon Manifold Flow — dS/dt Dynamics: Relaxation, Driving, Aging")
def silicon_manifold_flow():
    fig, axes = plt.subplots(2, 2, figsize=(13, 10))
    fig.suptitle("Silicon Manifold Dynamics: dS/dt = F(n, d, ℓ, κ)", fontsize=14)

    # Simplified dynamics:
    # dn/dt = -γ_n (n - n_eq) + gate_drive(t)
    # dd/dt = +α_d (slow defect accumulation)
    # dℓ/dt = 0 (fixed by geometry)
    # dκ/dt = -γ_κ (κ - κ_eq)

    t = np.linspace(0, 100, 1000)
    n_eq = 1e17
    gamma_n = 0.1
    alpha_d = 0.002
    gamma_k = 0.05

    # Panel 1: Carrier relaxation (no driving)
    ax = axes[0, 0]
    for n0 in [1e15, 1e17, 1e19]:
        n_t = n_eq + (n0 - n_eq) * np.exp(-gamma_n * t)
        ax.semilogx(t + 0.1, n_t, label=f"n₀ = {n0:.0e}")
    ax.axhline(n_eq, color="k", ls="--", lw=1, label=f"n_eq = {n_eq:.0e}")
    ax.set_xlabel("Time (a.u.)")
    ax.set_ylabel("Carrier density n [cm⁻³]")
    ax.set_title("Carrier Relaxation (Thermodynamic Restoring Force)")
    ax.legend(fontsize=8)

    # Panel 2: Defect accumulation (aging trajectory)
    ax = axes[0, 1]
    d0 = 0.05
    d_t = d0 + alpha_d * t
    d_t = np.clip(d_t, 0, 1)
    regime_t = []
    for d in d_t:
        S = SiliconState(n=1e17, d=d, l=3,
                         k={"electrical": 1.0, "optical": 0.2, "thermal": 0.3})
        regime_t.append(S.regime())
    ax.plot(t, d_t, "orange", lw=2, label="d(t) — defect accumulation")
    # Mark regime transitions
    prev = regime_t[0]
    for i, r in enumerate(regime_t):
        if r != prev:
            ax.axvline(t[i], color="red", ls="--", lw=1.5, alpha=0.7)
            ax.text(t[i] + 1, d_t[i], f"→ {r}", fontsize=7, color="red")
            prev = r
    ax.set_xlabel("Time (a.u.)")
    ax.set_ylabel("Defect density d")
    ax.set_title("Aging Trajectory — Slow Drift in d")
    ax.legend(fontsize=9)

    # Panel 3: Gate-driven oscillation (transistor switching)
    ax = axes[1, 0]
    gate_freq = 0.5
    gate = 0.5 * (1 + np.sign(np.sin(2 * np.pi * gate_freq * t / 100)))
    n_driven = n_eq * (0.01 + gate * 10)  # off: 1e15, on: 1e18
    ax.plot(t, np.log10(n_driven), "blue", lw=1.5, label="n(t) — gate driven")
    ax.axhline(np.log10(1e19), color="red", ls="--", lw=1, label="Metallic breakdown")
    ax.axhline(np.log10(1e14), color="green", ls="--", lw=1, label="Depletion floor")
    ax.fill_between(t, np.log10(1e14), np.log10(1e18), alpha=0.08, color="blue",
                    label="CMOS basin")
    ax.set_xlabel("Time (a.u.)")
    ax.set_ylabel("log₁₀(n) [cm⁻³]")
    ax.set_title("Transistor Switching — Loop in S-Space\n(never crosses metallic boundary)")
    ax.legend(fontsize=8)

    # Panel 4: Phase portrait in (n, d) space with flow arrows
    ax = axes[1, 1]
    n_grid = np.logspace(14, 20, 15)
    d_grid = np.linspace(0, 0.8, 15)
    NG, DG = np.meshgrid(np.log10(n_grid), d_grid)
    # Flow: dn/dt proportional to (n_eq - n), dd/dt > 0
    U = (np.log10(n_eq) - NG) * 0.3
    V = np.ones_like(DG) * 0.02
    ax.quiver(NG, DG, U, V, alpha=0.6, color="gray")
    # Mark attractor basins
    ax.annotate("CMOS\nbasin", xy=(17, 0.15), fontsize=9, color="blue",
                ha="center",
                bbox=dict(boxstyle="round", facecolor="lightblue", alpha=0.6))
    ax.annotate("Metallic\nzone", xy=(20, 0.15), fontsize=9, color="red",
                ha="center",
                bbox=dict(boxstyle="round", facecolor="lightyellow", alpha=0.6))
    ax.annotate("Defect\nzone", xy=(17, 0.75), fontsize=9, color="orange",
                ha="center",
                bbox=dict(boxstyle="round", facecolor="lightyellow", alpha=0.6))
    ax.set_xlabel("log₁₀(n) [cm⁻³]")
    ax.set_ylabel("Defect density d")
    ax.set_title("Phase Portrait — Flow on Silicon Manifold")
    ax.set_xlim(14, 21)
    ax.set_ylim(0, 0.9)

    plt.tight_layout()
    savefig("silicon_manifold_flow")


# ─────────────────────────────────────────────────────────────────────────────
# Simulation 4: Fabrication Trajectories
# ─────────────────────────────────────────────────────────────────────────────

@sim("fabrication_trajectories",
     "Fabrication Trajectories — Steering S(t) to Target Basins")
def fabrication_trajectories():
    fig, axes = plt.subplots(2, 2, figsize=(13, 10))
    fig.suptitle("Fabrication as Trajectory Design in S-Space", fontsize=14)

    # Three fabrication paths: CMOS, Photonic, Quantum dot
    # Each starts from raw silicon: high d, uncontrolled n, ℓ=3

    def make_trajectory(target, n_steps=100):
        """Simulate a fabrication path to a target regime."""
        t = np.linspace(0, 1, n_steps)
        if target == "cmos":
            n = 1e15 + (1e17 - 1e15) * t          # ion implantation
            d = 0.8 * np.exp(-5 * t) + 0.05        # annealing removes defects
            l = np.ones(n_steps) * 3.0
            k_e = 0.2 + 0.8 * t
            k_o = np.ones(n_steps) * 0.1
        elif target == "photonic":
            n = 1e15 * np.ones(n_steps)             # undoped
            d = 0.8 * np.exp(-5 * t) + 0.02
            l = np.ones(n_steps) * 2.5              # thin film
            k_e = 0.3 * np.ones(n_steps)
            k_o = 0.1 + 1.5 * t                    # optical coupling grows
        elif target == "quantum":
            n = 1e16 * np.ones(n_steps)
            d = 0.8 * np.exp(-8 * t) + 0.01        # ultra-clean
            l = 3.0 - 2.8 * t                      # dimension reduction
            k_e = 0.5 * np.ones(n_steps)
            k_o = 0.1 * np.ones(n_steps)
        return t, n, d, l, k_e, k_o

    colors = {"cmos": "blue", "photonic": "green", "quantum": "purple"}
    labels = {"cmos": "CMOS (ion implant + anneal)",
              "photonic": "Photonic (thin film + optical coupling)",
              "quantum": "Quantum dot (dimension reduction)"}

    # Panel 1: n trajectory
    ax = axes[0, 0]
    for target in ["cmos", "photonic", "quantum"]:
        t, n, d, l, k_e, k_o = make_trajectory(target)
        ax.semilogy(t, n, color=colors[target], lw=2, label=labels[target])
    ax.set_xlabel("Fabrication progress")
    ax.set_ylabel("Carrier density n [cm⁻³]")
    ax.set_title("n(t) — Doping Trajectory")
    ax.legend(fontsize=8)

    # Panel 2: d trajectory
    ax = axes[0, 1]
    for target in ["cmos", "photonic", "quantum"]:
        t, n, d, l, k_e, k_o = make_trajectory(target)
        ax.plot(t, d, color=colors[target], lw=2, label=labels[target])
    ax.set_xlabel("Fabrication progress")
    ax.set_ylabel("Defect density d")
    ax.set_title("d(t) — Defect Reduction (Annealing)")
    ax.legend(fontsize=8)

    # Panel 3: ℓ and κ trajectories
    ax = axes[1, 0]
    for target in ["cmos", "photonic", "quantum"]:
        t, n, d, l, k_e, k_o = make_trajectory(target)
        ax.plot(t, l, color=colors[target], lw=2, label=f"ℓ — {target}")
    ax.set_xlabel("Fabrication progress")
    ax.set_ylabel("Effective dimensionality ℓ")
    ax.set_title("ℓ(t) — Dimensional Engineering")
    ax.legend(fontsize=8)

    # Panel 4: Phase portrait showing all three trajectories
    ax = axes[1, 1]
    for target in ["cmos", "photonic", "quantum"]:
        t, n, d, l, k_e, k_o = make_trajectory(target)
        ax.plot(np.log10(n), d, color=colors[target], lw=2.5,
                label=labels[target], alpha=0.85)
        ax.plot(np.log10(n[0]), d[0], "o", color=colors[target], ms=10)
        ax.plot(np.log10(n[-1]), d[-1], "*", color=colors[target], ms=14)
    ax.set_xlabel("log₁₀(n) [cm⁻³]")
    ax.set_ylabel("Defect density d")
    ax.set_title("Fabrication Paths in (n, d) Phase Space\n● = start, ★ = target basin")
    ax.legend(fontsize=7)
    # Basin annotations
    ax.annotate("CMOS\nbasin", xy=(17.2, 0.12), fontsize=9, color="blue",
                bbox=dict(boxstyle="round", facecolor="lightblue", alpha=0.4))
    ax.annotate("Photonic\nbasin", xy=(15.2, 0.05), fontsize=9, color="green",
                bbox=dict(boxstyle="round", facecolor="lightgreen", alpha=0.4))
    ax.annotate("Quantum\nbasin", xy=(16.2, 0.02), fontsize=9, color="purple",
                bbox=dict(boxstyle="round", facecolor="lavender", alpha=0.4))

    plt.tight_layout()
    savefig("fabrication_trajectories")


# ─────────────────────────────────────────────────────────────────────────────
# Simulation 5: Full Geometry → Binary Pipeline
# ─────────────────────────────────────────────────────────────────────────────

@sim("geometry_to_binary_pipeline",
     "Geometry → Silicon → Graph → Binary — Full Pipeline Demo")
def geometry_to_binary_pipeline():
    fig, axes = plt.subplots(2, 3, figsize=(16, 10))
    fig.suptitle("Geometry → Silicon State → Graph → Binary Logic Pipeline", fontsize=14)

    # Generate 4 different geometry fields
    np.random.seed(42)
    x = np.linspace(0, 1, 32)
    y = np.linspace(0, 1, 32)
    XX, YY = np.meshgrid(x, y)

    fields = {
        "Smooth wave\n(photonic)":
            np.sin(4 * np.pi * XX) * np.cos(4 * np.pi * YY) * 0.5 + 0.5,
        "High variance\n(defect-dominated)":
            np.random.rand(32, 32),
        "Dense lattice\n(semiconductor)":
            0.5 + 0.3 * np.sin(10 * np.pi * XX) * np.sin(10 * np.pi * YY),
        "Sparse dot\n(quantum confinement)":
            np.exp(-((XX - 0.5)**2 + (YY - 0.5)**2) / 0.01) * 0.1 + 0.01,
    }

    REGIME_COLORS = {
        "semiconductor":       "#2196F3",
        "metallic_breakdown":  "#F44336",
        "quantum_confinement": "#9C27B0",
        "photonic_transport":  "#4CAF50",
        "defect_dominated":    "#FF9800",
    }

    results = []
    for name, field in fields.items():
        S = geometry_to_silicon(field)
        G = silicon_to_graph(S, n_nodes=8)
        bits = graph_to_binary(G, S)
        results.append((name, field, S, G, bits))

    # Panel 1: Input geometry fields
    ax = axes[0, 0]
    ax.axis("off")
    ax.set_title("Input Geometry Fields", fontsize=11)
    for i, (name, field, S, G, bits) in enumerate(results):
        inset = ax.inset_axes([0.02 + (i % 2) * 0.5, 0.52 - (i // 2) * 0.5, 0.44, 0.44])
        inset.imshow(field, cmap="viridis", origin="lower")
        inset.set_title(name, fontsize=7)
        inset.axis("off")

    # Panel 2: Silicon states
    ax = axes[0, 1]
    ax.axis("off")
    ax.set_title("Extracted Silicon States", fontsize=11)
    rows = [["Field", "n [cm⁻³]", "d", "ℓ", "Regime"]]
    for name, field, S, G, bits in results:
        rows.append([
            name.split("\n")[0],
            f"{S.n:.1e}",
            f"{S.d:.2f}",
            f"{S.l:.2f}",
            S.regime().replace("_", " "),
        ])
    tbl = ax.table(cellText=rows[1:], colLabels=rows[0],
                   loc="center", cellLoc="center")
    tbl.auto_set_font_size(False)
    tbl.set_fontsize(8)
    tbl.scale(1, 1.8)
    # Color regime cells
    for i, (_, _, S, _, _) in enumerate(results):
        color = REGIME_COLORS.get(S.regime(), "white")
        tbl[i + 1, 4].set_facecolor(color)
        tbl[i + 1, 4].set_text_props(color="white")

    # Panel 3: Computational graphs
    ax = axes[0, 2]
    ax.axis("off")
    ax.set_title("Computational Graphs (from S)", fontsize=11)
    for i, (name, field, S, G, bits) in enumerate(results):
        inset = ax.inset_axes([0.02 + (i % 2) * 0.5, 0.52 - (i // 2) * 0.5, 0.44, 0.44])
        pos = nx.spring_layout(G, seed=42)
        node_colors = [REGIME_COLORS.get(S.regime(), "gray")] * len(G.nodes)
        nx.draw_networkx(G, pos, ax=inset, node_color=node_colors,
                         node_size=100, with_labels=False, edge_color="gray",
                         width=0.5, alpha=0.8)
        inset.set_title(f"{name.split(chr(10))[0]}\n{S.regime()[:12]}", fontsize=6)
        inset.axis("off")

    # Panel 4: Binary outputs
    ax = axes[1, 0]
    ax.set_title("Binary Logic Output per Field", fontsize=11)
    for i, (name, field, S, G, bits) in enumerate(results):
        ax.barh(i, sum(bits), color=REGIME_COLORS.get(S.regime(), "gray"),
                label=f"{name.split(chr(10))[0]} ({S.regime()[:8]})")
        ax.text(sum(bits) + 0.05, i, f"{bits}", fontsize=7, va="center")
    ax.set_yticks(range(len(results)))
    ax.set_yticklabels([r[0].split("\n")[0] for r in results], fontsize=8)
    ax.set_xlabel("Number of 1-bits")
    ax.legend(fontsize=7, loc="lower right")

    # Panel 5: Layout output
    ax = axes[1, 1]
    ax.set_title("Silicon Layout Routing", fontsize=11)
    for i, (name, field, S, G, bits) in enumerate(results):
        routing = "photonic" if S.k.get("optical", 0) > 0.5 else "metal"
        color = "green" if routing == "photonic" else "blue"
        ax.barh(i, 1, color=color, alpha=0.7)
        ax.text(0.05, i, f"{name.split(chr(10))[0]} → {routing} routing",
                va="center", fontsize=9)
    ax.set_xlim(0, 1.5)
    ax.set_yticks([])
    ax.set_xlabel("")
    ax.axvline(0, color="black", lw=0.5)

    # Panel 6: Pipeline summary
    ax = axes[1, 2]
    ax.axis("off")
    pipeline_text = (
        "PIPELINE SUMMARY\n\n"
        "Step 1: Geometry Field\n"
        "  ↓  Extract (mean, var, std, grad)\n\n"
        "Step 2: Silicon State S=(n,d,ℓ,κ)\n"
        "  ↓  Classify regime\n\n"
        "Step 3: Computational Graph G\n"
        "  Nodes = silicon states\n"
        "  Edges = coupling κᵢⱼ\n"
        "  ↓  Regime-dependent evaluation\n\n"
        "Step 4: Binary Logic Stream\n"
        "  ↓  Map to fabrication constraints\n\n"
        "Step 5: Silicon Layout\n"
        "  Routing: photonic vs metal\n"
        "  Doping: n → mask constraints\n"
        "  Defects: d → yield model"
    )
    ax.text(0.05, 0.95, pipeline_text, transform=ax.transAxes,
            fontsize=9, va="top", fontfamily="monospace",
            bbox=dict(boxstyle="round", facecolor="lightyellow", alpha=0.8))

    plt.tight_layout()
    savefig("geometry_to_binary_pipeline")


# ─────────────────────────────────────────────────────────────────────────────
# Simulation 6: Basin Stability and Failure Modes
# ─────────────────────────────────────────────────────────────────────────────

@sim("basin_stability",
     "Basin Stability — Stability Margins, Noise Sensitivity, Device Failure")
def basin_stability():
    fig, axes = plt.subplots(2, 2, figsize=(13, 10))
    fig.suptitle("Basin Stability: Distance to Boundary, Noise, and Failure Modes", fontsize=14)

    # Panel 1: Stability margin = distance to nearest phase boundary
    ax = axes[0, 0]
    n_vals = np.logspace(14, 21, 200)
    d_vals = np.linspace(0, 1, 200)
    NN, DD = np.meshgrid(n_vals, d_vals)
    stab = np.vectorize(lambda n, d: SiliconState(n=n, d=d, l=3,
                        k={"electrical": 1, "optical": 0.2, "thermal": 0.3}).stability())(NN, DD)
    cf = ax.contourf(np.log10(n_vals), d_vals, stab, levels=25, cmap="RdYlGn")
    plt.colorbar(cf, ax=ax, label="Stability metric")
    ax.set_xlabel("log₁₀(n) [cm⁻³]")
    ax.set_ylabel("Defect density d")
    ax.set_title("Stability Margin in (n, d) Space\n(green = stable CMOS basin)")
    ax.annotate("Maximum\nstability", xy=(17, 0.05), fontsize=9, color="darkgreen",
                ha="center",
                bbox=dict(boxstyle="round", facecolor="lightgreen", alpha=0.5))

    # Panel 2: Noise sensitivity — trajectory escape probability
    ax = axes[0, 1]
    np.random.seed(0)
    n_steps = 500
    n0 = 1e17
    noise_levels = [0.01, 0.05, 0.15, 0.3]
    for sigma in noise_levels:
        n_traj = [n0]
        for _ in range(n_steps - 1):
            dn = -0.05 * (n_traj[-1] - 1e17) + sigma * 1e17 * np.random.randn()
            n_traj.append(max(1e13, n_traj[-1] + dn))
        escaped = [n > 1e19 or n < 1e14 for n in n_traj]
        escape_frac = np.cumsum(escaped) / np.arange(1, n_steps + 1)
        ax.plot(range(n_steps), escape_frac, label=f"σ = {sigma}")
    ax.set_xlabel("Time steps")
    ax.set_ylabel("Cumulative escape probability")
    ax.set_title("Noise-Driven Basin Escape\n(trajectory leaves CMOS basin)")
    ax.legend(fontsize=9)
    ax.axhline(0.5, color="red", ls="--", lw=1, label="50% failure")

    # Panel 3: Device failure as trajectory escape
    ax = axes[1, 0]
    np.random.seed(1)
    t = np.linspace(0, 200, 1000)
    # Simulate aging: slow d increase + occasional noise spikes
    d_aging = 0.05 + 0.003 * t + 0.02 * np.cumsum(np.random.randn(1000)) / 100
    d_aging = np.clip(d_aging, 0, 1)
    n_aging = 1e17 * (1 + 0.1 * np.cumsum(np.random.randn(1000)) / 100)
    n_aging = np.clip(n_aging, 1e14, 1e21)

    regimes = []
    for n, d in zip(n_aging, d_aging):
        S = SiliconState(n=n, d=d, l=3, k={"electrical": 1, "optical": 0.2, "thermal": 0.3})
        regimes.append(S.regime())

    regime_map = {"semiconductor": 0, "metallic_breakdown": 1,
                  "defect_dominated": 2, "quantum_confinement": 3, "photonic_transport": 4}
    regime_colors_list = ["#2196F3", "#F44336", "#FF9800", "#9C27B0", "#4CAF50"]
    regime_nums = [regime_map[r] for r in regimes]

    ax.scatter(t, np.log10(n_aging), c=regime_nums, cmap=matplotlib.colors.ListedColormap(
        regime_colors_list), s=3, alpha=0.7)
    ax.set_xlabel("Time (aging)")
    ax.set_ylabel("log₁₀(n) [cm⁻³]")
    ax.set_title("Device Aging Trajectory\n(color = current regime)")
    ax2 = ax.twinx()
    ax2.plot(t, d_aging, "orange", lw=1.5, alpha=0.6, label="d(t)")
    ax2.set_ylabel("Defect density d", color="orange")
    ax2.tick_params(axis="y", labelcolor="orange")

    # Panel 4: Summary table of geometric engineering concepts
    ax = axes[1, 1]
    ax.axis("off")
    concepts = [
        ["Concept", "Geometric Meaning", "Engineering Implication"],
        ["Stability margin", "Distance to phase boundary in S-space",
         "How much noise/drift before failure"],
        ["Device failure", "Trajectory escapes intended basin",
         "Reliability engineering"],
        ["Fabrication yield", "Prob. of landing in target basin",
         "Process control"],
        ["Cross-domain device", "Trajectory navigates between basins",
         "Optoelectronics, MEMS"],
        ["Noise sensitivity", "Local curvature of basin walls",
         "Thermal/shot noise tolerance"],
    ]
    tbl = ax.table(cellText=concepts[1:], colLabels=concepts[0],
                   loc="center", cellLoc="center")
    tbl.auto_set_font_size(False)
    tbl.set_fontsize(8)
    tbl.scale(1, 1.7)
    ax.set_title("Geometric Engineering Summary", pad=20)

    plt.tight_layout()
    savefig("basin_stability")


# ─────────────────────────────────────────────────────────────────────────────
# CLI
# ─────────────────────────────────────────────────────────────────────────────

def run_all():
    print(f"\n{'='*60}")
    print("  connections_sims.py — Silicon Phase-Space Framework")
    print(f"{'='*60}\n")
    for name, meta in REGISTRY.items():
        print(f"  [{name}]  {meta['title']}")
        meta["fn"]()
    print(f"\n  All plots saved to: {PLOT_DIR}\n")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Silicon Phase-Space Framework Simulations")
    parser.add_argument("--list", action="store_true",
                        help="List all available simulations")
    parser.add_argument("--sim", type=str, default=None,
                        help="Run a single simulation by name")
    args = parser.parse_args()

    if args.list:
        print(f"\n{'Name':<35} Title")
        print("-" * 80)
        for name, meta in REGISTRY.items():
            print(f"{name:<35} {meta['title']}")
        print()
    elif args.sim:
        if args.sim not in REGISTRY:
            print(f"Unknown simulation '{args.sim}'. Use --list.")
        else:
            print(f"Running [{args.sim}]: {REGISTRY[args.sim]['title']}")
            REGISTRY[args.sim]["fn"]()
    else:
        run_all()
