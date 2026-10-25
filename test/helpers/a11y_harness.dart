import 'dart:convert';
import 'dart:io';

import 'package:flutter/material.dart';
import 'package:flutter/services.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:flutter_test/flutter_test.dart';
import 'package:go_router/go_router.dart';
import 'package:zany_test_prep/app/app.dart';
import 'package:zany_test_prep/app/app_controller.dart';
import 'package:zany_test_prep/app/router.dart';
import 'package:zany_test_prep/data/local/key_value_store.dart';
import 'package:zany_test_prep/domain/models/profile.dart';
import 'package:zany_test_prep/domain/models/progress.dart';

import 'pump_app.dart';

// Shared setup for the accessibility suite (test/a11y/): a phone-size
// viewport, a text scale, and a returning player with enough state that every
// screen shows its full furniture (streak, chests, owned/equipped items, a
// companion, a review badge).

/// Real catalog ids (assets/avatar/manifest/avatar_catalog.json).
const kA11yGlasses = 'item_041_round_glasses'; // "Round Glasses" (eyewear)
const kA11yMask = 'item_071_simple_mask'; // "Simple Mask"
const kA11yStuds = 'item_249_silver_studs'; // "Silver Studs"
const kA11yPet = 'pet_fox_study_cap_001'; // "Study Cap Fox"

/// The text scales the app must stay usable at (Android "Font size" steps).
const kA11yTextScales = [1.0, 1.3, 1.6, 2.0];

/// A store for an onboarded SAT player mid-way through their journey.
/// [diagnosticDone] hides the Home "Personalize your plan" card.
MemoryStore a11yStore({
  bool diagnosticDone = false,
  ThemeMode themeMode = ThemeMode.light,
  bool equipped = true,
}) {
  final store = MemoryStore();
  store.setString('onboarded.v1', 'true');
  store.setString(
    'profile.v1',
    jsonEncode(
      UserProfile.initial('sat', 10).copyWith(themeMode: themeMode).toJson(),
    ),
  );
  final progress = AppProgress();
  final today = dayKey(DateTime.now());
  progress.game
    ..totalXp = 5240
    ..spentXp = 400
    ..currentStreak = 12
    ..longestStreak = 15
    ..lastActiveDay = today
    ..dailyXp = 40
    ..dailyDay = today
    ..survivalBest = 7
    ..unopenedChests = 2
    ..streakFreezes = 1
    ..ownedAssetIds.addAll({kA11yGlasses, kA11yMask, kA11yStuds, kA11yPet})
    ..petXp['pet_fox_study_cap'] = 120;
  if (equipped) {
    progress.game.equipped
      ..['eyewear'] = kA11yGlasses
      ..['side_right_1'] = kA11yPet;
  }
  if (diagnosticDone) progress.game.diagnosticDoneExams.add('sat');
  store.setString('progress.v1', jsonEncode(progress.toJson()));
  return store;
}

/// A fresh install (onboarding not done yet).
MemoryStore a11yOnboardingStore() => MemoryStore();

/// Pumps the whole app on a 360x780 phone at [textScale].
Future<void> pumpPhone(
  WidgetTester tester, {
  MemoryStore? store,
  double textScale = 1.0,
  Key? boundaryKey,
}) async {
  tester.view.physicalSize = const Size(360, 780);
  tester.view.devicePixelRatio = 1.0;
  tester.platformDispatcher.textScaleFactorTestValue = textScale;
  addTearDown(() {
    tester.view.reset();
    tester.platformDispatcher.clearTextScaleFactorTestValue();
  });
  Widget app = ProviderScope(
    overrides: testOverrides(store ?? a11yStore()),
    child: const ZanyTestPrepApp(),
  );
  if (boundaryKey != null) app = RepaintBoundary(key: boundaryKey, child: app);
  await tester.pumpWidget(app);
  await tester.pump();
  await tester.pumpAndSettle();
}

/// The app's router, for jumping straight to a screen.
GoRouter appRouter(WidgetTester tester) => ProviderScope.containerOf(
  tester.element(find.byType(MaterialApp)),
).read(routerProvider);

/// Pushes [location] and waits for it to settle.
Future<void> openRoute(WidgetTester tester, String location) async {
  appRouter(tester).push(location);
  await tester.pumpAndSettle();
}

/// The id of the first lesson on the active exam's first path (unlocked
/// from the start).
String firstLessonId(WidgetTester tester) {
  final bundle = ProviderScope.containerOf(
    tester.element(find.byType(MaterialApp)),
  ).read(appControllerProvider).requireValue.bundle;
  return bundle.lessonsForDomain(bundle.domainIds.first).first.id;
}

/// From the lesson's teaching card, pages through to the first question.
Future<void> startQuiz(WidgetTester tester) async {
  for (var i = 0; i < 8 && find.text('Next').evaluate().isNotEmpty; i++) {
    await tester.tap(find.text('Next'));
    await tester.pumpAndSettle();
  }
  if (find.text('Start').evaluate().isNotEmpty) {
    await tester.tap(find.text('Start'));
    await tester.pumpAndSettle();
  }
}

/// Scrolls every vertical scrollable on screen to its end and back, so
/// lazily built rows are laid out (and any overflow in them is reported).
Future<void> scrollThrough(WidgetTester tester) async {
  final states = tester
      .stateList<ScrollableState>(find.byType(Scrollable))
      .toList();
  for (final s in states) {
    if (!s.mounted || s.position.axis != Axis.vertical) continue;
    final max = s.position.maxScrollExtent;
    for (var y = 0.0; y <= max; y += 300) {
      s.position.jumpTo(y);
      await tester.pump();
    }
    if (s.mounted) s.position.jumpTo(0);
    await tester.pump();
  }
}

/// Scrolls the question until choice "A" is on screen and taps it. Returns
/// false when the question has no choices (a grid-in).
Future<bool> tapChoiceA(WidgetTester tester) async {
  if (find.byType(TextField).evaluate().isNotEmpty) return false;
  final scrollable = find.byType(Scrollable).first;
  for (
    var i = 0;
    i < 40 && find.text('A').hitTestable().evaluate().isEmpty;
    i++
  ) {
    await tester.drag(scrollable, const Offset(0, -150));
    await tester.pumpAndSettle();
  }
  await tester.tap(find.text('A').hitTestable().first);
  await tester.pumpAndSettle();
  return true;
}

/// Answers the visible lesson question (choice A, or "1" for a grid-in) and
/// taps Check.
Future<void> answerAndCheck(WidgetTester tester) async {
  if (!await tapChoiceA(tester)) {
    await tester.enterText(find.byType(TextField).first, '1');
    await tester.pump();
  }
  await tester.tap(find.text('Check'));
  await tester.pumpAndSettle();
}

/// Opens the practice test and begins its first module.
Future<void> beginTimedTest(WidgetTester tester) async {
  await openRoute(tester, '/test');
  await tester.scrollUntilVisible(
    find.text('Begin test'),
    200,
    scrollable: find.byType(Scrollable).first,
  );
  await tester.tap(find.text('Begin test'));
  await tester.pumpAndSettle();
}

String get _fontDir {
  final root = Platform.environment['FLUTTER_ROOT'];
  final fromRoot = '$root/bin/cache/artifacts/material_fonts';
  return root != null && Directory(fromRoot).existsSync()
      ? fromRoot
      : '.tooling/flutter/bin/cache/artifacts/material_fonts';
}

/// Whether the real Roboto/Material Icons fonts ship with this Flutter SDK
/// (they do with every standard install; text-scale tests skip otherwise).
bool get kRealFontsAvailable =>
    File('$_fontDir/Roboto-Regular.ttf').existsSync();

/// Loads Roboto and Material Icons so text measures like on a phone. The
/// default test font draws every glyph a full em wide (about twice Roboto's
/// width), which would make every text-scale check wildly pessimistic.
Future<void> loadRealFonts() async {
  Future<void> load(String family, List<String> files) async {
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

  await load('Roboto', [
    'Roboto-Regular.ttf',
    'Roboto-Medium.ttf',
    'Roboto-Bold.ttf',
    'Roboto-Black.ttf',
  ]);
  await load('MaterialIcons', ['MaterialIcons-Regular.otf']);
}
