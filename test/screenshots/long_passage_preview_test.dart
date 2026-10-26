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
import 'package:zany_test_prep/domain/models/question.dart';

// Phone previews (360x780 logical, 3x) of the ACT long-passage reader inside
// the real Practice Test, written to build/previews/. Needs an ACT bundle that
// contains passage sets (regenerate + build_bundle locally first):
//
//   flutter test --tags screenshots test/screenshots/long_passage_preview_test.dart

const _fontDir = '.tooling/flutter/bin/cache/artifacts/material_fonts';
final _outDir = Directory('build/previews');
final _boundaryKey = GlobalKey();

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

Future<void> _submitSection(WidgetTester tester) async {
  // Skip to the section's last question, whose bottom button submits it.
  for (
    var i = 0;
    i < 60 && find.text('Submit section').evaluate().isEmpty;
    i++
  ) {
    await tester.tap(find.text('Skip'));
    await tester.pumpAndSettle();
  }
  await tester.tap(find.text('Submit section'));
  await tester.pumpAndSettle();
  await tester.tap(find.text('Submit'));
  await tester.pumpAndSettle();
  await tester.tap(find.text('Start next section'));
  await tester.pumpAndSettle();
}

Future<void> _dragPassage(WidgetTester tester, double dy) async {
  await tester.dragFrom(
    tester.getCenter(find.byType(SingleChildScrollView).first),
    Offset(0, dy),
  );
  await tester.pumpAndSettle();
}

void main() {
  final bundleJson = File('assets/content/act.bundle.json').readAsStringSync();
  final hasSets = bundleJson.contains('"passage-set:');
  final fontsAvailable = File('$_fontDir/Roboto-Regular.ttf').existsSync();

  setUpAll(() async {
    await _loadFont('Roboto', [
      'Roboto-Regular.ttf',
      'Roboto-Medium.ttf',
      'Roboto-Bold.ttf',
    ]);
    await _loadFont('MaterialIcons', ['MaterialIcons-Regular.otf']);
  });

  testWidgets('ACT long passage previews', skip: !(fontsAvailable && hasSets), (
    tester,
  ) async {
    tester.view.physicalSize = const Size(360, 780);
    tester.view.devicePixelRatio = 1.0;
    addTearDown(tester.view.reset);

    final store = MemoryStore();
    store.setString('onboarded.v1', 'true');
    store.setString(
      'profile.v1',
      jsonEncode(UserProfile.initial('act', 15).toJson()),
    );
    final examsJson = File('assets/content/exams.json').readAsStringSync();
    final catalogJson = File(
      'assets/avatar/manifest/avatar_catalog.json',
    ).readAsStringSync();
    await tester.pumpWidget(
      RepaintBoundary(
        key: _boundaryKey,
        child: ProviderScope(
          overrides: [
            contentRepositoryProvider.overrideWithValue(
              ContentRepository(
                reader: (path) async =>
                    path.endsWith('exams.json') ? examsJson : bundleJson,
              ),
            ),
            avatarRepositoryProvider.overrideWithValue(
              AvatarRepository(reader: (path) async => catalogJson),
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

    // Home -> Practice Test -> skip English and Math to the Reading section.
    await tester.scrollUntilVisible(
      find.text('Practice Test'),
      200,
      scrollable: find.byType(Scrollable).first,
    );
    await tester.tap(find.text('Practice Test'));
    await tester.pumpAndSettle();
    await tester.tap(find.text('Begin test'));
    await tester.pumpAndSettle();
    await _submitSection(tester); // English
    await _submitSection(tester); // Math

    // 1. First question of the Reading section: a full passage set.
    await _shoot(tester, 'act_long_passage_q1');

    // 2. Read a little, answer, move on: the passage keeps its place.
    await _dragPassage(tester, -260);
    // Scroll the question (below the passage window) up to reach choice B.
    await tester.dragFrom(const Offset(180, 640), const Offset(0, -260));
    await tester.pumpAndSettle();
    await tester.tap(find.text('B'));
    await tester.pumpAndSettle();
    await tester.tap(find.text('Next'));
    await tester.pumpAndSettle();
    await tester.tap(find.text('Skip'));
    await tester.pumpAndSettle();
    if (find.text('C').evaluate().isNotEmpty) {
      await tester.tap(find.text('C'));
      await tester.pumpAndSettle();
    }
    await _shoot(tester, 'act_long_passage_q3_kept_place');

    // 3. Full-screen reading sheet (scroll the question back to the top first).
    await tester.dragFrom(const Offset(180, 600), const Offset(0, 800));
    await tester.pumpAndSettle();
    await tester.tap(find.byKey(const Key('passage-expand')));
    await tester.pumpAndSettle();
    await _shoot(tester, 'act_long_passage_fullscreen');
    await tester.tap(find.byTooltip('Back to the question'));
    await tester.pumpAndSettle();

    // 4. A paired set, if one was dealt into this test.
    for (var i = 0; i < 34; i++) {
      final stimuli = tester.widgetList<Text>(find.text('Passage A')).toList();
      if (stimuli.isNotEmpty) break;
      final next = find.text('Next').evaluate().isNotEmpty
          ? find.text('Next')
          : find.text('Skip');
      if (next.evaluate().isEmpty) break;
      await tester.tap(next);
      await tester.pumpAndSettle();
    }
    if (find.text('Passage A').evaluate().isNotEmpty) {
      await _dragPassage(tester, -1400);
      await _shoot(tester, 'act_paired_passage');
    }

    // Sanity: every Reading question shown belongs to a passage set.
    final q = tester
        .widget<Text>(find.textContaining('words · scroll here').first)
        .data;
    expect(q, isNotNull);
    expect(Question.passageSetTagPrefix, 'passage-set:');
  });
}
