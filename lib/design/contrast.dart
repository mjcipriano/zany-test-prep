import 'dart:math' as math;
import 'dart:ui' show Color;

/// WCAG 2.x colour-contrast maths (pure: no widgets, no theme lookups), used
/// to pick readable text colours and by test/unit/contrast_test.dart to keep
/// the theme's text/background pairs at AA.
///
/// See https://www.w3.org/TR/WCAG21/#dfn-contrast-ratio.

/// AA minimum for normal text.
const double kContrastText = 4.5;

/// AA minimum for large text (>= 18pt, or >= 14pt bold, i.e. 24 / 18.66 dp)
/// and for meaningful UI graphics (icons, borders, focus indicators).
const double kContrastLarge = 3.0;

double _channel(double c) =>
    c <= 0.04045 ? c / 12.92 : math.pow((c + 0.055) / 1.055, 2.4).toDouble();

/// Relative luminance of an opaque colour (0 = black, 1 = white).
double relativeLuminance(Color c) =>
    0.2126 * _channel(c.r) + 0.7152 * _channel(c.g) + 0.0722 * _channel(c.b);

/// [fg] composited over the opaque [bg] (alpha blending, like the screen).
Color composite(Color fg, Color bg) {
  final a = fg.a;
  double mix(double f, double b) => f * a + b * (1 - a);
  return Color.from(
    alpha: 1,
    red: mix(fg.r, bg.r),
    green: mix(fg.g, bg.g),
    blue: mix(fg.b, bg.b),
  );
}

/// Contrast ratio (1..21) of [fg] drawn on [bg]. A translucent [fg] is first
/// composited over [bg]; [bg] itself must be opaque (composite it first).
double contrastRatio(Color fg, Color bg) {
  final f = relativeLuminance(fg.a < 1 ? composite(fg, bg) : fg);
  final b = relativeLuminance(bg);
  final hi = math.max(f, b), lo = math.min(f, b);
  return (hi + 0.05) / (lo + 0.05);
}

/// Whether [fg] on [bg] meets WCAG AA for normal text, or for large text and
/// UI components when [large] is set.
bool meetsAA(Color fg, Color bg, {bool large = false}) =>
    contrastRatio(fg, bg) >= (large ? kContrastLarge : kContrastText);

/// The colour closest to [fg] (same hue and saturation, lightness nudged
/// toward black or white, whichever side [bg] leaves room on) that reaches
/// [minRatio] against [bg]. Returns [fg] unchanged when it already does.
/// Used for brand/rarity colours that double as text: a minimal shift keeps
/// them recognisable while making them readable.
Color readableOn(Color fg, Color bg, {double minRatio = kContrastText}) {
  final opaque = fg.a < 1 ? composite(fg, bg) : fg;
  if (contrastRatio(opaque, bg) >= minRatio) return opaque;
  final darken = relativeLuminance(bg) > 0.18;
  // Binary search on the mix toward black/white: the smallest step that
  // passes is the least visible change.
  final target = darken ? const Color(0xFF000000) : const Color(0xFFFFFFFF);
  var lo = 0.0, hi = 1.0;
  for (var i = 0; i < 24; i++) {
    final mid = (lo + hi) / 2;
    if (contrastRatio(_lerp(opaque, target, mid), bg) >= minRatio) {
      hi = mid;
    } else {
      lo = mid;
    }
  }
  return _lerp(opaque, target, hi);
}

Color _lerp(Color a, Color b, double t) => Color.from(
  alpha: 1,
  red: a.r + (b.r - a.r) * t,
  green: a.g + (b.g - a.g) * t,
  blue: a.b + (b.b - a.b) * t,
);
