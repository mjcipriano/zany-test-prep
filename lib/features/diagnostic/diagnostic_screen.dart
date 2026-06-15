import 'dart:math';

import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:go_router/go_router.dart';

import '../../app/app_controller.dart';
import '../../design/theme.dart';
import '../../design/widgets.dart';
import '../../domain/models/difficulty.dart';
import '../../domain/models/question.dart';
import '../../domain/services/answer_checker.dart';
import '../../domain/services/game_service.dart';
import '../lessons/question_view.dart';

/// A short placement quiz: one question per skill, no feedback. Seeds per-skill
/// mastery and shows the learner where to focus.
class DiagnosticScreen extends ConsumerStatefulWidget {
  const DiagnosticScreen({super.key});

  @override
  ConsumerState<DiagnosticScreen> createState() => _DiagnosticScreenState();
}

class _DiagnosticScreenState extends ConsumerState<DiagnosticScreen> {
  static const _checker = AnswerChecker();

  late List<Question> _questions;
  int _index = 0;
  String? _selected;
  final _text = TextEditingController();
  final List<AnswerResult> _results = [];
  bool _ended = false;
  bool _submitting = false;

  @override
  void initState() {
    super.initState();
    _text.addListener(() {
      if (_question.type.isStudentProduced) setState(() {});
    });
    _questions = _pick();
  }

  List<Question> _pick() {
    final bundle = ref.read(appControllerProvider).valueOrNull?.bundle;
    if (bundle == null) return [];
    // One question per skill (prefer medium difficulty), then balance domains.
    final bySkill = <String, Question>{};
    for (final q in bundle.questions) {
      final cur = bySkill[q.skill];
      if (cur == null ||
          (cur.difficulty != Difficulty.medium &&
              q.difficulty == Difficulty.medium)) {
        bySkill[q.skill] = q;
      }
    }
    final picks = bySkill.values.toList()..shuffle(Random());
    picks.sort(
      (a, b) => a.domain.compareTo(b.domain),
    ); // group, then interleave
    final math = picks.where((q) => q.domain == 'math').toList();
    final rw = picks.where((q) => q.domain != 'math').toList();
    final out = <Question>[];
    for (
      var i = 0;
      out.length < 16 && (i < math.length || i < rw.length);
      i++
    ) {
      if (i < rw.length) out.add(rw[i]);
      if (i < math.length) out.add(math[i]);
    }
    return out;
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

  Future<void> _next() async {
    final correct = _checker.isCorrect(
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
    } else {
      setState(() => _submitting = true);
      await ref
          .read(appControllerProvider.notifier)
          .applyDiagnostic(results: _results);
      setState(() {
        _ended = true;
        _submitting = false;
      });
    }
  }

  @override
  Widget build(BuildContext context) {
    if (_questions.isEmpty) {
      return const Scaffold(body: Center(child: CircularProgressIndicator()));
    }
    return Scaffold(body: SafeArea(child: _ended ? _results_() : _quiz()));
  }

  Widget _quiz() {
    final total = _questions.length;
    return Column(
      children: [
        Padding(
          padding: const EdgeInsets.fromLTRB(12, 8, 16, 8),
          child: Row(
            children: [
              IconButton(
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
        const Padding(
          padding: EdgeInsets.symmetric(horizontal: 20),
          child: Align(
            alignment: Alignment.centerLeft,
            child: Text(
              'Diagnostic — answer your best; no penalties.',
              style: TextStyle(fontWeight: FontWeight.w700),
            ),
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
          padding: const EdgeInsets.all(20),
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
    );
  }

  Widget _results_() {
    final bundle = ref.read(appControllerProvider).valueOrNull!.bundle;
    final correct = _results.where((r) => r.correct).length;
    final weak = _results.where((r) => !r.correct).take(5).toList();
    final strong = _results.where((r) => r.correct).take(5).toList();
    return Column(
      children: [
        Expanded(
          child: ListView(
            padding: kPagePadding,
            children: [
              Gap.l,
              Center(
                child: Column(
                  children: [
                    const Text('🧭', style: TextStyle(fontSize: 56)),
                    Text(
                      'Your starting point',
                      style: Theme.of(context).textTheme.headlineSmall
                          ?.copyWith(fontWeight: FontWeight.w800),
                    ),
                    Text(
                      'You got $correct of ${_results.length} right.',
                      style: Theme.of(context).textTheme.bodyMedium,
                    ),
                  ],
                ),
              ),
              Gap.l,
              if (weak.isNotEmpty) ...[
                const SectionLabel('Focus here first'),
                ...weak.map(
                  (r) => AppCard(
                    child: Row(
                      children: [
                        const Icon(Icons.flag_rounded, color: AppTheme.streak),
                        Gap.s,
                        Expanded(
                          child: Text(bundle.skillName(r.question.skill)),
                        ),
                      ],
                    ),
                  ),
                ),
                Gap.m,
              ],
              if (strong.isNotEmpty) ...[
                const SectionLabel('Already solid'),
                ...strong.map(
                  (r) => AppCard(
                    child: Row(
                      children: [
                        const Icon(
                          Icons.check_circle_rounded,
                          color: AppTheme.correct,
                        ),
                        Gap.s,
                        Expanded(
                          child: Text(bundle.skillName(r.question.skill)),
                        ),
                      ],
                    ),
                  ),
                ),
              ],
              Gap.xl,
            ],
          ),
        ),
        Padding(
          padding: kPagePadding,
          child: FilledButton(
            onPressed: () => context.go('/home'),
            child: const Text('Start learning'),
          ),
        ),
      ],
    );
  }
}
