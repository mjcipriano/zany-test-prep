"""Tests for the Reading & Writing family tables (rw_gen, rw_extra, rw_act).

Run from the repo root:  python3 -m unittest discover -s tools/tests -t .
"""
from __future__ import annotations

import collections
import json
import random
import re
import unittest
from pathlib import Path

from jsonschema import Draft7Validator

from tools.tests import helpers  # noqa: F401  (sets sys.path)
from content_gen import registry, rw_act, rw_extra, rw_gen, util
from content_gen.teaching_rw_act import TEACHING_ACT

MODULES = {"rw_gen": rw_gen, "rw_extra": rw_extra, "rw_act": rw_act}
MIN_FAMILIES = {"rw_gen": 4, "rw_extra": 4, "rw_act": 3}
EXPECTED_SKILLS = {
    "rw_gen": {"sentence_boundaries", "subject_verb_agreement", "punctuation", "pronouns",
               "modifiers", "transitions"},
    "rw_extra": {"verb_tense", "parallel_structure", "pronoun_antecedent", "quantitative_evidence"},
    "rw_act": {"usage_idioms"},
}
_LESSON_SCHEMA = json.loads((helpers.ROOT / "content" / "schemas" / "lesson.schema.json").read_text())
_CARD_VALIDATOR = Draft7Validator(_LESSON_SCHEMA["properties"]["teaching_card"])


def _all_families():
    """Yield (module_name, skill, difficulty, fn) for every registered family."""
    for mname, mod in MODULES.items():
        for skill, by_diff in mod.FAMILIES.items():
            for diff in registry.DIFFICULTIES:
                for fn in by_diff.get(diff, []):
                    yield mname, skill, diff, fn


def _distinct_families():
    seen = set()
    for mname, skill, diff, fn in _all_families():
        if fn not in seen:
            seen.add(fn)
            yield mname, skill, fn


def _first_word(text: str) -> str:
    m = re.search(r"[A-Za-z0-9]+", text or "")
    return m.group(0).lower() if m else ""


def _correct_text(body):
    return next(c["text"] for c in body["choices"] if c["id"] == body["correct_choice"])


class FamilyTableTests(unittest.TestCase):
    def test_tables_cover_expected_skills(self):
        for mname, mod in MODULES.items():
            self.assertEqual(set(mod.FAMILIES), EXPECTED_SKILLS[mname], mname)

    def test_minimum_family_counts(self):
        for mname, mod in MODULES.items():
            probs = registry.validate_table(mod.FAMILIES, min_per_tier=MIN_FAMILIES[mname])
            self.assertEqual(probs, [], mname)

    def test_every_family_yields_valid_bodies(self):
        for mname, mod in MODULES.items():
            helpers.check_family_table(self, mod.FAMILIES, samples=25,
                                       min_families=MIN_FAMILIES[mname])

    def test_fill_in_attribute_and_blank_convention(self):
        for mname, skill, diff, fn in _all_families():
            self.assertIn(getattr(fn, "fill_in", None), (True, False),
                          f"{mname}.{fn.__name__} must declare fn.fill_in")
            self.assertIn(getattr(fn, "small_space", None), (True, False),
                          f"{mname}.{fn.__name__} must declare fn.small_space")
            for b in helpers.sample_family(fn, diff, 20, seed=11):
                prompt = b["prompt"]
                where = f"{mname}.{fn.__name__}/{diff}"
                if fn.fill_in:
                    self.assertEqual(prompt.count("___"), 1, f"{where}: {prompt!r}")
                    text, _, stem = prompt.rpartition("\n\n")
                    self.assertIn("___", text, f"{where}: blank must be in the text, not the stem")
                    self.assertTrue(stem.strip().endswith("?"), f"{where}: stem {stem!r}")
                    self.assertNotIn("___", stem, where)
                    self.assertNotIn("\n", stem.strip(), where)
                else:
                    self.assertNotIn("___", prompt, f"{where}: {prompt!r}")

    def test_quantitative_evidence_uses_tables(self):
        for diff in registry.DIFFICULTIES:
            for fn in rw_extra.FAMILIES["quantitative_evidence"][diff]:
                for b in helpers.sample_family(fn, diff, 10, seed=3):
                    self.assertEqual(b["stimulus"]["type"], "table", fn.__name__)
                    tbl = b["stimulus"]["table"]
                    self.assertTrue(tbl["rows"], fn.__name__)
                    for row in tbl["rows"]:
                        self.assertEqual(len(row), len(tbl["headers"]), fn.__name__)

    def test_families_produce_many_distinct_items(self):
        for mname, skill, diff, fn in _all_families():
            bodies = helpers.sample_family(fn, diff, 120, seed=7)
            n = helpers.unique_signatures(bodies)
            need = 8 if fn.small_space else 30
            self.assertGreaterEqual(n, need, f"{mname}.{fn.__name__}/{diff}: {n} distinct of 120")

    def test_choice_texts_distinct_within_item(self):
        for mname, skill, diff, fn in _all_families():
            for b in helpers.sample_family(fn, diff, 40, seed=5):
                texts = [c["text"].strip() for c in b["choices"]]
                self.assertEqual(len(texts), len(set(texts)), f"{mname}.{fn.__name__}/{diff}: {texts}")
                self.assertGreaterEqual(len(texts), 4, f"{mname}.{fn.__name__}/{diff}")

    def test_correct_not_usually_longest(self):
        for mname, skill, diff, fn in _all_families():
            bodies = helpers.sample_family(fn, diff, 200, seed=13)
            longest = 0
            for b in bodies:
                cur = _correct_text(b)
                others = [c["text"] for c in b["choices"] if c["id"] != b["correct_choice"]]
                if all(len(cur) > len(o) for o in others):
                    longest += 1
            self.assertLessEqual(longest / len(bodies), 0.45,
                                 f"{mname}.{fn.__name__}/{diff}: correct is longest "
                                 f"{longest}/{len(bodies)}")

    def test_correct_position_is_shuffled(self):
        for mname, skill, diff, fn in _all_families():
            bodies = helpers.sample_family(fn, diff, 200, seed=17)
            pos = collections.Counter(b["correct_choice"] for b in bodies)
            self.assertLess(pos.most_common(1)[0][1] / len(bodies), 0.5,
                            f"{mname}.{fn.__name__}/{diff}: {pos}")

    def test_no_first_word_tell(self):
        """Mirror the validator: flag when >60% of keys share a first word that
        fewer than 25% of distractors use."""
        for mname, skill, diff, fn in _all_families():
            bodies = helpers.sample_family(fn, diff, 200, seed=19)
            correct_words = [_first_word(_correct_text(b)) for b in bodies]
            distractor_words = [_first_word(c["text"]) for b in bodies for c in b["choices"]
                                if c["id"] != b["correct_choice"]]
            word, cnt = collections.Counter(correct_words).most_common(1)[0]
            c_share = cnt / len(correct_words)
            d_share = distractor_words.count(word) / len(distractor_words)
            self.assertFalse(c_share > 0.6 and d_share < 0.25,
                             f"{mname}.{fn.__name__}/{diff}: {c_share:.0%} of keys start with "
                             f"{word!r} but only {d_share:.0%} of distractors do")

    def test_rationales_mark_correct_choice(self):
        for mname, skill, diff, fn in _all_families():
            for b in helpers.sample_family(fn, diff, 10, seed=23):
                cur = next(c for c in b["choices"] if c["id"] == b["correct_choice"])
                self.assertTrue(cur["rationale"].startswith("Correct"), f"{mname}.{fn.__name__}: {cur}")
                for c in b["choices"]:
                    if c["id"] != b["correct_choice"]:
                        self.assertFalse(c["rationale"].startswith("Correct"), f"{mname}.{fn.__name__}: {c}")

    def test_determinism(self):
        for mname, skill, fn in _distinct_families():
            a = helpers.sample_family(fn, "medium", 5, seed=99)
            b = helpers.sample_family(fn, "medium", 5, seed=99)
            self.assertEqual(a, b, f"{mname}.{fn.__name__} is not deterministic")

    def test_five_option_mode(self):
        util.set_option_count(5)
        try:
            for mname, skill, fn in _distinct_families():
                for b in helpers.sample_family(fn, "medium", 3, seed=31):
                    helpers.assert_valid_body(self, b, f"{mname}.{fn.__name__} (5 options)")
                    self.assertIn(len(b["choices"]), (4, 5))
        finally:
            util.set_option_count(4)


class LegacyDispatcherTests(unittest.TestCase):
    def test_legacy_generators_still_work(self):
        fns = [rw_gen.gen_sva, rw_gen.gen_boundaries, rw_gen.gen_punctuation, rw_gen.gen_pronouns,
               rw_gen.gen_modifiers, rw_gen.gen_transition, rw_extra.gen_verb_tense,
               rw_extra.gen_parallelism, rw_extra.gen_pronoun_antecedent,
               rw_extra.gen_quantitative_evidence, rw_act.gen_usage_idioms]
        for fn in fns:
            for diff in registry.DIFFICULTIES:
                rng = random.Random(41)
                for i in range(6):
                    b = fn(rng, diff)
                    helpers.assert_valid_body(self, b, f"{fn.__name__}/{diff}#{i}")
                    self.assertIsNotNone(registry.family_of(b), fn.__name__)

    def test_legacy_pools_still_work(self):
        rng = random.Random(2)
        for pool in (rw_gen.pool_concision, rw_gen.pool_synthesis, rw_gen.pool_transitions):
            items = pool(rng)
            self.assertGreater(len(items), 10, pool.__name__)
            for i, b in enumerate(items):
                helpers.assert_valid_body(self, b, f"{pool.__name__}#{i}")


class ActTeachingTests(unittest.TestCase):
    def test_subskills_declared(self):
        self.assertEqual(set(rw_act.SUBSKILLS), {"usage_idioms"})
        self.assertGreaterEqual(len(rw_act.SUBSKILLS["usage_idioms"]), 3)
        seen = set()
        for diff in registry.DIFFICULTIES:
            for fn in rw_act.FAMILIES["usage_idioms"][diff]:
                for b in helpers.sample_family(fn, diff, 5, seed=1):
                    seen.add(b["subskill"])
        self.assertTrue(seen <= set(rw_act.SUBSKILLS["usage_idioms"]), seen)

    def test_teaching_act_is_lesson_schema_valid(self):
        self.assertIn("usage_idioms", TEACHING_ACT)
        for skill, card in TEACHING_ACT.items():
            errors = [e.message for e in _CARD_VALIDATOR.iter_errors(card)]
            self.assertEqual(errors, [], skill)
            self.assertGreaterEqual(len(card["body"]), 30)
            self.assertGreaterEqual(len(card["key_points"]), 2)
            self.assertTrue(2 <= len(card["screens"]) <= 4, skill)
            for s in card["screens"]:
                self.assertGreaterEqual(len(s["body"]), 20)


if __name__ == "__main__":
    unittest.main()
