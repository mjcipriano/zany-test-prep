import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';

import '../../app/app_controller.dart';

/// XP granted by the hidden cheat.
const int kCheatXp = 10000;

/// Taps needed in quick succession to trigger the cheat.
const int kCheatTaps = 10;

/// Longest pause allowed between two taps before the count starts over.
const Duration kCheatTapWindow = Duration(milliseconds: 1500);

/// Taps after which a "N more taps…" countdown is shown.
const int kCheatHintFrom = 5;

/// Wraps [child] so that [kCheatTaps] quick taps grant [kCheatXp] XP (the
/// hidden testing cheat on the content version).
///
/// Taps are counted on *pointer down* through a [Listener], so they can't be
/// lost to a parent scroll view claiming the gesture when a finger wobbles,
/// and the whole padded area is hit-testable. A countdown snackbar appears
/// from the [kCheatHintFrom]th tap, like Android's developer-options unlock.
class CheatTapTarget extends ConsumerStatefulWidget {
  const CheatTapTarget({super.key, required this.child, this.clock});

  final Widget child;

  /// Injectable clock for tests (defaults to [DateTime.now]).
  final DateTime Function()? clock;

  @override
  ConsumerState<CheatTapTarget> createState() => _CheatTapTargetState();
}

class _CheatTapTargetState extends ConsumerState<CheatTapTarget> {
  int _taps = 0;
  DateTime? _lastTap;
  bool _granting = false;

  DateTime _now() => (widget.clock ?? DateTime.now)();

  Future<void> _onTap() async {
    if (_granting) return;
    final now = _now();
    if (_lastTap == null || now.difference(_lastTap!) > kCheatTapWindow) {
      _taps = 0;
    }
    _lastTap = now;
    _taps++;
    final messenger = ScaffoldMessenger.maybeOf(context);
    if (_taps >= kCheatTaps) {
      _taps = 0;
      _granting = true;
      await ref.read(appControllerProvider.notifier).grantCheatXp(kCheatXp);
      _granting = false;
      messenger
        ?..hideCurrentSnackBar()
        ..showSnackBar(
          const SnackBar(content: Text('🎉 Cheat unlocked: +$kCheatXp XP!')),
        );
      return;
    }
    if (_taps >= kCheatHintFrom) {
      final left = kCheatTaps - _taps;
      messenger
        ?..hideCurrentSnackBar()
        ..showSnackBar(
          SnackBar(
            content: Text('$left more tap${left == 1 ? '' : 's'}…'),
            duration: const Duration(milliseconds: 900),
          ),
        );
    }
  }

  @override
  Widget build(BuildContext context) {
    return Listener(
      behavior: HitTestBehavior.opaque,
      onPointerDown: (_) => _onTap(),
      child: widget.child,
    );
  }
}
