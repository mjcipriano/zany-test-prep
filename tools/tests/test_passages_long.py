"""Tests for the ACT-length passage sets (passages_long, passages_long_sets,
passages_long_paired) and for how the generator files them into the bank.

Run from the repo root:  python3 -m unittest discover -s tools/tests -t .

The sets are hand-authored, so these tests guard what an author gets wrong:
set and question counts, word counts, tuple shape, a mis-set correct index,
paragraph references and quotations that do not match the passage, duplicate
ids/prompts/options, and the key standing out as the longest option.
"""
from __future__ import annotations

import collections
import importlib.util
import random
import re
import unittest

from tools.tests import helpers
from content_gen import passages, passages_long, util
from content_gen.exam_plans import PLANS
from content_gen.passages_long import KINDS, LONG_PAIRED, LONG_PASSAGES, all_sets

SINGLE_WORDS = (650, 820)
PAIRED_TEXT_WORDS = (300, 450)
PAIRED_TOTAL_WORDS = (680, 860)
MIN_SINGLES_PER_GENRE = 3
MIN_PAIRED = 2
MAX_LONGEST_SHARE = 0.25
QUOTE = re.compile(r"“([^”]+)”")
PARA_REF = re.compile(r"paragraph (\d+)(?: of Passage ([AB]))?")
PLACEHOLDER = re.compile(r"\bTODO\b|\bTBD\b|\bFIXME\b|lorem ipsum|\bxxx+\b|\bplaceholder\b", re.I)


def _words(text: str) -> int:
    return len(text.split())


def _paragraphs(pset, which=None):
    if passages_long.is_paired(pset):
        if which == "A":
            return pset["paragraphs_a"]
        if which == "B":
            return pset["paragraphs_b"]
        return pset["paragraphs_a"] + pset["paragraphs_b"]
    return pset["paragraphs"]


def _questions():
    for pset in all_sets():
        for i, q in enumerate(pset["questions"]):
            yield pset, f"{pset['id']}/q{i + 1}", q


def _norm(s: str) -> str:
    return re.sub(r"\s+", " ", s.replace("’", "'")).lower()


class SetCompositionTests(unittest.TestCase):
    def test_enough_sets_in_every_genre_and_tier(self):
        genres = collections.Counter(p["genre"] for p in LONG_PASSAGES)
        for genre in passages_long.GENRE_LABELS:
            self.assertGreaterEqual(genres[genre], MIN_SINGLES_PER_GENRE, genre)
        self.assertGreaterEqual(len(LONG_PAIRED), MIN_PAIRED)
        tiers = collections.Counter(p["difficulty"] for p in all_sets())
        for diff in ("easy", "medium", "hard"):
            self.assertGreaterEqual(tiers[diff], 4, f"{diff}: {dict(tiers)}")
        # Each genre's singles span the tiers, so every level reads every genre.
        for genre in passages_long.GENRE_LABELS:
            diffs = {p["difficulty"] for p in LONG_PASSAGES if p["genre"] == genre}
            self.assertEqual(diffs, {"easy", "medium", "hard"}, genre)

    def test_every_set_has_nine_questions_covering_the_core_skills(self):
        for pset in all_sets():
            kinds = [q[0] for q in pset["questions"]]
            self.assertEqual(len(kinds), passages_long.QUESTIONS_PER_SET, pset["id"])
            for k in kinds:
                self.assertIn(k, KINDS, f"{pset['id']}: unknown kind {k}")
            for need in ("main_idea", "detail", "vocab"):
                self.assertIn(need, kinds, f"{pset['id']} lacks {need}")
            self.assertTrue({"inference", "view"} & set(kinds), pset["id"])
            self.assertTrue({"function", "structure"} & set(kinds), pset["id"])
            if passages_long.is_paired(pset):
                self.assertGreaterEqual(kinds.count("comparison"), 3, pset["id"])
            else:
                self.assertNotIn("comparison", kinds, pset["id"])

    def test_ids_titles_and_texts_are_unique(self):
        ids = [p["id"] for p in all_sets()]
        self.assertEqual(len(ids), len(set(ids)))
        for i in ids:
            self.assertRegex(i, r"^[a-z0-9]+(?:-[a-z0-9]+)*$")
        titles = [p["title"] for p in all_sets()]
        self.assertEqual(len(titles), len(set(titles)))
        # No overlap with the short shared pool either.
        self.assertFalse(set(ids) & {p["id"] for p in passages.PASSAGES})
        paras = [para for p in all_sets() for para in _paragraphs(p)]
        self.assertEqual(len(paras), len(set(paras)), "a paragraph is repeated")

    def test_word_counts(self):
        lo, hi = SINGLE_WORDS
        for p in LONG_PASSAGES:
            n = passages_long.word_count(p)
            self.assertTrue(lo <= n <= hi, f"{p['id']}: {n} words, want {lo}-{hi}")
            self.assertGreaterEqual(len(p["paragraphs"]), 5, p["id"])
        for p in LONG_PAIRED:
            for which in ("A", "B"):
                n = sum(_words(t) for t in _paragraphs(p, which))
                lo, hi = PAIRED_TEXT_WORDS
                self.assertTrue(lo <= n <= hi, f"{p['id']}/{which}: {n} words")
            n = passages_long.word_count(p)
            lo, hi = PAIRED_TOTAL_WORDS
            self.assertTrue(lo <= n <= hi, f"{p['id']}: {n} words in all")

    def test_paragraphs_are_single_blocks(self):
        for p in all_sets():
            for para in _paragraphs(p):
                self.assertEqual(para, para.strip(), p["id"])
                self.assertNotIn("\n", para, p["id"])


class QuestionTests(unittest.TestCase):
    def test_tuples_are_well_formed_and_key_is_marked(self):
        for pset, where, q in _questions():
            self.assertEqual(len(q), 6, where)
            kind, prompt, options, ci, rats, expl = q
            self.assertGreaterEqual(len(prompt.strip()), 10, where)
            self.assertEqual(len(options), 4, where)
            self.assertEqual(len(rats), 4, where)
            texts = [o.strip() for o in options]
            self.assertTrue(all(texts), where)
            self.assertEqual(len(set(texts)), 4, f"{where}: duplicate options")
            self.assertTrue(0 <= ci < 4, where)
            for i, r in enumerate(rats):
                self.assertTrue(r.strip(), f"{where}: rationale {i} empty")
                # The key's rationale (and only the key's) starts with "Correct".
                self.assertEqual(i == ci, r.startswith("Correct"),
                                 f"{where}: rationale {i} / correct_index {ci} disagree")
            self.assertGreaterEqual(len(expl.strip()), 10, where)
            for text in [prompt, expl, *options, *rats]:
                self.assertIsNone(PLACEHOLDER.search(text), f"{where}: {text[:50]!r}")

    def test_prompts_are_unique_within_a_set(self):
        for pset in all_sets():
            prompts = [_norm(q[1]) for q in pset["questions"]]
            self.assertEqual(len(prompts), len(set(prompts)), pset["id"])

    def test_paragraph_references_exist_and_quotes_are_verbatim(self):
        """'paragraph N' must exist, and every “quoted” bit of a prompt must
        appear in the passage (in the cited paragraph when one is cited)."""
        for pset, where, q in _questions():
            prompt = q[1]
            refs = PARA_REF.findall(prompt)
            scope = _paragraphs(pset)
            for num, which in refs:
                paras = _paragraphs(pset, which or None)
                if passages_long.is_paired(pset):
                    self.assertTrue(which, f"{where}: paired refs must name Passage A or B")
                n = int(num)
                self.assertTrue(1 <= n <= len(paras), f"{where}: no paragraph {n}")
            if len(refs) == 1:
                num, which = refs[0]
                scope = [_paragraphs(pset, which or None)[int(num) - 1]]
            haystack = _norm(" ".join(scope))
            for quoted in QUOTE.findall(prompt):
                quoted = quoted.rstrip(",.;:")  # US style puts punctuation inside quotes
                self.assertIn(_norm(quoted), haystack, f"{where}: “{quoted}” not in cited text")

    def test_key_is_not_systematically_the_longest_option(self):
        hits = total = 0
        for _pset, _where, q in _questions():
            _k, _p, options, ci, _r, _e = q
            lens = [len(o) for o in options]
            total += 1
            hits += lens[ci] > max(n for i, n in enumerate(lens) if i != ci)
        self.assertLessEqual(hits / total, MAX_LONGEST_SHARE,
                             f"key strictly longest in {hits}/{total}")


class BuilderTests(unittest.TestCase):
    def setUp(self):
        util.set_option_count(4)

    def test_bodies_are_valid_and_tagged_with_their_set(self):
        sets = passages_long.build_passage_sets(random.Random(5))
        self.assertEqual(len(sets), len(all_sets()))
        for built, src in zip(sets, all_sets()):
            self.assertEqual(built["id"], src["id"])
            self.assertEqual(len(built["questions"]), len(src["questions"]))
            for i, ((skill, body), q) in enumerate(zip(built["questions"], src["questions"])):
                where = f"{src['id']}#{i}"
                helpers.assert_valid_body(self, body, where)
                self.assertEqual(skill, KINDS[q[0]][0], where)
                self.assertEqual(body["question_type"], "passage_reading")
                self.assertIn("passage-set:" + src["id"], body["tags"])
                self.assertIn("long-passage", body["tags"])
                stim = body["stimulus"]
                if passages_long.is_paired(src):
                    self.assertEqual(stim["type"], "paired_passages")
                    self.assertEqual(stim["text"].count("\n\n"), len(src["paragraphs_a"]) - 1)
                    self.assertEqual(stim["text_b"].count("\n\n"), len(src["paragraphs_b"]) - 1)
                else:
                    self.assertEqual(stim["type"], "passage")
                    self.assertEqual(stim["text"].count("\n\n"), len(src["paragraphs"]) - 1)
                self.assertTrue(stim["title"].startswith(passages_long.GENRE_LABELS[src["genre"]]))
                # The shuffle keeps the key's text and rationale together.
                key = next(c for c in body["choices"] if c["id"] == body["correct_choice"])
                self.assertEqual(key["text"], q[2][q[3]], where)
                self.assertEqual(key["rationale"], q[4][q[3]], where)

    def test_items_are_distinct_and_keys_spread_across_positions(self):
        sets = passages_long.build_passage_sets(random.Random(9))
        bodies = [b for s in sets for _sk, b in s["questions"]]
        sigs = {util.item_signature(b) for b in bodies}
        self.assertEqual(len(sigs), len(bodies))
        pos = collections.Counter(b["correct_choice"] for b in bodies)
        for letter in "ABCD":
            self.assertGreater(pos[letter] / len(bodies), 0.15, dict(pos))

    def test_skills_and_subskills_exist_in_act_skill_map(self):
        import yaml
        doc = yaml.safe_load((helpers.ROOT / "content" / "exams" / "act" / "skills.yaml").read_text())
        subs = {sk["id"]: set(sk.get("subskills") or [])
                for d in doc["domains"] for s in d["sections"] for sk in s["skills"]}
        for kind, (skill, sub, _tag) in KINDS.items():
            self.assertIn(skill, subs, kind)
            self.assertIn(sub, subs[skill], kind)


def _load_generator():
    spec = importlib.util.spec_from_file_location(
        "generate_content", helpers.ROOT / "tools" / "generate_content.py")
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


class GeneratorWiringTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.gen = _load_generator()

    def _builder(self, exam_id="act"):
        b = self.gen.Builder(PLANS[exam_id], {}, {})
        # Stand-in lessons for every reading skill tier (the real run builds them).
        b.lessons = [{"lesson_id": b.lesson_id(spec, diff)}
                     for spec in PLANS[exam_id].skills
                     if b.skill_index[spec.skill][0] == "reading"
                     for diff, _n in spec.tiers]
        return b

    def test_act_plan_serves_long_passages_and_sat_does_not(self):
        self.assertTrue(PLANS["act"].long_passage_sets)
        self.assertFalse(PLANS["sat"].long_passage_sets)

    def test_one_bank_file_per_set_in_authored_order(self):
        b = self._builder()
        b.build_passage_set_bank()
        util.set_option_count(4)
        self.assertEqual(len(b.bank_files), len(all_sets()))
        for src in all_sets():
            stem = f"act-reading-passage-{src['id']}"
            domain, qs = b.bank_files[stem]
            self.assertEqual(domain, "reading")
            self.assertEqual([q["question_id"] for q in qs],
                             [f"{stem}-q{i:02d}" for i in range(1, 10)])
            self.assertEqual([q["prompt"] for q in qs], [q[1] for q in src["questions"]])
            for q, srcq in zip(qs, src["questions"]):
                skill = KINDS[srcq[0]][0]
                self.assertEqual(q["skill"], skill)
                self.assertEqual(q["difficulty"], src["difficulty"])
                self.assertEqual(q["lesson_id"],
                                 f"act-reading-{skill.replace('_', '-')}-{src['difficulty']}")
                self.assertEqual(q["exam_id"], "act")
                self.assertEqual(len(q["choices"]), 4)

    def test_missing_lesson_is_an_error(self):
        b = self._builder()
        b.lessons = [l for l in b.lessons if "main-idea" not in l["lesson_id"]]
        with self.assertRaises(RuntimeError):
            b.build_passage_set_bank()
        util.set_option_count(4)

    def test_passage_bank_uses_its_own_rng(self):
        """Building the sets must not advance the main generator RNG, so adding
        passages never reshuffles the rest of the bank."""
        b = self._builder()
        before = b.rng.getstate()
        b.build_passage_set_bank()
        util.set_option_count(4)
        self.assertEqual(b.rng.getstate(), before)


if __name__ == "__main__":  # pragma: no cover
    unittest.main()
