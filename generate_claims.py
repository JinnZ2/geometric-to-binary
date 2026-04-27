"""
generate_claims.py

Convert this repo's EquationRegistry (90 equations) into the canonical
compressed claim format defined in CLAIM_SCHEMA.py.

Outputs:
  CLAIM_TABLE.json  — repo-level lookup (deduped rates / bounds / cond / rel / fail / meas)
  .claims           — pipe-delimited line per equation, one line each

Run: python generate_claims.py

Deterministic — running this on the same registry produces byte-identical
output. Re-run after registry changes; commit both .claims and
CLAIM_TABLE.json so AI readers can pull them without executing code.
"""

from __future__ import annotations

import json
import os
import re
from collections import OrderedDict

import sympy as sp

from physics_playground import EquationRegistry, PhysicsDomain
import graph as graph_module


REPO = os.path.dirname(os.path.abspath(__file__))


# ── LaTeX → compact ASCII ────────────────────────────────────────────────────

GREEK = {
    r"\alpha": "alpha", r"\beta": "beta", r"\gamma": "gamma", r"\delta": "delta",
    r"\epsilon": "eps", r"\varepsilon": "eps", r"\zeta": "zeta", r"\eta": "eta",
    r"\theta": "theta", r"\vartheta": "theta", r"\iota": "iota", r"\kappa": "kappa",
    r"\lambda": "lambda", r"\mu": "mu", r"\nu": "nu", r"\xi": "xi", r"\pi": "pi",
    r"\rho": "rho", r"\sigma": "sigma", r"\tau": "tau", r"\upsilon": "ups",
    r"\phi": "phi", r"\varphi": "phi", r"\chi": "chi", r"\psi": "psi", r"\omega": "omega",
    r"\Gamma": "Gamma", r"\Delta": "Delta", r"\Theta": "Theta", r"\Lambda": "Lambda",
    r"\Xi": "Xi", r"\Pi": "Pi", r"\Sigma": "Sigma", r"\Phi": "Phi", r"\Psi": "Psi",
    r"\Omega": "Omega",
}


def _expand_frac(s: str) -> str:
    """Replace \\frac{a}{b} with (a)/(b). Supports nested braces by walking
    the string and balancing braces manually (regex can't do this)."""
    out, i, n = [], 0, len(s)
    while i < n:
        if s.startswith(r"\frac", i):
            j = i + 5
            while j < n and s[j].isspace(): j += 1
            if j >= n or s[j] != "{":
                out.append(r"\frac"); i += 5; continue
            depth, k = 1, j + 1
            while k < n and depth:
                if s[k] == "{": depth += 1
                elif s[k] == "}": depth -= 1
                k += 1
            num = s[j + 1:k - 1]
            j = k
            while j < n and s[j].isspace(): j += 1
            if j >= n or s[j] != "{":
                out.append(r"\frac{" + num + "}"); i = j; continue
            depth, m = 1, j + 1
            while m < n and depth:
                if s[m] == "{": depth += 1
                elif s[m] == "}": depth -= 1
                m += 1
            den = s[j + 1:m - 1]
            out.append(f"({_expand_frac(num)})/({_expand_frac(den)})")
            i = m
        else:
            out.append(s[i]); i += 1
    return "".join(out)


# LaTeX commands we want to preserve as bare identifiers (must run before the
# "drop unknown \word" sweep at the end).
KEEP_AS_NAME = {
    r"\cos": "cos", r"\sin": "sin", r"\tan": "tan",
    r"\sec": "sec", r"\csc": "csc", r"\cot": "cot",
    r"\sinh": "sinh", r"\cosh": "cosh", r"\tanh": "tanh",
    r"\arcsin": "asin", r"\arccos": "acos", r"\arctan": "atan",
    r"\log": "log", r"\ln": "ln", r"\exp": "exp",
    r"\min": "min", r"\max": "max",
    r"\det": "det", r"\Tr": "Tr", r"\tr": "tr",
    r"\Re": "Re", r"\Im": "Im",
    r"\sum": "sum", r"\prod": "prod", r"\int": "int",
}

RELATIONAL = {
    r"\propto": "~prop", r"\sim": "~", r"\approx": "~",
    r"\to":     "->",     r"\rightarrow": "->", r"\leftarrow": "<-",
    r"\Leftrightarrow": "<=>",
    r"\geq":    ">=",     r"\ge": ">=",
    r"\leq":    "<=",     r"\le": "<=",
    r"\neq":    "!=",     r"\ne": "!=",
    r"\pm":     "+-",     r"\mp": "-+",
    r"\infty":  "inf",
    r"\equiv":  "==",
}


def latex_to_compact(s: str) -> str:
    """LaTeX → compact ASCII. Best-effort; never raises.
    Output is guaranteed ASCII-safe for the pipe-delimited .claims format
    (no literal `|` or `,` survives in the rate string)."""
    # Whitespace / spacing
    s = s.replace(r"\,", "").replace(r"\;", "").replace(r"\!", "")
    s = s.replace(r"\quad", " ").replace(r"\qquad", " ")
    s = s.replace(r"\left", "").replace(r"\right", "")
    # \| is LaTeX for parallel (‖). Replace BEFORE \\ unknown-command sweep
    # so it doesn't confuse the pipe-delimited line format.
    s = s.replace(r"\|", "~par~").replace(r"\parallel", "~par~")

    # Constants & operators
    s = s.replace(r"\hbar", "hbar").replace(r"\Box", "box")
    s = s.replace(r"\cdot", "*").replace(r"\times", "*")
    s = s.replace(r"\nabla^2", "lap").replace(r"\nabla", "grad")
    s = s.replace(r"\partial", "d")

    # Relational / comparison operators
    for k, v in RELATIONAL.items():
        s = s.replace(k, v)

    # Named functions to keep
    for k, v in KEEP_AS_NAME.items():
        s = s.replace(k, v)

    # \frac with nested-brace support
    s = _expand_frac(s)

    # Decorated derivatives
    s = re.sub(r"\\dot\{([^{}]+)\}", r"d\1/dt", s)
    s = re.sub(r"\\ddot\{([^{}]+)\}", r"d2\1/dt2", s)
    s = re.sub(r"\\bar\{([^{}]+)\}", r"\1bar", s)
    s = re.sub(r"\\tilde\{([^{}]+)\}", r"\1tilde", s)
    s = re.sub(r"\\hat\{([^{}]+)\}", r"\1hat", s)
    s = re.sub(r"\\sqrt\{([^{}]*)\}", r"sqrt(\1)", s)

    # Greek (last so we don't mis-prefix e.g. \rightarrow → r-arrow)
    for k, v in GREEK.items():
        s = s.replace(k, v)

    # Sub/superscripts: keep multi-char in parens, single char inline
    s = re.sub(r"\^\{([^{}]+)\}", r"^(\1)", s)
    s = re.sub(r"_\{([^{}]+)\}", r"_(\1)", s)

    # Stray escaped chars / drop unknown commands
    s = s.replace(r"\(", "(").replace(r"\)", ")")
    s = s.replace(r"\[", "[").replace(r"\]", "]")
    s = re.sub(r"\\[a-zA-Z]+", "", s)
    s = s.replace("{", "").replace("}", "")
    s = re.sub(r"\s+", "", s)

    # Second-derivative cleanup
    s = re.sub(r"d\^\(2\)\s*([A-Za-z])", r"d2\1", s)
    s = re.sub(r"d\^2\s*([A-Za-z])", r"d2\1", s)
    s = re.sub(r"d\s+([A-Za-z])", r"d\1", s)
    # Final sanitize: the .claims format uses `|` as field sep and `,` as
    # in-field list sep. Any literal that survived must be neutralized.
    s = s.replace("|", "~").replace(",", ";")
    return s


# ── Field extractors ─────────────────────────────────────────────────────────

# Domain → cycle-class enum (CLAIM_SCHEMA.CYCLE_ENUM)
DOMAIN_CYC = {
    "quantum": 0, "electromagnetism": 0, "optics": 0, "nuclear_physics": 0,
    "condensed_matter": 0, "classical_mechanics": 0, "relativity": 0,
    "general_relativity": 0, "statistical": 0, "thermodynamics": 0,
    "fluid_dynamics": 0, "plasma_physics": 0, "acoustics": 0, "biophysics": 0,
    "nonlinear_dynamics": 0, "information_theory": 0, "high_energy_string": 0,
    "molecular_biology": 0,
    "neuroscience":        1,   # diurnal: circadian / sleep cycles
    "ecology_systems":     2,   # seasonal
    "population_dynamics": 3,   # annual reproductive cycles
    "astrophysics":        5,   # century-scale stellar evolution
    "cosmology":           6,   # geologic / cosmological
    "custom":              0,
}

# Domain → bounds[2] scale label
DOMAIN_SCALE = {
    "quantum": "quantum", "electromagnetism": "EM_field", "optics": "optical",
    "nuclear_physics": "nuclear", "condensed_matter": "lattice",
    "classical_mechanics": "classical", "relativity": "relativistic",
    "general_relativity": "spacetime", "statistical": "ensemble",
    "thermodynamics": "thermo", "fluid_dynamics": "fluid",
    "plasma_physics": "plasma", "acoustics": "acoustic",
    "biophysics": "biological", "nonlinear_dynamics": "nonlinear",
    "information_theory": "info", "high_energy_string": "stringy",
    "molecular_biology": "molecular", "neuroscience": "neural",
    "ecology_systems": "ecosystem", "population_dynamics": "population",
    "astrophysics": "stellar", "cosmology": "cosmological", "custom": "custom",
}


def extract_bounds(eq, latex_compact: str) -> list[str]:
    """3-tuple [spatial, temporal, scale]."""
    has_t = "/dt" in latex_compact or "/(dt)" in latex_compact
    has_x = "/dx" in latex_compact or "/(dx)" in latex_compact
    has_r = "/dr" in latex_compact
    has_lap = "lap(" in latex_compact or "grad" in latex_compact

    if has_lap or has_x or has_r:
        spatial = "field"
    elif "(x" in latex_compact or "(r" in latex_compact:
        spatial = "field"
    else:
        spatial = "scalar"

    temporal = "t" if has_t else "stationary"
    scale = DOMAIN_SCALE.get(eq.domain.value, eq.domain.value)
    return [spatial, temporal, scale]


def extract_meas(eq) -> list[str]:
    """Observables: free symbols and functions appearing in the SymPy expr."""
    expr = eq.symbolic_expr
    if expr is None:
        return []
    symbols = set()
    # Free symbols (constants and parameters)
    for sym in expr.free_symbols:
        symbols.add(str(sym))
    # Applied functions like psi(x, t) — record the head name
    for f in expr.atoms(sp.Function):
        symbols.add(str(type(f).__name__))
    # Drop standard constants
    drop = {"hbar", "c", "G", "k_B", "kB", "m", "M", "pi", "e",
            "x", "t", "r", "k", "n"}  # also drop common indep vars
    symbols = sorted(s for s in symbols if s not in drop)
    return symbols[:6]                   # cap at 6 for compactness


def extract_rel(eq, G) -> list[str]:
    """Coupled claim ids = morphism graph successors."""
    if eq.name not in G.nodes:
        return []
    return sorted(G.successors(eq.name))


def extract_cond(eq) -> list[str]:
    """Domain-derived constraint stub. Future: pull from eq.symbolic constraints."""
    return [f"domain={eq.domain.value}"]


def extract_fail(eq, latex_compact: str) -> list[str]:
    """invalid_if conditions — heuristic stubs we can refine later."""
    fails = []
    # Equations defined on bounded ranges
    if "f_dirac" in eq.name or "fermi" in eq.name or "bose" in eq.name:
        fails.append("T_le_0")
    if "schwarzschild" in eq.name or "kerr" in eq.name or "friedmann" in eq.name:
        fails.append("singularity_r_eq_rs")
    if "lorenz" in eq.name:
        fails.append("integrator_stiff")
    if eq.domain == PhysicsDomain.QUANTUM:
        fails.append("classical_limit_hbar_to_0")
    if eq.domain == PhysicsDomain.RELATIVITY:
        fails.append("v_ge_c")
    if eq.domain == PhysicsDomain.GENERAL_RELATIVITY:
        fails.append("flat_spacetime_limit")
    if eq.domain == PhysicsDomain.POPULATION_DYNAMICS:
        fails.append("N_lt_0")
    return fails or ["form_invalid"]


# ── Build & write ────────────────────────────────────────────────────────────

def build_claims(registry: EquationRegistry, eq_graph) -> list[dict]:
    G = eq_graph.G
    claims = []
    for name in sorted(registry._equations.keys()):
        eq = registry.get(name)
        rate = latex_to_compact(eq.latex)
        bounds = extract_bounds(eq, rate)
        cond = extract_cond(eq)
        rel = extract_rel(eq, G)
        fail = extract_fail(eq, rate)
        meas = extract_meas(eq)
        cyc = DOMAIN_CYC.get(eq.domain.value, 0)
        claims.append({
            "id":     name,
            "rate":   rate,
            "bounds": bounds,
            "cond":   cond,
            "rel":    rel,
            "fail":   fail,
            "meas":   meas,
            "cyc":    cyc,
        })
    return claims


def build_table(claims: list[dict]) -> dict:
    """Deduped repo-level lookup. Lists preserve insertion order."""
    table = {k: [] for k in ("rates", "bounds", "cond", "rel", "fail", "meas")}
    seen = {k: OrderedDict() for k in table}

    def add(category: str, value: str):
        if value not in seen[category]:
            seen[category][value] = len(seen[category])
            table[category].append(value)

    for c in claims:
        add("rates", c["rate"])
        # bounds is the 3-tuple joined
        add("bounds", ",".join(c["bounds"]))
        for v in c["cond"]:  add("cond", v)
        for v in c["rel"]:   add("rel", v)
        for v in c["fail"]:  add("fail", v)
        for v in c["meas"]:  add("meas", v)
    return table


def write_claims_file(claims: list[dict], path: str) -> None:
    lines = [
        "# .claims — pipe-delimited differential schema (CLAIM_SCHEMA.py)",
        "# id|rate|bounds|cond|rel|fail|meas|cyc",
    ]
    for c in claims:
        lines.append("|".join([
            c["id"],
            c["rate"],
            ",".join(c["bounds"]),
            ",".join(c["cond"]),
            ",".join(c["rel"]),
            ",".join(c["fail"]),
            ",".join(c["meas"]),
            str(c["cyc"]),
        ]))
    with open(path, "w", encoding="utf-8") as fh:
        fh.write("\n".join(lines) + "\n")


def main() -> None:
    r = EquationRegistry(); r._register_all()
    G = graph_module.build_morphism_graph(r)

    claims = build_claims(r, G)
    table = build_table(claims)

    table_path = os.path.join(REPO, "CLAIM_TABLE.json")
    claims_path = os.path.join(REPO, ".claims")

    with open(table_path, "w", encoding="utf-8") as fh:
        json.dump(table, fh, indent=2, ensure_ascii=False)
        fh.write("\n")
    write_claims_file(claims, claims_path)

    print(f"  wrote {table_path}  ({sum(len(v) for v in table.values())} total entries across categories)")
    print(f"  wrote {claims_path} ({len(claims)} claims)")
    # Quick sanity peek
    for c in claims[:3]:
        print(f"    sample: {c['id']:25s} rate={c['rate'][:60]}")


if __name__ == "__main__":
    main()
