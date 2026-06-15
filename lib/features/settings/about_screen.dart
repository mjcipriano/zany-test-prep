import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';

import '../../app/app_controller.dart';
import '../../design/theme.dart';
import '../../design/widgets.dart';

const String kAppVersion = '1.0.0';

class AboutScreen extends ConsumerWidget {
  const AboutScreen({super.key});

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    final data = ref.watch(appControllerProvider).valueOrNull;
    final scheme = Theme.of(context).colorScheme;
    return Scaffold(
      appBar: AppBar(title: const Text('About')),
      body: ListView(
        padding: kPagePadding,
        children: [
          Center(
            child: Column(
              children: [
                Icon(Icons.school_rounded, size: 64, color: scheme.primary),
                Gap.s,
                Text(
                  'Zany Test Prep',
                  style: Theme.of(context).textTheme.headlineSmall?.copyWith(
                    fontWeight: FontWeight.w800,
                  ),
                ),
                const Text('Version $kAppVersion'),
                if (data != null)
                  Text(
                    'Content ${data.bundle.exam.contentVersion}',
                    style: Theme.of(context).textTheme.bodySmall,
                  ),
              ],
            ),
          ),
          Gap.l,
          AppCard(
            color: AppTheme.correct.withValues(alpha: 0.12),
            child: const Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                Row(
                  children: [
                    Icon(Icons.lock_outline_rounded, color: AppTheme.correct),
                    SizedBox(width: 8),
                    Text(
                      'Your privacy',
                      style: TextStyle(fontWeight: FontWeight.w800),
                    ),
                  ],
                ),
                Gap.s,
                Text(
                  'This app works entirely offline. All of your progress — XP, '
                  'streaks, mastery, and answers — is stored locally on this '
                  'device only. There is no account, no login, no backend, and '
                  'no data is ever sent over the internet.',
                  style: TextStyle(height: 1.5),
                ),
              ],
            ),
          ),
          Gap.m,
          const AppCard(
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                Text(
                  'About the content',
                  style: TextStyle(fontWeight: FontWeight.w800),
                ),
                Gap.s,
                Text(
                  'All practice questions are original, SAT-style content created '
                  'for this app. They contain no copyrighted College Board '
                  'material. "SAT" is a trademark of the College Board, which is '
                  'not affiliated with and does not endorse this app.',
                  style: TextStyle(height: 1.5),
                ),
              ],
            ),
          ),
        ],
      ),
    );
  }
}
