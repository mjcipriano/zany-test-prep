/// Avatar customization catalog, loaded from the vendored pack manifest
/// (`assets/avatar/manifest/avatar_catalog.json`, synced by
/// tools/sync_avatars.py from mjcipriano/zany-test-prep-avatars).
///
/// Nothing here hardcodes individual avatars/items — the catalog is the single
/// source of truth, so pulling a newer pack release expands the store and
/// customizer automatically. Item/pet PNGs are tightly trimmed sprites; each
/// carries a [TargetBox] placement (the pack's `target_box_v1` contract) telling
/// the preview where to center it and how big it may be. Side assets also provide
/// per-slot targets. See the AvatarPreview widget / `placementRect`.
library;

/// Item categories we deliberately exclude from the app: top/jacket overlays
/// ("blazers") don't line up with the varied avatar torsos, so they're filtered
/// out of the store, customizer, and chest drops.
const Set<String> kExcludedItemCategories = {'jacket_overlay'};

/// A normalized placement box (fractions of the 512 composition frame): where a
/// trimmed sprite's center goes ([cx],[cy]) and the max box it may occupy
/// ([w],[h], fit with contain). This is the pack's `target_box_v1` contract.
class TargetBox {
  const TargetBox(this.cx, this.cy, this.w, this.h);

  final double cx;
  final double cy;
  final double w;
  final double h;

  /// Full-frame fallback (used for avatars / assets without placement data).
  static const TargetBox full = TargetBox(0.5, 0.5, 1.0, 1.0);

  factory TargetBox.fromJson(Map<String, dynamic> j) => TargetBox(
    (j['cx'] as num?)?.toDouble() ?? 0.5,
    (j['cy'] as num?)?.toDouble() ?? 0.5,
    (j['w'] as num?)?.toDouble() ?? 1.0,
    (j['h'] as num?)?.toDouble() ?? 1.0,
  );
}

/// One entry in the catalog: an avatar, a wearable item, or a side pet/prop.
class CatalogAsset {
  const CatalogAsset({
    required this.id,
    required this.name,
    required this.type,
    required this.category,
    required this.slotType,
    required this.rarity,
    required this.xpCost,
    required this.assetPath,
    required this.previewAssetPath,
    required this.allowedSlots,
    required this.zIndex,
    required this.scale,
    required this.target,
    required this.targetsBySlot,
    required this.defaultUnlocked,
  });

  final String id;
  final String name;
  final String type; // 'avatar' | 'item' | 'pet'
  final String category; // e.g. 'starter', 'headwear', 'common'
  final String slotType; // 'base' (avatar) | 'worn' | 'side'
  final String rarity; // 'starter' | 'common' | 'rare' | ...
  final int xpCost;
  final String assetPath;
  final String previewAssetPath;
  final List<String> allowedSlots;
  final int zIndex;
  final double scale; // optional multiplier on the target box (default 1.0)
  final TargetBox target; // default placement target
  final Map<String, TargetBox>
  targetsBySlot; // per-slot overrides (side assets)
  final bool defaultUnlocked;

  bool get isAvatar => type == 'avatar';
  bool get isPet => type == 'pet';
  bool get isItem => type == 'item';

  /// Pets and floating props float in the four side slots; everything else is a
  /// worn overlay anchored to the body.
  bool get isSide => slotType == 'side';

  /// The single slot a non-avatar asset occupies (items/pets list one or, for
  /// pets, the interchangeable side slots — we use the first as canonical).
  String? get primarySlot => allowedSlots.isEmpty ? null : allowedSlots.first;

  /// The placement box to use when equipped in [slot] (per-slot override for
  /// side assets, otherwise the default [target]).
  TargetBox targetForSlot(String? slot) =>
      (slot != null ? targetsBySlot[slot] : null) ?? target;

  factory CatalogAsset.fromJson(Map<String, dynamic> j) {
    final placement =
        (j['placement'] as Map?)?.cast<String, dynamic>() ?? const {};
    final target = placement['target'] is Map
        ? TargetBox.fromJson(
            (placement['target'] as Map).cast<String, dynamic>(),
          )
        : TargetBox.full;
    final rawBySlot =
        (placement['targets_by_slot'] as Map?)?.cast<String, dynamic>() ??
        const {};
    final targetsBySlot = <String, TargetBox>{
      for (final e in rawBySlot.entries)
        if (e.value is Map)
          e.key: TargetBox.fromJson((e.value as Map).cast<String, dynamic>()),
    };
    return CatalogAsset(
      id: j['id'] as String,
      name: j['name'] as String,
      type: j['type'] as String,
      category: j['category'] as String? ?? '',
      slotType: j['slot_type'] as String? ?? 'worn',
      rarity: j['rarity'] as String? ?? 'common',
      xpCost: (j['xp_cost'] as num?)?.toInt() ?? 0,
      assetPath: j['asset_path'] as String,
      previewAssetPath: (j['preview_asset_path'] ?? j['asset_path']) as String,
      allowedSlots: ((j['allowed_slots'] as List?) ?? const [])
          .map((e) => e.toString())
          .toList(),
      zIndex: (j['z_index'] as num?)?.toInt() ?? 0,
      scale: (j['scale'] as num?)?.toDouble() ?? 1.0,
      target: target,
      targetsBySlot: targetsBySlot,
      defaultUnlocked: j['default_unlocked'] as bool? ?? false,
    );
  }
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
        .where((a) => !kExcludedItemCategories.contains(a.category))
        .toList(),
  );

  /// Empty catalog, used as a safe fallback if the manifest is missing.
  factory AvatarCatalog.empty() =>
      AvatarCatalog(packId: 'none', styleVersion: 'none', assets: const []);
}
