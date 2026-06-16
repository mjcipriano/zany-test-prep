import 'dart:convert';

import 'package:flutter/material.dart';
import 'package:flutter_test/flutter_test.dart';
import 'package:zany_test_prep/core/app_info.dart';
import 'package:zany_test_prep/domain/models/backup.dart';
import 'package:zany_test_prep/domain/models/profile.dart';
import 'package:zany_test_prep/domain/models/progress.dart';

BackupData _sample() {
  final progress = AppProgress();
  progress.game.totalXp = 1200;
  progress.game.spentXp = 200;
  progress.game.currentStreak = 7;
  progress.game.streakFreezes = 2;
  progress.game.ownedAssetIds.addAll({'av_premium', 'hat'});
  progress.game.earnedBadges.add('first_lesson');
  progress.lessonProgress('l1')
    ..completed = true
    ..stars = 3;
  return BackupData(
    profile: UserProfile.initial('sat', 15).copyWith(themeMode: ThemeMode.dark),
    progress: progress,
    onboarded: true,
  );
}

void main() {
  test('backup round-trips all state', () {
    final raw = encodeBackup(_sample());
    final parsed = decodeBackup(raw);
    expect(parsed.ok, isTrue);
    final g = parsed.data!.progress.game;
    expect(g.totalXp, 1200);
    expect(g.availableXp, 1000);
    expect(g.currentStreak, 7);
    expect(g.streakFreezes, 2);
    expect(g.ownedAssetIds, containsAll(['av_premium', 'hat']));
    expect(parsed.data!.profile!.dailyGoalMinutes, 15);
    expect(parsed.data!.profile!.themeMode, ThemeMode.dark);
    expect(parsed.data!.onboarded, isTrue);
  });

  test('summary reflects the snapshot', () {
    final parsed = decodeBackup(encodeBackup(_sample()));
    expect(parsed.summary!.totalXp, 1200);
    expect(parsed.summary!.currentStreak, 7);
    expect(parsed.summary!.lessonsCompleted, 1);
    expect(parsed.summary!.ownedAssets, 2);
    expect(parsed.summary!.appVersion, kAppVersion);
    expect(parsed.summary!.exportedAt, isNotNull);
  });

  group('cross-version / robustness', () {
    test('non-backup JSON is rejected with a clear error', () {
      final r = decodeBackup('{"foo":"bar"}');
      expect(r.ok, isFalse);
      expect(r.error, BackupError.notBackup);
    });

    test('garbage / empty input is rejected, not fatal', () {
      expect(decodeBackup('not json').error, BackupError.parseFailed);
      expect(decodeBackup('   ').error, BackupError.empty);
    });

    test('a newer backup format still imports, with a warning', () {
      final env =
          jsonDecode(encodeBackup(_sample())) as Map<String, dynamic>
            ..['formatVersion'] = 999
            ..['someFutureField'] = {'x': 1};
      final r = decodeBackup(jsonEncode(env));
      expect(r.ok, isTrue); // forward-compatible
      expect(r.warnings.any((w) => w.contains('newer version')), isTrue);
      expect(r.data!.progress.game.totalXp, 1200); // known data still restored
    });

    test('a different app version produces an informational warning', () {
      final env = jsonDecode(encodeBackup(_sample(), appVersion: '0.9.0'))
          as Map<String, dynamic>;
      final r = decodeBackup(jsonEncode(env));
      expect(r.ok, isTrue);
      expect(r.warnings.any((w) => w.contains('0.9.0')), isTrue);
    });

    test('matching app version yields no version warning', () {
      final r = decodeBackup(encodeBackup(_sample()));
      expect(r.warnings, isEmpty);
    });

    test('a backup with no profile (pre-onboarding) imports', () {
      final data = BackupData(
        profile: null,
        progress: AppProgress()..game.totalXp = 50,
        onboarded: false,
      );
      final r = decodeBackup(encodeBackup(data));
      expect(r.ok, isTrue);
      expect(r.data!.profile, isNull);
      expect(r.data!.onboarded, isFalse);
      expect(r.data!.progress.game.totalXp, 50);
    });

    test('wrong-typed inner fields are coerced (defensive parse)', () {
      // Hand-build an envelope with a stringy XP and a null owned-set.
      final env = {
        'format': kBackupFormat,
        'formatVersion': 1,
        'appVersion': kAppVersion,
        'progress': {
          'game': {'totalXp': '777', 'ownedAssetIds': null},
        },
      };
      final r = decodeBackup(jsonEncode(env));
      expect(r.ok, isTrue);
      expect(r.data!.progress.game.totalXp, 777);
      expect(r.data!.progress.game.ownedAssetIds, isEmpty);
    });
  });
}
