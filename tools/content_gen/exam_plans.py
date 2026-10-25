"""Per-exam generation plans (SAT, ACT).

A plan says, for one exam, which skills get lessons, how many items each
difficulty tier holds, where the items come from (family registry, authored
pools, reading passages), how many answer choices each domain uses, how big the
practice bank is, and which exam-specific transforms to apply (e.g. the ACT
English "NO CHANGE" format). ``tools/generate_content.py`` just walks a plan.
"""
from __future__ import annotations

import random
from dataclasses import dataclass, field
from typing import Callable, Dict, List, Optional, Sequence, Tuple

from . import registry
from .util import LETTERS

Tier = Tuple[str, int]

# ---- lesson tier shapes ------------------------------------------------------
STD3: Tuple[Tier, ...] = (("easy", 20), ("medium", 20), ("hard", 20))
SMALL3: Tuple[Tier, ...] = (("easy", 8), ("medium", 8), ("hard", 8))
CONV3: Tuple[Tier, ...] = (("easy", 24), ("medium", 24), ("hard", 24))
READ3: Tuple[Tier, ...] = (("easy", 14), ("medium", 14), ("hard", 14))  # 69 authored passages
MID3: Tuple[Tier, ...] = (("easy", 16), ("medium", 16), ("hard", 16))
SYN3: Tuple[Tier, ...] = (("easy", 11), ("medium", 11), ("hard", 11))
SCI3: Tuple[Tier, ...] = (("easy", 12), ("medium", 12), ("hard", 12))


@dataclass(frozen=True)
class SkillSpec:
    """One skill track in a plan.

    kind:
      "family"     -> items come from the family registry (source = skill id
                      to look up; defaults to ``skill``)
      "rw_pool"    -> authored pool key ("concision", "synthesis") drawn in order
      "reading"    -> passages.build_reading(<source>) items
      "cross_text" -> passages.build_cross_text() items
    """
    skill: str
    kind: str = "family"
    source: Optional[str] = None
    tiers: Tuple[Tier, ...] = STD3
    bank_per_tier: Optional[int] = None  # None -> plan default for the kind

    @property
    def family_key(self) -> str:
        return self.source or self.skill


@dataclass
class ExamPlan:
    exam_id: str
    exam_name: str
    seed: int
    skills: List[SkillSpec]
    domain_slug: Dict[str, str]
    skill_titles: Dict[str, str]
    # answer choices per domain (ACT Math uses 5)
    option_count: Dict[str, int] = field(default_factory=dict)
    default_option_count: int = 4
    bank_per_kind: Dict[str, int] = field(default_factory=dict)
    no_bank_skills: frozenset = frozenset()
    # transforms applied to every finished body: fn(body, domain, rng) -> body
    transforms: List[Callable[[dict, str, random.Random], dict]] = field(default_factory=list)
    # family exclusion: fn(family_fn, domain) -> bool (True = skip this family)
    exclude_family: Callable[[Callable, str], bool] = lambda fn, domain: False
    # body acceptance after generation: fn(body, domain) -> bool
    accept_body: Callable[[dict, str], bool] = lambda body, domain: True
    # minimum items per lesson (schema requires 8)
    min_lesson_items: int = 8
    # emit the long passage sets (passages_long) into the practice bank, one
    # file per set, each item filed under the reading skill it trains
    long_passage_sets: bool = False

    def option_count_for(self, domain: str) -> int:
        return self.option_count.get(domain, self.default_option_count)


# --------------------------------------------------------------------------- #
# Shared titles
# --------------------------------------------------------------------------- #
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
    # ACT-only
    "number_properties": "Number Properties", "coordinate_geometry": "Coordinate Geometry",
    "angles_polygons": "Angles & Polygons", "sequences": "Sequences",
    "logarithms": "Logarithms", "complex_numbers": "Complex Numbers",
    "usage_idioms": "Usage & Idioms",
    "data_representation": "Reading Tables & Graphs",
    "trends_extrapolation": "Trends & Extrapolation",
    "experimental_design": "Experimental Design",
    "conflicting_viewpoints": "Conflicting Viewpoints",
}

ACT_TITLE_OVERRIDES = {
    "rhetorical_synthesis": "Writer's Goal",
    "cross_text_connections": "Comparing Passages",
    "command_of_evidence": "Supporting Details",
    "concision": "Concision & Precision",
}

# --------------------------------------------------------------------------- #
# SAT
# --------------------------------------------------------------------------- #
SAT_MATH = [
    SkillSpec("linear_equations"), SkillSpec("linear_inequalities"),
    SkillSpec("systems_of_equations"), SkillSpec("functions"),
    SkillSpec("quadratics"), SkillSpec("exponents_radicals"),
    SkillSpec("polynomials"), SkillSpec("ratios_percentages_units"),
    SkillSpec("proportions"), SkillSpec("data_analysis"),
    SkillSpec("statistics"), SkillSpec("probability"),
    SkillSpec("area_volume"),
    SkillSpec("circles", tiers=SMALL3), SkillSpec("right_triangles", tiers=SMALL3),
    SkillSpec("trigonometry", tiers=SMALL3),
    SkillSpec("word_problems"), SkillSpec("absolute_value"),
    SkillSpec("exponential"), SkillSpec("two_way_tables"),
    SkillSpec("scatterplots"),
]

SAT_RW = [
    SkillSpec("main_idea", "reading", "main_idea", READ3),
    SkillSpec("inferences", "reading", "inference", READ3),
    SkillSpec("command_of_evidence", "reading", "evidence", READ3),
    SkillSpec("text_structure_purpose", "reading", "structure", READ3),
    SkillSpec("words_in_context", "reading", "wic", READ3),
    SkillSpec("cross_text_connections", "cross_text", None, READ3),
    SkillSpec("quantitative_evidence", tiers=CONV3),
    SkillSpec("sentence_boundaries", tiers=CONV3),
    SkillSpec("subject_verb_agreement", tiers=CONV3),
    SkillSpec("punctuation", tiers=CONV3),
    SkillSpec("pronouns", tiers=CONV3),
    SkillSpec("modifiers", tiers=MID3),
    SkillSpec("verb_tense", tiers=CONV3),
    SkillSpec("parallel_structure", tiers=CONV3),
    SkillSpec("pronoun_antecedent", tiers=CONV3),
    SkillSpec("transitions", tiers=MID3),
    SkillSpec("concision", "rw_pool", "concision", MID3),
    SkillSpec("rhetorical_synthesis", "rw_pool", "synthesis", SYN3),
]

SAT_PLAN = ExamPlan(
    exam_id="sat", exam_name="SAT", seed=20240614,
    skills=SAT_MATH + SAT_RW,
    domain_slug={"reading_writing": "rw", "math": "math"},
    skill_titles=SKILL_TITLES,
    bank_per_kind={"math": 260, "reading_writing": 500},
    no_bank_skills=frozenset({"circles", "right_triangles", "trigonometry"}),
)

# --------------------------------------------------------------------------- #
# ACT
# --------------------------------------------------------------------------- #
ACT_ENGLISH = [
    SkillSpec("sentence_boundaries", tiers=CONV3),
    SkillSpec("subject_verb_agreement", tiers=CONV3),
    SkillSpec("punctuation", tiers=CONV3),
    SkillSpec("pronouns", tiers=CONV3),
    SkillSpec("modifiers", tiers=MID3),
    SkillSpec("verb_tense", tiers=CONV3),
    SkillSpec("parallel_structure", tiers=CONV3),
    SkillSpec("pronoun_antecedent", tiers=CONV3),
    SkillSpec("transitions", tiers=MID3),
    SkillSpec("rhetorical_synthesis", "rw_pool", "synthesis", SYN3),
    SkillSpec("concision", "rw_pool", "concision", MID3),
    SkillSpec("usage_idioms", tiers=CONV3),
]

ACT_MATH = [
    SkillSpec("number_properties"), SkillSpec("exponents_radicals"),
    SkillSpec("complex_numbers"),
    SkillSpec("linear_equations"), SkillSpec("linear_inequalities"),
    SkillSpec("systems_of_equations"), SkillSpec("word_problems"),
    SkillSpec("absolute_value"), SkillSpec("polynomials"),
    SkillSpec("functions"), SkillSpec("quadratics"), SkillSpec("exponential"),
    SkillSpec("sequences"), SkillSpec("logarithms"),
    SkillSpec("area_volume"), SkillSpec("circles", tiers=SMALL3),
    SkillSpec("right_triangles", tiers=SMALL3), SkillSpec("trigonometry", tiers=SMALL3),
    SkillSpec("angles_polygons"), SkillSpec("coordinate_geometry"),
    SkillSpec("statistics"), SkillSpec("probability"), SkillSpec("data_analysis"),
    SkillSpec("two_way_tables"), SkillSpec("scatterplots"),
    SkillSpec("ratios_percentages_units"), SkillSpec("proportions"),
]

READ10: Tuple[Tier, ...] = (("easy", 20), ("medium", 20), ("hard", 20))  # ACT: 69 passages, 73 cross-text items

ACT_READING = [
    SkillSpec("main_idea", "reading", "main_idea", READ10),
    SkillSpec("inferences", "reading", "inference", READ10),
    SkillSpec("command_of_evidence", "reading", "evidence", READ10),
    SkillSpec("words_in_context", "reading", "wic", READ10),
    SkillSpec("text_structure_purpose", "reading", "structure", READ10),
    SkillSpec("cross_text_connections", "cross_text", None, READ10),
]

ACT_SCIENCE = [
    SkillSpec("data_representation", tiers=SCI3),
    SkillSpec("trends_extrapolation", tiers=SCI3),
    SkillSpec("experimental_design", tiers=SCI3),
    SkillSpec("conflicting_viewpoints", tiers=READ3),
]


def _is_fill_in(body: dict) -> bool:
    prompt = body.get("prompt", "")
    return prompt.count("___") == 1 and "\n\n" in prompt and bool(body.get("choices"))


def act_no_change(body: dict, domain: str, rng: random.Random) -> dict:
    """Rewrite an English fill-in item into the ACT's underlined-portion format.

    The blank is replaced by a bracketed candidate wording; choice A is always
    "NO CHANGE". A quarter of the time the shown wording is already correct
    (so NO CHANGE is the answer); otherwise a distractor is shown and the real
    answer sits among B–D. Items that are not blank-fillers are returned as is.
    """
    if domain != "english" or not _is_fill_in(body):
        return body
    text, _stem = body["prompt"].rsplit("\n\n", 1)
    choices = body["choices"]
    correct = next(c for c in choices if c["id"] == body["correct_choice"])
    distractors = [c for c in choices if c["id"] != body["correct_choice"]]
    if not distractors:
        return body
    show_correct = rng.random() < 0.25
    if show_correct:
        shown = correct
        rest = distractors[:3]
        first = {"text": "NO CHANGE",
                 "rationale": "Correct. The bracketed wording is already right: "
                              + correct["rationale"].removeprefix("Correct. ").removeprefix("Correct: ")}
        correct_text = "NO CHANGE"
    else:
        shown = rng.choice(distractors)
        rest = [correct] + [d for d in distractors if d is not shown][:2]
        rng.shuffle(rest)
        first = {"text": "NO CHANGE", "rationale": shown["rationale"]}
        correct_text = correct["text"]
    new_text = text.replace("___", f"[{shown['text']}]", 1)
    stem = rng.choice([
        "Which choice is the best version of the bracketed portion?",
        "What is the best way to write the bracketed portion?",
        "Which of the following is the best replacement for the bracketed portion?",
        "Choose the best version of the bracketed portion.",
    ])
    out = dict(body)
    out["prompt"] = f"{new_text}\n\n{stem} (Choose NO CHANGE if it is best as written.)"
    new_choices = [first] + [{"text": c["text"], "rationale": c["rationale"]} for c in rest]
    out["choices"] = [{"id": LETTERS[i], "text": c["text"], "rationale": c["rationale"]}
                      for i, c in enumerate(new_choices)]
    out["correct_choice"] = next(c["id"] for c in out["choices"] if c["text"] == correct_text)
    tags = [t for t in out.get("tags", []) if t != "act-no-change"]
    out["tags"] = tags + ["act-no-change"]
    return out


def _act_exclude(fn: Callable, domain: str) -> bool:
    # Grid-in (student-produced) families are SAT-only; the ACT is all MC.
    return bool(getattr(fn, "sat_only", False))


def _act_accept(body: dict, domain: str) -> bool:
    return body.get("question_type") != "student_produced"


ACT_PLAN = ExamPlan(
    exam_id="act", exam_name="ACT", seed=20250301,
    skills=ACT_ENGLISH + ACT_MATH + ACT_READING + ACT_SCIENCE,
    domain_slug={"english": "english", "math": "math", "reading": "reading",
                 "science": "science"},
    skill_titles={**SKILL_TITLES, **ACT_TITLE_OVERRIDES},
    option_count={"math": 5},
    bank_per_kind={"english": 200, "math": 160, "science": 150},
    no_bank_skills=frozenset({"circles", "right_triangles", "trigonometry",
                              "conflicting_viewpoints"}),
    transforms=[act_no_change],
    exclude_family=_act_exclude,
    accept_body=_act_accept,
    long_passage_sets=True,
)

PLANS = {"sat": SAT_PLAN, "act": ACT_PLAN}
