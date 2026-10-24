#!/usr/bin/env python3
"""Generate the content bank for one or every exam.

Writes canonical, schema-conforming JSON into content/exams/<exam>/ and a
manifest. Deterministic: each exam plan has a fixed seed so regeneration is
reproducible. Re-run any time:

    python tools/generate_content.py              # every exam (sat, act)
    python tools/generate_content.py --exam act   # one exam

Then validate with tools/validate_content.py and bundle with
tools/build_bundle.py. Lesson planning lives in tools/content_gen/exam_plans.py;
question families live in tools/content_gen/*_gen.py (see registry.py).
"""
from __future__ import annotations

import argparse
import json
import random
import sys
from pathlib import Path

import yaml

sys.path.insert(0, str(Path(__file__).resolve().parent))
from content_gen import registry, util, passages, rw_gen  # noqa: E402
from content_gen.exam_plans import PLANS, ExamPlan, SkillSpec  # noqa: E402
from content_gen.util import item_signature  # noqa: E402

ROOT = Path(__file__).resolve().parent.parent
CONTENT = ROOT / "content" / "exams"
VERSION = "1.0.0"
DIFF_LABEL = {"easy": "Easy", "medium": "Medium", "hard": "Hard"}


# --------------------------------------------------------------------------- #
# Families + teaching, gathered from every generator module
# --------------------------------------------------------------------------- #
def _legacy_table(module, names) -> dict:
    """Wrap a module's legacy single-function generators as one-family tables
    (used until a module exposes FAMILIES)."""
    table = {}
    for skill, fn_name in names.items():
        fn = getattr(module, fn_name, None)
        if fn is None:
            continue
        table[skill] = {d: [fn] for d in registry.DIFFICULTIES}
    return table


def load_families() -> dict:
    """Merge every generator module's FAMILIES (falling back to legacy fns)."""
    from content_gen import math_gen, math_extra, rw_extra
    tables = []
    for mod, legacy in (
        (math_gen, {s: s for s in (
            "linear_equations", "linear_inequalities", "systems_of_equations",
            "functions", "quadratics", "exponents_radicals", "polynomials",
            "ratios_percentages_units", "proportions", "data_analysis", "statistics",
            "probability", "area_volume", "circles", "right_triangles", "trigonometry")}),
        (math_extra, {"word_problems": "word_problems", "absolute_value": "absolute_value",
                      "exponential": "exponential_growth", "two_way_tables": "two_way_tables",
                      "scatterplots": "line_of_best_fit"}),
        (rw_gen, {"sentence_boundaries": "gen_boundaries", "subject_verb_agreement": "gen_sva",
                  "punctuation": "gen_punctuation", "pronouns": "gen_pronouns",
                  "modifiers": "gen_modifiers", "transitions": "gen_transition"}),
        (rw_extra, {"verb_tense": "gen_verb_tense", "parallel_structure": "gen_parallelism",
                    "pronoun_antecedent": "gen_pronoun_antecedent",
                    "quantitative_evidence": "gen_quantitative_evidence"}),
    ):
        table = getattr(mod, "FAMILIES", None)
        tables.append(table if table else _legacy_table(mod, legacy))
    for name in ("math_act", "rw_act", "science_gen"):
        try:
            mod = __import__(f"content_gen.{name}", fromlist=["FAMILIES"])
        except ImportError:
            continue
        tables.append(getattr(mod, "FAMILIES", {}))
    return registry.merge(*tables)


def load_teaching() -> dict:
    from content_gen.teaching import TEACHING
    teaching = {k: dict(v) for k, v in TEACHING.items()}
    for name, attr in (("teaching_math_act", "TEACHING_ACT"),
                       ("teaching_rw_act", "TEACHING_ACT"),
                       ("teaching_science", "TEACHING_SCIENCE")):
        try:
            mod = __import__(f"content_gen.{name}", fromlist=[attr])
        except ImportError:
            continue
        for k, v in getattr(mod, attr, {}).items():
            teaching[k] = dict(v)
    return teaching


def load_skill_index(exam_id: str) -> dict:
    """Map skill_id -> (domain_id, section_id) from the exam's skills.yaml."""
    data = yaml.safe_load((CONTENT / exam_id / "skills.yaml").read_text())
    idx = {}
    for dom in data["domains"]:
        for sec in dom["sections"]:
            for sk in sec["skills"]:
                idx[sk["id"]] = (dom["id"], sec["id"])
    return idx


# --------------------------------------------------------------------------- #
# Building one exam
# --------------------------------------------------------------------------- #
class Builder:
    def __init__(self, plan: ExamPlan, families: dict, teaching: dict):
        self.plan = plan
        self.families = families
        self.teaching = teaching
        self.rng = random.Random(plan.seed)
        self.skill_index = load_skill_index(plan.exam_id)
        self.seen = set()
        self.pools = {
            "concision": rw_gen.pool_concision(self.rng),
            "synthesis": rw_gen.pool_synthesis(self.rng),
        }
        self.pool_cursor = {k: 0 for k in self.pools}
        self.reading = {key: passages.build_reading(key, self.rng)
                        for key in ("main_idea", "inference", "evidence", "structure", "wic")}
        self.cross_text = passages.build_cross_text(self.rng)
        self.lessons = []
        self.questions_by_lesson = {}
        self.bank_files = {}
        self.order = 0

    # ---- helpers ---------------------------------------------------------
    def lesson_id(self, spec: SkillSpec, diff: str) -> str:
        domain, _ = self.skill_index[spec.skill]
        return f"{self.plan.exam_id}-{self.plan.domain_slug[domain]}-{spec.skill.replace('_', '-')}-{diff}"

    def family_fns(self, spec: SkillSpec, diff: str, domain: str):
        fns = registry.families_for(self.families, spec.family_key, diff)
        kept = [fn for fn in fns if not self.plan.exclude_family(fn, domain)]
        if not kept:
            raise RuntimeError(f"{self.plan.exam_id}: no usable families for "
                               f"{spec.skill}/{diff}")
        return kept

    def finalize(self, body: dict, skill: str, lesson_id: str, qid: str, diff: str) -> dict:
        domain, section = self.skill_index[skill]
        q = {
            "question_id": qid,
            "exam_id": self.plan.exam_id, "exam_name": self.plan.exam_name,
            "domain": domain, "section": section, "skill": skill,
            "lesson_id": lesson_id, "difficulty": diff, "version": VERSION,
        }
        q.update(body)
        q["difficulty"] = diff
        if "subskill" in q and not q["subskill"]:
            del q["subskill"]
        return q

    def _draw(self, fns, diff: str, domain: str, index: int, *, tries: int):
        """Generate a unique, accepted body from a family (round-robin for
        lessons, random for the bank)."""
        util.set_option_count(self.plan.option_count_for(domain))
        order = [registry.round_robin(fns, index + k) for k in range(len(fns))]
        for attempt in range(tries):
            fn = order[0] if attempt < tries // 2 else order[attempt % len(order)]
            body = registry.run_family(fn, self.rng, diff)
            for tf in self.plan.transforms:
                body = tf(body, domain, self.rng)
            if not self.plan.accept_body(body, domain):
                continue
            k = item_signature(body)
            if k in self.seen:
                continue
            self.seen.add(k)
            return body
        return None

    def body_for(self, spec: SkillSpec, diff: str, domain: str, index: int):
        if spec.kind == "family":
            body = self._draw(self.family_fns(spec, diff, domain), diff, domain, index, tries=600)
            if body is None:
                raise RuntimeError(f"could not produce a unique {spec.skill}/{diff} item")
            return body
        if spec.kind == "rw_pool":
            pool = self.pools[spec.source]
            body = pool[self.pool_cursor[spec.source]]
            self.pool_cursor[spec.source] += 1
        elif spec.kind == "reading":
            body = self.reading[spec.source].pop()
        elif spec.kind == "cross_text":
            body = self.cross_text.pop()
        else:
            raise ValueError(spec.kind)
        util.set_option_count(self.plan.option_count_for(domain))
        for tf in self.plan.transforms:
            body = tf(body, domain, self.rng)
        self.seen.add(item_signature(body))
        return body

    # ---- lessons ---------------------------------------------------------
    def build_lessons(self):
        for spec in self.plan.skills:
            domain, section = self.skill_index[spec.skill]
            prev = None
            for diff, n in spec.tiers:
                lid = self.lesson_id(spec, diff)
                tcard = dict(self.teaching[spec.skill])
                tcard["title"] = f"{tcard['title']} ({DIFF_LABEL[diff]})"
                lesson = {
                    "lesson_id": lid, "exam_id": self.plan.exam_id,
                    "exam_name": self.plan.exam_name,
                    "domain": domain, "section": section, "skill": spec.skill,
                    "title": f"{self.plan.skill_titles[spec.skill]} · {DIFF_LABEL[diff]}",
                    "order": self.order, "difficulty": diff,
                    "teaching_card": tcard, "question_ids": [],
                    "prerequisite_lesson_ids": [prev] if prev else [],
                    "unlock_xp": 0, "tags": [domain, spec.skill, diff],
                    "version": VERSION,
                }
                qs = []
                for i in range(n):
                    qid = f"{lid}-q{i + 1:02d}"
                    body = self.body_for(spec, diff, domain, i)
                    qs.append(self.finalize(body, spec.skill, lid, qid, diff))
                    lesson["question_ids"].append(qid)
                est = sum(q["estimated_time_seconds"] for q in qs)
                lesson["estimated_minutes"] = max(3, min(30, round(est / 60)))
                self.lessons.append(lesson)
                self.questions_by_lesson[lid] = qs
                prev = lid
                self.order += 1

    # ---- practice bank ---------------------------------------------------
    def build_bank(self):
        for spec in self.plan.skills:
            if spec.kind != "family" or spec.skill in self.plan.no_bank_skills:
                continue
            domain, _ = self.skill_index[spec.skill]
            target = spec.bank_per_tier or self.plan.bank_per_kind.get(domain, 0)
            if target <= 0:
                continue
            for diff, _n in spec.tiers:
                lid = self.lesson_id(spec, diff)
                fns = self.family_fns(spec, diff, domain)
                qs = []
                idx = 1
                fails = 0
                while len(qs) < target and fails < 40:
                    start = self.rng.randrange(len(fns))
                    body = self._draw(fns, diff, domain, start, tries=12)
                    if body is None:
                        fails += 1
                        continue
                    fails = 0
                    qs.append(self.finalize(body, spec.skill, lid, f"{lid}-b{idx:04d}", diff))
                    idx += 1
                if qs:
                    self.bank_files[f"{lid}-bank"] = (domain, qs)

    # ---- output ----------------------------------------------------------
    def write(self):
        exam_dir = CONTENT / self.plan.exam_id
        slugs = set(self.plan.domain_slug.values())
        for sub in [f"lessons/{s}" for s in slugs] + [f"questions/{s}" for s in slugs] + \
                   [f"questions/bank/{s}" for s in slugs]:
            d = exam_dir / sub
            d.mkdir(parents=True, exist_ok=True)
            for f in d.glob("*.json"):
                f.unlink()
        manifest = {"exam_id": self.plan.exam_id, "version": VERSION,
                    "lessons": [], "questions": [], "bank": []}
        for lesson in self.lessons:
            slug = self.plan.domain_slug[lesson["domain"]]
            lpath = exam_dir / "lessons" / slug / f"{lesson['lesson_id']}.json"
            lpath.write_text(json.dumps(lesson, indent=2, ensure_ascii=False) + "\n")
            manifest["lessons"].append(str(lpath.relative_to(exam_dir)))
            qpath = exam_dir / "questions" / slug / f"{lesson['lesson_id']}.json"
            qpath.write_text(json.dumps(self.questions_by_lesson[lesson["lesson_id"]],
                                        indent=2, ensure_ascii=False) + "\n")
            manifest["questions"].append(str(qpath.relative_to(exam_dir)))
        for stem, (domain, qs) in sorted(self.bank_files.items()):
            slug = self.plan.domain_slug[domain]
            bpath = exam_dir / "questions" / "bank" / slug / f"{stem}.json"
            bpath.write_text(json.dumps(qs, indent=2, ensure_ascii=False) + "\n")
            manifest["bank"].append(str(bpath.relative_to(exam_dir)))
        (exam_dir / "manifest.json").write_text(json.dumps(manifest, indent=2) + "\n")

    def summary(self) -> str:
        lesson_q = sum(len(v) for v in self.questions_by_lesson.values())
        bank_q = sum(len(v) for _, v in self.bank_files.values())
        by_domain = {}
        for qs in list(self.questions_by_lesson.values()) + [v for _, v in self.bank_files.values()]:
            for q in qs:
                by_domain[q["domain"]] = by_domain.get(q["domain"], 0) + 1
        doms = ", ".join(f"{d} {n}" for d, n in sorted(by_domain.items()))
        return (f"[{self.plan.exam_id}] lessons: {len(self.lessons)}  lesson questions: "
                f"{lesson_q}  bank: {bank_q}  total: {lesson_q + bank_q}  ({doms})")


def generate(exam_id: str, families=None, teaching=None) -> Builder:
    plan = PLANS[exam_id]
    b = Builder(plan, families or load_families(), teaching or load_teaching())
    b.build_lessons()
    b.build_bank()
    util.set_option_count(4)
    return b


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--exam", default="all", choices=["all", *PLANS])
    args = ap.parse_args()
    exams = list(PLANS) if args.exam == "all" else [args.exam]
    families, teaching = load_families(), load_teaching()
    for exam_id in exams:
        b = generate(exam_id, families, teaching)
        b.write()
        print(b.summary())
        print(f"Written under content/exams/{exam_id}/")


if __name__ == "__main__":
    main()
