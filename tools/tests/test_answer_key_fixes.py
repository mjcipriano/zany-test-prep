"""Regression tests for generator bugs found by the answer-key audit
(tools/audit/automated_checks.py). Each family that shipped wrong keys or
contradictory explanations is sampled heavily and must pass every audit check.
"""
from __future__ import annotations

import math
import random
import re
import unittest
import zlib
from fractions import Fraction

from tools.tests import helpers
from audit import automated_checks as ac
from audit.expr import holds, parse, parse_number
from content_gen import math_act, math_extra, math_gen, registry, science_gen, util

SAMPLES = 150

FIXED = [
    (math_gen.poly_factor, ("easy",)),
    (math_gen.rp_percent_of, ("easy", "hard")),
    (math_gen.rp_gridin, ("easy",)),
    (math_gen.pb_expected, ("easy",)),
    (math_gen.st_change_effect, ("easy", "medium", "hard")),
    (math_gen.st_outlier_effect, ("medium",)),
    (math_gen.pr_recipe, ("hard",)),
    (math_gen.fn_undefined, ("easy", "medium", "hard")),
    (math_gen.li_not_solution, ("easy", "medium", "hard")),
    (math_gen.ex_rules, ("medium",)),
    (math_extra.wp_interest, ("hard",)),
    (math_extra.tw_relative_freq, ("easy", "medium")),
    (math_act.cx_conjugate_modulus, ("medium", "hard")),
    (math_act.sq_geometric_term, ("hard",)),
    (science_gen.dr_lookup_value, ("easy", "medium", "hard")),
]


def sample(fn, diff, n=SAMPLES, options=4):
    util.set_option_count(options)
    try:
        rng = random.Random(zlib.crc32(f"{fn.__name__}/{diff}/{options}".encode()))
        return [helpers.as_question(registry.run_family(fn, rng, diff), difficulty=diff)
                for _ in range(n)]
    finally:
        util.set_option_count(4)


def keyed(q):
    return next(c["text"] for c in q["choices"] if c["id"] == q["correct_choice"])


class AuditChecksPassTest(unittest.TestCase):
    def test_fixed_families_pass_every_check(self):
        for fn, diffs in FIXED:
            for diff in diffs:
                for options in (4, 5):
                    for q in sample(fn, diff, options=options):
                        res = ac.run_checks(q)
                        bad = {c: r for c, r in res.items()
                               if c not in ac.WARN_CHECKS and r not in (ac.PASS, ac.SKIP)}
                        self.assertEqual(bad, {}, f"{fn.__name__}/{diff}/{options}: {q['prompt']}\n"
                                                  f"{q.get('explanation')}")


class TargetedTest(unittest.TestCase):
    def test_percent_of_is_exact(self):
        for q in sample(math_gen.rp_percent_of, "easy"):
            nums = [int(x) for x in re.findall(r"\d+", q["prompt"])]
            pct = next(int(m) for m in re.findall(r"(\d+)%", q["prompt"]))
            whole = next(x for x in nums if x != pct)
            self.assertEqual(parse_number(keyed(q)), Fraction(whole * pct, 100), q["prompt"])
            if parse_number(keyed(q)).denominator != 1:
                self.assertTrue(q["prompt"].startswith("What is"), "fractional counts of items")

    def test_gridin_percent_is_exact(self):
        for q in sample(math_gen.rp_gridin, "easy"):
            pct, whole = map(int, re.match(r"What is (\d+)% of (\d+)\?", q["prompt"]).groups())
            self.assertAlmostEqual(q["answer"]["value"], whole * pct / 100)

    def test_successive_discount_not_truncated(self):
        for q in sample(math_gen.rp_percent_of, "hard"):
            p, d1, d2 = map(int, re.search(r"\$(\d+) is marked down (\d+)%.*additional (\d+)%",
                                           q["prompt"]).groups())
            exact = Fraction(p * (100 - d1) * (100 - d2), 10000)
            self.assertAlmostEqual(parse_number(keyed(q)), float(round(exact, 2)), places=6)

    def test_expected_count_rounds_to_nearest(self):
        for q in sample(math_gen.pb_expected, "easy"):
            pct, n = map(int, re.search(r"(\d+)% of .* If (\d+) ", q["prompt"]).groups())
            exact = Fraction(pct * n, 100)
            self.assertLessEqual(abs(parse_number(keyed(q)) - exact), Fraction(1, 2))

    def test_factoring_asks_for_complete_factorization(self):
        for q in sample(math_gen.poly_factor, "easy"):
            self.assertIn("completely factored form", q["prompt"])
            expr = q["prompt"].split(" of ")[-1].rstrip("?")
            self.assertEqual(parse(keyed(q)), parse(expr))

    def test_rounded_keys_say_so(self):
        for fn, diffs in ((math_gen.st_change_effect, ("medium", "hard")),
                          (math_gen.st_outlier_effect, ("medium",))):
            for diff in diffs:
                for q in sample(fn, diff):
                    if "." in keyed(q):
                        self.assertIn("Round to the nearest hundredth", q["prompt"])

    def test_rational_function_has_a_zero(self):
        zero_items = 0
        for q in sample(math_gen.fn_undefined, "easy", n=400):
            if not q["prompt"].endswith("f(x) = 0?"):
                continue  # "(x + 9)/(x + 9) is undefined at −9" is degenerate but correct
            zero_items += 1
            m = re.search(r"f\(x\) = \((.+?)\)/\((.+?)\)", q["prompt"])
            self.assertNotEqual(m.group(1), m.group(2), q["prompt"])
        self.assertGreater(zero_items, 100)

    def test_exactly_one_non_solution(self):
        for options in (4, 5):
            for q in sample(math_gen.li_not_solution, "hard", options=options):
                rel = re.search(r"inequality (.+?)\?|satisfies (.+?) EXCEPT", q["prompt"])
                rel = rel.group(1) or rel.group(2)
                bad = [c["id"] for c in q["choices"]
                       if not holds(rel, {"x": parse_number(c["text"])})]
                self.assertEqual(bad, [q["correct_choice"]], q["prompt"])

    def test_power_distractors_never_equal_the_key(self):
        def log_value(text):  # b^e compared as e·ln b (9^1296 is too big to expand)
            b, e = re.fullmatch(r"(\d+)\^(-?\d+)", text).groups()
            return round(int(e) * math.log(int(b)), 9) if int(b) > 1 else 0.0
        for q in sample(math_gen.ex_rules, "medium", n=400):
            vals = [log_value(c["text"]) for c in q["choices"]]
            self.assertEqual(vals.count(log_value(keyed(q))), 1, q["choices"])

    def test_lookup_choices_are_distinct_values(self):
        for q in sample(science_gen.dr_lookup_value, "medium", n=300):
            self.assertEqual(ac.check_choices(q), ac.PASS, [c["text"] for c in q["choices"]])

    def test_relative_frequency_counts_are_whole(self):
        for q in sample(math_extra.tw_relative_freq, "easy"):
            total = int(re.search(r"for (\d+) responses", q["prompt"]).group(1))
            self.assertIn(total, (50, 100, 200, 250, 400, 500))
            self.assertTrue(float(keyed(q)).is_integer())

    def test_modulus_explanation_parenthesizes_negatives(self):
        for q in sample(math_act.cx_conjugate_modulus, "medium") + \
                sample(math_act.cx_conjugate_modulus, "hard"):
            self.assertNotRegex(q["explanation"], r"(?<![(\d])[−-]\d+²")


if __name__ == "__main__":
    unittest.main()
