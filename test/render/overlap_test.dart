import 'dart:convert';
import 'dart:io';
import 'dart:typed_data';
import 'dart:ui' as ui;

import 'package:flutter/material.dart';
import 'package:flutter/rendering.dart';
import 'package:flutter_test/flutter_test.dart';
import 'package:zany_test_prep/domain/models/avatar_catalog.dart';
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
  final rect = placementRect(asset, slot, size);
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

void main() {
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
      final target = placementRect(cap, null, size);
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
