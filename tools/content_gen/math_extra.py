"""Additional SAT Math generators covering question types missing from math_gen.py:
linear word problems, exponential growth, two-way-table probability, line of best
fit (scatterplots), and absolute-value equations. Answers are computed, so they are
machine-checkable; numeric ranges are wide for a large unique space.
"""
from __future__ import annotations

import random
from fractions import Fraction

from .math_gen import _numeric_mc
from .util import num_str, spr


def word_problems(rng: random.Random, difficulty: str):
    worker, unit = rng.choice([
        ("plumber", "hour"), ("tutor", "hour"), ("rental company", "day"),
        ("painter", "hour"), ("caterer", "guest"), ("printer", "page")])
    a = rng.randint(3, 30)        # per-unit rate
    h = rng.randint(2, 25)        # number of units (the answer)
    b = rng.randint(5, 80)        # flat fee
    total = b + a * h
    prompt = (f"A {worker} charges a ${b} flat fee plus ${a} per {unit}. "
              f"If a job costs ${total} in total, how many {unit}s were billed?")
    explanation = (f"Subtract the flat fee: {total} − {b} = {total - b}. "
                   f"Divide by the rate: {total - b} ÷ {a} = {h}.")
    if rng.random() < 0.35:
        return spr(prompt, h, subskill="linear_word_problem", explanation=explanation,
                   tags=["algebra", "word-problem", "grid-in"], est=80,
                   verify=f"{b}+{a}*{h}={total}")
    return _numeric_mc(
        rng, prompt, h,
        [(total // a, "This ignores the flat fee; subtract it before dividing."),
         (total - b, "This is the cost after the fee, not the number of units."),
         (h + 1, "Off by one; recheck the division.")],
        subskill="linear_word_problem", explanation=explanation, est=80,
        tags=["algebra", "word-problem"], verify=f"{b}+{a}*{h}={total}")


def exponential_growth(rng: random.Random, difficulty: str):
    n0 = rng.choice([2, 3, 4, 5, 6, 8, 10, 12, 15, 20, 25, 50])
    r = rng.choice([2, 3]) if difficulty != "hard" else rng.choice([2, 3, 4])
    word = {2: "doubles", 3: "triples", 4: "quadruples"}[r]
    h = rng.randint(2, 5)
    val = n0 * r ** h
    thing, per = rng.choice([
        ("bacteria in a culture", "hour"), ("users of an app", "month"),
        ("cells in a sample", "hour"), ("shares of a rumor", "day")])
    prompt = (f"A population of {n0} {thing} {word} every {per}. "
              f"How many will there be after {h} {per}s?")
    explanation = (f"Multiply by {r} each {per}: {n0} × {r}^{h} = {val}.")
    return _numeric_mc(
        rng, prompt, val,
        [(n0 * r * h, "This grows linearly (×r×time) instead of exponentially."),
         (n0 * r ** (h - 1), "This is the count one period too early."),
         (n0 + r * h, "This adds instead of repeatedly multiplying.")],
        subskill="exponential", explanation=explanation, est=85,
        tags=["advanced-math", "exponential"], verify=f"{n0}*{r}^{h}={val}")


def two_way_tables(rng: random.Random, difficulty: str):
    rcat = rng.choice([("Cats", "Dogs"), ("Fiction", "Nonfiction"),
                       ("Bus", "Bike"), ("Coffee", "Tea")])
    ccat = rng.choice([("Weekday", "Weekend"), ("Morning", "Evening"),
                       ("Adults", "Students")])
    a = rng.randint(5, 40)
    b = rng.randint(5, 40)
    c = rng.randint(5, 40)
    d = rng.randint(5, 40)
    total = a + b + c + d
    rows = [[rcat[0], str(a), str(b)], [rcat[1], str(c), str(d)]]
    headers = ["", ccat[0], ccat[1]]
    row_total = a + b
    val = Fraction(row_total, total)
    prompt = (f"The table shows survey responses. If one response is chosen at "
              f"random, what is the probability that it is in the “{rcat[0]}” row?")
    explanation = (f"The “{rcat[0]}” row totals {a} + {b} = {row_total} out of "
                   f"{total} responses, so the probability is "
                   f"{row_total}/{total} = {num_str(val)}.")
    return _numeric_mc(
        rng, prompt, val,
        [(Fraction(a, total), f"This uses only one cell ({a}), not the whole row."),
         (Fraction(row_total, c + d) if (c + d) else Fraction(row_total, total),
          "Divide by the grand total, not by the other row."),
         (Fraction(c + d, total), "This is the probability of the other row.")],
        subskill="two_way_tables", explanation=explanation,
        qtype="data_interpretation", est=85, tags=["data", "probability", "table"],
        verify=f"P={num_str(val)}",
        stimulus={"type": "table", "table": {
            "caption": "Survey responses", "headers": headers, "rows": rows}})


def line_of_best_fit(rng: random.Random, difficulty: str):
    m = rng.randint(2, 12)
    b = rng.randint(-12, 25)
    mode = rng.choice(["predict", "slope"])
    if mode == "slope":
        if abs(b) == m:        # keep the intercept distractor distinct from the slope
            b = m + 5
        bsign = "+" if b >= 0 else "−"
        prompt = (f"A line of best fit for a scatterplot is modeled by "
                  f"y = {m}x {bsign} {abs(b)}. Which statement best interprets the "
                  f"slope of this model?")
        correct = f"For each increase of 1 in x, y increases by about {m}."
        return _numeric_mc(
            rng, prompt, correct,
            [(f"For each increase of 1 in x, y increases by about {abs(b)}.",
              "That is the y-intercept's value, not the slope."),
             (f"When x is 0, y is about {m}.",
              "That describes the intercept, not the slope; the slope is the rate."),
             (f"For each increase of 1 in y, x increases by about {m}.",
              "This reverses the roles of x and y.")],
            subskill="line_of_best_fit", explanation=(
                f"In y = {m}x {bsign} {abs(b)}, the slope {m} is the predicted change "
                "in y per unit increase in x."),
            qtype="data_interpretation", fmt=str, est=80,
            tags=["data", "scatterplot"], verify=f"slope={m}")
    k = rng.randint(2, 18)
    y = m * k + b
    bsign = "+" if b >= 0 else "−"
    prompt = (f"The line of best fit for a set of data is y = {m}x {bsign} {abs(b)}. "
              f"Based on this model, what value of y is predicted when x = {k}?")
    explanation = f"Substitute x = {k}: y = {m}·{k} {bsign} {abs(b)} = {y}."
    return _numeric_mc(
        rng, prompt, y,
        [(m * k, "You left off the y-intercept term."),
         (m + k + b, "Add the product m·x, not m + x."),
         (m * k - b if b >= 0 else m * k + b,
          "Check the sign of the intercept term.")],
        subskill="line_of_best_fit", explanation=explanation,
        qtype="data_interpretation", est=80, tags=["data", "scatterplot"],
        verify=f"y={y}")


def absolute_value(rng: random.Random, difficulty: str):
    a = rng.randint(1, 20)
    c = rng.randint(1, 20)
    mode = rng.choice(["greatest", "sum", "least"])
    greatest = a + c
    least = a - c
    if mode == "greatest":
        val = greatest
        prompt = f"If |x − {a}| = {c}, what is the greatest possible value of x?"
        expl = (f"|x − {a}| = {c} gives x − {a} = {c} or x − {a} = −{c}, so x = "
                f"{greatest} or x = {least}. The greatest is {greatest}.")
        ds = [(least, "This is the lesser solution."),
              (c - a, "Recheck the signs when solving the two cases."),
              (a * c, "Do not multiply; solve the two linear cases.")]
    elif mode == "least":
        val = least
        prompt = f"If |x − {a}| = {c}, what is the least possible value of x?"
        expl = (f"The two solutions are x = {greatest} and x = {least}; "
                f"the least is {least}.")
        ds = [(greatest, "This is the greater solution."),
              (a + c + 1, "Off by one; recompute the two cases."),
              (-least, "Check the sign of the solution.")]
    else:
        val = 2 * a
        prompt = f"If |x − {a}| = {c}, what is the sum of all possible values of x?"
        expl = (f"The solutions x = {greatest} and x = {least} sum to "
                f"{greatest} + {least} = {2 * a}.")
        ds = [(greatest, "This is only one solution, not the sum."),
              (2 * c, "The solutions are symmetric about {0}, not about c.".format(a)),
              (greatest - least, "This is the difference, not the sum.")]
    return _numeric_mc(rng, prompt, val, ds, subskill="absolute_value",
                       explanation=expl, est=80, tags=["algebra", "absolute-value"],
                       verify=f"|x-{a}|={c}")
