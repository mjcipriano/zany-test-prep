"""Tests for the ACT-only math families (math_act.py) and their teaching cards.

Run from the repo root:  python3 -m unittest discover -s tools/tests -t .
"""
from __future__ import annotations

import json
import random
import re
import unittest
from fractions import Fraction

from jsonschema import Draft7Validator

from tools.tests import helpers  # noqa: F401  (sets sys.path)
from content_gen import math_act, registry, util
from content_gen.teaching_math_act import TEACHING_ACT

ACT_SKILLS = ["number_properties", "coordinate_geometry", "angles_polygons", "sequences",
              "logarithms", "complex_numbers"]
TABLE = math_act.FAMILIES
_LESSON_SCHEMA = json.loads((helpers.ROOT / "content" / "schemas" / "lesson.schema.json").read_text())
_LESSON_VALIDATOR = Draft7Validator(_LESSON_SCHEMA)

NUMERIC_RE = re.compile(r"^-?[\d.,]+(/\d+)?%?$")


def _all_families():
    seen = {}
    for skill, by_diff in TABLE.items():
        for diff in helpers.DIFFICULTIES:
            for fn in by_diff[diff]:
                seen.setdefault(fn, set()).add(diff)
    return seen


def _correct_text(body):
    return next(c["text"] for c in body["choices"] if c["id"] == body["correct_choice"])


class ActFamilyTableTests(unittest.TestCase):
    def test_skills_and_subskills(self):
        self.assertEqual(sorted(TABLE), sorted(ACT_SKILLS))
        self.assertEqual(sorted(math_act.SUBSKILLS), sorted(ACT_SKILLS))
        for skill, subs in math_act.SUBSKILLS.items():
            self.assertTrue(subs)
            for s in subs:
                self.assertRegex(s, r"^[a-z][a-z_]*$")

    def test_bodies_use_declared_subskills(self):
        for skill in ACT_SKILLS:
            for diff in helpers.DIFFICULTIES:
                for fn in TABLE[skill][diff]:
                    for b in helpers.sample_family(fn, diff, 10, seed=4):
                        self.assertIn(b["subskill"], math_act.SUBSKILLS[skill],
                                      f"{registry.family_name(fn)} uses subskill {b['subskill']!r}")

    def test_minimum_family_counts(self):
        for skill in ACT_SKILLS:
            for diff in helpers.DIFFICULTIES:
                fns = TABLE[skill][diff]
                self.assertGreaterEqual(len(fns), 6, f"{skill}/{diff}")
                names = [registry.family_name(fn) for fn in fns]
                self.assertEqual(len(names), len(set(names)))

    def test_all_families_valid_and_tagged(self):
        helpers.check_family_table(self, TABLE, samples=20, min_families=3)

    def test_no_grid_ins_on_act(self):
        for fn, diffs in _all_families().items():
            self.assertFalse(getattr(fn, "sat_only", False))
            for diff in diffs:
                for b in helpers.sample_family(fn, diff, 8, seed=1):
                    self.assertNotEqual(b["question_type"], "student_produced")

    def test_families_are_deterministic(self):
        for fn, diffs in _all_families().items():
            for diff in diffs:
                self.assertEqual(helpers.sample_family(fn, diff, 3, seed=11),
                                 helpers.sample_family(fn, diff, 3, seed=11))

    def test_families_produce_many_distinct_items(self):
        for fn, diffs in _all_families().items():
            need = 8 if getattr(fn, "small_space", False) else 40
            for diff in diffs:
                uniq = helpers.unique_signatures(helpers.sample_family(fn, diff, 120, seed=5))
                self.assertGreaterEqual(uniq, need, f"{registry.family_name(fn)}/{diff}: {uniq}")

    def test_lessons_mix_prompt_shapes(self):
        for skill in ACT_SKILLS:
            for diff in helpers.DIFFICULTIES:
                fns = TABLE[skill][diff]
                rng = random.Random(7)
                shapes = {helpers.shape(registry.run_family(registry.round_robin(fns, i), rng, diff)["prompt"])
                          for i in range(20)}
                self.assertGreaterEqual(len(shapes), 3, f"{skill}/{diff}: {shapes}")

    def test_bodies_carry_answer_verification(self):
        for fn, diffs in _all_families().items():
            for diff in diffs:
                for b in helpers.sample_family(fn, diff, 5, seed=3):
                    self.assertTrue(b.get("answer_verification"), registry.family_name(fn))

    def test_dispatchers_work(self):
        for skill in ACT_SKILLS:
            fn = getattr(math_act, skill)
            for diff in helpers.DIFFICULTIES:
                rng = random.Random(3)
                for _ in range(5):
                    b = fn(rng, diff)
                    helpers.assert_valid_body(self, b, f"{skill}/{diff}")
                    self.assertIsNotNone(registry.family_of(b))


class ActOptionCountTests(unittest.TestCase):
    def tearDown(self):
        util.set_option_count(4)

    def test_five_choices(self):
        util.set_option_count(5)
        for fn, diffs in _all_families().items():
            for diff in diffs:
                for b in helpers.sample_family(fn, diff, 12, seed=9):
                    n = len(b["choices"])
                    self.assertIn(n, (4, 5), f"{registry.family_name(fn)}/{diff}: {n}")
                    if all(NUMERIC_RE.match(c["text"].strip()) for c in b["choices"]):
                        self.assertEqual(n, 5, f"{registry.family_name(fn)}/{diff}")
                    helpers.assert_valid_body(self, b, f"{registry.family_name(fn)}/{diff}@5")


class ActCorrectnessTests(unittest.TestCase):
    def test_lg_evaluate_easy(self):
        for b in helpers.sample_family(math_act.lg_evaluate, "easy", 40, seed=1):
            m = re.search(r"log(?:_(\d+)|₁₀)?\s*\(?(\d+)\)?", b["prompt"])
            base = int(m.group(1)) if m.group(1) else 10
            x = int(m.group(2))
            self.assertEqual(base ** int(_correct_text(b)), x, b["prompt"])

    def test_cg_distance_easy(self):
        for b in helpers.sample_family(math_act.cg_distance, "easy", 40, seed=2):
            pts = re.findall(r"\((-?\d+), (-?\d+)\)", b["prompt"].replace("−", "-"))
            (x1, y1), (x2, y2) = [(int(a), int(c)) for a, c in pts[:2]]
            dist = int(_correct_text(b))
            self.assertEqual((x2 - x1) ** 2 + (y2 - y1) ** 2, dist * dist)

    def test_np_divisibility_easy_remainder(self):
        for b in helpers.sample_family(math_act.np_divisibility, "easy", 40, seed=3):
            n, k = map(int, re.search(r"when (\d+) is divided by (\d+)", b["prompt"]).groups())
            self.assertEqual(n % k, int(_correct_text(b)))

    def test_sq_arithmetic_medium(self):
        ords = {"first": 1, "second": 2, "third": 3, "fourth": 4, "fifth": 5, "sixth": 6,
                "seventh": 7, "eighth": 8, "ninth": 9, "tenth": 10}
        for b in helpers.sample_family(math_act.sq_arithmetic_term, "medium", 40, seed=4):
            p = b["prompt"].replace("−", "-")
            a1, d = map(int, re.search(r"first term (-?\d+) and common difference (-?\d+)", p).groups())
            m = re.search(r"What is the (\w+) term", p)
            n = ords.get(m.group(1)) or int(m.group(1).rstrip("thsndr"))
            self.assertEqual(a1 + (n - 1) * d, int(_correct_text(b).replace("−", "-")))

    def test_cx_modulus_medium(self):
        for b in helpers.sample_family(math_act.cx_conjugate_modulus, "medium", 40, seed=5):
            a, b2 = map(int, re.search(r"a=(-?\d+),b=(-?\d+)|\|(-?\d+)\+(-?\d+)i\|", b["answer_verification"]).group(0).replace("|", "").replace("i", "").split("+"))
            self.assertEqual(a * a + b2 * b2, int(_correct_text(b)) ** 2)

    def test_ap_diagonals(self):
        for diff in ("easy", "medium"):
            for b in helpers.sample_family(math_act.ap_diagonals, diff, 30, seed=7):
                names = {"quadrilateral": 4, "pentagon": 5, "hexagon": 6, "heptagon": 7, "octagon": 8, "nonagon": 9, "decagon": 10, "dodecagon": 12}
                m = re.search(r"with (\d+) sides", b["prompt"])
                n = int(m.group(1)) if m else next(v for k, v in names.items() if k in b["prompt"])
                self.assertEqual(n * (n - 3) // 2, int(_correct_text(b)))

    def test_np_counting_sum(self):
        for b in helpers.sample_family(math_act.np_counting, "medium", 30, seed=8):
            n = max(map(int, re.findall(r"\d+", b["prompt"])))
            self.assertEqual(n * (n + 1) // 2, int(_correct_text(b)))

    def test_cg_parallel_distance_easy(self):
        for b in helpers.sample_family(math_act.cg_parallel_distance, "easy", 30, seed=9):
            b1, b2 = map(int, re.findall(r"[xy] = (-?\d+)", b["prompt"].replace("−", "-")))
            self.assertEqual(abs(b1 - b2), int(_correct_text(b)))

    def test_lg_word_ph(self):
        for b in helpers.sample_family(math_act.lg_word, "easy", 40, seed=10):
            k = int(re.search(r"10\^\(?−?(\d+)\)?", b["prompt"]).group(1))
            val = int(_correct_text(b))
            self.assertEqual(val, k if "pH" in b["prompt"] else 10 * k)

    def test_cx_conj_product_easy(self):
        for b in helpers.sample_family(math_act.cx_conj_product, "easy", 30, seed=11):
            a, bb = map(int, re.search(r"a=(-?\d+),b=(-?\d+)", b["answer_verification"]).groups())
            self.assertEqual(a * a + bb * bb, int(_correct_text(b)))

    def test_ap_triangle_easy(self):
        for b in helpers.sample_family(math_act.ap_triangle, "easy", 40, seed=6):
            a, c = map(int, re.findall(r"(\d+)°", b["prompt"])[:2])
            self.assertEqual(a + c + int(_correct_text(b)), 180)


class TeachingActTests(unittest.TestCase):
    def _lesson(self, skill):
        card = dict(TEACHING_ACT[skill])
        return {
            "lesson_id": f"act-math-{skill.replace('_', '-')}-easy", "exam_id": "act", "exam_name": "ACT",
            "domain": "math", "section": "s", "skill": skill, "title": f"{card['title']} · Easy",
            "order": 0, "difficulty": "easy", "estimated_minutes": 10, "teaching_card": card,
            "question_ids": [f"q{i}" for i in range(8)], "prerequisite_lesson_ids": [],
            "unlock_xp": 0, "tags": ["math"], "version": "1.0.0",
        }

    def test_covers_all_act_skills(self):
        self.assertEqual(sorted(TEACHING_ACT), sorted(ACT_SKILLS))

    def test_cards_satisfy_lesson_schema(self):
        for skill in ACT_SKILLS:
            errors = [e.message for e in _LESSON_VALIDATOR.iter_errors(self._lesson(skill))]
            self.assertEqual(errors, [], f"{skill}: {errors}")

    def test_card_shape(self):
        for skill, card in TEACHING_ACT.items():
            self.assertGreaterEqual(len(card["body"]), 30)
            self.assertGreaterEqual(len(card["key_points"]), 2)
            self.assertTrue(card.get("worked_example"))
            screens = card["screens"]
            self.assertTrue(2 <= len(screens) <= 4, skill)
            for sc in screens:
                self.assertGreaterEqual(len(sc["title"]), 3)
                self.assertGreaterEqual(len(sc["body"]), 20)
                for kp in sc.get("key_points", []):
                    self.assertGreaterEqual(len(kp), 3)
            for pat in (r"\bTODO\b", r"\bTBD\b", r"lorem ipsum"):
                self.assertIsNone(re.search(pat, json.dumps(card), re.I), skill)


if __name__ == "__main__":
    unittest.main()
