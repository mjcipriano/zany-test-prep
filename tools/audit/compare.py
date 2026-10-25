#!/usr/bin/env python3
"""Grade human-style solver output against the exported answer key.

    python tools/audit/compare.py --dir <audit dir>             # key.json + solved_*.json there
    python tools/audit/compare.py --key key.json solved_01.json solved_02.json
    python tools/audit/compare.py --dir <audit dir> --out report.md --json report.json

Solver files map ``question_id -> {"answer": "B" | value, "confidence":
"high"|"medium"|"low", "note": "..."}``. The report groups disagreements by
exam:family (families with the most high-confidence disagreements first, as
those are the likeliest key errors), and lists unanswered questions. When
batch files are present in the same directory their prompts are quoted for
context.
"""
from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path
from typing import Dict, List, Optional

if __package__ in (None, ""):
    sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
    from audit.expr import num_equal, parse_number  # type: ignore  # noqa: E402
else:
    from .expr import num_equal, parse_number

CONF_ORDER = {"high": 0, "medium": 1, "low": 2}


def normalize_choice(ans) -> Optional[str]:
    """"B", "b", "(B)", "B)", "B. 42", "Choice B" -> "B"."""
    if ans is None:
        return None
    s = str(ans).strip()
    m = re.fullmatch(r"(?:choice\s+)?\(?([A-Fa-f])\)?(?:[.):\s].*)?", s, re.I | re.S)
    return m.group(1).upper() if m else None


def answers_match(entry: dict, given) -> bool:
    """Does the solver's ``given`` answer agree with key ``entry``?"""
    if entry.get("question_type") == "student_produced":
        g = parse_number(str(given).strip()) if given is not None else None
        if g is None:
            return False
        targets = [entry.get("answer")] + [parse_number(a) for a in entry.get("accepted") or []]
        tol = max(float(entry.get("tolerance") or 0), 1e-6)
        for t in targets:
            if t is None:
                continue
            if isinstance(t, (int, float)) and not isinstance(t, bool):
                if abs(float(g) - float(t)) <= tol * max(1.0, abs(float(t))) or num_equal(g, t):
                    return True
            elif num_equal(g, t):
                return True
        return False
    return normalize_choice(given) == entry.get("answer")


def load_solved(paths: List[Path]) -> Dict[str, dict]:
    out: Dict[str, dict] = {}
    for p in paths:
        data = json.loads(Path(p).read_text())
        if isinstance(data, dict) and "answers" in data and isinstance(data["answers"], dict):
            data = data["answers"]
        for qid, v in data.items():
            if not isinstance(v, dict):
                v = {"answer": v}
            out[qid] = v
    return out


def load_prompts(dir_: Optional[Path]) -> Dict[str, str]:
    prompts: Dict[str, str] = {}
    if not dir_:
        return prompts
    for p in sorted(Path(dir_).glob("batch_*.json")):
        for q in json.loads(p.read_text()).get("questions", []):
            prompts[q["question_id"]] = q.get("prompt", "")
    return prompts


def batch_members(dir_: Optional[Path], solved_paths: List[Path]) -> Optional[set]:
    """Question ids of the batches whose solved_NN.json was given (None if unknown).

    Lets a partial run (only some batches solved) report only its own gaps."""
    if not dir_:
        return None
    ids = set()
    found = False
    for sp in solved_paths:
        m = re.search(r"solved_(\d+)\.json$", str(sp))
        bp = Path(dir_) / f"batch_{m.group(1)}.json" if m else None
        if bp is None or not bp.exists():
            return None
        found = True
        ids |= {q["question_id"] for q in json.loads(bp.read_text()).get("questions", [])}
    return ids if found else None


def compare(key: Dict[str, dict], solved: Dict[str, dict], expected: Optional[set] = None) -> dict:
    """Grade ``solved`` against ``key``; ``expected`` limits which ids count as missing."""
    fams: Dict[str, dict] = {}
    unknown = sorted(set(solved) - set(key))
    for qid, entry in sorted(key.items()):
        if expected is not None and qid not in expected and qid not in solved:
            continue
        fk = f"{entry.get('exam')}:{entry.get('family')}"
        f = fams.setdefault(fk, {"family": fk, "domain": entry.get("domain"), "answered": 0,
                                 "agree": 0, "disagree": [], "missing": []})
        s = solved.get(qid)
        if s is None or s.get("answer") in (None, ""):
            f["missing"].append(qid)
            continue
        f["answered"] += 1
        if answers_match(entry, s.get("answer")):
            f["agree"] += 1
            continue
        f["disagree"].append({
            "question_id": qid, "difficulty": entry.get("difficulty"),
            "key": entry.get("answer"), "key_text": entry.get("answer_text"),
            "solver": s.get("answer"), "confidence": str(s.get("confidence", "")).lower(),
            "note": s.get("note", ""),
        })
    for f in fams.values():
        f["disagree"].sort(key=lambda d: (CONF_ORDER.get(d["confidence"], 3), d["question_id"]))
        f["high_conf_disagree"] = sum(1 for d in f["disagree"] if d["confidence"] == "high")
    ordered = sorted(fams.values(), key=lambda f: (-f["high_conf_disagree"], -len(f["disagree"]),
                                                   f["family"]))
    answered = sum(f["answered"] for f in ordered)
    agree = sum(f["agree"] for f in ordered)
    return {
        "questions": len(key), "answered": answered, "agree": agree,
        "disagree": answered - agree,
        "high_conf_disagree": sum(f["high_conf_disagree"] for f in ordered),
        "missing": sum(len(f["missing"]) for f in ordered),
        "unknown_ids": unknown,
        "families": ordered,
    }


def format_report(rep: dict, prompts: Optional[Dict[str, str]] = None) -> str:
    prompts = prompts or {}
    pct = 100.0 * rep["agree"] / rep["answered"] if rep["answered"] else 0.0
    lines = ["# Answer-key audit: solver disagreements", "",
             f"- Key questions: {rep['questions']}; answered: {rep['answered']}; "
             f"missing: {rep['missing']}",
             f"- Agree: {rep['agree']} ({pct:.1f}%); disagree: {rep['disagree']} "
             f"(high confidence: {rep['high_conf_disagree']})"]
    if rep["unknown_ids"]:
        lines.append(f"- Solver ids not in the key (ignored): {len(rep['unknown_ids'])}")
    bad = [f for f in rep["families"] if f["disagree"]]
    lines += ["", f"## Families with disagreements ({len(bad)})", ""]
    for f in bad:
        lines.append(f"### {f['family']} - {len(f['disagree'])} of {f['answered']} disagree "
                     f"({f['high_conf_disagree']} high confidence)")
        for d in f["disagree"]:
            key_txt = f"{d['key']}" + (f" ({d['key_text']})" if d.get("key_text") else "")
            lines.append(f"- `{d['question_id']}` [{d['difficulty']}] key {key_txt}; solver "
                         f"{d['solver']} [{d['confidence'] or '?'}]: {d['note']}")
            if d["question_id"] in prompts:
                lines.append(f"  - prompt: {prompts[d['question_id']][:200]}")
        lines.append("")
    missing = [(f["family"], q) for f in rep["families"] for q in f["missing"]]
    if missing:
        lines += [f"## Unanswered ({len(missing)})", ""]
        lines += [f"- `{q}` ({fam})" for fam, q in missing[:200]]
        if len(missing) > 200:
            lines.append(f"- ... and {len(missing) - 200} more")
    return "\n".join(lines).rstrip() + "\n"


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    ap.add_argument("solved", nargs="*", type=Path, help="solved_NN.json files")
    ap.add_argument("--dir", type=Path, help="audit dir holding key.json, batch_*.json, solved_*.json")
    ap.add_argument("--key", type=Path, help="key.json (default: <dir>/key.json)")
    ap.add_argument("--out", type=Path, help="write the Markdown report here (default: stdout)")
    ap.add_argument("--json", type=Path, help="also write the report as JSON")
    args = ap.parse_args(argv)
    key_path = args.key or (args.dir / "key.json" if args.dir else None)
    if key_path is None:
        ap.error("pass --dir or --key")
    solved_paths = list(args.solved) or (sorted(args.dir.glob("solved_*.json")) if args.dir else [])
    if not solved_paths:
        ap.error("no solver files given or found")
    key = json.loads(key_path.read_text())
    rep = compare(key, load_solved(solved_paths),
                  batch_members(args.dir or key_path.parent, solved_paths))
    text = format_report(rep, load_prompts(args.dir or key_path.parent))
    if args.out:
        args.out.write_text(text)
        print(f"wrote {args.out}: {rep['disagree']} disagreements in "
              f"{sum(1 for f in rep['families'] if f['disagree'])} families")
    else:
        print(text)
    if args.json:
        args.json.write_text(json.dumps(rep, indent=1, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    sys.exit(main())
