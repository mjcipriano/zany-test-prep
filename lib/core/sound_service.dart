import 'package:audioplayers/audioplayers.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';

/// UI sound cues. Files live in assets/audio/ (Kenney CC0 clicks + original
/// synthesized melodic cues — see assets/audio/CREDITS.md).
enum Sfx {
  tap('audio/kenney_click1.wav'),
  select('audio/kenney_click3.wav'),
  advance('audio/kenney_switch2.wav'),
  correct('audio/correct.wav'),
  incorrect('audio/incorrect.wav'),
  levelUp('audio/level_up.wav'),
  lessonComplete('audio/lesson_complete.wav');

  const Sfx(this.asset);
  final String asset;
}

/// Plays short sound effects. Implementations must never throw to the caller.
abstract class SoundService {
  Future<void> play(Sfx sfx);
  void dispose();
}

/// Real implementation backed by audioplayers. One low-latency player per cue so
/// cues can overlap (e.g. lesson-complete + level-up).
class AudioPlayersSoundService implements SoundService {
  final Map<Sfx, AudioPlayer> _players = {};

  AudioPlayer _playerFor(Sfx sfx) => _players.putIfAbsent(
    sfx,
    () => AudioPlayer()..setReleaseMode(ReleaseMode.stop),
  );

  @override
  Future<void> play(Sfx sfx) async {
    try {
      final p = _playerFor(sfx);
      await p.stop();
      await p.play(AssetSource(sfx.asset), volume: 0.7);
    } catch (_) {
      // Audio is non-essential; never let a playback failure surface.
    }
  }

  @override
  void dispose() {
    for (final p in _players.values) {
      p.dispose();
    }
    _players.clear();
  }
}

/// No-op implementation used in tests (and as a safe fallback).
class NoopSoundService implements SoundService {
  @override
  Future<void> play(Sfx sfx) async {}
  @override
  void dispose() {}
}

final soundServiceProvider = Provider<SoundService>((ref) {
  final service = AudioPlayersSoundService();
  ref.onDispose(service.dispose);
  return service;
});
