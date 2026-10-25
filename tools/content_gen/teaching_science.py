"""Teaching cards for the ACT Science skills (same shape as teaching.TEACHING,
with the multi-screen mini-lesson already attached under ``screens``)."""

TEACHING_SCIENCE = {
    "data_representation": {
        "title": "Reading Tables and Graphs Fast",
        "body": ("ACT Science data questions are open-book: every answer is sitting in the "
                 "table or graph. Your job is to find the right cell quickly. Read the "
                 "question first, find the variable it names in the headers, locate the row "
                 "or point it asks about, and only then read the number. Watch the units and "
                 "the column labels; most wrong answers come from the right row in the wrong "
                 "column, or the right column one row off."),
        "key_points": [
            "Question first, then the table: know what you are hunting for.",
            "Match the exact variable name and unit in the header before reading a value.",
            "Put a finger on the row and a finger on the column; read where they meet.",
            "For 'greatest' or 'least', scan one column top to bottom and mark the extreme.",
            "A difference or ratio needs two reads; write both numbers down before combining.",
            "Converting units? Multiply by the factor and check the size makes sense (1.2 km is 1200 m, not 12).",
            "'Which graph matches the table?' Look at the row-to-row changes: equal steps mean a straight line.",
        ],
        "worked_example": ("Table: 20 cm → 0.90 s, 40 cm → 1.27 s, 60 cm → 1.55 s. 'What was the "
                           "period at 40 cm?' Row 40 cm, column Period: 1.27 s. Not 1.55 s (that is "
                           "the next row)."),
        "screens": [
            {"title": "The data is the answer key",
             "body": ("Science passages look intimidating, but data questions do not test "
                      "memory. Each one points at a specific place in a table or figure. Skim "
                      "the setup for what was varied and what was measured, then go straight "
                      "to the questions and let them tell you where to look."),
             "key_points": ["Skim the setup: what changed, what was measured, in what units.",
                            "Do not study the whole table; let each question direct you."]},
            {"title": "Row, column, read",
             "body": ("Find the question's variable in the headers. If two columns share a name "
                      "(two trials, two conditions), check the label after the comma. Slide "
                      "down to the row for the value in the question and read across. Common "
                      "traps: the adjacent row, the other condition's column, and the value "
                      "of the independent variable instead of the measured one."),
             "key_points": ["Header first, then row, then the cell.",
                            "Adjacent rows and sibling columns are the usual wrong answers."]},
            {"title": "Direction and extremes",
             "body": ("'As x increased, y...' means compare each value with the one above it. "
                      "If every step goes up, it increased only; if it rises then falls, say "
                      "so. For 'greatest' or 'least', run a finger down one column and note "
                      "the row where the extreme sits, then report that row's x value."),
             "worked_example": ("Period column: 0.90, 1.27, 1.55, 1.79 → every step rises, so "
                                "'increased only.' Greatest period is 1.79 s, at 80 cm.")},
            {"title": "Two numbers, one answer",
             "body": ("Differences, ratios, and percent changes combine two cells. Write both "
                      "values before doing arithmetic, keep track of which is first, and "
                      "estimate before choosing: if 169 ÷ 64 is asked, the answer is a bit "
                      "under 3, so 2.6 is plausible and 0.4 (the inverted ratio) is not."),
             "key_points": ["Write both values down; then subtract or divide.",
                            "Percent change = (new − old) ÷ old × 100.",
                            "Sanity-check the size of the answer before you commit."]},
        ],
    },
    "trends_extrapolation": {
        "title": "Trends, Interpolation and Extrapolation",
        "body": ("Many questions ask what the data would show between two rows or beyond the "
                 "last one. The method is always the same: find the direction of the trend, "
                 "find the two rows that bracket the value you need, and assume the change "
                 "continues smoothly. Between rows, the answer sits between the two listed "
                 "values. Beyond the table, continue the last step at the same rate unless "
                 "the data are clearly leveling off or speeding up."),
        "key_points": [
            "Describe the trend from the row-to-row changes, not from one glance.",
            "Interpolation: the answer lies between the values of the bracketing rows.",
            "Extrapolation: continue the pattern of the last rows in the same direction.",
            "Steady, slowing, or accelerating? Compare the sizes of successive changes.",
            "If x doubles, divide the two y values to see what happened to y.",
            "A rate of change is Δy ÷ Δx; to compare two series over the same interval, compare their Δy values.",
            "Two series heading toward each other cross when the faster one catches up; continue both at their last rates.",
        ],
        "worked_example": ("Stretch: 100 g → 4.0 cm, 200 g → 8.0 cm, 300 g → 12.0 cm. At 250 g "
                           "the stretch is between 8.0 and 12.0, about 10.0 cm. At 400 g, continuing "
                           "the +4.0 per 100 g step gives 16.0 cm."),
        "screens": [
            {"title": "Name the trend precisely",
             "body": ("Subtract each value from the next. All positive means increasing; all "
                      "negative means decreasing. Then look at the sizes of those changes: about "
                      "equal means a steady (linear) trend, shrinking means the curve is "
                      "leveling off, growing means it is accelerating. Those distinctions are "
                      "exactly what the answer choices test."),
             "key_points": ["Direction comes from the sign of each change.",
                            "Pace comes from whether the changes shrink, grow, or stay the same."]},
            {"title": "Reading between the rows",
             "body": ("To predict a value for an x that was not tested, find the two tested "
                      "x values on either side of it. The prediction must fall between their "
                      "y values. Halfway between the x values means roughly halfway between "
                      "the y values; a quarter of the way means closer to the nearer row."),
             "worked_example": ("40 cm → 1.27 s and 60 cm → 1.55 s. At 50 cm: about halfway, "
                                "so ≈ 1.41 s. 'Between 1.27 and 1.55' is the safe answer form.")},
            {"title": "Reading beyond the table",
             "body": ("To predict past the last row, use the change between the last two rows "
                      "and add it again for each additional step. If asked when a target will "
                      "be reached, count how many of those steps are needed. For a decreasing "
                      "trend, the next value is lower than the last, never back up among "
                      "earlier values."),
             "key_points": ["Next value = last value + last change (per step).",
                            "Steps needed = (target − last) ÷ change per step."]},
            {"title": "Doubling and crossing",
             "body": ("If the question says x doubled, divide the y at 2x by the y at x. A "
                      "ratio near 2 means y doubled; near 4, quadrupled; near 0.25, fell to a "
                      "quarter; between 1 and 2, increased but less than doubled. For two "
                      "series, compare them row by row to find where one first passes the "
                      "other or where they are closest."),
             "key_points": ["Ratio y(2x) ÷ y(x) tells the story in one division.",
                            "Crossing: compare the two columns row by row."]},
        ],
    },
    "experimental_design": {
        "title": "Research Summaries: Variables and Design",
        "body": ("Research-summary passages describe one or more experiments and then ask you "
                 "to reason about how they were built. Sort every quantity into three bins: "
                 "the independent variable (deliberately changed), the dependent variable "
                 "(measured as the result), and the controlled variables (kept the same). "
                 "When two experiments are compared, find the single thing that differed "
                 "between them; that difference is the point of the comparison."),
        "key_points": [
            "Independent = what the experimenters changed on purpose.",
            "Dependent = what they measured in response.",
            "Controlled = everything deliberately kept the same.",
            "A zero or untreated trial is a control for comparison.",
            "Experiments 1 and 2 usually differ in exactly one condition; find it.",
            "To test a new factor, vary only that factor and hold the old one fixed.",
            "A flaw is anything that changed besides the independent variable; reliability comes from more repeats, not fewer rows.",
            "A conclusion about values never tested, or about a variable held constant, is not supported by the data.",
        ],
        "worked_example": ("Students varied string length and timed the period, keeping bob "
                           "mass and release angle the same. Independent: length. Dependent: "
                           "period. Controlled: mass, angle. Experiment 2 repeated it in water: "
                           "the only change is the medium."),
        "screens": [
            {"title": "Three bins for every variable",
             "body": ("As you read the procedure, label each quantity: changed on purpose "
                      "(independent), measured (dependent), or held the same (controlled). "
                      "The table's first column is almost always the independent variable "
                      "and the other columns are the dependent variable. Anything the text "
                      "says was 'the same' or 'identical' is a controlled variable."),
             "key_points": ["First table column = independent; other columns = dependent.",
                            "'Same,' 'identical,' 'kept at' signal controlled variables."]},
            {"title": "Why a step was done",
             "body": ("Questions about purpose have standard answers. A trial with zero "
                      "treatment is a control that shows the baseline. Repeating and "
                      "averaging reduces random error. Holding a factor constant prevents it "
                      "from confusing the result. Choose the answer that names the specific "
                      "scientific purpose, not one that restates the procedure."),
             "key_points": ["Zero trial = control = baseline for comparison.",
                            "Repeat and average = less random error."]},
            {"title": "Comparing experiments",
             "body": ("When Experiment 2 repeats Experiment 1 with one condition changed, "
                      "compare the two sets of results row by row. If the measured values "
                      "differ in the same direction at every row, the changed condition "
                      "matters. If they match, it does not. A trend that appears in both "
                      "experiments says nothing about the changed condition."),
             "worked_example": ("Period in water is higher than in air at every length → the "
                                "medium affects period. Period rising with length in both "
                                "experiments is about length, not the medium.")},
            {"title": "Designing the next experiment",
             "body": ("To test whether some factor affects the result, vary that factor and "
                      "keep everything else, including the original independent variable, "
                      "fixed. Changing two things at once makes the result impossible to "
                      "interpret. To predict a new trial, place it between the tested "
                      "conditions that bracket it and expect a result between theirs."),
             "key_points": ["One new variable at a time.",
                            "A setting between two tested ones gives a result between theirs."]},
        ],
    },
    "conflicting_viewpoints": {
        "title": "Attacking Conflicting Viewpoints",
        "body": ("Conflicting-viewpoints passages give two scientists who explain the same "
                 "observation differently. Before the questions, write a one-line summary of "
                 "each view: the cause each proposes and the key evidence each cites. Most "
                 "questions then ask what one scientist would agree with, what both accept, "
                 "which finding would help one side, or how a new observation changes the "
                 "balance. Stay inside the passage; your own science knowledge is not the "
                 "answer."),
        "key_points": [
            "Summarize each viewpoint in one line: cause + main evidence.",
            "Agreement questions: the answer restates that scientist's own claim.",
            "Common ground is the shared observation, not either explanation.",
            "Supporting evidence confirms the mechanism that scientist proposed.",
            "A new observation weakens the view whose prediction it contradicts.",
            "A shared assumption is something every scientist takes for granted without arguing for it.",
            "With three scientists, sort each piece of evidence by which view it fits before reading the choices.",
        ],
        "worked_example": ("Scientist 1: impact caused the extinction (iridium layer, crater). "
                           "Scientist 2: volcanoes did (long eruptions, earlier declines). Both "
                           "accept the iridium layer. Finding most lava erupted after the layer "
                           "formed weakens Scientist 2."),
        "screens": [
            {"title": "Map the two views first",
             "body": ("Read each viewpoint once and jot the proposed cause, the two or three "
                      "pieces of evidence, and any point where the scientist concedes "
                      "something to the other side. Those concessions are where 'both would "
                      "agree' answers hide, and the evidence lists are where 'which finding "
                      "supports' answers come from."),
             "key_points": ["Cause, evidence, concessions: three notes per scientist.",
                            "Note what each scientist explicitly denies."]},
            {"title": "Would agree / would disagree",
             "body": ("For 'Scientist 2 would most likely agree that...', the correct choice "
                      "is a restatement of something Scientist 2 actually said or clearly "
                      "implied. Wrong choices usually belong to the other scientist or "
                      "contradict a detail in the passage. Check each choice against the "
                      "text rather than against what sounds scientifically reasonable."),
             "worked_example": ("Scientist 2 says zander arrived eight years ago. 'Zander were "
                                "present for decades' contradicts that, so Scientist 2 would "
                                "not agree with it.")},
            {"title": "Evidence and new findings",
             "body": ("A finding supports a view when it confirms that view's mechanism or "
                      "prediction. A finding weakens a view when it contradicts something the "
                      "view requires. Ask: what does each scientist predict should be true? "
                      "Then see which prediction the new observation matches. A finding "
                      "consistent with both views does not favor either."),
             "key_points": ["Support = matches that view's prediction.",
                            "Weaken = contradicts something that view needs to be true.",
                            "Consistent with both = favors neither."]},
            {"title": "The main difference",
             "body": ("When asked what the views differ on, rule out anything both accept: "
                      "the observation being explained, shared facts, and background "
                      "science. What remains is the disputed cause or mechanism. The correct "
                      "choice names that dispute; the others are points of agreement dressed "
                      "up as disagreements."),
             "key_points": ["Cross out shared facts; the dispute is what is left.",
                            "The difference is usually 'which cause,' not 'whether it happened.'"]},
        ],
    },
}
