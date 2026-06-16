/// Persisted progress, gamification, mastery, and review state.
///
/// Dates that matter only at day granularity (streaks, daily goal, review) are
/// stored as 'yyyy-MM-dd' strings to avoid timezone/precision pitfalls.
///
/// Every `fromJson` here is **defensive** (see [safe_json.dart]): missing or
/// wrongly-typed fields fall back to sane defaults instead of throwing, so the
/// app survives schema changes across updates without losing the rest of a
/// user's progress.
library;

import 'safe_json.dart';

/// Bumped only when the persisted progress shape needs a real migration.
/// Stored in [AppProgress.toJson] so future versions can detect old documents.
const int kProgressSchemaVersion = 1;

String dayKey(DateTime d) =>
    '${d.year.toString().padLeft(4, '0')}-${d.month.toString().padLeft(2, '0')}-${d.day.toString().padLeft(2, '0')}';

/// Per-lesson outcome and best score.
class LessonProgress {
  LessonProgress({
    required this.lessonId,
    this.completed = false,
    this.bestCorrect = 0,
    this.total = 0,
    this.stars = 0,
    this.timesCompleted = 0,
    this.lastCompletedDay,
  });

  final String lessonId;
  bool completed;
  int bestCorrect;
  int total;
  int stars; // 0-3 crowns
  int timesCompleted;
  String? lastCompletedDay;

  Map<String, dynamic> toJson() => {
    'lessonId': lessonId,
    'completed': completed,
    'bestCorrect': bestCorrect,
    'total': total,
    'stars': stars,
    'timesCompleted': timesCompleted,
    'lastCompletedDay': lastCompletedDay,
  };

  factory LessonProgress.fromJson(Map<String, dynamic> j) => LessonProgress(
    lessonId: asString(j['lessonId']),
    completed: asBool(j['completed']),
    bestCorrect: asInt(j['bestCorrect']),
    total: asInt(j['total']),
    stars: asInt(j['stars']),
    timesCompleted: asInt(j['timesCompleted']),
    lastCompletedDay: asStringOrNull(j['lastCompletedDay']),
  );
}

/// Aggregate stats for a single question, used by review + mastery.
class QuestionStat {
  QuestionStat({
    required this.questionId,
    this.attempts = 0,
    this.correct = 0,
    this.lastCorrect = false,
    this.totalResponseMs = 0,
  });

  final String questionId;
  int attempts;
  int correct;
  bool lastCorrect;
  int totalResponseMs;

  Map<String, dynamic> toJson() => {
    'questionId': questionId,
    'attempts': attempts,
    'correct': correct,
    'lastCorrect': lastCorrect,
    'totalResponseMs': totalResponseMs,
  };

  factory QuestionStat.fromJson(Map<String, dynamic> j) => QuestionStat(
    questionId: asString(j['questionId']),
    attempts: asInt(j['attempts']),
    correct: asInt(j['correct']),
    lastCorrect: asBool(j['lastCorrect']),
    totalResponseMs: asInt(j['totalResponseMs']),
  );
}

/// 0-100 mastery for a skill.
class SkillMastery {
  SkillMastery({required this.skillId, this.mastery = 0});

  final String skillId;
  double mastery;

  Map<String, dynamic> toJson() => {'skillId': skillId, 'mastery': mastery};

  factory SkillMastery.fromJson(Map<String, dynamic> j) => SkillMastery(
    skillId: asString(j['skillId']),
    mastery: asDouble(j['mastery']),
  );
}

/// A question queued for spaced review after being missed.
class ReviewItem {
  ReviewItem({
    required this.questionId,
    required this.skillId,
    this.priority = 3,
    this.lastReviewedDay,
    this.intervalDays = 0,
    this.ease = 2.3,
    this.dueDay,
  });

  final String questionId;
  final String skillId;
  int priority; // higher = needs review sooner
  String? lastReviewedDay;
  int intervalDays; // SM-2 interval; days until next review
  double ease; // SM-2 ease factor (>= 1.3)
  String? dueDay; // yyyy-MM-dd this item is next due

  Map<String, dynamic> toJson() => {
    'questionId': questionId,
    'skillId': skillId,
    'priority': priority,
    'lastReviewedDay': lastReviewedDay,
    'intervalDays': intervalDays,
    'ease': ease,
    'dueDay': dueDay,
  };

  factory ReviewItem.fromJson(Map<String, dynamic> j) => ReviewItem(
    questionId: asString(j['questionId']),
    skillId: asString(j['skillId']),
    priority: asInt(j['priority'], 3),
    lastReviewedDay: asStringOrNull(j['lastReviewedDay']),
    intervalDays: asInt(j['intervalDays']),
    ease: asDouble(j['ease'], 2.3),
    dueDay: asStringOrNull(j['dueDay']),
  );
}

/// Max streak freezes a player can bank at once.
const int kMaxStreakFreezes = 3;

/// XP / streak / daily-goal / badge state, plus the rewards economy.
///
/// XP has two halves: [totalXp] is **lifetime gained** and only ever grows
/// (levels, badges, and the dashboard read it), while [spentXp] tracks XP burned
/// in the store. [availableXp] is what's left to spend. This lets the player
/// unlock avatars/items without ever losing their lifetime total.
class GameState {
  GameState({
    this.totalXp = 0,
    this.spentXp = 0,
    this.currentStreak = 0,
    this.longestStreak = 0,
    this.lastActiveDay,
    this.dailyXp = 0,
    this.dailyDay,
    this.survivalBest = 0,
    this.diagnosticDone = false,
    Set<String>? earnedBadges,
    this.streakFreezes = 0,
    this.unopenedChests = 0,
    this.xpBoostDay,
    this.xpBoostMultiplier = 1.0,
    this.selectedAvatarId,
    Set<String>? ownedAssetIds,
    Map<String, String>? equipped,
  }) : earnedBadges = earnedBadges ?? <String>{},
       ownedAssetIds = ownedAssetIds ?? <String>{},
       equipped = equipped ?? <String, String>{};

  int totalXp; // lifetime XP gained (never decreases)
  int spentXp; // lifetime XP spent in the store
  int currentStreak;
  int longestStreak;
  String? lastActiveDay;
  int dailyXp;
  String? dailyDay;
  int survivalBest; // longest correct streak in Survival mode
  bool diagnosticDone;
  Set<String> earnedBadges;

  // --- Rewards economy ---
  int streakFreezes; // banked freezes, capped at [kMaxStreakFreezes]
  int unopenedChests; // chests earned (one per daily-goal day) awaiting opening
  String? xpBoostDay; // yyyy-MM-dd the XP boost is active for
  double xpBoostMultiplier; // multiplier applied on [xpBoostDay] (1.0 = none)
  String? selectedAvatarId; // null => first starter avatar
  Set<String> ownedAssetIds; // unlocked avatar/item/pet catalog ids
  Map<String, String> equipped; // slot id -> equipped asset id

  /// XP still available to spend in the store.
  int get availableXp => totalXp - spentXp;

  /// Whether an XP boost is active for [day].
  bool boostActiveOn(String day) =>
      xpBoostMultiplier > 1.0 && xpBoostDay == day;

  Map<String, dynamic> toJson() => {
    'totalXp': totalXp,
    'spentXp': spentXp,
    'currentStreak': currentStreak,
    'longestStreak': longestStreak,
    'lastActiveDay': lastActiveDay,
    'dailyXp': dailyXp,
    'dailyDay': dailyDay,
    'survivalBest': survivalBest,
    'diagnosticDone': diagnosticDone,
    'earnedBadges': earnedBadges.toList(),
    'streakFreezes': streakFreezes,
    'unopenedChests': unopenedChests,
    'xpBoostDay': xpBoostDay,
    'xpBoostMultiplier': xpBoostMultiplier,
    'selectedAvatarId': selectedAvatarId,
    'ownedAssetIds': ownedAssetIds.toList(),
    'equipped': equipped,
  };

  factory GameState.fromJson(Map<String, dynamic> j) => GameState(
    totalXp: asInt(j['totalXp']),
    spentXp: asInt(j['spentXp']),
    currentStreak: asInt(j['currentStreak']),
    longestStreak: asInt(j['longestStreak']),
    lastActiveDay: asStringOrNull(j['lastActiveDay']),
    dailyXp: asInt(j['dailyXp']),
    dailyDay: asStringOrNull(j['dailyDay']),
    survivalBest: asInt(j['survivalBest']),
    diagnosticDone: asBool(j['diagnosticDone']),
    earnedBadges: asStringList(j['earnedBadges']).toSet(),
    streakFreezes: asInt(j['streakFreezes']),
    unopenedChests: asInt(j['unopenedChests']),
    xpBoostDay: asStringOrNull(j['xpBoostDay']),
    xpBoostMultiplier: asDouble(j['xpBoostMultiplier'], 1.0),
    selectedAvatarId: asStringOrNull(j['selectedAvatarId']),
    ownedAssetIds: asStringList(j['ownedAssetIds']).toSet(),
    equipped: asMap(
      j['equipped'],
    ).map((k, v) => MapEntry(k.toString(), v.toString())),
  );
}

/// Per-day activity, used by the progress dashboard.
class DailyStat {
  DailyStat({
    required this.day,
    this.xp = 0,
    this.answered = 0,
    this.correct = 0,
  });

  final String day; // yyyy-MM-dd
  int xp;
  int answered;
  int correct;

  Map<String, dynamic> toJson() => {
    'day': day,
    'xp': xp,
    'answered': answered,
    'correct': correct,
  };

  factory DailyStat.fromJson(Map<String, dynamic> j) => DailyStat(
    day: asString(j['day']),
    xp: asInt(j['xp']),
    answered: asInt(j['answered']),
    correct: asInt(j['correct']),
  );
}

/// The whole persisted progress document.
class AppProgress {
  AppProgress({
    GameState? game,
    Map<String, LessonProgress>? lessons,
    Map<String, QuestionStat>? questionStats,
    Map<String, SkillMastery>? skillMastery,
    List<ReviewItem>? reviewQueue,
    Map<String, DailyStat>? history,
  }) : game = game ?? GameState(),
       lessons = lessons ?? {},
       questionStats = questionStats ?? {},
       skillMastery = skillMastery ?? {},
       reviewQueue = reviewQueue ?? [],
       history = history ?? {};

  final GameState game;
  final Map<String, LessonProgress> lessons;
  final Map<String, QuestionStat> questionStats;
  final Map<String, SkillMastery> skillMastery;
  final List<ReviewItem> reviewQueue;
  final Map<String, DailyStat> history;

  /// Records a day's activity into the rolling history (used by the dashboard).
  void recordDay(String day, {int xp = 0, int answered = 0, int correct = 0}) {
    final d = history.putIfAbsent(day, () => DailyStat(day: day));
    d.xp += xp;
    d.answered += answered;
    d.correct += correct;
  }

  LessonProgress lessonProgress(String lessonId) =>
      lessons.putIfAbsent(lessonId, () => LessonProgress(lessonId: lessonId));

  SkillMastery mastery(String skillId) =>
      skillMastery.putIfAbsent(skillId, () => SkillMastery(skillId: skillId));

  bool isLessonCompleted(String lessonId) =>
      lessons[lessonId]?.completed ?? false;

  Map<String, dynamic> toJson() => {
    'schema': kProgressSchemaVersion,
    'game': game.toJson(),
    'lessons': lessons.map((k, v) => MapEntry(k, v.toJson())),
    'questionStats': questionStats.map((k, v) => MapEntry(k, v.toJson())),
    'skillMastery': skillMastery.map((k, v) => MapEntry(k, v.toJson())),
    'reviewQueue': reviewQueue.map((e) => e.toJson()).toList(),
    'history': history.map((k, v) => MapEntry(k, v.toJson())),
  };

  /// Parses persisted progress, tolerating missing/garbled fields and entries.
  /// Individual bad collection entries are skipped rather than aborting the load.
  factory AppProgress.fromJson(Map<String, dynamic> j) {
    Map<String, T> parseMap<T>(
      Object? raw,
      T Function(Map<String, dynamic>) f,
    ) {
      final out = <String, T>{};
      asMap(raw).forEach((k, v) {
        if (v is Map) {
          try {
            out[k] = f(v.cast<String, dynamic>());
          } catch (_) {
            /* skip a single corrupt entry */
          }
        }
      });
      return out;
    }

    final reviewQueue = <ReviewItem>[];
    for (final e in asList(j['reviewQueue'])) {
      if (e is Map) {
        try {
          reviewQueue.add(ReviewItem.fromJson(e.cast<String, dynamic>()));
        } catch (_) {
          /* skip */
        }
      }
    }

    return AppProgress(
      game: GameState.fromJson(asMap(j['game'])),
      lessons: parseMap(j['lessons'], LessonProgress.fromJson),
      questionStats: parseMap(j['questionStats'], QuestionStat.fromJson),
      skillMastery: parseMap(j['skillMastery'], SkillMastery.fromJson),
      reviewQueue: reviewQueue,
      history: parseMap(j['history'], DailyStat.fromJson),
    );
  }
}
