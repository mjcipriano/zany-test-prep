#!/usr/bin/env python3
"""Export a stratified, answer-free sample of the bank for human-style solving.

Other agents solve the exported batches cold, like students; ``compare.py``
then grades their answers against the separately written key.

    python tools/audit/export_sample.py                       # -> build/audit/
    python tools/audit/export_sample.py --out-dir /tmp/audit --max-total 2500
    python tools/audit/export_sample.py --bundle-dir <dir with sat/act.bundle.json>

Sampling: one stratum per exam × family × difficulty (authored items without a
``family:`` tag are stratified by skill as ``authored-<skill>``). Every stratum
gets one question, then second questions are added in a seeded random order
until ``--max-total`` (so each stratum has 1-2). Everything is deterministic
for a given ``--seed``.

Outputs in ``--out-dir``:

* ``batch_NN.json`` - ``{"batch", "instructions", "questions": [...]}``; each
  question carries ONLY what a student sees: question_id, exam, domain,
  question_type, stimulus (passage / table / figure), prompt, and choices as
  ``{id, text}``. No correct_choice, rationales, explanation, answer,
  answer_verification, skill or tags.
* ``key.json`` - ``{question_id: {exam, domain, question_type, family,
  difficulty, skill, answer, accepted?}}`` where ``answer`` is the keyed choice
  letter, or the grid-in value.
"""
from __future__ import annotations

import argparse
import json
import random
import sys
import zlib
from pathlib import Path
from typing import Dict, List, Tuple

ROOT = Path(__file__).resolve().parents[2]
BUNDLE_DIR = ROOT / "assets" / "content"
DEFAULT_OUT = ROOT / "build" / "audit"  # git-ignored; pass --out-dir for elsewhere
EXAMS = ("sat", "act")

# The only question fields a student-facing export may carry.
STUDENT_FIELDS = ("question_id", "exam", "domain", "question_type", "stimulus", "prompt", "choices")
# Fields that reveal or explain the answer; never exported to a batch.
LEAKY_FIELDS = ("correct_choice", "answer", "explanation", "answer_verification", "tags",
                "skill", "subskill", "lesson_id", "rationale")

INSTRUCTIONS = (
    "Solve each question as a strong student would, from the prompt, stimulus and choices only. "
    "Write your answers to solved_NN.json (same NN as this batch) as a JSON object "
    '{question_id: {"answer": "B" (choice id) or the numeric/text value for student_produced items, '
    '"confidence": "high"|"medium"|"low", "note": "one line: your reasoning or why the item looks flawed"}}. '
    "If no choice is correct or more than one is, still give your best answer, set confidence to low, "
    "and say so in the note. A 'figure' stimulus is a data description of the picture the student sees."
)


def family_key(q: dict) -> str:
    for t in q.get("tags") or []:
        if isinstance(t, str) and t.startswith("family:"):
            return t[len("family:"):]
    return f"authored-{q.get('skill', 'unknown')}"


def student_view(q: dict) -> dict:
    """The question exactly as a student sees it (nothing that leaks the key)."""
    out = {
        "question_id": q["question_id"],
        "exam": q.get("exam_id"),
        "domain": q.get("domain"),
        "question_type": q.get("question_type"),
    }
    if q.get("stimulus"):
        out["stimulus"] = q["stimulus"]
    out["prompt"] = q.get("prompt")
    if q.get("question_type") == "student_produced":
        out["answer_format"] = "Enter a number (integer, decimal, or fraction like 3/4)."
    else:
        out["choices"] = [{"id": c["id"], "text": c["text"]} for c in q.get("choices") or []]
    return out


def key_entry(q: dict) -> dict:
    e = {
        "exam": q.get("exam_id"),
        "domain": q.get("domain"),
        "question_type": q.get("question_type"),
        "family": family_key(q),
        "difficulty": q.get("difficulty"),
        "skill": q.get("skill"),
    }
    if q.get("question_type") == "student_produced":
        ans = q.get("answer") or {}
        e["answer"] = ans.get("value")
        e["accepted"] = list(ans.get("accepted") or [])
        e["tolerance"] = ans.get("tolerance", 0)
    else:
        e["answer"] = q.get("correct_choice")
        e["answer_text"] = next((c["text"] for c in q.get("choices") or []
                                 if c["id"] == q.get("correct_choice")), None)
    return e


def _rng_for(seed: int, *parts: str) -> random.Random:
    return random.Random(zlib.crc32("|".join((str(seed),) + parts).encode()))


def stratified_sample(questions_by_exam: Dict[str, List[dict]], per_stratum: int = 2,
                      max_total: int = 3000, seed: int = 1234) -> List[dict]:
    """Up to ``per_stratum`` questions per exam × family × difficulty."""
    strata: Dict[Tuple[str, str, str], List[dict]] = {}
    for exam, qs in questions_by_exam.items():
        for q in qs:
            strata.setdefault((exam, family_key(q), q.get("difficulty", "")), []).append(q)
    picks: Dict[Tuple[str, str, str], List[dict]] = {}
    for key in sorted(strata):
        pool = sorted(strata[key], key=lambda q: q["question_id"])
        picks[key] = _rng_for(seed, *key).sample(pool, min(per_stratum, len(pool)))
    chosen = [p[0] for p in picks.values() if p]
    extra = [q for p in picks.values() for q in p[1:]]
    _rng_for(seed, "extra").shuffle(extra)
    room = max(0, max_total - len(chosen))
    chosen += extra[:room]
    # Mix exams/domains/families across batches; deterministic for the seed.
    chosen.sort(key=lambda q: q["question_id"])
    _rng_for(seed, "order").shuffle(chosen)
    return chosen


def export(questions_by_exam: Dict[str, List[dict]], out_dir: Path, *, per_stratum: int = 2,
           max_total: int = 3000, batch_size: int = 150, seed: int = 1234) -> dict:
    out_dir.mkdir(parents=True, exist_ok=True)
    for old in out_dir.glob("batch_*.json"):
        old.unlink()
    sample = stratified_sample(questions_by_exam, per_stratum, max_total, seed)
    batches = [sample[i:i + batch_size] for i in range(0, len(sample), batch_size)]
    paths = []
    for n, batch in enumerate(batches, 1):
        p = out_dir / f"batch_{n:02d}.json"
        p.write_text(json.dumps({"batch": f"{n:02d}", "instructions": INSTRUCTIONS,
                                 "questions": [student_view(q) for q in batch]},
                                ensure_ascii=False, indent=1))
        paths.append(p)
    key = {q["question_id"]: key_entry(q) for q in sample}
    (out_dir / "key.json").write_text(json.dumps(key, ensure_ascii=False, indent=1))
    return {"questions": len(sample), "batches": [str(p) for p in paths],
            "key": str(out_dir / "key.json")}


def load_bundles(bundle_dir: Path = BUNDLE_DIR, exams=EXAMS) -> Dict[str, List[dict]]:
    return {e: json.loads((bundle_dir / f"{e}.bundle.json").read_text())["questions"] for e in exams}


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    ap.add_argument("--bundle-dir", type=Path, default=BUNDLE_DIR)
    ap.add_argument("--out-dir", type=Path, default=DEFAULT_OUT)
    ap.add_argument("--per-stratum", type=int, default=2)
    ap.add_argument("--max-total", type=int, default=3000)
    ap.add_argument("--batch-size", type=int, default=150)
    ap.add_argument("--seed", type=int, default=1234)
    args = ap.parse_args(argv)
    res = export(load_bundles(args.bundle_dir), args.out_dir, per_stratum=args.per_stratum,
                 max_total=args.max_total, batch_size=args.batch_size, seed=args.seed)
    print(f"Exported {res['questions']} questions in {len(res['batches'])} batches:")
    for p in res["batches"]:
        print("  " + p)
    print("Key: " + res["key"])
    return 0


if __name__ == "__main__":
    sys.exit(main())
