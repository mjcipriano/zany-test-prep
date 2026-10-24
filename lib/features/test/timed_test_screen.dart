import 'dart:async';
import 'dart:math';

import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:go_router/go_router.dart';

import '../../app/app_controller.dart';
import '../../design/theme.dart';
import '../../design/widgets.dart';
import '../../domain/models/content_bundle.dart';
import '../../domain/models/exam.dart';
import '../../domain/models/question.dart';
import '../../domain/services/answer_checker.dart';
import '../../domain/services/game_service.dart';
import '../../domain/services/scoring.dart';
import '../lessons/question_view.dart';

enum _Phase { intro, module, breakScreen, results }

/// Deals [bundle]'s questions into the exam's timed-test modules (from
/// exam.yaml: SAT = 2 Reading & Writing + 2 Math modules; ACT = English, Math,
/// Reading, Science). Each module draws fresh questions from its domain; a
/// module is simply shorter when the domain runs out of questions.
List<List<Question>> dealTestModules(
  ContentBundle bundle,
  List<TestModule> modules,
  Random rng,
) {
  final byDomain = <String, List<Question>>{};
  for (final q in bundle.questions) {
    byDomain.putIfAbsent(q.domain, () => []).add(q);
  }
  for (final list in byDomain.values) {
    list.shuffle(rng);
  }
  final cursor = <String, int>{};
  return [
    for (final m in modules)
      () {
        final src = byDomain[m.domain] ?? const <Question>[];
        final start = (cursor[m.domain] ?? 0).clamp(0, src.length);
        final end = (start + m.count).clamp(0, src.length);
        cursor[m.domain] = end;
        return src.sublist(start, end);
      }(),
  ];
}

/// Full timed practice test with per-module timers, flag/navigate, and an
/// estimated section + total/composite score on the exam's own scale.
class TimedTestScreen extends ConsumerStatefulWidget {
  const TimedTestScreen({super.key});

  @override
  ConsumerState<TimedTestScreen> createState() => _TimedTestScreenState();
}

class _TimedTestScreenState extends ConsumerState<TimedTestScreen> {
  static const _checker = AnswerChecker();

  _Phase _phase = _Phase.intro;
  late List<TestModule> _modules;
  late List<List<Question>> _moduleQs; // questions per module
  int _moduleIndex = 0;
  int _q = 0;
  final Map<String, String> _answers = {}; // questionId -> choiceId or text
  final Set<String> _flagged = {};
  final _text = TextEditingController();
  int _remaining = 0;
  Timer? _timer;
  bool _ending = false; // the current module is being closed/scored

  @override
  void dispose() {
    _timer?.cancel();
    _text.dispose();
    super.dispose();
  }

  ContentBundle get _bundle =>
      ref.read(appControllerProvider).valueOrNull!.bundle;

  Exam get _exam => _bundle.exam;

  void _buildTest() {
    _modules = _exam.timedTest.modules;
    _moduleQs = dealTestModules(_bundle, _modules, Random());
    // Drop modules that received no questions at all (domain absent).
    final keep = <int>[
      for (var i = 0; i < _modules.length; i++)
        if (_moduleQs[i].isNotEmpty) i,
    ];
    _modules = [for (final i in keep) _modules[i]];
    _moduleQs = [for (final i in keep) _moduleQs[i]];
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
      if (_remaining <= 0) {
        t.cancel();
        _endModule();
      }
    });
  }

  List<Question> get _qs => _moduleQs[_moduleIndex];
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
    if (_moduleIndex < _modules.length - 1) {
      setState(() => _phase = _Phase.breakScreen);
    } else {
      _finish();
    }
  }

  Future<void> _finish() async {
    _timer?.cancel();
    // Score everything and apply XP/mastery/review.
    final results = <AnswerResult>[];
    for (final mod in _moduleQs) {
      for (final q in mod) {
        final ans = _answers[q.id];
        final correct =
            ans != null &&
            _checker.isCorrect(
              q,
              choiceId: q.type.isStudentProduced ? null : ans,
              produced: q.type.isStudentProduced ? ans : null,
            );
        results.add(AnswerResult(question: q, correct: correct));
      }
    }
    await ref
        .read(appControllerProvider.notifier)
        .completeReview(results: results);
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
    final plan = exam.timedTest;
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
            '$intro You can flag questions and move back and forth within a '
            'section, but not between sections. There is no feedback until the '
            'end.',
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
                    if (_moduleQs.isEmpty) return;
                    _startModule(0);
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
          Center(
            child: Padding(
              padding: const EdgeInsets.only(right: 12),
              child: Text(
                '$mm:$ss',
                style: TextStyle(
                  fontWeight: FontWeight.w800,
                  fontSize: 18,
                  color: low ? AppTheme.incorrect : null,
                ),
              ),
            ),
          ),
        ],
      ),
      body: SafeArea(
        child: Column(
          children: [
            Padding(
              padding: const EdgeInsets.fromLTRB(20, 4, 20, 0),
              child: Row(
                children: [
                  Text(
                    'Question ${_q + 1} of ${_qs.length}',
                    style: const TextStyle(fontWeight: FontWeight.w700),
                  ),
                  const Spacer(),
                  IconButton(
                    tooltip: 'Flag',
                    icon: Icon(
                      _flagged.contains(_question.id)
                          ? Icons.flag_rounded
                          : Icons.flag_outlined,
                    ),
                    color: _flagged.contains(_question.id)
                        ? AppTheme.streak
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
    return Scaffold(
      body: Center(
        child: Padding(
          padding: kPagePadding,
          child: Column(
            mainAxisSize: MainAxisSize.min,
            children: [
              const Icon(Icons.coffee_rounded, size: 56),
              Gap.m,
              Text(
                'Section complete',
                style: Theme.of(context).textTheme.headlineSmall?.copyWith(
                  fontWeight: FontWeight.w800,
                ),
              ),
              Gap.s,
              Text(
                'Next up: ${_modules[_moduleIndex + 1].name}',
                textAlign: TextAlign.center,
              ),
              Gap.l,
              FilledButton(
                onPressed: () => _startModule(_moduleIndex + 1),
                child: const Text('Start next section'),
              ),
            ],
          ),
        ),
      ),
    );
  }

  int _correctIn(String domain) {
    var c = 0;
    for (final mod in _moduleQs) {
      for (final q in mod) {
        if (q.domain != domain) continue;
        final ans = _answers[q.id];
        if (ans != null &&
            _checker.isCorrect(
              q,
              choiceId: q.type.isStudentProduced ? null : ans,
              produced: q.type.isStudentProduced ? ans : null,
            )) {
          c++;
        }
      }
    }
    return c;
  }

  int _totalIn(String domain) =>
      _moduleQs.expand((m) => m).where((q) => q.domain == domain).length;

  Widget _results() {
    final bundle = _bundle;
    final scoring = ExamScoring(bundle.exam.scoring);
    final domains = [
      for (final d in bundle.domainIds)
        if (_totalIn(d) > 0) d,
    ];
    final sectionScores = {
      for (final d in domains)
        d: scoring.sectionScore(_correctIn(d), _totalIn(d)),
    };
    final composite = scoring.composite(sectionScores);
    final compositeDomains = scoring.compositeDomains(domains);
    final scheme = Theme.of(context).colorScheme;
    return Scaffold(
      appBar: AppBar(
        title: const Text('Test results'),
        automaticallyImplyLeading: false,
      ),
      body: ListView(
        padding: kPagePadding,
        children: [
          Gap.m,
          AppCard(
            color: scheme.primaryContainer,
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                Text(
                  bundle.exam.scoring.compositeLabel,
                  style: const TextStyle(fontWeight: FontWeight.w700),
                ),
                Text(
                  scoring.formatSection(composite),
                  style: const TextStyle(
                    fontSize: 44,
                    fontWeight: FontWeight.w900,
                  ),
                ),
                Text(
                  '${scoring.compositeCaption(domains)} — an estimate based on '
                  'raw correct answers.',
                ),
                if (compositeDomains.length < domains.length)
                  Padding(
                    padding: const EdgeInsets.only(top: 4),
                    child: Text(
                      'Composite counts: '
                      '${compositeDomains.map(bundle.domainName).join(', ')}.',
                      style: Theme.of(context).textTheme.bodySmall,
                    ),
                  ),
              ],
            ),
          ),
          Gap.m,
          Wrap(
            spacing: 8,
            runSpacing: 8,
            children: [
              for (final (i, d) in domains.indexed)
                SizedBox(
                  width:
                      (MediaQuery.of(context).size.width -
                          kPagePadding.horizontal -
                          8) /
                      2,
                  child: _ScoreCard(
                    label: bundle.domainName(d),
                    score: scoring.formatSection(sectionScores[d]!),
                    detail: '${_correctIn(d)} / ${_totalIn(d)} correct',
                    color: AppTheme.domainColor(
                      bundle.domainIndex(d) < 0 ? i : bundle.domainIndex(d),
                    ),
                  ),
                ),
            ],
          ),
          Gap.l,
          const Text(
            'Your answers also updated your XP, skill mastery, and review queue. '
            'Missed questions were added to spaced review.',
          ),
          Gap.l,
          FilledButton(
            onPressed: () => context.go('/home'),
            child: const Text('Back to home'),
          ),
        ],
      ),
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
    return InkWell(
      onTap: onTap,
      borderRadius: BorderRadius.circular(8),
      child: Container(
        width: 40,
        height: 40,
        alignment: Alignment.center,
        decoration: BoxDecoration(
          color: bg,
          borderRadius: BorderRadius.circular(8),
          border: flagged ? Border.all(color: AppTheme.streak, width: 2) : null,
        ),
        child: Text(
          '$number',
          style: TextStyle(
            fontWeight: FontWeight.w700,
            color: current ? scheme.onPrimary : null,
          ),
        ),
      ),
    );
  }
}

class _ScoreCard extends StatelessWidget {
  const _ScoreCard({
    required this.label,
    required this.score,
    required this.detail,
    required this.color,
  });
  final String label;
  final String score;
  final String detail;
  final Color color;

  @override
  Widget build(BuildContext context) => AppCard(
    color: color.withValues(alpha: 0.12),
    child: Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        Text(label, style: const TextStyle(fontWeight: FontWeight.w700)),
        Gap.xs,
        Text(
          score,
          style: const TextStyle(fontSize: 28, fontWeight: FontWeight.w900),
        ),
        Text(detail, style: Theme.of(context).textTheme.bodySmall),
      ],
    ),
  );
}
