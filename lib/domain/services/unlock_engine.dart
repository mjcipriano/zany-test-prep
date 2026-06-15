import '../models/content_bundle.dart';
import '../models/lesson.dart';
import '../models/progress.dart';

/// Decides which lessons are unlocked and which to suggest next.
class UnlockEngine {
  const UnlockEngine();

  /// A lesson is unlocked when every prerequisite lesson is completed and the
  /// learner has enough total XP. Lessons with no prerequisites and 0 unlock_xp
  /// are available from the start.
  bool isUnlocked(Lesson lesson, AppProgress progress) {
    if (progress.game.totalXp < lesson.unlockXp) return false;
    for (final pre in lesson.prerequisiteLessonIds) {
      if (!progress.isLessonCompleted(pre)) return false;
    }
    return true;
  }

  /// The next lesson to suggest: the first unlocked, not-yet-completed lesson,
  /// preferring the learner's currently active domain order. Falls back to the
  /// first incomplete lesson overall.
  Lesson? suggestNext(ContentBundle bundle, AppProgress progress) {
    final ordered = [...bundle.lessons]
      ..sort((a, b) {
        final d = (a.domain == 'reading_writing' ? 0 : 1).compareTo(
          b.domain == 'reading_writing' ? 0 : 1,
        );
        return d != 0 ? d : a.order.compareTo(b.order);
      });
    for (final l in ordered) {
      if (isUnlocked(l, progress) && !progress.isLessonCompleted(l.id)) {
        return l;
      }
    }
    // Everything done — suggest the lesson with the lowest stars to improve.
    Lesson? weakest;
    var minStars = 4;
    for (final l in ordered) {
      final stars = progress.lessons[l.id]?.stars ?? 0;
      if (stars < minStars) {
        minStars = stars;
        weakest = l;
      }
    }
    return weakest;
  }
}
