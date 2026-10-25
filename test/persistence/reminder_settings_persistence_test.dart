import 'dart:convert';

import 'package:flutter_test/flutter_test.dart';
import 'package:zany_test_prep/data/local/key_value_store.dart';
import 'package:zany_test_prep/data/repositories/progress_repository.dart';
import 'package:zany_test_prep/domain/models/backup.dart';
import 'package:zany_test_prep/domain/models/profile.dart';
import 'package:zany_test_prep/domain/models/reminder_settings.dart';

void main() {
  test('reminder settings round-trip through the stored profile', () async {
    final store = MemoryStore();
    const reminders = ReminderSettings(
      enabled: true,
      minutesOfDay: 19 * 60 + 45,
      streakNudge: false,
    );
    await ProgressRepository(store).saveProfile(
      UserProfile.initial('act', 15).copyWith(reminders: reminders),
    );

    // A fresh repository simulates the next app launch.
    final loaded = ProgressRepository(store).loadProfile()!;
    expect(loaded.reminders, reminders);
    expect(loaded.examId, 'act');
    expect(loaded.dailyGoalMinutes, 15);
  });

  test('copyWith without reminders keeps them', () {
    final p = UserProfile.initial(
      'sat',
      10,
    ).copyWith(reminders: const ReminderSettings(enabled: true));
    expect(p.copyWith(soundOn: false).reminders.enabled, isTrue);
  });

  test('a profile saved before reminders existed loads with them off', () {
    final store = MemoryStore();
    // The exact shape older builds wrote (no "reminders" key).
    store.setString(
      'profile.v1',
      jsonEncode({
        'schema': 1,
        'examId': 'sat',
        'dailyGoalMinutes': 10,
        'targetTestDate': null,
        'soundOn': false,
        'hapticsOn': true,
        'themeMode': 'dark',
        'createdAt': '2026-01-02T03:04:05.000',
      }),
    );
    final loaded = ProgressRepository(store).loadProfile()!;
    expect(loaded.reminders, const ReminderSettings());
    expect(loaded.reminders.enabled, isFalse);
    // Everything else is untouched.
    expect(loaded.soundOn, isFalse);
    expect(loaded.dailyGoalMinutes, 10);
  });

  test('garbled reminder blobs fall back to safe defaults', () {
    ReminderSettings parse(Object? blob) =>
        UserProfile.fromJson({'examId': 'sat', 'reminders': blob}).reminders;

    expect(parse('nonsense'), const ReminderSettings());
    expect(parse(42), const ReminderSettings());
    expect(parse(<String, dynamic>{}), const ReminderSettings());
    // Wrong types are coerced, out-of-range times reset to the default.
    expect(
      parse({'enabled': 'true', 'minutesOfDay': '480', 'streakNudge': 'false'}),
      const ReminderSettings(
        enabled: true,
        minutesOfDay: 480,
        streakNudge: false,
      ),
    );
    expect(
      parse({'enabled': true, 'minutesOfDay': 99999}).minutesOfDay,
      kDefaultReminderMinutes,
    );
    expect(
      parse({'enabled': true, 'minutesOfDay': -5}).minutesOfDay,
      kDefaultReminderMinutes,
    );
  });

  test('reminders travel with a backup export/import', () async {
    final source = MemoryStore();
    final repo = ProgressRepository(source);
    await repo.saveProfile(
      UserProfile.initial('sat', 10).copyWith(
        reminders: const ReminderSettings(enabled: true, minutesOfDay: 450),
      ),
    );
    await repo.setOnboarded(true);
    final parsed = decodeBackup(repo.exportBackup());
    expect(parsed.ok, isTrue);

    final target = MemoryStore();
    await ProgressRepository(target).writeBackup(parsed.data!);
    final restored = ProgressRepository(target).loadProfile()!;
    expect(restored.reminders.enabled, isTrue);
    expect(restored.reminders.minutesOfDay, 450);
  });
}
