# Prompt: Generate SAT Reading & Writing Question Sets

You are generating ORIGINAL SAT Reading and Writing (RW) questions for an offline Flutter
test-prep app. Output a JSON ARRAY of question objects, each conforming EXACTLY to
`content/schemas/question.schema.json`. These questions belong to one lesson.

## Question types you may use (from the schema enum)
- `passage_reading`: comprehension/inference/evidence questions tied to a passage.
- `grammar_editing`: Standard English Conventions edits (a sentence/short passage with a
  blank or underlined span to fix).
- `multiple_choice`: generic single-answer item when neither label above fits.
All three use `choices` + `correct_choice` (NOT the `answer` object).

## Skills to cover (use real ids from skills.yaml)
Information & Ideas: `main_idea`, `inferences`, `command_of_evidence`.
Craft & Structure: `words_in_context`, `text_structure_purpose`, `cross_text_connections`.
Expression of Ideas: `transitions`, `rhetorical_synthesis`, `concision`.
Standard English Conventions: `sentence_boundaries`, `subject_verb_agreement`,
`punctuation`, `pronouns`, `modifiers`.

## Required fields per question (question.schema.json)
- `question_id`: pattern `^[a-z0-9]+(?:-[a-z0-9]+)*$`, e.g. `sat-rw-main-idea-1-q01`.
- `exam_id`: `"sat"`, `exam_name`: `"SAT"`.
- `domain`: `"reading_writing"`. `section`: the section id. `skill`: the skill id.
- `subskill` (optional but recommended): a subskill id from skills.yaml.
- `lesson_id`: the owning lesson id.
- `difficulty`: `easy` | `medium` | `hard`.
- `question_type`: one of the three above.
- `estimated_time_seconds`: integer 10-600 (RW reading items typically 60-100).
- `prompt`: the question stem (min 5 chars).
- `choices`: 2-6 objects, each `{ "id": "A".."F", "text": "...", "rationale": "..." }`.
  Provide a rationale for EVERY choice (correct one says why it is right; each distractor
  says why it is wrong). Typically use 4 choices A-D.
- `correct_choice`: the single correct choice id (`^[A-F]$`).
- `explanation`: min 10 chars; must directly support the keyed correct answer.
- `tags`: >= 1 string.
- `version`: `"1.0.0"` style.
- `stimulus` (use whenever a passage/context is needed): object with
  `type` in {`passage`, `table`, `paired_passages`}, plus `title`/`text`, and `text_b`
  for paired passages. For `cross_text_connections`, use `paired_passages` with `text`
  and `text_b`. Embed the relevant sentence/passage context the question depends on.

## OUTPUT REQUIREMENTS
- Output a JSON ARRAY of question objects. No extra/unknown fields
  (`additionalProperties` is false). No markdown fences.
- Original passages and sentences only. No copyrighted or official College Board text.
- Exactly ONE defensible correct answer per item; the other choices must be clearly wrong.
- The `explanation` must support the SAME choice given in `correct_choice`.
- Every choice has a non-empty `rationale`.
- Include the passage/sentence context the question relies on (in `stimulus` or `prompt`).
  A reader must be able to answer from the provided text alone.
- Accurate `difficulty`; include `estimated_time_seconds`, `skill`, and `subskill`.
- Avoid ambiguity and multiple-correct-answer traps. Avoid trick questions unless they
  teach a real RW concept. Keep style similar to standardized tests without copying items.

## OUTPUT FORMAT (minimal valid example)
```json
[
  {
    "question_id": "sat-rw-command-of-evidence-1-q01",
    "exam_id": "sat",
    "exam_name": "SAT",
    "domain": "reading_writing",
    "section": "information_and_ideas",
    "skill": "command_of_evidence",
    "subskill": "textual_evidence",
    "lesson_id": "sat-rw-command-of-evidence-1",
    "difficulty": "medium",
    "question_type": "passage_reading",
    "estimated_time_seconds": 80,
    "prompt": "Which detail best supports the claim that the cold preserves the seeds?",
    "stimulus": {
      "type": "passage",
      "title": "A Vault for Seeds",
      "text": "Inside a frozen mountain, a vault holds seeds. The cold slows their aging, so even after decades they can still sprout."
    },
    "choices": [
      { "id": "A", "text": "Even after decades, the seeds can still sprout.", "rationale": "Correct. Sprouting after decades shows preserved viability." },
      { "id": "B", "text": "The vault is built inside a mountain.", "rationale": "Location alone does not show preserved viability." },
      { "id": "C", "text": "The seeds come from around the world.", "rationale": "Origin does not address viability." },
      { "id": "D", "text": "The vault is a backup.", "rationale": "States purpose, not preservation." }
    ],
    "correct_choice": "A",
    "explanation": "Preserved viability is shown by the seeds sprouting after decades.",
    "tags": ["reading", "evidence"],
    "version": "1.0.0"
  }
]
```
