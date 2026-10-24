import 'dart:convert';
import 'dart:io';

import 'package:flutter/material.dart';
import 'package:flutter_test/flutter_test.dart';
import 'package:zany_test_prep/domain/models/avatar_catalog.dart';
import 'package:zany_test_prep/features/rewards/avatar_view.dart';

/// Layout checks over EVERY asset in the vendored catalog (no rendering, so
/// this stays fast): fitted sprites must stay inside the frame, side
/// companions must never cover the face, side slots must not overlap each
/// other, headwear must rest on the brow line, and stacked worn slots may only
/// overlap where the design intends (hat brim on glasses, mask under glasses).
void main() {
  final raw =
      jsonDecode(
            File(
              'assets/avatar/manifest/avatar_catalog.json',
            ).readAsStringSync(),
          )
          as Map<String, dynamic>;
  final catalog = AvatarCatalog.fromJson(raw);
  const size = 512.0;

  Rect region(String name) {
    final r = ((raw['rig'] as Map)['regions'] as Map)[name] as Map;
    final cx = (r['cx'] as num) * size, cy = (r['cy'] as num) * size;
    final w = (r['w'] as num) * size, h = (r['h'] as num) * size;
    return Rect.fromCenter(center: Offset(cx, cy), width: w, height: h);
  }

  double overlapShare(Rect a, Rect b) {
    final i = a.intersect(b);
    if (i.width <= 0 || i.height <= 0) return 0;
    final smaller = (a.width * a.height) < (b.width * b.height) ? a : b;
    return (i.width * i.height) / (smaller.width * smaller.height);
  }

  test('catalog is non-trivial and every sprite records its size', () {
    expect(catalog.avatars.length, greaterThanOrEqualTo(100));
    expect(catalog.items.length, greaterThanOrEqualTo(200));
    expect(catalog.pets.length, greaterThanOrEqualTo(30));
    for (final a in catalog.assets.where((a) => !a.isAvatar)) {
      expect(a.spriteAspect, isNotNull, reason: a.id);
    }
  });

  test('every fitted sprite lies inside the frame', () {
    final frame = const Rect.fromLTWH(0, 0, size, size).inflate(0.5);
    for (final a in catalog.assets.where((a) => !a.isAvatar)) {
      final slots = a.allowedSlots.isEmpty ? <String?>[null] : a.allowedSlots;
      for (final slot in slots) {
        final r = fittedRect(a, slot, size);
        expect(r.width, greaterThan(size * 0.04), reason: '${a.id}/$slot');
        expect(r.height, greaterThan(size * 0.04), reason: '${a.id}/$slot');
        expect(
          frame.contains(r.topLeft) && frame.contains(r.bottomRight),
          isTrue,
          reason: '${a.id}/$slot rect $r leaves the frame',
        );
      }
    }
  });

  test('side companions never cover the face and never overlap each other', () {
    // The pack's own QA face window (the drawn face is narrower than the rig
    // region, which pads out to the hairline and ears).
    const face = Rect.fromLTRB(
      size * 0.36,
      size * 0.18,
      size * 0.64,
      size * 0.44,
    );
    for (final a in catalog.assets.where((a) => a.isSide)) {
      final rects = <String, Rect>{};
      for (final slot in a.allowedSlots) {
        final r = fittedRect(a, slot, size);
        rects[slot] = r;
        expect(
          r.overlaps(face),
          isFalse,
          reason: '${a.id}/$slot covers the face',
        );
        if (slot.contains('left')) {
          expect(
            r.right,
            lessThanOrEqualTo(size * 0.5 + 1),
            reason: '${a.id}/$slot',
          );
        } else {
          expect(
            r.left,
            greaterThanOrEqualTo(size * 0.5 - 1),
            reason: '${a.id}/$slot',
          );
        }
      }
      final slots = rects.keys.toList();
      for (var i = 0; i < slots.length; i++) {
        for (var j = i + 1; j < slots.length; j++) {
          expect(
            overlapShare(rects[slots[i]]!, rects[slots[j]]!),
            lessThan(0.05),
            reason: '${a.id}: ${slots[i]} overlaps ${slots[j]}',
          );
        }
      }
    }
  });

  test('worn items sit on their body region; headwear rests on the brow', () {
    final head = region('head').inflate(size * 0.08);
    final torso = region('torso').inflate(size * 0.15);
    for (final a in catalog.items.where((a) => !a.isSide)) {
      final r = fittedRect(a, a.primarySlot, size);
      switch (a.category) {
        case 'headwear':
          expect(head.overlaps(r), isTrue, reason: '${a.id} is off the head');
          if (!a.floatsAboveHead) {
            expect(
              r.bottom,
              closeTo(kHeadwearBrimLine * size, 0.01),
              reason: a.id,
            );
          }
          expect(
            r.bottom,
            lessThanOrEqualTo(size * 0.27),
            reason: '${a.id} covers the eyes',
          );
          expect(r.top, greaterThanOrEqualTo(-1), reason: a.id);
        case 'eyewear' || 'face_accessory' || 'ear_accessory':
          expect(head.overlaps(r), isTrue, reason: '${a.id} is off the head');
          expect(r.center.dy, lessThan(size * 0.42), reason: '${a.id} too low');
        case 'neck_accessory' || 'chest_badge':
          expect(
            r.center.dy,
            inInclusiveRange(size * 0.35, size * 0.75),
            reason: '${a.id} is not on the torso',
          );
          expect(torso.overlaps(r), isTrue, reason: a.id);
        case 'back_aura' || 'background_frame':
          expect(
            r.width,
            greaterThan(size * 0.5),
            reason: '${a.id} aura too small',
          );
        default:
          break;
      }
    }
  });

  test('stacked worn slots only overlap where the design intends', () {
    final byCategory = <String, List<Rect>>{};
    for (final a in catalog.items.where((a) => !a.isSide)) {
      byCategory
          .putIfAbsent(a.category, () => [])
          .add(fittedRect(a, a.primarySlot, size));
    }
    // A hat brim may rest on the top of glasses (it is z-ordered above them)
    // and a mask meets the bottom of glasses, so those adjacent pairs get a
    // looser bound; everything else must stay almost disjoint. Every item
    // pair is checked.
    const pairs = [
      ('headwear', 'eyewear', 0.60),
      ('eyewear', 'face_accessory', 0.60),
      ('headwear', 'face_accessory', 0.05),
      ('neck_accessory', 'chest_badge', 0.15),
      ('chest_badge', 'face_accessory', 0.0),
      ('headwear', 'neck_accessory', 0.0),
      ('eyewear', 'chest_badge', 0.0),
      ('headwear', 'chest_badge', 0.0),
    ];
    for (final (p, q, maxShare) in pairs) {
      final a = byCategory[p], b = byCategory[q];
      if (a == null || b == null) continue;
      var worst = 0.0;
      for (final ra in a) {
        for (final rb in b) {
          final s = overlapShare(ra, rb);
          if (s > worst) worst = s;
        }
      }
      expect(worst, lessThanOrEqualTo(maxShare + 1e-9), reason: '$p vs $q');
    }
  });

  test('evolved pets and item variants stay aligned with their base', () {
    for (final p in catalog.pets.where((p) => p.evolution != null)) {
      final e = p.evolution!;
      expect(catalog[e.baseId], isNotNull, reason: '${p.id} base ${e.baseId}');
      if (e.nextId != null) {
        expect(catalog[e.nextId!], isNotNull, reason: '${p.id} next');
        expect(catalog[e.nextId!]!.evolution!.stage, e.stage + 1);
      }
      final base = catalog[e.baseId]!;
      for (final slot in p.allowedSlots) {
        expect(
          placementRect(p, slot, size),
          placementRect(base, slot, size),
          reason: '${p.id}/$slot drifts from its base',
        );
        // The glow may pad an evolved sprite a little, but the pet itself must
        // stay about as large as its base once fitted.
        final fb = fittedRect(base, slot, size);
        final fp = fittedRect(p, slot, size);
        expect(fp.width, greaterThanOrEqualTo(fb.width * 0.75), reason: p.id);
        expect(fp.height, greaterThanOrEqualTo(fb.height * 0.75), reason: p.id);
      }
      expect(p.isEvolvedStage, e.stage > 1);
    }
    for (final v in catalog.items.where((i) => i.variantOf != null)) {
      final base = catalog[v.variantOf!];
      expect(base, isNotNull, reason: '${v.id} variant of ${v.variantOf}');
      expect(v.category, base!.category);
      expect(
        placementRect(v, v.primarySlot, size),
        placementRect(base, base.primarySlot, size),
      );
    }
  });
}
