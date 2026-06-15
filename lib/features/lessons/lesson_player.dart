import 'package:flutter/material.dart';
import 'package:flutter/services.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:go_router/go_router.dart';

import '../../app/app_controller.dart';
import '../../design/theme.dart';
import '../../design/widgets.dart';
import '../../domain/models/lesson.dart';
import '../../domain/models/question.dart';
import '../../domain/services/answer_checker.dart';
import '../../domain/services/game_service.dart';
import 'lesson_summary.dart';
import 'question_view.dart';

enum _Phase { teaching, quiz, summary }

/// Plays through a teaching card + questions with immediate feedback, then a
/// summary. Used for both lessons and the review queue.
class LessonPlayer extends ConsumerStatefulWidget {
  const LessonPlayer({
    super.key,
    required this.title,
    required this.questions,
    required this.onComplete,
    this.teachingCard,
    this.isReview = false,
  });

  final String title;
  final List<Question> questions;
  final TeachingCard? teachingCard;
  final bool isReview;
  final Future<LessonOutcome> Function(List<AnswerResult>) onComplete;

  @override
  ConsumerState<LessonPlayer> createState() => _LessonPlayerState();
}

class _LessonPlayerState extends ConsumerState<LessonPlayer> {
  static const _checker = AnswerChecker();

  late _Phase _phase = widget.teachingCard == null
      ? _Phase.quiz
      : _Phase.teaching;
  int _index = 0;
  bool _answered = false;
  bool _lastCorrect = false;
  String? _selectedChoiceId;
  final _textController = TextEditingController();
  final List<AnswerResult> _results = [];
  DateTime _questionStart = DateTime.now();
  LessonOutcome? _outcome;
  bool _submitting = false;

  Question get _q => widget.questions[_index];

  bool get _canCheck {
    if (_q.type.isStudentProduced)
      return _textController.text.trim().isNotEmpty;
    return _selectedChoiceId != null;
  }

  @override
  void dispose() {
    _textController.dispose();
    super.dispose();
  }

  void _feedbackEffects(bool correct) {
    final profile = ref.read(appControllerProvider).valueOrNull?.profile;
    if (profile?.hapticsOn ?? true) {
      correct ? HapticFeedback.lightImpact() : HapticFeedback.heavyImpact();
    }
    if (profile?.soundOn ?? true) {
      SystemSound.play(SystemSoundType.click);
    }
  }

  void _check() {
    final correct = _checker.isCorrect(
      _q,
      choiceId: _selectedChoiceId,
      produced: _textController.text,
    );
    _results.add(
      AnswerResult(
        question: _q,
        correct: correct,
        isReview: widget.isReview,
        responseMs: DateTime.now().difference(_questionStart).inMilliseconds,
      ),
    );
    _feedbackEffects(correct);
    setState(() {
      _answered = true;
      _lastCorrect = correct;
    });
  }

  Future<void> _next() async {
    if (_index < widget.questions.length - 1) {
      setState(() {
        _index++;
        _answered = false;
        _selectedChoiceId = null;
        _textController.clear();
        _questionStart = DateTime.now();
      });
    } else {
      setState(() => _submitting = true);
      final outcome = await widget.onComplete(_results);
      setState(() {
        _outcome = outcome;
        _phase = _Phase.summary;
        _submitting = false;
      });
    }
  }

  Future<bool> _confirmExit() async {
    if (_phase != _Phase.quiz) return true;
    final leave = await showDialog<bool>(
      context: context,
      builder: (ctx) => AlertDialog(
        title: const Text('Leave lesson?'),
        content: const Text(
          'Your progress in this lesson will not be saved. You can start it '
          'again anytime.',
        ),
        actions: [
          TextButton(
            onPressed: () => Navigator.pop(ctx, false),
            child: const Text('Keep going'),
          ),
          FilledButton(
            onPressed: () => Navigator.pop(ctx, true),
            child: const Text('Leave'),
          ),
        ],
      ),
    );
    return leave ?? false;
  }

  @override
  Widget build(BuildContext context) {
    return PopScope(
      canPop: _phase != _Phase.quiz,
      onPopInvokedWithResult: (didPop, _) async {
        if (didPop) return;
        if (await _confirmExit() && context.mounted) context.pop();
      },
      child: Scaffold(body: SafeArea(child: _buildPhase())),
    );
  }

  Widget _buildPhase() {
    switch (_phase) {
      case _Phase.teaching:
        return _TeachingView(
          title: widget.title,
          card: widget.teachingCard!,
          onStart: () => setState(() {
            _phase = _Phase.quiz;
            _questionStart = DateTime.now();
          }),
          onClose: () => context.pop(),
        );
      case _Phase.summary:
        return LessonSummary(
          outcome: _outcome!,
          questions: widget.questions,
          results: _results,
          isReview: widget.isReview,
          onDone: () => context.pop(),
        );
      case _Phase.quiz:
        return _buildQuiz();
    }
  }

  Widget _buildQuiz() {
    final total = widget.questions.length;
    return Column(
      children: [
        Padding(
          padding: const EdgeInsets.fromLTRB(12, 8, 16, 8),
          child: Row(
            children: [
              IconButton(
                icon: const Icon(Icons.close_rounded),
                onPressed: () async {
                  if (await _confirmExit() && mounted) context.pop();
                },
              ),
              Expanded(
                child: ProgressBar(
                  value: total == 0
                      ? 0
                      : (_index + (_answered ? 1 : 0)) / total,
                ),
              ),
              const SizedBox(width: 12),
              Text(
                '${_index + 1}/$total',
                style: const TextStyle(fontWeight: FontWeight.w700),
              ),
            ],
          ),
        ),
        Expanded(
          child: QuestionView(
            question: _q,
            answered: _answered,
            selectedChoiceId: _selectedChoiceId,
            textController: _textController,
            onSelectChoice: (id) => setState(() => _selectedChoiceId = id),
          ),
        ),
        _BottomBar(
          answered: _answered,
          correct: _lastCorrect,
          canCheck: _canCheck && !_submitting,
          question: _q,
          chosenRationale: _chosenRationale(),
          onCheck: _check,
          onNext: _next,
          isLast: _index == total - 1,
          submitting: _submitting,
        ),
      ],
    );
  }

  String? _chosenRationale() {
    if (!_answered || _q.type.isStudentProduced) return null;
    for (final c in _q.choices) {
      if (c.id == _selectedChoiceId) return c.rationale;
    }
    return null;
  }
}

class _TeachingView extends StatelessWidget {
  const _TeachingView({
    required this.title,
    required this.card,
    required this.onStart,
    required this.onClose,
  });

  final String title;
  final TeachingCard card;
  final VoidCallback onStart;
  final VoidCallback onClose;

  @override
  Widget build(BuildContext context) {
    final scheme = Theme.of(context).colorScheme;
    return Column(
      children: [
        Align(
          alignment: Alignment.centerLeft,
          child: IconButton(
            icon: const Icon(Icons.close_rounded),
            onPressed: onClose,
          ),
        ),
        Expanded(
          child: ListView(
            padding: kPagePadding,
            children: [
              Text(
                title,
                style: Theme.of(context).textTheme.titleMedium?.copyWith(
                  color: scheme.primary,
                  fontWeight: FontWeight.w800,
                ),
              ),
              Gap.s,
              Text(
                card.title,
                style: Theme.of(context).textTheme.headlineSmall?.copyWith(
                  fontWeight: FontWeight.w800,
                ),
              ),
              Gap.m,
              Text(
                card.body,
                style: const TextStyle(fontSize: 16, height: 1.5),
              ),
              Gap.l,
              AppCard(
                color: scheme.primaryContainer,
                child: Column(
                  crossAxisAlignment: CrossAxisAlignment.start,
                  children: [
                    const Text(
                      'Key points',
                      style: TextStyle(fontWeight: FontWeight.w800),
                    ),
                    Gap.s,
                    ...card.keyPoints.map(
                      (k) => Padding(
                        padding: const EdgeInsets.only(bottom: 6),
                        child: Row(
                          crossAxisAlignment: CrossAxisAlignment.start,
                          children: [
                            const Text('•  '),
                            Expanded(child: Text(k)),
                          ],
                        ),
                      ),
                    ),
                  ],
                ),
              ),
              if (card.workedExample != null) ...[
                Gap.m,
                AppCard(
                  child: Column(
                    crossAxisAlignment: CrossAxisAlignment.start,
                    children: [
                      const Text(
                        'Example',
                        style: TextStyle(fontWeight: FontWeight.w800),
                      ),
                      Gap.s,
                      Text(
                        card.workedExample!,
                        style: const TextStyle(fontSize: 15.5, height: 1.4),
                      ),
                    ],
                  ),
                ),
              ],
            ],
          ),
        ),
        Padding(
          padding: kPagePadding,
          child: FilledButton(onPressed: onStart, child: const Text('Start')),
        ),
      ],
    );
  }
}

class _BottomBar extends StatelessWidget {
  const _BottomBar({
    required this.answered,
    required this.correct,
    required this.canCheck,
    required this.question,
    required this.chosenRationale,
    required this.onCheck,
    required this.onNext,
    required this.isLast,
    required this.submitting,
  });

  final bool answered;
  final bool correct;
  final bool canCheck;
  final Question question;
  final String? chosenRationale;
  final VoidCallback onCheck;
  final VoidCallback onNext;
  final bool isLast;
  final bool submitting;

  @override
  Widget build(BuildContext context) {
    final color = correct ? AppTheme.correct : AppTheme.incorrect;
    return AnimatedSize(
      duration: const Duration(milliseconds: 200),
      alignment: Alignment.bottomCenter,
      child: Container(
        width: double.infinity,
        decoration: BoxDecoration(
          color: answered
              ? color.withValues(alpha: 0.12)
              : Theme.of(context).colorScheme.surface,
          borderRadius: const BorderRadius.vertical(top: Radius.circular(20)),
        ),
        padding: const EdgeInsets.fromLTRB(20, 16, 20, 20),
        child: Column(
          mainAxisSize: MainAxisSize.min,
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            if (answered) ...[
              Row(
                children: [
                  Icon(
                    correct ? Icons.check_circle_rounded : Icons.cancel_rounded,
                    color: color,
                  ),
                  const SizedBox(width: 8),
                  Text(
                    correct ? 'Correct!' : 'Not quite',
                    style: TextStyle(
                      color: color,
                      fontWeight: FontWeight.w800,
                      fontSize: 18,
                    ),
                  ),
                ],
              ),
              Gap.s,
              if (!correct && question.type.isStudentProduced)
                Padding(
                  padding: const EdgeInsets.only(bottom: 6),
                  child: Text(
                    'Answer: ${question.answer?.accepted.first ?? ''}',
                    style: const TextStyle(fontWeight: FontWeight.w700),
                  ),
                ),
              if (chosenRationale != null && !correct)
                Padding(
                  padding: const EdgeInsets.only(bottom: 6),
                  child: Text(chosenRationale!),
                ),
              Text(question.explanation, style: const TextStyle(height: 1.4)),
              Gap.m,
            ],
            FilledButton(
              onPressed: answered ? onNext : (canCheck ? onCheck : null),
              style: FilledButton.styleFrom(
                backgroundColor: answered ? color : null,
              ),
              child: submitting
                  ? const SizedBox(
                      height: 22,
                      width: 22,
                      child: CircularProgressIndicator(strokeWidth: 2),
                    )
                  : Text(answered ? (isLast ? 'Finish' : 'Continue') : 'Check'),
            ),
          ],
        ),
      ),
    );
  }
}
