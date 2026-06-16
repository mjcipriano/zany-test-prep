import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';

import 'dart:math';

import '../data/local/key_value_store.dart';
import '../data/repositories/avatar_repository.dart';
import '../data/repositories/content_repository.dart';
import '../data/repositories/progress_repository.dart';
import '../domain/models/avatar_catalog.dart';
import '../domain/models/content_bundle.dart';
import '../domain/models/lesson.dart';
import '../domain/models/profile.dart';
import '../domain/models/progress.dart';
import '../domain/models/reward.dart';
import '../domain/services/badges.dart';
import '../domain/services/game_service.dart';
import '../domain/services/rewards_service.dart';

/// Immutable snapshot of the app session handed to the UI.
class AppData {
  const AppData({
    required this.bundle,
    required this.profile,
    required this.progress,
    required this.onboarded,
    required this.catalog,
    this.revision = 0,
  });

  final ContentBundle bundle;
  final UserProfile? profile;
  final AppProgress progress;
  final bool onboarded;
  final AvatarCatalog catalog;
  final int revision;

  AppData bump({
    UserProfile? profile,
    bool? onboarded,
    AppProgress? progress,
  }) => AppData(
    bundle: bundle,
    profile: profile ?? this.profile,
    progress: progress ?? this.progress,
    onboarded: onboarded ?? this.onboarded,
    catalog: catalog,
    revision: revision + 1,
  );
}

/// Outcome of a Survival run.
class SurvivalResult {
  const SurvivalResult({
    required this.streak,
    required this.best,
    required this.isRecord,
    required this.newBadges,
  });

  final int streak;
  final int best;
  final bool isRecord;
  final List<BadgeDef> newBadges;
}

/// Provides the content repository (overridable in tests).
final contentRepositoryProvider = Provider<ContentRepository>(
  (ref) => ContentRepository(),
);

/// Overridable factory for the local key/value store (tests inject MemoryStore).
final keyValueStoreProvider = FutureProvider<KeyValueStore>((ref) async {
  return PrefsStore.create();
});

final gameServiceProvider = Provider<GameService>((ref) => const GameService());

/// Provides the avatar catalog repository (overridable in tests).
final avatarRepositoryProvider = Provider<AvatarRepository>(
  (ref) => AvatarRepository(),
);

final rewardsServiceProvider = Provider<RewardsService>(
  (ref) => const RewardsService(),
);

/// Root controller: loads content + persisted state and applies mutations.
class AppController extends AsyncNotifier<AppData> {
  late ProgressRepository _repo;
  late GameService _game;
  late RewardsService _rewards;

  @override
  Future<AppData> build() async {
    final store = await ref.watch(keyValueStoreProvider.future);
    _repo = ProgressRepository(store);
    _game = ref.read(gameServiceProvider);
    _rewards = ref.read(rewardsServiceProvider);
    final content = ref.read(contentRepositoryProvider);
    final avatars = ref.read(avatarRepositoryProvider);

    final profile = _repo.loadProfile();
    final examId = profile?.examId ?? 'sat';
    final bundle = await content.loadBundle(examId);
    final catalog = await avatars.loadCatalog();
    return AppData(
      bundle: bundle,
      profile: profile,
      progress: _repo.loadProgress(),
      onboarded: _repo.isOnboarded,
      catalog: catalog,
    );
  }

  AppData get _data => state.requireValue;

  /// Creates the local profile at the end of onboarding.
  Future<void> completeOnboarding({
    required String examId,
    required int dailyGoalMinutes,
    DateTime? targetTestDate,
  }) async {
    final profile = UserProfile.initial(
      examId,
      dailyGoalMinutes,
    ).copyWith(targetTestDate: targetTestDate);
    await _repo.saveProfile(profile);
    await _repo.setOnboarded(true);
    state = AsyncData(_data.bump(profile: profile, onboarded: true));
  }

  /// Applies a finished lesson attempt; persists and returns the outcome.
  Future<LessonOutcome> completeLesson({
    required Lesson lesson,
    required List<AnswerResult> results,
  }) async {
    final data = _data;
    final outcome = _game.applyLessonResult(
      progress: data.progress,
      profile: data.profile!,
      lesson: lesson,
      results: results,
      bundle: data.bundle,
    );
    await _repo.saveProgress(data.progress);
    state = AsyncData(data.bump());
    return outcome;
  }

  /// Applies a finished review session (updates XP/mastery/review, not lessons).
  Future<LessonOutcome> completeReview({
    required List<AnswerResult> results,
  }) async {
    final data = _data;
    final outcome = _game.applyPracticeResult(
      progress: data.progress,
      profile: data.profile!,
      results: results,
      bundle: data.bundle,
    );
    await _repo.saveProgress(data.progress);
    state = AsyncData(data.bump());
    return outcome;
  }

  /// Applies a finished Survival run: per-question XP/mastery/review plus the
  /// best-streak record. [streak] is the number answered correctly before a miss.
  Future<SurvivalResult> completeSurvival({
    required List<AnswerResult> results,
    required int streak,
  }) async {
    final data = _data;
    if (results.isNotEmpty) {
      _game.applyPracticeResult(
        progress: data.progress,
        profile: data.profile!,
        results: results,
        bundle: data.bundle,
      );
    }
    final g = data.progress.game;
    final isRecord = streak > g.survivalBest;
    if (isRecord) g.survivalBest = streak;
    // Re-evaluate badges now that survivalBest is updated (catches survival badges).
    final newBadges = Badges.evaluateAndGrant(
      data.progress,
      data.bundle,
    ).map(Badges.byId).whereType<BadgeDef>().toList();
    await _repo.saveProgress(data.progress);
    state = AsyncData(data.bump());
    return SurvivalResult(
      streak: streak,
      best: g.survivalBest,
      isRecord: isRecord,
      newBadges: newBadges,
    );
  }

  /// Seeds per-skill mastery from a diagnostic and marks it done.
  Future<void> applyDiagnostic({required List<AnswerResult> results}) async {
    final data = _data;
    for (final r in results) {
      data.progress.mastery(r.question.skill).mastery = r.correct ? 60 : 25;
    }
    data.progress.game.diagnosticDone = true;
    await _repo.saveProgress(data.progress);
    state = AsyncData(data.bump());
  }

  /// Marks the diagnostic as dismissed without taking it.
  Future<void> skipDiagnostic() async {
    final data = _data;
    data.progress.game.diagnosticDone = true;
    await _repo.saveProgress(data.progress);
    state = AsyncData(data.bump());
  }

  Future<void> updateProfile(UserProfile profile) async {
    await _repo.saveProfile(profile);
    state = AsyncData(_data.bump(profile: profile));
  }

  Future<void> setDailyGoal(int minutes) =>
      updateProfile(_data.profile!.copyWith(dailyGoalMinutes: minutes));

  Future<void> setThemeMode(ThemeMode mode) =>
      updateProfile(_data.profile!.copyWith(themeMode: mode));

  Future<void> setSound(bool on) =>
      updateProfile(_data.profile!.copyWith(soundOn: on));

  Future<void> setHaptics(bool on) =>
      updateProfile(_data.profile!.copyWith(hapticsOn: on));

  Future<void> setTargetDate(DateTime? date) => updateProfile(
    _data.profile!.copyWith(
      targetTestDate: date,
      clearTargetDate: date == null,
    ),
  );

  /// Wipes all local progress and profile (Settings -> Reset Progress).
  Future<void> resetProgress() async {
    await _repo.resetAll();
    state = AsyncData(
      AppData(
        bundle: _data.bundle,
        profile: null,
        progress: AppProgress(),
        onboarded: false,
        catalog: _data.catalog,
        revision: _data.revision + 1,
      ),
    );
  }

  // --- Rewards ---

  /// Opens one banked chest, applies its reward, persists, and returns it.
  /// Returns null when there are no chests to open.
  Future<Reward?> openChest() async {
    final data = _data;
    final reward = _rewards.openChest(
      data.progress.game,
      data.catalog,
      rng: Random(),
      now: DateTime.now(),
    );
    if (reward == null) return null;
    await _repo.saveProgress(data.progress);
    state = AsyncData(data.bump());
    return reward;
  }

  /// Buys a catalog asset (avatar/item/pet) with spendable XP. Returns success.
  Future<bool> purchaseAsset(String assetId) async {
    final data = _data;
    final asset = data.catalog[assetId];
    if (asset == null) return false;
    final ok = _rewards.purchase(data.progress.game, asset);
    if (ok) {
      await _repo.saveProgress(data.progress);
      state = AsyncData(data.bump());
    }
    return ok;
  }

  /// Buys a streak freeze with spendable XP (capped at the max banked).
  Future<bool> purchaseStreakFreeze() async {
    final data = _data;
    final ok = _rewards.purchaseStreakFreeze(data.progress.game);
    if (ok) {
      await _repo.saveProgress(data.progress);
      state = AsyncData(data.bump());
    }
    return ok;
  }

  /// Selects an owned avatar as the active one.
  Future<bool> selectAvatar(String avatarId) async {
    final data = _data;
    final ok = _rewards.selectAvatar(
      data.progress.game,
      data.catalog,
      avatarId,
    );
    if (ok) {
      await _repo.saveProgress(data.progress);
      state = AsyncData(data.bump());
    }
    return ok;
  }

  /// Equips an owned item/pet into its slot.
  Future<bool> equipItem(String assetId) async {
    final data = _data;
    final ok = _rewards.equip(data.progress.game, data.catalog, assetId);
    if (ok) {
      await _repo.saveProgress(data.progress);
      state = AsyncData(data.bump());
    }
    return ok;
  }

  /// Removes whatever item occupies [slot].
  Future<void> unequipSlot(String slot) async {
    final data = _data;
    _rewards.unequip(data.progress.game, slot);
    await _repo.saveProgress(data.progress);
    state = AsyncData(data.bump());
  }
}

final appControllerProvider = AsyncNotifierProvider<AppController, AppData>(
  AppController.new,
);
