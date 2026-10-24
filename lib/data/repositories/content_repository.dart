import 'dart:convert';

import 'package:flutter/services.dart' show rootBundle;

import '../../domain/models/content_bundle.dart';
import '../../domain/models/exam.dart';

/// Reads a raw asset string. Injectable so tests can supply content directly.
typedef AssetReader = Future<String> Function(String path);

Future<String> _rootBundleReader(String path) => rootBundle.loadString(path);

/// Loads offline content bundles from assets/content/.
class ContentRepository {
  ContentRepository({AssetReader? reader})
    : _reader = reader ?? _rootBundleReader;

  final AssetReader _reader;
  final Map<String, ContentBundle> _cache = {};

  /// The enabled exams (from assets/content/exams.json). Tolerates both the
  /// legacy `{"enabled": ["sat"]}` shape and the richer
  /// `{"enabled": [...], "exams": [{id, name, display_name, tagline}]}` shape.
  Future<List<ExamInfo>> enabledExams() async {
    final raw = await _reader('assets/content/exams.json');
    final json = jsonDecode(raw) as Map<String, dynamic>;
    final enabled = (json['enabled'] as List? ?? const [])
        .map((e) => e.toString())
        .toSet();
    final described = (json['exams'] as List? ?? const [])
        .map(ExamInfo.fromJson)
        .where((e) => e.id.isNotEmpty && enabled.contains(e.id))
        .toList();
    final seen = described.map((e) => e.id).toSet();
    return [
      ...described,
      for (final id in enabled)
        if (!seen.contains(id)) ExamInfo.fromJson(id),
    ];
  }

  /// Just the enabled exam ids, in exams.json order.
  Future<List<String>> enabledExamIds() async =>
      (await enabledExams()).map((e) => e.id).toList();

  /// Loads (and caches) the content bundle for an exam.
  Future<ContentBundle> loadBundle(String examId) async {
    final cached = _cache[examId];
    if (cached != null) return cached;
    final raw = await _reader('assets/content/$examId.bundle.json');
    final json = jsonDecode(raw) as Map<String, dynamic>;
    final bundle = ContentBundle.fromJson(json);
    _cache[examId] = bundle;
    return bundle;
  }
}
