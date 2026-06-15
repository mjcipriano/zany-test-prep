import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:flutter_test/flutter_test.dart';
import 'package:zany_test_prep/core/sound_service.dart';
import 'package:zany_test_prep/domain/models/difficulty.dart';
import 'package:zany_test_prep/domain/models/question.dart';
import 'package:zany_test_prep/domain/services/game_service.dart';
import 'package:zany_test_prep/features/lessons/lesson_player.dart';

Question _spr() => const Question(
  id: 'spr1',
  examId: 'sat',
  domain: 'math',
  section: 'algebra',
  skill: 'linear_equations',
  lessonId: 'l1',
  difficulty: Difficulty.easy,
  type: QuestionType.studentProduced,
  estimatedTimeSeconds: 70,
  prompt: 'If 3x = 36, what is x?',
  explanation: 'Divide both sides by 3: x = 12.',
  tags: ['algebra'],
  answer: ProducedAnswer(type: 'numeric', value: 12, accepted: ['12']),
);

void main() {
  testWidgets('grid-in: Check enables after typing and accepts the answer', (
    tester,
  ) async {
    await tester.pumpWidget(
      ProviderScope(
        overrides: [soundServiceProvider.overrideWithValue(NoopSoundService())],
        child: MaterialApp(
          home: LessonPlayer(
            title: 'Test',
            questions: [_spr()],
            onComplete: (results) async => const LessonOutcome(
              xpGained: 0,
              correct: 1,
              total: 1,
              stars: 3,
              leveledUp: false,
              oldLevel: 1,
              newLevel: 1,
              currentStreak: 1,
              streakExtended: true,
              streakReset: false,
              dailyGoalMet: false,
              dailyGoalJustMet: false,
              newBadges: [],
            ),
          ),
        ),
      ),
    );
    await tester.pumpAndSettle();

    // Before typing, Check is disabled (tapping does nothing → no feedback).
    await tester.tap(find.text('Check'));
    await tester.pumpAndSettle();
    expect(find.text('Correct!'), findsNothing);

    // Type the answer; Check should now work and accept it.
    await tester.enterText(find.byType(TextField), '12');
    await tester.pumpAndSettle();
    await tester.tap(find.text('Check'));
    await tester.pumpAndSettle();
    expect(find.text('Correct!'), findsOneWidget);
  });
}
