import 'dart:math';

import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';

import '../../app/app_controller.dart';
import '../../domain/models/question.dart';
import '../../domain/services/unlock_engine.dart';
import '../lessons/lesson_player.dart';
import 'sampling.dart';

/// Endless-style practice: a session of random questions, one after another.
/// Two modes:
///   - 'unlocked': only from sections the learner has already unlocked
///   - 'all': from any section, including ones not yet unlocked
class PracticeScreen extends ConsumerWidget {
  const PracticeScreen({super.key, required this.mode, this.count = 15});

  final String mode; // 'unlocked' | 'all'
  final int count;

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    final data = ref.watch(appControllerProvider).valueOrNull;
    if (data == null) {
      return const Scaffold(body: Center(child: CircularProgressIndicator()));
    }
    final bundle = data.bundle;

    final List<Question> pool;
    if (mode == 'all') {
      pool = [...bundle.questions];
    } else {
      // All questions (lesson + practice bank) whose owning lesson is unlocked.
      const unlock = UnlockEngine();
      final unlockedLessons = <String, bool>{};
      bool lessonUnlocked(String lessonId) =>
          unlockedLessons.putIfAbsent(lessonId, () {
            final l = bundle.lesson(lessonId);
            return l != null && unlock.isUnlocked(l, data.progress);
          });
      pool = bundle.questions.where((q) => lessonUnlocked(q.lessonId)).toList();
    }

    if (pool.isEmpty) {
      return Scaffold(
        appBar: AppBar(title: const Text('Practice')),
        body: const Center(
          child: Padding(
            padding: EdgeInsets.all(24),
            child: Text(
              'No questions available yet. Complete a lesson first.',
              textAlign: TextAlign.center,
            ),
          ),
        ),
      );
    }

    // A fresh, domain-balanced selection each time the screen is opened.
    final questions = balancedSample(pool, count, Random());

    return LessonPlayer(
      title: mode == 'all' ? 'Challenge Mode' : 'Quick Practice',
      questions: questions,
      isReview: true,
      onComplete: (results) => ref
          .read(appControllerProvider.notifier)
          .completeReview(results: results),
    );
  }
}
