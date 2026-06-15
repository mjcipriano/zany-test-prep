import 'package:flutter_test/flutter_test.dart';
import 'package:zany_test_prep/domain/models/content_bundle.dart';
import 'package:zany_test_prep/domain/models/difficulty.dart';
import 'package:zany_test_prep/domain/models/exam.dart';
import 'package:zany_test_prep/domain/models/lesson.dart';
import 'package:zany_test_prep/domain/models/progress.dart';
import 'package:zany_test_prep/domain/models/question.dart';
import 'package:zany_test_prep/domain/models/skill.dart';
import 'package:zany_test_prep/domain/services/mastery_engine.dart';
import 'package:zany_test_prep/domain/services/review_engine.dart';
import 'package:zany_test_prep/domain/services/unlock_engine.dart';

Question _q(
  String id, {
  Difficulty d = Difficulty.medium,
  String skill = 's1',
}) => Question(
  id: id,
  examId: 'sat',
  domain: 'math',
  section: 'algebra',
  skill: skill,
  lessonId: 'l1',
  difficulty: d,
  type: QuestionType.multipleChoice,
  estimatedTimeSeconds: 60,
  prompt: 'p',
  explanation: 'e',
  tags: const ['t'],
  choices: const [Choice(id: 'A', text: '1', rationale: 'r')],
  correctChoice: 'A',
);

Lesson _lesson(String id, {List<String> prereq = const [], int unlockXp = 0}) =>
    Lesson(
      id: id,
      examId: 'sat',
      domain: 'math',
      section: 'algebra',
      skill: 's1',
      title: id,
      order: 0,
      difficulty: Difficulty.easy,
      estimatedMinutes: 5,
      teachingCard: const TeachingCard(
        title: 't',
        body: 'b',
        keyPoints: ['a', 'b'],
      ),
      questionIds: const ['q1'],
      prerequisiteLessonIds: prereq,
      unlockXp: unlockXp,
      tags: const ['math'],
    );

void main() {
  group('MasteryEngine', () {
    const m = MasteryEngine();
    test('correct answers raise mastery, harder more', () {
      expect(
        m.update(current: 0, correct: true, difficulty: Difficulty.easy),
        4,
      );
      expect(
        m.update(current: 0, correct: true, difficulty: Difficulty.hard),
        12,
      );
    });
    test('wrong answers lower mastery but less than a correct raises', () {
      expect(
        m.update(current: 50, correct: false, difficulty: Difficulty.hard),
        44,
      );
    });
    test('mastery is clamped to 0..100', () {
      expect(
        m.update(current: 99, correct: true, difficulty: Difficulty.hard),
        100,
      );
      expect(
        m.update(current: 1, correct: false, difficulty: Difficulty.hard),
        0,
      );
    });
    test('review correct gains less than a fresh correct', () {
      final fresh = m.update(
        current: 0,
        correct: true,
        difficulty: Difficulty.hard,
      );
      final review = m.update(
        current: 0,
        correct: true,
        difficulty: Difficulty.hard,
        isReview: true,
      );
      expect(review, lessThan(fresh));
    });
  });

  group('ReviewEngine', () {
    const r = ReviewEngine();
    test('a missed question enters the queue, due immediately', () {
      final p = AppProgress();
      r.onAnswered(progress: p, question: _q('q1'), correct: false);
      expect(p.reviewQueue.length, 1);
      expect(p.reviewQueue.first.questionId, 'q1');
      expect(r.dueCount(p), 1); // reviewable right away
    });
    test('a correct review pushes the next due date into the future', () {
      final p = AppProgress();
      final q = _q('q1', d: Difficulty.easy);
      final now = DateTime(2026, 6, 1);
      r.onAnswered(progress: p, question: q, correct: false, now: now);
      r.onAnswered(progress: p, question: q, correct: true, now: now);
      // Interval grew, so it is no longer due today.
      expect(r.isDue(p.reviewQueue.first, now: now), isFalse);
      expect(p.reviewQueue.first.intervalDays, greaterThan(1));
    });
    test('repeated correct reviews eventually graduate the item out', () {
      final p = AppProgress();
      final q = _q('q1', d: Difficulty.easy);
      var now = DateTime(2026, 6, 1);
      r.onAnswered(progress: p, question: q, correct: false, now: now);
      for (var i = 0; i < 8 && p.reviewQueue.isNotEmpty; i++) {
        now = now.add(const Duration(days: 60)); // always due again
        r.onAnswered(progress: p, question: q, correct: true, now: now);
      }
      expect(p.reviewQueue, isEmpty);
    });
    test('due questions are ordered by urgency (priority on ties)', () {
      final p = AppProgress();
      r.onAnswered(
        progress: p,
        question: _q('easy', d: Difficulty.easy),
        correct: false,
      );
      r.onAnswered(
        progress: p,
        question: _q('hard', d: Difficulty.hard),
        correct: false,
      );
      final due = r.dueQuestionIds(p);
      expect(due.first, 'hard'); // higher difficulty -> higher initial priority
    });
  });

  group('UnlockEngine', () {
    const u = UnlockEngine();
    final bundle = ContentBundle(
      exam: const Exam(
        id: 'sat',
        name: 'SAT',
        displayName: 'SAT',
        enabled: true,
        contentVersion: '1.0.0',
        description: 'd',
        domains: ['math'],
      ),
      skillMap: SkillMap(domains: const []),
      lessons: [
        _lesson('l1'),
        _lesson('l2', prereq: ['l1']),
      ],
      questions: [_q('q1')],
    );

    test('lesson with no prerequisites is unlocked', () {
      expect(u.isUnlocked(_lesson('l1'), AppProgress()), isTrue);
    });
    test('lesson with an incomplete prerequisite is locked', () {
      expect(
        u.isUnlocked(_lesson('l2', prereq: ['l1']), AppProgress()),
        isFalse,
      );
    });
    test('completing the prerequisite unlocks the next lesson', () {
      final p = AppProgress();
      p.lessonProgress('l1').completed = true;
      expect(u.isUnlocked(_lesson('l2', prereq: ['l1']), p), isTrue);
    });
    test('unlock_xp gates a lesson', () {
      final locked = _lesson('l3', unlockXp: 100);
      expect(u.isUnlocked(locked, AppProgress()), isFalse);
      final p = AppProgress()..game.totalXp = 120;
      expect(u.isUnlocked(locked, p), isTrue);
    });
    test('suggestNext returns the first incomplete unlocked lesson', () {
      final next = u.suggestNext(bundle, AppProgress());
      expect(next!.id, 'l1');
    });
  });
}
