"""
addon_sims.py
Simulations for the concepts in Addon.md.

Covers:
  1. phase_diagram_4d       — The 4D phase diagram of physics (Λ, dim, signature, topology)
  2. dewitt_supermetric     — Distance between geometries in configuration space
  3. entanglement_curvature — Off-diagonal metric coupling as quantum entanglement
  4. signature_transition   — Holonomy / monodromy around an Ω²=0 singularity
  5. bundle_geodesics       — Geodesic flow on the space of geometries

Run all:      python addon_sims.py
Run one:      python addon_sims.py --sim entanglement_curvature
List all:     python addon_sims.py --list
"""

import argparse
import os
import warnings
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from scipy.integrate import solve_ivp
from scipy.linalg import expm

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
# SIM 1: THE 4D PHASE DIAGRAM
# ─────────────────────────────────────────────────────────────

@sim("phase_diagram_4d",
     "The 4D Phase Diagram of Physics: Λ, Dimension, Signature, Topology")
def sim_phase_diagram_4d():
    """
    Visualizes the 4-axis phase diagram from Addon.md.
    Axes: Λ (coupling), dimension, signature (Riemannian↔Lorentzian), topology χ.
    Shows where known physics lives in this space.
    """
    fig = plt.figure(figsize=(16, 12))
    fig.suptitle("The 4D Phase Diagram of Physics\n"
                 "Quantum Mechanics is just one phase of a larger geometric structure",
                 fontsize=13, fontweight="bold")

    # ── Panel 1: Λ vs Topology (χ) ──
    ax1 = fig.add_subplot(2, 3, 1)
    Lambda_vals = np.logspace(-2, 2, 300)
    chi_vals    = np.linspace(-2, 4, 300)
    L, C = np.meshgrid(Lambda_vals, chi_vals)

    # Phase boundaries
    # Quantum: Λ<0.5, χ>0 (compact)
    # Soliton: 0.5<Λ<5, any χ
    # Chaotic: Λ>5
    # Topological: χ<0 (non-compact)
    phase = np.zeros_like(L)
    phase[L < 0.5]                        = 1   # Quantum
    phase[(L >= 0.5) & (L < 5.0)]         = 2   # Soliton/Nonlinear
    phase[L >= 5.0]                        = 3   # Chaotic
    phase[(L < 0.5) & (C < 0)]            = 4   # Topological QFT
    phase[(L >= 5.0) & (C < 0)]           = 5   # Chaotic + non-compact

    cmap = matplotlib.colors.ListedColormap(
        ["royalblue", "darkorange", "crimson", "mediumseagreen", "darkred"])
    ax1.contourf(np.log10(L), C, phase, levels=[-0.5,0.5,1.5,2.5,3.5,4.5,5.5],
                 cmap=cmap, alpha=0.75)
    ax1.axvline(np.log10(0.5), color="white", linewidth=1.5, linestyle="--")
    ax1.axvline(np.log10(5.0), color="white", linewidth=1.5, linestyle=":")
    ax1.axhline(0, color="white", linewidth=1.5, linestyle="-.")

    # Known physics labels
    labels = [
        (np.log10(0.1), 2.0,  "Quantum\nMechanics",  "white"),
        (np.log10(1.5), 1.5,  "Solitons /\nNonlinear QM", "white"),
        (np.log10(15),  1.5,  "Chaos /\nTurbulence",  "white"),
        (np.log10(0.1), -1.0, "Topological\nQFT",     "white"),
        (np.log10(15),  -1.0, "Chaotic\nGravity",     "white"),
    ]
    for x, y, label, color in labels:
        ax1.text(x, y, label, color=color, fontsize=7.5, ha="center", va="center",
                 fontweight="bold")

    ax1.set_xlabel("log₁₀(Λ)  [coupling strength]")
    ax1.set_ylabel("Euler characteristic χ  [topology]")
    ax1.set_title("Phase Diagram: Λ vs Topology")
    ax1.set_xlim(-2, 2)

    # ── Panel 2: Λ vs Signature ──
    ax2 = fig.add_subplot(2, 3, 2)
    sig_vals = np.linspace(-1, 1, 300)   # -1=Lorentzian, +1=Riemannian
    L2, S = np.meshgrid(Lambda_vals, sig_vals)

    phase2 = np.zeros_like(L2)
    phase2[L2 < 0.5]                                  = 1  # Quantum (Riemannian)
    phase2[(L2 >= 0.5) & (L2 < 5.0)]                  = 2  # Nonlinear
    phase2[L2 >= 5.0]                                  = 3  # Chaotic
    phase2[(S < 0) & (L2 < 0.5)]                       = 6  # QFT (Lorentzian)
    phase2[(S < 0) & (L2 >= 0.5) & (L2 < 5.0)]        = 7  # GR
    phase2[(S < 0) & (L2 >= 5.0)]                      = 8  # Black holes / chaotic GR

    cmap2 = matplotlib.colors.ListedColormap([
        "royalblue", "darkorange", "crimson",
        "steelblue", "steelblue", "steelblue",
        "teal", "darkcyan", "navy"])
    ax2.contourf(np.log10(L2), S, phase2,
                 levels=[-0.5,0.5,1.5,2.5,5.5,6.5,7.5,8.5],
                 cmap=cmap2, alpha=0.75)
    ax2.axhline(0, color="white", linewidth=2, linestyle="-", label="Signature boundary")
    ax2.axvline(np.log10(0.5), color="white", linewidth=1.5, linestyle="--")
    ax2.axvline(np.log10(5.0), color="white", linewidth=1.5, linestyle=":")

    sig_labels = [
        (np.log10(0.1),  0.6, "Quantum\nMechanics",   "white"),
        (np.log10(1.5),  0.6, "Solitons",              "white"),
        (np.log10(15),   0.6, "Chaos",                 "white"),
        (np.log10(0.1), -0.5, "QFT\n(Minkowski)",     "white"),
        (np.log10(1.5), -0.5, "General\nRelativity",  "white"),
        (np.log10(15),  -0.5, "Black Holes\n/ Chaos", "white"),
    ]
    for x, y, label, color in sig_labels:
        ax2.text(x, y, label, color=color, fontsize=7.5, ha="center", va="center",
                 fontweight="bold")

    ax2.set_xlabel("log₁₀(Λ)")
    ax2.set_ylabel("Signature  [+1=Riemannian, -1=Lorentzian]")
    ax2.set_title("Phase Diagram: Λ vs Signature")
    ax2.set_xlim(-2, 2)

    # ── Panel 3: Dimension vs Λ ──
    ax3 = fig.add_subplot(2, 3, 3)
    dim_vals = np.array([1, 2, 3, 4, 5, 6, 10, 11])
    Lambda_range = np.logspace(-2, 2, 200)
    # In d dimensions, the Weyl tensor vanishes for d<4 (conformally trivial)
    # Quantum regime requires Weyl suppression → d<4 or Λ<<1
    for d in dim_vals:
        weyl_threshold = 0.5 * (d / 4.0)**2  # schematic: Weyl grows with d
        color = plt.cm.plasma(d / 11.0)
        ax3.semilogx(Lambda_range,
                     np.where(Lambda_range < weyl_threshold,
                              np.ones_like(Lambda_range) * d,
                              np.ones_like(Lambda_range) * np.nan),
                     color=color, linewidth=4, alpha=0.8)
        ax3.semilogx(Lambda_range,
                     np.where(Lambda_range >= weyl_threshold,
                               np.ones_like(Lambda_range) * d,
                               np.ones_like(Lambda_range) * np.nan),
                     color=color, linewidth=4, alpha=0.3, linestyle="--")
        ax3.text(1.5e-2, d + 0.1, f"d={d}", fontsize=7, color=color)

    ax3.axvline(0.5, color="gray", linestyle="--", linewidth=1.5, alpha=0.7,
                label="Λ=0.5 (QM boundary)")
    ax3.axvline(5.0, color="gray", linestyle=":",  linewidth=1.5, alpha=0.7,
                label="Λ=5 (chaos threshold)")
    ax3.fill_betweenx([0.5, 4.5], 1e-2, 0.5, alpha=0.08, color="royalblue")
    ax3.text(0.05, 2.5, "Quantum\nphase\n(d<4, Λ<0.5)", fontsize=8,
             ha="center", color="royalblue", fontweight="bold")
    ax3.set_xlabel("Λ (coupling strength)")
    ax3.set_ylabel("Spacetime dimension d")
    ax3.set_title("Quantum Phase Boundary vs Dimension")
    ax3.legend(fontsize=7)
    ax3.grid(alpha=0.3)
    ax3.set_xlim(1e-2, 1e2)

    # ── Panel 4: The 4D axes summary ──
    ax4 = fig.add_subplot(2, 3, 4)
    ax4.axis("off")
    rows = [
        ["Axis", "Low end", "High end", "QM lives at..."],
        ["Dimension d", "d=1,2 (trivial)", "d=4+ (Weyl)", "d<4"],
        ["Signature", "Riemannian (+)", "Lorentzian (−)", "Riemannian"],
        ["Coupling Λ", "Λ≪1 (linear QM)", "Λ≫1 (chaos)", "Λ<0.5"],
        ["Topology χ", "χ<0 (open)", "χ>0 (compact)", "χ>0"],
    ]
    col_w = [0.22, 0.26, 0.26, 0.26]
    y = 0.92
    for row in rows:
        x = 0.02
        bold = (row == rows[0])
        for cell, w in zip(row, col_w):
            ax4.text(x, y, cell, transform=ax4.transAxes,
                     fontsize=8.5, fontweight="bold" if bold else "normal",
                     verticalalignment="top",
                     color="navy" if bold else "black")
            x += w
        y -= 0.16
    ax4.set_title("The Four Axes of the Phase Diagram", fontsize=10,
                  fontweight="bold")
    ax4.add_patch(plt.Rectangle((0, 0), 1, 1, fill=False,
                                 edgecolor="lightgray", linewidth=1,
                                 transform=ax4.transAxes))

    # ── Panel 5: QM as a corner of the diagram ──
    ax5 = fig.add_subplot(2, 3, 5)
    theta = np.linspace(0, 2 * np.pi, 200)
    # Draw the 4 axes as a radar/spider plot
    axes_labels = ["Low Λ\n(weak coupling)", "Riemannian\nsignature",
                   "Low dim\n(d<4)", "Compact\ntopology (χ>0)"]
    N = 4
    angles = np.linspace(0, 2 * np.pi, N, endpoint=False)

    # QM point (all low/compact)
    qm_vals    = np.array([0.9, 0.9, 0.9, 0.9])
    # GR point
    gr_vals    = np.array([0.3, 0.1, 0.7, 0.5])
    # Chaos point
    chaos_vals = np.array([0.1, 0.5, 0.5, 0.3])
    # String theory point
    str_vals   = np.array([0.4, 0.6, 0.1, 0.2])

    def radar_plot(ax, values, label, color, alpha=0.3):
        vals = np.concatenate([values, [values[0]]])
        angs = np.concatenate([angles, [angles[0]]])
        ax.plot(angs, vals, color=color, linewidth=2, label=label)
        ax.fill(angs, vals, color=color, alpha=alpha)

    ax5 = plt.subplot(2, 3, 5, projection="polar")
    radar_plot(ax5, qm_vals,    "Quantum Mechanics", "royalblue")
    radar_plot(ax5, gr_vals,    "General Relativity", "darkorange")
    radar_plot(ax5, chaos_vals, "Chaos / Turbulence", "crimson")
    radar_plot(ax5, str_vals,   "String Theory",       "mediumseagreen")
    ax5.set_xticks(angles)
    ax5.set_xticklabels(axes_labels, fontsize=8)
    ax5.set_yticks([0.25, 0.5, 0.75, 1.0])
    ax5.set_yticklabels(["0.25", "0.5", "0.75", "1.0"], fontsize=6)
    ax5.set_title("Known Theories as Points\nin the Phase Diagram",
                  fontsize=9, fontweight="bold", pad=15)
    ax5.legend(loc="upper right", bbox_to_anchor=(1.4, 1.1), fontsize=7)

    # ── Panel 6: Phase transition boundaries ──
    ax6 = fig.add_subplot(2, 3, 6)
    x = np.linspace(0, 10, 500)
    # Schematic energy landscape with 3 minima (QM, soliton, chaos)
    V = (np.cos(x) + 0.3 * np.cos(2 * x) + 0.1 * np.cos(3 * x)
         - 0.05 * x + 0.5 * np.exp(-0.3 * x))
    ax6.plot(x, V, color="darkblue", linewidth=2)
    ax6.fill_between(x, V, V.min() - 0.2, alpha=0.1, color="royalblue")
    # Mark the three minima
    minima_x = [0.5, 3.2, 6.3]
    minima_labels = ["Quantum\nPhase", "Soliton\nPhase", "Chaotic\nPhase"]
    minima_colors = ["royalblue", "darkorange", "crimson"]
    for mx, ml, mc in zip(minima_x, minima_labels, minima_colors):
        idx = np.argmin(np.abs(x - mx))
        ax6.plot(x[idx], V[idx], "o", color=mc, markersize=10, zorder=5)
        ax6.annotate(ml, xy=(x[idx], V[idx]),
                     xytext=(x[idx], V[idx] - 0.4),
                     ha="center", fontsize=8, color=mc, fontweight="bold",
                     arrowprops=dict(arrowstyle="->", color=mc, lw=1.5))
    ax6.set_xlabel("Geometric configuration (schematic)")
    ax6.set_ylabel("Effective potential V")
    ax6.set_title("Phase Transitions as Potential Barriers")
    ax6.grid(alpha=0.3)
    ax6.set_xlim(0, 9)

    plt.tight_layout()
    savefig("phase_diagram_4d", fig)


# ─────────────────────────────────────────────────────────────
# SIM 2: DEWITT SUPERMETRIC — DISTANCE BETWEEN GEOMETRIES
# ─────────────────────────────────────────────────────────────

@sim("dewitt_supermetric",
     "DeWitt Supermetric: Measuring Distance Between Spacetimes")
def sim_dewitt_supermetric():
    """
    Computes the DeWitt supermetric distance between different 1D metric
    configurations (conformal factors Ω²) and visualizes the geometry
    of the configuration space S.
    """
    N = 64
    x = np.linspace(-5, 5, N)
    dx = x[1] - x[0]

    def make_metric(alpha, psi_profile):
        """Conformal factor Ω² = 1 + α ψ²"""
        return 1.0 + alpha * psi_profile**2

    def dewitt_distance(g1, g2, g_ref, lam=0.5, d=1):
        """
        Approximate DeWitt supermetric distance between two conformal metrics.
        G_ijkl δg δg = (δg)² - λ (tr δg)²  (in 1D: scalar)
        """
        dg = g2 - g1
        g_bar = 0.5 * (g1 + g2)
        # DeWitt integrand: (δΩ²)² / Ω^(2+2λd)
        integrand = dg**2 / (g_bar**(1 + lam * d) + 1e-10)
        return np.sqrt(np.sum(integrand) * dx)

    # Build a family of geometries parameterized by α
    alpha_vals = np.linspace(-2.0, 2.0, 40)
    psi_gauss  = np.exp(-x**2 / 2.0)
    psi_double = np.exp(-(x - 1.5)**2) + np.exp(-(x + 1.5)**2)
    psi_flat   = np.ones_like(x) * 0.3

    profiles = {
        "Gaussian ψ":      psi_gauss  / np.max(np.abs(psi_gauss)),
        "Double-peak ψ":   psi_double / np.max(np.abs(psi_double)),
        "Flat ψ":          psi_flat,
    }

    fig, axes = plt.subplots(2, 3, figsize=(15, 9))
    fig.suptitle("DeWitt Supermetric: Distance Between Geometries",
                 fontsize=13, fontweight="bold")

    # ── Panel 1: Metric profiles ──
    ax = axes[0, 0]
    for name, psi in profiles.items():
        g = make_metric(1.0, psi)
        ax.plot(x, g, linewidth=2, label=f"Ω²({name})")
    ax.axhline(1.0, color="gray", linestyle="--", alpha=0.5, label="Flat (Ω²=1)")
    ax.set_xlabel("x"); ax.set_ylabel("Ω²(x)")
    ax.set_title("Metric Profiles (α=1)")
    ax.legend(fontsize=8); ax.grid(alpha=0.3)

    # ── Panel 2: Distance matrix between geometries ──
    ax = axes[0, 1]
    n_alpha = 20
    alpha_sample = np.linspace(-1.5, 1.5, n_alpha)
    dist_matrix = np.zeros((n_alpha, n_alpha))
    psi_ref = psi_gauss / np.max(np.abs(psi_gauss))
    g_ref   = make_metric(0.0, psi_ref)  # flat reference

    for i, a1 in enumerate(alpha_sample):
        for j, a2 in enumerate(alpha_sample):
            g1 = make_metric(a1, psi_ref)
            g2 = make_metric(a2, psi_ref)
            dist_matrix[i, j] = dewitt_distance(g1, g2, g_ref)

    im = ax.imshow(dist_matrix, origin="lower", aspect="auto",
                   extent=[alpha_sample[0], alpha_sample[-1],
                            alpha_sample[0], alpha_sample[-1]],
                   cmap="plasma")
    plt.colorbar(im, ax=ax, label="DeWitt distance")
    ax.set_xlabel("α₁"); ax.set_ylabel("α₂")
    ax.set_title("Distance Matrix D(α₁, α₂)\nbetween Gaussian geometries")

    # ── Panel 3: Distance from flat geometry vs α ──
    ax = axes[0, 2]
    for name, psi in profiles.items():
        psi_n = psi / np.max(np.abs(psi))
        dists = []
        for alpha in alpha_vals:
            g = make_metric(alpha, psi_n)
            dists.append(dewitt_distance(g_ref, g, g_ref))
        ax.plot(alpha_vals, dists, linewidth=2, label=name)
    ax.axvline(0, color="gray", linestyle="--", alpha=0.5)
    ax.set_xlabel("α (coupling)"); ax.set_ylabel("D(g_flat, g_α)")
    ax.set_title("Distance from Flat Geometry vs α")
    ax.legend(fontsize=8); ax.grid(alpha=0.3)

    # ── Panel 4: Geodesic in configuration space ──
    ax = axes[1, 0]
    # Geodesic: linear interpolation in α (approximate)
    alpha_path = np.linspace(-1.5, 1.5, 50)
    psi_n = psi_gauss / np.max(np.abs(psi_gauss))
    # Compute cumulative arc length along path
    arc_lengths = [0.0]
    for k in range(1, len(alpha_path)):
        g1 = make_metric(alpha_path[k-1], psi_n)
        g2 = make_metric(alpha_path[k],   psi_n)
        arc_lengths.append(arc_lengths[-1] + dewitt_distance(g1, g2, g_ref))
    ax.plot(alpha_path, arc_lengths, color="darkblue", linewidth=2)
    ax.fill_between(alpha_path, arc_lengths, alpha=0.15, color="royalblue")
    ax.axvline(0, color="gray", linestyle="--", alpha=0.5, label="Flat geometry")
    ax.set_xlabel("α (along path)"); ax.set_ylabel("Cumulative arc length s")
    ax.set_title("Arc Length Along α-Path\n(Geodesic in Config Space)")
    ax.legend(fontsize=8); ax.grid(alpha=0.3)

    # ── Panel 5: DeWitt λ parameter effect ──
    ax = axes[1, 1]
    lambda_vals = [0.1, 0.5, 1.0, 2.0]
    for lam in lambda_vals:
        dists = []
        for alpha in alpha_vals:
            g = make_metric(alpha, psi_n)
            dists.append(dewitt_distance(g_ref, g, g_ref, lam=lam))
        ax.plot(alpha_vals, dists, linewidth=2, label=f"λ={lam}")
    ax.axvline(0, color="gray", linestyle="--", alpha=0.5)
    ax.set_xlabel("α"); ax.set_ylabel("DeWitt distance")
    ax.set_title("Effect of DeWitt λ Parameter\n(λ>1/d → Lorentzian superspace)")
    ax.legend(fontsize=8); ax.grid(alpha=0.3)

    # ── Panel 6: Conceptual diagram of S ──
    ax = axes[1, 2]
    ax.axis("off")
    # Draw a schematic of the bundle
    theta = np.linspace(0, 2 * np.pi, 200)
    # Base space (circle = space of metrics)
    ax.plot(np.cos(theta) * 2, np.sin(theta) * 0.5, color="darkblue",
            linewidth=2, label="Base space G (all metrics)")
    # Fibers at several points
    for angle in np.linspace(0, 2 * np.pi, 8, endpoint=False):
        bx = np.cos(angle) * 2
        by = np.sin(angle) * 0.5
        # Fiber direction (perpendicular to base circle)
        fx = -np.sin(angle) * 0.6
        fy =  np.cos(angle) * 0.6
        ax.annotate("", xy=(bx + fx, by + fy), xytext=(bx, by),
                    arrowprops=dict(arrowstyle="->", color="darkorange", lw=1.5))
    ax.plot([], [], color="darkorange", linewidth=2, label="Fibers (conformal rescalings)")
    # Mark the flat section
    ax.plot([0], [0], "k*", markersize=12, label="Flat section (Ω²=1)")
    ax.set_xlim(-3.5, 3.5); ax.set_ylim(-1.8, 1.8)
    ax.set_aspect("equal")
    ax.set_title("Bundle B → G\n(Schematic)", fontsize=10, fontweight="bold")
    ax.legend(loc="lower center", fontsize=7)

    plt.tight_layout()
    savefig("dewitt_supermetric", fig)


# ─────────────────────────────────────────────────────────────
# SIM 3: ENTANGLEMENT AS GEOMETRIC CURVATURE
# ─────────────────────────────────────────────────────────────

@sim("entanglement_curvature",
     "Entanglement as Off-Diagonal Metric Curvature")
def sim_entanglement_curvature():
    """
    Simulates two coupled geometric systems (System A and B).
    Shows how coupling creates off-diagonal metric components
    (entanglement curvature F_ent) and how this relates to
    standard quantum entanglement entropy.
    """
    N = 64
    x = np.linspace(-4, 4, N)
    dx = x[1] - x[0]

    def evolve_psi(psi, alpha, beta, D, dt, n_steps):
        """Simple 1D PDE evolution: ∂ψ/∂t = D∇²ψ - β/(2α) ψ(1+αψ²)"""
        dx_loc = x[1] - x[0]
        for _ in range(n_steps):
            lap = np.gradient(np.gradient(psi, dx_loc), dx_loc)
            if abs(alpha) > 1e-10:
                reaction = -(beta / (2 * alpha)) * psi * (1 + alpha * psi**2)
            else:
                reaction = np.zeros_like(psi)
            dpsi = D * lap + reaction
            psi = psi + dt * dpsi
            psi = np.clip(psi, -1e3, 1e3)
            norm = np.sqrt(np.sum(psi**2) * dx_loc)
            if norm > 1e-12:
                psi /= norm
        return psi

    def compute_joint_metric(psi_A, psi_B, alpha_A, alpha_B, coupling):
        """
        Joint metric G_AB for two systems.
        G = diag(Ω²_A, Ω²_B) + coupling * off-diagonal term.
        """
        Omega_A = 1.0 + alpha_A * psi_A**2
        Omega_B = 1.0 + alpha_B * psi_B**2
        # Off-diagonal: coupling * ψ_A * ψ_B (entanglement term)
        off_diag = coupling * psi_A * psi_B
        return Omega_A, Omega_B, off_diag

    def entanglement_curvature(off_diag, dx_loc):
        """F_ent ≈ d(off_diag) — measures non-factorizability"""
        return np.gradient(off_diag, dx_loc)

    def entanglement_entropy(off_diag, dx_loc):
        """S_ent ≈ (1/8π) ∫ F_ent² dx (schematic)"""
        F = entanglement_curvature(off_diag, dx_loc)
        return np.sum(F**2) * dx_loc / (8 * np.pi)

    # Initial states
    psi_A0 = np.exp(-x**2 / 2.0); psi_A0 /= np.sqrt(np.sum(psi_A0**2) * dx)
    psi_B0 = np.exp(-(x - 1.0)**2 / 2.0); psi_B0 /= np.sqrt(np.sum(psi_B0**2) * dx)

    coupling_vals = np.linspace(0, 2.0, 20)
    alpha_A, alpha_B = -0.5, -0.3
    beta_A,  beta_B  =  0.5,  0.3
    D = 0.2

    fig, axes = plt.subplots(2, 3, figsize=(15, 9))
    fig.suptitle("Entanglement as Geometric Curvature\n"
                 "Off-diagonal metric components = quantum entanglement",
                 fontsize=13, fontweight="bold")

    # ── Panel 1: Individual metrics ──
    ax = axes[0, 0]
    psi_A = evolve_psi(psi_A0.copy(), alpha_A, beta_A, D, 0.005, 200)
    psi_B = evolve_psi(psi_B0.copy(), alpha_B, beta_B, D, 0.005, 200)
    Omega_A, Omega_B, _ = compute_joint_metric(psi_A, psi_B, alpha_A, alpha_B, 0.0)
    ax.plot(x, Omega_A, color="royalblue",   linewidth=2, label="Ω²_A (System A)")
    ax.plot(x, Omega_B, color="darkorange",  linewidth=2, label="Ω²_B (System B)")
    ax.axhline(1.0, color="gray", linestyle="--", alpha=0.5, label="Flat")
    ax.set_xlabel("x"); ax.set_ylabel("Ω²")
    ax.set_title("Individual Metrics (Uncoupled)")
    ax.legend(fontsize=8); ax.grid(alpha=0.3)

    # ── Panel 2: Off-diagonal coupling at different coupling strengths ──
    ax = axes[0, 1]
    for c in [0.0, 0.5, 1.0, 2.0]:
        _, _, off = compute_joint_metric(psi_A, psi_B, alpha_A, alpha_B, c)
        ax.plot(x, off, linewidth=2, label=f"coupling={c:.1f}")
    ax.axhline(0, color="gray", linestyle="--", alpha=0.5)
    ax.set_xlabel("x"); ax.set_ylabel("G_AB off-diagonal")
    ax.set_title("Off-Diagonal Metric Component\n(Entanglement Term)")
    ax.legend(fontsize=8); ax.grid(alpha=0.3)

    # ── Panel 3: Entanglement curvature F_ent ──
    ax = axes[0, 2]
    for c in [0.5, 1.0, 2.0]:
        _, _, off = compute_joint_metric(psi_A, psi_B, alpha_A, alpha_B, c)
        F_ent = entanglement_curvature(off, dx)
        ax.plot(x, F_ent, linewidth=2, label=f"coupling={c:.1f}")
    ax.axhline(0, color="gray", linestyle="--", alpha=0.5)
    ax.set_xlabel("x"); ax.set_ylabel("F_ent = d(G_AB)")
    ax.set_title("Entanglement Curvature F_ent\n(Non-zero = entangled)")
    ax.legend(fontsize=8); ax.grid(alpha=0.3)

    # ── Panel 4: Entanglement entropy vs coupling ──
    ax = axes[1, 0]
    S_ent_vals = []
    for c in coupling_vals:
        _, _, off = compute_joint_metric(psi_A, psi_B, alpha_A, alpha_B, c)
        S_ent_vals.append(entanglement_entropy(off, dx))
    ax.plot(coupling_vals, S_ent_vals, color="purple", linewidth=2.5)
    ax.fill_between(coupling_vals, S_ent_vals, alpha=0.15, color="purple")
    ax.axvline(0, color="gray", linestyle="--", alpha=0.5, label="Separable (coupling=0)")
    ax.set_xlabel("Coupling strength"); ax.set_ylabel("S_ent (geometric)")
    ax.set_title("Entanglement Entropy vs Coupling\nS_ent = (1/8π) ∫ F_ent² dx")
    ax.legend(fontsize=8); ax.grid(alpha=0.3)

    # ── Panel 5: Product vs entangled density ──
    ax = axes[1, 1]
    # Product state: ρ_AB = ρ_A ⊗ ρ_B
    rho_A = psi_A**2
    rho_B = psi_B**2
    # 2D product density
    rho_product = np.outer(rho_A, rho_B)
    # Entangled state: add off-diagonal coupling
    c_strong = 1.5
    _, _, off = compute_joint_metric(psi_A, psi_B, alpha_A, alpha_B, c_strong)
    rho_ent = rho_product + 0.3 * np.outer(psi_A * off, psi_B)
    rho_ent = np.abs(rho_ent)
    rho_ent /= rho_ent.sum() * dx**2

    im = ax.imshow(rho_ent, origin="lower", aspect="auto",
                   extent=[x[0], x[-1], x[0], x[-1]],
                   cmap="hot")
    plt.colorbar(im, ax=ax, label="ρ_AB(x_A, x_B)")
    ax.set_xlabel("x_A"); ax.set_ylabel("x_B")
    ax.set_title("Entangled Joint Density ρ_AB\n(Non-separable: ρ ≠ ρ_A ⊗ ρ_B)")

    # ── Panel 6: Separability test ──
    ax = axes[1, 2]
    # Schmidt number as function of coupling
    schmidt_vals = []
    for c in coupling_vals:
        _, _, off = compute_joint_metric(psi_A, psi_B, alpha_A, alpha_B, c)
        rho_joint = np.outer(rho_A, rho_B) + 0.1 * c * np.outer(psi_A, psi_B * off)
        rho_joint = np.abs(rho_joint)
        rho_joint /= rho_joint.sum() * dx**2
        # Schmidt rank approximation via SVD
        U, s, Vt = np.linalg.svd(rho_joint)
        s_norm = s / s.sum()
        # Effective Schmidt number = 1/Σs²
        schmidt = 1.0 / np.sum(s_norm**2)
        schmidt_vals.append(schmidt)

    ax.plot(coupling_vals, schmidt_vals, color="darkred", linewidth=2.5)
    ax.fill_between(coupling_vals, 1, schmidt_vals, alpha=0.15, color="darkred")
    ax.axhline(1.0, color="gray", linestyle="--", alpha=0.7,
               label="Schmidt rank=1 (separable)")
    ax.set_xlabel("Coupling strength")
    ax.set_ylabel("Effective Schmidt number")
    ax.set_title("Schmidt Number vs Coupling\n(>1 = entangled, non-separable)")
    ax.legend(fontsize=8); ax.grid(alpha=0.3)

    plt.tight_layout()
    savefig("entanglement_curvature", fig)


# ─────────────────────────────────────────────────────────────
# SIM 4: SIGNATURE TRANSITION AND HOLONOMY
# ─────────────────────────────────────────────────────────────

@sim("signature_transition",
     "Signature Transition: Holonomy Around Ω²=0 Singularity")
def sim_signature_transition():
    """
    Simulates what happens when Ω² = 1 + α ψ² passes through zero.
    Shows:
    - The degenerate locus in (α, ψ_max) space
    - Holonomy (monodromy) of a loop around the singularity
    - Signature change as a branch-point jump
    """
    fig, axes = plt.subplots(2, 3, figsize=(15, 9))
    fig.suptitle("Signature Transition: Holonomy Around Ω²=0 Singularity",
                 fontsize=13, fontweight="bold")

    # ── Panel 1: Ω² as function of α and ψ_max ──
    ax = axes[0, 0]
    alpha_range = np.linspace(-3, 3, 300)
    psi_max_range = np.linspace(0, 3, 300)
    A, P = np.meshgrid(alpha_range, psi_max_range)
    Omega_sq = 1.0 + A * P**2

    # Contour at Ω²=0 (degenerate locus)
    levels = [-2, -1, -0.5, 0, 0.5, 1, 2, 4, 8]
    cf = ax.contourf(A, P, Omega_sq, levels=levels, cmap="RdBu_r")
    ax.contour(A, P, Omega_sq, levels=[0], colors="black", linewidths=2.5)
    plt.colorbar(cf, ax=ax, label="Ω²")
    ax.text(-2.5, 2.5, "Ω²<0\n(Lorentzian)", fontsize=9, color="white",
            fontweight="bold")
    ax.text(1.5, 2.5, "Ω²>0\n(Riemannian)", fontsize=9, color="black",
            fontweight="bold")
    ax.set_xlabel("α (metric coupling)"); ax.set_ylabel("ψ_max (field amplitude)")
    ax.set_title("Degenerate Locus: Ω²=0\n(Signature transition boundary)")

    # ── Panel 2: Loop around singularity ──
    ax = axes[0, 1]
    # Draw a loop in (α, ψ) space that encircles Ω²=0
    theta = np.linspace(0, 2 * np.pi, 500)
    # Singularity at α=-1, ψ=1 → α*ψ²=-1 → Ω²=0
    alpha_sing = -1.0
    psi_sing   = 1.0
    r_loop = 0.6
    loop_alpha = alpha_sing + r_loop * np.cos(theta)
    loop_psi   = psi_sing   + r_loop * np.sin(theta)

    # Color the loop by Ω² value
    Omega_loop = 1.0 + loop_alpha * loop_psi**2
    sc = ax.scatter(loop_alpha, loop_psi, c=Omega_loop, cmap="RdBu_r",
                    s=8, vmin=-2, vmax=2)
    plt.colorbar(sc, ax=ax, label="Ω² along loop")
    ax.plot(alpha_sing, psi_sing, "k*", markersize=15, label="Singularity (Ω²=0)")
    ax.contour(A, P, Omega_sq, levels=[0], colors="gray",
               linewidths=1.5, linestyles="--")
    ax.set_xlabel("α"); ax.set_ylabel("ψ_max")
    ax.set_title("Loop Around Singularity\n(Holonomy path)")
    ax.legend(fontsize=8); ax.grid(alpha=0.3)
    ax.set_xlim(-2.5, 0.5); ax.set_ylim(0, 2.5)

    # ── Panel 3: Holonomy angle vs loop radius ──
    ax = axes[0, 2]
    radii = np.linspace(0.1, 1.5, 50)
    holonomy_angles = []
    for r in radii:
        loop_a = alpha_sing + r * np.cos(theta)
        loop_p = psi_sing   + r * np.sin(theta)
        Omega_l = 1.0 + loop_a * loop_p**2
        # Holonomy angle: ∮ d(arg Ω) around the loop
        # When Ω² crosses zero, arg(Ω) jumps by π
        sign_changes = np.sum(np.diff(np.sign(Omega_l)) != 0)
        holonomy_angles.append(sign_changes * np.pi)

    ax.plot(radii, holonomy_angles, color="darkred", linewidth=2.5)
    ax.axhline(np.pi, color="gray", linestyle="--", alpha=0.7, label="π (one crossing)")
    ax.axhline(2 * np.pi, color="gray", linestyle=":", alpha=0.7, label="2π (two crossings)")
    ax.set_xlabel("Loop radius r"); ax.set_ylabel("Holonomy angle (rad)")
    ax.set_title("Holonomy vs Loop Radius\n(Non-trivial = signature transition)")
    ax.legend(fontsize=8); ax.grid(alpha=0.3)

    # ── Panel 4: Ω² profile crossing zero ──
    ax = axes[1, 0]
    x_1d = np.linspace(-4, 4, 300)
    psi_profile = np.exp(-x_1d**2 / 2.0)
    for alpha in [-0.5, -1.0, -1.5, -2.0, -3.0]:
        Omega = 1.0 + alpha * psi_profile**2
        color = plt.cm.Reds(abs(alpha) / 3.0)
        ax.plot(x_1d, Omega, color=color, linewidth=2, label=f"α={alpha}")
    ax.axhline(0, color="black", linewidth=2, linestyle="--", label="Ω²=0 (degenerate)")
    ax.fill_between(x_1d, 0, -3, alpha=0.08, color="red",
                    label="Ω²<0 (Lorentzian region)")
    ax.set_xlabel("x"); ax.set_ylabel("Ω²(x)")
    ax.set_title("Ω² Profile: Transition from\nRiemannian to Lorentzian")
    ax.legend(fontsize=7); ax.grid(alpha=0.3)
    ax.set_ylim(-3, 2)

    # ── Panel 5: Phase of Ω around singularity ──
    ax = axes[1, 1]
    # Complex extension: Ω = sqrt(Ω²), phase jumps by π when Ω²<0
    alpha_c = -1.5
    Omega_sq_1d = 1.0 + alpha_c * psi_profile**2
    phase_Omega = np.where(Omega_sq_1d >= 0, 0.0, np.pi)  # 0 = Riemannian, π = Lorentzian
    ax.plot(x_1d, Omega_sq_1d, color="darkblue", linewidth=2, label="Ω²(x)")
    ax2_twin = ax.twinx()
    ax2_twin.plot(x_1d, phase_Omega, color="crimson", linewidth=2,
                  linestyle="--", label="Phase of Ω")
    ax2_twin.set_ylabel("Phase (rad)", color="crimson")
    ax2_twin.tick_params(axis="y", labelcolor="crimson")
    ax2_twin.set_yticks([0, np.pi])
    ax2_twin.set_yticklabels(["0 (Riemannian)", "π (Lorentzian)"])
    ax.axhline(0, color="gray", linestyle=":", alpha=0.5)
    ax.set_xlabel("x"); ax.set_ylabel("Ω²(x)", color="darkblue")
    ax.set_title(f"Phase Jump at Ω²=0 (α={alpha_c})\nMonodromy of the Bundle")
    ax.grid(alpha=0.3)
    lines1, labels1 = ax.get_legend_handles_labels()
    lines2, labels2 = ax2_twin.get_legend_handles_labels()
    ax.legend(lines1 + lines2, labels1 + labels2, fontsize=8)

    # ── Panel 6: Signature transition conceptual ──
    ax = axes[1, 2]
    ax.axis("off")
    rows = [
        ["Concept",           "Mathematical Object",      "Physical Meaning"],
        ["Ω²=0 locus",        "Degenerate fiber",         "Metric degenerates"],
        ["Loop around Ω²=0",  "Holonomy path γ",          "Signature change path"],
        ["Holonomy H_γ",      "Monodromy of bundle",      "Signature flip operator"],
        ["H_γ ≠ I",           "Non-trivial monodromy",    "Irreversible transition"],
        ["Branch jump",       "Section discontinuity",    "Measurement / collapse"],
        ["F_ent ≠ 0",         "Non-zero curvature",       "Entangled state"],
    ]
    col_w = [0.28, 0.36, 0.36]
    y = 0.92
    for row in rows:
        x_pos = 0.02
        bold = (row == rows[0])
        for cell, w in zip(row, col_w):
            ax.text(x_pos, y, cell, transform=ax.transAxes,
                    fontsize=8, fontweight="bold" if bold else "normal",
                    verticalalignment="top",
                    color="navy" if bold else "black")
            x_pos += w
        y -= 0.14
    ax.set_title("Summary: Signature Transitions\nin the Bundle Language",
                 fontsize=10, fontweight="bold")

    plt.tight_layout()
    savefig("signature_transition", fig)


# ─────────────────────────────────────────────────────────────
# SIM 5: BUNDLE GEODESICS — GEODESIC FLOW ON THE SPACE OF GEOMETRIES
# ─────────────────────────────────────────────────────────────

@sim("bundle_geodesics",
     "Bundle Geodesics: Physical Evolution as Shortest Path Through Geometry Space")
def sim_bundle_geodesics():
    """
    Simulates geodesic flow on the configuration space S (the metric bundle).
    Shows how different initial conditions lead to different phases,
    and how the potential V encodes topological constraints.
    """
    fig, axes = plt.subplots(2, 3, figsize=(15, 9))
    fig.suptitle("Bundle Geodesics: Physical Evolution = Shortest Path in Geometry Space",
                 fontsize=13, fontweight="bold")

    # ── Configuration space: (α, ψ_max) as 2D proxy for S ──
    alpha_range = np.linspace(-3, 3, 200)
    psi_range   = np.linspace(0, 3, 200)
    A, P = np.meshgrid(alpha_range, psi_range)

    # Effective potential V(α, ψ_max) on S
    # V = Gauss-Bonnet constraint + normalization + coupling energy
    Omega_sq = 1.0 + A * P**2
    # Penalty for Ω²<0 (signature transition barrier)
    penalty = np.where(Omega_sq < 0, 10 * Omega_sq**2, 0)
    # Kinetic energy (DeWitt metric contribution)
    kinetic = 0.5 * A**2 * P**2
    # Coupling energy
    coupling_energy = 0.5 * (A**2 - 1)**2 + 0.3 * P**2
    V = kinetic + coupling_energy + penalty

    # ── Panel 1: Potential landscape ──
    ax = axes[0, 0]
    cf = ax.contourf(A, P, np.clip(V, 0, 20), levels=30, cmap="viridis")
    ax.contour(A, P, Omega_sq, levels=[0], colors="red",
               linewidths=2, linestyles="--")
    plt.colorbar(cf, ax=ax, label="V(α, ψ_max)")
    ax.set_xlabel("α"); ax.set_ylabel("ψ_max")
    ax.set_title("Potential Landscape V on Config Space S\n(red dashed = Ω²=0 barrier)")

    # ── Panel 2: Geodesics from different initial conditions ──
    ax = axes[0, 1]
    ax.contourf(A, P, np.clip(V, 0, 20), levels=30, cmap="viridis", alpha=0.5)
    ax.contour(A, P, Omega_sq, levels=[0], colors="red",
               linewidths=2, linestyles="--")

    def geodesic_ode(t, state, lam=0.5):
        """
        Simplified geodesic ODE on (α, ψ) space:
        d²α/dt² = -∂V/∂α,  d²ψ/dt² = -∂V/∂ψ
        (Christoffel terms approximated by potential gradient)
        """
        a, p, da, dp = state
        dV_da = 2 * a * p**2 + 2 * (a**2 - 1) * a
        dV_dp = a**2 * p + 0.6 * p
        # Add barrier gradient near Ω²=0
        Omega2 = 1.0 + a * p**2
        if Omega2 < 0.5:
            barrier = 20 * max(0, 0.5 - Omega2)
            dV_da += barrier * p**2
            dV_dp += barrier * 2 * a * p
        return [da, dp, -dV_da, -dV_dp]

    colors_geo = ["royalblue", "darkorange", "crimson", "mediumseagreen", "purple"]
    initial_conditions = [
        [0.5, 0.5, -0.3, 0.1],   # Starts in quantum phase
        [2.0, 0.5, -0.5, 0.2],   # Starts in soliton phase
        [-0.5, 2.0, 0.2, -0.3],  # Near signature boundary
        [1.5, 1.5, -0.8, 0.0],   # High energy
        [0.1, 0.1, 0.1, 0.5],    # Near flat geometry
    ]
    labels_geo = ["QM initial", "Soliton initial", "Near boundary",
                  "High energy", "Near flat"]

    for ic, color, label in zip(initial_conditions, colors_geo, labels_geo):
        try:
            sol = solve_ivp(geodesic_ode, [0, 8], ic,
                            t_eval=np.linspace(0, 8, 400),
                            method="RK45", rtol=1e-6, max_step=0.05)
            alpha_traj = np.clip(sol.y[0], -3, 3)
            psi_traj   = np.clip(np.abs(sol.y[1]), 0, 3)
            ax.plot(alpha_traj, psi_traj, color=color, linewidth=2,
                    label=label, alpha=0.85)
            ax.plot(ic[0], ic[1], "o", color=color, markersize=7)
        except Exception:
            pass

    ax.set_xlabel("α"); ax.set_ylabel("ψ_max")
    ax.set_title("Geodesics on S\n(Physical evolution = shortest path)")
    ax.legend(fontsize=7); ax.set_xlim(-3, 3); ax.set_ylim(0, 3)

    # ── Panel 3: Energy conservation along geodesics ──
    ax = axes[0, 2]
    for ic, color, label in zip(initial_conditions[:3], colors_geo[:3], labels_geo[:3]):
        try:
            sol = solve_ivp(geodesic_ode, [0, 8], ic,
                            t_eval=np.linspace(0, 8, 400),
                            method="RK45", rtol=1e-6, max_step=0.05)
            a_t, p_t, da_t, dp_t = sol.y
            # Total energy E = kinetic + potential
            V_t = (0.5 * a_t**2 * np.clip(p_t, 0, 3)**2
                   + 0.5 * (a_t**2 - 1)**2
                   + 0.3 * np.clip(p_t, 0, 3)**2)
            T_t = 0.5 * (da_t**2 + dp_t**2)
            E_t = T_t + V_t
            ax.plot(sol.t, E_t / E_t[0], color=color, linewidth=2, label=label)
        except Exception:
            pass
    ax.axhline(1.0, color="gray", linestyle="--", alpha=0.7, label="E₀ (conserved)")
    ax.set_xlabel("t"); ax.set_ylabel("E(t) / E₀")
    ax.set_title("Energy Conservation Along Geodesics\n(Deviation = numerical error)")
    ax.legend(fontsize=7); ax.grid(alpha=0.3)

    # ── Panel 4: Phase portrait (α, dα/dt) ──
    ax = axes[1, 0]
    for ic, color, label in zip(initial_conditions, colors_geo, labels_geo):
        try:
            sol = solve_ivp(geodesic_ode, [0, 8], ic,
                            t_eval=np.linspace(0, 8, 400),
                            method="RK45", rtol=1e-6, max_step=0.05)
            ax.plot(np.clip(sol.y[0], -3, 3), sol.y[2],
                    color=color, linewidth=1.5, label=label, alpha=0.8)
            ax.plot(ic[0], ic[2], "o", color=color, markersize=6)
        except Exception:
            pass
    ax.axvline(0, color="gray", linestyle="--", alpha=0.5)
    ax.set_xlabel("α"); ax.set_ylabel("dα/dt")
    ax.set_title("Phase Portrait (α, dα/dt)\nAttractor structure in config space")
    ax.legend(fontsize=7); ax.grid(alpha=0.3)

    # ── Panel 5: Attractor basins ──
    ax = axes[1, 1]
    # Classify where each initial condition ends up
    n_ic = 30
    alpha_ic = np.linspace(-2.5, 2.5, n_ic)
    psi_ic   = np.linspace(0.1, 2.5, n_ic)
    AI, PI = np.meshgrid(alpha_ic, psi_ic)
    basin_map = np.zeros((n_ic, n_ic))

    for i in range(n_ic):
        for j in range(n_ic):
            ic = [AI[i, j], PI[i, j], 0.0, 0.0]
            try:
                sol = solve_ivp(geodesic_ode, [0, 5], ic,
                                t_eval=[5.0], method="RK45",
                                rtol=1e-4, max_step=0.1)
                a_f = sol.y[0, -1]
                p_f = abs(sol.y[1, -1])
                Omega_f = 1.0 + a_f * p_f**2
                if Omega_f < 0:
                    basin_map[i, j] = 3   # Lorentzian
                elif a_f > 0.5:
                    basin_map[i, j] = 1   # Quantum attractor
                elif a_f < -0.5:
                    basin_map[i, j] = 2   # Soliton attractor
                else:
                    basin_map[i, j] = 0   # Near flat
            except Exception:
                basin_map[i, j] = -1

    cmap_basin = matplotlib.colors.ListedColormap(
        ["gray", "royalblue", "darkorange", "crimson"])
    ax.contourf(AI, PI, basin_map,
                levels=[-1.5, -0.5, 0.5, 1.5, 2.5, 3.5],
                cmap=cmap_basin, alpha=0.75)
    ax.contour(A, P, Omega_sq, levels=[0], colors="white",
               linewidths=2, linestyles="--")
    ax.set_xlabel("α₀"); ax.set_ylabel("ψ_max₀")
    ax.set_title("Attractor Basins\n(Blue=QM, Orange=Soliton, Red=Lorentzian)")

    # ── Panel 6: Summary table ──
    ax = axes[1, 2]
    ax.axis("off")
    rows = [
        ["Object",              "Addon.md Name",          "Physical Role"],
        ["Config space S",      "Submanifold of C",       "Space of all geometries"],
        ["Geodesic on S",       "Physical trajectory",    "Equation of motion"],
        ["Potential V",         "Topological constraints","Gauss-Bonnet, normalization"],
        ["Attractor basin",     "Phase of the diagram",   "QM / Soliton / Chaos"],
        ["Signature boundary",  "Ω²=0 locus",             "Degenerate metric"],
        ["Holonomy H_γ",        "Monodromy",              "Signature flip"],
        ["Off-diag metric",     "F_ent curvature",        "Quantum entanglement"],
    ]
    col_w = [0.28, 0.34, 0.38]
    y = 0.94
    for row in rows:
        x_pos = 0.02
        bold = (row == rows[0])
        for cell, w in zip(row, col_w):
            ax.text(x_pos, y, cell, transform=ax.transAxes,
                    fontsize=8, fontweight="bold" if bold else "normal",
                    verticalalignment="top",
                    color="navy" if bold else "black")
            x_pos += w
        y -= 0.12
    ax.set_title("Complete Object Summary\nfrom Addon.md",
                 fontsize=10, fontweight="bold")

    plt.tight_layout()
    savefig("bundle_geodesics", fig)


# ─────────────────────────────────────────────────────────────
# RUNNER
# ─────────────────────────────────────────────────────────────

def run_all():
    print(f"\nRunning {len(REGISTRY)} Addon simulations → plots/\n")
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
    parser = argparse.ArgumentParser(description="Addon.md Simulations")
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
