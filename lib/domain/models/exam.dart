/// Top-level exam descriptor (from exam.yaml, embedded in the content bundle).
class Exam {
  const Exam({
    required this.id,
    required this.name,
    required this.displayName,
    required this.enabled,
    required this.contentVersion,
    required this.description,
    required this.domains,
  });

  final String id;
  final String name;
  final String displayName;
  final bool enabled;
  final String contentVersion;
  final String description;
  final List<String> domains;

  factory Exam.fromJson(Map<String, dynamic> json) => Exam(
        id: json['exam_id'] as String,
        name: json['exam_name'] as String,
        displayName: json['display_name'] as String? ?? json['exam_name'] as String,
        enabled: json['enabled'] as bool? ?? true,
        contentVersion: json['content_version'] as String? ?? '1.0.0',
        description: (json['description'] as String? ?? '').trim(),
        domains: (json['domains'] as List? ?? const [])
            .map((e) => e.toString())
            .toList(),
      );
}
