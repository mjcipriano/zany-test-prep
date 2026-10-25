import 'dart:math';

import '../models/difficulty.dart';
import '../models/exam.dart';
import '../models/question.dart';
import 'answer_checker.dart';
import 'scoring.dart';

/// Relative share of easy/medium/hard questions in a module.
class DifficultyMix {
  const DifficultyMix(this.easy, this.medium, this.hard, this.fillOrder);

  final double easy;
  final double medium;
  final double hard;

  /// Where to borrow from (nearest first) when a difficulty bucket runs dry.
  final List<Difficulty> fillOrder;

  double weight(Difficulty d) => switch (d) {
    Difficulty.easy => easy,
    Difficulty.medium => medium,
    Difficulty.hard => hard,
  };

  /// Module 1 of an adaptive section: an even spread, so it can tell a
  /// struggling student from a strong one.
  static const routing = DifficultyMix(1, 1, 1, [
    Difficulty.medium,
    Difficulty.easy,
    Difficulty.hard,
  ]);

  /// The harder module 2: mostly medium/hard.
  static const harder = DifficultyMix(0.15, 0.35, 0.50, [
    Difficulty.hard,
    Difficulty.medium,
    Difficulty.easy,
  ]);

  /// The easier module 2: mostly easy/medium.
  static const easier = DifficultyMix(0.50, 0.35, 0.15, [
    Difficulty.easy,
    Difficulty.medium,
    Difficulty.hard,
  ]);

  /// Splits [n] questions across easy/medium/hard by largest remainder, so
  /// the counts always sum to [n] and are deterministic.
  List<int> allocate(int n) {
    final w = [for (final d in Difficulty.values) weight(d)];
    final sum = w.fold(0.0, (s, x) => s + x);
    if (n <= 0 || sum <= 0) return [0, 0, 0];
    final exact = [for (final x in w) n * x / sum];
    final counts = [for (final e in exact) e.floor()];
    var left = n - counts.fold(0, (s, c) => s + c);
    final order = [0, 1, 2]
      ..sort((a, b) {
        final c = (exact[b] - counts[b]).compareTo(exact[a] - counts[a]);
        return c != 0 ? c : a.compareTo(b);
      });
    for (final i in order) {
      if (left-- <= 0) break;
      counts[i]++;
    }
    return counts;
  }
}

/// The route a section takes after its routing module: [SectionRoute.harder]
/// when at least [spec.routeThreshold] of the routing module was answered
/// correctly, [SectionRoute.easier] otherwise (including an empty module).
SectionRoute routeFor(int correct, int total, AdaptiveSpec spec) {
  if (total <= 0) return SectionRoute.easier;
  return correct / total >= spec.routeThreshold
      ? SectionRoute.harder
      : SectionRoute.easier;
}

/// Builds the modules of a full-length timed test from a question pool.
///
/// Linear modules (ACT, or any non-adaptive plan) draw at random from their
/// domain, exactly as before. On an adaptive plan the routing module draws an
/// even difficulty mix and each later module of that domain is assembled only
/// once its route is known ([buildModule] with `route:`), from the harder or
/// easier mix. Adaptive modules are ordered easy → hard, like the real test.
///
/// All randomness comes from the injected [Random] (shuffled once, up front),
/// so the same seed, pool and routes always produce the same test. No
/// question is used twice in one test; a module is simply shorter when its
/// domain runs out.
class TestAssembler {
  TestAssembler(Iterable<Question> questions, TimedTestPlan plan, Random rng) {
    for (final q in questions) {
      _pool.putIfAbsent(q.domain, () => []).add(q);
    }
    for (final list in _pool.values) {
      list.shuffle(rng);
    }
    // Drop modules whose domain has no questions at all (domain absent).
    this.plan = plan.only([
      for (var i = 0; i < plan.modules.length; i++)
        if (_pool[plan.modules[i].domain]?.isNotEmpty ?? false) i,
    ]);
  }

  final Map<String, List<Question>> _pool = {};
  final Set<String> _used = {};

  /// The plan actually being taken (modules for absent domains removed).
  late final TimedTestPlan plan;

  /// Questions for module [index] of [plan]. [route] is required (and only
  /// used) for a routed module; see [TimedTestPlan.routedBy].
  List<Question> buildModule(
    int index, {
    SectionRoute route = SectionRoute.linear,
  }) {
    final m = plan.modules[index];
    final src = _pool[m.domain] ?? const <Question>[];
    final DifficultyMix? mix;
    if (plan.isRoutingModule(index)) {
      mix = DifficultyMix.routing;
    } else if (plan.routedBy(index) != null) {
      mix = switch (route) {
        SectionRoute.harder => DifficultyMix.harder,
        SectionRoute.easier => DifficultyMix.easier,
        SectionRoute.linear => DifficultyMix.routing,
      };
    } else {
      mix = null;
    }

    final picked = <Question>[];
    void take(Iterable<Question> from, int n) {
      var left = n;
      for (final q in from) {
        if (left <= 0) break;
        if (_used.add(q.id)) {
          picked.add(q);
          left--;
        }
      }
    }

    if (mix == null) {
      take(src, m.count);
      return picked;
    }
    Iterable<Question> of(Difficulty d) => src.where((q) => q.difficulty == d);
    final want = mix.allocate(m.count);
    for (final d in Difficulty.values) {
      take(of(d), want[d.index]);
    }
    // Borrow from the nearest difficulty if a bucket ran dry.
    for (final d in mix.fillOrder) {
      take(of(d), m.count - picked.length);
    }
    return [
      for (final d in Difficulty.values)
        ...picked.where((q) => q.difficulty == d),
    ];
  }
}

/// One section's line on the results screen.
class SectionResult {
  const SectionResult({
    required this.domain,
    required this.correct,
    required this.total,
    required this.route,
    required this.score,
  });

  final String domain;
  final int correct;
  final int total;
  final SectionRoute route;
  final int score;
}

/// Scored outcome of a finished timed test.
class TimedTestReport {
  const TimedTestReport({required this.sections, required this.composite});

  final List<SectionResult> sections;
  final int composite;

  List<String> get domains => [for (final s in sections) s.domain];

  /// Scores every answered module. [domainOrder] fixes the section order;
  /// domains with no questions are left out. [routes] maps domain → route
  /// (missing = linear).
  factory TimedTestReport.score({
    required List<List<Question>> modules,
    required Map<String, String> answers,
    required Map<String, SectionRoute> routes,
    required ExamScoring scoring,
    required List<String> domainOrder,
  }) {
    final correct = <String, int>{};
    final total = <String, int>{};
    for (final q in modules.expand((m) => m)) {
      total[q.domain] = (total[q.domain] ?? 0) + 1;
      if (isAnsweredCorrectly(q, answers[q.id])) {
        correct[q.domain] = (correct[q.domain] ?? 0) + 1;
      }
    }
    final order = [
      ...domainOrder,
      ...total.keys.where((d) => !domainOrder.contains(d)),
    ];
    final sections = [
      for (final d in order)
        if ((total[d] ?? 0) > 0)
          () {
            final route = routes[d] ?? SectionRoute.linear;
            final c = correct[d] ?? 0;
            return SectionResult(
              domain: d,
              correct: c,
              total: total[d]!,
              route: route,
              score: scoring.sectionScore(c, total[d]!, route: route),
            );
          }(),
    ];
    return TimedTestReport(
      sections: sections,
      composite: scoring.composite({
        for (final s in sections) s.domain: s.score,
      }),
    );
  }
}

const _checker = AnswerChecker();

/// Whether [answer] (a choice id, or produced text for grid-ins) is correct.
bool isAnsweredCorrectly(Question q, String? answer) =>
    answer != null &&
    _checker.isCorrect(
      q,
      choiceId: q.type.isStudentProduced ? null : answer,
      produced: q.type.isStudentProduced ? answer : null,
    );
