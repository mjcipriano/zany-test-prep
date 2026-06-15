import '../models/content_bundle.dart';
import '../models/difficulty.dart';
import '../models/lesson.dart';
import '../models/profile.dart';
import '../models/progress.dart';
import '../models/question.dart';
import 'badges.dart';
import 'leveling.dart';
import 'mastery_engine.dart';
import 'review_engine.dart';
import 'streak_engine.dart';

/// One answered question within a lesson attempt.
class AnswerResult {
  const AnswerResult({
    required this.question,
    required this.correct,
    this.isReview = false,
    this.responseMs = 0,
  });

  final Question question;
  final bool correct;
  final bool isReview;
  final int responseMs;
}

/// Summary returned to the UI after a lesson is applied to progress.
class LessonOutcome {
  const LessonOutcome({
    required this.xpGained,
    required this.correct,
    required this.total,
    required this.stars,
    required this.leveledUp,
    required this.oldLevel,
    required this.newLevel,
    required this.currentStreak,
    required this.streakExtended,
    required this.streakReset,
    required this.dailyGoalMet,
    required this.dailyGoalJustMet,
    required this.newBadges,
  });

  final int xpGained;
  final int correct;
  final int total;
  final int stars;
  final bool leveledUp;
  final int oldLevel;
  final int newLevel;
  final int currentStreak;
  final bool streakExtended;
  final bool streakReset;
  final bool dailyGoalMet;
  final bool dailyGoalJustMet;
  final List<BadgeDef> newBadges;

  double get accuracy => total == 0 ? 0 : correct / total;
}

/// Applies a finished lesson attempt to the persisted progress state.
class GameService {
  const GameService({
    this.xp = const XpEngine(),
    this.level = const LevelEngine(),
    this.streak = const StreakEngine(),
    this.mastery = const MasteryEngine(),
    this.review = const ReviewEngine(),
  });

  final XpEngine xp;
  final LevelEngine level;
  final StreakEngine streak;
  final MasteryEngine mastery;
  final ReviewEngine review;

  static int starsForAccuracy(double accuracy) {
    if (accuracy >= 0.999) return 3;
    if (accuracy >= 0.8) return 2;
    if (accuracy >= 0.6) return 1;
    return 0;
  }

  /// Apply a finished practice set with no associated lesson (e.g. review mode).
  LessonOutcome applyPracticeResult({
    required AppProgress progress,
    required UserProfile profile,
    required List<AnswerResult> results,
    required ContentBundle bundle,
    DateTime? now,
  }) => applyLessonResult(
    progress: progress,
    profile: profile,
    lesson: null,
    results: results,
    bundle: bundle,
    now: now,
  );

  LessonOutcome applyLessonResult({
    required AppProgress progress,
    required UserProfile profile,
    required Lesson? lesson,
    required List<AnswerResult> results,
    required ContentBundle bundle,
    DateTime? now,
  }) {
    final today = now ?? DateTime.now();
    final correctCount = results.where((r) => r.correct).length;
    final total = results.length;
    final accuracy = total == 0 ? 0.0 : correctCount / total;
    final stars = starsForAccuracy(accuracy);

    // --- XP ---
    var gained = 0;
    for (final r in results) {
      gained += xp.xpForAnswer(
        correct: r.correct,
        difficulty: r.question.difficulty,
        isReview: r.isReview,
      );
    }
    if (total > 0) {
      gained += xp.lessonCompletionBonus;
      if (correctCount == total) gained += xp.perfectLessonBonus;
    }

    final g = progress.game;
    final oldLevel = level.levelForXp(g.totalXp);
    g.totalXp += gained;
    final newLevel = level.levelForXp(g.totalXp);

    // --- Streak ---
    final sr = streak.registerActivity(
      lastActiveDay: g.lastActiveDay,
      currentStreak: g.currentStreak,
      longestStreak: g.longestStreak,
      today: today,
    );
    g.currentStreak = sr.currentStreak;
    g.longestStreak = sr.longestStreak;
    g.lastActiveDay = sr.lastActiveDay;

    // --- Daily goal ---
    final todayKey = dayKey(today);
    if (g.dailyDay != todayKey) {
      g.dailyDay = todayKey;
      g.dailyXp = 0;
    }
    final goalBefore = g.dailyXp >= profile.dailyGoalXp;
    g.dailyXp += gained;
    final goalAfter = g.dailyXp >= profile.dailyGoalXp;

    // --- Lesson progress (skipped for review/practice with no lesson) ---
    if (lesson != null) {
      final lp = progress.lessonProgress(lesson.id);
      lp.completed = true;
      lp.timesCompleted += 1;
      lp.total = total;
      if (correctCount > lp.bestCorrect) lp.bestCorrect = correctCount;
      if (stars > lp.stars) lp.stars = stars;
      lp.lastCompletedDay = todayKey;
    }

    // --- Daily history (for the progress dashboard) ---
    progress.recordDay(
      todayKey,
      xp: gained,
      answered: total,
      correct: correctCount,
    );

    // --- Per-question stats, mastery, review ---
    for (final r in results) {
      final q = r.question;
      final stat = progress.questionStats.putIfAbsent(
        q.id,
        () => QuestionStat(questionId: q.id),
      );
      stat.attempts += 1;
      if (r.correct) stat.correct += 1;
      stat.lastCorrect = r.correct;
      stat.totalResponseMs += r.responseMs;

      final m = progress.mastery(q.skill);
      m.mastery = mastery.update(
        current: m.mastery,
        correct: r.correct,
        difficulty: q.difficulty,
        isReview: r.isReview,
      );

      review.onAnswered(
        progress: progress,
        question: q,
        correct: r.correct,
        now: today,
      );
    }

    // --- Badges ---
    final newBadgeIds = Badges.evaluateAndGrant(progress, bundle);
    final newBadges = newBadgeIds
        .map((id) => Badges.byId(id))
        .whereType<BadgeDef>()
        .toList();

    return LessonOutcome(
      xpGained: gained,
      correct: correctCount,
      total: total,
      stars: stars,
      leveledUp: newLevel > oldLevel,
      oldLevel: oldLevel,
      newLevel: newLevel,
      currentStreak: g.currentStreak,
      streakExtended: sr.extended,
      streakReset: sr.reset,
      dailyGoalMet: goalAfter,
      dailyGoalJustMet: goalAfter && !goalBefore,
      newBadges: newBadges,
    );
  }

  /// Difficulties helper for callers that precompute XP previews.
  List<Difficulty> difficultiesOf(List<Question> qs) =>
      qs.map((q) => q.difficulty).toList();
}
