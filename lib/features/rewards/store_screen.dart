import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';

import '../../app/app_controller.dart';
import '../../core/sound_service.dart';
import '../../design/theme.dart';
import '../../design/widgets.dart';
import '../../domain/models/avatar_catalog.dart';
import '../../domain/models/progress.dart';
import '../../domain/services/catalog_filter.dart';
import '../../domain/services/rewards_service.dart';
import 'avatar_view.dart';
import 'catalog_filter_bar.dart';

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
            _StoreGrid(assets: catalog.avatars, noun: 'avatars'),
            _StoreGrid(
              assets: catalog.items,
              noun: 'items',
              header: const _StreakFreezeCard(),
              mode: _FilterMode.items,
            ),
            _StoreGrid(
              assets: catalog.basePets,
              noun: 'pets',
              header: const _PetHint(),
              mode: _FilterMode.pets,
            ),
          ],
        ),
      ),
    );
  }
}

class _PetHint extends StatelessWidget {
  const _PetHint();
  @override
  Widget build(BuildContext context) => AppCard(
    color: const Color(0xFF8E44AD).withValues(alpha: 0.12),
    child: Row(
      children: [
        const Icon(Icons.pets_rounded, color: Color(0xFF8E44AD)),
        Gap.m,
        Expanded(
          child: Text(
            'Equip a companion and it earns pet XP while you practice. Level it '
            'up to evolve it into Shiny and Radiant forms.',
            style: Theme.of(context).textTheme.bodySmall,
          ),
        ),
      ],
    ),
  );
}

class _XpChip extends StatelessWidget {
  const _XpChip({required this.xp});
  final int xp;
  @override
  Widget build(BuildContext context) =>
      StatPill(icon: Icons.bolt_rounded, value: '$xp', color: AppTheme.xpGold);
}

/// Which filter controls a store tab shows.
enum _FilterMode {
  /// No filter bar (the avatars tab): just sorted by price.
  none,

  /// Category chips, rarity chips, sort, Hide owned / Affordable; the "All"
  /// view is grouped into category sections.
  items,

  /// Name/species search, rarity chips, sort, Hide owned / Affordable.
  pets,
}

class _StoreGrid extends ConsumerStatefulWidget {
  const _StoreGrid({
    required this.assets,
    required this.noun,
    this.header,
    this.mode = _FilterMode.none,
  });

  final List<CatalogAsset> assets;

  /// Plural noun for counts and the empty state ("items", "pets").
  final String noun;
  final Widget? header;
  final _FilterMode mode;

  @override
  ConsumerState<_StoreGrid> createState() => _StoreGridState();
}

class _StoreGridState extends ConsumerState<_StoreGrid>
    with AutomaticKeepAliveClientMixin {
  CatalogFilter _filter = const CatalogFilter();

  // Keep each tab's filters (and scroll position) when switching tabs.
  @override
  bool get wantKeepAlive => true;

  static const _gridDelegate = SliverGridDelegateWithMaxCrossAxisExtent(
    maxCrossAxisExtent: 200,
    mainAxisSpacing: 12,
    crossAxisSpacing: 12,
    childAspectRatio: 0.74,
  );

  void _set(CatalogFilter f) => setState(() => _filter = f);

  @override
  Widget build(BuildContext context) {
    super.build(context);
    final data = ref.watch(appControllerProvider).valueOrNull!;
    final rewards = ref.read(rewardsServiceProvider);
    final g = data.progress.game;
    final status = CatalogStatus(
      isOwned: (a) => rewards.isOwned(g, a),
      canAfford: (a) => rewards.canAfford(g, a.xpCost),
    );
    final filtering = widget.mode != _FilterMode.none;
    final filter = filtering ? _filter : const CatalogFilter();
    final shown = filter.apply(widget.assets, status: status);
    final grouped = widget.mode == _FilterMode.items && filter.category == null;

    Widget grid(List<CatalogAsset> assets) => SliverPadding(
      padding: const EdgeInsets.symmetric(horizontal: 20),
      sliver: SliverGrid.builder(
        gridDelegate: _gridDelegate,
        itemCount: assets.length,
        itemBuilder: (context, i) {
          final asset = assets[i];
          return _StoreTile(
            key: ValueKey('store-tile-${asset.id}'),
            asset: asset,
            owned: rewards.isOwned(g, asset),
            affordable: rewards.canAfford(g, asset.xpCost),
          );
        },
      ),
    );

    return CustomScrollView(
      slivers: [
        if (widget.header != null)
          SliverPadding(
            padding: const EdgeInsets.fromLTRB(20, 20, 20, 0),
            sliver: SliverToBoxAdapter(child: widget.header),
          ),
        SliverToBoxAdapter(
          child: SizedBox(height: widget.header == null ? 20 : 16),
        ),
        if (filtering) ...[
          SliverToBoxAdapter(
            child: CatalogFilterBar(
              assets: widget.assets,
              filter: _filter,
              onChanged: _set,
              status: status,
              showCategories: widget.mode == _FilterMode.items,
              showSearch: widget.mode == _FilterMode.pets,
              searchHint: 'Search pets — fox, cat, dragon…',
              toggles: const [
                CatalogToggle.hideOwned,
                CatalogToggle.affordableOnly,
              ],
            ),
          ),
          SliverPadding(
            padding: const EdgeInsets.symmetric(horizontal: 20),
            sliver: SliverToBoxAdapter(
              child: CatalogResultsLine(
                shown: shown.length,
                total: widget.assets.length,
                noun: widget.noun,
                filtered: _filter.hasActiveFilters,
                onClear: () => _set(_filter.cleared()),
              ),
            ),
          ),
        ],
        if (shown.isEmpty && filtering)
          SliverToBoxAdapter(
            child: CatalogEmptyState(
              noun: widget.noun,
              onClear: () => _set(_filter.cleared()),
            ),
          )
        else if (grouped)
          for (final section in groupByCategory(shown)) ...[
            SliverPadding(
              padding: const EdgeInsets.fromLTRB(20, 8, 20, 0),
              sliver: SliverToBoxAdapter(
                child: _SectionHeader(
                  category: section.key,
                  count: section.value.length,
                ),
              ),
            ),
            grid(section.value),
          ]
        else
          grid(shown),
        const SliverToBoxAdapter(child: SizedBox(height: 20)),
      ],
    );
  }
}

/// "🎓 HATS · 12" above a category section of the items grid.
class _SectionHeader extends StatelessWidget {
  const _SectionHeader({required this.category, required this.count});
  final String category;
  final int count;

  @override
  Widget build(BuildContext context) {
    final muted = Theme.of(context).colorScheme.onSurfaceVariant;
    return Padding(
      padding: const EdgeInsets.only(bottom: 4),
      child: Row(
        children: [
          Icon(categoryIcon(category), size: 18, color: muted),
          const SizedBox(width: 8),
          Expanded(
            child: SectionLabel(
              categoryLabel(category),
              trailing: Text(
                '$count',
                style: TextStyle(color: muted, fontWeight: FontWeight.w700),
              ),
            ),
          ),
        ],
      ),
    );
  }
}

class _StoreTile extends ConsumerWidget {
  const _StoreTile({
    super.key,
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
