#!/usr/bin/env python3
"""Build the Flutter asset bundle(s) from the canonical content.

Reads content/exams/<exam>/ (manifest + lessons + questions + exam.yaml +
skills.yaml) and writes a single JSON bundle per exam into
assets/content/<exam>.bundle.json, plus assets/content/exams.json describing
the enabled exams (id, name, display name, tagline) so the app's exam picker
never has to parse a full bundle. The app loads bundles at startup for fast
offline access.

    python tools/build_bundle.py            # every exam under content/exams/
    python tools/build_bundle.py --exam act # just one (exams.json still lists all)
"""
from __future__ import annotations

import argparse
import json
from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parent.parent
CONTENT = ROOT / "content"
ASSETS = ROOT / "assets" / "content"


# Order exams are listed in (the picker shows them in this order); any exam
# not named here follows alphabetically.
EXAM_ORDER = ["sat", "act"]


def exam_dirs() -> list[Path]:
    dirs = [d for d in (CONTENT / "exams").iterdir()
            if d.is_dir() and (d / "exam.yaml").exists()]
    rank = {e: i for i, e in enumerate(EXAM_ORDER)}
    return sorted(dirs, key=lambda d: (rank.get(d.name, len(rank)), d.name))


def load_exam(exam_dir: Path) -> dict:
    return yaml.safe_load((exam_dir / "exam.yaml").read_text())


def build_exam(exam_id: str) -> dict:
    exam_dir = CONTENT / "exams" / exam_id
    exam = load_exam(exam_dir)
    skills = yaml.safe_load((exam_dir / "skills.yaml").read_text())
    manifest = json.loads((exam_dir / "manifest.json").read_text())

    lessons = [json.loads((exam_dir / rel).read_text()) for rel in manifest["lessons"]]
    questions = []
    for rel in manifest["questions"] + manifest.get("bank", []):
        questions.extend(json.loads((exam_dir / rel).read_text()))

    # Stable path order: the exam's domain order (skills.yaml), then `order`.
    domain_order = [d["id"] for d in skills["domains"]]

    def dom_rank(lesson):
        return domain_order.index(lesson["domain"]) if lesson["domain"] in domain_order \
            else len(domain_order)

    lessons.sort(key=lambda l: (dom_rank(l), l["order"]))
    return {
        "schema_version": 1,
        "exam": exam,
        "skills": skills,
        "lessons": lessons,
        "questions": questions,
    }


def exams_index() -> dict:
    """The exams.json document: enabled ids plus a short descriptor for each."""
    enabled, infos = [], []
    for exam_dir in exam_dirs():
        exam = load_exam(exam_dir)
        if not exam.get("enabled", True):
            continue
        enabled.append(exam["exam_id"])
        infos.append({
            "id": exam["exam_id"],
            "name": exam.get("exam_name", exam["exam_id"].upper()),
            "display_name": exam.get("display_name", exam.get("exam_name")),
            "tagline": exam.get("tagline", ""),
        })
    return {"enabled": enabled, "exams": infos}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--exam", help="build only this exam's bundle")
    args = ap.parse_args()

    ASSETS.mkdir(parents=True, exist_ok=True)
    for exam_dir in exam_dirs():
        exam_id = exam_dir.name
        if args.exam and exam_id != args.exam:
            continue
        bundle = build_exam(exam_id)
        out = ASSETS / f"{exam_id}.bundle.json"
        out.write_text(json.dumps(bundle, ensure_ascii=False, separators=(",", ":")))
        print(f"wrote {out.relative_to(ROOT)}  "
              f"({len(bundle['lessons'])} lessons, {len(bundle['questions'])} questions, "
              f"{out.stat().st_size // 1024} KB)")
    index = exams_index()
    (ASSETS / "exams.json").write_text(json.dumps(index, indent=2) + "\n")
    print(f"enabled exams: {index['enabled']}")


if __name__ == "__main__":
    main()
