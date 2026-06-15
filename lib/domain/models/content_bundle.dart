import 'exam.dart';
import 'lesson.dart';
import 'question.dart';
import 'skill.dart';

/// A fully parsed exam content bundle, ready for the app to use offline.
class ContentBundle {
  ContentBundle({
    required this.exam,
    required this.skillMap,
    required this.lessons,
    required this.questions,
  }) : _questionsById = {for (final q in questions) q.id: q},
       _lessonsById = {for (final l in lessons) l.id: l};

  final Exam exam;
  final SkillMap skillMap;
  final List<Lesson> lessons;
  final List<Question> questions;

  final Map<String, Question> _questionsById;
  final Map<String, Lesson> _lessonsById;

  Question? question(String id) => _questionsById[id];
  Lesson? lesson(String id) => _lessonsById[id];

  List<Question> questionsFor(Lesson lesson) => [
    for (final id in lesson.questionIds)
      if (_questionsById[id] != null) _questionsById[id]!,
  ];

  List<Lesson> lessonsForDomain(String domain) =>
      lessons.where((l) => l.domain == domain).toList()
        ..sort((a, b) => a.order.compareTo(b.order));

  String skillName(String skillId) => skillMap.nameFor(skillId);

  factory ContentBundle.fromJson(Map<String, dynamic> json) {
    final lessons = (json['lessons'] as List)
        .map((e) => Lesson.fromJson(e as Map<String, dynamic>))
        .toList();
    final questions = (json['questions'] as List)
        .map((e) => Question.fromJson(e as Map<String, dynamic>))
        .toList();
    return ContentBundle(
      exam: Exam.fromJson(json['exam'] as Map<String, dynamic>),
      skillMap: SkillMap.fromJson(json['skills'] as Map<String, dynamic>),
      lessons: lessons,
      questions: questions,
    );
  }
}
