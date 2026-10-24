import '../models/exam.dart';

/// Maps raw accuracy onto an exam's reported scale (SAT 200–800 / 400–1600,
/// ACT 1–36 / composite, or plain percent). Pure functions, easy to test.
///
/// These are rough linear estimates from accuracy — good enough to show a
/// learner where they stand, not an official equating table.
class ExamScoring {
  const ExamScoring(this.spec);

  final ScoringSpec spec;

  /// A section score for [correct] of [total] on [spec.scale].
  int sectionScore(int correct, int total) {
    final acc = total <= 0 ? 0.0 : (correct / total).clamp(0.0, 1.0);
    switch (spec.scale) {
      case ScoreScale.sat1600:
        // 200..800, reported to the nearest 10.
        return ((200 + acc * 600) / 10).round() * 10;
      case ScoreScale.act36:
        return (1 + acc * 35).round().clamp(1, 36);
      case ScoreScale.percent:
        return (acc * 100).round();
    }
  }

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
