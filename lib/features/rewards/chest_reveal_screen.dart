import 'dart:math';

import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:go_router/go_router.dart';

import '../../app/app_controller.dart';
import '../../core/sound_service.dart';
import '../../design/theme.dart';
import '../../domain/models/reward.dart';

/// Full-screen animated chest opening: tap the chest, watch it shake and burst,
/// then the reward springs in. Reached from the rewards hub when a chest is
/// available (`/chest`).
class ChestRevealScreen extends ConsumerStatefulWidget {
  const ChestRevealScreen({super.key});

  @override
  ConsumerState<ChestRevealScreen> createState() => _ChestRevealScreenState();
}

enum _Phase { closed, opening, revealed }

class _ChestRevealScreenState extends ConsumerState<ChestRevealScreen>
    with TickerProviderStateMixin {
  late final AnimationController _entrance = AnimationController(
    vsync: this,
    duration: const Duration(milliseconds: 500),
  )..forward();

  late final AnimationController _open =
      AnimationController(
        vsync: this,
        duration: const Duration(milliseconds: 1600),
      )..addStatusListener((s) {
        if (s == AnimationStatus.completed && mounted) {
          setState(() => _phase = _Phase.revealed);
        }
      });

  _Phase _phase = _Phase.closed;
  Reward? _reward;

  @override
  void dispose() {
    _entrance.dispose();
    _open.dispose();
    super.dispose();
  }

  Future<void> _openChest() async {
    if (_phase != _Phase.closed) return;
    final reward = await ref.read(appControllerProvider.notifier).openChest();
    if (!mounted) return;
    if (reward == null) {
      context.pop();
      return;
    }
    ref.read(soundServiceProvider).play(Sfx.levelUp);
    setState(() {
      _reward = reward;
      _phase = _Phase.opening;
    });
    _open.forward(from: 0);
  }

  void _reset() {
    setState(() {
      _phase = _Phase.closed;
      _reward = null;
    });
    _open.reset();
    _entrance.forward(from: 0);
  }

  @override
  Widget build(BuildContext context) {
    final data = ref.watch(appControllerProvider).valueOrNull;
    final remaining = data?.progress.game.unopenedChests ?? 0;
    final scheme = Theme.of(context).colorScheme;

    return Scaffold(
      appBar: AppBar(title: const Text('Chest')),
      body: Center(
        child: Padding(
          padding: kPagePadding,
          child: Column(
            mainAxisAlignment: MainAxisAlignment.center,
            children: [
              SizedBox(
                height: 280,
                width: double.infinity,
                child: AnimatedBuilder(
                  animation: Listenable.merge([_open, _entrance]),
                  builder: (context, _) => _buildStage(scheme),
                ),
              ),
              Gap.xl,
              _buildCaption(),
              Gap.l,
              _buildAction(remaining),
            ],
          ),
        ),
      ),
    );
  }

  Widget _buildStage(ColorScheme scheme) {
    final t = _open.value;
    // Build-up shake during the first ~45% of the open animation.
    final shakeT = (t / 0.45).clamp(0.0, 1.0);
    final shaking = _phase == _Phase.opening && t < 0.45;
    final angle = shaking ? sin(shakeT * pi * 8) * 0.18 * (1 - shakeT) : 0.0;
    final chestScale = 1.0 + (shaking ? shakeT * 0.15 : 0.0);

    // Chest fades out as it "pops" around 45–60%.
    final chestOpacity = (1 - ((t - 0.45) / 0.15)).clamp(0.0, 1.0);
    // Glow ring bursts outward 45–100%.
    final burst = ((t - 0.45) / 0.55).clamp(0.0, 1.0);
    // Reward springs in from ~55%.
    final revealT = ((t - 0.55) / 0.45).clamp(0.0, 1.0);
    final entrance = Curves.easeOutBack.transform(_entrance.value);

    return Stack(
      alignment: Alignment.center,
      children: [
        // Burst glow.
        if (burst > 0)
          Opacity(
            opacity: (1 - burst) * 0.8,
            child: Container(
              width: 120 + burst * 220,
              height: 120 + burst * 220,
              decoration: BoxDecoration(
                shape: BoxShape.circle,
                gradient: RadialGradient(
                  colors: [
                    AppTheme.xpGold.withValues(alpha: 0.7),
                    AppTheme.xpGold.withValues(alpha: 0.0),
                  ],
                ),
              ),
            ),
          ),
        // Flying sparkles.
        if (burst > 0) ..._sparkles(burst),
        // Closed chest (shaking, then popping).
        if (_phase != _Phase.revealed && chestOpacity > 0)
          Opacity(
            opacity: (_phase == _Phase.closed ? entrance : chestOpacity).clamp(
              0.0,
              1.0,
            ),
            child: Transform.scale(
              scale: (_phase == _Phase.closed ? entrance : chestScale).clamp(
                0.01,
                2.0,
              ),
              child: Transform.rotate(
                angle: angle,
                child: const Text('🎁', style: TextStyle(fontSize: 150)),
              ),
            ),
          ),
        // Revealed reward badge.
        if (revealT > 0 && _reward != null)
          Transform.scale(
            scale: Curves.elasticOut.transform(revealT).clamp(0.0, 1.4),
            child: _RewardBadge(reward: _reward!),
          ),
      ],
    );
  }

  List<Widget> _sparkles(double burst) {
    const glyphs = ['✨', '⭐', '🌟', '🎉', '💫', '✨', '⭐', '🎊'];
    return List.generate(glyphs.length, (i) {
      final a = (i / glyphs.length) * 2 * pi;
      final r = burst * 150;
      return Transform.translate(
        offset: Offset(cos(a) * r, sin(a) * r),
        child: Opacity(
          opacity: (1 - burst).clamp(0.0, 1.0),
          child: Text(glyphs[i], style: const TextStyle(fontSize: 30)),
        ),
      );
    });
  }

  Widget _buildCaption() {
    return switch (_phase) {
      _Phase.closed => Text(
        'Tap the chest to open it!',
        style: Theme.of(context).textTheme.titleMedium,
        textAlign: TextAlign.center,
      ),
      _Phase.opening => const SizedBox(height: 24),
      _Phase.revealed => Column(
        children: [
          Text(
            _reward!.title,
            textAlign: TextAlign.center,
            style: const TextStyle(fontSize: 26, fontWeight: FontWeight.w900),
          ),
          Gap.s,
          Text(_reward!.description, textAlign: TextAlign.center),
        ],
      ),
    };
  }

  Widget _buildAction(int remaining) {
    switch (_phase) {
      case _Phase.closed:
        return FilledButton.icon(
          onPressed: _openChest,
          icon: const Icon(Icons.lock_open_rounded),
          label: const Text('Open chest'),
        );
      case _Phase.opening:
        return const SizedBox(height: 40);
      case _Phase.revealed:
        return Column(
          children: [
            if (remaining > 0)
              FilledButton.icon(
                onPressed: _reset,
                icon: const Icon(Icons.card_giftcard_rounded),
                label: Text('Open another ($remaining left)'),
              ),
            if (remaining > 0) Gap.s,
            TextButton(
              onPressed: () => context.pop(),
              child: const Text('Done'),
            ),
          ],
        );
    }
  }
}

class _RewardBadge extends StatelessWidget {
  const _RewardBadge({required this.reward});
  final Reward reward;

  @override
  Widget build(BuildContext context) {
    final emoji = switch (reward.kind) {
      RewardKind.xp => '⚡',
      RewardKind.streakFreeze => '❄️',
      RewardKind.xpBoost => '🚀',
      RewardKind.avatar => '🧑‍🚀',
      RewardKind.item => '✨',
    };
    return Container(
      width: 150,
      height: 150,
      decoration: BoxDecoration(
        shape: BoxShape.circle,
        color: AppTheme.xpGold.withValues(alpha: 0.16),
        border: Border.all(color: AppTheme.xpGold, width: 3),
      ),
      alignment: Alignment.center,
      child: Text(emoji, style: const TextStyle(fontSize: 72)),
    );
  }
}
