import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:go_router/go_router.dart';

import '../../app/app_controller.dart';
import '../../core/sound_service.dart';
import '../../design/theme.dart';
import '../../design/widgets.dart';
import '../../domain/models/avatar_catalog.dart';
import 'avatar_view.dart';

/// Customize the player's avatar: pick an owned avatar and equip owned
/// items/pets. Locked content is bought in the Store.
class AvatarScreen extends ConsumerWidget {
  const AvatarScreen({super.key});

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    final data = ref.watch(appControllerProvider).valueOrNull;
    if (data == null) {
      return const Scaffold(body: Center(child: CircularProgressIndicator()));
    }
    final catalog = data.catalog;
    final rewards = ref.read(rewardsServiceProvider);
    final g = data.progress.game;

    final ownedAvatars = catalog.avatars
        .where((a) => rewards.isOwned(g, a))
        .toList();
    final ownedItems = [
      ...catalog.items.where((a) => rewards.isOwned(g, a)),
      ...catalog.pets.where((a) => rewards.isOwned(g, a)),
    ];
    final selectedId = rewards.selectedAvatar(g, catalog).id;

    return Scaffold(
      appBar: AppBar(
        title: const Text('Customize avatar'),
        actions: [
          TextButton.icon(
            onPressed: () => context.push('/store'),
            icon: const Icon(Icons.storefront_rounded),
            label: const Text('Store'),
          ),
        ],
      ),
      body: ListView(
        padding: kPagePadding,
        children: [
          Center(
            child: AvatarPreview(
              layers: rewards.equippedLayers(g, catalog),
              size: 200,
            ),
          ),
          Gap.l,
          const SectionLabel('Your avatars'),
          GridView.builder(
            shrinkWrap: true,
            physics: const NeverScrollableScrollPhysics(),
            gridDelegate: const SliverGridDelegateWithMaxCrossAxisExtent(
              maxCrossAxisExtent: 120,
              mainAxisSpacing: 12,
              crossAxisSpacing: 12,
              childAspectRatio: 1,
            ),
            itemCount: ownedAvatars.length,
            itemBuilder: (context, i) {
              final a = ownedAvatars[i];
              return _PickTile(
                asset: a,
                selected: a.id == selectedId,
                onTap: () async {
                  await ref
                      .read(appControllerProvider.notifier)
                      .selectAvatar(a.id);
                  ref.read(soundServiceProvider).play(Sfx.select);
                },
              );
            },
          ),
          Gap.l,
          const SectionLabel('Your items'),
          if (ownedItems.isEmpty)
            AppCard(
              child: Row(
                children: [
                  Icon(
                    Icons.auto_awesome_rounded,
                    color: Theme.of(context).colorScheme.primary,
                  ),
                  Gap.m,
                  const Expanded(
                    child: Text(
                      'No items yet. Earn them from chests or buy them in the '
                      'Store, then equip them here.',
                    ),
                  ),
                ],
              ),
            )
          else
            ...ownedItems.map(
              (item) => _ItemRow(
                item: item,
                equippedSlot: rewards.equippedSlotOf(g, item.id),
              ),
            ),
        ],
      ),
    );
  }
}

class _PickTile extends StatelessWidget {
  const _PickTile({
    required this.asset,
    required this.selected,
    required this.onTap,
  });

  final CatalogAsset asset;
  final bool selected;
  final VoidCallback onTap;

  @override
  Widget build(BuildContext context) {
    final scheme = Theme.of(context).colorScheme;
    return GestureDetector(
      onTap: onTap,
      child: Container(
        decoration: BoxDecoration(
          borderRadius: BorderRadius.circular(16),
          border: Border.all(
            color: selected ? scheme.primary : Colors.transparent,
            width: 3,
          ),
        ),
        clipBehavior: Clip.antiAlias,
        child: AssetImage512(asset),
      ),
    );
  }
}

/// Human-readable label for a side slot (the four floating positions).
String _slotLabel(String slot) => switch (slot) {
  'side_left_1' => 'Left · top',
  'side_left_2' => 'Left · bottom',
  'side_right_1' => 'Right · top',
  'side_right_2' => 'Right · bottom',
  _ => slot.replaceAll('_', ' '),
};

class _ItemRow extends ConsumerWidget {
  const _ItemRow({required this.item, required this.equippedSlot});
  final CatalogAsset item;
  final String? equippedSlot;

  bool get _equipped => equippedSlot != null;

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    final controller = ref.read(appControllerProvider.notifier);
    // For an equipped side asset, show its current position; otherwise the
    // category (e.g. "headwear", "floating props").
    final subtitle = _equipped && item.isSide
        ? _slotLabel(equippedSlot!)
        : item.category.replaceAll('_', ' ');
    return Padding(
      padding: const EdgeInsets.only(bottom: 8),
      child: AppCard(
        child: Row(
          children: [
            SizedBox(
              width: 48,
              height: 48,
              child: ClipRRect(
                borderRadius: BorderRadius.circular(10),
                child: AssetImage512(item),
              ),
            ),
            Gap.m,
            Expanded(
              child: Column(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  Text(
                    item.name,
                    style: const TextStyle(fontWeight: FontWeight.w700),
                  ),
                  Text(subtitle, style: Theme.of(context).textTheme.bodySmall),
                ],
              ),
            ),
            // Side assets get a "move" control to cycle through the 4 slots.
            if (_equipped && item.isSide)
              IconButton(
                tooltip: 'Move to next slot',
                onPressed: () => controller.cycleSideSlot(item.id),
                icon: const Icon(Icons.open_with_rounded),
              ),
            if (_equipped)
              OutlinedButton(
                // Bounded width: the themed default is full-width, invalid as a
                // non-flex child of a Row.
                style: OutlinedButton.styleFrom(
                  minimumSize: const Size(88, 40),
                ),
                onPressed: () => controller.unequipAsset(item.id),
                child: const Text('Remove'),
              )
            else
              FilledButton.tonal(
                style: FilledButton.styleFrom(minimumSize: const Size(88, 40)),
                onPressed: () => controller.equipItem(item.id),
                child: const Text('Equip'),
              ),
          ],
        ),
      ),
    );
  }
}
