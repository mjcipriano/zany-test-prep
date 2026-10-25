import 'dart:math';

import '../models/content_bundle.dart';
import '../models/difficulty.dart';
import '../models/progress.dart';
import '../models/question.dart';
import 'game_service.dart';
import 'recommendation_engine.dart';

/// One skill's line in the placement-check summary.
class DiagnosticSkillResult {
  const DiagnosticSkillResult({
    required this.skillId,
    required this.domain,
    required this.correct,
    required this.estimate,
  });

  final String skillId;
  final String domain;
  final bool correct;
  final double estimate;
}

/// Right/total per domain, in exam order.
class DiagnosticDomainResult {
  const DiagnosticDomainResult({
    required this.domain,
    required this.correct,
    required this.total,
  });

  final String domain;
  final int correct;
  final int total;
}

/// What the placement check found, for the friendly summary screen.
class DiagnosticSummary {
  const DiagnosticSummary({
    required this.correct,
    required this.total,
    required this.strong,
    required this.focus,
    required this.domains,
  });

  final int correct;
  final int total;

  /// Tested skills answered right, best first.
  final List<DiagnosticSkillResult> strong;

  /// Tested skills answered wrong, weakest first.
  final List<DiagnosticSkillResult> focus;
  final List<DiagnosticDomainResult> domains;
}

/// The onboarding placement check ("diagnostic"): a short quiz spanning the
/// exam's domains and sections that seeds per-skill mastery estimates, so
/// recommendations are useful from day one. Exam-agnostic: the domains,
/// sections and skills come from the bundle's skill map.
///
/// **Seeding math.** A tested skill gets [testedEstimate] (right: easy 50 /
/// medium 62 / hard 72; wrong: 15 / 25 / 32). Every other skill in a tested
/// section is inferred as the section's mean shrunk toward
/// [kUnknownMasteryPrior] with one pseudo-observation:
/// `(sum + prior) / (n + 1)`. Skills whose section was not tested but whose
/// domain was use the domain's results with two pseudo-observations. Estimates
/// are marked [SkillMastery.seeded] so badges ignore them; real practice
/// clears the flag. A skill with real practice is never overwritten: a tested
/// one is averaged with the new estimate, an inferred one is left alone.
///
/// The check grants no XP, streak or chest — it is a measurement, not a
/// session — so retaking it can't be farmed.
class DiagnosticEngine {
  const DiagnosticEngine({this.length = 12});

  /// Questions per check (≈ 2–3 minutes).
  final int length;

  static double testedEstimate(bool correct, Difficulty d) => correct
      ? switch (d) {
          Difficulty.easy => 50,
          Difficulty.medium => 62,
          Difficulty.hard => 72,
        }
      : switch (d) {
          Difficulty.easy => 15,
          Difficulty.medium => 25,
          Difficulty.hard => 32,
        };

  /// Picks [length] questions, one per skill, spread evenly: domains take
  /// turns (exam order) and, within a domain, sections take turns, so a
  /// 12-question SAT check covers all 8 sections and an ACT one covers all 4
  /// domains. Skill order within a section and the question per skill (medium
  /// preferred) come from [rng].
  List<Question> pick(ContentBundle bundle, Random rng) {
    final bySkill = <String, List<Question>>{};
    for (final q in bundle.questions) {
      bySkill.putIfAbsent(q.skill, () => []).add(q);
    }

    // Per domain: its sections' skills (shuffled), round-robined by section.
    final perDomain = <List<String>>[];
    for (final d in bundle.skillMap.domains) {
      final sections = [
        for (final s in d.sections)
          [
            for (final sk in s.skills)
              if (bySkill.containsKey(sk.id)) sk.id,
          ]..shuffle(rng),
      ]..removeWhere((s) => s.isEmpty);
      perDomain.add(_roundRobin(sections));
    }
    if (perDomain.every((d) => d.isEmpty)) {
      // No skill map: fall back to every skill in question order.
      perDomain.add(bySkill.keys.toList()..shuffle(rng));
    }

    final skills = _roundRobin(perDomain).take(length);
    return [for (final skill in skills) _questionFor(bySkill[skill]!, rng)];
  }

  Question _questionFor(List<Question> pool, Random rng) {
    final medium = pool.where((q) => q.difficulty == Difficulty.medium);
    final from = medium.isNotEmpty ? medium.toList() : pool;
    return from[rng.nextInt(from.length)];
  }

  static List<String> _roundRobin(List<List<String>> lists) {
    final out = <String>[];
    for (var i = 0; ; i++) {
      var any = false;
      for (final l in lists) {
        if (i < l.length) {
          out.add(l[i]);
          any = true;
        }
      }
      if (!any) return out;
    }
  }

  /// Mastery estimates (bare skill id -> 0-100) from [results]: tested skills
  /// plus skills inferred from their section or domain.
  Map<String, double> estimates(
    ContentBundle bundle,
    List<AnswerResult> results,
  ) {
    final tested = <String, double>{};
    for (final r in results) {
      final e = testedEstimate(r.correct, r.question.difficulty);
      // A skill answered twice keeps the mean.
      tested.update(r.question.skill, (v) => (v + e) / 2, ifAbsent: () => e);
    }

    final out = <String, double>{...tested};
    for (final d in bundle.skillMap.domains) {
      final domainVals = [
        for (final s in d.sections)
          for (final sk in s.skills)
            if (tested.containsKey(sk.id)) tested[sk.id]!,
      ];
      for (final s in d.sections) {
        final sectionVals = [
          for (final sk in s.skills)
            if (tested.containsKey(sk.id)) tested[sk.id]!,
        ];
        for (final sk in s.skills) {
          if (out.containsKey(sk.id)) continue;
          if (sectionVals.isNotEmpty) {
            out[sk.id] = _shrink(sectionVals, 1);
          } else if (domainVals.isNotEmpty) {
            out[sk.id] = _shrink(domainVals, 2);
          }
        }
      }
    }
    return out;
  }

  static double _shrink(List<double> vals, int pseudo) =>
      (vals.reduce((a, b) => a + b) + kUnknownMasteryPrior * pseudo) /
      (vals.length + pseudo);

  /// Writes the estimates into [progress] (see the class doc for the rules)
  /// and marks the check done for the bundle's exam.
  void seed(
    AppProgress progress,
    ContentBundle bundle,
    List<AnswerResult> results,
  ) {
    final examId = bundle.exam.id;
    final testedSkills = {for (final r in results) r.question.skill};
    estimates(bundle, results).forEach((skill, estimate) {
      final key = masteryKey(examId, skill);
      final existing = progress.skillMastery[key];
      // Real evidence: practiced since the field existed, or legacy mastery.
      final practiced =
          existing != null &&
          !existing.seeded &&
          (existing.attempts > 0 || existing.mastery > 0);
      if (!practiced) {
        progress.skillMastery[key] = SkillMastery(
          skillId: key,
          mastery: estimate,
          attempts: existing?.attempts ?? 0,
          lastPracticedDay: existing?.lastPracticedDay,
          seeded: true,
        );
      } else if (testedSkills.contains(skill)) {
        existing.mastery = (existing.mastery + estimate) / 2;
      }
    });
    progress.game.markDiagnosticDone(examId);
  }

  /// The friendly summary: score, per-domain tallies, strong and focus skills.
  DiagnosticSummary summarize(
    ContentBundle bundle,
    List<AnswerResult> results,
  ) {
    final perSkill = <String, DiagnosticSkillResult>{};
    for (final r in results) {
      final q = r.question;
      perSkill[q.skill] = DiagnosticSkillResult(
        skillId: q.skill,
        domain: q.domain,
        correct: r.correct,
        estimate: testedEstimate(r.correct, q.difficulty),
      );
    }
    final strong = perSkill.values.where((s) => s.correct).toList()
      ..sort((a, b) => b.estimate.compareTo(a.estimate));
    final focus = perSkill.values.where((s) => !s.correct).toList()
      ..sort((a, b) => a.estimate.compareTo(b.estimate));

    final domains = <DiagnosticDomainResult>[];
    for (final d in bundle.domainIds) {
      final rs = results.where((r) => r.question.domain == d).toList();
      if (rs.isEmpty) continue;
      domains.add(
        DiagnosticDomainResult(
          domain: d,
          correct: rs.where((r) => r.correct).length,
          total: rs.length,
        ),
      );
    }
    return DiagnosticSummary(
      correct: results.where((r) => r.correct).length,
      total: results.length,
      strong: strong,
      focus: focus,
      domains: domains,
    );
  }
}
