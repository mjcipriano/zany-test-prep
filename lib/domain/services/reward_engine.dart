import 'dart:math';

import '../models/progress.dart';
import '../models/reward.dart';

/// A catalog asset eligible to be granted by a chest (avatar/item/pet).
typedef RewardCandidate = ({String id, String name});

/// The pools a chest can draw unlockable content from. The engine stays
/// catalog-agnostic: callers pass only the *unowned* candidates.
class ChestPools {
  const ChestPools({
    this.avatars = const [],
    this.items = const [],
    this.streakFreezesOwned = 0,
  });

  final List<RewardCandidate> avatars;
  final List<RewardCandidate> items;
  final int streakFreezesOwned;
}

/// Rolls the contents of a chest.
///
/// The drop table here is a deliberate **first pass / stub** — the user has more
/// reward types and tuning to specify later. It's a pure function of an injected
/// [Random] so it's fully unit-testable, and every probability lives in one
/// place ([_weights]) for easy balancing.
class RewardEngine {
  const RewardEngine();

  // Relative weights per reward kind. Categories that can't drop (e.g. no
  // unowned avatars left, freezes already maxed) are skipped and their weight
  // redistributes naturally.
  static const Map<RewardKind, double> _weights = {
    RewardKind.xp: 45,
    RewardKind.item: 20,
    RewardKind.xpBoost: 15,
    RewardKind.streakFreeze: 15,
    RewardKind.avatar: 5,
  };

  // XP payout buckets (amount -> weight), small amounts favoured.
  static const Map<int, double> _xpBuckets = {
    25: 5,
    50: 4,
    75: 2,
    100: 2,
    150: 1,
  };

  // XP-boost multipliers (value -> weight). Not const: double map keys aren't
  // allowed in const maps.
  static final Map<double, double> _boostBuckets = {1.5: 3, 2.0: 1};

  Reward openChest(Random rng, ChestPools pools) {
    final available = <RewardKind, double>{};
    _weights.forEach((kind, weight) {
      final possible = switch (kind) {
        RewardKind.avatar => pools.avatars.isNotEmpty,
        RewardKind.item => pools.items.isNotEmpty,
        RewardKind.streakFreeze => pools.streakFreezesOwned < kMaxStreakFreezes,
        RewardKind.xp || RewardKind.xpBoost => true,
      };
      if (possible) available[kind] = weight;
    });

    final kind = _pickWeighted(rng, available);
    return switch (kind) {
      RewardKind.xp => XpReward(_pickWeighted(rng, _xpBuckets)),
      RewardKind.xpBoost => XpBoostReward(_pickWeighted(rng, _boostBuckets)),
      RewardKind.streakFreeze => const StreakFreezeReward(1),
      RewardKind.avatar => () {
        final a = pools.avatars[rng.nextInt(pools.avatars.length)];
        return AvatarReward(assetId: a.id, assetName: a.name);
      }(),
      RewardKind.item => () {
        final it = pools.items[rng.nextInt(pools.items.length)];
        return ItemReward(assetId: it.id, assetName: it.name);
      }(),
    };
  }

  /// Weighted pick over a map of value -> weight. Falls back to XP if empty
  /// (should never happen since xp is always available).
  static T _pickWeighted<T>(Random rng, Map<T, double> weights) {
    final total = weights.values.fold<double>(0, (a, b) => a + b);
    var roll = rng.nextDouble() * total;
    for (final entry in weights.entries) {
      roll -= entry.value;
      if (roll < 0) return entry.key;
    }
    return weights.keys.last;
  }
}
