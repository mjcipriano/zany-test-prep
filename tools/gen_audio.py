#!/usr/bin/env python3
"""Generate original, royalty-free UI sound cues for the app.

These melodic cues (correct / incorrect / level-up / lesson-complete) are
synthesized from scratch here, so they are genuinely original and carry no
licensing restrictions. They complement the Kenney CC0 click sounds used for
taps. Output: assets/audio/*.wav (44.1 kHz, 16-bit mono).

    python tools/gen_audio.py
"""
from __future__ import annotations

import math
import struct
import wave
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
OUT = ROOT / "assets" / "audio"
SR = 44100


def _note(freq, dur, *, vol=0.5, harmonics=(1.0, 0.35, 0.15), attack=0.005,
          decay=0.06, sustain=0.7, release=0.08):
    """One enveloped tone with a few harmonics; returns a list of float samples."""
    n = int(SR * dur)
    out = []
    for i in range(n):
        t = i / SR
        # ADSR-ish envelope.
        if t < attack:
            env = t / attack
        elif t < attack + decay:
            env = 1.0 - (1.0 - sustain) * (t - attack) / decay
        elif t > dur - release:
            env = sustain * max(0.0, (dur - t) / release)
        else:
            env = sustain
        s = 0.0
        for k, amp in enumerate(harmonics, start=1):
            s += amp * math.sin(2 * math.pi * freq * k * t)
        out.append(s * env * vol)
    return out


def _silence(dur):
    return [0.0] * int(SR * dur)


def _seq(*chunks):
    out = []
    for c in chunks:
        out.extend(c)
    return out


def _mix_into(base, overlay, start_s):
    start = int(SR * start_s)
    for i, v in enumerate(overlay):
        j = start + i
        if j < len(base):
            base[j] += v
        else:
            base.append(v)
    return base


def _write(name, samples):
    OUT.mkdir(parents=True, exist_ok=True)
    # normalize / clip
    peak = max((abs(s) for s in samples), default=1.0) or 1.0
    scale = 0.95 / peak if peak > 0.95 else 1.0
    path = OUT / name
    with wave.open(str(path), "w") as w:
        w.setnchannels(1)
        w.setsampwidth(2)
        w.setframerate(SR)
        frames = bytearray()
        for s in samples:
            v = int(max(-1.0, min(1.0, s * scale)) * 32767)
            frames += struct.pack("<h", v)
        w.writeframes(bytes(frames))
    print(f"wrote {path.relative_to(ROOT)} ({path.stat().st_size // 1024} KB)")


# Note frequencies (equal temperament).
A4 = 440.0
def f(semitones_from_a4):  # noqa: E743
    return A4 * (2 ** (semitones_from_a4 / 12))


C5, D5, E5, G5, A5, C6, E6, G6 = (f(3), f(5), f(7), f(10), f(12), f(15), f(19), f(22))


def correct():
    # Bright two-note rising chime: E5 -> A5.
    return _seq(_note(E5, 0.10, vol=0.45), _note(A5, 0.18, vol=0.5))


def incorrect():
    # Soft "wrong" buzz: two low descending tones with a duller timbre.
    low = _note(f(-2), 0.12, vol=0.4, harmonics=(1.0, 0.5, 0.4, 0.2))
    lower = _note(f(-5), 0.20, vol=0.4, harmonics=(1.0, 0.5, 0.4, 0.2))
    return _seq(low, lower)


def level_up():
    # Major arpeggio C-E-G-C with a final shimmer.
    return _seq(
        _note(C5, 0.10, vol=0.45),
        _note(E5, 0.10, vol=0.45),
        _note(G5, 0.10, vol=0.45),
        _note(C6, 0.28, vol=0.5),
    )


def lesson_complete():
    # Short triumphant fanfare: C-E-G then a C6 with a sparkle on top.
    base = _seq(
        _note(C5, 0.12, vol=0.4),
        _note(E5, 0.12, vol=0.4),
        _note(G5, 0.12, vol=0.45),
        _note(C6, 0.34, vol=0.5),
    )
    # add a high sparkle overlapping the final note
    base = _mix_into(base, _note(E6, 0.30, vol=0.22), 0.36)
    base = _mix_into(base, _note(G6, 0.26, vol=0.16), 0.42)
    return base


if __name__ == "__main__":
    _write("correct.wav", correct())
    _write("incorrect.wav", incorrect())
    _write("level_up.wav", level_up())
    _write("lesson_complete.wav", lesson_complete())
