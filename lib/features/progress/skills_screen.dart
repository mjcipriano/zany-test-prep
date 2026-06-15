import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';

import '../../app/app_controller.dart';
import '../../design/theme.dart';
import '../../design/widgets.dart';
import '../../domain/services/mastery_engine.dart';

/// Shows per-skill mastery (0-100) grouped by domain and section.
class SkillsScreen extends ConsumerWidget {
  const SkillsScreen({super.key});

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    final data = ref.watch(appControllerProvider).valueOrNull;
    if (data == null) {
      return const Scaffold(body: Center(child: CircularProgressIndicator()));
    }
    const masteryEngine = MasteryEngine();
    final masteryFor = data.progress.skillMastery;
    final overall = masteryEngine.overall(
      data.bundle.skillMap.domains
          .expand((d) => d.sections)
          .expand((s) => s.skills)
          .map((sk) => masteryFor[sk.id]?.mastery ?? 0),
    );

    return Scaffold(
      appBar: AppBar(title: const Text('Skills & Mastery')),
      body: ListView(
        padding: kPagePadding,
        children: [
          AppCard(
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                Text(
                  'Overall mastery',
                  style: Theme.of(context).textTheme.titleMedium,
                ),
                Gap.s,
                Row(
                  children: [
                    Expanded(
                      child: ProgressBar(value: overall / 100, height: 16),
                    ),
                    const SizedBox(width: 12),
                    Text(
                      '${overall.round()}%',
                      style: const TextStyle(fontWeight: FontWeight.w800),
                    ),
                  ],
                ),
              ],
            ),
          ),
          Gap.m,
          for (final domain in data.bundle.skillMap.domains) ...[
            SectionLabel(domain.name),
            for (final section in domain.sections)
              for (final skill in section.skills)
                _SkillRow(
                  name: skill.name,
                  mastery: masteryFor[skill.id]?.mastery ?? 0,
                  label: masteryEngine.label(
                    masteryFor[skill.id]?.mastery ?? 0,
                  ),
                ),
            Gap.s,
          ],
        ],
      ),
    );
  }
}

class _SkillRow extends StatelessWidget {
  const _SkillRow({
    required this.name,
    required this.mastery,
    required this.label,
  });
  final String name;
  final double mastery;
  final String label;

  @override
  Widget build(BuildContext context) {
    final color = mastery >= 80
        ? AppTheme.correct
        : mastery >= 50
        ? AppTheme.seed
        : mastery >= 20
        ? AppTheme.streak
        : Theme.of(context).colorScheme.outline;
    return Padding(
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
                label,
                style: Theme.of(context).textTheme.bodySmall?.copyWith(
                  color: color,
                  fontWeight: FontWeight.w700,
                ),
              ),
            ],
          ),
          Gap.xs,
          ProgressBar(value: mastery / 100, color: color, height: 8),
        ],
      ),
    );
  }
}
