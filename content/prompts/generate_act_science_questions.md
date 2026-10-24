# Prompt: Generate ACT Science Question Sets

You are generating ORIGINAL ACT Science questions for an offline Flutter test-prep app.
Output a JSON ARRAY of question objects, each conforming EXACTLY to
`content/schemas/question.schema.json`. These questions belong to one lesson.

ACT Science tests reasoning over data, not memorised facts. Every item hangs off a
**single stimulus** (the schema allows one per question):

- `stimulus.type: "table"` — `{caption, headers, rows}` with real numbers. Put the method
  description (what was varied, what was measured, what was held constant) in `caption`
  or in a `passage` stimulus; never both on one item.
- `stimulus.type: "passage"` — a short research-summary (Experiment 1 / Experiment 2…)
  with results stated inline.
- `stimulus.type: "paired_passages"` — `text` = Scientist 1, `text_b` = Scientist 2
  (90–160 words each) for conflicting-viewpoint items.
- `stimulus.type: "figure"` with `figure.kind: "scatter"` (`points`, `xlabel`, optional
  `line`) for graph reading.

## Skills (ids from `content/exams/act/skills.yaml`, domain `science`)
- `data_representation` (section `interpretation_of_data`): lookup, direction of change,
  greatest/least, difference/ratio, which statement the table supports, graph reads.
- `trends_extrapolation` (section `interpretation_of_data`): trend shape, interpolation
  ("closest to"), extrapolation beyond the table, "as x doubles…", series crossings.
- `experimental_design` (section `scientific_investigation`): independent / dependent /
  controlled variables, why a control was used, what changed between experiments, which
  design change tests a new hypothesis, which hypothesis the results support, predictions.
- `conflicting_viewpoints` (section `evaluation_of_models`): what each scientist would
  agree/disagree with, common ground, which finding supports Scientist 2, how a new
  observation affects each view, the main difference between the views.

Use the subskill ids listed under each skill in skills.yaml.

## Rules
- `exam_id: "act"`, `exam_name: "ACT"`, `domain: "science"`, 4 choices `A`–`D`.
- `question_type`: `data_interpretation` for table items, `passage_reading` for passage /
  paired-passage items, `multiple_choice` for figure items.
- Data must be computed from a described relationship so the key is provably right; put
  the check in `answer_verification` (e.g. `"science:interpolate;x=35;y=12.4"`).
- Exactly one defensible answer. Distractors are specific errors (wrong column, reversed
  trend, off-by-one row, extrapolating the wrong way) and each carries a `rationale`.
- Vary prompt phrasing and question forms; the correct answer must not be systematically
  the longest option or sit in one position.
- Difficulty: easy = direct lookup/identification; medium = comparison, interpolation,
  variable identification; hard = extrapolation, multi-table reasoning, design changes,
  subtle viewpoint reasoning.
- Original content only. No copyrighted ACT, Inc. material.

Generated items carry a `family:<name>` tag naming the question form; hand-written
items should add one too (e.g. `family:cv_common_ground`) so the validator can check
that a lesson mixes at least three forms.
