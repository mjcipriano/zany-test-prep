#!/usr/bin/env python3
"""Validate the offline content bank. Runs locally and in CI.

Usage:
    python tools/validate_content.py            # validate content/exams/sat
    python tools/validate_content.py --exam sat

Exit code 0 means all checks passed; non-zero means at least one failure.
"""
from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path

import yaml
from jsonschema import Draft7Validator

ROOT = Path(__file__).resolve().parent.parent
CONTENT = ROOT / "content"
SCHEMAS = CONTENT / "schemas"

PLACEHOLDER_PATTERNS = [
    r"lorem ipsum", r"\bTODO\b", r"\bTBD\b", r"\bFIXME\b", r"placeholder",
    r"\bxxx+\b", r"\byour answer here\b", r"\bsample text\b",
]
ID_RE = re.compile(r"^[a-z0-9]+(?:-[a-z0-9]+)*$")


class Report:
    def __init__(self):
        self.errors = []
        self.warnings = []
        self.stats = {}

    def err(self, msg):
        self.errors.append(msg)

    def warn(self, msg):
        self.warnings.append(msg)


def load_json(path):
    with open(path, encoding="utf-8") as f:
        return json.load(f)


def normalize_prompt(text):
    # keep letters, digits, and signs (+ - /) so equations differing only by a
    # sign are not treated as duplicates; normalise the unicode minus first.
    s = text.lower().replace("−", "-").replace("–", "-")
    s = re.sub(r"[^a-z0-9+\-/]+", " ", s)
    s = re.sub(r"\s+", " ", s).strip()
    return s


def check_placeholders(rep, where, *texts):
    for t in texts:
        if not t:
            continue
        low = t.lower()
        for pat in PLACEHOLDER_PATTERNS:
            if re.search(pat, low):
                rep.err(f"{where}: placeholder-like text matched /{pat}/")


def validate_exam(exam_id, rep: Report):
    sat = CONTENT / "exams" / exam_id
    if not sat.exists():
        rep.err(f"exam directory missing: {sat}")
        return

    # --- exam.yaml + skills.yaml ---
    exam = yaml.safe_load((sat / "exam.yaml").read_text())
    if not exam.get("exam_id"):
        rep.err("exam.yaml missing exam_id")
    if not exam.get("content_version"):
        rep.err("exam.yaml missing content_version")

    skills_doc = yaml.safe_load((sat / "skills.yaml").read_text())
    skill_ids = set()
    section_ids = set()
    domain_ids = set()
    for dom in skills_doc["domains"]:
        domain_ids.add(dom["id"])
        for sec in dom["sections"]:
            section_ids.add(sec["id"])
            for sk in sec["skills"]:
                skill_ids.add(sk["id"])
    rep.stats["skills"] = len(skill_ids)

    # --- schemas ---
    q_schema = load_json(SCHEMAS / "question.schema.json")
    l_schema = load_json(SCHEMAS / "lesson.schema.json")
    q_validator = Draft7Validator(q_schema)
    l_validator = Draft7Validator(l_schema)

    # --- manifest ---
    manifest = load_json(sat / "manifest.json")

    lessons = {}
    questions = {}
    prompt_index = {}     # normalized prompt -> first id (with same choices signature)
    dup_prompts = 0

    # Load + schema-validate lessons.
    for rel in manifest["lessons"]:
        path = sat / rel
        lesson = load_json(path)
        for e in l_validator.iter_errors(lesson):
            rep.err(f"lesson {path.name}: schema: {e.message}")
        lid = lesson["lesson_id"]
        if lid in lessons:
            rep.err(f"duplicate lesson_id: {lid}")
        lessons[lid] = lesson
        if not ID_RE.match(lid):
            rep.err(f"lesson_id not a valid slug: {lid}")
        if lesson["domain"] not in domain_ids:
            rep.err(f"lesson {lid}: unknown domain {lesson['domain']}")
        if lesson["skill"] not in skill_ids:
            rep.err(f"lesson {lid}: references unknown skill {lesson['skill']}")
        tc = lesson["teaching_card"]
        check_placeholders(rep, f"lesson {lid} teaching_card",
                           tc["title"], tc["body"], *tc["key_points"])

    # Load + schema-validate questions.
    bank_ids = set()
    for rel in manifest["questions"] + manifest.get("bank", []):
        path = sat / rel
        items = load_json(path)
        if not isinstance(items, list):
            rep.err(f"question file not a list: {path.name}")
            continue
        is_bank = rel in manifest.get("bank", [])
        for q in items:
            for e in q_validator.iter_errors(q):
                rep.err(f"question {q.get('question_id','?')}: schema: {e.message}")
            qid = q["question_id"]
            if qid in questions:
                rep.err(f"duplicate question_id: {qid}")
            questions[qid] = q
            if is_bank:
                bank_ids.add(qid)

    rep.stats["lessons"] = len(lessons)
    rep.stats["questions"] = len(questions)
    rep.stats["bank_questions"] = len(bank_ids)

    # --- per-question semantic checks ---
    by_domain = {"math": 0, "reading_writing": 0}
    # Track correct-answer position and "correct is longest option" to catch the
    # tells where the right answer always sits in slot A or is the longest choice.
    pos_counts = {}   # domain -> {A,B,C,D: n}
    mc_counts = {}    # domain -> total MC items
    longest_counts = {}  # domain -> n where correct is the longest option
    # Per-(skill, difficulty) first-word tracking, to catch "all correct answers
    # start with the same word, distractors with another" tells.
    group_words = {}  # (skill, diff) -> {"correct": [w...], "distractor": [w...]}
    for qid, q in questions.items():
        where = f"question {qid}"
        if not ID_RE.match(qid):
            rep.err(f"{where}: id not a valid slug")
        if q["skill"] not in skill_ids:
            rep.err(f"{where}: unknown skill {q['skill']}")
        if q["lesson_id"] not in lessons:
            rep.err(f"{where}: references missing lesson {q['lesson_id']}")
        if q["exam_id"] != exam_id:
            rep.err(f"{where}: wrong exam_id {q['exam_id']}")
        if not q.get("version"):
            rep.err(f"{where}: missing version")
        by_domain[q["domain"]] = by_domain.get(q["domain"], 0) + 1

        # position + length-tell tracking (multiple-choice style only)
        if q["question_type"] != "student_produced" and q.get("choices"):
            dom = q["domain"]
            cc = q.get("correct_choice")
            pos_counts.setdefault(dom, {})
            pos_counts[dom][cc] = pos_counts[dom].get(cc, 0) + 1
            mc_counts[dom] = mc_counts.get(dom, 0) + 1
            cur = next((c for c in q["choices"] if c["id"] == cc), None)
            if cur:
                longest = max(len(c["text"]) for c in q["choices"])
                if len(cur["text"]) == longest:
                    longest_counts[dom] = longest_counts.get(dom, 0) + 1
            gk = (q["skill"], q["difficulty"])
            g = group_words.setdefault(gk, {"correct": [], "distractor": []})
            for c in q["choices"]:
                bucket = "correct" if c["id"] == cc else "distractor"
                g[bucket].append(_first_word(c["text"]))

        # placeholder scan
        choice_texts = [c["text"] for c in q.get("choices", [])]
        check_placeholders(rep, where, q.get("prompt"), q.get("explanation"),
                           *choice_texts)

        qtype = q["question_type"]
        if qtype == "student_produced":
            ans = q.get("answer")
            if not ans:
                rep.err(f"{where}: student_produced needs an answer object")
            else:
                if ans["type"] == "numeric":
                    for a in ans["accepted"]:
                        if not _parse_numeric(a):
                            rep.err(f"{where}: accepted answer '{a}' is not numeric")
                    if "value" in ans and not isinstance(ans["value"], (int, float)):
                        rep.err(f"{where}: numeric value must be a number")
                if ans.get("tolerance", 0) < 0:
                    rep.err(f"{where}: negative tolerance")
        else:
            choices = q.get("choices", [])
            cids = [c["id"] for c in choices]
            if len(cids) != len(set(cids)):
                rep.err(f"{where}: duplicate choice ids")
            ctexts = [c["text"].strip() for c in choices]
            if len(ctexts) != len(set(ctexts)):
                rep.err(f"{where}: duplicate choice texts")
            if q.get("correct_choice") not in cids:
                rep.err(f"{where}: correct_choice not among choices")
            for c in choices:
                if not c.get("rationale", "").strip():
                    rep.err(f"{where}: choice {c['id']} missing rationale")
        if not q.get("explanation", "").strip():
            rep.err(f"{where}: missing explanation")
        if not (10 <= q["estimated_time_seconds"] <= 600):
            rep.err(f"{where}: estimated_time_seconds out of range")

        # near-duplicate detection (prompt + sorted choices + stimulus head)
        sig_parts = [normalize_prompt(q.get("prompt", ""))]
        sig_parts += sorted(normalize_prompt(t) for t in choice_texts)
        stim = q.get("stimulus") or {}
        if stim.get("text"):
            sig_parts.append(normalize_prompt(stim["text"])[:80])
        sig = "|".join(sig_parts)
        if sig in prompt_index:
            dup_prompts += 1
            rep.err(f"{where}: near-duplicate of {prompt_index[sig]}")
        else:
            prompt_index[sig] = qid

    # --- per-lesson checks ---
    for lid, lesson in lessons.items():
        where = f"lesson {lid}"
        qids = lesson["question_ids"]
        if not (8 <= len(qids) <= 25):
            rep.err(f"{where}: has {len(qids)} questions (must be 8-25)")
        if len(qids) != len(set(qids)):
            rep.err(f"{where}: duplicate question ids in list")
        for qid in qids:
            if qid not in questions:
                rep.err(f"{where}: references missing question {qid}")
            elif questions[qid]["lesson_id"] != lid:
                rep.err(f"{where}: question {qid} points to a different lesson")
        for pre in lesson["prerequisite_lesson_ids"]:
            if pre not in lessons:
                rep.err(f"{where}: missing prerequisite lesson {pre}")
        if lesson["difficulty"] not in ("easy", "medium", "hard"):
            rep.err(f"{where}: bad difficulty")
        if not (3 <= lesson["estimated_minutes"] <= 30):
            rep.err(f"{where}: estimated_minutes out of range")

    # --- aggregate requirements ---
    rep.stats["math_questions"] = by_domain.get("math", 0)
    rep.stats["rw_questions"] = by_domain.get("reading_writing", 0)
    rep.stats["duplicate_prompts"] = dup_prompts
    if len(lessons) < 50:
        rep.err(f"need >= 50 lessons, found {len(lessons)}")
    if len(questions) < 1000:
        rep.err(f"need >= 1000 questions, found {len(questions)}")
    if by_domain.get("reading_writing", 0) < 500:
        rep.err(f"need >= 500 reading/writing questions, found {by_domain.get('reading_writing',0)}")
    if by_domain.get("math", 0) < 500:
        rep.err(f"need >= 500 math questions, found {by_domain.get('math',0)}")

    # --- answer-position and length-tell balance ---
    # A well-shuffled bank spreads the correct answer roughly evenly across
    # positions and does not let it stand out as the longest option.
    for dom, total in mc_counts.items():
        if total < 40:
            continue
        share = {k: v / total for k, v in pos_counts.get(dom, {}).items()}
        top = max(share.values()) if share else 0
        rep.stats[f"{dom}_correct_positions"] = {
            k: round(v, 2) for k, v in sorted(share.items())}
        if top > 0.40:
            rep.err(f"{dom}: correct answer is in one position {top*100:.0f}% of the "
                    "time (>40%); shuffle option order")
        elif top > 0.32:
            rep.warn(f"{dom}: correct-answer positions are uneven (top {top*100:.0f}%)")
        longest_rate = longest_counts.get(dom, 0) / total
        rep.stats[f"{dom}_correct_is_longest"] = round(longest_rate, 2)
        # Numeric math answers are often the largest value, so only flag text-heavy
        # reading/writing where a long correct option is a real tell.
        if dom == "reading_writing" and longest_rate > 0.45:
            rep.warn(f"{dom}: correct answer is the longest option {longest_rate*100:.0f}% "
                     "of the time; balance distractor lengths")

    # --- per-section answer-wording pattern (first word) ---
    # Flag groups where the correct answer disproportionately starts with one
    # word that the distractors rarely use — a guessable tell.
    from collections import Counter
    wording_flags = 0
    for (skill, diff), g in sorted(group_words.items()):
        n = len(g["correct"])
        if n < 6:
            continue
        word, cnt = Counter(g["correct"]).most_common(1)[0]
        if not word:
            continue
        c_share = cnt / n
        d = g["distractor"]
        d_share = (d.count(word) / len(d)) if d else 0
        if c_share >= 0.6 and d_share < 0.25:
            wording_flags += 1
            rep.warn(
                f"{skill}/{diff}: {c_share*100:.0f}% of correct answers start with "
                f"'{word}' but only {d_share*100:.0f}% of distractors do — "
                "vary answer wording")
    rep.stats["answer_wording_flags"] = wording_flags


def _first_word(text: str) -> str:
    """Lowercased first alphanumeric token of a choice (for pattern detection)."""
    m = re.search(r"[A-Za-z0-9]+", text or "")
    return m.group(0).lower() if m else ""


def _parse_numeric(s):
    s = s.strip()
    if re.fullmatch(r"-?\d+(\.\d+)?", s):
        return True
    if re.fullmatch(r"-?\d+/\d+", s):  # fraction
        return True
    return False


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--exam", default="sat")
    args = ap.parse_args()
    rep = Report()
    validate_exam(args.exam, rep)

    print("Content validation report")
    print("=" * 40)
    for k, v in rep.stats.items():
        print(f"  {k}: {v}")
    print("-" * 40)
    for w in rep.warnings:
        print(f"  WARN: {w}")
    if rep.errors:
        for e in rep.errors[:100]:
            print(f"  ERROR: {e}")
        more = len(rep.errors) - 100
        if more > 0:
            print(f"  ... and {more} more errors")
        print(f"\nFAILED with {len(rep.errors)} error(s).")
        sys.exit(1)
    print("\nAll content checks passed.")
    sys.exit(0)


if __name__ == "__main__":
    main()
