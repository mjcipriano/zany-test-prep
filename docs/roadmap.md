# Known limitations & roadmap

## Known limitations

- **Two exams.** SAT and ACT ship; switching exams in Settings keeps XP, streaks and
  rewards (lesson/question ids are exam-prefixed, so each exam keeps its own path
  progress; skills with the same id share mastery across exams).
- **Score estimates are linear.** Section scores (SAT 200–800, ACT 1–36) are mapped
  from accuracy, not from an official equating table.
- **ACT Reading uses the shared passage pool.** Passages are shorter than a real ACT
  reading passage (one question per skill per passage).
- **Lesson resume is coarse.** Leaving a lesson mid-way discards in-lesson progress
  (with a confirm dialog); completed-lesson state is always saved. Per-question resume
  is not implemented.
- **Audio is a small SFX set.** The app ships original melodic cues + Kenney CC0
  clicks (`assets/audio/`, gated by the Sound setting); there is no music or
  voiceover yet.
- **Single-file persistence.** State is JSON in `shared_preferences`. This is robust at
  the current scale (hundreds of entries) but is not a query-able database.
- **Content breadth.** SAT: 117 curated lessons + practice bank (24,171 questions);
  ACT: 147 lessons + bank (16,617 questions). Every generated skill mixes several
  question families per difficulty. Passage-based reading comprehension is authored
  (32 passages + 16 paired sets, shared by both exams), so heavy passage-reading-only
  practice cycles sooner than math, grammar or science; ACT Reading has 180 items.
- **Reading option lengths.** The authored passage questions skew toward a longer
  correct option; the validator reports the share so it can be driven down over time.
- **Android-first.** iOS/web/desktop targets are scaffolded and the code is
  cross-platform, but only Android is built/tested in CI.

## Roadmap

**Content**
- Grow the bank (more lessons per skill, more reading passages, more grid-ins).
- Add AP (Biology, Chemistry, Calculus, Statistics) exams using the existing
  per-exam plans.
- Longer ACT-style reading passages with multiple questions each; more
  conflicting-viewpoint sets.

**Learning**
- Adaptive difficulty and smarter "suggested next" using mastery + review signals.
- A full diagnostic flow during onboarding to seed mastery.
- Per-question lesson resume.

**Platform & polish**
- iOS, web, and desktop builds in CI; release signing for Play Store.
- Richer animations/sound, optional reminders/notifications.
- Accessibility pass (screen-reader labels, larger text scaling, contrast review).

**Infrastructure**
- Migrate persistence to Drift/Isar if the data model grows query-heavy.
- Content authoring tooling/CLI and a near-duplicate similarity check beyond exact
  normalization.
