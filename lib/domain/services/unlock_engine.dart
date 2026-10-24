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

  /// Lessons in path order: by the exam's domain order (as listed in the skill
  /// map), then by each lesson's `order`.
  List<Lesson> pathOrder(ContentBundle bundle) =>
      [...bundle.lessons]..sort((a, b) {
        final d = bundle
            .domainIndex(a.domain)
            .compareTo(bundle.domainIndex(b.domain));
        return d != 0 ? d : a.order.compareTo(b.order);
      });

  /// The next lesson to suggest: the first unlocked, not-yet-completed lesson
  /// in path order. Once everything is done, the lesson with the fewest crowns.
  Lesson? suggestNext(ContentBundle bundle, AppProgress progress) {
    final ordered = pathOrder(bundle);
    for (final l in ordered) {
      if (isUnlocked(l, progress) && !progress.isLessonCompleted(l.id)) {
        return l;
      }
    }
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
