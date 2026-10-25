import 'dart:math';

import '../models/avatar_catalog.dart';
import '../models/progress.dart';
import '../models/reward.dart';
import 'pet_engine.dart';
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

  /// The avatar the player is currently showing (falls back to the default;
  /// null only when the catalog is empty).
  CatalogAsset? selectedAvatar(GameState g, AvatarCatalog catalog) {
    final id = g.selectedAvatarId;
    if (id != null && catalog[id] != null) return catalog[id]!;
    return catalog.defaultAvatar;
  }

  /// Layers to render for the current loadout, ordered back-to-front by z-index.
  /// The base avatar comes first (slot null); each equipped asset carries its
  /// slot so side pets/props can be placed in the right side position.
  List<EquippedLayer> equippedLayers(GameState g, AvatarCatalog catalog) {
    final base = selectedAvatar(g, catalog);
    final layers = <EquippedLayer>[if (base != null) EquippedLayer(null, base)];
    final builtIn = base?.builtInSlots ?? const <String>[];
    g.equipped.forEach((slot, id) {
      final a = catalog[id];
      // The avatar's own art already wears this slot (a cap, glasses): keep
      // the item equipped but don't stack a second one on top.
      if (a != null && !builtIn.contains(slot)) {
        layers.add(EquippedLayer(slot, a));
      }
    });
    layers.sort((a, b) => a.asset.renderZ.compareTo(b.asset.renderZ));
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
    // Evolved pet stages are earned by levelling, never dropped.
    final items = [
      ...catalog.items.where((a) => !isOwned(g, a)).map(cand),
      ...catalog.pets.where((a) => !isOwned(g, a) && a.isPurchasable).map(cand),
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
        // A second boost on the same day never downgrades a bigger one.
        final sameDay =
            g.xpBoostDay == dayKey(now.add(const Duration(days: 1)));
        g.xpBoostMultiplier = sameDay
            ? max(g.xpBoostMultiplier, multiplier)
            : multiplier;
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
  /// Evolved pet stages cannot be bought (see [evolvePet]).
  bool purchase(GameState g, CatalogAsset asset) {
    if (isOwned(g, asset)) return false;
    if (asset.isEvolvedStage) return false;
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

  // --- Pet companions ---

  static const PetEngine petEngine = PetEngine();

  /// Companion XP of a pet's line.
  int petXpOf(GameState g, CatalogAsset pet) => g.petXp[pet.lineId] ?? 0;

  /// Companion level (1..[PetEngine.maxLevel]) of a pet's line.
  int petLevel(GameState g, CatalogAsset pet) =>
      petEngine.levelForXp(petXpOf(g, pet));

  /// The pets currently equipped in side slots.
  List<CatalogAsset> equippedPets(GameState g, AvatarCatalog catalog) => [
    for (final id in g.equipped.values)
      if (catalog[id] case final a? when a.isPet) a,
  ];

  /// Grants [amount] companion XP to every equipped pet line. Returns the
  /// lines that levelled up (line id -> new level).
  Map<String, int> grantPetXp(GameState g, AvatarCatalog catalog, int amount) {
    final levelUps = <String, int>{};
    if (amount <= 0) return levelUps;
    final seen = <String>{};
    for (final pet in equippedPets(g, catalog)) {
      if (!seen.add(pet.lineId)) continue;
      final before = petEngine.levelForXp(g.petXp[pet.lineId] ?? 0);
      g.petXp[pet.lineId] = (g.petXp[pet.lineId] ?? 0) + amount;
      final after = petEngine.levelForXp(g.petXp[pet.lineId]!);
      if (after > before) levelUps[pet.lineId] = after;
    }
    return levelUps;
  }

  /// The highest owned stage of a pet line, or null when none is owned.
  CatalogAsset? highestOwnedStage(
    GameState g,
    AvatarCatalog catalog,
    String lineId,
  ) {
    CatalogAsset? best;
    for (final stage in catalog.evolutionLine(lineId)) {
      if (isOwned(g, stage)) best = stage;
    }
    return best;
  }

  /// The stage a pet line could evolve into next (the stage after the highest
  /// owned one), or null at the final stage / when nothing is owned.
  CatalogAsset? nextStage(GameState g, AvatarCatalog catalog, String lineId) {
    final current = highestOwnedStage(g, catalog, lineId);
    final nextId = current?.evolution?.nextId;
    return nextId == null ? null : catalog[nextId];
  }

  /// Whether the line's next stage is unlocked by its current level.
  bool canEvolve(GameState g, AvatarCatalog catalog, String lineId) {
    final next = nextStage(g, catalog, lineId);
    if (next == null) return false;
    final level = petEngine.levelForXp(g.petXp[lineId] ?? 0);
    return level >= (next.evolution?.requiresLevel ?? PetEngine.maxLevel);
  }

  /// Evolves a pet line into its next stage: the new stage becomes owned and
  /// replaces the old stage wherever it was equipped. Returns the new stage,
  /// or null when the line cannot evolve yet.
  CatalogAsset? evolvePet(GameState g, AvatarCatalog catalog, String lineId) {
    if (!canEvolve(g, catalog, lineId)) return null;
    final next = nextStage(g, catalog, lineId)!;
    g.ownedAssetIds.add(next.id);
    final lineIds = catalog.evolutionLine(lineId).map((p) => p.id).toSet();
    for (final slot in g.equipped.keys.toList()) {
      if (lineIds.contains(g.equipped[slot])) g.equipped[slot] = next.id;
    }
    return next;
  }

  /// The slot [assetId] is currently equipped in, or null.
  String? equippedSlotOf(GameState g, String assetId) {
    for (final e in g.equipped.entries) {
      if (e.value == assetId) return e.key;
    }
    return null;
  }

  /// Moves an equipped side asset (pet/floating prop) to the next available one
  /// of its allowed slots, wrapping around — the "toggle through open slots"
  /// control. Skips slots occupied by *other* assets. Returns false if it can't
  /// move (not a side asset, not equipped, or no other free slot).
  bool cycleSideSlot(GameState g, AvatarCatalog catalog, String assetId) {
    final a = catalog[assetId];
    if (a == null || !a.isSide) return false;
    final current = equippedSlotOf(g, assetId);
    if (current == null) return false;
    final slots = a.allowedSlots;
    final start = slots.indexOf(current);
    for (var i = 1; i <= slots.length; i++) {
      final cand = slots[(start + i) % slots.length];
      if (cand == current) break;
      final occupant = g.equipped[cand];
      if (occupant == null || occupant == assetId) {
        g.equipped.remove(current);
        g.equipped[cand] = assetId;
        return true;
      }
    }
    return false;
  }
}
