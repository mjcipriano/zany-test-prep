/// Defensive JSON coercion used by every `fromJson` in the persistence layer.
///
/// Stored documents survive app updates: a newer build must never crash because
/// an old (or hand-edited, or partially-written) value has the "wrong" type or
/// is missing. These helpers coerce loosely and fall back to a default instead
/// of throwing, so any individual bad field degrades to its default rather than
/// taking down the whole load. See docs/persistence.md (update strategy).
library;

int asInt(Object? v, [int fallback = 0]) {
  if (v is int) return v;
  if (v is num) return v.toInt();
  if (v is String) return int.tryParse(v) ?? fallback;
  return fallback;
}

double asDouble(Object? v, [double fallback = 0]) {
  if (v is num) return v.toDouble();
  if (v is String) return double.tryParse(v) ?? fallback;
  return fallback;
}

bool asBool(Object? v, [bool fallback = false]) {
  if (v is bool) return v;
  if (v is num) return v != 0;
  if (v is String) {
    final s = v.toLowerCase();
    if (s == 'true' || s == '1') return true;
    if (s == 'false' || s == '0') return false;
  }
  return fallback;
}

/// Non-null string; non-string values are stringified, null -> [fallback].
String asString(Object? v, [String fallback = '']) => v?.toString() ?? fallback;

/// Nullable string; null stays null, everything else is stringified.
String? asStringOrNull(Object? v) => v?.toString();

List<String> asStringList(Object? v) =>
    v is List ? v.map((e) => e.toString()).toList() : const <String>[];

Map<String, dynamic> asMap(Object? v) =>
    v is Map ? v.cast<String, dynamic>() : const <String, dynamic>{};

List<dynamic> asList(Object? v) => v is List ? v : const <dynamic>[];
