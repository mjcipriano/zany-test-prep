import 'dart:math' as math;

import 'package:flutter/material.dart';

import '../../domain/services/rewards_service.dart';
import 'avatar_view.dart';

/// Opens the equipped loadout full screen (pinch to zoom).
Future<void> showAvatarFullScreen(
  BuildContext context,
  List<EquippedLayer> layers,
) => Navigator.of(context).push(
  MaterialPageRoute<void>(
    fullscreenDialog: true,
    builder: (_) => AvatarFullScreen(layers: layers),
  ),
);

/// The avatar as large as the screen allows, with what it's wearing listed
/// underneath. Pinch or double-tap to zoom in on the details.
class AvatarFullScreen extends StatefulWidget {
  const AvatarFullScreen({super.key, required this.layers});

  final List<EquippedLayer> layers;

  @override
  State<AvatarFullScreen> createState() => _AvatarFullScreenState();
}

class _AvatarFullScreenState extends State<AvatarFullScreen> {
  final _zoom = TransformationController();

  @override
  void dispose() {
    _zoom.dispose();
    super.dispose();
  }

  void _toggleZoom(TapDownDetails d) {
    if (_zoom.value.getMaxScaleOnAxis() > 1.01) {
      _zoom.value = Matrix4.identity();
      return;
    }
    const scale = 2.5;
    final p = d.localPosition;
    _zoom.value = Matrix4.identity()
      ..translateByDouble(-p.dx * (scale - 1), -p.dy * (scale - 1), 0, 1)
      ..scaleByDouble(scale, scale, 1, 1);
  }

  @override
  Widget build(BuildContext context) {
    final avatar = widget.layers.where((l) => l.asset.isAvatar).firstOrNull;
    final worn = [
      for (final l in widget.layers)
        if (!l.asset.isAvatar) l.asset,
    ];
    return Scaffold(
      appBar: AppBar(
        title: Text(avatar?.asset.name ?? 'Your avatar'),
        leading: IconButton(
          tooltip: 'Close',
          icon: const Icon(Icons.close_rounded),
          onPressed: () => Navigator.of(context).maybePop(),
        ),
      ),
      body: SafeArea(
        child: LayoutBuilder(
          builder: (context, c) {
            // Leave room for the "wearing" chips under the avatar.
            final side = math.max(
              120.0,
              math.min(c.maxWidth - 32, c.maxHeight - 140),
            );
            return SingleChildScrollView(
              padding: const EdgeInsets.symmetric(horizontal: 16, vertical: 8),
              child: Column(
                children: [
                  GestureDetector(
                    onDoubleTapDown: _toggleZoom,
                    onDoubleTap: () {},
                    child: ClipRRect(
                      borderRadius: BorderRadius.circular(24),
                      child: InteractiveViewer(
                        key: const Key('avatar-fullscreen-zoom'),
                        transformationController: _zoom,
                        minScale: 1,
                        maxScale: 4,
                        child: AvatarPreview(
                          key: const Key('avatar-fullscreen-preview'),
                          layers: widget.layers,
                          size: side,
                        ),
                      ),
                    ),
                  ),
                  const SizedBox(height: 8),
                  Text(
                    'Pinch or double-tap to zoom',
                    style: Theme.of(context).textTheme.bodySmall,
                  ),
                  const SizedBox(height: 12),
                  if (worn.isEmpty)
                    Text(
                      'Nothing equipped yet — visit the Store for hats, '
                      'glasses, pets and more.',
                      textAlign: TextAlign.center,
                      style: Theme.of(context).textTheme.bodyMedium,
                    )
                  else
                    Wrap(
                      spacing: 8,
                      runSpacing: 8,
                      alignment: WrapAlignment.center,
                      children: [
                        for (final a in worn)
                          Chip(
                            avatar: CircleAvatar(
                              backgroundColor: rarityColor(a.rarity),
                              radius: 6,
                            ),
                            label: Text(a.name),
                          ),
                      ],
                    ),
                ],
              ),
            );
          },
        ),
      ),
    );
  }
}

/// An [AvatarPreview] that opens [AvatarFullScreen] when tapped, with a small
/// expand badge so the affordance is visible.
class TappableAvatarPreview extends StatelessWidget {
  const TappableAvatarPreview({
    super.key,
    required this.layers,
    this.size = 180,
  });

  final List<EquippedLayer> layers;
  final double size;

  @override
  Widget build(BuildContext context) {
    final scheme = Theme.of(context).colorScheme;
    return Semantics(
      button: true,
      label: 'View avatar full screen',
      child: GestureDetector(
        behavior: HitTestBehavior.opaque,
        onTap: () => showAvatarFullScreen(context, layers),
        child: Stack(
          children: [
            AvatarPreview(layers: layers, size: size),
            Positioned(
              right: 6,
              bottom: 6,
              child: Container(
                padding: EdgeInsets.all(size >= 140 ? 6 : 3),
                decoration: BoxDecoration(
                  color: scheme.surface.withValues(alpha: 0.85),
                  shape: BoxShape.circle,
                ),
                child: Icon(
                  Icons.open_in_full_rounded,
                  size: size >= 140 ? 18 : 14,
                  color: scheme.onSurface,
                ),
              ),
            ),
          ],
        ),
      ),
    );
  }
}
