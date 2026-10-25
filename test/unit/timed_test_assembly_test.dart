import 'dart:math';

import 'package:flutter_test/flutter_test.dart';
import 'package:zany_test_prep/domain/models/content_bundle.dart';
import 'package:zany_test_prep/domain/models/difficulty.dart';
import 'package:zany_test_prep/domain/models/exam.dart';
import 'package:zany_test_prep/domain/models/question.dart';
import 'package:zany_test_prep/domain/services/scoring.dart';
import 'package:zany_test_prep/domain/services/timed_test.dart';

const _difficulties = ['easy', 'medium', 'hard'];

/// A bundle with [perDomain] questions per domain, difficulties cycling
/// easy/medium/hard (or all [only] when given). Every answer is "A".
ContentBundle _bundle(Map<String, int> perDomain, {String? only}) =>
    ContentBundle.fromJson({
      'exam': {
        'exam_id': 'x',
        'exam_name': 'X',
        'domains': perDomain.keys.toList(),
      },
      'skills': {
        'domains': [
          for (final d in perDomain.keys)
            {
              'id': d,
              'name': d,
              'sections': [
                {
                  'id': 's',
                  'name': 's',
                  'skills': [
                    {'id': 'k', 'name': 'k'},
                  ],
                },
              ],
            },
        ],
      },
      'lessons': [],
      'questions': [
        for (final e in perDomain.entries)
          for (var i = 0; i < e.value; i++)
            {
              'question_id': '${e.key}-$i',
              'exam_id': 'x',
              'domain': e.key,
              'section': 's',
              'skill': 'k',
              'lesson_id': 'l',
              'difficulty': only ?? _difficulties[i % 3],
              'question_type': 'multiple_choice',
              'estimated_time_seconds': 30,
              'prompt': 'p',
              'explanation': 'e',
              'choices': [
                {'id': 'A', 'text': 'a', 'rationale': 'r'},
                {'id': 'B', 'text': 'b', 'rationale': 'r'},
              ],
              'correct_choice': 'A',
            },
      ],
    });

const _satModules = [
  TestModule(name: 'RW1', domain: 'reading_writing', count: 27, minutes: 32),
  TestModule(name: 'RW2', domain: 'reading_writing', count: 27, minutes: 32),
  TestModule(name: 'M1', domain: 'math', count: 22, minutes: 35),
  TestModule(name: 'M2', domain: 'math', count: 22, minutes: 35),
];

const _satPlan = TimedTestPlan(
  modules: _satModules,
  adaptive: AdaptiveSpec(enabled: true),
);

Map<Difficulty, int> _mix(List<Question> qs) => {
  for (final d in Difficulty.values)
    d: qs.where((q) => q.difficulty == d).length,
};

bool _ascending(List<Question> qs) {
  for (var i = 1; i < qs.length; i++) {
    if (qs[i].difficulty.index < qs[i - 1].difficulty.index) return false;
  }
  return true;
}

void main() {
  group('linear plans (ACT) deal at random per domain', () {
    test('deals distinct questions into each module by domain', () {
      final bundle = _bundle({'math': 60, 'reading_writing': 60});
      final a = TestAssembler(
        bundle.questions,
        const TimedTestPlan(modules: _satModules), // adaptive off
        Random(1),
      );
      final dealt = [for (var i = 0; i < 4; i++) a.buildModule(i)];
      expect(dealt.map((m) => m.length).toList(), [27, 27, 22, 22]);
      expect(dealt[0].every((q) => q.domain == 'reading_writing'), isTrue);
      expect(dealt[2].every((q) => q.domain == 'math'), isTrue);
      final ids = dealt.expand((m) => m).map((q) => q.id).toList();
      expect(ids.toSet().length, ids.length, reason: 'no repeats');
    });

    test('a short domain yields shorter (then empty) modules; an absent '
        'domain is dropped from the plan', () {
      final bundle = _bundle({'math': 30, 'english': 5});
      final a = TestAssembler(
        bundle.questions,
        const TimedTestPlan(
          modules: [
            TestModule(name: 'E1', domain: 'english', count: 50, minutes: 35),
            TestModule(name: 'E2', domain: 'english', count: 50, minutes: 35),
            TestModule(name: 'M', domain: 'math', count: 45, minutes: 50),
            TestModule(name: 'S', domain: 'science', count: 40, minutes: 40),
          ],
        ),
        Random(2),
      );
      expect(a.plan.modules.map((m) => m.name), ['E1', 'E2', 'M']);
      final dealt = [for (var i = 0; i < 3; i++) a.buildModule(i)];
      expect(dealt.map((m) => m.length).toList(), [5, 0, 30]);
    });
  });

  group('adaptive plan structure', () {
    test('first module of a domain routes the later one', () {
      expect(_satPlan.isRoutingModule(0), isTrue);
      expect(_satPlan.isRoutingModule(1), isFalse);
      expect(_satPlan.isRoutingModule(2), isTrue);
      expect(_satPlan.routedBy(0), isNull);
      expect(_satPlan.routedBy(1), 0);
      expect(_satPlan.routedBy(3), 2);
    });

    test('linear plans and lone modules never route', () {
      const linear = TimedTestPlan(modules: _satModules);
      expect(linear.isRoutingModule(0), isFalse);
      expect(linear.routedBy(1), isNull);
      const lone = TimedTestPlan(
        modules: [TestModule(name: 'M', domain: 'math', count: 5, minutes: 5)],
        adaptive: AdaptiveSpec(enabled: true),
      );
      expect(lone.isRoutingModule(0), isFalse);
      expect(lone.routedBy(0), isNull);
    });
  });

  group('routing threshold', () {
    const spec = AdaptiveSpec(enabled: true); // 0.6 default

    test('at or above the threshold routes harder', () {
      expect(routeFor(17, 27, spec), SectionRoute.harder); // 63%
      expect(routeFor(3, 5, spec), SectionRoute.harder); // exactly 60%
      expect(routeFor(27, 27, spec), SectionRoute.harder);
    });

    test('below the threshold routes easier', () {
      expect(routeFor(16, 27, spec), SectionRoute.easier); // 59%
      expect(routeFor(0, 27, spec), SectionRoute.easier);
      expect(routeFor(0, 0, spec), SectionRoute.easier);
    });

    test('a custom threshold moves the cut', () {
      const strict = AdaptiveSpec(enabled: true, routeThreshold: 0.8);
      expect(routeFor(17, 27, strict), SectionRoute.easier);
      expect(routeFor(22, 27, strict), SectionRoute.harder);
    });
  });

  group('adaptive module assembly', () {
    final bundle = _bundle({'reading_writing': 300, 'math': 300});

    test('module 1 is an even mix, ordered easy to hard', () {
      final a = TestAssembler(bundle.questions, _satPlan, Random(3));
      final m1 = a.buildModule(0);
      expect(m1.length, 27);
      expect(_mix(m1), {
        Difficulty.easy: 9,
        Difficulty.medium: 9,
        Difficulty.hard: 9,
      });
      expect(_ascending(m1), isTrue);
    });

    test('the harder module 2 leans hard; the easier one leans easy', () {
      final a = TestAssembler(bundle.questions, _satPlan, Random(4));
      a.buildModule(0);
      final hard = a.buildModule(1, route: SectionRoute.harder);
      expect(_mix(hard), {
        Difficulty.easy: 4,
        Difficulty.medium: 9,
        Difficulty.hard: 14,
      });
      final b = TestAssembler(bundle.questions, _satPlan, Random(4));
      b.buildModule(0);
      final easy = b.buildModule(1, route: SectionRoute.easier);
      expect(_mix(easy), {
        Difficulty.easy: 14,
        Difficulty.medium: 9,
        Difficulty.hard: 4,
      });
      expect(_ascending(hard) && _ascending(easy), isTrue);
    });

    test('mix allocation always sums to the module size', () {
      for (final mix in [
        DifficultyMix.routing,
        DifficultyMix.harder,
        DifficultyMix.easier,
      ]) {
        for (var n = 0; n <= 40; n++) {
          expect(mix.allocate(n).fold(0, (s, c) => s + c), n);
        }
      }
    });

    test('a dry difficulty bucket is filled from the nearest one', () {
      final easyOnly = _bundle({'math': 100}, only: 'easy');
      const plan = TimedTestPlan(
        modules: [
          TestModule(name: 'M1', domain: 'math', count: 10, minutes: 5),
          TestModule(name: 'M2', domain: 'math', count: 10, minutes: 5),
        ],
        adaptive: AdaptiveSpec(enabled: true),
      );
      final a = TestAssembler(easyOnly.questions, plan, Random(5));
      expect(a.buildModule(0).length, 10);
      expect(a.buildModule(1, route: SectionRoute.harder).length, 10);
    });

    test('is deterministic for a given seed and differs across seeds', () {
      List<String> run(int seed, SectionRoute route) {
        final a = TestAssembler(bundle.questions, _satPlan, Random(seed));
        return [
          ...a.buildModule(0),
          ...a.buildModule(1, route: route),
          ...a.buildModule(2),
          ...a.buildModule(3, route: route),
        ].map((q) => q.id).toList();
      }

      final first = run(7, SectionRoute.harder);
      expect(run(7, SectionRoute.harder), first);
      expect(first.toSet().length, first.length, reason: 'no repeats');
      expect(run(8, SectionRoute.harder), isNot(first));
      expect(run(7, SectionRoute.easier), isNot(first));
    });
  });

  group('TimedTestReport', () {
    test('scores each section on its route and sums the SAT total', () {
      final bundle = _bundle({'reading_writing': 10, 'math': 10});
      final rw = bundle.questions.where((q) => q.domain == 'reading_writing');
      final math = bundle.questions.where((q) => q.domain == 'math');
      final report = TimedTestReport.score(
        modules: [rw.toList(), math.toList()],
        answers: {
          for (final q in rw) q.id: 'A', // all right
          for (final q in math.take(5)) q.id: 'A', // half right
          for (final q in math.skip(5).take(2)) q.id: 'B', // wrong
        },
        routes: {
          'reading_writing': SectionRoute.harder,
          'math': SectionRoute.easier,
        },
        scoring: const ExamScoring(ScoringSpec(scale: ScoreScale.sat1600)),
        domainOrder: const ['reading_writing', 'math'],
      );
      expect(report.domains, ['reading_writing', 'math']);
      final rwResult = report.sections.first;
      final mathResult = report.sections.last;
      expect((rwResult.correct, rwResult.total), (10, 10));
      expect(rwResult.score, 800);
      expect((mathResult.correct, mathResult.total), (5, 10));
      expect(mathResult.route, SectionRoute.easier);
      expect(mathResult.score, 430);
      expect(report.composite, 1230);
    });
  });
}
