import 'dart:convert';

import 'package:flutter/services.dart' show rootBundle;

import '../../domain/models/avatar_catalog.dart';

/// Reads a raw asset string. Injectable so tests can supply a catalog directly.
typedef AssetReader = Future<String> Function(String path);

Future<String> _rootBundleReader(String path) => rootBundle.loadString(path);

/// Loads the vendored avatar customization catalog from assets/avatar/.
class AvatarRepository {
  AvatarRepository({AssetReader? reader})
    : _reader = reader ?? _rootBundleReader;

  final AssetReader _reader;
  AvatarCatalog? _cache;

  static const String catalogPath =
      'assets/avatar/manifest/avatar_catalog.json';

  /// Loads (and caches) the catalog. Returns an empty catalog if the manifest
  /// is missing or unreadable, so the app degrades gracefully.
  Future<AvatarCatalog> loadCatalog() async {
    final cached = _cache;
    if (cached != null) return cached;
    try {
      final raw = await _reader(catalogPath);
      final json = jsonDecode(raw) as Map<String, dynamic>;
      return _cache = AvatarCatalog.fromJson(json);
    } catch (_) {
      return _cache = AvatarCatalog.empty();
    }
  }
}
