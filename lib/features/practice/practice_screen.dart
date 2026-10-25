import 'dart:math';

import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';

import '../../app/app_controller.dart';
import '../../domain/models/question.dart';
import '../../domain/services/smart_practice.dart';
import '../../domain/services/unlock_engine.dart';
import '../lessons/lesson_player.dart';
import 'sampling.dart';

/// Endless-style practice: a session of questions, one after another.
/// Three modes:
///   - 'unlocked': random, only from sections the learner has already unlocked
///   - 'all': random, from any section, including ones not yet unlocked
///   - 'smart': adaptive ([SmartPracticeSession]) — the recommender's top
///     unlocked skills (or [focusSkill]) at mastery-matched difficulty that
///     steps up/down with the learner's answers
///
/// The sample is drawn once when the screen opens (not on every rebuild), so
/// state changes while the session runs never swap the questions underneath
/// the player.
class PracticeScreen extends ConsumerStatefulWidget {
  const PracticeScreen({
    super.key,
    required this.mode,
    this.count = 15,
    this.focusSkill,
    this.rng,
  });

  final String mode; // 'unlocked' | 'all' | 'smart'
  final int count;

  /// Smart mode: the skill to spend half the session on (bare skill id).
  final String? focusSkill;

  /// Sampling randomness (tests pass a seeded one).
  final Random? rng;

  /// Smart practice sessions are a little shorter than the random modes.
  static const int smartCount = 12;

  @override
  ConsumerState<PracticeScreen> createState() => _PracticeScreenState();
}

class _PracticeScreenState extends ConsumerState<PracticeScreen> {
  List<Question>? _questions;
  SmartPracticeSession? _smart;

  String get mode => widget.mode;

  @override
  void initState() {
    super.initState();
    final data = ref.read(appControllerProvider).valueOrNull;
    if (data != null) _questions = _sample(data);
  }

  List<Question> _sample(AppData data) {
    final bundle = data.bundle;
    final rng = widget.rng ?? Random();
    if (mode == 'smart') {
      final session = SmartPracticeSession.plan(
        bundle: bundle,
        progress: data.progress,
        now: DateTime.now(),
        rng: rng,
        count: PracticeScreen.smartCount,
        focusSkill: widget.focusSkill,
      );
      _smart = session;
      return session.questions;
    }

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

    // A fresh, domain-balanced selection each time the screen is opened.
    return balancedSample(pool, widget.count, rng);
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
        if (mounted) setState(() => _questions = _sample(data));
      });
      return const Scaffold(body: Center(child: CircularProgressIndicator()));
    }

    if (questions.isEmpty) {
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

    final smart = _smart;
    return LessonPlayer(
      title: switch (mode) {
        'all' => 'Challenge Mode',
        'smart' => 'Smart Practice',
        _ => 'Quick Practice',
      },
      questions: questions,
      isReview: true,
      onAnswered: smart == null
          ? null
          : (i, result) => smart.record(i, result.correct),
      onComplete: (results) => ref
          .read(appControllerProvider.notifier)
          .completeReview(results: results),
    );
  }
}
