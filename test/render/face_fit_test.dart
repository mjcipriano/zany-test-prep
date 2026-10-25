import 'dart:convert';
import 'dart:io';

import 'package:flutter/material.dart';
import 'package:flutter_test/flutter_test.dart';
import 'package:zany_test_prep/domain/models/avatar_catalog.dart';
import 'package:zany_test_prep/domain/services/rewards_service.dart';
import 'package:zany_test_prep/features/rewards/avatar_view.dart';

/// face_fit_v1: head, face and ear items are placed on each avatar's own
/// measured face, not one box per slot. These checks run every fitted item on
/// every avatar in the vendored catalog (pure geometry, so they stay fast).
void main() {
  final catalog = AvatarCatalog.fromJson(
    jsonDecode(
          File('assets/avatar/manifest/avatar_catalog.json').readAsStringSync(),
        )
        as Map<String, dynamic>,
    includeRetired: true,
  );
  const size = 512.0;
  final fitted = catalog.items.where((i) => i.fit != null).toList();
  const fitCategories = {
    'headwear',
    'eyewear',
    'face_accessory',
    'ear_accessory',
  };

  CatalogAsset item(String id) => catalog[id]!;
  CatalogAsset avatar(String id) => catalog[id]!;

  group('catalog data', () {
    test('every avatar has a face rig with the points items hang on', () {
      expect(catalog.avatars, isNotEmpty);
      for (final a in catalog.avatars) {
        final rig = a.faceRig;
        expect(rig, isNotNull, reason: a.id);
        for (final p in ['eyes', 'brow', 'nose_bridge', 'mouth', 'ears']) {
          expect(rig!.points[p], isNotNull, reason: '${a.id} $p');
        }
        expect(rig!.widths['face'], greaterThan(0), reason: a.id);
      }
    });

    test('every head, face and ear item has a fit; nothing else does', () {
      for (final i in catalog.items) {
        expect(i.fit != null, fitCategories.contains(i.category), reason: i.id);
      }
    });

    test('heads differ, which is why one box per slot could not work', () {
      final eyes = catalog.avatars
          .map((a) => a.faceRig!.points['eyes']!.y)
          .toList();
      final lo = eyes.reduce((a, b) => a < b ? a : b);
      final hi = eyes.reduce((a, b) => a > b ? a : b);
      expect(hi - lo, greaterThan(0.05));
    });
  });

  group('placement on every avatar', () {
    test('masks, gaiters, nose strips and moustaches stay below the eyes', () {
      const lower = {'mask', 'gaiter', 'nose_strip', 'mustache'};
      for (final a in catalog.avatars) {
        final rig = a.faceRig!;
        final eyeY = rig.points['eyes']!.y * size;
        for (final i in fitted.where((i) => lower.contains(i.fit!.kind))) {
          final r = fittedRect(i, i.primarySlot, size, rig: rig);
          expect(
            r.top,
            greaterThanOrEqualTo(eyeY - 0.01 * size),
            reason: '${i.id} on ${a.id}',
          );
        }
      }
    });

    test('masks cover the mouth', () {
      for (final a in catalog.avatars) {
        final rig = a.faceRig!;
        final mouth = rig.points['mouth']!;
        for (final i in fitted.where((i) => i.fit!.kind == 'mask')) {
          final r = fittedRect(i, i.primarySlot, size, rig: rig);
          expect(
            r.contains(Offset(mouth.x * size, mouth.y * size)),
            isTrue,
            reason: '${i.id} on ${a.id}',
          );
        }
      }
    });

    test('glasses centre on the eyes', () {
      for (final a in catalog.avatars) {
        final rig = a.faceRig!;
        final eyes = rig.points['eyes']!;
        for (final i in fitted.where((i) => i.fit!.kind == 'glasses')) {
          final c = fittedRect(i, i.primarySlot, size, rig: rig).center;
          expect((c.dx - eyes.x * size).abs(), lessThan(0.02 * size));
          expect((c.dy - eyes.y * size).abs(), lessThan(0.02 * size));
        }
      }
    });

    test('earrings straddle the face at ear height', () {
      for (final a in catalog.avatars) {
        final rig = a.faceRig!;
        final earL = rig.points['ear_l']!, earR = rig.points['ear_r']!;
        for (final i in fitted.where((i) => i.fit!.kind == 'earring')) {
          final r = fittedRect(i, i.primarySlot, size, rig: rig);
          expect(r.left, lessThanOrEqualTo(earL.x * size), reason: i.id);
          expect(r.right, greaterThanOrEqualTo(earR.x * size), reason: i.id);
          // The pair hangs from the lobes: never above the eyes, never past
          // the chin.
          expect(r.top, greaterThan(rig.points['eyes']!.y * size));
          expect(r.top, lessThan(rig.points['chin']!.y * size));
        }
      }
    });

    test('hats sit above the eyes and nothing strays far past the frame', () {
      for (final a in catalog.avatars) {
        final rig = a.faceRig!;
        final eyeY = rig.points['eyes']!.y * size;
        for (final i in fitted) {
          final r = fittedRect(i, i.primarySlot, size, rig: rig);
          final frame = const Rect.fromLTWH(
            0,
            0,
            size,
            size,
          ).inflate(0.25 * size);
          expect(
            frame.contains(r.topLeft) && frame.contains(r.bottomRight),
            isTrue,
            reason: '${i.id} on ${a.id}',
          );
          if (i.category == 'headwear' && i.fit!.kind != 'shade_visor') {
            expect(r.top, lessThan(eyeY), reason: '${i.id} on ${a.id}');
          }
        }
      }
    });

    test('a hood is drawn behind the avatar, a cap in front', () {
      final hood = fitted.firstWhere((i) => i.fit!.kind == 'hood');
      final cap = fitted.firstWhere((i) => i.fit!.kind == 'cap');
      final base = catalog.avatars.first;
      expect(hood.renderZ, lessThan(base.zIndex));
      expect(hood.renderZ, greaterThan(-20)); // still above back auras
      expect(cap.renderZ, greaterThan(base.zIndex));
    });
  });

  group('hats and hair', () {
    test('hats grow to cover big hair', () {
      final cap = item('item_001_classic_cap');
      final short = avatar('avatar_basic_001_nova_learner').faceRig!;
      final curly = avatar('avatar_basic_008_kiki_quest').faceRig!;
      final wShort = fittedRect(cap, 'headwear', 1, rig: short).width;
      final wCurly = fittedRect(cap, 'headwear', 1, rig: curly).width;
      expect(wCurly, greaterThan(wShort * 1.2));
      expect(wCurly, greaterThanOrEqualTo(curly.widths['hair']!));
    });

    test('a cap hides the hair above its crown; crowns and hoods do not', () {
      final cap = item('item_001_classic_cap');
      final crown = item('item_030_galaxy_hood'); // drawn as a gem crown
      final hood = item('item_016_calculator_cap'); // drawn as a hood
      for (final a in catalog.avatars) {
        final rig = a.faceRig!;
        final r = fittedRect(cap, 'headwear', size, rig: rig);
        final line = avatarClipTop([
          EquippedLayer(null, a),
          EquippedLayer('headwear', cap),
        ], size);
        expect(line, greaterThan(r.top), reason: a.id);
        expect(line, lessThan(r.top + r.height / 2), reason: a.id);
        expect(line, lessThan(rig.points['brow']!.y * size), reason: a.id);
        for (final other in [crown, hood]) {
          expect(
            avatarClipTop([
              EquippedLayer(null, a),
              EquippedLayer('headwear', other),
            ], size),
            0,
          );
        }
      }
    });

    test('avatars whose art wears a hat or glasses hide that slot', () {
      final capped = avatar('avatar_advanced_034_vocab_knight'); // beanie
      final specs = avatar('avatar_advanced_007_algebra_dragon'); // glasses
      expect(capped.builtInSlots, ['headwear']);
      expect(specs.builtInSlots, ['eyewear']);
      expect(
        catalog.avatars.where((a) => a.builtInSlots.isNotEmpty).length,
        13,
      );
    });
  });

  testWidgets('a cap clips the hair above it in the preview', (tester) async {
    final a = avatar('avatar_basic_008_kiki_quest');
    Future<void> pump(List<EquippedLayer> layers) => tester.pumpWidget(
      MaterialApp(
        home: Center(
          child: AvatarPreview(layers: layers, size: size, animate: false),
        ),
      ),
    );
    await pump([EquippedLayer(null, a)]);
    expect(find.byKey(const Key('avatar-hat-hair-clip')), findsNothing);
    await pump([
      EquippedLayer(null, a),
      EquippedLayer('headwear', item('item_001_classic_cap')),
    ]);
    expect(find.byKey(const Key('avatar-hat-hair-clip')), findsOneWidget);
  });

  group('faceFitRect maths', () {
    const rig = FaceRig(
      points: {'eyes': FramePoint(0.5, 0.3)},
      widths: {'eyes': 0.2},
    );
    const raw = {
      'id': 'x',
      'name': 'x',
      'type': 'item',
      'category': 'eyewear',
      'asset_path': 'x.webp',
      'sprite_size': {'width': 300, 'height': 100},
      'fit': {
        'kind': 'glasses',
        'anchor': 'eyes',
        'sprite_anchor': {'x': 0.5, 'y': 0.5},
        'width_ref': 'eyes',
        'width': 1.5,
        'behind': false,
      },
    };

    test('width from the rig, height from the sprite, anchor on the point', () {
      final a = CatalogAsset.fromJson(raw);
      final r = faceFitRect(a, rig, 1)!;
      expect(r.width, closeTo(0.3, 1e-9));
      expect(r.height, closeTo(0.1, 1e-9));
      expect(r.left, closeTo(0.35, 1e-9));
      expect(r.top, closeTo(0.25, 1e-9));
    });

    test('falls back to the target box without a rig or a known anchor', () {
      final a = CatalogAsset.fromJson(raw);
      expect(faceFitRect(a, null, 1), isNull);
      const other = FaceRig(
        points: {'mouth': FramePoint(0.5, 0.4)},
        widths: {},
      );
      expect(faceFitRect(a, other, 1), isNull);
      expect(fittedRect(a, null, 512), placementFallback(a));
    });
  });

  group('sceneScale', () {
    test('is 1 when everything fits', () {
      final base = avatar(catalog.avatars.first.id);
      expect(sceneScale([EquippedLayer(null, base)]), 1.0);
      expect(
        sceneScale([
          EquippedLayer(null, base),
          EquippedLayer('eyewear', item('item_041_round_glasses')),
        ]),
        1.0,
      );
    });

    test('shrinks (bottom-anchored) when a tall hat pokes above the frame', () {
      // Find a real avatar + hat pair that overflows the top of the frame.
      for (final a in catalog.avatars) {
        for (final h in fitted.where((i) => i.category == 'headwear')) {
          final r = fittedRect(h, 'headwear', 1, rig: a.faceRig);
          if (r.top < -0.02) {
            final s = sceneScale([
              EquippedLayer(null, a),
              EquippedLayer('headwear', h),
            ]);
            expect(s, lessThan(1.0));
            expect(s, greaterThanOrEqualTo(kMinSceneScale));
            // After scaling about the bottom edge, the hat's top is in frame.
            expect(1 - s * (1 - r.top), greaterThanOrEqualTo(-1e-9));
            return;
          }
        }
      }
      fail('expected at least one hat to reach above the frame');
    });
  });

  testWidgets('the preview draws a mask where the rig says, per avatar', (
    tester,
  ) async {
    final mask = item('item_071_simple_mask');
    for (final a in [catalog.avatars.first, catalog.avatars.last]) {
      await tester.pumpWidget(
        MaterialApp(
          home: Center(
            child: AvatarPreview(
              key: ValueKey(a.id),
              layers: [
                EquippedLayer(null, a),
                EquippedLayer('face_accessory', mask),
              ],
              size: size,
              animate: false,
            ),
          ),
        ),
      );
      final positioned = tester.widget<Positioned>(
        find
            .ancestor(
              of: find.byWidgetPredicate(
                (w) => w is AssetImage512 && w.asset.id == mask.id,
              ),
              matching: find.byType(Positioned),
            )
            .first,
      );
      final expected = fittedRect(mask, 'face_accessory', size, rig: a.faceRig);
      expect(positioned.left, closeTo(expected.left, 0.01));
      expect(positioned.top, closeTo(expected.top, 0.01));
      expect(positioned.width, closeTo(expected.width, 0.01));
    }
  });
}

/// The target-box rect [fittedRect] uses when no face fit applies.
Rect placementFallback(CatalogAsset a) {
  final box = placementRect(a, null, 512);
  final aspect = a.spriteAspect!;
  final h = box.width / aspect < box.height ? box.width / aspect : box.height;
  return Rect.fromCenter(center: box.center, width: h * aspect, height: h);
}
