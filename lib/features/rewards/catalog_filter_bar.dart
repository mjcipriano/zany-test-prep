import 'package:flutter/material.dart';

import '../../design/theme.dart';
import '../../domain/models/avatar_catalog.dart';
import '../../domain/services/catalog_filter.dart';
import 'avatar_view.dart';

/// Icon for an item category chip / section header.
IconData categoryIcon(String category) => switch (category) {
  'headwear' => Icons.school_rounded,
  'eyewear' => Icons.visibility_rounded,
  'face_accessory' => Icons.masks_rounded,
  'ear_accessory' => Icons.hearing_rounded,
  'neck_accessory' => Icons.diamond_rounded,
  'chest_badge' => Icons.military_tech_rounded,
  'back_aura' => Icons.auto_awesome_rounded,
  'background_frame' => Icons.wallpaper_rounded,
  'floating_props' => Icons.bubble_chart_rounded,
  _ => Icons.category_rounded,
};

/// Filter controls shared by the Store tabs and the avatar customizer:
///
/// 1. a scrolling row of category chips with counts ("All", "Hats", …) — or,
///    with [showSearch], a search field (pets: name or species);
/// 2. a scrolling row of rarity chips (multi-select, rarity-coloured);
/// 3. a sort menu plus the status [toggles] (Hide owned / Affordable /
///    Equipped).
///
/// Chip counts are faceted: each shows what tapping it would yield given the
/// other active filters.
class CatalogFilterBar extends StatefulWidget {
  const CatalogFilterBar({
    super.key,
    required this.assets,
    required this.filter,
    required this.onChanged,
    this.status = const CatalogStatus(),
    this.showCategories = true,
    this.showSearch = false,
    this.searchHint = 'Search',
    this.sortOptions = CatalogSort.values,
    this.toggles = const [],
    this.horizontalPadding = 20,
  });

  /// The unfiltered list (counts are computed from it).
  final List<CatalogAsset> assets;
  final CatalogFilter filter;
  final ValueChanged<CatalogFilter> onChanged;
  final CatalogStatus status;
  final bool showCategories;
  final bool showSearch;
  final String searchHint;
  final List<CatalogSort> sortOptions;
  final List<CatalogToggle> toggles;

  /// Inset of the scrolling rows, so chips scroll edge to edge on the page.
  final double horizontalPadding;

  @override
  State<CatalogFilterBar> createState() => _CatalogFilterBarState();
}

class _CatalogFilterBarState extends State<CatalogFilterBar> {
  late final TextEditingController _search = TextEditingController(
    text: widget.filter.query,
  );

  @override
  void didUpdateWidget(CatalogFilterBar old) {
    super.didUpdateWidget(old);
    // Keep the field in sync when the query is reset from outside
    // (e.g. "Clear filters").
    if (widget.filter.query != _search.text) {
      _search.text = widget.filter.query;
    }
  }

  @override
  void dispose() {
    _search.dispose();
    super.dispose();
  }

  Widget _row(List<Widget> children) => SingleChildScrollView(
    scrollDirection: Axis.horizontal,
    padding: EdgeInsets.symmetric(horizontal: widget.horizontalPadding),
    child: Row(
      children: [
        for (var i = 0; i < children.length; i++) ...[
          if (i > 0) const SizedBox(width: 8),
          children[i],
        ],
      ],
    ),
  );

  @override
  Widget build(BuildContext context) {
    final f = widget.filter;
    final rarityCounts = f.rarityCounts(widget.assets, status: widget.status);
    return Column(
      crossAxisAlignment: CrossAxisAlignment.stretch,
      mainAxisSize: MainAxisSize.min,
      children: [
        if (widget.showSearch)
          Padding(
            padding: EdgeInsets.symmetric(horizontal: widget.horizontalPadding),
            child: TextField(
              key: const ValueKey('catalog-search'),
              controller: _search,
              onChanged: (v) => widget.onChanged(f.withQuery(v)),
              textInputAction: TextInputAction.search,
              decoration: InputDecoration(
                isDense: true,
                hintText: widget.searchHint,
                prefixIcon: const Icon(Icons.search_rounded),
                suffixIcon: f.query.isEmpty
                    ? null
                    : IconButton(
                        tooltip: 'Clear search',
                        icon: const Icon(Icons.close_rounded),
                        onPressed: () => widget.onChanged(f.withQuery('')),
                      ),
                border: OutlineInputBorder(
                  borderRadius: BorderRadius.circular(14),
                ),
              ),
            ),
          ),
        if (widget.showSearch && widget.showCategories)
          const SizedBox(height: 8),
        if (widget.showCategories) _categoryRow(f),
        if (rarityCounts.length > 1) ...[
          const SizedBox(height: 8),
          _row([
            for (final e in rarityCounts.entries)
              // Skip rarities the other filters rule out (e.g. "Common 0"
              // under Hats), unless selected so it can be unticked.
              if (e.value > 0 || f.rarities.contains(e.key))
                _RarityChip(
                  rarity: e.key,
                  count: e.value,
                  selected: f.rarities.contains(e.key),
                  onTap: () => widget.onChanged(f.toggleRarity(e.key)),
                ),
          ]),
        ],
        const SizedBox(height: 8),
        _row([
          _SortMenu(
            value: f.sort,
            options: widget.sortOptions,
            onSelected: (s) => widget.onChanged(f.withSort(s)),
          ),
          for (final t in widget.toggles)
            FilterChip(
              key: ValueKey('catalog-toggle-${t.name}'),
              label: Text(t.label),
              selected: f.toggles.contains(t),
              onSelected: (_) => widget.onChanged(f.toggle(t)),
            ),
        ]),
      ],
    );
  }

  Widget _categoryRow(CatalogFilter f) {
    final counts = f.categoryCounts(widget.assets, status: widget.status);
    final total = counts.values.fold(0, (a, b) => a + b);
    return _row([
      _CategoryChip(
        key: const ValueKey('catalog-category-all'),
        icon: Icons.apps_rounded,
        label: 'All',
        count: total,
        selected: f.category == null,
        onTap: () => widget.onChanged(f.withCategory(null)),
      ),
      for (final e in counts.entries)
        _CategoryChip(
          key: ValueKey('catalog-category-${e.key}'),
          icon: categoryIcon(e.key),
          label: categoryLabel(e.key),
          count: e.value,
          selected: f.category == e.key,
          // Tapping the selected chip again goes back to "All".
          onTap: () => widget.onChanged(
            f.withCategory(f.category == e.key ? null : e.key),
          ),
        ),
    ]);
  }
}

class _CountLabel extends StatelessWidget {
  const _CountLabel({required this.label, required this.count});
  final String label;
  final int count;

  @override
  Widget build(BuildContext context) => Row(
    mainAxisSize: MainAxisSize.min,
    children: [
      Text(label),
      const SizedBox(width: 6),
      Text(
        '$count',
        style: TextStyle(
          fontSize: 12,
          fontWeight: FontWeight.w700,
          color: Theme.of(context).colorScheme.onSurfaceVariant,
        ),
      ),
    ],
  );
}

class _CategoryChip extends StatelessWidget {
  const _CategoryChip({
    super.key,
    required this.icon,
    required this.label,
    required this.count,
    required this.selected,
    required this.onTap,
  });

  final IconData icon;
  final String label;
  final int count;
  final bool selected;
  final VoidCallback onTap;

  @override
  Widget build(BuildContext context) => ChoiceChip(
    avatar: Icon(icon, size: 18),
    showCheckmark: false,
    label: _CountLabel(label: label, count: count),
    selected: selected,
    onSelected: (_) => onTap(),
  );
}

class _RarityChip extends StatelessWidget {
  const _RarityChip({
    required this.rarity,
    required this.count,
    required this.selected,
    required this.onTap,
  });

  final String rarity;
  final int count;
  final bool selected;
  final VoidCallback onTap;

  @override
  Widget build(BuildContext context) {
    final color = rarityColor(rarity);
    return FilterChip(
      key: ValueKey('catalog-rarity-$rarity'),
      avatar: selected
          ? null
          : Container(
              width: 10,
              height: 10,
              decoration: BoxDecoration(color: color, shape: BoxShape.circle),
            ),
      label: _CountLabel(label: rarityLabel(rarity), count: count),
      selected: selected,
      checkmarkColor: AppColors.of(context).textOn(color, minRatio: 3),
      selectedColor: color.withValues(alpha: 0.22),
      side: BorderSide(color: color.withValues(alpha: selected ? 1 : 0.5)),
      onSelected: (_) => onTap(),
    );
  }
}

class _SortMenu extends StatelessWidget {
  const _SortMenu({
    required this.value,
    required this.options,
    required this.onSelected,
  });

  final CatalogSort value;
  final List<CatalogSort> options;
  final ValueChanged<CatalogSort> onSelected;

  @override
  Widget build(BuildContext context) => PopupMenuButton<CatalogSort>(
    key: const ValueKey('catalog-sort'),
    tooltip: 'Sort',
    initialValue: value,
    onSelected: onSelected,
    itemBuilder: (context) => [
      for (final s in options)
        CheckedPopupMenuItem(
          value: s,
          checked: s == value,
          child: Text(s.label),
        ),
    ],
    child: Chip(
      avatar: const Icon(Icons.sort_rounded, size: 18),
      label: Text(value.shortLabel),
    ),
  );
}

/// "Showing 12 of 376" above a filtered list, with a Clear action while any
/// filter is active.
class CatalogResultsLine extends StatelessWidget {
  const CatalogResultsLine({
    super.key,
    required this.shown,
    required this.total,
    required this.noun,
    required this.filtered,
    required this.onClear,
  });

  final int shown;
  final int total;

  /// Plural noun for the unfiltered count ("items", "pets").
  final String noun;
  final bool filtered;
  final VoidCallback onClear;

  @override
  Widget build(BuildContext context) => SizedBox(
    height: 40,
    child: Row(
      children: [
        Expanded(
          child: Text(
            filtered ? 'Showing $shown of $total' : '$total $noun',
            key: const ValueKey('catalog-result-count'),
            style: Theme.of(
              context,
            ).textTheme.bodySmall?.copyWith(fontWeight: FontWeight.w700),
          ),
        ),
        if (filtered)
          TextButton.icon(
            key: const ValueKey('catalog-clear'),
            onPressed: onClear,
            icon: const Icon(Icons.filter_alt_off_rounded, size: 18),
            label: const Text('Clear'),
          ),
      ],
    ),
  );
}

/// Shown when no asset passes the filters.
class CatalogEmptyState extends StatelessWidget {
  const CatalogEmptyState({
    super.key,
    required this.noun,
    required this.onClear,
  });

  final String noun;
  final VoidCallback onClear;

  @override
  Widget build(BuildContext context) {
    final scheme = Theme.of(context).colorScheme;
    return Padding(
      padding: const EdgeInsets.symmetric(vertical: 32),
      child: Column(
        mainAxisSize: MainAxisSize.min,
        children: [
          Icon(Icons.search_off_rounded, size: 48, color: scheme.outline),
          const SizedBox(height: 8),
          Text(
            'No $noun match these filters',
            textAlign: TextAlign.center,
            style: Theme.of(context).textTheme.titleMedium,
          ),
          const SizedBox(height: 12),
          // Bounded width: the themed default button is full-width.
          OutlinedButton.icon(
            style: OutlinedButton.styleFrom(minimumSize: const Size(160, 44)),
            onPressed: onClear,
            icon: const Icon(Icons.filter_alt_off_rounded),
            label: const Text('Clear filters'),
          ),
        ],
      ),
    );
  }
}
