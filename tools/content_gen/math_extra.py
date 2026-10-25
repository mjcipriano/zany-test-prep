"""Additional SAT/ACT Math families: linear word problems, absolute value,
exponential growth/decay, two-way tables and scatterplots (line of best fit).

Same contract as math_gen.py: ``FAMILIES[skill][difficulty] -> [fn, ...]`` with
``fn(rng, difficulty) -> body``. Answers are computed, never authored.
"""
from __future__ import annotations

import math
import random
from fractions import Fraction

from .math_gen import (_numeric_mc, _text_mc, _spr_num, _lin, _m, _pm, _table,
                       _dispatch, _ordinal, _money, NAMES)
from .util import num_str


# --------------------------------------------------------------------------- #
# word_problems
# --------------------------------------------------------------------------- #
def wp_fee_rate(rng, d):
    """Flat fee + per-unit rate -> count (easy), rate (medium), compare two plans (hard)."""
    worker, unit = rng.choice([("plumber", "hour"), ("tutor", "hour"), ("rental company", "day"),
                               ("painter", "hour"), ("caterer", "guest"), ("print shop", "page"),
                               ("electrician", "hour"), ("dog walker", "walk")])
    a, h, b = rng.randint(3, 30), rng.randint(2, 25), rng.randint(5, 80)
    total = b + a * h
    if d == "easy":
        prompt = (f"A {worker} charges a ${b} flat fee plus ${a} per {unit}. If a job costs "
                  f"${total} in total, how many {unit}s were billed?")
        val = h
        expl = f"Subtract the fee: {total} − {b} = {total - b}. Divide by the rate: {total - b} ÷ {a} = {h}."
        ds = [(total // a, "This ignores the flat fee; subtract it before dividing."),
              (total - b, "This is the cost after the fee, not the number of {0}s.".format(unit)),
              (h + 1, "Off by one; recheck the division."),
              ((total + b) // a, "Subtract the fee; don't add it.")]
    elif d == "medium":
        prompt = (f"A {worker} charges a flat fee of ${b} plus a fixed rate per {unit}. A job of "
                  f"{h} {unit}s cost ${total}. What is the rate per {unit}, in dollars?")
        val = a
        expl = f"({total} − {b}) ÷ {h} = {total - b} ÷ {h} = {a}."
        ds = [(Fraction(total, h), "Subtract the flat fee before dividing."),
              (total - b, "That is the total for the {0}s, not the rate per {0}.".format(unit)),
              (Fraction(total - b, h + 1), "Divide by the number of {0}s, {1}.".format(unit, h)),
              (a + 2, "Arithmetic slip.")]
    else:
        a2 = rng.choice([v for v in range(3, 30) if v != a])
        # plan 1: b + a h ; plan 2: b2 + a2 h ; equal at h = n
        n = rng.randint(3, 20)
        b2 = b + (a - a2) * n
        if b2 <= 0:
            return wp_fee_rate(rng, d)
        prompt = (f"Two {worker}s quote prices for the same job. The first charges ${b} plus ${a} "
                  f"per {unit}; the second charges ${b2} plus ${a2} per {unit}. For how many {unit}s "
                  f"would the two quotes be equal?")
        val = n
        expl = f"Set {b} + {a}h = {b2} + {a2}h: {_m(a - a2)}h = {_m(b2 - b)}, so h = {n}."
        ds = [(abs(b2 - b), "Divide the difference in fees by the difference in rates."),
              (abs(a - a2), "That is the difference in rates, not the number of {0}s.".format(unit)),
              (n + 1, "Arithmetic slip; substitute back to check."),
              (Fraction(b + b2, a + a2), "Subtract, don't add, when setting the quotes equal.")]
        return _numeric_mc(rng, prompt, val, ds, subskill="model_and_solve", explanation=expl,
                           qtype="multi_step_math", tags=["algebra", "word-problem"], est=100,
                           verify=f"{b}+{a}*{n}={b2}+{a2}*{n}")
    return _numeric_mc(rng, prompt, val, ds, subskill="model_and_solve", explanation=expl,
                       tags=["algebra", "word-problem"], est=80, verify=f"{b}+{a}*{h}={total}")


def wp_two_numbers(rng, d):
    """Sum/difference (easy), one more than other (medium), multiple/ratio (hard)."""
    if d == "easy":
        small = rng.randint(3, 40)
        diff = rng.randint(2, 20)
        big = small + diff
        prompt = f"The sum of two numbers is {big + small}, and their difference is {diff}. What is the smaller number?"
        val = small
        expl = f"Larger = ({big + small} + {diff})/2 = {big}; smaller = {big} − {diff} = {small}."
        ds = [(big, "That is the larger number."),
              ((big + small) // 2, "Splitting the sum evenly ignores the difference."),
              (small + diff // 2, "Recheck: the two numbers differ by {0}.".format(diff)),
              (big + small - diff, "That is twice the smaller number.")]
    elif d == "medium":
        big = rng.randint(15, 60)
        diff = rng.randint(3, 20)
        small = big - diff
        s = big + small
        prompt = rng.choice([f"The sum of two numbers is {s}, and one number is {diff} more than the other. What is the larger number?",
                             f"Two numbers add up to {s}. One of them exceeds the other by {diff}. What is the larger number?"])
        val = big
        expl = f"Let the smaller be n: n + (n + {diff}) = {s} → 2n = {s - diff} → n = {small}; larger = {big}."
        ds = [(small, "This is the smaller number, not the larger."),
              (s // 2, "Splitting the sum evenly ignores the difference."),
              (big + 1, "Off by one; recompute (sum + difference) ÷ 2."),
              (s - diff, "That is 2n, twice the smaller number.")]
    else:
        mult = rng.randint(2, 5)
        small = rng.randint(6, 25)
        k = rng.randint(1, 9)
        big = mult * small + k
        s = big + small
        prompt = (f"Two numbers have a sum of {s}. The larger number is {k} more than {mult} times "
                  f"the smaller. What is the larger number?")
        val = big
        expl = f"n + ({mult}n + {k}) = {s} → {mult + 1}n = {s - k} → n = {small}; larger = {mult}·{small} + {k} = {big}."
        ds = [(small, "This is the smaller number, not the larger."),
              (mult * small, "Add the extra {0}.".format(k)),
              (Fraction(s, mult + 1), "Subtract {0} before dividing by {1}.".format(k, mult + 1)),
              (s - small - k, "Arithmetic slip; recheck {0}n + {1}.".format(mult, k))]
    return _numeric_mc(rng, prompt, val, ds, subskill="model_and_solve", explanation=expl,
                       tags=["algebra", "word-problem"], est=90, verify=f"{val}")


def wp_consecutive(rng, d):
    """Consecutive integers."""
    if d == "easy":
        n = rng.randint(3, 150)
        s = 3 * n + 3
        prompt = rng.choice([f"The sum of three consecutive integers is {s}. What is the largest of the three integers?",
                             f"Three consecutive integers have a sum of {s}. What is the greatest of them?"])
        val = n + 2
        expl = f"n + (n + 1) + (n + 2) = {s} → 3n = {s - 3} → n = {n}; the largest is {n + 2}."
        ds = [(n, "That is the smallest of the three."), (n + 1, "That is the middle integer."),
              (s // 3 + 2 + 1, "Arithmetic slip."), (s // 3, "That is the middle value, not the largest.")]
    elif d == "medium":
        n = rng.randint(2, 150) * 2
        s = 3 * n + 6
        prompt = f"The sum of three consecutive even integers is {s}. What is the smallest of the integers?"
        val = n
        expl = f"n + (n + 2) + (n + 4) = {s} → 3n = {s - 6} → n = {n}."
        ds = [(n + 2, "That is the middle integer."), (n + 4, "That is the largest."),
              (Fraction(s - 3, 3), "Consecutive even integers differ by 2, not 1."), (s // 3, "That is the middle value.")]
    else:
        n = rng.randint(3, 120) * 2 + 1
        s2 = n * n + (n + 2) ** 2
        prompt = f"The sum of the squares of two consecutive odd integers is {s2}. What is the larger integer, if both are positive?"
        val = n + 2
        expl = f"n² + (n + 2)² = {s2} → 2n² + 4n + 4 = {s2} → n² + 2n − {(s2 - 4) // 2} = 0 → n = {n}; the larger is {n + 2}."
        ds = [(n, "That is the smaller integer."), (n + 4, "Consecutive odd integers differ by 2."),
              (math.isqrt(s2 // 2), "Set up the equation; don't just halve and take a root."), (n + 1, "The integers must be odd.")]
    return _numeric_mc(rng, prompt, val, ds, subskill="model_and_solve", explanation=expl,
                       tags=["algebra", "word-problem", "consecutive"], est=85 if d != "hard" else 110,
                       verify=f"n={n}")


def wp_expression(rng, d):
    """Choose the expression/equation that models the situation (text options)."""
    name = rng.choice(NAMES)
    if d == "easy":
        p, q = rng.randint(2, 20), rng.randint(2, 20)
        ctx = rng.choice([("apples", "oranges"), ("pens", "notebooks"), ("adult tickets", "child tickets")])
        prompt = (f"{name} buys x {ctx[0]} at ${p} each and y {ctx[1]} at ${q} each. Which expression "
                  f"gives the total cost, in dollars?")
        correct = f"{p}x + {q}y"
        ds = [(f"{q}x + {p}y", "The prices are attached to the wrong items."),
              (f"{p + q}(x + y)", "Each item has its own price; they aren't both charged for every item."),
              (f"{p}x · {q}y", "Costs add; they aren't multiplied."),
              (f"({p} + {q})xy", "Multiply each count by its own price, then add.")]
        expl = f"Each {ctx[0][:-1]} costs {p} and each {ctx[1][:-1]} costs {q}: {correct}."
    elif d == "medium":
        r, b = rng.randint(2, 15), rng.randint(20, 300)
        ctx = rng.choice([("saves ${r} each week starting with ${b}", "savings after w weeks", "w", f"{b} + {r}w"),
                          ("has ${b} on a gift card and spends ${r} each visit", "balance after v visits", "v", f"{b} − {r}v"),
                          ("reads {r} pages per day of a {b}-page book", "pages remaining after t days", "t", f"{b} − {r}t")])
        prompt = f"{name} {ctx[0].format(r=r, b=b)}. Which expression represents {name}'s {ctx[1]}?"
        correct = ctx[3]
        v = ctx[2]
        if "−" in correct:
            ds = [(f"{b} + {r}{v}", "The amount decreases, so the rate is subtracted."),
                  (f"{r}{v} − {b}", "Start from {0}; the signs are reversed.".format(b)),
                  (f"({b} − {r}){v}", "Only the rate is multiplied by {0}.".format(v)),
                  (f"{b}{v} − {r}", "The rate, not the starting amount, multiplies {0}.".format(v))]
        else:
            ds = [(f"{b} − {r}{v}", "Savings grow, so the rate is added."),
                  (f"({b} + {r}){v}", "The starting amount isn't multiplied by the number of weeks."),
                  (f"{r} + {b}{v}", "The weekly amount, not the starting amount, multiplies w."),
                  (f"{b}{v} + {r}", "Swap the roles: the rate multiplies w.")]
        expl = f"Start at {b} and {'add' if '+' in correct else 'subtract'} {r} per {v}: {correct}."
    else:
        v, t, w = rng.randint(2, 12), rng.randint(3, 15), rng.randint(2, 9)
        ctx = rng.choice([
            (f"A tank contains {v * t} liters of water and is drained at a constant rate so that it is empty after {t} minutes. Which equation gives the volume V, in liters, after m minutes (0 ≤ m ≤ {t})?",
             f"V = {v * t} − {v}m", [(f"V = {v * t} − {t}m", "The rate is {0}/{1} = {2} liters per minute.".format(v * t, t, v)),
                                     (f"V = {v * t} + {v}m", "The volume decreases."),
                                     (f"V = {v}m", "That is the amount drained, not the amount remaining."),
                                     (f"V = {v * t} − m/{v}", "The rate multiplies m.")]),
            (f"A car rental costs ${w * 10} per day plus ${w} per mile driven. Which equation gives the cost C, in dollars, of renting the car for d days and driving x miles?",
             f"C = {w * 10}d + {w}x", [(f"C = {w}d + {w * 10}x", "The daily rate and the per-mile rate are swapped."),
                                       (f"C = {w * 10 + w}(d + x)", "Days and miles have different rates."),
                                       (f"C = {w * 10}d · {w}x", "Costs add."),
                                       (f"C = {w * 10} + {w}dx", "Each day costs {0}; days are multiplied by the daily rate.".format(w * 10))]),
        ])
        prompt, correct, ds = ctx
        expl = f"Translate each quantity into its term: {correct}."
    return _text_mc(rng, prompt, correct, ds, subskill="model_and_solve", explanation=expl,
                    tags=["algebra", "word-problem", "model"], est=85, verify=f"model {correct}")


def wp_rate_time(rng, d):
    """Distance/rate/time and work-rate word problems."""
    name, other = rng.sample(NAMES, 2)
    if d == "easy":
        r, t = rng.randint(30, 75), rng.randint(2, 9)
        which = rng.choice(["distance", "time", "rate"])
        if which == "distance":
            prompt = f"A train travels at a constant speed of {r} miles per hour. How many miles does it travel in {t} hours?"
            val = r * t
            expl = f"Distance = rate × time = {r} × {t} = {val}."
            ds = [(r + t, "Multiply rate by time; don't add."), (Fraction(r, t), "Distance = rate × time, not rate ÷ time."), (val + r, "Off by one hour."), (r * (t - 1), "Count all {0} hours.".format(t))]
        elif which == "time":
            prompt = f"A bus travels {r * t} miles at a constant speed of {r} miles per hour. How many hours does the trip take?"
            val = t
            expl = f"Time = distance ÷ rate = {r * t} ÷ {r} = {t}."
            ds = [(r * t * r, "Divide distance by rate; don't multiply."), (t + 1, "Arithmetic slip."), (r * t - r, "Divide; don't subtract."), (Fraction(r, r * t) if False else t * 2, "Recheck the division.")]
        else:
            prompt = f"A cyclist covers {r * t} kilometers in {t} hours at a constant speed. What is the speed, in kilometers per hour?"
            val = r
            expl = f"Rate = distance ÷ time = {r * t} ÷ {t} = {r}."
            ds = [(r * t * t, "Divide distance by time; don't multiply."), (r + 5, "Arithmetic slip."), (r * t - t, "Divide; don't subtract."), (Fraction(t, r * t) * 100 if False else r * 2, "Recheck the division.")]
    elif d == "medium":
        r1, r2 = rng.randint(40, 70), rng.randint(40, 70)
        if r1 == r2:
            r2 += 5
        t = rng.randint(2, 6)
        gap = (r1 + r2) * t
        prompt = (f"Two cars leave the same point at the same time and travel in opposite directions, one at "
                  f"{r1} miles per hour and the other at {r2} miles per hour. After how many hours will they be "
                  f"{gap} miles apart?")
        val = t
        expl = f"They separate at {r1} + {r2} = {r1 + r2} mph; {gap} ÷ {r1 + r2} = {t} hours."
        ds = [(Fraction(gap, abs(r1 - r2)), "Opposite directions: add the speeds, don't subtract."), (Fraction(gap, max(r1, r2)), "Both cars contribute to the separation."), (t + 1, "Arithmetic slip."), (Fraction(gap, r1 + r2) * 2, "Divide the gap by the combined speed once.")]
    else:
        a = rng.randint(2, 12)
        b = rng.randint(a, 24)
        val = Fraction(a * b, a + b)
        prompt = rng.choice([
            f"One pump can fill a pool in {a} hours, and a second pump can fill the same pool in {b} hours. Working together at these rates, how many hours would the two pumps take to fill the pool?",
            f"{name} can paint a fence in {a} hours, and {other} can paint the same fence in {b} hours. Working together at these rates, how many hours would it take them to paint the fence?",
            f"A large printer finishes a job in {a} minutes and a smaller printer finishes the same job in {b} minutes. If both printers work on the job together, how many minutes does it take?"])
        expl = f"Rates: 1/{a} + 1/{b} = {a + b}/{a * b} pool per hour; time = {a * b}/{a + b} = {num_str(val)} hours."
        ds = [(Fraction(a + b, 2), "Averaging the times is wrong; add the rates."), (a + b, "Together they are faster than either alone."), (Fraction(a + b, a * b), "That is the combined rate (jobs per hour); the time is its reciprocal."), (Fraction(a * b, 2), "Divide ab by a + b, not by 2."), (Fraction(a * b, a + b) + 1, "Arithmetic slip; recompute ab/(a + b).")]
        return _numeric_mc(rng, prompt, val, ds, subskill="model_and_solve", explanation=expl,
                           qtype="multi_step_math", tags=["algebra", "word-problem", "work-rate"], est=105,
                           verify=f"{a}*{b}/({a}+{b})={num_str(val)}")
    return _numeric_mc(rng, prompt, val, ds, subskill="model_and_solve", explanation=expl,
                       tags=["algebra", "word-problem", "rate"], est=80, verify=f"val={val}")


def wp_age_money(rng, d):
    """Age and coin/bill problems (medium/hard); easy: simple total with change."""
    name, other = rng.sample(NAMES, 2)
    if d == "easy":
        p, n, paid = rng.randint(2, 9), rng.randint(2, 9), rng.choice([20, 50, 100])
        total = p * n
        if total >= paid:
            paid = 100
        prompt = f"{name} buys {n} sandwiches at ${p} each and pays with a ${paid} bill. How much change, in dollars, does {name} receive?"
        val = paid - total
        expl = f"{n} × {p} = {total}; {paid} − {total} = {val}."
        ds = [(total, "That is the cost, not the change."), (paid - p, "Multiply the price by the number bought first."), (val + p, "Arithmetic slip."), (paid - n, "Subtract the total cost, not the count.")]
    elif d == "medium":
        a = rng.randint(6, 40)
        k = rng.randint(2, 4)
        diff = a * k - a
        prompt = f"{other} is {k} times as old as {name}. The difference between their ages is {diff} years. How old is {name}?"
        val = a
        expl = f"If {name} is x, {other} is {k}x; {k}x − x = {diff} → {k - 1}x = {diff} → x = {a}."
        ds = [(a * k, f"That is {other}'s age."), (Fraction(diff, k), "The difference is (k − 1)x, so divide by {0}.".format(k - 1)), (a + k, "Arithmetic slip."), (diff, "That is the difference, not an age.")]
    else:
        q, dm = rng.randint(3, 20), rng.randint(3, 20)
        n = q + dm
        cents = 25 * q + 10 * dm
        prompt = (f"A jar contains {n} coins, all quarters and dimes, worth ${cents / 100:.2f} in total. "
                  f"How many quarters are in the jar?")
        val = q
        expl = f"q + d = {n} and 25q + 10d = {cents}. Substituting d = {n} − q: 15q = {cents - 10 * n} → q = {q}."
        ds = [(dm, "That is the number of dimes."), (n - q + 1, "Recheck which coin you solved for."), (cents // 25, "Not all coins are quarters."), (q + 1, "Arithmetic slip; check the total value.")]
        return _numeric_mc(rng, prompt, val, ds, subskill="model_and_solve", explanation=expl,
                           qtype="multi_step_math", tags=["algebra", "word-problem", "coins"], est=100,
                           verify=f"q={q},d={dm}")
    return _numeric_mc(rng, prompt, val, ds, subskill="model_and_solve", explanation=expl,
                       tags=["algebra", "word-problem"], est=80, verify=f"val={val}")


def wp_gridin(rng, d):
    """Grid-in word problem."""
    if d == "easy":
        a, h, b = rng.randint(3, 30), rng.randint(2, 25), rng.randint(5, 80)
        prompt = f"A plumber charges a ${b} flat fee plus ${a} per hour. If a job costs ${b + a * h}, how many hours were billed?"
        val = h
        expl = f"({b + a * h} − {b}) ÷ {a} = {h}."
    elif d == "medium":
        big = rng.randint(15, 60)
        diff = rng.randint(3, 20)
        small = big - diff
        prompt = f"The sum of two numbers is {big + small}, and one number is {diff} more than the other. What is the smaller number?"
        val = small
        expl = f"2n + {diff} = {big + small} → n = {small}."
    else:
        mult, small = rng.randint(2, 7), rng.randint(6, 60)
        big = mult * small
        prompt = f"Two numbers have a sum of {big + small}. The larger is {mult} times the smaller. What is the larger number?"
        val = big
        expl = f"{mult + 1}n = {big + small} → n = {small}; larger = {big}."
    return _spr_num(prompt, val, subskill="model_and_solve", explanation=expl,
                    tags=["algebra", "word-problem", "grid-in"], est=85, verify=f"val={val}")


wp_gridin.sat_only = True


# --------------------------------------------------------------------------- #
# absolute_value
# --------------------------------------------------------------------------- #
def ab_solve(rng, d):
    """Solve |x − a| = c (easy), |kx − b| = c (medium), |ax + b| + k = m (hard)."""
    if d == "easy":
        a, c = rng.randint(1, 25), rng.randint(1, 25)
        mode = rng.choice(["greatest", "least", "sum"])
        g, l = a + c, a - c
        if mode == "greatest":
            val = g
            prompt = rng.choice([f"If |x − {a}| = {c}, what is the greatest possible value of x?",
                                 f"What is the larger solution to the equation |x − {a}| = {c}?"])
            expl = f"x − {a} = {c} or x − {a} = −{c}, so x = {g} or x = {_m(l)}. The greatest is {g}."
            ds = [(l, "This is the lesser solution."), (c - a, "Recheck the signs in the two cases."), (a * c, "Do not multiply; solve the two linear cases."), (g + 1, "Arithmetic slip.")]
        elif mode == "least":
            val = l
            prompt = f"If |x − {a}| = {c}, what is the least possible value of x?"
            expl = f"The two solutions are x = {g} and x = {_m(l)}; the least is {_m(l)}."
            ds = [(g, "This is the greater solution."), (-g, "Check the sign of the solution."), (c - a if c - a != l else -l + 1, "Recheck the second case: x − a = −c."), (l - 1, "Arithmetic slip.")]
        else:
            val = 2 * a
            prompt = f"If |x − {a}| = {c}, what is the sum of all possible values of x?"
            expl = f"The solutions x = {g} and x = {_m(l)} sum to {2 * a}."
            ds = [(g, "This is only one solution, not the sum."), (2 * c, "The solutions are symmetric about {0}, not about {1}.".format(a, c)), (g - l, "This is the difference, not the sum."), (a, "That is the center; the sum is twice it.")]
        verify = f"|x-{a}|={c}"
    elif d == "medium":
        k, m, g = rng.randint(2, 6), rng.randint(2, 12), rng.randint(1, 8)
        b, c = k * m, k * g
        greatest, least = m + g, m - g
        ask = rng.random() < 0.5
        val, which = (greatest, "greatest") if ask else (least, "least")
        prompt = f"If |{k}x − {b}| = {c}, what is the {which} possible value of x?"
        expl = (f"{k}x − {b} = {c} or {k}x − {b} = −{c}. Solving, x = {greatest} or x = {_m(least)}; "
                f"the {which} is {_m(val)}.")
        ds = [(least if ask else greatest, f"This is the {'least' if ask else 'greatest'} solution."),
              (val + 1, "Off by one; re-solve both linear cases."),
              (m, "This is the center (b ÷ k); add or subtract c ÷ k to get x."),
              (b + c if ask else b - c, "Divide by {0} after isolating {0}x.".format(k))]
        verify = f"|{k}x-{b}|={c}"
    else:
        a, b = rng.randint(2, 5), rng.choice([v for v in range(-12, 13) if v != 0])
        kk, c = rng.randint(1, 15), rng.randint(2, 20)
        mm = kk + a * c  # |ax + b| + kk = mm  ->  |ax + b| = a c
        # solutions: ax + b = ±ac -> x = (±ac - b)/a
        s1, s2 = Fraction(a * c - b, a), Fraction(-a * c - b, a)
        mode = rng.choice(["sum", "greater"])
        prompt = (f"If |{_lin(a, b)}| + {kk} = {mm}, what is the "
                  f"{'sum of the solutions' if mode == 'sum' else 'greater solution'}?")
        val = s1 + s2 if mode == "sum" else max(s1, s2)
        expl = (f"Isolate: |{_lin(a, b)}| = {a * c}. Then {_lin(a, b)} = {a * c} or {_lin(a, b)} = −{a * c}, "
                f"giving x = {num_str(s1)} or x = {num_str(s2)}. The {'sum is' if mode == 'sum' else 'greater is'} {num_str(val)}.")
        ds = [(min(s1, s2) if mode == "greater" else s1, "That is one solution; the question asks for the {0}.".format("greater one" if mode == "greater" else "sum")),
              (Fraction(mm - b, a) if mode == "greater" else Fraction(-2 * b, a) + 1, "Subtract {0} before removing the absolute value.".format(kk)),
              (-val if val else val + 1, "Sign slip in the two cases."),
              (Fraction(a * c - b, a) + Fraction(a * c + b, a) if mode == "sum" else Fraction(a * c + b, a), "In the second case the right side is −{0}.".format(a * c))]
        verify = f"|{a}x+({b})|={a * c}"
    return _numeric_mc(rng, prompt, val, ds, subskill="solve_equations", explanation=expl,
                       est=80 if d == "easy" else 95, tags=["algebra", "absolute-value"], verify=verify)


def ab_evaluate(rng, d):
    """Evaluate expressions with absolute value."""
    if d == "easy":
        a, b = rng.randint(-20, 20), rng.randint(-20, 20)
        if a == b:
            b += 3
        prompt = f"What is the value of |{_m(a)} − {_m(b)}|?" if rng.random() < 0.5 else f"What is the value of |{_m(a - b)}| ?".replace(" ?", "?")
        val = abs(a - b)
        expl = f"|{_m(a)} − {_m(b)}| = |{_m(a - b)}| = {val}." if "−" in prompt and str(abs(a - b)) not in prompt.split("|")[1] else f"The absolute value of {_m(a - b)} is its distance from 0: {val}."
        ds = [(a - b if a - b != val else b - a, "Absolute value is never negative."), (abs(a) - abs(b) if abs(a) - abs(b) != val else abs(a) + abs(b), "|a − b| is not |a| − |b|."), (abs(a) + abs(b) if abs(a) + abs(b) != val else val + 2, "Subtract first, then take the absolute value."), (val + 1, "Arithmetic slip.")]
    elif d == "medium":
        x = rng.choice([v for v in range(-9, 10) if v != 0])
        a, b, c = rng.randint(2, 6), rng.choice([v for v in range(-12, 13) if v != 0]), rng.choice([v for v in range(-10, 11) if v != 0])
        val = abs(a * x + b) + c
        prompt = f"If x = {_m(x)}, what is the value of |{_lin(a, b)}| {_pm(c)}?"
        expl = f"|{a}({_m(x)}) {_pm(b)}| {_pm(c)} = |{_m(a * x + b)}| {_pm(c)} = {abs(a * x + b)} {_pm(c)} = {_m(val)}."
        ds = [(a * x + b + c, "Take the absolute value of {0} before adding {1}.".format(_m(a * x + b), _m(c))), (abs(a * x + b + c), "The absolute value covers only {0}, not the {1} term.".format(_lin(a, b), _m(c))), (abs(a * x) + b + c, "The absolute value covers the whole expression {0}.".format(_lin(a, b))), (val - 2 * c, "Check the sign of the outside term.")]
    else:
        p, q = rng.choice([v for v in range(-9, 10) if v != 0]), rng.choice([v for v in range(-9, 10) if v != 0])
        prompt = f"If a = {_m(p)} and b = {_m(q)}, what is the value of |a − b| − |a| + |b|?"
        val = abs(p - q) - abs(p) + abs(q)
        expl = f"|{_m(p)} − ({_m(q)})| − |{_m(p)}| + |{_m(q)}| = {abs(p - q)} − {abs(p)} + {abs(q)} = {_m(val)}."
        ds = [(abs(p - q) - abs(p) - abs(q), "The last term is added, not subtracted."), ((p - q) - p + q, "Each absolute value is non-negative."), (abs(p - q - p + q) if abs(p - q - p + q) != val else val + 3, "Evaluate each absolute value separately."), (abs(p - q) + abs(p) + abs(q), "Watch the sign on |a|.")]
    return _numeric_mc(rng, prompt, val, ds, subskill="solve_equations", explanation=expl,
                       tags=["algebra", "absolute-value", "evaluate"], est=70 if d == "easy" else 85, verify=f"val={val}")


def ab_inequality(rng, d):
    """Solution sets of absolute-value inequalities (text), counts of integers (numeric)."""
    a = rng.randint(-8, 15)
    c = rng.randint(1, 9)
    lo, hi = a - c, a + c
    if d == "easy":
        prompt = f"Which of the following describes all values of x that satisfy |x − {_m(a)}| < {c}?".replace("− -", "+ ")
        prompt = f"Which of the following describes all values of x that satisfy |x {_pm(-a)}| < {c}?"
        correct = f"{_m(lo)} < x < {_m(hi)}"
        ds = [(f"x < {_m(hi)}", "The inequality also bounds x from below."),
              (f"x < {_m(lo)} or x > {_m(hi)}", "That is the solution of |x − a| > c, not < c."),
              (f"{_m(-hi)} < x < {_m(-lo)}" if a != 0 else f"{_m(lo - 1)} < x < {_m(hi + 1)}", "The interval is centered at {0}.".format(_m(a))),
              (f"{_m(a)} < x < {_m(hi)}", "The distance condition applies on both sides of {0}.".format(_m(a)))]
        expl = f"|x − a| < c means a − c < x < a + c: {_m(lo)} < x < {_m(hi)}."
        return _text_mc(rng, prompt, correct, ds, subskill="solve_equations", explanation=expl,
                        tags=["algebra", "absolute-value", "inequality"], est=80, verify=correct.replace("−", "-"))
    if d == "medium":
        prompt = f"Which of the following describes all values of x that satisfy |x {_pm(-a)}| ≥ {c}?"
        correct = f"x ≤ {_m(lo)} or x ≥ {_m(hi)}"
        ds = [(f"{_m(lo)} ≤ x ≤ {_m(hi)}", "That is the solution of |x − a| ≤ c; ≥ gives the outside."),
              (f"x ≥ {_m(hi)}", "The left branch x ≤ {0} is also part of the solution.".format(_m(lo))),
              (f"x ≤ {_m(lo)} and x ≥ {_m(hi)}", "No x satisfies both; the branches are joined by 'or'."),
              (f"x ≥ {_m(lo)} or x ≤ {_m(hi)}", "The inequality directions are reversed.")]
        expl = f"|x − a| ≥ c means x − a ≥ c or x − a ≤ −c: x ≥ {_m(hi)} or x ≤ {_m(lo)}."
        return _text_mc(rng, prompt, correct, ds, subskill="solve_equations", explanation=expl,
                        tags=["algebra", "absolute-value", "inequality"], est=85, verify=correct.replace("−", "-"))
    val = 2 * c + 1
    prompt = rng.choice([f"How many integer values of x satisfy |x {_pm(-a)}| ≤ {c}?",
                         f"How many integers x satisfy the inequality |{_m(a)} − x| ≤ {c}?"])
    expl = f"|x − {_m(a)}| ≤ {c} means {_m(lo)} ≤ x ≤ {_m(hi)}, which contains {hi} − ({_m(lo)}) + 1 = {val} integers."
    ds = [(2 * c, "Count both endpoints: the range is inclusive, so add 1."),
          (c, "This counts only one side of the center, not the full range."),
          (2 * c + 2, "An inclusive range a − c to a + c has 2c + 1 integers."),
          (hi - lo if hi - lo != 2 * c else c + 1, "Recount the integers from {0} to {1}.".format(_m(lo), _m(hi)))]
    return _numeric_mc(rng, prompt, val, ds, subskill="solve_equations", explanation=expl,
                       tags=["algebra", "absolute-value", "inequality"], est=95, verify=f"|x-{a}|<={c}")


def ab_model(rng, d):
    """Absolute value as tolerance / distance (text options), or number of solutions."""
    if d == "hard" and rng.random() < 0.4:
        k = rng.randint(1, 12)
        a = rng.randint(1, 9)
        prompt = f"How many real solutions does the equation |x {_pm(a)}| = −{k} have?"
        val = 0
        expl = f"An absolute value is never negative, so |x {_pm(a)}| = −{k} has no solutions."
        ds = [(2, "An absolute-value equation has two solutions only when the right side is positive."),
              (1, "There is one solution only when the right side is 0."),
              (k, "The right side's size doesn't give the number of solutions."),
              (3, "An absolute-value equation has at most two solutions.")]
        return _numeric_mc(rng, prompt, val, ds, subskill="solve_equations", explanation=expl,
                           tags=["algebra", "absolute-value", "reasoning"], est=70, verify="0 solutions")
    ctx = rng.choice([
        ("A machine part must have a length within {t} millimeters of {c} millimeters.", "L", "length L", "millimeters"),
        ("A bakery's loaves are acceptable if their weight is within {t} grams of {c} grams.", "w", "weight w", "grams"),
        ("A thermostat keeps the room temperature within {t} degrees of {c} degrees.", "T", "temperature T", "degrees"),
        ("A bottling line fills bottles to within {t} milliliters of {c} milliliters.", "v", "volume v", "milliliters"),
    ])
    c = rng.randint(8, 60) * 5 if d != "easy" else rng.randint(10, 90)
    t = rng.choice([1, 2, 3, 5, 10]) if d != "easy" else rng.randint(1, 9)
    setup, var, vname, unit = ctx
    setup = setup.format(t=t, c=c)
    if d == "hard":
        prompt = f"{setup} Which inequality represents all acceptable values of the {vname}?"
        correct = f"|{var} − {c}| ≤ {t}"
        ds = [(f"|{var} − {t}| ≤ {c}", "The center is {0} and the tolerance is {1}.".format(c, t)),
              (f"|{var} + {c}| ≤ {t}", "Distance from {0} is |{1} − {0}|, with a minus sign.".format(c, var)),
              (f"|{var} − {c}| ≥ {t}", "Acceptable values are within the tolerance, so the distance is at most {0}.".format(t)),
              (f"{var} − {c} ≤ {t}", "This allows values far below {0}; the absolute value captures both directions.".format(c))]
        expl = f"'Within {t} of {c}' means the distance |{var} − {c}| is at most {t}."
        return _text_mc(rng, prompt, correct, ds, subskill="solve_equations", explanation=expl,
                        tags=["algebra", "absolute-value", "model"], est=85, verify=correct)
    if d == "medium":
        prompt = f"{setup} Which of the following is the greatest acceptable {vname.split()[0]}, in {unit}?"
        val = c + t
        expl = f"|{var} − {c}| ≤ {t} gives {c - t} ≤ {var} ≤ {c + t}; the greatest is {c + t}."
        ds = [(c - t, "That is the least acceptable value."), (c, "The target itself is acceptable but not the greatest."), (c + 2 * t, "The tolerance is {0}, not {1}.".format(t, 2 * t)), (t, "That is the tolerance, not a value.")]
    else:
        prompt = f"{setup} What is the range of acceptable values, in {unit}, from least to greatest?"
        correct = f"{c - t} to {c + t}"
        ds = [(f"{c} to {c + t}", "Values below {0} are also acceptable, down to {1}.".format(c, c - t)),
              (f"{c - 2 * t} to {c + 2 * t}", "The tolerance is {0} on each side.".format(t)),
              (f"{t} to {c}", "The tolerance is a distance from {0}, not a bound.".format(c)),
              (f"{c - t} to {c}", "Values above {0} up to {1} are acceptable too.".format(c, c + t))]
        expl = f"Within {t} of {c} means from {c} − {t} = {c - t} to {c} + {t} = {c + t}."
        return _text_mc(rng, prompt, correct, ds, subskill="solve_equations", explanation=expl,
                        tags=["algebra", "absolute-value", "model"], est=75, verify=correct)
    return _numeric_mc(rng, prompt, val, ds, subskill="solve_equations", explanation=expl,
                       tags=["algebra", "absolute-value", "model"], est=80, verify=f"max={val}")


def ab_gridin(rng, d):
    """Grid-in absolute value."""
    a, c = rng.randint(1, 25), rng.randint(1, 25)
    if d == "easy":
        prompt = f"If |x − {a}| = {c}, what is the greatest possible value of x?"
        val = a + c
        expl = f"x − {a} = {c} gives x = {a + c}."
    elif d == "medium":
        k, m, g = rng.randint(2, 6), rng.randint(2, 12), rng.randint(1, 8)
        prompt = f"If |{k}x − {k * m}| = {k * g}, what is the sum of all possible values of x?"
        val = 2 * m
        expl = f"x = {m + g} or x = {m - g}; sum = {2 * m}."
    else:
        c = rng.randint(1, 9)
        a = rng.randint(-5, 15)
        prompt = f"How many integer values of x satisfy |x {_pm(-a)}| < {c}?"
        val = 2 * c - 1
        expl = f"{_m(a - c)} < x < {_m(a + c)} (strict) contains {2 * c - 1} integers."
    return _spr_num(prompt, val, subskill="solve_equations", explanation=expl,
                    tags=["algebra", "absolute-value", "grid-in"], est=80, verify=f"val={val}")


ab_gridin.sat_only = True


# --------------------------------------------------------------------------- #
# exponential
# --------------------------------------------------------------------------- #
_EXP_CTX = [("bacteria in a culture", "hour"), ("users of an app", "month"), ("cells in a sample", "hour"),
            ("views of a video", "day"), ("fruit flies in a jar", "week"), ("subscribers to a newsletter", "month")]


def ex_value(rng, d):
    """Growth value (easy), decay value (medium), percent growth value (hard)."""
    thing, per = rng.choice(_EXP_CTX)
    if d == "easy":
        n0 = rng.choice([2, 3, 4, 5, 6, 8, 10, 12, 15, 20, 25, 30, 40, 50])
        r = rng.choice([2, 3])
        h = rng.randint(2, 5)
        val = n0 * r ** h
        word = {2: "doubles", 3: "triples"}[r]
        prompt = rng.choice([f"A population of {n0} {thing} {word} every {per}. How many will there be after {h} {per}s?",
                             f"There are {n0} {thing}, and the number {word} each {per}. How many {thing} are there after {h} {per}s?"])
        expl = f"Multiply by {r} each {per}: {n0} × {r}^{h} = {val}."
        ds = [(n0 * r * h, "This grows linearly (×r×time) instead of exponentially."),
              (n0 * r ** (h - 1), "This is the count one period too early."),
              (n0 + r * h, "This adds instead of repeatedly multiplying."),
              (n0 * r ** (h + 1), "This is one period too late.")]
    elif d == "medium":
        r = rng.choice([2, 3, 4])
        h = rng.randint(2, 4)
        final = rng.randint(2, 25)
        n0 = final * r ** h
        word = {2: "halves", 3: "is cut to one-third", 4: "is cut to one-quarter"}[r]
        prompt = f"A population of {n0} {thing} {word} every {per}. How many will there be after {h} {per}s?"
        val = final
        expl = f"Divide by {r} each {per}: {n0} ÷ {r}^{h} = {val}."
        ds = [(n0 // (r * h), "This divides once by r×time instead of repeatedly."),
              (n0 - r * h, "This subtracts instead of repeatedly dividing."),
              (val * r, "This stops one period too early."),
              (n0 // (r ** (h + 1)) if n0 % (r ** (h + 1)) == 0 else val // 2 if val % 2 == 0 else val + 1, "This goes one period too far.")]
    else:
        n0 = rng.choice([100, 200, 400, 500, 800, 1000, 2000, 2500, 5000])
        pct = rng.choice([5, 10, 20, 25, 50])
        up = rng.random() < 0.6
        h = rng.randint(2, 3)
        f = Fraction(100 + pct, 100) if up else Fraction(100 - pct, 100)
        val = n0 * f ** h
        word = "increases" if up else "decreases"
        prompt = (f"The number of {thing} is {n0} and {word} by {pct}% each {per}. How many {thing} "
                  f"will there be after {h} {per}s? (Round to the nearest whole number if necessary.)")
        expl = f"Each {per} multiplies by {num_str(f)}: {n0} × ({num_str(f)})^{h} ≈ {round(float(val))}."
        valr = round(float(val))
        ds = [(round(n0 * (1 + (pct / 100) * h * (1 if up else -1))), "Percent change compounds; it doesn't add up linearly."),
              (round(n0 * float(f)), "That is after only one {0}.".format(per)),
              (round(n0 * float(f) ** (h + 1)), "That is one {0} too many.".format(per)),
              (round(n0 * (pct / 100) ** h), "Multiply by (1 ± rate), not by the rate alone.")]
        return _numeric_mc(rng, prompt, valr, ds, subskill="growth_decay", explanation=expl,
                           tags=["advanced-math", "exponential", "percent"], est=95,
                           verify=f"{n0}*({num_str(f)})^{h}={float(val):.2f}")
    return _numeric_mc(rng, prompt, val, ds, subskill="growth_decay", explanation=expl,
                       tags=["advanced-math", "exponential"], est=80, verify=f"val={val}")


def ex_model(rng, d):
    """Choose the function that models the situation (text options)."""
    thing, per = rng.choice(_EXP_CTX)
    if d == "easy":
        n0 = rng.choice([5, 8, 10, 12, 15, 20, 25, 30, 40, 50, 60, 75, 80, 100, 120, 150, 200, 250, 300, 400, 500])
        r = rng.choice([2, 3, 4])
        verb = {2: "doubles", 3: "triples", 4: "quadruples"}[r] + f" every {per}"
        prompt = f"A population of {n0} {thing} {verb}. Which expression gives the population after t {per}s?"
        correct = f"{n0}·{r}^t"
        ds = [(f"{n0}·{r}·t", "This models linear change (a fixed amount each period), not repeated multiplication."),
              (f"{n0} + {r}·t", "This adds a constant each period instead of multiplying."),
              (f"{n0}^t·{r}", "The repeating growth factor is the base raised to t, applied to the starting amount."),
              (f"{r}·t^{n0}" if n0 < 100 else f"({n0}·{r})^t", "The variable t belongs in the exponent, with base {0}.".format(r))]
        expl = f"Each {per} multiplies the amount by {r}, so after t {per}s the population is {correct}."
    elif d == "medium":
        n0 = rng.choice([100, 250, 500, 800, 1000, 1500, 2000, 5000])
        pct = rng.choice([2, 3, 4, 5, 6, 8, 10, 12, 15, 20, 25])
        up = rng.random() < 0.5
        f = (100 + pct) / 100 if up else (100 - pct) / 100
        word = "increases" if up else "decreases"
        ctx = rng.choice([f"The value of a car is ${n0} and {word} by {pct}% each year",
                          f"A town's population is {n0} and {word} by {pct}% per year",
                          f"An investment of ${n0} {word} by {pct}% each year"])
        prompt = f"{ctx}. Which function gives the value V after t years?"
        correct = f"V(t) = {n0}({f:g})^t"
        wrong_f = (100 - pct) / 100 if up else (100 + pct) / 100
        ds = [(f"V(t) = {n0}({wrong_f:g})^t", f"A {pct}% {word.rstrip('s')} means a factor of {f:g}, not {wrong_f:g}."),
              (f"V(t) = {n0}({pct / 100:g})^t", "The factor is 1 ± the rate, not the rate alone."),
              (f"V(t) = {n0} {'+' if up else '−'} {pct / 100 * n0:g}t", "Percent change compounds (exponential), it doesn't add a fixed amount each year."),
              (f"V(t) = {n0}·{f:g}·t", "The time t belongs in the exponent.")]
        expl = f"A {pct}% {word.rstrip('s')} per year multiplies by {f:g} each year: {correct}."
    else:
        n0 = rng.choice([100, 200, 400, 500, 1000, 2000, 3000])
        r = rng.choice([2, 3, 4])
        k = rng.choice([2, 3, 4, 5, 6, 8, 10, 12, 24])
        verb = {2: "doubles", 3: "triples", 4: "quadruples"}[r]
        unit = rng.choice([("hours", "hour"), ("days", "day"), ("years", "year"), ("minutes", "minute")])
        prompt = (f"A population of {n0} {thing} {verb} every {k} {unit[0]}. Which function gives the "
                  f"population P after t {unit[0]}?")
        correct = f"P(t) = {n0}·{r}^(t/{k})"
        ds = [(f"P(t) = {n0}·{r}^({k}t)", "The population multiplies once every {0} {1}, so the exponent is t/{0}.".format(k, unit[0])),
              (f"P(t) = {n0}·{r}^t", "That would be {0} every {1}, not every {2} {3}.".format(verb.replace("s", "ing", 1) if False else verb, unit[1], k, unit[0])),
              (f"P(t) = {n0}·{k}^(t/{r})", "The growth factor is {0}; the period is {1}.".format(r, k)),
              (f"P(t) = {n0}·({r}/{k})^t", "The period divides the exponent, not the base.")]
        expl = f"In t {unit[0]} there are t/{k} periods, each multiplying by {r}: {correct}."
    return _text_mc(rng, prompt, correct, ds, subskill="growth_decay", explanation=expl,
                    tags=["advanced-math", "exponential", "model"], est=90, verify=f"model {correct}")


def ex_interpret(rng, d):
    """Read parameters of an exponential model: initial value, rate, meaning."""
    n0 = rng.choice([50, 80, 120, 150, 200, 250, 300, 400, 500, 600, 750, 800, 1000, 1200, 2000])
    pct = rng.choice([2, 3, 4, 5, 6, 8, 10, 12, 15, 20, 25, 30])
    up = rng.random() < 0.5
    f = (100 + pct) / 100 if up else (100 - pct) / 100
    ctx = rng.choice([("the number of fish in a lake", "years", "fish"), ("the value, in dollars, of a collectible", "years", "dollars"),
                      ("the mass, in grams, of a substance", "hours", "grams"), ("the number of members of a club", "months", "members")])
    rule = f"f(t) = {n0}({f:g})^t"
    if d == "easy":
        prompt = f"The function {rule} models {ctx[0]} t {ctx[1]} after it was first measured. What was the initial value?"
        val = n0
        expl = f"At t = 0, f(0) = {n0}·({f:g})⁰ = {n0}."
        ds = [(round(n0 * f), "That is the value after one {0}.".format(ctx[1][:-1])), (pct, "That is the percent rate, not the starting value."), (round(n0 * f * f), "That is the value after two periods."), (n0 + pct, "The initial value is the coefficient.")]
        return _numeric_mc(rng, prompt, val, ds, subskill="growth_decay", explanation=expl,
                           tags=["advanced-math", "exponential", "interpret"], est=65, verify=f"f(0)={n0}")
    if d == "medium":
        prompt = f"The function {rule} models {ctx[0]} t {ctx[1]} after it was first measured. By what percent does the quantity {'increase' if up else 'decrease'} each {ctx[1][:-1]}?"
        val = pct
        expl = f"The factor {f:g} = 1 {'+' if up else '−'} {pct / 100:g}, so the quantity {'grows' if up else 'shrinks'} by {pct}% per {ctx[1][:-1]}."
        ds = [(round(f * 100), "{0}% is the factor as a percent; the change is the part above or below 100%.".format(round(f * 100))), (100 - pct if up else 100 + pct, "Compare the factor to 1 (100%)."), (pct * 2, "Arithmetic slip; {0} − 1 = ±{1}.".format(f, pct / 100)), (n0 // 10 if n0 // 10 != pct else n0 // 5, "The percent comes from the base, not the coefficient.")]
        return _numeric_mc(rng, prompt, val, ds, subskill="growth_decay", explanation=expl,
                           tags=["advanced-math", "exponential", "interpret"], fmt=lambda v: f"{num_str(v)}%", est=80, verify=f"rate={pct}%")
    prompt = f"The function {rule} models {ctx[0]} t {ctx[1]} after it was first measured. Which statement best interprets the number {f:g} in this model?"
    correct = f"Each {ctx[1][:-1]}, the quantity is {f:g} times what it was the previous {ctx[1][:-1]}."
    ds = [(f"Each {ctx[1][:-1]}, the quantity {'increases' if up else 'decreases'} by {f:g} {ctx[2]} compared with the previous {ctx[1][:-1]}.", "The base is a multiplier, not an amount added or removed."),
          (f"The quantity was {f:g} {ctx[2]} at the moment it was first measured, when t = 0.", "The initial value is {0}, the coefficient.".format(n0)),
          (f"After {f:g} {ctx[1]} have passed, the quantity is twice what it was at the start.", "The base says nothing about doubling time directly."),
          (f"Each {ctx[1][:-1]}, the quantity {'increases' if up else 'decreases'} by {round(f * 100)}% of what it was the previous {ctx[1][:-1]}.", "The percent change is {0}%, the part of {1} beyond 1.".format(pct, f))]
    expl = f"In f(t) = a·b^t, the base b = {f:g} is the factor applied each {ctx[1][:-1]}: a {pct}% {'increase' if up else 'decrease'}."
    return _text_mc(rng, prompt, correct, ds, subskill="growth_decay", explanation=expl,
                    tags=["advanced-math", "exponential", "interpret"], est=85, verify=f"base={f:g}")


def ex_periods(rng, d):
    """How many periods to reach a value / half-life / linear vs exponential tables."""
    if d == "easy":
        n0 = rng.choice([1, 2, 3, 5, 10, 20, 25, 50, 100])
        r = rng.choice([2, 3, 4, 5, 10])
        h = rng.randint(2, 5) if r <= 3 else rng.randint(2, 3)
        target = n0 * r ** h
        per = rng.choice(["hour", "day", "week", "year"])
        thing = rng.choice(["bacteria", "rabbits", "subscribers", "cells", "dollars in an account"])
        prompt = f"A count of {n0} {thing} is multiplied by {r} every {per}. After how many {per}s will the count first reach {target}?"
        val = h
        expl = f"{n0}·{r}^t = {target} → {r}^t = {target // n0} = {r}^{h} → t = {h}."
        ds = [(h + 1, "That is one period too many."), (h - 1, "That is one period too few."), (target // n0, "That is the growth multiple, not the number of periods."), (Fraction(target, n0 * r), "Count how many times {0} must be multiplied in.".format(r))]
        return _numeric_mc(rng, prompt, val, ds, subskill="growth_decay", explanation=expl,
                           tags=["advanced-math", "exponential"], est=80, verify=f"{n0}*{r}^{h}={target}")
    if d == "medium":
        hl = rng.choice([2, 3, 4, 5, 6, 8, 10, 12, 20, 25, 50, 100])
        n = rng.randint(2, 4)
        n0 = rng.choice([8, 16, 32, 40, 48, 64, 80, 96, 120, 160, 200, 240, 320, 400, 800])
        unit = rng.choice(["hours", "days", "years", "minutes"])
        val = Fraction(n0, 2 ** n)
        prompt = (f"A radioactive sample has a half-life of {hl} {unit}: every {hl} {unit}, half of it decays. "
                  f"If the sample starts at {n0} grams, how many grams remain after {hl * n} {unit}?")
        expl = f"{hl * n} {unit} is {n} half-lives; {n0} ÷ 2^{n} = {num_str(val)} grams."
        ds = [(n0 - n0 // 2 * n if n0 - n0 // 2 * n > 0 else Fraction(n0, 2 ** (n + 1)), "Each half-life halves what remains; it doesn't subtract a fixed amount."),
              (Fraction(n0, 2), "That is after one half-life only."),
              (Fraction(n0, 2 * n), "Divide by 2 repeatedly ({0} times), not by 2·{0}.".format(n)),
              (Fraction(n0, 2 ** (n + 1)), "That is one half-life too many.")]
        return _numeric_mc(rng, prompt, val, ds, subskill="growth_decay", explanation=expl,
                           tags=["advanced-math", "exponential", "half-life"], est=90, verify=f"{n0}/2^{n}")
    # hard: which table shows exponential growth (text), with table stimulus of one data set
    kind = rng.choice(["exp", "lin"])
    r = rng.choice([2, 3, 4, 5])
    a = rng.choice([1, 2, 3, 4, 5, 6, 8, 10, 12, 15, 20])
    m = rng.randint(3, 25)
    xs = [0, 1, 2, 3]
    ys = [a * r ** x for x in xs] if kind == "exp" else [a + m * x for x in xs]
    stim = _table("Values of f", ["x", "f(x)"], [[x, y] for x, y in zip(xs, ys)])
    prompt = "The table gives values of the function f for four consecutive integer inputs. Which statement about f is supported by the table?"
    if kind == "exp":
        correct = f"f is exponential, because each output is {r} times the previous output."
        ds = [(f"f is linear, because each output increases by {ys[1] - ys[0]}.", f"The differences {ys[1] - ys[0]}, {ys[2] - ys[1]}, {ys[3] - ys[2]} are not constant."),
              (f"f is linear, because the outputs increase as x increases.", "Increasing outputs alone don't make a function linear; check the differences."),
              (f"f is exponential, because each output is {ys[1] - ys[0]} more than the previous output.", "Exponential growth is a constant ratio, not a constant difference."),
              ("f is neither linear nor exponential.", f"The ratios are all {r}, which is exponential.")]
        expl = f"Ratios of consecutive outputs: {ys[1]}/{ys[0]} = {ys[2]}/{ys[1]} = {ys[3]}/{ys[2]} = {r}, a constant ratio, so f is exponential."
    else:
        correct = f"f is linear, because each output is {m} more than the previous output."
        ds = [(f"f is exponential, because each output is {Fraction(ys[1], ys[0])} times the previous output.", f"The ratios {num_str(Fraction(ys[1], ys[0]))} and {num_str(Fraction(ys[2], ys[1]))} differ, so the ratio isn't constant."),
              (f"f is exponential, because the outputs increase as x increases.", "Increasing outputs alone don't make a function exponential; check the ratios."),
              (f"f is linear, because each output is {m} times the previous output.", "Linear growth is a constant difference, not a constant ratio."),
              ("f is neither linear nor exponential.", f"The differences are all {m}, which is linear.")]
        expl = f"Differences of consecutive outputs: {ys[1] - ys[0]}, {ys[2] - ys[1]}, {ys[3] - ys[2]}, a constant {m}, so f is linear."
    prompt = f"The table gives values of a function f with f(0) = {ys[0]} and f(3) = {ys[3]}. Which statement about f is supported by the table?"
    return _text_mc(rng, prompt, correct, ds, subskill="growth_decay", explanation=expl,
                    qtype="data_interpretation", tags=["advanced-math", "exponential", "table"], est=95,
                    stimulus=stim, verify=f"{kind} {ys}")


def ex_gridin(rng, d):
    """Grid-in exponential values."""
    if d == "easy":
        n0 = rng.choice([2, 3, 4, 5, 6, 8, 10, 12, 15, 20, 25])
        r, h = rng.choice([2, 3]), rng.randint(2, 5)
        prompt = f"A population of {n0} doubles every hour." if r == 2 else f"A population of {n0} triples every hour."
        prompt += f" What is the population after {h} hours?"
        val = n0 * r ** h
        expl = f"{n0} × {r}^{h} = {val}."
    elif d == "medium":
        r, h, final = rng.choice([2, 3, 4, 5]), rng.randint(2, 4), rng.randint(2, 60)
        n0 = final * r ** h
        prompt = f"A quantity of {n0} is divided by {r} every day. What is the quantity after {h} days?"
        val = final
        expl = f"{n0} ÷ {r}^{h} = {final}."
    else:
        n0 = rng.choice([100, 200, 300, 400, 500, 600, 800, 1000, 1200, 1500, 2000, 2500, 4000, 5000])
        pct = rng.choice([5, 10, 15, 20, 25, 30, 40, 50])
        f = Fraction(100 + pct, 100)
        val = n0 * f * f
        prompt = f"An account balance of ${n0} grows by {pct}% each year. What is the balance, in dollars, after 2 years?"
        expl = f"{n0} × ({num_str(f)})² = {num_str(val)}."
    return _spr_num(prompt, val, subskill="growth_decay", explanation=expl,
                    tags=["advanced-math", "exponential", "grid-in"], est=85, verify=f"val={num_str(val)}")


ex_gridin.sat_only = True


# --------------------------------------------------------------------------- #
# two_way_tables
# --------------------------------------------------------------------------- #
def _two_way(rng, missing=False):
    rcat = rng.choice([("Cats", "Dogs"), ("Fiction", "Nonfiction"), ("Bus", "Bike"), ("Coffee", "Tea"),
                       ("Soccer", "Basketball"), ("Left-handed", "Right-handed")])
    ccat = rng.choice([("Weekday", "Weekend"), ("Morning", "Evening"), ("Adults", "Students"),
                       ("Grade 9", "Grade 10"), ("Urban", "Rural")])
    a, b, c, d = (rng.randint(5, 60) for _ in range(4))
    total = a + b + c + d
    rows = [[rcat[0], a, b, a + b], [rcat[1], c, d, c + d], ["Total", a + c, b + d, total]]
    stim = _table("Survey responses", ["", ccat[0], ccat[1], "Total"], rows)
    return rcat, ccat, a, b, c, d, total, stim


def tw_probability(rng, d):
    """Marginal (easy), joint (medium), conditional (hard) probability."""
    rcat, ccat, a, b, c, e, total, stim = _two_way(rng)
    if d == "easy":
        val = Fraction(a + b, total)
        prompt = f"The table shows {total} survey responses. If one response is chosen at random, what is the probability that it is in the “{rcat[0]}” row?"
        expl = f"The “{rcat[0]}” row totals {a} + {b} = {a + b} of {total}: {num_str(val)}."
        ds = [(Fraction(a, total), f"This uses only one cell ({a}), not the whole row."),
              (Fraction(c + e, total), "This is the probability of the other row."),
              (Fraction(a + b, c + e), "Divide by the grand total, not the other row."),
              (Fraction(a + c, total), f"That is the “{ccat[0]}” column, not the “{rcat[0]}” row.")]
    elif d == "medium":
        val = Fraction(a, total)
        prompt = f"The table shows {total} survey responses. If one response is chosen at random, what is the probability that it is both “{rcat[0]}” and “{ccat[0]}”?"
        expl = f"That single cell holds {a} of the {total} responses: {num_str(val)}."
        ds = [(Fraction(a, a + b), "This conditions on the row instead of using the grand total."),
              (Fraction(a, a + c), "This conditions on the column instead of the grand total."),
              (Fraction(a + b, total), "This is the whole row, not the single cell."),
              (Fraction(a + b + c, total), "'Both' means the single cell, not either/or.")]
    else:
        val = Fraction(a, a + c)
        prompt = f"The table shows {total} survey responses. Given that a response is “{ccat[0]}”, what is the probability that it is also “{rcat[0]}”?"
        expl = f"Restrict to the “{ccat[0]}” column ({a} + {c} = {a + c}); of those, {a} are “{rcat[0]}”: {num_str(val)}."
        ds = [(Fraction(a, total), "Condition on the column total, not the grand total."),
              (Fraction(a, a + b), "Condition on the column, not the row."),
              (Fraction(c, a + c), "This is the probability of the other row in the column."),
              (Fraction(a + c, total), "That is the probability of the column itself.")]
    return _numeric_mc(rng, prompt, val, ds, subskill="conditional_probability", explanation=expl,
                       qtype="data_interpretation", est=90, tags=["data", "probability", "table"],
                       verify=f"P={num_str(val)}", stimulus=stim)


def tw_count(rng, d):
    """Read or reconstruct counts from a two-way table."""
    rcat, ccat, a, b, c, e, total, stim = _two_way(rng)
    if d == "easy":
        which = rng.choice(["cell", "row", "col"])
        if which == "cell":
            prompt = f"According to the table of {total} responses, how many responses were “{rcat[1]}” and “{ccat[1]}”?"
            val = e
            expl = f"The cell in the “{rcat[1]}” row and “{ccat[1]}” column is {e}."
            ds = [(c, "That is the other cell in the row."), (b, "That is the other cell in the column."), (c + e, "That is the row total, not the single cell."), (b + e, "That is the column total.")]
        elif which == "row":
            prompt = f"According to the table of {total} responses, how many responses in all were “{rcat[0]}”?"
            val = a + b
            expl = f"Add across the row: {a} + {b} = {a + b}."
            ds = [(a, "That is one cell, not the whole row."), (a + c, "That is a column total."), (c + e, "That is the other row."), (total, "That is the grand total.")]
        else:
            prompt = f"According to the table of {total} responses, how many responses came from the “{ccat[1]}” group?"
            val = b + e
            expl = f"Add down the column: {b} + {e} = {b + e}."
            ds = [(a + c, "That is the other column."), (e, "That is one cell, not the whole column."), (c + e, "That is a row total."), (total, "That is the grand total.")]
    elif d == "medium":
        rows = [[rcat[0], a, "?", a + b], [rcat[1], c, e, c + e], ["Total", a + c, b + e, total]]
        stim = _table("Survey responses", ["", ccat[0], ccat[1], "Total"], rows)
        prompt = f"In the table of {total} responses, one value is missing. How many responses were “{rcat[0]}” and “{ccat[1]}”?"
        val = b
        expl = f"Row total minus the known cell: {a + b} − {a} = {b} (check: column {b} + {e} = {b + e})."
        ds = [(a, "That is the known cell in the row."), (a + b, "That is the row total; subtract the known cell."), (e, "That is the other cell in the column."), (b + e - a if b + e - a > 0 and b + e - a != b else b + 3, "Subtract within the same row or the same column.")]
    else:
        rows = [[rcat[0], a, "?", a + b], [rcat[1], "?", e, c + e], ["Total", a + c, b + e, total]]
        stim = _table("Survey responses", ["", ccat[0], ccat[1], "Total"], rows)
        if b == e:
            return tw_count(rng, d)
        # Ask "how many more" of the larger group, so the answer is positive.
        more, fewer = (rcat[0], rcat[1]) if b > e else (rcat[1], rcat[0])
        prompt = f"Two values in the table of {total} responses are missing. How many more responses were “{more}” than “{fewer}” in the “{ccat[1]}” column?"
        val = abs(b - e)
        expl = (f"Missing “{rcat[0]}”/“{ccat[1]}” = {a + b} − {a} = {b}; the “{rcat[1]}”/“{ccat[1]}” cell is {e}. "
                f"Then {max(b, e)} − {min(b, e)} = {val}.")
        ds = [(b if b != val else b + e, "That is the missing cell itself, not the difference."), (-val, "The comparison is reversed."), (b + e, "Subtract; don't add."), (a - e, "Use the “{0}” column, not the “{1}” cell.".format(ccat[1], ccat[0]))]
    return _numeric_mc(rng, prompt, val, ds, subskill="conditional_probability", explanation=expl,
                       qtype="data_interpretation", est=75 if d == "easy" else 95,
                       tags=["data", "table"], verify=f"val={val}", stimulus=stim)


def tw_fraction_percent(rng, d):
    """Fraction/percent of a group from a two-way table."""
    rcat, ccat, a, b, c, e, total, stim = _two_way(rng)
    if d == "easy":
        val = Fraction(a, a + b)
        prompt = f"Based on the table of {total} responses, what fraction of the “{rcat[0]}” responses were “{ccat[0]}”?"
        expl = f"{a} of the {a + b} “{rcat[0]}” responses were “{ccat[0]}”: {num_str(val)}."
        ds = [(Fraction(a, total), "Use the row total as the denominator, not the grand total."), (Fraction(a, a + c), "That is the fraction of the column, not the row."), (Fraction(b, a + b), "That is the fraction that were “{0}”.".format(ccat[1])), (Fraction(a + b, total), "That is the row's share of all responses.")]
    elif d == "medium":
        pct = round(100 * c / (a + c))
        val = pct
        prompt = f"Based on the table of {total} responses, approximately what percent of the “{ccat[0]}” responses were “{rcat[1]}”?"
        expl = f"{c}/{a + c} × 100 ≈ {pct}%."
        ds = [(round(100 * c / total), "Divide by the column total, not the grand total."), (round(100 * c / (c + e)), "Divide by the column total, not the row total."), (round(100 * a / (a + c)), "That is the percent that were “{0}”.".format(rcat[0])), (100 - pct + 1 if 100 - pct + 1 != pct else pct + 7, "Arithmetic slip.")]
        return _numeric_mc(rng, prompt, val, ds, subskill="conditional_probability", explanation=expl,
                           qtype="data_interpretation", est=90, tags=["data", "table", "percent"],
                           fmt=lambda v: f"{num_str(v)}%", verify=f"{c}/{a + c}", stimulus=stim)
    else:
        n = rng.choice([200, 300, 400, 500, 1000, 1200, 1500, 2000])
        val = round(n * (a + c) / total)
        prompt = (f"The table shows a random sample of {total} responses from a population of {n}. Based on the "
                  f"sample, approximately how many people in the whole population would be expected to be “{ccat[0]}”?")
        expl = f"Sample proportion = {a + c}/{total}; × {n} ≈ {val}."
        ds = [(a + c, "That is the sample count; scale it to the population."), (round(n * a / total), "Use the whole “{0}” column, not one cell.".format(ccat[0])), (round(n * (b + e) / total), "That is the expected count for “{0}”.".format(ccat[1])), (round(n * (a + c) / (b + e)), "Divide by the grand total of the sample.")]
    return _numeric_mc(rng, prompt, val, ds, subskill="conditional_probability", explanation=expl,
                       qtype="data_interpretation", est=90, tags=["data", "table"],
                       verify=f"val={num_str(val)}", stimulus=stim)


def tw_compare(rng, d):
    """Which group is more likely / statement supported (text)."""
    rcat, ccat, a, b, c, e, total, stim = _two_way(rng)
    p_col0 = Fraction(a, a + c)   # P(rcat0 | ccat0)
    p_col1 = Fraction(b, b + e)   # P(rcat0 | ccat1)
    if p_col0 == p_col1:
        return tw_compare(rng, d)
    hi_col = ccat[0] if p_col0 > p_col1 else ccat[1]
    lo_col = ccat[1] if hi_col == ccat[0] else ccat[0]
    if d != "hard":
        prompt = (f"Based on the table of {total} responses, which statement correctly compares the two "
                  f"“{ccat[0]}”/“{ccat[1]}” groups?")
        correct = f"A “{hi_col}” response is more likely than a “{lo_col}” response to be “{rcat[0]}”."
        ds = [(f"A “{lo_col}” response is more likely than a “{hi_col}” response to be “{rcat[0]}”.",
               f"Compare proportions: {a}/{a + c} ≈ {float(p_col0):.2f} vs {b}/{b + e} ≈ {float(p_col1):.2f}."),
              (f"The two groups are equally likely to be “{rcat[0]}”.", "The proportions differ."),
              (f"A “{hi_col}” response is more likely to be “{rcat[0]}” because the “{hi_col}” column has more responses.",
               "Likelihood depends on the proportion within the group, not the group's size."),
              (f"Every “{hi_col}” response is “{rcat[0]}”.", "The “{0}” column contains both rows.".format(hi_col))]
        expl = (f"P({rcat[0]} | {ccat[0]}) = {a}/{a + c} ≈ {float(p_col0):.2f} and P({rcat[0]} | {ccat[1]}) = "
                f"{b}/{b + e} ≈ {float(p_col1):.2f}; the larger is “{hi_col}”.")
    else:
        p_row0 = Fraction(a, a + b)
        prompt = f"Based on the table of {total} responses, which of the following statements must be true?"
        bigger_col = ccat[0] if a + c > b + e else ccat[1]
        if a + c == b + e:
            return tw_compare(rng, d)
        correct = f"The proportion of “{rcat[0]}” responses is higher among “{hi_col}” responses than among “{lo_col}” responses."
        ds = [(f"The proportion of “{rcat[0]}” responses is higher among “{lo_col}” responses than among “{hi_col}” responses.",
               f"{float(p_col0):.2f} vs {float(p_col1):.2f}: the higher proportion is in “{hi_col}”."),
              (f"More than half of all responses are “{rcat[0]}”." if 2 * (a + b) <= total else f"Fewer than half of all responses are “{rcat[0]}”.",
               f"“{rcat[0]}” accounts for {a + b} of {total} responses."),
              (f"The “{bigger_col}” group has a higher proportion of “{rcat[0]}” responses simply because it is the larger group.",
               "Group size doesn't determine the within-group proportion."),
              (f"Exactly {a + b} of the “{ccat[0]}” responses are “{rcat[0]}”.", f"The “{ccat[0]}” column has {a} “{rcat[0]}” responses; {a + b} is the row total.")]
        expl = (f"Within “{ccat[0]}”: {a}/{a + c} ≈ {float(p_col0):.2f}; within “{ccat[1]}”: {b}/{b + e} ≈ {float(p_col1):.2f}. "
                f"So the proportion is higher among “{hi_col}”.")
    return _text_mc(rng, prompt, correct, ds, subskill="conditional_probability", explanation=expl,
                    qtype="data_interpretation", est=100, tags=["data", "table", "compare"],
                    verify=f"{float(p_col0):.3f} vs {float(p_col1):.3f}", stimulus=stim)


def tw_gridin(rng, d):
    """Grid-in from a two-way table."""
    rcat, ccat, a, b, c, e, total, stim = _two_way(rng)
    if d == "easy":
        prompt = f"The table shows {total} survey responses. How many responses were “{rcat[0]}” and “{ccat[1]}”?"
        val = b
        expl = f"Read the “{rcat[0]}” row, “{ccat[1]}” column: {b}."
    elif d == "medium":
        prompt = f"The table shows {total} survey responses. If one response is selected at random, what is the probability that it is “{rcat[1]}”?"
        val = Fraction(c + e, total)
        expl = f"({c} + {e})/{total} = {num_str(val)}."
    else:
        prompt = f"The table shows {total} survey responses. If a “{ccat[1]}” response is selected at random, what is the probability that it is “{rcat[1]}”?"
        val = Fraction(e, b + e)
        expl = f"{e}/({b} + {e}) = {num_str(val)}."
    return _spr_num(prompt, val, subskill="conditional_probability", explanation=expl,
                    tags=["data", "table", "grid-in"], est=85, verify=f"val={num_str(val)}", stimulus=stim)


tw_gridin.sat_only = True


# --------------------------------------------------------------------------- #
# scatterplots
# --------------------------------------------------------------------------- #
_SP_CTX = [("hours studied", "test score", "points", "hour"), ("temperature (°F)", "ice cream sales", "sales", "degree"),
           ("years since 2010", "price (dollars)", "dollars", "year"), ("engine size (liters)", "fuel use (gallons per 100 miles)", "gallons", "liter"),
           ("age of car (years)", "value (thousands of dollars)", "thousand dollars", "year"), ("minutes of exercise", "heart rate (bpm)", "bpm", "minute")]


def _scatter(rng, m, b, n=7, xmax=14):
    xs = sorted(rng.sample(range(1, xmax), n))
    pts = [[x, m * x + b + rng.randint(-3, 3)] for x in xs]
    return pts, {"type": "figure", "figure": {"kind": "scatter", "caption": "Scatterplot with line of best fit",
                                             "points": pts, "line": {"m": m, "b": b}, "xlabel": "x"}}


def sp_interpret(rng, d):
    """Interpret slope (easy) / intercept (medium) / in context (hard)."""
    m = rng.choice([v for v in range(-9, 10) if v != 0])
    b = rng.randint(-8, 40)
    if abs(b) == abs(m):
        b += 5
    pts, fig = _scatter(rng, m, b)
    eq = f"y = {_lin(m, b)}"
    if d == "easy":
        prompt = f"The line of best fit for the scatterplot is {eq}. Which statement best interprets the slope of this model?"
        correct = f"For each increase of 1 in x, y {'increases' if m > 0 else 'decreases'} by about {abs(m)}."
        ds = [(f"For each increase of 1 in x, y {'increases' if b > 0 else 'decreases'} by about {abs(b)}.", "That is the y-intercept's value, not the slope."),
              (f"When x is 0, y is about {_m(m)}.", "That describes the intercept, not the slope; the slope is the rate."),
              (f"For each increase of 1 in y, x {'increases' if m > 0 else 'decreases'} by about {abs(m)}.", "This reverses the roles of x and y."),
              (f"For each increase of 1 in x, y {'decreases' if m > 0 else 'increases'} by about {abs(m)}.", "The sign of the slope gives the direction of change.")]
        expl = f"In {eq}, the slope {_m(m)} is the predicted change in y per unit increase in x."
        verify = f"slope={m}"
    elif d == "medium":
        prompt = f"The line of best fit for the scatterplot is {eq}. Which statement best interprets the y-intercept of this model?"
        correct = f"When x is 0, the predicted value of y is about {_m(b)}."
        ds = [(f"For each increase of 1 in x, y changes by about {_m(b)}.", "That describes the slope's role, not the intercept."),
              (f"When x is 0, the predicted value of y is about {_m(m)}.", "The intercept is the constant term, not the slope."),
              (f"When y is 0, the predicted value of x is about {_m(b)}.", "The y-intercept is the value of y when x = 0, not the reverse."),
              (f"The maximum value of y is about {_m(b)}.", "The intercept is a starting value, not a maximum.")]
        expl = f"In {eq}, the y-intercept {_m(b)} is the predicted y when x = 0."
        verify = f"intercept={b}"
    else:
        xl, yl, unit, xunit = rng.choice(_SP_CTX)
        m = abs(m) if "studied" in xl or "temperature" in xl or "since" in xl or "exercise" in xl else -abs(m)
        b = abs(b) + 10
        pts, fig = _scatter(rng, m, b)
        fig["figure"]["xlabel"] = xl
        eq = f"y = {_lin(m, b)}"
        prompt = (f"The scatterplot shows {yl} (y) versus {xl} (x) for a sample, and the line of best fit is {eq}. "
                  f"Which statement is the best interpretation of the number {abs(m)} in this context?")
        correct = f"For each additional {xunit}, the predicted {yl.split(' (')[0]} {'increases' if m > 0 else 'decreases'} by about {abs(m)} {unit}."
        ds = [(f"When the {xl.split(' (')[0]} is 0, the predicted {yl.split(' (')[0]} is about {abs(m)} {unit}.", "That would describe the intercept, which is {0}.".format(b)),
              (f"For each additional {xunit}, the predicted {yl.split(' (')[0]} {'decreases' if m > 0 else 'increases'} by about {abs(m)} {unit}.", "The sign of the slope is {0}.".format("positive" if m > 0 else "negative")),
              (f"The {yl.split(' (')[0]} is exactly {abs(m)} {unit} for every data point.", "A line of best fit predicts; it doesn't fit every point exactly."),
              (f"For each additional {unit.split()[0] if unit != 'thousand dollars' else 'thousand dollars'} of {yl.split(' (')[0]}, the {xl.split(' (')[0]} increases by about {abs(m)} {xunit}s.", "This reverses the roles of x and y.")]
        expl = f"The slope {_m(m)} is the predicted change in y ({yl}) per unit of x ({xl})."
        verify = f"slope={m}"
    return _text_mc(rng, prompt, correct, ds, subskill="model_interpret", explanation=expl,
                    qtype="data_interpretation", est=85, tags=["data", "scatterplot"], verify=verify, stimulus=fig)


def sp_predict(rng, d):
    """Predict y from x (easy/medium), solve for x (hard)."""
    m = rng.choice([v for v in range(-9, 10) if v != 0])
    b = rng.randint(-8, 40)
    pts, fig = _scatter(rng, m, b)
    eq = f"y = {_lin(m, b)}"
    if d != "hard":
        k = rng.randint(2, 14) if d == "easy" else rng.randint(15, 40)
        y = m * k + b
        prompt = rng.choice([f"The line of best fit for the scatterplot is {eq}. Based on this model, what value of y is predicted when x = {k}?",
                             f"A line of best fit for the data shown is {eq}. According to the model, what is the predicted value of y for x = {k}?"])
        expl = f"Substitute x = {k}: y = {_m(m)}·{k} {_pm(b)} = {_m(y)}."
        ds = [(m * k, "You left off the y-intercept term."), (m + k + b, "Multiply m by x; don't add."), (m * k - b, "Check the sign of the intercept term."), (k * b + m, "The slope multiplies x, not the intercept.")]
        val = y
    else:
        k = rng.randint(2, 14)
        y = m * k + b
        prompt = f"The line of best fit for the scatterplot is {eq}. According to the model, for what value of x is the predicted value of y equal to {_m(y)}?"
        expl = f"Solve {_m(y)} = {_lin(m, b)}: {_m(m)}x = {_m(y - b)}, so x = {k}."
        ds = [(y - b, "Divide by the slope after subtracting the intercept."), (Fraction(y + b, m), "Subtract the intercept; don't add it."), (m * y + b, "This evaluates the model at x = {0} instead of solving for x.".format(_m(y))), (-k, "Sign slip.")]
        val = k
    return _numeric_mc(rng, prompt, val, ds, subskill="model_interpret", explanation=expl,
                       qtype="data_interpretation", est=85, tags=["data", "scatterplot"], verify=f"y={y} at x={k}", stimulus=fig)


def sp_residual(rng, d):
    """Points above/below the line; residual of a data point."""
    m = rng.choice([v for v in range(-6, 7) if v != 0])
    b = rng.randint(0, 30)
    pts, fig = _scatter(rng, m, b)
    eq = f"y = {_lin(m, b)}"
    above = [p for p in pts if p[1] > m * p[0] + b]
    below = [p for p in pts if p[1] < m * p[0] + b]
    if d == "easy":
        val = len(above)
        prompt = f"The scatterplot shows {len(pts)} data points and the line of best fit {eq}. For how many of the data points is the actual y-value greater than the value predicted by the line?"
        expl = f"A point lies above the line when y > {_lin(m, b)}; that holds for {val} of the points."
        ds = [(len(below), "That counts the points below the line."), (len(pts), "Not every point is above the line."), (len(pts) - len(above) - len(below) + len(above) + 1 if len(pts) - len(below) != val else val + 2, "Count only points strictly above the line."), (val - 1 if val > 0 else val + 1, "Recount the points above the line.")]
        return _numeric_mc(rng, prompt, val, ds, subskill="model_interpret", explanation=expl,
                           qtype="data_interpretation", est=85, tags=["data", "scatterplot", "residual"], verify=f"above={val}", stimulus=fig)
    pt = rng.choice([p for p in pts if p[1] != m * p[0] + b] or pts)
    pred = m * pt[0] + b
    res = pt[1] - pred
    if d == "medium":
        prompt = f"The line of best fit for the scatterplot is {eq}. One data point is ({pt[0]}, {_m(pt[1])}). How much greater or less is the actual y-value than the value predicted by the line at x = {pt[0]}?"
        val = res
        expl = f"Predicted y = {_m(m)}·{pt[0]} {_pm(b)} = {_m(pred)}; actual − predicted = {_m(pt[1])} − ({_m(pred)}) = {_m(res)}."
        ds = [(-res, "Actual minus predicted; the sign is reversed."), (pred, "That is the predicted value, not the difference."), (pt[1], "That is the actual value, not the difference."), (res + m if res + m != 0 else res + 1, "Arithmetic slip computing the prediction.")]
        return _numeric_mc(rng, prompt, val, ds, subskill="model_interpret", explanation=expl,
                           qtype="data_interpretation", est=90, tags=["data", "scatterplot", "residual"], verify=f"res={res}", stimulus=fig)
    prompt = f"The line of best fit for the scatterplot is {eq}. Which of the following statements about the data point ({pt[0]}, {_m(pt[1])}) is true?"
    correct = f"The actual y-value is {abs(res)} {'greater' if res > 0 else 'less'} than the value predicted by the line."
    ds = [(f"The actual y-value is {abs(res)} {'less' if res > 0 else 'greater'} than the value predicted by the line.", f"The line predicts {_m(pred)}; the actual {_m(pt[1])} is {'above' if res > 0 else 'below'} it."),
          (f"The point lies exactly on the line of best fit, so its actual and predicted y-values are equal.", f"The line predicts {_m(pred)}, not {_m(pt[1])}."),
          (f"The value predicted by the line at x = {pt[0]} is {_m(pt[1])}, the same as the actual y-value.", f"{_m(pt[1])} is the actual value; the prediction is {_m(pred)}."),
          (f"The actual y-value is {abs(res) + abs(m)} {'greater' if res > 0 else 'less'} than the predicted value.", "Recompute the prediction with the slope and intercept.")]
    expl = f"Predicted y = {_m(pred)}; actual = {_m(pt[1])}; the difference is {_m(res)}."
    return _text_mc(rng, prompt, correct, ds, subskill="model_interpret", explanation=expl,
                    qtype="data_interpretation", est=95, tags=["data", "scatterplot", "residual"], verify=f"res={res}", stimulus=fig)


def sp_association(rng, d):
    """Direction/strength of association; choose the best-fit equation."""
    m = rng.choice([v for v in range(-6, 7) if v != 0])
    b = rng.randint(0, 30)
    pts, fig = _scatter(rng, m, b)
    if d == "easy":
        xl, yl, _, _ = rng.choice(_SP_CTX)
        fig["figure"]["xlabel"] = xl
        fig["figure"].pop("line", None)
        prompt = f"The scatterplot shows {yl} versus {xl}, with the points trending along y = {_lin(m, b)}. Which statement best describes the association between the variables?"
        correct = ("There is a positive linear association: as x increases, y tends to increase." if m > 0
                   else "There is a negative linear association: as x increases, y tends to decrease.")
        ds = [("There is a negative linear association: as x increases, y tends to decrease." if m > 0
               else "There is a positive linear association: as x increases, y tends to increase.", "The trend goes the other way."),
              ("There is no association between the variables, because the points do not all lie on one line.", "The points follow a clear linear trend."),
              ("The association is nonlinear, because y changes by different amounts between points.", "Small scatter around a line is still a linear association."),
              ("There is a positive association because all y-values are positive." if m < 0 else "There is a negative association because the slope is less than 10.",
               "The direction of association comes from the trend, not the sign or size of the values.")]
        expl = f"The slope of the trend is {_m(m)}, so y tends to {'increase' if m > 0 else 'decrease'} as x increases."
        verify = f"m={m}"
    elif d == "medium":
        prompt = "Which of the following equations best represents the line of best fit shown in the scatterplot?"
        pt = pts[len(pts) // 2]
        prompt = (f"A scatterplot's line of best fit passes near the points ({pts[0][0]}, {_m(m * pts[0][0] + b)}) and "
                  f"({pts[-1][0]}, {_m(m * pts[-1][0] + b)}). Which equation best represents the line?")
        correct = f"y = {_lin(m, b)}"
        ds = [(f"y = {_lin(-m, b)}", "The line {0}, so the slope should be {1}.".format("rises" if m > 0 else "falls", "positive" if m > 0 else "negative")),
              (f"y = {_lin(b, m)}", "The slope and intercept are swapped."),
              (f"y = {_lin(m, b + 10)}", "This intercept is too high for the points given."),
              (f"y = {_lin(2 * m, b)}", "This slope is twice as steep as the data's trend.")]
        expl = f"Slope = ({_m(m * pts[-1][0] + b)} − ({_m(m * pts[0][0] + b)}))/({pts[-1][0]} − {pts[0][0]}) = {_m(m)}; intercept {_m(b)}."
        verify = f"y={m}x+{b}"
    else:
        xl, yl, unit, xunit = rng.choice(_SP_CTX)
        k = max(p[0] for p in pts) + rng.randint(5, 15)
        prompt = (f"The scatterplot shows {yl} versus {xl} for x-values from {pts[0][0]} to {pts[-1][0]}, with line of best fit "
                  f"y = {_lin(m, b)}. A student uses the model to predict y when x = {k}. Which statement best describes this prediction?")
        correct = f"It is an extrapolation beyond the observed data, so it may be unreliable."
        ds = [(f"It is reliable because the model gives an exact value, y = {_m(m * k + b)}, at x = {k}.", "A value from the model is not automatically reliable outside the data's range."),
              ("It cannot be computed because x = {0} does not appear among the data points.".format(k), "The equation can be evaluated at any x; the issue is reliability."),
              (f"It is an interpolation within the range of the observed data, so it is reliable.", f"x = {k} is beyond the largest observed x-value, {pts[-1][0]}."),
              (f"The prediction must be 0 because the trend in the data cannot continue past x = {pts[-1][0]}.", "The model gives a number; it is the trustworthiness that is uncertain.")]
        expl = f"x = {k} lies outside the observed range ({pts[0][0]} to {pts[-1][0]}), so using the model there is extrapolation."
        verify = f"extrapolate x={k}"
    return _text_mc(rng, prompt, correct, ds, subskill="model_interpret", explanation=expl,
                    qtype="data_interpretation", est=85, tags=["data", "scatterplot", "association"], verify=verify, stimulus=fig)


def sp_gridin(rng, d):
    """Grid-in prediction from a line of best fit."""
    m = rng.choice([v for v in range(1, 10)])
    b = rng.randint(0, 40)
    pts, fig = _scatter(rng, m, b)
    if d == "easy":
        k = rng.randint(2, 14)
        prompt = f"The line of best fit for the scatterplot is y = {_lin(m, b)}. What value of y does the model predict when x = {k}?"
        val = m * k + b
        expl = f"{m}·{k} + {b} = {val}."
    elif d == "medium":
        k = rng.randint(2, 14)
        y = m * k + b
        prompt = f"The line of best fit for the scatterplot is y = {_lin(m, b)}. For what value of x does the model predict y = {y}?"
        val = k
        expl = f"{y} − {b} = {m}x → x = {k}."
    else:
        pt = rng.choice([p for p in pts if p[1] > m * p[0] + b] or pts)
        pred = m * pt[0] + b
        prompt = f"The line of best fit for the scatterplot is y = {_lin(m, b)}. One data point is ({pt[0]}, {pt[1]}). By how much does the actual y-value exceed the value predicted by the line?"
        val = max(pt[1] - pred, 0)
        if val == 0:
            return sp_gridin(rng, d)
        expl = f"Predicted {pred}; {pt[1]} − {pred} = {val}."
    return _spr_num(prompt, val, subskill="model_interpret", explanation=expl,
                    tags=["data", "scatterplot", "grid-in"], est=85, verify=f"val={val}", stimulus=fig)


sp_gridin.sat_only = True


# --------------------------------------------------------------------------- #
# Family registry
# --------------------------------------------------------------------------- #
FAMILIES = {
    "word_problems": {
        "easy": [wp_fee_rate, wp_two_numbers, wp_consecutive, wp_expression, wp_rate_time, wp_age_money, wp_gridin],
        "medium": [wp_fee_rate, wp_two_numbers, wp_consecutive, wp_expression, wp_rate_time, wp_age_money, wp_gridin],
        "hard": [wp_fee_rate, wp_two_numbers, wp_consecutive, wp_expression, wp_rate_time, wp_age_money, wp_gridin],
    },
    "absolute_value": {
        "easy": [ab_solve, ab_evaluate, ab_inequality, ab_model, ab_gridin],
        "medium": [ab_solve, ab_evaluate, ab_inequality, ab_model, ab_gridin],
        "hard": [ab_solve, ab_evaluate, ab_inequality, ab_model, ab_gridin],
    },
    "exponential": {
        "easy": [ex_value, ex_model, ex_interpret, ex_periods, ex_gridin],
        "medium": [ex_value, ex_model, ex_interpret, ex_periods, ex_gridin],
        "hard": [ex_value, ex_model, ex_interpret, ex_periods, ex_gridin],
    },
    "two_way_tables": {
        "easy": [tw_probability, tw_count, tw_fraction_percent, tw_compare, tw_gridin],
        "medium": [tw_probability, tw_count, tw_fraction_percent, tw_compare, tw_gridin],
        "hard": [tw_probability, tw_count, tw_fraction_percent, tw_compare, tw_gridin],
    },
    "scatterplots": {
        "easy": [sp_interpret, sp_predict, sp_residual, sp_association, sp_gridin],
        "medium": [sp_interpret, sp_predict, sp_residual, sp_association, sp_gridin],
        "hard": [sp_interpret, sp_predict, sp_residual, sp_association, sp_gridin],
    },
}

# Legacy entry points used by the current orchestrator.
word_problems = _dispatch(FAMILIES, "word_problems")
absolute_value = _dispatch(FAMILIES, "absolute_value")
exponential_growth = _dispatch(FAMILIES, "exponential")
two_way_tables = _dispatch(FAMILIES, "two_way_tables")
line_of_best_fit = _dispatch(FAMILIES, "scatterplots")


# =========================================================================== #
# Bank-growth families (v2.1)
# =========================================================================== #
# ---- word_problems ---------------------------------------------------------- #
def wp_interest(rng, d):
    """Simple interest I = Prt: find interest, rate, or compare accounts."""
    P = rng.randint(5, 80) * 100
    r = rng.choice([2, 3, 4, 5, 6, 8])
    t = rng.randint(1, 6)
    I = P * r * t // 100
    name = rng.choice(NAMES)
    if d == "easy":
        prompt = f"{name} deposits ${P} in an account that earns {r}% simple interest per year. How much interest, in dollars, is earned after {t} years?"
        val = I
        expl = f"I = Prt = {P} × {r}/100 × {t} = {I}."
        ds = [(P * r // 100, "That is one year's interest; multiply by {0} years.".format(t)), (P + I, "That is the total balance, not the interest."), (P * r * t, "Divide by 100 when using a percent."), (I + P * r // 100, "Arithmetic slip.")]
    elif d == "medium":
        prompt = f"{name} invested ${P} at a simple annual interest rate and earned ${I} in interest over {t} years. What was the annual interest rate, as a percent?"
        val = r
        expl = f"I = Prt → {I} = {P}·r·{t} → r = {I}/({P}·{t}) = {r / 100} = {r}%."
        ds = [(r * t, "Divide by the number of years as well."), (Fraction(I * 100, P) if Fraction(I * 100, P) != r else r + 1, "Divide by t = {0} too.".format(t)), (r + 1, "Arithmetic slip."), (Fraction(r, t), "Multiply, don't divide, by the years when isolating r.")]
        return _numeric_mc(rng, prompt, val, ds, subskill="model_and_solve", explanation=expl, tags=["algebra", "word-problem", "interest"], est=90, fmt=lambda v: f"{num_str(v)}%", verify=f"r={r}%")
    else:
        r2 = rng.choice([v for v in (2, 3, 4, 5, 6, 8) if v != r])
        # same interest: P r t = P2 r2 t -> P2 = P r / r2 ; choose P so integer
        P = r2 * rng.randint(5, 40) * 10
        P2 = P * r // r2
        I = Fraction(P * r * t, 100)  # may be fractional (e.g. 446.4): never truncate it
        I = int(I) if I.denominator == 1 else float(I)
        prompt = (f"{name} earns the same amount of simple interest from two accounts over {t} years. The first holds ${P} at {r}% per year. "
                  f"If the second account earns {r2}% per year, how much, in dollars, is in the second account?")
        val = P2
        expl = f"Interest from the first: {P}·{r / 100}·{t} = {I}. Then P₂·{r2 / 100}·{t} = {I} → P₂ = {P2}."
        ds = [(P, "The rates differ, so the principals must differ."), (P * r2 // r if (P * r2) % r == 0 else P2 + 100, "Divide by the second rate, not multiply by it."), (I, "That is the interest, not the principal."), (P2 + 50, "Arithmetic slip.")]
        return _numeric_mc(rng, prompt, val, ds, subskill="model_and_solve", explanation=expl, qtype="multi_step_math", tags=["algebra", "word-problem", "interest"], est=100, verify=f"P2={P2}")
    return _numeric_mc(rng, prompt, val, ds, subskill="model_and_solve", explanation=expl, tags=["algebra", "word-problem", "interest"], est=80, verify=f"I={I}")


def wp_meeting(rng, d):
    """Two movers: catching up, meeting, or head start."""
    a, b = rng.sample(NAMES, 2)
    if d == "easy":
        r1, r2 = rng.randint(40, 70), rng.randint(40, 70)
        if r1 == r2:
            r2 += 5
        t = rng.randint(2, 6)
        D = (r1 + r2) * t
        prompt = f"{a} and {b} start {D} miles apart and drive toward each other, at {r1} and {r2} miles per hour. After how many hours do they meet?"
        val = t
        expl = f"Closing speed = {r1} + {r2} = {r1 + r2} mph; {D} ÷ {r1 + r2} = {t} hours."
        ds = [(Fraction(D, abs(r1 - r2)), "Toward each other: add the speeds."), (Fraction(D, max(r1, r2)), "Both drivers close the gap."), (t + 1, "Arithmetic slip."), (Fraction(D, r1 + r2) * 2, "Divide by the combined speed once.")]
    elif d == "medium":
        r1 = rng.randint(3, 8)
        r2 = r1 + rng.randint(2, 6)
        head = rng.randint(1, 4)
        t = r1 * head // (r2 - r1) if (r1 * head) % (r2 - r1) == 0 else None
        if t is None or t < 1:
            return wp_meeting(rng, d)
        prompt = f"{a} starts walking at {r1} miles per hour. {head} hour{'s' if head > 1 else ''} later, {b} starts cycling along the same route at {r2} miles per hour. How many hours after {b} starts does {b} catch up to {a}?"
        val = t
        expl = f"{a}'s lead is {r1}·{head} = {r1 * head} miles; the gap closes at {r2} − {r1} = {r2 - r1} mph: {r1 * head}/{r2 - r1} = {t} hours."
        ds = [(t + head, f"That counts from when {a} started, not {b}."), (Fraction(r1 * head, r2 + r1), "Same direction: subtract the speeds."), (head, "That is the head start, not the catch-up time."), (t + 1, "Arithmetic slip.")]
    else:
        r1, r2 = rng.randint(30, 60), rng.randint(30, 60)
        if r1 == r2:
            r2 += 10
        t = rng.randint(2, 5)
        D = (r1 + r2) * t
        prompt = f"Two trains leave stations {D} miles apart at the same time and travel toward each other on parallel tracks at {r1} and {r2} miles per hour. How many miles from the first train's station do they pass each other?"
        val = r1 * t
        expl = f"They meet after {D}/({r1} + {r2}) = {t} hours; the first train has gone {r1}·{t} = {val} miles."
        ds = [(r2 * t, "That is the distance from the second station."), (t, "That is the time, not a distance."), (D // 2, "They meet at the midpoint only if the speeds are equal."), (val + r1, "Arithmetic slip.")]
    return _numeric_mc(rng, prompt, val, ds, subskill="model_and_solve", explanation=expl, qtype="multi_step_math",
                       tags=["algebra", "word-problem", "rate"], est=100, verify=f"val={val}")


# ---- absolute_value ------------------------------------------------------- #
def ab_vertex(rng, d):
    """Vertex / extreme value of y = a|x − h| + k."""
    h = rng.choice([v for v in range(-12, 13) if v])
    k = rng.choice([v for v in range(-15, 16) if v])
    a = 1 if d == "easy" else rng.choice([-3, -2, -1, 2, 3])
    rule = ("" if a == 1 else "−" if a == -1 else _m(a)) + f"|x {_pm(-h)}| {_pm(k)}"
    if d == "easy":
        prompt = f"The function f is defined by f(x) = {rule}. What is the minimum value of f(x)?"
        val = k
        expl = f"|x {_pm(-h)}| is at least 0, with equality at x = {_m(h)}; so the minimum is {_m(k)}."
        ds = [(h, "That is the x-value where the minimum occurs."), (-k, "The constant keeps its sign."), (-h, "x − h = 0 when x = h."), (abs(k) if abs(k) != k else k + 1, "The minimum can be negative.")]
    elif d == "medium":
        which = rng.choice(["x", "value"])
        word = "minimum" if a > 0 else "maximum"
        if which == "x":
            prompt = f"For what value of x does f(x) = {rule} reach its {word} value?"
            val = h
            expl = f"The absolute value is 0 exactly when x {_pm(-h)} = 0, i.e. x = {_m(h)}."
            ds = [(-h, "Set x − h = 0; the sign flips from what is written."), (k, "That is the {0} value, not where it occurs.".format(word)), (-k, "That is the opposite of the {0} value.".format(word)), (h + k, "Don't add the two constants.")]
        else:
            prompt = f"What is the {word} value of f(x) = {rule}?"
            val = k
            expl = f"{_m(a)}|x {_pm(-h)}| is {'at least' if a > 0 else 'at most'} 0, so f(x) is {'at least' if a > 0 else 'at most'} {_m(k)}."
            ds = [(h, "That is where the {0} occurs.".format(word)), (-k, "The constant keeps its sign."), (a * h + k, "Don't multiply a by h."), (a + k, "The {0} is k alone.".format(word))]
    else:
        # f(x) = a|x - h| + k ; find x-intercept count or intercept values
        kk = -a * rng.randint(1, 6)   # k opposite sign to a -> two x-intercepts
        rule = ("" if a == 1 else "−" if a == -1 else _m(a)) + f"|x {_pm(-h)}| {_pm(kk)}"
        w = -kk // a if (-kk) % a == 0 else None
        if w is None:
            return ab_vertex(rng, d)
        x1, x2 = h - w, h + w
        prompt = f"The graph of y = {rule} in the xy-plane crosses the x-axis at two points. What is the sum of the x-coordinates of these points?"
        val = x1 + x2
        expl = f"Set y = 0: |x {_pm(-h)}| = {w}, so x = {_m(x1)} or x = {_m(x2)}; their sum is {_m(val)}."
        ds = [(x2, "That is one intercept, not the sum."), (2 * w, "The intercepts are symmetric about x = {0}, so the sum is 2·{0}.".format(_m(h))), (x2 - x1, "That is the distance between the intercepts."), (-val if val else val + 1, "Sign slip.")]
    return _numeric_mc(rng, prompt, val, ds, subskill="solve_equations", explanation=expl,
                       tags=["algebra", "absolute-value", "graph"], est=80 if d != "hard" else 95, verify=f"h={h},k={k}")


def ab_distance_form(rng, d):
    """Distance between numbers; write an interval as an absolute-value inequality."""
    if d == "easy":
        a, b = rng.randint(-30, 30), rng.randint(-30, 30)
        if a == b:
            b += 7
        prompt = rng.choice([f"On a number line, what is the distance between the points {_m(a)} and {_m(b)}?",
                             f"The temperature changed from {_m(a)}° to {_m(b)}°. By how many degrees did it change (as a positive number)?"])
        val = abs(a - b)
        expl = f"Distance = |{_m(a)} − ({_m(b)})| = |{_m(a - b)}| = {val}."
        ds = [(a - b if a - b != val else b - a, "Distance is never negative; take the absolute value."), (abs(a + b) if abs(a + b) != val else val + 3, "Subtract the coordinates; don't add them."), (abs(a) + abs(b) if abs(a) + abs(b) != val else val + 5, "|a − b| is not |a| + |b| in general."), (val + 1, "Arithmetic slip.")]
        return _numeric_mc(rng, prompt, val, ds, subskill="solve_equations", explanation=expl, tags=["algebra", "absolute-value", "distance"], est=65, verify=f"|{a}-{b}|={val}")
    lo = rng.randint(-20, 20)
    w = rng.choice([2, 4, 6, 8, 10, 12, 14, 16]) if d == "medium" else rng.choice([1, 3, 5, 7, 9, 11, 13])
    hi = lo + w
    mid, rad = Fraction(lo + hi, 2), Fraction(w, 2)
    sym = rng.choice(["≤", "<"])
    prompt = rng.choice([f"Which absolute-value inequality has the solution set {_m(lo)} {sym} x {sym} {_m(hi)}?",
                         f"The acceptable values of x are those with {_m(lo)} {sym} x {sym} {_m(hi)}. Which inequality represents this?"])
    correct = f"|x {_pm(-mid)}| {sym} {num_str(rad)}"
    ds = [(f"|x {_pm(mid)}| {sym} {num_str(rad)}", "The center is {0}, so the expression is x − ({0}).".format(num_str(mid))),
          (f"|x {_pm(-mid)}| {sym} {num_str(2 * rad)}", "The radius is half the width of the interval."),
          (f"|x {_pm(-lo)}| {sym} {num_str(2 * rad)}", "Center the inequality at the midpoint, not the endpoint."),
          (f"|x {_pm(-mid)}| {'≥' if sym == '≤' else '>'} {num_str(rad)}", "This describes values outside the interval.")]
    expl = f"The interval is centered at ({_m(lo)} + {_m(hi)})/2 = {num_str(mid)} with half-width {num_str(rad)}: {correct}."
    return _text_mc(rng, prompt, correct, ds, subskill="solve_equations", explanation=expl, tags=["algebra", "absolute-value", "interval"], est=85, verify=correct)


# ---- exponential ------------------------------------------------------------ #
def ex_compound(rng, d):
    """Compound interest / growth with a formula to evaluate."""
    P = rng.choice([500, 800, 1000, 1200, 1500, 2000, 2500, 3000, 4000, 5000, 6000, 8000, 10000])
    name = rng.choice(NAMES)
    if d == "easy":
        r = rng.choice([2, 3, 4, 5, 6, 8, 10])
        t = rng.choice([1, 2])
        A = P * Fraction(100 + r, 100) ** t
        prompt = f"{name} deposits ${P} in an account that earns {r}% interest, compounded annually. What is the balance, in dollars, after {t} year{'s' if t > 1 else ''}?"
        val = round(float(A), 2)
        expl = f"A = P(1 + r)^t = {P}(1.{r:02d})^{t} = {float(A):.2f}."
        ds = [(round(P * (1 + r / 100 * t), 2), "Compound interest multiplies each year; it doesn't add the same amount." if t > 1 else "Arithmetic slip."), (round(P * r / 100 * t, 2), "That is only the interest earned, not the balance."), (round(P * (1 + r / 100) ** (t + 1), 2), "That is one year too many."), (round(P * (r / 100) ** t, 2), "Multiply by (1 + r), not r.")]
    elif d == "medium":
        r = rng.choice([2, 3, 4, 5, 6, 8, 10, 12])
        t = rng.randint(2, 4)
        prompt = f"An investment of ${P} grows by {r}% per year, compounded annually. Which expression gives the value, in dollars, of the investment after {t} years?"
        correct = f"{P}(1.{r:02d})^{t}"
        ds = [(f"{P}(0.{r:02d})^{t}", "The growth factor is 1 + r, not r."), (f"{P}(1 + {t}·0.{r:02d})", "Compound growth is repeated multiplication, not repeated addition."), (f"{P}·{t}·1.{r:02d}", "The number of years is an exponent."), (f"{P}(1.{r:02d})·{t}", "Raise the factor to the power {0}.".format(t))]
        expl = f"Each year multiplies the value by 1 + {r}/100 = 1.{r:02d}; after {t} years: {correct}."
        return _text_mc(rng, prompt, correct, ds, subskill="growth_decay", explanation=expl, tags=["advanced-math", "exponential", "compound"], est=80, verify=correct)
    else:
        r = rng.choice([4, 6, 8, 12])
        n = rng.choice([2, 4, 12])
        t = rng.randint(1, 3)
        prompt = (f"${P} is invested at an annual rate of {r}%, compounded {'semiannually' if n == 2 else 'quarterly' if n == 4 else 'monthly'}. "
                  f"Which expression gives the value, in dollars, after {t} years?")
        correct = f"{P}(1 + 0.{r:02d}/{n})^({n}·{t})" if t > 1 else f"{P}(1 + 0.{r:02d}/{n})^{n}"
        ds = [(f"{P}(1 + 0.{r:02d})^{t}" if t > 1 else f"{P}(1 + 0.{r:02d})^1", "That compounds once a year; divide the rate by {0} and multiply the exponent by {0}.".format(n)),
              (f"{P}(1 + 0.{r:02d}/{n})^{t}", "The exponent counts compounding periods: {0}·{1}.".format(n, t)),
              (f"{P}(1 + 0.{r:02d}·{n})^({n}·{t})" if t > 1 else f"{P}(1 + 0.{r:02d}·{n})^{n}", "Divide the annual rate by the number of periods; don't multiply."),
              (f"{P}(1 + 0.{r:02d}/{n})·{n}·{t}", "The number of periods is an exponent.")]
        expl = f"A = P(1 + r/n)^(nt) with r = 0.{r:02d}, n = {n}, t = {t}: {correct}."
        return _text_mc(rng, prompt, correct, ds, subskill="growth_decay", explanation=expl, tags=["advanced-math", "exponential", "compound"], est=95, verify=correct)
    return _numeric_mc(rng, prompt, val, ds, subskill="growth_decay", explanation=expl, tags=["advanced-math", "exponential", "compound"], est=85, fmt=lambda v: _money(v), verify=f"A={float(A):.2f}")


def ex_identify_type(rng, d):
    """Identify growth/decay/linear from equations or descriptions (text options)."""
    n0 = rng.choice([50, 100, 200, 250, 400, 500, 800, 1000, 1500])
    if d == "easy":
        want = rng.choice(["exponential growth", "exponential decay"])
        g = rng.choice([1.02, 1.05, 1.1, 1.25, 1.5, 2, 3])
        dc = rng.choice([0.5, 0.75, 0.8, 0.9, 0.95, 0.98])
        m = rng.randint(2, 30)
        exp_g, exp_d = f"f(t) = {n0}({g:g})^t", f"f(t) = {n0}({dc:g})^t"
        lin_g, lin_d = f"f(t) = {n0} + {m}t", f"f(t) = {n0} − {m}t"
        correct = exp_g if want == "exponential growth" else exp_d
        ds = [(exp_d if want == "exponential growth" else exp_g, "A base {0} 1 gives exponential {1}.".format("less than" if want == "exponential growth" else "greater than", "decay" if want == "exponential growth" else "growth")),
              (lin_g, "Adding a fixed amount each period is linear growth."), (lin_d, "Subtracting a fixed amount each period is linear decay."), (f"f(t) = {n0}t^2", "A power of t is not exponential.")]
        prompt = f"Which of the following functions models {want}?"
        expl = f"Exponential functions have t in the exponent; the base {'above' if want == 'exponential growth' else 'below'} 1 gives {want}: {correct}."
    elif d == "medium":
        pct = rng.choice([3, 5, 8, 10, 12, 15, 20, 25])
        up = rng.random() < 0.5
        f = (100 + pct) / 100 if up else (100 - pct) / 100
        desc = rng.choice([f"The number of trees in a forest is {n0} and {'increases' if up else 'decreases'} by {pct}% each year",
                           f"A town's population is {n0} and {'grows' if up else 'shrinks'} by {pct}% per year",
                           f"A machine worth ${n0} {'gains' if up else 'loses'} {pct}% of its value each year"])
        prompt = f"{desc}. Which statement best describes the quantity over time?"
        correct = f"It changes exponentially: it is multiplied by {f:g} each year."
        ds = [(f"It changes linearly: it changes by exactly {n0 * pct // 100} every year.", "A percent change is proportional to the current amount, so the yearly change is not constant."),
              (f"It changes exponentially: it changes by exactly {n0 * pct // 100} every year.", "Exponential change is a constant factor, not a constant amount."),
              (f"It changes linearly: the same percent is applied every year.", "A constant percent is a constant multiplier, which is exponential."),
              (f"It stays essentially constant, because {pct}% is a small change.", "Any nonzero percent change compounds over time.")]
        expl = f"A {pct}% {'increase' if up else 'decrease'} multiplies by {f:g} every year, so the model is exponential."
    else:
        xs = [0, 1, 2, 3]
        kind = rng.choice(["exp", "lin"])
        r = rng.choice([2, 3, 4, Fraction(1, 2)])
        a = rng.choice([4, 8, 16, 32, 64, 5, 10, 20, 40, 80]) if r != Fraction(1, 2) else rng.choice([64, 80, 96, 128, 160, 200, 320])
        m = rng.randint(3, 25)
        ys = [a * r ** x for x in xs] if kind == "exp" else [a + m * x for x in xs]
        shown = ", ".join(num_str(v) for v in ys)
        prompt = f"A quantity is measured at times t = 0, 1, 2, 3 and takes the values {shown}. Which function best models the quantity Q(t)?"
        if kind == "exp":
            correct = f"Q(t) = {a}({num_str(r)})^t"
            ds = [(f"Q(t) = {a} + {num_str(ys[1] - ys[0])}t", "The differences are not constant, so the model is not linear."), (f"Q(t) = {a}({num_str(r)})t", "t belongs in the exponent."), (f"Q(t) = {num_str(ys[1])}({num_str(r)})^t", "Q(0) = {0}, so the coefficient is {0}.".format(a)), (f"Q(t) = {a}({num_str(1 / r)})^t", "The ratio of consecutive values is {0}.".format(num_str(r)))]
            expl = f"Consecutive values have constant ratio {num_str(r)}, so Q(t) = {a}·({num_str(r)})^t."
        else:
            correct = f"Q(t) = {a} + {m}t"
            ds = [(f"Q(t) = {a}({num_str(Fraction(ys[1], ys[0]))})^t", "The ratios are not constant, so the model is not exponential."), (f"Q(t) = {m} + {a}t", "The starting value is {0} and the rate is {1}.".format(a, m)), (f"Q(t) = {a} − {m}t", "The values increase."), (f"Q(t) = {ys[1]} + {m}t", "Q(0) = {0}.".format(a))]
            expl = f"Consecutive values differ by a constant {m}, so Q(t) = {a} + {m}t."
    return _text_mc(rng, prompt, correct, ds, subskill="growth_decay", explanation=expl, tags=["advanced-math", "exponential", "identify"], est=85, verify=correct)


# ---- two_way_tables --------------------------------------------------------- #
def tw_build(rng, d):
    """Reconstruct a two-way table from a description; find a cell / total / probability."""
    rcat = rng.choice([("seniors", "juniors"), ("employees", "managers"), ("cats", "dogs"), ("morning classes", "afternoon classes")])
    yes = rng.choice(["voted yes", "attended the workshop", "were adopted", "were full"])
    a, b, c, e = (rng.randint(5, 60) for _ in range(4))
    total = a + b + c + e
    desc = (f"Of the {total} {rcat[0]} and {rcat[1]} surveyed, {a + b} were {rcat[0]}. {a} of the {rcat[0]} and {c} of the {rcat[1]} {yes}.")
    if d == "easy":
        prompt = f"{desc} How many of the {rcat[1]} did NOT meet the condition ({yes})?"
        val = e
        expl = f"{rcat[1].capitalize()}: {total} − {a + b} = {c + e}; of those, {c} did, so {c + e} − {c} = {e} did not."
        ds = [(b, f"That is the number of {rcat[0]} who did not."), (c, f"That is the number of {rcat[1]} who did."), (c + e, f"That is all the {rcat[1]}."), (e + 1, "Arithmetic slip.")]
    elif d == "medium":
        prompt = f"{desc} If one of the surveyed is chosen at random, what is the probability that it is one of the {rcat[1]} who {yes}?"
        val = Fraction(c, total)
        expl = f"{c} of the {total} fit both conditions: {num_str(val)}."
        ds = [(Fraction(c, c + e), "Divide by the grand total, not the {0} total.".format(rcat[1])), (Fraction(a + c, total), "That counts the {0} who {1} as well.".format(rcat[0], yes)), (Fraction(c, a + c), "That conditions on the condition, not the whole group."), (Fraction(e, total), "That is the probability of a {0} who did not.".format(rcat[1][:-1]))]
    else:
        prompt = f"{desc} Given that a randomly chosen respondent did NOT meet the condition ({yes}), what is the probability that the respondent is one of the {rcat[0]}?"
        val = Fraction(b, b + e)
        expl = f"Those who did not: {b} {rcat[0]} + {e} {rcat[1]} = {b + e}; of them {b} are {rcat[0]}: {num_str(val)}."
        ds = [(Fraction(b, total), "Condition on the 'did not' group, not everyone."), (Fraction(b, a + b), "Condition on the 'did not' group, not on the {0}.".format(rcat[0])), (Fraction(e, b + e), "That is the probability of a {0}.".format(rcat[1][:-1])), (Fraction(a, a + c), "That conditions on those who DID meet the condition.")]
    return _numeric_mc(rng, prompt, val, ds, subskill="conditional_probability", explanation=expl, qtype="multi_step_math",
                       tags=["data", "table", "build"], est=100, verify=f"cells {a},{b},{c},{e}")


def tw_relative_freq(rng, d):
    """Relative-frequency (decimal) two-way tables."""
    rcat, ccat, a, b, c, e, total, _ = _two_way(rng)
    # scale to a 'nice' total
    total = rng.choice([50, 100, 200, 250, 400, 500])
    pa = rng.choice([0.1, 0.12, 0.15, 0.18, 0.2, 0.24, 0.25, 0.3])
    pb = rng.choice([0.1, 0.12, 0.15, 0.2, 0.22, 0.25, 0.3])
    pc = rng.choice([0.1, 0.14, 0.15, 0.2, 0.25])
    pe = round(1 - pa - pb - pc, 2)
    if pe <= 0.04:
        return tw_relative_freq(rng, d)
    # The asked count must be a whole number of responses (0.25 × 250 = 62.5 is
    # not). Proportions are in hundredths, so a multiple of 100 always works
    # (not 100 itself, which would collide with the "times 100" distractor).
    asked = {"easy": pb, "medium": pa + pc}.get(d)
    if asked is not None and round(asked * total, 6) % 1:
        total = {50: 200, 250: 500}[total]
    rows = [[rcat[0], f"{pa:.2f}", f"{pb:.2f}", f"{pa + pb:.2f}"], [rcat[1], f"{pc:.2f}", f"{pe:.2f}", f"{pc + pe:.2f}"], ["Total", f"{pa + pc:.2f}", f"{pb + pe:.2f}", "1.00"]]
    stim = _table(f"Relative frequencies (n = {total})", ["", ccat[0], ccat[1], "Total"], rows)
    if d == "easy":
        prompt = f"The table shows relative frequencies for {total} responses. How many responses were “{rcat[0]}” and “{ccat[1]}”?"
        val = round(pb * total)
        expl = f"{pb:.2f} × {total} = {val}."
        ds = [(round(pa * total), "That is the other cell in the row."), (round((pa + pb) * total), "That is the whole row."), (round(pb * 100), "Multiply by the total {0}, not 100.".format(total)), (round(pe * total), "That is the other cell in the column.")]
    elif d == "medium":
        prompt = f"The table shows relative frequencies for {total} responses. How many responses in total were “{ccat[0]}”?"
        val = round((pa + pc) * total)
        expl = f"Column total {pa + pc:.2f} × {total} = {val}."
        ds = [(round((pa + pb) * total), "That is a row total."), (round(pa * total), "That is one cell only."), (round((pb + pe) * total), "That is the other column."), (round((pa + pc) * 100), "Multiply by {0}.".format(total))]
    else:
        prompt = f"The table shows relative frequencies for {total} responses. Given that a response is “{rcat[1]}”, what is the probability that it is “{ccat[0]}”? (Round to the nearest hundredth.)"
        val = round(pc / (pc + pe), 2)
        expl = f"P({ccat[0]} | {rcat[1]}) = {pc:.2f}/({pc:.2f} + {pe:.2f}) = {val:.2f}."
        ds = [(round(pc, 2), "Divide by the row's relative frequency to condition on it."), (round(pc / (pa + pc), 2), "Condition on the row, not the column."), (round(pe / (pc + pe), 2), "That is the probability of the other column."), (round(val + 0.1, 2), "Arithmetic slip.")]
    return _numeric_mc(rng, prompt, val, ds, subskill="conditional_probability", explanation=expl, qtype="data_interpretation",
                       tags=["data", "table", "relative-frequency"], est=90, stimulus=stim, verify=f"{pa},{pb},{pc},{pe}")


# ---- scatterplots ------------------------------------------------------------ #
def _ols_slope(pts):
    n = len(pts)
    mx = sum(p[0] for p in pts) / n
    my = sum(p[1] for p in pts) / n
    return (sum((p[0] - mx) * (p[1] - my) for p in pts) / sum((p[0] - mx) ** 2 for p in pts))


def sp_outlier_point(rng, d):
    """Which data point is farthest from / closest to the line of best fit (text options)."""
    m = rng.choice([v for v in range(-6, 7) if v])
    b = rng.randint(0, 30)
    xs = sorted(rng.sample(range(1, 14), 5))
    # Distinct residual sizes, so "closest to the line" has one answer (the old
    # draw from ±1, ±2, ... could tie, e.g. residuals −2 and +2).
    res = [mag * rng.choice([-1, 1]) for mag in rng.sample([1, 2, 3, 4, 5, 6], 5)]
    big = rng.choice([8, 9, 10, 11, 12]) * rng.choice([-1, 1])
    i = rng.randrange(5)
    res[i] = big
    pts = [[x, m * x + b + r] for x, r in zip(xs, res)]
    fig = {"type": "figure", "figure": {"kind": "scatter", "caption": "Scatterplot with line of best fit", "points": pts, "line": {"m": m, "b": b}, "xlabel": "x"}}
    eq = f"y = {_lin(m, b)}"
    if d == "easy":
        prompt = f"The scatterplot shows five data points and the line of best fit {eq}. Which data point is farthest from the line?"
        correct = f"({pts[i][0]}, {_m(pts[i][1])})"
        ds = [(f"({p[0]}, {_m(p[1])})", f"Its y-value is {abs(r)} from the line's prediction, less than {abs(big)}.") for p, r in zip(pts, res) if p is not pts[i]]
        expl = f"Compare each point with the line: at x = {pts[i][0]} the line predicts {_m(m * pts[i][0] + b)}, and the point is {abs(big)} away, the largest gap."
    elif d == "medium":
        j = min(range(5), key=lambda k: abs(res[k]))
        prompt = f"The line of best fit for the scatterplot is {eq}. For which data point is the actual y-value closest to the value predicted by the line?"
        correct = f"({pts[j][0]}, {_m(pts[j][1])})"
        ds = [(f"({p[0]}, {_m(p[1])})", f"Its y-value differs from the prediction by {abs(r)}, more than {abs(res[j])}.") for p, r in zip(pts, res) if p is not pts[j]]
        expl = f"At x = {pts[j][0]} the line predicts {_m(m * pts[j][0] + b)}; the point is only {abs(res[j])} away, the smallest gap."
    else:
        prompt = f"The line of best fit for the scatterplot is {eq}. If the point ({pts[i][0]}, {_m(pts[i][1])}) were removed and the line refit, how would the slope most likely change?"
        above = big > 0
        mean_x = sum(xs) / 5
        right = pts[i][0] > mean_x
        # Check against an actual least-squares refit: a point near the mean x
        # barely moves the slope, so redraw those.
        before, after = _ols_slope(pts), _ols_slope([p for p in pts if p is not pts[i]])
        if abs(pts[i][0] - mean_x) < 2 or abs(after - before) < 0.2 or (after < before) != ((above and right) or (not above and not right)):
            return sp_outlier_point(rng, d)
        # outlier above on the right pulls slope up; removing it lowers slope
        if (above and right) or (not above and not right):
            correct = "The slope would decrease."
            why = f"The outlier is {'above' if above else 'below'} the line on the {'right' if right else 'left'}, which tilts the line upward; removing it lowers the slope."
        else:
            correct = "The slope would increase."
            why = f"The outlier is {'above' if above else 'below'} the line on the {'right' if right else 'left'}, which tilts the line downward; removing it raises the slope."
        other = "The slope would increase." if correct.endswith("decrease.") else "The slope would decrease."
        ds = [(other, "Think about which way the outlier pulls the line."), ("The slope would not change, because one point cannot affect the line.", "Every point affects a least-squares line."), ("The slope would become 0.", "The remaining points still show a clear trend."), ("The slope would change sign.", "The other points keep the same direction of association.")]
        expl = why
        return _text_mc(rng, prompt, correct, ds, subskill="model_interpret", explanation=expl, qtype="data_interpretation", tags=["data", "scatterplot", "outlier"], est=95, stimulus=fig, verify=f"outlier ({pts[i][0]},{pts[i][1]})")
    return _text_mc(rng, prompt, correct, ds, subskill="model_interpret", explanation=expl, qtype="data_interpretation", tags=["data", "scatterplot", "residual"], est=85, stimulus=fig, verify=f"res={res}")


def sp_line_from_points(rng, d):
    """Line of best fit passes through two given points -> slope / equation / prediction."""
    m = rng.choice([v for v in range(-8, 9) if v])
    b = rng.randint(0, 40)
    x1 = rng.randint(1, 6)
    x2 = x1 + rng.randint(2, 8)
    y1, y2 = m * x1 + b, m * x2 + b
    pts, fig = _scatter(rng, m, b)
    if d == "easy":
        prompt = f"The line of best fit for the scatterplot passes through the points ({x1}, {_m(y1)}) and ({x2}, {_m(y2)}). What is the slope of the line?"
        val = m
        expl = f"Slope = ({_m(y2)} − ({_m(y1)}))/({x2} − {x1}) = {_m(y2 - y1)}/{x2 - x1} = {_m(m)}."
        ds = [(Fraction(x2 - x1, y2 - y1) if y2 != y1 else m + 1, "Rise over run, not run over rise."), (-m, "Sign slip."), (y2 - y1, "Divide by the change in x."), (Fraction(y2, x2), "Use the change between the two points.")]
        return _numeric_mc(rng, prompt, val, ds, subskill="model_interpret", explanation=expl, qtype="data_interpretation", tags=["data", "scatterplot", "slope"], est=80, stimulus=fig, verify=f"m={m}")
    if d == "medium":
        prompt = f"The line of best fit for the scatterplot passes through ({x1}, {_m(y1)}) and ({x2}, {_m(y2)}). Which equation represents the line?"
        correct = f"y = {_lin(m, b)}"
        ds = [(f"y = {_lin(-m, b)}", "Check the sign of the slope."), (f"y = {_lin(m, y1)}", f"{_m(y1)} is y at x = {x1}, not at x = 0."), (f"y = {_lin(b, m)}" if b != m else f"y = {_lin(m, b + 5)}", "The slope and intercept are swapped." if b != m else "Recheck the intercept."), (f"y = {_lin(y2 - y1, b)}" if y2 - y1 != m else f"y = {_lin(m, b - 3)}", "Divide the change in y by the change in x.")]
        expl = f"Slope {_m(m)}; then {_m(y1)} = {_m(m)}·{x1} + b gives b = {_m(b)}: {correct}."
        return _text_mc(rng, prompt, correct, ds, subskill="model_interpret", explanation=expl, qtype="data_interpretation", tags=["data", "scatterplot", "equation"], est=90, stimulus=fig, verify=f"y={m}x+{b}")
    k = x2 + rng.randint(3, 10)
    prompt = f"The line of best fit for the scatterplot passes through ({x1}, {_m(y1)}) and ({x2}, {_m(y2)}). Based on the line, what value of y is predicted when x = {k}?"
    val = m * k + b
    expl = f"Slope {_m(m)} and intercept {_m(b)} give y = {_lin(m, b)}; at x = {k}, y = {_m(val)}."
    ds = [(m * k, "Include the intercept."), (y2 + (k - x2), "Each unit of x changes y by {0}, not 1.".format(_m(m))), (-m * k + b, "Sign slip on the slope."), (val + m, "Arithmetic slip.")]
    return _numeric_mc(rng, prompt, val, ds, subskill="model_interpret", explanation=expl, qtype="data_interpretation", tags=["data", "scatterplot", "predict"], est=95, qtype_override=None) if False else \
        _numeric_mc(rng, prompt, val, ds, subskill="model_interpret", explanation=expl, qtype="multi_step_math", tags=["data", "scatterplot", "predict"], est=95, stimulus=fig, verify=f"y={val}")


_NEW_EXTRA = {
    "word_problems": [wp_interest, wp_meeting],
    "absolute_value": [ab_vertex, ab_distance_form],
    "exponential": [ex_compound, ex_identify_type],
    "two_way_tables": [tw_build, tw_relative_freq],
    "scatterplots": [sp_outlier_point, sp_line_from_points],
}
for _skill, _fns in _NEW_EXTRA.items():
    for _d in ("easy", "medium", "hard"):
        FAMILIES[_skill][_d].extend(_fns)
