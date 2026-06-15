import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';

import '../../app/app_controller.dart';
import 'lesson_player.dart';

/// Loads a lesson by id and plays it.
class LessonScreen extends ConsumerWidget {
  const LessonScreen({
    super.key,
    required this.lessonId,
    this.reviewMode = false,
  });

  final String lessonId;
  final bool reviewMode;

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    final data = ref.watch(appControllerProvider).valueOrNull;
    if (data == null) {
      return const Scaffold(body: Center(child: CircularProgressIndicator()));
    }
    final lesson = data.bundle.lesson(lessonId);
    if (lesson == null) {
      return Scaffold(
        appBar: AppBar(),
        body: const Center(child: Text('Lesson not found.')),
      );
    }
    final questions = data.bundle.questionsFor(lesson);
    return LessonPlayer(
      title: data.bundle.skillName(lesson.skill),
      teachingCard: lesson.teachingCard,
      questions: questions,
      onComplete: (results) => ref
          .read(appControllerProvider.notifier)
          .completeLesson(lesson: lesson, results: results),
    );
  }
}
