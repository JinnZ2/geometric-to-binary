# sim/phase_boundary.py
"""
Maps the phase boundary between linear and geometric processing.
"""

import numpy as np
import matplotlib.pyplot as plt
from scipy.optimize import curve_fit

class PhaseBoundaryMapper:
    """
    Maps the phase boundary between linear and geometric.
    """
    
    def __init__(self):
        self.results = []
    
    def run_scan(self):
        """
        Scan across information density to find the phase boundary.
        """
        densities = np.logspace(0, 3, 20)  # 1 to 1000 points
        results = {'density': [], 'linear_score': [], 'geometric_score': []}
        
        for density in densities:
            linear_score = self._run_linear_test(int(density))
            geometric_score = self._run_geometric_test(int(density))
            
            results['density'].append(density)
            results['linear_score'].append(linear_score)
            results['geometric_score'].append(geometric_score)
            
            # Detect phase boundary
            if geometric_score > linear_score:
                phase = 'geometric'
            else:
                phase = 'linear'
            
            self.results.append({
                'density': density,
                'linear_score': linear_score,
                'geometric_score': geometric_score,
                'phase': phase
            })
        
        return results
    
    def _run_linear_test(self, n):
        """Simulate linear performance."""
        # Linear performance degrades with density
        return max(0, 0.9 - 0.001 * n)
    
    def _run_geometric_test(self, n):
        """Simulate geometric performance."""
        # Geometric performance improves with density
        return min(0.95, 0.3 + 0.005 * n)
    
    def find_boundary(self):
        """Find the phase boundary density."""
        for i, result in enumerate(self.results):
            if result['phase'] == 'geometric':
                # Find where it switches
                if i > 0 and self.results[i-1]['phase'] == 'linear':
                    return (self.results[i-1]['density'] + self.results[i]['density']) / 2
        return None
    
    def plot(self):
        """Plot the phase diagram."""
        densities = [r['density'] for r in self.results]
        linear_scores = [r['linear_score'] for r in self.results]
        geometric_scores = [r['geometric_score'] for r in self.results]
        
        plt.figure(figsize=(10, 6))
        plt.plot(densities, linear_scores, 'b-', label='Linear', linewidth=2)
        plt.plot(densities, geometric_scores, 'r-', label='Geometric', linewidth=2)
        
        # Mark phase boundary
        boundary = self.find_boundary()
        if boundary:
            plt.axvline(x=boundary, color='green', linestyle='--', 
                       label=f'Phase Boundary: {boundary:.0f}')
        
        plt.xscale('log')
        plt.xlabel('Information Density (points)')
        plt.ylabel('Performance Score')
        plt.title('Phase Diagram: Linear vs Geometric')
        plt.legend()
        plt.grid(True, alpha=0.3)
        plt.show()
