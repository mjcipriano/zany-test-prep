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
  testWidgets(
    'Quick Practice launches a random session from unlocked sections',
    (tester) async {
      await pumpApp(tester);
      await _onboard(tester);

      await tester.tap(find.text('Quick Practice'));
      await tester.pumpAndSettle();

      // A practice session starts straight into questions (no teaching card),
      // so a Check button should be present.
      expect(find.text('Check'), findsOneWidget);
      expect(find.textContaining('/'), findsWidgets); // progress "1/15"
    },
  );

  testWidgets('Challenge mode launches a session from any section', (
    tester,
  ) async {
    await pumpApp(tester);
    await _onboard(tester);

    await tester.tap(find.text('Challenge'));
    await tester.pumpAndSettle();
    expect(find.text('Check'), findsOneWidget);
  });
}
