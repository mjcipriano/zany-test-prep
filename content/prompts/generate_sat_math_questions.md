# Prompt: Generate SAT Math Question Sets

You are generating ORIGINAL SAT Math questions for an offline Flutter test-prep app.
Output a JSON ARRAY of question objects, each conforming EXACTLY to
`content/schemas/question.schema.json`. These questions belong to one lesson.

## Question types you may use (from the schema enum)
- `multiple_choice`: single-answer MC; uses `choices` + `correct_choice`.
- `student_produced`: grid-in numeric entry; uses the `answer` object (NO choices).
- `data_interpretation`: question keyed to a `stimulus` of type `table` (uses `choices`).
- `multi_step_math`: multi-step problem (MC form: uses `choices` + `correct_choice`).

Schema rule (`allOf`): if `question_type` is `student_produced`, `answer` is REQUIRED and
`choices`/`correct_choice` are not used. For ALL OTHER types, `choices` AND
`correct_choice` are REQUIRED.

## Skills to cover (use real ids from skills.yaml)
Algebra: `linear_equations`, `linear_inequalities`, `systems_of_equations`.
Advanced Math: `functions`, `quadratics`, `exponents_radicals`, `polynomials`.
Problem-Solving & Data: `ratios_percentages_units`, `proportions`, `data_analysis`,
`statistics`, `probability`.
Geometry & Trig: `area_volume`, `circles`, `right_triangles`, `trigonometry`.

## Required fields per question
- `question_id`: pattern `^[a-z0-9]+(?:-[a-z0-9]+)*$`, e.g. `sat-math-linear-equations-1-q01`.
- `exam_id`: `"sat"`, `exam_name`: `"SAT"`, `domain`: `"math"`.
- `section`, `skill`, optional `subskill`: real ids from skills.yaml.
- `lesson_id`, `difficulty` (`easy|medium|hard`), `question_type`.
- `estimated_time_seconds`: integer 10-600 (math items typically 50-120).
- `prompt` (min 5 chars), `explanation` (min 10 chars), `tags` (>=1), `version` `"1.0.0"`.
- `answer_verification` (string): SHOW the recomputed answer / key relation here for every
  math item, e.g. `"x=3; check 2*3+1=7"`. Required-by-policy for math even though the
  schema marks it optional.

## Machine-checkable numeric answers (`student_produced`)
Provide an `answer` object: `additionalProperties` false, required `type` and `accepted`.
- `type`: `"numeric"` (or `"string"` for non-numeric grid-ins, rare).
- `value` (optional): the canonical number or string.
- `accepted`: array (>= 1) of accepted string forms the grader will match, e.g.
  `["2.5", "5/2"]`. Include every equivalent form a learner could legitimately enter.
- `tolerance` (optional, >= 0): numeric tolerance for decimals, e.g. `0.01`. Use a real
  tolerance for irrational/rounded answers; omit or `0` for exact integers/fractions.
Ensure the answer is reachable within the SAT grid-in format (no negatives if the skill
forbids them, value fits the grid).

## OUTPUT REQUIREMENTS
- Output a JSON ARRAY of question objects. No unknown fields. No markdown fences.
- Original problems only. No copyrighted or official College Board items.
- For MC/data/multi-step: exactly ONE correct choice; every distractor is genuinely wrong
  with a rationale that names the likely mistake. `correct_choice` matches `explanation`.
- For `student_produced`: the `answer` object must be machine-checkable; `accepted` covers
  all equivalent forms; `tolerance` set when decimals are involved.
- Recompute every answer and record it in `answer_verification`.
- Accurate `difficulty`; include `estimated_time_seconds`, `skill`, `subskill`.
- For `data_interpretation`, include a `stimulus` of type `table` with `headers` and
  `rows`; the question must be answerable from that table.
- Avoid ambiguity and multiple-correct answers. Avoid trick questions unless they teach a
  real concept. Keep style similar to standardized tests without copying real items.

## OUTPUT FORMAT (minimal valid examples)
```json
[
  {
    "question_id": "sat-math-area-volume-1-q01",
    "exam_id": "sat",
    "exam_name": "SAT",
    "domain": "math",
    "section": "geometry_trigonometry",
    "skill": "area_volume",
    "subskill": "area",
    "lesson_id": "sat-math-area-volume-1",
    "difficulty": "easy",
    "question_type": "multiple_choice",
    "estimated_time_seconds": 70,
    "prompt": "A triangle has a base of 11 and a height of 5. What is its area?",
    "choices": [
      { "id": "A", "text": "55", "rationale": "You forgot the factor of 1/2." },
      { "id": "B", "text": "8", "rationale": "Averaging the sides is not the area." },
      { "id": "C", "text": "55/2", "rationale": "Correct." },
      { "id": "D", "text": "16", "rationale": "This adds the dimensions." }
    ],
    "correct_choice": "C",
    "explanation": "Area = 1/2 * base * height = 1/2*11*5 = 55/2.",
    "answer_verification": "area=55/2",
    "tags": ["geometry", "area"],
    "version": "1.0.0"
  },
  {
    "question_id": "sat-math-linear-equations-1-q07",
    "exam_id": "sat",
    "exam_name": "SAT",
    "domain": "math",
    "section": "algebra",
    "skill": "linear_equations",
    "subskill": "one_variable",
    "lesson_id": "sat-math-linear-equations-1",
    "difficulty": "medium",
    "question_type": "student_produced",
    "estimated_time_seconds": 90,
    "prompt": "If 2x + 1 = 7, what is the value of x?",
    "answer": { "type": "numeric", "value": 3, "accepted": ["3"], "tolerance": 0 },
    "explanation": "Subtract 1 then divide by 2: x = (7-1)/2 = 3.",
    "answer_verification": "x=3; check 2*3+1=7",
    "tags": ["algebra", "linear"],
    "version": "1.0.0"
  }
]
```
