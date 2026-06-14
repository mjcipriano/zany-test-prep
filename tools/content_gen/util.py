"""Shared helpers for the SAT content generators.

Generators return a *question body* dict (no ids/exam metadata); the orchestrator
in tools/generate_content.py attaches question_id, lesson_id, exam fields, etc.

The body dict uses these keys:
    question_type, subskill, prompt, explanation, answer_verification,
    estimated_time_seconds, tags
and EITHER:
    choices (list of {id,text,rationale}) + correct_choice         # MC-style
or:
    answer ({type,value,accepted,tolerance})                       # student_produced
optionally:
    stimulus ({type,...})                                          # passage/table
"""
from __future__ import annotations

import random
from fractions import Fraction

LETTERS = ["A", "B", "C", "D", "E", "F"]


def mc(prompt, options, correct_index, rationales, *, subskill, explanation,
       qtype="multiple_choice", est=60, tags=None, stimulus=None, verify=None):
    """Build a multiple-choice body.

    options: list of choice texts (order as shown).
    correct_index: index into options of the correct choice.
    rationales: list parallel to options explaining why each is right/wrong.
    """
    assert len(options) == len(rationales), "need a rationale per option"
    assert 2 <= len(options) <= 6
    assert 0 <= correct_index < len(options)
    choices = []
    for i, (text, rat) in enumerate(zip(options, rationales)):
        choices.append({"id": LETTERS[i], "text": str(text), "rationale": rat})
    body = {
        "question_type": qtype,
        "subskill": subskill,
        "prompt": prompt,
        "choices": choices,
        "correct_choice": LETTERS[correct_index],
        "explanation": explanation,
        "estimated_time_seconds": est,
        "tags": tags or [],
    }
    if stimulus:
        body["stimulus"] = stimulus
    if verify:
        body["answer_verification"] = verify
    return body


def spr(prompt, value, *, subskill, explanation, accepted=None, tolerance=0.0,
        est=75, tags=None, stimulus=None, verify=None):
    """Build a student-produced-response (grid-in) numeric body."""
    if accepted is None:
        accepted = [num_str(value)]
    body = {
        "question_type": "student_produced",
        "subskill": subskill,
        "prompt": prompt,
        "answer": {
            "type": "numeric",
            "value": value if isinstance(value, (int, float)) else float(value),
            "accepted": [str(a) for a in accepted],
            "tolerance": tolerance,
        },
        "explanation": explanation,
        "estimated_time_seconds": est,
        "tags": tags or [],
    }
    if stimulus:
        body["stimulus"] = stimulus
    if verify:
        body["answer_verification"] = verify
    return body


def num_str(x):
    """Render a number the way a student would grid it (no trailing .0)."""
    if isinstance(x, Fraction):
        if x.denominator == 1:
            return str(x.numerator)
        return f"{x.numerator}/{x.denominator}"
    if isinstance(x, float) and x.is_integer():
        return str(int(x))
    return str(x)


def shuffle_with_correct(rng: random.Random, correct_text, distractor_pairs):
    """Given the correct option text and a list of (distractor_text, rationale),
    plus a correct rationale supplied separately, return (options, correct_index,
    rationales) with options shuffled. distractor_pairs items are (text, rationale).

    The correct option's rationale must be appended by the caller; here we expect
    distractor_pairs to be (text, rationale) and correct passed as (text, rationale)
    via correct_text being a tuple.
    """
    correct = correct_text  # (text, rationale)
    items = [(correct[0], correct[1], True)] + [(t, r, False) for t, r in distractor_pairs]
    rng.shuffle(items)
    options = [it[0] for it in items]
    rationales = [it[1] for it in items]
    correct_index = next(i for i, it in enumerate(items) if it[2])
    return options, correct_index, rationales


def item_signature(body) -> str:
    """A near-duplicate signature for a whole item.

    Uses the prompt plus the choice texts (or the numeric answer), because some
    item families share a fixed prompt and differ only in their choices/sentence.
    Accepts either a generator body dict or a finalized question dict.
    """
    # normalise each choice, then sort, so option order doesn't matter but the
    # actual values (including their signs) do.
    parts = [dedupe_key(body.get("prompt", ""))]
    parts += sorted(dedupe_key(c.get("text", ""))
                    for c in (body.get("choices", []) or []))
    ans = body.get("answer")
    if ans:
        parts.append(dedupe_key(str(ans.get("value", ""))))
    # include any stimulus text so identical prompts over different passages differ
    stim = body.get("stimulus") or {}
    if stim.get("text"):
        parts.append(dedupe_key(stim["text"])[:80])
    return "|".join(parts)


def dedupe_key(prompt: str) -> str:
    """Normalised text for near-duplicate detection (generator + validator).

    Numbers AND signs are kept (items differing only in numbers/signs are NOT
    duplicates); we normalise case, the unicode minus, punctuation, and
    whitespace so trivial formatting differences still collide.
    """
    import re
    s = prompt.lower().replace("−", "-").replace("–", "-")  # unicode minus/en-dash
    s = re.sub(r"[^a-z0-9+\-/]+", " ", s)   # keep letters, digits, + - /
    s = re.sub(r"\s+", " ", s).strip()
    return s
