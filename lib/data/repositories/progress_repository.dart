import 'dart:convert';

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

  UserProfile? loadProfile() {
    final raw = _store.getString(_profileKey);
    if (raw == null) return null;
    return UserProfile.fromJson(jsonDecode(raw) as Map<String, dynamic>);
  }

  AppProgress loadProgress() {
    final raw = _store.getString(_progressKey);
    if (raw == null) return AppProgress();
    return AppProgress.fromJson(jsonDecode(raw) as Map<String, dynamic>);
  }

  Future<void> saveProfile(UserProfile profile) =>
      _store.setString(_profileKey, jsonEncode(profile.toJson()));

  Future<void> saveProgress(AppProgress progress) =>
      _store.setString(_progressKey, jsonEncode(progress.toJson()));

  Future<void> setOnboarded(bool value) =>
      _store.setString(_onboardedKey, value ? 'true' : 'false');

  /// Wipes all stored progress and profile (Reset Progress in settings).
  Future<void> resetAll() async {
    await _store.remove(_profileKey);
    await _store.remove(_progressKey);
    await _store.remove(_onboardedKey);
  }
}
