import 'dart:io';

import 'package:flutter_test/flutter_test.dart';
import 'package:zany_test_prep/data/repositories/content_repository.dart';
import 'package:zany_test_prep/domain/models/question.dart';

/// Loads the real committed bundle and asserts the app can parse all content
/// without runtime errors, plus structural guarantees the content must satisfy.
void main() {
  test('the SAT bundle parses and meets content requirements', () async {
    final repo = ContentRepository(reader: (path) => File(path).readAsString());
    final bundle = await repo.loadBundle('sat');

    expect(bundle.exam.id, 'sat');
    expect(bundle.lessons.length, greaterThanOrEqualTo(50));
    expect(bundle.questions.length, greaterThanOrEqualTo(1000));

    final math = bundle.questions.where((q) => q.domain == 'math').length;
    final rw = bundle.questions
        .where((q) => q.domain == 'reading_writing')
        .length;
    expect(math, greaterThanOrEqualTo(500));
    expect(rw, greaterThanOrEqualTo(500));

    // Every lesson resolves all of its questions and has 8-25 of them.
    for (final lesson in bundle.lessons) {
      final qs = bundle.questionsFor(lesson);
      expect(
        qs.length,
        lesson.questionIds.length,
        reason: 'lesson ${lesson.id} has unresolved question ids',
      );
      expect(qs.length, inInclusiveRange(8, 25));
      expect(lesson.teachingCard.body.isNotEmpty, isTrue);
    }

    // Every question has a usable answer and explanation.
    for (final q in bundle.questions) {
      expect(q.explanation.trim().isNotEmpty, isTrue);
      if (q.type == QuestionType.studentProduced) {
        expect(q.answer, isNotNull);
        expect(q.answer!.accepted, isNotEmpty);
      } else {
        expect(q.choices.length, greaterThanOrEqualTo(2));
        expect(
          q.correct,
          isNotNull,
          reason: 'question ${q.id} has no correct choice',
        );
        for (final c in q.choices) {
          expect(c.rationale.trim().isNotEmpty, isTrue);
        }
      }
    }
  });

  test(
    'skills form independent difficulty tracks (per-skill prerequisites)',
    () async {
      final repo = ContentRepository(
        reader: (path) => File(path).readAsString(),
      );
      final bundle = await repo.loadBundle('sat');
      final byId = {for (final l in bundle.lessons) l.id: l};

      // Many skills each have a first lesson with no prerequisites, so the learner
      // can start any subject area without finishing another first.
      final openers = bundle.lessons
          .where((l) => l.prerequisiteLessonIds.isEmpty)
          .toList();
      final openerSkills = openers.map((l) => l.skill).toSet();
      expect(
        openerSkills.length,
        greaterThanOrEqualTo(20),
        reason: 'most skills should be independently startable',
      );

      // Every prerequisite is a lesson of the SAME skill (independent tracks).
      for (final l in bundle.lessons) {
        for (final pre in l.prerequisiteLessonIds) {
          expect(byId[pre], isNotNull);
          expect(
            byId[pre]!.skill,
            l.skill,
            reason: '${l.id} should only depend on its own skill',
          );
        }
      }
    },
  );
}
