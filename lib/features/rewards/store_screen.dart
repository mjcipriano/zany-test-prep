import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';

import '../../app/app_controller.dart';
import '../../core/sound_service.dart';
import '../../design/theme.dart';
import '../../design/widgets.dart';
import '../../domain/models/avatar_catalog.dart';
import '../../domain/models/progress.dart';
import '../../domain/services/rewards_service.dart';
import 'avatar_view.dart';

/// Spend XP on avatars, items, pets, and streak freezes.
class StoreScreen extends ConsumerWidget {
  const StoreScreen({super.key});

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    final data = ref.watch(appControllerProvider).valueOrNull;
    if (data == null) {
      return const Scaffold(body: Center(child: CircularProgressIndicator()));
    }
    final catalog = data.catalog;

    return DefaultTabController(
      length: 3,
      child: Scaffold(
        appBar: AppBar(
          title: const Text('Store'),
          actions: [
            Center(child: _XpChip(xp: data.progress.game.availableXp)),
            Gap.m,
          ],
          bottom: const TabBar(
            tabs: [
              Tab(text: 'Avatars'),
              Tab(text: 'Items'),
              Tab(text: 'Pets'),
            ],
          ),
        ),
        body: TabBarView(
          children: [
            _StoreGrid(assets: _sorted(catalog.avatars)),
            _StoreGrid(
              assets: _sorted(catalog.items),
              header: const _StreakFreezeCard(),
            ),
            _StoreGrid(assets: _sorted(catalog.pets)),
          ],
        ),
      ),
    );
  }

  static List<CatalogAsset> _sorted(List<CatalogAsset> a) =>
      [...a]..sort((x, y) => x.xpCost.compareTo(y.xpCost));
}

class _XpChip extends StatelessWidget {
  const _XpChip({required this.xp});
  final int xp;
  @override
  Widget build(BuildContext context) =>
      StatPill(icon: Icons.bolt_rounded, value: '$xp', color: AppTheme.xpGold);
}

class _StoreGrid extends ConsumerWidget {
  const _StoreGrid({required this.assets, this.header});
  final List<CatalogAsset> assets;
  final Widget? header;

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    final data = ref.watch(appControllerProvider).valueOrNull!;
    final rewards = ref.read(rewardsServiceProvider);
    final g = data.progress.game;

    return ListView(
      padding: kPagePadding,
      children: [
        if (header != null) ...[header!, Gap.m],
        GridView.builder(
          shrinkWrap: true,
          physics: const NeverScrollableScrollPhysics(),
          gridDelegate: const SliverGridDelegateWithMaxCrossAxisExtent(
            maxCrossAxisExtent: 200,
            mainAxisSpacing: 12,
            crossAxisSpacing: 12,
            childAspectRatio: 0.74,
          ),
          itemCount: assets.length,
          itemBuilder: (context, i) {
            final asset = assets[i];
            return _StoreTile(
              asset: asset,
              owned: rewards.isOwned(g, asset),
              affordable: rewards.canAfford(g, asset.xpCost),
            );
          },
        ),
      ],
    );
  }
}

class _StoreTile extends ConsumerWidget {
  const _StoreTile({
    required this.asset,
    required this.owned,
    required this.affordable,
  });

  final CatalogAsset asset;
  final bool owned;
  final bool affordable;

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    final color = rarityColor(asset.rarity);
    return AppCard(
      padding: const EdgeInsets.all(10),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.stretch,
        children: [
          Expanded(
            child: ClipRRect(
              borderRadius: BorderRadius.circular(12),
              child: AssetImage512(asset),
            ),
          ),
          Gap.s,
          Text(
            asset.name,
            maxLines: 1,
            overflow: TextOverflow.ellipsis,
            style: const TextStyle(fontWeight: FontWeight.w700, fontSize: 13),
          ),
          Text(
            asset.rarity,
            style: TextStyle(
              color: color,
              fontSize: 11,
              fontWeight: FontWeight.w700,
            ),
          ),
          Gap.xs,
          if (owned)
            const _OwnedChip()
          else
            FilledButton(
              onPressed: affordable ? () => _buy(context, ref) : null,
              style: FilledButton.styleFrom(
                padding: const EdgeInsets.symmetric(vertical: 6),
                minimumSize: const Size.fromHeight(34),
              ),
              child: Row(
                mainAxisAlignment: MainAxisAlignment.center,
                children: [
                  const Icon(Icons.bolt_rounded, size: 16),
                  Text('${asset.xpCost}'),
                ],
              ),
            ),
        ],
      ),
    );
  }

  Future<void> _buy(BuildContext context, WidgetRef ref) async {
    final ok = await ref
        .read(appControllerProvider.notifier)
        .purchaseAsset(asset.id);
    if (!context.mounted) return;
    if (ok) {
      ref.read(soundServiceProvider).play(Sfx.levelUp);
      ScaffoldMessenger.of(
        context,
      ).showSnackBar(SnackBar(content: Text('Unlocked ${asset.name}!')));
    }
  }
}

class _OwnedChip extends StatelessWidget {
  const _OwnedChip();
  @override
  Widget build(BuildContext context) {
    return Container(
      height: 34,
      alignment: Alignment.center,
      decoration: BoxDecoration(
        color: AppTheme.correct.withValues(alpha: 0.16),
        borderRadius: BorderRadius.circular(10),
      ),
      child: const Row(
        mainAxisAlignment: MainAxisAlignment.center,
        children: [
          Icon(Icons.check_rounded, size: 16, color: AppTheme.correct),
          SizedBox(width: 4),
          Text(
            'Owned',
            style: TextStyle(
              color: AppTheme.correct,
              fontWeight: FontWeight.w700,
            ),
          ),
        ],
      ),
    );
  }
}

class _StreakFreezeCard extends ConsumerWidget {
  const _StreakFreezeCard();

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    final data = ref.watch(appControllerProvider).valueOrNull!;
    final g = data.progress.game;
    final maxed = g.streakFreezes >= kMaxStreakFreezes;
    final affordable = g.availableXp >= RewardsService.streakFreezeCost;

    const freezeBlue = Color(0xFF4FA3D1);
    return AppCard(
      color: freezeBlue.withValues(alpha: 0.14),
      child: Row(
        children: [
          Container(
            width: 52,
            height: 52,
            decoration: const BoxDecoration(
              color: freezeBlue,
              shape: BoxShape.circle,
            ),
            alignment: Alignment.center,
            child: const Icon(
              Icons.ac_unit_rounded,
              color: Colors.white,
              size: 28,
            ),
          ),
          Gap.m,
          Expanded(
            child: Column(
              mainAxisSize: MainAxisSize.min,
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                const Text(
                  'Streak Freeze',
                  style: TextStyle(fontWeight: FontWeight.w800, fontSize: 16),
                ),
                Text(
                  maxed
                      ? 'Banked ${g.streakFreezes}/$kMaxStreakFreezes — full'
                      : 'Banked ${g.streakFreezes}/$kMaxStreakFreezes · protects your streak',
                  style: Theme.of(context).textTheme.bodySmall,
                ),
              ],
            ),
          ),
          Gap.s,
          FilledButton(
            // Bounded width: the themed default is full-width, which is invalid
            // as a non-flex child of a Row.
            style: FilledButton.styleFrom(minimumSize: const Size(64, 44)),
            onPressed: (maxed || !affordable) ? null : () => _buy(context, ref),
            child: const Row(
              mainAxisSize: MainAxisSize.min,
              children: [
                Icon(Icons.bolt_rounded, size: 16),
                SizedBox(width: 2),
                Text('${RewardsService.streakFreezeCost}'),
              ],
            ),
          ),
        ],
      ),
    );
  }

  Future<void> _buy(BuildContext context, WidgetRef ref) async {
    final ok = await ref
        .read(appControllerProvider.notifier)
        .purchaseStreakFreeze();
    if (!context.mounted) return;
    if (ok) {
      ref.read(soundServiceProvider).play(Sfx.levelUp);
      ScaffoldMessenger.of(
        context,
      ).showSnackBar(const SnackBar(content: Text('Streak freeze added!')));
    }
  }
}
