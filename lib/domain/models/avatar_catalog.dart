/// Avatar customization catalog, loaded from the vendored pack manifest
/// (`assets/avatar/manifest/avatar_catalog.json`, synced by
/// tools/sync_avatars.py from mjcipriano/zany-test-prep-avatars).
///
/// Nothing here hardcodes individual avatars/items — the catalog is the single
/// source of truth, so pulling a newer pack release expands the store and
/// customizer automatically. Each app-facing PNG is a full 512×512 pre-aligned
/// layer, so an avatar preview is just the equipped assets stacked by [zIndex].
library;

/// One entry in the catalog: an avatar, a wearable item, or a side pet/prop.
class CatalogAsset {
  const CatalogAsset({
    required this.id,
    required this.name,
    required this.type,
    required this.category,
    required this.rarity,
    required this.xpCost,
    required this.assetPath,
    required this.previewAssetPath,
    required this.allowedSlots,
    required this.zIndex,
    required this.scale,
    required this.defaultUnlocked,
  });

  final String id;
  final String name;
  final String type; // 'avatar' | 'item' | 'pet'
  final String category; // e.g. 'starter', 'headwear', 'common'
  final String rarity; // 'starter' | 'common' | 'rare' | ...
  final int xpCost;
  final String assetPath;
  final String previewAssetPath;
  final List<String> allowedSlots;
  final int zIndex;
  final double scale;
  final bool defaultUnlocked;

  bool get isAvatar => type == 'avatar';
  bool get isPet => type == 'pet';
  bool get isItem => type == 'item';

  /// The single slot a non-avatar asset occupies (items/pets list one or, for
  /// pets, the interchangeable side slots — we use the first as canonical).
  String? get primarySlot => allowedSlots.isEmpty ? null : allowedSlots.first;

  factory CatalogAsset.fromJson(Map<String, dynamic> j) => CatalogAsset(
    id: j['id'] as String,
    name: j['name'] as String,
    type: j['type'] as String,
    category: j['category'] as String? ?? '',
    rarity: j['rarity'] as String? ?? 'common',
    xpCost: (j['xp_cost'] as num?)?.toInt() ?? 0,
    assetPath: j['asset_path'] as String,
    previewAssetPath: (j['preview_asset_path'] ?? j['asset_path']) as String,
    allowedSlots: ((j['allowed_slots'] as List?) ?? const [])
        .map((e) => e.toString())
        .toList(),
    zIndex: (j['z_index'] as num?)?.toInt() ?? 0,
    scale: (j['scale'] as num?)?.toDouble() ?? 1.0,
    defaultUnlocked: j['default_unlocked'] as bool? ?? false,
  );
}

/// The whole parsed catalog plus convenience lookups.
class AvatarCatalog {
  AvatarCatalog({
    required this.packId,
    required this.styleVersion,
    required this.assets,
  }) : byId = {for (final a in assets) a.id: a};

  final String packId;
  final String styleVersion;
  final List<CatalogAsset> assets;
  final Map<String, CatalogAsset> byId;

  List<CatalogAsset> get avatars => assets.where((a) => a.isAvatar).toList();
  List<CatalogAsset> get items => assets.where((a) => a.isItem).toList();
  List<CatalogAsset> get pets => assets.where((a) => a.isPet).toList();

  /// Avatars unlocked by default (the starter set, always owned).
  List<CatalogAsset> get starterAvatars =>
      avatars.where((a) => a.defaultUnlocked).toList();

  CatalogAsset? operator [](String id) => byId[id];

  /// The avatar shown when the player hasn't picked one yet.
  CatalogAsset get defaultAvatar =>
      starterAvatars.isNotEmpty ? starterAvatars.first : avatars.first;

  factory AvatarCatalog.fromJson(Map<String, dynamic> j) => AvatarCatalog(
    packId: j['pack_id'] as String? ?? 'unknown',
    styleVersion: j['style_version'] as String? ?? 'unknown',
    assets: ((j['assets'] as List?) ?? const [])
        .map((e) => CatalogAsset.fromJson((e as Map).cast<String, dynamic>()))
        .toList(),
  );

  /// Empty catalog, used as a safe fallback if the manifest is missing.
  factory AvatarCatalog.empty() =>
      AvatarCatalog(packId: 'none', styleVersion: 'none', assets: const []);
}
