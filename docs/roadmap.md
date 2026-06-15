# Known limitations & roadmap

## Known limitations

- **One exam surfaced.** The data model is exam-agnostic and the bundler builds every
  exam under `content/exams/`, but only SAT is authored and the UI exam-switcher is
  not built yet.
- **Lesson resume is coarse.** Leaving a lesson mid-way discards in-lesson progress
  (with a confirm dialog); completed-lesson state is always saved. Per-question resume
  is not implemented.
- **Audio is a small SFX set.** The app ships original melodic cues + Kenney CC0
  clicks (`assets/audio/`, gated by the Sound setting); there is no music or
  voiceover yet.
- **Single-file persistence.** State is JSON in `shared_preferences`. This is robust at
  the current scale (hundreds of entries) but is not a query-able database.
- **Content breadth.** 117 curated lessons plus a large practice bank (~20.9k total
  questions; ~11.4k math, ~9.4k reading/writing) covering the Digital SAT R&W and Math
  domains, with easy/medium/hard tiers per skill. Passage-based reading comprehension
  is authored (~32 passages); the high-volume R&W bank is the combinatorial Writing
  types (grammar, transitions, evidence, etc.), so very heavy passage-reading-only
  practice will cycle sooner than math or grammar.
- **Android-first.** iOS/web/desktop targets are scaffolded and the code is
  cross-platform, but only Android is built/tested in CI.

## Roadmap

**Content**
- Grow the bank (more lessons per skill, more reading passages, more grid-ins).
- Add ACT and AP (Biology, Chemistry, Calculus, Statistics) exams using the existing
  pipeline; build the exam-switcher UI.

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
