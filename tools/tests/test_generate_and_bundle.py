"""Orchestrator + bundler tests using stub families (fast, no real content)."""
import importlib.util
import json
import random
import sys
import tempfile
import unittest
from pathlib import Path

from tools.tests import helpers
from content_gen import registry, util
from content_gen.exam_plans import ExamPlan, SkillSpec

ROOT = helpers.ROOT


def _load(name):
    spec = importlib.util.spec_from_file_location(name, ROOT / "tools" / f"{name}.py")
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


gen = _load("generate_content")
bundle_tool = _load("build_bundle")


def _fam(label):
    def fn(rng, difficulty):
        a, b = rng.randint(1, 500), rng.randint(1, 500)
        return util.mc(f"{label} {difficulty}: what is {a} + {b}?",
                       [str(a + b), str(a + b + 1), str(a + b - 1), str(a - b)], 0,
                       ["Correct.", "Off by one.", "Off by one.", "Subtracted."],
                       subskill="s", explanation="Add the two numbers.", tags=["t"],
                       est=40)
    fn.__name__ = f"fam_{label}"
    return fn


def _grid(rng, difficulty):
    a = rng.randint(1, 900)
    return util.spr(f"grid: what is {a} + 1?", a + 1, subskill="s",
                    explanation="Add one.", tags=["t"])
_grid.sat_only = True


class StubBuilderTests(unittest.TestCase):
    def setUp(self):
        self.families = {"linear_equations": {d: [_fam("a"), _fam("b"), _fam("c"), _grid]
                                              for d in registry.DIFFICULTIES}}
        self.teaching = {"linear_equations": {
            "title": "T", "body": "x" * 40, "key_points": ["one", "two"]}}

    def _plan(self, exam_id):
        base = gen.PLANS[exam_id]
        return ExamPlan(
            exam_id=exam_id, exam_name=base.exam_name, seed=1,
            skills=[SkillSpec("linear_equations", tiers=(("easy", 8), ("medium", 8), ("hard", 8)))],
            domain_slug=base.domain_slug, skill_titles=base.skill_titles,
            option_count=base.option_count, bank_per_kind={"math": 10},
            transforms=base.transforms, exclude_family=base.exclude_family,
            accept_body=base.accept_body)

    def test_lessons_round_robin_across_families_and_are_unique(self):
        b = gen.Builder(self._plan("sat"), self.families, self.teaching)
        b.build_lessons()
        self.assertEqual(len(b.lessons), 3)
        for lesson in b.lessons:
            qs = b.questions_by_lesson[lesson["lesson_id"]]
            self.assertEqual(len(qs), 8)
            fams = [registry.family_of(q) for q in qs]
            # 4 families cycled over 8 items -> each twice, in order
            self.assertEqual(fams[:4], ["fam_a", "fam_b", "fam_c", "grid"])
            self.assertEqual(fams[4:], ["fam_a", "fam_b", "fam_c", "grid"])
            for q in qs:
                self.assertEqual(q["exam_id"], "sat")
                self.assertEqual(q["lesson_id"], lesson["lesson_id"])
                self.assertEqual(q["difficulty"], lesson["difficulty"])
                self.assertEqual(q["domain"], "math")
                self.assertEqual(q["section"], "algebra")
            self.assertEqual(lesson["question_ids"], [q["question_id"] for q in qs])
        self.assertEqual(b.lessons[1]["prerequisite_lesson_ids"], [b.lessons[0]["lesson_id"]])
        self.assertEqual(b.lessons[0]["prerequisite_lesson_ids"], [])
        self.assertEqual(b.lessons[0]["lesson_id"], "sat-math-linear-equations-easy")
        sigs = {util.item_signature(q) for qs in b.questions_by_lesson.values() for q in qs}
        self.assertEqual(len(sigs), 24)

    def test_act_skips_grid_ins_and_uses_five_choices(self):
        b = gen.Builder(self._plan("act"), self.families, self.teaching)
        b.build_lessons()
        b.build_bank()
        util.set_option_count(4)
        all_qs = [q for qs in b.questions_by_lesson.values() for q in qs]
        all_qs += [q for _, qs in b.bank_files.values() for q in qs]
        self.assertTrue(all_qs)
        for q in all_qs:
            self.assertNotEqual(q["question_type"], "student_produced")
            self.assertEqual(len(q["choices"]), 4)  # stub families only offer 4 options
            self.assertEqual(q["exam_id"], "act")
        self.assertEqual(b.lessons[0]["lesson_id"], "act-math-linear-equations-easy")

    def test_bank_is_deduplicated_against_lessons_and_itself(self):
        b = gen.Builder(self._plan("sat"), self.families, self.teaching)
        b.build_lessons()
        b.build_bank()
        util.set_option_count(4)
        self.assertEqual(len(b.bank_files), 3)
        bank = [q for _, qs in b.bank_files.values() for q in qs]
        self.assertEqual(len(bank), 30)
        sigs = {util.item_signature(q) for q in bank}
        lesson_sigs = {util.item_signature(q) for qs in b.questions_by_lesson.values() for q in qs}
        self.assertEqual(len(sigs), 30)
        self.assertFalse(sigs & lesson_sigs)
        self.assertTrue(all(q["question_id"].endswith(("-b0001", "-b0002", "-b0003", "-b0004",
                                                       "-b0005", "-b0006", "-b0007", "-b0008",
                                                       "-b0009", "-b0010")) for q in bank))

    def test_write_produces_manifest_and_files(self):
        b = gen.Builder(self._plan("sat"), self.families, self.teaching)
        b.build_lessons()
        with tempfile.TemporaryDirectory() as tmp:
            gen.CONTENT = Path(tmp)
            try:
                (Path(tmp) / "sat").mkdir()
                b.write()
                manifest = json.loads((Path(tmp) / "sat" / "manifest.json").read_text())
            finally:
                gen.CONTENT = ROOT / "content" / "exams"
            self.assertEqual(len(manifest["lessons"]), 3)
            self.assertEqual(len(manifest["questions"]), 3)
            self.assertEqual(manifest["bank"], [])
            self.assertTrue(all(p.startswith("lessons/math/") for p in manifest["lessons"]))

    def test_load_families_covers_every_family_skill_in_every_plan(self):
        families = gen.load_families()
        for exam_id, plan in gen.PLANS.items():
            for spec in plan.skills:
                if spec.kind != "family":
                    continue
                for diff, _ in spec.tiers:
                    fns = registry.families_for(families, spec.family_key, diff)
                    usable = [f for f in fns if not plan.exclude_family(f, "math")]
                    self.assertTrue(usable, f"{exam_id}: {spec.skill}/{diff} has no families")

    def test_load_teaching_covers_every_plan_skill(self):
        teaching = gen.load_teaching()
        for exam_id, plan in gen.PLANS.items():
            for spec in plan.skills:
                self.assertIn(spec.skill, teaching, f"{exam_id}: no teaching card for {spec.skill}")
                card = teaching[spec.skill]
                self.assertGreaterEqual(len(card["body"]), 30)
                self.assertGreaterEqual(len(card["key_points"]), 2)


class BundleToolTests(unittest.TestCase):
    def test_exams_index_lists_enabled_exams_with_descriptors(self):
        index = bundle_tool.exams_index()
        self.assertIn("sat", index["enabled"])
        by_id = {e["id"]: e for e in index["exams"]}
        self.assertEqual(set(by_id), set(index["enabled"]))
        self.assertEqual(by_id["sat"]["name"], "SAT")
        self.assertTrue(by_id["sat"]["tagline"])

    def test_build_exam_sorts_lessons_by_domain_order_then_order(self):
        for exam_dir in bundle_tool.exam_dirs():
            if not (exam_dir / "manifest.json").exists():
                continue
            bundle = bundle_tool.build_exam(exam_dir.name)
            domain_order = [d["id"] for d in bundle["skills"]["domains"]]
            keys = [(domain_order.index(l["domain"]), l["order"]) for l in bundle["lessons"]]
            self.assertEqual(keys, sorted(keys))
            self.assertEqual(bundle["schema_version"], 1)
            self.assertIn("timed_test", bundle["exam"])
            self.assertIn("scoring", bundle["exam"])


if __name__ == "__main__":
    unittest.main()


class ContentVersionLockTests(unittest.TestCase):
    """build_bundle.py must refuse content changes without a content_version bump."""

    def setUp(self):
        self.tmp = Path(tempfile.mkdtemp())
        self.exam_dir = self.tmp / "toy"
        self.exam_dir.mkdir()
        (self.exam_dir / "exam.yaml").write_text(
            'exam_id: toy\n# a comment that must survive\ncontent_version: "2.1.0"   # note\n')

    def tearDown(self):
        import shutil
        shutil.rmtree(self.tmp, ignore_errors=True)

    def _bundle(self, prompt="p1", version="2.1.0"):
        return {"schema_version": 1, "exam": {"exam_id": "toy", "content_version": version},
                "skills": {"domains": []}, "lessons": [], "questions": [{"prompt": prompt}]}

    def test_fingerprint_ignores_version_but_tracks_content(self):
        fp = bundle_tool.content_fingerprint
        self.assertEqual(fp(self._bundle(version="1.0.0")), fp(self._bundle(version="9.9.9")))
        self.assertNotEqual(fp(self._bundle("p1")), fp(self._bundle("p2")))
        b = self._bundle()
        b["exam"]["content_fingerprint"] = "anything"
        self.assertEqual(fp(b), fp(self._bundle()))

    def test_bump_version(self):
        self.assertEqual(bundle_tool.bump_version("2.1.0"), "2.2.0")
        self.assertEqual(bundle_tool.bump_version("2.1.3", "patch"), "2.1.4")
        self.assertEqual(bundle_tool.bump_version("2.1.3", "major"), "3.0.0")

    def test_lock_lifecycle(self):
        rec = bundle_tool.reconcile_lock
        fp1 = bundle_tool.content_fingerprint(self._bundle("p1"))
        fp2 = bundle_tool.content_fingerprint(self._bundle("p2"))
        self.assertEqual(rec(self.exam_dir, "2.1.0", fp1), ("2.1.0", "created"))
        self.assertEqual(rec(self.exam_dir, "2.1.0", fp1), ("2.1.0", "unchanged"))
        # Content changed, version not bumped: refused, lock untouched.
        with self.assertRaises(bundle_tool.ContentVersionError):
            rec(self.exam_dir, "2.1.0", fp2)
        lock = json.loads((self.exam_dir / "content.lock.json").read_text())
        self.assertEqual(lock, {"content_version": "2.1.0", "fingerprint": fp1})
        # --bump edits exam.yaml (keeping comments) and records the new state.
        self.assertEqual(rec(self.exam_dir, "2.1.0", fp2, bump=True), ("2.2.0", "bumped"))
        text = (self.exam_dir / "exam.yaml").read_text()
        self.assertIn('content_version: "2.2.0"   # note', text)
        self.assertIn("# a comment that must survive", text)
        # A manual bump with new content is simply recorded.
        fp3 = bundle_tool.content_fingerprint(self._bundle("p3"))
        self.assertEqual(rec(self.exam_dir, "2.3.0", fp3), ("2.3.0", "recorded"))

    def test_real_exams_are_locked_and_current(self):
        for exam_dir in bundle_tool.exam_dirs():
            lock = json.loads((exam_dir / "content.lock.json").read_text())
            bundle = bundle_tool.build_exam(exam_dir.name)
            self.assertEqual(lock["fingerprint"], bundle["exam"]["content_fingerprint"],
                             f"{exam_dir.name}: content changed; run build_bundle.py --bump")
            self.assertEqual(lock["content_version"], str(bundle["exam"]["content_version"]))
