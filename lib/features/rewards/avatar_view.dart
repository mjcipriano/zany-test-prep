import 'package:flutter/material.dart';

import '../../domain/models/avatar_catalog.dart';
import '../../domain/services/rewards_service.dart';

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

/// Composes the equipped loadout (avatar + items/pets) into a single preview.
///
/// Each PNG is a 512×512 canvas with its art centered, so layers are *positioned*
/// rather than naively stacked: the avatar fills the frame; worn items are placed
/// so their centered art lands on the asset's [anchor] (scaled by `scale`); side
/// pets/props go into one of the four fixed side positions for their slot.
class AvatarPreview extends StatelessWidget {
  const AvatarPreview({super.key, required this.layers, this.size = 180});

  /// Layers already sorted back-to-front (see RewardsService.equippedLayers).
  final List<EquippedLayer> layers;
  final double size;

  // Fixed positions (fraction of the frame) for the four side slots, matching
  // the pack's integration reference.
  static const Map<String, Offset> _sideSlots = {
    'side_left_1': Offset(0.22, 0.48),
    'side_left_2': Offset(0.24, 0.74),
    'side_right_1': Offset(0.78, 0.48),
    'side_right_2': Offset(0.76, 0.74),
  };

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
        clipBehavior: Clip.hardEdge,
        children: [for (final layer in layers) _positioned(layer)],
      ),
    );
  }

  Widget _positioned(EquippedLayer layer) {
    final a = layer.asset;
    // The avatar (and any unexpected base layer) fills the whole frame.
    if (a.isAvatar) return Positioned.fill(child: AssetImage512(a));

    // Where the layer's (centered) art should land, as a fraction of the frame.
    final Offset center = a.isSide
        ? (_sideSlots[layer.slot] ?? Offset(a.anchorX / 512, a.anchorY / 512))
        : Offset(a.anchorX / 512, a.anchorY / 512);
    final dim = size * a.scale;
    return Positioned(
      left: center.dx * size - dim / 2,
      top: center.dy * size - dim / 2,
      width: dim,
      height: dim,
      child: AssetImage512(a),
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
