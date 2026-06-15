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

To grow the content, edit the skill-centric `MATH_SKILLS` / `RW_SKILLS` tables in
`generate_content.py` (each skill is an independent easy→medium→hard track) and the
generators/pools, then regenerate.

### Practice bank

Beyond the ~81 curated lessons, the generator also emits a large **practice bank**
(`content/exams/sat/questions/bank/`, ~14k questions) that is not bound into any
lesson. The two practice modes draw from it for near-endless variety (enough for a
year of daily practice without repeating exact items). Bank size per skill is
controlled by `BANK_PER_TIER` in `generate_content.py` and is best-effort: math
skills (computed answers) and combinatorial conventions produce thousands of unique
items, while small-space math (circles/trig/right-triangles) and authored
reading/pools are not banked. Widen a generator's numeric ranges to grow its share.

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
