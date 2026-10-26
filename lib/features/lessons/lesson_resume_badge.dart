import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';

import '../../app/app_controller.dart';
import '../../app/lesson_resume_controller.dart';
import '../../domain/models/lesson.dart';

/// Small "In progress · question 7 of 12" line for a lesson on the path when
/// the student left it part-way. Renders nothing otherwise, and also nothing
/// for a stale save the lesson would discard on open (content changed).
class LessonResumeBadge extends ConsumerWidget {
  const LessonResumeBadge({super.key, required this.lesson});

  final Lesson lesson;

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    final book = ref.watch(lessonResumeProvider).valueOrNull;
    final bundle = ref.watch(appControllerProvider).valueOrNull?.bundle;
    if (book == null || bundle == null) return const SizedBox.shrink();
    final saved = book.get(bundle.exam.id, lesson.id);
    if (saved == null ||
        !saved.isValidFor(lesson.id, bundle.questionsFor(lesson))) {
      return const SizedBox.shrink();
    }
    final color = Theme.of(context).colorScheme.primary;
    return Padding(
      padding: const EdgeInsets.only(top: 2),
      child: Row(
        mainAxisSize: MainAxisSize.min,
        children: [
          Icon(Icons.bookmark_rounded, size: 14, color: color),
          const SizedBox(width: 4),
          Flexible(
            child: Text(
              'In progress · question ${saved.resumeQuestionNumber} '
              'of ${saved.total}',
              overflow: TextOverflow.ellipsis,
              style: TextStyle(
                color: color,
                fontWeight: FontWeight.w700,
                fontSize: 12.5,
              ),
            ),
          ),
        ],
      ),
    );
  }
}
