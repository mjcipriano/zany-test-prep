import 'package:flutter/material.dart';
import 'package:flutter_test/flutter_test.dart';
import 'package:go_router/go_router.dart';
import 'package:zany_test_prep/data/local/key_value_store.dart';
import 'package:zany_test_prep/data/repositories/progress_repository.dart';
import 'package:zany_test_prep/domain/models/profile.dart';
import 'package:zany_test_prep/domain/models/reminder_settings.dart';
import 'package:zany_test_prep/domain/services/reminder_planner.dart';
import 'package:zany_test_prep/features/practice/practice_screen.dart';

import '../helpers/fake_notification_gateway.dart';
import '../helpers/pump_app.dart';

/// A store holding an onboarded SAT profile with [reminders].
Future<MemoryStore> _onboardedStore([
  ReminderSettings reminders = const ReminderSettings(),
]) async {
  final store = MemoryStore();
  final repo = ProgressRepository(store);
  await repo.saveProfile(
    UserProfile.initial('sat', 10).copyWith(reminders: reminders),
  );
  await repo.setOnboarded(true);
  return store;
}

ReminderSettings _stored(MemoryStore store) =>
    ProgressRepository(store).loadProfile()!.reminders;

Future<void> _openSettings(WidgetTester tester) async {
  await tester.tap(find.byIcon(Icons.settings_rounded));
  await tester.pumpAndSettle();
}

Finder _switch(String title) => find.descendant(
  of: find.widgetWithText(SwitchListTile, title),
  matching: find.byType(Switch),
);

const _blockedTitle = 'Notifications are off for this app';

void main() {
  group('Settings → Reminders', () {
    testWidgets('off by default; turning on asks permission and schedules', (
      tester,
    ) async {
      final gateway = FakeNotificationGateway();
      final store = await pumpApp(
        tester,
        store: await _onboardedStore(),
        notifications: gateway,
      );
      await _openSettings(tester);

      expect(find.text('REMINDERS'), findsOneWidget);
      expect(
        find.text('A friendly nudge to study, once a day'),
        findsOneWidget,
      );
      expect(find.text('Reminder time'), findsNothing);
      expect(gateway.permissionRequests, 0);

      await tester.tap(_switch('Daily reminder'));
      await tester.pumpAndSettle();

      expect(gateway.permissionRequests, 1);
      expect(find.text('Every day at 5:00 PM'), findsOneWidget);
      expect(find.text('Reminder time'), findsOneWidget);
      expect(find.text('Streak saver'), findsOneWidget);
      expect(find.textContaining('Heads-up at 8:00 PM'), findsOneWidget);
      expect(find.text(_blockedTitle), findsNothing);
      expect(_stored(store).enabled, isTrue);
      expect(gateway.pending, isNotEmpty);

      // And off again: nothing stays scheduled.
      await tester.tap(_switch('Daily reminder'));
      await tester.pumpAndSettle();
      expect(_stored(store).enabled, isFalse);
      expect(gateway.pending, isEmpty);
      expect(find.text('Reminder time'), findsNothing);
    });

    testWidgets('the time picker changes the reminder time', (tester) async {
      final gateway = FakeNotificationGateway();
      final store = await pumpApp(
        tester,
        store: await _onboardedStore(const ReminderSettings(enabled: true)),
        notifications: gateway,
      );
      await _openSettings(tester);

      await tester.tap(find.byKey(const ValueKey('reminder-time')));
      await tester.pumpAndSettle();
      expect(find.text('Remind me at'), findsOneWidget);

      // Type the time instead of dragging the dial.
      await tester.tap(find.byIcon(Icons.keyboard_outlined));
      await tester.pumpAndSettle();
      final fields = find.descendant(
        of: find.byType(Dialog),
        matching: find.byType(TextField),
      );
      await tester.enterText(fields.at(0), '7');
      await tester.enterText(fields.at(1), '45');
      await tester.tap(find.text('OK'));
      await tester.pumpAndSettle();

      expect(find.text('Every day at 7:45 PM'), findsOneWidget);
      expect(_stored(store).minutesOfDay, 19 * 60 + 45);
      // Rescheduled at the new time; the nudge moves to an hour later.
      final daily = gateway.pending.values.firstWhere(
        (r) => r.kind == ReminderKind.daily,
      );
      expect((daily.when.hour, daily.when.minute), (19, 45));
      expect(find.textContaining('Heads-up at 8:45 PM'), findsOneWidget);
    });

    testWidgets('cancelling the time picker keeps the old time', (
      tester,
    ) async {
      final store = await pumpApp(
        tester,
        store: await _onboardedStore(const ReminderSettings(enabled: true)),
      );
      await _openSettings(tester);
      await tester.tap(find.byKey(const ValueKey('reminder-time')));
      await tester.pumpAndSettle();
      await tester.tap(find.text('Cancel'));
      await tester.pumpAndSettle();
      expect(_stored(store).minutesOfDay, kDefaultReminderMinutes);
    });

    testWidgets('streak saver can be switched off on its own', (tester) async {
      final gateway = FakeNotificationGateway();
      final store = await pumpApp(
        tester,
        store: await _onboardedStore(const ReminderSettings(enabled: true)),
        notifications: gateway,
      );
      await _openSettings(tester);
      await tester.tap(_switch('Streak saver'));
      await tester.pumpAndSettle();
      expect(_stored(store).streakNudge, isFalse);
      expect(_stored(store).enabled, isTrue);
    });

    testWidgets('permission denied: stays off and shows how to enable', (
      tester,
    ) async {
      final gateway = FakeNotificationGateway(grantOnRequest: false);
      final store = await pumpApp(
        tester,
        store: await _onboardedStore(),
        notifications: gateway,
      );
      await _openSettings(tester);

      await tester.tap(_switch('Daily reminder'));
      await tester.pumpAndSettle();

      expect(gateway.permissionRequests, 1);
      expect(_stored(store).enabled, isFalse);
      expect(tester.widget<Switch>(_switch('Daily reminder')).value, isFalse);
      expect(find.text(_blockedTitle), findsOneWidget);
      expect(find.textContaining('allow its notifications'), findsOneWidget);
      expect(gateway.pending, isEmpty);

      await tester.tap(find.text('Open settings'));
      await tester.pumpAndSettle();
      expect(gateway.settingsOpened, 1);

      // Allowed in the system settings, then switched on again: works.
      gateway.grantOnRequest = true;
      await tester.tap(_switch('Daily reminder'));
      await tester.pumpAndSettle();
      expect(_stored(store).enabled, isTrue);
      expect(find.text(_blockedTitle), findsNothing);
    });

    testWidgets('settings app unavailable: falls back to a snackbar hint', (
      tester,
    ) async {
      final gateway = FakeNotificationGateway(
        grantOnRequest: false,
        canOpenSettings: false,
      );
      await pumpApp(
        tester,
        store: await _onboardedStore(),
        notifications: gateway,
      );
      await _openSettings(tester);
      await tester.tap(_switch('Daily reminder'));
      await tester.pumpAndSettle();
      await tester.tap(find.text('Open settings'));
      await tester.pump();
      expect(
        find.textContaining("Open your phone's Settings app"),
        findsOneWidget,
      );
    });

    testWidgets('reminders on but blocked by the OS: shows the note', (
      tester,
    ) async {
      final gateway = FakeNotificationGateway(allowed: false);
      await pumpApp(
        tester,
        store: await _onboardedStore(const ReminderSettings(enabled: true)),
        notifications: gateway,
      );
      await _openSettings(tester);
      expect(find.text(_blockedTitle), findsOneWidget);
    });

    testWidgets('reminders off and OS blocked: no nagging note', (
      tester,
    ) async {
      final gateway = FakeNotificationGateway(allowed: false);
      await pumpApp(
        tester,
        store: await _onboardedStore(),
        notifications: gateway,
      );
      await _openSettings(tester);
      expect(find.text(_blockedTitle), findsNothing);
    });
  });

  group('Onboarding reminder offer', () {
    Future<void> toLastStep(WidgetTester tester) async {
      for (var i = 0; i < 4; i++) {
        await tester.tap(find.text('Continue'));
        await tester.pumpAndSettle();
      }
      expect(find.text('Want a daily reminder?'), findsOneWidget);
    }

    testWidgets('default is off and never asks for permission', (tester) async {
      final gateway = FakeNotificationGateway();
      final store = await pumpApp(tester, notifications: gateway);
      await onboardDefault(tester);
      expect(gateway.permissionRequests, 0);
      expect(_stored(store).enabled, isFalse);
      expect(gateway.pending, isEmpty);
    });

    testWidgets('opting in asks permission, picks a time and schedules', (
      tester,
    ) async {
      final gateway = FakeNotificationGateway();
      final store = await pumpApp(tester, notifications: gateway);
      await toLastStep(tester);

      await tester.tap(_switch('Want a daily reminder?'));
      await tester.pumpAndSettle();
      expect(gateway.permissionRequests, 1);
      expect(find.text('5:00 PM'), findsOneWidget);

      await tester.tap(find.byKey(const ValueKey('onboarding-reminder-time')));
      await tester.pumpAndSettle();
      await tester.tap(find.byIcon(Icons.keyboard_outlined));
      await tester.pumpAndSettle();
      final fields = find.descendant(
        of: find.byType(Dialog),
        matching: find.byType(TextField),
      );
      await tester.enterText(fields.at(0), '4');
      await tester.enterText(fields.at(1), '30');
      await tester.tap(find.text('OK'));
      await tester.pumpAndSettle();
      expect(find.text('4:30 PM'), findsOneWidget);

      await tester.tap(find.text('Start learning'));
      await tester.pumpAndSettle();
      expect(find.text('READING & WRITING'), findsOneWidget);
      expect(_stored(store).enabled, isTrue);
      expect(_stored(store).minutesOfDay, 16 * 60 + 30);
      expect(gateway.pending, isNotEmpty);
    });

    testWidgets('permission denied: offer stays off with the how-to note', (
      tester,
    ) async {
      final gateway = FakeNotificationGateway(grantOnRequest: false);
      final store = await pumpApp(tester, notifications: gateway);
      await toLastStep(tester);
      await tester.tap(_switch('Want a daily reminder?'));
      await tester.pumpAndSettle();
      expect(find.text(_blockedTitle), findsOneWidget);
      expect(find.text('5:00 PM'), findsNothing);

      await tester.tap(find.text('Start learning'));
      await tester.pumpAndSettle();
      expect(_stored(store).enabled, isFalse);
    });
  });

  group('Tapping a reminder', () {
    testWidgets('a streak nudge that launched the app opens Quick Practice', (
      tester,
    ) async {
      final gateway = FakeNotificationGateway(
        launchPayload: kReminderRoutePractice,
      );
      await pumpApp(
        tester,
        store: await _onboardedStore(),
        notifications: gateway,
      );
      expect(find.byType(PracticeScreen), findsOneWidget);
      // Pushed on top of Home, so leaving practice goes back there.
      final router = GoRouter.of(tester.element(find.byType(PracticeScreen)));
      expect(router.canPop(), isTrue);
      router.pop();
      await tester.pumpAndSettle();
      expect(find.text('READING & WRITING'), findsOneWidget);
    });

    testWidgets('a daily reminder launch lands on Home', (tester) async {
      final gateway = FakeNotificationGateway(
        launchPayload: kReminderRouteHome,
      );
      await pumpApp(
        tester,
        store: await _onboardedStore(),
        notifications: gateway,
      );
      expect(find.byType(PracticeScreen), findsNothing);
      expect(find.text('READING & WRITING'), findsOneWidget);
    });

    testWidgets('unknown payloads are ignored', (tester) async {
      final gateway = FakeNotificationGateway(launchPayload: '/settings');
      await pumpApp(
        tester,
        store: await _onboardedStore(),
        notifications: gateway,
      );
      expect(find.text('Settings'), findsNothing);
      expect(find.text('READING & WRITING'), findsOneWidget);
    });

    testWidgets('a tap while on Home opens practice; elsewhere it waits', (
      tester,
    ) async {
      final gateway = FakeNotificationGateway();
      await pumpApp(
        tester,
        store: await _onboardedStore(),
        notifications: gateway,
      );

      // Mid-way through something else (Settings here): no hijacking.
      await _openSettings(tester);
      gateway.tap(kReminderRoutePractice);
      await tester.pumpAndSettle();
      expect(find.byType(PracticeScreen), findsNothing);
      await tester.pageBack();
      await tester.pumpAndSettle();

      gateway.tap(kReminderRoutePractice);
      await tester.pumpAndSettle();
      expect(find.byType(PracticeScreen), findsOneWidget);
    });
  });
}
