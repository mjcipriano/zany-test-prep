/// Portable, cross-version backup of all local state (profile + progress +
/// onboarding), used by the export/import feature so progress can move between
/// devices or survive a reinstall.
///
/// The on-disk format is a single JSON envelope that stamps the app + schema
/// versions, so an import on a different platform or app version can validate it,
/// warn about mismatches, and still restore everything it understands. Parsing
/// reuses the defensive model `fromJson`s (see [safe_json.dart]), so unknown or
/// wrongly-typed fields degrade gracefully instead of failing the whole import.
library;

import 'dart:convert';

import '../../core/app_info.dart';
import 'profile.dart';
import 'progress.dart';
import 'safe_json.dart';

/// Magic string identifying a Zany Test Prep backup document.
const String kBackupFormat = 'zany-test-prep-backup';

/// Envelope version. Bump only if the *envelope* shape changes (not the inner
/// profile/progress schemas, which carry their own versions).
const int kBackupFormatVersion = 1;

/// The three pieces of local state a backup carries.
class BackupData {
  const BackupData({
    required this.profile,
    required this.progress,
    required this.onboarded,
  });

  final UserProfile? profile;
  final AppProgress progress;
  final bool onboarded;
}

/// A short, human-readable summary of a backup, shown before importing so the
/// user can confirm they're restoring the right snapshot.
class BackupSummary {
  const BackupSummary({
    required this.totalXp,
    required this.currentStreak,
    required this.lessonsCompleted,
    required this.ownedAssets,
    this.appVersion,
    this.exportedAt,
  });

  final int totalXp;
  final int currentStreak;
  final int lessonsCompleted;
  final int ownedAssets;
  final String? appVersion;
  final DateTime? exportedAt;
}

enum BackupError { empty, notBackup, parseFailed }

/// Result of decoding a backup string: either parsed [data] (+ optional
/// [warnings]) or an [error] describing why it couldn't be read.
class BackupParse {
  const BackupParse._({
    this.data,
    this.summary,
    this.warnings = const [],
    this.error,
  });

  factory BackupParse.success(
    BackupData data,
    BackupSummary summary,
    List<String> warnings,
  ) => BackupParse._(data: data, summary: summary, warnings: warnings);

  factory BackupParse.failure(BackupError error) => BackupParse._(error: error);

  final BackupData? data;
  final BackupSummary? summary;
  final List<String> warnings;
  final BackupError? error;

  bool get ok => data != null;

  /// A user-facing explanation for a failed parse.
  String get message => switch (error) {
    BackupError.empty => 'Nothing to import — the backup is empty.',
    BackupError.notBackup =>
      "This doesn't look like a Zany Test Prep backup file.",
    BackupError.parseFailed =>
      'The backup is corrupted or not valid backup data.',
    null => 'OK',
  };
}

/// Serializes [data] into a pretty-printed backup string.
String encodeBackup(
  BackupData data, {
  String appVersion = kAppVersion,
  DateTime? now,
}) {
  final envelope = <String, dynamic>{
    'format': kBackupFormat,
    'formatVersion': kBackupFormatVersion,
    'appVersion': appVersion,
    'exportedAt': (now ?? DateTime.now()).toIso8601String(),
    'profileSchema': kProfileSchemaVersion,
    'progressSchema': kProgressSchemaVersion,
    'onboarded': data.onboarded,
    'profile': data.profile?.toJson(),
    'progress': data.progress.toJson(),
  };
  return const JsonEncoder.withIndent('  ').convert(envelope);
}

/// Parses a backup string, tolerating version drift and partial corruption.
BackupParse decodeBackup(String raw) {
  if (raw.trim().isEmpty) return BackupParse.failure(BackupError.empty);

  final Object? decoded;
  try {
    decoded = jsonDecode(raw);
  } catch (_) {
    return BackupParse.failure(BackupError.parseFailed);
  }
  if (decoded is! Map) return BackupParse.failure(BackupError.notBackup);
  final env = decoded.cast<String, dynamic>();
  if (asString(env['format']) != kBackupFormat) {
    return BackupParse.failure(BackupError.notBackup);
  }

  final warnings = <String>[];
  final formatVersion = asInt(env['formatVersion'], 1);
  if (formatVersion > kBackupFormatVersion) {
    warnings.add(
      'This backup was created by a newer version of the app (backup format '
      'v$formatVersion). It will still be imported, but anything this version '
      "doesn't recognize is skipped.",
    );
  }
  final appVersion = asStringOrNull(env['appVersion']);
  if (appVersion != null && appVersion != kAppVersion) {
    warnings.add(
      'Backup is from app version $appVersion; this device runs $kAppVersion.',
    );
  }

  final BackupData data;
  try {
    final progress = AppProgress.fromJson(asMap(env['progress']));
    final profileRaw = env['profile'];
    final profile = profileRaw is Map
        ? UserProfile.fromJson(profileRaw.cast<String, dynamic>())
        : null;
    final onboarded = asBool(env['onboarded'], profile != null);
    data = BackupData(
      profile: profile,
      progress: progress,
      onboarded: onboarded,
    );
  } catch (_) {
    return BackupParse.failure(BackupError.parseFailed);
  }

  final summary = BackupSummary(
    totalXp: data.progress.game.totalXp,
    currentStreak: data.progress.game.currentStreak,
    lessonsCompleted: data.progress.lessons.values
        .where((l) => l.completed)
        .length,
    ownedAssets: data.progress.game.ownedAssetIds.length,
    appVersion: appVersion,
    exportedAt: DateTime.tryParse(asString(env['exportedAt'])),
  );
  return BackupParse.success(data, summary, warnings);
}
