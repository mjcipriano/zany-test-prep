import 'package:flutter_test/flutter_test.dart';
import 'package:zany_test_prep/domain/models/avatar_catalog.dart';
import 'package:zany_test_prep/domain/models/content_bundle.dart';
import 'package:zany_test_prep/domain/models/difficulty.dart';
import 'package:zany_test_prep/domain/models/exam.dart';
import 'package:zany_test_prep/domain/models/skill.dart';
import 'package:zany_test_prep/domain/models/lesson.dart';
import 'package:zany_test_prep/domain/models/profile.dart';
import 'package:zany_test_prep/domain/models/progress.dart';
import 'package:zany_test_prep/domain/models/question.dart';
import 'package:zany_test_prep/domain/models/reward.dart';
import 'package:zany_test_prep/domain/services/game_service.dart';
import 'package:zany_test_prep/domain/services/review_engine.dart';
import 'package:zany_test_prep/domain/services/rewards_service.dart';
import 'package:zany_test_prep/domain/services/streak_engine.dart';

Question _q(String id, String examId, {String skill = 'linear_equations'}) =>
    Question(
      id: id,
      examId: examId,
      domain: 'math',
      section: 's',
      skill: skill,
      lessonId: '$examId-math-l',
      difficulty: Difficulty.easy,
      type: QuestionType.multipleChoice,
      estimatedTimeSeconds: 30,
      prompt: 'p',
      explanation: 'e',
      tags: const [],
      choices: const [
        Choice(id: 'A', text: 'a', rationale: 'r'),
        Choice(id: 'B', text: 'b', rationale: 'r'),
      ],
      correctChoice: 'A',
    );

ContentBundle _bundle(String examId, List<Question> qs) => ContentBundle(
  exam: Exam0.make(examId),
  skillMap: SkillMap(domains: const []),
  lessons: [
    Lesson(
      id: '$examId-math-l',
      examId: examId,
      domain: 'math',
      section: 's',
      skill: 'linear_equations',
      title: 't',
      order: 0,
      difficulty: Difficulty.easy,
      estimatedMinutes: 5,
      teachingCard: const TeachingCard(title: 't', body: 'b', keyPoints: []),
      questionIds: qs.map((q) => q.id).toList(),
      prerequisiteLessonIds: const [],
      unlockXp: 0,
      tags: const [],
    ),
  ],
  questions: qs,
);

void main() {
  group('ReviewEngine scoped to the active exam', () {
    test('dueCount/dueQuestionIds ignore items from another exam', () {
      const engine = ReviewEngine();
      final progress = AppProgress();
      final now = DateTime(2025, 1, 10);
      // 15 overdue SAT misses with top priority…
      for (var i = 0; i < 15; i++) {
        engine.onAnswered(
          progress: progress,
          question: _q('sat-q$i', 'sat'),
          correct: false,
          now: now.subtract(const Duration(days: 5)),
        );
      }
      // …and 3 fresh ACT misses.
      final actQs = [for (var i = 0; i < 3; i++) _q('act-q$i', 'act')];
      for (final q in actQs) {
        engine.onAnswered(
          progress: progress,
          question: q,
          correct: false,
          now: now,
        );
      }
      final act = _bundle('act', actQs);

      expect(engine.dueCount(progress, now: now), 18);
      expect(engine.dueCount(progress, now: now, bundle: act), 3);
      final ids = engine.dueQuestionIds(progress, now: now, bundle: act);
      expect(ids.toSet(), {'act-q0', 'act-q1', 'act-q2'});
      // Unscoped, the 12 most urgent are all SAT — the old dead-end.
      final unscoped = engine.dueQuestionIds(progress, now: now, limit: 12);
      expect(unscoped.every((id) => id.startsWith('sat-')), isTrue);
    });

    test('review items store the exam-scoped mastery key', () {
      const engine = ReviewEngine();
      final progress = AppProgress();
      engine.onAnswered(
        progress: progress,
        question: _q('a', 'act'),
        correct: false,
      );
      engine.onAnswered(
        progress: progress,
        question: _q('s', 'sat'),
        correct: false,
      );
      expect(progress.reviewQueue[0].skillId, 'act:linear_equations');
      expect(progress.reviewQueue[1].skillId, 'linear_equations');
    });
  });

  group('mastery is scoped per exam', () {
    test('masteryKey keeps bare ids for the SAT and prefixes other exams', () {
      expect(masteryKey('sat', 'main_idea'), 'main_idea');
      expect(masteryKey('act', 'main_idea'), 'act:main_idea');
      expect(skillIdOfMasteryKey('act:main_idea'), 'main_idea');
      expect(skillIdOfMasteryKey('main_idea'), 'main_idea');
      expect(masteryKeyFor(_q('x', 'act')), 'act:linear_equations');
    });

    test('answering ACT questions does not move SAT mastery', () {
      const game = GameService();
      final progress = AppProgress();
      progress.mastery('linear_equations').mastery = 90;
      final act = _bundle('act', [_q('a1', 'act')]);
      game.applyPracticeResult(
        progress: progress,
        profile: UserProfile.initial('act', 10),
        results: [AnswerResult(question: _q('a1', 'act'), correct: false)],
        bundle: act,
      );
      expect(progress.mastery('linear_equations').mastery, 90);
      expect(
        progress.skillMastery['act:linear_equations']!.mastery,
        lessThan(90),
      );
    });

    test('diagnostic completion is tracked per exam (legacy flag = SAT)', () {
      final g = GameState();
      expect(g.diagnosticDoneFor('sat'), isFalse);
      g.markDiagnosticDone('act');
      expect(g.diagnosticDoneFor('act'), isTrue);
      expect(g.diagnosticDoneFor('sat'), isFalse);
      g.markDiagnosticDone('sat');
      expect(g.diagnosticDone, isTrue);
      final round = GameState.fromJson(g.toJson());
      expect(round.diagnosticDoneFor('act'), isTrue);
      expect(round.diagnosticDoneFor('sat'), isTrue);
      // An old document with only the legacy flag still counts for the SAT.
      final legacy = GameState.fromJson({'diagnosticDone': true});
      expect(legacy.diagnosticDoneFor('sat'), isTrue);
      expect(legacy.diagnosticDoneFor('act'), isFalse);
    });
  });

  group('day arithmetic is calendar-based, not wall-clock', () {
    test('consecutive days are always one day apart (incl. DST weekends)', () {
      for (final start in [
        DateTime.utc(2024, 3, 9),
        DateTime.utc(2024, 11, 2),
        DateTime.utc(2024, 2, 28),
        DateTime.utc(2024, 12, 31),
      ]) {
        final a = dayKey(start);
        final b = dayKey(start.add(const Duration(days: 1)));
        expect(daysBetweenDayKeys(a, b), 1, reason: '$a -> $b');
        expect(daysBetweenDayKeys(b, a), -1);
        expect(addDaysToDayKey(a, 1), b);
      }
      expect(daysBetweenDayKeys('2024-03-01', '2024-03-31'), 30);
      expect(addDaysToDayKey('2024-02-28', 2), '2024-03-01');
    });

    test('streak extends across the spring-forward night', () {
      const engine = StreakEngine();
      final r = engine.registerActivity(
        lastActiveDay: '2024-03-09',
        currentStreak: 4,
        longestStreak: 4,
        today: DateTime(2024, 3, 10, 9),
      );
      expect(r.extended, isTrue);
      expect(r.currentStreak, 5);
    });
  });

  group('rewards robustness', () {
    test('an empty avatar catalog renders no layers instead of throwing', () {
      const rewards = RewardsService();
      final empty = AvatarCatalog.empty();
      expect(rewards.selectedAvatar(GameState(), empty), isNull);
      expect(rewards.equippedLayers(GameState(), empty), isEmpty);
    });

    test(
      'a smaller XP boost never downgrades a bigger one on the same day',
      () {
        const rewards = RewardsService();
        final g = GameState();
        final now = DateTime(2025, 1, 1);
        rewards.applyReward(g, const XpBoostReward(2.0), now: now);
        rewards.applyReward(g, const XpBoostReward(1.5), now: now);
        expect(g.xpBoostMultiplier, 2.0);
        rewards.applyReward(
          g,
          const XpBoostReward(1.5),
          now: now.add(const Duration(days: 3)),
        );
        expect(g.xpBoostMultiplier, 1.5);
      },
    );
  });

  test('best score resets when a lesson changes length', () {
    const game = GameService();
    final progress = AppProgress();
    final qs = [for (var i = 0; i < 4; i++) _q('q$i', 'sat')];
    final bundle = _bundle('sat', qs);
    final lesson = bundle.lessons.single;
    final profile = UserProfile.initial('sat', 10);
    game.applyLessonResult(
      progress: progress,
      profile: profile,
      lesson: lesson,
      results: [for (final q in qs) AnswerResult(question: q, correct: true)],
      bundle: bundle,
    );
    expect(progress.lessons[lesson.id]!.bestCorrect, 4);
    game.applyLessonResult(
      progress: progress,
      profile: profile,
      lesson: lesson,
      results: [
        AnswerResult(question: qs[0], correct: false),
        AnswerResult(question: qs[1], correct: true),
      ],
      bundle: bundle,
    );
    final lp = progress.lessons[lesson.id]!;
    expect(lp.total, 2);
    expect(lp.bestCorrect, lessThanOrEqualTo(lp.total));
  });
}

/// Minimal exam factory for tests.
extension Exam0 on Exam {
  static Exam make(String id) => Exam(
    id: id,
    name: id.toUpperCase(),
    displayName: id.toUpperCase(),
    enabled: true,
    contentVersion: '1',
    description: '',
    domains: const ['math'],
  );
}
