import 'package:flutter_test/flutter_test.dart';
import 'package:zany_test_prep/domain/models/progress.dart';
import 'package:zany_test_prep/domain/services/recommendation_engine.dart';

import '../helpers/adaptive_fixtures.dart';

final _now = DateTime(2026, 5, 10, 18);
const _engine = RecommendationEngine();

/// Two skills in one domain, both unlocked from the start.
final _twoSkills = syntheticBundle(
  skills: const [('math', 'alg', 'a'), ('math', 'alg', 'b')],
);

SkillMastery _sm(
  String key,
  double mastery, {
  int attempts = 10,
  String? last,
  bool seeded = false,
}) => SkillMastery(
  skillId: key,
  mastery: mastery,
  attempts: attempts,
  lastPracticedDay: last,
  seeded: seeded,
);

void _due(AppProgress p, String skillKey, int n, {String day = '2026-05-09'}) {
  for (var i = 0; i < n; i++) {
    p.reviewQueue.add(
      ReviewItem(
        questionId: 'sat-$skillKey-easy-q$i',
        skillId: skillKey,
        intervalDays: 1,
        dueDay: day,
      ),
    );
  }
}

List<String> _ranked(AppProgress p, {bundle}) => _engine
    .rankSkills(bundle ?? _twoSkills, p, now: _now)
    .map((s) => s.skillId)
    .toList();

void main() {
  group('RecommendationEngine.rankSkills', () {
    test('weak skills rank above strong ones', () {
      final p = AppProgress(
        skillMastery: {'a': _sm('a', 85), 'b': _sm('b', 20)},
      );
      expect(_ranked(p), ['b', 'a']);
      final rec = _engine.recommend(_twoSkills, p, now: _now)!;
      expect(rec.kind, RecommendationKind.practice);
      expect(rec.reason, RecommendationReason.weakest);
      expect(rec.label, 'Weakest: Skill b');
      expect(rec.route, '/practice/smart?skill=b');
    });

    test('due reviews boost a skill', () {
      final p = AppProgress(
        skillMastery: {'a': _sm('a', 50), 'b': _sm('b', 50)},
      );
      expect(_ranked(p), ['a', 'b']); // tie -> path order
      _due(p, 'b', 2);
      final ranked = _engine.rankSkills(_twoSkills, p, now: _now);
      expect(ranked.first.skillId, 'b');
      expect(ranked.first.dueReviews, 2);
      expect(ranked.first.dueBoost, closeTo(0.24, 1e-9));
    });

    test('items not yet due do not boost', () {
      final p = AppProgress(
        skillMastery: {'a': _sm('a', 50), 'b': _sm('b', 50)},
      );
      _due(p, 'b', 2, day: '2026-05-20');
      expect(_ranked(p), ['a', 'b']);
    });

    test('recency penalty: a skill practiced today drops below its twin', () {
      final p = AppProgress(
        skillMastery: {
          'a': _sm('a', 40, last: '2026-05-10'),
          'b': _sm('b', 40, last: '2026-05-01'),
        },
      );
      expect(_ranked(p), ['b', 'a']);
      final a = _engine
          .rankSkills(_twoSkills, p, now: _now)
          .firstWhere((s) => s.skillId == 'a');
      expect(a.daysSincePractice, 0);
      expect(a.recencyPenalty, -0.4);
      // The penalty fades: yesterday is milder, a week ago is none.
      expect(RecommendationEngine.recencyPenaltyFor(1), -0.2);
      expect(RecommendationEngine.recencyPenaltyFor(2), -0.1);
      expect(RecommendationEngine.recencyPenaltyFor(7), 0);
      expect(RecommendationEngine.recencyPenaltyFor(null), 0);
    });

    test('recency outweighs a small mastery gap but not a large one', () {
      final small = AppProgress(
        skillMastery: {
          'a': _sm('a', 35, last: '2026-05-10'),
          'b': _sm('b', 45),
        },
      );
      expect(_ranked(small), ['b', 'a']);
      final large = AppProgress(
        skillMastery: {
          'a': _sm('a', 5, last: '2026-05-10'),
          'b': _sm('b', 90),
        },
      );
      expect(_ranked(large), ['a', 'b']);
    });

    test('little-practiced skills get an uncertainty bonus', () {
      final p = AppProgress(
        skillMastery: {
          'a': _sm('a', 50, attempts: 40),
          'b': _sm('b', 50, attempts: 1),
        },
      );
      expect(_ranked(p), ['b', 'a']);
    });

    test('only unlocked skills are candidates', () {
      final bundle = syntheticBundle(
        skills: const [('math', 'alg', 'a'), ('math', 'alg', 'locked')],
        lockedSkills: const {'locked'},
      );
      final p = AppProgress(
        skillMastery: {'a': _sm('a', 90), 'locked': _sm('locked', 0)},
      );
      expect(_ranked(p, bundle: bundle), ['a']);
      expect(_engine.recommend(bundle, p, now: _now)!.skillId, 'a');
      // XP unlocks it.
      p.game.totalXp = 1000000;
      expect(_ranked(p, bundle: bundle).first, 'locked');
    });

    test('domain balance nudges toward an under-practiced domain', () {
      final bundle = syntheticBundle(
        skills: const [('math', 'alg', 'm'), ('reading', 'info', 'r')],
      );
      final p = AppProgress(
        skillMastery: {
          'm': _sm('m', 50, attempts: 30),
          'r': _sm('r', 50, attempts: 30),
        },
      );
      expect(_ranked(p, bundle: bundle), ['m', 'r']); // tie -> path order
      p.skillMastery['m']!.attempts = 54;
      p.skillMastery['r']!.attempts = 6;
      final ranked = _engine.rankSkills(bundle, p, now: _now);
      expect(ranked.first.skillId, 'r');
      expect(ranked.first.domainBalance, greaterThan(0));
      expect(ranked.last.domainBalance, lessThan(0));
    });

    test('ACT skills read exam-scoped mastery keys', () {
      final bundle = syntheticBundle(
        examId: 'act',
        skills: const [('english', 'usage', 'a'), ('english', 'usage', 'b')],
      );
      final p = AppProgress(
        skillMastery: {
          // A same-named SAT skill must not leak into the ACT ranking.
          'b': _sm('b', 0),
          'act:a': _sm('act:a', 10),
          'act:b': _sm('act:b', 70),
        },
      );
      final ranked = _engine.rankSkills(bundle, p, now: _now);
      expect(ranked.map((s) => s.skillId), ['a', 'b']);
      expect(ranked.first.masteryKey, 'act:a');
    });

    test('is deterministic', () {
      final bundle = realBundle('sat');
      final p = AppProgress(
        skillMastery: {
          'linear_equations': _sm('linear_equations', 20),
          'main_idea': _sm('main_idea', 70, last: '2026-05-09'),
        },
      );
      final one = _engine.rankSkills(bundle, p, now: _now);
      final two = _engine.rankSkills(bundle, p, now: _now);
      expect(
        one.map((s) => '${s.skillId}:${s.score}'),
        two.map((s) => '${s.skillId}:${s.score}'),
      );
    });
  });

  group('RecommendationEngine.recommend', () {
    test('a brand-new learner gets no recommendation', () {
      expect(_engine.recommend(_twoSkills, AppProgress(), now: _now), isNull);
    });

    test('three or more due reviews make review the pick', () {
      final p = AppProgress(skillMastery: {'a': _sm('a', 10)});
      _due(p, 'b', 3);
      final rec = _engine.recommend(_twoSkills, p, now: _now)!;
      expect(rec.kind, RecommendationKind.review);
      expect(rec.label, '3 reviews due');
      expect(rec.route, '/review');
    });

    test('one due review with no other evidence still suggests review', () {
      final p = AppProgress();
      _due(p, 'a', 1);
      final rec = _engine.recommend(_twoSkills, p, now: _now)!;
      expect(rec.kind, RecommendationKind.review);
      expect(rec.label, '1 review due');
    });

    test('an untouched skill is taught first via its next open lesson', () {
      final p = AppProgress(skillMastery: {'a': _sm('a', 95, attempts: 30)});
      final rec = _engine.recommend(_twoSkills, p, now: _now)!;
      expect(rec.reason, RecommendationReason.newSkill);
      expect(rec.kind, RecommendationKind.lesson);
      expect(rec.lessonId, 'sat-b-easy');
      expect(rec.label, 'New to you: Skill b');
      expect(rec.route, '/lesson/sat-b-easy');
    });

    test('placement estimates count as evidence (weakest, not new)', () {
      final p = AppProgress(
        skillMastery: {
          'a': _sm('a', 62, attempts: 0, seeded: true),
          'b': _sm('b', 25, attempts: 0, seeded: true),
        },
      );
      final rec = _engine.recommend(_twoSkills, p, now: _now)!;
      expect(rec.label, 'Weakest: Skill b');
      expect(rec.kind, RecommendationKind.practice);
    });
  });
}
