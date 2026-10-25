import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:flutter_test/flutter_test.dart';
import 'package:zany_test_prep/app/app_controller.dart';
import 'package:zany_test_prep/data/local/key_value_store.dart';
import 'package:zany_test_prep/features/settings/cheat_tap.dart';

import '../helpers/pump_app.dart';

int _xp(WidgetTester tester) {
  final container = ProviderScope.containerOf(
    tester.element(find.byType(Scaffold).first),
  );
  return container
      .read(appControllerProvider)
      .requireValue
      .progress
      .game
      .totalXp;
}

Future<void> _openSettings(WidgetTester tester) async {
  await pumpApp(tester);
  await onboardDefault(tester);
  await tester.tap(find.byIcon(Icons.settings_rounded));
  await tester.pumpAndSettle();
}

/// Taps [finder] [n] times; each tap is a fresh pointer down/up.
Future<void> _tapTimes(WidgetTester tester, Finder finder, int n) async {
  for (var i = 0; i < n; i++) {
    await tester.tap(finder);
    await tester.pump(const Duration(milliseconds: 50));
  }
}

void main() {
  testWidgets('10 quick taps on the About content version grant 10,000 XP', (
    tester,
  ) async {
    await _openSettings(tester);
    await tester.tap(find.text('About this app'));
    await tester.pumpAndSettle();

    final version = find.textContaining('Content ');
    expect(version, findsOneWidget);
    final before = _xp(tester);

    await _tapTimes(tester, version, 4);
    expect(find.textContaining('more tap'), findsNothing);
    await _tapTimes(tester, version, 1); // 5th tap: countdown appears
    expect(find.text('5 more taps…'), findsOneWidget);
    await _tapTimes(tester, version, 4); // 9th tap
    expect(find.text('1 more tap…'), findsOneWidget);
    expect(find.textContaining('Cheat unlocked'), findsNothing);

    await _tapTimes(tester, version, 1); // 10th tap
    await tester.pump();
    expect(find.textContaining('Cheat unlocked'), findsOneWidget);
    expect(_xp(tester), before + kCheatXp);

    // The XP shows up in the rewards hub's spendable balance.
    await tester.pumpAndSettle();
    await tester.pageBack();
    await tester.pumpAndSettle();
    await tester.pageBack();
    await tester.pumpAndSettle();
    await tester.tap(find.byIcon(Icons.card_giftcard_rounded));
    await tester.pumpAndSettle();
    expect(find.text('${before + kCheatXp} XP'), findsOneWidget);
  });

  testWidgets('the Settings "Content version" row triggers the cheat too', (
    tester,
  ) async {
    await _openSettings(tester);
    final row = find.text('Content version');
    expect(row, findsOneWidget);
    final before = _xp(tester);
    await _tapTimes(tester, row, kCheatTaps);
    await tester.pump();
    expect(find.textContaining('Cheat unlocked'), findsOneWidget);
    expect(_xp(tester), before + kCheatXp);
  });

  testWidgets('a tap that drifts like a small scroll still counts', (
    tester,
  ) async {
    await _openSettings(tester);
    await tester.tap(find.text('About this app'));
    await tester.pumpAndSettle();
    final version = find.textContaining('Content ');
    final before = _xp(tester);
    for (var i = 0; i < kCheatTaps; i++) {
      // Press, wobble 30 px (enough for the list to claim a drag), release.
      final g = await tester.startGesture(tester.getCenter(version));
      await g.moveBy(const Offset(0, 30));
      await g.up();
      await tester.pump(const Duration(milliseconds: 50));
    }
    await tester.pump();
    expect(_xp(tester), before + kCheatXp);
  });

  testWidgets('pausing longer than the window starts the count over', (
    tester,
  ) async {
    var now = DateTime(2026, 1, 1, 12);
    final container = ProviderContainer(
      overrides: testOverrides(MemoryStore()),
    );
    addTearDown(container.dispose);
    // Load the session first: the cheat writes XP through the controller.
    await container.read(appControllerProvider.future);
    await tester.pumpWidget(
      UncontrolledProviderScope(
        container: container,
        child: MaterialApp(
          home: Scaffold(
            body: Center(
              child: CheatTapTarget(
                clock: () => now,
                child: const SizedBox(width: 120, height: 60, child: Text('v')),
              ),
            ),
          ),
        ),
      ),
    );
    await tester.pumpAndSettle();
    Future<void> tap() async {
      await tester.tap(find.text('v'));
      await tester.pump();
    }

    for (var i = 0; i < 6; i++) {
      await tap();
      now = now.add(const Duration(milliseconds: 1200)); // within the window
    }
    expect(find.text('4 more taps…'), findsOneWidget);
    now = now.add(const Duration(seconds: 2)); // too slow: start over
    for (var i = 0; i < kCheatTaps - 1; i++) {
      await tap();
      now = now.add(const Duration(milliseconds: 300));
    }
    expect(find.textContaining('Cheat unlocked'), findsNothing);
    await tap();
    await tester.pump();
    expect(find.textContaining('Cheat unlocked'), findsOneWidget);
    expect(
      container.read(appControllerProvider).requireValue.progress.game.totalXp,
      kCheatXp,
    );
  });
}
