import 'package:flutter/material.dart';
import 'package:flutter_test/flutter_test.dart';

import '../helpers/pump_app.dart';

Future<void> _onboard(WidgetTester tester) async {
  for (var i = 0; i < 4; i++) {
    await tester.tap(find.text('Continue'));
    await tester.pumpAndSettle();
  }
  await tester.tap(find.text('Start learning'));
  await tester.pumpAndSettle();
}

void main() {
  testWidgets('progress dashboard opens from the home app bar', (tester) async {
    await pumpApp(tester);
    await _onboard(tester);
    await tester.tap(find.byIcon(Icons.bar_chart_rounded));
    await tester.pumpAndSettle();
    expect(find.text('Estimated SAT score'), findsOneWidget);
    expect(find.text('XP — last 14 days'.toUpperCase()), findsOneWidget);
  });

  testWidgets('diagnostic card launches the diagnostic for new users', (
    tester,
  ) async {
    await pumpApp(tester);
    await _onboard(tester);
    expect(find.text('Personalize your plan'), findsOneWidget);
    await tester.tap(find.text('Take it'));
    await tester.pumpAndSettle();
    expect(find.textContaining('Diagnostic'), findsOneWidget);
    expect(find.text('Next'), findsOneWidget);
  });

  testWidgets('timed practice test shows its intro and structure', (
    tester,
  ) async {
    await pumpApp(tester);
    await _onboard(tester);
    await tester.tap(find.text('Practice Test'));
    await tester.pumpAndSettle();
    expect(find.text('Begin test'), findsOneWidget);
    expect(find.textContaining('Reading & Writing — Module 1'), findsOneWidget);
  });
}
