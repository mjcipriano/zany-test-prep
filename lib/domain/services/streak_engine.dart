import '../models/progress.dart';

/// Result of applying a day's activity to streak state.
class StreakResult {
  const StreakResult({
    required this.currentStreak,
    required this.longestStreak,
    required this.lastActiveDay,
    required this.extended,
    required this.reset,
    this.freezesUsed = 0,
  });

  final int currentStreak;
  final int longestStreak;
  final String lastActiveDay;
  final bool extended; // streak grew today
  final bool reset; // streak broke and restarted at 1
  final int freezesUsed; // streak freezes consumed to survive missed days
}

/// Pure day-based streak logic. Works on 'yyyy-MM-dd' keys.
class StreakEngine {
  const StreakEngine();

  int _daysBetween(String fromDay, String toDay) {
    final a = DateTime.parse(fromDay);
    final b = DateTime.parse(toDay);
    return DateTime(
      b.year,
      b.month,
      b.day,
    ).difference(DateTime(a.year, a.month, a.day)).inDays;
  }

  /// Apply activity occurring on [today] to the prior streak state.
  ///
  /// [streakFreezes] are banked freezes available to absorb missed days: if the
  /// player returns after a gap, one freeze is spent per missed day (when enough
  /// are banked) to keep the streak alive instead of resetting. Freezes are only
  /// spent when they fully cover the gap; otherwise they're kept for a future,
  /// smaller miss and the streak resets.
  StreakResult registerActivity({
    required String? lastActiveDay,
    required int currentStreak,
    required int longestStreak,
    required DateTime today,
    int streakFreezes = 0,
  }) {
    final todayKey = dayKey(today);
    if (lastActiveDay == null) {
      return StreakResult(
        currentStreak: 1,
        longestStreak: longestStreak < 1 ? 1 : longestStreak,
        lastActiveDay: todayKey,
        extended: true,
        reset: false,
      );
    }
    final gap = _daysBetween(lastActiveDay, todayKey);
    if (gap == 0) {
      // Already active today; nothing changes.
      return StreakResult(
        currentStreak: currentStreak,
        longestStreak: longestStreak,
        lastActiveDay: todayKey,
        extended: false,
        reset: false,
      );
    }
    if (gap == 1) {
      final next = currentStreak + 1;
      return StreakResult(
        currentStreak: next,
        longestStreak: next > longestStreak ? next : longestStreak,
        lastActiveDay: todayKey,
        extended: true,
        reset: false,
      );
    }
    // gap > 1: one or more full days were missed. Spend freezes to bridge them.
    final missedDays = gap - 1;
    if (missedDays > 0 && streakFreezes >= missedDays) {
      final next = currentStreak + 1; // today's activity still extends it
      return StreakResult(
        currentStreak: next,
        longestStreak: next > longestStreak ? next : longestStreak,
        lastActiveDay: todayKey,
        extended: true,
        reset: false,
        freezesUsed: missedDays,
      );
    }
    // Not enough freezes (or a negative/clock change): streak broke; restart at 1.
    return StreakResult(
      currentStreak: 1,
      longestStreak: longestStreak < 1 ? 1 : longestStreak,
      lastActiveDay: todayKey,
      extended: false,
      reset: true,
    );
  }

  /// Whether a streak shown on [today] is still "alive" given last activity.
  /// Used by the home screen to show a broken streak after a missed day.
  int displayedStreak({
    required String? lastActiveDay,
    required int currentStreak,
    required DateTime today,
  }) {
    if (lastActiveDay == null) return 0;
    final gap = _daysBetween(lastActiveDay, dayKey(today));
    if (gap <= 1) return currentStreak; // today or yesterday -> still alive
    return 0; // missed a full day
  }
}
