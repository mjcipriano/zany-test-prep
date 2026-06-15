import '../models/progress.dart';
import '../models/question.dart';

/// Spaced-repetition review (an SM-2-style scheduler).
///
/// A missed question enters the queue due immediately. Each correct review pushes
/// its next due date further out (1 -> 3 -> ~7 -> ~16 days …) and raises its ease;
/// a miss resets the interval and lowers ease. An item graduates out of the queue
/// once it has been answered correctly with a long interval.
class ReviewEngine {
  const ReviewEngine();

  static const int maxPriority = 5;
  static const double minEase = 1.3;
  static const int graduateInterval = 30; // days; correct beyond this -> remove

  int _daysBetween(String from, String to) {
    final a = DateTime.parse(from);
    final b = DateTime.parse(to);
    return DateTime(
      b.year,
      b.month,
      b.day,
    ).difference(DateTime(a.year, a.month, a.day)).inDays;
  }

  String _addDays(String day, int n) {
    final d = DateTime.parse(day).add(Duration(days: n));
    return dayKey(d);
  }

  /// Record an answer to [question]. Mutates [progress.reviewQueue] in place.
  void onAnswered({
    required AppProgress progress,
    required Question question,
    required bool correct,
    DateTime? now,
  }) {
    final queue = progress.reviewQueue;
    final idx = queue.indexWhere((r) => r.questionId == question.id);
    final today = dayKey(now ?? DateTime.now());

    if (!correct) {
      if (idx >= 0) {
        final item = queue[idx];
        item.priority = (item.priority + 1).clamp(1, maxPriority);
        item.ease = (item.ease - 0.2).clamp(minEase, 3.0);
        item.intervalDays = 1;
        item.dueDay = today; // re-review starting now
        item.lastReviewedDay = today;
      } else {
        queue.add(
          ReviewItem(
            questionId: question.id,
            skillId: question.skill,
            priority: 3 + question.difficulty.weight - 1, // 3..5 by difficulty
            intervalDays: 1,
            dueDay: today, // available to review immediately after a miss
            lastReviewedDay: today,
          ),
        );
      }
    } else if (idx >= 0) {
      final item = queue[idx];
      item.priority = (item.priority - 1).clamp(0, maxPriority);
      item.lastReviewedDay = today;
      item.ease = (item.ease + 0.1).clamp(minEase, 3.0);
      item.intervalDays = item.intervalDays <= 1
          ? 3
          : (item.intervalDays * item.ease).round();
      if (item.intervalDays >= graduateInterval) {
        queue.removeAt(idx); // well-learned: graduate out of the queue
      } else {
        item.dueDay = _addDays(today, item.intervalDays);
      }
    }
  }

  /// Whether an item is due for review on [today] (default: now).
  bool isDue(ReviewItem item, {DateTime? now}) {
    if (item.dueDay == null) return true;
    return _daysBetween(item.dueDay!, dayKey(now ?? DateTime.now())) >= 0;
  }

  /// Number of items due right now.
  int dueCount(AppProgress progress, {DateTime? now}) =>
      progress.reviewQueue.where((r) => isDue(r, now: now)).length;

  /// Question ids due for review, most urgent first (overdue + priority).
  List<String> dueQuestionIds(
    AppProgress progress, {
    int limit = 12,
    DateTime? now,
  }) {
    final today = dayKey(now ?? DateTime.now());
    final due = progress.reviewQueue.where((r) => isDue(r, now: now)).toList()
      ..sort((a, b) {
        final ao = a.dueDay == null ? 9999 : _daysBetween(a.dueDay!, today);
        final bo = b.dueDay == null ? 9999 : _daysBetween(b.dueDay!, today);
        if (ao != bo) return bo.compareTo(ao); // most overdue first
        return b.priority.compareTo(a.priority);
      });
    return due.take(limit).map((e) => e.questionId).toList();
  }

  /// Skills that most need work (lowest mastery first), for suggestions.
  List<String> weakestSkills(AppProgress progress, {int limit = 3}) {
    final entries = progress.skillMastery.values.toList()
      ..sort((a, b) => a.mastery.compareTo(b.mastery));
    return entries.take(limit).map((e) => e.skillId).toList();
  }
}
