import 'dart:convert';

import 'package:flutter/material.dart';
import 'package:flutter_test/flutter_test.dart';
import 'package:zany_test_prep/data/local/key_value_store.dart';
import 'package:zany_test_prep/domain/models/profile.dart';
import 'package:zany_test_prep/domain/models/progress.dart';
import 'package:zany_test_prep/features/rewards/avatar_fullscreen.dart';
import 'package:zany_test_prep/features/rewards/avatar_view.dart';

import '../helpers/pump_app.dart';

const _hat = 'item_001_classic_cap'; // "Classic Cap"
const _mask = 'item_071_simple_mask'; // "Simple Mask"

MemoryStore _store({Map<String, String> equipped = const {}}) {
  final store = MemoryStore();
  store.setString('onboarded.v1', 'true');
  store.setString(
    'profile.v1',
    jsonEncode(UserProfile.initial('sat', 10).toJson()),
  );
  final progress = AppProgress();
  progress.game.totalXp = 5000;
  progress.game.ownedAssetIds.addAll({_hat, _mask});
  progress.game.equipped.addAll(equipped);
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
  testWidgets('tapping the customizer preview opens the avatar full screen', (
    tester,
  ) async {
    await pumpApp(
      tester,
      store: _store(equipped: {'headwear': _hat, 'face_accessory': _mask}),
    );
    await _openCustomizer(tester);

    expect(find.byType(TappableAvatarPreview), findsOneWidget);
    await tester.tap(find.byType(TappableAvatarPreview));
    await tester.pumpAndSettle();

    expect(find.byType(AvatarFullScreen), findsOneWidget);
    // The big preview fills the width (minus margins) of the test screen.
    final preview = tester.widget<AvatarPreview>(
      find.byKey(const Key('avatar-fullscreen-preview')),
    );
    final screenW =
        tester.view.physicalSize.width / tester.view.devicePixelRatio;
    expect(preview.size, greaterThan(screenW * 0.6));
    // What it's wearing is listed underneath.
    expect(
      find.descendant(
        of: find.byType(AvatarFullScreen),
        matching: find.widgetWithText(Chip, 'Classic Cap'),
      ),
      findsOneWidget,
    );
    expect(
      find.descendant(
        of: find.byType(AvatarFullScreen),
        matching: find.widgetWithText(Chip, 'Simple Mask'),
      ),
      findsOneWidget,
    );
    expect(find.text('Pinch or double-tap to zoom'), findsOneWidget);

    // Close returns to the customizer.
    await tester.tap(find.byTooltip('Close'));
    await tester.pumpAndSettle();
    expect(find.byType(AvatarFullScreen), findsNothing);
    expect(find.text('Customize avatar'), findsOneWidget);
  });

  testWidgets('full screen with nothing equipped points to the Store', (
    tester,
  ) async {
    await pumpApp(tester, store: _store());
    await _openCustomizer(tester);
    await tester.tap(find.byType(TappableAvatarPreview));
    await tester.pumpAndSettle();
    expect(find.textContaining('Nothing equipped yet'), findsOneWidget);
  });

  testWidgets('double-tap zooms in and a second double-tap resets', (
    tester,
  ) async {
    await pumpApp(tester, store: _store(equipped: {'headwear': _hat}));
    await _openCustomizer(tester);
    await tester.tap(find.byType(TappableAvatarPreview));
    await tester.pumpAndSettle();

    final zoom = find.byKey(const Key('avatar-fullscreen-zoom'));
    double scale() => tester
        .widget<InteractiveViewer>(zoom)
        .transformationController!
        .value
        .getMaxScaleOnAxis();
    expect(scale(), closeTo(1, 1e-6));

    Future<void> doubleTap() async {
      final c = tester.getCenter(zoom);
      await tester.tapAt(c);
      await tester.pump(const Duration(milliseconds: 50));
      await tester.tapAt(c);
      await tester.pumpAndSettle();
    }

    await doubleTap();
    expect(scale(), greaterThan(2));
    await doubleTap();
    expect(scale(), closeTo(1, 1e-6));
  });

  testWidgets('the rewards hub preview opens it too', (tester) async {
    await pumpApp(tester, store: _store(equipped: {'headwear': _hat}));
    await tester.tap(find.byIcon(Icons.card_giftcard_rounded));
    await tester.pumpAndSettle();
    await tester.tap(find.byType(TappableAvatarPreview));
    await tester.pumpAndSettle();
    expect(find.byType(AvatarFullScreen), findsOneWidget);
  });
}
