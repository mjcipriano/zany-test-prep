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
from content_gen import math_gen, rw_gen, passages, math_extra, rw_extra  # noqa: E402
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


# ---- Lesson plan -----------------------------------------------------------
# Each skill is an INDEPENDENT track: the learner can pick any subject area and
# progress through its difficulty tiers (easy -> medium -> hard). Within a skill,
# each tier requires the previous tier of the SAME skill; the first tier of every
# skill is open from the start, so unlocking one section is never required to
# start another.
#
# Each SKILLS entry: (skill, kind, source, tiers)
#   tiers = [(difficulty, n_questions), ...] in unlock order
#   kind "math"            -> source is a math_gen function (uses difficulty)
#   kind "rw_combinatorial"-> source is an rw_gen single-item function (uses difficulty)
#   kind "rw_pool"         -> source is a key into POOLS (drawn in order)
#   kind "reading"         -> source is a reading skill key for passages.build_reading
#   kind "cross_text"      -> source is None
STD3 = [("easy", 20), ("medium", 20), ("hard", 20)]   # generators with wide spaces
SMALL3 = [("easy", 8), ("medium", 8), ("hard", 8)]    # smaller-space math skills
CONV3 = [("easy", 24), ("medium", 24), ("hard", 24)]  # combinatorial conventions
READ3 = [("easy", 8), ("medium", 8), ("hard", 8)]     # 32 authored items -> 3 tiers

MATH_SKILLS = [
    ("linear_equations", "math", math_gen.linear_equations, STD3),
    ("linear_inequalities", "math", math_gen.linear_inequalities, STD3),
    ("systems_of_equations", "math", math_gen.systems_of_equations, STD3),
    ("functions", "math", math_gen.functions, STD3),
    ("quadratics", "math", math_gen.quadratics, STD3),
    ("exponents_radicals", "math", math_gen.exponents_radicals, STD3),
    ("polynomials", "math", math_gen.polynomials, STD3),
    ("ratios_percentages_units", "math", math_gen.ratios_percentages_units, STD3),
    ("proportions", "math", math_gen.proportions, STD3),
    ("data_analysis", "math", math_gen.data_analysis, STD3),
    ("statistics", "math", math_gen.statistics, STD3),
    ("probability", "math", math_gen.probability, STD3),
    ("area_volume", "math", math_gen.area_volume, STD3),
    ("circles", "math", math_gen.circles, SMALL3),
    ("right_triangles", "math", math_gen.right_triangles, SMALL3),
    ("trigonometry", "math", math_gen.trigonometry, SMALL3),
    ("word_problems", "math", math_extra.word_problems, STD3),
    ("absolute_value", "math", math_extra.absolute_value, STD3),
    ("exponential", "math", math_extra.exponential_growth, STD3),
    ("two_way_tables", "math", math_extra.two_way_tables, STD3),
    ("scatterplots", "math", math_extra.line_of_best_fit, STD3),
]

RW_SKILLS = [
    ("main_idea", "reading", "main_idea", READ3),
    ("inferences", "reading", "inference", READ3),
    ("command_of_evidence", "reading", "evidence", READ3),
    ("text_structure_purpose", "reading", "structure", READ3),
    ("words_in_context", "reading", "wic", READ3),
    ("cross_text_connections", "cross_text", None, READ3),
    ("quantitative_evidence", "rw_combinatorial", rw_extra.gen_quantitative_evidence, CONV3),
    ("sentence_boundaries", "rw_combinatorial", rw_gen.gen_boundaries, CONV3),
    ("subject_verb_agreement", "rw_combinatorial", rw_gen.gen_sva, CONV3),
    ("punctuation", "rw_combinatorial", rw_gen.gen_punctuation, CONV3),
    ("pronouns", "rw_combinatorial", rw_gen.gen_pronouns, CONV3),
    ("modifiers", "rw_combinatorial", rw_gen.gen_modifiers,
     [("easy", 8), ("medium", 8), ("hard", 8)]),
    ("verb_tense", "rw_combinatorial", rw_extra.gen_verb_tense, CONV3),
    ("parallel_structure", "rw_combinatorial", rw_extra.gen_parallelism, CONV3),
    ("pronoun_antecedent", "rw_combinatorial", rw_extra.gen_pronoun_antecedent, CONV3),
    ("transitions", "rw_combinatorial", rw_gen.gen_transition,
     [("easy", 16), ("medium", 16), ("hard", 16)]),
    ("concision", "rw_pool", "concision",
     [("easy", 16), ("medium", 16), ("hard", 16)]),
    ("rhetorical_synthesis", "rw_pool", "synthesis",
     [("easy", 11), ("medium", 11), ("hard", 11)]),
]

DIFF_LABEL = {"easy": "Easy", "medium": "Medium", "hard": "Hard"}

DOMAIN_SLUG = {"reading_writing": "rw", "math": "math"}

# Extra "practice bank" questions per (skill, difficulty) beyond the curated
# lessons. These are not listed in any lesson; the practice modes draw from them
# for near-endless variety. Best-effort: generation stops when a skill's space is
# exhausted. Authored pools/reading are not banked. Small-space math is skipped.
BANK_PER_TIER = {"math": 200, "rw_combinatorial": 800}
NO_BANK_SKILLS = {"circles", "right_triangles", "trigonometry"}

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
    "verb_tense": "Verb Tense & Form", "parallel_structure": "Parallel Structure",
    "pronoun_antecedent": "Pronoun-Antecedent Agreement",
    "quantitative_evidence": "Quantitative Evidence",
    "word_problems": "Linear Word Problems", "absolute_value": "Absolute Value",
    "exponential": "Exponential Growth", "two_way_tables": "Two-Way Tables",
    "scatterplots": "Scatterplots & Best Fit",
}
def build():
    rng = random.Random(SEED)
    skill_index = load_skill_index()
    seen_keys = set()

    # Pre-build pools and reading sources.
    pools = {
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

    order_counter = [0]

    def process_skills(skill_specs):
        for skill, kind, source, tiers in skill_specs:
            domain, section = skill_index[skill]
            prev_lesson_id = None  # per-skill chain; resets for each skill
            for diff, n in tiers:
                lesson_id = f"sat-{DOMAIN_SLUG[domain]}-{slug(skill)}-{diff}"
                tcard = dict(TEACHING[skill])
                tcard["title"] = f"{tcard['title']} ({DIFF_LABEL[diff]})"
                lesson = {
                    "lesson_id": lesson_id, "exam_id": EXAM_ID, "exam_name": EXAM_NAME,
                    "domain": domain, "section": section, "skill": skill,
                    "title": f"{SKILL_TITLES[skill]} · {DIFF_LABEL[diff]}",
                    "order": order_counter[0], "difficulty": diff,
                    "teaching_card": tcard,
                    "question_ids": [],
                    "prerequisite_lesson_ids": [prev_lesson_id] if prev_lesson_id else [],
                    "unlock_xp": 0, "tags": [domain, skill, diff], "version": VERSION,
                }
                qs = []
                for i in range(n):
                    qid = f"{lesson_id}-q{i + 1:02d}"
                    if kind == "math":
                        body = _unique_generated(source, rng, diff, seen_keys)
                    elif kind == "rw_combinatorial":
                        body = _unique_combinatorial(source, rng, diff, seen_keys)
                    elif kind == "rw_pool":
                        body = pools[source][pool_cursor[source]]
                        pool_cursor[source] += 1
                    elif kind == "reading":
                        body = reading_sources[source].pop()
                    elif kind == "cross_text":
                        body = cross_text_items.pop()
                    else:
                        raise ValueError(kind)
                    qs.append(finalize_question(body, lesson, qid, diff))
                    lesson["question_ids"].append(qid)
                est_seconds = sum(q["estimated_time_seconds"] for q in qs)
                lesson["estimated_minutes"] = max(3, min(30, round(est_seconds / 60)))
                lessons.append(lesson)
                questions_by_lesson[lesson_id] = qs
                prev_lesson_id = lesson_id
                order_counter[0] += 1

    process_skills(MATH_SKILLS)
    process_skills(RW_SKILLS)

    # ---- Practice bank (best-effort, not tied to lesson question lists) ----
    bank_files = {}  # file_stem -> (domain, [questions])

    def build_bank(skill_specs):
        for skill, kind, source, tiers in skill_specs:
            if kind not in BANK_PER_TIER or skill in NO_BANK_SKILLS:
                continue
            domain, section = skill_index[skill]
            stub = {"skill": skill}
            for diff, _n in tiers:
                lesson_id = f"sat-{DOMAIN_SLUG[domain]}-{slug(skill)}-{diff}"
                stub_lesson = {"skill": skill, "lesson_id": lesson_id}
                target = BANK_PER_TIER[kind]
                qs = []
                fails = 0
                idx = 1
                while len(qs) < target and fails < 600:
                    body = source(rng, diff)
                    k = item_signature(body)
                    if k in seen_keys:
                        fails += 1
                        continue
                    seen_keys.add(k)
                    fails = 0
                    qid = f"{lesson_id}-b{idx:04d}"
                    idx += 1
                    qs.append(finalize_question(body, stub_lesson, qid, diff))
                if qs:
                    bank_files[f"{lesson_id}-bank"] = (domain, qs)

    build_bank(MATH_SKILLS)
    build_bank(RW_SKILLS)
    return lessons, questions_by_lesson, bank_files


def _unique_generated(fn, rng, difficulty, seen):
    for _ in range(400):
        body = fn(rng, difficulty)
        k = item_signature(body)
        if k not in seen:
            seen.add(k)
            return body
    raise RuntimeError(f"could not produce a unique item from {fn.__name__}")


def _unique_combinatorial(fn, rng, difficulty, seen):
    for _ in range(1200):
        body = fn(rng, difficulty)
        k = item_signature(body)
        if k not in seen:
            seen.add(k)
            return body
    raise RuntimeError(f"could not produce a unique item from {fn.__name__}")


def write_all(lessons, questions_by_lesson, bank_files):
    # Clean previous output dirs.
    for sub in ["lessons/rw", "lessons/math", "questions/rw", "questions/math",
                "questions/bank/rw", "questions/bank/math"]:
        d = SAT / sub
        d.mkdir(parents=True, exist_ok=True)
        for f in d.glob("*.json"):
            f.unlink()

    manifest = {"exam_id": EXAM_ID, "version": VERSION, "lessons": [],
                "questions": [], "bank": []}
    for lesson in lessons:
        dom = DOMAIN_SLUG[lesson["domain"]]
        lpath = SAT / "lessons" / dom / f"{lesson['lesson_id']}.json"
        lpath.write_text(json.dumps(lesson, indent=2, ensure_ascii=False) + "\n")
        manifest["lessons"].append(str(lpath.relative_to(SAT)))
        qs = questions_by_lesson[lesson["lesson_id"]]
        qpath = SAT / "questions" / dom / f"{lesson['lesson_id']}.json"
        qpath.write_text(json.dumps(qs, indent=2, ensure_ascii=False) + "\n")
        manifest["questions"].append(str(qpath.relative_to(SAT)))
    for stem, (domain, qs) in sorted(bank_files.items()):
        dom = DOMAIN_SLUG[domain]
        bpath = SAT / "questions" / "bank" / dom / f"{stem}.json"
        bpath.write_text(json.dumps(qs, indent=2, ensure_ascii=False) + "\n")
        manifest["bank"].append(str(bpath.relative_to(SAT)))
    (SAT / "manifest.json").write_text(json.dumps(manifest, indent=2) + "\n")


def main():
    lessons, qbl, bank = build()
    write_all(lessons, qbl, bank)
    lesson_q = sum(len(v) for v in qbl.values())
    bank_q = sum(len(v) for _, v in bank.values())
    total_q = lesson_q + bank_q
    math_q = (sum(len(v) for k, v in qbl.items() if "-math-" in k)
              + sum(len(v) for k, (_, v) in bank.items() if "-math-" in k))
    rw_q = total_q - math_q
    print(f"Lessons: {len(lessons)}")
    print(f"Lesson questions: {lesson_q}  Bank questions: {bank_q}")
    print(f"Total questions: {total_q}  (math {math_q}, reading/writing {rw_q})")
    print(f"Written under {SAT.relative_to(ROOT)}/")


if __name__ == "__main__":
    main()
