import 'package:flutter_test/flutter_test.dart';
import 'package:zany_test_prep/domain/models/avatar_catalog.dart';

Map<String, dynamic> _raw({
  required String id,
  required String type,
  required String slotType,
  String category = 'headwear',
  List<String> slots = const ['headwear'],
  double scale = 1.0,
  int ax = 256,
  int ay = 118,
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
  'anchor': {'x': ax, 'y': ay},
};

void main() {
  test('parses slot type, anchor, and scale', () {
    final c = AvatarCatalog.fromJson({
      'pack_id': 'p',
      'style_version': 'v',
      'assets': [
        _raw(id: 'cap', type: 'item', slotType: 'worn', ax: 256, ay: 118),
        _raw(
          id: 'fox',
          type: 'pet',
          slotType: 'side',
          category: 'common',
          slots: const ['side_left_1', 'side_left_2'],
          scale: 0.78,
          ax: 128,
          ay: 330,
        ),
      ],
    });
    final cap = c['cap']!;
    expect(cap.slotType, 'worn');
    expect(cap.isSide, isFalse);
    expect(cap.anchorX, 256);
    expect(cap.anchorY, 118);

    final fox = c['fox']!;
    expect(fox.isSide, isTrue);
    expect(fox.scale, 0.78);
    expect(fox.anchorX, 128);
    expect(fox.anchorY, 330);
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
    expect(c['blazer'], isNull); // filtered out
    expect(c.items.any((a) => a.category == 'jacket_overlay'), isFalse);
  });
}
