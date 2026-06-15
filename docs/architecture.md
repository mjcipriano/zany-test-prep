# Architecture

Zany Test Prep is a single-package Flutter app with a clean, layered structure.
It is **offline-first**: all content ships as a bundled asset and all state is
persisted locally. There is no backend, no login, and no network dependency.

## Layers

The code under `lib/` is organized into four layers plus the feature UI:

```text
lib/
├── main.dart                # entrypoint: ProviderScope + ZanyApp
├── app/                     # composition root
│   ├── app.dart             # root MaterialApp.router + theme wiring
│   ├── app_controller.dart  # AppController (AsyncNotifier) + providers
│   └── router.dart          # GoRouter config + onboarding redirect
├── core/                    # cross-cutting services (e.g. SoundService)
├── domain/                  # pure business logic (no Flutter UI, no I/O)
│   ├── models/              # exam-agnostic data models
│   └── services/            # game engines (pure, deterministic, unit-tested)
├── data/                    # persistence + content I/O
│   ├── local/               # KeyValueStore interface + impls
│   └── repositories/        # ContentRepository, ProgressRepository
├── design/                  # Material 3 theme + shared widgets
└── features/                # screen-level UI per feature
```

The dependency direction is **features → app → domain ← data**. `domain/models`
and `domain/services` have no dependency on Flutter widgets or on `data`, which
keeps the engines pure and testable.

### `domain/models`

Exam-agnostic data classes, all with `fromJson` factories that parse the content
bundle and persisted JSON:

- `exam.dart`, `skill.dart` — exam descriptor and skill map.
- `lesson.dart` — a lesson (teaching card + ordered `question_ids`).
- `question.dart` — `Question`, `Choice`, `Stimulus`/`StimulusTable`,
  `ProducedAnswer`, and the `QuestionType` enum.
- `difficulty.dart` — `easy`/`medium`/`hard` with a numeric `weight` (1/2/3)
  used by the XP and mastery engines.
- `content_bundle.dart` — the in-memory `ContentBundle` (exam + skills + lessons
  + questions), with lookups by id.
- `profile.dart` — `UserProfile` (exam, daily goal, target date, theme, sound,
  haptics).
- `progress.dart` — `AppProgress` document: `GameState`, per-lesson
  `LessonProgress`, per-question `QuestionStat`, per-skill `SkillMastery`, and
  the `ReviewItem` queue. Also defines `dayKey()` for day-granular dates.

### `domain/services` (the engines)

Pure, deterministic logic with real unit tests. Each engine is a `const` class
operating on plain inputs so it can be tested in isolation:

| Engine | File | Responsibility |
| --- | --- | --- |
| `XpEngine` + `LevelEngine` | `leveling.dart` | XP per answer/lesson; XP→level mapping |
| `StreakEngine` | `streak_engine.dart` | Day-based streak extend/reset logic |
| `MasteryEngine` | `mastery_engine.dart` | 0–100 per-skill mastery updates |
| `ReviewEngine` | `review_engine.dart` | Missed-question review queue + priorities |
| `UnlockEngine` | `unlock_engine.dart` | Which lessons are unlocked / suggest next |
| `Badges` | `badges.dart` | Achievement predicates + granting |
| `AnswerChecker` | `answer_checker.dart` | Grading MC and student-produced answers |
| `GameService` | `game_service.dart` | Orchestrates all of the above for a lesson |

`GameService.applyLessonResult(...)` is the heart of the app: given a finished
lesson attempt, it updates XP, level, streak, daily goal, per-lesson progress,
per-question stats, mastery, the review queue, and badges in one pass, then
returns a `LessonOutcome` for the UI to celebrate. See
[gamification.md](gamification.md) for the formulas.

### `data`

- `local/key_value_store.dart` — a tiny `KeyValueStore` interface with two
  implementations: `PrefsStore` (backed by `shared_preferences`) and
  `MemoryStore` (used in tests). Keeping persistence behind an interface makes
  the app trivial to test without a real device.
- `repositories/content_repository.dart` — loads and caches the offline content
  bundle from `assets/content/<exam>.bundle.json` (and the enabled-exam list
  from `assets/content/exams.json`). The asset reader is injectable so tests can
  supply content directly.
- `repositories/progress_repository.dart` — serializes `UserProfile` and
  `AppProgress` to JSON in the key/value store. See
  [persistence.md](persistence.md).

### `design`

`theme.dart` defines the Material 3 light/dark themes; `widgets.dart` holds
shared UI building blocks used across features.

### `features`

Screen-level UI, one folder per feature: `onboarding`, `home`, `lessons`,
`review`, `progress` (skills), `achievements`, and `settings`. Each screen reads
the current `AppData` from the `appControllerProvider` and calls controller
methods to mutate state.

## State management — Riverpod

State flows through a single root controller plus a few small providers, defined
in `lib/app/app_controller.dart`.

### `AppData` (immutable snapshot)

`AppData` is the immutable session handed to the UI:

```dart
class AppData {
  final ContentBundle bundle;   // loaded offline content
  final UserProfile? profile;   // null until onboarding completes
  final AppProgress progress;   // XP/streak/mastery/review/etc.
  final bool onboarded;
  final int revision;           // bumped to force UI rebuilds on mutation
}
```

`AppProgress` is a mutable document; the `revision` counter is what changes the
identity of the snapshot so Riverpod-driven widgets rebuild after an in-place
mutation. `AppData.bump(...)` returns a new snapshot with `revision + 1`.

### `AppController` (`AsyncNotifier<AppData>`)

`AppController.build()` is async: it awaits the `KeyValueStore`, constructs the
`ProgressRepository`, loads the persisted profile/progress, and loads the content
bundle for the profile's exam (defaulting to `sat`). Mutating methods persist
first, then publish a new `AsyncData` snapshot:

- `completeOnboarding(...)` — creates the local profile, marks onboarded.
- `completeLesson(lesson, results)` — delegates to `GameService`, persists
  progress, and returns a `LessonOutcome`.
- `updateProfile`, `setDailyGoal`, `setThemeMode`, `setSound`, `setHaptics`,
  `setTargetDate` — settings mutations.
- `resetProgress()` — wipes all local data and returns to a fresh, un-onboarded
  state.

### Providers

| Provider | Purpose | Overridable in tests |
| --- | --- | --- |
| `appControllerProvider` | the root `AsyncNotifierProvider<AppController, AppData>` | yes |
| `contentRepositoryProvider` | the `ContentRepository` | yes (inject a fake asset reader) |
| `keyValueStoreProvider` | builds the `PrefsStore` | yes (override with `MemoryStore`) |
| `gameServiceProvider` | the `GameService` | yes |

Because the store and content repository are providers, widget and integration
tests can inject a `MemoryStore` and in-memory content without touching disk or
assets.

## Navigation — GoRouter

`lib/app/router.dart` exposes `routerProvider`, a `GoRouter` wired to the
controller:

- It listens to `appControllerProvider` and refreshes the router whenever app
  state changes (via a `ValueNotifier` `refreshListenable`).
- A `redirect` enforces onboarding: while content is loading or errored it does
  nothing; otherwise an un-onboarded user is sent to `/onboarding`, and an
  onboarded user visiting `/onboarding` is sent to `/home`.

Routes:

| Path | Screen |
| --- | --- |
| `/onboarding` | onboarding flow |
| `/home` | home / learning path (initial location) |
| `/lesson/:id` | lesson player (`?review=true` for review mode) |
| `/review` | review queue session |
| `/skills` | per-skill mastery / progress |
| `/achievements` | badges |
| `/settings` | settings |
| `/about` | about page |

## Content loading

At startup the `AppController` asks the `ContentRepository` for the bundle of the
active exam. The repository reads `assets/content/<exam>.bundle.json` (built from
the canonical content by `tools/build_bundle.py`), parses it into a
`ContentBundle`, and caches it. The bundle contains the exam descriptor, skill
map, all lessons, and all questions, so the app has everything it needs offline
from the first frame. See [content.md](content.md) for the bundle shape and the
generate → validate → bundle pipeline.

## Testing seams

The architecture is built for testability:

- Engines are pure `const` classes — straightforward unit tests with no mocks.
- `KeyValueStore` has a `MemoryStore` implementation for persistence tests.
- `ContentRepository` accepts an injectable `AssetReader`.
- All key dependencies are Riverpod providers, overridable per test.

Run them with `flutter test` (unit + widget) and
`flutter test integration_test` (launch → onboard → complete a lesson → verify
XP and persistence across a reload).
