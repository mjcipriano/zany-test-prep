import 'package:flutter/material.dart';
import 'package:flutter_test/flutter_test.dart';
import 'package:zany_test_prep/domain/models/difficulty.dart';
import 'package:zany_test_prep/domain/models/question.dart';
import 'package:zany_test_prep/domain/services/answer_checker.dart';
import 'package:zany_test_prep/features/lessons/question_view.dart';

const _five = Question(
  id: 'act-math-x',
  examId: 'act',
  domain: 'math',
  section: 'algebra',
  skill: 'linear_equations',
  lessonId: 'l',
  difficulty: Difficulty.medium,
  type: QuestionType.multipleChoice,
  estimatedTimeSeconds: 60,
  prompt: 'If 3x + 2 = 17, what is x?',
  explanation: 'Subtract 2, divide by 3.',
  tags: ['t'],
  choices: [
    Choice(id: 'A', text: '3', rationale: 'no'),
    Choice(id: 'B', text: '4', rationale: 'no'),
    Choice(id: 'C', text: '5', rationale: 'Correct.'),
    Choice(id: 'D', text: '6', rationale: 'no'),
    Choice(id: 'E', text: '15', rationale: 'no'),
  ],
  correctChoice: 'C',
);

void main() {
  test('AnswerChecker handles a fifth choice id', () {
    const checker = AnswerChecker();
    expect(checker.checkChoice(_five, 'C'), isTrue);
    expect(checker.checkChoice(_five, 'E'), isFalse);
    expect(checker.isCorrect(_five, choiceId: 'E'), isFalse);
    expect(checker.isCorrect(_five, choiceId: 'C'), isTrue);
  });

  testWidgets('QuestionView renders all five ACT math choices', (tester) async {
    String? picked;
    await tester.pumpWidget(
      MaterialApp(
        home: Scaffold(
          body: QuestionView(
            question: _five,
            answered: false,
            selectedChoiceId: null,
            textController: TextEditingController(),
            onSelectChoice: (id) => picked = id,
          ),
        ),
      ),
    );
    for (final c in _five.choices) {
      expect(find.text(c.text), findsOneWidget, reason: c.id);
      expect(find.text(c.id), findsOneWidget, reason: c.id);
    }
    await tester.tap(find.text('15'));
    expect(picked, 'E');
  });
}
