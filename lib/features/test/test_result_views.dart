import 'package:flutter/material.dart';

import '../../design/theme.dart';
import '../../design/widgets.dart';
import '../../domain/models/exam.dart';
import '../../domain/services/scoring.dart';
import '../../domain/services/timed_test.dart';

/// The pause between two timed modules: what was just finished, a module
/// progress strip, what comes next, and a start button. Stateless so it can
/// be previewed and tested on its own.
class ModuleTransitionView extends StatelessWidget {
  const ModuleTransitionView({
    super.key,
    required this.title,
    required this.note,
    required this.completed,
    required this.totalModules,
    required this.nextName,
    required this.nextCount,
    required this.nextMinutes,
    required this.startLabel,
    required this.onStart,
  });

  final String title;
  final String note;

  /// Modules finished so far (the strip fills this many segments).
  final int completed;
  final int totalModules;
  final String nextName;
  final int nextCount;
  final int nextMinutes;
  final String startLabel;
  final VoidCallback onStart;

  @override
  Widget build(BuildContext context) {
    final scheme = Theme.of(context).colorScheme;
    return Scaffold(
      body: SafeArea(
        child: Center(
          child: SingleChildScrollView(
            padding: kPagePadding,
            child: Column(
              mainAxisSize: MainAxisSize.min,
              children: [
                Icon(
                  Icons.check_circle_rounded,
                  size: 64,
                  color: AppColors.of(context).correct,
                ),
                Gap.m,
                Text(
                  title,
                  textAlign: TextAlign.center,
                  style: Theme.of(context).textTheme.headlineSmall?.copyWith(
                    fontWeight: FontWeight.w800,
                  ),
                ),
                Gap.s,
                Text(
                  'Module $completed of $totalModules done',
                  style: TextStyle(color: scheme.onSurfaceVariant),
                ),
                Gap.s,
                _ModuleStrip(done: completed, total: totalModules),
                Gap.l,
                Text(note, textAlign: TextAlign.center),
                Gap.l,
                AppCard(
                  child: Row(
                    children: [
                      Icon(Icons.timer_outlined, color: scheme.primary),
                      Gap.m,
                      Expanded(
                        child: Column(
                          crossAxisAlignment: CrossAxisAlignment.start,
                          children: [
                            Text(
                              'Up next',
                              style: Theme.of(context).textTheme.bodySmall,
                            ),
                            Text(
                              nextName,
                              style: const TextStyle(
                                fontWeight: FontWeight.w800,
                              ),
                            ),
                            Text('$nextCount questions · $nextMinutes min'),
                          ],
                        ),
                      ),
                    ],
                  ),
                ),
                Gap.l,
                FilledButton(onPressed: onStart, child: Text(startLabel)),
              ],
            ),
          ),
        ),
      ),
    );
  }
}

class _ModuleStrip extends StatelessWidget {
  const _ModuleStrip({required this.done, required this.total});
  final int done;
  final int total;

  @override
  Widget build(BuildContext context) {
    final scheme = Theme.of(context).colorScheme;
    return Row(
      mainAxisAlignment: MainAxisAlignment.center,
      children: [
        for (var i = 0; i < total; i++)
          Container(
            width: 36,
            height: 8,
            margin: const EdgeInsets.symmetric(horizontal: 3),
            decoration: BoxDecoration(
              color: i < done ? scheme.primary : scheme.surfaceContainerHighest,
              borderRadius: BorderRadius.circular(4),
            ),
          ),
      ],
    );
  }
}

/// End-of-test results: the headline total/composite, one card per section
/// (score, raw correct and, on adaptive tests, which module 2 was taken) and
/// an honest "this is an estimate" note.
class TestResultsView extends StatelessWidget {
  const TestResultsView({
    super.key,
    required this.report,
    required this.scoring,
    required this.compositeLabel,
    required this.adaptive,
    required this.domainName,
    required this.domainColor,
    required this.onDone,
  });

  final TimedTestReport report;
  final ExamScoring scoring;
  final String compositeLabel;

  /// Whether sections were routed (adds the module-2 line and route caveat).
  final bool adaptive;
  final String Function(String domain) domainName;
  final Color Function(String domain) domainColor;
  final VoidCallback onDone;

  /// The caveat under the scores, worded for the exam's scale.
  String get estimateNote => switch (scoring.spec.scale) {
    ScoreScale.sat1600 =>
      'Estimate only, not an official score. We convert your raw correct '
          'answers with our own curve, shaped like published practice-test '
          'tables${adaptive ? ', and adjust for which second module you got '
                    '(the easier one tops out at ${ExamScoring.satEasierCap} '
                    'per section)' : ''}. Real scores are equated for each '
          'test form, so yours could land a bit higher or lower.',
    ScoreScale.act36 =>
      'Estimate only, not an official score. We convert your raw correct '
          'answers with our own curve, shaped like published practice-test '
          'tables. Real scores are equated for each test form, so yours '
          'could land a bit higher or lower.',
    ScoreScale.percent =>
      'Percent correct per section; not a scaled exam score.',
  };

  @override
  Widget build(BuildContext context) {
    final scheme = Theme.of(context).colorScheme;
    final domains = report.domains;
    final compositeDomains = scoring.compositeDomains(domains);
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
                  compositeLabel,
                  style: const TextStyle(fontWeight: FontWeight.w700),
                ),
                Text(
                  scoring.formatSection(report.composite),
                  style: const TextStyle(
                    fontSize: 44,
                    fontWeight: FontWeight.w900,
                  ),
                ),
                Text(scoring.compositeCaption(domains)),
                if (compositeDomains.length < domains.length)
                  Padding(
                    padding: const EdgeInsets.only(top: 4),
                    child: Text(
                      'Composite counts: '
                      '${compositeDomains.map(domainName).join(', ')}.',
                      style: Theme.of(context).textTheme.bodySmall,
                    ),
                  ),
              ],
            ),
          ),
          Gap.m,
          LayoutBuilder(
            builder: (context, box) => Wrap(
              spacing: 8,
              runSpacing: 8,
              children: [
                for (final s in report.sections)
                  SizedBox(
                    width: (box.maxWidth - 8) / 2,
                    child: _ScoreCard(
                      label: domainName(s.domain),
                      score: scoring.formatSection(s.score),
                      detail: '${s.correct} / ${s.total} correct',
                      route: adaptive ? _routeLabel(s.route) : null,
                      color: domainColor(s.domain),
                    ),
                  ),
              ],
            ),
          ),
          Gap.m,
          Row(
            crossAxisAlignment: CrossAxisAlignment.start,
            children: [
              Icon(
                Icons.info_outline_rounded,
                size: 18,
                color: scheme.onSurfaceVariant,
              ),
              Gap.s,
              Expanded(
                child: Text(
                  estimateNote,
                  style: Theme.of(context).textTheme.bodySmall,
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
          FilledButton(onPressed: onDone, child: const Text('Back to home')),
        ],
      ),
    );
  }

  static String? _routeLabel(SectionRoute r) => switch (r) {
    SectionRoute.harder => 'Module 2: harder set',
    SectionRoute.easier => 'Module 2: easier set',
    SectionRoute.linear => null,
  };
}

class _ScoreCard extends StatelessWidget {
  const _ScoreCard({
    required this.label,
    required this.score,
    required this.detail,
    required this.color,
    this.route,
  });
  final String label;
  final String score;
  final String detail;
  final String? route;
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
        if (route != null)
          Text(route!, style: Theme.of(context).textTheme.bodySmall),
      ],
    ),
  );
}
