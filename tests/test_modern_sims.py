"""
tests/test_modern_sims.py

Tests for modern_sims.py — Level 6: Modern Mathematical Models. Follows the
repo's pytest style: registry completeness plus a correctness invariant per sim.

Run with:
    python -m pytest tests/test_modern_sims.py -v
"""

import sys
import os

import numpy as np
import pytest

# Ensure the repo root is on the path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from modern_sims import REGISTRY, MODERN_SIMS, run_sim


# ── Module contract ──────────────────────────────────────────────────────────

def test_registry_complete():
    assert len(REGISTRY) == 12
    assert all(callable(meta["fn"]) for meta in REGISTRY.values())
    assert all(meta["title"] for meta in REGISTRY.values())


def test_module_follows_sim_contract():
    """run_all_sims.py --module modern_sims needs REGISTRY + run_all + PLOT_DIR."""
    import modern_sims

    assert callable(modern_sims.run_all)
    assert os.path.basename(modern_sims.PLOT_DIR) == "plots"
    # back-compat view stays in sync with the decorated registry
    assert set(MODERN_SIMS) == set(REGISTRY)


def test_module_is_registered_in_run_all_sims():
    import run_all_sims

    assert "modern_sims" in [m for m, _ in run_all_sims.MODULES]


# ── Per-sim correctness invariants ───────────────────────────────────────────

def test_koopman_reconstruction_is_close():
    assert run_sim("koopman_dmd")["rel_error"] < 0.15


def test_wasserstein_variance_grows():
    assert run_sim("wasserstein_jko")["variance_growth"] > 0


def test_fisher_rao_geodesic_stays_in_halfplane():
    geo = run_sim("fisher_rao_flow")["geodesic"]
    assert np.all(geo[:, 1] > 0)  # sigma > 0 everywhere along the geodesic


def test_lorenz_has_two_persistent_loops():
    assert run_sim("persistent_homology")["max_betti1"] >= 2


def test_exceptional_point_at_gamma_equals_k():
    assert run_sim("pt_symmetric_dimer")["exceptional_point_gamma"] == pytest.approx(1.0)


def test_mps_chi8_fidelity_high():
    assert run_sim("mps_compression")["fidelity_at_chi8"] > 0.99


def test_symplectic_beats_rk4():
    res = run_sim("symplectic_vs_rk4")
    assert abs(res["verlet_final_drift"]) < abs(res["rk4_final_drift"]) * 0.1


def test_fractional_kernels_computed():
    assert run_sim("fractional_diffusion")["alphas"] == [2.0, 1.5, 1.0, 0.7]


def test_fluctuation_theorem_slope_near_one():
    res = run_sim("fluctuation_theorem")
    assert res["mean_entropy"] > 0
    assert 0.8 < res["measured_slope"] < 1.2


def test_clifford_rotor_flips():
    assert run_sim("clifford_rotor")["flip_period_approx"] > 0


def test_sinkhorn_cost_decreases_with_eps():
    costs = run_sim("sinkhorn_ot")["transport_cost_by_eps"]
    vals = [costs[k] for k in (0.001, 0.01, 0.05)]
    assert vals[0] <= vals[-1] + 1e-9


def test_fno_low_modes_suffice():
    assert run_sim("fourier_neural_op")["truncation_rel_error"] < 0.05
