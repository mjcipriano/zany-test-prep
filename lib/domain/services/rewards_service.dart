import 'dart:math';

import '../models/avatar_catalog.dart';
import '../models/progress.dart';
import '../models/reward.dart';
import 'reward_engine.dart';

/// One renderable layer of the avatar preview: an asset plus the slot it's
/// equipped in (null for the base avatar). The slot tells the renderer which of
/// the four side positions a pet/prop occupies.
class EquippedLayer {
  const EquippedLayer(this.slot, this.asset);
  final String? slot;
  final CatalogAsset asset;
}

/// Pure rewards/economy operations over [GameState] + the avatar [AvatarCatalog].
///
/// Everything here mutates the passed-in [GameState] in place (matching the rest
/// of the domain layer) and is deterministic given an injected [Random], so it's
/// straightforward to unit-test. The store/chest UI calls through these.
class RewardsService {
  const RewardsService({this.engine = const RewardEngine()});

  final RewardEngine engine;

  /// XP price of a streak freeze in the store (tunable; balancing TBD).
  static const int streakFreezeCost = 200;

  /// Whether [asset] is already unlocked (starter assets are always owned).
  bool isOwned(GameState g, CatalogAsset asset) =>
      asset.defaultUnlocked || g.ownedAssetIds.contains(asset.id);

  /// The avatar the player is currently showing (falls back to the default).
  CatalogAsset selectedAvatar(GameState g, AvatarCatalog catalog) {
    final id = g.selectedAvatarId;
    if (id != null && catalog[id] != null) return catalog[id]!;
    return catalog.defaultAvatar;
  }

  /// Layers to render for the current loadout, ordered back-to-front by z-index.
  /// The base avatar comes first (slot null); each equipped asset carries its
  /// slot so side pets/props can be placed in the right side position.
  List<EquippedLayer> equippedLayers(GameState g, AvatarCatalog catalog) {
    final layers = <EquippedLayer>[
      EquippedLayer(null, selectedAvatar(g, catalog)),
    ];
    g.equipped.forEach((slot, id) {
      final a = catalog[id];
      if (a != null) layers.add(EquippedLayer(slot, a));
    });
    layers.sort((a, b) => a.asset.zIndex.compareTo(b.asset.zIndex));
    return layers;
  }

  // --- Chests ---

  /// Opens one banked chest, granting and applying its reward. Returns null if
  /// there are no chests to open.
  Reward? openChest(
    GameState g,
    AvatarCatalog catalog, {
    required Random rng,
    required DateTime now,
  }) {
    if (g.unopenedChests <= 0) return null;
    g.unopenedChests -= 1;
    final reward = engine.openChest(rng, _poolsFor(g, catalog));
    applyReward(g, reward, now: now);
    return reward;
  }

  ChestPools _poolsFor(GameState g, AvatarCatalog catalog) {
    RewardCandidate cand(CatalogAsset a) => (id: a.id, name: a.name);
    final avatars = catalog.avatars
        .where((a) => !isOwned(g, a))
        .map(cand)
        .toList();
    // Items + pets are both "items" for chest purposes (worn/side cosmetics).
    final items = [
      ...catalog.items.where((a) => !isOwned(g, a)).map(cand),
      ...catalog.pets.where((a) => !isOwned(g, a)).map(cand),
    ];
    return ChestPools(
      avatars: avatars,
      items: items,
      streakFreezesOwned: g.streakFreezes,
    );
  }

  /// Applies a single reward to state. [now] is needed to schedule an XP boost.
  void applyReward(GameState g, Reward reward, {required DateTime now}) {
    switch (reward) {
      case XpReward(:final amount):
        g.totalXp += amount; // grows lifetime + spendable; spent unchanged
      case StreakFreezeReward(:final count):
        g.streakFreezes = min(kMaxStreakFreezes, g.streakFreezes + count);
      case XpBoostReward(:final multiplier):
        g.xpBoostMultiplier = multiplier;
        g.xpBoostDay = dayKey(now.add(const Duration(days: 1)));
      case AvatarReward(:final assetId):
        g.ownedAssetIds.add(assetId);
      case ItemReward(:final assetId):
        g.ownedAssetIds.add(assetId);
    }
  }

  // --- Store ---

  bool canAfford(GameState g, int cost) => g.availableXp >= cost;

  /// Buys a catalog asset with spendable XP. Returns true on success.
  bool purchase(GameState g, CatalogAsset asset) {
    if (isOwned(g, asset)) return false;
    if (!canAfford(g, asset.xpCost)) return false;
    g.spentXp += asset.xpCost;
    g.ownedAssetIds.add(asset.id);
    return true;
  }

  /// Buys a streak freeze with XP (capped at [kMaxStreakFreezes]).
  bool purchaseStreakFreeze(GameState g) {
    if (g.streakFreezes >= kMaxStreakFreezes) return false;
    if (!canAfford(g, streakFreezeCost)) return false;
    g.spentXp += streakFreezeCost;
    g.streakFreezes += 1;
    return true;
  }

  // --- Customization ---

  /// Selects an owned avatar. Returns false if not owned.
  bool selectAvatar(GameState g, AvatarCatalog catalog, String avatarId) {
    final a = catalog[avatarId];
    if (a == null || !a.isAvatar || !isOwned(g, a)) return false;
    g.selectedAvatarId = avatarId;
    return true;
  }

  /// Whether [assetId] is currently equipped in any slot.
  bool isEquipped(GameState g, String assetId) =>
      g.equipped.containsValue(assetId);

  /// Equips an owned item/pet. Worn items occupy their single slot (replacing
  /// whatever was there); pets/props with several allowed side slots fill the
  /// first empty one so multiple can be worn at once. Returns false if not owned.
  bool equip(GameState g, AvatarCatalog catalog, String assetId) {
    final a = catalog[assetId];
    if (a == null || a.isAvatar || !isOwned(g, a)) return false;
    if (a.allowedSlots.isEmpty) return false;
    if (isEquipped(g, assetId)) return true; // already on
    // Prefer an empty allowed slot; otherwise reuse the first (replace).
    final slot = a.allowedSlots.firstWhere(
      (s) => !g.equipped.containsKey(s),
      orElse: () => a.allowedSlots.first,
    );
    g.equipped[slot] = assetId;
    return true;
  }

  /// Removes whatever occupies [slot].
  void unequip(GameState g, String slot) => g.equipped.remove(slot);

  /// Removes [assetId] from whatever slot(s) it occupies.
  void unequipAsset(GameState g, String assetId) =>
      g.equipped.removeWhere((slot, id) => id == assetId);
}
