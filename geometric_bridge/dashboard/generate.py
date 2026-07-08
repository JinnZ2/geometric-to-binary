"""
generate.py — Generates unified dashboard.
"""

import json
import time
from typing import Dict, Any

def generate_dashboard(bridge) -> str:
    """Generate HTML dashboard."""
    
    stats = bridge.get_stats()
    
    html = f"""
<!DOCTYPE html>
<html>
<head>
    <title>Geometric Bridge Dashboard</title>
    <style>
        body {{ font-family: monospace; background: #0d1117; color: #c9d1d9; padding: 20px; }}
        .container {{ max-width: 1200px; margin: 0 auto; }}
        h1 {{ color: #58a6ff; }}
        .grid {{ display: grid; grid-template-columns: repeat(auto-fit, minmax(300px, 1fr)); gap: 20px; }}
        .card {{ background: #161b22; border: 1px solid #30363d; border-radius: 12px; padding: 20px; }}
        .card h3 {{ color: #f0f6fc; }}
        .metric {{ font-size: 24px; font-weight: bold; color: #58a6ff; }}
        .subtitle {{ color: #8b949e; font-size: 14px; }}
        table {{ width: 100%; border-collapse: collapse; }}
        td, th {{ padding: 8px; border-bottom: 1px solid #21262d; }}
        .status-ok {{ color: #3fb950; }}
        .status-warn {{ color: #d29922; }}
        .status-fail {{ color: #f85149; }}
    </style>
</head>
<body>
<div class="container">
    <h1>🧊 Geometric Bridge Dashboard</h1>
    <p class="subtitle">Unified view of geometric intelligence ecosystem</p>
    <p class="subtitle">Generated: {time.ctime()} | Operations: {stats['operations']}</p>
    
    <div class="grid">
        <div class="card">
            <h3>Versor (CGA)</h3>
            <div class="metric">{stats['subsystems']['versor']['dimensions']}D</div>
            <div class="subtitle">{stats['subsystems']['versor']['operations']} operations</div>
        </div>
        <div class="card">
            <h3>TongGeometry</h3>
            <div class="metric">{stats['subsystems']['tong']['max_depth']}</div>
            <div class="subtitle">{stats['subsystems']['tong']['solutions_found']} solutions</div>
        </div>
        <div class="card">
            <h3>Geo-Mamba</h3>
            <div class="metric">{stats['subsystems']['geomamba']['manifold_dim']}D</div>
            <div class="subtitle">{stats['subsystems']['geomamba']['history_length']} states</div>
        </div>
        <div class="card">
            <h3>MaGi Toroidal</h3>
            <div class="metric">{stats['subsystems']['magi']['memory_used']}</div>
            <div class="subtitle">/{stats['subsystems']['magi']['memory_capacity']} memory</div>
        </div>
        <div class="card">
            <h3>GeoSym</h3>
            <div class="metric">{stats['subsystems']['geosym']['verified_count']}</div>
            <div class="subtitle">{stats['subsystems']['geosym']['dataset_size']} total</div>
        </div>
    </div>
    
    <h2>Recent Results</h2>
    <table>
        <tr><th>Operation</th><th>Subsystem</th><th>Status</th></tr>
        {''.join([f"<tr><td>{r['operation']}</td><td>{r['subsystem']}</td><td class='status-ok'>✓</td></tr>" for r in stats.get('recent', [])[-5:]])}
    </table>
    
    <h2>Connections</h2>
    <div class="card">
        <pre>
Your Framework          → Current Research
Geometric Stack         → Versor CGA
Distortion Sensing      → TangramSR
Stack Expansion         → TongGeometry
Polyhedral Families     → GIQ Benchmark
Living Intelligence     → MaGi Toroidal
Homeostasis             → Geo-Mamba
Semantic Geometry       → FGA
        </pre>
    </div>
</div>
</body>
</html>
    """
    
    return html
