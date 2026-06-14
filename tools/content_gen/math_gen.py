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
        a = rng.randint(2, 9)
        x = rng.randint(2, 12)
        b = rng.randint(1, 20)
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
        a = rng.randint(3, 9)
        c = rng.randint(1, a - 1)  # ensure a != c
        x = rng.randint(2, 10)
        b = rng.randint(1, 12)
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
    m = rng.randint(2, 6)
    b = rng.randint(-6, 6)
    x1 = rng.randint(1, 6)
    x2 = x1 + rng.randint(2, 5)
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
    a = rng.randint(2, 8)
    x = rng.randint(2, 9)
    b = rng.randint(1, 15)
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
    x = rng.randint(1, 8)
    y = rng.randint(1, 8)
    a1, b1 = rng.randint(1, 4), rng.randint(1, 4)
    a2, b2 = rng.randint(1, 4), rng.randint(1, 4)
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
        a = rng.randint(1, 3)
        b = rng.randint(-4, 4)
        c = rng.randint(-6, 6)
        k = rng.randint(-3, 4)
        val = a * k * k + b * k + c
        prompt = (f"The function f is defined by f(x) = {a}x² + {b}x + {c}. "
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
    a = rng.randint(2, 6)
    b = rng.randint(-8, 8)
    k = rng.randint(-4, 6)
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


def quadratics(rng: random.Random, difficulty: str):
    r1 = rng.randint(-8, -1)
    r2 = rng.randint(1, 8)
    b = -(r1 + r2)
    c = r1 * r2
    bsign = "+" if b >= 0 else "−"
    csign = "+" if c >= 0 else "−"
    mode = rng.choice(["sum", "product", "greater_root"])
    eq = f"x² {bsign} {abs(b)}x {csign} {abs(c)} = 0"
    base = (f"The expression factors as (x − {r1})(x − {r2}) = 0, so the "
            f"solutions are x = {r1} and x = {r2}.")
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


def exponents_radicals(rng: random.Random, difficulty: str):
    base = rng.randint(2, 7)
    m = rng.randint(2, 6)
    n = rng.randint(2, 5)
    while m + n == m * n:   # avoid m=n=2, where add/multiply distractors collide
        n = rng.randint(2, 5)
    val = base ** (m + n)
    prompt = f"Which of the following is equal to {base}^{m} · {base}^{n}?"
    correct = f"{base}^{m + n}"
    return _numeric_mc(
        rng, prompt, correct,
        [(f"{base}^{m * n}", "When multiplying powers you add exponents, not multiply them."),
         (f"{base * base}^{m + n}", "The base does not change when multiplying powers."),
         (f"{base}^{abs(m - n)}", "Subtracting exponents applies to division, not multiplication.")],
        subskill="exponent_rules",
        explanation=(f"When multiplying powers with the same base, add the exponents: "
                     f"{base}^{m}·{base}^{n} = {base}^({m}+{n}) = {base}^{m+n}."),
        tags=["exponents"], fmt=str, verify=f"{base}^{m+n}={val}")


def polynomials(rng: random.Random, difficulty: str):
    a = rng.randint(1, 5)
    b = rng.randint(1, 6)
    c = rng.randint(1, 5)
    d = rng.randint(1, 6)
    # (a x + b)(c x + d): coefficient of x is a*d + b*c
    coeff = a * d + b * c
    prompt = (f"In the expansion of ({a}x + {b})({c}x + {d}), "
              f"what is the coefficient of x?")
    explanation = (f"Using FOIL, the x-terms are {a}x·{d} and {b}·{c}x, giving "
                   f"({a}·{d} + {b}·{c})x = {coeff}x.")
    return _numeric_mc(
        rng, prompt, coeff,
        [(a * c, "This is the coefficient of x², not x."),
         (b * d, "This is the constant term, not the x coefficient."),
         (a * d, "This includes only one of the two x-terms.")],
        subskill="operations", explanation=explanation,
        tags=["polynomials", "foil"], est=80, verify=f"coeff={coeff}")


# --------------------------------------------------------------------------- #
# Problem-Solving and Data Analysis
# --------------------------------------------------------------------------- #
def ratios_percentages_units(rng: random.Random, difficulty: str):
    mode = rng.choice(["percent_of", "percent_change"])
    if mode == "percent_of":
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
    old = rng.randint(20, 60)
    pct = rng.choice([10, 20, 25, 50])
    new = old + old * pct // 100
    prompt = (f"A quantity increases from {old} to {new}. "
              f"What is the percent increase?")
    explanation = (f"Percent increase = (new − old)/old × 100 = "
                   f"({new} − {old})/{old} × 100 = {pct}%.")
    return _numeric_mc(
        rng, prompt, pct,
        [(new - old, "This is the raw increase, not the percent increase."),
         ((new - old) * 100 // new, "Divide by the original value, not the new value."),
         (pct + 5, "Recheck the division; the percent is off.")],
        subskill="percent_change", explanation=explanation,
        tags=["percent", "change"], fmt=lambda v: f"{v}%", est=80,
        verify=f"increase={pct}%")


def proportions(rng: random.Random, difficulty: str):
    rate_n = rng.randint(2, 9)
    rate_d = rng.randint(2, 6)
    mult = rng.randint(3, 8)
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
    cats = rng.sample(["Mon", "Tue", "Wed", "Thu", "Fri"], 4)
    vals = [rng.randint(10, 40) for _ in cats]
    headers = ["Day", "Tickets sold"]
    rows = [[c, str(v)] for c, v in zip(cats, vals)]
    total = sum(vals)
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
    red = rng.randint(2, 8)
    blue = rng.randint(2, 8)
    green = rng.randint(1, 6)
    total = red + blue + green
    pick = rng.choice([("red", red), ("blue", blue), ("green", green)])
    val = Fraction(pick[1], total)
    prompt = (f"A bag contains {red} red, {blue} blue, and {green} green marbles. "
              f"If one marble is drawn at random, what is the probability it is "
              f"{pick[0]}?")
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
