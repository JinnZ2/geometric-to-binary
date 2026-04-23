"""
tests/test_registry.py
Smoke tests for the geometric-to-binary repo.

Run with:
    python -m pytest tests/ -v
    python -m pytest tests/ -v --tb=short
"""

import sys
import os
import pytest
import networkx as nx

# Ensure the repo root is on the path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from physics_playground import (
    EquationRegistry, PhysicsDomain, PhysicsEquation,
    PropellerTransform, PhysicsPlayground,
)
import graph as graph_module


# ─────────────────────────────────────────────────────────────
# Fixtures
# ─────────────────────────────────────────────────────────────

@pytest.fixture(scope="module")
def registry():
    r = EquationRegistry()
    r._register_all()
    return r


@pytest.fixture(scope="module")
def eq_graph(registry):
    return graph_module.build_morphism_graph(registry)


@pytest.fixture(scope="module")
def playground():
    return PhysicsPlayground()


# ─────────────────────────────────────────────────────────────
# Registry tests
# ─────────────────────────────────────────────────────────────

class TestRegistry:

    def test_minimum_equation_count(self, registry):
        """Registry must contain at least 90 equations."""
        count = len(registry._equations)
        assert count >= 90, f"Expected ≥90 equations, got {count}"

    def test_minimum_domain_count(self, registry):
        """Registry must span at least 20 physics domains."""
        domains = set(eq.domain for eq in registry._equations.values())
        assert len(domains) >= 20, f"Expected ≥20 domains, got {len(domains)}"

    def test_all_required_domains_present(self, registry):
        """All 23 expected domains must be present."""
        expected = {
            "classical_mechanics", "electromagnetism", "quantum",
            "thermodynamics", "fluid_dynamics", "statistical",
            "relativity", "general_relativity", "plasma_physics",
            "optics", "condensed_matter", "nuclear_physics",
            "astrophysics", "nonlinear_dynamics", "acoustics",
            "biophysics", "information_theory", "cosmology",
            "high_energy_string", "population_dynamics", "neuroscience",
            "molecular_biology", "ecology_systems",
        }
        actual = {eq.domain.value for eq in registry._equations.values()}
        missing = expected - actual
        assert not missing, f"Missing domains: {missing}"

    def test_get_returns_equation(self, registry):
        """registry.get() must return a PhysicsEquation for known names."""
        eq = registry.get("harmonic_oscillator")
        assert eq is not None
        assert isinstance(eq, PhysicsEquation)
        assert eq.name == "harmonic_oscillator"

    def test_get_returns_none_for_unknown(self, registry):
        """registry.get() must return None for unknown equation names."""
        assert registry.get("nonexistent_equation_xyz") is None

    def test_list_all_returns_all_names(self, registry):
        """list_all() must return the same count as _equations."""
        names = registry.list_all()
        assert len(names) == len(registry._equations)
        assert "schrodinger_free" in names
        assert "lotka_volterra_prey" in names
        assert "hill_equation" in names

    def test_biology_equations_present(self, registry):
        """All 17 biology equations must be in the registry."""
        bio_eqs = [
            "logistic_growth", "lotka_volterra_prey", "lotka_volterra_predator",
            "replicator_equation", "wright_fisher_drift",
            "fitzhugh_nagumo_v", "fitzhugh_nagumo_w", "cable_equation",
            "wilson_cowan_E", "hill_equation", "arrhenius",
            "turing_activator", "turing_inhibitor",
            "fisher_kpp", "sir_susceptible", "sir_infected", "allometric_scaling",
        ]
        for name in bio_eqs:
            assert registry.get(name) is not None, f"Missing biology equation: {name}"

    def test_equations_have_required_fields(self, registry):
        """Every equation must have name, domain, description, latex, symbolic_expr."""
        for name, eq in registry._equations.items():
            assert eq.name,          f"{name}: missing name"
            assert eq.domain,        f"{name}: missing domain"
            assert eq.description,   f"{name}: missing description"
            assert eq.latex,         f"{name}: missing latex"
            assert eq.symbolic_expr is not None, f"{name}: missing symbolic_expr"

    def test_mix_returns_sympy_expression(self, registry):
        """mix() must return a non-None sympy expression."""
        result = registry.mix("continuity_1d", "schrodinger_free", "add")
        assert result is not None


# ─────────────────────────────────────────────────────────────
# Graph tests
# ─────────────────────────────────────────────────────────────

class TestGraph:

    def test_graph_node_count(self, eq_graph, registry):
        """Graph must have exactly as many nodes as registry equations."""
        assert eq_graph.G.number_of_nodes() == len(registry._equations)

    def test_graph_minimum_edge_count(self, eq_graph):
        """Graph must have at least 110 morphism edges."""
        count = eq_graph.G.number_of_edges()
        assert count >= 110, f"Expected ≥110 edges, got {count}"

    def test_graph_fully_connected(self, eq_graph):
        """The morphism graph must be a single weakly connected component."""
        components = list(nx.weakly_connected_components(eq_graph.G))
        assert len(components) == 1, (
            f"Graph has {len(components)} components; "
            f"isolated: {[list(c)[0] for c in components if len(c)==1]}"
        )

    def test_no_isolated_nodes(self, eq_graph):
        """No equation should have degree zero (no morphism connections)."""
        isolated = [n for n, d in eq_graph.G.degree() if d == 0]
        assert not isolated, f"Isolated nodes: {isolated}"

    def test_path_exists_classical_to_quantum(self, eq_graph):
        """A path must exist from harmonic_oscillator to klein_gordon."""
        path = eq_graph.path("harmonic_oscillator", "klein_gordon")
        assert len(path) >= 2
        assert path[0] == "harmonic_oscillator"
        assert path[-1] == "klein_gordon"

    def test_path_exists_biology_to_quantum(self, eq_graph):
        """A path must exist from hill_equation to fermi_dirac."""
        path = eq_graph.path("hill_equation", "fermi_dirac")
        assert len(path) >= 1
        assert path[0] == "hill_equation"
        assert path[-1] == "fermi_dirac"

    def test_path_exists_classical_to_plasma(self, eq_graph):
        """A path must exist from newton_2 to vlasov_1d (classical → plasma)."""
        path = eq_graph.path("newton_2", "vlasov_1d")
        assert len(path) >= 3
        assert path[0] == "newton_2"
        assert path[-1] == "vlasov_1d"

    def test_reachable_from_returns_set(self, eq_graph):
        """reachable_from() must return a non-empty collection."""
        # Use a high-degree hub node (schrodinger_free has many outgoing edges)
        reachable = eq_graph.reachable_from("schrodinger_free")
        assert reachable is not None
        assert len(reachable) >= 1, "Expected schrodinger_free to reach at least 1 equation"

    def test_domain_cluster_returns_correct_domain(self, eq_graph):
        """domain_cluster() must return a non-empty list for a known domain."""
        from physics_playground import PhysicsDomain
        cluster = eq_graph.domain_cluster(PhysicsDomain.QUANTUM)
        assert isinstance(cluster, list)
        assert len(cluster) > 0, "Expected at least one equation in quantum domain"

    def test_all_paths_returns_list(self, eq_graph):
        """all_paths() must return a list of paths."""
        paths = eq_graph.all_paths("continuity_1d", "schrodinger_free", cutoff=4)
        assert isinstance(paths, list)
        assert len(paths) >= 1

    def test_edge_weights_are_non_negative(self, eq_graph):
        """All edge weights must be non-negative."""
        for u, v, data in eq_graph.G.edges(data=True):
            w = data.get("weight", 0.0)
            assert w >= 0, f"Negative weight on edge {u}→{v}: {w}"


# ─────────────────────────────────────────────────────────────
# PhysicsPlayground tests
# ─────────────────────────────────────────────────────────────

class TestPlayground:

    def test_info_returns_string(self, playground):
        """info() must return a non-empty string for a known equation."""
        result = playground.info("harmonic_oscillator")
        assert isinstance(result, str)
        assert "harmonic_oscillator" in result
        assert "classical_mechanics" in result

    def test_info_unknown_equation(self, playground):
        """info() must return a helpful message for unknown equations."""
        result = playground.info("not_a_real_equation")
        assert "not found" in result.lower()

    def test_morph_returns_dict(self, playground):
        """morph() must return a dict with path, steps, and total_weight."""
        result = playground.morph("harmonic_oscillator", "klein_gordon")
        assert isinstance(result, dict)
        assert "path" in result
        assert "steps" in result
        assert "total_weight" in result

    def test_morph_path_is_valid(self, playground):
        """morph() path must start and end at the correct equations."""
        result = playground.morph("harmonic_oscillator", "klein_gordon")
        assert result["path"][0]  == "harmonic_oscillator"
        assert result["path"][-1] == "klein_gordon"

    def test_morph_steps_match_path(self, playground):
        """morph() steps must have len(path)-1 entries."""
        result = playground.morph("harmonic_oscillator", "klein_gordon")
        assert len(result["steps"]) == len(result["path"]) - 1

    def test_morph_total_weight_non_negative(self, playground):
        """morph() total_weight must be non-negative."""
        result = playground.morph("hill_equation", "fermi_dirac")
        assert result["total_weight"] >= 0

    def test_morph_biology_to_quantum(self, playground):
        """morph() must find a path from a biology equation to a quantum one."""
        result = playground.morph("hill_equation", "fermi_dirac")
        assert len(result["path"]) >= 2
        assert "error" not in result

    def test_creative_mix_morph(self, playground):
        """creative_mix() with operation='morph' must return a sympy expression."""
        result = playground.creative_mix("harmonic_oscillator", operation="morph")
        assert result is not None

    def test_propeller_transform(self, playground):
        """PropellerTransform must apply to a classical equation without error."""
        result = playground.propeller.apply_fokker_planck_morph("harmonic_oscillator")
        assert result is not None


# ─────────────────────────────────────────────────────────────
# PropellerTransform tests
# ─────────────────────────────────────────────────────────────

class TestPropellerTransform:

    def test_apply_to_all_classical_equations(self, registry):
        """PropellerTransform must not crash on any classical mechanics equation."""
        pt = PropellerTransform(registry)
        classical = [
            name for name, eq in registry._equations.items()
            if eq.domain == PhysicsDomain.CLASSICAL_MECHANICS
        ]
        for name in classical:
            result = pt.apply_fokker_planck_morph(name)
            assert result is not None, f"PropellerTransform failed on {name}"
