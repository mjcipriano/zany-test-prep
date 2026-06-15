import 'package:flutter_test/flutter_test.dart';

import '../helpers/pump_app.dart';

void main() {
  testWidgets('onboarding flows from welcome to the home screen', (
    tester,
  ) async {
    await pumpApp(tester);

    // Welcome step.
    expect(find.text('Welcome to Zany Test Prep'), findsOneWidget);

    // Step through: welcome -> offline -> exam -> goal -> date.
    for (var i = 0; i < 4; i++) {
      await tester.tap(find.text('Continue'));
      await tester.pumpAndSettle();
    }
    expect(find.text('When is your test?'), findsOneWidget);

    // Finish onboarding.
    await tester.tap(find.text('Start learning'));
    await tester.pumpAndSettle();

    // We should now be on the home screen.
    expect(find.text('Zany Test Prep'), findsOneWidget);
    expect(find.text('READING & WRITING'), findsOneWidget);
  });

  testWidgets('daily goal selection is reflected on home', (tester) async {
    await pumpApp(tester);
    // Advance to the goal step (welcome -> offline -> exam -> goal).
    for (var i = 0; i < 3; i++) {
      await tester.tap(find.text('Continue'));
      await tester.pumpAndSettle();
    }
    expect(find.text('Pick a daily goal'), findsOneWidget);
    await tester.tap(find.text('15 minutes a day'));
    await tester.pumpAndSettle();
    await tester.tap(find.text('Continue')); // to date step
    await tester.pumpAndSettle();
    await tester.tap(find.text('Start learning'));
    await tester.pumpAndSettle();

    // 15 min goal -> 75 XP daily goal shown on home.
    expect(find.textContaining('/ 75 XP'), findsOneWidget);
  });
}
