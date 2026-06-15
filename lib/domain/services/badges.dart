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

  /// Number of completed lessons, optionally filtered to a domain encoded in
  /// the lesson id (e.g. 'math' or 'rw' as in sat-math-... / sat-rw-...).
  static int _completedLessons(AppProgress p, [String? domain]) {
    var n = 0;
    for (final lp in p.lessons.values) {
      if (!lp.completed) continue;
      if (domain == null) {
        n++;
      } else {
        if (lp.lessonId.contains('-$domain-')) n++;
      }
    }
    return n;
  }

  /// Number of lessons earning the full 3 crowns.
  static int _threeCrownLessons(AppProgress p) {
    var n = 0;
    for (final lp in p.lessons.values) {
      if (lp.stars >= 3) n++;
    }
    return n;
  }

  /// Number of skills whose mastery is at or above [threshold].
  static int _skillsAtLeast(AppProgress p, double threshold) {
    var n = 0;
    for (final sm in p.skillMastery.values) {
      if (sm.mastery >= threshold) n++;
    }
    return n;
  }

  /// Total questions attempted across all tracked questions.
  static int _totalAttempts(AppProgress p) {
    var n = 0;
    for (final qs in p.questionStats.values) {
      n += qs.attempts;
    }
    return n;
  }

  /// Total correct answers across all tracked questions.
  static int _totalCorrect(AppProgress p) {
    var n = 0;
    for (final qs in p.questionStats.values) {
      n += qs.correct;
    }
    return n;
  }

  /// Distinct skills the learner has practiced (have any mastery tracked).
  static int _distinctSkillsPracticed(AppProgress p) => p.skillMastery.length;

  static final List<BadgeDef> all = [
    // -------------------------------------------------------------------
    // Total XP milestones
    // -------------------------------------------------------------------
    BadgeDef(
      id: 'xp_50',
      title: 'Warming Up',
      description: 'Earn 50 XP.',
      emoji: '✨',
      test: (p, b) => p.game.totalXp >= 50,
    ),
    BadgeDef(
      id: 'xp_100',
      title: 'Century',
      description: 'Earn 100 XP.',
      emoji: '💯',
      test: (p, b) => p.game.totalXp >= 100,
    ),
    BadgeDef(
      id: 'xp_250',
      title: 'Climbing',
      description: 'Earn 250 XP.',
      emoji: '📈',
      test: (p, b) => p.game.totalXp >= 250,
    ),
    BadgeDef(
      id: 'xp_500',
      title: 'High Achiever',
      description: 'Earn 500 XP.',
      emoji: '🌟',
      test: (p, b) => p.game.totalXp >= 500,
    ),
    BadgeDef(
      id: 'xp_1000',
      title: 'XP Thousandaire',
      description: 'Earn 1,000 XP.',
      emoji: '💎',
      test: (p, b) => p.game.totalXp >= 1000,
    ),
    BadgeDef(
      id: 'xp_2000',
      title: 'XP Tycoon',
      description: 'Earn 2,000 XP.',
      emoji: '🏆',
      test: (p, b) => p.game.totalXp >= 2000,
    ),
    BadgeDef(
      id: 'xp_3500',
      title: 'XP Magnate',
      description: 'Earn 3,500 XP.',
      emoji: '👑',
      test: (p, b) => p.game.totalXp >= 3500,
    ),
    BadgeDef(
      id: 'xp_5000',
      title: 'XP Legend',
      description: 'Earn 5,000 XP.',
      emoji: '🔱',
      test: (p, b) => p.game.totalXp >= 5000,
    ),
    BadgeDef(
      id: 'xp_7500',
      title: 'XP Titan',
      description: 'Earn 7,500 XP.',
      emoji: '🌠',
      test: (p, b) => p.game.totalXp >= 7500,
    ),
    BadgeDef(
      id: 'xp_10000',
      title: 'XP Immortal',
      description: 'Earn 10,000 XP.',
      emoji: '🪐',
      test: (p, b) => p.game.totalXp >= 10000,
    ),

    // -------------------------------------------------------------------
    // Longest streak
    // -------------------------------------------------------------------
    BadgeDef(
      id: 'streak_2',
      title: 'Back for More',
      description: 'Reach a 2-day streak.',
      emoji: '🌱',
      test: (p, b) => p.game.longestStreak >= 2,
    ),
    BadgeDef(
      id: 'streak_3',
      title: 'On a Roll',
      description: 'Reach a 3-day streak.',
      emoji: '🔥',
      test: (p, b) => p.game.longestStreak >= 3,
    ),
    BadgeDef(
      id: 'streak_5',
      title: 'Building Momentum',
      description: 'Reach a 5-day streak.',
      emoji: '⚙️',
      test: (p, b) => p.game.longestStreak >= 5,
    ),
    BadgeDef(
      id: 'streak_7',
      title: 'Week Warrior',
      description: 'Reach a 7-day streak.',
      emoji: '⚡',
      test: (p, b) => p.game.longestStreak >= 7,
    ),
    BadgeDef(
      id: 'streak_10',
      title: 'Perfect Ten',
      description: 'Reach a 10-day streak.',
      emoji: '🔟',
      test: (p, b) => p.game.longestStreak >= 10,
    ),
    BadgeDef(
      id: 'streak_14',
      title: 'Two Weeks Strong',
      description: 'Reach a 14-day streak.',
      emoji: '🗓️',
      test: (p, b) => p.game.longestStreak >= 14,
    ),
    BadgeDef(
      id: 'streak_21',
      title: 'Habit Formed',
      description: 'Reach a 21-day streak.',
      emoji: '🧠',
      test: (p, b) => p.game.longestStreak >= 21,
    ),
    BadgeDef(
      id: 'streak_30',
      title: 'Monthly Master',
      description: 'Reach a 30-day streak.',
      emoji: '📆',
      test: (p, b) => p.game.longestStreak >= 30,
    ),
    BadgeDef(
      id: 'streak_50',
      title: 'Unstoppable',
      description: 'Reach a 50-day streak.',
      emoji: '🚀',
      test: (p, b) => p.game.longestStreak >= 50,
    ),
    BadgeDef(
      id: 'streak_100',
      title: 'Century Streak',
      description: 'Reach a 100-day streak.',
      emoji: '🔥',
      test: (p, b) => p.game.longestStreak >= 100,
    ),

    // -------------------------------------------------------------------
    // Level reached
    // -------------------------------------------------------------------
    BadgeDef(
      id: 'level_2',
      title: 'Level 2',
      description: 'Reach level 2.',
      emoji: '🥉',
      test: (p, b) => _level.levelForXp(p.game.totalXp) >= 2,
    ),
    BadgeDef(
      id: 'level_3',
      title: 'Level 3',
      description: 'Reach level 3.',
      emoji: '🥈',
      test: (p, b) => _level.levelForXp(p.game.totalXp) >= 3,
    ),
    BadgeDef(
      id: 'level_5',
      title: 'Level 5',
      description: 'Reach level 5.',
      emoji: '🏅',
      test: (p, b) => _level.levelForXp(p.game.totalXp) >= 5,
    ),
    BadgeDef(
      id: 'level_7',
      title: 'Level 7',
      description: 'Reach level 7.',
      emoji: '🎖️',
      test: (p, b) => _level.levelForXp(p.game.totalXp) >= 7,
    ),
    BadgeDef(
      id: 'level_10',
      title: 'Double Digits',
      description: 'Reach level 10.',
      emoji: '🏆',
      test: (p, b) => _level.levelForXp(p.game.totalXp) >= 10,
    ),
    BadgeDef(
      id: 'level_15',
      title: 'Seasoned',
      description: 'Reach level 15.',
      emoji: '🛡️',
      test: (p, b) => _level.levelForXp(p.game.totalXp) >= 15,
    ),
    BadgeDef(
      id: 'level_20',
      title: 'Veteran',
      description: 'Reach level 20.',
      emoji: '⚔️',
      test: (p, b) => _level.levelForXp(p.game.totalXp) >= 20,
    ),
    BadgeDef(
      id: 'level_25',
      title: 'Elite',
      description: 'Reach level 25.',
      emoji: '🌟',
      test: (p, b) => _level.levelForXp(p.game.totalXp) >= 25,
    ),
    BadgeDef(
      id: 'level_30',
      title: 'Grandmaster',
      description: 'Reach level 30.',
      emoji: '👑',
      test: (p, b) => _level.levelForXp(p.game.totalXp) >= 30,
    ),
    BadgeDef(
      id: 'level_40',
      title: 'Ascended',
      description: 'Reach level 40.',
      emoji: '🪽',
      test: (p, b) => _level.levelForXp(p.game.totalXp) >= 40,
    ),

    // -------------------------------------------------------------------
    // Lessons completed
    // -------------------------------------------------------------------
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
      id: 'lessons_10',
      title: 'Dedicated',
      description: 'Complete 10 lessons.',
      emoji: '📖',
      test: (p, b) => _completedLessons(p) >= 10,
    ),
    BadgeDef(
      id: 'lessons_20',
      title: 'Bookworm',
      description: 'Complete 20 lessons.',
      emoji: '🐛',
      test: (p, b) => _completedLessons(p) >= 20,
    ),
    BadgeDef(
      id: 'lessons_30',
      title: 'Scholar',
      description: 'Complete 30 lessons.',
      emoji: '🎓',
      test: (p, b) => _completedLessons(p) >= 30,
    ),
    BadgeDef(
      id: 'lessons_50',
      title: 'Half-Centurion',
      description: 'Complete 50 lessons.',
      emoji: '📕',
      test: (p, b) => _completedLessons(p) >= 50,
    ),
    BadgeDef(
      id: 'lessons_75',
      title: 'Lesson Devotee',
      description: 'Complete 75 lessons.',
      emoji: '📗',
      test: (p, b) => _completedLessons(p) >= 75,
    ),
    BadgeDef(
      id: 'lessons_100',
      title: 'Lesson Centurion',
      description: 'Complete 100 lessons.',
      emoji: '📘',
      test: (p, b) => _completedLessons(p) >= 100,
    ),
    BadgeDef(
      id: 'lessons_150',
      title: 'Lesson Maven',
      description: 'Complete 150 lessons.',
      emoji: '📙',
      test: (p, b) => _completedLessons(p) >= 150,
    ),
    BadgeDef(
      id: 'lessons_200',
      title: 'Lesson Sage',
      description: 'Complete 200 lessons.',
      emoji: '📚',
      test: (p, b) => _completedLessons(p) >= 200,
    ),

    // -------------------------------------------------------------------
    // Math lessons completed
    // -------------------------------------------------------------------
    BadgeDef(
      id: 'math_1',
      title: 'First Equation',
      description: 'Complete your first Math lesson.',
      emoji: '🔢',
      test: (p, b) => _completedLessons(p, 'math') >= 1,
    ),
    BadgeDef(
      id: 'math_5',
      title: 'Number Cruncher',
      description: 'Complete 5 Math lessons.',
      emoji: '➗',
      test: (p, b) => _completedLessons(p, 'math') >= 5,
    ),
    BadgeDef(
      id: 'math_10',
      title: 'Algebra Ace',
      description: 'Complete 10 Math lessons.',
      emoji: '➕',
      test: (p, b) => _completedLessons(p, 'math') >= 10,
    ),
    BadgeDef(
      id: 'math_20',
      title: 'Math Whiz',
      description: 'Complete 20 Math lessons.',
      emoji: '🧮',
      test: (p, b) => _completedLessons(p, 'math') >= 20,
    ),
    BadgeDef(
      id: 'math_35',
      title: 'Quant Pro',
      description: 'Complete 35 Math lessons.',
      emoji: '📐',
      test: (p, b) => _completedLessons(p, 'math') >= 35,
    ),
    BadgeDef(
      id: 'math_50',
      title: 'Math Maestro',
      description: 'Complete 50 Math lessons.',
      emoji: '🧠',
      test: (p, b) => _completedLessons(p, 'math') >= 50,
    ),

    // -------------------------------------------------------------------
    // Reading & Writing lessons completed
    // -------------------------------------------------------------------
    BadgeDef(
      id: 'rw_1',
      title: 'First Word',
      description: 'Complete your first Reading & Writing lesson.',
      emoji: '📝',
      test: (p, b) => _completedLessons(p, 'rw') >= 1,
    ),
    BadgeDef(
      id: 'rw_5',
      title: 'Wordsmith',
      description: 'Complete 5 Reading & Writing lessons.',
      emoji: '✍️',
      test: (p, b) => _completedLessons(p, 'rw') >= 5,
    ),
    BadgeDef(
      id: 'rw_10',
      title: 'Avid Reader',
      description: 'Complete 10 Reading & Writing lessons.',
      emoji: '📜',
      test: (p, b) => _completedLessons(p, 'rw') >= 10,
    ),
    BadgeDef(
      id: 'rw_20',
      title: 'Grammar Guru',
      description: 'Complete 20 Reading & Writing lessons.',
      emoji: '🖋️',
      test: (p, b) => _completedLessons(p, 'rw') >= 20,
    ),
    BadgeDef(
      id: 'rw_35',
      title: 'Prose Pro',
      description: 'Complete 35 Reading & Writing lessons.',
      emoji: '📃',
      test: (p, b) => _completedLessons(p, 'rw') >= 35,
    ),
    BadgeDef(
      id: 'rw_50',
      title: 'Literary Legend',
      description: 'Complete 50 Reading & Writing lessons.',
      emoji: '🏛️',
      test: (p, b) => _completedLessons(p, 'rw') >= 50,
    ),

    // -------------------------------------------------------------------
    // Lessons earning 3 crowns
    // -------------------------------------------------------------------
    BadgeDef(
      id: 'perfect_lesson',
      title: 'Flawless',
      description: 'Earn 3 crowns on any lesson.',
      emoji: '👑',
      test: (p, b) => _threeCrownLessons(p) >= 1,
    ),
    BadgeDef(
      id: 'crowns_5',
      title: 'Crown Collector',
      description: 'Earn 3 crowns on 5 lessons.',
      emoji: '👑',
      test: (p, b) => _threeCrownLessons(p) >= 5,
    ),
    BadgeDef(
      id: 'crowns_10',
      title: 'Crowned Ten',
      description: 'Earn 3 crowns on 10 lessons.',
      emoji: '💫',
      test: (p, b) => _threeCrownLessons(p) >= 10,
    ),
    BadgeDef(
      id: 'crowns_20',
      title: 'Royalty',
      description: 'Earn 3 crowns on 20 lessons.',
      emoji: '🤴',
      test: (p, b) => _threeCrownLessons(p) >= 20,
    ),
    BadgeDef(
      id: 'crowns_35',
      title: 'Crown Hoarder',
      description: 'Earn 3 crowns on 35 lessons.',
      emoji: '🏰',
      test: (p, b) => _threeCrownLessons(p) >= 35,
    ),
    BadgeDef(
      id: 'crowns_50',
      title: 'Crown Sovereign',
      description: 'Earn 3 crowns on 50 lessons.',
      emoji: '👸',
      test: (p, b) => _threeCrownLessons(p) >= 50,
    ),
    BadgeDef(
      id: 'crowns_75',
      title: 'Crown Emperor',
      description: 'Earn 3 crowns on 75 lessons.',
      emoji: '🫅',
      test: (p, b) => _threeCrownLessons(p) >= 75,
    ),

    // -------------------------------------------------------------------
    // Skills mastered (>= 80 mastery)
    // -------------------------------------------------------------------
    BadgeDef(
      id: 'mastered_1',
      title: 'First Mastery',
      description: 'Master 1 skill (80%+ mastery).',
      emoji: '🌟',
      test: (p, b) => _skillsAtLeast(p, 80) >= 1,
    ),
    BadgeDef(
      id: 'mastered_3',
      title: 'Triple Threat',
      description: 'Master 3 skills (80%+ mastery).',
      emoji: '⭐',
      test: (p, b) => _skillsAtLeast(p, 80) >= 3,
    ),
    BadgeDef(
      id: 'mastered_5',
      title: 'Skill Specialist',
      description: 'Master 5 skills (80%+ mastery).',
      emoji: '🌠',
      test: (p, b) => _skillsAtLeast(p, 80) >= 5,
    ),
    BadgeDef(
      id: 'mastered_10',
      title: 'Skill Expert',
      description: 'Master 10 skills (80%+ mastery).',
      emoji: '🎇',
      test: (p, b) => _skillsAtLeast(p, 80) >= 10,
    ),
    BadgeDef(
      id: 'mastered_15',
      title: 'Skill Authority',
      description: 'Master 15 skills (80%+ mastery).',
      emoji: '🏵️',
      test: (p, b) => _skillsAtLeast(p, 80) >= 15,
    ),
    BadgeDef(
      id: 'mastered_20',
      title: 'Skill Virtuoso',
      description: 'Master 20 skills (80%+ mastery).',
      emoji: '🎆',
      test: (p, b) => _skillsAtLeast(p, 80) >= 20,
    ),
    BadgeDef(
      id: 'mastered_25',
      title: 'Master of Masters',
      description: 'Master 25 skills (80%+ mastery).',
      emoji: '💠',
      test: (p, b) => _skillsAtLeast(p, 80) >= 25,
    ),

    // -------------------------------------------------------------------
    // Skills proficient (>= 50 mastery)
    // -------------------------------------------------------------------
    BadgeDef(
      id: 'proficient_1',
      title: 'Getting Good',
      description: 'Reach 50%+ mastery in 1 skill.',
      emoji: '👍',
      test: (p, b) => _skillsAtLeast(p, 50) >= 1,
    ),
    BadgeDef(
      id: 'proficient_5',
      title: 'Well Rounded',
      description: 'Reach 50%+ mastery in 5 skills.',
      emoji: '🔆',
      test: (p, b) => _skillsAtLeast(p, 50) >= 5,
    ),
    BadgeDef(
      id: 'proficient_10',
      title: 'Broadly Capable',
      description: 'Reach 50%+ mastery in 10 skills.',
      emoji: '🌐',
      test: (p, b) => _skillsAtLeast(p, 50) >= 10,
    ),
    BadgeDef(
      id: 'proficient_20',
      title: 'Versatile Mind',
      description: 'Reach 50%+ mastery in 20 skills.',
      emoji: '🧩',
      test: (p, b) => _skillsAtLeast(p, 50) >= 20,
    ),
    BadgeDef(
      id: 'proficient_30',
      title: 'Renaissance Learner',
      description: 'Reach 50%+ mastery in 30 skills.',
      emoji: '🎨',
      test: (p, b) => _skillsAtLeast(p, 50) >= 30,
    ),

    // -------------------------------------------------------------------
    // Total questions answered (sum of attempts)
    // -------------------------------------------------------------------
    BadgeDef(
      id: 'attempts_10',
      title: 'First Reps',
      description: 'Answer 10 questions.',
      emoji: '❓',
      test: (p, b) => _totalAttempts(p) >= 10,
    ),
    BadgeDef(
      id: 'attempts_50',
      title: 'Question Hunter',
      description: 'Answer 50 questions.',
      emoji: '🔍',
      test: (p, b) => _totalAttempts(p) >= 50,
    ),
    BadgeDef(
      id: 'attempts_100',
      title: 'Hundred Questions',
      description: 'Answer 100 questions.',
      emoji: '💯',
      test: (p, b) => _totalAttempts(p) >= 100,
    ),
    BadgeDef(
      id: 'attempts_250',
      title: 'Quiz Machine',
      description: 'Answer 250 questions.',
      emoji: '🤖',
      test: (p, b) => _totalAttempts(p) >= 250,
    ),
    BadgeDef(
      id: 'attempts_500',
      title: 'Question Crusher',
      description: 'Answer 500 questions.',
      emoji: '🪓',
      test: (p, b) => _totalAttempts(p) >= 500,
    ),
    BadgeDef(
      id: 'attempts_1000',
      title: 'Thousand Tries',
      description: 'Answer 1,000 questions.',
      emoji: '🎰',
      test: (p, b) => _totalAttempts(p) >= 1000,
    ),
    BadgeDef(
      id: 'attempts_2500',
      title: 'Practice Powerhouse',
      description: 'Answer 2,500 questions.',
      emoji: '🏋️',
      test: (p, b) => _totalAttempts(p) >= 2500,
    ),
    BadgeDef(
      id: 'attempts_5000',
      title: 'Question Marathon',
      description: 'Answer 5,000 questions.',
      emoji: '🏃',
      test: (p, b) => _totalAttempts(p) >= 5000,
    ),
    BadgeDef(
      id: 'attempts_10000',
      title: 'Question Colossus',
      description: 'Answer 10,000 questions.',
      emoji: '🗿',
      test: (p, b) => _totalAttempts(p) >= 10000,
    ),

    // -------------------------------------------------------------------
    // Total correct answers (sum of correct)
    // -------------------------------------------------------------------
    BadgeDef(
      id: 'correct_10',
      title: 'First Wins',
      description: 'Answer 10 questions correctly.',
      emoji: '✅',
      test: (p, b) => _totalCorrect(p) >= 10,
    ),
    BadgeDef(
      id: 'correct_50',
      title: 'Right Answers',
      description: 'Answer 50 questions correctly.',
      emoji: '☑️',
      test: (p, b) => _totalCorrect(p) >= 50,
    ),
    BadgeDef(
      id: 'correct_100',
      title: 'Hundred Right',
      description: 'Answer 100 questions correctly.',
      emoji: '🎯',
      test: (p, b) => _totalCorrect(p) >= 100,
    ),
    BadgeDef(
      id: 'correct_250',
      title: 'Sharpshooter',
      description: 'Answer 250 questions correctly.',
      emoji: '🏹',
      test: (p, b) => _totalCorrect(p) >= 250,
    ),
    BadgeDef(
      id: 'correct_500',
      title: 'Accuracy Ace',
      description: 'Answer 500 questions correctly.',
      emoji: '🎖️',
      test: (p, b) => _totalCorrect(p) >= 500,
    ),
    BadgeDef(
      id: 'correct_1000',
      title: 'Thousand Right',
      description: 'Answer 1,000 questions correctly.',
      emoji: '🏆',
      test: (p, b) => _totalCorrect(p) >= 1000,
    ),
    BadgeDef(
      id: 'correct_2500',
      title: 'Precision Master',
      description: 'Answer 2,500 questions correctly.',
      emoji: '🎱',
      test: (p, b) => _totalCorrect(p) >= 2500,
    ),
    BadgeDef(
      id: 'correct_5000',
      title: 'Correctness King',
      description: 'Answer 5,000 questions correctly.',
      emoji: '👑',
      test: (p, b) => _totalCorrect(p) >= 5000,
    ),

    // -------------------------------------------------------------------
    // Distinct skills practiced
    // -------------------------------------------------------------------
    BadgeDef(
      id: 'skills_1',
      title: 'Skill Sampler',
      description: 'Practice 1 distinct skill.',
      emoji: '🔬',
      test: (p, b) => _distinctSkillsPracticed(p) >= 1,
    ),
    BadgeDef(
      id: 'skills_5',
      title: 'Skill Explorer',
      description: 'Practice 5 distinct skills.',
      emoji: '🧭',
      test: (p, b) => _distinctSkillsPracticed(p) >= 5,
    ),
    BadgeDef(
      id: 'skills_10',
      title: 'Skill Adventurer',
      description: 'Practice 10 distinct skills.',
      emoji: '🗺️',
      test: (p, b) => _distinctSkillsPracticed(p) >= 10,
    ),
    BadgeDef(
      id: 'skills_15',
      title: 'Skill Voyager',
      description: 'Practice 15 distinct skills.',
      emoji: '⛵',
      test: (p, b) => _distinctSkillsPracticed(p) >= 15,
    ),
    BadgeDef(
      id: 'skills_20',
      title: 'Skill Pioneer',
      description: 'Practice 20 distinct skills.',
      emoji: '🚩',
      test: (p, b) => _distinctSkillsPracticed(p) >= 20,
    ),
    BadgeDef(
      id: 'skills_25',
      title: 'Skill Cartographer',
      description: 'Practice 25 distinct skills.',
      emoji: '🧱',
      test: (p, b) => _distinctSkillsPracticed(p) >= 25,
    ),
    BadgeDef(
      id: 'skills_30',
      title: 'Skill Conqueror',
      description: 'Practice 30 distinct skills.',
      emoji: '🏔️',
      test: (p, b) => _distinctSkillsPracticed(p) >= 30,
    ),

    // -------------------------------------------------------------------
    // Fun one-offs
    // -------------------------------------------------------------------
    BadgeDef(
      id: 'daily_100',
      title: 'Big Day',
      description: 'Earn 100 XP in a single day.',
      emoji: '☀️',
      test: (p, b) => p.game.dailyXp >= 100,
    ),
    BadgeDef(
      id: 'daily_250',
      title: 'Grind Day',
      description: 'Earn 250 XP in a single day.',
      emoji: '🌞',
      test: (p, b) => p.game.dailyXp >= 250,
    ),
    BadgeDef(
      id: 'comeback',
      title: 'Comeback Kid',
      description: 'Rebuild a streak after losing one.',
      emoji: '🔄',
      test: (p, b) =>
          p.game.longestStreak >= 3 &&
          p.game.currentStreak >= 1 &&
          p.game.currentStreak < p.game.longestStreak,
    ),
    BadgeDef(
      id: 'review_cleared',
      title: 'Clean Slate',
      description: 'Empty your review queue after practicing.',
      emoji: '🧹',
      test: (p, b) => p.reviewQueue.isEmpty && _totalAttempts(p) >= 10,
    ),
    BadgeDef(
      id: 'review_grind',
      title: 'Review Grinder',
      description: 'Build a review queue of 20+ items.',
      emoji: '🔁',
      test: (p, b) => p.reviewQueue.length >= 20,
    ),
    BadgeDef(
      id: 'lesson_replayer',
      title: 'Repeat Performer',
      description: 'Complete a single lesson 5 times.',
      emoji: '🔂',
      test: (p, b) => p.lessons.values.any((lp) => lp.timesCompleted >= 5),
    ),
    BadgeDef(
      id: 'all_correct_lesson',
      title: 'Spotless',
      description: 'Ace a lesson with every answer correct.',
      emoji: '🥇',
      test: (p, b) => p.lessons.values.any(
        (lp) => lp.completed && lp.total > 0 && lp.bestCorrect >= lp.total,
      ),
    ),
    BadgeDef(
      id: 'well_rounded',
      title: 'Both Sides',
      description: 'Complete both a Math and a Reading & Writing lesson.',
      emoji: '⚖️',
      test: (p, b) =>
          _completedLessons(p, 'math') >= 1 && _completedLessons(p, 'rw') >= 1,
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
