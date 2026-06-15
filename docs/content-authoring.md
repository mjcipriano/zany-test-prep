# Authoring & expanding content

Content is **original, SAT-style** material with no copyrighted College Board items.
The canonical source lives in `content/exams/sat/`; the app loads a single bundle
built from it. See [content.md](content.md) for the full schema.

## The pipeline

```
content/exams/sat/  ──generate──▶  (lessons + questions JSON + manifest.json)
        │                                   │
        │                                   ├─ validate ─▶  python tools/validate_content.py
        └────────────────── build ─────────┴─ bundle ───▶  assets/content/sat.bundle.json
```

```bash
python tools/generate_content.py    # (re)generate the canonical JSON bank
python tools/validate_content.py    # schema + referential + duplicate + answer checks
python tools/build_bundle.py        # write assets/content/sat.bundle.json (loaded by the app)
```

CI runs the validator and fails if the committed bundle is stale (see
`.github/workflows/ci.yml`). Always run **validate → build_bundle** before committing
content changes, and re-run `flutter test` (it parses the real bundle).

## How content is generated

`tools/generate_content.py` + `tools/content_gen/` build the bank deterministically
(fixed seed) so it is reproducible and auditable:

- **Math** (`math_gen.py`): questions are *computed*, so answers are provably correct;
  distractors model common errors and each carries a rationale.
- **Conventions/Expression RW** (`rw_gen.py`): rule-based/combinatorial items
  (boundaries, subject-verb agreement, punctuation, pronouns, modifiers, transitions,
  concision, rhetorical synthesis) with exactly one defensible answer.
- **Reading** (`passages.py`): original authored passages, each with main-idea,
  inference, structure/purpose, words-in-context, and command-of-evidence questions,
  plus paired passages for cross-text questions.

To grow the bank, add generators/items there and bump per-lesson counts in the
`MATH_PLAN` / `RW_PLAN` tables in `generate_content.py`, then regenerate.

## Adding content by hand or with an AI agent

You can also add lessons/questions as JSON directly under
`content/exams/sat/lessons/{rw,math}/` and `content/exams/sat/questions/{rw,math}/`,
add them to `manifest.json`, then validate + bundle. The prompt files in
`content/prompts/` are written for AI agents and enforce the rules (original content,
one correct answer, rationales, accurate difficulty, machine-checkable math answers,
schema conformance). See `content/validators/README.md`.

## Adding a new exam (ACT, AP, …)

The model is exam-agnostic. To add an exam:

1. Create `content/exams/<id>/` with `exam.yaml` (set `enabled: true` when ready) and
   `skills.yaml` (domains → sections → skills).
2. Add lessons and questions referencing that exam's skill ids; keep ids lowercase
   `a-z0-9-`.
3. Generate a `manifest.json` for it (the generator does this; or write it by hand).
4. `python tools/validate_content.py --exam <id>` then `python tools/build_bundle.py`
   (it builds every exam under `content/exams/` and lists enabled ones in
   `assets/content/exams.json`).

No app code needs to change for a new exam's content to load. Surfacing multiple exams
in the onboarding/exam-switcher UI is a small follow-up (see [roadmap.md](roadmap.md)).
