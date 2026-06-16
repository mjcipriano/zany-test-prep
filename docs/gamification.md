# Gamification model

All logic is in `lib/domain/services/` as small, pure, unit-tested engines. The
`GameService` ties them together when a lesson or review finishes
(`applyLessonResult` / `applyPracticeResult`).

## XP (`XpEngine`)

- Correct answer: `5 × difficulty.weight` → **easy 5, medium 10, hard 15**.
- Wrong answer: **0**.
- Review answers earn 60% (rounded) of the normal value.
- Lesson completion bonus: **+20**. Perfect (all correct) lesson: **+15** more.

## Levels (`LevelEngine`)

Cumulative thresholds with a growing increment: the XP needed to go from level *L*
to *L+1* is `100 + (L−1)×25`.

- Level 2 at 100 XP, level 3 at 225, level 4 at 375, …
- `levelForXp`, `xpIntoLevel`, `xpForNextLevel`, and `progressToNext` drive the
  home-screen level bar.

## Streaks (`StreakEngine`)

Day-based (`yyyy-MM-dd`):

- First activity → streak 1.
- Activity the next calendar day → streak + 1.
- Same day again → no change.
- A fully missed day → streak resets to 1 on the next activity.
- `longestStreak` is preserved. `displayedStreak` shows 0 on the home screen once a
  day has been fully missed (the streak is "at risk"/broken).

## Daily goal

The goal is expressed in XP: `dailyGoalMinutes × 20` (so 5/10/15 min → 100/200/300 XP),
calibrated to roughly 20 XP per minute of focused practice.
`GameService` resets the daily counter when the day rolls over and reports
`dailyGoalMet` / `dailyGoalJustMet` for celebration.

## Mastery (`MasteryEngine`)

Per-skill, 0–100:

- Correct: `+4 × weight` (easy 4, medium 8, hard 12); review correct ×0.75.
- Wrong: `−2 × weight` (gentler than a correct raises, so progress is sticky).
- Clamped to 0–100. Labels: New / Developing (≥20) / Proficient (≥50) / Mastered (≥80).

## Lesson crowns (stars)

By accuracy: **3** for 100%, **2** for ≥80%, **1** for ≥60%, else **0**. A lesson is
marked complete once finished regardless of stars; the best star count is kept.

## Unlocks & progression (`UnlockEngine`)

Each **skill is an independent track**: the learner picks any subject area and works
through its difficulty tiers (**easy → medium → hard**). Within a skill, a tier
requires the previous tier of the *same* skill; the first tier of every skill is open
from the start. So unlocking one section is never required to start another —
e.g., you can begin Quadratics and Transitions without finishing Linear Equations.

A lesson is unlocked when every `prerequisiteLessonIds` lesson is completed **and**
`totalXp ≥ unlockXp` (prerequisites only ever reference the same skill).
`suggestNext` powers the home screen's "Continue" card.

## Practice modes

Two endless-style modes draw random questions one after another (each session is a
fresh random set; XP/mastery/review apply, but no lesson is marked complete):

- **Quick Practice** — random questions from any section the learner has unlocked.
- **Challenge** — random questions from any section, including not-yet-unlocked ones.
- **Survival** — answer as many as you can in a row; the run ends on the first miss,
  and your longest correct streak (`game.survivalBest`) is recorded with its own
  achievement tier.

Challenge and Survival draw from the whole bank and use **domain-balanced sampling**
(`lib/features/practice/sampling.dart`) so sessions stay ~50/50 Math vs Reading &
Writing. Quick Practice and Challenge run through the lesson player via the practice
(`completeReview`) path; Survival has its own end-on-miss flow (`completeSurvival`).

## Spaced-repetition review (`ReviewEngine`)

An SM-2-style scheduler:
- A missed question enters the queue **due immediately** (interval 1 day).
- Each correct **review** answer grows the interval (1 → 3 → ~7 → ~16 …) via an ease
  factor and pushes the next due date out; a miss resets the interval and lowers ease.
  An item **graduates** out once its interval passes ~30 days.
- The home "Review" badge and the Review screen use only items **due now**, most-overdue
  first (priority breaks ties).

## Diagnostic & dashboard

- **Diagnostic** (one question per skill, no feedback) seeds per-skill mastery and shows
  where to focus; offered as a one-time card to new learners.
- **Progress dashboard** visualizes local data: estimated SAT score (from accuracy),
  totals, a daily-XP bar chart, a streak calendar heatmap, accuracy by domain, and the
  weakest skills. Daily history is logged via `AppProgress.recordDay`.

## Timed practice test

A Digital-SAT-shaped simulation: two timed Reading & Writing modules then two Math
modules, with flag/navigate within a module and an estimated section + total score (raw
correct mapped to a 200–800 scale per section). Answers feed XP, mastery, and the review
queue at the end.

## Badges (`Badges`)

Over **100** achievements — pure predicates over progress, organized in tiers: total
XP, longest streak, level reached, lessons completed (overall, math, and
reading/writing), 3-crown lessons, skills mastered (≥80) and proficient (≥50), total
questions answered, total correct, distinct skills practiced, plus one-offs (big
single-day XP, clearing the review queue, etc.). `evaluateAndGrant` awards any newly
satisfied badges after each lesson or practice session.

## Audio & haptic feedback

Short sound cues reinforce feedback, gated by the **Sound** setting (and haptics by
the **Haptics** setting). Sounds play through `SoundService`
(`lib/core/sound_service.dart`), which is a no-op in tests:

- Answer correct / incorrect → original melodic chime / buzz.
- Choice select & advancing to the next question → Kenney UI clicks.
- Lesson complete → success jingle; level-up → fanfare.

Audio assets live in `assets/audio/`: the click sounds are **Kenney UI Audio (CC0)**
and the melodic cues are **original**, synthesized by `tools/gen_audio.py`
(regenerate with `python tools/gen_audio.py`). See `assets/audio/CREDITS.md`.

## Tests

`test/unit/leveling_test.dart`, `streak_test.dart`,
`mastery_review_unlock_test.dart`, `game_service_test.dart`. Screenshots in the
README are generated by `test/screenshots/` (`flutter test --tags screenshots`).
