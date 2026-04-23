"""
tests/test_doc_consistency.py

Catch documentation count drift. The repo has claims like "90 equations",
"23 domains", "112 morphisms", and "54 simulations" scattered across README.md,
CLAUDE.md, EXPLAINER.md, and the sim module docstrings. Those claims are
supposed to match the live code, but historically they drift (we shipped
"44 simulations" in three places after the count was actually 54).

This test mirrors the spirit of the Bridge repo's validate_bridge_contract.py:
compare claimed counts against live sources of truth, fail on mismatch.

Run with:
    python -m pytest tests/test_doc_consistency.py -v
"""

import os
import re
import sys
import importlib

import pytest

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, REPO)

from physics_playground import EquationRegistry
import graph as graph_module


# ── Live counts (the source of truth) ────────────────────────────────────────

@pytest.fixture(scope="module")
def live():
    r = EquationRegistry()
    r._register_all()
    G = graph_module.build_morphism_graph(r)

    modules = ["sims", "workon_sims", "todo_sims", "addon_sims", "connections_sims"]
    per_module = {m: len(importlib.import_module(m).REGISTRY) for m in modules}

    return {
        "equations": len(r._equations),
        "domains":   len({eq.domain for eq in r._equations.values()}),
        "morphisms": G.G.number_of_edges(),
        "sims":      sum(per_module.values()),
        "per_module": per_module,
    }


# ── Which docs claim which totals ────────────────────────────────────────────
#
# Format: (path, pattern, kind)
#   pattern must have a single capture group that parses as int.
#   kind ∈ {"equations", "domains", "morphisms", "sims"}.

DOC_FILES = [
    "README.md",
    "CLAUDE.md",
    "EXPLAINER.md",
    "run_all_sims.py",
    "sims.py",
    "workon_sims.py",
    "todo_sims.py",
    "addon_sims.py",
    "connections_sims.py",
]

CLAIM_PATTERNS = [
    # "90 equations"          ,  "N equations"
    (re.compile(r"\b(\d+)\s+equations\b", re.I),            "equations"),
    # "23 (physics )?domains"
    (re.compile(r"\b(\d+)\s+(?:physics\s+)?domains\b", re.I), "domains"),
    # "112 morphisms" / "112 morphism edges"
    (re.compile(r"\b(\d+)\s+morphism(?:s| edges)\b", re.I),  "morphisms"),
    # "54 sims" / "54 simulations"
    (re.compile(r"\b(\d+)\s+sim(?:s|ulations)\b", re.I),     "sims"),
]


def _collect_claims():
    claims = []   # list of (file, lineno, kind, value)
    for rel in DOC_FILES:
        p = os.path.join(REPO, rel)
        if not os.path.exists(p):
            continue
        with open(p, "r", encoding="utf-8") as f:
            for lineno, line in enumerate(f, 1):
                for rx, kind in CLAIM_PATTERNS:
                    for m in rx.finditer(line):
                        claims.append((rel, lineno, kind, int(m.group(1))))
    return claims


# ── Tests ────────────────────────────────────────────────────────────────────

class TestDocConsistency:

    def test_claims_match_live_totals(self, live):
        """Every 'N <kind>' claim in docs must match the live count."""
        mismatches = []
        per_module_totals = set(live["per_module"].values())

        for rel, lineno, kind, val in _collect_claims():
            expected = live[kind]
            # sim claims may refer to a single module's count (e.g. "26 sims"
            # for sims.py) rather than the global total — accept either.
            if kind == "sims" and val in per_module_totals:
                continue
            if val != expected:
                mismatches.append(
                    f"{rel}:{lineno}  claims {val} {kind}  (live: {expected})"
                )

        assert not mismatches, (
            "Doc count drift detected — update the docs or the code:\n  "
            + "\n  ".join(mismatches)
        )

    def test_per_module_counts_match_run_all_sims(self, live):
        """Per-module sim counts in run_all_sims.py's MODULES descriptions
        must match the live REGISTRY sizes."""
        import run_all_sims as r
        # e.g. "Core physics domain simulations (26)"
        rx = re.compile(r"\((\d+)\)\s*$")
        mismatches = []
        for mod_name, desc in r.MODULES:
            m = rx.search(desc)
            assert m, f"{mod_name} description missing (N): {desc!r}"
            claimed = int(m.group(1))
            actual = live["per_module"][mod_name]
            if claimed != actual:
                mismatches.append(f"{mod_name}: MODULES claims {claimed}, REGISTRY has {actual}")
        assert not mismatches, "Per-module count drift:\n  " + "\n  ".join(mismatches)

    def test_fieldlink_is_valid_json(self):
        """.fieldlink.json must parse and declare a fieldlink.version."""
        import json
        p = os.path.join(REPO, ".fieldlink.json")
        with open(p) as f:
            data = json.load(f)
        assert "fieldlink" in data
        assert "version" in data["fieldlink"]
