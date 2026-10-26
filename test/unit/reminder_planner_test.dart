import 'package:flutter_test/flutter_test.dart';
import 'package:timezone/data/latest.dart' as tz_data;
import 'package:timezone/timezone.dart' as tz;
import 'package:zany_test_prep/domain/models/progress.dart';
import 'package:zany_test_prep/domain/models/reminder_settings.dart';
import 'package:zany_test_prep/domain/services/reminder_planner.dart';

const _planner = ReminderPlanner();
const _on = ReminderSettings(enabled: true); // 5:00 PM + streak nudge

late tz.Location ny;

tz.TZDateTime _ny(int y, int m, int d, [int h = 0, int min = 0, int s = 0]) =>
    tz.TZDateTime(ny, y, m, d, h, min, s);

List<PlannedReminder> _plan(
  tz.TZDateTime now, {
  ReminderSettings settings = _on,
  GameState? game,
  int goalXp = 200,
}) => _planner.plan(
  now: now,
  settings: settings,
  game: game ?? GameState(),
  dailyGoalXp: goalXp,
  dailyGoalMinutes: goalXp ~/ 20,
);

List<PlannedReminder> _daily(List<PlannedReminder> p) =>
    p.where((r) => r.kind == ReminderKind.daily).toList();
List<PlannedReminder> _nudges(List<PlannedReminder> p) =>
    p.where((r) => r.kind == ReminderKind.streakNudge).toList();

/// A player on a [streak]-day streak whose last activity was [lastActive].
GameState _streak(
  int streak,
  String lastActive, {
  int freezes = 0,
  int dailyXp = 0,
  String? dailyDay,
}) => GameState(
  currentStreak: streak,
  longestStreak: streak,
  lastActiveDay: lastActive,
  streakFreezes: freezes,
  dailyXp: dailyXp,
  dailyDay: dailyDay,
);

void main() {
  setUpAll(() {
    tz_data.initializeTimeZones();
    ny = tz.getLocation('America/New_York');
  });

  group('disabled', () {
    test('reminders off schedules nothing, even with a streak at risk', () {
      final plan = _plan(
        _ny(2026, 6, 10, 9),
        settings: const ReminderSettings(),
        game: _streak(9, '2026-06-09'),
      );
      expect(plan, isEmpty);
    });

    test('default settings are off at 5 PM with the streak saver on', () {
      const s = ReminderSettings();
      expect(s.enabled, isFalse);
      expect((s.hour, s.minute), (17, 0));
      expect(s.streakNudge, isTrue);
    });
  });

  group('daily reminder', () {
    test('one per day for the horizon, starting today when still ahead', () {
      final plan = _daily(_plan(_ny(2026, 6, 10, 9)));
      expect(plan, hasLength(kReminderHorizonDays));
      expect(plan.first.when, _ny(2026, 6, 10, 17));
      expect(plan[1].when, _ny(2026, 6, 11, 17));
      expect(plan.last.when, _ny(2026, 6, 23, 17));
      expect(plan.map((r) => r.id).toSet(), hasLength(plan.length));
      expect(plan.every((r) => r.payload == kReminderRouteHome), isTrue);
    });

    test('a reminder time already past today starts tomorrow', () {
      final plan = _daily(_plan(_ny(2026, 6, 10, 17, 0, 1)));
      expect(plan.first.when, _ny(2026, 6, 11, 17));
      expect(plan, hasLength(kReminderHorizonDays - 1));
    });

    test('exactly at the reminder time does not re-fire it', () {
      final plan = _daily(_plan(_ny(2026, 6, 10, 17)));
      expect(plan.first.when, _ny(2026, 6, 11, 17));
    });

    test('crosses midnight and the year boundary', () {
      final plan = _daily(_plan(_ny(2026, 12, 31, 23, 59, 30)));
      expect(plan.first.when, _ny(2027, 1, 1, 17));
      expect(plan[1].when, _ny(2027, 1, 2, 17));
    });

    test('a midnight reminder set late in the evening fires in minutes', () {
      final plan = _daily(
        _plan(
          _ny(2026, 2, 28, 23, 30),
          settings: _on.copyWith(minutesOfDay: 0),
        ),
      );
      expect(plan.first.when, _ny(2026, 3, 1));
      expect(
        plan.first.when.difference(_ny(2026, 2, 28, 23, 30)),
        const Duration(minutes: 30),
      );
    });

    test('keeps the wall-clock time across spring-forward DST', () {
      final plan = _daily(_plan(_ny(2026, 3, 7, 9)));
      expect(plan[0].when, _ny(2026, 3, 7, 17));
      expect(plan[1].when.hour, 17);
      expect(plan[1].when.day, 8);
      // The night the clocks jump is only 23 hours long.
      expect(plan[1].when.difference(plan[0].when), const Duration(hours: 23));
      expect(plan[2].when.difference(plan[1].when), const Duration(hours: 24));
    });

    test('keeps the wall-clock time across fall-back DST', () {
      final plan = _daily(_plan(_ny(2026, 10, 31, 9)));
      expect(plan[0].when.hour, 17);
      expect(plan[1].when.hour, 17);
      expect(plan[1].when.day, 1);
      expect(plan[1].when.difference(plan[0].when), const Duration(hours: 25));
    });

    test('a time skipped by spring-forward fires once, an hour later', () {
      final plan = _daily(
        _plan(
          _ny(2026, 3, 7, 9),
          settings: _on.copyWith(minutesOfDay: 2 * 60 + 30),
        ),
      );
      final onDstDay = plan.where((r) => r.when.day == 8 && r.when.month == 3);
      expect(onDstDay, hasLength(1));
      expect((onDstDay.single.when.hour, onDstDay.single.when.minute), (3, 30));
      // Every calendar day still gets exactly one reminder.
      expect(plan.map((r) => dayKey(r.when)).toSet(), hasLength(plan.length));
    });

    test('a time repeated by fall-back fires once', () {
      final plan = _daily(
        _plan(_ny(2026, 10, 31, 9), settings: _on.copyWith(minutesOfDay: 90)),
      );
      final onDstDay = plan.where((r) => r.when.day == 1 && r.when.month == 11);
      expect(onDstDay, hasLength(1));
      expect((onDstDay.single.when.hour, onDstDay.single.when.minute), (1, 30));
    });

    test('works in UTC and in zones east of UTC', () {
      final tokyo = tz.getLocation('Asia/Tokyo');
      final now = tz.TZDateTime(tokyo, 2026, 6, 10, 23);
      final plan = _daily(_plan(now));
      expect(plan.first.when, tz.TZDateTime(tokyo, 2026, 6, 11, 17));
      final utcPlan = _daily(_plan(tz.TZDateTime.utc(2026, 6, 10, 8)));
      expect(utcPlan.first.when, tz.TZDateTime.utc(2026, 6, 10, 17));
    });

    test("meeting today's goal skips today's reminder only", () {
      final game = _streak(
        3,
        '2026-06-10',
        dailyXp: 250,
        dailyDay: '2026-06-10',
      );
      final plan = _daily(_plan(_ny(2026, 6, 10, 9), game: game));
      expect(plan.first.when, _ny(2026, 6, 11, 17));
    });

    test("yesterday's goal does not count for today", () {
      final game = _streak(
        3,
        '2026-06-09',
        dailyXp: 999,
        dailyDay: '2026-06-09',
      );
      final plan = _daily(_plan(_ny(2026, 6, 10, 9), game: game));
      expect(plan.first.when, _ny(2026, 6, 10, 17));
    });

    test('mentions the streak while it is alive, the goal otherwise', () {
      final alive = _daily(
        _plan(_ny(2026, 6, 10, 9), game: _streak(6, '2026-06-09')),
      );
      expect('${alive.first.title} ${alive.first.body}', contains('6'));
      final fresh = _daily(_plan(_ny(2026, 6, 10, 9)));
      for (final r in fresh) {
        final text = '${r.title} ${r.body}';
        expect(text, isNot(contains('streak')));
      }
      expect(
        fresh.map((r) => '${r.title} ${r.body}').any((t) => t.contains('10')),
        isTrue,
        reason: 'some fresh copy mentions the 10-minute goal',
      );
    });

    test('copy rotates from day to day and is fully filled in', () {
      final plan = _daily(_plan(_ny(2026, 6, 10, 9)));
      expect(plan.map((r) => r.title).toSet().length, greaterThan(2));
      for (var i = 1; i < plan.length; i++) {
        expect(plan[i].title, isNot(plan[i - 1].title));
      }
      for (final r in _plan(
        _ny(2026, 6, 10, 9),
        game: _streak(2, '2026-06-10'),
      )) {
        expect(r.title + r.body, isNot(contains('{')));
      }
    });
  });

  group('streak nudge', () {
    test('fires this evening when the streak is alive and goal not met', () {
      final plan = _nudges(
        _plan(_ny(2026, 6, 10, 12), game: _streak(5, '2026-06-09')),
      );
      expect(plan, hasLength(1));
      final nudge = plan.single;
      expect(nudge.when, _ny(2026, 6, 10, 20));
      expect(nudge.payload, kReminderRoutePractice);
      expect('${nudge.title} ${nudge.body}', contains('5-day streak'));
      expect(
        ReminderCopy.nudgeAtRisk.map((t) => t.title.replaceAll('{n}', '5')),
        contains(nudge.title),
      );
    });

    test("meeting today's goal cancels today's nudge, keeps tomorrow's", () {
      final before = _streak(
        5,
        '2026-06-10',
        dailyXp: 50,
        dailyDay: '2026-06-10',
      );
      final now = _ny(2026, 6, 10, 18);
      expect(
        _nudges(_plan(now, game: before)).first.when,
        _ny(2026, 6, 10, 20),
      );

      final after = _streak(
        5,
        '2026-06-10',
        dailyXp: 230,
        dailyDay: '2026-06-10',
      );
      final plan = _nudges(_plan(now, game: after));
      expect(plan.where((r) => dayKey(r.when) == '2026-06-10'), isEmpty);
      // Studied today, so tomorrow the streak is at risk again.
      expect(plan.single.when, _ny(2026, 6, 11, 20));
    });

    test('active today but goal open: goal copy instead of at-risk copy', () {
      final game = _streak(
        4,
        '2026-06-10',
        dailyXp: 40,
        dailyDay: '2026-06-10',
      );
      final today = _nudges(_plan(_ny(2026, 6, 10, 9), game: game)).first;
      expect(
        ReminderCopy.nudgeGoalPending
            .map((t) => t.title.replaceAll('{n}', '4'))
            .contains(today.title),
        isTrue,
      );
    });

    test('a broken streak gets no nudge', () {
      final plan = _plan(_ny(2026, 6, 10, 12), game: _streak(8, '2026-06-07'));
      expect(_nudges(plan), isEmpty);
      // ...and the daily copy no longer brags about the lost streak.
      expect(_daily(plan).first.title, isNot(contains('8')));
    });

    test('no streak, no nudge', () {
      expect(_nudges(_plan(_ny(2026, 6, 10, 12))), isEmpty);
    });

    test('banked freezes keep later days savable', () {
      final noFreeze = _nudges(
        _plan(_ny(2026, 6, 10, 12), game: _streak(5, '2026-06-09')),
      );
      expect(noFreeze.map((r) => dayKey(r.when)), ['2026-06-10']);

      final twoFreezes = _nudges(
        _plan(_ny(2026, 6, 10, 12), game: _streak(5, '2026-06-09', freezes: 2)),
      );
      expect(twoFreezes.map((r) => dayKey(r.when)), [
        '2026-06-10',
        '2026-06-11',
        '2026-06-12',
      ]);

      // Missed a day already, one freeze bridges it: still savable today.
      final bridged = _nudges(
        _plan(_ny(2026, 6, 10, 12), game: _streak(5, '2026-06-08', freezes: 1)),
      );
      expect(bridged.map((r) => dayKey(r.when)), ['2026-06-10']);
    });

    test('evening already past: no nudge for today', () {
      final plan = _nudges(
        _plan(_ny(2026, 6, 10, 20, 1), game: _streak(5, '2026-06-09')),
      );
      expect(plan, isEmpty);
    });

    test('nudge switched off: daily reminders only', () {
      final plan = _plan(
        _ny(2026, 6, 10, 12),
        settings: _on.copyWith(streakNudge: false),
        game: _streak(5, '2026-06-09'),
      );
      expect(_nudges(plan), isEmpty);
      expect(_daily(plan), isNotEmpty);
    });

    test('fires on the evening of a DST change at local 8 PM', () {
      final plan = _nudges(
        _plan(_ny(2026, 3, 8, 1), game: _streak(3, '2026-03-07')),
      );
      expect(plan.single.when, _ny(2026, 3, 8, 20));
      expect(plan.single.when.toUtc().hour, 0); // EDT: UTC-4
    });

    test('nudge time follows a late daily reminder, never after 10 PM', () {
      int? at(int minutes) =>
          streakNudgeMinutesFor(_on.copyWith(minutesOfDay: minutes));
      expect(at(7 * 60), kStreakNudgeMinutes);
      expect(at(17 * 60), 20 * 60);
      expect(at(19 * 60), 20 * 60);
      expect(at(19 * 60 + 30), 20 * 60 + 30);
      expect(at(21 * 60), 22 * 60);
      expect(at(21 * 60 + 1), isNull);
      expect(streakNudgeMinutesFor(const ReminderSettings()), isNull);
      expect(streakNudgeMinutesFor(_on.copyWith(streakNudge: false)), isNull);
    });

    test('a 10:30 PM reminder carries the streak itself (no extra nudge)', () {
      final plan = _plan(
        _ny(2026, 6, 10, 12),
        settings: _on.copyWith(minutesOfDay: 22 * 60 + 30),
        game: _streak(5, '2026-06-09'),
      );
      expect(_nudges(plan), isEmpty);
      expect(_daily(plan).first.when, _ny(2026, 6, 10, 22, 30));
      expect(_daily(plan).first.title + _daily(plan).first.body, contains('5'));
    });
  });

  test('every planned time is in the future and ids are unique', () {
    final now = _ny(2026, 6, 10, 19, 30);
    final plan = _plan(
      now,
      settings: _on.copyWith(minutesOfDay: 6 * 60),
      game: _streak(12, '2026-06-10', freezes: 3),
    );
    expect(plan.every((r) => r.when.isAfter(now)), isTrue);
    expect(plan.map((r) => r.id).toSet(), hasLength(plan.length));
  });

  test('savableStreakOn mirrors the streak engine', () {
    final g = _streak(7, '2026-06-10', freezes: 1);
    expect(ReminderPlanner.savableStreakOn(g, '2026-06-10'), 7);
    expect(ReminderPlanner.savableStreakOn(g, '2026-06-11'), 7);
    expect(ReminderPlanner.savableStreakOn(g, '2026-06-12'), 7); // 1 freeze
    expect(ReminderPlanner.savableStreakOn(g, '2026-06-13'), 0);
    expect(ReminderPlanner.savableStreakOn(GameState(), '2026-06-13'), 0);
  });
}
