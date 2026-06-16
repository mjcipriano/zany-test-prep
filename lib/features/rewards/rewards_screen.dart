import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:go_router/go_router.dart';

import '../../app/app_controller.dart';
import '../../core/sound_service.dart';
import '../../design/theme.dart';
import '../../design/widgets.dart';
import '../../domain/models/progress.dart';
import '../../domain/models/reward.dart';
import 'avatar_view.dart';

/// The rewards hub: XP balance, chests to open, streak freezes, XP boost, and
/// entry points into the store and avatar customizer. Reached from the stats
/// page and the home screen.
class RewardsScreen extends ConsumerWidget {
  const RewardsScreen({super.key});

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    final data = ref.watch(appControllerProvider).valueOrNull;
    if (data == null) {
      return const Scaffold(body: Center(child: CircularProgressIndicator()));
    }
    final g = data.progress.game;
    final rewards = ref.read(rewardsServiceProvider);
    final layers = rewards.equippedLayers(g, data.catalog);
    final scheme = Theme.of(context).colorScheme;

    return Scaffold(
      appBar: AppBar(title: const Text('Rewards')),
      body: ListView(
        padding: kPagePadding,
        children: [
          // --- XP wallet ---
          AppCard(
            color: AppTheme.xpGold.withValues(alpha: 0.14),
            child: Row(
              children: [
                const Icon(
                  Icons.bolt_rounded,
                  color: AppTheme.xpGold,
                  size: 36,
                ),
                Gap.m,
                Expanded(
                  child: Column(
                    crossAxisAlignment: CrossAxisAlignment.start,
                    children: [
                      Text(
                        '${g.availableXp} XP',
                        style: const TextStyle(
                          fontSize: 26,
                          fontWeight: FontWeight.w900,
                        ),
                      ),
                      Text(
                        'available to spend  •  ${g.totalXp} earned all-time',
                        style: Theme.of(context).textTheme.bodySmall,
                      ),
                    ],
                  ),
                ),
              ],
            ),
          ),
          Gap.m,

          // --- Current avatar ---
          AppCard(
            child: Row(
              children: [
                AvatarPreview(layers: layers, size: 96),
                Gap.m,
                Expanded(
                  child: Column(
                    crossAxisAlignment: CrossAxisAlignment.start,
                    children: [
                      Text(
                        rewards.selectedAvatar(g, data.catalog).name,
                        style: const TextStyle(
                          fontWeight: FontWeight.w800,
                          fontSize: 18,
                        ),
                      ),
                      Gap.xs,
                      Text(
                        'Your avatar',
                        style: Theme.of(context).textTheme.bodySmall,
                      ),
                      Gap.s,
                      FilledButton.tonalIcon(
                        onPressed: () => context.push('/avatar'),
                        icon: const Icon(Icons.tune_rounded),
                        label: const Text('Customize'),
                      ),
                    ],
                  ),
                ),
              ],
            ),
          ),
          Gap.l,

          // --- Chests ---
          const SectionLabel('Chests'),
          _ChestCard(chests: g.unopenedChests),
          Gap.l,

          // --- Boosts & freezes ---
          const SectionLabel('Boosts'),
          Row(
            children: [
              Expanded(
                child: _MiniStat(
                  icon: Icons.ac_unit_rounded,
                  color: const Color(0xFF4FA3D1),
                  value: '${g.streakFreezes}/$kMaxStreakFreezes',
                  label: 'Streak freezes',
                ),
              ),
              Gap.m,
              Expanded(
                child: _MiniStat(
                  icon: Icons.rocket_launch_rounded,
                  color: AppTheme.streak,
                  value: g.xpBoostMultiplier > 1.0 && g.xpBoostDay != null
                      ? '${g.xpBoostMultiplier.toStringAsFixed(g.xpBoostMultiplier == g.xpBoostMultiplier.roundToDouble() ? 0 : 1)}×'
                      : 'None',
                  label: 'XP boost queued',
                ),
              ),
            ],
          ),
          Gap.l,

          // --- Store ---
          AppCard(
            color: scheme.primaryContainer,
            onTap: () => context.push('/store'),
            child: Row(
              children: [
                Icon(Icons.storefront_rounded, color: scheme.primary, size: 32),
                Gap.m,
                const Expanded(
                  child: Text(
                    'Store',
                    style: TextStyle(fontWeight: FontWeight.w800, fontSize: 18),
                  ),
                ),
                const Icon(Icons.chevron_right_rounded),
              ],
            ),
          ),
        ],
      ),
    );
  }
}

class _ChestCard extends ConsumerWidget {
  const _ChestCard({required this.chests});
  final int chests;

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    final has = chests > 0;
    return AppCard(
      color: has ? AppTheme.xpGold.withValues(alpha: 0.16) : null,
      child: Row(
        children: [
          Opacity(
            opacity: has ? 1 : 0.5,
            child: const Text('🎁', style: TextStyle(fontSize: 40)),
          ),
          Gap.m,
          Expanded(
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                Text(
                  has
                      ? '$chests chest${chests == 1 ? '' : 's'} to open'
                      : 'No chests yet',
                  style: const TextStyle(
                    fontWeight: FontWeight.w800,
                    fontSize: 16,
                  ),
                ),
                Text(
                  has
                      ? 'Earned by meeting your daily goal.'
                      : 'Meet your daily goal to earn a chest.',
                  style: Theme.of(context).textTheme.bodySmall,
                ),
              ],
            ),
          ),
          if (has)
            FilledButton(
              onPressed: () => _openOne(context, ref),
              child: const Text('Open'),
            ),
        ],
      ),
    );
  }

  Future<void> _openOne(BuildContext context, WidgetRef ref) async {
    final reward = await ref.read(appControllerProvider.notifier).openChest();
    if (reward == null || !context.mounted) return;
    ref.read(soundServiceProvider).play(Sfx.levelUp);
    await showRewardDialog(context, reward);
  }
}

/// Shows a single reward reveal.
Future<void> showRewardDialog(BuildContext context, Reward reward) {
  final emoji = switch (reward.kind) {
    RewardKind.xp => '⚡',
    RewardKind.streakFreeze => '❄️',
    RewardKind.xpBoost => '🚀',
    RewardKind.avatar => '🧑‍🚀',
    RewardKind.item => '✨',
  };
  return showDialog<void>(
    context: context,
    builder: (context) => AlertDialog(
      content: Column(
        mainAxisSize: MainAxisSize.min,
        children: [
          Text(emoji, style: const TextStyle(fontSize: 56)),
          Gap.m,
          Text(
            reward.title,
            textAlign: TextAlign.center,
            style: const TextStyle(fontSize: 22, fontWeight: FontWeight.w900),
          ),
          Gap.s,
          Text(reward.description, textAlign: TextAlign.center),
        ],
      ),
      actions: [
        FilledButton(
          onPressed: () => Navigator.of(context).pop(),
          child: const Text('Nice!'),
        ),
      ],
    ),
  );
}

class _MiniStat extends StatelessWidget {
  const _MiniStat({
    required this.icon,
    required this.color,
    required this.value,
    required this.label,
  });

  final IconData icon;
  final Color color;
  final String value;
  final String label;

  @override
  Widget build(BuildContext context) {
    return AppCard(
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Icon(icon, color: color),
          Gap.s,
          Text(
            value,
            style: const TextStyle(fontSize: 20, fontWeight: FontWeight.w900),
          ),
          Text(label, style: Theme.of(context).textTheme.bodySmall),
        ],
      ),
    );
  }
}
