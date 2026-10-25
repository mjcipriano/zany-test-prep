/// Browsing filters for the Store and the avatar customizer: narrow a list of
/// catalog assets by item category, rarity, a free-text search (pets: name or
/// species tag), and the player's status (owned / affordable / equipped), then
/// sort it.
///
/// Pure Dart (no Flutter) so it is unit-testable; the chips that drive it live
/// in `features/rewards/catalog_filter_bar.dart`.
library;

import '../models/avatar_catalog.dart';

/// Item categories in display order: head to toe, then the backdrop and the
/// floating props. Categories the pack adds later sort after these, A→Z.
const List<String> kItemCategoryOrder = [
  'headwear',
  'eyewear',
  'face_accessory',
  'ear_accessory',
  'neck_accessory',
  'chest_badge',
  'back_aura',
  'background_frame',
  'floating_props',
];

const Map<String, String> _categoryLabels = {
  'headwear': 'Hats',
  'eyewear': 'Glasses',
  'face_accessory': 'Face',
  'ear_accessory': 'Ears',
  'neck_accessory': 'Neck',
  'chest_badge': 'Badges',
  'back_aura': 'Auras',
  'background_frame': 'Frames',
  'floating_props': 'Floating',
};

/// Rarities from most common to rarest.
const List<String> kRarityOrder = [
  'starter',
  'common',
  'uncommon',
  'rare',
  'epic',
  'legendary',
];

String _titleCase(String s) => s
    .split(RegExp(r'[_\s]+'))
    .where((w) => w.isNotEmpty)
    .map((w) => w[0].toUpperCase() + w.substring(1))
    .join(' ');

/// Short, friendly chip label for an item category ("headwear" → "Hats").
/// Unknown categories fall back to title case ("jet_packs" → "Jet Packs").
String categoryLabel(String category) =>
    _categoryLabels[category] ??
    (category.isEmpty ? 'Other' : _titleCase(category));

/// "legendary" → "Legendary".
String rarityLabel(String rarity) =>
    rarity.isEmpty ? 'Unknown' : _titleCase(rarity);

/// 0 for the most common rarity; unknown rarities rank after legendary.
int rarityRank(String rarity) {
  final i = kRarityOrder.indexOf(rarity);
  return i < 0 ? kRarityOrder.length : i;
}

int _categoryRank(String category) {
  final i = kItemCategoryOrder.indexOf(category);
  return i < 0 ? kItemCategoryOrder.length : i;
}

/// Orders categories by [kItemCategoryOrder], unknown ones after, A→Z.
int compareCategories(String a, String b) {
  final byRank = _categoryRank(a).compareTo(_categoryRank(b));
  return byRank != 0 ? byRank : a.compareTo(b);
}

/// Orders rarities common → legendary, unknown ones after, A→Z.
int compareRarities(String a, String b) {
  final byRank = rarityRank(a).compareTo(rarityRank(b));
  return byRank != 0 ? byRank : a.compareTo(b);
}

/// How a filtered list is ordered.
enum CatalogSort {
  priceLowHigh('Price: low to high', 'Cheapest'),
  priceHighLow('Price: high to low', 'Priciest'),
  rarity('Rarest first', 'Rarest'),
  name('Name (A–Z)', 'A–Z');

  const CatalogSort(this.label, this.shortLabel);

  /// Menu label.
  final String label;

  /// Compact label for the sort chip.
  final String shortLabel;
}

/// Player-status toggles a screen can offer.
enum CatalogToggle {
  hideOwned('Hide owned'),
  affordableOnly('Affordable'),
  equippedOnly('Equipped');

  const CatalogToggle(this.label);
  final String label;
}

/// The player's relationship to each asset, supplied by the screen. A toggle
/// whose callback is missing filters nothing.
class CatalogStatus {
  const CatalogStatus({this.isOwned, this.canAfford, this.isEquipped});

  final bool Function(CatalogAsset a)? isOwned;

  /// Whether the player has enough XP to buy [a] (ownership is checked
  /// separately: "Affordable" means buyable right now).
  final bool Function(CatalogAsset a)? canAfford;
  final bool Function(CatalogAsset a)? isEquipped;
}

/// An immutable filter + sort selection.
class CatalogFilter {
  const CatalogFilter({
    this.category,
    this.rarities = const {},
    this.query = '',
    this.toggles = const {},
    this.sort = CatalogSort.priceLowHigh,
  });

  /// Selected item category, or null for "All".
  final String? category;

  /// Selected rarities (multi-select); empty means every rarity.
  final Set<String> rarities;

  /// Free text matched against the name and tags (e.g. a pet species).
  final String query;

  /// Active status toggles.
  final Set<CatalogToggle> toggles;
  final CatalogSort sort;

  /// Whether anything (other than the sort order) narrows the list.
  bool get hasActiveFilters =>
      category != null ||
      rarities.isNotEmpty ||
      query.trim().isNotEmpty ||
      toggles.isNotEmpty;

  /// Same sort, no filters.
  CatalogFilter cleared() => CatalogFilter(sort: sort);

  CatalogFilter withCategory(String? value) => CatalogFilter(
    category: value,
    rarities: rarities,
    query: query,
    toggles: toggles,
    sort: sort,
  );

  CatalogFilter toggleRarity(String rarity) => CatalogFilter(
    category: category,
    rarities: rarities.contains(rarity)
        ? ({...rarities}..remove(rarity))
        : {...rarities, rarity},
    query: query,
    toggles: toggles,
    sort: sort,
  );

  CatalogFilter withQuery(String value) => CatalogFilter(
    category: category,
    rarities: rarities,
    query: value,
    toggles: toggles,
    sort: sort,
  );

  CatalogFilter toggle(CatalogToggle t) => CatalogFilter(
    category: category,
    rarities: rarities,
    query: query,
    toggles: toggles.contains(t) ? ({...toggles}..remove(t)) : {...toggles, t},
    sort: sort,
  );

  CatalogFilter withSort(CatalogSort value) => CatalogFilter(
    category: category,
    rarities: rarities,
    query: query,
    toggles: toggles,
    sort: value,
  );

  bool _matchesQuery(CatalogAsset a) {
    final tokens = query.toLowerCase().split(RegExp(r'\s+'))
      ..removeWhere((t) => t.isEmpty);
    if (tokens.isEmpty) return true;
    final name = a.name.toLowerCase();
    final tags = a.tags.map((t) => t.toLowerCase()).toSet();
    return tokens.every((t) => name.contains(t) || tags.contains(t));
  }

  /// Whether [a] passes every active filter. [ignoreCategory] /
  /// [ignoreRarity] skip one facet, for computing chip counts.
  bool matches(
    CatalogAsset a, {
    CatalogStatus status = const CatalogStatus(),
    bool ignoreCategory = false,
    bool ignoreRarity = false,
  }) {
    if (!ignoreCategory && category != null && a.category != category) {
      return false;
    }
    if (!ignoreRarity && rarities.isNotEmpty && !rarities.contains(a.rarity)) {
      return false;
    }
    if (!_matchesQuery(a)) return false;
    final owned = status.isOwned?.call(a) ?? false;
    if (toggles.contains(CatalogToggle.hideOwned) && owned) return false;
    if (toggles.contains(CatalogToggle.affordableOnly) &&
        status.canAfford != null &&
        (owned || !status.canAfford!(a))) {
      return false;
    }
    if (toggles.contains(CatalogToggle.equippedOnly) &&
        status.isEquipped != null &&
        !status.isEquipped!(a)) {
      return false;
    }
    return true;
  }

  int _compare(CatalogAsset x, CatalogAsset y) {
    int byName() {
      final n = x.name.toLowerCase().compareTo(y.name.toLowerCase());
      return n != 0 ? n : x.id.compareTo(y.id);
    }

    int byPrice() => x.xpCost.compareTo(y.xpCost);
    switch (sort) {
      case CatalogSort.priceLowHigh:
        final c = byPrice();
        return c != 0 ? c : byName();
      case CatalogSort.priceHighLow:
        final c = -byPrice();
        return c != 0 ? c : byName();
      case CatalogSort.rarity:
        final r = -compareRarities(x.rarity, y.rarity);
        if (r != 0) return r;
        final c = byPrice();
        return c != 0 ? c : byName();
      case CatalogSort.name:
        return byName();
    }
  }

  /// The assets that pass the filter, in [sort] order (a new list).
  List<CatalogAsset> apply(
    Iterable<CatalogAsset> assets, {
    CatalogStatus status = const CatalogStatus(),
  }) =>
      assets.where((a) => matches(a, status: status)).toList()..sort(_compare);

  /// Count per category of the assets passing every *other* filter, so each
  /// chip shows what tapping it would yield. Every category present in
  /// [assets] gets an entry (possibly 0), in display order.
  Map<String, int> categoryCounts(
    Iterable<CatalogAsset> assets, {
    CatalogStatus status = const CatalogStatus(),
  }) {
    final keys = assets.map((a) => a.category).toSet().toList()
      ..sort(compareCategories);
    final counts = {for (final k in keys) k: 0};
    for (final a in assets) {
      if (matches(a, status: status, ignoreCategory: true)) {
        counts[a.category] = counts[a.category]! + 1;
      }
    }
    return counts;
  }

  /// Count per rarity of the assets passing every *other* filter; every
  /// rarity present in [assets] gets an entry, common → legendary.
  Map<String, int> rarityCounts(
    Iterable<CatalogAsset> assets, {
    CatalogStatus status = const CatalogStatus(),
  }) {
    final keys = assets.map((a) => a.rarity).toSet().toList()
      ..sort(compareRarities);
    final counts = {for (final k in keys) k: 0};
    for (final a in assets) {
      if (matches(a, status: status, ignoreRarity: true)) {
        counts[a.rarity] = counts[a.rarity]! + 1;
      }
    }
    return counts;
  }
}

/// Splits an already-sorted list into category sections (display order),
/// keeping the sort within each section.
List<MapEntry<String, List<CatalogAsset>>> groupByCategory(
  Iterable<CatalogAsset> sorted,
) {
  final groups = <String, List<CatalogAsset>>{};
  for (final a in sorted) {
    (groups[a.category] ??= []).add(a);
  }
  return groups.entries.toList()
    ..sort((a, b) => compareCategories(a.key, b.key));
}
