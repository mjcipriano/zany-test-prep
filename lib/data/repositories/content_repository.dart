import 'dart:convert';

import 'package:flutter/services.dart' show rootBundle;

import '../../domain/models/content_bundle.dart';

/// Reads a raw asset string. Injectable so tests can supply content directly.
typedef AssetReader = Future<String> Function(String path);

Future<String> _rootBundleReader(String path) => rootBundle.loadString(path);

/// Loads offline content bundles from assets/content/.
class ContentRepository {
  ContentRepository({AssetReader? reader})
      : _reader = reader ?? _rootBundleReader;

  final AssetReader _reader;
  final Map<String, ContentBundle> _cache = {};

  /// The list of enabled exam ids (from assets/content/exams.json).
  Future<List<String>> enabledExams() async {
    final raw = await _reader('assets/content/exams.json');
    final json = jsonDecode(raw) as Map<String, dynamic>;
    return (json['enabled'] as List).map((e) => e.toString()).toList();
  }

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
