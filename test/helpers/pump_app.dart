import 'dart:io';

import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:flutter_test/flutter_test.dart';
import 'package:zany_test_prep/app/app.dart';
import 'package:zany_test_prep/app/app_controller.dart';
import 'package:zany_test_prep/core/notifications/notification_gateway.dart';
import 'package:zany_test_prep/core/notifications/reminder_scheduler.dart';
import 'package:zany_test_prep/core/sound_service.dart';
import 'package:zany_test_prep/data/local/key_value_store.dart';
import 'package:zany_test_prep/data/repositories/avatar_repository.dart';
import 'package:zany_test_prep/data/repositories/content_repository.dart';

import 'fake_notification_gateway.dart';

// Preloaded once from disk (cwd == repo root during tests). Returned to the app
// via completed futures so bootstrap resolves through microtasks under the
// test's controlled async — no real event loop / runAsync needed.
final String _examsJson = File('assets/content/exams.json').readAsStringSync();
final Map<String, String> _bundleJson = {};

String _bundleFor(String examId) => _bundleJson.putIfAbsent(
  examId,
  () => File('assets/content/$examId.bundle.json').readAsStringSync(),
);

/// Serves the real committed exam index and bundles. [examsJson] overrides
/// assets/content/exams.json (e.g. to pretend only one exam ships).
ContentRepository testContentRepository({String? examsJson}) =>
    ContentRepository(
      reader: (path) async {
        if (path.endsWith('exams.json')) return examsJson ?? _examsJson;
        final name = path.split('/').last; // <exam>.bundle.json
        return _bundleFor(name.split('.').first);
      },
    );

final String _avatarCatalogJson = File(
  'assets/avatar/manifest/avatar_catalog.json',
).readAsStringSync();

AvatarRepository _testAvatarRepository() =>
    AvatarRepository(reader: (path) async => _avatarCatalogJson);

/// The provider overrides [pumpApp] uses (real content, in-memory store,
/// silent audio, fake notifications). Also handy for pumping a single screen
/// or a [ProviderContainer] in unit tests.
List<Override> testOverrides(
  MemoryStore memory, {
  String? examsJson,
  NotificationGateway? notifications,
}) => [
  contentRepositoryProvider.overrideWithValue(
    testContentRepository(examsJson: examsJson),
  ),
  avatarRepositoryProvider.overrideWithValue(_testAvatarRepository()),
  keyValueStoreProvider.overrideWith((ref) async => memory),
  soundServiceProvider.overrideWithValue(NoopSoundService()),
  notificationGatewayProvider.overrideWithValue(
    notifications ?? FakeNotificationGateway(),
  ),
];

/// Pumps the full app with test overrides. Reuse [store] across pumps to
/// simulate an app restart with persisted state.
Future<MemoryStore> pumpApp(
  WidgetTester tester, {
  MemoryStore? store,
  String? examsJson,
  NotificationGateway? notifications,
}) async {
  final memory = store ?? MemoryStore();
  // Tall viewport so long scrollable screens render without manual scrolling.
  tester.view.physicalSize = const Size(1000, 3200);
  tester.view.devicePixelRatio = 1.0;
  addTearDown(() {
    tester.view.resetPhysicalSize();
    tester.view.resetDevicePixelRatio();
  });

  // A real restart: tear down any previous tree first so no element state
  // (scroll offsets, controllers, provider caches) survives into the new app.
  if (store != null) {
    await tester.pumpWidget(const SizedBox.shrink());
    await tester.pump();
  }
  await tester.pumpWidget(
    ProviderScope(
      overrides: testOverrides(
        memory,
        examsJson: examsJson,
        notifications: notifications,
      ),
      child: const ZanyTestPrepApp(),
    ),
  );
  // Swap splash for the loaded screen (microtask bootstrap), then settle.
  await tester.pump();
  await tester.pumpAndSettle();
  return memory;
}

/// Steps through onboarding with the defaults (SAT, 10 min).
Future<void> onboardDefault(WidgetTester tester) async {
  for (var i = 0; i < 4; i++) {
    await tester.tap(find.text('Continue'));
    await tester.pumpAndSettle();
  }
  await tester.tap(find.text('Start learning'));
  await tester.pumpAndSettle();
}

/// Steps through onboarding choosing the exam whose picker label is
/// [examLabel] (e.g. 'ACT').
Future<void> onboardWithExam(WidgetTester tester, String examLabel) async {
  await tester.tap(find.text('Continue')); // welcome -> offline
  await tester.pumpAndSettle();
  await tester.tap(find.text('Continue')); // offline -> exam
  await tester.pumpAndSettle();
  expect(find.text('Choose your exam'), findsOneWidget);
  await tester.tap(find.text(examLabel));
  await tester.pumpAndSettle();
  await tester.tap(find.text('Continue')); // exam -> goal
  await tester.pumpAndSettle();
  await tester.tap(find.text('Continue')); // goal -> date
  await tester.pumpAndSettle();
  await tester.tap(find.text('Start learning'));
  await tester.pumpAndSettle();
}
