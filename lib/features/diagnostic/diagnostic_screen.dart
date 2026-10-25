import 'dart:math';

import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:go_router/go_router.dart';

import '../../app/app_controller.dart';
import '../../design/theme.dart';
import '../../design/widgets.dart';
import '../../domain/models/content_bundle.dart';
import '../../domain/models/question.dart';
import '../../domain/services/answer_checker.dart';
import '../../domain/services/diagnostic_engine.dart';
import '../../domain/services/game_service.dart';
import '../lessons/question_view.dart';

/// The placement check: a short quiz (one question per skill, spread across
/// the exam's domains and sections) with no feedback, no XP and no penalties.
/// Seeds per-skill mastery estimates via [DiagnosticEngine] and ends with a
/// friendly "Strong / Focus" summary.
///
/// Offered at the end of onboarding, by the Home card until taken, and any
/// time from Home ("Placement check") or Settings.
class DiagnosticScreen extends ConsumerStatefulWidget {
  const DiagnosticScreen({super.key, this.rng});

  /// Question picker randomness (tests and previews pass a seeded one).
  final Random? rng;

  @override
  ConsumerState<DiagnosticScreen> createState() => _DiagnosticScreenState();
}

class _DiagnosticScreenState extends ConsumerState<DiagnosticScreen> {
  static const _checker = AnswerChecker();
  static const _engine = DiagnosticEngine();

  late List<Question> _questions;
  int _index = 0;
  String? _selected;
  final _text = TextEditingController();
  final List<AnswerResult> _results = [];
  DiagnosticSummary? _summary;
  bool _submitting = false;

  @override
  void initState() {
    super.initState();
    _text.addListener(() {
      if (_summary == null && _question.type.isStudentProduced) {
        setState(() {});
      }
    });
    final bundle = ref.read(appControllerProvider).valueOrNull?.bundle;
    _questions = bundle == null
        ? []
        : _engine.pick(bundle, widget.rng ?? Random());
  }

  Question get _question => _questions[_index];

  bool get _canAnswer => _question.type.isStudentProduced
      ? _text.text.trim().isNotEmpty
      : _selected != null;

  @override
  void dispose() {
    _text.dispose();
    super.dispose();
  }

  /// Records the current answer ([dontKnow] counts as a miss) and moves on.
  Future<void> _next({bool dontKnow = false}) async {
    if (_submitting) return;
    final correct =
        !dontKnow &&
        _checker.isCorrect(
          _question,
          choiceId: _selected,
          produced: _text.text,
        );
    _results.add(AnswerResult(question: _question, correct: correct));
    if (_index < _questions.length - 1) {
      setState(() {
        _index += 1;
        _selected = null;
        _text.clear();
      });
      return;
    }
    setState(() => _submitting = true);
    final notifier = ref.read(appControllerProvider.notifier);
    await notifier.applyDiagnostic(results: _results);
    if (!mounted) return;
    final bundle = ref.read(appControllerProvider).requireValue.bundle;
    setState(() {
      _summary = _engine.summarize(bundle, _results);
      _submitting = false;
    });
  }

  @override
  Widget build(BuildContext context) {
    if (_questions.isEmpty) {
      return const Scaffold(body: Center(child: CircularProgressIndicator()));
    }
    final summary = _summary;
    return Scaffold(
      body: SafeArea(
        child: summary == null
            ? _quiz()
            : DiagnosticSummaryView(
                summary: summary,
                bundle: ref.watch(appControllerProvider).requireValue.bundle,
                onDone: () => context.go('/home'),
              ),
      ),
    );
  }

  Widget _quiz() {
    final total = _questions.length;
    final scheme = Theme.of(context).colorScheme;
    return Column(
      children: [
        Padding(
          padding: const EdgeInsets.fromLTRB(12, 8, 16, 8),
          child: Row(
            children: [
              IconButton(
                tooltip: 'Leave the check',
                icon: const Icon(Icons.close_rounded),
                onPressed: () => context.go('/home'),
              ),
              Expanded(child: ProgressBar(value: (_index + 1) / total)),
              const SizedBox(width: 12),
              Text(
                '${_index + 1}/$total',
                style: const TextStyle(fontWeight: FontWeight.w700),
              ),
            ],
          ),
        ),
        Padding(
          padding: const EdgeInsets.symmetric(horizontal: 20),
          child: Row(
            children: [
              Icon(Icons.explore_rounded, size: 18, color: scheme.primary),
              Gap.s,
              const Expanded(
                child: Text(
                  'Placement check — no XP, no penalties. Just your best guess.',
                  style: TextStyle(fontWeight: FontWeight.w700),
                ),
              ),
            ],
          ),
        ),
        Expanded(
          child: QuestionView(
            question: _question,
            answered: false,
            selectedChoiceId: _selected,
            textController: _text,
            onSelectChoice: (id) => setState(() => _selected = id),
          ),
        ),
        Padding(
          padding: const EdgeInsets.fromLTRB(20, 8, 20, 20),
          child: Row(
            children: [
              TextButton(
                onPressed: _submitting ? null : () => _next(dontKnow: true),
                child: const Text('Not sure'),
              ),
              Gap.s,
              Expanded(
                child: FilledButton(
                  onPressed: (_canAnswer && !_submitting) ? _next : null,
                  child: _submitting
                      ? const SizedBox(
                          height: 22,
                          width: 22,
                          child: CircularProgressIndicator(strokeWidth: 2),
                        )
                      : Text(_index == total - 1 ? 'Finish' : 'Next'),
                ),
              ),
            ],
          ),
        ),
      ],
    );
  }
}

/// The friendly results page: score, a bar per domain, then "Strong" and
/// "Focus" skill chips.
class DiagnosticSummaryView extends StatelessWidget {
  const DiagnosticSummaryView({
    super.key,
    required this.summary,
    required this.bundle,
    required this.onDone,
  });

  final DiagnosticSummary summary;
  final ContentBundle bundle;
  final VoidCallback onDone;

  @override
  Widget build(BuildContext context) {
    final theme = Theme.of(context);
    final strong = summary.strong.take(3).toList();
    final focus = summary.focus.take(3).toList();
    return Column(
      children: [
        Expanded(
          child: ListView(
            padding: kPagePadding,
            children: [
              Gap.s,
              Center(
                child: Column(
                  children: [
                    const Text('🧭', style: TextStyle(fontSize: 40)),
                    Text(
                      'Your starting point',
                      style: theme.textTheme.headlineSmall?.copyWith(
                        fontWeight: FontWeight.w800,
                      ),
                    ),
                    Gap.xs,
                    Text(
                      'You got ${summary.correct} of ${summary.total} right.',
                      style: theme.textTheme.bodyLarge,
                    ),
                  ],
                ),
              ),
              Gap.m,
              AppCard(
                padding: const EdgeInsets.symmetric(
                  horizontal: 16,
                  vertical: 10,
                ),
                child: Column(
                  children: [
                    for (final d in summary.domains)
                      Padding(
                        padding: const EdgeInsets.symmetric(vertical: 4),
                        child: Row(
                          children: [
                            SizedBox(
                              width: 120,
                              child: Text(
                                bundle.domainName(d.domain),
                                overflow: TextOverflow.ellipsis,
                                style: const TextStyle(
                                  fontWeight: FontWeight.w700,
                                ),
                              ),
                            ),
                            Expanded(
                              child: ProgressBar(
                                value: d.total == 0 ? 0 : d.correct / d.total,
                                color: AppTheme.domainColor(
                                  bundle.domainIndex(d.domain),
                                ),
                              ),
                            ),
                            const SizedBox(width: 10),
                            Text('${d.correct}/${d.total}'),
                          ],
                        ),
                      ),
                  ],
                ),
              ),
              Gap.s,
              if (strong.isNotEmpty)
                _SkillGroup(
                  title: 'Strong',
                  icon: Icons.check_circle_rounded,
                  color: AppTheme.correct,
                  names: [for (final s in strong) bundle.skillName(s.skillId)],
                ),
              if (strong.isNotEmpty && focus.isNotEmpty) Gap.s,
              if (focus.isNotEmpty)
                _SkillGroup(
                  title: 'Focus',
                  icon: Icons.flag_rounded,
                  color: AppTheme.streak,
                  names: [for (final s in focus) bundle.skillName(s.skillId)],
                ),
              Gap.m,
              Text(
                'Your "Recommended for you" picks are now tuned to these '
                'results, and they keep adapting as you practice.',
                textAlign: TextAlign.center,
                style: theme.textTheme.bodyMedium?.copyWith(
                  color: theme.colorScheme.onSurfaceVariant,
                ),
              ),
              Gap.l,
            ],
          ),
        ),
        Padding(
          padding: kPagePadding,
          child: FilledButton(
            onPressed: onDone,
            child: const Text('Start learning'),
          ),
        ),
      ],
    );
  }
}

class _SkillGroup extends StatelessWidget {
  const _SkillGroup({
    required this.title,
    required this.icon,
    required this.color,
    required this.names,
  });

  final String title;
  final IconData icon;
  final Color color;
  final List<String> names;

  @override
  Widget build(BuildContext context) {
    return AppCard(
      color: color.withValues(alpha: 0.12),
      padding: const EdgeInsets.fromLTRB(16, 12, 16, 12),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Row(
            children: [
              Icon(icon, color: color),
              Gap.s,
              Text(
                title,
                style: TextStyle(
                  fontWeight: FontWeight.w800,
                  fontSize: 16,
                  color: color,
                ),
              ),
            ],
          ),
          Gap.s,
          Wrap(
            spacing: 6,
            runSpacing: 6,
            children: [
              for (final n in names)
                Chip(
                  label: Text(n),
                  visualDensity: VisualDensity.compact,
                  materialTapTargetSize: MaterialTapTargetSize.shrinkWrap,
                  labelPadding: const EdgeInsets.symmetric(horizontal: 4),
                  side: BorderSide.none,
                  backgroundColor: Theme.of(context).colorScheme.surface,
                ),
            ],
          ),
        ],
      ),
    );
  }
}
