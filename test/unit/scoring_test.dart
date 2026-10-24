import 'package:flutter_test/flutter_test.dart';
import 'package:zany_test_prep/domain/models/exam.dart';
import 'package:zany_test_prep/domain/services/scoring.dart';

void main() {
  group('SAT scoring', () {
    const sat = ExamScoring(ScoringSpec(scale: ScoreScale.sat1600));

    test('section scores span 200-800 in steps of 10', () {
      expect(sat.sectionScore(0, 50), 200);
      expect(sat.sectionScore(50, 50), 800);
      expect(sat.sectionScore(25, 50), 500);
      expect(sat.sectionScore(13, 27) % 10, 0);
      expect(sat.sectionScore(0, 0), 200);
      expect(sat.sectionMin, 200);
      expect(sat.sectionMax, 800);
    });

    test('total is the sum of sections, out of 1600', () {
      expect(sat.composite({'reading_writing': 650, 'math': 700}), 1350);
      expect(sat.compositeMax(['reading_writing', 'math']), 1600);
      expect(sat.compositeCaption(['reading_writing', 'math']), 'Out of 1600');
      expect(sat.formatSection(650), '650');
    });
  });

  group('ACT scoring', () {
    const act = ExamScoring(
      ScoringSpec(
        scale: ScoreScale.act36,
        compositeDomains: ['english', 'math', 'reading'],
      ),
    );

    test('section scores span 1-36', () {
      expect(act.sectionScore(0, 40), 1);
      expect(act.sectionScore(40, 40), 36);
      expect(act.sectionScore(20, 40), 19);
      expect(act.sectionScore(0, 0), 1);
    });

    test(
      'composite averages only the composite domains (science excluded)',
      () {
        final scores = {'english': 30, 'math': 24, 'reading': 27, 'science': 1};
        expect(act.composite(scores), 27);
        expect(
          act.compositeDomains(['english', 'math', 'reading', 'science']),
          ['english', 'math', 'reading'],
        );
        expect(act.compositeMax(['english', 'math', 'reading', 'science']), 36);
        expect(act.compositeCaption(['english']), contains('1–36'));
      },
    );

    test('composite rounds to the nearest whole point', () {
      expect(act.composite({'english': 30, 'math': 31, 'reading': 31}), 31);
      expect(act.composite({'english': 30, 'math': 30, 'reading': 31}), 30);
    });

    test('missing composite domains fall back to the minimum', () {
      expect(act.composite({'science': 36}), 1);
    });
  });

  group('percent scoring', () {
    const pct = ExamScoring(ScoringSpec());

    test('reports accuracy percentages', () {
      expect(pct.sectionScore(3, 4), 75);
      expect(pct.composite({'a': 50, 'b': 100}), 75);
      expect(pct.formatSection(75), '75%');
      expect(pct.compositeMax(['a', 'b']), 100);
    });
  });
}
