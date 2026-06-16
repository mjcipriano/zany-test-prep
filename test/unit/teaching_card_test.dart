import 'package:flutter_test/flutter_test.dart';
import 'package:zany_test_prep/domain/models/lesson.dart';

void main() {
  test('legacy single card renders as one screen', () {
    final card = TeachingCard.fromJson({
      'title': 'Solving Linear Equations',
      'body': 'Undo operations to isolate the variable, keeping both sides equal.',
      'key_points': ['Same op both sides', 'Constants then coefficient'],
      'worked_example': '3x + 5 = 20 → x = 5',
    });
    expect(card.screens, hasLength(1));
    expect(card.screens.single.title, 'Solving Linear Equations');
    expect(card.screens.single.keyPoints, hasLength(2));
    expect(card.screens.single.workedExample, contains('x = 5'));
  });

  test('multi-screen card parses each screen in order', () {
    final card = TeachingCard.fromJson({
      'title': 'Central Ideas',
      'body': 'How to find the main idea of a passage and avoid detail traps.',
      'key_points': ['Read for the point'],
      'screens': [
        {
          'title': 'What is a main idea?',
          'body': 'The single biggest point the whole passage supports.',
          'key_points': ['Not one detail', 'The umbrella over the details'],
        },
        {
          'title': 'How to find it',
          'body': 'Summarize each part in a few words, then ask what they share.',
          'worked_example': 'Topic sentences usually point at it.',
        },
      ],
    });
    expect(card.screens, hasLength(2));
    expect(card.screens[0].title, 'What is a main idea?');
    expect(card.screens[0].keyPoints, hasLength(2));
    expect(card.screens[1].title, 'How to find it');
    expect(card.screens[1].workedExample, isNotNull);
  });
}
