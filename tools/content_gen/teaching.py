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
        "screens": [
            {
                "title": "What is an inference?",
                "body": ("An inference is a conclusion the passage points to but never "
                         "says outright. It is not a wild guess and not your own outside "
                         "knowledge — it's what the evidence in the text makes almost "
                         "certain. If the passage doesn't support it, it's wrong, even if "
                         "it's true in real life."),
                "key_points": ["Supported by the text, but not stated word for word.",
                               "Use only what the passage gives you — not outside facts."],
            },
            {
                "title": "How to do it",
                "body": ("Find the sentence(s) that bear on the question and ask, 'Given "
                         "this, what must be true?' Predict an answer in your own words "
                         "before reading the choices, then pick the choice closest to your "
                         "prediction. The right answer is usually a small, safe step from "
                         "the text."),
                "key_points": ["Locate the evidence first, then reason from it.",
                               "Predict before you peek at the choices.",
                               "Prefer the cautious step over the dramatic one."],
            },
            {
                "title": "Dodge the traps",
                "body": ("Wrong inferences usually go too far (a leap the text doesn't "
                         "license), use extreme words like always, never, or proves, bring "
                         "in outside knowledge, or quietly contradict the passage. 'Could "
                         "be true' is not enough — it must be forced by the evidence."),
                "key_points": ["Too far: a bigger claim than the evidence supports.",
                               "Too extreme: always/never/proves rarely fit.",
                               "Contradiction: reverses or ignores what the text says."],
            },
            {
                "title": "Try the moves",
                "body": ("A passage says an octopus is colorblind yet changes color when "
                         "muscles widen tiny sacs of pigment under its skin. Ask what must "
                         "be true: the color change is produced by those muscles widening "
                         "the sacs (forced by the text). 'The octopus picks colors to match "
                         "what it sees' contradicts the passage — it's colorblind."),
                "worked_example": ("Find the evidence ('colorblind' + 'muscles widen sacs') "
                                   "-> infer only what it forces, not a tempting leap."),
            },
        ],
    },
    "command_of_evidence": {
        "title": "Command of Evidence",
        "body": ("These questions ask which detail best supports a claim. Find the "
                 "specific sentence or data point that directly backs the claim — not one "
                 "that is merely related to the topic."),
        "key_points": ["Match the evidence to the exact claim.",
                       "Specific, on-point details beat general ones.",
                       "Beware details that are true but off-topic."],
        "screens": [
            {
                "title": "What it asks",
                "body": ("Command-of-evidence questions hand you a claim and ask which "
                         "detail best backs it up. Your job isn't to pick the most "
                         "interesting fact — it's to pick the one that actually proves "
                         "that specific claim. (The SAT also has a data version that asks "
                         "you to read a graph or table; the skill is the same.)"),
                "key_points": ["You're matching evidence to one exact claim.",
                               "'Best supports' means most directly proves it."],
            },
            {
                "title": "How to do it",
                "body": ("First, nail down the claim in your own words — what exactly must "
                         "the detail show? Then test each choice: does it directly make "
                         "that claim more true? The winner connects straight to the claim, "
                         "not just to the general topic."),
                "key_points": ["Restate the claim before reading the choices.",
                               "Ask of each choice: does this prove *that* claim?",
                               "Specific and on-point beats broad and related."],
            },
            {
                "title": "Dodge the traps",
                "body": ("Wrong choices are usually on-topic but off-claim (true, related, "
                         "but proves something else), too general to pin anything down, or "
                         "actually point the other way and weaken the claim. Relevance to "
                         "the topic is not the same as support for the claim."),
                "key_points": ["Off-claim: about the topic, but not the claim.",
                               "Too general: doesn't lock in the specific point.",
                               "Backfire: the detail undercuts the claim."],
            },
            {
                "title": "Try the moves",
                "body": ("Claim: the octopus cannot perceive its own display. The detail "
                         "'the octopus is colorblind, so it cannot see the very hues it "
                         "produces' proves it directly. 'Muscles widen sacs of pigment' is "
                         "true and on-topic, but it supports *how* the color appears, not "
                         "that the animal can't perceive it — an off-claim trap."),
                "worked_example": ("Restate the claim ('can't see its own colors'), then "
                                   "pick the detail that proves exactly that."),
            },
        ],
    },
    "text_structure_purpose": {
        "title": "Text Structure and Purpose",
        "body": ("Every passage is built a certain way — by contrast, cause and effect, "
                 "problem and solution, and so on — to serve a purpose. Ask why the "
                 "author included a part and how the whole is organized."),
        "key_points": ["Identify the organizing pattern.",
                       "Ask what a sentence accomplishes in context.",
                       "Match purpose to the passage's overall aim."],
        "screens": [
            {
                "title": "Two flavors",
                "body": ("These questions come in two shapes. 'Overall structure' asks how "
                         "the whole passage is organized. 'Purpose / function' asks what a "
                         "specific part (often the first or last sentence) is doing. Both "
                         "are about the job of the writing, not just what it says."),
                "key_points": ["Structure = the shape of the whole passage.",
                               "Purpose = the job of one part within it."],
            },
            {
                "title": "Reading for structure",
                "body": ("Sum up each chunk in a few words — 'sets up a puzzle,' 'gives "
                         "the mechanism,' 'adds a twist' — then name the pattern they form. "
                         "Common patterns: contrast, cause and effect, problem then "
                         "solution, claim then support, and general then specific."),
                "key_points": ["Label each part's job, then connect the labels.",
                               "Know the usual patterns so you can name the shape."],
            },
            {
                "title": "Reading for purpose",
                "body": ("For a part, ask: what does this sentence DO here? Verbs help — "
                         "it might introduce, illustrate, qualify, counter, transition, or "
                         "conclude. The right answer names that job AND fits the passage's "
                         "overall aim, not just the local content."),
                "key_points": ["Answer with a function verb (introduce, qualify, conclude).",
                               "The function must fit the whole passage's aim."],
            },
            {
                "title": "Dodge traps & try it",
                "body": ("Traps describe a different part, state true content but the wrong "
                         "function, or name a structure the passage never uses. Example: "
                         "the octopus passage 'introduces a surprising trait, explains its "
                         "mechanism, then notes a deeper puzzle.' 'Lists steps a diver "
                         "should follow' names a structure that isn't there."),
                "worked_example": ("Label the parts (surprise → mechanism → puzzle), then "
                                   "pick the choice that names that shape — not absent steps."),
            },
        ],
    },
    "words_in_context": {
        "title": "Words in Context",
        "body": ("A word's meaning on the test depends on its sentence. Predict a "
                 "substitute that fits the context, then pick the choice closest to your "
                 "prediction. Common words often carry less common meanings here."),
        "key_points": ["Read the whole sentence, not just the word.",
                       "Predict a meaning before reading choices.",
                       "Watch for secondary meanings of familiar words."],
        "screens": [
            {
                "title": "What it asks",
                "body": ("Two close cousins show up here. One gives a word and asks what "
                         "it 'most nearly means' as used in the passage. The other gives a "
                         "blank and asks for the most logical, precise word to fill it. "
                         "Both are decided by the sentence around the word — not by the "
                         "word's dictionary-first meaning."),
                "key_points": ["'Most nearly means' = the meaning that fits *here*.",
                               "Completion = the word the context calls for."],
            },
            {
                "title": "Predict, then match",
                "body": ("Cover the word or blank and read the sentence for clues — "
                         "especially contrast words (but, however) and the overall tone. "
                         "Say your own plain word that fits, then pick the choice closest "
                         "to it. Deciding before you read the options keeps the traps from "
                         "steering you."),
                "key_points": ["Use clues in the sentence to predict a word.",
                               "Pick the choice nearest your prediction.",
                               "Let contrast words flip the meaning you expect."],
            },
            {
                "title": "Dodge the traps",
                "body": ("The most common meaning of a familiar word is often the trap — "
                         "the answer wants a secondary sense. Also watch for words that are "
                         "loose synonyms in general but wrong for this sentence, words with "
                         "the wrong tone (too strong or too negative), and words that don't "
                         "fit the grammar."),
                "key_points": ["The everyday meaning is often a decoy.",
                               "'Synonym in general' isn't 'fits this sentence'.",
                               "Match tone/connotation, not just rough meaning."],
            },
            {
                "title": "Try the moves",
                "body": ("'In less than a second it can flush deep red.' Predict a word: "
                         "fill or flood with color. The match is 'become suffused with "
                         "color.' 'Rinse clean with water' is flush's everyday meaning — "
                         "the classic trap — and 'grow red with embarrassment' adds a "
                         "feeling the sentence never gives."),
                "worked_example": ("Predict 'fill with color' for 'flush' -> choose "
                                   "'become suffused with color', not the everyday 'rinse'."),
            },
        ],
    },
    "cross_text_connections": {
        "title": "Cross-Text Connections",
        "body": ("Paired passages present two views on one topic. Pin down each author's "
                 "claim, then judge how they relate: agreement, disagreement, or one "
                 "qualifying the other. Predict how one author would answer the other."),
        "key_points": ["Summarize each text's main claim first.",
                       "Determine the relationship between the claims.",
                       "Anticipate how one author would respond to the other."],
        "screens": [
            {
                "title": "Two texts, one topic",
                "body": ("Cross-text questions give two short passages on the same subject "
                         "and ask how they relate. The two common asks are: 'What is the "
                         "relationship between the texts?' and 'How would the author of "
                         "Text 2 respond to Text 1?' Everything rides on each author's "
                         "actual position."),
                "key_points": ["First job: state each author's claim in your own words.",
                               "Then judge how the two claims relate."],
            },
            {
                "title": "Name the relationship",
                "body": ("Decide how Text 2 stands toward Text 1: agree, disagree, "
                         "partly agree (qualify), add a cause or example, or shift the "
                         "focus. Watch the tone — 'however,' 'yet,' and 'admittedly' are "
                         "signposts. Be precise: 'disagrees' and 'qualifies' are different "
                         "answers."),
                "key_points": ["Options: agree / disagree / qualify / extend / reframe.",
                               "Transition and tone words reveal the stance."],
            },
            {
                "title": "Predict the response",
                "body": ("For 'how would Author 2 respond,' don't invent a new opinion — "
                         "use only what Text 2 already says, applied to Text 1's specific "
                         "claim. Find the line in Text 2 that bears on that claim and "
                         "paraphrase it. The answer must be something Text 2's author "
                         "truly holds."),
                "key_points": ["Respond using Text 2's stated views only.",
                               "Aim the response at Text 1's exact claim."],
            },
            {
                "title": "Dodge traps & try it",
                "body": ("Traps overstate the conflict (says 'flatly rejects' when Text 2 "
                         "only qualifies), swap which author thinks what, or bring in a "
                         "view neither text holds. If Text 1 calls homework essential and "
                         "Text 2 says it helps only in small amounts, Author 2 would "
                         "'partly agree but warn against overuse' — not 'completely "
                         "reject homework.'"),
                "worked_example": ("State both claims, label the link (qualifies, not "
                                   "rejects), then pick the precise relationship."),
            },
        ],
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
        "screens": [
            {
                "title": "Independent vs. dependent",
                "body": ("An independent clause could be its own sentence ('Attendance "
                         "doubled'). A dependent clause cannot — it starts with a word like "
                         "because, although, when, or since ('Although attendance "
                         "doubled'). Knowing which is which decides the punctuation."),
                "key_points": ["Independent = a complete sentence on its own.",
                               "Dependent = starts with because/although/when/since/while."],
            },
            {
                "title": "Joining two independent clauses",
                "body": ("Two independent clauses need a real boundary between them: a "
                         "period (two sentences), a semicolon, or a comma PLUS a FANBOYS "
                         "word (and, but, or, so…). A comma by itself is a comma splice; "
                         "nothing at all is a run-on."),
                "key_points": ["Period, semicolon, or comma + FANBOYS — pick one.",
                               "Comma alone = splice; no punctuation = run-on.",
                               "Don't use a semicolon AND 'and' together."],
            },
            {
                "title": "When one clause is dependent",
                "body": ("If the sentence opens with a dependent clause, attach it to the "
                         "main clause with a comma: 'Although attendance doubled, the venue "
                         "stayed calm.' A period there leaves a fragment, and a semicolon "
                         "wrongly treats the dependent clause as independent."),
                "key_points": ["Dependent + main clause = join with a comma.",
                               "A period after a dependent clause = fragment.",
                               "Don't semicolon a dependent clause."],
            },
            {
                "title": "Try the moves",
                "body": ("Two independent clauses: 'The bakery sells out by noon' + "
                         "'regular customers arrive early.' A semicolon joins them; a comma "
                         "alone would splice. But 'Because the bakery sells out by noon, "
                         "regular customers arrive early' needs a comma — the 'because' "
                         "part can't stand alone."),
                "worked_example": ("Two independent -> period/semicolon. Starts with "
                                   "'Because…' -> comma (not a period or semicolon)."),
            },
        ],
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
        "screens": [
            {
                "title": "Relationship first, word second",
                "body": ("A transition names how the second idea relates to the first. "
                         "Cover the choices and decide the link yourself: does idea 2 push "
                         "back on idea 1, result from it, add to it, illustrate it, or come "
                         "next in time? Pick the relationship before any word."),
                "key_points": ["Read both ideas; name the relationship in your head.",
                               "Only then look for a transition that matches it."],
            },
            {
                "title": "Know the families",
                "body": ("Group transitions by job: Contrast — however, but, yet, on the "
                         "other hand. Cause/result — therefore, thus, as a result. Addition "
                         "— moreover, furthermore, also. Example — for instance, for "
                         "example. Sequence — first, then, later. Emphasis — indeed, in "
                         "fact."),
                "key_points": ["Contrast / cause / addition / example / sequence / emphasis.",
                               "Memorize a couple of words per family."],
            },
            {
                "title": "Dodge the traps",
                "body": ("The wrong choices are usually transitions from a *different* "
                         "family that sound smooth but signal the wrong link — the SAT "
                         "leans on the near-misses (addition vs. emphasis, cause vs. "
                         "sequence). 'However' and 'therefore' are opposites; don't let a "
                         "sentence's flow fool you into the wrong relationship."),
                "key_points": ["A smooth-sounding word can still be the wrong relationship.",
                               "Watch close pairs: addition vs. emphasis, cause vs. sequence.",
                               "Plug your choice back in and check the logic."],
            },
            {
                "title": "Try the moves",
                "body": ("'The new policy promised faster service. ____, wait times "
                         "actually grew longer.' Idea 2 contradicts idea 1, so the link is "
                         "contrast: 'However.' 'Therefore' (result) and 'For example' "
                         "(illustration) signal the wrong relationship even though the "
                         "sentence still reads smoothly."),
                "worked_example": ("Promise vs. opposite outcome = contrast -> 'However', "
                                   "not 'Therefore' (result) or 'For example'."),
            },
        ],
    },
    "concision": {
        "title": "Concision",
        "body": ("Good writing says it once. Eliminate redundancy (repeating the same "
                 "idea in different words) and wordy filler. The best choice is usually "
                 "the shortest one that keeps the full meaning and stays grammatical."),
        "key_points": ["Cut words that repeat an idea.",
                       "Prefer the shortest clear, grammatical option.",
                       "Don't delete meaning — only redundancy."],
        "screens": [
            {
                "title": "Say it once",
                "body": ("Concision questions ask for the clearest version with no "
                         "repeated ideas and no filler. The goal is to keep the full "
                         "meaning while cutting words that don't add anything. Shorter "
                         "usually wins — as long as nothing important is lost."),
                "key_points": ["Keep all the meaning; cut only the dead weight.",
                               "Among correct options, the shortest is usually best."],
            },
            {
                "title": "Spot the padding",
                "body": ("Watch for two things: redundancy (saying the same idea twice — "
                         "'free gift,' 'postponed until later') and filler phrases ('due "
                         "to the fact that' = 'because,' 'in order to' = 'to'). If removing "
                         "words changes nothing about the meaning, remove them."),
                "key_points": ["Redundancy: two words for one idea.",
                               "Filler: long phrases that mean a short word.",
                               "Test: does cutting it change the meaning? If no, cut."],
            },
            {
                "title": "Don't overcut",
                "body": ("Concise isn't the same as shortest-at-any-cost. The right answer "
                         "still has to be grammatical and keep the actual information. A "
                         "choice that drops a needed detail or breaks the sentence is wrong "
                         "even if it's the fewest words."),
                "key_points": ["The shortest option can be wrong if it loses meaning.",
                               "Stay grammatical — don't create a fragment."],
            },
            {
                "title": "Try the moves",
                "body": ("'Due to the fact that of scheduling, the meeting was postponed "
                         "until a later time' is padded twice over. 'The meeting was "
                         "postponed' keeps the whole meaning with none of the filler — "
                         "'postponed' already means 'put off until later.'"),
                "worked_example": ("Cut 'due to the fact that' and 'until a later time' "
                                   "(redundant with 'postponed') -> 'The meeting was "
                                   "postponed.'"),
            },
        ],
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
        "screens": [
            {
                "title": "Read the table first",
                "body": ("Before the choices, read the caption, the column headers, and "
                         "the units. Then trace the numbers down the column: are they "
                         "going up, going down, or bouncing around? Know the actual trend "
                         "before anything tempts you."),
                "key_points": ["Caption + headers + units, every time.",
                               "Name the trend in your own words first."],
            },
            {
                "title": "Match data to the claim",
                "body": ("You're not picking the most interesting fact — you're picking "
                         "the statement whose numbers truly support the given claim. Check "
                         "the values it cites against the table. If a choice's numbers or "
                         "direction don't match the table, it's out, even if it sounds "
                         "data-y."),
                "key_points": ["The right choice's numbers match the table exactly.",
                               "Direction and endpoints both have to fit the claim."],
            },
            {
                "title": "Dodge the traps",
                "body": ("Common wrong answers: says it 'held steady' or moved both ways "
                         "when it didn't; claims it changed by the *same amount* each year "
                         "when the steps actually vary; pins the change to one span when "
                         "every year moved; or exaggerates a one-year jump. Check the "
                         "arithmetic — don't trust the vibe."),
                "key_points": ["'Same amount each year' is false when the steps differ.",
                               "'Held steady' / 'both directions' must match the column.",
                               "Verify any specific number it names."],
            },
            {
                "title": "Try the moves",
                "body": ("Claim: the value rose steadily 2018–2021. Table: 40, 46, 54, "
                         "60. It rises every year, so 'the value increased each year, from "
                         "40 to 60' is supported. 'Rose by the same amount each year' is a "
                         "trap — the steps are 6, 8, 6, not constant."),
                "worked_example": ("Trend = up every year (40→60). Reject 'constant "
                                   "increase': the yearly steps (6, 8, 6) aren't equal."),
            },
        ],
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
        "screens": [
            {
                "title": "The goal is everything",
                "body": ("You get a few bullet-point notes and one specific goal — to "
                         "introduce a topic, emphasize a contrast, compare two things, and "
                         "so on. Your job is to pick the sentence that accomplishes THAT "
                         "goal using the notes. The goal, not the topic, decides the "
                         "answer."),
                "key_points": ["Read and underline the goal first.",
                               "Every choice may be true; only one meets the goal."],
            },
            {
                "title": "How to choose",
                "body": ("Put the goal in plain words ('I need to highlight the "
                         "difference'). Then check each choice: does it actually do that "
                         "job with the relevant notes? The right answer pulls in the notes "
                         "that serve the goal and leaves out the rest."),
                "key_points": ["Restate the goal as a task.",
                               "Keep the notes that serve it; ignore the others.",
                               "Match the choice's job to the goal's job."],
            },
            {
                "title": "Dodge the traps",
                "body": ("Wrong choices are usually true and on-topic but do the wrong "
                         "job — they describe when the goal was to compare, or state one "
                         "fact when the goal was to generalize. A choice can use the notes "
                         "accurately and still miss the goal."),
                "key_points": ["Accurate but off-goal is the #1 trap.",
                               "Wrong job = wrong answer, even if it's true.",
                               "Don't reward the choice that simply says the most."],
            },
            {
                "title": "Try the moves",
                "body": ("Goal: emphasize that a method is fast. Notes include its cost, "
                         "its accuracy, and that it runs in seconds. The right sentence "
                         "leads with the speed ('The method returns results in seconds'); "
                         "a choice about its cost is accurate but does the wrong job."),
                "worked_example": ("Goal = stress speed -> pick the sentence built around "
                                   "'in seconds', not the (true) one about cost."),
            },
        ],
    },
}


# Multi-screen mini-lessons authored separately and merged into TEACHING below,
# so each teaching card can open with a 2-5 screen "how to solve" intro.
TEACHING_SCREENS = {
    "subject_verb_agreement": [
        {"title": "Match the verb to the subject",
         "body": ("A verb agrees with its subject in number: a singular subject takes a "
                  "singular verb, a plural subject a plural verb. The trick is finding the "
                  "real subject — it's often not the noun closest to the verb."),
         "key_points": ["Singular subject -> singular verb; plural -> plural.",
                        "Find the true subject before choosing the verb."]},
        {"title": "Ignore what's in between",
         "body": ("Phrases between the subject and verb — especially 'of …' phrases — are "
                  "there to bait you. Mentally cross them out: 'The box of old tools (is/"
                  "are)' -> 'The box … is.' Also know that 'each,' 'every,' and 'neither' "
                  "are singular even though they feel plural."),
         "key_points": ["Cross out 'of the …' phrases, then check.",
                        "each / every / neither / one = singular."]},
        {"title": "Try the moves",
         "body": ("'The collection of rare coins (was/were) donated.' The subject is "
                  "'collection' (singular), not 'coins,' so the verb is 'was.' The plural "
                  "'coins' right before the verb is the trap."),
         "worked_example": "The list of winners WAS posted (subject = list, not winners)."},
    ],
    "punctuation": [
        {"title": "Possessive vs. plural",
         "body": ("An apostrophe shows possession, not a plural. Singular owner: add 's "
                  "(the dog's leash). Plural owner already ending in -s: add just an "
                  "apostrophe (the dogs' leashes). A plain -s with no apostrophe just makes "
                  "a plural."),
         "key_points": ["Singular owner: 's.  Plural owner ending in -s: s'.",
                        "No apostrophe = plural, not possessive."]},
        {"title": "its / it's and commas",
         "body": ("'It's' always means 'it is' or 'it has'; the possessive 'its' has no "
                  "apostrophe. For commas, don't split a subject from its verb, and use a "
                  "pair of commas around nonessential information you could lift out."),
         "key_points": ["it's = it is; its = belonging to it.",
                        "Nonessential info gets a comma on both sides."]},
        {"title": "Try the moves",
         "body": ("'The teams' uniforms' = uniforms of several teams. 'The team's "
                  "uniform' = one team. And 'The dog wagged its tail' takes no apostrophe — "
                  "'it's tail' would read 'it is tail.'"),
         "worked_example": "Workers' tools (plural owners) vs. a worker's tools (one)."},
    ],
    "pronouns": [
        {"title": "Case follows the job",
         "body": ("Use subject pronouns (I, he, she, they, who) for subjects and object "
                  "pronouns (me, him, her, them, whom) for objects. The pronoun's role in "
                  "the sentence — not how it sounds — decides the case."),
         "key_points": ["Subjects: I/he/she/they/who.",
                        "Objects: me/him/her/them/whom."]},
        {"title": "Two quick tests",
         "body": ("In a compound ('Maya and I/me'), drop the other person and listen: "
                  "'…thanked me,' not '…thanked I.' For who vs. whom, answer with he/him: "
                  "if 'he' fits, use 'who'; if 'him' fits, use 'whom' (both end in m)."),
         "key_points": ["Compound: remove the other name and check.",
                        "he = who; him = whom."]},
        {"title": "Try the moves",
         "body": ("'The coach emailed Noah and (I/me).' Drop 'Noah and': 'emailed me.' "
                  "'The athlete (who/whom) the judges praised' — the judges praised HIM, "
                  "so it's 'whom.'"),
         "worked_example": "He won -> 'who won'; judges praised him -> 'whom they praised.'"},
    ],
    "modifiers": [
        {"title": "Modifiers need the right neighbor",
         "body": ("An opening descriptive phrase attaches to the noun that comes right "
                  "after the comma. If that noun can't logically do the action, the "
                  "modifier 'dangles' and the sentence says something absurd."),
         "key_points": ["The noun after the comma must fit the opening phrase.",
                        "Wrong noun = a dangling/misplaced modifier."]},
        {"title": "Spot the absurdity",
         "body": ("Read the opening phrase, then ask 'who or what is doing this?' The "
                  "answer must be the first word after the comma. 'Walking to school, the "
                  "rain soaked us' wrongly says the rain was walking."),
         "key_points": ["Name the doer, then check it's right after the comma.",
                        "Fix by putting the right noun first (or rewriting)."]},
        {"title": "Try the moves",
         "body": ("'Having studied all night, the exam felt easy' — the exam didn't study. "
                  "The right subject is the student: 'Having studied all night, she found "
                  "the exam easy.'"),
         "worked_example": "Opening phrase about a person -> a person must follow the comma."},
    ],
    "verb_tense": [
        {"title": "Match the time",
         "body": ("Pick the tense the sentence's time clues call for: 'last year,' "
                  "'in 1990' -> past; 'today,' 'currently' -> present; 'next year,' 'will' "
                  "-> future. Don't switch times without a reason."),
         "key_points": ["Time words set the tense.",
                        "Keep tense consistent unless the meaning changes."]},
        {"title": "Forms that trip people up",
         "body": ("An -ing word by itself can't be the main verb ('The team winning' is "
                  "not a sentence). Use perfect tenses for one action before another: "
                  "'had finished' (before a past point), 'has finished' (up to now)."),
         "key_points": ["-ing alone isn't a complete verb.",
                        "had + verb = earlier past; has/have + verb = up to now."]},
        {"title": "Try the moves",
         "body": ("'Last spring the crew (plants/planted) trees.' 'Last spring' is past, "
                  "so 'planted.' 'By the time we arrived, the show (started/had started)' "
                  "needs 'had started' — it happened first."),
         "worked_example": "Last year -> 'traveled' (past), not 'travels.'"},
    ],
    "parallel_structure": [
        {"title": "Same form in a series",
         "body": ("When items are joined in a list or by and/or, they must share the same "
                  "grammatical form: all -ing, all nouns, or all to-verbs. A mismatch "
                  "stands out as the error."),
         "key_points": ["-ing with -ing, noun with noun, to-verb with to-verb.",
                        "Find the item whose form doesn't match the others."]},
        {"title": "Also for paired connectors",
         "body": ("Parallelism applies to paired structures too — 'not only … but also,' "
                  "'either … or,' 'both … and.' The words after each half should line up in "
                  "form."),
         "key_points": ["Make the parts after 'either/or' and 'not only/but also' match.",
                        "Comparisons ('more X than Y') should be parallel too."]},
        {"title": "Try the moves",
         "body": ("'She likes hiking, biking, and to swim' breaks the pattern — two -ing "
                  "words then a to-verb. Make the third match: 'hiking, biking, and "
                  "swimming.'"),
         "worked_example": "to read, to write, and to edit (all to-verbs), not '…editing.'"},
    ],
    "pronoun_antecedent": [
        {"title": "Agree in number",
         "body": ("A pronoun must match the noun it stands for (its antecedent) in number. "
                  "A singular antecedent takes a singular pronoun (its, his, her); a plural "
                  "antecedent takes a plural one (their)."),
         "key_points": ["Singular antecedent -> its/his/her.",
                        "Plural antecedent -> their."]},
        {"title": "Find the real antecedent",
         "body": ("Look past phrases that come between the noun and the pronoun. 'The "
                  "company, along with its partners,' is still singular — 'company,' not "
                  "'partners,' is the antecedent. Collective nouns (team, committee) are "
                  "usually singular."),
         "key_points": ["Ignore 'along with …,' 'of the …' phrases.",
                        "team / committee / company = singular."]},
        {"title": "Try the moves",
         "body": ("'The committee, along with the regional offices, released ___ report.' "
                  "The antecedent is 'committee' (singular), so 'its' — the plural "
                  "'offices' is bait. Note: 'it's' means 'it is,' never possession."),
         "worked_example": "The players released THEIR statement; the team released ITS."},
    ],
    "linear_equations": [
        {"title": "Undo to isolate",
         "body": ("A linear equation keeps the variable to the first power. Solve by "
                  "undoing operations in reverse order, doing the same thing to both sides: "
                  "move constants first (add/subtract), then remove the coefficient "
                  "(divide)."),
         "key_points": ["Whatever you do to one side, do to the other.",
                        "Constants first, then divide by the coefficient."]},
        {"title": "Clear the clutter",
         "body": ("If there are parentheses, distribute first. If there are fractions, "
                  "multiply every term by the common denominator. If the variable appears "
                  "on both sides, collect the variable terms on one side and the numbers on "
                  "the other."),
         "key_points": ["Distribute, then combine like terms.",
                        "Get all variable terms on one side."]},
        {"title": "Check and watch signs",
         "body": ("Most mistakes are sign errors when moving terms across the equals sign — "
                  "the term flips sign. Plug your answer back in to confirm both sides "
                  "match."),
         "key_points": ["Moving a term across '=' flips its sign.",
                        "Substitute your answer back to verify."]},
        {"title": "Try the moves",
         "body": ("Solve 3(x + 2) = 18. Distribute: 3x + 6 = 18. Subtract 6: 3x = 12. "
                  "Divide by 3: x = 4. Check: 3(4 + 2) = 18. ✓"),
         "worked_example": "3x + 5 = 20 -> 3x = 15 -> x = 5."},
    ],
    "linear_inequalities": [
        {"title": "Solve like an equation…",
         "body": ("Isolate the variable exactly as you would in an equation — add, "
                  "subtract, multiply, and divide both sides. The answer is a range of "
                  "values, not a single number."),
         "key_points": ["Same isolating steps as equations.",
                        "The solution is a range (many values)."]},
        {"title": "…but flip on a negative",
         "body": ("The one special rule: if you multiply or divide both sides by a "
                  "negative number, reverse the inequality sign. ≤ and ≥ include the "
                  "endpoint; < and > do not."),
         "key_points": ["Multiply/divide by a negative -> flip the sign.",
                        "≤ / ≥ include the endpoint; < / > exclude it."]},
        {"title": "Try the moves",
         "body": ("Solve -2x + 1 < 9. Subtract 1: -2x < 8. Divide by -2 AND flip: x > -4. "
                  "On a number line that's an open circle at -4 shading to the right."),
         "worked_example": "2x + 3 ≤ 11 -> 2x ≤ 8 -> x ≤ 4 (no flip; positive divide)."},
    ],
    "systems_of_equations": [
        {"title": "Two equations, two unknowns",
         "body": ("A system asks for the values that make BOTH equations true at once — "
                  "the point where the two lines cross. Two main methods: substitution and "
                  "elimination."),
         "key_points": ["A solution satisfies both equations.",
                        "Pick substitution or elimination."]},
        {"title": "Substitution",
         "body": ("Solve one equation for one variable, then plug that expression into the "
                  "other equation. Best when a variable already has a coefficient of 1 "
                  "(easy to isolate)."),
         "key_points": ["Isolate a variable, then substitute into the other equation.",
                        "Solve for one variable, then back-substitute for the other."]},
        {"title": "Elimination",
         "body": ("Line the equations up and add or subtract them to cancel one variable. "
                  "If needed, multiply an equation so one variable's coefficients match. "
                  "Best when adding the equations cancels a variable cleanly."),
         "key_points": ["Add/subtract to cancel a variable.",
                        "Scale an equation first so coefficients line up."]},
        {"title": "Try the moves",
         "body": ("x + y = 7 and x − y = 1. Add them: 2x = 8, so x = 4. Back-substitute: "
                  "4 + y = 7, so y = 3. Solution: (4, 3)."),
         "worked_example": "Add the equations to cancel y -> 2x = 8 -> x = 4, y = 3."},
    ],
    "functions": [
        {"title": "f(x) is a rule",
         "body": ("f(x) is a machine: put an input in for x, get an output. To evaluate "
                  "f at a number, substitute that number everywhere x appears and "
                  "simplify, minding order of operations."),
         "key_points": ["f(k): replace every x with k.",
                        "Square and handle negatives before multiplying."]},
        {"title": "Going backward",
         "body": ("Sometimes you're given the output and asked for the input: 'if "
                  "f(x) = N, find x.' Set the rule equal to N and solve the equation — "
                  "undo the constant, then the coefficient."),
         "key_points": ["f(x) = N -> set the rule equal to N and solve.",
                        "Solving for x is one step beyond plugging in."]},
        {"title": "Quadratic care",
         "body": ("With f(x) = ax² + bx + c, square the input first (a negative input "
                  "squared is positive), then multiply and add. The most common slip is "
                  "forgetting to square or mishandling a negative."),
         "key_points": ["Square the whole input, including its sign.",
                        "(−k)² is positive."]},
        {"title": "Try the moves",
         "body": ("If f(x) = 2x + 1, then f(3) = 2·3 + 1 = 7. Backward: if f(x) = 7, then "
                  "2x + 1 = 7 -> x = 3. If f(x) = x² − 4 and x = −3, f(−3) = 9 − 4 = 5."),
         "worked_example": "f(3) for 2x+1 = 7; solve 2x+1=7 -> x=3; (−3)² − 4 = 5."},
    ],
    "quadratics": [
        {"title": "Roots from factors",
         "body": ("Many quadratics factor into (x − r₁)(x − r₂) = 0. Setting each factor "
                  "to zero gives the solutions (roots) r₁ and r₂. Watch the signs: a "
                  "factor (x − 5) has root +5."),
         "key_points": ["Set each factor equal to zero.",
                        "Factor (x − r) has root r (sign flips)."]},
        {"title": "Sum and product shortcuts",
         "body": ("For x² + bx + c, the roots add to −b and multiply to c (for a leading "
                  "1). More generally, sum = −b/a and product = c/a — handy when you only "
                  "need the sum or product, not each root."),
         "key_points": ["Sum of roots = −b/a.",
                        "Product of roots = c/a."]},
        {"title": "How many real roots?",
         "body": ("The discriminant b² − 4ac tells you the number of real solutions "
                  "without solving: positive -> two, zero -> one (a repeated root), "
                  "negative -> none. Compute it carefully, signs included."),
         "key_points": ["b²−4ac > 0: two real roots.",
                        "= 0: one; < 0: none."]},
        {"title": "Try the moves",
         "body": ("x² − 5x + 6 = 0 factors as (x − 2)(x − 3) = 0, so x = 2 or 3 (sum 5, "
                  "product 6). For x² + x + 4 = 0, the discriminant 1 − 16 = −15 < 0, so "
                  "there are no real solutions."),
         "worked_example": "(x−2)(x−3)=0 -> x=2,3.  D = 1−16 = −15 < 0 -> no real roots."},
    ],
    "exponents_radicals": [
        {"title": "The three core rules",
         "body": ("Same base: multiplying ADDS exponents (xᵃ·xᵇ = xᵃ⁺ᵇ), dividing "
                  "SUBTRACTS them (xᵃ ÷ xᵇ = xᵃ⁻ᵇ), and a power of a power MULTIPLIES "
                  "them ((xᵃ)ᵇ = xᵃᵇ). The base never changes."),
         "key_points": ["Multiply -> add exponents; divide -> subtract.",
                        "Power of a power -> multiply exponents."]},
        {"title": "Negative and zero",
         "body": ("A zero exponent is 1 (x⁰ = 1). A negative exponent means a reciprocal: "
                  "x⁻ⁿ = 1/xⁿ. So when subtracting exponents gives a negative, the answer "
                  "is a fraction."),
         "key_points": ["x⁰ = 1.",
                        "x⁻ⁿ = 1/xⁿ (a negative exponent flips it)."]},
        {"title": "Roots are fractional powers",
         "body": ("A radical is a fractional exponent: √x = x^(1/2), and ⁿ√(xᵏ) = "
                  "x^(k/n). Rewriting roots as powers lets you use the same exponent "
                  "rules to simplify."),
         "key_points": ["√x = x^(1/2); cube root = x^(1/3).",
                        "Convert roots to powers, then apply the rules."]},
        {"title": "Try the moves",
         "body": ("(2³)² ÷ 2⁸ = 2⁶ ÷ 2⁸ = 2⁻² = 1/2² = 1/4. Apply power-of-a-power, then "
                  "subtract for the division, then read the negative exponent as a "
                  "reciprocal."),
         "worked_example": "(2³)² ÷ 2⁸ = 2⁶⁻⁸ = 2⁻² = 1/4."},
    ],
    "polynomials": [
        {"title": "Multiply with FOIL",
         "body": ("To expand (ax + b)(cx + d), multiply every pair: First, Outer, Inner, "
                  "Last. The x² term is ac, the x term is (ad + bc), and the constant is "
                  "bd. Combine the two middle (x) terms."),
         "key_points": ["x² coeff = a·c; constant = b·d.",
                        "x coeff = a·d + b·c (add the two middle terms)."]},
        {"title": "Mind the signs",
         "body": ("Negative terms flip signs as you multiply. (x − 5)(x + 2) gives a "
                  "constant of −10 and a middle term of −3x. Track each sign rather than "
                  "rushing."),
         "key_points": ["A negative times a positive is negative.",
                        "Recombine middle terms with their signs."]},
        {"title": "Factoring is FOIL in reverse",
         "body": ("To factor x² + bx + c, find two numbers that multiply to c and add to "
                  "b; those give the factors (x + p)(x + q). A factor (x − r) means r is a "
                  "root that makes the trinomial zero."),
         "key_points": ["Find two numbers: product c, sum b.",
                        "Factor (x − r) <-> root r."]},
        {"title": "Try the moves",
         "body": ("(x − 4)(x + 3) = x² − x − 12 (x² term 1, middle −x, constant −12). "
                  "Reverse: x² − x − 12 factors back to (x − 4)(x + 3), so (x − 4) is a "
                  "factor."),
         "worked_example": "(x−4)(x+3) = x² − x − 12; so (x−4) is a factor of it."},
    ],
    "word_problems": [
        {"title": "Translate, then solve",
         "body": ("Turn the words into an equation. 'Flat fee plus a rate' is "
                  "total = fee + rate·n. 'Sum' means add; 'is/equals' is the = sign; "
                  "'more than' and 'times' tell you how the quantities relate."),
         "key_points": ["Name the unknown, then write an equation.",
                        "Translate keywords: sum (+), times (×), is (=)."]},
        {"title": "Undo step by step",
         "body": ("Solve by reversing what was done to the unknown. For total = fee + "
                  "rate·n, subtract the fee first, then divide by the rate. Do the inverse "
                  "operations in reverse order."),
         "key_points": ["Subtract constants first, then divide by the rate.",
                        "Inverse operations, in reverse order."]},
        {"title": "Two related unknowns",
         "body": ("When two quantities are linked ('one is 12 more than the other,' 'the "
                  "larger is 3 times the smaller'), write both in terms of one variable, "
                  "then use the total. e.g., n + 3n = total."),
         "key_points": ["Express both quantities with one variable.",
                        "Then substitute into the sum/total."]},
        {"title": "Try the moves",
         "body": ("A fee of $20 plus $15/hour totals $95: 20 + 15h = 95 -> 15h = 75 -> "
                  "h = 5. Sum of two numbers is 40 and one is 6 more: larger = "
                  "(40 + 6)/2 = 23."),
         "worked_example": "20 + 15h = 95 -> h = 5.  larger = (sum+diff)/2 = (40+6)/2 = 23."},
    ],
    "absolute_value": [
        {"title": "Two cases",
         "body": ("|expression| = c means the inside equals c OR equals −c, because both "
                  "are distance c from zero. So an absolute-value equation usually has two "
                  "solutions — solve both linear cases."),
         "key_points": ["|A| = c -> A = c or A = −c.",
                        "Expect two solutions, one on each side."]},
        {"title": "With a coefficient",
         "body": ("If there's a coefficient, like |kx − b| = c, still split into the two "
                  "cases (kx − b = c and kx − b = −c), then solve each for x by "
                  "isolating and dividing by k."),
         "key_points": ["Split first, then solve each case for x.",
                        "Divide by the coefficient at the end."]},
        {"title": "Absolute-value inequalities",
         "body": ("|x − a| ≤ c means x is within c of a, i.e., a − c ≤ x ≤ a + c — a whole "
                  "range. To count integers in an inclusive range, do high − low + 1 "
                  "(here, 2c + 1)."),
         "key_points": ["|x − a| ≤ c -> a − c ≤ x ≤ a + c.",
                        "Integer count of an inclusive range = high − low + 1."]},
        {"title": "Try the moves",
         "body": ("|x − 3| = 5 -> x − 3 = 5 or −5 -> x = 8 or −2. And |x − 3| ≤ 5 means "
                  "−2 ≤ x ≤ 8, which contains 8 − (−2) + 1 = 11 integers."),
         "worked_example": "|x−3|=5 -> x=8 or −2.  |x−3|≤5 -> 11 integers (−2…8)."},
    ],
    "exponential": [
        {"title": "Multiply, don't add",
         "body": ("Exponential change multiplies by the same factor each period; linear "
                  "change adds the same amount. 'Doubles every hour' or 'loses half each "
                  "day' is exponential — the step gets bigger (or smaller) over time."),
         "key_points": ["Exponential = repeated multiplication by a factor.",
                        "Linear = repeated addition of a fixed amount."]},
        {"title": "The model",
         "body": ("After t periods, amount = start × (factor)^t. Growth uses a factor > 1 "
                  "(×2, ×3); decay uses a factor < 1 (×½, ×⅓). The starting amount is "
                  "multiplied, and the factor is what's raised to the power t."),
         "key_points": ["amount = start · (factor)^t.",
                        "Growth factor > 1; decay factor < 1."]},
        {"title": "Compute carefully",
         "body": ("To find a value, raise the factor to the number of periods, then "
                  "multiply by the start. For decay, dividing by r each period is the same "
                  "as multiplying by 1/r. Don't multiply the factor by the time."),
         "key_points": ["Do start × factor^t, not start × factor × t.",
                        "Dividing by r per period = ×(1/r)^t."]},
        {"title": "Try the moves",
         "body": ("5 bacteria triple every hour: after 3 hours, 5 × 3³ = 5 × 27 = 135. A "
                  "model for 'n₀ doubles every hour' after t hours is n₀·2^t — not n₀·2·t "
                  "(that's linear)."),
         "worked_example": "5 × 3³ = 135.  Model: n₀ doubling -> n₀·2^t."},
    ],
    "ratios_percentages_units": [
        {"title": "Percent means 'per 100'",
         "body": ("P% of N is (P/100)·N. To go the other way, 'what percent is A of B?' is "
                  "(A/B)·100. Convert the percent to a decimal or fraction and multiply — "
                  "don't forget the ÷100."),
         "key_points": ["P% of N = P/100 × N.",
                        "A is (A/B)·100 percent of B."]},
        {"title": "Percent change",
         "body": ("Percent change = (new − old)/old × 100. The denominator is always the "
                  "ORIGINAL value, not the new one. A drop uses the same formula; the "
                  "result is a decrease."),
         "key_points": ["Change% = (new − old)/old × 100.",
                        "Always divide by the original amount."]},
        {"title": "Working backward",
         "body": ("A P% increase multiplies the original by (1 + P/100); a P% decrease by "
                  "(1 − P/100). Given the result, divide by that factor to recover the "
                  "original — don't just apply the percent to the new value."),
         "key_points": ["new = original × (1 ± P/100).",
                        "Recover the original by dividing by the factor."]},
        {"title": "Try the moves",
         "body": ("20% of 150 = 0.20 × 150 = 30. From 40 to 50 is (50−40)/40 × 100 = 25%. "
                  "If a price after a 25% increase is 100, the original was 100 ÷ 1.25 = 80."),
         "worked_example": "0.2×150=30;  (50−40)/40=25%;  100 ÷ 1.25 = 80."},
    ],
    "proportions": [
        {"title": "Set up the ratio",
         "body": ("A proportion sets two equal ratios: a/b = x/c. Keep the same units in "
                  "the same positions (miles over hours on both sides), then cross-multiply "
                  "and solve for the unknown."),
         "key_points": ["Match units across the equal ratios.",
                        "Cross-multiply: a·c = b·x."]},
        {"title": "Unit rate first",
         "body": ("Often it's quickest to find the unit rate (the amount for ONE) by "
                  "dividing, then multiply by however many you need. '5 cost $15' -> $3 "
                  "each -> 8 cost $24."),
         "key_points": ["Unit rate = total ÷ quantity.",
                        "Then multiply the unit rate by the new quantity."]},
        {"title": "Direct vs. inverse",
         "body": ("Direct: more of one means more of the other (more hours, more miles). "
                  "Inverse: more of one means LESS of the other (more workers, less time). "
                  "For inverse, the product stays constant: w₁·h₁ = w₂·h₂."),
         "key_points": ["Direct -> same direction; ratio is constant.",
                        "Inverse -> opposite direction; the product is constant."]},
        {"title": "Try the moves",
         "body": ("3 machines in 2 hours -> 12 in x hours? Direct: 3/2 = 12/x -> x = 8. "
                  "But 4 workers take 6 hours, so 3 workers (inverse) take 4·6 ÷ 3 = 8 "
                  "hours — fewer workers, more time."),
         "worked_example": "Direct: 3/2 = 12/x -> x=8.  Inverse: 4·6 ÷ 3 = 8 hours."},
    ],
    "data_analysis": [
        {"title": "Read the table first",
         "body": ("Start with the caption, the column headers, and the units. Make sure "
                  "you know what each number represents before you compute anything — the "
                  "wrong column is the classic trap."),
         "key_points": ["Caption + headers + units, every time.",
                        "Confirm which column the question asks about."]},
        {"title": "Common computations",
         "body": ("Total = add the column. Mean = total ÷ count. Range = greatest − least. "
                  "'How many more' = subtract. Match the operation to the wording before "
                  "you start."),
         "key_points": ["Total / mean / range / difference — pick the right one.",
                        "Mean divides by the number of entries."]},
        {"title": "Two-step questions",
         "body": ("Harder items combine steps: compute the mean, then compare a value to "
                  "it; or add two categories and compare to a third. Do one step at a time "
                  "and keep your intermediate numbers."),
         "key_points": ["Compute the mean, then compare to it.",
                        "Track intermediate results; don't rush to an answer."]},
        {"title": "Try the moves",
         "body": ("Days sold 10, 20, 30, 20: total 80, mean 80 ÷ 4 = 20. The busiest day "
                  "(30) is 30 − 20 = 10 above the mean."),
         "worked_example": "mean = 80 ÷ 4 = 20;  busiest 30 is 10 above the mean."},
    ],
    "statistics": [
        {"title": "Center: mean, median, mode",
         "body": ("Mean is the average (sum ÷ count). Median is the middle value when the "
                  "data is sorted (average the two middle ones if the count is even). Mode "
                  "is the most frequent value."),
         "key_points": ["Mean = sum ÷ count.",
                        "Median = middle of the sorted list; mode = most frequent."]},
        {"title": "Spread: range",
         "body": ("Range measures how spread out the data is: greatest − least. It's a "
                  "quick measure of spread and is easy to confuse with the other "
                  "statistics, so read the question word carefully."),
         "key_points": ["Range = greatest − least.",
                        "Don't mix up range with mean or median."]},
        {"title": "Work backward from the mean",
         "body": ("If you know the mean and the count, you know the TOTAL (mean × count). "
                  "That lets you find a missing value: total minus the values you do know "
                  "gives the one you don't."),
         "key_points": ["Total = mean × count.",
                        "Missing value = total − (sum of the known values)."]},
        {"title": "Try the moves",
         "body": ("Mean of 4, 6, 8, 10, 12 is 40 ÷ 5 = 8; median is 8; range is 12 − 4 = 8. "
                  "If five numbers average 10 and four are 8, 9, 11, 12 (sum 40), the fifth "
                  "is 50 − 40 = 10."),
         "worked_example": "mean=40÷5=8.  Missing: 10·5 − 40 = 10."},
    ],
    "probability": [
        {"title": "Favorable over total",
         "body": ("The probability of an event is (favorable outcomes) ÷ (total outcomes). "
                  "For one marble from a bag, it's (that colour) ÷ (all marbles). Keep the "
                  "TOTAL in the denominator."),
         "key_points": ["P = favorable ÷ total.",
                        "The denominator is the total number of outcomes."]},
        {"title": "Complement and 'or'",
         "body": ("P(not A) = 1 − P(A) = (everything else) ÷ total. For mutually exclusive "
                  "outcomes, P(A or B) adds the favorable counts: (A + B) ÷ total."),
         "key_points": ["P(not A) = 1 − P(A).",
                        "P(A or B) = (count A + count B) ÷ total (no overlap)."]},
        {"title": "Without replacement",
         "body": ("If you don't put the first item back, the second draw has one fewer of "
                  "that item AND one fewer total. P(both A) = (A/total)·((A−1)/(total−1)). "
                  "Both numbers drop by one."),
         "key_points": ["Second draw: subtract 1 from favorable AND from total.",
                        "Multiply the two draw probabilities."]},
        {"title": "Try the moves",
         "body": ("Bag of 3 red, 5 blue (8 total): P(red) = 3/8; P(not red) = 5/8. Two "
                  "reds without replacement: 3/8 × 2/7 = 6/56 = 3/28."),
         "worked_example": "P(red)=3/8;  two reds = 3/8 × 2/7 = 3/28."},
    ],
    "two_way_tables": [
        {"title": "Rows, columns, totals",
         "body": ("A two-way table sorts data by two categories at once. Each cell is a "
                  "count; the row totals, column totals, and grand total sit on the "
                  "edges. The whole question is choosing the right total to divide by."),
         "key_points": ["Cells are counts; the margins are the totals.",
                        "Pick the total that matches what's being asked."]},
        {"title": "Three kinds of probability",
         "body": ("Marginal: a whole row or column ÷ grand total. Joint: a single cell ÷ "
                  "grand total ('both A and B'). Conditional: a cell ÷ that row's or "
                  "column's total ('given A, the chance of B')."),
         "key_points": ["Marginal & joint divide by the grand total.",
                        "Conditional divides by the row/column you're given."]},
        {"title": "'Given' changes the denominator",
         "body": ("The word 'given' (or 'of the …') means you only look within that group, "
                  "so divide by that group's total, not the grand total. This is the most "
                  "common place to slip."),
         "key_points": ["'Given X' -> denominator is X's total.",
                        "No 'given' -> denominator is the grand total."]},
        {"title": "Try the moves",
         "body": ("Suppose 20 of 50 responses are in the Cats row, and within the Weekday "
                  "column (total 30) 12 are Cats. P(Cats) = 20/50 = 2/5. P(Cats given "
                  "Weekday) = 12/30 = 2/5 — note the different denominator."),
         "worked_example": "P(Cats)=20/50.  P(Cats | Weekday)=12/30 (column total, not 50)."},
    ],
    "area_volume": [
        {"title": "Area formulas",
         "body": ("Area measures the flat space inside a shape. Rectangle = base × "
                  "height. Triangle = ½ × base × height (it's half a rectangle). Circle = "
                  "πr². Match the formula to the shape in the figure."),
         "key_points": ["Rectangle: base × height.",
                        "Triangle: ½ × base × height.  Circle: πr²."]},
        {"title": "Volume formulas",
         "body": ("Volume measures the space inside a solid. Rectangular box = length × "
                  "width × height. Cylinder = πr²h (base area × height). Volume always "
                  "multiplies three lengths, so the units are cubic."),
         "key_points": ["Box: l × w × h.",
                        "Cylinder: πr²h (base × height)."]},
        {"title": "Don't mix them up",
         "body": ("Common traps: using perimeter instead of area, forgetting the ½ for a "
                  "triangle, using r instead of r² for circles, or stopping at the base "
                  "area instead of multiplying by the height for volume."),
         "key_points": ["Perimeter ≠ area; surface area ≠ volume.",
                        "Circles use r², not r; finish volume with × height."]},
        {"title": "Try the moves",
         "body": ("A triangle with base 6 and height 8 has area ½·6·8 = 24. A cylinder "
                  "with radius 3 and height 5 has volume π·3²·5 = 45π."),
         "worked_example": "Triangle ½·6·8 = 24.  Cylinder π·3²·5 = 45π."},
    ],
    "circles": [
        {"title": "Radius, diameter, and π",
         "body": ("The radius r reaches from the center to the edge; the diameter is 2r. "
                  "Most circle formulas are written 'in terms of π' — leave π in the "
                  "answer rather than approximating."),
         "key_points": ["Diameter = 2 × radius.",
                        "Answers are often left in terms of π."]},
        {"title": "Circumference and area",
         "body": ("Circumference (the distance around) = 2πr. Area (the space inside) = "
                  "πr². The key difference: circumference uses r, area uses r². Mixing "
                  "these is the most common mistake."),
         "key_points": ["Circumference = 2πr.",
                        "Area = πr² (square the radius)."]},
        {"title": "Arcs and sectors",
         "body": ("An arc or a sector is a fraction of the whole circle — the fraction is "
                  "(central angle)/360. Arc length = (θ/360)·2πr; sector area = "
                  "(θ/360)·πr². Take the fraction of the full circumference or area."),
         "key_points": ["Fraction of the circle = θ/360.",
                        "Arc = fraction × 2πr; sector area = fraction × πr²."]},
        {"title": "Try the moves",
         "body": ("Radius 6: circumference 2π·6 = 12π, area π·6² = 36π. A 90° sector is "
                  "¼ of the circle, so its area is ¼·36π = 9π."),
         "worked_example": "C=12π, A=36π;  90° sector = ¼·36π = 9π."},
    ],
    "right_triangles": [
        {"title": "The Pythagorean theorem",
         "body": ("In a right triangle, the legs a and b and the hypotenuse c (the side "
                  "opposite the right angle) satisfy a² + b² = c². The hypotenuse is "
                  "always the longest side."),
         "key_points": ["a² + b² = c² (c is the hypotenuse).",
                        "The hypotenuse is opposite the right angle and is longest."]},
        {"title": "Finding a side",
         "body": ("To find the hypotenuse, add the squares of the legs and take the "
                  "square root. To find a leg, subtract: leg = √(c² − a²). Don't just add "
                  "or subtract the side lengths themselves."),
         "key_points": ["Hypotenuse = √(a² + b²).",
                        "Missing leg = √(c² − a²)."]},
        {"title": "Special right triangles",
         "body": ("Two come up a lot. 45-45-90: the legs are equal and the hypotenuse is "
                  "leg·√2. 30-60-90: sides are in the ratio 1 : √3 : 2 (short leg, longer "
                  "leg, hypotenuse). Memorizing these saves time."),
         "key_points": ["45-45-90: hypotenuse = leg·√2.",
                        "30-60-90: sides are x, x√3, 2x."]},
        {"title": "Try the moves",
         "body": ("Legs 3 and 4: hypotenuse √(9+16) = √25 = 5. A 45-45-90 triangle with "
                  "legs 5 has hypotenuse 5√2. A 30-60-90 with short leg 6 has longer leg "
                  "6√3 and hypotenuse 12."),
         "worked_example": "√(3²+4²)=5;  45-45-90 leg 5 -> 5√2;  30-60-90 short 6 -> 6√3."},
    ],
    "trigonometry": [
        {"title": "SOH-CAH-TOA",
         "body": ("For an acute angle θ in a right triangle: sin θ = opposite/hypotenuse, "
                  "cos θ = adjacent/hypotenuse, tan θ = opposite/adjacent. 'Opposite' and "
                  "'adjacent' are relative to the angle θ you're looking at."),
         "key_points": ["sin = opp/hyp, cos = adj/hyp, tan = opp/adj.",
                        "Opposite/adjacent depend on which angle is θ."]},
        {"title": "Identify the sides",
         "body": ("The hypotenuse is always opposite the right angle. The opposite side is "
                  "across from θ; the adjacent side touches θ (and isn't the hypotenuse). "
                  "Label them before writing a ratio."),
         "key_points": ["Hypotenuse: opposite the right angle.",
                        "Opposite: across from θ; adjacent: next to θ."]},
        {"title": "Use a ratio to find a side",
         "body": ("If you know a ratio and one side, multiply: opposite = sin θ × "
                  "hypotenuse, adjacent = cos θ × hypotenuse. You can also find a second "
                  "ratio from the first using the third side (Pythagorean theorem)."),
         "key_points": ["opposite = sin θ × hyp; adjacent = cos θ × hyp.",
                        "Get the third side, then any other ratio."]},
        {"title": "Try the moves",
         "body": ("With opposite 3, adjacent 4, hypotenuse 5: sin θ = 3/5, cos θ = 4/5, "
                  "tan θ = 3/4. If sin θ = 3/5 and the hypotenuse is 20, the opposite "
                  "side is 3/5 × 20 = 12."),
         "worked_example": "sin θ=3/5, cos θ=4/5;  opposite = 3/5 × 20 = 12."},
    ],
    "scatterplots": [
        {"title": "The line of best fit",
         "body": ("A scatterplot shows paired data; the line of best fit is the straight "
                  "line that comes closest to the points. It's written y = mx + b, and "
                  "you use it to describe the trend and to predict."),
         "key_points": ["Best-fit line summarizes the trend.",
                        "It has the form y = mx + b."]},
        {"title": "Slope and intercept",
         "body": ("The slope m is the predicted change in y for each increase of 1 in x "
                  "(the rate). The y-intercept b is the predicted y when x = 0. Read the "
                  "question to see which one it's asking you to interpret."),
         "key_points": ["Slope m = change in y per +1 in x.",
                        "Intercept b = predicted y when x = 0."]},
        {"title": "Predict with the model",
         "body": ("To predict, substitute the x-value into y = mx + b and compute. Don't "
                  "forget the +b term, and watch its sign. Predictions are estimates, not "
                  "exact data points."),
         "key_points": ["Predict: plug x into y = mx + b.",
                        "Include the intercept; mind its sign."]},
        {"title": "Try the moves",
         "body": ("For y = 3x + 5: the slope 3 means y rises about 3 for each +1 in x; the "
                  "intercept 5 is the predicted y at x = 0. At x = 4, y ≈ 3·4 + 5 = 17."),
         "worked_example": "y=3x+5: slope 3, intercept 5;  at x=4, y=17."},
    ],
}

for _skill, _screens in TEACHING_SCREENS.items():
    if _skill in TEACHING:
        TEACHING[_skill]["screens"] = _screens
