# Prompt: Generate ACT English Question Sets

You are generating ORIGINAL ACT English questions for an offline Flutter test-prep app.
Output a JSON ARRAY of question objects, each conforming EXACTLY to
`content/schemas/question.schema.json`. These questions belong to one lesson.

## Format: the bracketed portion + NO CHANGE
ACT English items present a passage with an underlined portion. In this app the
portion is shown in **square brackets** inside the prompt, followed by a blank line and
a short stem, and choice **A is always `NO CHANGE`**:

```
The box of old photographs, in most years, [include] a detailed summary.

Which choice is the best version of the bracketed portion? (Choose NO CHANGE if it is best as written.)
```

- About a quarter of the time the bracketed wording is already correct (NO CHANGE is
  the key); otherwise the key sits among `B`–`D`.
- `question_type: "grammar_editing"` for conventions items; `multiple_choice` for
  rhetorical items (transitions, writer's goal, concision) whose choices are not
  alternatives for a bracketed portion.
- Tag NO CHANGE items `act-no-change`.

(The generator pipeline produces these automatically from blank-filling families —
`exam_plans.act_no_change` — so hand-written items must follow the same shape.)

## Skills (ids from `content/exams/act/skills.yaml`, domain `english`)
- Conventions of Standard English: `sentence_boundaries`, `subject_verb_agreement`,
  `punctuation`, `pronouns`, `modifiers`, `verb_tense`, `parallel_structure`,
  `pronoun_antecedent`.
- Production of Writing: `transitions`, `rhetorical_synthesis` (writer's goal /
  organisation).
- Knowledge of Language: `concision`, `usage_idioms` (commonly confused words,
  idiomatic prepositions, comparatives, precise word choice).

## Rules
- `exam_id: "act"`, `exam_name: "ACT"`, `domain: "english"`, 4 choices.
- Vary the sentence frames, the position of the bracketed portion and the amount of
  context (single sentence vs. a 2–3 sentence mini-passage); never reuse one frame
  across a lesson. Add a `family:<form>` tag naming the question form.
- One and only one correct answer; each distractor is a specific error with a
  `rationale`; the correct answer must not be identifiable by length, position or by
  always starting with the same word.
- Original sentences only. No copyrighted ACT, Inc. material.
