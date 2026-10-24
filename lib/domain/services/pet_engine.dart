/// Pet companion progression: pets gain XP while they are equipped and level
/// up through fixed thresholds; reaching a stage's `requires_level` lets the
/// pet evolve into its next catalog stage (Shiny → Radiant). Pure functions so
/// the economy is easy to tune and test.
class PetEngine {
  const PetEngine();

  /// Highest pet level.
  static const int maxLevel = 10;

  /// Cumulative pet XP needed to *reach* each level (index = level - 1).
  static const List<int> thresholds = [
    0, // level 1
    40, // 2
    100, // 3
    180, // 4
    280, // 5  -> Shiny
    400, // 6
    540, // 7
    700, // 8
    880, // 9
    1080, // 10 -> Radiant
  ];

  /// Pet XP earned per answered question while a pet is equipped.
  static const int xpPerCorrect = 4;
  static const int xpPerWrong = 1;

  /// Bonus pet XP for finishing any session (lesson, practice, review, test).
  static const int sessionBonus = 10;

  int levelForXp(int xp) {
    var level = 1;
    for (var i = 1; i < thresholds.length; i++) {
      if (xp >= thresholds[i]) level = i + 1;
    }
    return level;
  }

  /// XP earned since the current level began.
  int xpIntoLevel(int xp) => xp - thresholds[levelForXp(xp) - 1];

  /// XP span of the current level (0 at max level).
  int xpForNextLevel(int xp) {
    final level = levelForXp(xp);
    if (level >= maxLevel) return 0;
    return thresholds[level] - thresholds[level - 1];
  }

  /// Progress within the current level, 0..1 (1 at max level).
  double progressInLevel(int xp) {
    final span = xpForNextLevel(xp);
    return span == 0 ? 1 : (xpIntoLevel(xp) / span).clamp(0, 1).toDouble();
  }

  /// Pet XP for a session with [correct] right answers out of [total].
  int xpForSession({required int correct, required int total}) {
    if (total <= 0) return 0;
    return correct * xpPerCorrect +
        (total - correct) * xpPerWrong +
        sessionBonus;
  }
}
