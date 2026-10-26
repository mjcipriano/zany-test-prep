"""Tests for the audit's exact-arithmetic expression engine (tools/audit/expr.py)."""
from __future__ import annotations

import unittest
from fractions import Fraction

from tools.tests import helpers  # noqa: F401  (sets sys.path)
from audit.expr import (ExprError, Poly, evaluate, holds, normalize, num_equal, parse,
                        parse_equation, parse_function_def, parse_number, solve_linear_system,
                        solve_univariate)


class EvaluateTest(unittest.TestCase):
    def test_bank_notation(self):
        cases = {
            "|−3 − −16|": 13, "√252 · √112": 168, "−3^2": -9, "(−5)^3": -125,
            "7 + 5 × 2 − 8": 9, "log_4 64": 3, "log₁₀(10)": 1, "2.75 × 10^7": 27500000,
            "(25/100)·275": Fraction(275, 4), "⅓·12·11": 44, "√(12² + 16²)": 20,
            "81^(3/4)": 27, "8^24": 8 ** 24, "450/900 × 100": 50,
        }
        for text, want in cases.items():
            with self.subTest(text=text):
                self.assertEqual(evaluate(text), want)

    def test_inline_fractions_read_as_numbers(self):
        # A student reads 3/8 ÷ 3/10 as (3/8) ÷ (3/10), not ((3/8)/3)/10.
        self.assertEqual(evaluate("3/8 ÷ 3/10"), Fraction(5, 4))
        self.assertEqual(evaluate("243/25 ÷ 27/25"), 9)
        # ...but a radical over a number stays "radical, then divide".
        self.assertTrue(num_equal(evaluate("√2/2"), 2 ** 0.5 / 2))
        self.assertTrue(num_equal(evaluate("3√3/9"), 3 ** 0.5 / 3))

    def test_irrationals_are_floats(self):
        self.assertTrue(num_equal(evaluate("54π"), 54 * 3.141592653589793))
        self.assertTrue(num_equal(evaluate("4√7 + 8√7"), 12 * 7 ** 0.5))

    def test_rejects_unknown_notation(self):
        for bad in ("x + 1 = ", "3 +", "√(−4)", "ln(0)", "2 ? 3"):
            with self.subTest(bad=bad), self.assertRaises((ExprError, ZeroDivisionError)):
                evaluate(bad)

    def test_normalize(self):
        self.assertEqual(normalize("x² − 4"), "x^(2) - 4")


class PolyTest(unittest.TestCase):
    def test_equivalence(self):
        self.assertEqual(parse("(x + 2)² + 9"), parse("x² + 4x + 13"))
        self.assertEqual(parse("3x(4x + 7)"), parse("12x² + 21x"))
        self.assertNotEqual(parse("3x(4x − 7)"), parse("12x² + 21x"))
        self.assertEqual(parse("(30x² + 30x) / (5x)"), parse("6x + 6"))

    def test_functions(self):
        name, var, body = parse_function_def("f(x) = 11x + 15")
        self.assertEqual(evaluate("f(3)", {name: (var, body)}), 48)
        table = {"g": ("x", parse("3x − 4"))}
        table["f"] = ("x", parse("4x + 1", table))
        self.assertEqual(evaluate("f(g(−2))", table), -39)

    def test_solve(self):
        self.assertEqual(solve_univariate(parse_equation("3x + 26 = 50")), [8])
        self.assertEqual(solve_univariate(parse_equation("(x − 7)(x + 6) = 0")), [-6, 7])
        self.assertEqual(solve_univariate(parse_equation("x² + 1 = 0")), [])
        sol = solve_linear_system([parse_equation("x + 5y = 45"), parse_equation("4x − y = 12")])
        self.assertEqual(sol, {"x": 5, "y": 8})
        self.assertIsNone(solve_linear_system([parse_equation("x + y = 1"),
                                               parse_equation("2x + 2y = 3")]))

    def test_holds(self):
        self.assertTrue(holds("|x − 8| < 5", {"x": 4}))
        self.assertFalse(holds("3 < x < 13", {"x": 13}))
        self.assertTrue(holds("x < 3 or x > 13", {"x": 20}))
        self.assertTrue(holds("y < x − 4", {"x": -1, "y": -6}))

    def test_poly_const(self):
        self.assertEqual(Poly.const(3).value(), 3)
        with self.assertRaises(ExprError):
            Poly.var("x").value()


class ParseNumberTest(unittest.TestCase):
    def test_choice_values(self):
        cases = {"$4,080": 4080, "−7": -7, "9/2": Fraction(9, 2), "0.80": Fraction(4, 5),
                 "4%": Fraction(1, 25), "72°": 72, "$61.88": Fraction(6188, 100)}
        for text, want in cases.items():
            with self.subTest(text=text):
                self.assertEqual(parse_number(text), want)

    def test_non_values(self):
        for text in ("x = 8", "6, 8, 10", "100–119", "3 < x < 13", "North", "y = 2x + 1"):
            with self.subTest(text=text):
                self.assertIsNone(parse_number(text))


if __name__ == "__main__":
    unittest.main()
