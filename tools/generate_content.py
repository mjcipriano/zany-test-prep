#!/usr/bin/env python3
"""Generate the full SAT content bank (50 lessons, 1000+ questions).

Writes canonical, schema-conforming JSON into content/exams/sat/ and a manifest.
Deterministic: a fixed seed makes regeneration reproducible. Re-run any time:

    python tools/generate_content.py

Then validate with tools/validate_content.py and bundle with tools/build_bundle.py.
"""
from __future__ import annotations

import json
import random
import sys
from pathlib import Path

import yaml

sys.path.insert(0, str(Path(__file__).resolve().parent))
from content_gen import math_gen, rw_gen, passages  # noqa: E402
from content_gen.teaching import TEACHING  # noqa: E402
from content_gen.util import item_signature  # noqa: E402

ROOT = Path(__file__).resolve().parent.parent
SAT = ROOT / "content" / "exams" / "sat"
VERSION = "1.0.0"
SEED = 20240614

EXAM_ID = "sat"
EXAM_NAME = "SAT"


def slug(s: str) -> str:
    return s.replace("_", "-")


def load_skill_index():
    """Map skill_id -> (domain_id, section_id) from skills.yaml."""
    data = yaml.safe_load((SAT / "skills.yaml").read_text())
    idx = {}
    for dom in data["domains"]:
        for sec in dom["sections"]:
            for sk in sec["skills"]:
                idx[sk["id"]] = (dom["id"], sec["id"])
    return idx


def difficulties_for(n: int, base: str):
    """Build a difficulty ramp for a lesson of n questions."""
    if base == "easy":
        pattern = ["easy"] * 6 + ["medium"] * 3 + ["easy"]
    elif base == "medium":
        pattern = ["easy"] * 2 + ["medium"] * 5 + ["hard"] * 3
    else:  # hard
        pattern = ["medium"] * 3 + ["hard"] * 7
    return [pattern[i % len(pattern)] for i in range(n)]


# ---- Lesson plan -----------------------------------------------------------
# Each entry: (skill, level, base_difficulty, n_questions, kind, source)
#   kind "math"            -> source is a math_gen function
#   kind "rw_combinatorial"-> source is an rw_gen single-item function
#   kind "rw_pool"         -> source is a key into POOLS
#   kind "reading"         -> source is a reading skill key for passages.build_reading
#   kind "cross_text"      -> source is None
MATH_PLAN = [
    ("linear_equations", 1, "easy", 20, "math", math_gen.linear_equations),
    ("linear_equations", 2, "medium", 20, "math", math_gen.linear_equations),
    ("linear_inequalities", 1, "easy", 20, "math", math_gen.linear_inequalities),
    ("systems_of_equations", 1, "medium", 20, "math", math_gen.systems_of_equations),
    ("systems_of_equations", 2, "hard", 20, "math", math_gen.systems_of_equations),
    ("functions", 1, "easy", 20, "math", math_gen.functions),
    ("functions", 2, "hard", 20, "math", math_gen.functions),
    ("quadratics", 1, "medium", 20, "math", math_gen.quadratics),
    ("quadratics", 2, "hard", 20, "math", math_gen.quadratics),
    ("exponents_radicals", 1, "easy", 20, "math", math_gen.exponents_radicals),
    ("exponents_radicals", 2, "medium", 20, "math", math_gen.exponents_radicals),
    ("polynomials", 1, "medium", 20, "math", math_gen.polynomials),
    ("ratios_percentages_units", 1, "easy", 20, "math", math_gen.ratios_percentages_units),
    ("ratios_percentages_units", 2, "medium", 20, "math", math_gen.ratios_percentages_units),
    ("proportions", 1, "easy", 20, "math", math_gen.proportions),
    ("data_analysis", 1, "easy", 20, "math", math_gen.data_analysis),
    ("data_analysis", 2, "medium", 20, "math", math_gen.data_analysis),
    ("statistics", 1, "easy", 20, "math", math_gen.statistics),
    ("statistics", 2, "medium", 20, "math", math_gen.statistics),
    ("probability", 1, "medium", 20, "math", math_gen.probability),
    ("area_volume", 1, "easy", 20, "math", math_gen.area_volume),
    ("area_volume", 2, "hard", 20, "math", math_gen.area_volume),
    ("circles", 1, "medium", 20, "math", math_gen.circles),
    ("right_triangles", 1, "medium", 20, "math", math_gen.right_triangles),
    ("trigonometry", 1, "hard", 20, "math", math_gen.trigonometry),
]

RW_PLAN = [
    ("main_idea", 1, "easy", 16, "reading", "main_idea"),
    ("inferences", 1, "medium", 16, "reading", "inference"),
    ("command_of_evidence", 1, "medium", 16, "reading", "evidence"),
    ("text_structure_purpose", 1, "medium", 16, "reading", "structure"),
    ("words_in_context", 1, "easy", 16, "reading", "wic"),
    ("cross_text_connections", 1, "hard", 16, "cross_text", None),
    ("sentence_boundaries", 1, "easy", 25, "rw_combinatorial", rw_gen.gen_boundaries),
    ("sentence_boundaries", 2, "medium", 25, "rw_combinatorial", rw_gen.gen_boundaries),
    ("sentence_boundaries", 3, "medium", 25, "rw_combinatorial", rw_gen.gen_boundaries),
    ("sentence_boundaries", 4, "hard", 25, "rw_combinatorial", rw_gen.gen_boundaries),
    ("subject_verb_agreement", 1, "easy", 25, "rw_combinatorial", rw_gen.gen_sva),
    ("subject_verb_agreement", 2, "medium", 25, "rw_combinatorial", rw_gen.gen_sva),
    ("subject_verb_agreement", 3, "medium", 25, "rw_combinatorial", rw_gen.gen_sva),
    ("subject_verb_agreement", 4, "hard", 25, "rw_combinatorial", rw_gen.gen_sva),
    ("punctuation", 1, "easy", 25, "rw_combinatorial", rw_gen.gen_punctuation),
    ("punctuation", 2, "medium", 25, "rw_combinatorial", rw_gen.gen_punctuation),
    ("punctuation", 3, "hard", 25, "rw_combinatorial", rw_gen.gen_punctuation),
    ("pronouns", 1, "medium", 25, "rw_combinatorial", rw_gen.gen_pronouns),
    ("pronouns", 2, "hard", 25, "rw_combinatorial", rw_gen.gen_pronouns),
    ("modifiers", 1, "medium", 16, "rw_combinatorial", rw_gen.gen_modifiers),
    ("transitions", 1, "easy", 15, "rw_pool", "transitions"),
    ("transitions", 2, "medium", 15, "rw_pool", "transitions"),
    ("concision", 1, "easy", 12, "rw_pool", "concision"),
    ("concision", 2, "medium", 12, "rw_pool", "concision"),
    ("rhetorical_synthesis", 1, "medium", 12, "rw_pool", "synthesis"),
]
# skill -> nice section name mapping comes from skills.yaml section ids.

DOMAIN_SLUG = {"reading_writing": "rw", "math": "math"}

SKILL_TITLES = {
    "linear_equations": "Linear Equations", "linear_inequalities": "Linear Inequalities",
    "systems_of_equations": "Systems of Equations", "functions": "Functions",
    "quadratics": "Quadratics", "exponents_radicals": "Exponents & Radicals",
    "polynomials": "Polynomials", "ratios_percentages_units": "Percentages & Ratios",
    "proportions": "Proportions & Rates", "data_analysis": "Data Analysis",
    "statistics": "Statistics", "probability": "Probability",
    "area_volume": "Area & Volume", "circles": "Circles",
    "right_triangles": "Right Triangles", "trigonometry": "Trigonometry",
    "main_idea": "Main Idea", "inferences": "Inferences",
    "command_of_evidence": "Command of Evidence",
    "text_structure_purpose": "Text Structure & Purpose",
    "words_in_context": "Words in Context",
    "cross_text_connections": "Cross-Text Connections",
    "sentence_boundaries": "Sentence Boundaries",
    "subject_verb_agreement": "Subject-Verb Agreement",
    "punctuation": "Punctuation & Possessives", "pronouns": "Pronouns",
    "modifiers": "Modifier Placement", "transitions": "Transitions",
    "concision": "Concision", "rhetorical_synthesis": "Rhetorical Synthesis",
}
LEVEL_SUFFIX = {1: "", 2: " II", 3: " III"}


def build():
    rng = random.Random(SEED)
    skill_index = load_skill_index()
    seen_keys = set()

    # Pre-build pools and reading sources.
    pools = {
        "transitions": rw_gen.pool_transitions(rng),
        "concision": rw_gen.pool_concision(rng),
        "synthesis": rw_gen.pool_synthesis(rng),
    }
    for k in pools:
        rng.shuffle(pools[k])
    pool_cursor = {k: 0 for k in pools}
    reading_sources = {key: passages.build_reading(key, rng)
                       for key in ("main_idea", "inference", "evidence",
                                   "structure", "wic")}
    cross_text_items = passages.build_cross_text(rng)

    lessons = []
    questions_by_lesson = {}

    def finalize_question(body, lesson, qid, difficulty):
        domain, section = skill_index[lesson["skill"]]
        q = {
            "question_id": qid,
            "exam_id": EXAM_ID, "exam_name": EXAM_NAME,
            "domain": domain, "section": section,
            "skill": lesson["skill"],
            "lesson_id": lesson["lesson_id"],
            "difficulty": difficulty,
            "version": VERSION,
        }
        q.update(body)
        # difficulty in body would be absent; ensure ordering/required fields exist.
        q["difficulty"] = difficulty
        if "subskill" in q and not q["subskill"]:
            del q["subskill"]
        return q

    def process_plan(plan, domain_id):
        order = 0
        prev_lesson_id = None
        for skill, level, base, n, kind, source in plan:
            domain, section = skill_index[skill]
            lesson_id = f"sat-{DOMAIN_SLUG[domain]}-{slug(skill)}-{level}"
            title = SKILL_TITLES[skill] + LEVEL_SUFFIX.get(level, f" {level}")
            tcard = dict(TEACHING[skill])
            if level > 1:
                tcard = dict(tcard)
                tcard["title"] = tcard["title"] + f" (Level {level})"
            lesson = {
                "lesson_id": lesson_id, "exam_id": EXAM_ID, "exam_name": EXAM_NAME,
                "domain": domain, "section": section, "skill": skill,
                "title": title, "order": order, "difficulty": base,
                "teaching_card": tcard,
                "question_ids": [], "prerequisite_lesson_ids":
                    [prev_lesson_id] if prev_lesson_id else [],
                "unlock_xp": 0, "tags": [domain, skill], "version": VERSION,
            }
            qs = []
            difficulties = difficulties_for(n, base)
            for i in range(n):
                qid = f"{lesson_id}-q{i + 1:02d}"
                diff = difficulties[i]
                if kind == "math":
                    body = _unique_generated(source, rng, diff, seen_keys)
                elif kind == "rw_combinatorial":
                    body = _unique_combinatorial(source, rng, seen_keys)
                    diff = base
                elif kind == "rw_pool":
                    body = pools[source][pool_cursor[source]]
                    pool_cursor[source] += 1
                    diff = base
                elif kind == "reading":
                    body = reading_sources[source].pop()
                    diff = base
                elif kind == "cross_text":
                    body = cross_text_items.pop()
                    diff = base
                else:
                    raise ValueError(kind)
                q = finalize_question(body, lesson, qid, diff)
                qs.append(q)
                lesson["question_ids"].append(qid)
            est_seconds = sum(q["estimated_time_seconds"] for q in qs)
            lesson["estimated_minutes"] = max(3, min(30, round(est_seconds / 60)))
            lessons.append(lesson)
            questions_by_lesson[lesson_id] = qs
            prev_lesson_id = lesson_id
            order += 1

    process_plan(MATH_PLAN, "math")
    process_plan(RW_PLAN, "reading_writing")
    return lessons, questions_by_lesson


def _unique_generated(fn, rng, difficulty, seen):
    for _ in range(400):
        body = fn(rng, difficulty)
        k = item_signature(body)
        if k not in seen:
            seen.add(k)
            return body
    raise RuntimeError(f"could not produce a unique item from {fn.__name__}")


def _unique_combinatorial(fn, rng, seen):
    for _ in range(800):
        body = fn(rng)
        k = item_signature(body)
        if k not in seen:
            seen.add(k)
            return body
    raise RuntimeError(f"could not produce a unique item from {fn.__name__}")


def write_all(lessons, questions_by_lesson):
    # Clean previous output dirs.
    for sub in ["lessons/rw", "lessons/math", "questions/rw", "questions/math"]:
        d = SAT / sub
        d.mkdir(parents=True, exist_ok=True)
        for f in d.glob("*.json"):
            f.unlink()

    manifest = {"exam_id": EXAM_ID, "version": VERSION, "lessons": [], "questions": []}
    for lesson in lessons:
        dom = DOMAIN_SLUG[lesson["domain"]]
        lpath = SAT / "lessons" / dom / f"{lesson['lesson_id']}.json"
        lpath.write_text(json.dumps(lesson, indent=2, ensure_ascii=False) + "\n")
        manifest["lessons"].append(str(lpath.relative_to(SAT)))
        qs = questions_by_lesson[lesson["lesson_id"]]
        qpath = SAT / "questions" / dom / f"{lesson['lesson_id']}.json"
        qpath.write_text(json.dumps(qs, indent=2, ensure_ascii=False) + "\n")
        manifest["questions"].append(str(qpath.relative_to(SAT)))
    (SAT / "manifest.json").write_text(json.dumps(manifest, indent=2) + "\n")


def main():
    lessons, qbl = build()
    write_all(lessons, qbl)
    total_q = sum(len(v) for v in qbl.values())
    math_q = sum(len(v) for k, v in qbl.items() if "-math-" in k)
    rw_q = total_q - math_q
    print(f"Lessons: {len(lessons)}")
    print(f"Questions: {total_q}  (math {math_q}, reading/writing {rw_q})")
    print(f"Written under {SAT.relative_to(ROOT)}/")


if __name__ == "__main__":
    main()
