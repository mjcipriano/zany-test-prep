import 'dart:math';

import 'package:flutter_test/flutter_test.dart';
import 'package:zany_test_prep/domain/models/avatar_catalog.dart';
import 'package:zany_test_prep/domain/models/progress.dart';
import 'package:zany_test_prep/domain/models/reward.dart';
import 'package:zany_test_prep/domain/services/pet_engine.dart';
import 'package:zany_test_prep/domain/services/rewards_service.dart';

Map<String, dynamic> _pet(
  String id,
  int stage, {
  String? next,
  int req = 1,
}) => {
  'id': id,
  'name': 'Fox stage $stage',
  'type': 'pet',
  'category': 'rare',
  'slot_type': 'side',
  'allowed_slots': ['side_left_1', 'side_right_1'],
  'rarity': 'rare',
  'xp_cost': stage == 1 ? 900 : 0,
  'unlock_condition': stage == 1 ? 'spend_xp:900' : 'evolve:fox_001:level:$req',
  'asset_path': 'assets/avatar/pets/rare/$id.png',
  'z_index': 60,
  'placement': {
    'target': {'cx': 0.2, 'cy': 0.3, 'w': 0.28, 'h': 0.26},
  },
  'evolution': {
    'line_id': 'fox',
    'stage': stage,
    'stage_name': ['Base', 'Shiny', 'Radiant'][stage - 1],
    'base_id': 'fox_001',
    'next_id': next,
    'requires_level': req,
  },
};

AvatarCatalog _catalog() => AvatarCatalog.fromJson({
  'pack_id': 'test',
  'assets': [
    {
      'id': 'av1',
      'name': 'Nova',
      'type': 'avatar',
      'category': 'starter',
      'slot_type': 'base',
      'rarity': 'starter',
      'xp_cost': 0,
      'asset_path': 'a.png',
      'default_unlocked': true,
    },
    _pet('fox_001', 1, next: 'fox_002', req: 1),
    _pet('fox_002', 2, next: 'fox_003', req: 5),
    _pet('fox_003', 3, req: 10),
    {
      'id': 'owl_001',
      'name': 'Owl',
      'type': 'pet',
      'category': 'common',
      'slot_type': 'side',
      'allowed_slots': ['side_left_1', 'side_right_1'],
      'rarity': 'common',
      'xp_cost': 500,
      'asset_path': 'o.png',
    },
    {
      'id': 'hat',
      'name': 'Hat',
      'type': 'item',
      'category': 'headwear',
      'slot_type': 'worn',
      'allowed_slots': ['headwear'],
      'rarity': 'common',
      'xp_cost': 300,
      'asset_path': 'h.png',
    },
  ],
});

void main() {
  const engine = PetEngine();
  const rewards = RewardsService();

  group('PetEngine', () {
    test('levels follow the thresholds and cap at the max level', () {
      expect(engine.levelForXp(0), 1);
      expect(engine.levelForXp(39), 1);
      expect(engine.levelForXp(40), 2);
      expect(engine.levelForXp(280), 5);
      expect(engine.levelForXp(1080), 10);
      expect(engine.levelForXp(99999), PetEngine.maxLevel);
      for (var xp = 0; xp < 1200; xp++) {
        expect(
          engine.levelForXp(xp + 1),
          greaterThanOrEqualTo(engine.levelForXp(xp)),
        );
      }
    });

    test('progress within a level is 0..1 and full at max', () {
      expect(engine.xpIntoLevel(50), 10);
      expect(engine.xpForNextLevel(50), 60);
      expect(engine.progressInLevel(50), closeTo(10 / 60, 1e-9));
      expect(engine.progressInLevel(5000), 1);
      expect(engine.xpForNextLevel(5000), 0);
    });

    test('session XP rewards correctness and completion', () {
      expect(engine.xpForSession(correct: 0, total: 0), 0);
      expect(
        engine.xpForSession(correct: 10, total: 10),
        10 * PetEngine.xpPerCorrect + PetEngine.sessionBonus,
      );
      expect(
        engine.xpForSession(correct: 4, total: 10),
        4 * PetEngine.xpPerCorrect +
            6 * PetEngine.xpPerWrong +
            PetEngine.sessionBonus,
      );
    });
  });

  group('catalog evolution parsing', () {
    test('reads evolution fields and derives purchasability', () {
      final c = _catalog();
      final base = c['fox_001']!,
          shiny = c['fox_002']!,
          radiant = c['fox_003']!;
      expect(base.evolution!.stage, 1);
      expect(base.evolution!.nextId, 'fox_002');
      expect(shiny.evolution!.requiresLevel, 5);
      expect(radiant.evolution!.nextId, isNull);
      expect(base.isPurchasable, isTrue);
      expect(shiny.isPurchasable, isFalse);
      expect(radiant.isEvolvedStage, isTrue);
      expect(c.basePets.map((p) => p.id), ['fox_001', 'owl_001']);
      expect(c.evolutionLine('fox').map((p) => p.id), [
        'fox_001',
        'fox_002',
        'fox_003',
      ]);
      // A pet without evolution data is its own one-stage line.
      expect(c['owl_001']!.lineId, 'owl_001');
      expect(c['owl_001']!.isPurchasable, isTrue);
    });
  });

  group('RewardsService pets', () {
    test('equipped pets earn XP, unequipped ones do not', () {
      final c = _catalog();
      final g = GameState(ownedAssetIds: {'fox_001', 'owl_001'});
      expect(rewards.equip(g, c, 'fox_001'), isTrue);
      final ups = rewards.grantPetXp(g, c, 45);
      expect(g.petXp['fox'], 45);
      expect(g.petXp.containsKey('owl_001'), isFalse);
      expect(ups, {'fox': 2});
      expect(rewards.petLevel(g, c['fox_001']!), 2);
      expect(rewards.grantPetXp(g, c, 0), isEmpty);
    });

    test('evolves only when the level allows and swaps the equipped stage', () {
      final c = _catalog();
      final g = GameState(ownedAssetIds: {'fox_001'});
      rewards.equip(g, c, 'fox_001');
      expect(rewards.canEvolve(g, c, 'fox'), isFalse);
      expect(rewards.evolvePet(g, c, 'fox'), isNull);

      g.petXp['fox'] = PetEngine.thresholds[4]; // level 5
      expect(rewards.nextStage(g, c, 'fox')!.id, 'fox_002');
      expect(rewards.canEvolve(g, c, 'fox'), isTrue);
      final shiny = rewards.evolvePet(g, c, 'fox');
      expect(shiny!.id, 'fox_002');
      expect(g.ownedAssetIds, contains('fox_002'));
      expect(g.equipped.values, contains('fox_002'));
      expect(g.equipped.values, isNot(contains('fox_001')));
      expect(rewards.highestOwnedStage(g, c, 'fox')!.id, 'fox_002');

      // Needs level 10 for the final stage.
      expect(rewards.canEvolve(g, c, 'fox'), isFalse);
      g.petXp['fox'] = PetEngine.thresholds[9];
      expect(rewards.evolvePet(g, c, 'fox')!.id, 'fox_003');
      expect(rewards.nextStage(g, c, 'fox'), isNull);
      expect(rewards.evolvePet(g, c, 'fox'), isNull);
    });

    test('evolved stages cannot be bought and never drop from chests', () {
      final c = _catalog();
      final g = GameState(totalXp: 100000);
      expect(rewards.purchase(g, c['fox_002']!), isFalse);
      expect(rewards.purchase(g, c['fox_001']!), isTrue);
      // Open many chests: no evolved stage ever appears.
      final seen = <String>{};
      for (var i = 0; i < 400; i++) {
        final g2 = GameState(
          unopenedChests: 1,
          ownedAssetIds: {'fox_001', 'owl_001', 'hat'},
        );
        final r = rewards.openChest(g2, c, rng: Random(i), now: DateTime(2025));
        if (r is ItemReward) seen.add(r.assetId);
        if (r is AvatarReward) seen.add(r.assetId);
      }
      expect(seen, isNot(contains('fox_002')));
      expect(seen, isNot(contains('fox_003')));
    });

    test('pet XP survives a save/load round trip', () {
      final g = GameState(petXp: {'fox': 123});
      final back = GameState.fromJson(g.toJson());
      expect(back.petXp, {'fox': 123});
      final legacy = GameState.fromJson({'totalXp': 5});
      expect(legacy.petXp, isEmpty);
    });
  });
}
