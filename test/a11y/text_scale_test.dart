import 'package:flutter/material.dart';
import 'package:flutter/rendering.dart';
import 'package:flutter_test/flutter_test.dart';

import '../helpers/a11y_harness.dart';

// The app must stay usable with Android's large font sizes on a 360x780
// phone: every key screen is pumped at text scale 1.3, 1.6 and 2.0 and
// scrolled end to end; any RenderFlex overflow (or other layout error)
// fails the test. Runs with the real Roboto metrics (the default test font
// draws every glyph a full em wide, about twice Roboto's width).

typedef _Visit = Future<void> Function(WidgetTester tester);

final Map<String, _Visit> _screens = {
  'home': (t) async {},
  'home overflow menu': (t) async {
    await t.tap(find.byTooltip('More'));
    await t.pumpAndSettle();
  },
  'lesson teaching card': (t) => openRoute(t, '/lesson/${firstLessonId(t)}'),
  'lesson question + feedback': (t) async {
    await openRoute(t, '/lesson/${firstLessonId(t)}');
    await startQuiz(t);
    await scrollThrough(t);
    await answerAndCheck(t);
  },
  'rewards': (t) => openRoute(t, '/rewards'),
  'store (all tabs)': (t) async {
    await openRoute(t, '/store');
    for (final tab in ['Items', 'Pets']) {
      await scrollThrough(t);
      await t.tap(find.text(tab));
      await t.pumpAndSettle();
    }
  },
  'avatar customizer': (t) => openRoute(t, '/avatar'),
  'avatar full screen': (t) async {
    await openRoute(t, '/rewards');
    await t.tap(find.bySemanticsLabel(RegExp('^Your avatar')).first);
    await t.pumpAndSettle();
  },
  'chest reveal': (t) async {
    await openRoute(t, '/chest');
    await scrollThrough(t);
    await t.tap(find.text('Open chest'));
    await t.pumpAndSettle();
  },
  'settings': (t) => openRoute(t, '/settings'),
  'about + backup': (t) async {
    await openRoute(t, '/about');
    await scrollThrough(t);
    await openRoute(t, '/backup');
  },
  'progress, skills, achievements': (t) async {
    for (final r in ['/dashboard', '/skills', '/achievements']) {
      await openRoute(t, r);
      await scrollThrough(t);
    }
  },
  'timed test intro + module + navigator': (t) async {
    await openRoute(t, '/test');
    await scrollThrough(t);
    await t.pageBack();
    await t.pumpAndSettle();
    await beginTimedTest(t);
    await scrollThrough(t);
    await t.tap(find.text('Review'));
    await t.pumpAndSettle();
  },
  'placement check': (t) async {
    await openRoute(t, '/diagnostic');
    await scrollThrough(t);
    await tapChoiceA(t);
  },
  'practice + survival': (t) async {
    await openRoute(t, '/practice/smart');
    await scrollThrough(t);
    await openRoute(t, '/survival');
  },
};

void main() {
  setUpAll(() async {
    if (kRealFontsAvailable) await loadRealFonts();
  });

  for (final scale in kA11yTextScales.where((s) => s > 1)) {
    group('text scale $scale', () {
      for (final MapEntry(key: name, value: visit) in _screens.entries) {
        testWidgets('$name lays out without overflow', (tester) async {
          await pumpPhone(tester, textScale: scale);
          await visit(tester);
          await scrollThrough(tester);
          expect(tester.takeException(), isNull);
        }, skip: !kRealFontsAvailable);
      }

      testWidgets('onboarding lays out without overflow', (tester) async {
        await pumpPhone(tester, store: a11yOnboardingStore(), textScale: scale);
        for (var i = 0; i < 4; i++) {
          await scrollThrough(tester);
          await tester.tap(find.text('Continue'));
          await tester.pumpAndSettle();
        }
        await scrollThrough(tester);
        expect(tester.takeException(), isNull);
      }, skip: !kRealFontsAvailable);
    });
  }

  group('home app bar on a 360dp phone', () {
    testWidgets('shows the whole title at the default text size', (
      tester,
    ) async {
      await pumpPhone(tester);
      final title = tester.renderObject<RenderParagraph>(
        find.text('Zany Test Prep'),
      );
      expect(title.didExceedMaxLines, isFalse);
      expect(
        title.size.width,
        greaterThanOrEqualTo(title.getMaxIntrinsicWidth(double.infinity) - 1),
        reason: 'the title should not be ellipsized ("Zany T…")',
      );
    }, skip: !kRealFontsAvailable);

    testWidgets('keeps Rewards and Settings one tap away; the rest in More', (
      tester,
    ) async {
      await pumpPhone(tester);
      expect(find.byTooltip('Rewards, 2 chests to open'), findsOneWidget);
      expect(find.byTooltip('Settings'), findsOneWidget);
      await tester.tap(find.byTooltip('More'));
      await tester.pumpAndSettle();
      await tester.tap(find.text('Achievements'));
      await tester.pumpAndSettle();
      expect(find.textContaining('unlocked'), findsOneWidget);
    });

    testWidgets(
      'quick actions go one per row at large text sizes',
      (tester) async {
        await pumpPhone(tester, textScale: 2.0);
        await tester.scrollUntilVisible(
          find.text('Skills'),
          200,
          scrollable: find.byType(Scrollable).first,
        );
        final review = tester.getRect(find.text('Review'));
        final skills = tester.getRect(find.text('Skills'));
        expect(skills.top, greaterThan(review.bottom));
      },
      skip: !kRealFontsAvailable,
    );
  });
}
