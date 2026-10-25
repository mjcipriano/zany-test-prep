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
import 'package:zany_test_prep/data/local/key_value_store.dart';
import 'package:zany_test_prep/domain/models/progress.dart';
import 'package:zany_test_prep/features/lessons/question_view.dart';

import '../helpers/adaptive_fixtures.dart';
import '../helpers/pump_app.dart';

// Phone-size previews of the placement check and "Recommended for you" card
// (360x780 logical, 3x) written to build/previews/:
//
//   flutter test --tags screenshots test/screenshots/adaptive_previews_test.dart

final _outDir = Directory('build/previews');
final _boundaryKey = GlobalKey();

/// The Flutter SDK's bundled Material fonts, found from the running tester
/// binary (…/flutter/bin/cache/…) or the repo's .tooling/ checkout.
String? _materialFontDir() {
  final candidates = <String>[
    '.tooling/flutter/bin/cache/artifacts/material_fonts',
  ];
  final exe = Platform.resolvedExecutable;
  final i = exe.indexOf('/bin/cache/');
  if (i > 0) {
    candidates.add('${exe.substring(0, i)}/bin/cache/artifacts/material_fonts');
  }
  for (final c in candidates) {
    if (File('$c/Roboto-Regular.ttf').existsSync()) return c;
  }
  return null;
}

Future<void> _loadFont(String family, List<String> paths) async {
  final loader = FontLoader(family);
  var added = 0;
  for (final p in paths) {
    final f = File(p);
    if (!f.existsSync()) continue;
    loader.addFont(
      Future.value(
        ByteData.view(Uint8List.fromList(f.readAsBytesSync()).buffer),
      ),
    );
    added++;
  }
  if (added > 0) await loader.load();
}

Future<void> _pump(WidgetTester tester, MemoryStore store) async {
  tester.view.physicalSize = const Size(360, 780);
  tester.view.devicePixelRatio = 1.0;
  addTearDown(() {
    tester.view.resetPhysicalSize();
    tester.view.resetDevicePixelRatio();
  });
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

Future<void> _tapText(WidgetTester tester, String text) async {
  await tester.tap(find.text(text));
  await tester.pumpAndSettle();
}

/// Answers the visible placement-check question (right or "Not sure").
Future<void> _answer(WidgetTester tester, {required bool right}) async {
  final view = tester.widget<QuestionView>(find.byType(QuestionView));
  final q = view.question;
  if (!right) return _tapText(tester, 'Not sure');
  if (q.type.isStudentProduced) {
    await tester.enterText(find.byType(TextField), q.answer!.accepted.first);
  } else {
    view.onSelectChoice(q.correctChoice!);
  }
  await tester.pump();
  final next = find.text('Next');
  await tester.tap(next.evaluate().isNotEmpty ? next : find.text('Finish'));
  await tester.pumpAndSettle();
}

Future<void> _takeCheck(WidgetTester tester, String prefix) async {
  // Right on 7 of 12, in a pattern that leaves every domain mixed.
  const pattern = [
    true,
    true,
    false,
    true,
    true,
    false,
    true,
    false,
    true,
    false,
    true,
    false,
  ];
  for (var i = 0; i < pattern.length; i++) {
    if (find.byType(QuestionView).evaluate().isEmpty) break;
    if (i == 1) await _shoot(tester, '${prefix}placement_question');
    await _answer(tester, right: pattern[i]);
  }
  await _shoot(tester, '${prefix}placement_results');
}

MemoryStore _seeded(AppProgress progress) {
  final store = MemoryStore();
  store.setString('onboarded.v1', 'true');
  store.setString(
    'profile.v1',
    jsonEncode({
      'examId': 'sat',
      'dailyGoalMinutes': 10,
      'createdAt': DateTime(2025).toIso8601String(),
    }),
  );
  store.setString('progress.v1', jsonEncode(progress.toJson()));
  return store;
}

void main() {
  final fonts = _materialFontDir();

  setUpAll(() async {
    if (fonts == null) return;
    await _loadFont('Roboto', [
      '$fonts/Roboto-Regular.ttf',
      '$fonts/Roboto-Medium.ttf',
      '$fonts/Roboto-Bold.ttf',
    ]);
    await _loadFont('MaterialIcons', ['$fonts/MaterialIcons-Regular.otf']);
    await _loadFont('NotoEmoji', [
      '.tooling/fonts/NotoEmoji-Regular.ttf',
      '/usr/share/fonts/truetype/noto/NotoColorEmoji.ttf',
    ]);
  });

  testWidgets(
    'SAT onboarding placement check + home card',
    skip: fonts == null,
    (tester) async {
      await _pump(tester, MemoryStore());
      await _tapText(tester, 'Continue');
      await _tapText(tester, 'Continue');
      await _tapText(tester, 'Continue');
      await _shoot(tester, '01_onboarding_goal_and_date');
      await _tapText(tester, 'Continue');
      await _shoot(tester, '02_onboarding_placement_intro');
      await _tapText(tester, 'Take the quick check');
      await _takeCheck(tester, '03_sat_'); // 03_sat_placement_question/results
      await _tapText(tester, 'Start learning');
      await _shoot(tester, '04_home_recommended');
      await tester.tap(find.byKey(const Key('recommended-card')));
      await tester.pumpAndSettle();
      await _shoot(tester, '05_smart_practice');
    },
  );

  testWidgets('ACT placement results', skip: fonts == null, (tester) async {
    await _pump(tester, MemoryStore());
    await _tapText(tester, 'Continue');
    await _tapText(tester, 'Continue');
    await _tapText(tester, 'ACT');
    await _tapText(tester, 'Continue');
    await _tapText(tester, 'Continue');
    await _tapText(tester, 'Take the quick check');
    await _takeCheck(tester, '06_act_');
    await _tapText(tester, 'Start learning');
    await _shoot(tester, '07_act_home_recommended');
  });

  testWidgets('home card with reviews due', skip: fonts == null, (
    tester,
  ) async {
    final sat = realBundle('sat');
    final progress = AppProgress(
      skillMastery: {
        'linear_equations': SkillMastery(
          skillId: 'linear_equations',
          mastery: 40,
          attempts: 8,
        ),
      },
    );
    for (final q in sat.questions.take(3)) {
      progress.reviewQueue.add(
        ReviewItem(questionId: q.id, skillId: q.skill, dueDay: '2020-01-01'),
      );
    }
    await _pump(tester, _seeded(progress));
    await _shoot(tester, '08_home_reviews_due');
  });
}
