#!/usr/bin/env python3
"""Build the Flutter asset bundle(s) from the canonical content.

Reads content/exams/<exam>/ (manifest + lessons + questions + exam.yaml +
skills.yaml) and writes a single JSON bundle per exam into
assets/content/<exam>.bundle.json, plus assets/content/exams.json listing the
enabled exams. The app loads these bundles at startup for fast offline access.

    python tools/build_bundle.py
"""
from __future__ import annotations

import json
from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parent.parent
CONTENT = ROOT / "content"
ASSETS = ROOT / "assets" / "content"


def build_exam(exam_id: str) -> dict:
    sat = CONTENT / "exams" / exam_id
    exam = yaml.safe_load((sat / "exam.yaml").read_text())
    skills = yaml.safe_load((sat / "skills.yaml").read_text())
    manifest = json.loads((sat / "manifest.json").read_text())

    lessons = [json.loads((sat / rel).read_text()) for rel in manifest["lessons"]]
    questions = []
    for rel in manifest["questions"]:
        questions.extend(json.loads((sat / rel).read_text()))

    lessons.sort(key=lambda l: (0 if l["domain"] == "reading_writing" else 1, l["order"]))
    return {
        "schema_version": 1,
        "exam": exam,
        "skills": skills,
        "lessons": lessons,
        "questions": questions,
    }


def main():
    ASSETS.mkdir(parents=True, exist_ok=True)
    enabled = []
    for exam_dir in sorted((CONTENT / "exams").iterdir()):
        if not exam_dir.is_dir():
            continue
        exam_id = exam_dir.name
        bundle = build_exam(exam_id)
        if bundle["exam"].get("enabled", True):
            enabled.append(exam_id)
        out = ASSETS / f"{exam_id}.bundle.json"
        out.write_text(json.dumps(bundle, ensure_ascii=False, separators=(",", ":")))
        print(f"wrote {out.relative_to(ROOT)}  "
              f"({len(bundle['lessons'])} lessons, {len(bundle['questions'])} questions, "
              f"{out.stat().st_size // 1024} KB)")
    (ASSETS / "exams.json").write_text(json.dumps({"enabled": enabled}, indent=2))
    print(f"enabled exams: {enabled}")


if __name__ == "__main__":
    main()
