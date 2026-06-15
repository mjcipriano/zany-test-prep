import 'dart:io';

import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:flutter_test/flutter_test.dart';
import 'package:zany_test_prep/app/app.dart';
import 'package:zany_test_prep/app/app_controller.dart';
import 'package:zany_test_prep/core/sound_service.dart';
import 'package:zany_test_prep/data/local/key_value_store.dart';
import 'package:zany_test_prep/data/repositories/content_repository.dart';

// Preloaded once from disk (cwd == repo root during tests). Returned to the app
// via completed futures so bootstrap resolves through microtasks under the
// test's controlled async — no real event loop / runAsync needed.
final String _examsJson = File('assets/content/exams.json').readAsStringSync();
final String _bundleJson = File(
  'assets/content/sat.bundle.json',
).readAsStringSync();

ContentRepository _testContentRepository() => ContentRepository(
  reader: (path) async =>
      path.endsWith('exams.json') ? _examsJson : _bundleJson,
);

/// Pumps the full app with test overrides. Reuse [store] across pumps to
/// simulate an app restart with persisted state.
Future<MemoryStore> pumpApp(WidgetTester tester, {MemoryStore? store}) async {
  final memory = store ?? MemoryStore();
  // Tall viewport so long scrollable screens render without manual scrolling.
  tester.view.physicalSize = const Size(1000, 3200);
  tester.view.devicePixelRatio = 1.0;
  addTearDown(() {
    tester.view.resetPhysicalSize();
    tester.view.resetDevicePixelRatio();
  });

  await tester.pumpWidget(
    ProviderScope(
      overrides: [
        contentRepositoryProvider.overrideWithValue(_testContentRepository()),
        keyValueStoreProvider.overrideWith((ref) async => memory),
        soundServiceProvider.overrideWithValue(NoopSoundService()),
      ],
      child: const ZanyTestPrepApp(),
    ),
  );
  // Swap splash for the loaded screen (microtask bootstrap), then settle.
  await tester.pump();
  await tester.pumpAndSettle();
  return memory;
}
