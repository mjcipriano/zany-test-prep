import 'package:flutter_test/flutter_test.dart';
import 'package:zany_test_prep/domain/models/exam.dart';
import 'package:zany_test_prep/domain/services/scoring.dart';

void main() {
  group('SAT scoring', () {
    const sat = ExamScoring(ScoringSpec(scale: ScoreScale.sat1600));
    const routes = SectionRoute.values;

    test('section scores span 200-800 in steps of 10', () {
      expect(sat.sectionScore(0, 50), 200);
      expect(sat.sectionScore(50, 50), 800);
      expect(sat.sectionScore(25, 50), 480);
      expect(sat.sectionScore(13, 27) % 10, 0);
      expect(sat.sectionScore(0, 0), 200);
      expect(sat.sectionMin, 200);
      expect(sat.sectionMax, 800);
    });

    test('every route is monotonic and within its bounds', () {
      for (final route in routes) {
        for (var total = 1; total <= 60; total++) {
          final table = sat.conversionTable(total, route: route);
          expect(table.length, total + 1);
          expect(table.first, 200, reason: '$route raw 0 of $total');
          expect(table.last, sat.sectionCeiling(route));
          for (var raw = 1; raw <= total; raw++) {
            expect(
              table[raw],
              greaterThanOrEqualTo(table[raw - 1]),
              reason: '$route $raw/$total',
            );
            expect(table[raw] % 10, 0);
            expect(table[raw], inInclusiveRange(200, 800));
          }
        }
      }
    });

    test('the easier route caps the section in the low 600s', () {
      for (var total = 1; total <= 60; total++) {
        for (var raw = 0; raw <= total; raw++) {
          expect(
            sat.sectionScore(raw, total, route: SectionRoute.easier),
            lessThanOrEqualTo(ExamScoring.satEasierCap),
          );
        }
      }
      expect(sat.sectionScore(54, 54, route: SectionRoute.easier), 640);
      expect(sat.sectionCeiling(SectionRoute.easier), 640);
    });

    test('only the harder route reaches 800, and it is worth more per '
        'question than the easier one', () {
      expect(sat.sectionScore(54, 54, route: SectionRoute.harder), 800);
      expect(sat.sectionCeiling(SectionRoute.harder), 800);
      for (var raw = 0; raw <= 54; raw++) {
        final easy = sat.sectionScore(raw, 54, route: SectionRoute.easier);
        final linear = sat.sectionScore(raw, 54);
        final hard = sat.sectionScore(raw, 54, route: SectionRoute.harder);
        expect(easy, lessThanOrEqualTo(linear), reason: 'raw $raw');
        expect(linear, lessThanOrEqualTo(hard), reason: 'raw $raw');
      }
    });

    test('the curve is nonlinear: flat at the floor, steep at the top', () {
      // Points gained over the first, a middle, and the last 10%.
      int gain(double from, double to) =>
          sat.sectionScore((to * 100).round(), 100) -
          sat.sectionScore((from * 100).round(), 100);
      expect(gain(0, 0.1), lessThan(gain(0.5, 0.6)));
      expect(gain(0.9, 1.0), greaterThan(gain(0.5, 0.6)));
    });

    test('interpolation hits the anchors and clamps outside them', () {
      expect(ExamScoring.interpolate(ExamScoring.satLinearCurve, 0.5), 480);
      expect(
        ExamScoring.interpolate(ExamScoring.satLinearCurve, 0.55),
        closeTo(510, 1e-9),
      );
      expect(ExamScoring.interpolate(ExamScoring.satLinearCurve, -1), 200);
      expect(ExamScoring.interpolate(ExamScoring.satLinearCurve, 2), 800);
    });

    test('anchor curves are strictly increasing in x and never decrease', () {
      for (final curve in [
        ExamScoring.satLinearCurve,
        ExamScoring.satHarderCurve,
        ExamScoring.satEasierCurve,
        ExamScoring.actCurve,
      ]) {
        expect(curve.first.$1, 0.0);
        expect(curve.last.$1, 1.0);
        for (var i = 1; i < curve.length; i++) {
          expect(curve[i].$1, greaterThan(curve[i - 1].$1));
          expect(curve[i].$2, greaterThanOrEqualTo(curve[i - 1].$2));
        }
      }
    });

    test('route parsing tolerates junk', () {
      expect(SectionRoute.parse('harder'), SectionRoute.harder);
      expect(SectionRoute.parse('easier'), SectionRoute.easier);
      expect(SectionRoute.parse(null), SectionRoute.linear);
      expect(SectionRoute.parse(42), SectionRoute.linear);
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
      expect(act.sectionScore(20, 40), 18);
      expect(act.sectionScore(0, 0), 1);
    });

    test('is monotonic, bounded, and ignores SAT routes', () {
      for (var total = 1; total <= 75; total++) {
        final table = act.conversionTable(total);
        expect(table.first, 1);
        expect(table.last, 36);
        for (var raw = 1; raw <= total; raw++) {
          expect(table[raw], greaterThanOrEqualTo(table[raw - 1]));
          expect(table[raw], inInclusiveRange(1, 36));
          for (final route in SectionRoute.values) {
            expect(act.sectionScore(raw, total, route: route), table[raw]);
          }
        }
      }
      expect(act.sectionCeiling(SectionRoute.easier), 36);
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
      expect(pct.sectionScore(3, 4, route: SectionRoute.easier), 75);
      expect(pct.composite({'a': 50, 'b': 100}), 75);
      expect(pct.formatSection(75), '75%');
      expect(pct.compositeMax(['a', 'b']), 100);
    });
  });
}
