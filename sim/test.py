def run_experiment():
    """Run the falsifiable experiment."""
    results = {
        'linear': {'detect_times': [], 'correct_times': []},
        'geometric': {'detect_times': [], 'correct_times': []}
    }
    
    for trial in range(100):
        # Generate data with a distortion
        data = generate_data_with_distortion(trial)
        
        # Linear
        linear = LinearSystem()
        start = time.time()
        detect_pos = linear.process(data)
        detect_time = time.time() - start
        results['linear']['detect_times'].append(detect_time)
        
        # Geometric
        geo = GeometricSystem()
        start = time.time()
        detect_pos, layer = geo.process(data)
        detect_time = time.time() - start
        results['geometric']['detect_times'].append(detect_time)
    
    return results
