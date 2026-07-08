# silicon_closure.py
"""
Closes the loop: geometry → physics → silicon → geometry.
"""
class SiliconClosure:
    def __init__(self):
        self.geometry = GeometricStack()
        self.physics = PhysicsPlayground()
        self.silicon = SiliconState()  # from connections_sims.py
    
    def run_loop(self, input_state):
        # 1. Geometry → Physics
        physics_state = self.geometry_to_physics(input_state)
        
        # 2. Physics → Silicon
        silicon_state = self.physics_to_silicon(physics_state)
        
        # 3. Silicon → Geometry (feedback)
        geometry_state = self.silicon_to_geometry(silicon_state)
        
        # 4. Check closure
        return self.verify_closure(input_state, geometry_state)
