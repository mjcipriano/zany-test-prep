import 'safe_json.dart';

/// Default daily reminder time: 5:00 PM (after school), in minutes after
/// midnight.
const int kDefaultReminderMinutes = 17 * 60;

/// Opt-in local reminder preferences, stored inside the profile.
///
/// Reminders are **off by default**; the user turns them on at the end of
/// onboarding or in Settings (which is also when the OS notification
/// permission is requested).
class ReminderSettings {
  const ReminderSettings({
    this.enabled = false,
    this.minutesOfDay = kDefaultReminderMinutes,
    this.streakNudge = true,
  });

  /// Master switch: the daily study reminder (and the streak nudge with it).
  final bool enabled;

  /// Local wall-clock time of the daily reminder, minutes after midnight
  /// (0..1439).
  final int minutesOfDay;

  /// Also send an evening "streak at risk" nudge when today's goal isn't met.
  final bool streakNudge;

  int get hour => minutesOfDay ~/ 60;
  int get minute => minutesOfDay % 60;

  ReminderSettings copyWith({
    bool? enabled,
    int? minutesOfDay,
    bool? streakNudge,
  }) => ReminderSettings(
    enabled: enabled ?? this.enabled,
    minutesOfDay: minutesOfDay ?? this.minutesOfDay,
    streakNudge: streakNudge ?? this.streakNudge,
  );

  Map<String, dynamic> toJson() => {
    'enabled': enabled,
    'minutesOfDay': minutesOfDay,
    'streakNudge': streakNudge,
  };

  /// Defensive parse: a missing/garbled blob (e.g. a profile saved before
  /// reminders existed) yields the defaults, i.e. reminders off.
  factory ReminderSettings.fromJson(Map<String, dynamic> json) {
    final minutes = asInt(json['minutesOfDay'], kDefaultReminderMinutes);
    return ReminderSettings(
      enabled: asBool(json['enabled']),
      minutesOfDay: minutes < 0 || minutes >= 24 * 60
          ? kDefaultReminderMinutes
          : minutes,
      streakNudge: asBool(json['streakNudge'], true),
    );
  }

  @override
  bool operator ==(Object other) =>
      other is ReminderSettings &&
      other.enabled == enabled &&
      other.minutesOfDay == minutesOfDay &&
      other.streakNudge == streakNudge;

  @override
  int get hashCode => Object.hash(enabled, minutesOfDay, streakNudge);

  @override
  String toString() =>
      'ReminderSettings(enabled: $enabled, at: $hour:$minute, '
      'streakNudge: $streakNudge)';
}
