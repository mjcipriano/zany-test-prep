import 'package:flutter/material.dart';
import 'package:flutter_test/flutter_test.dart';
import 'package:zany_test_prep/data/local/key_value_store.dart';
import 'package:zany_test_prep/data/repositories/progress_repository.dart';
import 'package:zany_test_prep/domain/models/profile.dart';
import 'package:zany_test_prep/domain/models/progress.dart';

void main() {
  test('profile round-trips through storage', () async {
    final store = MemoryStore();
    final repo = ProgressRepository(store);
    final profile = UserProfile.initial('sat', 15);
    await repo.saveProfile(profile);

    final loaded = ProgressRepository(store).loadProfile();
    expect(loaded, isNotNull);
    expect(loaded!.examId, 'sat');
    expect(loaded.dailyGoalMinutes, 15);
    expect(loaded.dailyGoalXp, 300);
  });

  test('progress (xp, streak, lessons, mastery, review) round-trips', () async {
    final store = MemoryStore();
    final repo = ProgressRepository(store);

    final progress = AppProgress();
    progress.game.totalXp = 130;
    progress.game.currentStreak = 4;
    progress.game.earnedBadges.add('first_lesson');
    progress.lessonProgress('l1')
      ..completed = true
      ..stars = 3;
    progress.mastery('linear_equations').mastery = 42;
    progress.reviewQueue.add(ReviewItem(questionId: 'q9', skillId: 's1'));
    await repo.saveProgress(progress);

    // Simulate a fresh app launch by reading with a new repository.
    final loaded = ProgressRepository(store).loadProgress();
    expect(loaded.game.totalXp, 130);
    expect(loaded.game.currentStreak, 4);
    expect(loaded.game.earnedBadges, contains('first_lesson'));
    expect(loaded.isLessonCompleted('l1'), isTrue);
    expect(loaded.lessons['l1']!.stars, 3);
    expect(loaded.mastery('linear_equations').mastery, 42);
    expect(loaded.reviewQueue.single.questionId, 'q9');
  });

  test('reset clears profile, progress, and onboarding flag', () async {
    final store = MemoryStore();
    final repo = ProgressRepository(store);
    await repo.saveProfile(UserProfile.initial('sat', 10));
    await repo.setOnboarded(true);
    expect(repo.isOnboarded, isTrue);

    await repo.resetAll();
    expect(repo.isOnboarded, isFalse);
    expect(repo.loadProfile(), isNull);
    expect(repo.loadProgress().game.totalXp, 0);
  });

  group('update resilience (no crash, valid settings preserved)', () {
    test('corrupt JSON falls back to defaults instead of crashing', () async {
      final store = MemoryStore();
      await store.setString('progress.v1', '{not valid json');
      await store.setString('profile.v1', 'totally broken');
      final repo = ProgressRepository(store);
      expect(repo.loadProfile(), isNull); // -> re-onboard, not a crash
      expect(repo.loadProgress().game.totalXp, 0); // -> fresh progress
    });

    test('wrong-typed fields are coerced/defaulted, not fatal', () async {
      final store = MemoryStore();
      // Numbers as strings, ints as doubles, a bool as a string, a null set.
      await store.setString(
        'progress.v1',
        '{"game":{"totalXp":"1500","spentXp":250.0,'
            '"diagnosticDone":"true","streakFreezes":2,'
            '"ownedAssetIds":null,"xpBoostMultiplier":"2.0"}}',
      );
      final progress = ProgressRepository(store).loadProgress();
      expect(progress.game.totalXp, 1500);
      expect(progress.game.spentXp, 250);
      expect(progress.game.availableXp, 1250);
      expect(progress.game.diagnosticDone, isTrue);
      expect(progress.game.streakFreezes, 2);
      expect(progress.game.ownedAssetIds, isEmpty);
      expect(progress.game.xpBoostMultiplier, 2.0);
    });

    test('a single corrupt collection entry is skipped, not fatal', () async {
      final store = MemoryStore();
      await store.setString(
        'progress.v1',
        '{"lessons":{"good":{"lessonId":"good","completed":true,"stars":3},'
            '"bad":"not a map"},"reviewQueue":[{"questionId":"q1","skillId":"s1"},42]}',
      );
      final progress = ProgressRepository(store).loadProgress();
      expect(progress.isLessonCompleted('good'), isTrue);
      expect(progress.lessons.containsKey('bad'), isFalse);
      expect(progress.reviewQueue.single.questionId, 'q1');
    });

    test('unknown future fields are ignored; known settings round-trip', () {
      final store = MemoryStore();
      final repo = ProgressRepository(store);
      final profile = UserProfile.initial(
        'sat',
        15,
      ).copyWith(soundOn: false, themeMode: ThemeMode.dark);
      repo.saveProfile(profile);
      // Simulate a value written by a *newer* app version with extra keys.
      final raw = store
          .getString('profile.v1')!
          .replaceFirst('{', '{"futureFeatureFlag":true,');
      store.setString('profile.v1', raw);

      final loaded = ProgressRepository(store).loadProfile()!;
      expect(loaded.dailyGoalMinutes, 15);
      expect(loaded.soundOn, isFalse);
      expect(loaded.themeMode, ThemeMode.dark);
    });

    test('missing rewards fields default cleanly for old saves', () async {
      final store = MemoryStore();
      // An "old" progress doc from before the rewards system existed.
      await store.setString(
        'progress.v1',
        '{"game":{"totalXp":300,"currentStreak":4,"earnedBadges":["first_lesson"]}}',
      );
      final progress = ProgressRepository(store).loadProgress();
      expect(progress.game.totalXp, 300);
      expect(progress.game.currentStreak, 4);
      expect(progress.game.earnedBadges, contains('first_lesson'));
      // New fields take safe defaults.
      expect(progress.game.spentXp, 0);
      expect(progress.game.streakFreezes, 0);
      expect(progress.game.unopenedChests, 0);
      expect(progress.game.ownedAssetIds, isEmpty);
      expect(progress.game.availableXp, 300);
    });
  });
}
