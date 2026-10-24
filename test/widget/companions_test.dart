import 'dart:convert';

import 'package:flutter/material.dart';
import 'package:flutter_test/flutter_test.dart';
import 'package:zany_test_prep/data/local/key_value_store.dart';
import 'package:zany_test_prep/domain/models/avatar_catalog.dart';
import 'package:zany_test_prep/domain/models/progress.dart';
import 'package:zany_test_prep/domain/services/pet_engine.dart';

import '../helpers/pump_app.dart';
import 'dart:io';

final AvatarCatalog _catalog = AvatarCatalog.fromJson(
  jsonDecode(
        File('assets/avatar/manifest/avatar_catalog.json').readAsStringSync(),
      )
      as Map<String, dynamic>,
);

MemoryStore _store(AppProgress progress) {
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
  testWidgets('the customizer lists owned companions with level and equip', (
    tester,
  ) async {
    final pet = _catalog.basePets.first;
    final progress = AppProgress(
      game: GameState(ownedAssetIds: {pet.id}, petXp: {pet.lineId: 50}),
    );
    await pumpApp(tester, store: _store(progress));
    await tester.tap(find.byIcon(Icons.card_giftcard_rounded));
    await tester.pumpAndSettle();
    await tester.tap(find.text('Customize'));
    await tester.pumpAndSettle();

    expect(find.text('COMPANIONS'), findsOneWidget);
    expect(find.text(pet.name), findsOneWidget);
    expect(find.textContaining('Lv 2'), findsOneWidget);
    await tester.tap(find.widgetWithText(FilledButton, 'Equip').first);
    await tester.pumpAndSettle();
    expect(find.widgetWithText(OutlinedButton, 'Remove'), findsOneWidget);
  });

  testWidgets('a levelled companion evolves into its next stage', (
    tester,
  ) async {
    final evolvable = _catalog.pets.where(
      (p) => p.evolution != null && p.evolution!.nextId != null,
    );
    if (evolvable.isEmpty) {
      markTestSkipped('vendored pack has no pet evolution data yet');
      return;
    }
    final pet = evolvable.first;
    final next = _catalog[pet.evolution!.nextId!]!;
    final progress = AppProgress(
      game: GameState(
        ownedAssetIds: {pet.id},
        equipped: {'side_left_1': pet.id},
        petXp: {
          pet.lineId: PetEngine.thresholds[next.evolution!.requiresLevel - 1],
        },
      ),
    );
    final store = _store(progress);
    await pumpApp(tester, store: store);
    await tester.tap(find.byIcon(Icons.card_giftcard_rounded));
    await tester.pumpAndSettle();
    await tester.tap(find.text('Customize'));
    await tester.pumpAndSettle();

    expect(find.textContaining('Ready to evolve'), findsOneWidget);
    await tester.tap(find.text('Evolve'));
    await tester.pumpAndSettle();

    expect(find.textContaining('evolved into ${next.name}'), findsOneWidget);
    expect(find.text(next.name), findsWidgets);
    final saved = jsonDecode(store.getString('progress.v1')!) as Map;
    final game = saved['game'] as Map;
    expect((game['ownedAssetIds'] as List), contains(next.id));
    expect((game['equipped'] as Map)['side_left_1'], next.id);
  });

  testWidgets('the store only sells base-stage pets', (tester) async {
    await pumpApp(tester, store: _store(AppProgress()));
    await tester.tap(find.byIcon(Icons.card_giftcard_rounded));
    await tester.pumpAndSettle();
    await tester.tap(find.text('Customize'));
    await tester.pumpAndSettle();
    await tester.tap(find.text('Store'));
    await tester.pumpAndSettle();
    await tester.tap(find.text('Pets'));
    await tester.pumpAndSettle();
    expect(find.textContaining('earns pet XP'), findsOneWidget);
    for (final p in _catalog.pets.where((p) => p.isEvolvedStage)) {
      expect(find.text(p.name), findsNothing, reason: p.id);
    }
  });
}
