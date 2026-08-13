#!/usr/bin/env python3
"""
demo_unified.py — Demonstration of unified geometric bridge.
"""

import os
import sys

import numpy as np

# Ensure the package root is on the path, so the demo runs from any CWD
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from bridge.unified import GeometricBridge

def main():
    print("🧊 Geometric Bridge Demo")
    print("=" * 60)
    
    bridge = GeometricBridge()
    
    # 1. Versor computation
    print("\n1. Versor Computation:")
    result = bridge.compute(
        geometry="octahedron",
        operation="factor",
        input_data=143
    )
    print(f"   Result: {result['output']}")
    
    # 2. Tong search
    print("\n2. Tong Search:")
    result = bridge.compute(
        geometry="triangle",
        operation="search",
        input_data={'points': [(0,0), (1,0), (0,1)]}
    )
    print(f"   Solutions found: {len(result['output'])}")
    
    # 3. Geo-Mamba evolution
    print("\n3. Geo-Mamba Evolution:")
    result = bridge.compute(
        geometry="manifold",
        operation="evolve",
        input_data={'sequence': [np.array([1,2,3]), np.array([4,5,6])]}
    )
    print(f"   State history: {len(result['output'])} steps")
    
    # 4. MaGi memory
    print("\n4. MaGi Memory:")
    result = bridge.compute(
        geometry="torus",
        operation="memory",
        input_data={'frequency': 1.0, 'delay': 0.5}
    )
    print(f"   Query results: {len(result['output'])}")
    
    # 5. GeoSym generation
    print("\n5. GeoSym Generation:")
    result = bridge.compute(
        geometry="triangle",
        operation="generate",
        input_data={'type': 'triangle', 'symmetry': 'reflection'}
    )
    print(f"   Generated {result['output']['type']} with {len(result['output']['points'])} points")
    
    # 6. Validation
    print("\n6. Validation:")
    validation = bridge.validate(result)
    print(f"   Score: {validation['score']:.2f}")
    print(f"   Valid: {validation['valid']}")
    
    # 7. Stats
    print("\n7. Stats:")
    stats = bridge.get_stats()
    print(f"   Operations: {stats['operations']}")
    for name, metrics in stats['subsystems'].items():
        print(f"   - {name}: {metrics}")

if __name__ == "__main__":
    main()
