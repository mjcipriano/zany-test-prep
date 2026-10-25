import 'package:flutter/material.dart';
import 'package:flutter/services.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:go_router/go_router.dart';

import '../../app/app_controller.dart';
import '../../core/sound_service.dart';
import '../../design/theme.dart';
import '../../design/widgets.dart';
import '../../domain/models/lesson.dart';
import '../../domain/models/lesson_resume.dart';
import '../../domain/models/question.dart';
import '../../domain/services/answer_checker.dart';
import '../../domain/services/game_service.dart';
import 'lesson_summary.dart';
import 'question_view.dart';

enum _Phase { teaching, quiz, summary }

/// Plays through a teaching card + questions with immediate feedback, then a
/// summary. Used for both lessons and the review queue.
///
/// Lessons pass [onProgress] to have the attempt saved after every step, and
/// [resumeFrom] to continue a saved attempt at the same question (with the
/// same answers and feedback) instead of starting over.
class LessonPlayer extends ConsumerStatefulWidget {
  const LessonPlayer({
    super.key,
    required this.title,
    required this.questions,
    required this.onComplete,
    this.teachingCard,
    this.isReview = false,
    this.resumeFrom,
    this.onProgress,
  });

  final String title;
  final List<Question> questions;
  final TeachingCard? teachingCard;
  final bool isReview;
  final Future<LessonOutcome> Function(List<AnswerResult>) onComplete;

  /// A saved attempt to continue. Must already be validated against
  /// [questions] (see [LessonResume.isValidFor]).
  final LessonAttempt? resumeFrom;

  /// Called with the attempt so far whenever it changes (quiz started, answer
  /// checked, moved on). Null means progress is not saved (reviews).
  final ValueChanged<LessonAttempt>? onProgress;

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
  // Parallel to [_results]: what was picked/typed, for saving the attempt.
  final List<SavedAnswer> _saved = [];
  DateTime _questionStart = DateTime.now();
  DateTime _startedAt = DateTime.now();
  LessonOutcome? _outcome;
  bool _submitting = false;

  Question get _q => widget.questions[_index];

  bool get _canCheck {
    if (_q.type.isStudentProduced) {
      return _textController.text.trim().isNotEmpty;
    }
    return _selectedChoiceId != null;
  }

  @override
  void initState() {
    super.initState();
    final resume = widget.resumeFrom;
    if (resume != null) _restore(resume);
    // Re-evaluate the Check button as the user types a grid-in answer.
    _textController.addListener(_onTextChanged);
  }

  /// Rebuilds the in-memory attempt from a saved one. The results restored
  /// here are only handed to [LessonPlayer.onComplete] at the end, so no XP
  /// is granted for them twice.
  void _restore(LessonAttempt attempt) {
    _startedAt = attempt.startedAt;
    _index = attempt.index;
    for (var i = 0; i < attempt.answers.length; i++) {
      final a = attempt.answers[i];
      _saved.add(a);
      _results.add(
        AnswerResult(
          question: widget.questions[i],
          correct: a.correct,
          isReview: widget.isReview,
          responseMs: a.responseMs,
        ),
      );
    }
    if (attempt.teachingDone || widget.teachingCard == null) {
      _phase = _Phase.quiz;
    }
    if (attempt.showingFeedback) {
      final last = attempt.answers.last;
      _answered = true;
      _lastCorrect = last.correct;
      _selectedChoiceId = last.choiceId;
      _textController.text = last.produced ?? '';
    }
  }

  /// Reports the attempt so far to [LessonPlayer.onProgress] (saves it).
  void _emitProgress() {
    widget.onProgress?.call(
      LessonAttempt(
        teachingDone: true,
        index: _index,
        answers: List.unmodifiable(_saved),
        startedAt: _startedAt,
      ),
    );
  }

  void _onTextChanged() {
    if (!_answered && _q.type.isStudentProduced) setState(() {});
  }

  @override
  void dispose() {
    _textController.removeListener(_onTextChanged);
    _textController.dispose();
    super.dispose();
  }

  void _feedbackEffects(bool correct) {
    final profile = ref.read(appControllerProvider).valueOrNull?.profile;
    if (profile?.hapticsOn ?? true) {
      correct ? HapticFeedback.lightImpact() : HapticFeedback.heavyImpact();
    }
    if (profile?.soundOn ?? true) {
      ref
          .read(soundServiceProvider)
          .play(correct ? Sfx.correct : Sfx.incorrect);
    }
  }

  void _uiSound(Sfx sfx) {
    final profile = ref.read(appControllerProvider).valueOrNull?.profile;
    if (profile?.soundOn ?? true) ref.read(soundServiceProvider).play(sfx);
  }

  void _summaryEffects(LessonOutcome outcome) {
    final profile = ref.read(appControllerProvider).valueOrNull?.profile;
    if (profile?.hapticsOn ?? true) HapticFeedback.mediumImpact();
    if (profile?.soundOn ?? true) {
      final sound = ref.read(soundServiceProvider);
      sound.play(outcome.leveledUp ? Sfx.levelUp : Sfx.lessonComplete);
    }
  }

  void _check() {
    final correct = _checker.isCorrect(
      _q,
      choiceId: _selectedChoiceId,
      produced: _textController.text,
    );
    final responseMs = DateTime.now().difference(_questionStart).inMilliseconds;
    _results.add(
      AnswerResult(
        question: _q,
        correct: correct,
        isReview: widget.isReview,
        responseMs: responseMs,
      ),
    );
    final produced = _q.type.isStudentProduced;
    _saved.add(
      SavedAnswer(
        questionId: _q.id,
        correct: correct,
        responseMs: responseMs,
        choiceId: produced ? null : _selectedChoiceId,
        produced: produced ? _textController.text : null,
      ),
    );
    _feedbackEffects(correct);
    setState(() {
      _answered = true;
      _lastCorrect = correct;
    });
    _emitProgress();
  }

  Future<void> _next() async {
    if (_submitting) return; // ignore a second tap while the result is saving
    if (_index < widget.questions.length - 1) {
      _uiSound(Sfx.advance);
      setState(() {
        _index++;
        _answered = false;
        _selectedChoiceId = null;
        _textController.clear();
        _questionStart = DateTime.now();
      });
      _emitProgress();
    } else {
      setState(() => _submitting = true);
      final outcome = await widget.onComplete(_results);
      if (!mounted) return;
      _summaryEffects(outcome);
      setState(() {
        _outcome = outcome;
        _phase = _Phase.summary;
        _submitting = false;
      });
    }
  }

  Future<bool> _confirmExit() async {
    if (_phase != _Phase.quiz) return true;
    final saved = widget.onProgress != null;
    final leave = await showDialog<bool>(
      context: context,
      builder: (ctx) => AlertDialog(
        title: const Text('Leave lesson?'),
        content: Text(
          saved
              ? 'Your progress is saved. Come back anytime to pick up at '
                    'question ${_index + 1} of ${widget.questions.length}.'
              : 'Your progress in this lesson will not be saved. You can '
                    'start it again anytime.',
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
          onStart: () {
            setState(() {
              _phase = _Phase.quiz;
              _questionStart = DateTime.now();
              if (_results.isEmpty) _startedAt = DateTime.now();
            });
            _emitProgress();
          },
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
            onSelectChoice: (id) {
              _uiSound(Sfx.select);
              setState(() => _selectedChoiceId = id);
            },
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

/// A paged mini-lesson (2-5 screens) shown before a lesson's questions, ending
/// in a "Start" button. Single-screen teaching cards page as one screen.
class _TeachingView extends StatefulWidget {
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
  State<_TeachingView> createState() => _TeachingViewState();
}

class _TeachingViewState extends State<_TeachingView> {
  final _controller = PageController();
  int _page = 0;

  @override
  void dispose() {
    _controller.dispose();
    super.dispose();
  }

  @override
  Widget build(BuildContext context) {
    final scheme = Theme.of(context).colorScheme;
    final screens = widget.card.screens;
    final isLast = _page >= screens.length - 1;
    return Column(
      children: [
        Row(
          children: [
            IconButton(
              icon: const Icon(Icons.close_rounded),
              onPressed: widget.onClose,
            ),
            Expanded(
              child: Text(
                widget.title,
                style: Theme.of(context).textTheme.titleSmall?.copyWith(
                  color: scheme.primary,
                  fontWeight: FontWeight.w800,
                ),
              ),
            ),
            if (screens.length > 1)
              Padding(
                padding: const EdgeInsets.only(right: 16),
                child: Text(
                  '${_page + 1}/${screens.length}',
                  style: Theme.of(context).textTheme.bodySmall,
                ),
              ),
          ],
        ),
        Expanded(
          child: PageView.builder(
            controller: _controller,
            itemCount: screens.length,
            onPageChanged: (i) => setState(() => _page = i),
            itemBuilder: (context, i) => _ScreenView(screen: screens[i]),
          ),
        ),
        if (screens.length > 1)
          Row(
            mainAxisAlignment: MainAxisAlignment.center,
            children: [
              for (var i = 0; i < screens.length; i++)
                AnimatedContainer(
                  duration: const Duration(milliseconds: 200),
                  margin: const EdgeInsets.symmetric(horizontal: 3),
                  width: i == _page ? 18 : 7,
                  height: 7,
                  decoration: BoxDecoration(
                    color: i == _page
                        ? scheme.primary
                        : scheme.surfaceContainerHighest,
                    borderRadius: BorderRadius.circular(4),
                  ),
                ),
            ],
          ),
        Padding(
          padding: kPagePadding,
          child: Row(
            children: [
              if (_page > 0)
                Expanded(
                  child: OutlinedButton(
                    onPressed: () => _controller.previousPage(
                      duration: const Duration(milliseconds: 250),
                      curve: Curves.easeOut,
                    ),
                    child: const Text('Back'),
                  ),
                ),
              if (_page > 0) Gap.m,
              Expanded(
                flex: 2,
                child: FilledButton(
                  onPressed: isLast
                      ? widget.onStart
                      : () => _controller.nextPage(
                          duration: const Duration(milliseconds: 250),
                          curve: Curves.easeOut,
                        ),
                  child: Text(isLast ? 'Start' : 'Next'),
                ),
              ),
            ],
          ),
        ),
      ],
    );
  }
}

class _ScreenView extends StatelessWidget {
  const _ScreenView({required this.screen});
  final TeachingScreen screen;

  @override
  Widget build(BuildContext context) {
    final scheme = Theme.of(context).colorScheme;
    return ListView(
      padding: kPagePadding,
      children: [
        Text(
          screen.title,
          style: Theme.of(
            context,
          ).textTheme.headlineSmall?.copyWith(fontWeight: FontWeight.w800),
        ),
        Gap.m,
        Text(screen.body, style: const TextStyle(fontSize: 16, height: 1.5)),
        if (screen.keyPoints.isNotEmpty) ...[
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
                ...screen.keyPoints.map(
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
        ],
        if (screen.workedExample != null) ...[
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
                  screen.workedExample!,
                  style: const TextStyle(fontSize: 15.5, height: 1.4),
                ),
              ],
            ),
          ),
        ],
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
                    'Answer: ${question.answer?.accepted.firstOrNull ?? ''}',
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
              onPressed: submitting
                  ? null
                  : (answered ? onNext : (canCheck ? onCheck : null)),
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
