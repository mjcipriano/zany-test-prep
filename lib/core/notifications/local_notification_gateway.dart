import 'dart:async';

import 'package:flutter/foundation.dart';
import 'package:flutter/services.dart';
import 'package:flutter_local_notifications/flutter_local_notifications.dart';
import 'package:flutter_timezone/flutter_timezone.dart';
import 'package:timezone/data/latest.dart' as tz_data;
import 'package:timezone/timezone.dart' as tz;

import '../../domain/services/reminder_planner.dart';
import 'notification_gateway.dart';

/// Android notification channel for study reminders. Users can tune it (sound,
/// importance) in the system settings.
const String kReminderChannelId = 'study_reminders';
const String kReminderChannelName = 'Study reminders';

/// Small monochrome status-bar icon (android/app/src/main/res/drawable,
/// kept from resource shrinking by res/raw/keep.xml).
const String kReminderIcon = 'ic_stat_notify';

/// Opens the app's notification settings page (MainActivity.kt).
const MethodChannel kNotificationSettingsChannel = MethodChannel(
  'ai.zanybot.zany_test_prep/notification_settings',
);

/// [NotificationGateway] backed by flutter_local_notifications (Android).
///
/// Uses inexact scheduling (`inexactAllowWhileIdle`), so no exact-alarm
/// permission is needed; the plugin's boot receiver (AndroidManifest.xml)
/// restores pending reminders after a reboot or app update.
class LocalNotificationGateway implements NotificationGateway {
  LocalNotificationGateway({FlutterLocalNotificationsPlugin? plugin})
    : _plugin = plugin ?? FlutterLocalNotificationsPlugin();

  final FlutterLocalNotificationsPlugin _plugin;
  final _taps = StreamController<String>.broadcast();
  Future<bool>? _init;
  tz.Location? _location;
  bool _launchTaken = false;

  AndroidFlutterLocalNotificationsPlugin? get _android => _plugin
      .resolvePlatformSpecificImplementation<
        AndroidFlutterLocalNotificationsPlugin
      >();

  /// Initializes the plugin once; false if the platform side is unavailable.
  Future<bool> _ready() => _init ??= () async {
    try {
      await _plugin.initialize(
        settings: const InitializationSettings(
          android: AndroidInitializationSettings(kReminderIcon),
        ),
        onDidReceiveNotificationResponse: (response) {
          final payload = response.payload;
          if (payload != null) _taps.add(payload);
        },
      );
      return true;
    } catch (e) {
      debugPrint('Notifications unavailable: $e');
      return false;
    }
  }();

  @override
  Future<tz.Location> localLocation() async {
    final cached = _location;
    if (cached != null) return cached;
    tz_data.initializeTimeZones();
    var location = tz.UTC;
    try {
      final info = await FlutterTimezone.getLocalTimezone();
      location = tz.getLocation(info.identifier);
    } catch (e) {
      // Unknown zone id: fall back to UTC; reminders may drift by the offset
      // but still fire daily.
      debugPrint('Could not resolve the local time zone: $e');
    }
    tz.setLocalLocation(location);
    return _location = location;
  }

  @override
  Future<bool?> notificationsAllowed() async {
    if (!await _ready()) return null;
    try {
      return await _android?.areNotificationsEnabled();
    } catch (_) {
      return null;
    }
  }

  @override
  Future<bool> requestPermission() async {
    if (!await _ready()) return false;
    try {
      // Below Android 13 there is no runtime prompt; this just reports
      // whether notifications are enabled for the app.
      return await _android?.requestNotificationsPermission() ?? false;
    } catch (_) {
      return false;
    }
  }

  @override
  Future<bool> openSystemSettings() async {
    try {
      return await kNotificationSettingsChannel.invokeMethod<bool>(
            'openNotificationSettings',
          ) ??
          false;
    } catch (_) {
      return false;
    }
  }

  @override
  Future<void> cancelAll() async {
    if (!await _ready()) return;
    try {
      await _plugin.cancelAllPendingNotifications();
    } catch (e) {
      debugPrint('Could not cancel reminders: $e');
    }
  }

  @override
  Future<void> schedule(PlannedReminder reminder) async {
    if (!await _ready()) return;
    try {
      await _plugin.zonedSchedule(
        id: reminder.id,
        scheduledDate: reminder.when,
        title: reminder.title,
        body: reminder.body,
        payload: reminder.payload,
        androidScheduleMode: AndroidScheduleMode.inexactAllowWhileIdle,
        notificationDetails: const NotificationDetails(
          android: AndroidNotificationDetails(
            kReminderChannelId,
            kReminderChannelName,
            channelDescription:
                'Daily study reminders and evening streak nudges',
            icon: kReminderIcon,
            category: AndroidNotificationCategory.reminder,
          ),
        ),
      );
    } catch (e) {
      debugPrint('Could not schedule reminder ${reminder.id}: $e');
    }
  }

  @override
  Stream<String> get taps => _taps.stream;

  @override
  Future<String?> takeLaunchPayload() async {
    if (_launchTaken || !await _ready()) return null;
    _launchTaken = true;
    try {
      final details = await _plugin.getNotificationAppLaunchDetails();
      if (details?.didNotificationLaunchApp ?? false) {
        return details!.notificationResponse?.payload;
      }
    } catch (_) {}
    return null;
  }
}
