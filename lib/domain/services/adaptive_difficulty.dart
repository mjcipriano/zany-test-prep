import 'dart:math' as math;

import '../models/difficulty.dart';

/// Picks question difficulty from mastery so practice sits at the edge of the
/// learner's ability (~70% expected correct).
///
/// The expected-correct model is a logistic curve per difficulty:
/// `p = 1 / (1 + e^-((mastery - center) / spread))`, centered at 20 / 50 / 80
/// mastery for easy / medium / hard. [forMastery] returns the difficulty whose
/// expected success is closest to [targetCorrect] (ties go to the easier one):
/// easy below ~51 mastery, medium up to ~81, hard above.
class AdaptiveDifficulty {
  const AdaptiveDifficulty({this.targetCorrect = 0.7, this.spread = 15});

  final double targetCorrect;
  final double spread;

  static double centerOf(Difficulty d) => switch (d) {
    Difficulty.easy => 20,
    Difficulty.medium => 50,
    Difficulty.hard => 80,
  };

  /// Modelled chance of answering a [d] question right at [mastery] (0-100).
  double expectedCorrect(double mastery, Difficulty d) =>
      1 / (1 + math.exp(-(mastery - centerOf(d)) / spread));

  Difficulty forMastery(double mastery) {
    var best = Difficulty.easy;
    var bestGap = double.infinity;
    for (final d in Difficulty.values) {
      final gap = (expectedCorrect(mastery, d) - targetCorrect).abs();
      if (gap < bestGap - 1e-9) {
        best = d;
        bestGap = gap;
      }
    }
    return best;
  }
}

/// In-session difficulty stepping: a transformed up/down staircase.
///
/// [upAfter] correct answers in a row step one level harder; [downAfter] wrong
/// answers in a row step one level easier. The default 2-up/1-down staircase
/// converges on ~71% correct (Levitt, 1971) — the same target as
/// [AdaptiveDifficulty]. The staircase is an [offset] applied on top of each
/// skill's mastery-based level, clamped to ±[maxOffset].
class DifficultyStaircase {
  DifficultyStaircase({
    this.upAfter = 2,
    this.downAfter = 1,
    this.maxOffset = 2,
  });

  final int upAfter;
  final int downAfter;
  final int maxOffset;

  int offset = 0;
  int _rightRun = 0;
  int _wrongRun = 0;

  /// Feeds one answer; returns the change in [offset] (-1, 0 or +1).
  int record(bool correct) {
    if (correct) {
      _wrongRun = 0;
      _rightRun += 1;
      if (_rightRun >= upAfter) {
        _rightRun = 0;
        return _step(1);
      }
    } else {
      _rightRun = 0;
      _wrongRun += 1;
      if (_wrongRun >= downAfter) {
        _wrongRun = 0;
        return _step(-1);
      }
    }
    return 0;
  }

  int _step(int by) {
    final next = (offset + by).clamp(-maxOffset, maxOffset);
    final moved = next - offset;
    offset = next;
    return moved;
  }

  /// [base] shifted by the current offset, clamped to easy..hard.
  Difficulty apply(Difficulty base) =>
      Difficulty.values[(base.index + offset).clamp(
        0,
        Difficulty.values.length - 1,
      )];
}
