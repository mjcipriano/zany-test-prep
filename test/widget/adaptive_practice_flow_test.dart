import 'dart:convert';

import 'package:flutter/material.dart';
import 'package:flutter_test/flutter_test.dart';
import 'package:zany_test_prep/data/local/key_value_store.dart';
import 'package:zany_test_prep/domain/models/progress.dart';
import 'package:zany_test_prep/features/lessons/question_view.dart';

import '../helpers/adaptive_fixtures.dart';
import '../helpers/pump_app.dart';

/// Seeds a persisted profile + progress so the app opens straight on Home.
MemoryStore _seededStore(AppProgress progress, {String examId = 'sat'}) {
  final store = MemoryStore();
  store.setString('onboarded.v1', 'true');
  store.setString(
    'profile.v1',
    jsonEncode({
      'examId': examId,
      'dailyGoalMinutes': 10,
      'createdAt': DateTime(2025).toIso8601String(),
    }),
  );
  store.setString('progress.v1', jsonEncode(progress.toJson()));
  return store;
}

/// Onboarding up to the last step (the placement-check offer).
Future<void> _toPlacementStep(WidgetTester tester, {String? exam}) async {
  await tester.tap(find.text('Continue')); // welcome -> offline
  await tester.pumpAndSettle();
  await tester.tap(find.text('Continue')); // offline -> exam
  await tester.pumpAndSettle();
  if (exam != null) {
    await tester.tap(find.text(exam));
    await tester.pumpAndSettle();
  }
  await tester.tap(find.text('Continue')); // exam -> goal (+ date)
  await tester.pumpAndSettle();
  await tester.tap(find.text('Continue')); // goal -> placement
  await tester.pumpAndSettle();
  expect(find.text('Find your starting point'), findsOneWidget);
}

/// Answers the placement check: the first [right] questions correctly, the
/// rest with "Not sure". Returns how many questions there were.
Future<int> _answerCheck(WidgetTester tester, {required int right}) async {
  var n = 0;
  while (find.byType(QuestionView).evaluate().isNotEmpty) {
    final view = tester.widget<QuestionView>(find.byType(QuestionView));
    final q = view.question;
    if (n < right) {
      if (q.type.isStudentProduced) {
        await tester.enterText(
          find.byType(TextField),
          q.answer!.accepted.first,
        );
      } else {
        view.onSelectChoice(q.correctChoice!);
      }
      await tester.pump();
      final next = find.text('Next');
      await tester.tap(next.evaluate().isNotEmpty ? next : find.text('Finish'));
    } else {
      await tester.tap(find.text('Not sure'));
    }
    await tester.pumpAndSettle();
    n++;
  }
  return n;
}

void main() {
  group('onboarding placement check', () {
    for (final (exam, label, domainName) in [
      ('sat', 'SAT', 'Reading & Writing'),
      ('act', 'ACT', 'Science'),
    ]) {
      testWidgets('$exam: take the check, see the summary, get a pick', (
        tester,
      ) async {
        await pumpApp(tester);
        await _toPlacementStep(tester, exam: exam == 'sat' ? null : label);
        await tester.tap(find.text('Take the quick check'));
        await tester.pumpAndSettle();

        expect(find.textContaining('Placement check'), findsOneWidget);
        expect(find.text('1/12'), findsOneWidget);

        final total = await _answerCheck(tester, right: 6);
        expect(total, 12);
        expect(find.text('Your starting point'), findsOneWidget);
        expect(find.text('You got 6 of 12 right.'), findsOneWidget);
        expect(find.text('Strong'), findsOneWidget);
        expect(find.text('Focus'), findsOneWidget);
        expect(find.text(domainName), findsOneWidget);

        await tester.tap(find.text('Start learning'));
        await tester.pumpAndSettle();

        // Home: tuned recommendation, no nag card, and no XP for the check.
        expect(find.text('Recommended for you'), findsOneWidget);
        expect(find.textContaining('Weakest: '), findsOneWidget);
        expect(find.text('Personalize your plan'), findsNothing);
        expect(find.text('0 XP'), findsOneWidget);
      });
    }

    testWidgets('skipping goes home and keeps offering the check', (
      tester,
    ) async {
      await pumpApp(tester);
      await _toPlacementStep(tester);
      await tester.tap(find.text('Start learning'));
      await tester.pumpAndSettle();

      expect(find.text('Zany Test Prep'), findsOneWidget);
      expect(find.text('Personalize your plan'), findsOneWidget);
      // Nothing to go on yet: no recommendation card.
      expect(find.text('Recommended for you'), findsNothing);
    });

    testWidgets('the date picker now lives on the goal step', (tester) async {
      await pumpApp(tester);
      for (var i = 0; i < 3; i++) {
        await tester.tap(find.text('Continue'));
        await tester.pumpAndSettle();
      }
      expect(find.text('Pick a daily goal'), findsOneWidget);
      expect(find.text('Test date (optional)'), findsOneWidget);
      expect(find.text('Pick a date'), findsOneWidget);
    });

    testWidgets('leaving the check midway keeps it offered on Home', (
      tester,
    ) async {
      await pumpApp(tester);
      await _toPlacementStep(tester);
      await tester.tap(find.text('Take the quick check'));
      await tester.pumpAndSettle();
      await tester.tap(find.byTooltip('Leave the check'));
      await tester.pumpAndSettle();
      expect(find.text('Personalize your plan'), findsOneWidget);
    });
  });

  group('home recommendation card', () {
    testWidgets('names the weakest skill and opens Smart Practice', (
      tester,
    ) async {
      final sat = realBundle('sat');
      final weak = sat.skillMap.domains.last.sections.first.skills.first;
      final progress = AppProgress();
      for (final d in sat.skillMap.domains) {
        for (final s in d.sections) {
          for (final k in s.skills) {
            progress.skillMastery[k.id] = SkillMastery(
              skillId: k.id,
              mastery: k.id == weak.id ? 5 : 75,
              attempts: 12,
            );
          }
        }
      }
      await pumpApp(tester, store: _seededStore(progress));

      final card = find.byKey(const Key('recommended-card'));
      expect(card, findsOneWidget);
      expect(find.text('Smart practice'), findsOneWidget);
      expect(find.text('Weakest: ${weak.name}'), findsOneWidget);

      await tester.tap(card);
      await tester.pumpAndSettle();
      expect(find.text('Check'), findsOneWidget);
      expect(find.text('1/12'), findsOneWidget);
    });

    testWidgets('shows due reviews first', (tester) async {
      final sat = realBundle('sat');
      final progress = AppProgress(
        skillMastery: {
          'x': SkillMastery(skillId: 'x', mastery: 50, attempts: 3),
        },
      );
      for (final q in sat.questions.take(3)) {
        progress.reviewQueue.add(
          ReviewItem(questionId: q.id, skillId: q.skill, dueDay: '2020-01-01'),
        );
      }
      await pumpApp(tester, store: _seededStore(progress));
      expect(find.text('Review your misses'), findsOneWidget);
      expect(find.text('3 reviews due'), findsOneWidget);
      await tester.tap(find.byKey(const Key('recommended-card')));
      await tester.pumpAndSettle();
      expect(find.text('Check'), findsOneWidget);
    });

    testWidgets('ACT: card uses ACT skills', (tester) async {
      final act = realBundle('act');
      final science = act.skillMap.domains.firstWhere((d) => d.id == 'science');
      final weak = science.sections.first.skills.first;
      final progress = AppProgress();
      for (final d in act.skillMap.domains) {
        for (final s in d.sections) {
          for (final k in s.skills) {
            final key = masteryKey('act', k.id);
            progress.skillMastery[key] = SkillMastery(
              skillId: key,
              mastery: k.id == weak.id ? 5 : 80,
              attempts: 12,
            );
          }
        }
      }
      await pumpApp(tester, store: _seededStore(progress, examId: 'act'));
      expect(find.text('Weakest: ${weak.name}'), findsOneWidget);
    });
  });

  testWidgets('Smart Practice tile starts an adaptive session', (tester) async {
    await pumpApp(tester);
    await onboardDefault(tester);
    await tester.tap(find.text('Smart Practice'));
    await tester.pumpAndSettle();
    expect(find.text('Check'), findsOneWidget);
    expect(find.text('1/12'), findsOneWidget);
  });

  testWidgets('Settings can retake the placement check', (tester) async {
    await pumpApp(tester);
    await onboardDefault(tester);
    await tester.tap(find.byTooltip('Settings'));
    await tester.pumpAndSettle();
    await tester.tap(find.text('Placement check'));
    await tester.pumpAndSettle();
    expect(find.textContaining('Placement check —'), findsOneWidget);
  });
}
