# Content Validation

All SAT content (lessons and questions) is checked by an automated validator before it can
be merged. Authors and content-generating agents MUST run it locally and get a clean pass
before committing.

## How to run

```bash
python tools/validate_content.py
```

The same command runs in CI on every pull request. A non-zero exit code fails the build,
so a green local run is required before you commit or open a PR.

## What it checks

The validator inspects everything under `content/exams/sat/` against the schemas in
`content/schemas/` and the skill map in `content/exams/sat/skills.yaml`:

1. Schema conformance — every question validates against
   `content/schemas/question.schema.json` and every lesson against
   `content/schemas/lesson.schema.json` (including `additionalProperties: false`, so
   unknown fields fail).
2. Unique ids — every `question_id` is unique across the whole content set, and every
   `lesson_id` is unique. Duplicate question ids are reported explicitly.
3. Referential integrity — every id in a lesson's `question_ids` resolves to a real
   question; each question's `lesson_id` points to an existing lesson; and each
   `domain`/`section`/`skill` (and `subskill`, when present) exists in `skills.yaml`.
4. One correct answer for MC — for `multiple_choice`, `passage_reading`,
   `grammar_editing`, `data_interpretation`, and `multi_step_math`, exactly one
   `correct_choice` is set and it matches an existing choice `id`.
5. Numeric answer parsing — for `student_produced`, the `answer` object is present and
   every entry in `answer.accepted` parses as a number (when `answer.type` is `numeric`),
   so the offline grader can check learner input.
6. No placeholder text — rejects leftover drafting markers such as `TODO`, `TBD`,
   `FIXME`, `lorem`, `xxx`, or empty/whitespace-only required strings in prompts,
   choices, rationales, explanations, and teaching-card fields.
7. No duplicate question ids — flagged separately from the general uniqueness check so the
   offending ids are easy to find.
8. Version present — every question and lesson has a valid `version`
   (`^[0-9]+\.[0-9]+\.[0-9]+$`), and the exam version is present in `skills.yaml`.
9. Prerequisite lessons exist — every id in a lesson's `prerequisite_lesson_ids` refers to
   a lesson that actually exists.

## Before you commit

1. Generate or edit content following the prompts in `content/prompts/`.
2. Run `python tools/validate_content.py`.
3. Fix every reported error (the validator prints the file, id, and reason).
4. Re-run until it passes with no errors, then commit.

If you add a new question, remember to add its `question_id` to the owning lesson's
`question_ids` (keeping the count between 8 and 25) so referential integrity stays intact.
