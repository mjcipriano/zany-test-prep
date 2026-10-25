"""A tiny exact-arithmetic expression and polynomial engine for the audit.

The audit re-solves generated math stems independently of the generators, so
it needs to read the notation the bank actually uses ("3x + 26 = 50",
"|−3 − −16|", "√252 · √112", "4^x = 256", "f(x) = 11x + 15", "(x − 7)(x + 6)")
and do exact arithmetic on it. CI only installs pyyaml + jsonschema, so rather
than depend on sympy this module implements just enough:

* :func:`normalize` - unicode math notation -> ASCII tokens.
* :func:`parse` - recursive-descent parser producing a :class:`Poly`
  (multivariate polynomial with Fraction, or float when irrational,
  coefficients). Pure numbers are constant polynomials.
* :func:`solve_univariate` / :func:`solve_linear_system` - exact solving of
  degree <= 2 equations and 2x2 linear systems.
* :func:`parse_number` - the numeric value of an answer-choice string such as
  "$4,080", "9/2", "−7", "4%", "7√2" or "54π" (None when not purely numeric).
* :func:`num_equal` - exact (Fraction) or tolerant (float) comparison.

Anything outside this subset raises :class:`ExprError`; callers treat that as
"can't check this item" rather than a failure.
"""
from __future__ import annotations

import math
import re
from fractions import Fraction
from typing import Dict, Iterable, List, Optional, Tuple, Union

Num = Union[Fraction, float]
Mono = Tuple[Tuple[str, int], ...]


class ExprError(ValueError):
    """The text is outside the notation subset this engine understands."""


# --------------------------------------------------------------------------
# numbers


def _clean(x: Num) -> Num:
    """Collapse floats that are (numerically) integers/simple back to exact."""
    if isinstance(x, float):
        if math.isnan(x) or math.isinf(x):
            raise ExprError("non-finite value")
        r = round(x)
        if abs(x - r) < 1e-9:
            return Fraction(int(r))
    return x


def num_equal(a: Num, b: Num, rel: float = 1e-6) -> bool:
    """Equality for audit values: exact for two Fractions, else tolerant."""
    if isinstance(a, Fraction) and isinstance(b, Fraction):
        return a == b
    fa, fb = float(a), float(b)
    return abs(fa - fb) <= rel * max(1.0, abs(fa), abs(fb))


def _sqrt(x: Num) -> Num:
    if x < 0:
        raise ExprError("square root of a negative number")
    if isinstance(x, Fraction):
        n, d = math.isqrt(x.numerator), math.isqrt(x.denominator)
        if n * n == x.numerator and d * d == x.denominator:
            return Fraction(n, d)
    return _clean(math.sqrt(float(x)))


def _root(x: Num, k: int) -> Num:
    if k == 2:
        return _sqrt(x)
    if x < 0 and k % 2 == 0:
        raise ExprError("even root of a negative number")
    sign = -1 if x < 0 else 1
    r = sign * abs(float(x)) ** (1.0 / k)
    if isinstance(x, Fraction):
        cand = Fraction(round(r))
        if cand ** k == x:
            return cand
    return _clean(r)


def _pow(base: Num, exp: Num) -> Num:
    if isinstance(exp, Fraction) and exp.denominator == 1:
        e = exp.numerator
        if abs(e) > 400:
            raise ExprError("exponent too large")
        if isinstance(base, Fraction):
            if base == 0 and e < 0:
                raise ExprError("division by zero")
            return base ** e
        return _clean(base ** e)
    if isinstance(exp, Fraction) and isinstance(base, Fraction) and base >= 0:
        # rational exponent of a rational base: try an exact root first
        r = _root(base, exp.denominator)
        if isinstance(r, Fraction):
            return r ** exp.numerator
    if base < 0:
        raise ExprError("fractional power of a negative number")
    return _clean(float(base) ** float(exp))


# --------------------------------------------------------------------------
# polynomials


class Poly:
    """A multivariate polynomial: {monomial: coefficient}.

    A monomial is a sorted tuple of (variable, exponent) pairs; the constant
    term has the empty monomial ``()``.
    """

    __slots__ = ("terms",)

    def __init__(self, terms: Optional[Dict[Mono, Num]] = None):
        self.terms: Dict[Mono, Num] = {}
        for m, c in (terms or {}).items():
            c = _clean(c)
            if c != 0:
                self.terms[m] = c

    # constructors ---------------------------------------------------------
    @staticmethod
    def const(c: Union[int, Num]) -> "Poly":
        return Poly({(): Fraction(c) if isinstance(c, int) else c})

    @staticmethod
    def var(name: str) -> "Poly":
        return Poly({((name, 1),): Fraction(1)})

    # inspection -----------------------------------------------------------
    def is_const(self) -> bool:
        return all(m == () for m in self.terms)

    def value(self) -> Num:
        if not self.is_const():
            raise ExprError("expression is not a constant")
        return self.terms.get((), Fraction(0))

    def variables(self) -> set:
        return {v for m in self.terms for v, _ in m}

    def degree(self, var: Optional[str] = None) -> int:
        best = 0
        for m in self.terms:
            d = sum(e for v, e in m if var is None or v == var)
            best = max(best, d)
        return best

    def coeffs(self, var: str) -> Dict[int, Num]:
        """Coefficients by power of ``var`` (requires a univariate poly)."""
        out: Dict[int, Num] = {}
        for m, c in self.terms.items():
            if any(v != var for v, _ in m):
                raise ExprError("not univariate in " + var)
            p = sum(e for _, e in m)
            out[p] = out.get(p, Fraction(0)) + c
        return out

    def __eq__(self, other):  # structural equality with tolerance
        if not isinstance(other, Poly):
            return NotImplemented
        keys = set(self.terms) | set(other.terms)
        return all(num_equal(self.terms.get(k, Fraction(0)),
                             other.terms.get(k, Fraction(0))) for k in keys)

    def __hash__(self):
        return hash(tuple(sorted(self.terms)))

    def __repr__(self):
        return f"Poly({self.terms!r})"

    # arithmetic -----------------------------------------------------------
    def __add__(self, o: "Poly") -> "Poly":
        t = dict(self.terms)
        for m, c in o.terms.items():
            t[m] = t.get(m, Fraction(0)) + c
        return Poly(t)

    def __neg__(self) -> "Poly":
        return Poly({m: -c for m, c in self.terms.items()})

    def __sub__(self, o: "Poly") -> "Poly":
        return self + (-o)

    def __mul__(self, o: "Poly") -> "Poly":
        t: Dict[Mono, Num] = {}
        for m1, c1 in self.terms.items():
            for m2, c2 in o.terms.items():
                exps: Dict[str, int] = {}
                for v, e in m1 + m2:
                    exps[v] = exps.get(v, 0) + e
                m = tuple(sorted(exps.items()))
                t[m] = t.get(m, Fraction(0)) + c1 * c2
        return Poly(t)

    def __truediv__(self, o: "Poly") -> "Poly":
        if o.is_const():
            c = o.value()
            if c == 0:
                raise ExprError("division by zero")
            inv = Fraction(1) / c if isinstance(c, Fraction) else 1.0 / c
            return self * Poly.const(inv)
        if len(o.terms) == 1:  # divide by a monomial, term by term
            (dm, dc), = o.terms.items()
            dexp = dict(dm)
            t: Dict[Mono, Num] = {}
            for m, c in self.terms.items():
                exps = dict(m)
                for v, e in dexp.items():
                    if exps.get(v, 0) < e:
                        raise ExprError("not a polynomial quotient")
                    exps[v] -= e
                key = tuple(sorted((v, e) for v, e in exps.items() if e))
                t[key] = t.get(key, Fraction(0)) + (c / dc)
            return Poly(t)
        raise ExprError("division by a non-monomial")

    def __pow__(self, o: "Poly") -> "Poly":
        if not o.is_const():
            raise ExprError("variable exponent")
        e = o.value()
        if self.is_const():
            return Poly.const(_pow(self.value(), e))
        if not (isinstance(e, Fraction) and e.denominator == 1 and 0 <= e <= 12):
            raise ExprError("non-integer power of a polynomial")
        out = Poly.const(1)
        for _ in range(int(e)):
            out = out * self
        return out

    def subs(self, values: Dict[str, "Poly"]) -> "Poly":
        out = Poly()
        for m, c in self.terms.items():
            term = Poly.const(c)
            for v, e in m:
                base = values.get(v, Poly.var(v))
                term = term * (base ** Poly.const(e))
            out = out + term
        return out


# --------------------------------------------------------------------------
# tokenizer / parser

_SUPERSCRIPTS = {"⁰": "0", "¹": "1", "²": "2", "³": "3", "⁴": "4", "⁵": "5",
                 "⁶": "6", "⁷": "7", "⁸": "8", "⁹": "9", "⁻": "-"}
_SUBSCRIPTS = str.maketrans("₀₁₂₃₄₅₆₇₈₉", "0123456789")


def normalize(text: str) -> str:
    """Unicode math notation -> the ASCII subset :func:`parse` reads."""
    # An inline fraction of two integer literals ("3/8 ÷ 3/10", "243/25") reads
    # as one number, the way a student reads it, not as left-assoc division.
    # ("√3/2" stays √3 over 2.)
    s = re.sub(r"(?<![\w.)^/√∛∜])(\d+)/(\d+)(?![\w.(^√π])", r"(\1/\2)", text)
    for a in ("−", "–", "—", "‒"):
        s = s.replace(a, "-")
    for a in ("×", "·", "⋅", "∙", "•"):
        s = s.replace(a, "*")
    s = s.replace("÷", "/").replace("π", " pi ").replace("≤", "<=").replace("≥", ">=")
    s = s.replace("√", " sqrt ").replace("∛", " cbrt ").replace("∜", " qrt ")
    s = s.replace("ℓ", "l").replace(" ", " ").replace(" ", " ")
    s = s.replace("⅓", "(1/3)").replace("½", "(1/2)").replace("¼", "(1/4)")
    s = re.sub(r"log([₀₁₂₃₄₅₆₇₈₉]+)", lambda m: "log_" + m.group(1).translate(_SUBSCRIPTS), s)
    # runs of superscripts become ^(...)
    s = re.sub("[" + "".join(_SUPERSCRIPTS) + "]+",
               lambda m: "^(" + "".join(_SUPERSCRIPTS[c] for c in m.group(0)) + ")", s)
    return s.translate(_SUBSCRIPTS)


_TOKEN = re.compile(r"""
    (?P<num>\d+(?:\.\d+)?|\.\d+)
  | (?P<log>log_\{?\d+(?:\.\d+)?\}?|log_[a-z])
  | (?P<word>sqrt|cbrt|qrt|pi|ln|log)
  | (?P<id>[A-Za-z])
  | (?P<op><=|>=|[-+*/^()|=<>%,])
  | (?P<ws>\s+)
""", re.VERBOSE)

_FUNCS = {"sqrt", "cbrt", "qrt", "ln", "log"}


def tokenize(s: str) -> List[Tuple[str, str]]:
    out: List[Tuple[str, str]] = []
    pos = 0
    while pos < len(s):
        m = _TOKEN.match(s, pos)
        if not m:
            raise ExprError(f"unexpected character {s[pos]!r}")
        pos = m.end()
        kind = m.lastgroup
        if kind == "ws":
            continue
        out.append((kind, m.group(0)))
    return out


FunctionTable = Dict[str, Tuple[str, Poly]]


class _Parser:
    def __init__(self, tokens, functions: Optional[FunctionTable] = None,
                 env: Optional[Dict[str, "Poly"]] = None):
        self.t = tokens
        self.i = 0
        self.functions = functions or {}
        self.env = env or {}

    def peek(self, k: int = 0):
        j = self.i + k
        return self.t[j] if j < len(self.t) else (None, None)

    def take(self, value=None):
        kind, val = self.peek()
        if kind is None or (value is not None and val != value):
            raise ExprError(f"expected {value!r}, got {val!r}")
        self.i += 1
        return kind, val

    def at_end(self) -> bool:
        return self.i >= len(self.t)

    # grammar --------------------------------------------------------------
    def expr(self) -> Poly:
        left = self.term()
        while self.peek()[1] in ("+", "-"):
            op = self.take()[1]
            right = self.term()
            left = left + right if op == "+" else left - right
        return left

    def _starts_atom(self) -> bool:
        kind, val = self.peek()
        return kind in ("id", "word", "log") or val == "("

    def term(self) -> Poly:
        left = self.unary()
        while True:
            val = self.peek()[1]
            if val in ("*", "/"):
                self.take()
                right = self.unary()
                left = left * right if val == "*" else left / right
            elif self._starts_atom():
                left = left * self.power()  # implicit multiplication
            else:
                return left

    def unary(self) -> Poly:
        val = self.peek()[1]
        if val == "-":
            self.take()
            return -self.unary()
        if val == "+":
            self.take()
            return self.unary()
        return self.power()

    def power(self) -> Poly:
        base = self.postfix()
        if self.peek()[1] == "^":
            self.take()
            exp = self.unary()  # right-associative, allows 2^-1
            return base ** exp
        return base

    def postfix(self) -> Poly:
        a = self.atom()
        while self.peek()[1] == "%":
            self.take()
            a = a / Poly.const(100)
        return a

    def atom(self) -> Poly:
        kind, val = self.peek()
        if kind == "num":
            self.take()
            return Poly.const(Fraction(val))
        if val == "(":
            self.take()
            e = self.expr()
            self.take(")")
            return e
        if val == "|":
            self.take()
            e = self.expr()
            self.take("|")
            v = e.value()
            return Poly.const(abs(v))
        if kind == "word" and val == "pi":
            self.take()
            return Poly.const(math.pi)
        if kind in ("word", "log"):
            self.take()
            if kind == "log":
                base_txt = val[4:].strip("{}")
                if base_txt.isalpha():
                    raise ExprError("symbolic log base")
                base = float(base_txt)
            arg = self.power() if val in ("sqrt", "cbrt", "qrt") else self.postfix()
            x = arg.value()
            if val == "sqrt":
                return Poly.const(_sqrt(x))
            if val == "cbrt":
                return Poly.const(_root(x, 3))
            if val == "qrt":
                return Poly.const(_root(x, 4))
            if x <= 0:
                raise ExprError("log of a non-positive number")
            if val == "ln":
                return Poly.const(_clean(math.log(float(x))))
            if val == "log":
                return Poly.const(_clean(math.log10(float(x))))
            return Poly.const(_log_exact(x, base))
        if kind == "id":
            self.take()
            if val in self.functions and self.peek()[1] == "(":
                self.take("(")
                arg = self.expr()
                self.take(")")
                param, body = self.functions[val]
                return body.subs({param: arg})
            if val in self.env:
                return self.env[val]
            return Poly.var(val)
        raise ExprError(f"unexpected token {val!r}")


def _log_exact(x: Num, base: float) -> Num:
    r = math.log(float(x)) / math.log(base)
    rr = round(r)
    if isinstance(x, Fraction) and float(base).is_integer() and abs(r - rr) < 1e-9:
        b = Fraction(int(base))
        if b ** rr == x:
            return Fraction(rr)
    return _clean(r)


def parse(text: str, functions: Optional[FunctionTable] = None,
          env: Optional[Dict[str, Num]] = None) -> Poly:
    """Parse an expression (unicode or ASCII) into a :class:`Poly`.

    ``functions`` maps a name to (parameter, body) for calls like ``f(3)``;
    ``env`` substitutes numbers for variables while parsing (so ``|x − 8|``
    can be evaluated at a point).
    """
    penv = {k: Poly.const(v) for k, v in (env or {}).items()}
    p = _Parser(tokenize(normalize(text)), functions, penv)
    out = p.expr()
    if not p.at_end():
        raise ExprError(f"trailing input {p.peek()[1]!r}")
    return out


def evaluate(text: str, functions: Optional[FunctionTable] = None,
             env: Optional[Dict[str, Num]] = None) -> Num:
    """The numeric value of a constant expression."""
    return parse(text, functions, env).value()


_REL = re.compile(r"(<=|>=|<|>|=)")


def holds(text: str, env: Dict[str, Num]) -> bool:
    """Whether a chained relation such as ``3 < x < 13`` or ``|x − 8| <= 5``
    (or an equation) is true at the point ``env``."""
    low = text.strip()
    if re.search(r"\bor\b", low):
        return any(holds(part, env) for part in re.split(r"\bor\b", low))
    if re.search(r"\band\b", low):
        return all(holds(part, env) for part in re.split(r"\band\b", low))
    parts = _REL.split(normalize(text))
    if len(parts) < 3 or len(parts) % 2 == 0:
        raise ExprError("not a relation")
    vals = [evaluate(p, env=env) for p in parts[0::2]]
    for a, op, b in zip(vals, parts[1::2], vals[1:]):
        eq = num_equal(a, b, 1e-12)
        ok = {"<": a < b and not eq, ">": a > b and not eq, "<=": a < b or eq,
              ">=": a > b or eq, "=": eq}[op]
        if not ok:
            return False
    return True


def parse_equation(text: str, functions: Optional[FunctionTable] = None) -> Poly:
    """``lhs = rhs`` -> the polynomial ``lhs - rhs`` (== 0)."""
    s = normalize(text)
    if s.count("=") != 1 or "<=" in s or ">=" in s:
        raise ExprError("not a single equation")
    lhs, rhs = s.split("=")
    return parse(lhs, functions) - parse(rhs, functions)


def parse_function_def(text: str) -> Tuple[str, str, Poly]:
    """``f(x) = 11x + 15`` -> ("f", "x", Poly)."""
    m = re.fullmatch(r"\s*([a-zA-Z])\s*\(\s*([a-z])\s*\)\s*=\s*(.+?)\s*", normalize(text))
    if not m:
        raise ExprError("not a function definition")
    return m.group(1), m.group(2), parse(m.group(3))


# --------------------------------------------------------------------------
# solving


def solve_univariate(poly: Poly, var: Optional[str] = None) -> List[Num]:
    """Real roots (sorted, deduplicated) of ``poly == 0`` for degree 1 or 2."""
    vs = poly.variables()
    if var is None:
        if len(vs) != 1:
            raise ExprError("need exactly one variable")
        var = next(iter(vs))
    if vs - {var}:
        raise ExprError("extra variables")
    c = poly.coeffs(var)
    deg = max(c) if c else 0
    a2, a1, a0 = c.get(2, Fraction(0)), c.get(1, Fraction(0)), c.get(0, Fraction(0))
    if deg == 1:
        return [_clean(-a0 / a1)]
    if deg == 2:
        disc = a1 * a1 - 4 * a2 * a0
        if disc < 0:
            return []
        r = _sqrt(disc)
        roots = {_clean((-a1 - r) / (2 * a2)), _clean((-a1 + r) / (2 * a2))}
        return sorted(roots, key=float)
    raise ExprError(f"degree {deg} not supported")


def solve_linear_system(polys: Iterable[Poly], variables=("x", "y")) -> Optional[Dict[str, Num]]:
    """Unique solution of two linear equations in two variables (None if not unique)."""
    rows = []
    vx, vy = variables
    for p in polys:
        if p.degree() > 1 or p.variables() - {vx, vy}:
            raise ExprError("not a linear system in " + vx + "," + vy)
        t = p.terms
        rows.append((t.get(((vx, 1),), Fraction(0)), t.get(((vy, 1),), Fraction(0)),
                     -t.get((), Fraction(0))))
    if len(rows) != 2:
        raise ExprError("need two equations")
    (a, b, e), (c, d, f) = rows
    det = a * d - b * c
    if det == 0:
        return None
    return {vx: _clean((e * d - b * f) / det), vy: _clean((a * f - e * c) / det)}


# --------------------------------------------------------------------------
# answer-choice values

_UNIT_WORDS = re.compile(r"\s*(?:°|degrees?|units?|square units|cubic units)\s*$")


def parse_number(text: str) -> Optional[Num]:
    """Numeric value of a choice/answer string, or None if it isn't one.

    Accepts "$4,080", "4,080", "−7", "9/2", "0.80", "4%", "7√2", "54π",
    "72°"; rejects anything with variables or prose.
    """
    if text is None:
        return None
    s = str(text).strip().rstrip(".")
    if not s or len(s) > 40:
        return None
    s = s.replace("$", "")
    if re.search(r"\d\s*[–-]\s*\d", s):
        return None  # "100–119" is a range, not a subtraction (minus is "−")
    s = _UNIT_WORDS.sub("", s)
    s = re.sub(r"(?<=\d),(?=\d{3}(?!\d))", "", s)
    s = s.strip()
    if not re.fullmatch(r"[0-9.\s/+\-−–()%^√π·×*÷²³]+", s):
        return None
    if not re.search(r"\d", s):
        return None
    try:
        return evaluate(s)
    except (ExprError, ZeroDivisionError, OverflowError):
        return None
