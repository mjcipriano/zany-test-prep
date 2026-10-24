"""Item-family registry shared by every content generator.

A *family* is one recognisable question form for a skill ("solve ax+b=c",
"interpret the slope in context", "which equation models the situation", ...).
Real SAT/ACT sections mix many forms of the same skill, so every skill exposes
several families per difficulty and the lesson builder round-robins across
them. This is what keeps lessons from feeling like the same template with new
numbers.

Contract for generator modules
------------------------------
Each module exposes ``FAMILIES``::

    FAMILIES = {
        "linear_equations": {
            "easy":   [fn_a, fn_b, ...],
            "medium": [...],
            "hard":   [...],
        },
        ...
    }

where every ``fn(rng: random.Random, difficulty: str) -> body`` returns a
question *body* dict (see ``util.mc`` / ``util.spr``). Families are plain
functions so they stay easy to unit test in isolation.

Every emitted body is stamped with a ``family:<name>`` tag (``<name>`` is the
function name) by :func:`run_family`; the validator uses these tags to enforce
per-lesson variety.
"""
from __future__ import annotations

import random
from typing import Callable, Dict, List

Body = dict
FamilyFn = Callable[[random.Random, str], Body]
FamilyTable = Dict[str, Dict[str, List[FamilyFn]]]

DIFFICULTIES = ("easy", "medium", "hard")
FAMILY_TAG_PREFIX = "family:"


def merge(*tables: FamilyTable) -> FamilyTable:
    """Combine several modules' FAMILIES into one skill -> difficulty -> fns map."""
    out: FamilyTable = {}
    for table in tables:
        for skill, by_diff in table.items():
            dst = out.setdefault(skill, {d: [] for d in DIFFICULTIES})
            for diff, fns in by_diff.items():
                if diff not in DIFFICULTIES:
                    raise ValueError(f"{skill}: unknown difficulty {diff!r}")
                dst[diff].extend(fns)
    return out


def families_for(table: FamilyTable, skill: str, difficulty: str) -> List[FamilyFn]:
    fns = table.get(skill, {}).get(difficulty) or []
    if not fns:
        raise KeyError(f"no families registered for {skill}/{difficulty}")
    return fns


def family_name(fn: FamilyFn) -> str:
    return getattr(fn, "__name__", "anonymous").lstrip("_")


def run_family(fn: FamilyFn, rng: random.Random, difficulty: str) -> Body:
    """Call a family and stamp the body with its ``family:<name>`` tag."""
    body = fn(rng, difficulty)
    tags = list(body.get("tags") or [])
    tag = FAMILY_TAG_PREFIX + family_name(fn)
    if tag not in tags:
        tags.append(tag)
    body["tags"] = tags
    return body


def family_of(body: Body) -> str | None:
    """The family name stamped on a body/question, if any."""
    for t in body.get("tags") or []:
        if isinstance(t, str) and t.startswith(FAMILY_TAG_PREFIX):
            return t[len(FAMILY_TAG_PREFIX):]
    return None


def round_robin(fns: List[FamilyFn], index: int) -> FamilyFn:
    """Family to use for the ``index``-th item of a lesson (cycles in order)."""
    return fns[index % len(fns)]


def validate_table(table: FamilyTable, min_per_tier: int = 1) -> List[str]:
    """Return human-readable problems with a family table (empty = ok)."""
    problems = []
    for skill, by_diff in table.items():
        for diff in DIFFICULTIES:
            fns = by_diff.get(diff) or []
            if len(fns) < min_per_tier:
                problems.append(f"{skill}/{diff}: {len(fns)} families (< {min_per_tier})")
            for fn in fns:
                if not callable(fn):
                    problems.append(f"{skill}/{diff}: {fn!r} is not callable")
    return problems
