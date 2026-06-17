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
    if difficulty == "medium":
        # Sum-and-difference of two numbers (two-step setup).
        big = rng.randint(15, 60)
        diff = rng.randint(3, 20)
        small = big - diff
        s = big + small
        prompt = (f"The sum of two numbers is {s}, and one number is {diff} more "
                  f"than the other. What is the larger number?")
        explanation = f"Larger = (sum + difference) ÷ 2 = ({s} + {diff}) ÷ 2 = {big}."
        return _numeric_mc(
            rng, prompt, big,
            [(small, "This is the smaller number, not the larger."),
             (s // 2, "Splitting the sum evenly ignores the difference."),
             (big + 1, "Off by one; recompute (sum + difference) ÷ 2.")],
            subskill="linear_word_problem", explanation=explanation, est=90,
            tags=["algebra", "word-problem"], verify=f"{big}+{small}={s}")
    if difficulty == "hard":
        # One number is a multiple of the other; given their sum (two-step).
        mult = rng.randint(2, 5)
        small = rng.randint(6, 25)
        big = mult * small
        s = big + small
        prompt = (f"Two numbers have a sum of {s}. The larger number is {mult} times "
                  f"the smaller. What is the larger number?")
        explanation = (f"Let the smaller be n: n + {mult}n = {s}, so {mult + 1}n = {s} "
                       f"and n = {small}. The larger is {mult}·{small} = {big}.")
        return _numeric_mc(
            rng, prompt, big,
            [(small, "This is the smaller number, not the larger."),
             (s // (mult + 1), "This is the smaller number; multiply it by the ratio."),
             (s // mult, "Divide the sum by (ratio + 1), not by the ratio.")],
            subskill="linear_word_problem", explanation=explanation, est=95,
            tags=["algebra", "word-problem"], verify=f"{big}+{small}={s}")
    # Easy: flat fee + per-unit rate, solve for the number of units.
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
    thing, per = rng.choice([
        ("bacteria in a culture", "hour"), ("users of an app", "month"),
        ("cells in a sample", "hour"), ("shares of a rumor", "day")])
    # Hard: choose the EXPRESSION that models the situation (conceptual).
    if difficulty == "hard":
        n0 = rng.choice([5, 10, 20, 50, 100, 200])
        grow = rng.random() < 0.5
        r = rng.choice([2, 3]) if grow else rng.choice([2, 4])
        if grow:
            verb = {2: "doubles", 3: "triples"}[r] + f" every {per}"
            correct = f"{n0}·{r}^t"
            third = f"{n0}^t·{r}"
        else:
            verb = f"is divided by {r} every {per}"
            correct = f"{n0}·(1/{r})^t"
            third = f"{n0}/({r}·t)"
        prompt = (f"A population of {n0} {thing} {verb}. Which expression gives the "
                  f"population after t {per}s?")
        ds = [(f"{n0}·{r}·t", "This models linear change (a fixed amount each period), "
               "not repeated multiplication."),
              (f"{n0}+{r}·t", "This adds a constant each period instead of multiplying."),
              (third, "The repeating growth factor is the base raised to t, applied to "
               "the starting amount.")]
        return _numeric_mc(
            rng, prompt, correct, ds, subskill="exponential",
            explanation=(f"Each {per} multiplies the amount by the factor, so after t "
                         f"{per}s the population is {correct}."),
            tags=["advanced-math", "exponential", "model"], fmt=str, est=90,
            verify=f"model {correct}")
    # Medium: exponential DECAY — value after h periods (clean integer division).
    if difficulty == "medium":
        r = rng.choice([2, 3])
        h = rng.randint(2, 4)
        final = rng.randint(2, 20)
        n0 = final * r ** h
        word = {2: "halves", 3: "is cut to one-third"}[r]
        val = final
        prompt = (f"A population of {n0} {thing} {word} every {per}. "
                  f"How many will there be after {h} {per}s?")
        explanation = (f"Divide by {r} each {per}: {n0} ÷ {r}^{h} = {val}.")
        return _numeric_mc(
            rng, prompt, val,
            [(n0 // (r * h), "This divides once by r×time instead of repeatedly."),
             (n0 - r * h, "This subtracts instead of repeatedly dividing."),
             (val * r, "This stops one period too early.")],
            subskill="exponential", explanation=explanation, est=85,
            tags=["advanced-math", "exponential", "decay"], verify=f"{n0}/{r}^{h}={val}")
    # Easy: exponential growth — value after h periods.
    n0 = rng.choice([2, 3, 4, 5, 6, 8, 10, 12, 15, 20, 25])
    r = rng.choice([2, 3])
    word = {2: "doubles", 3: "triples"}[r]
    h = rng.randint(2, 5)
    val = n0 * r ** h
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
    # Include row/column totals so marginal and conditional reads are well-defined.
    rows = [[rcat[0], str(a), str(b), str(a + b)],
            [rcat[1], str(c), str(d), str(c + d)],
            ["Total", str(a + c), str(b + d), str(total)]]
    headers = ["", ccat[0], ccat[1], "Total"]
    table = {"type": "table", "table": {
        "caption": "Survey responses", "headers": headers, "rows": rows}}

    if difficulty == "hard":
        # Conditional probability: given a column, probability of a row.
        col_total = a + c
        val = Fraction(a, col_total)
        prompt = (f"The table shows survey responses. Given that a response is "
                  f"“{ccat[0]}”, what is the probability that it is also “{rcat[0]}”?")
        explanation = (f"Restrict to the “{ccat[0]}” column (total {a} + {c} = "
                       f"{col_total}); of those, {a} are “{rcat[0]}”, so the "
                       f"probability is {a}/{col_total} = {num_str(val)}.")
        ds = [(Fraction(a, total), "Condition on the column total, not the grand total."),
              (Fraction(a, a + b), "Condition on the column, not the row."),
              (Fraction(c, col_total), "This is the probability of the other row in the column.")]
    elif difficulty == "medium":
        # Joint probability of a single cell out of the grand total.
        val = Fraction(a, total)
        prompt = (f"The table shows survey responses. If one response is chosen at "
                  f"random, what is the probability that it is both “{rcat[0]}” and "
                  f"“{ccat[0]}”?")
        explanation = (f"That single cell holds {a} of the {total} responses, so the "
                       f"probability is {a}/{total} = {num_str(val)}.")
        ds = [(Fraction(a, a + b), "This conditions on the row instead of using the grand total."),
              (Fraction(a, a + c), "This conditions on the column instead of the grand total."),
              (Fraction(a + b, total), "This is the whole row, not the single cell.")]
    else:
        # Marginal probability of a row.
        row_total = a + b
        val = Fraction(row_total, total)
        prompt = (f"The table shows survey responses. If one response is chosen at "
                  f"random, what is the probability that it is in the “{rcat[0]}” row?")
        explanation = (f"The “{rcat[0]}” row totals {a} + {b} = {row_total} out of "
                       f"{total} responses, so the probability is "
                       f"{row_total}/{total} = {num_str(val)}.")
        ds = [(Fraction(a, total), f"This uses only one cell ({a}), not the whole row."),
              (Fraction(c + d, total), "This is the probability of the other row."),
              (Fraction(row_total, c + d), "Divide by the grand total, not the other row.")]
    return _numeric_mc(
        rng, prompt, val, ds, subskill="two_way_tables", explanation=explanation,
        qtype="data_interpretation", est=90, tags=["data", "probability", "table"],
        verify=f"P={num_str(val)}", stimulus=table)


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
    if difficulty == "medium":
        # Coefficient on x: |k·x − b| = c. Built from a center m and gap g so the
        # solutions m ± g are clean integers: b = k·m, c = k·g.
        k = rng.randint(2, 5)
        m = rng.randint(2, 12)
        g = rng.randint(1, 8)
        b, c = k * m, k * g
        greatest, least = m + g, m - g
        ask_greatest = rng.random() < 0.5
        val, which = (greatest, "greatest") if ask_greatest else (least, "least")
        prompt = f"If |{k}x − {b}| = {c}, what is the {which} possible value of x?"
        expl = (f"|{k}x − {b}| = {c} gives {k}x − {b} = {c} or {k}x − {b} = −{c}. "
                f"Solving, x = {greatest} or x = {least}; the {which} is {val}.")
        ds = [(least if ask_greatest else greatest,
               f"This is the {'least' if ask_greatest else 'greatest'} solution."),
              (val + 1, "Off by one; re-solve both linear cases."),
              (m, "This is the center (b ÷ k); add or subtract c ÷ k to get x.")]
        return _numeric_mc(rng, prompt, val, ds, subskill="absolute_value",
                           explanation=expl, est=90, tags=["algebra", "absolute-value"],
                           verify=f"|{k}x-{b}|={c}")
    if difficulty == "hard":
        # Inequality: count integer solutions of |x − a| ≤ c  ->  2c + 1.
        a = rng.randint(-5, 15)
        c = rng.randint(2, 9)
        val = 2 * c + 1
        lo, hi = a - c, a + c
        prompt = (f"How many integer values of x satisfy |x − {a}| ≤ {c}?")
        expl = (f"|x − {a}| ≤ {c} means {lo} ≤ x ≤ {hi}. That range contains "
                f"{hi} − {lo} + 1 = {val} integers.")
        ds = [(2 * c, "Count both endpoints: the range is inclusive, so add 1."),
              (c, "This counts only one side of the center, not the full range."),
              (2 * c + 2, "Recount: an inclusive range a−c to a+c has 2c + 1 integers.")]
        return _numeric_mc(rng, prompt, val, ds, subskill="absolute_value",
                           explanation=expl, est=95, tags=["algebra", "absolute-value"],
                           verify=f"|x-{a}|<={c}")
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
