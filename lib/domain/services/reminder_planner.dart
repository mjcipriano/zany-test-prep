import 'package:timezone/timezone.dart' as tz;

import '../models/progress.dart';
import '../models/reminder_settings.dart';

/// The evening slot for the "streak at risk" nudge: 8:00 PM.
const int kStreakNudgeMinutes = 20 * 60;

/// The nudge never lands later than 10:00 PM (teens, school nights).
const int kLatestNudgeMinutes = 22 * 60;

/// How far ahead reminders are scheduled. They are one-shot notifications
/// (so each day's copy can vary and mention the streak) and the plan is rebuilt
/// on every app start, settings change and finished session; a player who
/// ignores the app for this long simply stops getting reminders.
const int kReminderHorizonDays = 14;

/// Where a tapped notification takes the player (validated before routing).
const String kReminderRouteHome = '/home';
const String kReminderRoutePractice = '/practice/unlocked';
const Set<String> kReminderRoutes = {
  kReminderRouteHome,
  kReminderRoutePractice,
};

enum ReminderKind { daily, streakNudge }

/// One notification to schedule. [when] is an absolute instant in the
/// device's time zone.
class PlannedReminder {
  const PlannedReminder({
    required this.id,
    required this.kind,
    required this.when,
    required this.title,
    required this.body,
    required this.payload,
  });

  /// Stable per (kind, day offset) so a re-plan replaces the same slots.
  final int id;
  final ReminderKind kind;
  final tz.TZDateTime when;
  final String title;
  final String body;

  /// Route opened when the notification is tapped (see [kReminderRoutes]).
  final String payload;

  @override
  String toString() => 'PlannedReminder($id, $kind, $when, "$title")';
}

/// When the evening streak nudge fires for [settings] (minutes after
/// midnight), or null when there is no nudge.
///
/// It sits at [kStreakNudgeMinutes] but always at least an hour after the
/// daily reminder, and never after [kLatestNudgeMinutes]; when the daily
/// reminder is itself that late, the reminder is the last call of the day.
int? streakNudgeMinutesFor(ReminderSettings settings) {
  if (!settings.enabled || !settings.streakNudge) return null;
  final after = settings.minutesOfDay + 60;
  final at = after > kStreakNudgeMinutes ? after : kStreakNudgeMinutes;
  return at > kLatestNudgeMinutes ? null : at;
}

/// Pure "what to schedule when" logic for local reminders. No plugin, no
/// clock: give it the current instant (in the device's zone) and the game
/// state and it returns the notifications that should be pending.
///
/// Rules:
/// - Disabled reminders -> nothing.
/// - A daily reminder at the chosen time on each of the next
///   [horizonDays] days, skipping today once today's goal is met (and any
///   time already past).
/// - A streak nudge in the evening on each day the current streak could
///   still be saved (it is alive, possibly bridged by banked freezes) and the
///   day's goal is not met yet. Meeting today's goal therefore cancels
///   today's nudge on the next re-plan.
class ReminderPlanner {
  const ReminderPlanner({this.horizonDays = kReminderHorizonDays});

  final int horizonDays;

  static const int dailyIdBase = 100;
  static const int nudgeIdBase = 200;

  List<PlannedReminder> plan({
    required tz.TZDateTime now,
    required ReminderSettings settings,
    required GameState game,
    required int dailyGoalXp,
    required int dailyGoalMinutes,
  }) {
    if (!settings.enabled) return const [];
    final todayKey = dayKey(now);
    final goalMetToday =
        game.dailyDay == todayKey && game.dailyXp >= dailyGoalXp;
    final activeToday = game.lastActiveDay == todayKey;
    final nudgeAt = streakNudgeMinutesFor(settings);

    final out = <PlannedReminder>[];
    for (var i = 0; i < horizonDays; i++) {
      // Calendar arithmetic in UTC so a DST change can't skip or repeat a day.
      final date = DateTime.utc(now.year, now.month, now.day + i);
      final key = dayKey(date);
      if (i == 0 && goalMetToday) continue;
      final streak = savableStreakOn(game, key);
      final copySeed = date.difference(DateTime.utc(2024)).inDays;

      final dailyAt = _at(now.location, date, settings.minutesOfDay);
      if (dailyAt.isAfter(now)) {
        final copy = ReminderCopy.daily(
          seed: copySeed,
          streak: streak,
          goalMinutes: dailyGoalMinutes,
        );
        out.add(
          PlannedReminder(
            id: dailyIdBase + i,
            kind: ReminderKind.daily,
            when: dailyAt,
            title: copy.title,
            body: copy.body,
            payload: kReminderRouteHome,
          ),
        );
      }

      if (nudgeAt != null && streak > 0) {
        final at = _at(now.location, date, nudgeAt);
        if (at.isAfter(now)) {
          final copy = ReminderCopy.nudge(
            seed: copySeed,
            streak: streak,
            // Already practiced today: the streak is safe, only the goal is
            // open, so the copy talks about the goal instead.
            goalPending: i == 0 && activeToday,
          );
          out.add(
            PlannedReminder(
              id: nudgeIdBase + i,
              kind: ReminderKind.streakNudge,
              when: at,
              title: copy.title,
              body: copy.body,
              payload: kReminderRoutePractice,
            ),
          );
        }
      }
    }
    return out;
  }

  /// The streak that practicing on [day] would keep alive, or 0 when it is
  /// already lost by then. Mirrors [StreakEngine.registerActivity]: missed
  /// days in between are bridged only if enough freezes are banked.
  static int savableStreakOn(GameState game, String day) {
    final last = game.lastActiveDay;
    if (game.currentStreak <= 0 || last == null) return 0;
    final gap = daysBetweenDayKeys(last, day);
    if (gap <= 1) return game.currentStreak;
    return gap - 1 <= game.streakFreezes ? game.currentStreak : 0;
  }

  static tz.TZDateTime _at(tz.Location loc, DateTime date, int minutes) =>
      // TZDateTime normalizes a wall time that doesn't exist (DST gap) forward.
      tz.TZDateTime(
        loc,
        date.year,
        date.month,
        date.day,
        minutes ~/ 60,
        minutes % 60,
      );
}

/// A notification's title and body.
class ReminderText {
  const ReminderText(this.title, this.body);
  final String title;
  final String body;
}

/// Friendly, rotating reminder copy. Picks deterministically from [seed]
/// (the target day), so consecutive days read differently and tests are
/// stable. `{n}` is the streak, `{m}` the daily goal in minutes.
class ReminderCopy {
  ReminderCopy._();

  static const List<ReminderText> dailyFresh = [
    ReminderText(
      'Quick study break? 📚',
      'Your {m}-minute goal is waiting. Future you says thanks!',
    ),
    ReminderText(
      'Ready for a mini challenge? ⚡',
      'Knock out a few questions and grab some XP.',
    ),
    ReminderText(
      'Your future score says hi 👋',
      'A little practice today adds up fast.',
    ),
    ReminderText(
      'Time to level up 🚀',
      'Jump in for a quick lesson. {m} minutes is all it takes.',
    ),
  ];

  static const List<ReminderText> dailyStreak = [
    ReminderText(
      '{n} days strong 💪',
      'Keep the streak rolling with a quick lesson today.',
    ),
    ReminderText(
      'Your {n}-day streak 🔥 is waiting',
      'A few questions today keeps it going.',
    ),
    ReminderText(
      'Streak check: {n} days 🔥',
      'Nice run! Hop in for today\'s {m} minutes.',
    ),
  ];

  static const List<ReminderText> nudgeAtRisk = [
    ReminderText(
      'Your {n}-day streak needs you 🔥',
      'Still time today! One quick lesson keeps it alive.',
    ),
    ReminderText(
      'Save your streak! ⏰',
      'A quick session tonight keeps your {n}-day streak going.',
    ),
    ReminderText(
      'Streak SOS 🆘',
      'Your {n}-day streak is on the line tonight. Quick practice to the rescue?',
    ),
  ];

  static const List<ReminderText> nudgeGoalPending = [
    ReminderText(
      'So close to today\'s goal 🎯',
      'Finish it off and keep your {n}-day streak shining.',
    ),
    ReminderText(
      'Almost there! 🏁',
      'A few more questions and today\'s goal is done. {n} days and counting!',
    ),
  ];

  static ReminderText daily({
    required int seed,
    required int streak,
    required int goalMinutes,
  }) => _fill(
    _pick(streak > 0 ? dailyStreak : dailyFresh, seed),
    streak,
    goalMinutes,
  );

  static ReminderText nudge({
    required int seed,
    required int streak,
    required bool goalPending,
  }) => _fill(
    _pick(goalPending ? nudgeGoalPending : nudgeAtRisk, seed),
    streak,
    0,
  );

  static ReminderText _pick(List<ReminderText> pool, int seed) =>
      pool[seed.abs() % pool.length];

  static ReminderText _fill(ReminderText t, int streak, int minutes) {
    String f(String s) =>
        s.replaceAll('{n}', '$streak').replaceAll('{m}', '$minutes');
    return ReminderText(f(t.title), f(t.body));
  }
}
