/// Reward types that can come out of a chest (or, later, other sources).
///
/// This is intentionally a small **sealed** hierarchy so new reward kinds can be
/// added in one place and every `switch` over [Reward] is forced to handle them.
/// The user has more reward types coming ("other item types we will go over
/// later"); add them here and the UI/grant logic will surface the gaps.
library;

/// Coarse category, handy for icons/grouping and analytics without pattern
/// matching the concrete type.
enum RewardKind { xp, streakFreeze, xpBoost, avatar, item }

sealed class Reward {
  const Reward();

  RewardKind get kind;

  /// Short label for a reward reveal card.
  String get title;

  /// One-line description of what the player got.
  String get description;
}

/// A lump of spendable XP. (Adds to both lifetime totalXp and the spendable
/// balance, so it never dilutes the lifetime number.)
class XpReward extends Reward {
  const XpReward(this.amount);
  final int amount;

  @override
  RewardKind get kind => RewardKind.xp;
  @override
  String get title => '+$amount XP';
  @override
  String get description => 'A bonus of $amount XP to spend or save.';
}

/// One or more streak freezes (banked, capped at [kMaxStreakFreezes]).
class StreakFreezeReward extends Reward {
  const StreakFreezeReward(this.count);
  final int count;

  @override
  RewardKind get kind => RewardKind.streakFreeze;
  @override
  String get title => count == 1 ? 'Streak Freeze' : '$count Streak Freezes';
  @override
  String get description =>
      'Protects your streak on a missed day (up to 3 banked).';
}

/// An XP multiplier active for a single upcoming day.
class XpBoostReward extends Reward {
  const XpBoostReward(this.multiplier);
  final double multiplier;

  @override
  RewardKind get kind => RewardKind.xpBoost;
  @override
  String get title => '${_fmt(multiplier)}× XP Boost';
  @override
  String get description =>
      'Earn ${_fmt(multiplier)}× XP on your next day of practice.';

  static String _fmt(double m) =>
      m == m.roundToDouble() ? m.toStringAsFixed(0) : m.toStringAsFixed(1);
}

/// A catalog avatar unlocked for free.
class AvatarReward extends Reward {
  const AvatarReward({required this.assetId, required this.assetName});
  final String assetId;
  final String assetName;

  @override
  RewardKind get kind => RewardKind.avatar;
  @override
  String get title => 'New Avatar';
  @override
  String get description => 'Unlocked the "$assetName" avatar!';
}

/// A catalog item or pet unlocked for free.
class ItemReward extends Reward {
  const ItemReward({required this.assetId, required this.assetName});
  final String assetId;
  final String assetName;

  @override
  RewardKind get kind => RewardKind.item;
  @override
  String get title => 'New Item';
  @override
  String get description => 'Unlocked "$assetName" for your avatar!';
}
