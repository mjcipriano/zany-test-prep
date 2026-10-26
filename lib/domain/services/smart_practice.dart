import 'dart:math';

import '../models/content_bundle.dart';
import '../models/difficulty.dart';
import '../models/progress.dart';
import '../models/question.dart';
import 'adaptive_difficulty.dart';
import 'recommendation_engine.dart';

/// An adaptive "Smart practice" session.
///
/// **Which skills:** the top [maxSkills] unlocked skills from
/// [RecommendationEngine.rankSkills] (weak, uncertain, due for review, not
/// just practiced, under-practiced domain). Slots are shared out in proportion
/// to each skill's score; a [focusSkill] (e.g. the one the Home card names)
/// gets half the session. The order avoids the same skill twice in a row when
/// there is any alternative.
///
/// **Which difficulty:** each skill starts at [AdaptiveDifficulty.forMastery]
/// (~70% expected correct), shifted by a session-wide [DifficultyStaircase]:
/// two right in a row step harder, a miss steps easier.
///
/// **Which question:** unseen questions first, then the least-attempted, with
/// random tie-breaks from the injected [Random]; never repeated in a session.
/// If a difficulty has run dry the nearest one (easier first) is used.
///
/// [questions] has a fixed length. Slot `i + 1` is (re)picked when
/// [record] reports the answer to slot `i`, so the player can show it next.
class SmartPracticeSession {
  SmartPracticeSession._({
    required this.skillPlan,
    required Map<String, Difficulty> baseDifficulty,
    required Map<String, List<Question>> pools,
    required AppProgress progress,
    required Random rng,
    required this.staircase,
  }) : _base = baseDifficulty,
       _pools = pools,
       _progress = progress,
       _rng = rng;

  /// Plans a session of up to [count] questions.
  factory SmartPracticeSession.plan({
    required ContentBundle bundle,
    required AppProgress progress,
    required DateTime now,
    required Random rng,
    int count = 12,
    String? focusSkill,
    int maxSkills = 4,
    RecommendationEngine recommender = const RecommendationEngine(),
    AdaptiveDifficulty adaptive = const AdaptiveDifficulty(),
    DifficultyStaircase? staircase,
  }) {
    final ranked = recommender.rankSkills(bundle, progress, now: now);
    final chosen = <SkillScore>[];
    final focus = ranked.where((s) => s.skillId == focusSkill).firstOrNull;
    if (focus != null) chosen.add(focus);
    for (final s in ranked) {
      if (chosen.length >= maxSkills) break;
      if (s.skillId != focus?.skillId) chosen.add(s);
    }

    final pools = <String, List<Question>>{
      for (final s in chosen) s.skillId: [],
    };
    for (final q in bundle.questions) {
      pools[q.skill]?.add(q);
    }
    chosen.removeWhere((s) => pools[s.skillId]!.isEmpty);

    final plan = planSkills(
      [for (final s in chosen) (s.skillId, s.score)],
      count,
      focusSkill: focus == null ? null : focusSkill,
    );
    final session = SmartPracticeSession._(
      skillPlan: plan,
      baseDifficulty: {
        for (final s in chosen) s.skillId: adaptive.forMastery(s.mastery),
      },
      pools: pools,
      progress: progress,
      rng: rng,
      staircase: staircase ?? DifficultyStaircase(),
    );
    session._fillAll();
    return session;
  }

  /// The skill for each slot, in play order.
  final List<String> skillPlan;
  final DifficultyStaircase staircase;
  final Map<String, Difficulty> _base;
  final Map<String, List<Question>> _pools;
  final AppProgress _progress;
  final Random _rng;

  late final List<Question> questions;
  final Set<String> _used = {};
  int _answered = 0;

  /// Mastery-based starting difficulty for [skill].
  Difficulty baseFor(String skill) => _base[skill] ?? Difficulty.easy;

  /// The difficulty a new question for [skill] gets right now.
  Difficulty difficultyFor(String skill) => staircase.apply(baseFor(skill));

  void _fillAll() {
    final out = <Question>[];
    for (final skill in skillPlan) {
      final q = _pick(skill, difficultyFor(skill));
      if (q == null) break;
      out.add(q);
    }
    questions = List.of(out, growable: false);
  }

  /// Reports the answer to slot [index] (in order) and re-picks the next slot
  /// at the stepped difficulty. Out-of-order or repeated calls are ignored.
  void record(int index, bool correct) {
    if (index != _answered || index >= questions.length) return;
    _answered += 1;
    staircase.record(correct);
    final next = index + 1;
    if (next >= questions.length) return;
    final skill = skillPlan[next];
    final want = difficultyFor(skill);
    if (questions[next].difficulty == want) return;
    final old = questions[next];
    _used.remove(old.id);
    final q = _pick(skill, want);
    questions[next] = q ?? old;
    _used.add(questions[next].id);
  }

  Question? _pick(String skill, Difficulty want) {
    final pool = _pools[skill] ?? const [];
    // Nearest difficulty first; on a tie the easier one.
    final order = [...Difficulty.values]
      ..sort((a, b) {
        final da = (a.index - want.index).abs();
        final db = (b.index - want.index).abs();
        return da != db ? da.compareTo(db) : a.index.compareTo(b.index);
      });
    for (final d in order) {
      final group = <Question>[];
      var fewest = 1 << 30;
      for (final q in pool) {
        if (q.difficulty != d || _used.contains(q.id)) continue;
        final n = _progress.questionStats[q.id]?.attempts ?? 0;
        if (n < fewest) {
          fewest = n;
          group.clear();
        }
        if (n == fewest) group.add(q);
      }
      if (group.isNotEmpty) {
        final q = group[_rng.nextInt(group.length)];
        _used.add(q.id);
        return q;
      }
    }
    return null;
  }

  /// Shares [count] slots between [skills] (id, score) and orders them.
  ///
  /// A [focusSkill] gets `ceil(count / 2)` slots; the rest are split in
  /// proportion to score (largest remainder, ties to the earlier skill). The
  /// order is greedy: the skill with the most slots left goes next, skipping
  /// the previous slot's skill whenever another skill still has slots.
  static List<String> planSkills(
    List<(String, double)> skills,
    int count, {
    String? focusSkill,
  }) {
    if (skills.isEmpty || count <= 0) return const [];
    final left = <String, int>{for (final s in skills) s.$1: 0};
    var remaining = count;
    final others = [...skills];
    if (focusSkill != null && left.containsKey(focusSkill)) {
      final n = skills.length == 1 ? count : (count + 1) ~/ 2;
      left[focusSkill] = n;
      remaining -= n;
      others.removeWhere((s) => s.$1 == focusSkill);
    }
    if (others.isNotEmpty && remaining > 0) {
      final weights = [for (final s in others) max(s.$2, 0.05)];
      final total = weights.reduce((a, b) => a + b);
      final exact = [for (final w in weights) remaining * w / total];
      final floors = [for (final e in exact) e.floor()];
      var spare = remaining - floors.reduce((a, b) => a + b);
      final byRemainder = List.generate(others.length, (i) => i)
        ..sort((a, b) {
          final c = (exact[b] - floors[b]).compareTo(exact[a] - floors[a]);
          return c != 0 ? c : a.compareTo(b);
        });
      for (final i in byRemainder) {
        if (spare <= 0) break;
        floors[i] += 1;
        spare -= 1;
      }
      for (var i = 0; i < others.length; i++) {
        left[others[i].$1] = left[others[i].$1]! + floors[i];
      }
    }

    final ids = [for (final s in skills) s.$1];
    final out = <String>[];
    while (out.length < count) {
      String? pick;
      for (final avoidRepeat in [true, false]) {
        for (final id in ids) {
          if (left[id]! <= 0) continue;
          if (avoidRepeat && out.isNotEmpty && out.last == id) continue;
          if (pick == null || left[id]! > left[pick]!) pick = id;
        }
        if (pick != null) break;
      }
      if (pick == null) break;
      out.add(pick);
      left[pick] = left[pick]! - 1;
    }
    return out;
  }
}
