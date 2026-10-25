import 'dart:math';

import 'package:flutter_test/flutter_test.dart';
import 'package:zany_test_prep/domain/models/content_bundle.dart';
import 'package:zany_test_prep/domain/models/difficulty.dart';
import 'package:zany_test_prep/domain/models/profile.dart';
import 'package:zany_test_prep/domain/models/progress.dart';
import 'package:zany_test_prep/domain/models/question.dart';
import 'package:zany_test_prep/domain/services/badges.dart';
import 'package:zany_test_prep/domain/services/diagnostic_engine.dart';
import 'package:zany_test_prep/domain/services/game_service.dart';
import 'package:zany_test_prep/domain/services/recommendation_engine.dart';

import '../helpers/adaptive_fixtures.dart';

const _engine = DiagnosticEngine();

/// math: alg {a, b}, geo {c}; reading: info {d}.
final _bundle = syntheticBundle(
  skills: const [
    ('math', 'alg', 'a'),
    ('math', 'alg', 'b'),
    ('math', 'geo', 'c'),
    ('reading', 'info', 'd'),
    ('reading', 'craft', 'e'),
  ],
);

Question _medium(ContentBundle b, String skill) => b.questions.firstWhere(
  (q) => q.skill == skill && q.difficulty == Difficulty.medium,
);

AnswerResult _r(ContentBundle b, String skill, bool correct) =>
    AnswerResult(question: _medium(b, skill), correct: correct);

void main() {
  group('DiagnosticEngine.pick', () {
    for (final exam in ['sat', 'act']) {
      test('$exam: 12 questions, one per skill, spanning every domain', () {
        final b = realBundle(exam);
        final qs = _engine.pick(b, Random(1));
        expect(qs.length, 12);
        expect(qs.map((q) => q.skill).toSet().length, 12);
        expect(qs.every((q) => q.examId == exam), isTrue);
        expect(qs.map((q) => q.domain).toSet(), b.domainIds.toSet());
        // Domains take turns in exam order.
        expect(qs.take(b.domainIds.length).map((q) => q.domain), b.domainIds);
        expect(qs.every((q) => q.difficulty == Difficulty.medium), isTrue);
      });
    }

    test('SAT: 12 questions reach all 8 sections', () {
      final qs = _engine.pick(realBundle('sat'), Random(2));
      expect(qs.map((q) => q.section).toSet().length, 8);
    });

    test('is deterministic for a seed and varies across seeds', () {
      final b = realBundle('sat');
      final ids1 = _engine.pick(b, Random(5)).map((q) => q.id).toList();
      final ids2 = _engine.pick(b, Random(5)).map((q) => q.id).toList();
      final ids3 = _engine.pick(b, Random(6)).map((q) => q.id).toList();
      expect(ids1, ids2);
      expect(ids1, isNot(ids3));
    });

    test('a short bank yields fewer questions instead of failing', () {
      final qs = _engine.pick(_bundle, Random(1));
      expect(qs.length, 5);
    });
  });

  group('DiagnosticEngine.estimates (seeding math)', () {
    test('tested skills map right/wrong by difficulty', () {
      expect(DiagnosticEngine.testedEstimate(true, Difficulty.medium), 62);
      expect(DiagnosticEngine.testedEstimate(false, Difficulty.medium), 25);
      expect(DiagnosticEngine.testedEstimate(true, Difficulty.hard), 72);
      expect(DiagnosticEngine.testedEstimate(false, Difficulty.easy), 15);
    });

    test('untested skills are inferred from their section, then domain', () {
      final e = _engine.estimates(_bundle, [
        _r(_bundle, 'a', true), // alg tested: 62
        _r(_bundle, 'd', false), // info tested: 25
      ]);
      expect(e['a'], 62);
      expect(e['d'], 25);
      // Same section: (62 + prior) / 2.
      expect(e['b'], (62 + kUnknownMasteryPrior) / 2);
      // Untested section, tested domain: (62 + 2 × prior) / 3.
      expect(e['c'], closeTo((62 + 2 * kUnknownMasteryPrior) / 3, 1e-9));
      expect(e['e'], closeTo((25 + 2 * kUnknownMasteryPrior) / 3, 1e-9));
    });

    test('a domain with no answers gets no estimate', () {
      final e = _engine.estimates(_bundle, [_r(_bundle, 'a', true)]);
      expect(e.containsKey('d'), isFalse);
      expect(e.containsKey('e'), isFalse);
    });
  });

  group('DiagnosticEngine.seed', () {
    test('writes seeded estimates and marks the check done', () {
      final p = AppProgress();
      _engine.seed(p, _bundle, [
        _r(_bundle, 'a', true),
        _r(_bundle, 'd', false),
      ]);
      expect(p.skillMastery['a']!.mastery, 62);
      expect(p.skillMastery['a']!.seeded, isTrue);
      expect(p.skillMastery['a']!.attempts, 0);
      expect(p.skillMastery['d']!.mastery, 25);
      expect(p.game.diagnosticDoneFor('sat'), isTrue);
    });

    test('grants no XP, streak, chest, history or review items', () {
      final p = AppProgress();
      _engine.seed(p, _bundle, [
        _r(_bundle, 'a', true),
        _r(_bundle, 'b', false),
      ]);
      expect(p.game.totalXp, 0);
      expect(p.game.dailyXp, 0);
      expect(p.game.currentStreak, 0);
      expect(p.game.unopenedChests, 0);
      expect(p.history, isEmpty);
      expect(p.reviewQueue, isEmpty);
      expect(p.questionStats, isEmpty);
    });

    test('never overwrites real practice; a retest averages in', () {
      final p = AppProgress(
        skillMastery: {
          'a': SkillMastery(skillId: 'a', mastery: 90, attempts: 20),
          'b': SkillMastery(skillId: 'b', mastery: 70, attempts: 5),
        },
      );
      _engine.seed(p, _bundle, [_r(_bundle, 'a', false)]);
      expect(p.skillMastery['a']!.mastery, (90 + 25) / 2); // tested: averaged
      expect(p.skillMastery['a']!.seeded, isFalse);
      expect(p.skillMastery['b']!.mastery, 70); // inferred: untouched
    });

    test('a retake replaces earlier estimates', () {
      final p = AppProgress();
      _engine.seed(p, _bundle, [_r(_bundle, 'a', false)]);
      _engine.seed(p, _bundle, [_r(_bundle, 'a', true)]);
      expect(p.skillMastery['a']!.mastery, 62);
      expect(p.skillMastery['a']!.seeded, isTrue);
    });

    test('ACT estimates use exam-scoped keys', () {
      final act = syntheticBundle(
        examId: 'act',
        skills: const [('science', 'data', 'a'), ('science', 'data', 'b')],
      );
      final p = AppProgress();
      _engine.seed(p, act, [_r(act, 'a', true)]);
      expect(p.skillMastery.keys, containsAll(['act:a', 'act:b']));
      expect(p.skillMastery.containsKey('a'), isFalse);
      expect(p.game.diagnosticDoneFor('act'), isTrue);
      expect(p.game.diagnosticDoneFor('sat'), isFalse);
    });

    test('seeded estimates earn no mastery badges until practiced', () {
      final p = AppProgress();
      for (var i = 0; i < 5; i++) {
        p.skillMastery['s$i'] = SkillMastery(
          skillId: 's$i',
          mastery: 85,
          seeded: true,
        );
      }
      bool skillBadge(String id) =>
          id.startsWith('mastered_') ||
          id.startsWith('proficient_') ||
          id.startsWith('skills_');
      expect(Badges.evaluateAndGrant(p, _bundle).where(skillBadge), isEmpty);
      // The same masteries earned for real do count.
      for (final m in p.skillMastery.values) {
        m.seeded = false;
      }
      expect(
        Badges.evaluateAndGrant(p, _bundle).where(skillBadge),
        containsAll(['mastered_1', 'proficient_5', 'skills_5']),
      );
    });

    test('real practice clears the seeded flag and counts attempts', () {
      final p = AppProgress();
      _engine.seed(p, _bundle, [_r(_bundle, 'a', true)]);
      const GameService().applyPracticeResult(
        progress: p,
        profile: UserProfile.initial('sat', 10),
        results: [_r(_bundle, 'a', true)],
        bundle: _bundle,
        now: DateTime(2026, 5, 10),
      );
      final a = p.skillMastery['a']!;
      expect(a.seeded, isFalse);
      expect(a.attempts, 1);
      expect(a.lastPracticedDay, '2026-05-10');
      expect(a.mastery, greaterThan(62));
    });
  });

  group('DiagnosticEngine.summarize', () {
    test('splits strong and focus and tallies domains in exam order', () {
      final s = _engine.summarize(_bundle, [
        _r(_bundle, 'd', true),
        _r(_bundle, 'a', false),
        _r(_bundle, 'c', true),
      ]);
      expect(s.correct, 2);
      expect(s.total, 3);
      expect(s.strong.map((x) => x.skillId), containsAll(['c', 'd']));
      expect(s.focus.map((x) => x.skillId), ['a']);
      expect(s.domains.map((d) => d.domain), ['math', 'reading']);
      expect(s.domains.first.correct, 1);
      expect(s.domains.first.total, 2);
    });
  });

  group('SkillMastery persistence', () {
    test('round-trips the new fields and reads legacy entries', () {
      final m = SkillMastery(
        skillId: 'x',
        mastery: 40,
        attempts: 3,
        lastPracticedDay: '2026-05-01',
        seeded: true,
      );
      final back = SkillMastery.fromJson(m.toJson());
      expect(back.attempts, 3);
      expect(back.lastPracticedDay, '2026-05-01');
      expect(back.seeded, isTrue);
      final legacy = SkillMastery.fromJson({'skillId': 'x', 'mastery': 55});
      expect(legacy.mastery, 55);
      expect(legacy.attempts, 0);
      expect(legacy.seeded, isFalse);
      expect(legacy.lastPracticedDay, isNull);
    });
  });
}
