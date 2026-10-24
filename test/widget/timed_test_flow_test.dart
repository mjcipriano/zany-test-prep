import 'package:flutter/material.dart';
import 'package:flutter_test/flutter_test.dart';

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
    expect(find.text('Section complete'), findsOneWidget);
    expect(tester.takeException(), isNull);
  });
}
