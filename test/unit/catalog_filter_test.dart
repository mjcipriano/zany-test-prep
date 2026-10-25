import 'dart:convert';
import 'dart:io';

import 'package:flutter_test/flutter_test.dart';
import 'package:zany_test_prep/domain/models/avatar_catalog.dart';
import 'package:zany_test_prep/domain/services/catalog_filter.dart';

final AvatarCatalog _catalog = AvatarCatalog.fromJson(
  jsonDecode(
        File('assets/avatar/manifest/avatar_catalog.json').readAsStringSync(),
      )
      as Map<String, dynamic>,
);

CatalogAsset _asset(
  String id, {
  String name = '',
  String category = 'headwear',
  String rarity = 'common',
  int xp = 100,
  String type = 'item',
  List<String> tags = const [],
}) => CatalogAsset(
  id: id,
  name: name.isEmpty ? id : name,
  type: type,
  category: category,
  slotType: 'worn',
  rarity: rarity,
  xpCost: xp,
  assetPath: '',
  previewAssetPath: '',
  allowedSlots: const [],
  zIndex: 0,
  scale: 1,
  target: TargetBox.full,
  targetsBySlot: const {},
  defaultUnlocked: false,
  tags: tags,
);

List<String> _ids(List<CatalogAsset> list) => list.map((a) => a.id).toList();

void main() {
  group('labels', () {
    test('every item category in the catalog has a friendly label', () {
      final categories = _catalog.items.map((a) => a.category).toSet();
      expect(categories, isNotEmpty);
      for (final c in categories) {
        expect(kItemCategoryOrder, contains(c), reason: c);
      }
      expect(
        {for (final c in kItemCategoryOrder) c: categoryLabel(c)},
        {
          'headwear': 'Hats',
          'eyewear': 'Glasses',
          'face_accessory': 'Face',
          'ear_accessory': 'Ears',
          'neck_accessory': 'Neck',
          'chest_badge': 'Badges',
          'back_aura': 'Auras',
          'background_frame': 'Frames',
          'floating_props': 'Floating',
        },
      );
    });

    test('unknown categories fall back to title case', () {
      expect(categoryLabel('jet_packs'), 'Jet Packs');
      expect(categoryLabel(''), 'Other');
    });

    test('rarities have labels and a common-to-legendary rank', () {
      expect(rarityLabel('legendary'), 'Legendary');
      expect(
        kRarityOrder.map(rarityRank).toList(),
        List.generate(kRarityOrder.length, (i) => i),
      );
      expect(rarityRank('mythic'), kRarityOrder.length);
      for (final r in _catalog.assets.map((a) => a.rarity).toSet()) {
        expect(kRarityOrder, contains(r), reason: r);
      }
    });

    test('categories order head to toe, unknown ones last A-Z', () {
      final sorted = ['zeta', 'floating_props', 'alpha', 'headwear', 'eyewear']
        ..sort(compareCategories);
      expect(sorted, [
        'headwear',
        'eyewear',
        'floating_props',
        'alpha',
        'zeta',
      ]);
    });
  });

  group('counts', () {
    test('category counts cover every category and sum to the total', () {
      final items = _catalog.items;
      final counts = const CatalogFilter().categoryCounts(items);
      expect(counts.keys.toList(), [
        for (final c in kItemCategoryOrder)
          if (items.any((a) => a.category == c)) c,
      ]);
      expect(counts.values.fold(0, (a, b) => a + b), items.length);
      for (final e in counts.entries) {
        expect(
          e.value,
          items.where((a) => a.category == e.key).length,
          reason: e.key,
        );
      }
    });

    test('category counts are faceted on the other filters', () {
      final items = _catalog.items;
      final filter = const CatalogFilter(
        category: 'neck_accessory',
      ).toggleRarity('legendary');
      final counts = filter.categoryCounts(items);
      // The selected category does not narrow its own counts...
      expect(counts['eyewear'], 0); // glasses are all uncommon
      expect(
        counts['neck_accessory'],
        items
            .where(
              (a) => a.category == 'neck_accessory' && a.rarity == 'legendary',
            )
            .length,
      );
      // ...but every category is still listed.
      expect(counts.length, items.map((a) => a.category).toSet().length);

      final rarities = filter.rarityCounts(items);
      expect(rarities.keys.first, 'common'); // ordered common -> legendary
      expect(rarities['legendary'], greaterThan(0));
      expect(rarities['common'], 0); // no common necklaces
      expect(
        rarities.values.fold(0, (a, b) => a + b),
        items.where((a) => a.category == 'neck_accessory').length,
      );
    });

    test('pets: rarity counts match the store pets', () {
      final pets = _catalog.basePets;
      final counts = const CatalogFilter().rarityCounts(pets);
      expect(counts.keys, ['common', 'uncommon', 'rare', 'epic', 'legendary']);
      expect(counts.values.fold(0, (a, b) => a + b), pets.length);
    });
  });

  group('filtering', () {
    final hat = _asset('hat', category: 'headwear', rarity: 'rare', xp: 300);
    final cap = _asset('cap', category: 'headwear', rarity: 'common', xp: 100);
    final specs = _asset('specs', category: 'eyewear', rarity: 'epic', xp: 200);
    final halo = _asset('halo', category: 'back_aura', rarity: 'rare', xp: 50);
    final all = [hat, cap, specs, halo];

    test('All returns everything; a category narrows to it', () {
      expect(const CatalogFilter().apply(all).length, 4);
      expect(_ids(const CatalogFilter().withCategory('headwear').apply(all)), [
        'cap',
        'hat',
      ]);
      expect(
        const CatalogFilter()
            .withCategory('headwear')
            .withCategory(null)
            .apply(all),
        hasLength(4),
      );
    });

    test('rarity is multi-select and toggles off again', () {
      var f = const CatalogFilter().toggleRarity('rare');
      expect(_ids(f.apply(all)), ['halo', 'hat']);
      f = f.toggleRarity('epic');
      expect(_ids(f.apply(all)), ['halo', 'specs', 'hat']);
      f = f.toggleRarity('rare');
      expect(_ids(f.apply(all)), ['specs']);
      f = f.toggleRarity('epic');
      expect(f.rarities, isEmpty);
      expect(f.apply(all), hasLength(4));
    });

    test('category and rarity combine', () {
      final f = const CatalogFilter(category: 'headwear').toggleRarity('rare');
      expect(_ids(f.apply(all)), ['hat']);
    });

    test('hide owned and affordable only use the player status', () {
      final status = CatalogStatus(
        isOwned: (a) => a.id == 'cap',
        canAfford: (a) => a.xpCost <= 200,
      );
      expect(
        _ids(
          const CatalogFilter()
              .toggle(CatalogToggle.hideOwned)
              .apply(all, status: status),
        ),
        ['halo', 'specs', 'hat'],
      );
      // Affordable = buyable now: excludes the owned cap and the 300 XP hat.
      expect(
        _ids(
          const CatalogFilter()
              .toggle(CatalogToggle.affordableOnly)
              .apply(all, status: status),
        ),
        ['halo', 'specs'],
      );
      // Toggling twice turns it off.
      expect(
        const CatalogFilter()
            .toggle(CatalogToggle.hideOwned)
            .toggle(CatalogToggle.hideOwned)
            .apply(all, status: status),
        hasLength(4),
      );
    });

    test('equipped only keeps equipped assets', () {
      final status = CatalogStatus(isEquipped: (a) => a.id == 'specs');
      expect(
        _ids(
          const CatalogFilter()
              .toggle(CatalogToggle.equippedOnly)
              .apply(all, status: status),
        ),
        ['specs'],
      );
    });

    test('toggles without status callbacks filter nothing', () {
      final f = const CatalogFilter()
          .toggle(CatalogToggle.affordableOnly)
          .toggle(CatalogToggle.equippedOnly)
          .toggle(CatalogToggle.hideOwned);
      expect(f.apply(all), hasLength(4));
    });

    test('search matches name substrings and exact tags, all tokens', () {
      final pets = [
        _asset('a', name: 'Prism Fox', type: 'pet', tags: ['pet', 'fox']),
        _asset('b', name: 'Hoodie Cat', type: 'pet', tags: ['pet', 'cat']),
        _asset('c', name: 'Plasma Kitten', type: 'pet', tags: ['pet', 'cat']),
        _asset('d', name: 'Catalog Owl', type: 'pet', tags: ['pet', 'owl']),
      ];
      List<String> search(String q) => _ids(
        const CatalogFilter(sort: CatalogSort.name).withQuery(q).apply(pets),
      );
      expect(search('FOX'), ['a']);
      expect(search('cat'), ['d', 'b', 'c']); // name substring or species tag
      expect(search('kitten cat'), ['c']);
      expect(search('  '), hasLength(4));
      expect(search('dragon'), isEmpty);
    });

    test('real catalog: species search finds every fox', () {
      final foxes = const CatalogFilter()
          .withQuery('fox')
          .apply(_catalog.basePets);
      expect(foxes, isNotEmpty);
      expect(
        foxes.every(
          (p) => p.tags.contains('fox') || p.name.toLowerCase().contains('fox'),
        ),
        isTrue,
      );
      expect(
        foxes.length,
        _catalog.basePets.where((p) => p.tags.contains('fox')).length,
      );
    });

    test('hasActiveFilters ignores the sort; cleared keeps it', () {
      const base = CatalogFilter(sort: CatalogSort.name);
      expect(base.hasActiveFilters, isFalse);
      expect(base.withSort(CatalogSort.rarity).hasActiveFilters, isFalse);
      for (final f in [
        base.withCategory('eyewear'),
        base.toggleRarity('rare'),
        base.withQuery('fox'),
        base.toggle(CatalogToggle.hideOwned),
      ]) {
        expect(f.hasActiveFilters, isTrue);
        final cleared = f.cleared();
        expect(cleared.hasActiveFilters, isFalse);
        expect(cleared.sort, CatalogSort.name);
      }
    });
  });

  group('sorting', () {
    final list = [
      _asset('b', name: 'Bravo', rarity: 'rare', xp: 300),
      _asset('a', name: 'alpha', rarity: 'legendary', xp: 300),
      _asset('c', name: 'Charlie', rarity: 'common', xp: 100),
      _asset('d', name: 'Delta', rarity: 'rare', xp: 50),
    ];

    test('price low to high is the default, ties broken by name', () {
      expect(const CatalogFilter().sort, CatalogSort.priceLowHigh);
      expect(_ids(const CatalogFilter().apply(list)), ['d', 'c', 'a', 'b']);
    });

    test('price high to low', () {
      expect(
        _ids(const CatalogFilter(sort: CatalogSort.priceHighLow).apply(list)),
        ['a', 'b', 'c', 'd'],
      );
    });

    test('rarest first, then cheapest', () {
      expect(_ids(const CatalogFilter(sort: CatalogSort.rarity).apply(list)), [
        'a',
        'd',
        'b',
        'c',
      ]);
    });

    test('name, case-insensitive', () {
      expect(_ids(const CatalogFilter(sort: CatalogSort.name).apply(list)), [
        'a',
        'b',
        'c',
        'd',
      ]);
    });

    test('every sort has a menu label and a short chip label', () {
      for (final s in CatalogSort.values) {
        expect(s.label, isNotEmpty);
        expect(s.shortLabel, isNotEmpty);
      }
    });

    test('apply does not mutate its input', () {
      final input = [...list];
      const CatalogFilter(sort: CatalogSort.name).apply(input);
      expect(_ids(input), ['b', 'a', 'c', 'd']);
    });
  });

  test('groupByCategory keeps the sort within display-ordered sections', () {
    final sorted = const CatalogFilter(
      sort: CatalogSort.priceHighLow,
    ).apply(_catalog.items);
    final groups = groupByCategory(sorted);
    expect(groups.map((g) => g.key).toList(), [
      for (final c in kItemCategoryOrder)
        if (_catalog.items.any((a) => a.category == c)) c,
    ]);
    expect(groups.fold(0, (n, g) => n + g.value.length), _catalog.items.length);
    for (final g in groups) {
      for (var i = 1; i < g.value.length; i++) {
        expect(g.value[i - 1].xpCost, greaterThanOrEqualTo(g.value[i].xpCost));
      }
    }
  });
}
