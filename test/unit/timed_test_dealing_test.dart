import 'dart:math';

import 'package:flutter_test/flutter_test.dart';
import 'package:zany_test_prep/domain/models/content_bundle.dart';
import 'package:zany_test_prep/domain/models/exam.dart';
import 'package:zany_test_prep/domain/models/question.dart';
import 'package:zany_test_prep/domain/services/timed_test.dart';

Map<String, dynamic> _q(String id, String domain, {String? set}) => {
  'question_id': id,
  'exam_id': 'x',
  'domain': domain,
  'section': 's',
  'skill': 'k',
  'lesson_id': 'l',
  'difficulty': 'easy',
  'question_type': 'multiple_choice',
  'estimated_time_seconds': 30,
  'prompt': 'p',
  'explanation': 'e',
  'tags': ['t', if (set != null) 'passage-set:$set'],
  'choices': [
    {'id': 'A', 'text': 'a', 'rationale': 'r'},
    {'id': 'B', 'text': 'b', 'rationale': 'r'},
  ],
  'correct_choice': 'A',
};

ContentBundle _bundle(
  Map<String, int> perDomain, {
  Map<String, List<int>> setsPerDomain = const {},
}) => ContentBundle.fromJson({
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
      for (var i = 0; i < e.value; i++) _q('${e.key}-$i', e.key),
    // Passage sets: setsPerDomain[d][k] questions in set "d-set-k", in order.
    for (final e in setsPerDomain.entries)
      for (final (k, size) in e.value.indexed)
        for (var i = 1; i <= size; i++)
          _q('${e.key}-set$k-q$i', e.key, set: '${e.key}-set-$k'),
  ],
});

void main() {
  test('deals distinct questions into each module by domain', () {
    final bundle = _bundle({'math': 60, 'reading_writing': 60});
    final modules = [
      const TestModule(
        name: 'RW1',
        domain: 'reading_writing',
        count: 27,
        minutes: 32,
      ),
      const TestModule(
        name: 'RW2',
        domain: 'reading_writing',
        count: 27,
        minutes: 32,
      ),
      const TestModule(name: 'M1', domain: 'math', count: 22, minutes: 35),
      const TestModule(name: 'M2', domain: 'math', count: 22, minutes: 35),
    ];
    final dealt = dealLinearModules(bundle.questions, modules, Random(1));
    expect(dealt.map((m) => m.length).toList(), [27, 27, 22, 22]);
    expect(dealt[0].every((q) => q.domain == 'reading_writing'), isTrue);
    expect(dealt[2].every((q) => q.domain == 'math'), isTrue);
    final ids = dealt.expand((m) => m).map((q) => q.id).toList();
    expect(ids.toSet().length, ids.length, reason: 'no repeats across modules');
  });

  test(
    'a short domain yields shorter (then empty) modules instead of throwing',
    () {
      // Regression: the old code called sublist(start, …) with start > length.
      final bundle = _bundle({'math': 30, 'english': 5});
      final modules = [
        const TestModule(name: 'E1', domain: 'english', count: 50, minutes: 35),
        const TestModule(name: 'E2', domain: 'english', count: 50, minutes: 35),
        const TestModule(name: 'M', domain: 'math', count: 45, minutes: 50),
        const TestModule(name: 'S', domain: 'science', count: 40, minutes: 40),
      ];
      final dealt = dealLinearModules(bundle.questions, modules, Random(2));
      expect(dealt.map((m) => m.length).toList(), [5, 0, 30, 0]);
    },
  );

  group('long passage sets', () {
    List<String?> setsIn(List<Question> module) => [
      for (final q in module) q.passageSetId,
    ];

    test('a reading module is filled with whole sets, kept in order', () {
      final bundle = _bundle(
        {'reading': 40},
        setsPerDomain: {
          'reading': [9, 9, 9, 9, 9, 9],
        },
      );
      const module = TestModule(
        name: 'Reading',
        domain: 'reading',
        count: 36,
        minutes: 40,
      );
      final dealt = dealLinearModules(bundle.questions, [module, module], Random(3));
      expect(dealt[0], hasLength(36));
      // Module 1: exactly four sets, each contiguous and in authored order.
      final ids = setsIn(dealt[0]);
      expect(ids.every((id) => id != null), isTrue);
      expect(ids.toSet(), hasLength(4));
      for (var i = 0; i < 36; i += 9) {
        final chunk = dealt[0].sublist(i, i + 9);
        expect(chunk.map((q) => q.passageSetId).toSet(), hasLength(1));
        expect(chunk.map((q) => q.id.split('-q').last).toList(), [
          '1',
          '2',
          '3',
          '4',
          '5',
          '6',
          '7',
          '8',
          '9',
        ]);
      }
      // Module 2: the two remaining sets first, then single questions.
      expect(dealt[1], hasLength(36));
      expect(setsIn(dealt[1]).take(18).every((id) => id != null), isTrue);
      expect(setsIn(dealt[1]).skip(18).every((id) => id == null), isTrue);
      final all = dealt.expand((m) => m).map((q) => q.id).toList();
      expect(all.toSet(), hasLength(all.length));
    });

    test('sets that do not fit are skipped and singles fill the room', () {
      final bundle = _bundle(
        {'reading': 10},
        setsPerDomain: {
          'reading': [9, 9, 9],
        },
      );
      const module = TestModule(
        name: 'R',
        domain: 'reading',
        count: 20,
        minutes: 20,
      );
      final dealt = dealLinearModules(bundle.questions, [module], Random(4));
      expect(dealt.single, hasLength(20));
      expect(setsIn(dealt.single).where((id) => id != null), hasLength(18));
      expect(setsIn(dealt.single).skip(18), [null, null]);
    });

    test('domains without sets are dealt exactly as before', () {
      final bundle = _bundle(
        {'math': 30, 'reading': 10},
        setsPerDomain: {
          'reading': [9],
        },
      );
      const m = TestModule(name: 'M', domain: 'math', count: 20, minutes: 20);
      final dealt = dealLinearModules(bundle.questions, [m], Random(5));
      expect(dealt.single, hasLength(20));
      expect(dealt.single.every((q) => q.passageSetId == null), isTrue);
    });
  });
}
