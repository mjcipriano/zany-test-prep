import 'package:flutter_test/flutter_test.dart';
import 'package:zany_test_prep/domain/models/content_bundle.dart';
import 'package:zany_test_prep/domain/models/progress.dart';
import 'package:zany_test_prep/domain/services/badges.dart';
import 'package:zany_test_prep/domain/services/unlock_engine.dart';
import 'package:zany_test_prep/features/practice/sampling.dart';

Map<String, dynamic> _lesson(String id, String domain, int order) => {
  'lesson_id': id,
  'exam_id': 'act',
  'domain': domain,
  'section': 's',
  'skill': 'k',
  'title': id,
  'order': order,
  'difficulty': 'easy',
  'estimated_minutes': 5,
  'teaching_card': {
    'title': 't',
    'body': 'b',
    'key_points': ['a', 'b'],
  },
  'question_ids': const [],
  'prerequisite_lesson_ids': const [],
  'unlock_xp': 0,
  'tags': const ['x'],
};

ContentBundle _actBundle() => ContentBundle.fromJson({
  'exam': {
    'exam_id': 'act',
    'exam_name': 'ACT',
    'domains': ['english', 'math', 'reading', 'science'],
  },
  'skills': {
    'domains': [
      for (final d in ['english', 'math', 'reading', 'science'])
        {
          'id': d,
          'name': d == 'english' ? 'English' : d,
          'sections': [
            {
              'id': 's',
              'name': 's',
              'skills': [
                {'id': 'k', 'name': 'Skill K'},
              ],
            },
          ],
        },
    ],
  },
  'lessons': [
    _lesson('act-science-k-easy', 'science', 0),
    _lesson('act-math-k-easy', 'math', 1),
    _lesson('act-english-k-easy', 'english', 2),
    _lesson('act-reading-k-easy', 'reading', 3),
    _lesson('act-english-k-medium', 'english', 4),
  ],
  'questions': [
    for (final d in ['english', 'math', 'reading', 'science'])
      for (var i = 0; i < 3; i++)
        {
          'question_id': '$d-$i',
          'exam_id': 'act',
          'domain': d,
          'section': 's',
          'skill': 'k$i',
          'lesson_id': 'act-$d-k-easy',
          'difficulty': 'medium',
          'question_type': 'multiple_choice',
          'estimated_time_seconds': 30,
          'prompt': 'p',
          'explanation': 'e',
          'choices': [
            {'id': 'A', 'text': 'a', 'rationale': 'r'},
            {'id': 'B', 'text': 'b', 'rationale': 'r'},
          ],
          'correct_choice': 'A',
        },
  ],
});

void main() {
  group('ContentBundle domain helpers', () {
    test('domainIds follow the skill map order', () {
      final b = _actBundle();
      expect(b.domainIds, ['english', 'math', 'reading', 'science']);
      expect(b.domainIndex('science'), 3);
      expect(b.domainIndex('nope'), 4);
      expect(b.domainName('english'), 'English');
      expect(b.domainName('reading_writing'), 'Reading Writing');
    });
  });

  group('UnlockEngine.pathOrder', () {
    test('orders by exam domain order, then lesson order', () {
      final b = _actBundle();
      final ids = const UnlockEngine().pathOrder(b).map((l) => l.id).toList();
      expect(ids, [
        'act-english-k-easy',
        'act-english-k-medium',
        'act-math-k-easy',
        'act-reading-k-easy',
        'act-science-k-easy',
      ]);
      final next = const UnlockEngine().suggestNext(b, AppProgress());
      expect(next!.id, 'act-english-k-easy');
    });
  });

  group('Badges domain counting', () {
    test(
      'uses the bundle domain, so ACT english/reading/science count as verbal',
      () {
        final b = _actBundle();
        expect(Badges.lessonIsMath('act-math-k-easy', b), isTrue);
        expect(Badges.lessonIsMath('act-science-k-easy', b), isFalse);
        expect(Badges.lessonIsMath('act-english-k-easy', b), isFalse);
        // Unknown lesson ids fall back to the id convention.
        expect(Badges.lessonIsMath('sat-math-zzz-easy', b), isTrue);
        expect(Badges.lessonIsMath('sat-rw-zzz-easy', b), isFalse);
        expect(Badges.lessonIsMath('sat-rw-zzz-easy', null), isFalse);
      },
    );
  });

  group('Diagnostic interleave', () {
    test('round-robins one question per domain in exam order', () {
      final b = _actBundle();
      final picks = b.questions.toList();
      final out = interleaveByDomain(picks, b.domainIds, 8);
      expect(out.length, 8);
      expect(out.map((q) => q.domain).toList(), [
        'english',
        'math',
        'reading',
        'science',
        'english',
        'math',
        'reading',
        'science',
      ]);
    });

    test('stops when every domain is exhausted', () {
      final b = _actBundle();
      final out = interleaveByDomain(
        b.questions.where((q) => q.domain == 'math').toList(),
        b.domainIds,
        16,
      );
      expect(out.length, 3);
    });
  });
}
