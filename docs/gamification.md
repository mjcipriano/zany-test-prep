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

## Rewards economy (chests, store, avatar)

A two-sided XP economy sits on top of the lifetime total:

- `GameState.totalXp` stays **lifetime-gained** (levels, badges, dashboard read it).
- `GameState.spentXp` tracks XP burned in the store; `availableXp = totalXp − spentXp`
  is the spendable balance. XP rewards add to `totalXp` only, so spending never
  shrinks the lifetime number.

**Chests** — meeting the daily goal grants exactly one chest for that day
(`GameService` sets `unopenedChests++` on `dailyGoalJustMet`). Opening a chest
(`RewardsService.openChest` → `RewardEngine`) rolls a weighted drop: spendable XP,
a streak freeze, a next-day XP boost, or an unowned avatar/item/pet. The drop table
(`RewardEngine._weights`) is a tunable first pass; `Reward` is a sealed type so new
reward kinds force every switch to be updated. Opening happens on the animated
`/chest` screen (`ChestRevealScreen`): the chest shakes, bursts with sparkles, and
the reward springs in; "Open another" appears while chests remain.

**Streak freezes** — banked, capped at `kMaxStreakFreezes` (3). On return after a
gap, `StreakEngine` spends one freeze per missed day to keep the streak alive when
enough are banked (otherwise it resets and keeps them for a smaller future miss).

**XP boost** — a chest can queue an `xpBoostMultiplier` for the next calendar day
(`xpBoostDay`); `GameService` multiplies that day's earnings while it's active.

**Store** (`/store`) — spend `availableXp` on avatars, items, pets, or extra streak
freezes. The Items tab has a scrolling row of **category chips** with counts (Hats,
Glasses, Face, Ears, Neck, Badges, Auras, Frames, Floating); under "All" the grid is
grouped into sections by category. The Pets tab has a **search box** (name or species,
e.g. "fox") instead, since a pet's category is its rarity. Both have multi-select
**rarity chips**, a **sort** menu (Cheapest, Priciest, Rarest first, A–Z) and **Hide
owned** / **Affordable** toggles; a "Showing N of M · Clear" line and an empty state
with **Clear filters**. The logic is pure Dart in `domain/services/catalog_filter.dart`
(`CatalogFilter`); the bar is `features/rewards/catalog_filter_bar.dart`.
**Customizer** (`/avatar`) — pick an owned avatar and equip owned items/pets; the
same filter bar (with an **Equipped** toggle) appears once a list has 6+ entries.
**Tap the avatar** (customizer or Rewards hub) to open it **full screen**
(`avatar_fullscreen.dart`): as large as the screen allows, pinch or double-tap to
zoom, equipped items listed underneath. Reached from the **Rewards** hub
(`/rewards`), linked off the stats page and a home-screen gift button.

### Avatar content pack

Avatar/item/pet content comes from the external dataset repo
`mjcipriano/zany-test-prep-avatars` (release **v3.1.0**), vendored under
`assets/avatar/` by `tools/sync_avatars.py`. The JSON catalog
(`assets/avatar/manifest/avatar_catalog.json`) is the single source of truth and
lists all 756 assets. The **full pack is bundled** (110 avatars, 376 items, 270 pets;
~22 MB as WebP) so everything works offline. To pull a newer pack release, re-run the script
(`tools/sync_avatars.py --tag <ver> --full`) — nothing hardcodes asset lists, so the
store/customizer expand automatically. (Jacket/top overlays are filtered out via
`kExcludedItemCategories` because they don't fit the varied avatar torsos. **Hats are
retired for now** via `kRetiredItemCategories`: the art is drawn tilted, so the
underside of the brim shows over the face. The art and catalog entries stay in the
pack, owned hats stay owned, and removing `headwear` from that set brings them back
once they are redrawn front-facing; see the pack's docs/hat_art_guidelines.md.)

**Compositing (`target_box_v1`).** Item/pet PNGs are tightly-trimmed sprites; each
carries a normalized **placement target** (`cx,cy,w,h` as fractions of the 512
frame). `AvatarPreview` (`placementRect`) draws the avatar full-frame, then places
each worn item centered on its target box sized to fit (BoxFit.contain), and each
side pet/prop into the side slot it's equipped in (side assets provide per-slot
targets via `targets_by_slot`). Layers render back-to-front by `z_index` (negative z
— e.g. a background frame — sits behind the avatar). Render/pixel tests live in
`test/render/overlap_test.dart`.

**Face fit (`face_fit_v1`, pack v3.1.0).** The avatars' heads sit at different
heights and sizes (eye lines vary by ~7% of the frame, face widths by ~1.4×), so one
box per slot put masks over some avatars' eyes and earrings on cheeks. Every avatar
now carries a measured `face_rig` (`FaceRig`: named points such as `eyes`, `brow`,
`nose_bridge`, `mouth`, `ear_l/ear_r`, plus reference widths `face`, `eyes`, `mouth`,
`ears`), and every head, face and ear item carries a `fit` (`ItemFit`: which rig point
it hangs on, which point of the sprite goes there, and its width as a multiple of a rig
width). `faceFitRect` places those items on the wearer's own face; `fittedRect` falls
back to the target box when either side lacks the data. Hoods and the headset are
`behind` items (`renderZ` = `kBehindAvatarZ`, under the avatar but above auras), and
`sceneScale` shrinks the whole scene a little (bottom-anchored, never below 0.8) when a
tall hat would otherwise be cut off at the top. `test/render/face_fit_test.dart` places
every fitted item on every avatar (masks below the eyes and over the mouth, glasses
centred on the eyes, earrings at ear height, nothing far outside the frame). The rigs
are measured in the pack repo (`scripts/measure_face_rigs.py`, MediaPipe) and the fits
come from `data/item_fit.json` there; see the pack's README_INTEGRATION.md.

**Side slots.** Pets and floating props share four side slots
(`side_left_1/2`, `side_right_1/2`). Equipping fills the first free one; the
customizer's **move** control (`RewardsService.cycleSideSlot`) toggles an equipped
side asset through the remaining open slots so several can be arranged.

> **Stubbed for later:** the chest drop-table balancing and additional reward/item
> types ("other item types we will go over later") are intentionally minimal pending
> further product details.

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

## Pet companions (`PetEngine`, `RewardsService` pets)

Pets are side-slot companions that **level up while equipped** and **evolve**
through the pack's `pet_evolution_v1` contract:

- Every finished session (lesson, practice, review, survival, timed test) grants
  the equipped pet line(s) **pet XP** = `4 × correct + 1 × wrong + 10`
  (`PetEngine.xpForSession`). Unequipped pets earn nothing — pick a buddy.
- Pet XP maps to **levels 1–10** through fixed cumulative thresholds
  (`PetEngine.thresholds`: 40, 100, 180, 280, 400, 540, 700, 880, 1080). The
  Companions section of the customizer shows the level and an XP bar.
- Each pet line has three catalog stages: **Base** (bought in the store or dropped
  from a chest), **Shiny** (`requires_level: 5`) and **Radiant**
  (`requires_level: 10`). Evolved stages are never sold or dropped
  (`CatalogAsset.isPurchasable` is false; the store lists `catalog.basePets`).
  When the line reaches the next stage's level, **Evolve** unlocks the next asset
  and swaps it into whatever slot the pet was wearing (`RewardsService.evolvePet`).
- Pet XP is stored per line id in `GameState.petXp` (`progress.v1`), so a pet keeps
  its level across stages and across exams.
- Rendering: side companions get a soft contact shadow, a rarity/stage glow
  (epic violet, legendary gold, Shiny ice-blue, Radiant gold) and a gentle idle
  float (`AvatarPreview`, disabled under `flutter test`). Layout is guarded by
  `test/render/catalog_geometry_test.dart` (every asset's box stays inside the
  frame, side slots never overlap the face or each other, stacked worn slots
  overlap ≤ 35%) and the pixel tests in `test/render/overlap_test.dart`.
