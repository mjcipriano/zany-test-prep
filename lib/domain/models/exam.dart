/// Top-level exam descriptor (from exam.yaml, embedded in the content bundle).
///
/// Everything exam-specific the app needs — how a full-length timed test is
/// structured and how raw scores map to the exam's scale — lives here, so the
/// UI never hard-codes "SAT" or "ACT" shapes.
class Exam {
  const Exam({
    required this.id,
    required this.name,
    required this.displayName,
    required this.enabled,
    required this.contentVersion,
    required this.description,
    required this.domains,
    this.tagline = '',
    this.timedTest = const TimedTestPlan(),
    this.scoring = const ScoringSpec(),
  });

  final String id;
  final String name;
  final String displayName;
  final bool enabled;
  final String contentVersion;
  final String description;
  final List<String> domains;

  /// One-line pitch shown in the exam picker (e.g. "Reading, Writing & Math").
  final String tagline;

  /// The full-length practice-test layout (modules, counts, minutes).
  final TimedTestPlan timedTest;

  /// How raw correct counts map onto the exam's reported scale.
  final ScoringSpec scoring;

  factory Exam.fromJson(Map<String, dynamic> json) {
    final domains = (json['domains'] as List? ?? const [])
        .map((e) => e.toString())
        .toList();
    final timed = json['timed_test'];
    final scoring = json['scoring'];
    return Exam(
      id: json['exam_id'] as String,
      name: json['exam_name'] as String,
      displayName:
          json['display_name'] as String? ?? json['exam_name'] as String,
      enabled: json['enabled'] as bool? ?? true,
      contentVersion: json['content_version'] as String? ?? '1.0.0',
      description: (json['description'] as String? ?? '').trim(),
      domains: domains,
      tagline: (json['tagline'] as String? ?? '').trim(),
      timedTest: timed is Map
          ? TimedTestPlan.fromJson(timed.cast<String, dynamic>(), domains)
          : TimedTestPlan.defaultFor(domains),
      scoring: scoring is Map
          ? ScoringSpec.fromJson(scoring.cast<String, dynamic>())
          : const ScoringSpec(),
    );
  }
}

/// A lightweight exam summary (from assets/content/exams.json) used by the
/// onboarding picker and settings without loading a full bundle.
class ExamInfo {
  const ExamInfo({
    required this.id,
    required this.name,
    required this.displayName,
    this.tagline = '',
  });

  final String id;
  final String name;
  final String displayName;
  final String tagline;

  /// Accepts either the legacy bare id ("sat") or a descriptor object.
  factory ExamInfo.fromJson(Object? json) {
    if (json is Map) {
      final m = json.cast<String, dynamic>();
      final id = (m['id'] ?? m['exam_id'] ?? '').toString();
      final name = (m['name'] ?? m['exam_name'] ?? id.toUpperCase()).toString();
      return ExamInfo(
        id: id,
        name: name,
        displayName: (m['display_name'] ?? name).toString(),
        tagline: (m['tagline'] ?? '').toString(),
      );
    }
    final id = json.toString();
    return ExamInfo(
      id: id,
      name: id.toUpperCase(),
      displayName: id.toUpperCase(),
    );
  }
}

/// One timed section/module of a full-length practice test.
class TestModule {
  const TestModule({
    required this.name,
    required this.domain,
    required this.count,
    required this.minutes,
  });

  final String name;
  final String domain;
  final int count;
  final int minutes;

  factory TestModule.fromJson(Map<String, dynamic> json) => TestModule(
    name: json['name'] as String? ?? json['domain'].toString(),
    domain: json['domain'].toString(),
    count: (json['count'] as num?)?.toInt() ?? 20,
    minutes: (json['minutes'] as num?)?.toInt() ?? 25,
  );
}

/// The timed-test layout. [intro] is the explanatory blurb on the start page.
class TimedTestPlan {
  const TimedTestPlan({this.modules = const [], this.intro = ''});

  final List<TestModule> modules;
  final String intro;

  bool get isEmpty => modules.isEmpty;

  int get totalQuestions => modules.fold(0, (s, m) => s + m.count);
  int get totalMinutes => modules.fold(0, (s, m) => s + m.minutes);

  /// Domains in the order they first appear in the plan.
  List<String> get domains {
    final seen = <String>[];
    for (final m in modules) {
      if (!seen.contains(m.domain)) seen.add(m.domain);
    }
    return seen;
  }

  factory TimedTestPlan.fromJson(
    Map<String, dynamic> json,
    List<String> examDomains,
  ) {
    final raw = json['modules'];
    final modules = raw is List
        ? raw
              .whereType<Map>()
              .map((m) => TestModule.fromJson(m.cast<String, dynamic>()))
              .toList()
        : const <TestModule>[];
    if (modules.isEmpty) return TimedTestPlan.defaultFor(examDomains);
    return TimedTestPlan(
      modules: modules,
      intro: (json['intro'] as String? ?? '').trim(),
    );
  }

  /// A sensible fallback when exam.yaml has no explicit plan: one 20-question,
  /// 25-minute module per domain.
  factory TimedTestPlan.defaultFor(List<String> domains) => TimedTestPlan(
    modules: [
      for (final d in domains)
        TestModule(name: _titleCase(d), domain: d, count: 20, minutes: 25),
    ],
  );
}

/// Which scale an exam reports on.
enum ScoreScale {
  /// SAT: each section 200–800, total 400–1600 (sum of sections).
  sat1600,

  /// ACT: each section 1–36, composite = rounded mean of the composite domains.
  act36,

  /// Fallback: percent correct per section and overall.
  percent;

  static ScoreScale parse(String? value) {
    switch (value) {
      case 'sat_1600':
        return ScoreScale.sat1600;
      case 'act_36':
        return ScoreScale.act36;
      case 'percent':
        return ScoreScale.percent;
      default:
        return ScoreScale.percent;
    }
  }
}

/// How to report scores for an exam.
class ScoringSpec {
  const ScoringSpec({
    this.scale = ScoreScale.percent,
    this.compositeDomains = const [],
    this.compositeLabel = 'Overall',
  });

  final ScoreScale scale;

  /// Domains that count toward the composite/total. Empty = all domains.
  final List<String> compositeDomains;

  /// Label for the headline number ("Total score", "Composite score").
  final String compositeLabel;

  factory ScoringSpec.fromJson(Map<String, dynamic> json) => ScoringSpec(
    scale: ScoreScale.parse(json['type']?.toString()),
    compositeDomains: (json['composite_domains'] as List? ?? const [])
        .map((e) => e.toString())
        .toList(),
    compositeLabel:
        json['composite_label'] as String? ??
        switch (ScoreScale.parse(json['type']?.toString())) {
          ScoreScale.sat1600 => 'Estimated total score',
          ScoreScale.act36 => 'Estimated composite score',
          ScoreScale.percent => 'Overall accuracy',
        },
  );
}

String _titleCase(String id) => id
    .split('_')
    .where((w) => w.isNotEmpty)
    .map((w) => w[0].toUpperCase() + w.substring(1))
    .join(' ');
