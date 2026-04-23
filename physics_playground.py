"""
physics_playground.py
A symbolic sandbox for mixing, matching, and morphing physics equations.
Built on SymPy for the "geometric to binary" style experimental repo.

Domains (20 total):
  Original: Classical Mechanics, Electromagnetism, Quantum, Thermodynamics,
            Fluid Dynamics, Statistical, Relativity
  Extended: General Relativity, Plasma Physics, Optics, Condensed Matter,
            Nuclear Physics, Astrophysics, Nonlinear Dynamics, Acoustics,
            Biophysics, Information Theory, Cosmology, High Energy / String
  Biology:  Population Dynamics, Neuroscience, Molecular Biology,
            Ecology & Systems Biology
"""

import sympy as sp
from sympy import (
    symbols, Function, diff, integrate, exp, sin, cos, sqrt, log,
    pi, I, oo, Rational, Abs
)
from dataclasses import dataclass, field
from typing import Dict, List, Optional
from enum import Enum

# ============================================================
# SECTION 1: CORE SYMBOLIC ENGINE
# ============================================================

class PhysicsDomain(Enum):
    """Label equations by their native domain for creative mixing."""
    CLASSICAL_MECHANICS = "classical_mechanics"
    ELECTROMAGNETISM    = "electromagnetism"
    QUANTUM             = "quantum"
    THERMODYNAMICS      = "thermodynamics"
    FLUID_DYNAMICS      = "fluid_dynamics"
    STATISTICAL         = "statistical"
    RELATIVITY          = "relativity"
    GENERAL_RELATIVITY  = "general_relativity"
    PLASMA_PHYSICS      = "plasma_physics"
    OPTICS              = "optics"
    CONDENSED_MATTER    = "condensed_matter"
    NUCLEAR_PHYSICS     = "nuclear_physics"
    ASTROPHYSICS        = "astrophysics"
    NONLINEAR_DYNAMICS  = "nonlinear_dynamics"
    ACOUSTICS           = "acoustics"
    BIOPHYSICS          = "biophysics"
    INFORMATION_THEORY  = "information_theory"
    COSMOLOGY           = "cosmology"
    HIGH_ENERGY_STRING  = "high_energy_string"
    # --- Biology sub-domains ---
    POPULATION_DYNAMICS = "population_dynamics"
    NEUROSCIENCE        = "neuroscience"
    MOLECULAR_BIOLOGY   = "molecular_biology"
    ECOLOGY_SYSTEMS     = "ecology_systems"
    CUSTOM              = "custom"


@dataclass
class PhysicsEquation:
    """Container for a single physics equation with metadata."""
    name: str
    latex: str
    symbolic_expr: sp.Basic
    domain: PhysicsDomain
    parameters: Dict[str, sp.Basic] = field(default_factory=dict)
    constraints: List[sp.Basic]     = field(default_factory=list)
    description: str = ""

    def substitute(self, subs_dict: Dict) -> 'PhysicsEquation':
        new_expr = self.symbolic_expr.subs(subs_dict)
        return PhysicsEquation(
            name=f"{self.name}_substituted",
            latex=sp.latex(new_expr),
            symbolic_expr=new_expr,
            domain=self.domain,
            parameters={k: v for k, v in self.parameters.items()
                        if k not in subs_dict}
        )

    def moralize(self, target_domain: PhysicsDomain) -> 'MorphedEquation':
        return MorphedEquation(source=self, target_domain=target_domain)


@dataclass
class MorphedEquation:
    """Result of applying a cross-domain transform to an equation."""
    source: PhysicsEquation
    target_domain: PhysicsDomain
    morphed_expr: Optional[sp.Basic] = None
    morph_rules_applied: List[str]   = field(default_factory=list)

    def apply_diffusion_morphism(self,
                                  noise_term: sp.Symbol = None) -> sp.Basic:
        """Classical deterministic eq → add Fokker-Planck stochastic term."""
        if noise_term is None:
            noise_term = symbols('D')
        x, t = symbols('x t')
        P = Function('P')(x, t)
        classical_part = self.source.symbolic_expr
        diffusion_part = noise_term * diff(P, x, 2)
        self.morphed_expr = classical_part + diffusion_part
        self.morph_rules_applied.append("added_diffusion_term")
        return self.morphed_expr


# ============================================================
# SECTION 2: EQUATION REGISTRY
# ============================================================

class EquationRegistry:
    """Central database of physics equations ready for creative mixing."""

    def __init__(self):
        self._equations: Dict[str, PhysicsEquation] = {}
        self._init_symbols()
        self._register_all()

    # ----------------------------------------------------------
    # Symbol table
    # ----------------------------------------------------------
    def _init_symbols(self):
        self.s = {
            't':       symbols('t',       real=True),
            'x':       symbols('x',       real=True),
            'y':       symbols('y',       real=True),
            'z':       symbols('z',       real=True),
            'r':       symbols('r',       positive=True),
            'm':       symbols('m',       positive=True),
            'v':       symbols('v',       real=True),
            'E':       symbols('E',       real=True),
            'p':       symbols('p',       real=True),
            'hbar':    symbols('hbar',    positive=True),
            'k':       symbols('k',       real=True),
            'T':       symbols('T',       positive=True),
            'S':       symbols('S',       real=True),
            'c':       symbols('c',       positive=True),
            'G':       symbols('G',       positive=True),
            'rho':     symbols('rho',     real=True),
            'P':       symbols('P',       real=True),
            'n':       symbols('n',       positive=True),
            'e':       symbols('e',       positive=True),
            'eps0':    symbols('epsilon_0', positive=True),
            'kB':      symbols('k_B',     positive=True),
            'omega':   symbols('omega',   real=True),
            'lambda_': symbols('lambda',  positive=True),
        }

    # ----------------------------------------------------------
    # Helpers
    # ----------------------------------------------------------
    def _sym(self, *keys):
        return (self.s[k] for k in keys)

    def register(self, eq: PhysicsEquation):
        self._equations[eq.name] = eq

    def get(self, name: str) -> Optional[PhysicsEquation]:
        return self._equations.get(name)

    def list_all(self) -> List[str]:
        return list(self._equations.keys())

    def list_by_domain(self, domain: PhysicsDomain) -> List[str]:
        return [n for n, eq in self._equations.items()
                if eq.domain == domain]

    def mix(self, eq1_name: str, eq2_name: str,
            operation: str = 'add') -> sp.Basic:
        """Algebraically combine two equations."""
        eq1, eq2 = self.get(eq1_name), self.get(eq2_name)
        if not eq1 or not eq2:
            raise ValueError("Equation not found in registry")
        lhs1 = eq1.symbolic_expr.lhs if isinstance(eq1.symbolic_expr, sp.Eq) else eq1.symbolic_expr
        lhs2 = eq2.symbolic_expr.lhs if isinstance(eq2.symbolic_expr, sp.Eq) else eq2.symbolic_expr
        if operation == 'add':
            return lhs1 + lhs2
        elif operation == 'multiply':
            return lhs1 * lhs2
        elif operation == 'embed':
            return eq1.symbolic_expr.subs(
                eq2.symbolic_expr.lhs, eq2.symbolic_expr.rhs)
        raise ValueError(f"Unknown operation: {operation}")

    # ----------------------------------------------------------
    # Master registration method
    # ----------------------------------------------------------
    def _register_all(self):
        self._reg_classical_mechanics()
        self._reg_electromagnetism()
        self._reg_quantum()
        self._reg_thermodynamics()
        self._reg_fluid_dynamics()
        self._reg_statistical()
        self._reg_special_relativity()
        self._reg_general_relativity()
        self._reg_plasma_physics()
        self._reg_optics()
        self._reg_condensed_matter()
        self._reg_nuclear_physics()
        self._reg_astrophysics()
        self._reg_nonlinear_dynamics()
        self._reg_acoustics()
        self._reg_biophysics()
        self._reg_information_theory()
        self._reg_cosmology()
        self._reg_high_energy_string()
        # Biology sub-domains
        self._reg_population_dynamics()
        self._reg_neuroscience()
        self._reg_molecular_biology()
        self._reg_ecology_systems()

    # ==========================================================
    # DOMAIN REGISTRATIONS
    # ==========================================================

    # ----------------------------------------------------------
    # 1. CLASSICAL MECHANICS
    # ----------------------------------------------------------
    def _reg_classical_mechanics(self):
        t, x, m, v, k, S = (self.s[q] for q in ['t','x','m','v','k','S'])
        F = Function('F')(t);  a = Function('a')(t)

        self.register(PhysicsEquation(
            name="newton_2", domain=PhysicsDomain.CLASSICAL_MECHANICS,
            latex=r"F = m a",
            symbolic_expr=sp.Eq(F, m * a),
            description="Newton's second law of motion."
        ))
        self.register(PhysicsEquation(
            name="harmonic_oscillator", domain=PhysicsDomain.CLASSICAL_MECHANICS,
            latex=r"m \ddot{x} = -k x",
            symbolic_expr=sp.Eq(m * diff(x, t, 2), -k * x),
            description="Classical spring-mass harmonic oscillator."
        ))
        self.register(PhysicsEquation(
            name="lagrangian_free_particle", domain=PhysicsDomain.CLASSICAL_MECHANICS,
            latex=r"L = \frac{1}{2} m v^2",
            symbolic_expr=sp.Eq(Function('L')(x, v, t), Rational(1,2) * m * v**2),
            description="Lagrangian for a 1D free particle."
        ))
        # Euler-Lagrange equation
        L_fn = Function('L')
        q_fn = Function('q')(t)
        self.register(PhysicsEquation(
            name="euler_lagrange", domain=PhysicsDomain.CLASSICAL_MECHANICS,
            latex=r"\frac{d}{dt}\frac{\partial L}{\partial \dot{q}} - \frac{\partial L}{\partial q} = 0",
            symbolic_expr=sp.Eq(
                diff(diff(L_fn(q_fn, diff(q_fn,t), t), diff(q_fn,t)), t)
                - diff(L_fn(q_fn, diff(q_fn,t), t), q_fn), 0),
            description="Euler-Lagrange equation of motion."
        ))
        # Conservation of energy
        self.register(PhysicsEquation(
            name="energy_conservation", domain=PhysicsDomain.CLASSICAL_MECHANICS,
            latex=r"E = \frac{1}{2}mv^2 + V(x)",
            symbolic_expr=sp.Eq(
                Function('E')(t),
                Rational(1,2)*m*v**2 + Function('V')(x)),
            description="Total mechanical energy (kinetic + potential)."
        ))

    # ----------------------------------------------------------
    # 2. ELECTROMAGNETISM
    # ----------------------------------------------------------
    def _reg_electromagnetism(self):
        x, t, c = self.s['x'], self.s['t'], self.s['c']
        phi = Function('phi')(x, t)
        eps0, e = self.s['eps0'], self.s['e']
        r = self.s['r'];  q = symbols('q')

        self.register(PhysicsEquation(
            name="wave_equation_1d", domain=PhysicsDomain.ELECTROMAGNETISM,
            latex=r"\frac{\partial^2 \phi}{\partial t^2} = c^2 \frac{\partial^2 \phi}{\partial x^2}",
            symbolic_expr=sp.Eq(diff(phi, t, 2), c**2 * diff(phi, x, 2)),
            description="1D classical wave equation."
        ))
        # Coulomb's law
        F_c = symbols('F_c');  k_e = symbols('k_e')
        self.register(PhysicsEquation(
            name="coulombs_law", domain=PhysicsDomain.ELECTROMAGNETISM,
            latex=r"F = k_e \frac{q_1 q_2}{r^2}",
            symbolic_expr=sp.Eq(F_c, k_e * symbols('q1') * symbols('q2') / r**2),
            description="Coulomb's electrostatic force law."
        ))
        # Faraday's law (1D integral form)
        EMF = symbols('EMF');  Phi_B = Function('Phi_B')(t)
        self.register(PhysicsEquation(
            name="faradays_law", domain=PhysicsDomain.ELECTROMAGNETISM,
            latex=r"\mathcal{E} = -\frac{d\Phi_B}{dt}",
            symbolic_expr=sp.Eq(EMF, -diff(Phi_B, t)),
            description="Faraday's law of electromagnetic induction."
        ))
        # Poynting energy flux
        S_p = symbols('S_p');  E_f = symbols('E_f');  B_f = symbols('B_f')
        mu0 = symbols('mu_0', positive=True)
        self.register(PhysicsEquation(
            name="poynting_vector", domain=PhysicsDomain.ELECTROMAGNETISM,
            latex=r"S = \frac{1}{\mu_0}(E \times B)",
            symbolic_expr=sp.Eq(S_p, (1/mu0) * E_f * B_f),
            description="Poynting vector (1D scalar proxy) for EM energy flux."
        ))

    # ----------------------------------------------------------
    # 3. QUANTUM MECHANICS
    # ----------------------------------------------------------
    def _reg_quantum(self):
        x, t, m, hbar = (self.s[q] for q in ['x','t','m','hbar'])
        psi = Function('psi')(x, t)
        j   = Function('j')(x, t)

        self.register(PhysicsEquation(
            name="schrodinger_free", domain=PhysicsDomain.QUANTUM,
            latex=r"i\hbar \frac{\partial \psi}{\partial t} = -\frac{\hbar^2}{2m}\frac{\partial^2 \psi}{\partial x^2}",
            symbolic_expr=sp.Eq(
                I*hbar*diff(psi, t),
                -(hbar**2)/(2*m)*diff(psi, x, 2)),
            description="Time-dependent Schrödinger equation, 1D free particle."
        ))
        self.register(PhysicsEquation(
            name="probability_current", domain=PhysicsDomain.QUANTUM,
            latex=r"j = \frac{\hbar}{2mi}(\psi^*\nabla\psi - \psi\nabla\psi^*)",
            symbolic_expr=sp.Eq(
                j,
                (hbar/(2*m*I))*(sp.conjugate(psi)*diff(psi,x)
                                - psi*diff(sp.conjugate(psi),x))),
            description="Quantum probability current density."
        ))
        # Heisenberg uncertainty principle
        Delta_x, Delta_p = symbols('Delta_x Delta_p', positive=True)
        self.register(PhysicsEquation(
            name="heisenberg_uncertainty", domain=PhysicsDomain.QUANTUM,
            latex=r"\Delta x \, \Delta p \geq \frac{\hbar}{2}",
            symbolic_expr=sp.Ge(Delta_x * Delta_p, hbar/2),
            description="Heisenberg position-momentum uncertainty principle."
        ))
        # Quantum harmonic oscillator energy levels
        n_qn = symbols('n', nonnegative=True, integer=True)
        omega = self.s['omega']
        self.register(PhysicsEquation(
            name="qho_energy_levels", domain=PhysicsDomain.QUANTUM,
            latex=r"E_n = \hbar\omega\left(n + \frac{1}{2}\right)",
            symbolic_expr=sp.Eq(
                Function('E')(n_qn),
                hbar*omega*(n_qn + Rational(1,2))),
            description="Quantum harmonic oscillator energy eigenvalues."
        ))
        # de Broglie wavelength
        lam = symbols('lambda_dB', positive=True)
        p   = self.s['p']
        self.register(PhysicsEquation(
            name="de_broglie", domain=PhysicsDomain.QUANTUM,
            latex=r"\lambda = \frac{h}{p}",
            symbolic_expr=sp.Eq(lam, 2*pi*hbar / p),
            description="de Broglie matter-wave wavelength."
        ))

    # ----------------------------------------------------------
    # 4. THERMODYNAMICS
    # ----------------------------------------------------------
    def _reg_thermodynamics(self):
        T, S, E, P_sym, n = (self.s[q] for q in ['T','S','E','P','n'])
        kB = self.s['kB'];  V = symbols('V', positive=True)

        self.register(PhysicsEquation(
            name="first_law_thermo", domain=PhysicsDomain.THERMODYNAMICS,
            latex=r"dU = \delta Q - \delta W",
            symbolic_expr=sp.Eq(
                symbols('dU'),
                symbols('delta_Q') - symbols('delta_W')),
            description="First law of thermodynamics."
        ))
        self.register(PhysicsEquation(
            name="second_law_entropy", domain=PhysicsDomain.THERMODYNAMICS,
            latex=r"dS \geq \frac{\delta Q}{T}",
            symbolic_expr=sp.Ge(symbols('dS'), symbols('delta_Q')/T),
            description="Second law: entropy never decreases in an isolated system."
        ))
        self.register(PhysicsEquation(
            name="ideal_gas_law", domain=PhysicsDomain.THERMODYNAMICS,
            latex=r"PV = nRT",
            symbolic_expr=sp.Eq(P_sym*V, n*symbols('R')*T),
            description="Ideal gas law."
        ))
        self.register(PhysicsEquation(
            name="boltzmann_entropy", domain=PhysicsDomain.THERMODYNAMICS,
            latex=r"S = k_B \ln \Omega",
            symbolic_expr=sp.Eq(S, kB * log(symbols('Omega'))),
            description="Boltzmann's statistical definition of entropy."
        ))

    # ----------------------------------------------------------
    # 5. FLUID DYNAMICS
    # ----------------------------------------------------------
    def _reg_fluid_dynamics(self):
        x, t, rho, P_sym = (self.s[q] for q in ['x','t','rho','P'])
        u = Function('u')(x, t)

        self.register(PhysicsEquation(
            name="continuity_1d", domain=PhysicsDomain.FLUID_DYNAMICS,
            latex=r"\frac{\partial\rho}{\partial t}+\frac{\partial(\rho u)}{\partial x}=0",
            symbolic_expr=sp.Eq(diff(rho, t) + diff(rho*u, x), 0),
            description="1D mass continuity equation."
        ))
        # Euler momentum equation (1D inviscid)
        self.register(PhysicsEquation(
            name="euler_momentum_1d", domain=PhysicsDomain.FLUID_DYNAMICS,
            latex=r"\rho\left(\frac{\partial u}{\partial t}+u\frac{\partial u}{\partial x}\right)=-\frac{\partial P}{\partial x}",
            symbolic_expr=sp.Eq(
                rho*(diff(u,t) + u*diff(u,x)),
                -diff(P_sym, x)),
            description="1D Euler momentum equation (inviscid)."
        ))
        # Navier-Stokes (1D viscous)
        mu = symbols('mu', positive=True)
        self.register(PhysicsEquation(
            name="navier_stokes_1d", domain=PhysicsDomain.FLUID_DYNAMICS,
            latex=r"\rho\frac{Du}{Dt}=-\frac{\partial P}{\partial x}+\mu\frac{\partial^2 u}{\partial x^2}",
            symbolic_expr=sp.Eq(
                rho*(diff(u,t) + u*diff(u,x)),
                -diff(P_sym,x) + mu*diff(u,x,2)),
            description="1D Navier-Stokes viscous momentum equation."
        ))
        # Bernoulli equation
        v, g_acc = self.s['v'], symbols('g', positive=True)
        h = symbols('h', real=True)
        self.register(PhysicsEquation(
            name="bernoulli", domain=PhysicsDomain.FLUID_DYNAMICS,
            latex=r"P + \frac{1}{2}\rho v^2 + \rho g h = \text{const}",
            symbolic_expr=P_sym + Rational(1,2)*rho*v**2 + rho*g_acc*h,
            description="Bernoulli's principle for steady inviscid flow."
        ))

    # ----------------------------------------------------------
    # 6. STATISTICAL MECHANICS
    # ----------------------------------------------------------
    def _reg_statistical(self):
        E, k, T, kB = (self.s[q] for q in ['E','k','T','kB'])

        self.register(PhysicsEquation(
            name="boltzmann_factor", domain=PhysicsDomain.STATISTICAL,
            latex=r"P(E)\propto e^{-E/k_BT}",
            symbolic_expr=exp(-E/(kB*T)),
            description="Boltzmann probability weight."
        ))
        # Partition function (discrete)
        Z = symbols('Z');  beta = symbols('beta', positive=True)
        self.register(PhysicsEquation(
            name="partition_function", domain=PhysicsDomain.STATISTICAL,
            latex=r"Z = \sum_i e^{-\beta E_i}",
            symbolic_expr=sp.Eq(Z, sp.Sum(exp(-beta*Function('E')(symbols('i'))),
                                          (symbols('i'), 0, oo))),
            description="Canonical partition function."
        ))
        # Maxwell-Boltzmann speed distribution
        m, v = self.s['m'], self.s['v']
        self.register(PhysicsEquation(
            name="maxwell_boltzmann_speed", domain=PhysicsDomain.STATISTICAL,
            latex=r"f(v)=4\pi\left(\frac{m}{2\pi k_BT}\right)^{3/2}v^2 e^{-mv^2/2k_BT}",
            symbolic_expr=sp.Eq(
                Function('f')(v),
                4*pi*(m/(2*pi*kB*T))**Rational(3,2) * v**2 * exp(-m*v**2/(2*kB*T))),
            description="Maxwell-Boltzmann speed distribution."
        ))

    # ----------------------------------------------------------
    # 7. SPECIAL RELATIVITY
    # ----------------------------------------------------------
    def _reg_special_relativity(self):
        m, c, v = self.s['m'], self.s['c'], self.s['v']
        beta_r = v/c
        gamma  = 1/sqrt(1 - beta_r**2)

        self.register(PhysicsEquation(
            name="mass_energy_equivalence", domain=PhysicsDomain.RELATIVITY,
            latex=r"E = mc^2",
            symbolic_expr=sp.Eq(self.s['E'], m*c**2),
            description="Einstein mass-energy equivalence."
        ))
        self.register(PhysicsEquation(
            name="lorentz_factor", domain=PhysicsDomain.RELATIVITY,
            latex=r"\gamma = \frac{1}{\sqrt{1-v^2/c^2}}",
            symbolic_expr=sp.Eq(symbols('gamma'), gamma),
            description="Lorentz factor."
        ))
        self.register(PhysicsEquation(
            name="relativistic_momentum", domain=PhysicsDomain.RELATIVITY,
            latex=r"p = \gamma m v",
            symbolic_expr=sp.Eq(self.s['p'], gamma*m*v),
            description="Relativistic momentum."
        ))
        # Spacetime interval
        tau = symbols('tau', positive=True)
        dt, dx = symbols('dt dx', real=True)
        self.register(PhysicsEquation(
            name="spacetime_interval", domain=PhysicsDomain.RELATIVITY,
            latex=r"ds^2 = -c^2 dt^2 + dx^2",
            symbolic_expr=sp.Eq(symbols('ds')**2, -c**2*dt**2 + dx**2),
            description="Minkowski spacetime interval (1+1D)."
        ))

    # ----------------------------------------------------------
    # 8. GENERAL RELATIVITY
    # ----------------------------------------------------------
    def _reg_general_relativity(self):
        G, c = self.s['G'], self.s['c']
        R_uv  = symbols('R_mu_nu')
        R_sc  = symbols('R')
        g_uv  = symbols('g_mu_nu')
        T_uv  = symbols('T_mu_nu')
        Lambda = symbols('Lambda')

        self.register(PhysicsEquation(
            name="einstein_field_equation", domain=PhysicsDomain.GENERAL_RELATIVITY,
            latex=r"R_{\mu\nu}-\frac{1}{2}Rg_{\mu\nu}+\Lambda g_{\mu\nu}=\frac{8\pi G}{c^4}T_{\mu\nu}",
            symbolic_expr=sp.Eq(
                R_uv - Rational(1,2)*R_sc*g_uv + Lambda*g_uv,
                (8*pi*G/c**4)*T_uv),
            description="Einstein field equations with cosmological constant."
        ))
        # Schwarzschild metric (tt component)
        r, M = self.s['r'], symbols('M', positive=True)
        self.register(PhysicsEquation(
            name="schwarzschild_metric_tt", domain=PhysicsDomain.GENERAL_RELATIVITY,
            latex=r"g_{tt} = -\left(1 - \frac{2GM}{c^2 r}\right)",
            symbolic_expr=sp.Eq(symbols('g_tt'), -(1 - 2*G*M/(c**2*r))),
            description="Time-time component of the Schwarzschild metric."
        ))
        # Geodesic equation (symbolic)
        tau_s = symbols('tau')
        x_mu  = Function('x_mu')(tau_s)
        Gamma = symbols('Gamma^mu_nu_rho')
        self.register(PhysicsEquation(
            name="geodesic_equation", domain=PhysicsDomain.GENERAL_RELATIVITY,
            latex=r"\frac{d^2 x^\mu}{d\tau^2}+\Gamma^\mu_{\nu\rho}\frac{dx^\nu}{d\tau}\frac{dx^\rho}{d\tau}=0",
            symbolic_expr=sp.Eq(
                diff(x_mu, tau_s, 2) + Gamma*diff(x_mu,tau_s)**2, 0),
            description="Geodesic equation of motion in curved spacetime."
        ))

    # ----------------------------------------------------------
    # 9. PLASMA PHYSICS
    # ----------------------------------------------------------
    def _reg_plasma_physics(self):
        n, e, m, eps0 = (self.s[q] for q in ['n','e','m','eps0'])
        omega = self.s['omega']
        omega_p = symbols('omega_p', positive=True)
        kB, T   = self.s['kB'], self.s['T']

        self.register(PhysicsEquation(
            name="plasma_frequency", domain=PhysicsDomain.PLASMA_PHYSICS,
            latex=r"\omega_p=\sqrt{\frac{n_e e^2}{m_e\epsilon_0}}",
            symbolic_expr=sp.Eq(omega_p, sqrt(n*e**2/(m*eps0))),
            description="Electron plasma oscillation frequency."
        ))
        # Debye length
        lambda_D = symbols('lambda_D', positive=True)
        self.register(PhysicsEquation(
            name="debye_length", domain=PhysicsDomain.PLASMA_PHYSICS,
            latex=r"\lambda_D=\sqrt{\frac{\epsilon_0 k_B T}{n e^2}}",
            symbolic_expr=sp.Eq(lambda_D, sqrt(eps0*kB*T/(n*e**2))),
            description="Debye screening length in a plasma."
        ))
        # Vlasov equation (1D, collisionless)
        x, v_p, t = self.s['x'], self.s['v'], self.s['t']
        f_vl = Function('f')(x, v_p, t)
        E_field = Function('E_field')(x, t)
        self.register(PhysicsEquation(
            name="vlasov_1d", domain=PhysicsDomain.PLASMA_PHYSICS,
            latex=r"\frac{\partial f}{\partial t}+v\frac{\partial f}{\partial x}+\frac{eE}{m}\frac{\partial f}{\partial v}=0",
            symbolic_expr=sp.Eq(
                diff(f_vl,t) + v_p*diff(f_vl,x) + (e*E_field/m)*diff(f_vl,v_p),
                0),
            description="1D collisionless Vlasov equation for phase-space distribution."
        ))

    # ----------------------------------------------------------
    # 10. OPTICS
    # ----------------------------------------------------------
    def _reg_optics(self):
        n1, n2, theta1, theta2 = symbols('n_1 n_2 theta_1 theta_2')
        c = self.s['c'];  lam = symbols('lambda', positive=True)
        f_lens = symbols('f', positive=True)
        d_o, d_i = symbols('d_o d_i', positive=True)

        self.register(PhysicsEquation(
            name="snells_law", domain=PhysicsDomain.OPTICS,
            latex=r"n_1\sin\theta_1=n_2\sin\theta_2",
            symbolic_expr=sp.Eq(n1*sin(theta1), n2*sin(theta2)),
            description="Snell's law of refraction."
        ))
        # Thin lens equation
        self.register(PhysicsEquation(
            name="thin_lens", domain=PhysicsDomain.OPTICS,
            latex=r"\frac{1}{f}=\frac{1}{d_o}+\frac{1}{d_i}",
            symbolic_expr=sp.Eq(1/f_lens, 1/d_o + 1/d_i),
            description="Thin lens equation."
        ))
        # Paraxial wave (Helmholtz) equation (1D)
        x, z = self.s['x'], self.s['z']
        k_opt = 2*pi*n1/lam
        E_opt = Function('E_opt')(x, z)
        self.register(PhysicsEquation(
            name="paraxial_helmholtz", domain=PhysicsDomain.OPTICS,
            latex=r"\frac{\partial^2 E}{\partial x^2}+\frac{\partial^2 E}{\partial z^2}+k^2 E=0",
            symbolic_expr=sp.Eq(
                diff(E_opt,x,2) + diff(E_opt,z,2) + k_opt**2*E_opt, 0),
            description="Paraxial Helmholtz (scalar wave) equation."
        ))
        # Rayleigh resolution criterion
        theta_R = symbols('theta_R', positive=True)
        D_ap    = symbols('D', positive=True)
        self.register(PhysicsEquation(
            name="rayleigh_criterion", domain=PhysicsDomain.OPTICS,
            latex=r"\theta_R = 1.22\frac{\lambda}{D}",
            symbolic_expr=sp.Eq(theta_R, sp.Float('1.22')*lam/D_ap),
            description="Rayleigh angular resolution criterion."
        ))

    # ----------------------------------------------------------
    # 11. CONDENSED MATTER
    # ----------------------------------------------------------
    def _reg_condensed_matter(self):
        n, e, m = self.s['n'], self.s['e'], self.s['m']
        tau = symbols('tau', positive=True)
        sigma = symbols('sigma', positive=True)
        kB, T = self.s['kB'], self.s['T']
        hbar  = self.s['hbar']
        omega = self.s['omega']

        self.register(PhysicsEquation(
            name="drude_conductivity", domain=PhysicsDomain.CONDENSED_MATTER,
            latex=r"\sigma=\frac{ne^2\tau}{m}",
            symbolic_expr=sp.Eq(sigma, n*e**2*tau/m),
            description="Drude model DC electrical conductivity."
        ))
        # Bloch energy dispersion (tight-binding 1D)
        k_bz = symbols('k', real=True)
        t_hop = symbols('t_hop', positive=True)
        a_lat = symbols('a', positive=True)
        self.register(PhysicsEquation(
            name="bloch_dispersion_1d", domain=PhysicsDomain.CONDENSED_MATTER,
            latex=r"E(k) = -2t\cos(ka)",
            symbolic_expr=sp.Eq(Function('E')(k_bz), -2*t_hop*cos(k_bz*a_lat)),
            description="1D tight-binding Bloch energy dispersion."
        ))
        # BCS gap equation (simplified)
        Delta = symbols('Delta', positive=True)
        N0    = symbols('N_0', positive=True)
        V_bcs = symbols('V', positive=True)
        omega_D = symbols('omega_D', positive=True)
        self.register(PhysicsEquation(
            name="bcs_gap_equation", domain=PhysicsDomain.CONDENSED_MATTER,
            latex=r"1 = N(0)V\ln\!\left(\frac{2\hbar\omega_D}{\Delta}\right)",
            symbolic_expr=sp.Eq(1, N0*V_bcs*log(2*hbar*omega_D/Delta)),
            description="BCS superconducting gap equation (weak coupling)."
        ))
        # Fermi-Dirac distribution
        E_k = symbols('E_k', real=True)
        mu_fd = symbols('mu', real=True)
        self.register(PhysicsEquation(
            name="fermi_dirac", domain=PhysicsDomain.CONDENSED_MATTER,
            latex=r"f(E)=\frac{1}{e^{(E-\mu)/k_BT}+1}",
            symbolic_expr=sp.Eq(
                Function('f')(E_k),
                1/(exp((E_k - mu_fd)/(kB*T)) + 1)),
            description="Fermi-Dirac occupation probability."
        ))

    # ----------------------------------------------------------
    # 12. NUCLEAR PHYSICS
    # ----------------------------------------------------------
    def _reg_nuclear_physics(self):
        t = self.s['t']
        lambda_d = self.s['lambda_']
        N = Function('N')(t)

        self.register(PhysicsEquation(
            name="radioactive_decay", domain=PhysicsDomain.NUCLEAR_PHYSICS,
            latex=r"\frac{dN}{dt}=-\lambda N",
            symbolic_expr=sp.Eq(diff(N, t), -lambda_d*N),
            description="First-order radioactive decay law."
        ))
        # Semi-empirical mass formula (SEMF) binding energy
        Z_n = symbols('Z', positive=True, integer=True)
        A_n = symbols('A', positive=True, integer=True)
        a_v, a_s, a_c, a_a = symbols('a_v a_s a_c a_a', positive=True)
        self.register(PhysicsEquation(
            name="semf_binding_energy", domain=PhysicsDomain.NUCLEAR_PHYSICS,
            latex=r"B=a_v A - a_s A^{2/3} - a_c\frac{Z(Z-1)}{A^{1/3}} - a_a\frac{(A-2Z)^2}{A}",
            symbolic_expr=sp.Eq(
                symbols('B'),
                a_v*A_n - a_s*A_n**Rational(2,3)
                - a_c*Z_n*(Z_n-1)/A_n**Rational(1,3)
                - a_a*(A_n - 2*Z_n)**2/A_n),
            description="Semi-empirical mass formula (Bethe-Weizsäcker) binding energy."
        ))
        # Yukawa potential
        r = self.s['r'];  g_y = symbols('g', positive=True)
        m_pi = symbols('m_pi', positive=True);  hbar = self.s['hbar']
        c    = self.s['c']
        self.register(PhysicsEquation(
            name="yukawa_potential", domain=PhysicsDomain.NUCLEAR_PHYSICS,
            latex=r"V(r)=-g^2\frac{e^{-m_\pi c r/\hbar}}{r}",
            symbolic_expr=sp.Eq(
                Function('V')(r),
                -g_y**2 * exp(-m_pi*c*r/hbar) / r),
            description="Yukawa short-range nuclear potential."
        ))

    # ----------------------------------------------------------
    # 13. ASTROPHYSICS
    # ----------------------------------------------------------
    def _reg_astrophysics(self):
        r, G, rho, P_sym = (self.s[q] for q in ['r','G','rho','P'])
        M_r = Function('M')(r)

        self.register(PhysicsEquation(
            name="hydrostatic_equilibrium", domain=PhysicsDomain.ASTROPHYSICS,
            latex=r"\frac{dP}{dr}=-\frac{GM(r)\rho}{r^2}",
            symbolic_expr=sp.Eq(diff(P_sym, r), -(G*M_r*rho)/r**2),
            description="Hydrostatic equilibrium in a star."
        ))
        # Mass continuity in a star
        self.register(PhysicsEquation(
            name="stellar_mass_continuity", domain=PhysicsDomain.ASTROPHYSICS,
            latex=r"\frac{dM}{dr}=4\pi r^2\rho",
            symbolic_expr=sp.Eq(diff(M_r, r), 4*pi*r**2*rho),
            description="Mass enclosed within radius r in a spherical star."
        ))
        # Virial theorem
        E_kin, E_grav = symbols('E_kin E_grav', real=True)
        self.register(PhysicsEquation(
            name="virial_theorem", domain=PhysicsDomain.ASTROPHYSICS,
            latex=r"2\langle E_{kin}\rangle + \langle E_{grav}\rangle = 0",
            symbolic_expr=sp.Eq(2*E_kin + E_grav, 0),
            description="Virial theorem for gravitationally bound systems."
        ))
        # Jeans mass
        M_J = symbols('M_J', positive=True)
        kB, T, m_mol = self.s['kB'], self.s['T'], self.s['m']
        self.register(PhysicsEquation(
            name="jeans_mass", domain=PhysicsDomain.ASTROPHYSICS,
            latex=r"M_J\sim\left(\frac{k_BT}{Gm}\right)^{3/2}\rho^{-1/2}",
            symbolic_expr=sp.Eq(
                M_J,
                (kB*T/(G*m_mol))**Rational(3,2) * rho**Rational(-1,2)),
            description="Jeans mass for gravitational collapse."
        ))

    # ----------------------------------------------------------
    # 14. NONLINEAR DYNAMICS
    # ----------------------------------------------------------
    def _reg_nonlinear_dynamics(self):
        t = self.s['t']
        x_n = symbols('x_n', real=True)
        r_l = symbols('r', positive=True)

        self.register(PhysicsEquation(
            name="logistic_map", domain=PhysicsDomain.NONLINEAR_DYNAMICS,
            latex=r"x_{n+1}=rx_n(1-x_n)",
            symbolic_expr=r_l*x_n*(1 - x_n),
            description="Discrete logistic map; exhibits period-doubling route to chaos."
        ))
        # Lorenz system (x component)
        sigma_l = symbols('sigma', positive=True)
        X, Y = Function('X')(t), Function('Y')(t)
        self.register(PhysicsEquation(
            name="lorenz_x", domain=PhysicsDomain.NONLINEAR_DYNAMICS,
            latex=r"\dot{X}=\sigma(Y-X)",
            symbolic_expr=sp.Eq(diff(X, t), sigma_l*(Y - X)),
            description="Lorenz system X-component (convective roll)."
        ))
        # Van der Pol oscillator
        mu_vdp = symbols('mu', positive=True)
        x_vdp  = Function('x')(t)
        self.register(PhysicsEquation(
            name="van_der_pol", domain=PhysicsDomain.NONLINEAR_DYNAMICS,
            latex=r"\ddot{x}-\mu(1-x^2)\dot{x}+x=0",
            symbolic_expr=sp.Eq(
                diff(x_vdp,t,2) - mu_vdp*(1 - x_vdp**2)*diff(x_vdp,t) + x_vdp,
                0),
            description="Van der Pol nonlinear limit-cycle oscillator."
        ))
        # Lyapunov exponent (definition)
        lam_L = symbols('lambda_L', real=True)
        delta0, delta_t = symbols('delta_0 delta_t', positive=True)
        self.register(PhysicsEquation(
            name="lyapunov_exponent", domain=PhysicsDomain.NONLINEAR_DYNAMICS,
            latex=r"\lambda_L=\lim_{t\to\infty}\frac{1}{t}\ln\frac{|\delta(t)|}{|\delta_0|}",
            symbolic_expr=sp.Eq(lam_L, log(delta_t/delta0)/symbols('t')),
            description="Lyapunov exponent measuring sensitivity to initial conditions."
        ))

    # ----------------------------------------------------------
    # 15. ACOUSTICS
    # ----------------------------------------------------------
    def _reg_acoustics(self):
        rho, c = self.s['rho'], self.s['c']
        x, t   = self.s['x'], self.s['t']
        p_ac   = Function('p')(x, t)
        Z_ac   = symbols('Z')
        v_s    = symbols('v_s', positive=True)

        self.register(PhysicsEquation(
            name="acoustic_impedance", domain=PhysicsDomain.ACOUSTICS,
            latex=r"Z=\rho v_s",
            symbolic_expr=sp.Eq(Z_ac, rho*v_s),
            description="Specific acoustic impedance."
        ))
        # Acoustic wave equation
        self.register(PhysicsEquation(
            name="acoustic_wave_equation", domain=PhysicsDomain.ACOUSTICS,
            latex=r"\frac{\partial^2 p}{\partial t^2}=v_s^2\frac{\partial^2 p}{\partial x^2}",
            symbolic_expr=sp.Eq(diff(p_ac,t,2), v_s**2*diff(p_ac,x,2)),
            description="1D acoustic pressure wave equation."
        ))
        # Doppler effect
        f_obs, f_src = symbols('f_obs f_src', positive=True)
        v_obs, v_src = symbols('v_obs v_src', real=True)
        self.register(PhysicsEquation(
            name="doppler_effect", domain=PhysicsDomain.ACOUSTICS,
            latex=r"f_{obs}=f_{src}\frac{v_s+v_{obs}}{v_s-v_{src}}",
            symbolic_expr=sp.Eq(f_obs, f_src*(v_s + v_obs)/(v_s - v_src)),
            description="Doppler frequency shift for moving source and observer."
        ))

    # ----------------------------------------------------------
    # 16. BIOPHYSICS
    # ----------------------------------------------------------
    def _reg_biophysics(self):
        x, t = self.s['x'], self.s['t']
        D = symbols('D', positive=True)
        C = Function('C')(x, t)
        J = symbols('J', real=True)

        self.register(PhysicsEquation(
            name="ficks_first_law", domain=PhysicsDomain.BIOPHYSICS,
            latex=r"J=-D\frac{\partial C}{\partial x}",
            symbolic_expr=sp.Eq(J, -D*diff(C, x)),
            description="Fick's first law of diffusion."
        ))
        # Fick's second law (diffusion equation)
        self.register(PhysicsEquation(
            name="ficks_second_law", domain=PhysicsDomain.BIOPHYSICS,
            latex=r"\frac{\partial C}{\partial t}=D\frac{\partial^2 C}{\partial x^2}",
            symbolic_expr=sp.Eq(diff(C, t), D*diff(C, x, 2)),
            description="Fick's second law: diffusion equation for concentration."
        ))
        # Michaelis-Menten kinetics
        V_max, K_m, S_sub = symbols('V_max K_m S', positive=True)
        v_rxn = symbols('v', positive=True)
        self.register(PhysicsEquation(
            name="michaelis_menten", domain=PhysicsDomain.BIOPHYSICS,
            latex=r"v=\frac{V_{max}[S]}{K_m+[S]}",
            symbolic_expr=sp.Eq(v_rxn, V_max*S_sub/(K_m + S_sub)),
            description="Michaelis-Menten enzyme kinetics."
        ))
        # Hodgkin-Huxley membrane (simplified capacitive term)
        C_m = symbols('C_m', positive=True)
        V_m = Function('V_m')(t)
        I_ion = symbols('I_ion', real=True)
        self.register(PhysicsEquation(
            name="hodgkin_huxley_membrane", domain=PhysicsDomain.BIOPHYSICS,
            latex=r"C_m\frac{dV_m}{dt}=I_{ion}",
            symbolic_expr=sp.Eq(C_m*diff(V_m, t), I_ion),
            description="Hodgkin-Huxley membrane capacitance equation."
        ))

    # ----------------------------------------------------------
    # 17. INFORMATION THEORY
    # ----------------------------------------------------------
    def _reg_information_theory(self):
        p_i = symbols('p_i', positive=True)
        H   = symbols('H', real=True)
        C_cap = symbols('C', positive=True)
        B_bw  = symbols('B', positive=True)
        SNR   = symbols('SNR', positive=True)
        kB    = self.s['kB']
        T     = self.s['T']

        self.register(PhysicsEquation(
            name="shannon_entropy", domain=PhysicsDomain.INFORMATION_THEORY,
            latex=r"H=-\sum_i p_i\log_2 p_i",
            symbolic_expr=sp.Eq(H, -p_i*log(p_i, 2)),
            description="Shannon information entropy (single-term symbolic form)."
        ))
        # Shannon channel capacity
        self.register(PhysicsEquation(
            name="shannon_capacity", domain=PhysicsDomain.INFORMATION_THEORY,
            latex=r"C=B\log_2(1+\text{SNR})",
            symbolic_expr=sp.Eq(C_cap, B_bw*log(1 + SNR, 2)),
            description="Shannon-Hartley channel capacity theorem."
        ))
        # Landauer's principle
        E_land = symbols('E_land', positive=True)
        self.register(PhysicsEquation(
            name="landauer_principle", domain=PhysicsDomain.INFORMATION_THEORY,
            latex=r"E\geq k_BT\ln 2",
            symbolic_expr=sp.Ge(E_land, kB*T*log(2)),
            description="Landauer's principle: minimum energy cost of erasing one bit."
        ))
        # Kullback-Leibler divergence
        q_i = symbols('q_i', positive=True)
        D_KL = symbols('D_KL', positive=True)
        self.register(PhysicsEquation(
            name="kl_divergence", domain=PhysicsDomain.INFORMATION_THEORY,
            latex=r"D_{KL}(P\|Q)=\sum_i p_i\log\frac{p_i}{q_i}",
            symbolic_expr=sp.Eq(D_KL, p_i*log(p_i/q_i)),
            description="Kullback-Leibler divergence (single-term symbolic form)."
        ))

    # ----------------------------------------------------------
    # 18. COSMOLOGY
    # ----------------------------------------------------------
    def _reg_cosmology(self):
        t = self.s['t']
        G = self.s['G'];  c = self.s['c']
        a = Function('a')(t)
        H_param = symbols('H', positive=True)
        rho_c   = symbols('rho', positive=True)
        k_curv  = symbols('k', real=True)
        Lambda  = symbols('Lambda')

        self.register(PhysicsEquation(
            name="hubble_parameter", domain=PhysicsDomain.COSMOLOGY,
            latex=r"H=\frac{\dot{a}}{a}",
            symbolic_expr=sp.Eq(H_param, diff(a,t)/a),
            description="Hubble parameter from the cosmic scale factor."
        ))
        # Friedmann equation (first)
        self.register(PhysicsEquation(
            name="friedmann_first", domain=PhysicsDomain.COSMOLOGY,
            latex=r"\left(\frac{\dot{a}}{a}\right)^2=\frac{8\pi G\rho}{3}-\frac{kc^2}{a^2}+\frac{\Lambda c^2}{3}",
            symbolic_expr=sp.Eq(
                (diff(a,t)/a)**2,
                Rational(8,3)*pi*G*rho_c - k_curv*c**2/a**2 + Lambda*c**2/3),
            description="First Friedmann equation governing cosmic expansion."
        ))
        # Dark energy equation of state
        w_de = symbols('w', real=True)
        P_de = symbols('P_de', real=True)
        self.register(PhysicsEquation(
            name="dark_energy_eos", domain=PhysicsDomain.COSMOLOGY,
            latex=r"P=w\rho c^2",
            symbolic_expr=sp.Eq(P_de, w_de*rho_c*c**2),
            description="Dark energy equation of state (w = -1 for cosmological constant)."
        ))
        # Redshift-scale factor relation
        z_rs = symbols('z', positive=True)
        a_0  = symbols('a_0', positive=True)
        self.register(PhysicsEquation(
            name="redshift_scale_factor", domain=PhysicsDomain.COSMOLOGY,
            latex=r"1+z=\frac{a_0}{a}",
            symbolic_expr=sp.Eq(1 + z_rs, a_0/a),
            description="Cosmological redshift as a function of scale factor."
        ))

    # ----------------------------------------------------------
    # 19. HIGH ENERGY / STRING THEORY
    # ----------------------------------------------------------
    def _reg_high_energy_string(self):
        x, t = self.s['x'], self.s['t']
        m     = self.s['m']
        hbar  = self.s['hbar']
        c     = self.s['c']
        phi_f = Function('phi')(x, t)

        self.register(PhysicsEquation(
            name="klein_gordon", domain=PhysicsDomain.HIGH_ENERGY_STRING,
            latex=r"\Box\phi+m^2\phi=0",
            symbolic_expr=sp.Eq(
                diff(phi_f,t,2) - c**2*diff(phi_f,x,2) + (m*c**2/hbar)**2*phi_f,
                0),
            description="Klein-Gordon relativistic scalar field equation."
        ))
        # Nambu-Goto action (1+1D worldsheet)
        tau_ng, sigma_ng = symbols('tau sigma', real=True)
        T_str = symbols('T_s', positive=True)
        gamma_ng = symbols('gamma', positive=True)
        self.register(PhysicsEquation(
            name="nambu_goto_action", domain=PhysicsDomain.HIGH_ENERGY_STRING,
            latex=r"S=-T_s\int d\tau\,d\sigma\sqrt{-\gamma}",
            symbolic_expr=sp.Eq(
                symbols('S_NG'),
                -T_str * sp.Integral(sqrt(gamma_ng), (tau_ng, -oo, oo))),
            description="Nambu-Goto string action (area of worldsheet)."
        ))
        # Dirac equation (1+1D, matrix-free scalar proxy)
        psi_d = Function('psi')(x, t)
        self.register(PhysicsEquation(
            name="dirac_1d", domain=PhysicsDomain.HIGH_ENERGY_STRING,
            latex=r"(i\hbar\gamma^\mu\partial_\mu - mc)\psi=0",
            symbolic_expr=sp.Eq(
                I*hbar*(diff(psi_d,t)/c + diff(psi_d,x)) - m*c*psi_d,
                0),
            description="1D scalar proxy for the Dirac relativistic wave equation."
        ))
        # Renormalization group beta function (symbolic)
        g_rg = symbols('g', real=True)
        mu_rg = symbols('mu', positive=True)
        beta_fn = symbols('beta')
        self.register(PhysicsEquation(
            name="rg_beta_function", domain=PhysicsDomain.HIGH_ENERGY_STRING,
            latex=r"\beta(g)=\mu\frac{\partial g}{\partial\mu}",
            symbolic_expr=sp.Eq(beta_fn, mu_rg*diff(Function('g')(mu_rg), mu_rg)),
            description="Renormalization group beta function for coupling constant running."
        ))


    # ----------------------------------------------------------
    # 20. POPULATION DYNAMICS
    # ----------------------------------------------------------
    def _reg_population_dynamics(self):
        t = self.s['t']
        N = Function('N')(t)
        r_pop = symbols('r', real=True)      # intrinsic growth rate
        K_cap = symbols('K', positive=True)  # carrying capacity
        x_var, y_var = self.s['x'], self.s['y']

        # Logistic growth (continuous)
        self.register(PhysicsEquation(
            name="logistic_growth", domain=PhysicsDomain.POPULATION_DYNAMICS,
            latex=r"\frac{dN}{dt}=rN\left(1-\frac{N}{K}\right)",
            symbolic_expr=sp.Eq(diff(N, t), r_pop * N * (1 - N/K_cap)),
            description="Continuous logistic population growth with carrying capacity K."
        ))

        # Lotka-Volterra predator-prey (prey equation)
        alpha_lv = symbols('alpha', positive=True)  # prey growth rate
        beta_lv  = symbols('beta',  positive=True)  # predation rate
        X_lv = Function('X')(t)  # prey
        Y_lv = Function('Y')(t)  # predator
        self.register(PhysicsEquation(
            name="lotka_volterra_prey", domain=PhysicsDomain.POPULATION_DYNAMICS,
            latex=r"\frac{dX}{dt}=\alpha X - \beta X Y",
            symbolic_expr=sp.Eq(diff(X_lv, t), alpha_lv*X_lv - beta_lv*X_lv*Y_lv),
            description="Lotka-Volterra prey equation: growth minus predation."
        ))
        # Lotka-Volterra predator equation
        delta_lv = symbols('delta', positive=True)  # predator growth from prey
        gamma_lv = symbols('gamma', positive=True)  # predator death rate
        self.register(PhysicsEquation(
            name="lotka_volterra_predator", domain=PhysicsDomain.POPULATION_DYNAMICS,
            latex=r"\frac{dY}{dt}=\delta X Y - \gamma Y",
            symbolic_expr=sp.Eq(diff(Y_lv, t), delta_lv*X_lv*Y_lv - gamma_lv*Y_lv),
            description="Lotka-Volterra predator equation: growth from prey minus death."
        ))
        # Replicator equation (evolutionary game theory)
        f_i = symbols('f_i', real=True)   # fitness of strategy i
        f_bar = symbols('bar_f', real=True)  # mean population fitness
        x_i = Function('x_i')(t)            # frequency of strategy i
        self.register(PhysicsEquation(
            name="replicator_equation", domain=PhysicsDomain.POPULATION_DYNAMICS,
            latex=r"\dot{x}_i = x_i(f_i - \bar{f})",
            symbolic_expr=sp.Eq(diff(x_i, t), x_i*(f_i - f_bar)),
            description="Replicator equation: evolutionary selection dynamics."
        ))
        # Wright-Fisher genetic drift (Fokker-Planck form)
        p_wf = symbols('p', real=True)   # allele frequency
        N_e  = symbols('N_e', positive=True)  # effective population size
        self.register(PhysicsEquation(
            name="wright_fisher_drift", domain=PhysicsDomain.POPULATION_DYNAMICS,
            latex=r"\frac{\partial \phi}{\partial t}=\frac{1}{2N_e}\frac{\partial^2}{\partial p^2}[p(1-p)\phi]",
            symbolic_expr=sp.Eq(
                diff(Function('phi')(p_wf, t), t),
                Rational(1, 2) / N_e * diff(p_wf*(1-p_wf)*Function('phi')(p_wf, t), p_wf, 2)),
            description="Wright-Fisher diffusion: genetic drift as a Fokker-Planck equation."
        ))

    # ----------------------------------------------------------
    # 21. NEUROSCIENCE
    # ----------------------------------------------------------
    def _reg_neuroscience(self):
        t = self.s['t']
        x = self.s['x']

        # FitzHugh-Nagumo (v equation)
        v_fn = Function('v')(t)   # membrane potential variable
        w_fn = Function('w')(t)   # recovery variable
        I_ext = symbols('I_ext', real=True)
        a_fn, b_fn, tau_fn = symbols('a b tau', real=True)
        self.register(PhysicsEquation(
            name="fitzhugh_nagumo_v", domain=PhysicsDomain.NEUROSCIENCE,
            latex=r"\dot{v}=v-\frac{v^3}{3}-w+I_{ext}",
            symbolic_expr=sp.Eq(
                diff(v_fn, t),
                v_fn - v_fn**3/3 - w_fn + I_ext),
            description="FitzHugh-Nagumo fast voltage variable (reduced Hodgkin-Huxley)."
        ))
        # FitzHugh-Nagumo (w recovery equation)
        self.register(PhysicsEquation(
            name="fitzhugh_nagumo_w", domain=PhysicsDomain.NEUROSCIENCE,
            latex=r"\dot{w}=\frac{1}{\tau}(v+a-bw)",
            symbolic_expr=sp.Eq(
                diff(w_fn, t),
                (1/tau_fn)*(v_fn + a_fn - b_fn*w_fn)),
            description="FitzHugh-Nagumo slow recovery variable."
        ))
        # Cable equation (dendrite)
        lambda_c = symbols('lambda_c', positive=True)  # space constant
        tau_m    = symbols('tau_m',    positive=True)  # membrane time constant
        V_cable  = Function('V')(x, t)
        self.register(PhysicsEquation(
            name="cable_equation", domain=PhysicsDomain.NEUROSCIENCE,
            latex=r"\tau_m\frac{\partial V}{\partial t}=\lambda_c^2\frac{\partial^2 V}{\partial x^2}-V",
            symbolic_expr=sp.Eq(
                tau_m * diff(V_cable, t),
                lambda_c**2 * diff(V_cable, x, 2) - V_cable),
            description="Cable equation for passive voltage propagation in a dendrite."
        ))
        # Wilson-Cowan neural population (excitatory)
        E_wc = Function('E')(t)   # excitatory activity
        I_wc = Function('I')(t)   # inhibitory activity
        tau_E = symbols('tau_E', positive=True)
        c_EE, c_EI = symbols('c_EE c_EI', real=True)
        P_ext = symbols('P', real=True)
        S_fn  = Function('S')  # sigmoid transfer function
        self.register(PhysicsEquation(
            name="wilson_cowan_E", domain=PhysicsDomain.NEUROSCIENCE,
            latex=r"\tau_E\dot{E}=-E+S(c_{EE}E - c_{EI}I + P)",
            symbolic_expr=sp.Eq(
                tau_E * diff(E_wc, t),
                -E_wc + S_fn(c_EE*E_wc - c_EI*I_wc + P_ext)),
            description="Wilson-Cowan excitatory neural population mean-field equation."
        ))

    # ----------------------------------------------------------
    # 22. MOLECULAR BIOLOGY
    # ----------------------------------------------------------
    def _reg_molecular_biology(self):
        # Hill equation (cooperative binding)
        theta_h = symbols('theta', positive=True)  # fractional occupancy
        L_conc  = symbols('L',  positive=True)     # ligand concentration
        K_d     = symbols('K_d', positive=True)    # dissociation constant
        n_h     = symbols('n',   positive=True)    # Hill coefficient
        self.register(PhysicsEquation(
            name="hill_equation", domain=PhysicsDomain.MOLECULAR_BIOLOGY,
            latex=r"\theta=\frac{[L]^n}{K_d^n+[L]^n}",
            symbolic_expr=sp.Eq(theta_h, L_conc**n_h / (K_d**n_h + L_conc**n_h)),
            description="Hill equation for cooperative ligand binding (n=1 → Michaelis-Menten)."
        ))
        # Arrhenius rate equation
        k_rate = symbols('k_rate', positive=True)  # rate constant
        A_pre  = symbols('A',  positive=True)      # pre-exponential factor
        E_a    = symbols('E_a', positive=True)     # activation energy
        R_gas  = symbols('R',   positive=True)     # gas constant
        T      = self.s['T']
        self.register(PhysicsEquation(
            name="arrhenius", domain=PhysicsDomain.MOLECULAR_BIOLOGY,
            latex=r"k=A e^{-E_a/RT}",
            symbolic_expr=sp.Eq(k_rate, A_pre * exp(-E_a / (R_gas * T))),
            description="Arrhenius equation: temperature dependence of reaction rate."
        ))
        # Turing reaction-diffusion (activator u)
        x, t = self.s['x'], self.s['t']
        u_rd = Function('u')(x, t)   # activator
        v_rd = Function('v')(x, t)   # inhibitor
        D_u  = symbols('D_u', positive=True)
        f_rd = Function('f')(u_rd, v_rd)  # reaction term
        self.register(PhysicsEquation(
            name="turing_activator", domain=PhysicsDomain.MOLECULAR_BIOLOGY,
            latex=r"\frac{\partial u}{\partial t}=D_u\nabla^2 u + f(u,v)",
            symbolic_expr=sp.Eq(
                diff(u_rd, t),
                D_u * diff(u_rd, x, 2) + f_rd),
            description="Turing reaction-diffusion activator equation for pattern formation."
        ))
        # Turing reaction-diffusion (inhibitor v)
        D_v  = symbols('D_v', positive=True)
        g_rd = Function('g')(u_rd, v_rd)  # reaction term
        self.register(PhysicsEquation(
            name="turing_inhibitor", domain=PhysicsDomain.MOLECULAR_BIOLOGY,
            latex=r"\frac{\partial v}{\partial t}=D_v\nabla^2 v + g(u,v)",
            symbolic_expr=sp.Eq(
                diff(v_rd, t),
                D_v * diff(v_rd, x, 2) + g_rd),
            description="Turing reaction-diffusion inhibitor equation for pattern formation."
        ))

    # ----------------------------------------------------------
    # 23. ECOLOGY & SYSTEMS BIOLOGY
    # ----------------------------------------------------------
    def _reg_ecology_systems(self):
        t = self.s['t']
        N = Function('N')(t)
        r_pop = symbols('r', real=True)
        K_cap = symbols('K', positive=True)

        # Fisher-KPP traveling wave
        x = self.s['x']
        u_kpp = Function('u')(x, t)
        D_kpp = symbols('D', positive=True)
        self.register(PhysicsEquation(
            name="fisher_kpp", domain=PhysicsDomain.ECOLOGY_SYSTEMS,
            latex=r"\frac{\partial u}{\partial t}=D\frac{\partial^2 u}{\partial x^2}+ru(1-u)",
            symbolic_expr=sp.Eq(
                diff(u_kpp, t),
                D_kpp * diff(u_kpp, x, 2) + r_pop * u_kpp * (1 - u_kpp)),
            description="Fisher-KPP equation: reaction-diffusion with logistic growth."
        ))
        # SIR epidemic model (S equation)
        S_sir = Function('S')(t)
        I_sir = Function('I')(t)
        R_sir = Function('R')(t)
        beta_sir  = symbols('beta_sir',  positive=True)  # transmission rate
        gamma_sir = symbols('gamma_sir', positive=True)  # recovery rate
        self.register(PhysicsEquation(
            name="sir_susceptible", domain=PhysicsDomain.ECOLOGY_SYSTEMS,
            latex=r"\frac{dS}{dt}=-\beta SI",
            symbolic_expr=sp.Eq(diff(S_sir, t), -beta_sir * S_sir * I_sir),
            description="SIR model: rate of change of susceptible population."
        ))
        # SIR epidemic model (I equation)
        self.register(PhysicsEquation(
            name="sir_infected", domain=PhysicsDomain.ECOLOGY_SYSTEMS,
            latex=r"\frac{dI}{dt}=\beta SI - \gamma I",
            symbolic_expr=sp.Eq(
                diff(I_sir, t),
                beta_sir * S_sir * I_sir - gamma_sir * I_sir),
            description="SIR model: rate of change of infected population."
        ))
        # Allometric scaling (Kleiber's law)
        M_body = symbols('M', positive=True)  # body mass
        B_met  = symbols('B', positive=True)  # metabolic rate
        B_0    = symbols('B_0', positive=True)
        self.register(PhysicsEquation(
            name="allometric_scaling", domain=PhysicsDomain.ECOLOGY_SYSTEMS,
            latex=r"B=B_0 M^{3/4}",
            symbolic_expr=sp.Eq(B_met, B_0 * M_body**Rational(3, 4)),
            description="Kleiber's allometric scaling law: metabolic rate ∝ M^(3/4)."
        ))


# ============================================================
# SECTION 3: THE "PROPELLER" TRANSFORM (MIT Paper Style)
# ============================================================

class PropellerTransform:
    """
    Implements the creative mapping from the MIT droplet paper:
    Classical Diffusion + Memory Term = Quantum-like Behavior.
    """

    def __init__(self, registry: EquationRegistry):
        self.registry = registry

    def apply_fokker_planck_morph(self, classical_eq_name: str) -> sp.Basic:
        """
        Take a classical deterministic equation and add the stochastic
        "propeller" term that mimics quantum potential.
        """
        eq = self.registry.get(classical_eq_name)
        if not eq:
            raise ValueError(f"Equation '{classical_eq_name}' not found")

        t, x   = self.registry.s['t'], self.registry.s['x']
        hbar, m = self.registry.s['hbar'], self.registry.s['m']
        D = symbols('D', positive=True)
        P = Function('P')(x, t)
        v = Function('v')(x)

        sqrt_P = sqrt(P)
        Q = -(hbar**2/(2*m)) * (1/sqrt_P) * diff(sqrt_P, x, 2)

        morphed = sp.Eq(
            diff(P, t),
            -diff(v*P, x) + D*diff(P, x, 2) + Q)
        return morphed


# ============================================================
# SECTION 4: MAIN PLAYGROUND INTERFACE
# ============================================================

class PhysicsPlayground:
    """Main interface for the geometric-to-binary experimental repo."""

    def __init__(self):
        self.registry  = EquationRegistry()
        self.propeller = PropellerTransform(self.registry)
        self.sp        = sp

    def info(self, eq_name: str) -> str:
        eq = self.registry.get(eq_name)
        if not eq:
            return f"Equation '{eq_name}' not found."
        return (f"\n  Name:        {eq.name}"
                f"\n  Domain:      {eq.domain.value}"
                f"\n  Description: {eq.description}"
                f"\n  LaTeX:       {eq.latex}"
                f"\n  Expression:  {eq.symbolic_expr}")

    def creative_mix(self, classical_eq: str,
                     operation: str = 'morph') -> sp.Basic:
        if operation == 'morph':
            return self.propeller.apply_fokker_planck_morph(classical_eq)
        elif operation == 'diffuse':
            eq = self.registry.get(classical_eq)
            if eq:
                morphed = MorphedEquation(
                    source=eq, target_domain=PhysicsDomain.QUANTUM)
                return morphed.apply_diffusion_morphism()
        raise ValueError(f"Unknown creative operation: {operation}")

    def morph(self, source: str, target: str) -> dict:
        """
        Find the shortest morphism path from source equation to target equation
        and return a dict with the path, edge descriptions, and total weight.

        Example
        -------
        >>> pg = PhysicsPlayground()
        >>> result = pg.morph('harmonic_oscillator', 'klein_gordon')
        >>> print(result['path'])
        >>> print(result['total_weight'])
        """
        import graph as _graph
        import networkx as _nx
        eq_graph = _graph.build_morphism_graph(self.registry)
        try:
            path = eq_graph.path(source, target)
        except (_nx.NetworkXNoPath, _nx.NodeNotFound) as exc:
            return {"path": [], "steps": [], "total_weight": float("inf"),
                    "error": str(exc)}
        steps = []
        total_weight = 0.0
        for i in range(len(path) - 1):
            src, tgt = path[i], path[i + 1]
            edge_data    = eq_graph.G.get_edge_data(src, tgt) or {}
            morphism_key = edge_data.get("morphism", "unknown")
            description  = edge_data.get("description", "")
            weight       = edge_data.get("weight", 0.0)
            total_weight += weight
            steps.append({
                "from":        src,
                "to":          tgt,
                "morphism":    morphism_key,
                "description": description,
                "weight":      round(weight, 4),
            })
        return {
            "path":         path,
            "steps":        steps,
            "total_weight": round(total_weight, 4),
        }

    def run_example(self):
        print("=" * 65)
        print("  PHYSICS PLAYGROUND: Geometric → Binary")
        print("=" * 65)

        all_eqs = self.registry.list_all()
        print(f"\n[1] Registry: {len(all_eqs)} equations across "
              f"{len(set(self.registry.get(n).domain for n in all_eqs))} domains\n")
        for name in all_eqs:
            eq = self.registry.get(name)
            print(f"    {name:<35} [{eq.domain.value}]")

        print("\n[2] Propeller morph: harmonic_oscillator → quantum-diffusion form")
        morphed = self.creative_mix("harmonic_oscillator", operation="morph")
        print(f"    {sp.latex(morphed)}")

        print("\n[3] Cross-domain mix: continuity_1d + schrodinger_free (add)")
        mixed = self.registry.mix("continuity_1d", "schrodinger_free", "add")
        print(f"    {sp.latex(mixed)}")

        print("\n" + "=" * 65)
        print("  Playground ready.  playground.info('<equation_name>')")
        print("=" * 65)


# ============================================================
# SECTION 5: ENTRY POINT
# ============================================================

if __name__ == "__main__":
    playground = PhysicsPlayground()
    playground.run_example()
