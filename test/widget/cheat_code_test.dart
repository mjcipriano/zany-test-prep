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
  // Note: the "quick succession" reset relies on DateTime.now(), which the
  // widget tester's fake clock does not advance, so the slow-tap reset can only
  // be exercised on a real device. Here we verify the positive path.
  testWidgets('tapping content version 10× quickly grants 10,000 XP', (
    tester,
  ) async {
    await pumpApp(tester);
    await _onboard(tester);

    // Settings -> About.
    await tester.tap(find.byIcon(Icons.settings_rounded));
    await tester.pumpAndSettle();
    await tester.tap(find.text('About this app'));
    await tester.pumpAndSettle();

    final version = find.textContaining('Content ');
    expect(version, findsOneWidget);

    // 9 quick taps: no cheat yet.
    for (var i = 0; i < 9; i++) {
      await tester.tap(version);
      await tester.pump(const Duration(milliseconds: 50));
    }
    expect(find.textContaining('Cheat unlocked'), findsNothing);

    // 10th tap triggers the cheat.
    await tester.tap(version);
    await tester.pump();
    expect(find.textContaining('Cheat unlocked'), findsOneWidget);

    // The XP actually landed: the rewards hub shows the spendable balance.
    // (Exact match avoids also matching the snackbar's "+10000 XP!" text.)
    await tester.pumpAndSettle();
    await tester.pageBack(); // About -> Settings
    await tester.pumpAndSettle();
    await tester.pageBack(); // Settings -> Home
    await tester.pumpAndSettle();
    await tester.tap(find.byIcon(Icons.card_giftcard_rounded));
    await tester.pumpAndSettle();
    expect(find.text('10000 XP'), findsOneWidget);
  });
}
