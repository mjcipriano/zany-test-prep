import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';

import '../../app/app_controller.dart';
import '../../design/theme.dart';
import '../../design/widgets.dart';

/// App version shown on the About screen. Keep in sync with `version:` in
/// pubspec.yaml when cutting a release (see docs/release.md).
const String kAppVersion = '1.7.2';

/// XP granted by the hidden cheat (tap the content version 10× quickly).
const int _cheatXp = 10000;
const int _cheatTaps = 10;

class AboutScreen extends ConsumerStatefulWidget {
  const AboutScreen({super.key});

  @override
  ConsumerState<AboutScreen> createState() => _AboutScreenState();
}

class _AboutScreenState extends ConsumerState<AboutScreen> {
  int _taps = 0;
  DateTime? _lastTap;

  Future<void> _onVersionTap() async {
    final now = DateTime.now();
    // Reset the counter if taps slow down (must be a quick succession).
    if (_lastTap == null ||
        now.difference(_lastTap!) > const Duration(milliseconds: 800)) {
      _taps = 0;
    }
    _lastTap = now;
    _taps++;
    if (_taps >= _cheatTaps) {
      _taps = 0;
      await ref.read(appControllerProvider.notifier).grantCheatXp(_cheatXp);
      if (!mounted) return;
      ScaffoldMessenger.of(context).showSnackBar(
        const SnackBar(content: Text('🎉 Cheat unlocked: +$_cheatXp XP!')),
      );
    }
  }

  @override
  Widget build(BuildContext context) {
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
                  // Hidden cheat: 10 quick taps on the content version grants XP.
                  GestureDetector(
                    behavior: HitTestBehavior.opaque,
                    onTap: _onVersionTap,
                    child: Padding(
                      padding: const EdgeInsets.symmetric(vertical: 4),
                      child: Text(
                        'Content ${data.bundle.exam.contentVersion}',
                        style: Theme.of(context).textTheme.bodySmall,
                      ),
                    ),
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
