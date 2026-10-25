import 'dart:async';

import 'package:timezone/timezone.dart' as tz;
import 'package:zany_test_prep/core/notifications/notification_gateway.dart';
import 'package:zany_test_prep/domain/services/reminder_planner.dart';

/// In-memory [NotificationGateway]: records what would be scheduled and lets
/// tests script the permission answers and notification taps.
class FakeNotificationGateway implements NotificationGateway {
  FakeNotificationGateway({
    tz.Location? location,
    this.allowed = true,
    this.grantOnRequest = true,
    this.canOpenSettings = true,
    this.launchPayload,
  }) : location = location ?? tz.UTC;

  tz.Location location;

  /// What [notificationsAllowed] reports.
  bool? allowed;

  /// Whether the permission prompt is accepted.
  bool grantOnRequest;
  bool canOpenSettings;
  String? launchPayload;

  int permissionRequests = 0;
  int settingsOpened = 0;
  int cancelAllCalls = 0;

  /// Currently pending reminders by id.
  final Map<int, PlannedReminder> pending = {};
  final _taps = StreamController<String>.broadcast();

  List<PlannedReminder> get pendingSorted =>
      pending.values.toList()..sort((a, b) => a.when.compareTo(b.when));

  /// Simulates the user tapping a notification while the app runs.
  void tap(String payload) => _taps.add(payload);

  @override
  Future<tz.Location> localLocation() async => location;

  @override
  Future<bool?> notificationsAllowed() async => allowed;

  @override
  Future<bool> requestPermission() async {
    permissionRequests++;
    allowed = grantOnRequest;
    return grantOnRequest;
  }

  @override
  Future<bool> openSystemSettings() async {
    settingsOpened++;
    return canOpenSettings;
  }

  @override
  Future<void> cancelAll() async {
    cancelAllCalls++;
    pending.clear();
  }

  @override
  Future<void> schedule(PlannedReminder reminder) async {
    pending[reminder.id] = reminder;
  }

  @override
  Stream<String> get taps => _taps.stream;

  @override
  Future<String?> takeLaunchPayload() async {
    final p = launchPayload;
    launchPayload = null;
    return p;
  }
}
