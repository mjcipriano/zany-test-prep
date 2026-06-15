import 'dart:math' as math;

import '../models/difficulty.dart';

/// XP awards. Deterministic and pure so they are easy to unit-test.
class XpEngine {
  const XpEngine();

  /// XP for a single answer. Harder questions are worth more.
  int xpForAnswer({
    required bool correct,
    required Difficulty difficulty,
    bool isReview = false,
  }) {
    if (!correct) return 0;
    final base = 5 * difficulty.weight; // easy 5, medium 10, hard 15
    if (isReview) return (base * 0.6).round();
    return base;
  }

  /// Bonus for finishing a lesson at all.
  int get lessonCompletionBonus => 20;

  /// Extra bonus for a flawless lesson.
  int get perfectLessonBonus => 15;

  /// Total XP for a finished lesson given per-answer results.
  int xpForLesson({
    required List<bool> results,
    required List<Difficulty> difficulties,
    bool isReview = false,
  }) {
    assert(results.length == difficulties.length);
    var xp = 0;
    for (var i = 0; i < results.length; i++) {
      xp += xpForAnswer(
        correct: results[i],
        difficulty: difficulties[i],
        isReview: isReview,
      );
    }
    if (results.isNotEmpty) {
      xp += lessonCompletionBonus;
      if (results.every((r) => r)) xp += perfectLessonBonus;
    }
    return xp;
  }
}

/// Maps total XP to a level and exposes progress within the current level.
class LevelEngine {
  const LevelEngine();

  /// XP increment required to go from [level] to [level]+1 (level >= 1).
  int _incrementToNext(int level) => 100 + (level - 1) * 25;

  /// Cumulative XP needed to *reach* [level] (level 1 == 0 XP).
  int xpToReach(int level) {
    var total = 0;
    for (var l = 1; l < level; l++) {
      total += _incrementToNext(l);
    }
    return total;
  }

  /// The level for a given total XP (>= 1).
  int levelForXp(int totalXp) {
    var level = 1;
    while (totalXp >= xpToReach(level + 1)) {
      level++;
    }
    return level;
  }

  /// XP accumulated within the current level.
  int xpIntoLevel(int totalXp) {
    final level = levelForXp(totalXp);
    return totalXp - xpToReach(level);
  }

  /// XP required to advance from the current level to the next.
  int xpForNextLevel(int totalXp) {
    final level = levelForXp(totalXp);
    return _incrementToNext(level);
  }

  /// Fraction (0..1) of progress toward the next level.
  double progressToNext(int totalXp) {
    final into = xpIntoLevel(totalXp);
    final need = xpForNextLevel(totalXp);
    if (need <= 0) return 0;
    return math.min(1.0, into / need);
  }
}
