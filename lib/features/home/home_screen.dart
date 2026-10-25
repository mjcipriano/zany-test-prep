import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:go_router/go_router.dart';

import '../../app/app_controller.dart';
import '../../design/theme.dart';
import '../../design/widgets.dart';
import '../../domain/models/content_bundle.dart';
import '../../domain/models/lesson.dart';
import '../../domain/models/progress.dart';
import '../../domain/services/leveling.dart';
import '../../domain/services/recommendation_engine.dart';
import '../../domain/services/review_engine.dart';
import '../../domain/services/streak_engine.dart';
import '../../domain/services/unlock_engine.dart';
import '../lessons/lesson_resume_badge.dart';

class HomeScreen extends ConsumerWidget {
  const HomeScreen({super.key});

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    final data = ref.watch(appControllerProvider).valueOrNull;
    if (data == null || data.profile == null) {
      return const Scaffold(body: Center(child: CircularProgressIndicator()));
    }
    final bundle = data.bundle;
    final progress = data.progress;
    const level = LevelEngine();
    const streak = StreakEngine();
    const unlock = UnlockEngine();

    final totalXp = progress.game.totalXp;
    final lvl = level.levelForXp(totalXp);
    final shownStreak = streak.displayedStreak(
      lastActiveDay: progress.game.lastActiveDay,
      currentStreak: progress.game.currentStreak,
      today: DateTime.now(),
    );
    final goalXp = data.profile!.dailyGoalXp;
    final dailyXp = progress.game.dailyDay == dayKey(DateTime.now())
        ? progress.game.dailyXp
        : 0;
    final suggested = unlock.suggestNext(bundle, progress);
    const review = ReviewEngine();
    final reviewCount = review.dueCount(progress, bundle: bundle);
    final recommendation = const RecommendationEngine().recommend(
      bundle,
      progress,
      now: DateTime.now(),
    );

    return Scaffold(
      appBar: AppBar(
        title: Row(
          children: [
            // Ellipsize rather than overflow on narrow (360dp) phones.
            const Flexible(
              child: Text(
                'Zany Test Prep',
                overflow: TextOverflow.ellipsis,
                style: TextStyle(fontWeight: FontWeight.w800),
              ),
            ),
            Gap.s,
            Container(
              padding: const EdgeInsets.symmetric(horizontal: 8, vertical: 2),
              decoration: BoxDecoration(
                color: Theme.of(context).colorScheme.primaryContainer,
                borderRadius: BorderRadius.circular(10),
              ),
              child: Text(
                bundle.exam.name,
                style: TextStyle(
                  fontSize: 12,
                  fontWeight: FontWeight.w800,
                  color: Theme.of(context).colorScheme.onPrimaryContainer,
                ),
              ),
            ),
          ],
        ),
        // Rewards and Settings stay one tap away; Progress and Achievements
        // live in the overflow menu so the title fits on 360dp phones.
        actions: [
          IconButton(
            tooltip: progress.game.unopenedChests > 0
                ? 'Rewards, ${progress.game.unopenedChests} '
                      'chest${progress.game.unopenedChests == 1 ? '' : 's'} '
                      'to open'
                : 'Rewards',
            onPressed: () => context.push('/rewards'),
            icon: Badge(
              isLabelVisible: progress.game.unopenedChests > 0,
              label: Text('${progress.game.unopenedChests}'),
              child: const Icon(Icons.card_giftcard_rounded),
            ),
          ),
          IconButton(
            tooltip: 'Settings',
            onPressed: () => context.push('/settings'),
            icon: const Icon(Icons.settings_rounded),
          ),
          PopupMenuButton<String>(
            key: const Key('home-more-menu'),
            tooltip: 'More',
            icon: const Icon(Icons.more_vert_rounded),
            onSelected: (route) => context.push(route),
            itemBuilder: (context) => const [
              PopupMenuItem(
                value: '/dashboard',
                child: ListTile(
                  leading: Icon(Icons.bar_chart_rounded),
                  title: Text('Progress'),
                  contentPadding: EdgeInsets.zero,
                ),
              ),
              PopupMenuItem(
                value: '/achievements',
                child: ListTile(
                  leading: Icon(Icons.emoji_events_rounded),
                  title: Text('Achievements'),
                  contentPadding: EdgeInsets.zero,
                ),
              ),
            ],
          ),
        ],
      ),
      body: ListView(
        padding: kPagePadding,
        children: [
          _StatsHeader(
            level: lvl,
            xp: totalXp,
            xpIntoLevel: level.xpIntoLevel(totalXp),
            xpForNext: level.xpForNextLevel(totalXp),
            streak: shownStreak,
            dailyXp: dailyXp,
            goalXp: goalXp,
          ),
          Gap.m,
          if (!progress.game.diagnosticDoneFor(bundle.exam.id))
            Padding(
              padding: const EdgeInsets.only(bottom: 8),
              child: AppCard(
                color: Theme.of(context).colorScheme.tertiaryContainer,
                child: Column(
                  crossAxisAlignment: CrossAxisAlignment.start,
                  children: [
                    const Row(
                      children: [
                        Icon(Icons.explore_rounded),
                        Gap.s,
                        Expanded(
                          child: Text(
                            'Personalize your plan',
                            style: TextStyle(
                              fontWeight: FontWeight.w800,
                              fontSize: 16,
                            ),
                          ),
                        ),
                      ],
                    ),
                    Gap.xs,
                    const Text(
                      'Take a 3-minute placement check so we can find your '
                      'strengths and what to study first.',
                    ),
                    Gap.s,
                    Row(
                      children: [
                        Expanded(
                          child: FilledButton(
                            onPressed: () => context.push('/diagnostic'),
                            child: const Text('Take it'),
                          ),
                        ),
                        Gap.s,
                        TextButton(
                          onPressed: () => ref
                              .read(appControllerProvider.notifier)
                              .skipDiagnostic(),
                          child: const Text('Skip'),
                        ),
                      ],
                    ),
                  ],
                ),
              ),
            ),
          if (recommendation != null) ...[
            RecommendedCard(recommendation: recommendation, bundle: bundle),
            Gap.s,
          ],
          if (suggested != null)
            _ContinueCard(
              lesson: suggested,
              bundle: bundle,
              done: progress.isLessonCompleted(suggested.id),
            ),
          Gap.s,
          _QuickActions(
            actions: [
              _QuickAction(
                icon: Icons.refresh_rounded,
                label: 'Review',
                badge: reviewCount > 0 ? '$reviewCount' : null,
                semanticLabel: reviewCount > 0
                    ? 'Review, $reviewCount due'
                    : 'Review, nothing due',
                onTap: reviewCount > 0 ? () => context.push('/review') : null,
              ),
              _QuickAction(
                icon: Icons.insights_rounded,
                label: 'Skills',
                onTap: () => context.push('/skills'),
              ),
              _QuickAction(
                icon: Icons.auto_awesome_rounded,
                label: 'Smart Practice',
                onTap: () => context.push('/practice/smart'),
              ),
              _QuickAction(
                icon: Icons.explore_rounded,
                label: 'Placement check',
                onTap: () => context.push('/diagnostic'),
              ),
              _QuickAction(
                icon: Icons.shuffle_rounded,
                label: 'Quick Practice',
                onTap: () => context.push('/practice/unlocked'),
              ),
              _QuickAction(
                icon: Icons.whatshot_rounded,
                label: 'Challenge',
                onTap: () => context.push('/practice/all'),
              ),
              _QuickAction(
                icon: Icons.bolt_rounded,
                label: progress.game.survivalBest > 0
                    ? 'Survival · ${progress.game.survivalBest}'
                    : 'Survival',
                semanticLabel: progress.game.survivalBest > 0
                    ? 'Survival, best ${progress.game.survivalBest}'
                    : null,
                onTap: () => context.push('/survival'),
              ),
              _QuickAction(
                icon: Icons.timer_rounded,
                label: 'Practice Test',
                onTap: () => context.push('/test'),
              ),
            ],
          ),
          for (final (i, domain) in bundle.domainIds.indexed) ...[
            Gap.l,
            _DomainPath(
              title: bundle.domainName(domain),
              color: AppTheme.domainColor(i),
              lessons: bundle.lessonsForDomain(domain),
              bundle: bundle,
              progress: progress,
              unlock: unlock,
            ),
          ],
          Gap.xl,
        ],
      ),
    );
  }
}

class _StatsHeader extends StatelessWidget {
  const _StatsHeader({
    required this.level,
    required this.xp,
    required this.xpIntoLevel,
    required this.xpForNext,
    required this.streak,
    required this.dailyXp,
    required this.goalXp,
  });

  final int level;
  final int xp;
  final int xpIntoLevel;
  final int xpForNext;
  final int streak;
  final int dailyXp;
  final int goalXp;

  @override
  Widget build(BuildContext context) {
    final goalProgress = goalXp == 0 ? 0.0 : dailyXp / goalXp;
    return AppCard(
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Row(
            crossAxisAlignment: CrossAxisAlignment.start,
            children: [
              // Wraps onto a second line at large text sizes.
              Expanded(
                child: Wrap(
                  spacing: 8,
                  runSpacing: 8,
                  children: [
                    StatPill(
                      icon: Icons.local_fire_department_rounded,
                      value: '$streak',
                      color: AppTheme.streak,
                      semanticLabel: '$streak day streak',
                    ),
                    StatPill(
                      icon: Icons.bolt_rounded,
                      value: '$xp XP',
                      color: AppTheme.xpGold,
                      semanticLabel: '$xp total XP',
                    ),
                  ],
                ),
              ),
              Gap.s,
              StatPill(
                icon: Icons.military_tech_rounded,
                value: 'Lvl $level',
                color: Theme.of(context).colorScheme.primary,
                semanticLabel: 'Level $level',
              ),
            ],
          ),
          Gap.m,
          Row(
            children: [
              Expanded(
                child: Text(
                  'Daily goal',
                  style: Theme.of(context).textTheme.labelLarge,
                ),
              ),
              Text(
                '$dailyXp / $goalXp XP',
                style: Theme.of(context).textTheme.labelLarge,
              ),
            ],
          ),
          Gap.xs,
          ProgressBar(
            value: goalProgress,
            color: AppTheme.streak,
            semanticLabel: 'Daily goal',
            semanticValue: '$dailyXp of $goalXp XP',
          ),
          Gap.s,
          Row(
            children: [
              Icon(
                Icons.military_tech_rounded,
                size: 16,
                color: Theme.of(context).colorScheme.primary,
              ),
              const SizedBox(width: 6),
              Expanded(
                child: ProgressBar(
                  value: xpForNext == 0 ? 0 : xpIntoLevel / xpForNext,
                  semanticLabel: 'Progress to level ${level + 1}',
                  semanticValue: '$xpIntoLevel of $xpForNext XP',
                ),
              ),
              const SizedBox(width: 8),
              ExcludeSemantics(
                child: Text(
                  '$xpIntoLevel/$xpForNext',
                  style: Theme.of(context).textTheme.bodySmall,
                ),
              ),
            ],
          ),
        ],
      ),
    );
  }
}

/// "Recommended for you": the [RecommendationEngine]'s single pick with a
/// one-line reason ("Weakest: Linear equations", "3 reviews due").
class RecommendedCard extends StatelessWidget {
  const RecommendedCard({
    super.key,
    required this.recommendation,
    required this.bundle,
  });

  final Recommendation recommendation;
  final ContentBundle bundle;

  @override
  Widget build(BuildContext context) {
    final scheme = Theme.of(context).colorScheme;
    final r = recommendation;
    final (IconData icon, String title) = switch (r.kind) {
      RecommendationKind.review => (
        Icons.refresh_rounded,
        'Review your misses',
      ),
      RecommendationKind.lesson => (
        Icons.play_arrow_rounded,
        bundle.lesson(r.lessonId ?? '')?.title ?? 'Start a new skill',
      ),
      RecommendationKind.practice => (
        Icons.auto_awesome_rounded,
        'Smart practice',
      ),
    };
    final reasonIcon = switch (r.reason) {
      RecommendationReason.reviewsDue => Icons.history_rounded,
      RecommendationReason.weakest => Icons.trending_up_rounded,
      RecommendationReason.newSkill => Icons.fiber_new_rounded,
    };
    return AppCard(
      key: const Key('recommended-card'),
      color: scheme.secondaryContainer,
      onTap: () => context.push(r.route),
      child: Row(
        children: [
          CircleAvatar(
            radius: 26,
            backgroundColor: scheme.secondary,
            child: Icon(icon, color: scheme.onSecondary),
          ),
          Gap.m,
          Expanded(
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                Text(
                  'Recommended for you',
                  style: TextStyle(color: scheme.onSecondaryContainer),
                ),
                Text(
                  title,
                  style: const TextStyle(
                    fontWeight: FontWeight.w800,
                    fontSize: 18,
                  ),
                ),
                Row(
                  children: [
                    Icon(
                      reasonIcon,
                      size: 16,
                      color: scheme.onSecondaryContainer,
                    ),
                    const SizedBox(width: 4),
                    Flexible(
                      child: Text(
                        r.label,
                        overflow: TextOverflow.ellipsis,
                        style: TextStyle(
                          color: scheme.onSecondaryContainer,
                          fontWeight: FontWeight.w600,
                        ),
                      ),
                    ),
                  ],
                ),
              ],
            ),
          ),
          const Icon(Icons.chevron_right_rounded),
        ],
      ),
    );
  }
}

class _ContinueCard extends StatelessWidget {
  const _ContinueCard({
    required this.lesson,
    required this.bundle,
    required this.done,
  });
  final Lesson lesson;
  final ContentBundle bundle;
  final bool done;

  @override
  Widget build(BuildContext context) {
    final scheme = Theme.of(context).colorScheme;
    return AppCard(
      color: scheme.primaryContainer,
      onTap: () => context.push('/lesson/${lesson.id}'),
      child: Row(
        children: [
          CircleAvatar(
            radius: 26,
            backgroundColor: scheme.primary,
            child: Icon(
              done ? Icons.replay_rounded : Icons.play_arrow_rounded,
              color: scheme.onPrimary,
            ),
          ),
          Gap.m,
          Expanded(
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                Text(
                  done ? 'Keep practicing' : 'Continue learning',
                  style: TextStyle(color: scheme.onPrimaryContainer),
                ),
                Text(
                  lesson.title,
                  style: const TextStyle(
                    fontWeight: FontWeight.w800,
                    fontSize: 18,
                  ),
                ),
                Text(
                  '${bundle.skillName(lesson.skill)} • ~${lesson.estimatedMinutes} min',
                  style: TextStyle(color: scheme.onPrimaryContainer),
                ),
              ],
            ),
          ),
          const Icon(Icons.chevron_right_rounded),
        ],
      ),
    );
  }
}

/// The Home shortcut tiles: two per row, or one per row at large text sizes
/// so labels like "Placement check" never shrink or clip.
class _QuickActions extends StatelessWidget {
  const _QuickActions({required this.actions});
  final List<_QuickAction> actions;

  @override
  Widget build(BuildContext context) {
    final perRow = MediaQuery.textScalerOf(context).scale(10) > 13 ? 1 : 2;
    final rows = <Widget>[];
    for (var i = 0; i < actions.length; i += perRow) {
      if (i > 0) rows.add(Gap.s);
      rows.add(
        perRow == 1
            ? actions[i]
            : Row(
                children: [
                  Expanded(child: actions[i]),
                  Gap.s,
                  Expanded(
                    child: i + 1 < actions.length
                        ? actions[i + 1]
                        : const SizedBox.shrink(),
                  ),
                ],
              ),
      );
    }
    return Column(
      crossAxisAlignment: CrossAxisAlignment.stretch,
      children: rows,
    );
  }
}

class _QuickAction extends StatelessWidget {
  const _QuickAction({
    required this.icon,
    required this.label,
    this.badge,
    this.semanticLabel,
    this.onTap,
  });
  final IconData icon;
  final String label;
  final String? badge;

  /// Spoken instead of [label] + [badge] ("Review, 3 due").
  final String? semanticLabel;
  final VoidCallback? onTap;

  @override
  Widget build(BuildContext context) {
    final scheme = Theme.of(context).colorScheme;
    return Semantics(
      button: true,
      enabled: onTap != null,
      label: semanticLabel ?? label,
      excludeSemantics: true,
      onTap: onTap,
      child: Opacity(
        opacity: onTap == null ? 0.5 : 1,
        child: AppCard(
          onTap: onTap,
          child: Row(
            children: [
              Icon(icon, color: scheme.primary),
              Gap.s,
              Expanded(
                // Shrink long labels ("Quick Practice") to fit 360dp phones
                // rather than ellipsizing them. (At large text sizes the tiles
                // go one per row, so this never shrinks below the user's size.)
                child: FittedBox(
                  fit: BoxFit.scaleDown,
                  alignment: Alignment.centerLeft,
                  child: Text(
                    label,
                    maxLines: 1,
                    style: const TextStyle(fontWeight: FontWeight.w700),
                  ),
                ),
              ),
              if (badge != null) ...[
                Gap.s,
                Container(
                  padding: const EdgeInsets.symmetric(
                    horizontal: 8,
                    vertical: 2,
                  ),
                  decoration: BoxDecoration(
                    color: AppColors.of(context).incorrectFill,
                    borderRadius: BorderRadius.circular(10),
                  ),
                  child: Text(
                    badge!,
                    style: const TextStyle(
                      color: Colors.white,
                      fontWeight: FontWeight.w800,
                    ),
                  ),
                ),
              ],
            ],
          ),
        ),
      ),
    );
  }
}

class _DomainPath extends StatelessWidget {
  const _DomainPath({
    required this.title,
    required this.color,
    required this.lessons,
    required this.bundle,
    required this.progress,
    required this.unlock,
  });

  final String title;
  final Color color;
  final List<Lesson> lessons;
  final ContentBundle bundle;
  final AppProgress progress;
  final UnlockEngine unlock;

  @override
  Widget build(BuildContext context) {
    return Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        SectionLabel(title),
        ...lessons.asMap().entries.map((e) {
          final i = e.key;
          final lesson = e.value;
          final unlocked = unlock.isUnlocked(lesson, progress);
          final lp = progress.lessons[lesson.id];
          return _LessonNode(
            lesson: lesson,
            bundle: bundle,
            color: color,
            unlocked: unlocked,
            completed: lp?.completed ?? false,
            stars: lp?.stars ?? 0,
            alignRight: i.isOdd,
          );
        }),
      ],
    );
  }
}

class _LessonNode extends StatelessWidget {
  const _LessonNode({
    required this.lesson,
    required this.bundle,
    required this.color,
    required this.unlocked,
    required this.completed,
    required this.stars,
    required this.alignRight,
  });

  final Lesson lesson;
  final ContentBundle bundle;
  final Color color;
  final bool unlocked;
  final bool completed;
  final int stars;
  final bool alignRight;

  @override
  Widget build(BuildContext context) {
    final scheme = Theme.of(context).colorScheme;
    final bg = !unlocked
        ? scheme.surfaceContainerHighest
        : completed
        ? color
        : color.withValues(alpha: 0.18);
    final fg = !unlocked
        ? scheme.onSurfaceVariant
        : completed
        ? Colors.white
        // The path colour on its own pale tint: nudged to stay visible (3:1).
        : AppColors.of(context).textOn(color, minRatio: 3);

    return Padding(
      padding: const EdgeInsets.symmetric(vertical: 6),
      child: Row(
        children: [
          Expanded(
            child: AppCard(
              onTap: unlocked
                  ? () => context.push('/lesson/${lesson.id}')
                  : null,
              child: Row(
                children: [
                  Container(
                    width: 52,
                    height: 52,
                    decoration: BoxDecoration(
                      color: bg,
                      shape: BoxShape.circle,
                    ),
                    child: Icon(
                      !unlocked
                          ? Icons.lock_rounded
                          : completed
                          ? Icons.check_rounded
                          : Icons.play_arrow_rounded,
                      color: fg,
                      semanticLabel: !unlocked
                          ? 'Locked'
                          : completed
                          ? 'Completed'
                          : 'Not started',
                    ),
                  ),
                  Gap.m,
                  Expanded(
                    child: Column(
                      crossAxisAlignment: CrossAxisAlignment.start,
                      children: [
                        Text(
                          lesson.title,
                          style: TextStyle(
                            fontWeight: FontWeight.w700,
                            color: unlocked ? null : scheme.onSurfaceVariant,
                          ),
                        ),
                        Text(
                          '${lesson.difficulty.label} • ${lesson.questionIds.length} questions',
                          style: Theme.of(context).textTheme.bodySmall,
                        ),
                        if (completed) CrownRow(stars: stars),
                        if (unlocked) LessonResumeBadge(lesson: lesson),
                      ],
                    ),
                  ),
                  if (unlocked) const Icon(Icons.chevron_right_rounded),
                ],
              ),
            ),
          ),
        ],
      ),
    );
  }
}
