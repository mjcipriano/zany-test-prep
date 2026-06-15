import 'package:flutter_test/flutter_test.dart';
import 'package:zany_test_prep/domain/models/difficulty.dart';
import 'package:zany_test_prep/domain/services/leveling.dart';

void main() {
  group('XpEngine', () {
    const xp = XpEngine();
    test('xp scales with difficulty for correct answers', () {
      expect(xp.xpForAnswer(correct: true, difficulty: Difficulty.easy), 5);
      expect(xp.xpForAnswer(correct: true, difficulty: Difficulty.medium), 10);
      expect(xp.xpForAnswer(correct: true, difficulty: Difficulty.hard), 15);
    });
    test('wrong answers earn no xp', () {
      expect(xp.xpForAnswer(correct: false, difficulty: Difficulty.hard), 0);
    });
    test('review answers earn reduced xp', () {
      expect(
        xp.xpForAnswer(
          correct: true,
          difficulty: Difficulty.medium,
          isReview: true,
        ),
        6,
      ); // 10 * 0.6
    });
    test('lesson xp includes completion and perfect bonuses', () {
      final perfect = xp.xpForLesson(
        results: const [true, true],
        difficulties: const [Difficulty.easy, Difficulty.easy],
      );
      // 5 + 5 + 20 (completion) + 15 (perfect) = 45
      expect(perfect, 45);

      final imperfect = xp.xpForLesson(
        results: const [true, false],
        difficulties: const [Difficulty.easy, Difficulty.easy],
      );
      // 5 + 0 + 20 = 25 (no perfect bonus)
      expect(imperfect, 25);
    });
  });

  group('LevelEngine', () {
    const lvl = LevelEngine();
    test('level 1 starts at 0 xp', () {
      expect(lvl.levelForXp(0), 1);
      expect(lvl.xpToReach(1), 0);
    });
    test('thresholds increase by a growing increment', () {
      expect(lvl.xpToReach(2), 100);
      expect(lvl.xpToReach(3), 225); // 100 + 125
      expect(lvl.xpToReach(4), 375); // + 150
    });
    test('levelForXp is monotonic across thresholds', () {
      expect(lvl.levelForXp(99), 1);
      expect(lvl.levelForXp(100), 2);
      expect(lvl.levelForXp(224), 2);
      expect(lvl.levelForXp(225), 3);
    });
    test('progress within level is between 0 and 1', () {
      final p = lvl.progressToNext(150); // level 2, 50 into a 125 band
      expect(p, closeTo(50 / 125, 1e-9));
      expect(lvl.xpIntoLevel(150), 50);
      expect(lvl.xpForNextLevel(150), 125);
    });
  });
}
