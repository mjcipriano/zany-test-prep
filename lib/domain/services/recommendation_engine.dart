import 'dart:math' as math;

import '../models/content_bundle.dart';
import '../models/lesson.dart';
import '../models/progress.dart';
import 'review_engine.dart';
import 'unlock_engine.dart';

/// Mastery assumed for a skill with no evidence at all (never practiced, no
/// placement estimate). Shared with the placement check's inference.
const double kUnknownMasteryPrior = 30;

/// Why a skill (or the review queue) is being recommended.
enum RecommendationReason {
  /// Enough misses are due that clearing the review queue comes first.
  reviewsDue,

  /// The skill has the lowest (estimated) mastery among unlocked skills.
  weakest,

  /// The skill has no practice or estimate yet.
  newSkill,
}

/// What the recommendation asks the learner to do.
enum RecommendationKind {
  /// Play the spaced-review queue (`/review`).
  review,

  /// Start the next lesson for the skill (teaching card first).
  lesson,

  /// Adaptive "Smart practice" focused on the skill.
  practice,
}

/// One unlocked skill's recommendation score, with the terms that built it
/// (kept so the UI can explain the pick and tests can check each term).
class SkillScore {
  const SkillScore({
    required this.skillId,
    required this.masteryKey,
    required this.domain,
    required this.mastery,
    required this.hasEstimate,
    required this.attempts,
    required this.dueReviews,
    required this.daysSincePractice,
    required this.weakness,
    required this.uncertainty,
    required this.dueBoost,
    required this.recencyPenalty,
    required this.domainBalance,
    required this.pathIndex,
  });

  final String skillId;
  final String masteryKey;
  final String domain;

  /// Mastery (0-100), or [kUnknownMasteryPrior] when [hasEstimate] is false.
  final double mastery;

  /// Whether the skill has a stored mastery (from practice or the placement
  /// check) rather than the prior.
  final bool hasEstimate;
  final int attempts;
  final int dueReviews;

  /// Whole days since the skill was last practiced (null = never).
  final int? daysSincePractice;

  final double weakness;
  final double uncertainty;
  final double dueBoost;
  final double recencyPenalty;
  final double domainBalance;

  /// Position of the skill's first lesson in path order (stable tie-break).
  final int pathIndex;

  double get score =>
      weakness + uncertainty + dueBoost + recencyPenalty + domainBalance;

  /// The one-line reason this skill would be recommended.
  RecommendationReason get reason => hasEstimate
      ? RecommendationReason.weakest
      : RecommendationReason.newSkill;
}

/// The single "Recommended for you" pick shown on Home.
class Recommendation {
  const Recommendation({
    required this.kind,
    required this.reason,
    required this.label,
    this.skillId,
    this.lessonId,
    this.dueCount = 0,
  });

  final RecommendationKind kind;
  final RecommendationReason reason;

  /// A short, friendly reason line ("Weakest: Linear equations",
  /// "3 reviews due").
  final String label;
  final String? skillId;
  final String? lessonId;
  final int dueCount;

  /// The route that starts the recommended activity.
  String get route => switch (kind) {
    RecommendationKind.review => '/review',
    RecommendationKind.lesson => '/lesson/$lessonId',
    RecommendationKind.practice => '/practice/smart?skill=$skillId',
  };
}

/// Ranks the learner's unlocked skills and picks what to do next.
///
/// Each unlocked skill gets an additive, explainable score:
///
/// - **weakness** `(100 - mastery) / 100` — weak skills first. Skills with no
///   mastery yet use [kUnknownMasteryPrior].
/// - **uncertainty** `0.3 / sqrt(1 + attempts)` — little-practiced skills get
///   a bonus (an upper-confidence-style nudge) so estimates firm up.
/// - **due reviews** `+0.12` per due review item for the skill (capped at 5).
/// - **recency** `-0.4` if practiced today, `-0.2` yesterday, `-0.1` two days
///   ago — so one skill isn't hammered session after session.
/// - **domain balance** `0.6 × (fair share − actual share)` of all practice,
///   once there are at least [balanceMinAttempts] answers — nudges toward the
///   exam's under-practiced domains (fair share = equal per domain).
///
/// Only skills with at least one unlocked lesson are candidates. Everything is
/// pure: the caller passes the clock, so results are deterministic.
class RecommendationEngine {
  const RecommendationEngine({
    this.unlock = const UnlockEngine(),
    this.review = const ReviewEngine(),
  });

  final UnlockEngine unlock;
  final ReviewEngine review;

  static const double uncertaintyWeight = 0.3;
  static const double duePerItem = 0.12;
  static const int dueCap = 5;
  static const double balanceWeight = 0.6;
  static const int balanceMinAttempts = 10;

  /// Due reviews at or above this make the review queue the recommendation.
  static const int reviewNudge = 3;

  static double recencyPenaltyFor(int? daysSince) => switch (daysSince) {
    null => 0,
    <= 0 => -0.4,
    1 => -0.2,
    2 => -0.1,
    _ => 0,
  };

  /// Unlocked skills, highest score (most worth practicing) first. Ties keep
  /// path order.
  List<SkillScore> rankSkills(
    ContentBundle bundle,
    AppProgress progress, {
    required DateTime now,
  }) {
    final examId = bundle.exam.id;
    final today = dayKey(now);

    // Skills in path order, with their domain and whether any lesson is open.
    final skillDomain = <String, String>{};
    final skillIndex = <String, int>{};
    final unlocked = <String>{};
    final ordered = unlock.pathOrder(bundle);
    for (final (i, l) in ordered.indexed) {
      skillDomain.putIfAbsent(l.skill, () => l.domain);
      skillIndex.putIfAbsent(l.skill, () => i);
      if (unlock.isUnlocked(l, progress)) unlocked.add(l.skill);
    }
    if (unlocked.isEmpty) return const [];

    // Due review items per mastery key (active exam only).
    final due = <String, int>{};
    for (final r in review.dueItems(progress, now: now, bundle: bundle)) {
      due[r.skillId] = (due[r.skillId] ?? 0) + 1;
    }

    // Practice share per domain, for the balance term.
    final domainAttempts = <String, int>{};
    var totalAttempts = 0;
    for (final e in skillDomain.entries) {
      final n = progress.skillMastery[masteryKey(examId, e.key)]?.attempts ?? 0;
      domainAttempts[e.value] = (domainAttempts[e.value] ?? 0) + n;
      totalAttempts += n;
    }
    final domains = skillDomain.values.toSet();
    final fairShare = domains.isEmpty ? 0.0 : 1 / domains.length;

    final out = <SkillScore>[];
    for (final skill in unlocked) {
      final key = masteryKey(examId, skill);
      final sm = progress.skillMastery[key];
      final mastery = sm?.mastery ?? kUnknownMasteryPrior;
      final attempts = sm?.attempts ?? 0;
      final last = sm?.lastPracticedDay;
      final days = last == null ? null : daysBetweenDayKeys(last, today);
      final dueN = due[key] ?? 0;
      final domain = skillDomain[skill]!;
      final balance = totalAttempts < balanceMinAttempts
          ? 0.0
          : balanceWeight *
                (fairShare - (domainAttempts[domain] ?? 0) / totalAttempts);
      out.add(
        SkillScore(
          skillId: skill,
          masteryKey: key,
          domain: domain,
          mastery: mastery,
          hasEstimate: sm != null,
          attempts: attempts,
          dueReviews: dueN,
          daysSincePractice: days,
          weakness: (100 - mastery.clamp(0, 100)) / 100,
          uncertainty: uncertaintyWeight / math.sqrt(1 + attempts),
          dueBoost: duePerItem * math.min(dueN, dueCap),
          recencyPenalty: recencyPenaltyFor(days),
          domainBalance: balance,
          pathIndex: skillIndex[skill]!,
        ),
      );
    }
    out.sort((a, b) {
      final c = b.score.compareTo(a.score);
      return c != 0 ? c : a.pathIndex.compareTo(b.pathIndex);
    });
    return out;
  }

  /// The single best next step, or null for a brand-new learner with nothing
  /// to go on yet (no practice, no placement check, no reviews) — Home then
  /// leans on the placement check and "Continue learning" instead.
  Recommendation? recommend(
    ContentBundle bundle,
    AppProgress progress, {
    required DateTime now,
  }) {
    final dueCount = review.dueCount(progress, now: now, bundle: bundle);
    Recommendation reviewPick() => Recommendation(
      kind: RecommendationKind.review,
      reason: RecommendationReason.reviewsDue,
      label: '$dueCount review${dueCount == 1 ? '' : 's'} due',
      dueCount: dueCount,
    );
    if (dueCount >= reviewNudge) return reviewPick();

    final ranked = rankSkills(bundle, progress, now: now);
    final anyEvidence = ranked.any((s) => s.hasEstimate);
    if (ranked.isEmpty || !anyEvidence) {
      return dueCount > 0 ? reviewPick() : null;
    }

    final top = ranked.first;
    final name = bundle.skillName(top.skillId);
    if (top.reason == RecommendationReason.newSkill) {
      // Never touched: teach it first when a lesson is open for it.
      final lesson = _nextLessonFor(bundle, progress, top.skillId);
      return Recommendation(
        kind: lesson == null
            ? RecommendationKind.practice
            : RecommendationKind.lesson,
        reason: RecommendationReason.newSkill,
        label: 'New to you: $name',
        skillId: top.skillId,
        lessonId: lesson?.id,
        dueCount: dueCount,
      );
    }
    return Recommendation(
      kind: RecommendationKind.practice,
      reason: RecommendationReason.weakest,
      label: 'Weakest: $name',
      skillId: top.skillId,
      dueCount: dueCount,
    );
  }

  /// The first unlocked, not-yet-completed lesson for [skill] in path order.
  Lesson? _nextLessonFor(
    ContentBundle bundle,
    AppProgress progress,
    String skill,
  ) {
    for (final l in unlock.pathOrder(bundle)) {
      if (l.skill == skill &&
          unlock.isUnlocked(l, progress) &&
          !progress.isLessonCompleted(l.id)) {
        return l;
      }
    }
    return null;
  }
}
