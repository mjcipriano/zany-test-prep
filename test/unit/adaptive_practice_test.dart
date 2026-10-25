import 'dart:math';

import 'package:flutter_test/flutter_test.dart';
import 'package:zany_test_prep/domain/models/difficulty.dart';
import 'package:zany_test_prep/domain/models/progress.dart';
import 'package:zany_test_prep/domain/services/adaptive_difficulty.dart';
import 'package:zany_test_prep/domain/services/smart_practice.dart';

import '../helpers/adaptive_fixtures.dart';

final _now = DateTime(2026, 5, 10, 18);

void main() {
  group('AdaptiveDifficulty', () {
    const a = AdaptiveDifficulty();

    test('picks the level closest to ~70% expected correct', () {
      expect(a.forMastery(0), Difficulty.easy);
      expect(a.forMastery(30), Difficulty.easy);
      expect(a.forMastery(50), Difficulty.easy);
      expect(a.forMastery(55), Difficulty.medium);
      expect(a.forMastery(70), Difficulty.medium);
      expect(a.forMastery(85), Difficulty.hard);
      expect(a.forMastery(100), Difficulty.hard);
    });

    test('expected success falls with difficulty and rises with mastery', () {
      expect(
        a.expectedCorrect(50, Difficulty.easy),
        greaterThan(a.expectedCorrect(50, Difficulty.hard)),
      );
      expect(
        a.expectedCorrect(80, Difficulty.medium),
        greaterThan(a.expectedCorrect(40, Difficulty.medium)),
      );
      // In the medium band the pick sits near the 70% target.
      expect(a.expectedCorrect(65, Difficulty.medium), closeTo(0.7, 0.05));
    });
  });

  group('DifficultyStaircase (2-up / 1-down)', () {
    test('two right in a row step up; one wrong steps down', () {
      final s = DifficultyStaircase();
      expect(s.record(true), 0);
      expect(s.record(true), 1);
      expect(s.offset, 1);
      expect(s.apply(Difficulty.easy), Difficulty.medium);
      expect(s.record(false), -1);
      expect(s.offset, 0);
      expect(s.record(false), -1);
      expect(s.apply(Difficulty.medium), Difficulty.easy);
    });

    test('a miss resets the run of correct answers', () {
      final s = DifficultyStaircase();
      s.record(true);
      s.record(false); // -1
      s.record(true);
      expect(s.offset, -1);
      s.record(true);
      expect(s.offset, 0);
    });

    test('offset and levels are clamped', () {
      final s = DifficultyStaircase();
      for (var i = 0; i < 20; i++) {
        s.record(true);
      }
      expect(s.offset, 2);
      expect(s.apply(Difficulty.medium), Difficulty.hard);
      for (var i = 0; i < 20; i++) {
        s.record(false);
      }
      expect(s.offset, -2);
      expect(s.apply(Difficulty.hard), Difficulty.easy);
    });

    test('custom streak lengths', () {
      final s = DifficultyStaircase(upAfter: 3, downAfter: 2);
      s.record(true);
      s.record(true);
      expect(s.offset, 0);
      s.record(true);
      expect(s.offset, 1);
      s.record(false);
      expect(s.offset, 1);
      s.record(false);
      expect(s.offset, 0);
    });

    test('converges on roughly 70% correct for a simulated learner', () {
      // A learner who gets 95% / 75% / 40% right on easy / medium / hard.
      const pRight = [0.95, 0.75, 0.40];
      final rng = Random(7);
      final s = DifficultyStaircase();
      var right = 0;
      const n = 4000;
      for (var i = 0; i < n; i++) {
        final level = s.apply(Difficulty.medium).index;
        final ok = rng.nextDouble() < pRight[level];
        if (ok) right++;
        s.record(ok);
      }
      expect(right / n, closeTo(0.71, 0.06));
    });
  });

  group('SmartPracticeSession.planSkills', () {
    test('a focus skill gets half; the rest split by score', () {
      final plan = SmartPracticeSession.planSkills(
        [('a', 1.0), ('b', 1.0), ('c', 0.5)],
        12,
        focusSkill: 'c',
      );
      expect(plan.length, 12);
      expect(plan.where((s) => s == 'c').length, 6);
      expect(plan.where((s) => s == 'a').length, 3);
      expect(plan.where((s) => s == 'b').length, 3);
    });

    test('without focus, slots follow score', () {
      final plan = SmartPracticeSession.planSkills([('a', 3.0), ('b', 1.0)], 8);
      expect(plan.where((s) => s == 'a').length, 6);
      expect(plan.where((s) => s == 'b').length, 2);
    });

    test('never the same skill twice in a row while others remain', () {
      final plan = SmartPracticeSession.planSkills(
        [('a', 1.0), ('b', 1.0), ('c', 1.0)],
        12,
        focusSkill: 'a',
      );
      for (var i = 1; i < plan.length; i++) {
        expect(plan[i], isNot(plan[i - 1]), reason: plan.join(','));
      }
    });

    test('a single skill fills the session', () {
      expect(
        SmartPracticeSession.planSkills([('a', 1.0)], 5, focusSkill: 'a'),
        ['a', 'a', 'a', 'a', 'a'],
      );
      expect(SmartPracticeSession.planSkills(const [], 5), isEmpty);
    });
  });

  group('SmartPracticeSession', () {
    final bundle = syntheticBundle(
      skills: const [
        ('math', 'alg', 'a'),
        ('math', 'alg', 'b'),
        ('math', 'geo', 'c'),
        ('reading', 'info', 'd'),
        ('reading', 'info', 'e'),
      ],
      perDifficulty: 12,
    );

    AppProgress progress() => AppProgress(
      skillMastery: {
        'a': SkillMastery(skillId: 'a', mastery: 10, attempts: 10),
        'b': SkillMastery(skillId: 'b', mastery: 65, attempts: 10),
        'c': SkillMastery(skillId: 'c', mastery: 85, attempts: 10),
        'd': SkillMastery(skillId: 'd', mastery: 30, attempts: 10),
        'e': SkillMastery(skillId: 'e', mastery: 100, attempts: 10),
      },
    );

    SmartPracticeSession plan({String? focus, int seed = 1, AppProgress? p}) =>
        SmartPracticeSession.plan(
          bundle: bundle,
          progress: p ?? progress(),
          now: _now,
          rng: Random(seed),
          focusSkill: focus,
        );

    test('draws from the top-ranked skills, no repeats', () {
      final s = plan();
      expect(s.questions.length, 12);
      expect(s.questions.map((q) => q.id).toSet().length, 12);
      // The strongest skill (e) is outranked by the four others.
      expect(s.questions.map((q) => q.skill).toSet(), {'a', 'b', 'c', 'd'});
      for (var i = 0; i < 12; i++) {
        expect(s.questions[i].skill, s.skillPlan[i]);
      }
    });

    test('starting difficulty follows each skill\'s mastery', () {
      final s = plan();
      expect(s.baseFor('a'), Difficulty.easy);
      expect(s.baseFor('b'), Difficulty.medium);
      expect(s.baseFor('c'), Difficulty.hard);
      for (final q in s.questions) {
        expect(q.difficulty, s.baseFor(q.skill));
      }
    });

    test('a focus skill gets half the session', () {
      final s = plan(focus: 'e');
      expect(s.questions.where((q) => q.skill == 'e').length, 6);
    });

    test('is deterministic for a seed', () {
      expect(
        plan(seed: 3).questions.map((q) => q.id),
        plan(seed: 3).questions.map((q) => q.id),
      );
    });

    test('prefers questions not answered before', () {
      final p = progress();
      for (final q in bundle.questions) {
        if (q.skill == 'a' && !q.id.endsWith('-q11')) {
          p.questionStats[q.id] = QuestionStat(questionId: q.id, attempts: 1);
        }
      }
      final s = plan(focus: 'a', p: p);
      final firstA = s.questions.firstWhere((q) => q.skill == 'a');
      expect(firstA.id, endsWith('-q11'));
    });

    test('steps the next question up after two right, down after a miss', () {
      final s = plan(focus: 'a'); // a starts easy
      // Plan alternates a / other; slot 2 is 'a' again.
      expect(s.skillPlan[0], 'a');
      expect(s.skillPlan[2], 'a');
      s.record(0, true);
      s.record(1, true); // two right -> +1
      expect(s.staircase.offset, 1);
      expect(s.questions[2].difficulty, Difficulty.medium);
      s.record(2, false); // miss -> back to 0
      expect(s.staircase.offset, 0);
      expect(s.questions[3].difficulty, s.baseFor(s.skillPlan[3]));
      // Still no duplicates after re-picks.
      expect(s.questions.map((q) => q.id).toSet().length, 12);
    });

    test('ignores out-of-order and repeated answers', () {
      final s = plan();
      s.record(1, true);
      expect(s.staircase.offset, 0);
      s.record(0, true);
      s.record(0, true);
      expect(s.staircase.offset, 0);
    });

    test('works on the real SAT and ACT bundles', () {
      for (final exam in ['sat', 'act']) {
        final b = realBundle(exam);
        final s = SmartPracticeSession.plan(
          bundle: b,
          progress: AppProgress(),
          now: _now,
          rng: Random(1),
        );
        expect(s.questions.length, 12, reason: exam);
        expect(s.questions.every((q) => q.examId == exam), isTrue);
        expect(s.questions.map((q) => q.id).toSet().length, 12);
      }
    });
  });
}
