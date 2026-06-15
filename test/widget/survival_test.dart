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
  testWidgets('Survival mode starts a run and shows the running streak', (
    tester,
  ) async {
    await pumpApp(tester);
    await _onboard(tester);

    await tester.tap(find.textContaining('Survival'));
    await tester.pumpAndSettle();

    expect(find.text('Check'), findsOneWidget);
    expect(find.textContaining('Streak'), findsOneWidget);
  });
}
