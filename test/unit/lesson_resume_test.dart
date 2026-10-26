import 'dart:convert';

import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:flutter_test/flutter_test.dart';
import 'package:zany_test_prep/app/app_controller.dart';
import 'package:zany_test_prep/app/lesson_resume_controller.dart';
import 'package:zany_test_prep/data/local/key_value_store.dart';
import 'package:zany_test_prep/data/repositories/progress_repository.dart';
import 'package:zany_test_prep/domain/models/backup.dart';
import 'package:zany_test_prep/domain/models/difficulty.dart';
import 'package:zany_test_prep/domain/models/lesson_resume.dart';
import 'package:zany_test_prep/domain/models/progress.dart';
import 'package:zany_test_prep/domain/models/question.dart';
import 'package:zany_test_prep/domain/services/game_service.dart';

import '../helpers/pump_app.dart';

Question _q(String id, {String prompt = 'What is 2 + 2?', String key = 'B'}) =>
    Question(
      id: id,
      examId: 'sat',
      domain: 'math',
      section: 'math',
      skill: 'arith',
      lessonId: 'l1',
      difficulty: Difficulty.easy,
      type: QuestionType.multipleChoice,
      estimatedTimeSeconds: 60,
      prompt: prompt,
      explanation: '',
      tags: const [],
      choices: const [
        Choice(id: 'A', text: '3', rationale: ''),
        Choice(id: 'B', text: '4', rationale: ''),
      ],
      correctChoice: key,
    );

final _questions = [_q('q1'), _q('q2'), _q('q3'), _q('q4')];

LessonResume _resume({
  String examId = 'sat',
  String lessonId = 'l1',
  List<Question>? questions,
  int index = 2,
  int answers = 2,
  DateTime? updatedAt,
}) {
  final qs = questions ?? _questions;
  return LessonResume(
    examId: examId,
    lessonId: lessonId,
    fingerprint: lessonFingerprint(lessonId, qs),
    total: qs.length,
    attempt: LessonAttempt(
      teachingDone: true,
      index: index,
      answers: [
        for (var i = 0; i < answers; i++)
          SavedAnswer(
            questionId: qs[i].id,
            correct: i.isEven,
            responseMs: 1000 + i,
            choiceId: i.isEven ? 'B' : 'A',
          ),
      ],
      startedAt: DateTime(2026, 10, 1, 9, 30),
    ),
    updatedAt: updatedAt ?? DateTime(2026, 10, 1, 9, 35),
  );
}

void main() {
  group('LessonResume model', () {
    test('round-trips through the repository (fresh launch)', () async {
      final store = MemoryStore();
      final saved = _resume(index: 2, answers: 3);
      await ProgressRepository(
        store,
      ).saveLessonResume(const LessonResumeBook().put(saved));

      final loaded = ProgressRepository(
        store,
      ).loadLessonResume().get('sat', 'l1')!;
      expect(loaded.fingerprint, saved.fingerprint);
      expect(loaded.total, 4);
      expect(loaded.attempt.teachingDone, isTrue);
      expect(loaded.attempt.index, 2);
      expect(loaded.attempt.startedAt, DateTime(2026, 10, 1, 9, 30));
      expect(loaded.updatedAt, DateTime(2026, 10, 1, 9, 35));
      expect(loaded.attempt.answers.map((a) => a.questionId), [
        'q1',
        'q2',
        'q3',
      ]);
      expect(loaded.attempt.answers.map((a) => a.correct), [true, false, true]);
      expect(loaded.attempt.answers[1].choiceId, 'A');
      expect(loaded.attempt.answers[1].responseMs, 1001);
      expect(loaded.attempt.showingFeedback, isTrue);
      expect(loaded.resumeQuestionNumber, 3);
      expect(loaded.isValidFor('l1', _questions), isTrue);
    });

    test('grid-in answers keep the typed text', () {
      const a = SavedAnswer(questionId: 'q9', correct: true, produced: '3/4');
      final back = SavedAnswer.fromJson(jsonDecode(jsonEncode(a.toJson())))!;
      expect(back.produced, '3/4');
      expect(back.choiceId, isNull);
    });

    test('the stored document stays small', () {
      final book = const LessonResumeBook().put(_resume(index: 3, answers: 3));
      expect(jsonEncode(book.toJson()).length, lessThan(600));
    });

    test('keys are per exam, so an exam switch never crosses over', () {
      final book = const LessonResumeBook()
          .put(_resume(examId: 'sat'))
          .put(_resume(examId: 'act', index: 1, answers: 1));
      expect(book.get('sat', 'l1')!.attempt.index, 2);
      expect(book.get('act', 'l1')!.attempt.index, 1);
      expect(book.remove('act', 'l1').get('sat', 'l1'), isNotNull);
      expect(book.remove('act', 'l1').get('act', 'l1'), isNull);
    });

    test('keeps at most kMaxSavedLessons, dropping the oldest', () {
      var book = const LessonResumeBook();
      for (var i = 0; i < kMaxSavedLessons + 3; i++) {
        book = book.put(
          _resume(
            lessonId: 'l$i',
            updatedAt: DateTime(2026, 1, 1).add(Duration(minutes: i)),
          ),
        );
      }
      expect(book.entries.length, kMaxSavedLessons);
      expect(book.get('sat', 'l0'), isNull);
      expect(book.get('sat', 'l2'), isNull);
      expect(book.get('sat', 'l3'), isNotNull);
    });
  });

  group('stale content is discarded', () {
    test('fingerprint is stable and order-sensitive', () {
      expect(
        lessonFingerprint('l1', _questions),
        lessonFingerprint('l1', [_q('q1'), _q('q2'), _q('q3'), _q('q4')]),
      );
      expect(
        lessonFingerprint('l1', _questions),
        isNot(lessonFingerprint('l1', _questions.reversed.toList())),
      );
      expect(lessonFingerprint('l1', _questions), hasLength(8));
    });

    test('changed questions invalidate the saved attempt', () {
      final saved = _resume();
      // A question swapped out.
      expect(
        saved.isValidFor('l1', [_q('q1'), _q('qX'), _q('q3'), _q('q4')]),
        isFalse,
      );
      // A question added.
      expect(saved.isValidFor('l1', [..._questions, _q('q5')]), isFalse);
      // Same ids, but the answer key changed.
      expect(
        saved.isValidFor('l1', [_q('q1', key: 'A'), ..._questions.skip(1)]),
        isFalse,
      );
      // Same ids, reworded prompt.
      expect(
        saved.isValidFor('l1', [
          _q('q1', prompt: 'New?'),
          ..._questions.skip(1),
        ]),
        isFalse,
      );
      expect(saved.isValidFor('l1', _questions), isTrue);
    });

    test('inconsistent saved data is never resumed', () {
      expect(
        _resume(index: 2, answers: 0).isValidFor('l1', _questions),
        isFalse,
      );
      expect(
        _resume(index: 4, answers: 4).isValidFor('l1', _questions),
        isFalse,
      );
      expect(
        _resume(index: 1, answers: 1).isValidFor('l2', _questions),
        isFalse,
      );
    });
  });

  group('backward compatibility and resilience', () {
    test('an existing install without the key loads an empty book', () async {
      final store = MemoryStore();
      final progress = AppProgress()..game.totalXp = 77;
      await ProgressRepository(store).saveProgress(progress);
      final repo = ProgressRepository(store);
      expect(repo.loadLessonResume().isEmpty, isTrue);
      expect(repo.loadProgress().game.totalXp, 77);
    });

    test('corrupt JSON loads an empty book', () {
      final store = MemoryStore()..setString('lessonResume.v1', '{nope');
      expect(ProgressRepository(store).loadLessonResume().isEmpty, isTrue);
    });

    test('a corrupt entry is skipped; others survive', () {
      final good = _resume().toJson();
      final store = MemoryStore()
        ..setString(
          'lessonResume.v1',
          jsonEncode({
            'schema': 1,
            'lessons': [
              good,
              42,
              {'exam': 'sat'},
              {'exam': 'sat', 'lesson': 'l9', 'index': 'x', 'answers': 'bad'},
            ],
          }),
        );
      final book = ProgressRepository(store).loadLessonResume();
      expect(book.get('sat', 'l1')!.isValidFor('l1', _questions), isTrue);
      // Wrong types degrade to defaults and then fail validation, not parse.
      expect(book.get('sat', 'l9')!.isValidFor('l9', _questions), isFalse);
      expect(book.entries.length, 2);
    });

    test('reset and backup import clear in-progress lessons', () async {
      final store = MemoryStore();
      final repo = ProgressRepository(store);
      final book = const LessonResumeBook().put(_resume());
      await repo.saveLessonResume(book);
      await repo.resetAll();
      expect(store.getString('lessonResume.v1'), isNull);
      await repo.saveLessonResume(book);
      expect(store.getString('lessonResume.v1'), isNotNull);
      await repo.writeBackup(
        BackupData(profile: null, progress: AppProgress(), onboarded: true),
      );
      expect(store.getString('lessonResume.v1'), isNull);
    });
  });

  group('finishing', () {
    test(
      'completeLesson clears the saved attempt before granting XP once',
      () async {
        final store = MemoryStore();
        final container = ProviderContainer(overrides: testOverrides(store));
        addTearDown(container.dispose);
        final controller = container.read(appControllerProvider.notifier);
        await container.read(appControllerProvider.future);
        await controller.completeOnboarding(
          examId: 'sat',
          dailyGoalMinutes: 10,
        );
        final bundle = container
            .read(appControllerProvider)
            .requireValue
            .bundle;
        final lesson = bundle.lessons.first;
        final questions = bundle.questionsFor(lesson);

        final resume = container.read(lessonResumeProvider.notifier);
        await container.read(lessonResumeProvider.future);
        await resume.save(
          LessonResume(
            examId: 'sat',
            lessonId: lesson.id,
            fingerprint: lessonFingerprint(lesson.id, questions),
            total: questions.length,
            attempt: LessonAttempt(
              teachingDone: true,
              index: 1,
              answers: [
                SavedAnswer(questionId: questions[0].id, correct: true),
              ],
              startedAt: DateTime.now(),
            ),
            updatedAt: DateTime.now(),
          ),
        );
        expect(store.getString('lessonResume.v1'), isNotNull);

        final outcome = await controller.completeLesson(
          lesson: lesson,
          results: [
            for (final q in questions) AnswerResult(question: q, correct: true),
          ],
        );
        expect(
          container.read(lessonResumeProvider).requireValue.isEmpty,
          isTrue,
        );
        expect(store.getString('lessonResume.v1'), isNull);
        final data = container.read(appControllerProvider).requireValue;
        expect(data.progress.lessons[lesson.id]!.timesCompleted, 1);
        expect(data.progress.game.totalXp, outcome.xpGained);
        expect(outcome.xpGained, greaterThan(0));
      },
    );

    test('resetProgress forgets in-progress lessons in memory too', () async {
      final store = MemoryStore();
      final container = ProviderContainer(overrides: testOverrides(store));
      addTearDown(container.dispose);
      await container.read(appControllerProvider.future);
      await container.read(lessonResumeProvider.future);
      await container.read(lessonResumeProvider.notifier).save(_resume());
      await container.read(appControllerProvider.notifier).resetProgress();
      final book = await container.read(lessonResumeProvider.future);
      expect(book.isEmpty, isTrue);
    });
  });
}
