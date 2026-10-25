import 'dart:convert';

import 'package:flutter/material.dart';
import 'package:flutter_test/flutter_test.dart';
import 'package:zany_test_prep/data/local/key_value_store.dart';
import 'package:zany_test_prep/data/repositories/progress_repository.dart';
import 'package:zany_test_prep/domain/models/lesson_resume.dart';

import '../helpers/pump_app.dart';

/// Opens the first lesson on the path ("Main Idea…").
Future<void> _openFirstLesson(WidgetTester tester) async {
  await tester.tap(find.textContaining('Main Idea').first);
  await tester.pumpAndSettle();
}

/// Pages through the mini-lesson and taps Start.
Future<void> _startQuiz(WidgetTester tester) async {
  for (var i = 0; i < 6 && find.text('Next').evaluate().isNotEmpty; i++) {
    await tester.tap(find.text('Next'));
    await tester.pumpAndSettle();
  }
  await tester.tap(find.text('Start'));
  await tester.pumpAndSettle();
}

/// Answers the visible question (choice A, or "1" for a grid-in) and checks.
Future<void> _answerAndCheck(WidgetTester tester) async {
  final field = find.byType(TextField);
  if (field.evaluate().isNotEmpty) {
    await tester.enterText(field.first, '1');
  } else {
    await tester.tap(find.text('A').first);
  }
  await tester.pumpAndSettle();
  await tester.tap(find.text('Check'));
  await tester.pumpAndSettle();
}

Future<void> _continue(WidgetTester tester) async {
  await tester.tap(find.text('Continue'));
  await tester.pumpAndSettle();
}

/// Answers every remaining question and taps Finish, landing on the summary.
Future<void> _finish(WidgetTester tester) async {
  for (var guard = 0; guard < 60; guard++) {
    if (find.text('Check').evaluate().isNotEmpty) {
      await _answerAndCheck(tester);
    } else if (find.text('Finish').evaluate().isNotEmpty) {
      await tester.tap(find.text('Finish'));
      await tester.pumpAndSettle();
      return;
    } else {
      await _continue(tester);
    }
  }
  fail('never reached Finish');
}

/// Taps the quiz close button and confirms leaving.
Future<void> _leave(WidgetTester tester) async {
  await tester.tap(find.byIcon(Icons.close_rounded));
  await tester.pumpAndSettle();
  expect(find.textContaining('Your progress is saved'), findsOneWidget);
  await tester.tap(find.text('Leave'));
  await tester.pumpAndSettle();
}

LessonResumeBook _book(MemoryStore store) =>
    ProgressRepository(store).loadLessonResume();

int _totalXp(MemoryStore store) =>
    ProgressRepository(store).loadProgress().game.totalXp;

void main() {
  testWidgets('answer some, leave, restart, resume at the same question', (
    tester,
  ) async {
    final store = await pumpApp(tester);
    await onboardDefault(tester);
    await _openFirstLesson(tester);
    await _startQuiz(tester);
    for (var i = 0; i < 3; i++) {
      await _answerAndCheck(tester);
      await _continue(tester);
    }
    final saved = _book(store).entries.values.single;
    final total = saved.total;
    expect(find.text('4/$total'), findsOneWidget);
    expect(saved.attempt.index, 3);
    expect(saved.attempt.answers, hasLength(3));
    expect(saved.attempt.teachingDone, isTrue);

    await _leave(tester);
    // Home path marks the lesson as in progress.
    expect(find.text('In progress · question 4 of $total'), findsOneWidget);

    // Simulate the app being killed and relaunched.
    await pumpApp(tester, store: store);
    expect(find.text('In progress · question 4 of $total'), findsOneWidget);
    await _openFirstLesson(tester);
    expect(find.text('Welcome back!'), findsOneWidget);
    expect(find.textContaining('3 of $total answered'), findsOneWidget);
    await tester.tap(find.text('Resume (question 4 of $total)'));
    await tester.pumpAndSettle();

    // Straight back to question 4: no teaching card, nothing re-answered.
    expect(find.text('Key points'), findsNothing);
    expect(find.text('4/$total'), findsOneWidget);
    expect(find.text('Check'), findsOneWidget);
  });

  testWidgets('leaving after Check restores that question with feedback', (
    tester,
  ) async {
    final store = await pumpApp(tester);
    await onboardDefault(tester);
    await _openFirstLesson(tester);
    await _startQuiz(tester);
    await _answerAndCheck(tester);
    await _continue(tester);
    await _answerAndCheck(tester); // question 2 checked, not continued
    final wasCorrect = find.text('Correct!').evaluate().isNotEmpty;
    await _leave(tester);

    await pumpApp(tester, store: store);
    await _openFirstLesson(tester);
    final total = _book(store).entries.values.single.total;
    await tester.tap(find.text('Resume (question 2 of $total)'));
    await tester.pumpAndSettle();
    expect(find.text('2/$total'), findsOneWidget);
    expect(find.text(wasCorrect ? 'Correct!' : 'Not quite'), findsOneWidget);
    expect(find.text('Continue'), findsOneWidget);
    await _continue(tester);
    expect(find.text('3/$total'), findsOneWidget);
  });

  testWidgets('start over discards the save and replays the teaching card', (
    tester,
  ) async {
    final store = await pumpApp(tester);
    await onboardDefault(tester);
    await _openFirstLesson(tester);
    await _startQuiz(tester);
    await _answerAndCheck(tester);
    await _continue(tester);
    await _leave(tester);

    await _openFirstLesson(tester);
    await tester.tap(find.text('Start over'));
    await tester.pumpAndSettle();
    expect(_book(store).isEmpty, isTrue);
    expect(find.text('Key points'), findsWidgets);
    await _startQuiz(tester);
    final total = _book(store).entries.values.single.total;
    expect(find.text('1/$total'), findsOneWidget);
    expect(_book(store).entries.values.single.attempt.answers, isEmpty);
  });

  testWidgets('a resumed lesson grants XP once, like a straight run', (
    tester,
  ) async {
    // Straight run for the reference XP (same answers, same day, new user).
    final straight = await pumpApp(tester);
    await onboardDefault(tester);
    await _openFirstLesson(tester);
    await _startQuiz(tester);
    await _finish(tester);
    expect(find.text('Lesson complete!'), findsOneWidget);
    final expectedXp = _totalXp(straight);
    expect(expectedXp, greaterThan(0));

    // Interrupted run: answer 3, leave, relaunch, resume, finish.
    final store = await pumpApp(tester, store: MemoryStore());
    await onboardDefault(tester);
    await _openFirstLesson(tester);
    await _startQuiz(tester);
    for (var i = 0; i < 3; i++) {
      await _answerAndCheck(tester);
      await _continue(tester);
    }
    await _leave(tester);
    expect(_totalXp(store), 0, reason: 'no XP is granted mid-lesson');
    await pumpApp(tester, store: store);
    await _openFirstLesson(tester);
    await tester.tap(find.textContaining('Resume (question 4'));
    await tester.pumpAndSettle();
    await _finish(tester);
    expect(find.text('Lesson complete!'), findsOneWidget);

    // Finishing cleared the save; XP and completion counted once.
    expect(_book(store).isEmpty, isTrue);
    expect(_totalXp(store), expectedXp);
    final lessons = ProgressRepository(store).loadProgress().lessons;
    expect(lessons.values.single.timesCompleted, 1);

    // Back home: no indicator; reopening starts fresh with no prompt.
    await tester.tap(find.text('Continue'));
    await tester.pumpAndSettle();
    expect(find.textContaining('In progress ·'), findsNothing);
    await _openFirstLesson(tester);
    expect(find.text('Welcome back!'), findsNothing);
    expect(find.text('Key points'), findsWidgets);
  });

  testWidgets('a save from older content is discarded, not resumed', (
    tester,
  ) async {
    final store = await pumpApp(tester);
    await onboardDefault(tester);
    await _openFirstLesson(tester);
    await _startQuiz(tester);
    await _answerAndCheck(tester);
    await _continue(tester);
    await _leave(tester);

    // Pretend the lesson's questions changed in a content update.
    final saved = _book(store).entries.values.single;
    final json = saved.toJson()..['fp'] = 'deadbeef';
    store.setString(
      'lessonResume.v1',
      jsonEncode({
        'schema': 1,
        'lessons': [json],
      }),
    );

    await pumpApp(tester, store: store);
    expect(find.textContaining('In progress ·'), findsNothing);
    await _openFirstLesson(tester);
    expect(find.text('Welcome back!'), findsNothing);
    expect(find.text('Key points'), findsWidgets);
    expect(_book(store).isEmpty, isTrue);
  });
}
