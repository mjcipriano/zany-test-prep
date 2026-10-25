import 'dart:async';
import 'dart:math';

import 'package:flutter/material.dart';
import 'package:flutter/semantics.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:go_router/go_router.dart';

import '../../app/app_controller.dart';
import '../../design/theme.dart';
import '../../domain/models/content_bundle.dart';
import '../../domain/models/exam.dart';
import '../../domain/models/question.dart';
import '../../domain/services/game_service.dart';
import '../../domain/services/scoring.dart';
import '../../domain/services/timed_test.dart';
import '../lessons/question_view.dart';
import 'test_result_views.dart';

enum _Phase { intro, module, breakScreen, results }

/// Full timed practice test with per-module timers, flag/navigate, and an
/// estimated section + total/composite score on the exam's own scale.
///
/// Module layout comes from the bundle (exam.yaml `timed_test`). On an
/// adaptive plan (the Digital SAT) each section's first module is a mixed
/// routing module and the second module is assembled only after the first is
/// submitted — harder or easier depending on the routing accuracy; see
/// [TestAssembler]. Linear plans (the ACT) are dealt at random per domain.
class TimedTestScreen extends ConsumerStatefulWidget {
  const TimedTestScreen({super.key, this.random, this.plan});

  /// Source of all question-selection randomness (inject a seeded one in
  /// tests). Defaults to a fresh [Random].
  final Random? random;

  /// Overrides the bundle's timed-test layout (tests use tiny modules).
  final TimedTestPlan? plan;

  @override
  ConsumerState<TimedTestScreen> createState() => _TimedTestScreenState();
}

class _TimedTestScreenState extends ConsumerState<TimedTestScreen> {
  _Phase _phase = _Phase.intro;
  late TestAssembler _assembler;
  // Questions per module; null until the module is assembled (routed modules
  // wait for their routing module's result).
  late List<List<Question>?> _moduleQs;
  final Map<String, SectionRoute> _routes = {}; // domain -> route taken
  int _moduleIndex = 0;
  int? _nextIndex; // the module the transition screen leads to
  int _q = 0;
  final Map<String, String> _answers = {}; // questionId -> choiceId or text
  final Set<String> _flagged = {};
  final _text = TextEditingController();
  int _remaining = 0;
  Timer? _timer;
  bool _ending = false; // the current module is being closed/scored
  TimedTestReport? _report;

  @override
  void dispose() {
    _timer?.cancel();
    _text.dispose();
    super.dispose();
  }

  ContentBundle get _bundle =>
      ref.read(appControllerProvider).valueOrNull!.bundle;

  Exam get _exam => _bundle.exam;

  TimedTestPlan get _sourcePlan => widget.plan ?? _exam.timedTest;

  TimedTestPlan get _plan => _assembler.plan;

  List<TestModule> get _modules => _plan.modules;

  void _buildTest() {
    _assembler = TestAssembler(
      _bundle.questions,
      _sourcePlan,
      widget.random ?? Random(),
    );
    _routes.clear();
    _moduleQs = List<List<Question>?>.filled(_modules.length, null);
  }

  /// Assembles module [i] if needed (routing it first when it is adaptive)
  /// and returns its questions.
  List<Question> _prepare(int i) {
    final ready = _moduleQs[i];
    if (ready != null) return ready;
    var route = SectionRoute.linear;
    final by = _plan.routedBy(i);
    if (by != null) {
      final routing = _prepare(by);
      route = _routes.putIfAbsent(
        _modules[i].domain,
        () => routeFor(
          routing.where((q) => isAnsweredCorrectly(q, _answers[q.id])).length,
          routing.length,
          _plan.adaptive,
        ),
      );
    }
    return _moduleQs[i] = _assembler.buildModule(i, route: route);
  }

  /// The next module after [from] that actually has questions, or null.
  int? _nextPlayable(int from) {
    for (var j = from + 1; j < _modules.length; j++) {
      if (_prepare(j).isNotEmpty) return j;
    }
    return null;
  }

  void _startModule(int i) {
    _timer?.cancel();
    _ending = false;
    setState(() {
      _moduleIndex = i;
      _q = 0;
      _phase = _Phase.module;
      _remaining = _modules[i].minutes * 60;
      _syncText();
    });
    _timer = Timer.periodic(const Duration(seconds: 1), (t) {
      if (!mounted) return;
      setState(() => _remaining -= 1);
      // Screen readers get two heads-ups, never a per-second countdown.
      if (_remaining == 5 * 60 || _remaining == 60) {
        SemanticsService.announce(
          '${remainingTimeLabel(_remaining)} left in this section',
          Directionality.of(context),
        );
      }
      if (_remaining <= 0) {
        t.cancel();
        _endModule();
      }
    });
  }

  List<Question> get _qs => _moduleQs[_moduleIndex]!;
  Question get _question => _qs[_q];

  void _syncText() {
    if (_question.type.isStudentProduced) {
      _text.text = _answers[_question.id] ?? '';
    }
  }

  void _record(String value) => _answers[_question.id] = value;

  void _go(int delta) {
    final next = (_q + delta).clamp(0, _qs.length - 1);
    if (_question.type.isStudentProduced && _text.text.trim().isNotEmpty) {
      _record(_text.text.trim());
    }
    setState(() {
      _q = next;
      _syncText();
    });
  }

  void _endModule() {
    // The timer can fire while the submit dialog is open; whichever path gets
    // here first wins, so a section is never scored twice.
    if (_ending || _phase != _Phase.module) return;
    _ending = true;
    _timer?.cancel();
    if (_question.type.isStudentProduced && _text.text.trim().isNotEmpty) {
      _record(_text.text.trim());
    }
    // Routing happens here: the next module is assembled from this one's
    // answers before the student sees the transition screen.
    final next = _nextPlayable(_moduleIndex);
    if (next != null) {
      setState(() {
        _nextIndex = next;
        _phase = _Phase.breakScreen;
      });
    } else {
      _finish();
    }
  }

  Future<void> _finish() async {
    _timer?.cancel();
    final modules = [
      for (final m in _moduleQs)
        if (m != null) m,
    ];
    // Score everything and apply XP/mastery/review.
    final results = [
      for (final q in modules.expand((m) => m))
        AnswerResult(
          question: q,
          correct: isAnsweredCorrectly(q, _answers[q.id]),
        ),
    ];
    _report = TimedTestReport.score(
      modules: modules,
      answers: _answers,
      routes: _routes,
      scoring: ExamScoring(_exam.scoring),
      domainOrder: _bundle.domainIds,
    );
    await ref
        .read(appControllerProvider.notifier)
        .completeReview(results: results);
    if (!mounted) return;
    setState(() => _phase = _Phase.results);
  }

  @override
  Widget build(BuildContext context) {
    switch (_phase) {
      case _Phase.intro:
        return _intro();
      case _Phase.module:
        return _moduleView();
      case _Phase.breakScreen:
        return _break();
      case _Phase.results:
        return _results();
    }
  }

  Widget _intro() {
    final exam = _exam;
    final plan = _sourcePlan;
    final intro = plan.intro.isNotEmpty
        ? plan.intro
        : 'This mirrors the ${exam.displayName}: ${plan.modules.length} timed '
              'sections.';
    return Scaffold(
      appBar: AppBar(title: Text('${exam.name} Practice Test')),
      body: ListView(
        padding: kPagePadding,
        children: [
          Gap.m,
          const Text(
            'Full timed practice test',
            style: TextStyle(fontSize: 22, fontWeight: FontWeight.w800),
          ),
          Gap.s,
          Text(
            '$intro${plan.adaptive.enabled ? ' Like the real test, the second '
                      'module of each section adapts to how you did on the '
                      'first.' : ''} You can flag questions and move back and '
            'forth within a module, but not between modules. There is no '
            'feedback until the end.',
          ),
          Gap.m,
          for (final m in plan.modules)
            Padding(
              padding: const EdgeInsets.only(bottom: 6),
              child: Row(
                children: [
                  const Icon(Icons.timer_outlined, size: 18),
                  Gap.s,
                  Expanded(child: Text(m.name)),
                  Text('${m.count} q · ${m.minutes} min'),
                ],
              ),
            ),
          Padding(
            padding: const EdgeInsets.only(top: 6),
            child: Text(
              'Total: ${plan.totalQuestions} questions · ${plan.totalMinutes} min',
              style: const TextStyle(fontWeight: FontWeight.w700),
            ),
          ),
          Gap.l,
          FilledButton(
            onPressed: plan.isEmpty
                ? null
                : () {
                    _buildTest();
                    final first = _nextPlayable(-1);
                    if (first == null) return;
                    _startModule(first);
                  },
            child: const Text('Begin test'),
          ),
          TextButton(
            onPressed: () => context.pop(),
            child: const Text('Not now'),
          ),
        ],
      ),
    );
  }

  Widget _moduleView() {
    final m = _modules[_moduleIndex];
    final mm = (_remaining ~/ 60).toString().padLeft(2, '0');
    final ss = (_remaining % 60).toString().padLeft(2, '0');
    final low = _remaining <= 60;
    final answered = _answers.containsKey(_question.id);
    return Scaffold(
      appBar: AppBar(
        automaticallyImplyLeading: false,
        title: Text(m.name, style: const TextStyle(fontSize: 15)),
        actions: [
          _TimerChip(remaining: _remaining, low: low, mm: mm, ss: ss),
          const SizedBox(width: 4),
        ],
      ),
      body: SafeArea(
        child: Column(
          children: [
            Padding(
              padding: const EdgeInsets.fromLTRB(20, 4, 20, 0),
              child: Row(
                children: [
                  Expanded(
                    child: Text(
                      'Question ${_q + 1} of ${_qs.length}',
                      style: const TextStyle(fontWeight: FontWeight.w700),
                    ),
                  ),
                  IconButton(
                    tooltip: 'Flag for review',
                    isSelected: _flagged.contains(_question.id),
                    icon: Icon(
                      _flagged.contains(_question.id)
                          ? Icons.flag_rounded
                          : Icons.flag_outlined,
                    ),
                    color: _flagged.contains(_question.id)
                        ? AppColors.of(context).streak
                        : null,
                    onPressed: () => setState(() {
                      final id = _question.id;
                      _flagged.contains(id)
                          ? _flagged.remove(id)
                          : _flagged.add(id);
                    }),
                  ),
                  TextButton.icon(
                    onPressed: _openNavigator,
                    icon: const Icon(Icons.grid_view_rounded, size: 18),
                    label: const Text('Review'),
                  ),
                ],
              ),
            ),
            Expanded(
              // Swipe left/right to move between questions (in addition to the
              // Back/Next buttons below).
              child: GestureDetector(
                behavior: HitTestBehavior.opaque,
                onHorizontalDragEnd: (d) {
                  final v = d.primaryVelocity ?? 0;
                  if (v < -250) {
                    _go(1);
                  } else if (v > 250) {
                    _go(-1);
                  }
                },
                child: QuestionView(
                  question: _question,
                  answered: false,
                  selectedChoiceId: _question.type.isStudentProduced
                      ? null
                      : _answers[_question.id],
                  textController: _text,
                  onSelectChoice: (id) => setState(() => _record(id)),
                ),
              ),
            ),
            Padding(
              padding: const EdgeInsets.all(16),
              child: Row(
                children: [
                  OutlinedButton(
                    // Bounded width: the themed default is full-width, which
                    // is an infinite-width constraint inside a Row.
                    style: OutlinedButton.styleFrom(
                      minimumSize: const Size(96, 54),
                    ),
                    onPressed: _q > 0 ? () => _go(-1) : null,
                    child: const Text('Back'),
                  ),
                  Gap.s,
                  Expanded(
                    child: _q < _qs.length - 1
                        ? FilledButton(
                            onPressed: () => _go(1),
                            child: Text(answered ? 'Next' : 'Skip'),
                          )
                        : FilledButton(
                            onPressed: _confirmSubmit,
                            child: const Text('Submit section'),
                          ),
                  ),
                ],
              ),
            ),
          ],
        ),
      ),
    );
  }

  void _openNavigator() {
    showModalBottomSheet<void>(
      context: context,
      builder: (ctx) => Padding(
        padding: const EdgeInsets.all(16),
        child: Column(
          mainAxisSize: MainAxisSize.min,
          children: [
            const Text(
              'Jump to a question',
              style: TextStyle(fontWeight: FontWeight.w800),
            ),
            Gap.s,
            Wrap(
              spacing: 8,
              runSpacing: 8,
              children: [
                for (var i = 0; i < _qs.length; i++)
                  _NavChip(
                    number: i + 1,
                    answered: _answers.containsKey(_qs[i].id),
                    flagged: _flagged.contains(_qs[i].id),
                    current: i == _q,
                    onTap: () {
                      Navigator.pop(ctx);
                      if (_question.type.isStudentProduced &&
                          _text.text.trim().isNotEmpty) {
                        _record(_text.text.trim());
                      }
                      setState(() {
                        _q = i;
                        _syncText();
                      });
                    },
                  ),
              ],
            ),
            Gap.m,
            FilledButton(
              onPressed: () {
                Navigator.pop(ctx);
                _confirmSubmit();
              },
              child: const Text('Submit section'),
            ),
          ],
        ),
      ),
    );
  }

  Future<void> _confirmSubmit() async {
    final unanswered = _qs.where((q) => !_answers.containsKey(q.id)).length;
    final ok = await showDialog<bool>(
      context: context,
      builder: (ctx) => AlertDialog(
        title: const Text('Submit this section?'),
        content: Text(
          unanswered == 0
              ? 'You have answered every question.'
              : 'You have $unanswered unanswered question(s). They will be marked '
                    'incorrect.',
        ),
        actions: [
          TextButton(
            onPressed: () => Navigator.pop(ctx, false),
            child: const Text('Keep working'),
          ),
          FilledButton(
            onPressed: () => Navigator.pop(ctx, true),
            child: const Text('Submit'),
          ),
        ],
      ),
    );
    if (ok == true) _endModule();
  }

  Widget _break() {
    final done = _modules[_moduleIndex];
    final next = _modules[_nextIndex!];
    final newSection = next.domain != done.domain;
    final String note;
    if (newSection) {
      note = _plan.adaptive.enabled
          ? 'That section is done. On test day you get a 10-minute break '
                'here — stretch, breathe, then start when you are ready.'
          : 'Nice work. Take a breather, then start when you are ready.';
    } else if (_plan.routedBy(_nextIndex!) != null) {
      // Like the real test, never reveal which way the student was routed.
      note =
          'Your answers are locked in. The next module is put together '
          'based on how this one went, just like on the real test.';
    } else {
      note = 'Your answers are locked in. Start when you are ready.';
    }
    return ModuleTransitionView(
      title: newSection ? 'Section complete' : 'Module complete',
      note: note,
      completed: _nextIndex!,
      totalModules: _modules.length,
      nextName: next.name,
      nextCount: _moduleQs[_nextIndex!]!.length,
      nextMinutes: next.minutes,
      startLabel: newSection ? 'Start next section' : 'Start next module',
      onStart: () => _startModule(_nextIndex!),
    );
  }

  Widget _results() {
    final bundle = _bundle;
    return TestResultsView(
      report: _report!,
      scoring: ExamScoring(bundle.exam.scoring),
      compositeLabel: bundle.exam.scoring.compositeLabel,
      adaptive: _plan.adaptive.enabled,
      domainName: bundle.domainName,
      domainColor: (d) => AppTheme.domainColor(
        bundle.domainIndex(d) < 0 ? 0 : bundle.domainIndex(d),
      ),
      onDone: () => context.go('/home'),
    );
  }
}

class _NavChip extends StatelessWidget {
  const _NavChip({
    required this.number,
    required this.answered,
    required this.flagged,
    required this.current,
    required this.onTap,
  });
  final int number;
  final bool answered;
  final bool flagged;
  final bool current;
  final VoidCallback onTap;

  @override
  Widget build(BuildContext context) {
    final scheme = Theme.of(context).colorScheme;
    final bg = current
        ? scheme.primary
        : answered
        ? scheme.primaryContainer
        : scheme.surfaceContainerHighest;
    final state = [
      if (current) 'current',
      answered ? 'answered' : 'not answered',
      if (flagged) 'flagged',
    ].join(', ');
    return Semantics(
      button: true,
      label: 'Question $number, $state',
      excludeSemantics: true,
      onTap: onTap,
      child: InkWell(
        onTap: onTap,
        borderRadius: BorderRadius.circular(8),
        child: Container(
          constraints: const BoxConstraints(minWidth: 48, minHeight: 48),
          alignment: Alignment.center,
          decoration: BoxDecoration(
            color: bg,
            borderRadius: BorderRadius.circular(8),
            border: flagged
                ? Border.all(color: AppColors.of(context).streak, width: 2)
                : null,
          ),
          child: Text(
            '$number',
            style: TextStyle(
              fontWeight: FontWeight.w700,
              color: current
                  ? scheme.onPrimary
                  : answered
                  ? scheme.onPrimaryContainer
                  : scheme.onSurface,
            ),
          ),
        ),
      ),
    );
  }
}

/// "12 minutes 5 seconds" (or "45 seconds") for screen readers.
String remainingTimeLabel(int seconds) {
  final s = seconds < 0 ? 0 : seconds;
  final m = s ~/ 60, r = s % 60;
  String unit(int n, String w) => '$n $w${n == 1 ? '' : 's'}';
  if (m == 0) return unit(r, 'second');
  if (r == 0) return unit(m, 'minute');
  return '${unit(m, 'minute')} ${unit(r, 'second')}';
}

/// The module countdown. Its text ticks every second, so it is hidden from
/// screen readers (a focused, ever-changing label would be re-read
/// constantly); instead the chip is a button whose label is the time
/// rounded to the minute, and activating it announces the exact time left.
class _TimerChip extends StatelessWidget {
  const _TimerChip({
    required this.remaining,
    required this.low,
    required this.mm,
    required this.ss,
  });

  final int remaining;
  final bool low;
  final String mm;
  final String ss;

  @override
  Widget build(BuildContext context) {
    final minutes = (remaining / 60).ceil();
    final color = low ? AppColors.of(context).incorrect : null;
    void announce() => SemanticsService.announce(
      '${remainingTimeLabel(remaining)} left',
      Directionality.of(context),
    );
    return Semantics(
      key: const Key('test-timer'),
      button: true,
      label: remaining <= 60
          ? 'Time remaining: under a minute'
          : 'Time remaining: about $minutes minutes',
      hint: 'Announces the exact time left',
      excludeSemantics: true,
      onTap: announce,
      child: InkWell(
        onTap: announce,
        borderRadius: BorderRadius.circular(12),
        child: ConstrainedBox(
          constraints: const BoxConstraints(minHeight: 48, minWidth: 48),
          child: Padding(
            padding: const EdgeInsets.symmetric(horizontal: 8),
            child: Row(
              mainAxisSize: MainAxisSize.min,
              children: [
                // Low time is shown by an icon too, not only by colour.
                if (low) ...[
                  Icon(Icons.hourglass_bottom_rounded, size: 18, color: color),
                  const SizedBox(width: 2),
                ],
                Text(
                  '$mm:$ss',
                  style: TextStyle(
                    fontWeight: FontWeight.w800,
                    fontSize: 18,
                    color: color,
                  ),
                ),
              ],
            ),
          ),
        ),
      ),
    );
  }
}
