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
    'opening a lesson shows the teaching card and a question with feedback',
    (tester) async {
      await pumpApp(tester);
      await _onboard(tester);

      // Open the first lesson from the home path.
      await tester.tap(find.textContaining('Main Idea').first);
      await tester.pumpAndSettle();

      // Multi-screen mini-lesson: page through to the Start button.
      expect(find.text('Key points'), findsWidgets);
      for (var i = 0; i < 6 && find.text('Next').evaluate().isNotEmpty; i++) {
        await tester.tap(find.text('Next'));
        await tester.pumpAndSettle();
      }
      expect(find.text('Start'), findsOneWidget);
      await tester.tap(find.text('Start'));
      await tester.pumpAndSettle();

      // First question: a Check button and answer choices labelled A-D.
      expect(find.text('Check'), findsOneWidget);
      expect(find.text('A'), findsWidgets);

      // Answer the first choice and check.
      await tester.tap(find.text('A').first);
      await tester.pumpAndSettle();
      await tester.tap(find.text('Check'));
      await tester.pumpAndSettle();

      // Feedback appears (either correct or not) along with a continue affordance.
      final feedback =
          find.text('Correct!').evaluate().isNotEmpty ||
          find.text('Not quite').evaluate().isNotEmpty;
      expect(feedback, isTrue);
      expect(
        find.text('Continue').evaluate().isNotEmpty ||
            find.text('Finish').evaluate().isNotEmpty,
        isTrue,
      );
    },
  );
}
