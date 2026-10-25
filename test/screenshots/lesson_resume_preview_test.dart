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

import '../helpers/pump_app.dart';

// Phone-size (360x780 @3x) previews of the lesson-resume UI: the leave
// dialog, the in-progress marker on the home path, and the resume prompt.
//
//   flutter test --tags screenshots test/screenshots/lesson_resume_preview_test.dart
//
// Writes PNGs to build/previews/. A generator, not an assertion test.

final _outDir = Directory('build/previews');
final _boundaryKey = GlobalKey();

String get _fontDir {
  final root = Platform.environment['FLUTTER_ROOT'];
  const rel = 'bin/cache/artifacts/material_fonts';
  if (root != null && Directory('$root/$rel').existsSync()) {
    return '$root/$rel';
  }
  return '.tooling/flutter/$rel';
}

Future<void> _loadFont(String family, List<String> files) async {
  final loader = FontLoader(family);
  for (final f in files) {
    final file = File('$_fontDir/$f');
    if (!file.existsSync()) continue;
    loader.addFont(Future.value(ByteData.sublistView(file.readAsBytesSync())));
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

Future<void> _pump(WidgetTester tester, MemoryStore store) async {
  tester.view.physicalSize = const Size(360, 780);
  tester.view.devicePixelRatio = 1.0;
  addTearDown(tester.view.reset);
  await tester.pumpWidget(const SizedBox.shrink());
  await tester.pumpWidget(
    RepaintBoundary(
      key: _boundaryKey,
      child: ProviderScope(
        overrides: testOverrides(store),
        child: const ZanyTestPrepApp(),
      ),
    ),
  );
  await tester.pump();
  await tester.pumpAndSettle();
}

Future<void> _answerAndContinue(WidgetTester tester) async {
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
  await tester.tap(find.text('Check'));
  await tester.pumpAndSettle();
  await tester.tap(find.text('Continue'));
  await tester.pumpAndSettle();
}

void main() {
  final fontsAvailable = File('$_fontDir/Roboto-Regular.ttf').existsSync();

  setUpAll(() async {
    await _loadFont('Roboto', [
      'Roboto-Regular.ttf',
      'Roboto-Medium.ttf',
      'Roboto-Bold.ttf',
    ]);
    await _loadFont('MaterialIcons', ['MaterialIcons-Regular.otf']);
  });

  testWidgets('lesson resume previews', skip: !fontsAvailable, (tester) async {
    final store = MemoryStore();
    await _pump(tester, store);
    await onboardDefault(tester);

    // Into the first lesson, past the mini-lesson, answer six questions.
    await tester.tap(find.textContaining('Main Idea').first);
    await tester.pumpAndSettle();
    for (var i = 0; i < 6 && find.text('Next').evaluate().isNotEmpty; i++) {
      await tester.tap(find.text('Next'));
      await tester.pumpAndSettle();
    }
    await tester.tap(find.text('Start'));
    await tester.pumpAndSettle();
    for (var i = 0; i < 6; i++) {
      await _answerAndContinue(tester);
    }

    // 1. The leave dialog now says progress is saved.
    await tester.tap(find.byIcon(Icons.close_rounded));
    await tester.pumpAndSettle();
    await _shoot(tester, 'resume_01_leave_dialog');
    await tester.tap(find.text('Leave'));
    await tester.pumpAndSettle();

    // 2. Home path: the lesson shows an in-progress marker.
    final marker = find.textContaining('In progress ·');
    await tester.scrollUntilVisible(
      marker,
      200,
      scrollable: find.byType(Scrollable).first,
    );
    await tester.drag(find.byType(Scrollable).first, const Offset(0, 150));
    await _shoot(tester, 'resume_02_home_in_progress');

    // 3. Re-entering offers Resume / Start over.
    await tester.tap(find.textContaining('Main Idea').first);
    await tester.pumpAndSettle();
    await _shoot(tester, 'resume_03_prompt');

    // 4. Resumed straight onto question 7.
    await tester.tap(find.textContaining('Resume (question'));
    await tester.pumpAndSettle();
    await _shoot(tester, 'resume_04_resumed_question');
  });
}
