import 'dart:math';

import 'package:flutter/material.dart';
import 'package:flutter/services.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:go_router/go_router.dart';

import '../../app/app_controller.dart';
import '../../core/sound_service.dart';
import '../../design/theme.dart';
import '../../design/widgets.dart';
import '../../domain/models/question.dart';
import '../../domain/services/answer_checker.dart';
import '../../domain/services/game_service.dart';
import '../lessons/question_view.dart';
import 'sampling.dart';

/// Survival mode: answer questions one after another from any section. The run
/// ends the moment you miss one. Your longest correct streak is recorded.
class SurvivalScreen extends ConsumerStatefulWidget {
  const SurvivalScreen({super.key});

  @override
  ConsumerState<SurvivalScreen> createState() => _SurvivalScreenState();
}

class _SurvivalScreenState extends ConsumerState<SurvivalScreen> {
  static const _checker = AnswerChecker();

  late List<Question> _pool;
  int _index = 0;
  int _streak = 0;
  bool _answered = false;
  bool _lastCorrect = false;
  String? _selected;
  final _text = TextEditingController();
  final List<AnswerResult> _results = [];
  bool _ended = false;
  bool _submitting = false;
  SurvivalResult? _result;

  @override
  void initState() {
    super.initState();
    _text.addListener(() {
      if (!_answered && _question.type.isStudentProduced) setState(() {});
    });
    _pool = _buildPool();
  }

  List<Question> _buildPool() {
    final bundle = ref.read(appControllerProvider).valueOrNull?.bundle;
    if (bundle == null) return [];
    // A large, domain-balanced pool so a long run rarely repeats.
    return balancedSample([...bundle.questions], 300, Random());
  }

  Question get _question => _pool[_index];

  bool get _canCheck => _question.type.isStudentProduced
      ? _text.text.trim().isNotEmpty
      : _selected != null;

  @override
  void dispose() {
    _text.dispose();
    super.dispose();
  }

  void _check() {
    final correct = _checker.isCorrect(
      _question,
      choiceId: _selected,
      produced: _text.text,
    );
    _results.add(
      AnswerResult(question: _question, correct: correct, isReview: true),
    );
    final profile = ref.read(appControllerProvider).valueOrNull?.profile;
    if (profile?.hapticsOn ?? true) {
      correct ? HapticFeedback.lightImpact() : HapticFeedback.heavyImpact();
    }
    if (profile?.soundOn ?? true) {
      ref
          .read(soundServiceProvider)
          .play(correct ? Sfx.correct : Sfx.incorrect);
    }
    setState(() {
      _answered = true;
      _lastCorrect = correct;
      if (correct) _streak += 1;
    });
  }

  Future<void> _next() async {
    if (!_lastCorrect || _index >= _pool.length - 1) {
      await _finish();
      return;
    }
    setState(() {
      _index += 1;
      _answered = false;
      _selected = null;
      _text.clear();
    });
  }

  Future<void> _finish() async {
    setState(() => _submitting = true);
    final result = await ref
        .read(appControllerProvider.notifier)
        .completeSurvival(results: _results, streak: _streak);
    if (result.isRecord || result.newBadges.isNotEmpty) {
      final profile = ref.read(appControllerProvider).valueOrNull?.profile;
      if (profile?.soundOn ?? true) {
        ref.read(soundServiceProvider).play(Sfx.levelUp);
      }
    }
    setState(() {
      _ended = true;
      _submitting = false;
      _result = result;
    });
  }

  void _restart() {
    setState(() {
      _pool = _buildPool();
      _index = 0;
      _streak = 0;
      _answered = false;
      _selected = null;
      _text.clear();
      _results.clear();
      _ended = false;
      _result = null;
    });
  }

  @override
  Widget build(BuildContext context) {
    if (_pool.isEmpty) {
      return const Scaffold(body: Center(child: CircularProgressIndicator()));
    }
    return Scaffold(
      body: SafeArea(child: _ended ? _buildResult() : _buildQuiz()),
    );
  }

  Widget _buildQuiz() {
    return Column(
      children: [
        Padding(
          padding: const EdgeInsets.fromLTRB(12, 8, 16, 8),
          child: Row(
            children: [
              IconButton(
                icon: const Icon(Icons.close_rounded),
                onPressed: () => context.pop(),
              ),
              const Spacer(),
              StatPill(
                icon: Icons.bolt_rounded,
                value: 'Streak $_streak',
                color: AppTheme.streak,
              ),
            ],
          ),
        ),
        Expanded(
          child: QuestionView(
            question: _question,
            answered: _answered,
            selectedChoiceId: _selected,
            textController: _text,
            onSelectChoice: (id) => setState(() => _selected = id),
          ),
        ),
        _bottomBar(),
      ],
    );
  }

  Widget _bottomBar() {
    final color = _lastCorrect ? AppTheme.correct : AppTheme.incorrect;
    final q = _question;
    final answer = q.type.isStudentProduced
        ? (q.answer?.accepted.first ?? '')
        : (q.correct?.text ?? '');
    return Container(
      width: double.infinity,
      decoration: BoxDecoration(
        color: _answered ? color.withValues(alpha: 0.12) : null,
        borderRadius: const BorderRadius.vertical(top: Radius.circular(20)),
      ),
      padding: const EdgeInsets.fromLTRB(20, 16, 20, 20),
      child: Column(
        mainAxisSize: MainAxisSize.min,
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          if (_answered) ...[
            Row(
              children: [
                Icon(
                  _lastCorrect
                      ? Icons.check_circle_rounded
                      : Icons.cancel_rounded,
                  color: color,
                ),
                const SizedBox(width: 8),
                Text(
                  _lastCorrect ? 'Correct!' : 'Run over',
                  style: TextStyle(
                    color: color,
                    fontWeight: FontWeight.w800,
                    fontSize: 18,
                  ),
                ),
              ],
            ),
            Gap.s,
            if (!_lastCorrect)
              Padding(
                padding: const EdgeInsets.only(bottom: 6),
                child: Text(
                  'Answer: $answer',
                  style: const TextStyle(fontWeight: FontWeight.w700),
                ),
              ),
            Text(q.explanation, style: const TextStyle(height: 1.4)),
            Gap.m,
          ],
          FilledButton(
            onPressed: _answered
                ? _next
                : (_canCheck && !_submitting ? _check : null),
            style: FilledButton.styleFrom(
              backgroundColor: _answered ? color : null,
            ),
            child: _submitting
                ? const SizedBox(
                    height: 22,
                    width: 22,
                    child: CircularProgressIndicator(strokeWidth: 2),
                  )
                : Text(
                    _answered
                        ? (_lastCorrect ? 'Continue' : 'See results')
                        : 'Check',
                  ),
          ),
        ],
      ),
    );
  }

  Widget _buildResult() {
    final r = _result!;
    final scheme = Theme.of(context).colorScheme;
    return Column(
      children: [
        Expanded(
          child: ListView(
            padding: kPagePadding,
            children: [
              Gap.xl,
              Center(
                child: Column(
                  children: [
                    Text(
                      r.isRecord ? '🏆' : '🛡️',
                      style: const TextStyle(fontSize: 64),
                    ),
                    Text(
                      r.isRecord ? 'New best streak!' : 'Run complete',
                      style: Theme.of(context).textTheme.headlineSmall
                          ?.copyWith(fontWeight: FontWeight.w800),
                    ),
                  ],
                ),
              ),
              Gap.l,
              Row(
                children: [
                  Expanded(
                    child: AppCard(
                      color: AppTheme.streak.withValues(alpha: 0.12),
                      child: Column(
                        crossAxisAlignment: CrossAxisAlignment.start,
                        children: [
                          const Icon(
                            Icons.bolt_rounded,
                            color: AppTheme.streak,
                          ),
                          Gap.s,
                          Text(
                            '${r.streak}',
                            style: const TextStyle(
                              fontSize: 28,
                              fontWeight: FontWeight.w800,
                            ),
                          ),
                          const Text('This run'),
                        ],
                      ),
                    ),
                  ),
                  Gap.s,
                  Expanded(
                    child: AppCard(
                      color: AppTheme.xpGold.withValues(alpha: 0.12),
                      child: Column(
                        crossAxisAlignment: CrossAxisAlignment.start,
                        children: [
                          const Icon(
                            Icons.emoji_events_rounded,
                            color: AppTheme.xpGold,
                          ),
                          Gap.s,
                          Text(
                            '${r.best}',
                            style: const TextStyle(
                              fontSize: 28,
                              fontWeight: FontWeight.w800,
                            ),
                          ),
                          const Text('Best ever'),
                        ],
                      ),
                    ),
                  ),
                ],
              ),
              if (r.newBadges.isNotEmpty) ...[
                Gap.l,
                const SectionLabel('New achievements'),
                ...r.newBadges.map(
                  (bdg) => AppCard(
                    child: Row(
                      children: [
                        Text(bdg.emoji, style: const TextStyle(fontSize: 28)),
                        Gap.m,
                        Expanded(
                          child: Column(
                            crossAxisAlignment: CrossAxisAlignment.start,
                            children: [
                              Text(
                                bdg.title,
                                style: const TextStyle(
                                  fontWeight: FontWeight.w800,
                                ),
                              ),
                              Text(bdg.description),
                            ],
                          ),
                        ),
                      ],
                    ),
                  ),
                ),
              ],
            ],
          ),
        ),
        Padding(
          padding: kPagePadding,
          child: Row(
            children: [
              Expanded(
                child: OutlinedButton(
                  onPressed: () => context.pop(),
                  child: const Text('Home'),
                ),
              ),
              Gap.s,
              Expanded(
                child: FilledButton(
                  onPressed: _restart,
                  style: FilledButton.styleFrom(
                    backgroundColor: scheme.primary,
                  ),
                  child: const Text('Play again'),
                ),
              ),
            ],
          ),
        ),
      ],
    );
  }
}
