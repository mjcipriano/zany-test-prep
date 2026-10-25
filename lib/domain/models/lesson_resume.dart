import 'question.dart';
import 'safe_json.dart';

/// Schema stamp written into the `lessonResume.v1` document (see
/// docs/persistence.md). Parsing is field-tolerant, like the other documents.
const int kLessonResumeSchemaVersion = 1;

/// How many in-progress lessons are kept at once; the least recently touched
/// ones are dropped beyond this so the document stays small.
const int kMaxSavedLessons = 20;

/// One answer given during an in-progress lesson. Stores what the student
/// picked/typed so the feedback view can be restored exactly.
class SavedAnswer {
  const SavedAnswer({
    required this.questionId,
    required this.correct,
    this.responseMs = 0,
    this.choiceId,
    this.produced,
  });

  final String questionId;
  final bool correct;
  final int responseMs;

  /// The selected choice for choice questions; null for grid-ins.
  final String? choiceId;

  /// The typed answer for student-produced (grid-in) questions.
  final String? produced;

  Map<String, dynamic> toJson() => {
    'id': questionId,
    'correct': correct,
    'ms': responseMs,
    if (choiceId != null) 'choice': choiceId,
    if (produced != null) 'text': produced,
  };

  static SavedAnswer? fromJson(Object? raw) {
    final json = asMap(raw);
    final id = asString(json['id']);
    if (id.isEmpty) return null;
    return SavedAnswer(
      questionId: id,
      correct: asBool(json['correct']),
      responseMs: asInt(json['ms']),
      choiceId: asStringOrNull(json['choice']),
      produced: asStringOrNull(json['text']),
    );
  }
}

/// The player-level state of a lesson attempt: what the student has done so
/// far. This is everything [LessonPlayer] needs to pick up where it left off.
class LessonAttempt {
  const LessonAttempt({
    required this.teachingDone,
    required this.index,
    required this.answers,
    required this.startedAt,
  });

  /// Whether the teaching card was paged through (resume skips it).
  final bool teachingDone;

  /// 0-based index of the current question.
  final int index;

  /// Answers in question order. Holds [index] entries, or [index] + 1 when the
  /// current question was checked but "Continue" not yet tapped (resume then
  /// shows that question's feedback again).
  final List<SavedAnswer> answers;

  /// When the attempt began (first entered the quiz).
  final DateTime startedAt;

  int get correctCount => answers.where((a) => a.correct).length;

  /// The current question was answered but not yet moved past.
  bool get showingFeedback => answers.length > index;
}

/// A persisted in-progress lesson, keyed by exam + lesson id.
///
/// [fingerprint] hashes the lesson's question ids, order, and answer-bearing
/// content at save time; if the shipped content changes the saved attempt no
/// longer matches and is discarded instead of resumed onto different
/// questions (see [isValidFor]).
class LessonResume {
  const LessonResume({
    required this.examId,
    required this.lessonId,
    required this.fingerprint,
    required this.total,
    required this.attempt,
    required this.updatedAt,
  });

  final String examId;
  final String lessonId;
  final String fingerprint;

  /// Number of questions in the lesson when saved.
  final int total;
  final LessonAttempt attempt;
  final DateTime updatedAt;

  String get key => keyFor(examId, lessonId);

  static String keyFor(String examId, String lessonId) => '$examId/$lessonId';

  /// 1-based question number the student resumes at.
  int get resumeQuestionNumber => attempt.index + 1;

  int get answeredCount => attempt.answers.length;

  /// Whether this saved attempt can be resumed against the lesson's current
  /// [questions] (in play order). False when the content changed since it was
  /// saved or the stored data is inconsistent.
  bool isValidFor(String lessonId, List<Question> questions) {
    if (lessonId != this.lessonId || questions.length != total) return false;
    if (fingerprint != lessonFingerprint(lessonId, questions)) return false;
    final answers = attempt.answers;
    final index = attempt.index;
    if (index < 0 || index >= total) return false;
    if (answers.length != index && answers.length != index + 1) return false;
    for (var i = 0; i < answers.length; i++) {
      if (answers[i].questionId != questions[i].id) return false;
    }
    return true;
  }

  Map<String, dynamic> toJson() => {
    'exam': examId,
    'lesson': lessonId,
    'fp': fingerprint,
    'total': total,
    'teachingDone': attempt.teachingDone,
    'index': attempt.index,
    'answers': attempt.answers.map((a) => a.toJson()).toList(),
    'startedAt': attempt.startedAt.toIso8601String(),
    'updatedAt': updatedAt.toIso8601String(),
  };

  /// Returns null for an entry too broken to identify (no exam/lesson id).
  static LessonResume? fromJson(Object? raw) {
    final json = asMap(raw);
    final exam = asString(json['exam']);
    final lesson = asString(json['lesson']);
    if (exam.isEmpty || lesson.isEmpty) return null;
    final epoch = DateTime.fromMillisecondsSinceEpoch(0);
    return LessonResume(
      examId: exam,
      lessonId: lesson,
      fingerprint: asString(json['fp']),
      total: asInt(json['total']),
      attempt: LessonAttempt(
        teachingDone: asBool(json['teachingDone']),
        index: asInt(json['index']),
        answers: asList(
          json['answers'],
        ).map(SavedAnswer.fromJson).whereType<SavedAnswer>().toList(),
        startedAt: DateTime.tryParse(asString(json['startedAt'])) ?? epoch,
      ),
      updatedAt: DateTime.tryParse(asString(json['updatedAt'])) ?? epoch,
    );
  }
}

/// All saved in-progress lessons (immutable; edits return a new book).
class LessonResumeBook {
  const LessonResumeBook([this.entries = const {}]);

  /// Keyed by [LessonResume.keyFor].
  final Map<String, LessonResume> entries;

  bool get isEmpty => entries.isEmpty;

  LessonResume? get(String examId, String lessonId) =>
      entries[LessonResume.keyFor(examId, lessonId)];

  /// Adds/replaces [resume], dropping the oldest entries beyond
  /// [kMaxSavedLessons].
  LessonResumeBook put(LessonResume resume) {
    final next = {...entries, resume.key: resume};
    if (next.length > kMaxSavedLessons) {
      final oldest = next.values.toList()
        ..sort((a, b) => a.updatedAt.compareTo(b.updatedAt));
      for (final r in oldest.take(next.length - kMaxSavedLessons)) {
        next.remove(r.key);
      }
    }
    return LessonResumeBook(next);
  }

  LessonResumeBook remove(String examId, String lessonId) {
    final key = LessonResume.keyFor(examId, lessonId);
    if (!entries.containsKey(key)) return this;
    return LessonResumeBook({...entries}..remove(key));
  }

  Map<String, dynamic> toJson() => {
    'schema': kLessonResumeSchemaVersion,
    'lessons': entries.values.map((r) => r.toJson()).toList(),
  };

  /// Defensive: a corrupt entry is skipped rather than failing the load.
  factory LessonResumeBook.fromJson(Map<String, dynamic> json) {
    final map = <String, LessonResume>{};
    for (final raw in asList(json['lessons'])) {
      final r = LessonResume.fromJson(raw);
      if (r != null) map[r.key] = r;
    }
    return LessonResumeBook(map);
  }
}

/// A stable hash of the parts of a lesson's questions that make a saved
/// attempt meaningful: ids and order, prompts, choices, and answer keys. A
/// change to any of them invalidates in-progress state for that lesson.
///
/// FNV-1a (32-bit) over a canonical string, so it is identical across runs and
/// platforms (unlike [String.hashCode]).
String lessonFingerprint(String lessonId, List<Question> questions) {
  final buf = StringBuffer(lessonId);
  for (final q in questions) {
    buf
      ..write('\u0001')
      ..write(q.id)
      ..write('\u0002')
      ..write(q.prompt)
      ..write('\u0002')
      ..write(q.correctChoice ?? '');
    for (final c in q.choices) {
      buf
        ..write('\u0003')
        ..write(c.id)
        ..write('=')
        ..write(c.text);
    }
    final answer = q.answer;
    if (answer != null) {
      buf
        ..write('\u0004')
        ..write(answer.accepted.join('|'))
        ..write('~')
        ..write(answer.value ?? '')
        ..write('~')
        ..write(answer.tolerance);
    }
  }
  var hash = 0x811c9dc5;
  for (final unit in buf.toString().codeUnits) {
    hash ^= unit;
    // hash * 0x01000193 split as (hash * 0x193) + (hash << 24) so the
    // intermediate stays exact on the web (53-bit doubles) too.
    hash = (hash * 0x193 + ((hash << 24) & 0xffffffff)) & 0xffffffff;
  }
  return hash.toRadixString(16).padLeft(8, '0');
}
