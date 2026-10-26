import 'package:flutter/foundation.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:timezone/timezone.dart' as tz;

import '../../domain/models/profile.dart';
import '../../domain/models/progress.dart';
import '../../domain/services/reminder_planner.dart';
import 'local_notification_gateway.dart';
import 'notification_gateway.dart';

/// Keeps the OS's pending reminders in line with the profile + game state.
///
/// [sync] is idempotent: it cancels every pending reminder and schedules the
/// fresh [ReminderPlanner] plan. Calls are serialized so two quick syncs
/// (e.g. a finished lesson right after app start) can't interleave their
/// cancel/schedule steps.
class ReminderScheduler {
  ReminderScheduler(
    this.gateway, {
    this.planner = const ReminderPlanner(),
    DateTime Function()? clock,
  }) : _clock = clock ?? DateTime.now;

  final NotificationGateway gateway;
  final ReminderPlanner planner;
  final DateTime Function() _clock;
  Future<void> _queue = Future.value();

  /// Re-plans reminders for [profile] (null = no profile: cancel everything).
  /// Returns the plan that was scheduled. Never throws.
  Future<List<PlannedReminder>> sync({
    required UserProfile? profile,
    required GameState game,
  }) {
    final run = _queue.then((_) => _sync(profile, game));
    _queue = run.then((_) {}, onError: (_) {});
    return run;
  }

  Future<List<PlannedReminder>> _sync(
    UserProfile? profile,
    GameState game,
  ) async {
    try {
      var plan = const <PlannedReminder>[];
      if (profile != null && profile.reminders.enabled) {
        final location = await gateway.localLocation();
        plan = planner.plan(
          now: tz.TZDateTime.from(_clock(), location),
          settings: profile.reminders,
          game: game,
          dailyGoalXp: profile.dailyGoalXp,
          dailyGoalMinutes: profile.dailyGoalMinutes,
        );
      }
      await gateway.cancelAll();
      for (final r in plan) {
        await gateway.schedule(r);
      }
      return plan;
    } catch (e) {
      debugPrint('Reminder sync failed: $e');
      return const [];
    }
  }
}

/// The platform notification seam. Overridden with a fake in tests.
final notificationGatewayProvider = Provider<NotificationGateway>((ref) {
  if (!kIsWeb && defaultTargetPlatform == TargetPlatform.android) {
    return LocalNotificationGateway();
  }
  return NoopNotificationGateway();
});

final reminderSchedulerProvider = Provider<ReminderScheduler>(
  (ref) => ReminderScheduler(ref.watch(notificationGatewayProvider)),
);

/// Routes from notifications tapped while the app is running.
final notificationTapsProvider = StreamProvider<String>(
  (ref) => ref.watch(notificationGatewayProvider).taps,
);
