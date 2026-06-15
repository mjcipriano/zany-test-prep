import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:flutter_test/flutter_test.dart';
import 'package:integration_test/integration_test.dart';
import 'package:shared_preferences/shared_preferences.dart';
import 'package:zany_test_prep/app/app.dart';
import 'package:zany_test_prep/core/sound_service.dart';

/// On-device integration test: launch -> onboard -> complete a lesson -> XP
/// updates. Run with: flutter test integration_test
///
/// (The same end-to-end flow, including persistence across a simulated restart,
/// is also covered headlessly by test/widget/full_flow_test.dart so it runs in
/// CI without a device.)
void main() {
  IntegrationTestWidgetsFlutterBinding.ensureInitialized();

  setUp(() => SharedPreferences.setMockInitialValues({}));

  testWidgets('complete onboarding and a lesson, earning XP', (tester) async {
    tester.view.physicalSize = const Size(1000, 3200);
    tester.view.devicePixelRatio = 1.0;
    addTearDown(() {
      tester.view.resetPhysicalSize();
      tester.view.resetDevicePixelRatio();
    });

    await tester.pumpWidget(
      ProviderScope(
        overrides: [soundServiceProvider.overrideWithValue(NoopSoundService())],
        child: const ZanyTestPrepApp(),
      ),
    );
    await tester.pumpAndSettle();

    // Onboarding.
    expect(find.text('Welcome to Zany Test Prep'), findsOneWidget);
    for (var i = 0; i < 4; i++) {
      await tester.tap(find.text('Continue'));
      await tester.pumpAndSettle();
    }
    await tester.tap(find.text('Start learning'));
    await tester.pumpAndSettle();
    expect(find.text('READING & WRITING'), findsOneWidget);

    // Open and complete the first lesson.
    await tester.tap(find.textContaining('Main Idea').first);
    await tester.pumpAndSettle();
    await tester.tap(find.text('Start'));
    await tester.pumpAndSettle();

    for (var guard = 0; guard < 80; guard++) {
      if (find.text('Lesson complete!').evaluate().isNotEmpty) break;
      if (find.text('Check').evaluate().isNotEmpty) {
        final field = find.byType(TextField);
        if (field.evaluate().isNotEmpty) {
          await tester.enterText(field.first, '1');
        } else {
          await tester.tap(find.text('A').first);
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

    expect(find.text('Lesson complete!'), findsOneWidget);
    expect(find.textContaining('XP'), findsWidgets);
  });
}
