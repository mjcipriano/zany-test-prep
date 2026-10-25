import 'dart:convert';
import 'dart:io';

import 'package:flutter_test/flutter_test.dart';
import 'package:zany_test_prep/data/repositories/content_repository.dart';
import 'package:zany_test_prep/domain/models/exam.dart';
import 'package:zany_test_prep/domain/models/question.dart';

/// Loads the committed ACT bundle and checks the guarantees the app relies on.
void main() {
  test(
    'the ACT bundle parses, covers four domains, and uses ACT formats',
    () async {
      final repo = ContentRepository(
        reader: (path) => File(path).readAsString(),
      );
      final bundle = await repo.loadBundle('act');

      expect(bundle.exam.id, 'act');
      // Content is versioned: the bundle's version and fingerprint must match
      // content/exams/act/content.lock.json (tools/build_bundle.py keeps them in sync).
      final lock =
          jsonDecode(
                File('content/exams/act/content.lock.json').readAsStringSync(),
              )
              as Map<String, dynamic>;
      expect(bundle.exam.contentVersion, lock['content_version']);
      expect(bundle.exam.contentFingerprint, lock['fingerprint']);
      expect(bundle.exam.contentVersion, isNot('1.0.0'));
      expect(bundle.domainIds, ['english', 'math', 'reading', 'science']);
      expect(bundle.exam.scoring.scale, ScoreScale.act36);
      expect(bundle.exam.timedTest.modules.map((m) => m.domain).toList(), [
        'english',
        'math',
        'reading',
        'science',
      ]);
      expect(bundle.lessons.length, greaterThanOrEqualTo(36));
      expect(bundle.questions.length, greaterThanOrEqualTo(1000));
      for (final d in bundle.domainIds) {
        expect(
          bundle.questions.where((q) => q.domain == d).length,
          greaterThanOrEqualTo(d == 'reading' ? 150 : 250),
          reason: 'domain $d',
        );
        expect(bundle.lessonsForDomain(d), isNotEmpty, reason: 'domain $d');
      }

      // The ACT has no grid-ins; its math items carry 5 choices (most) and every
      // item resolves to exactly one correct choice.
      var fiveChoiceMath = 0, mathTotal = 0, noChange = 0;
      for (final q in bundle.questions) {
        expect(q.type, isNot(QuestionType.studentProduced), reason: q.id);
        expect(q.correct, isNotNull, reason: q.id);
        if (q.domain == 'math') {
          mathTotal++;
          if (q.choices.length == 5) fiveChoiceMath++;
        }
        if (q.domain == 'english' && q.choices.first.text == 'NO CHANGE') {
          noChange++;
        }
      }
      expect(fiveChoiceMath / mathTotal, greaterThan(0.6));
      expect(noChange, greaterThan(100));

      // Science items come with data: a table, passage, or figure.
      final science = bundle.questions.where((q) => q.domain == 'science');
      expect(
        science.where((q) => q.stimulus != null).length / science.length,
        greaterThan(0.9),
      );

      for (final lesson in bundle.lessons) {
        expect(
          bundle.questionsFor(lesson).length,
          lesson.questionIds.length,
          reason: lesson.id,
        );
        expect(lesson.teachingCard.screens.length, greaterThanOrEqualTo(1));
      }
    },
  );
}
