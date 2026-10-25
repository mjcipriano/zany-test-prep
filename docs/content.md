# Content model & pipeline

All practice content is **original, SAT- and ACT-style** material with **no
copyrighted College Board or ACT, Inc. questions**. Content is exam-agnostic by
design: the SAT and ACT share the same schemas, and AP can reuse them later.

## Where content lives

```text
content/
├── exams/
│   ├── sat/
│   │   ├── exam.yaml          # exam descriptor (id, names, domains, timed_test, scoring)
│   │   ├── skills.yaml        # skill map: domains → sections → skills → subskills
│   │   ├── lessons/{rw,math}/ # one JSON object per lesson
│   │   ├── questions/{rw,math}/        # one JSON file per lesson = an array of questions
│   │   ├── questions/bank/{rw,math}/   # practice-bank items (not bound to a lesson)
│   │   └── manifest.json      # lists every lesson + question file for the builder
│   └── act/                   # same layout; domains english/math/reading/science
├── schemas/
│   ├── question.schema.json   # JSON Schema (draft-07) for a question
│   └── lesson.schema.json     # JSON Schema (draft-07) for a lesson
├── prompts/                   # reusable AI content-generation prompts
└── validators/README.md       # what the validator checks
```

The canonical content under `content/exams/<exam>/` is the **source of truth**. The
app never loads it directly; instead `tools/build_bundle.py` compiles each exam into
`assets/content/<exam>.bundle.json` and writes `assets/content/exams.json` (the list
of shipped exams with display names), which the app loads at runtime.

See the README for the current lesson/question counts per exam.

## The exam descriptor — `exam.yaml`

```yaml
exam_id: sat
exam_name: "SAT"
display_name: "Digital SAT"
tagline: "Reading, Writing & Math"   # shown in the exam picker
enabled: true            # only enabled exams are surfaced in the UI / bundle list
content_version: "2.1.0"  # bumped whenever content changes; build_bundle.py enforces it
domains: [reading_writing, math]
difficulties: [easy, medium, hard]
question_types: [multiple_choice, student_produced, passage_reading,
                 grammar_editing, data_interpretation, multi_step_math]
# Full-length practice test layout (app: Practice Test).
timed_test:
  intro: "This mirrors the Digital SAT: ..."
  modules:
    - { name: "Reading & Writing — Module 1", domain: reading_writing, count: 27, minutes: 32 }
    # ...
# Score scale: sat_1600 (200-800 per section, summed), act_36 (1-36 per
# section, composite = rounded mean of composite_domains) or percent.
scoring:
  type: sat_1600
  composite_label: "Estimated total score"
```

The ACT descriptor uses four domains (`english`, `math`, `reading`, `science`), one
timed module per section (50/45/36/40 questions in 35/50/40/40 minutes) and
`scoring: {type: act_36, composite_domains: [english, math, reading]}` — Science is
scored but, as on the enhanced ACT, not part of the composite.

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
| `tags` | string[] | At least one tag. Generated items also carry `family:<name>` (the question form that produced them; used by the validator's variety check) and, for ACT English, `act-no-change`. |

### Optional fields

| Field | Type | Notes |
| --- | --- | --- |
| `subskill` | string | Should exist in `skills.yaml` when present. |
| `stimulus` | object | Passage or table shown above the prompt (see below). |
| `choices` | object[] | 2–6 answer choices (required for MC-style types). SAT items use 4 (`A`–`D`); ACT Math items use 5 (`A`–`E`). |
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

Regenerates every exam's bank into `content/exams/<exam>/` by walking the exam's
plan (`tools/content_gen/exam_plans.py`) over the question **families** registered
by the generator modules in `tools/content_gen/` (see
[content-authoring.md](content-authoring.md) for the family contract). Each plan
has a fixed seed so output is **reproducible**. Math and science answers are
computed; conventions are rule-based; reading items draw from an authored
original-passage pool. It also writes each exam's `manifest.json`.

```bash
python tools/generate_content.py              # all exams
python tools/generate_content.py --exam act   # one exam
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
python tools/validate_content.py              # every exam
python tools/validate_content.py --exam act   # one exam
```

It also enforces per-lesson **variety** (≥ 3 question families per generated lesson,
none above 50%) and cross-checks `exam.yaml`'s domains and timed-test modules against
`skills.yaml`.

### 3. Bundle — `tools/build_bundle.py`

Reads the manifest + lessons + questions + `exam.yaml` + `skills.yaml` and writes
a single minified JSON bundle per exam to `assets/content/<exam>.bundle.json`,
plus `assets/content/exams.json` describing the enabled exams (`id`, `name`,
`display_name`, `tagline`). Lessons are sorted by the exam's domain order (as
listed in `skills.yaml`), then by `order`, so the app's path is stable.

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
| `generate_act_math_questions.md` | ACT Math (5 choices, no grid-ins, ACT skill map). |
| `generate_act_english_questions.md` | ACT English in the bracketed-portion / NO CHANGE format. |
| `generate_act_science_questions.md` | ACT Science (data, research summaries, conflicting viewpoints). |

See [content-authoring.md](content-authoring.md) for the end-to-end authoring
workflow.
