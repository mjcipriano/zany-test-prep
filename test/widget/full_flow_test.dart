import 'dart:convert';

import 'package:flutter/material.dart';
import 'package:flutter_test/flutter_test.dart';

import '../helpers/pump_app.dart';

Future<void> onboard(WidgetTester tester) async {
  for (var i = 0; i < 4; i++) {
    await tester.tap(find.text('Continue'));
    await tester.pumpAndSettle();
  }
  await tester.tap(find.text('Start learning'));
  await tester.pumpAndSettle();
}

/// Plays a lesson to completion by answering every question (correctly when it
/// can, otherwise just submitting) until the summary appears.
Future<void> completeOpenLesson(WidgetTester tester) async {
  await tester.tap(find.text('Start'));
  await tester.pumpAndSettle();

  for (var guard = 0; guard < 80; guard++) {
    if (find.text('Lesson complete!').evaluate().isNotEmpty) return;

    if (find.text('Check').evaluate().isNotEmpty) {
      final field = find.byType(TextField);
      if (field.evaluate().isNotEmpty) {
        await tester.enterText(field.first, '1');
      } else {
        await tester.tap(find.text('A').first); // pick the first choice
      }
      await tester.pumpAndSettle();
      if (find.text('Check').evaluate().isNotEmpty) {
        await tester.tap(find.text('Check'));
        await tester.pumpAndSettle();
      }
    } else if (find.text('Finish').evaluate().isNotEmpty) {
      await tester.tap(find.text('Finish'));
      await tester.pumpAndSettle();
    } else if (find.text('Continue').evaluate().isNotEmpty) {
      await tester.tap(find.text('Continue'));
      await tester.pumpAndSettle();
    }
  }
  fail('lesson did not reach the summary screen');
}

void main() {
  testWidgets(
    'launch -> onboard -> complete a lesson -> XP increases -> persists on reload',
    (tester) async {
      final store = await pumpApp(tester);

      // Onboarding.
      expect(find.text('Welcome to Zany Test Prep'), findsOneWidget);
      await onboard(tester);
      expect(find.text('READING & WRITING'), findsOneWidget);

      // Open the first lesson and complete it.
      await tester.tap(find.text('Main Idea').first);
      await tester.pumpAndSettle();
      await completeOpenLesson(tester);

      // Summary shows and reports earned XP.
      expect(find.text('Lesson complete!'), findsOneWidget);
      expect(find.textContaining('XP'), findsWidgets);

      // Progress was persisted with non-zero XP.
      final raw = store.getString('progress.v1');
      expect(raw, isNotNull);
      final totalXp = (jsonDecode(raw!)['game'] as Map)['totalXp'] as int;
      expect(totalXp, greaterThan(0));

      // Return home.
      await tester.tap(find.text('Continue'));
      await tester.pumpAndSettle();
      expect(find.text('Zany Test Prep'), findsOneWidget);

      // Simulate an app restart with the SAME storage: state must survive.
      await pumpApp(tester, store: store);
      // We skip onboarding (already onboarded) and land on home.
      expect(find.text('Welcome to Zany Test Prep'), findsNothing);
      expect(find.text('READING & WRITING'), findsOneWidget);
      final rawAfter = store.getString('progress.v1');
      final xpAfter = (jsonDecode(rawAfter!)['game'] as Map)['totalXp'] as int;
      expect(xpAfter, totalXp);
    },
  );
}
