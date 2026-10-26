import 'package:flutter/material.dart';
import 'package:flutter_test/flutter_test.dart';
import 'package:zany_test_prep/domain/models/question.dart';
import 'package:zany_test_prep/features/lessons/passage_panel.dart';
import 'package:zany_test_prep/features/lessons/question_view.dart';

/// [n] paragraphs of ~[words] words each, blank-line separated.
String _text(String tag, {int n = 7, int words = 105}) => [
  for (var p = 1; p <= n; p++)
    [
      '$tag-p$p-start',
      for (var w = 0; w < words - 2; w++) 'word',
      '$tag-p$p-end.',
    ].join(' '),
].join('\n\n');

Question _question({
  String id = 'q1',
  String prompt = 'Which choice best states the main idea of the passage?',
  Map<String, dynamic>? stimulus,
}) => Question.fromJson({
  'question_id': id,
  'exam_id': 'act',
  'domain': 'reading',
  'section': 's',
  'skill': 'main_idea',
  'lesson_id': 'l',
  'difficulty': 'medium',
  'question_type': 'passage_reading',
  'estimated_time_seconds': 75,
  'prompt': prompt,
  'explanation': 'Because.',
  'tags': ['reading', 'passage-set:night-ferry'],
  'stimulus':
      stimulus ??
      {
        'type': 'passage',
        'title': 'Literary Narrative: Night Ferry',
        'text': _text('a'),
      },
  'choices': [
    for (final id in ['A', 'B', 'C', 'D'])
      {'id': id, 'text': 'Option $id', 'rationale': 'r'},
  ],
  'correct_choice': 'B',
});

Future<void> _pump(WidgetTester tester, Question q) async {
  tester.view.physicalSize = const Size(360, 780);
  tester.view.devicePixelRatio = 1.0;
  addTearDown(tester.view.reset);
  await tester.pumpWidget(
    MaterialApp(
      home: Scaffold(
        body: QuestionView(
          question: q,
          answered: false,
          selectedChoiceId: null,
          textController: TextEditingController(),
          onSelectChoice: (_) {},
        ),
      ),
    ),
  );
  await tester.pump();
}

ScrollPosition _passageScroll(WidgetTester tester) => tester
    .state<ScrollableState>(
      find
          .descendant(
            of: find.byType(LongPassagePanel),
            matching: find.byType(Scrollable),
          )
          .first,
    )
    .position;

/// Drags inside the passage window (its own scroll view).
Future<void> _dragPassage(WidgetTester tester, double dy) => tester.dragFrom(
  tester.getCenter(find.byType(SingleChildScrollView)),
  Offset(0, dy),
);

void main() {
  test('stimulus word counts, paragraphs and set ids', () {
    final q = _question();
    expect(q.stimulus!.wordCount, 7 * 105);
    expect(q.stimulus!.isLongPassage, isTrue);
    expect(q.stimulus!.paragraphs, hasLength(7));
    expect(q.stimulus!.paragraphs.first, startsWith('a-p1-start'));
    expect(q.passageSetId, 'night-ferry');

    final short = _question(
      stimulus: {'type': 'passage', 'text': 'A short passage.\n\nTwo parts.'},
    );
    expect(short.stimulus!.isLongPassage, isFalse);
    expect(short.stimulus!.paragraphs, ['A short passage.', 'Two parts.']);
    final table = _question(
      stimulus: {
        'type': 'table',
        'text': _text('t'),
        'table': {
          'headers': ['x'],
          'rows': [
            ['1'],
          ],
        },
      },
    );
    expect(table.stimulus!.isLongPassage, isFalse);
  });

  testWidgets('a long passage sits in a capped, scrollable panel with the '
      'question visible below it on a phone', (tester) async {
    await _pump(tester, _question());

    expect(find.byType(LongPassagePanel), findsOneWidget);
    expect(find.text('Literary Narrative: Night Ferry'), findsOneWidget);
    // Paragraphs are numbered to match "paragraph N" references.
    expect(find.text('1'), findsOneWidget);
    expect(find.text('2'), findsOneWidget);
    expect(find.textContaining('735 words'), findsOneWidget);

    // The prompt and the first choice are on screen without scrolling.
    final prompt = tester.getRect(
      find.text('Which choice best states the main idea of the passage?'),
    );
    expect(prompt.bottom, lessThan(780));
    expect(tester.getRect(find.text('Option A')).top, lessThan(780));

    // The passage scrolls inside its own window, reaching the last paragraph.
    final pos = _passageScroll(tester);
    expect(pos.maxScrollExtent, greaterThan(0));
    await _dragPassage(tester, -20000);
    await tester.pumpAndSettle();
    expect(
      _passageScroll(tester).pixels,
      _passageScroll(tester).maxScrollExtent,
    );
    expect(find.textContaining('a-p7-end'), findsOneWidget);
    expect(tester.takeException(), isNull);
  });

  testWidgets('the expand button opens the whole passage full screen', (
    tester,
  ) async {
    await _pump(tester, _question());
    await tester.tap(find.byKey(const Key('passage-expand')));
    await tester.pumpAndSettle();
    final sheet = find.byKey(const Key('passage-sheet'));
    expect(sheet, findsOneWidget);
    expect(
      find.descendant(of: sheet, matching: find.textContaining('a-p1-start')),
      findsOneWidget,
    );
    await tester.tap(find.byTooltip('Back to the question'));
    await tester.pumpAndSettle();
    expect(sheet, findsNothing);
  });

  testWidgets('long paired passages are labelled Passage A and Passage B', (
    tester,
  ) async {
    await _pump(
      tester,
      _question(
        stimulus: {
          'type': 'paired_passages',
          'title': 'Social Science: When Should School Start?',
          'text': _text('a', n: 4, words: 90),
          'text_b': _text('b', n: 4, words: 90),
        },
      ),
    );
    expect(find.byType(LongPassagePanel), findsOneWidget);
    expect(find.text('Passage A'), findsOneWidget);
    await _dragPassage(tester, -20000);
    await tester.pumpAndSettle();
    expect(find.text('Passage B'), findsOneWidget);
    expect(find.textContaining('b-p4-end'), findsOneWidget);
  });

  testWidgets('short passages keep the inline card', (tester) async {
    await _pump(
      tester,
      _question(
        stimulus: {
          'type': 'passage',
          'title': 'Short',
          'text': 'An octopus has no bones.',
        },
      ),
    );
    expect(find.byType(LongPassagePanel), findsNothing);
    expect(find.text('An octopus has no bones.'), findsOneWidget);
  });

  testWidgets('the reading position is kept across questions on the same '
      'passage and reset for a new passage', (tester) async {
    await _pump(tester, _question(id: 'q1'));
    await _dragPassage(tester, -300);
    await tester.pumpAndSettle();
    final offset = _passageScroll(tester).pixels;
    expect(offset, greaterThan(0));

    await _pump(tester, _question(id: 'q2', prompt: 'What does “true” mean?'));
    expect(_passageScroll(tester).pixels, offset);

    await _pump(
      tester,
      _question(
        id: 'q3',
        stimulus: {'type': 'passage', 'title': 'Other', 'text': _text('z')},
      ),
    );
    expect(_passageScroll(tester).pixels, 0);
  });
}
