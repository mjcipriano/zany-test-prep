@Tags(['screenshots'])
library;

import 'dart:convert';
import 'dart:io';
import 'dart:ui' as ui;

import 'package:flutter/material.dart';
import 'package:flutter/rendering.dart';
import 'package:flutter/services.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:flutter_test/flutter_test.dart';
import 'package:zany_test_prep/app/app.dart';
import 'package:zany_test_prep/app/app_controller.dart';
import 'package:zany_test_prep/core/sound_service.dart';
import 'package:zany_test_prep/data/local/key_value_store.dart';
import 'package:zany_test_prep/data/repositories/avatar_repository.dart';
import 'package:zany_test_prep/data/repositories/content_repository.dart';
import 'package:zany_test_prep/domain/models/profile.dart';
import 'package:zany_test_prep/domain/models/progress.dart';

// Generates real PNG screenshots into docs/screenshots/ by rendering the app
// headlessly with the actual Roboto + Material Icons fonts loaded.
//
//   flutter test --tags screenshots test/screenshots/screenshot_test.dart
//
// This is a generator, not an assertion test; it always passes if it can render.

const _fontDir = '.tooling/flutter/bin/cache/artifacts/material_fonts';
final _outDir = Directory('docs/screenshots');
final _boundaryKey = GlobalKey();

final String _examsJson = File('assets/content/exams.json').readAsStringSync();
final String _bundleJson = File(
  'assets/content/sat.bundle.json',
).readAsStringSync();
final String _avatarCatalogJson = File(
  'assets/avatar/manifest/avatar_catalog.json',
).readAsStringSync();

Future<void> _loadFont(String family, List<String> files) async {
  final loader = FontLoader(family);
  var added = 0;
  for (final f in files) {
    final file = File('$_fontDir/$f');
    if (!file.existsSync()) continue;
    loader.addFont(
      Future.value(
        ByteData.view(Uint8List.fromList(file.readAsBytesSync()).buffer),
      ),
    );
    added++;
  }
  if (added > 0) await loader.load();
}

Future<void> _pump(WidgetTester tester, MemoryStore store) async {
  tester.view.physicalSize = const Size(393, 852);
  tester.view.devicePixelRatio = 1.0;
  await tester.pumpWidget(
    RepaintBoundary(
      key: _boundaryKey,
      child: ProviderScope(
        overrides: [
          contentRepositoryProvider.overrideWithValue(
            ContentRepository(
              reader: (path) async =>
                  path.endsWith('exams.json') ? _examsJson : _bundleJson,
            ),
          ),
          avatarRepositoryProvider.overrideWithValue(
            AvatarRepository(reader: (path) async => _avatarCatalogJson),
          ),
          keyValueStoreProvider.overrideWith((ref) async => store),
          soundServiceProvider.overrideWithValue(NoopSoundService()),
        ],
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

Future<void> _onboard(WidgetTester tester) async {
  for (var i = 0; i < 4; i++) {
    await tester.tap(find.text('Continue'));
    await tester.pumpAndSettle();
  }
  await tester.tap(find.text('Start learning'));
  await tester.pumpAndSettle();
}

Future<void> _answerVisibleQuestion(WidgetTester tester) async {
  final field = find.byType(TextField);
  if (field.evaluate().isNotEmpty) {
    await tester.enterText(field.first, '1');
  } else {
    final choice = find.text('A').first;
    await tester.scrollUntilVisible(
      choice,
      250,
      scrollable: find.byType(Scrollable).first,
    );
    await tester.tap(choice);
  }
  await tester.pumpAndSettle();
}

void main() {
  setUpAll(() async {
    // Roboto for text; add a monochrome emoji font (if present) as a fallback in
    // the same family so emoji codepoints render instead of notdef boxes.
    await _loadFont('Roboto', [
      'Roboto-Regular.ttf',
      'Roboto-Medium.ttf',
      'Roboto-Bold.ttf',
    ]);
    await _loadFont('MaterialIcons', ['MaterialIcons-Regular.otf']);
    // Emoji fallback (matches the theme's fontFamilyFallback). Optional.
    if (File('.tooling/fonts/NotoEmoji-Regular.ttf').existsSync()) {
      final loader = FontLoader('NotoEmoji');
      final bytes = File(
        '.tooling/fonts/NotoEmoji-Regular.ttf',
      ).readAsBytesSync();
      loader.addFont(
        Future.value(ByteData.view(Uint8List.fromList(bytes).buffer)),
      );
      await loader.load();
    }
  });

  final fontsAvailable = File('$_fontDir/Roboto-Regular.ttf').existsSync();

  testWidgets('generate screenshots', skip: !fontsAvailable, (tester) async {
    final store = MemoryStore();
    await _pump(tester, store);

    // 1. Onboarding welcome.
    await _shoot(tester, '01_onboarding');

    // 2. Home learning path.
    await _onboard(tester);
    await _shoot(tester, '02_home');

    // 3. Lesson teaching card.
    await tester.tap(find.textContaining('Main Idea').first);
    await tester.pumpAndSettle();
    await _shoot(tester, '03_teaching');

    // 4. A question.
    await tester.tap(find.text('Start'));
    await tester.pumpAndSettle();
    await _shoot(tester, '04_question');

    // 5. Immediate feedback after answering.
    await _answerVisibleQuestion(tester);
    await tester.tap(find.text('Check'));
    await tester.pumpAndSettle();
    await _shoot(tester, '05_feedback');

    // 6. Finish the lesson to capture the celebration summary.
    for (var guard = 0; guard < 80; guard++) {
      if (find.text('Lesson complete!').evaluate().isNotEmpty) break;
      if (find.text('Check').evaluate().isNotEmpty) {
        await _answerVisibleQuestion(tester);
        if (find.text('Check').evaluate().isNotEmpty) {
          await tester.tap(find.text('Check'));
          await tester.pumpAndSettle();
        }
      } else if (find.text('Finish').evaluate().isNotEmpty) {
        await tester.tap(find.text('Finish'));
        await tester.pumpAndSettle();
      } else if (find.text('Continue').evaluate().isNotEmpty) {
        await tester.tap(find.text('Continue'));
        await tester.pumpAndSettle();
      }
    }
    if (find.text('Lesson complete!').evaluate().isNotEmpty) {
      await _shoot(tester, '06_summary');
      await tester.tap(find.text('Continue'));
      await tester.pumpAndSettle();
    }

    // 7. Settings.
    await tester.tap(find.byIcon(Icons.settings_rounded));
    await tester.pumpAndSettle();
    await _shoot(tester, '07_settings');
    // Back to home.
    await tester.pageBack();
    await tester.pumpAndSettle();

    // 8. Achievements.
    await tester.tap(find.byIcon(Icons.emoji_events_rounded));
    await tester.pumpAndSettle();
    await _shoot(tester, '08_achievements');
    await tester.pageBack();
    await tester.pumpAndSettle();

    // 9. Progress dashboard.
    await tester.tap(find.byIcon(Icons.bar_chart_rounded));
    await tester.pumpAndSettle();
    await _shoot(tester, '09_dashboard');
    await tester.pageBack();
    await tester.pumpAndSettle();

    // 10. Rewards hub (chests, XP wallet, avatar).
    await tester.tap(find.byIcon(Icons.card_giftcard_rounded));
    await tester.pumpAndSettle();
    await _shoot(tester, '10_rewards');

    // 11. Store.
    await tester.tap(find.text('Store'));
    await tester.pumpAndSettle();
    await _shoot(tester, '11_store');

    // 12. Store — Items tab (shows the streak-freeze card).
    await tester.tap(find.text('Items'));
    await tester.pumpAndSettle();
    await _shoot(tester, '12_store_items');
  });

  testWidgets('chest reveal screenshot', skip: !fontsAvailable, (tester) async {
    // Seed an onboarded user who already has a chest, so we can capture the
    // animated reveal.
    final store = MemoryStore();
    store.setString('onboarded.v1', 'true');
    store.setString(
      'profile.v1',
      jsonEncode(UserProfile.initial('sat', 10).toJson()),
    );
    final progress = AppProgress();
    progress.game.unopenedChests = 1;
    progress.game.totalXp = 500;
    store.setString('progress.v1', jsonEncode(progress.toJson()));

    await _pump(tester, store);
    await tester.tap(find.byIcon(Icons.card_giftcard_rounded));
    await tester.pumpAndSettle();
    await tester.tap(find.text('Open'));
    await tester.pumpAndSettle();
    await tester.tap(find.text('Open chest'));
    await tester.pump();
    await tester.pump(const Duration(milliseconds: 50));
    await tester.pump(const Duration(seconds: 2));
    await tester.pumpAndSettle();
    await _shoot(tester, '13_chest_reward');
  });

  testWidgets('owned items customizer screenshots', skip: !fontsAvailable, (
    tester,
  ) async {
    const owned = {
      'item_001_classic_cap', // headwear
      'item_041_round_glasses', // eyewear
      'item_071_simple_mask', // face_accessory
      'pet_fox_study_cap_001', // side pet
    };
    const paths = [
      'assets/avatar/avatars/starter/avatar_basic_001_nova_learner.png',
      'assets/avatar/items/headwear/item_001_classic_cap.png',
      'assets/avatar/items/eyewear/item_041_round_glasses.png',
      'assets/avatar/items/face_accessory/item_071_simple_mask.png',
      'assets/avatar/pets/common/pet_fox_study_cap_001.png',
    ];

    final store = MemoryStore();
    store.setString('onboarded.v1', 'true');
    store.setString(
      'profile.v1',
      jsonEncode(UserProfile.initial('sat', 10).toJson()),
    );
    final progress = AppProgress();
    progress.game.totalXp = 5000;
    progress.game.ownedAssetIds.addAll(owned);
    store.setString('progress.v1', jsonEncode(progress.toJson()));

    await _pump(tester, store);
    // Warm the image cache so the avatar art renders in the capture.
    await tester.runAsync(() async {
      final ctx = _boundaryKey.currentContext!;
      for (final p in paths) {
        await precacheImage(AssetImage(p), ctx);
      }
    });
    await tester.pumpAndSettle();

    await tester.tap(find.byIcon(Icons.card_giftcard_rounded));
    await tester.pumpAndSettle();
    await tester.tap(find.text('Customize'));
    await tester.pumpAndSettle();

    // Scroll the owned-items rows into view (the regression area) and capture.
    final scrollable = find.byType(Scrollable).first;
    await tester.scrollUntilVisible(
      find.text('Classic Cap'),
      300,
      scrollable: scrollable,
    );
    await tester.pumpAndSettle();
    await _shoot(tester, '14_avatar_items');

    // Equip everything (rows are in view), then scroll back up to the preview.
    for (var i = 0; i < 4; i++) {
      final equip = find.text('Equip');
      if (equip.evaluate().isEmpty) break;
      await tester.tap(equip.first);
      await tester.pumpAndSettle();
    }
    await tester.drag(scrollable, const Offset(0, 1200));
    await tester.pumpAndSettle();
    await _shoot(tester, '15_avatar_equipped');
  });
}
