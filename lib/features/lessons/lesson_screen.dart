import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:go_router/go_router.dart';

import '../../app/app_controller.dart';
import '../../app/lesson_resume_controller.dart';
import '../../design/theme.dart';
import '../../design/widgets.dart';
import '../../domain/models/lesson.dart';
import '../../domain/models/lesson_resume.dart';
import '../../domain/models/question.dart';
import 'lesson_player.dart';

enum _Start { undecided, fresh, resume }

/// Loads a lesson by id and plays it. If the student left this lesson
/// part-way, first offers to resume at the saved question or start over.
class LessonScreen extends ConsumerStatefulWidget {
  const LessonScreen({
    super.key,
    required this.lessonId,
    this.reviewMode = false,
  });

  final String lessonId;
  final bool reviewMode;

  @override
  ConsumerState<LessonScreen> createState() => _LessonScreenState();
}

class _LessonScreenState extends ConsumerState<LessonScreen> {
  // Decided once on entry; the per-answer saves that follow must not bring
  // the prompt back.
  _Start _start = _Start.undecided;
  LessonResume? _resume;

  @override
  Widget build(BuildContext context) {
    final data = ref.watch(appControllerProvider).valueOrNull;
    final book = ref.watch(lessonResumeProvider).valueOrNull;
    if (data == null || book == null) {
      return const Scaffold(body: Center(child: CircularProgressIndicator()));
    }
    final lesson = data.bundle.lesson(widget.lessonId);
    if (lesson == null) {
      return Scaffold(
        appBar: AppBar(),
        body: const Center(child: Text('Lesson not found.')),
      );
    }
    final questions = data.bundle.questionsFor(lesson);
    if (questions.isEmpty) {
      return Scaffold(
        appBar: AppBar(title: Text(lesson.title)),
        body: const Center(child: Text('This lesson has no questions yet.')),
      );
    }
    final examId = data.bundle.exam.id;
    if (_start == _Start.undecided) {
      final saved = book.get(examId, lesson.id);
      if (saved != null && saved.isValidFor(lesson.id, questions)) {
        _resume = saved;
        return LessonResumePrompt(
          lesson: lesson,
          skillName: data.bundle.skillName(lesson.skill),
          resume: saved,
          onResume: () => setState(() => _start = _Start.resume),
          onStartOver: () {
            _discard(examId, lesson.id);
            setState(() {
              _resume = null;
              _start = _Start.fresh;
            });
          },
        );
      }
      // Stale (content changed since it was saved) or absent: start fresh.
      if (saved != null) _discard(examId, lesson.id);
      _start = _Start.fresh;
    }
    return _player(
      examId,
      lesson,
      questions,
      data.bundle.skillName(lesson.skill),
    );
  }

  void _discard(String examId, String lessonId) =>
      ref.read(lessonResumeProvider.notifier).clear(examId, lessonId);

  Widget _player(
    String examId,
    Lesson lesson,
    List<Question> questions,
    String title,
  ) {
    final fingerprint = lessonFingerprint(lesson.id, questions);
    return LessonPlayer(
      title: title,
      teachingCard: lesson.teachingCard,
      questions: questions,
      resumeFrom: _start == _Start.resume ? _resume?.attempt : null,
      onProgress: (attempt) => ref
          .read(lessonResumeProvider.notifier)
          .save(
            LessonResume(
              examId: examId,
              lessonId: lesson.id,
              fingerprint: fingerprint,
              total: questions.length,
              attempt: attempt,
              updatedAt: DateTime.now(),
            ),
          ),
      onComplete: (results) => ref
          .read(appControllerProvider.notifier)
          .completeLesson(lesson: lesson, results: results),
    );
  }
}

/// "Welcome back" screen shown when re-entering a lesson left part-way:
/// resume at the saved question or start over.
class LessonResumePrompt extends StatelessWidget {
  const LessonResumePrompt({
    super.key,
    required this.lesson,
    required this.skillName,
    required this.resume,
    required this.onResume,
    required this.onStartOver,
  });

  final Lesson lesson;
  final String skillName;
  final LessonResume resume;
  final VoidCallback onResume;
  final VoidCallback onStartOver;

  @override
  Widget build(BuildContext context) {
    final scheme = Theme.of(context).colorScheme;
    final text = Theme.of(context).textTheme;
    final answered = resume.answeredCount;
    final total = resume.total;
    final correct = resume.attempt.correctCount;
    return Scaffold(
      body: SafeArea(
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.stretch,
          children: [
            Align(
              alignment: Alignment.centerLeft,
              child: Padding(
                padding: const EdgeInsets.fromLTRB(12, 8, 12, 0),
                child: IconButton(
                  tooltip: 'Close',
                  icon: const Icon(Icons.close_rounded),
                  onPressed: () => context.pop(),
                ),
              ),
            ),
            Expanded(
              child: ListView(
                padding: kPagePadding,
                children: [
                  Gap.l,
                  Center(
                    child: CircleAvatar(
                      radius: 40,
                      backgroundColor: scheme.primaryContainer,
                      child: Icon(
                        Icons.bookmark_rounded,
                        size: 40,
                        color: scheme.primary,
                      ),
                    ),
                  ),
                  Gap.l,
                  Text(
                    'Welcome back!',
                    textAlign: TextAlign.center,
                    style: text.headlineSmall?.copyWith(
                      fontWeight: FontWeight.w800,
                    ),
                  ),
                  Gap.s,
                  Text(
                    'You were partway through this lesson.',
                    textAlign: TextAlign.center,
                    style: text.bodyLarge,
                  ),
                  Gap.l,
                  AppCard(
                    child: Column(
                      crossAxisAlignment: CrossAxisAlignment.start,
                      children: [
                        Text(
                          skillName,
                          style: text.labelLarge?.copyWith(
                            color: scheme.primary,
                            fontWeight: FontWeight.w800,
                          ),
                        ),
                        Text(
                          lesson.title,
                          style: const TextStyle(
                            fontWeight: FontWeight.w800,
                            fontSize: 18,
                          ),
                        ),
                        Gap.m,
                        ProgressBar(value: total == 0 ? 0 : answered / total),
                        Gap.s,
                        Text(
                          answered == 0
                              ? 'No questions answered yet'
                              : '$answered of $total answered · $correct correct',
                          style: text.bodyMedium?.copyWith(
                            color: scheme.onSurfaceVariant,
                          ),
                        ),
                      ],
                    ),
                  ),
                ],
              ),
            ),
            Padding(
              padding: kPagePadding,
              child: Column(
                crossAxisAlignment: CrossAxisAlignment.stretch,
                children: [
                  FilledButton.icon(
                    onPressed: onResume,
                    icon: const Icon(Icons.play_arrow_rounded),
                    label: Text(
                      'Resume (question ${resume.resumeQuestionNumber} of $total)',
                    ),
                  ),
                  Gap.s,
                  OutlinedButton.icon(
                    onPressed: onStartOver,
                    icon: const Icon(Icons.replay_rounded),
                    label: const Text('Start over'),
                  ),
                ],
              ),
            ),
          ],
        ),
      ),
    );
  }
}
