"""
magi_adapter.py — Connects to MaGi toroidal memory.
"""

import numpy as np
from typing import Optional, Dict, Any, List

class MaGiAdapter:
    """
    Adapter for MaGi self-organizing geometric intelligence.
    Organizes memory as points on a toroidal phase space.
    """
    
    def __init__(self, torus_dims: int = 3, memory_capacity: int = 1000):
        self.torus_dims = torus_dims
        self.memory_capacity = memory_capacity
        self.memory = []
        self.phase_space = []
    
    def encode_memory(
        self,
        data: np.ndarray,
        frequency: float = 1.0,
        delay: float = 0.0,
        direction: np.ndarray = None
    ) -> Dict[str, Any]:
        """Encode data as a point on the torus."""
        if direction is None:
            direction = np.random.randn(self.torus_dims)
            direction = direction / np.linalg.norm(direction)
        
        point = {
            'data': data,
            'position': self._torus_position(frequency, delay, direction),
            'frequency': frequency,
            'delay': delay,
            'direction': direction,
        }
        
        self.memory.append(point)
        self.phase_space.append(point['position'])
        
        # Truncate if memory full
        if len(self.memory) > self.memory_capacity:
            self.memory = self.memory[-self.memory_capacity:]
            self.phase_space = self.phase_space[-self.memory_capacity:]
        
        return point
    
    def _torus_position(
        self,
        frequency: float,
        delay: float,
        direction: np.ndarray
    ) -> np.ndarray:
        """Compute position on torus."""
        t = frequency * (1 + delay)
        position = np.zeros(self.torus_dims)
        for i in range(self.torus_dims):
            position[i] = np.sin(t + i * 2 * np.pi / self.torus_dims)
        return position
    
    def query(
        self,
        frequency: float = 1.0,
        delay: float = 0.0,
        radius: float = 0.5
    ) -> List[Dict[str, Any]]:
        """Query memory by proximity in phase space."""
        target = self._torus_position(frequency, delay, np.zeros(self.torus_dims))
        
        results = []
        for point in self.memory:
            dist = np.linalg.norm(point['position'] - target)
            if dist < radius:
                results.append(point)
        
        return results
    
    def get_metrics(self) -> Dict[str, Any]:
        return {
            "type": "magi_toroidal",
            "torus_dims": self.torus_dims,
            "memory_capacity": self.memory_capacity,
            "memory_used": len(self.memory),
            "phase_space": len(self.phase_space),
        }
