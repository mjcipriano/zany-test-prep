import '../models/exam.dart';

/// Which module-2 set a section was routed to on a multistage test.
///
/// [linear] = no routing (ACT, a lone module, the dashboard's practice-based
/// prediction). On the SAT the route decides which part of the scale is
/// reachable: [harder] unlocks the top, [easier] caps the section.
enum SectionRoute {
  linear,
  easier,
  harder;

  String get id => name;

  static SectionRoute parse(Object? value) => switch (value) {
    'easier' => SectionRoute.easier,
    'harder' => SectionRoute.harder,
    _ => SectionRoute.linear,
  };
}

/// Maps raw correct answers onto an exam's reported scale (SAT 200–800 /
/// 400–1600, ACT 1–36 / composite, or plain percent). Pure functions, easy to
/// test.
///
/// SAT and ACT use nonlinear raw→scale conversion curves shaped like published
/// practice-test tables: flat near the floor (guessing territory), roughly
/// linear through the middle, and steep at the top (each of the last few
/// questions is worth more). The anchor points below are ORIGINAL — invented
/// for this app, not copied from any College Board or ACT table — and are
/// interpolated linearly by fraction correct, so they apply to any module
/// length. They are estimates, not an official equating.
class ExamScoring {
  const ExamScoring(this.spec);

  final ScoringSpec spec;

  /// SAT section, no routing (linear test / practice-based prediction).
  /// (fraction correct, scaled score); 50% ≈ 480, 80% ≈ 660.
  static const satLinearCurve = <(double, int)>[
    (0.00, 200),
    (0.10, 220),
    (0.20, 290),
    (0.30, 360),
    (0.40, 420),
    (0.50, 480),
    (0.60, 540),
    (0.70, 600),
    (0.80, 660),
    (0.90, 730),
    (0.95, 770),
    (1.00, 800),
  ];

  /// SAT section routed to the HARDER module 2: the same raw fraction is worth
  /// more because the second half was harder; only this route reaches 800.
  static const satHarderCurve = <(double, int)>[
    (0.00, 200),
    (0.10, 260),
    (0.20, 330),
    (0.30, 400),
    (0.40, 460),
    (0.50, 520),
    (0.60, 580),
    (0.70, 640),
    (0.80, 700),
    (0.90, 750),
    (0.95, 780),
    (1.00, 800),
  ];

  /// SAT section routed to the EASIER module 2: a perfect section tops out at
  /// [satEasierCap] (the real test caps this route in the low-to-mid 600s).
  static const satEasierCurve = <(double, int)>[
    (0.00, 200),
    (0.10, 210),
    (0.20, 260),
    (0.30, 320),
    (0.40, 380),
    (0.50, 430),
    (0.60, 480),
    (0.70, 530),
    (0.80, 570),
    (0.90, 610),
    (0.95, 630),
    (1.00, satEasierCap),
  ];

  /// Highest section score reachable on the easier route.
  static const satEasierCap = 640;

  /// ACT section, 1–36: about half right ≈ 18, 80% ≈ 26.
  static const actCurve = <(double, int)>[
    (0.00, 1),
    (0.10, 6),
    (0.20, 10),
    (0.30, 13),
    (0.40, 15),
    (0.50, 18),
    (0.60, 20),
    (0.70, 23),
    (0.80, 26),
    (0.90, 30),
    (0.95, 33),
    (1.00, 36),
  ];

  /// Piecewise-linear lookup of [x] (0..1) in an ascending anchor [curve].
  static double interpolate(List<(double, int)> curve, double x) {
    if (x <= curve.first.$1) return curve.first.$2.toDouble();
    for (var i = 1; i < curve.length; i++) {
      final (x1, y1) = curve[i];
      if (x <= x1) {
        final (x0, y0) = curve[i - 1];
        return y0 + (y1 - y0) * (x - x0) / (x1 - x0);
      }
    }
    return curve.last.$2.toDouble();
  }

  /// A section score for [correct] of [total] on [spec.scale]. [route] only
  /// matters on the SAT scale (see [SectionRoute]).
  int sectionScore(
    int correct,
    int total, {
    SectionRoute route = SectionRoute.linear,
  }) {
    final acc = total <= 0 ? 0.0 : (correct / total).clamp(0.0, 1.0);
    switch (spec.scale) {
      case ScoreScale.sat1600:
        final curve = switch (route) {
          SectionRoute.linear => satLinearCurve,
          SectionRoute.easier => satEasierCurve,
          SectionRoute.harder => satHarderCurve,
        };
        // Reported to the nearest 10, like the real scale.
        return (interpolate(curve, acc) / 10).round() * 10;
      case ScoreScale.act36:
        return interpolate(actCurve, acc).round().clamp(1, 36);
      case ScoreScale.percent:
        return (acc * 100).round();
    }
  }

  /// The full raw→scaled table for a section of [total] questions on [route]
  /// (index = raw correct). Handy for docs, debugging and tests.
  List<int> conversionTable(
    int total, {
    SectionRoute route = SectionRoute.linear,
  }) => [
    for (var raw = 0; raw <= total; raw++)
      sectionScore(raw, total, route: route),
  ];

  /// The best section score reachable on [route] (the easier SAT route is
  /// capped; everything else can reach [sectionMax]).
  int sectionCeiling(SectionRoute route) =>
      spec.scale == ScoreScale.sat1600 && route == SectionRoute.easier
      ? satEasierCap
      : sectionMax;

  /// The lowest/highest possible section score on this scale.
  int get sectionMin => switch (spec.scale) {
    ScoreScale.sat1600 => 200,
    ScoreScale.act36 => 1,
    ScoreScale.percent => 0,
  };

  int get sectionMax => switch (spec.scale) {
    ScoreScale.sat1600 => 800,
    ScoreScale.act36 => 36,
    ScoreScale.percent => 100,
  };

  /// Domains that feed the composite/total, in [domains] order.
  List<String> compositeDomains(List<String> domains) =>
      spec.compositeDomains.isEmpty
      ? domains
      : domains.where(spec.compositeDomains.contains).toList();

  /// Combines per-domain section scores into the headline number.
  /// [sectionScores] maps domain id -> section score.
  int composite(Map<String, int> sectionScores) {
    final use = compositeDomains(sectionScores.keys.toList());
    if (use.isEmpty) return sectionMin;
    final values = [for (final d in use) sectionScores[d] ?? sectionMin];
    switch (spec.scale) {
      case ScoreScale.sat1600:
        return values.fold(0, (s, v) => s + v);
      case ScoreScale.act36:
      case ScoreScale.percent:
        return (values.fold(0, (s, v) => s + v) / values.length).round();
    }
  }

  /// The best possible composite for [domains] (e.g. 1600, 36, 100).
  int compositeMax(List<String> domains) {
    final n = compositeDomains(domains).length;
    switch (spec.scale) {
      case ScoreScale.sat1600:
        return sectionMax * (n == 0 ? 1 : n);
      case ScoreScale.act36:
      case ScoreScale.percent:
        return sectionMax;
    }
  }

  /// Short caption under the headline number ("Out of 1600", "1–36 composite").
  String compositeCaption(List<String> domains) => switch (spec.scale) {
    ScoreScale.sat1600 => 'Out of ${compositeMax(domains)}',
    ScoreScale.act36 => 'On the 1–36 composite scale',
    ScoreScale.percent => 'Average accuracy across sections',
  };

  /// Formats a section score for display ("640", "28", "72%").
  String formatSection(int score) =>
      spec.scale == ScoreScale.percent ? '$score%' : '$score';
}
