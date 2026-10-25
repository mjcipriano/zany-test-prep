import 'dart:async';
import 'dart:math';

import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';

import '../core/notifications/reminder_scheduler.dart';
import '../data/local/key_value_store.dart';
import '../data/repositories/avatar_repository.dart';
import '../data/repositories/content_repository.dart';
import '../data/repositories/progress_repository.dart';
import '../domain/models/avatar_catalog.dart';
import '../domain/models/backup.dart';
import '../domain/models/content_bundle.dart';
import '../domain/models/exam.dart';
import '../domain/models/lesson.dart';
import '../domain/models/profile.dart';
import '../domain/models/progress.dart';
import '../domain/models/reminder_settings.dart';
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
    this.exams = const [],
    this.revision = 0,
  });

  final ContentBundle bundle;
  final UserProfile? profile;
  final AppProgress progress;
  final bool onboarded;
  final AvatarCatalog catalog;

  /// Every exam the app ships content for (SAT, ACT, …), for the exam picker.
  final List<ExamInfo> exams;
  final int revision;

  AppData bump({
    UserProfile? profile,
    bool? onboarded,
    AppProgress? progress,
    ContentBundle? bundle,
  }) => AppData(
    bundle: bundle ?? this.bundle,
    profile: profile ?? this.profile,
    progress: progress ?? this.progress,
    onboarded: onboarded ?? this.onboarded,
    catalog: catalog,
    exams: exams,
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

/// The exam loaded when no profile exists yet (first launch).
const String kDefaultExamId = 'sat';

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
    final exams = await _loadExams(content);
    // Fall back to the first shipped exam if the stored exam no longer exists.
    final wanted = profile?.examId ?? kDefaultExamId;
    final examId = exams.any((e) => e.id == wanted)
        ? wanted
        : (exams.isEmpty ? wanted : exams.first.id);
    final bundle = await content.loadBundle(examId);
    final catalog = await avatars.loadCatalog();
    final data = AppData(
      bundle: bundle,
      profile: profile,
      progress: _repo.loadProgress(),
      // A missing/corrupt profile means onboarding again, whatever the flag
      // says; Home cannot render without a profile.
      onboarded: _repo.isOnboarded && profile != null,
      catalog: catalog,
      exams: exams,
    );
    // App start: re-plan reminders (today's copy, streak, a new day).
    _syncReminders(data);
    return data;
  }

  /// Re-plans local reminders in the background (cancel + reschedule). Called
  /// on app start, when settings change and after every finished session, so
  /// meeting today's goal cancels today's streak nudge.
  void _syncReminders(AppData data) {
    unawaited(
      ref
          .read(reminderSchedulerProvider)
          .sync(
            profile: data.onboarded ? data.profile : null,
            game: data.progress.game,
          ),
    );
  }

  /// Sets [state] and re-plans reminders against it.
  void _emitAndSync(AppData data) {
    state = AsyncData(data);
    _syncReminders(data);
  }

  AppData get _data => state.requireValue;

  /// Reads exams.json; a missing/corrupt file degrades to the default exam so
  /// the app still boots.
  Future<List<ExamInfo>> _loadExams(ContentRepository content) async {
    try {
      final exams = await content.enabledExams();
      if (exams.isNotEmpty) return exams;
    } catch (_) {
      // fall through
    }
    return const [
      ExamInfo(id: kDefaultExamId, name: 'SAT', displayName: 'Digital SAT'),
    ];
  }

  /// Switches the active exam (e.g. SAT -> ACT): loads that exam's bundle and
  /// updates the profile. Progress is kept — lesson/question ids are
  /// exam-prefixed, so each exam's path keeps its own completion state while
  /// XP, streaks, and rewards carry across.
  Future<void> switchExam(String examId) async {
    final data = _data;
    if (data.bundle.exam.id == examId) return;
    final bundle = await ref.read(contentRepositoryProvider).loadBundle(examId);
    final profile = data.profile?.copyWith(examId: examId);
    if (profile != null) await _repo.saveProfile(profile);
    state = AsyncData(data.bump(bundle: bundle, profile: profile));
  }

  /// Creates the local profile at the end of onboarding and loads the chosen
  /// exam's content if it differs from the bundle loaded at boot.
  Future<void> completeOnboarding({
    required String examId,
    required int dailyGoalMinutes,
    DateTime? targetTestDate,
    ReminderSettings reminders = const ReminderSettings(),
  }) async {
    final data = _data;
    final profile = UserProfile.initial(
      examId,
      dailyGoalMinutes,
    ).copyWith(targetTestDate: targetTestDate, reminders: reminders);
    final bundle = data.bundle.exam.id == examId
        ? data.bundle
        : await ref.read(contentRepositoryProvider).loadBundle(examId);
    await _repo.saveProfile(profile);
    await _repo.setOnboarded(true);
    _emitAndSync(data.bump(profile: profile, onboarded: true, bundle: bundle));
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
      catalog: data.catalog,
    );
    await _repo.saveProgress(data.progress);
    _emitAndSync(data.bump());
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
      catalog: data.catalog,
    );
    await _repo.saveProgress(data.progress);
    _emitAndSync(data.bump());
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
        catalog: data.catalog,
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
    _emitAndSync(data.bump());
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
      data.progress.mastery(masteryKeyFor(r.question)).mastery = r.correct
          ? 60
          : 25;
    }
    data.progress.game.markDiagnosticDone(data.bundle.exam.id);
    await _repo.saveProgress(data.progress);
    state = AsyncData(data.bump());
  }

  /// Marks the diagnostic as dismissed without taking it.
  Future<void> skipDiagnostic() async {
    final data = _data;
    data.progress.game.markDiagnosticDone(data.bundle.exam.id);
    await _repo.saveProgress(data.progress);
    state = AsyncData(data.bump());
  }

  Future<void> updateProfile(UserProfile profile) async {
    await _repo.saveProfile(profile);
    // Any setting can matter to reminders (the daily goal changes whether
    // today's goal is met), so re-plan on every profile change.
    _emitAndSync(_data.bump(profile: profile));
  }

  /// Saves reminder preferences and reschedules. The caller has already
  /// obtained the notification permission when turning reminders on.
  Future<void> setReminders(ReminderSettings reminders) =>
      updateProfile(_data.profile!.copyWith(reminders: reminders));

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
    _emitAndSync(
      AppData(
        bundle: _data.bundle,
        profile: null,
        progress: AppProgress(),
        onboarded: false,
        catalog: _data.catalog,
        exams: _data.exams,
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
    // A chest can grant XP, which may cross a level/badge threshold.
    Badges.evaluateAndGrant(data.progress, data.bundle);
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

  /// Removes [assetId] from wherever it's equipped.
  Future<void> unequipAsset(String assetId) async {
    final data = _data;
    _rewards.unequipAsset(data.progress.game, assetId);
    await _repo.saveProgress(data.progress);
    state = AsyncData(data.bump());
  }

  /// Evolves a pet line into its next stage once its level allows. Returns the
  /// new stage, or null when it cannot evolve yet.
  Future<CatalogAsset?> evolvePet(String lineId) async {
    final data = _data;
    final next = _rewards.evolvePet(data.progress.game, data.catalog, lineId);
    if (next == null) return null;
    await _repo.saveProgress(data.progress);
    state = AsyncData(data.bump());
    return next;
  }

  /// Moves an equipped side asset to its next available side slot.
  Future<void> cycleSideSlot(String assetId) async {
    final data = _data;
    if (_rewards.cycleSideSlot(data.progress.game, data.catalog, assetId)) {
      await _repo.saveProgress(data.progress);
      state = AsyncData(data.bump());
    }
  }

  // --- Backup / restore (export & import) ---

  /// Serializes all local state into a portable, version-stamped backup string.
  String exportBackup() => _repo.exportBackup();

  /// Validates a backup string without applying it (for a confirm screen).
  BackupParse parseBackup(String raw) => decodeBackup(raw);

  /// Replaces all local state with [data] and reloads the session. Reloads the
  /// content bundle if the backup is for a different exam.
  Future<void> importBackup(BackupData data) async {
    final data0 = _data;
    // Resolve the bundle first so a backup for an exam this build does not
    // ship cannot leave the store written but the session unchanged.
    final wantedExam = data.profile?.examId ?? data0.bundle.exam.id;
    var bundle = data0.bundle;
    var profile = data.profile;
    if (wantedExam != data0.bundle.exam.id) {
      try {
        bundle = await ref
            .read(contentRepositoryProvider)
            .loadBundle(wantedExam);
      } catch (_) {
        // Unknown exam: keep the current bundle and point the profile at it.
        profile = profile?.copyWith(examId: data0.bundle.exam.id);
      }
    }
    await _repo.writeBackup(
      BackupData(
        profile: profile,
        progress: data.progress,
        onboarded: data.onboarded,
      ),
    );
    final storedProfile = _repo.loadProfile();
    _emitAndSync(
      AppData(
        bundle: bundle,
        profile: storedProfile,
        progress: _repo.loadProgress(),
        onboarded: _repo.isOnboarded && storedProfile != null,
        catalog: data0.catalog,
        exams: data0.exams,
        revision: data0.revision + 1,
      ),
    );
  }

  /// Debug/testing cheat: grants [amount] XP to the lifetime + spendable total
  /// (also logged to today's history) so the rewards economy is easy to exercise
  /// without grinding. Triggered by the hidden tap gesture on the About screen.
  Future<void> grantCheatXp(int amount) async {
    final data = _data;
    data.progress.game.totalXp += amount;
    data.progress.recordDay(dayKey(DateTime.now()), xp: amount);
    await _repo.saveProgress(data.progress);
    state = AsyncData(data.bump());
  }
}

final appControllerProvider = AsyncNotifierProvider<AppController, AppData>(
  AppController.new,
);
