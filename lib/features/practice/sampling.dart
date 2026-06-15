import 'dart:math';

import '../../domain/models/question.dart';

/// Returns up to [count] questions from [pool], balanced ~50/50 between Math and
/// Reading & Writing so all-section quizzes don't skew toward whichever domain
/// has more questions. Falls back to whatever is available if one side is short.
List<Question> balancedSample(List<Question> pool, int count, Random rng) {
  final math = <Question>[];
  final rw = <Question>[];
  for (final q in pool) {
    (q.domain == 'math' ? math : rw).add(q);
  }
  math.shuffle(rng);
  rw.shuffle(rng);
  final out = <Question>[];
  var i = 0, j = 0;
  // Alternate domains; if one runs out, draw from the other.
  while (out.length < count && (i < math.length || j < rw.length)) {
    final pickMath = out.length.isEven;
    if (pickMath && i < math.length) {
      out.add(math[i++]);
    } else if (!pickMath && j < rw.length) {
      out.add(rw[j++]);
    } else if (i < math.length) {
      out.add(math[i++]);
    } else if (j < rw.length) {
      out.add(rw[j++]);
    }
  }
  return out;
}
