import 'dart:math' as math;

import 'package:flutter/material.dart';

import '../../design/widgets.dart';

/// Renders a declarative figure spec (a `figure` stimulus) as a diagram, the
/// way the SAT shows one for geometry, scatterplots, etc. The spec is
/// `{ "kind": ..., ...params }`; supported kinds: right_triangle, rect, circle,
/// box, cylinder, scatter. Unknown kinds render nothing (the prompt text still
/// fully describes the problem).
class FigureView extends StatelessWidget {
  const FigureView({super.key, required this.figure});
  final Map<String, dynamic> figure;

  @override
  Widget build(BuildContext context) {
    final caption = figure['caption'] as String?;
    final scheme = Theme.of(context).colorScheme;
    return AppCard(
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          if (caption != null)
            Padding(
              padding: const EdgeInsets.only(bottom: 8),
              child: Text(caption,
                  style: const TextStyle(fontWeight: FontWeight.w700)),
            ),
          Center(
            child: SizedBox(
              width: 248,
              height: 196,
              child: CustomPaint(
                painter: _FigurePainter(figure, scheme.onSurface, scheme.primary),
              ),
            ),
          ),
        ],
      ),
    );
  }
}

double _d(Object? v, [double fallback = 0]) => v is num
    ? v.toDouble()
    : (v is String ? double.tryParse(v) ?? fallback : fallback);

String? _s(Object? v) => v?.toString();

class _FigurePainter extends CustomPainter {
  _FigurePainter(this.f, this.ink, this.accent);
  final Map<String, dynamic> f;
  final Color ink;
  final Color accent;

  late final Paint _stroke = Paint()
    ..color = ink
    ..style = PaintingStyle.stroke
    ..strokeWidth = 2;
  late final Paint _thin = Paint()
    ..color = ink
    ..style = PaintingStyle.stroke
    ..strokeWidth = 1;
  late final Paint _accentStroke = Paint()
    ..color = accent
    ..style = PaintingStyle.stroke
    ..strokeWidth = 2.5;
  late final Paint _fill = Paint()..color = accent.withValues(alpha: 0.12);

  @override
  void paint(Canvas canvas, Size size) {
    switch (f['kind'] as String? ?? '') {
      case 'right_triangle':
        _rightTriangle(canvas, size);
      case 'rect':
        _rect(canvas, size);
      case 'circle':
        _circle(canvas, size);
      case 'box':
        _box(canvas, size);
      case 'cylinder':
        _cylinder(canvas, size);
      case 'scatter':
        _scatter(canvas, size);
    }
  }

  void _label(Canvas c, String? text, Offset at, {Color? color}) {
    if (text == null || text.isEmpty) return;
    final tp = TextPainter(
      text: TextSpan(
        text: text,
        style: TextStyle(
            color: color ?? ink, fontSize: 13, fontWeight: FontWeight.w700),
      ),
      textDirection: TextDirection.ltr,
    )..layout();
    tp.paint(c, at - Offset(tp.width / 2, tp.height / 2));
  }

  Map _labels() => (f['labels'] as Map?) ?? const {};

  // Right triangle: right angle at bottom-left; base = a, vertical leg = b,
  // hypotenuse = c. Optional acute-angle label at the bottom-right vertex.
  void _rightTriangle(Canvas c, Size s) {
    final lab = _labels();
    const pad = 36.0;
    final corner = Offset(pad, s.height - pad);
    final right = Offset(s.width - pad, s.height - pad);
    const top = Offset(pad, pad);
    final path = Path()
      ..moveTo(corner.dx, corner.dy)
      ..lineTo(right.dx, right.dy)
      ..lineTo(top.dx, top.dy)
      ..close();
    c.drawPath(path, _fill);
    c.drawPath(path, _stroke);
    // right-angle square
    const m = 12.0;
    c.drawRect(Rect.fromLTWH(corner.dx, corner.dy - m, m, m), _thin);
    _label(c, _s(lab['a']), Offset((corner.dx + right.dx) / 2, corner.dy + 14));
    _label(c, _s(lab['b']), Offset(corner.dx - 16, (corner.dy + top.dy) / 2));
    _label(c, _s(lab['c']),
        Offset((right.dx + top.dx) / 2 + 10, (right.dy + top.dy) / 2 - 8));
    final angle = _s(f['angle']);
    if (angle != null) _label(c, angle, Offset(right.dx - 26, right.dy - 12));
  }

  void _rect(Canvas c, Size s) {
    final lab = _labels();
    final r = Rect.fromLTWH(40, 44, s.width - 80, s.height - 92);
    c.drawRect(r, _fill);
    c.drawRect(r, _stroke);
    _label(c, _s(lab['w']), Offset(r.center.dx, r.bottom + 14));
    _label(c, _s(lab['h']), Offset(r.left - 16, r.center.dy));
  }

  void _circle(Canvas c, Size s) {
    final lab = _labels();
    final center = Offset(s.width / 2, s.height / 2);
    final radius = math.min(s.width, s.height) / 2 - 34;
    final sector = _d(f['sector']);
    if (sector > 0) {
      final sweep = sector * math.pi / 180;
      final p = Path()
        ..moveTo(center.dx, center.dy)
        ..arcTo(Rect.fromCircle(center: center, radius: radius), -math.pi / 2,
            sweep, false)
        ..close();
      c.drawPath(p, _fill);
    }
    c.drawCircle(center, radius, _stroke);
    c.drawcircleDot(center, ink);
    // radius (or diameter) marker
    if (_s(lab['d']) != null) {
      c.drawLine(Offset(center.dx - radius, center.dy),
          Offset(center.dx + radius, center.dy), _accentStroke);
      _label(c, _s(lab['d']), Offset(center.dx, center.dy - 12), color: accent);
    } else {
      c.drawLine(center, Offset(center.dx + radius, center.dy), _accentStroke);
      _label(c, _s(lab['r']) ?? 'r',
          Offset(center.dx + radius / 2, center.dy - 12), color: accent);
    }
    if (sector > 0) {
      _label(c, _s(lab['angle']) ?? '${sector.toStringAsFixed(0)}°',
          Offset(center.dx + 16, center.dy - radius / 3), color: accent);
    }
  }

  void _box(Canvas c, Size s) {
    final lab = _labels();
    const dx = 26.0, dy = 16.0;
    final r = Rect.fromLTWH(36, 56, s.width - 96, s.height - 104);
    // front face
    c.drawRect(r, _fill);
    c.drawRect(r, _stroke);
    final off = const Offset(dx, -dy);
    // back corners
    final tl = r.topLeft + off,
        tr = r.topRight + off,
        br = r.bottomRight + off;
    c.drawLine(r.topLeft, tl, _stroke);
    c.drawLine(r.topRight, tr, _stroke);
    c.drawLine(r.bottomRight, br, _stroke);
    c.drawLine(tl, tr, _stroke);
    c.drawLine(tr, br, _stroke);
    _label(c, _s(lab['l']), Offset(r.center.dx, r.bottom + 14));
    _label(c, _s(lab['h']), Offset(r.left - 14, r.center.dy));
    _label(c, _s(lab['w']), Offset((r.topRight.dx + tr.dx) / 2 + 8, tr.dy + 4));
  }

  void _cylinder(Canvas c, Size s) {
    final lab = _labels();
    final cx = s.width / 2;
    final rx = (s.width - 96) / 2;
    final ry = 14.0;
    final topY = 40.0;
    final botY = s.height - 40.0;
    final topRect = Rect.fromCenter(
        center: Offset(cx, topY), width: rx * 2, height: ry * 2);
    final botRect = Rect.fromCenter(
        center: Offset(cx, botY), width: rx * 2, height: ry * 2);
    // body
    final body = Path()
      ..moveTo(cx - rx, topY)
      ..lineTo(cx - rx, botY)
      ..arcTo(botRect, math.pi, -math.pi, false)
      ..lineTo(cx + rx, topY);
    c.drawPath(body, _fill);
    c.drawLine(Offset(cx - rx, topY), Offset(cx - rx, botY), _stroke);
    c.drawLine(Offset(cx + rx, topY), Offset(cx + rx, botY), _stroke);
    c.drawArc(botRect, 0, math.pi, false, _stroke);        // front bottom
    c.drawArc(botRect, math.pi, math.pi, false, _thin);    // back bottom (dashed-ish)
    c.drawOval(topRect, _stroke);                           // top ellipse
    // radius on top
    c.drawLine(Offset(cx, topY), Offset(cx + rx, topY), _accentStroke);
    _label(c, _s(lab['r']) ?? 'r', Offset(cx + rx / 2, topY - 12), color: accent);
    _label(c, _s(lab['h']), Offset(cx + rx + 14, (topY + botY) / 2));
  }

  void _scatter(Canvas c, Size s) {
    final raw = (f['points'] as List?) ?? const [];
    final pts = <Offset>[];
    for (final p in raw) {
      if (p is List && p.length >= 2) {
        pts.add(Offset(_d(p[0]), _d(p[1])));
      }
    }
    const padL = 34.0, padB = 28.0, padT = 12.0, padR = 12.0;
    final plot = Rect.fromLTRB(padL, padT, s.width - padR, s.height - padB);
    // axes
    c.drawLine(plot.bottomLeft, plot.bottomRight, _stroke);
    c.drawLine(plot.topLeft, plot.bottomLeft, _stroke);
    if (pts.isEmpty) return;
    final xs = pts.map((p) => p.dx), ys = pts.map((p) => p.dy);
    double minX = xs.reduce(math.min), maxX = xs.reduce(math.max);
    double minY = ys.reduce(math.min), maxY = ys.reduce(math.max);
    // pad domain a touch
    final dx = (maxX - minX) == 0 ? 1 : (maxX - minX) * 0.1;
    final dy = (maxY - minY) == 0 ? 1 : (maxY - minY) * 0.1;
    minX -= dx; maxX += dx; minY -= dy; maxY += dy;
    Offset toPx(double x, double y) => Offset(
          plot.left + (x - minX) / (maxX - minX) * plot.width,
          plot.bottom - (y - minY) / (maxY - minY) * plot.height,
        );
    final dot = Paint()..color = accent;
    for (final p in pts) {
      c.drawCircle(toPx(p.dx, p.dy), 3.5, dot);
    }
    final line = f['line'] as Map?;
    if (line != null) {
      final m = _d(line['m']), b = _d(line['b']);
      c.drawLine(toPx(minX, m * minX + b), toPx(maxX, m * maxX + b),
          _accentStroke);
    }
    _label(c, _s(f['xlabel']), Offset(plot.center.dx, s.height - 8));
  }

  @override
  bool shouldRepaint(covariant _FigurePainter old) => old.f != f;
}

extension _Dot on Canvas {
  void drawcircleDot(Offset center, Color color) =>
      drawCircle(center, 2.5, Paint()..color = color);
}
