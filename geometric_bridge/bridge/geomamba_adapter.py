"""
geomamba_adapter.py — Connects to Geo-Mamba Riemannian State Space Model.
"""

import numpy as np
from typing import Optional, Dict, Any

class GeoMambaAdapter:
    """
    Adapter for Geo-Mamba Riemannian State Space Model.
    Maps sequences to geometry-preserving state-space evolution.
    """
    
    def __init__(self, manifold_dim: int = 64):
        self.manifold_dim = manifold_dim
        self.state = np.zeros(manifold_dim)
        self.history = []
    
    def evolve(
        self,
        input_seq: np.ndarray,
        steps: int = 10
    ) -> np.ndarray:
        """
        Evolve state on manifold with geometry-preserving dynamics.
        """
        self.history = []
        self.state = np.zeros(self.manifold_dim)
        
        for i in range(steps):
            # Riemannian step (simplified)
            delta = self._compute_delta(input_seq[i % len(input_seq)])
            self.state = self._riemannian_step(self.state, delta)
            self.history.append(self.state.copy())
        
        return np.array(self.history)
    
    def _compute_delta(self, input_vec: np.ndarray) -> np.ndarray:
        """Compute Riemannian step direction."""
        # Simplified: project input to manifold
        if len(input_vec) > self.manifold_dim:
            return input_vec[:self.manifold_dim] * 0.01
        else:
            delta = np.zeros(self.manifold_dim)
            delta[:len(input_vec)] = input_vec
            return delta * 0.01
    
    def _riemannian_step(
        self,
        state: np.ndarray,
        delta: np.ndarray
    ) -> np.ndarray:
        """Apply Riemannian step with geometry preservation."""
        # Simplified: gradient descent with manifold constraint
        new_state = state + delta
        
        # Project back to manifold (unit sphere)
        norm = np.linalg.norm(new_state)
        if norm > 0:
            new_state = new_state / norm * min(norm, 1.0)
        
        return new_state
    
    def get_manifold_state(self) -> np.ndarray:
        """Get current manifold state."""
        return self.state
    
    def get_metrics(self) -> Dict[str, Any]:
        return {
            "type": "geo_mamba",
            "manifold_dim": self.manifold_dim,
            "history_length": len(self.history),
            "state_norm": float(np.linalg.norm(self.state)),
        }
