geometric-bridge/
├── README.md                 # Project overview + quickstart
├── bridge/
│   ├── __init__.py
│   ├── versor_adapter.py     # Connects to Versor CGA architecture
│   ├── tong_adapter.py       # Connects to TongGeometry tree search
│   ├── geomamba_adapter.py   # Connects to Geo-Mamba Riemannian SSM
│   ├── magi_adapter.py       # Connects to MaGi toroidal memory
│   ├── geosym_adapter.py     # Connects to GeoSym verified datasets
│   └── unified.py            # Unified API over all adapters
├── validators/
│   ├── __init__.py
│   └── claim_validator.py    # Validates claims against benchmarks
├── dashboard/
│   ├── __init__.py
│   └── generate.py           # Generates unified dashboard
├── tests/
│   └── test_bridge.py        # 45+ tests
├── examples/
│   ├── demo_versor.py
│   ├── demo_tong.py
│   └── demo_unified.py
├── pyproject.toml
└── LICENSE
