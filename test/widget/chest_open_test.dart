import 'dart:convert';

import 'package:flutter/material.dart';
import 'package:flutter_test/flutter_test.dart';
import 'package:zany_test_prep/data/local/key_value_store.dart';
import 'package:zany_test_prep/domain/models/profile.dart';
import 'package:zany_test_prep/domain/models/progress.dart';

import '../helpers/pump_app.dart';

/// Seeds an onboarded user that already has [chests] chests banked.
MemoryStore _seededStore({int chests = 1}) {
  final store = MemoryStore();
  store.setString('onboarded.v1', 'true');
  store.setString(
    'profile.v1',
    jsonEncode(UserProfile.initial('sat', 10).toJson()),
  );
  final progress = AppProgress();
  progress.game.unopenedChests = chests;
  progress.game.totalXp = 500; // enough that any reward roll is valid
  store.setString('progress.v1', jsonEncode(progress.toJson()));
  return store;
}

void main() {
  testWidgets('opening a chest reveals a reward and consumes the chest', (
    tester,
  ) async {
    await pumpApp(tester, store: _seededStore(chests: 1));

    // Home shows the rewards/gift action; open the rewards hub.
    await tester.tap(find.byIcon(Icons.card_giftcard_rounded));
    await tester.pumpAndSettle();
    expect(find.text('1 chest to open'), findsOneWidget);

    // Into the animated chest screen.
    await tester.tap(find.text('Open'));
    await tester.pumpAndSettle();
    expect(find.text('Tap the chest to open it!'), findsOneWidget);

    // Open it: roll the reward, then drive the reveal animation to completion.
    await tester.tap(find.text('Open chest'));
    await tester.pump(); // kick off the async roll
    await tester.pump(const Duration(milliseconds: 50));
    await tester.pump(const Duration(seconds: 2)); // finish the animation
    await tester.pumpAndSettle();

    // Revealed state: a "Done" button is shown and only one chest existed,
    // so there is no "Open another".
    expect(find.text('Done'), findsOneWidget);
    expect(find.textContaining('Open another'), findsNothing);

    // Back to the hub — the chest is now spent.
    await tester.tap(find.text('Done'));
    await tester.pumpAndSettle();
    expect(find.text('No chests yet'), findsOneWidget);
  });

  testWidgets('with multiple chests, "Open another" is offered', (
    tester,
  ) async {
    await pumpApp(tester, store: _seededStore(chests: 2));

    await tester.tap(find.byIcon(Icons.card_giftcard_rounded));
    await tester.pumpAndSettle();
    expect(find.text('2 chests to open'), findsOneWidget);

    await tester.tap(find.text('Open'));
    await tester.pumpAndSettle();
    await tester.tap(find.text('Open chest'));
    await tester.pump();
    await tester.pump(const Duration(milliseconds: 50));
    await tester.pump(const Duration(seconds: 2));
    await tester.pumpAndSettle();

    // One chest left -> can open another.
    expect(find.textContaining('Open another'), findsOneWidget);
  });
}
