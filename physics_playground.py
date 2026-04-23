"""
physics_playground.py
A symbolic sandbox for mixing, matching, and morphing physics equations.
Built on SymPy for the "geometric to binary" style experimental repo.
"""

import sympy as sp
from sympy import symbols, Function, diff, integrate, exp, sin, cos, sqrt
from sympy.physics.quantum import Dagger, Ket, Bra, Operator
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
    CUSTOM = "custom"

@dataclass
class PhysicsEquation:
    """Container for a single physics equation with metadata."""
    name: str
    latex: str
    symbolic_expr: sp.Expr
    domain: PhysicsDomain
    parameters: Dict[str, sp.Symbol] = field(default_factory=dict)
    constraints: List[sp.Relational] = field(default_factory=list)
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
        # Transform a classical ODE/PDE into a stochastic PDE form
        # P(x,t) is the probability density
        P = Function('P')(x, t)
        
        # This is the minimalist morph: Classical field + Diffusion
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
            'm': symbols('m', positive=True),       # mass
            'v': symbols('v', real=True),           # velocity
            'E': symbols('E', real=True),           # energy
            'p': symbols('p', real=True),           # momentum
            'hbar': symbols('hbar', positive=True), # reduced Planck
            'k': symbols('k', real=True),           # wave number / spring constant
            'T': symbols('T', positive=True),       # temperature
            'S': symbols('S', real=True),           # entropy / action
        }
    
    def _register_builtins(self):
        """Populate with standard equations from multiple domains."""
        s = self.syms
        t, x, m, v, E, p, hbar, k, T, S = s.values()
        
        # ===== CLASSICAL MECHANICS =====
        # Newton's Second Law
        F = Function('F')(t)
        a = Function('a')(t)
        self.register(PhysicsEquation(
            name="newton_2",
            latex=r"F = m a",
            symbolic_expr=sp.Eq(F, m * a),
            domain=PhysicsDomain.CLASSICAL_MECHANICS,
            parameters={'F': F, 'm': m, 'a': a}
        ))
        
        # Harmonic Oscillator
        self.register(PhysicsEquation(
            name="harmonic_oscillator",
            latex=r"m \ddot{x} = -k x",
            symbolic_expr=sp.Eq(m * diff(x, t, 2), -k * x),
            domain=PhysicsDomain.CLASSICAL_MECHANICS,
            parameters={'m': m, 'k': k, 'x(t)': sp.Function('x')(t)}
        ))
        
        # Lagrangian (1D free particle - minimal action)
        L = Function('L')(x, v, t)
        self.register(PhysicsEquation(
            name="lagrangian_free_particle",
            latex=r"L = \frac{1}{2} m v^2",
            symbolic_expr=sp.Eq(L, (1/2) * m * v**2),
            domain=PhysicsDomain.CLASSICAL_MECHANICS,
            parameters={'L': L, 'm': m, 'v': v}
        ))
        
        # ===== QUANTUM MECHANICS =====
        # Time-dependent Schrödinger (1D free particle)
        psi = Function('psi')(x, t)
        self.register(PhysicsEquation(
            name="schrodinger_free",
            latex=r"i\hbar \frac{\partial \psi}{\partial t} = -\frac{\hbar^2}{2m} \frac{\partial^2 \psi}{\partial x^2}",
            symbolic_expr=sp.Eq(
                sp.I * hbar * diff(psi, t),
                -(hbar**2)/(2*m) * diff(psi, x, 2)
            ),
            domain=PhysicsDomain.QUANTUM,
            parameters={'psi': psi, 'hbar': hbar, 'm': m}
        ))
        
        # Probability Current (where the "propeller" idea lives)
        j = Function('j')(x, t)
        self.register(PhysicsEquation(
            name="probability_current",
            latex=r"j = \frac{\hbar}{2mi}(\psi^* \nabla \psi - \psi \nabla \psi^*)",
            symbolic_expr=sp.Eq(
                j, 
                (hbar/(2*m*sp.I)) * (sp.conjugate(psi) * diff(psi, x) - psi * diff(sp.conjugate(psi), x))
            ),
            domain=PhysicsDomain.QUANTUM
        ))
        
        # ===== THERMODYNAMICS / STATISTICAL =====
        # Boltzmann factor (bridges to quantum statistics)
        Z = Function('Z')(T)
        self.register(PhysicsEquation(
            name="boltzmann_factor",
            latex=r"P(E) \propto e^{-E/k_B T}",
            symbolic_expr=exp(-E / (k * T)),
            domain=PhysicsDomain.STATISTICAL,
            parameters={'E': E, 'k_B': k, 'T': T}
        ))
        
        # ===== FLUID DYNAMICS =====
        # Continuity equation
        rho = Function('rho')(x, t)
        u = Function('u')(x, t)
        self.register(PhysicsEquation(
            name="continuity_1d",
            latex=r"\frac{\partial \rho}{\partial t} + \frac{\partial (\rho u)}{\partial x} = 0",
            symbolic_expr=sp.Eq(diff(rho, t) + diff(rho * u, x), 0),
            domain=PhysicsDomain.FLUID_DYNAMICS,
            parameters={'rho': rho, 'u': u}
        ))
        
        # ===== ELECTROMAGNETISM =====
        # Wave equation (classical field)
        phi = Function('phi')(x, t)
        c = symbols('c', positive=True)
        self.syms['c'] = c
        self.register(PhysicsEquation(
            name="wave_equation_1d",
            latex=r"\frac{\partial^2 \phi}{\partial t^2} = c^2 \frac{\partial^2 \phi}{\partial x^2}",
            symbolic_expr=sp.Eq(diff(phi, t, 2), c**2 * diff(phi, x, 2)),
            domain=PhysicsDomain.ELECTROMAGNETISM,
            parameters={'phi': phi, 'c': c}
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
        print("Playground ready. Try: playground.registry.list_all()")
        print("=" * 60)

# ============================================================
# SECTION 5: INITIALIZATION
# ============================================================

if __name__ == "__main__":
    playground = PhysicsPlayground()
    playground.run_example()
