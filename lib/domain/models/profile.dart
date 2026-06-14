import 'package:flutter/material.dart';

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

  /// Daily goal expressed as XP (about 5 XP per minute of focused practice).
  int get dailyGoalXp => dailyGoalMinutes * 5;

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
      targetTestDate:
          clearTargetDate ? null : (targetTestDate ?? this.targetTestDate),
      soundOn: soundOn ?? this.soundOn,
      hapticsOn: hapticsOn ?? this.hapticsOn,
      themeMode: themeMode ?? this.themeMode,
      createdAt: createdAt,
    );
  }

  Map<String, dynamic> toJson() => {
        'examId': examId,
        'dailyGoalMinutes': dailyGoalMinutes,
        'targetTestDate': targetTestDate?.toIso8601String(),
        'soundOn': soundOn,
        'hapticsOn': hapticsOn,
        'themeMode': themeMode.name,
        'createdAt': createdAt.toIso8601String(),
      };

  factory UserProfile.fromJson(Map<String, dynamic> json) => UserProfile(
        examId: json['examId'] as String? ?? 'sat',
        dailyGoalMinutes: json['dailyGoalMinutes'] as int? ?? 10,
        targetTestDate: json['targetTestDate'] == null
            ? null
            : DateTime.tryParse(json['targetTestDate'] as String),
        soundOn: json['soundOn'] as bool? ?? true,
        hapticsOn: json['hapticsOn'] as bool? ?? true,
        themeMode: ThemeMode.values.firstWhere(
          (m) => m.name == json['themeMode'],
          orElse: () => ThemeMode.system,
        ),
        createdAt: DateTime.tryParse(json['createdAt'] as String? ?? '') ??
            DateTime.now(),
      );

  static UserProfile initial(String examId, int dailyGoalMinutes) => UserProfile(
        examId: examId,
        dailyGoalMinutes: dailyGoalMinutes,
        createdAt: DateTime.now(),
      );
}
