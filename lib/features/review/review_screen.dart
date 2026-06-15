import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';

import '../../app/app_controller.dart';
import '../../domain/models/question.dart';
import '../../domain/services/review_engine.dart';
import '../lessons/lesson_player.dart';

/// Plays the spaced-review queue: the most-needed missed questions first.
class ReviewScreen extends ConsumerWidget {
  const ReviewScreen({super.key});

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    final data = ref.watch(appControllerProvider).valueOrNull;
    if (data == null) {
      return const Scaffold(body: Center(child: CircularProgressIndicator()));
    }
    const review = ReviewEngine();
    final ids = review.dueQuestionIds(data.progress, limit: 12);
    final questions = <Question>[
      for (final id in ids)
        if (data.bundle.question(id) != null) data.bundle.question(id)!,
    ];

    if (questions.isEmpty) {
      return Scaffold(
        appBar: AppBar(title: const Text('Review')),
        body: const Center(
          child: Padding(
            padding: EdgeInsets.all(24),
            child: Text(
              'Nothing to review right now.\nMiss a question in a lesson and it '
              'will show up here for practice.',
              textAlign: TextAlign.center,
            ),
          ),
        ),
      );
    }

    return LessonPlayer(
      title: 'Review',
      questions: questions,
      isReview: true,
      onComplete: (results) => ref
          .read(appControllerProvider.notifier)
          .completeReview(results: results),
    );
  }
}
