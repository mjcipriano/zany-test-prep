import 'package:flutter/material.dart';
import 'package:flutter_test/flutter_test.dart';
import 'package:zany_test_prep/design/contrast.dart';
import 'package:zany_test_prep/design/theme.dart';
import 'package:zany_test_prep/features/rewards/avatar_view.dart';

const _white = Color(0xFFFFFFFF);
const _black = Color(0xFF000000);

/// Every accent the app draws as text or as a meaningful icon.
const _accents = {
  'correct': AppTheme.correct,
  'incorrect': AppTheme.incorrect,
  'streak': AppTheme.streak,
  'xpGold': AppTheme.xpGold,
  'violet (pets)': Color(0xFF8E44AD),
  'freeze blue': Color(0xFF4FA3D1),
};

Map<String, Color> get _allAccents => {
  ..._accents,
  for (final (i, c) in AppTheme.domainPalette.indexed) 'domain $i': c,
  for (final r in [
    'starter',
    'common',
    'uncommon',
    'rare',
    'epic',
    'legendary',
  ])
    'rarity $r': rarityColor(r),
};

void main() {
  group('contrast maths', () {
    test('black on white is 21:1 and a colour on itself is 1:1', () {
      expect(contrastRatio(_black, _white), closeTo(21, 0.01));
      expect(contrastRatio(_white, _black), closeTo(21, 0.01));
      expect(contrastRatio(AppTheme.seed, AppTheme.seed), closeTo(1, 1e-9));
    });

    test('matches published WCAG values', () {
      // #767676 is the lightest grey that passes AA on white (4.54:1).
      expect(
        contrastRatio(const Color(0xFF767676), _white),
        closeTo(4.54, .01),
      );
      expect(meetsAA(const Color(0xFF767676), _white), isTrue);
      expect(meetsAA(const Color(0xFF777777), _white), isFalse);
      expect(meetsAA(const Color(0xFF949494), _white, large: true), isTrue);
    });

    test('translucent foregrounds are composited over the background', () {
      final half = _black.withValues(alpha: 0.5);
      expect(composite(half, _white).r, closeTo(0.5, 0.01));
      expect(
        contrastRatio(half, _white),
        closeTo(contrastRatio(composite(half, _white), _white), 1e-9),
      );
    });

    test('readableOn makes the smallest change that passes', () {
      const bg = Color(0xFFFBF8FF);
      final fixed = readableOn(AppTheme.streak, bg);
      expect(contrastRatio(fixed, bg), greaterThanOrEqualTo(kContrastText));
      expect(contrastRatio(fixed, bg), lessThan(kContrastText + 0.1));
      // Darkened toward black: same hue family (still orange: r > g > b).
      expect(fixed.r, greaterThan(fixed.g));
      expect(fixed.g, greaterThan(fixed.b));
      // Already readable colours are returned unchanged.
      expect(readableOn(_black, bg), _black);
      // On a dark background it lightens instead.
      final onDark = readableOn(AppTheme.seed, const Color(0xFF29292F));
      expect(
        relativeLuminance(onDark),
        greaterThan(relativeLuminance(AppTheme.seed)),
      );
    });
  });

  for (final (name, theme) in [
    ('light', AppTheme.light()),
    ('dark', AppTheme.dark()),
  ]) {
    group('$name theme meets WCAG AA', () {
      final s = theme.colorScheme;
      final colors = theme.extension<AppColors>()!;

      test('Material text/background pairs', () {
        final pairs = {
          'onSurface/surface': (s.onSurface, s.surface),
          'onSurface/card': (s.onSurface, s.surfaceContainerHigh),
          'onSurfaceVariant/surface': (s.onSurfaceVariant, s.surface),
          'onSurfaceVariant/card': (s.onSurfaceVariant, s.surfaceContainerHigh),
          'onSurfaceVariant/highest': (
            s.onSurfaceVariant,
            s.surfaceContainerHighest,
          ),
          'primary/surface': (s.primary, s.surface),
          'onPrimary/primary': (s.onPrimary, s.primary),
          'onPrimaryContainer': (s.onPrimaryContainer, s.primaryContainer),
          'onSecondaryContainer': (
            s.onSecondaryContainer,
            s.secondaryContainer,
          ),
          'onTertiaryContainer': (s.onTertiaryContainer, s.tertiaryContainer),
          'onSurface/tertiaryContainer': (s.onSurface, s.tertiaryContainer),
          'onError/error': (s.onError, s.error),
        };
        for (final MapEntry(key: label, value: (fg, bg)) in pairs.entries) {
          expect(meetsAA(fg, bg), isTrue, reason: label);
        }
      });

      test('outlines used as state indicators reach 3:1', () {
        // Choice letter circles and empty mastery stars.
        expect(meetsAA(s.outline, s.surfaceContainerHigh, large: true), isTrue);
        expect(meetsAA(s.outline, s.surface, large: true), isTrue);
      });

      test('feedback colours read on cards and on their own tints', () {
        final fgs = {
          'correct': (colors.correct, AppTheme.correct),
          'incorrect': (colors.incorrect, AppTheme.incorrect),
          'streak': (colors.streak, AppTheme.streak),
          'xp': (colors.xp, AppTheme.xpGold),
        };
        for (final MapEntry(key: label, value: (fg, accent)) in fgs.entries) {
          for (final bg in [
            s.surface,
            s.surfaceContainerHigh,
            composite(accent.withValues(alpha: 0.12), s.surface),
            composite(
              accent.withValues(alpha: AppColors.tintAlpha),
              s.surfaceContainerHigh,
            ),
          ]) {
            expect(meetsAA(fg, bg), isTrue, reason: '$label on $bg');
          }
        }
      });

      test('white text on the solid feedback fills', () {
        expect(meetsAA(_white, colors.correctFill), isTrue);
        expect(meetsAA(_white, colors.incorrectFill), isTrue);
      });

      test('every accent has a readable text variant', () {
        for (final MapEntry(key: label, value: accent) in _allAccents.entries) {
          final fg = colors.textOn(accent);
          for (final bg in [
            s.surfaceContainerHigh,
            composite(
              accent.withValues(alpha: AppColors.tintAlpha),
              s.surfaceContainerHigh,
            ),
          ]) {
            expect(meetsAA(fg, bg), isTrue, reason: '$label on $bg');
          }
        }
      });

      test('the readable variants stay close to the brand colours', () {
        // "Minimal visual change": no accent moves further than needed — at
        // most a third of the way to black or white.
        for (final MapEntry(key: label, value: accent) in _allAccents.entries) {
          final fg = colors.textOn(accent);
          final shift =
              (fg.r - accent.r).abs() +
              (fg.g - accent.g).abs() +
              (fg.b - accent.b).abs();
          expect(shift, lessThan(1.0), reason: label);
        }
      });

      test('completed lesson nodes: white check on the path colour (3:1)', () {
        // SAT and ACT use the first four path colours.
        for (final c in AppTheme.domainPalette.take(4)) {
          expect(meetsAA(_white, c, large: true), isTrue, reason: '$c');
        }
      });
    });
  }
}
