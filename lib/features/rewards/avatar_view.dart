import 'package:flutter/material.dart';

import '../../domain/models/avatar_catalog.dart';

/// Renders a single catalog asset's PNG, falling back to a rarity-tinted tile
/// when the art isn't bundled (only starter avatars ship by default; run
/// tools/sync_avatars.py --full to vendor the rest).
class AssetImage512 extends StatelessWidget {
  const AssetImage512(this.asset, {super.key, this.fit = BoxFit.contain});

  final CatalogAsset asset;
  final BoxFit fit;

  @override
  Widget build(BuildContext context) {
    return Image.asset(
      asset.previewAssetPath,
      fit: fit,
      gaplessPlayback: true,
      errorBuilder: (context, _, __) => _AssetPlaceholder(asset: asset),
    );
  }
}

/// Stacks the equipped loadout (avatar + items/pets) into a single preview.
/// Each pack PNG is a full 512×512 pre-aligned layer, so a simple z-ordered
/// stack is the correct composition.
class AvatarPreview extends StatelessWidget {
  const AvatarPreview({super.key, required this.layers, this.size = 180});

  /// Catalog assets already sorted back-to-front (see RewardsService).
  final List<CatalogAsset> layers;
  final double size;

  @override
  Widget build(BuildContext context) {
    final scheme = Theme.of(context).colorScheme;
    return Container(
      width: size,
      height: size,
      decoration: BoxDecoration(
        color: scheme.surfaceContainerHighest,
        borderRadius: BorderRadius.circular(24),
      ),
      clipBehavior: Clip.antiAlias,
      child: Stack(
        fit: StackFit.expand,
        children: [for (final layer in layers) AssetImage512(layer)],
      ),
    );
  }
}

const Map<String, Color> _rarityColors = {
  'starter': Color(0xFF8A93A6),
  'common': Color(0xFF6FB36F),
  'uncommon': Color(0xFF4FA3D1),
  'rare': Color(0xFF5B6CF6),
  'epic': Color(0xFFB05BD6),
  'legendary': Color(0xFFF4B740),
};

Color rarityColor(String rarity) =>
    _rarityColors[rarity] ?? const Color(0xFF8A93A6);

class _AssetPlaceholder extends StatelessWidget {
  const _AssetPlaceholder({required this.asset});
  final CatalogAsset asset;

  @override
  Widget build(BuildContext context) {
    final color = rarityColor(asset.rarity);
    final icon = switch (asset.type) {
      'avatar' => Icons.face_retouching_natural_rounded,
      'pet' => Icons.pets_rounded,
      _ => Icons.auto_awesome_rounded,
    };
    return Container(
      color: color.withValues(alpha: 0.18),
      alignment: Alignment.center,
      child: Icon(icon, color: color, size: 40),
    );
  }
}
