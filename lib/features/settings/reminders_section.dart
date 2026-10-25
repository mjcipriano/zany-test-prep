import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';

import '../../app/app_controller.dart';
import '../../core/notifications/reminder_scheduler.dart';
import '../../design/theme.dart';
import '../../domain/models/reminder_settings.dart';
import '../../domain/services/reminder_planner.dart';

/// Formats minutes-after-midnight in the device's 12/24-hour style.
String formatReminderTime(BuildContext context, int minutesOfDay) =>
    MaterialLocalizations.of(context).formatTimeOfDay(
      TimeOfDay(hour: minutesOfDay ~/ 60, minute: minutesOfDay % 60),
      alwaysUse24HourFormat: MediaQuery.alwaysUse24HourFormatOf(context),
    );

/// Shows the time picker for the daily reminder; returns minutes after
/// midnight, or null if cancelled.
Future<int?> pickReminderTime(BuildContext context, int minutesOfDay) async {
  final picked = await showTimePicker(
    context: context,
    initialTime: TimeOfDay(hour: minutesOfDay ~/ 60, minute: minutesOfDay % 60),
    helpText: 'Remind me at',
  );
  return picked == null ? null : picked.hour * 60 + picked.minute;
}

/// Settings → Reminders: daily reminder switch + time, the evening streak
/// saver, and a how-to-enable note when the OS blocks notifications.
///
/// The notification permission is requested only when the user switches
/// reminders on; if it's denied, reminders stay off and the note explains how
/// to allow them.
class RemindersSection extends ConsumerStatefulWidget {
  const RemindersSection({super.key});

  @override
  ConsumerState<RemindersSection> createState() => _RemindersSectionState();
}

class _RemindersSectionState extends ConsumerState<RemindersSection>
    with WidgetsBindingObserver {
  /// The OS blocks our notifications (denied prompt, or turned off later).
  bool _blocked = false;
  bool _busy = false;

  @override
  void initState() {
    super.initState();
    WidgetsBinding.instance.addObserver(this);
    _refreshBlocked();
  }

  @override
  void dispose() {
    WidgetsBinding.instance.removeObserver(this);
    super.dispose();
  }

  // Coming back from the system settings: pick up a newly granted permission.
  @override
  void didChangeAppLifecycleState(AppLifecycleState state) {
    if (state == AppLifecycleState.resumed) _refreshBlocked();
  }

  ReminderSettings? get _settings =>
      ref.read(appControllerProvider).valueOrNull?.profile?.reminders;

  Future<void> _refreshBlocked() async {
    final allowed = await ref
        .read(notificationGatewayProvider)
        .notificationsAllowed();
    if (!mounted) return;
    final enabled = _settings?.enabled ?? false;
    setState(() {
      if (allowed == true) {
        _blocked = false;
      } else if (allowed == false && enabled) {
        // Reminders are on but the OS silently drops them: say so.
        _blocked = true;
      }
    });
  }

  Future<void> _toggle(bool on) async {
    final settings = _settings;
    if (settings == null || _busy) return;
    final controller = ref.read(appControllerProvider.notifier);
    if (!on) {
      await controller.setReminders(settings.copyWith(enabled: false));
      if (mounted) setState(() => _blocked = false);
      return;
    }
    setState(() => _busy = true);
    final granted = await ref
        .read(notificationGatewayProvider)
        .requestPermission();
    if (!mounted) return;
    setState(() {
      _busy = false;
      _blocked = !granted;
    });
    if (granted) {
      await controller.setReminders(settings.copyWith(enabled: true));
    }
  }

  Future<void> _pickTime(ReminderSettings settings) async {
    final picked = await pickReminderTime(context, settings.minutesOfDay);
    if (picked == null || !mounted) return;
    await ref
        .read(appControllerProvider.notifier)
        .setReminders(settings.copyWith(minutesOfDay: picked));
  }

  @override
  Widget build(BuildContext context) {
    final settings =
        ref.watch(appControllerProvider).valueOrNull?.profile?.reminders ??
        const ReminderSettings();
    final controller = ref.read(appControllerProvider.notifier);
    final time = formatReminderTime(context, settings.minutesOfDay);
    final nudgeAt = streakNudgeMinutesFor(settings);

    return Column(
      children: [
        SwitchListTile(
          contentPadding: EdgeInsets.zero,
          secondary: const Icon(Icons.notifications_active_rounded),
          title: const Text('Daily reminder'),
          subtitle: Text(
            settings.enabled
                ? 'Every day at $time'
                : 'A friendly nudge to study, once a day',
          ),
          value: settings.enabled,
          onChanged: _busy ? null : _toggle,
        ),
        if (settings.enabled) ...[
          const Divider(height: 1),
          ListTile(
            contentPadding: EdgeInsets.zero,
            leading: const Icon(Icons.schedule_rounded),
            title: const Text('Reminder time'),
            trailing: TextButton(
              key: const ValueKey('reminder-time'),
              onPressed: () => _pickTime(settings),
              child: Text(time),
            ),
          ),
          const Divider(height: 1),
          SwitchListTile(
            contentPadding: EdgeInsets.zero,
            secondary: const Icon(
              Icons.local_fire_department_rounded,
              color: AppTheme.streak,
            ),
            title: const Text('Streak saver'),
            subtitle: Text(
              nudgeAt == null && settings.streakNudge
                  ? 'Your reminder is late enough to cover it'
                  : 'Heads-up at ${formatReminderTime(context, nudgeAt ?? kStreakNudgeMinutes)} '
                        'if your streak is at risk',
            ),
            value: settings.streakNudge,
            onChanged: (v) =>
                controller.setReminders(settings.copyWith(streakNudge: v)),
          ),
        ],
        if (_blocked) ...[
          const SizedBox(height: 8),
          const NotificationsBlockedNote(),
        ],
      ],
    );
  }
}

/// Explains how to turn notifications back on after the permission was
/// denied, with a shortcut to the app's notification settings.
class NotificationsBlockedNote extends ConsumerWidget {
  const NotificationsBlockedNote({super.key});

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    final scheme = Theme.of(context).colorScheme;
    return Container(
      width: double.infinity,
      padding: const EdgeInsets.all(12),
      decoration: BoxDecoration(
        color: AppTheme.streak.withValues(alpha: 0.12),
        borderRadius: BorderRadius.circular(14),
      ),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Row(
            children: [
              const Icon(
                Icons.notifications_off_rounded,
                color: AppTheme.streak,
              ),
              const SizedBox(width: 8),
              Expanded(
                child: Text(
                  'Notifications are off for this app',
                  style: Theme.of(
                    context,
                  ).textTheme.titleSmall?.copyWith(fontWeight: FontWeight.w800),
                ),
              ),
            ],
          ),
          const SizedBox(height: 6),
          Text(
            'To get reminders, open your phone\'s Settings, find this app '
            'under Apps, and allow its notifications. Then switch reminders '
            'on here.',
            style: TextStyle(color: scheme.onSurfaceVariant),
          ),
          Align(
            alignment: Alignment.centerRight,
            child: TextButton.icon(
              onPressed: () async {
                final opened = await ref
                    .read(notificationGatewayProvider)
                    .openSystemSettings();
                if (!opened && context.mounted) {
                  ScaffoldMessenger.of(context).showSnackBar(
                    const SnackBar(
                      content: Text(
                        'Open your phone\'s Settings app to allow '
                        'notifications.',
                      ),
                    ),
                  );
                }
              },
              icon: const Icon(Icons.open_in_new_rounded),
              label: const Text('Open settings'),
            ),
          ),
        ],
      ),
    );
  }
}
