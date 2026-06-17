"""Original SAT-style Math question generators.

Every item is constructed so the answer is computed (not authored), which makes
correctness machine-checkable. Distractors model common student errors and each
carries a rationale. All wording is original.
"""
from __future__ import annotations

import math
import random
from fractions import Fraction

from .util import mc, spr, num_str, shuffle_with_correct


def _numeric_mc(rng, prompt, correct, distractor_specs, *, subskill, explanation,
                est=70, tags=None, fmt=num_str, verify=None,
                qtype="multiple_choice", correct_note="Correct.", stimulus=None):
    """Assemble a numeric multiple-choice item with deduped distractors."""
    seen = {fmt(correct)}
    ds = []
    for val, rat in distractor_specs:
        s = fmt(val)
        if s in seen:
            continue
        seen.add(s)
        ds.append((s, rat))
    attempts = 0
    while len(ds) < 3:
        attempts += 1
        if attempts > 60:
            raise RuntimeError(
                f"could not build 3 distinct distractors for correct={correct!r}; "
                "provide more distinct distractors at the call site")
        if isinstance(correct, (int, float, Fraction)):
            delta = rng.choice([-5, -3, -2, -1, 1, 2, 3, 4, 6])
            cand = correct + delta
        else:
            continue  # string answers must supply 3 distinct distractors upfront
        s = fmt(cand)
        if s in seen:
            continue
        seen.add(s)
        ds.append((s, "This comes from a small arithmetic slip; recompute carefully."))
    ds = ds[:3]
    options, ci, rats = shuffle_with_correct(
        rng, (fmt(correct), correct_note), ds)
    return mc(prompt, options, ci, rats, subskill=subskill, explanation=explanation,
              qtype=qtype, est=est, tags=tags, verify=verify, stimulus=stimulus)


def _names():
    return ["Maya", "Liam", "Aria", "Noah", "Priya", "Diego", "Ivy", "Omar",
            "Lena", "Theo", "Zoe", "Caleb", "Nina", "Ravi", "Sora", "Jonas"]


# --------------------------------------------------------------------------- #
# Algebra
# --------------------------------------------------------------------------- #
def linear_equations(rng: random.Random, difficulty: str):
    if difficulty == "easy":
        a = rng.randint(2, 12)
        x = rng.randint(2, 20)
        b = rng.randint(1, 40)
        c = a * x + b
        prompt = f"If {a}x + {b} = {c}, what is the value of x?"
        explanation = (f"Subtract {b} from both sides: {a}x = {c - b}. "
                       f"Divide both sides by {a}: x = {x}.")
        if rng.random() < 0.4:  # grid-in (student-produced) variant
            return spr(prompt, x, subskill="one_variable", explanation=explanation,
                       tags=["algebra", "linear", "grid-in"], est=70,
                       verify=f"{a}*{x}+{b}={c}")
        return _numeric_mc(
            rng, prompt, x,
            [(x + 1, f"This adds 1 too many; {a}·{x+1}+{b} ≠ {c}."),
             (c - b, f"This is {a}x, not x; you still must divide by {a}."),
             (x - 1, "This is one less than the solution; recheck the subtraction.")],
            subskill="one_variable", explanation=explanation,
            tags=["algebra", "linear"], verify=f"{a}*{x}+{b}={c}",
            correct_note=f"Correct: {a}·{x}+{b}={c}.")
    if difficulty == "medium":
        a = rng.randint(3, 14)
        c = rng.randint(1, a - 1)  # ensure a != c
        x = rng.randint(2, 16)
        b = rng.randint(1, 25)
        # a x + b = c x + d  -> d = (a-c)x + b - ... solve forward
        d = (a - c) * x + b
        prompt = f"If {a}x + {b} = {c}x + {d}, what is the value of x?"
        explanation = (f"Bring x-terms together: {a}x − {c}x = {d} − {b}, so "
                       f"{a - c}x = {d - b}. Then x = {x}.")
        return _numeric_mc(
            rng, prompt, x,
            [(d - b, f"This is {a-c}x, not x; divide by {a-c}."),
             (x + 1, "Off by one; recheck moving terms across the equals sign."),
             (Fraction(d - b, a + c), "This divides by a+c instead of a−c.")],
            subskill="one_variable", explanation=explanation,
            tags=["algebra", "linear"], verify=f"x={x}")
    # hard: solve for slope/value in two-variable linear context
    m = rng.randint(2, 9)
    b = rng.randint(-12, 12)
    x1 = rng.randint(1, 9)
    x2 = x1 + rng.randint(2, 8)
    y1 = m * x1 + b
    y2 = m * x2 + b
    prompt = (f"A line passes through the points ({x1}, {y1}) and ({x2}, {y2}). "
              f"What is the slope of the line?")
    explanation = (f"Slope = (y₂ − y₁)/(x₂ − x₁) = ({y2} − {y1})/({x2} − {x1}) "
                   f"= {y2 - y1}/{x2 - x1} = {m}.")
    return _numeric_mc(
        rng, prompt, m,
        [(Fraction(x2 - x1, y2 - y1), "This inverts the slope formula (run over rise)."),
         (y2 - y1, "This is only the change in y; divide by the change in x."),
         (m + 1, "Off by one; recompute the differences.")],
        subskill="slope_intercept", explanation=explanation,
        tags=["algebra", "linear", "slope"], est=80, verify=f"slope={m}")


def linear_inequalities(rng: random.Random, difficulty: str):
    a = rng.randint(2, 12)
    x = rng.randint(2, 16)
    b = rng.randint(1, 30)
    c = a * x + b
    # a x + b <= c  -> x <= x ; we want the greatest integer value of x
    prompt = (f"What is the greatest integer value of x that satisfies "
              f"{a}x + {b} ≤ {c}?")
    explanation = (f"Subtract {b}: {a}x ≤ {c - b}. Divide by {a}: x ≤ {x}. "
                   f"The greatest integer is {x}.")
    return _numeric_mc(
        rng, prompt, x,
        [(x + 1, f"x={x+1} makes the left side exceed {c}."),
         (c - b, f"This is {a}x; divide by {a}."),
         (x - 1, "This satisfies the inequality but is not the greatest such value.")],
        subskill="one_variable", explanation=explanation,
        tags=["algebra", "inequality"], verify=f"x<= {x}")


def systems_of_equations(rng: random.Random, difficulty: str):
    x = rng.randint(1, 12)
    y = rng.randint(1, 12)
    a1, b1 = rng.randint(1, 6), rng.randint(1, 6)
    a2, b2 = rng.randint(1, 6), rng.randint(1, 6)
    # avoid parallel
    while a1 * b2 - a2 * b1 == 0:
        a2 = rng.randint(1, 5)
    c1 = a1 * x + b1 * y
    c2 = a2 * x + b2 * y
    target = rng.choice(["x", "y", "x+y"])
    if target == "x":
        val = x
    elif target == "y":
        val = y
    else:
        val = x + y
    prompt = (f"The system below has solution (x, y):\n"
              f"{a1}x + {b1}y = {c1}\n{a2}x + {b2}y = {c2}\n"
              f"What is the value of {target}?")
    explanation = (f"Solving the system gives x = {x} and y = {y}, so "
                   f"{target} = {val}.")
    return _numeric_mc(
        rng, prompt, val,
        [(x if target != "x" else y, "This is the other variable's value."),
         (val + 1, "Off by one; recheck the elimination step."),
         (abs(x - y) if target == "x+y" else val + 2,
          "This combines the variables incorrectly.")],
        subskill="elimination", explanation=explanation, qtype="multi_step_math",
        tags=["algebra", "systems"], est=90, verify=f"x={x},y={y}")


# --------------------------------------------------------------------------- #
# Advanced Math
# --------------------------------------------------------------------------- #
def functions(rng: random.Random, difficulty: str):
    if difficulty == "hard":
        a = rng.randint(1, 6)
        b = rng.randint(-9, 9)
        c = rng.randint(-12, 12)
        k = rng.randint(-5, 6)
        val = a * k * k + b * k + c
        fx = (f"{a}x² {'+' if b >= 0 else '−'} {abs(b)}x "
              f"{'+' if c >= 0 else '−'} {abs(c)}")
        prompt = (f"The function f is defined by f(x) = {fx}. "
                  f"What is the value of f({k})?")
        explanation = (f"f({k}) = {a}·({k})² + {b}·({k}) + {c} "
                       f"= {a*k*k} + {b*k} + {c} = {val}.")
        return _numeric_mc(
            rng, prompt, val,
            [(a * k + b * k + c, "This squares only the coefficient, not x."),
             (a * k * k - b * k + c, "Watch the sign on the middle term."),
             (val + a, "Arithmetic slip in squaring; recompute (k)².")],
            subskill="evaluate", explanation=explanation,
            tags=["functions", "quadratic"], est=80, verify=f"f({k})={val}")
    if difficulty == "medium":
        # Solve f(x) = N for x (one step beyond plugging in a value).
        a = rng.randint(2, 9)
        x = rng.randint(-7, 9)
        b = rng.randint(-12, 12)
        n = a * x + b
        prompt = (f"The function f is defined by f(x) = {a}x {'+' if b >= 0 else '−'} "
                  f"{abs(b)}. If f(x) = {n}, what is the value of x?")
        explanation = (f"Set {a}x {'+' if b >= 0 else '−'} {abs(b)} = {n}: "
                       f"{a}x = {n - b}, so x = {x}.")
        return _numeric_mc(
            rng, prompt, x,
            [(n - b, "This is a·x (before dividing by the coefficient a)."),
             (n + b, "Subtract b before dividing, don't add it."),
             (x + 1, "Off by one; recheck the division.")],
            subskill="interpret", explanation=explanation,
            tags=["functions", "solve"], est=80, verify=f"f({x})={n}")
    a = rng.randint(2, 12)
    b = rng.randint(-15, 15)
    k = rng.randint(-8, 10)
    val = a * k + b
    prompt = (f"The function f is defined by f(x) = {a}x + {b}. "
              f"What is the value of f({k})?")
    explanation = f"f({k}) = {a}·{k} + {b} = {a*k} + {b} = {val}."
    if val >= 0 and rng.random() < 0.4:  # grid-in variant (non-negative answers)
        return spr(prompt, val, subskill="evaluate", explanation=explanation,
                   tags=["functions", "linear", "grid-in"], est=70,
                   verify=f"f({k})={val}")
    return _numeric_mc(
        rng, prompt, val,
        [(a + k + b, "This adds k to the coefficient instead of multiplying."),
         (a * k - b, "Check the sign of the constant term."),
         (val + a, "Arithmetic slip; recompute a·k.")],
        subskill="evaluate", explanation=explanation,
        tags=["functions", "linear"], verify=f"f({k})={val}")


def _quad_str(b, c, a=1):
    """Format a·x² + b·x + c = 0, omitting unit coefficients and zero terms."""
    s = f"{a}x²" if a != 1 else "x²"
    if b != 0:
        term = "x" if abs(b) == 1 else f"{abs(b)}x"
        s += f" {'+' if b > 0 else '−'} {term}"
    if c != 0:
        s += f" {'+' if c > 0 else '−'} {abs(c)}"
    return s + " = 0"


def quadratics(rng: random.Random, difficulty: str):
    # Hard tier: discriminant reasoning (how many real solutions) instead of
    # reading roots off a pre-factored quadratic.
    if difficulty == "hard":
        cat = rng.choice([0, 1, 2])  # target number of real solutions
        a = rng.randint(1, 3)
        if cat == 1:                    # perfect square -> discriminant 0
            t = rng.randint(1, 6)
            b, c = 2 * a * t, a * t * t
        elif cat == 2:                  # two real roots -> negative c
            b, c = rng.randint(-8, 8), -rng.randint(1, 9)
        else:                           # no real roots -> small b, positive c
            b, c = rng.randint(-4, 4), rng.randint(5, 9)
        eq = _quad_str(b, c, a)
        disc = b * b - 4 * a * c
        others = [n for n in (0, 1, 2) if n != cat]
        ds = [(others[0], "Recompute the discriminant b²−4ac and use its sign."),
              (others[1], "The sign of b²−4ac decides the number of real roots."),
              (3, "A quadratic can have at most two real solutions.")]
        sign = ("positive (two roots)" if disc > 0 else
                "zero (one root)" if disc == 0 else "negative (no real roots)")
        return _numeric_mc(
            rng, f"How many distinct real solutions does {eq} have?", cat, ds,
            subskill="roots",
            explanation=(f"The discriminant is b²−4ac = {b}²−4·{a}·{c} = {disc}, "
                         f"which is {sign}."),
            tags=["quadratics", "discriminant"], est=90, verify=f"D={disc}")

    # Easy: small roots, sum/product. Medium: larger roots, identify a root.
    span = 9 if difficulty == "easy" else 14
    r1 = rng.randint(-span, -1)
    r2 = rng.randint(1, span)
    b = -(r1 + r2)
    c = r1 * r2
    eq = _quad_str(b, c)
    base = (f"The expression factors as (x − {r1})(x − {r2}) = 0, so the "
            f"solutions are x = {r1} and x = {r2}.")
    mode = (rng.choice(["sum", "product"]) if difficulty == "easy"
            else rng.choice(["greater_root", "lesser_root", "product"]))
    if mode == "sum":
        val = r1 + r2
        prompt = f"What is the sum of the solutions to {eq}?"
        explanation = base + f" Their sum is {val}."
        ds = [(r1 * r2, "This is the product of the roots, not the sum."),
              (-val, "This has the wrong sign; the sum of roots is −b/a."),
              (r2 - r1, "This subtracts the roots instead of adding them.")]
    elif mode == "product":
        val = r1 * r2
        prompt = f"What is the product of the solutions to {eq}?"
        explanation = base + f" Their product is {val}."
        ds = [(r1 + r2, "This is the sum of the roots, not the product."),
              (-val, "Watch the signs when multiplying the roots."),
              (abs(r1) * abs(r2) + 1, "Recheck the multiplication of the roots.")]
    elif mode == "lesser_root":
        val = min(r1, r2)
        prompt = f"What is the lesser of the two solutions to {eq}?"
        explanation = base + f" The lesser solution is {val}."
        ds = [(max(r1, r2), "This is the greater solution."),
              (-val, "Check the sign of the solution."),
              (r1 + r2, "This is the sum of the roots, not a single root.")]
    else:
        val = max(r1, r2)
        prompt = f"What is the greater of the two solutions to {eq}?"
        explanation = base + f" The greater solution is {val}."
        ds = [(min(r1, r2), "This is the lesser solution."),
              (-val, "Check the sign of the solution."),
              (r1 + r2, "This is the sum of the roots, not a single root.")]
    return _numeric_mc(
        rng, prompt, val, ds,
        subskill="roots", explanation=explanation,
        tags=["quadratics", "factoring"], est=85, verify=f"roots {r1},{r2}")


def _pow_distractors(rng, base, exp, specs):
    """Build 3 distinct power-string distractors (≠ base^exp), topping up with
    nearby exponents so string-answer items always have enough options."""
    correct = f"{base}^{exp}"
    seen = {correct}
    out = []
    for s, rat in specs:
        if s not in seen:
            seen.add(s)
            out.append((s, rat))
    k = 1
    while len(out) < 3:
        for cand in (exp + k, exp - k):
            s = f"{base}^{cand}"
            if s not in seen:
                seen.add(s)
                out.append((s, "Recompute the exponent step by step."))
                if len(out) == 3:
                    break
        k += 1
    return out[:3]


def exponents_radicals(rng: random.Random, difficulty: str):
    base = rng.randint(2, 9)
    if difficulty == "easy":
        # Product rule: add the exponents.
        m, n = rng.randint(2, 8), rng.randint(2, 6)
        while m + n == m * n:           # avoid add/multiply distractor collision
            n = rng.randint(2, 5)
        exp = m + n
        prompt = f"Which of the following is equal to {base}^{m} · {base}^{n}?"
        ds = _pow_distractors(rng, base, exp, [
            (f"{base}^{m * n}", "When multiplying powers you add the exponents, not multiply them."),
            (f"{base * base}^{m + n}", "The base does not change when multiplying powers."),
            (f"{base}^{abs(m - n)}", "Subtracting exponents applies to division, not multiplication.")])
        expl = (f"Multiplying powers with the same base adds exponents: "
                f"{base}^{m}·{base}^{n} = {base}^{exp}.")
    elif difficulty == "medium":
        if rng.random() < 0.5:
            # Quotient rule: subtract the exponents.
            m, n = rng.randint(6, 12), rng.randint(2, 5)
            exp = m - n
            prompt = f"Which of the following is equal to {base}^{m} ÷ {base}^{n}?"
            ds = _pow_distractors(rng, base, exp, [
                (f"{base}^{m + n}", "Dividing powers subtracts exponents; it doesn't add them."),
                (f"{base}^{m * n}", "Don't multiply the exponents when dividing."),
                (f"1^{m - n}", "The base stays the same; only the exponents subtract.")])
            expl = (f"Dividing powers with the same base subtracts exponents: "
                    f"{base}^{m} ÷ {base}^{n} = {base}^{exp}.")
        else:
            # Power of a power: multiply the exponents (avoid m=n=2 collisions).
            m, n = rng.randint(2, 6), rng.randint(2, 4)
            while m + n == m * n:
                m = rng.randint(3, 6)
            exp = m * n
            prompt = f"Which of the following is equal to ({base}^{m})^{n}?"
            ds = _pow_distractors(rng, base, exp, [
                (f"{base}^{m + n}", "A power of a power multiplies the exponents, not adds them."),
                (f"{base * n}^{m}", "The base is unchanged by an outer exponent.")])
            expl = (f"A power raised to a power multiplies exponents: "
                    f"({base}^{m})^{n} = {base}^{exp}.")
    else:
        # Hard: combine rules, with a negative exponent (reciprocal) in the result.
        m, n = rng.randint(2, 5), rng.randint(2, 4)
        while m + n == m * n:
            m = rng.randint(3, 5)
        p = m * n + rng.randint(1, 6)     # guarantees exp < 0
        exp = m * n - p
        prompt = f"Which of the following is equal to ({base}^{m})^{n} ÷ {base}^{p}?"
        ds = _pow_distractors(rng, base, exp, [
            (f"{base}^{m * n + p}", "Dividing subtracts the exponent; it doesn't add it."),
            (f"{base}^{m + n - p}", "A power of a power multiplies (m·n), it doesn't add."),
            (f"{base}^{abs(exp)}", "Watch the sign: m·n − p is negative here.")])
        expl = (f"Work in order: ({base}^{m})^{n} = {base}^{m * n}, then ÷ {base}^{p} "
                f"subtracts to {base}^{exp}. A negative exponent is a reciprocal: "
                f"{base}^{exp} = 1/{base}^{abs(exp)}.")
    return _numeric_mc(
        rng, prompt, f"{base}^{exp}", ds, subskill="exponent_rules",
        explanation=expl, tags=["exponents"], fmt=str, est=85,
        verify=f"{base}^{exp}")


def _binom_str(coef, const):
    """Format (x + k) or (m x − k) style binomials for factor choices."""
    lead = "x" if coef == 1 else f"{coef}x"
    return f"({lead} {'+' if const >= 0 else '−'} {abs(const)})"


def polynomials(rng: random.Random, difficulty: str):
    # Hard: factor a quadratic trinomial (choose the correct binomial factor).
    if difficulty == "hard":
        r1 = rng.randint(-9, -1)
        r2 = rng.randint(1, 9)
        b = -(r1 + r2)          # x² + b x + c  with c = r1*r2
        c = r1 * r2
        tri = _quad_str(b, c).replace(" = 0", "")
        correct = _binom_str(1, -r1)        # (x − r1)
        true_roots = {r1, r2}
        # Fake roots: distinct from both real roots, each giving a wrong factor.
        fakes = []
        for w in (-r1, -r2, r1 + 1, r2 + 1, r1 - 1, r2 - 1, r1 + 2, r2 + 2):
            if w not in true_roots and w not in fakes:
                fakes.append(w)
            if len(fakes) == 3:
                break
        ds = [(_binom_str(1, -w),
               "Expanding this doesn't reproduce the trinomial; its root isn't a "
               "solution.") for w in fakes]
        return _numeric_mc(
            rng, f"Which of the following is a factor of {tri}?", correct, ds,
            subskill="factoring",
            explanation=(f"{tri} factors as (x − {r1})(x − {r2}); the roots are "
                         f"{r1} and {r2}, so (x − {r1}) is a factor."),
            tags=["polynomials", "factoring"], fmt=str, est=90,
            verify=f"roots {r1},{r2}")

    # Easy/medium: expand (a x + b)(c x + d) and read a coefficient. Medium
    # allows negative terms and asks for any of the three coefficients.
    if difficulty == "easy":
        a, c = rng.randint(1, 6), rng.randint(1, 6)
        b, d = rng.randint(1, 9), rng.randint(1, 9)
        target = "x"
    else:
        a, c = rng.randint(1, 7), rng.randint(1, 7)
        b = rng.choice([-1, 1]) * rng.randint(2, 9)
        d = rng.choice([-1, 1]) * rng.randint(2, 9)
        target = rng.choice(["x", "x2", "const"])
    expr = _binom_str(a, b) + _binom_str(c, d)
    x2, x1, const = a * c, a * d + b * c, b * d
    if target == "x2":
        val = x2
        prompt = f"In the expansion of {expr}, what is the coefficient of x²?"
        expl = f"The x² term is {a}x·{c}x = {x2}x²."
        ds = [(x1, "This is the coefficient of x, not x²."),
              (const, "This is the constant term, not the x² coefficient."),
              (a + c, "Multiply the leading coefficients; don't add them.")]
    elif target == "const":
        val = const
        prompt = f"In the expansion of {expr}, what is the constant term?"
        expl = f"The constant term is {b}·{d} = {const}."
        ds = [(x1, "This is the coefficient of x, not the constant."),
              (x2, "This is the coefficient of x², not the constant."),
              (b + d, "Multiply the constants; don't add them.")]
    else:
        val = x1
        prompt = f"In the expansion of {expr}, what is the coefficient of x?"
        expl = (f"Using FOIL, the x-terms are {a}x·{d} and {b}·{c}x, giving "
                f"({a}·{d} + {b}·{c}) = {x1}.")
        ds = [(x2, "This is the coefficient of x², not x."),
              (const, "This is the constant term, not the x coefficient."),
              (a * d, "This includes only one of the two x-terms.")]
    return _numeric_mc(
        rng, prompt, val, ds, subskill="operations", explanation=expl,
        tags=["polynomials", "foil"], est=80, verify=f"x2={x2},x={x1},c={const}")


# --------------------------------------------------------------------------- #
# Problem-Solving and Data Analysis
# --------------------------------------------------------------------------- #
def ratios_percentages_units(rng: random.Random, difficulty: str):
    # Easy: "what is P% of N".
    if difficulty == "easy":
        whole = rng.randint(20, 80) * 5
        pct = rng.choice([10, 15, 20, 25, 30, 40, 60, 75])
        val = whole * pct // 100
        prompt = f"What is {pct}% of {whole}?"
        explanation = f"{pct}% of {whole} = {pct}/100 × {whole} = {val}."
        return _numeric_mc(
            rng, prompt, val,
            [(whole * pct, "You forgot to divide by 100."),
             (val * 2, "This doubles the correct value."),
             (whole - val, "This is the remaining amount, not the part asked for.")],
            subskill="percent_change", explanation=explanation,
            tags=["percent"], verify=f"{pct}% of {whole}={val}")
    # Medium: percent increase or decrease (compute the percent).
    if difficulty == "medium":
        old = rng.randint(20, 60)
        pct = rng.choice([10, 20, 25, 50])
        up = rng.random() < 0.5
        new = old + old * pct // 100 if up else old - old * pct // 100
        word = "increase" if up else "decrease"
        prompt = (f"A quantity changes from {old} to {new}. "
                  f"What is the percent {word}?")
        explanation = (f"Percent {word} = |new − old|/old × 100 = "
                       f"|{new} − {old}|/{old} × 100 = {pct}%.")
        return _numeric_mc(
            rng, prompt, pct,
            [(abs(new - old), "This is the raw change, not the percent change."),
             (abs(new - old) * 100 // new, "Divide by the original value, not the new value."),
             (pct + 5, "Recheck the division; the percent is off.")],
            subskill="percent_change", explanation=explanation,
            tags=["percent", "change"], fmt=lambda v: f"{v}%", est=80,
            verify=f"{word}={pct}%")
    # Hard: reverse percent — recover the original before a known % change.
    pct = rng.choice([10, 20, 25, 50])
    original = rng.randint(4, 24) * 20      # keeps the result an integer
    up = rng.random() < 0.5
    new = original + original * pct // 100 if up else original - original * pct // 100
    word = "increase" if up else "decrease"
    prompt = (f"After a {pct}% {word}, a quantity is {new}. "
              f"What was the original value?")
    factor = f"(1 {'+' if up else '−'} {pct}/100)"
    explanation = (f"new = original × {factor}, so original = {new} ÷ {factor} = "
                   f"{original}.")
    return _numeric_mc(
        rng, prompt, original,
        [(new + new * pct // 100 if up else new - new * pct // 100,
          f"This applies the {word} to the new value instead of reversing it."),
         (new, "This is the value after the change, not the original.")],
        subskill="percent_change", explanation=explanation,
        tags=["percent", "reverse"], est=90, verify=f"orig={original}")


def proportions(rng: random.Random, difficulty: str):
    # Hard: inverse proportion (more workers -> less time).
    if difficulty == "hard":
        w1 = rng.randint(2, 6)
        w2 = rng.choice([w for w in range(2, 9) if w != w1])
        per_worker = rng.randint(2, 8)          # keeps the answer an integer
        h1 = per_worker * w2
        val = per_worker * w1                   # = w1*h1 / w2
        prompt = (f"It takes {w1} workers {h1} hours to finish a job. Working at the "
                  f"same rate, how many hours would it take {w2} workers?")
        explanation = (f"Total work = {w1}×{h1} = {w1 * h1} worker-hours. With {w2} "
                       f"workers: {w1 * h1} ÷ {w2} = {val} hours.")
        return _numeric_mc(
            rng, prompt, val,
            [(h1 * w2 // w1, "More workers means less time; this scales the wrong way."),
             (h1, "This ignores the change in the number of workers."),
             (w1 * h1, "This is the total worker-hours, not the time for {0} workers.".format(w2))],
            subskill="scaling", explanation=explanation,
            tags=["proportion", "inverse"], est=95, verify=f"t={val}")
    # Medium: find the unit rate first, then scale to a non-multiple amount.
    if difficulty == "medium":
        per = rng.randint(2, 9)                  # cost/output per single unit
        n1 = rng.randint(2, 6)
        n2 = rng.choice([k for k in range(7, 20) if k != n1])
        c1 = per * n1
        val = per * n2
        thing, money = rng.choice([("notebooks", "$"), ("tickets", "$"), ("bags", "$")])
        prompt = (f"{n1} {thing} cost {money}{c1}. At the same rate, how much do "
                  f"{n2} {thing} cost?")
        explanation = (f"Unit rate = {money}{c1} ÷ {n1} = {money}{per} each, so "
                       f"{n2} × {money}{per} = {money}{val}.")
        return _numeric_mc(
            rng, prompt, val,
            [(c1 * n2, "You forgot to divide by the first quantity to get the unit rate."),
             (c1 + (n2 - n1), "This adds the extra count instead of scaling by the rate."),
             (per * (n2 - n1), "This prices only the additional items, not all of them.")],
            subskill="scaling", explanation=explanation,
            tags=["proportion", "unit-rate"], est=85, verify=f"cost={val}")
    # Easy: direct proportion at a clean multiple of the given rate.
    rate_n = rng.randint(2, 15)
    rate_d = rng.randint(2, 9)
    mult = rng.randint(3, 12)
    given = rate_d * mult
    val = rate_n * mult
    unit = rng.choice([("miles", "hours"), ("pages", "minutes"), ("dollars", "items")])
    prompt = (f"A machine produces {rate_n} {unit[0]} every {rate_d} {unit[1]}. "
              f"At this rate, how many {unit[0]} does it produce in {given} {unit[1]}?")
    explanation = (f"Set up the proportion {rate_n}/{rate_d} = x/{given}. "
                   f"Then x = {rate_n}×{given}/{rate_d} = {val}.")
    return _numeric_mc(
        rng, prompt, val,
        [(rate_n * given, "You forgot to divide by the rate's denominator."),
         (given - rate_d, "This subtracts instead of scaling proportionally."),
         (val + rate_n, "Off by one multiple; recheck the scale factor.")],
        subskill="scaling", explanation=explanation,
        tags=["proportion", "rate"], est=80, verify=f"x={val}")


def data_analysis(rng: random.Random, difficulty: str):
    n = 4 if difficulty == "easy" else 5
    cats = rng.sample(["Mon", "Tue", "Wed", "Thu", "Fri"], n)
    vals = [rng.randint(10, 40) for _ in cats]
    if difficulty != "easy":
        vals[-1] += (n - sum(vals) % n) % n      # make the mean an integer
    headers = ["Day", "Tickets sold"]
    rows = [[c, str(v)] for c, v in zip(cats, vals)]
    total = sum(vals)
    table = {"type": "table", "table": {"caption": "Daily ticket sales",
                                        "headers": headers, "rows": rows}}
    if difficulty == "medium":
        mean = total // n
        prompt = "Based on the table, what is the mean number of tickets sold per day?"
        return _numeric_mc(
            rng, prompt, mean,
            [(max(vals), "This is the busiest day, not the average."),
             (max(vals) - min(vals), "This is the range, not the mean."),
             (total, "This is the total; divide by the number of days.")],
            subskill="tables", explanation=(
                f"Mean = total ÷ days = {total} ÷ {n} = {mean}."),
            qtype="data_interpretation", tags=["data", "table"], est=85,
            stimulus=table, verify=f"mean={mean}")
    if difficulty == "hard":
        mean = total // n
        val = max(vals) - mean
        busy = cats[vals.index(max(vals))]
        prompt = ("Based on the table, how many more tickets than the daily mean "
                  "were sold on the busiest day?")
        return _numeric_mc(
            rng, prompt, val,
            [(max(vals), "This is the busiest day's total, not its excess over the mean."),
             (mean, "This is the mean itself, not the amount above it."),
             (max(vals) - min(vals), "This compares to the least day, not the mean.")],
            subskill="tables", explanation=(
                f"Mean = {total} ÷ {n} = {mean}. The busiest day ({busy}) sold "
                f"{max(vals)}, which is {max(vals)} − {mean} = {val} above the mean."),
            qtype="data_interpretation", tags=["data", "table"], est=95,
            stimulus=table, verify=f"excess={val}")
    qmode = rng.choice(["total", "max", "diff"])
    if qmode == "total":
        prompt = "Based on the table, how many tickets were sold in all four days combined?"
        val = total
        expl = f"Add the four values: {' + '.join(map(str, vals))} = {total}."
        ds = [(max(vals), "This is only the largest single day."),
              (total - min(vals), "This omits the smallest day."),
              (total + min(vals), "This double-counts the smallest day.")]
    elif qmode == "max":
        val = max(vals)
        day = cats[vals.index(val)]
        prompt = "Based on the table, how many tickets were sold on the busiest day?"
        expl = f"The largest value in the table is {val} (on {day})."
        ds = [(min(vals), "This is the least busy day."),
              (total // 4, "This is the average, not the maximum."),
              (sorted(vals)[-2], "This is the second-largest value.")]
    else:
        val = max(vals) - min(vals)
        prompt = ("Based on the table, what is the difference between the greatest "
                  "and least number of tickets sold in a single day?")
        expl = f"The greatest is {max(vals)} and the least is {min(vals)}; the difference is {val}."
        ds = [(max(vals), "This is only the greatest value."),
              (total, "This is the total, not the difference."),
              (val + 2, "Recheck the subtraction.")]
    return _numeric_mc(
        rng, prompt, val, ds,
        subskill="tables", explanation=expl, qtype="data_interpretation",
        tags=["data", "table"], est=80,
        stimulus={"type": "table", "table": {"caption": "Daily ticket sales",
                                             "headers": headers, "rows": rows}},
        verify=f"val={val}")


def statistics(rng: random.Random, difficulty: str):
    n = 5
    # Hard: find a missing value given the mean (work backwards from the total).
    if difficulty == "hard":
        target_mean = rng.randint(8, 16)
        four = [rng.randint(2, 20) for _ in range(4)]
        missing = target_mean * n - sum(four)
        while not (1 <= missing <= 30):          # keep it a sensible value
            four = [rng.randint(2, 20) for _ in range(4)]
            missing = target_mean * n - sum(four)
        shown = ", ".join(map(str, four))
        prompt = (f"The mean of 5 numbers is {target_mean}. Four of the numbers are "
                  f"{shown}. What is the fifth number?")
        explanation = (f"The five numbers total {target_mean}×5 = {target_mean * n}. "
                       f"The four shown total {sum(four)}, so the fifth is "
                       f"{target_mean * n} − {sum(four)} = {missing}.")
        return _numeric_mc(
            rng, prompt, missing,
            [(target_mean, "This is the mean itself, not the missing value."),
             (sum(four), "This is the sum of the four shown numbers."),
             (target_mean * n, "This is the total of all five; subtract the four shown.")],
            subskill="mean_median_mode", explanation=explanation,
            tags=["statistics", "mean"], est=95, verify=f"missing={missing}")
    # Medium: range or mode.
    if difficulty == "medium":
        if rng.random() < 0.5:
            data = sorted(rng.randint(2, 30) for _ in range(6))
            val = max(data) - min(data)
            prompt = (f"What is the range of the data set {', '.join(map(str, data))}?")
            explanation = (f"Range = greatest − least = {max(data)} − {min(data)} = {val}.")
            ds = [(max(data), "This is the greatest value, not the range."),
                  (sum(data) // len(data), "This is the mean, not the range."),
                  (data[len(data) // 2], "This is a middle value, not the range.")]
            return _numeric_mc(rng, prompt, val, ds, subskill="spread",
                               explanation=explanation, tags=["statistics", "range"],
                               est=80, verify=f"range={val}")
        # mode: build a set with one clear most-frequent value
        m = rng.randint(3, 15)
        data = [m, m, m] + rng.sample([x for x in range(2, 20) if x != m], 3)
        rng.shuffle(data)
        prompt = (f"What is the mode of the data set {', '.join(map(str, data))}?")
        explanation = f"The value {m} appears most often (three times), so it is the mode."
        ds = [(max(data), "This is the greatest value, not the most frequent."),
              (sum(data) // len(data), "This is the mean, not the mode."),
              (min(data), "This is the least value, not the most frequent.")]
        return _numeric_mc(rng, prompt, m, ds, subskill="mean_median_mode",
                           explanation=explanation, tags=["statistics", "mode"],
                           est=80, verify=f"mode={m}")
    data = sorted(rng.randint(2, 20) for _ in range(n))
    mode = rng.choice(["mean", "median"])
    if mode == "mean":
        s = sum(data)
        if s % n != 0:
            # adjust last to make integer mean for clean SPR
            data[-1] += n - (s % n)
            s = sum(data)
        val = s // n
        prompt = (f"What is the mean (average) of the data set "
                  f"{', '.join(map(str, data))}?")
        explanation = (f"Mean = sum / count = {s} / {n} = {val}.")
        ds = [(sorted(data)[n // 2], "This is the median, not the mean."),
              (max(data) - min(data), "This is the range, not the mean."),
              (val + 1, "Recheck the sum before dividing.")]
        return _numeric_mc(rng, prompt, val, ds, subskill="mean_median_mode",
                           explanation=explanation, tags=["statistics", "mean"],
                           est=80, verify=f"mean={val}")
    val = data[n // 2]
    prompt = (f"What is the median of the data set {', '.join(map(str, data))}?")
    explanation = (f"With the values in order, the middle (3rd of 5) value is {val}.")
    ds = [(sum(data) // n, "This is the mean, not the median."),
          (max(data) - min(data), "This is the range, not the median."),
          (data[0], "The median is the middle value, not the smallest.")]
    return _numeric_mc(rng, prompt, val, ds, subskill="mean_median_mode",
                       explanation=explanation, tags=["statistics", "median"],
                       est=70, verify=f"median={val}")


def probability(rng: random.Random, difficulty: str):
    red = rng.randint(2, 14)
    blue = rng.randint(2, 14)
    green = rng.randint(1, 10)
    total = red + blue + green
    counts = {"red": red, "blue": blue, "green": green}
    bag = (f"A bag contains {red} red, {blue} blue, and {green} green marbles. ")

    # Hard: two draws without replacement, both the same colour.
    if difficulty == "hard":
        color = rng.choice(["red", "blue"])
        k = counts[color]
        val = Fraction(k * (k - 1), total * (total - 1))
        prompt = (bag + f"If two marbles are drawn at random without replacement, "
                  f"what is the probability that both are {color}?")
        explanation = (f"P(both {color}) = {k}/{total} × {k - 1}/{total - 1} = "
                       f"{num_str(val)}.")
        return _numeric_mc(
            rng, prompt, val,
            [(Fraction(k, total) * Fraction(k, total),
              "Without replacement the second draw has one fewer marble of that colour and one fewer total."),
             (Fraction(k, total),
              "This is the probability for a single draw, not two."),
             (Fraction(k * (k - 1), total * total),
              "Reduce the total by one on the second draw as well.")],
            subskill="simple_probability", explanation=explanation,
            tags=["probability", "without-replacement"], est=95,
            verify=f"P={num_str(val)}")
    # Medium: complement, or the union of two colours.
    if difficulty == "medium":
        if rng.random() < 0.5:
            color = rng.choice(["red", "blue", "green"])
            k = counts[color]
            val = Fraction(total - k, total)
            prompt = (bag + f"If one marble is drawn at random, what is the "
                      f"probability that it is NOT {color}?")
            explanation = (f"P(not {color}) = ({total} − {k})/{total} = {num_str(val)}.")
            ds = [(Fraction(k, total), f"This is the probability of drawing {color}."),
                  (Fraction(total - k, k), "Keep the total in the denominator."),
                  (Fraction(k, total - k), "Compare favourable to total, not to the rest.")]
        else:
            c1, c2 = rng.sample(["red", "blue", "green"], 2)
            k = counts[c1] + counts[c2]
            val = Fraction(k, total)
            prompt = (bag + f"If one marble is drawn at random, what is the "
                      f"probability that it is {c1} or {c2}?")
            explanation = (f"P({c1} or {c2}) = ({counts[c1]} + {counts[c2]})/{total} "
                           f"= {num_str(val)}.")
            ds = [(Fraction(counts[c1], total), f"This counts only the {c1} marbles."),
                  (Fraction(total - k, total), "This is the probability of the third colour."),
                  (Fraction(k, total - k), "Use the total in the denominator.")]
        return _numeric_mc(rng, prompt, val, ds, subskill="simple_probability",
                           explanation=explanation, tags=["probability"], est=85,
                           verify=f"P={num_str(val)}")
    # Easy: single draw, one colour.
    pick = rng.choice([("red", red), ("blue", blue), ("green", green)])
    val = Fraction(pick[1], total)
    prompt = (bag + f"If one marble is drawn at random, what is the probability it "
              f"is {pick[0]}?")
    explanation = (f"There are {pick[1]} {pick[0]} marbles out of {total} total, so "
                   f"the probability is {pick[1]}/{total} = {num_str(val)}.")
    return _numeric_mc(
        rng, prompt, val,
        [(Fraction(pick[1], total - pick[1]), "Use the total count in the denominator, not the rest."),
         (Fraction(total - pick[1], total), "This is the probability of NOT drawing that colour."),
         (Fraction(pick[1], total) + Fraction(1, total), "Off by one marble; recount the favourable outcomes.")],
        subskill="simple_probability", explanation=explanation,
        tags=["probability"], est=80, verify=f"P={num_str(val)}")


# --------------------------------------------------------------------------- #
# Geometry and Trigonometry
# --------------------------------------------------------------------------- #
def area_volume(rng: random.Random, difficulty: str):
    if difficulty == "hard":
        l = rng.randint(2, 9)
        w = rng.randint(2, 9)
        h = rng.randint(2, 9)
        val = l * w * h
        prompt = (f"A rectangular box has length {l}, width {w}, and height {h}. "
                  f"What is its volume?")
        explanation = f"Volume = length × width × height = {l}×{w}×{h} = {val}."
        if rng.random() < 0.4:  # grid-in variant
            return spr(prompt, val, subskill="volume", explanation=explanation,
                       tags=["geometry", "volume", "grid-in"], est=75,
                       verify=f"V={val}")
        ds = [(2 * (l * w + l * h + w * h), "This is the surface area, not the volume."),
              (l + w + h, "This adds the dimensions instead of multiplying."),
              (l * w, "This is only the area of the base.")]
        return _numeric_mc(rng, prompt, val, ds, subskill="volume",
                           explanation=explanation, tags=["geometry", "volume"],
                           est=80, verify=f"V={val}")
    b = rng.randint(3, 12)
    h = rng.randint(3, 12)
    shape = rng.choice(["rectangle", "triangle"])
    if shape == "rectangle":
        val = b * h
        prompt = f"A rectangle has a base of {b} and a height of {h}. What is its area?"
        explanation = f"Area of a rectangle = base × height = {b}×{h} = {val}."
        ds = [(2 * (b + h), "This is the perimeter, not the area."),
              (b * h // 2, "Halving applies to triangles, not rectangles."),
              (b + h, "This adds the sides instead of multiplying.")]
    else:
        val = Fraction(b * h, 2)
        prompt = f"A triangle has a base of {b} and a height of {h}. What is its area?"
        explanation = f"Area of a triangle = ½ × base × height = ½×{b}×{h} = {num_str(val)}."
        ds = [(b * h, "You forgot the factor of ½."),
              (b + h, "This adds the dimensions instead of using the area formula."),
              (Fraction(b + h, 2), "Average of the sides is not the area.")]
    return _numeric_mc(rng, prompt, val, ds, subskill="area",
                       explanation=explanation, tags=["geometry", "area"],
                       est=70, verify=f"area={num_str(val)}")


def circles(rng: random.Random, difficulty: str):
    # Exclude r=2 (area 4π == circumference 4π) and r=4 (circ distractors collide).
    r = rng.choice([3, 5, 6, 7, 8, 9, 10, 11, 12])
    mode = rng.choice(["area", "circumference", "diameter"])
    if mode == "area":
        val = f"{r*r}π"
        prompt = f"A circle has radius {r}. What is its area, in terms of π?"
        explanation = f"Area = πr² = π·{r}² = {r*r}π."
        ds = [(f"{2*r}π", "This is the circumference, not the area."),
              (f"{r}π", "Area uses r², not r."),
              (f"{r*r*r}π", "Area uses r², not r³.")]
    elif mode == "circumference":
        val = f"{2*r}π"
        prompt = f"A circle has radius {r}. What is its circumference, in terms of π?"
        explanation = f"Circumference = 2πr = 2π·{r} = {2*r}π."
        ds = [(f"{r*r}π", "This is the area, not the circumference."),
              (f"{r}π", "Circumference is 2πr, so include the factor of 2."),
              (f"{4*r}π", "Recheck the formula 2πr.")]
    else:
        val = 2 * r
        prompt = (f"A circle has radius {r}. What is its diameter?")
        explanation = f"Diameter = 2 × radius = 2 × {r} = {2*r}."
        return _numeric_mc(rng, prompt, val,
                           [(r, "This is the radius, not the diameter."),
                            (r * r, "This squares the radius; diameter is 2r."),
                            (4 * r, "Diameter is 2r, not 4r.")],
                           subskill="circumference_area", explanation=explanation,
                           tags=["geometry", "circle"], est=60, verify=f"d={2*r}")
    return _numeric_mc(rng, prompt, val, ds, subskill="circumference_area",
                       explanation=explanation, tags=["geometry", "circle"],
                       fmt=str, est=75, verify=f"{val}")


def right_triangles(rng: random.Random, difficulty: str):
    triples = [(3, 4, 5), (6, 8, 10), (5, 12, 13), (8, 15, 17), (9, 12, 15),
               (7, 24, 25), (20, 21, 29), (9, 40, 41), (12, 16, 20), (10, 24, 26),
               (15, 20, 25), (12, 35, 37), (16, 30, 34), (18, 24, 30)]
    a, b, c = rng.choice(triples)
    find = rng.choice(["hyp", "leg"])
    if find == "hyp":
        prompt = (f"A right triangle has legs of length {a} and {b}. "
                  f"What is the length of the hypotenuse?")
        val = c
        explanation = (f"By the Pythagorean theorem, c² = {a}² + {b}² "
                       f"= {a*a} + {b*b} = {a*a+b*b}, so c = {c}.")
        ds = [(a + b, "You added the legs instead of using a²+b²=c²."),
              (c - 1, "Off by one; recompute the square root."),
              (a * b, "This multiplies the legs; use the Pythagorean theorem.")]
    else:
        prompt = (f"A right triangle has one leg of length {a} and a hypotenuse "
                  f"of length {c}. What is the length of the other leg?")
        val = b
        explanation = (f"By the Pythagorean theorem, leg = √(c² − a²) "
                       f"= √({c*c} − {a*a}) = √{c*c-a*a} = {b}.")
        ds = [(c - a, "Subtracting the lengths is not the Pythagorean theorem."),
              (b + 1, "Off by one; recompute c² − a²."),
              (c + a, "Add/subtract under the square root, not outside it.")]
    return _numeric_mc(rng, prompt, val, ds, subskill="pythagorean",
                       explanation=explanation, tags=["geometry", "right-triangle"],
                       est=85, verify=f"sides {a},{b},{c}")


def trigonometry(rng: random.Random, difficulty: str):
    triples = [(3, 4, 5), (6, 8, 10), (5, 12, 13), (8, 15, 17), (7, 24, 25),
               (20, 21, 29), (9, 40, 41), (12, 16, 20), (10, 24, 26), (15, 20, 25)]
    a, b, c = rng.choice(triples)  # a opposite angle θ, b adjacent, c hyp
    ratio = rng.choice(["sin", "cos", "tan"])
    if ratio == "sin":
        val = f"{a}/{c}"
        expl = f"sin θ = opposite/hypotenuse = {a}/{c}."
        ds = [(f"{b}/{c}", "That ratio is cosine (adjacent/hypotenuse)."),
              (f"{a}/{b}", "That ratio is tangent (opposite/adjacent)."),
              (f"{c}/{a}", "This inverts the sine ratio.")]
    elif ratio == "cos":
        val = f"{b}/{c}"
        expl = f"cos θ = adjacent/hypotenuse = {b}/{c}."
        ds = [(f"{a}/{c}", "That ratio is sine (opposite/hypotenuse)."),
              (f"{a}/{b}", "That ratio is tangent (opposite/adjacent)."),
              (f"{c}/{b}", "This inverts the cosine ratio.")]
    else:
        val = f"{a}/{b}"
        expl = f"tan θ = opposite/adjacent = {a}/{b}."
        ds = [(f"{a}/{c}", "That ratio is sine (opposite/hypotenuse)."),
              (f"{b}/{c}", "That ratio is cosine (adjacent/hypotenuse)."),
              (f"{b}/{a}", "This inverts the tangent ratio.")]
    prompt = (f"In a right triangle, the side opposite angle θ has length {a}, the "
              f"side adjacent to θ has length {b}, and the hypotenuse has length {c}. "
              f"What is {ratio} θ?")
    return _numeric_mc(rng, prompt, val, ds, subskill="sohcahtoa",
                       explanation=expl, tags=["trigonometry"], fmt=str,
                       est=85, verify=f"{ratio}={val}")
