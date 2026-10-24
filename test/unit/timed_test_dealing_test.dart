import 'dart:math';

import 'package:flutter_test/flutter_test.dart';
import 'package:zany_test_prep/domain/models/content_bundle.dart';
import 'package:zany_test_prep/domain/models/exam.dart';
import 'package:zany_test_prep/features/test/timed_test_screen.dart';

ContentBundle _bundle(Map<String, int> perDomain) => ContentBundle.fromJson({
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
          'difficulty': 'easy',
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
    final dealt = dealTestModules(bundle, modules, Random(1));
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
      final dealt = dealTestModules(bundle, modules, Random(2));
      expect(dealt.map((m) => m.length).toList(), [5, 0, 30, 0]);
    },
  );
}
