import 'package:flutter/material.dart';

import 'theme.dart';

/// A rounded surface card used across the app.
class AppCard extends StatelessWidget {
  const AppCard({
    super.key,
    required this.child,
    this.padding,
    this.color,
    this.onTap,
  });

  final Widget child;
  final EdgeInsetsGeometry? padding;
  final Color? color;
  final VoidCallback? onTap;

  @override
  Widget build(BuildContext context) {
    final scheme = Theme.of(context).colorScheme;
    return Material(
      color: color ?? scheme.surfaceContainerHigh,
      borderRadius: BorderRadius.circular(20),
      child: InkWell(
        onTap: onTap,
        borderRadius: BorderRadius.circular(20),
        child: Padding(
          padding: padding ?? const EdgeInsets.all(16),
          child: child,
        ),
      ),
    );
  }
}

/// A small icon + value chip (streak, XP, level). The accent [color] tints
/// the chip; the icon and value use its readable variant
/// ([AppColors.textOn]). Screen readers hear [semanticLabel] (e.g. "12 day
/// streak") instead of the bare number.
class StatPill extends StatelessWidget {
  const StatPill({
    super.key,
    required this.icon,
    required this.value,
    required this.color,
    this.semanticLabel,
  });

  final IconData icon;
  final String value;
  final Color color;
  final String? semanticLabel;

  @override
  Widget build(BuildContext context) {
    final fg = AppColors.of(context).textOn(color);
    return Semantics(
      label: semanticLabel,
      excludeSemantics: semanticLabel != null,
      child: Container(
        padding: const EdgeInsets.symmetric(horizontal: 12, vertical: 8),
        decoration: BoxDecoration(
          color: color.withValues(alpha: 0.14),
          borderRadius: BorderRadius.circular(14),
        ),
        child: Row(
          mainAxisSize: MainAxisSize.min,
          children: [
            Icon(icon, color: fg, size: 20),
            const SizedBox(width: 6),
            Flexible(
              child: Text(
                value,
                maxLines: 1,
                overflow: TextOverflow.ellipsis,
                style: TextStyle(fontWeight: FontWeight.w800, color: fg),
              ),
            ),
          ],
        ),
      ),
    );
  }
}

/// An animated XP/progress bar that fills toward [value] (0..1).
class ProgressBar extends StatelessWidget {
  const ProgressBar({
    super.key,
    required this.value,
    this.color,
    this.height = 12,
    this.animate = true,
    this.semanticLabel,
    this.semanticValue,
  });

  final double value;
  final Color? color;
  final double height;
  final bool animate;

  /// What the bar measures ("Daily goal"), read by screen readers.
  final String? semanticLabel;

  /// The value as words ("40 of 50 XP"); defaults to a percentage.
  final String? semanticValue;

  @override
  Widget build(BuildContext context) {
    final scheme = Theme.of(context).colorScheme;
    final c = color ?? scheme.primary;
    final v = value.isNaN ? 0.0 : value.clamp(0.0, 1.0);
    // Reduce motion: fill instantly when the system asks for no animations.
    final animate =
        this.animate &&
        !(MediaQuery.maybeDisableAnimationsOf(context) ?? false);
    return Semantics(
      label: semanticLabel,
      value: semanticValue ?? '${(v * 100).round()}%',
      excludeSemantics: true,
      child: _bar(scheme, c, v, animate),
    );
  }

  Widget _bar(ColorScheme scheme, Color c, double v, bool animate) {
    return ClipRRect(
      borderRadius: BorderRadius.circular(height),
      child: Stack(
        children: [
          Container(height: height, color: scheme.surfaceContainerHighest),
          TweenAnimationBuilder<double>(
            tween: Tween(begin: 0, end: v),
            duration: animate
                ? const Duration(milliseconds: 600)
                : Duration.zero,
            curve: Curves.easeOutCubic,
            builder: (context, v, _) => FractionallySizedBox(
              widthFactor: v,
              child: Container(height: height, color: c),
            ),
          ),
        ],
      ),
    );
  }
}

/// Section label used above grouped content.
class SectionLabel extends StatelessWidget {
  const SectionLabel(this.text, {super.key, this.trailing});
  final String text;
  final Widget? trailing;

  @override
  Widget build(BuildContext context) {
    return Padding(
      padding: const EdgeInsets.only(bottom: 8, top: 8),
      child: Row(
        children: [
          Expanded(
            child: Text(
              text.toUpperCase(),
              style: Theme.of(context).textTheme.labelLarge?.copyWith(
                letterSpacing: 1,
                fontWeight: FontWeight.w800,
                color: Theme.of(context).colorScheme.onSurfaceVariant,
              ),
            ),
          ),
          if (trailing != null) trailing!,
        ],
      ),
    );
  }
}

/// Row of crown/star icons (0-3) for lesson mastery, read as "2 of 3 stars".
class CrownRow extends StatelessWidget {
  const CrownRow({super.key, required this.stars, this.size = 18});
  final int stars;
  final double size;

  @override
  Widget build(BuildContext context) {
    final gold = AppColors.of(context).textOn(AppTheme.xpGold, minRatio: 3);
    return Semantics(
      label: '$stars of 3 stars',
      excludeSemantics: true,
      child: Row(
        mainAxisSize: MainAxisSize.min,
        children: List.generate(3, (i) {
          final filled = i < stars;
          return Icon(
            filled ? Icons.star_rounded : Icons.star_outline_rounded,
            size: size,
            color: filled ? gold : Theme.of(context).colorScheme.outline,
          );
        }),
      ),
    );
  }
}
