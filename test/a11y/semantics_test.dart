import 'package:flutter/material.dart';
import 'package:flutter/semantics.dart';
import 'package:flutter_test/flutter_test.dart';
import 'package:zany_test_prep/design/widgets.dart';
import 'package:zany_test_prep/features/rewards/avatar_view.dart';
import 'package:zany_test_prep/features/test/timed_test_screen.dart';

import '../helpers/a11y_harness.dart';

// What TalkBack users hear, and reduced motion.

/// Turns on Android's "Remove animations" for the rest of the test.
void _reduceMotion(WidgetTester tester) {
  tester.platformDispatcher.accessibilityFeaturesTestValue =
      const FakeAccessibilityFeatures(disableAnimations: true);
  addTearDown(tester.platformDispatcher.clearAccessibilityFeaturesTestValue);
}

SemanticsNode _node(WidgetTester tester, Pattern label) =>
    tester.getSemantics(find.bySemanticsLabel(label).first);

void main() {
  group('screen reader labels', () {
    testWidgets('home stats speak as words, not bare numbers', (tester) async {
      final handle = tester.ensureSemantics();
      await pumpPhone(tester);
      // The stats card reads as one item: "12 day streak, 5240 total XP,
      // Level 18, Daily goal…".
      final card = find.bySemanticsLabel(
        RegExp(r'^12 day streak\n5240 total XP\nLevel \d+\n'),
      );
      expect(card, findsOneWidget);
      final goal = _node(tester, 'Daily goal');
      expect(goal.value, matches(RegExp(r'^40 of \d+ XP$')));
      expect(
        _node(tester, RegExp(r'^Progress to level')).value,
        matches(RegExp(r'^\d+ of \d+ XP$')),
      );
      expect(find.bySemanticsLabel('Review, nothing due'), findsOneWidget);
      handle.dispose();
    });

    testWidgets('answer choices say their letter, text and state, and the '
        'result is announced', (tester) async {
      final handle = tester.ensureSemantics();
      await pumpPhone(tester);
      await openRoute(tester, '/lesson/${firstLessonId(tester)}');
      await startQuiz(tester);
      await scrollToChoices(tester);

      final choiceA = find.bySemanticsLabel(RegExp(r'^Choice A: .+'));
      expect(choiceA, findsOneWidget);
      expect(
        tester.getSemantics(choiceA),
        containsSemantics(
          isButton: true,
          isSelected: false,
          hasTapAction: true,
        ),
      );
      await tapChoiceA(tester);
      expect(
        tester.getSemantics(find.bySemanticsLabel(RegExp(r'^Choice A: .+'))),
        containsSemantics(isSelected: true),
      );

      tester.takeAnnouncements(); // ignore anything earlier
      await tester.tap(find.text('Check'));
      await tester.pumpAndSettle();

      // Choice A (the pick) carries "your answer"; scrolling through the
      // question, exactly one choice is marked as the correct answer.
      final picked = _node(tester, RegExp(r'^Choice A: [\s\S]+, your answer'));
      final pickedRight = picked.label.endsWith('your answer, correct');
      final marked = <String>{};
      final list = tester.state<ScrollableState>(find.byType(Scrollable).first);
      for (var y = 0.0; ; y += 100) {
        list.position.jumpTo(y.clamp(0, list.position.maxScrollExtent));
        await tester.pump();
        for (final e
            in find
                .bySemanticsLabel(
                  RegExp(r', (correct answer|your answer, correct)$'),
                )
                .evaluate()) {
          marked.add(
            (e as RenderObjectElement).renderObject.debugSemantics!.label,
          );
        }
        if (y >= list.position.maxScrollExtent) break;
      }
      expect(marked, hasLength(1));

      final said = tester.takeAnnouncements().map((a) => a.message).toList();
      expect(said, hasLength(1));
      if (pickedRight) {
        expect(said.single, 'Correct!');
        expect(find.text('Correct!'), findsOneWidget);
      } else {
        expect(said.single, startsWith('Not quite. The answer is '));
        expect(picked.label, endsWith('your answer, incorrect'));
        expect(find.text('Not quite'), findsOneWidget);
      }
      // Never colour alone: the result also shows as a check / cross icon.
      expect(find.byIcon(Icons.check_circle_rounded), findsWidgets);
      handle.dispose();
    });

    testWidgets('the avatar preview describes the loadout', (tester) async {
      final handle = tester.ensureSemantics();
      await pumpPhone(tester);
      await openRoute(tester, '/rewards');
      final avatar = find.bySemanticsLabel(
        RegExp(
          r'^Your avatar: \S.* wearing Round Glasses, with Study Cap Fox$',
        ),
      );
      expect(avatar, findsOneWidget);
      expect(
        tester.getSemantics(avatar),
        containsSemantics(isButton: true, hint: 'Opens full screen'),
      );
      handle.dispose();
    });

    testWidgets('customizer avatar tiles and equip buttons are named', (
      tester,
    ) async {
      final handle = tester.ensureSemantics();
      await pumpPhone(tester, store: a11yStore(equipped: false));
      await openRoute(tester, '/avatar');
      expect(
        find.bySemanticsLabel(RegExp(r'^Your avatar: \S+')),
        findsOneWidget,
      );
      await tester.scrollUntilVisible(
        find.text('Round Glasses'),
        200,
        scrollable: find.byType(Scrollable).first,
      );
      expect(find.bySemanticsLabel('Equip Round Glasses'), findsOneWidget);
      expect(find.bySemanticsLabel('Equip Study Cap Fox'), findsOneWidget);
      handle.dispose();
    });

    testWidgets('store prices say what they buy', (tester) async {
      final handle = tester.ensureSemantics();
      await pumpPhone(tester);
      await openRoute(tester, '/store');
      expect(find.bySemanticsLabel('4840 XP to spend'), findsOneWidget);
      await tester.tap(find.text('Items'));
      await tester.pumpAndSettle();
      expect(
        find.bySemanticsLabel(RegExp(r'^Buy .+ for \d+ XP$')),
        findsWidgets,
      );
      handle.dispose();
    });
  });

  group('timed test timer', () {
    test('remaining time reads naturally', () {
      expect(remainingTimeLabel(0), '0 seconds');
      expect(remainingTimeLabel(1), '1 second');
      expect(remainingTimeLabel(60), '1 minute');
      expect(remainingTimeLabel(125), '2 minutes 5 seconds');
      expect(remainingTimeLabel(-3), '0 seconds');
    });

    testWidgets('does not announce every tick; tells the time on request', (
      tester,
    ) async {
      final handle = tester.ensureSemantics();
      await pumpPhone(tester);
      await beginTimedTest(tester);
      final timer = find.byKey(const Key('test-timer'));
      final before = tester.getSemantics(timer).label;
      expect(before, matches(RegExp(r'^Time remaining: about \d+ minutes$')));
      tester.takeAnnouncements();

      // Ten seconds pass: the visible clock ticks, the spoken label and the
      // announcement queue do not.
      for (var i = 0; i < 10; i++) {
        await tester.pump(const Duration(seconds: 1));
      }
      expect(tester.getSemantics(timer).label, before);
      expect(tester.takeAnnouncements(), isEmpty);

      await tester.tap(timer);
      await tester.pump();
      final said = tester.takeAnnouncements();
      expect(said, hasLength(1));
      expect(
        said.single.message,
        matches(RegExp(r'^\d+ minutes 50 seconds left$')),
      );
      handle.dispose();
    });

    testWidgets('question navigator chips are 48dp and labelled', (
      tester,
    ) async {
      final handle = tester.ensureSemantics();
      await pumpPhone(tester);
      await beginTimedTest(tester);
      await tester.tap(find.text('Review'));
      await tester.pumpAndSettle();
      final first = find.bySemanticsLabel('Question 1, current, not answered');
      expect(first, findsOneWidget);
      final size = tester.getSize(first);
      expect(size.width, greaterThanOrEqualTo(48));
      expect(size.height, greaterThanOrEqualTo(48));
      handle.dispose();
    });
  });

  group('reduce motion', () {
    testWidgets('the avatar idle float stops', (tester) async {
      Widget preview() => const MaterialApp(
        home: Scaffold(body: AvatarPreview(layers: [], animate: true)),
      );
      await tester.pumpWidget(preview());
      expect(tester.hasRunningAnimations, isTrue);

      _reduceMotion(tester);
      await tester.pumpWidget(const SizedBox());
      await tester.pumpWidget(preview());
      expect(tester.hasRunningAnimations, isFalse);
    });

    testWidgets('progress bars fill without animating', (tester) async {
      _reduceMotion(tester);
      await tester.pumpWidget(
        const MaterialApp(home: Scaffold(body: ProgressBar(value: 0.6))),
      );
      final box = tester.widget<FractionallySizedBox>(
        find.byType(FractionallySizedBox),
      );
      expect(box.widthFactor, closeTo(0.6, 1e-9));
    });

    testWidgets('a chest opens straight to its reward', (tester) async {
      _reduceMotion(tester);
      await pumpPhone(tester);
      await openRoute(tester, '/chest');
      tester.takeAnnouncements();
      await tester.tap(find.text('Open chest'));
      await tester.pump(); // the reward is saved
      await tester.pump(); // ...and shown, with no 1.6 s shake and burst
      expect(find.text('Done'), findsOneWidget);
      final said = tester.takeAnnouncements();
      expect(said.single.message, startsWith('You got '));
    });
  });
}
