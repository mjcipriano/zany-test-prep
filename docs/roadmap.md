# Known limitations & roadmap

## Known limitations

- **Two exams.** SAT and ACT ship; switching exams in Settings keeps XP, streaks and
  rewards (lesson/question ids are exam-prefixed, so each exam keeps its own path
  progress; skills with the same id share mastery across exams).
- **Score estimates are approximate.** Section scores come from original nonlinear,
  route-aware curves, not an official equating table.
- **ACT Reading** has 15 ACT-length passage sets (9 questions each) plus the shared
  short-passage pool.
- **Resume** is per-question for lessons; reviews and practice sessions are not resumable.
- **Audio is a small SFX set.** The app ships original melodic cues + Kenney CC0
  clicks (`assets/audio/`, gated by the Sound setting); there is no music or
  voiceover yet.
- **Single-file persistence.** State is JSON in `shared_preferences`. This is robust at
  the current scale (hundreds of entries) but is not a query-able database.
- **Content breadth.** SAT: 117 curated lessons + practice bank (31,172 questions);
  ACT: 147 lessons + bank (21,780 questions). Every generated skill mixes several
  question families per difficulty. Passage-based reading comprehension is authored
  (69 passages + 29 paired sets, shared by both exams), so heavy passage-reading-only
  practice still cycles sooner than math, grammar or science; ACT Reading has 495 items.
- **Android-first.** iOS/web/desktop targets are scaffolded and the code is
  cross-platform, but only Android is built/tested in CI.

## Roadmap

**Content**
- Grow the bank (more lessons per skill, more reading passages, more grid-ins).
- Add AP (Biology, Chemistry, Calculus, Statistics) exams using the existing
  per-exam plans.

**Learning**

**Platform & polish**
- iOS, web, and desktop builds in CI; release signing for Play Store.
- Richer animations/sound; iOS notification wiring.

**Infrastructure**
- Migrate persistence to Drift/Isar if the data model grows query-heavy.
- Content authoring tooling/CLI and a near-duplicate similarity check beyond exact
  normalization.
