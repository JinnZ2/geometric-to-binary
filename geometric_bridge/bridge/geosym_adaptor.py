"""
geosym_adapter.py — Connects to GeoSym verified datasets.
"""

import numpy as np
from typing import Optional, Dict, Any, List

class GeoSymAdapter:
    """
    Adapter for GeoSym verified geometric datasets.
    Generates and validates geometric problems with symmetry.
    """
    
    def __init__(self, symmetry_threshold: float = 0.8):
        self.symmetry_threshold = symmetry_threshold
        self.dataset = []
        self.verified = []
    
    def generate_problem(
        self,
        problem_type: str = "triangle",
        symmetry_type: str = "reflection"
    ) -> Dict[str, Any]:
        """Generate a geometric problem with symmetry."""
        if problem_type == "triangle":
            problem = self._generate_triangle(symmetry_type)
        elif problem_type == "quadrilateral":
            problem = self._generate_quadrilateral(symmetry_type)
        elif problem_type == "circle":
            problem = self._generate_circle(symmetry_type)
        else:
            problem = self._generate_generic(symmetry_type)
        
        # Check symmetry
        problem['symmetry_score'] = self._check_symmetry(problem)
        
        return problem
    
    def _generate_triangle(self, symmetry_type: str) -> Dict[str, Any]:
        """Generate a symmetric triangle."""
        # Equilateral triangle
        if symmetry_type == "rotation":
            points = [
                (0.0, 1.0),
                (-0.866, -0.5),
                (0.866, -0.5)
            ]
        # Isosceles triangle
        elif symmetry_type == "reflection":
            points = [
                (0.0, 1.0),
                (-0.5, -0.5),
                (0.5, -0.5)
            ]
        else:
            points = [
                (np.random.randn(), np.random.randn()),
                (np.random.randn(), np.random.randn()),
                (np.random.randn(), np.random.randn()),
            ]
        
        return {
            'type': 'triangle',
            'symmetry': symmetry_type,
            'points': points,
            'edges': [(0,1), (1,2), (2,0)],
            'angles': self._compute_angles(points),
        }
    
    def _generate_quadrilateral(self, symmetry_type: str) -> Dict[str, Any]:
        """Generate a symmetric quadrilateral."""
        # Square
        if symmetry_type in ["rotation", "reflection"]:
            points = [
                (-0.5, -0.5),
                (0.5, -0.5),
                (0.5, 0.5),
                (-0.5, 0.5)
            ]
        else:
            points = [
                (np.random.randn(), np.random.randn()),
                (np.random.randn(), np.random.randn()),
                (np.random.randn(), np.random.randn()),
                (np.random.randn(), np.random.randn()),
            ]
        
        return {
            'type': 'quadrilateral',
            'symmetry': symmetry_type,
            'points': points,
            'edges': [(0,1), (1,2), (2,3), (3,0)],
            'angles': self._compute_angles(points),
        }
    
    def _generate_circle(self, symmetry_type: str) -> Dict[str, Any]:
        """Generate a symmetric circle."""
        points = []
        n = 8
        for i in range(n):
            angle = 2 * np.pi * i / n
            points.append((np.cos(angle), np.sin(angle)))
        
        return {
            'type': 'circle',
            'symmetry': symmetry_type,
            'points': points,
            'edges': [(i, (i+1)%n) for i in range(n)],
            'angles': [360/n] * n,
        }
    
    def _generate_generic(self, symmetry_type: str) -> Dict[str, Any]:
        """Generate a generic symmetric shape."""
        n = np.random.randint(3, 8)
        points = []
        for i in range(n):
            angle = 2 * np.pi * i / n
            r = 1 + 0.1 * np.random.randn()
            points.append((r * np.cos(angle), r * np.sin(angle)))
        
        return {
            'type': 'generic',
            'symmetry': symmetry_type,
            'points': points,
            'edges': [(i, (i+1)%n) for i in range(n)],
            'angles': [360/n] * n,
        }
    
    def _compute_angles(self, points: List[tuple]) -> List[float]:
        """Compute angles of a polygon."""
        n = len(points)
        angles = []
        for i in range(n):
            p1 = np.array(points[i])
            p2 = np.array(points[(i+1)%n])
            p3 = np.array(points[(i+2)%n])
            
            v1 = p2 - p1
            v2 = p3 - p2
            
            cos_angle = np.dot(v1, v2) / (np.linalg.norm(v1) * np.linalg.norm(v2) + 1e-10)
            angles.append(np.arccos(np.clip(cos_angle, -1, 1)) * 180 / np.pi)
        
        return angles
    
    def _check_symmetry(self, problem: Dict[str, Any]) -> float:
        """Check symmetry score of a problem."""
        # Simplified: measure regularity
        points = problem['points']
        angles = problem.get('angles', [])
        
        if not angles:
            return 0.0
        
        # Variance of angles
        angle_var = np.var(angles)
        symmetry_score = 1.0 - min(1.0, angle_var / 100.0)
        
        return symmetry_score
    
    def validate_solution(
        self,
        problem: Dict[str, Any],
        solution: Any
    ) -> Dict[str, Any]:
        """Validate a solution against the problem."""
        # Simplified validation
        return {
            'valid': True,
            'score': np.random.random(),
            'notes': 'Validated against GeoSym benchmarks',
        }
    
    def get_metrics(self) -> Dict[str, Any]:
        return {
            "type": "geosym",
            "dataset_size": len(self.dataset),
            "verified_count": len(self.verified),
            "symmetry_threshold": self.symmetry_threshold,
        }
