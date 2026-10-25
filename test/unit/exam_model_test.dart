import 'package:flutter_test/flutter_test.dart';
import 'package:zany_test_prep/domain/models/exam.dart';

void main() {
  group('Exam.fromJson', () {
    test('parses timed test plan and scoring from exam.yaml fields', () {
      final exam = Exam.fromJson({
        'exam_id': 'act',
        'exam_name': 'ACT',
        'display_name': 'ACT',
        'tagline': 'English, Math, Reading & Science',
        'domains': ['english', 'math', 'reading', 'science'],
        'timed_test': {
          'intro': 'Four sections.',
          'modules': [
            {
              'name': 'English',
              'domain': 'english',
              'count': 50,
              'minutes': 35,
            },
            {'name': 'Math', 'domain': 'math', 'count': 45, 'minutes': 50},
          ],
        },
        'scoring': {
          'type': 'act_36',
          'composite_domains': ['english', 'math', 'reading'],
        },
      });
      expect(exam.tagline, 'English, Math, Reading & Science');
      expect(exam.timedTest.intro, 'Four sections.');
      expect(exam.timedTest.modules.length, 2);
      expect(exam.timedTest.modules.first.count, 50);
      expect(exam.timedTest.modules.first.minutes, 35);
      expect(exam.timedTest.totalQuestions, 95);
      expect(exam.timedTest.totalMinutes, 85);
      expect(exam.timedTest.domains, ['english', 'math']);
      expect(exam.scoring.scale, ScoreScale.act36);
      expect(exam.scoring.compositeDomains, ['english', 'math', 'reading']);
      expect(exam.scoring.compositeLabel, 'Estimated composite score');
    });

    test('falls back to one module per domain and percent scoring', () {
      final exam = Exam.fromJson({
        'exam_id': 'ap',
        'exam_name': 'AP',
        'domains': ['multiple_choice', 'free_response'],
      });
      expect(exam.displayName, 'AP');
      expect(exam.timedTest.modules.length, 2);
      expect(exam.timedTest.modules.first.name, 'Multiple Choice');
      expect(exam.timedTest.modules.first.domain, 'multiple_choice');
      expect(exam.timedTest.modules.first.count, 20);
      expect(exam.scoring.scale, ScoreScale.percent);
      expect(exam.scoring.compositeDomains, isEmpty);
    });

    test('an empty modules list also falls back to defaults', () {
      final exam = Exam.fromJson({
        'exam_id': 'x',
        'exam_name': 'X',
        'domains': ['a'],
        'timed_test': {'modules': []},
        'scoring': {'type': 'sat_1600'},
      });
      expect(exam.timedTest.modules.length, 1);
      expect(exam.scoring.scale, ScoreScale.sat1600);
      expect(exam.scoring.compositeLabel, 'Estimated total score');
    });

    test('unknown scoring type parses as percent', () {
      expect(ScoreScale.parse('bogus'), ScoreScale.percent);
      expect(ScoreScale.parse(null), ScoreScale.percent);
      expect(ScoreScale.parse('sat_1600'), ScoreScale.sat1600);
    });
  });

  group('content version label', () {
    test('shows the version plus a short fingerprint', () {
      final exam = Exam.fromJson({
        'exam_id': 'sat',
        'exam_name': 'SAT',
        'content_version': '2.1.0',
        'content_fingerprint': '413ec7ff14db4aac',
      });
      expect(exam.contentVersion, '2.1.0');
      expect(exam.contentFingerprint, '413ec7ff14db4aac');
      expect(exam.contentLabel, '2.1.0 · 413ec7f');
    });

    test('falls back to the bare version for older bundles', () {
      final exam = Exam.fromJson({'exam_id': 'x', 'exam_name': 'X'});
      expect(exam.contentVersion, '1.0.0');
      expect(exam.contentLabel, '1.0.0');
    });
  });

  group('ExamInfo.fromJson', () {
    test('accepts a bare id (legacy exams.json)', () {
      final info = ExamInfo.fromJson('sat');
      expect(info.id, 'sat');
      expect(info.name, 'SAT');
      expect(info.displayName, 'SAT');
      expect(info.tagline, '');
    });

    test('accepts a descriptor object', () {
      final info = ExamInfo.fromJson({
        'id': 'act',
        'name': 'ACT',
        'display_name': 'The ACT',
        'tagline': 'Four sections',
      });
      expect(info.id, 'act');
      expect(info.displayName, 'The ACT');
      expect(info.tagline, 'Four sections');
    });

    test('tolerates partial descriptors', () {
      final info = ExamInfo.fromJson({'exam_id': 'psat'});
      expect(info.id, 'psat');
      expect(info.name, 'PSAT');
      expect(info.displayName, 'PSAT');
    });
  });
}
