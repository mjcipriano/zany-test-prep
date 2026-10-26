"""ACT-only Math skills: number properties, coordinate geometry, angles and
polygons, sequences, logarithms and complex numbers.

Same ``FAMILIES`` contract as math_gen.py. The ACT has no grid-ins, so every
family here is multiple choice; supply 4 distractors so items work with
``util.OPTION_COUNT`` = 5 (ACT) as well as 4.

Subskill ids used by each skill (the exam plan lists them in skills.yaml):
"""
from __future__ import annotations

import math
import random
from fractions import Fraction

from .math_gen import (_numeric_mc, _text_mc, _lin, _m, _pm, _ordinal, _dispatch,
                       _pyth_triple, _table, _poly_str, NAMES)
from .util import num_str

SUBSKILLS = {
    "number_properties": ["factors_multiples", "primes", "integer_reasoning",
                          "order_of_operations", "scientific_notation", "fraction_decimal_percent"],
    "coordinate_geometry": ["distance_midpoint", "circle_equation", "parallel_perpendicular", "points_on_lines"],
    "angles_polygons": ["parallel_lines", "triangle_angles", "polygon_angles"],
    "sequences": ["arithmetic", "geometric", "series", "recursive"],
    "logarithms": ["evaluate", "convert_forms", "properties", "solve_exponential"],
    "complex_numbers": ["powers_of_i", "arithmetic", "conjugate_modulus"],
}

_PRIMES = [2, 3, 5, 7, 11, 13, 17, 19, 23, 29, 31, 37, 41, 43, 47]


def _distinct(correct, ds, k=3):
    """True when ``ds`` holds at least ``k`` distractor texts different from ``correct``."""
    return len({str(t) for t, _ in ds if str(t) != str(correct)}) >= k


def _factors(n):
    return [k for k in range(1, n + 1) if n % k == 0]


def _prime_factors(n):
    out, p = [], 2
    while p * p <= n:
        while n % p == 0:
            out.append(p)
            n //= p
        p += 1
    if n > 1:
        out.append(n)
    return out


# --------------------------------------------------------------------------- #
# number_properties
# --------------------------------------------------------------------------- #
def np_gcf_lcm(rng, d):
    """GCF / LCM (easy numeric, medium word, hard with three numbers)."""
    if d == "easy":
        g = rng.choice([2, 3, 4, 5, 6, 7, 8, 9, 10, 12])
        p, q = rng.sample([2, 3, 4, 5, 7, 9, 11], 2)
        while math.gcd(p, q) != 1:
            p, q = rng.sample([2, 3, 4, 5, 7, 9, 11], 2)
        a, b = g * p, g * q
        which = rng.choice(["GCF", "LCM"])
        val = g if which == "GCF" else g * p * q
        name = "greatest common factor" if which == "GCF" else "least common multiple"
        prompt = f"What is the {name} of {a} and {b}?"
        expl = (f"{a} = {g}·{p} and {b} = {g}·{q}; the {name} is {val}.")
        ds = [(g * p * q if which == "GCF" else g, f"That is the {'LCM' if which == 'GCF' else 'GCF'}, not the {which}."),
              (a * b, "The product is a common multiple but not the least one." if which == "LCM" else "The product is not a factor."),
              (min(a, b), "The smaller number is not a factor of the larger here." if which == "GCF" else "The smaller number is not a multiple of the larger."),
              (val + g if which == "GCF" else val // 2 if val % 2 == 0 else val + g, "Recheck by listing factors/multiples.")]
        sub = "factors_multiples"
    elif d == "medium":
        p, q = rng.sample([2, 3, 4, 5, 6, 8, 9, 10, 12, 15], 2)
        l = p * q // math.gcd(p, q)
        ctx = rng.choice([("Two buses leave a station at the same time. One returns every {p} minutes and the other every {q} minutes. After how many minutes will they next leave together?", "minutes"),
                          ("A red light blinks every {p} seconds and a blue light every {q} seconds. If they blink together now, in how many seconds will they next blink together?", "seconds"),
                          ("Hot dogs come in packs of {p} and buns in packs of {q}. What is the least number of hot dogs you can buy so that hot dogs and buns match exactly?", "")])
        prompt = ctx[0].format(p=p, q=q)
        val = l
        expl = f"The least common multiple of {p} and {q} is {l}."
        ds = [(p * q if p * q != l else l * 2, "The product is a common multiple, but not necessarily the least."),
              (math.gcd(p, q), "That is the greatest common factor; the question needs a common multiple."),
              (p + q, "Adding the two periods doesn't give a common multiple."),
              (l + max(p, q), "Recheck: list multiples of {0} and find the first multiple of {1}.".format(max(p, q), min(p, q)))]
        sub = "factors_multiples"
    else:
        g = rng.choice([2, 3, 4, 6, 8, 12])
        a, b, c = sorted(rng.sample([g * k for k in (2, 3, 5, 7, 9, 11, 4)], 3))
        which = rng.choice(["GCF", "LCM"])
        if which == "GCF":
            val = math.gcd(math.gcd(a, b), c)
            prompt = f"What is the greatest common factor of {a}, {b}, and {c}?"
            expl = f"Prime-factor each: the common factors give {val}."
            ds = [(math.gcd(a, b) if math.gcd(a, b) != val else val * 2, "All three numbers must share the factor."),
                  (a * b * c // (math.lcm(a, b, c)) if a * b * c // math.lcm(a, b, c) not in (val,) else val + 1, "Recheck the common prime factors."),
                  (math.lcm(a, b, c), "That is the least common multiple."),
                  (min(a, b, c), "The smallest number is not a factor of the others.")]
        else:
            val = math.lcm(a, b, c)
            prompt = f"What is the least common multiple of {a}, {b}, and {c}?"
            expl = f"Take the highest power of each prime appearing in {a}, {b}, {c}: LCM = {val}."
            ds = [(a * b * c, "The product is a common multiple but far from the least."),
                  (math.lcm(a, b) if math.lcm(a, b) != val else val * 2, "All three numbers must divide the result."),
                  (math.gcd(a, b, c), "That is the greatest common factor."),
                  (max(a, b, c), "The largest number is not a multiple of the others.")]
        sub = "factors_multiples"
    return _numeric_mc(rng, prompt, val, ds, subskill=sub, explanation=expl,
                       tags=["number", "gcf-lcm"], est=70 if d == "easy" else 85, verify=f"val={val}")


def np_primes_factors(rng, d):
    """Prime factorization, counting factors, largest prime factor."""
    if d == "easy":
        n = rng.choice([v for v in range(10, 100) if len(_prime_factors(v)) >= 2 and v not in _PRIMES])
        pf = _prime_factors(n)
        if rng.random() < 0.5:
            prompt = f"What is the largest prime factor of {n}?"
            val = max(pf)
            expl = f"{n} = {' × '.join(map(str, pf))}; the largest prime factor is {val}."
            ds = [(max(_factors(n)[:-1]), "That is the largest factor, but it is not prime." if max(_factors(n)[:-1]) not in _PRIMES else "Recheck."),
                  (min(pf), "That is the smallest prime factor."),
                  (n, "{0} itself is not prime.".format(n)),
                  (max(pf) + (2 if max(pf) + 2 not in pf else 4), "Recheck the factorization.")]
        else:
            prompt = f"Which of the following is the prime factorization of {n}?"
            correct = " × ".join(map(str, pf))
            f2 = [k for k in _factors(n) if 1 < k < n]
            alt = f"{f2[0]} × {n // f2[0]}"
            ds = [(alt, "{0} and {1} are factors, but they are not both prime.".format(f2[0], n // f2[0])),
                  (" × ".join(map(str, pf[:-1] + [pf[-1] + 1])) if pf[-1] + 1 not in (1,) else "2 × " + correct, "This product does not equal {0}.".format(n)),
                  (" × ".join(map(str, pf[1:])) if len(pf) > 2 else f"{pf[0]} × {n}", "This product does not equal {0}.".format(n)),
                  (f"1 × {n}", "1 is not prime and {0} is not prime.".format(n))]
            return _text_mc(rng, prompt, correct, ds, subskill="primes", explanation=f"{n} = {correct}.",
                            tags=["number", "primes"], est=70, verify=correct)
        sub = "primes"
    elif d == "medium":
        n = rng.choice([v for v in range(12, 200) if len(_factors(v)) >= 6])
        val = len(_factors(n))
        prompt = rng.choice([f"How many positive integers are factors of {n}?",
                             f"How many positive divisors does {n} have?"])
        expl = f"The factors of {n} are {', '.join(map(str, _factors(n)))}: {val} in all."
        ds = [(val - 1, "Don't forget 1 or {0} itself.".format(n)), (val - 2, "Both 1 and {0} count as factors.".format(n)),
              (len(set(_prime_factors(n))), "That counts only the distinct prime factors."), (val + 1, "Recheck by pairing factors.")]
        sub = "factors_multiples"
    else:
        p, q = rng.sample(_PRIMES[:6], 2)
        a, b = rng.randint(1, 3), rng.randint(1, 3)
        n = p ** a * q ** b
        val = (a + 1) * (b + 1)
        prompt = f"If n = {p}^{a} · {q}^{b}, how many positive factors does n have?"
        expl = f"Each factor is {p}^i·{q}^j with 0 ≤ i ≤ {a} and 0 ≤ j ≤ {b}: ({a} + 1)({b} + 1) = {val}."
        ds = [(a * b, "Count the exponent choices from 0 to each exponent (add 1 to each)."), (a + b, "Multiply the (exponent + 1) counts; don't add."),
              (val - 1, "1 is a factor too."), (2 * (a + b), "Use (a + 1)(b + 1).")]
        sub = "primes"
    return _numeric_mc(rng, prompt, val, ds, subskill=sub, explanation=expl,
                       tags=["number", "factors"], est=75 if d != "hard" else 90, verify=f"val={val}")


def np_parity(rng, d):
    """Even/odd and integer reasoning (text options)."""
    if d == "easy":
        prompt = "If n is an even integer, which of the following must be odd?"
        k = rng.choice([1, 3, 5, 7, 9])
        correct = rng.choice([f"n + {k}", f"{rng.choice([3, 5, 7])}n + {k}", f"n² + {k}"])
        ds = [(f"n + {k + 1}", "Even plus even is even."), (f"{rng.choice([2, 4, 6])}n", "An even multiple is even."),
              (f"n² + {k + 1}", "Even squared is even; plus an even stays even."), ("n/2 + n", "n/2 may be even or odd; n/2 + n is not always odd.")]
        expl = f"An even number plus an odd number is odd, so {correct} is always odd."
    elif d == "medium":
        a, b = rng.randint(2, 9), rng.randint(2, 9)
        prompt = f"If x and y are integers and {a}x + {b}y is odd, which of the following must be true?"
        if a % 2 == 0 and b % 2 == 0:
            return np_parity(rng, d)
        if a % 2 == 0:
            correct = "y is odd"
            ds = [("x is odd", f"{a}x is even for any integer x."), ("x is even", "x may be either; only y is constrained."),
                  ("y is even", f"If y were even, {a}x + {b}y would be even."), ("x and y are both odd", "x is unrestricted.")]
            expl = f"{a}x is always even, so the sum is odd only when {b}y is odd, i.e. y is odd."
        elif b % 2 == 0:
            correct = "x is odd"
            ds = [("y is odd", f"{b}y is even for any integer y."), ("y is even", "y may be either; only x is constrained."),
                  ("x is even", f"If x were even, {a}x + {b}y would be even."), ("x and y are both odd", "y is unrestricted.")]
            expl = f"{b}y is always even, so the sum is odd only when {a}x is odd, i.e. x is odd."
        else:
            correct = "exactly one of x and y is odd"
            ds = [("x and y are both odd", "Odd + odd is even."), ("x and y are both even", "Even + even is even."),
                  ("x is odd", "x could be even if y is odd."), ("y is odd", "y could be even if x is odd.")]
            expl = f"{a}x has the parity of x and {b}y has the parity of y; the sum is odd exactly when one of them is odd."
    else:
        prompt = rng.choice(["If n is an integer, which of the following is always divisible by 3?",
                             "If n is a positive integer, which of the following must be an even integer?",
                             "If n is an integer, which of the following is always divisible by 4?"])
        if "by 4" in prompt:
            correct = rng.choice(["4n² + 8n", "n(n + 1)(n + 2)(n + 3)", "(2n)(2n + 2)"])
            ds = [("n(n + 1)(n + 2)", "For n = 1 this is 6, not a multiple of 4."), ("(2n + 1)(2n + 3)", "This is a product of odd numbers, so it is odd."),
                  ("n² + 4n + 4", "For n = 1 this is 9."), ("2n(n + 2)", "For n = 1 this is 6, not a multiple of 4.")]
            expl = f"{correct} always contains a factor of 4 (a multiple of 4 or two even factors)."
        elif "3" in prompt:
            correct = rng.choice(["n(n + 1)(n + 2)", "n³ − n", "(n − 1)n(n + 1)"])
            ds = [("n(n + 1)(n + 3)", "For n = 1 this is 8, not a multiple of 3."), ("(n + 1)(n + 2)", "For n = 3 this is 20."),
                  ("3n² + 3n + 1", "This leaves remainder 1 when divided by 3."), ("n² + n + 1", "For n = 1 this is 3, but for n = 2 it is 7.")]
            expl = f"Among any three consecutive integers one is a multiple of 3, so {correct} is divisible by 3."
        else:
            correct = rng.choice(["n(n + 1)", "n² + n", "n² − n"])
            ds = [("n² + n + 1", "n² + n is even, so this is always odd."), ("(n + 1)(n + 3)", "For even n this is a product of two odd numbers."),
                  ("n³ + 2n", "For odd n this is odd."), ("n(n + 2)", "For odd n this is a product of two odd numbers.")]
            expl = f"{correct} is the product of two consecutive integers, one of which is even."
    return _text_mc(rng, prompt, correct, ds, subskill="integer_reasoning", explanation=expl,
                    tags=["number", "parity"], est=80, verify=correct)


np_parity.small_space = True


def np_order_ops(rng, d):
    """Order of operations / integer arithmetic."""
    if d == "easy":
        a, b, c = rng.randint(2, 9), rng.randint(2, 9), rng.randint(2, 9)
        e = rng.randint(1, 12)
        val = a + b * c - e
        prompt = f"What is the value of {a} + {b} × {c} − {e}?"
        expl = f"Multiply first: {b} × {c} = {b * c}; then {a} + {b * c} − {e} = {val}."
        ds = [((a + b) * c - e, "Multiplication comes before addition."), (a + b * (c - e), "Subtraction comes after multiplication."),
              (val + e, "Don't drop the subtraction."), ((a + b) * (c - e), "Follow the order of operations, not left to right.")]
    elif d == "medium":
        a, b, c, e = rng.randint(2, 9), rng.randint(2, 6), rng.randint(1, 9), rng.randint(2, 5)
        val = a * (b + c) ** 2 // 1 - e ** 2 if False else a * (b + c) - e ** 2
        prompt = f"What is the value of {a}({b} + {c}) − {e}²?"
        expl = f"Parentheses: {b} + {c} = {b + c}; exponent: {e}² = {e * e}; then {a}·{b + c} − {e * e} = {_m(val)}."
        ds = [(a * b + c - e * e, "Distribute {0} to both terms inside the parentheses.".format(a)), (a * (b + c) - 2 * e, "{0}² means {0}·{0}, not 2·{0}.".format(e)),
              (a * (b + c - e) ** 2 if a * (b + c - e) ** 2 != val else val + 7, "The square applies only to {0}.".format(e)), (a * (b + c) + e * e, "Subtract the square.")]
    else:
        a, b, c = rng.randint(2, 8), rng.randint(2, 6), rng.randint(2, 9)
        e = rng.choice([2, 3])
        val = Fraction((-a) ** 2 * b - c * e, a) if ((-a) ** 2 * b - c * e) % a == 0 else Fraction((-a) ** 2 * b - c * e, a)
        num = (-a) ** 2 * b - c * e
        prompt = f"What is the value of ((−{a})² · {b} − {c} · {e}) ÷ {a}?"
        expl = f"(−{a})² = {a * a}; {a * a}·{b} = {a * a * b}; {c}·{e} = {c * e}; ({a * a * b} − {c * e}) ÷ {a} = {num_str(val)}."
        ds = [(Fraction(-(a * a) * b - c * e, a), "(−{0})² is positive.".format(a)), (Fraction(a * a * b, a) - c * e, "The whole numerator is divided by {0}.".format(a)),
              (Fraction(a * 2 * b - c * e, a), "(−{0})² is {0}·{0}, not 2·{0}.".format(a)), (Fraction(num, a) + 1, "Arithmetic slip.")]
    return _numeric_mc(rng, prompt, val, ds, subskill="order_of_operations", explanation=expl,
                       tags=["number", "order-of-operations"], est=65 if d == "easy" else 80, verify=f"val={num_str(val)}")


def np_scientific(rng, d):
    """Scientific notation: convert (easy), multiply/divide (medium), compare/word (hard)."""
    if d == "easy":
        mant = rng.choice([1.2, 2.5, 3.4, 4.1, 5.6, 6.3, 7.8, 8.2, 9.5, 1.05, 2.75, 4.02, 6.5, 3.9])
        e = rng.choice([-5, -4, -3, -2, 3, 4, 5, 6, 7])
        if rng.random() < 0.5:
            val_num = mant * 10 ** e
            shown = f"{val_num:.10f}".rstrip("0").rstrip(".") if e < 0 else str(int(round(val_num)))
            prompt = f"Which of the following expresses {shown} in scientific notation?"
            correct = f"{mant:g} × 10^{e}"
            ds = [(f"{mant:g} × 10^{-e}", "The sign of the exponent is reversed."), (f"{mant:g} × 10^{e + 1}", "Count the places the decimal moves."),
                  (f"{mant:g} × 10^{e - 1}", "Count the places the decimal moves."), (f"{mant * 10:g} × 10^{e - 1}", "The coefficient must be at least 1 and less than 10.")]
            expl = f"Move the decimal so the coefficient is between 1 and 10: {correct}."
        else:
            val_num = mant * 10 ** e
            correct = f"{val_num:.10f}".rstrip("0").rstrip(".") if e < 0 else str(int(round(val_num)))
            prompt = f"What is {mant:g} × 10^{e} written in standard decimal form?"
            w1 = f"{mant * 10 ** (-e):.10f}".rstrip("0").rstrip(".") if e > 0 else str(int(round(mant * 10 ** (-e))))
            w2 = f"{mant * 10 ** (e + 1):.10f}".rstrip("0").rstrip(".") if e + 1 < 0 else str(int(round(mant * 10 ** (e + 1))))
            w3 = f"{mant * 10 ** (e - 1):.10f}".rstrip("0").rstrip(".") if e - 1 < 0 else str(int(round(mant * 10 ** (e - 1))))
            ds = [(w1, "A {0} exponent moves the decimal to the {1}.".format("negative" if e < 0 else "positive", "left" if e < 0 else "right")),
                  (w2, "Move the decimal exactly {0} places.".format(abs(e))), (w3, "Move the decimal exactly {0} places.".format(abs(e))),
                  (f"{mant:g}{abs(e)}" if e > 0 else f"0.{abs(e)}{mant:g}".replace(".", "", 1) if False else f"{mant:g}0" , "The exponent moves the decimal; it isn't appended.")]
            expl = f"10^{e} moves the decimal {abs(e)} places to the {'right' if e > 0 else 'left'}: {correct}."
        return _text_mc(rng, prompt, correct, ds, subskill="scientific_notation", explanation=expl,
                        tags=["number", "scientific-notation"], est=70, verify=correct)
    if d == "medium":
        m1, m2 = rng.choice([2, 3, 4, 1.5, 2.5, 5, 6]), rng.choice([2, 3, 4, 1.5, 2.5, 5, 6])
        e1, e2 = rng.randint(2, 8), rng.randint(-4, 6)
        op = rng.choice(["×", "÷"])
        if op == "×":
            m, e = m1 * m2, e1 + e2
        else:
            m, e = m1 / m2, e1 - e2
        while m >= 10:
            m, e = m / 10, e + 1
        while m < 1:
            m, e = m * 10, e - 1
        m = round(m, 4)
        prompt = f"What is ({m1:g} × 10^{e1}) {op} ({m2:g} × 10^{e2}) in scientific notation?"
        correct = f"{m:g} × 10^{e}"
        raw_m = m1 * m2 if op == "×" else m1 / m2
        ds = [(f"{m:g} × 10^{e1 * e2 if op == '×' else (e1 // e2 if e2 and e1 % e2 == 0 else e1 + e2)}", "{0} the exponents when you {1} powers of 10.".format("Add" if op == "×" else "Subtract", "multiply" if op == "×" else "divide")),
              (f"{raw_m:g} × 10^{e1 + e2 if op == '×' else e1 - e2}" if raw_m != m else f"{m:g} × 10^{e + 2}", "The coefficient must be between 1 and 10; adjust the exponent."),
              (f"{m:g} × 10^{e - 1 if raw_m != m else e + 1}", "Recheck the exponent adjustment."),
              (f"{m:g} × 10^{-e}" if e != 0 else f"{m:g} × 10^1", "Check the sign of the exponent.")]
        expl = f"Coefficients: {m1:g} {op} {m2:g} = {raw_m:g}; exponents: {e1} {'+' if op == '×' else '−'} {e2} = {e1 + e2 if op == '×' else e1 - e2}. Normalize: {correct}."
        if e == 0 or not _distinct(correct, ds):
            return np_scientific(rng, d)
        return _text_mc(rng, prompt, correct, ds, subskill="scientific_notation", explanation=expl,
                        tags=["number", "scientific-notation"], est=85, verify=correct)
    m1 = rng.choice([1.2, 2.4, 3.6, 4.8, 6, 7.2, 8.4, 9.6, 1.5, 3, 4.5, 2.1])
    e1 = rng.randint(6, 12)
    n = rng.choice([2, 3, 4, 5, 6, 8, 12])
    val_m = m1 / n
    e = e1
    while val_m < 1:
        val_m, e = val_m * 10, e - 1
    val_m = round(val_m, 4)
    ctx = rng.choice([("A country produces {m1} × 10^{e1} kilograms of grain per year. If this is shared equally among {n} regions, how many kilograms does each region get?", "kilograms"),
                      ("A data center stores {m1} × 10^{e1} bytes. If the storage is split evenly across {n} servers, how many bytes does each server hold?", "bytes"),
                      ("A star is {m1} × 10^{e1} kilometers away. A probe travels this distance in {n} equal stages. How long, in kilometers, is each stage?", "kilometers")])
    prompt = ctx[0].format(m1=f"{m1:g}", e1=e1, n=n) + " (Express the answer in scientific notation.)"
    correct = f"{val_m:g} × 10^{e}"
    ds = [(f"{m1 / n:g} × 10^{e1}" if m1 / n < 1 else f"{val_m:g} × 10^{e + 1}", "Normalize so the coefficient is at least 1."),
          (f"{m1:g} × 10^{e1 - n}", "Dividing by {0} doesn't subtract {0} from the exponent.".format(n)),
          (f"{val_m:g} × 10^{e + 1}" if m1 / n < 1 else f"{val_m:g} × 10^{e - 1}", "Recheck the exponent after normalizing."),
          (f"{m1 * n:g} × 10^{e1}" if m1 * n < 10 else f"{m1 * n / 10:g} × 10^{e1 + 1}", "Divide the coefficient; don't multiply.")]
    expl = f"{m1:g} ÷ {n} = {m1 / n:g}; rewrite with a coefficient between 1 and 10: {correct}."
    return _text_mc(rng, prompt, correct, ds, subskill="scientific_notation", explanation=expl,
                    tags=["number", "scientific-notation"], est=90, verify=correct)


def np_fdp(rng, d):
    """Fraction / decimal / percent conversions and comparisons."""
    if d == "easy":
        n, dn = rng.choice([(1, 2), (1, 4), (3, 4), (1, 5), (2, 5), (3, 5), (4, 5), (1, 8), (3, 8), (5, 8), (7, 8), (1, 10), (3, 10), (7, 10), (9, 10), (1, 20), (3, 20), (7, 20), (9, 20), (1, 25), (3, 25), (11, 25), (13, 50), (1, 50),
                            (11, 20), (13, 20), (17, 20), (19, 20), (2, 25), (4, 25), (6, 25), (7, 25), (8, 25), (9, 25), (12, 25), (14, 25), (16, 25), (18, 25), (21, 25), (3, 50), (7, 50), (9, 50), (11, 50), (17, 50), (19, 50), (21, 50), (23, 50), (1, 16), (3, 16), (5, 16), (7, 16), (9, 16), (11, 16), (1, 40), (3, 40), (7, 40), (9, 40)])
        f = Fraction(n, dn)
        mode = rng.choice(["f2d", "f2p", "d2f", "p2f"])
        dec = float(f)
        pct = round(dec * 100, 2)
        if mode == "f2d":
            prompt = f"What is {n}/{dn} written as a decimal?"
            val = dec
            ds = [(round(dn / n, 3) if dn / n < 100 else dec * 10, "Divide the numerator by the denominator, not the reverse."), (round(dec * 10, 3), "Check the decimal place."), (round(dec / 10, 4), "Check the decimal place."), (round(dec + 0.05, 3), "Arithmetic slip.")]
            expl = f"{n} ÷ {dn} = {num_str(dec)}."
            return _numeric_mc(rng, prompt, val, ds, subskill="fraction_decimal_percent", explanation=expl, tags=["number", "fdp"], est=60, verify=f"{n}/{dn}={dec}")
        if mode == "f2p":
            prompt = f"What is {n}/{dn} written as a percent?"
            val = pct
            ds = [(round(dec, 3), "Multiply the decimal by 100 to get a percent."), (round(pct / 10, 2), "Check the decimal place."), (round(pct * 10, 2) if pct * 10 <= 1000 else pct + 10, "Check the decimal place."), (round(100 * dn / n, 1) if dn / n < 10 else pct + 5, "Divide the numerator by the denominator.")]
            expl = f"{n}/{dn} = {num_str(dec)} = {num_str(pct)}%."
            return _numeric_mc(rng, prompt, val, ds, subskill="fraction_decimal_percent", explanation=expl, tags=["number", "fdp"], fmt=lambda v: f"{num_str(v)}%", est=60, verify=f"{n}/{dn}={pct}%")
        if mode == "d2f":
            prompt = f"Which fraction is equal to {num_str(dec)}?"
            correct = f"{n}/{dn}"
            ds = [(f"{dn}/{n}" if dn != n else f"{n + 1}/{dn}", "This is the reciprocal."), (f"{n}/{dn * 10}", "Check the place value of the last digit."), (f"{n + 1}/{dn}", "This fraction has a different value."), (f"{n}/{dn + 1 if dn + 1 != 2 * n else dn + 2}", "This fraction has a different value.")]
            places = len(num_str(dec).split(".")[1]) if "." in num_str(dec) else 0
            expl = (f"{num_str(dec)} = {int(round(dec * 10 ** places))}/{10 ** places} = {correct} in lowest terms."
                    if places else f"{num_str(dec)} = {correct}.")  # 0.625 is 625/1000, not 62/100
        else:
            prompt = f"Which fraction is equal to {num_str(pct)}%?"
            correct = f"{n}/{dn}"
            ds = [(f"{dn}/{n}" if dn != n else f"{n + 1}/{dn}", "This is the reciprocal."), (f"{n}/{dn * 10}", "Percent means per 100: divide by 100, not 1000."), (f"{n * 10}/{dn}" if n * 10 < dn else f"{n + 1}/{dn}", "Divide by 100 to convert a percent."), (f"{n}/{dn + 2}", "This fraction has a different value.")]
            expl = f"{num_str(pct)}% = {num_str(pct)}/100 = {correct} in lowest terms."
        return _text_mc(rng, prompt, correct, ds, subskill="fraction_decimal_percent", explanation=expl, tags=["number", "fdp"], est=60, verify=correct)
    if d == "medium":
        vals = rng.sample([Fraction(1, 2), Fraction(2, 3), Fraction(3, 5), Fraction(5, 8), Fraction(7, 10), Fraction(3, 4), Fraction(4, 7), Fraction(5, 9), Fraction(9, 16), Fraction(11, 20), Fraction(13, 20), Fraction(7, 12), Fraction(17, 25), Fraction(5, 6)], 5)
        forms = []
        for v in vals:
            kind = rng.choice(["f", "d", "p"])
            if kind == "f":
                forms.append((f"{v.numerator}/{v.denominator}", v))
            elif kind == "d":
                forms.append((f"{float(v):.3f}".rstrip("0"), v))
            else:
                forms.append((f"{float(v) * 100:.1f}%".replace(".0%", "%"), v))
        want = rng.choice(["greatest", "least"])
        target = max(forms, key=lambda t: t[1]) if want == "greatest" else min(forms, key=lambda t: t[1])
        prompt = f"Which of the following numbers is the {want}?"
        ds = [(t[0], f"{t[0]} ≈ {float(t[1]):.3f}, which is not the {want}.") for t in forms if t is not target]
        expl = "Convert each to a decimal: " + ", ".join(f"{t[0]} ≈ {float(t[1]):.3f}" for t in forms) + f". The {want} is {target[0]}."
        return _text_mc(rng, prompt, target[0], ds, subskill="fraction_decimal_percent", explanation=expl, tags=["number", "fdp", "compare"], est=80, verify=f"{want}={target[0]}")
    a = rng.choice([Fraction(1, 2), Fraction(2, 3), Fraction(3, 4), Fraction(3, 5), Fraction(5, 6), Fraction(4, 5), Fraction(7, 8), Fraction(2, 5), Fraction(5, 8), Fraction(3, 8)])
    b = rng.choice([Fraction(1, 3), Fraction(1, 4), Fraction(2, 5), Fraction(3, 10), Fraction(1, 6), Fraction(5, 12), Fraction(1, 8), Fraction(3, 8)])
    op = rng.choice(["+", "−", "×", "÷"])
    val = {"+": a + b, "−": a - b, "×": a * b, "÷": a / b}[op]
    prompt = f"What is the value of {a} {op} {b}?"
    expl = {"+": f"Common denominator {math.lcm(a.denominator, b.denominator)}: {a} + {b} = {val}.",
            "−": f"Common denominator {math.lcm(a.denominator, b.denominator)}: {a} − {b} = {val}.",
            "×": f"Multiply numerators and denominators: {a.numerator * b.numerator}/{a.denominator * b.denominator} = {val}.",
            "÷": f"Multiply by the reciprocal: {a} × {b.denominator}/{b.numerator} = {val}."}[op]
    ds = [(Fraction(a.numerator + b.numerator, a.denominator + b.denominator) if op == "+" else Fraction(a.numerator - b.numerator, max(1, a.denominator - b.denominator)) if op == "−" and a.denominator != b.denominator else a * b if op != "×" else a + b, "Fractions {0} don't combine numerators and denominators separately.".format("added" if op == "+" else "subtracted" if op == "−" else "multiplied")),
          (a / b if op == "×" else a * b if op == "÷" else a * b, "Check the operation: {0}.".format({"+": "add", "−": "subtract", "×": "multiply", "÷": "divide (multiply by the reciprocal)"}[op])),
          (b / a if op == "÷" else val + Fraction(1, a.denominator), "Multiply by the reciprocal of the second fraction, not the first." if op == "÷" else "Arithmetic slip."),
          (val * 2, "Recheck the arithmetic.")]
    return _numeric_mc(rng, prompt, val, ds, subskill="fraction_decimal_percent", explanation=expl, tags=["number", "fractions"], est=80, verify=f"{a}{op}{b}={val}")


def np_divisibility(rng, d):
    """Remainders and divisibility reasoning."""
    if d == "easy":
        n = rng.randint(20, 300)
        k = rng.choice([3, 4, 5, 6, 7, 8, 9])
        val = n % k
        prompt = f"What is the remainder when {n} is divided by {k}?"
        expl = f"{n} = {k}·{n // k} + {val}, so the remainder is {val}."
        ds = [(n // k, "That is the quotient, not the remainder."), ((val + 1) % k, "Recheck: {0} × {1} = {2}.".format(k, n // k, k * (n // k))), ((val + k - 1) % k, "Recheck the subtraction."), (k - val if k - val != val and k - val != k else (val + 2) % k, "The remainder is what's left after subtracting the largest multiple of {0}.".format(k))]
        return _numeric_mc(rng, prompt, val, ds, subskill="integer_reasoning", explanation=expl, tags=["number", "remainder"], est=65, verify=f"{n}%{k}={val}")
    if d == "medium":
        k, r = rng.choice([5, 6, 7, 8, 9]), rng.randint(1, 4)
        m = rng.randint(2, 6)
        val = (m * r) % k
        prompt = f"When a positive integer n is divided by {k}, the remainder is {r}. What is the remainder when {m}n is divided by {k}?"
        expl = f"n = {k}q + {r}, so {m}n = {k}({m}q) + {m * r}; {m * r} leaves remainder {val} when divided by {k}."
        ds = [(m * r if m * r != val else val + 1, "{0} is {1} or more; reduce it modulo {1}.".format(m * r, k) if m * r >= k else "Recheck."), (r, "Multiplying n by {0} multiplies the remainder too (then reduce).".format(m)), ((r + m) % k, "The remainder is multiplied, not increased, by {0}.".format(m)), ((val + 1) % k, "Arithmetic slip.")]
        return _numeric_mc(rng, prompt, val, ds, subskill="integer_reasoning", explanation=expl, tags=["number", "remainder"], est=85, verify=f"{m}*{r} mod {k}={val}")
    k = rng.choice([3, 4, 6, 8, 9, 12])
    prompt = f"Which of the following numbers is divisible by {k}?"
    base = rng.randint(100, 900)
    good = [n for n in range(base, base + 60) if n % k == 0]
    bad = [n for n in range(base, base + 60) if n % k != 0]
    g = rng.choice(good)
    bads = rng.sample(bad, 4)
    rule = {3: "the digit sum is a multiple of 3", 4: "the last two digits form a multiple of 4", 6: "it is even and its digit sum is a multiple of 3",
            8: "the last three digits form a multiple of 8", 9: "the digit sum is a multiple of 9", 12: "it is divisible by both 3 and 4"}[k]
    ds = [(str(n), f"{n} ÷ {k} leaves remainder {n % k}.") for n in bads]
    expl = f"A number is divisible by {k} when {rule}: {g} = {k} × {g // k}."
    return _text_mc(rng, prompt, str(g), ds, subskill="integer_reasoning", explanation=expl, tags=["number", "divisibility"], est=80, verify=f"{g}/{k}")


# --------------------------------------------------------------------------- #
# coordinate_geometry
# --------------------------------------------------------------------------- #
def _pt(x, y):
    return f"({_m(x)}, {_m(y)})"


def cg_distance(rng, d):
    """Distance between two points (integer via triples; hard: radical)."""
    if d != "hard":
        a, b, c = _pyth_triple(rng, 26)
        if rng.random() < 0.5:
            a, b = b, a
        x1, y1 = rng.randint(-9, 9), rng.randint(-9, 9)
        sx, sy = rng.choice([-1, 1]), rng.choice([-1, 1])
        x2, y2 = x1 + sx * a, y1 + sy * b
        val = c
        prompt = rng.choice([f"What is the distance between the points {_pt(x1, y1)} and {_pt(x2, y2)} in the standard (x, y) coordinate plane?",
                             f"In the standard (x, y) coordinate plane, how far apart are the points {_pt(x1, y1)} and {_pt(x2, y2)}?"])
        expl = f"d = √(({_m(x2)} − ({_m(x1)}))² + ({_m(y2)} − ({_m(y1)}))²) = √({a}² + {b}²) = √{c * c} = {c}."
        ds = [(a + b, "Add the squares, then take the square root; don't add the differences."), (c * c, "Take the square root."), (abs(a - b) if abs(a - b) else c + 2, "Add the squared differences; don't subtract."), (c + 1, "Arithmetic slip.")]
        if d == "medium":
            prompt = f"Points A{_pt(x1, y1)} and B{_pt(x2, y2)} are the endpoints of a segment. What is the length of segment AB?"
        return _numeric_mc(rng, prompt, val, ds, subskill="distance_midpoint", explanation=expl, tags=["coordinate", "distance"], est=80, verify=f"d={c}")
    dx, dy = rng.choice([(1, 1), (2, 2), (1, 2), (2, 4), (3, 3), (1, 3), (2, 3), (3, 6), (4, 4), (2, 6), (5, 5), (3, 4 if False else 9)])
    x1, y1 = rng.randint(-8, 8), rng.randint(-8, 8)
    x2, y2 = x1 + dx, y1 - dy
    sq = dx * dx + dy * dy
    k = 1
    while any(sq % (p * p) == 0 for p in range(2, 10)):
        p = next(p for p in range(2, 10) if sq % (p * p) == 0)
        sq //= p * p
        k *= p
    correct = f"{k if k > 1 else ''}√{sq}" if sq > 1 else str(k)
    prompt = f"What is the distance between {_pt(x1, y1)} and {_pt(x2, y2)} in the standard (x, y) coordinate plane?"
    expl = f"d = √({dx}² + {dy}²) = √{dx * dx + dy * dy} = {correct}."
    ds = [(f"√{dx + dy}", "Square the differences before adding."), (f"{dx + dy}", "Use the Pythagorean form, not the sum of differences."),
          (f"√{abs(dx * dx - dy * dy)}" if dx != dy else f"√{2 * (dx * dx + dy * dy)}", "Add the squared differences."), (f"{k * k if k > 1 else 2}√{sq}", "Simplify the radical carefully: √{0} = {1}.".format(dx * dx + dy * dy, correct)),
          # spares, used when one above equals another in value (√100 vs 10)
          (f"√{dx * dx + dy * dy + 1}", "Recompute the sum of the squared differences."),
          (f"{k + 1}√{sq}" if sq > 1 else f"√{k * k + 2}", "Simplify the radical carefully: √{0} = {1}.".format(dx * dx + dy * dy, correct))]
    return _text_mc(rng, prompt, correct, ds, subskill="distance_midpoint", explanation=expl, tags=["coordinate", "distance", "radical"], est=90, verify=correct)


def cg_midpoint(rng, d):
    """Midpoint (easy), missing endpoint (medium), midpoint with fractions / segment reasoning (hard)."""
    if d == "easy":
        x1 = rng.choice([v for v in range(-9, 10) if v])
        y1 = rng.choice([v for v in range(-9, 10) if v])
        x2 = x1 + 2 * rng.choice([v for v in range(-6, 7) if v and v != -x1])
        y2 = y1 + 2 * rng.choice([v for v in range(-6, 7) if v and v != -y1])
        mx, my = (x1 + x2) // 2, (y1 + y2) // 2
        prompt = f"What is the midpoint of the segment with endpoints {_pt(x1, y1)} and {_pt(x2, y2)}?"
        correct = _pt(mx, my)
        ds = [(_pt(x2 - x1, y2 - y1), "That is the difference of the coordinates, not their average."), (_pt((x2 - x1) // 2, (y2 - y1) // 2), "Average the coordinates: add, then halve."),
              (_pt(my, mx) if mx != my else _pt(mx + 1, my), "The x-coordinate comes from the x-values."), (_pt(x1 + x2, y1 + y2), "Divide the sums by 2.")]
        expl = f"Midpoint = (({_m(x1)} + {_m(x2)})/2, ({_m(y1)} + {_m(y2)})/2) = {correct}."
        if not _distinct(correct, ds):
            return cg_midpoint(rng, d)
    elif d == "medium":
        x1, y1 = rng.randint(-9, 9), rng.randint(-9, 9)
        mx, my = x1 + rng.choice([v for v in range(-6, 7) if v]), y1 + rng.choice([v for v in range(-6, 7) if v])
        x2, y2 = 2 * mx - x1, 2 * my - y1
        prompt = f"The midpoint of segment AB is {_pt(mx, my)}, and point A is {_pt(x1, y1)}. What are the coordinates of point B?"
        correct = _pt(x2, y2)
        ds = [(_pt((x1 + mx) // 2 if (x1 + mx) % 2 == 0 else mx - x1, (y1 + my) // 2 if (y1 + my) % 2 == 0 else my - y1), "That is between A and the midpoint; B is on the other side."), (_pt(mx - x1, my - y1), "B = 2M − A, not M − A."),
              (_pt(x1 + mx, y1 + my), "Subtract A from twice the midpoint."), (_pt(-x2, -y2) if (x2, y2) != (0, 0) else _pt(x2 + 1, y2), "Sign slip.")]
        expl = f"B = (2·{_m(mx)} − ({_m(x1)}), 2·{_m(my)} − ({_m(y1)})) = {correct}."
    else:
        x1, y1 = rng.randint(-9, 9), rng.randint(-9, 9)
        x2 = x1 + rng.choice([v for v in range(-9, 10) if v % 2])
        y2 = y1 + rng.choice([v for v in range(-9, 10) if v % 2])
        mx, my = Fraction(x1 + x2, 2), Fraction(y1 + y2, 2)
        prompt = f"Segment PQ has endpoints P{_pt(x1, y1)} and Q{_pt(x2, y2)}. What is the midpoint of PQ?"
        correct = f"({num_str(mx)}, {num_str(my)})"
        ds = [(f"({num_str(Fraction(x2 - x1, 2))}, {num_str(Fraction(y2 - y1, 2))})", "Average the coordinates: add, then halve."), (f"({num_str(mx * 2)}, {num_str(my * 2)})", "Divide the sums by 2."),
              (f"({num_str(my)}, {num_str(mx)})" if mx != my else f"({num_str(mx + 1)}, {num_str(my)})", "The x-coordinate comes from the x-values."), (f"({num_str(-mx)}, {num_str(-my)})" if mx != 0 or my != 0 else f"({num_str(mx + 1)}, {num_str(my)})", "Sign slip.")]
        expl = f"Midpoint = (({_m(x1)} + {_m(x2)})/2, ({_m(y1)} + {_m(y2)})/2) = {correct}."
    if not _distinct(correct, ds):
        return cg_midpoint(rng, d)
    return _text_mc(rng, prompt, correct, ds, subskill="distance_midpoint", explanation=expl, tags=["coordinate", "midpoint"], est=75, verify=correct)


def cg_circle(rng, d):
    """Circle equation: center/radius (easy), write the equation (medium), general form (hard)."""
    h = rng.choice([v for v in range(-9, 10) if v])
    k = rng.choice([v for v in range(-9, 10) if v])
    r = rng.randint(2, 12)
    eq = f"(x {_pm(-h)})² + (y {_pm(-k)})² = {r * r}"
    if d == "easy":
        if rng.random() < 0.5:
            prompt = f"In the standard (x, y) coordinate plane, what is the center of the circle {eq}?"
            correct = _pt(h, k)
            ds = [(_pt(-h, -k), "The center is (h, k) in (x − h)² + (y − k)²; the signs flip from what's written."), (_pt(k, h) if h != k else _pt(h, -k), "The x-coordinate comes from the x-term."), (_pt(h, -k), "Check the sign of the y-coordinate."), (_pt(-h, k), "Check the sign of the x-coordinate.")]
            expl = f"(x − h)² + (y − k)² = r² has center (h, k) = {correct}."
            return _text_mc(rng, prompt, correct, ds, subskill="circle_equation", explanation=expl, tags=["coordinate", "circle"], est=70, verify=correct)
        prompt = f"In the standard (x, y) coordinate plane, what is the radius of the circle {eq}?"
        val = r
        expl = f"The right side is r² = {r * r}, so r = {r}."
        ds = [(r * r, "That is r²; take the square root."), (2 * r, "That is the diameter."), (Fraction(r * r, 2), "Take the square root, don't halve."), (abs(h) if abs(h) not in (r, r * r, 2 * r) else r + 1, "The center's coordinates don't give the radius.")]
        return _numeric_mc(rng, prompt, val, ds, subskill="circle_equation", explanation=expl, tags=["coordinate", "circle"], est=65, verify=f"r={r}")
    if d == "medium":
        prompt = f"Which of the following is an equation of the circle with center {_pt(h, k)} and radius {r} in the standard (x, y) coordinate plane?"
        ds = [(f"(x {_pm(h)})² + (y {_pm(k)})² = {r * r}", "The signs inside the parentheses are opposite to the center's coordinates."), (f"(x {_pm(-h)})² + (y {_pm(-k)})² = {r}", "The right side is r², not r."),
              (f"(x {_pm(-k)})² + (y {_pm(-h)})² = {r * r}" if h != k else f"(x {_pm(-h)})² + (y {_pm(-k)})² = {2 * r}", "The x-term uses the x-coordinate of the center."), (f"(x {_pm(h)})² + (y {_pm(k)})² = {r}", "Both the signs and the radius are wrong.")]
        expl = f"Standard form (x − h)² + (y − k)² = r² with h = {_m(h)}, k = {_m(k)}, r² = {r * r}: {eq}."
        return _text_mc(rng, prompt, eq, ds, subskill="circle_equation", explanation=expl, tags=["coordinate", "circle"], est=80, verify=eq)
    c = h * h + k * k - r * r
    gen = f"x² + y² {_pm(-2 * h)}x {_pm(-2 * k)}y {_pm(c)} = 0" if c else f"x² + y² {_pm(-2 * h)}x {_pm(-2 * k)}y = 0"
    which = rng.choice(["center", "radius"])
    if which == "radius":
        prompt = f"The equation {gen} represents a circle in the standard (x, y) coordinate plane. What is the radius of the circle?"
        val = r
        expl = f"Complete the square: {eq}, so r = {r}."
        ds = [(r * r, "That is r²."), (abs(c) if abs(c) not in (r, r * r) else r + 2, "The constant term is not the radius; complete the square."), (abs(h) + abs(k) if abs(h) + abs(k) not in (r, r * r) else r + 3, "Complete the square for both x and y."), (2 * r, "That is the diameter.")]
        return _numeric_mc(rng, prompt, val, ds, subskill="circle_equation", explanation=expl, tags=["coordinate", "circle"], est=100, qtype="multi_step_math", verify=f"r={r}")
    prompt = f"The equation {gen} represents a circle in the standard (x, y) coordinate plane. What is the center of the circle?"
    correct = _pt(h, k)
    ds = [(_pt(-h, -k), "The center coordinates are half the x- and y-coefficients with the opposite sign."), (_pt(-2 * h, -2 * k), "Halve the coefficients of x and y."), (_pt(2 * h, 2 * k), "Halve the coefficients and flip their signs."), (_pt(h, -k), "Check the sign of the y-coordinate.")]
    expl = f"Group and complete the square: {eq}; the center is {correct}."
    return _text_mc(rng, prompt, correct, ds, subskill="circle_equation", explanation=expl, tags=["coordinate", "circle"], est=100, qtype="multi_step_math", verify=correct)


def cg_lines(rng, d):
    """Slopes of parallel/perpendicular lines; equation of such a line."""
    m = rng.choice([v for v in range(-7, 8) if v not in (0, 1, -1)])
    b = rng.randint(-10, 10)
    rel = rng.choice(["parallel", "perpendicular"])
    if d == "easy":
        prompt = f"In the standard (x, y) coordinate plane, what is the slope of any line {rel} to the line y = {_lin(m, b)}?"
        val = Fraction(m) if rel == "parallel" else Fraction(-1, m)
        expl = (f"Parallel lines have equal slopes: {m}." if rel == "parallel" else f"Perpendicular slopes are negative reciprocals: −1/{_m(m)} = {num_str(val)}.")
        ds = [(Fraction(-1, m) if rel == "parallel" else Fraction(m), f"That is the {'perpendicular' if rel == 'parallel' else 'parallel'} slope."), (Fraction(-m), "Parallel keeps the slope; perpendicular needs the reciprocal too." if rel == "parallel" else "Take the reciprocal as well as changing the sign."), (Fraction(1, m), "Don't invert for parallel." if rel == "parallel" else "Change the sign too."), (Fraction(b), "The y-intercept is not the slope.")]
        return _numeric_mc(rng, prompt, val, ds, subskill="parallel_perpendicular", explanation=expl, tags=["coordinate", "slope", rel], est=70, verify=f"{rel} slope {num_str(val)}")
    if d == "medium":
        A = rng.choice([v for v in range(-6, 7) if v not in (0,)])
        B = rng.choice([v for v in range(-6, 7) if v not in (0, A, -A)])
        C = rng.randint(-12, 12)
        slope = Fraction(-A, B)
        val = slope if rel == "parallel" else -1 / slope
        line = f"{_lin(A, 0)} {'+' if B > 0 else '−'} {_lin(abs(B), 0, 'y')} = {_m(C)}"
        prompt = f"What is the slope of a line that is {rel} to the line {line} in the standard (x, y) coordinate plane?"
        expl = f"Solve for y: slope of the given line is −A/B = {num_str(slope)}. {'Parallel: same slope' if rel == 'parallel' else 'Perpendicular: negative reciprocal'}, {num_str(val)}."
        ds = [(-1 / slope if rel == "parallel" else slope, f"That is the {'perpendicular' if rel == 'parallel' else 'parallel'} slope."), (Fraction(A, B), "The slope of Ax + By = C is −A/B." if rel == "parallel" else "Take the negative reciprocal of −A/B."), (Fraction(B, A) if rel == "parallel" else Fraction(-B, A) * -1 if False else Fraction(B, A), "Recheck: solve for y to read the slope."), (Fraction(A), "The slope is −A/B, not A.")]
        return _numeric_mc(rng, prompt, val, ds, subskill="parallel_perpendicular", explanation=expl, tags=["coordinate", "slope", rel], est=85, verify=f"{rel} slope {num_str(val)}")
    x1 = rng.choice([v for v in range(-6, 7) if v])
    if rel == "parallel":
        ms = m
        y1 = ms * x1 + rng.choice([v for v in range(-9, 10) if v])
        bb = y1 - ms * x1
        correct = f"y = {_lin(ms, bb)}"
        ds = [(f"y = {_lin(-ms, y1 + ms * x1)}", "A parallel line has the same slope, {0}.".format(_m(ms))), (f"y = {_lin(ms, b)}", "That is the original line's intercept; use the given point."), (f"y = {_lin(ms, y1)}", f"{_m(y1)} is y at x = {_m(x1)}, not the intercept."), (f"y = {_lin(Fraction(-1, ms), y1 + Fraction(x1, ms))}".replace("y = ", "y = ") if False else f"y = {_lin(ms, -bb)}" if bb else f"y = {_lin(ms, 1)}", "Sign slip solving for the intercept.")]
        expl = f"Slope {_m(ms)} (parallel). {_m(y1)} = {_m(ms)}·({_m(x1)}) + b gives b = {_m(bb)}: {correct}."
        if not _distinct(correct, ds):
            return cg_lines(rng, d)
    else:
        m2 = rng.choice([2, 3, 4, 5, -2, -3, -4, -5])
        ms = Fraction(-1, m2)
        y1 = rng.randint(-9, 9)
        x1 = m2 * rng.choice([v for v in range(-3, 4) if v])
        bb = y1 - ms * x1
        correct = f"y = {_lin(ms, bb)}".replace(f"{num_str(ms)}x", f"({num_str(ms)})x")
        correct = f"y = ({num_str(ms)})x {_pm(bb)}" if bb else f"y = ({num_str(ms)})x"
        m = m2
        ds = [(f"y = {_lin(m2, y1 - m2 * x1)}", "A perpendicular line has slope −1/{0}, not {0}.".format(_m(m2))), (f"y = ({num_str(Fraction(1, m2))})x {_pm(y1 - Fraction(x1, m2))}", "The perpendicular slope is the NEGATIVE reciprocal."), (f"y = ({num_str(ms)})x {_pm(y1)}" if y1 != bb else f"y = ({num_str(ms)})x {_pm(y1 + 2)}", f"{_m(y1)} is y at x = {_m(x1)}, not the intercept."), (f"y = ({num_str(-m2)})x {_pm(y1 + m2 * x1)}", "Take the reciprocal as well as changing the sign.")]
        expl = f"Perpendicular slope −1/{_m(m2)} = {num_str(ms)}. {_m(y1)} = ({num_str(ms)})({_m(x1)}) + b gives b = {num_str(bb)}: {correct}."
        b = rng.randint(-10, 10)
        if not _distinct(correct, ds):
            return cg_lines(rng, d)
    prompt = f"Which of the following is an equation of the line through {_pt(x1, y1)} that is {rel} to the line y = {_lin(m, b)}?"
    return _text_mc(rng, prompt, correct, ds, subskill="parallel_perpendicular", explanation=expl, tags=["coordinate", "line", rel], est=95, verify=correct)


def cg_point_on_line(rng, d):
    """Is a point on a line / find a missing coordinate / intercepts & collinearity."""
    m = rng.choice([v for v in range(-6, 7) if v])
    b = rng.randint(-10, 10)
    if d == "easy":
        pts = [(x, m * x + b) for x in range(-5, 6)]
        on = rng.choice(pts)
        offs = []
        while len(offs) < 4:
            x = rng.randint(-5, 5)
            y = m * x + b + rng.choice([-3, -2, -1, 1, 2, 3])
            if (x, y) not in offs:
                offs.append((x, y))
        prompt = f"Which of the following points lies on the line y = {_lin(m, b)} in the standard (x, y) coordinate plane?"
        ds = [(_pt(x, y), f"At x = {_m(x)} the line gives y = {_m(m * x + b)}, not {_m(y)}.") for x, y in offs]
        expl = f"Substitute x = {_m(on[0])}: y = {_m(m)}({_m(on[0])}) {_pm(b)} = {_m(on[1])}, so {_pt(*on)} is on the line."
        return _text_mc(rng, prompt, _pt(*on), ds, subskill="points_on_lines", explanation=expl, tags=["coordinate", "line"], est=70, verify=_pt(*on))
    if d == "medium":
        x = rng.choice([v for v in range(-8, 9) if v])
        y = m * x + b
        if rng.random() < 0.5:
            prompt = f"The point ({_m(x)}, k) lies on the line y = {_lin(m, b)}. What is the value of k?"
            val = y
            expl = f"k = {_m(m)}({_m(x)}) {_pm(b)} = {_m(y)}."
            ds = [(m * x - b, "Check the sign of the constant."), (m + x + b, "Multiply m by x; don't add."), (-y if y else y + 1, "Sign slip."), (m * x, "Include the y-intercept.")]
        else:
            prompt = f"The point (k, {_m(y)}) lies on the line y = {_lin(m, b)}. What is the value of k?"
            val = x
            expl = f"{_m(y)} = {_m(m)}k {_pm(b)} → {_m(m)}k = {_m(y - b)} → k = {_m(x)}."
            ds = [(y - b, "Divide by the slope."), (Fraction(y + b, m), "Subtract the intercept; don't add."), (-x, "Sign slip."), (m * y + b, "Solve for x, don't evaluate at x = {0}.".format(_m(y)))]
        return _numeric_mc(rng, prompt, val, ds, subskill="points_on_lines", explanation=expl, tags=["coordinate", "line"], est=75, verify=f"({x},{y})")
    x1 = rng.randint(-6, 6)
    x2 = x1 + rng.choice([v for v in range(-5, 6) if v])
    x3 = x2 + rng.choice([v for v in range(-5, 6) if v and x2 + v != x1])
    y1, y2 = m * x1 + b, m * x2 + b
    y3 = m * x3 + b
    prompt = f"Points {_pt(x1, y1)}, {_pt(x2, y2)}, and ({_m(x3)}, k) lie on the same line in the standard (x, y) coordinate plane. What is the value of k?"
    val = y3
    expl = f"Slope from the first two points: ({_m(y2)} − ({_m(y1)}))/({_m(x2)} − ({_m(x1)})) = {_m(m)}. Then k = {_m(y1)} + {_m(m)}({_m(x3)} − ({_m(x1)})) = {_m(y3)}."
    ds = [(-m * x3 + b, "Check the sign of the slope."), (m * x3, "Include the intercept."), (y2 + (x3 - x2), "Multiply the x-change by the slope, not by 1."), (y3 + m, "Arithmetic slip.")]
    return _numeric_mc(rng, prompt, val, ds, subskill="points_on_lines", explanation=expl, tags=["coordinate", "collinear"], est=95, qtype="multi_step_math", verify=f"k={y3}")


# --------------------------------------------------------------------------- #
# angles_polygons
# --------------------------------------------------------------------------- #
def ap_transversal(rng, d):
    """Angle pairs formed by parallel lines and a transversal."""
    a = rng.randint(31, 149)
    if a == 90:
        a = 85
    if d == "easy":
        rel = rng.choice([("corresponding", a), ("alternate interior", a), ("same-side interior", 180 - a), ("vertical", a), ("alternate exterior", a)])
        prompt = f"Two parallel lines are cut by a transversal. One angle measures {a}°. What is the measure of its {rel[0]} angle?"
        val = rel[1]
        expl = (f"{rel[0].capitalize()} angles are congruent, so it is {a}°." if rel[1] == a else f"Same-side interior angles are supplementary: 180 − {a} = {180 - a}°.")
        ds = [(180 - a if rel[1] == a else a, "Congruent or supplementary? {0} angles are {1}.".format(rel[0], "congruent" if rel[1] == a else "supplementary")), (90 - a if a < 90 else a - 90, "Supplementary angles sum to 180°, not 90°."), (360 - a, "Angles around a point sum to 360°, but this pair doesn't."), (val + 10, "Arithmetic slip.")]
    elif d == "medium":
        k, c = rng.randint(2, 5), rng.randint(1, 30)
        x = rng.randint(10, 40)
        angle = k * x + c
        other = angle if rng.random() < 0.5 else 180 - angle
        rel = "alternate interior" if other == angle else "same-side interior"
        if other <= 0 or other >= 180:
            return ap_transversal(rng, d)
        prompt = f"Two parallel lines are cut by a transversal. Two {rel} angles measure ({k}x + {c})° and {other}°. What is the value of x?"
        val = x
        expl = (f"{rel.capitalize()} angles are congruent: {k}x + {c} = {other} → x = {x}." if rel == "alternate interior"
                else f"Same-side interior angles are supplementary: {k}x + {c} + {other} = 180 → {k}x = {180 - other - c} → x = {x}.")
        ds = [(Fraction(180 - other - c, k) if rel == "alternate interior" else Fraction(other - c, k), "Check whether the pair is congruent or supplementary."), (angle, "That is the angle measure, not x."), (Fraction(other, k), "Subtract {0} before dividing by {1}.".format(c, k)), (x + 2, "Arithmetic slip.")]
    else:
        # angle x, find an angle after two parallel-line steps: with exterior angle sum
        k1, k2 = rng.randint(2, 4), rng.randint(2, 4)
        x = rng.randint(10, 35)
        c1 = rng.randint(1, 20)
        a1 = k1 * x + c1
        c2 = 180 - a1 - k2 * x
        if c2 <= 0:
            return ap_transversal(rng, d)
        prompt = (f"Two parallel lines are cut by a transversal. A pair of same-side interior angles measure "
                  f"({k1}x + {c1})° and ({k2}x + {c2})°. What is the measure of the smaller of the two angles?")
        val = min(a1, 180 - a1)
        expl = f"They are supplementary: {k1 + k2}x + {c1 + c2} = 180 → x = {x}. The angles are {a1}° and {180 - a1}°; the smaller is {val}°."
        ds = [(x, "That is x, not an angle measure."), (max(a1, 180 - a1), "That is the larger angle."), (Fraction(180 - c1 - c2, k1 + k2) * k1 + c1 if False else (a1 + 180 - a1) // 2, "The two angles are not equal here."), (abs(a1 - (180 - a1)), "That is the difference of the two angles.")]
    return _numeric_mc(rng, prompt, val, ds, subskill="parallel_lines", explanation=expl, tags=["geometry", "angles", "parallel"], est=75 if d == "easy" else 90, verify=f"val={val}")


def ap_triangle(rng, d):
    """Triangle angle sum, isosceles, exterior angles."""
    if d == "easy":
        a, b = rng.randint(20, 80), rng.randint(20, 80)
        c = 180 - a - b
        if c < 15:
            return ap_triangle(rng, d)
        prompt = rng.choice([f"Two angles of a triangle measure {a}° and {b}°. What is the measure of the third angle?",
                             f"In triangle ABC, ∠A = {a}° and ∠B = {b}°. What is the measure of ∠C?"])
        val = c
        expl = f"The angles of a triangle sum to 180°: 180 − {a} − {b} = {c}°."
        ds = [(360 - a - b, "A triangle's angles sum to 180°, not 360°."), (90 - abs(a - b) if 90 - abs(a - b) > 0 and 90 - abs(a - b) != c else a + b, "Subtract both from 180."), (a + b, "That is the sum of the two given angles (equal to the exterior angle at C)."), (c + 10, "Arithmetic slip.")]
    elif d == "medium":
        kind = rng.choice(["iso_base", "iso_vertex", "exterior"])
        if kind == "iso_base":
            v = rng.choice(range(20, 140, 2))
            base = (180 - v) // 2
            prompt = f"In an isosceles triangle, the vertex angle (between the two congruent sides) measures {v}°. What is the measure of each base angle?"
            val = base
            expl = f"The base angles are congruent: (180 − {v})/2 = {base}°."
            ds = [(180 - v, "That is the sum of both base angles; halve it."), (v, "The base angles are not equal to the vertex angle here."), ((180 - v) // 2 + v // 2 if (180 - v) // 2 + v // 2 != base else base + 5, "Subtract the vertex angle from 180, then halve."), (90 - v // 2 + 1 if 90 - v // 2 + 1 != base else base + 3, "Arithmetic slip.")]
        elif kind == "iso_vertex":
            base = rng.randint(20, 85)
            v = 180 - 2 * base
            prompt = f"An isosceles triangle has two angles that each measure {base}°. What is the measure of the third angle?"
            val = v
            expl = f"180 − 2·{base} = {v}°."
            ds = [(180 - base, "Both congruent angles must be subtracted."), (base, "The third angle is different unless the triangle is equilateral."), (90 - base if 90 - base > 0 else 2 * base, "Subtract from 180, not 90."), (v + 10, "Arithmetic slip.")]
        else:
            a, b = rng.randint(25, 80), rng.randint(25, 80)
            prompt = f"In a triangle, two interior angles measure {a}° and {b}°. What is the measure of the exterior angle at the third vertex?"
            val = a + b
            expl = f"An exterior angle equals the sum of the two remote interior angles: {a} + {b} = {a + b}°."
            ds = [(180 - a - b, "That is the third interior angle, not the exterior angle."), (360 - a - b, "Use 180° − interior, or the sum of the remote interior angles."), (abs(a - b) if a != b else a + b + 10, "Add the remote interior angles."), (a + b + 10, "Arithmetic slip.")]
    else:
        # angles in ratio or algebraic
        if rng.random() < 0.5:
            p, q, r = rng.choice([(1, 2, 3), (2, 3, 4), (3, 4, 5), (1, 1, 2), (2, 2, 5), (1, 3, 5), (3, 5, 7), (4, 5, 6), (2, 7, 9), (1, 4, 7)])
            k = 180 // (p + q + r)
            if k * (p + q + r) != 180:
                return ap_triangle(rng, d)
            prompt = f"The measures of the angles of a triangle are in the ratio {p}:{q}:{r}. What is the measure of the largest angle?"
            val = r * k
            expl = f"Let the angles be {p}x, {q}x, {r}x: {p + q + r}x = 180 → x = {k}; largest = {r}·{k} = {val}°."
            ds = [(k, "That is x, the common factor."), (p * k, "That is the smallest angle."), (q * k, "That is the middle angle."), (r * 360 // (p + q + r), "The angle sum is 180°, not 360°.")]
        else:
            x = rng.randint(10, 40)
            k1, k2 = rng.randint(1, 4), rng.randint(1, 4)
            c1, c2 = rng.randint(1, 30), rng.randint(1, 30)
            third = 180 - (k1 * x + c1) - (k2 * x + c2)
            if third < 15:
                return ap_triangle(rng, d)
            prompt = f"The angles of a triangle measure ({k1}x + {c1})°, ({k2}x + {c2})°, and {third}°. What is the measure of the largest angle?"
            angles = [k1 * x + c1, k2 * x + c2, third]
            val = max(angles)
            expl = f"{k1 + k2}x + {c1 + c2} + {third} = 180 → x = {x}. The angles are {angles[0]}°, {angles[1]}°, {angles[2]}°; the largest is {val}°."
            ds = [(x, "That is x, not an angle."), (min(angles), "That is the smallest angle."), (sorted(angles)[1] if sorted(angles)[1] != val else val - 5, "That is the middle angle."), (val + 5, "Arithmetic slip.")]
    return _numeric_mc(rng, prompt, val, ds, subskill="triangle_angles", explanation=expl, tags=["geometry", "angles", "triangle"], est=70 if d == "easy" else 90, verify=f"val={val}")


def ap_polygon(rng, d):
    """Polygon interior-angle sums, regular polygon angles, sides from an angle."""
    names = {3: "triangle", 4: "quadrilateral", 5: "pentagon", 6: "hexagon", 7: "heptagon", 8: "octagon", 9: "nonagon", 10: "decagon", 12: "dodecagon"}
    if d == "easy":
        n = rng.choice([4, 5, 6, 7, 8, 9, 10, 12])
        val = 180 * (n - 2)
        prompt = rng.choice([f"What is the sum of the interior angle measures of a {names[n]}?",
                             f"What is the sum of the interior angles, in degrees, of a polygon with {n} sides?"])
        expl = f"Sum = 180(n − 2) = 180·({n} − 2) = {val}°."
        ds = [(180 * n, "Use n − 2, not n."), (360, "360° is the sum of the exterior angles of any polygon."), (180 * (n - 1), "Use n − 2."), (val + 180, "Arithmetic slip.")]
    elif d == "medium":
        n = rng.choice([5, 6, 8, 9, 10, 12, 15, 18, 20])
        if rng.random() < 0.5:
            val = 180 * (n - 2) // n
            prompt = f"What is the measure of each interior angle of a regular {names.get(n, str(n) + '-sided polygon')}?"
            expl = f"Each interior angle = 180(n − 2)/n = 180·{n - 2}/{n} = {val}°."
            ds = [(360 // n, "That is each exterior angle."), (180 * (n - 2), "Divide the sum by the number of angles."), (180 - 360 // n + 10 if 180 - 360 // n + 10 != val else val + 5, "Arithmetic slip."), (180 // n if 180 % n == 0 else 90, "Use the interior-angle sum 180(n − 2).")]
        else:
            val = 360 // n
            prompt = f"What is the measure of each exterior angle of a regular polygon with {n} sides?"
            expl = f"Exterior angles sum to 360°, so each is 360/{n} = {val}°."
            ds = [(180 * (n - 2) // n, "That is each interior angle."), (180 // n if 180 % n == 0 else 180 - 360 // n, "Exterior angles sum to 360°."), (360 // (n - 2) if 360 % (n - 2) == 0 else val + 6, "Divide by n, not n − 2."), (val + 5, "Arithmetic slip.")]
    else:
        n = rng.choice([5, 6, 8, 9, 10, 12, 15, 18, 20, 24, 30, 36])
        if rng.random() < 0.5:
            ia = 180 * (n - 2) // n
            prompt = f"Each interior angle of a regular polygon measures {ia}°. How many sides does the polygon have?"
            val = n
            expl = f"Each exterior angle is 180 − {ia} = {180 - ia}°, and 360/{180 - ia} = {n} sides."
            ds = [(180 - ia, "That is the exterior angle, not the number of sides."), (n - 2, "Recheck: 360 ÷ exterior angle gives n directly."), (n + 2, "Arithmetic slip."), (ia // 10 if ia // 10 not in (n,) else n + 1, "Use the exterior angle 180 − {0}.".format(ia))]
        else:
            total = 180 * (n - 2)
            prompt = f"The interior angles of a polygon sum to {total}°. How many sides does the polygon have?"
            val = n
            expl = f"180(n − 2) = {total} → n − 2 = {total // 180} → n = {n}."
            ds = [(n - 2, "That is n − 2; add 2."), (total // 180 + 1, "Add 2 to {0}.".format(total // 180)), (n + 2, "Arithmetic slip."), (total // 360 if total // 360 != n else n + 3, "Divide by 180, not 360.")]
    return _numeric_mc(rng, prompt, val, ds, subskill="polygon_angles", explanation=expl, tags=["geometry", "angles", "polygon"], est=70 if d == "easy" else 85, verify=f"val={val}")


ap_polygon.small_space = True


def ap_pairs(rng, d):
    """Complementary/supplementary/vertical angle pairs with algebra (easy/medium); quadrilateral (hard)."""
    if d == "easy":
        a = rng.randint(10, 80)
        kind = rng.choice(["complement", "supplement"])
        val = 90 - a if kind == "complement" else 180 - a
        prompt = f"What is the measure of the {kind} of a {a}° angle?"
        expl = f"{kind.capitalize()}ary angles sum to {90 if kind == 'complement' else 180}°: {90 if kind == 'complement' else 180} − {a} = {val}°."
        ds = [(180 - a if kind == "complement" else 90 - a if a < 90 else 270 - a, "Complementary = 90°, supplementary = 180°."), (a, "The {0} is a different angle.".format(kind)), (360 - a, "Not a full turn."), (val + 10, "Arithmetic slip.")]
    elif d == "medium":
        x = rng.randint(5, 40)
        k1, k2 = rng.randint(1, 5), rng.randint(1, 5)
        c1 = rng.randint(1, 30)
        kind = rng.choice(["supplementary", "complementary", "vertical"])
        if kind == "vertical":
            c2 = (k1 - k2) * x + c1
            if c2 <= 0 or k1 == k2:
                return ap_pairs(rng, d)
            prompt = f"Two vertical angles measure ({k1}x + {c1})° and ({k2}x + {c2})°. What is the value of x?"
            expl = f"Vertical angles are congruent: {k1}x + {c1} = {k2}x + {c2} → x = {x}."
            ds = [(Fraction(180 - c1 - c2, k1 + k2), "Vertical angles are equal, not supplementary."), (k1 * x + c1, "That is the angle measure, not x."), (Fraction(c2 - c1, k1 + k2), "Subtract the x-coefficients; don't add."), (x + 3, "Arithmetic slip.")]
        else:
            total = 180 if kind == "supplementary" else 90
            c2 = total - (k1 + k2) * x - c1
            if c2 <= 0:
                return ap_pairs(rng, d)
            prompt = f"Two {kind} angles measure ({k1}x + {c1})° and ({k2}x + {c2})°. What is the value of x?"
            expl = f"{kind.capitalize()} angles sum to {total}°: {k1 + k2}x + {c1 + c2} = {total} → x = {x}."
            ds = [(Fraction(c2 - c1, k1 - k2) if k1 != k2 and (c2 - c1) % (k1 - k2) == 0 else x + 7, "The angles are not equal; they sum to {0}°.".format(total)), (k1 * x + c1, "That is one angle's measure, not x."), (Fraction((360 if total == 180 else 180) - c1 - c2, k1 + k2), "The pair sums to {0}°.".format(total)), (x - 2, "Arithmetic slip.")]
        val = x
    else:
        a, b, c = rng.randint(50, 130), rng.randint(50, 130), rng.randint(30, 110)
        dd = 360 - a - b - c
        if dd < 20 or dd > 160:
            return ap_pairs(rng, d)
        prompt = f"Three angles of a quadrilateral measure {a}°, {b}°, and {c}°. What is the measure of the fourth angle?"
        val = dd
        expl = f"A quadrilateral's angles sum to 360°: 360 − {a} − {b} − {c} = {dd}°."
        ds = [(180 - (a + b + c - 180) if 0 < 180 - (a + b + c - 180) != dd else dd + 20, "The sum for a quadrilateral is 360°, not 180°."), (a + b + c, "Subtract that sum from 360."), (dd + 10, "Arithmetic slip."), ((a + b + c) // 3 if (a + b + c) // 3 != dd else dd - 10, "The fourth angle isn't the average of the others.")]
    return _numeric_mc(rng, prompt, val, ds, subskill="triangle_angles" if d == "hard" else "parallel_lines", explanation=expl, tags=["geometry", "angles", "pairs"], est=65 if d == "easy" else 85, verify=f"val={val}")


# --------------------------------------------------------------------------- #
# sequences
# --------------------------------------------------------------------------- #
def sq_arithmetic_term(rng, d):
    """nth term of an arithmetic sequence (list -> formula -> two given terms)."""
    a1 = rng.randint(-20, 30)
    dd = rng.choice([v for v in range(-9, 13) if v])
    if d == "easy":
        n = rng.randint(6, 15)
        terms = ", ".join(str(a1 + k * dd) for k in range(4))
        val = a1 + (n - 1) * dd
        prompt = rng.choice([f"The first four terms of an arithmetic sequence are {terms}, … What is the {_ordinal(n)} term?",
                             f"An arithmetic sequence begins {terms}, … What is the value of the {_ordinal(n)} term of the sequence?"])
        expl = f"The common difference is {_m(dd)}; a_n = a₁ + (n − 1)d = {_m(a1)} + {n - 1}·({_m(dd)}) = {_m(val)}."
        ds = [(a1 + n * dd, "Use (n − 1), not n, as the multiplier."), (a1 + (n - 2) * dd, "That is the {0} term.".format(_ordinal(n - 1))), (n * dd, "Start from the first term, {0}.".format(_m(a1))), (a1 * n if a1 * n != val else val + dd + 1, "Add the common difference repeatedly; don't multiply the first term.")]
    elif d == "medium":
        n = rng.randint(10, 40)
        val = a1 + (n - 1) * dd
        prompt = f"An arithmetic sequence has first term {_m(a1)} and common difference {_m(dd)}. What is the {_ordinal(n)} term?"
        expl = f"a_n = a₁ + (n − 1)d = {_m(a1)} + ({n} − 1)({_m(dd)}) = {_m(val)}."
        ds = [(a1 + n * dd, "Use n − 1 = {0} steps from the first term.".format(n - 1)), (a1 + (n - 2) * dd, "There are n − 1 = {0} steps, not {1}.".format(n - 1, n - 2)), ((a1 + dd) * (n - 1) if (a1 + dd) * (n - 1) != val else val + 2, "Add (n − 1)d to a₁; don't multiply."), (val - dd + 1, "Arithmetic slip.")]
    else:
        p, q = sorted(rng.sample(range(2, 30), 2))
        ap_, aq = a1 + (p - 1) * dd, a1 + (q - 1) * dd
        n = rng.choice([v for v in range(2, 50) if v not in (p, q)])
        val = a1 + (n - 1) * dd
        prompt = f"In an arithmetic sequence, the {_ordinal(p)} term is {_m(ap_)} and the {_ordinal(q)} term is {_m(aq)}. What is the {_ordinal(n)} term?"
        expl = f"d = ({_m(aq)} − ({_m(ap_)}))/({q} − {p}) = {_m(dd)}; a₁ = {_m(ap_)} − {p - 1}·({_m(dd)}) = {_m(a1)}; a_{n} = {_m(a1)} + {n - 1}·({_m(dd)}) = {_m(val)}."
        ds = [(ap_ + (n - p) * dd + dd, "From the {0} term there are n − {1} = {2} steps.".format(_ordinal(p), p, n - p)), (a1 + n * dd, "Use n − 1 steps from the first term."), (ap_ + (n - p) * (aq - ap_), "Divide the difference of terms by the number of steps between them to get d."), (val + dd, "Arithmetic slip.")]
    return _numeric_mc(rng, prompt, val, ds, subskill="arithmetic", explanation=expl, tags=["sequences", "arithmetic"], est=75 if d == "easy" else 95, verify=f"a1={a1},d={dd},val={val}")


def sq_geometric_term(rng, d):
    """Geometric sequences: next term / nth term / common ratio."""
    a1 = rng.choice([1, 2, 3, 4, 5, 6, 8, 10, 12, 20, 25, 32, 50, 64, 81, 96, 100, 128, 243, 256, 500, 729, 1024])
    r = rng.choice([2, 3, Fraction(1, 2), Fraction(1, 3), -2, 4, Fraction(3, 2), Fraction(2, 3), 5, 10, -3])
    if d == "easy":
        r = rng.choice([2, 3, 4, 5, 10, -2])
        a1 = rng.randint(1, 12)
        n = rng.randint(5, 8) if abs(r) <= 3 else rng.randint(4, 6)
        terms = ", ".join(num_str(a1 * r ** k) for k in range(4))
        val = a1 * r ** (n - 1)
        prompt = f"The first four terms of a geometric sequence are {terms}, … What is the {_ordinal(n)} term?"
        expl = f"The common ratio is {_m(r)}; a_n = a₁·r^(n−1) = {a1}·({_m(r)})^{n - 1} = {_m(val)}."
        ds = [(a1 * r ** n, "Use the exponent n − 1, not n."), (a1 * r ** (n - 2), "That is the {0} term.".format(_ordinal(n - 1))), (a1 + (n - 1) * r, "A geometric sequence multiplies; it doesn't add the ratio."), (a1 * r * (n - 1), "Multiply by r repeatedly: r^(n−1).")]
        sub = "geometric"
    elif d == "medium":
        terms = [a1 * r ** k for k in range(4)]
        if any(isinstance(t, Fraction) and t.denominator != 1 for t in terms[:3]):
            terms = [a1 * r ** k for k in range(4)]
        shown = ", ".join(num_str(t) for t in terms[:3])
        if rng.random() < 0.5:
            prompt = f"A geometric sequence begins {shown}, … What is the common ratio of the sequence?"
            val = r
            expl = f"Divide any term by the previous term: {num_str(terms[1])} ÷ {num_str(terms[0])} = {num_str(r)}."
            ds = [(1 / r, "Divide the later term by the earlier one, not the reverse."), (terms[1] - terms[0], "The ratio is a quotient, not a difference."), (r + 1, "Arithmetic slip."), (-r, "Check the sign of the ratio.")]
        else:
            prompt = f"A geometric sequence begins {shown}, … What is the next term?"
            val = terms[3]
            expl = f"The common ratio is {num_str(r)}; {num_str(terms[2])} × {num_str(r)} = {num_str(val)}."
            ds = [(terms[2] + (terms[2] - terms[1]), "Multiply by the ratio; don't add the last difference."), (terms[2] * r * r, "That is two terms ahead."), (terms[2] + r, "Multiply by r; don't add it."), (-terms[3] if val else terms[3] + 1, "Check the sign.")]
        sub = "geometric"
    else:
        r = rng.choice([2, 3, Fraction(1, 2), Fraction(1, 3), -2, Fraction(3, 2), 4, 5])
        a1 = rng.choice([1, 2, 3, 4, 6, 8, 16, 32, 64, 81, 243, 96, 128])
        p, q = sorted(rng.sample(range(2, 7), 2))
        ap_, aq = a1 * r ** (p - 1), a1 * r ** (q - 1)
        n = rng.choice([v for v in range(1, 9) if v not in (p, q)])
        val = a1 * r ** (n - 1)
        if isinstance(ap_, Fraction) and ap_.denominator > 64 or isinstance(aq, Fraction) and aq.denominator > 64:
            return sq_geometric_term(rng, d)
        prompt = f"In a geometric sequence with positive ratio, the {_ordinal(p)} term is {num_str(ap_)} and the {_ordinal(q)} term is {num_str(aq)}. What is the {_ordinal(n)} term?" if r > 0 else \
                 f"In a geometric sequence, the {_ordinal(p)} term is {num_str(ap_)} and the {_ordinal(q)} term is {num_str(aq)}, and the ratio is negative. What is the {_ordinal(n)} term?"
        def par(v):  # (81/16)/(81/4), not the ambiguous 81/16/81/4
            return f"({num_str(v)})" if isinstance(v, Fraction) and v.denominator != 1 else num_str(v)
        expl = f"r^({q} − {p}) = {par(aq)}/{par(ap_)} = {num_str(aq / ap_)}, so r = {num_str(r)}; a₁ = {num_str(a1)}; a_{n} = {num_str(a1)}·({num_str(r)})^{n - 1} = {num_str(val)}."
        ds = [(a1 * r ** n, "Use the exponent n − 1."), (ap_ * r ** (n - p) * r if n != p else val * r, "From the {0} term there are n − {1} steps.".format(_ordinal(p), p)), (ap_ + (n - p) * (aq - ap_) / (q - p), "That treats the sequence as arithmetic."), (val * r if val * r != val else val + 1, "Off by one step.")]
        sub = "geometric"
    return _numeric_mc(rng, prompt, val, ds, subskill=sub, explanation=expl, tags=["sequences", "geometric"], est=80 if d == "easy" else 100, verify=f"a1={num_str(a1)},r={num_str(r)},val={num_str(val)}")


def sq_sum(rng, d):
    """Sum of the first n terms (arithmetic), finite geometric sum (hard)."""
    if d != "hard":
        a1 = rng.randint(-10, 30) if d == "medium" else rng.randint(1, 20)
        dd = rng.choice([v for v in range(1, 10)]) if d == "easy" else rng.choice([v for v in range(-8, 12) if v])
        n = rng.randint(5, 12) if d == "easy" else rng.randint(10, 40)
        an = a1 + (n - 1) * dd
        val = n * (a1 + an) // 2
        if d == "easy":
            prompt = f"What is the sum of the first {n} terms of the arithmetic sequence {a1}, {a1 + dd}, {a1 + 2 * dd}, …?"
        else:
            prompt = rng.choice([f"An arithmetic sequence has first term {_m(a1)} and common difference {_m(dd)}. What is the sum of its first {n} terms?",
                                 f"What is the sum of the first {n} terms of an arithmetic sequence whose first term is {_m(a1)} and whose {_ordinal(n)} term is {_m(an)}?"])
        expl = f"The {_ordinal(n)} term is {_m(an)}; S_n = n(a₁ + a_n)/2 = {n}({_m(a1)} + ({_m(an)}))/2 = {_m(val)}."
        ds = [(n * an, "Average the first and last terms before multiplying by n."), (n * (a1 + an), "Divide by 2."), (an, "That is the last term, not the sum."), (n * (a1 + a1 + n * dd) // 2, "The last term is a₁ + (n − 1)d, not a₁ + nd.")]
        return _numeric_mc(rng, prompt, val, ds, subskill="series", explanation=expl, tags=["sequences", "series"], est=85 if d == "easy" else 95, verify=f"S={val}")
    a1 = rng.choice([1, 2, 3, 4, 5, 6, 8, 10])
    r = rng.choice([2, 3, 4, 5, Fraction(1, 2), Fraction(1, 3)])
    n = rng.randint(4, 7) if r in (2, 3, Fraction(1, 2), Fraction(1, 3)) else rng.randint(3, 5)
    val = a1 * (r ** n - 1) / (r - 1)
    terms = ", ".join(num_str(a1 * r ** k) for k in range(3))
    prompt = f"What is the sum of the first {n} terms of the geometric sequence {terms}, …?"
    expl = f"S_n = a₁(rⁿ − 1)/(r − 1) with a₁ = {a1}, r = {num_str(r)}, n = {n}: {num_str(val)}."
    ds = [(a1 * r ** (n - 1), "That is the {0} term, not the sum.".format(_ordinal(n))), (a1 * (r ** (n - 1) - 1) / (r - 1), "That sums only {0} terms.".format(n - 1)), (a1 * (r ** (n + 1) - 1) / (r - 1), "That sums {0} terms.".format(n + 1)), (n * a1 * r, "Geometric terms don't all equal a₁r.")]
    return _numeric_mc(rng, prompt, val, ds, subskill="series", explanation=expl, tags=["sequences", "series", "geometric"], est=105, qtype="multi_step_math", verify=f"S={num_str(val)}")


def sq_recursive(rng, d):
    """Recursive definitions: evaluate terms / identify the rule."""
    if d == "easy":
        a1 = rng.randint(1, 15)
        k, c = rng.choice([1, 2, 3]), rng.choice([v for v in range(-6, 10) if v])
        if k == 1 and c == 0:
            c = 3
        terms = [a1]
        for _ in range(5):
            terms.append(k * terms[-1] + c)
        rule = f"a_n = {k if k != 1 else ''}a_(n−1) {_pm(c)}".replace("a_n = a_(n−1)", "a_n = a_(n−1)")
        n = rng.choice([3, 4, 5])
        val = terms[n - 1]
        prompt = f"A sequence is defined by a₁ = {a1} and {rule} for n ≥ 2. What is the value of a_{n}?"
        expl = "Compute term by term: " + ", ".join(f"a_{i + 1} = {_m(t)}" for i, t in enumerate(terms[:n])) + "."
        ds = [(terms[n], "That is a_{0}; stop one term earlier.".format(n + 1)), (terms[n - 2], "That is a_{0}; apply the rule once more.".format(n - 1)), (k * a1 * (n - 1) + c if k * a1 * (n - 1) + c != val else val + 1, "Apply the rule to each previous term in turn."), (a1 + (n - 1) * c if k != 1 else a1 * n + c, "Follow the rule exactly (multiply then add).")]
    elif d == "medium":
        a1, a2 = rng.randint(1, 9), rng.randint(1, 12)
        terms = [a1, a2]
        kind = rng.choice(["sum", "diff", "prod"])
        for _ in range(5):
            if kind == "sum":
                terms.append(terms[-1] + terms[-2])
            elif kind == "diff":
                terms.append(terms[-1] - terms[-2])
            else:
                terms.append(terms[-1] * 2 - terms[-2])
        rule = {"sum": "a_n = a_(n−1) + a_(n−2)", "diff": "a_n = a_(n−1) − a_(n−2)", "prod": "a_n = 2a_(n−1) − a_(n−2)"}[kind]
        n = rng.choice([4, 5, 6])
        val = terms[n - 1]
        prompt = f"A sequence is defined by a₁ = {a1}, a₂ = {a2}, and {rule} for n ≥ 3. What is a_{n}?"
        expl = "Term by term: " + ", ".join(f"a_{i + 1} = {_m(t)}" for i, t in enumerate(terms[:n])) + "."
        ds = [(terms[n], "That is a_{0}.".format(n + 1)), (terms[n - 2], "That is a_{0}.".format(n - 1)), (val + a1, "Arithmetic slip; recompute each term from the two before it."), (terms[n - 1] + terms[n - 2] if kind != "sum" else terms[n - 1] - terms[n - 2], "Apply the rule exactly as written.")]
    else:
        a1 = rng.randint(-5, 10)
        dd = rng.choice([v for v in range(-6, 8) if v])
        rr = rng.choice([2, 3, Fraction(1, 2), -2])
        kind = rng.choice(["arith", "geo"])
        if kind == "arith":
            seq = [a1 + k * dd for k in range(4)]
            correct = f"a₁ = {_m(a1)}, a_n = a_(n−1) {_pm(dd)}"
            ds = [(f"a₁ = {_m(a1)}, a_n = {_m(dd)}·a_(n−1)", "Multiplying by {0} would make the sequence geometric.".format(_m(dd))), (f"a₁ = {_m(a1)}, a_n = a_(n−1) {_pm(-dd)}", "The terms change by {0} each step, so the sign is wrong.".format(_m(dd))), (f"a₁ = {_m(a1 + dd)}, a_n = a_(n−1) {_pm(dd)}", "The first term is {0}, not {1}.".format(_m(a1), _m(a1 + dd))), (f"a₁ = {_m(a1)}, a_n = a_(n−1) + n·{_m(dd)}" if dd > 0 else f"a₁ = {_m(a1)}, a_n = a_(n−1) + n·({_m(dd)})", "The difference is constant, not growing with n.")]
            expl = f"Each term is the previous term plus {_m(dd)}: {correct}."
        else:
            a1 = rng.choice([1, 2, 3, 4, 8, 16, 32, 64, 5, 10])
            seq = [a1 * rr ** k for k in range(4)]
            correct = f"a₁ = {num_str(a1)}, a_n = {num_str(rr)}·a_(n−1)"
            ds = [(f"a₁ = {num_str(a1)}, a_n = a_(n−1) + {num_str(seq[1] - seq[0])}", "The differences are not constant; the ratio is."), (f"a₁ = {num_str(a1)}, a_n = {num_str(1 / rr)}·a_(n−1)", "The ratio is later ÷ earlier = {0}.".format(num_str(rr))), (f"a₁ = {num_str(seq[1])}, a_n = {num_str(rr)}·a_(n−1)", "The first term is {0}.".format(num_str(a1))), (f"a₁ = {num_str(a1)}, a_n = a_(n−1)^{num_str(rr)}" if rr in (2, 3) else f"a₁ = {num_str(a1)}, a_n = {num_str(-rr)}·a_(n−1)", "Check the rule against the given terms.")]
            expl = f"Each term is {num_str(rr)} times the previous: {correct}."
        prompt = f"Which of the following recursive definitions produces the sequence {', '.join(num_str(t) for t in seq)}, …?"
        return _text_mc(rng, prompt, correct, ds, subskill="recursive", explanation=expl, tags=["sequences", "recursive"], est=90, verify=correct)
    return _numeric_mc(rng, prompt, val, ds, subskill="recursive", explanation=expl, tags=["sequences", "recursive"], est=80 if d == "easy" else 90, verify=f"val={val}")


def sq_which_term(rng, d):
    """Which term equals a value / common difference from two terms / word context."""
    a1 = rng.randint(-10, 40)
    dd = rng.choice([v for v in range(2, 12)])
    if d == "easy":
        n = rng.randint(5, 25)
        target = a1 + (n - 1) * dd
        prompt = f"In the arithmetic sequence {_m(a1)}, {_m(a1 + dd)}, {_m(a1 + 2 * dd)}, …, which term has the value {_m(target)}?"
        val = n
        expl = f"{_m(target)} = {_m(a1)} + (n − 1)·{dd} → n − 1 = {n - 1} → n = {n}; it is the {_ordinal(n)} term."
        ds = [(n - 1, "That is n − 1; add 1."), (n + 1, "Arithmetic slip."), (Fraction(target, dd) if target % dd == 0 else n + 2, "Subtract a₁ first."), (target, "That is the value, not the position.")]
        sub = "arithmetic"
    elif d == "medium":
        p, q = sorted(rng.sample(range(2, 25), 2))
        ap_, aq = a1 + (p - 1) * dd, a1 + (q - 1) * dd
        prompt = f"In an arithmetic sequence, the {_ordinal(p)} term is {_m(ap_)} and the {_ordinal(q)} term is {_m(aq)}. What is the common difference?"
        val = dd
        expl = f"d = ({_m(aq)} − ({_m(ap_)}))/({q} − {p}) = {aq - ap_}/{q - p} = {dd}."
        ds = [(aq - ap_, "Divide the difference by the number of steps, {0}.".format(q - p)), (Fraction(aq - ap_, q), "There are {0} − {1} = {2} steps between the terms.".format(q, p, q - p)), (Fraction(aq - ap_, q - p + 1), "Steps between the {0} and {1} terms: {2}.".format(_ordinal(p), _ordinal(q), q - p)), (dd + 1, "Arithmetic slip.")]
        sub = "arithmetic"
    else:
        n = rng.randint(8, 30)
        ctx = rng.choice([("A theater has {a1} seats in the first row, and each row after the first has {dd} more seats than the row before it. How many seats are in the {nth} row?", "rows"),
                          ("A stack of logs has {a1} logs in the top layer, and each layer below has {dd} more logs than the layer above. How many logs are in the {nth} layer from the top?", "layers"),
                          ("{name} saves ${a1} in the first week and increases the amount saved by ${dd} every week. How much does {name} save in the {nth} week?", "weeks")])
        a1 = rng.randint(5, 30)
        prompt = ctx[0].format(a1=a1, dd=dd, nth=_ordinal(n), name=rng.choice(NAMES))
        val = a1 + (n - 1) * dd
        expl = f"This is arithmetic with a₁ = {a1}, d = {dd}: a_{n} = {a1} + ({n} − 1)·{dd} = {val}."
        ds = [(a1 + n * dd, "Use n − 1 = {0} increases.".format(n - 1)), (n * (a1 + val) // 2, "That is the total of all {0} {1}, not the {2}.".format(n, ctx[1], _ordinal(n))), (a1 * n, "Add {0} repeatedly; don't multiply the first value by n.".format(dd)), (val - dd, "That is the {0} value.".format(_ordinal(n - 1)))]
        sub = "arithmetic"
    return _numeric_mc(rng, prompt, val, ds, subskill=sub, explanation=expl, tags=["sequences", "arithmetic"], est=80 if d != "hard" else 95, verify=f"val={val}")


# --------------------------------------------------------------------------- #
# logarithms
# --------------------------------------------------------------------------- #
def lg_evaluate(rng, d):
    """Evaluate log_b(x): integer (easy), fractional/negative (medium), expression (hard)."""
    if d == "easy":
        b = rng.choice([2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 15, 20])
        e = rng.randint(1, 8 if b <= 3 else 5 if b <= 5 else 3)
        x = b ** e
        prompt = rng.choice([f"What is the value of log_{b}({x})?", f"log_{b} {x} = ?",
                             f"What is log_{b}({x})?"]) if b != 10 else rng.choice([f"What is the value of log({x})? (log denotes the base-10 logarithm.)", f"What is log₁₀({x})?"])
        val = e
        expl = f"log_{b}({x}) asks: {b} to what power is {x}? Since {b}^{e} = {x}, the answer is {e}."
        ds = [(x // b, "A logarithm is an exponent, not a quotient."), (e + 1, "Count the factors of {0} in {1}.".format(b, x)), (e - 1 if e > 1 else e + 2, "Count the factors of {0} in {1}.".format(b, x)), (b * e, "The answer is the exponent itself.")]
    elif d == "medium":
        kind = rng.choice(["neg", "frac", "one", "self"])
        b = rng.choice([2, 3, 4, 5, 10])
        if kind == "neg":
            e = rng.randint(1, 3)
            val = -e
            prompt = f"What is the value of log_{b}(1/{b ** e})?"
            expl = f"1/{b ** e} = {b}^(−{e}), so the logarithm is −{e}."
            ds = [(e, "1/{0} is {1} to a negative power.".format(b ** e, b)), (Fraction(1, e), "The exponent is −{0}, not its reciprocal.".format(e)), (Fraction(-1, b ** e), "The log is the exponent, −{0}.".format(e)), (-e - 1, "Count the factors of {0}.".format(b))]
        elif kind == "frac":
            b, x, val = rng.choice([(4, 8, Fraction(3, 2)), (8, 4, Fraction(2, 3)), (9, 27, Fraction(3, 2)), (27, 9, Fraction(2, 3)), (4, 2, Fraction(1, 2)), (9, 3, Fraction(1, 2)), (16, 8, Fraction(3, 4)), (8, 16, Fraction(4, 3)), (25, 5, Fraction(1, 2)), (16, 2, Fraction(1, 4)), (32, 8, Fraction(3, 5)), (4, 32, Fraction(5, 2)), (100, 10, Fraction(1, 2)), (1000, 100, Fraction(2, 3))])
            prompt = f"What is the value of log_{b}({x})?"
            expl = f"{b}^({num_str(val)}) = {x}, so log_{b}({x}) = {num_str(val)}."
            ds = [(1 / val, "This inverts the exponent: check {0}^({1}) = {2}.".format(b, num_str(val), x)), (Fraction(x, b), "A logarithm is an exponent, not a quotient."), (val + 1, "Write both as powers of a common base."), (-val, "The exponent is positive here.")]
        elif kind == "one":
            prompt = f"What is the value of log_{b}(1) + log_{b}({b})?"
            val = 1
            expl = f"log_{b}(1) = 0 (since {b}⁰ = 1) and log_{b}({b}) = 1; the sum is 1."
            ds = [(0, "log_b(b) = 1, not 0."), (2, "log_b(1) = 0, not 1."), (b, "Each logarithm is an exponent: 0 and 1."), (b + 1, "Logs are exponents, not the arguments.")]
        else:
            k = rng.randint(2, 9)
            prompt = f"What is the value of {b}^(log_{b}({k}))?"
            val = k
            expl = f"Raising {b} to log_{b}({k}) undoes the logarithm: the result is {k}."
            ds = [(b, "b^(log_b x) = x, not b."), (k * b, "The exponential and log cancel exactly."), (1, "The answer is the argument of the log."), (k + 1, "Arithmetic slip.")]
    else:
        b = rng.choice([2, 3, 5, 10])
        m = rng.randint(1, 4)
        n = rng.choice([v for v in range(1, 4) if v != m])
        x, y = b ** m, b ** n
        op = rng.choice(["+", "−"])
        val = m + n if op == "+" else m - n
        prompt = f"What is the value of log_{b}({x}) {op} log_{b}({y})?" if rng.random() < 0.5 else (f"What is the value of log_{b}({x * y})?" if op == "+" else f"What is the value of log_{b}({x}/{y})?")
        expl = f"log_{b}({x}) = {m} and log_{b}({y}) = {n}; {m} {op} {n} = {_m(val)}." if "(" + str(x) + ")" in prompt else (f"{x * y} = {b}^{m + n}, so the logarithm is {m + n}." if op == "+" else f"{x}/{y} = {b}^{m - n}, so the logarithm is {_m(val)}.")
        ds = [(m * n if op == "+" else Fraction(m, n), "Logs of a product add; logs of a quotient subtract (exponents, not multiply/divide)."), (m - n if op == "+" else m + n, "Check the operation."), (x * y if op == "+" else Fraction(x, y), "That is the argument, not the logarithm."), (val + 1, "Arithmetic slip.")]
    return _numeric_mc(rng, prompt, val, ds, subskill="evaluate", explanation=expl, tags=["logarithms", "evaluate"], est=70 if d == "easy" else 85, verify=f"val={num_str(val)}")


def lg_convert(rng, d):
    """Convert between exponential and logarithmic forms (text options)."""
    b = rng.choice([2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12])
    e = rng.randint(2, 6 if b <= 3 else 4 if b <= 5 else 3)
    x = b ** e
    if d == "easy":
        prompt = rng.choice([f"Which of the following is equivalent to {b}^{e} = {x}?",
                             f"The equation {b}^{e} = {x} can be rewritten in logarithmic form as which of the following?",
                             f"Which logarithmic equation expresses the same relationship as {b}^{e} = {x}?"])
        correct = f"log_{b}({x}) = {e}"
        ds = [(f"log_{e}({x}) = {b}", "The base of the power is the base of the log."), (f"log_{b}({e}) = {x}", "The argument of the log is the result {0}; the log equals the exponent.".format(x)), (f"log_{x}({b}) = {e}", "The base of the log is {0}.".format(b)), (f"log_{b}({x}) = {x // b}", "The logarithm equals the exponent, {0}.".format(e))]
        expl = f"b^y = x means log_b(x) = y: {correct}."
        if not _distinct(correct, ds):
            return lg_convert(rng, d)
    elif d == "medium":
        prompt = rng.choice([f"Which of the following is equivalent to log_{b}({x}) = {e}?",
                             f"The equation log_{b}({x}) = {e} is equivalent to which of the following?",
                             f"Which exponential equation expresses the same relationship as log_{b}({x}) = {e}?"])
        correct = f"{b}^{e} = {x}"
        ds = [(f"{e}^{b} = {x}", "The base of the log becomes the base of the power."), (f"{b}^{x} = {e}", "The log's value is the exponent."), (f"{x}^{e} = {b}", "The argument {0} is the result of the power.".format(x)), (f"{b} · {e} = {x}", "A logarithm is an exponent, not a factor.")]
        expl = f"log_b(x) = y means b^y = x: {correct}."
    else:
        kind = rng.choice(["frac", "var"])
        if kind == "frac":
            b, x, val = rng.choice([(4, 8, "3/2"), (8, 4, "2/3"), (9, 27, "3/2"), (27, 9, "2/3"), (16, 8, "3/4"), (25, 125, "3/2"), (4, 32, "5/2"), (32, 4, "2/5")])
            prompt = f"Which of the following is equivalent to {b}^({val}) = {x}?"
            correct = f"log_{b}({x}) = {val}"
            p, q = val.split("/")
            ds = [(f"log_{b}({x}) = {q}/{p}", "The log equals the exponent {0}, not its reciprocal.".format(val)), (f"log_{x}({b}) = {val}", "The base of the power is the base of the log."), (f"log_{b}({val}) = {x}", "The argument is {0}.".format(x)), (f"log_{b}({x}) = {b}", "The log is the exponent {0}.".format(val))]
            expl = f"b^y = x ⇔ log_b(x) = y, so {correct}."
        else:
            k = rng.randint(2, 9)
            prompt = f"If log_{b}(y) = {k}, which of the following gives y?"
            correct = f"y = {b}^{k}"
            ds = [(f"y = {k}^{b}", "The log's base is the base of the power."), (f"y = {b}·{k}", "A logarithm is an exponent."), (f"y = {k}/{b}", "Rewrite as a power: y = {0}^{1}.".format(b, k)), (f"y = {b}^(1/{k})", "The exponent is {0}, not 1/{0}.".format(k))]
            expl = f"log_{b}(y) = {k} means {b}^{k} = y."
    return _text_mc(rng, prompt, correct, ds, subskill="convert_forms", explanation=expl, tags=["logarithms", "convert"], est=70 if d != "hard" else 85, verify=correct)


def lg_properties(rng, d):
    """Product/quotient/power rules (text), evaluate with given logs (numeric)."""
    if d == "easy":
        kind = rng.choice(["prod", "quot", "pow"])
        b = rng.choice(["", "_2", "_3", "_5"])
        L = f"log{b}"
        if kind == "prod":
            p, q = rng.sample(["x", "y", "a", "m", "n", "p"], 2)
            prompt = f"Which of the following is equivalent to {L}({p}{q}) for positive {p} and {q}?"
            correct = f"{L}({p}) + {L}({q})"
            ds = [(f"{L}({p}) · {L}({q})", "The log of a product is a SUM of logs."), (f"{L}({p}) − {L}({q})", "Subtraction is for a quotient."), (f"{L}({p} + {q})", "The log of a product is not the log of a sum."), (f"{L}({p})^{L}({q})" if False else f"({L}({p}))({L}({q})) / 2", "Logs of products add.")]
            expl = f"Product rule: log(pq) = log p + log q."
        elif kind == "quot":
            p, q = rng.sample(["x", "y", "a", "m", "n", "p"], 2)
            prompt = f"Which of the following is equivalent to {L}({p}/{q}) for positive {p} and {q}?"
            correct = f"{L}({p}) − {L}({q})"
            ds = [(f"{L}({p}) / {L}({q})", "The log of a quotient is a DIFFERENCE of logs."), (f"{L}({p}) + {L}({q})", "Addition is for a product."), (f"{L}({p} − {q})", "The log of a quotient is not the log of a difference."), (f"{L}({q}) − {L}({p})", "The order matters: numerator minus denominator.")]
            expl = f"Quotient rule: log(p/q) = log p − log q."
        else:
            p = rng.choice(["x", "y", "a", "m"])
            k = rng.randint(2, 7)
            prompt = f"Which of the following is equivalent to {L}({p}^{k}) for positive {p}?"
            correct = f"{k}·{L}({p})"
            ds = [(f"({L}({p}))^{k}", "The exponent comes out front as a factor."), (f"{L}({k}{p})", "The power rule moves the exponent, not into a coefficient inside."), (f"{L}({p}) + {k}", "The exponent multiplies the log; it isn't added."), (f"{L}({p})/{k}", "Multiply by {0}, don't divide.".format(k))]
            expl = f"Power rule: log(p^k) = k·log p."
        return _text_mc(rng, prompt, correct, ds, subskill="properties", explanation=expl, tags=["logarithms", "properties"], est=65, verify=correct)
    if d == "medium":
        logs = {2: 0.30, 3: 0.48, 5: 0.70, 7: 0.85, 11: 1.04, 13: 1.11}
        pa, pb = sorted(rng.sample(list(logs), 2))
        a, b = logs[pa], logs[pb]
        kind = rng.choice(["prod", "quot", "pow", "pow2"])
        if kind == "prod":
            prompt = f"If log {pa} ≈ {a} and log {pb} ≈ {b}, what is the approximate value of log {pa * pb}?"
            val = round(a + b, 2)
            expl = f"log({pa}·{pb}) = log {pa} + log {pb} ≈ {a} + {b} = {val}."
            ds = [(round(a * b, 3), "Logs of a product add."), (round(b - a, 2), "Subtraction is for a quotient."), (round(a + b + 0.1, 2), "Arithmetic slip."), (round((a + b) / 2, 2), "Add; don't average.")]
        elif kind == "quot":
            prompt = f"If log {pa} ≈ {a} and log {pb} ≈ {b}, what is the approximate value of log({pb}/{pa})?"
            val = round(b - a, 2)
            expl = f"log({pb}/{pa}) = log {pb} − log {pa} ≈ {b} − {a} = {val}."
            ds = [(round(b / a, 2), "Logs of a quotient subtract."), (round(a + b, 2), "Addition is for a product."), (round(a - b, 2), "Numerator minus denominator."), (round(b - a + 0.1, 2), "Arithmetic slip.")]
        elif kind == "pow":
            k = rng.randint(2, 6)
            prompt = f"If log {pa} ≈ {a}, what is the approximate value of log {pa ** k}?"
            val = round(k * a, 2)
            expl = f"{pa ** k} = {pa}^{k}, so log {pa ** k} = {k}·log {pa} ≈ {val}."
            ds = [(round(a ** k, 3), "The exponent multiplies the log; don't raise the log to the power."), (round(a + k, 2), "Multiply by {0}; don't add.".format(k)), (round((k + 1) * a, 2), "Check the exponent: {0} = {1}^{2}.".format(pa ** k, pa, k)), (round(a, 2), "The argument is {0}, not {1}.".format(pa ** k, pa))]
        else:
            prompt = f"If log {pa} ≈ {a}, what is the approximate value of log({pa * 10})?"
            val = round(a + 1, 2)
            expl = f"log({pa}·10) = log {pa} + log 10 = {a} + 1 = {val}."
            ds = [(round(a * 10, 2), "log(10x) = log x + 1, not 10·log x."), (round(a, 2), "Multiplying by 10 adds 1 to a base-10 log."), (round(a + 10, 2), "log 10 = 1."), (round(a + 2, 2), "Arithmetic slip.")]
        return _numeric_mc(rng, prompt, val, ds, subskill="properties", explanation=expl, tags=["logarithms", "properties"], est=85, verify=f"val={val}")
    b = rng.choice([2, 3, 5, 10])
    L = f"log_{b}" if b != 10 else "log"
    p, q = rng.sample(["x", "y", "a", "m", "n"], 2)
    k, j = rng.randint(2, 5), rng.randint(2, 4)
    kind = rng.choice(["expand", "condense"])
    if kind == "expand":
        prompt = f"Which of the following is equivalent to {L}({p}^{k}/{q}^{j}) for positive {p} and {q}?"
        correct = f"{k}·{L}({p}) − {j}·{L}({q})"
        ds = [(f"{k}·{L}({p}) + {j}·{L}({q})", "A quotient gives a difference of logs."), (f"{L}({p}^{k}) · {L}({q}^{j})" if False else f"({k}/{j})·{L}({p}/{q})", "Each exponent applies to its own log."), (f"{k}·{L}({p}) / ({j}·{L}({q}))", "Quotient inside becomes subtraction outside, not division."), (f"{j}·{L}({q}) − {k}·{L}({p})", "Numerator minus denominator.")]
        expl = f"log(p^k/q^j) = log(p^k) − log(q^j) = {correct}."
    else:
        prompt = f"Which of the following is equivalent to {k}·{L}({p}) + {L}({q}) − {L}({p}) for positive {p} and {q}?"
        correct = f"{L}({p}^{k - 1}·{q})" if k - 1 != 1 else f"{L}({p}{q})"
        ds = [(f"{L}({p}^{k}·{q}/{p})" if False else f"{L}({p}^{k}{q}) − {L}({p})" if False else f"{L}({p}^{k} + {q} − {p})", "Sums of logs become products, not sums of arguments."), (f"{L}({p}^{k}·{q})", "The −log({0}) term divides by {0}, lowering the exponent.".format(p)), (f"{L}({p}^{k - 1} + {q})", "Adding logs multiplies the arguments."), (f"{k - 1}·{L}({p}{q})", "Only {0} carries the exponent {1}.".format(p, k - 1))]
        expl = f"Combine: {k}·log p − log p = {k - 1}·log p = log(p^{k - 1}); adding log q gives {correct}."
    return _text_mc(rng, prompt, correct, ds, subskill="properties", explanation=expl, tags=["logarithms", "properties"], est=90, verify=correct)


def lg_solve(rng, d):
    """Solve exponential / logarithmic equations."""
    b = rng.choice([2, 3, 4, 5, 6, 7, 8, 9, 10, 12])
    if d == "easy":
        e = rng.randint(2, 8 if b <= 3 else 4 if b <= 6 else 3)
        prompt = rng.choice([f"What is the solution to the equation {b}^x = {b ** e}?",
                             f"If {b}^x = {b ** e}, what is the value of x?",
                             f"For what value of x does {b}^x equal {b ** e}?"])
        val = e
        expl = f"{b ** e} = {b}^{e}, so x = {e}."
        ds = [(b ** e // b, "x is an exponent, not a quotient."), (e + 1, "Count the factors of {0}.".format(b)), (e - 1 if e > 1 else e + 2, "Count the factors of {0}.".format(b)), (b * e, "The answer is the exponent.")]
        sub = "solve_exponential"
    elif d == "medium":
        kind = rng.choice(["log_eq", "exp_shift", "exp_coef"])
        if kind == "log_eq":
            k = rng.randint(1, 4 if b <= 4 else 3)
            c = rng.choice([v for v in range(-9, 10) if v])
            val = b ** k - c
            prompt = f"What is the solution to log_{b}(x {_pm(c)}) = {k}?"
            expl = f"Rewrite: x {_pm(c)} = {b}^{k} = {b ** k}, so x = {_m(val)}."
            ds = [(b ** k, "Subtract {0} after rewriting.".format(_m(c))), (b * k - c, "{0}^{1} means {0} raised to the {1}, not {0}·{1}.".format(b, k)), (k - c, "Rewrite the log as a power first."), (b ** k + c, "Move {0} to the other side with the opposite sign.".format(_m(c)))]
        elif kind == "exp_shift":
            e = rng.randint(2, 5 if b <= 3 else 3)
            c = rng.choice([v for v in range(-4, 5) if v])
            val = e - c
            prompt = f"What is the solution to {b}^(x {_pm(c)}) = {b ** e}?"
            expl = f"{b ** e} = {b}^{e}, so x {_pm(c)} = {e} and x = {_m(val)}."
            ds = [(e, "Still solve x {0} = {1}.".format(_pm(c), e)), (e + c, "Subtract {0}; don't add.".format(_m(c))), (b ** e - c, "Match exponents first."), (-val if val else val + 1, "Sign slip.")]
        else:
            e = rng.randint(2, 6 if b <= 3 else 4)
            k = rng.choice([2, 3])
            if e % k:
                e = k * rng.randint(1, 2)
            val = e // k
            prompt = f"What is the solution to {b}^({k}x) = {b ** e}?"
            expl = f"{b ** e} = {b}^{e}, so {k}x = {e} and x = {val}."
            ds = [(e, "Divide by {0}.".format(k)), (e * k, "Divide by {0}; don't multiply.".format(k)), (val + 1, "Arithmetic slip."), (Fraction(b ** e, k), "Match the exponents first.")]
        sub = "solve_exponential"
    else:
        kind = rng.choice(["change_base", "log_both", "two_logs"])
        if kind == "change_base":
            b1, b2, e1, e2 = rng.choice([(4, 8, 2, 3), (8, 4, 3, 2), (9, 27, 2, 3), (27, 9, 3, 2), (4, 32, 2, 5), (16, 8, 4, 3), (25, 125, 2, 3), (32, 4, 5, 2), (8, 16, 3, 4), (125, 25, 3, 2)])
            k = rng.randint(1, 3)
            val = Fraction(e2, e1 * k)
            prompt = f"What is the solution to {b1}^({k}x) = {b2}?" if k > 1 else f"What is the solution to {b1}^x = {b2}?"
            common = {4: 2, 8: 2, 16: 2, 32: 2, 9: 3, 27: 3, 25: 5, 125: 5}[b1]
            expl = f"Write both sides with base {common}: {common}^({e1 * k}x) = {common}^{e2}, so x = {num_str(val)}."
            ds = [(1 / val, "This inverts the exponent ratio."), (Fraction(e2, k), "Account for {0} = {1}^{2}.".format(b1, common, e1)), (Fraction(b2, b1), "x is an exponent, not a quotient."), (val + 1, "Arithmetic slip.")]
        elif kind == "log_both":
            # 2^x = 10 -> x = log 10 / log 2 ... keep algebraic: x = log_b(c) with c given; options as expressions
            c = rng.choice([v for v in range(3, 30) if all(v != b ** k for k in range(1, 6))])
            prompt = f"Which of the following is the solution to {b}^x = {c}?"
            correct = f"x = log({c})/log({b})"
            ds = [(f"x = log({b})/log({c})", "Taking logs gives x·log({0}) = log({1}), so x = log({1})/log({0}).".format(b, c)), (f"x = log({c}) − log({b})", "Divide the logs; don't subtract."), (f"x = log({c}/{b})", "x = log c ÷ log b, not log(c ÷ b)."), (f"x = {c}/{b}", "x is an exponent; use logarithms.")]
            expl = f"Take the log of both sides: x·log {b} = log {c}, so {correct}."
            return _text_mc(rng, prompt, correct, ds, subskill="solve_exponential", explanation=expl, tags=["logarithms", "solve"], est=90, verify=correct)
        else:
            x = rng.randint(2, 12)
            k = rng.randint(1, 3)
            # log_b(x) + log_b(x + c) = log_b(product) -> simpler: log_b(kx) = log_b(m) ; use log_b(x) + log_b(k) = log_b(m)
            m = k * x
            prompt = f"What is the solution to log_{b}(x) + log_{b}({k}) = log_{b}({m})?" if k > 1 else f"What is the solution to log_{b}(x) − log_{b}({rng.randint(2, 5)}) = 0?"
            if k == 1:
                kk = int(prompt.split("log_{0}(".format(b))[2].split(")")[0])
                val = kk
                expl = f"log_{b}(x) = log_{b}({kk}), so x = {kk}."
                ds = [(0, "x itself is not 0; the logs are equal when the arguments are equal."), (b, "The base is {0}; the arguments must match.".format(b)), (kk + b, "Set the arguments equal."), (1, "log_b(x) = 0 only if x = 1, but here it equals log_b({0}).".format(kk))]
            else:
                val = x
                expl = f"log_{b}(x) + log_{b}({k}) = log_{b}({k}x), so {k}x = {m} and x = {x}."
                ds = [(m - k, "Logs add when arguments multiply: {0}x = {1}.".format(k, m)), (m, "Divide by {0}.".format(k)), (m * k, "Divide by {0}; don't multiply.".format(k)), (x + 1, "Arithmetic slip.")]
        sub = "solve_exponential"
    return _numeric_mc(rng, prompt, val, ds, subskill=sub, explanation=expl, tags=["logarithms", "solve"], est=70 if d == "easy" else 90, verify=f"x={num_str(val)}")


# --------------------------------------------------------------------------- #
# complex_numbers
# --------------------------------------------------------------------------- #
def _cx(a, b):
    """Render a + bi."""
    if b == 0:
        return _m(a)
    bi = "i" if b == 1 else "−i" if b == -1 else f"{_m(b)}i"
    if a == 0:
        return bi
    return f"{_m(a)} {'+' if b > 0 else '−'} {bi.lstrip('−')}"


def cx_powers(rng, d):
    """Powers of i."""
    cycle = {0: "1", 1: "i", 2: "−1", 3: "−i"}
    if d == "easy":
        n = rng.randint(2, 40)
    elif d == "medium":
        n = rng.randint(41, 160)
    else:
        n = rng.randint(100, 999)
    val = cycle[n % 4]
    if d == "hard" and rng.random() < 0.5:
        m = rng.randint(2, 40)
        prompt = f"What is the value of i^{n} + i^{m}?"
        a = {"1": 1, "i": 0, "−1": -1, "−i": 0}
        b = {"1": 0, "i": 1, "−1": 0, "−i": -1}
        s1, s2 = cycle[n % 4], cycle[m % 4]
        re, im = a[s1] + a[s2], b[s1] + b[s2]
        val = _cx(re, im) if (re, im) != (0, 0) else "0"
        expl = f"i^{n} = {s1} (since {n} ≡ {n % 4} mod 4) and i^{m} = {s2}; their sum is {val}."
        others = [v for v in ["0", "1", "−1", "i", "−i", "2", "−2", "2i", "−2i", "1 + i", "1 − i", "−1 + i", "−1 − i"] if v != val]
        ds = [(o, "Reduce each exponent modulo 4 and add the results.") for o in rng.sample(others, 4)]
        return _text_mc(rng, prompt, val, ds, subskill="powers_of_i", explanation=expl, tags=["complex", "powers-of-i"], est=85, verify=f"i^{n}+i^{m}={val}")
    prompt = rng.choice([f"What is the value of i^{n}, where i = √(−1)?", f"If i² = −1, what is i^{n}?", f"Which of the following is equal to i^{n}?"])
    expl = f"Powers of i cycle every 4: i, −1, −i, 1. Since {n} = 4·{n // 4} + {n % 4}, i^{n} = i^{n % 4} = {val}."
    others = [v for v in cycle.values() if v != val]
    ds = [(o, "Reduce the exponent modulo 4: i^{0} = i^{1}.".format(n, n % 4)) for o in others]
    ds.append(("0", "No power of i is 0."))
    return _text_mc(rng, prompt, val, ds, subskill="powers_of_i", explanation=expl, tags=["complex", "powers-of-i"], est=65 if d == "easy" else 75, verify=f"i^{n}={val}")


def cx_add_sub(rng, d):
    """Add / subtract complex numbers (easy/medium); simplify √ of negatives (hard)."""
    a, b = rng.choice([v for v in range(-9, 10) if v]), rng.choice([v for v in range(-9, 10) if v])
    c, e = rng.choice([v for v in range(-9, 10) if v]), rng.choice([v for v in range(-9, 10) if v])
    if d == "easy":
        prompt = f"What is the sum ({_cx(a, b)}) + ({_cx(c, e)})?"
        re, im = a + c, b + e
        correct = _cx(re, im) if (re, im) != (0, 0) else "0"
        ds = [(_cx(a + c, b * e) if (a + c, b * e) != (re, im) else _cx(re + 1, im), "Add the imaginary coefficients; don't multiply them."), (_cx(a - c, b - e) if (a - c, b - e) != (re, im) else _cx(re, im + 2), "This subtracts."), (_cx(a + c + b + e, 0) if a + c + b + e != re or im != 0 else _cx(re, im + 3), "Real and imaginary parts stay separate."), (_cx(re, -im) if im else _cx(re + 2, im), "Check the sign of the imaginary part.")]
        expl = f"Add real parts: {_m(a)} + {_m(c)} = {_m(re)}; add imaginary parts: {_m(b)} + {_m(e)} = {_m(im)}. Result: {correct}."
    elif d == "medium":
        prompt = f"What is ({_cx(a, b)}) − ({_cx(c, e)})?"
        re, im = a - c, b - e
        correct = _cx(re, im) if (re, im) != (0, 0) else "0"
        ds = [(_cx(a - c, b + e) if (a - c, b + e) != (re, im) else _cx(re + 1, im), "Distribute the minus sign to the imaginary part too."), (_cx(a + c, b + e) if (a + c, b + e) != (re, im) else _cx(re, im + 2), "This adds."), (_cx(c - a, e - b) if (c - a, e - b) != (re, im) else _cx(re + 3, im), "The order of subtraction is reversed."), (_cx(a - c, -(b - e)) if im else _cx(re + 2, im), "Check the sign of the imaginary part.")]
        expl = f"({_m(a)} − {_m(c)}) + ({_m(b)} − {_m(e)})i = {correct}."
    else:
        k = rng.randint(2, 12)
        r = rng.choice([2, 3, 5, 6, 7, 10, 11, 13, 14, 15, 17, 19, 21, 22, 23])
        n = k * k * r
        prompt = rng.choice([f"Which of the following is equivalent to √(−{n})?",
                             f"For i = √(−1), which expression equals √(−{n})?"])
        correct = f"{k}i√{r}"
        ds = [(f"−{k}√{r}", "√(−n) is imaginary, not negative."), (f"{k}√{r}", "The negative under the root produces a factor of i."), (f"{n}i", "Simplify the radical: √{0} = {1}√{2}.".format(n, k, r)), (f"{r}i√{k}", "The perfect-square factor {0} comes out as {1}.".format(k * k, k))]
        expl = f"√(−{n}) = √(−1)·√{n} = i·{k}√{r} = {correct}."
        return _text_mc(rng, prompt, correct, ds, subskill="arithmetic", explanation=expl, tags=["complex", "radicals"], est=80, verify=correct)
    return _text_mc(rng, prompt, correct, ds, subskill="arithmetic", explanation=expl, tags=["complex", "add-subtract"], est=70, verify=correct)


def cx_multiply(rng, d):
    """Multiply complex numbers; squares; i² = −1."""
    a, b = rng.choice([v for v in range(-7, 8) if v]), rng.choice([v for v in range(-7, 8) if v])
    c, e = rng.choice([v for v in range(-7, 8) if v]), rng.choice([v for v in range(-7, 8) if v])
    if d == "easy":
        k = rng.choice([v for v in range(-6, 7) if v and abs(v) != 1])
        prompt = f"What is the product {_m(k)}i · ({_cx(a, b)})?"
        re, im = -k * b, k * a
        correct = _cx(re, im)
        ds = [(_cx(k * b, k * a), "i·i = −1, so the real part gets a minus sign."), (_cx(k * a, k * b), "Multiply through by i: the imaginary term becomes real (with i² = −1)."), (_cx(-k * b, -k * a) if (-k * b, -k * a) != (re, im) else _cx(re + 1, im), "Check the sign of the imaginary part."), (_cx(k * a, -k * b) if (k * a, -k * b) != (re, im) else _cx(re, im + 1), "Distribute carefully: ki·a = kai and ki·bi = −kb.")]
        expl = f"{_m(k)}i·{_m(a)} = {_m(k * a)}i and {_m(k)}i·{_m(b)}i = {_m(k * b)}i² = {_m(-k * b)}; total {correct}."
    elif d == "medium":
        re, im = a * c - b * e, a * e + b * c
        prompt = f"What is the product ({_cx(a, b)})({_cx(c, e)})?"
        correct = _cx(re, im) if (re, im) != (0, 0) else "0"
        ds = [(_cx(a * c + b * e, a * e + b * c) if (a * c + b * e, im) != (re, im) else _cx(re + 1, im), "i² = −1, so the bi·ei term is subtracted."), (_cx(a * c, b * e), "Use FOIL; the outer and inner terms give the imaginary part."), (_cx(a * c - b * e, a * e - b * c) if (re, a * e - b * c) != (re, im) else _cx(re, im + 2), "Add the outer and inner products."), (_cx(a * c, a * e + b * c) if (a * c, im) != (re, im) else _cx(re + 2, im), "Don't drop the bi·ei = −be term.")]
        expl = f"FOIL: {_m(a * c)} + {_m(a * e)}i + {_m(b * c)}i + {_m(b * e)}i² = {_m(a * c)} − ({_m(b * e)}) + {_m(a * e + b * c)}i = {correct}."
    else:
        re, im = a * a - b * b, 2 * a * b
        prompt = f"What is ({_cx(a, b)})² written in the form x + yi?"
        correct = _cx(re, im)
        ds = [(_cx(a * a + b * b, 2 * a * b), "i² = −1, so b² is subtracted."), (_cx(a * a, b * b), "(a + bi)² = a² + 2abi + b²i², not a² + b²."), (_cx(a * a - b * b, a * b) if a * b != im else _cx(re + 1, im), "The middle term is 2abi."), (_cx(a * a + b * b, 0) if a * a + b * b != re or im else _cx(re, -im), "Squaring is not multiplying by the conjugate.")]
        expl = f"({_m(a)} + {_m(b)}i)² = {_m(a * a)} + {_m(2 * a * b)}i + {_m(b * b)}i² = {correct}."
    return _text_mc(rng, prompt, correct, ds, subskill="arithmetic", explanation=expl, tags=["complex", "multiply"], est=75 if d == "easy" else 90, verify=correct)


def cx_conjugate_modulus(rng, d):
    """Conjugates (easy), modulus |a + bi| (medium), division by the conjugate (hard)."""
    if d == "easy":
        a, b = rng.choice([v for v in range(-9, 10) if v]), rng.choice([v for v in range(-9, 10) if v])
        prompt = rng.choice([f"What is the complex conjugate of {_cx(a, b)}?", f"Which of the following is the conjugate of {_cx(a, b)}?"])
        correct = _cx(a, -b)
        ds = [(_cx(-a, b), "The conjugate changes the sign of the IMAGINARY part only."), (_cx(-a, -b), "Only the imaginary part changes sign."), (_cx(b, a) if (b, a) != (a, -b) else _cx(a + 1, -b), "The real and imaginary parts don't swap."), (_cx(a, b), "The conjugate must differ in the sign of the imaginary part.")]
        expl = f"The conjugate of a + bi is a − bi: {correct}."
        return _text_mc(rng, prompt, correct, ds, subskill="conjugate_modulus", explanation=expl, tags=["complex", "conjugate"], est=60, verify=correct)
    if d == "medium":
        p, q, r = _pyth_triple(rng, 41)
        a, b = rng.choice([(p, q), (q, p), (-p, q), (p, -q), (-q, p), (-p, -q)])
        prompt = rng.choice([f"What is the modulus (absolute value) of the complex number {_cx(a, b)}?", f"What is |{_cx(a, b)}|?"])
        val = r
        def sq(v):  # (−21)², not −21² (which is −441)
            return f"({_m(v)})²" if v < 0 else f"{v}²"
        expl = f"|a + bi| = √(a² + b²) = √({sq(a)} + {sq(b)}) = √{r * r} = {r}."
        ds = [(abs(a) + abs(b), "Square, add, then take the square root; don't just add."), (r * r, "Take the square root."), (abs(a * a - b * b) if a * a != b * b else r + 2, "Add the squares; don't subtract."), (r + 1, "Arithmetic slip.")]
        return _numeric_mc(rng, prompt, val, ds, subskill="conjugate_modulus", explanation=expl, tags=["complex", "modulus"], est=75, verify=f"|{a}+{b}i|={r}")
    a, b = rng.choice([v for v in range(-6, 7) if v]), rng.choice([v for v in range(-6, 7) if v])
    c, e = rng.choice([(1, 1), (1, -1), (2, 1), (1, 2), (2, -1), (3, 1), (1, 3), (2, 3), (3, -2), (1, -2), (3, 4), (4, -3)])
    den = c * c + e * e
    re_n, im_n = a * c + b * e, b * c - a * e
    re, im = Fraction(re_n, den), Fraction(im_n, den)
    prompt = f"Which of the following is equivalent to ({_cx(a, b)})/({_cx(c, e)})?"
    def fr(x):
        return num_str(x)
    correct = f"({fr(re)}) + ({fr(im)})i" if im != 0 else f"{fr(re)}"
    ds = [(f"({fr(Fraction(a * c - b * e, den))}) + ({fr(Fraction(b * c + a * e, den))})i", "Multiply numerator and denominator by the conjugate {0}, then use i² = −1.".format(_cx(c, -e))),
          (f"({fr(Fraction(re_n, c * c - e * e))}) + ({fr(Fraction(im_n, c * c - e * e))})i" if c * c != e * e else f"({fr(re_n)}) + ({fr(im_n)})i", "The denominator becomes c² + e², a positive real number."),
          (f"({fr(Fraction(a, c))}) + ({fr(Fraction(b, e))})i", "Don't divide real by real and imaginary by imaginary."),
          (f"({fr(re)}) − ({fr(im)})i" if im else f"({fr(re + 1)}) + ({fr(im)})i", "Check the sign of the imaginary part.")]
    def sq(v):  # (−1)², not −1² (which is −1)
        return f"({_m(v)})²" if v < 0 else f"{v}²"
    expl = (f"Multiply top and bottom by the conjugate {_cx(c, -e)}: numerator ({_m(re_n)}) + ({_m(im_n)})i, denominator "
            f"{sq(c)} + {sq(e)} = {den}. Result: {correct}.")
    return _text_mc(rng, prompt, correct, ds, subskill="conjugate_modulus", explanation=expl, tags=["complex", "divide"], est=105, qtype="multi_step_math", verify=correct)


# --------------------------------------------------------------------------- #
# Family registry
# --------------------------------------------------------------------------- #
FAMILIES = {
    "number_properties": {
        "easy": [np_gcf_lcm, np_primes_factors, np_parity, np_order_ops, np_scientific, np_fdp, np_divisibility],
        "medium": [np_gcf_lcm, np_primes_factors, np_parity, np_order_ops, np_scientific, np_fdp, np_divisibility],
        "hard": [np_gcf_lcm, np_primes_factors, np_parity, np_order_ops, np_scientific, np_fdp, np_divisibility],
    },
    "coordinate_geometry": {
        "easy": [cg_distance, cg_midpoint, cg_circle, cg_lines, cg_point_on_line],
        "medium": [cg_distance, cg_midpoint, cg_circle, cg_lines, cg_point_on_line],
        "hard": [cg_distance, cg_midpoint, cg_circle, cg_lines, cg_point_on_line],
    },
    "angles_polygons": {
        "easy": [ap_transversal, ap_triangle, ap_polygon, ap_pairs],
        "medium": [ap_transversal, ap_triangle, ap_polygon, ap_pairs],
        "hard": [ap_transversal, ap_triangle, ap_polygon, ap_pairs],
    },
    "sequences": {
        "easy": [sq_arithmetic_term, sq_geometric_term, sq_sum, sq_recursive, sq_which_term],
        "medium": [sq_arithmetic_term, sq_geometric_term, sq_sum, sq_recursive, sq_which_term],
        "hard": [sq_arithmetic_term, sq_geometric_term, sq_sum, sq_recursive, sq_which_term],
    },
    "logarithms": {
        "easy": [lg_evaluate, lg_convert, lg_properties, lg_solve],
        "medium": [lg_evaluate, lg_convert, lg_properties, lg_solve],
        "hard": [lg_evaluate, lg_convert, lg_properties, lg_solve],
    },
    "complex_numbers": {
        "easy": [cx_powers, cx_add_sub, cx_multiply, cx_conjugate_modulus],
        "medium": [cx_powers, cx_add_sub, cx_multiply, cx_conjugate_modulus],
        "hard": [cx_powers, cx_add_sub, cx_multiply, cx_conjugate_modulus],
    },
}

# Convenience dispatchers (one per skill), mirroring the legacy SAT entry points.
number_properties = _dispatch(FAMILIES, "number_properties")
coordinate_geometry = _dispatch(FAMILIES, "coordinate_geometry")
angles_polygons = _dispatch(FAMILIES, "angles_polygons")
sequences = _dispatch(FAMILIES, "sequences")
logarithms = _dispatch(FAMILIES, "logarithms")
complex_numbers = _dispatch(FAMILIES, "complex_numbers")


# =========================================================================== #
# Bank-growth families (v2.1)
# =========================================================================== #
# ---- number_properties ------------------------------------------------------ #
def np_counting(rng, d):
    """Count multiples in a range; sum of consecutive integers; digit problems."""
    if d == "easy":
        k = rng.choice([3, 4, 5, 6, 7, 8, 9, 11, 12, 15])
        lo, hi = rng.randint(1, 60), rng.randint(100, 400)
        val = hi // k - (lo - 1) // k
        prompt = rng.choice([f"How many multiples of {k} are there between {lo} and {hi}, inclusive?",
                             f"How many integers from {lo} to {hi}, inclusive, are divisible by {k}?"])
        expl = f"Multiples of {k} up to {hi}: {hi // k}; up to {lo - 1}: {(lo - 1) // k}. Difference: {val}."
        ds = [(val + 1, "Check whether the endpoints are multiples."), (val - 1, "Check whether the endpoints are multiples."), ((hi - lo) // k, "Count by subtracting the multiples below {0} from those up to {1}.".format(lo, hi)), (hi // k, "That counts multiples from 1, not from {0}.".format(lo))]
    elif d == "medium":
        n = rng.randint(10, 60)
        prompt = rng.choice([f"What is the sum of the integers from 1 to {n}, inclusive?",
                             f"What is the sum of all positive integers less than or equal to {n}?"])
        val = n * (n + 1) // 2
        expl = f"Sum = n(n + 1)/2 = {n}·{n + 1}/2 = {val}."
        ds = [(n * n, "Use n(n + 1)/2, not n²."), (n * (n + 1), "Divide by 2."), (n * (n - 1) // 2, "Use n + 1, not n − 1."), (val + n, "Arithmetic slip.")]
    else:
        lo, hi = rng.randint(10, 40), rng.randint(60, 120)
        k = rng.choice([3, 4, 5, 6, 7, 8, 9])
        mults = [x for x in range(lo, hi + 1) if x % k == 0]
        val = sum(mults)
        prompt = f"What is the sum of all the multiples of {k} between {lo} and {hi}, inclusive?"
        expl = f"The multiples are {mults[0]}, {mults[1]}, …, {mults[-1]} ({len(mults)} terms); sum = {len(mults)}·({mults[0]} + {mults[-1]})/2 = {val}."
        ds = [(len(mults), "That is how many multiples there are, not their sum."), (val + k, "Check the last multiple."), (val - mults[0], "Include the first multiple."), (len(mults) * (mults[0] + mults[-1]), "Divide by 2 after multiplying by the count.")]
    return _numeric_mc(rng, prompt, val, ds, subskill="integer_reasoning", explanation=expl, tags=["number", "counting"], est=75 if d == "easy" else 90, verify=f"val={val}")


def np_fraction_word(rng, d):
    """Fraction-of-a-fraction and fraction word problems."""
    name = rng.choice(NAMES)
    if d == "easy":
        p, q = rng.choice([(1, 2), (1, 3), (2, 3), (1, 4), (3, 4), (2, 5), (3, 5), (5, 6), (3, 8), (5, 8)])
        n = q * rng.randint(4, 30)
        val = p * n // q
        prompt = rng.choice([f"{name} has {n} stickers and gives away {p}/{q} of them. How many stickers does {name} give away?",
                             f"A tank holds {n} gallons and is {p}/{q} full. How many gallons are in the tank?"])
        expl = f"{p}/{q} of {n} = {p}·{n}/{q} = {val}."
        ds = [(n - val, "That is the remaining part."), (n * q // p if n * q % p == 0 else val + q, "Multiply by the fraction; don't divide by it."), (Fraction(n, q), "That is 1/{0} of the amount; multiply by {1}.".format(q, p)), (val + p, "Arithmetic slip.")]
    elif d == "medium":
        p1, q1 = rng.choice([(1, 2), (2, 3), (3, 4), (1, 3), (3, 5)])
        p2, q2 = rng.choice([(1, 2), (1, 3), (2, 5), (1, 4), (3, 4)])
        n = q1 * q2 * rng.randint(2, 12)
        first = p1 * n // q1
        val = p2 * first // q2
        prompt = f"Of the {n} students at a camp, {p1}/{q1} are in the swimming program. Of those swimmers, {p2}/{q2} are beginners. How many students are beginner swimmers?"
        expl = f"Swimmers: {p1}/{q1} × {n} = {first}. Beginners: {p2}/{q2} × {first} = {val}."
        ds = [(first, "That is all the swimmers."), (p2 * n // q2, "The second fraction applies to the swimmers, not all students."), (first - val, "That is the number of non-beginner swimmers."), (val + p2, "Arithmetic slip.")]
    else:
        p, q = rng.choice([(1, 3), (2, 5), (3, 7), (1, 4), (3, 8), (2, 7), (4, 9)])
        rest_frac = Fraction(1, 1) - Fraction(p, q)
        k = rng.randint(2, 5)
        unit = rng.choice([15, 20, 24, 30, 36, 40, 48, 60, 72, 90])
        total = unit * q
        left = rest_frac * total
        # after spending p/q, spends a further fixed amount m, left with L
        m = rng.randint(5, int(left) - 5)
        L = int(left) - m
        prompt = f"{name} spent {p}/{q} of a paycheck on rent and then ${m} on groceries, leaving ${L}. How much, in dollars, was the paycheck?"
        val = total
        expl = f"After rent, {num_str(rest_frac)} of the paycheck remains: {num_str(rest_frac)}P − {m} = {L} → P = {total}."
        ds = [(int(left), "That is the amount left after rent, not the whole paycheck."), ((L + m) * q // p, "The remaining part is {0} of the paycheck, not {1}/{2}.".format(num_str(rest_frac), p, q)), (L + m, "That is the amount after rent; divide by {0}.".format(num_str(rest_frac))), (total + unit, "Arithmetic slip.")]
    return _numeric_mc(rng, prompt, val, ds, subskill="fraction_decimal_percent", explanation=expl, tags=["number", "fractions", "word-problem"], est=80 if d != "hard" else 100, qtype="multi_step_math" if d != "easy" else "multiple_choice", verify=f"val={val}")


# ---- coordinate_geometry ---------------------------------------------------- #
def cg_parallel_distance(rng, d):
    """Distance between parallel lines (horizontal/vertical, then slanted with 3-4-5 slopes)."""
    if d == "easy":
        b1 = rng.randint(-20, 20)
        b2 = b1 + rng.choice([v for v in range(-15, 16) if v])
        if rng.random() < 0.5:
            prompt = f"In the standard (x, y) coordinate plane, what is the distance between the lines y = {_m(b1)} and y = {_m(b2)}?"
            expl = f"Horizontal lines; the distance is |{_m(b1)} − ({_m(b2)})| = {abs(b1 - b2)}."
        else:
            prompt = f"In the standard (x, y) coordinate plane, what is the distance between the lines x = {_m(b1)} and x = {_m(b2)}?"
            expl = f"Vertical lines; the distance is |{_m(b1)} − ({_m(b2)})| = {abs(b1 - b2)}."
        val = abs(b1 - b2)
        ds = [(b1 + b2 if b1 + b2 != val else val + 3, "Subtract the constants; don't add."), (abs(b1 - b2) // 2 if val % 2 == 0 and val > 2 else val + 2, "The distance is the full gap."), (val + 1, "Arithmetic slip."), (b1 - b2 if b1 - b2 != val else b2 - b1, "Distance is positive.")]
    else:
        p, q = rng.choice([(3, 4), (4, 3)]) if d == "medium" else rng.choice([(3, 4), (4, 3), (5, 12), (12, 5), (8, 15), (15, 8)])
        c = math.isqrt(p * p + q * q)
        m = Fraction(p, q)
        k = rng.randint(1, 8)
        gap = k * c                 # |b1 - b2| = k c -> distance = k c / sqrt(1+m^2) = k c * q / c = k q
        b1 = rng.randint(-10, 10)
        b2 = b1 + rng.choice([-1, 1]) * gap
        val = k * q
        prompt = f"In the standard (x, y) coordinate plane, what is the distance between the parallel lines y = ({num_str(m)})x {_pm(b1)} and y = ({num_str(m)})x {_pm(b2)}?"
        expl = f"Distance = |b₁ − b₂|/√(1 + m²) = {gap}/√(1 + ({num_str(m)})²) = {gap}/({c}/{q}) = {val}."
        ds = [(gap, "That is the vertical gap; divide by √(1 + m²)."), (Fraction(gap, c), "√(1 + m²) = {0}/{1}, not {0}.".format(c, q)), (k * p, "Use the denominator of the slope, not the numerator, after simplifying."), (val + k, "Arithmetic slip.")]
    return _numeric_mc(rng, prompt, val, ds, subskill="parallel_perpendicular", explanation=expl, tags=["coordinate", "distance", "parallel"], est=70 if d == "easy" else 100, verify=f"val={val}")


def cg_area_coords(rng, d):
    """Area of a figure from vertex coordinates."""
    if d == "easy":
        x1, y1 = rng.randint(-8, 4), rng.randint(-8, 4)
        w, h = rng.randint(2, 12), rng.randint(2, 12)
        prompt = f"A rectangle in the standard (x, y) coordinate plane has vertices at {_pt(x1, y1)}, {_pt(x1 + w, y1)}, {_pt(x1 + w, y1 + h)}, and {_pt(x1, y1 + h)}. What is its area?"
        val = w * h
        expl = f"Width = {x1 + w} − ({_m(x1)}) = {w}; height = {y1 + h} − ({_m(y1)}) = {h}; area = {w}·{h} = {val}."
        ds = [(2 * (w + h), "That is the perimeter."), (w + h, "Multiply the side lengths."), (w * h // 2, "A rectangle's area is not halved."), ((x1 + w) * (y1 + h) if (x1 + w) * (y1 + h) != val else val + w, "Use the side lengths (differences of coordinates), not the coordinates themselves.")]
    elif d == "medium":
        x1, y1 = rng.randint(-8, 4), rng.randint(-8, 4)
        a, b = rng.randint(2, 14), rng.randint(2, 14)
        if (a * b) % 2:
            b += 1
        prompt = f"A triangle in the standard (x, y) coordinate plane has vertices {_pt(x1, y1)}, {_pt(x1 + a, y1)}, and {_pt(x1, y1 + b)}. What is its area?"
        val = a * b // 2
        expl = f"The legs are horizontal ({a}) and vertical ({b}): area = ½·{a}·{b} = {val}."
        ds = [(a * b, "Multiply by ½ for a triangle."), (a + b + math.isqrt(a * a + b * b), "That is roughly the perimeter."), ((a + b) // 2, "Multiply the legs; don't add."), (val + a, "Arithmetic slip.")]
    else:
        # shoelace for a triangle with general vertices (integer area guaranteed by choosing coordinates)
        x1, y1 = rng.randint(-6, 6), rng.randint(-6, 6)
        x2, y2 = x1 + rng.randint(2, 8), y1 + rng.choice([v for v in range(-5, 6)])
        x3, y3 = x1 + rng.choice([v for v in range(-4, 5)]), y1 + rng.randint(2, 8)
        twice = abs(x1 * (y2 - y3) + x2 * (y3 - y1) + x3 * (y1 - y2))
        if twice == 0 or twice % 2:
            return cg_area_coords(rng, d)
        val = twice // 2
        prompt = f"What is the area of the triangle in the standard (x, y) coordinate plane with vertices {_pt(x1, y1)}, {_pt(x2, y2)}, and {_pt(x3, y3)}?"
        expl = f"Use the shoelace formula: ½|x₁(y₂ − y₃) + x₂(y₃ − y₁) + x₃(y₁ − y₂)| = ½·{twice} = {val}."
        ds = [(twice, "Take half of the shoelace sum."), ((x2 - x1) * (y3 - y1) // 2 if (x2 - x1) * (y3 - y1) // 2 != val else val + 2, "The triangle is not a right triangle with those legs."), (val + 1, "Arithmetic slip."), ((x2 - x1) * (y3 - y1), "The enclosing box is larger than the triangle.")]
    return _numeric_mc(rng, prompt, val, ds, subskill="distance_midpoint", explanation=expl, tags=["coordinate", "area"], est=80 if d != "hard" else 105, verify=f"area={val}")


def cg_transform(rng, d):
    """Reflections and translations of points (text options)."""
    x, y = rng.choice([v for v in range(-9, 10) if v]), rng.choice([v for v in range(-9, 10) if v])
    if d == "easy":
        axis = rng.choice(["x-axis", "y-axis"])
        nx, ny = (x, -y) if axis == "x-axis" else (-x, y)
        prompt = f"The point {_pt(x, y)} is reflected across the {axis}. What are the coordinates of its image?"
        correct = _pt(nx, ny)
        ds = [(_pt(-x, -y), "That reflects across both axes (a 180° rotation)."), (_pt(-nx, -ny) if (nx, ny) != (x, y) else _pt(y, x), "Reflecting across the {0} changes the sign of the {1}-coordinate only.".format(axis, "y" if axis == "x-axis" else "x")), (_pt(y, x) if x != y else _pt(x + 1, y), "Coordinates are not swapped by an axis reflection."), (_pt(x, y), "The image is a different point unless the point lies on the axis.")]
        expl = f"Reflecting across the {axis} negates the {'y' if axis == 'x-axis' else 'x'}-coordinate: {correct}."
    elif d == "medium":
        dx, dy = rng.choice([v for v in range(-8, 9) if v]), rng.choice([v for v in range(-8, 9) if v])
        prompt = f"The point {_pt(x, y)} is translated {abs(dx)} unit{'s' if abs(dx) != 1 else ''} {'right' if dx > 0 else 'left'} and {abs(dy)} unit{'s' if abs(dy) != 1 else ''} {'up' if dy > 0 else 'down'}. What are the coordinates of the image?"
        correct = _pt(x + dx, y + dy)
        ds = [(_pt(x - dx, y - dy), "The directions are reversed."), (_pt(x + dy, y + dx) if dx != dy else _pt(x + dx, y - dy), "Horizontal moves change x; vertical moves change y."), (_pt(x + dx, y - dy), "Check the vertical direction."), (_pt(x - dx, y + dy), "Check the horizontal direction.")]
        expl = f"Add {_m(dx)} to x and {_m(dy)} to y: {correct}."
    else:
        kind = rng.choice(["y=x", "origin", "rot90"])
        if kind == "y=x":
            correct = _pt(y, x)
            prompt = f"The point {_pt(x, y)} is reflected across the line y = x. What are the coordinates of its image?"
            expl = "Reflecting across y = x swaps the coordinates."
            ds = [(_pt(-y, -x), "Swapping is all that happens; the signs don't change."), (_pt(x, -y), "That is a reflection across the x-axis."), (_pt(-x, y), "That is a reflection across the y-axis."), (_pt(-x, -y), "That is a reflection through the origin.")]
        elif kind == "origin":
            correct = _pt(-x, -y)
            prompt = f"The point {_pt(x, y)} is rotated 180° about the origin. What are the coordinates of its image?"
            expl = "A 180° rotation about the origin negates both coordinates."
            ds = [(_pt(x, -y), "Both coordinates change sign."), (_pt(-x, y), "Both coordinates change sign."), (_pt(y, x), "A 180° rotation doesn't swap coordinates."), (_pt(-y, x), "That is a 90° rotation.")]
        else:
            correct = _pt(-y, x)
            prompt = f"The point {_pt(x, y)} is rotated 90° counterclockwise about the origin. What are the coordinates of its image?"
            expl = "A 90° counterclockwise rotation maps (x, y) to (−y, x)."
            ds = [(_pt(y, -x), "That is a 90° clockwise rotation."), (_pt(-x, -y), "That is a 180° rotation."), (_pt(y, x), "That is a reflection across y = x."), (_pt(-x, y), "That is a reflection across the y-axis.")]
        if x == y or x == -y:
            return cg_transform(rng, d)
    return _text_mc(rng, prompt, correct, ds, subskill="points_on_lines", explanation=expl, tags=["coordinate", "transformation"], est=70 if d != "hard" else 85, verify=correct)


# ---- angles_polygons ---------------------------------------------------------- #
def ap_diagonals(rng, d):
    """Number of diagonals of a polygon and related counting."""
    names = {4: "quadrilateral", 5: "pentagon", 6: "hexagon", 7: "heptagon", 8: "octagon", 9: "nonagon", 10: "decagon", 12: "dodecagon"}
    if d == "easy":
        n = rng.choice([5, 6, 7, 8])
        val = n * (n - 3) // 2
        prompt = rng.choice([f"How many diagonals does a {names[n]} have?", f"How many diagonals can be drawn in a convex polygon with {n} sides?"])
        expl = f"Each of the {n} vertices connects to {n - 3} others by a diagonal; each diagonal is counted twice: {n}·{n - 3}/2 = {val}."
        ds = [(n * (n - 3), "Each diagonal joins two vertices, so divide by 2."), (n - 3, "That is the number of diagonals from one vertex."), (n * (n - 1) // 2, "That counts the sides as well as the diagonals."), (val + n, "Arithmetic slip.")]
    elif d == "medium":
        n = rng.choice([9, 10, 11, 12, 14, 15, 16, 18, 20])
        val = n * (n - 3) // 2
        prompt = f"How many diagonals does a convex polygon with {n} sides have?"
        expl = f"Diagonals = n(n − 3)/2 = {n}·{n - 3}/2 = {val}."
        ds = [(n * (n - 3), "Divide by 2."), (n * (n - 1) // 2 - n + n, "Subtract the {0} sides from the number of segments joining vertices.".format(n)) if False else (n * (n - 1) // 2, "That counts sides too; subtract {0}.".format(n)), (n - 3, "That is the diagonals from a single vertex."), (val - n, "Arithmetic slip.")]
    else:
        n = rng.choice([6, 7, 8, 9, 10, 11, 12, 13, 14, 15])
        val = n
        prompt = f"A convex polygon has {n * (n - 3) // 2} diagonals. How many sides does it have?"
        expl = f"Solve n(n − 3)/2 = {n * (n - 3) // 2}: n² − 3n − {n * (n - 3)} = 0 → (n − {n})(n + {n - 3}) = 0 → n = {n}."
        ds = [(n - 3, "That is n − 3, the diagonals per vertex."), (n + 1, "Check: {0}·{1}/2 ≠ {2}.".format(n + 1, n - 2, n * (n - 3) // 2)), (n * (n - 3) // 2 // 2 if n * (n - 3) // 4 != n else n + 2, "Solve n(n − 3)/2 = diagonals; don't halve the count."), (n - 1, "Check: {0}·{1}/2 ≠ {2}.".format(n - 1, n - 4, n * (n - 3) // 2))]
    return _numeric_mc(rng, prompt, val, ds, subskill="polygon_angles", explanation=expl, tags=["geometry", "polygon", "diagonals"], est=70 if d != "hard" else 95, verify=f"n={n}")


ap_diagonals.small_space = True


def ap_angle_chase(rng, d):
    """Angles around a point / on a line in ratios; bisectors."""
    if d == "easy":
        a = rng.randint(20, 150)
        b = rng.randint(20, 180 - a - 10)
        c = 180 - a - b
        prompt = f"Three angles together form a straight line. Two of them measure {a}° and {b}°. What is the measure of the third angle?"
        val = c
        expl = f"Angles on a straight line sum to 180°: 180 − {a} − {b} = {c}°."
        ds = [(360 - a - b, "A straight angle is 180°, not 360°."), (a + b, "Subtract from 180."), (abs(a - b) if abs(a - b) != c else c + 10, "Subtract both from 180."), (c + 5, "Arithmetic slip.")]
    elif d == "medium":
        triples = [(p, q, r) for p in range(1, 12) for q in range(p, 14) for r in range(q + 1, 20)
                   if 360 % (p + q + r) == 0 and math.gcd(math.gcd(p, q), r) == 1 and p + q + r <= 36]
        p, q, r = rng.choice(triples)
        k = 360 // (p + q + r)
        prompt = rng.choice([f"Three angles with a common vertex fill the full turn around that vertex, and their measures are in the ratio {p}:{q}:{r}. What is the measure of the largest angle?",
                             f"Three angles meet at a point and together measure 360°. If their measures are in the ratio {p}:{q}:{r}, what is the measure of the largest angle?",
                             f"The angles around a point are in the ratio {p}:{q}:{r}. What is the measure, in degrees, of the largest of the three angles?"])
        val = r * k
        expl = f"{p + q + r}x = 360 → x = {k}; largest = {r}·{k} = {val}°."
        ds = [(p * k, "That is the smallest angle."), (q * k, "That is the middle angle."), (r * 180 // (p + q + r), "Angles around a point sum to 360°, not 180°."), (k, "That is x, the common factor.")]
    else:
        a = rng.randint(30, 150)
        x = rng.randint(10, 40)
        k = rng.randint(2, 4)
        # AOB + BOC = (kx + c) + x = a, so c = a − (k + 1)x. (The old c = a − kx
        # left x off BOC: the keyed x did not solve the stated equation.)
        c = a - (k + 1) * x
        if c <= 0:
            return ap_angle_chase(rng, d)
        prompt = f"Ray OB lies inside angle AOC, which measures {a}°. If angle AOB measures ({k}x + {c})° and angle BOC measures x°, what is the measure of angle BOC?"
        val = x
        expl = f"({k}x + {c}) + x = {a} → {k + 1}x = {a - c} → x = {x}; angle BOC = {x}°."
        ds = [(k * x + c, "That is angle AOB."), (Fraction(a - c, k), "Both angles contain x; the coefficient is {0}.".format(k + 1)), (a - c, "That is {0}x; divide by {0} to find x.".format(k + 1)), (x + 2, "Arithmetic slip.")]
    return _numeric_mc(rng, prompt, val, ds, subskill="parallel_lines" if d != "hard" else "triangle_angles", explanation=expl, tags=["geometry", "angles", "chase"], est=70 if d == "easy" else 90, verify=f"val={val}")


# ---- sequences -------------------------------------------------------------- #
def sq_geometric_word(rng, d):
    """Geometric sequences and series in context."""
    name = rng.choice(NAMES)
    if d == "easy":
        a1 = rng.choice([2, 3, 4, 5, 6, 8, 10, 12, 16, 20, 25])
        r = rng.choice([2, 3, 4])
        n = rng.randint(4, 6)
        word = {2: "doubles", 3: "triples", 4: "quadruples"}[r]
        # Pin the first term to day 1 / the first hour (otherwise "day n" could count from day 0).
        prompt = rng.choice([f"On day 1, a chain message is sent to {a1} people. Each day after that, the number of people who receive it that day {word}. How many people receive it on day {n}?",
                             f"A colony has {a1} bacteria at the start of the first hour, and the number {word} every hour. How many bacteria are there at the start of the {_ordinal(n)} hour?"])
        val = a1 * r ** (n - 1)
        expl = f"Geometric with a₁ = {a1}, r = {r}: a_{n} = {a1}·{r}^{n - 1} = {val}."
        ds = [(a1 * r ** n, "Use the exponent n − 1 = {0}.".format(n - 1)), (a1 * r * (n - 1), "The number multiplies each day; it doesn't add."), (a1 * r ** (n - 2), "That is one step too few."), (a1 * (r ** n - 1) // (r - 1), "That is the total over all days, not the amount on day {0}.".format(n))]
    elif d == "medium":
        a1 = rng.choice([1, 2, 3, 4, 5, 10])
        r = rng.choice([2, 3])
        n = rng.randint(4, 7)
        val = a1 * (r ** n - 1) // (r - 1)
        prompt = rng.choice([f"{name} saves ${a1} in the first week and {'doubles' if r == 2 else 'triples'} the amount saved each week. How much, in dollars, has {name} saved in total after {n} weeks?",
                             f"A tournament starts with {a1} match{'es' if a1 > 1 else ''} in round 1, and each round has {r} times as many matches as the previous round. How many matches are played in the first {n} rounds combined?"])
        expl = f"S_n = a₁(rⁿ − 1)/(r − 1) = {a1}({r}^{n} − 1)/{r - 1} = {val}."
        ds = [(a1 * r ** (n - 1), "That is the amount in week {0} alone.".format(n)), (a1 * (r ** (n - 1) - 1) // (r - 1), "That sums only {0} terms.".format(n - 1)), (a1 * r ** n, "That is the next term, not the sum."), (val + a1, "Arithmetic slip.")]
    else:
        a1 = rng.choice([8, 10, 12, 16, 20, 24, 30, 36, 40, 48, 60, 80, 90, 100])
        r = rng.choice([Fraction(1, 2), Fraction(1, 3), Fraction(2, 3), Fraction(3, 4), Fraction(1, 4), Fraction(3, 5), Fraction(4, 5)])
        val = a1 / (1 - r)
        prompt = rng.choice([f"A ball is dropped and its first bounce rises {a1} centimeters; each later bounce rises {num_str(r)} as high as the previous one. What is the total of all the bounce heights, in centimeters?",
                             f"A pendulum's first swing covers {a1} centimeters, and each swing covers {num_str(r)} of the distance of the previous swing. What is the total distance, in centimeters, covered by all the swings?"])
        expl = f"Infinite geometric series with |r| < 1: S = a₁/(1 − r) = {a1}/(1 − {num_str(r)}) = {num_str(val)}."
        ds = [(a1 * (1 - r), "Divide by 1 − r; don't multiply."), (Fraction(a1, r), "The denominator is 1 − r, not r."), (a1 + a1 * r, "That is only the first two swings."), (val + a1, "Arithmetic slip.")]
    return _numeric_mc(rng, prompt, val, ds, subskill="series" if d != "easy" else "geometric", explanation=expl, tags=["sequences", "geometric", "word-problem"], est=85 if d == "easy" else 100, verify=f"val={num_str(val)}")


def sq_pattern(rng, d):
    """Figure/toothpick patterns and explicit formulas."""
    a, dd = rng.randint(3, 10), rng.randint(2, 6)
    if a == dd:
        a += 1
    obj = rng.choice(["toothpicks", "tiles", "dots", "blocks"])
    if d == "easy":
        n = rng.randint(5, 12)
        prompt = f"In a pattern, figure 1 uses {a} {obj}, figure 2 uses {a + dd}, figure 3 uses {a + 2 * dd}, and each figure uses {dd} more than the one before. How many {obj} does figure {n} use?"
        val = a + (n - 1) * dd
        expl = f"Figure n uses {a} + (n − 1)·{dd}; figure {n} uses {a} + {n - 1}·{dd} = {val}."
        ds = [(a + n * dd, "Figure 1 already has {0}, so there are n − 1 additions.".format(a)), (n * dd, "Start from {0} {1}.".format(a, obj)), (a + (n - 2) * dd, "That is figure {0}.".format(n - 1)), (a * n, "Add {0} each time; don't multiply.".format(dd))]
    elif d == "medium":
        prompt = f"In a pattern, figure 1 uses {a} {obj} and each figure after the first uses {dd} more {obj} than the previous figure. Which expression gives the number of {obj} in figure n?"
        correct = f"{dd}n + {a - dd}" if a - dd > 0 else (f"{dd}n − {dd - a}" if a - dd < 0 else f"{dd}n")
        ds = [(f"{dd}n + {a}", "Check n = 1: this gives {0}, not {1}.".format(dd + a, a)), (f"{a}n + {dd}", "The rate of change is {0}, so {0} multiplies n.".format(dd)), (f"{a} + {dd}n" if a - dd != 0 else f"{a}n", "Check n = 1: this gives {0}, not {1}.".format(a + dd, a)), (f"{dd}(n − 1)", "Add the first figure's {0} {1}.".format(a, obj))]
        expl = f"Arithmetic pattern: {a} + (n − 1)·{dd} = {correct}."
        return _text_mc(rng, prompt, correct, ds, subskill="arithmetic", explanation=expl, tags=["sequences", "pattern"], est=85, verify=correct)
    else:
        total_n = rng.randint(6, 15)
        prompt = f"In a pattern, figure 1 uses {a} {obj} and each later figure uses {dd} more than the previous one. How many {obj} are needed to build figures 1 through {total_n} all together?"
        last = a + (total_n - 1) * dd
        val = total_n * (a + last) // 2
        expl = f"Figure {total_n} uses {last}; total = {total_n}({a} + {last})/2 = {val}."
        ds = [(last, "That is figure {0} alone.".format(total_n)), (total_n * last, "Average the first and last figures before multiplying."), (total_n * (a + last), "Divide by 2."), (val + a, "Arithmetic slip.")]
    return _numeric_mc(rng, prompt, val, ds, subskill="arithmetic" if d == "easy" else "series", explanation=expl, tags=["sequences", "pattern"], est=80 if d == "easy" else 100, verify=f"val={val}")


# ---- logarithms ------------------------------------------------------------- #
def lg_word(rng, d):
    """Logarithms in context: pH, decibels, Richter scale."""
    if d == "easy":
        k = rng.randint(1, 14)
        prompt = rng.choice([f"The pH of a solution is given by pH = −log[H⁺], where [H⁺] is the hydrogen ion concentration. What is the pH of a solution with [H⁺] = 10^(−{k})?",
                             f"A chemist measures a hydrogen ion concentration of 10^(−{k}) moles per liter. Using pH = −log[H⁺], what is the pH?",
                             f"The loudness of a sound, in decibels, is L = 10·log(I/I₀). What is the loudness of a sound with I/I₀ = 10^{k}?",
                             f"A sound's intensity is 10^{k} times the reference intensity I₀. Using L = 10·log(I/I₀), what is its loudness in decibels?"])
        if "pH" in prompt:
            val = k
            expl = f"pH = −log(10^(−{k})) = −(−{k}) = {k}."
            ds = [(-k, "The negative signs cancel."), (10 ** k if k <= 4 else k * 10, "The log of 10^(−k) is −k."), (k + 1, "Arithmetic slip."), (Fraction(1, k), "log(10^n) = n.")]
        else:
            val = 10 * k
            expl = f"L = 10·log(10^{k}) = 10·{k} = {val} decibels."
            ds = [(k, "Multiply by 10."), (10 ** k if k <= 4 else 10 * k + 10, "log(10^k) = k, then multiply by 10."), (10 * k + 10, "Arithmetic slip."), (k * k, "Multiply by 10, not by k.")]
    elif d == "medium":
        a, b = sorted(rng.sample(range(2, 9), 2))
        kind = rng.choice(["pH", "richter", "db"])
        if kind == "pH":
            prompt = f"Solution A has a pH of {a} and solution B has a pH of {b}. Since pH = −log[H⁺], how many times greater is the hydrogen ion concentration of solution A than that of solution B?"
            val = 10 ** (b - a)
            expl = f"[H⁺] = 10^(−pH); ratio = 10^(−{a})/10^(−{b}) = 10^{b - a} = {val}."
        elif kind == "richter":
            prompt = f"On the Richter scale, each whole-number increase in magnitude corresponds to a tenfold increase in amplitude: M = log(A/A₀). How many times greater is the amplitude of a magnitude-{b} earthquake than that of a magnitude-{a} earthquake?"
            val = 10 ** (b - a)
            expl = f"Ratio = 10^{b}/10^{a} = 10^{b - a} = {val}."
        else:
            prompt = f"Sound intensity relates to loudness by L = 10·log(I/I₀). How many times more intense is a {10 * b}-decibel sound than a {10 * a}-decibel sound?"
            val = 10 ** (b - a)
            expl = f"I/I₀ = 10^(L/10): 10^{b}/10^{a} = 10^{b - a} = {val}."
        ds = [(10 ** (b - a + 1), "The exponent is the difference {0} − {1} = {2}.".format(b, a, b - a)), (b - a, "A difference of {0} on a log scale is a factor of 10^{0}.".format(b - a)), (10 * (b - a), "Each unit is a factor of 10, so the factor is 10^{0}, not 10·{0}.".format(b - a)), (Fraction(b, a), "The scale is logarithmic; don't divide the readings.")]
    else:
        P = rng.choice([500, 1000, 1500, 2000, 2500, 4000, 5000, 8000])
        r = rng.choice([2, 3, 4, 5, 6, 7, 8, 9, 10, 12])
        mult = rng.choice([2, 3, 4, 5])
        prompt = (f"An account earning {r}% interest compounded annually grows from ${P} to ${P}(1.{r:02d})^t after t years. "
                  f"Which expression gives the number of years needed for the account to reach ${P * mult}?")
        correct = f"t = log({mult})/log(1.{r:02d})"
        ds = [(f"t = log(1.{r:02d})/log({mult})", "Solve (1.{0})^t = {1} by taking logs: t·log(1.{0}) = log {1}.".format(f"{r:02d}", mult)), (f"t = {mult}/1.{r:02d}", "t is an exponent; use logarithms."), (f"t = log({mult}·1.{r:02d})", "Divide the logs; don't multiply the arguments."), (f"t = log({P * mult})/log(1.{r:02d})", "First divide both sides by {0} to get (1.{1})^t = {2}.".format(P, f"{r:02d}", mult))]
        expl = f"{P}(1.{r:02d})^t = {P * mult} → (1.{r:02d})^t = {mult} → t·log(1.{r:02d}) = log {mult} → {correct}."
        return _text_mc(rng, prompt, correct, ds, subskill="solve_exponential", explanation=expl, tags=["logarithms", "word-problem"], est=100, verify=correct)
    return _numeric_mc(rng, prompt, val, ds, subskill="evaluate", explanation=expl, tags=["logarithms", "word-problem"], est=80 if d == "easy" else 95, verify=f"val={val}")


def lg_natural(rng, d):
    """Natural logs and e: ln(e^k), e^(ln k), solving e^x = c (expressions)."""
    k = rng.randint(2, 40)
    if d == "easy":
        if rng.random() < 0.5:
            prompt = rng.choice([f"What is the value of ln(e^{k})?", f"If y = ln(e^{k}), what is y?", f"Simplify ln(e^{k})."])
            val = k
            expl = f"ln and e^x are inverses: ln(e^{k}) = {k}."
            ds = [(1, "ln(e) = 1, but ln(e^k) = k."), (k * 2, "The logarithm returns the exponent."), (0, "ln(1) = 0, not ln(e^k)."), (k + 1, "Arithmetic slip.")]
        else:
            prompt = rng.choice([f"What is the value of e^(ln {k})?", f"If y = e^(ln {k}), what is y?", f"Simplify e^(ln {k})."])
            val = k
            expl = f"e^x and ln are inverses: e^(ln {k}) = {k}."
            ds = [(1, "e^(ln k) = k, not 1."), (k * k, "The functions cancel exactly."), (0, "ln of a positive number is defined; the result is k."), (k - 1, "Arithmetic slip.")]
        return _numeric_mc(rng, prompt, val, ds, subskill="evaluate", explanation=expl, tags=["logarithms", "natural"], est=65, verify=f"val={val}")
    if d == "medium":
        c = rng.choice([v for v in range(2, 100)])
        prompt = rng.choice([f"Which of the following is the solution to e^x = {c}?", f"If e^x = {c}, which expression gives x?"])
        correct = f"x = ln({c})"
        ds = [(f"x = e^{c}", "Apply ln to both sides, not e^x."), (f"x = {c}/e", "x is an exponent; use ln."), (f"x = log({c})", "The base is e, so use the natural log (ln), not log base 10."), (f"x = ln({c})/ln(e²)", "ln(e) = 1, so the division is unnecessary.")]
        expl = f"Take ln of both sides: ln(e^x) = x = ln({c})."
        return _text_mc(rng, prompt, correct, ds, subskill="solve_exponential", explanation=expl, tags=["logarithms", "natural"], est=75, verify=correct)
    a = rng.randint(2, 9)
    b = rng.choice([v for v in range(-9, 10) if v])
    c = rng.randint(2, 50)
    prompt = f"Which of the following is the solution to e^({a}x {_pm(b)}) = {c}?"
    correct = f"x = (ln({c}) {_pm(-b)})/{a}"
    ds = [(f"x = (ln({c}) {_pm(b)})/{a}", "Subtract {0} after taking ln; the sign is wrong.".format(_m(b))), (f"x = ln({c} {_pm(-b)})/{a}", "ln applies to {0} alone; move {1} afterward.".format(c, _m(b))), (f"x = ln({c})/{a} {_pm(b)}", "Divide the whole expression ln({0}) − ({1}) by {2}.".format(c, _m(b), a)), (f"x = {a}·ln({c}) {_pm(-b)}", "Divide by {0}; don't multiply.".format(a))]
    expl = f"ln both sides: {a}x {_pm(b)} = ln({c}), so x = (ln({c}) {_pm(-b)})/{a}."
    return _text_mc(rng, prompt, correct, ds, subskill="solve_exponential", explanation=expl, tags=["logarithms", "natural"], est=90, verify=correct)


# ---- complex_numbers ---------------------------------------------------------- #
def cx_conj_product(rng, d):
    """(a + bi)(a − bi), |z|², and the real/imaginary parts of products."""
    a, b = rng.choice([v for v in range(-9, 10) if v]), rng.choice([v for v in range(-9, 10) if v])
    if d == "easy":
        prompt = f"What is the product ({_cx(a, b)})({_cx(a, -b)})?"
        val = a * a + b * b
        expl = f"(a + bi)(a − bi) = a² + b² = {a * a} + {b * b} = {val}."
        ds = [(a * a - b * b, "i² = −1 turns −b²i² into +b²."), (_cx(a * a + b * b, 2 * a * b), "The imaginary terms cancel.") if False else (a * a, "Include the b² term."), (-val, "The product is positive."), (val + 1, "Arithmetic slip.")]
    elif d == "medium":
        c, e = rng.choice([v for v in range(-7, 8) if v]), rng.choice([v for v in range(-7, 8) if v])
        which = rng.choice(["real", "imaginary"])
        re, im = a * c - b * e, a * e + b * c
        prompt = f"What is the {which} part of the product ({_cx(a, b)})({_cx(c, e)})?"
        val = re if which == "real" else im
        expl = f"({_cx(a, b)})({_cx(c, e)}) = ({_m(a * c)} − ({_m(b * e)})) + ({_m(a * e)} + ({_m(b * c)}))i = {_cx(re, im)}; the {which} part is {_m(val)}."
        ds = [(im if which == "real" else re, f"That is the {'imaginary' if which == 'real' else 'real'} part."), (a * c + b * e if which == "real" else a * e - b * c, "Watch the sign from i² = −1." if which == "real" else "Add the outer and inner products."), (a * c if which == "real" else a * e, "Include both contributing terms."), (-val if val else val + 1, "Sign slip.")]
    else:
        prompt = f"If z = {_cx(a, b)}, what is the value of z·z̄ − |z|², where z̄ is the conjugate of z?"
        val = 0
        expl = f"z·z̄ = a² + b² = {a * a + b * b} and |z|² = a² + b² = {a * a + b * b}; the difference is 0."
        ds = [(a * a + b * b, "z·z̄ and |z|² are equal, so they cancel."), (2 * (a * a + b * b), "z·z̄ equals |z|², not −|z|²."), (2 * a * b, "No cross term survives."), (a * a - b * b, "|z|² = a² + b², and z·z̄ is the same.")]
    return _numeric_mc(rng, prompt, val, ds, subskill="conjugate_modulus", explanation=expl, tags=["complex", "conjugate"], est=75 if d != "hard" else 90, verify=f"a={a},b={b},val={val}")


def cx_quadratic(rng, d):
    """Complex solutions of quadratics."""
    if d == "easy":
        s = rng.randint(1, 20)
        k = s * s
        prompt = rng.choice([f"What are the solutions to the equation x² + {k} = 0?", f"In the complex numbers, what are the solutions to x² = −{k}?", f"Which of the following gives all solutions to x² + {k} = 0?"])
        correct = f"x = ±{s}i" if s != 1 else "x = ±i"
        ds = [(f"x = ±{s}", f"x² = −{k} has no real solutions; the square root of −1 is i."), (f"x = ±{k}i" if s != 1 else "x = ±3i", "Take the square root of {0}.".format(k)), (f"x = {s}i" if s != 1 else "x = i", "There are two solutions, ±."), (f"x = ±{s + 1}i", f"Check: ({s + 1}i)² = −{(s + 1) ** 2}, not −{k}.")]  # not ±√{k}i: equal in value
        expl = f"x² = −{k}, so x = ±√(−{k}) = ±{s}i."
    elif d == "medium":
        k = rng.randint(2, 9)
        r = rng.choice([2, 3, 5, 6, 7, 10, 11, 13])
        n = k * k * r
        prompt = rng.choice([f"What are the solutions to x² + {n} = 0?", f"Which of the following gives all complex solutions to x² = −{n}?"])
        correct = f"x = ±{k}i√{r}"
        ds = [(f"x = ±{k}√{r}", "The solutions are imaginary."), (f"x = ±{n}i", "Take the square root of {0}.".format(n)), (f"x = ±{k * k}i√{r}", "The perfect-square factor {0} comes out of the radical as {1}, not {0}.".format(k * k, k)),
              (f"x = ±{r}i√{k}" if r != k else f"x = ±{k + 1}i√{r}", "The perfect-square factor {0} comes out as {1}.".format(k * k, k))]
        # (No "±i√{n}" option: it equals the key in value, so two choices were correct.)
        expl = f"x² = −{n}, so x = ±i√{n} = ±{k}i√{r}."
    else:
        p = rng.choice([v for v in range(-6, 7) if v])
        q = rng.randint(1, 6)
        # roots p ± qi -> x^2 - 2p x + (p^2 + q^2)
        b, c = -2 * p, p * p + q * q
        prompt = f"What are the solutions to the equation {_poly_str([1, b, c])} = 0?"
        correct = f"x = {_m(p)} ± {q}i" if q != 1 else f"x = {_m(p)} ± i"
        ds = [(f"x = {_m(-p)} ± {q}i" if q != 1 else f"x = {_m(-p)} ± i", "x = −b/(2a) ± …: the real part is {0}.".format(_m(p))), (f"x = {_m(p)} ± {q}", "The discriminant is negative, so the solutions are complex."), (f"x = {_m(p)} ± {2 * q}i", "Divide the √ of the discriminant by 2a = 2."), (f"x = {_m(2 * p)} ± {q}i", "Divide −b by 2a = 2.")]
        expl = f"Discriminant b² − 4ac = {b * b} − {4 * c} = {b * b - 4 * c} = −{4 * q * q}; x = ({_m(-b)} ± {2 * q}i)/2 = {correct[4:]}."
    return _text_mc(rng, prompt, correct, ds, subskill="arithmetic", explanation=expl, tags=["complex", "quadratic"], est=80 if d != "hard" else 100, verify=correct)


_NEW_ACT = {
    "number_properties": [np_counting, np_fraction_word],
    "coordinate_geometry": [cg_parallel_distance, cg_area_coords, cg_transform],
    "angles_polygons": [ap_diagonals, ap_angle_chase],
    "sequences": [sq_geometric_word, sq_pattern],
    "logarithms": [lg_word, lg_natural],
    "complex_numbers": [cx_conj_product, cx_quadratic],
}
for _skill, _fns in _NEW_ACT.items():
    for _d in ("easy", "medium", "hard"):
        FAMILIES[_skill][_d].extend(_fns)
