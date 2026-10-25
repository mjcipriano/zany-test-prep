import 'dart:convert';
import 'dart:io';

import 'package:flutter/material.dart';
import 'package:flutter_test/flutter_test.dart';
import 'package:zany_test_prep/data/local/key_value_store.dart';
import 'package:zany_test_prep/domain/models/avatar_catalog.dart';
import 'package:zany_test_prep/domain/models/profile.dart';
import 'package:zany_test_prep/domain/models/progress.dart';
import 'package:zany_test_prep/domain/services/catalog_filter.dart';
import 'package:zany_test_prep/features/rewards/catalog_filter_bar.dart';

import '../helpers/pump_app.dart';

final AvatarCatalog _catalog = AvatarCatalog.fromJson(
  jsonDecode(
        File('assets/avatar/manifest/avatar_catalog.json').readAsStringSync(),
      )
      as Map<String, dynamic>,
);

MemoryStore _store({int xp = 0, Set<String> owned = const {}}) {
  final store = MemoryStore();
  store.setString('onboarded.v1', 'true');
  store.setString(
    'profile.v1',
    jsonEncode(UserProfile.initial('sat', 10).toJson()),
  );
  final progress = AppProgress();
  progress.game.totalXp = xp;
  progress.game.ownedAssetIds.addAll(owned);
  store.setString('progress.v1', jsonEncode(progress.toJson()));
  return store;
}

/// Store order within a filter: cheapest first, ties by name.
List<CatalogAsset> _sorted(Iterable<CatalogAsset> assets) =>
    const CatalogFilter().apply(assets);

Finder _key(String k, {Finder? within}) => within == null
    ? find.byKey(ValueKey(k))
    : find.descendant(of: within, matching: find.byKey(ValueKey(k)));

String _count(WidgetTester tester, {Finder? within}) =>
    tester.widget<Text>(_key('catalog-result-count', within: within)).data!;

Finder _tile(CatalogAsset a) => _key('store-tile-${a.id}');

Future<void> _tap(WidgetTester tester, Finder f) async {
  await tester.tap(f);
  await tester.pumpAndSettle();
}

Future<void> _openStoreTab(WidgetTester tester, String tab) async {
  await _tap(tester, find.byIcon(Icons.card_giftcard_rounded)); // -> /rewards
  await _tap(tester, find.text('Store'));
  await _tap(tester, find.text(tab));
}

void main() {
  final items = _catalog.items;
  final pets = _catalog.basePets;

  group('store items', () {
    testWidgets('category chips narrow the grid; All groups by category', (
      tester,
    ) async {
      await pumpApp(tester, store: _store());
      await _openStoreTab(tester, 'Items');

      expect(_count(tester), '${items.length} items');
      // "All" is grouped into category sections, hats first.
      expect(find.text('HATS'), findsOneWidget);
      final hats = _sorted(items.where((a) => a.category == 'headwear'));
      expect(_tile(hats.first), findsOneWidget);

      // Every category chip is present with its friendly label.
      for (final c in items.map((a) => a.category).toSet()) {
        expect(_key('catalog-category-$c'), findsOneWidget, reason: c);
        expect(
          find.descendant(
            of: _key('catalog-category-$c'),
            matching: find.text(categoryLabel(c)),
          ),
          findsOneWidget,
        );
      }

      await _tap(tester, _key('catalog-category-eyewear'));
      final glasses = _sorted(items.where((a) => a.category == 'eyewear'));
      expect(_count(tester), 'Showing ${glasses.length} of ${items.length}');
      expect(_tile(glasses.first), findsOneWidget);
      expect(_tile(hats.first), findsNothing);
      expect(find.text('HATS'), findsNothing); // no sections when filtered

      // Tapping the selected chip again goes back to All.
      await _tap(tester, _key('catalog-category-eyewear'));
      expect(_count(tester), '${items.length} items');
    });

    testWidgets('rarity chips multi-select and Clear restores the grid', (
      tester,
    ) async {
      await pumpApp(tester, store: _store());
      await _openStoreTab(tester, 'Items');

      await _tap(tester, _key('catalog-rarity-legendary'));
      final legendary = items.where((a) => a.rarity == 'legendary').toList();
      expect(_count(tester), 'Showing ${legendary.length} of ${items.length}');

      await _tap(tester, _key('catalog-rarity-epic'));
      final epicOrLegendary = items
          .where((a) => a.rarity == 'legendary' || a.rarity == 'epic')
          .toList();
      expect(
        _count(tester),
        'Showing ${epicOrLegendary.length} of ${items.length}',
      );

      // Combine with a category: legendary/epic hats only, no rare hats.
      await _tap(tester, _key('catalog-category-headwear'));
      final bigHats = _sorted(
        epicOrLegendary.where((a) => a.category == 'headwear'),
      );
      expect(_count(tester), 'Showing ${bigHats.length} of ${items.length}');
      expect(_tile(bigHats.first), findsOneWidget);
      final rareHat = _sorted(
        items.where((a) => a.category == 'headwear' && a.rarity == 'rare'),
      ).first;
      expect(_tile(rareHat), findsNothing);

      await _tap(tester, _key('catalog-clear'));
      expect(_count(tester), '${items.length} items');
      expect(find.text('HATS'), findsOneWidget);
    });

    testWidgets('an empty result offers Clear filters', (tester) async {
      await pumpApp(tester, store: _store());
      await _openStoreTab(tester, 'Items');

      // No hat is common.
      await _tap(tester, _key('catalog-rarity-common'));
      await _tap(tester, _key('catalog-category-headwear'));
      expect(_count(tester), 'Showing 0 of ${items.length}');
      expect(find.text('No items match these filters'), findsOneWidget);

      await _tap(tester, find.text('Clear filters'));
      expect(_count(tester), '${items.length} items');
      expect(find.text('No items match these filters'), findsNothing);
    });

    testWidgets('sort menu reorders the grid', (tester) async {
      await pumpApp(tester, store: _store());
      await _openStoreTab(tester, 'Items');
      await _tap(tester, _key('catalog-category-eyewear'));
      final byPrice = _sorted(items.where((a) => a.category == 'eyewear'));
      final cheap = byPrice.first, dear = byPrice.last;
      expect(cheap.xpCost, lessThan(dear.xpCost));
      double y(CatalogAsset a) => tester.getTopLeft(_tile(a)).dy;
      expect(y(cheap), lessThan(y(dear)));

      await _tap(tester, _key('catalog-sort'));
      await _tap(
        tester,
        find.widgetWithText(
          CheckedPopupMenuItem<CatalogSort>,
          CatalogSort.priceHighLow.label,
        ),
      );
      expect(find.text(CatalogSort.priceHighLow.shortLabel), findsOneWidget);
      expect(y(dear), lessThan(y(cheap)));
      // Sorting alone is not a filter.
      expect(_count(tester), 'Showing ${byPrice.length} of ${items.length}');
    });

    testWidgets('hide owned / affordable use the wallet and collection', (
      tester,
    ) async {
      final glasses = _sorted(items.where((a) => a.category == 'eyewear'));
      final owned = glasses.first;
      final xp = glasses[3].xpCost; // can afford the 4 cheapest
      await pumpApp(
        tester,
        store: _store(xp: xp, owned: {owned.id}),
      );
      await _openStoreTab(tester, 'Items');
      await _tap(tester, _key('catalog-category-eyewear'));
      expect(_tile(owned), findsOneWidget);

      await _tap(tester, _key('catalog-toggle-hideOwned'));
      expect(_tile(owned), findsNothing);
      expect(
        _count(tester),
        'Showing ${glasses.length - 1} of ${items.length}',
      );

      await _tap(tester, _key('catalog-toggle-hideOwned'));
      await _tap(tester, _key('catalog-toggle-affordableOnly'));
      final affordable = glasses
          .where((a) => a.id != owned.id && a.xpCost <= xp)
          .length;
      expect(_count(tester), 'Showing $affordable of ${items.length}');
      expect(_tile(owned), findsNothing);
      expect(_tile(glasses[1]), findsOneWidget);
    });
  });

  group('store pets', () {
    testWidgets('rarity chips narrow the pets and Clear restores them', (
      tester,
    ) async {
      await pumpApp(tester, store: _store());
      await _openStoreTab(tester, 'Pets');

      expect(_count(tester), '${pets.length} pets');
      final cheapest = _sorted(pets).first;
      expect(_tile(cheapest), findsOneWidget);

      await _tap(tester, _key('catalog-rarity-legendary'));
      final legendary = _sorted(pets.where((p) => p.rarity == 'legendary'));
      expect(_count(tester), 'Showing ${legendary.length} of ${pets.length}');
      expect(_tile(legendary.first), findsOneWidget);
      expect(_tile(cheapest), findsNothing);

      await _tap(tester, _key('catalog-rarity-epic'));
      expect(
        _count(tester),
        'Showing ${pets.where((p) => p.rarity == 'legendary' || p.rarity == 'epic').length} of ${pets.length}',
      );

      await _tap(tester, _key('catalog-clear'));
      expect(_count(tester), '${pets.length} pets');
      expect(_tile(cheapest), findsOneWidget);
    });

    testWidgets('search finds a species; no match shows Clear filters', (
      tester,
    ) async {
      await pumpApp(tester, store: _store());
      await _openStoreTab(tester, 'Pets');

      await tester.enterText(_key('catalog-search'), 'fox');
      await tester.pumpAndSettle();
      final foxes = const CatalogFilter().withQuery('fox').apply(pets);
      expect(foxes.length, greaterThan(1));
      expect(_count(tester), 'Showing ${foxes.length} of ${pets.length}');
      expect(_tile(foxes.first), findsOneWidget);

      await tester.enterText(_key('catalog-search'), 'zzz');
      await tester.pumpAndSettle();
      expect(find.text('No pets match these filters'), findsOneWidget);
      await _tap(tester, find.text('Clear filters'));
      expect(_count(tester), '${pets.length} pets');
      final field = tester.widget<TextField>(_key('catalog-search'));
      expect(field.controller!.text, isEmpty);
    });

    testWidgets('hide owned removes adopted pets', (tester) async {
      final owned = _sorted(pets).first;
      await pumpApp(tester, store: _store(owned: {owned.id}));
      await _openStoreTab(tester, 'Pets');
      expect(_tile(owned), findsOneWidget);
      await _tap(tester, _key('catalog-toggle-hideOwned'));
      expect(_tile(owned), findsNothing);
      expect(_count(tester), 'Showing ${pets.length - 1} of ${pets.length}');
    });

    testWidgets('each tab keeps its own filters', (tester) async {
      await pumpApp(tester, store: _store());
      await _openStoreTab(tester, 'Items');
      await _tap(tester, _key('catalog-category-eyewear'));
      final glasses = items.where((a) => a.category == 'eyewear').length;

      await _tap(tester, find.text('Pets'));
      expect(_count(tester), '${pets.length} pets');
      await _tap(tester, find.text('Items'));
      expect(_count(tester), 'Showing $glasses of ${items.length}');
    });
  });

  group('customizer', () {
    // 3 hats, 3 glasses, 2 necklaces; 6 pets across rarities.
    List<CatalogAsset> pick(String category, int n) =>
        _sorted(items.where((a) => a.category == category)).take(n).toList();
    final hats = pick('headwear', 3);
    final glasses = pick('eyewear', 3);
    final necks = pick('neck_accessory', 2);
    final ownedItems = [...hats, ...glasses, ...necks];
    final ownedPets = [
      ..._sorted(pets.where((p) => p.rarity == 'common')).take(3),
      ..._sorted(pets.where((p) => p.rarity == 'rare')).take(2),
      _sorted(pets.where((p) => p.rarity == 'legendary')).first,
    ];

    Future<void> openCustomizer(WidgetTester tester, Set<String> owned) async {
      await pumpApp(tester, store: _store(xp: 100000, owned: owned));
      await _tap(tester, find.byIcon(Icons.card_giftcard_rounded));
      await _tap(tester, find.text('Customize'));
    }

    final itemList = _key('customizer-items');
    final petList = _key('customizer-companions');
    Finder itemRow(CatalogAsset a) => _key('item-row-${a.id}');
    Finder petRow(CatalogAsset a) => _key('companion-row-${a.id}');

    testWidgets('item category chips narrow the owned items', (tester) async {
      await openCustomizer(tester, {for (final a in ownedItems) a.id});
      expect(_count(tester, within: itemList), '${ownedItems.length} items');
      for (final a in ownedItems) {
        expect(itemRow(a), findsOneWidget);
      }

      await _tap(tester, _key('catalog-category-eyewear', within: itemList));
      expect(
        _count(tester, within: itemList),
        'Showing ${glasses.length} of ${ownedItems.length}',
      );
      for (final a in glasses) {
        expect(itemRow(a), findsOneWidget);
      }
      for (final a in [...hats, ...necks]) {
        expect(itemRow(a), findsNothing);
      }

      // Equipped only + Glasses (none equipped) -> empty -> Clear filters.
      await _tap(tester, _key('catalog-toggle-equippedOnly', within: itemList));
      expect(find.text('No items match these filters'), findsOneWidget);
      await _tap(tester, find.text('Clear filters'));
      for (final a in ownedItems) {
        expect(itemRow(a), findsOneWidget);
      }
    });

    testWidgets('equipped toggle shows only equipped items', (tester) async {
      await openCustomizer(tester, {for (final a in ownedItems) a.id});
      await _tap(
        tester,
        find.descendant(
          of: itemRow(glasses.first),
          matching: find.text('Equip'),
        ),
      );
      await _tap(tester, _key('catalog-toggle-equippedOnly', within: itemList));
      expect(itemRow(glasses.first), findsOneWidget);
      expect(itemRow(hats.first), findsNothing);
      expect(
        _count(tester, within: itemList),
        'Showing 1 of ${ownedItems.length}',
      );
    });

    testWidgets('companion rarity chips and search narrow the pets', (
      tester,
    ) async {
      await openCustomizer(tester, {for (final p in ownedPets) p.id});
      expect(_count(tester, within: petList), '${ownedPets.length} companions');

      await _tap(tester, _key('catalog-rarity-rare', within: petList));
      final rare = ownedPets.where((p) => p.rarity == 'rare').toList();
      expect(
        _count(tester, within: petList),
        'Showing ${rare.length} of ${ownedPets.length}',
      );
      for (final p in ownedPets) {
        expect(petRow(p), p.rarity == 'rare' ? findsOneWidget : findsNothing);
      }

      await _tap(tester, _key('catalog-clear', within: petList));
      final target = ownedPets.first;
      await tester.enterText(
        _key('catalog-search', within: petList),
        target.name,
      );
      await tester.pumpAndSettle();
      expect(petRow(target), findsOneWidget);
      expect(petRow(ownedPets.last), findsNothing);
    });

    testWidgets('short lists skip the filter bar', (tester) async {
      await openCustomizer(tester, {hats.first.id, ownedPets.first.id});
      expect(find.byType(CatalogFilterBar), findsNothing);
      expect(itemRow(hats.first), findsOneWidget);
      expect(petRow(ownedPets.first), findsOneWidget);
    });
  });
}
