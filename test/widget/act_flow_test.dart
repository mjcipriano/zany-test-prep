import 'dart:convert';

import 'package:flutter/material.dart';
import 'package:flutter_test/flutter_test.dart';

import '../helpers/pump_app.dart';

/// End-to-end ACT coverage: the exam picker offers the ACT, choosing it loads
/// the ACT bundle, the home path shows all four ACT sections, the practice
/// test uses the ACT layout and scale, and Settings can switch back to the SAT.
void main() {
  testWidgets('onboarding offers the ACT and home shows its four sections', (
    tester,
  ) async {
    final store = await pumpApp(tester);
    await onboardWithExam(tester, 'ACT');

    expect(find.text('ENGLISH'), findsOneWidget);
    expect(find.text('MATH'), findsOneWidget);
    expect(find.text('READING'), findsOneWidget);
    expect(find.text('SCIENCE'), findsOneWidget);
    expect(find.text('READING & WRITING'), findsNothing);

    // The profile remembers the exam, so a restart lands on the ACT path.
    final profile = jsonDecode(store.getString('profile.v1')!) as Map;
    expect(profile['examId'], 'act');
    await pumpApp(tester, store: store);
    expect(find.text('SCIENCE'), findsOneWidget);
  });

  testWidgets('ACT practice test intro lists four timed sections', (
    tester,
  ) async {
    await pumpApp(tester);
    await onboardWithExam(tester, 'ACT');

    await tester.tap(find.text('Practice Test'));
    await tester.pumpAndSettle();

    expect(find.text('ACT Practice Test'), findsOneWidget);
    expect(find.text('English'), findsOneWidget);
    expect(find.text('Science'), findsOneWidget);
    expect(find.text('50 q · 35 min'), findsOneWidget);
    expect(find.text('40 q · 40 min'), findsWidgets);
    expect(find.textContaining('Total: 171 questions'), findsOneWidget);

    // Beginning the test starts the English section.
    await tester.tap(find.text('Begin test'));
    await tester.pumpAndSettle();
    expect(find.text('English'), findsOneWidget);
    expect(find.text('Question 1 of 50'), findsOneWidget);
  });

  testWidgets('an ACT science lesson plays with a table or passage stimulus', (
    tester,
  ) async {
    await pumpApp(tester);
    await onboardWithExam(tester, 'ACT');

    // Open the first Science lesson on the path.
    await tester.scrollUntilVisible(
      find.textContaining('Reading Tables').first,
      400,
      scrollable: find.byType(Scrollable).first,
    );
    await tester.tap(find.textContaining('Reading Tables').first);
    await tester.pumpAndSettle();
    for (var guard = 0; guard < 6; guard++) {
      if (find.text('Start').evaluate().isNotEmpty) break;
      await tester.tap(find.text('Next'));
      await tester.pumpAndSettle();
    }
    await tester.tap(find.text('Start'));
    await tester.pumpAndSettle();
    expect(find.text('Check'), findsOneWidget);
    expect(find.byType(Table), findsWidgets);
  });

  testWidgets('settings can switch from the ACT back to the SAT', (
    tester,
  ) async {
    final store = await pumpApp(tester);
    await onboardWithExam(tester, 'ACT');

    await tester.tap(find.byIcon(Icons.settings_rounded));
    await tester.pumpAndSettle();
    expect(find.text('Exam'), findsOneWidget);
    expect(find.text('ACT'), findsOneWidget);

    await tester.tap(find.text('Exam'));
    await tester.pumpAndSettle();
    expect(find.text('Switch exam'), findsOneWidget);
    await tester.tap(find.text('SAT'));
    await tester.pumpAndSettle();

    expect(find.text('Switched to the SAT.'), findsOneWidget);
    final profile = jsonDecode(store.getString('profile.v1')!) as Map;
    expect(profile['examId'], 'sat');

    await tester.pageBack();
    await tester.pumpAndSettle();
    expect(find.text('READING & WRITING'), findsOneWidget);
    expect(find.text('SCIENCE'), findsNothing);
  });

  testWidgets('with a single shipped exam the picker shows just that exam', (
    tester,
  ) async {
    await pumpApp(tester, examsJson: '{"enabled": ["sat"]}');
    await tester.tap(find.text('Continue'));
    await tester.pumpAndSettle();
    await tester.tap(find.text('Continue'));
    await tester.pumpAndSettle();
    expect(find.text('Choose your exam'), findsOneWidget);
    expect(find.text('SAT'), findsOneWidget);
    expect(find.text('ACT'), findsNothing);
  });
}
