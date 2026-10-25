"""Tests for the authored reading-passage pools (passages, passages_extra,
passages_more) and the builders that turn them into question bodies.

Run from the repo root:  python3 -m unittest discover -s tools/tests -t .

The pools are hand-authored, so these tests guard the things a human author
gets wrong: tuple shape, duplicate ids or option texts, placeholder text,
word-count bounds, and the correct option standing out by length.
"""
from __future__ import annotations

import collections
import random
import re
import unittest

from tools.tests import helpers
from content_gen import passages
from content_gen.passages import PAIRED, PASSAGES
from content_gen.passages_extra import PAIRED2, PASSAGES2
from content_gen.passages_more import PAIRED3, PASSAGES3

SKILLS = ("main_idea", "inference", "structure", "wic", "evidence")
PLACEHOLDER = re.compile(r"\bTODO\b|\bTBD\b|\bFIXME\b|lorem ipsum|\bxxx+\b|\bplaceholder\b", re.IGNORECASE)

# Bounds for the new pool. (The older pools were written to a shorter target.)
PASSAGE_WORDS = (110, 190)
PAIRED_TEXT_WORDS = (90, 140)
MIN_NEW_PASSAGES = 36
MIN_NEW_PAIRS = 12
# The correct option may be strictly the longest in at most this share of
# questions, overall and within every skill (including cross-text).
MAX_LONGEST_SHARE = 0.25
# After registration every skill must yield at least this many passage items
# (32 original + 36 new).
MIN_READING_PER_SKILL = 68


def _words(text: str) -> int:
    return len(text.split())


def _questions(pool, pairs):
    """Yield (where, skill, question_tuple) for single passages and pairs."""
    for p in pool:
        for skill in SKILLS:
            yield f"{p['id']}/{skill}", skill, p[skill]
    for pair in pairs:
        for i, q in enumerate(pair["questions"]):
            yield f"{pair['id']}/q{i}", "cross", q


def _new_questions():
    return list(_questions(PASSAGES3, PAIRED3))


def _all_questions():
    # passages.PASSAGES/PAIRED already include the extra and more pools after
    # registration, so this covers every authored question.
    return list(_questions(PASSAGES, PAIRED))


def _correct_is_strictly_longest(q) -> bool:
    _prompt, options, ci, _rats, _expl = q
    lens = [len(o) for o in options]
    return lens[ci] > max(l for i, l in enumerate(lens) if i != ci)


def longest_share(questions):
    """(overall share, {skill: share}) of questions whose key is strictly longest."""
    hits = collections.Counter()
    totals = collections.Counter()
    for _where, skill, q in questions:
        totals[skill] += 1
        hits[skill] += _correct_is_strictly_longest(q)
    overall = sum(hits.values()) / max(1, sum(totals.values()))
    return overall, {s: hits[s] / totals[s] for s in totals}


class QuestionTupleTests(unittest.TestCase):
    def _check_tuple(self, where, q):
        self.assertEqual(len(q), 5, f"{where}: tuple must have 5 parts")
        prompt, options, ci, rationales, explanation = q
        self.assertIsInstance(prompt, str)
        self.assertGreaterEqual(len(prompt.strip()), 5, f"{where}: prompt too short")
        self.assertEqual(len(options), 4, f"{where}: need exactly 4 options")
        self.assertEqual(len(rationales), 4, f"{where}: need exactly 4 rationales")
        self.assertIsInstance(ci, int)
        self.assertTrue(0 <= ci < 4, f"{where}: correct_index {ci} out of range")
        texts = [str(o).strip() for o in options]
        self.assertTrue(all(texts), f"{where}: empty option text")
        self.assertEqual(len(set(texts)), 4, f"{where}: duplicate option texts {texts}")
        for i, r in enumerate(rationales):
            self.assertGreaterEqual(len(str(r).strip()), 3, f"{where}: rationale {i} missing")
        self.assertTrue(str(explanation).strip(), f"{where}: empty explanation")

    def test_every_tuple_in_every_pool_is_structurally_valid(self):
        qs = _all_questions()
        self.assertGreater(len(qs), 0)
        for where, _skill, q in qs:
            self._check_tuple(where, q)

    def test_every_passage_has_all_five_skills(self):
        for p in PASSAGES:
            for skill in SKILLS:
                self.assertIn(skill, p, f"{p['id']} missing {skill}")
            self.assertTrue(p.get("title", "").strip(), f"{p['id']} missing title")
            self.assertTrue(p.get("text", "").strip(), f"{p['id']} missing text")

    def test_new_pool_marks_exactly_the_correct_rationale(self):
        """In passages_more the key's rationale starts with 'Correct' and no
        other one does: a cheap guard against a mis-set correct_index."""
        for where, _skill, q in _new_questions():
            _prompt, _opts, ci, rats, _expl = q
            for i, r in enumerate(rats):
                self.assertEqual(i == ci, str(r).startswith("Correct"),
                                 f"{where}: rationale {i} / correct_index {ci} disagree")

    def test_no_placeholder_text_anywhere(self):
        for p in PASSAGES:
            self.assertIsNone(PLACEHOLDER.search(p["text"]), p["id"])
            self.assertIsNone(PLACEHOLDER.search(p["title"]), p["id"])
        for pair in PAIRED:
            self.assertIsNone(PLACEHOLDER.search(pair["text_a"]), pair["id"])
            self.assertIsNone(PLACEHOLDER.search(pair["text_b"]), pair["id"])
        for where, _skill, (prompt, options, _ci, rats, expl) in _all_questions():
            for text in [prompt, expl, *options, *rats]:
                self.assertIsNone(PLACEHOLDER.search(str(text)), f"{where}: {text[:60]!r}")


class PoolCompositionTests(unittest.TestCase):
    def test_new_pool_sizes(self):
        self.assertGreaterEqual(len(PASSAGES3), MIN_NEW_PASSAGES)
        self.assertGreaterEqual(len(PAIRED3), MIN_NEW_PAIRS)
        for pair in PAIRED3:
            self.assertTrue(3 <= len(pair["questions"]) <= 4, f"{pair['id']}: {len(pair['questions'])} questions")

    def test_new_pool_is_registered(self):
        ids = {p["id"] for p in PASSAGES}
        for p in PASSAGES3:
            self.assertIn(p["id"], ids)
        pair_ids = {p["id"] for p in PAIRED}
        for p in PAIRED3:
            self.assertIn(p["id"], pair_ids)

    def test_ids_unique_across_all_passage_pools(self):
        ids = [p["id"] for p in PASSAGES]
        dups = [i for i, c in collections.Counter(ids).items() if c > 1]
        self.assertEqual(dups, [], f"duplicate passage ids: {dups}")
        # No module is registered twice.
        self.assertEqual(len(ids), len(set(ids)))
        self.assertEqual(sum(1 for i in ids if i in {p["id"] for p in PASSAGES3}), len(PASSAGES3))
        pair_ids = [p["id"] for p in PAIRED]
        pdups = [i for i, c in collections.Counter(pair_ids).items() if c > 1]
        self.assertEqual(pdups, [], f"duplicate pair ids: {pdups}")
        self.assertEqual(len(PAIRED2) + len(PAIRED3), len({p["id"] for p in PAIRED2 + PAIRED3}))

    def test_new_passage_word_counts(self):
        lo, hi = PASSAGE_WORDS
        for p in PASSAGES3:
            n = _words(p["text"])
            self.assertTrue(lo <= n <= hi, f"{p['id']}: {n} words, want {lo}-{hi}")
        # Lengths should actually vary so the complexity ordering has spread.
        counts = [_words(p["text"]) for p in PASSAGES3]
        self.assertGreaterEqual(max(counts) - min(counts), 40)

    def test_new_paired_text_word_counts(self):
        lo, hi = PAIRED_TEXT_WORDS
        for pair in PAIRED3:
            for key in ("text_a", "text_b"):
                n = _words(pair[key])
                self.assertTrue(lo <= n <= hi, f"{pair['id']}/{key}: {n} words, want {lo}-{hi}")

    def test_new_pool_varies_correct_index_and_prompt_wording(self):
        cis = collections.Counter(q[2] for _w, _s, q in _new_questions())
        for idx in range(4):
            self.assertGreaterEqual(cis[idx], 20, f"correct_index {idx} used only {cis[idx]} times: {dict(cis)}")
        # Prompts should not all follow one template per skill.
        for skill in SKILLS:
            shapes = {helpers.shape(re.sub(r"“[^”]*”|'[^']*'", "X", p[skill][0])) for p in PASSAGES3}
            self.assertGreaterEqual(len(shapes), 3, f"{skill}: prompt wording too uniform ({len(shapes)} shapes)")

    def test_correct_option_not_systematically_longest(self):
        qs = _new_questions()
        overall, by_skill = longest_share(qs)
        self.assertLessEqual(overall, MAX_LONGEST_SHARE,
                             f"correct option strictly longest in {overall:.0%} of new questions")
        for skill, share in by_skill.items():
            self.assertLessEqual(share, MAX_LONGEST_SHARE,
                                 f"{skill}: correct option strictly longest in {share:.0%}")


class BuilderTests(unittest.TestCase):
    def test_build_reading_yields_enough_valid_bodies_per_skill(self):
        for skill in SKILLS:
            bodies = passages.build_reading(skill, random.Random(7))
            self.assertGreaterEqual(len(bodies), MIN_READING_PER_SKILL, skill)
            for i, body in enumerate(bodies):
                helpers.assert_valid_body(self, body, f"build_reading/{skill}#{i}")
                self.assertEqual(body["question_type"], "passage_reading")
                self.assertEqual(body["stimulus"]["type"], "passage")
                self.assertIn("reading", body["tags"])

    def test_build_reading_orders_hardest_first(self):
        bodies = passages.build_reading("main_idea", random.Random(1))
        texts = [b["stimulus"]["text"] for b in bodies]
        scores = [passages._passage_complexity({"text": t}) for t in texts]
        self.assertEqual(scores, sorted(scores, reverse=True))

    def test_build_cross_text_yields_valid_bodies(self):
        bodies = passages.build_cross_text(random.Random(3))
        expected = sum(len(p["questions"]) for p in PAIRED)
        self.assertEqual(len(bodies), expected)
        self.assertGreaterEqual(len(bodies), 2 * (16 + MIN_NEW_PAIRS))
        for i, body in enumerate(bodies):
            helpers.assert_valid_body(self, body, f"build_cross_text#{i}")
            self.assertEqual(body["stimulus"]["type"], "paired_passages")
            self.assertTrue(body["stimulus"].get("text_b"))

    def test_shuffle_keeps_correct_choice_text(self):
        """The seeded shuffle must move the key with its rationale intact."""
        for p in PASSAGES3[:5]:
            for skill in SKILLS:
                prompt, options, ci, rats, _ = p[skill]
                body = passages._reading_q(p, skill, "passage_reading", 70, random.Random(11))
                key = next(c for c in body["choices"] if c["id"] == body["correct_choice"])
                self.assertEqual(key["text"], options[ci])
                self.assertEqual(key["rationale"], rats[ci])


if __name__ == "__main__":  # pragma: no cover
    unittest.main()
