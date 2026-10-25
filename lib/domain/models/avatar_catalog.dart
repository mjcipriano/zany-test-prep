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

/// z of items drawn behind the avatar: under the avatar (0), above back auras
/// (-20) and background frames (-40).
const int kBehindAvatarZ = -10;

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

/// A point in the normalised 512 composition frame (0..1 on both axes).
class FramePoint {
  const FramePoint(this.x, this.y);
  final double x;
  final double y;

  factory FramePoint.fromJson(Map<String, dynamic> j) => FramePoint(
    (j['x'] as num?)?.toDouble() ?? 0.5,
    (j['y'] as num?)?.toDouble() ?? 0.5,
  );
}

/// An avatar's measured face (pack contract `face_fit_v1`): named points
/// (`eyes`, `brow`, `nose_bridge`, `mouth`, `ear_l`, …) and reference widths
/// (`face`, `eyes`, `mouth`, `ears`), all normalised to the 512 frame. Each
/// avatar's head sits at its own height and size, so worn face/head items are
/// placed on this rig instead of one fixed box per slot.
class FaceRig {
  const FaceRig({required this.points, required this.widths});

  final Map<String, FramePoint> points;
  final Map<String, double> widths;

  static FaceRig? fromJson(Object? raw) {
    if (raw is! Map) return null;
    final points = <String, FramePoint>{
      for (final e in ((raw['points'] as Map?) ?? const {}).entries)
        if (e.value is Map)
          e.key.toString(): FramePoint.fromJson(
            (e.value as Map).cast<String, dynamic>(),
          ),
    };
    final widths = <String, double>{
      for (final e in ((raw['widths'] as Map?) ?? const {}).entries)
        if (e.value is num) e.key.toString(): (e.value as num).toDouble(),
    };
    if (points.isEmpty || widths.isEmpty) return null;
    return FaceRig(points: points, widths: widths);
  }
}

/// Where a worn item hangs on a [FaceRig] (pack contract `face_fit_v1`): the
/// sprite point [spriteAnchor] (0..1 of the sprite) lands on the rig point
/// [anchor], and the sprite is [width] × the rig's [widthRef] width wide.
/// [behind] items (hoods, the headset) draw under the avatar.
class ItemFit {
  const ItemFit({
    required this.kind,
    required this.anchor,
    required this.spriteAnchor,
    required this.widthRef,
    required this.width,
    this.behind = false,
    this.widthFloorRef,
    this.widthFloor,
    this.clipAvatarAbove,
  });

  final String kind;
  final String anchor;
  final FramePoint spriteAnchor;
  final String widthRef;
  final double width;
  final bool behind;

  /// Hats are at least [widthFloor] × the rig's [widthFloorRef] width (the
  /// `hair` width) so they cover big hair instead of perching on it.
  final String? widthFloorRef;
  final double? widthFloor;

  /// "Hat hair": hide the avatar above `top + clipAvatarAbove × height` of this
  /// item — the hair that would be squashed under the hat.
  final double? clipAvatarAbove;

  static ItemFit? fromJson(Object? raw) {
    if (raw is! Map) return null;
    final j = raw.cast<String, dynamic>();
    final anchor = j['anchor'], widthRef = j['width_ref'], width = j['width'];
    if (anchor is! String || widthRef is! String || width is! num) return null;
    return ItemFit(
      kind: (j['kind'] ?? '').toString(),
      anchor: anchor,
      spriteAnchor: j['sprite_anchor'] is Map
          ? FramePoint.fromJson(
              (j['sprite_anchor'] as Map).cast<String, dynamic>(),
            )
          : const FramePoint(0.5, 0.5),
      widthRef: widthRef,
      width: width.toDouble(),
      behind: j['behind'] == true,
      widthFloorRef: (j['width_floor'] as Map?)?['ref']?.toString(),
      widthFloor: ((j['width_floor'] as Map?)?['width'] as num?)?.toDouble(),
      clipAvatarAbove: (j['clip_avatar_above'] as num?)?.toDouble(),
    );
  }
}

/// A pet's place in its evolution line (pack contract `pet_evolution_v1`).
/// Stage 1 is the base companion bought in the store; stages 2 and 3 are
/// unlocked by levelling the pet up while it is equipped.
class PetEvolution {
  const PetEvolution({
    required this.lineId,
    required this.stage,
    required this.stageName,
    required this.baseId,
    required this.nextId,
    required this.requiresLevel,
  });

  final String lineId;
  final int stage;
  final String stageName;
  final String baseId;
  final String? nextId;

  /// Pet level needed to unlock *this* stage (1 for the base stage).
  final int requiresLevel;

  bool get isBase => stage <= 1;

  factory PetEvolution.fromJson(Map<String, dynamic> j, String fallbackId) {
    final stage = (j['stage'] as num?)?.toInt() ?? 1;
    return PetEvolution(
      lineId: (j['line_id'] ?? fallbackId).toString(),
      stage: stage,
      stageName: (j['stage_name'] ?? 'Stage $stage').toString(),
      baseId: (j['base_id'] ?? fallbackId).toString(),
      nextId: j['next_id']?.toString(),
      requiresLevel: (j['requires_level'] as num?)?.toInt() ?? 1,
    );
  }
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
    this.unlockCondition = '',
    this.evolution,
    this.variantOf,
    this.spriteWidth = 0,
    this.spriteHeight = 0,
    this.tags = const [],
    this.faceRig,
    this.fit,
    this.builtInSlots = const [],
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

  /// Raw unlock rule from the pack (`default`, `spend_xp:<n>`, `evolve:…`).
  final String unlockCondition;

  /// Evolution metadata (pets only; null for packs without the contract).
  final PetEvolution? evolution;

  /// For procedurally derived item variants, the base item's id.
  final String? variantOf;

  /// Pixel size of the trimmed sprite (0 when the pack does not record it).
  final int spriteWidth;
  final int spriteHeight;
  final List<String> tags;

  /// Avatars only: the measured face that worn items are fitted to.
  final FaceRig? faceRig;

  /// Head/face/ear items only: how the item hangs on an avatar's [FaceRig].
  final ItemFit? fit;

  /// Avatars only: worn slots the art already fills (it wears a cap or
  /// glasses). Items equipped in these slots are hidden on this avatar.
  final List<String> builtInSlots;

  /// Draw order: items fitted [ItemFit.behind] the avatar (hoods, the headset)
  /// sit just behind it — in front of auras and frames, under the avatar.
  int get renderZ => (fit?.behind ?? false) ? kBehindAvatarZ : zIndex;

  /// Sprite aspect ratio (width / height), or null when unknown.
  double? get spriteAspect =>
      spriteWidth > 0 && spriteHeight > 0 ? spriteWidth / spriteHeight : null;

  /// Headwear that should hover above the head (a halo, an orbiting ring)
  /// rather than sit on the brow line. Decided by the pack's `floating` tag
  /// only — item ids are not reliable (the pack's "halo_ring" is drawn as a
  /// bucket hat).
  bool get floatsAboveHead => tags.contains('floating');

  /// Pets beyond their base stage are earned by levelling, never bought or
  /// dropped from chests.
  bool get isEvolvedStage => (evolution?.stage ?? 1) > 1;

  /// Whether the store / chests may hand this out.
  bool get isPurchasable =>
      !defaultUnlocked &&
      !isEvolvedStage &&
      !unlockCondition.startsWith('evolve:');

  /// The evolution line this pet belongs to (its own id when the pack has no
  /// evolution data, so every pet still has a line to level).
  String get lineId => evolution?.lineId ?? id;

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
      unlockCondition: (j['unlock_condition'] ?? '').toString(),
      evolution: j['evolution'] is Map
          ? PetEvolution.fromJson(
              (j['evolution'] as Map).cast<String, dynamic>(),
              j['id'] as String,
            )
          : null,
      variantOf: j['variant_of']?.toString(),
      spriteWidth: ((j['sprite_size'] as Map?)?['width'] as num?)?.toInt() ?? 0,
      spriteHeight:
          ((j['sprite_size'] as Map?)?['height'] as num?)?.toInt() ?? 0,
      tags: ((j['tags'] as List?) ?? const [])
          .map((e) => e.toString())
          .toList(),
      faceRig: FaceRig.fromJson(j['face_rig']),
      fit: ItemFit.fromJson(j['fit']),
      builtInSlots: ((j['built_in_slots'] as List?) ?? const [])
          .map((e) => e.toString())
          .toList(),
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

  /// Base-stage pets (what the store sells); evolved stages are earned.
  List<CatalogAsset> get basePets =>
      pets.where((p) => !p.isEvolvedStage).toList();

  /// All stages of a pet line, lowest stage first.
  List<CatalogAsset> evolutionLine(String lineId) =>
      pets.where((p) => p.lineId == lineId).toList()..sort(
        (a, b) => (a.evolution?.stage ?? 1).compareTo(b.evolution?.stage ?? 1),
      );

  CatalogAsset? operator [](String id) => byId[id];

  /// The avatar shown when the player hasn't picked one yet, or null when the
  /// catalog has no avatars at all (e.g. the asset pack failed to load).
  CatalogAsset? get defaultAvatar => starterAvatars.isNotEmpty
      ? starterAvatars.first
      : (avatars.isNotEmpty ? avatars.first : null);

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
