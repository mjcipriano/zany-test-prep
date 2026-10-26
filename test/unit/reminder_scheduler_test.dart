import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:flutter_test/flutter_test.dart';
import 'package:timezone/data/latest.dart' as tz_data;
import 'package:timezone/timezone.dart' as tz;
import 'package:zany_test_prep/app/app_controller.dart';
import 'package:zany_test_prep/core/notifications/notification_gateway.dart';
import 'package:zany_test_prep/core/notifications/reminder_scheduler.dart';
import 'package:zany_test_prep/data/local/key_value_store.dart';
import 'package:zany_test_prep/data/repositories/progress_repository.dart';
import 'package:zany_test_prep/domain/models/profile.dart';
import 'package:zany_test_prep/domain/models/progress.dart';
import 'package:zany_test_prep/domain/models/reminder_settings.dart';
import 'package:zany_test_prep/domain/services/reminder_planner.dart';

import '../helpers/fake_notification_gateway.dart';
import '../helpers/pump_app.dart';

UserProfile _profile({bool enabled = true, int goalMinutes = 10}) =>
    UserProfile.initial(
      'sat',
      goalMinutes,
    ).copyWith(reminders: ReminderSettings(enabled: enabled));

void main() {
  late tz.Location ny;
  setUpAll(() {
    tz_data.initializeTimeZones();
    ny = tz.getLocation('America/New_York');
  });

  group('ReminderScheduler', () {
    late FakeNotificationGateway gateway;
    late DateTime now;
    late ReminderScheduler scheduler;

    setUp(() {
      gateway = FakeNotificationGateway(location: ny);
      now = tz.TZDateTime(ny, 2026, 6, 10, 12);
      scheduler = ReminderScheduler(gateway, clock: () => now);
    });

    test('disabled: cancels and schedules nothing', () async {
      gateway.pending[999] = PlannedReminder(
        id: 999,
        kind: ReminderKind.daily,
        when: tz.TZDateTime(ny, 2026, 6, 11),
        title: 'stale',
        body: '',
        payload: kReminderRouteHome,
      );
      final plan = await scheduler.sync(
        profile: _profile(enabled: false),
        game: GameState(),
      );
      expect(plan, isEmpty);
      expect(gateway.pending, isEmpty);
      expect(gateway.cancelAllCalls, 1);
    });

    test('no profile (reset/not onboarded): cancels everything', () async {
      await scheduler.sync(profile: _profile(), game: GameState());
      expect(gateway.pending, isNotEmpty);
      await scheduler.sync(profile: null, game: GameState());
      expect(gateway.pending, isEmpty);
    });

    test('enabled: schedules the plan in the device time zone', () async {
      final plan = await scheduler.sync(profile: _profile(), game: GameState());
      expect(plan, hasLength(kReminderHorizonDays));
      expect(gateway.pending.length, plan.length);
      final first = gateway.pendingSorted.first;
      expect(first.when.location, ny);
      expect(first.when, tz.TZDateTime(ny, 2026, 6, 10, 17));
    });

    test("finishing today's goal cancels today's streak nudge", () async {
      final game = GameState(
        currentStreak: 5,
        longestStreak: 5,
        lastActiveDay: '2026-06-09',
      );
      await scheduler.sync(profile: _profile(), game: game);
      bool nudgeToday() => gateway.pending.values.any(
        (r) =>
            r.kind == ReminderKind.streakNudge &&
            dayKey(r.when) == '2026-06-10',
      );
      expect(nudgeToday(), isTrue);

      // A session at 6 PM meets the 200 XP goal and extends the streak.
      now = tz.TZDateTime(ny, 2026, 6, 10, 18);
      game
        ..currentStreak = 6
        ..lastActiveDay = '2026-06-10'
        ..dailyDay = '2026-06-10'
        ..dailyXp = 210;
      await scheduler.sync(profile: _profile(), game: game);
      expect(nudgeToday(), isFalse);
      // Tomorrow's nudge now protects the 6-day streak.
      final tomorrow = gateway.pending.values.singleWhere(
        (r) => r.kind == ReminderKind.streakNudge,
      );
      expect(dayKey(tomorrow.when), '2026-06-11');
      expect(tomorrow.title + tomorrow.body, contains('6'));
    });

    test('overlapping syncs run in order; the last one wins', () async {
      final a = scheduler.sync(profile: _profile(), game: GameState());
      final b = scheduler.sync(
        profile: _profile(enabled: false),
        game: GameState(),
      );
      await Future.wait([a, b]);
      expect(gateway.pending, isEmpty);
      expect(gateway.cancelAllCalls, 2);
    });

    test('a failing gateway never throws into the caller', () async {
      final s = ReminderScheduler(_ThrowingGateway(), clock: () => now);
      expect(await s.sync(profile: _profile(), game: GameState()), isEmpty);
    });
  });

  group('AppController keeps reminders in sync', () {
    test('app start schedules for a stored opted-in profile', () async {
      final store = MemoryStore();
      final repo = ProgressRepository(store);
      await repo.saveProfile(_profile());
      await repo.setOnboarded(true);
      final gateway = FakeNotificationGateway();
      final container = ProviderContainer(
        overrides: testOverrides(store, notifications: gateway),
      );
      addTearDown(container.dispose);
      await container.read(appControllerProvider.future);
      await pumpEventQueue();
      expect(gateway.pending, isNotEmpty);
      expect(
        gateway.pending.values.every((r) => r.kind == ReminderKind.daily),
        isTrue,
      );
    });

    test('turning reminders off in settings cancels them', () async {
      final store = MemoryStore();
      final repo = ProgressRepository(store);
      await repo.saveProfile(_profile());
      await repo.setOnboarded(true);
      final gateway = FakeNotificationGateway();
      final container = ProviderContainer(
        overrides: testOverrides(store, notifications: gateway),
      );
      addTearDown(container.dispose);
      await container.read(appControllerProvider.future);
      await pumpEventQueue();
      expect(gateway.pending, isNotEmpty);

      await container
          .read(appControllerProvider.notifier)
          .setReminders(const ReminderSettings());
      await pumpEventQueue();
      expect(gateway.pending, isEmpty);
      expect(
        ProgressRepository(store).loadProfile()!.reminders.enabled,
        isFalse,
      );
    });

    test('reset progress cancels pending reminders', () async {
      final store = MemoryStore();
      final repo = ProgressRepository(store);
      await repo.saveProfile(_profile());
      await repo.setOnboarded(true);
      final gateway = FakeNotificationGateway();
      final container = ProviderContainer(
        overrides: testOverrides(store, notifications: gateway),
      );
      addTearDown(container.dispose);
      await container.read(appControllerProvider.future);
      await pumpEventQueue();
      await container.read(appControllerProvider.notifier).resetProgress();
      await pumpEventQueue();
      expect(gateway.pending, isEmpty);
    });
  });
}

class _ThrowingGateway extends NoopNotificationGateway {
  @override
  Future<tz.Location> localLocation() async => throw StateError('boom');
}
