"""
tests/test_modern_claims.py

modern_claims.json is the symbolic surface of the Level 6 sims. Unlike the
repo-level `.claims` file it is hand-written, so nothing regenerates it — which
means it can silently drift away from both the sim registry and the equation
registry. This test pins it to both.

Run with:
    python -m pytest tests/test_modern_claims.py -v
"""

import json
import os
import sys

import pytest

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, REPO)

from physics_playground import EquationRegistry
from modern_sims import REGISTRY as SIM_REGISTRY

CLAIMS_PATH = os.path.join(REPO, "modern_claims.json")


@pytest.fixture(scope="module")
def claims():
    with open(CLAIMS_PATH, encoding="utf-8") as f:
        return json.load(f)


@pytest.fixture(scope="module")
def equation_ids():
    r = EquationRegistry()
    r._register_all()
    return set(r._equations)


def test_one_claim_per_sim(claims):
    sims_claimed = [c["sim"] for c in claims["claims"]]
    assert sorted(sims_claimed) == sorted(SIM_REGISTRY)


def test_claim_ids_are_unique(claims):
    ids = [c["id"] for c in claims["claims"]]
    assert len(ids) == len(set(ids))


def test_every_claim_has_the_required_fields(claims):
    required = {"id", "claim", "scope", "sim", "anchor", "morphism"}
    missing = [
        f"{c.get('id', '<no id>')}: missing {sorted(required - set(c))}"
        for c in claims["claims"]
        if not required <= set(c)
    ]
    assert not missing, "Incomplete claims:\n  " + "\n  ".join(missing)


def test_every_anchor_resolves_to_a_registry_equation(claims, equation_ids):
    """The whole point of an anchor is that it names a real node in the
    morphism graph — an anchor that does not resolve is a dangling claim."""
    dangling = [
        f"{c['id']}: anchor '{c['anchor']}' is not a registered equation"
        for c in claims["claims"]
        if c["anchor"] not in equation_ids
    ]
    assert not dangling, "Dangling claim anchors:\n  " + "\n  ".join(dangling)


def test_claims_are_rates_of_change(claims):
    """The claims schema says every entry is dX/dt under scope."""
    not_rates = [c["id"] for c in claims["claims"] if not c["claim"].startswith("d")]
    assert not not_rates, f"Claims that are not stated as rates: {not_rates}"
