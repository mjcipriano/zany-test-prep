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
    python tools/build_bundle.py --bump     # also bump content_version where content changed

Content versioning
------------------
Each exam's `content_version` (exam.yaml) must change whenever its content does.
The builder fingerprints every bundle (all lessons, questions, skills and exam
metadata except the version itself) and records `{content_version, fingerprint}`
in content/exams/<exam>/content.lock.json. If the content changed but the version
did not, the build fails with a message telling you to bump it — or pass
`--bump` (optionally `--bump-part major|minor|patch`, default minor) and the
builder edits exam.yaml for you. CI runs the builder without `--bump`, so a
forgotten bump fails CI. The fingerprint is also embedded in the bundle and
shown on the About screen next to the version.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import re
import sys
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


LOCK_NAME = "content.lock.json"
VERSION_RE = re.compile(r'^(content_version:\s*)"?(\d+)\.(\d+)\.(\d+)"?', re.M)


def content_fingerprint(bundle: dict) -> str:
    """Stable hash of a bundle's content, ignoring the content version and the
    fingerprint field itself (so bumping the version never changes it)."""
    exam = {k: v for k, v in bundle["exam"].items()
            if k not in ("content_version", "content_fingerprint")}
    payload = {**bundle, "exam": exam}
    raw = json.dumps(payload, sort_keys=True, ensure_ascii=False, separators=(",", ":"))
    return hashlib.sha256(raw.encode("utf-8")).hexdigest()[:16]


def bump_version(version: str, part: str = "minor") -> str:
    major, minor, patch = (int(x) for x in version.split("."))
    if part == "major":
        return f"{major + 1}.0.0"
    if part == "patch":
        return f"{major}.{minor}.{patch + 1}"
    return f"{major}.{minor + 1}.0"


def set_content_version(exam_yaml: Path, version: str) -> None:
    """Rewrite content_version in exam.yaml in place (keeps comments)."""
    text = exam_yaml.read_text()
    new, n = VERSION_RE.subn(lambda m: f'{m.group(1)}"{version}"', text, count=1)
    if n != 1:
        raise SystemExit(f"{exam_yaml}: no content_version line to bump")
    exam_yaml.write_text(new)


class ContentVersionError(Exception):
    pass


def reconcile_lock(exam_dir: Path, version: str, fingerprint: str, *,
                   bump: bool = False, part: str = "minor") -> tuple[str, str]:
    """Compare the content against content.lock.json.

    Returns (content_version, action) where action is one of
    "created", "unchanged", "recorded" (content changed and the version had
    already been bumped), or "bumped" (content changed; exam.yaml was bumped).
    Raises ContentVersionError when content changed but the version did not and
    bump is False. The caller rebuilds the bundle after a bump.
    """
    lock_path = exam_dir / LOCK_NAME
    lock = json.loads(lock_path.read_text()) if lock_path.exists() else None
    action = "unchanged"
    if lock is None:
        action = "created"
    elif lock.get("fingerprint") != fingerprint:
        if lock.get("content_version") != version:
            action = "recorded"
        elif bump:
            version = bump_version(version, part)
            set_content_version(exam_dir / "exam.yaml", version)
            action = "bumped"
        else:
            raise ContentVersionError(
                f"{exam_dir.name}: content changed since content_version "
                f"{version} (fingerprint {lock.get('fingerprint')} -> {fingerprint}). "
                f"Bump content_version in {exam_dir.name}/exam.yaml, or rerun "
                f"`python tools/build_bundle.py --bump`.")
    elif lock.get("content_version") != version:
        action = "recorded"  # version bumped without a content change: allowed
    lock_path.write_text(json.dumps(
        {"content_version": version, "fingerprint": fingerprint}, indent=2) + "\n")
    return version, action


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
    bundle = {
        "schema_version": 1,
        "exam": exam,
        "skills": skills,
        "lessons": lessons,
        "questions": questions,
    }
    bundle["exam"]["content_fingerprint"] = content_fingerprint(bundle)
    return bundle


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
    ap.add_argument("--bump", action="store_true",
                    help="bump content_version in exam.yaml for exams whose content changed")
    ap.add_argument("--bump-part", choices=["major", "minor", "patch"], default="minor",
                    help="which part of content_version --bump increments (default minor)")
    args = ap.parse_args()

    ASSETS.mkdir(parents=True, exist_ok=True)
    for exam_dir in exam_dirs():
        exam_id = exam_dir.name
        if args.exam and exam_id != args.exam:
            continue
        bundle = build_exam(exam_id)
        try:
            version, action = reconcile_lock(
                exam_dir, str(bundle["exam"].get("content_version", "1.0.0")),
                bundle["exam"]["content_fingerprint"],
                bump=args.bump, part=args.bump_part)
        except ContentVersionError as e:
            print(f"ERROR: {e}", file=sys.stderr)
            raise SystemExit(1)
        if action == "bumped":
            bundle = build_exam(exam_id)  # pick up the new version
        print(f"{exam_id}: content_version {version} "
              f"(fingerprint {bundle['exam']['content_fingerprint']}, {action})")
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
