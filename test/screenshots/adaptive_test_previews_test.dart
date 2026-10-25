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
import 'package:zany_test_prep/design/theme.dart';
import 'package:zany_test_prep/domain/models/exam.dart';
import 'package:zany_test_prep/domain/services/scoring.dart';
import 'package:zany_test_prep/domain/services/timed_test.dart';
import 'package:zany_test_prep/features/test/test_result_views.dart';

import '../helpers/pump_app.dart';

// Phone-size previews (360x780 logical, 3x) of the adaptive practice test's
// intro, module transition, section break and results screens, written to
// build/previews/. Run locally:
//
//   flutter test --tags screenshots test/screenshots/adaptive_test_previews_test.dart

final _outDir = Directory('build/previews');
final _boundaryKey = GlobalKey();

String get _fontDir {
  const rel = '.tooling/flutter/bin/cache/artifacts/material_fonts';
  if (Directory(rel).existsSync()) return rel;
  // Worktrees share the main clone's Flutter SDK.
  final sdk = File(Platform.resolvedExecutable).parent.path;
  final fromSdk = '$sdk/../../artifacts/material_fonts';
  return Directory(fromSdk).existsSync()
      ? fromSdk
      : '/home/user/zany-test-prep/$rel';
}

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

void _phone(WidgetTester tester) {
  tester.view.physicalSize = const Size(360, 780);
  tester.view.devicePixelRatio = 1.0;
  addTearDown(() {
    tester.view.resetPhysicalSize();
    tester.view.resetDevicePixelRatio();
  });
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

Future<void> _pumpView(WidgetTester tester, Widget child) async {
  _phone(tester);
  await tester.pumpWidget(
    RepaintBoundary(
      key: _boundaryKey,
      child: MaterialApp(
        debugShowCheckedModeBanner: false,
        theme: AppTheme.light(),
        home: child,
      ),
    ),
  );
  await tester.pumpAndSettle();
}

const _names = {
  'reading_writing': 'Reading and Writing',
  'math': 'Math',
  'english': 'English',
  'reading': 'Reading',
  'science': 'Science',
};

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

  testWidgets('intro and module transition (real app)', skip: !fontsAvailable, (
    tester,
  ) async {
    final memory = MemoryStore();
    _phone(tester);
    await tester.pumpWidget(
      RepaintBoundary(
        key: _boundaryKey,
        child: ProviderScope(
          overrides: testOverrides(memory),
          child: const ZanyTestPrepApp(),
        ),
      ),
    );
    await tester.pump();
    await tester.pumpAndSettle();
    await onboardDefault(tester);
    final entry = find.text('Practice Test');
    await tester.scrollUntilVisible(
      entry,
      200,
      scrollable: find.byType(Scrollable).first,
    );
    await tester.tap(entry);
    await tester.pumpAndSettle();
    await _shoot(tester, 'adaptive_01_intro');

    await tester.tap(find.text('Begin test'));
    await tester.pumpAndSettle();
    await tester.tap(find.text('Review'));
    await tester.pumpAndSettle();
    await tester.tap(find.text('Submit section').last);
    await tester.pumpAndSettle();
    await tester.tap(find.text('Submit'));
    await tester.pumpAndSettle();
    await _shoot(tester, 'adaptive_02_module_transition');
  });

  testWidgets('section break', skip: !fontsAvailable, (tester) async {
    await _pumpView(
      tester,
      ModuleTransitionView(
        title: 'Section complete',
        note:
            'That section is done. On test day you get a 10-minute break '
            'here — stretch, breathe, then start when you are ready.',
        completed: 2,
        totalModules: 4,
        nextName: 'Math — Module 1',
        nextCount: 22,
        nextMinutes: 35,
        startLabel: 'Start next section',
        onStart: () {},
      ),
    );
    await _shoot(tester, 'adaptive_03_section_break');
  });

  testWidgets('results', skip: !fontsAvailable, (tester) async {
    const sat = ExamScoring(ScoringSpec(scale: ScoreScale.sat1600));
    SectionResult section(String d, int c, int t, SectionRoute r) =>
        SectionResult(
          domain: d,
          correct: c,
          total: t,
          route: r,
          score: sat.sectionScore(c, t, route: r),
        );
    final satSections = [
      section('reading_writing', 44, 54, SectionRoute.harder),
      section('math', 33, 44, SectionRoute.easier),
    ];
    await _pumpView(
      tester,
      TestResultsView(
        report: TimedTestReport(
          sections: satSections,
          composite: sat.composite({
            for (final s in satSections) s.domain: s.score,
          }),
        ),
        scoring: sat,
        compositeLabel: 'Estimated total score',
        adaptive: true,
        domainName: (d) => _names[d] ?? d,
        domainColor: (d) => AppTheme.domainColor(d == 'math' ? 1 : 0),
        onDone: () {},
      ),
    );
    await _shoot(tester, 'adaptive_04_results_sat');

    const act = ExamScoring(
      ScoringSpec(
        scale: ScoreScale.act36,
        compositeDomains: ['english', 'math', 'reading'],
      ),
    );
    final actSections = [
      for (final (d, c, t) in [
        ('english', 38, 50),
        ('math', 27, 45),
        ('reading', 25, 36),
        ('science', 24, 40),
      ])
        SectionResult(
          domain: d,
          correct: c,
          total: t,
          route: SectionRoute.linear,
          score: act.sectionScore(c, t),
        ),
    ];
    await _pumpView(
      tester,
      TestResultsView(
        report: TimedTestReport(
          sections: actSections,
          composite: act.composite({
            for (final s in actSections) s.domain: s.score,
          }),
        ),
        scoring: act,
        compositeLabel: 'Estimated composite score',
        adaptive: false,
        domainName: (d) => _names[d] ?? d,
        domainColor: (d) => AppTheme.domainColor(
          ['english', 'math', 'reading', 'science'].indexOf(d),
        ),
        onDone: () {},
      ),
    );
    await _shoot(tester, 'adaptive_05_results_act');
  });
}
