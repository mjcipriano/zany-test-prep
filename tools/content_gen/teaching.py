"""Teaching cards (short concept explanations) keyed by skill id."""

TEACHING = {
    # ---- Math ----
    "linear_equations": {
        "title": "Solving Linear Equations",
        "body": ("A linear equation keeps the variable to the first power. To solve, "
                 "undo what was done to the variable using inverse operations, keeping "
                 "both sides balanced: add/subtract to move constants, then multiply/"
                 "divide to isolate the variable."),
        "key_points": ["Do the same operation to both sides.",
                       "Move constants first, then divide by the coefficient.",
                       "Check by substituting your answer back in."],
        "worked_example": "3x + 5 = 20 → 3x = 15 → x = 5.",
    },
    "linear_inequalities": {
        "title": "Linear Inequalities",
        "body": ("Solve an inequality like an equation, but remember one rule: if you "
                 "multiply or divide both sides by a negative number, flip the "
                 "inequality sign. The solution is a range of values, not a single one."),
        "key_points": ["Isolate the variable as with equations.",
                       "Flip the sign when multiplying/dividing by a negative.",
                       "≤ and ≥ include the endpoint; < and > do not."],
        "worked_example": "2x + 3 ≤ 11 → 2x ≤ 8 → x ≤ 4.",
    },
    "systems_of_equations": {
        "title": "Systems of Equations",
        "body": ("A system gives two equations with two unknowns. Use substitution "
                 "(solve one equation for a variable and plug in) or elimination (add or "
                 "subtract the equations to cancel a variable). The solution makes both "
                 "equations true at once."),
        "key_points": ["Substitution: isolate one variable, then substitute.",
                       "Elimination: combine equations to cancel a variable.",
                       "A solution satisfies both equations simultaneously."],
        "worked_example": "x+y=7 and x−y=1 → add: 2x=8 → x=4, y=3.",
    },
    "functions": {
        "title": "Function Notation",
        "body": ("f(x) is a rule that turns an input x into an output. To evaluate f at "
                 "a number, substitute that number everywhere x appears and simplify. "
                 "Mind the order of operations, especially with squares and negatives."),
        "key_points": ["f(k) means substitute k for x.",
                       "Square before multiplying; handle negatives carefully.",
                       "The output depends only on the input you plug in."],
        "worked_example": "If f(x)=2x+1, then f(3)=2·3+1=7.",
    },
    "quadratics": {
        "title": "Quadratic Equations",
        "body": ("A quadratic has an x² term. Many factor into (x−r₁)(x−r₂)=0, whose "
                 "solutions (roots) are r₁ and r₂. The sum of the roots equals −b/a and "
                 "the product equals c/a, a useful shortcut on the test."),
        "key_points": ["Set each factor equal to zero to find the roots.",
                       "Sum of roots = −b/a; product of roots = c/a.",
                       "Check signs carefully when factoring."],
        "worked_example": "x²−5x+6=0 → (x−2)(x−3)=0 → x=2 or x=3.",
    },
    "exponents_radicals": {
        "title": "Exponents and Radicals",
        "body": ("Exponent rules let you combine powers. Multiplying powers with the "
                 "same base adds exponents; dividing subtracts them; a power of a power "
                 "multiplies them. A radical is a fractional exponent."),
        "key_points": ["aᵐ·aⁿ = aᵐ⁺ⁿ (add when multiplying).",
                       "aᵐ/aⁿ = aᵐ⁻ⁿ (subtract when dividing).",
                       "(aᵐ)ⁿ = aᵐⁿ (multiply for a power of a power)."],
        "worked_example": "2³·2⁴ = 2⁷ = 128.",
    },
    "polynomials": {
        "title": "Polynomial Expressions",
        "body": ("To multiply two binomials, use FOIL: First, Outer, Inner, Last, then "
                 "combine like terms. The coefficient of x comes from the Outer and Inner "
                 "products added together."),
        "key_points": ["FOIL: First, Outer, Inner, Last.",
                       "Combine like terms after multiplying.",
                       "The x² term comes from First; the constant from Last."],
        "worked_example": "(x+2)(x+3)=x²+5x+6.",
    },
    "ratios_percentages_units": {
        "title": "Percentages and Ratios",
        "body": ("A percent is a part out of 100. To find a percent of a number, "
                 "multiply by the percent over 100. Percent change is the difference "
                 "divided by the original amount, times 100."),
        "key_points": ["x% of n = (x/100)·n.",
                       "Percent change = (new − old)/old × 100.",
                       "Always divide by the original value for percent change."],
        "worked_example": "20% of 50 = 0.20·50 = 10.",
    },
    "proportions": {
        "title": "Proportions and Rates",
        "body": ("A proportion sets two ratios equal. Cross-multiply to solve for an "
                 "unknown. Rates compare two quantities with different units, like miles "
                 "per hour; scale them up or down proportionally."),
        "key_points": ["Set equal ratios: a/b = c/d.",
                       "Cross-multiply to solve: a·d = b·c.",
                       "Keep units consistent on each side."],
        "worked_example": "3/4 = x/12 → x = 9.",
    },
    "data_analysis": {
        "title": "Reading Data from Tables",
        "body": ("Tables and graphs pack information into rows and columns. Read the "
                 "headers first so you know what each value means, then locate exactly "
                 "the value(s) the question asks for before doing any arithmetic."),
        "key_points": ["Read titles and headers before the numbers.",
                       "Match the question to the right row/column.",
                       "Totals, maxima, and differences are common asks."],
        "worked_example": "To find a total, add the relevant column's entries.",
    },
    "statistics": {
        "title": "Mean, Median, and Range",
        "body": ("The mean is the sum divided by the count. The median is the middle "
                 "value when data are in order. The range is the largest value minus the "
                 "smallest. Each summarizes a data set differently."),
        "key_points": ["Mean = sum ÷ count.",
                       "Median = middle value (order the data first).",
                       "Range = max − min."],
        "worked_example": "For 2,4,9: mean=5, median=4, range=7.",
    },
    "probability": {
        "title": "Basic Probability",
        "body": ("Probability measures how likely an event is, from 0 (impossible) to 1 "
                 "(certain). For equally likely outcomes, it is the number of favorable "
                 "outcomes divided by the total number of outcomes."),
        "key_points": ["P(event) = favorable ÷ total.",
                       "Use the total count in the denominator.",
                       "P(not event) = 1 − P(event)."],
        "worked_example": "2 red of 5 marbles → P(red) = 2/5.",
    },
    "area_volume": {
        "title": "Area and Volume",
        "body": ("Area measures a flat region; volume measures space inside a solid. "
                 "Rectangle area = base × height; triangle area = ½ × base × height; "
                 "box volume = length × width × height."),
        "key_points": ["Rectangle area = b·h.",
                       "Triangle area = ½·b·h.",
                       "Box volume = l·w·h."],
        "worked_example": "A 4×5 rectangle has area 20.",
    },
    "circles": {
        "title": "Circles",
        "body": ("For a circle of radius r: the circumference (distance around) is 2πr, "
                 "and the area is πr². The diameter is twice the radius. Answers are "
                 "often left 'in terms of π.'"),
        "key_points": ["Circumference = 2πr.",
                       "Area = πr².",
                       "Diameter = 2r."],
        "worked_example": "Radius 3: area = 9π, circumference = 6π.",
    },
    "right_triangles": {
        "title": "Right Triangles",
        "body": ("In a right triangle, the Pythagorean theorem links the legs a and b to "
                 "the hypotenuse c: a² + b² = c². Recognizing common triples like "
                 "3-4-5 saves time."),
        "key_points": ["a² + b² = c² (c is the hypotenuse).",
                       "The hypotenuse is the longest side.",
                       "Memorize 3-4-5, 5-12-13, 8-15-17."],
        "worked_example": "Legs 3 and 4 → hypotenuse 5.",
    },
    "trigonometry": {
        "title": "Right-Triangle Trigonometry",
        "body": ("SOH-CAH-TOA relates an acute angle to side ratios: sine = opposite/"
                 "hypotenuse, cosine = adjacent/hypotenuse, tangent = opposite/adjacent. "
                 "Identify the sides relative to the angle first."),
        "key_points": ["sin = opposite/hypotenuse.",
                       "cos = adjacent/hypotenuse.",
                       "tan = opposite/adjacent."],
        "worked_example": "In a 3-4-5 triangle, sin θ = 3/5 if 3 is opposite θ.",
    },
    # ---- Reading & Writing ----
    "main_idea": {
        "title": "Finding the Main Idea",
        "body": ("The main idea is the single point a passage is built to make. Look for "
                 "what every sentence supports, not a small detail. A good summary "
                 "captures the whole passage without adding outside claims."),
        "key_points": ["Ask: what is the passage mostly about?",
                       "Avoid choices that are true but too narrow.",
                       "Reject choices that go beyond the passage."],
        "screens": [
            {
                "title": "What is a main idea?",
                "body": ("The main idea is the one point the whole passage is built to "
                         "make — the umbrella that every sentence sits under. It is not "
                         "the topic (a word or two) and not any single detail; it is the "
                         "claim the details add up to."),
                "key_points": ["Topic = what it's about; main idea = the point made about it.",
                               "Every sentence should support the main idea."],
            },
            {
                "title": "How to find it",
                "body": ("Read for the point, not the trivia. In your own words, sum up "
                         "what each part is doing, then ask: what do they all add up to? "
                         "The first or last sentence often states or hints at it."),
                "key_points": ["Summarize the passage in one short sentence first.",
                               "Then match that summary to the closest choice.",
                               "A turn like 'but' or 'however' often signals the point."],
            },
            {
                "title": "Dodge the traps",
                "body": ("Wrong answers are usually true-but-too-narrow (one detail), "
                         "too-broad or outside the passage (adds claims it never makes), "
                         "or a distortion that flips or exaggerates the text. The best "
                         "answer covers the whole passage and nothing more."),
                "key_points": ["Too narrow: a real detail, but not the overall point.",
                               "Too broad / outside: ideas the passage never states.",
                               "Distortion: close, but changes or overstates the meaning."],
            },
            {
                "title": "Try the moves",
                "body": ("A passage explains that an octopus changes color with muscles "
                         "that widen pigment sacs — yet it is colorblind and cannot see "
                         "its own colors. One-sentence summary: it changes color by a "
                         "mechanism it can't perceive. The choice matching that whole idea "
                         "wins; 'octopuses talk with color' (never stated) and 'it changes "
                         "color slowly' (it's under a second) are traps."),
                "worked_example": ("Summarize first -> 'changes color it can't see,' then "
                                   "pick the choice that says exactly that, not one detail."),
            },
        ],
    },
    "inferences": {
        "title": "Making Inferences",
        "body": ("An inference is a conclusion the passage supports but does not state "
                 "outright. Stay close to the text: the best answer is the one the "
                 "evidence forces, not the one that merely sounds reasonable."),
        "key_points": ["Base inferences on stated evidence.",
                       "Avoid going further than the text allows.",
                       "Eliminate choices the passage contradicts."],
    },
    "command_of_evidence": {
        "title": "Command of Evidence",
        "body": ("These questions ask which detail best supports a claim. Find the "
                 "specific sentence or data point that directly backs the claim — not one "
                 "that is merely related to the topic."),
        "key_points": ["Match the evidence to the exact claim.",
                       "Specific, on-point details beat general ones.",
                       "Beware details that are true but off-topic."],
    },
    "text_structure_purpose": {
        "title": "Text Structure and Purpose",
        "body": ("Every passage is built a certain way — by contrast, cause and effect, "
                 "problem and solution, and so on — to serve a purpose. Ask why the "
                 "author included a part and how the whole is organized."),
        "key_points": ["Identify the organizing pattern.",
                       "Ask what a sentence accomplishes in context.",
                       "Match purpose to the passage's overall aim."],
    },
    "words_in_context": {
        "title": "Words in Context",
        "body": ("A word's meaning on the test depends on its sentence. Predict a "
                 "substitute that fits the context, then pick the choice closest to your "
                 "prediction. Common words often carry less common meanings here."),
        "key_points": ["Read the whole sentence, not just the word.",
                       "Predict a meaning before reading choices.",
                       "Watch for secondary meanings of familiar words."],
    },
    "cross_text_connections": {
        "title": "Cross-Text Connections",
        "body": ("Paired passages present two views on one topic. Pin down each author's "
                 "claim, then judge how they relate: agreement, disagreement, or one "
                 "qualifying the other. Predict how one author would answer the other."),
        "key_points": ["Summarize each text's main claim first.",
                       "Determine the relationship between the claims.",
                       "Anticipate how one author would respond to the other."],
    },
    "sentence_boundaries": {
        "title": "Sentence Boundaries",
        "body": ("An independent clause can stand alone as a sentence. Two independent "
                 "clauses cannot be joined by a comma alone (a comma splice) or by "
                 "nothing (a run-on). Use a period, a semicolon, or a comma plus a "
                 "coordinating conjunction."),
        "key_points": ["A comma alone can't join two independent clauses.",
                       "Use a period or semicolon between independent clauses.",
                       "A comma + FANBOYS conjunction also works."],
    },
    "subject_verb_agreement": {
        "title": "Subject-Verb Agreement",
        "body": ("A verb must match its subject in number. Ignore words between the "
                 "subject and verb — especially prepositional phrases — which often hide "
                 "the true subject and bait you into the wrong number."),
        "key_points": ["Find the true subject, ignoring in-between phrases.",
                       "Singular subject → singular verb; plural → plural.",
                       "Watch indefinite pronouns like 'each' (singular)."],
    },
    "punctuation": {
        "title": "Punctuation and Possessives",
        "body": ("Possession is shown with an apostrophe: add 's to a singular noun, and "
                 "just an apostrophe after a plural noun ending in -s. A plain -s makes a "
                 "plural, not a possessive."),
        "key_points": ["Singular possessive: add 's.",
                       "Plural ending in -s: add only an apostrophe.",
                       "No apostrophe makes a noun plural, not possessive."],
    },
    "pronouns": {
        "title": "Pronoun Case",
        "body": ("Choose pronoun case by the pronoun's job. Subjects take I, he, she, "
                 "they, who; objects take me, him, her, them, whom. In compounds, test "
                 "the pronoun alone to hear the right case."),
        "key_points": ["Subjective case for subjects (I, who).",
                       "Objective case for objects (me, whom).",
                       "In compounds, drop the other name to check."],
    },
    "modifiers": {
        "title": "Modifier Placement",
        "body": ("An introductory phrase must modify the noun that immediately follows "
                 "it. If it doesn't, the modifier 'dangles' and the sentence says "
                 "something illogical. Place the right noun right after the phrase."),
        "key_points": ["Put the modified noun right after the phrase.",
                       "Check that the opening phrase logically fits that noun.",
                       "Dangling modifiers create unintended meanings."],
    },
    "transitions": {
        "title": "Transitions",
        "body": ("Transitions signal the logical link between ideas: contrast (however), "
                 "cause and effect (therefore), addition (moreover), example (for "
                 "instance). Decide the relationship first, then choose the matching "
                 "transition."),
        "key_points": ["Identify the relationship between the two ideas.",
                       "However/yet = contrast; therefore = result.",
                       "Moreover = addition; for example = illustration."],
    },
    "concision": {
        "title": "Concision",
        "body": ("Good writing says it once. Eliminate redundancy (repeating the same "
                 "idea in different words) and wordy filler. The best choice is usually "
                 "the shortest one that keeps the full meaning and stays grammatical."),
        "key_points": ["Cut words that repeat an idea.",
                       "Prefer the shortest clear, grammatical option.",
                       "Don't delete meaning — only redundancy."],
    },
    "verb_tense": {
        "title": "Verb Tense and Form",
        "body": ("Match the verb to the time the sentence describes. Clues like "
                 "'last year' signal past, 'every day' or 'currently' signal present, "
                 "and 'next year' or 'will' signal future. Keep tenses consistent."),
        "key_points": ["Let time markers set the tense.",
                       "Past: -ed; present: base/-s; future: will + base.",
                       "An -ing form alone can't be the main verb."],
        "worked_example": "Last year, the team traveled (not travels) abroad.",
    },
    "parallel_structure": {
        "title": "Parallel Structure",
        "body": ("Items joined in a list or by 'and'/'or' should share the same "
                 "grammatical form. If two items are -ing forms, the third must be too."),
        "key_points": ["Match the form of items in a series.",
                       "-ing with -ing; nouns with nouns; to-verb with to-verb.",
                       "Mismatched forms break parallelism."],
        "worked_example": "She likes hiking, biking, and swimming (not 'to swim').",
    },
    "pronoun_antecedent": {
        "title": "Pronoun-Antecedent Agreement",
        "body": ("A pronoun must agree in number with the noun it refers to (its "
                 "antecedent). A singular antecedent takes a singular pronoun; a "
                 "plural antecedent takes a plural one."),
        "key_points": ["Singular antecedent -> its, his, her.",
                       "Plural antecedent -> their.",
                       "'it's' = 'it is'; 'they're' = 'they are' (not possessive)."],
        "worked_example": "The company released its (not their) report.",
    },
    "quantitative_evidence": {
        "title": "Quantitative Command of Evidence",
        "body": ("Some questions give a claim and a small table or graph. Pick the "
                 "choice whose data accurately supports the claim — read the actual "
                 "values and trend, and avoid options that misread the table."),
        "key_points": ["Read the headers and units first.",
                       "Match the data to the exact claim.",
                       "Reject choices that distort or invent values."],
    },
    "word_problems": {
        "title": "Linear Word Problems",
        "body": ("Translate the words into an equation. A 'flat fee plus a rate' is "
                 "total = fee + rate × amount. Subtract the fixed part, then divide by "
                 "the rate to find the unknown."),
        "key_points": ["Identify the fixed amount and the per-unit rate.",
                       "total = fixed + rate × quantity.",
                       "Undo the fixed part first, then divide."],
        "worked_example": "$20 + $15·h = $80 -> 15h = 60 -> h = 4.",
    },
    "absolute_value": {
        "title": "Absolute-Value Equations",
        "body": ("|expression| = c means the expression equals c OR −c, giving two "
                 "solutions. Solve both linear cases. The two solutions are symmetric "
                 "around the value that makes the inside zero."),
        "key_points": ["Split into two cases: = c and = −c.",
                       "|x − a| = c -> x = a + c or x = a − c.",
                       "The two solutions sum to 2a."],
        "worked_example": "|x − 5| = 3 -> x = 8 or x = 2.",
    },
    "exponential": {
        "title": "Exponential Growth",
        "body": ("In exponential growth a quantity is multiplied by the same factor "
                 "each period: value = start × factor^periods. This grows far faster "
                 "than adding the same amount each time (linear growth)."),
        "key_points": ["Multiply, don't add, each period.",
                       "value = start × factor^time.",
                       "Doubling = ×2 each period."],
        "worked_example": "5 cells doubling for 3 hours: 5×2³ = 40.",
    },
    "two_way_tables": {
        "title": "Two-Way Tables",
        "body": ("A two-way table sorts data by two categories. Probabilities come "
                 "from the right total: use a row or column total for that group, and "
                 "the grand total for the whole sample."),
        "key_points": ["Find the correct row/column total.",
                       "Probability = favorable ÷ appropriate total.",
                       "Use the grand total for a whole-sample probability."],
    },
    "scatterplots": {
        "title": "Scatterplots & Line of Best Fit",
        "body": ("A line of best fit, y = mx + b, models a scatterplot. The slope m is "
                 "the predicted change in y for each 1-unit increase in x; b is the "
                 "predicted y when x = 0. Plug in x to predict y."),
        "key_points": ["Slope m = change in y per unit x.",
                       "Intercept b = predicted y at x = 0.",
                       "Predict by substituting x into y = mx + b."],
        "worked_example": "y = 3x + 4 at x = 5: y = 19.",
    },
    "rhetorical_synthesis": {
        "title": "Rhetorical Synthesis",
        "body": ("You're given notes and a specific goal (introduce, emphasize, compare). "
                 "Pick the sentence that uses the relevant notes to accomplish that exact "
                 "goal — not just any accurate sentence."),
        "key_points": ["Read the goal carefully before the choices.",
                       "Choose the option that serves that goal.",
                       "Accurate but off-goal choices are traps."],
    },
}
