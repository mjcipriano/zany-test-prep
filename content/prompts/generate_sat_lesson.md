# Prompt: Generate a New SAT Lesson

You are generating ONE original SAT lesson object for an offline Flutter test-prep app.
The lesson is a short, Duolingo-style challenge: one teaching card followed by 8-25 linked
questions. Output must conform EXACTLY to `content/schemas/lesson.schema.json`.

## Inputs you need
- `domain`: `reading_writing` or `math` (matches `content/exams/sat/skills.yaml`).
- `section`: the section id for the chosen domain (e.g. `geometry_trigonometry`, `algebra`,
  `information_and_ideas`, `standard_english_conventions`).
- `skill`: a skill id under that section (e.g. `area_volume`, `linear_equations`, `main_idea`).
- `order`: integer >= 0 used for ordering lessons within the skill path.

## Required fields (from lesson.schema.json)
- `lesson_id`: lowercase letters/digits/hyphens only, pattern `^[a-z0-9]+(?:-[a-z0-9]+)*$`.
  Convention: `sat-<domain-short>-<skill>-<n>`, e.g. `sat-math-area-volume-1`,
  `sat-rw-main-idea-1`.
- `exam_id`: `"sat"`. `exam_name`: `"SAT"`.
- `domain`, `section`, `skill`: must be real ids from `skills.yaml`.
- `title`: short human title (min 3 chars), e.g. `"Area & Volume"`.
- `subtitle` (optional): one short clarifying line.
- `order`: integer >= 0.
- `difficulty`: one of `easy`, `medium`, `hard` (overall lesson level).
- `estimated_minutes`: integer 3-30. Roughly sum of question times / 60, rounded.
- `teaching_card`: object with:
  - `title` (min 3 chars),
  - `body` (min 30 chars; plain teaching prose, no markdown headers),
  - `key_points`: array of >= 2 short strings,
  - `worked_example` (optional but recommended): one solved example.
- `question_ids`: array of 8-25 strings. These MUST be the `question_id`s of the
  questions generated for this lesson, in the order learners should see them.
- `prerequisite_lesson_ids`: array (may be empty `[]`) of existing lesson ids.
- `unlock_xp`: integer >= 0 (XP required to unlock; `0` for the first lesson in a path).
- `tags`: array with >= 1 string (e.g. `["math","area_volume"]`).
- `version`: semantic version string, pattern `^[0-9]+\.[0-9]+\.[0-9]+$`, start at `"1.0.0"`.

## Difficulty progression
Order `question_ids` so the linked questions progress roughly easy -> medium -> hard.
A typical 20-question lesson is ~10 easy, ~6 medium, ~4 hard. The lesson-level
`difficulty` reflects the overall target audience, not the single hardest item.

## OUTPUT REQUIREMENTS
- Output a SINGLE JSON object (the lesson) conforming exactly to lesson.schema.json.
  No extra/unknown fields (`additionalProperties` is false). No markdown fences.
- Original content only. No copyrighted or official College Board items.
- `question_ids` must exactly match the ids of the questions you generate (referential
  integrity is validated). Count must be 8-25.
- `domain`/`section`/`skill` must exist in `skills.yaml`.
- `prerequisite_lesson_ids` must reference lessons that exist (or be empty).
- Keep teaching-card style similar to standardized-test instruction without copying real
  items. Avoid trick framing unless it teaches a real concept.

## OUTPUT FORMAT (minimal valid example)
```json
{
  "lesson_id": "sat-math-area-volume-1",
  "exam_id": "sat",
  "exam_name": "SAT",
  "domain": "math",
  "section": "geometry_trigonometry",
  "skill": "area_volume",
  "title": "Area & Volume",
  "order": 20,
  "difficulty": "easy",
  "estimated_minutes": 23,
  "teaching_card": {
    "title": "Area and Volume",
    "body": "Area measures a flat region; volume measures the space inside a solid. Rectangle area = base x height; triangle area = 1/2 x base x height.",
    "key_points": ["Rectangle area = b*h.", "Triangle area = 1/2*b*h."],
    "worked_example": "A 4x5 rectangle has area 20."
  },
  "question_ids": [
    "sat-math-area-volume-1-q01",
    "sat-math-area-volume-1-q02",
    "sat-math-area-volume-1-q03",
    "sat-math-area-volume-1-q04",
    "sat-math-area-volume-1-q05",
    "sat-math-area-volume-1-q06",
    "sat-math-area-volume-1-q07",
    "sat-math-area-volume-1-q08"
  ],
  "prerequisite_lesson_ids": [],
  "unlock_xp": 0,
  "tags": ["math", "area_volume"],
  "version": "1.0.0"
}
```
