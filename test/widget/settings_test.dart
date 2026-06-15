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
  testWidgets('settings screen shows options and the reset dialog', (
    tester,
  ) async {
    await pumpApp(tester);
    await _onboard(tester);

    await tester.tap(find.byIcon(Icons.settings_rounded));
    await tester.pumpAndSettle();

    expect(find.text('Settings'), findsOneWidget);
    expect(find.text('Daily goal'), findsOneWidget);
    expect(find.text('Theme'), findsOneWidget);
    expect(find.text('Reset progress'), findsOneWidget);

    // Reset shows a confirmation dialog that can be cancelled.
    await tester.tap(find.text('Reset progress'));
    await tester.pumpAndSettle();
    expect(find.text('Reset progress?'), findsOneWidget);
    await tester.tap(find.text('Cancel'));
    await tester.pumpAndSettle();
    expect(find.text('Reset progress?'), findsNothing);
  });

  testWidgets('about screen states the offline privacy note', (tester) async {
    await pumpApp(tester);
    await _onboard(tester);
    await tester.tap(find.byIcon(Icons.settings_rounded));
    await tester.pumpAndSettle();
    await tester.tap(find.text('About this app'));
    await tester.pumpAndSettle();

    expect(find.text('Your privacy'), findsOneWidget);
    expect(find.textContaining('works entirely offline'), findsOneWidget);
  });
}
