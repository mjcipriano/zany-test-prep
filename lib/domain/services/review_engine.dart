import '../models/progress.dart';
import '../models/question.dart';

/// Manages the spaced-review queue: missed questions go in, repeated correct
/// review answers bring their priority down until they leave the queue.
class ReviewEngine {
  const ReviewEngine();

  static const int maxPriority = 5;

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
      } else {
        queue.add(
          ReviewItem(
            questionId: question.id,
            skillId: question.skill,
            priority: 3 + question.difficulty.weight - 1, // 3..5 by difficulty
          ),
        );
      }
    } else if (idx >= 0) {
      final item = queue[idx];
      item.priority -= 1;
      item.lastReviewedDay = today;
      if (item.priority <= 0) {
        queue.removeAt(idx);
      }
    }
  }

  /// Question ids due for review, highest priority first.
  List<String> dueQuestionIds(AppProgress progress, {int limit = 12}) {
    final sorted = [...progress.reviewQueue]
      ..sort((a, b) => b.priority.compareTo(a.priority));
    return sorted.take(limit).map((e) => e.questionId).toList();
  }

  int get queueLength => 0; // convenience overridden by callers via progress

  /// Skills that most need work (lowest mastery first), for suggestions.
  List<String> weakestSkills(AppProgress progress, {int limit = 3}) {
    final entries = progress.skillMastery.values.toList()
      ..sort((a, b) => a.mastery.compareTo(b.mastery));
    return entries.take(limit).map((e) => e.skillId).toList();
  }
}
