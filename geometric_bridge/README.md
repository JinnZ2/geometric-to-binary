# Geometric Bridge

A unified integration layer for the geometric intelligence ecosystem.

Maps JinnZ2 ecosystem framework to current research:

| Your Concept | Research Implementation |
|--------------|------------------------|
| Geometric Stack | Versor CGA |
| Distortion Sensing | TangramSR |
| Stack Expansion | TongGeometry |
| Polyhedral Families | GIQ Benchmark |
| Living Intelligence | MaGi Toroidal Memory |
| Homeostasis | Geo-Mamba |
| Semantic Geometry | Functional Geometric Algebra |

## Layout

```text
bridge/
  unified.py            GeometricBridge — the unified API over all adapters
  versor_adapter.py     Versor CGA architecture
  tong_adapter.py       TongGeometry tree search
  geomamba_adapter.py   Geo-Mamba Riemannian SSM
  magi_adapter.py       MaGi toroidal memory
  geosym_adapter.py     GeoSym verified datasets
dashboard/
  generate.py           generate_dashboard(bridge) → dashboard output
examples/
  demo_unified.py       Exercises all five adapters end to end
```

`GeometricBridge` dispatches on `operation`: `factor` → Versor,
`search` → Tong, `evolve` → Geo-Mamba, `memory` → MaGi, `generate` → GeoSym.

## Quickstart

```bash
python examples/demo_unified.py
```

```python
from bridge.unified import GeometricBridge

bridge = GeometricBridge()

# Run a geometric computation
result = bridge.compute(
    geometry="octahedron",
    operation="factor",
    input_data=143,
)

# Validate against benchmarks
validation = bridge.validate(result)
print(validation["score"])

# Per-adapter usage counters
print(bridge.get_stats())
```

## Status

This layer is standalone — it is not imported by the physics playground and is
not covered by the repo's `tests/` suite. There is no `validators/` package and
no adapter test suite yet; `bridge.validate()` currently scores in-process
rather than against an external benchmark.

## License

MIT (matching the `consent.license` field in the repo's `.fieldlink.json`).
