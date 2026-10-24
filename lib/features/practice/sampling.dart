import 'dart:math';

import '../../domain/models/question.dart';

/// Returns up to [count] questions from [pool], balanced across every domain
/// present (SAT: Math / Reading & Writing; ACT: English / Math / Reading /
/// Science) so mixed quizzes don't skew toward whichever domain has the most
/// questions. Domains are interleaved in a stable order; when one runs dry the
/// remaining domains keep filling the sample.
List<Question> balancedSample(List<Question> pool, int count, Random rng) {
  if (count <= 0 || pool.isEmpty) return const [];
  final byDomain = <String, List<Question>>{};
  for (final q in pool) {
    byDomain.putIfAbsent(q.domain, () => []).add(q);
  }
  final domains = byDomain.keys.toList()..sort();
  for (final list in byDomain.values) {
    list.shuffle(rng);
  }
  final cursor = {for (final d in domains) d: 0};
  final out = <Question>[];
  var turn = 0;
  while (out.length < count) {
    var progressed = false;
    for (var i = 0; i < domains.length && out.length < count; i++) {
      final d = domains[(turn + i) % domains.length];
      final list = byDomain[d]!;
      final c = cursor[d]!;
      if (c < list.length) {
        out.add(list[c]);
        cursor[d] = c + 1;
        progressed = true;
        turn++;
        break;
      }
    }
    if (!progressed) break; // every domain exhausted
  }
  return out;
}

/// Round-robins [picks] across [domainOrder] (one question from each domain in
/// turn, keeping each domain's own order) so a short quiz samples every section
/// evenly, up to [limit]. Domains missing from [domainOrder] go last.
List<Question> interleaveByDomain(
  List<Question> picks,
  List<String> domainOrder,
  int limit,
) {
  final byDomain = <String, List<Question>>{};
  for (final q in picks) {
    byDomain.putIfAbsent(q.domain, () => []).add(q);
  }
  final domains = [
    ...domainOrder.where(byDomain.containsKey),
    ...byDomain.keys.where((d) => !domainOrder.contains(d)),
  ];
  final out = <Question>[];
  for (var i = 0; out.length < limit; i++) {
    var any = false;
    for (final d in domains) {
      final list = byDomain[d]!;
      if (i < list.length && out.length < limit) {
        out.add(list[i]);
        any = true;
      }
    }
    if (!any) break;
  }
  return out;
}
