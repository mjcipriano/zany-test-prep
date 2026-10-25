import 'dart:convert';
import 'dart:io';

import 'package:zany_test_prep/domain/models/content_bundle.dart';
import 'package:zany_test_prep/domain/models/difficulty.dart';
import 'package:zany_test_prep/domain/models/exam.dart';
import 'package:zany_test_prep/domain/models/lesson.dart';
import 'package:zany_test_prep/domain/models/question.dart';
import 'package:zany_test_prep/domain/models/skill.dart';

final Map<String, ContentBundle> _real = {};

/// The committed runtime bundle for [examId] ('sat' / 'act'), parsed once.
ContentBundle realBundle(String examId) => _real.putIfAbsent(
  examId,
  () => ContentBundle.fromJson(
    jsonDecode(File('assets/content/$examId.bundle.json').readAsStringSync())
        as Map<String, dynamic>,
  ),
);

/// A skill in a synthetic bundle: `(domain, section, skillId)`.
typedef SkillSpec = (String domain, String section, String skill);

/// A small synthetic bundle: per skill, an easy/medium/hard lesson chain
/// (medium needs easy, hard needs medium) with [perDifficulty] questions each.
/// Skills listed in [lockedSkills] need 1,000,000 XP for every lesson.
ContentBundle syntheticBundle({
  String examId = 'sat',
  required List<SkillSpec> skills,
  int perDifficulty = 6,
  Set<String> lockedSkills = const {},
}) {
  final domains = <String, Map<String, List<String>>>{};
  for (final (d, s, k) in skills) {
    domains.putIfAbsent(d, () => {}).putIfAbsent(s, () => []).add(k);
  }
  final lessons = <Lesson>[];
  final questions = <Question>[];
  var order = 0;
  for (final (d, s, k) in skills) {
    String? prev;
    for (final diff in Difficulty.values) {
      final lessonId = '$examId-$k-${diff.id}';
      final ids = <String>[];
      for (var i = 0; i < perDifficulty; i++) {
        final id = '$lessonId-q$i';
        ids.add(id);
        questions.add(
          Question(
            id: id,
            examId: examId,
            domain: d,
            section: s,
            skill: k,
            lessonId: lessonId,
            difficulty: diff,
            type: QuestionType.multipleChoice,
            estimatedTimeSeconds: 60,
            prompt: 'p',
            explanation: 'e',
            tags: const ['t'],
            choices: const [
              Choice(id: 'A', text: '1', rationale: 'r'),
              Choice(id: 'B', text: '2', rationale: 'r'),
            ],
            correctChoice: 'A',
          ),
        );
      }
      lessons.add(
        Lesson(
          id: lessonId,
          examId: examId,
          domain: d,
          section: s,
          skill: k,
          title: '$k ${diff.label}',
          order: order++,
          difficulty: diff,
          estimatedMinutes: 5,
          teachingCard: const TeachingCard(
            title: 't',
            body: 'b',
            keyPoints: ['a'],
          ),
          questionIds: ids,
          prerequisiteLessonIds: prev == null ? const [] : [prev],
          unlockXp: lockedSkills.contains(k) ? 1000000 : 0,
          tags: const ['t'],
        ),
      );
      prev = lessonId;
    }
  }
  return ContentBundle(
    exam: Exam(
      id: examId,
      name: examId.toUpperCase(),
      displayName: examId.toUpperCase(),
      enabled: true,
      contentVersion: '1.0.0',
      description: 'd',
      domains: domains.keys.toList(),
    ),
    skillMap: SkillMap(
      domains: [
        for (final d in domains.entries)
          SkillDomain(
            id: d.key,
            name: 'Domain ${d.key}',
            sections: [
              for (final s in d.value.entries)
                Section(
                  id: s.key,
                  name: s.key,
                  skills: [
                    for (final k in s.value)
                      SkillNode(id: k, name: 'Skill $k', subskills: const []),
                  ],
                ),
            ],
          ),
      ],
    ),
    lessons: lessons,
    questions: questions,
  );
}
