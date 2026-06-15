# Content model & pipeline

All practice content is **original, SAT-style** material with **no copyrighted
College Board questions**. Content is exam-agnostic by design, so ACT and AP can
reuse the exact same shapes later.

## Where content lives

```text
content/
├── exams/
│   └── sat/
│       ├── exam.yaml          # exam descriptor (id, name, domains, enabled, version)
│       ├── skills.yaml        # skill map: domains → sections → skills → subskills
│       ├── lessons/
│       │   ├── math/          # one JSON object per lesson
│       │   └── rw/
│       ├── questions/
│       │   ├── math/          # one JSON file per lesson = an array of questions
│       │   └── rw/
│       └── manifest.json      # lists every lesson + question file for the builder
├── schemas/
│   ├── question.schema.json   # JSON Schema (draft-07) for a question
│   └── lesson.schema.json     # JSON Schema (draft-07) for a lesson
├── prompts/                   # reusable AI content-generation prompts
└── validators/README.md       # what the validator checks
```

The canonical content under `content/exams/sat/` is the **source of truth**. The
app never loads it directly; instead `tools/build_bundle.py` compiles it into
`assets/content/sat.bundle.json`, which the app loads at runtime.

Current SAT bank: **50 lessons** and **1,003 questions** (500 Math, 503 Reading
& Writing).

## The exam descriptor — `exam.yaml`

```yaml
exam_id: sat
exam_name: "SAT"
display_name: "Digital SAT"
enabled: true            # only enabled exams are surfaced in the UI / bundle list
content_version: "1.0.0"
domains: [reading_writing, math]
difficulties: [easy, medium, hard]
question_types: [multiple_choice, student_produced, passage_reading,
                 grammar_editing, data_interpretation, multi_step_math]
```

## The skill map — `skills.yaml`

A nested tree of `exam → domains → sections → skills → subskills`. Skill ids are
stable identifiers referenced by lessons and questions; the validator checks that
every `domain`/`section`/`skill`/`subskill` used by content exists here.

```yaml
domains:
  - id: reading_writing
    name: "Reading and Writing"
    sections:
      - id: information_and_ideas
        name: "Information and Ideas"
        skills:
          - id: main_idea
            name: "Central Ideas and Main Idea"
            subskills: [central_idea, summary]
          # …
  - id: math
    sections:
      - id: algebra
        skills:
          - id: linear_equations
            subskills: [one_variable, two_variable, slope_intercept]
          # …
```

The SAT map covers Reading & Writing (Information and Ideas, Craft and Structure,
Expression of Ideas, Standard English Conventions) and Math (Algebra, Advanced
Math, Problem-Solving and Data Analysis, Geometry and Trigonometry).

## Question schema

Defined in `content/schemas/question.schema.json` (draft-07,
`additionalProperties: false`). The matching app model is `Question` in
`lib/domain/models/question.dart`.

### Required fields

| Field | Type | Notes |
| --- | --- | --- |
| `question_id` | string | Unique, pattern `^[a-z0-9]+(?:-[a-z0-9]+)*$`. Convention: `sat-<domain>-<skill>-<n>-qNN`. |
| `exam_id` | string | e.g. `"sat"`. |
| `exam_name` | string | e.g. `"SAT"`. |
| `domain` | string | Must exist in `skills.yaml`. |
| `section` | string | Must exist in `skills.yaml`. |
| `skill` | string | Must exist in `skills.yaml`. |
| `lesson_id` | string | The owning lesson; must exist. |
| `difficulty` | enum | `easy` \| `medium` \| `hard`. |
| `question_type` | enum | One of the six types below. |
| `estimated_time_seconds` | integer | 10–600. |
| `prompt` | string | The question text (min length 5). |
| `explanation` | string | Why the answer is correct (min length 10). |
| `version` | string | Semver, e.g. `"1.0.0"`. |
| `tags` | string[] | At least one tag. |

### Optional fields

| Field | Type | Notes |
| --- | --- | --- |
| `subskill` | string | Should exist in `skills.yaml` when present. |
| `stimulus` | object | Passage or table shown above the prompt (see below). |
| `choices` | object[] | 2–6 answer choices (required for MC-style types). |
| `correct_choice` | string | The id (`A`–`F`) of the correct choice (required for MC-style types). |
| `answer` | object | Numeric/string answer (required for `student_produced`). |
| `answer_verification` | string | A machine-checkable note, e.g. `"4*11+9=53"`. |

### Conditional rule

The schema enforces:

- `question_type == student_produced` → the `answer` object is **required**.
- any other type → `choices` **and** `correct_choice` are **required**.

### The `choices` array

Each choice is `{ "id": "A".."F", "text": "...", "rationale": "..." }`. The
`rationale` explains why a wrong choice is wrong (the correct choice's rationale
is typically `"Correct."`). Every choice must have a non-empty rationale.

### The `stimulus` object

```jsonc
{
  "type": "passage" | "table" | "paired_passages",
  "title": "optional title",
  "text": "passage text",          // primary passage / table intro
  "text_b": "second passage",      // only for paired_passages
  "table": {                        // only for table stimuli
    "caption": "optional",
    "headers": ["Year", "Sales"],
    "rows": [["2019", "120"], ["2020", "98"]]
  }
}
```

### The `answer` object (student-produced / grid-in)

```jsonc
{
  "type": "numeric" | "string",
  "value": 11,                 // canonical value (number or string)
  "accepted": ["11"],          // accepted textual forms (>= 1)
  "tolerance": 0.0             // numeric tolerance for "close enough"
}
```

The offline grader (`AnswerChecker` in `lib/domain/services/answer_checker.dart`)
accepts an input if it exactly matches any `accepted` string, or — for numeric
answers — parses to a value within `tolerance` of `value`/any accepted numeric
form. It understands integers, decimals, simple fractions like `3/4`, and a
trailing `%`. When `tolerance` is `0`, a small epsilon (`1e-6`) is still used so
exact decimals compare cleanly.

### Example question (multiple choice)

```jsonc
{
  "question_id": "sat-math-area-volume-1-q01",
  "exam_id": "sat", "exam_name": "SAT",
  "domain": "math", "section": "geometry_trigonometry", "skill": "area_volume",
  "subskill": "area",
  "lesson_id": "sat-math-area-volume-1",
  "difficulty": "easy", "question_type": "multiple_choice",
  "estimated_time_seconds": 70,
  "prompt": "A triangle has a base of 3 and a height of 9. What is its area?",
  "choices": [
    { "id": "A", "text": "27",   "rationale": "You forgot the factor of ½." },
    { "id": "B", "text": "12",   "rationale": "This adds the dimensions instead of using the area formula." },
    { "id": "C", "text": "6",    "rationale": "Average of the sides is not the area." },
    { "id": "D", "text": "27/2", "rationale": "Correct." }
  ],
  "correct_choice": "D",
  "explanation": "Area of a triangle = ½ × base × height = ½×3×9 = 27/2.",
  "version": "1.0.0",
  "tags": ["geometry", "area"]
}
```

### Example question (student-produced / grid-in)

```jsonc
{
  "question_id": "sat-math-linear-equations-1-q04",
  "exam_id": "sat", "exam_name": "SAT",
  "domain": "math", "section": "algebra", "skill": "linear_equations",
  "subskill": "one_variable",
  "lesson_id": "sat-math-linear-equations-1",
  "difficulty": "easy", "question_type": "student_produced",
  "estimated_time_seconds": 70,
  "prompt": "If 4x + 9 = 53, what is the value of x?",
  "answer": { "type": "numeric", "value": 11, "accepted": ["11"], "tolerance": 0.0 },
  "explanation": "Subtract 9 from both sides: 4x = 44. Divide by 4: x = 11.",
  "answer_verification": "4*11+9=53",
  "version": "1.0.0",
  "tags": ["algebra", "linear", "grid-in"]
}
```

## The six question types

| `question_type` | Answer style | Typical content |
| --- | --- | --- |
| `multiple_choice` | one correct `choice` | standard 4-option items (math or RW) |
| `student_produced` | `answer` object (grid-in) | numeric free-response math |
| `passage_reading` | one correct `choice` over a `passage`/`paired_passages` stimulus | reading comprehension, inference, evidence |
| `grammar_editing` | one correct `choice` | Standard English conventions, transitions, concision |
| `data_interpretation` | one correct `choice` over a `table` stimulus | data analysis / statistics |
| `multi_step_math` | one correct `choice` | word problems needing several steps |

All five MC-style types require exactly one `correct_choice`; only
`student_produced` uses the `answer` object. In the app, `QuestionType`
(`lib/domain/models/question.dart`) maps these strings to the renderer.

## Lesson schema

Defined in `content/schemas/lesson.schema.json`. The app model is `Lesson` in
`lib/domain/models/lesson.dart`.

| Field | Type | Notes |
| --- | --- | --- |
| `lesson_id` | string | Unique, hyphen-slug. Convention: `sat-<domain>-<skill>-<n>`. |
| `exam_id` / `exam_name` | string | `"sat"` / `"SAT"`. |
| `domain` / `section` / `skill` | string | Must exist in `skills.yaml`. |
| `title` | string | Short human title (min 3). |
| `subtitle` | string | Optional one-liner. |
| `order` | integer | ≥ 0; orders lessons within the path. |
| `difficulty` | enum | Overall lesson level. |
| `estimated_minutes` | integer | 3–30. |
| `teaching_card` | object | `{ title, body, key_points[≥2], worked_example? }`. |
| `question_ids` | string[] | 8–25 ids, in learner order; each must resolve to a real question. |
| `prerequisite_lesson_ids` | string[] | May be empty; each must reference an existing lesson. |
| `unlock_xp` | integer | ≥ 0; total XP required to unlock (`0` for first-in-path). |
| `tags` | string[] | ≥ 1. |
| `version` | string | Semver. |

The `teaching_card` is the short concept explainer shown before the questions.
`prerequisite_lesson_ids` + `unlock_xp` drive the unlock logic (see
[gamification.md](gamification.md)).

## The pipeline: generate → validate → bundle

Three Python tools live under `tools/`. Run them inside the activated env
(`source scripts/activate.sh`).

### 1. Generate — `tools/generate_content.py`

Regenerates the entire SAT bank into `content/exams/sat/` from deterministic
generators in `tools/content_gen/` (`math_gen.py`, `rw_gen.py`, `passages.py`,
`teaching.py`, `util.py`). It uses a fixed seed (`SEED = 20240614`) so output is
**reproducible**. Math answers are computed; RW conventions are rule-based;
reading items draw from an authored original-passage pool. It also writes
`manifest.json` listing every lesson and question file.

```bash
python tools/generate_content.py
```

> You usually only run this when changing the generators themselves. Hand-authored
> edits to individual JSON files are fine too — just keep them schema-valid.

### 2. Validate — `tools/validate_content.py`

Validates everything under `content/exams/sat/` against the schemas and skill
map. Exit code `0` means clean. **This runs in CI on every push and PR.** It
checks (see `content/validators/README.md` for the full list):

- JSON Schema conformance for every question and lesson (unknown fields fail).
- Unique `question_id` and `lesson_id`; duplicate question ids reported explicitly.
- Referential integrity: lesson `question_ids` resolve; each question's
  `lesson_id` exists; `domain`/`section`/`skill`/`subskill` exist in `skills.yaml`;
  `prerequisite_lesson_ids` exist.
- Exactly one valid `correct_choice` for MC-style types.
- `student_produced` items have an `answer` whose accepted numeric forms parse.
- No placeholder text (`TODO`, `TBD`, `FIXME`, `lorem`, `xxx`, etc.).
- `version` present and valid for questions, lessons, and the exam.

```bash
python tools/validate_content.py
python tools/validate_content.py --exam sat   # explicit exam
```

### 3. Bundle — `tools/build_bundle.py`

Reads the manifest + lessons + questions + `exam.yaml` + `skills.yaml` and writes
a single minified JSON bundle per exam to `assets/content/<exam>.bundle.json`,
plus `assets/content/exams.json` listing enabled exams. Lessons are sorted
(Reading & Writing first, then Math, by `order`) so the app's path is stable.

```bash
python tools/build_bundle.py
```

The bundle has the shape `{ schema_version, exam, skills, lessons[], questions[] }`
and is what `ContentRepository` loads at runtime. **CI rebuilds the bundle and
fails if the committed `assets/content/` is stale**, so always run this and
commit the result after content changes.

## Content-generation prompts

`content/prompts/` holds reusable, explicit prompts so future AI agents can
extend the bank safely and consistently. Each one specifies strict output rules
(original content only, schema-exact, one correct answer, wrong-answer
rationales, accurate difficulty, estimated time, skill metadata, answer
verification).

| Prompt file | Use |
| --- | --- |
| `generate_sat_lesson.md` | Create one new SAT lesson object. |
| `generate_sat_math_questions.md` | Generate a set of SAT Math questions. |
| `generate_sat_rw_questions.md` | Generate a set of SAT Reading/Writing questions. |
| `expand_question_bank.md` | Expand an existing skill area with more items. |
| `review_question_quality.md` | Audit generated questions for quality/ambiguity. |
| `verify_math_questions.md` | Check math answer correctness. |
| `verify_rw_questions.md` | Check grammar/reading question correctness. |
| `convert_to_schema.md` | Convert drafted content into schema-exact JSON/YAML. |

See [content-authoring.md](content-authoring.md) for the end-to-end authoring
workflow.
