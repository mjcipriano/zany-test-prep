import 'dart:async';
import 'dart:convert';
import 'dart:io';

import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:flutter_test/flutter_test.dart';
import 'package:zany_test_prep/data/local/key_value_store.dart';
import 'package:zany_test_prep/domain/models/content_bundle.dart';
import 'package:zany_test_prep/domain/models/difficulty.dart';
import 'package:zany_test_prep/domain/models/progress.dart';
import 'package:zany_test_prep/domain/models/question.dart';
import 'package:zany_test_prep/domain/services/game_service.dart';
import 'package:zany_test_prep/features/lessons/lesson_player.dart';

import '../helpers/pump_app.dart';

ContentBundle _sat() => ContentBundle.fromJson(
  jsonDecode(File('assets/content/sat.bundle.json').readAsStringSync())
      as Map<String, dynamic>,
);

/// Seeds a persisted profile + progress so the app opens straight on Home.
MemoryStore _seededStore(AppProgress progress) {
  final store = MemoryStore();
  store.setString('onboarded.v1', 'true');
  store.setString(
    'profile.v1',
    jsonEncode({
      'examId': 'sat',
      'dailyGoalMinutes': 10,
      'createdAt': DateTime(2025).toIso8601String(),
    }),
  );
  store.setString('progress.v1', jsonEncode(progress.toJson()));
  return store;
}

void main() {
  testWidgets(
    'a review session answered fully correctly still shows its summary',
    (tester) async {
      // Regression: the review screen used to recompute the due list on every
      // rebuild, so once all items were rescheduled the player was unmounted
      // before the summary could appear (and `ref` was used after dispose).
      final bundle = _sat();
      final picks = bundle.questions
          .where(
            (q) =>
                q.type == QuestionType.multipleChoice &&
                q.difficulty == Difficulty.easy &&
                q.stimulus == null,
          )
          .take(2)
          .toList();
      final progress = AppProgress();
      for (final q in picks) {
        progress.reviewQueue.add(
          ReviewItem(questionId: q.id, skillId: q.skill, dueDay: '2020-01-01'),
        );
      }
      await pumpApp(tester, store: _seededStore(progress));
      expect(find.text('Zany Test Prep'), findsOneWidget);
      await tester.tap(find.text('Review'));
      await tester.pumpAndSettle();

      for (var i = 0; i < picks.length; i++) {
        // Identify the question on screen and tap its correct choice.
        final shown = picks.firstWhere(
          (q) => find.text(q.prompt).evaluate().isNotEmpty,
        );
        await tester.tap(find.text(shown.correct!.text).first);
        await tester.pumpAndSettle();
        await tester.tap(find.text('Check'));
        await tester.pumpAndSettle();
        await tester.tap(
          find.text(i == picks.length - 1 ? 'Finish' : 'Continue'),
        );
        await tester.pumpAndSettle();
      }
      expect(find.text('Nothing to review right now.'), findsNothing);
      expect(find.textContaining('XP'), findsWidgets);
      expect(find.text('Continue'), findsOneWidget); // summary's exit button
      expect(tester.takeException(), isNull);
    },
  );

  testWidgets('a double-tap on Finish applies the result only once', (
    tester,
  ) async {
    final bundle = _sat();
    final q = bundle.questions.firstWhere(
      (q) => q.type == QuestionType.multipleChoice && q.stimulus == null,
    );
    var completions = 0;
    final gate = Completer<LessonOutcome>();
    await tester.pumpWidget(
      ProviderScope(
        overrides: testOverrides(MemoryStore()),
        child: MaterialApp(
          home: LessonPlayer(
            title: 't',
            questions: [q],
            isReview: true,
            onComplete: (results) {
              completions++;
              return gate.future;
            },
          ),
        ),
      ),
    );
    await tester.pumpAndSettle();
    await tester.tap(find.text(q.choices.first.text).first);
    await tester.pumpAndSettle();
    await tester.tap(find.text('Check'));
    await tester.pumpAndSettle();
    await tester.tap(find.text('Finish'));
    await tester.pump();
    // Second tap while the save is still pending.
    await tester.tap(find.byType(FilledButton).first, warnIfMissed: false);
    await tester.pump();
    expect(completions, 1);
    gate.complete(
      const LessonOutcome(
        xpGained: 10,
        correct: 1,
        total: 1,
        stars: 3,
        leveledUp: false,
        oldLevel: 1,
        newLevel: 1,
        currentStreak: 1,
        streakExtended: true,
        streakReset: false,
        dailyGoalMet: false,
        dailyGoalJustMet: false,
        newBadges: [],
      ),
    );
    await tester.pumpAndSettle();
    expect(completions, 1);
    expect(find.textContaining('XP'), findsWidgets);
  });
}
