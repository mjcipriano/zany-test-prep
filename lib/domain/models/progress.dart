/// Persisted progress, gamification, mastery, and review state.
///
/// Dates that matter only at day granularity (streaks, daily goal, review) are
/// stored as 'yyyy-MM-dd' strings to avoid timezone/precision pitfalls.
library;

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
        lessonId: j['lessonId'] as String,
        completed: j['completed'] as bool? ?? false,
        bestCorrect: j['bestCorrect'] as int? ?? 0,
        total: j['total'] as int? ?? 0,
        stars: j['stars'] as int? ?? 0,
        timesCompleted: j['timesCompleted'] as int? ?? 0,
        lastCompletedDay: j['lastCompletedDay'] as String?,
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
        questionId: j['questionId'] as String,
        attempts: j['attempts'] as int? ?? 0,
        correct: j['correct'] as int? ?? 0,
        lastCorrect: j['lastCorrect'] as bool? ?? false,
        totalResponseMs: j['totalResponseMs'] as int? ?? 0,
      );
}

/// 0-100 mastery for a skill.
class SkillMastery {
  SkillMastery({required this.skillId, this.mastery = 0});

  final String skillId;
  double mastery;

  Map<String, dynamic> toJson() => {'skillId': skillId, 'mastery': mastery};

  factory SkillMastery.fromJson(Map<String, dynamic> j) => SkillMastery(
        skillId: j['skillId'] as String,
        mastery: (j['mastery'] as num?)?.toDouble() ?? 0,
      );
}

/// A question queued for spaced review after being missed.
class ReviewItem {
  ReviewItem({
    required this.questionId,
    required this.skillId,
    this.priority = 3,
    this.lastReviewedDay,
  });

  final String questionId;
  final String skillId;
  int priority; // higher = needs review sooner
  String? lastReviewedDay;

  Map<String, dynamic> toJson() => {
        'questionId': questionId,
        'skillId': skillId,
        'priority': priority,
        'lastReviewedDay': lastReviewedDay,
      };

  factory ReviewItem.fromJson(Map<String, dynamic> j) => ReviewItem(
        questionId: j['questionId'] as String,
        skillId: j['skillId'] as String,
        priority: j['priority'] as int? ?? 3,
        lastReviewedDay: j['lastReviewedDay'] as String?,
      );
}

/// XP / streak / daily-goal / badge state.
class GameState {
  GameState({
    this.totalXp = 0,
    this.currentStreak = 0,
    this.longestStreak = 0,
    this.lastActiveDay,
    this.dailyXp = 0,
    this.dailyDay,
    Set<String>? earnedBadges,
  }) : earnedBadges = earnedBadges ?? <String>{};

  int totalXp;
  int currentStreak;
  int longestStreak;
  String? lastActiveDay;
  int dailyXp;
  String? dailyDay;
  Set<String> earnedBadges;

  Map<String, dynamic> toJson() => {
        'totalXp': totalXp,
        'currentStreak': currentStreak,
        'longestStreak': longestStreak,
        'lastActiveDay': lastActiveDay,
        'dailyXp': dailyXp,
        'dailyDay': dailyDay,
        'earnedBadges': earnedBadges.toList(),
      };

  factory GameState.fromJson(Map<String, dynamic> j) => GameState(
        totalXp: j['totalXp'] as int? ?? 0,
        currentStreak: j['currentStreak'] as int? ?? 0,
        longestStreak: j['longestStreak'] as int? ?? 0,
        lastActiveDay: j['lastActiveDay'] as String?,
        dailyXp: j['dailyXp'] as int? ?? 0,
        dailyDay: j['dailyDay'] as String?,
        earnedBadges:
            (j['earnedBadges'] as List? ?? const []).map((e) => e.toString()).toSet(),
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
  })  : game = game ?? GameState(),
        lessons = lessons ?? {},
        questionStats = questionStats ?? {},
        skillMastery = skillMastery ?? {},
        reviewQueue = reviewQueue ?? [];

  final GameState game;
  final Map<String, LessonProgress> lessons;
  final Map<String, QuestionStat> questionStats;
  final Map<String, SkillMastery> skillMastery;
  final List<ReviewItem> reviewQueue;

  LessonProgress lessonProgress(String lessonId) =>
      lessons.putIfAbsent(lessonId, () => LessonProgress(lessonId: lessonId));

  SkillMastery mastery(String skillId) =>
      skillMastery.putIfAbsent(skillId, () => SkillMastery(skillId: skillId));

  bool isLessonCompleted(String lessonId) =>
      lessons[lessonId]?.completed ?? false;

  Map<String, dynamic> toJson() => {
        'game': game.toJson(),
        'lessons': lessons.map((k, v) => MapEntry(k, v.toJson())),
        'questionStats':
            questionStats.map((k, v) => MapEntry(k, v.toJson())),
        'skillMastery': skillMastery.map((k, v) => MapEntry(k, v.toJson())),
        'reviewQueue': reviewQueue.map((e) => e.toJson()).toList(),
      };

  factory AppProgress.fromJson(Map<String, dynamic> j) => AppProgress(
        game: GameState.fromJson(
            (j['game'] as Map?)?.cast<String, dynamic>() ?? const {}),
        lessons: ((j['lessons'] as Map?) ?? const {}).map(
          (k, v) => MapEntry(
              k as String, LessonProgress.fromJson((v as Map).cast<String, dynamic>())),
        ),
        questionStats: ((j['questionStats'] as Map?) ?? const {}).map(
          (k, v) => MapEntry(
              k as String, QuestionStat.fromJson((v as Map).cast<String, dynamic>())),
        ),
        skillMastery: ((j['skillMastery'] as Map?) ?? const {}).map(
          (k, v) => MapEntry(
              k as String, SkillMastery.fromJson((v as Map).cast<String, dynamic>())),
        ),
        reviewQueue: ((j['reviewQueue'] as List?) ?? const [])
            .map((e) => ReviewItem.fromJson((e as Map).cast<String, dynamic>()))
            .toList(),
      );
}
