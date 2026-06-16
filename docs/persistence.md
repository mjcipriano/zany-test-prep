# Persistence model

The app is **offline-first**: all state lives on the device and survives force-close
and restart. There is no backend, account, or network call.

## Where it lives

State is JSON-serialized and stored via `shared_preferences`, behind a small
`KeyValueStore` interface (`lib/data/local/key_value_store.dart`) so it can be faked
in tests (`MemoryStore`). The repository is `ProgressRepository`
(`lib/data/repositories/progress_repository.dart`).

Keys:

| Key            | Contents                                  |
|----------------|-------------------------------------------|
| `profile.v1`   | `UserProfile` (exam, daily goal, target date, sound/haptics/theme, createdAt) |
| `progress.v1`  | `AppProgress` (see below)                  |
| `onboarded.v1` | `"true"` once onboarding is complete       |

## `AppProgress` shape

```jsonc
{
  "game": {
    "totalXp": 130, "currentStreak": 4, "longestStreak": 7,
    "lastActiveDay": "2026-06-14", "dailyXp": 40, "dailyDay": "2026-06-14",
    "earnedBadges": ["first_lesson", "streak_3"]
  },
  "lessons":       { "<lessonId>": { "completed": true, "bestCorrect": 18, "total": 20, "stars": 3, "timesCompleted": 2, "lastCompletedDay": "..." } },
  "questionStats": { "<questionId>": { "attempts": 3, "correct": 2, "lastCorrect": true, "totalResponseMs": 12000 } },
  "skillMastery":  { "<skillId>": { "mastery": 62.0 } },
  "reviewQueue":   [ { "questionId": "...", "skillId": "...", "priority": 4, "lastReviewedDay": "..." } ]
}
```

Day-granular values (streak, daily goal, review) are stored as `yyyy-MM-dd` strings
to avoid timezone/precision bugs.

## When it is written

`AppController` (`lib/app/app_controller.dart`) saves after every meaningful change:
finishing a lesson or review, editing a setting, completing onboarding. Each save
serializes the whole document — small at this scale (hundreds of entries).

## Surviving app updates (no data loss, no crash-on-load)

Updating the app must never wipe XP/streaks/mastery/settings or crash because the
stored data was written by an older (or newer) build. The strategy:

1. **Stable keys, no destructive bumps.** The `*.v1` keys are not changed casually.
   shared_preferences persists across app updates as long as the package id and
   signing key are unchanged, so install-over-install keeps the data. (Android also
   requires the `versionCode` in `pubspec.yaml` to only ever increase.)

2. **Additive schema.** New fields are *added* with safe defaults; existing fields
   keep their meaning. Reading a document re-serializes the full known shape, so a
   user's existing valid settings are preserved. A `"schema"` integer
   (`kProgressSchemaVersion` / `kProfileSchemaVersion`) is written for future
   migrations, but field-level tolerance handles ordinary additions without one.

3. **Defensive parsing — any valid setting is kept, invalid ones never crash.**
   Every `fromJson` uses the coercion helpers in
   `lib/domain/models/safe_json.dart`: a missing or wrong-typed field falls back to
   its default instead of throwing (e.g. `"1500"`/`1500.0` → `1500`, `"true"` →
   `true`, a null list → empty). A single corrupt collection entry is skipped rather
   than aborting the whole load. As a last resort, `ProgressRepository` wraps decode
   + parse in try/catch: unreadable progress → fresh `AppProgress`, unreadable
   profile → re-onboard. The app therefore boots cleanly no matter what is on disk.

4. **Old saves are forward-compatible.** A pre-rewards `game` blob (no `spentXp`,
   `streakFreezes`, chests, owned assets…) loads with those fields defaulted, so
   updating into the rewards release keeps all prior XP and streaks intact.

Coverage: `test/persistence/progress_repository_test.dart` → the *update resilience*
group (corrupt JSON, wrong types, partial corruption, unknown future fields, missing
rewards fields).

## Export / import (cross-device, cross-version)

**Settings → Backup & restore** exports all local state to a portable JSON backup
and imports it on another device or after a reinstall.

- The format is a versioned envelope (`lib/domain/models/backup.dart`): `format`
  magic string, `formatVersion`, `appVersion`, schema versions, `exportedAt`, plus
  the `profile` + `progress` + `onboarded` payload.
- **Cross-version aware:** import validates the magic string, warns (but still
  proceeds) if the backup came from a newer format/app version, and parses the
  payload through the same defensive `fromJson`s — so unknown/mistyped fields
  degrade gracefully instead of failing the import. A confirm screen summarizes the
  snapshot (XP, streak, lessons, unlocks) before it **replaces** current data.
- **Cross-platform:** export shares a `.json` file (share sheet) or copies to the
  clipboard; import reads a file (`file_picker`) or pastes from the clipboard.
- Pure codec (`encodeBackup`/`decodeBackup`) is unit-tested in
  `test/unit/backup_test.dart`; the device-to-device round trip is covered in
  `progress_repository_test.dart`.

## Reset

**Settings → Reset progress** calls `ProgressRepository.resetAll()`, which removes all
three keys. The router then redirects to onboarding.

## Testing

`test/persistence/progress_repository_test.dart` round-trips the profile and full
progress document (xp, streak, lessons, mastery, review) through a fresh repository,
and `test/widget/full_flow_test.dart` proves state survives a simulated app restart
(re-pumping the app against the same store).
