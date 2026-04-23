"""
graph.py
EquationGraph: a directed, weighted state-space graph over the equation registry.

Nodes  = PhysicsEquation objects (identified by name)
Edges  = Morphisms (named transformations between equations)
Weights = composite score:
    α * dimensional_inconsistency
    β * constraint_violation
    γ * domain_distance

Domain distance matrix encodes how "far apart" two physics domains are
conceptually (0 = same domain, 1 = adjacent, 2 = moderate jump, 3 = large jump).
"""

import networkx as nx
from dataclasses import dataclass, field
from typing import Dict, List, Optional, Tuple, Callable
from physics_playground import PhysicsEquation, PhysicsDomain, EquationRegistry

# ============================================================
# WEIGHT PARAMETERS
# ============================================================

ALPHA = 0.4   # weight for dimensional inconsistency
BETA  = 0.3   # weight for constraint violation
GAMMA = 0.3   # weight for domain distance

# ============================================================
# DOMAIN DISTANCE MATRIX
# ============================================================
# Symmetric integer distances between domains.
# 0 = same domain, 1 = closely related, 2 = moderate, 3 = large conceptual gap

_DOMAIN_DISTANCE: Dict[Tuple[str, str], int] = {
    # --- Classical Mechanics neighbours ---
    ("classical_mechanics", "fluid_dynamics"):       1,
    ("classical_mechanics", "thermodynamics"):       1,
    ("classical_mechanics", "statistical"):          2,
    ("classical_mechanics", "quantum"):              2,
    ("classical_mechanics", "relativity"):           2,
    ("classical_mechanics", "general_relativity"):   3,
    ("classical_mechanics", "electromagnetism"):     1,
    ("classical_mechanics", "acoustics"):            1,
    ("classical_mechanics", "nonlinear_dynamics"):   1,
    ("classical_mechanics", "astrophysics"):         2,
    ("classical_mechanics", "plasma_physics"):       2,
    ("classical_mechanics", "optics"):               2,
    ("classical_mechanics", "condensed_matter"):     2,
    ("classical_mechanics", "nuclear_physics"):      3,
    ("classical_mechanics", "biophysics"):           2,
    ("classical_mechanics", "information_theory"):   3,
    ("classical_mechanics", "cosmology"):            3,
    ("classical_mechanics", "high_energy_string"):   3,
    # --- Quantum neighbours ---
    ("quantum", "statistical"):                      1,
    ("quantum", "condensed_matter"):                 1,
    ("quantum", "high_energy_string"):               1,
    ("quantum", "nuclear_physics"):                  1,
    ("quantum", "electromagnetism"):                 1,
    ("quantum", "fluid_dynamics"):                   2,
    ("quantum", "thermodynamics"):                   2,
    ("quantum", "biophysics"):                       2,
    ("quantum", "information_theory"):               2,
    ("quantum", "optics"):                           1,
    ("quantum", "plasma_physics"):                   2,
    ("quantum", "relativity"):                       2,
    ("quantum", "general_relativity"):               3,
    ("quantum", "astrophysics"):                     3,
    ("quantum", "cosmology"):                        3,
    ("quantum", "nonlinear_dynamics"):               3,
    ("quantum", "acoustics"):                        3,
    # --- Fluid Dynamics neighbours ---
    ("fluid_dynamics", "acoustics"):                 1,
    ("fluid_dynamics", "plasma_physics"):            1,
    ("fluid_dynamics", "astrophysics"):              1,
    ("fluid_dynamics", "thermodynamics"):            1,
    ("fluid_dynamics", "statistical"):               2,
    ("fluid_dynamics", "biophysics"):                2,
    ("fluid_dynamics", "nonlinear_dynamics"):        1,
    ("fluid_dynamics", "electromagnetism"):          2,
    ("fluid_dynamics", "cosmology"):                 2,
    ("fluid_dynamics", "general_relativity"):        3,
    ("fluid_dynamics", "high_energy_string"):        3,
    # --- Thermodynamics neighbours ---
    ("thermodynamics", "statistical"):               1,
    ("thermodynamics", "condensed_matter"):          1,
    ("thermodynamics", "astrophysics"):              2,
    ("thermodynamics", "cosmology"):                 2,
    ("thermodynamics", "information_theory"):        2,
    ("thermodynamics", "biophysics"):                2,
    ("thermodynamics", "plasma_physics"):            2,
    ("thermodynamics", "high_energy_string"):        3,
    # --- Statistical neighbours ---
    ("statistical", "information_theory"):           1,
    ("statistical", "condensed_matter"):             1,
    ("statistical", "biophysics"):                   2,
    ("statistical", "astrophysics"):                 2,
    ("statistical", "cosmology"):                    2,
    ("statistical", "high_energy_string"):           2,
    # --- Relativity neighbours ---
    ("relativity", "general_relativity"):            1,
    ("relativity", "electromagnetism"):              1,
    ("relativity", "high_energy_string"):            1,
    ("relativity", "cosmology"):                     2,
    ("relativity", "astrophysics"):                  2,
    ("relativity", "quantum"):                       2,
    # --- General Relativity neighbours ---
    ("general_relativity", "cosmology"):             1,
    ("general_relativity", "astrophysics"):          1,
    ("general_relativity", "high_energy_string"):    1,
    # --- Plasma Physics neighbours ---
    ("plasma_physics", "electromagnetism"):          1,
    ("plasma_physics", "astrophysics"):              1,
    ("plasma_physics", "condensed_matter"):          2,
    ("plasma_physics", "nuclear_physics"):           2,
    # --- Optics neighbours ---
    ("optics", "electromagnetism"):                  1,
    ("optics", "condensed_matter"):                  2,
    ("optics", "quantum"):                           1,
    # --- Condensed Matter neighbours ---
    ("condensed_matter", "nuclear_physics"):         2,
    ("condensed_matter", "biophysics"):              2,
    ("condensed_matter", "information_theory"):      2,
    # --- Nuclear Physics neighbours ---
    ("nuclear_physics", "astrophysics"):             1,
    ("nuclear_physics", "high_energy_string"):       2,
    # --- Astrophysics neighbours ---
    ("astrophysics", "cosmology"):                   1,
    # --- Nonlinear Dynamics neighbours ---
    ("nonlinear_dynamics", "biophysics"):            2,
    ("nonlinear_dynamics", "statistical"):           2,
    ("nonlinear_dynamics", "information_theory"):    2,
    # --- Acoustics neighbours ---
    ("acoustics", "biophysics"):                     2,
    # --- Biophysics neighbours ---
    ("biophysics", "information_theory"):            2,
    # --- Information Theory neighbours ---
    ("information_theory", "cosmology"):             3,
    ("information_theory", "high_energy_string"):    3,
}

def domain_distance(d1: PhysicsDomain, d2: PhysicsDomain) -> int:
    """Return the conceptual distance between two domains (0–3)."""
    if d1 == d2:
        return 0
    key = (d1.value, d2.value)
    rev = (d2.value, d1.value)
    return _DOMAIN_DISTANCE.get(key, _DOMAIN_DISTANCE.get(rev, 3))


def compute_weight(src_domain: PhysicsDomain,
                   tgt_domain: PhysicsDomain,
                   dim_inconsistency: float = 0.0,
                   constraint_violation: float = 0.0) -> float:
    """
    Composite edge weight:
        w = α * dim_inconsistency + β * constraint_violation + γ * domain_distance
    Lower weight = more natural / lower-cost transformation.
    """
    dd = domain_distance(src_domain, tgt_domain)
    return (ALPHA * dim_inconsistency
            + BETA  * constraint_violation
            + GAMMA * dd)


# ============================================================
# MORPHISM DESCRIPTOR
# ============================================================

@dataclass
class Morphism:
    """Describes a named transformation between two equations."""
    name: str
    source_eq: str
    target_eq: str
    source_domain: PhysicsDomain
    target_domain: PhysicsDomain
    description: str
    weight: float
    invariants_preserved: List[str] = field(default_factory=list)
    transform_fn: Optional[Callable] = field(default=None, repr=False)


# ============================================================
# EQUATION GRAPH
# ============================================================

class EquationGraph:
    """
    Directed weighted graph over the equation registry.

    Nodes  = equation names (str)
    Edges  = Morphism objects stored as edge attributes
    """

    def __init__(self):
        self.G: nx.DiGraph = nx.DiGraph()
        self._morphisms: Dict[str, Morphism] = {}

    # ----------------------------------------------------------
    # Node management
    # ----------------------------------------------------------
    def add_equation(self, eq: PhysicsEquation):
        self.G.add_node(
            eq.name,
            domain=eq.domain.value,
            description=eq.description,
            latex=eq.latex
        )

    def add_equations_from_registry(self, registry: EquationRegistry):
        for name in registry.list_all():
            self.add_equation(registry.get(name))

    # ----------------------------------------------------------
    # Edge management
    # ----------------------------------------------------------
    def add_morphism(self, morphism: Morphism):
        """Add a directed edge for a named morphism."""
        # Ensure nodes exist (add stubs if needed)
        if morphism.source_eq not in self.G:
            self.G.add_node(morphism.source_eq,
                            domain=morphism.source_domain.value)
        if morphism.target_eq not in self.G:
            self.G.add_node(morphism.target_eq,
                            domain=morphism.target_domain.value)

        self.G.add_edge(
            morphism.source_eq,
            morphism.target_eq,
            morphism=morphism.name,
            weight=morphism.weight,
            description=morphism.description,
            invariants=morphism.invariants_preserved
        )
        self._morphisms[morphism.name] = morphism

    # ----------------------------------------------------------
    # Navigation
    # ----------------------------------------------------------
    def neighbors(self, eq_name: str) -> List[str]:
        return list(self.G.successors(eq_name))

    def path(self, start: str, end: str) -> List[str]:
        """Shortest (lowest-weight) path between two equations."""
        return nx.shortest_path(self.G, start, end, weight="weight")

    def all_paths(self, start: str, end: str,
                  cutoff: int = 5) -> List[List[str]]:
        """All simple paths up to a given length."""
        return list(nx.all_simple_paths(self.G, start, end, cutoff=cutoff))

    def reachable_from(self, eq_name: str) -> List[str]:
        """All equations reachable from a given node."""
        return list(nx.descendants(self.G, eq_name))

    def domain_cluster(self, domain: PhysicsDomain) -> List[str]:
        """All equations belonging to a given domain."""
        return [n for n, d in self.G.nodes(data='domain')
                if d == domain.value]

    def summary(self) -> str:
        lines = [
            f"EquationGraph: {self.G.number_of_nodes()} nodes, "
            f"{self.G.number_of_edges()} edges",
            f"Morphisms registered: {len(self._morphisms)}",
        ]
        for name, m in self._morphisms.items():
            lines.append(
                f"  [{m.weight:.2f}] {m.source_eq} --[{m.name}]--> {m.target_eq}"
            )
        return "\n".join(lines)


# ============================================================
# MORPHISM LIBRARY
# ============================================================

def build_morphism_graph(registry: EquationRegistry) -> EquationGraph:
    """
    Construct the fully wired EquationGraph from the registry.
    Each morphism is a named, physically motivated transformation.
    """
    graph = EquationGraph()
    graph.add_equations_from_registry(registry)

    def M(name, src, tgt, desc, dim=0.0, con=0.0, inv=None):
        """Shorthand morphism factory."""
        src_eq = registry.get(src)
        tgt_eq = registry.get(tgt)
        if src_eq is None or tgt_eq is None:
            return  # skip if either node missing
        w = compute_weight(src_eq.domain, tgt_eq.domain, dim, con)
        graph.add_morphism(Morphism(
            name=name,
            source_eq=src, target_eq=tgt,
            source_domain=src_eq.domain, target_domain=tgt_eq.domain,
            description=desc, weight=w,
            invariants_preserved=inv or []
        ))

    # ----------------------------------------------------------
    # CLASSICAL MECHANICS → other domains
    # ----------------------------------------------------------
    M("newtonian_to_lagrangian",
      "newton_2", "lagrangian_free_particle",
      "Replace F=ma with Lagrangian variational principle.",
      dim=0.0, con=0.0, inv=["energy"])

    M("lagrangian_to_euler_lagrange",
      "lagrangian_free_particle", "euler_lagrange",
      "Derive equations of motion from the Lagrangian via calculus of variations.",
      dim=0.0, con=0.0, inv=["action"])

    M("classical_to_statistical",
      "energy_conservation", "boltzmann_factor",
      "Replace deterministic energy with Boltzmann probability weight.",
      dim=0.1, con=0.2, inv=["energy"])

    M("classical_to_quantum_correspondence",
      "harmonic_oscillator", "qho_energy_levels",
      "Quantize the harmonic oscillator: replace classical amplitude with discrete energy levels.",
      dim=0.0, con=0.1, inv=["frequency"])

    M("classical_to_diffusion_morph",
      "harmonic_oscillator", "ficks_second_law",
      "Propeller morph: add Fokker-Planck diffusion term to classical oscillator.",
      dim=0.2, con=0.3)

    M("newton_to_euler_fluid",
      "newton_2", "euler_momentum_1d",
      "Extend Newton's law to a continuous fluid element (continuum limit).",
      dim=0.0, con=0.1, inv=["momentum"])

    M("newton_to_navier_stokes",
      "euler_momentum_1d", "navier_stokes_1d",
      "Add viscous stress term to the Euler momentum equation.",
      dim=0.0, con=0.0, inv=["momentum"])

    M("classical_to_acoustic",
      "newton_2", "acoustic_wave_equation",
      "Apply Newton's law to a compressible fluid element to derive acoustic waves.",
      dim=0.0, con=0.1, inv=["momentum"])

    M("classical_to_relativistic",
      "energy_conservation", "mass_energy_equivalence",
      "Extend classical energy to include rest-mass energy via special relativity.",
      dim=0.0, con=0.1, inv=["energy"])

    # ----------------------------------------------------------
    # QUANTUM MECHANICS bridges
    # ----------------------------------------------------------
    M("schrodinger_to_probability_current",
      "schrodinger_free", "probability_current",
      "Derive the probability current from the Schrödinger equation.",
      dim=0.0, con=0.0, inv=["probability"])

    M("schrodinger_to_de_broglie",
      "schrodinger_free", "de_broglie",
      "Extract the de Broglie wavelength from the plane-wave solution of Schrödinger.",
      dim=0.0, con=0.0, inv=["momentum"])

    M("schrodinger_to_klein_gordon",
      "schrodinger_free", "klein_gordon",
      "Relativistic extension of Schrödinger: replace non-relativistic kinetic term.",
      dim=0.0, con=0.2, inv=["probability"])

    M("schrodinger_to_dirac",
      "klein_gordon", "dirac_1d",
      "Factor the Klein-Gordon equation to obtain the first-order Dirac equation.",
      dim=0.0, con=0.1, inv=["probability", "spin"])

    M("quantum_to_statistical",
      "qho_energy_levels", "boltzmann_factor",
      "Populate quantum energy levels with Boltzmann thermal weights.",
      dim=0.0, con=0.1, inv=["energy"])

    M("quantum_to_information",
      "heisenberg_uncertainty", "shannon_entropy",
      "Map quantum uncertainty (ΔxΔp) to information-theoretic entropy bound.",
      dim=0.3, con=0.2)

    M("quantum_to_condensed_matter",
      "schrodinger_free", "bloch_dispersion_1d",
      "Apply Schrödinger equation to a periodic lattice to obtain Bloch bands.",
      dim=0.0, con=0.1, inv=["energy", "momentum"])

    M("quantum_to_bcs",
      "schrodinger_free", "bcs_gap_equation",
      "Cooper-pair condensation: quantum many-body extension to BCS superconductivity.",
      dim=0.1, con=0.2, inv=["energy"])

    # ----------------------------------------------------------
    # FLUID DYNAMICS bridges
    # ----------------------------------------------------------
    M("continuity_to_schrodinger_madelung",
      "continuity_1d", "schrodinger_free",
      "Madelung transform: rewrite fluid continuity + Euler as Schrödinger equation.",
      dim=0.1, con=0.1, inv=["probability", "mass"])

    M("fluid_to_acoustic",
      "continuity_1d", "acoustic_wave_equation",
      "Linearize continuity + Euler equations around equilibrium to get acoustic waves.",
      dim=0.0, con=0.0, inv=["mass"])

    M("euler_to_bernoulli",
      "euler_momentum_1d", "bernoulli",
      "Integrate Euler momentum along a streamline to obtain Bernoulli's principle.",
      dim=0.0, con=0.0, inv=["energy"])

    M("fluid_to_plasma_vlasov",
      "navier_stokes_1d", "vlasov_1d",
      "Replace fluid velocity field with phase-space distribution function.",
      dim=0.1, con=0.2, inv=["mass", "momentum"])

    M("fluid_to_stellar",
      "euler_momentum_1d", "hydrostatic_equilibrium",
      "Apply fluid momentum balance to a self-gravitating sphere (stellar interior).",
      dim=0.0, con=0.1, inv=["momentum"])

    # ----------------------------------------------------------
    # THERMODYNAMICS bridges
    # ----------------------------------------------------------
    M("thermo_to_statistical",
      "boltzmann_entropy", "partition_function",
      "Connect Boltzmann entropy S = k_B ln Ω to the canonical partition function.",
      dim=0.0, con=0.0, inv=["entropy"])

    M("thermo_to_information",
      "boltzmann_entropy", "shannon_entropy",
      "Shannon entropy is the information-theoretic analogue of Boltzmann entropy.",
      dim=0.1, con=0.1, inv=["entropy"])

    M("thermo_to_landauer",
      "boltzmann_entropy", "landauer_principle",
      "Landauer's principle connects thermodynamic entropy to the cost of bit erasure.",
      dim=0.1, con=0.1, inv=["entropy"])

    M("ideal_gas_to_cosmology",
      "ideal_gas_law", "dark_energy_eos",
      "Generalize ideal gas EOS to cosmic fluid with dark energy equation of state.",
      dim=0.2, con=0.3)

    # ----------------------------------------------------------
    # STATISTICAL MECHANICS bridges
    # ----------------------------------------------------------
    M("statistical_to_maxwell_boltzmann",
      "boltzmann_factor", "maxwell_boltzmann_speed",
      "Apply Boltzmann factor to kinetic energy to derive Maxwell-Boltzmann speed distribution.",
      dim=0.0, con=0.0, inv=["energy"])

    M("statistical_to_fermi_dirac",
      "partition_function", "fermi_dirac",
      "Restrict partition function to fermionic states to obtain Fermi-Dirac distribution.",
      dim=0.0, con=0.1, inv=["energy", "particle_number"])

    # ----------------------------------------------------------
    # SPECIAL RELATIVITY bridges
    # ----------------------------------------------------------
    M("lorentz_to_momentum",
      "lorentz_factor", "relativistic_momentum",
      "Multiply rest mass momentum by Lorentz factor.",
      dim=0.0, con=0.0, inv=["momentum"])

    M("special_to_general_relativity",
      "spacetime_interval", "schwarzschild_metric_tt",
      "Promote flat Minkowski metric to curved Schwarzschild geometry.",
      dim=0.0, con=0.2, inv=["spacetime_interval"])

    M("mass_energy_to_friedmann",
      "mass_energy_equivalence", "friedmann_first",
      "Apply mass-energy equivalence to cosmic energy density in Friedmann equations.",
      dim=0.1, con=0.2, inv=["energy"])

    # ----------------------------------------------------------
    # GENERAL RELATIVITY bridges
    # ----------------------------------------------------------
    M("einstein_to_geodesic",
      "einstein_field_equation", "geodesic_equation",
      "Derive test-particle geodesic motion from the Einstein field equations.",
      dim=0.0, con=0.0, inv=["energy", "momentum"])

    M("schwarzschild_to_geodesic",
      "schwarzschild_metric_tt", "geodesic_equation",
      "Compute geodesics in the Schwarzschild spacetime.",
      dim=0.0, con=0.0, inv=["energy", "angular_momentum"])

    M("gr_to_cosmology",
      "einstein_field_equation", "friedmann_first",
      "Apply Einstein equations to a homogeneous isotropic universe (FLRW ansatz).",
      dim=0.0, con=0.0, inv=["energy"])

    M("gr_to_astrophysics",
      "einstein_field_equation", "hydrostatic_equilibrium",
      "Newtonian limit of Einstein equations recovers stellar hydrostatic equilibrium.",
      dim=0.1, con=0.1, inv=["energy"])

    # ----------------------------------------------------------
    # PLASMA PHYSICS bridges
    # ----------------------------------------------------------
    M("plasma_to_debye",
      "plasma_frequency", "debye_length",
      "Debye length is the spatial analogue of the plasma frequency (screening scale).",
      dim=0.0, con=0.0, inv=["charge"])

    M("vlasov_to_fluid",
      "vlasov_1d", "continuity_1d",
      "Take velocity moments of the Vlasov equation to recover fluid continuity.",
      dim=0.0, con=0.1, inv=["mass"])

    M("plasma_to_wave",
      "plasma_frequency", "wave_equation_1d",
      "Plasma oscillations at ω_p propagate as electromagnetic waves.",
      dim=0.1, con=0.1, inv=["frequency"])

    # ----------------------------------------------------------
    # OPTICS bridges
    # ----------------------------------------------------------
    M("snell_to_paraxial",
      "snells_law", "paraxial_helmholtz",
      "Snell's law is the ray-optics limit of the paraxial Helmholtz wave equation.",
      dim=0.0, con=0.1, inv=["frequency"])

    M("paraxial_to_wave",
      "paraxial_helmholtz", "wave_equation_1d",
      "Paraxial Helmholtz equation reduces to the 1D wave equation along the optical axis.",
      dim=0.0, con=0.0, inv=["frequency"])

    M("optics_to_quantum",
      "paraxial_helmholtz", "schrodinger_free",
      "Formal analogy: paraxial wave equation ↔ time-dependent Schrödinger (z ↔ t).",
      dim=0.1, con=0.2, inv=["frequency"])

    # ----------------------------------------------------------
    # CONDENSED MATTER bridges
    # ----------------------------------------------------------
    M("drude_to_plasma",
      "drude_conductivity", "plasma_frequency",
      "Drude model conductivity diverges at ω_p; both arise from free-electron dynamics.",
      dim=0.0, con=0.1, inv=["charge"])

    M("bloch_to_schrodinger",
      "bloch_dispersion_1d", "schrodinger_free",
      "Bloch states are solutions of the Schrödinger equation in a periodic potential.",
      dim=0.0, con=0.0, inv=["energy", "momentum"])

    M("fermi_dirac_to_statistical",
      "fermi_dirac", "boltzmann_factor",
      "High-temperature limit of Fermi-Dirac recovers the classical Boltzmann factor.",
      dim=0.0, con=0.1, inv=["energy"])

    # ----------------------------------------------------------
    # NUCLEAR PHYSICS bridges
    # ----------------------------------------------------------
    M("decay_to_statistical",
      "radioactive_decay", "boltzmann_factor",
      "Decay probability per unit time is analogous to a Boltzmann rate factor.",
      dim=0.1, con=0.2)

    M("yukawa_to_klein_gordon",
      "yukawa_potential", "klein_gordon",
      "Yukawa potential is the static solution of the massive Klein-Gordon equation.",
      dim=0.0, con=0.0, inv=["energy"])

    M("nuclear_to_astrophysics",
      "semf_binding_energy", "stellar_mass_continuity",
      "Nuclear binding energy determines stellar fuel; links to stellar mass distribution.",
      dim=0.2, con=0.2)

    # ----------------------------------------------------------
    # ASTROPHYSICS bridges
    # ----------------------------------------------------------
    M("hydrostatic_to_stellar_mass",
      "hydrostatic_equilibrium", "stellar_mass_continuity",
      "Hydrostatic equilibrium and mass continuity form the coupled stellar structure equations.",
      dim=0.0, con=0.0, inv=["mass", "momentum"])

    M("virial_to_jeans",
      "virial_theorem", "jeans_mass",
      "Jeans mass is derived by applying the virial theorem to a self-gravitating gas cloud.",
      dim=0.0, con=0.0, inv=["energy"])

    M("astrophysics_to_cosmology",
      "hydrostatic_equilibrium", "friedmann_first",
      "Cosmological Friedmann equations generalize stellar hydrostatic equilibrium to the universe.",
      dim=0.1, con=0.2, inv=["energy"])

    # ----------------------------------------------------------
    # NONLINEAR DYNAMICS bridges
    # ----------------------------------------------------------
    M("logistic_to_lorenz",
      "logistic_map", "lorenz_x",
      "Both exhibit period-doubling and chaotic attractors; logistic map is the 1D limit.",
      dim=0.0, con=0.1)

    M("van_der_pol_to_harmonic",
      "van_der_pol", "harmonic_oscillator",
      "Van der Pol oscillator reduces to harmonic oscillator when μ → 0.",
      dim=0.0, con=0.0, inv=["frequency"])

    M("chaos_to_information",
      "lyapunov_exponent", "shannon_entropy",
      "Positive Lyapunov exponent implies information production (Kolmogorov-Sinai entropy).",
      dim=0.2, con=0.2, inv=["entropy"])

    # ----------------------------------------------------------
    # ACOUSTICS bridges
    # ----------------------------------------------------------
    M("acoustic_to_fluid",
      "acoustic_wave_equation", "continuity_1d",
      "Acoustic wave equation is the linearized limit of fluid continuity + Euler.",
      dim=0.0, con=0.0, inv=["mass"])

    M("acoustic_to_em_wave",
      "acoustic_wave_equation", "wave_equation_1d",
      "Structural analogy between acoustic pressure waves and EM field waves.",
      dim=0.1, con=0.1, inv=["frequency"])

    # ----------------------------------------------------------
    # BIOPHYSICS bridges
    # ----------------------------------------------------------
    M("ficks_first_to_second",
      "ficks_first_law", "ficks_second_law",
      "Combine Fick's first law with mass conservation to derive the diffusion equation.",
      dim=0.0, con=0.0, inv=["mass"])

    M("diffusion_to_fokker_planck",
      "ficks_second_law", "continuity_1d",
      "Diffusion equation is the zero-drift limit of the Fokker-Planck equation.",
      dim=0.0, con=0.1, inv=["probability"])

    M("biophysics_to_statistical",
      "michaelis_menten", "boltzmann_factor",
      "Michaelis-Menten saturation kinetics can be derived from statistical rate theory.",
      dim=0.2, con=0.2)

    M("membrane_to_wave",
      "hodgkin_huxley_membrane", "acoustic_wave_equation",
      "Nerve impulse propagation along an axon is formally analogous to a damped wave.",
      dim=0.2, con=0.3)

    # ----------------------------------------------------------
    # INFORMATION THEORY bridges
    # ----------------------------------------------------------
    M("shannon_to_kl",
      "shannon_entropy", "kl_divergence",
      "KL divergence generalizes Shannon entropy to relative information between distributions.",
      dim=0.0, con=0.0, inv=["entropy"])

    M("landauer_to_thermo",
      "landauer_principle", "boltzmann_entropy",
      "Landauer's principle connects bit erasure cost to thermodynamic entropy.",
      dim=0.0, con=0.0, inv=["entropy"])

    M("information_to_cosmology",
      "shannon_entropy", "dark_energy_eos",
      "Holographic principle: information entropy bounds relate to cosmological dark energy.",
      dim=0.3, con=0.3)

    # ----------------------------------------------------------
    # COSMOLOGY bridges
    # ----------------------------------------------------------
    M("hubble_to_friedmann",
      "hubble_parameter", "friedmann_first",
      "Hubble parameter H = ȧ/a is the central quantity in the Friedmann equations.",
      dim=0.0, con=0.0, inv=["energy"])

    M("friedmann_to_dark_energy",
      "friedmann_first", "dark_energy_eos",
      "Dark energy equation of state w enters the Friedmann equations as a fluid component.",
      dim=0.0, con=0.0, inv=["energy"])

    M("redshift_to_hubble",
      "redshift_scale_factor", "hubble_parameter",
      "Cosmological redshift directly encodes the expansion history H(z).",
      dim=0.0, con=0.0, inv=["energy"])

    # ----------------------------------------------------------
    # HIGH ENERGY / STRING THEORY bridges
    # ----------------------------------------------------------
    M("klein_gordon_to_dirac",
      "klein_gordon", "dirac_1d",
      "Dirac equation is the square root of the Klein-Gordon equation.",
      dim=0.0, con=0.1, inv=["probability"])

    M("dirac_to_schrodinger",
      "dirac_1d", "schrodinger_free",
      "Non-relativistic limit of the Dirac equation recovers the Schrödinger equation.",
      dim=0.0, con=0.1, inv=["probability"])

    M("nambu_goto_to_action",
      "nambu_goto_action", "lagrangian_free_particle",
      "Nambu-Goto string action generalizes the point-particle action to a 1D extended object.",
      dim=0.1, con=0.2, inv=["action"])

    M("rg_to_statistical",
      "rg_beta_function", "partition_function",
      "RG flow of coupling constants is governed by the partition function under scale transformations.",
      dim=0.1, con=0.2, inv=["symmetry"])

    return graph


# ============================================================
# ENTRY POINT
# ============================================================

if __name__ == "__main__":
    registry = EquationRegistry()
    graph    = build_morphism_graph(registry)

    print(graph.summary())

    print("\n--- Shortest path: harmonic_oscillator → klein_gordon ---")
    try:
        p = graph.path("harmonic_oscillator", "klein_gordon")
        print(" → ".join(p))
    except nx.NetworkXNoPath:
        print("No path found.")

    print("\n--- All paths (cutoff=4): continuity_1d → schrodinger_free ---")
    for path in graph.all_paths("continuity_1d", "schrodinger_free", cutoff=4):
        print(" → ".join(path))

    print("\n--- Equations reachable from harmonic_oscillator ---")
    print(", ".join(sorted(graph.reachable_from("harmonic_oscillator"))))
