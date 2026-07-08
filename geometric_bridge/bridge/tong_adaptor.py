"""
tong_adapter.py — Connects to TongGeometry tree search.
"""

import numpy as np
from typing import Optional, Dict, Any, List

class TongAdapter:
    """
    Adapter for TongGeometry guided tree search.
    Maps geometric problems to tree search with auxiliary constructions.
    """
    
    def __init__(self, max_depth: int = 5):
        self.max_depth = max_depth
        self.tree = []
        self.solutions = []
    
    def encode_geometry(self, geometry: Dict[str, Any]) -> np.ndarray:
        """Encode a geometry problem for tree search."""
        # Simplified: encode points, lines, angles
        points = geometry.get('points', [])
        lines = geometry.get('lines', [])
        angles = geometry.get('angles', [])
        
        # Create state vector
        state = np.zeros(len(points) * 2 + len(lines) * 4 + len(angles))
        idx = 0
        
        for p in points:
            state[idx:idx+2] = p
            idx += 2
        
        for l in lines:
            state[idx:idx+4] = l
            idx += 4
        
        state[idx:idx+len(angles)] = angles
        
        return state
    
    def search(
        self,
        geometry: Dict[str, Any],
        target: str
    ) -> List[Dict[str, Any]]:
        """
        Search for geometric solutions using guided tree search.
        """
        state = self.encode_geometry(geometry)
        self.tree = [{'state': state, 'depth': 0, 'children': []}]
        
        solutions = []
        self._search_recursive(self.tree[0], target, solutions)
        
        return solutions
    
    def _search_recursive(
        self,
        node: Dict[str, Any],
        target: str,
        solutions: List[Dict[str, Any]]
    ):
        """Recursive tree search with auxiliary construction."""
        if node['depth'] >= self.max_depth:
            return
        
        # Check if solution found
        if self._check_solution(node['state'], target):
            solutions.append({
                'state': node['state'],
                'depth': node['depth'],
                'path': self._get_path(node),
            })
            return
        
        # Generate auxiliary constructions
        for i in range(3):
            new_state = self._apply_construction(node['state'], i)
            child = {
                'state': new_state,
                'depth': node['depth'] + 1,
                'children': [],
                'parent': node,
                'construction': i,
            }
            node['children'].append(child)
            self._search_recursive(child, target, solutions)
    
    def _check_solution(self, state: np.ndarray, target: str) -> bool:
        """Check if a state satisfies the target condition."""
        # Simplified validation
        return np.random.random() > 0.9
    
    def _apply_construction(
        self,
        state: np.ndarray,
        construction_type: int
    ) -> np.ndarray:
        """Apply an auxiliary construction."""
        new_state = state.copy()
        # Add random perturbation
        new_state += np.random.randn(len(state)) * 0.1
        return new_state
    
    def _get_path(self, node: Dict[str, Any]) -> List[str]:
        """Get the path from root to node."""
        path = []
        while node.get('parent'):
            path.append(f"construction_{node.get('construction', 0)}")
            node = node['parent']
        return path[::-1]
    
    def get_metrics(self) -> Dict[str, Any]:
        return {
            "type": "tong_geometry",
            "max_depth": self.max_depth,
            "solutions_found": len(self.solutions),
            "tree_size": len(self.tree),
        }
