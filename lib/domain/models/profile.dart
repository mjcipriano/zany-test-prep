import 'package:flutter/material.dart';

import 'safe_json.dart';

/// Bumped only when the persisted profile shape needs a real migration.
const int kProfileSchemaVersion = 1;

/// The locally stored user profile. No login, no backend.
class UserProfile {
  const UserProfile({
    required this.examId,
    required this.dailyGoalMinutes,
    this.targetTestDate,
    this.soundOn = true,
    this.hapticsOn = true,
    this.themeMode = ThemeMode.system,
    required this.createdAt,
  });

  final String examId;
  final int dailyGoalMinutes; // 5, 10, or 15
  final DateTime? targetTestDate;
  final bool soundOn;
  final bool hapticsOn;
  final ThemeMode themeMode;
  final DateTime createdAt;

  /// Daily goal expressed as XP. Calibrated to roughly 20 XP per minute of
  /// focused practice (a short lesson is ~150-200 XP), so 5/10/15-minute goals
  /// are 100/200/300 XP — a meaningful session rather than a single question.
  int get dailyGoalXp => dailyGoalMinutes * 20;

  UserProfile copyWith({
    String? examId,
    int? dailyGoalMinutes,
    DateTime? targetTestDate,
    bool clearTargetDate = false,
    bool? soundOn,
    bool? hapticsOn,
    ThemeMode? themeMode,
  }) {
    return UserProfile(
      examId: examId ?? this.examId,
      dailyGoalMinutes: dailyGoalMinutes ?? this.dailyGoalMinutes,
      targetTestDate: clearTargetDate
          ? null
          : (targetTestDate ?? this.targetTestDate),
      soundOn: soundOn ?? this.soundOn,
      hapticsOn: hapticsOn ?? this.hapticsOn,
      themeMode: themeMode ?? this.themeMode,
      createdAt: createdAt,
    );
  }

  Map<String, dynamic> toJson() => {
    'schema': kProfileSchemaVersion,
    'examId': examId,
    'dailyGoalMinutes': dailyGoalMinutes,
    'targetTestDate': targetTestDate?.toIso8601String(),
    'soundOn': soundOn,
    'hapticsOn': hapticsOn,
    'themeMode': themeMode.name,
    'createdAt': createdAt.toIso8601String(),
  };

  /// Defensive parse: every field tolerates a missing or wrong-typed value and
  /// falls back to a valid default, so a profile written by any version loads
  /// without crashing. [dailyGoalMinutes] is also clamped to a sane range.
  factory UserProfile.fromJson(Map<String, dynamic> json) {
    final minutes = asInt(json['dailyGoalMinutes'], 10);
    return UserProfile(
      examId: asString(json['examId'], 'sat'),
      dailyGoalMinutes: minutes < 1 ? 10 : (minutes > 120 ? 120 : minutes),
      targetTestDate: DateTime.tryParse(asString(json['targetTestDate'])),
      soundOn: asBool(json['soundOn'], true),
      hapticsOn: asBool(json['hapticsOn'], true),
      themeMode: ThemeMode.values.firstWhere(
        (m) => m.name == asStringOrNull(json['themeMode']),
        orElse: () => ThemeMode.system,
      ),
      createdAt:
          DateTime.tryParse(asString(json['createdAt'])) ?? DateTime.now(),
    );
  }

  static UserProfile initial(String examId, int dailyGoalMinutes) =>
      UserProfile(
        examId: examId,
        dailyGoalMinutes: dailyGoalMinutes,
        createdAt: DateTime.now(),
      );
}
