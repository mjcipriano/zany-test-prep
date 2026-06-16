import 'dart:math';

import '../models/avatar_catalog.dart';
import '../models/progress.dart';
import '../models/reward.dart';
import 'reward_engine.dart';

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

  /// Catalog assets to render for the current loadout, ordered back-to-front.
  List<CatalogAsset> equippedLayers(GameState g, AvatarCatalog catalog) {
    final layers = <CatalogAsset>[selectedAvatar(g, catalog)];
    for (final id in g.equipped.values) {
      final a = catalog[id];
      if (a != null) layers.add(a);
    }
    layers.sort((a, b) => a.zIndex.compareTo(b.zIndex));
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

  /// Equips an owned item/pet into its slot. Returns false if not owned.
  bool equip(GameState g, AvatarCatalog catalog, String assetId) {
    final a = catalog[assetId];
    if (a == null || a.isAvatar || !isOwned(g, a)) return false;
    final slot = a.primarySlot;
    if (slot == null) return false;
    g.equipped[slot] = assetId;
    return true;
  }

  /// Removes whatever occupies [slot].
  void unequip(GameState g, String slot) => g.equipped.remove(slot);
}
