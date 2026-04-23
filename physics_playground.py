"""
physics_playground.py
A symbolic sandbox for mixing, matching, and morphing physics equations.
Built on SymPy for the "geometric to binary" style experimental repo.
"""

import sympy as sp
from sympy import symbols, Function, diff, integrate, exp, sin, cos, sqrt, log
from dataclasses import dataclass, field
from typing import Callable, Dict, List, Optional, Any
from enum import Enum

# ============================================================
# SECTION 1: CORE SYMBOLIC ENGINE
# ============================================================

class PhysicsDomain(Enum):
    """Label equations by their native domain for creative mixing."""
    CLASSICAL_MECHANICS = "classical_mechanics"
    ELECTROMAGNETISM = "electromagnetism"
    QUANTUM = "quantum"
    THERMODYNAMICS = "thermodynamics"
    FLUID_DYNAMICS = "fluid_dynamics"
    STATISTICAL = "statistical"
    RELATIVITY = "relativity"
    # --- 12 New Domains ---
    GENERAL_RELATIVITY = "general_relativity"
    PLASMA_PHYSICS = "plasma_physics"
    OPTICS = "optics"
    CONDENSED_MATTER = "condensed_matter"
    NUCLEAR_PHYSICS = "nuclear_physics"
    ASTROPHYSICS = "astrophysics"
    NONLINEAR_DYNAMICS = "nonlinear_dynamics"
    ACOUSTICS = "acoustics"
    BIOPHYSICS = "biophysics"
    INFORMATION_THEORY = "information_theory"
    COSMOLOGY = "cosmology"
    HIGH_ENERGY_STRING = "high_energy_string"
    CUSTOM = "custom"

@dataclass
class PhysicsEquation:
    """Container for a single physics equation with metadata."""
    name: str
    latex: str
    symbolic_expr: sp.Expr
    domain: PhysicsDomain
    parameters: Dict[str, sp.Symbol] = field(default_factory=dict)
    constraints: List[sp.core.relational.Relational] = field(default_factory=list)
    description: str = ""
    
    def substitute(self, subs_dict: Dict) -> 'PhysicsEquation':
        """Return a new equation with parameters substituted."""
        new_expr = self.symbolic_expr.subs(subs_dict)
        return PhysicsEquation(
            name=f"{self.name}_substituted",
            latex=sp.latex(new_expr),
            symbolic_expr=new_expr,
            domain=self.domain,
            parameters={k: v for k, v in self.parameters.items() if k not in subs_dict}
        )
    
    def moralize(self, target_domain: PhysicsDomain) -> 'MorphedEquation':
        """Creative step: treat this classical equation as if it were quantum/statistical."""
        return MorphedEquation(source=self, target_domain=target_domain)

@dataclass
class MorphedEquation:
    """Result of taking an equation from one domain and applying the
    mathematical "propeller" treatment from another domain."""
    source: PhysicsEquation
    target_domain: PhysicsDomain
    morphed_expr: Optional[sp.Expr] = None
    morph_rules_applied: List[str] = field(default_factory=list)
    
    def apply_diffusion_morphism(self, noise_term: sp.Symbol = None) -> sp.Expr:
        """
        The MIT droplet paper trick: 
        Classical deterministic eq -> Add Fokker-Planck / stochastic term.
        """
        if noise_term is None:
            noise_term = symbols('D')  # Diffusion coefficient
            
        x, t = symbols('x t')
        P = Function('P')(x, t)
        
        classical_part = self.source.symbolic_expr
        diffusion_part = noise_term * diff(P, x, 2)
        
        self.morphed_expr = classical_part + diffusion_part
        self.morph_rules_applied.append("added_diffusion_term")
        return self.morphed_expr

# ============================================================
# SECTION 2: EQUATION REGISTRY (The Mixing Palette)
# ============================================================

class EquationRegistry:
    """Central database of physics equations ready for creative abuse."""
    
    def __init__(self):
        self._equations: Dict[str, PhysicsEquation] = {}
        self._initialize_default_symbols()
        self._register_builtins()
    
    def _initialize_default_symbols(self):
        """Common symbols across domains."""
        self.syms = {
            't': symbols('t', real=True),           # time
            'x': symbols('x', real=True),           # position
            'y': symbols('y', real=True),
            'z': symbols('z', real=True),
            'm': symbols('m', positive=True),       # mass
            'v': symbols('v', real=True),           # velocity
            'E': symbols('E', real=True),           # energy
            'p': symbols('p', real=True),           # momentum
            'hbar': symbols('hbar', positive=True), # reduced Planck
            'k': symbols('k', real=True),           # wave number / spring constant
            'T': symbols('T', positive=True),       # temperature
            'S': symbols('S', real=True),           # entropy / action
            'c': symbols('c', positive=True),       # speed of light
            'G': symbols('G', positive=True),       # gravitational constant
            'rho': symbols('rho', real=True),       # density
            'P': symbols('P', real=True),           # pressure
        }
    
    def _register_builtins(self):
        """Populate with standard equations from multiple domains."""
        s = self.syms
        t, x, y, z, m, v, E, p, hbar, k, T, S, c, G, rho, P_sym = s.values()
        
        # --------------------------------------------------
        # ORIGINAL DOMAINS
        # --------------------------------------------------
        
        # CLASSICAL MECHANICS
        F = Function('F')(t)
        a = Function('a')(t)
        self.register(PhysicsEquation(
            name="newton_2", latex=r"F = m a",
            symbolic_expr=sp.Eq(F, m * a), domain=PhysicsDomain.CLASSICAL_MECHANICS,
            parameters={'F': F, 'm': m, 'a': a}
        ))
        
        self.register(PhysicsEquation(
            name="harmonic_oscillator", latex=r"m \ddot{x} = -k x",
            symbolic_expr=sp.Eq(m * diff(x, t, 2), -k * x), domain=PhysicsDomain.CLASSICAL_MECHANICS,
            parameters={'m': m, 'k': k, 'x(t)': sp.Function('x')(t)}
        ))
        
        # QUANTUM MECHANICS
        psi = Function('psi')(x, t)
        self.register(PhysicsEquation(
            name="schrodinger_free", latex=r"i\hbar \frac{\partial \psi}{\partial t} = -\frac{\hbar^2}{2m} \frac{\partial^2 \psi}{\partial x^2}",
            symbolic_expr=sp.Eq(sp.I * hbar * diff(psi, t), -(hbar**2)/(2*m) * diff(psi, x, 2)),
            domain=PhysicsDomain.QUANTUM, parameters={'psi': psi, 'hbar': hbar, 'm': m}
        ))
        
        # STATISTICAL
        self.register(PhysicsEquation(
            name="boltzmann_factor", latex=r"P(E) \propto e^{-E/k_B T}",
            symbolic_expr=exp(-E / (k * T)), domain=PhysicsDomain.STATISTICAL,
            parameters={'E': E, 'k_B': k, 'T': T}
        ))
        
        # FLUID DYNAMICS
        u = Function('u')(x, t)
        self.register(PhysicsEquation(
            name="continuity_1d", latex=r"\frac{\partial \rho}{\partial t} + \frac{\partial (\rho u)}{\partial x} = 0",
            symbolic_expr=sp.Eq(diff(rho, t) + diff(rho * u, x), 0), domain=PhysicsDomain.FLUID_DYNAMICS,
            parameters={'rho': rho, 'u': u}
        ))
        
        # ELECTROMAGNETISM
        phi = Function('phi')(x, t)
        self.register(PhysicsEquation(
            name="wave_equation_1d", latex=r"\frac{\partial^2 \phi}{\partial t^2} = c^2 \frac{\partial^2 \phi}{\partial x^2}",
            symbolic_expr=sp.Eq(diff(phi, t, 2), c**2 * diff(phi, x, 2)), domain=PhysicsDomain.ELECTROMAGNETISM,
            parameters={'phi': phi, 'c': c}
        ))

        # --------------------------------------------------
        # NEW DOMAIN 1: GENERAL RELATIVITY
        # --------------------------------------------------
        R_uv = symbols('R_mu_nu') # Ricci tensor component
        R = symbols('R') # Ricci scalar
        g_uv = symbols('g_mu_nu') # Metric tensor
        T_uv = symbols('T_mu_nu') # Stress-energy tensor
        Lambda = symbols('Lambda') # Cosmological constant
        self.register(PhysicsEquation(
            name="einstein_field_equation", latex=r"R_{\mu\nu} - \frac{1}{2}R g_{\mu\nu} + \Lambda g_{\mu\nu} = \frac{8\pi G}{c^4} T_{\mu\nu}",
            symbolic_expr=sp.Eq(R_uv - (1/2)*R*g_uv + Lambda*g_uv, (8*sp.pi*G / c**4)*T_uv),
            domain=PhysicsDomain.GENERAL_RELATIVITY, parameters={'R_uv': R_uv, 'R': R, 'g_uv': g_uv, 'T_uv': T_uv, 'Lambda': Lambda, 'G': G, 'c': c}
        ))
        
        # --------------------------------------------------
        # NEW DOMAIN 2: PLASMA PHYSICS
        # --------------------------------------------------
        n_e = symbols('n_e') # electron density
        e = symbols('e') # elementary charge
        epsilon_0 = symbols('epsilon_0') # vacuum permittivity
        omega_p = symbols('omega_p') # plasma frequency
        self.register(PhysicsEquation(
            name="plasma_frequency", latex=r"\omega_p = \sqrt{\frac{n_e e^2}{m_e \epsilon_0}}",
            symbolic_expr=sp.Eq(omega_p, sqrt((n_e * e**2)/(m * epsilon_0))),
            domain=PhysicsDomain.PLASMA_PHYSICS, parameters={'n_e': n_e, 'e': e, 'm_e': m, 'epsilon_0': epsilon_0}
        ))

        # --------------------------------------------------
        # NEW DOMAIN 3: OPTICS
        # --------------------------------------------------
        n1, n2, theta1, theta2 = symbols('n_1 n_2 theta_1 theta_2')
        self.register(PhysicsEquation(
            name="snells_law", latex=r"n_1 \sin(\theta_1) = n_2 \sin(\theta_2)",
            symbolic_expr=sp.Eq(n1 * sin(theta1), n2 * sin(theta2)),
            domain=PhysicsDomain.OPTICS, parameters={'n1': n1, 'n2': n2, 'theta1': theta1, 'theta2': theta2}
        ))

        # --------------------------------------------------
        # NEW DOMAIN 4: CONDENSED MATTER
        # --------------------------------------------------
        sigma = symbols('sigma') # conductivity
        tau = symbols('tau') # scattering time
        self.register(PhysicsEquation(
            name="drude_conductivity", latex=r"\sigma = \frac{n e^2 \tau}{m}",
            symbolic_expr=sp.Eq(sigma, (n_e * e**2 * tau)/m),
            domain=PhysicsDomain.CONDENSED_MATTER, parameters={'sigma': sigma, 'n': n_e, 'e': e, 'tau': tau, 'm': m}
        ))

        # --------------------------------------------------
        # NEW DOMAIN 5: NUCLEAR PHYSICS
        # --------------------------------------------------
        N = Function('N')(t)
        lambda_decay = symbols('lambda')
        self.register(PhysicsEquation(
            name="radioactive_decay", latex=r"\frac{dN}{dt} = -\lambda N",
            symbolic_expr=sp.Eq(diff(N, t), -lambda_decay * N),
            domain=PhysicsDomain.NUCLEAR_PHYSICS, parameters={'N': N, 'lambda': lambda_decay}
        ))

        # --------------------------------------------------
        # NEW DOMAIN 6: ASTROPHYSICS
        # --------------------------------------------------
        r = symbols('r')
        M_r = Function('M')(r)
        self.register(PhysicsEquation(
            name="hydrostatic_equilibrium", latex=r"\frac{dP}{dr} = -\frac{G M(r) \rho}{r^2}",
            symbolic_expr=sp.Eq(diff(P_sym, r), -(G * M_r * rho) / r**2),
            domain=PhysicsDomain.ASTROPHYSICS, parameters={'P': P_sym, 'G': G, 'M_r': M_r, 'rho': rho, 'r': r}
        ))

        # --------------------------------------------------
        # NEW DOMAIN 7: NONLINEAR DYNAMICS
        # --------------------------------------------------
        x_n = symbols('x_n')
        r_log = symbols('r')
        self.register(PhysicsEquation(
            name="logistic_map", latex=r"x_{n+1} = r x_n (1 - x_n)",
            symbolic_expr=r_log * x_n * (1 - x_n),
            domain=PhysicsDomain.NONLINEAR_DYNAMICS, parameters={'r': r_log, 'x_n': x_n}
        ))

        # --------------------------------------------------
        # NEW DOMAIN 8: ACOUSTICS
        # --------------------------------------------------
        Z = symbols('Z')
        v_sound = symbols('v_s')
        self.register(PhysicsEquation(
            name="acoustic_impedance", latex=r"Z = \rho v_s",
            symbolic_expr=sp.Eq(Z, rho * v_sound),
            domain=PhysicsDomain.ACOUSTICS, parameters={'Z': Z, 'rho': rho, 'v_s': v_sound}
        ))

        # --------------------------------------------------
        # NEW DOMAIN 9: BIOPHYSICS
        # --------------------------------------------------
        J = symbols('J') # diffusion flux
        D = symbols('D') # diffusion coefficient
        C = Function('C')(x) # concentration
        self.register(PhysicsEquation(
            name="ficks_first_law", latex=r"J = -D \frac{\partial C}{\partial x}",
            symbolic_expr=sp.Eq(J, -D * diff(C, x)),
            domain=PhysicsDomain.BIOPHYSICS, parameters={'J': J, 'D': D, 'C': C, 'x': x}
        ))

        # --------------------------------------------------
        # NEW DOMAIN 10: INFORMATION THEORY
        # --------------------------------------------------
        p_i = symbols('p_i')
        H = symbols('H')
        self.register(PhysicsEquation(
            name="shannon_entropy", latex=r"H = -\sum p_i \log_2(p_i)",
            symbolic_expr=sp.Eq(H, -p_i * log(p_i, 2)), # simplified symbolic representation
            domain=PhysicsDomain.INFORMATION_THEORY, parameters={'H': H, 'p_i': p_i}
        ))

        # --------------------------------------------------
        # NEW DOMAIN 11: COSMOLOGY
        # --------------------------------------------------
        a_scale = Function('a')(t)
        H_param = symbols('H')
        self.register(PhysicsEquation(
            name="hubble_parameter", latex=r"H = \frac{\dot{a}}{a}",
            symbolic_expr=sp.Eq(H_param, diff(a_scale, t) / a_scale),
            domain=PhysicsDomain.COSMOLOGY, parameters={'H': H_param, 'a': a_scale, 't': t}
        ))

        # --------------------------------------------------
        # NEW DOMAIN 12: HIGH ENERGY / STRING THEORY
        # --------------------------------------------------
        phi_field = Function('phi')(x, t)
        m_field = symbols('m')
        self.register(PhysicsEquation(
            name="klein_gordon", latex=r"\Box \phi + m^2 \phi = 0",
            symbolic_expr=sp.Eq(diff(phi_field, t, 2) - diff(phi_field, x, 2) + m_field**2 * phi_field, 0), # 1D simplified
            domain=PhysicsDomain.HIGH_ENERGY_STRING, parameters={'phi': phi_field, 'm': m_field}
        ))
    
    def register(self, eq: PhysicsEquation):
        self._equations[eq.name] = eq
    
    def get(self, name: str) -> Optional[PhysicsEquation]:
        return self._equations.get(name)
    
    def list_all(self) -> List[str]:
        return list(self._equations.keys())
    
    def mix(self, eq1_name: str, eq2_name: str, operation: str = 'add') -> sp.Expr:
        """
        Naive mixing: combine two equations algebraically.
        This is the "what if we just add gravity to quantum mechanics?" playground button.
        """
        eq1 = self.get(eq1_name)
        eq2 = self.get(eq2_name)
        
        if not eq1 or not eq2:
            raise ValueError("Equation not found in registry")
        
        if operation == 'add':
            return eq1.symbolic_expr.lhs + eq2.symbolic_expr.lhs
        elif operation == 'multiply':
            return eq1.symbolic_expr.lhs * eq2.symbolic_expr.lhs
        elif operation == 'embed':
            # Substitute one equation into another (requires same variables)
            return eq1.symbolic_expr.subs(eq2.symbolic_expr.lhs, eq2.symbolic_expr.rhs)
        else:
            raise ValueError(f"Unknown operation: {operation}")

# ============================================================
# SECTION 3: THE "PROPELLER" TRANSFORM (MIT Paper Style)
# ============================================================

class PropellerTransform:
    """
    Implements the specific creative mapping described in the MIT droplet paper:
    Classical Diffusion + Memory Term = Quantum-like Behavior.
    """
    
    def __init__(self, registry: EquationRegistry):
        self.registry = registry
    
    def apply_fokker_planck_morph(self, classical_eq_name: str) -> sp.Expr:
        """
        Take a classical deterministic equation and add the stochastic
        "propeller" term that mimics quantum potential.
        """
        eq = self.registry.get(classical_eq_name)
        if not eq:
            raise ValueError(f"Equation {classical_eq_name} not found")
        
        # Get common symbols
        t, x = self.registry.syms['t'], self.registry.syms['x']
        D = symbols('D', positive=True)  # Diffusion coefficient
        
        # Define probability density P(x,t)
        P = Function('P')(x, t)
        
        # Step 1: Start with classical drift term (extracted from eq)
        # For simplicity, assume the equation has a velocity field v(x)
        v = Function('v')(x)
        
        # Step 2: The Fokker-Planck (classical diffusion) part
        fp_eq = diff(P, t) + diff(v * P, x) - D * diff(P, x, 2)
        
        # Step 3: Add the "propeller" / quantum potential term
        # Q = - (hbar^2 / 2m) * (1/sqrt(P)) * d^2(sqrt(P))/dx^2
        hbar, m = self.registry.syms['hbar'], self.registry.syms['m']
        sqrt_P = sqrt(P)
        Q = -(hbar**2 / (2*m)) * (1/sqrt_P) * diff(sqrt_P, x, 2)
        
        # The "morphed" equation: classical FP + quantum potential source term
        morphed = sp.Eq(diff(P, t), -diff(v * P, x) + D * diff(P, x, 2) + Q)
        
        return morphed

# ============================================================
# SECTION 4: MAIN PLAYGROUND INTERFACE
# ============================================================

class PhysicsPlayground:
    """
    Main interface for the "geometric to binary" experimental repo.
    """
    
    def __init__(self):
        self.registry = EquationRegistry()
        self.propeller = PropellerTransform(self.registry)
        self.sp = sp  # Expose sympy for interactive use
    
    def info(self, eq_name: str) -> str:
        """Get formatted info about a registered equation."""
        eq = self.registry.get(eq_name)
        if not eq:
            return f"Equation '{eq_name}' not found."
        return f"""
        Name: {eq.name}
        Domain: {eq.domain.value}
        LaTeX: {eq.latex}
        Expression: {eq.symbolic_expr}
        Parameters: {list(eq.parameters.keys())}
        """
    
    def creative_mix(self, classical_eq: str, operation: str = 'morph') -> sp.Expr:
        """
        Apply a creative transformation to a classical equation.
        
        Args:
            classical_eq: Name of equation in registry
            operation: 'morph' (add quantum-like terms), 'diffuse' (add noise)
        """
        if operation == 'morph':
            return self.propeller.apply_fokker_planck_morph(classical_eq)
        elif operation == 'diffuse':
            eq = self.registry.get(classical_eq)
            if eq:
                morphed = MorphedEquation(source=eq, target_domain=PhysicsDomain.QUANTUM)
                return morphed.apply_diffusion_morphism()
        else:
            raise ValueError(f"Unknown creative operation: {operation}")
    
    def run_example(self):
        """Demonstrate the MIT droplet paper style transformation."""
        print("=" * 60)
        print("PHYSICS PLAYGROUND: Creative Equation Mixing")
        print("=" * 60)
        
        print("\n[1] Available Equations:")
        for name in self.registry.list_all():
            eq = self.registry.get(name)
            print(f"    - {name} ({eq.domain.value})")
        
        print("\n[2] Classical Harmonic Oscillator:")
        ho = self.registry.get("harmonic_oscillator")
        print(f"    {sp.latex(ho.symbolic_expr)}")
        
        print("\n[3] Morphing with Quantum 'Propeller' Term (MIT Droplet Style):")
        morphed = self.creative_mix("harmonic_oscillator", operation="morph")
        print(f"    {sp.latex(morphed)}")
        
        print("\n[4] Naive Cross-Domain Addition (Classical + Quantum):")
        mixed = self.registry.mix("harmonic_oscillator", "schrodinger_free", "add")
        print(f"    {sp.latex(mixed)}")
        
        print("\n" + "=" * 60)
        print(f"Playground ready. {len(self.registry.list_all())} equations registered.")
        print("Try: playground.registry.list_all()")
        print("=" * 60)

# ============================================================
# SECTION 5: INITIALIZATION
# ============================================================

if __name__ == "__main__":
    playground = PhysicsPlayground()
    playground.run_example()
