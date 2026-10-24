import 'dart:convert';
import 'dart:io';
import 'dart:typed_data';
import 'dart:ui' as ui;

import 'package:flutter/material.dart';
import 'package:flutter/rendering.dart';
import 'package:flutter_test/flutter_test.dart';
import 'package:zany_test_prep/domain/models/avatar_catalog.dart';
import 'package:zany_test_prep/domain/models/progress.dart';
import 'package:zany_test_prep/domain/services/rewards_service.dart';
import 'package:zany_test_prep/features/rewards/avatar_view.dart';

final AvatarCatalog _catalog = AvatarCatalog.fromJson(
  jsonDecode(
        File('assets/avatar/manifest/avatar_catalog.json').readAsStringSync(),
      )
      as Map<String, dynamic>,
);

/// Renders a single trimmed sprite into a [size]² transparent frame using the
/// app's real [placementRect] math, then returns the opaque bounding box of the
/// result — i.e. where the art actually landed on screen.
Future<Rect> _renderedBounds(
  WidgetTester tester,
  CatalogAsset asset,
  String? slot,
  double size,
) async {
  final key = GlobalKey();
  final rect = fittedRect(asset, slot, size);
  await tester.pumpWidget(
    Directionality(
      textDirection: TextDirection.ltr,
      child: Center(
        child: RepaintBoundary(
          key: key,
          child: SizedBox(
            width: size,
            height: size,
            child: Stack(
              children: [
                Positioned.fromRect(
                  rect: rect,
                  child: Image.asset(asset.assetPath, fit: BoxFit.contain),
                ),
              ],
            ),
          ),
        ),
      ),
    ),
  );
  await tester.pump();

  late Rect bounds;
  await tester.runAsync(() async {
    await precacheImage(AssetImage(asset.assetPath), key.currentContext!);
    await tester.pump();
    final boundary =
        key.currentContext!.findRenderObject() as RenderRepaintBoundary;
    final image = await boundary.toImage(pixelRatio: 1.0);
    final data = (await image.toByteData(format: ui.ImageByteFormat.rawRgba))!;
    bounds = _alphaBounds(data, image.width, image.height);
    image.dispose();
  });
  return bounds;
}

/// Bounding box of pixels with alpha > 10 (RGBA byte order).
Rect _alphaBounds(ByteData data, int w, int h) {
  final px = data.buffer.asUint8List();
  int minX = w, minY = h, maxX = -1, maxY = -1;
  for (var y = 0; y < h; y++) {
    for (var x = 0; x < w; x++) {
      if (px[(y * w + x) * 4 + 3] > 10) {
        if (x < minX) minX = x;
        if (x > maxX) maxX = x;
        if (y < minY) minY = y;
        if (y > maxY) maxY = y;
      }
    }
  }
  if (maxX < 0) return Rect.zero;
  return Rect.fromLTRB(
    minX.toDouble(),
    minY.toDouble(),
    maxX.toDouble(),
    maxY.toDouble(),
  );
}

/// Renders a full [AvatarPreview] loadout and returns its RGBA pixels.
Future<(ByteData, int, int)> _renderPreview(
  WidgetTester tester,
  GameState g,
  double size,
) async {
  final key = GlobalKey();
  final layers = const RewardsService().equippedLayers(g, _catalog);
  await tester.pumpWidget(
    MaterialApp(
      home: Center(
        child: RepaintBoundary(
          key: key,
          child: AvatarPreview(layers: layers, size: size, animate: false),
        ),
      ),
    ),
  );
  await tester.pump();
  late ByteData data;
  late int w, h;
  await tester.runAsync(() async {
    for (final l in layers) {
      await precacheImage(AssetImage(l.asset.assetPath), key.currentContext!);
    }
    await tester.pump();
    final boundary =
        key.currentContext!.findRenderObject() as RenderRepaintBoundary;
    final image = await boundary.toImage(pixelRatio: 1.0);
    data = (await image.toByteData(format: ui.ImageByteFormat.rawRgba))!;
    w = image.width;
    h = image.height;
    image.dispose();
  });
  return (data, w, h);
}

/// Number of pixels inside [area] that differ between two renders.
int _diffCount(ByteData a, ByteData b, int w, Rect area) {
  final pa = a.buffer.asUint8List(), pb = b.buffer.asUint8List();
  var n = 0;
  for (var y = area.top.toInt(); y < area.bottom.toInt(); y++) {
    for (var x = area.left.toInt(); x < area.right.toInt(); x++) {
      final i = (y * w + x) * 4;
      if ((pa[i] - pb[i]).abs() > 8 ||
          (pa[i + 1] - pb[i + 1]).abs() > 8 ||
          (pa[i + 2] - pb[i + 2]).abs() > 8) {
        n++;
      }
    }
  }
  return n;
}

void main() {
  group('composed preview (avatar + companions)', () {
    testWidgets('a companion with shadow and glow never touches the face', (
      tester,
    ) async {
      const size = 256.0;
      final avatar = _catalog.starterAvatars.first.id;
      final pet = _catalog.pets.firstWhere(
        (p) => p.rarity == 'legendary' || p.rarity == 'epic',
        orElse: () => _catalog.pets.first,
      );
      final (plain, w, _) = await _renderPreview(
        tester,
        GameState(selectedAvatarId: avatar),
        size,
      );
      final (withPet, _, _) = await _renderPreview(
        tester,
        GameState(
          selectedAvatarId: avatar,
          ownedAssetIds: {pet.id},
          equipped: {'side_left_1': pet.id, 'side_right_2': pet.id},
        ),
        size,
      );
      // The face region (rig 'face' + eye line) must be pixel-identical.
      const face = Rect.fromLTRB(
        size * 0.36,
        size * 0.18,
        size * 0.64,
        size * 0.44,
      );
      expect(_diffCount(plain, withPet, w, face), 0);
      // But the companions did draw something on the sides.
      const left = Rect.fromLTRB(0, size * 0.15, size * 0.36, size * 0.5);
      const right = Rect.fromLTRB(size * 0.64, size * 0.5, size, size * 0.9);
      expect(_diffCount(plain, withPet, w, left), greaterThan(50));
      expect(_diffCount(plain, withPet, w, right), greaterThan(50));
    });

    testWidgets('every worn category renders inside its target box', (
      tester,
    ) async {
      const size = 512.0;
      final seen = <String>{};
      for (final item in _catalog.items.where((i) => !i.isSide)) {
        if (!seen.add(item.category)) continue; // one sample per category
        final target = fittedRect(item, item.primarySlot, size);
        final bounds = await _renderedBounds(
          tester,
          item,
          item.primarySlot,
          size,
        );
        expect(bounds, isNot(Rect.zero), reason: '${item.id} rendered nothing');
        const tol = 2.0;
        expect(
          bounds.left,
          greaterThanOrEqualTo(target.left - tol),
          reason: item.id,
        );
        expect(
          bounds.top,
          greaterThanOrEqualTo(target.top - tol),
          reason: item.id,
        );
        expect(
          bounds.right,
          lessThanOrEqualTo(target.right + tol),
          reason: item.id,
        );
        expect(
          bounds.bottom,
          lessThanOrEqualTo(target.bottom + tol),
          reason: item.id,
        );
      }
      expect(seen.length, greaterThanOrEqualTo(8));
    });

    testWidgets('a sample of pets from every rarity fits its side slot', (
      tester,
    ) async {
      const size = 512.0;
      final seen = <String>{};
      for (final pet in _catalog.pets) {
        if (!seen.add('${pet.rarity}/${pet.evolution?.stage ?? 1}')) continue;
        for (final slot in ['side_left_1', 'side_right_2']) {
          final target = fittedRect(pet, slot, size);
          final bounds = await _renderedBounds(tester, pet, slot, size);
          expect(bounds, isNot(Rect.zero), reason: pet.id);
          const tol = 2.0;
          expect(
            bounds.left,
            greaterThanOrEqualTo(target.left - tol),
            reason: '${pet.id}/$slot',
          );
          expect(
            bounds.right,
            lessThanOrEqualTo(target.right + tol),
            reason: '${pet.id}/$slot',
          );
          expect(
            bounds.top,
            greaterThanOrEqualTo(target.top - tol),
            reason: '${pet.id}/$slot',
          );
          expect(
            bounds.bottom,
            lessThanOrEqualTo(target.bottom + tol),
            reason: '${pet.id}/$slot',
          );
          // The sprite should actually fill most of its box (not a tiny speck).
          expect(
            (bounds.width / target.width).clamp(0, 1) >= 0.6 ||
                (bounds.height / target.height).clamp(0, 1) >= 0.6,
            isTrue,
            reason:
                '${pet.id}/$slot renders too small (${bounds.size} in ${target.size})',
          );
        }
      }
      expect(seen.length, greaterThanOrEqualTo(5));
    });
  });

  group('placementRect math (target_box_v1)', () {
    test('worn item is centered on its target and sized to the box', () {
      final cap = _catalog['item_001_classic_cap']!;
      final r = placementRect(cap, null, 512);
      final t = cap.target;
      expect(r.center.dx, closeTo(t.cx * 512, 0.01));
      expect(r.center.dy, closeTo(t.cy * 512, 0.01));
      expect(r.width, closeTo(t.w * 512, 0.01));
      expect(r.height, closeTo(t.h * 512, 0.01));
    });

    test(
      'fittedRect keeps the sprite aspect and rests headwear on the brim',
      () {
        final cap = _catalog['item_001_classic_cap']!;
        final box = placementRect(cap, null, 512);
        final f = fittedRect(cap, null, 512);
        expect(f.width / f.height, closeTo(cap.spriteAspect!, 1e-6));
        expect(f.width, lessThanOrEqualTo(box.width + 1e-6));
        expect(f.height, lessThanOrEqualTo(box.height + 1e-6));
        expect(f.bottom, closeTo(kHeadwearBrimLine * 512, 1e-6));
        // A pet keeps its box centre.
        final fox = _catalog['pet_fox_study_cap_001']!;
        final fb = placementRect(fox, 'side_left_1', 512);
        final ff = fittedRect(fox, 'side_left_1', 512);
        expect(ff.center.dx, closeTo(fb.center.dx, 1e-6));
        expect(ff.center.dy, closeTo(fb.center.dy, 1e-6));
        // Halos float rather than sit on the brow.
        final halo = _catalog['item_007_halo_ring'];
        if (halo != null) {
          expect(halo.floatsAboveHead, isTrue);
          expect(
            fittedRect(halo, null, 512).center.dy,
            closeTo(placementRect(halo, null, 512).center.dy, 1e-6),
          );
        }
      },
    );

    test('side asset uses the per-slot target for the equipped slot', () {
      final fox = _catalog['pet_fox_study_cap_001']!;
      final r1 = placementRect(fox, 'side_left_1', 512);
      final r2 = placementRect(fox, 'side_right_2', 512);
      // Different side slots place the sprite in different positions.
      expect(r1.center.dx, lessThan(256)); // left
      expect(r2.center.dx, greaterThan(256)); // right
      expect(r2.center.dy, greaterThan(r1.center.dy)); // bottom vs top
    });
  });

  group('rendered overlap (looking at the composed pixels)', () {
    testWidgets('a headwear sprite lands inside its head target box', (
      tester,
    ) async {
      final cap = _catalog['item_001_classic_cap']!;
      const size = 512.0;
      final target = fittedRect(cap, null, size);
      final bounds = await _renderedBounds(tester, cap, null, size);

      expect(bounds, isNot(Rect.zero), reason: 'nothing rendered');
      // Contain-fit keeps the art within its target box (small AA tolerance).
      const tol = 2.0;
      expect(bounds.left, greaterThanOrEqualTo(target.left - tol));
      expect(bounds.top, greaterThanOrEqualTo(target.top - tol));
      expect(bounds.right, lessThanOrEqualTo(target.right + tol));
      expect(bounds.bottom, lessThanOrEqualTo(target.bottom + tol));
      // And it sits in the upper third of the frame (on the head), not centered.
      expect(bounds.center.dy, lessThan(size * 0.33));
    });

    testWidgets('the same pet renders on the left vs right per slot', (
      tester,
    ) async {
      final fox = _catalog['pet_fox_study_cap_001']!;
      const size = 512.0;
      final left = await _renderedBounds(tester, fox, 'side_left_1', size);
      final right = await _renderedBounds(tester, fox, 'side_right_1', size);
      expect(left, isNot(Rect.zero));
      expect(right, isNot(Rect.zero));
      expect(left.center.dx, lessThan(size * 0.5));
      expect(right.center.dx, greaterThan(size * 0.5));
      // Both fit within the side-slot box height (not full-frame / oversized).
      expect(left.height, lessThan(size * 0.5));
      expect(right.height, lessThan(size * 0.5));
    });
  });
}
