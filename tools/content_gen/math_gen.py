"""Original SAT/ACT-style Math question generators (item families).

Every skill exposes several *families* per difficulty in ``FAMILIES`` (see
``registry.py`` for the contract). A family is one recognisable question form;
the lesson builder round-robins across families so a lesson reads like a real
test section instead of one template with new numbers.

Every item is constructed so the answer is computed (not authored), which makes
correctness machine-checkable; ``answer_verification`` carries the check.
Distractors model specific student errors and each carries a rationale. All
wording is original.

Conventions
-----------
* ``fn.sat_only = True``  -> grid-in (student_produced) families; the ACT has none.
* ``fn.small_space = True`` -> the family has a deliberately small item space
  (special triangles, trig ratios from Pythagorean triples, ...).
* Multiple-choice items supply at least 4 distractors where a natural 4th exists
  so they work with ``util.OPTION_COUNT`` of 4 (SAT) or 5 (ACT); numeric items
  are padded to ``OPTION_COUNT - 1`` distractors automatically.
"""
from __future__ import annotations

import math
import random
from fractions import Fraction

from . import util
from .util import mc, spr, num_str, shuffle_with_correct, pad_numeric_distractors


# --------------------------------------------------------------------------- #
# Shared helpers (also used by math_extra.py and math_act.py)
# --------------------------------------------------------------------------- #
NAMES = ["Maya", "Liam", "Aria", "Noah", "Priya", "Diego", "Ivy", "Omar",
         "Lena", "Theo", "Zoe", "Caleb", "Nina", "Ravi", "Sora", "Jonas",
         "Amara", "Felix", "Hana", "Mateo", "Keiko", "Tariq", "Elena", "Kwame",
         "Sofia", "Arjun", "Mila", "Dmitri", "Yara", "Lucas", "Imani", "Oscar"]


def _names():
    return NAMES


def _m(n):
    """Render a number with a typographic minus sign."""
    return num_str(n).replace("-", "−")


def _pm(b):
    """'+ 5' / '− 5' for a trailing constant."""
    return f"{'+' if b >= 0 else '−'} {num_str(abs(b))}"


def _lin(m, b, var="x"):
    """'3x + 5', '−x − 2', 'x', '7' (no zero terms, no unit coefficients)."""
    parts = []
    if m != 0:
        if m == 1:
            parts.append(var)
        elif m == -1:
            parts.append("−" + var)
        else:
            parts.append(f"{_m(m)}{var}")
    if b != 0 or not parts:
        parts.append(_pm(b) if parts else _m(b))
    return " ".join(parts)


def _coef(a, var="x"):
    return _lin(a, 0, var)


def _ask(rng, eq, var="x"):
    """Varied stems for 'solve this equation' items."""
    return rng.choice([
        f"If {eq}, what is the value of {var}?",
        f"What value of {var} satisfies the equation {eq}?",
        f"{eq}\nWhat is the solution to the given equation?",
        f"Which of the following is the solution to the equation {eq}?",
        f"In the equation {eq}, what is the value of {var}?",
        f"{eq}\nWhat value of {var} makes the equation true?",
    ])


def _spr_num(prompt, value, **kw):
    """spr() for ints or Fractions; terminating fractions also accept a decimal."""
    # A grid-in has no options, so a stem written for multiple choice is reworded.
    prompt = prompt.replace("Which of the following is the solution to",
                            "What is the solution to")
    if isinstance(value, Fraction):
        if value.denominator == 1:
            value = int(value)
        else:
            acc = [num_str(value)]
            d = value.denominator
            while d % 2 == 0:
                d //= 2
            while d % 5 == 0:
                d //= 5
            if d == 1:
                acc.append(num_str(float(value)))
            kw.setdefault("accepted", acc)
            value = float(value)
    return spr(prompt, value, **kw)


def _need():
    return util.OPTION_COUNT - 1


def _numeric_mc(rng, prompt, correct, distractor_specs, *, subskill, explanation,
                est=70, tags=None, fmt=num_str, verify=None,
                qtype="multiple_choice", correct_note="Correct.", stimulus=None,
                pad=None):
    """Assemble a multiple-choice item with deduped distractors.

    ``correct`` may be a number (int/float/Fraction) or a string (expression,
    statement, '12π', ...). Numeric answers are padded with near-miss values up
    to ``OPTION_COUNT - 1`` distractors; string answers must bring at least 3
    distinct distractors (4 preferred) or a ``pad(ds, n)`` callback.
    """
    need = _need()
    seen = {fmt(correct)}
    ds = []
    for val, rat in distractor_specs:
        s = fmt(val)
        if s in seen or not s:
            continue
        seen.add(s)
        ds.append((s, rat))
    numeric = isinstance(correct, (int, float, Fraction)) and not isinstance(correct, bool)
    if len(ds) < need:
        if pad is not None:
            ds = pad(ds, need)
        elif numeric:
            ds = pad_numeric_distractors(rng, correct, ds, need, fmt)
    if len(ds) < min(3, need):
        raise RuntimeError(
            f"could not build enough distinct distractors for correct={correct!r}")
    ds = ds[:need]
    options, ci, rats = shuffle_with_correct(rng, (fmt(correct), correct_note), ds)
    return mc(prompt, options, ci, rats, subskill=subskill, explanation=explanation,
              qtype=qtype, est=est, tags=tags, verify=verify, stimulus=stimulus)


def _text_mc(rng, prompt, correct, distractors, **kw):
    """Multiple choice over expressions/statements (strings)."""
    return _numeric_mc(rng, prompt, correct, distractors, fmt=str, **kw)


def _pow_distractors(rng, base, exp, specs, n=None):
    """Distinct power-string distractors (≠ base^exp), topped up with nearby
    exponents so string-answer items always have enough options."""
    n = n or _need()
    correct = f"{base}^{exp}"
    seen = {correct}
    out = []
    for s, rat in specs:
        if s not in seen:
            seen.add(s)
            out.append((s, rat))
    k = 1
    while len(out) < n:
        for cand in (exp + k, exp - k):
            s = f"{base}^{cand}"
            if s not in seen:
                seen.add(s)
                out.append((s, "Recompute the exponent step by step."))
                if len(out) == n:
                    break
        k += 1
    return out[:n]


def _pi_distractors(correct_coef, specs, n=None):
    """Distinct '<coef>π' distractors (≠ correct), topped up with nearby
    coefficients so π-string answers always have enough distinct options."""
    n = n or _need()
    seen = {correct_coef}
    out = []
    for coef, rat in specs:
        if coef not in seen and coef > 0:
            seen.add(coef)
            out.append((f"{num_str(coef)}π", rat))
    k = 1
    while len(out) < n:
        for c in (correct_coef + k, correct_coef - k):
            if c > 0 and c not in seen:
                seen.add(c)
                out.append((f"{num_str(c)}π", "Recheck the formula and recompute."))
                if len(out) == n:
                    break
        k += 1
    return out[:n]


def _pyth_triple(rng, max_c=41):
    prim = [(3, 4, 5), (5, 12, 13), (8, 15, 17), (7, 24, 25), (20, 21, 29), (9, 40, 41),
            (12, 35, 37), (11, 60, 61), (28, 45, 53), (33, 56, 65), (16, 63, 65), (48, 55, 73)]
    triples = sorted({(a * k, b * k, c * k) for a, b, c in prim for k in range(1, 13)})
    return rng.choice([t for t in triples if t[2] <= max_c])


def _tri_fig(a, b, c, angle=None, caption="Right triangle"):
    """Right-triangle figure: a = base, b = vertical leg, c = hypotenuse; the
    acute angle label sits at the bottom-right vertex (between a and c)."""
    fig = {"kind": "right_triangle", "caption": caption,
           "labels": {"a": str(a), "b": str(b), "c": str(c)}}
    if angle:
        fig["angle"] = angle
    return {"type": "figure", "figure": fig}


def _table(caption, headers, rows):
    return {"type": "table", "table": {"caption": caption, "headers": headers,
                                       "rows": [[str(x) for x in r] for r in rows]}}


def _money(v):
    if isinstance(v, Fraction):
        v = float(v)
    if isinstance(v, float) and not v.is_integer():
        return f"${v:,.2f}"
    return f"${int(v):,}"


def _ordinal(n):
    return {1: "first", 2: "second", 3: "third", 4: "fourth", 5: "fifth",
            6: "sixth", 7: "seventh", 8: "eighth", 9: "ninth", 10: "tenth"}.get(
        n, f"{n}th")


def _dispatch(table, skill):
    """Legacy entry point: pick a random family for the skill/difficulty."""
    from . import registry

    def fn(rng: random.Random, difficulty: str):
        fams = table[skill][difficulty]
        return registry.run_family(rng.choice(fams), rng, difficulty)
    fn.__name__ = skill
    return fn


# --------------------------------------------------------------------------- #
# linear_equations
# --------------------------------------------------------------------------- #
def le_two_step(rng, d):
    """Solve ax + b = c (ints -> negatives -> fractions/decimals)."""
    if d == "easy":
        a, x, b = rng.randint(2, 12), rng.randint(2, 20), rng.randint(1, 40)
        c = a * x + b
        eq = f"{_lin(a, b)} = {c}"
        expl = (f"Subtract {b} from both sides: {a}x = {c - b}. Divide by {a}: "
                f"x = {x}.")
        ds = [(x + 1, "Off by one; recheck the division."),
              (c - b, f"This is {a}x, not x; you still must divide by {a}."),
              (Fraction(c, a), "The constant must be subtracted before dividing."),
              (x - 1, "Off by one; recheck the subtraction.")]
    elif d == "medium":
        a = rng.choice([-1, 1]) * rng.randint(2, 12)
        x = rng.choice([v for v in range(-15, 16) if v != 0])
        b = rng.choice([v for v in range(-40, 41) if v != 0])
        c = a * x + b
        eq = (f"{_lin(a, b)} = {_m(c)}" if rng.random() < 0.6
              else f"{_m(c)} = {_lin(a, b)}")
        expl = (f"Isolate the x-term: {_m(a)}x = {_m(c)} − ({_m(b)}) = {_m(c - b)}. "
                f"Divide by {_m(a)}: x = {_m(x)}.")
        ds = [(-x, "Sign error when dividing by the coefficient."),
              (c - b, f"This is {_m(a)}x; divide by {_m(a)}."),
              (Fraction(c + b, a), "Subtract the constant; don't add it."),
              (x + rng.choice([-2, -1, 1, 2]), "Arithmetic slip; recheck each step.")]
    else:
        kind = rng.choice(["frac_coef", "decimal", "frac_answer"])
        if kind == "frac_coef":
            n = rng.randint(2, 9)
            k = rng.choice([v for v in range(-12, 13) if v != 0])
            x = n * k
            b = rng.choice([v for v in range(-20, 21) if v != 0])
            c = k + b
            eq = f"x/{n} {_pm(b)} = {_m(c)}"
            expl = (f"Subtract {_m(b)}: x/{n} = {_m(c - b)}. Multiply both sides by "
                    f"{n}: x = {_m(x)}.")
            ds = [(k, f"This is x/{n}; multiply by {n} to get x."),
                  (Fraction(k, n), f"Multiply by {n}; don't divide again."),
                  (n * (c + b), "Subtract the constant before multiplying."),
                  (-x, "Sign slip; recheck the subtraction.")]
        elif kind == "decimal":
            a = rng.choice([0.2, 0.4, 0.5, 0.6, 0.8, 1.2, 1.5, 2.5])
            x = rng.choice([v for v in range(-20, 21) if v != 0])
            b = rng.choice([v for v in range(-9, 10) if v != 0]) * 0.5
            c = round(a * x + b, 2)
            eq = f"{num_str(a)}x {_pm(b)} = {_m(c)}"
            expl = (f"Subtract {_m(b)}: {num_str(a)}x = {_m(round(c - b, 2))}. Divide by "
                    f"{num_str(a)}: x = {_m(x)}.")
            ds = [(round((c + b) / a, 2), "Subtract the constant; don't add it."),
                  (round(c - b, 2), f"This is {num_str(a)}x; divide by {num_str(a)}."),
                  (-x, "Sign slip when dividing."),
                  (round(c / a - b, 2), "Subtract the constant before dividing, not after.")]
        else:
            a = rng.randint(2, 9)
            p = rng.choice([v for v in range(-30, 31) if v != 0 and v % a != 0])
            x = Fraction(p, a)
            b = rng.choice([v for v in range(-25, 26) if v != 0])
            c = p + b
            eq = f"{_lin(a, b)} = {_m(c)}"
            expl = (f"Subtract {_m(b)}: {a}x = {_m(p)}. Divide by {a}: x = {num_str(x)}.")
            ds = [(Fraction(a, p), "This inverts the final division."),
                  (Fraction(c + b, a), "Subtract the constant; don't add it."),
                  (p, f"This is {a}x; divide by {a}."),
                  (-x, "Sign slip when dividing.")]
    return _numeric_mc(rng, _ask(rng, eq), x, ds, subskill="one_variable",
                       explanation=expl, tags=["algebra", "linear"],
                       verify=f"{eq.replace(chr(8722), '-')} at x={num_str(x)}",
                       correct_note="Correct: substituting back makes both sides equal.")


def le_both_sides(rng, d):
    """Solve ax + b = cx + e (variable on both sides)."""
    if d == "easy":
        a = rng.randint(3, 12)
        c = rng.randint(1, a - 1)
        x = rng.randint(2, 15)
        b = rng.randint(1, 20)
        e = (a - c) * x + b
    elif d == "medium":
        a = rng.choice([v for v in range(-9, 13) if v not in (0, 1)])
        c = rng.choice([v for v in range(-9, 10) if v not in (0, a)])
        x = rng.choice([v for v in range(-12, 13) if v != 0])
        b = rng.choice([v for v in range(-25, 26) if v != 0])
        e = (a - c) * x + b
    else:
        a = rng.choice([v for v in range(-9, 13) if v not in (0, 1)])
        c = rng.choice([v for v in range(-9, 10) if v != 0 and abs(a - v) >= 2])
        k = a - c
        p = rng.choice([v for v in range(-30, 31) if v != 0 and v % k != 0])
        x = Fraction(p, k)
        b = rng.choice([v for v in range(-25, 26) if v != 0])
        e = p + b
    eq = f"{_lin(a, b)} = {_lin(c, e)}"
    k = a - c
    expl = (f"Collect the x-terms: {_m(a)}x − ({_m(c)}x) = {_m(e)} − ({_m(b)}), so "
            f"{_m(k)}x = {_m(e - b)}. Divide by {_m(k)}: x = {num_str(x)}.")
    ds = [(e - b, f"This is {_m(k)}x, not x; divide by {_m(k)}."),
          (Fraction(e - b, a + c) if a + c != 0 else -x,
           "This divides by a + c instead of a − c."),
          (-x, "Sign slip when moving terms across the equals sign."),
          (Fraction(e + b, k), "The constant moves with the opposite sign.")]
    return _numeric_mc(rng, _ask(rng, eq), x, ds, subskill="one_variable",
                       explanation=expl, tags=["algebra", "linear"],
                       est=80 if d != "easy" else 70,
                       verify=f"x={num_str(x)} satisfies {eq.replace(chr(8722), '-')}")


def le_distribute(rng, d):
    """Equations with parentheses: distribute first."""
    if d == "easy":
        a, b, x = rng.randint(2, 9), rng.randint(1, 12), rng.randint(2, 15)
        c = a * (x + b)
        eq = f"{a}(x + {b}) = {c}"
        expl = (f"Distribute: {a}x + {a * b} = {c}. Subtract {a * b}: {a}x = "
                f"{c - a * b}. Divide by {a}: x = {x}.")
        ds = [(c - b, f"Distribute {a} to the {b} as well; don't just subtract {b}."),
              (x + b, f"This is x + {b}, the value inside the parentheses."),
              (Fraction(c, a) - b + 1, "Arithmetic slip after dividing."),
              (Fraction(c - b, a), f"You must subtract {a}·{b}, not {b}.")]
    elif d == "medium":
        a = rng.choice([v for v in range(-7, 9) if v not in (0, 1)])
        b = rng.choice([v for v in range(-12, 13) if v != 0])
        c = rng.choice([v for v in range(-15, 16) if v != 0])
        x = rng.choice([v for v in range(-12, 13) if v != 0])
        e = a * (x + b) + c
        eq = f"{_m(a)}(x {_pm(b)}) {_pm(c)} = {_m(e)}"
        expl = (f"Distribute: {_m(a)}x {_pm(a * b)} {_pm(c)} = {_m(e)}, so "
                f"{_m(a)}x = {_m(e - a * b - c)} and x = {_m(x)}.")
        ds = [(Fraction(e - c, a) if a else x + 1, f"This forgets to subtract {_m(a)}·({_m(b)})."),
              (-x, "Sign slip while distributing a negative."),
              (Fraction(e - b - c, a), f"Multiply {_m(b)} by {_m(a)} when distributing."),
              (x + b, "This is the value of x + b, not x.")]
    else:
        a = rng.randint(2, 7)
        b = rng.choice([v for v in range(-9, 10) if v != 0])
        c = rng.choice([v for v in range(-7, 8) if v not in (0, a)])
        e = rng.choice([v for v in range(-12, 13) if v != 0])
        # a(x + b) = c(x + e)  ->  (a - c) x = c e - a b
        num, den = c * e - a * b, a - c
        x = Fraction(num, den)
        eq = f"{a}(x {_pm(b)}) = {_m(c)}(x {_pm(e)})"
        expl = (f"Distribute both sides: {a}x {_pm(a * b)} = {_m(c)}x {_pm(c * e)}. "
                f"Collect: {_m(den)}x = {_m(num)}, so x = {num_str(x)}.")
        ds = [(-x, "Sign slip when collecting like terms."),
              (Fraction(num, a + c) if a + c else x + 1, "Subtract the x-coefficients; don't add them."),
              (Fraction(c * e + a * b, den), "The constant moves with the opposite sign."),
              (Fraction(den, num) if num else x - 1, "This inverts the final division.")]
    return _numeric_mc(rng, _ask(rng, eq), x, ds, subskill="one_variable",
                       explanation=expl, tags=["algebra", "linear", "distribute"],
                       est=85, verify=f"x={num_str(x)} in {eq.replace(chr(8722), '-')}")


_MODEL_CTX = [
    ("gym", "A gym charges a one-time sign-up fee of ${F} plus ${m} per month.",
     "the total cost C, in dollars, after t months", "C", "t"),
    ("plumber", "A plumber charges ${F} for a house call plus ${m} per hour of work.",
     "the total charge C, in dollars, for a job lasting t hours", "C", "t"),
    ("taxi", "A taxi ride costs ${F} to start plus ${m} per mile.",
     "the fare C, in dollars, for a ride of t miles", "C", "t"),
    ("phone", "A phone plan costs ${F} per month plus ${m} for each gigabyte of data used.",
     "the monthly bill C, in dollars, when t gigabytes are used", "C", "t"),
    ("tutor", "A tutor charges a ${F} registration fee plus ${m} per session.",
     "the total cost C, in dollars, for t sessions", "C", "t"),
]


def le_model_equation(rng, d):
    """'Which equation represents the situation?' (text options)."""
    if d == "easy":
        _, setup, asks, y, t = rng.choice(_MODEL_CTX)
        F, m = rng.randint(10, 90), rng.randint(2, 45)
        setup = setup.format(F=F, m=m)
        correct = f"{y} = {m}{t} + {F}"
        ds = [(f"{y} = {F}{t} + {m}", "This swaps the fixed fee and the per-unit rate."),
              (f"{y} = ({F} + {m}){t}", "The fixed fee is paid once, not every period."),
              (f"{y} = {m}{t} − {F}", "The fee adds to the cost; it doesn't subtract."),
              (f"{y} = {F + m}{t}", "Only the rate is multiplied by the count.")]
        expl = (f"The fee {F} is paid once and the rate {m} is multiplied by {t}, "
                f"so {correct}.")
        prompt = f"{setup} Which equation gives {asks}?"
    elif d == "medium":
        V = rng.randint(20, 90) * 10
        r = rng.randint(3, 40)
        thing, per = rng.choice([("A water tank holds {V} gallons and drains at a constant {r} gallons per minute.", "minute"),
                                 ("A phone battery starts at {V} units of charge and loses {r} units per hour of use.", "hour"),
                                 ("A gift card has a balance of ${V}, and ${r} is spent from it each week.", "week"),
                                 ("A hiker starts {V} meters from base camp and walks toward it at {r} meters per minute.", "minute")])
        setup = thing.format(V=V, r=r)
        correct = f"A = {V} − {r}t"
        ds = [(f"A = {V} + {r}t", "The amount decreases, so the rate term is subtracted."),
              (f"A = {r}t − {V}", "This starts at −{0} and increases; the signs are reversed.".format(V)),
              (f"A = ({V} − {r})t", f"Only {r} is lost per {per}; the start value isn't multiplied by t."),
              (f"A = {V} − {r}/t", "The loss is proportional to t, not to 1/t.")]
        expl = (f"Start at {V} and subtract {r} for each {per}: A = {V} − {r}t.")
        prompt = (f"{setup} Which equation gives the remaining amount A after t "
                  f"{per}s?")
    else:
        m = rng.randint(2, 12)
        b = rng.randint(3, 40)
        t1 = rng.randint(1, 6)
        t2 = t1 + rng.randint(2, 6)
        h1, h2 = m * t1 + b, m * t2 + b
        ctx, y, unit, per = rng.choice([
            ("A plant's height h, in centimeters, grows at a constant rate", "h", "cm", "week"),
            ("The number of members m in a club grows at a constant rate", "m", "members", "month"),
            ("The cost c, in dollars, of a custom order depends linearly on the number of items", "c", "dollars", "item"),
            ("The temperature T, in degrees, of a tank rises at a constant rate", "T", "degrees", "minute")])
        var = "n" if per == "item" else "t"
        prompt = (f"{ctx}. After {t1} {per}s it is {h1} {unit}, and after {t2} {per}s "
                  f"it is {h2} {unit}. Which equation gives {y} in terms of the number "
                  f"of {per}s {var}?")
        correct = f"{y} = {m}{var} + {b}"
        ds = [(f"{y} = {b}{var} + {m}", "This swaps the rate and the starting value."),
              (f"{y} = {m}{var} + {h1}", f"{h1} is the value at {var} = {t1}, not at {var} = 0."),
              (f"{y} = {h2 - h1}{var} + {b}", f"Divide the change {h2 - h1} by the {t2 - t1} {per}s it took."),
              (f"{y} = {m}{var} − {b}", "The starting value is added, not subtracted.")]
        expl = (f"Rate = ({h2} − {h1})/({t2} − {t1}) = {m} per {per}. Then {h1} = "
                f"{m}·{t1} + b gives b = {b}, so {correct}.")
    return _text_mc(rng, prompt, correct, ds, subskill="two_variable",
                    explanation=expl, tags=["algebra", "linear", "model"], est=85,
                    verify=f"model {correct}")


_INTERP_CTX = [
    ("The cost C, in dollars, of renting a kayak for h hours is given by C = {m}h + {b}.",
     "h", "the cost per hour of rental", "the fixed fee charged for any rental",
     "the number of hours rented", "the total cost of the rental"),
    ("A caterer's charge P, in dollars, for a party with g guests is P = {m}g + {b}.",
     "g", "the charge per guest", "the base charge regardless of the number of guests",
     "the number of guests", "the total charge for the party"),
    ("The total weight W, in pounds, of a crate holding n identical jars is W = {m}n + {b}.",
     "n", "the weight of one jar", "the weight of the empty crate",
     "the number of jars", "the total weight of the crate"),
    ("A technician's fee F, in dollars, for a repair taking t hours is F = {m}t + {b}.",
     "t", "the hourly labor rate", "the flat diagnostic fee",
     "the number of hours of labor", "the total repair fee"),
    ("The length L, in inches, of a spring holding a mass of x grams is L = {m}x + {b}.",
     "x", "the stretch, in inches, per gram of mass", "the length of the spring with no mass attached",
     "the mass hanging from the spring", "the total length of the spring"),
]


_INTERP_CTX_DOWN = [
    ("The amount of fuel F, in gallons, left in a truck's tank after it has driven m miles is F = {b} − {m}m.",
     "m", "the number of gallons of fuel used per mile driven", "the number of gallons in the tank before the trip began",
     "the number of miles the truck has driven so far on the trip", "the amount of fuel left in the tank after driving m miles"),
    ("The balance B, in dollars, of a gift card after it has been used to buy n coffees is B = {b} − {m}n.",
     "n", "the price, in dollars, of one coffee", "the balance of the card before any coffees were bought",
     "the number of coffees that have been bought with the card", "the balance remaining on the card after n coffees"),
    ("The depth D, in centimeters, of water in a leaking tank t hours after it was filled is D = {b} − {m}t.",
     "t", "the decrease in depth, in centimeters, each hour", "the depth of the water when the tank was full",
     "the number of hours that have passed since the tank was filled", "the depth of the water in the tank after t hours"),
    ("The distance R, in miles, remaining on a road trip after h hours of driving is R = {b} − {m}h.",
     "h", "the number of miles driven each hour", "the total length of the trip, in miles",
     "the number of hours that have been spent driving so far", "the distance remaining on the trip after h hours of driving"),
]


def le_interpret(rng, d):
    """Interpret the slope or intercept of a linear model in context."""
    setup, var, slope_mean, int_mean, var_mean, total_mean = rng.choice(
        _INTERP_CTX_DOWN if d == "hard" else _INTERP_CTX)
    m, b = rng.randint(2, 60), rng.randint(5, 120)
    if d == "hard":
        b = rng.randint(10, 60) * 10
    setup = setup.format(m=m, b=b)
    which = rng.choice(["slope", "intercept"])
    num = m if which == "slope" else b
    prompt = (f"{setup} Which of the following is the best interpretation of the "
              f"number {num} in this context?")
    if which == "slope":
        correct, note = slope_mean, "The coefficient of the variable is the rate of change."
        ds = [(int_mean, "That describes the constant term (the value when the variable is 0)."),
              (var_mean, "The variable itself is not a fixed number in the equation."),
              (total_mean, "The total is the output of the equation, not a single constant."),
              (f"the change in {var} for each 1-dollar change in cost" if "dollar" in setup
               else f"the change in {var} for each unit change in the output",
               "This reverses the roles of input and output.")]
        expl = f"In a linear model the coefficient of {var} is the rate of change: {correct}."
    else:
        correct, note = int_mean, "The constant term is the value when the variable is 0."
        ds = [(slope_mean, "That describes the coefficient of the variable (the rate)."),
              (var_mean, "The variable itself is not a fixed number in the equation."),
              (total_mean, "The total is the output, not the constant term."),
              (f"the value of {var} when the output is 0", "That would be the horizontal intercept, not the constant term.")]
        expl = f"When {var} = 0 the model equals the constant term, so it represents {correct}."
    return _text_mc(rng, prompt, correct, ds, subskill="slope_intercept",
                    explanation=expl, tags=["algebra", "linear", "interpret"],
                    est=80, verify=f"{which}={num}", correct_note=note)


def le_intercepts(rng, d):
    """Find an x- or y-intercept of a line."""
    if d == "easy":
        m = rng.choice([v for v in range(-9, 10) if v != 0])
        b = rng.choice([v for v in range(-20, 21) if v != 0])
        which = rng.choice(["y", "x"])
        if which == "x":
            # ensure integer x-intercept
            k = rng.choice([v for v in range(-9, 10) if v != 0])
            b = -m * k
            val = k
            prompt = (f"The graph of y = {_lin(m, b)} in the xy-plane crosses the "
                      f"x-axis at what value of x?")
            expl = f"Set y = 0: 0 = {_lin(m, b)}, so x = {_m(-b)}/{_m(m)} = {_m(val)}."
            ds = [(b, "That is the y-intercept (the constant term)."),
                  (-val, "Sign slip when solving 0 = mx + b."),
                  (m, "That is the slope, not an intercept."),
                  (-b, "Divide −b by the slope m.")]
        else:
            val = b
            prompt = rng.choice([
                f"What is the y-intercept of the graph of y = {_lin(m, b)} in the xy-plane?",
                f"The line y = {_lin(m, b)} is graphed in the xy-plane. At what y-value does it cross the y-axis?"])
            expl = f"The y-intercept is the value of y when x = 0: y = {_m(b)}."
            ds = [(m, "That is the slope, not the y-intercept."),
                  (-b, "Sign slip; the constant is the y-intercept as written."),
                  (Fraction(-b, m), "That is the x-intercept."),
                  (m + b, "That is y when x = 1, not x = 0.")]
    elif d == "medium":
        a = rng.choice([v for v in range(-9, 10) if v != 0])
        bb = rng.choice([v for v in range(-9, 10) if v != 0])
        which = rng.choice(["x", "y"])
        k = rng.choice([v for v in range(-8, 9) if v != 0])
        c = a * k if which == "x" else bb * k
        val = k
        prompt = (f"The line {_lin(a, 0)} {_pm(bb).replace(' ', ' ', 1)}y = {_m(c)} is "
                  f"graphed in the xy-plane. What is the {which}-coordinate of its "
                  f"{which}-intercept?")
        prompt = prompt.replace(f"{_pm(bb)}y", f"{'+' if bb > 0 else '−'} {_coef(abs(bb), 'y')}")
        other = "y" if which == "x" else "x"
        coef = a if which == "x" else bb
        expl = (f"Set {other} = 0: {_m(coef)}{which} = {_m(c)}, so {which} = "
                f"{_m(c)}/{_m(coef)} = {_m(val)}.")
        ds = [(Fraction(c, bb if which == "x" else a), f"That is the {other}-intercept."),
              (-val, "Sign slip in the division."),
              (c, f"Divide {_m(c)} by the coefficient of {which}."),
              (Fraction(coef, c) if c else val + 1, "This inverts the division.")]
    else:
        m = rng.choice([v for v in range(-8, 9) if v != 0])
        x1 = rng.randint(-8, 8)
        x2 = x1 + rng.choice([v for v in range(-6, 7) if v != 0])
        b = rng.choice([v for v in range(-15, 16) if v != 0])
        y1, y2 = m * x1 + b, m * x2 + b
        which = rng.choice(["y", "x"])
        if which == "y":
            val = b
            expl = (f"Slope = ({_m(y2)} − ({_m(y1)}))/({_m(x2)} − ({_m(x1)})) = {_m(m)}. "
                    f"Then {_m(y1)} = {_m(m)}·({_m(x1)}) + b gives b = {_m(b)}.")
        else:
            val = Fraction(-b, m)
            expl = (f"Slope = {_m(m)}, so y = {_lin(m, b)}. Set y = 0: x = "
                    f"{_m(-b)}/{_m(m)} = {num_str(val)}.")
        prompt = (f"A line in the xy-plane passes through the points ({_m(x1)}, {_m(y1)}) "
                  f"and ({_m(x2)}, {_m(y2)}). What is the {which}-coordinate of the "
                  f"{which}-intercept of the line?")
        ds = [(m, "That is the slope, not an intercept."),
              (Fraction(-b, m) if which == "y" else b, f"That is the {'x' if which == 'y' else 'y'}-intercept."),
              (-val, "Sign slip when solving for the intercept."),
              (y1 if which == "y" else x1, "That is a coordinate of a given point, not the intercept.")]
    return _numeric_mc(rng, prompt, val, ds, subskill="slope_intercept",
                       explanation=expl, tags=["algebra", "linear", "intercept"],
                       est=75 if d == "easy" else 90, verify=f"{which}-int={num_str(val)}")


def le_slope_points(rng, d):
    """Slope of a line through two points."""
    if d == "medium":
        m = rng.choice([v for v in range(-9, 10) if v != 0])
        x1 = rng.randint(-6, 9)
        x2 = x1 + rng.choice([v for v in range(-8, 9) if v != 0])
        b = rng.randint(-12, 12)
        y1, y2 = m * x1 + b, m * x2 + b
        val = m
    else:
        p, q = rng.choice([(1, 2), (1, 3), (2, 3), (3, 2), (3, 4), (4, 3), (2, 5), (5, 2),
                           (3, 5), (5, 3), (1, 4), (4, 5), (5, 4), (2, 7), (7, 2)])
        s = rng.choice([-1, 1])
        val = Fraction(s * p, q)
        x1 = rng.randint(-9, 9)
        k = rng.choice([v for v in range(-4, 5) if v != 0])
        x2 = x1 + q * k
        y1 = rng.randint(-12, 12)
        y2 = y1 + s * p * k
    prompt = rng.choice([
        f"What is the slope of the line that passes through the points ({_m(x1)}, {_m(y1)}) and ({_m(x2)}, {_m(y2)}) in the xy-plane?",
        f"In the xy-plane, a line passes through ({_m(x1)}, {_m(y1)}) and ({_m(x2)}, {_m(y2)}). What is the slope of the line?",
        f"Line k contains the points ({_m(x1)}, {_m(y1)}) and ({_m(x2)}, {_m(y2)}). What is the slope of line k?"])
    expl = (f"Slope = (y₂ − y₁)/(x₂ − x₁) = ({_m(y2)} − ({_m(y1)}))/({_m(x2)} − ({_m(x1)})) "
            f"= {_m(y2 - y1)}/{_m(x2 - x1)} = {num_str(val)}.")
    ds = [(Fraction(x2 - x1, y2 - y1) if y2 != y1 else val + 1, "This is run over rise; slope is rise over run."),
          (-val, "Sign slip; subtract the coordinates in the same order."),
          (y2 - y1, "That is only the change in y; divide by the change in x."),
          (Fraction(y2 + y1, x2 + x1) if x2 + x1 else val + 2, "Subtract the coordinates; don't add them.")]
    return _numeric_mc(rng, prompt, val, ds, subskill="slope_intercept",
                       explanation=expl, tags=["algebra", "linear", "slope"],
                       est=80, verify=f"({y2}-{y1})/({x2}-{x1})={num_str(val)}")


def le_parallel_perp(rng, d):
    """Slope of a line parallel or perpendicular to a given line."""
    rel = rng.choice(["parallel", "perpendicular"])
    if d == "medium":
        m = rng.choice([v for v in range(-9, 10) if v not in (0, 1, -1)])
        b = rng.randint(-12, 12)
        given = f"y = {_lin(m, b)}"
        slope = Fraction(m)
    else:
        a = rng.choice([v for v in range(-9, 10) if v not in (0, 1, -1)])
        bb = rng.choice([v for v in range(-9, 10) if v not in (0, 1, -1, a, -a)])
        c = rng.randint(-20, 20)
        given = f"{_coef(a)} {'+' if bb > 0 else '−'} {_coef(abs(bb), 'y')} = {_m(c)}"
        slope = Fraction(-a, bb)
    val = slope if rel == "parallel" else -1 / slope
    prompt = rng.choice([
        f"In the xy-plane, line ℓ is {rel} to the line {given}. What is the slope of line ℓ?",
        f"What is the slope of a line that is {rel} to the graph of {given} in the xy-plane?"])
    if rel == "parallel":
        expl = (f"The given line has slope {num_str(slope)}"
                + (f" (rewrite as y = {_lin(0, 0)}…: solve for y to see the slope −a/b)" if d == "hard" else "")
                + f"; parallel lines share the same slope, so the answer is {num_str(val)}.")
        expl = expl.replace(" (rewrite as y = 0…: solve for y to see the slope −a/b)",
                            " (solve for y: the slope is −a/b)")
        ds = [(-1 / slope, "That is the perpendicular slope (negative reciprocal)."),
              (-1 / slope - 1, "Recheck: parallel lines share the given slope exactly."),
              (-slope, "Parallel lines have the same slope, not the opposite sign."),
              (1 / slope, "Don't invert; parallel means equal slopes."),
              (slope + 1, "Recheck the slope of the given line.")]
    else:
        expl = (f"The given line has slope {num_str(slope)}; a perpendicular line has the "
                f"negative reciprocal slope, {num_str(val)}.")
        ds = [(slope, "That is the parallel slope; perpendicular needs the negative reciprocal."),
              (-1 / slope - 1, "Recheck the negative reciprocal; don't shift it."),
              (-slope, "Take the reciprocal as well as changing the sign."),
              (1 / slope, "Change the sign as well as taking the reciprocal."),
              (-1 / slope + 1, "Recheck the slope of the given line.")]
    return _numeric_mc(rng, prompt, val, ds, subskill="slope_intercept",
                       explanation=expl, tags=["algebra", "linear", rel], est=80,
                       verify=f"given slope {num_str(slope)}; {rel} -> {num_str(val)}")


def le_line_equation(rng, d):
    """Equation of a line (text options)."""
    m = rng.choice([v for v in range(-7, 8) if v != 0])
    b = rng.choice([v for v in range(-12, 13) if v != 0])
    if d == "medium":
        x1 = rng.choice([v for v in range(-6, 7) if v != 0])
        y1 = m * x1 + b
        prompt = (f"A line with slope {_m(m)} passes through the point ({_m(x1)}, {_m(y1)}) "
                  f"in the xy-plane. Which equation defines the line?")
        expl = (f"Use y = mx + b with m = {_m(m)}: {_m(y1)} = {_m(m)}·({_m(x1)}) + b, "
                f"so b = {_m(b)} and y = {_lin(m, b)}.")
        ds = [(f"y = {_lin(m, y1)}", f"{_m(y1)} is the y-value at x = {_m(x1)}, not the y-intercept."),
              (f"y = {_lin(m, -b)}", "Sign slip when solving for b."),
              (f"y = {_lin(x1, b)}", "The slope is the given m, not the x-coordinate."),
              (f"y = {_lin(-m, b)}", "The slope keeps its given sign."),
              (f"y = {_lin(b, m)}", "The slope and the y-intercept are swapped.")]
    else:
        x1 = rng.choice([v for v in range(-7, 8) if v != 0])
        x2 = x1 + rng.choice([v for v in range(-5, 6) if v != 0 and v != -x1])
        y1, y2 = m * x1 + b, m * x2 + b
        prompt = (f"Which of the following is an equation of the line that passes "
                  f"through the points ({_m(x1)}, {_m(y1)}) and ({_m(x2)}, {_m(y2)}) in the xy-plane?")
        expl = (f"Slope = ({_m(y2)} − ({_m(y1)}))/({_m(x2)} − ({_m(x1)})) = {_m(m)}. Then "
                f"{_m(y1)} = {_m(m)}({_m(x1)}) + b gives b = {_m(b)}, so y = {_lin(m, b)}.")
        ds = [(f"y = {_lin(-m, b)}", "The slope's sign is wrong; subtract in the same order."),
              (f"y = {_lin(m, y1)}", f"{_m(y1)} is y at x = {_m(x1)}, not the intercept."),
              (f"y = {_lin(m, -b)}", "Sign slip when solving for the intercept."),
              (f"y = {_lin(y2 - y1, b)}" if y2 - y1 != m else f"y = {_lin(m, b + 1)}",
               "Divide the change in y by the change in x to get the slope."),
              (f"y = {_lin(b, m)}", "The slope and the y-intercept are swapped.")]
    return _text_mc(rng, prompt, f"y = {_lin(m, b)}", ds, subskill="two_variable",
                    explanation=expl, tags=["algebra", "linear", "equation"], est=90,
                    verify=f"y={m}x+({b}) through ({x1},{y1})")


def le_literal(rng, d):
    """Solve a literal equation for one variable (text options)."""
    kind = rng.choice(["axby", "fraction", "formula"])
    if kind == "axby":
        a, bb, c = rng.randint(2, 9), rng.randint(2, 9), rng.randint(1, 30)
        prompt = (f"If {a}x + {bb}y = {c}, which of the following expresses y in terms "
                  f"of x?")
        correct = f"y = ({c} − {a}x)/{bb}"
        ds = [(f"y = ({a}x − {c})/{bb}", "Sign slip: subtract the x-term from the constant."),
              (f"y = {c} − {a}x", f"Both terms must be divided by {bb}."),
              (f"y = ({c} − {a}x)/{a}", f"Divide by the coefficient of y, which is {bb}."),
              (f"y = {c}/{bb} − {a}x", f"Divide the x-term by {bb} too.")]
        expl = f"Subtract {a}x: {bb}y = {c} − {a}x. Divide by {bb}: y = ({c} − {a}x)/{bb}."
    elif kind == "fraction":
        k, c = rng.randint(2, 9), rng.randint(1, 20)
        prompt = (f"If y = {k}x/(x + {c}), and the quantities are positive, which of the following "
                  f"expresses x in terms of y?")
        correct = f"x = {c}y/({k} − y)"
        ds = [(f"x = {c}y/(y − {k})", "Sign slip when factoring out x."),
              (f"x = ({k} − y)/({c}y)", "This is the reciprocal of the correct expression."),
              (f"x = {c}y/{k}", "The y-term on the x side must be moved before dividing."),
              (f"x = y(x + {c})/{k}", "x must not appear on the right side.")]
        expl = (f"Multiply out: y(x + {c}) = {k}x → yx + {c}y = {k}x → {c}y = {k}x − yx "
                f"= x({k} − y) → x = {c}y/({k} − y).")
    else:
        a, bb = rng.randint(2, 9), rng.randint(2, 9)
        prompt = (f"The formula P = {a}L + {bb}W relates the perimeter P of a figure to "
                  f"its length L and width W. Which equation gives W in terms of P and L?")
        correct = f"W = (P − {a}L)/{bb}"
        ds = [(f"W = (P + {a}L)/{bb}", "Subtract the L-term; don't add it."),
              (f"W = P/{bb} − {a}L", f"The L-term must also be divided by {bb}."),
              (f"W = (P − {bb}L)/{a}", "The coefficients are swapped."),
              (f"W = P − {a}L − {bb}", f"Divide by {bb} instead of subtracting it.")]
        expl = f"Subtract {a}L from both sides, then divide by {bb}: W = (P − {a}L)/{bb}."
    return _text_mc(rng, prompt, correct, ds, subskill="two_variable",
                    explanation=expl, tags=["algebra", "linear", "literal"], est=90,
                    verify=f"literal {kind}: {correct}")


def le_expression_value(rng, d):
    """Given one linear equation, find the value of a related expression."""
    a = rng.randint(2, 9)
    b = rng.choice([v for v in range(-15, 16) if v != 0])
    x = rng.choice([v for v in range(-9, 13) if v != 0])
    c = a * x + b
    if d == "medium":
        k = rng.randint(2, 4)
        target = f"{_lin(k * a, k * b)}"
        val = k * c
        expl = (f"{target} is {k} times ({_lin(a, b)}), so it equals {k}·{_m(c)} = {_m(val)}. "
                f"(You could also solve to get x = {_m(x)} and substitute.)")
        ds = [(c, f"That is the value of {_lin(a, b)}; multiply by {k}."),
              (x, "That is x itself, not the requested expression."),
              (k * c - k * b, "The constant term is multiplied too."),
              (k * x, "Multiply the whole expression's value, not just x.")]
    else:
        p = rng.choice([v for v in range(-9, 10) if v not in (0, a)])
        q = rng.choice([v for v in range(-20, 21) if v != 0])
        target = f"{_lin(p, q)}"
        val = p * x + q
        expl = (f"Solve: {a}x = {_m(c - b)}, so x = {_m(x)}. Then {target} = "
                f"{_m(p)}·({_m(x)}) {_pm(q)} = {_m(val)}.")
        ds = [(x, "That is x itself; substitute it into the expression."),
              (p * c + q, "Substitute x, not the whole equation's right side."),
              (p * x - q, "Check the sign of the constant term."),
              (p * (-x) + q, "Sign slip when solving for x.")]
    prompt = f"If {_lin(a, b)} = {_m(c)}, what is the value of {target}?"
    return _numeric_mc(rng, prompt, val, ds, subskill="one_variable",
                       explanation=expl, tags=["algebra", "linear"], est=80,
                       verify=f"x={x}; {target.replace(chr(8722), '-')}={val}")


def le_gridin(rng, d):
    """Student-produced response: solve a linear equation."""
    if d == "easy":
        a, x, b = rng.randint(2, 12), rng.randint(1, 25), rng.randint(1, 40)
        c = a * x + b
        eq = f"{_lin(a, b)} = {c}"
        expl = f"Subtract {b}: {a}x = {c - b}. Divide by {a}: x = {x}."
    elif d == "medium":
        a = rng.randint(3, 12)
        cc = rng.randint(1, a - 1)
        x = rng.randint(1, 20)
        b = rng.choice([v for v in range(-20, 21) if v != 0])
        e = (a - cc) * x + b
        eq = f"{_lin(a, b)} = {_lin(cc, e)}"
        expl = (f"Collect terms: {a - cc}x = {_m(e - b)}, so x = {x}.")
    else:
        a = rng.randint(2, 8)
        p = rng.choice([v for v in range(1, 40) if v % a != 0])
        x = Fraction(p, a)
        b = rng.choice([v for v in range(-20, 21) if v != 0])
        k = rng.randint(2, 5)
        eq = f"{k}({_lin(a, b)}) = {_m(k * (p + b))}"
        expl = (f"Divide both sides by {k}: {_lin(a, b)} = {_m(p + b)}. Then {a}x = {p} "
                f"and x = {num_str(x)}.")
    prompt = _ask(rng, eq)
    return _spr_num(prompt, x, subskill="one_variable", explanation=expl,
                    tags=["algebra", "linear", "grid-in"], est=75,
                    verify=f"x={num_str(x)} satisfies {eq.replace(chr(8722), '-')}")


le_gridin.sat_only = True


# --------------------------------------------------------------------------- #
# linear_inequalities
# --------------------------------------------------------------------------- #
def li_extreme_integer(rng, d):
    """Greatest/least integer satisfying an inequality (flip at medium+)."""
    if d == "easy":
        a, x, b = rng.randint(2, 12), rng.randint(2, 16), rng.randint(1, 30)
        c = a * x + b
        sym = rng.choice(["≤", "<"])
        ineq = f"{_lin(a, b)} {sym} {c}"
        val = x if sym == "≤" else x - 1
        expl = (f"Subtract {b}: {a}x {sym} {c - b}. Divide by {a}: x {sym} {x}. "
                f"The greatest integer is {val}.")
        word = "greatest"
        ds = [(x + 1, f"x = {x + 1} makes the left side exceed {c}."),
              (c - b, f"This is {a}x; divide by {a}."),
              (val - 1, "This satisfies the inequality but is not the greatest such value."),
              (x if sym == "<" else x - 1, "Check whether the endpoint itself is allowed.")]
    elif d == "medium":
        a, x, b = rng.randint(2, 9), rng.randint(2, 16), rng.randint(1, 30)
        c = -a * x + b
        sym = rng.choice(["≤", "<", "≥", ">"])
        ineq = f"{_lin(-a, b)} {sym} {_m(c)}"
        # -a x + b sym c  ->  -a x sym c - b  ->  x flipsym x
        flipped = {"≤": "≥", "<": ">", "≥": "≤", ">": "<"}[sym]
        if flipped in ("≥", ">"):
            word = "least"
            val = x if flipped == "≥" else x + 1
        else:
            word = "greatest"
            val = x if flipped == "≤" else x - 1
        expl = (f"Subtract {b}: {_m(-a)}x {sym} {_m(c - b)}. Dividing by {_m(-a)} flips the "
                f"sign: x {flipped} {x}. The {word} integer is {val}.")
        ds = [(x + 1 if word == "greatest" else x - 1, "This value does not satisfy the inequality."),
              (-x, "Sign slip; the solution is positive."),
              (val - 1 if word == "greatest" else val + 1, f"This works but is not the {word} such value."),
              (x if val != x else x + (1 if word == "least" else -1), "Check whether the endpoint is included.")]
    else:
        a = rng.randint(2, 9)
        lo_x = rng.randint(-6, 6)
        hi_x = lo_x + rng.randint(2, 9)
        b = rng.choice([v for v in range(-15, 16) if v != 0])
        lo, hi = a * lo_x + b, a * hi_x + b
        ineq = f"{_m(lo)} < {_lin(a, b)} ≤ {_m(hi)}"
        val = hi_x - lo_x
        word = "how many"
        expl = (f"Subtract {_m(b)} and divide by {a}: {_m(lo_x)} < x ≤ {_m(hi_x)}. The "
                f"integers from {_m(lo_x + 1)} to {_m(hi_x)} number {val}.")
        ds = [(val + 1, "The left endpoint is not included (strict inequality)."),
              (val - 1, "The right endpoint is included; count it."),
              (hi - lo, "Divide by the coefficient before counting."),
              (hi_x, "Count the integers in the interval, not the endpoint value.")]
    if word == "how many":
        prompt = f"How many integer values of x satisfy {ineq}?"
    else:
        prompt = rng.choice([
            f"What is the {word} integer value of x that satisfies {ineq}?",
            f"If {ineq}, what is the {word} possible integer value of x?"])
    return _numeric_mc(rng, prompt, val, ds, subskill="one_variable",
                       explanation=expl, tags=["algebra", "inequality"], est=80,
                       verify=f"{ineq.replace(chr(8722), '-')} -> {word} {val}")


def li_solution_set(rng, d):
    """Choose the solution set (text options like 'x > 3')."""
    sym = rng.choice(["<", ">", "≤", "≥"])
    flip = {"<": ">", ">": "<", "≤": "≥", "≥": "≤"}
    if d == "easy":
        a, b = rng.randint(2, 9), rng.randint(1, 20)
        x = rng.choice([v for v in range(-8, 13) if v != 0])
        c = a * x + b
        ineq = f"{_lin(a, b)} {sym} {_m(c)}"
        res = sym
        expl = f"Subtract {b}: {a}x {sym} {_m(c - b)}. Divide by {a}: x {sym} {_m(x)}."
    elif d == "medium":
        a, b = rng.randint(2, 9), rng.randint(1, 20)
        x = rng.choice([v for v in range(-8, 13) if v != 0])
        c = -a * x + b
        ineq = f"{_lin(-a, b)} {sym} {_m(c)}"
        res = flip[sym]
        expl = (f"Subtract {b}: {_m(-a)}x {sym} {_m(c - b)}. Dividing by {_m(-a)} flips the "
                f"inequality: x {res} {_m(x)}.")
    else:
        a = rng.randint(2, 9)
        cc = rng.choice([v for v in range(a + 1, a + 8)])
        x = rng.choice([v for v in range(-8, 11) if v != 0])
        b = rng.choice([v for v in range(-15, 16) if v != 0])
        e = (a - cc) * x + b
        ineq = f"{_lin(a, b)} {sym} {_lin(cc, e)}"
        res = flip[sym]
        expl = (f"Collect: {_m(a - cc)}x {sym} {_m(e - b)}. Dividing by the negative "
                f"{_m(a - cc)} flips the sign: x {res} {_m(x)}.")
    correct = f"x {res} {_m(x)}"
    ds = [(f"x {flip[res]} {_m(x)}", "The direction of the inequality is reversed."),
          (f"x {res} {_m(-x)}", "Sign slip on the boundary value."),
          (f"x {flip[res]} {_m(-x)}", "Both the direction and the sign are wrong."),
          (f"x {res.replace('<', '≤').replace('>', '≥') if res in '<>' else res.replace('≤', '<').replace('≥', '>')} {_m(x)}",
           "Check whether the boundary is included.")]
    prompt = rng.choice([f"Which of the following describes all solutions to {ineq}?",
                         f"What is the solution set of the inequality {ineq}?"])
    return _text_mc(rng, prompt, correct, ds, subskill="one_variable",
                    explanation=expl, tags=["algebra", "inequality"], est=75,
                    verify=f"{ineq.replace(chr(8722), '-')} -> {correct.replace(chr(8722), '-')}")


def li_model(rng, d):
    """Which inequality represents the situation (text options)."""
    name = rng.choice(NAMES)
    if d == "easy":
        B, f, p = rng.randint(30, 200), rng.randint(5, 40), rng.randint(2, 15)
        item = rng.choice(["ride tickets", "raffle tickets", "songs", "arcade tokens", "bus passes"])
        prompt = (f"{name} has ${B} to spend at a fair that charges a ${f} entry fee plus "
                  f"${p} for each of the {item}. Which inequality represents the number of "
                  f"{item} n that {name} can buy?")
        correct = f"{p}n + {f} ≤ {B}"
        ds = [(f"{p}n + {f} ≥ {B}", "Spending must not exceed the budget; the sign is reversed."),
              (f"{f}n + {p} ≤ {B}", "The per-item price, not the fee, multiplies n."),
              (f"{p}n ≤ {B} + {f}", "The fee reduces what is left for items; it isn't added to the budget."),
              (f"({p} + {f})n ≤ {B}", "The entry fee is paid once, not per item.")]
        expl = f"Cost is {p}n + {f}, which must be at most {B}: {correct}."
    elif d == "medium":
        T, r = rng.randint(100, 500), rng.randint(5, 30)
        prompt = (f"A truck can carry at most {T} kilograms. It already holds a {rng.randint(20, 80)}-kilogram "
                  f"toolbox, and each crate loaded weighs {r} kilograms. Which inequality gives the "
                  f"number of crates c that can be added?")
        tb = int(prompt.split("holds a ")[1].split("-")[0])
        correct = f"{r}c + {tb} ≤ {T}"
        ds = [(f"{r}c + {tb} ≥ {T}", "The load must stay at or below the limit."),
              (f"{r}c ≤ {T} + {tb}", "The toolbox uses up capacity; it doesn't add to it."),
              (f"{tb}c + {r} ≤ {T}", "The crate weight, not the toolbox, multiplies c."),
              (f"{r}c + {tb} < {T}", "Exactly reaching the limit is allowed ('at most').")]
        expl = f"Total weight {r}c + {tb} must be at most {T}: {correct}."
    else:
        a, b = rng.randint(2, 9), rng.randint(2, 9)
        if a == b:
            b += 1
        T, M = rng.randint(10, 40), rng.randint(60, 300)
        prompt = (f"A bakery makes muffins and scones. Each muffin takes {a} minutes of "
                  f"oven time and each scone takes {b} minutes, and the oven is available "
                  f"for at most {M} minutes. The bakery must make at least {T} items in all. "
                  f"If m muffins and s scones are made, which system of inequalities "
                  f"represents the constraints?")
        correct = f"{a}m + {b}s ≤ {M}; m + s ≥ {T}"
        ds = [(f"{a}m + {b}s ≥ {M}; m + s ≤ {T}", "Both inequality directions are reversed."),
              (f"{a}m + {b}s ≤ {M}; m + s ≤ {T}", "'At least' {0} items means m + s ≥ {0}.".format(T)),
              (f"{b}m + {a}s ≤ {M}; m + s ≥ {T}", "The minutes per muffin and per scone are swapped."),
              (f"m + s ≤ {M}; {a}m + {b}s ≥ {T}", "Oven minutes, not item counts, are limited by {0}.".format(M))]
        expl = (f"Oven time {a}m + {b}s cannot exceed {M}, and the count m + s must be "
                f"at least {T}.")
    return _text_mc(rng, prompt, correct, ds, subskill="one_variable",
                    explanation=expl, tags=["algebra", "inequality", "model"], est=85,
                    verify=f"model {correct}")


def li_word_max(rng, d):
    """Maximum/minimum count from a budget constraint (numeric)."""
    name = rng.choice(NAMES)
    if d == "easy":
        p, n = rng.randint(2, 15), rng.randint(3, 30)
        B = p * n + rng.randint(0, p - 1)
        item = rng.choice(["notebooks", "snacks", "stickers", "pens", "postcards"])
        prompt = (f"{name} has ${B} and wants to buy as many {item} as possible at ${p} "
                  f"each. What is the greatest number of {item} {name} can buy?")
        val = n
        expl = f"{B} ÷ {p} = {B / p:.2f}, so at most {n} {item} (the next one would cost too much)."
        ds = [(n + 1, f"{n + 1} {item} would cost ${p * (n + 1)}, more than ${B}."),
              (B - p, "Subtracting one price does not give a count."),
              (n - 1, "One more item still fits the budget."),
              (p, "That is the price, not the count.")]
    elif d == "medium":
        f, p, n = rng.randint(5, 60), rng.randint(3, 25), rng.randint(3, 25)
        B = f + p * n + rng.randint(0, p - 1)
        prompt = (f"A car rental costs ${f} plus ${p} per day. {name} can spend at most "
                  f"${B}. What is the maximum number of whole days {name} can rent the car?")
        val = n
        expl = (f"{f} + {p}d ≤ {B} → d ≤ ({B} − {f})/{p} = {(B - f) / p:.2f}, so d = {n}.")
        ds = [(n + 1, "That many days would exceed the budget."),
              (B // p, "Subtract the fixed cost before dividing by the daily rate."),
              (n - 1, "One more day still fits the budget."),
              (B - f, "That is the money left for daily charges, not the number of days.")]
    else:
        price = rng.randint(8, 40)
        cost = rng.randint(2, price - 3)
        fixed = rng.randint(50, 400)
        n = rng.randint(5, 60)
        # profit = (price - cost) n - fixed >= target
        target = (price - cost) * n - fixed - rng.randint(0, price - cost - 1)
        val = n
        prompt = (f"A club sells T-shirts for ${price} each. Each shirt costs ${cost} to "
                  f"make, and the club paid ${fixed} for a printing setup. What is the "
                  f"least number of shirts the club must sell to make a profit of at least "
                  f"${target}?")
        expl = (f"Profit = ({price} − {cost})n − {fixed} ≥ {target} → n ≥ "
                f"{(target + fixed) / (price - cost):.2f}, so n = {n}.")
        ds = [(n - 1, "That many shirts leaves the profit below the target."),
              (math.ceil((target + fixed) / price), "Use the profit per shirt (price − cost), not the price."),
              (math.ceil(target / (price - cost)), "The setup cost must be covered too."),
              (n + 1, "One fewer shirt already reaches the target.")]
    return _numeric_mc(rng, prompt, val, ds, subskill="one_variable",
                       explanation=expl, tags=["algebra", "inequality", "word-problem"],
                       est=90, qtype="multi_step_math", verify=f"n={val}")


def li_ordered_pair(rng, d):
    """Which ordered pair satisfies an inequality / system of inequalities."""
    m = rng.choice([v for v in range(-4, 5) if v != 0])
    b = rng.randint(-6, 6)
    sym = rng.choice(["<", ">", "≤", "≥"])

    def ok(x, y, sym=sym, m=m, b=b):
        v = m * x + b
        return {"<": y < v, ">": y > v, "≤": y <= v, "≥": y >= v}[sym]

    if d == "medium":
        prompt = (f"Which of the following ordered pairs (x, y) is a solution to the "
                  f"inequality y {sym} {_lin(m, b)}?")
        pts = [(x, y) for x in range(-5, 6) for y in range(-9, 10)]
        good = [p for p in pts if ok(*p)]
        bad = [p for p in pts if not ok(*p)]
        gx, gy = rng.choice(good)
        bads = rng.sample(bad, 4)
        expl = (f"Substitute ({_m(gx)}, {_m(gy)}): {_m(gy)} {sym} {_m(m)}({_m(gx)}) {_pm(b)} = "
                f"{_m(m * gx + b)} is true.")
        ds = [(f"({_m(x)}, {_m(y)})", f"{_m(y)} {sym} {_m(m * x + b)} is false.") for x, y in bads]
        verify = f"({gx},{gy}) satisfies y {sym} {m}x+{b}"
    else:
        m2 = rng.choice([v for v in range(-4, 5) if v not in (0, m)])
        b2 = rng.randint(-6, 6)
        sym2 = rng.choice(["<", ">", "≤", "≥"])

        def ok2(x, y):
            return ok(x, y) and ok(x, y, sym2, m2, b2)
        pts = [(x, y) for x in range(-6, 7) for y in range(-10, 11)]
        good = [p for p in pts if ok2(*p)]
        bad = [p for p in pts if not ok2(*p) and (ok(*p) or ok(*p, sym2, m2, b2))]
        if len(good) < 1 or len(bad) < 4:
            return li_ordered_pair(rng, d)
        gx, gy = rng.choice(good)
        bads = rng.sample(bad, 4)
        prompt = (f"y {sym} {_lin(m, b)}\ny {sym2} {_lin(m2, b2)}\nWhich ordered pair "
                  f"(x, y) is a solution to the system of inequalities above?")
        expl = (f"({_m(gx)}, {_m(gy)}) satisfies both: {_m(gy)} {sym} {_m(m * gx + b)} and "
                f"{_m(gy)} {sym2} {_m(m2 * gx + b2)}.")
        ds = [(f"({_m(x)}, {_m(y)})", "This pair fails at least one of the two inequalities.")
              for x, y in bads]
        verify = f"({gx},{gy}) satisfies both"
    return _text_mc(rng, prompt, f"({_m(gx)}, {_m(gy)})", ds, subskill="graph_regions",
                    explanation=expl, tags=["algebra", "inequality", "graph"], est=90,
                    verify=verify)


def li_must_be_true(rng, d):
    """If x satisfies an inequality, which statement must be true (text)."""
    x0 = rng.randint(-6, 12)
    k = rng.randint(2, 6)
    c = rng.randint(1, 12)
    prompt = f"If x > {_m(x0)}, which of the following must be true?"
    correct = f"{k}x + {c} > {_m(k * x0 + c)}"
    ds = [(f"{k}x + {c} < {_m(k * x0 + c)}", f"Multiplying by {k} and adding {c} keeps the direction of the inequality."),
          (f"−x > {_m(-x0)}", "Multiplying by −1 flips the inequality."),
          (f"x − {c} > {_m(x0)}", f"Subtracting {c} lowers the boundary to {_m(x0 - c)}."),
          (f"x² > {x0 * x0}", "Squaring doesn't preserve inequalities when x can be negative or small.")]
    expl = (f"Multiplying x > {_m(x0)} by the positive number {k} gives {k}x > {_m(k * x0)}, "
            f"and adding {c} gives {correct}.")
    return _text_mc(rng, prompt, correct, ds, subskill="one_variable",
                    explanation=expl, tags=["algebra", "inequality", "reasoning"], est=70,
                    verify=f"x>{x0} -> {k}x+{c}>{k * x0 + c}")


def li_gridin(rng, d):
    """Grid-in: an extreme integer value satisfying an inequality."""
    if d == "easy":
        a, x, b = rng.randint(2, 12), rng.randint(2, 20), rng.randint(1, 30)
        c = a * x + b
        prompt = f"What is the greatest integer value of x for which {_lin(a, b)} ≤ {c}?"
        val = x
        expl = f"{a}x ≤ {c - b}, so x ≤ {x}. The greatest integer is {x}."
    elif d == "medium":
        a, x, b = rng.randint(2, 9), rng.randint(2, 20), rng.randint(1, 30)
        c = b - a * x
        prompt = f"What is the least integer value of x for which {_lin(-a, b)} ≤ {_m(c)}?"
        val = x
        expl = f"{_m(-a)}x ≤ {_m(c - b)}; dividing by {_m(-a)} flips the sign: x ≥ {x}."
    else:
        a = rng.randint(2, 8)
        lo_x = rng.randint(-5, 5)
        hi_x = lo_x + rng.randint(3, 9)
        b = rng.choice([v for v in range(-10, 11) if v != 0])
        prompt = (f"How many integers x satisfy {_m(a * lo_x + b)} ≤ {_lin(a, b)} < "
                  f"{_m(a * hi_x + b)}?")
        val = hi_x - lo_x
        expl = (f"Subtract {_m(b)}, divide by {a}: {_m(lo_x)} ≤ x < {_m(hi_x)}, which holds "
                f"{val} integers.")
    return _spr_num(prompt, val, subskill="one_variable", explanation=expl,
                    tags=["algebra", "inequality", "grid-in"], est=75, verify=f"val={val}")


li_gridin.sat_only = True


# --------------------------------------------------------------------------- #
# systems_of_equations
# --------------------------------------------------------------------------- #
def sys_solve(rng, d):
    """Solve a 2×2 linear system for x, y, or a combination."""
    x = rng.randint(-8, 12)
    y = rng.randint(-8, 12)
    if d == "easy":
        x, y = rng.randint(1, 12), rng.randint(1, 12)
        a1, b1 = 1, rng.randint(1, 5)
        a2, b2 = rng.randint(1, 5), rng.choice([-1, 1]) * rng.randint(1, 5)
        if a1 * b2 - a2 * b1 == 0:
            b2 += 1
        target = rng.choice(["x", "y"])
    elif d == "medium":
        a1, b1 = rng.randint(2, 7), rng.choice([-1, 1]) * rng.randint(1, 7)
        a2, b2 = rng.randint(1, 7), rng.choice([-1, 1]) * rng.randint(1, 7)
        while a1 * b2 - a2 * b1 == 0:
            a2 = rng.randint(1, 7)
        target = rng.choice(["x", "y", "x + y"])
    else:
        a1, b1 = rng.randint(2, 9), rng.choice([-1, 1]) * rng.randint(2, 9)
        a2, b2 = rng.randint(2, 9), rng.choice([-1, 1]) * rng.randint(2, 9)
        while a1 * b2 - a2 * b1 == 0:
            a2 = rng.randint(2, 9)
        target = rng.choice(["x + y", "x − y", "xy", "2x + y"])
    c1 = a1 * x + b1 * y
    c2 = a2 * x + b2 * y
    val = {"x": x, "y": y, "x + y": x + y, "x − y": x - y, "xy": x * y,
           "2x + y": 2 * x + y}[target]
    e1 = f"{_lin(a1, 0)} {'+' if b1 > 0 else '−'} {_coef(abs(b1), 'y')} = {_m(c1)}"
    e2 = f"{_lin(a2, 0)} {'+' if b2 > 0 else '−'} {_coef(abs(b2), 'y')} = {_m(c2)}"
    prompt = rng.choice([
        f"{e1}\n{e2}\nIf (x, y) is the solution to the system of equations above, what is the value of {target}?",
        f"The system of equations {e1} and {e2} has solution (x, y). What is the value of {target}?",
        f"{e1}\n{e2}\nWhat is the value of {target} for the solution (x, y) of the system above?"])
    expl = (f"Solving by elimination gives x = {_m(x)} and y = {_m(y)}, so {target} = "
            f"{_m(val)}.")
    ds = [(y if target == "x" else x, "This is the other variable's value."),
          (x - y if target == "x + y" else x + y, "This combines the variables the wrong way."),
          (-val, "Sign slip in the elimination step."),
          (val + rng.choice([1, 2, -1]), "Arithmetic slip; substitute back to check.")]
    return _numeric_mc(rng, prompt, val, ds, subskill="elimination",
                       explanation=expl, qtype="multi_step_math",
                       tags=["algebra", "systems"], est=95, verify=f"x={x},y={y}")


def sys_substitution(rng, d):
    """Intersection of two lines given in slope-intercept form."""
    m1 = rng.choice([v for v in range(-6, 7) if v != 0])
    m2 = rng.choice([v for v in range(-6, 7) if v not in (0, m1)])
    x = rng.randint(-8, 10) if d != "easy" else rng.randint(1, 10)
    b1 = rng.randint(-15, 15)
    y = m1 * x + b1
    b2 = y - m2 * x
    which = rng.choice(["x", "y"]) if d != "easy" else "x"
    val = x if which == "x" else y
    prompt = rng.choice([
        f"y = {_lin(m1, b1)}\ny = {_lin(m2, b2)}\nThe graphs of the equations above intersect at the point (x, y). What is the value of {which}?",
        f"In the xy-plane, the lines y = {_lin(m1, b1)} and y = {_lin(m2, b2)} intersect at a single point. What is the {which}-coordinate of that point?"])
    expl = (f"Set the right sides equal: {_lin(m1, b1)} = {_lin(m2, b2)} → {_m(m1 - m2)}x = "
            f"{_m(b2 - b1)} → x = {_m(x)}. Then y = {_m(m1)}({_m(x)}) {_pm(b1)} = {_m(y)}.")
    ds = [(y if which == "x" else x, "That is the other coordinate of the intersection."),
          (-val, "Sign slip when collecting terms."),
          (b2 - b1, "Divide by the difference of the slopes."),
          (val + rng.choice([1, -1, 2]), "Arithmetic slip; substitute back into both equations.")]
    return _numeric_mc(rng, prompt, val, ds, subskill="substitution",
                       explanation=expl, tags=["algebra", "systems"], est=85,
                       verify=f"intersection ({x},{y})")


def sys_word(rng, d):
    """Word problems that translate to a system."""
    name = rng.choice(NAMES)
    if d == "easy":
        a = rng.randint(5, 40)
        b = rng.randint(1, a - 1)
        s, diff = a + b, a - b
        prompt = (f"The sum of two numbers is {s} and their difference is {diff}. What "
                  f"is the larger number?")
        val = a
        expl = f"Adding x + y = {s} and x − y = {diff} gives 2x = {s + diff}, so x = {a}."
        ds = [(b, "This is the smaller number."),
              (s // 2, "Averaging the sum ignores the difference."),
              (s - diff, "That is twice the smaller number."),
              (a + 1, "Arithmetic slip; recheck (sum + difference) ÷ 2.")]
    elif d == "medium":
        pa, pc = rng.randint(8, 20), rng.randint(3, 7)
        na, nc = rng.randint(10, 80), rng.randint(10, 80)
        n, T = na + nc, pa * na + pc * nc
        prompt = (f"A theater sold {n} tickets for a show. Adult tickets cost ${pa} and "
                  f"child tickets cost ${pc}, and the total collected was ${T}. How many "
                  f"adult tickets were sold?")
        val = na
        expl = (f"Let a + c = {n} and {pa}a + {pc}c = {T}. Substituting c = {n} − a: "
                f"{pa}a + {pc}({n} − a) = {T} → {pa - pc}a = {T - pc * n} → a = {na}.")
        ds = [(nc, "This is the number of child tickets."),
              (T // pa, "Not all tickets were adult tickets."),
              (n - na + 1, "Recheck which variable you solved for."),
              (na + 2, "Arithmetic slip; check that the totals match.")]
    else:
        w1, w2 = rng.randint(2, 9), rng.randint(2, 9)
        if w1 == w2:
            w2 += 1
        n1, n2 = rng.randint(3, 30), rng.randint(3, 30)
        total_items, total_w = n1 + n2, w1 * n1 + w2 * n2
        prompt = (f"{name} packs {total_items} boxes for shipping. Small boxes weigh "
                  f"{w1} kg each and large boxes weigh {w2} kg each, and the whole shipment "
                  f"weighs {total_w} kg. How many large boxes are in the shipment?")
        val = n2
        expl = (f"s + l = {total_items} and {w1}s + {w2}l = {total_w}. Substituting s = "
                f"{total_items} − l gives {w2 - w1}l = {total_w - w1 * total_items}, so "
                f"l = {n2}.")
        ds = [(n1, "This is the number of small boxes."),
              (total_w // w2, "Not every box is large; use the system."),
              (total_items - n2 + 1, "Recheck which variable you solved for."),
              (n2 - 1, "Arithmetic slip; check the total weight.")]
    return _numeric_mc(rng, prompt, val, ds, subskill="substitution",
                       explanation=expl, qtype="multi_step_math",
                       tags=["algebra", "systems", "word-problem"], est=100,
                       verify=f"val={val}")


def sys_which_system(rng, d):
    """Choose the system that models the situation (text options)."""
    if d == "easy":
        n, T = rng.randint(10, 60), rng.randint(100, 900)
        p1, p2 = rng.randint(2, 9), rng.randint(10, 25)
        prompt = (f"A shop sold {n} items, some pens at ${p1} each and some notebooks at "
                  f"${p2} each, for a total of ${T}. If p pens and k notebooks were sold, "
                  f"which system of equations represents this situation?")
        correct = f"p + k = {n}; {p1}p + {p2}k = {T}"
        ds = [(f"p + k = {T}; {p1}p + {p2}k = {n}", "The item count and the dollar total are swapped."),
              (f"p + k = {n}; {p2}p + {p1}k = {T}", "The prices are attached to the wrong items."),
              (f"{p1}p + {p2}k = {n}; p + k = {T}", "Prices multiply the counts in the money equation."),
              (f"p + k = {n}; {p1 + p2}(p + k) = {T}", "Each item type has its own price.")]
        expl = f"Counts add to {n}; money is {p1} per pen and {p2} per notebook, totaling {T}."
    else:
        r1, r2 = rng.randint(2, 9), rng.randint(2, 9)
        if r1 == r2:
            r2 += 1
        h, D = rng.randint(2, 9), rng.randint(20, 90)
        prompt = (f"A cyclist rode for a total of {h} hours. For part of the time she rode "
                  f"on flat ground at {r1} miles per hour, and for the rest she climbed at "
                  f"{r2} miles per hour, covering {D} miles in all. If f and c are the hours "
                  f"spent on flat ground and climbing, which system models the ride?")
        correct = f"f + c = {h}; {r1}f + {r2}c = {D}"
        ds = [(f"f + c = {D}; {r1}f + {r2}c = {h}", "Hours add to {0}, miles add to {1}.".format(h, D)),
              (f"f + c = {h}; {r2}f + {r1}c = {D}", "The speeds are matched to the wrong segments."),
              (f"f + c = {h}; f/{r1} + c/{r2} = {D}", "Distance is rate × time, not time ÷ rate."),
              (f"{r1}f + {r2}c = {h}; f + c = {D}", "Rate × time gives miles, not hours.")]
        expl = f"Times add to {h} hours; distances {r1}f and {r2}c add to {D} miles."
    return _text_mc(rng, prompt, correct, ds, subskill="substitution",
                    explanation=expl, tags=["algebra", "systems", "model"], est=85,
                    verify=f"system {correct}")


def sys_solution_count(rng, d):
    """How many solutions / value of a constant for no solution."""
    a, b = rng.randint(2, 9), rng.randint(2, 9)
    k = rng.randint(2, 4)
    c = rng.randint(1, 30)
    if d == "medium":
        case = rng.choice(["none", "inf", "one"])
        if case == "none":
            e2 = f"{k * a}x + {k * b}y = {k * c + rng.randint(1, 9)}"
            correct, note = "no solution", "The left sides are proportional but the right sides are not, so the lines are parallel."
        elif case == "inf":
            e2 = f"{k * a}x + {k * b}y = {k * c}"
            correct, note = "infinitely many solutions", f"The second equation is {k} times the first: the same line."
        else:
            e2 = f"{k * a}x + {k * b + rng.randint(1, 5)}y = {k * c}"
            correct, note = "exactly one solution", "The slopes differ, so the lines cross once."
        prompt = (f"{a}x + {b}y = {c}\n{e2}\nHow many solutions does the system of "
                  f"equations above have?")
        others = [s for s in ["no solution", "infinitely many solutions", "exactly one solution"]
                  if s != correct]
        ds = [(others[0], "Compare the ratios of the coefficients and constants."),
              (others[1], "Compare the ratios of the coefficients and constants."),
              ("exactly two solutions", "Two distinct lines meet at most once.")]
        expl = note
        verify = f"case={case}"
        subskill = "elimination"
    else:
        # ax + by = c ; (ka)x + p y = q  no solution -> p = kb and q != kc
        q = k * c + rng.randint(1, 9)
        prompt = (f"{a}x + {b}y = {c}\n{k * a}x + py = {q}\nIn the system of equations "
                  f"above, p is a constant. For what value of p does the system have no "
                  f"solution?")
        correct = k * b
        ds = [(k * c, "That makes the constants proportional, not the y-coefficients."),
              (b, "The y-coefficient must scale by the same factor as the x-coefficient."),
              (k * a, "That is the x-coefficient; find the matching y-coefficient."),
              (Fraction(b, k), "Multiply b by k; don't divide.")]
        expl = (f"No solution means parallel lines: the coefficients must be proportional "
                f"with factor {k} (since {k * a} = {k}·{a}), so p = {k}·{b} = {k * b}, while "
                f"{q} ≠ {k}·{c} keeps the lines distinct.")
        verify = f"p={k * b}"
        subskill = "elimination"
        return _numeric_mc(rng, prompt, correct, ds, subskill=subskill,
                           explanation=expl, tags=["algebra", "systems", "reasoning"],
                           est=95, verify=verify)
    return _text_mc(rng, prompt, correct, ds, subskill=subskill, explanation=expl,
                    tags=["algebra", "systems", "reasoning"], est=85, verify=verify)


def sys_gridin(rng, d):
    """Grid-in: value from a system's solution."""
    x, y = rng.randint(1, 12), rng.randint(1, 12)
    if d == "easy":
        b1 = rng.randint(1, 5)
        a2, b2 = rng.randint(1, 5), -rng.randint(1, 5)
        a1 = 1
        target, val = rng.choice([("x", x), ("y", y)])
    elif d == "medium":
        a1, b1 = rng.randint(2, 7), rng.randint(1, 7)
        a2, b2 = rng.randint(1, 7), -rng.randint(1, 7)
        while a1 * b2 - a2 * b1 == 0:
            a2 += 1
        target, val = rng.choice([("x", x), ("y", y), ("x + y", x + y)])
    else:
        a1, b1 = rng.randint(2, 9), rng.randint(2, 9)
        a2, b2 = rng.randint(2, 9), -rng.randint(2, 9)
        while a1 * b2 - a2 * b1 == 0:
            a2 += 1
        target, val = rng.choice([("xy", x * y), ("x + y", x + y), ("3x − y", 3 * x - y)])
        if val < 0:
            target, val = "x + y", x + y
    c1, c2 = a1 * x + b1 * y, a2 * x + b2 * y
    e1 = f"{_lin(a1, 0)} {'+' if b1 > 0 else '−'} {_coef(abs(b1), 'y')} = {_m(c1)}"
    e2 = f"{_lin(a2, 0)} {'+' if b2 > 0 else '−'} {_coef(abs(b2), 'y')} = {_m(c2)}"
    prompt = (f"{e1}\n{e2}\nIf (x, y) satisfies the system of equations above, what is "
              f"the value of {target}?")
    expl = f"Solving gives x = {x} and y = {y}, so {target} = {val}."
    return _spr_num(prompt, val, subskill="elimination", explanation=expl,
                    tags=["algebra", "systems", "grid-in"], est=95, verify=f"x={x},y={y}")


sys_gridin.sat_only = True


# --------------------------------------------------------------------------- #
# functions
# --------------------------------------------------------------------------- #
def _fx(a, b, c=None):
    """'3x + 5' or '2x² − 3x + 1' with clean signs."""
    if c is None:
        return _lin(a, b)
    s = "x²" if a == 1 else ("−x²" if a == -1 else f"{_m(a)}x²")
    if b:
        s += f" {'+' if b > 0 else '−'} {'x' if abs(b) == 1 else str(abs(b)) + 'x'}"
    if c:
        s += f" {_pm(c)}"
    return s


def fn_evaluate(rng, d):
    """Evaluate f(k) for a linear (easy) or quadratic (medium/hard) rule."""
    if d == "easy":
        a, b, k = rng.randint(2, 12), rng.randint(-15, 15), rng.randint(-8, 10)
        val = a * k + b
        rule = _fx(a, b)
        expl = f"f({_m(k)}) = {a}·({_m(k)}) {_pm(b)} = {_m(a * k)} {_pm(b)} = {_m(val)}."
        ds = [(a + k + b, "This adds k to the coefficient instead of multiplying."),
              (a * k - b, "Check the sign of the constant term."),
              (val + a, "Arithmetic slip; recompute a·k."),
              (a * (k + b), "Multiply a by k first, then add b.")]
    else:
        a = rng.randint(1, 6) if d == "medium" else rng.choice([-3, -2, -1, 2, 3, 4, 5])
        b = rng.randint(-9, 9)
        c = rng.randint(-12, 12)
        k = rng.randint(-5, 6) if d == "medium" else rng.choice([-7, -6, -5, -4, -3, 4, 5, 6, 7])
        val = a * k * k + b * k + c
        rule = _fx(a, b, c)
        expl = (f"f({_m(k)}) = {_m(a)}·({_m(k)})² {_pm(b)}·({_m(k)}) {_pm(c)} = "
                f"{_m(a * k * k)} {_pm(b * k)} {_pm(c)} = {_m(val)}.")
        ds = [(a * k + b * k + c, "This squares only the coefficient, not x."),
              (a * k * k - b * k + c, "Watch the sign on the middle term."),
              (-a * k * k + b * k + c, "(−k)² is positive; don't carry the sign through the square."),
              (val + a, "Arithmetic slip in squaring; recompute (k)².")]
    prompt = rng.choice([
        f"The function f is defined by f(x) = {rule}. What is the value of f({_m(k)})?",
        f"If f(x) = {rule}, what is f({_m(k)})?",
        f"For the function f defined by f(x) = {rule}, what is f({_m(k)})?"])
    return _numeric_mc(rng, prompt, val, ds, subskill="evaluate", explanation=expl,
                       tags=["functions", "evaluate"], est=70 if d == "easy" else 85,
                       verify=f"f({k})={val}")


def fn_solve_input(rng, d):
    """Given f(x) = N, find x (or the zero of f)."""
    a = rng.randint(2, 9)
    x = rng.randint(-7, 9) if d != "hard" else rng.choice([v for v in range(-9, 10) if v != 0])
    b = rng.randint(-12, 12)
    if d == "easy":
        x = rng.randint(1, 12)
        n = a * x + b
        prompt = f"The function f is defined by f(x) = {_fx(a, b)}. If f(x) = {_m(n)}, what is the value of x?"
        expl = f"Set {_fx(a, b)} = {_m(n)}: {a}x = {_m(n - b)}, so x = {_m(x)}."
        ds = [(n - b, "This is a·x (before dividing by the coefficient a)."),
              (n + b, "Subtract b before dividing, don't add it."),
              (a * n + b, "This evaluates f(n) instead of solving f(x) = n."),
              (x + 1, "Off by one; recheck the division.")]
        val = x
    elif d == "medium":
        b = -a * x
        prompt = rng.choice([
            f"The function f is defined by f(x) = {_fx(a, b)}. For what value of x is f(x) = 0?",
            f"What is the zero of the function f(x) = {_fx(a, b)}?"])
        expl = f"Set {_fx(a, b)} = 0: {a}x = {_m(-b)}, so x = {_m(x)}."
        ds = [(b, "That is f(0), the y-intercept, not the zero."),
              (-x, "Sign slip when moving the constant."),
              (a, "The zero is −b/a, not the coefficient."),
              (Fraction(a, -b) if b else x + 1, "This inverts the division.")]
        val = x
    else:
        r = rng.choice([v for v in range(-9, 10) if v != 0])
        g = rng.choice([v for v in range(-9, 10) if v != 0])
        # f(x) = (x - r)(x - g) + k  ; find positive x with f(x) = k
        k = rng.randint(-10, 10)
        bb, cc = -(r + g), r * g + k
        rule = _fx(1, bb, cc)
        val = max(r, g)
        prompt = (f"The function f is defined by f(x) = {rule}. What is the greatest "
                  f"value of x for which f(x) = {_m(k)}?")
        expl = (f"Set {rule} = {_m(k)}: x² {_pm(bb).replace(' ', ' ', 1)}x {_pm(r * g)} = 0, "
                f"which factors as (x − ({_m(r)}))(x − ({_m(g)})) = 0. The greater "
                f"solution is {_m(val)}.")
        expl = expl.replace(f"x² {_pm(bb)}x", f"{_fx(1, bb)}".replace("x", "x²", 1) + "")
        expl = (f"Set {rule} = {_m(k)}: {_fx(1, bb, r * g)} = 0, which factors as "
                f"(x − ({_m(r)}))(x − ({_m(g)})) = 0. The greater solution is {_m(val)}.")
        ds = [(min(r, g), "That is the lesser solution."),
              (-val, "Sign slip when reading the roots from the factors."),
              (r + g, "That is the sum of the solutions, not one of them."),
              (k, "That is the output value, not the input.")]
    return _numeric_mc(rng, prompt, val, ds, subskill="interpret", explanation=expl,
                       tags=["functions", "solve"], est=80, verify=f"x={val}")


def fn_table(rng, d):
    """Function given by a table (data_interpretation)."""
    xs = sorted(rng.sample(range(-4, 10), 5))
    if d == "easy":
        ys = [rng.randint(-10, 30) for _ in xs]
        if len(set(ys)) < 5:
            return fn_table(rng, d)
        i = rng.randrange(5)
        if rng.random() < 0.5:
            prompt = f"The table gives selected values of the function f. What is the value of f({_m(xs[i])})?"
            val = ys[i]
            expl = f"Find x = {_m(xs[i])} in the table; the corresponding f(x) is {_m(val)}."
            ds = [(xs[i], "That is the input, not the output."),
                  (ys[(i + 1) % 5], "That is the output for a different input; read the row for x = {0}.".format(_m(xs[i]))),
                  (ys[(i - 1) % 5], "Read across the correct row."),
                  (sum(ys) // 5, "No calculation is needed; read the table.")]
        else:
            prompt = f"The table gives selected values of the function f. For what value of x is f(x) = {_m(ys[i])}?"
            val = xs[i]
            expl = f"Find {_m(ys[i])} in the f(x) column; the matching x is {_m(val)}."
            ds = [(ys[i], "That is the output; the question asks for the input."),
                  (xs[(i + 1) % 5], "That input gives a different output."),
                  (xs[(i - 1) % 5], "Read the x in the same row."),
                  (-val if val else val + 1, "Sign slip reading the table.")]
        rows = [[x, y] for x, y in zip(xs, ys)]
        subskill = "evaluate"
    else:
        m = rng.choice([v for v in range(-6, 7) if v != 0])
        b = rng.choice([v for v in range(-12, 13) if v not in (0, m, -m)])
        ys = [m * x + b for x in xs]
        rows = [[x, y] for x, y in zip(xs, ys)]
        if d == "medium":
            k = rng.choice([v for v in range(-6, 15) if v not in xs])
            val = m * k + b
            prompt = (f"The table gives values of the linear function f. What is the "
                      f"value of f({_m(k)})?")
            expl = (f"The outputs change by {_m(m)} for each increase of 1 in x, so "
                    f"f(x) = {_fx(m, b)} and f({_m(k)}) = {_m(val)}.")
            ds = [(m * k, "Include the constant term b."),
                  (m + k + b, "Multiply the slope by k; don't add."),
                  (val + m, "Off by one step of the pattern."),
                  (b, "That is f(0); extend the pattern to x = {0}.".format(_m(k)))]
            subskill = "evaluate"
        else:
            prompt = ("The table gives values of the linear function f. Which equation "
                      "defines f?")
            val = f"f(x) = {_fx(m, b)}"
            expl = (f"Between consecutive rows, f changes by {_m(m)} per unit of x, so the "
                    f"slope is {_m(m)}; using one row gives b = {_m(b)}.")
            ds = [(f"f(x) = {_fx(b, m)}", "The slope and intercept are swapped."),
                  (f"f(x) = {_fx(m, -b)}", "Sign slip solving for the constant."),
                  (f"f(x) = {_fx(-m, b)}", "The outputs {0} as x increases, so the slope's sign is wrong.".format(
                      "increase" if m > 0 else "decrease")),
                  (f"f(x) = {_fx(m, ys[0])}", f"{_m(ys[0])} is f({_m(xs[0])}), not f(0)."),
                  (f"f(x) = {_fx(2 * m, b)}", "The slope is the change in f per unit change in x; check the x-spacing in the table.")]
            subskill = "interpret"
            return _text_mc(rng, prompt, val, ds, subskill=subskill, explanation=expl,
                            qtype="data_interpretation", tags=["functions", "table"],
                            est=90, stimulus=_table("Values of f", ["x", "f(x)"], rows),
                            verify=f"f(x)={m}x+({b})")
    return _numeric_mc(rng, prompt, val, ds, subskill=subskill, explanation=expl,
                       qtype="data_interpretation", tags=["functions", "table"],
                       est=70 if d == "easy" else 85,
                       stimulus=_table("Values of f", ["x", "f(x)"], rows),
                       verify=f"val={val}")


def fn_compose_transform(rng, d):
    """Composition f(g(k)) (medium) or a transformed function g(x) = f(x − h) + k (hard)."""
    a, b = rng.randint(2, 6), rng.randint(-8, 8)
    c, e = rng.randint(2, 5), rng.randint(-6, 6)
    k = rng.randint(-4, 5)
    if d == "medium":
        inner = c * k + e
        val = a * inner + b
        prompt = (f"The functions f and g are defined by f(x) = {_fx(a, b)} and "
                  f"g(x) = {_fx(c, e)}. What is the value of f(g({_m(k)}))?")
        expl = (f"First g({_m(k)}) = {_m(c)}({_m(k)}) {_pm(e)} = {_m(inner)}. Then "
                f"f({_m(inner)}) = {a}·({_m(inner)}) {_pm(b)} = {_m(val)}.")
        ds = [(c * (a * k + b) + e, "This computes g(f(k)); evaluate g first."),
              ((a * k + b) * (c * k + e), "Composition is not multiplication."),
              (inner, "That is g(k); now apply f."),
              ((a * k + b) + (c * k + e), "Composition is not addition.")]
    else:
        h, v = rng.choice([v for v in range(-5, 6) if v != 0]), rng.choice([v for v in range(-6, 7) if v != 0])
        # f(x) = a x^2 + b  ; g(x) = f(x - h) + v ; g(k)
        f_at = a * (k - h) ** 2 + b
        val = f_at + v
        rule = f"{_m(a)}x² {_pm(b)}"
        prompt = (f"The function f is defined by f(x) = {rule}, and the function g is "
                  f"defined by g(x) = f(x {_pm(-h)}) {_pm(v)}. What is the value of g({_m(k)})?")
        expl = (f"g({_m(k)}) = f({_m(k)} {_pm(-h)}) {_pm(v)} = f({_m(k - h)}) {_pm(v)} = "
                f"{_m(a)}·({_m(k - h)})² {_pm(b)} {_pm(v)} = {_m(val)}.")
        ds = [(a * (k + h) ** 2 + b + v, "Inside the parentheses the shift is x − h; check its sign."),
              (a * k * k + b + v, "Apply the horizontal shift before squaring."),
              (f_at, "Don't forget to add the vertical shift."),
              (f_at - v, "The vertical shift is added, not subtracted.")]
    return _numeric_mc(rng, prompt, val, ds, subskill="evaluate", explanation=expl,
                       tags=["functions", "composition" if d == "medium" else "transformation"],
                       est=95, qtype="multi_step_math", verify=f"val={val}")


def fn_interpret(rng, d):
    """Interpret a function model in context (text options)."""
    ctx = rng.choice([
        ("The function p(t) = {b} − {m}t gives the amount of water, in gallons, remaining in a tank t minutes after a valve opens.",
         "p(0)", "the amount of water in the tank when the valve opens", "the number of minutes until the tank is empty",
         "the number of gallons drained each minute", "the amount of water remaining after {b} minutes"),
        ("The function C(n) = {m}n + {b} gives the cost, in dollars, of printing n posters.",
         "C(0)", "the cost before any posters are printed", "the cost of printing one poster",
         "the number of posters that cost ${b}", "the cost per poster"),
        ("The function h(t) = {b} + {m}t gives the height, in centimeters, of a plant t weeks after it was planted.",
         "h(0)", "the height of the plant when it was planted", "the number of weeks until it reaches {b} cm",
         "the growth, in centimeters, each week", "the height after {b} weeks"),
    ])
    m, b = rng.randint(2, 25), rng.randint(30, 500)
    setup, expr, correct, w1, w2, w3 = [s.format(m=m, b=b) if isinstance(s, str) else s for s in ctx]
    if d == "medium":
        prompt = f"{setup} Which of the following is the best interpretation of {expr} = {b}?"
        ds = [(f"the total change in the output of the function over the first {b} units of input",
               "The constant term is a starting value, not a change over an interval."),
              (w1, "That would be an input (a time or count) set equal to the output, which reverses the roles."),
              (w2, "That describes the coefficient of the variable, the rate of change."),
              (w3, "The input {0} here is 0, not {1}.".format(expr[2], b))]
        expl = f"{expr} is the output when the input is 0, so {b} is {correct}."
    else:
        k = rng.randint(2, 12)
        var = expr[2]
        prompt = (f"{setup} Which of the following is the best interpretation of the "
                  f"statement {expr[0]}({k}) {'−' if '−' in setup else '+'} … Which statement best "
                  f"describes the meaning of the number {m} in this model?")
        prompt = (f"{setup} Which statement best describes the meaning of the number {m} "
                  f"in this model?")
        correct = w2
        ds = [(ctx[2].format(m=m, b=b), "That describes the constant term, the value at input 0."),
              (f"the value of the function when the input {var} is equal to {m}", f"{m} is a coefficient, not an input."),
              (f"the input {var} at which the output of the function is equal to {m}", "The number multiplies the variable; it is a rate, not an input."),
              (f"the total change in the output over {m} {'minutes' if var == 't' and 'tank' in setup else ('weeks' if var == 't' else 'posters')}",
               "The coefficient is the change per single unit of input.")]
        expl = f"In a linear model the coefficient of {var} is the rate of change: {correct}."
    return _text_mc(rng, prompt, correct, ds, subskill="interpret", explanation=expl,
                    tags=["functions", "interpret"], est=85, verify=f"interpret {expr}")


def fn_undefined(rng, d):
    """For what x is a rational function undefined, or f(x) = 0 for a product."""
    a = rng.randint(1, 9)
    b = rng.choice([v for v in range(-9, 10) if v != 0])
    if rng.random() < 0.5:
        prompt = (f"The function f is defined by f(x) = (x {_pm(a)})/(x {_pm(b)}). For what "
                  f"value of x is f(x) undefined?")
        val = -b
        expl = f"A fraction is undefined when its denominator is 0: x {_pm(b)} = 0 gives x = {_m(val)}."
        ds = [(-a, "That makes the numerator 0, so f(x) = 0 there; the function is defined."),
              (b, "Solve x + b = 0, so x = −b."),
              (a, "The numerator's constant doesn't make f undefined."),
              (0, "f(0) is a perfectly good value here.")]
    else:
        prompt = (f"The function f is defined by f(x) = (x {_pm(a)})/(x {_pm(b)}). For what "
                  f"value of x is f(x) = 0?")
        val = -a
        expl = f"A fraction is 0 when its numerator is 0 (and the denominator isn't): x {_pm(a)} = 0 gives x = {_m(val)}."
        ds = [(-b, "That makes the denominator 0, so f is undefined there."),
              (a, "Solve x + a = 0, so x = −a."),
              (b, "The denominator's constant isn't the zero of f."),
              (0, "f(0) equals a/b, which isn't 0.")]
    return _numeric_mc(rng, prompt, val, ds, subskill="interpret", explanation=expl,
                       tags=["functions", "rational"], est=75, verify=f"x={val}")


def fn_gridin(rng, d):
    """Grid-in: evaluate or invert a function."""
    if d == "easy":
        a, b, k = rng.randint(2, 12), rng.randint(-15, 15), rng.randint(-8, 10)
        val = a * k + b
        if val < 0:
            b, val = b + 2 * abs(val), abs(val)
            val = a * k + b
        prompt = f"The function f is defined by f(x) = {_fx(a, b)}. What is the value of f({_m(k)})?"
        expl = f"f({_m(k)}) = {a}·({_m(k)}) {_pm(b)} = {_m(val)}."
    elif d == "medium":
        a, x, b = rng.randint(2, 9), rng.randint(1, 15), rng.randint(-12, 12)
        n = a * x + b
        val = x
        prompt = f"If f(x) = {_fx(a, b)} and f(x) = {_m(n)}, what is the value of x?"
        expl = f"{a}x = {_m(n - b)}, so x = {x}."
    else:
        a, b, c = rng.randint(1, 4), rng.randint(-6, 6), rng.randint(-9, 9)
        k = rng.randint(-5, 5)
        val = a * k * k + b * k + c
        if val < 0:
            c += -val + rng.randint(0, 5)
            val = a * k * k + b * k + c
        prompt = f"If f(x) = {_fx(a, b, c)}, what is the value of f({_m(k)})?"
        expl = f"f({_m(k)}) = {_m(a)}·({_m(k)})² {_pm(b)}·({_m(k)}) {_pm(c)} = {_m(val)}."
    return _spr_num(prompt, val, subskill="evaluate", explanation=expl,
                    tags=["functions", "grid-in"], est=75, verify=f"val={val}")


fn_gridin.sat_only = True


# --------------------------------------------------------------------------- #
# quadratics
# --------------------------------------------------------------------------- #
def _quad_str(b, c, a=1):
    """Format a·x² + b·x + c = 0, omitting unit coefficients and zero terms."""
    return _fx(a, b, c) + " = 0"


def q_roots(rng, d):
    """Solve a quadratic: pre-factored (easy), factor it (medium), non-monic (hard)."""
    if d == "easy":
        r1 = rng.randint(-9, 9)
        r2 = rng.choice([v for v in range(-9, 10) if v != r1])
        which = rng.choice(["greater", "lesser"])
        val = max(r1, r2) if which == "greater" else min(r1, r2)
        prompt = (f"What is the {which} of the two solutions to the equation "
                  f"(x {_pm(-r1)})(x {_pm(-r2)}) = 0?")
        expl = (f"A product is 0 when a factor is 0: x = {_m(r1)} or x = {_m(r2)}. "
                f"The {which} is {_m(val)}.")
        ds = [(min(r1, r2) if which == "greater" else max(r1, r2), f"That is the {'lesser' if which == 'greater' else 'greater'} solution."),
              (-val, "Each factor x − r is 0 when x = r, not −r."),
              (r1 + r2, "That is the sum of the solutions."),
              (r1 * r2, "That is the product of the solutions.")]
    elif d == "medium":
        r1 = rng.randint(-9, -1)
        r2 = rng.randint(1, 9)
        b, c = -(r1 + r2), r1 * r2
        mode = rng.choice(["greater", "lesser", "sum", "product"])
        val = {"greater": r2, "lesser": r1, "sum": r1 + r2, "product": c}[mode]
        ask = {"greater": "the greater of the two solutions", "lesser": "the lesser of the two solutions",
               "sum": "the sum of the solutions", "product": "the product of the solutions"}[mode]
        prompt = f"What is {ask} to {_quad_str(b, c)}?"
        expl = (f"The expression factors as (x − ({_m(r1)}))(x − ({_m(r2)})) = 0, so x = {_m(r1)} "
                f"or x = {_m(r2)}; {ask} is {_m(val)}.")
        ds = [(r1 if mode != "lesser" else r2, "That is the other root."),
              (-val, "Check the signs when reading roots from the factors."),
              (c if mode != "product" else r1 + r2, "That is the product/sum of the roots, not what was asked."),
              (b, "That is the coefficient b, which equals −(sum of roots).")]
    else:
        a = rng.choice([2, 3, 4, 5, 6])
        p = rng.choice([v for v in range(-7, 8) if v != 0 and math.gcd(abs(v), a) == 1])
        r2 = rng.choice([v for v in range(-6, 7) if v != 0])
        # (a x - p)(x - r2) = a x^2 - (a r2 + p) x + p r2
        b, c = -(a * r2 + p), p * r2
        root1 = Fraction(p, a)
        which = rng.choice(["greater", "lesser", "sum"])
        val = {"greater": max(root1, r2), "lesser": min(root1, r2), "sum": root1 + r2}[which]
        ask = f"the {which} of the two solutions" if which != "sum" else "the sum of the solutions"
        prompt = f"What is {ask} to the equation {_quad_str(b, c, a)}?"
        expl = (f"Factor: ({_lin(a, -p)})(x {_pm(-r2)}) = 0, so x = {num_str(root1)} or "
                f"x = {_m(r2)}. Then {ask} is {num_str(val)}.")
        ds = [(Fraction(a, p), "The root of ax − p = 0 is p/a, not a/p."),
              (Fraction(-b, a) if which != "sum" else -Fraction(b, a) + 1, "Sum of roots is −b/a; make sure you answer what was asked."),
              (-val, "Sign slip reading the roots."),
              (r2 if which == "greater" and root1 > r2 else root1, "That is the other solution.")]
    return _numeric_mc(rng, prompt, val, ds, subskill="roots", explanation=expl,
                       tags=["quadratics", "factoring"], est=85, verify=f"val={num_str(val)}")


def q_vertex(rng, d):
    """Vertex / extreme value of a parabola."""
    if d == "easy":
        h, k = rng.randint(-9, 9), rng.randint(-15, 15)
        s = rng.choice([1, -1])
        rule = f"{'' if s > 0 else '−'}(x {_pm(-h)})² {_pm(k)}"
        which = "minimum" if s > 0 else "maximum"
        if rng.random() < 0.5:
            prompt = f"The function f is defined by f(x) = {rule}. What is the {which} value of f?"
            val = k
            expl = f"In vertex form the vertex is ({_m(h)}, {_m(k)}); the {which} value is {_m(k)}."
            ds = [(h, "That is the x-coordinate of the vertex, not the extreme value."),
                  (-k, "The vertical shift k keeps its sign in the output."),
                  (-h, "That is the opposite of the vertex's x-coordinate."),
                  (h + k, "Don't add the two coordinates.")]
        else:
            prompt = f"The function f is defined by f(x) = {rule}. At what value of x does f reach its {which}?"
            val = h
            expl = f"The vertex of (x − h)² + k is at x = h; here h = {_m(h)}."
            ds = [(-h, "x − h = 0 when x = h, so the sign flips from what's written."),
                  (k, "That is the extreme value, not where it occurs."),
                  (-k, "That is the opposite of the extreme value."),
                  (h * h, "Don't square the shift.")]
    else:
        a = 1 if d == "medium" else rng.choice([-2, -1, 2, 3])
        h = rng.randint(-8, 8)
        k = rng.randint(-20, 20)
        # a(x-h)^2 + k = a x^2 - 2 a h x + a h^2 + k
        b, c = -2 * a * h, a * h * h + k
        rule = _fx(a, b, c)
        which = "minimum" if a > 0 else "maximum"
        if d == "medium" or rng.random() < 0.5:
            prompt = f"The graph of y = {rule} in the xy-plane is a parabola. What is the x-coordinate of its vertex?"
            val = h
            expl = f"The vertex is at x = −b/(2a) = {_m(-b)}/({_m(2 * a)}) = {_m(h)}."
            ds = [(-h, "x = −b/(2a); watch the sign."),
                  (k, "That is the y-coordinate of the vertex."),
                  (Fraction(-b, a), "Divide by 2a, not a."),
                  (c, "That is the y-intercept, not the vertex.")]
        else:
            prompt = f"The function f is defined by f(x) = {rule}. What is the {which} value of f(x)?"
            val = k
            expl = (f"The vertex is at x = −b/(2a) = {_m(h)}; f({_m(h)}) = {_m(a)}({_m(h)})² "
                    f"{_pm(b)}({_m(h)}) {_pm(c)} = {_m(k)}.")
            ds = [(h, "That is the x-coordinate of the vertex, not the value of f there."),
                  (c, "That is f(0), not the extreme value."),
                  (-k, "Sign slip evaluating f at the vertex."),
                  (k + a, "Arithmetic slip; recompute f(h).")]
    return _numeric_mc(rng, prompt, val, ds, subskill="vertex", explanation=expl,
                       tags=["quadratics", "vertex"], est=80 if d == "easy" else 95,
                       verify=f"vertex ({h},{k})")


def q_discriminant(rng, d):
    """Number of real solutions (discriminant), or the k giving one solution."""
    if d == "hard" and rng.random() < 0.5:
        t = rng.randint(2, 9)
        a = 1
        # x^2 + kx + t^2 = 0 has one solution when k = ±2t
        prompt = (f"In the equation x² + kx + {t * t} = 0, k is a positive constant. If the "
                  f"equation has exactly one real solution, what is the value of k?")
        val = 2 * t
        expl = (f"One solution means b² − 4ac = 0: k² − 4·{t * t} = 0, so k² = {4 * t * t} "
                f"and k = {2 * t} (positive).")
        ds = [(t, "k² = 4·{0}, so k = 2·{1}, not {1}.".format(t * t, t)),
              (4 * t * t, "That is k², not k."),
              (t * t, "Set the discriminant to 0, not k equal to c."),
              (4 * t, "k² = 4c gives k = 2√c, not 4√c.")]
        return _numeric_mc(rng, prompt, val, ds, subskill="roots", explanation=expl,
                           tags=["quadratics", "discriminant"], est=95, verify=f"k={val}")
    cat = rng.choice([0, 1, 2])
    a = rng.randint(1, 3)
    if cat == 1:
        t = rng.randint(1, 6)
        b, c = 2 * a * t, a * t * t
    elif cat == 2:
        b, c = rng.randint(-8, 8), -rng.randint(1, 9)
    else:
        b, c = rng.randint(-4, 4), rng.randint(5, 9)
    eq = _quad_str(b, c, a)
    disc = b * b - 4 * a * c
    others = [n for n in (0, 1, 2) if n != cat]
    ds = [(others[0], "Recompute the discriminant b² − 4ac and use its sign."),
          (others[1], "The sign of b² − 4ac decides the number of real roots."),
          (3, "A quadratic can have at most two real solutions.")]
    sign = ("positive (two roots)" if disc > 0 else
            "zero (one root)" if disc == 0 else "negative (no real roots)")
    prompt = rng.choice([f"How many distinct real solutions does {eq} have?",
                         f"{eq}\nHow many distinct real solutions does the equation above have?"])
    return _numeric_mc(rng, prompt, cat, ds, subskill="roots",
                       explanation=(f"The discriminant is b² − 4ac = ({_m(b)})² − 4·{a}·({_m(c)}) "
                                    f"= {_m(disc)}, which is {sign}."),
                       tags=["quadratics", "discriminant"], est=90, verify=f"D={disc}")


def q_equivalent_form(rng, d):
    """Factored form / equation with given roots (text options)."""
    r1 = rng.randint(-15, -1)
    r2 = rng.choice([v for v in range(1, 16) if v != -r1])
    b, c = -(r1 + r2), r1 * r2
    if d == "medium":
        prompt = f"Which of the following is equivalent to {_fx(1, b, c)}?"
        correct = f"(x {_pm(-r1)})(x {_pm(-r2)})"
        ds = [(f"(x {_pm(r1)})(x {_pm(r2)})", "Expanding this gives the opposite sign on the x-term."),
              (f"(x {_pm(-r1)})(x {_pm(r2)})", "Check the Outer + Inner terms; they don't match the x-coefficient."),
              (f"(x {_pm(r1)})(x {_pm(-r2)})", "Check the Outer + Inner terms; they don't match the x-coefficient."),
              (f"(x {_pm(-r1 + 1)})(x {_pm(-r2)})" if -r1 + 1 != 0 else f"(x {_pm(-r1)})(x {_pm(-r2 + 1)})",
               "The constant terms must multiply to the constant {0}.".format(_m(c)))]
        expl = (f"Find two numbers with product {_m(c)} and sum {_m(b)}: {_m(-r1)} and {_m(-r2)}. "
                f"So the expression is {correct}.")
    else:
        prompt = f"Which equation has solutions x = {_m(r1)} and x = {_m(r2)}?"
        correct = _quad_str(b, c)
        ds = [(_quad_str(-b, c), "The x-coefficient is −(sum of roots); the sign is wrong."),
              (_quad_str(b, -c), "The constant is the product of the roots, including its sign."),
              (_quad_str(-b, -c), "Both the x-coefficient and the constant have the wrong sign."),
              (_quad_str(r1 + r2, c) if r1 + r2 != b else _quad_str(b, c + 1),
               "x² − (sum)x + (product): the sum enters with a minus sign.")]
        expl = (f"(x − ({_m(r1)}))(x − ({_m(r2)})) = {_fx(1, b, c)}, since the sum of the roots "
                f"is {_m(r1 + r2)} and their product is {_m(c)}.")
    return _text_mc(rng, prompt, correct, ds, subskill="factoring", explanation=expl,
                    tags=["quadratics", "factoring"], est=85, verify=f"roots {r1},{r2}")


def q_square_root(rng, d):
    """Solve x² = k or (x − a)² = k."""
    if d == "easy":
        n = rng.randint(2, 60)
        k = n * n
        prompt = rng.choice([f"If x² = {k} and x > 0, what is the value of x?",
                             f"What is the positive solution to x² − {k} = 0?",
                             f"If x² = {k}, what is the greater of the two solutions?"])
        val = n
        expl = f"x = √{k} = {n} (taking the positive root)."
        ds = [(k // 2, "Halving is not the inverse of squaring."),
              (n * 2, "Recheck: ({0})² = {1}, not {2}.".format(2 * n, 4 * k, k)),
              (-n, "The question asks for the positive solution."),
              (n + 1, "Recheck the square root.")]
    else:
        a = rng.choice([v for v in range(-20, 21) if v != 0])
        n = rng.randint(2, 15)
        k = n * n
        sols = (a + n, a - n)
        if d == "medium":
            prompt = f"If (x {_pm(-a)})² = {k}, what is the greatest possible value of x?"
            val = max(sols)
            expl = (f"Take square roots: x {_pm(-a)} = ±{n}, so x = {_m(a + n)} or x = {_m(a - n)}. "
                    f"The greatest is {_m(val)}.")
            ds = [(min(sols), "That is the lesser solution."),
                  (k + a, "Take the square root before solving for x."),
                  (a, "That is the center of the two solutions."),
                  (-val, "Sign slip after taking the square root.")]
        else:
            prompt = f"If (x {_pm(-a)})² = {k}, what is the sum of all possible values of x?"
            val = 2 * a
            expl = (f"x {_pm(-a)} = ±{n}, so x = {_m(a + n)} or x = {_m(a - n)}; the sum is "
                    f"{_m(2 * a)}.")
            ds = [(max(sols), "That is one solution, not the sum."),
                  (2 * n, "The solutions are symmetric about {0}, so their sum is 2·{0}.".format(_m(a))),
                  (a, "That is the average of the solutions, not their sum."),
                  (-2 * a, "Sign slip; the solutions are centered at {0}.".format(_m(a)))]
    return _numeric_mc(rng, prompt, val, ds, subskill="roots", explanation=expl,
                       tags=["quadratics", "square-root"], est=75 if d == "easy" else 85,
                       verify=f"val={val}")


def q_projectile(rng, d):
    """Quadratic models: height of a launched object (hard)."""
    v = rng.choice([16, 32, 48, 64, 80, 96, 112])
    h0 = rng.choice([0, 16, 32, 48, 80, 96, 128, 144])
    rule = f"h(t) = −16t² + {v}t" + (f" + {h0}" if h0 else "")
    # roots of -16 t^2 + v t + h0 = 0  -> 16 t^2 - v t - h0 = 0
    disc = v * v + 64 * h0
    rt = math.isqrt(disc)
    if rt * rt != disc:
        return q_projectile(rng, d)
    t_ground = Fraction(v + rt, 32)
    t_peak = Fraction(v, 32)
    h_peak = -16 * t_peak * t_peak + v * t_peak + h0
    if rng.random() < 0.5:
        prompt = (f"A ball is thrown upward, and its height above the ground, in feet, t seconds "
                  f"after it is thrown is given by {rule}. After how many seconds does the ball "
                  f"hit the ground?")
        val = t_ground
        expl = (f"Set h(t) = 0: 16t² − {v}t{' − ' + str(h0) if h0 else ''} = 0 → t = "
                f"({v} ± √{disc})/32 = {num_str(val)} (the positive root).")
        ds = [(t_peak, "That is when the ball reaches its maximum height."),
              (Fraction(v, 16), "That is the time to return to the launch height, not the ground.") if h0 else (2 * t_peak + 1, "Recheck the quadratic formula."),
              (h_peak, "That is the maximum height, not a time."),
              (val + 1, "Arithmetic slip in the quadratic formula.")]
    else:
        prompt = (f"A ball is thrown upward, and its height above the ground, in feet, t seconds "
                  f"after it is thrown is given by {rule}. What is the maximum height, in feet, "
                  f"the ball reaches?")
        val = h_peak
        expl = (f"The vertex is at t = −b/(2a) = {v}/32 = {num_str(t_peak)}; h({num_str(t_peak)}) = "
                f"{num_str(val)} feet.")
        ds = [(t_peak, "That is the time of the peak, not the height."),
              (h0 + v, "Substitute the vertex time, not t = 1."),
              (val - h0 if h0 else val + 16, "Include the initial height in the maximum."),
              (t_ground, "That is when the ball lands.")]
    return _numeric_mc(rng, prompt, val, ds, subskill="vertex", explanation=expl,
                       qtype="multi_step_math", tags=["quadratics", "model"], est=110,
                       verify=f"peak t={num_str(t_peak)} h={num_str(h_peak)} ground t={num_str(t_ground)}")


q_projectile.small_space = True


def q_gridin(rng, d):
    """Grid-in: a (positive) solution of a quadratic."""
    r1 = rng.randint(1, 12)
    if d == "easy":
        n = rng.randint(2, 60)
        prompt = rng.choice([f"If x² − {n * n} = 0 and x > 0, what is the value of x?",
                             f"What is the positive solution to the equation x² = {n * n}?",
                             f"If (x − {n})(x + {n}) = 0 and x > 0, what is the value of x?"])
        val = n
        expl = f"x² = {n * n}, so x = {n}."
    elif d == "medium":
        r2 = rng.randint(-15, -1)
        r1 = rng.randint(1, 15)
        b, c = -(r1 + r2), r1 * r2
        prompt = f"What is the positive solution to the equation {_quad_str(b, c)}?"
        val = r1
        expl = f"Factor: (x − {r1})(x {_pm(-r2)}) = 0, so the positive solution is {r1}."
    else:
        a = rng.choice([2, 3, 4, 5])
        p = rng.choice([v for v in range(1, 8) if math.gcd(v, a) == 1])
        r2 = -rng.randint(1, 7)
        b, c = -(a * r2 + p), p * r2
        prompt = f"What is the positive solution to the equation {_quad_str(b, c, a)}?"
        val = Fraction(p, a)
        expl = f"Factor: ({_lin(a, -p)})(x {_pm(-r2)}) = 0, so the positive solution is x = {num_str(val)}."
    return _spr_num(prompt, val, subskill="roots", explanation=expl,
                    tags=["quadratics", "grid-in"], est=85, verify=f"x={num_str(val)}")


q_gridin.sat_only = True


# --------------------------------------------------------------------------- #
# exponents_radicals
# --------------------------------------------------------------------------- #
def ex_rules(rng, d):
    """Apply product / quotient / power rules (string answers like 3^7)."""
    base = rng.randint(2, 9)
    if d == "easy":
        m, n = rng.randint(2, 8), rng.randint(2, 6)
        while m + n == m * n:
            n = rng.randint(2, 5)
        exp = m + n
        prompt = rng.choice([f"Which of the following is equal to {base}^{m} · {base}^{n}?",
                             f"What is {base}^{m} · {base}^{n} written as a single power?"])
        ds = _pow_distractors(rng, base, exp, [
            (f"{base}^{m * n}", "When multiplying powers you add the exponents, not multiply them."),
            (f"{base * base}^{m + n}", "The base does not change when multiplying powers."),
            (f"{base}^{abs(m - n)}", "Subtracting exponents applies to division, not multiplication.")])
        expl = f"Same base, multiplying: add exponents. {base}^{m}·{base}^{n} = {base}^{exp}."
    elif d == "medium":
        if rng.random() < 0.5:
            m, n = rng.randint(6, 12), rng.randint(2, 5)
            exp = m - n
            prompt = f"Which of the following is equal to {base}^{m} ÷ {base}^{n}?"
            ds = _pow_distractors(rng, base, exp, [
                (f"{base}^{m + n}", "Dividing powers subtracts exponents; it doesn't add them."),
                (f"{base}^{m * n}", "Don't multiply the exponents when dividing."),
                (f"1^{m - n}", "The base stays the same; only the exponents subtract.")])
            expl = f"Same base, dividing: subtract exponents. {base}^{m} ÷ {base}^{n} = {base}^{exp}."
        else:
            m, n = rng.randint(2, 6), rng.randint(2, 4)
            while m + n == m * n:
                m = rng.randint(3, 6)
            exp = m * n
            prompt = f"Which of the following is equal to ({base}^{m})^{n}?"
            ds = _pow_distractors(rng, base, exp, [
                (f"{base}^{m + n}", "A power of a power multiplies the exponents, not adds them."),
                (f"{base * n}^{m}", "The base is unchanged by an outer exponent."),
                (f"{base}^{m ** n}", "Multiply the exponents; don't raise one to the other.")])
            expl = f"A power raised to a power multiplies exponents: ({base}^{m})^{n} = {base}^{exp}."
    else:
        m, n = rng.randint(2, 5), rng.randint(2, 4)
        while m + n == m * n:
            m = rng.randint(3, 5)
        p = m * n + rng.randint(1, 6)
        exp = m * n - p
        prompt = f"Which of the following is equal to ({base}^{m})^{n} ÷ {base}^{p}?"
        ds = _pow_distractors(rng, base, exp, [
            (f"{base}^{m * n + p}", "Dividing subtracts the exponent; it doesn't add it."),
            (f"{base}^{m + n - p}", "A power of a power multiplies (m·n), it doesn't add."),
            (f"{base}^{abs(exp)}", "Watch the sign: m·n − p is negative here.")])
        expl = (f"({base}^{m})^{n} = {base}^{m * n}, then ÷ {base}^{p} subtracts: {base}^{exp}. "
                f"A negative exponent means a reciprocal: {base}^{exp} = 1/{base}^{abs(exp)}.")
    return _numeric_mc(rng, prompt, f"{base}^{exp}", ds, subskill="exponent_rules",
                       explanation=expl, tags=["exponents"], fmt=str, est=80,
                       verify=f"{base}^{exp}")


def ex_evaluate(rng, d):
    """Numeric evaluation: powers, negative exponents, fractional exponents."""
    if d == "easy":
        base = rng.randint(2, 15)
        e = rng.randint(2, 7 if base == 2 else 5 if base <= 4 else 3)
        val = base ** e
        prompt = rng.choice([f"What is the value of {base}^{e}?",
                             f"Which of the following is equal to {base}^{e}?",
                             f"If x = {base}^{e}, what is the value of x?",
                             f"{base}^{e} = ?"])
        expl = f"{base}^{e} = " + "·".join([str(base)] * e) + f" = {val}."
        ds = [(base * e, "This multiplies the base by the exponent instead of repeated multiplication."),
              (base ** (e - 1), "One factor short; count the multiplications."),
              (e ** base, "The base is {0}, raised to the {1}.".format(base, e)),
              (base ** e + base, "Arithmetic slip in the last multiplication.")]
    elif d == "medium":
        base, e = rng.choice([(2, 1), (2, 2), (2, 3), (2, 4), (2, 5), (2, 6), (3, 1), (3, 2), (3, 3), (3, 4), (4, 1), (4, 2), (4, 3), (5, 1), (5, 2), (5, 3), (10, 1), (10, 2), (10, 3), (6, 1), (6, 2), (7, 1), (7, 2), (8, 1), (8, 2), (9, 1), (9, 2), (11, 1), (12, 1), (11, 2), (12, 2), (20, 1), (25, 1), (15, 1), (15, 2), (13, 1), (14, 1), (16, 1)])
        val = Fraction(1, base ** e)
        prompt = rng.choice([f"What is the value of {base}^(−{e})?",
                             f"Which of the following is equal to {base}^(−{e})?"])
        expl = f"A negative exponent means a reciprocal: {base}^(−{e}) = 1/{base}^{e} = {num_str(val)}."
        ds = [(-(base ** e), "A negative exponent does not make the value negative."),
              (Fraction(-1, base ** e), "The reciprocal is positive."),
              (base ** e, "The negative exponent means 1 over this."),
              (Fraction(1, base * e), "Compute the power first, then take the reciprocal.")]
    else:
        base, p, q = rng.choice([(8, 2, 3), (27, 2, 3), (16, 3, 4), (16, 3, 2), (25, 3, 2),
                                 (4, 3, 2), (9, 3, 2), (32, 2, 5), (64, 2, 3), (81, 3, 4),
                                 (8, 4, 3), (27, 4, 3), (16, 5, 4), (125, 2, 3), (64, 5, 6), (36, 3, 2),
                                 (100, 3, 2), (1000, 2, 3), (49, 3, 2), (64, 4, 3), (32, 3, 5),
                                 (81, 5, 4), (16, 1, 4), (27, 1, 3), (8, 1, 3), (81, 1, 4), (32, 1, 5),
                                 (64, 1, 6), (128, 2, 7), (125, 4, 3), (243, 2, 5), (1000, 1, 3),
                                 (64, 1, 3), (81, 1, 2), (121, 1, 2), (144, 3, 2), (8, 5, 3), (4, 5, 2)])
        root = round(base ** (1 / q))
        val = root ** p
        prompt = rng.choice([f"What is the value of {base}^({p}/{q})?",
                             f"Which of the following is equal to {base}^({p}/{q})?",
                             f"If x = {base}^({p}/{q}), what is the value of x?"])
        expl = (f"{base}^({p}/{q}) = ({base}^(1/{q}))^{p} = ({root})^{p} = {val}, since the "
                f"{_ordinal(q)} root of {base} is {root}.")
        ds = [(round(base * p / q), "Don't multiply the base by the fraction; the exponent means root then power."),
              (root ** q if root ** q != val else root ** p * 2, "Raise the root to the power p, not q."),
              (root, "That is the {0} root; now raise it to the power {1}.".format(_ordinal(q), p)),
              (base ** p // root if base ** p % root == 0 else val + base, "Take the root first, then the power.")]
    return _numeric_mc(rng, prompt, val, ds, subskill="exponent_rules", explanation=expl,
                       tags=["exponents", "evaluate"], est=70 if d == "easy" else 85,
                       verify=f"val={num_str(val)}")


def ex_radicals(rng, d):
    """Simplify or combine radicals (string answers like 4√3)."""
    if d == "easy":
        r = rng.choice([2, 3, 5, 6, 7, 10, 11, 13])
        a, b = rng.randint(2, 12), rng.randint(2, 12)
        op = rng.choice(["+", "−"])
        if op == "−" and a <= b:
            a, b = b + rng.randint(1, 4), b
        val = a + b if op == "+" else a - b
        prompt = f"Which of the following is equal to {a}√{r} {op} {b}√{r}?"
        correct = f"{val}√{r}"
        ds = [(f"{val}√{2 * r}", "The radicand doesn't change when adding like radicals."),
              (f"{a * b if op == '+' else abs(a - b) + 1}√{r}", "Add (or subtract) the coefficients; don't multiply."),
              (f"{val}", "The √{0} stays; only the coefficients combine.".format(r)),
              (f"{a + b if op == '−' else a - b}√{r}", "Check the sign of the operation.")]
        expl = f"Like radicals combine their coefficients: ({a} {op} {b})√{r} = {correct}."
    elif d == "medium":
        k = rng.randint(2, 12)
        r = rng.choice([2, 3, 5, 6, 7, 10, 11, 13, 14, 15, 17, 19, 21, 22, 23])
        n = k * k * r
        prompt = f"Which of the following is equivalent to √{n}?"
        correct = f"{k}√{r}"
        ds = [(f"{r}√{k}", "The perfect-square factor comes out of the radical; the rest stays."),
              (f"{k * k}√{r}", "Taking the square root of {0} gives {1}, not {0}.".format(k * k, k)),
              (f"{k}√{r * k}" if r * k != n else f"{k}√{r + 1}", "Factor out the largest perfect square."),
              (f"{k * r}", "√{0} is not an integer; only the square factor simplifies.".format(n))]
        expl = f"√{n} = √({k * k}·{r}) = √{k * k}·√{r} = {k}√{r}."
    else:
        c, a = rng.choice([v for v in range(1, 10)]), rng.randint(2, 9)
        b = rng.randint(1, 9)
        # sqrt(x + a) = b  -> x = b^2 - a ; with coefficient: c*sqrt(x+a) = c*b
        prompt = f"If √(x + {a}) {_pm(c)} = {b + c}, what is the value of x?"
        val = b * b - a
        expl = f"Isolate the radical: √(x + {a}) = {b}. Square: x + {a} = {b * b}, so x = {_m(val)}."
        ds = [((b + c) ** 2 - a, "Subtract {0} before squaring, not after.".format(c)),
              (b - a, "Square both sides to undo the square root."),
              (b * b + a, "Subtract {0} after squaring.".format(a)),
              (-val if val else val + 1, "Sign slip when subtracting {0}.".format(a))]
        return _numeric_mc(rng, prompt, val, ds, subskill="radical_simplify", explanation=expl,
                           tags=["radicals", "equation"], est=90, verify=f"x={val}")
    return _text_mc(rng, prompt, correct, ds, subskill="radical_simplify", explanation=expl,
                    tags=["radicals"], est=80, verify=f"{correct}")


def ex_solve_exponential(rng, d):
    """Solve b^x = c type equations for x."""
    base = rng.choice([2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12])
    if d == "easy":
        e = rng.randint(2, 7 if base <= 3 else 4 if base <= 6 else 3)
        prompt = rng.choice([f"If {base}^x = {base ** e}, what is the value of x?",
                             f"For what value of x is {base}^x equal to {base ** e}?",
                             f"{base}^x = {base ** e}\nWhat is the value of x in the equation above?"])
        val = e
        expl = f"{base ** e} = {base}^{e}, so x = {e}."
        ds = [(base ** e // base, "That is {0}^{1} divided by {0}, not an exponent.".format(base, e)),
              (e + 1, "Count the factors of {0} carefully.".format(base)),
              (e - 1, "Count the factors of {0} carefully.".format(base)),
              (base * e, "The exponent is the number of times {0} is a factor.".format(base))]
    elif d == "medium":
        e = rng.randint(2, 6 if base <= 3 else 3)
        k = rng.choice([v for v in range(-9, 10) if v != 0])
        prompt = rng.choice([f"If {base}^(x {_pm(k)}) = {base ** e}, what is the value of x?",
                             f"What value of x satisfies {base}^(x {_pm(k)}) = {base ** e}?"])
        val = e - k
        expl = f"{base ** e} = {base}^{e}, so x {_pm(k)} = {e} and x = {_m(val)}."
        ds = [(e, "That is the exponent on the right; still solve x + k = e."),
              (e + k, "Subtract {0} from both sides; don't add it.".format(_m(k))),
              (base ** e - k, "Match exponents first instead of subtracting from {0}.".format(base ** e)),
              (-val if val else val + 1, "Sign slip solving the linear equation.")]
    else:
        # base^(a x) = (base^p)^? -> use different-looking bases: 4^x = 8 -> 2^(2x) = 2^3 -> x = 3/2
        b1, b2, e1, e2 = rng.choice([(4, 8, 2, 3), (8, 4, 3, 2), (9, 27, 2, 3), (27, 9, 3, 2),
                                     (4, 32, 2, 5), (16, 8, 4, 3), (8, 16, 3, 4), (25, 125, 2, 3),
                                     (4, 2, 2, 1), (9, 3, 2, 1), (8, 2, 3, 1), (16, 2, 4, 1), (32, 4, 5, 2)])
        k = rng.randint(1, 3)
        n = rng.randint(1, 3)
        # b1^(k x) = b2^n  -> base^(e1 k x) = base^(e2 n) -> x = e2 n / (e1 k)
        val = Fraction(e2 * n, e1 * k)
        lhs = f"{b1}^x" if k == 1 else f"{b1}^({k}x)"
        rhs = f"{b2}" if n == 1 else f"{b2}^{n}"
        prompt = f"If {lhs} = {rhs}, what is the value of x?"
        common = {4: 2, 8: 2, 16: 2, 32: 2, 2: 2, 9: 3, 27: 3, 3: 3, 25: 5, 125: 5}[b1]
        expl = (f"Write both sides with base {common}: {b1} = {common}^{e1} and {b2} = {common}^{e2}, "
                f"so {common}^({e1 * k}x) = {common}^{e2 * n}. Then {e1 * k}x = {e2 * n} and x = {num_str(val)}.")
        ds = [(Fraction(e1 * k, e2 * n), "This inverts the final ratio of exponents."),
              (Fraction(e2 * n, k) if e1 != 1 else val + 1, "Account for {0} = {1}^{2} as well.".format(b1, common, e1)),
              (Fraction(n, k), "Rewrite both numbers as powers of the same base first."),
              (e2 * n, "Divide by the exponent on the left side.")]
    return _numeric_mc(rng, prompt, val, ds, subskill="exponent_rules", explanation=expl,
                       tags=["exponents", "equation"], est=75 if d == "easy" else 90,
                       verify=f"x={num_str(val)}")


def ex_algebraic(rng, d):
    """Exponent rules with variables (text options like 12x^7)."""
    a, b = rng.randint(2, 9), rng.randint(3, 9)
    m, n = rng.randint(2, 7), rng.randint(3, 7)
    if d == "medium":
        prompt = f"Which of the following is equivalent to ({a}x^{m})({b}x^{n})?"
        correct = f"{a * b}x^{m + n}"
        ds = [(f"{a * b}x^{m * n}", "Add the exponents when multiplying; don't multiply them."),
              (f"{a + b}x^{m + n}", "Multiply the coefficients; don't add them."),
              (f"{a + b}x^{m * n}", "Multiply coefficients and add exponents."),
              (f"{a * b}x^{abs(m - n) if m != n else m + n + 1}", "Subtracting exponents is for division.")]
        expl = f"Multiply coefficients ({a}·{b} = {a * b}) and add exponents ({m} + {n} = {m + n}): {correct}."
    else:
        kind = rng.choice(["power", "quotient"])
        if kind == "power":
            a = rng.randint(3, 5)
            n = rng.randint(2, 3)
            m = rng.randint(3, 7)
            prompt = f"Which of the following is equivalent to ({a}x^{m})^{n}?"
            correct = f"{a ** n}x^{m * n}"
            ds = [(f"{a}x^{m * n}", "The coefficient is raised to the power too."),
                  (f"{a * n}x^{m * n}", "Raise {0} to the {1} power; don't multiply.".format(a, n)),
                  (f"{a ** n}x^{m + n}", "Multiply the exponents for a power of a power."),
                  (f"{a ** n}x^{m ** n}" if m ** n != m * n else f"{a ** n}x^{m * n + 1}", "Multiply the exponents; don't raise one to the other.")]
            expl = f"Raise each factor to the power: {a}^{n} = {a ** n} and (x^{m})^{n} = x^{m * n}: {correct}."
        else:
            a = a * b
            m = n + rng.randint(1, 5)
            prompt = f"Which of the following is equivalent to {a}x^{m} / ({b}x^{n})?"
            correct = f"{a // b}x^{m - n}"
            ds = [(f"{a // b}x^{m + n}", "Subtract the exponents when dividing."),
                  (f"{a - b}x^{m - n}", "Divide the coefficients; don't subtract them."),
                  (f"{a // b}x^{Fraction(m, n)}" if m % n else f"{a // b}x^{m // n}", "Subtract the exponents; don't divide them."),
                  (f"{a}x^{m - n}", "Divide the coefficient by {0} as well.".format(b))]
            expl = f"Divide coefficients ({a} ÷ {b} = {a // b}) and subtract exponents ({m} − {n} = {m - n}): {correct}."
    return _text_mc(rng, prompt, correct, ds, subskill="exponent_rules", explanation=expl,
                    tags=["exponents", "algebraic"], est=80, verify=correct)


def ex_rewrite_radical(rng, d):
    """Convert between radical and rational-exponent forms (text options)."""
    p, q = rng.choice([(1, 2), (1, 3), (2, 3), (3, 2), (3, 4), (1, 4), (5, 2), (2, 5), (4, 3), (5, 3)])
    root = {2: "√", 3: "∛", 4: "∜", 5: "⁵√"}[q]
    if rng.random() < 0.5:
        prompt = f"Which of the following is equivalent to x^({p}/{q}) for x > 0?"
        correct = f"{root}(x^{p})" if p != 1 else f"{root}x"
        ds = [(f"{root if q != p else '√'}(x^{q})" if p != 1 else f"x^{q}", "The denominator is the root index, the numerator is the power."),
              (f"x^{p}/x^{q}" if p != 1 else f"x/{q}", "A fractional exponent is a root, not a quotient."),
              (f"{'√' if q != 2 else '∛'}(x^{p})", "Check the root index: the denominator {0} gives a {1} root.".format(q, _ordinal(q))),
              (f"{p}{root}x" if p != 1 else f"{q}√x", "The numerator is a power on x, not a coefficient.")]
        expl = f"x^(p/q) = {root.strip()}(x^p): the denominator {q} is the root and the numerator {p} is the power."
    else:
        prompt = f"Which of the following is equivalent to {root}(x^{p}) for x > 0?" if p != 1 else f"Which of the following is equivalent to {root}x for x > 0?"
        correct = f"x^({p}/{q})"
        ds = [(f"x^({q}/{p})", "The root index goes in the denominator of the exponent."),
              (f"x^{p * q}", "A root divides the exponent; it doesn't multiply it."),
              (f"x^({p}−{q})" if p != q else f"x^({p}+{q})", "Roots correspond to fractional exponents, not differences."),
              (f"x^({p}/{q + 1})", "Check the root index: {0} means divide the exponent by {1}.".format(root.strip(), q))]
        expl = f"{root}(x^{p}) = x^({p}/{q}): a {_ordinal(q)} root divides the exponent by {q}."
    return _text_mc(rng, prompt, correct, ds, subskill="radical_simplify", explanation=expl,
                    tags=["radicals", "exponents"], est=80, verify=correct)


ex_rewrite_radical.small_space = True


def ex_gridin(rng, d):
    """Grid-in: exponent/radical values."""
    if d == "easy":
        base = rng.choice([2, 3, 4, 5, 6, 7, 10])
        e = rng.randint(2, 6 if base <= 3 else 4)
        prompt = f"If {base}^x = {base ** e}, what is the value of x?"
        val = e
        expl = f"{base ** e} = {base}^{e}, so x = {e}."
    elif d == "medium":
        k, r = rng.choice([(2, 3), (3, 2), (2, 5), (4, 3), (5, 2), (3, 5), (2, 7), (6, 2), (2, 11), (3, 7)])
        prompt = f"If √{k * k * r} = k√{r}, where k is a positive constant, what is the value of k?"
        val = k
        expl = f"√{k * k * r} = √({k * k}·{r}) = {k}√{r}, so k = {k}."
    else:
        base, p, q = rng.choice([(8, 2, 3), (27, 2, 3), (16, 3, 4), (16, 3, 2), (25, 3, 2), (4, 3, 2), (9, 3, 2), (32, 2, 5), (64, 2, 3), (81, 3, 4), (125, 2, 3)])
        root = round(base ** (1 / q))
        prompt = f"What is the value of {base}^({p}/{q})?"
        val = root ** p
        expl = f"{base}^({p}/{q}) = ({root})^{p} = {val}."
    return _spr_num(prompt, val, subskill="exponent_rules", explanation=expl,
                    tags=["exponents", "grid-in"], est=75, verify=f"val={val}")


ex_gridin.sat_only = True
ex_gridin.small_space = True


# --------------------------------------------------------------------------- #
# polynomials
# --------------------------------------------------------------------------- #
def _binom_str(coef, const):
    """Format (x + k) or (m x − k) style binomials for factor choices."""
    return f"({_lin(coef, const)})"


def _poly_str(coeffs):
    """coeffs high->low, e.g. [3, -2, 5] -> '3x² − 2x + 5'."""
    deg = len(coeffs) - 1
    parts = []
    for i, c in enumerate(coeffs):
        p = deg - i
        if c == 0:
            continue
        mag = abs(c)
        var = "" if p == 0 else ("x" if p == 1 else f"x{'²' if p == 2 else '³' if p == 3 else '^' + str(p)}")
        coef = "" if (mag == 1 and p > 0) else str(mag)
        term = coef + var
        if not parts:
            parts.append(("−" if c < 0 else "") + term)
        else:
            parts.append(("− " if c < 0 else "+ ") + term)
    return " ".join(parts) if parts else "0"


def poly_expand(rng, d):
    """Expand (ax + b)(cx + d) and read a coefficient."""
    if d == "easy":
        a, c = rng.randint(1, 6), rng.randint(1, 6)
        b, e = rng.randint(1, 9), rng.randint(1, 9)
        target = rng.choice(["x", "x", "const"])
    else:
        a, c = rng.randint(1, 7), rng.randint(1, 7)
        b = rng.choice([-1, 1]) * rng.randint(2, 9)
        e = rng.choice([-1, 1]) * rng.randint(2, 9)
        target = rng.choice(["x", "x2", "const"])
    expr = _binom_str(a, b) + _binom_str(c, e)
    x2, x1, const = a * c, a * e + b * c, b * e
    if target == "x2":
        val = x2
        prompt = f"In the expansion of {expr}, what is the coefficient of x²?"
        expl = f"The x² term is {_m(a)}x·{_m(c)}x = {_m(x2)}x²."
        ds = [(x1, "This is the coefficient of x, not x²."),
              (const, "This is the constant term, not the x² coefficient."),
              (a + c, "Multiply the leading coefficients; don't add them."),
              (a * e, "That is one of the x-term products, not the x² product.")]
    elif target == "const":
        val = const
        prompt = f"In the expansion of {expr}, what is the constant term?"
        expl = f"The constant term is ({_m(b)})·({_m(e)}) = {_m(const)}."
        ds = [(x1, "This is the coefficient of x, not the constant."),
              (x2, "This is the coefficient of x², not the constant."),
              (b + e, "Multiply the constants; don't add them."),
              (-const, "Check the signs of the two constants.")]
    else:
        val = x1
        prompt = rng.choice([f"In the expansion of {expr}, what is the coefficient of x?",
                             f"If {expr} is written in the form px² + qx + r, what is the value of q?"])
        expl = (f"Using FOIL, the x-terms are {_m(a)}x·({_m(e)}) and ({_m(b)})·{_m(c)}x, giving "
                f"({_m(a * e)}) + ({_m(b * c)}) = {_m(x1)}.")
        ds = [(x2, "This is the coefficient of x², not x."),
              (const, "This is the constant term, not the x coefficient."),
              (a * e, "This includes only one of the two x-terms."),
              (a * e - b * c, "Add the Outer and Inner products; don't subtract.")]
    return _numeric_mc(rng, prompt, val, ds, subskill="operations", explanation=expl,
                       tags=["polynomials", "foil"], est=80, verify=f"x2={x2},x={x1},c={const}")


def poly_add_sub(rng, d):
    """Add or subtract polynomials (text options)."""
    p = [rng.randint(1, 9), rng.choice([v for v in range(-9, 10) if v]), rng.choice([v for v in range(-9, 10) if v])]
    q = [rng.randint(1, 9), rng.choice([v for v in range(-9, 10) if v]), rng.choice([v for v in range(-9, 10) if v])]
    if d == "easy":
        q = [rng.randint(1, 9), rng.randint(1, 9), rng.randint(1, 9)]
        p = [rng.randint(1, 9), rng.randint(1, 9), rng.randint(1, 9)]
        op = "+"
    else:
        op = "−"
        if d == "hard":
            k = rng.randint(2, 4)
            q = [k * v for v in q]
    if op == "+":
        res = [a + b for a, b in zip(p, q)]
        wrong_sign = [a - b for a, b in zip(p, q)]
        prompt = f"Which of the following is equivalent to ({_poly_str(p)}) + ({_poly_str(q)})?"
        expl = f"Add like terms: ({p[0]} + {q[0]})x² + ({p[1]} + {q[1]})x + ({p[2]} + {q[2]}) = {_poly_str(res)}."
        ds = [(_poly_str(wrong_sign), "This subtracts instead of adding."),
              (_poly_str([res[0], res[1], p[2] * q[2]]), "Constants add; they aren't multiplied."),
              (_poly_str([p[0] * q[0], res[1], res[2]]), "Like terms add; coefficients aren't multiplied."),
              (_poly_str([res[0], p[1] + q[2], p[2] + q[1]]), "Match like terms: x with x, constants with constants.")]
    else:
        res = [a - b for a, b in zip(p, q)]
        prompt = f"Which of the following is equivalent to ({_poly_str(p)}) − ({_poly_str(q)})?"
        expl = (f"Distribute the minus sign to every term of the second polynomial, then combine: "
                f"{_poly_str(res)}.")
        ds = [(_poly_str([p[0] - q[0], p[1] + q[1], p[2] + q[2]]), "The minus sign must be distributed to every term, not just the first."),
              (_poly_str([a + b for a, b in zip(p, q)]), "This adds instead of subtracting."),
              (_poly_str([b - a for a, b in zip(p, q)]), "This subtracts in the wrong order."),
              (_poly_str([p[0] - q[0], p[1] - q[1], p[2] + q[2]]), "The constant term is subtracted too.")]
    if len({t for t, _ in ds} | {_poly_str(res)}) < 4:
        return poly_add_sub(rng, d)
    return _text_mc(rng, prompt, _poly_str(res), ds, subskill="operations", explanation=expl,
                    tags=["polynomials", "add-subtract"], est=80, verify=f"result {res}")


def poly_factor(rng, d):
    """Factoring: GCF (easy), difference of squares (medium), trinomial factor (hard)."""
    if d == "easy":
        g = rng.randint(2, 6)
        a = rng.randint(2, 7)
        b = rng.choice([v for v in range(-9, 10) if v and math.gcd(abs(v), a) == 1])
        expr = _poly_str([g * a, g * b, 0])
        prompt = f"Which of the following is equivalent to {expr}?"
        correct = f"{g}x({_lin(a, b)})"
        ds = [(f"{g}({_lin(a, b)})", "x is also a common factor of both terms."),
              (f"x({_lin(g * a, g * b)})", "Factor out the common numerical factor {0} as well.".format(g)),
              (f"{g}x({_lin(a, -b)})", "Check the sign of the second term."),
              (f"{g * a}x({_lin(1, b)})", "{0}x doesn't divide the second term evenly.".format(g * a))]
        expl = f"Both terms share the factor {g}x: {expr} = {correct}."
    elif d == "medium":
        k = rng.randint(2, 20)
        a = rng.choice([1, 1, 2, 3, 4, 5, 6, 7])
        expr = _poly_str([a * a, 0, -k * k])
        prompt = f"Which of the following is a factor of {expr}?"
        correct = f"({_lin(a, k)})"
        ds = [(f"({_lin(a, k * k)})", "Take the square root of {0}, which is {1}.".format(k * k, k)),
              (f"({_lin(a * a, k)})", "Take the square root of the leading coefficient as well."),
              (f"({_lin(a, 2 * k)})", "a² − b² = (a + b)(a − b); b is √{0} = {1}.".format(k * k, k)),
              (f"({_lin(a, k)})²", "A difference of squares has two different factors, not a square."),
              (f"(x² {_pm(k)})", "The factors are linear: (ax + b)(ax − b).")]
        expl = f"{expr} is a difference of squares: ({_lin(a, k)})({_lin(a, -k)})."
    else:
        r1 = rng.randint(-15, -1)
        r2 = rng.randint(1, 15)
        b, c = -(r1 + r2), r1 * r2
        tri = _fx(1, b, c)
        correct = _binom_str(1, -r1)
        fakes = []
        for w in (-r1, -r2, r1 + 1, r2 + 1, r1 - 1, r2 - 1, r1 + 2, r2 + 2):
            if w not in (r1, r2) and w not in fakes:
                fakes.append(w)
            if len(fakes) == 4:
                break
        ds = [(_binom_str(1, -w), "Expanding this doesn't reproduce the trinomial; its root isn't a solution.")
              for w in fakes]
        prompt = f"Which of the following is a factor of {tri}?"
        expl = (f"{tri} factors as (x − ({_m(r1)}))(x − ({_m(r2)})); the roots are "
                f"{_m(r1)} and {_m(r2)}, so {correct} is a factor.")
    return _text_mc(rng, prompt, correct, ds, subskill="factoring", explanation=expl,
                    tags=["polynomials", "factoring"], est=85, verify=f"factor {correct}")


def poly_evaluate(rng, d):
    """Evaluate a polynomial (easy) or use the factor/remainder theorem (hard)."""
    if d == "easy":
        a, b, c = rng.randint(1, 5), rng.choice([v for v in range(-9, 10) if v]), rng.randint(-9, 9)
        k = rng.randint(-4, 5)
        val = a * k * k + b * k + c
        p = _poly_str([a, b, c])
        prompt = f"What is the value of {p} when x = {_m(k)}?"
        expl = f"Substitute: {a}({_m(k)})² {_pm(b)}({_m(k)}) {_pm(c)} = {_m(a * k * k)} {_pm(b * k)} {_pm(c)} = {_m(val)}."
        ds = [(a * k + b * k + c, "x² means square x before multiplying by {0}.".format(a)),
              (a * k * k - b * k + c, "Check the sign of the x-term."),
              (-a * k * k + b * k + c, "A squared negative is positive."),
              (val - c + 1, "Arithmetic slip; recompute carefully.")]
    elif d == "medium":
        a, b = rng.randint(1, 4), rng.choice([v for v in range(-9, 10) if v])
        k = rng.randint(1, 6)
        val = (a * k + b) ** 2
        prompt = f"If x = {k}, what is the value of ({_lin(a, b)})²?"
        inner = a * k + b
        expl = f"{a}·{k} {_pm(b)} = {_m(inner)}, and ({_m(inner)})² = {val}."
        ds = [(a * a * k * k + b * b, "(p + q)² = p² + 2pq + q²; the middle term is missing."),
              (2 * inner, "Square the value; don't double it."),
              (-val, "A square is never negative."),
              (inner, "Don't forget to square.")]
    else:
        r = rng.choice([v for v in range(-5, 6) if v != 0])
        a, b = rng.randint(1, 3), rng.choice([v for v in range(-8, 9) if v])
        c = rng.choice([v for v in range(-9, 10) if v])
        # p(x) = a x^3 + b x^2 + c x + k, with (x - r) a factor -> k = -(a r^3 + b r^2 + c r)
        k = -(a * r ** 3 + b * r * r + c * r)
        p = _poly_str([a, b, c, 0]).replace(" + 0", "") + " + k"
        p = _poly_str([a, b, c]).replace("x²", "x³", 1)
        p = _poly_str([a, b, c, 0])
        p = p.rsplit(" ", 2)[0] if p.endswith("0") else p
        p = _poly_str([a, b, c, 0])[:-4] if _poly_str([a, b, c, 0]).endswith(" + 0") else _poly_str([a, b, c, 0])
        prompt = (f"The polynomial p(x) = {_poly_str([a, b, c, 0]).replace(' + 0', '').replace(' − 0', '')} + k, where k "
                  f"is a constant, has (x {_pm(-r)}) as a factor. What is the value of k?")
        val = k
        expl = (f"If (x − r) is a factor then p(r) = 0. Substituting x = {_m(r)}: "
                f"{_m(a * r ** 3)} {_pm(b * r * r)} {_pm(c * r)} + k = 0, so k = {_m(val)}.")
        ds = [(-val, "p(r) = 0 means k is the opposite of the other terms' sum."),
              (a * r ** 3 + b * r * r - c * r, "Check the sign of the linear term when substituting."),
              (-(a * (-r) ** 3 + b * r * r + c * (-r)), "(x + r) is a factor when p(−r) = 0; here the root is {0}.".format(_m(r))),
              (-(a * r * r + b * r + c), "x³ means the cube of x, not the square.")]
    return _numeric_mc(rng, prompt, val, ds, subskill="operations", explanation=expl,
                       tags=["polynomials", "evaluate"], est=75 if d != "hard" else 100,
                       verify=f"val={val}")


def poly_product_coeff(rng, d):
    """Coefficient in a product of a trinomial and a binomial, or a squared binomial."""
    if d == "medium":
        a, b = rng.randint(1, 7), rng.choice([v for v in range(-12, 13) if v])
        prompt = f"Which of the following is equivalent to ({_lin(a, b)})²?"
        correct = _poly_str([a * a, 2 * a * b, b * b])
        ds = [(_poly_str([a * a, 0, b * b]), "(p + q)² has a middle term 2pq."),
              (_poly_str([a * a, a * b, b * b]), "The middle term is 2·p·q, not p·q."),
              (_poly_str([a * a, 2 * a * b, -b * b]) if b else _poly_str([a * a, 1, 1]), "The last term is q², which is positive."),
              (_poly_str([a * a, -2 * a * b, b * b]), "Check the sign of the middle term.")]
        expl = f"({_lin(a, b)})² = ({_lin(a, b)})({_lin(a, b)}) = {correct}."
        return _text_mc(rng, prompt, correct, ds, subskill="operations", explanation=expl,
                        tags=["polynomials", "square"], est=80, verify=correct)
    a, b, c = 1, rng.choice([v for v in range(-7, 8) if v]), rng.choice([v for v in range(-9, 10) if v])
    e = rng.choice([v for v in range(-6, 7) if v])
    # (x^2 + b x + c)(x + e) = x^3 + (b + e) x^2 + (c + b e) x + c e
    coeffs = [1, b + e, c + b * e, c * e]
    which = rng.choice(["x²", "x", "constant"])
    idx = {"x²": 1, "x": 2, "constant": 3}[which]
    val = coeffs[idx]
    prompt = (f"When ({_poly_str([a, b, c])})(x {_pm(e)}) is expanded and written in standard form, "
              f"what is the {'coefficient of ' + which if which != 'constant' else 'constant term'}?")
    expl = (f"Multiply each term: x³ + ({_m(b)} + {_m(e)})x² + ({_m(c)} + ({_m(b)})({_m(e)}))x + "
            f"({_m(c)})({_m(e)}) = {_poly_str(coeffs)}; the requested value is {_m(val)}.")
    others = [coeffs[i] for i in (1, 2, 3) if i != idx]
    ds = [(others[0], "That is a different coefficient of the product."),
          (others[1], "That is a different coefficient of the product."),
          (b * e if which == "x" else b + e + 1, "Two products contribute to this term; add both."),
          (-val, "Check the signs when multiplying.")]
    return _numeric_mc(rng, prompt, val, ds, subskill="operations", explanation=expl,
                       tags=["polynomials", "expand"], est=95, verify=f"{coeffs}")


# --------------------------------------------------------------------------- #
# ratios_percentages_units
# --------------------------------------------------------------------------- #
def rp_percent_of(rng, d):
    """What is P% of N (easy); 'a is what percent of b' (medium); successive % (hard)."""
    if d == "easy":
        whole = rng.randint(20, 90) * 5
        pct = rng.choice([5, 10, 15, 20, 25, 30, 40, 60, 75, 80])
        val = whole * pct // 100
        ctx = rng.choice([f"What is {pct}% of {whole}?",
                          f"A store has {whole} items in stock, and {pct}% of them are on sale. How many items are on sale?",
                          f"Of the {whole} students at a school, {pct}% ride the bus. How many students ride the bus?"])
        expl = f"{pct}% of {whole} = ({pct}/100)·{whole} = {val}."
        ds = [(whole * pct, "You forgot to divide by 100."),
              (whole - val, "This is the remaining part, not the part asked for."),
              (Fraction(whole, pct), "Multiply by the percent over 100; don't divide by the percent."),
              (val + whole // 20 if whole // 20 else val + 1, "Arithmetic slip; recompute (pct/100)·whole.")]
        prompt = ctx
    elif d == "medium":
        whole = rng.randint(8, 40) * 5
        pct = rng.choice([5, 10, 12, 15, 20, 25, 30, 35, 40, 45, 60, 65, 70, 75, 80, 85, 90])
        part = whole * pct // 100
        while part * 100 != whole * pct:
            whole += 5
            part = whole * pct // 100
        val = pct
        prompt = rng.choice([f"{part} is what percent of {whole}?",
                             f"A team won {part} of its {whole} games. What percent of its games did the team win?",
                             f"On a quiz, {rng.choice(NAMES)} answered {part} of {whole} questions correctly. What percent of the questions were answered correctly?"])
        expl = f"{part}/{whole} = {part / whole:.2f}, which is {pct}%."
        ds = [(round(100 * whole / part) if part else pct + 5, "Divide the part by the whole, not the whole by the part."),
              (whole - part, "That is the number of the rest, not a percent."),
              (100 - pct, "That is the percent of the remaining part."),
              (part, "A percent compares the part to the whole, times 100.")]
        return _numeric_mc(rng, prompt, val, ds, subskill="percent_change", explanation=expl,
                           tags=["percent"], fmt=lambda v: f"{num_str(v)}%", est=75, verify=f"{part}/{whole}={pct}%")
    else:
        P = rng.randint(4, 40) * 10
        d1 = rng.choice([10, 20, 25, 30, 40, 50])
        d2 = rng.choice([10, 20, 25, 50])
        after1 = P * (100 - d1) // 100
        val = Fraction(after1 * (100 - d2), 100)
        prompt = (f"A jacket priced at ${P} is marked down {d1}%, and a week later the sale "
                  f"price is reduced by an additional {d2}%. What is the final price, in dollars?")
        expl = (f"First markdown: {P}·(1 − {d1}/100) = {after1}. Second: {after1}·(1 − {d2}/100) = "
                f"{num_str(val)}.")
        ds = [(Fraction(P * (100 - d1 - d2), 100), "Successive discounts don't simply add; apply the second to the reduced price."),
              (after1, "That is the price after only the first markdown."),
              (Fraction(P * (100 - d2), 100), "Apply both discounts, in order."),
              (Fraction(P * (d1 + d2), 100), "That is the total of the two percents applied to the original, not a price.")]
        return _numeric_mc(rng, prompt, val, ds, subskill="percent_change", explanation=expl,
                           tags=["percent", "successive"], fmt=lambda v: _money(v), est=95,
                           qtype="multi_step_math", verify=f"final={num_str(val)}")
    return _numeric_mc(rng, prompt, val, ds, subskill="percent_change", explanation=expl,
                       tags=["percent"], est=65, verify=f"{pct}% of {whole}={val}")


def rp_percent_change(rng, d):
    """Compute a percent change (medium) or reverse one (hard); easy: apply a change."""
    pct = rng.choice([5, 10, 15, 20, 25, 30, 40, 50, 60, 75])
    up = rng.random() < 0.5
    word = "increase" if up else "decrease"
    if d == "easy":
        old = rng.randint(4, 60) * 20
        new = old + old * pct // 100 if up else old - old * pct // 100
        thing = rng.choice(["The price of a bike", "A town's population", "A monthly rent", "The number of club members"])
        prompt = f"{thing} was {old} and then {word}d by {pct}%. What is the new value?"
        val = new
        expl = f"{pct}% of {old} is {old * pct // 100}; {old} {'+' if up else '−'} {old * pct // 100} = {new}."
        ds = [(old * pct // 100, "That is the amount of change, not the new value."),
              (old - old * pct // 100 if up else old + old * pct // 100, f"The value {word}s; apply the change in the right direction."),
              (old + pct if up else old - pct, "Percent means per hundred of the original, not a raw amount."),
              (new + 10, "Arithmetic slip; recompute the percent of the original.")]
    elif d == "medium":
        old = rng.randint(2, 60) * 20 // 20 * 20
        new = old + old * pct // 100 if up else old - old * pct // 100
        prompt = rng.choice([f"A quantity changes from {old} to {new}. What is the percent {word}?",
                             f"Last year a shop sold {old} units; this year it sold {new}. By what percent did sales {word}?",
                             f"A laptop's price dropped from ${old} to ${new}." if not up else f"A laptop's price rose from ${old} to ${new}."])
        if prompt.startswith("A laptop"):
            prompt += f" What was the percent {word} in price?"
        val = pct
        expl = f"Percent {word} = |new − old|/old × 100 = {abs(new - old)}/{old} × 100 = {pct}%."
        ds = [(abs(new - old), "This is the raw change, not the percent change."),
              (round(abs(new - old) * 100 / new, 1), "Divide by the original value, not the new value."),
              (pct + 5, "Recheck the division."),
              (100 - pct, "That is the percent of the original that remains/isn't the change.")]
        return _numeric_mc(rng, prompt, val, ds, subskill="percent_change", explanation=expl,
                           tags=["percent", "change"], fmt=lambda v: f"{num_str(v)}%", est=80,
                           verify=f"{word}={pct}%")
    else:
        original = rng.randint(4, 30) * 20
        new = original + original * pct // 100 if up else original - original * pct // 100
        prompt = rng.choice([f"After a {pct}% {word}, a quantity is {new}. What was the original value?",
                             f"A coat is on sale for ${new}, which is {pct}% {'more' if up else 'less'} than its original price. What was the original price, in dollars?" if not up else
                             f"After a {pct}% raise, an employee earns ${new} per week. What was the weekly pay before the raise, in dollars?"])
        val = original
        factor = f"(1 {'+' if up else '−'} {pct}/100)"
        expl = f"new = original × {factor}, so original = {new} ÷ {factor} = {original}."
        ds = [(new + new * pct // 100 if up else new - new * pct // 100, f"This applies the {word} to the new value instead of reversing it."),
              (new - new * pct // 100 if up else new + new * pct // 100, "Divide by the factor; don't apply the opposite percent to the new value."),
              (new, "This is the value after the change, not the original."),
              (original + 10, "Arithmetic slip; recheck the division.")]
    return _numeric_mc(rng, prompt, val, ds, subskill="percent_change", explanation=expl,
                       tags=["percent", "reverse" if d == "hard" else "apply"], est=90 if d == "hard" else 70,
                       verify=f"val={val}")


def rp_ratio(rng, d):
    """Part-to-part ratios with a total; hard: ratio change."""
    p, q = rng.choice([(1, 2), (2, 3), (3, 4), (2, 5), (3, 5), (1, 3), (1, 4), (3, 7), (4, 5), (5, 7), (2, 7), (5, 8)])
    if rng.random() < 0.5:
        p, q = q, p
    ctx = rng.choice([("red", "blue", "marbles in a bag"), ("boys", "girls", "students in a class"),
                      ("cats", "dogs", "animals at a shelter"), ("fiction", "nonfiction", "books on a shelf"),
                      ("apples", "pears", "pieces of fruit in a basket")])
    k = rng.randint(3, 30)
    a, b = p * k, q * k
    if d == "easy":
        prompt = (f"The ratio of {ctx[0]} to {ctx[1]} {ctx[2]} is {p}:{q}. If there are {b} "
                  f"{ctx[1]}, how many {ctx[0]} are there?")
        val = a
        expl = f"{p}/{q} = x/{b}, so x = {p}·{b}/{q} = {a}."
        ds = [(Fraction(q * b, p), "Set up the proportion with {0} matched to {1}.".format(ctx[0], p)),
              (b - (q - p) if q > p else b + (p - q), "Ratios scale multiplicatively, not by adding a difference."),
              (a + b, "That is the total, not the number of {0}.".format(ctx[0])),
              (k, "That is the scale factor; multiply it by {0}.".format(p))]
    elif d == "medium":
        total = a + b
        prompt = (f"The ratio of {ctx[0]} to {ctx[1]} {ctx[2]} is {p}:{q}, and there are "
                  f"{total} in all. How many {ctx[0]} are there?")
        val = a
        expl = f"The ratio has {p} + {q} = {p + q} parts; each part is {total}/{p + q} = {k}, so {ctx[0]} = {p}·{k} = {a}."
        ds = [(b, "That is the number of {0}.".format(ctx[1])),
              (Fraction(total * p, q), "Divide the total by the sum of the ratio parts, not by {0}.".format(q)),
              (k, "That is one part; multiply by {0}.".format(p)),
              (total - a + k if total - a + k != b else total - k, "Recheck: each part is {0}.".format(k))]
    else:
        total = a + b
        add = rng.randint(1, 4) * (p + q)
        # add 'add' to the first group: new ratio?
        new_a = a + add
        g = math.gcd(new_a, b)
        prompt = (f"A collection of {ctx[2]} has {a} {ctx[0]} and {b} {ctx[1]}. How many "
                  f"{ctx[0]} must be added so that the ratio of {ctx[0]} to {ctx[1]} becomes "
                  f"{new_a // g}:{b // g}?")
        val = add
        expl = (f"The {ctx[1]} stay at {b}, so {ctx[0]} must become {new_a // g}·({b}/{b // g}) = "
                f"{new_a}; that is {new_a} − {a} = {add} more.")
        ds = [(new_a, "That is the new total of {0}, not the number added.".format(ctx[0])),
              (add + p, "Arithmetic slip; recompute the new count minus the old."),
              (new_a // g, "Scale the ratio to the actual count of {0} first.".format(ctx[1])),
              (abs(add - q), "Keep {0} fixed and solve for the new {1} count.".format(ctx[1], ctx[0]))]
        return _numeric_mc(rng, prompt, val, ds, subskill="unit_rate", explanation=expl,
                           tags=["ratio"], est=100, qtype="multi_step_math", verify=f"add={add}")
    return _numeric_mc(rng, prompt, val, ds, subskill="unit_rate", explanation=expl,
                       tags=["ratio"], est=75, verify=f"{a}:{b}")


_UNITS = [("feet", "inches", 12), ("yards", "feet", 3), ("hours", "minutes", 60),
          ("minutes", "seconds", 60), ("meters", "centimeters", 100), ("kilometers", "meters", 1000),
          ("pounds", "ounces", 16), ("gallons", "quarts", 4), ("days", "hours", 24), ("weeks", "days", 7),
          ("liters", "milliliters", 1000), ("kilograms", "grams", 1000)]


def rp_units(rng, d):
    """Unit conversions (one step -> two steps -> rates)."""
    big, small, f = rng.choice(_UNITS)
    if d == "easy":
        n = rng.randint(2, 40)
        if rng.random() < 0.5:
            val = n * f
            prompt = f"How many {small} are in {n} {big}?"
            expl = f"1 {big[:-1] if big.endswith('s') else big} = {f} {small}, so {n} × {f} = {val} {small}."
            ds = [(Fraction(n, f), "Multiply by the conversion factor when going to the smaller unit."),
                  (n + f, "Convert by multiplying, not adding."),
                  (val + f, "Arithmetic slip; recompute n × {0}.".format(f)),
                  (n * f * 2, "Check the conversion factor: {0}.".format(f))]
        else:
            val = n
            prompt = f"How many {big} are equal to {n * f} {small}?"
            expl = f"Divide by {f}: {n * f} ÷ {f} = {n} {big}."
            ds = [(n * f * f, "Divide by the conversion factor when going to the larger unit."),
                  (n * f - f, "Convert by dividing, not subtracting."),
                  (n + 1, "Arithmetic slip; recompute the division."),
                  (n * 2, "Check the conversion factor: {0}.".format(f))]
    elif d == "medium":
        chain = rng.choice([("yards", "inches", 36, "1 yard = 3 feet and 1 foot = 12 inches"),
                            ("hours", "seconds", 3600, "1 hour = 60 minutes and 1 minute = 60 seconds"),
                            ("days", "minutes", 1440, "1 day = 24 hours and 1 hour = 60 minutes"),
                            ("kilometers", "centimeters", 100000, "1 km = 1000 m and 1 m = 100 cm"),
                            ("gallons", "cups", 16, "1 gallon = 4 quarts and 1 quart = 4 cups"),
                            ("pounds", "ounces", 16, "1 pound = 16 ounces")])
        big, small, f, hint = chain
        n = rng.choice([Fraction(1, 2), Fraction(1, 4), Fraction(3, 4), 2, 3, 5, Fraction(3, 2), Fraction(5, 2), 1, 4, 6,
                        7, 8, 9, 10, 12, Fraction(7, 2), Fraction(9, 2), Fraction(5, 4), Fraction(7, 4), Fraction(11, 4), 15, 20])
        val = n * f
        prompt = f"How many {small} are in {num_str(n)} {big}? ({hint}.)"
        expl = f"{num_str(n)} × {f} = {num_str(val)} {small}."
        ds = [(n * (f // (12 if f == 36 else 60 if f in (3600, 1440) else 100 if f == 100000 else 4 if f == 16 else 1)), "Only one of the two conversion steps was applied."),
              (Fraction(n, f) if isinstance(n, int) or n.denominator == 1 else n * f // 2, "Multiply to convert to a smaller unit."),
              (val + f, "Arithmetic slip; recompute."),
              (n * (f + 1), "Check the product of the two conversion factors.")]
    else:
        v = rng.randint(20, 90)
        prompt = rng.choice([f"A car travels at {v} miles per hour. How many feet does it travel in one second? (1 mile = 5,280 feet.) Round to the nearest tenth.",
                             f"A machine fills {v} bottles per minute. At this rate, how many bottles does it fill in {rng.randint(2, 9)} hours and 30 minutes?"])
        if prompt.startswith("A car"):
            val = round(v * 5280 / 3600, 1)
            expl = f"{v} mi/h × 5280 ft/mi ÷ 3600 s/h = {val} ft/s."
            ds = [(round(v * 5280 / 60, 1), "Divide by 3600 seconds per hour, not 60."),
                  (round(v * 3600 / 5280, 1), "Multiply by feet per mile and divide by seconds per hour."),
                  (round(v / 3600, 2), "Convert miles to feet as well."),
                  (round(v * 5280 / 3600, 1) + 1, "Arithmetic slip; recompute.")]
        else:
            h = int(prompt.split("in ")[1].split(" hours")[0])
            mins = h * 60 + 30
            val = v * mins
            expl = f"{h} h 30 min = {mins} minutes; {v} × {mins} = {val} bottles."
            ds = [(v * h * 60, "Include the extra 30 minutes."),
                  (v * (h + 30), "Convert the time entirely to minutes before multiplying."),
                  (v * mins + 30, "Multiply the rate by the whole number of minutes."),
                  (v * (h * 60 + 50), "30 minutes is half an hour, not 0.5 × 100.")]
    return _numeric_mc(rng, prompt, val, ds, subskill="unit_rate", explanation=expl,
                       tags=["units"], est=70 if d == "easy" else 90, verify=f"val={num_str(val)}")


def rp_gridin(rng, d):
    """Grid-in: percent and ratio computations."""
    if d == "easy":
        whole = rng.randint(20, 90) * 5
        pct = rng.choice([5, 10, 15, 20, 25, 30, 40, 60, 75, 80])
        val = whole * pct // 100
        prompt = f"What is {pct}% of {whole}?"
        expl = f"({pct}/100)·{whole} = {val}."
    elif d == "medium":
        old = rng.randint(2, 50) * 20
        pct = rng.choice([5, 10, 15, 20, 25, 30, 40, 50])
        new = old + old * pct // 100
        prompt = f"A value increases from {old} to {new}. By what percent did it increase? (Ignore the percent sign when gridding.)"
        val = pct
        expl = f"({new} − {old})/{old} × 100 = {pct}."
    else:
        pct = rng.choice([10, 20, 25, 40, 50, 60, 75])
        original = rng.randint(4, 40) * 20
        new = original - original * pct // 100
        prompt = f"After a {pct}% discount, an item costs ${new}. What was the original price, in dollars?"
        val = original
        expl = f"{new} = original × (1 − {pct}/100), so original = {new}/{(100 - pct) / 100} = {original}."
    return _spr_num(prompt, val, subskill="percent_change", explanation=expl,
                    tags=["percent", "grid-in"], est=75, verify=f"val={val}")


rp_gridin.sat_only = True


# --------------------------------------------------------------------------- #
# proportions
# --------------------------------------------------------------------------- #
def pr_direct(rng, d):
    """Direct proportion: scale a rate."""
    rate_n = rng.randint(2, 15)
    rate_d = rng.randint(2, 9)
    unit = rng.choice([("miles", "hours", "A cyclist rides"), ("pages", "minutes", "A printer prints"),
                       ("liters", "minutes", "A pump moves"), ("loaves", "hours", "A bakery makes"),
                       ("parts", "minutes", "A machine produces")])
    if d == "easy":
        mult = rng.randint(3, 12)
        given = rate_d * mult
        val = rate_n * mult
        prompt = (f"{unit[2]} {rate_n} {unit[0]} every {rate_d} {unit[1]}. At this rate, how "
                  f"many {unit[0]} in {given} {unit[1]}?")
        expl = f"Set up {rate_n}/{rate_d} = x/{given}; x = {rate_n}·{given}/{rate_d} = {val}."
        ds = [(rate_n * given, "You forgot to divide by {0}.".format(rate_d)),
              (given - rate_d + rate_n, "This adds instead of scaling proportionally."),
              (val + rate_n, "Off by one multiple; recheck the scale factor."),
              (Fraction(rate_d * given, rate_n), "The proportion is set up upside down.")]
    elif d == "medium":
        per = rng.randint(2, 12)
        n1 = rng.randint(2, 6)
        n2 = rng.choice([k for k in range(7, 25) if k != n1])
        c1, val = per * n1, per * n2
        thing = rng.choice(["notebooks", "tickets", "bags of rice", "movie passes", "plants"])
        prompt = rng.choice([f"{n1} {thing} cost ${c1}. At the same rate, how much do {n2} {thing} cost, in dollars?",
                             f"If {n1} {thing} cost ${c1}, what is the cost, in dollars, of {n2} {thing} at the same price each?"])
        expl = f"Unit price = {c1} ÷ {n1} = ${per}; {n2} × {per} = ${val}."
        ds = [(c1 * n2, "Divide by {0} to get the unit price first.".format(n1)),
              (c1 + (n2 - n1), "Each extra item costs the unit price, not $1."),
              (per * (n2 - n1), "This prices only the extra items."),
              (val + per, "Off by one item.")]
    else:
        a, b = rng.randint(2, 9), rng.randint(2, 9)
        x_given = rng.randint(2, 12) * b
        k = Fraction(a, b)
        y_given = k * x_given
        x_new = rng.choice([v * b for v in range(1, 15) if v * b != x_given])
        val = k * x_new
        prompt = (f"The quantity y is directly proportional to x. When x = {x_given}, "
                  f"y = {num_str(y_given)}. What is the value of y when x = {x_new}?")
        expl = (f"y = kx with k = {num_str(y_given)}/{x_given} = {num_str(k)}; "
                f"y = {num_str(k)}·{x_new} = {num_str(val)}.")
        ds = [(Fraction(x_new * x_given, y_given) if y_given else val + 1, "Direct proportion: y/x is constant, so y₂ = y₁·(x₂/x₁)."),
              (y_given + (x_new - x_given), "Proportional change is multiplicative, not additive."),
              (k, "That is the constant of proportionality; multiply it by the new x."),
              (Fraction(y_given * x_given, x_new), "That is an inverse-proportion computation.")]
    return _numeric_mc(rng, prompt, val, ds, subskill="direct_proportion", explanation=expl,
                       tags=["proportion", "rate"], est=75 if d == "easy" else 90,
                       verify=f"val={num_str(val)}")


def pr_solve(rng, d):
    """Solve a bare proportion a/b = x/c (or with an expression)."""
    a, b = rng.randint(1, 12), rng.randint(2, 12)
    if d == "easy":
        k = rng.randint(2, 9)
        c = b * k
        val = a * k
        prompt = f"If {a}/{b} = x/{c}, what is the value of x?"
        expl = f"Cross-multiply: {b}x = {a}·{c} = {a * c}, so x = {val}."
        ds = [(Fraction(b * c, a), "The proportion is inverted."),
              (a * c, "That is {0}x; divide by {0}.".format(b)),
              (a + (c - b), "Scale by multiplying, not adding."),
              (val + k, "Arithmetic slip; recheck {0}·{1}/{2}.".format(a, c, b))]
    elif d == "medium":
        k = rng.randint(2, 9)
        c = a * k
        val = b * k
        prompt = rng.choice([f"If {a}/{b} = {c}/x, what is the value of x?",
                             f"What value of x makes {a}/{b} and {c}/x equal?"])
        expl = f"Cross-multiply: {a}x = {b}·{c} = {b * c}, so x = {val}."
        ds = [(Fraction(a * c, b), "x is in the denominator here; cross-multiply carefully."),
              (b * c, "That is {0}x; divide by {0}.".format(a)),
              (c - a + b, "Scale multiplicatively."),
              (val - b, "Arithmetic slip; recheck.")]
    else:
        # (x + p)/q = r/s with integer solution
        q, s = rng.randint(2, 9), rng.randint(2, 9)
        x = rng.randint(1, 20)
        p = rng.choice([v for v in range(-9, 10) if v != 0])
        # (x + p)/q = r/s -> r = s (x + p)/q ; choose q dividing s(x+p): simplest set r = s*(x+p) and denominator q*s... keep ints: let q = 1? no. Use r = (x+p)*s/q with x+p multiple of q
        x = q * rng.randint(1, 6) - p
        if x <= 0:
            x += q * 3
        r = s * (x + p) // q
        prompt = f"If (x {_pm(p)})/{q} = {r}/{s}, what is the value of x?"
        val = x
        expl = f"Cross-multiply: {s}(x {_pm(p)}) = {q}·{r} = {q * r}, so x {_pm(p)} = {q * r // s} and x = {x}."
        ds = [(x + p, "That is x + {0}; subtract {0}.".format(_m(p))),
              (x + 2 * p, "Move {0} to the other side with the opposite sign.".format(_m(p))),
              (Fraction(q * r, s) + p, "Subtract p after dividing, don't add."),
              (x - 1, "Arithmetic slip in the division.")]
    return _numeric_mc(rng, prompt, val, ds, subskill="direct_proportion", explanation=expl,
                       tags=["proportion", "solve"], est=70 if d != "hard" else 85, verify=f"x={val}")


def pr_inverse(rng, d):
    """Inverse proportion: workers/time, speed/time."""
    if d == "medium":
        w1 = rng.randint(2, 6)
        w2 = rng.choice([w for w in range(2, 13) if w != w1])
        per = rng.randint(2, 8)
        h1 = per * w2
        val = per * w1
        prompt = (f"It takes {w1} painters {h1} hours to paint a house. Working at the same "
                  f"rate, how many hours would it take {w2} painters?")
        expl = f"Total work = {w1}×{h1} = {w1 * h1} painter-hours; ÷ {w2} painters = {val} hours."
        ds = [(Fraction(h1 * w2, w1), "More painters means less time; this scales the wrong way."),
              (h1, "This ignores the change in the number of painters."),
              (w1 * h1, "That is total painter-hours, not the time for {0} painters.".format(w2)),
              (h1 - (w2 - w1), "Inverse proportion is multiplicative, not additive.")]
    else:
        s1 = rng.randint(30, 80)
        t1 = rng.randint(2, 9)
        D = s1 * t1
        cands = [v for v in range(20, 100) if D % v == 0 and v != s1]
        if not cands:
            return pr_inverse(rng, d)
        s2 = rng.choice(cands)
        val = D // s2
        prompt = (f"A trip takes {t1} hours at an average speed of {s1} miles per hour. "
                  f"How many hours would the same trip take at an average speed of {s2} "
                  f"miles per hour?")
        expl = f"Distance = {s1}×{t1} = {D} miles; at {s2} mph the time is {D}/{s2} = {val} hours."
        ds = [(Fraction(s2 * t1, s1), "Faster means less time; the proportion is inverted."),
              (D, "That is the distance, not the time."),
              (t1 + (s1 - s2), "Inverse proportion is multiplicative."),
              (val + 1, "Arithmetic slip; recompute {0}/{1}.".format(D, s2))]
    return _numeric_mc(rng, prompt, val, ds, subskill="scaling", explanation=expl,
                       tags=["proportion", "inverse"], est=95, verify=f"val={val}")


def pr_similar(rng, d):
    """Similar figures / scale drawings."""
    if d == "easy":
        scale = rng.randint(2, 12)
        cm = rng.randint(2, 15)
        prompt = (f"On a map, 1 centimeter represents {scale} kilometers. Two towns are "
                  f"{cm} centimeters apart on the map. How many kilometers apart are they?")
        val = cm * scale
        expl = f"{cm} cm × {scale} km/cm = {val} km."
        ds = [(Fraction(cm, scale), "Multiply by the scale to go from map to real distance."),
              (cm + scale, "Scale by multiplying, not adding."),
              (val + scale, "Arithmetic slip; recompute."),
              (scale, "That is the scale, not the distance.")]
    elif d == "medium":
        a, b, c = _pyth_triple(rng, 26)
        k = rng.randint(2, 5)
        which = rng.choice([0, 1, 2])
        sides = (a, b, c)
        names = ("the shortest side", "the middle side", "the longest side")
        prompt = (f"Two triangles are similar. The sides of the smaller triangle are {a}, "
                  f"{b}, and {c}. If the shortest side of the larger triangle is {a * k}, "
                  f"what is the length of {names[which]} of the larger triangle?")
        val = sides[which] * k
        expl = f"The scale factor is {a * k}/{a} = {k}; {sides[which]} × {k} = {val}."
        ds = [(sides[which] + a * k - a, "Similar triangles scale by multiplying, not adding."),
              (sides[(which + 1) % 3] * k, "That is a different side of the larger triangle."),
              (Fraction(sides[which], k), "Multiply by the scale factor; the larger triangle is bigger."),
              (sides[which] * (k + 1), "Recheck the scale factor: {0}/{1} = {2}.".format(a * k, a, k))]
    else:
        w, h = rng.randint(3, 12), rng.randint(3, 12)
        if w == h:
            h += 1
        k = rng.randint(2, 4)
        prompt = (f"A rectangular photo {w} inches wide and {h} inches tall is enlarged so "
                  f"that its width becomes {w * k} inches. What is the area, in square inches, "
                  f"of the enlarged photo?")
        val = w * h * k * k
        expl = f"Scale factor {k}: new dimensions {w * k} by {h * k}, area {w * k}×{h * k} = {val}."
        ds = [(w * h * k, "Both dimensions scale, so area scales by k², not k."),
              (w * h * k ** 3, "Area scales by k², not k³ (that is for volume)."),
              (w * h, "That is the original area."),
              (2 * (w * k + h * k), "That is the new perimeter, not the area."),
              (w * k * h + w, "Arithmetic slip; recompute the scaled dimensions.")]
    return _numeric_mc(rng, prompt, val, ds, subskill="scaling", explanation=expl,
                       tags=["proportion", "similar"], est=80 if d != "hard" else 95,
                       verify=f"val={val}")


def pr_recipe(rng, d):
    """Scaling a recipe/mixture (easy/medium); mixture concentration (hard)."""
    if d != "hard":
        base_servings = rng.choice([2, 4, 6, 8])
        cups = rng.choice([Fraction(1, 2), Fraction(3, 4), 1, Fraction(3, 2), 2, Fraction(5, 2), 3])
        mult = rng.randint(2, 6) if d == "easy" else rng.choice([Fraction(1, 2), Fraction(3, 2), Fraction(5, 2), 3, Fraction(7, 2)])
        new_servings = base_servings * mult
        val = cups * mult
        ingredient = rng.choice(["flour", "sugar", "rice", "oats", "milk"])
        prompt = (f"A recipe that serves {base_servings} people calls for {num_str(cups)} cups of "
                  f"{ingredient}. How many cups of {ingredient} are needed to serve "
                  f"{num_str(new_servings)} people?")
        expl = f"The recipe is scaled by {num_str(new_servings)}/{base_servings} = {num_str(mult)}; {num_str(cups)} × {num_str(mult)} = {num_str(val)} cups."
        ds = [(cups + (new_servings - base_servings), "Scale multiplicatively, not by adding the extra servings."),
              (cups * new_servings, "Divide by the original number of servings first."),
              (Fraction(cups, mult), "The recipe is scaled up, not down.") if mult > 1 else (cups * 2, "Scale down when serving fewer people."),
              (val + Fraction(1, 2), "Arithmetic slip; recompute.")]
        return _numeric_mc(rng, prompt, val, ds, subskill="scaling", explanation=expl,
                           tags=["proportion", "recipe"], est=75, verify=f"val={num_str(val)}")
    # hard: mixture — liters of pure solution to add to reach a concentration
    v0 = rng.randint(2, 10) * 10
    c0 = rng.choice([10, 20, 25, 30, 40])
    c1 = rng.choice([c for c in (20, 25, 40, 50, 60) if c > c0])
    # (c0 v0 + 100 x) / (v0 + x) = c1 -> x = v0 (c1 - c0)/(100 - c1)
    x = Fraction(v0 * (c1 - c0), 100 - c1)
    prompt = (f"A {v0}-liter solution is {c0}% acid. How many liters of pure acid must be "
              f"added to make the solution {c1}% acid?")
    expl = (f"Acid: {c0}% of {v0} = {c0 * v0 // 100} L. Adding x liters: ({c0 * v0 // 100} + x)/({v0} + x) "
            f"= {c1}/100, so x = {num_str(x)}.")
    ds = [(Fraction(v0 * (c1 - c0), 100), "The added acid also increases the total volume."),
          (Fraction(v0 * c1, 100) - Fraction(v0 * c0, 100), "Account for the change in total volume."),
          (x + v0, "That is the new total volume, not the amount added."),
          (Fraction(v0 * (c1 - c0), c1), "The denominator should be 100 − {0}.".format(c1))]
    return _numeric_mc(rng, prompt, x, ds, subskill="scaling", explanation=expl,
                       qtype="multi_step_math", tags=["proportion", "mixture"], est=110,
                       verify=f"x={num_str(x)}")


def pr_gridin(rng, d):
    """Grid-in proportion."""
    if d == "easy":
        a, b, k = rng.randint(1, 12), rng.randint(2, 12), rng.randint(2, 9)
        prompt = f"If {a}/{b} = x/{b * k}, what is the value of x?"
        val = a * k
        expl = f"Cross-multiply: {b}x = {a * b * k}, so x = {val}."
    elif d == "medium":
        per, n1, n2 = rng.randint(2, 12), rng.randint(2, 6), rng.randint(7, 25)
        prompt = f"{n1} identical tickets cost ${per * n1}. How much, in dollars, do {n2} of the same tickets cost?"
        val = per * n2
        expl = f"Each ticket is ${per}; {n2} × {per} = {val}."
    else:
        w1, w2, per = rng.randint(2, 6), rng.randint(2, 12), rng.randint(2, 8)
        if w1 == w2:
            w2 += 1
        prompt = f"It takes {w1} workers {per * w2} hours to complete a job. At the same rate, how many hours would {w2} workers take?"
        val = per * w1
        expl = f"{w1} × {per * w2} = {w1 * per * w2} worker-hours; ÷ {w2} = {val}."
    return _spr_num(prompt, val, subskill="direct_proportion", explanation=expl,
                    tags=["proportion", "grid-in"], est=75, verify=f"val={val}")


pr_gridin.sat_only = True


# --------------------------------------------------------------------------- #
# data_analysis (table stimuli)
# --------------------------------------------------------------------------- #
_DA_CTX = [("Day", "Tickets sold", ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat"], "Daily ticket sales", "tickets"),
           ("Month", "Rainfall (mm)", ["Jan", "Feb", "Mar", "Apr", "May", "Jun"], "Monthly rainfall", "millimeters of rain"),
           ("Store", "Bikes sold", ["North", "South", "East", "West", "Central", "Harbor"], "Bike sales by store", "bikes"),
           ("Team", "Points scored", ["Hawks", "Bears", "Otters", "Lynx", "Wolves", "Rams"], "Points scored", "points"),
           ("Plant", "Height (cm)", ["A", "B", "C", "D", "E", "F"], "Plant heights", "centimeters")]


def _da_table(rng, n, lo=10, hi=60):
    cat, qty, labels, cap, unit = rng.choice(_DA_CTX)
    labs = labels[:n]
    vals = [rng.randint(lo, hi) for _ in labs]
    return cat, qty, labs, vals, cap, unit


def da_read(rng, d):
    """Read values: total/max/difference (easy); percent of total or ratio (medium/hard)."""
    n = 4 if d == "easy" else 5
    cat, qty, labs, vals, cap, unit = _da_table(rng, n)
    total = sum(vals)
    stim = _table(cap, [cat, qty], [[l, v] for l, v in zip(labs, vals)])
    if d == "easy":
        mode = rng.choice(["total", "max", "diff", "sum2"])
        if mode == "total":
            val = total
            prompt = f"Based on the table, what is the total number of {unit} for all {n} {cat.lower()}s combined?"
            expl = f"Add the values: {' + '.join(map(str, vals))} = {total}."
            ds = [(max(vals), "This is only the largest single value."),
                  (total - min(vals), "This omits the smallest value."),
                  (total + min(vals), "This double-counts the smallest value."),
                  (total // n, "That is the mean, not the total.")]
        elif mode == "max":
            val = max(vals)
            prompt = f"According to the table, which is the greatest number of {unit} recorded for a single {cat.lower()}?"
            expl = f"The largest value in the table is {val} ({labs[vals.index(val)]})."
            ds = [(min(vals), "This is the least value."),
                  (total // n, "This is the average, not the maximum."),
                  (sorted(vals)[-2], "This is the second-largest value."),
                  (total, "That is the total of all values.")]
        elif mode == "diff":
            val = max(vals) - min(vals)
            prompt = f"Based on the table, how many more {unit} does the greatest {cat.lower()} have than the least?"
            expl = f"Greatest {max(vals)} − least {min(vals)} = {val}."
            ds = [(max(vals), "This is only the greatest value."),
                  (max(vals) + min(vals), "Subtract; don't add."),
                  (total, "This is the total, not the difference."),
                  (val + 2, "Recheck the subtraction.")]
        else:
            i, j = sorted(rng.sample(range(n), 2))
            val = vals[i] + vals[j]
            prompt = f"Based on the table, what is the combined number of {unit} for {labs[i]} and {labs[j]}?"
            expl = f"{vals[i]} + {vals[j]} = {val}."
            ds = [(abs(vals[i] - vals[j]), "Add the two values; don't subtract."),
                  (total, "Only two of the {0}s are asked about.".format(cat.lower())),
                  (val + min(vals), "Add only the two requested rows."),
                  (vals[i], "That is one row only.")]
        return _numeric_mc(rng, prompt, val, ds, subskill="tables", explanation=expl,
                           qtype="data_interpretation", tags=["data", "table"], est=70,
                           stimulus=stim, verify=f"val={val}")
    if d == "medium":
        i = rng.randrange(n)
        pct = round(100 * vals[i] / total)
        val = pct
        prompt = f"Based on the table, approximately what percent of the total {unit} were recorded for {labs[i]}?"
        expl = f"{vals[i]}/{total} × 100 ≈ {pct}%."
        ds = [(round(100 * vals[i] / (total - vals[i])), "Divide by the total of all rows, not the other rows."),
              (vals[i], "That is the count, not a percent."),
              (round(100 * (total - vals[i]) / total), "That is the percent for all the other rows."),
              (round(100 * vals[i] / total) + 10, "Arithmetic slip; recompute the fraction.")]
        return _numeric_mc(rng, prompt, val, ds, subskill="tables", explanation=expl,
                           qtype="data_interpretation", tags=["data", "table", "percent"],
                           fmt=lambda v: f"{num_str(v)}%", est=85, stimulus=stim, verify=f"{vals[i]}/{total}")
    i, j = rng.sample(range(n), 2)
    g = math.gcd(vals[i], vals[j])
    val = Fraction(vals[i], vals[j])
    prompt = f"Based on the table, what is the ratio of {unit} for {labs[i]} to {unit} for {labs[j]}?"
    expl = f"{vals[i]}:{vals[j]} = {vals[i] // g}:{vals[j] // g}, i.e. {num_str(val)}."
    ds = [(Fraction(vals[j], vals[i]), "The ratio is in the wrong order."),
          (Fraction(vals[i], total), "That compares {0} to the total, not to {1}.".format(labs[i], labs[j])),
          (Fraction(vals[i] - vals[j], vals[j]) if vals[i] != vals[j] else val + 1, "A ratio is a quotient, not a difference over a value."),
          (Fraction(vals[i], vals[j] + 1), "Read the correct rows.")]
    return _numeric_mc(rng, prompt, val, ds, subskill="tables", explanation=expl,
                       qtype="data_interpretation", tags=["data", "table", "ratio"], est=85,
                       stimulus=stim, verify=f"{vals[i]}/{vals[j]}")


def da_mean_from_table(rng, d):
    """Mean of table values (medium); excess over mean / missing value (hard); easy: find missing row given total."""
    n = 4 if d == "easy" else 5
    cat, qty, labs, vals, cap, unit = _da_table(rng, n)
    if d != "easy":
        vals[-1] += (n - sum(vals) % n) % n
    total = sum(vals)
    mean = total // n
    if d == "easy":
        i = rng.randrange(n)
        rows = [[l, v if k != i else "?"] for k, (l, v) in enumerate(zip(labs, vals))]
        stim = _table(cap, [cat, qty], rows)
        prompt = f"The table shows {unit} for {n} {cat.lower()}s, but the value for {labs[i]} is missing. If the total for all {n} is {total}, what is the missing value?"
        val = vals[i]
        expl = f"{total} − ({' + '.join(str(v) for k, v in enumerate(vals) if k != i)}) = {val}."
        ds = [(total - val, "That is the sum of the other rows, not the missing one."),
              (total // n, "That is the mean, not necessarily the missing value."),
              (val + min(v for k, v in enumerate(vals) if k != i), "Subtract every known row from the total."),
              (total, "That is the total, not the missing value.")]
        return _numeric_mc(rng, prompt, val, ds, subskill="tables", explanation=expl,
                           qtype="data_interpretation", tags=["data", "table"], est=75,
                           stimulus=stim, verify=f"missing={val}")
    stim = _table(cap, [cat, qty], [[l, v] for l, v in zip(labs, vals)])
    if d == "medium":
        prompt = f"Based on the table, what is the mean number of {unit} per {cat.lower()}?"
        val = mean
        expl = f"Mean = total ÷ count = {total} ÷ {n} = {mean}."
        ds = [(max(vals), "This is the largest value, not the average."),
              (max(vals) - min(vals), "This is the range, not the mean."),
              (total, "This is the total; divide by the number of {0}s.".format(cat.lower())),
              (sorted(vals)[n // 2], "This is the median, not the mean.")]
        return _numeric_mc(rng, prompt, val, ds, subskill="tables", explanation=expl,
                           qtype="data_interpretation", tags=["data", "table", "mean"], est=85,
                           stimulus=stim, verify=f"mean={mean}")
    mode = rng.choice(["excess", "needed"])
    if mode == "excess":
        val = max(vals) - mean
        busy = labs[vals.index(max(vals))]
        prompt = f"Based on the table, how many more {unit} than the mean per {cat.lower()} were recorded for {busy}?"
        expl = f"Mean = {total} ÷ {n} = {mean}; {max(vals)} − {mean} = {val}."
        ds = [(max(vals), "That is the value itself, not its excess over the mean."),
              (mean, "That is the mean, not the amount above it."),
              (max(vals) - min(vals), "This compares to the least value, not the mean."),
              (val + 1, "Arithmetic slip; recompute the mean.")]
    else:
        target = mean + rng.randint(1, 8)
        val = target * (n + 1) - total
        prompt = (f"A {_ordinal(n + 1)} {cat.lower()} is to be added to the table. How many "
                  f"{unit} must it have so that the mean for all {n + 1} {cat.lower()}s is {target}?")
        expl = f"Needed total = {target} × {n + 1} = {target * (n + 1)}; minus the current total {total} gives {val}."
        ds = [(target, "The new value must pull the mean up; it is larger than the target mean."),
              (target * n - total, "Use {0} rows after the addition, not {1}.".format(n + 1, n)),
              (target * (n + 1), "That is the required total, not the added value."),
              (val - target, "Subtract the current total from the required total.")]
    return _numeric_mc(rng, prompt, val, ds, subskill="tables", explanation=expl,
                       qtype="data_interpretation", tags=["data", "table", "mean"], est=100,
                       stimulus=stim, verify=f"mean={mean};val={val}")


def da_two_year(rng, d):
    """Two-column tables: which category changed most / statement supported (text)."""
    n = 4 if d == "easy" else 5
    cat, qty, labs, vals, cap, unit = _da_table(rng, n, 20, 80)
    deltas = rng.sample(range(-25, 26), n)
    y1, y2 = rng.choice([(2021, 2022), (2022, 2023), (2023, 2024)])
    vals2 = [max(5, v + dl) for v, dl in zip(vals, deltas)]
    deltas = [b - a for a, b in zip(vals, vals2)]
    stim = _table(f"{cap}, {y1} and {y2}", [cat, f"{y1}", f"{y2}"],
                  [[l, a, b] for l, a, b in zip(labs, vals, vals2)])
    lead = (f"The table shows the number of {unit} for {n} {cat.lower()}s in {y1} and {y2} "
            f"(a total of {sum(vals)} in {y1} and {sum(vals2)} in {y2}). ")
    if d == "easy":
        i = max(range(n), key=lambda k: deltas[k])
        if sorted(deltas)[-1] == sorted(deltas)[-2]:
            return da_two_year(rng, d)
        prompt = f"{lead}Which {cat.lower()} had the greatest increase in {unit} from {y1} to {y2}?"
        correct = labs[i]
        ds = [(labs[k], f"{labs[k]} changed by {_m(deltas[k])}, which is not the greatest increase.")
              for k in range(n) if k != i]
        expl = f"Compute {y2} − {y1} for each row; {labs[i]} increased by {deltas[i]}, the most."
    elif d == "medium":
        i = min(range(n), key=lambda k: deltas[k])
        if sorted(deltas)[0] == sorted(deltas)[1]:
            return da_two_year(rng, d)
        prompt = f"{lead}Which {cat.lower()} had the greatest decrease in {unit} from {y1} to {y2}?"
        if deltas[i] >= 0:
            return da_two_year(rng, d)
        correct = labs[i]
        ds = [(labs[k], f"{labs[k]} changed by {_m(deltas[k])}, which is not the greatest decrease.")
              for k in range(n) if k != i]
        expl = f"{labs[i]} went from {vals[i]} to {vals2[i]}, a decrease of {-deltas[i]}, the largest drop."
    else:
        pcts = [round(100 * dl / a) for dl, a in zip(deltas, vals)]
        i = max(range(n), key=lambda k: pcts[k])
        if sorted(pcts)[-1] == sorted(pcts)[-2] or pcts[i] <= 0:
            return da_two_year(rng, d)
        j = max(range(n), key=lambda k: deltas[k])
        prompt = f"{lead}Which {cat.lower()} had the greatest percent increase in {unit} from {y1} to {y2}?"
        correct = labs[i]
        ds = [(labs[k], f"{labs[k]} changed by about {_m(pcts[k])}%" + (", the largest raw increase but not the largest percent increase." if k == j and j != i else "."))
              for k in range(n) if k != i]
        expl = f"Percent change = (new − old)/old; {labs[i]}: {deltas[i]}/{vals[i]} ≈ {pcts[i]}%, the greatest."
    return _text_mc(rng, prompt, correct, ds, subskill="tables", explanation=expl,
                    qtype="data_interpretation", tags=["data", "table", "compare"],
                    est=80 if d == "easy" else 100, stimulus=stim, verify=f"{correct}")


def da_rate_table(rng, d):
    """Distance/time or cost/quantity tables: find the constant rate or extrapolate."""
    r = rng.randint(2, 15) * (1 if d == "easy" else rng.choice([1, 5]))
    ctx = rng.choice([("Time (hours)", "Distance (miles)", "miles per hour", "distance"),
                      ("Number of items", "Cost (dollars)", "dollars per item", "cost"),
                      ("Minutes", "Gallons pumped", "gallons per minute", "amount")])
    xs = sorted(rng.sample(range(1, 10), 4))
    b = 0 if d != "hard" else rng.randint(5, 40)
    ys = [r * x + b for x in xs]
    stim = _table("Recorded values", [ctx[0], ctx[1]], [[x, y] for x, y in zip(xs, ys)])
    if d == "easy":
        prompt = f"The table shows a constant rate. What is the rate, in {ctx[2]}?"
        val = r
        expl = f"Divide any row: {ys[0]} ÷ {xs[0]} = {r} {ctx[2]}."
        ds = [(ys[0], "That is a value from the table, not the rate."),
              (Fraction(xs[1], ys[1]), "Divide the second column by the first, not the reverse."),
              (ys[1] - ys[0], "Divide by the change in the first column too.") if xs[1] - xs[0] != 1 else (r + 1, "Arithmetic slip."),
              (r * 2, "Recheck the division.")]
    elif d == "medium":
        k = rng.choice([v for v in range(10, 25)])
        prompt = f"The table shows a constant rate. At this rate, what is the {ctx[3]} when the first column is {k}?"
        val = r * k
        expl = f"Rate = {ys[0]}/{xs[0]} = {r}; {r} × {k} = {val}."
        ds = [(ys[-1] + (k - xs[-1]), "Each unit adds {0}, not 1.".format(r)),
              (r + k, "Multiply the rate by {0}; don't add.".format(k)),
              (ys[-1] * k, "Use the unit rate, not the last table value."),
              (val + r, "Off by one unit.")]
    else:
        prompt = (f"The values in the table follow a linear relationship. Which equation gives "
                  f"the second quantity y in terms of the first quantity x?")
        correct = f"y = {_lin(r, b)}"
        ds = [(f"y = {_lin(b, r)}", "The slope and the constant are swapped."),
              (f"y = {_lin(r, 0)}", "The relationship has a nonzero starting value; check x = 0."),
              (f"y = {_lin(r, ys[0])}", f"{ys[0]} is y when x = {xs[0]}, not when x = 0."),
              (f"y = {_lin(ys[1] - ys[0], b)}" if ys[1] - ys[0] != r else f"y = {_lin(r + 1, b)}", "Divide the change in y by the change in x to get the rate.")]
        expl = (f"Between rows, y changes by {r} per unit of x, so the rate is {r}; then "
                f"{ys[0]} = {r}·{xs[0]} + b gives b = {b}.")
        return _text_mc(rng, prompt, correct, ds, subskill="graphs", explanation=expl,
                        qtype="data_interpretation", tags=["data", "table", "linear"], est=100,
                        stimulus=stim, verify=f"y={r}x+{b}")
    return _numeric_mc(rng, prompt, val, ds, subskill="graphs", explanation=expl,
                       qtype="data_interpretation", tags=["data", "table", "rate"],
                       est=75 if d == "easy" else 90, stimulus=stim, verify=f"r={r},val={val}")


def da_statement(rng, d):
    """Which statement is supported by the table (text options)."""
    n = 4 if d != "hard" else 5
    cat, qty, labs, vals, cap, unit = _da_table(rng, n, 10, 90)
    if len(set(vals)) < n:
        return da_statement(rng, d)
    total = sum(vals)
    stim = _table(cap, [cat, qty], [[l, v] for l, v in zip(labs, vals)])
    hi, lo = labs[vals.index(max(vals))], labs[vals.index(min(vals))]
    order = sorted(range(n), key=lambda k: -vals[k])
    second = labs[order[1]]
    mean = total / n
    above = [labs[k] for k in range(n) if vals[k] > mean]
    i, j = order[0], order[-1]
    if d == "easy":
        correct = f"{hi} recorded more {unit} than any other {cat.lower()}."
        ds = [(f"{lo} recorded more {unit} than any other {cat.lower()}.", f"{lo} has the least value, {min(vals)}."),
              (f"{second} recorded the greatest number of {unit} of any {cat.lower()}.", f"{hi} has {max(vals)}, more than {second}."),
              (f"The total number of {unit} for all {n} {cat.lower()}s is {total + rng.randint(5, 20)}.", f"The values sum to {total}."),
              (f"{hi} recorded fewer {unit} than {lo} recorded.", f"{hi} has {max(vals)}, far more than {lo}'s {min(vals)}.")]
        expl = f"{hi} has the largest value in the table ({max(vals)})."
    elif d == "medium":
        correct = f"{hi} recorded {max(vals) - min(vals)} more {unit} than {lo}."
        ds = [(f"{hi} recorded {max(vals) + min(vals)} more {unit} than {lo}.", "That is the sum, not the difference, of the two values."),
              (f"{lo} recorded {max(vals) - min(vals)} more {unit} than {hi}.", "The comparison is reversed."),
              (f"The mean number of {unit} is {max(vals)}.", f"The mean is {total}/{n} = {mean:.1f}."),
              (f"{second} recorded exactly twice as many {unit} as {lo}.", f"{vals[order[1]]} is not twice {min(vals)}." if vals[order[1]] != 2 * min(vals) else "Check again.")]
        if vals[order[1]] == 2 * min(vals):
            return da_statement(rng, d)
        expl = f"{max(vals)} − {min(vals)} = {max(vals) - min(vals)}."
    else:
        k = len(above)
        correct = f"Exactly {k} of the {cat.lower()}s recorded more {unit} than the mean."
        ds = [(f"Exactly {n - k} of the {cat.lower()}s recorded more {unit} than the mean.", f"The mean is {mean:.1f}; count the values above it: {k}."),
              (f"The median number of {unit} equals the mean.", f"The median is {sorted(vals)[n // 2]} and the mean is {mean:.1f}."),
              (f"{hi} accounts for more than half of the total {unit}.", f"{max(vals)} is less than half of {total}." if max(vals) * 2 < total else "Check the arithmetic."),
              (f"The range of the values is {max(vals) - min(vals) + rng.randint(1, 9)}.", f"The range is {max(vals)} − {min(vals)} = {max(vals) - min(vals)}.")]
        if max(vals) * 2 >= total or k in (0, n) or sorted(vals)[n // 2] == mean:
            return da_statement(rng, d)
        expl = f"The mean is {total}/{n} = {mean:.1f}; the values above it are {', '.join(above)} ({k} of them)."
    prompt = (f"The table shows the number of {unit} recorded for {n} {cat.lower()}s, "
              f"{total} in all. Which of the following statements is supported by the data?")
    return _text_mc(rng, prompt, correct, ds, subskill="tables", explanation=expl,
                    qtype="data_interpretation", tags=["data", "table", "statement"],
                    est=85 if d != "hard" else 105, stimulus=stim, verify="statement")


# --------------------------------------------------------------------------- #
# statistics
# --------------------------------------------------------------------------- #
def _data_list(rng, n, lo=2, hi=30):
    return [rng.randint(lo, hi) for _ in range(n)]


def st_center_list(rng, d):
    """Mean / median / mode of a listed data set."""
    if d == "easy":
        n = 5
        data = sorted(_data_list(rng, n, 2, 25))
        mode = rng.choice(["mean", "median"])
    elif d == "medium":
        n = rng.choice([6, 8])
        data = sorted(_data_list(rng, n, 3, 40))
        mode = rng.choice(["median", "mode", "mean"])
    else:
        n = rng.choice([7, 9])
        data = sorted(_data_list(rng, n, 5, 60))
        mode = rng.choice(["median_vs_mean", "mean"])
    if mode in ("mean",) :
        s = sum(data)
        if s % n:
            data[-1] += n - (s % n)
            s = sum(data)
        val = s // n
        shown = ", ".join(map(str, rng.sample(data, len(data))))
        ctx = rng.choice([f"What is the mean (average) of the data set {shown}?",
                          f"The numbers of points {rng.choice(NAMES)} scored in {n} games were {shown}. What was the mean number of points per game?",
                          f"A sample of {n} packages had weights, in pounds, of {shown}. What is the mean weight?"])
        expl = f"Mean = sum ÷ count = {s} ÷ {n} = {val}."
        med = data[n // 2] if n % 2 else Fraction(data[n // 2 - 1] + data[n // 2], 2)
        ds = [(med, "This is the median, not the mean."),
              (max(data) - min(data), "This is the range, not the mean."),
              (val + 1, "Recheck the sum before dividing."),
              (s, "This is the sum; divide by the count.")]
        return _numeric_mc(rng, ctx, val, ds, subskill="mean_median_mode", explanation=expl,
                           tags=["statistics", "mean"], est=75, verify=f"mean={val}")
    if mode == "median":
        val = data[n // 2] if n % 2 else Fraction(data[n // 2 - 1] + data[n // 2], 2)
        shown = ", ".join(map(str, rng.sample(data, len(data))))
        prompt = rng.choice([f"What is the median of the data set {shown}?",
                             f"The ages of {n} volunteers are {shown}. What is the median age?",
                             f"The daily high temperatures, in °F, over {n} days were {shown}. What was the median high temperature?"])
        expl = (f"Order the data: {', '.join(map(str, data))}. " +
                (f"The middle value is {val}." if n % 2 else
                 f"The two middle values are {data[n // 2 - 1]} and {data[n // 2]}; their average is {num_str(val)}."))
        ds = [(Fraction(sum(data), n), "This is the mean, not the median."),
              (max(data) - min(data), "This is the range, not the median."),
              (data[0], "The median is the middle value of the ordered data, not the smallest."),
              (data[n // 2 - 1] if n % 2 == 0 else data[n // 2 + 1], "Average the two middle values when the count is even." if n % 2 == 0 else "Order the data first; the middle is the {0} value.".format(_ordinal(n // 2 + 1)))]
        return _numeric_mc(rng, prompt, val, ds, subskill="mean_median_mode", explanation=expl,
                           tags=["statistics", "median"], est=75, verify=f"median={num_str(val)}")
    if mode == "mode":
        m = rng.randint(3, 20)
        others = rng.sample([x for x in range(2, 30) if x != m], n - 3)
        data = [m, m, m] + others
        rng.shuffle(data)
        shown = ", ".join(map(str, data))
        prompt = rng.choice([f"What is the mode of the data set {shown}?",
                             f"The shoe sizes of {n} players are {shown}. What is the mode of the sizes?"])
        expl = f"The value {m} appears three times, more than any other value, so it is the mode."
        ds = [(max(data), "This is the greatest value, not the most frequent."),
              (Fraction(sum(data), n), "This is the mean, not the mode."),
              (min(data), "This is the least value, not the most frequent."),
              (sorted(data)[n // 2], "This is the median, not the mode.")]
        return _numeric_mc(rng, prompt, m, ds, subskill="mean_median_mode", explanation=expl,
                           tags=["statistics", "mode"], est=70, verify=f"mode={m}")
    # hard: skewed data with an outlier — compare mean and median
    data = sorted(_data_list(rng, n - 1, 10, 30)) + [rng.randint(80, 150)]
    s = sum(data)
    med = data[n // 2]
    mean = Fraction(s, n)
    shown = ", ".join(map(str, rng.sample(data, len(data))))
    prompt = (f"The data set {shown} lists the number of minutes {n} customers waited. "
              f"Which of the following is true about the mean and the median of the data?")
    correct = f"The mean is greater than the median, because the value {data[-1]} pulls the mean up."
    ds = [(f"The median is greater than the mean, because the value {data[-1]} pulls the median up.",
           "The median is resistant to outliers; it is the middle value, {0}.".format(med)),
          ("The mean and the median are equal, because the data are symmetric.",
           f"The mean is {float(mean):.1f} and the median is {med}; they differ."),
          (f"The mean is less than the median, because most values are below {data[-1]}.",
           "A large outlier raises the mean above the median."),
          ("The median cannot be determined without the mode.",
           "The median is simply the middle value of the ordered data.")]
    expl = f"Median = {med} (middle value); mean = {s}/{n} ≈ {float(mean):.1f}. The outlier {data[-1]} raises the mean."
    return _text_mc(rng, prompt, correct, ds, subskill="mean_median_mode", explanation=expl,
                    tags=["statistics", "outlier"], est=95, verify=f"mean={float(mean):.2f} median={med}")


def st_spread(rng, d):
    """Range (easy); compare standard deviations (medium/hard)."""
    if d == "easy":
        n = rng.choice([5, 6, 7])
        data = _data_list(rng, n, 2, 45)
        shown = ", ".join(map(str, data))
        val = max(data) - min(data)
        prompt = rng.choice([f"What is the range of the data set {shown}?",
                             f"The scores on a quiz were {shown}. What is the range of the scores?"])
        expl = f"Range = greatest − least = {max(data)} − {min(data)} = {val}."
        ds = [(max(data), "This is the greatest value, not the range."),
              (Fraction(sum(data), n), "This is the mean, not the range."),
              (sorted(data)[n // 2], "This is the median, not the range."),
              (max(data) + min(data), "Subtract the least from the greatest; don't add.")]
        return _numeric_mc(rng, prompt, val, ds, subskill="spread", explanation=expl,
                           tags=["statistics", "range"], est=65, verify=f"range={val}")
    center = rng.randint(20, 60)
    tight = sorted(center + rng.choice([-2, -1, 0, 1, 2]) for _ in range(6))
    wide = sorted(center + rng.choice([-15, -10, -6, 6, 10, 15]) for _ in range(6))
    if d == "medium":
        a, b = ("A", tight), ("B", wide)
        if rng.random() < 0.5:
            a, b = b, a
        prompt = (f"Data set {a[0]}: {', '.join(map(str, a[1]))}\nData set {b[0]}: "
                  f"{', '.join(map(str, b[1]))}\nWhich statement about the standard deviations "
                  f"of the two data sets is true?")
        wide_name = "A" if a[1] is wide else "B"
        tight_name = "B" if wide_name == "A" else "A"
        correct = f"The standard deviation of data set {wide_name} is greater than that of data set {tight_name}."
        ds = [(f"The standard deviation of data set {tight_name} is greater than that of data set {wide_name}.",
               f"Set {tight_name}'s values cluster tightly around {center}; set {wide_name}'s are spread out."),
              ("The two data sets have the same standard deviation.", "The spreads clearly differ."),
              (f"The standard deviation of data set {tight_name} is greater because its values are larger.",
               "Standard deviation measures spread, not size."),
              ("The standard deviations cannot be compared without computing the medians.",
               "Spread can be judged from how far values sit from the center.")]
        expl = f"Set {wide_name}'s values are far from the center; set {tight_name}'s are within 2 of it. Larger spread means larger standard deviation."
        return _text_mc(rng, prompt, correct, ds, subskill="spread", explanation=expl,
                        tags=["statistics", "standard-deviation"], est=80, verify=f"wide={wide_name}")
    # hard: effect of adding/removing a value on mean / SD
    data = sorted(_data_list(rng, 6, 10, 40))
    s = sum(data)
    mean = Fraction(s, 6)
    outlier = max(data) + rng.randint(20, 40)
    new_mean = Fraction(s + outlier, 7)
    prompt = (f"A data set has the values {', '.join(map(str, data))}. If the value {outlier} is "
              f"added to the data set, which of the following describes the effect on the mean "
              f"and the standard deviation?")
    correct = "Both the mean and the standard deviation increase."
    ds = [("The mean increases and the standard deviation decreases.", "A value far from the others increases the spread."),
          ("The mean decreases and the standard deviation increases.", f"{outlier} is above the current mean {float(mean):.1f}, so the mean rises."),
          ("The mean increases and the standard deviation is unchanged.", "Adding a distant value changes the spread."),
          ("Neither the mean nor the standard deviation changes.", "Adding a value far from the center changes both.")]
    expl = (f"The mean rises from {float(mean):.1f} to {float(new_mean):.1f} because {outlier} is above it, "
            f"and the added value is far from the center, so the spread (standard deviation) grows.")
    return _text_mc(rng, prompt, correct, ds, subskill="spread", explanation=expl,
                    tags=["statistics", "standard-deviation", "outlier"], est=90,
                    verify=f"mean {float(mean):.2f}->{float(new_mean):.2f}")


def st_missing_value(rng, d):
    """Find a missing value from a known mean (hard: after a change / weighted)."""
    if d == "easy":
        n = 4
        target = rng.randint(5, 20)
        three = [rng.randint(2, 30) for _ in range(3)]
        missing = target * n - sum(three)
        if not 1 <= missing <= 40:
            return st_missing_value(rng, d)
        prompt = f"The mean of four numbers is {target}. Three of the numbers are {', '.join(map(str, three))}. What is the fourth number?"
        val = missing
        expl = f"The four numbers total {target}×4 = {target * n}; {target * n} − {sum(three)} = {missing}."
        ds = [(target, "That is the mean itself, not the missing number."),
              (sum(three), "That is the sum of the three known numbers."),
              (target * n, "That is the total of all four; subtract the three shown."),
              (Fraction(sum(three), 3), "The mean of the three shown isn't the missing value.")]
    elif d == "medium":
        n = rng.choice([5, 6])
        target = rng.randint(8, 25)
        known = [rng.randint(2, 40) for _ in range(n - 1)]
        missing = target * n - sum(known)
        if not 1 <= missing <= 60:
            return st_missing_value(rng, d)
        name = rng.choice(NAMES)
        prompt = (f"{name}'s scores on the first {n - 1} quizzes were {', '.join(map(str, known))}. "
                  f"What score does {name} need on the {_ordinal(n)} quiz for the mean of all "
                  f"{n} scores to be exactly {target}?")
        val = missing
        expl = f"Required total = {target} × {n} = {target * n}; {target * n} − {sum(known)} = {missing}."
        ds = [(target, "The missing score must balance the others; it isn't simply the target mean."),
              (target * (n - 1) - sum(known) + target, "Use {0} scores in the total, not {1}.".format(n, n - 1)) if target * (n - 1) - sum(known) + target != missing else (missing + 3, "Arithmetic slip."),
              (target * n, "That is the required total, not the last score."),
              (missing - target + Fraction(sum(known), n - 1), "Recompute: total needed minus total so far.")]
    else:
        n1, n2 = rng.randint(10, 30), rng.randint(10, 30)
        m1, m2 = rng.randint(60, 90), rng.randint(60, 90)
        if m1 == m2:
            m2 += 3
        val = Fraction(n1 * m1 + n2 * m2, n1 + n2)
        prompt = (f"In one class of {n1} students the mean test score was {m1}, and in another "
                  f"class of {n2} students the mean was {m2}. What is the mean score of all "
                  f"{n1 + n2} students? (Round to the nearest tenth.)")
        expl = (f"Total points = {n1}·{m1} + {n2}·{m2} = {n1 * m1 + n2 * m2}; divide by {n1 + n2}: "
                f"{float(val):.1f}.")
        valr = round(float(val), 1)
        ds = [(round((m1 + m2) / 2, 1), "Averaging the two means ignores the different class sizes."),
              (round(float(val) + (m2 - m1) / 4, 1), "Weight each mean by its class size."),
              (round(float(val) + 1.5, 1), "Arithmetic slip; recompute the weighted total."),
              (max(m1, m2), "The combined mean lies between the two means.")]
        return _numeric_mc(rng, prompt, valr, ds, subskill="mean_median_mode", explanation=expl,
                           tags=["statistics", "weighted-mean"], est=100, qtype="multi_step_math",
                           verify=f"({n1}*{m1}+{n2}*{m2})/{n1 + n2}={float(val):.2f}")
    return _numeric_mc(rng, prompt, val, ds, subskill="mean_median_mode", explanation=expl,
                       tags=["statistics", "mean"], est=90, verify=f"missing={val}")


def st_frequency_table(rng, d):
    """Mean/median/mode from a frequency table (data_interpretation)."""
    ctx = rng.choice([("Number of pets", "Number of students", "pets per student"),
                      ("Goals scored", "Number of games", "goals per game"),
                      ("Books read", "Number of readers", "books per reader"),
                      ("Siblings", "Number of children", "siblings per child")])
    k = 4 if d == "easy" else 5
    values = list(range(0, k)) if rng.random() < 0.5 else list(range(1, k + 1))
    freqs = [rng.randint(1, 9) for _ in values]
    N = sum(freqs)
    stim = _table("Survey results", [ctx[0], ctx[1]], [[v, f] for v, f in zip(values, freqs)])
    expanded = [v for v, f in zip(values, freqs) for _ in range(f)]
    if d == "easy":
        mode_f = max(freqs)
        if freqs.count(mode_f) > 1:
            return st_frequency_table(rng, d)
        if rng.random() < 0.5:
            val = values[freqs.index(mode_f)]
            prompt = f"The table shows the results of a survey of {N} people. What is the mode of the data?"
            expl = f"The mode is the value with the greatest frequency: {val} (frequency {mode_f})."
            ds = [(mode_f, "That is the frequency, not the value that occurs most."),
                  (N, "That is the number of people surveyed."),
                  (max(values), "The mode is the most frequent value, not the largest."),
                  (values[freqs.index(min(freqs))], "That value occurs least often.")]
        else:
            val = N
            prompt = "The table summarizes survey responses. How many people were surveyed in total?"
            expl = f"Add the frequencies: {' + '.join(map(str, freqs))} = {N}."
            ds = [(sum(values), "Add the frequencies, not the values."),
                  (sum(v * f for v, f in zip(values, freqs)), "That is the total of all responses' values, not the number of people."),
                  (max(freqs), "That is one frequency, not the total."),
                  (N + 1, "Arithmetic slip; recheck the sum.")]
    elif d == "medium":
        val = expanded[N // 2] if N % 2 else Fraction(expanded[N // 2 - 1] + expanded[N // 2], 2)
        prompt = f"The table shows the results of a survey of {N} people. What is the median of the data?"
        expl = (f"List the {N} responses in order using the frequencies; the middle "
                f"{'value is' if N % 2 else 'two values average to'} {num_str(val)}.")
        ds = [(values[len(values) // 2], "The median is the middle of the {0} responses, not the middle listed value.".format(N)),
              (values[freqs.index(max(freqs))] if values[freqs.index(max(freqs))] != val else max(values), "That is the mode, not the median."),
              (Fraction(sum(v * f for v, f in zip(values, freqs)), N), "That is the mean, not the median."),
              (Fraction(N, 2), "That is the position of the middle, not its value.")]
    else:
        total_val = sum(v * f for v, f in zip(values, freqs))
        val = Fraction(total_val, N)
        prompt = f"The table shows the results of a survey of {N} people. What is the mean {ctx[2]}? (Round to the nearest hundredth if necessary.)"
        expl = f"Mean = Σ(value × frequency)/N = {total_val}/{N} ≈ {float(val):.2f}."
        valr = round(float(val), 2)
        ds = [(round(sum(values) / len(values), 2), "Weight each value by its frequency; don't average the listed values."),
              (round(total_val / len(values), 2), "Divide by the number of people, not the number of rows."),
              (round(N / len(values), 2), "That is the mean frequency, not the mean value."),
              (round(valr + 0.5, 2), "Arithmetic slip; recompute Σ(value × frequency).")]
        return _numeric_mc(rng, prompt, valr, ds, subskill="mean_median_mode", explanation=expl,
                           qtype="data_interpretation", tags=["statistics", "table", "mean"],
                           est=100, stimulus=stim, verify=f"{total_val}/{N}")
    return _numeric_mc(rng, prompt, val, ds, subskill="mean_median_mode", explanation=expl,
                       qtype="data_interpretation", tags=["statistics", "table"], est=80,
                       stimulus=stim, verify=f"val={num_str(val)}")


def st_change_effect(rng, d):
    """Effect of adding/removing a value on the mean/median."""
    n = 5 if d != "hard" else 6
    data = sorted(_data_list(rng, n, 4, 40))
    data[-1] += (n - sum(data) % n) % n
    s = sum(data)
    if d == "easy":
        add = rng.randint(1, 10)
        prompt = (f"The mean of the data set {', '.join(map(str, data))} is {num_str(Fraction(s, n))}. "
                  f"If {add} is added to every value, what is the new mean?")
        val = Fraction(s, n) + add
        expl = f"Adding {add} to every value adds {add} to the mean: {num_str(Fraction(s, n))} + {add} = {num_str(val)}."
        ds = [(Fraction(s, n), "The mean shifts by the same amount as the data."),
              (Fraction(s, n) + Fraction(add, n), "Every value increases by {0}, so the mean does too (not by {0}/{1}).".format(add, n)),
              (Fraction(s, n) * add, "The values are shifted, not multiplied."),
              (Fraction(s + add, n), "{0} is added to each value, not just once to the total.".format(add))]
    elif d == "medium":
        new = rng.randint(41, 80)
        val = Fraction(s + new, n + 1)
        prompt = (f"A data set consists of {', '.join(map(str, data))}. If the value {new} is added "
                  f"to the set, what is the mean of the new data set?")
        expl = f"New total = {s} + {new} = {s + new}; new count = {n + 1}; mean = {num_str(val)}."
        ds = [(Fraction(s + new, n), "The count increases to {0} as well.".format(n + 1)),
              (Fraction(s, n), "That is the old mean."),
              (Fraction(s, n) + Fraction(new, n), "Divide the new total by the new count."),
              (new, "The mean is not the added value.")]
    else:
        rem = rng.choice([data[0], data[-1]])
        rest = list(data)
        rest.remove(rem)
        val = Fraction(sum(rest), n - 1)
        which = "least" if rem == data[0] else "greatest"
        prompt = (f"The data set {', '.join(map(str, data))} has mean {num_str(Fraction(s, n))}. "
                  f"If the {which} value is removed, what is the mean of the remaining values?")
        expl = f"Remove {rem}: new total {s} − {rem} = {sum(rest)}, over {n - 1} values: {num_str(val)}."
        ds = [(Fraction(s - rem, n), "Divide by the new count, {0}.".format(n - 1)),
              (Fraction(s, n), "Removing an extreme value changes the mean."),
              (Fraction(s, n - 1), "Subtract the removed value from the total as well."),
              (Fraction(sum(rest), n - 1) + (1 if which == "least" else -1), "Arithmetic slip; recompute the new total.")]
    fmt = lambda v: num_str(round(float(v), 2)) if isinstance(v, Fraction) and v.denominator not in (1, 2, 4, 5, 10) else num_str(v)
    return _numeric_mc(rng, prompt, val, ds, subskill="mean_median_mode", explanation=expl,
                       tags=["statistics", "mean", "change"], est=85, fmt=fmt,
                       verify=f"val={num_str(val)}")


def st_gridin(rng, d):
    """Grid-in: mean/median/missing value."""
    if d == "easy":
        data = _data_list(rng, 5, 2, 25)
        s = sum(data)
        data[-1] += (5 - s % 5) % 5
        s = sum(data)
        prompt = f"What is the mean of the data set {', '.join(map(str, data))}?"
        val = s // 5
        expl = f"{s} ÷ 5 = {val}."
    elif d == "medium":
        data = sorted(_data_list(rng, 6, 3, 40))
        prompt = f"What is the median of the data set {', '.join(map(str, rng.sample(data, 6)))}?"
        val = Fraction(data[2] + data[3], 2)
        expl = f"Ordered: {', '.join(map(str, data))}; the median is the average of {data[2]} and {data[3]}: {num_str(val)}."
    else:
        n = rng.choice([5, 6, 7])
        target = rng.randint(8, 25)
        known = [rng.randint(2, 40) for _ in range(n - 1)]
        val = target * n - sum(known)
        if not 1 <= val <= 60:
            return st_gridin(rng, d)
        prompt = f"The mean of {n} numbers is {target}. If {n - 1} of the numbers are {', '.join(map(str, known))}, what is the remaining number?"
        expl = f"{target} × {n} − {sum(known)} = {val}."
    return _spr_num(prompt, val, subskill="mean_median_mode", explanation=expl,
                    tags=["statistics", "grid-in"], est=80, verify=f"val={num_str(val)}")


st_gridin.sat_only = True


# --------------------------------------------------------------------------- #
# probability
# --------------------------------------------------------------------------- #
def _bag(rng):
    colors = rng.sample(["red", "blue", "green", "yellow", "white", "black", "orange", "purple"], 3)
    counts = {c: rng.randint(2, 14) for c in colors}
    thing = rng.choice(["marbles", "tokens", "balls", "beads", "chips"])
    text = (f"A bag contains {counts[colors[0]]} {colors[0]}, {counts[colors[1]]} {colors[1]}, and "
            f"{counts[colors[2]]} {colors[2]} {thing}.")
    return colors, counts, thing, text


def pb_single(rng, d):
    """Single-draw probability (easy); complement / union (medium); percent-based (hard)."""
    colors, counts, thing, bag = _bag(rng)
    total = sum(counts.values())
    if d == "easy":
        c = rng.choice(colors)
        val = Fraction(counts[c], total)
        prompt = f"{bag} If one of the {thing} is chosen at random, what is the probability that it is {c}?"
        expl = f"{counts[c]} of the {total} {thing} are {c}: {counts[c]}/{total} = {num_str(val)}."
        ds = [(Fraction(counts[c], total - counts[c]), "Use the total count in the denominator, not the rest."),
              (Fraction(total - counts[c], total), "This is the probability of NOT drawing that colour."),
              (Fraction(counts[c] + 1, total), "Recount the favourable outcomes."),
              (Fraction(1, 3), "The colours are not equally likely; use the counts.")]
    elif d == "medium":
        if rng.random() < 0.5:
            c = rng.choice(colors)
            val = Fraction(total - counts[c], total)
            prompt = f"{bag} If one of the {thing} is selected at random, what is the probability that it is not {c}?"
            expl = f"P(not {c}) = 1 − {counts[c]}/{total} = {num_str(val)}."
            ds = [(Fraction(counts[c], total), f"This is the probability of drawing {c}."),
                  (Fraction(total - counts[c], counts[c]), "Keep the total in the denominator."),
                  (Fraction(counts[c], total - counts[c]), "Compare favourable to total, not to the rest."),
                  (Fraction(2, 3), "The colours are not equally likely.")]
        else:
            c1, c2 = rng.sample(colors, 2)
            k = counts[c1] + counts[c2]
            val = Fraction(k, total)
            prompt = f"{bag} If one of the {thing} is selected at random, what is the probability that it is {c1} or {c2}?"
            expl = f"P({c1} or {c2}) = ({counts[c1]} + {counts[c2]})/{total} = {num_str(val)}."
            ds = [(Fraction(counts[c1], total), f"This counts only the {c1} {thing}."),
                  (Fraction(total - k, total), "This is the probability of the third colour."),
                  (Fraction(counts[c1], total) * Fraction(counts[c2], total), "'Or' with disjoint outcomes adds probabilities; it doesn't multiply."),
                  (Fraction(k, total - k), "Use the total in the denominator.")]
    else:
        pct_a = rng.choice(range(12, 60, 2))
        pct_b = rng.choice(range(10, 42, 2))
        both = rng.choice([v for v in (2, 4, 5, 6, 8, 10, 12, 15) if v < min(pct_a, pct_b)])
        if both >= min(pct_a, pct_b):
            both = 5
        either = pct_a + pct_b - both
        prompt = (f"In a survey, {pct_a}% of respondents own a bicycle, {pct_b}% own a scooter, and "
                  f"{both}% own both. If a respondent is selected at random, what is the probability "
                  f"that the respondent owns a bicycle or a scooter (or both)?")
        val = Fraction(either, 100)
        expl = f"P(A or B) = P(A) + P(B) − P(A and B) = ({pct_a} + {pct_b} − {both})/100 = {num_str(val)}."
        ds = [(Fraction(pct_a + pct_b, 100), "Subtract the overlap; it was counted twice."),
              (Fraction(pct_a + pct_b + both, 100), "The overlap is subtracted, not added."),
              (Fraction(both, 100), "That is P(both), not P(either)."),
              (Fraction(pct_a * pct_b, 10000), "Multiplying is for independent 'and', not for 'or'.")]
    return _numeric_mc(rng, prompt, val, ds, subskill="simple_probability", explanation=expl,
                       tags=["probability"], est=75 if d == "easy" else 90, verify=f"P={num_str(val)}")


def pb_compound(rng, d):
    """Two events: independent 'and' (medium), without replacement (hard), easy: equally likely outcomes."""
    if d == "easy":
        kind = rng.choice(["die", "spinner", "cards"])
        if kind == "die":
            k = rng.choice([1, 2, 3, 4])
            ev = rng.choice([("an even number", 3), ("a number greater than 4", 2), ("a number less than 3", 2),
                             ("a multiple of 3", 2), ("a number greater than 1", 5), ("a prime number", 3)])
            val = Fraction(ev[1], 6)
            prompt = f"A fair six-sided die is rolled once. What is the probability of rolling {ev[0]}?"
            expl = f"{ev[1]} of the 6 equally likely outcomes satisfy the condition: {ev[1]}/6 = {num_str(val)}."
            ds = [(Fraction(ev[1], 5), "The die has 6 outcomes, not 5."),
                  (Fraction(6 - ev[1], 6), "That is the probability of the complement."),
                  (Fraction(ev[1] + 1, 6), "Recount the favourable outcomes."),
                  (Fraction(1, 6), "More than one outcome satisfies the condition.")]
        elif kind == "spinner":
            n = rng.randint(5, 12)
            k = rng.randint(1, n - 1)
            val = Fraction(k, n)
            prompt = f"A spinner has {n} equal sections numbered 1 through {n}. What is the probability that the spinner lands on a number less than or equal to {k}?"
            expl = f"{k} of the {n} equal sections qualify: {k}/{n} = {num_str(val)}."
            ds = [(Fraction(k - 1, n), "'Less than or equal to' includes {0} itself.".format(k)),
                  (Fraction(n - k, n), "That is the probability of a number greater than {0}.".format(k)),
                  (Fraction(k, n - 1), "The spinner has {0} sections.".format(n)),
                  (Fraction(k + 1, n), "Recount the sections from 1 to {0}.".format(k))]
        else:
            n = rng.randint(10, 30)
            k = rng.randint(2, n - 2)
            val = Fraction(k, n)
            prompt = f"A jar holds {n} tickets numbered 1 through {n}. If one ticket is drawn at random, what is the probability its number is at most {k}?"
            expl = f"{k} of the {n} tickets have numbers from 1 to {k}: {k}/{n} = {num_str(val)}."
            ds = [(Fraction(n - k, n), "That is the probability of a number greater than {0}.".format(k)),
                  (Fraction(k - 1, n), "'At most {0}' includes {0}.".format(k)),
                  (Fraction(k, n - 1), "There are {0} tickets in all.".format(n)),
                  (Fraction(k + 1, n), "Recount: the numbers 1 through {0}.".format(k))]
        return _numeric_mc(rng, prompt, val, ds, subskill="simple_probability", explanation=expl,
                           tags=["probability"], est=70, verify=f"P={num_str(val)}")
    if d == "medium":
        p1 = rng.choice([Fraction(1, 2), Fraction(1, 3), Fraction(1, 4), Fraction(2, 3), Fraction(3, 4), Fraction(1, 6), Fraction(1, 5), Fraction(2, 5)])
        p2 = rng.choice([Fraction(1, 2), Fraction(1, 3), Fraction(1, 4), Fraction(2, 3), Fraction(3, 5), Fraction(1, 6), Fraction(3, 4)])
        ctx = rng.choice([("a coin lands heads", "a die shows a 6") if (p1, p2) == (Fraction(1, 2), Fraction(1, 6)) else None,
                          ("the first spinner lands on red", "the second spinner lands on blue"),
                          ("it rains on Saturday", "it rains on Sunday"),
                          ("the first machine passes inspection", "the second machine passes inspection")])
        if ctx is None:
            ctx = ("the first spinner lands on red", "the second spinner lands on blue")
        val = p1 * p2
        prompt = (f"Two events are independent. The probability that {ctx[0]} is {num_str(p1)}, and the "
                  f"probability that {ctx[1]} is {num_str(p2)}. What is the probability that both events occur?")
        expl = f"For independent events, P(both) = {num_str(p1)} × {num_str(p2)} = {num_str(val)}."
        ds = [(p1 + p2 if p1 + p2 < 1 else p1 + p2 - 1 + Fraction(1, 12), "'Both' means multiply the probabilities, not add."),
              (p1 + p2 - p1 * p2, "That is P(at least one), not P(both)."),
              (Fraction(p1.numerator + p2.numerator, p1.denominator + p2.denominator), "Multiply numerators and denominators separately."),
              (max(p1, p2), "Both must happen, so the probability is less than either alone.")]
        return _numeric_mc(rng, prompt, val, ds, subskill="simple_probability", explanation=expl,
                           tags=["probability", "independent"], est=85, verify=f"P={num_str(val)}")
    colors, counts, thing, bag = _bag(rng)
    total = sum(counts.values())
    if rng.random() < 0.5:
        c = rng.choice(colors)
        k = counts[c]
        val = Fraction(k * (k - 1), total * (total - 1))
        prompt = f"{bag} Two {thing} are drawn at random without replacement. What is the probability that both are {c}?"
        expl = f"P(both {c}) = {k}/{total} × {k - 1}/{total - 1} = {num_str(val)}."
        ds = [(Fraction(k, total) ** 2, "Without replacement, the second draw has one fewer {0} and one fewer total.".format(c)),
              (Fraction(k, total), "This is the probability for a single draw."),
              (Fraction(k * (k - 1), total * total), "Reduce the total by one on the second draw as well."),
              (Fraction(2 * k, total), "Two draws of the same colour multiply, not add.")]
    else:
        c1, c2 = rng.sample(colors, 2)
        val = Fraction(counts[c1] * counts[c2], total * (total - 1))
        prompt = (f"{bag} Two {thing} are drawn at random without replacement. What is the probability "
                  f"that the first is {c1} and the second is {c2}?")
        expl = f"P = {counts[c1]}/{total} × {counts[c2]}/{total - 1} = {num_str(val)}."
        ds = [(Fraction(counts[c1] * counts[c2], total * total), "The second draw is from {0} {1}, not {2}.".format(total - 1, thing, total)),
              (Fraction(counts[c1] + counts[c2], total), "'And' for two draws multiplies; it doesn't add."),
              (Fraction(counts[c1] * (counts[c2] - 1), total * (total - 1)), "The {0} count doesn't drop after drawing a {1}.".format(c2, c1)),
              (Fraction(counts[c1], total), "That is only the first draw.")]
    return _numeric_mc(rng, prompt, val, ds, subskill="simple_probability", explanation=expl,
                       tags=["probability", "without-replacement"], est=100, verify=f"P={num_str(val)}")


def pb_expected(rng, d):
    """Expected counts / probability from percents and sample sizes."""
    if d == "easy":
        n = rng.choice([50, 100, 150, 200, 250, 300, 400, 500, 600, 750, 800, 1000, 1200, 1500, 2000])
        pct = rng.choice([4, 5, 6, 8, 10, 12, 15, 18, 20, 22, 25, 30, 35, 40, 45, 60, 65, 75, 80])
        val = n * pct // 100
        prompt = (f"A survey found that {pct}% of a town's residents use public transit. If {n} "
                  f"residents are selected at random, about how many would be expected to use "
                  f"public transit?")
        expl = f"Expected count = probability × sample size = {pct}/100 × {n} = {val}."
        ds = [(n - val, "That is the expected number who do NOT use transit."),
              (pct, "Multiply the percent by the sample size."),
              (n * pct, "Divide by 100 when using a percent."),
              (val + 10, "Arithmetic slip; recompute the percent of {0}.".format(n))]
    elif d == "medium":
        num, den = rng.choice([(1, 4), (3, 8), (2, 5), (3, 10), (1, 6), (5, 12), (2, 3), (3, 5), (7, 20), (1, 8)])
        k = rng.randint(5, 40)
        n = den * k
        val = num * k
        prompt = (f"The probability that a randomly chosen part from a production line is defective "
                  f"is {num}/{den}. If {n} parts are produced, how many are expected to be defective?")
        expl = f"{num}/{den} × {n} = {val}."
        ds = [(n - val, "That is the expected number of good parts."),
              (Fraction(n, num) if n % num == 0 else n // num + 1, "Multiply by the probability, not by its reciprocal."),
              (den * k - k if den * k - k != val else val + k, "Multiply {0} by the numerator {1}.".format(k, num)),
              (val + k, "Arithmetic slip; recompute {0}/{1} of {2}.".format(num, den, n))]
    else:
        n = rng.choice([200, 300, 400, 500, 600, 800])
        k = rng.randint(3, 12) * (n // 100)
        p = Fraction(k, n)
        m = rng.choice([1000, 1500, 2000, 2500, 3000, 5000])
        val = p * m
        prompt = (f"In a random sample of {n} light bulbs from a factory, {k} were defective. Based on "
                  f"the sample, approximately how many defective bulbs would be expected in a shipment "
                  f"of {m} bulbs?")
        expl = f"Sample rate = {k}/{n} = {num_str(p)}; × {m} = {num_str(val)}."
        ds = [(Fraction(n, k) * 100 if (Fraction(n, k) * 100).denominator == 1 else val * 2, "Use the fraction defective (k/n), not n/k."),
              (k, "That is the number defective in the sample, not the shipment."),
              (Fraction(k * m, 100), "Divide by the sample size {0}, not by 100.".format(n)),
              (val + m // 100, "Arithmetic slip; recompute k/n × {0}.".format(m))]
    return _numeric_mc(rng, prompt, val, ds, subskill="simple_probability", explanation=expl,
                       tags=["probability", "expected"], est=80, verify=f"val={num_str(val)}")


def pb_table(rng, d):
    """Probability from a two-way table (data_interpretation)."""
    rcat = rng.choice([("Freshmen", "Sophomores"), ("Morning", "Afternoon"), ("Online", "In store"), ("Adults", "Children")])
    ccat = rng.choice([("Yes", "No"), ("Passed", "Failed"), ("Prefers tea", "Prefers coffee"), ("Member", "Non-member")])
    a, b, c, e = (rng.randint(5, 45) for _ in range(4))
    total = a + b + c + e
    rows = [[rcat[0], a, b, a + b], [rcat[1], c, e, c + e], ["Total", a + c, b + e, total]]
    stim = _table("Survey results", ["", ccat[0], ccat[1], "Total"], rows)
    if d == "easy":
        val = Fraction(a + b, total)
        prompt = f"The table summarizes {total} responses. If one response is chosen at random, what is the probability that it is from the {rcat[0]} group?"
        expl = f"The {rcat[0]} row totals {a + b} of {total}: {num_str(val)}."
        ds = [(Fraction(a, total), f"That uses only one cell ({a}), not the whole row."),
              (Fraction(c + e, total), f"That is the probability of the {rcat[1]} row."),
              (Fraction(a + b, c + e), "Divide by the grand total, not the other row."),
              (Fraction(a + c, total), f"That is the probability of the {ccat[0]} column.")]
    elif d == "medium":
        val = Fraction(a, total)
        prompt = f"The table summarizes {total} responses. If one response is selected at random, what is the probability that it is from the {rcat[0]} group and in the {ccat[0]} category?"
        expl = f"The single cell holds {a} of the {total} responses: {num_str(val)}."
        ds = [(Fraction(a, a + b), "This conditions on the row instead of using the grand total."),
              (Fraction(a, a + c), "This conditions on the column instead of the grand total."),
              (Fraction(a + b, total), "That is the whole row, not the single cell."),
              (Fraction(a + b + c, total), "'And' means the single cell, not the union.")]
    else:
        val = Fraction(a, a + c)
        prompt = f"The table summarizes {total} responses. If a response in the {ccat[0]} category is selected at random, what is the probability that it is from the {rcat[0]} group?"
        expl = f"Restrict to the {ccat[0]} column ({a + c} responses); {a} are {rcat[0]}: {num_str(val)}."
        ds = [(Fraction(a, total), "Condition on the column total, not the grand total."),
              (Fraction(a, a + b), "Condition on the column, not the row."),
              (Fraction(c, a + c), f"That is the probability of the {rcat[1]} group within the column."),
              (Fraction(a + c, total), "That is the probability of the column itself.")]
    return _numeric_mc(rng, prompt, val, ds, subskill="two_way_tables", explanation=expl,
                       qtype="data_interpretation", tags=["probability", "table"], est=90,
                       stimulus=stim, verify=f"P={num_str(val)}")


def pb_gridin(rng, d):
    """Grid-in probability (as a fraction or decimal)."""
    colors, counts, thing, bag = _bag(rng)
    total = sum(counts.values())
    if d == "easy":
        c = rng.choice(colors)
        val = Fraction(counts[c], total)
        prompt = f"{bag} If one of the {thing} is chosen at random, what is the probability that it is {c}?"
        expl = f"{counts[c]}/{total} = {num_str(val)}."
    elif d == "medium":
        c = rng.choice(colors)
        val = Fraction(total - counts[c], total)
        prompt = f"{bag} If one of the {thing} is chosen at random, what is the probability that it is not {c}?"
        expl = f"1 − {counts[c]}/{total} = {num_str(val)}."
    else:
        pct = rng.choice([4, 5, 8, 10, 12, 15, 16, 20, 24, 25, 30, 35, 40, 45, 60])
        n = rng.choice([40, 60, 80, 100, 120, 150, 200, 240, 250, 300, 400, 500])
        val = n * pct // 100
        if val * 100 != n * pct:
            n = 100 * rng.randint(1, 8)
            val = n * pct // 100
        prompt = f"The probability that a randomly selected customer uses a coupon is {pct}%. Of {n} customers, how many are expected to use a coupon?"
        expl = f"{pct}/100 × {n} = {val}."
    return _spr_num(prompt, val, subskill="simple_probability", explanation=expl,
                    tags=["probability", "grid-in"], est=80, verify=f"val={num_str(val)}")


pb_gridin.sat_only = True


# --------------------------------------------------------------------------- #
# area_volume
# --------------------------------------------------------------------------- #
def _rect_fig(w, h, caption="Rectangle"):
    return {"type": "figure", "figure": {"kind": "rect", "caption": caption,
                                         "labels": {"w": str(w), "h": str(h)}}}


def av_rect_tri(rng, d):
    """Area of a rectangle (easy) / triangle (medium) / trapezoid or parallelogram (hard)."""
    b, h = rng.randint(3, 20), rng.randint(3, 20)
    if d == "easy":
        val = b * h
        prompt = rng.choice([f"The rectangle shown has a width of {b} and a height of {h}. What is its area?",
                             f"A rectangular garden is {b} meters by {h} meters. What is its area, in square meters?"])
        expl = f"Area of a rectangle = width × height = {b} × {h} = {val}."
        fig = _rect_fig(b, h)
        ds = [(2 * (b + h), "This is the perimeter, not the area."),
              (b * h // 2, "Halving applies to triangles, not rectangles."),
              (b + h, "This adds the sides instead of multiplying."),
              (b * b, "Use both dimensions; the figure is not a square.") if b != h else (b * h + b, "Arithmetic slip.")]
        sub = "area"
    elif d == "medium":
        if b % 2 and h % 2:
            b += 1
        val = b * h // 2
        prompt = rng.choice([f"The right triangle shown has legs of length {b} and {h}. What is its area?",
                             f"A triangular sail has a base of {b} feet and a height of {h} feet. What is its area, in square feet?"])
        expl = f"Area of a triangle = ½ × base × height = ½ × {b} × {h} = {val}."
        fig = _tri_fig(b, h, "", caption="Triangle")
        ds = [(b * h, "You forgot the factor of ½."),
              (b + h, "This adds the dimensions instead of using the area formula."),
              ((b + h) // 2, "Average of the sides is not the area."),
              (b * h // 4, "Only one factor of ½ is used.")]
        sub = "area"
    else:
        kind = rng.choice(["trapezoid", "parallelogram"])
        if kind == "trapezoid":
            b2 = b + rng.randint(2, 10)
            if (b + b2) % 2:
                b2 += 1
            val = (b + b2) * h // 2
            prompt = f"A trapezoid has parallel sides of length {b} and {b2} and a height of {h}. What is its area?"
            expl = f"Area = ½(b₁ + b₂)h = ½({b} + {b2})·{h} = {val}."
            ds = [((b + b2) * h, "Average the two bases (multiply by ½)."),
                  (b * h, "Use both parallel sides."),
                  (b2 * h, "Use both parallel sides."),
                  (b * b2 * h // 2, "Add the bases; don't multiply them.")]
        else:
            s = rng.randint(h + 1, h + 9)
            val = b * h
            prompt = (f"A parallelogram has a base of {b}, a slanted side of length {s}, and a "
                      f"height of {h} measured perpendicular to the base. What is its area?")
            expl = f"Area of a parallelogram = base × height = {b} × {h} = {val} (the slanted side is not used)."
            ds = [(b * s, "Use the perpendicular height, not the slanted side."),
                  (b * h // 2, "The ½ is for triangles."),
                  (2 * (b + s), "That is the perimeter."),
                  (b * h + s, "Arithmetic slip.")]
        fig = None
        sub = "area"
    return _numeric_mc(rng, prompt, val, ds, subskill=sub, explanation=expl,
                       tags=["geometry", "area"], est=70 if d != "hard" else 85,
                       verify=f"area={val}", stimulus=fig)


def av_perimeter(rng, d):
    """Perimeter / side from area / dimension from perimeter."""
    if d == "easy":
        w, h = rng.randint(3, 25), rng.randint(3, 25)
        val = 2 * (w + h)
        prompt = rng.choice([f"A rectangle has a length of {w} and a width of {h}. What is its perimeter?",
                             f"The rectangle shown has width {w} and height {h}. What is the perimeter of the rectangle?"])
        expl = f"Perimeter = 2(length + width) = 2({w} + {h}) = {val}."
        ds = [(w * h, "That is the area, not the perimeter."),
              (w + h, "Count all four sides."),
              (2 * w + h, "Both widths and both lengths are counted."),
              (val + 2, "Arithmetic slip.")]
        fig = _rect_fig(w, h)
    elif d == "medium":
        s = rng.randint(3, 60)
        if rng.random() < 0.5:
            prompt = f"A square has an area of {s * s} square inches. What is its perimeter, in inches?"
            val = 4 * s
            expl = f"Side = √{s * s} = {s}; perimeter = 4 × {s} = {val}."
            ds = [(s, "That is the side length, not the perimeter."),
                  (2 * s, "A square has four equal sides."),
                  (s * s, "That is the area again."),
                  (4 * s * s, "Take the square root first.")]
        else:
            prompt = f"A square has a perimeter of {4 * s} centimeters. What is its area, in square centimeters?"
            val = s * s
            expl = f"Side = {4 * s} ÷ 4 = {s}; area = {s}² = {val}."
            ds = [(s, "That is the side length, not the area."),
                  (4 * s * 4 * s, "Divide the perimeter by 4 before squaring."),
                  (2 * s * s, "Area of a square is side², not 2·side²."),
                  (4 * s, "That is the perimeter again.")]
        fig = None
    else:
        w = rng.randint(3, 15)
        k = rng.randint(2, 4)
        h = k * w + rng.randint(0, 5)
        P = 2 * (w + h)
        prompt = (f"The length of a rectangle is {h - k * w} more than {k} times its width. If the "
                  f"perimeter of the rectangle is {P}, what is its width?") if h - k * w else \
                 (f"The length of a rectangle is {k} times its width. If the perimeter of the rectangle is {P}, what is its area?")
        if h - k * w:
            val = w
            expl = f"Let width = w, length = {k}w + {h - k * w}. 2(w + {k}w + {h - k * w}) = {P} → {2 * (k + 1)}w = {P - 2 * (h - k * w)} → w = {w}."
            ds = [(h, "That is the length, not the width."),
                  (w * h, "That is the area."),
                  (P // 4, "The sides are not equal; set up the equation."),
                  (w + 1, "Arithmetic slip; recheck the equation.")]
        else:
            val = w * h
            expl = f"2(w + {k}w) = {P} → {2 * (k + 1)}w = {P} → w = {w}, length = {h}; area = {w}·{h} = {val}."
            ds = [(w, "That is the width, not the area."),
                  (h, "That is the length, not the area."),
                  (P * P // 16, "The sides are not equal."),
                  (w * h + w, "Arithmetic slip.")]
        fig = None
    return _numeric_mc(rng, prompt, val, ds, subskill="area", explanation=expl,
                       tags=["geometry", "perimeter"], est=70 if d == "easy" else 90,
                       verify=f"val={val}", stimulus=fig)


def av_volume(rng, d):
    """Volume of a box (medium) / cylinder (hard); easy: cube."""
    if d == "easy":
        s = rng.randint(2, 40)
        val = s ** 3
        prompt = rng.choice([f"A cube has edges of length {s}. What is its volume?",
                             f"The box shown is a cube with edge length {s}. What is the volume of the cube?",
                             f"A storage cube measures {s} inches on each edge. What is its volume, in cubic inches?"])
        expl = f"Volume of a cube = edge³ = {s}³ = {val}."
        fig = {"type": "figure", "figure": {"kind": "box", "caption": "Cube",
               "labels": {"l": str(s), "w": str(s), "h": str(s)}}}
        ds = [(s * s, "That is the area of one face."),
              (6 * s * s, "That is the surface area."),
              (3 * s, "Multiply the three edges; don't add."),
              (12 * s, "That is the total edge length.")]
    elif d == "medium":
        l, w, h = rng.randint(2, 12), rng.randint(2, 12), rng.randint(2, 12)
        val = l * w * h
        prompt = rng.choice([f"The rectangular box shown has length {l}, width {w}, and height {h}. What is its volume?",
                             f"A shipping crate is {l} feet long, {w} feet wide, and {h} feet tall. What is its volume, in cubic feet?"])
        expl = f"Volume = length × width × height = {l} × {w} × {h} = {val}."
        fig = {"type": "figure", "figure": {"kind": "box", "caption": "Rectangular box",
               "labels": {"l": str(l), "w": str(w), "h": str(h)}}}
        ds = [(2 * (l * w + l * h + w * h), "This is the surface area, not the volume."),
              (l + w + h, "This adds the dimensions instead of multiplying."),
              (l * w, "This is only the area of the base."),
              (l * w * h + l, "Arithmetic slip.")]
    else:
        r, h = rng.randint(2, 9), rng.randint(3, 15)
        coef = r * r * h
        val = f"{coef}π"
        prompt = rng.choice([f"The cylinder shown has radius {r} and height {h}. What is its volume, in terms of π?",
                             f"A cylindrical tank has a radius of {r} meters and a height of {h} meters. What is its volume, in cubic meters, in terms of π?"])
        expl = f"Volume = πr²h = π·{r}²·{h} = {coef}π."
        fig = {"type": "figure", "figure": {"kind": "cylinder", "caption": "Cylinder",
               "labels": {"r": str(r), "h": str(h)}}}
        ds = _pi_distractors(coef, [
            (2 * r * h, "This uses r instead of r²; volume is πr²h."),
            (r * r, "This is the base area; multiply by the height too."),
            (r * h, "Volume is πr²h, not πrh."),
            (4 * r * r * h, "Use the radius, not the diameter.")])
        return _numeric_mc(rng, prompt, val, ds, subskill="volume", explanation=expl,
                           tags=["geometry", "volume"], fmt=str, est=90, verify=val, stimulus=fig)
    return _numeric_mc(rng, prompt, val, ds, subskill="volume", explanation=expl,
                       tags=["geometry", "volume"], est=75, verify=f"V={val}", stimulus=fig)


def av_composite(rng, d):
    """Composite / scaled figures and surface area."""
    if d == "easy":
        w, h = rng.randint(6, 20), rng.randint(6, 20)
        s = rng.randint(2, min(w, h) - 2)
        val = w * h - s * s
        prompt = (f"A rectangular sheet of paper {w} inches by {h} inches has a square of side "
                  f"{s} inches cut out of one corner. What is the area, in square inches, of the "
                  f"remaining paper?")
        expl = f"Rectangle area {w}×{h} = {w * h}; minus the square {s}² = {s * s}: {val}."
        ds = [(w * h, "Subtract the cut-out square."),
              (w * h - s, "The cut-out is a square with area s², not s."),
              (w * h - 4 * s, "Subtract the square's area, not its perimeter."),
              ((w - s) * (h - s), "Only one corner square is removed, not a strip on two sides.")]
    elif d == "medium":
        l, w, h = rng.randint(2, 10), rng.randint(2, 10), rng.randint(2, 10)
        val = 2 * (l * w + l * h + w * h)
        prompt = f"A closed rectangular box has dimensions {l} by {w} by {h}. What is its total surface area?"
        expl = f"Surface area = 2(lw + lh + wh) = 2({l * w} + {l * h} + {w * h}) = {val}."
        ds = [(l * w * h, "That is the volume."),
              (l * w + l * h + w * h, "Each pair of faces appears twice."),
              (4 * (l + w + h), "That is the total edge length."),
              (2 * (l * w + l * h), "Include the {0}×{1} faces too.".format(w, h))]
    else:
        k = rng.choice([2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 15, 20])
        kind = rng.choice(["area", "volume"])
        shape = rng.choice(["square", "circle", "triangle"]) if kind == "area" else rng.choice(["cube", "sphere", "cylinder"])
        if kind == "area":
            val = k * k
            prompt = (f"The side lengths of a {shape} are each multiplied by {k}. The area of the "
                      f"new {shape} is how many times the area of the original?") if shape != "circle" else \
                     f"The radius of a circle is multiplied by {k}. The area of the new circle is how many times the area of the original?"
            expl = f"Area depends on the square of the lengths, so it scales by {k}² = {val}."
            ds = [(k, "Area scales by the square of the length factor."),
                  (2 * k, "Scale factor squared, not doubled."),
                  (k ** 3, "The cube applies to volume, not area."),
                  (4 * k, "Area scales by k², i.e. {0}².".format(k))]
        else:
            val = k ** 3
            prompt = (f"Every dimension of a {shape} is multiplied by {k}. The volume of the new "
                      f"{shape} is how many times the volume of the original?")
            expl = f"Volume depends on the cube of the lengths, so it scales by {k}³ = {val}."
            ds = [(k * k, "The square applies to area; volume uses the cube."),
                  (k, "Volume scales by the cube of the length factor."),
                  (3 * k, "Scale factor cubed, not tripled."),
                  (k ** 3 + k, "Arithmetic slip.")]
    return _numeric_mc(rng, prompt, val, ds, subskill="area" if d != "medium" else "volume",
                       explanation=expl, tags=["geometry", "composite"], est=85, verify=f"val={val}")


def av_gridin(rng, d):
    """Grid-in area/volume."""
    if d == "easy":
        b, h = rng.randint(3, 25), rng.randint(3, 25)
        prompt = f"A rectangle has a length of {b} and a width of {h}. What is its area?"
        val = b * h
        expl = f"{b} × {h} = {val}."
    elif d == "medium":
        b, h = rng.randint(3, 25), rng.randint(3, 25)
        if b % 2 and h % 2:
            h += 1
        prompt = f"A triangle has a base of {b} and a height of {h}. What is its area?"
        val = b * h // 2
        expl = f"½ × {b} × {h} = {val}."
    else:
        l, w, h = rng.randint(2, 12), rng.randint(2, 12), rng.randint(2, 12)
        prompt = f"A rectangular box is {l} by {w} by {h}. If its volume is V, what is the value of V ÷ {l}?"
        val = w * h
        expl = f"V = {l}·{w}·{h} = {l * w * h}; V ÷ {l} = {val}."
    return _spr_num(prompt, val, subskill="area", explanation=expl,
                    tags=["geometry", "grid-in"], est=70, verify=f"val={val}")


av_gridin.sat_only = True


# --------------------------------------------------------------------------- #
# circles
# --------------------------------------------------------------------------- #
def _circ_fig(r=None, d=None, sector=None, caption="Circle"):
    labels = {}
    if r is not None:
        labels["r"] = str(r)
    if d is not None:
        labels["d"] = str(d)
    fig = {"kind": "circle", "caption": caption, "labels": labels}
    if sector:
        fig["sector"] = sector
        labels["angle"] = f"{sector}°"
    return {"type": "figure", "figure": fig}


def ci_basic(rng, d):
    """Diameter/circumference (easy), area (medium), from diameter (hard)."""
    r = rng.randint(2, 60)
    if d == "easy":
        if rng.random() < 0.5:
            val = 2 * r
            prompt = rng.choice([f"The circle shown has radius {r}. What is its diameter?",
                                 f"A circular pond has a radius of {r} feet. What is the diameter of the pond, in feet?"])
            expl = f"Diameter = 2 × radius = 2 × {r} = {val}."
            ds = [(r, "This is the radius, not the diameter."),
                  (r * r, "This squares the radius; diameter is 2r."),
                  (4 * r, "Diameter is 2r, not 4r."),
                  (r + 2, "Multiply by 2; don't add.")]
            return _numeric_mc(rng, prompt, val, ds, subskill="circumference_area", explanation=expl,
                               tags=["geometry", "circle"], est=55, verify=f"d={val}", stimulus=_circ_fig(r))
        val = f"{2 * r}π"
        prompt = rng.choice([f"The circle shown has radius {r}. What is its circumference, in terms of π?",
                             f"What is the circumference of a circle with radius {r}, in terms of π?"])
        expl = f"Circumference = 2πr = 2π·{r} = {2 * r}π."
        ds = _pi_distractors(2 * r, [(r * r, "This is the area, not the circumference."),
                                     (r, "Circumference is 2πr, so include the factor of 2."),
                                     (4 * r, "Recheck the formula 2πr."),
                                     (r * r * 2, "Circumference uses r, not r².")])
        return _numeric_mc(rng, prompt, val, ds, subskill="circumference_area", explanation=expl,
                           tags=["geometry", "circle"], fmt=str, est=65, verify=val, stimulus=_circ_fig(r))
    if d == "medium":
        val = f"{r * r}π"
        prompt = rng.choice([f"The circle shown has radius {r}. What is its area, in terms of π?",
                             f"A circular rug has a radius of {r} feet. What is its area, in square feet, in terms of π?"])
        expl = f"Area = πr² = π·{r}² = {r * r}π."
        ds = _pi_distractors(r * r, [(2 * r, "This is the circumference, not the area."),
                                     (r, "Area uses r², not r."),
                                     (r * r * r, "Area uses r², not r³."),
                                     (4 * r * r, "Use the radius, not the diameter.")])
        return _numeric_mc(rng, prompt, val, ds, subskill="circumference_area", explanation=expl,
                           tags=["geometry", "circle"], fmt=str, est=75, verify=val, stimulus=_circ_fig(r))
    dia = 2 * r
    which = rng.choice(["area", "circumference"])
    if which == "area":
        val = f"{r * r}π"
        expl = f"Radius = {dia}/2 = {r}; area = π·{r}² = {r * r}π."
        ds = _pi_distractors(r * r, [(dia * dia, "Use the radius ({0}), not the diameter, in πr².".format(r)),
                                     (dia, "That would be πd, which is not a formula for area."),
                                     (2 * r, "That is the circumference coefficient."),
                                     (r, "Area uses r².")])
    else:
        val = f"{dia}π"
        expl = f"Circumference = πd = π·{dia} = {dia}π (equivalently 2πr with r = {r})."
        ds = _pi_distractors(dia, [(4 * r, "Circumference is πd or 2πr, not 2πd."),
                                   (r, "Circumference is 2πr, not πr."),
                                   (r * r, "That is the area coefficient."),
                                   (dia * dia, "Circumference uses d, not d².")])
    prompt = f"The circle shown has diameter {dia}. What is its {which}, in terms of π?"
    return _numeric_mc(rng, prompt, val, ds, subskill="circumference_area", explanation=expl,
                       tags=["geometry", "circle"], fmt=str, est=80, verify=val,
                       stimulus=_circ_fig(d=dia))


def ci_reverse(rng, d):
    """Recover radius/diameter from circumference or area."""
    r = rng.randint(2, 50)
    if d == "easy":
        prompt = rng.choice([f"A circle has a circumference of {2 * r}π. What is its radius?",
                             f"The circumference of a circular track is {2 * r}π meters. What is the radius of the track, in meters?",
                             f"If the circumference of a circle is {2 * r}π, what is the length of its radius?"])
        val = r
        expl = f"C = 2πr, so r = {2 * r}π/(2π) = {r}."
        ds = [(2 * r, "That is the diameter; divide by 2."),
              (4 * r, "Divide by 2π, not multiply."),
              (r * r, "Don't square."),
              (r + 1, "Arithmetic slip.")]
    elif d == "medium":
        prompt = rng.choice([f"A circle has an area of {r * r}π. What is its diameter?",
                             f"The area of a circle is {r * r}π square units. What is the length of its diameter?"])
        val = 2 * r
        expl = f"A = πr² = {r * r}π gives r = {r}; the diameter is 2r = {val}."
        ds = [(r, "That is the radius; the diameter is twice it."),
              (r * r, "Take the square root of {0}.".format(r * r)),
              (2 * r * r, "Find r first, then double it."),
              (4 * r, "Diameter is 2r.")]
    else:
        prompt = rng.choice([f"A circle has an area of {r * r}π. What is its circumference, in terms of π?",
                             f"The circumference of a circle is {2 * r}π. What is its area, in terms of π?"])
        if prompt.startswith("A circle has an area"):
            val = f"{2 * r}π"
            expl = f"πr² = {r * r}π → r = {r}; circumference = 2π·{r} = {2 * r}π."
            ds = _pi_distractors(2 * r, [(r * r, "That is the area again."), (r, "Circumference is 2πr."),
                                         (4 * r, "Circumference is 2πr, not 4πr."), (r * r * 2, "Find r = √{0} first.".format(r * r))])
        else:
            val = f"{r * r}π"
            expl = f"2πr = {2 * r}π → r = {r}; area = π·{r}² = {r * r}π."
            ds = _pi_distractors(r * r, [(2 * r, "That is the circumference again."), (4 * r * r, "Use r, not the diameter, in πr²."),
                                         (r, "Area uses r²."), (2 * r * 2 * r, "r = {0}, not {1}.".format(r, 2 * r))])
        return _numeric_mc(rng, prompt, val, ds, subskill="circumference_area", explanation=expl,
                           tags=["geometry", "circle"], fmt=str, est=85, verify=val)
    return _numeric_mc(rng, prompt, val, ds, subskill="circumference_area", explanation=expl,
                       tags=["geometry", "circle"], est=70, verify=f"val={val}")


def ci_arc_sector(rng, d):
    """Arc length / sector area / central angle."""
    k = rng.choice([2, 3, 4, 5, 6, 8, 9, 10, 12, 15, 18, 20])
    m = rng.choice([1, 2, 3, 4, 5, 6])
    r = k * m
    theta = 360 // k
    fig = _circ_fig(r, sector=theta)
    if d == "medium":
        val = f"{2 * m}π"
        prompt = rng.choice([f"In the circle shown, the radius is {r} and the central angle of the highlighted arc is {theta}°. What is the length of the arc, in terms of π?",
                             f"A circle has radius {r}. What is the length of an arc with a central angle of {theta}°, in terms of π?"])
        expl = f"Arc length = (θ/360)·2πr = ({theta}/360)·2π·{r} = {2 * m}π."
        ds = _pi_distractors(2 * m, [(2 * r, "This is the whole circumference, not the arc."),
                                     (k * m * m, "That's the sector area, not the arc length."),
                                     (m, "Use 2πr (not πr) before taking the fraction."),
                                     (2 * m * k, "Multiply by the fraction θ/360; don't ignore it.")])
    elif d == "hard":
        val = f"{k * m * m}π"
        prompt = rng.choice([f"In the circle shown, the radius is {r} and the shaded sector has a central angle of {theta}°. What is the area of the sector, in terms of π?",
                             f"A circle has radius {r}. What is the area of a sector with central angle {theta}°, in terms of π?"])
        expl = f"Sector area = (θ/360)·πr² = ({theta}/360)·π·{r}² = {k * m * m}π."
        ds = _pi_distractors(k * m * m, [(r * r, "This is the whole circle's area, not the sector."),
                                         (2 * m, "That's the arc length, not the sector area."),
                                         (k * m, "Use πr² (not πr) before taking the fraction."),
                                         (k * k * m * m, "The fraction is θ/360 = 1/{0}.".format(k))])
    else:
        k = rng.choice([2, 3, 4, 5, 6, 8, 9, 10, 12, 15, 18, 20, 24, 30, 36, 40, 45])
        theta = 360 // k
        val = theta
        prompt = rng.choice([
            f"A sector of a circle has an area equal to 1/{k} of the area of the whole circle. What is the measure, in degrees, of the sector's central angle?",
            f"An arc of a circle has a length equal to 1/{k} of the circle's circumference. What is the measure, in degrees, of the arc's central angle?",
            f"A pie chart is divided into {k} equal sectors. What is the central angle, in degrees, of one sector?"])
        expl = f"The central angle is the same fraction of 360°: 360/{k} = {theta}°."
        ds = [(k, "That is the fraction's denominator, not an angle."),
              (180 // k if k % 2 == 0 or True else theta + 10, "The whole circle is 360°, not 180°."),
              (360 - theta, "That is the angle of the rest of the circle."),
              (theta * 2, "Divide 360 by {0}.".format(k))]
        return _numeric_mc(rng, prompt, val, ds, subskill="arc_sector", explanation=expl,
                           tags=["geometry", "circle", "sector"], est=75, verify=f"angle={theta}")
    return _numeric_mc(rng, prompt, val, ds, subskill="arc_sector", explanation=expl,
                       tags=["geometry", "circle", "sector"], fmt=str, est=95, verify=val, stimulus=fig)


def ci_equation(rng, d):
    """Equation of a circle in the xy-plane (text options)."""
    h = rng.choice([v for v in range(-9, 10) if v != 0])
    k = rng.choice([v for v in range(-9, 10) if v != 0])
    r = rng.randint(2, 12)
    eq = f"(x {_pm(-h)})² + (y {_pm(-k)})² = {r * r}"
    if d == "medium":
        which = rng.choice(["center", "radius"])
        if which == "center":
            prompt = f"The equation {eq} represents a circle in the xy-plane. What are the coordinates of the center of the circle?"
            correct = f"({_m(h)}, {_m(k)})"
            ds = [(f"({_m(-h)}, {_m(-k)})", "The center is (h, k) in (x − h)² + (y − k)²; the signs flip from what's written."),
                  (f"({_m(k)}, {_m(h)})", "The x-coordinate comes from the x-term."),
                  (f"({_m(h)}, {_m(-k)})", "Check the sign of the y-coordinate."),
                  (f"({_m(-h)}, {_m(k)})", "Check the sign of the x-coordinate.")]
            expl = f"The standard form (x − h)² + (y − k)² = r² has center (h, k) = ({_m(h)}, {_m(k)})."
            return _text_mc(rng, prompt, correct, ds, subskill="circumference_area", explanation=expl,
                            tags=["geometry", "circle", "equation"], est=80, verify=f"center ({h},{k})")
        prompt = f"The equation {eq} represents a circle in the xy-plane. What is the radius of the circle?"
        val = r
        expl = f"The right side is r² = {r * r}, so r = {r}."
        ds = [(r * r, "That is r²; take the square root."),
              (2 * r, "That is the diameter."),
              (Fraction(r * r, 2), "Take the square root, don't halve."),
              (abs(h) if abs(h) not in (r, r * r, 2 * r) else r + 1, "The center's coordinates don't give the radius.")]
        return _numeric_mc(rng, prompt, val, ds, subskill="circumference_area", explanation=expl,
                           tags=["geometry", "circle", "equation"], est=75, verify=f"r={r}")
    # hard: write the equation / complete the square
    if rng.random() < 0.5:
        prompt = f"Which equation represents the circle in the xy-plane with center ({_m(h)}, {_m(k)}) and radius {r}?"
        correct = eq
        ds = [(f"(x {_pm(h)})² + (y {_pm(k)})² = {r * r}", "The signs inside the parentheses are opposite to the center's coordinates."),
              (f"(x {_pm(-h)})² + (y {_pm(-k)})² = {r}", "The right side is r², not r."),
              (f"(x {_pm(-k)})² + (y {_pm(-h)})² = {r * r}", "The x-term uses the x-coordinate of the center."),
              (f"(x {_pm(h)})² + (y {_pm(k)})² = {r}", "Both the signs and the radius are wrong.")]
        expl = f"Standard form: (x − h)² + (y − k)² = r² with h = {_m(h)}, k = {_m(k)}, r² = {r * r}."
        return _text_mc(rng, prompt, correct, ds, subskill="circumference_area", explanation=expl,
                        tags=["geometry", "circle", "equation"], est=85, verify=eq)
    # expanded form -> radius
    c = h * h + k * k - r * r
    expanded = f"x² + y² {_pm(-2 * h)}x {_pm(-2 * k)}y {_pm(c)} = 0".replace(" + 0 = 0", " = 0")
    prompt = f"The equation {expanded} represents a circle in the xy-plane. What is the radius of the circle?"
    val = r
    expl = (f"Complete the square: (x {_pm(-h)})² + (y {_pm(-k)})² = {h * h} + {k * k} − ({_m(c)}) = {r * r}, "
            f"so r = {r}.")
    ds = [(r * r, "That is r²; take the square root."),
          (abs(c) if abs(c) not in (r, r * r) else r + 2, "The constant term is not the radius; complete the square."),
          (abs(h) + abs(k) if abs(h) + abs(k) not in (r, r * r) else r + 3, "Complete the square for both x and y."),
          (2 * r, "That is the diameter.")]
    return _numeric_mc(rng, prompt, val, ds, subskill="circumference_area", explanation=expl,
                       tags=["geometry", "circle", "equation"], est=110, qtype="multi_step_math",
                       verify=f"r={r}")


# --------------------------------------------------------------------------- #
# right_triangles
# --------------------------------------------------------------------------- #
def rt_pythagorean(rng, d):
    """Hypotenuse (easy), missing leg (medium), word/diagonal (hard)."""
    a, b, c = _pyth_triple(rng)
    if rng.random() < 0.5:
        a, b = b, a
    if d == "easy":
        prompt = rng.choice([f"The right triangle shown has legs of length {a} and {b}. What is the length of the hypotenuse?",
                             f"A right triangle has legs of length {a} and {b}. What is the length of its hypotenuse?"])
        val = c
        expl = f"c² = {a}² + {b}² = {a * a} + {b * b} = {c * c}, so c = {c}."
        ds = [(a + b, "You added the legs instead of using a² + b² = c²."),
              (c - 1, "Off by one; recompute the square root."),
              (a * b, "This multiplies the legs; use the Pythagorean theorem."),
              (c * c, "That is c²; take the square root.")]
        fig = _tri_fig(a, b, "?")
    elif d == "medium":
        prompt = rng.choice([f"The right triangle shown has one leg of length {a} and a hypotenuse of length {c}. What is the length of the other leg?",
                             f"In a right triangle, the hypotenuse has length {c} and one leg has length {a}. What is the length of the other leg?"])
        val = b
        expl = f"leg = √(c² − a²) = √({c * c} − {a * a}) = √{b * b} = {b}."
        ds = [(c - a, "Subtracting the lengths is not the Pythagorean theorem."),
              (b + 1, "Off by one; recompute c² − a²."),
              (c + a, "Add/subtract under the square root, not outside it."),
              (math.isqrt(c * c + a * a), "The hypotenuse is the longest side; subtract, don't add.")]
        fig = _tri_fig(a, "?", c)
    else:
        ctx = rng.choice([("A {c}-foot ladder leans against a wall with its base {a} feet from the wall. How high up the wall, in feet, does the ladder reach?", b),
                          ("A rectangular field is {a} meters by {b} meters. What is the length, in meters, of a diagonal path across the field?", c),
                          ("A boat travels {a} km due east and then {b} km due north. How far, in km, is the boat from its starting point?", c),
                          ("A wire runs from the top of a {b}-meter pole to a point on the ground {a} meters from the base. How long, in meters, is the wire?", c)])
        prompt = ctx[0].format(a=a, b=b, c=c)
        val = ctx[1]
        expl = (f"The situation forms a right triangle with legs {a} and {b} and hypotenuse {c}: "
                f"{a}² + {b}² = {c}². The answer is {val}.")
        ds = [(a + b if val == c else c - a, "Use a² + b² = c², not addition/subtraction of lengths."),
              (val + 1, "Off by one; recheck the squares."),
              (a * b if val == c else a * c, "Don't multiply the sides."),
              (c if val != c else b, "That is a different side of the triangle.")]
        fig = None
    return _numeric_mc(rng, prompt, val, ds, subskill="pythagorean", explanation=expl,
                       tags=["geometry", "right-triangle"], est=80 if d != "hard" else 95,
                       verify=f"sides {a},{b},{c}", stimulus=fig)


def rt_special(rng, d):
    """Special right triangles: 45-45-90 and 30-60-90."""
    n = rng.randint(2, 15)
    if d == "medium":
        kind = rng.choice(["45_hyp", "30_hyp"])
        if kind == "45_hyp":
            val = f"{n}√2"
            prompt = f"The right triangle shown is a 45°-45°-90° triangle with legs of length {n}. What is the length of the hypotenuse?"
            expl = f"In a 45-45-90 triangle the hypotenuse is leg·√2, so it is {n}√2."
            ds = [(f"{2 * n}", "That would be 2·leg; a 45-45-90 hypotenuse is leg·√2."),
                  (f"{n}√3", "√3 is for a 30-60-90 triangle, not 45-45-90."),
                  (f"{n * n}", "Don't square the leg; multiply by √2."),
                  (f"{2 * n}√2", "The factor is √2, not 2√2.")]
            fig = _tri_fig(n, n, "?", angle="45°", caption="45°-45°-90° triangle")
        else:
            val = 2 * n
            prompt = f"In the 30°-60°-90° triangle shown, the shorter leg (opposite the 30° angle) has length {n}. What is the length of the hypotenuse?"
            expl = f"In a 30-60-90 triangle the hypotenuse is twice the shorter leg: 2·{n} = {2 * n}."
            ds = [(n * 3, "The hypotenuse is 2·(short leg), not 3·(short leg)."),
                  (n + 2, "Multiply by 2; don't add."),
                  (n * n, "Don't square the leg."),
                  (n * 2 + 1, "Arithmetic slip.")]
            fig = _tri_fig("?", n, "?", angle="30°", caption="30°-60°-90° triangle")
            return _numeric_mc(rng, prompt, val, ds, subskill="special_triangles", explanation=expl,
                               tags=["geometry", "right-triangle", "special"], est=85,
                               verify=f"hyp={val}", stimulus=fig)
    else:
        kind = rng.choice(["30_long", "45_leg", "30_from_hyp"])
        if kind == "30_long":
            val = f"{n}√3"
            prompt = f"The right triangle shown is a 30°-60°-90° triangle. The shorter leg has length {n}. What is the length of the longer leg?"
            expl = f"In a 30-60-90 triangle the longer leg is (short leg)·√3, so it is {n}√3."
            ds = [(f"{2 * n}", "That is the hypotenuse (2·short leg), not the longer leg."),
                  (f"{n}√2", "√2 is for a 45-45-90 triangle, not 30-60-90."),
                  (f"{3 * n}", "The factor is √3, not 3."),
                  (f"{2 * n}√3", "The longer leg is short·√3, without the 2.")]
            fig = _tri_fig("?", n, str(2 * n), angle="30°", caption="30°-60°-90° triangle")
        elif kind == "45_leg":
            val = f"{n}"
            prompt = f"A 45°-45°-90° triangle has a hypotenuse of length {n}√2. What is the length of each leg?"
            expl = f"Hypotenuse = leg·√2, so leg = {n}√2/√2 = {n}."
            ds = [(f"{n}√2", "That is the hypotenuse; divide by √2."),
                  (f"{2 * n}", "Divide by √2, not multiply."),
                  (f"{n}/2", "Divide by √2, not by 2."),
                  (f"{n}√3", "√3 belongs to 30-60-90 triangles.")]
            fig = _tri_fig("?", "?", f"{n}√2", angle="45°", caption="45°-45°-90° triangle")
        else:
            val = f"{n}√3"
            prompt = f"In a 30°-60°-90° triangle the hypotenuse has length {2 * n}. What is the length of the longer leg?"
            expl = f"Short leg = hypotenuse/2 = {n}; longer leg = {n}√3."
            ds = [(f"{n}", "That is the shorter leg."),
                  (f"{2 * n}√3", "Halve the hypotenuse first to get the short leg."),
                  (f"{n}√2", "√2 is for 45-45-90 triangles."),
                  (f"{3 * n}", "The factor is √3, not 3.")]
            fig = _tri_fig("?", "?", str(2 * n), angle="30°", caption="30°-60°-90° triangle")
    return _numeric_mc(rng, prompt, val, ds, subskill="special_triangles", explanation=expl,
                       fmt=str, est=95, tags=["geometry", "right-triangle", "special"],
                       verify=val, stimulus=fig)


rt_special.small_space = True


def rt_is_right(rng, d):
    """Which set of side lengths forms a right triangle (text options)."""
    a, b, c = _pyth_triple(rng, 30)
    correct = f"{a}, {b}, {c}"
    fakes = []
    for trip in [(a, b, c + 1), (a + 1, b, c), (a, b + 1, c), (a, b, c - 1), (a + 2, b, c), (a, b, c + 2)]:
        t = f"{trip[0]}, {trip[1]}, {trip[2]}"
        if t != correct and t not in fakes and trip[0] * trip[0] + trip[1] * trip[1] != trip[2] * trip[2]:
            fakes.append(t)
    ds = [(t, "Check: the squares of the two smaller numbers do not add to the square of the largest.") for t in fakes[:4]]
    prompt = "Which of the following sets of side lengths could form a right triangle?"
    expl = f"{a}² + {b}² = {a * a} + {b * b} = {c * c} = {c}², so {correct} satisfies the Pythagorean theorem."
    return _text_mc(rng, prompt, correct, ds, subskill="pythagorean", explanation=expl,
                    tags=["geometry", "right-triangle", "converse"], est=85, verify=f"{a},{b},{c}")


rt_is_right.small_space = True


def rt_area_perimeter(rng, d):
    """Area or perimeter of a right triangle from two sides."""
    a, b, c = _pyth_triple(rng)
    which = rng.choice(["area", "perimeter"])
    if d == "easy":
        prompt = f"A right triangle has legs of length {a} and {b}. What is its {which}?" if which == "area" else \
                 f"A right triangle has legs {a} and {b} and hypotenuse {c}. What is its perimeter?"
        val = a * b // 2 if which == "area" else a + b + c
        if which == "area":
            expl = f"Area = ½ × {a} × {b} = {val}."
            ds = [(a * b, "You forgot the ½."), (a + b + c, "That is the perimeter."), (a * c // 2, "The legs are the base and height, not the hypotenuse."), (val + a, "Arithmetic slip.")]
        else:
            expl = f"Perimeter = {a} + {b} + {c} = {val}."
            ds = [(a * b // 2, "That is the area."), (a + b, "Include the hypotenuse."), (val + c, "Count each side once."), (a * b, "Add the sides; don't multiply.")]
        fig = _tri_fig(a, b, c)
    else:
        given = "legs" if rng.random() < 0.5 else "hyp"
        if given == "legs":
            prompt = f"The right triangle shown has legs of length {a} and {b}. What is its perimeter?"
            val = a + b + c
            expl = f"Hypotenuse = √({a}² + {b}²) = {c}; perimeter = {a} + {b} + {c} = {val}."
            ds = [(a + b, "Find and include the hypotenuse."), (a * b // 2, "That is the area."), (a + b + (a + b), "The hypotenuse is √(a² + b²), not a + b."), (val - 1, "Recheck the hypotenuse.")]
            fig = _tri_fig(a, b, "?")
        else:
            prompt = f"The right triangle shown has a hypotenuse of length {c} and one leg of length {a}. What is its area?"
            val = a * b // 2
            expl = f"Other leg = √({c}² − {a}²) = {b}; area = ½ × {a} × {b} = {val}."
            ds = [(a * c // 2, "Use the two legs, not the hypotenuse, for base and height."), (a * b, "You forgot the ½."), (a + b + c, "That is the perimeter."), ((c - a) * a // 2, "The missing leg is √(c² − a²), not c − a.")]
            fig = _tri_fig(a, "?", c)
    return _numeric_mc(rng, prompt, val, ds, subskill="pythagorean", explanation=expl,
                       tags=["geometry", "right-triangle"], est=80 if d == "easy" else 95,
                       verify=f"sides {a},{b},{c}", stimulus=fig)


rt_area_perimeter.small_space = True


# --------------------------------------------------------------------------- #
# trigonometry
# --------------------------------------------------------------------------- #
def _trig_setup(rng):
    """Figure with θ at the bottom-right: adjacent = base a, opposite = vertical b."""
    a, b, c = _pyth_triple(rng)
    if rng.random() < 0.5:
        a, b = b, a
    fig = _tri_fig(a, b, c, angle="θ")
    return a, b, c, fig   # adjacent, opposite, hypotenuse


def tr_ratio(rng, d):
    """Identify sin/cos/tan from a labeled triangle."""
    adj, opp, hyp, fig = _trig_setup(rng)
    ratio = rng.choice(["sin", "cos", "tan"])
    vals = {"sin": (opp, hyp), "cos": (adj, hyp), "tan": (opp, adj)}
    n, m = vals[ratio]
    val = f"{n}/{m}"
    names = {"sin": "opposite/hypotenuse", "cos": "adjacent/hypotenuse", "tan": "opposite/adjacent"}
    ds = []
    for r2, (p, q) in vals.items():
        if r2 != ratio:
            ds.append((f"{p}/{q}", f"That ratio is {r2} θ ({names[r2]})."))
    ds.append((f"{m}/{n}", f"This inverts the {ratio} ratio."))
    ds.append((f"{adj}/{opp}", "That is the reciprocal of tan θ.") if ratio != "tan" else (f"{hyp}/{opp}", "That is the reciprocal of sin θ."))
    prompt = (f"In the right triangle shown, the side opposite angle θ has length {opp}, the side "
              f"adjacent to θ has length {adj}, and the hypotenuse has length {hyp}. What is the "
              f"value of {ratio} θ?")
    return _numeric_mc(rng, prompt, val, ds, subskill="sohcahtoa", explanation=f"{ratio} θ = {names[ratio]} = {val}.",
                       tags=["trigonometry"], fmt=str, est=80, verify=f"{ratio}={val}", stimulus=fig)


tr_ratio.small_space = True


def tr_find_side(rng, d):
    """Use a trig ratio to find a side (medium), or the other ratio (hard)."""
    adj, opp, hyp, fig = _trig_setup(rng)
    if d == "medium":
        scale = rng.randint(2, 6)
        ratio = rng.choice(["sin", "cos", "tan"])
        if ratio == "sin":
            val = opp * scale
            prompt = f"In a right triangle, sin θ = {opp}/{hyp}. If the hypotenuse has length {hyp * scale}, what is the length of the side opposite θ?"
            expl = f"sin θ = opposite/hypotenuse → opposite = ({opp}/{hyp})·{hyp * scale} = {val}."
            ds = [(adj * scale, "That is the adjacent side (from cos θ)."), (hyp * scale, "That is the hypotenuse."), (opp, "Scale by the actual hypotenuse."), (val + scale, "Arithmetic slip.")]
        elif ratio == "cos":
            val = adj * scale
            prompt = f"In a right triangle, cos θ = {adj}/{hyp}. If the hypotenuse has length {hyp * scale}, what is the length of the side adjacent to θ?"
            expl = f"cos θ = adjacent/hypotenuse → adjacent = ({adj}/{hyp})·{hyp * scale} = {val}."
            ds = [(opp * scale, "That is the opposite side (from sin θ)."), (hyp * scale, "That is the hypotenuse."), (adj, "Scale by the actual hypotenuse."), (val + scale, "Arithmetic slip.")]
        else:
            val = opp * scale
            prompt = f"In a right triangle, tan θ = {opp}/{adj}. If the side adjacent to θ has length {adj * scale}, what is the length of the side opposite θ?"
            expl = f"tan θ = opposite/adjacent → opposite = ({opp}/{adj})·{adj * scale} = {val}."
            ds = [(adj * scale, "That is the adjacent side."), (hyp * scale, "That is the hypotenuse."), (opp, "Scale by the actual adjacent side."), (val + scale, "Arithmetic slip.")]
        return _numeric_mc(rng, prompt, val, ds, subskill="sohcahtoa", explanation=expl,
                           tags=["trigonometry"], est=90, verify=f"side={val}")
    given, want = rng.choice([("sin", "cos"), ("cos", "sin"), ("sin", "tan"), ("cos", "tan"), ("tan", "sin"), ("tan", "cos")])
    vals = {"sin": f"{opp}/{hyp}", "cos": f"{adj}/{hyp}", "tan": f"{opp}/{adj}"}
    prompt = f"In a right triangle, {given} θ = {vals[given]}. What is the value of {want} θ?"
    val = vals[want]
    expl = (f"From {given} θ = {vals[given]} the sides are opposite {opp}, adjacent {adj}, hypotenuse {hyp} "
            f"(since {opp}² + {adj}² = {hyp}²). So {want} θ = {val}.")
    other = [r for r in ("sin", "cos", "tan") if r not in (given, want)][0]
    ds = [(vals[given], f"That is {given} θ again."),
          (vals[other], f"That is {other} θ."),
          (f"{val.split('/')[1]}/{val.split('/')[0]}", f"This inverts {want} θ."),
          (f"{hyp}/{adj}" if want != "cos" else f"{hyp}/{opp}", "That is a reciprocal ratio (sec or csc), not {0} θ.".format(want))]
    return _numeric_mc(rng, prompt, val, ds, subskill="sohcahtoa", explanation=expl,
                       tags=["trigonometry"], fmt=str, est=95, verify=f"{want}={val}", stimulus=fig)


tr_find_side.small_space = True


def tr_complementary(rng, d):
    """sin x° = cos(90 − x)°; find angles / values."""
    if d == "easy":
        x = rng.randint(5, 85)
        prompt = rng.choice([f"If sin {x}° = cos y°, and 0 < y < 90, what is the value of y?",
                             f"For what value of y, with 0 < y < 90, is cos {x}° equal to sin y°?",
                             f"If sin({x}°) = cos(y°) for an acute angle y°, what is y?"])
        val = 90 - x
        expl = f"Sine and cosine of complementary angles are equal: y = 90 − {x} = {val}."
        ds = [(x, "sin x = cos x only when x = 45."), (180 - x, "Complementary angles sum to 90°, not 180°."), (90 + x, "Subtract from 90; don't add."), (val + 5, "Arithmetic slip.")]
    elif d == "medium":
        a, b = rng.randint(2, 6), rng.randint(1, 20)
        # sin(ax + b) = cos(... ) with a x + b + (c x + e) = 90 ; choose x answer
        x = rng.randint(3, 15)
        e = 90 - (a * x + b) - x   # second angle = x + e  -> coefficient 1
        if e <= 0 or a * x + b >= 90:
            return tr_complementary(rng, d)
        prompt = f"If sin({a}x + {b})° = cos(x + {e})°, where both angles are acute, what is the value of x?"
        val = x
        expl = f"The angles are complementary: ({a}x + {b}) + (x + {e}) = 90 → {a + 1}x = {90 - b - e} → x = {x}."
        ds = [(Fraction(90 - b - e, a) if (90 - b - e) % a else x + 1, "Collect both x terms: {0}x + x.".format(a)),
              (Fraction(b - e, a - 1) if a != 1 and (b - e) % (a - 1) == 0 else -x, "Setting the angles equal is wrong; they are complementary."),
              (Fraction(180 - b - e, a + 1), "Complementary angles sum to 90°, not 180°."),
              (x - 1, "Arithmetic slip.")]
    else:
        adj, opp, hyp, fig = _trig_setup(rng)
        prompt = rng.choice([f"In a right triangle with acute angles A and B, sin A = {opp}/{hyp}. What is the value of cos B?",
                             f"Angles A and B are the acute angles of a right triangle. If sin A = {opp}/{hyp}, what is cos B?",
                             f"In right triangle ABC with right angle at C, sin A = {opp}/{hyp}. What is the value of cos B?"])
        val = f"{opp}/{hyp}"
        expl = f"A and B are complementary, so cos B = sin A = {val}."
        ds = [(f"{adj}/{hyp}", "That is cos A, not cos B."), (f"{opp}/{adj}", "That is tan A."),
              (f"{hyp}/{opp}", "That is the reciprocal of sin A."), (f"{adj}/{opp}", "That is tan B.")]
        return _numeric_mc(rng, prompt, val, ds, subskill="sohcahtoa", explanation=expl,
                           tags=["trigonometry", "complementary"], fmt=str, est=90, verify=f"cosB={val}")
    return _numeric_mc(rng, prompt, val, ds, subskill="sohcahtoa", explanation=expl,
                       tags=["trigonometry", "complementary"], est=80, verify=f"val={num_str(val)}")


def tr_radians(rng, d):
    """Convert between degrees and radians."""
    pairs = [(30, "π/6"), (45, "π/4"), (60, "π/3"), (90, "π/2"), (120, "2π/3"), (135, "3π/4"), (150, "5π/6"),
             (180, "π"), (210, "7π/6"), (225, "5π/4"), (240, "4π/3"), (270, "3π/2"), (300, "5π/3"), (315, "7π/4"), (360, "2π")]
    deg, rad = rng.choice(pairs)
    if d == "easy" or (d == "medium" and rng.random() < 0.5):
        prompt = f"What is {deg}° expressed in radians?"
        val = rad
        expl = f"Multiply by π/180: {deg}·π/180 = {rad}."
        others = [r for dg, r in pairs if r != rad]
        picks = rng.sample(others, 3)
        ds = [(picks[0], "Recompute: degrees × π/180."), (f"{deg}π", "Divide by 180."),
              (f"{Fraction(180, deg)}π" if Fraction(180, deg).denominator == 1 else f"180π/{deg}", "This inverts the conversion factor."),
              (picks[1], "Recompute the fraction."), (picks[2], "Check the fraction of π.")]
    else:
        prompt = f"What is {rad} radians expressed in degrees?"
        val = deg
        expl = f"Multiply by 180/π: {rad}·180/π = {deg}°."
        ds = [(360 - deg if 360 - deg not in (0, deg) else deg + 30, "Recompute: radians × 180/π."),
              (deg // 2 if deg % 2 == 0 else deg + 15, "Check the fraction of π."),
              (deg * 2 if deg * 2 <= 720 else deg - 30, "Check the fraction of π."),
              (Fraction(deg, 180), "Multiply by 180/π to get degrees.")]
        return _numeric_mc(rng, prompt, val, ds, subskill="sohcahtoa", explanation=expl,
                           tags=["trigonometry", "radians"], est=70, verify=f"{rad}={deg}°")
    return _numeric_mc(rng, prompt, val, ds, subskill="sohcahtoa", explanation=expl,
                       tags=["trigonometry", "radians"], fmt=str, est=70, verify=f"{deg}°={rad}")


tr_radians.small_space = True


def tr_word(rng, d):
    """Trig ratio from a real-world right triangle (small_space)."""
    adj, opp, hyp, fig = _trig_setup(rng)
    ctx = rng.choice([
        ("A ramp rises {opp} feet over a horizontal distance of {adj} feet, so its length is {hyp} feet. If θ is the angle the ramp makes with the ground, what is tan θ?", f"{opp}/{adj}", "tan"),
        ("A kite string of length {hyp} meters makes an angle θ with the ground; the kite is {opp} meters above the ground. What is sin θ?", f"{opp}/{hyp}", "sin"),
        ("A {hyp}-foot ladder leans against a wall with its base {adj} feet from the wall, making an angle θ with the ground. What is cos θ?", f"{adj}/{hyp}", "cos"),
    ])
    prompt = ctx[0].format(adj=adj, opp=opp, hyp=hyp)
    val = ctx[1]
    ratio = ctx[2]
    vals = {"sin": f"{opp}/{hyp}", "cos": f"{adj}/{hyp}", "tan": f"{opp}/{adj}"}
    ds = [(v, f"That is {r} θ.") for r, v in vals.items() if r != ratio]
    ds.append((f"{val.split('/')[1]}/{val.split('/')[0]}", f"This inverts {ratio} θ."))
    for r, v in vals.items():
        if r != ratio:
            ds.append((f"{v.split('/')[1]}/{v.split('/')[0]}", f"That is the reciprocal of {r} θ."))
    expl = f"Relative to θ: opposite = {opp}, adjacent = {adj}, hypotenuse = {hyp}. {ratio} θ = {val}."
    return _numeric_mc(rng, prompt, val, ds, subskill="sohcahtoa", explanation=expl,
                       tags=["trigonometry", "word-problem"], fmt=str, est=85, verify=f"{ratio}={val}",
                       stimulus=fig)


tr_word.small_space = True


# --------------------------------------------------------------------------- #
# Family registry
# --------------------------------------------------------------------------- #
FAMILIES = {
    "linear_equations": {
        "easy": [le_two_step, le_both_sides, le_distribute, le_model_equation, le_intercepts, le_gridin],
        "medium": [le_two_step, le_both_sides, le_distribute, le_model_equation, le_interpret,
                   le_intercepts, le_slope_points, le_parallel_perp, le_line_equation,
                   le_expression_value, le_gridin],
        "hard": [le_two_step, le_both_sides, le_distribute, le_model_equation, le_interpret,
                 le_intercepts, le_slope_points, le_parallel_perp, le_line_equation, le_literal,
                 le_expression_value, le_gridin],
    },
    "linear_inequalities": {
        "easy": [li_extreme_integer, li_solution_set, li_model, li_word_max, li_must_be_true, li_gridin],
        "medium": [li_extreme_integer, li_solution_set, li_model, li_word_max, li_ordered_pair, li_gridin],
        "hard": [li_extreme_integer, li_solution_set, li_model, li_word_max, li_ordered_pair, li_gridin],
    },
    "systems_of_equations": {
        "easy": [sys_solve, sys_substitution, sys_word, sys_which_system, sys_gridin],
        "medium": [sys_solve, sys_substitution, sys_word, sys_which_system, sys_solution_count, sys_gridin],
        "hard": [sys_solve, sys_substitution, sys_word, sys_which_system, sys_solution_count, sys_gridin],
    },
    "functions": {
        "easy": [fn_evaluate, fn_solve_input, fn_table, fn_undefined, fn_gridin],
        "medium": [fn_evaluate, fn_solve_input, fn_table, fn_compose_transform, fn_interpret, fn_undefined, fn_gridin],
        "hard": [fn_evaluate, fn_solve_input, fn_table, fn_compose_transform, fn_interpret, fn_gridin],
    },
    "quadratics": {
        "easy": [q_roots, q_vertex, q_square_root, q_gridin],
        "medium": [q_roots, q_vertex, q_discriminant, q_equivalent_form, q_square_root, q_gridin],
        "hard": [q_roots, q_vertex, q_discriminant, q_equivalent_form, q_square_root, q_projectile, q_gridin],
    },
    "exponents_radicals": {
        "easy": [ex_rules, ex_evaluate, ex_radicals, ex_solve_exponential, ex_gridin],
        "medium": [ex_rules, ex_evaluate, ex_radicals, ex_solve_exponential, ex_algebraic, ex_gridin],
        "hard": [ex_rules, ex_evaluate, ex_radicals, ex_solve_exponential, ex_algebraic, ex_rewrite_radical, ex_gridin],
    },
    "polynomials": {
        "easy": [poly_expand, poly_add_sub, poly_factor, poly_evaluate],
        "medium": [poly_expand, poly_add_sub, poly_factor, poly_evaluate, poly_product_coeff],
        "hard": [poly_add_sub, poly_factor, poly_evaluate, poly_product_coeff, poly_expand],
    },
    "ratios_percentages_units": {
        "easy": [rp_percent_of, rp_percent_change, rp_ratio, rp_units, rp_gridin],
        "medium": [rp_percent_of, rp_percent_change, rp_ratio, rp_units, rp_gridin],
        "hard": [rp_percent_of, rp_percent_change, rp_ratio, rp_units, rp_gridin],
    },
    "proportions": {
        "easy": [pr_direct, pr_solve, pr_similar, pr_recipe, pr_gridin],
        "medium": [pr_direct, pr_solve, pr_inverse, pr_similar, pr_recipe, pr_gridin],
        "hard": [pr_direct, pr_solve, pr_inverse, pr_similar, pr_recipe, pr_gridin],
    },
    "data_analysis": {
        "easy": [da_read, da_mean_from_table, da_two_year, da_rate_table, da_statement],
        "medium": [da_read, da_mean_from_table, da_two_year, da_rate_table, da_statement],
        "hard": [da_read, da_mean_from_table, da_two_year, da_rate_table, da_statement],
    },
    "statistics": {
        "easy": [st_center_list, st_spread, st_missing_value, st_frequency_table, st_change_effect, st_gridin],
        "medium": [st_center_list, st_spread, st_missing_value, st_frequency_table, st_change_effect, st_gridin],
        "hard": [st_center_list, st_spread, st_missing_value, st_frequency_table, st_change_effect, st_gridin],
    },
    "probability": {
        "easy": [pb_single, pb_compound, pb_expected, pb_table, pb_gridin],
        "medium": [pb_single, pb_compound, pb_expected, pb_table, pb_gridin],
        "hard": [pb_single, pb_compound, pb_expected, pb_table, pb_gridin],
    },
    "area_volume": {
        "easy": [av_rect_tri, av_perimeter, av_volume, av_composite, av_gridin],
        "medium": [av_rect_tri, av_perimeter, av_volume, av_composite, av_gridin],
        "hard": [av_rect_tri, av_perimeter, av_volume, av_composite, av_gridin],
    },
    "circles": {
        "easy": [ci_basic, ci_reverse, ci_arc_sector],
        "medium": [ci_basic, ci_reverse, ci_arc_sector, ci_equation],
        "hard": [ci_basic, ci_reverse, ci_arc_sector, ci_equation],
    },
    "right_triangles": {
        "easy": [rt_pythagorean, rt_is_right, rt_area_perimeter],
        "medium": [rt_pythagorean, rt_special, rt_area_perimeter],
        "hard": [rt_pythagorean, rt_special, rt_is_right, rt_area_perimeter],
    },
    "trigonometry": {
        "easy": [tr_ratio, tr_complementary, tr_radians, tr_word],
        "medium": [tr_find_side, tr_complementary, tr_radians, tr_word],
        "hard": [tr_find_side, tr_complementary, tr_radians, tr_word],
    },
}

# Legacy entry points (one function per skill) kept for the current
# orchestrator; each picks a random family for the requested difficulty.
linear_equations = _dispatch(FAMILIES, "linear_equations")
linear_inequalities = _dispatch(FAMILIES, "linear_inequalities")
systems_of_equations = _dispatch(FAMILIES, "systems_of_equations")
functions = _dispatch(FAMILIES, "functions")
quadratics = _dispatch(FAMILIES, "quadratics")
exponents_radicals = _dispatch(FAMILIES, "exponents_radicals")
polynomials = _dispatch(FAMILIES, "polynomials")
ratios_percentages_units = _dispatch(FAMILIES, "ratios_percentages_units")
proportions = _dispatch(FAMILIES, "proportions")
data_analysis = _dispatch(FAMILIES, "data_analysis")
statistics = _dispatch(FAMILIES, "statistics")
probability = _dispatch(FAMILIES, "probability")
area_volume = _dispatch(FAMILIES, "area_volume")
circles = _dispatch(FAMILIES, "circles")
right_triangles = _dispatch(FAMILIES, "right_triangles")
trigonometry = _dispatch(FAMILIES, "trigonometry")


# =========================================================================== #
# Bank-growth families (v2.1): additional question forms for every skill.
# =========================================================================== #
# ---- linear_equations ----------------------------------------------------- #
def le_point_on_line(rng, d):
    """Which point is / is NOT on a line; or the k that puts a point on it."""
    m = rng.choice([v for v in range(-7, 8) if v])
    b = rng.choice([v for v in range(-15, 16) if v])
    if d == "easy":
        xs = rng.sample(range(-6, 7), 5)
        good = (xs[0], m * xs[0] + b)
        bads = [(x, m * x + b + rng.choice([-4, -3, -2, -1, 1, 2, 3, 4])) for x in xs[1:]]
        prompt = f"Which of the following points lies on the graph of y = {_lin(m, b)} in the xy-plane?"
        correct = f"({_m(good[0])}, {_m(good[1])})"
        ds = [(f"({_m(x)}, {_m(y)})", f"At x = {_m(x)} the equation gives y = {_m(m * x + b)}, not {_m(y)}.") for x, y in bads]
        expl = f"Substitute x = {_m(good[0])}: y = {_m(m)}({_m(good[0])}) {_pm(b)} = {_m(good[1])}. That matches {correct}."
        verify = f"({good[0]},{good[1]}) on y={m}x+({b})"
    elif d == "medium":
        a, bb = rng.choice([v for v in range(-6, 7) if v]), rng.choice([v for v in range(-6, 7) if v])
        xs = rng.sample(range(-6, 7), 5)
        # points on ax + by = c
        x0 = xs[0]
        y0 = rng.randint(-6, 6)
        c = a * x0 + bb * y0
        goods = [(x, y) for x in range(-8, 9) for y in range(-8, 9) if a * x + bb * y == c]
        offs = []
        while len(offs) < 4:
            x, y = rng.randint(-8, 8), rng.randint(-8, 8)
            if a * x + bb * y != c and (x, y) not in offs:
                offs.append((x, y))
        goods = [g for g in goods if g not in offs]
        line = f"{_lin(a, 0)} {'+' if bb > 0 else '−'} {_coef(abs(bb), 'y')} = {_m(c)}"
        if rng.random() < 0.5:
            prompt = f"Which of the following ordered pairs (x, y) is a solution to the equation {line}?"
            good = rng.choice(goods)
            correct = f"({_m(good[0])}, {_m(good[1])})"
            ds = [(f"({_m(x)}, {_m(y)})", f"{_m(a)}({_m(x)}) {'+' if bb > 0 else '−'} {abs(bb)}({_m(y)}) = {_m(a * x + bb * y)}, not {_m(c)}.") for x, y in offs]
            expl = f"Check {correct}: {_m(a)}({_m(good[0])}) {'+' if bb > 0 else '−'} {abs(bb)}({_m(good[1])}) = {_m(c)}."
        else:
            prompt = f"Which of the following ordered pairs (x, y) is NOT a solution to the equation {line}?"
            bad = offs[0]
            correct = f"({_m(bad[0])}, {_m(bad[1])})"
            picks = rng.sample(goods, min(4, len(goods)))
            if len(picks) < 3:
                return le_point_on_line(rng, d)
            ds = [(f"({_m(x)}, {_m(y)})", f"This pair satisfies the equation: {_m(a)}({_m(x)}) {'+' if bb > 0 else '−'} {abs(bb)}({_m(y)}) = {_m(c)}.") for x, y in picks]
            expl = f"For {correct}: {_m(a)}({_m(bad[0])}) {'+' if bb > 0 else '−'} {abs(bb)}({_m(bad[1])}) = {_m(a * bad[0] + bb * bad[1])} ≠ {_m(c)}, so it is not a solution."
        verify = f"line {a}x+({bb})y={c}"
    else:
        a, bb = rng.choice([v for v in range(2, 10)]), rng.choice([v for v in range(-9, 10) if v])
        x0, y0 = rng.choice([v for v in range(-9, 10) if v]), rng.choice([v for v in range(-9, 10) if v])
        c = a * x0 + bb * y0
        line = f"{_lin(a, 0)} {'+' if bb > 0 else '−'} {_coef(abs(bb), 'y')} = {_m(c)}"
        if rng.random() < 0.5:
            prompt = f"The point ({_m(x0)}, k) lies on the graph of {line} in the xy-plane. What is the value of k?"
            val = y0
            expl = f"Substitute x = {_m(x0)}: {_m(a * x0)} {'+' if bb > 0 else '−'} {abs(bb)}k = {_m(c)}, so k = {_m(y0)}."
            ds = [(Fraction(c - a * x0, -bb), "Sign slip when isolating k."), (Fraction(c + a * x0, bb), "Subtract {0}; don't add it.".format(_m(a * x0))), (c - a * x0, "Divide by the coefficient of y."), (x0, "That is the x-coordinate.")]
        else:
            prompt = f"The point (k, {_m(y0)}) lies on the graph of {line} in the xy-plane. What is the value of k?"
            val = x0
            expl = f"Substitute y = {_m(y0)}: {a}k {_pm(bb * y0)} = {_m(c)}, so k = {_m(x0)}."
            ds = [(Fraction(c + bb * y0, a), "Subtract {0}; don't add it.".format(_m(bb * y0))), (-x0, "Sign slip when isolating k."), (c - bb * y0, "Divide by the coefficient of x."), (y0, "That is the y-coordinate.")]
        return _numeric_mc(rng, prompt, val, ds, subskill="two_variable", explanation=expl,
                           tags=["algebra", "linear", "point"], est=85, verify=f"({x0},{y0}) on {a}x+({bb})y={c}")
    return _text_mc(rng, prompt, correct, ds, subskill="two_variable", explanation=expl,
                    tags=["algebra", "linear", "point"], est=80, verify=verify)


def le_table_equation(rng, d):
    """A table of (x, y) values -> which equation relates them (text options)."""
    m = rng.choice([v for v in range(-6, 7) if v])
    if d == "easy":
        b = 0
        xs = sorted(rng.sample(range(1, 10), 4))
    elif d == "medium":
        b = rng.choice([v for v in range(-12, 13) if v])
        xs = sorted(rng.sample(range(-3, 8), 4))
    else:
        b = rng.choice([v for v in range(-12, 13) if v])
        xs = sorted(rng.sample(range(-8, 9, 2), 4))   # spacing 2+ so the slope must be computed
    ys = [m * x + b for x in xs]
    stim = _table("Values of x and y", ["x", "y"], [[x, y] for x, y in zip(xs, ys)])
    correct = f"y = {_lin(m, b)}"
    prompt = rng.choice([f"The table shows four pairs of values of x and y that satisfy a linear equation (x = {xs[0]} gives y = {_m(ys[0])}). Which equation is it?",
                         f"The table gives values of y for four values of x; when x = {xs[-1]}, y = {_m(ys[-1])}. Which equation relates x and y?"])
    dy = ys[1] - ys[0]
    ds = [(f"y = {_lin(dy, b)}" if dy != m else f"y = {_lin(m + 1, b)}", "Divide the change in y by the change in x; the x-values are not 1 apart." if dy != m else "Recheck the rate of change."),
          (f"y = {_lin(m, ys[0])}" if ys[0] != b else f"y = {_lin(m, b + 2)}", f"{_m(ys[0])} is y when x = {xs[0]}, not when x = 0."),
          (f"y = {_lin(b, m)}" if b != m else f"y = {_lin(-m, b)}", "The slope and the constant are swapped." if b != m else "Check the sign of the slope."),
          (f"y = {_lin(-m, b)}" if b != m else f"y = {_lin(m, -b)}", "Check the sign of the slope." if b != m else "Check the sign of the constant.")]
    expl = (f"Between rows, y changes by {_m(ys[1] - ys[0])} when x changes by {xs[1] - xs[0]}: slope {_m(m)}. "
            f"Then {_m(ys[0])} = {_m(m)}·{xs[0]} + b gives b = {_m(b)}: {correct}.")
    return _text_mc(rng, prompt, correct, ds, subskill="two_variable", explanation=expl,
                    qtype="data_interpretation", tags=["algebra", "linear", "table"], est=85,
                    stimulus=stim, verify=f"y={m}x+({b})")


_RATE_CTX = [("A tank is being filled at a constant rate. After {t1} minutes it holds {v1} liters, and after {t2} minutes it holds {v2} liters.", "liters per minute", "liters"),
             ("A car travels at a constant speed. After {t1} hours it has gone {v1} miles, and after {t2} hours it has gone {v2} miles.", "miles per hour", "miles"),
             ("A printer works at a constant rate. After {t1} minutes it has printed {v1} pages, and after {t2} minutes it has printed {v2} pages.", "pages per minute", "pages"),
             ("A plant grows at a constant rate. On day {t1} it was {v1} centimeters tall, and on day {t2} it was {v2} centimeters tall.", "centimeters per day", "centimeters")]


def le_rate_word(rng, d):
    """Two-step word problem: find the constant rate (or start value) from two readings."""
    setup, unit, qty = rng.choice(_RATE_CTX)
    r = rng.randint(2, 40)
    b = rng.randint(0, 80) if d != "easy" else 0
    t1 = rng.randint(1, 8)
    t2 = t1 + rng.randint(2, 10)
    v1, v2 = r * t1 + b, r * t2 + b
    prompt = setup.format(t1=t1, v1=v1, t2=t2, v2=v2)
    if d == "easy":
        prompt += f" What is the rate, in {unit}?"
        val = r
        expl = f"Rate = change ÷ time = ({v2} − {v1})/({t2} − {t1}) = {v2 - v1}/{t2 - t1} = {r}."
        ds = [(Fraction(v2, t2), "That works only if the amount was 0 at time 0; use the change between the two readings." if b else "Recheck: ({0} − {1})/({2} − {3}).".format(v2, v1, t2, t1)), (v2 - v1, "Divide the change by the time elapsed."), (Fraction(v1, t1), "Use both readings."), (r + 1, "Arithmetic slip.")]
    elif d == "medium":
        prompt += f" What is the rate, in {unit}?"
        val = r
        expl = f"Rate = ({v2} − {v1})/({t2} − {t1}) = {v2 - v1}/{t2 - t1} = {r} (the starting amount {b} cancels)."
        ds = [(Fraction(v2, t2), "That divides the total by the total time, ignoring the starting amount."), (v2 - v1, "Divide the change by the time elapsed."), (Fraction(v1, t1), "That ignores the starting amount; use the change between the readings."), (Fraction(v2 - v1, t2), "Divide by the elapsed time {0} − {1}, not {0}.".format(t2, t1))]
    else:
        prompt += f" How many {qty} were there at time 0?"
        val = b
        expl = f"Rate = ({v2} − {v1})/({t2} − {t1}) = {r}; starting amount = {v1} − {r}·{t1} = {b}."
        ds = [(v1, "That is the amount at time {0}, not time 0.".format(t1)), (r, "That is the rate, not the starting amount."), (v1 - r, "Subtract the rate times {0}, not the rate once.".format(t1)), (b + r, "Arithmetic slip.")]
    return _numeric_mc(rng, prompt, val, ds, subskill="two_variable", explanation=expl,
                       tags=["algebra", "linear", "rate", "word-problem"], est=90,
                       qtype="multi_step_math", verify=f"v={r}t+{b}")


def le_fraction_eq(rng, d):
    """Equations with fractions: (x + a)/b = c; x/a + x/b = c; (ax + b)/c = (dx + e)/f."""
    if d == "easy":
        bden = rng.randint(2, 9)
        a = rng.choice([v for v in range(-12, 13) if v])
        c = rng.choice([v for v in range(-8, 9) if v])
        x = c * bden - a
        eq = f"(x {_pm(a)})/{bden} = {_m(c)}"
        expl = f"Multiply both sides by {bden}: x {_pm(a)} = {_m(c * bden)}, so x = {_m(x)}."
        ds = [(c - a, "Multiply by {0} before subtracting {1}.".format(bden, _m(a))), (c * bden + a, "Subtract {0}; don't add it.".format(_m(a))), (-x if x else x + 1, "Sign slip."), (Fraction(c, bden) - a, "Multiply by {0}, don't divide.".format(bden))]
    elif d == "medium":
        p, q = rng.choice([(2, 3), (2, 5), (3, 4), (3, 5), (4, 5), (2, 7), (3, 7), (5, 6), (4, 7), (5, 7), (3, 8), (5, 8)])
        k = rng.choice([v for v in range(-6, 7) if v])
        x = p * q * k
        c = k * (p + q)
        eq = f"x/{p} + x/{q} = {_m(c)}"
        expl = f"Multiply by {p * q}: {q}x + {p}x = {_m(c * p * q)}, so {p + q}x = {_m(c * p * q)} and x = {_m(x)}."
        ds = [(Fraction(c, Fraction(1, p) + Fraction(1, q)) * 2 if False else c * (p + q), "Multiply by the common denominator, then divide by {0}.".format(p + q)), (Fraction(c * p * q, p * q), "After clearing denominators, divide by {0}, not {1}.".format(p + q, p * q)), (-x if x else x + 2, "Sign slip."), (c * p * q, "Divide by {0}x's coefficient, {0}.".format(p + q))]
    else:
        a, c, dd, f = rng.randint(2, 7), rng.randint(2, 5), rng.randint(1, 6), rng.randint(2, 5)
        if a * f == dd * c:
            dd += 1
        b, e = rng.choice([v for v in range(-9, 10) if v]), rng.choice([v for v in range(-9, 10) if v])
        # (ax + b)/c = (dx + e)/f -> f(ax + b) = c(dx + e) -> (fa - cd)x = ce - fb
        num, den = c * e - f * b, f * a - c * dd
        x = Fraction(num, den)
        eq = f"({_lin(a, b)})/{c} = ({_lin(dd, e)})/{f}"
        expl = f"Cross-multiply: {f}({_lin(a, b)}) = {c}({_lin(dd, e)}) → {_m(f * a)}x {_pm(f * b)} = {_m(c * dd)}x {_pm(c * e)} → {_m(den)}x = {_m(num)} → x = {num_str(x)}."
        ds = [(Fraction(num, f * a + c * dd), "Subtract the x-terms; don't add them."), (Fraction(c * e + f * b, den), "The constant moves with the opposite sign."), (-x if x else x + 1, "Sign slip."), (Fraction(den, num) if num else x + 2, "This inverts the final division.")]
    return _numeric_mc(rng, _ask(rng, eq), x, ds, subskill="one_variable", explanation=expl,
                       tags=["algebra", "linear", "fractions"], est=85, verify=f"x={num_str(x)} in {eq.replace(chr(8722), '-')}")


# ---- linear_inequalities ------------------------------------------------- #
def li_not_solution(rng, d):
    """Which value is NOT a solution of an inequality (numeric options)."""
    a = rng.randint(2, 9)
    b = rng.choice([v for v in range(-20, 21) if v])
    x0 = rng.randint(-8, 10)
    if d == "easy":
        sym = rng.choice(["<", "≤", ">", "≥"])
        ineq = f"{_lin(a, b)} {sym} {_m(a * x0 + b)}"
        ok = {"<": lambda x: x < x0, "≤": lambda x: x <= x0, ">": lambda x: x > x0, "≥": lambda x: x >= x0}[sym]
    elif d == "medium":
        sym = rng.choice(["<", "≤", ">", "≥"])
        ineq = f"{_lin(-a, b)} {sym} {_m(-a * x0 + b)}"
        flip = {"<": ">", "≤": "≥", ">": "<", "≥": "≤"}[sym]
        ok = {"<": lambda x: x < x0, "≤": lambda x: x <= x0, ">": lambda x: x > x0, "≥": lambda x: x >= x0}[flip]
        sym = flip
    else:
        w = rng.randint(2, 8)
        lo, hi = x0, x0 + w
        ineq = f"{_m(a * lo + b)} ≤ {_lin(a, b)} < {_m(a * hi + b)}"
        ok = lambda x: lo <= x < hi
    cands = list(range(x0 - 10, x0 + 12))
    goods = [x for x in cands if ok(x)]
    bads = [x for x in cands if not ok(x)]
    bad = rng.choice([x for x in bads if abs(x - x0) <= 3] or bads)
    picks = rng.sample(goods, 4) if len(goods) >= 4 else goods
    prompt = rng.choice([f"Which of the following is NOT a solution to the inequality {ineq}?",
                         f"Each of the following values of x satisfies {ineq} EXCEPT"])
    sol = (f"x {sym} {_m(x0)}" if d != "hard" else f"{_m(lo)} ≤ x < {_m(hi)}")
    expl = f"Solving gives {sol}. The value {_m(bad)} does not satisfy this, while the other choices do."
    ds = [(x, f"x = {_m(x)} satisfies {sol}.") for x in picks]
    return _numeric_mc(rng, prompt, bad, ds, subskill="one_variable", explanation=expl,
                       tags=["algebra", "inequality", "not-solution"], est=80, verify=f"solution {sol.replace(chr(8722), '-')}; not {bad}")


def li_compound(rng, d):
    """Compound inequalities: solve, count integers, or express as a single statement."""
    a = rng.randint(2, 8)
    b = rng.choice([v for v in range(-12, 13) if v])
    lo_x = rng.randint(-8, 6)
    hi_x = lo_x + rng.randint(2, 9)
    lo, hi = a * lo_x + b, a * hi_x + b
    if d == "easy":
        ineq = f"{_m(lo)} < {_lin(a, b)} < {_m(hi)}"
        correct = f"{_m(lo_x)} < x < {_m(hi_x)}"
        ds = [(f"{_m(lo - b)} < x < {_m(hi - b)}", "Divide every part by {0} as well.".format(a)), (f"{_m(hi_x)} < x < {_m(lo_x)}", "The smaller bound goes on the left."), (f"{_m(-hi_x)} < x < {_m(-lo_x)}", "Sign slip."), (f"{_m(lo_x)} ≤ x ≤ {_m(hi_x)}", "The inequalities are strict (<), so the endpoints are excluded.")]
        expl = f"Subtract {_m(b)} from all three parts: {_m(lo - b)} < {a}x < {_m(hi - b)}; divide by {a}: {correct}."
        prompt = f"Which of the following describes all values of x that satisfy {ineq}?"
        return _text_mc(rng, prompt, correct, ds, subskill="one_variable", explanation=expl, tags=["algebra", "inequality", "compound"], est=80, verify=correct.replace("−", "-"))
    if d == "medium":
        ineq = f"{_m(lo)} ≤ {_lin(a, b)} ≤ {_m(hi)}"
        prompt = f"How many integer values of x satisfy {ineq}?"
        val = hi_x - lo_x + 1
        expl = f"Subtract {_m(b)} and divide by {a}: {_m(lo_x)} ≤ x ≤ {_m(hi_x)}, which contains {val} integers."
        ds = [(val - 1, "Both endpoints are included (≤)."), (val + 1, "Count from {0} to {1} inclusive.".format(_m(lo_x), _m(hi_x))), (hi - lo, "Divide by {0} before counting.".format(a)), (hi_x, "Count the integers in the interval, not the endpoint.")]
        return _numeric_mc(rng, prompt, val, ds, subskill="one_variable", explanation=expl, tags=["algebra", "inequality", "compound"], est=85, verify=f"{lo_x}<=x<={hi_x}")
    # hard: "or" compound from absolute-value-free statement; find the least/greatest excluded integer
    c = rng.choice([v for v in range(-12, 13) if v])
    p, q = rng.randint(2, 6), rng.randint(2, 6)
    r1 = rng.randint(-6, 4)
    r2 = r1 + rng.randint(2, 8)
    # p x + c < p r1 + c  or  q x - c > q r2 - c  -> x < r1 or x > r2
    ineq = f"{_lin(p, c)} < {_m(p * r1 + c)} or {_lin(q, -c)} > {_m(q * r2 - c)}"
    prompt = f"Which of the following integers is NOT a solution to the compound inequality {ineq}?"
    val = rng.randint(r1, r2)
    goods = [x for x in range(r1 - 6, r2 + 7) if x < r1 or x > r2]
    picks = rng.sample(goods, 4)
    expl = f"The first part gives x < {_m(r1)} and the second gives x > {_m(r2)}; values from {_m(r1)} to {_m(r2)} satisfy neither, so {_m(val)} is not a solution."
    ds = [(x, f"x = {_m(x)} satisfies {'x < ' + _m(r1) if x < r1 else 'x > ' + _m(r2)}.") for x in picks]
    return _numeric_mc(rng, prompt, val, ds, subskill="one_variable", explanation=expl, tags=["algebra", "inequality", "compound"], est=95, verify=f"x<{r1} or x>{r2}; not {val}")


def li_interpret(rng, d):
    """Interpret an inequality model in context (text options)."""
    ctx = rng.choice([
        ("A caterer charges ${p} per guest and has a ${f} setup fee. {name} can spend at most ${B}.", "{p}g + {f} ≤ {B}", "g", "guests", "the number of guests"),
        ("A ride-share costs ${f} plus ${p} per mile. {name} has budgeted at most ${B} for the trip.", "{p}m + {f} ≤ {B}", "m", "miles", "the number of miles"),
        ("A club pays ${f} to rent a hall and ${p} per attendee for food, with a total budget of at most ${B}.", "{p}n + {f} ≤ {B}", "n", "attendees", "the number of attendees")])
    name = rng.choice(NAMES)
    p, f = rng.randint(3, 40), rng.randint(20, 200)
    nmax = rng.randint(5, 60)
    B = p * nmax + f + rng.randint(0, p - 1)
    setup = ctx[0].format(p=p, f=f, B=B, name=name)
    ineq = ctx[1].format(p=p, f=f, B=B)
    var, unit, meaning = ctx[2], ctx[3], ctx[4]
    if d == "easy":
        prompt = f"{setup} The inequality {ineq} models the situation. What does the variable {var} represent?"
        correct = meaning
        ds = [(f"the total cost, in dollars", "The total cost is the left side of the inequality, not the variable."), (f"the cost per {unit[:-1]}, in dollars", f"That is the coefficient {p}."), (f"the fixed fee, in dollars", f"That is the constant {f}."), (f"the budget, in dollars", f"That is the right side, {B}.")]
        expl = f"{p}{var} is the variable cost, so {var} counts the {unit}: {correct}."
    elif d == "medium":
        prompt = f"{setup} The inequality {ineq} models the situation. Which of the following is the best interpretation of the number {f}?"
        correct = f"the fixed cost, in dollars, that is paid regardless of the number of {unit}"
        ds = [(f"the cost, in dollars, for each additional {unit[:-1]}", f"That describes the coefficient {p}."), (f"the greatest number of {unit} that can be afforded", f"That would be found by solving; it is {nmax}."), (f"the total amount, in dollars, that can be spent", f"That is the right side, {B}."), (f"the number of {unit} that cost ${f} in all", "The constant is a dollar amount, not a count.")]
        expl = f"The constant term is paid once no matter how many {unit}: {correct}."
    else:
        prompt = f"{setup} Based on the inequality {ineq}, what is the greatest number of {unit} possible?"
        val = nmax
        expl = f"{p}{var} ≤ {B} − {f} = {B - f}, so {var} ≤ {(B - f) / p:.2f}; the greatest whole number is {nmax}."
        ds = [(nmax + 1, "That many would exceed the budget."), (B // p, "Subtract the fixed fee before dividing."), (nmax - 1, "One more still fits the budget."), ((B + f) // p, "Subtract the fee; don't add it.")]
        return _numeric_mc(rng, prompt, val, ds, subskill="one_variable", explanation=expl, tags=["algebra", "inequality", "interpret"], est=85, verify=f"max={nmax}")
    return _text_mc(rng, prompt, correct, ds, subskill="one_variable", explanation=expl, tags=["algebra", "inequality", "interpret"], est=80, verify=f"interpret {ineq}")


# ---- systems_of_equations -------------------------------------------------- #
def sys_intersection_point(rng, d):
    """Give the full intersection point (text options)."""
    x, y = rng.randint(-8, 9), rng.randint(-8, 9)
    if d == "easy":
        m1 = rng.choice([v for v in range(-5, 6) if v])
        m2 = rng.choice([v for v in range(-5, 6) if v not in (0, m1)])
        b1, b2 = y - m1 * x, y - m2 * x
        e1, e2 = f"y = {_lin(m1, b1)}", f"y = {_lin(m2, b2)}"
        expl = f"Set {_lin(m1, b1)} = {_lin(m2, b2)}: x = {_m(x)}; then y = {_m(y)}."
    elif d == "medium":
        m1 = rng.choice([v for v in range(-5, 6) if v])
        a2, b2c = rng.choice([v for v in range(1, 7)]), rng.choice([v for v in range(-6, 7) if v])
        b1 = y - m1 * x
        c2 = a2 * x + b2c * y
        if a2 + b2c * m1 == 0:
            return sys_intersection_point(rng, d)
        e1 = f"y = {_lin(m1, b1)}"
        e2 = f"{_lin(a2, 0)} {'+' if b2c > 0 else '−'} {_coef(abs(b2c), 'y')} = {_m(c2)}"
        expl = f"Substitute y = {_lin(m1, b1)} into the second equation and solve: x = {_m(x)}, y = {_m(y)}."
    else:
        a1, b1c = rng.randint(2, 7), rng.choice([v for v in range(-7, 8) if v])
        a2, b2c = rng.randint(2, 7), rng.choice([v for v in range(-7, 8) if v])
        if a1 * b2c - a2 * b1c == 0:
            return sys_intersection_point(rng, d)
        c1, c2 = a1 * x + b1c * y, a2 * x + b2c * y
        e1 = f"{_lin(a1, 0)} {'+' if b1c > 0 else '−'} {_coef(abs(b1c), 'y')} = {_m(c1)}"
        e2 = f"{_lin(a2, 0)} {'+' if b2c > 0 else '−'} {_coef(abs(b2c), 'y')} = {_m(c2)}"
        expl = f"Eliminate one variable (multiply and subtract): x = {_m(x)}, y = {_m(y)}."
    prompt = rng.choice([f"{e1}\n{e2}\nWhat is the solution (x, y) to the system of equations above?",
                         f"In the xy-plane, the graphs of {e1} and {e2} intersect at which point?"])
    correct = f"({_m(x)}, {_m(y)})"
    ds = [(f"({_m(y)}, {_m(x)})" if x != y else f"({_m(x + 1)}, {_m(y)})", "The coordinates are reversed." if x != y else "Arithmetic slip."),
          (f"({_m(-x)}, {_m(y)})" if x else f"({_m(x + 2)}, {_m(y)})", "Sign slip in x."),
          (f"({_m(x)}, {_m(-y)})" if y else f"({_m(x)}, {_m(y + 2)})", "Sign slip in y."),
          (f"({_m(x + 1)}, {_m(y - 1)})", "Substitute back: this pair fails at least one equation.")]
    return _text_mc(rng, prompt, correct, ds, subskill="substitution", explanation=expl, qtype="multi_step_math",
                    tags=["algebra", "systems", "intersection"], est=95, verify=f"({x},{y})")


def sys_dependent(rng, d):
    """Which system has no/infinitely many solutions (easy); k for infinitely many (medium); p+q (hard)."""
    a, b = rng.randint(2, 9), rng.choice([v for v in range(2, 10)])
    c = rng.randint(1, 40)
    k = rng.randint(2, 4)
    if d == "easy":
        want = rng.choice(["no solution", "infinitely many solutions"])
        base = f"{a}x + {b}y = {c}"
        same = f"{k * a}x + {k * b}y = {k * c}"
        para = f"{k * a}x + {k * b}y = {k * c + rng.randint(1, 9)}"
        one1 = f"{k * a}x + {k * b + rng.randint(1, 5)}y = {k * c}"
        one2 = f"{a}x − {b}y = {c}"
        correct = same if want == "infinitely many solutions" else para
        ds = [(para if want == "infinitely many solutions" else same, "The coefficients are proportional " + ("but the constants are not: parallel lines, no solution." if want == "infinitely many solutions" else "and so are the constants: the same line, infinitely many solutions.")),
              (one1, "The slopes differ, so the lines meet exactly once."), (one2, "The slopes differ, so the lines meet exactly once.")]
        prompt = f"Which of the following equations, together with {base}, forms a system that has {want}?"
        expl = (f"{correct} is {k} times {base}: the same line, so infinitely many solutions." if want == "infinitely many solutions"
                else f"{correct} has the same left side as {k}·({base}) but a different constant: parallel lines, no solution.")
        return _text_mc(rng, prompt, correct, ds, subskill="elimination", explanation=expl, tags=["algebra", "systems", "dependent"], est=85, verify=want)
    if d == "medium":
        prompt = f"{a}x + {b}y = {c}\n{k * a}x + ky = {k * c}\nIn the system of equations above, k is a constant. If the system has infinitely many solutions, what is the value of k?"
        val = k * b
        expl = f"Infinitely many solutions means the second equation is a multiple of the first; {k * a}/{a} = {k}, so k = {k}·{b} = {val}."
        ds = [(b, "k must be scaled by the same factor {0} as the other coefficients.".format(k)), (k, "That is the scale factor, not k."), (k * c, "k multiplies y; compare it with {0}, not {1}.".format(b, c)), (Fraction(b, k), "Multiply by {0}; don't divide.".format(k))]
        return _numeric_mc(rng, prompt, val, ds, subskill="elimination", explanation=expl, tags=["algebra", "systems", "dependent"], est=90, verify=f"k={val}")
    prompt = f"{a}x + {b}y = {c}\npx + qy = {k * c}\nIn the system of equations above, p and q are constants. If the system has infinitely many solutions, what is the value of p + q?"
    val = k * (a + b)
    expl = f"The second equation must be {k} times the first (since {k * c} = {k}·{c}): p = {k * a}, q = {k * b}, so p + q = {val}."
    ds = [(a + b, "Scale by the factor {0} = {1}/{2}.".format(k, k * c, c)), (k * a, "That is p alone."), (k * b, "That is q alone."), (k * (a + b) + k, "Arithmetic slip.")]
    return _numeric_mc(rng, prompt, val, ds, subskill="elimination", explanation=expl, tags=["algebra", "systems", "dependent"], est=100, verify=f"p+q={val}")


def sys_rate_word(rng, d):
    """System word problems with rates/mixtures that ask for a derived quantity."""
    name = rng.choice(NAMES)
    if d == "easy":
        h, w = rng.randint(3, 12), rng.randint(2, 8)
        prompt = f"{name} works two jobs. One week, {name} worked {h + w} hours in all, working {h - w} more hours at the first job than at the second. How many hours did {name} work at the first job?"
        val = h
        expl = f"a + b = {h + w} and a − b = {h - w}; adding gives 2a = {2 * h}, so a = {h}."
        ds = [(w, "That is the hours at the second job."), ((h + w) // 2, "Splitting evenly ignores the difference."), (h + w - (h - w), "That is twice the second job's hours."), (h + 1, "Arithmetic slip.")]
    elif d == "medium":
        pa, pb = rng.randint(2, 6), rng.randint(7, 15)
        na, nb = rng.randint(3, 20), rng.randint(3, 20)
        prompt = (f"A vending machine sells snacks for ${pa} and drinks for ${pb}. In one day it sold {na + nb} items for a total of "
                  f"${pa * na + pb * nb}. How much money, in dollars, came from drinks?")
        val = pb * nb
        expl = f"s + d = {na + nb}, {pa}s + {pb}d = {pa * na + pb * nb} → d = {nb}; drinks brought in {pb}·{nb} = ${val}."
        ds = [(nb, "That is the number of drinks, not the money."), (pa * na, "That is the money from snacks."), (pb * na, "That uses the number of snacks."), (val + pb, "Arithmetic slip.")]
    else:
        r1, r2 = rng.randint(3, 9), rng.randint(10, 20)
        t1, t2 = rng.randint(2, 8), rng.randint(2, 8)
        prompt = (f"{name} jogged at {r1} miles per hour and then cycled at {r2} miles per hour, covering {r1 * t1 + r2 * t2} miles in {t1 + t2} hours. "
                  f"How many miles did {name} cycle?")
        val = r2 * t2
        expl = f"j + c = {t1 + t2} and {r1}j + {r2}c = {r1 * t1 + r2 * t2} → c = {t2} hours; cycling distance = {r2}·{t2} = {val} miles."
        ds = [(t2, "That is the cycling time in hours, not the distance."), (r1 * t1, "That is the jogging distance."), (r2 * t1, "That uses the jogging time."), (val - r2, "Arithmetic slip.")]
    return _numeric_mc(rng, prompt, val, ds, subskill="substitution", explanation=expl, qtype="multi_step_math",
                       tags=["algebra", "systems", "word-problem"], est=100, verify=f"val={val}")


# ---- functions ------------------------------------------------------------- #
def fn_rate_of_change(rng, d):
    """Average rate of change of a function between two inputs."""
    x1 = rng.randint(-5, 5)
    x2 = x1 + rng.randint(1, 6)
    if d == "easy":
        m, b = rng.choice([v for v in range(-8, 9) if v]), rng.randint(-10, 10)
        rule = _fx(m, b)
        val = m
        prompt = f"The function f is defined by f(x) = {rule}. What is the average rate of change of f between x = {_m(x1)} and x = {_m(x2)}?"
        expl = f"For a linear function the average rate of change is the slope, {_m(m)}: (f({_m(x2)}) − f({_m(x1)}))/({_m(x2)} − {_m(x1)}) = {_m(m)}."
        ds = [(b, "That is the y-intercept, not the rate of change."), (-m, "Sign slip."), (m * (x2 - x1), "Divide the change in f by the change in x."), (m + b, "That is f(1), not the rate.")]
    else:
        a = rng.choice([1, 2, 3, -1, -2]) if d == "hard" else 1
        bq, c = rng.randint(-6, 6), rng.randint(-10, 10)
        rule = _fx(a, bq, c)
        f1, f2 = a * x1 * x1 + bq * x1 + c, a * x2 * x2 + bq * x2 + c
        val = Fraction(f2 - f1, x2 - x1)
        prompt = rng.choice([f"The function f is defined by f(x) = {rule}. What is the average rate of change of f over the interval from x = {_m(x1)} to x = {_m(x2)}?",
                             f"If f(x) = {rule}, what is the average rate of change of f between x = {_m(x1)} and x = {_m(x2)}?"])
        expl = f"f({_m(x1)}) = {_m(f1)} and f({_m(x2)}) = {_m(f2)}; average rate = ({_m(f2)} − ({_m(f1)}))/({_m(x2)} − ({_m(x1)})) = {num_str(val)}."
        ds = [(f2 - f1, "Divide by the change in x."), (Fraction(f2, x2) if x2 else val + 1, "Use the change in f over the change in x, not f(x₂)/x₂."), (-val if val else val + 1, "Sign slip."), (Fraction(f1 + f2, 2), "Average rate of change is not the average of the outputs.")]
    return _numeric_mc(rng, prompt, val, ds, subskill="interpret", explanation=expl, tags=["functions", "rate-of-change"], est=80 if d == "easy" else 95, verify=f"rate={num_str(val)}")


def fn_graph_point(rng, d):
    """Graph facts: a point on the graph determines a constant; points on y = f(x)."""
    if d == "easy":
        m = rng.choice([v for v in range(-7, 8) if v])
        x0 = rng.choice([v for v in range(-6, 7) if v])
        k = rng.choice([v for v in range(-12, 13) if v])
        y0 = m * x0 + k
        prompt = f"The graph of f(x) = {_lin(m, 0)} + k in the xy-plane passes through the point ({_m(x0)}, {_m(y0)}). What is the value of the constant k?"
        val = k
        expl = f"Substitute: {_m(y0)} = {_m(m)}({_m(x0)}) + k, so k = {_m(y0)} − ({_m(m * x0)}) = {_m(k)}."
        ds = [(y0 + m * x0, "Subtract {0}; don't add it.".format(_m(m * x0))), (-k if k else k + 1, "Sign slip."), (y0, "That is the y-coordinate of the point, not k."), (Fraction(y0, m) - x0, "k is added, not multiplied, so don't divide by m.")]
    elif d == "medium":
        c = rng.choice([v for v in range(-9, 10) if v])
        xs = rng.sample(range(-5, 6), 5)
        good = (xs[0], xs[0] ** 2 + c)
        bads = [(x, x * x + c + rng.choice([-3, -2, -1, 1, 2, 3])) for x in xs[1:]]
        prompt = f"Which of the following points lies on the graph of y = x² {_pm(c)} in the xy-plane?"
        correct = f"({_m(good[0])}, {_m(good[1])})"
        ds = [(f"({_m(x)}, {_m(y)})", f"At x = {_m(x)}, y = {_m(x * x + c)}, not {_m(y)}.") for x, y in bads]
        expl = f"Substitute x = {_m(good[0])}: y = ({_m(good[0])})² {_pm(c)} = {_m(good[1])}."
        return _text_mc(rng, prompt, correct, ds, subskill="evaluate", explanation=expl, tags=["functions", "graph"], est=75, verify=correct)
    else:
        a = rng.choice([1, 2, 3, -1, -2])
        b = rng.choice([v for v in range(-6, 7) if v])
        c = rng.randint(-9, 9)
        f0, f1, f2 = c, a + b + c, 4 * a + 2 * b + c
        which = rng.choice(["a", "b"])
        prompt = f"The function f is defined by f(x) = ax² + bx + c, where a, b, and c are constants. If f(0) = {_m(f0)}, f(1) = {_m(f1)}, and f(2) = {_m(f2)}, what is the value of {which}?"
        val = a if which == "a" else b
        expl = f"f(0) = c = {_m(c)}. Then a + b = {_m(f1 - c)} and 4a + 2b = {_m(f2 - c)}; solving gives a = {_m(a)}, b = {_m(b)}."
        ds = [(b if which == "a" else a, f"That is {'b' if which == 'a' else 'a'}."), (c, "That is c = f(0)."), (f1 - c, "That is a + b, not a single constant."), (-val if val else val + 1, "Sign slip.")]
    return _numeric_mc(rng, prompt, val, ds, subskill="interpret", explanation=expl, tags=["functions", "graph"], est=80 if d == "easy" else 100, qtype="multi_step_math" if d == "hard" else "multiple_choice", verify=f"val={val}")


# ---- quadratics ---------------------------------------------------------- #
def q_complete_square(rng, d):
    """Vertex form from standard form (text options), or read the vertex from completed square."""
    h = rng.choice([v for v in range(-9, 10) if v])
    k = rng.choice([v for v in range(-20, 21) if v])
    if d == "easy":
        b, c = -2 * h, h * h + k
        prompt = f"Which of the following is equivalent to {_fx(1, b, c)}?"
        correct = f"(x {_pm(-h)})² {_pm(k)}"
        ds = [(f"(x {_pm(h)})² {_pm(k)}", "The sign inside the parentheses is wrong: (x − h)² expands to x² − 2hx + h²."), (f"(x {_pm(-h)})² {_pm(c)}", "Subtract h² = {0} from the constant.".format(h * h)), (f"(x {_pm(-h)})² {_pm(-k)}", "Check the sign of the constant after completing the square."), (f"(x {_pm(-2 * h)})² {_pm(k)}", "Half of the x-coefficient goes inside the parentheses.")]
        expl = f"x² {_pm(b)}x = (x {_pm(-h)})² − {h * h}; so the expression is (x {_pm(-h)})² {_pm(c)} − {h * h} = {correct}."
    elif d == "medium":
        a = rng.choice([2, 3, -1, -2])
        b, c = -2 * a * h, a * h * h + k
        prompt = f"Which of the following is equivalent to {_fx(a, b, c)}?"
        correct = f"{_m(a)}(x {_pm(-h)})² {_pm(k)}"
        ds = [(f"{_m(a)}(x {_pm(h)})² {_pm(k)}", "Sign inside the parentheses is wrong."), (f"{_m(a)}(x {_pm(-h)})² {_pm(c)}", "Subtract a·h² = {0} from the constant.".format(_m(a * h * h))), (f"{_m(a)}(x {_pm(-h)})² {_pm(c - h * h)}", "Subtract a·h², not h²."), (f"(x {_pm(-h)})² {_pm(k)}", "The leading coefficient {0} must stay.".format(_m(a)))]
        expl = f"Factor {_m(a)} from the x-terms: {_m(a)}(x² {_pm(-2 * h)}x) {_pm(c)} = {_m(a)}(x {_pm(-h)})² − {_m(a * h * h)} {_pm(c)} = {correct}."
    else:
        a = rng.choice([1, 2, 3, -1, -2, 4])
        b, c = -2 * a * h, a * h * h + k
        prompt = f"The function f is defined by f(x) = {_fx(a, b, c)}. When f(x) is written in the form a(x − h)² + k, what is the value of k?"
        val = k
        expl = f"h = −b/(2a) = {_m(h)}; k = f({_m(h)}) = {_m(a)}({_m(h)})² {_pm(b)}({_m(h)}) {_pm(c)} = {_m(k)}."
        ds = [(h, "That is h, not k."), (c, "k is f(h), not the constant c."), (-k if k else k + 1, "Sign slip."), (c - h * h, "Subtract a·h², not h², from c.")]
        return _numeric_mc(rng, prompt, val, ds, subskill="vertex", explanation=expl, tags=["quadratics", "vertex-form"], est=100, verify=f"h={h},k={k}")
    return _text_mc(rng, prompt, correct, ds, subskill="vertex", explanation=expl, tags=["quadratics", "vertex-form"], est=85, verify=correct)


def q_word(rng, d):
    """Quadratic word problems: rectangle dimensions, consecutive integers, bordered garden."""
    if d == "easy":
        w = rng.randint(3, 15)
        k = rng.randint(1, 9)
        A = w * (w + k)
        prompt = f"The length of a rectangle is {k} more than its width, and its area is {A}. What is the width of the rectangle?"
        val = w
        expl = f"w(w + {k}) = {A} → w² + {k}w − {A} = 0 → (w − {w})(w + {w + k}) = 0 → w = {w}."
        ds = [(w + k, "That is the length."), (A // k if A % k == 0 and A // k != w else w + 2, "Set up w(w + k) = A; don't divide the area by {0}.".format(k)), (w + 1, "Check: {0}·{1} ≠ {2}.".format(w + 1, w + 1 + k, A)), (A // 2 - w if A // 2 - w not in (w, w + k) else w - 1, "Area, not perimeter, is given.")]
    elif d == "medium":
        n = rng.randint(3, 60)
        prod = n * (n + 1)
        if rng.random() < 0.5:
            prompt = rng.choice([f"The product of two consecutive positive integers is {prod}. What is the larger integer?",
                                 f"Two consecutive positive integers have a product of {prod}. What is the greater of the two?"])
            val = n + 1
            expl = f"n(n + 1) = {prod} → n² + n − {prod} = 0 → (n − {n})(n + {n + 1}) = 0 → n = {n}; the larger is {n + 1}."
            ds = [(n, "That is the smaller integer."), (prod // 2, "The integers multiply to {0}; halving isn't the way.".format(prod)), (n + 2, "Check: {0}·{1} ≠ {2}.".format(n + 1, n + 2, prod)), (math.isqrt(prod), "That is √{0} rounded down; the integers are {1} and {2}.".format(prod, n, n + 1))]
        else:
            m = rng.randint(3, 45)
            s2 = m * m + (m + 1) ** 2
            prompt = rng.choice([f"The sum of the squares of two consecutive positive integers is {s2}. What is the smaller integer?",
                                 f"If n and n + 1 are positive integers with n² + (n + 1)² = {s2}, what is n?"])
            val = m
            expl = f"n² + (n + 1)² = {s2} → 2n² + 2n + 1 = {s2} → n² + n − {(s2 - 1) // 2} = 0 → n = {m}."
            ds = [(m + 1, "That is the larger integer."), (math.isqrt(s2 // 2), "Set up the equation; don't halve and take a root."), (m - 1, "Check: {0}² + {1}² ≠ {2}.".format(m - 1, m, s2)), (s2 // 2 - m if s2 // 2 - m not in (m, m + 1) else m + 2, "Both squares are included in the sum.")]
    else:
        L, W = rng.randint(6, 20), rng.randint(4, 15)
        x = rng.randint(1, 4)
        total = (L + 2 * x) * (W + 2 * x)
        prompt = (f"A rectangular garden measures {L} feet by {W} feet and is surrounded by a path of uniform width. "
                  f"If the garden and path together cover {total} square feet, what is the width of the path, in feet?")
        val = x
        expl = f"({L} + 2x)({W} + 2x) = {total} → 4x² + {2 * (L + W)}x + {L * W} = {total} → 4x² + {2 * (L + W)}x − {total - L * W} = 0 → x = {x}."
        ds = [(2 * x, "The path adds 2x to each dimension, but its width is x."), (x + 1, "Check: ({0})({1}) ≠ {2}.".format(L + 2 * (x + 1), W + 2 * (x + 1), total)), ((total - L * W) // (2 * (L + W)), "The x² term matters; solve the quadratic."), (x + 2, "Arithmetic slip.")]
        return _numeric_mc(rng, prompt, val, ds, subskill="roots", explanation=expl, qtype="multi_step_math", tags=["quadratics", "word-problem"], est=110, verify=f"x={x}")
    return _numeric_mc(rng, prompt, val, ds, subskill="roots", explanation=expl, qtype="multi_step_math", tags=["quadratics", "word-problem"], est=95, verify=f"val={val}")


def q_intercepts(rng, d):
    """Intercepts of a parabola; number of x-intercepts; axis of symmetry from intercepts."""
    r1 = rng.randint(-9, 9)
    r2 = rng.choice([v for v in range(-9, 10) if v != r1])
    if d == "easy":
        prompt = f"The graph of y = (x {_pm(-r1)})(x {_pm(-r2)}) in the xy-plane has x-intercepts at x = p and x = q. What is the value of p + q?"
        val = r1 + r2
        expl = f"The x-intercepts are where each factor is 0: x = {_m(r1)} and x = {_m(r2)}; their sum is {_m(val)}."
        ds = [(-(r1 + r2) if r1 + r2 else 1, "Each factor x − r is 0 at x = r, not −r."), (r1 * r2, "That is the product of the intercepts (the y-intercept)."), (r1 - r2, "Add the intercepts; don't subtract."), (abs(r1) + abs(r2) if abs(r1) + abs(r2) != val else val + 2, "Keep the signs of the intercepts.")]
    elif d == "medium":
        prompt = f"The graph of y = (x {_pm(-r1)})(x {_pm(-r2)}) in the xy-plane crosses the y-axis at (0, c). What is the value of c?"
        val = r1 * r2
        expl = f"Set x = 0: y = ({_m(-r1)})({_m(-r2)}) = {_m(val)}."
        ds = [(r1 + r2, "That is the sum of the x-intercepts."), (-r1 * r2 if r1 * r2 else 3, "Check the signs: (−r₁)(−r₂) = r₁r₂."), (r1 if r1 != val else r2, "That is an x-intercept, not the y-intercept."), (-(r1 + r2) if -(r1 + r2) != val else val + 1, "Multiply the constants; don't add.")]
    else:
        kind = rng.choice(["axis", "vertex_from_intercepts", "count"])
        if kind == "axis":
            prompt = f"A parabola in the xy-plane has x-intercepts at x = {_m(r1)} and x = {_m(r2)}. What is the equation of its axis of symmetry?"
            mid = Fraction(r1 + r2, 2)
            correct = f"x = {num_str(mid)}"
            ds = [(f"x = {num_str(mid * 2)}", "The axis is halfway between the intercepts: divide by 2."), (f"y = {num_str(mid)}", "The axis of symmetry of y = ax² + … is a vertical line x = h."), (f"x = {num_str(-mid)}" if mid else f"x = {num_str(mid + 1)}", "Sign slip."), (f"x = {num_str(Fraction(r2 - r1, 2))}", "Average the intercepts; don't halve their difference.")]
            expl = f"The axis of symmetry passes midway between the x-intercepts: x = ({_m(r1)} + {_m(r2)})/2 = {num_str(mid)}."
            return _text_mc(rng, prompt, correct, ds, subskill="vertex", explanation=expl, tags=["quadratics", "intercepts", "symmetry"], est=85, verify=correct)
        if kind == "vertex_from_intercepts":
            a = rng.choice([1, 2, -1, -2])
            if (r1 + r2) % 2:
                r2 += 1
                if r2 == r1:
                    r2 += 2
            h = (r1 + r2) // 2
            k = a * (h - r1) * (h - r2)
            prompt = f"The graph of y = {_m(a)}(x {_pm(-r1)})(x {_pm(-r2)}) in the xy-plane has its vertex at (h, k). What is the value of k?"
            val = k
            expl = f"h is midway between the intercepts: h = {_m(h)}; k = {_m(a)}({_m(h)} − ({_m(r1)}))({_m(h)} − ({_m(r2)})) = {_m(k)}."
            ds = [(h, "That is h, not k."), (-k if k else k + 1, "Sign slip."), (a * r1 * r2, "That is the y-intercept, not the vertex's y-coordinate."), (k // a if a != 1 and k % a == 0 else k + 2, "Include the factor a = {0}.".format(_m(a)))]
            return _numeric_mc(rng, prompt, val, ds, subskill="vertex", explanation=expl, tags=["quadratics", "intercepts", "vertex"], est=100, verify=f"h={h},k={k}")
        a = rng.choice([1, 2, -1, -2])
        k = rng.choice([v for v in range(-8, 9) if v])
        h = rng.randint(-5, 5)
        prompt = f"How many x-intercepts does the graph of y = {_m(a)}(x {_pm(-h)})² {_pm(k)} have in the xy-plane?"
        val = 2 if (a > 0) != (k > 0) else 0
        expl = (f"The vertex is at ({_m(h)}, {_m(k)}) and the parabola opens {'upward' if a > 0 else 'downward'}; "
                + ("it crosses the x-axis twice." if val == 2 else "it never reaches the x-axis."))
        ds = [(2 - val, "Compare the vertex's position with the direction the parabola opens."), (1, "One intercept happens only when the vertex is on the x-axis (k = 0)."), (abs(k), "The number of intercepts is not |k|."), (3, "A parabola has at most two x-intercepts.")]
        return _numeric_mc(rng, prompt, val, ds, subskill="roots", explanation=expl, tags=["quadratics", "intercepts"], est=85, verify=f"a={a},k={k}")
    return _numeric_mc(rng, prompt, val, ds, subskill="roots", explanation=expl, tags=["quadratics", "intercepts"], est=80, verify=f"roots {r1},{r2}")


# ---- exponents_radicals -------------------------------------------------- #
def ex_radical_ops(rng, d):
    """Operations with radicals: products, sums needing simplification, rationalizing."""
    if d == "easy":
        r = rng.choice([2, 3, 5, 6, 7, 10, 11, 13])
        p, q = rng.sample([1, 2, 3, 4, 5, 6], 2)
        a, b = r * p * p, r * q * q
        if rng.random() < 0.5:
            a, b = b, a
        val = math.isqrt(a * b)
        prompt = rng.choice([f"What is the value of √{a} · √{b}?", f"Which of the following is equal to √{a} × √{b}?"])
        expl = f"√{a}·√{b} = √{a * b} = {val}."
        ds = [(a * b, "Take the square root of the product."), (a + b, "Multiply the radicands; don't add."), (val * 2, "Recheck √{0}.".format(a * b)), (math.isqrt(a) * math.isqrt(b) if math.isqrt(a) ** 2 == a and math.isqrt(b) ** 2 == b else val + 1, "Arithmetic slip.")]
        return _numeric_mc(rng, prompt, val, ds, subskill="radical_simplify", explanation=expl, tags=["radicals", "product"], est=65, verify=f"sqrt({a * b})={val}")
    if d == "medium":
        r = rng.choice([2, 3, 5, 6, 7])
        k1, k2 = rng.sample([2, 3, 4, 5, 6], 2)
        n1, n2 = k1 * k1 * r, k2 * k2 * r
        op = rng.choice(["+", "−"])
        coef = k1 + k2 if op == "+" else k1 - k2
        if coef == 0:
            return ex_radical_ops(rng, d)
        correct = f"{coef}√{r}" if abs(coef) != 1 else ("√" + str(r) if coef == 1 else f"−√{r}")
        prompt = f"Which of the following is equivalent to √{n1} {op} √{n2}?"
        ds = [(f"√{n1 + n2 if op == '+' else abs(n1 - n2)}", "Radicals don't combine by adding/subtracting the radicands."), (f"{coef}√{2 * r}", "Simplify each radical first; the radicand stays {0}.".format(r)), (f"{k1 + k2 if op == '−' else k1 - k2}√{r}" if (k1 + k2 if op == '−' else k1 - k2) != 0 else f"{coef * 2}√{r}", "Check the operation."), (f"{coef * r}", "√{0} stays in the answer.".format(r))]
        expl = f"√{n1} = {k1}√{r} and √{n2} = {k2}√{r}; {k1}√{r} {op} {k2}√{r} = {correct}."
        return _text_mc(rng, prompt, correct, ds, subskill="radical_simplify", explanation=expl, tags=["radicals", "combine"], est=85, verify=correct)
    k = rng.choice([2, 3, 5, 6, 7, 10, 11])
    a = rng.randint(1, 9)
    g = math.gcd(a, k)
    num, den = a // g, k // g
    prompt = f"Which of the following is equivalent to {a}/√{k}?"
    correct = (f"{num}√{k}/{den}" if den != 1 else f"{num}√{k}") if num != 1 else (f"√{k}/{den}" if den != 1 else f"√{k}")
    ds = [(f"{a}√{k}", "Multiplying top and bottom by √{0} leaves {0} in the denominator.".format(k)), (f"{a}/{k}", "√{0} is not {0}.".format(k)), (f"√{k}/{a}", "This inverts the fraction."), (f"{a}√{k}/{k * k}" if num != a or den != k * k else f"{a}√{k}/{k + 1}", "The denominator becomes √{0}·√{0} = {0}, not {1}.".format(k, k * k))]
    expl = f"Multiply numerator and denominator by √{k}: {a}√{k}/{k} = {correct}."
    return _text_mc(rng, prompt, correct, ds, subskill="radical_simplify", explanation=expl, tags=["radicals", "rationalize"], est=85, verify=correct)


def ex_exp_expressions(rng, d):
    """Signed bases, zero exponents, and rewriting b^(x+k) (text options)."""
    if d == "easy":
        b = rng.randint(2, 6)
        n = rng.randint(2, 5 if b <= 3 else 3)
        kind = rng.choice(["neg_paren", "neg_noparen", "zero"])
        if kind == "neg_paren":
            prompt = f"What is the value of (−{b})^{n}?"
            val = (-b) ** n
            expl = f"The parentheses mean the whole −{b} is raised to the {n}: {'positive' if n % 2 == 0 else 'negative'} result {_m(val)}."
            ds = [(-val, "Check the sign: an {0} power of a negative number is {1}.".format("even" if n % 2 == 0 else "odd", "positive" if n % 2 == 0 else "negative")), (-b * n, "Multiply repeatedly; don't multiply base by exponent."), (b ** n + b if n % 2 == 0 else -(b ** n) - b, "Arithmetic slip."), (b * n, "Use repeated multiplication.")]
        elif kind == "neg_noparen":
            prompt = f"What is the value of −{b}^{n}?"
            val = -(b ** n)
            expl = f"Without parentheses only {b} is raised to the power, then negated: −{b ** n}."
            ds = [(b ** n, "The leading minus sign applies to the result."), (-b * n, "Multiply repeatedly."), ((-b) ** n if (-b) ** n != val else -(b ** n) + 1, "The exponent applies to {0} only, not to −{0}.".format(b)), (val - b, "Arithmetic slip.")]
        else:
            k = rng.randint(2, 9)
            prompt = f"What is the value of {k}·{b}⁰ + {b}?"
            val = k + b
            expl = f"Any nonzero number to the 0 power is 1: {k}·1 + {b} = {val}."
            ds = [(b, "b⁰ = 1, not 0."), (k * b + b, "b⁰ = 1, not b."), (k + 1, "Add {0}, not 1.".format(b)), (val + 1, "Arithmetic slip.")]
        return _numeric_mc(rng, prompt, val, ds, subskill="exponent_rules", explanation=expl, tags=["exponents", "sign"], est=65, verify=f"val={val}")
    b = rng.choice([2, 3, 4, 5, 6, 7, 10])
    k = rng.randint(1, 4 if b <= 3 else 3)
    if d == "medium":
        prompt = rng.choice([f"Which of the following is equivalent to {b}^(x + {k})?",
                             f"For all real x, {b}^(x + {k}) is equal to which of the following?",
                             f"Which expression is equivalent to {b}^(x + {k}) for every value of x?"])
        correct = f"{b ** k}·{b}^x"
        ds = [(f"{b}^x + {b ** k}", "Adding exponents comes from multiplying, so the result is a product, not a sum."), (f"{b * k}·{b}^x", "{0}^{1} = {2}, not {0}·{1}.".format(b, k, b ** k)), (f"{b}^x + {k}", "The {0} is in the exponent; rewrite as a product.".format(k)), (f"({b}^x)^{k}", "That would be {0}^(kx).".format(b))]
        expl = f"{b}^(x + {k}) = {b}^x · {b}^{k} = {correct}."
    else:
        kind = rng.choice(["diff", "ratio", "sum"])
        if kind == "diff":
            prompt = f"Which of the following is equivalent to {b}^(x + {k}) − {b}^x?"
            correct = f"{b ** k - 1}·{b}^x"
            ds = [(f"{b}^{k}", "Factor {0}^x out of both terms first.".format(b)), (f"{b ** k}·{b}^x", "Subtract the {0}^x term after factoring: ({1} − 1){0}^x.".format(b, b ** k)), (f"{b}^x", "{0}^(x+{1}) is not {0}^x + something small.".format(b, k)), (f"{b ** k - 1}", "The factor {0}^x remains.".format(b))]
            expl = f"{b}^(x + {k}) − {b}^x = {b ** k}·{b}^x − {b}^x = ({b ** k} − 1)·{b}^x = {correct}."
        elif kind == "ratio":
            j = rng.randint(1, 3)
            prompt = f"Which of the following is equivalent to {b}^(x + {k})/{b}^(x − {j})?"
            correct = f"{b ** (k + j)}"
            ds = [(f"{b}^(x + {k - j})" if k != j else f"{b}^({k - j + 1})", "Subtract the exponents: (x + {0}) − (x − {1}) = {2}.".format(k, j, k + j)), (f"{b}^({k - j})" if k != j else f"{b}^0 = 0", "Subtracting a negative adds: {0} + {1}.".format(k, j)), (f"{b}^(2x + {k - j})", "Dividing subtracts exponents; the x's cancel."), (f"{b ** k}/{b ** j}" if b ** k % b ** j else f"{b ** (k + j) + 1}", "Simplify fully: {0}^{1}.".format(b, k + j))]
            expl = f"Subtract exponents: (x + {k}) − (x − {j}) = {k + j}, so the quotient is {b}^{k + j} = {correct}."
        else:
            prompt = f"If {b}^x = y, which of the following is equivalent to {b}^(x + {k}) + {b}^x in terms of y?"
            correct = f"{b ** k + 1}y"
            ds = [(f"y + {b ** k}", "{0}^(x+{1}) = {2}·{0}^x = {2}y, not y + {2}.".format(b, k, b ** k)), (f"y^{b ** k} + y", "The {0} adds to the exponent, giving a product with y, not a power of y.".format(k)), (f"{b ** k}y", "Include the + {0}^x = y term.".format(b)), (f"{b * k + 1}y", "{0}^{1} = {2}.".format(b, k, b ** k))]
            expl = f"{b}^(x + {k}) = {b ** k}·{b}^x = {b ** k}y, so the sum is {b ** k}y + y = {correct}."
    return _text_mc(rng, prompt, correct, ds, subskill="exponent_rules", explanation=expl, tags=["exponents", "rewrite"], est=85 if d == "medium" else 95, verify=correct)


# ---- polynomials --------------------------------------------------------- #
def poly_divide(rng, d):
    """Divide a polynomial by a monomial or binomial; remainder theorem."""
    if d == "easy":
        g = rng.randint(2, 6)
        a, b = rng.randint(1, 7), rng.randint(1, 9)
        if math.gcd(math.gcd(a, b), 1) != 1:
            pass
        expr = _poly_str([g * a, g * b, 0])
        prompt = f"Which of the following is equivalent to ({expr}) ÷ {g}x?"
        correct = f"{_lin(a, b)}"
        ds = [(f"{_lin(g * a, b)}", "Divide every term by {0}x.".format(g)), (_poly_str([a, b, 0]), "Divide each term by x as well: the degree drops by 1."), (f"{_lin(a, g * b)}", "Divide the second term by {0} too.".format(g)), (f"{_lin(a, -b)}", "Check the sign of the constant.")]
        expl = f"Divide term by term: {g * a}x²/{g}x = {a}x and {g * b}x/{g}x = {b}: {correct}."
    elif d == "medium":
        r1 = rng.choice([v for v in range(-9, 10) if v])
        r2 = rng.choice([v for v in range(-9, 10) if v and v != r1])
        b, c = -(r1 + r2), r1 * r2
        prompt = f"Which of the following is equivalent to ({_fx(1, b, c)}) ÷ (x {_pm(-r1)}) for x ≠ {_m(r1)}?"
        correct = f"x {_pm(-r2)}"
        ds = [(f"x {_pm(r2)}", "Check the sign: the other factor's root is {0}.".format(_m(r2))), (f"x {_pm(-r1)}", "That is the divisor itself."), (f"x {_pm(b)}" if b != -r2 else f"x {_pm(c)}", "Factor the trinomial; the quotient is the other factor."), (f"x² {_pm(-r2)}", "Dividing a quadratic by a linear factor gives a linear result.")]
        expl = f"{_fx(1, b, c)} = (x {_pm(-r1)})(x {_pm(-r2)}), so dividing by (x {_pm(-r1)}) leaves {correct}."
    else:
        a, b, c = rng.randint(1, 3), rng.choice([v for v in range(-8, 9) if v]), rng.choice([v for v in range(-9, 10) if v])
        r = rng.choice([v for v in range(-5, 6) if v])
        rem = a * r * r + b * r + c
        prompt = f"What is the remainder when {_fx(a, b, c)} is divided by (x {_pm(-r)})?"
        val = rem
        expl = f"By the remainder theorem the remainder is p({_m(r)}) = {_m(a)}({_m(r)})² {_pm(b)}({_m(r)}) {_pm(c)} = {_m(rem)}."
        ds = [(a * r * r - b * r + c, "Evaluate at x = {0}, not {1}.".format(_m(r), _m(-r))), (c, "The remainder is p(r), not the constant term."), (-rem if rem else rem + 1, "Sign slip."), (rem - c, "Include the constant term.")]
        return _numeric_mc(rng, prompt, val, ds, subskill="factoring", explanation=expl, tags=["polynomials", "remainder"], est=95, verify=f"p({r})={rem}")
    return _text_mc(rng, prompt, correct, ds, subskill="operations", explanation=expl, tags=["polynomials", "division"], est=80, verify=correct)


def poly_zeros(rng, d):
    """Zeros of factored polynomials: list, count, sum."""
    r1 = rng.choice([v for v in range(-9, 10) if v])
    r2 = rng.choice([v for v in range(-9, 10) if v and v != r1])
    if d == "easy":
        prompt = f"What are the zeros of the function f(x) = (x {_pm(-r1)})(x {_pm(-r2)})?"
        correct = f"x = {_m(min(r1, r2))} and x = {_m(max(r1, r2))}"
        ds = [(f"x = {_m(-min(r1, r2))} and x = {_m(-max(r1, r2))}" if r1 != -r2 else f"x = {_m(r1)} only", "Each factor x − r is 0 when x = r; the signs flip from what is written."), (f"x = {_m(r1)} only", "Both factors give a zero."), (f"x = {_m(r1 + r2)}", "That is the sum of the zeros, not a zero."), (f"x = {_m(r1 * r2)}", "That is the product of the zeros.")]
        expl = f"Set each factor to 0: x = {_m(r1)} or x = {_m(r2)}."
        return _text_mc(rng, prompt, correct, ds, subskill="factoring", explanation=expl, tags=["polynomials", "zeros"], est=70, verify=correct)
    if d == "medium":
        r3 = rng.choice([v for v in range(-9, 10) if v not in (r1, r2)])
        dup = rng.random() < 0.4
        if dup:
            prompt = f"How many distinct real zeros does the function f(x) = x(x {_pm(-r1)})²(x {_pm(-r2)}) have?"
            val = 3
            expl = f"The zeros are 0, {_m(r1)} (repeated), and {_m(r2)}: 3 distinct zeros."
            ds = [(4, "The repeated factor (x − {0})² gives one zero, not two.".format(_m(r1))), (2, "Don't forget the factor x, which gives the zero 0."), (1, "Each distinct factor gives a zero."), (5, "Count distinct factors, not the degree plus one.")]
        else:
            prompt = f"What is the sum of the zeros of the function f(x) = (x {_pm(-r1)})(x {_pm(-r2)})(x {_pm(-r3)})?"
            val = r1 + r2 + r3
            expl = f"The zeros are {_m(r1)}, {_m(r2)}, {_m(r3)}; their sum is {_m(val)}."
            ds = [(-val if val else 1, "The zeros are r, not −r, for factors x − r."), (r1 * r2 * r3, "That is the product of the zeros."), (r1 + r2, "Include all three zeros."), (val + 1, "Arithmetic slip.")]
        return _numeric_mc(rng, prompt, val, ds, subskill="factoring", explanation=expl, tags=["polynomials", "zeros"], est=80, verify=f"val={val}")
    a = rng.choice([2, 3, 4, 5])
    p = rng.choice([v for v in range(-7, 8) if v and math.gcd(abs(v), a) == 1])
    prompt = f"The function f is defined by f(x) = ({_lin(a, -p)})(x {_pm(-r1)})(x² + {rng.randint(1, 9)}). How many real zeros does f have, and what is their sum?"
    s = Fraction(p, a) + r1
    correct = f"2 real zeros with sum {num_str(s)}"
    ds = [(f"3 real zeros with sum {num_str(s)}", "x² + c = 0 has no real solutions for c > 0."), (f"4 real zeros with sum {num_str(s)}", "The quadratic factor contributes no real zeros."), (f"2 real zeros with sum {num_str(Fraction(a, p) + r1)}", "The zero of {0} is {1}, not {2}.".format(_lin(a, -p), num_str(Fraction(p, a)), num_str(Fraction(a, p)))), (f"2 real zeros with sum {num_str(-s) if s else num_str(s + 1)}", "Sign slip on the zeros.")]
    expl = f"Real zeros: x = {num_str(Fraction(p, a))} and x = {_m(r1)} (the factor x² + c has none); their sum is {num_str(s)}."
    return _text_mc(rng, prompt, correct, ds, subskill="factoring", explanation=expl, tags=["polynomials", "zeros"], est=100, verify=correct)


# ---- ratios_percentages_units ------------------------------------------- #
def rp_tax_tip(rng, d):
    """Sales tax / tip / discount money problems."""
    name = rng.choice(NAMES)
    if d == "easy":
        P = rng.randint(8, 120)
        t = rng.choice([5, 6, 7, 8, 10, 15, 20, 25])
        kind = rng.choice(["tax", "tip"])
        val = Fraction(P * (100 + t), 100)
        prompt = f"{name}'s {'restaurant bill' if kind == 'tip' else 'purchase'} comes to ${P}. If {name} {'leaves a' if kind == 'tip' else 'pays'} {t}% {kind}, what is the total amount paid, in dollars?"
        expl = f"{t}% of {P} is {num_str(Fraction(P * t, 100))}; total = {P} + {num_str(Fraction(P * t, 100))} = {num_str(val)}."
        ds = [(Fraction(P * t, 100), f"That is the {kind} alone, not the total."), (P + t, "Percent of the bill, not a flat ${0}.".format(t)), (Fraction(P * (100 - t), 100), "A {0} is added, not subtracted.".format(kind)), (val + Fraction(P, 100), "Arithmetic slip.")]
    elif d == "medium":
        t = rng.choice([4, 5, 6, 8, 10, 12, 15, 20, 25])
        P = rng.randint(2, 40) * (100 // math.gcd(100, 100 + t)) if False else rng.randint(2, 60)
        total = Fraction(P * (100 + t), 100)
        prompt = f"After a {t}% sales tax was added, {name} paid ${num_str(total)} for a jacket. What was the price of the jacket before tax, in dollars?"
        val = P
        expl = f"total = price × (1 + {t}/100), so price = {num_str(total)} ÷ {num_str(Fraction(100 + t, 100))} = {P}."
        ds = [(total * Fraction(100 - t, 100), "Divide by 1.{0:02d}; don't subtract {1}%.".format(t, t)), (total - t, "The tax is a percent, not ${0}.".format(t)), (total, "That is the total with tax."), (P + 1, "Arithmetic slip.")]
    else:
        P = rng.randint(4, 40) * 5
        dpct = rng.choice([10, 15, 20, 25, 30, 40])
        t = rng.choice([5, 6, 8, 10])
        val = Fraction(P * (100 - dpct) * (100 + t), 10000)
        prompt = f"A coat with a list price of ${P} is on sale for {dpct}% off, and a {t}% sales tax is applied to the sale price. What is the final cost, in dollars?"
        expl = f"Sale price: {P} × {num_str(Fraction(100 - dpct, 100))} = {num_str(Fraction(P * (100 - dpct), 100))}; with tax × {num_str(Fraction(100 + t, 100))}: {num_str(val)}."
        ds = [(Fraction(P * (100 - dpct + t), 100), "Apply the tax to the sale price; percents don't simply combine."), (Fraction(P * (100 - dpct), 100), "That is the sale price before tax."), (Fraction(P * (100 + t), 100), "Apply the discount first."), (Fraction(P * (100 - dpct) * (100 - t), 10000), "Tax is added, not subtracted.")]
    return _numeric_mc(rng, prompt, val, ds, subskill="percent_change", explanation=expl, tags=["percent", "money"], est=75 if d == "easy" else 95, fmt=lambda v: _money(v), qtype="multi_step_math" if d == "hard" else "multiple_choice", verify=f"val={num_str(val)}")


def rp_best_deal(rng, d):
    """Unit prices and comparing rates (text + numeric)."""
    item = rng.choice(["cereal", "juice", "rice", "coffee", "detergent", "trail mix"])
    unit = rng.choice(["ounce", "pound", "liter", "gram"])
    if d == "easy":
        q = rng.choice([4, 5, 8, 10, 12, 16, 20, 25, 32])
        per = rng.choice([Fraction(k, 100) for k in range(15, 400, 5)])
        price = per * q
        prompt = f"A {q}-{unit} package of {item} costs {_money(price)}. What is the price per {unit}?"
        val = per
        expl = f"{_money(price)} ÷ {q} = {_money(per)} per {unit}."
        ds = [(price * q, "Divide the price by the quantity; don't multiply."), (Fraction(q, 1) / price if price else per + 1, "That is {0}s per dollar.".format(unit)), (per + Fraction(5, 100), "Arithmetic slip."), (price, "That is the package price, not the unit price.")]
        return _numeric_mc(rng, prompt, val, ds, subskill="unit_rate", explanation=expl, tags=["ratio", "unit-price"], est=70, fmt=lambda v: _money(v), verify=f"per={num_str(per)}")
    sizes = sorted(rng.sample([6, 8, 10, 12, 16, 20, 24, 32, 40, 48], 4))
    base = rng.choice([Fraction(k, 100) for k in range(20, 120, 5)])
    pers = [base + Fraction(rng.choice([-9, -6, -3, 3, 6, 9]), 100) for _ in sizes]
    best = min(range(4), key=lambda i: pers[i])
    if len({p for p in pers}) < 4:
        return rp_best_deal(rng, d)
    options = [(s, pers[i] * s) for i, s in enumerate(sizes)]
    if d == "medium":
        prompt = f"Four packages of {item} are priced as follows: " + "; ".join(f"{s} {unit}s for {_money(p)}" for s, p in options) + ". Which package has the lowest price per {unit}?"
        correct = f"{sizes[best]} {unit}s for {_money(options[best][1])}"
        ds = [(f"{s} {unit}s for {_money(p)}", f"Its unit price is {_money(pers[i])} per {unit}, higher than {_money(pers[best])}.") for i, (s, p) in enumerate(options) if i != best]
        expl = f"Compute each price per {unit}: " + ", ".join(_money(p) for p in pers) + f". The lowest is {_money(pers[best])}."
        return _text_mc(rng, prompt, correct, ds, subskill="unit_rate", explanation=expl, tags=["ratio", "unit-price", "compare"], est=95, verify=f"best={sizes[best]}")
    i, j = rng.sample(range(4), 2)
    diff = abs(pers[i] - pers[j])
    prompt = (f"A {sizes[i]}-{unit} package of {item} costs {_money(options[i][1])} and a {sizes[j]}-{unit} package costs {_money(options[j][1])}. "
              f"How much more, in dollars per {unit}, does the more expensive package cost per {unit}?")
    val = diff
    expl = f"Unit prices: {_money(pers[i])} and {_money(pers[j])}; the difference is {_money(diff)}."
    ds = [(abs(options[i][1] - options[j][1]), "Compare prices per {0}, not package prices.".format(unit)), (pers[i], "That is one unit price, not the difference."), (pers[j], "That is one unit price, not the difference."), (diff * 2, "Arithmetic slip.")]
    return _numeric_mc(rng, prompt, val, ds, subskill="unit_rate", explanation=expl, tags=["ratio", "unit-price"], est=100, fmt=lambda v: _money(v), qtype="multi_step_math", verify=f"diff={num_str(diff)}")


# ---- proportions ------------------------------------------------------------ #
def pr_shadow(rng, d):
    """Similar triangles in context: shadows, ramps, scale models."""
    k = rng.choice([Fraction(3, 2), 2, Fraction(5, 2), 3, 4, Fraction(1, 2), Fraction(4, 3), Fraction(5, 4)])
    if d == "easy":
        h1 = rng.randint(2, 8)
        s1 = h1 * rng.choice([1, 2, 3])
        h2 = h1 * rng.choice([2, 3, 4, 5])
        s2 = s1 * h2 // h1
        prompt = f"At the same time of day, a {h1}-meter pole casts a {s1}-meter shadow and a tree casts a {s2}-meter shadow. How tall is the tree, in meters?"
        val = h2
        expl = f"Set up {h1}/{s1} = h/{s2}: h = {h1}·{s2}/{s1} = {h2}."
        ds = [(Fraction(s1 * s2, h1), "The proportion is inverted."), (h1 + (s2 - s1), "Shadows and heights scale multiplicatively."), (s2, "That is the tree's shadow, not its height."), (h2 + h1, "Arithmetic slip.")]
    elif d == "medium":
        b1 = rng.randint(3, 12)
        hgt = rng.randint(2, 10)
        mult = rng.choice([2, 3, 4, 5])
        b2 = b1 * mult
        prompt = f"A ramp rises {hgt} feet over a horizontal distance of {b1} feet. A longer ramp with the same slope covers a horizontal distance of {b2} feet. How many feet does the longer ramp rise?"
        val = hgt * mult
        expl = f"Same slope means similar triangles: rise/run is constant, {hgt}/{b1} = r/{b2}, so r = {hgt * mult}."
        ds = [(Fraction(b1 * b2, hgt), "The proportion is inverted."), (hgt + (b2 - b1), "Scale multiplicatively."), (b2, "That is the horizontal distance."), (hgt * mult + hgt, "Arithmetic slip.")]
    else:
        d1, h1 = rng.randint(2, 6), rng.randint(3, 9)
        D = d1 * rng.randint(3, 8)
        # person height h1 at distance d1 from lamp base casts shadow s: h1/(s) = H/(d1+s); choose H, s nicely: pick s, then H = h1 (d1+s)/s integer
        s = rng.choice([v for v in range(1, 7) if (h1 * (d1 + v)) % v == 0])
        H = h1 * (d1 + s) // s
        prompt = (f"A person {h1} feet tall stands {d1} feet from the base of a streetlight and casts a shadow {s} feet long. "
                  f"How tall is the streetlight, in feet?")
        val = H
        expl = f"Similar triangles: H/({d1} + {s}) = {h1}/{s}, so H = {h1}·{d1 + s}/{s} = {H}."
        ds = [(Fraction(h1 * d1, s), "The light's triangle has base {0} + {1}, not {0}.".format(d1, s)), (h1 + d1, "Use similar triangles, not addition."), (Fraction(h1 * s, d1 + s) if Fraction(h1 * s, d1 + s) != H else H + 1, "The proportion is inverted."), (H + h1, "Arithmetic slip.")]
        return _numeric_mc(rng, prompt, val, ds, subskill="scaling", explanation=expl, qtype="multi_step_math", tags=["proportion", "similar", "shadow"], est=105, verify=f"H={H}")
    return _numeric_mc(rng, prompt, val, ds, subskill="scaling", explanation=expl, tags=["proportion", "similar"], est=80, verify=f"val={val}")


def pr_fuel(rng, d):
    """Fuel/consumption rates and multi-step proportional reasoning."""
    if d == "easy":
        mpg = rng.randint(18, 45)
        g = rng.randint(2, 15)
        prompt = f"A car travels {mpg} miles on each gallon of gasoline. How many miles can it travel on {g} gallons?"
        val = mpg * g
        expl = f"{mpg} miles/gallon × {g} gallons = {val} miles."
        ds = [(Fraction(mpg, g), "Multiply the rate by the gallons; don't divide."), (mpg + g, "Multiply, don't add."), (val + mpg, "Off by one gallon."), (g, "That is the fuel, not the distance.")]
    elif d == "medium":
        mpg = rng.randint(18, 45)
        miles = mpg * rng.randint(3, 20)
        price = rng.choice([Fraction(k, 100) for k in range(280, 460, 10)])
        gallons = miles // mpg
        val = price * gallons
        prompt = f"A car gets {mpg} miles per gallon. Gasoline costs {_money(price)} per gallon. How much does the gasoline for a {miles}-mile trip cost, in dollars?"
        expl = f"Gallons needed: {miles} ÷ {mpg} = {gallons}; cost = {gallons} × {_money(price)} = {_money(val)}."
        ds = [(price * miles, "Convert miles to gallons before pricing."), (Fraction(gallons), "That is the number of gallons, not the cost."), (price * mpg, "Use the gallons for the trip, not the miles per gallon."), (val + price, "Off by one gallon.")]
        return _numeric_mc(rng, prompt, val, ds, subskill="scaling", explanation=expl, qtype="multi_step_math", tags=["proportion", "rate", "fuel"], est=95, fmt=lambda v: _money(v), verify=f"cost={num_str(val)}")
    else:
        rate_n, rate_d = rng.randint(2, 9), rng.randint(2, 9)
        if rate_n == rate_d:
            rate_d += 1
        t = rng.randint(3, 12) * rate_d
        used = rate_n * (t // rate_d)
        tank = used + rng.randint(5, 40)
        prompt = (f"A generator uses {rate_n} gallons of fuel every {rate_d} hours. It starts with a full {tank}-gallon tank and runs for {t} hours. "
                  f"How many gallons of fuel remain?")
        val = tank - used
        expl = f"Fuel used: {rate_n}/{rate_d} × {t} = {used} gallons; remaining = {tank} − {used} = {val}."
        ds = [(used, "That is the fuel used, not what remains."), (tank - rate_n * t // 1 if tank - rate_n * t != val else val + 2, "Divide by {0} hours per {1} gallons.".format(rate_d, rate_n)), (tank - t * rate_d // rate_n if tank - t * rate_d // rate_n != val else val - 1, "The rate is {0} gallons per {1} hours, not the reverse.".format(rate_n, rate_d)), (val + rate_n, "Arithmetic slip.")]
        return _numeric_mc(rng, prompt, val, ds, subskill="scaling", explanation=expl, qtype="multi_step_math", tags=["proportion", "rate", "fuel"], est=100, verify=f"left={val}")
    return _numeric_mc(rng, prompt, val, ds, subskill="direct_proportion", explanation=expl, tags=["proportion", "rate", "fuel"], est=65, verify=f"val={val}")


# ---- data_analysis ----------------------------------------------------------- #
def da_interval_table(rng, d):
    """Grouped-frequency (histogram-style) tables."""
    width = rng.choice([5, 10, 20])
    start = rng.choice([0, 10, 20, 50, 100])
    k = 5
    labels = [f"{start + i * width}–{start + (i + 1) * width - 1}" for i in range(k)]
    freqs = [rng.randint(2, 14) for _ in range(k)]
    N = sum(freqs)
    qty = rng.choice([("Score", "Number of students", "students"), ("Minutes", "Number of commuters", "commuters"),
                      ("Price (dollars)", "Number of items", "items"), ("Age", "Number of members", "members")])
    stim = _table("Frequency table", [qty[0], qty[1]], [[l, f] for l, f in zip(labels, freqs)])
    if d == "easy":
        i = rng.randrange(1, k)
        val = sum(freqs[i:])
        prompt = f"The table groups {N} {qty[2]} by {qty[0].lower()}. How many {qty[2]} have a {qty[0].lower().split(' (')[0]} of at least {start + i * width}?"
        expl = f"Add the frequencies of the intervals from {labels[i]} upward: {' + '.join(map(str, freqs[i:]))} = {val}."
        ds = [(sum(freqs[:i]), "That counts the intervals below the cutoff."), (freqs[i], "Include all higher intervals too."), (N - freqs[i], "That excludes only one interval."), (val + freqs[i - 1], "The interval {0} is below the cutoff.".format(labels[i - 1]))]
    elif d == "medium":
        cum = 0
        pos = (N + 1) / 2
        for i, f in enumerate(freqs):
            cum += f
            if cum >= pos:
                med_i = i
                break
        prompt = f"The table groups {N} {qty[2]} by {qty[0].lower()}. In which interval does the median {qty[0].lower().split(' (')[0]} lie?"
        correct = labels[med_i]
        ds = [(labels[j], f"The cumulative count reaches the middle position ({N} values → position {pos:g}) in a different interval.") for j in range(k) if j != med_i]
        expl = f"The median is the {_ordinal(int(pos)) if pos == int(pos) else 'middle'} value of {N}; cumulative frequencies reach that position in the {correct} interval."
        return _text_mc(rng, prompt, correct, ds, subskill="tables", explanation=expl, qtype="data_interpretation", tags=["data", "table", "histogram", "median"], est=95, stimulus=stim, verify=f"median interval {correct}")
    else:
        i = rng.randrange(k)
        pct = round(100 * freqs[i] / N)
        prompt = f"The table groups {N} {qty[2]} by {qty[0].lower()}. Approximately what percent of the {qty[2]} fall in the {labels[i]} interval?"
        val = pct
        expl = f"{freqs[i]}/{N} × 100 ≈ {pct}%."
        ds = [(freqs[i], "That is the count, not a percent."), (round(100 * freqs[i] / (N - freqs[i])), "Divide by the total {0}, not the rest.".format(N)), (round(100 * sum(freqs[:i + 1]) / N) if round(100 * sum(freqs[:i + 1]) / N) != pct else pct + 7, "That is the cumulative percent up to this interval."), (pct + 10, "Arithmetic slip.")]
        return _numeric_mc(rng, prompt, val, ds, subskill="tables", explanation=expl, qtype="data_interpretation", tags=["data", "table", "histogram", "percent"], est=90, fmt=lambda v: f"{num_str(v)}%", stimulus=stim, verify=f"{freqs[i]}/{N}")
    return _numeric_mc(rng, prompt, val, ds, subskill="tables", explanation=expl, qtype="data_interpretation", tags=["data", "table", "histogram"], est=80, stimulus=stim, verify=f"val={val}")


def da_two_series(rng, d):
    """Tables with two numeric columns: differences, totals, averages, ratios."""
    n = 4 if d == "easy" else 5
    cat, qty, labs, vals, cap, unit = _da_table(rng, n, 10, 80)
    vals2 = [rng.randint(10, 80) for _ in labs]
    col1, col2 = rng.choice([("Online", "In store"), ("Morning", "Afternoon"), ("Girls", "Boys"), ("Year 1", "Year 2"), ("Home", "Away")])
    stim = _table(f"{cap} by {col1.lower()} and {col2.lower()}", [cat, col1, col2], [[l, a, b] for l, a, b in zip(labs, vals, vals2)])
    totals = [a + b for a, b in zip(vals, vals2)]
    if d == "easy":
        i = rng.randrange(n)
        val = totals[i]
        prompt = f"The table shows {unit} for {n} {cat.lower()}s split into {col1.lower()} and {col2.lower()} ({sum(totals)} in all). What is the combined total for {labs[i]}?"
        expl = f"{vals[i]} + {vals2[i]} = {val}."
        ds = [(abs(vals[i] - vals2[i]), "Add the two columns; don't subtract."), (vals[i], f"That is only the {col1.lower()} value."), (vals2[i], f"That is only the {col2.lower()} value."), (val + 10, "Arithmetic slip.")]
    elif d == "medium":
        diffs = [a - b for a, b in zip(vals, vals2)]
        i = max(range(n), key=lambda k: diffs[k])
        if sorted(diffs)[-1] == sorted(diffs)[-2]:
            return da_two_series(rng, d)
        prompt = f"The table shows {unit} for {n} {cat.lower()}s split into {col1.lower()} and {col2.lower()} ({sum(totals)} in all). For which {cat.lower()} does {col1.lower()} exceed {col2.lower()} by the greatest amount?"
        correct = labs[i]
        ds = [(labs[j], f"{labs[j]}: {col1.lower()} − {col2.lower()} = {_m(diffs[j])}, not the greatest.") for j in range(n) if j != i]
        expl = f"Compute {col1.lower()} − {col2.lower()} for each row; {labs[i]} gives {diffs[i]}, the greatest."
        return _text_mc(rng, prompt, correct, ds, subskill="tables", explanation=expl, qtype="data_interpretation", tags=["data", "table", "two-series"], est=85, stimulus=stim, verify=f"{correct}")
    else:
        s1, s2 = sum(vals), sum(vals2)
        kind = rng.choice(["mean_diff", "pct"])
        if kind == "mean_diff":
            val = Fraction(s1 - s2, n)
            prompt = f"The table shows {unit} for {n} {cat.lower()}s split into {col1.lower()} and {col2.lower()} ({s1 + s2} in all). How much greater is the mean {col1.lower()} value than the mean {col2.lower()} value? (A negative answer means it is smaller.)"
            expl = f"Mean {col1.lower()} = {s1}/{n}, mean {col2.lower()} = {s2}/{n}; difference = ({s1} − {s2})/{n} = {num_str(val)}."
            ds = [(s1 - s2, "Divide the difference in totals by {0}.".format(n)), (Fraction(s2 - s1, n), "The order of subtraction is reversed."), (Fraction(s1, n), "That is the mean of one column, not the difference."), (Fraction(s1 - s2, 2 * n), "Divide by n = {0}, not 2n.".format(n))]
            fmt = lambda v: num_str(round(float(v), 2))
        else:
            pct = round(100 * s1 / (s1 + s2))
            val = pct
            prompt = f"The table shows {unit} for {n} {cat.lower()}s split into {col1.lower()} and {col2.lower()} ({s1 + s2} in all). Approximately what percent of all the {unit} were {col1.lower()}?"
            expl = f"{s1}/({s1} + {s2}) × 100 ≈ {pct}%."
            ds = [(round(100 * s1 / s2), "Divide by the grand total, not the other column."), (100 - pct, f"That is the {col2.lower()} share."), (s1, "That is a count, not a percent."), (pct + 8, "Arithmetic slip.")]
            fmt = lambda v: f"{num_str(v)}%"
        return _numeric_mc(rng, prompt, val, ds, subskill="tables", explanation=expl, qtype="data_interpretation", tags=["data", "table", "two-series"], est=100, fmt=fmt, stimulus=stim, verify=f"s1={s1},s2={s2}")
    return _numeric_mc(rng, prompt, val, ds, subskill="tables", explanation=expl, qtype="data_interpretation", tags=["data", "table", "two-series"], est=70, stimulus=stim, verify=f"val={val}")


# ---- statistics -------------------------------------------------------------- #
def st_compare_tables(rng, d):
    """Two distributions summarized as value/count tables: compare mean, SD, spread (text)."""
    values = list(range(1, 6)) if d != "hard" else list(range(10, 60, 10))
    tight = [rng.randint(0, 1), rng.randint(2, 4), rng.randint(6, 10), rng.randint(2, 4), rng.randint(0, 1)]
    wide = [rng.randint(4, 8), rng.randint(1, 3), rng.randint(0, 2), rng.randint(1, 3), rng.randint(4, 8)]
    a_is_tight = rng.random() < 0.5
    A, B = (tight, wide) if a_is_tight else (wide, tight)
    rows = [[v, a, b] for v, a, b in zip(values, A, B)]
    stim = _table("Number of responses by value", ["Value", "Group A", "Group B"], rows)
    tight_name, wide_name = ("A", "B") if a_is_tight else ("B", "A")
    if d == "easy":
        prompt = f"The table shows how many responses in two groups took each value (Group A: {sum(A)} responses, Group B: {sum(B)}). Which group's data has the greater standard deviation?"
        correct = f"Group {wide_name}, because its responses are spread farther from the center."
        ds = [(f"Group {tight_name}, because its responses cluster near the center.", "Clustering near the center means a SMALLER standard deviation."), (f"Group {tight_name}, because it has more responses at a single value.", "A tall peak at the center indicates less spread."), ("The groups have the same standard deviation, because they have the same values.", "The frequencies differ, so the spreads differ."), (f"Group {wide_name}, because its mean is larger.", "Standard deviation measures spread, not the size of the mean.")]
        expl = f"Group {wide_name} has many responses at the extreme values and few in the middle, so its spread (standard deviation) is larger."
    elif d == "medium":
        meanA = Fraction(sum(v * a for v, a in zip(values, A)), sum(A))
        meanB = Fraction(sum(v * b for v, b in zip(values, B)), sum(B))
        prompt = f"The table shows how many responses in two groups took each value (Group A: {sum(A)} responses, Group B: {sum(B)}). Which statement about the means and standard deviations is true?"
        rel = "greater than" if meanA > meanB else "less than" if meanA < meanB else "equal to"
        correct = f"The mean of Group A is {rel} the mean of Group B, and Group {wide_name} has the larger standard deviation."
        ds = [(f"The mean of Group A is {rel} the mean of Group B, and Group {tight_name} has the larger standard deviation.", f"Group {tight_name}'s data clusters near the center, so its standard deviation is smaller."),
              (f"The mean of Group A is {'less than' if meanA > meanB else 'greater than'} the mean of Group B, and Group {wide_name} has the larger standard deviation.", f"Mean A = {float(meanA):.2f}, mean B = {float(meanB):.2f}."),
              (f"The two groups have the same mean and the same standard deviation.", "At least the spreads differ: one group clusters, the other does not."),
              (f"Group {wide_name} has the larger standard deviation because it has more total responses.", f"Spread depends on distances from the center, not on the number of responses.")]
        expl = f"Mean A = {float(meanA):.2f}, mean B = {float(meanB):.2f}; Group {wide_name}'s responses sit far from the center, so its standard deviation is larger."
    else:
        prompt = f"The table shows how many responses in two groups took each value (Group A: {sum(A)} responses, Group B: {sum(B)}). If every value in Group {wide_name} were increased by 10, how would its mean and standard deviation change?"
        correct = "The mean would increase by 10 and the standard deviation would not change."
        ds = [("Both the mean and the standard deviation would increase by 10.", "Shifting every value leaves the distances from the center unchanged."), ("The mean would not change and the standard deviation would increase by 10.", "Adding 10 to every value raises the mean by 10."), ("The mean would increase by 10 and the standard deviation would increase by a factor of 10.", "Only multiplying every value scales the standard deviation."), ("Neither the mean nor the standard deviation would change.", "The mean shifts with the data.")]
        expl = "Adding a constant to every data value shifts the mean by that constant but leaves the spread (standard deviation) unchanged."
    return _text_mc(rng, prompt, correct, ds, subskill="spread", explanation=expl, qtype="data_interpretation", tags=["statistics", "table", "standard-deviation"], est=90, stimulus=stim, verify=f"wide={wide_name}")


def st_outlier_effect(rng, d):
    """How an outlier changes mean vs median (numeric and text)."""
    n = rng.choice([5, 7])
    data = sorted(_data_list(rng, n, 10, 40))
    data[-1] += (n - sum(data) % n) % n
    s = sum(data)
    mean = s // n
    med = data[n // 2]
    out = max(data) + rng.randint(30, 80)
    new_data = sorted(data + [out])
    new_mean = Fraction(s + out, n + 1)
    new_med = Fraction(new_data[n // 2] + new_data[n // 2 + 1], 2)
    shown = ", ".join(map(str, data))
    if d == "easy":
        prompt = f"The data set {shown} has mean {mean} and median {med}. If the value {out} is added to the set, which statistic changes by more?"
        correct = f"The mean, which increases from {mean} to {num_str(new_mean)}."
        ds = [(f"The median, which increases from {med} to {num_str(new_med)}.", f"The median moves only to {num_str(new_med)}; the mean moves to {num_str(new_mean)}."), ("Both change by the same amount.", "The mean is pulled by the outlier much more than the median."), ("Neither changes, because one value cannot affect a summary statistic.", "Every value affects the mean."), (f"The median, which increases from {med} to {out}.", "The median is the middle value; it does not jump to the new value.")]
        expl = f"New mean = ({s} + {out})/{n + 1} = {num_str(new_mean)}; new median = {num_str(new_med)}. The mean changes far more."
        return _text_mc(rng, prompt, correct, ds, subskill="mean_median_mode", explanation=expl, tags=["statistics", "outlier"], est=85, verify=f"mean {mean}->{num_str(new_mean)}, median {med}->{num_str(new_med)}")
    if d == "medium":
        prompt = f"The data set {shown} has mean {mean}. If the value {out} is added, by how much does the mean increase?"
        val = new_mean - mean
        expl = f"New mean = ({s} + {out})/{n + 1} = {num_str(new_mean)}; increase = {num_str(new_mean)} − {mean} = {num_str(val)}."
        ds = [(out - mean, "The outlier's excess is shared among all {0} values.".format(n + 1)), (Fraction(out, n + 1), "Compute the new mean, then subtract the old mean."), (new_mean, "That is the new mean, not the increase."), (Fraction(out - mean, n), "Divide by the new count {0}.".format(n + 1))]
        fmt = lambda v: num_str(round(float(v), 2))
        return _numeric_mc(rng, prompt, val, ds, subskill="mean_median_mode", explanation=expl, tags=["statistics", "outlier"], est=90, fmt=fmt, verify=f"inc={num_str(val)}")
    prompt = f"A data set of {n} values, {shown}, is extended by one value x. For what value of x will the mean of the new data set equal {mean + rng.randint(2, 6)}?"
    target = int(prompt.split("equal ")[1].rstrip("?"))
    val = target * (n + 1) - s
    expl = f"Required total = {target} × {n + 1} = {target * (n + 1)}; x = {target * (n + 1)} − {s} = {val}."
    ds = [(target, "x must be well above the target mean to pull it up."), (target * n - s, "Use the new count {0}.".format(n + 1)), (target * (n + 1), "That is the required total, not x."), (val - target, "Subtract the current total from the required total.")]
    return _numeric_mc(rng, prompt, val, ds, subskill="mean_median_mode", explanation=expl, tags=["statistics", "mean"], est=95, verify=f"x={val}")


def st_quartiles(rng, d):
    """Quartiles, interquartile range, and box-plot reasoning."""
    n = 8 if d != "hard" else 12
    data = sorted(_data_list(rng, n, 2, 60))
    half = n // 2
    lower, upper = data[:half], data[half:]
    q1 = Fraction(lower[half // 2 - 1] + lower[half // 2], 2)
    q3 = Fraction(upper[half // 2 - 1] + upper[half // 2], 2)
    med = Fraction(data[half - 1] + data[half], 2)
    shown = ", ".join(map(str, rng.sample(data, n)))
    if d == "easy":
        which = rng.choice(["first", "third"])
        val = q1 if which == "first" else q3
        prompt = f"What is the {which} quartile of the data set {shown}?"
        expl = f"Order the data: {', '.join(map(str, data))}. The median is {num_str(med)}; the {which} quartile is the median of the {'lower' if which == 'first' else 'upper'} half: {num_str(val)}."
        ds = [(q3 if which == "first" else q1, f"That is the {'third' if which == 'first' else 'first'} quartile."), (med, "That is the median (second quartile)."), (data[0] if which == "first" else data[-1], "That is the minimum/maximum, not a quartile."), (val + 1, "Recheck the median of the half.")]
    elif d == "medium":
        prompt = f"What is the interquartile range of the data set {shown}?"
        val = q3 - q1
        expl = f"Ordered: {', '.join(map(str, data))}. Q1 = {num_str(q1)}, Q3 = {num_str(q3)}; IQR = {num_str(q3)} − {num_str(q1)} = {num_str(val)}."
        ds = [(data[-1] - data[0], "That is the range, not the interquartile range."), (q3, "Subtract Q1 from Q3."), (med, "That is the median."), (Fraction(data[-1] - data[0], 2), "The IQR is Q3 − Q1, not half the range.")]
    else:
        fence_hi = q3 + Fraction(3, 2) * (q3 - q1)
        out = int(fence_hi) + rng.randint(5, 25)
        prompt = f"For the data set {shown}, an outlier is defined as a value more than 1.5 times the interquartile range above the third quartile. What is the least integer value that would be considered an outlier if added to the set?"
        val = int(fence_hi) + 1
        expl = f"Q1 = {num_str(q1)}, Q3 = {num_str(q3)}, IQR = {num_str(q3 - q1)}; fence = {num_str(q3)} + 1.5·{num_str(q3 - q1)} = {num_str(fence_hi)}; the least integer above it is {val}."
        ds = [(int(q3) + 1, "Add 1.5 × IQR to Q3, not just 1."), (int(fence_hi) if int(fence_hi) != val else val + 1, "The value must be strictly greater than the fence."), (int(q3 + (q3 - q1)) + 1, "Multiply the IQR by 1.5, not 1."), (data[-1] + 1, "The fence is computed from the quartiles, not the maximum.")]
    fmt = lambda v: num_str(v)
    return _numeric_mc(rng, prompt, val, ds, subskill="spread", explanation=expl, tags=["statistics", "quartiles"], est=85 if d != "hard" else 110, fmt=fmt, verify=f"q1={num_str(q1)},q3={num_str(q3)}")


# ---- probability -------------------------------------------------------------- #
def pb_conditional_words(rng, d):
    """Conditional probability from a verbal description (no table)."""
    total = rng.choice([40, 50, 60, 80, 100, 120])
    a = rng.randint(total // 4, total * 3 // 4)       # in group A
    both = rng.randint(2, a - 2)
    b_only = rng.randint(2, total - a - 1) if total - a - 1 >= 2 else 1
    b = both + b_only
    ctx = rng.choice([("students", "play a sport", "play an instrument"), ("employees", "work remotely", "have a company laptop"),
                      ("customers", "bought coffee", "bought a pastry"), ("visitors", "saw the exhibit", "bought a ticket online")])
    desc = f"In a group of {total} {ctx[0]}, {a} {ctx[1]}, {b} {ctx[2]}, and {both} do both."
    if d == "easy":
        prompt = f"{desc} If one of the {ctx[0]} who {ctx[1].replace('bought', 'bought').replace('saw', 'saw')} is chosen at random, what is the probability that this person also {ctx[2].replace('have', 'has').replace('bought', 'bought').replace('play', 'plays')}?"
        val = Fraction(both, a)
        expl = f"Restrict to the {a} who {ctx[1]}; {both} of them also {ctx[2]}: {num_str(val)}."
        ds = [(Fraction(both, total), "Condition on the group who {0}, not everyone.".format(ctx[1])), (Fraction(both, b), "Condition on those who {0}, not those who {1}.".format(ctx[1], ctx[2])), (Fraction(a, total), "That is the probability of the condition itself."), (Fraction(a - both, a), "That is the probability of NOT doing the second thing.")]
    elif d == "medium":
        neither = total - (a + b - both)
        prompt = f"{desc} If one of the {ctx[0]} is chosen at random, what is the probability that this person does neither?"
        val = Fraction(neither, total)
        expl = f"Either or both: {a} + {b} − {both} = {a + b - both}; neither: {total} − {a + b - both} = {neither}; probability {num_str(val)}."
        ds = [(Fraction(total - a - b, total) if total - a - b > 0 else Fraction(neither + both, total), "Those who do both were subtracted twice; add {0} back.".format(both)), (Fraction(both, total), "That is the probability of doing both."), (Fraction(a + b - both, total), "That is the probability of doing at least one."), (Fraction(neither, total - both), "Divide by the whole group.")]
    else:
        prompt = f"{desc} If one of the {ctx[0]} who do NOT {ctx[1]} is chosen at random, what is the probability that this person {ctx[2].replace('have', 'has').replace('play', 'plays')}?"
        val = Fraction(b - both, total - a)
        expl = f"Those who do not {ctx[1]}: {total} − {a} = {total - a}; of them, {b} − {both} = {b - both} {ctx[2]}: {num_str(val)}."
        ds = [(Fraction(b, total - a), "Those who do both are in the other group; subtract them."), (Fraction(b - both, total), "Condition on the {0} who do not {1}.".format(total - a, ctx[1])), (Fraction(both, total - a), "Those who do both DO {0}.".format(ctx[1])), (Fraction(b - both, b), "Condition on the complement of the first group, not on the second group.")]
    return _numeric_mc(rng, prompt, val, ds, subskill="simple_probability", explanation=expl, qtype="multi_step_math", tags=["probability", "conditional", "word-problem"], est=95, verify=f"total={total},a={a},b={b},both={both}")


def pb_geometric(rng, d):
    """Geometric probability: areas and lengths."""
    if d == "easy":
        n = rng.randint(4, 12)
        k = rng.randint(1, n - 1)
        prompt = f"A spinner is divided into {n} equal sections, {k} of which are shaded. What is the probability that the spinner lands on a shaded section?"
        val = Fraction(k, n)
        expl = f"{k} of {n} equal sections: {num_str(val)}."
        ds = [(Fraction(n - k, n), "That is the probability of an unshaded section."), (Fraction(k, n - k), "Divide by the total number of sections."), (Fraction(k, n + 1), "There are {0} sections in all.".format(n)), (Fraction(1, n), "More than one section is shaded.")]
    elif d == "medium":
        W, H = rng.randint(6, 20), rng.randint(6, 20)
        w, h = rng.randint(2, W - 1), rng.randint(2, H - 1)
        prompt = f"A point is chosen at random inside a rectangle that is {W} by {H}. A smaller rectangle {w} by {h} lies inside it. What is the probability that the point lies inside the smaller rectangle?"
        val = Fraction(w * h, W * H)
        expl = f"Probability = area of small/area of large = {w * h}/{W * H} = {num_str(val)}."
        ds = [(Fraction(2 * (w + h), 2 * (W + H)), "Use areas, not perimeters."), (Fraction(w, W), "Use both dimensions (areas)."), (Fraction(W * H - w * h, W * H), "That is the probability of landing OUTSIDE the small rectangle."), (Fraction(w * h, W * H) * 2 if Fraction(w * h, W * H) * 2 < 1 else Fraction(w * h, W * H) / 2, "Arithmetic slip.")]
    else:
        r = rng.randint(2, 30)
        kind = rng.choice(["circle_in_square", "square_in_circle", "semicircle"])
        if kind == "circle_in_square":
            s = 2 * r
            prompt = f"A circle of radius {r} is inscribed in a square. If a point is chosen at random inside the square, what is the probability that it lies inside the circle, in terms of π?"
            correct = "π/4"
            ds = [("π/2", "Area of circle/area of square = πr²/(2r)² = π/4."), ("1/4", "The circle's area involves π."), ("π/16", "The square has side 2r, so its area is 4r², not 16r²."), ("4/π", "The probability must be less than 1.")]
            expl = f"Circle area π·{r}² = {r * r}π; square side {s}, area {s * s}; ratio {r * r}π/{s * s} = π/4."
        elif kind == "square_in_circle":
            prompt = f"A square is inscribed in a circle of radius {r}. If a point is chosen at random inside the circle, what is the probability that it lies inside the square, in terms of π?"
            correct = "2/π"
            ds = [("π/4", "That is the probability for a circle inscribed in a square."), ("1/2", "The circle's area involves π."), ("4/π", "The probability must be less than 1."), ("1/π", "The square's area is 2r², so the ratio is 2r²/(πr²) = 2/π.")]
            expl = f"The square's diagonal is 2·{r} = {2 * r}, so its area is {2 * r * r}; circle area {r * r}π; ratio = 2/π."
        else:
            prompt = f"A semicircle of radius {r} is drawn inside a rectangle that is {2 * r} by {r}, with its diameter along the longer side. If a point is chosen at random in the rectangle, what is the probability that it lies inside the semicircle, in terms of π?"
            correct = "π/4"
            ds = [("π/2", "The semicircle's area is ½πr² and the rectangle's is 2r², giving π/4."), ("1/2", "The semicircle's area involves π."), ("π/8", "The rectangle's area is 2r², not 4r²."), ("2/π", "That is the inverse-type ratio for a square in a circle.")]
            expl = f"Semicircle area ½π·{r}² = {num_str(Fraction(r * r, 2))}π; rectangle area {2 * r}·{r} = {2 * r * r}; ratio = π/4."
        return _text_mc(rng, prompt, correct, ds, subskill="simple_probability", explanation=expl, tags=["probability", "geometric"], est=90, verify=f"{kind} {correct}")
    return _numeric_mc(rng, prompt, val, ds, subskill="simple_probability", explanation=expl, tags=["probability", "geometric"], est=75 if d == "easy" else 90, verify=f"P={num_str(val)}")


def pb_counting(rng, d):
    """Counting outcomes and probabilities of specific outcomes."""
    name = rng.choice(NAMES)
    if d == "easy":
        a, b = rng.randint(2, 8), rng.randint(2, 8)
        items = rng.choice([("shirts", "pairs of pants"), ("sandwiches", "drinks"), ("paint colors", "trim colors"), ("appetizers", "entrees")])
        prompt = f"{name} can choose from {a} {items[0]} and {b} {items[1]}. How many different combinations of one {items[0][:-1] if not items[0].endswith('pants') else 'shirt'} and one {items[1].replace('pairs of pants', 'pair of pants').rstrip('s') if not items[1].endswith('pants') else 'pair of pants'} are possible?"
        prompt = f"{name} can choose from {a} {items[0]} and {b} {items[1]}. How many different combinations of one of each are possible?"
        val = a * b
        expl = f"Multiply the choices: {a} × {b} = {val}."
        ds = [(a + b, "Multiply the numbers of choices; don't add."), (val + a, "Arithmetic slip."), (a * b * 2, "Each combination is one of each; no doubling."), (max(a, b), "Both choices matter.")]
    elif d == "medium":
        a, b, c = rng.randint(2, 6), rng.randint(2, 6), rng.randint(2, 5)
        total = a * b * c
        prompt = f"A meal consists of one of {a} appetizers, one of {b} main courses, and one of {c} desserts. If a meal is chosen at random, what is the probability that it includes a particular appetizer and a particular dessert?"
        val = Fraction(b, total)
        expl = f"There are {total} meals in all; those with the given appetizer and dessert number {b} (one per main course): {b}/{total} = {num_str(val)}."
        ds = [(Fraction(1, total), "Any of the {0} main courses works, so {0} meals qualify.".format(b)), (Fraction(1, a) + Fraction(1, c) if Fraction(1, a) + Fraction(1, c) < 1 else Fraction(2, total), "Independent choices multiply: (1/{0})(1/{1}).".format(a, c)), (Fraction(1, a), "The dessert choice matters too."), (Fraction(a + c, total), "Multiply, don't add, the favorable counts.")]
    else:
        if rng.random() < 0.5:
            n = rng.randint(3, 7)
            kk = rng.randint(1, min(3, n - 1))
            cnt = math.comb(n, kk)
            val = Fraction(cnt, 2 ** n)
            prompt = rng.choice([f"A fair coin is flipped {n} times. What is the probability that it lands heads up exactly {kk} time{'s' if kk > 1 else ''}?",
                                 f"If a fair coin is tossed {n} times, what is the probability of getting exactly {kk} head{'s' if kk > 1 else ''}?"])
            expl = f"There are 2^{n} = {2 ** n} equally likely sequences; exactly {kk} heads can occur in C({n}, {kk}) = {cnt} ways: {cnt}/{2 ** n} = {num_str(val)}."
            ds = [(Fraction(1, 2 ** n), "Count the arrangements of the heads: C({0}, {1}) = {2}.".format(n, kk, cnt)), (Fraction(kk, n), "Count sequences out of 2^{0}.".format(n)), (Fraction(cnt, 2 * n), "The denominator is 2^{0} = {1}.".format(n, 2 ** n)), (Fraction(math.comb(n, kk + 1), 2 ** n), "That is the probability of exactly {0} heads.".format(kk + 1))]
        else:
            s = rng.randint(3, 11)
            cnt = sum(1 for i in range(1, 7) for j in range(1, 7) if i + j == s)
            val = Fraction(cnt, 36)
            prompt = rng.choice([f"Two fair six-sided dice are rolled. What is the probability that the sum of the numbers rolled is {s}?",
                                 f"What is the probability that the two numbers showing on a pair of fair dice add to {s}?"])
            expl = f"There are 36 equally likely outcomes; {cnt} of them have sum {s}: {cnt}/36 = {num_str(val)}."
            ds = [(Fraction(1, 36), "More than one pair of numbers adds to {0}.".format(s)), (Fraction(cnt, 12), "There are 36 outcomes, not 12."), (Fraction(1, 11), "The 11 possible sums are not equally likely."), (Fraction(cnt + 1, 36), "Recount the pairs that add to {0}.".format(s))]
    return _numeric_mc(rng, prompt, val, ds, subskill="simple_probability", explanation=expl, tags=["probability", "counting"], est=75 if d == "easy" else 95, verify=f"val={num_str(val)}")


# ---- area_volume ----------------------------------------------------------- #
def av_inscribed(rng, d):
    """Shaded regions: circle in square, square in circle, semicircle on rectangle (π-strings)."""
    if d == "easy":
        r = rng.randint(2, 40)
        s = 2 * r
        prompt = rng.choice([f"A circle of radius {r} is inscribed in a square. What is the area of the region inside the square but outside the circle, in terms of π?",
                             f"A circular table top of radius {r} inches is cut from a square board whose sides equal the circle's diameter. What is the area of the board left over, in square inches, in terms of π?"])
        correct = f"{s * s} − {r * r}π"
        ds = [(f"{s * s} − {2 * r}π", "Use the circle's area πr², not its circumference."), (f"{r * r} − {r * r}π", "The square's side is 2r = {0}, so its area is {1}.".format(s, s * s)), (f"{r * r}π − {s * s}", "Subtract the circle from the square, not the reverse."), (f"{s * s} − {s * s}π", "The circle's radius is {0}, not {1}.".format(r, s))]
        expl = f"Square side = diameter = {s}, area {s * s}; circle area π·{r}² = {r * r}π; shaded = {correct}."
    elif d == "medium":
        r = rng.randint(2, 40)
        # square inscribed in circle: diagonal 2r, area = 2r^2
        prompt = rng.choice([f"A square is inscribed in a circle of radius {r}. What is the area of the region inside the circle but outside the square, in terms of π?",
                             f"The vertices of a square lie on a circle of radius {r}. What is the total area of the four regions between the square and the circle, in terms of π?"])
        correct = f"{r * r}π − {2 * r * r}"
        ds = [(f"{r * r}π − {4 * r * r}", "The square's diagonal is 2r, so its area is (2r)²/2 = 2r², not (2r)²."), (f"{r * r}π − {r * r}", "The square's area is 2r², not r²."), (f"{2 * r * r} − {r * r}π", "Subtract the square from the circle."), (f"{2 * r}π − {2 * r * r}", "Use the circle's area, not its circumference.")]
        expl = f"The square's diagonal equals the diameter {2 * r}; its area is d²/2 = {2 * r * r}. Circle area = {r * r}π. Shaded = {correct}."
    else:
        w, h = rng.choice([4, 6, 8, 10, 12, 14, 16, 20]), rng.randint(3, 15)
        r = w // 2
        prompt = f"A figure consists of a rectangle {w} by {h} with a semicircle attached along one of its sides of length {w}. What is the total area of the figure, in terms of π?"
        correct = f"{w * h} + {Fraction(r * r, 2)}π" if (r * r) % 2 else f"{w * h} + {r * r // 2}π"
        half = Fraction(r * r, 2)
        ds = [(f"{w * h} + {r * r}π", "A semicircle has half the area of a full circle."), (f"{w * h} + {num_str(Fraction(w * w, 2))}π", "The radius is half of {0}, i.e. {1}.".format(w, r)), (f"{w * h} + {num_str(Fraction(r, 2))}π", "The semicircle's area is ½πr², not ½πr."), (f"{2 * (w + h)} + {num_str(half)}π", "Add areas, not perimeters.")]
        expl = f"Rectangle area {w}·{h} = {w * h}; semicircle radius {r}, area ½π·{r}² = {num_str(half)}π; total {correct}."
    return _text_mc(rng, prompt, correct, ds, subskill="area", explanation=expl, tags=["geometry", "area", "inscribed"], est=90 if d != "easy" else 80, verify=correct)


def av_composite_shapes(rng, d):
    """L-shapes, frames, and figures built from rectangles and triangles."""
    if d == "easy":
        W, H = rng.randint(8, 20), rng.randint(8, 20)
        a, b = rng.randint(2, W - 3), rng.randint(2, H - 3)
        prompt = f"An L-shaped floor is formed by removing a {a}-foot by {b}-foot rectangle from one corner of a {W}-foot by {H}-foot rectangle. What is the area of the floor, in square feet?"
        val = W * H - a * b
        expl = f"{W}·{H} − {a}·{b} = {W * H} − {a * b} = {val}."
        ds = [(W * H, "Subtract the removed corner."), (W * H - a - b, "Subtract the corner's AREA a·b."), ((W - a) * (H - b), "Only one corner rectangle is removed, not strips along two sides."), (val + a * b // 2, "Arithmetic slip.")]
    elif d == "medium":
        W, H = rng.randint(10, 30), rng.randint(8, 25)
        t = rng.randint(1, min(W, H) // 3)
        prompt = f"A rectangular picture frame has outer dimensions {W} by {H} and a uniform border {t} units wide. What is the area of the border?"
        val = W * H - (W - 2 * t) * (H - 2 * t)
        expl = f"Outer area {W * H}; inner opening ({W} − {2 * t})({H} − {2 * t}) = {(W - 2 * t) * (H - 2 * t)}; border = {val}."
        ds = [(W * H - (W - t) * (H - t), "The border is on both sides, so subtract 2t from each dimension."), ((W - 2 * t) * (H - 2 * t), "That is the inner opening, not the border."), (2 * t * (W + H), "This double-counts the corners."), (val + t, "Arithmetic slip.")]
    else:
        b, h = rng.randint(4, 16), rng.randint(3, 12)
        rect_h = rng.randint(3, 12)
        if (b * h) % 2:
            b += 1
        prompt = f"A pentagon-shaped sign is made from a rectangle {b} wide and {rect_h} tall topped by a triangle with the same base {b} and height {h}. What is the area of the sign?"
        val = b * rect_h + b * h // 2
        expl = f"Rectangle {b}·{rect_h} = {b * rect_h}; triangle ½·{b}·{h} = {b * h // 2}; total {val}."
        ds = [(b * rect_h + b * h, "The triangle's area needs the factor ½."), (b * (rect_h + h), "The top is a triangle, not a rectangle."), (b * rect_h, "Include the triangle."), (val + b, "Arithmetic slip.")]
    return _numeric_mc(rng, prompt, val, ds, subskill="area", explanation=expl, tags=["geometry", "area", "composite"], est=85 if d != "hard" else 95, verify=f"val={val}")


def av_solids(rng, d):
    """Cones, spheres, pyramids, and prisms (π-strings or integers)."""
    if d == "easy":
        B, h = rng.randint(4, 60), rng.randint(2, 20)
        kind = rng.choice(["prism", "pyramid"])
        if kind == "prism":
            prompt = f"A prism has a base of area {B} and a height of {h}. What is its volume?"
            val = B * h
            expl = f"Volume of a prism = base area × height = {B}·{h} = {val}."
            ds = [(B * h // 3 if (B * h) % 3 == 0 else Fraction(B * h, 3), "The factor ⅓ is for pyramids and cones, not prisms."), (B + h, "Multiply, don't add."), (2 * B + h, "That is not a volume formula."), (val + B, "Arithmetic slip.")]
        else:
            B = 3 * rng.randint(2, 20)
            prompt = f"A pyramid has a base of area {B} and a height of {h}. What is its volume?"
            val = B * h // 3
            expl = f"Volume of a pyramid = ⅓ × base area × height = ⅓·{B}·{h} = {val}."
            ds = [(B * h, "A pyramid's volume is one third of the prism's."), (B * h // 2, "The factor is ⅓, not ½."), (B + h, "Multiply, don't add."), (val + h, "Arithmetic slip.")]
        return _numeric_mc(rng, prompt, val, ds, subskill="volume", explanation=expl, tags=["geometry", "volume", "solids"], est=70, verify=f"V={val}")
    if d == "medium":
        r = rng.randint(2, 12)
        h = 3 * rng.randint(1, 6)
        kind = rng.choice(["cone", "sphere"])
        if kind == "cone":
            coef = r * r * h // 3
            prompt = f"A cone has a radius of {r} and a height of {h}. What is its volume, in terms of π?"
            correct = f"{coef}π"
            ds = _pi_distractors(coef, [(r * r * h, "A cone's volume is ⅓πr²h."), (r * h // 3 if (r * h) % 3 == 0 else r * h, "Use r², not r."), (2 * r * h, "That is from a wrong formula; use ⅓πr²h."), (r * r * h // 2 if (r * r * h) % 2 == 0 else r * r, "The factor is ⅓, not ½.")])
            expl = f"V = ⅓πr²h = ⅓·π·{r}²·{h} = {coef}π."
        else:
            r = 3 * rng.randint(1, 5)
            coef = 4 * r ** 3 // 3
            prompt = f"What is the volume of a sphere with radius {r}, in terms of π?"
            correct = f"{coef}π"
            ds = _pi_distractors(coef, [(4 * r * r, "That is the surface area coefficient (4πr²)."), (r ** 3, "Multiply by 4/3."), (4 * r ** 3, "Divide by 3."), (Fraction(4, 3) * r * r if (Fraction(4, 3) * r * r).denominator == 1 else 2 * r ** 3, "Use r³, not r².")])
            expl = f"V = (4/3)πr³ = (4/3)·π·{r}³ = {coef}π."
        return _text_mc(rng, prompt, correct, ds, subskill="volume", explanation=expl, tags=["geometry", "volume", "solids"], est=85, verify=correct)
    r, h = rng.randint(2, 10), rng.randint(3, 15)
    kind = rng.choice(["cylinder_sa", "cone_in_cylinder", "sphere_sa"])
    if kind == "cylinder_sa":
        coef = 2 * r * r + 2 * r * h
        prompt = f"A closed cylinder has radius {r} and height {h}. What is its total surface area, in terms of π?"
        correct = f"{coef}π"
        ds = _pi_distractors(coef, [(2 * r * h, "Add the two circular ends (2πr²)."), (r * r + 2 * r * h, "There are two ends."), (r * r * h, "That is the volume coefficient."), (2 * r * r + r * h, "The side is 2πrh.")])
        expl = f"SA = 2πr² + 2πrh = 2π·{r}² + 2π·{r}·{h} = {coef}π."
    elif kind == "cone_in_cylinder":
        h = 3 * rng.randint(1, 5)
        coef = r * r * h - r * r * h // 3
        prompt = f"A cone with radius {r} and height {h} is carved out of a cylinder with the same radius and height. What is the volume of the remaining solid, in terms of π?"
        correct = f"{coef}π"
        ds = _pi_distractors(coef, [(r * r * h, "Subtract the cone's volume."), (r * r * h // 3, "That is the cone's volume, not what remains."), (r * r * h // 2 if (r * r * h) % 2 == 0 else r * r * h + 1, "The cone is ⅓ of the cylinder, so ⅔ remains."), (2 * r * h, "Use the volume formulas, πr²h and ⅓πr²h.")])
        expl = f"Cylinder {r * r * h}π minus cone ⅓·{r * r * h}π = {r * r * h // 3}π leaves {coef}π (two thirds of the cylinder)."
    else:
        coef = 4 * r * r
        prompt = f"What is the surface area of a sphere with radius {r}, in terms of π?"
        correct = f"{coef}π"
        ds = _pi_distractors(coef, [(r * r, "The surface area of a sphere is 4πr²."), (2 * r * r, "The factor is 4, not 2."), (4 * r ** 3 // 3 if (4 * r ** 3) % 3 == 0 else 4 * r ** 3, "That is the volume, (4/3)πr³."), (4 * r, "Use r², not r.")])
        expl = f"SA = 4πr² = 4π·{r}² = {coef}π."
    return _text_mc(rng, prompt, correct, ds, subskill="volume", explanation=expl, tags=["geometry", "surface-area", "solids"], est=95, verify=correct)


# ---- circles --------------------------------------------------------------- #
def ci_tangent(rng, d):
    """Tangent segments: right angle with the radius; distance from an external point."""
    a, b, c = _pyth_triple(rng, 120)
    if rng.random() < 0.5:
        a, b = b, a
    if d == "easy":
        prompt = rng.choice([f"A line is tangent to a circle of radius {a} at point T. A point P on the tangent line is {b} units from T. How far is P from the center of the circle?",
                             f"Segment PT is tangent to a circle with center O at point T. If OT = {a} and PT = {b}, what is the length of OP?"])
        val = c
        expl = f"The radius to the point of tangency is perpendicular to the tangent, so √({a}² + {b}²) = {c}."
        ds = [(a + b, "Use the Pythagorean theorem, not addition."), (c - 1, "Arithmetic slip."), (b, "That is the tangent segment length."), (a * b, "Don't multiply the legs.")]
    elif d == "medium":
        prompt = rng.choice([f"From a point P outside a circle, a tangent segment to the circle has length {b}. If P is {c} units from the center of the circle, what is the radius of the circle?",
                             f"PT is tangent to a circle with center O at T. If PT = {b} and OP = {c}, what is the radius of the circle?"])
        val = a
        expl = f"Radius ⟂ tangent, so r² = {c}² − {b}² = {c * c - b * b}; r = {a}."
        ds = [(c - b, "Subtract the squares, not the lengths."), (math.isqrt(c * c + b * b) if math.isqrt(c * c + b * b) ** 2 == c * c + b * b else c + 1, "The distance to the center is the hypotenuse; subtract."), (a + 1, "Arithmetic slip."), (b, "That is the tangent length, not the radius.")]
    else:
        prompt = rng.choice([f"A circle has radius {a}. From an external point P, the two tangent segments to the circle each have length {b}. What is the perimeter of the quadrilateral formed by P, the two points of tangency, and the center of the circle?",
                             f"Two tangent segments from a point P to a circle with center O each have length {b}, and the circle's radius is {a}. What is the perimeter of the kite with vertices P, O, and the two points of tangency?"])
        val = 2 * a + 2 * b
        expl = f"The quadrilateral has two radii ({a} each) and two tangent segments ({b} each): perimeter 2·{a} + 2·{b} = {val}."
        ds = [(a + b + c, "The distance from P to the center is a diagonal, not a side."), (2 * b, "Include the two radii."), (2 * a + 2 * b + 2 * c, "Diagonals are not part of the perimeter."), (a + b, "Each length appears twice.")]
    return _numeric_mc(rng, prompt, val, ds, subskill="circumference_area", explanation=expl, tags=["geometry", "circle", "tangent"], est=85 if d != "hard" else 100, verify=f"triple {a},{b},{c}")


def ci_inscribed_angle(rng, d):
    """Central vs inscribed angles; arc measures."""
    arc = rng.choice(range(20, 180, 2))
    if d == "easy":
        prompt = rng.choice([f"In a circle, a central angle measures {arc}°. What is the measure of the arc it intercepts?",
                             f"Points A and B lie on a circle with center O, and angle AOB measures {arc}°. What is the measure of minor arc AB?"])
        val = arc
        expl = "A central angle has the same measure as its intercepted arc."
        ds = [(arc // 2, "Halving applies to inscribed angles, not central angles."), (2 * arc, "Doubling applies when going from an inscribed angle to its arc."), (180 - arc, "Arcs and central angles are equal, not supplementary."), (360 - arc, "That is the measure of the rest of the circle.")]
    elif d == "medium":
        prompt = rng.choice([f"An inscribed angle in a circle intercepts an arc of {arc}°. What is the measure of the inscribed angle?",
                             f"Points A, B, and C lie on a circle, and arc AC (not containing B) measures {arc}°. What is the measure of angle ABC?"])
        val = arc // 2
        expl = f"An inscribed angle is half its intercepted arc: {arc}/2 = {arc // 2}°."
        ds = [(arc, "That is the central angle; the inscribed angle is half."), (2 * arc if 2 * arc <= 360 else arc + 10, "Halve, don't double."), (180 - arc // 2, "The inscribed angle is half the arc, not its supplement."), (arc // 2 + 5, "Arithmetic slip.")]
    else:
        ins = rng.choice(range(20, 90, 2))
        prompt = rng.choice([f"In a circle, an inscribed angle measures {ins}°. What is the measure of the central angle that intercepts the same arc?",
                             f"Chord AB of a circle with center O subtends an inscribed angle of {ins}° at a point on the major arc. What is the measure of angle AOB?"])
        val = 2 * ins
        expl = f"The central angle is twice the inscribed angle on the same arc: 2·{ins} = {2 * ins}°."
        ds = [(ins, "The central angle is twice the inscribed angle."), (ins // 2, "Double, don't halve."), (180 - ins, "They are not supplementary."), (360 - 2 * ins, "That is the reflex angle / rest of the circle.")]
    return _numeric_mc(rng, prompt, val, ds, subskill="arc_sector", explanation=expl, tags=["geometry", "circle", "inscribed"], est=70 if d == "easy" else 85, verify=f"val={val}")


def ci_ring(rng, d):
    """Annulus (ring) areas and sector-minus-triangle regions."""
    r = rng.randint(2, 25)
    R = r + rng.randint(1, 25)
    if d == "easy":
        prompt = f"Two concentric circles have radii {r} and {R}. What is the area of the ring between them, in terms of π?"
        coef = R * R - r * r
        correct = f"{coef}π"
        ds = _pi_distractors(coef, [((R - r) ** 2, "Subtract the areas, not the radii before squaring."), (R * R, "Subtract the inner circle."), (2 * (R - r), "Use areas (πr²), not circumferences."), (R * R + r * r, "Subtract, don't add.")])
        expl = f"π·{R}² − π·{r}² = {R * R}π − {r * r}π = {coef}π."
    elif d == "medium":
        k = rng.choice([2, 4])
        theta = 360 // k
        coef = Fraction(R * R - r * r, k)
        prompt = f"Two concentric circles have radii {r} and {R}. A {theta}° sector is cut from the ring between them. What is the area of that piece of the ring, in terms of π?"
        correct = f"{num_str(coef)}π"
        ds = _pi_distractors(coef, [(R * R - r * r, "Take the fraction {0}/360 = 1/{1} of the ring.".format(theta, k)), (Fraction(R * R, k), "Subtract the inner circle's part."), (Fraction((R - r) ** 2, k), "Square each radius before subtracting."), (Fraction(R * R - r * r, 2 * k), "The fraction is 1/{0}, not 1/{1}.".format(k, 2 * k))])
        expl = f"Ring area ({R * R} − {r * r})π = {R * R - r * r}π; a {theta}° sector is 1/{k} of it: {correct}."
    else:
        prompt = rng.choice([f"A quarter-circle of radius {R} has the right triangle formed by its two radii removed. What is the area of the remaining region, in terms of π?",
                             f"In a circle of radius {R}, a 90° sector is drawn and the triangle formed by the two radii and the chord is shaded. What is the area of the part of the sector that is NOT shaded, in terms of π?"])
        coef = Fraction(R * R, 4)
        tri = Fraction(R * R, 2)
        correct = f"{num_str(coef)}π − {num_str(tri)}"
        ds = [(f"{num_str(coef)}π − {R * R}", "The triangle's area is ½·R·R, not R²."), (f"{R * R}π − {num_str(tri)}", "A quarter circle has area ¼πR²."), (f"{num_str(tri)} − {num_str(coef)}π", "Subtract the triangle from the sector, not the reverse."), (f"{num_str(Fraction(R, 2))}π − {num_str(tri)}", "The sector's area uses R², not R.")]
        expl = f"Quarter circle ¼π·{R}² = {num_str(coef)}π; triangle ½·{R}·{R} = {num_str(tri)}; region = {correct}."
        return _text_mc(rng, prompt, correct, ds, subskill="arc_sector", explanation=expl, tags=["geometry", "circle", "segment"], est=100, verify=correct)
    return _text_mc(rng, prompt, correct, ds, subskill="circumference_area", explanation=expl, tags=["geometry", "circle", "ring"], est=85, verify=correct)


# ---- right_triangles --------------------------------------------------------- #
def rt_similar(rng, d):
    """Similar right triangles: proportional sides and the altitude to the hypotenuse."""
    a, b, c = _pyth_triple(rng, 65 if d != "hard" else 30)
    if rng.random() < 0.5:
        a, b = b, a
    if d == "easy":
        k = rng.randint(2, 6)
        prompt = f"Two right triangles are similar. The smaller has legs {a} and {b}. If the longer leg of the larger triangle is {max(a, b) * k}, what is the length of its hypotenuse?"
        val = c * k
        expl = f"Scale factor {max(a, b) * k}/{max(a, b)} = {k}; the smaller triangle's hypotenuse is {c}, so the larger's is {c * k}."
        ds = [(c + max(a, b) * (k - 1), "Scale multiplicatively, not by adding the difference."), (min(a, b) * k, "That is the shorter leg of the larger triangle."), (c, "The larger triangle is scaled up."), (c * (k + 1), "Recheck the scale factor.")]
    elif d == "medium":
        k = rng.choice([Fraction(1, 2), Fraction(3, 2), Fraction(5, 2), Fraction(2, 3), Fraction(3, 4), Fraction(4, 3)])
        if (a * k).denominator != 1 or (b * k).denominator != 1 or (c * k).denominator != 1:
            return rt_similar(rng, d)
        prompt = f"Right triangle PQR is similar to a right triangle with sides {a}, {b}, and {c}. If the hypotenuse of PQR is {num_str(c * k)}, what is the perimeter of PQR?"
        val = (a + b + c) * k
        expl = f"Scale factor {num_str(c * k)}/{c} = {num_str(k)}; perimeter = ({a} + {b} + {c})·{num_str(k)} = {num_str(val)}."
        ds = [(a + b + c, "Scale the perimeter by {0}.".format(num_str(k))), ((a + b) * k + c, "Scale the hypotenuse too (it's {0}).".format(num_str(c * k))), (Fraction(a * b, 2) * k * k, "That is roughly the area, not the perimeter."), (val + c * k, "Arithmetic slip.")]
    else:
        # altitude to hypotenuse: h = ab/c, segments a^2/c, b^2/c ; use triple scaled by c so values are integers
        A, B, C = a * c, b * c, c * c
        h = a * b
        prompt = rng.choice([f"In a right triangle with legs {A} and {B} and hypotenuse {C}, an altitude is drawn to the hypotenuse. What is the length of the altitude?",
                             f"A right triangle has legs of length {A} and {B}. What is the distance from the right-angle vertex to the hypotenuse?",
                             f"The legs of a right triangle are {A} and {B}, and its hypotenuse is {C}. What is the height of the triangle when the hypotenuse is taken as the base?"])
        val = h
        expl = f"Area two ways: ½·{A}·{B} = ½·{C}·h, so h = {A}·{B}/{C} = {h}."
        ds = [(Fraction(C, 2), "The altitude is not half the hypotenuse in general."), (min(A, B), "The altitude to the hypotenuse is shorter than either leg."), (Fraction(A * A, C), "That is the segment of the hypotenuse adjacent to leg {0}, not the altitude.".format(A)), (h + a, "Arithmetic slip.")]
        return _numeric_mc(rng, prompt, val, ds, subskill="pythagorean", explanation=expl, qtype="multi_step_math", tags=["geometry", "right-triangle", "altitude"], est=105, verify=f"h={h}")
    return _numeric_mc(rng, prompt, val, ds, subskill="pythagorean", explanation=expl, tags=["geometry", "right-triangle", "similar"], est=85, verify=f"val={num_str(val)}")


def rt_diagonal(rng, d):
    """Diagonals of rectangles, squares, and boxes."""
    a, b, c = _pyth_triple(rng, 50)
    if d == "easy":
        prompt = rng.choice([f"A rectangle is {a} by {b}. What is the length of its diagonal?", f"A rectangular field measures {a} meters by {b} meters. How long, in meters, is a straight path from one corner to the opposite corner?"])
        val = c
        expl = f"The diagonal is the hypotenuse of a right triangle with legs {a} and {b}: √({a}² + {b}²) = {c}."
        ds = [(a + b, "Use the Pythagorean theorem."), (c - 1, "Arithmetic slip."), ((a + b) // 2 if (a + b) % 2 == 0 else a + b + 1, "The diagonal is not the average of the sides."), (a * b, "Don't multiply the sides.")]
    elif d == "medium":
        dgl = rng.choice([v for v in range(2, 20)])
        prompt = rng.choice([f"A square has a diagonal of length {dgl}√2. What is the area of the square?", f"The diagonal of a square is {dgl}√2 units long. What is the perimeter of the square?"])
        if "area" in prompt:
            val = dgl * dgl
            expl = f"Side = diagonal/√2 = {dgl}; area = {dgl}² = {val}."
            ds = [(2 * dgl * dgl, "That is the square of the diagonal; the area is d²/2."), (4 * dgl, "That is the perimeter."), (dgl, "That is the side length."), (val + dgl, "Arithmetic slip.")]
        else:
            val = 4 * dgl
            expl = f"Side = {dgl}√2/√2 = {dgl}; perimeter = 4·{dgl} = {val}."
            ds = [(dgl * dgl, "That is the area."), (dgl, "That is one side."), (2 * dgl, "A square has four sides."), (val + 4, "Arithmetic slip.")]
    else:
        # box diagonal with integer result: (a, b, c) triple and then (c, d, e) triple
        p, q, r = _pyth_triple(rng, 65)
        base_diag = r
        # find triple with leg r
        cands = [(r, y, z) for y in range(1, 120) for z in range(r + 1, 160) if r * r + y * y == z * z]
        if not cands:
            return rt_diagonal(rng, d)
        _, hgt, space = rng.choice(cands)
        prompt = rng.choice([f"A rectangular box has length {p}, width {q}, and height {hgt}. What is the length of the longest straight rod that fits inside the box (its space diagonal)?",
                             f"What is the length of the diagonal connecting opposite corners of a {p} by {q} by {hgt} rectangular box?"])
        val = space
        expl = f"Space diagonal = √({p}² + {q}² + {hgt}²) = √({p * p} + {q * q} + {hgt * hgt}) = {space}."
        ds = [(base_diag, "That is only the diagonal of the base; include the height."), (p + q + hgt, "Use the three-dimensional Pythagorean theorem."), (space + 1, "Arithmetic slip."), (math.isqrt(p * p + hgt * hgt) if math.isqrt(p * p + hgt * hgt) ** 2 == p * p + hgt * hgt else space - 1, "Include all three dimensions.")]
        return _numeric_mc(rng, prompt, val, ds, subskill="pythagorean", explanation=expl, qtype="multi_step_math", tags=["geometry", "right-triangle", "diagonal", "3d"], est=100, verify=f"{p},{q},{hgt}->{space}")
    return _numeric_mc(rng, prompt, val, ds, subskill="pythagorean", explanation=expl, tags=["geometry", "right-triangle", "diagonal"], est=80, verify=f"val={val}")


# ---- trigonometry -------------------------------------------------------------- #
_SPECIAL = {30: ("1/2", "√3/2", "√3/3"), 45: ("√2/2", "√2/2", "1"), 60: ("√3/2", "1/2", "√3")}


def tr_special_values(rng, d):
    """Exact trig values of 30°, 45°, 60° and expressions built from them."""
    ang = rng.choice([30, 45, 60])
    s, c, t = _SPECIAL[ang]
    if d == "easy":
        fn = rng.choice(["sin", "cos", "tan"])
        val = {"sin": s, "cos": c, "tan": t}[fn]
        prompt = rng.choice([f"What is the exact value of {fn} {ang}°?", f"{fn} {ang}° = ?"])
        others = {v for a2 in _SPECIAL for v in _SPECIAL[a2]} - {val}
        ds = [(o, f"That is the value of a different ratio or angle; recall the {ang}° reference triangle.") for o in rng.sample(sorted(others), 4)]
        expl = f"In a {ang}° reference triangle, {fn} {ang}° = {val}."
    elif d == "medium":
        fn = rng.choice(["sin", "cos"])
        other = "cos" if fn == "sin" else "sin"
        val = {"sin": s, "cos": c}[fn]
        prompt = f"If {other} θ = {c if fn == 'sin' else s} and 0° < θ < 90°, what is the value of {fn} θ?"
        others = {v for a2 in _SPECIAL for v in _SPECIAL[a2]} - {val}
        ds = [(o, "Identify θ from the given value, then read the other ratio.") for o in rng.sample(sorted(others), 4)]
        expl = f"{other} θ = {c if fn == 'sin' else s} means θ = {ang}°, so {fn} θ = {val}."
    else:
        kind = rng.choice(["sum", "product", "identity"])
        if kind == "sum":
            prompt = "What is the value of sin 30° + cos 60°?"
            val = "1"
            ds = [("√3", "sin 30° = cos 60° = 1/2."), ("√3/2", "Both values are 1/2."), ("1/2", "Add the two halves."), ("2", "Each value is 1/2, so the sum is 1.")]
            expl = "sin 30° = 1/2 and cos 60° = 1/2; their sum is 1."
        elif kind == "product":
            prompt = "What is the value of (sin 60°)(cos 30°)?"
            val = "3/4"
            ds = [("√3/2", "Both factors are √3/2; multiply them."), ("1/2", "(√3/2)² = 3/4, not 1/2."), ("3/2", "Multiply the denominators too."), ("√3/4", "(√3)(√3) = 3.")]
            expl = "sin 60° = cos 30° = √3/2; (√3/2)² = 3/4."
        else:
            k = rng.randint(2, 9)
            prompt = f"What is the value of {k}sin²θ + {k}cos²θ?"
            val = str(k)
            ds = [("1", "sin²θ + cos²θ = 1, then multiply by {0}.".format(k)), (str(2 * k), "The identity gives 1, not 2."), (f"{k}sin 2θ", "This is not a double-angle expression."), ("0", "sin²θ + cos²θ = 1.")]
            expl = f"Factor: {k}(sin²θ + cos²θ) = {k}·1 = {k}."
    return _text_mc(rng, prompt, val, ds, subskill="sohcahtoa", explanation=expl, tags=["trigonometry", "special-angles"], est=70 if d != "hard" else 85, verify=f"{val}")


tr_special_values.small_space = True


def tr_identity(rng, d):
    """Pythagorean identity and tan = sin/cos with a given ratio."""
    adj, opp, hyp, fig = _trig_setup(rng)
    if d == "easy":
        prompt = f"If sin θ = {opp}/{hyp}, what is the value of sin²θ + cos²θ?"
        val = "1"
        ds = [(f"{opp * opp}/{hyp * hyp}", "That is sin²θ alone."), (f"{adj * adj}/{hyp * hyp}", "That is cos²θ alone."), (f"{opp + adj}/{hyp}", "Square the ratios; don't add sin and cos."), ("2", "The identity gives 1.")]
        expl = "For every angle, sin²θ + cos²θ = 1."
    elif d == "medium":
        prompt = f"If sin θ = {opp}/{hyp} and θ is acute, what is the value of cos²θ?"
        val = f"{adj * adj}/{hyp * hyp}"
        ds = [(f"{adj}/{hyp}", "That is cos θ, not cos²θ."), (f"{opp * opp}/{hyp * hyp}", "That is sin²θ."), (f"{hyp * hyp - opp}/{hyp * hyp}", "Subtract sin²θ = {0}/{1}, not sin θ.".format(opp * opp, hyp * hyp)), (f"{opp * opp}/{adj * adj}", "That is tan²θ.")]
        expl = f"cos²θ = 1 − sin²θ = 1 − {opp * opp}/{hyp * hyp} = {hyp * hyp - opp * opp}/{hyp * hyp} = {val}."
    else:
        prompt = f"If cos θ = {adj}/{hyp} and θ is acute, what is the value of tan θ?"
        g = math.gcd(opp, adj)
        val = f"{opp // g}/{adj // g}" if adj // g != 1 else f"{opp // g}"
        ds = [(f"{adj}/{opp}" if adj != opp else f"{hyp}/{opp}", "tan θ = sin θ/cos θ = opposite/adjacent, not the reciprocal."), (f"{opp}/{hyp}", "That is sin θ."), (f"{hyp}/{adj}", "That is sec θ, the reciprocal of cos θ."), (f"{adj * adj}/{hyp * hyp}", "That is cos²θ.")]
        expl = f"sin θ = √(1 − ({adj}/{hyp})²) = {opp}/{hyp}; tan θ = sin θ/cos θ = ({opp}/{hyp})/({adj}/{hyp}) = {opp}/{adj}" + (f" = {val}." if val != f"{opp}/{adj}" else ".")
    return _text_mc(rng, prompt, val, ds, subskill="sohcahtoa", explanation=expl, tags=["trigonometry", "identity"], est=80 if d != "hard" else 95, verify=f"{val}", stimulus=fig if d != "easy" else None)


tr_identity.small_space = True


# ---- registry extension ----------------------------------------------------- #
_NEW_GEN = {
    "linear_equations": [le_point_on_line, le_table_equation, le_rate_word, le_fraction_eq],
    "linear_inequalities": [li_not_solution, li_compound, li_interpret],
    "systems_of_equations": [sys_intersection_point, sys_dependent, sys_rate_word],
    "functions": [fn_rate_of_change, fn_graph_point],
    "quadratics": [q_complete_square, q_word, q_intercepts],
    "exponents_radicals": [ex_radical_ops, ex_exp_expressions],
    "polynomials": [poly_divide, poly_zeros],
    "ratios_percentages_units": [rp_tax_tip, rp_best_deal],
    "proportions": [pr_shadow, pr_fuel],
    "data_analysis": [da_interval_table, da_two_series],
    "statistics": [st_compare_tables, st_outlier_effect, st_quartiles],
    "probability": [pb_conditional_words, pb_geometric, pb_counting],
    "area_volume": [av_inscribed, av_composite_shapes, av_solids],
    "circles": [ci_tangent, ci_inscribed_angle, ci_ring],
    "right_triangles": [rt_similar, rt_diagonal],
    "trigonometry": [tr_special_values, tr_identity],
}
for _skill, _fns in _NEW_GEN.items():
    for _d in ("easy", "medium", "hard"):
        FAMILIES[_skill][_d].extend(_fns)
