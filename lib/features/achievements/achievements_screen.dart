import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';

import '../../app/app_controller.dart';
import '../../design/theme.dart';
import '../../design/widgets.dart';
import '../../domain/services/badges.dart';

/// Shows all achievements with earned/locked state.
class AchievementsScreen extends ConsumerWidget {
  const AchievementsScreen({super.key});

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    final data = ref.watch(appControllerProvider).valueOrNull;
    if (data == null) {
      return const Scaffold(body: Center(child: CircularProgressIndicator()));
    }
    final earned = data.progress.game.earnedBadges;

    return Scaffold(
      appBar: AppBar(title: const Text('Achievements')),
      body: ListView(
        padding: kPagePadding,
        children: [
          AppCard(
            color: AppTheme.xpGold.withValues(alpha: 0.14),
            child: Row(
              children: [
                const Text('🏆', style: TextStyle(fontSize: 32)),
                Gap.m,
                Expanded(
                  child: Text(
                    '${earned.length} of ${Badges.all.length} unlocked',
                    style: const TextStyle(
                      fontSize: 18,
                      fontWeight: FontWeight.w800,
                    ),
                  ),
                ),
              ],
            ),
          ),
          Gap.m,
          ...Badges.all.map((b) {
            final got = earned.contains(b.id);
            return Padding(
              padding: const EdgeInsets.only(bottom: 8),
              child: Opacity(
                opacity: got ? 1 : 0.55,
                child: AppCard(
                  child: Row(
                    children: [
                      Text(
                        got ? b.emoji : '🔒',
                        style: const TextStyle(fontSize: 30),
                      ),
                      Gap.m,
                      Expanded(
                        child: Column(
                          crossAxisAlignment: CrossAxisAlignment.start,
                          children: [
                            Text(
                              b.title,
                              style: const TextStyle(
                                fontWeight: FontWeight.w800,
                                fontSize: 16,
                              ),
                            ),
                            Text(b.description),
                          ],
                        ),
                      ),
                      if (got)
                        const Icon(
                          Icons.check_circle_rounded,
                          color: AppTheme.correct,
                        ),
                    ],
                  ),
                ),
              ),
            );
          }),
        ],
      ),
    );
  }
}
