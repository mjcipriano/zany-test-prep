/// The exam skill map: domains -> sections -> skills. Exam-agnostic.
class SkillNode {
  const SkillNode({required this.id, required this.name, required this.subskills});

  final String id;
  final String name;
  final List<String> subskills;

  factory SkillNode.fromJson(Map<String, dynamic> json) => SkillNode(
        id: json['id'] as String,
        name: json['name'] as String,
        subskills: (json['subskills'] as List? ?? const [])
            .map((e) => e.toString())
            .toList(),
      );
}

class Section {
  const Section({required this.id, required this.name, required this.skills});

  final String id;
  final String name;
  final List<SkillNode> skills;

  factory Section.fromJson(Map<String, dynamic> json) => Section(
        id: json['id'] as String,
        name: json['name'] as String,
        skills: (json['skills'] as List)
            .map((e) => SkillNode.fromJson(e as Map<String, dynamic>))
            .toList(),
      );
}

class SkillDomain {
  const SkillDomain({required this.id, required this.name, required this.sections});

  final String id;
  final String name;
  final List<Section> sections;

  factory SkillDomain.fromJson(Map<String, dynamic> json) => SkillDomain(
        id: json['id'] as String,
        name: json['name'] as String,
        sections: (json['sections'] as List)
            .map((e) => Section.fromJson(e as Map<String, dynamic>))
            .toList(),
      );
}

/// Parsed skill map with a fast id -> name lookup.
class SkillMap {
  SkillMap({required this.domains})
      : _names = {
          for (final d in domains)
            for (final s in d.sections)
              for (final sk in s.skills) sk.id: sk.name,
        };

  final List<SkillDomain> domains;
  final Map<String, String> _names;

  String nameFor(String skillId) => _names[skillId] ?? skillId;

  factory SkillMap.fromJson(Map<String, dynamic> json) => SkillMap(
        domains: (json['domains'] as List)
            .map((e) => SkillDomain.fromJson(e as Map<String, dynamic>))
            .toList(),
      );
}
