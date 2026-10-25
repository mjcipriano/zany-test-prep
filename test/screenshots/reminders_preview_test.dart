@Tags(['screenshots'])
library;

import 'dart:io';
import 'dart:ui' as ui;

import 'package:flutter/material.dart';
import 'package:flutter/rendering.dart';
import 'package:flutter/services.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:flutter_test/flutter_test.dart';
import 'package:zany_test_prep/app/app.dart';
import 'package:zany_test_prep/data/local/key_value_store.dart';
import 'package:zany_test_prep/data/repositories/progress_repository.dart';
import 'package:zany_test_prep/domain/models/profile.dart';
import 'package:zany_test_prep/domain/models/progress.dart';
import 'package:zany_test_prep/domain/models/reminder_settings.dart';

import '../helpers/fake_notification_gateway.dart';
import '../helpers/pump_app.dart';

// Phone-size previews of the reminder UI (360x780 logical at 3x) into
// build/previews/:
//
//   flutter test --tags screenshots test/screenshots/reminders_preview_test.dart

final _outDir = Directory('build/previews');
final _boundaryKey = GlobalKey();

String get _fontDir {
  final root = Platform.environment['FLUTTER_ROOT'];
  final fromRoot = '$root/bin/cache/artifacts/material_fonts';
  return root != null && Directory(fromRoot).existsSync()
      ? fromRoot
      : '.tooling/flutter/bin/cache/artifacts/material_fonts';
}

Future<void> _loadFont(String family, List<String> files) async {
  final loader = FontLoader(family);
  for (final f in files) {
    final file = File('$_fontDir/$f');
    if (!file.existsSync()) continue;
    loader.addFont(
      Future.value(
        ByteData.view(Uint8List.fromList(file.readAsBytesSync()).buffer),
      ),
    );
  }
  await loader.load();
}

Future<MemoryStore> _store(ReminderSettings reminders) async {
  final store = MemoryStore();
  final repo = ProgressRepository(store);
  await repo.saveProfile(
    UserProfile.initial('sat', 10).copyWith(reminders: reminders),
  );
  await repo.setOnboarded(true);
  final progress = AppProgress();
  progress.game
    ..currentStreak = 6
    ..longestStreak = 9
    ..lastActiveDay = dayKey(DateTime.now().subtract(const Duration(days: 1)))
    ..totalXp = 1840;
  await repo.saveProgress(progress);
  return store;
}

Future<void> _pump(
  WidgetTester tester,
  MemoryStore store,
  FakeNotificationGateway gateway,
) async {
  tester.view.physicalSize = const Size(360, 780);
  tester.view.devicePixelRatio = 1.0;
  addTearDown(tester.view.reset);
  await tester.pumpWidget(
    RepaintBoundary(
      key: _boundaryKey,
      child: ProviderScope(
        overrides: testOverrides(store, notifications: gateway),
        child: const ZanyTestPrepApp(),
      ),
    ),
  );
  await tester.pump();
  await tester.pumpAndSettle();
}

Future<void> _shoot(WidgetTester tester, String name) async {
  await tester.pumpAndSettle();
  await tester.runAsync(() async {
    final boundary =
        _boundaryKey.currentContext!.findRenderObject()
            as RenderRepaintBoundary;
    final image = await boundary.toImage(pixelRatio: 3.0);
    final bytes = await image.toByteData(format: ui.ImageByteFormat.png);
    _outDir.createSync(recursive: true);
    File(
      '${_outDir.path}/$name.png',
    ).writeAsBytesSync(bytes!.buffer.asUint8List());
    image.dispose();
  });
}

Future<void> _openSettingsAtReminders(WidgetTester tester) async {
  await tester.tap(find.byIcon(Icons.settings_rounded));
  await tester.pumpAndSettle();
  await tester.ensureVisible(find.text('REMINDERS'));
  await tester.pumpAndSettle();
  // Scroll the section label to the top of the screen.
  Scrollable.ensureVisible(
    tester.element(find.text('REMINDERS')),
    alignment: 0.02,
  );
  await tester.pumpAndSettle();
}

void main() {
  setUpAll(() async {
    await _loadFont('Roboto', [
      'Roboto-Regular.ttf',
      'Roboto-Medium.ttf',
      'Roboto-Bold.ttf',
    ]);
    await _loadFont('MaterialIcons', ['MaterialIcons-Regular.otf']);
  });

  final fontsAvailable = File('$_fontDir/Roboto-Regular.ttf').existsSync();

  testWidgets('settings: reminders on', skip: !fontsAvailable, (tester) async {
    await _pump(
      tester,
      await _store(
        const ReminderSettings(enabled: true, minutesOfDay: 16 * 60 + 30),
      ),
      FakeNotificationGateway(),
    );
    await _openSettingsAtReminders(tester);
    await _shoot(tester, 'reminders_settings_on');
  });

  testWidgets('settings: reminders off', skip: !fontsAvailable, (tester) async {
    await _pump(
      tester,
      await _store(const ReminderSettings()),
      FakeNotificationGateway(),
    );
    await _openSettingsAtReminders(tester);
    await _shoot(tester, 'reminders_settings_off');
  });

  testWidgets('settings: permission denied', skip: !fontsAvailable, (
    tester,
  ) async {
    await _pump(
      tester,
      await _store(const ReminderSettings()),
      FakeNotificationGateway(grantOnRequest: false),
    );
    await _openSettingsAtReminders(tester);
    await tester.tap(
      find.descendant(
        of: find.widgetWithText(SwitchListTile, 'Daily reminder'),
        matching: find.byType(Switch),
      ),
    );
    await _shoot(tester, 'reminders_settings_denied');
  });

  testWidgets('time picker', skip: !fontsAvailable, (tester) async {
    await _pump(
      tester,
      await _store(const ReminderSettings(enabled: true)),
      FakeNotificationGateway(),
    );
    await _openSettingsAtReminders(tester);
    await tester.tap(find.byKey(const ValueKey('reminder-time')));
    await _shoot(tester, 'reminders_time_picker');
  });

  for (final on in [false, true]) {
    testWidgets(
      'onboarding offer (${on ? 'on' : 'off'})',
      skip: !fontsAvailable,
      (tester) async {
        await _pump(tester, MemoryStore(), FakeNotificationGateway());
        for (var i = 0; i < 4; i++) {
          await tester.tap(find.text('Continue'));
          await tester.pumpAndSettle();
        }
        final offer = find.text('Want a daily reminder?');
        if (on) {
          await tester.ensureVisible(offer);
          await tester.tap(
            find.descendant(
              of: find.widgetWithText(SwitchListTile, 'Want a daily reminder?'),
              matching: find.byType(Switch),
            ),
          );
          await tester.pumpAndSettle();
        }
        await tester.ensureVisible(
          find.text('5:00 PM').evaluate().isEmpty
              ? offer
              : find.text('5:00 PM'),
        );
        await _shoot(tester, 'onboarding_reminder_offer_${on ? 'on' : 'off'}');
      },
    );
  }
}
