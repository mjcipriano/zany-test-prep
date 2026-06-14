# Prompt: Convert Drafted Content into Schema JSON

You are CONVERTING drafted SAT content (loose notes, prose, or a rough draft) into valid
JSON that conforms EXACTLY to `content/schemas/question.schema.json` (questions) and
`content/schemas/lesson.schema.json` (lessons). Both schemas set `additionalProperties:
false`, so output NO fields beyond those defined.

## ID format rules (both schemas)
- `question_id` and `lesson_id` pattern: `^[a-z0-9]+(?:-[a-z0-9]+)*$`
  (lowercase letters, digits, and single hyphens only; no spaces, underscores, capitals,
  leading/trailing/double hyphens).
  Convention: `sat-<domain-short>-<skill>-<n>` for lessons; append `-qNN` for questions,
  e.g. lesson `sat-math-linear-equations-1`, question `sat-math-linear-equations-1-q03`.
- `version` pattern: `^[0-9]+\.[0-9]+\.[0-9]+$`, e.g. `"1.0.0"`.
- choice `id` pattern: `^[A-F]$`. `correct_choice` pattern: `^[A-F]$`.

## Field-by-field mapping — QUESTION
Required: `question_id`, `exam_id` (`"sat"`), `exam_name` (`"SAT"`), `domain`
(`reading_writing`|`math`), `section`, `skill`, `lesson_id`, `difficulty`
(`easy|medium|hard`), `question_type` (one of `multiple_choice`, `student_produced`,
`passage_reading`, `grammar_editing`, `data_interpretation`, `multi_step_math`),
`estimated_time_seconds` (int 10-600), `prompt` (>=5 chars), `explanation` (>=10 chars),
`version`, `tags` (>=1 string).
Optional: `subskill`, `stimulus`, `choices`, `correct_choice`, `answer`,
`answer_verification`.
Conditional (schema `allOf`): if `question_type` == `student_produced`, include `answer`
(no `choices`/`correct_choice`); otherwise include `choices` (2-6 items, each with `id`,
`text`, `rationale`) AND `correct_choice`.
- `stimulus`: `{ type: passage|table|paired_passages, title?, text?, text_b?, table? }`.
  `table` = `{ caption?, headers[>=1], rows[>=1 of string arrays] }`.
- `answer`: `{ type: numeric|string, value?, accepted[>=1 strings], tolerance?>=0 }`.

## Field-by-field mapping — LESSON
Required: `lesson_id`, `exam_id`, `exam_name`, `domain`, `section`, `skill`, `title`
(>=3), `order` (int >=0), `difficulty`, `estimated_minutes` (int 3-30), `teaching_card`,
`question_ids` (8-25 strings), `prerequisite_lesson_ids` (array, may be `[]`), `unlock_xp`
(int >=0), `tags` (>=1), `version`.
Optional: `subtitle`.
- `teaching_card`: required `title` (>=3), `body` (>=30 chars), `key_points` (>=2 strings);
  optional `worked_example`.

## Conversion steps
1. Pick `domain`/`section`/`skill` ids from `content/exams/sat/skills.yaml` (must be real).
2. Assign ids following the rules above; verify uniqueness against existing content.
3. Map each draft element to its exact field; convert difficulty words to the enum;
   convert any rationale notes into a `rationale` per choice.
4. For numeric answers, populate `answer.accepted` with all equivalent forms and set
   `tolerance` for decimals.
5. Drop anything that has no schema home (do NOT invent fields). Keep math symbols as plain
   text (e.g. `1/2`, `x^2`) for offline rendering.
6. Set `question_ids` in the lesson to match the converted questions exactly.

## OUTPUT REQUIREMENTS
- Output valid JSON only: a single lesson OBJECT, or a question ARRAY. No markdown fences,
  no comments, no trailing commas, no unknown fields.
- Preserve original content; convert only structure. No copyrighted/official items.
- Result must pass `python tools/validate_content.py` (see content/validators/README.md):
  schema-valid, unique ids, referential integrity, one correct answer for MC, parseable
  numeric answers, no placeholder text.

## OUTPUT FORMAT (minimal valid question example)
```json
[
  {
    "question_id": "sat-math-linear-equations-1-q01",
    "exam_id": "sat",
    "exam_name": "SAT",
    "domain": "math",
    "section": "algebra",
    "skill": "linear_equations",
    "subskill": "one_variable",
    "lesson_id": "sat-math-linear-equations-1",
    "difficulty": "easy",
    "question_type": "multiple_choice",
    "estimated_time_seconds": 60,
    "prompt": "If x + 4 = 9, what is x?",
    "choices": [
      { "id": "A", "text": "5", "rationale": "Correct: 9 - 4 = 5." },
      { "id": "B", "text": "13", "rationale": "This adds instead of subtracting." },
      { "id": "C", "text": "4", "rationale": "This is the constant, not x." },
      { "id": "D", "text": "36", "rationale": "This multiplies instead of subtracting." }
    ],
    "correct_choice": "A",
    "explanation": "Subtract 4 from both sides: x = 9 - 4 = 5.",
    "answer_verification": "x=5; check 5+4=9",
    "tags": ["algebra", "linear"],
    "version": "1.0.0"
  }
]
```
