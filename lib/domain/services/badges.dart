import '../models/content_bundle.dart';
import '../models/progress.dart';
import 'leveling.dart';

/// A definition of an earnable achievement.
class BadgeDef {
  const BadgeDef({
    required this.id,
    required this.title,
    required this.description,
    required this.emoji,
    required this.test,
  });

  final String id;
  final String title;
  final String description;
  final String emoji;

  /// Returns true when the badge's condition is met.
  final bool Function(AppProgress p, ContentBundle bundle) test;
}

/// All achievements. Pure predicates over progress so they are easy to test.
class Badges {
  static const _level = LevelEngine();

  static int _completedLessons(AppProgress p, [String? domain]) {
    var n = 0;
    for (final lp in p.lessons.values) {
      if (!lp.completed) continue;
      if (domain == null) {
        n++;
      } else {
        // lesson id encodes domain: sat-math-... or sat-rw-...
        if (lp.lessonId.contains('-$domain-')) n++;
      }
    }
    return n;
  }

  static final List<BadgeDef> all = [
    BadgeDef(
      id: 'first_lesson',
      title: 'First Steps',
      description: 'Complete your first lesson.',
      emoji: '🎯',
      test: (p, b) => _completedLessons(p) >= 1,
    ),
    BadgeDef(
      id: 'five_lessons',
      title: 'Getting Serious',
      description: 'Complete 5 lessons.',
      emoji: '📚',
      test: (p, b) => _completedLessons(p) >= 5,
    ),
    BadgeDef(
      id: 'streak_3',
      title: 'On a Roll',
      description: 'Reach a 3-day streak.',
      emoji: '🔥',
      test: (p, b) => p.game.longestStreak >= 3,
    ),
    BadgeDef(
      id: 'streak_7',
      title: 'Week Warrior',
      description: 'Reach a 7-day streak.',
      emoji: '⚡',
      test: (p, b) => p.game.longestStreak >= 7,
    ),
    BadgeDef(
      id: 'xp_100',
      title: 'Century',
      description: 'Earn 100 XP.',
      emoji: '💯',
      test: (p, b) => p.game.totalXp >= 100,
    ),
    BadgeDef(
      id: 'xp_500',
      title: 'High Achiever',
      description: 'Earn 500 XP.',
      emoji: '🌟',
      test: (p, b) => p.game.totalXp >= 500,
    ),
    BadgeDef(
      id: 'level_5',
      title: 'Level 5',
      description: 'Reach level 5.',
      emoji: '🏅',
      test: (p, b) => _level.levelForXp(p.game.totalXp) >= 5,
    ),
    BadgeDef(
      id: 'perfect_lesson',
      title: 'Flawless',
      description: 'Earn 3 crowns on any lesson.',
      emoji: '👑',
      test: (p, b) => p.lessons.values.any((lp) => lp.stars >= 3),
    ),
    BadgeDef(
      id: 'math_5',
      title: 'Number Cruncher',
      description: 'Complete 5 Math lessons.',
      emoji: '➗',
      test: (p, b) => _completedLessons(p, 'math') >= 5,
    ),
    BadgeDef(
      id: 'rw_5',
      title: 'Wordsmith',
      description: 'Complete 5 Reading & Writing lessons.',
      emoji: '✍️',
      test: (p, b) => _completedLessons(p, 'rw') >= 5,
    ),
  ];

  static BadgeDef? byId(String id) {
    for (final b in all) {
      if (b.id == id) return b;
    }
    return null;
  }

  /// Returns badge ids newly earned (and adds them to progress.game.earnedBadges).
  static List<String> evaluateAndGrant(AppProgress p, ContentBundle bundle) {
    final newly = <String>[];
    for (final b in all) {
      if (p.game.earnedBadges.contains(b.id)) continue;
      if (b.test(p, bundle)) {
        p.game.earnedBadges.add(b.id);
        newly.add(b.id);
      }
    }
    return newly;
  }
}
