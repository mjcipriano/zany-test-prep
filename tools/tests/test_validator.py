"""Tests for the content validator's checks, using tiny synthetic exams."""
import importlib.util
import json
import shutil
import tempfile
import unittest
from pathlib import Path

import yaml

from tools.tests import helpers

ROOT = helpers.ROOT


def _load_validator():
    spec = importlib.util.spec_from_file_location("validate_content", ROOT / "tools" / "validate_content.py")
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


validator = _load_validator()


def _question(qid, lesson_id, i, *, family="fam_a", qtype="multiple_choice"):
    q = {
        "question_id": qid, "exam_id": "toy", "exam_name": "TOY",
        "domain": "math", "section": "algebra", "skill": "adding",
        "subskill": "ints", "lesson_id": lesson_id, "difficulty": "easy",
        "question_type": qtype, "estimated_time_seconds": 30,
        "prompt": f"What is {i} + {i + 1}?", "explanation": "Add the two integers.",
        "version": "1.0.0", "tags": ["t", f"family:{family}"],
    }
    if qtype == "student_produced":
        q["answer"] = {"type": "numeric", "value": 2 * i + 1, "accepted": [str(2 * i + 1)],
                       "tolerance": 0}
    else:
        correct = ["A", "B", "C", "D"][i % 4]
        q["choices"] = [{"id": c, "text": str(2 * i + 1 + k), "rationale": "Correct." if c == correct else "Slip."}
                        for k, c in enumerate(["A", "B", "C", "D"])]
        q["correct_choice"] = correct
    return q


class ToyExam:
    """Writes a minimal valid exam under a temp content root."""

    def __init__(self, n_lessons=40, per_lesson=8, families=("fam_a", "fam_b", "fam_c", "fam_d")):
        self.tmp = Path(tempfile.mkdtemp())
        self.exam_dir = self.tmp / "exams" / "toy"
        (self.exam_dir / "lessons").mkdir(parents=True)
        (self.exam_dir / "questions").mkdir()
        shutil.copytree(ROOT / "content" / "schemas", self.tmp / "schemas")
        (self.exam_dir / "exam.yaml").write_text(yaml.safe_dump({
            "exam_id": "toy", "exam_name": "TOY", "content_version": "1.0.0",
            "domains": ["math"], "timed_test": {"modules": [{"name": "M", "domain": "math",
                                                              "count": 5, "minutes": 5}]}}))
        (self.exam_dir / "skills.yaml").write_text(yaml.safe_dump({
            "exam_id": "toy", "domains": [{"id": "math", "name": "Math", "sections": [
                {"id": "algebra", "name": "Algebra", "skills": [
                    {"id": "adding", "name": "Adding", "subskills": ["ints"]}]}]}]}))
        self.lessons, self.questions = [], {}
        counter = 0
        for n in range(n_lessons):
            lid = f"toy-math-adding-{n}"
            qs = []
            for i in range(per_lesson):
                qs.append(_question(f"{lid}-q{i:02d}", lid, counter, family=families[i % len(families)]))
                counter += 1
            self.lessons.append({
                "lesson_id": lid, "exam_id": "toy", "exam_name": "TOY", "domain": "math",
                "section": "algebra", "skill": "adding", "title": f"Lesson {n}", "order": n,
                "difficulty": "easy", "estimated_minutes": 5,
                "teaching_card": {"title": "Adding", "body": "Add the numbers carefully, left to right.",
                                  "key_points": ["Line up digits.", "Carry when needed."]},
                "question_ids": [q["question_id"] for q in qs],
                "prerequisite_lesson_ids": [], "unlock_xp": 0, "tags": ["math"], "version": "1.0.0"})
            self.questions[lid] = qs

    def write(self):
        manifest = {"exam_id": "toy", "version": "1.0.0", "lessons": [], "questions": [], "bank": []}
        for lesson in self.lessons:
            lp = self.exam_dir / "lessons" / f"{lesson['lesson_id']}.json"
            lp.write_text(json.dumps(lesson))
            manifest["lessons"].append(str(lp.relative_to(self.exam_dir)))
            qp = self.exam_dir / "questions" / f"{lesson['lesson_id']}.json"
            qp.write_text(json.dumps(self.questions[lesson["lesson_id"]]))
            manifest["questions"].append(str(qp.relative_to(self.exam_dir)))
        (self.exam_dir / "manifest.json").write_text(json.dumps(manifest))
        return self

    def validate(self):
        validator.CONTENT = self.tmp
        validator.SCHEMAS = self.tmp / "schemas"
        try:
            rep = validator.Report()
            validator.validate_exam("toy", rep)
            return rep
        finally:
            validator.CONTENT = ROOT / "content"
            validator.SCHEMAS = ROOT / "content" / "schemas"
            shutil.rmtree(self.tmp, ignore_errors=True)


class ValidatorTests(unittest.TestCase):
    def test_clean_toy_exam_only_fails_aggregate_minimums(self):
        rep = ToyExam().write().validate()
        # 40 lessons * 8 = 320 questions: below the 1000 minimum but otherwise clean.
        self.assertTrue(all("need >=" in e for e in rep.errors), rep.errors)
        self.assertEqual(rep.stats["low_variety_lessons"], 0)
        self.assertEqual(rep.stats["duplicate_prompts"], 0)

    def test_low_variety_lesson_is_flagged(self):
        toy = ToyExam(families=("only",)).write()
        rep = toy.validate()
        self.assertEqual(rep.stats["low_variety_lessons"], 40)
        self.assertTrue(any("low variety" in e for e in rep.errors))

    def test_two_families_with_one_dominant_is_flagged(self):
        toy = ToyExam(families=("a", "a", "a", "b")).write()
        rep = toy.validate()
        self.assertEqual(rep.stats["low_variety_lessons"], 40)

    def test_authored_lessons_without_family_tags_are_exempt(self):
        toy = ToyExam()
        for qs in toy.questions.values():
            for q in qs:
                q["tags"] = ["t"]
        rep = toy.write().validate()
        self.assertEqual(rep.stats["low_variety_lessons"], 0)

    def test_duplicate_prompt_wrong_answer_and_bad_refs_are_errors(self):
        toy = ToyExam()
        first = toy.questions[toy.lessons[0]["lesson_id"]]
        first[1]["prompt"] = first[0]["prompt"]
        first[1]["choices"] = [dict(c) for c in first[0]["choices"]]
        first[2]["correct_choice"] = "F"
        first[3]["skill"] = "ghost"
        first[4]["subskill"] = "nope"
        toy.lessons[1]["prerequisite_lesson_ids"] = ["missing-lesson"]
        unknown = toy.exam_dir  # keep reference alive
        rep = toy.write().validate()
        msgs = "\n".join(rep.errors)
        self.assertIn("near-duplicate", msgs)
        self.assertIn("correct_choice not among choices", msgs)
        self.assertIn("unknown skill ghost", msgs)
        self.assertIn("missing prerequisite lesson", msgs)
        self.assertTrue(any("subskill 'nope'" in w for w in rep.warnings))
        del unknown

    def test_timed_test_module_domain_must_exist(self):
        toy = ToyExam()
        (toy.exam_dir / "exam.yaml").write_text(yaml.safe_dump({
            "exam_id": "toy", "exam_name": "TOY", "content_version": "1.0.0",
            "domains": ["math", "ghost"],
            "timed_test": {"modules": [{"name": "M", "domain": "nope", "count": 1, "minutes": 1}]}}))
        rep = toy.write().validate()
        msgs = "\n".join(rep.errors)
        self.assertIn("domain 'ghost' is not in skills.yaml", msgs)
        self.assertIn("unknown domain 'nope'", msgs)

    def test_position_tell_is_an_error(self):
        toy = ToyExam()
        for qs in toy.questions.values():
            for q in qs:
                q["correct_choice"] = "A"
                for c in q["choices"]:
                    c["rationale"] = "Correct." if c["id"] == "A" else "Slip."
        rep = toy.write().validate()
        self.assertTrue(any("one position" in e for e in rep.errors))

    def test_helpers(self):
        self.assertTrue(validator._parse_numeric("3/4"))
        self.assertTrue(validator._parse_numeric("-2.5"))
        self.assertFalse(validator._parse_numeric("x"))
        self.assertEqual(validator._first_word("The dog's"), "the")
        self.assertEqual(validator.normalize_prompt("x − 2 = 4"), "x - 2 4")


if __name__ == "__main__":
    unittest.main()
