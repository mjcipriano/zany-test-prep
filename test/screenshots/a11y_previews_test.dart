@Tags(['screenshots'])
library;

import 'dart:io';
import 'dart:ui' as ui;

import 'package:flutter/material.dart';
import 'package:flutter/rendering.dart';
import 'package:flutter_test/flutter_test.dart';

import '../helpers/a11y_harness.dart';

// Phone-size previews of the accessibility pass (360x780 logical at 3x) into
// build/previews/:
//
//   flutter test --tags screenshots test/screenshots/a11y_previews_test.dart

final _outDir = Directory('build/previews');
final _boundaryKey = GlobalKey();

Future<void> _shoot(WidgetTester tester, String name) async {
  await tester.pumpAndSettle();
  final providers = {
    for (final img in tester.widgetList<Image>(find.byType(Image))) img.image,
  };
  if (providers.isNotEmpty) {
    await tester.runAsync(() async {
      final ctx = _boundaryKey.currentContext!;
      for (final p in providers) {
        await precacheImage(p, ctx);
      }
    });
    await tester.pumpAndSettle();
  }
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

void main() {
  setUpAll(loadRealFonts);

  for (final scale in [1.0, 2.0]) {
    final tag = scale == 1.0 ? '1x' : '2x';

    testWidgets('home @$scale', skip: !kRealFontsAvailable, (tester) async {
      await pumpPhone(tester, textScale: scale, boundaryKey: _boundaryKey);
      await _shoot(tester, 'a11y_home_text$tag');
      if (scale == 2.0) {
        await tester.drag(find.byType(Scrollable).first, const Offset(0, -700));
        await _shoot(tester, 'a11y_home_text${tag}_scrolled');
      }
    });

    testWidgets('lesson @$scale', skip: !kRealFontsAvailable, (tester) async {
      await pumpPhone(tester, textScale: scale, boundaryKey: _boundaryKey);
      await openRoute(tester, '/lesson/${firstLessonId(tester)}');
      await startQuiz(tester);
      await scrollToChoices(tester);
      await tapChoiceA(tester);
      await _shoot(tester, 'a11y_lesson_question_text$tag');
      await tester.tap(find.text('Check'));
      await _shoot(tester, 'a11y_lesson_feedback_text$tag');
    });
  }

  testWidgets('home, dark theme', skip: !kRealFontsAvailable, (tester) async {
    await pumpPhone(
      tester,
      store: a11yStore(themeMode: ThemeMode.dark),
      boundaryKey: _boundaryKey,
    );
    await _shoot(tester, 'a11y_home_dark');
  });

  testWidgets('home overflow menu', skip: !kRealFontsAvailable, (tester) async {
    await pumpPhone(tester, boundaryKey: _boundaryKey);
    await tester.tap(find.byTooltip('More'));
    await _shoot(tester, 'a11y_home_more_menu');
  });

  testWidgets('store items @2.0', skip: !kRealFontsAvailable, (tester) async {
    await pumpPhone(tester, textScale: 2.0, boundaryKey: _boundaryKey);
    await openRoute(tester, '/store');
    await tester.tap(find.text('Items'));
    await _shoot(tester, 'a11y_store_items_text2x');
  });

  testWidgets('timed test navigator', skip: !kRealFontsAvailable, (
    tester,
  ) async {
    await pumpPhone(tester, boundaryKey: _boundaryKey);
    await beginTimedTest(tester);
    await _shoot(tester, 'a11y_timed_test');
    await tester.tap(find.text('Review'));
    await _shoot(tester, 'a11y_timed_test_navigator');
  });
}
