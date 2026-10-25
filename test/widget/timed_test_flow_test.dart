import 'dart:math';

import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:flutter_test/flutter_test.dart';
import 'package:zany_test_prep/app/app_controller.dart';
import 'package:zany_test_prep/domain/models/difficulty.dart';
import 'package:zany_test_prep/domain/models/exam.dart';
import 'package:zany_test_prep/domain/models/question.dart';
import 'package:zany_test_prep/domain/services/scoring.dart';
import 'package:zany_test_prep/domain/services/timed_test.dart';
import 'package:zany_test_prep/features/home/home_screen.dart';
import 'package:zany_test_prep/features/test/timed_test_screen.dart';

import '../helpers/pump_app.dart';

/// Starts a full practice test and moves through a module. Regression: the
/// module view's Back button used the theme's full-width minimum size inside
/// a Row, which crashed layout the moment a test began.
void main() {
  testWidgets('a SAT practice test starts, navigates, and flags questions', (
    tester,
  ) async {
    await pumpApp(tester);
    await onboardDefault(tester);

    await tester.tap(find.text('Practice Test'));
    await tester.pumpAndSettle();
    expect(find.text('SAT Practice Test'), findsOneWidget);
    expect(find.textContaining('Reading & Writing — Module 1'), findsWidgets);

    await tester.tap(find.text('Begin test'));
    await tester.pumpAndSettle();
    expect(tester.takeException(), isNull);
    expect(find.text('Question 1 of 27'), findsOneWidget);

    // Skip forward, go back, flag, and open the navigator sheet.
    await tester.tap(find.text('Skip'));
    await tester.pumpAndSettle();
    expect(find.text('Question 2 of 27'), findsOneWidget);
    await tester.tap(find.text('Back'));
    await tester.pumpAndSettle();
    expect(find.text('Question 1 of 27'), findsOneWidget);
    await tester.tap(find.byIcon(Icons.flag_outlined));
    await tester.pumpAndSettle();
    expect(find.byIcon(Icons.flag_rounded), findsOneWidget);
    await tester.tap(find.text('Review'));
    await tester.pumpAndSettle();
    expect(find.text('Jump to a question'), findsOneWidget);
    await tester.tap(find.text('Submit section'));
    await tester.pumpAndSettle();
    expect(find.text('Submit this section?'), findsOneWidget);
    await tester.tap(find.text('Submit'));
    await tester.pumpAndSettle();
    // Module 1 -> module 2 of the same section: a module transition that
    // does not reveal which way the student was routed.
    expect(find.text('Module complete'), findsOneWidget);
    expect(find.text('Module 1 of 4 done'), findsOneWidget);
    expect(find.text('Reading & Writing — Module 2'), findsOneWidget);
    expect(find.textContaining('harder'), findsNothing);
    expect(find.textContaining('easier'), findsNothing);
    expect(tester.takeException(), isNull);
  });

  testWidgets('a full adaptive SAT run routes each section and scores it', (
    tester,
  ) async {
    await pumpApp(tester);
    await onboardDefault(tester);

    // Tiny SAT-shaped plan so the run stays short.
    const plan = TimedTestPlan(
      modules: [
        TestModule(
          name: 'RW 1',
          domain: 'reading_writing',
          count: 3,
          minutes: 5,
        ),
        TestModule(
          name: 'RW 2',
          domain: 'reading_writing',
          count: 3,
          minutes: 5,
        ),
        TestModule(name: 'Math 1', domain: 'math', count: 2, minutes: 5),
        TestModule(name: 'Math 2', domain: 'math', count: 2, minutes: 5),
      ],
      adaptive: AdaptiveSpec(enabled: true),
    );
    final home = tester.element(find.byType(HomeScreen));
    final bundle = ProviderScope.containerOf(
      home,
    ).read(appControllerProvider).value!.bundle;
    // The same seed assembles the same test, so we know the right answers.
    final mirror = TestAssembler(bundle.questions, plan, Random(42));
    final rw1 = mirror.buildModule(0);
    final rw2 = mirror.buildModule(1, route: SectionRoute.harder);
    expect(rw2.where((q) => q.difficulty == Difficulty.hard).length, 2);

    Navigator.of(home).push(
      MaterialPageRoute<void>(
        builder: (_) => TimedTestScreen(plan: plan, random: Random(42)),
      ),
    );
    await tester.pumpAndSettle();
    expect(
      find.textContaining('second module of each section adapts'),
      findsOneWidget,
    );
    await tester.tap(find.text('Begin test'));
    await tester.pumpAndSettle();

    Future<void> answerAll(List<Question> qs) async {
      for (final (i, q) in qs.indexed) {
        expect(find.text('Question ${i + 1} of ${qs.length}'), findsOneWidget);
        if (q.type.isStudentProduced) {
          await tester.enterText(
            find.byType(TextField),
            q.answer!.accepted.first,
          );
        } else {
          final choice = find.text(q.correctChoice!).last;
          await tester.ensureVisible(choice);
          await tester.tap(choice);
        }
        await tester.pumpAndSettle();
        await tester.tap(
          find.text(i < qs.length - 1 ? 'Next' : 'Submit section'),
        );
        await tester.pumpAndSettle();
      }
      await tester.tap(find.text('Submit'));
      await tester.pumpAndSettle();
    }

    Future<void> skipAll(int n) async {
      for (var i = 0; i < n - 1; i++) {
        await tester.tap(find.text('Skip'));
        await tester.pumpAndSettle();
      }
      await tester.tap(find.text('Submit section'));
      await tester.pumpAndSettle();
      await tester.tap(find.text('Submit'));
      await tester.pumpAndSettle();
    }

    // Reading & Writing: ace module 1 -> routed to the harder module 2.
    await answerAll(rw1);
    expect(find.text('Module complete'), findsOneWidget);
    expect(find.text('3 questions · 5 min'), findsOneWidget);
    await tester.tap(find.text('Start next module'));
    await tester.pumpAndSettle();
    await answerAll(rw2);

    // Section boundary: the break screen between sections.
    expect(find.text('Section complete'), findsOneWidget);
    expect(find.textContaining('10-minute break'), findsOneWidget);
    await tester.tap(find.text('Start next section'));
    await tester.pumpAndSettle();

    // Math: blank module 1 -> routed to the easier module 2.
    await skipAll(2);
    expect(find.text('Module complete'), findsOneWidget);
    await tester.tap(find.text('Start next module'));
    await tester.pumpAndSettle();
    await skipAll(2);

    expect(find.text('Test results'), findsOneWidget);
    expect(find.text('Module 2: harder set'), findsOneWidget);
    expect(find.text('Module 2: easier set'), findsOneWidget);
    expect(find.text('6 / 6 correct'), findsOneWidget);
    expect(find.text('0 / 4 correct'), findsOneWidget);
    expect(find.text('800'), findsOneWidget); // RW, harder route, perfect
    expect(find.text('200'), findsOneWidget); // Math floor
    expect(find.text('1000'), findsOneWidget);
    expect(find.textContaining('Estimate only'), findsOneWidget);
    expect(tester.takeException(), isNull);
  });
}
