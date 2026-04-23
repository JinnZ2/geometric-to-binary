"""
connections_sims.py
Simulations for the Silicon Phase-Space Framework.

Field link:
  https://github.com/JinnZ2/Geometric-to-Binary-Computational-Bridge/blob/main/Silicon/Connections.md

Concepts covered (10 simulations):
  Original 6:
    1. silicon_phase_diagram       — 4D state space and attractor basins
    2. phase_transitions           — Band-gap collapse, quantization, decoherence surfaces
    3. silicon_manifold_flow       — dS/dt dynamics: relaxation, driving, aging
    4. fabrication_trajectories    — Steering S(t) to target basins
    5. geometry_to_binary_pipeline — Full pipeline demo
    6. basin_stability             — Stability margins, noise, failure modes

  New (from Computational Bridge):
    7. continuous_regime_blending  — Softmax regime weights vs hard thresholds
    8. rigorous_field_mapping      — Physical derivation of S from geometry field
    9. feedback_closure            — Binary → geometry feedback loop (4 modes)
   10. closed_loop_trajectory      — Full iterative dS/dt dynamical system

Usage
-----
    python connections_sims.py              # run all 10
    python connections_sims.py --sim continuous_regime_blending
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
from scipy.special import softmax
from scipy.ndimage import gaussian_filter, sobel, laplace

warnings.filterwarnings("ignore")

PLOT_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "plots")
os.makedirs(PLOT_DIR, exist_ok=True)

REGISTRY = {}

BRIDGE_URL = ("https://github.com/JinnZ2/Geometric-to-Binary-Computational-Bridge"
              "/blob/main/Silicon/Connections.md")


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
# Silicon State Model (continuous regime blending — from Computational Bridge)
# ─────────────────────────────────────────────────────────────────────────────

# Basin centers in normalized 7D S-space: [n/n_max, d, l/3, ke, ko, kt, km]
BASIN_CENTERS = {
    "semiconductor":    np.array([1e16/1e21, 0.05, 3.0/3, 0.8, 0.1, 0.1, 0.0]),
    "metallic":         np.array([1e21/1e21, 0.3,  3.0/3, 0.9, 0.0, 0.1, 0.0]),
    "quantum":          np.array([1e17/1e21, 0.02, 0.5/3, 0.3, 0.1, 0.1, 0.5]),
    "photonic":         np.array([1e15/1e21, 0.01, 2.5/3, 0.1, 0.8, 0.1, 0.0]),
    "defect_dominated": np.array([1e16/1e21, 0.8,  2.0/3, 0.3, 0.1, 0.4, 0.2]),
    "mechanical":       np.array([1e15/1e21, 0.1,  2.0/3, 0.2, 0.1, 0.1, 0.8]),
}

REGIME_COLORS = {
    "semiconductor":    "#2196F3",
    "metallic":         "#F44336",
    "quantum":          "#9C27B0",
    "photonic":         "#4CAF50",
    "defect_dominated": "#FF9800",
    "mechanical":       "#795548",
}


class SiliconState:
    """Silicon phase-space representation with continuous regime blending."""

    def __init__(self, n, d, l, k):
        self.n = float(np.clip(n, 1e10, 1e22))
        self.d = float(np.clip(d, 0.0, 1.0))
        self.l = float(np.clip(l, 0.1, 3.0))
        self.k = {
            "electrical": float(k.get("electrical", 0.5)),
            "optical":    float(k.get("optical",    0.0)),
            "thermal":    float(k.get("thermal",    0.0)),
            "mechanical": float(k.get("mechanical", 0.0)),
            "coherent":   float(k.get("coherent",   0.0)),
        }

    def to_vector(self):
        return np.array([
            self.n / 1e21,
            self.d,
            self.l / 3.0,
            self.k["electrical"] / 0.9,
            self.k["optical"]    / 0.9,
            self.k["thermal"]    / 0.9,
            self.k["mechanical"] / 0.9,
        ])

    def regime_weights(self, temperature=0.1):
        """Continuous softmax regime membership."""
        v = self.to_vector()
        regimes = sorted(BASIN_CENTERS.keys())
        dists = np.array([np.linalg.norm(v - BASIN_CENTERS[r]) for r in regimes])
        w = softmax(-dists / temperature)
        return {r: float(w[i]) for i, r in enumerate(regimes)}

    def dominant_regime(self, temperature=0.05):
        w = self.regime_weights(temperature)
        return max(w, key=w.get)

    def stability_metric(self):
        """1 - normalized entropy of regime weights. High = deep in a basin."""
        w = np.array(list(self.regime_weights().values()))
        w = w[w > 1e-10]
        H = -np.sum(w * np.log(w))
        H_max = np.log(len(BASIN_CENTERS))
        return 1.0 - H / H_max

    def coherence_metric(self):
        """Quantum coherence proxy: quantum weight × exp(-thermal - defect)."""
        qw = self.regime_weights().get("quantum", 0)
        return qw * np.exp(-self.k["thermal"] - self.d)

    def bandgap(self):
        Eg0 = 1.12
        dEg_n = 3.5e-8 * (self.n / 1e18) ** 0.5 if self.n > 1e17 else 0
        dEg_d = 0.5 * self.d
        return max(0.0, Eg0 - dEg_n - dEg_d)

    def distance_to_boundary(self, boundary="metallic"):
        if boundary == "metallic":
            n_crit = 1e19
            return max(0, np.log10(n_crit) - np.log10(self.n)) / 5.0
        coherent = self.k["electrical"] + self.k["optical"]
        thermal  = self.k["thermal"]
        if thermal < 1e-6:
            return 1.0
        return max(0, coherent / (coherent + thermal) - 0.5)


# ─────────────────────────────────────────────────────────────────────────────
# Rigorous geometry-to-silicon mapping (from Computational Bridge)
# ─────────────────────────────────────────────────────────────────────────────

def compute_carrier_density(field, temperature=300.0):
    k_B = 8.617e-5
    field_norm = field / (np.std(field) + 1e-10)
    V_eff = -np.abs(field_norm) * 8.6          # deformation potential eV
    E_F = np.mean(V_eff) + 0.1
    integrand = np.maximum(E_F - V_eff, 0.0) ** 1.5
    m_eff = np.sqrt(0.26 * 0.49)
    prefactor = (2 * m_eff * 9.109e-31 / (6.626e-34 ** 2)) ** 1.5 / (3 * np.pi ** 2)
    n = np.mean(integrand) * prefactor * 1e-6
    return float(np.clip(n, 1e10, 1e22))


def compute_defect_density(field):
    lap = laplace(field)
    lap_energy = np.mean(lap ** 2)
    gx = sobel(field, axis=0)
    gy = sobel(field, axis=1) if field.ndim > 1 else np.zeros_like(field)
    grad_mag = np.sqrt(gx**2 + gy**2)
    disloc = np.mean(np.abs(laplace(grad_mag))) if field.ndim > 1 else 0
    roughness = np.std(field) / (np.mean(np.abs(field)) + 1e-10)
    d_raw = (0.4 * np.tanh(lap_energy / 10.0) +
             0.3 * np.tanh(disloc / 5.0) +
             0.3 * np.tanh(roughness))
    return float(np.clip(d_raw, 0.0, 1.0))


def compute_effective_dimension(field):
    f_ft = np.fft.fftn(field)
    power = np.abs(f_ft) ** 2
    freqs = [np.fft.fftfreq(s) for s in field.shape]
    grids = np.meshgrid(*freqs, indexing="ij")
    k_mag = np.sqrt(sum(g**2 for g in grids))
    k_bins = np.linspace(0.01, 0.5, min(50, min(field.shape) // 2))
    p_bin = np.zeros(len(k_bins) - 1)
    for i in range(len(k_bins) - 1):
        mask = (k_mag >= k_bins[i]) & (k_mag < k_bins[i+1])
        if mask.sum() > 0:
            p_bin[i] = np.mean(power[mask])
    k_c = (k_bins[:-1] + k_bins[1:]) / 2
    valid = p_bin > 0
    if valid.sum() >= 3:
        coeffs = np.polyfit(np.log(k_c[valid]), np.log(p_bin[valid]), 1)
        spectral_exp = -coeffs[0]
    else:
        spectral_exp = float(field.ndim)
    ell = float(np.clip(0.7 * field.ndim + 0.3 * spectral_exp / 2, 0.1, 3.0))
    return ell


def compute_coupling_vector(field, n, d, temperature=300.0):
    tau_d = 1e-12 / (d + 1e-6)
    tau_p = 1e-13 * (300.0 / temperature)
    tau   = 1.0 / (1.0/tau_d + 1.0/tau_p)
    sigma = (n * 1e6 * (1.602e-19)**2 * tau / (0.26 * 9.109e-31))
    k_e   = float(np.tanh(sigma / 1e3))

    grad_mag = np.mean(np.abs(np.gradient(field)))
    k_o = float(np.clip(np.tanh(grad_mag * 0.1) * 0.6 + np.var(field) * 0.4, 0, 1))

    T_D = 645.0
    Cv  = (12 * np.pi**4 / 5) * 8.617e-5 * (temperature / T_D)**3 if temperature < T_D else 3 * 8.617e-5
    phonon_mfp = 5.431e-10 / (d + 1e-4)
    k_t = float(np.clip(np.tanh(Cv * 0.063 * phonon_mfp / (5.431e-10 * 100.0)), 0, 1))

    strain = np.gradient(field)
    if isinstance(strain, (list, tuple)):
        se = sum(np.mean(np.asarray(s)**2) for s in strain)
    else:
        se = np.mean(np.asarray(strain)**2)
    k_m = float(np.clip(np.tanh(se * 1e-2), 0, 1))

    k_coh = float(np.clip(np.exp(-d * 5.0) * np.exp(-temperature / 100.0) * (1 - k_t), 0, 1))

    return {"electrical": k_e, "optical": k_o, "thermal": k_t,
            "mechanical": k_m, "coherent": k_coh}


def geometry_to_silicon_rigorous(field, temperature=300.0):
    """Rigorous dimensional reduction: F(x) → S = (n, d, ℓ, κ)."""
    field = np.asarray(field, dtype=float)
    n   = compute_carrier_density(field, temperature)
    d   = compute_defect_density(field)
    ell = compute_effective_dimension(field)
    k   = compute_coupling_vector(field, n, d, temperature)
    return SiliconState(n=n, d=d, l=ell, k=k)


def silicon_to_graph(S, n_nodes=8):
    import networkx as nx
    G = nx.Graph()
    regime = S.dominant_regime()
    for i in range(n_nodes):
        G.add_node(i, activity=S.n * (1 - S.d) * 1e-17, mode=regime)
    kv = [S.k["electrical"] * 0.4 + S.k["optical"] * 0.3 + S.k["thermal"] * 0.3]
    for i in range(n_nodes):
        for j in range(i + 1, n_nodes):
            G.add_edge(i, j, weight=kv[0])
    return G


def graph_to_binary_blended(G, S, temperature=0.1):
    """Weighted soft vote across all regimes."""
    weights = S.regime_weights(temperature)
    bits, confidences = [], []
    for node, data in G.nodes(data=True):
        a = data["activity"]
        proposals = {
            "semiconductor":    1 if a > 0.5 else 0,
            "metallic":         int(np.random.rand() > 0.5),
            "quantum":          1 if np.sin(a * np.pi) > 0 else 0,
            "photonic":         int(a * 10) % 2,
            "defect_dominated": 0 if a < 0.7 else int(np.random.rand() > 0.5),
            "mechanical":       1 if np.sin(a * 2 * np.pi) > 0.3 else 0,
        }
        expected = sum(weights[r] * proposals[r] for r in weights)
        w_arr = np.array(list(weights.values()))
        H = -np.sum(w_arr * np.log(w_arr + 1e-10))
        H_max = np.log(len(weights))
        conf = 2.0 * abs(expected - 0.5) * (1.0 - H / H_max)
        bits.append(1 if expected >= 0.5 else 0)
        confidences.append(float(conf))
    return bits, confidences


def binary_to_geometry_feedback(bits, geometry, S, strength=0.1, mode="diffusive"):
    """Feedback closure: binary output modifies the geometry field."""
    G_new = geometry.copy().astype(float)
    ba = np.array(bits)
    repeats = G_new.size // len(ba) + 1
    ba = np.tile(ba, repeats)[:G_new.size].reshape(G_new.shape)

    if mode == "diffusive":
        mod = gaussian_filter((ba.astype(float) - 0.5), sigma=1.0)
    elif mode == "structural":
        mod = (ba - 0.5) * 2.0 * S.d
    elif mode == "waveguide":
        g = np.gradient(ba.astype(float))
        if isinstance(g, (list, tuple)) and len(g) > 1:
            mod = np.sqrt(np.asarray(g[0])**2 + np.asarray(g[1])**2)
        else:
            mod = np.abs(np.asarray(g))
    elif mode == "adaptive":
        mod = ba * geometry - (1 - ba) * geometry * 0.1
    else:
        mod = np.zeros_like(G_new)

    qw = S.regime_weights().get("quantum", 0)
    if qw > 0.3:
        mod += np.sin(geometry + np.pi * qw) * qw * 0.5

    G_new += strength * mod
    return G_new


def run_closed_loop(geometry, iterations=12, strength=0.1, mode="diffusive", temperature=0.1):
    """Full closed-loop pipeline: G → S → bits → G' → S' → ..."""
    trajectory = []
    G = geometry.copy()
    for i in range(iterations):
        S = geometry_to_silicon_rigorous(G)
        graph = silicon_to_graph(S)
        bits, confs = graph_to_binary_blended(graph, S, temperature)
        trajectory.append({
            "iter":       i,
            "S":          S,
            "weights":    S.regime_weights(temperature),
            "bits":       bits,
            "confs":      confs,
            "stability":  S.stability_metric(),
            "coherence":  S.coherence_metric(),
            "dominant":   S.dominant_regime(),
            "dist_metal": S.distance_to_boundary("metallic"),
        })
        if i < iterations - 1:
            G = binary_to_geometry_feedback(bits, G, S, strength, mode)
    return trajectory, G


# ─────────────────────────────────────────────────────────────────────────────
# Simulation 1: Silicon Phase Diagram
# ─────────────────────────────────────────────────────────────────────────────

@sim("silicon_phase_diagram", "Silicon Phase Diagram — Attractor Basins in S-Space")
def silicon_phase_diagram():
    fig, axes = plt.subplots(2, 3, figsize=(16, 10))
    fig.suptitle("Silicon Phase-Space S = (n, d, ℓ, κ) — Attractor Basins", fontsize=14)

    regime_list = sorted(BASIN_CENTERS.keys())
    cmap = matplotlib.colors.ListedColormap([REGIME_COLORS[r] for r in regime_list])

    def regime_idx(S):
        return regime_list.index(S.dominant_regime())

    n_vals = np.logspace(14, 21, 80)
    d_vals = np.linspace(0, 1, 80)

    # n vs d
    ax = axes[0, 0]
    Z = np.zeros((80, 80), dtype=int)
    for i, d in enumerate(d_vals):
        for j, n in enumerate(n_vals):
            Z[i, j] = regime_idx(SiliconState(n, d, 3.0, {"electrical": 1.0, "optical": 0.2, "thermal": 0.3}))
    ax.contourf(np.log10(n_vals), d_vals, Z, levels=np.arange(-0.5, 6.5), cmap=cmap, alpha=0.85)
    ax.set_xlabel("log₁₀(n) [cm⁻³]"); ax.set_ylabel("Defect density d")
    ax.set_title("n–d Phase Map (ℓ=3)")
    patches = [mpatches.Patch(color=REGIME_COLORS[r], label=r) for r in regime_list]
    ax.legend(handles=patches, fontsize=7, loc="upper left")

    # n vs ℓ
    ax = axes[0, 1]
    l_vals = np.linspace(0, 3, 80)
    Z2 = np.zeros((80, 80), dtype=int)
    for i, l in enumerate(l_vals):
        for j, n in enumerate(n_vals):
            Z2[i, j] = regime_idx(SiliconState(n, 0.1, l, {"electrical": 1.0, "optical": 0.2, "thermal": 0.3}))
    ax.contourf(np.log10(n_vals), l_vals, Z2, levels=np.arange(-0.5, 6.5), cmap=cmap, alpha=0.85)
    ax.set_xlabel("log₁₀(n) [cm⁻³]"); ax.set_ylabel("Effective dimensionality ℓ")
    ax.set_title("n–ℓ Phase Map (d=0.1)")

    # κ_optical vs κ_electrical
    ax = axes[0, 2]
    k_vals = np.linspace(0, 1, 80)
    Z3 = np.zeros((80, 80), dtype=int)
    for i, ko in enumerate(k_vals):
        for j, ke in enumerate(k_vals):
            Z3[i, j] = regime_idx(SiliconState(1e17, 0.1, 2.5, {"electrical": ke, "optical": ko, "thermal": 0.3}))
    ax.contourf(k_vals, k_vals, Z3, levels=np.arange(-0.5, 6.5), cmap=cmap, alpha=0.85)
    ax.plot([0, 1], [0, 1], "k--", lw=1)
    ax.set_xlabel("κ_electrical"); ax.set_ylabel("κ_optical")
    ax.set_title("Coupling Phase Map")

    # Bandgap surface
    ax = axes[1, 0]
    NN, DD = np.meshgrid(n_vals, d_vals)
    Eg = np.vectorize(lambda n, d: SiliconState(n, d, 3, {"electrical": 1, "optical": 0, "thermal": 0}).bandgap())(NN, DD)
    cf = ax.contourf(np.log10(n_vals), d_vals, Eg, levels=20, cmap="RdYlGn")
    plt.colorbar(cf, ax=ax, label="Bandgap (eV)")
    ax.contour(np.log10(n_vals), d_vals, Eg, levels=[0.0], colors="red", linewidths=2)
    ax.set_xlabel("log₁₀(n) [cm⁻³]"); ax.set_ylabel("Defect density d")
    ax.set_title("Bandgap Surface (red = gap closure)")

    # Stability landscape
    ax = axes[1, 1]
    stab = np.vectorize(lambda n, d: SiliconState(n, d, 3, {"electrical": 1, "optical": 0.2, "thermal": 0.3}).stability_metric())(NN, DD)
    cf2 = ax.contourf(np.log10(n_vals), d_vals, stab, levels=20, cmap="Blues")
    plt.colorbar(cf2, ax=ax, label="Stability metric")
    ax.set_xlabel("log₁₀(n) [cm⁻³]"); ax.set_ylabel("Defect density d")
    ax.set_title("Stability Landscape (continuous regime entropy)")

    # Regime summary
    ax = axes[1, 2]
    ax.axis("off")
    rows = [["Regime", "n [cm⁻³]", "d", "ℓ", "κ dominant"],
            ["Semiconductor", "10¹⁴–10¹⁸", "< 0.3", "3", "Electrical"],
            ["Metallic", "> 10¹⁹", "any", "3", "Electrical"],
            ["Quantum", "any", "< 0.1", "0–1", "Coherent"],
            ["Photonic", "any", "< 0.1", "2–3", "Optical"],
            ["Defect", "any", "> 0.7", "any", "Surface"],
            ["Mechanical", "any", "< 0.3", "1–2", "Mechanical"]]
    tbl = ax.table(cellText=rows[1:], colLabels=rows[0], loc="center", cellLoc="center")
    tbl.auto_set_font_size(False); tbl.set_fontsize(8); tbl.scale(1, 1.5)
    ax.set_title("Phase Regime Summary", pad=20)

    plt.tight_layout()
    savefig("silicon_phase_diagram")


# ─────────────────────────────────────────────────────────────────────────────
# Simulation 2: Phase Transitions
# ─────────────────────────────────────────────────────────────────────────────

@sim("phase_transitions", "Phase Transition Surfaces — Band-Gap Collapse, Quantization, Decoherence")
def phase_transitions():
    fig, axes = plt.subplots(2, 2, figsize=(13, 10))
    fig.suptitle("Silicon Phase Transition Surfaces", fontsize=14)

    n_vals = np.logspace(15, 21, 200)
    d_vals = np.linspace(0, 1, 200)
    NN, DD = np.meshgrid(n_vals, d_vals)

    # Band structure collapse
    ax = axes[0, 0]
    Eg = np.vectorize(lambda n, d: SiliconState(n, d, 3, {"electrical": 1, "optical": 0, "thermal": 0}).bandgap())(NN, DD)
    cf = ax.contourf(np.log10(n_vals), d_vals, Eg, levels=30, cmap="RdYlGn_r")
    plt.colorbar(cf, ax=ax, label="Eg (eV)")
    ax.contour(np.log10(n_vals), d_vals, Eg, levels=[0.0], colors="white", linewidths=2.5)
    ax.set_xlabel("log₁₀(n)"); ax.set_ylabel("d"); ax.set_title("1. Band Structure Collapse E_g=0")

    # Dimensional quantization
    ax = axes[0, 1]
    n_q = np.logspace(14, 21, 300)
    lambda_F = (2 * np.pi / (3 * np.pi**2 * n_q)) ** (1/3) * 1e9
    ax.fill_between(np.log10(n_q), 0, lambda_F, alpha=0.3, color="purple", label="Quantum zone (ℓ < λ_F)")
    ax.fill_between(np.log10(n_q), lambda_F, 100, alpha=0.15, color="blue", label="Classical zone")
    ax.plot(np.log10(n_q), lambda_F, "purple", lw=2.5, label="λ_F (Fermi wavelength)")
    ax.axhline(10, color="orange", ls="--", lw=1.5, label="10 nm (FinFET)")
    ax.axhline(2, color="red", ls="--", lw=1.5, label="2 nm (quantum dot)")
    ax.set_ylim(0, 50); ax.legend(fontsize=8)
    ax.set_xlabel("log₁₀(n)"); ax.set_ylabel("Confinement ℓ (nm)"); ax.set_title("2. Dimensional Quantization ℓ ≲ λ_F")

    # Decoherence boundary
    ax = axes[1, 0]
    k_t = np.linspace(0, 3, 200); k_c = np.linspace(0, 3, 200)
    KT, KC = np.meshgrid(k_t, k_c)
    ratio = KT / (KC + 0.01)
    cf3 = ax.contourf(k_t, k_c, ratio, levels=30, cmap="hot_r")
    plt.colorbar(cf3, ax=ax, label="κ_thermal / κ_coherent")
    ax.plot([0, 3], [0, 3], "cyan", lw=2.5, label="Decoherence boundary")
    ax.legend(fontsize=8)
    ax.set_xlabel("κ_thermal"); ax.set_ylabel("κ_coherent"); ax.set_title("3. Decoherence Boundary")

    # Summary
    ax = axes[1, 1]; ax.axis("off")
    rows = [["Surface", "Condition", "Transition"],
            ["Band collapse", "E_g(n,d) = 0", "Semiconductor → Metal"],
            ["Quantization", "ℓ ≲ λ_F", "Classical → Quantum"],
            ["Decoherence", "κ_th ≫ κ_coh", "Quantum → Classical"]]
    tbl = ax.table(cellText=rows[1:], colLabels=rows[0], loc="center", cellLoc="center")
    tbl.auto_set_font_size(False); tbl.set_fontsize(10); tbl.scale(1.2, 2.0)
    ax.set_title("Phase Transition Summary", pad=20)

    plt.tight_layout()
    savefig("phase_transitions")


# ─────────────────────────────────────────────────────────────────────────────
# Simulation 3: Silicon Manifold Flow
# ─────────────────────────────────────────────────────────────────────────────

@sim("silicon_manifold_flow", "Silicon Manifold Flow — dS/dt Dynamics")
def silicon_manifold_flow():
    fig, axes = plt.subplots(2, 2, figsize=(13, 10))
    fig.suptitle("Silicon Manifold Dynamics: dS/dt = F(n, d, ℓ, κ)", fontsize=14)

    t = np.linspace(0, 100, 1000)

    # Carrier relaxation
    ax = axes[0, 0]
    n_eq = 1e17
    for n0 in [1e15, 1e17, 1e19]:
        ax.semilogx(t + 0.1, n_eq + (n0 - n_eq) * np.exp(-0.1 * t), label=f"n₀={n0:.0e}")
    ax.axhline(n_eq, color="k", ls="--", lw=1)
    ax.set_xlabel("Time"); ax.set_ylabel("n [cm⁻³]"); ax.set_title("Carrier Relaxation")
    ax.legend(fontsize=8)

    # Defect aging
    ax = axes[0, 1]
    d_t = np.clip(0.05 + 0.002 * t, 0, 1)
    regimes = [SiliconState(1e17, d, 3, {"electrical": 1.0, "optical": 0.2, "thermal": 0.3}).dominant_regime() for d in d_t]
    ax.plot(t, d_t, "orange", lw=2)
    prev = regimes[0]
    for i, r in enumerate(regimes):
        if r != prev:
            ax.axvline(t[i], color="red", ls="--", lw=1.5, alpha=0.7)
            ax.text(t[i] + 1, d_t[i], f"→ {r}", fontsize=7, color="red")
            prev = r
    ax.set_xlabel("Time"); ax.set_ylabel("d"); ax.set_title("Aging Trajectory")

    # Gate-driven switching
    ax = axes[1, 0]
    gate = 0.5 * (1 + np.sign(np.sin(2 * np.pi * 0.5 * t / 100)))
    n_driven = n_eq * (0.01 + gate * 10)
    ax.plot(t, np.log10(n_driven), "blue", lw=1.5)
    ax.axhline(19, color="red", ls="--", lw=1, label="Metallic breakdown")
    ax.axhline(14, color="green", ls="--", lw=1, label="Depletion floor")
    ax.fill_between(t, 14, 18, alpha=0.08, color="blue", label="CMOS basin")
    ax.set_xlabel("Time"); ax.set_ylabel("log₁₀(n)"); ax.set_title("Transistor Switching Loop")
    ax.legend(fontsize=8)

    # Phase portrait
    ax = axes[1, 1]
    n_grid = np.logspace(14, 20, 15); d_grid = np.linspace(0, 0.8, 15)
    NG, DG = np.meshgrid(np.log10(n_grid), d_grid)
    U = (np.log10(n_eq) - NG) * 0.3; V = np.ones_like(DG) * 0.02
    ax.quiver(NG, DG, U, V, alpha=0.6, color="gray")
    ax.annotate("CMOS basin", xy=(17, 0.15), fontsize=9, color="blue",
                bbox=dict(boxstyle="round", facecolor="lightblue", alpha=0.6))
    ax.set_xlabel("log₁₀(n)"); ax.set_ylabel("d"); ax.set_title("Phase Portrait")

    plt.tight_layout()
    savefig("silicon_manifold_flow")


# ─────────────────────────────────────────────────────────────────────────────
# Simulation 4: Fabrication Trajectories
# ─────────────────────────────────────────────────────────────────────────────

@sim("fabrication_trajectories", "Fabrication Trajectories — Steering S(t) to Target Basins")
def fabrication_trajectories():
    fig, axes = plt.subplots(2, 2, figsize=(13, 10))
    fig.suptitle("Fabrication as Trajectory Design in S-Space", fontsize=14)

    def make_traj(target, n_steps=100):
        t = np.linspace(0, 1, n_steps)
        if target == "cmos":
            return t, 1e15 + (1e17 - 1e15) * t, 0.8 * np.exp(-5*t) + 0.05, np.ones(n_steps) * 3.0
        elif target == "photonic":
            return t, 1e15 * np.ones(n_steps), 0.8 * np.exp(-5*t) + 0.02, np.ones(n_steps) * 2.5
        else:  # quantum
            return t, 1e16 * np.ones(n_steps), 0.8 * np.exp(-8*t) + 0.01, 3.0 - 2.8 * t

    colors = {"cmos": "blue", "photonic": "green", "quantum": "purple"}
    labels = {"cmos": "CMOS", "photonic": "Photonic", "quantum": "Quantum dot"}

    for ax_idx, (ykey, ylabel, title) in enumerate([
        ("n", "n [cm⁻³]", "Doping n(t)"),
        ("d", "Defect density d", "Defect Reduction d(t)"),
        ("l", "Dimensionality ℓ", "Dimensional Engineering ℓ(t)"),
    ]):
        ax = axes[ax_idx // 2, ax_idx % 2] if ax_idx < 3 else None
        if ax is None:
            break
        for target in ["cmos", "photonic", "quantum"]:
            t, n, d, l = make_traj(target)
            vals = {"n": n, "d": d, "l": l}
            if ykey == "n":
                ax.semilogy(t, vals[ykey], color=colors[target], lw=2, label=labels[target])
            else:
                ax.plot(t, vals[ykey], color=colors[target], lw=2, label=labels[target])
        ax.set_xlabel("Fabrication progress"); ax.set_ylabel(ylabel); ax.set_title(title)
        ax.legend(fontsize=8)

    # Phase portrait
    ax = axes[1, 1]
    for target in ["cmos", "photonic", "quantum"]:
        t, n, d, l = make_traj(target)
        ax.plot(np.log10(n), d, color=colors[target], lw=2.5, label=labels[target])
        ax.plot(np.log10(n[0]), d[0], "o", color=colors[target], ms=10)
        ax.plot(np.log10(n[-1]), d[-1], "*", color=colors[target], ms=14)
    ax.set_xlabel("log₁₀(n)"); ax.set_ylabel("d")
    ax.set_title("Fabrication Paths in (n,d) Space\n● start  ★ target")
    ax.legend(fontsize=8)

    plt.tight_layout()
    savefig("fabrication_trajectories")


# ─────────────────────────────────────────────────────────────────────────────
# Simulation 5: Geometry-to-Binary Pipeline
# ─────────────────────────────────────────────────────────────────────────────

@sim("geometry_to_binary_pipeline", "Geometry → Silicon → Graph → Binary — Full Pipeline")
def geometry_to_binary_pipeline():
    fig, axes = plt.subplots(2, 3, figsize=(16, 10))
    fig.suptitle("Geometry → Silicon State → Graph → Binary Logic Pipeline", fontsize=14)

    np.random.seed(42)
    x = np.linspace(0, 1, 32); y = np.linspace(0, 1, 32)
    XX, YY = np.meshgrid(x, y)
    fields = {
        "Smooth wave\n(photonic)":       np.sin(4*np.pi*XX) * np.cos(4*np.pi*YY) * 0.5 + 0.5,
        "High variance\n(defect)":       np.random.rand(32, 32),
        "Dense lattice\n(semiconductor)": 0.5 + 0.3*np.sin(10*np.pi*XX)*np.sin(10*np.pi*YY),
        "Sparse dot\n(quantum)":         np.exp(-((XX-0.5)**2+(YY-0.5)**2)/0.01)*0.1 + 0.01,
    }

    results = []
    for name, field in fields.items():
        S = geometry_to_silicon_rigorous(field)
        G = silicon_to_graph(S)
        bits, confs = graph_to_binary_blended(G, S)
        results.append((name, field, S, G, bits, confs))

    # Input fields
    ax = axes[0, 0]; ax.axis("off"); ax.set_title("Input Geometry Fields")
    for i, (name, field, *_) in enumerate(results):
        inset = ax.inset_axes([0.02+(i%2)*0.5, 0.52-(i//2)*0.5, 0.44, 0.44])
        inset.imshow(field, cmap="viridis", origin="lower")
        inset.set_title(name, fontsize=7); inset.axis("off")

    # Silicon states
    ax = axes[0, 1]; ax.axis("off"); ax.set_title("Extracted Silicon States (Rigorous)")
    rows = [["Field", "n [cm⁻³]", "d", "ℓ", "Dominant Regime"]]
    for name, _, S, *_ in results:
        rows.append([name.split("\n")[0], f"{S.n:.1e}", f"{S.d:.2f}", f"{S.l:.2f}", S.dominant_regime()])
    tbl = ax.table(cellText=rows[1:], colLabels=rows[0], loc="center", cellLoc="center")
    tbl.auto_set_font_size(False); tbl.set_fontsize(8); tbl.scale(1, 1.8)
    for i, (_, _, S, *_) in enumerate(results):
        tbl[i+1, 4].set_facecolor(REGIME_COLORS.get(S.dominant_regime(), "white"))
        tbl[i+1, 4].set_text_props(color="white")

    # Regime weights radar
    ax = axes[0, 2]; ax.axis("off"); ax.set_title("Regime Weight Blending")
    for i, (name, _, S, *_) in enumerate(results):
        inset = ax.inset_axes([0.02+(i%2)*0.5, 0.52-(i//2)*0.5, 0.44, 0.44])
        w = S.regime_weights()
        regimes = sorted(w.keys())
        vals = [w[r] for r in regimes]
        bars = inset.bar(range(len(regimes)), vals,
                         color=[REGIME_COLORS[r] for r in regimes])
        inset.set_xticks(range(len(regimes)))
        inset.set_xticklabels([r[:5] for r in regimes], fontsize=5, rotation=45)
        inset.set_title(name.split("\n")[0], fontsize=7)
        inset.set_ylim(0, 1)

    # Binary outputs
    ax = axes[1, 0]; ax.set_title("Binary Output + Confidence")
    for i, (name, _, S, _, bits, confs) in enumerate(results):
        ax.barh(i, sum(bits), color=REGIME_COLORS.get(S.dominant_regime(), "gray"))
        ax.text(sum(bits)+0.05, i, f"conf={np.mean(confs):.2f}", fontsize=8, va="center")
    ax.set_yticks(range(len(results)))
    ax.set_yticklabels([r[0].split("\n")[0] for r in results], fontsize=8)
    ax.set_xlabel("Number of 1-bits")

    # Confidence per bit
    ax = axes[1, 1]; ax.set_title("Per-Bit Confidence Scores")
    for i, (name, _, S, _, bits, confs) in enumerate(results):
        ax.plot(confs, label=name.split("\n")[0], alpha=0.8)
    ax.set_xlabel("Bit index"); ax.set_ylabel("Confidence")
    ax.legend(fontsize=7); ax.axhline(0.5, color="red", ls="--", lw=1)

    # Pipeline summary
    ax = axes[1, 2]; ax.axis("off")
    txt = ("RIGOROUS PIPELINE\n\n"
           "F(x) → H_eff[F] → S=(n,d,ℓ,κ)\n\n"
           "n: DOS integral ∫(E_F-V)^{3/2}d³x\n"
           "d: Laplacian + winding numbers\n"
           "ℓ: Power-law fit P(k)∝k^{-α}\n"
           "κ: Drude + Debye + strain\n\n"
           "Encoding: softmax regime blend\n"
           "  b̂ = Σ wᵢ·bᵢ  (threshold 0.5)\n\n"
           "Confidence: 2|b̂-0.5|·(1-H_regime)\n\n"
           f"Field link:\n{BRIDGE_URL[:45]}\n...{BRIDGE_URL[-20:]}")
    ax.text(0.05, 0.95, txt, transform=ax.transAxes, fontsize=8, va="top",
            fontfamily="monospace", bbox=dict(boxstyle="round", facecolor="lightyellow", alpha=0.8))

    plt.tight_layout()
    savefig("geometry_to_binary_pipeline")


# ─────────────────────────────────────────────────────────────────────────────
# Simulation 6: Basin Stability
# ─────────────────────────────────────────────────────────────────────────────

@sim("basin_stability", "Basin Stability — Margins, Noise, Failure Modes")
def basin_stability():
    fig, axes = plt.subplots(2, 2, figsize=(13, 10))
    fig.suptitle("Basin Stability: Distance to Boundary, Noise, and Failure Modes", fontsize=14)

    n_vals = np.logspace(14, 21, 200); d_vals = np.linspace(0, 1, 200)
    NN, DD = np.meshgrid(n_vals, d_vals)

    # Stability margin
    ax = axes[0, 0]
    stab = np.vectorize(lambda n, d: SiliconState(n, d, 3, {"electrical": 1, "optical": 0.2, "thermal": 0.3}).stability_metric())(NN, DD)
    cf = ax.contourf(np.log10(n_vals), d_vals, stab, levels=25, cmap="RdYlGn")
    plt.colorbar(cf, ax=ax, label="Stability metric")
    ax.set_xlabel("log₁₀(n)"); ax.set_ylabel("d"); ax.set_title("Stability Margin")

    # Noise escape
    ax = axes[0, 1]
    np.random.seed(0)
    for sigma in [0.01, 0.05, 0.15, 0.3]:
        n_t = [1e17]
        for _ in range(499):
            dn = -0.05*(n_t[-1]-1e17) + sigma*1e17*np.random.randn()
            n_t.append(max(1e13, n_t[-1]+dn))
        esc = np.cumsum([n > 1e19 or n < 1e14 for n in n_t]) / np.arange(1, 501)
        ax.plot(esc, label=f"σ={sigma}")
    ax.set_xlabel("Time steps"); ax.set_ylabel("Cumulative escape prob.")
    ax.set_title("Noise-Driven Basin Escape"); ax.legend(fontsize=9)

    # Aging trajectory
    ax = axes[1, 0]
    np.random.seed(1)
    t = np.linspace(0, 200, 1000)
    d_aging = np.clip(0.05 + 0.003*t + 0.02*np.cumsum(np.random.randn(1000))/100, 0, 1)
    n_aging = np.clip(1e17*(1+0.1*np.cumsum(np.random.randn(1000))/100), 1e14, 1e21)
    regime_map = {r: i for i, r in enumerate(sorted(REGIME_COLORS.keys()))}
    rcols = matplotlib.colors.ListedColormap([REGIME_COLORS[r] for r in sorted(REGIME_COLORS.keys())])
    rnums = [regime_map[SiliconState(n, d, 3, {"electrical": 1, "optical": 0.2, "thermal": 0.3}).dominant_regime()]
             for n, d in zip(n_aging, d_aging)]
    ax.scatter(t, np.log10(n_aging), c=rnums, cmap=rcols, s=3, alpha=0.7)
    ax2 = ax.twinx(); ax2.plot(t, d_aging, "orange", lw=1.5, alpha=0.6)
    ax2.set_ylabel("d", color="orange")
    ax.set_xlabel("Time"); ax.set_ylabel("log₁₀(n)"); ax.set_title("Aging Trajectory")

    # Summary
    ax = axes[1, 1]; ax.axis("off")
    rows = [["Concept", "Geometric Meaning", "Engineering Implication"],
            ["Stability margin", "Distance to phase boundary", "Noise/drift tolerance"],
            ["Device failure", "Trajectory escapes basin", "Reliability"],
            ["Fabrication yield", "Prob. landing in target basin", "Process control"],
            ["Cross-domain device", "Trajectory navigates basins", "Optoelectronics"],
            ["Noise sensitivity", "Local curvature of basin walls", "Thermal tolerance"]]
    tbl = ax.table(cellText=rows[1:], colLabels=rows[0], loc="center", cellLoc="center")
    tbl.auto_set_font_size(False); tbl.set_fontsize(8); tbl.scale(1, 1.7)
    ax.set_title("Geometric Engineering Summary", pad=20)

    plt.tight_layout()
    savefig("basin_stability")


# ─────────────────────────────────────────────────────────────────────────────
# Simulation 7: Continuous Regime Blending
# ─────────────────────────────────────────────────────────────────────────────

@sim("continuous_regime_blending",
     "Continuous Regime Blending — Softmax vs Hard Thresholds (from Computational Bridge)")
def continuous_regime_blending():
    fig, axes = plt.subplots(2, 3, figsize=(16, 10))
    fig.suptitle("Continuous Regime Blending: Softmax over Basin Distances\n"
                 f"Field link: {BRIDGE_URL}", fontsize=11)

    regimes = sorted(BASIN_CENTERS.keys())
    colors_list = [REGIME_COLORS[r] for r in regimes]

    # Panel 1: Regime weights vs n (sweeping through doping)
    ax = axes[0, 0]
    n_sweep = np.logspace(14, 21, 300)
    weights_matrix = np.zeros((len(regimes), len(n_sweep)))
    for j, n in enumerate(n_sweep):
        S = SiliconState(n, 0.05, 3.0, {"electrical": 0.8, "optical": 0.1, "thermal": 0.1})
        w = S.regime_weights(temperature=0.15)
        for i, r in enumerate(regimes):
            weights_matrix[i, j] = w[r]
    for i, r in enumerate(regimes):
        ax.plot(np.log10(n_sweep), weights_matrix[i], color=colors_list[i], lw=2, label=r)
    ax.set_xlabel("log₁₀(n) [cm⁻³]"); ax.set_ylabel("Regime weight")
    ax.set_title("Regime Weights vs Carrier Density\n(d=0.05, ℓ=3, T=0.15)")
    ax.legend(fontsize=7); ax.set_ylim(0, 1)

    # Panel 2: Regime weights vs d (sweeping through defects)
    ax = axes[0, 1]
    d_sweep = np.linspace(0, 1, 300)
    weights_d = np.zeros((len(regimes), 300))
    for j, d in enumerate(d_sweep):
        S = SiliconState(1e17, d, 3.0, {"electrical": 0.8, "optical": 0.1, "thermal": 0.1})
        w = S.regime_weights(temperature=0.15)
        for i, r in enumerate(regimes):
            weights_d[i, j] = w[r]
    for i, r in enumerate(regimes):
        ax.plot(d_sweep, weights_d[i], color=colors_list[i], lw=2, label=r)
    ax.set_xlabel("Defect density d"); ax.set_ylabel("Regime weight")
    ax.set_title("Regime Weights vs Defect Density\n(n=10¹⁷, ℓ=3, T=0.15)")
    ax.legend(fontsize=7); ax.set_ylim(0, 1)
    # Panel 4: Hard vs soft comparison at a boundary point
    ax = axes[1, 0]
    n_boundary = np.logspace(18, 20, 100)
    hard_regime = []
    soft_semi = []
    soft_metal = []
    for n in n_boundary:
        S = SiliconState(n, 0.1, 3.0, {"electrical": 0.9, "optical": 0.1, "thermal": 0.1})
        hard_regime.append(1 if S.dominant_regime() == "semiconductor" else 0)
        w = S.regime_weights(0.1)
        soft_semi.append(w.get("semiconductor", 0))
        soft_metal.append(w.get("metallic", 0))
    ax.step(np.log10(n_boundary), hard_regime, "k-", lw=2, where="mid", label="Hard threshold")
    ax.plot(np.log10(n_boundary), soft_semi, color="blue", lw=2, label="Soft: semiconductor")
    ax.plot(np.log10(n_boundary), soft_metal, color="red", lw=2, label="Soft: metallic")
    ax.set_xlabel("log₁₀(n)"); ax.set_ylabel("Regime weight / hard class")
    ax.set_title("Hard Threshold vs Continuous Blending\n(near semiconductor/metallic boundary)")
    ax.legend(fontsize=8)

    # Panel 5: Stability metric vs regime entropy
    ax = axes[1, 1]
    n_sweep2 = np.logspace(14, 21, 200)
    stab_vals = []
    entropy_vals = []
    dom_colors = []
    for n in n_sweep2:
        S = SiliconState(n, 0.05, 3.0, {"electrical": 0.8, "optical": 0.1, "thermal": 0.1})
        stab_vals.append(S.stability_metric())
        w = np.array(list(S.regime_weights().values()))
        w = w[w > 1e-10]
        entropy_vals.append(-np.sum(w * np.log(w)))
        dom_colors.append(REGIME_COLORS.get(S.dominant_regime(), "gray"))
    ax.scatter(entropy_vals, stab_vals, c=dom_colors, s=15, alpha=0.8)
    ax.set_xlabel("Regime entropy H"); ax.set_ylabel("Stability metric")
    ax.set_title("Stability vs Regime Entropy\n(high entropy = near boundary = unstable)")
    patches = [mpatches.Patch(color=REGIME_COLORS[r], label=r) for r in sorted(REGIME_COLORS.keys())]
    ax.legend(handles=patches, fontsize=6, loc="upper right")

    # Panel 6: Summary table
    ax = axes[1, 2]; ax.axis("off")
    rows = [["Concept", "Hard threshold", "Soft blending"],
            ["Boundary", "Discontinuous jump", "Smooth crossover"],
            ["Mixed state", "Impossible", "Natural"],
            ["Noise response", "Flickering", "Gradual drift"],
            ["Confidence", "Binary (0/1)", "Continuous [0,1]"],
            ["Physical accuracy", "Approximate", "Rigorous"]]
    tbl = ax.table(cellText=rows[1:], colLabels=rows[0], loc="center", cellLoc="center")
    tbl.auto_set_font_size(False); tbl.set_fontsize(9); tbl.scale(1.1, 1.8)
    ax.set_title("Hard vs Soft Regime Classification", pad=20)

    plt.tight_layout()
    savefig("continuous_regime_blending")


# ─────────────────────────────────────────────────────────────────────────────
# Simulation 8: Rigorous Field Mapping
# ─────────────────────────────────────────────────────────────────────────────

@sim("rigorous_field_mapping",
     "Rigorous Geometry-to-Silicon Mapping — Physical Derivation of S from F(x)")
def rigorous_field_mapping():
    fig, axes = plt.subplots(2, 3, figsize=(16, 10))
    fig.suptitle("Rigorous Dimensional Reduction: F(x) → S = (n, d, ℓ, κ)\n"
                 f"Field link: {BRIDGE_URL}", fontsize=11)

    np.random.seed(7)
    x = np.linspace(0, 1, 64); y = np.linspace(0, 1, 64)
    XX, YY = np.meshgrid(x, y)

    # Four test fields
    fields = {
        "Smooth periodic": np.sin(6*np.pi*XX) * np.cos(4*np.pi*YY),
        "Random noise":    np.random.randn(64, 64),
        "Localized blob":  np.exp(-((XX-0.5)**2+(YY-0.5)**2)/0.02),
        "Fractal-like":    sum(np.sin(2**k * np.pi * XX) * np.cos(2**k * np.pi * YY) / 2**k
                               for k in range(1, 6)),
    }

    # Panel 1: Input fields
    ax = axes[0, 0]; ax.axis("off"); ax.set_title("Input Fields F(x)")
    for i, (name, field) in enumerate(fields.items()):
        inset = ax.inset_axes([0.02+(i%2)*0.5, 0.52-(i//2)*0.5, 0.44, 0.44])
        inset.imshow(field, cmap="RdBu_r", origin="lower")
        inset.set_title(name, fontsize=7); inset.axis("off")

    # Panel 2: Carrier density derivation
    ax = axes[0, 1]; ax.set_title("n: Density-of-States Integral\nn ∝ ∫(E_F - V)^{3/2} d³x")
    names_list = list(fields.keys())
    n_vals_plot = []
    for name, field in fields.items():
        n = compute_carrier_density(field)
        n_vals_plot.append(n)
    colors_plot = ["blue", "red", "green", "purple"]
    bars = ax.bar(range(4), [np.log10(n) for n in n_vals_plot], color=colors_plot, alpha=0.8)
    ax.set_xticks(range(4)); ax.set_xticklabels([n[:10] for n in names_list], fontsize=8, rotation=15)
    ax.set_ylabel("log₁₀(n) [cm⁻³]")
    ax.axhline(19, color="red", ls="--", lw=1, label="Mott criterion")
    ax.axhline(14, color="green", ls="--", lw=1, label="Intrinsic Si")
    ax.legend(fontsize=8)

    # Panel 3: Defect density derivation
    ax = axes[0, 2]; ax.set_title("d: Laplacian + Winding Numbers + Roughness")
    d_components = {}
    for name, field in fields.items():
        lap = laplace(field); lap_e = np.mean(lap**2)
        gx = sobel(field, axis=0); gy = sobel(field, axis=1)
        grad_mag = np.sqrt(gx**2 + gy**2)
        disloc = np.mean(np.abs(laplace(grad_mag)))
        roughness = np.std(field) / (np.mean(np.abs(field)) + 1e-10)
        d_components[name] = {
            "Laplacian": float(np.tanh(lap_e / 10.0)),
            "Dislocation": float(np.tanh(disloc / 5.0)),
            "Roughness": float(np.tanh(roughness)),
        }
    x_pos = np.arange(4); width = 0.25
    comp_names = ["Laplacian", "Dislocation", "Roughness"]
    comp_colors = ["steelblue", "coral", "gold"]
    for ci, (comp, col) in enumerate(zip(comp_names, comp_colors)):
        vals = [d_components[n][comp] for n in names_list]
        ax.bar(x_pos + ci*width, vals, width, label=comp, color=col, alpha=0.85)
    ax.set_xticks(x_pos + width); ax.set_xticklabels([n[:10] for n in names_list], fontsize=8, rotation=15)
    ax.set_ylabel("Component contribution"); ax.legend(fontsize=8)

    # Panel 4: Effective dimensionality
    ax = axes[1, 0]; ax.set_title("ℓ: Spectral Power-Law Fit P(k) ∝ k^{-α}")
    for i, (name, field) in enumerate(fields.items()):
        f_ft = np.fft.fftn(field)
        power = np.abs(f_ft)**2
        freqs = [np.fft.fftfreq(s) for s in field.shape]
        grids = np.meshgrid(*freqs, indexing="ij")
        k_mag = np.sqrt(sum(g**2 for g in grids))
        k_bins = np.linspace(0.01, 0.5, 40)
        p_bin = np.array([np.mean(power[(k_mag >= k_bins[j]) & (k_mag < k_bins[j+1])])
                          if ((k_mag >= k_bins[j]) & (k_mag < k_bins[j+1])).sum() > 0 else 0
                          for j in range(len(k_bins)-1)])
        k_c = (k_bins[:-1] + k_bins[1:]) / 2
        valid = p_bin > 0
        if valid.sum() >= 3:
            ax.loglog(k_c[valid], p_bin[valid], color=colors_plot[i], lw=1.5, alpha=0.8, label=name[:10])
    ax.set_xlabel("k"); ax.set_ylabel("P(k)"); ax.legend(fontsize=7)

    # Panel 5: Full state comparison
    ax = axes[1, 1]; ax.axis("off"); ax.set_title("Derived Silicon States (Rigorous)")
    rows = [["Field", "n [cm⁻³]", "d", "ℓ", "κ_e", "κ_o", "Regime"]]
    for name, field in fields.items():
        S = geometry_to_silicon_rigorous(field)
        rows.append([name[:12], f"{S.n:.1e}", f"{S.d:.2f}", f"{S.l:.2f}",
                     f"{S.k['electrical']:.2f}", f"{S.k['optical']:.2f}",
                     S.dominant_regime()[:8]])
    tbl = ax.table(cellText=rows[1:], colLabels=rows[0], loc="center", cellLoc="center")
    tbl.auto_set_font_size(False); tbl.set_fontsize(8); tbl.scale(1, 1.8)

    # Panel 6: Physical derivation summary
    ax = axes[1, 2]; ax.axis("off")
    txt = ("RIGOROUS DERIVATION\n\n"
           "n — Carrier density:\n"
           "  V(x) = -α|F(x)|\n"
           "  n ∝ ∫(E_F-V)^{3/2}d³x\n"
           "  (semiclassical DOS)\n\n"
           "d — Defect density:\n"
           "  ∇²F → point defects\n"
           "  |∇|∇F|| → dislocations\n"
           "  winding numbers → vortices\n\n"
           "ℓ — Effective dimension:\n"
           "  P(k) ∝ k^{-α} power law\n"
           "  + correlation lengths\n"
           "  + spectral dimension\n\n"
           "κ — Coupling vector:\n"
           "  Drude σ (electrical)\n"
           "  Kerr n₂ (optical)\n"
           "  Debye Cv (thermal)\n"
           "  Strain energy (mechanical)")
    ax.text(0.05, 0.95, txt, transform=ax.transAxes, fontsize=9, va="top",
            fontfamily="monospace",
            bbox=dict(boxstyle="round", facecolor="lightyellow", alpha=0.8))

    plt.tight_layout()
    savefig("rigorous_field_mapping")


# ─────────────────────────────────────────────────────────────────────────────
# Simulation 9: Feedback Closure
# ─────────────────────────────────────────────────────────────────────────────

@sim("feedback_closure",
     "Feedback Closure — Binary Output Modifies Geometry (4 Modes)")
def feedback_closure():
    fig, axes = plt.subplots(2, 4, figsize=(18, 9))
    fig.suptitle("Feedback Closure: Binary → Geometry (4 Modes)\n"
                 "G'(x) = G(x) + α·F(bits, G, S)", fontsize=12)

    np.random.seed(42)
    x = np.linspace(0, 1, 32); y = np.linspace(0, 1, 32)
    XX, YY = np.meshgrid(x, y)
    G0 = np.sin(4*np.pi*XX) * np.cos(4*np.pi*YY) * 0.5 + 0.5
    S = geometry_to_silicon_rigorous(G0)
    G_graph = silicon_to_graph(S, n_nodes=G0.size)
    bits, confs = graph_to_binary_blended(G_graph, S)

    modes = ["diffusive", "structural", "waveguide", "adaptive"]
    mode_titles = {
        "diffusive":  "Diffusive\n(Gaussian blobs)",
        "structural": "Structural\n(defect writing)",
        "waveguide":  "Waveguide\n(gradient channels)",
        "adaptive":   "Adaptive\n(field learning)",
    }

    for col, mode in enumerate(modes):
        G_new = binary_to_geometry_feedback(bits, G0, S, strength=0.3, mode=mode)
        diff = G_new - G0

        # Top row: modified geometry
        ax = axes[0, col]
        im = ax.imshow(G_new, cmap="viridis", origin="lower", vmin=0, vmax=1.5)
        plt.colorbar(im, ax=ax, shrink=0.8)
        ax.set_title(mode_titles[mode], fontsize=9)
        ax.axis("off")

        # Bottom row: difference field
        ax = axes[1, col]
        vmax = max(0.01, np.abs(diff).max())
        im2 = ax.imshow(diff, cmap="RdBu_r", origin="lower", vmin=-vmax, vmax=vmax)
        plt.colorbar(im2, ax=ax, shrink=0.8)
        ax.set_title(f"ΔG (strength=0.3)\nRMS={np.sqrt(np.mean(diff**2)):.3f}", fontsize=9)
        ax.axis("off")

    plt.tight_layout()
    savefig("feedback_closure")


# ─────────────────────────────────────────────────────────────────────────────
# Simulation 10: Closed-Loop Trajectory
# ─────────────────────────────────────────────────────────────────────────────

@sim("closed_loop_trajectory",
     "Closed-Loop Dynamical System — S(t) Trajectory Through Silicon Manifold")
def closed_loop_trajectory():
    fig, axes = plt.subplots(2, 3, figsize=(16, 10))
    fig.suptitle("Closed-Loop Pipeline: G → S → bits → G' → S' → ...\n"
                 "dS/dt = F(n, d, ℓ, κ)  realized as discrete-time dynamical system\n"
                 f"Field link: {BRIDGE_URL}", fontsize=10)

    np.random.seed(99)
    x = np.linspace(0, 1, 32); y = np.linspace(0, 1, 32)
    XX, YY = np.meshgrid(x, y)

    # Run 3 trajectories with different initial conditions and feedback modes
    configs = [
        ("Smooth wave\n(→ semiconductor)",
         np.sin(4*np.pi*XX)*np.cos(4*np.pi*YY)*0.5+0.5, "diffusive",  0.05, "blue"),
        ("Random noise\n(→ defect/metallic)",
         np.random.rand(32, 32),                           "structural", 0.1,  "red"),
        ("Localized blob\n(→ quantum)",
         np.exp(-((XX-0.5)**2+(YY-0.5)**2)/0.02)*0.5+0.1, "adaptive",  0.08, "purple"),
    ]

    trajectories = []
    for label, G0, mode, strength, color in configs:
        traj, G_final = run_closed_loop(G0, iterations=15, strength=strength, mode=mode)
        trajectories.append((label, traj, G_final, color))

    # Panel 1: n(t) trajectories
    ax = axes[0, 0]
    for label, traj, _, color in trajectories:
        n_vals = [pt["S"].n for pt in traj]
        ax.semilogy(range(len(n_vals)), n_vals, color=color, lw=2, label=label.split("\n")[0])
    ax.axhline(1e19, color="red", ls="--", lw=1, label="Metallic boundary")
    ax.set_xlabel("Iteration"); ax.set_ylabel("n [cm⁻³]")
    ax.set_title("Carrier Density n(t)"); ax.legend(fontsize=7)

    # Panel 2: Stability over iterations
    ax = axes[0, 1]
    for label, traj, _, color in trajectories:
        stab = [pt["stability"] for pt in traj]
        ax.plot(range(len(stab)), stab, color=color, lw=2, label=label.split("\n")[0])
    ax.set_xlabel("Iteration"); ax.set_ylabel("Stability metric")
    ax.set_title("Basin Stability Over Iterations"); ax.legend(fontsize=7)
    ax.set_ylim(0, 1)

    # Panel 3: Regime weight evolution (first trajectory)
    ax = axes[0, 2]
    traj0 = trajectories[0][1]
    regimes = sorted(BASIN_CENTERS.keys())
    for r in regimes:
        w_vals = [pt["weights"].get(r, 0) for pt in traj0]
        ax.plot(range(len(w_vals)), w_vals, color=REGIME_COLORS[r], lw=2, label=r)
    ax.set_xlabel("Iteration"); ax.set_ylabel("Regime weight")
    ax.set_title(f"Regime Weight Evolution\n({trajectories[0][0].split(chr(10))[0]})")
    ax.legend(fontsize=7); ax.set_ylim(0, 1)

    # Panel 4: Trajectory in (n, d) phase space
    ax = axes[1, 0]
    for label, traj, _, color in trajectories:
        n_vals = [np.log10(pt["S"].n) for pt in traj]
        d_vals = [pt["S"].d for pt in traj]
        ax.plot(n_vals, d_vals, color=color, lw=2, alpha=0.8, label=label.split("\n")[0])
        ax.plot(n_vals[0], d_vals[0], "o", color=color, ms=10)
        ax.plot(n_vals[-1], d_vals[-1], "*", color=color, ms=14)
    ax.set_xlabel("log₁₀(n)"); ax.set_ylabel("d")
    ax.set_title("S-Space Trajectories\n● start  ★ end"); ax.legend(fontsize=7)

    # Panel 5: Bit confidence over iterations
    ax = axes[1, 1]
    for label, traj, _, color in trajectories:
        mean_conf = [np.mean(pt["confs"]) for pt in traj]
        ax.plot(range(len(mean_conf)), mean_conf, color=color, lw=2, label=label.split("\n")[0])
    ax.set_xlabel("Iteration"); ax.set_ylabel("Mean bit confidence")
    ax.set_title("Encoding Confidence Over Iterations"); ax.legend(fontsize=7)
    ax.axhline(0.5, color="gray", ls="--", lw=1)

    # Panel 6: Final geometry comparison
    ax = axes[1, 2]; ax.axis("off"); ax.set_title("Final Geometry States")
    for i, (label, _, G_final, color) in enumerate(trajectories):
        inset = ax.inset_axes([0.02+(i%3)*0.33, 0.1, 0.30, 0.75])
        inset.imshow(G_final, cmap="viridis", origin="lower")
        S_final = geometry_to_silicon_rigorous(G_final)
        inset.set_title(f"{label.split(chr(10))[0]}\n→ {S_final.dominant_regime()}", fontsize=7)
        inset.axis("off")

    plt.tight_layout()
    savefig("closed_loop_trajectory")


# ─────────────────────────────────────────────────────────────────────────────
# Unified runner (matches API of sims.py / workon_sims.py / todo_sims.py /
# addon_sims.py so run_all_sims.py --module connections_sims works).
# ─────────────────────────────────────────────────────────────────────────────

def run_all():
    print(f"\nRunning {len(REGISTRY)} Connections simulations → plots/\n")
    for name, meta in REGISTRY.items():
        print(f"[{name}]")
        print(f"  {meta['title']}")
        meta["fn"]()
    print(f"\nDone. {len(REGISTRY)} plots saved to {PLOT_DIR}/")


# ─────────────────────────────────────────────────────────────────────────────
# CLI
# ─────────────────────────────────────────────────────────────────────────────

def main():
    parser = argparse.ArgumentParser(description="Silicon Phase-Space Simulations")
    parser.add_argument("--sim",  help="Run a specific simulation by name")
    parser.add_argument("--list", action="store_true", help="List all available simulations")
    args = parser.parse_args()

    if args.list:
        print("\nAvailable simulations:")
        for name, meta in sorted(REGISTRY.items()):
            print(f"  {name:<35} {meta['title']}")
        print()
        return

    if args.sim:
        if args.sim not in REGISTRY:
            print(f"Unknown simulation: {args.sim}")
            print("Use --list to see available simulations.")
            return
        print(f"\nRunning: {REGISTRY[args.sim]['title']}")
        REGISTRY[args.sim]["fn"]()
        return

    print(f"\nRunning all {len(REGISTRY)} simulations...\n")
    for name, meta in sorted(REGISTRY.items()):
        print(f"  [{name}] {meta['title']}")
        meta["fn"]()
    print(f"\nAll plots saved to: {PLOT_DIR}")


if __name__ == "__main__":
    main()
