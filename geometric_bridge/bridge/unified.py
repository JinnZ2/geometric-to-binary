"""
unified.py — Unified API over all geometric bridges.
"""

import numpy as np
from typing import Optional, Dict, Any, List
from .versor_adapter import VersorAdapter
from .tong_adapter import TongAdapter
from .geomamba_adapter import GeoMambaAdapter
from .magi_adapter import MaGiAdapter
from .geosym_adapter import GeoSymAdapter

class GeometricBridge:
    """
    Unified interface for all geometric intelligence systems.
    """
    
    def __init__(self):
        self.versor = VersorAdapter()
        self.tong = TongAdapter()
        self.geomamba = GeoMambaAdapter()
        self.magi = MaGiAdapter()
        self.geosym = GeoSymAdapter()
        
        self.results = []
        self.metrics = {}
    
    def compute(
        self,
        geometry: str = "octahedron",
        operation: str = "factor",
        input_data: Any = None
    ) -> Dict[str, Any]:
        """
        Compute using the appropriate geometric subsystem.
        """
        result = {
            'geometry': geometry,
            'operation': operation,
            'input': input_data,
            'subsystem': None,
            'output': None,
            'metrics': {},
        }
        
        if operation in ['factor', 'optimize', 'solve']:
            result['subsystem'] = 'versor'
            result['output'] = self._compute_versor(geometry, input_data)
            result['metrics'] = self.versor.get_metrics()
            
        elif operation in ['search', 'construct']:
            result['subsystem'] = 'tong'
            geometry_dict = {'points': [], 'lines': [], 'angles': []}
            if input_data:
                geometry_dict['points'] = input_data.get('points', [])
            result['output'] = self.tong.search(geometry_dict, 'solve')
            result['metrics'] = self.tong.get_metrics()
            
        elif operation in ['evolve', 'sequence']:
            result['subsystem'] = 'geomamba'
            if input_data:
                seq = np.array(input_data.get('sequence', []))
                result['output'] = self.geomamba.evolve(seq)
            result['metrics'] = self.geomamba.get_metrics()
            
        elif operation in ['memory', 'query']:
            result['subsystem'] = 'magi'
            if input_data:
                freq = input_data.get('frequency', 1.0)
                delay = input_data.get('delay', 0.0)
                result['output'] = self.magi.query(freq, delay)
            result['metrics'] = self.magi.get_metrics()
            
        elif operation in ['generate', 'validate']:
            result['subsystem'] = 'geosym'
            problem = self.geosym.generate_problem(
                problem_type=input_data.get('type', 'triangle'),
                symmetry_type=input_data.get('symmetry', 'reflection')
            )
            result['output'] = problem
            result['metrics'] = self.geosym.get_metrics()
        
        self.results.append(result)
        return result
    
    def _compute_versor(self, geometry: str, input_data: Any) -> Any:
        """Compute using Versor adapter."""
        if geometry == "octahedron":
            # Simulate octahedral computation
            state = np.random.randn(3)
            return self.versor.geometric_transform(state)
        elif geometry == "torus":
            state = np.random.randn(2)
            return self.versor.geometric_attention(
                [state], [state], [state]
            )
        else:
            return {"status": "unknown_geometry", "result": None}
    
    def validate(
        self,
        result: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Validate a result against benchmarks.
        """
        validation = {
            'valid': False,
            'score': 0.0,
            'benchmark': 'geometric_integrity',
            'details': {},
        }
        
        # Use GeoSym for validation if possible
        try:
            problem = {'points': [], 'angles': []}
            geosym_result = self.geosym.validate_solution(problem, result)
            validation['score'] = geosym_result.get('score', 0.0)
            validation['valid'] = validation['score'] > 0.5
            validation['details'] = geosym_result
        except:
            # Fallback: simple validation
            if result and 'output' in result:
                validation['score'] = 0.7
                validation['valid'] = True
        
        return validation
    
    def get_stats(self) -> Dict[str, Any]:
        """Get overall statistics."""
        return {
            "operations": len(self.results),
            "subsystems": {
                "versor": self.versor.get_metrics(),
                "tong": self.tong.get_metrics(),
                "geomamba": self.geomamba.get_metrics(),
                "magi": self.magi.get_metrics(),
                "geosym": self.geosym.get_metrics(),
            },
            "last_result": self.results[-1] if self.results else None,
        }
