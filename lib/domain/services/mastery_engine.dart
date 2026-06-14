import '../models/difficulty.dart';

/// Simple, explainable skill-mastery model (0-100 per skill).
///
/// - A correct answer raises mastery; harder questions raise it more.
/// - A wrong answer lowers mastery, but by less than a correct one raises it,
///   so progress is "sticky" yet responsive.
/// - Review answers move mastery a bit less (the item has been seen before).
class MasteryEngine {
  const MasteryEngine();

  double update({
    required double current,
    required bool correct,
    required Difficulty difficulty,
    bool isReview = false,
  }) {
    final w = difficulty.weight; // 1..3
    double next;
    if (correct) {
      final gain = (4.0 * w) * (isReview ? 0.75 : 1.0); // easy4 med8 hard12
      next = current + gain;
    } else {
      final loss = 2.0 * w; // easy2 med4 hard6 (gentler than the gain)
      next = current - loss;
    }
    return next.clamp(0, 100).toDouble();
  }

  /// Average mastery across the supplied skills (0 if empty).
  double overall(Iterable<double> masteries) {
    final list = masteries.toList();
    if (list.isEmpty) return 0;
    return list.reduce((a, b) => a + b) / list.length;
  }

  /// A coarse label for UI.
  String label(double mastery) {
    if (mastery >= 80) return 'Mastered';
    if (mastery >= 50) return 'Proficient';
    if (mastery >= 20) return 'Developing';
    return 'New';
  }
}
