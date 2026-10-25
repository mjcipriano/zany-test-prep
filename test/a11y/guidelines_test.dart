import 'package:flutter/material.dart';
import 'package:flutter_test/flutter_test.dart';

import '../helpers/a11y_harness.dart';

// flutter_test's Android accessibility guidelines on the main screens:
// 48x48 tap targets, a label on every tappable node, and WCAG AA text
// contrast (measured from the rendered pixels), in the light theme and on
// the dark Home screen. Phone size 360x780.

/// Skips Placement check / practice test questions whose stimulus is a data
/// table: the contrast guideline samples each table cell's whole rectangle,
/// grid lines included, and misreads the grey divider as the text colour.
Future<void> _skipTables(WidgetTester tester, String skipLabel) async {
  for (var i = 0; i < 12 && find.byType(DataTable).evaluate().isNotEmpty; i++) {
    await tester.tap(find.text(skipLabel));
    await tester.pumpAndSettle();
  }
}

Future<void> _expectGuidelines(
  WidgetTester tester, {
  bool contrast = true,
}) async {
  await expectLater(tester, meetsGuideline(androidTapTargetGuideline));
  await expectLater(tester, meetsGuideline(labeledTapTargetGuideline));
  if (contrast)
    await expectLater(tester, meetsGuideline(textContrastGuideline));
}

void main() {
  setUpAll(() async {
    if (kRealFontsAvailable) await loadRealFonts();
  });

  testWidgets('home', (tester) async {
    final handle = tester.ensureSemantics();
    await pumpPhone(tester);
    await _expectGuidelines(tester);
    handle.dispose();
  });

  testWidgets('home overflow menu', (tester) async {
    final handle = tester.ensureSemantics();
    await pumpPhone(tester);
    await tester.tap(find.byTooltip('More'));
    await tester.pumpAndSettle();
    await _expectGuidelines(tester);
    handle.dispose();
  });

  testWidgets('home, dark theme', (tester) async {
    final handle = tester.ensureSemantics();
    await pumpPhone(tester, store: a11yStore(themeMode: ThemeMode.dark));
    await _expectGuidelines(tester);
    handle.dispose();
  });

  testWidgets('lesson question, then its feedback', (tester) async {
    final handle = tester.ensureSemantics();
    await pumpPhone(tester);
    await openRoute(tester, '/lesson/${firstLessonId(tester)}');
    await _expectGuidelines(tester); // teaching card
    await startQuiz(tester);
    await _expectGuidelines(tester);
    await answerAndCheck(tester);
    await _expectGuidelines(tester);
    handle.dispose();
  });

  testWidgets('lesson feedback, dark theme', (tester) async {
    final handle = tester.ensureSemantics();
    await pumpPhone(tester, store: a11yStore(themeMode: ThemeMode.dark));
    await openRoute(tester, '/lesson/${firstLessonId(tester)}');
    await startQuiz(tester);
    await answerAndCheck(tester);
    await expectLater(tester, meetsGuideline(textContrastGuideline));
    handle.dispose();
  });

  for (final tab in ['Avatars', 'Items', 'Pets']) {
    testWidgets('store: $tab', (tester) async {
      final handle = tester.ensureSemantics();
      await pumpPhone(tester);
      await openRoute(tester, '/store');
      await tester.tap(find.text(tab));
      await tester.pumpAndSettle();
      await _expectGuidelines(tester);
      handle.dispose();
    });
  }

  testWidgets('rewards hub and avatar customizer', (tester) async {
    final handle = tester.ensureSemantics();
    await pumpPhone(tester);
    await openRoute(tester, '/rewards');
    await _expectGuidelines(tester);
    await openRoute(tester, '/avatar');
    await _expectGuidelines(tester);
    // Scrolled down to the companion and item rows.
    await tester.drag(find.byType(Scrollable).first, const Offset(0, -500));
    await tester.pumpAndSettle();
    await _expectGuidelines(tester);
    handle.dispose();
  });

  testWidgets('settings', (tester) async {
    final handle = tester.ensureSemantics();
    await pumpPhone(tester);
    await openRoute(tester, '/settings');
    await _expectGuidelines(tester);
    await tester.drag(find.byType(Scrollable).first, const Offset(0, -600));
    await tester.pumpAndSettle();
    await _expectGuidelines(tester);
    handle.dispose();
  });

  testWidgets('timed test: intro, module and question navigator', (
    tester,
  ) async {
    final handle = tester.ensureSemantics();
    await pumpPhone(tester);
    await openRoute(tester, '/test');
    await _expectGuidelines(tester);
    await beginTimedTest(tester);
    await _skipTables(tester, 'Skip');
    await _expectGuidelines(tester);
    await tester.tap(find.text('Review'));
    await tester.pumpAndSettle();
    await _expectGuidelines(tester);
    handle.dispose();
  });

  testWidgets('placement check', (tester) async {
    final handle = tester.ensureSemantics();
    await pumpPhone(tester);
    await openRoute(tester, '/diagnostic');
    await _skipTables(tester, 'Not sure');
    await _expectGuidelines(tester);
    if (await tapChoiceA(tester)) await _expectGuidelines(tester);
    handle.dispose();
  });

  testWidgets('chest reveal', (tester) async {
    final handle = tester.ensureSemantics();
    await pumpPhone(tester);
    await openRoute(tester, '/chest');
    await _expectGuidelines(tester);
    await tester.tap(find.text('Open chest'));
    await tester.pumpAndSettle();
    await _expectGuidelines(tester);
    handle.dispose();
  });

  testWidgets('progress, skills and achievements', (tester) async {
    final handle = tester.ensureSemantics();
    await pumpPhone(tester);
    for (final route in ['/dashboard', '/skills', '/achievements']) {
      await openRoute(tester, route);
      await _expectGuidelines(tester);
    }
    handle.dispose();
  });

  testWidgets('onboarding', (tester) async {
    final handle = tester.ensureSemantics();
    await pumpPhone(tester, store: a11yOnboardingStore());
    for (var i = 0; i < 4; i++) {
      await _expectGuidelines(tester);
      await tester.tap(find.text('Continue'));
      await tester.pumpAndSettle();
    }
    await _expectGuidelines(tester);
    handle.dispose();
  });
}
