"""Tests for the deterministic answer-key checks (tools/audit/automated_checks.py)
and the independent stem re-solvers (tools/audit/solvers.py)."""
from __future__ import annotations

import unittest

from tools.tests import helpers  # noqa: F401  (sets sys.path)
from audit import automated_checks as ac
from audit import solvers

LETTERS = "ABCDE"


def mcq(prompt, texts, correct, explanation="See the work.", *, rationales=None,
        verify=None, family="fam", stimulus=None):
    choices = [{"id": LETTERS[i], "text": t,
                "rationale": (rationales or {}).get(LETTERS[i],
                                                    "Correct." if LETTERS[i] == correct else "Slip.")}
               for i, t in enumerate(texts)]
    q = {"question_id": "t-q", "exam_id": "sat", "domain": "math", "difficulty": "easy",
         "question_type": "multiple_choice", "prompt": prompt, "choices": choices,
         "correct_choice": correct, "explanation": explanation, "tags": [f"family:{family}"]}
    if verify:
        q["answer_verification"] = verify
    if stimulus:
        q["stimulus"] = stimulus
    return q


def gridin(prompt, value, accepted, explanation="See the work."):
    return {"question_id": "t-g", "exam_id": "sat", "domain": "math", "difficulty": "easy",
            "question_type": "student_produced", "prompt": prompt, "explanation": explanation,
            "answer": {"type": "numeric", "value": value, "accepted": accepted, "tolerance": 0.0},
            "tags": ["family:grid"]}


def resolve(q):
    return ac.check_resolve(q)


class StructureChoicesRationaleTest(unittest.TestCase):
    def test_structure(self):
        self.assertEqual(ac.check_structure(mcq("Q?", ["1", "2"], "A")), ac.PASS)
        self.assertIn("not exactly once", ac.check_structure(mcq("Q?", ["1", "2"], "C")))
        q = mcq("Q?", ["1", "2"], "A")
        q["choices"][1]["id"] = "A"
        self.assertIn("duplicate choice ids", ac.check_structure(q))
        self.assertEqual(ac.check_structure(gridin("Q?", 21, ["21"])), ac.PASS)
        self.assertIn("!= value", ac.check_structure(gridin("Q?", 21, ["22"])))
        self.assertIn("does not parse", ac.check_structure(gridin("Q?", 21, ["twenty"])))

    def test_choice_texts_unique(self):
        self.assertIn("same text", ac.check_choices(mcq("Q?", ["The cat.", "the  cat", "dog"], "C")))
        # two choices with the keyed value: two right answers
        self.assertIn("both correct", ac.check_choices(mcq("Q?", ["98.0", "98", "111"], "B")))
        self.assertIn("both correct", ac.check_choices(mcq("Q?", ["√3", "3√3/9", "√3/3"], "C")))
        # forms are not values: "1 × 93" and "3 × 31" are different answers to a factoring item
        self.assertEqual(ac.check_choices(mcq("Q?", ["1 × 93", "3 × 31", "3 × 32"], "B")), ac.PASS)
        # ranges are not subtractions
        self.assertEqual(ac.check_choices(mcq("Q?", ["100–119", "120–139"], "A")), ac.PASS)

    def test_duplicate_distractors_are_warnings(self):
        q = mcq("Q?", ["10", "√100", "4√2"], "C")
        self.assertEqual(ac.check_choices(q), ac.PASS)
        self.assertIn("distractors A and B", ac.check_dup_distractors(q))

    def test_rationale_contradictions(self):
        q = mcq("Q?", ["1", "2"], "A", rationales={"B": "Correct: this is it."})
        self.assertIn("wrong choice B", ac.check_rationale(q))
        q = mcq("Q?", ["1", "2"], "A", rationales={"A": "Incorrect; recheck."})
        self.assertIn("keyed choice A", ac.check_rationale(q))
        q = mcq("Q?", ["1", "2"], "A", rationales={"B": "Correctly read, but the wrong row."})
        self.assertEqual(ac.check_rationale(q), ac.PASS)


class ArithmeticClaimsTest(unittest.TestCase):
    def test_claims_extracted_without_variables(self):
        claims = ac.arith_claims("Subtract 26: 3x = 24. f(3) = 11·(3) + 15 = 33 + 15 = 48.")
        self.assertIn(("11·(3) + 15", "33 + 15"), claims)
        self.assertIn(("33 + 15", "48"), claims)
        self.assertFalse(any("x" in a or "x" in b for a, b in claims))
        self.assertEqual(ac.arith_claims("x − 2 = −18, so 2x + 16 = 48"), [])
        self.assertEqual(ac.arith_claims("42:22 = 21:11"), [])

    def test_false_claims_fail(self):
        q = mcq("What is 25% of 275?", ["68", "69"], "A", "(25/100)·275 = 68.")
        self.assertIn("claims", ac.check_arithmetic(q))
        q = mcq("Q?", ["446"], "A", "Interest: 2480·0.03·6 = 446. Then …")
        self.assertIn("2480·0.03·6 = 446", ac.check_arithmetic(q))
        q = mcq("Q?", ["35"], "A", "√(-21² + (−28)²) = √1225 = 35.")
        self.assertIn("claims", ac.check_arithmetic(q))

    def test_true_claims_and_display_rounding_pass(self):
        for expl in ("263 ÷ 9 = 29.22, so at most 29.", "450/900 × 100 = 50%.",
                     "5% of 405 = (5/100)·405 = 20.25.", "√(5² + 5²) = √50 = 5√2.",
                     "Mean = 80 ÷ 5 = 16.", "From 61 − 9 = 52 to 61 + 9 = 70."):
            with self.subTest(expl=expl):
                self.assertEqual(ac.check_arithmetic(mcq("Q?", ["1", "2"], "A", expl)), ac.PASS)

    def test_verification_string_checked_too(self):
        q = mcq("Q?", ["5/4"], "A", "Multiply by the reciprocal.", verify="3/8÷3/10=5/4")
        self.assertEqual(ac.check_arithmetic(q), ac.PASS)
        q = mcq("Q?", ["20"], "A", "Multiply.", verify="5% of 405=20")
        self.assertIn("answer_verification", ac.check_arithmetic(q))


class FinalValueTest(unittest.TestCase):
    def test_final_value_extraction(self):
        self.assertEqual(ac.final_value("Subtract 26: 3x = 24. Divide by 3: x = 8."), 8)
        self.assertEqual(ac.final_value("The greatest is 9."), 9)
        self.assertEqual(ac.final_value("518 miles (37 × 14)."), None)
        self.assertEqual(ac.final_value("≈ 80% decrease."), -ac.parse_number("80%"))
        self.assertIsNone(ac.final_value("The mean changes far more."))

    def test_mismatch_fails_and_names_other_choice(self):
        q = mcq("Q?", ["8", "9"], "A", "So x = 9.")
        self.assertIn("(= choice B)", ac.check_final_value(q))

    def test_key_stated_earlier_passes(self):
        q = mcq("What is the x-coordinate?", ["27", "3"], "B",
                "9x = 27 → x = 3. Then y = 6(3) + 9 = 27.")
        self.assertEqual(ac.check_final_value(q), ac.PASS)

    def test_rounded_key_needs_rounding_instruction(self):
        expl = "New total = 188; mean = 94/3."
        q = mcq("What is the new mean?", ["31.33", "22"], "A", expl)
        self.assertNotEqual(ac.check_final_value(q), ac.PASS)
        q = mcq("What is the new mean? (Round to the nearest hundredth.)", ["31.33", "22"], "A", expl)
        self.assertEqual(ac.check_final_value(q), ac.PASS)

    def test_gridin_final_value(self):
        self.assertEqual(ac.check_final_value(gridin("Q?", 16, ["16"], "So x = 16.")), ac.PASS)
        self.assertNotEqual(ac.check_final_value(gridin("Q?", 68, ["68"], "So it is 68.75.")),
                            ac.PASS)


class VerificationTest(unittest.TestCase):
    def test_equation_at_value(self):
        q = mcq("In the equation 3x + 26 = 50, what is the value of x?", ["8", "9"], "A",
                verify="3x + 26 = 50 at x=8")
        self.assertEqual(ac.check_verification(q), ac.PASS)
        q["answer_verification"] = "x=9 satisfies 3x + 26 = 50"
        self.assertIn("does not satisfy", ac.check_verification(q))

    def test_val_against_key(self):
        self.assertEqual(ac.check_verification(mcq("Q?", ["13", "14"], "A", verify="val=13")), ac.PASS)
        self.assertIn("but key", ac.check_verification(mcq("Q?", ["13", "14"], "B", verify="val=13")))
        self.assertEqual(ac.check_verification(mcq("Q?", ["$61.88"], "A", verify="val=495/8")), ac.PASS)


class SolverTest(unittest.TestCase):
    def assertResolves(self, q):
        self.assertIsNotNone(solvers.expectation(q), "no solver recognised the stem")
        self.assertEqual(resolve(q), ac.PASS)

    def assertResolveFails(self, q, fragment=""):
        r = resolve(q)
        self.assertNotIn(r, (ac.PASS, ac.SKIP))
        self.assertIn(fragment, r)

    def test_linear_and_quadratic_equations(self):
        self.assertResolves(mcq("In the equation 3x + 26 = 50, what is the value of x?",
                                ["8", "50/3", "9", "24"], "A"))
        self.assertResolveFails(mcq("In the equation 3x + 26 = 50, what is the value of x?",
                                    ["8", "50/3", "9", "24"], "C"), "= choice A")
        self.assertResolves(mcq("If 8x − 14 = −6, what is the value of 16x − 28?",
                                ["-12", "1", "-6", "16"], "A"))
        self.assertResolves(mcq("What is the lesser of the two solutions to the equation (x − 7)(x + 6) = 0?",
                                ["7", "1", "6", "-6"], "D"))
        self.assertResolves(mcq("If |x − 24| = 17, what is the greatest possible value of x?",
                                ["-7", "41", "42", "7"], "B"))
        self.assertResolves(mcq("For what value of x is 11^x equal to 121?", ["11", "3", "2", "1"], "C"))
        self.assertResolves(gridin("2x + 16 = 48\nWhat is the solution to the given equation?", 16, ["16"]))

    def test_evaluate_and_percent(self):
        self.assertResolves(mcq("What is the value of |−3 − −16|?", ["14", "19", "-13", "13"], "D"))
        self.assertResolveFails(gridin("What is 25% of 275?", 68, ["68"]), "275/4")
        self.assertResolves(gridin("What is 25% of 275?", 68.75, ["275/4", "68.75"]))
        self.assertResolves(mcq("What is the product (4 + 5i)(4 − 5i)?", ["-9", "41", "16"], "B"))
        self.assertResolveFails(mcq("A store has 175 items in stock, and 10% of them are on sale. "
                                    "How many items are on sale?", ["17", "35/2", "25"], "A"))

    def test_functions(self):
        self.assertResolves(mcq("The functions f and g are defined by f(x) = 4x + 1 and g(x) = 3x − 4. "
                                "What is the value of f(g(−2))?", ["-10", "-39", "-25"], "B"))
        self.assertResolves(mcq("The function f is defined by f(x) = 2x² + 1, and the function g is "
                                "defined by g(x) = f(x + 3) + 3. What is the value of g(−3)?",
                                ["1", "76", "4", "22"], "C"))
        self.assertResolveFails(mcq("The function f is defined by f(x) = (x + 3)/(x + 3). For what "
                                    "value of x is f(x) = 0?", ["-3", "3", "0"], "A"))
        self.assertResolves(mcq("The function f is defined by f(x) = −(x − 8)² + 1. What is the "
                                "maximum value of f?", ["8", "-8", "-1", "1"], "D"))

    def test_systems_lines_inequalities(self):
        self.assertResolves(mcq("x + 5y = 45\n4x − y = 12\nWhat is the value of y for the solution "
                                "(x, y) of the system above?", ["8", "5", "13", "-8"], "A"))
        self.assertResolves(mcq("In the xy-plane, the graphs of y = x + 7 and y = 5x + 35 intersect "
                                "at which point?", ["(−7, 0)", "(−7, 2)", "(0, −7)"], "A"))
        self.assertResolves(mcq("Which of the following describes all values of x that satisfy "
                                "|x − 8| < 5?", ["x < 13", "x < 3 or x > 13", "3 < x < 13"], "C"))
        self.assertResolveFails(mcq("Which of the following is NOT a solution to the inequality "
                                    "−44 ≤ 8x + 20 < −28?", ["-8", "-1", "-7", "-6"], "D"),
                                "all correct")
        self.assertResolves(mcq("Which of the following points lies on the graph of y = −7x − 9 "
                                "in the xy-plane?", ["(5, −44)", "(−3, 9)", "(2, −26)"], "A"))

    def test_equivalent_forms(self):
        self.assertResolveFails(mcq("Which of the following is equivalent to 12x² + 21x?",
                                    ["3x(4x + 7)", "x(12x + 21)", "3(4x + 7)"], "A"), "all correct")
        self.assertResolves(mcq("Which of the following is equivalent to (30x² + 30x) ÷ 5x?",
                                ["6x² + 6x", "6x + 30", "6x + 6"], "C"))
        self.assertResolves(mcq("If 9x + 3y = 30, which of the following expresses y in terms of x?",
                                ["y = 30 − 9x", "y = (30 − 9x)/3", "y = (30 − 9x)/9"], "B"))

    def test_statistics_and_probability(self):
        self.assertResolves(mcq("What is the interquartile range of the data set 3, 4, 58, 3, 50, "
                                "49, 39, 37?", ["46", "55", "38", "99/2"], "A"))
        self.assertResolves(mcq("A bag contains 8 green, 10 purple, and 2 blue beads. If one of the "
                                "beads is chosen at random, what is the probability that it is green?",
                                ["3/5", "2/3", "2/5", "9/20"], "C"))
        # "about how many": nearest whole number
        self.assertResolves(mcq("A survey found that 45% of a town's residents use public transit. "
                                "If 750 residents are selected at random, about how many would be "
                                "expected to use public transit?", ["338", "412", "45"], "A"))
        # a statistic that is not "what is the mean" is not misread as one
        self.assertIsNone(solvers.expectation(mcq(
            "Ravi's scores were 31, 39, 18, 31. What score does Ravi need on the fifth quiz for the "
            "mean of all 5 scores to be exactly 25?", ["6", "25"], "A")))

    def test_unrecognised_stems_skip(self):
        q = mcq("Which choice best states the main idea of the text?", ["A", "B"], "A")
        self.assertIsNone(solvers.expectation(q))
        self.assertEqual(resolve(q), ac.SKIP)


class AuditReportTest(unittest.TestCase):
    def test_audit_groups_by_family(self):
        good = mcq("In the equation 3x + 26 = 50, what is the value of x?", ["8", "9"], "A",
                   "x = 8.", family="le_two_step")
        bad = dict(good, correct_choice="B", question_id="t-bad")
        warn = mcq("Q?", ["10", "√100", "4√2"], "C", family="cg_distance")
        rep = ac.audit(("sat",), questions_by_exam={"sat": [good, bad, warn]})
        self.assertEqual(rep["questions"], 3)
        self.assertEqual(rep["failed_questions"], 1)
        fams = {f["family"]: f for f in rep["families"]}
        self.assertEqual(fams["le_two_step"]["failed"], 1)
        self.assertEqual(fams["le_two_step"]["examples"][0]["question_id"], "t-bad")
        self.assertEqual(fams["cg_distance"]["failed"], 0)
        self.assertEqual(fams["cg_distance"]["warnings"], 1)
        text = ac.format_report(rep)
        self.assertIn("sat:le_two_step", text)
        self.assertIn("Families with warnings", text)


if __name__ == "__main__":
    unittest.main()
