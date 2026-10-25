"""Shared helpers for the Python content-tool tests.

Run the whole suite from the repo root with:

    python -m unittest discover -s tools/tests -t .

Tests import the generators as ``from content_gen import ...`` after this
module puts ``tools/`` on ``sys.path``.
"""
from __future__ import annotations

import json
import random
import zlib
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
TOOLS = ROOT / "tools"
if str(TOOLS) not in sys.path:
    sys.path.insert(0, str(TOOLS))

from jsonschema import Draft7Validator  # noqa: E402

from content_gen import registry  # noqa: E402

_Q_SCHEMA = json.loads((ROOT / "content" / "schemas" / "question.schema.json").read_text())
_Q_VALIDATOR = Draft7Validator(_Q_SCHEMA)

DIFFICULTIES = registry.DIFFICULTIES


def as_question(body: dict, *, exam_id="sat", skill="skill", difficulty="medium") -> dict:
    """Wrap a generator body in the metadata the orchestrator normally adds."""
    q = {
        "question_id": "test-q-01",
        "exam_id": exam_id, "exam_name": exam_id.upper(),
        "domain": "math", "section": "algebra", "skill": skill,
        "lesson_id": "test-lesson", "difficulty": difficulty, "version": "1.0.0",
    }
    q.update(body)
    q["difficulty"] = difficulty
    if "subskill" in q and not q["subskill"]:
        del q["subskill"]
    return q


def body_problems(body: dict) -> list[str]:
    """Everything wrong with a generator body: schema errors + semantic checks."""
    q = as_question(body)
    problems = [f"schema: {e.message}" for e in _Q_VALIDATOR.iter_errors(q)]
    if not str(q.get("explanation", "")).strip():
        problems.append("missing explanation")
    if q.get("question_type") == "student_produced":
        ans = q.get("answer") or {}
        if not ans.get("accepted"):
            problems.append("student_produced without accepted answers")
        for a in ans.get("accepted", []):
            if not re.fullmatch(r"-?\d+(\.\d+)?|-?\d+/\d+", str(a).strip()):
                problems.append(f"accepted answer {a!r} is not numeric")
    else:
        choices = q.get("choices") or []
        ids = [c["id"] for c in choices]
        texts = [c["text"].strip() for c in choices]
        if len(ids) != len(set(ids)):
            problems.append("duplicate choice ids")
        if len(texts) != len(set(texts)):
            problems.append(f"duplicate choice texts: {texts}")
        if q.get("correct_choice") not in ids:
            problems.append("correct_choice not among choices")
        for c in choices:
            if not str(c.get("rationale", "")).strip():
                problems.append(f"choice {c['id']} missing rationale")
    for pat in (r"\bTODO\b", r"\bTBD\b", r"\bFIXME\b", r"lorem ipsum", r"\bxxx+\b"):
        for text in [q.get("prompt", ""), q.get("explanation", "")] + [
                c["text"] for c in q.get("choices", [])]:
            if re.search(pat, str(text), re.IGNORECASE):
                problems.append(f"placeholder text /{pat}/ in {text[:40]!r}")
    return problems


def assert_valid_body(testcase, body: dict, where: str = ""):
    problems = body_problems(body)
    testcase.assertEqual(problems, [], f"{where}: {problems}\n{json.dumps(body, indent=1)[:1500]}")


def shape(text: str) -> str:
    """A prompt's template shape: digits -> '#', case/space-insensitive."""
    s = str(text).lower().replace("−", "-")
    s = re.sub(r"\d+(\.\d+)?", "#", s)
    s = re.sub(r"\s+", " ", s).strip()
    return s


def sample_family(fn, difficulty: str, n: int, seed: int = 1) -> list[dict]:
    """Generate ``n`` bodies from one family with a fixed seed (family-tagged)."""
    rng = random.Random(seed)
    return [registry.run_family(fn, rng, difficulty) for _ in range(n)]


def unique_signatures(bodies: list[dict]) -> int:
    from content_gen.util import item_signature
    return len({item_signature(b) for b in bodies})


def check_family_table(testcase, table, *, samples=25, min_families=1):
    """Every family in ``table`` must produce schema-valid, varied items on
    every difficulty it is registered for."""
    problems = registry.validate_table(table, min_per_tier=min_families)
    testcase.assertEqual(problems, [])
    for skill, by_diff in table.items():
        for diff in DIFFICULTIES:
            for fn in by_diff.get(diff, []):
                # crc32, not hash(): str hashes are randomised per process, which
                # made each test run exercise different draws (flaky failures).
                bodies = sample_family(fn, diff, samples, seed=zlib.crc32(f"{skill}/{diff}".encode()) & 0xFFFF)
                for i, b in enumerate(bodies):
                    assert_valid_body(testcase, b, f"{skill}/{diff}/{registry.family_name(fn)}#{i}")
                    testcase.assertIn(f"family:{registry.family_name(fn)}", b["tags"])
