import random
import unittest

from tools.tests import helpers
from content_gen import exam_plans, util
from content_gen.exam_plans import PLANS, act_no_change


def _fill_in_body(rng=None):
    rng = rng or random.Random(0)
    options, ci, rats = util.shuffle_with_correct(
        rng, ("includes", "Correct. Singular subject."),
        [("include", "Plural verb with a singular subject."),
         ("including", "An -ing form cannot be the main verb."),
         ("to include", "An infinitive cannot be the main verb.")])
    return util.mc("The box of photographs ___ a summary.\n\nWhich choice completes the text?",
                   options, ci, rats, subskill="agreement", qtype="grammar_editing",
                   explanation="The subject is singular, so 'includes'.", tags=["conventions"])


class PlanShapeTests(unittest.TestCase):
    def test_every_plan_skill_has_a_title_and_known_kind(self):
        for exam_id, plan in PLANS.items():
            self.assertEqual(plan.exam_id, exam_id)
            seen = set()
            for spec in plan.skills:
                self.assertIn(spec.kind, ("family", "rw_pool", "reading", "cross_text"), spec)
                self.assertIn(spec.skill, plan.skill_titles, f"{exam_id}: {spec.skill} has no title")
                self.assertNotIn(spec.skill, seen, f"{exam_id}: duplicate skill {spec.skill}")
                seen.add(spec.skill)
                for diff, n in spec.tiers:
                    self.assertIn(diff, ("easy", "medium", "hard"))
                    self.assertGreaterEqual(n, plan.min_lesson_items)
                    self.assertLessEqual(n, 25)

    def test_act_math_uses_five_choices_and_english_four(self):
        act = PLANS["act"]
        self.assertEqual(act.option_count_for("math"), 5)
        self.assertEqual(act.option_count_for("english"), 4)
        self.assertEqual(PLANS["sat"].option_count_for("math"), 4)

    def test_act_rejects_grid_ins(self):
        act = PLANS["act"]
        spr = util.spr("What is 2+2?", 4, subskill="s", explanation="Two plus two.", tags=["t"])
        self.assertFalse(act.accept_body(spr, "math"))
        self.assertTrue(act.accept_body(_fill_in_body(), "english"))

        def grid_in(rng, d):
            return spr
        grid_in.sat_only = True
        self.assertTrue(act.exclude_family(grid_in, "math"))
        self.assertFalse(act.exclude_family(lambda r, d: spr, "math"))
        self.assertFalse(PLANS["sat"].exclude_family(grid_in, "math"))

    def test_plans_cover_every_skill_in_skills_yaml(self):
        import yaml
        for exam_id, plan in PLANS.items():
            doc = yaml.safe_load((helpers.ROOT / "content" / "exams" / exam_id / "skills.yaml").read_text())
            yaml_skills = {sk["id"] for d in doc["domains"] for s in d["sections"] for sk in s["skills"]}
            plan_skills = {s.skill for s in plan.skills}
            self.assertEqual(plan_skills, yaml_skills, f"{exam_id}: plan/skills.yaml mismatch")
            self.assertEqual(set(plan.domain_slug), {d["id"] for d in doc["domains"]})


class NoChangeTransformTests(unittest.TestCase):
    def test_leaves_non_english_and_non_fill_in_alone(self):
        body = _fill_in_body()
        self.assertIs(act_no_change(body, "math", random.Random(1)), body)
        plain = util.mc("Which sentence is best?", ["a", "b", "c", "d"], 0,
                        ["Correct.", "no", "no", "no"], subskill="s",
                        explanation="Because it is.", tags=["t"])
        self.assertIs(act_no_change(plain, "english", random.Random(1)), plain)

    def test_choice_a_is_no_change_and_answer_is_preserved(self):
        for seed in range(60):
            body = _fill_in_body(random.Random(seed))
            out = act_no_change(body, "english", random.Random(seed))
            helpers.assert_valid_body(self, out, f"seed {seed}")
            self.assertEqual(out["choices"][0]["text"], "NO CHANGE")
            self.assertEqual([c["id"] for c in out["choices"]], ["A", "B", "C", "D"])
            self.assertNotIn("___", out["prompt"])
            self.assertIn("[", out["prompt"])
            self.assertIn("act-no-change", out["tags"])
            correct = next(c for c in out["choices"] if c["id"] == out["correct_choice"])
            shown = out["prompt"].split("[", 1)[1].split("]", 1)[0]
            if correct["text"] == "NO CHANGE":
                self.assertEqual(shown, "includes")
            else:
                self.assertEqual(correct["text"], "includes")
                self.assertNotEqual(shown, "includes")
                self.assertNotIn("includes", [c["text"] for c in out["choices"] if c is not correct])
            # the original body is not mutated
            self.assertIn("___", body["prompt"])

    def test_no_change_is_correct_about_a_quarter_of_the_time(self):
        rng = random.Random(42)
        n = 600
        hits = sum(
            act_no_change(_fill_in_body(random.Random(i)), "english", rng)["correct_choice"] == "A"
            for i in range(n))
        self.assertGreater(hits / n, 0.17)
        self.assertLess(hits / n, 0.33)


if __name__ == "__main__":
    unittest.main()
