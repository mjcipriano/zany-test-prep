import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:go_router/go_router.dart';

import '../../app/app_controller.dart';
import '../../design/theme.dart';
import '../../design/widgets.dart';
import '../../domain/models/content_bundle.dart';
import '../../domain/models/progress.dart';
import '../../domain/services/leveling.dart';

/// A progress dashboard: totals, an estimated SAT score, daily XP, a streak
/// calendar, and accuracy by domain and skill — all from local data.
class DashboardScreen extends ConsumerWidget {
  const DashboardScreen({super.key});

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    final data = ref.watch(appControllerProvider).valueOrNull;
    if (data == null) {
      return const Scaffold(body: Center(child: CircularProgressIndicator()));
    }
    final s = _Stats.from(data.progress, data.bundle);
    final scheme = Theme.of(context).colorScheme;

    return Scaffold(
      appBar: AppBar(title: const Text('Your progress')),
      body: ListView(
        padding: kPagePadding,
        children: [
          // Estimated score.
          AppCard(
            color: scheme.primaryContainer,
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                const Text(
                  'Estimated SAT score',
                  style: TextStyle(fontWeight: FontWeight.w700),
                ),
                Gap.xs,
                Text(
                  '${s.predictedTotal}',
                  style: const TextStyle(
                    fontSize: 40,
                    fontWeight: FontWeight.w900,
                  ),
                ),
                Text(
                  'Reading & Writing ${s.predictedRW}  •  Math ${s.predictedMath}',
                  style: TextStyle(color: scheme.onPrimaryContainer),
                ),
                Gap.xs,
                Text(
                  'A rough estimate from your accuracy so far — practice more to '
                  'sharpen it.',
                  style: Theme.of(context).textTheme.bodySmall,
                ),
              ],
            ),
          ),
          Gap.m,
          // Totals grid.
          Row(
            children: [
              Expanded(
                child: _stat(
                  'Level',
                  '${s.level}',
                  Icons.military_tech_rounded,
                  scheme.primary,
                ),
              ),
              Gap.s,
              Expanded(
                child: _stat(
                  'Total XP',
                  '${s.totalXp}',
                  Icons.bolt_rounded,
                  AppTheme.xpGold,
                ),
              ),
            ],
          ),
          Gap.s,
          Row(
            children: [
              Expanded(
                child: _stat(
                  'Streak',
                  '${s.streak}',
                  Icons.local_fire_department_rounded,
                  AppTheme.streak,
                ),
              ),
              Gap.s,
              Expanded(
                child: _stat(
                  'Survival best',
                  '${s.survivalBest}',
                  Icons.bolt_rounded,
                  AppTheme.incorrect,
                ),
              ),
            ],
          ),
          Gap.s,
          Row(
            children: [
              Expanded(
                child: _stat(
                  'Questions',
                  '${s.questionsAnswered}',
                  Icons.help_outline_rounded,
                  scheme.tertiary,
                ),
              ),
              Gap.s,
              Expanded(
                child: _stat(
                  'Accuracy',
                  '${(s.overallAccuracy * 100).round()}%',
                  Icons.track_changes_rounded,
                  AppTheme.correct,
                ),
              ),
            ],
          ),
          Gap.l,
          const SectionLabel('XP — last 14 days'),
          AppCard(
            child: SizedBox(
              height: 120,
              child: s.last14.every((v) => v == 0)
                  ? const Center(
                      child: Text('No activity yet — finish a lesson!'),
                    )
                  : CustomPaint(
                      painter: _BarChartPainter(s.last14, scheme.primary),
                      child: const SizedBox.expand(),
                    ),
            ),
          ),
          Gap.l,
          const SectionLabel('Activity — last 10 weeks'),
          AppCard(
            child: _Heatmap(days: s.heatmap, color: AppTheme.correct),
          ),
          Gap.l,
          const SectionLabel('Accuracy by domain'),
          _domainBar(
            'Reading & Writing',
            s.rwAccuracy,
            s.rwAttempts,
            AppTheme.seed,
            context,
          ),
          _domainBar(
            'Math',
            s.mathAccuracy,
            s.mathAttempts,
            AppTheme.correct,
            context,
          ),
          if (s.weakestSkills.isNotEmpty) ...[
            Gap.l,
            const SectionLabel('Focus next (weakest skills)'),
            ...s.weakestSkills.map(
              (e) => Padding(
                padding: const EdgeInsets.only(bottom: 8),
                child: Row(
                  children: [
                    Expanded(child: Text(e.name)),
                    Text(
                      '${(e.accuracy * 100).round()}%',
                      style: const TextStyle(fontWeight: FontWeight.w700),
                    ),
                  ],
                ),
              ),
            ),
            Gap.s,
            FilledButton.icon(
              onPressed: () => context.push('/skills'),
              icon: const Icon(Icons.insights_rounded),
              label: const Text('See all skills'),
            ),
          ],
          Gap.xl,
        ],
      ),
    );
  }

  Widget _stat(String label, String value, IconData icon, Color color) =>
      _StatTile(label: label, value: value, icon: icon, color: color);

  Widget _domainBar(
    String name,
    double acc,
    int attempts,
    Color color,
    BuildContext c,
  ) => Padding(
    padding: const EdgeInsets.only(bottom: 10),
    child: Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        Row(
          children: [
            Expanded(
              child: Text(
                name,
                style: const TextStyle(fontWeight: FontWeight.w600),
              ),
            ),
            Text(
              attempts == 0 ? '—' : '${(acc * 100).round()}%  ($attempts)',
              style: Theme.of(c).textTheme.bodySmall,
            ),
          ],
        ),
        Gap.xs,
        ProgressBar(value: attempts == 0 ? 0 : acc, color: color, height: 10),
      ],
    ),
  );
}

class _StatTile extends StatelessWidget {
  const _StatTile({
    required this.label,
    required this.value,
    required this.icon,
    required this.color,
  });
  final String label;
  final String value;
  final IconData icon;
  final Color color;
  @override
  Widget build(BuildContext context) => AppCard(
    color: color.withValues(alpha: 0.12),
    child: Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        Icon(icon, color: color),
        Gap.xs,
        Text(
          value,
          style: const TextStyle(fontSize: 22, fontWeight: FontWeight.w800),
        ),
        Text(label, style: Theme.of(context).textTheme.bodySmall),
      ],
    ),
  );
}

class _SkillAcc {
  _SkillAcc(this.name, this.accuracy, this.attempts);
  final String name;
  final double accuracy;
  final int attempts;
}

class _Stats {
  _Stats({
    required this.level,
    required this.totalXp,
    required this.streak,
    required this.survivalBest,
    required this.questionsAnswered,
    required this.overallAccuracy,
    required this.rwAccuracy,
    required this.mathAccuracy,
    required this.rwAttempts,
    required this.mathAttempts,
    required this.predictedRW,
    required this.predictedMath,
    required this.last14,
    required this.heatmap,
    required this.weakestSkills,
  });

  final int level, totalXp, streak, survivalBest, questionsAnswered;
  final double overallAccuracy, rwAccuracy, mathAccuracy;
  final int rwAttempts, mathAttempts;
  final int predictedRW, predictedMath;
  final List<int> last14;
  final List<int> heatmap; // xp per day, oldest..today
  final List<_SkillAcc> weakestSkills;

  int get predictedTotal => predictedRW + predictedMath;

  static int _score(double acc, int attempts) =>
      attempts == 0 ? 250 : (200 + acc * 600).round();

  static _Stats from(AppProgress p, ContentBundle bundle) {
    const level = LevelEngine();
    var answered = 0, correct = 0, rwA = 0, rwC = 0, mA = 0, mC = 0;
    final bySkillCorrect = <String, int>{};
    final bySkillAtt = <String, int>{};
    for (final st in p.questionStats.values) {
      final q = bundle.question(st.questionId);
      if (q == null) continue;
      answered += st.attempts;
      correct += st.correct;
      if (q.domain == 'math') {
        mA += st.attempts;
        mC += st.correct;
      } else {
        rwA += st.attempts;
        rwC += st.correct;
      }
      bySkillAtt[q.skill] = (bySkillAtt[q.skill] ?? 0) + st.attempts;
      bySkillCorrect[q.skill] = (bySkillCorrect[q.skill] ?? 0) + st.correct;
    }
    final weak = <_SkillAcc>[];
    bySkillAtt.forEach((skill, att) {
      if (att >= 4) {
        weak.add(
          _SkillAcc(
            bundle.skillName(skill),
            (bySkillCorrect[skill] ?? 0) / att,
            att,
          ),
        );
      }
    });
    weak.sort((a, b) => a.accuracy.compareTo(b.accuracy));

    String dk(DateTime d) => dayKey(d);
    final today = DateTime.now();
    final last14 = [
      for (var i = 13; i >= 0; i--)
        p.history[dk(today.subtract(Duration(days: i)))]?.xp ?? 0,
    ];
    final heatmap = [
      for (var i = 69; i >= 0; i--)
        p.history[dk(today.subtract(Duration(days: i)))]?.xp ?? 0,
    ];

    return _Stats(
      level: level.levelForXp(p.game.totalXp),
      totalXp: p.game.totalXp,
      streak: p.game.currentStreak,
      survivalBest: p.game.survivalBest,
      questionsAnswered: answered,
      overallAccuracy: answered == 0 ? 0 : correct / answered,
      rwAccuracy: rwA == 0 ? 0 : rwC / rwA,
      mathAccuracy: mA == 0 ? 0 : mC / mA,
      rwAttempts: rwA,
      mathAttempts: mA,
      predictedRW: _score(rwA == 0 ? 0 : rwC / rwA, rwA),
      predictedMath: _score(mA == 0 ? 0 : mC / mA, mA),
      last14: last14,
      heatmap: heatmap,
      weakestSkills: weak.take(5).toList(),
    );
  }
}

class _BarChartPainter extends CustomPainter {
  _BarChartPainter(this.values, this.color);
  final List<int> values;
  final Color color;

  @override
  void paint(Canvas canvas, Size size) {
    final maxV = values.fold<int>(1, (m, v) => v > m ? v : m);
    final n = values.length;
    final gap = 4.0;
    final barW = (size.width - gap * (n - 1)) / n;
    final paint = Paint()..color = color;
    final faint = Paint()..color = color.withValues(alpha: 0.18);
    for (var i = 0; i < n; i++) {
      final h = (values[i] / maxV) * (size.height - 6);
      final x = i * (barW + gap);
      final track = Rect.fromLTWH(x, 0, barW, size.height);
      canvas.drawRRect(
        RRect.fromRectAndRadius(track, const Radius.circular(3)),
        faint,
      );
      if (values[i] > 0) {
        final bar = Rect.fromLTWH(x, size.height - h, barW, h);
        canvas.drawRRect(
          RRect.fromRectAndRadius(bar, const Radius.circular(3)),
          paint,
        );
      }
    }
  }

  @override
  bool shouldRepaint(covariant _BarChartPainter old) => old.values != values;
}

class _Heatmap extends StatelessWidget {
  const _Heatmap({required this.days, required this.color});
  final List<int> days; // 70 values oldest..today
  final Color color;

  @override
  Widget build(BuildContext context) {
    final maxV = days.fold<int>(1, (m, v) => v > m ? v : m);
    final base = Theme.of(context).colorScheme.surfaceContainerHighest;
    // 10 columns (weeks) x 7 rows (days).
    return LayoutBuilder(
      builder: (context, c) {
        const cols = 10, rows = 7, gap = 4.0;
        final cell = (c.maxWidth - gap * (cols - 1)) / cols;
        return SizedBox(
          height: rows * cell + (rows - 1) * gap,
          child: Stack(
            children: [
              for (var i = 0; i < days.length; i++)
                Positioned(
                  left: (i ~/ rows) * (cell + gap),
                  top: (i % rows) * (cell + gap),
                  child: Container(
                    width: cell,
                    height: cell,
                    decoration: BoxDecoration(
                      color: days[i] == 0
                          ? base
                          : color.withValues(
                              alpha: 0.3 + 0.7 * (days[i] / maxV),
                            ),
                      borderRadius: BorderRadius.circular(3),
                    ),
                  ),
                ),
            ],
          ),
        );
      },
    );
  }
}
