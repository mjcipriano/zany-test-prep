import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';

import '../../app/app_controller.dart';
import '../../domain/models/question.dart';
import '../../domain/services/review_engine.dart';
import '../lessons/lesson_player.dart';

/// Plays the spaced-review queue: the most-needed missed questions first.
///
/// The session's question list is computed once when the screen opens. It
/// must not be recomputed on rebuild: completing the session updates the
/// review queue (answered items are rescheduled), and a rebuild that swapped
/// the player for the "nothing to review" state would unmount the player
/// before its summary could show.
class ReviewScreen extends ConsumerStatefulWidget {
  const ReviewScreen({super.key});

  @override
  ConsumerState<ReviewScreen> createState() => _ReviewScreenState();
}

class _ReviewScreenState extends ConsumerState<ReviewScreen> {
  List<Question>? _questions;

  @override
  void initState() {
    super.initState();
    final data = ref.read(appControllerProvider).valueOrNull;
    if (data != null) _questions = _pick(data);
  }

  static List<Question> _pick(AppData data) {
    const review = ReviewEngine();
    final ids = review.dueQuestionIds(
      data.progress,
      limit: 12,
      bundle: data.bundle,
    );
    return [
      for (final id in ids)
        if (data.bundle.question(id) != null) data.bundle.question(id)!,
    ];
  }

  @override
  Widget build(BuildContext context) {
    final questions = _questions;
    if (questions == null) {
      final data = ref.watch(appControllerProvider).valueOrNull;
      if (data == null) {
        return const Scaffold(body: Center(child: CircularProgressIndicator()));
      }
      WidgetsBinding.instance.addPostFrameCallback((_) {
        if (mounted) setState(() => _questions = _pick(data));
      });
      return const Scaffold(body: Center(child: CircularProgressIndicator()));
    }

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
