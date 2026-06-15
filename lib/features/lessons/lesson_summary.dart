import 'package:flutter/material.dart';

import '../../design/theme.dart';
import '../../design/widgets.dart';
import '../../domain/models/question.dart';
import '../../domain/services/game_service.dart';

/// End-of-lesson celebration + summary with animated XP and mistake review.
class LessonSummary extends StatelessWidget {
  const LessonSummary({
    super.key,
    required this.outcome,
    required this.questions,
    required this.results,
    required this.onDone,
    this.isReview = false,
  });

  final LessonOutcome outcome;
  final List<Question> questions;
  final List<AnswerResult> results;
  final VoidCallback onDone;
  final bool isReview;

  @override
  Widget build(BuildContext context) {
    final scheme = Theme.of(context).colorScheme;
    final mistakes = results.where((r) => !r.correct).toList();
    return Column(
      children: [
        Expanded(
          child: ListView(
            padding: kPagePadding,
            children: [
              Gap.l,
              Center(
                child: TweenAnimationBuilder<double>(
                  tween: Tween(begin: 0.6, end: 1),
                  duration: const Duration(milliseconds: 500),
                  curve: Curves.elasticOut,
                  builder: (context, s, child) =>
                      Transform.scale(scale: s, child: child),
                  child: Column(
                    children: [
                      Text(
                        outcome.accuracy >= 0.8 ? '🎉' : '💪',
                        style: const TextStyle(fontSize: 64),
                      ),
                      Text(
                        isReview ? 'Review complete!' : 'Lesson complete!',
                        style: Theme.of(context).textTheme.headlineSmall
                            ?.copyWith(fontWeight: FontWeight.w800),
                      ),
                    ],
                  ),
                ),
              ),
              Gap.m,
              if (!isReview)
                Center(child: _AnimatedStars(stars: outcome.stars)),
              Gap.l,
              Row(
                children: [
                  Expanded(
                    child: _SummaryStat(
                      label: 'XP earned',
                      valueWidget: _CountUp(
                        value: outcome.xpGained,
                        suffix: ' XP',
                      ),
                      color: AppTheme.xpGold,
                      icon: Icons.bolt_rounded,
                    ),
                  ),
                  Gap.s,
                  Expanded(
                    child: _SummaryStat(
                      label: 'Accuracy',
                      valueWidget: Text(
                        '${(outcome.accuracy * 100).round()}%',
                        style: _bigStyle,
                      ),
                      color: AppTheme.correct,
                      icon: Icons.track_changes_rounded,
                    ),
                  ),
                ],
              ),
              Gap.s,
              Row(
                children: [
                  Expanded(
                    child: _SummaryStat(
                      label: 'Streak',
                      valueWidget: Text(
                        '${outcome.currentStreak}',
                        style: _bigStyle,
                      ),
                      color: AppTheme.streak,
                      icon: Icons.local_fire_department_rounded,
                    ),
                  ),
                  Gap.s,
                  Expanded(
                    child: _SummaryStat(
                      label: 'Score',
                      valueWidget: Text(
                        '${outcome.correct}/${outcome.total}',
                        style: _bigStyle,
                      ),
                      color: scheme.primary,
                      icon: Icons.check_circle_rounded,
                    ),
                  ),
                ],
              ),
              if (outcome.leveledUp) ...[
                Gap.m,
                _Banner(
                  color: scheme.primary,
                  icon: Icons.military_tech_rounded,
                  text: 'Level up! You reached level ${outcome.newLevel}.',
                ),
              ],
              if (outcome.dailyGoalJustMet) ...[
                Gap.s,
                const _Banner(
                  color: AppTheme.streak,
                  icon: Icons.flag_rounded,
                  text: 'Daily goal reached! Nice work.',
                ),
              ],
              if (outcome.newBadges.isNotEmpty) ...[
                Gap.m,
                const SectionLabel('New achievements'),
                ...outcome.newBadges.map(
                  (b) => AppCard(
                    child: Row(
                      children: [
                        Text(b.emoji, style: const TextStyle(fontSize: 28)),
                        Gap.m,
                        Expanded(
                          child: Column(
                            crossAxisAlignment: CrossAxisAlignment.start,
                            children: [
                              Text(
                                b.title,
                                style: const TextStyle(
                                  fontWeight: FontWeight.w800,
                                ),
                              ),
                              Text(b.description),
                            ],
                          ),
                        ),
                      ],
                    ),
                  ),
                ),
              ],
              if (mistakes.isNotEmpty) ...[
                Gap.l,
                SectionLabel('Review your mistakes (${mistakes.length})'),
                ...mistakes.map((r) => _MistakeCard(result: r)),
              ],
              Gap.xl,
            ],
          ),
        ),
        Padding(
          padding: kPagePadding,
          child: FilledButton(onPressed: onDone, child: const Text('Continue')),
        ),
      ],
    );
  }

  static const _bigStyle = TextStyle(fontSize: 24, fontWeight: FontWeight.w800);
}

class _AnimatedStars extends StatelessWidget {
  const _AnimatedStars({required this.stars});
  final int stars;

  @override
  Widget build(BuildContext context) {
    return Row(
      mainAxisAlignment: MainAxisAlignment.center,
      children: List.generate(3, (i) {
        final filled = i < stars;
        return TweenAnimationBuilder<double>(
          tween: Tween(begin: 0, end: filled ? 1 : 0.4),
          duration: Duration(milliseconds: 400 + i * 150),
          curve: Curves.elasticOut,
          builder: (context, s, child) =>
              Transform.scale(scale: s, child: child),
          child: Icon(
            filled ? Icons.star_rounded : Icons.star_outline_rounded,
            size: 56,
            color: filled ? AppTheme.xpGold : Theme.of(context).disabledColor,
          ),
        );
      }),
    );
  }
}

class _CountUp extends StatelessWidget {
  const _CountUp({required this.value, this.suffix = ''});
  final int value;
  final String suffix;

  @override
  Widget build(BuildContext context) {
    return TweenAnimationBuilder<double>(
      tween: Tween(begin: 0, end: value.toDouble()),
      duration: const Duration(milliseconds: 900),
      curve: Curves.easeOut,
      builder: (context, v, _) => Text(
        '${v.round()}$suffix',
        style: const TextStyle(fontSize: 24, fontWeight: FontWeight.w800),
      ),
    );
  }
}

class _SummaryStat extends StatelessWidget {
  const _SummaryStat({
    required this.label,
    required this.valueWidget,
    required this.color,
    required this.icon,
  });
  final String label;
  final Widget valueWidget;
  final Color color;
  final IconData icon;

  @override
  Widget build(BuildContext context) {
    return AppCard(
      color: color.withValues(alpha: 0.12),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Icon(icon, color: color),
          Gap.s,
          valueWidget,
          Text(label, style: Theme.of(context).textTheme.bodySmall),
        ],
      ),
    );
  }
}

class _Banner extends StatelessWidget {
  const _Banner({required this.color, required this.icon, required this.text});
  final Color color;
  final IconData icon;
  final String text;

  @override
  Widget build(BuildContext context) {
    return Container(
      padding: const EdgeInsets.all(14),
      decoration: BoxDecoration(
        color: color.withValues(alpha: 0.15),
        borderRadius: BorderRadius.circular(16),
      ),
      child: Row(
        children: [
          Icon(icon, color: color),
          Gap.s,
          Expanded(
            child: Text(
              text,
              style: TextStyle(color: color, fontWeight: FontWeight.w700),
            ),
          ),
        ],
      ),
    );
  }
}

class _MistakeCard extends StatelessWidget {
  const _MistakeCard({required this.result});
  final AnswerResult result;

  @override
  Widget build(BuildContext context) {
    final q = result.question;
    final answer = q.type.isStudentProduced
        ? (q.answer?.accepted.first ?? '')
        : (q.correct?.text ?? '');
    return Padding(
      padding: const EdgeInsets.only(bottom: 8),
      child: AppCard(
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            Text(
              q.prompt,
              maxLines: 3,
              overflow: TextOverflow.ellipsis,
              style: const TextStyle(fontWeight: FontWeight.w700),
            ),
            Gap.s,
            Row(
              children: [
                const Icon(
                  Icons.check_circle_rounded,
                  color: AppTheme.correct,
                  size: 18,
                ),
                const SizedBox(width: 6),
                Expanded(
                  child: Text(
                    'Answer: $answer',
                    style: const TextStyle(color: AppTheme.correct),
                  ),
                ),
              ],
            ),
            Gap.xs,
            Text(q.explanation, style: Theme.of(context).textTheme.bodySmall),
          ],
        ),
      ),
    );
  }
}
