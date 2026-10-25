"""Tests for the human-style audit export (tools/audit/export_sample.py) and the
solver-vs-key comparison (tools/audit/compare.py)."""
from __future__ import annotations

import contextlib
import io
import json
import tempfile
import unittest
from pathlib import Path

from tools.tests import helpers  # noqa: F401  (sets sys.path)
from audit import compare, export_sample


def _q(exam, n, family, diff, *, grid=False, stimulus=None):
    q = {
        "question_id": f"{exam}-{family.replace('_', '-')}-{diff}-q{n:02d}",
        "exam_id": exam, "exam_name": exam.upper(), "domain": "math", "section": "algebra",
        "skill": "linear_equations", "subskill": "one_variable", "lesson_id": "l",
        "difficulty": diff, "version": "1.0.0", "prompt": f"Prompt {n}?",
        "explanation": "Because the secret answer is B.", "answer_verification": "val=42",
        "estimated_time_seconds": 60, "tags": ["algebra", f"family:{family}", "act-no-change"],
    }
    if grid:
        q["question_type"] = "student_produced"
        q["answer"] = {"type": "numeric", "value": 0.75, "accepted": ["3/4", ".75"], "tolerance": 0}
    else:
        q["question_type"] = "multiple_choice"
        q["choices"] = [{"id": c, "text": f"{c} text", "rationale": "Correct." if c == "B" else "No."}
                        for c in "ABCD"]
        q["correct_choice"] = "B"
    if stimulus:
        q["stimulus"] = stimulus
    return q


def _bank():
    sat = [_q("sat", i, fam, d) for fam in ("le_two_step", "q_roots") for d in ("easy", "hard")
           for i in range(5)]
    sat += [_q("sat", 90 + i, "grid", "easy", grid=True) for i in range(3)]
    act = [_q("act", i, "le_two_step", "medium",
              stimulus={"type": "table", "table": {"headers": ["x"], "rows": [["1"]]}}) for i in range(4)]
    act.append(dict(_q("act", 50, "x", "easy"), tags=["reading"], skill="main_idea"))  # authored
    return {"sat": sat, "act": act}


class ExportTest(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.out = Path(self.tmp.name)

    def tearDown(self):
        self.tmp.cleanup()

    def test_stratified_up_to_two_per_stratum(self):
        sample = export_sample.stratified_sample(_bank(), per_stratum=2, max_total=1000)
        strata = {}
        for q in sample:
            k = (q["exam_id"], export_sample.family_key(q), q["difficulty"])
            strata[k] = strata.get(k, 0) + 1
        # 4 sat family×difficulty strata + sat grid + act family + act authored
        self.assertEqual(len(strata), 7)
        self.assertTrue(all(1 <= n <= 2 for n in strata.values()))
        self.assertEqual(strata[("act", "authored-main_idea", "easy")], 1)

    def test_max_total_keeps_one_per_stratum(self):
        sample = export_sample.stratified_sample(_bank(), per_stratum=2, max_total=8)
        self.assertEqual(len(sample), 8)
        keys = {(q["exam_id"], export_sample.family_key(q), q["difficulty"]) for q in sample}
        self.assertEqual(len(keys), 7)  # every stratum still represented

    def test_deterministic(self):
        a = [q["question_id"] for q in export_sample.stratified_sample(_bank(), seed=7)]
        b = [q["question_id"] for q in export_sample.stratified_sample(_bank(), seed=7)]
        c = [q["question_id"] for q in export_sample.stratified_sample(_bank(), seed=8)]
        self.assertEqual(a, b)
        self.assertNotEqual(a, c)

    def test_batches_leak_nothing(self):
        res = export_sample.export(_bank(), self.out, batch_size=4, max_total=1000)
        self.assertEqual(len(res["batches"]), (res["questions"] + 3) // 4)
        seen = 0
        for p in res["batches"]:
            batch = json.loads(Path(p).read_text())
            self.assertIn("solved_", batch["instructions"])
            for q in batch["questions"]:
                seen += 1
                for leaky in export_sample.LEAKY_FIELDS:
                    self.assertNotIn(leaky, q)
                for c in q.get("choices", []):
                    self.assertEqual(set(c), {"id", "text"})
                self.assertLessEqual(set(q), set(export_sample.STUDENT_FIELDS) | {"answer_format"})
                blob = json.dumps(q)
                self.assertNotIn("secret answer", blob)   # explanation text
                self.assertNotIn("Correct.", blob)        # rationales
                self.assertNotIn("family:", blob)         # tags
                self.assertNotIn("val=42", blob)          # answer_verification
                self.assertNotIn("0.75", blob)            # grid-in value
        self.assertEqual(seen, res["questions"])

    def test_key_matches_batches(self):
        res = export_sample.export(_bank(), self.out, batch_size=5)
        key = json.loads(Path(res["key"]).read_text())
        ids = [q["question_id"] for p in res["batches"]
               for q in json.loads(Path(p).read_text())["questions"]]
        self.assertEqual(sorted(ids), sorted(key))
        mc = next(v for v in key.values() if v["question_type"] == "multiple_choice")
        self.assertEqual(mc["answer"], "B")
        self.assertEqual(mc["answer_text"], "B text")
        self.assertIn("family", mc)
        grid = next(v for v in key.values() if v["question_type"] == "student_produced")
        self.assertEqual(grid["answer"], 0.75)
        self.assertEqual(grid["accepted"], ["3/4", ".75"])

    def test_stimulus_is_kept(self):
        view = export_sample.student_view(_bank()["act"][0])
        self.assertEqual(view["stimulus"]["type"], "table")


class CompareTest(unittest.TestCase):
    KEY = {
        "q1": {"exam": "sat", "family": "le_two_step", "difficulty": "easy",
               "question_type": "multiple_choice", "answer": "B", "answer_text": "8"},
        "q2": {"exam": "sat", "family": "le_two_step", "difficulty": "hard",
               "question_type": "multiple_choice", "answer": "C", "answer_text": "x"},
        "q3": {"exam": "sat", "family": "grid", "difficulty": "easy",
               "question_type": "student_produced", "answer": 0.75, "accepted": ["3/4", ".75"],
               "tolerance": 0},
        "q4": {"exam": "act", "family": "q_roots", "difficulty": "easy",
               "question_type": "multiple_choice", "answer": "A"},
    }

    def test_choice_normalization(self):
        for given in ("B", "b", "(B)", "B)", "B. 8", "Choice B", " B "):
            self.assertEqual(compare.normalize_choice(given), "B", given)
        self.assertIsNone(compare.normalize_choice("8"))

    def test_gridin_matching(self):
        e = self.KEY["q3"]
        for given in ("3/4", "0.75", ".75", 0.75):
            self.assertTrue(compare.answers_match(e, given), given)
        self.assertFalse(compare.answers_match(e, "0.7"))
        self.assertFalse(compare.answers_match(e, "three quarters"))

    def test_report_groups_disagreements_by_family(self):
        solved = {
            "q1": {"answer": "B", "confidence": "high", "note": "x = 8"},
            "q2": {"answer": "A", "confidence": "high", "note": "C is not equivalent"},
            "q3": {"answer": "3/4", "confidence": "medium"},
            "zz": {"answer": "A"},
        }
        rep = compare.compare(self.KEY, solved)
        self.assertEqual((rep["answered"], rep["agree"], rep["disagree"], rep["missing"]), (3, 2, 1, 1))
        self.assertEqual(rep["high_conf_disagree"], 1)
        self.assertEqual(rep["unknown_ids"], ["zz"])
        top = rep["families"][0]
        self.assertEqual(top["family"], "sat:le_two_step")
        self.assertEqual(top["disagree"][0]["question_id"], "q2")
        text = compare.format_report(rep, {"q2": "Which is equivalent?"})
        self.assertIn("### sat:le_two_step - 1 of 2 disagree (1 high confidence)", text)
        self.assertIn("C is not equivalent", text)
        self.assertIn("Which is equivalent?", text)
        self.assertIn("Unanswered (1)", text)

    def test_cli_end_to_end(self):
        with tempfile.TemporaryDirectory() as d:
            d = Path(d)
            res = export_sample.export(_bank(), d, batch_size=100)
            key = json.loads(Path(res["key"]).read_text())
            # a solver that agrees with everything except one item
            answers = {qid: {"answer": v["answer"] if v["question_type"] != "student_produced" else "3/4",
                             "confidence": "high", "note": ""} for qid, v in key.items()}
            flipped = next(q for q, v in key.items() if v["question_type"] == "multiple_choice")
            answers[flipped]["answer"] = "D"
            (d / "solved_01.json").write_text(json.dumps(answers))
            out, js = d / "report.md", d / "report.json"
            with contextlib.redirect_stdout(io.StringIO()):
                self.assertEqual(compare.main(["--dir", str(d), "--out", str(out), "--json", str(js)]), 0)
            rep = json.loads(js.read_text())
            self.assertEqual(rep["disagree"], 1)
            self.assertEqual(rep["missing"], 0)
            self.assertIn(flipped, out.read_text())

    def test_partial_run_only_reports_its_own_gaps(self):
        with tempfile.TemporaryDirectory() as d:
            d = Path(d)
            res = export_sample.export(_bank(), d, batch_size=3)
            first = json.loads(Path(res["batches"][0]).read_text())["questions"]
            (d / "solved_01.json").write_text(json.dumps({first[0]["question_id"]: {"answer": "B"}}))
            js = d / "r.json"
            with contextlib.redirect_stdout(io.StringIO()):
                compare.main(["--dir", str(d), "--out", str(d / "r.md"), "--json", str(js)])
            rep = json.loads(js.read_text())
            self.assertEqual(rep["missing"], len(first) - 1)


if __name__ == "__main__":
    unittest.main()
