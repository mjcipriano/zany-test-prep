import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:go_router/go_router.dart';

import '../../app/app_controller.dart';
import '../../design/theme.dart';
import '../../design/widgets.dart';

class SettingsScreen extends ConsumerWidget {
  const SettingsScreen({super.key});

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    final data = ref.watch(appControllerProvider).valueOrNull;
    final profile = data?.profile;
    if (data == null || profile == null) {
      return const Scaffold(body: Center(child: CircularProgressIndicator()));
    }
    final controller = ref.read(appControllerProvider.notifier);

    return Scaffold(
      appBar: AppBar(title: const Text('Settings')),
      body: ListView(
        padding: kPagePadding,
        children: [
          const SectionLabel('Learning'),
          AppCard(
            child: Column(
              children: [
                ListTile(
                  contentPadding: EdgeInsets.zero,
                  leading: const Icon(Icons.flag_rounded),
                  title: const Text('Daily goal'),
                  trailing: DropdownButton<int>(
                    value: profile.dailyGoalMinutes,
                    underline: const SizedBox.shrink(),
                    items: const [
                      DropdownMenuItem(value: 5, child: Text('5 min')),
                      DropdownMenuItem(value: 10, child: Text('10 min')),
                      DropdownMenuItem(value: 15, child: Text('15 min')),
                    ],
                    onChanged: (v) {
                      if (v != null) controller.setDailyGoal(v);
                    },
                  ),
                ),
                const Divider(height: 1),
                ListTile(
                  contentPadding: EdgeInsets.zero,
                  leading: const Icon(Icons.menu_book_rounded),
                  title: const Text('Exam'),
                  subtitle: const Text('SAT (more coming soon)'),
                  trailing: Text(
                    data.bundle.exam.displayName,
                    style: const TextStyle(fontWeight: FontWeight.w700),
                  ),
                ),
                const Divider(height: 1),
                ListTile(
                  contentPadding: EdgeInsets.zero,
                  leading: const Icon(Icons.event_rounded),
                  title: const Text('Target test date'),
                  subtitle: Text(
                    profile.targetTestDate == null
                        ? 'Not set'
                        : _fmt(profile.targetTestDate!),
                  ),
                  trailing: TextButton(
                    onPressed: () async {
                      final now = DateTime.now();
                      final picked = await showDatePicker(
                        context: context,
                        initialDate:
                            profile.targetTestDate ??
                            now.add(const Duration(days: 60)),
                        firstDate: now,
                        lastDate: now.add(const Duration(days: 730)),
                      );
                      if (picked != null) controller.setTargetDate(picked);
                    },
                    child: Text(
                      profile.targetTestDate == null ? 'Set' : 'Change',
                    ),
                  ),
                ),
              ],
            ),
          ),
          Gap.m,
          const SectionLabel('Preferences'),
          AppCard(
            child: Column(
              children: [
                SwitchListTile(
                  contentPadding: EdgeInsets.zero,
                  secondary: const Icon(Icons.volume_up_rounded),
                  title: const Text('Sound'),
                  value: profile.soundOn,
                  onChanged: controller.setSound,
                ),
                const Divider(height: 1),
                SwitchListTile(
                  contentPadding: EdgeInsets.zero,
                  secondary: const Icon(Icons.vibration_rounded),
                  title: const Text('Haptics'),
                  value: profile.hapticsOn,
                  onChanged: controller.setHaptics,
                ),
                const Divider(height: 1),
                ListTile(
                  contentPadding: EdgeInsets.zero,
                  leading: const Icon(Icons.brightness_6_rounded),
                  title: const Text('Theme'),
                  trailing: DropdownButton<ThemeMode>(
                    value: profile.themeMode,
                    underline: const SizedBox.shrink(),
                    items: const [
                      DropdownMenuItem(
                        value: ThemeMode.system,
                        child: Text('System'),
                      ),
                      DropdownMenuItem(
                        value: ThemeMode.light,
                        child: Text('Light'),
                      ),
                      DropdownMenuItem(
                        value: ThemeMode.dark,
                        child: Text('Dark'),
                      ),
                    ],
                    onChanged: (v) {
                      if (v != null) controller.setThemeMode(v);
                    },
                  ),
                ),
              ],
            ),
          ),
          Gap.m,
          const SectionLabel('Data'),
          AppCard(
            child: ListTile(
              contentPadding: EdgeInsets.zero,
              leading: const Icon(Icons.import_export_rounded),
              title: const Text('Backup & restore'),
              subtitle: const Text('Move progress between devices'),
              trailing: const Icon(Icons.chevron_right_rounded),
              onTap: () => context.push('/backup'),
            ),
          ),
          Gap.m,
          const SectionLabel('About'),
          AppCard(
            child: Column(
              children: [
                ListTile(
                  contentPadding: EdgeInsets.zero,
                  leading: const Icon(Icons.info_outline_rounded),
                  title: const Text('About this app'),
                  trailing: const Icon(Icons.chevron_right_rounded),
                  onTap: () => context.push('/about'),
                ),
                const Divider(height: 1),
                ListTile(
                  contentPadding: EdgeInsets.zero,
                  leading: const Icon(Icons.dataset_rounded),
                  title: const Text('Content version'),
                  trailing: Text(data.bundle.exam.contentVersion),
                ),
              ],
            ),
          ),
          Gap.m,
          const SectionLabel('Danger zone'),
          AppCard(
            color: AppTheme.incorrect.withValues(alpha: 0.10),
            child: ListTile(
              contentPadding: EdgeInsets.zero,
              leading: const Icon(
                Icons.restart_alt_rounded,
                color: AppTheme.incorrect,
              ),
              title: const Text(
                'Reset progress',
                style: TextStyle(
                  color: AppTheme.incorrect,
                  fontWeight: FontWeight.w700,
                ),
              ),
              subtitle: const Text('Erase all local progress and start over'),
              onTap: () => _confirmReset(context, controller),
            ),
          ),
          Gap.xl,
        ],
      ),
    );
  }

  static String _fmt(DateTime d) =>
      '${d.year}-${d.month.toString().padLeft(2, '0')}-${d.day.toString().padLeft(2, '0')}';

  Future<void> _confirmReset(
    BuildContext context,
    AppController controller,
  ) async {
    final ok = await showDialog<bool>(
      context: context,
      builder: (ctx) => AlertDialog(
        title: const Text('Reset progress?'),
        content: const Text(
          'This permanently deletes your XP, streak, mastery, and lesson '
          'progress on this device. This cannot be undone.',
        ),
        actions: [
          TextButton(
            onPressed: () => Navigator.pop(ctx, false),
            child: const Text('Cancel'),
          ),
          FilledButton(
            style: FilledButton.styleFrom(backgroundColor: AppTheme.incorrect),
            onPressed: () => Navigator.pop(ctx, true),
            child: const Text('Reset'),
          ),
        ],
      ),
    );
    if (ok == true) {
      await controller.resetProgress();
      // Router redirects to onboarding once onboarded flips to false.
      if (context.mounted) context.go('/onboarding');
    }
  }
}
