import random
import unittest

from fractions import Fraction

from tools.tests import helpers  # noqa: F401  (sets sys.path)
from content_gen import registry, util


def _fam_a(rng, difficulty):
    return util.mc("Pick A " + difficulty, ["a", "b", "c", "d"], 0,
                   ["Correct.", "no", "no", "no"], subskill="s", explanation="because a.")


def _fam_b(rng, difficulty):
    return util.spr("What is 2+2?", 4, subskill="s", explanation="2+2=4")


class RegistryTests(unittest.TestCase):
    def test_merge_combines_modules(self):
        t1 = {"sk": {"easy": [_fam_a]}}
        t2 = {"sk": {"easy": [_fam_b], "hard": [_fam_b]}}
        merged = registry.merge(t1, t2)
        self.assertEqual(merged["sk"]["easy"], [_fam_a, _fam_b])
        self.assertEqual(merged["sk"]["medium"], [])
        self.assertEqual(merged["sk"]["hard"], [_fam_b])

    def test_merge_rejects_unknown_difficulty(self):
        with self.assertRaises(ValueError):
            registry.merge({"sk": {"insane": [_fam_a]}})

    def test_run_family_stamps_tag(self):
        body = registry.run_family(_fam_a, random.Random(1), "easy")
        self.assertIn("family:fam_a", body["tags"])
        self.assertEqual(registry.family_of(body), "fam_a")
        # Running twice does not duplicate the tag.
        body["tags"] = list(body["tags"])
        again = registry.run_family(lambda r, d: body, random.Random(1), "easy")
        self.assertEqual(again["tags"].count("family:fam_a"), 1)

    def test_round_robin_cycles(self):
        fns = [_fam_a, _fam_b]
        self.assertIs(registry.round_robin(fns, 0), _fam_a)
        self.assertIs(registry.round_robin(fns, 1), _fam_b)
        self.assertIs(registry.round_robin(fns, 2), _fam_a)

    def test_families_for_raises_when_missing(self):
        with self.assertRaises(KeyError):
            registry.families_for({}, "sk", "easy")

    def test_validate_table_reports_gaps(self):
        probs = registry.validate_table({"sk": {"easy": [_fam_a]}}, min_per_tier=2)
        self.assertTrue(any("sk/easy" in p for p in probs))
        self.assertTrue(any("sk/medium" in p for p in probs))


class UtilTests(unittest.TestCase):
    def tearDown(self):
        util.set_option_count(4)

    def test_mc_builds_choices_with_letters(self):
        body = util.mc("What is it?", ["x", "y", "z"], 1,
                       ["Wrong value.", "Correct.", "Wrong value."],
                       subskill="s", explanation="Because y is right.", tags=["t"])
        self.assertEqual([c["id"] for c in body["choices"]], ["A", "B", "C"])
        self.assertEqual(body["correct_choice"], "B")
        helpers.assert_valid_body(self, body)

    def test_mc_trims_to_option_count_keeping_correct(self):
        util.set_option_count(4)
        body = util.mc("p?", ["a", "b", "c", "d", "e"], 4,
                       ["no", "no", "no", "no", "Correct."],
                       subskill="s", explanation="why")
        self.assertEqual(len(body["choices"]), 4)
        self.assertEqual(body["choices"][-1]["text"], "e")
        self.assertEqual(body["correct_choice"], "D")
        util.set_option_count(5)
        body = util.mc("p?", ["a", "b", "c", "d", "e"], 0,
                       ["Correct.", "no", "no", "no", "no"],
                       subskill="s", explanation="why")
        self.assertEqual(len(body["choices"]), 5)
        self.assertEqual(body["correct_choice"], "A")

    def test_spr_renders_numbers_like_a_student(self):
        body = util.spr("What is 3/4?", Fraction(3, 4), subskill="s",
                        explanation="Three quarters.", tags=["t"])
        self.assertEqual(body["answer"]["accepted"], ["3/4"])
        body = util.spr("What is 5?", 5.0, subskill="s", explanation="It is five.",
                        tags=["t"])
        self.assertEqual(body["answer"]["accepted"], ["5"])
        helpers.assert_valid_body(self, body)

    def test_pad_numeric_distractors(self):
        rng = random.Random(3)
        ds = util.pad_numeric_distractors(rng, 12, [("13", "off by one")], 4)
        self.assertEqual(len(ds), 4)
        texts = [t for t, _ in ds]
        self.assertNotIn("12", texts)
        self.assertEqual(len(set(texts)), 4)

    def test_item_signature_ignores_choice_order_but_not_values(self):
        a = util.mc("If 2x = 4?", ["1", "2", "3", "4"], 1, ["n", "Correct.", "n", "n"],
                    subskill="s", explanation="e")
        b = util.mc("If 2x = 4?", ["4", "3", "2", "1"], 2, ["n", "n", "Correct.", "n"],
                    subskill="s", explanation="e")
        c = util.mc("If 2x = 6?", ["1", "2", "3", "4"], 2, ["n", "n", "Correct.", "n"],
                    subskill="s", explanation="e")
        self.assertEqual(util.item_signature(a), util.item_signature(b))
        self.assertNotEqual(util.item_signature(a), util.item_signature(c))

    def test_shuffle_with_correct_tracks_index(self):
        rng = random.Random(7)
        options, ci, rats = util.shuffle_with_correct(
            rng, ("right", "Correct."), [("w1", "r1"), ("w2", "r2")])
        self.assertEqual(options[ci], "right")
        self.assertEqual(rats[ci], "Correct.")
        self.assertEqual(sorted(options), ["right", "w1", "w2"])


if __name__ == "__main__":
    unittest.main()
