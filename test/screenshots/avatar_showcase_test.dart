@Tags(['screenshots'])
library;

import 'dart:convert';
import 'dart:io';
import 'dart:ui' as ui;

import 'package:flutter/material.dart';
import 'package:flutter/rendering.dart';
import 'package:flutter/services.dart';
import 'package:flutter_test/flutter_test.dart';
import 'package:zany_test_prep/domain/models/avatar_catalog.dart';
import 'package:zany_test_prep/domain/models/progress.dart';
import 'package:zany_test_prep/domain/services/rewards_service.dart';
import 'package:zany_test_prep/features/rewards/avatar_view.dart';

// Generates the avatar-customization showcase images used in the README:
// a few avatars shown being upgraded step by step.
//
//   flutter test --tags screenshots test/screenshots/avatar_showcase_test.dart

final _outDir = Directory('docs/screenshots/avatars');
final AvatarCatalog _catalog = AvatarCatalog.fromJson(
  jsonDecode(
        File('assets/avatar/manifest/avatar_catalog.json').readAsStringSync(),
      )
      as Map<String, dynamic>,
);
const _rewards = RewardsService();
const _fontDir = '.tooling/flutter/bin/cache/artifacts/material_fonts';

GameState _loadout(String avatarId, Map<String, String> equipped) => GameState(
  selectedAvatarId: avatarId,
  ownedAssetIds: {avatarId, ...equipped.values},
  equipped: equipped,
);

Future<void> _loadFonts() async {
  Future<void> load(String family, List<String> files) async {
    final loader = FontLoader(family);
    var added = 0;
    for (final f in files) {
      final file = File('$_fontDir/$f');
      if (file.existsSync()) {
        loader.addFont(
          Future.value(ByteData.view(file.readAsBytesSync().buffer)),
        );
        added++;
      }
    }
    if (added > 0) await loader.load();
  }

  await load('Roboto', [
    'Roboto-Regular.ttf',
    'Roboto-Medium.ttf',
    'Roboto-Bold.ttf',
  ]);
}

/// Renders one labelled avatar preview tile to a PNG.
Future<void> _shoot(
  WidgetTester tester,
  String file,
  String label,
  GameState g,
) async {
  final layers = _rewards.equippedLayers(g, _catalog);
  final paths = <String>{for (final l in layers) l.asset.assetPath};
  final key = GlobalKey();
  tester.view.physicalSize = const Size(360, 420);
  tester.view.devicePixelRatio = 1.0;
  addTearDown(tester.view.resetPhysicalSize);

  await tester.pumpWidget(
    MediaQuery(
      data: const MediaQueryData(),
      child: Directionality(
        textDirection: TextDirection.ltr,
        child: RepaintBoundary(
          key: key,
          child: Container(
            width: 360,
            height: 420,
            color: const Color(0xFFF6F7FB),
            padding: const EdgeInsets.all(20),
            child: Column(
              mainAxisAlignment: MainAxisAlignment.center,
              children: [
                AvatarPreview(layers: layers, size: 300),
                const SizedBox(height: 16),
                Text(
                  label,
                  style: const TextStyle(
                    fontFamily: 'Roboto',
                    fontSize: 20,
                    fontWeight: FontWeight.w800,
                    color: Color(0xFF1A1C2A),
                  ),
                ),
              ],
            ),
          ),
        ),
      ),
    ),
  );
  await tester.pump();
  await tester.runAsync(() async {
    for (final p in paths) {
      await precacheImage(AssetImage(p), key.currentContext!);
    }
  });
  await tester.pumpAndSettle();
  await tester.runAsync(() async {
    final boundary =
        key.currentContext!.findRenderObject() as RenderRepaintBoundary;
    final image = await boundary.toImage(pixelRatio: 2.0);
    final bytes = await image.toByteData(format: ui.ImageByteFormat.png);
    _outDir.createSync(recursive: true);
    File(
      '${_outDir.path}/$file.png',
    ).writeAsBytesSync(bytes!.buffer.asUint8List());
    image.dispose();
  });
}

void main() {
  final fontsAvailable = File('$_fontDir/Roboto-Regular.ttf').existsSync();

  setUpAll(_loadFonts);

  testWidgets('avatar upgrade showcase', skip: !fontsAvailable, (tester) async {
    const nova = 'avatar_basic_001_nova_learner';
    const luna = 'avatar_basic_004_luna_logic';
    const sage = 'avatar_basic_003_sage_solver';

    // Nova: progressive build-up, one layer at a time.
    await _shoot(tester, '01_base', 'Starter avatar', _loadout(nova, {}));
    await _shoot(
      tester,
      '02_headwear',
      '+ Classic Cap',
      _loadout(nova, {'headwear': 'item_001_classic_cap'}),
    );
    await _shoot(
      tester,
      '03_eyewear',
      '+ Round Glasses',
      _loadout(nova, {
        'headwear': 'item_001_classic_cap',
        'eyewear': 'item_041_round_glasses',
      }),
    );
    await _shoot(
      tester,
      '04_badge_scarf',
      '+ Scarf & Badge',
      _loadout(nova, {
        'headwear': 'item_001_classic_cap',
        'eyewear': 'item_041_round_glasses',
        'neck_accessory': 'item_096_red_scarf',
        'chest_badge': 'item_121_starter_star_badge',
      }),
    );
    await _shoot(
      tester,
      '05_full_look',
      'Full look + pet',
      _loadout(nova, {
        'background_frame': 'item_201_neon_focus_ring',
        'back_or_aura': 'item_151_soft_aura',
        'headwear': 'item_001_classic_cap',
        'eyewear': 'item_041_round_glasses',
        'neck_accessory': 'item_096_red_scarf',
        'chest_badge': 'item_121_starter_star_badge',
        'side_left_1': 'pet_fox_study_cap_001',
      }),
    );

    // A couple of other avatars styled differently.
    await _shoot(
      tester,
      '06_luna',
      'Luna · aura + pet',
      _loadout(luna, {
        'back_or_aura': 'item_151_soft_aura',
        'eyewear': 'item_041_round_glasses',
        'side_right_1': 'pet_hoodie_cat_001',
      }),
    );
    await _shoot(
      tester,
      '07_sage',
      'Sage · cap + props',
      _loadout(sage, {
        'headwear': 'item_001_classic_cap',
        'side_left_1': 'pet_fox_study_cap_001',
        'side_right_1': 'item_176_pencil_wand',
      }),
    );
  });
}
