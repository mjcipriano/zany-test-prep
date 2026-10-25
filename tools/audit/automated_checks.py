#!/usr/bin/env python3
"""Deterministic answer-key checks over every question in the shipped bundles.

Usage (from the repo root)::

    python tools/audit/automated_checks.py                 # both exams, summary
    python tools/audit/automated_checks.py --exam sat --examples 5
    python tools/audit/automated_checks.py --json out.json # full machine report
    python tools/audit/automated_checks.py --strict        # exit 1 on any failure

Checks (each question gets every check that applies to it):

``structure``       exactly one correct choice; its id is among the choices;
                    ids unique. Grid-ins: answer value numeric, every accepted
                    form parses and equals the value.
``choices``         choice texts unique after normalisation, and no two
                    numeric choices with the same value (two right answers).
``rationale``       a wrong choice's rationale must not start "Correct"; the
                    keyed choice's must not start "Incorrect"/"Wrong".
``arithmetic``      every pure-arithmetic "a = b" claim in the explanation
                    and answer_verification is true (display rounding allowed).
``final_value``     the explanation's final stated value equals the keyed
                    answer when both are numbers.
``verification``    answer_verification agrees with the key ("val=13",
                    "3x + 26 = 50 at x=8", ...).
``resolve``         an independent re-solve of the stem (tools/audit/solvers.py)
                    agrees with the key and no other choice is also right.
``dup_distractors`` (warning only) two wrong choices with the same value.

Results are grouped by exam and generator family (the ``family:<name>`` tag;
authored items without one are grouped as ``(authored)``).
"""
from __future__ import annotations

import argparse
import json
import re
import sys
from fractions import Fraction
from pathlib import Path
from typing import Dict, List, Optional, Tuple

if __package__ in (None, ""):
    sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
    from audit import solvers  # type: ignore  # noqa: E402
    from audit.expr import ExprError, evaluate, holds, num_equal, parse_number  # type: ignore  # noqa: E402
else:
    from . import solvers
    from .expr import ExprError, evaluate, holds, num_equal, parse_number

ROOT = Path(__file__).resolve().parents[2]
BUNDLE_DIR = ROOT / "assets" / "content"
EXAMS = ("sat", "act")
CHECKS = ("structure", "choices", "rationale", "arithmetic", "final_value",
          "verification", "resolve", "dup_distractors")
# Item-quality findings that don't make the key wrong: reported, but they don't
# count a question as failed.
WARN_CHECKS = ("dup_distractors",)

_ERRORS = (ExprError, ZeroDivisionError, OverflowError, ValueError, TypeError,
           RecursionError, IndexError, KeyError)

PASS, SKIP = "pass", "skip"


def family(q: dict) -> str:
    for t in q.get("tags") or []:
        if isinstance(t, str) and t.startswith("family:"):
            return t[len("family:"):]
    return "(authored)"


def keyed_text(q: dict) -> Optional[str]:
    """The text of the keyed answer (choice text, or the grid-in value)."""
    if q.get("question_type") == "student_produced":
        ans = q.get("answer") or {}
        acc = ans.get("accepted") or []
        return str(acc[0]) if acc else str(ans.get("value"))
    for c in q.get("choices") or []:
        if c.get("id") == q.get("correct_choice"):
            return c.get("text")
    return None


def keyed_value(q: dict):
    """Numeric value of the keyed answer, or None if it isn't a number."""
    if q.get("question_type") == "student_produced":
        v = (q.get("answer") or {}).get("value")
        if isinstance(v, bool) or not isinstance(v, (int, float)):
            return parse_number(str(v)) if v is not None else None
        acc = [parse_number(a) for a in (q.get("answer") or {}).get("accepted", [])]
        exact = [a for a in acc if isinstance(a, Fraction) and num_equal(a, v)]
        return exact[0] if exact else (Fraction(v) if isinstance(v, int) else v)
    t = keyed_text(q)
    return parse_number(t) if t is not None else None


# --------------------------------------------------------------------------
# individual checks: each returns PASS, SKIP or a failure message (str)


def check_structure(q: dict):
    if q.get("question_type") == "student_produced":
        ans = q.get("answer")
        if not isinstance(ans, dict):
            return "student_produced item has no answer object"
        if q.get("choices"):
            return "student_produced item also carries choices"
        if ans.get("type") != "numeric":
            return SKIP
        v = ans.get("value")
        if isinstance(v, bool) or not isinstance(v, (int, float)):
            return f"answer value {v!r} is not numeric"
        acc = ans.get("accepted") or []
        if not acc:
            return "no accepted answer forms"
        tol = max(float(ans.get("tolerance") or 0), 1e-6)
        for a in acc:
            av = parse_number(a)
            if av is None:
                return f"accepted form {a!r} does not parse"
            if abs(float(av) - float(v)) > tol * max(1.0, abs(float(v))):
                return f"accepted form {a!r} != value {v}"
        return PASS
    choices = q.get("choices") or []
    ids = [c.get("id") for c in choices]
    if len(choices) < 2:
        return "fewer than two choices"
    if len(set(ids)) != len(ids):
        return f"duplicate choice ids {ids}"
    cc = q.get("correct_choice")
    if not cc:
        return "no correct_choice"
    if ids.count(cc) != 1:
        return f"correct_choice {cc!r} not exactly once among {ids}"
    return PASS


def _norm_choice(t: str) -> str:
    s = str(t).lower().replace("−", "-").replace("–", "-").replace("’", "'")
    s = re.sub(r"\s+", " ", s).strip().rstrip(".")
    return s


def check_choices(q: dict):
    choices = q.get("choices") or []
    if not choices:
        return SKIP
    seen: Dict[str, str] = {}
    for c in choices:
        k = _norm_choice(c.get("text", ""))
        if k in seen:
            return f"choices {seen[k]} and {c['id']} have the same text {c['text']!r}"
        seen[k] = c["id"]
    cc = q.get("correct_choice")
    for a, b in _equal_value_pairs(choices):
        if cc in (a, b):
            return f"choices {a} and {b} have the same value (both correct)"
    return PASS


# A choice "is a value" (rather than a form such as "5.6 × 10^-4" or "3 × 31",
# where the question is about the form) when it is a single number, fraction,
# decimal, percent or radical/π multiple.
_SIMPLE_VALUE = re.compile(r"\$?[−-]?(?:\d[\d,]*(?:\.\d+)?)?(?:/\d+)?%?(?:√\d+|π)?(?:/\d+)?")


def _equal_value_pairs(choices) -> List[Tuple[str, str]]:
    vals = []
    for c in choices:
        t = str(c.get("text", "")).strip()
        if not _SIMPLE_VALUE.fullmatch(t) or not re.search(r"\d", t):
            continue
        v = parse_number(t)
        if v is not None:
            vals.append((c["id"], v))
    return [(vals[a][0], vals[b][0]) for a in range(len(vals)) for b in range(a + 1, len(vals))
            if num_equal(vals[a][1], vals[b][1], 1e-9)]


def check_dup_distractors(q: dict):
    choices = q.get("choices") or []
    if not choices:
        return SKIP
    cc = q.get("correct_choice")
    for a, b in _equal_value_pairs(choices):
        if cc not in (a, b):
            return f"distractors {a} and {b} have the same value"
    return PASS


_CORRECT_START = re.compile(r"^\W*correct\b(?!ly)", re.I)
_WRONG_START = re.compile(r"^\W*(incorrect|wrong|not correct|this is wrong|false)\b", re.I)


def check_rationale(q: dict):
    choices = q.get("choices") or []
    if not choices:
        return SKIP
    cc = q.get("correct_choice")
    for c in choices:
        r = str(c.get("rationale") or "")
        if c.get("id") != cc and _CORRECT_START.search(r):
            return f"wrong choice {c['id']} has rationale {r[:60]!r}"
        if c.get("id") == cc and _WRONG_START.search(r):
            return f"keyed choice {c['id']} has rationale {r[:60]!r}"
    return PASS


# ---- arithmetic claims ----------------------------------------------------

_ARITH = set("0123456789 +-−–×·÷/*^()|.%²³√π⅓½")
_LEAD_OK = set("0123456789(|√π−-⅓½.")


# Words that may directly precede a complete arithmetic left-hand side
# ("from 61 − 9 = 52", "total 12 × 4 = 48"). Any other word might be an
# operator the scan can't see ("log 10", "mod 8", "least 11").
_PROSE_BEFORE = {"from", "to", "is", "are", "so", "then", "gives", "giving", "equals", "total",
                 "totals", "area", "perimeter", "volume", "sum", "product", "difference",
                 "and", "compute", "computes", "becomes", "makes", "yields", "get", "gets"}


def _prep(text: str) -> str:
    s = text.replace("$", "")
    s = re.sub(r"(?<=\d),(?=\d{3}(?!\d))", "", s)
    s = re.sub(r"\.(?!\d)|(?<!\d)\.", ";", s)  # sentence periods are not decimals
    s = re.sub(r"(\d%|\d/\d+|\))\s+of\s+(?=[\d(−-])", r"\1 × ", s)  # "5% of 405", not "47 of 137"
    return s


def arith_claims(text: str) -> List[Tuple[str, str]]:
    """Pure-arithmetic ``lhs = rhs`` pairs stated in prose (no variables)."""
    s = _prep(text)
    out = []
    for m in re.finditer(r"(?<![<>!=≠≤≥])=(?!=)", s):
        i = m.start()
        j = i
        while j > 0 and s[j - 1] in _ARITH:
            j -= 1
        k = i + 1
        while k < len(s) and s[k] in _ARITH:
            k += 1
        left, right = s[j:i], s[i + 1:k]
        ls, rs = left.strip(), right.strip()
        if not ls or not rs or not re.search(r"\d", ls) or not re.search(r"\d", rs):
            continue
        stop_l = s[j - 1] if j > 0 else ""
        stop_r = s[k] if k < len(s) else ""
        if stop_l and (stop_l.isalnum() or stop_l in "_′'"):
            if not left.startswith(" ") or ls[0] in "+-−–×·÷/*^%)":
                continue  # glued to, or continuing, a variable ("f(3) = ", "2x − 5 = ")
            word = re.search(r"([A-Za-z]+)$", s[:j].rstrip())
            if not word or word.group(1).lower() not in _PROSE_BEFORE:
                continue  # "log 10 = …", "least 11 = …", "mod 8 = …": the word is math
        if (stop_l == ":" and j > 1 and s[j - 2].isdigit()) or \
                (stop_r == ":" and k + 1 < len(s) and s[k + 1].isdigit()):
            continue  # ratios "42:22 = 21:11"
        if stop_r == "°" and "π" in ls:
            continue  # "7π/6 = 210°" is a unit conversion
        if ls[0] not in _LEAD_OK:
            continue
        if stop_r and (stop_r.isalnum() or stop_r in "_′'") and not right.endswith(" "):
            continue  # "= 6x", "= 15i"
        if rs[-1] in "+-−–×·÷/*^(":
            continue
        out.append((ls, rs))
    return out


def _decimals(s: str) -> Optional[int]:
    m = re.fullmatch(r"−?-?\d+\.(\d+)%?", s.strip())
    return len(m.group(1)) if m else None


def claim_holds(lhs: str, rhs: str) -> Optional[bool]:
    try:
        a, b = evaluate(lhs), evaluate(rhs)
    except _ERRORS:
        return None
    if num_equal(a, b):
        return True
    # "450/900 × 100 = 50%": the % is a label on a number already scaled by 100
    if rhs.endswith("%") and num_equal(a, b * 100) or lhs.endswith("%") and num_equal(a * 100, b):
        return True
    for side, other in ((rhs, a), (lhs, b)):
        d = _decimals(side)
        if d is not None:
            shown = float(evaluate(side))
            if abs(float(other) - shown) <= 10 ** (-d) * 1.0000001:
                return True  # display rounding / truncation
    if re.search(r"[√π]", lhs + rhs) and abs(float(a) - float(b)) < 0.05 * max(1, abs(float(a))):
        return True if re.search(r"\.\d", lhs + rhs) else None
    return False


def check_arithmetic(q: dict):
    texts = [("explanation", q.get("explanation") or "")]
    if q.get("answer_verification"):
        texts.append(("answer_verification", q["answer_verification"]))
    any_claim = False
    for where, text in texts:
        for lhs, rhs in arith_claims(text):
            ok = claim_holds(lhs, rhs)
            if ok is None:
                continue
            any_claim = True
            if not ok:
                return f"{where} claims {lhs} = {rhs}"
    return PASS if any_claim else SKIP


# ---- final stated value ---------------------------------------------------

_STOP_WORDS = {"and", "or", "of", "the", "to", "when", "if", "is", "so", "then",
               "for", "than", "in", "at", "by", "with", "from", "not", "but", "less",
               "more", "times", "a", "an", "each", "per", "on", "as", "out", "which",
               "remain", "remaining", "left", "has", "have", "since", "because", "while",
               "does", "do", "gives", "makes", "satisfies", "would", "will", "can"}
_VAL = r"\$?[−–-]?(?:\d{1,3}(?:,\d{3})+|\d+)(?:\.\d+)?(?:/\d+)?%?(?:√\d+|π)?"
_FINAL = re.compile(r"(?:=|≈|:|\bis|\bare|\bbe|→|\bgives|\bequals|\bof)\s*(" + _VAL + r")\s*(°|[A-Za-z][A-Za-z ]{0,30})?$")


def final_value(expl: str):
    """The value an explanation ends on ("… = 48.", "The greatest is 9."), else None."""
    s = expl.strip()
    for _ in range(2):
        s = re.sub(r"\s*\([^()]*\)\s*\.?\s*$", "", s)
    s = s.rstrip(". ")
    m = _FINAL.search(s)
    if not m:
        return None
    tail = (m.group(2) or "").strip()
    sign = 1
    if re.fullmatch(r"(?:decrease|drop|reduction|decline)", tail.lower()):
        sign, tail = -1, ""  # "≈ 80% decrease" states −80%
    if tail and tail != "°":
        words = tail.lower().split()
        if len(words) > 3 or words[0] in _STOP_WORDS or any(w in ("and", "or", "than") for w in words):
            return None
    v = parse_number(m.group(1))
    return None if v is None else sign * v


_STATED = re.compile(r"(?:=|≈|:|\bis|\bare|→|\bgives|\bequals)\s*(" + _VAL + r")")


def stated_values(expl: str) -> list:
    """Every value the explanation states as a result ("= 27", "is 3", ": 9")."""
    out = []
    for m in _STATED.finditer(expl):
        v = parse_number(m.group(1))
        if v is not None:
            out.append(v)
    return out


def check_final_value(q: dict):
    """The explanation must land on the key. When its last stated value is a
    different number, the key must at least be stated as a result somewhere
    (explanations often go on to the other coordinate, the other root, ...)."""
    kv = keyed_value(q)
    if kv is None:
        return SKIP
    expl = q.get("explanation") or ""
    fv = final_value(expl)
    if fv is None:
        return SKIP
    if matches_key(q, fv, kv) or any(matches_key(q, v, kv) for v in stated_values(expl)):
        return PASS
    other = [c["id"] for c in q.get("choices") or []
             if c["id"] != q.get("correct_choice") and parse_number(c["text"]) is not None
             and num_equal(parse_number(c["text"]), fv)]
    hint = f" (= choice {other[0]})" if other else ""
    return f"explanation ends on {solvers._fmt(fv)}{hint} but key is {keyed_text(q)!r}"


def _has_cents(q):
    return any("$" in c.get("text", "") for c in q.get("choices") or [])


_ROUND_WORDS = {"hundredth": 2, "tenth": 1, "thousandth": 3, "whole number": 0,
                "integer": 0, "whole": 0, "cent": 2}


def rounding_places(q) -> Optional[int]:
    """Decimal places the stem asks the answer to be rounded to, if any."""
    m = re.search(r"(?:round|rounded)[^.?]*?nearest (hundredth|tenth|thousandth|whole number|integer|whole|cent)",
                  q.get("prompt") or "", re.I)
    return _ROUND_WORDS[m.group(1).lower()] if m else None


def matches_key(q, value, kv) -> bool:
    """``value`` (exact) agrees with the keyed value ``kv`` as the stem shows it."""
    if num_equal(value, kv):
        return True
    places = rounding_places(q)
    if places is None and _has_cents(q):
        places = 2
    if places is not None:
        return abs(round(float(value), places) - float(kv)) <= 0.5 * 10 ** -places + 1e-9
    return False


# ---- answer_verification --------------------------------------------------

_VAL_KEYS = ("val",)


def check_verification(q: dict):
    v = (q.get("answer_verification") or "").strip()
    if not v:
        return SKIP
    kv = keyed_value(q)
    m = re.fullmatch(r"(.+?=.+?) at ([a-z])=(" + _VAL + r")", v) or \
        re.fullmatch(r"([a-z])=(" + _VAL + r") (?:satisfies|in) (.+)", v)
    if m:
        if m.group(1).count("=") == 1 and len(m.groups()) == 3 and " at " in v:
            eq, var, val = m.group(1), m.group(2), m.group(3)
        else:
            var, val, eq = m.group(1), m.group(2), m.group(3)
        x = parse_number(val)
        try:
            ok = holds(eq, {var: x})
        except _ERRORS:
            ok = None
        if ok is False:
            return f"verification {v!r}: {var}={val} does not satisfy the equation"
        if kv is not None and x is not None and not num_equal(x, kv) and \
                re.search(r"value of " + var + r"\b|solution to", q.get("prompt", "")):
            return f"verification solves {var}={val} but key is {keyed_text(q)!r}"
        return PASS if ok else SKIP
    m = re.search(r"\b(?:" + "|".join(_VAL_KEYS) + r")=(" + _VAL + r")\s*$", v)
    if m and kv is not None:
        x = parse_number(m.group(1))
        if x is None:
            return SKIP
        if matches_key(q, x, kv):
            return PASS
        return f"verification {v!r} but key is {keyed_text(q)!r}"
    return SKIP


# ---- independent re-solve -------------------------------------------------


def check_resolve(q: dict):
    exp = solvers.expectation(q)
    if exp is None:
        return SKIP
    if exp.kind == "number" and exp.places is None:
        exp.places = rounding_places(q)
    status, msg = solvers.grade(q, exp)
    if status == "fail":
        return msg
    return PASS if status == "pass" else SKIP


CHECK_FNS = {
    "structure": check_structure,
    "choices": check_choices,
    "rationale": check_rationale,
    "arithmetic": check_arithmetic,
    "final_value": check_final_value,
    "verification": check_verification,
    "resolve": check_resolve,
    "dup_distractors": check_dup_distractors,
}


def run_checks(q: dict) -> Dict[str, object]:
    """{check name: PASS | SKIP | failure message} for one question."""
    out: Dict[str, object] = {}
    for name, fn in CHECK_FNS.items():
        try:
            out[name] = fn(q)
        except _ERRORS as e:  # a checker bug must not hide the rest
            out[name] = SKIP
            out.setdefault("_errors", []).append(f"{name}: {e!r}")  # type: ignore[union-attr]
    return out


# --------------------------------------------------------------------------
# report


def load_questions(exam: str, bundle_dir: Path = BUNDLE_DIR) -> List[dict]:
    data = json.loads((bundle_dir / f"{exam}.bundle.json").read_text())
    return data["questions"]


def audit(exams=EXAMS, bundle_dir: Path = BUNDLE_DIR, examples: int = 3,
          questions_by_exam: Optional[Dict[str, List[dict]]] = None) -> dict:
    fams: Dict[Tuple[str, str], dict] = {}
    totals = {c: {"applied": 0, "failed": 0} for c in CHECKS}
    for exam in exams:
        qs = (questions_by_exam or {}).get(exam) or load_questions(exam, bundle_dir)
        for q in qs:
            key = (exam, family(q))
            f = fams.setdefault(key, {"exam": exam, "family": key[1], "domain": q.get("domain"),
                                      "checked": 0, "failed": 0,
                                      "by_check": {c: {"applied": 0, "failed": 0} for c in CHECKS},
                                      "warnings": 0, "examples": [], "warning_examples": []})
            f["checked"] += 1
            res = run_checks(q)
            failed = False
            for c in CHECKS:
                r = res.get(c, SKIP)
                if r == SKIP:
                    continue
                f["by_check"][c]["applied"] += 1
                totals[c]["applied"] += 1
                if r != PASS:
                    if c in WARN_CHECKS:
                        f["warnings"] += 1
                        totals[c]["failed"] += 1
                        if len(f["warning_examples"]) < examples:
                            f["warning_examples"].append({"question_id": q.get("question_id"),
                                                          "check": c, "message": r})
                        continue
                    failed = True
                    f["by_check"][c]["failed"] += 1
                    totals[c]["failed"] += 1
                    if len(f["examples"]) < examples:
                        f["examples"].append({"question_id": q.get("question_id"), "check": c,
                                              "message": r})
            if failed:
                f["failed"] += 1
    fam_list = sorted(fams.values(), key=lambda f: (-f["failed"], f["exam"], f["family"]))
    return {
        "questions": sum(f["checked"] for f in fam_list),
        "failed_questions": sum(f["failed"] for f in fam_list),
        "checks": totals,
        "families": fam_list,
    }


def format_report(rep: dict, show_all: bool = False) -> str:
    lines = [f"Audited {rep['questions']} questions; {rep['failed_questions']} failed at least one check.",
             "", "Per check (applied / failed):"]
    for c, t in rep["checks"].items():
        lines.append(f"  {c:<13} {t['applied']:>6} / {t['failed']}")
    failing = [f for f in rep["families"] if f["failed"]]
    lines += ["", f"Families with failures: {len(failing)} of {len(rep['families'])}"]
    for f in failing:
        lines.append(f"  {f['exam']}:{f['family']}  checked {f['checked']}, failed {f['failed']}")
        for ex in f["examples"]:
            lines.append(f"      [{ex['check']}] {ex['question_id']}: {ex['message']}")
    warned = [f for f in rep["families"] if f["warnings"]]
    lines += ["", f"Families with warnings: {len(warned)}"]
    for f in sorted(warned, key=lambda f: -f["warnings"]):
        lines.append(f"  {f['exam']}:{f['family']}  {f['warnings']} warning(s)")
        for ex in f["warning_examples"][:1]:
            lines.append(f"      [{ex['check']}] {ex['question_id']}: {ex['message']}")
    if show_all:
        lines += ["", "All families (checked / failed / resolve applied):"]
        for f in sorted(rep["families"], key=lambda f: (f["exam"], f["family"])):
            lines.append(f"  {f['exam']}:{f['family']:<28} {f['checked']:>5} {f['failed']:>4} "
                         f"{f['by_check']['resolve']['applied']:>5}")
    return "\n".join(lines)


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    ap.add_argument("--exam", choices=EXAMS, action="append")
    ap.add_argument("--bundle-dir", type=Path, default=BUNDLE_DIR)
    ap.add_argument("--examples", type=int, default=3, help="examples kept per family")
    ap.add_argument("--json", type=Path, help="write the full report as JSON here")
    ap.add_argument("--all", action="store_true", help="also list every family")
    ap.add_argument("--strict", action="store_true", help="exit 1 if anything fails")
    args = ap.parse_args(argv)
    rep = audit(tuple(args.exam or EXAMS), args.bundle_dir, args.examples)
    print(format_report(rep, args.all))
    if args.json:
        args.json.write_text(json.dumps(rep, indent=1))
    return 1 if args.strict and rep["failed_questions"] else 0


if __name__ == "__main__":
    sys.exit(main())
