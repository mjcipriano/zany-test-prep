import '../models/question.dart';

/// Checks user answers against the correct answer for any question type.
class AnswerChecker {
  const AnswerChecker();

  /// True if [choiceId] is the correct multiple-choice option.
  bool checkChoice(Question q, String? choiceId) {
    if (choiceId == null) return false;
    return choiceId == q.correctChoice;
  }

  /// True if [input] is an acceptable student-produced (grid-in) answer.
  ///
  /// Accepts: exact matches against the `accepted` list (whitespace-trimmed),
  /// numeric values within tolerance, and equivalent fractions/decimals.
  bool checkProduced(Question q, String input) {
    final ans = q.answer;
    if (ans == null) return false;
    final cleaned = input.trim();
    if (cleaned.isEmpty) return false;

    // Exact accepted-string match (covers string answers and canonical forms).
    for (final a in ans.accepted) {
      if (a.trim() == cleaned) return true;
    }
    if (!ans.isNumeric) return false;

    final parsed = parseNumeric(cleaned);
    if (parsed == null) return false;

    // Compare against the numeric value (and any numeric accepted forms).
    final targets = <double>[];
    if (ans.value != null) targets.add(ans.value!.toDouble());
    for (final a in ans.accepted) {
      final p = parseNumeric(a);
      if (p != null) targets.add(p);
    }
    final tol = ans.tolerance > 0 ? ans.tolerance : 1e-6;
    for (final t in targets) {
      if ((parsed - t).abs() <= tol) return true;
    }
    return false;
  }

  /// True regardless of question type — convenience for the lesson engine.
  bool isCorrect(Question q, {String? choiceId, String? produced}) {
    if (q.type.isStudentProduced) {
      return checkProduced(q, produced ?? '');
    }
    return checkChoice(q, choiceId);
  }

  /// Parses a number from "12", "-3.5", or a fraction like "3/4".
  static double? parseNumeric(String s) {
    final t = s.trim().replaceAll('−', '-');
    if (t.isEmpty) return null;
    final slash = t.indexOf('/');
    if (slash > 0) {
      final num = double.tryParse(t.substring(0, slash).trim());
      final den = double.tryParse(t.substring(slash + 1).trim());
      if (num == null || den == null || den == 0) return null;
      return num / den;
    }
    // Strip a trailing percent sign if present.
    final pct = t.endsWith('%');
    final core = pct ? t.substring(0, t.length - 1).trim() : t;
    final v = double.tryParse(core);
    return v;
  }
}
