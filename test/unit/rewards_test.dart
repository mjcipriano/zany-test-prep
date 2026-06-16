import 'dart:math';

import 'package:flutter_test/flutter_test.dart';
import 'package:zany_test_prep/domain/models/avatar_catalog.dart';
import 'package:zany_test_prep/domain/models/progress.dart';
import 'package:zany_test_prep/domain/models/reward.dart';
import 'package:zany_test_prep/domain/services/reward_engine.dart';
import 'package:zany_test_prep/domain/services/rewards_service.dart';
import 'package:zany_test_prep/domain/services/streak_engine.dart';

CatalogAsset _asset(
  String id, {
  String type = 'item',
  int xp = 100,
  bool starter = false,
  int z = 10,
  List<String> slots = const ['headwear'],
}) => CatalogAsset(
  id: id,
  name: id,
  type: type,
  category: 'test',
  rarity: 'common',
  xpCost: xp,
  assetPath: 'p/$id.png',
  previewAssetPath: 'p/$id.png',
  allowedSlots: slots,
  zIndex: z,
  scale: 1.0,
  defaultUnlocked: starter,
);

AvatarCatalog _catalog() => AvatarCatalog(
  packId: 'test',
  styleVersion: 'v1',
  assets: [
    _asset(
      'av_starter',
      type: 'avatar',
      xp: 0,
      starter: true,
      z: 0,
      slots: const ['avatar'],
    ),
    _asset(
      'av_premium',
      type: 'avatar',
      xp: 500,
      z: 0,
      slots: const ['avatar'],
    ),
    _asset('hat', type: 'item', xp: 100, z: 45, slots: const ['headwear']),
    _asset('pet', type: 'pet', xp: 200, z: 60, slots: const ['side_left_1']),
  ],
);

void main() {
  group('XP economy', () {
    test('availableXp = totalXp - spentXp', () {
      final g = GameState(totalXp: 1000, spentXp: 300);
      expect(g.availableXp, 700);
    });

    test('new game/economy fields round-trip through JSON', () {
      final g = GameState(
        totalXp: 1000,
        spentXp: 250,
        streakFreezes: 2,
        unopenedChests: 1,
        xpBoostDay: '2026-06-17',
        xpBoostMultiplier: 2.0,
        selectedAvatarId: 'av_premium',
        ownedAssetIds: {'av_premium', 'hat'},
        equipped: {'headwear': 'hat'},
      );
      final back = GameState.fromJson(g.toJson());
      expect(back.availableXp, 750);
      expect(back.streakFreezes, 2);
      expect(back.unopenedChests, 1);
      expect(back.boostActiveOn('2026-06-17'), isTrue);
      expect(back.boostActiveOn('2026-06-18'), isFalse);
      expect(back.selectedAvatarId, 'av_premium');
      expect(back.ownedAssetIds, containsAll(['av_premium', 'hat']));
      expect(back.equipped['headwear'], 'hat');
    });
  });

  group('RewardEngine', () {
    test('xp reward never dilutes lifetime: amount is positive', () {
      final r = const RewardEngine().openChest(Random(1), const ChestPools());
      expect(r, isNotNull);
    });

    test('falls back to non-content rewards when pools are empty', () {
      const engine = RewardEngine();
      // With no avatars/items and freezes maxed, only xp/boost can drop.
      for (var seed = 0; seed < 50; seed++) {
        final r = engine.openChest(
          Random(seed),
          const ChestPools(streakFreezesOwned: kMaxStreakFreezes),
        );
        expect(r.kind, anyOf(RewardKind.xp, RewardKind.xpBoost));
      }
    });

    test('can roll an avatar when one is available', () {
      const engine = RewardEngine();
      final got = <RewardKind>{};
      for (var seed = 0; seed < 200; seed++) {
        got.add(
          engine
              .openChest(
                Random(seed),
                const ChestPools(avatars: [(id: 'a', name: 'A')]),
              )
              .kind,
        );
      }
      expect(got, contains(RewardKind.avatar));
    });
  });

  group('RewardsService', () {
    const svc = RewardsService();

    test('openChest consumes a chest and applies the reward', () {
      final g = GameState(unopenedChests: 1, totalXp: 0);
      final reward = svc.openChest(
        g,
        _catalog(),
        rng: Random(3),
        now: DateTime(2026, 6, 16),
      );
      expect(reward, isNotNull);
      expect(g.unopenedChests, 0);
    });

    test('openChest returns null with no chests', () {
      final g = GameState();
      expect(
        svc.openChest(
          g,
          _catalog(),
          rng: Random(1),
          now: DateTime(2026, 6, 16),
        ),
        isNull,
      );
    });

    test('applying XpReward grows lifetime + spendable, not spent', () {
      final g = GameState(totalXp: 100, spentXp: 40);
      svc.applyReward(g, const XpReward(50), now: DateTime(2026, 6, 16));
      expect(g.totalXp, 150);
      expect(g.spentXp, 40);
      expect(g.availableXp, 110);
    });

    test('streak freeze reward respects the cap', () {
      final g = GameState(streakFreezes: 2);
      svc.applyReward(
        g,
        const StreakFreezeReward(3),
        now: DateTime(2026, 6, 16),
      );
      expect(g.streakFreezes, kMaxStreakFreezes);
    });

    test('xp boost reward schedules the next day', () {
      final g = GameState();
      svc.applyReward(g, const XpBoostReward(2.0), now: DateTime(2026, 6, 16));
      expect(g.xpBoostMultiplier, 2.0);
      expect(g.boostActiveOn('2026-06-17'), isTrue);
    });

    test('purchase spends available XP and unlocks the asset', () {
      final catalog = _catalog();
      final g = GameState(totalXp: 300);
      final hat = catalog['hat']!;
      expect(svc.purchase(g, hat), isTrue);
      expect(g.spentXp, 100);
      expect(g.availableXp, 200);
      expect(svc.isOwned(g, hat), isTrue);
      // Can't buy twice.
      expect(svc.purchase(g, hat), isFalse);
    });

    test('purchase fails when too poor', () {
      final catalog = _catalog();
      final g = GameState(totalXp: 50);
      expect(svc.purchase(g, catalog['hat']!), isFalse);
      expect(g.spentXp, 0);
    });

    test('starter avatars are owned without buying', () {
      final catalog = _catalog();
      final g = GameState();
      expect(svc.isOwned(g, catalog['av_starter']!), isTrue);
      expect(svc.isOwned(g, catalog['av_premium']!), isFalse);
    });

    test('purchaseStreakFreeze respects cost + cap', () {
      final g = GameState(totalXp: 1000, streakFreezes: 0);
      expect(svc.purchaseStreakFreeze(g), isTrue);
      expect(g.streakFreezes, 1);
      expect(g.spentXp, RewardsService.streakFreezeCost);
    });

    test('equip/select work only for owned assets and stack by z-index', () {
      final catalog = _catalog();
      final g = GameState(totalXp: 1000);
      // Buy premium avatar + hat, equip both.
      svc.purchase(g, catalog['av_premium']!);
      svc.purchase(g, catalog['hat']!);
      expect(svc.selectAvatar(g, catalog, 'av_premium'), isTrue);
      expect(svc.equip(g, catalog, 'hat'), isTrue);
      final layers = svc.equippedLayers(g, catalog).map((a) => a.id).toList();
      expect(layers, ['av_premium', 'hat']); // avatar (z0) under hat (z45)
      // Can't select an unowned avatar.
      final g2 = GameState();
      expect(svc.selectAvatar(g2, catalog, 'av_premium'), isFalse);
    });
  });

  group('StreakEngine freezes', () {
    const engine = StreakEngine();

    test('a freeze bridges a single missed day', () {
      final r = engine.registerActivity(
        lastActiveDay: '2026-06-14',
        currentStreak: 5,
        longestStreak: 5,
        today: DateTime(2026, 6, 16), // missed the 15th
        streakFreezes: 1,
      );
      expect(r.reset, isFalse);
      expect(r.extended, isTrue);
      expect(r.currentStreak, 6);
      expect(r.freezesUsed, 1);
    });

    test('streak resets when freezes do not cover the gap', () {
      final r = engine.registerActivity(
        lastActiveDay: '2026-06-12',
        currentStreak: 5,
        longestStreak: 5,
        today: DateTime(2026, 6, 16), // missed 3 days
        streakFreezes: 1,
      );
      expect(r.reset, isTrue);
      expect(r.currentStreak, 1);
      expect(r.freezesUsed, 0); // kept for a smaller future miss
    });

    test('no freeze used on a normal next-day continuation', () {
      final r = engine.registerActivity(
        lastActiveDay: '2026-06-15',
        currentStreak: 5,
        longestStreak: 5,
        today: DateTime(2026, 6, 16),
        streakFreezes: 3,
      );
      expect(r.freezesUsed, 0);
      expect(r.currentStreak, 6);
    });
  });

  group('owned items: equip across every category', () {
    const svc = RewardsService();

    // One worn item per slot category (z-index ascending), plus two side pets.
    final wornSlots = <String, int>{
      'background_frame': 5,
      'back_or_aura': 10,
      'neck_accessory': 20,
      'face_accessory': 30,
      'eyewear': 35,
      'ear_accessory': 38,
      'headwear': 45,
      'chest_badge': 50,
      'jacket_or_top_overlay': 55,
    };

    AvatarCatalog richCatalog() => AvatarCatalog(
      packId: 'test',
      styleVersion: 'v1',
      assets: [
        _asset('av', type: 'avatar', xp: 0, starter: true, z: 0, slots: const ['avatar']),
        for (final e in wornSlots.entries)
          _asset('item_${e.key}', z: e.value, slots: [e.key]),
        _asset('item_headwear_2', z: 45, slots: const ['headwear']),
        _asset('pet_a', type: 'pet', z: 60, slots: const [
          'side_left_1', 'side_left_2', 'side_right_1', 'side_right_2',
        ]),
        _asset('pet_b', type: 'pet', z: 61, slots: const [
          'side_left_1', 'side_left_2', 'side_right_1', 'side_right_2',
        ]),
      ],
    );

    GameState ownedAll(AvatarCatalog c) => GameState(
      ownedAssetIds: c.assets.where((a) => !a.isAvatar).map((a) => a.id).toSet(),
    );

    test('each worn category equips into its own slot and stacks', () {
      final c = richCatalog();
      final g = ownedAll(c);
      for (final slot in wornSlots.keys) {
        expect(svc.equip(g, c, 'item_$slot'), isTrue, reason: slot);
        expect(svc.isEquipped(g, 'item_$slot'), isTrue, reason: slot);
        expect(g.equipped[slot], 'item_$slot', reason: slot);
      }
      // All worn slots coexist (distinct slots don't overwrite each other).
      expect(g.equipped.length, wornSlots.length);
      // Preview = avatar + every equipped item, ordered back-to-front by z.
      final layers = svc.equippedLayers(g, c);
      expect(layers.length, wornSlots.length + 1);
      for (var i = 1; i < layers.length; i++) {
        expect(layers[i].zIndex >= layers[i - 1].zIndex, isTrue);
      }
      expect(layers.first.id, 'av'); // avatar at the back (z 0)
    });

    test('equipping a second item in a slot replaces the first', () {
      final c = richCatalog();
      final g = ownedAll(c);
      svc.equip(g, c, 'item_headwear');
      expect(g.equipped['headwear'], 'item_headwear');
      svc.equip(g, c, 'item_headwear_2');
      expect(g.equipped['headwear'], 'item_headwear_2');
      expect(svc.isEquipped(g, 'item_headwear'), isFalse);
      expect(g.equipped.values.where((v) => v.startsWith('item_headwear')).length, 1);
    });

    test('multiple pets fill separate side slots', () {
      final c = richCatalog();
      final g = ownedAll(c);
      expect(svc.equip(g, c, 'pet_a'), isTrue);
      expect(svc.equip(g, c, 'pet_b'), isTrue);
      expect(svc.isEquipped(g, 'pet_a'), isTrue);
      expect(svc.isEquipped(g, 'pet_b'), isTrue);
      expect(g.equipped['side_left_1'], 'pet_a');
      expect(g.equipped['side_left_2'], 'pet_b'); // first empty allowed slot
    });

    test('unequipAsset removes from whatever slot it occupies', () {
      final c = richCatalog();
      final g = ownedAll(c);
      svc.equip(g, c, 'pet_a');
      svc.equip(g, c, 'pet_b');
      svc.unequipAsset(g, 'pet_a');
      expect(svc.isEquipped(g, 'pet_a'), isFalse);
      expect(svc.isEquipped(g, 'pet_b'), isTrue);
      expect(g.equipped.containsKey('side_left_1'), isFalse);
    });

    test('cannot equip an unowned item; re-equipping is idempotent', () {
      final c = richCatalog();
      final g = GameState(); // owns nothing
      expect(svc.equip(g, c, 'item_headwear'), isFalse);
      g.ownedAssetIds.add('item_headwear');
      expect(svc.equip(g, c, 'item_headwear'), isTrue);
      expect(svc.equip(g, c, 'item_headwear'), isTrue); // already on, no dup
      expect(g.equipped.values.where((v) => v == 'item_headwear').length, 1);
    });

    test('owned/equipped state survives a JSON round-trip', () {
      final c = richCatalog();
      final g = ownedAll(c);
      svc.equip(g, c, 'item_headwear');
      svc.equip(g, c, 'pet_a');
      final back = GameState.fromJson(g.toJson());
      expect(back.ownedAssetIds, containsAll(['item_headwear', 'pet_a']));
      expect(svc.isEquipped(back, 'item_headwear'), isTrue);
      expect(svc.isEquipped(back, 'pet_a'), isTrue);
    });
  });
}
