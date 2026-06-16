import 'package:flutter_test/flutter_test.dart';
import 'package:zany_test_prep/domain/models/content_bundle.dart';
import 'package:zany_test_prep/domain/models/difficulty.dart';
import 'package:zany_test_prep/domain/models/exam.dart';
import 'package:zany_test_prep/domain/models/lesson.dart';
import 'package:zany_test_prep/domain/models/profile.dart';
import 'package:zany_test_prep/domain/models/progress.dart';
import 'package:zany_test_prep/domain/models/question.dart';
import 'package:zany_test_prep/domain/models/skill.dart';
import 'package:zany_test_prep/domain/services/game_service.dart';

Question _q(String id, Difficulty d) => Question(
  id: id,
  examId: 'sat',
  domain: 'math',
  section: 'algebra',
  skill: 'linear_equations',
  lessonId: 'sat-math-linear-equations-1',
  difficulty: d,
  type: QuestionType.multipleChoice,
  estimatedTimeSeconds: 60,
  prompt: 'p',
  explanation: 'e',
  tags: const ['t'],
  choices: const [Choice(id: 'A', text: '1', rationale: 'r')],
  correctChoice: 'A',
);

final _lesson = const Lesson(
  id: 'sat-math-linear-equations-1',
  examId: 'sat',
  domain: 'math',
  section: 'algebra',
  skill: 'linear_equations',
  title: 'Linear Equations',
  order: 0,
  difficulty: Difficulty.easy,
  estimatedMinutes: 5,
  teachingCard: TeachingCard(title: 't', body: 'b', keyPoints: ['a', 'b']),
  questionIds: ['q1', 'q2'],
  prerequisiteLessonIds: [],
  unlockXp: 0,
  tags: ['math'],
);

ContentBundle _bundle() => ContentBundle(
  exam: const Exam(
    id: 'sat',
    name: 'SAT',
    displayName: 'SAT',
    enabled: true,
    contentVersion: '1.0.0',
    description: 'd',
    domains: ['math'],
  ),
  skillMap: SkillMap(domains: const []),
  lessons: [_lesson],
  questions: [_q('q1', Difficulty.easy), _q('q2', Difficulty.medium)],
);

void main() {
  const service = GameService();

  test(
    'perfect lesson awards xp, 3 stars, streak, badge, and updates mastery',
    () {
      final progress = AppProgress();
      final profile = UserProfile.initial('sat', 10);
      final bundle = _bundle();
      final results = [
        AnswerResult(question: _q('q1', Difficulty.easy), correct: true),
        AnswerResult(question: _q('q2', Difficulty.medium), correct: true),
      ];
      final out = service.applyLessonResult(
        progress: progress,
        profile: profile,
        lesson: _lesson,
        results: results,
        bundle: bundle,
        now: DateTime(2026, 6, 1),
      );

      // xp = 5 (easy) + 10 (medium) + 20 (completion) + 15 (perfect) = 50
      expect(out.xpGained, 50);
      expect(progress.game.totalXp, 50);
      expect(out.stars, 3);
      expect(out.correct, 2);
      expect(out.currentStreak, 1);
      expect(progress.isLessonCompleted(_lesson.id), isTrue);
      expect(progress.lessons[_lesson.id]!.stars, 3);
      expect(progress.mastery('linear_equations').mastery, greaterThan(0));
      expect(out.newBadges.map((b) => b.id), contains('first_lesson'));
      expect(progress.reviewQueue, isEmpty); // nothing missed
    },
  );

  test('a missed question lowers stars and enqueues review', () {
    final progress = AppProgress();
    final profile = UserProfile.initial('sat', 10);
    final out = service.applyLessonResult(
      progress: progress,
      profile: profile,
      lesson: _lesson,
      results: [
        AnswerResult(question: _q('q1', Difficulty.easy), correct: true),
        AnswerResult(question: _q('q2', Difficulty.medium), correct: false),
      ],
      bundle: _bundle(),
      now: DateTime(2026, 6, 1),
    );
    // accuracy 0.5 -> 0 stars; xp = 5 + 0 + 20 = 25
    expect(out.stars, 0);
    expect(out.xpGained, 25);
    expect(progress.reviewQueue.length, 1);
    expect(progress.reviewQueue.first.questionId, 'q2');
  });

  test('daily goal is detected once enough XP is earned in a day', () {
    final progress = AppProgress();
    final profile = UserProfile.initial('sat', 5); // goal = 100 XP
    List<AnswerResult> perfect() => [
      AnswerResult(question: _q('q1', Difficulty.easy), correct: true),
      AnswerResult(question: _q('q2', Difficulty.medium), correct: true),
    ];
    final day = DateTime(2026, 6, 1);
    // One perfect lesson = 50 XP — below the 100 XP goal.
    final first = service.applyLessonResult(
      progress: progress,
      profile: profile,
      lesson: _lesson,
      results: perfect(),
      bundle: _bundle(),
      now: day,
    );
    expect(first.dailyGoalMet, isFalse);
    // A second lesson the same day pushes daily XP to 100 — goal reached.
    final second = service.applyLessonResult(
      progress: progress,
      profile: profile,
      lesson: _lesson,
      results: perfect(),
      bundle: _bundle(),
      now: day,
    );
    expect(second.dailyGoalMet, isTrue);
    expect(second.dailyGoalJustMet, isTrue);
  });

  test('meeting the daily goal grants exactly one chest for the day', () {
    final progress = AppProgress();
    final profile = UserProfile.initial('sat', 5); // goal = 100 XP
    List<AnswerResult> perfect() => [
      AnswerResult(question: _q('q1', Difficulty.easy), correct: true),
      AnswerResult(question: _q('q2', Difficulty.medium), correct: true),
    ];
    final day = DateTime(2026, 6, 1);
    final first = service.applyLessonResult(
      progress: progress,
      profile: profile,
      lesson: _lesson,
      results: perfect(),
      bundle: _bundle(),
      now: day,
    );
    expect(first.chestEarned, isFalse);
    expect(progress.game.unopenedChests, 0);
    final second = service.applyLessonResult(
      progress: progress,
      profile: profile,
      lesson: _lesson,
      results: perfect(),
      bundle: _bundle(),
      now: day,
    );
    expect(second.chestEarned, isTrue);
    expect(progress.game.unopenedChests, 1);
    // A third lesson the same day does not grant another chest.
    final third = service.applyLessonResult(
      progress: progress,
      profile: profile,
      lesson: _lesson,
      results: perfect(),
      bundle: _bundle(),
      now: day,
    );
    expect(third.chestEarned, isFalse);
    expect(progress.game.unopenedChests, 1);
  });

  test('an active XP boost multiplies the day\'s earnings', () {
    final progress = AppProgress();
    final profile = UserProfile.initial('sat', 10);
    final day = DateTime(2026, 6, 1);
    progress.game.xpBoostMultiplier = 2.0;
    progress.game.xpBoostDay = dayKey(day);
    final out = service.applyLessonResult(
      progress: progress,
      profile: profile,
      lesson: _lesson,
      results: [
        AnswerResult(question: _q('q1', Difficulty.easy), correct: true),
        AnswerResult(question: _q('q2', Difficulty.medium), correct: true),
      ],
      bundle: _bundle(),
      now: day,
    );
    // Base perfect lesson = 50 XP; boosted 2x = 100.
    expect(out.xpBoosted, isTrue);
    expect(out.xpGained, 100);
    expect(progress.game.totalXp, 100);
  });
}
