import 'difficulty.dart';

/// The kind of question, which controls how it is rendered and answered.
enum QuestionType {
  multipleChoice,
  studentProduced,
  passageReading,
  grammarEditing,
  dataInterpretation,
  multiStepMath;

  static QuestionType parse(String value) {
    switch (value) {
      case 'multiple_choice':
        return QuestionType.multipleChoice;
      case 'student_produced':
        return QuestionType.studentProduced;
      case 'passage_reading':
        return QuestionType.passageReading;
      case 'grammar_editing':
        return QuestionType.grammarEditing;
      case 'data_interpretation':
        return QuestionType.dataInterpretation;
      case 'multi_step_math':
        return QuestionType.multiStepMath;
      default:
        return QuestionType.multipleChoice;
    }
  }

  bool get isStudentProduced => this == QuestionType.studentProduced;
}

/// A single answer choice for a multiple-choice-style question.
class Choice {
  const Choice({required this.id, required this.text, required this.rationale});

  final String id;
  final String text;
  final String rationale;

  factory Choice.fromJson(Map<String, dynamic> json) => Choice(
    id: json['id'] as String,
    text: json['text'] as String,
    rationale: json['rationale'] as String? ?? '',
  );
}

/// Optional supporting material shown above the question (passage or table).
class Stimulus {
  const Stimulus({
    required this.type,
    this.title,
    this.text,
    this.textB,
    this.table,
    this.figure,
  });

  /// 'passage', 'table', 'paired_passages', or 'figure'.
  final String type;
  final String? title;
  final String? text;
  final String? textB;
  final StimulusTable? table;

  /// Declarative diagram spec (kind + params) for `type == 'figure'`.
  final Map<String, dynamic>? figure;

  bool get isPaired => type == 'paired_passages';
  bool get isTable => type == 'table';
  bool get isFigure => type == 'figure';

  factory Stimulus.fromJson(Map<String, dynamic> json) => Stimulus(
    type: json['type'] as String,
    title: json['title'] as String?,
    text: json['text'] as String?,
    textB: json['text_b'] as String?,
    table: json['table'] == null
        ? null
        : StimulusTable.fromJson(json['table'] as Map<String, dynamic>),
    figure: (json['figure'] as Map?)?.cast<String, dynamic>(),
  );
}

class StimulusTable {
  const StimulusTable({
    this.caption,
    required this.headers,
    required this.rows,
  });

  final String? caption;
  final List<String> headers;
  final List<List<String>> rows;

  factory StimulusTable.fromJson(Map<String, dynamic> json) => StimulusTable(
    caption: json['caption'] as String?,
    headers: (json['headers'] as List).map((e) => e.toString()).toList(),
    rows: (json['rows'] as List)
        .map((r) => (r as List).map((e) => e.toString()).toList())
        .toList(),
  );
}

/// A numeric/string answer for student-produced (grid-in) questions.
class ProducedAnswer {
  const ProducedAnswer({
    required this.type,
    this.value,
    required this.accepted,
    this.tolerance = 0,
  });

  /// 'numeric' or 'string'.
  final String type;
  final num? value;
  final List<String> accepted;
  final double tolerance;

  bool get isNumeric => type == 'numeric';

  factory ProducedAnswer.fromJson(Map<String, dynamic> json) => ProducedAnswer(
    type: json['type'] as String,
    value: json['value'] as num?,
    accepted: (json['accepted'] as List).map((e) => e.toString()).toList(),
    tolerance: (json['tolerance'] as num?)?.toDouble() ?? 0,
  );
}

/// An exam question. Exam-agnostic: SAT now, ACT/AP later.
class Question {
  const Question({
    required this.id,
    required this.examId,
    required this.domain,
    required this.section,
    required this.skill,
    this.subskill,
    required this.lessonId,
    required this.difficulty,
    required this.type,
    required this.estimatedTimeSeconds,
    required this.prompt,
    required this.explanation,
    required this.tags,
    this.stimulus,
    this.choices = const [],
    this.correctChoice,
    this.answer,
    this.answerVerification,
  });

  final String id;
  final String examId;
  final String domain;
  final String section;
  final String skill;
  final String? subskill;
  final String lessonId;
  final Difficulty difficulty;
  final QuestionType type;
  final int estimatedTimeSeconds;
  final String prompt;
  final String explanation;
  final List<String> tags;
  final Stimulus? stimulus;
  final List<Choice> choices;
  final String? correctChoice;
  final ProducedAnswer? answer;
  final String? answerVerification;

  factory Question.fromJson(Map<String, dynamic> json) => Question(
    id: json['question_id'] as String,
    examId: json['exam_id'] as String,
    domain: json['domain'] as String,
    section: json['section'] as String,
    skill: json['skill'] as String,
    subskill: json['subskill'] as String?,
    lessonId: json['lesson_id'] as String,
    difficulty: Difficulty.parse(json['difficulty'] as String?),
    type: QuestionType.parse(json['question_type'] as String),
    estimatedTimeSeconds: json['estimated_time_seconds'] as int,
    prompt: json['prompt'] as String,
    explanation: json['explanation'] as String,
    tags:
        (json['tags'] as List?)?.map((e) => e.toString()).toList() ?? const [],
    stimulus: json['stimulus'] == null
        ? null
        : Stimulus.fromJson(json['stimulus'] as Map<String, dynamic>),
    choices:
        (json['choices'] as List?)
            ?.map((e) => Choice.fromJson(e as Map<String, dynamic>))
            .toList() ??
        const [],
    correctChoice: json['correct_choice'] as String?,
    answer: json['answer'] == null
        ? null
        : ProducedAnswer.fromJson(json['answer'] as Map<String, dynamic>),
    answerVerification: json['answer_verification'] as String?,
  );

  Choice? get correct {
    for (final c in choices) {
      if (c.id == correctChoice) return c;
    }
    return null;
  }
}
