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

## Reset

**Settings → Reset progress** calls `ProgressRepository.resetAll()`, which removes all
three keys. The router then redirects to onboarding.

## Testing

`test/persistence/progress_repository_test.dart` round-trips the profile and full
progress document (xp, streak, lessons, mastery, review) through a fresh repository,
and `test/widget/full_flow_test.dart` proves state survives a simulated app restart
(re-pumping the app against the same store).
