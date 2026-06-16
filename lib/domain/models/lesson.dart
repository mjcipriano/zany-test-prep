import 'difficulty.dart';

/// One screen of a mini-lesson: a heading, explanatory body, optional bullet
/// take-aways, and an optional worked example.
class TeachingScreen {
  const TeachingScreen({
    required this.title,
    required this.body,
    this.keyPoints = const [],
    this.workedExample,
  });

  final String title;
  final String body;
  final List<String> keyPoints;
  final String? workedExample;

  factory TeachingScreen.fromJson(Map<String, dynamic> json) => TeachingScreen(
    title: json['title'] as String,
    body: json['body'] as String,
    keyPoints: ((json['key_points'] as List?) ?? const [])
        .map((e) => e.toString())
        .toList(),
    workedExample: json['worked_example'] as String?,
  );
}

/// The concept explanation shown before a lesson's questions. Renders as a
/// 2-5 screen mini-lesson ([screens]); when a lesson only provides the legacy
/// single card, [screens] is a one-element list built from it, so old content
/// keeps working.
class TeachingCard {
  const TeachingCard({
    required this.title,
    required this.body,
    required this.keyPoints,
    this.workedExample,
    List<TeachingScreen>? screens,
  }) : _screens = screens;

  final String title;
  final String body;
  final List<String> keyPoints;
  final String? workedExample;
  final List<TeachingScreen>? _screens;

  /// The screens to page through (always at least one).
  List<TeachingScreen> get screens =>
      _screens ??
      [
        TeachingScreen(
          title: title,
          body: body,
          keyPoints: keyPoints,
          workedExample: workedExample,
        ),
      ];

  factory TeachingCard.fromJson(Map<String, dynamic> json) => TeachingCard(
    title: json['title'] as String,
    body: json['body'] as String,
    keyPoints: (json['key_points'] as List).map((e) => e.toString()).toList(),
    workedExample: json['worked_example'] as String?,
    screens: (json['screens'] as List?)
        ?.map((e) => TeachingScreen.fromJson((e as Map).cast<String, dynamic>()))
        .toList(),
  );
}

/// A Duolingo-style lesson: a teaching card plus 8-25 questions.
class Lesson {
  const Lesson({
    required this.id,
    required this.examId,
    required this.domain,
    required this.section,
    required this.skill,
    required this.title,
    required this.order,
    required this.difficulty,
    required this.estimatedMinutes,
    required this.teachingCard,
    required this.questionIds,
    required this.prerequisiteLessonIds,
    required this.unlockXp,
    required this.tags,
  });

  final String id;
  final String examId;
  final String domain;
  final String section;
  final String skill;
  final String title;
  final int order;
  final Difficulty difficulty;
  final int estimatedMinutes;
  final TeachingCard teachingCard;
  final List<String> questionIds;
  final List<String> prerequisiteLessonIds;
  final int unlockXp;
  final List<String> tags;

  bool get isMath => domain == 'math';

  factory Lesson.fromJson(Map<String, dynamic> json) => Lesson(
    id: json['lesson_id'] as String,
    examId: json['exam_id'] as String,
    domain: json['domain'] as String,
    section: json['section'] as String,
    skill: json['skill'] as String,
    title: json['title'] as String,
    order: json['order'] as int,
    difficulty: Difficulty.parse(json['difficulty'] as String?),
    estimatedMinutes: json['estimated_minutes'] as int,
    teachingCard: TeachingCard.fromJson(
      json['teaching_card'] as Map<String, dynamic>,
    ),
    questionIds: (json['question_ids'] as List)
        .map((e) => e.toString())
        .toList(),
    prerequisiteLessonIds:
        (json['prerequisite_lesson_ids'] as List? ?? const [])
            .map((e) => e.toString())
            .toList(),
    unlockXp: json['unlock_xp'] as int? ?? 0,
    tags: (json['tags'] as List? ?? const []).map((e) => e.toString()).toList(),
  );
}
