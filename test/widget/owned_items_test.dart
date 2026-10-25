import 'dart:convert';

import 'package:flutter/material.dart';
import 'package:flutter_test/flutter_test.dart';
import 'package:zany_test_prep/data/local/key_value_store.dart';
import 'package:zany_test_prep/domain/models/profile.dart';
import 'package:zany_test_prep/domain/models/progress.dart';

import 'package:zany_test_prep/features/rewards/avatar_view.dart';

import '../helpers/pump_app.dart';

// Real catalog asset ids (assets/avatar/manifest/avatar_catalog.json), one per
// worn category plus a side pet.
const _hat = 'item_249_silver_studs'; // "Silver Studs" (ear_accessory)
const _glasses = 'item_041_round_glasses'; // "Round Glasses" (eyewear)
const _mask = 'item_071_simple_mask'; // "Simple Mask" (face_accessory)
const _pet = 'pet_fox_study_cap_001'; // "Study Cap Fox" (side slots)

MemoryStore _storeOwning(Set<String> owned) {
  final store = MemoryStore();
  store.setString('onboarded.v1', 'true');
  store.setString(
    'profile.v1',
    jsonEncode(UserProfile.initial('sat', 10).toJson()),
  );
  final progress = AppProgress();
  progress.game.totalXp = 5000;
  progress.game.ownedAssetIds.addAll(owned);
  store.setString('progress.v1', jsonEncode(progress.toJson()));
  return store;
}

Future<void> _openCustomizer(WidgetTester tester) async {
  await tester.tap(find.byIcon(Icons.card_giftcard_rounded)); // -> /rewards
  await tester.pumpAndSettle();
  await tester.tap(find.text('Customize')); // -> /avatar
  await tester.pumpAndSettle();
}

void main() {
  testWidgets('owned items render and can be equipped (regression)', (
    tester,
  ) async {
    await pumpApp(tester, store: _storeOwning({_hat, _glasses, _mask, _pet}));
    await _openCustomizer(tester);

    // The rows render (no layout crash) — all owned items appear with an Equip
    // button each.
    expect(find.text('Silver Studs'), findsOneWidget);
    expect(find.text('Round Glasses'), findsOneWidget);
    expect(find.text('Simple Mask'), findsOneWidget);
    expect(find.text('Study Cap Fox'), findsOneWidget);
    expect(find.text('Equip'), findsNWidgets(4)); // one per owned item

    // Equip the hat -> its row flips to "Remove".
    await tester.tap(find.text('Equip').first);
    await tester.pumpAndSettle();
    expect(find.text('Remove'), findsOneWidget);
  });

  testWidgets('equipping items of different categories all stick', (
    tester,
  ) async {
    await pumpApp(tester, store: _storeOwning({_hat, _glasses, _mask}));
    await _openCustomizer(tester);

    // Equip every item (each tap consumes the first remaining "Equip").
    for (var i = 0; i < 3; i++) {
      await tester.tap(find.text('Equip').first);
      await tester.pumpAndSettle();
    }
    // All three now show Remove; none left to equip.
    expect(find.text('Remove'), findsNWidgets(3));
    expect(find.text('Equip'), findsNothing);

    // Remove one -> it becomes equippable again.
    await tester.tap(find.text('Remove').first);
    await tester.pumpAndSettle();
    expect(find.text('Remove'), findsNWidgets(2));
    expect(find.text('Equip'), findsOneWidget);
  });

  testWidgets('an avatar that already wears glasses hides equipped glasses', (
    tester,
  ) async {
    const specsAvatar = 'avatar_advanced_007_algebra_dragon'; // glasses in art
    final store = _storeOwning({_glasses, specsAvatar});
    final progress = AppProgress.fromJson(
      jsonDecode(store.getString('progress.v1')!) as Map<String, dynamic>,
    );
    progress.game.selectedAvatarId = specsAvatar;
    progress.game.equipped['eyewear'] = _glasses;
    store.setString('progress.v1', jsonEncode(progress.toJson()));

    await pumpApp(tester, store: store);
    await _openCustomizer(tester);

    // Still equipped (Remove), but the row explains why it isn't shown...
    expect(find.text('Remove'), findsOneWidget);
    expect(find.text('Algebra Dragon already wears glasses'), findsOneWidget);
    // ...and the preview doesn't stack a second pair on the avatar.
    expect(
      find.byWidgetPredicate(
        (w) => w is AssetImage512 && w.asset.id == _glasses,
      ),
      findsOneWidget, // only the row thumbnail, not a preview layer
    );
  });
}
