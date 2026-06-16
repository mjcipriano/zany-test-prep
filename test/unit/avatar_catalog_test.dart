import 'package:flutter_test/flutter_test.dart';
import 'package:zany_test_prep/domain/models/avatar_catalog.dart';

Map<String, dynamic> _raw({
  required String id,
  required String type,
  required String slotType,
  String category = 'headwear',
  List<String> slots = const ['headwear'],
  double scale = 1.0,
  Map<String, dynamic>? placement,
}) => {
  'id': id,
  'name': id,
  'type': type,
  'category': category,
  'slot_type': slotType,
  'allowed_slots': slots,
  'xp_cost': 100,
  'asset_path': 'p/$id.png',
  'z_index': 45,
  'scale': scale,
  if (placement != null) 'placement': placement,
};

void main() {
  test('parses slot type and placement target box', () {
    final c = AvatarCatalog.fromJson({
      'pack_id': 'p',
      'style_version': 'v',
      'assets': [
        _raw(
          id: 'cap',
          type: 'item',
          slotType: 'worn',
          placement: {
            'target': {'cx': 0.5, 'cy': 0.155, 'w': 0.42, 'h': 0.22},
            'fit': 'contain',
          },
        ),
      ],
    });
    final cap = c['cap']!;
    expect(cap.slotType, 'worn');
    expect(cap.isSide, isFalse);
    expect(cap.target.cx, 0.5);
    expect(cap.target.cy, 0.155);
    expect(cap.target.w, 0.42);
    expect(cap.target.h, 0.22);
  });

  test('parses per-slot targets for side assets', () {
    final c = AvatarCatalog.fromJson({
      'pack_id': 'p',
      'style_version': 'v',
      'assets': [
        _raw(
          id: 'fox',
          type: 'pet',
          slotType: 'side',
          category: 'common',
          slots: const ['side_left_1', 'side_right_2'],
          placement: {
            'target': {'cx': 0.215, 'cy': 0.33, 'w': 0.28, 'h': 0.26},
            'targets_by_slot': {
              'side_left_1': {'cx': 0.215, 'cy': 0.33, 'w': 0.28, 'h': 0.26},
              'side_right_2': {'cx': 0.78, 'cy': 0.68, 'w': 0.30, 'h': 0.30},
            },
          },
        ),
      ],
    });
    final fox = c['fox']!;
    expect(fox.isSide, isTrue);
    // targetForSlot picks the per-slot override...
    expect(fox.targetForSlot('side_right_2').cx, 0.78);
    expect(fox.targetForSlot('side_left_1').cy, 0.33);
    // ...and falls back to the default target for an unknown slot.
    expect(fox.targetForSlot('nope').cx, 0.215);
  });

  test('assets without placement fall back to a full-frame target', () {
    final c = AvatarCatalog.fromJson({
      'pack_id': 'p',
      'style_version': 'v',
      'assets': [
        _raw(id: 'av', type: 'avatar', slotType: 'base', slots: const []),
      ],
    });
    final a = c['av']!;
    expect(a.target.cx, 0.5);
    expect(a.target.w, 1.0);
    expect(a.target.h, 1.0);
  });

  test('excludes jacket/blazer overlays everywhere', () {
    final c = AvatarCatalog.fromJson({
      'pack_id': 'p',
      'style_version': 'v',
      'assets': [
        _raw(id: 'cap', type: 'item', slotType: 'worn'),
        _raw(
          id: 'blazer',
          type: 'item',
          slotType: 'worn',
          category: 'jacket_overlay',
          slots: const ['jacket_or_top_overlay'],
        ),
      ],
    });
    expect(c['cap'], isNotNull);
    expect(c['blazer'], isNull);
    expect(c.items.any((a) => a.category == 'jacket_overlay'), isFalse);
  });
}
