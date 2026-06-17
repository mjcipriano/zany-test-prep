import 'package:flutter/material.dart';
import 'package:flutter_test/flutter_test.dart';
import 'package:zany_test_prep/features/lessons/figure_view.dart';

Future<void> _pump(WidgetTester tester, Map<String, dynamic> figure) async {
  await tester.pumpWidget(
    MaterialApp(home: Scaffold(body: Center(child: FigureView(figure: figure)))),
  );
  await tester.pump();
}

void main() {
  final figures = <String, Map<String, dynamic>>{
    'right_triangle': {
      'kind': 'right_triangle',
      'caption': 'Right triangle',
      'angle': 'θ',
      'labels': {'a': '3', 'b': '4', 'c': '5'},
    },
    'rect': {
      'kind': 'rect',
      'labels': {'w': '8', 'h': '3'},
    },
    'circle': {
      'kind': 'circle',
      'sector': 90,
      'labels': {'r': '6', 'angle': '90°'},
    },
    'box': {
      'kind': 'box',
      'labels': {'l': '4', 'w': '3', 'h': '2'},
    },
    'cylinder': {
      'kind': 'cylinder',
      'labels': {'r': '3', 'h': '5'},
    },
    'scatter': {
      'kind': 'scatter',
      'points': [
        [1, 5],
        [3, 11],
        [6, 20],
        [9, 30],
      ],
      'line': {'m': 3, 'b': 2},
      'xlabel': 'x',
    },
  };

  figures.forEach((kind, spec) {
    testWidgets('FigureView renders $kind without error', (tester) async {
      await _pump(tester, spec);
      expect(find.byType(FigureView), findsOneWidget);
      expect(tester.takeException(), isNull);
    });
  });

  testWidgets('unknown figure kind renders nothing but does not crash', (
    tester,
  ) async {
    await _pump(tester, {'kind': 'totally_unknown'});
    expect(tester.takeException(), isNull);
  });
}
