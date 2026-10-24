import 'dart:io' show Platform;
import 'dart:math' as math;

import 'package:flutter/foundation.dart' show kIsWeb;
import 'package:flutter/material.dart';

import '../../domain/models/avatar_catalog.dart';
import '../../domain/services/rewards_service.dart';

/// Whether avatar previews may run idle animations. Off under `flutter test`
/// (a repeating animation never lets `pumpAndSettle` settle) unless a test
/// opts in via [AvatarPreview.animate].
bool get kAvatarAnimationsEnabled =>
    kIsWeb || !Platform.environment.containsKey('FLUTTER_TEST');

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
      // Sprites are vendored at a fixed size and drawn scaled; high-quality
      // sampling keeps outlines crisp at every preview size.
      filterQuality: FilterQuality.high,
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

/// Normalised y of the brow line that headwear rests on. Hats are
/// bottom-aligned here instead of centred in their box: a cap, a crown and a
/// tall wizard hat then all sit on the head at the same height, whereas
/// centring left short sprites floating above the hair.
const double kHeadwearBrimLine = 0.245;

/// The exact rectangle a sprite is drawn into: its target box shrunk to the
/// sprite's aspect ratio (contain-fit), with headwear bottom-aligned on the
/// [kHeadwearBrimLine] unless it is meant to float. Falls back to the box when
/// the pack records no sprite size.
Rect fittedRect(CatalogAsset asset, String? slot, double size) {
  final box = placementRect(asset, slot, size);
  final aspect = asset.spriteAspect;
  var r = box;
  if (aspect != null && aspect > 0) {
    final scale = math.min(box.width / aspect, box.height); // fitted height
    final h = scale, w = scale * aspect;
    r = Rect.fromCenter(center: box.center, width: w, height: h);
  }
  if (asset.category == 'headwear' && !asset.isSide && !asset.floatsAboveHead) {
    r = Rect.fromLTWH(
      r.left,
      kHeadwearBrimLine * size - r.height,
      r.width,
      r.height,
    );
  }
  return r;
}

/// Composes the equipped loadout (avatar + items/pets) into a single preview.
///
/// PNGs are tightly trimmed sprites, so each layer is *placed* into its target
/// box (see [placementRect]): the avatar fills the frame; worn items land on the
/// right body region sized to fit; side pets/props go into the side slot they're
/// equipped in. Layers are drawn back-to-front by z-index (negative z, e.g. a
/// background frame, sits behind the avatar). Side companions get a soft
/// drop shadow, a rarity glow for epic/legendary/evolved pets, and — when
/// [animate] is on — a gentle idle float so they feel alive.
class AvatarPreview extends StatefulWidget {
  const AvatarPreview({
    super.key,
    required this.layers,
    this.size = 180,
    bool? animate,
  }) : _animate = animate;

  /// Layers already sorted back-to-front (see RewardsService.equippedLayers).
  final List<EquippedLayer> layers;
  final double size;
  final bool? _animate;

  bool get animate => _animate ?? kAvatarAnimationsEnabled;

  @override
  State<AvatarPreview> createState() => _AvatarPreviewState();
}

class _AvatarPreviewState extends State<AvatarPreview>
    with SingleTickerProviderStateMixin {
  AnimationController? _idle;

  @override
  void initState() {
    super.initState();
    _syncAnimation();
  }

  @override
  void didUpdateWidget(covariant AvatarPreview oldWidget) {
    super.didUpdateWidget(oldWidget);
    if (oldWidget.animate != widget.animate) _syncAnimation();
  }

  void _syncAnimation() {
    if (widget.animate) {
      _idle ??= AnimationController(
        vsync: this,
        duration: const Duration(milliseconds: 2600),
      )..repeat();
    } else {
      _idle?.dispose();
      _idle = null;
    }
  }

  @override
  void dispose() {
    _idle?.dispose();
    super.dispose();
  }

  @override
  Widget build(BuildContext context) {
    final scheme = Theme.of(context).colorScheme;
    final size = widget.size;
    final frame = Container(
      width: size,
      height: size,
      decoration: BoxDecoration(
        color: scheme.surfaceContainerHighest,
        borderRadius: BorderRadius.circular(24),
      ),
      clipBehavior: Clip.antiAlias,
      child: Stack(
        clipBehavior: Clip.hardEdge,
        children: [for (final layer in widget.layers) _positioned(layer)],
      ),
    );
    final idle = _idle;
    if (idle == null) return frame;
    return AnimatedBuilder(animation: idle, builder: (_, __) => frame);
  }

  Widget _positioned(EquippedLayer layer) {
    final a = layer.asset;
    final size = widget.size;
    // The avatar (and any base layer) fills the whole frame.
    if (a.isAvatar) return Positioned.fill(child: AssetImage512(a));
    final r = fittedRect(a, layer.slot, size);
    if (!a.isSide) {
      return Positioned.fromRect(rect: r, child: AssetImage512(a));
    }
    // Side companions: float offset (per-slot phase so they don't move in
    // lockstep), shadow underneath, rarity glow behind.
    final t = _idle?.value ?? 0;
    final phase = (layer.slot?.hashCode ?? 0) % 7 / 7.0;
    final dy = _idle == null
        ? 0.0
        : math.sin((t + phase) * 2 * math.pi) * size * 0.012;
    final glow = companionGlowColor(a);
    return Positioned.fromRect(
      rect: r.shift(Offset(0, dy)),
      child: SideCompanionLayer(asset: a, glow: glow),
    );
  }
}

/// Glow tint for a side companion, or null for ordinary ones. Epic/legendary
/// and evolved pets shine so upgrades are visible at a glance.
Color? companionGlowColor(CatalogAsset a) {
  if (!a.isPet) return null;
  final stage = a.evolution?.stage ?? 1;
  if (stage >= 3) return const Color(0xFFFFE58A);
  if (stage == 2) return const Color(0xFFB7E3FF);
  return switch (a.rarity) {
    'legendary' => const Color(0xFFF4B740),
    'epic' => const Color(0xFFB05BD6),
    _ => null,
  };
}

/// A side pet/prop with its drop shadow and optional glow. Kept as a widget
/// so render tests can pump it directly.
class SideCompanionLayer extends StatelessWidget {
  const SideCompanionLayer({super.key, required this.asset, this.glow});

  final CatalogAsset asset;
  final Color? glow;

  @override
  Widget build(BuildContext context) {
    return LayoutBuilder(
      builder: (context, c) {
        final w = c.maxWidth, h = c.maxHeight;
        return Stack(
          clipBehavior: Clip.none,
          children: [
            if (glow != null)
              Positioned.fill(
                child: DecoratedBox(
                  decoration: BoxDecoration(
                    gradient: RadialGradient(
                      colors: [
                        glow!.withValues(alpha: 0.45),
                        glow!.withValues(alpha: 0.0),
                      ],
                      stops: const [0.35, 1.0],
                    ),
                  ),
                ),
              ),
            // Soft contact shadow under the sprite.
            Positioned(
              left: w * 0.18,
              right: w * 0.18,
              bottom: -h * 0.02,
              height: h * 0.12,
              child: DecoratedBox(
                decoration: BoxDecoration(
                  borderRadius: BorderRadius.all(
                    Radius.elliptical(w, h * 0.12),
                  ),
                  gradient: RadialGradient(
                    colors: [
                      Colors.black.withValues(alpha: 0.22),
                      Colors.black.withValues(alpha: 0.0),
                    ],
                  ),
                ),
              ),
            ),
            Positioned.fill(child: AssetImage512(asset)),
          ],
        );
      },
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
