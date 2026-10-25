"""Long, ACT-length reading passages served as whole passage sets.

The shared pool in passages.py uses short passages with one question per skill
per passage. Real ACT Reading is four long passages (one of them a paired set)
with about nine questions each, so this module adds original ~650-800 word
passages in the four ACT genres plus paired-passage sets, each carrying a full
nine-question set (passages_long_sets.py, passages_long_paired.py).

Every question in a set keeps the set's passage as its stimulus and is tagged
``passage-set:<id>`` so the app can keep a set together (the timed test's
Reading module deals whole sets; see dealTestModules in
lib/features/test/timed_test_screen.dart). Each question is filed under the
reading skill it trains (main idea, details, inferences, words in context,
purpose/structure, comparing passages), so mastery credit lands on the existing
skills and no new skill or lesson track is needed. The generator writes one
practice-bank file per set (ExamPlan.long_passage_sets).
"""
from __future__ import annotations

import random

from .passages import _shuffle
from .passages_long_paired import LONG_PAIRED
from .passages_long_sets import LONG_PASSAGES
from .util import mc

GENRE_LABELS = {
    "literary": "Literary Narrative",
    "social": "Social Science",
    "humanities": "Humanities",
    "natural": "Natural Science",
}

# kind -> (skill, subskill, tag). Skills/subskills exist in the ACT skills.yaml.
KINDS = {
    "main_idea": ("main_idea", "central_idea", "main-idea"),
    "detail": ("command_of_evidence", "textual_evidence", "detail"),
    "inference": ("inferences", "implied_meaning", "inference"),
    "view": ("inferences", "implied_meaning", "authors-view"),
    "vocab": ("words_in_context", "vocabulary", "vocabulary"),
    "function": ("text_structure_purpose", "authors_purpose", "purpose"),
    "structure": ("text_structure_purpose", "overall_structure", "structure"),
    "comparison": ("cross_text_connections", "compare_viewpoints", "cross-text"),
}

SET_TAG_PREFIX = "passage-set:"
QUESTIONS_PER_SET = 9
EST_SECONDS = 75  # ~40 min for 36 items, reading time included


def is_paired(pset: dict) -> bool:
    return "paragraphs_a" in pset


def join_paragraphs(paragraphs) -> str:
    """Paragraphs are separated by a blank line; the app numbers them."""
    return "\n\n".join(paragraphs)


def all_sets() -> list:
    return [*LONG_PASSAGES, *LONG_PAIRED]


def word_count(pset: dict) -> int:
    paras = (pset["paragraphs_a"] + pset["paragraphs_b"]) if is_paired(pset) \
        else pset["paragraphs"]
    return sum(len(p.split()) for p in paras)


def stimulus_for(pset: dict) -> dict:
    title = f"{GENRE_LABELS[pset['genre']]}: {pset['title']}"
    if is_paired(pset):
        return {"type": "paired_passages", "title": title,
                "text": join_paragraphs(pset["paragraphs_a"]),
                "text_b": join_paragraphs(pset["paragraphs_b"])}
    return {"type": "passage", "title": title, "text": join_paragraphs(pset["paragraphs"])}


def set_questions(pset: dict, rng: random.Random) -> list:
    """(skill, body) for every question of one set, in authored order, with the
    options shuffled (seeded) so the key is not always in the authored slot."""
    stim = stimulus_for(pset)
    out = []
    for kind, prompt, options, ci, rats, expl in pset["questions"]:
        skill, subskill, tag = KINDS[kind]
        options, ci, rats = _shuffle(rng, options, ci, rats)
        body = mc(prompt, options, ci, rats, subskill=subskill, qtype="passage_reading",
                  explanation=expl, est=EST_SECONDS, stimulus=stim,
                  tags=["reading", "long-passage", tag, f"genre:{pset['genre']}",
                        SET_TAG_PREFIX + pset["id"]])
        out.append((skill, body))
    return out


def build_passage_sets(rng: random.Random) -> list:
    """Every set as {"id", "difficulty", "questions": [(skill, body), ...]}."""
    return [{"id": s["id"], "difficulty": s["difficulty"],
             "questions": set_questions(s, rng)} for s in all_sets()]
