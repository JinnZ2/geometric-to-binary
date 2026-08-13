# sim/line_vs_geometry.py
"""
Falsifiable simulation comparing linear vs geometric processing.
"""

import numpy as np
import time
import matplotlib.pyplot as plt

class LinearSystem:
    """Standard linear sequence processing."""
    def __init__(self, sequence_length=100):
        self.sequence = np.zeros(sequence_length)
        self.position = 0
    
    def process(self, data):
        """Process data sequentially."""
        self.sequence = data
        self.position = 0
        return self.detect_distortion()
    
    def detect_distortion(self):
        """Detect distortion in the sequence."""
        # Linear detection: look for anomalies in the sequence
        for i in range(1, len(self.sequence)):
            if abs(self.sequence[i] - self.sequence[i-1]) > 0.5:
                self.position = i
                return i
        return -1

class GeometricSystem:
    """Geometric stack processing."""
    def __init__(self, dimensions=3):
        self.dimensions = dimensions
        self.stack = []
        self.homeostasis = 1.0
    
    def process(self, data):
        """Process data geometrically."""
        # Convert sequence to points in 3D
        points = self._sequence_to_points(data)
        
        # Build geometry
        self._build_geometry(points)
        
        # Detect distortion
        return self._detect_distortion()
    
    def _sequence_to_points(self, data):
        """Convert a sequence to points in 3D space."""
        points = []
        for i, val in enumerate(data):
            x = np.cos(i * 0.1) * val
            y = np.sin(i * 0.1) * val
            z = val * 0.5
            points.append(np.array([x, y, z]))
        return points
    
    def _build_geometry(self, points):
        """Build a geometric stack from points."""
        self.stack = [points]
        # Add layers
        for i in range(1, 3):
            layer = points[i::2]  # Transect
            self.stack.append(layer)
    
    def _detect_distortion(self):
        """Detect distortion in the geometry."""
        # Check each layer for outliers
        for layer_idx, layer in enumerate(self.stack):
            if len(layer) < 3:
                continue
            
            # Compute centroid
            centroid = np.mean(layer, axis=0)
            
            # Check distances from centroid
            for i, point in enumerate(layer):
                dist = np.linalg.norm(point - centroid)
                if dist > 0.5:
                    return i, layer_idx
        return -1, -1
