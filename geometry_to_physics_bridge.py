#!/usr/bin/env python3
"""
geometry_to_physics_bridge.py

Connects the geometric framework (Rosetta-Shape-Core, Polyhedral-Intelligence,
Mandala-Computing) to the physics repository (Geometric-to-Binary).

Provides:
    1. Geometry → Physics domain mapping
    2. Distortion → Morphism translation
    3. Healing via physics transformations
    4. Silicon closure loop
    5. Unified health scoring

The bridge closes the loop:
    Geometry → Physics → Silicon → Geometry

License: CC0 1.0 Universal (Public Domain Dedication)
Author:  JinnZ2 (bridge layer)
"""

from __future__ import annotations
import numpy as np
import time
import json
from dataclasses import dataclass, field
from typing import Optional, Dict, Any, List, Tuple, Union
from enum import Enum

# =====================================================================
# IMPORTS FROM GEOMETRIC FRAMEWORK
# =====================================================================

try:
    from geometric_stack import GeometricStack, SensingMode, HybridReasoningSystem
except ImportError:
    print("WARNING: geometric_stack.py not found. Using stubs.")
    class GeometricStack:
        def __init__(self, *args, **kwargs): pass
        def sense(self, signals, mode=None): return {'mode': 'unknown', 'homeostasis': 0.5}
        def expand_stack(self, **kwargs): return {'success': False}
        def get_health_score(self): return {'unified_health_score': 0.5}
    class HybridReasoningSystem: pass

# =====================================================================
# IMPORTS FROM PHYSICS REPOSITORY
# =====================================================================

try:
    from physics_playground import PhysicsPlayground
    from graph import EquationGraph
    from connections_sims import SiliconState
    HAS_PHYSICS = True
except ImportError:
    print("WARNING: physics_playground.py not found. Using stubs.")
    HAS_PHYSICS = False
    class PhysicsPlayground:
        def __init__(self, *args, **kwargs): pass
        def morph(self, eq1, eq2): return {'steps': []}
        def creative_mix(self, eq1, eq2): return {'result': 'mixed'}
    class EquationGraph:
        def __init__(self, *args, **kwargs): pass
        def shortest_path(self, a, b): return []
    class SiliconState:
        def __init__(self, *args, **kwargs): pass
        def evolve(self, **kwargs): return {'state': 0}


# =====================================================================
# SECTION 1 -- GEOMETRY TO PHYSICS MAPPING
# =====================================================================

class GeometryPhysicsMapper:
    """
    Maps geometric stack layers to physics domains.
    """
    
    # Mapping: geometry layer → physics domain
    LAYER_TO_DOMAIN = {
        0: "classical_mechanics",
        1: "quantum_mechanics",
        2: "chaos_theory",
        3: "general_relativity",
        4: "biology",
        5: "cosmology",
        6: "thermodynamics",
        7: "electromagnetism",
        8: "fluid_dynamics",
        9: "quantum_field_theory",
    }
    
    # Mapping: physics domain → geometry layer
    DOMAIN_TO_LAYER = {v: k for k, v in LAYER_TO_DOMAIN.items()}
    
    # Mapping: distortion type → physics morphism
    DISTORTION_TO_MORPHISM = {
        'decoupling': 'classical_to_diffusion_morph',
        'narrative_wrapping': 'continuity_to_schrodinger_madelung',
        'manifold_failure': 'schrodinger_to_klein_gordon',
        'homeostasis_violation': 'quantum_to_chaos_isomorphism',
        'stack_overflow': 'ricci_flow_curvature',
        'energy_loss': 'classical_to_thermodynamic_morph',
        'constraint_break': 'lagrangian_to_hamiltonian_morph',
        'symmetry_break': 'continuity_to_poisson_morph',
    }
    
    # Mapping: physics morphism → geometry healing operation
    MORPHISM_TO_HEALING = {
        'classical_to_diffusion_morph': {
            'operation': 're_tether',
            'description': 'Re-tether geometry to classical constraints'
        },
        'continuity_to_schrodinger_madelung': {
            'operation': 'ground_words',
            'description': 'Ground high-drift narrative words'
        },
        'schrodinger_to_klein_gordon': {
            'operation': 'correct_manifold',
            'description': 'Correct bridge matrix manifold'
        },
        'quantum_to_chaos_isomorphism': {
            'operation': 'narrative_stripping',
            'description': 'Strip narrative framing'
        },
        'ricci_flow_curvature': {
            'operation': 'expand_stack',
            'description': 'Expand geometry stack'
        },
        'classical_to_thermodynamic_morph': {
            'operation': 'substrate_aware',
            'description': 'Apply substrate-aware prompting'
        },
        'lagrangian_to_hamiltonian_morph': {
            'operation': 'constraint_reinsertion',
            'description': 'Re-insert original constraints'
        },
        'continuity_to_poisson_morph': {
            'operation': 'correct_manifold',
            'description': 'Rebalance geometry manifold'
        },
    }
    
    def __init__(self):
        if HAS_PHYSICS:
            self.physics = PhysicsPlayground()
            self.graph = EquationGraph()
        else:
            self.physics = None
            self.graph = None
    
    def map_layer_to_domain(self, layer_index: int) -> str:
        """Map a geometry layer to a physics domain."""
        return self.LAYER_TO_DOMAIN.get(layer_index, "unknown")
    
    def map_domain_to_layer(self, domain: str) -> int:
        """Map a physics domain to a geometry layer."""
        return self.DOMAIN_TO_LAYER.get(domain, 0)
    
    def detect_domain_from_geometry(self, geometry_state: Dict[str, Any]) -> str:
        """Detect the physics domain from a geometry state."""
        # Based on layer count and integrity
        layer_count = geometry_state.get('stack_depth', 1)
        homeostasis = geometry_state.get('homeostasis', 0.5)
        
        if homeostasis < 0.3:
            return "chaos_theory"
        elif layer_count <= 2:
            return "classical_mechanics"
        elif layer_count <= 4:
            return "quantum_mechanics"
        elif layer_count <= 6:
            return "general_relativity"
        else:
            return "cosmology"
    
    def map_distortion_to_morphism(self, distortion_type: str) -> str:
        """Map a distortion type to a physics morphism."""
        return self.DISTORTION_TO_MORPHISM.get(distortion_type, 'identity')
    
    def map_morphism_to_healing(self, morphism: str) -> Dict[str, str]:
        """Map a physics morphism to a healing operation."""
        return self.MORPHISM_TO_HEALING.get(morphism, {
            'operation': 're_tether',
            'description': 'Default healing operation'
        })
    
    def get_domain_equations(self, domain: str) -> List[str]:
        """Get equations for a physics domain."""
        if not HAS_PHYSICS:
            return []
        
        # Registry would be queried here
        return self.physics.get_domain_equations(domain) if hasattr(self.physics, 'get_domain_equations') else []


# =====================================================================
# SECTION 2 -- DISTORTION TO MORPHISM TRANSLATOR
# =====================================================================

@dataclass
class TranslationResult:
    """Result of translating a distortion to a morphism."""
    
    distortion_type: str
    morphism: str
    healing_operation: str
    healing_description: str
    confidence: float
    timestamp: float = field(default_factory=time.time)
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "distortion_type": self.distortion_type,
            "morphism": self.morphism,
            "healing_operation": self.healing_operation,
            "healing_description": self.healing_description,
            "confidence": self.confidence,
            "timestamp": time.ctime(self.timestamp),
        }


class DistortionTranslator:
    """
    Translates geometric distortions to physics morphisms.
    """
    
    def __init__(self, mapper: Optional[GeometryPhysicsMapper] = None):
        self.mapper = mapper or GeometryPhysicsMapper()
        self.history: List[TranslationResult] = []
    
    def translate(self, distortion_signal: Dict[str, Any]) -> TranslationResult:
        """
        Translate a distortion signal to a morphism.
        """
        # Detect distortion type
        distortion_type = self._detect_type(distortion_signal)
        
        # Map to morphism
        morphism = self.mapper.map_distortion_to_morphism(distortion_type)
        
        # Map to healing
        healing = self.mapper.map_morphism_to_healing(morphism)
        
        # Compute confidence
        confidence = self._compute_confidence(distortion_signal, distortion_type)
        
        result = TranslationResult(
            distortion_type=distortion_type,
            morphism=morphism,
            healing_operation=healing.get('operation', 're_tether'),
            healing_description=healing.get('description', 'Default healing'),
            confidence=confidence,
        )
        
        self.history.append(result)
        return result
    
    def _detect_type(self, signal: Dict[str, Any]) -> str:
        """Detect the type of distortion."""
        # Check for specific signals
        if signal.get('decoupling', 0) > 0.5:
            return 'decoupling'
        elif signal.get('narrative_wrapping', 0) > 0.5:
            return 'narrative_wrapping'
        elif signal.get('manifold_failure', 0) > 0.5:
            return 'manifold_failure'
        elif signal.get('homeostasis_violation', 0) > 0.5:
            return 'homeostasis_violation'
        elif signal.get('stack_overflow', 0) > 0.5:
            return 'stack_overflow'
        elif signal.get('energy_loss', 0) > 0.5:
            return 'energy_loss'
        elif signal.get('constraint_break', 0) > 0.5:
            return 'constraint_break'
        elif signal.get('symmetry_break', 0) > 0.5:
            return 'symmetry_break'
        else:
            return 'homeostasis_violation'  # Default
    
    def _compute_confidence(self, signal: Dict[str, Any], distortion_type: str) -> float:
        """Compute confidence in the translation."""
        # Base confidence on signal strength
        if distortion_type == 'homeostasis_violation':
            return signal.get('homeostasis', 0.5) - 0.3
        else:
            strength = signal.get(distortion_type, 0)
            if strength > 0.7:
                return 0.9
            elif strength > 0.4:
                return 0.6
            else:
                return 0.3
    
    def get_history(self, last_n: int = 10) -> List[Dict[str, Any]]:
        """Get translation history."""
        return [r.to_dict() for r in self.history[-last_n:]]


# =====================================================================
# SECTION 3 -- HEALING VIA PHYSICS
# =====================================================================

@dataclass
class HealingResult:
    """Result of a healing operation."""
    
    operation: str
    before_health: float
    after_health: float
    improvement: float
    morphism_applied: str
    healed: bool
    details: Dict[str, Any] = field(default_factory=dict)
    timestamp: float = field(default_factory=time.time)
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "operation": self.operation,
            "before_health": self.before_health,
            "after_health": self.after_health,
            "improvement": self.improvement,
            "morphism_applied": self.morphism_applied,
            "healed": self.healed,
            "details": self.details,
            "timestamp": time.ctime(self.timestamp),
        }


class PhysicsHealer:
    """
    Applies physics morphisms as geometric healing operations.
    """
    
    def __init__(self, mapper: Optional[GeometryPhysicsMapper] = None):
        self.mapper = mapper or GeometryPhysicsMapper()
        self.translator = DistortionTranslator(self.mapper)
        self.healing_history: List[HealingResult] = []
        
        if HAS_PHYSICS:
            self.physics = PhysicsPlayground()
        else:
            self.physics = None
    
    def heal(
        self,
        geometry_stack: GeometricStack,
        distortion_signal: Dict[str, Any],
        apply_physics: bool = True,
    ) -> HealingResult:
        """
        Heal a geometry using physics morphisms.
        """
        before_health = distortion_signal.get('homeostasis', 0.5)
        
        # Translate distortion to morphism
        translation = self.translator.translate(distortion_signal)
        
        # Apply healing operation
        if apply_physics and self.physics:
            # Use physics morphism directly
            result = self._apply_physics_healing(
                geometry_stack,
                translation.morphism,
                translation.healing_operation,
            )
        else:
            # Use healing operation only
            result = self._apply_healing_operation(
                geometry_stack,
                translation.healing_operation,
            )
        
        # Measure after health
        after_health = geometry_stack.get_health_score().get('unified_health_score', 0.5)
        improvement = after_health - before_health
        
        healing_result = HealingResult(
            operation=translation.healing_operation,
            before_health=before_health,
            after_health=after_health,
            improvement=improvement,
            morphism_applied=translation.morphism,
            healed=after_health >= 0.75,
            details={
                'translation': translation.to_dict(),
                'result': result,
            },
        )
        
        self.healing_history.append(healing_result)
        return healing_result
    
    def _apply_physics_healing(
        self,
        geometry_stack: GeometricStack,
        morphism: str,
        operation: str,
    ) -> Dict[str, Any]:
        """
        Apply a physics morphism to heal geometry.
        """
        # In full implementation, this would use the physics engine
        # to transform the geometry state through the morphism
        
        # Simplified: use the morphism to determine healing parameters
        if morphism == 'classical_to_diffusion_morph':
            # Re-tether: increase constraint_weight
            return {'applied': 're_tether', 'parameter': 'constraint_weight', 'delta': 0.2}
        elif morphism == 'continuity_to_schrodinger_madelung':
            # Ground words: increase grounding_weight
            return {'applied': 'ground_words', 'parameter': 'grounding_weight', 'delta': 0.2}
        elif morphism == 'schrodinger_to_klein_gordon':
            # Correct manifold: increase bridge_accuracy
            return {'applied': 'correct_manifold', 'parameter': 'bridge_accuracy', 'delta': 0.2}
        elif morphism == 'quantum_to_chaos_isomorphism':
            # Narrative stripping: decrease narrative_weight
            return {'applied': 'narrative_stripping', 'parameter': 'narrative_weight', 'delta': -0.2}
        elif morphism == 'ricci_flow_curvature':
            # Expand stack
            return {'applied': 'expand_stack', 'parameter': 'stack_depth', 'delta': 1}
        else:
            return {'applied': 'default', 'parameter': 'constraint_weight', 'delta': 0.1}
    
    def _apply_healing_operation(
        self,
        geometry_stack: GeometricStack,
        operation: str,
    ) -> Dict[str, Any]:
        """
        Apply a healing operation directly.
        """
        # Map operation to geometry stack method
        if operation == 're_tether':
            # Simulate re-tethering
            return {'applied': 're_tether', 'success': True}
        elif operation == 'ground_words':
            return {'applied': 'ground_words', 'success': True}
        elif operation == 'correct_manifold':
            return {'applied': 'correct_manifold', 'success': True}
        elif operation == 'narrative_stripping':
            return {'applied': 'narrative_stripping', 'success': True}
        elif operation == 'expand_stack':
            # Try to expand the stack
            result = geometry_stack.expand_stack(
                new_dimensions=geometry_stack.layers[-1].dimensions + 1 if geometry_stack.layers else 4,
                source_signal=np.random.randn(geometry_stack.layers[-1].dimensions + 1 if geometry_stack.layers else 4),
            )
            return {'applied': 'expand_stack', 'success': result.get('success', False)}
        else:
            return {'applied': 'default', 'success': False}
    
    def get_history(self, last_n: int = 10) -> List[Dict[str, Any]]:
        """Get healing history."""
        return [h.to_dict() for h in self.healing_history[-last_n:]]


# =====================================================================
# SECTION 4 -- SILICON CLOSURE LOOP
# =====================================================================

@dataclass
class ClosureResult:
    """Result of the silicon closure loop."""
    
    geometry_state: Dict[str, Any]
    physics_state: Dict[str, Any]
    silicon_state: Dict[str, Any]
    closure_verified: bool
    loop_iterations: int
    error: float
    timestamp: float = field(default_factory=time.time)
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "geometry_state": self.geometry_state,
            "physics_state": self.physics_state,
            "silicon_state": self.silicon_state,
            "closure_verified": self.closure_verified,
            "loop_iterations": self.loop_iterations,
            "error": self.error,
            "timestamp": time.ctime(self.timestamp),
        }


class SiliconClosure:
    """
    Closes the loop: Geometry → Physics → Silicon → Geometry.
    """
    
    def __init__(
        self,
        geometry_stack: Optional[GeometricStack] = None,
        mapper: Optional[GeometryPhysicsMapper] = None,
    ):
        self.geometry = geometry_stack or GeometricStack()
        self.mapper = mapper or GeometryPhysicsMapper()
        
        if HAS_PHYSICS:
            self.physics = PhysicsPlayground()
            self.silicon = SiliconState()
        else:
            self.physics = None
            self.silicon = None
        
        self.history: List[ClosureResult] = []
    
    def run_loop(
        self,
        input_state: Dict[str, Any],
        max_iterations: int = 10,
        tolerance: float = 0.01,
    ) -> ClosureResult:
        """
        Run the silicon closure loop.
        """
        initial_state = input_state.copy()
        current_state = input_state.copy()
        
        for iteration in range(max_iterations):
            # 1. Geometry → Physics
            physics_state = self._geometry_to_physics(current_state)
            
            # 2. Physics → Silicon
            silicon_state = self._physics_to_silicon(physics_state)
            
            # 3. Silicon → Geometry (feedback)
            new_geometry_state = self._silicon_to_geometry(silicon_state)
            
            # 4. Check closure
            error = self._compute_error(current_state, new_geometry_state)
            
            if error < tolerance:
                closure_verified = True
                break
            
            current_state = new_geometry_state
            closure_verified = False
        
        # Final state
        final_geometry = self._silicon_to_geometry(silicon_state) if 'silicon_state' in locals() else current_state
        
        result = ClosureResult(
            geometry_state=final_geometry,
            physics_state=physics_state if 'physics_state' in locals() else {},
            silicon_state=silicon_state if 'silicon_state' in locals() else {},
            closure_verified=closure_verified,
            loop_iterations=iteration + 1,
            error=error if 'error' in locals() else tolerance,
        )
        
        self.history.append(result)
        return result
    
    def _geometry_to_physics(self, geometry_state: Dict[str, Any]) -> Dict[str, Any]:
        """Map geometry state to physics state."""
        # Extract geometry parameters
        stack_depth = geometry_state.get('stack_depth', 1)
        homeostasis = geometry_state.get('homeostasis', 0.5)
        
        # Map to physics domain
        domain = self.mapper.detect_domain_from_geometry(geometry_state)
        
        # Return physics state
        return {
            'domain': domain,
            'stack_depth': stack_depth,
            'homeostasis': homeostasis,
            'equations': self.mapper.get_domain_equations(domain),
        }
    
    def _physics_to_silicon(self, physics_state: Dict[str, Any]) -> Dict[str, Any]:
        """Map physics state to silicon state."""
        if HAS_PHYSICS and self.silicon:
            # Use the silicon state model
            n = physics_state.get('stack_depth', 1)
            d = physics_state.get('homeostasis', 0.5)
            ℓ = 1.0 - d
            κ = n / (n + 1)
            
            # Evolve silicon state
            state = self.silicon.evolve(
                n=n,
                d=d,
                ℓ=ℓ,
                κ=κ,
            )
            return {'state': state, 'parameters': {'n': n, 'd': d, 'ℓ': ℓ, 'κ': κ}}
        else:
            # Simplified silicon state
            return {
                'n': physics_state.get('stack_depth', 1),
                'd': physics_state.get('homeostasis', 0.5),
                'ℓ': 1.0 - physics_state.get('homeostasis', 0.5),
                'κ': physics_state.get('stack_depth', 1) / (physics_state.get('stack_depth', 1) + 1),
            }
    
    def _silicon_to_geometry(self, silicon_state: Dict[str, Any]) -> Dict[str, Any]:
        """Map silicon state back to geometry state."""
        if HAS_PHYSICS and self.silicon:
            params = silicon_state.get('parameters', {})
            n = params.get('n', 1)
            d = params.get('d', 0.5)
            
            return {
                'stack_depth': int(n),
                'homeostasis': d,
                'silicon_processed': True,
            }
        else:
            n = silicon_state.get('n', 1)
            d = silicon_state.get('d', 0.5)
            
            return {
                'stack_depth': int(n),
                'homeostasis': d,
                'silicon_processed': True,
            }
    
    def _compute_error(self, state1: Dict[str, Any], state2: Dict[str, Any]) -> float:
        """Compute error between two states."""
        # Compare key parameters
        params = ['stack_depth', 'homeostasis']
        error = 0.0
        
        for param in params:
            v1 = state1.get(param, 0)
            v2 = state2.get(param, 0)
            error += abs(v1 - v2)
        
        return error
    
    def get_history(self, last_n: int = 10) -> List[Dict[str, Any]]:
        """Get closure history."""
        return [h.to_dict() for h in self.history[-last_n:]]


# =====================================================================
# SECTION 5 -- UNIFIED BRIDGE
# =====================================================================

class GeometryPhysicsBridge:
    """
    Unified bridge between geometric framework and physics repository.
    """
    
    def __init__(
        self,
        geometry_stack: Optional[GeometricStack] = None,
    ):
        self.geometry = geometry_stack or GeometricStack()
        self.mapper = GeometryPhysicsMapper()
        self.translator = DistortionTranslator(self.mapper)
        self.healer = PhysicsHealer(self.mapper)
        self.closure = SiliconClosure(self.geometry, self.mapper)
        
        self.bridge_history: List[Dict[str, Any]] = []
    
    def sense_and_translate(
        self,
        signals: List[np.ndarray],
    ) -> Dict[str, Any]:
        """
        Sense signals and translate distortions to physics.
        """
        # 1. Sense with geometry
        sense_result = self.geometry.sense(signals)
        
        # 2. Detect distortions
        distortions = sense_result.get('distortions', [])
        
        # 3. Translate each distortion
        translations = []
        for distortion in distortions:
            translation = self.translator.translate(distortion)
            translations.append(translation.to_dict())
        
        return {
            'sense_result': sense_result,
            'distortions': distortions,
            'translations': translations,
            'health': self.geometry.get_health_score(),
        }
    
    def heal_via_physics(
        self,
        distortion_signal: Dict[str, Any],
        apply_physics: bool = True,
    ) -> Dict[str, Any]:
        """
        Heal using physics morphisms.
        """
        result = self.healer.heal(self.geometry, distortion_signal, apply_physics)
        return result.to_dict()
    
    def run_closure_loop(
        self,
        input_state: Dict[str, Any],
        max_iterations: int = 10,
    ) -> Dict[str, Any]:
        """
        Run the full closure loop.
        """
        result = self.closure.run_loop(input_state, max_iterations)
        return result.to_dict()
    
    def get_full_health(self) -> Dict[str, Any]:
        """
        Get unified health score across all layers.
        """
        geometry_health = self.geometry.get_health_score()
        
        # Physics health
        physics_health = {
            'morphism_count': len(self.translator.history),
            'healing_count': len(self.healer.healing_history),
            'closure_count': len(self.closure.history),
        }
        
        # Silicon health
        silicon_health = {
            'closure_verified': self.closure.history[-1].closure_verified if self.closure.history else False,
            'loop_error': self.closure.history[-1].error if self.closure.history else 1.0,
        }
        
        return {
            'geometry': geometry_health,
            'physics': physics_health,
            'silicon': silicon_health,
            'unified_health_score': geometry_health.get('unified_health_score', 0.5),
            'ecosystem_health': geometry_health.get('unified_health_score', 0.5) * 0.7 + 0.3,
        }
    
    def to_dict(self) -> Dict[str, Any]:
        """
        Convert entire bridge to dictionary.
        """
        return {
            'geometry_state': self.geometry.to_dict(),
            'health': self.get_full_health(),
            'history': {
                'translations': len(self.translator.history),
                'healing': len(self.healer.healing_history),
                'closure': len(self.closure.history),
            },
            'bridge_history': self.bridge_history[-10:],
        }


# =====================================================================
# SECTION 6 -- DEMO
# =====================================================================

def demo():
    """Run a demonstration of the geometry-to-physics bridge."""
    print("🧊 GEOMETRY TO PHYSICS BRIDGE — DEMO")
    print("=" * 70)
    print()
    
    # Create bridge
    bridge = GeometryPhysicsBridge()
    
    # Generate test signals
    print("📡 Generating test signals...")
    signals = []
    for i in range(20):
        if i < 15:
            # Normal signals
            signal = np.random.randn(3) * 0.2 + np.array([1.0, 2.0, 3.0])
        else:
            # Distorted signals
            signal = np.random.randn(3) * 0.5 + np.array([5.0, 5.0, 5.0])
        signals.append(signal)
    
    # 1. Sense and translate
    print("\n🔍 1. Sense and Translate:")
    result = bridge.sense_and_translate(signals)
    print(f"   Distortions detected: {len(result['distortions'])}")
    print(f"   Translations: {len(result['translations'])}")
    for t in result['translations'][:3]:
        print(f"     - {t['distortion_type']} → {t['morphism']} (confidence: {t['confidence']:.2f})")
    
    # 2. Heal via physics
    print("\n💊 2. Heal via Physics:")
    distortion_signal = {'homeostasis_violation': 0.6, 'homeostasis': 0.4}
    healing = bridge.heal_via_physics(distortion_signal)
    print(f"   Operation: {healing['operation']}")
    print(f"   Improvement: {healing['improvement']:.3f}")
    print(f"   Healed: {healing['healed']}")
    
    # 3. Run closure loop
    print("\n🔄 3. Silicon Closure Loop:")
    input_state = {'stack_depth': 3, 'homeostasis': 0.5}
    closure = bridge.run_closure_loop(input_state)
    print(f"   Iterations: {closure['loop_iterations']}")
    print(f"   Verified: {closure['closure_verified']}")
    print(f"   Error: {closure['error']:.3f}")
    
    # 4. Full health
    print("\n🏥 4. Full Health:")
    health = bridge.get_full_health()
    print(f"   Unified Health: {health['unified_health_score']:.3f}")
    print(f"   Ecosystem Health: {health['ecosystem_health']:.3f}")
    print(f"   Geometry: {health['geometry']['unified_health_score']:.3f}")
    print(f"   Healing count: {health['physics']['healing_count']}")
    print(f"   Closure verified: {health['silicon']['closure_verified']}")
    
    print("\n" + "=" * 70)
    print("✅ Demo complete")


# =====================================================================
# SECTION 7 -- ENTRYPOINT
# =====================================================================

if __name__ == "__main__":
    import sys
    import argparse
    
    parser = argparse.ArgumentParser(description="Geometry to Physics Bridge")
    parser.add_argument("--demo", action="store_true", help="Run demo")
    parser.add_argument("--test", action="store_true", help="Run tests")
    parser.add_argument("--json", action="store_true", help="Output as JSON")
    
    args = parser.parse_args()
    
    if args.demo:
        demo()
    elif args.test:
        bridge = GeometryPhysicsBridge()
        signals = [np.random.randn(3) for _ in range(10)]
        result = bridge.sense_and_translate(signals)
        print(json.dumps(result, indent=2, default=str))
    elif args.json:
        bridge = GeometryPhysicsBridge()
        signals = [np.random.randn(3) for _ in range(10)]
        bridge.sense_and_translate(signals)
        print(json.dumps(bridge.to_dict(), indent=2, default=str))
    else:
        demo()
