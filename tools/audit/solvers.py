"""Independent re-solvers for common math stems.

Each solver reads ONLY what a student sees (prompt + choice texts; never the
explanation, rationales, family tag or answer_verification) and returns an
:class:`Expect` describing the right answer, or None when the stem is not a
form it recognises. Solvers are keyed on the wording of the stem, not on the
generator family, so they stay an independent check on the generators.

``Expect`` comes in two shapes:

* ``Expect.number(v)`` - the answer is the number ``v``; a choice is right iff
  :func:`expr.parse_number` of its text equals ``v``.
* ``Expect.predicate(fn)`` - ``fn(choice_text)`` returns True/False (or None
  when the choice can't be judged) for each option.

:func:`grade` turns an Expect into pass / fail / skip for a question.
"""
from __future__ import annotations

import math
import re
from dataclasses import dataclass
from fractions import Fraction
from typing import Callable, Dict, List, Optional, Sequence

from .expr import (ExprError, Num, Poly, evaluate, holds, normalize, num_equal, parse,
                   parse_equation, parse_number, solve_linear_system, solve_univariate)

_ERRORS = (ExprError, ZeroDivisionError, OverflowError, ValueError, KeyError,
           IndexError, TypeError, RecursionError)


@dataclass
class Expect:
    kind: str                     # "number" | "predicate"
    desc: str
    value: Optional[Num] = None
    pred: Optional[Callable[[str], Optional[bool]]] = None
    places: Optional[int] = None  # compare numbers rounded to this many decimals

    @staticmethod
    def number(v: Num, desc: str, places: Optional[int] = None) -> "Expect":
        return Expect("number", desc, value=v, places=places)

    @staticmethod
    def predicate(fn: Callable[[str], Optional[bool]], desc: str) -> "Expect":
        return Expect("predicate", desc, pred=fn)


def _same(a: Num, b: Num, places: Optional[int]) -> bool:
    if places is not None:
        return abs(float(a) - float(b)) < 0.5 * 10 ** (-places) + 1e-9
    return num_equal(a, b)


def _safe(fn, *args):
    try:
        return fn(*args)
    except _ERRORS:
        return None


def grade(q: dict, exp: Expect):
    """("pass"|"fail"|"skip", message) for question ``q`` against ``exp``."""
    if q.get("question_type") == "student_produced":
        ans = q.get("answer") or {}
        if exp.kind != "number":
            return "skip", "predicate solver on a grid-in"
        try:
            got = Fraction(str(ans.get("value"))) if not isinstance(ans.get("value"), float) \
                else ans["value"]
        except (ValueError, TypeError):
            return "skip", "unparseable answer value"
        accepted = [parse_number(a) for a in ans.get("accepted", [])]
        if any(a is not None and _same(a, exp.value, exp.places) for a in accepted) \
                or _same(got, exp.value, exp.places):
            return "pass", ""
        return "fail", f"{exp.desc}: expected {_fmt(exp.value)}, key has {ans.get('accepted')}"
    choices = q.get("choices") or []
    marked = q.get("correct_choice")
    verdicts: Dict[str, Optional[bool]] = {}
    for c in choices:
        if exp.kind == "number":
            v = parse_number(c["text"])
            verdicts[c["id"]] = None if v is None else _same(v, exp.value, exp.places)
        else:
            verdicts[c["id"]] = _safe(exp.pred, c["text"])
    mv = verdicts.get(marked)
    right = [cid for cid, ok in verdicts.items() if ok]
    want = _fmt(exp.value) if exp.kind == "number" else "predicate"
    if mv is None:
        if right:
            return "fail", f"{exp.desc}: expected {want} = choice {right}, marked {marked} unparseable"
        return "skip", "marked choice not machine-readable"
    if not mv:
        if right:
            return "fail", f"{exp.desc}: expected {want} = choice {','.join(right)}, marked {marked}"
        return "fail", f"{exp.desc}: expected {want}, no choice matches (marked {marked})"
    if len(right) > 1:
        return "fail", f"{exp.desc}: choices {','.join(right)} are all correct"
    return "pass", ""


def _fmt(v) -> str:
    if isinstance(v, Fraction):
        return str(v.numerator) if v.denominator == 1 else f"{v.numerator}/{v.denominator}"
    if isinstance(v, float):
        return f"{v:.6g}"
    return str(v)


# --------------------------------------------------------------------------
# text helpers

_MINUS = "−–"
_NUM = r"[−–-]?\d+(?:\.\d+)?(?:/\d+)?"


def _n(s: str) -> Fraction:
    s = s.replace(",", "")
    for m in _MINUS:
        s = s.replace(m, "-")
    return Fraction(s)


def _nums(s: str) -> List[Fraction]:
    return [_n(m) for m in re.findall(r"[−–-]?\d+(?:\.\d+)?", s.replace(",", ""))]


def _math_mask(text: str) -> List[bool]:
    """Per-character: could this be part of a math expression?"""
    mask = [False] * len(text)
    letter_runs = [(m.start(), m.end()) for m in re.finditer(r"[A-Za-z_]+", text)]
    single = set()
    for a, b in letter_runs:
        word = text[a:b]
        if b - a == 1 or word in ("ln", "log") or re.fullmatch(r"log_", word):
            single.update(range(a, b))
    for i, c in enumerate(text):
        if c.isdigit() or c in "+-−–*/^()|=<>≤≥ ²³√∛∜π·×÷%⁰¹⁴⁵⁶⁷⁸⁹₀₁₂₃₄₅₆₇₈₉":
            mask[i] = True
        elif c == "." and 0 < i < len(text) - 1 and text[i - 1].isdigit() and text[i + 1].isdigit():
            mask[i] = True
        elif c.isalpha() and i in single:
            mask[i] = True
        elif c == "_" and i in single:
            mask[i] = True
    return mask


def math_runs(text: str) -> List[str]:
    """Maximal math-looking substrings of ``text`` (trimmed)."""
    mask = _math_mask(text)
    out, i = [], 0
    while i < len(text):
        if not mask[i]:
            i += 1
            continue
        j = i
        while j < len(text) and mask[j]:
            j += 1
        run = text[i:j].strip()
        run = re.sub(r"^(?:[+*/^=<>≤≥·×÷]|\s)+", "", run)
        run = re.sub(r"(?:[+\-−*/^=<>≤≥·×÷(]|\s)+$", "", run)
        if run:
            out.append(run)
        i = j
    return out


def relations(text: str) -> List[str]:
    return [r for r in math_runs(text) if re.search(r"[=<>≤≥]", r)]


def equations(text: str) -> List[str]:
    return [r for r in relations(text) if "=" in r and not re.search(r"[<>≤≥]", r)]


def _clean_choice(text: str) -> str:
    return text.strip().rstrip(".")


def _point(text: str):
    m = re.fullmatch(r"\s*\(\s*(" + _NUM + r")\s*,\s*(" + _NUM + r")\s*\)\s*", text)
    return (_n(m.group(1)), _n(m.group(2))) if m else None


def _points_in(text: str):
    return [(_n(a), _n(b)) for a, b in
            re.findall(r"\(\s*(" + _NUM + r")\s*,\s*(" + _NUM + r")\s*\)", text)]


def _poly_equal(a: Poly, b: Poly) -> bool:
    return a == b


def _reduce_i(p: Poly) -> Poly:
    """Reduce powers of the imaginary unit i (i² = −1)."""
    out = Poly()
    for m, c in p.terms.items():
        e = dict(m).get("i", 0)
        rest = tuple((v, k) for v, k in m if v != "i")
        sign = [1, 1, -1, -1][e % 4]
        key = rest + ((("i", 1),) if e % 2 else ())
        out = out + Poly({tuple(sorted(key)): c * sign})
    return out


def _vars_ok(p: Poly, allowed) -> bool:
    return p.variables() <= set(allowed)


# --------------------------------------------------------------------------
# solvers: equations in one variable

_PICK = [(r"\b(greater|larger|greatest|largest|positive)\b", max),
         (r"\b(lesser|smaller|least|smallest|negative)\b", min)]


def _pick_root(roots: Sequence[Num], prompt: str) -> Optional[Num]:
    if not roots:
        return None
    if "x > 0" in prompt or "x>0" in prompt:
        roots = [r for r in roots if r > 0]
    if "x < 0" in prompt:
        roots = [r for r in roots if r < 0]
    if len(roots) == 1:
        return roots[0]
    for pat, fn in _PICK:
        if re.search(pat, prompt):
            if fn is max and re.search(r"\bpositive\b", prompt):
                pos = [r for r in roots if r > 0]
                return pos[0] if len(pos) == 1 else None
            return fn(roots, key=float)
    return None


def solve_one_var_equation(q) -> Optional[Expect]:
    p = q["prompt"]
    if q.get("stimulus"):
        return None
    m = re.search(r"(?:what is the value of|value of|what is|solution to)\s+([^?]+?)\s*(?:in the equation above)?\?",
                  p, re.I)
    asked = None
    if re.search(r"value of ([a-z])\b(?! *[(+\-−·×*/^²])", p):
        asked = re.search(r"value of ([a-z])\b(?! *[(+\-−·×*/^²])", p).group(1)
    elif re.search(r"what is ([a-z])\?", p):
        asked = re.search(r"what is ([a-z])\?", p).group(1)
    elif re.search(r"solutions? (to|of) (the|this) (given )?equation|solution to the equation", p, re.I):
        asked = "x"
    elif m and re.fullmatch(r"[a-z]", m.group(1).strip()):
        asked = m.group(1).strip()
    target = None
    if asked is None:
        mm = re.search(r"what is the value of (.+?)\?", p, re.I)
        if mm and re.search(r"[a-z]", mm.group(1)) and not re.search(r"[a-z]\(", mm.group(1)):
            target = mm.group(1)
            asked = "x"
    if asked is None:
        return None
    if re.search(r"\b(function|f\(|g\(|graph|line|system|inequalit|integer|percent|ratio)\b", p, re.I):
        return None
    eqs = [e for e in equations(re.sub(r" equal to ", " = ", p))]
    if len(eqs) != 1 or re.search(r"\|", eqs[0]) and asked:
        if len(eqs) == 1 and "|" in eqs[0]:
            return _abs_equation(eqs[0], p)
        return None
    eq = eqs[0]
    try:
        poly = parse_equation(eq)
    except _ERRORS:
        return _exponential_equation(eq, p)
    if poly.variables() != {asked} and target is None:
        return None
    var = next(iter(poly.variables())) if len(poly.variables()) == 1 else None
    if var is None:
        return None
    try:
        roots = solve_univariate(poly, var)
    except _ERRORS:
        return None
    if target is not None:
        if len(roots) != 1:
            return None
        try:
            v = parse(target).subs({var: Poly.const(roots[0])}).value()
        except _ERRORS:
            return None
        return Expect.number(v, f"solve {eq} then evaluate {target}")
    root = _pick_root(roots, p)
    if root is None:
        return None
    return Expect.number(root, f"solve {eq} for {var}")


def _abs_equation(eq: str, p: str) -> Optional[Expect]:
    m = re.fullmatch(r"\s*\|(.+)\|\s*=\s*(" + _NUM + r")\s*", eq)
    if not m:
        return None
    try:
        inner = parse(m.group(1))
        c = _n(m.group(2))
        roots = sorted(set(solve_univariate(inner - Poly.const(c)) + solve_univariate(inner + Poly.const(c))),
                       key=float)
    except _ERRORS:
        return None
    root = _pick_root(roots, p)
    return None if root is None else Expect.number(root, f"solve {eq}")


def _exponential_equation(eq: str, p: str) -> Optional[Expect]:
    s = normalize(eq).replace(" ", "")
    m = re.fullmatch(r"(?:(\d+)\*)?(\d+)\^\(?x\)?=(\d+)", s)
    if not m:
        m2 = re.fullmatch(r"(\d+)=(\d+)\^x", s)
        if not m2:
            return None
        a, b, c = 1, int(m2.group(2)), int(m2.group(1))
    else:
        a = int(m.group(1)) if m.group(1) else 1
        b, c = int(m.group(2)), int(m.group(3))
    if c % a or b < 2:
        return None
    t, n = c // a, 0
    while t > 1 and t % b == 0:
        t //= b
        n += 1
    if t != 1:
        return None
    return Expect.number(Fraction(n), f"solve {eq}")


# --------------------------------------------------------------------------
# plain evaluation


def _of_to_times(s: str) -> str:
    return re.sub(r"(\d%?|\))\s+of\s+(?=[\d(−-])", r"\1 * ", s)


def solve_evaluate(q) -> Optional[Expect]:
    p = q["prompt"].strip()
    if q.get("stimulus"):
        return None
    pats = [r"^What is the value of (.+?)\?$",
            r"^What is the (?:sum|product|difference|quotient) (.+?)\?$",
            r"^What is (.+?) written (?:as a|in) .+\?$",
            r"^What is (.+?) expressed .+\?$",
            r"^What is (.+?)\?$",
            r"^Which of the following is equal to (.+?)\?$",
            r"^(.+?) = \?$",
            r"^If [a-z] = (.+?), what is the value of [a-z]\?$"]
    for pat in pats:
        m = re.match(pat, p)
        if not m:
            continue
        e = _of_to_times(m.group(1))
        if re.search(r"[A-Za-z]{2,}", e.replace("log_", "").replace("ln", "")) and "log" not in e:
            return None
        try:
            poly = parse(e)
        except _ERRORS:
            return None
        if poly.is_const():
            return Expect.number(poly.value(), f"evaluate {m.group(1)}")
        if poly.variables() == {"i"}:
            target = _reduce_i(poly)

            def pred(t, target=target):
                return _reduce_i(parse(t)) == target
            return Expect.predicate(pred, f"complex {m.group(1)}")
        return None
    return None


# --------------------------------------------------------------------------
# functions

_FDEF = re.compile(r"\b([a-z])\(([a-z])\)\s*=\s*")


def _function_defs(p: str) -> Dict[str, tuple]:
    out = {}
    for m in _FDEF.finditer(p):
        rest = p[m.end():]
        runs = math_runs(rest[:120])
        if not runs or not rest.lstrip().startswith(runs[0][:3]):
            continue
        body = runs[0]
        # a run may swallow "and g": stop before a following definition
        body = re.split(r"\s+[a-z]\s*$", body)[0]
        if re.fullmatch(r"\s*" + _NUM + r"\s*", body) and m.group(1) in "fgh":
            # "f(x) = 16" is a condition, not a definition
            if any(k for k in out):
                continue
            continue
        out[m.group(1)] = (m.group(2), body)
    return out


def solve_function(q) -> Optional[Expect]:
    p = q["prompt"]
    if q.get("stimulus"):
        return None
    defs = _function_defs(p)
    if not defs:
        return None
    table: Optional[dict] = {}
    try:
        for name, (var, body) in defs.items():  # later defs may call earlier ones
            table[name] = (var, parse(body, table))
    except _ERRORS:
        table = None
    # f(a) / f(g(a))
    m = re.search(r"(?:value of|what is)\s+([a-z]\((?:[^()]|\([^()]*\))*\))\s*\?", p, re.I)
    if m and table and not re.search(r"\b[a-z]\([a-z]\)", m.group(1)):
        try:
            return Expect.number(evaluate(m.group(1), table), f"evaluate {m.group(1)}")
        except _ERRORS:
            return None
    name = next(iter(defs))
    var, body = defs[name]
    # If f(x) = c, what is x
    m = re.search(r"If " + name + r"\(" + var + r"\) = (" + _NUM + r"), what is the value of " + var, p)
    if m and table:
        try:
            roots = solve_univariate(table[name][1] - Poly.const(_n(m.group(1))), var)
        except _ERRORS:
            return None
        r = _pick_root(roots, p)
        return None if r is None else Expect.number(r, f"solve {name}({var}) = {m.group(1)}")
    # average rate of change
    m = re.search(r"average rate of change of " + name + r" between " + var + r" = (" + _NUM +
                  r") and " + var + r" = (" + _NUM + r")", p)
    if m and table:
        a, b = _n(m.group(1)), _n(m.group(2))
        f = table[name][1]
        try:
            fa = f.subs({var: Poly.const(a)}).value()
            fb = f.subs({var: Poly.const(b)}).value()
        except _ERRORS:
            return None
        return Expect.number((fb - fa) / (b - a), "average rate of change")
    # zero of a rational function
    if re.search(r"For what value of " + var + r" is " + name + r"\(" + var + r"\) = 0", p):
        mm = re.fullmatch(r"\((.+)\)\s*/\s*\((.+)\)", body.strip())
        try:
            if mm:
                num, den = parse(mm.group(1)), parse(mm.group(2))
                zeros = [r for r in solve_univariate(num, var)
                         if not num_equal(den.subs({var: Poly.const(r)}).value(), 0)]
            else:
                zeros = solve_univariate(table[name][1], var) if table else []
        except _ERRORS:
            return None
        if len(zeros) != 1:
            return Expect.predicate(lambda t: False if zeros == [] else None,
                                    f"{name} has no zero" if not zeros else "several zeros")
        return Expect.number(zeros[0], f"zero of {name}")
    # graph passes through (a, b): value of constant k
    m = re.search(r"passes through the point " + r"\((" + _NUM + r"), (" + _NUM + r")\)\. What is the value of the constant ([a-z])", p)
    if m:
        k = m.group(3)
        try:
            poly = parse(body).subs({var: Poly.const(_n(m.group(1)))}) - Poly.const(_n(m.group(2)))
            roots = solve_univariate(poly, k)
        except _ERRORS:
            return None
        return Expect.number(roots[0], "constant from a point") if len(roots) == 1 else None
    # max / min of a quadratic or |x − h| + k
    m = re.search(r"(maximum|minimum) value of " + name, p)
    if m:
        am = re.fullmatch(r"\s*\|\s*" + var + r"\s*([+\-−])\s*(\d+)\s*\|\s*(?:([+\-−])\s*(\d+))?\s*", body)
        if am:
            k = _n(am.group(4)) if am.group(4) else Fraction(0)
            if am.group(3) and am.group(3) in "-−":
                k = -k
            return Expect.number(k, "vertex of |x − h| + k") if m.group(1) == "minimum" else None
        if not table:
            return None
        try:
            c = table[name][1].coeffs(var)
        except _ERRORS:
            return None
        a2, a1, a0 = c.get(2, 0), c.get(1, 0), c.get(0, 0)
        if a2 == 0 or (a2 < 0) != (m.group(1) == "maximum"):
            return None
        return Expect.number(a0 - Fraction(a1) ** 2 / (4 * a2) if isinstance(a2, Fraction) else
                             a0 - a1 ** 2 / (4 * a2), "vertex value")
    return None


# --------------------------------------------------------------------------
# systems and lines


def solve_system(q) -> Optional[Expect]:
    p = q["prompt"]
    if q.get("stimulus"):
        return None
    eqs = [e for e in equations(p) if re.search(r"[xy]", e)]
    if "together with" in p:
        return _system_partner(q, eqs)
    if len(eqs) != 2:
        return None
    try:
        polys = [parse_equation(e) for e in eqs]
        if any(pp.degree() > 1 or not _vars_ok(pp, "xy") for pp in polys):
            return None
        sol = solve_linear_system(polys)
    except _ERRORS:
        return None
    if re.search(r"How many solutions", p):
        (a, b, c), (d, e, f) = [(pp.terms.get((("x", 1),), 0), pp.terms.get((("y", 1),), 0),
                                 pp.terms.get((), 0)) for pp in polys]
        if sol is not None:
            want = "one"
        elif a * f == c * d and b * f == c * e:
            want = "infinite"
        else:
            want = "none"

        def pred(t, want=want):
            t = t.lower()
            kind = ("infinite" if "infinite" in t else "none" if t.startswith("no") else
                    "one" if "exactly one" in t else "two" if "two" in t else None)
            return None if kind is None else kind == want
        return Expect.predicate(pred, f"solution count ({want})")
    if sol is None:
        return None
    if re.search(r"at which point|which (?:ordered pair|point)", p):
        target = (sol["x"], sol["y"])
        return Expect.predicate(lambda t: _point(t) == target if _point(t) else None,
                                f"intersection {target}")
    m = re.search(r"(?:value of|What is) ([xy](?: [+\-−] [xy])?)(?: for the solution| in the solution|\?)", p) \
        or re.search(r"what is the value of ([^?]+)\?", p)
    if re.search(r"x-coordinate", p):
        return Expect.number(sol["x"], "system x")
    if re.search(r"y-coordinate", p):
        return Expect.number(sol["y"], "system y")
    if not m:
        return None
    try:
        v = evaluate(m.group(1), env=sol)
    except _ERRORS:
        return None
    return Expect.number(v, f"system {m.group(1)}")


def _system_partner(q, eqs) -> Optional[Expect]:
    p = q["prompt"]
    if len(eqs) != 1:
        return None
    want = "none" if "no solution" in p else "infinite" if "infinitely many" in p else \
        "one" if "exactly one" in p else None
    if want is None:
        return None
    try:
        base = parse_equation(eqs[0])
    except _ERRORS:
        return None

    def pred(t):
        other = parse_equation(t)
        sol = solve_linear_system([base, other])
        if sol is not None:
            return want == "one"
        a, b, c = (base.terms.get((("x", 1),), 0), base.terms.get((("y", 1),), 0), base.terms.get((), 0))
        d, e, f = (other.terms.get((("x", 1),), 0), other.terms.get((("y", 1),), 0), other.terms.get((), 0))
        same = a * f == c * d and b * f == c * e
        return want == ("infinite" if same else "none")
    return Expect.predicate(pred, f"partner equation ({want})")


def solve_lines(q) -> Optional[Expect]:
    p = q["prompt"]
    if q.get("stimulus"):
        return None
    pts = _points_in(p)
    if re.search(r"\bslope\b", p) and len(pts) == 2 and "passes through" in p or \
            re.search(r"slope of the line that passes through", p):
        if len(pts) != 2 or "best fit" in p:
            return None
        (x1, y1), (x2, y2) = pts
        if x1 == x2:
            return None
        return Expect.number((y2 - y1) / (x2 - x1), "slope from two points")
    m = re.search(r"distance between the points (" + _NUM + r") and (" + _NUM + r")", p)
    if m:
        return Expect.number(abs(_n(m.group(1)) - _n(m.group(2))), "number-line distance")
    if re.search(r"distance between the points", p) and len(pts) == 2:
        (x1, y1), (x2, y2) = pts
        d2 = (x2 - x1) ** 2 + (y2 - y1) ** 2
        return Expect.number(_safe(lambda: evaluate(f"sqrt({d2})")), "distance formula")
    if re.search(r"midpoint of the segment", p) and len(pts) == 2:
        (x1, y1), (x2, y2) = pts
        target = ((x1 + x2) / 2, (y1 + y2) / 2)
        return Expect.predicate(lambda t: _point(t) == target if _point(t) else None, "midpoint")
    m = re.search(r"graph of y = (.+?) in the xy-plane crosses the x-axis", p)
    if m:
        try:
            r = solve_univariate(parse(m.group(1)), "x")
        except _ERRORS:
            return None
        return Expect.number(r[0], "x-intercept") if len(r) == 1 else None
    m = re.search(r"(perpendicular|parallel) to the (?:line|graph of) y = (.+?)(?: in the xy-plane)?[.?]", p)
    if m and re.search(r"What is the slope|slope of", p):
        try:
            c = parse(m.group(2)).coeffs("x")
        except _ERRORS:
            return None
        slope = c.get(1, Fraction(0))
        if m.group(1) == "parallel":
            return Expect.number(slope, "parallel slope")
        return None if slope == 0 else Expect.number(-1 / slope, "perpendicular slope")
    m = re.search(r"line with slope (" + _NUM + r") passes through the point \((" + _NUM + r"), (" + _NUM + r")\)", p)
    if m and "Which equation" in p:
        mm, x0, y0 = _n(m.group(1)), _n(m.group(2)), _n(m.group(3))

        def pred(t, mm=mm, x0=x0, y0=y0):
            eq = parse_equation(t)
            yc = eq.terms.get((("y", 1),))
            if not yc or eq.degree() > 1 or not _vars_ok(eq, "xy"):
                return None
            rhs = (Poly.var("y") * Poly.const(yc) - eq) / Poly.const(yc)   # y = rhs
            c = rhs.coeffs("x")
            return num_equal(c.get(1, 0), mm) and num_equal(rhs.subs({"x": Poly.const(x0)}).value(), y0)
        return Expect.predicate(pred, "line through point with slope")
    m = re.search(r"points? lies? on the (?:graph of |line )?(y = [^?]+?)(?: in the [^?]*)?\?", p)
    if m:
        eq = m.group(1)

        def pred(t, eq=eq):
            pt = _point(t)
            return None if pt is None else holds(eq, {"x": pt[0], "y": pt[1]})
        return Expect.predicate(pred, "point on line")
    m = re.search(r"is a solution to the inequality (.+?)\?", p)
    if m and "ordered pair" in p:
        rel = m.group(1)

        def pred(t, rel=rel):
            pt = _point(t)
            return None if pt is None else holds(rel, {"x": pt[0], "y": pt[1]})
        return Expect.predicate(pred, "ordered pair satisfies inequality")
    return None


# --------------------------------------------------------------------------
# inequalities


def _boundaries(rel: str) -> List[Num]:
    out: List[Num] = []
    parts = re.split(r"<=|>=|<|>|≤|≥", rel)
    for a, b in zip(parts, parts[1:]):
        am = re.fullmatch(r"\s*\|(.+)\|\s*", a)
        try:
            if am:
                inner, rhs = parse(am.group(1)), parse(b)
                out += solve_univariate(inner - rhs, "x") + solve_univariate(inner + rhs, "x")
            else:
                out += solve_univariate(parse(a) - parse(b), "x")
        except _ERRORS:
            continue
    return out


def _same_set(stem_rel: str, choice: str, extra: Sequence[Num]) -> Optional[bool]:
    t = _clean_choice(choice)
    if not re.search(r"[<>≤≥]", t) or not re.search(r"\bx\b", t):
        return None
    pts = set()
    for n in list(extra) + _nums(t) + _boundaries(stem_rel):
        for d in (Fraction(0), Fraction(1, 1000), Fraction(-1, 1000), Fraction(1, 2), Fraction(-1, 2)):
            pts.add(Fraction(n) + d if isinstance(n, Fraction) else n + float(d))
    pts |= {Fraction(-10 ** 6), Fraction(0), Fraction(10 ** 6)}
    for x in pts:
        if holds(stem_rel, {"x": x}) != holds(t, {"x": x}):
            return False
    return True


def solve_inequality(q) -> Optional[Expect]:
    p = q["prompt"]
    if q.get("stimulus"):
        return None
    m = re.search(r"(?:all values of x that satisfy|solution set of the inequality|all solutions to) (.+?)\??$", p)
    if m:
        rel = m.group(1).rstrip("?").strip()
        extra = _nums(rel)
        return Expect.predicate(lambda t: _same_set(rel, t, extra), f"solution set of {rel}")
    m = re.search(r"(?:satisfies|satisfy) (.+?) EXCEPT", p) or \
        re.search(r"NOT a solution to the inequality (.+?)\?", p)
    if m:
        rel = m.group(1)

        def pred(t, rel=rel):
            v = parse_number(t)
            return None if v is None else not holds(rel, {"x": v})
        return Expect.predicate(pred, f"non-solution of {rel}")
    m = re.search(r"(greatest|least) (?:possible )?integer value of x (?:that satisfies|for which) (.+?)\?", p) or \
        re.search(r"If (.+?), what is the (greatest|least) possible integer value of x\?", p)
    if m:
        if m.group(1) in ("greatest", "least"):
            which, rel = m.group(1), m.group(2)
        else:
            rel, which = m.group(1), m.group(2)
        bs = _boundaries(rel)
        if len(bs) != 1:
            return None
        b = bs[0]
        cands = [math.floor(b) + k for k in range(-3, 4)]
        ok = [c for c in cands if holds(rel, {"x": Fraction(c)})]
        if not ok:
            return None
        return Expect.number(Fraction(max(ok) if which == "greatest" else min(ok)), f"{which} integer in {rel}")
    return None


# --------------------------------------------------------------------------
# polynomials / equivalent expressions


def solve_equivalent(q) -> Optional[Expect]:
    p = q["prompt"]
    m = re.match(r"^Which of the following is (?:equivalent|equal) to (.+?)(?:,? for (?:all )?[a-z] [>≠<] 0| for positive [a-z])?\?$",
                 p.strip())
    if not m:
        return None
    e = m.group(1)
    e = re.sub(r"÷\s*(\d*[a-z](?:\^\d+|²|³)?)", r"/ (\1)", e)
    try:
        target = parse(e)
    except _ERRORS:
        return None
    if target.is_const():
        return None  # handled by solve_evaluate
    if "i" in target.variables():
        return None
    if re.search(r"√|∛|∜|\^\(", e):
        return None

    def pred(t, target=target):
        t = _clean_choice(t)
        t = re.sub(r"÷\s*(\d*[a-z](?:\^\d+|²|³)?)", r"/ (\1)", t)
        return parse(t) == target
    return Expect.predicate(pred, f"equivalent to {e}")


def solve_literal(q) -> Optional[Expect]:
    p = q["prompt"]
    m = re.search(r"expresses ([a-z]) in terms of|gives ([A-Za-z]) in terms of", p)
    if not m:
        return None
    v = m.group(1) or m.group(2)
    eqs = equations(p)
    if len(eqs) != 1:
        return None
    try:
        base = parse_equation(eqs[0])
    except _ERRORS:
        return None

    def pred(t):
        lhs, rhs = normalize(t).split("=")
        if lhs.strip() != v:
            return None
        return base.subs({v: parse(rhs)}) == Poly()
    return Expect.predicate(pred, f"solve for {v}")


def solve_quadratic_misc(q) -> Optional[Expect]:
    p = q["prompt"]
    if q.get("stimulus"):
        return None
    m = re.search(r"zeros of the function [a-z]\(x\) = (.+?)\?", p)
    if m:
        try:
            roots = solve_univariate(parse(m.group(1)), "x")
        except _ERRORS:
            return None

        def pred(t, roots=roots):
            if "only" in t:
                vals = _nums(t)
                return len(roots) == 1 and len(vals) == 1 and num_equal(vals[0], roots[0])
            vals = sorted(_nums(t))
            return len(vals) == len(roots) and all(num_equal(a, b) for a, b in zip(vals, roots))
        return Expect.predicate(pred, "zeros")
    m = re.search(r"graph of y = (.+?) in the xy-plane has x-intercepts at x = p and x = q\. What is the value of p ([+\-−·]) q", p)
    if m:
        try:
            roots = solve_univariate(parse(m.group(1)), "x")
        except _ERRORS:
            return None
        if len(roots) != 2:
            return None
        a, b = roots
        return Expect.number(a + b if m.group(2) == "+" else a * b if m.group(2) == "·" else None,
                             "intercept combination") if m.group(2) in "+·" else None
    if re.search(r"How many distinct real solutions", p):
        eqs = equations(p)
        if len(eqs) != 1:
            return None
        try:
            c = parse_equation(eqs[0]).coeffs("x")
        except _ERRORS:
            return None
        a2, a1, a0 = c.get(2, 0), c.get(1, 0), c.get(0, 0)
        if a2 == 0:
            return None
        d = a1 * a1 - 4 * a2 * a0
        return Expect.number(Fraction(2 if d > 0 else 1 if d == 0 else 0), "discriminant count")
    m = re.search(r"h\(t\) = (.+?)\. (.+)\?$", p)
    if m:
        try:
            c = parse(m.group(1)).coeffs("t")
        except _ERRORS:
            return None
        a2, a1, a0 = c.get(2, 0), c.get(1, 0), c.get(0, 0)
        if a2 >= 0:
            return None
        if "maximum height" in m.group(2):
            return Expect.number(a0 - a1 * a1 / (4 * a2), "projectile peak")
        if "hit the ground" in m.group(2):
            roots = [r for r in solve_univariate(parse(m.group(1)), "t") if r > 0]
            return Expect.number(roots[0], "projectile landing") if len(roots) == 1 else None
        if "maximum" in m.group(2) and "seconds" in m.group(2):
            return Expect.number(-a1 / (2 * a2), "projectile peak time")
    m = re.search(r"length of a rectangle is (\d+) more than its width, and its area is (\d+)\. What is the width", p)
    if m:
        k, a = int(m.group(1)), int(m.group(2))
        roots = [r for r in solve_univariate(parse(f"w^2 + {k}w - {a}"), "w") if r > 0]
        return Expect.number(roots[0], "rectangle width") if len(roots) == 1 else None
    return None


# --------------------------------------------------------------------------
# statistics


def _data_list(p: str) -> Optional[List[Fraction]]:
    runs = re.findall(r"(?<![\d.])(" + _NUM + r"(?:\s*,\s*(?:and\s+)?" + _NUM + r"){2,})", p)
    if not runs:
        return None
    best = max(runs, key=len)
    return [_n(x) for x in re.findall(_NUM, best)]


def _median(xs: List[Fraction]) -> Fraction:
    s = sorted(xs)
    n = len(s)
    return s[n // 2] if n % 2 else (s[n // 2 - 1] + s[n // 2]) / 2


def solve_statistics(q) -> Optional[Expect]:
    p = q["prompt"]
    if q.get("stimulus"):
        return None
    m = re.search(r"The mean of (\w+) numbers is (" + _NUM + r")\. (\w+) of the numbers are ([^.]+?)\. What is the (\w+) number", p)
    if m:
        words = {"three": 3, "four": 4, "five": 5, "six": 6, "seven": 7, "two": 2}
        n = words.get(m.group(1))
        known = _nums(m.group(4))
        if n is None or len(known) != n - 1:
            return None
        return Expect.number(_n(m.group(2)) * n - sum(known), "missing value from mean")
    m = re.search(r"If (" + _NUM + r") is added to every value, what is the new (mean|median)", p)
    xs = _data_list(p)
    if m and xs:
        stat = sum(xs) / len(xs) if m.group(2) == "mean" else _median(xs)
        return Expect.number(stat + _n(m.group(1)), "shifted center")
    if not xs or len(xs) < 3:
        return None
    if re.search(r"added|removed|standard deviation|changes by more|increase|decrease", p):
        return None
    tail = p.split("?")[0].lower().split(".")[-1]
    s = sorted(xs)
    n = len(s)
    lower, upper = s[: n // 2], s[(n + 1) // 2:]
    m = re.search(r"what (?:is|was) the (mean|average|median|range|mode|first quartile|third quartile|"
                  r"interquartile range)\b", tail.strip())
    if not m:
        return None
    tail = m.group(1)
    if "interquartile" in tail:
        return Expect.number(_median(upper) - _median(lower), "IQR (halves method)")
    if "mean" in tail or "average" in tail:
        return Expect.number(sum(xs) / len(xs), "mean of list")
    if "median" in tail:
        return Expect.number(_median(xs), "median of list")
    if "range" in tail:
        return Expect.number(max(xs) - min(xs), "range of list")
    if "mode" in tail:
        counts = {x: xs.count(x) for x in xs}
        top = max(counts.values())
        modes = [x for x, c in counts.items() if c == top]
        return Expect.number(modes[0], "mode of list") if len(modes) == 1 else None
    if "first quartile" in tail or "third quartile" in tail:
        return Expect.number(_median(lower if "first" in tail else upper), "quartile (halves method)")
    return None


# --------------------------------------------------------------------------
# percent / ratio / rate word problems

_MULT_WORDS = {"doubles": 2, "triples": 3, "quadruples": 4}


def solve_word(q) -> Optional[Expect]:
    p = q["prompt"]
    if q.get("stimulus"):
        return None
    N = _NUM.replace("[−–-]?", "")
    rules = [
        (r"What is (" + N + r")% of (" + N + r")\?", lambda a, b: a * b / 100),
        (r"has (" + N + r") items in stock, and (" + N + r")% of them", lambda a, b: a * b / 100),
        (r"was (" + N + r") and then increased by (" + N + r")%", lambda a, b: a * (1 + b / 100)),
        (r"was (" + N + r") and then decreased by (" + N + r")%", lambda a, b: a * (1 - b / 100)),
        (r"found that (" + N + r")% of .*?If (" + N + r") \w+ are selected", lambda a, b: a * b / 100),
        (r"\$(" + N + r")\. If \w+ leaves an? (" + N + r")% tip, what is the total", lambda a, b: a * (1 + b / 100)),
        (r"\$(" + N + r")\. If \w+ pays (" + N + r")% tax, what is the total", lambda a, b: a * (1 + b / 100)),
        (r"deposits \$(" + N + r") in an account that earns (" + N + r")% simple interest per year\. How much interest, in dollars, is earned after (" + N + r") years",
         lambda a, b, c: a * b * c / 100),
        (r"travels at a constant speed of (" + N + r") miles per hour\. How many miles does it travel in (" + N + r") hours",
         lambda a, b: a * b),
        (r"travels (" + N + r") miles at a constant speed of (" + N + r") miles per hour\. How many hours",
         lambda a, b: a / b),
        (r"start (" + N + r") miles apart and drive toward each other, at (" + N + r") and (" + N + r") miles per hour",
         lambda d, a, b: d / (a + b)),
        (r"charges a \$(" + N + r") flat fee plus \$(" + N + r") per \w+\. If a job costs \$(" + N + r")",
         lambda f, r, t: (t - f) / r),
        (r"has \$(" + N + r") and wants to buy as many [\w ]+ as possible at \$(" + N + r") each",
         lambda m, c: Fraction(math.floor(m / c))),
        (r"buys (" + N + r") \w+ at \$(" + N + r") each and pays with a \$(" + N + r") bill",
         lambda n, c, b: b - n * c),
        (r"travels (" + N + r") miles on each gallon of gasoline\. How many miles can it travel on (" + N + r") gallons",
         lambda a, b: a * b),
        (r"It takes (" + N + r") \w+ (" + N + r") hours to [\w ]+\. Working at the same rate, how many hours would it take (" + N + r") ",
         lambda n, h, m: n * h / m),
        (r"recipe that serves (" + N + r") people calls for (" + N + r") cups of \w+\. How many cups of \w+ are needed to serve (" + N + r") people",
         lambda a, c, b: c * b / a),
        (r"1 centimeter represents (" + N + r") kilometers\. Two towns are (" + N + r") centimeters apart",
         lambda k, d: k * d),
        (r"a (" + N + r")-meter pole casts a (" + N + r")-meter shadow and a tree casts a (" + N + r")-meter shadow",
         lambda h, s, t: h * t / s),
        (r"choose from (" + N + r") shirts and (" + N + r") pairs of pants", lambda a, b: a * b),
        (r"remainder when (" + N + r") is divided by (" + N + r")", lambda a, b: a % b),
        (r"greatest common factor of (" + N + r") and (" + N + r")",
         lambda a, b: Fraction(math.gcd(int(a), int(b)))),
        (r"least common multiple of (" + N + r") and (" + N + r")",
         lambda a, b: Fraction(int(a) * int(b) // math.gcd(int(a), int(b)))),
        (r"sum of three consecutive integers is (" + N + r")\. What is the largest", lambda s: s / 3 + 1),
        (r"sum of three consecutive integers is (" + N + r")\. What is the smallest", lambda s: s / 3 - 1),
        (r"sum of two numbers is (" + N + r"),? and their difference is (" + N + r")\. What is the larger",
         lambda s, d: (s + d) / 2),
        (r"sum of two numbers is (" + N + r"),? and their difference is (" + N + r")\. What is the smaller",
         lambda s, d: (s - d) / 2),
        (r"Two angles of a triangle measure (" + N + r")° and (" + N + r")°", lambda a, b: 180 - a - b),
        (r"complement of an? (" + N + r")° angle", lambda a: 90 - a),
        (r"supplement of an? (" + N + r")° angle", lambda a: 180 - a),
        (r"interior angles, in degrees, of a polygon with (" + N + r") sides", lambda n: 180 * (n - 2)),
        (r"right triangle has legs of length (" + N + r") and (" + N + r")\. What is the length of its hypotenuse",
         lambda a, b: evaluate(f"sqrt({a * a + b * b})")),
        (r"cube with edge length (" + N + r")\. What is the volume", lambda e: e ** 3),
        (r"has width (" + N + r") and height (" + N + r")\. What is the perimeter", lambda w, h: 2 * (w + h)),
        (r"has a width of (" + N + r") and a height of (" + N + r")\. What is its area", lambda w, h: w * h),
        (r"A rectangle has a length of (" + N + r") and a width of (" + N + r")\. What is its area", lambda a, b: a * b),
        (r"A pump moves (" + N + r") liters every (" + N + r") minutes\. At this rate, how many liters in (" + N + r") minutes",
         lambda a, b, c: a * c / b),
        (r"If the circumference of a circle is (" + N + r")π, what is the length of its radius", lambda c: c / 2),
        (r"How many multiples of (" + N + r") are there between (" + N + r") and (" + N + r"), inclusive",
         lambda k, a, b: Fraction(int(b) // int(k) - (int(a) - 1) // int(k))),
    ]
    for pat, fn in rules:
        m = re.search(pat, p)
        if m:
            try:
                v = fn(*[_n(g) for g in m.groups()])
            except _ERRORS:
                return None
            places = 2 if "$" in "".join(c["text"] for c in q.get("choices") or []) else None
            if re.search(r"\b(about|approximately)\b", p) and places is None:
                places = 0  # "about how many": the nearest whole number
            return Expect.number(v, pat.split("(")[0][:40].strip() or "word problem", places)
    m = re.search(r"There are (" + N + r") [\w ]+?, and the number (doubles|triples|quadruples) each \w+\. How many [\w ]+ after (" + N + r") ", p)
    if m:
        return Expect.number(_n(m.group(1)) * _MULT_WORDS[m.group(2)] ** int(m.group(3)), "repeated growth")
    m = re.search(r"deposits \$(" + N + r") in an account that earns (" + N + r")% interest, compounded annually\. What is the balance, in dollars, after (" + N + r") years?", p)
    if m:
        a, r, t = (_n(g) for g in m.groups())
        return Expect.number(a * (1 + r / 100) ** int(t), "compound interest", places=2)
    m = re.search(r"bag contains ([^.]+)\. If one of the \w+ is chosen at random, what is the probability that it is (\w+)", p)
    if m:
        parts = re.findall(r"(\d+) (\w+)", m.group(1))
        counts = {w: int(n) for n, w in parts}
        total = sum(counts.values())
        if m.group(2) in counts and total:
            return Expect.number(Fraction(counts[m.group(2)], total), "bag probability")
    m = re.search(r"divided into (\d+) equal sections, (\d+) of which are shaded", p)
    if m:
        return Expect.number(Fraction(int(m.group(2)), int(m.group(1))), "shaded fraction")
    m = re.search(r"spinner has (\d+) equal sections numbered 1 through \1\. What is the probability that the spinner lands on (?:a number|an? )?(.+?)\?", p)
    if m:
        n, cond = int(m.group(1)), m.group(2)
        mm = re.search(r"(less than or equal to|greater than or equal to|less than|greater than|multiple of) (\d+)", cond)
        if mm:
            k = int(mm.group(2))
            test = {"less than or equal to": lambda x: x <= k, "greater than or equal to": lambda x: x >= k,
                    "less than": lambda x: x < k, "greater than": lambda x: x > k,
                    "multiple of": lambda x: x % k == 0}[mm.group(1)]
        elif "even" in cond:
            test = lambda x: x % 2 == 0  # noqa: E731
        elif "odd" in cond:
            test = lambda x: x % 2 == 1  # noqa: E731
        else:
            return None
        return Expect.number(Fraction(sum(1 for x in range(1, n + 1) if test(x)), n), "spinner probability")
    m = re.search(r"ratio of (\w+) to (\w+) [\w ]*? is (\d+):(\d+)\. If there are (\d+) (\w+), how many (\w+) are there", p)
    if m:
        a_name, b_name, a, b, n, given, asked = m.groups()
        a, b, n = int(a), int(b), int(n)
        if given == b_name and asked == a_name:
            return Expect.number(Fraction(a * n, b), "ratio")
        if given == a_name and asked == b_name:
            return Expect.number(Fraction(b * n, a), "ratio")
    return None


# --------------------------------------------------------------------------
# logs and sequences


_ORD = {"first": 1, "second": 2, "third": 3, "fourth": 4, "fifth": 5, "sixth": 6, "seventh": 7,
        "eighth": 8, "ninth": 9, "tenth": 10, "eleventh": 11, "twelfth": 12}


def _ordinal(s: str) -> Optional[int]:
    m = re.fullmatch(r"(\d+)(?:st|nd|rd|th)", s)
    return int(m.group(1)) if m else _ORD.get(s)


def solve_sequences_logs(q) -> Optional[Expect]:
    p = q["prompt"]
    if q.get("stimulus"):
        return None
    m = re.search(r"y = ln\(e\^(" + _NUM + r")\)", p)
    if m:
        return Expect.number(_n(m.group(1)), "ln(e^k)")
    m = re.search(r"first four terms of an? (arithmetic|geometric) sequence are ([^…]+?),? …\.? What is the (\w+) term", p)
    if m:
        terms = _nums(m.group(2))
        n = _ordinal(m.group(3))
        if len(terms) < 2 or n is None:
            return None
        if m.group(1) == "arithmetic":
            d = terms[1] - terms[0]
            return Expect.number(terms[0] + (n - 1) * d, "arithmetic term")
        if terms[0] == 0:
            return None
        r = terms[1] / terms[0]
        return Expect.number(terms[0] * r ** (n - 1), "geometric term")
    m = re.search(r"sum of the first (\d+) terms of the arithmetic sequence ([^…]+?),? …", p)
    if m:
        n, terms = int(m.group(1)), _nums(m.group(2))
        d = terms[1] - terms[0]
        return Expect.number(sum(terms[0] + k * d for k in range(n)), "arithmetic sum")
    m = re.search(r"arithmetic sequence ([^…]+?),? …, which term has the value (" + _NUM + r")", p)
    if m:
        terms, v = _nums(m.group(1)), _n(m.group(2))
        d = terms[1] - terms[0]
        n = (v - terms[0]) / d + 1
        return Expect.predicate(lambda t: (_ordinal(t.strip().lower().split()[0].rstrip(","))
                                           if not re.fullmatch(r"\d+", t.strip()) else int(t)) == n,
                                "which term")
    m = re.search(r"a₁ = (" + _NUM + r") and a_n = a_\(n[−-]1\) ([+−-]|×|·) (" + _NUM + r") for n ≥ 2\. What is the value of a_(\d+)", p)
    if m:
        a, op, k, n = _n(m.group(1)), m.group(2), _n(m.group(3)), int(m.group(4))
        for _ in range(n - 1):
            a = a + k if op == "+" else a - k if op in "−-" else a * k
        return Expect.number(a, "recursive sequence")
    m = re.search(r"figure 1 uses (\d+) \w+, figure 2 uses (\d+), figure 3 uses (\d+), and each figure uses (\d+) more than the one before\. How many \w+ does figure (\d+) use", p)
    if m:
        a, _, _, d, n = (int(g) for g in m.groups())
        return Expect.number(Fraction(a + (n - 1) * d), "pattern term")
    return None


SOLVERS = [
    solve_function,
    solve_system,
    solve_lines,
    solve_inequality,
    solve_quadratic_misc,
    solve_literal,
    solve_equivalent,
    solve_statistics,
    solve_word,
    solve_sequences_logs,
    solve_one_var_equation,
    solve_evaluate,
]


def expectation(q) -> Optional[Expect]:
    """The first solver that recognises the stem (None if none does)."""
    for fn in SOLVERS:
        try:
            exp = fn(q)
        except _ERRORS:
            exp = None
        if exp is not None and (exp.kind != "number" or exp.value is not None):
            return exp
    return None
