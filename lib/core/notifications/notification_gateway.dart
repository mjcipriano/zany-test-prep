import 'dart:async';

import 'package:timezone/timezone.dart' as tz;

import '../../domain/services/reminder_planner.dart';

/// Thin seam over the platform notification plugin so the reminder logic is
/// testable with a fake (see test/helpers/fake_notification_gateway.dart).
///
/// Every method is best-effort: implementations swallow platform errors, and
/// none of them may throw into the UI.
abstract class NotificationGateway {
  /// The device's time zone, used to turn wall-clock reminder times into
  /// absolute instants.
  Future<tz.Location> localLocation();

  /// Whether the OS currently lets the app post notifications. Null when it
  /// can't be determined (unsupported platform).
  Future<bool?> notificationsAllowed();

  /// Asks for permission to post notifications (Android 13+ runtime prompt,
  /// iOS alert). Returns whether notifications are allowed afterwards. Only
  /// called when the user turns reminders on.
  Future<bool> requestPermission();

  /// Opens the system's notification settings for this app so a user who
  /// denied the permission can turn it back on. Returns false if it couldn't.
  Future<bool> openSystemSettings();

  /// Cancels every pending (scheduled, not yet shown) reminder.
  Future<void> cancelAll();

  /// Schedules one reminder (inexact; may fire a few minutes late).
  Future<void> schedule(PlannedReminder reminder);

  /// Payloads of notifications tapped while the app is running.
  Stream<String> get taps;

  /// The payload of the notification that launched the app, if any. Returns
  /// it once; later calls return null.
  Future<String?> takeLaunchPayload();
}

/// Gateway for platforms without local notifications (desktop, web): does
/// nothing and reports notifications as unavailable.
class NoopNotificationGateway implements NotificationGateway {
  @override
  Future<tz.Location> localLocation() async => tz.UTC;

  @override
  Future<bool?> notificationsAllowed() async => null;

  @override
  Future<bool> requestPermission() async => false;

  @override
  Future<bool> openSystemSettings() async => false;

  @override
  Future<void> cancelAll() async {}

  @override
  Future<void> schedule(PlannedReminder reminder) async {}

  @override
  Stream<String> get taps => const Stream.empty();

  @override
  Future<String?> takeLaunchPayload() async => null;
}
