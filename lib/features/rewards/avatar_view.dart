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

/// Computes where a layer's trimmed sprite should be drawn within a [size]×[size]
/// frame, per the pack's `target_box_v1` contract: pick the per-slot target
/// (falling back to the asset's default), center it at `cx,cy`, and bound it to
/// `w,h` (× optional `scale`). The image itself is fit with `contain`.
/// Pure + exported so render tests can assert exact placement.
Rect placementRect(CatalogAsset asset, String? slot, double size) {
  final t = asset.targetForSlot(slot);
  final w = t.w * size * asset.scale;
  final h = t.h * size * asset.scale;
  return Rect.fromLTWH(t.cx * size - w / 2, t.cy * size - h / 2, w, h);
}

/// Composes the equipped loadout (avatar + items/pets) into a single preview.
///
/// PNGs are tightly trimmed sprites, so each layer is *placed* into its target
/// box (see [placementRect]): the avatar fills the frame; worn items land on the
/// right body region sized to fit; side pets/props go into the side slot they're
/// equipped in. Layers are drawn back-to-front by z-index (negative z, e.g. a
/// background frame, sits behind the avatar).
class AvatarPreview extends StatelessWidget {
  const AvatarPreview({super.key, required this.layers, this.size = 180});

  /// Layers already sorted back-to-front (see RewardsService.equippedLayers).
  final List<EquippedLayer> layers;
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
        clipBehavior: Clip.hardEdge,
        children: [for (final layer in layers) _positioned(layer)],
      ),
    );
  }

  Widget _positioned(EquippedLayer layer) {
    final a = layer.asset;
    // The avatar (and any base layer) fills the whole frame.
    if (a.isAvatar) return Positioned.fill(child: AssetImage512(a));
    final r = placementRect(a, layer.slot, size);
    return Positioned(
      left: r.left,
      top: r.top,
      width: r.width,
      height: r.height,
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
