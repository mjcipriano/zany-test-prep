"""Teaching cards for the ACT-only math skills (see math_act.py).

Each entry follows the lesson-schema ``teaching_card`` shape used by
``teaching.py``: title, body (≥ 30 chars), key_points (≥ 2), worked_example, and
2–4 ``screens`` (each with title, body ≥ 20 chars, optional key_points /
worked_example). The orchestrator appends the difficulty label to the title.
"""

TEACHING_ACT = {
    "number_properties": {
        "title": "Number Properties",
        "body": ("Factors divide a number evenly; multiples are what you get by multiplying it. "
                 "Primes have exactly two factors. The order of operations (parentheses, "
                 "exponents, multiply/divide, add/subtract) and the rules for even/odd and "
                 "remainders let you reason about integers without a calculator."),
        "key_points": ["GCF = product of shared prime factors; LCM = highest power of every prime.",
                       "PEMDAS: parentheses, exponents, multiply/divide, add/subtract.",
                       "Scientific notation: coefficient from 1 to 10, times a power of 10.",
                       "Fraction ↔ decimal ↔ percent: divide, then move the decimal two places."],
        "worked_example": "GCF(24, 36): 24 = 2³·3, 36 = 2²·3² → shared 2²·3 = 12. LCM = 2³·3² = 72.",
        "screens": [
            {"title": "Factors, multiples, and primes",
             "body": ("Prime-factor a number first: 60 = 2²·3·5. The greatest common factor of two "
                      "numbers takes the smaller power of each shared prime; the least common "
                      "multiple takes the larger power of every prime that appears. A number with "
                      "prime factorization p^a·q^b has (a + 1)(b + 1) factors."),
             "key_points": ["GCF: shared primes, smaller exponents.",
                            "LCM: all primes, larger exponents.",
                            "Count factors with (exponent + 1) products."]},
            {"title": "Integers and order of operations",
             "body": ("Even ± even = even, odd ± odd = even, even ± odd = odd; a product is odd only "
                      "when every factor is odd. Among any k consecutive integers one is a multiple "
                      "of k. Evaluate expressions with PEMDAS, and remember (−3)² = 9 while −3² = −9."),
             "key_points": ["Products are odd only if all factors are odd.",
                            "Consecutive integers always include a multiple of k.",
                            "Square the sign too when it is inside parentheses."]},
            {"title": "Scientific notation and conversions",
             "body": ("Write a number as c × 10ⁿ with 1 ≤ c < 10: moving the decimal left raises n, "
                      "moving it right lowers n. Multiply coefficients and add exponents; divide "
                      "coefficients and subtract exponents, then re-normalize. To convert a "
                      "fraction, divide; to get a percent, multiply the decimal by 100."),
             "key_points": ["Keep the coefficient between 1 and 10.",
                            "× adds exponents, ÷ subtracts them.",
                            "3/8 = 0.375 = 37.5%."]},
            {"title": "Try the moves",
             "body": ("(3 × 10⁴)(4 × 10⁵) = 12 × 10⁹ = 1.2 × 10¹⁰. The remainder of 7n ÷ 5 when n "
                      "leaves remainder 3: 7·3 = 21 → remainder 1. And 2 + 3 × 4² = 2 + 48 = 50."),
             "worked_example": "LCM of 6 and 8 = 24; 5/8 = 0.625 = 62.5%."},
        ],
    },
    "coordinate_geometry": {
        "title": "Coordinate Geometry",
        "body": ("Points in the (x, y) plane are connected by three formulas: the distance "
                 "formula (a hidden Pythagorean theorem), the midpoint formula (average the "
                 "coordinates), and the slope. A circle with center (h, k) and radius r is "
                 "(x − h)² + (y − k)² = r²."),
        "key_points": ["Distance = √((x₂ − x₁)² + (y₂ − y₁)²).",
                       "Midpoint = ((x₁ + x₂)/2, (y₁ + y₂)/2).",
                       "Parallel lines share a slope; perpendicular slopes are negative reciprocals.",
                       "Circle: (x − h)² + (y − k)² = r², center (h, k)."],
        "worked_example": "From (1, 2) to (4, 6): √(3² + 4²) = 5; midpoint (2.5, 4).",
        "screens": [
            {"title": "Distance and midpoint",
             "body": ("Draw the right triangle between two points: the legs are the differences in "
                      "x and y, and the distance is the hypotenuse. The midpoint is simply the "
                      "average of the x's and the average of the y's. If a midpoint and one "
                      "endpoint are known, double the midpoint and subtract the endpoint."),
             "key_points": ["Distance: square the differences, add, take the root.",
                            "Midpoint: add and halve each coordinate.",
                            "Missing endpoint: B = 2M − A."]},
            {"title": "Lines: parallel and perpendicular",
             "body": ("Rewrite Ax + By = C as y = (−A/B)x + C/B to read the slope. A parallel "
                      "line keeps that slope; a perpendicular line uses the negative reciprocal "
                      "(flip the fraction and change the sign). Then use the given point to find "
                      "the intercept with y = mx + b."),
             "key_points": ["Slope of Ax + By = C is −A/B.",
                            "Perpendicular to 2/3 is −3/2.",
                            "A point is on a line if it satisfies the equation."]},
            {"title": "Circles in the plane",
             "body": ("In (x − h)² + (y − k)² = r², the signs inside the parentheses are opposite "
                      "to the center's coordinates, and the right side is r², not r. For an "
                      "expanded equation x² + y² + Dx + Ey + F = 0, complete the square: the center "
                      "is (−D/2, −E/2)."),
             "key_points": ["(x + 3)² means h = −3.",
                            "Radius = √(right side).",
                            "Complete the square to recover the center."]},
            {"title": "Try the moves",
             "body": ("Line through (2, 1) perpendicular to y = 2x + 5: slope −1/2, so 1 = −1/2·2 + b "
                      "gives b = 2 and y = −x/2 + 2. Circle x² + y² − 4x + 6y − 3 = 0: "
                      "(x − 2)² + (y + 3)² = 16, center (2, −3), radius 4."),
             "worked_example": "Distance (−1, 3) to (2, −1): √(9 + 16) = 5."},
        ],
    },
    "angles_polygons": {
        "title": "Angles and Polygons",
        "body": ("Most angle questions reduce to a few facts: angles on a line sum to 180°, "
                 "around a point to 360°, in a triangle to 180°. Parallel lines cut by a "
                 "transversal create equal (corresponding, alternate) and supplementary "
                 "(same-side) pairs, and a polygon with n sides has interior angles summing to "
                 "180(n − 2)."),
        "key_points": ["Triangle angles sum to 180°; an exterior angle equals the two remote interior angles.",
                       "Parallel lines + transversal: corresponding and alternate angles are equal; same-side interior angles sum to 180°.",
                       "Polygon interior sum = 180(n − 2); exterior angles always sum to 360°.",
                       "Regular polygon: each interior angle = 180(n − 2)/n."],
        "worked_example": "Regular hexagon: 180·4/6 = 120° per interior angle; exterior 360/6 = 60°.",
        "screens": [
            {"title": "Angle pairs and parallel lines",
             "body": ("Complementary angles sum to 90°, supplementary to 180°, and vertical angles "
                      "(across an X) are equal. When a transversal crosses parallel lines, every "
                      "angle is either equal to a given angle or supplementary to it: decide which "
                      "by whether the two angles 'look the same' (both acute or both obtuse)."),
             "key_points": ["Vertical angles are equal.",
                            "Same-side interior angles are supplementary.",
                            "With parallels, every angle is x or 180 − x."]},
            {"title": "Triangles",
             "body": ("The three angles add to 180°. In an isosceles triangle the base angles are "
                      "equal, so the vertex angle is 180 − 2·(base angle). An exterior angle equals "
                      "the sum of the two non-adjacent interior angles. When angles are given as "
                      "expressions, add them, set the sum to 180, and solve for x — then answer the "
                      "question actually asked (often the angle, not x)."),
             "key_points": ["Isosceles: base angles equal.",
                            "Exterior angle = sum of remote interior angles.",
                            "Solve for x, then compute the angle."]},
            {"title": "Polygons",
             "body": ("Split a polygon into n − 2 triangles from one vertex: the interior angles sum "
                      "to 180(n − 2). The exterior angles of any polygon sum to 360°, so a regular "
                      "n-gon has exterior angles of 360/n and interior angles of 180 − 360/n. To "
                      "find n from an interior angle, use the exterior angle: n = 360/(180 − interior)."),
             "key_points": ["Interior sum: 180(n − 2).",
                            "Exterior sum: always 360°.",
                            "n = 360 ÷ exterior angle."]},
            {"title": "Try the moves",
             "body": ("Each interior angle of a regular polygon is 150°: exterior = 30°, so n = "
                      "360/30 = 12 sides. Angles (2x + 10)°, (3x)°, and 50° in a triangle: 5x + 60 "
                      "= 180 → x = 24, so the angles are 58°, 72°, 50°."),
             "worked_example": "Same-side interior angles 3x and 2x + 30: 5x + 30 = 180 → x = 30."},
        ],
    },
    "sequences": {
        "title": "Sequences and Series",
        "body": ("An arithmetic sequence adds the same difference d each step: a_n = a₁ + (n − 1)d. "
                 "A geometric sequence multiplies by the same ratio r: a_n = a₁·r^(n−1). A "
                 "recursive rule tells you how to get each term from the ones before it."),
        "key_points": ["Arithmetic: a_n = a₁ + (n − 1)d; sum of n terms = n(a₁ + a_n)/2.",
                       "Geometric: a_n = a₁·r^(n−1); find r by dividing consecutive terms.",
                       "Use n − 1 steps from the first term, not n.",
                       "Recursive rules: compute term by term from the starting values."],
        "worked_example": "5, 9, 13, …: d = 4, a₂₀ = 5 + 19·4 = 81; sum of 20 terms = 20(5 + 81)/2 = 860.",
        "screens": [
            {"title": "Arithmetic sequences",
             "body": ("Subtract consecutive terms to find d. The nth term is the first term plus "
                      "n − 1 jumps of d. Given two far-apart terms, divide their difference by the "
                      "number of steps between them to recover d, then work back to a₁. The sum of "
                      "the first n terms is n times the average of the first and last terms."),
             "key_points": ["d = (later term − earlier term) ÷ (steps between).",
                            "a_n = a₁ + (n − 1)d.",
                            "S_n = n(a₁ + a_n)/2."]},
            {"title": "Geometric sequences",
             "body": ("Divide a term by the previous one to find r (it may be a fraction or "
                      "negative). The nth term is a₁ times r raised to n − 1. The sum of the first n "
                      "terms is a₁(rⁿ − 1)/(r − 1). Two known terms give r from the ratio "
                      "r^(gap) = later ÷ earlier."),
             "key_points": ["r = a₂ ÷ a₁.",
                            "a_n = a₁·r^(n−1).",
                            "Finite sum: a₁(rⁿ − 1)/(r − 1)."]},
            {"title": "Recursive rules",
             "body": ("A recursive definition such as a₁ = 3, a_n = 2a_(n−1) + 1 tells you to build "
                      "each term from the previous one: 3, 7, 15, 31, …. Write the terms out in "
                      "order and stop at the index asked for. To identify a rule from a list, test "
                      "whether consecutive terms differ by a constant (add) or divide to a constant "
                      "(multiply)."),
             "key_points": ["Compute recursive terms one at a time.",
                            "Constant difference → add; constant ratio → multiply.",
                            "Check the rule against the first three terms."]},
            {"title": "Try the moves",
             "body": ("Geometric: 2, 6, 18, …: r = 3, a₆ = 2·3⁵ = 486. Arithmetic with a₄ = 11 and "
                      "a₁₀ = 29: d = (29 − 11)/6 = 3, a₁ = 11 − 3·3 = 2, a₁₅ = 2 + 14·3 = 44."),
             "worked_example": "Sum of first 5 terms of 1, 2, 4, 8, …: (2⁵ − 1)/(2 − 1) = 31."},
        ],
    },
    "logarithms": {
        "title": "Logarithms",
        "body": ("A logarithm is an exponent: log_b(x) answers 'b to what power gives x?' So "
                 "log_b(x) = y means exactly b^y = x. Switch between the two forms to solve, "
                 "and use the product, quotient, and power rules to combine or expand logs."),
        "key_points": ["log_b(x) = y ⇔ b^y = x.",
                       "log_b(1) = 0, log_b(b) = 1, and b^(log_b x) = x.",
                       "log(pq) = log p + log q; log(p/q) = log p − log q; log(p^k) = k·log p.",
                       "Solve b^x = c by rewriting both sides with the same base, or x = log c / log b."],
        "worked_example": "log₂(32) = 5 because 2⁵ = 32; log₄(8) = 3/2 because 4^(3/2) = 8.",
        "screens": [
            {"title": "A log is an exponent",
             "body": ("Read log₃(81) as 'what power of 3 is 81?' — the answer is 4. Negative "
                      "results come from fractions (log₂(1/8) = −3) and fractional results from "
                      "roots (log₉(3) = 1/2). The base 10 is written log x; the base e is ln x."),
             "key_points": ["Ask: base to what power equals the argument?",
                            "Fractions give negative logs; roots give fractional logs.",
                            "log₁₀ is written log; logₑ is ln."]},
            {"title": "Switching forms",
             "body": ("The exponential form b^y = x and the logarithmic form log_b(x) = y say the "
                      "same thing. The base of the power is the base of the log, the exponent is "
                      "the value of the log, and the result of the power is the argument. To solve "
                      "log_b(x + c) = k, rewrite as x + c = b^k."),
             "key_points": ["Base stays the base; exponent ↔ log value.",
                            "log_b(expression) = k ⇒ expression = b^k.",
                            "Check that arguments stay positive."]},
            {"title": "Log rules",
             "body": ("Because logs are exponents, multiplying arguments adds logs, dividing "
                      "subtracts them, and a power inside becomes a multiplier outside: "
                      "log(x³/y) = 3·log x − log y. Running the rules backward condenses a sum of "
                      "logs into a single log, which is how you solve log equations."),
             "key_points": ["Product → sum, quotient → difference, power → coefficient.",
                            "Condense before solving: log_b(A) = log_b(B) ⇒ A = B.",
                            "log 6 = log 2 + log 3 ≈ 0.30 + 0.48."]},
            {"title": "Try the moves",
             "body": ("Solve 8^x = 32: both are powers of 2, so 2^(3x) = 2⁵ and x = 5/3. Solve "
                      "log₅(2x − 1) = 2: 2x − 1 = 25, x = 13. Solve 3^x = 20: x = log 20 / log 3 ≈ 2.73."),
             "worked_example": "log₂(x) + log₂(4) = log₂(28) ⇒ 4x = 28 ⇒ x = 7."},
        ],
    },
    "complex_numbers": {
        "title": "Complex Numbers",
        "body": ("The imaginary unit i satisfies i² = −1, and a complex number has the form "
                 "a + bi. Add and subtract by combining like parts, multiply with FOIL and "
                 "replace i² by −1, and divide by multiplying top and bottom by the conjugate."),
        "key_points": ["Powers of i cycle: i, −1, −i, 1 — reduce the exponent mod 4.",
                       "(a + bi)(c + di) = (ac − bd) + (ad + bc)i.",
                       "Conjugate of a + bi is a − bi; (a + bi)(a − bi) = a² + b².",
                       "|a + bi| = √(a² + b²)."],
        "worked_example": "(2 + 3i)(1 − i) = 2 − 2i + 3i − 3i² = 2 + i + 3 = 5 + i.",
        "screens": [
            {"title": "Powers of i",
             "body": ("i¹ = i, i² = −1, i³ = −i, i⁴ = 1, and then the pattern repeats. To find "
                      "i^n, divide n by 4 and use the remainder: remainder 0 → 1, 1 → i, 2 → −1, "
                      "3 → −i. For √(−n), pull out i first: √(−12) = i√12 = 2i√3."),
             "key_points": ["Reduce the exponent modulo 4.",
                            "i^(4k) = 1 for any whole k.",
                            "√(−n) = i√n."]},
            {"title": "Add, subtract, multiply",
             "body": ("Treat i like a variable, then simplify with i² = −1. Adding combines real "
                      "parts and imaginary parts separately; subtracting distributes the minus "
                      "sign to both parts. Multiplying uses FOIL; the last term bi·di = bd·i² = −bd "
                      "joins the real part."),
             "key_points": ["(a + bi) − (c + di) = (a − c) + (b − d)i.",
                            "FOIL, then replace i² with −1.",
                            "(a + bi)² = a² − b² + 2abi."]},
            {"title": "Conjugates, modulus, division",
             "body": ("The conjugate flips the sign of the imaginary part only. Multiplying a "
                      "number by its conjugate gives the real number a² + b², which is also the "
                      "square of the modulus |a + bi| = √(a² + b²). To divide, multiply the "
                      "numerator and denominator by the denominator's conjugate so the bottom "
                      "becomes real."),
             "key_points": ["Conjugate of 3 − 4i is 3 + 4i; their product is 25.",
                            "|3 − 4i| = 5.",
                            "Divide by multiplying by conjugate/conjugate."]},
            {"title": "Try the moves",
             "body": ("i^23: 23 = 4·5 + 3, so i^23 = i³ = −i. (4 + 2i)/(1 − i): multiply by (1 + i)/(1 + i) "
                      "to get (4 + 4i + 2i + 2i²)/(1 + 1) = (2 + 6i)/2 = 1 + 3i."),
             "worked_example": "|5 + 12i| = √(25 + 144) = 13; conjugate of 5 + 12i is 5 − 12i."},
        ],
    },
}
