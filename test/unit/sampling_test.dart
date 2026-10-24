import 'dart:math';

import 'package:flutter_test/flutter_test.dart';
import 'package:zany_test_prep/domain/models/difficulty.dart';
import 'package:zany_test_prep/domain/models/question.dart';
import 'package:zany_test_prep/features/practice/sampling.dart';

Question q(String id, String domain) => Question(
  id: id,
  examId: 'x',
  domain: domain,
  section: 's',
  skill: 'k',
  lessonId: 'l',
  difficulty: Difficulty.easy,
  type: QuestionType.multipleChoice,
  estimatedTimeSeconds: 30,
  prompt: 'p',
  explanation: 'e',
  tags: const [],
);

void main() {
  test('balances evenly across every domain present', () {
    final pool = [
      for (var i = 0; i < 20; i++) q('e$i', 'english'),
      for (var i = 0; i < 20; i++) q('m$i', 'math'),
      for (var i = 0; i < 20; i++) q('r$i', 'reading'),
      for (var i = 0; i < 20; i++) q('s$i', 'science'),
    ];
    final out = balancedSample(pool, 16, Random(1));
    expect(out.length, 16);
    for (final d in ['english', 'math', 'reading', 'science']) {
      expect(out.where((x) => x.domain == d).length, 4, reason: d);
    }
    // Interleaved: consecutive picks come from different domains.
    for (var i = 1; i < out.length; i++) {
      expect(out[i].domain, isNot(out[i - 1].domain));
    }
    expect(out.map((x) => x.id).toSet().length, 16);
  });

  test('keeps the SAT behaviour: alternates math and reading/writing', () {
    final pool = [
      for (var i = 0; i < 10; i++) q('m$i', 'math'),
      for (var i = 0; i < 10; i++) q('r$i', 'reading_writing'),
    ];
    final out = balancedSample(pool, 6, Random(3));
    expect(out.map((x) => x.domain).toList(), [
      'math',
      'reading_writing',
      'math',
      'reading_writing',
      'math',
      'reading_writing',
    ]);
  });

  test('falls back to the remaining domains when one runs dry', () {
    final pool = [
      q('m0', 'math'),
      for (var i = 0; i < 10; i++) q('r$i', 'reading_writing'),
    ];
    final out = balancedSample(pool, 5, Random(0));
    expect(out.length, 5);
    expect(out.where((x) => x.domain == 'math').length, 1);
    expect(out.where((x) => x.domain == 'reading_writing').length, 4);
  });

  test('never exceeds the pool and handles empty input', () {
    expect(balancedSample(const [], 5, Random(0)), isEmpty);
    expect(balancedSample([q('a', 'math')], 0, Random(0)), isEmpty);
    expect(
      balancedSample([q('a', 'math'), q('b', 'math')], 9, Random(0)).length,
      2,
    );
  });
}
