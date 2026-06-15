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
import '../../domain/services/streak_engine.dart';
import '../../domain/services/unlock_engine.dart';

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
    final reviewCount = progress.reviewQueue.length;

    return Scaffold(
      appBar: AppBar(
        title: const Text(
          'Zany Test Prep',
          style: TextStyle(fontWeight: FontWeight.w800),
        ),
        actions: [
          IconButton(
            tooltip: 'Achievements',
            onPressed: () => context.push('/achievements'),
            icon: const Icon(Icons.emoji_events_rounded),
          ),
          IconButton(
            tooltip: 'Settings',
            onPressed: () => context.push('/settings'),
            icon: const Icon(Icons.settings_rounded),
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
          if (suggested != null)
            _ContinueCard(
              lesson: suggested,
              bundle: bundle,
              done: progress.isLessonCompleted(suggested.id),
            ),
          Gap.s,
          Row(
            children: [
              Expanded(
                child: _QuickAction(
                  icon: Icons.refresh_rounded,
                  label: 'Review',
                  badge: reviewCount > 0 ? '$reviewCount' : null,
                  onTap: reviewCount > 0 ? () => context.push('/review') : null,
                ),
              ),
              Gap.s,
              Expanded(
                child: _QuickAction(
                  icon: Icons.insights_rounded,
                  label: 'Skills',
                  onTap: () => context.push('/skills'),
                ),
              ),
            ],
          ),
          Gap.s,
          Row(
            children: [
              Expanded(
                child: _QuickAction(
                  icon: Icons.shuffle_rounded,
                  label: 'Quick Practice',
                  onTap: () => context.push('/practice/unlocked'),
                ),
              ),
              Gap.s,
              Expanded(
                child: _QuickAction(
                  icon: Icons.whatshot_rounded,
                  label: 'Challenge',
                  onTap: () => context.push('/practice/all'),
                ),
              ),
            ],
          ),
          Gap.l,
          _DomainPath(
            title: 'Reading & Writing',
            color: AppTheme.seed,
            lessons: bundle.lessonsForDomain('reading_writing'),
            bundle: bundle,
            progress: progress,
            unlock: unlock,
          ),
          Gap.l,
          _DomainPath(
            title: 'Math',
            color: AppTheme.correct,
            lessons: bundle.lessonsForDomain('math'),
            bundle: bundle,
            progress: progress,
            unlock: unlock,
          ),
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
            children: [
              StatPill(
                icon: Icons.local_fire_department_rounded,
                value: '$streak',
                color: AppTheme.streak,
                semanticLabel: '$streak day streak',
              ),
              Gap.s,
              StatPill(
                icon: Icons.bolt_rounded,
                value: '$xp XP',
                color: AppTheme.xpGold,
                semanticLabel: '$xp total XP',
              ),
              const Spacer(),
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
            mainAxisAlignment: MainAxisAlignment.spaceBetween,
            children: [
              Text('Daily goal', style: Theme.of(context).textTheme.labelLarge),
              Text(
                '$dailyXp / $goalXp XP',
                style: Theme.of(context).textTheme.labelLarge,
              ),
            ],
          ),
          Gap.xs,
          ProgressBar(value: goalProgress, color: AppTheme.streak),
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
                ),
              ),
              const SizedBox(width: 8),
              Text(
                '$xpIntoLevel/$xpForNext',
                style: Theme.of(context).textTheme.bodySmall,
              ),
            ],
          ),
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

class _QuickAction extends StatelessWidget {
  const _QuickAction({
    required this.icon,
    required this.label,
    this.badge,
    this.onTap,
  });
  final IconData icon;
  final String label;
  final String? badge;
  final VoidCallback? onTap;

  @override
  Widget build(BuildContext context) {
    final scheme = Theme.of(context).colorScheme;
    return Opacity(
      opacity: onTap == null ? 0.5 : 1,
      child: AppCard(
        onTap: onTap,
        child: Row(
          children: [
            Icon(icon, color: scheme.primary),
            Gap.s,
            Text(label, style: const TextStyle(fontWeight: FontWeight.w700)),
            if (badge != null) ...[
              const Spacer(),
              Container(
                padding: const EdgeInsets.symmetric(horizontal: 8, vertical: 2),
                decoration: BoxDecoration(
                  color: AppTheme.incorrect,
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
        : color;

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
