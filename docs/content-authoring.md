# Authoring & expanding content

Content is **original, SAT- and ACT-style** material with no copyrighted College
Board or ACT, Inc. items. The canonical source lives in `content/exams/<exam>/`
(`sat`, `act`); the app loads one bundle per exam. See [content.md](content.md)
for the full schema.

## The pipeline

```
content/exams/<exam>/  ──generate──▶  (lessons + questions JSON + manifest.json)
        │                                      │
        │                                      ├─ validate ─▶  python tools/validate_content.py
        └────────────────── build ────────────┴─ bundle ───▶  assets/content/<exam>.bundle.json
                                                              assets/content/exams.json
```

```bash
python tools/generate_content.py              # (re)generate every exam (sat + act)
python tools/generate_content.py --exam act   # one exam
python -m unittest discover -s tools/tests -t .   # tooling + generator unit tests
python tools/validate_content.py              # schema + referential + duplicate + variety checks
python tools/build_bundle.py                  # write the bundles + exams.json (loaded by the app)
```

CI runs the tooling tests, the validator for every exam, and fails if a committed
bundle is stale (see `.github/workflows/ci.yml`). Always run **validate →
build_bundle** before committing content changes, and re-run `flutter test` (it
parses the real bundles).

## How content is generated

`tools/generate_content.py` walks a **plan** per exam (`tools/content_gen/exam_plans.py`)
and builds the bank deterministically (fixed seed per exam) so it is reproducible and
auditable.

### Question families (why lessons don't feel templated)

Every generated skill is made of several **item families** — distinct question
*forms* for the same skill, not the same template with new numbers. For example
`linear_equations` mixes "solve for x", "variables on both sides", "which equation
models the situation", "interpret the slope in context", "find the intercept",
"slope through two points", a grid-in, and more. Generator modules expose

```python
FAMILIES = {"linear_equations": {"easy": [fn, fn, ...], "medium": [...], "hard": [...]}}
```

where each `fn(rng, difficulty)` returns a question body (`tools/content_gen/registry.py`
documents the contract). The lesson builder **round-robins across a skill's families**,
so a 20-question lesson cycles through every form; the practice bank draws families at
random. Each emitted item is tagged `family:<name>`, and the validator fails any lesson
built from families that uses fewer than 3 of them or lets one family exceed 50% of
the items (`low_variety_lessons` in its report).

Generator modules:

- **Math** (`math_gen.py`, `math_extra.py`, ACT-only skills in `math_act.py`): every
  answer is *computed*, so correctness is machine-checkable; distractors model common
  errors and each carries a rationale. Items honour `util.OPTION_COUNT` (4 choices for
  the SAT, 5 for ACT Math).
- **Writing / English conventions** (`rw_gen.py`, `rw_extra.py`, ACT usage in
  `rw_act.py`): rule-based/combinatorial items with exactly one defensible answer, in
  several sentence frames and formats per skill. Blank-filling families use a single
  `___` plus an instruction paragraph; the ACT plan rewrites those into the ACT's
  bracketed-portion / **NO CHANGE** format (`exam_plans.act_no_change`).
- **Reading** (`passages.py`, `passages_extra.py`): original authored passages with
  main-idea, inference, structure/purpose, words-in-context and evidence questions,
  plus paired passages for cross-text items. Shared by both exams.
- **Science** (`science_gen.py`, ACT only): data-representation, trends/extrapolation
  and experimental-design items computed from a library of 40 templated experiments
  (tables with real numbers), plus 21 authored conflicting-viewpoint sets (some with
  three scientists).
- **Teaching** (`teaching.py` + `teaching_*_act.py`, `teaching_science.py`): the
  multi-screen mini-lesson shown before each lesson's questions.

To grow the content, add a family to a skill (a new function in its `FAMILIES` list),
or add a `SkillSpec` to the exam's plan (each skill is an independent easy→medium→hard
track), then regenerate. New families need a unit test in `tools/tests/` — the harness
(`tools/tests/helpers.py`) validates every family against the schema on every tier.

### Practice bank

Beyond the curated lessons, the generator also emits a large **practice bank**
(`content/exams/<exam>/questions/bank/`) that is not bound into any lesson. The
practice modes and the timed test draw from it for near-endless variety. Bank size
per skill tier is controlled by each plan's `bank_per_kind` (per domain) or a
`SkillSpec.bank_per_tier` override and is best-effort: computed math and combinatorial
conventions produce thousands of unique items, while small-space skills
(circles/trig/right-triangles, conflicting viewpoints) and authored reading/pools are
not banked (`no_bank_skills`).

## Adding content by hand or with an AI agent

You can also add lessons/questions as JSON directly under
`content/exams/sat/lessons/{rw,math}/` and `content/exams/sat/questions/{rw,math}/`,
add them to `manifest.json`, then validate + bundle. The prompt files in
`content/prompts/` are written for AI agents and enforce the rules (original content,
one correct answer, rationales, accurate difficulty, machine-checkable math answers,
schema conformance). See `content/validators/README.md`.

## Adding a new exam (AP, PSAT, …)

The model is exam-agnostic and the app already switches between SAT and ACT. To add
an exam:

1. Create `content/exams/<id>/` with `exam.yaml` (id, names, `tagline`, `domains`,
   the `timed_test` module layout, and `scoring` — `sat_1600`, `act_36` or `percent`
   with optional `composite_domains`) and `skills.yaml` (domains → sections → skills).
   Skill ids shared with an existing exam reuse its generators *and* its mastery.
2. Add an `ExamPlan` to `tools/content_gen/exam_plans.py` listing its `SkillSpec`s
   (kind `family`, `rw_pool`, `reading` or `cross_text`), choice counts, bank sizes and
   any transforms; add teaching cards for new skills.
3. `python tools/generate_content.py --exam <id>`, then validate and bundle. The
   bundler lists every enabled exam in `assets/content/exams.json`, which is all the
   app needs: onboarding offers it, Settings can switch to it, the home path shows one
   track per domain, and the practice test / dashboard use its layout and scale.
