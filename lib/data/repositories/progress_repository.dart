import 'dart:convert';

import '../../domain/models/backup.dart';
import '../../domain/models/profile.dart';
import '../../domain/models/progress.dart';
import '../local/key_value_store.dart';

/// Persists the user profile and progress document locally as JSON.
class ProgressRepository {
  ProgressRepository(this._store);

  final KeyValueStore _store;

  static const _profileKey = 'profile.v1';
  static const _progressKey = 'progress.v1';
  static const _onboardedKey = 'onboarded.v1';

  bool get isOnboarded => _store.getString(_onboardedKey) == 'true';

  /// Loads the profile, or null if absent. Returns null (rather than throwing)
  /// if the stored JSON is unreadable, so a corrupt profile leads to a fresh
  /// onboarding instead of a crash on launch.
  UserProfile? loadProfile() {
    final map = _decodeMap(_profileKey);
    if (map == null) return null;
    try {
      return UserProfile.fromJson(map);
    } catch (_) {
      return null;
    }
  }

  /// Loads progress, falling back to empty progress if the stored JSON is
  /// unreadable. Field-level parsing is already defensive (see the models), so
  /// this top-level guard only triggers for wholesale corruption.
  AppProgress loadProgress() {
    final map = _decodeMap(_progressKey);
    if (map == null) return AppProgress();
    try {
      return AppProgress.fromJson(map);
    } catch (_) {
      return AppProgress();
    }
  }

  /// Decodes a stored JSON object, returning null for missing or invalid data.
  Map<String, dynamic>? _decodeMap(String key) {
    final raw = _store.getString(key);
    if (raw == null) return null;
    try {
      final decoded = jsonDecode(raw);
      return decoded is Map ? decoded.cast<String, dynamic>() : null;
    } catch (_) {
      return null;
    }
  }

  Future<void> saveProfile(UserProfile profile) =>
      _store.setString(_profileKey, jsonEncode(profile.toJson()));

  Future<void> saveProgress(AppProgress progress) =>
      _store.setString(_progressKey, jsonEncode(progress.toJson()));

  Future<void> setOnboarded(bool value) =>
      _store.setString(_onboardedKey, value ? 'true' : 'false');

  /// Serializes all local state into a portable backup string.
  String exportBackup() => encodeBackup(
    BackupData(
      profile: loadProfile(),
      progress: loadProgress(),
      onboarded: isOnboarded,
    ),
  );

  /// Overwrites all local state from a parsed backup.
  Future<void> writeBackup(BackupData data) async {
    if (data.profile != null) {
      await saveProfile(data.profile!);
    } else {
      await _store.remove(_profileKey);
    }
    await saveProgress(data.progress);
    await setOnboarded(data.onboarded);
  }

  /// Wipes all stored progress and profile (Reset Progress in settings).
  Future<void> resetAll() async {
    await _store.remove(_profileKey);
    await _store.remove(_progressKey);
    await _store.remove(_onboardedKey);
  }
}
