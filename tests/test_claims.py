"""
tests/test_claims.py

Verify the compressed claim format (CLAIM_SCHEMA.py + CLAIM_TABLE.json +
.claims) is in sync with the registry. The generator generate_claims.py
must be deterministic; AI readers consume the committed files directly.

Run with:
    python -m pytest tests/test_claims.py -v
"""

import json
import os
import sys

import pytest

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, REPO)

from CLAIM_SCHEMA import (
    CLAIM_BIN_SIZE, CYCLE_ENUM,
    decode_claim, encode_claim, fnv1a_32,
    load_claims_file, parse_claims_line,
)
from physics_playground import EquationRegistry


CLAIMS_PATH = os.path.join(REPO, ".claims")
TABLE_PATH = os.path.join(REPO, "CLAIM_TABLE.json")


@pytest.fixture(scope="module")
def claims():
    return load_claims_file(CLAIMS_PATH)


@pytest.fixture(scope="module")
def table():
    with open(TABLE_PATH, encoding="utf-8") as fh:
        return json.load(fh)


@pytest.fixture(scope="module")
def registry():
    r = EquationRegistry()
    r._register_all()
    return r


class TestClaimsFile:

    def test_claims_file_exists(self):
        assert os.path.exists(CLAIMS_PATH)
        assert os.path.exists(TABLE_PATH)

    def test_one_claim_per_equation(self, claims, registry):
        """Every registered equation must have exactly one claim line."""
        ids = [c["id"] for c in claims]
        assert len(ids) == len(set(ids)), "Duplicate claim ids"
        assert set(ids) == set(registry._equations.keys()), (
            "Claim IDs don't match registry — re-run generate_claims.py"
        )

    def test_every_claim_has_required_fields(self, claims):
        required = {"id", "rate", "bounds", "cond", "rel", "fail", "meas", "cyc"}
        for c in claims:
            assert required.issubset(c.keys()), f"{c['id']} missing fields"
            assert c["rate"], f"{c['id']} has empty rate"
            assert len(c["bounds"]) == 3, f"{c['id']} bounds is not a 3-tuple"
            assert c["cyc"] in CYCLE_ENUM, f"{c['id']} cyc {c['cyc']} not in enum"

    def test_rel_targets_are_valid_claim_ids(self, claims):
        """Every coupled-claim id in `rel` must reference a real claim."""
        ids = {c["id"] for c in claims}
        for c in claims:
            for r in c["rel"]:
                assert r in ids, f"{c['id']} references unknown claim {r!r}"


class TestClaimTable:

    def test_table_categories_complete(self, table):
        for k in ("rates", "bounds", "cond", "rel", "fail", "meas"):
            assert k in table, f"CLAIM_TABLE.json missing category {k!r}"
            assert isinstance(table[k], list)

    def test_table_has_no_duplicates(self, table):
        for k, v in table.items():
            assert len(v) == len(set(v)), f"CLAIM_TABLE.json {k!r} has duplicates"

    def test_every_claim_field_resolvable_via_table(self, claims, table):
        """All values in claims must be present in CLAIM_TABLE."""
        rate_set = set(table["rates"])
        bounds_set = set(table["bounds"])
        cond_set = set(table["cond"])
        rel_set = set(table["rel"])
        fail_set = set(table["fail"])
        meas_set = set(table["meas"])
        for c in claims:
            assert c["rate"] in rate_set, f"{c['id']} rate not in table"
            assert ",".join(c["bounds"]) in bounds_set, f"{c['id']} bounds not in table"
            for v in c["cond"]: assert v in cond_set
            for v in c["rel"]:  assert v in rel_set
            for v in c["fail"]: assert v in fail_set
            for v in c["meas"]: assert v in meas_set


class TestRoundTrip:

    def test_parse_claims_line_round_trip(self, claims):
        """Re-emitting and re-parsing each claim produces the same dict."""
        for c in claims:
            line = "|".join([
                c["id"], c["rate"],
                ",".join(c["bounds"]),
                ",".join(c["cond"]),
                ",".join(c["rel"]),
                ",".join(c["fail"]),
                ",".join(c["meas"]),
                str(c["cyc"]),
            ])
            re_parsed = parse_claims_line(line)
            assert re_parsed == c, f"round-trip mismatch on {c['id']}"

    def test_binary_codec_round_trip(self, claims, table):
        """encode_claim/decode_claim survives a round-trip for a real claim."""
        # Pick claims that fit in 32-bit masks (≤32 unique values per category).
        rates_idx = {r: i for i, r in enumerate(table["rates"])}
        bounds_idx = {b: i for i, b in enumerate(table["bounds"])}
        cond_idx = {v: i for i, v in enumerate(table["cond"])}
        rel_idx = {v: i for i, v in enumerate(table["rel"])}
        fail_idx = {v: i for i, v in enumerate(table["fail"])}
        meas_idx = {v: i for i, v in enumerate(table["meas"])}

        def mask(items, idx_map):
            m = 0
            for v in items:
                i = idx_map[v]
                if i < 32:
                    m |= 1 << i
            return m

        # Use a claim whose all fields fit in 32 bits.
        pick = next(c for c in claims if c["id"] == "schrodinger_free")
        packed = {
            "id_hash":     fnv1a_32(pick["id"]),
            "rate_idx":    rates_idx[pick["rate"]],
            "bounds_idx":  bounds_idx[",".join(pick["bounds"])],
            "cond_mask":   mask(pick["cond"], cond_idx),
            "rel_mask":    mask([r for r in pick["rel"] if rel_idx[r] < 32], rel_idx),
            "fail_mask":   mask(pick["fail"], fail_idx),
            "meas_mask":   mask(pick["meas"], meas_idx),
            "cyc":         pick["cyc"],
        }
        blob = encode_claim(packed)
        assert len(blob) == CLAIM_BIN_SIZE

        id_lookup = {fnv1a_32(c["id"]): c["id"] for c in claims}
        decoded = decode_claim(blob, table, id_lookup)
        assert decoded["id"] == pick["id"]
        assert decoded["rate"] == pick["rate"]
        # CLAIM_SCHEMA stores bounds as a single joined string in the table
        # (indexed by a 2-byte bounds_idx, unlike the 32-bit mask categories).
        assert decoded["bounds"] == ",".join(pick["bounds"])
        assert decoded["cyc"] == CYCLE_ENUM[pick["cyc"]]


class TestDeterminism:

    def test_regenerator_is_deterministic(self):
        """generate_claims.py must produce byte-identical output on re-run."""
        import subprocess
        with open(CLAIMS_PATH, "rb") as fh:
            before = fh.read()
        with open(TABLE_PATH, "rb") as fh:
            before_table = fh.read()
        result = subprocess.run(
            [sys.executable, "generate_claims.py"],
            cwd=REPO, capture_output=True, text=True, timeout=60,
        )
        assert result.returncode == 0, result.stderr
        with open(CLAIMS_PATH, "rb") as fh:
            after = fh.read()
        with open(TABLE_PATH, "rb") as fh:
            after_table = fh.read()
        assert before == after, ".claims changed on re-run"
        assert before_table == after_table, "CLAIM_TABLE.json changed on re-run"
