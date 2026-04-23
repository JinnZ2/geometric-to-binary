"""
graph.py
EquationGraph implementation for navigating the state space of equations.
"""

import networkx as nx
from typing import Dict, Any, List
from physics_playground import PhysicsEquation, EquationRegistry

class EquationGraph:
    """
    A directed graph representing the state space of physics equations.
    Nodes are equations, edges are morphisms (transformations).
    """
    def __init__(self):
        self.G = nx.DiGraph()
    
    def add_equation(self, eq: PhysicsEquation):
        """Add an equation as a node in the graph."""
        self.G.add_node(eq.name, data=eq)
    
    def add_morphism(self, source: str, target: str, morphism: str, weight: float):
        """Add a directed edge representing a transformation between equations."""
        self.G.add_edge(source, target, morphism=morphism, weight=weight)
    
    def neighbors(self, eq_name: str) -> List[str]:
        """Get all equations that can be reached from the given equation."""
        return list(self.G.successors(eq_name))
    
    def path(self, start: str, end: str) -> List[str]:
        """Find the shortest path between two equations based on edge weights."""
        return nx.shortest_path(self.G, start, end, weight="weight")

def build_example_graph(registry: EquationRegistry) -> EquationGraph:
    """Build an example graph using equations from the registry."""
    graph = EquationGraph()
    
    # Add nodes
    graph.add_equation(registry.get("harmonic_oscillator"))
    graph.add_equation(registry.get("schrodinger_free"))
    graph.add_equation(registry.get("continuity_1d"))
    
    # Add edges (morphisms)
    graph.add_morphism(
        "harmonic_oscillator",
        "fokker_planck_form",
        morphism="diffusion_morph",
        weight=0.3
    )
    
    graph.add_morphism(
        "continuity_1d",
        "schrodinger_free",
        morphism="madelung_transform",
        weight=0.1
    )
    
    return graph

if __name__ == "__main__":
    registry = EquationRegistry()
    graph = build_example_graph(registry)
    print("Graph built successfully.")
    print(f"Nodes: {list(graph.G.nodes)}")
    print(f"Edges: {list(graph.G.edges(data=True))}")
