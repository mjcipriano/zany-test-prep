# Prompt: Expand an Existing Question Bank

You are ADDING questions to an existing SAT skill area without breaking what is already
there. Output a JSON ARRAY of NEW question objects conforming EXACTLY to
`content/schemas/question.schema.json`. Follow `generate_sat_math_questions.md` or
`generate_sat_rw_questions.md` for per-question rules; this file covers the EXPANSION rules.

## Before you generate
1. Read the existing question file(s) for the target skill under
   `content/exams/sat/questions/<domain>/`.
2. Read the owning lesson under `content/exams/sat/lessons/<domain>/` to see the current
   `question_ids` and difficulty mix.
3. Note every `question_id` already used and the prompts already covered.

## Keep IDs unique
- `question_id` pattern: `^[a-z0-9]+(?:-[a-z0-9]+)*$`.
- Continue the existing numbering scheme. If the file ends at `...-q20`, new items start at
  `...-q21`. Never reuse or renumber existing ids (validation fails on duplicates and on
  lessons referencing missing ids).
- If you add the new questions to a lesson, append their ids to that lesson's
  `question_ids` (count must stay within 8-25) and bump the lesson `version` patch number.

## Avoid near-duplicate prompts
- Do not restate an existing prompt with only the numbers swapped if that pattern is
  already well represented. Vary surface form, scenario context, and the specific
  sub-concept (different subskill values where applicable).
- Vary the position of the correct choice across A-D; do not let one letter dominate.
- For math, vary the numbers AND the structure (e.g. solve-for-x vs. interpret-slope vs.
  word problem) so the bank tests the skill, not one template.

## Maintain difficulty balance
- Check the current easy/medium/hard counts and add items that move the mix toward a
  healthy spread (roughly 50% easy, 30% medium, 20% hard unless the skill warrants more
  hard items). State the resulting counts in your summary.

## OUTPUT REQUIREMENTS
- Output ONLY the new question objects as a JSON ARRAY. No unknown fields. No fences.
- All NEW `question_id`s are globally unique and do not collide with existing ids.
- Original content only; no copyrighted or official College Board items.
- Each item meets full per-question requirements: one correct answer for MC, machine-
  checkable `answer` for `student_produced`, rationale for every choice, `explanation`
  matching the key, accurate `difficulty`, `estimated_time_seconds`, `skill`/`subskill`,
  and `answer_verification` for math.
- No near-duplicates of existing prompts; no ambiguous or multiple-correct items.

## OUTPUT FORMAT (minimal valid example — new items only)
```json
[
  {
    "question_id": "sat-math-area-volume-1-q21",
    "exam_id": "sat",
    "exam_name": "SAT",
    "domain": "math",
    "section": "geometry_trigonometry",
    "skill": "area_volume",
    "subskill": "volume",
    "lesson_id": "sat-math-area-volume-1",
    "difficulty": "hard",
    "question_type": "multiple_choice",
    "estimated_time_seconds": 100,
    "prompt": "A box measures 3 by 4 by 5. What is its volume?",
    "choices": [
      { "id": "A", "text": "12", "rationale": "This is one face area, not the volume." },
      { "id": "B", "text": "60", "rationale": "Correct." },
      { "id": "C", "text": "47", "rationale": "This is the surface area." },
      { "id": "D", "text": "24", "rationale": "This sums the edges." }
    ],
    "correct_choice": "B",
    "explanation": "Volume = l*w*h = 3*4*5 = 60.",
    "answer_verification": "volume=60",
    "tags": ["geometry", "volume"],
    "version": "1.0.0"
  }
]
```
