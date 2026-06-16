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
}
