"""Regression tests for the generator defects found by the phase-3 answer-key
audit (independent solvers on a 3,000-question sample; see tools/audit/).

Each test samples a family heavily and checks the property the audit found
broken: a reversed key, two defensible answers, a missing right answer, a
context that leaves the answer undetermined, or an unfilled template slot.
Every test here fails on the pre-fix generators.
"""
from __future__ import annotations

import math
import random
import re
import statistics
import unittest
import zlib

from tools.tests import helpers
from audit import automated_checks as ac
from content_gen import (math_act, math_extra, math_gen, registry, rw_act, rw_extra, rw_gen,
                         science_gen, util)

N = 120


def sample(fn, diff, n=N, options=4):
    util.set_option_count(options)
    try:
        rng = random.Random(zlib.crc32(f"phase3/{fn.__name__}/{diff}/{options}".encode()))
        return [helpers.as_question(registry.run_family(fn, rng, diff), difficulty=diff)
                for _ in range(n)]
    finally:
        util.set_option_count(4)


def keyed(q):
    return next(c["text"] for c in q["choices"] if c["id"] == q["correct_choice"])


def texts(q):
    return [c["text"] for c in q.get("choices", [])]


def wrong(q):
    return [c["text"] for c in q["choices"] if c["id"] != q["correct_choice"]]


def bracketed_or_blank(q):
    m = re.search(r"\[([^\]]*)\]", q["prompt"])
    return m.group(1) if m else None


# --------------------------------------------------------------------------- #
# 1. st_spread: the key named the tighter set whenever the labels were swapped
# --------------------------------------------------------------------------- #
class SpreadTest(unittest.TestCase):
    def test_keyed_set_has_the_larger_standard_deviation(self):
        for options in (4, 5):
            for q in sample(math_gen.st_spread, "medium", options=options):
                sets = dict(re.findall(r"Data set ([AB]): ([\d, ]+)", q["prompt"]))
                sd = {k: statistics.pstdev(int(x) for x in v.split(",")) for k, v in sets.items()}
                wide = max(sd, key=sd.get)
                self.assertGreater(sd[wide], min(sd.values()) + 1, q["prompt"])
                self.assertTrue(keyed(q).startswith(f"The standard deviation of data set {wide} is greater"),
                                f"{q['prompt']}\n{sd}\nkey: {keyed(q)}")


# --------------------------------------------------------------------------- #
# 2. transitions: relation labels and distractor relations
# --------------------------------------------------------------------------- #
_WORD_REL = {w.lower(): r for r, ws in rw_gen._TRANS_BANK.items() for w in ws}
_TRANS_FAMILIES = [rw_gen.trans_blank, rw_gen.trans_opener, rw_gen.trans_sentence_options,
                   rw_gen.trans_passage, rw_gen.trans_paragraph]


def _lead_word(text):
    t = text.strip().rstrip(",").split(",")[0].strip().lower()
    return t if t in _WORD_REL else None


class TransitionTest(unittest.TestCase):
    def test_audited_items_carry_the_right_relation(self):
        labels = {s1: rel for s1, _s2, rel in rw_gen._TRANS_ITEMS}
        self.assertEqual(labels["The committee debated the proposal for hours."], "contrast")
        self.assertEqual(labels["The lighthouse was automated decades ago."], "contrast")
        self.assertEqual(labels["The startup ran out of cash by the spring."], "cause")
        items = {s1: s2 for s1, s2, _ in rw_gen._TRANS_ITEMS}
        # "ripe bananas ... dense and bland" needed "Otherwise", which no choice offered
        self.assertNotIn("dense", items["The recipe calls for very ripe bananas."])
        self.assertNotIn("emphasis", {rel for *_x, rel in rw_gen._TRANS_ITEMS})
        harbor = next(p for p in rw_gen._TRANS_PASS if "harbor town" in p[0])
        self.assertNotIn("reinvented", harbor[2])  # was keyed "Still" for a time sequence
        library = next(p for p in rw_gen._TRANS_PARA if "photograph archive" in p[0])
        self.assertEqual(library[2], "sequence")  # "What is more" vs "For this reason"

    def test_no_distractor_from_an_overlapping_relation(self):
        for fn in _TRANS_FAMILIES:
            for diff in ("easy", "medium", "hard"):
                for options in (4, 5):
                    for q in sample(fn, diff, n=60, options=options):
                        rel = _WORD_REL[_lead_word(keyed(q))]
                        self.assertIn(rel, rw_gen._TRANS_DISTRACTOR_RELS, q["prompt"])
                        for t in wrong(q):
                            w = _lead_word(t)
                            self.assertIsNotNone(w, t)
                            self.assertIn(_WORD_REL[w], rw_gen._TRANS_DISTRACTOR_RELS[rel],
                                          f"{fn.__name__}: '{t}' also fits a {rel} item\n{q['prompt']}")

    def test_trans_delete_never_offers_a_fitting_transition(self):
        for q in sample(rw_gen.trans_delete, "hard", n=150):
            if keyed(q) == rw_gen._DELETE_TEXT:
                for t in wrong(q):
                    self.assertIn(_WORD_REL[_lead_word(t)], ("contrast", "cause", "example"), t)
            else:
                self.assertEqual(_WORD_REL[_lead_word(keyed(q))], "contrast", q["prompt"])


# --------------------------------------------------------------------------- #
# 3. pa_ambiguous: both people must take the same pronoun
# --------------------------------------------------------------------------- #
class AmbiguousPronounTest(unittest.TestCase):
    def test_both_antecedents_share_a_pronoun(self):
        for diff in ("easy", "medium", "hard"):
            for q in sample(rw_extra.pa_ambiguous, diff):
                text = q["prompt"].split("\n\n")[0]
                names = [n for n in rw_gen.NAMES if re.search(rf"\b{n}\b", text)]
                self.assertEqual(len(names), 2, text)
                self.assertEqual(rw_gen.pron(names[0])[0], rw_gen.pron(names[1])[0], text)
                self.assertFalse(set(names) & rw_extra._UNISEX_NAMES, text)


# --------------------------------------------------------------------------- #
# 4. punct_possessive: context must fix singular vs plural
# --------------------------------------------------------------------------- #
class PossessiveTest(unittest.TestCase):
    def test_determiner_fixes_the_number_of_owners(self):
        sing = tuple(rw_gen._POSS_DET["singular"])
        plur = tuple(rw_gen._POSS_DET["plural"])
        for diff in ("easy", "medium", "hard"):
            for q in sample(rw_gen.punct_possessive, diff):
                before = q["prompt"].split("___")[0].strip().lower()
                k = keyed(q)
                if k.endswith("s'") or k in dict(rw_gen._IRREG_PLUR).values():
                    self.assertTrue(before.endswith(plur), q["prompt"])
                else:
                    self.assertTrue(before.endswith(sing), q["prompt"])


# --------------------------------------------------------------------------- #
# 5. reflexive / point-of-view pronouns: exactly one right answer
# --------------------------------------------------------------------------- #
class PronounTest(unittest.TestCase):
    def test_reflexive_items_say_the_subject_acts_on_itself(self):
        for diff in ("easy", "medium", "hard"):
            for q in sample(rw_gen.pron_reflexive, diff):
                if keyed(q).endswith("self"):
                    self.assertRegex(q["prompt"], r"no teacher|own|Alone", q["prompt"])

    def test_he_or_she_is_never_offered_beside_singular_they(self):
        seen = 0
        for diff in ("easy", "medium", "hard"):
            for options in (4, 5):
                for q in sample(rw_gen.pron_shift, diff, options=options):
                    if "he or she" in texts(q) or any("he or she" in t for t in texts(q)):
                        seen += 1
                        self.assertFalse(any(re.search(r"\bthey\b", t) for t in texts(q)), texts(q))
        self.assertGreater(seen, 0)

    def test_vague_pronoun_items_do_not_offer_broad_which(self):
        for diff in ("easy", "medium", "hard"):
            for q in sample(rw_gen.pron_vague, diff):
                self.assertFalse(any(t.startswith("which ") for t in texts(q)), texts(q))
                shown = bracketed_or_blank(q)
                self.assertFalse(shown and shown.startswith("which "), q["prompt"])


# --------------------------------------------------------------------------- #
# 6. math
# --------------------------------------------------------------------------- #
def _choice_values(q):
    return [ac.keyed_value({**q, "correct_choice": c["id"]}) for c in q["choices"]]


class MathTest(unittest.TestCase):
    def test_similar_triangles_never_ask_for_the_given_side(self):
        for options in (4, 5):
            for q in sample(math_gen.pr_similar, "medium", options=options):
                self.assertNotIn("what is the length of the shortest side", q["prompt"])

    def test_angle_chase_key_solves_the_stated_equation(self):
        for q in sample(math_act.ap_angle_chase, "hard", options=5):
            a, k, c = map(int, re.search(r"measures (\d+)°\. If angle AOB measures \((\d+)x \+ (\d+)\)",
                                         q["prompt"]).groups())
            x = int(keyed(q))
            self.assertEqual((k + 1) * x + c, a, q["prompt"])

    def test_two_way_how_many_more_is_positive(self):
        for q in sample(math_extra.tw_count, "hard"):
            rows = q["stimulus"]["table"]["rows"]
            more, fewer = re.search(r"How many more responses were “(.+?)” than “(.+?)”", q["prompt"]).groups()
            col = next(i for i, h in enumerate(q["stimulus"]["table"]["headers"])
                       if h and h in q["prompt"].split("in the “")[-1])
            total = {r[0]: r for r in rows}
            # rebuild the missing cell of the first row from its total
            r0, r1 = rows[0], rows[1]
            vals = {r0[0]: int(r0[3]) - int(r0[1]), r1[0]: int(r1[col])}
            self.assertGreater(int(keyed(q)), 0)
            self.assertEqual(int(keyed(q)), vals[more] - vals[fewer], (q["prompt"], rows, total))

    def test_closest_point_to_line_is_unique(self):
        for q in sample(math_extra.sp_outlier_point, "medium"):
            fig = q["stimulus"]["figure"]
            m, b = fig["line"]["m"], fig["line"]["b"]
            res = sorted(abs(y - (m * x + b)) for x, y in fig["points"])
            self.assertLess(res[0], res[1], fig)

    def test_refit_direction_matches_least_squares(self):
        for q in sample(math_extra.sp_outlier_point, "hard"):
            pts = q["stimulus"]["figure"]["points"]
            px, py = map(int, re.search(r"point \((-?\d+), (−?-?\d+)\)", q["prompt"].replace("−", "-")).groups())
            rest = [p for p in pts if (p[0], p[1]) != (px, py)]
            before, after = math_extra._ols_slope(pts), math_extra._ols_slope(rest)
            want = "increase" if after > before else "decrease"
            self.assertIn(want, keyed(q), (pts, q["prompt"]))

    def test_no_two_choices_with_the_same_value(self):
        for fn, diffs in ((math_gen.ex_radicals, ("medium",)), (math_gen.ex_radical_ops, ("medium",)),
                          (math_act.cg_distance, ("hard",))):
            for diff in diffs:
                for options in (4, 5):
                    for q in sample(fn, diff, n=200, options=options):
                        res = ac.run_checks(q)
                        self.assertEqual(res["dup_distractors"], ac.PASS, (q["prompt"], texts(q)))
                        self.assertEqual(res["choices"], ac.PASS, (q["prompt"], texts(q)))

    def test_complex_roots_choices_are_distinct_in_value(self):
        def value(t):
            m = re.fullmatch(r"x = (±)?(\d*)(i?)(?:√(\d+))?(i?)", t)
            if not m:
                return t
            sign, coef, i1, rad, i2 = m.groups()
            v = (int(coef) if coef else 1) * (math.sqrt(int(rad)) if rad else 1)
            return (bool(sign), bool(i1 or i2), round(v, 9))
        for diff in ("easy", "medium"):
            for q in sample(math_act.cx_quadratic, diff, n=200, options=5):
                vals = [value(t) for t in texts(q)]
                self.assertEqual(len(vals), len(set(vals)), texts(q))

    def test_must_be_true_has_exactly_one_true_choice(self):
        def holds(choice, x):
            expr = choice.replace("−", "-").replace("x²", "(x**2)")
            expr = re.sub(r"(\d)x", r"\1*x", expr)
            return eval(expr, {"x": x})  # noqa: S307 - generator output, test only
        for options in (4, 5):
            for q in sample(math_gen.li_must_be_true, "easy", options=options):
                x0 = int(re.search(r"x > (−?\d+)", q["prompt"]).group(1).replace("−", "-"))
                xs = [x0 + 0.001, x0 + 0.5, x0 + 1, x0 + 7, x0 + 1000]
                always = [t for t in texts(q) if all(holds(t, x) for x in xs)]
                self.assertEqual(always, [keyed(q)], q["prompt"])

    def test_quartile_outlier_item_does_not_add_the_value(self):
        for q in sample(math_gen.st_quartiles, "hard"):
            self.assertNotIn("if added to the set", q["prompt"])
            self.assertIn("quartiles of this data set", q["prompt"])

    def test_function_slope_meaning_is_offered_and_keyed(self):
        posters = [q for q in sample(math_gen.fn_interpret, "hard", n=200) if "posters" in q["prompt"]]
        self.assertTrue(posters)
        for q in posters:
            self.assertEqual(keyed(q), "the cost per poster")

    def test_no_negative_profit_goal(self):
        for options in (4, 5):
            for q in sample(math_gen.li_word_max, "hard", options=options):
                self.assertNotRegex(q["prompt"], r"\$[−-]", q["prompt"])

    def test_frequency_tables_name_what_they_count(self):
        for diff in ("easy", "medium", "hard"):
            for q in sample(math_gen.st_frequency_table, diff, n=60):
                self.assertNotIn("people", q["prompt"])

    def test_geometric_word_problems_fix_the_first_term(self):
        for q in sample(math_act.sq_geometric_word, "easy", options=5):
            self.assertRegex(q["prompt"], r"On day 1|start of the first hour")


# --------------------------------------------------------------------------- #
# 7. science: percent questions offer only percents; "by how much" is the gap
# --------------------------------------------------------------------------- #
class ScienceTest(unittest.TestCase):
    def test_percent_items_offer_only_percents(self):
        for fn in (science_gen.tr_percent_across_table, science_gen.dr_percent_change):
            for diff in ("easy", "medium", "hard"):
                for q in sample(fn, diff, n=40):
                    self.assertTrue(all(t.endswith("%") for t in texts(q)), (q["prompt"], texts(q)))
                    self.assertIn("percent", q["prompt"])

    def test_condition_compare_asks_for_the_gap(self):
        for diff in ("easy", "medium", "hard"):
            for q in sample(science_gen.tr_condition_trend_compare, diff, n=40):
                self.assertNotIn("by what amount", q["prompt"])
                self.assertRegex(q["prompt"], r"than under the other condition|exceed the other")


# --------------------------------------------------------------------------- #
# Latent bugs surfaced by the regenerated bank (new random draws)
# --------------------------------------------------------------------------- #
class RegeneratedBankTest(unittest.TestCase):
    def test_families_pass_every_audit_check(self):
        cases = [(math_act.np_fdp, "easy", 5), (math_gen.q_intercepts, "hard", 5),
                 (math_gen.q_intercepts, "hard", 4), (science_gen.dr_ratio, "medium", 4),
                 (science_gen.tr_compare_slopes, "medium", 4),
                 (science_gen.tr_extrapolate_value, "hard", 4)]
        for fn, diff, options in cases:
            for q in sample(fn, diff, n=300, options=options):
                res = ac.run_checks(q)
                bad = {c: r for c, r in res.items() if r not in (ac.PASS, ac.SKIP)}
                self.assertEqual(bad, {}, f"{fn.__name__}: {q['prompt']}\n{texts(q)}\n{q.get('explanation')}")


# --------------------------------------------------------------------------- #
# 8. other low-confidence "flawed" items from the solver notes
# --------------------------------------------------------------------------- #
class OtherFlaggedTest(unittest.TestCase):
    def test_squinting_key_is_not_itself_squinting(self):
        for _base, _mod, _rest, _intent, good, squint, other, bad in rw_gen._SQUINT:
            self.assertEqual(len({good, squint, other, bad}), 4)
        keys = {keyed(q) for d in ("medium", "hard") for q in sample(rw_gen.mod_squinting, d)}
        self.assertNotIn("Walking the trail slowly reveals its beauty.", keys)
        self.assertNotIn("The coach told the players to rest on Friday.", keys)

    def test_dangling_modifier_items_have_one_logical_noun(self):
        snow = next(m for m in rw_gen._MODIFIERS if m[0] == "Covered in fresh snow,")
        self.assertNotIn("the village", snow[2:5])
        fog = next(m for m in rw_gen._MODIFIERS if m[0] == "Delayed by fog,")
        self.assertNotIn("the passengers", fog[2:5])

    def test_past_passage_cannot_read_as_present_habit(self):
        planetarium = next(v for v in rw_extra._VT_PASS if "planetarium" in v[0])
        self.assertIn("closed", planetarium[5])

    def test_collective_subject_has_no_competing_noun(self):
        for diff in ("easy", "medium", "hard"):
            for q in sample(rw_extra.pa_collective, diff):
                self.assertNotIn("hall", q["prompt"])

    def test_plural_people_never_take_a_which_clause(self):
        for q in sample(rw_extra.pa_possessive, "hard", n=200):
            self.assertNotRegex(q["prompt"], r"The (players|teachers|volunteers|residents|scientists|workers|"
                                             r"artists|members|engineers|students|farmers|divers|founders), which")

    def test_quantitative_evidence_percent_wording(self):
        for diff in ("easy", "medium", "hard"):
            for q in sample(rw_extra.qe_percent_change, diff, n=60):
                self.assertNotIn("(percent)", q["stimulus"]["table"]["caption"])
            for q in sample(rw_extra.qe_category_max, diff, n=60):
                self.assertNotRegex(keyed(q), r"by \d+ percent\.|\d+ percent higher", keyed(q))
        for q in sample(rw_extra.qe_compare_two, "hard", n=60):
            self.assertNotIn("has been closing", q["prompt"])

    def test_number_amount_has_no_tense_clash(self):
        for d in ("medium", "hard"):
            for q in sample(rw_act.ui_number_amount, d):
                self.assertNotIn("Last year,", q["prompt"])

    def test_no_unfilled_template_placeholders_anywhere(self):
        import generate_content
        table = generate_content.load_families()
        for skill, by_diff in table.items():
            for diff, fns in by_diff.items():
                for fn in fns:
                    for options in (4, 5):
                        for q in sample(fn, diff, n=8, options=options):
                            blob = " ".join([q.get("prompt", ""), q.get("explanation", "")] + texts(q))
                            self.assertIsNone(re.search(r"\{[a-z_]+\}", blob),
                                              f"{skill}/{diff}/{fn.__name__}: {blob[:300]}")


if __name__ == "__main__":
    unittest.main()
