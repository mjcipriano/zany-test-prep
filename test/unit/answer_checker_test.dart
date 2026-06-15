import 'package:flutter_test/flutter_test.dart';
import 'package:zany_test_prep/domain/models/difficulty.dart';
import 'package:zany_test_prep/domain/models/question.dart';
import 'package:zany_test_prep/domain/services/answer_checker.dart';

Question _mc() => const Question(
  id: 'q1',
  examId: 'sat',
  domain: 'math',
  section: 'algebra',
  skill: 'linear_equations',
  lessonId: 'l1',
  difficulty: Difficulty.easy,
  type: QuestionType.multipleChoice,
  estimatedTimeSeconds: 60,
  prompt: 'p',
  explanation: 'e',
  tags: ['t'],
  choices: [
    Choice(id: 'A', text: '1', rationale: 'r'),
    Choice(id: 'B', text: '2', rationale: 'r'),
  ],
  correctChoice: 'B',
);

Question _spr({num value = 12, List<String>? accepted, double tol = 0}) =>
    Question(
      id: 'q2',
      examId: 'sat',
      domain: 'math',
      section: 'algebra',
      skill: 'linear_equations',
      lessonId: 'l1',
      difficulty: Difficulty.medium,
      type: QuestionType.studentProduced,
      estimatedTimeSeconds: 75,
      prompt: 'p',
      explanation: 'e',
      tags: const ['t'],
      answer: ProducedAnswer(
        type: 'numeric',
        value: value,
        accepted: accepted ?? [value.toString()],
        tolerance: tol,
      ),
    );

void main() {
  const checker = AnswerChecker();

  group('multiple choice', () {
    test('accepts the correct choice', () {
      expect(checker.checkChoice(_mc(), 'B'), isTrue);
    });
    test('rejects a wrong choice', () {
      expect(checker.checkChoice(_mc(), 'A'), isFalse);
    });
    test('rejects null', () {
      expect(checker.checkChoice(_mc(), null), isFalse);
    });
  });

  group('student produced numeric', () {
    test('exact integer match', () {
      expect(checker.checkProduced(_spr(value: 12), '12'), isTrue);
    });
    test('rejects wrong number', () {
      expect(checker.checkProduced(_spr(value: 12), '13'), isFalse);
    });
    test('whitespace tolerant', () {
      expect(checker.checkProduced(_spr(value: 12), '  12 '), isTrue);
    });
    test('within tolerance', () {
      expect(
        checker.checkProduced(_spr(value: 3.14, tol: 0.01), '3.15'),
        isTrue,
      );
      expect(
        checker.checkProduced(_spr(value: 3.14, tol: 0.01), '3.2'),
        isFalse,
      );
    });
    test('fraction equivalent to decimal', () {
      expect(
        checker.checkProduced(_spr(value: 0.5, accepted: const ['1/2']), '1/2'),
        isTrue,
      );
      expect(
        checker.checkProduced(_spr(value: 0.5, accepted: const ['0.5']), '1/2'),
        isTrue,
      );
    });
    test('empty input is wrong', () {
      expect(checker.checkProduced(_spr(value: 12), ''), isFalse);
    });
  });

  group('parseNumeric', () {
    test('parses fractions and decimals', () {
      expect(AnswerChecker.parseNumeric('3/4'), closeTo(0.75, 1e-9));
      expect(AnswerChecker.parseNumeric('-2.5'), closeTo(-2.5, 1e-9));
      expect(AnswerChecker.parseNumeric('50%'), closeTo(50, 1e-9));
      expect(AnswerChecker.parseNumeric('abc'), isNull);
      expect(AnswerChecker.parseNumeric('1/0'), isNull);
    });
  });
}
