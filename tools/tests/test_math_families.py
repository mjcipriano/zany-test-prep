"""Tests for the SAT math item families (math_gen.py + math_extra.py).

Run from the repo root:  python3 -m unittest discover -s tools/tests -t .
"""
from __future__ import annotations

import random
import re
import unittest
from fractions import Fraction

from tools.tests import helpers  # noqa: F401  (sets sys.path)
from content_gen import math_extra, math_gen, registry, util

SAT_SKILLS = [
    "linear_equations", "linear_inequalities", "systems_of_equations", "functions",
    "quadratics", "exponents_radicals", "polynomials", "ratios_percentages_units",
    "proportions", "data_analysis", "statistics", "probability", "area_volume", "circles",
    "right_triangles", "trigonometry", "word_problems", "absolute_value", "exponential",
    "two_way_tables", "scatterplots",
]
SMALL_GEOMETRY = {"circles", "right_triangles", "trigonometry"}
TABLE = registry.merge(math_gen.FAMILIES, math_extra.FAMILIES)

NUMERIC_RE = re.compile(r"^-?[\d.,]+(/\d+)?%?$|^\$[\d.,]+$|^-?\d+(\.\d+)?π$|^-?\d*√\d+$")


def _norm(text: str) -> str:
    return text.replace("−", "-").replace("·", "*")


def _num(text: str):
    t = _norm(text).replace("$", "").replace("%", "").replace(",", "")
    return Fraction(t)


def _all_families(table=TABLE):
    seen = {}
    for skill, by_diff in table.items():
        for diff in helpers.DIFFICULTIES:
            for fn in by_diff[diff]:
                seen.setdefault(fn, set()).add(diff)
    return seen


class FamilyTableTests(unittest.TestCase):
    def test_every_sat_skill_has_families(self):
        self.assertEqual(sorted(TABLE), sorted(SAT_SKILLS))

    def test_minimum_family_counts(self):
        for skill in SAT_SKILLS:
            need = 5 if skill in SMALL_GEOMETRY else 6
            for diff in helpers.DIFFICULTIES:
                fns = TABLE[skill][diff]
                self.assertGreaterEqual(len(fns), need, f"{skill}/{diff} has {len(fns)} families")
                names = [registry.family_name(fn) for fn in fns]
                self.assertEqual(len(names), len(set(names)), f"{skill}/{diff} repeats a family")

    def test_all_families_valid_and_tagged(self):
        helpers.check_family_table(self, TABLE, samples=20, min_families=3)

    def test_families_are_deterministic(self):
        for fn, diffs in _all_families().items():
            for diff in diffs:
                a = helpers.sample_family(fn, diff, 3, seed=11)
                b = helpers.sample_family(fn, diff, 3, seed=11)
                self.assertEqual(a, b, f"{registry.family_name(fn)}/{diff} is not deterministic")

    def test_families_produce_many_distinct_items(self):
        for fn, diffs in _all_families().items():
            need = 8 if getattr(fn, "small_space", False) else 40
            for diff in diffs:
                bodies = helpers.sample_family(fn, diff, 120, seed=5)
                uniq = helpers.unique_signatures(bodies)
                self.assertGreaterEqual(
                    uniq, need, f"{registry.family_name(fn)}/{diff}: only {uniq} distinct items in 120")

    def test_lessons_mix_prompt_shapes(self):
        """Round-robin 20 items per skill/difficulty: the prompts must not all share a shape."""
        for skill in SAT_SKILLS:
            for diff in helpers.DIFFICULTIES:
                fns = TABLE[skill][diff]
                rng = random.Random(7)
                shapes = {helpers.shape(registry.run_family(registry.round_robin(fns, i), rng, diff)["prompt"])
                          for i in range(20)}
                self.assertGreaterEqual(len(shapes), min(4, len(fns)),
                                        f"{skill}/{diff} prompt shapes: {shapes}")

    def test_sat_only_marks_grid_ins(self):
        for fn, diffs in _all_families().items():
            for diff in diffs:
                types = {b["question_type"] for b in helpers.sample_family(fn, diff, 15, seed=2)}
                if getattr(fn, "sat_only", False):
                    self.assertEqual(types, {"student_produced"},
                                     f"{registry.family_name(fn)} is sat_only but yields {types}")
                else:
                    self.assertNotIn("student_produced", types,
                                     f"{registry.family_name(fn)} yields grid-ins without sat_only")

    def test_every_skill_has_non_grid_in_families_per_tier(self):
        """The ACT plan drops sat_only families; every tier must still have >= 3."""
        for skill in SAT_SKILLS:
            for diff in helpers.DIFFICULTIES:
                rest = [fn for fn in TABLE[skill][diff] if not getattr(fn, "sat_only", False)]
                self.assertGreaterEqual(len(rest), 3, f"{skill}/{diff} without grid-ins")

    def test_bodies_carry_answer_verification(self):
        for fn, diffs in _all_families().items():
            for diff in diffs:
                for b in helpers.sample_family(fn, diff, 5, seed=3):
                    self.assertTrue(b.get("answer_verification"),
                                    f"{registry.family_name(fn)}/{diff} lacks answer_verification")


class OptionCountTests(unittest.TestCase):
    def tearDown(self):
        util.set_option_count(4)

    def test_five_choices_for_act(self):
        util.set_option_count(5)
        for fn, diffs in _all_families().items():
            if getattr(fn, "sat_only", False):
                continue
            for diff in diffs:
                for b in helpers.sample_family(fn, diff, 12, seed=9):
                    n = len(b["choices"])
                    self.assertGreaterEqual(n, 4, f"{registry.family_name(fn)}/{diff}: {n} choices")
                    self.assertLessEqual(n, 5)
                    if all(NUMERIC_RE.match(c["text"].strip()) for c in b["choices"]):
                        self.assertEqual(n, 5, f"{registry.family_name(fn)}/{diff}: numeric item has {n} choices")
                    helpers.assert_valid_body(self, b, f"{registry.family_name(fn)}/{diff}@5")

    def test_four_choices_for_sat(self):
        util.set_option_count(4)
        for fn, diffs in _all_families().items():
            if getattr(fn, "sat_only", False):
                continue
            for diff in diffs:
                for b in helpers.sample_family(fn, diff, 6, seed=9):
                    self.assertEqual(len(b["choices"]), 4, registry.family_name(fn))


class CorrectnessTests(unittest.TestCase):
    """Recompute answers from the prompt text for several families."""

    @staticmethod
    def _correct_text(body):
        return next(c["text"] for c in body["choices"] if c["id"] == body["correct_choice"])

    def test_le_two_step_easy(self):
        for b in helpers.sample_family(math_gen.le_two_step, "easy", 60, seed=1):
            m = re.search(r"(\d+)x \+ (\d+) = (\d+)", _norm(b["prompt"]))
            self.assertIsNotNone(m, b["prompt"])
            a, k, c = map(int, m.groups())
            x = _num(self._correct_text(b))
            self.assertEqual(a * x + k, c, b["prompt"])
            for ch in b["choices"]:
                if ch["id"] != b["correct_choice"]:
                    self.assertNotEqual(a * _num(ch["text"]) + k, c, "distractor solves the equation")

    def test_le_gridin_easy(self):
        for b in helpers.sample_family(math_gen.le_gridin, "easy", 40, seed=2):
            m = re.search(r"(\d+)x \+ (\d+) = (\d+)", _norm(b["prompt"]))
            a, k, c = map(int, m.groups())
            self.assertEqual(a * b["answer"]["value"] + k, c)

    def test_st_gridin_mean(self):
        for b in helpers.sample_family(math_gen.st_gridin, "easy", 40, seed=3):
            nums = list(map(int, re.findall(r"\d+", b["prompt"])))
            self.assertEqual(Fraction(sum(nums), len(nums)), Fraction(b["answer"]["value"]))

    def test_rt_pythagorean_easy(self):
        for b in helpers.sample_family(math_gen.rt_pythagorean, "easy", 40, seed=4):
            m = re.search(r"legs of length (\d+) and (\d+)", b["prompt"])
            a, k = map(int, m.groups())
            c = int(self._correct_text(b))
            self.assertEqual(a * a + k * k, c * c)

    def test_pr_solve_easy(self):
        for b in helpers.sample_family(math_gen.pr_solve, "easy", 40, seed=5):
            m = re.search(r"If (\d+)/(\d+) = x/(\d+)", b["prompt"])
            a, k, c = map(int, m.groups())
            self.assertEqual(Fraction(a, k), Fraction(int(self._correct_text(b)), c))

    def test_wp_fee_rate_easy(self):
        for b in helpers.sample_family(math_extra.wp_fee_rate, "easy", 40, seed=6):
            fee, rate, total = map(int, re.findall(r"\$(\d+)", b["prompt"]))
            self.assertEqual(fee + rate * int(self._correct_text(b)), total)

    def test_sys_solve_satisfies_both_equations(self):
        for diff in helpers.DIFFICULTIES:
            for b in helpers.sample_family(math_gen.sys_solve, diff, 25, seed=8):
                m = re.search(r"x=(-?\d+),y=(-?\d+)", b["answer_verification"])
                x, y = map(int, m.groups())
                eqs = re.findall(r"(-?\d*)x ([+-]) (\d*)y = (-?\d+)", _norm(b["prompt"]))
                self.assertEqual(len(eqs), 2, b["prompt"])
                for ax, sign, by, c in eqs:
                    ax = int(ax) if ax not in ("", "-") else (-1 if ax == "-" else 1)
                    by = int(by) if by else 1
                    by = by if sign == "+" else -by
                    self.assertEqual(ax * x + by * y, int(c), b["prompt"])

    def test_le_fraction_eq_easy(self):
        for b in helpers.sample_family(math_gen.le_fraction_eq, "easy", 40, seed=11):
            m = re.search(r"\(x ([+-]) (\d+)\)/(\d+) = (-?\d+)", _norm(b["prompt"]))
            self.assertIsNotNone(m, b["prompt"])
            sign, a, den, c = m.groups()
            a = int(a) if sign == "+" else -int(a)
            x = _num(self._correct_text(b))
            self.assertEqual(Fraction(x + a, int(den)), Fraction(int(c)))

    def test_le_rate_word_rate(self):
        for diff in ("easy", "medium"):
            for b in helpers.sample_family(math_gen.le_rate_word, diff, 30, seed=12):
                nums = list(map(int, re.findall(r"\d+", b["prompt"])))
                t1, v1, t2, v2 = nums[0], nums[1], nums[2], nums[3]
                self.assertEqual(Fraction(v2 - v1, t2 - t1), _num(self._correct_text(b)))

    def test_li_not_solution_is_not_a_solution(self):
        for b in helpers.sample_family(math_gen.li_not_solution, "easy", 40, seed=13):
            m = re.search(r"(\d+)x ([+-]) (\d+) ([<>≤≥]) (-?\d+)", _norm(b["prompt"]))
            self.assertIsNotNone(m, b["prompt"])
            a, sign, k, sym, c = m.groups()
            a, k, c = int(a), int(k) if sign == "+" else -int(k), int(c)
            ok = {"<": lambda v: v < c, "≤": lambda v: v <= c, ">": lambda v: v > c, "≥": lambda v: v >= c}[sym]
            self.assertFalse(ok(a * _num(self._correct_text(b)) + k), b["prompt"])
            for ch in b["choices"]:
                if ch["id"] != b["correct_choice"]:
                    self.assertTrue(ok(a * _num(ch["text"]) + k), b["prompt"])

    def test_st_quartiles_iqr(self):
        for b in helpers.sample_family(math_gen.st_quartiles, "medium", 30, seed=14):
            data = sorted(map(int, re.findall(r"\d+", b["prompt"].split("data set")[1])))
            n = len(data)
            lo, hi = data[:n // 2], data[n // 2:]
            q1 = Fraction(lo[n // 4 - 1] + lo[n // 4], 2)
            q3 = Fraction(hi[n // 4 - 1] + hi[n // 4], 2)
            self.assertEqual(q3 - q1, _num(self._correct_text(b)))

    def test_rt_diagonal_easy(self):
        for b in helpers.sample_family(math_gen.rt_diagonal, "easy", 30, seed=15):
            a, k = map(int, re.findall(r"\d+", b["prompt"])[:2])
            c = int(self._correct_text(b))
            self.assertEqual(a * a + k * k, c * c)

    def test_wp_interest_easy(self):
        for b in helpers.sample_family(math_extra.wp_interest, "easy", 30, seed=16):
            P = int(re.search(r"\$(\d+)", b["prompt"]).group(1))
            r = int(re.search(r"(\d+)% simple", b["prompt"]).group(1))
            t = int(re.search(r"after (\d+) year", b["prompt"]).group(1))
            self.assertEqual(Fraction(P * r * t, 100), _num(self._correct_text(b)))

    def test_ab_vertex_easy_minimum(self):
        for b in helpers.sample_family(math_extra.ab_vertex, "easy", 30, seed=17):
            m = re.search(r"\|x ([+-]) (\d+)\| ([+-]) (\d+)", _norm(b["prompt"]))
            self.assertIsNotNone(m, b["prompt"])
            k = int(m.group(4)) if m.group(3) == "+" else -int(m.group(4))
            self.assertEqual(k, _num(self._correct_text(b)))

    def test_two_way_table_probabilities(self):
        for diff in helpers.DIFFICULTIES:
            for b in helpers.sample_family(math_extra.tw_probability, diff, 20, seed=9):
                rows = b["stimulus"]["table"]["rows"]
                a, c = int(rows[0][1]), int(rows[1][1])
                row_total, total = int(rows[0][3]), int(rows[2][3])
                val = _num(self._correct_text(b))
                expected = {"easy": Fraction(row_total, total), "medium": Fraction(a, total),
                            "hard": Fraction(a, a + c)}[diff]
                self.assertEqual(val, expected)


class LegacyDispatcherTests(unittest.TestCase):
    def test_legacy_functions_return_valid_tagged_bodies(self):
        legacy = [getattr(math_gen, s) for s in SAT_SKILLS[:16]] + [
            math_extra.word_problems, math_extra.absolute_value, math_extra.exponential_growth,
            math_extra.two_way_tables, math_extra.line_of_best_fit]
        for fn in legacy:
            for diff in helpers.DIFFICULTIES:
                rng = random.Random(42)
                for _ in range(6):
                    body = fn(rng, diff)
                    helpers.assert_valid_body(self, body, f"{fn.__name__}/{diff}")
                    self.assertIsNotNone(registry.family_of(body))

    def test_numeric_mc_pads_to_option_count(self):
        rng = random.Random(1)
        try:
            util.set_option_count(5)
            body = math_gen._numeric_mc(rng, "What is 7?", 7, [(8, "off by one")],
                                        subskill="s", explanation="Seven is seven.")
            self.assertEqual(len(body["choices"]), 5)
            util.set_option_count(4)
            body = math_gen._numeric_mc(rng, "What is 7?", 7, [(8, "off by one")],
                                        subskill="s", explanation="Seven is seven.")
            self.assertEqual(len(body["choices"]), 4)
        finally:
            util.set_option_count(4)


if __name__ == "__main__":
    unittest.main()


class RareDrawRegressionTests(unittest.TestCase):
    """Families that once crashed on rare draws (too few distinct distractors):
    q_intercepts when the axis of symmetry is x = 0, and le_line_equation when
    the slope equals the intercept. Hammer them at both option counts."""

    def test_rare_draws_never_crash(self):
        import random
        from content_gen import math_gen, registry, util
        targets = [("quadratics", "q_intercepts"), ("linear_equations", "le_line_equation")]
        try:
            for opt in (4, 5):
                util.set_option_count(opt)
                for skill, name in targets:
                    for diff, fns in math_gen.FAMILIES[skill].items():
                        fn = next((f for f in fns if f.__name__ == name), None)
                        if fn is None:
                            continue
                        for seed in range(2500):
                            body = registry.run_family(fn, random.Random(seed), diff)
                            # Some forms (e.g. "how many x-intercepts?") only have
                            # four sensible answers, so 4 choices is fine at 5.
                            n = len(body["choices"])
                            self.assertTrue(4 <= n <= opt, f"{name}/{diff}/{seed}: {n} choices")
        finally:
            util.set_option_count(4)
