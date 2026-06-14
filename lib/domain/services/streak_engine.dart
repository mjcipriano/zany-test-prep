import '../models/progress.dart';

/// Result of applying a day's activity to streak state.
class StreakResult {
  const StreakResult({
    required this.currentStreak,
    required this.longestStreak,
    required this.lastActiveDay,
    required this.extended,
    required this.reset,
  });

  final int currentStreak;
  final int longestStreak;
  final String lastActiveDay;
  final bool extended; // streak grew today
  final bool reset; // streak broke and restarted at 1
}

/// Pure day-based streak logic. Works on 'yyyy-MM-dd' keys.
class StreakEngine {
  const StreakEngine();

  int _daysBetween(String fromDay, String toDay) {
    final a = DateTime.parse(fromDay);
    final b = DateTime.parse(toDay);
    return DateTime(b.year, b.month, b.day)
        .difference(DateTime(a.year, a.month, a.day))
        .inDays;
  }

  /// Apply activity occurring on [today] to the prior streak state.
  StreakResult registerActivity({
    required String? lastActiveDay,
    required int currentStreak,
    required int longestStreak,
    required DateTime today,
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
    // gap > 1 (or negative/clock change): streak broke; restart at 1.
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
