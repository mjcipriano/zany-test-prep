import 'package:flutter_test/flutter_test.dart';
import 'package:zany_test_prep/domain/models/progress.dart';
import 'package:zany_test_prep/domain/services/streak_engine.dart';

void main() {
  const engine = StreakEngine();
  final mon = DateTime(2026, 6, 1);
  final tue = DateTime(2026, 6, 2);
  final wed = DateTime(2026, 6, 3);
  final fri = DateTime(2026, 6, 5);

  test('first activity starts streak at 1', () {
    final r = engine.registerActivity(
        lastActiveDay: null, currentStreak: 0, longestStreak: 0, today: mon);
    expect(r.currentStreak, 1);
    expect(r.longestStreak, 1);
    expect(r.extended, isTrue);
    expect(r.lastActiveDay, dayKey(mon));
  });

  test('consecutive day extends streak', () {
    final r = engine.registerActivity(
        lastActiveDay: dayKey(mon), currentStreak: 1, longestStreak: 1, today: tue);
    expect(r.currentStreak, 2);
    expect(r.longestStreak, 2);
    expect(r.extended, isTrue);
    expect(r.reset, isFalse);
  });

  test('same day does not change streak', () {
    final r = engine.registerActivity(
        lastActiveDay: dayKey(tue), currentStreak: 2, longestStreak: 5, today: tue);
    expect(r.currentStreak, 2);
    expect(r.longestStreak, 5);
    expect(r.extended, isFalse);
  });

  test('missing a day resets the streak to 1', () {
    final r = engine.registerActivity(
        lastActiveDay: dayKey(wed), currentStreak: 4, longestStreak: 4, today: fri);
    expect(r.currentStreak, 1);
    expect(r.reset, isTrue);
    expect(r.longestStreak, 4); // longest preserved
  });

  test('displayedStreak shows 0 after a fully missed day', () {
    expect(
        engine.displayedStreak(
            lastActiveDay: dayKey(wed), currentStreak: 4, today: fri),
        0);
    expect(
        engine.displayedStreak(
            lastActiveDay: dayKey(tue), currentStreak: 4, today: wed),
        4);
  });
}
