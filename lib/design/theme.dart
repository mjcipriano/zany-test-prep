import 'package:flutter/material.dart';

import 'contrast.dart';

/// Central design tokens and Material 3 themes (light + dark).
class AppTheme {
  static const seed = Color(0xFF5B6CF6); // friendly indigo
  static const correct = Color(0xFF2E9E5B);
  static const incorrect = Color(0xFFE0413E);
  static const streak = Color(0xFFFF8A3D);
  static const xpGold = Color(0xFFF4B740);

  /// Accent colours for an exam's domains, by position in the exam's domain
  /// order (SAT: Reading & Writing, Math; ACT: English, Math, Reading, Science).
  static const domainPalette = [
    seed,
    correct,
    Color(0xFF8E44AD), // violet
    Color(0xFF0E9AA7), // teal
    streak,
    Color(0xFFB03A6B), // berry
  ];

  static Color domainColor(int index) =>
      domainPalette[index < 0 ? 0 : index % domainPalette.length];

  static ThemeData light() => _build(Brightness.light);
  static ThemeData dark() => _build(Brightness.dark);

  static ThemeData _build(Brightness brightness) {
    final scheme = ColorScheme.fromSeed(
      seedColor: seed,
      brightness: brightness,
    );
    return ThemeData(
      useMaterial3: true,
      colorScheme: scheme,
      extensions: [AppColors.forScheme(scheme)],
      // Roboto is the Material/Android default; pinning it keeps typography
      // consistent across every text element (including buttons). The emoji
      // fallback family is a no-op on devices (the OS supplies emoji) and lets
      // the headless screenshot harness render emoji.
      fontFamily: 'Roboto',
      fontFamilyFallback: const ['NotoEmoji'],
      scaffoldBackgroundColor: scheme.surface,
      visualDensity: VisualDensity.adaptivePlatformDensity,
      appBarTheme: AppBarTheme(
        backgroundColor: scheme.surface,
        foregroundColor: scheme.onSurface,
        elevation: 0,
        centerTitle: false,
      ),
      cardTheme: CardThemeData(
        elevation: 0,
        color: scheme.surfaceContainerHigh,
        shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(20)),
      ),
      filledButtonTheme: FilledButtonThemeData(
        style: FilledButton.styleFrom(
          minimumSize: const Size.fromHeight(54),
          textStyle: const TextStyle(
            fontFamily: 'Roboto',
            fontSize: 16,
            fontWeight: FontWeight.w700,
          ),
          shape: RoundedRectangleBorder(
            borderRadius: BorderRadius.circular(16),
          ),
        ),
      ),
      outlinedButtonTheme: OutlinedButtonThemeData(
        style: OutlinedButton.styleFrom(
          minimumSize: const Size.fromHeight(54),
          textStyle: const TextStyle(
            fontFamily: 'Roboto',
            fontSize: 16,
            fontWeight: FontWeight.w700,
          ),
          shape: RoundedRectangleBorder(
            borderRadius: BorderRadius.circular(16),
          ),
        ),
      ),
      snackBarTheme: const SnackBarThemeData(
        behavior: SnackBarBehavior.floating,
      ),
    );
  }
}

/// Spacing scale used throughout the app.
class Gap {
  static const xs = SizedBox(height: 4, width: 4);
  static const s = SizedBox(height: 8, width: 8);
  static const m = SizedBox(height: 16, width: 16);
  static const l = SizedBox(height: 24, width: 24);
  static const xl = SizedBox(height: 32, width: 32);
}

const kPagePadding = EdgeInsets.all(20);

/// Readable variants of the app's accent colours for the active theme.
///
/// The brand accents ([AppTheme.correct], [AppTheme.streak], rarity and
/// domain colours…) are bright mid-tones: fine as fills, too light for text
/// on the light theme's cards (an orange "12" on a pale orange pill is about
/// 2:1). Text and meaningful icons drawn in an accent go through [textOn],
/// which nudges the accent's lightness just enough to reach WCAG AA (4.5:1)
/// on a card and on the accent's own tint; fills behind white text use the
/// `*Fill` colours. In the dark theme most accents already pass and come back
/// unchanged.
@immutable
class AppColors extends ThemeExtension<AppColors> {
  const AppColors._(this._card);

  /// Derives the readable colours for [scheme] (cards are
  /// `surfaceContainerHigh`).
  factory AppColors.forScheme(ColorScheme scheme) =>
      AppColors._(scheme.surfaceContainerHigh);

  final Color _card;

  static AppColors of(BuildContext context) =>
      Theme.of(context).extension<AppColors>() ??
      AppColors.forScheme(Theme.of(context).colorScheme);

  /// The strongest tint an accent is laid over (pills, chips, feedback bars).
  static const double tintAlpha = 0.18;

  /// [accent] adjusted to read as text (4.5:1) on a card, on the plain
  /// surface and on the accent's own [tintAlpha] tint over a card.
  Color textOn(Color accent, {double minRatio = kContrastText}) {
    final tint = composite(accent.withValues(alpha: tintAlpha), _card);
    var c = readableOn(accent, _card, minRatio: minRatio);
    c = readableOn(c, tint, minRatio: minRatio);
    return c;
  }

  /// [accent] darkened just enough to carry white text (4.5:1).
  Color fillFor(Color accent) => readableOn(accent, const Color(0xFFFFFFFF));

  Color get correct => textOn(AppTheme.correct);
  Color get incorrect => textOn(AppTheme.incorrect);
  Color get streak => textOn(AppTheme.streak);
  Color get xp => textOn(AppTheme.xpGold);

  /// Backgrounds for white text (feedback buttons, count badges).
  Color get correctFill => fillFor(AppTheme.correct);
  Color get incorrectFill => fillFor(AppTheme.incorrect);

  @override
  AppColors copyWith() => this;

  @override
  AppColors lerp(AppColors? other, double t) =>
      other == null || t < 0.5 ? this : other;
}
