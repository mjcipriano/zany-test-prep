import 'package:flutter_test/flutter_test.dart';
import 'package:zany_test_prep/data/repositories/content_repository.dart';

void main() {
  test('enabledExams reads the rich exams.json shape', () async {
    final repo = ContentRepository(
      reader: (path) async => '''
{"enabled": ["sat", "act"],
 "exams": [
   {"id": "sat", "name": "SAT", "display_name": "Digital SAT", "tagline": "RW & Math"},
   {"id": "act", "name": "ACT", "display_name": "ACT", "tagline": "Four sections"},
   {"id": "ap", "name": "AP", "display_name": "AP"}
 ]}''',
    );
    final exams = await repo.enabledExams();
    expect(exams.map((e) => e.id).toList(), ['sat', 'act']);
    expect(exams.first.displayName, 'Digital SAT');
    expect(exams.last.tagline, 'Four sections');
    expect(await repo.enabledExamIds(), ['sat', 'act']);
  });

  test('enabledExams tolerates the legacy id-only shape', () async {
    final repo = ContentRepository(
      reader: (path) async => '{"enabled": ["sat"]}',
    );
    final exams = await repo.enabledExams();
    expect(exams.length, 1);
    expect(exams.single.id, 'sat');
    expect(exams.single.name, 'SAT');
  });

  test('enabled ids missing a descriptor still appear', () async {
    final repo = ContentRepository(
      reader: (path) async =>
          '{"enabled": ["sat", "act"], "exams": [{"id": "sat", "name": "SAT"}]}',
    );
    final exams = await repo.enabledExams();
    expect(exams.map((e) => e.id).toList(), ['sat', 'act']);
    expect(exams.last.name, 'ACT');
  });

  test('loadBundle caches per exam id', () async {
    var reads = 0;
    final repo = ContentRepository(
      reader: (path) async {
        reads++;
        return '{"exam": {"exam_id": "x", "exam_name": "X"}, '
            '"skills": {"domains": []}, "lessons": [], "questions": []}';
      },
    );
    final a = await repo.loadBundle('x');
    final b = await repo.loadBundle('x');
    expect(identical(a, b), isTrue);
    expect(reads, 1);
    await repo.loadBundle('y');
    expect(reads, 2);
  });
}
