"""Original SAT/ACT-style Reading & Writing question generators.

Three kinds of content live here:
  * Combinatorial conventions (sentence boundaries, subject-verb agreement,
    punctuation, pronoun case, modifiers) and transitions — every skill is a
    *family table* (see registry.py): several recognisable question forms per
    difficulty, each built from clause/noun pools so items are unique and have
    exactly one defensible answer.
  * Legacy dispatchers (gen_sva, gen_boundaries, ...) that pick a random family
    so the current orchestrator keeps working until it switches to FAMILIES.
  * Authored pools (concision, rhetorical synthesis, transitions pool).

Fill-in convention: a family whose choices fill a blank builds its prompt as
"<text with exactly one ___>\\n\\n<instruction stem>" and is marked
``fn.fill_in = True``; families whose options are whole sentences/clauses are
marked ``fn.fill_in = False`` and never contain ``___``.

Reading-comprehension items live in passages.py.
"""
from __future__ import annotations

import random

from .util import mc, shuffle_with_correct

NAMES = ["Maya", "Liam", "Aria", "Noah", "Priya", "Diego", "Ivy", "Omar",
         "Lena", "Theo", "Zoe", "Caleb", "Nina", "Ravi", "Sora", "Jonas",
         "Elena", "Marcus", "Yuki", "Tariq", "Amara", "Felix", "Hana", "Mateo",
         "Nadia", "Oscar", "Rosa", "Samir", "Tessa", "Victor", "Wren", "Idris",
         "Leila", "Bruno", "Chloe", "Dmitri", "Esme", "Gavin", "Imani", "Kenji"]

# Pronoun sets keyed by a name: (subject, object, possessive, reflexive)
_FEM = {"Maya", "Aria", "Priya", "Ivy", "Lena", "Zoe", "Nina", "Sora", "Elena",
        "Amara", "Hana", "Nadia", "Rosa", "Tessa", "Wren", "Leila", "Chloe",
        "Esme", "Imani", "Yuki"}


def pron(name):
    return ("she", "her", "her", "herself") if name in _FEM else ("he", "him", "his", "himself")


CONV_STEMS = [
    "Which choice completes the text so that it conforms to the conventions of "
    "Standard English?",
    "Which choice completes the sentence so that it conforms to the conventions "
    "of standard English?",
    "Which choice best completes the text in keeping with the conventions of "
    "Standard English?",
]


def conv_stem(rng):
    return rng.choice(CONV_STEMS)


def cap(s: str) -> str:
    return s[0].upper() + s[1:] if s else s


def low(s: str) -> str:
    return s[0].lower() + s[1:] if s else s


def soft_low(s: str) -> str:
    """Lowercase the first letter unless the text opens with a proper name."""
    first = s.split()[0].strip(",.'") if s.strip() else ""
    return s if first in NAMES else low(s)


def fill(text: str, stem: str) -> str:
    """Prompt for a blank-filling item (one ___, stem on its own paragraph)."""
    assert text.count("___") == 1, text
    return f"{text}\n\n{stem}"


def family(fill_in: bool, small_space: bool = False):
    """Decorator stamping the family-contract attributes on a family fn."""
    def deco(fn):
        fn.fill_in = fill_in
        fn.small_space = small_space
        return fn
    return deco


def build(rng, prompt, correct, distractors, *, subskill, explanation, tags,
          est=45, qtype="grammar_editing", stimulus=None):
    """Shuffle (correct, rationale) with [(text, rationale)...] into an MC body.
    Distractors that duplicate the key or each other are dropped (the family
    pools are written so at least three survive)."""
    seen = {correct[0].strip()}
    clean = []
    for t, r in distractors:
        if t.strip() in seen:
            continue
        seen.add(t.strip())
        clean.append((t, r))
    assert len(clean) >= 3, (prompt, correct, distractors)
    options, ci, rats = shuffle_with_correct(rng, correct, clean[:4])
    return mc(prompt, options, ci, rats, subskill=subskill, qtype=qtype,
              explanation=explanation, tags=tags, est=est, stimulus=stimulus)


def dispatch(table, rng, difficulty):
    """Legacy entry point: run a random family of ``table`` for ``difficulty``."""
    from . import registry
    fns = table.get(difficulty) or table["medium"]
    return registry.run_family(rng.choice(fns), rng, difficulty)


# =========================================================================== #
# SUBJECT-VERB AGREEMENT
# =========================================================================== #
# Verb forms: (singular, plural, past, -ing, tail) split by subject category so
# the sentences stay plausible (people vs. things).
_SVA_VERBS_T = [
    ("requires", "require", "required", "requiring", "careful handling"),
    ("remains", "remain", "remained", "remaining", "a subject of debate"),
    ("appears", "appear", "appeared", "appearing", "in the final report"),
    ("reflects", "reflect", "reflected", "reflecting", "decades of change"),
    ("attracts", "attract", "attracted", "attracting", "attention every year"),
    ("belongs", "belong", "belonged", "belonging", "to the city archive"),
    ("seems", "seem", "seemed", "seeming", "surprisingly fragile"),
    ("suggests", "suggest", "suggested", "suggesting", "a different explanation"),
    ("needs", "need", "needed", "needing", "a second look"),
    ("deserves", "deserve", "deserved", "deserving", "closer study"),
]
_SVA_VERBS_P = [
    ("arrives", "arrive", "arrived", "arriving", "before the deadline"),
    ("works", "work", "worked", "working", "late during the festival"),
    ("receives", "receive", "received", "receiving", "a detailed schedule"),
    ("meets", "meet", "met", "meeting", "every Thursday afternoon"),
    ("expects", "expect", "expected", "expecting", "a busy season"),
    ("plans", "plan", "planned", "planning", "to present in May"),
    ("prefers", "prefer", "preferred", "preferring", "the earlier start time"),
    ("deserves", "deserve", "deserved", "deserving", "more credit"),
    ("hopes", "hope", "hoped", "hoping", "to finish by spring"),
    ("speaks", "speak", "spoke", "speaking", "at the opening ceremony"),
]
# (subject phrase, is_plural, category) — the noun nearest the blank is the
# opposite number from the head noun, which is the whole point of the trap.
_SVA_OF = [
    ("The collection of rare coins", False, "t"),
    ("The list of approved vendors", False, "t"),
    ("The box of old photographs", False, "t"),
    ("The team of researchers", False, "p"),
    ("The set of instructions", False, "t"),
    ("A bouquet of fresh flowers", False, "t"),
    ("The leader of the expeditions", False, "p"),
    ("The sound of the church bells", False, "t"),
    ("The captain of the rowers", False, "p"),
    ("The author of the essays", False, "p"),
    ("The results of the experiment", True, "t"),
    ("The shelves near the entrance", True, "t"),
    ("The players on the team", True, "p"),
    ("The paintings in the gallery", True, "t"),
    ("The windows of the old house", True, "t"),
    ("The ingredients in the sauce", True, "t"),
    ("The editors of the magazine", True, "p"),
    ("The trails through the forest", True, "t"),
    ("The nurses on the night shift", True, "p"),
    ("The founders of the company", True, "p"),
]
_SVA_INTER_MED = ["according to the report", "in most years", "as a rule",
                  "for better or worse", "at least on paper", "in the curator's view"]
_SVA_INTER_HARD = [
    "along with several related items noted earlier",
    "unlike the examples discussed in the previous chapter",
    "despite what the introduction seemed to promise",
    "which the committee reviewed at length last spring",
    "much to the surprise of the visiting inspectors",
    "together with the notes that accompanied the original donation",
]


def _ing(verb_phrase: str) -> str:
    """-ing form of the first word of a plural-form verb phrase ('take' -> 'taking')."""
    w = verb_phrase.split()[0]
    if w in ("are", "were", "have", "has", "is", "was"):
        return "being"
    if w.endswith("ie"):
        return w[:-2] + "ying"
    if w.endswith("e") and not w.endswith("ee"):
        return w[:-1] + "ing"
    if len(w) > 2 and w[-1] in "tnpgm" and w[-2] in "aeiou" and w[-3] not in "aeiou" and w not in ("open",):
        return w + w[-1] + "ing"
    return w + "ing"


def _sva_opts(plural, verbs, hard_tense=False):
    sing, plur, past, ing, tail = verbs
    right, wrong = (plur, sing) if plural else (sing, plur)
    num = "plural" if plural else "singular"
    anti = "singular" if plural else "plural"
    if hard_tense:
        aux_r, aux_w = ("have", "has") if plural else ("has", "have")
        pp = past
        correct = (f"{aux_r} {pp}", f"Correct. The subject is {num}, and 'since'/'for' "
                   f"calls for the present perfect, so '{aux_r} {pp}' is right.")
        ds = [(f"{aux_w} {pp}", f"Agreement error: '{aux_w}' is {anti}, but the subject is {num}."),
              (past, "The time phrase describes a period reaching to the present, which "
                     "needs the present perfect, not the simple past."),
              (f"{aux_w} been {ing}", f"'{aux_w}' is {anti}, so this form does not agree with the "
                                       f"{num} subject.")]
        return correct, ds, f"{aux_r} {pp}"
    correct = (right, f"Correct. The subject is {num}, so the verb must be '{right}'.")
    ds = [(wrong, f"Agreement error: '{wrong}' is {anti}, but the true subject is {num}. "
                  "Ignore the words between the subject and the verb."),
          (ing, "An -ing form alone cannot serve as the main verb of the sentence."),
          (f"to {plur}" if plur != "are" else "to be",
           "An infinitive cannot serve as the main verb here.")]
    return correct, ds, right


@family(fill_in=True)
def sva_of_phrase(rng, difficulty):
    """Head noun + 'of' phrase whose nearer noun has the opposite number."""
    subj, plural, cat = rng.choice(_SVA_OF)
    verbs = rng.choice(_SVA_VERBS_P if cat == "p" else _SVA_VERBS_T)
    hard = difficulty == "hard"
    if difficulty == "easy":
        mid = ""
    elif difficulty == "medium":
        mid = ", " + rng.choice(_SVA_INTER_MED) + ","
    else:
        mid = ", " + rng.choice(_SVA_INTER_HARD) + ","
    correct, ds, right = _sva_opts(plural, verbs, hard_tense=hard)
    tail = verbs[4]
    if hard:
        tail = tail + " " + rng.choice(["since 2019", "for several years", "since the renovation"])
    head = subj.split(" of ")[0] if " of " in subj else " ".join(subj.split()[:2])
    text = f"{subj}{mid} ___ {tail}."
    return build(rng, fill(text, conv_stem(rng)), correct, ds,
                 subskill="subject_verb_agreement",
                 explanation=(f"The verb agrees with the head of the subject ('{head}'), "
                              f"not with the noun closest to it, so '{right}' is correct."),
                 tags=["conventions", "agreement"])


_SVA_PAIRS_P = [("the director", "the actors"), ("the coach", "the players"),
                ("the chef", "the servers"), ("the editor", "the reporters"),
                ("the mayor", "the council members"), ("the guide", "the hikers")]
_SVA_PAIRS_T = [("the bridge", "the tunnels"), ("the mural", "the sculptures"),
                ("the engine", "the brakes"), ("the lobby", "the hallways"),
                ("the recipe", "the photographs"), ("the budget", "the schedules")]


@family(fill_in=True)
def sva_compound(rng, difficulty):
    """Compound subjects: and (plural), or/nor (nearer noun), as well as (first)."""
    cat = rng.choice(["p", "t"])
    pairs = _SVA_PAIRS_P if cat == "p" else _SVA_PAIRS_T
    a, b = rng.choice(pairs)
    verbs = rng.choice(_SVA_VERBS_P if cat == "p" else _SVA_VERBS_T)
    sing, plur, past, ing, tail = verbs
    kinds = {"easy": ["and", "and", "or_near_plural"],
             "medium": ["or_near_plural", "or_near_sing", "nor"],
             "hard": ["as_well_as", "nor_sing", "or_near_sing"]}[difficulty]
    kind = rng.choice(kinds)
    if kind == "and":
        subj = f"{cap(a)} and {b}"
        plural, rule = True, "two subjects joined by 'and' form a plural subject"
    elif kind == "or_near_plural":
        subj = f"{cap(a)} or {b}"
        plural, rule = True, "with 'or' the verb agrees with the nearer subject, which is plural"
    elif kind == "or_near_sing":
        subj = f"{cap(b)} or {a}"
        plural, rule = False, "with 'or' the verb agrees with the nearer subject, which is singular"
    elif kind == "nor":
        subj = f"Neither {a} nor {b}"
        plural, rule = True, "with 'neither...nor' the verb agrees with the nearer subject, which is plural"
    elif kind == "nor_sing":
        subj = f"Neither {b} nor {a}"
        plural, rule = False, "with 'neither...nor' the verb agrees with the nearer subject, which is singular"
    else:
        subj = f"{cap(a)}, as well as {b},"
        plural, rule = False, ("'as well as' does not make a compound subject, so the verb "
                               "agrees with the first subject, which is singular")
    correct, ds, right = _sva_opts(plural, verbs)
    text = f"{subj} ___ {tail}."
    return build(rng, fill(text, conv_stem(rng)), correct, ds,
                 subskill="subject_verb_agreement",
                 explanation=f"Here {rule}, so '{right}' is correct.",
                 tags=["conventions", "agreement", "compound-subject"])


_SVA_INDEF = {
    "easy": [("Each of the", True, False), ("Everyone among the", True, False),
             ("Every one of the", True, False), ("Several of the", True, True),
             ("Both of the", True, True), ("Many of the", True, True)],
    "medium": [("Neither of the", True, False), ("Either of the", True, False),
               ("One of the", True, False), ("Few of the", True, True),
               ("Each of the", True, False), ("Most of the", True, True)],
    "hard": [("A number of the", True, True), ("The number of", True, False),
             ("Not one of the", True, False), ("More than one of the", True, False),
             ("A majority of the", True, True), ("Each one of the", True, False)],
}
_SVA_GROUPS_P = ["new employees", "visiting scholars", "student volunteers",
                 "festival musicians", "junior architects", "exchange students"]
_SVA_GROUPS_T = ["proposals", "old manuscripts", "sample jars", "wooden bridges",
                 "lighthouse lamps", "solar panels"]
_SVA_INDEF_RULE = {
    "Each of the": "'each' is singular even when it is followed by a plural noun",
    "Everyone among the": "'everyone' is singular",
    "Every one of the": "'every one' is singular",
    "Several of the": "'several' is plural",
    "Both of the": "'both' is plural",
    "Many of the": "'many' is plural",
    "Neither of the": "'neither' is singular",
    "Either of the": "'either' is singular",
    "One of the": "'one' is singular; the plural noun after 'of' is not the subject",
    "Few of the": "'few' is plural",
    "Most of the": "'most' takes the number of the noun it refers to, which is plural here",
    "A number of the": "'a number of' means 'several' and is plural",
    "The number of": "'the number of' names a single quantity and is singular",
    "Not one of the": "'not one' is singular",
    "More than one of the": "'more than one' is treated as singular",
    "A majority of the": "'a majority of' takes the number of the following plural noun",
    "Each one of the": "'each one' is singular",
}


@family(fill_in=True)
def sva_indefinite(rng, difficulty):
    """Indefinite pronouns and quantity phrases (each, several, a number of)."""
    quant, _, plural = rng.choice(_SVA_INDEF[difficulty])
    cat = rng.choice(["p", "t"])
    group = rng.choice(_SVA_GROUPS_P if cat == "p" else _SVA_GROUPS_T)
    verbs = rng.choice(_SVA_VERBS_P if cat == "p" else _SVA_VERBS_T)
    if quant == "The number of":
        verbs = rng.choice([("has grown", "have grown", "grew", "growing", "every year"),
                            ("surprises", "surprise", "surprised", "surprising", "the organizers"),
                            ("remains", "remain", "remained", "remaining", "small")])
    correct, ds, right = _sva_opts(plural, verbs)
    text = f"{quant} {group} ___ {verbs[4]}."
    return build(rng, fill(text, conv_stem(rng)), correct, ds,
                 subskill="subject_verb_agreement",
                 explanation=f"Here {_SVA_INDEF_RULE[quant]}, so '{right}' is correct.",
                 tags=["conventions", "agreement", "indefinite-pronoun"])


_SVA_INV = [
    # (opening, noun phrase (after verb), plural, cat)
    ("There", "several reasons for the delay", True, "t"),
    ("There", "a simple reason for the delay", False, "t"),
    ("There", "two entrances to the garden", True, "t"),
    ("There", "only one entrance to the garden", False, "t"),
    ("Here", "the keys to the storeroom", True, "t"),
    ("Here", "the key to the storeroom", False, "t"),
    ("There", "a long line outside the bakery", False, "t"),
    ("There", "many ways to reach the summit", True, "t"),
    ("There", "no shortage of volunteers", False, "t"),
    ("There", "three candidates for the position", True, "p"),
    ("Here", "the photographs from the expedition", True, "t"),
    ("Here", "a map of the old quarry", False, "t"),
    ("There", "a reason the bridge was closed", False, "t"),
    ("There", "several errors in the first draft", True, "t"),
    ("Across the valley", "the ruins of a stone mill", True, "t"),
    ("Across the valley", "a single stone mill", False, "t"),
    ("Inside the envelope", "two faded tickets", True, "t"),
    ("Inside the envelope", "a single faded ticket", False, "t"),
    ("Next to the fountain", "the statues of the founders", True, "t"),
    ("Next to the fountain", "a statue of the founder", False, "t"),
    ("Among the exhibits", "a rare map of the harbor", False, "t"),
    ("Among the exhibits", "three maps of the harbor", True, "t"),
    ("Beneath the floorboards", "a bundle of letters", False, "t"),
    ("Beneath the floorboards", "dozens of letters", True, "t"),
    ("At the end of the hallway", "the offices of the dean", True, "t"),
    ("At the end of the hallway", "the office of the dean", False, "t"),
    ("On the committee", "two former mayors", True, "p"),
    ("On the committee", "a former mayor", False, "p"),
    ("Behind the curtain", "the musicians", True, "p"),
    ("Behind the curtain", "the conductor", False, "p"),
]


@family(fill_in=True)
def sva_inverted(rng, difficulty):
    """Inverted order: the subject follows the verb ('There ___ several...')."""
    pool = [x for x in _SVA_INV if (x[0] in ("There", "Here")) == (difficulty == "easy")]
    opening, np_, plural, cat = rng.choice(pool)
    tense = rng.choice(["present", "past"]) if difficulty == "hard" else "present"
    if tense == "present":
        right, wrong = ("are", "is") if plural else ("is", "are")
        others = [("was" if plural else "were"), "being"]
    else:
        right, wrong = ("were", "was") if plural else ("was", "were")
        others = [("is" if plural else "are"), "being"]
        np_ = np_ + rng.choice([" at the time", " when the inspectors visited"])
    num = "plural" if plural else "singular"
    correct = (right, f"Correct. The subject comes after the verb and is {num}, so "
                      f"'{right}' is needed.")
    ds = [(wrong, f"Agreement error: the subject ('{np_.split(' of ')[0]}') is {num}."),
          (others[0], "This form is the wrong tense for the sentence and does not match "
                      "the subject's number."),
          (others[1], "'being' cannot stand alone as the main verb.")]
    text = f"{opening} ___ {np_}."
    return build(rng, fill(text, conv_stem(rng)), correct, ds,
                 subskill="subject_verb_agreement",
                 explanation=(f"When a sentence opens with '{opening}', the subject follows "
                              f"the verb. That subject is {num}, so '{right}' is correct."),
                 tags=["conventions", "agreement", "inverted-order"])


# (plural noun, relative pronoun, verb sing, verb plural, -ing, past participle, object, category)
_SVA_REL = [
    ("researchers", "who", "oversees", "oversee", "overseeing", "overseen", "the study", "p"),
    ("architects", "who", "designs", "design", "designing", "designed", "the plaza", "p"),
    ("volunteers", "who", "runs", "run", "running", "run", "the shelter", "p"),
    ("engineers", "who", "maintains", "maintain", "maintaining", "maintained", "the dam", "p"),
    ("novels", "that", "describes", "describe", "describing", "described", "the harbor town", "t"),
    ("bridges", "that", "spans", "span", "spanning", "spanned", "the river", "t"),
    ("theories", "that", "explains", "explain", "explaining", "explained", "the data", "t"),
    ("murals", "that", "decorates", "decorate", "decorating", "decorated", "the station", "t"),
]


@family(fill_in=True)
def sva_relative(rng, difficulty):
    """Relative clauses: 'one of the X who ___' (plural) vs 'the only one of the X who ___'."""
    noun, rel, sing, plur, ing, pp, obj, cat = rng.choice(_SVA_REL)
    name = rng.choice(NAMES)
    lead = {"p": f"{name} is", "t": f"The {noun[:-1]} {name} chose is"}[cat]
    form = rng.choice({"easy": ["plain"], "medium": ["one_of", "plain"],
                       "hard": ["one_of", "only_one"]}[difficulty])
    if form == "plain":
        plural = False
        text = f"{lead} the {noun[:-1]} {rel} ___ {obj}."
        rule = f"the pronoun '{rel}' refers to the singular '{noun[:-1]}'"
    elif form == "one_of":
        plural = True
        text = f"{lead} one of the {noun} {rel} ___ {obj}."
        rule = (f"'{rel}' refers to the plural '{noun}' (several {noun} do this, and "
                f"{name if cat == 'p' else 'this one'} is one of them)")
    else:
        plural = False
        text = f"{lead} the only one of the {noun} {rel} ___ {obj}."
        rule = (f"'the only one' makes '{rel}' refer to a single {noun[:-1]}, so the "
                "verb is singular")
    right, wrong = (plur, sing) if plural else (sing, plur)
    num = "plural" if plural else "singular"
    correct = (right, f"Correct. In this clause {rule}, so '{right}' is required.")
    ds = [(wrong, f"Agreement error: the verb's subject here is {num}."),
          (ing, "An -ing form alone cannot serve as the verb of the clause."),
          (f"having {pp}", "This participle phrase leaves the relative clause without a finite verb.")]
    return build(rng, fill(text, conv_stem(rng)), correct, ds,
                 subskill="subject_verb_agreement",
                 explanation=(f"Find what the relative pronoun stands for: {rule}. "
                              f"So '{right}' is correct."),
                 tags=["conventions", "agreement", "relative-clause"])


_SVA_COLL = [("The committee", "p"), ("The jury", "p"), ("The orchestra", "p"),
             ("The faculty", "p"), ("The audience", "p"), ("The crew", "p"),
             ("The family", "p"), ("The board", "p"), ("The cast", "p")]
_SVA_COLL_PH = ["of twelve members", "of forty musicians", "of retired judges",
                "of volunteers from three towns", "of young performers",
                "of parents and teachers"]
_SVA_FIELDS = ["Economics", "Physics", "Statistics", "Mathematics", "Linguistics",
               "Gymnastics"]
_SVA_FIELD_TAILS = ["a demanding subject for first-year students",
                    "the department's most popular elective",
                    "offered only in the spring term"]


@family(fill_in=True)
def sva_collective(rng, difficulty):
    """Collective nouns and -ics subjects are singular; plural-looking bait."""
    if difficulty == "easy":
        subj, cat = rng.choice(_SVA_COLL)
        verbs = rng.choice(_SVA_VERBS_P if cat == "p" else _SVA_VERBS_T)
        text_subj = subj
        rule = f"a collective noun like '{subj.split()[1]}' acting as a unit is singular"
    elif difficulty == "medium":
        subj, cat = rng.choice(_SVA_COLL)
        verbs = rng.choice(_SVA_VERBS_P if cat == "p" else _SVA_VERBS_T)
        text_subj = f"{subj} {rng.choice(_SVA_COLL_PH)}"
        rule = (f"the collective noun '{subj.split()[1]}' is singular even though the "
                "phrase after it names many members")
    else:
        if rng.random() < 0.5:
            field = rng.choice(_SVA_FIELDS)
            verbs = ("is", "are", "was", "being", rng.choice(_SVA_FIELD_TAILS))
            text_subj = f"{field}, like most of the courses that end with the letter s,"
            rule = f"'{field}' names one field of study and is singular despite its -s ending"
        else:
            subj, cat = rng.choice(_SVA_COLL)
            verbs = rng.choice(_SVA_VERBS_P if cat == "p" else _SVA_VERBS_T)
            text_subj = (f"{subj}, whose members {rng.choice(['rarely agree on anything', 'come from six countries', 'were chosen by lottery'])},")
            rule = (f"'{subj.split()[1]}' is a singular collective noun; the plural "
                    "'members' inside the clause is not the subject")
    correct, ds, right = _sva_opts(False, verbs)
    text = f"{text_subj} ___ {verbs[4]}."
    return build(rng, fill(text, conv_stem(rng)), correct, ds,
                 subskill="subject_verb_agreement",
                 explanation=f"Here {rule}, so '{right}' is correct.",
                 tags=["conventions", "agreement", "collective-noun"])


# Mini-passage scenarios: (lead sentence, subject phrase, plural, be-forms used?,
# verb forms (sing, plur, past, ing, tail), closing sentence)
_SVA_PASSAGES = [
    ("The city archive holds thousands of letters from the 1890s.",
     "The handwriting in many of the letters", False,
     ("is", "are", "was", "being", "difficult to read without magnification"),
     "Volunteers have begun transcribing them one page at a time."),
    ("Every spring, the marsh fills with migrating birds.",
     "The reeds along the eastern shore", True,
     ("provides", "provide", "provided", "providing", "cover for nesting pairs"),
     "Local birders count the nests from a wooden platform."),
    ("The bakery on Elm Street opened in 1962.",
     "Its recipe for rye bread, unchanged for sixty years,", False,
     ("draws", "draw", "drew", "drawing", "customers from neighboring towns"),
     "The owners still mill part of the flour themselves."),
    ("The robotics club meets after school on Tuesdays.",
     "The students who built last year's winning robot", True,
     ("mentors", "mentor", "mentored", "mentoring", "the newer members"),
     "Their next competition is in March."),
    ("Jupiter's moon Europa is covered by a shell of ice.",
     "The cracks that crisscross its surface", True,
     ("hints", "hint", "hinted", "hinting", "at an ocean hidden below"),
     "A planned mission will fly past the moon dozens of times."),
    ("The town's annual kite festival takes place on the first Saturday in June.",
     "The field behind the elementary school", False,
     ("fills", "fill", "filled", "filling", "with families by midmorning"),
     "Prizes go to the largest kite and the most unusual design."),
    ("Nadia restores antique clocks in a small workshop downtown.",
     "The gears inside a typical mantel clock", True,
     ("requires", "require", "required", "requiring", "cleaning every few years"),
     "She keeps a drawer of spare parts sorted by century."),
    ("The documentary follows a team of cave divers in Mexico.",
     "The footage from the deepest chambers", False,
     ("reveals", "reveal", "revealed", "revealing", "formations no one had mapped"),
     "The film premiered at a festival last fall."),
    ("Olive trees can live for more than a thousand years.",
     "The oldest trees in the grove, planted long before the village existed,", True,
     ("yields", "yield", "yielded", "yielding", "fruit every other autumn"),
     "Farmers harvest them by hand with long wooden rakes."),
    ("The library's reading room was renovated last year.",
     "The tall windows, each one framed in oak,", True,
     ("lets", "let", "let", "letting", "in light until late afternoon"),
     "Students now compete for the seats nearest the glass."),
    ("The museum's new wing is devoted to textiles.",
     "A tapestry of woven silk threads", False,
     ("hangs", "hang", "hung", "hanging", "at the far end of the main hall"),
     "Curators rotate the pieces to limit their exposure to light."),
    ("The high school orchestra toured three cities over spring break.",
     "The set of pieces chosen for the tour", False,
     ("includes", "include", "included", "including", "two student compositions"),
     "Recordings of the concerts are posted on the school's website."),
    ("Theo repairs bicycles out of his garage on weekends.",
     "The tools hanging above his workbench", True,
     ("belongs", "belong", "belonged", "belonging", "to his grandfather"),
     "He refuses to replace them with newer models."),
    ("The coral nursery sits in a shallow lagoon.",
     "Each of the frames anchored to the seafloor", False,
     ("holds", "hold", "held", "holding", "about forty coral fragments"),
     "Divers check the frames twice a month."),
]


@family(fill_in=True)
def sva_passage(rng, difficulty):
    """Two- or three-sentence passage with the agreement blank in the middle."""
    lead, subj, plural, verbs, close = rng.choice(_SVA_PASSAGES)
    sing, plur, past, ing, tail = verbs
    right, wrong = (plur, sing) if plural else (sing, plur)
    num = "plural" if plural else "singular"
    anti = "singular" if plural else "plural"
    aux_w = "have" if not plural else "has"
    correct = (right, f"Correct. The subject of this sentence is {num}, so '{right}' agrees with it.")
    ds = [(wrong, f"Agreement error: '{wrong}' is {anti}, but the subject is {num}; the "
                  "noun nearest the blank is not the subject."),
          (ing, "An -ing form alone leaves the sentence without a main verb."),
          (f"{aux_w} been {ing}", f"'{aux_w}' is {anti} and does not agree with the {num} subject.")]
    if difficulty == "easy":
        text = f"{lead} {subj} ___ {tail}."
    elif difficulty == "medium":
        text = f"{lead} {subj} ___ {tail}. {close}"
    else:
        extra = rng.choice([", as the staff often point out,", ", perhaps surprisingly,",
                            ", at least according to the records,"])
        s = subj.rstrip(",")
        text = f"{lead} {s}{extra} ___ {tail}. {close}"
    return build(rng, fill(text, conv_stem(rng)), correct, ds,
                 subskill="subject_verb_agreement",
                 explanation=(f"Locate the subject of the sentence with the blank: it is "
                              f"{num}, so the verb is '{right}'."),
                 tags=["conventions", "agreement", "passage"], est=55)


@family(fill_in=True)
def sva_clause_options(rng, difficulty):
    """The blank covers subject + verb; each option is a whole clause opener."""
    subj, plural, cat = rng.choice(_SVA_OF)
    sing, plur, past, ing, tail = rng.choice(_SVA_VERBS_P if cat == "p" else _SVA_VERBS_T)
    right, wrong = (plur, sing) if plural else (sing, plur)
    num = "plural" if plural else "singular"
    head = subj.split(" of ")[0] if " of " in subj else " ".join(subj.split()[:2])
    frame = rng.choice(["According to the newsletter, ___ {t}.",
                        "As the report notes, ___ {t}.",
                        "Visitors soon learn that ___ {t}.",
                        "By all accounts, ___ {t}."])
    sl = low(subj)
    correct = (f"{sl} {right}", f"Correct. The head of the subject ('{low(head)}') is {num} "
                                f"and takes '{right}'.")
    ds = [(f"{sl} {wrong}", f"The verb '{wrong}' agrees with the nearer noun, not with the "
                            f"{num} head noun '{low(head)}'."),
          (f"{sl}, {right}", "A comma must not separate a subject from its verb."),
          (f"{sl} {ing}", "An -ing form alone cannot be the main verb of the clause.")]
    if difficulty != "easy":
        ds[2] = (f"{sl}, which {right}", "Adding 'which' turns the clause into a fragment "
                                        "with no main verb.")
    text = frame.format(t=tail)
    return build(rng, fill(text, conv_stem(rng)), correct, ds,
                 subskill="subject_verb_agreement",
                 explanation=(f"The subject's head noun is '{low(head)}' ({num}), so the "
                              f"clause needs '{right}' with no comma between subject and verb."),
                 tags=["conventions", "agreement", "clause-options"], est=55)


# =========================================================================== #
# SENTENCE BOUNDARIES
# =========================================================================== #
# (clause A, clause B, relation) — B logically follows A; both are independent.
_BND = [
    ("The museum extended its hours for the festival", "attendance doubled within a week", "cause"),
    ("Coral reefs support a quarter of all marine species", "their loss would ripple through the food web", "cause"),
    ("The new bridge cut the commute in half", "local businesses reported a surge in customers", "cause"),
    ("Volunteers planted three hundred saplings along the river", "the banks are already more stable", "cause"),
    ("The orchestra rehearsed the symphony for weeks", "the premiere drew a standing ovation", "cause"),
    ("Solar panels now cover the school's roof", "the building's energy bills dropped sharply", "cause"),
    ("The bakery sells out of sourdough by noon", "regular customers arrive early to be sure", "cause"),
    ("Migrating cranes stop at the wetland each autumn", "birdwatchers gather to count them", "cause"),
    ("The committee approved the revised budget", "the new plan takes effect next month", "cause"),
    ("Heavy rain delayed the construction schedule", "the crew worked double shifts to catch up", "cause"),
    ("The library digitized its oldest manuscripts", "researchers can now study them remotely", "cause"),
    ("The athletes trained at high altitude for months", "their endurance improved dramatically", "cause"),
    ("The documentary premiered to a packed theater", "critics praised its honest storytelling", "addition"),
    ("Engineers tested the rover in the desert", "every system performed flawlessly", "addition"),
    ("The startup designed an award-winning app", "investors took notice almost immediately", "cause"),
    ("The forecast called for clear skies", "a thunderstorm rolled in by noon", "contrast"),
    ("The novel received glowing reviews", "sales were disappointing", "contrast"),
    ("The trail is only four miles long", "it climbs nearly two thousand feet", "contrast"),
    ("The recipe looked simple", "the sauce took three attempts to get right", "contrast"),
    ("The team lost its first six games", "it finished the season with a winning record", "contrast"),
    ("The old theater seats only two hundred people", "its shows sell out months in advance", "contrast"),
    ("The glacier has retreated a mile since 1950", "scientists expect the trend to continue", "addition"),
    ("The market opens at dawn", "the best produce is gone by eight", "addition"),
    ("The lighthouse was automated in 1987", "a keeper still lives on the island", "contrast"),
]
# B clauses whose subject is longer than one word (default is one word).
_BND_SUBJ_WORDS = {"their loss": 2, "local businesses": 2, "the banks": 2, "the premiere": 2,
                   "the building's energy bills": 4, "regular customers": 2, "the crew": 2,
                   "their endurance": 2, "every system": 2, "the new plan": 3,
                   "a thunderstorm": 2, "the sauce": 2, "its shows": 2, "the best produce": 3,
                   "a keeper": 2, "it": 1}


def _split_subject(b: str):
    words = b.split()
    n = 1
    for k, v in _BND_SUBJ_WORDS.items():
        if b.startswith(k + " "):
            n = v
    return " ".join(words[:n]), " ".join(words[n:])


_BND_SUB = {"cause": ["Because", "Since", "After"], "contrast": ["Although", "While", "Even though"],
            "addition": ["When", "After", "Once"]}
_BND_ADV = {"cause": ["therefore", "as a result", "consequently"],
            "contrast": ["however", "nevertheless", "even so"],
            "addition": ["moreover", "in addition", "furthermore"]}
_BND_CONJ = {"cause": "so", "contrast": "but", "addition": "and"}
_JOIN_STEM = ("Which choice most effectively joins the two ideas while following the "
              "conventions of standard English?")


@family(fill_in=False)
def bnd_join_whole(rng, difficulty):
    """Whole-sentence options: period / semicolon / dependent-clause joins."""
    a, b, rel = rng.choice(_BND)
    b_cap = cap(b)
    if difficulty == "hard":
        sub = rng.choice(_BND_SUB[rel])
        dep = f"{sub} {low(a)}"
        correct = (f"{dep}, {b}.", "Correct. A dependent (subordinate) clause is joined to "
                                   "the main clause with a comma.")
        ds = [(f"{dep}. {b_cap}.", "The first part is a dependent clause; ending it with a "
                                  "period leaves a sentence fragment."),
              (f"{dep}; {b}.", "A semicolon joins two independent clauses, but the first "
                               "part here is dependent, not independent."),
              (f"{dep}, and {b}.", "A dependent clause cannot be joined to the main clause "
                                   "with 'and'; that leaves the sentence without a main clause.")]
        expl = ("The opening is a dependent clause, so it attaches to the main clause with "
                "a comma; a period makes a fragment and a semicolon wrongly treats it as "
                "independent.")
    elif difficulty == "medium":
        conj = _BND_CONJ[rel]
        variant = rng.choice(["semi", "conj"])
        if variant == "semi":
            correct = (f"{a}; {b}.", "Correct. A semicolon links two closely related "
                                     "independent clauses.")
        else:
            correct = (f"{a}, {conj} {b}.", f"Correct. A comma plus the coordinating "
                                            f"conjunction '{conj}' joins two independent clauses.")
        ds = [(f"{a}, {b}.", "Comma splice: a comma alone cannot join two independent clauses."),
              (f"{a} {b}.", "Run-on (fused sentence): the clauses need punctuation between them."),
              (f"{a}; {conj} {b}.", f"Don't pair a semicolon with the coordinating conjunction '{conj}'.")]
        expl = ("Both clauses are independent, so they need a semicolon or a comma plus a "
                "coordinating conjunction; a comma alone makes a splice and nothing makes a run-on.")
    else:
        conj = _BND_CONJ[rel]
        if rng.random() < 0.5:
            correct = (f"{a}. {b_cap}.", "Correct. Two independent clauses can stand as two "
                                         "separate sentences joined by a period.")
        else:
            correct = (f"{a}, {conj} {b}.", f"Correct. A comma plus the coordinating conjunction "
                                            f"'{conj}' joins two independent clauses.")
        ds = [(f"{a}, {b}.", "Comma splice: a comma alone cannot join two independent clauses."),
              (f"{a} {b}.", "Run-on (fused sentence): the two clauses need punctuation between them."),
              (f"{a}; {conj} {b}.", f"Don't pair a semicolon with a coordinating conjunction like '{conj}'.")]
        expl = ("Each clause is independent (it could stand alone), so separate them with a "
                "period or join them with a comma plus a conjunction, not a comma alone "
                "(splice) or nothing (run-on).")
    return build(rng, _JOIN_STEM, correct, ds, subskill="clause_joining",
                 explanation=expl, tags=["conventions", "boundaries"])


@family(fill_in=True)
def bnd_blank_junction(rng, difficulty):
    """The blank sits at the junction; options carry punctuation plus words."""
    a, b, rel = rng.choice(_BND)
    aw = a.split()
    bw = b.split()
    a_last, a_rest = aw[-1], " ".join(aw[:-1])
    b_first, b_rest = bw[0], " ".join(bw[1:])
    conj = _BND_CONJ[rel]
    kinds = {"easy": ["period", "semi"], "medium": ["semi", "conj"],
             "hard": ["conj", "semi_adv", "period_adv"]}[difficulty]
    kind = rng.choice(kinds)
    adv = rng.choice(_BND_ADV[rel])
    if kind == "period":
        correct = (f"{a_last}. {cap(b_first)}", "Correct. A period separates the two independent clauses.")
    elif kind == "semi":
        correct = (f"{a_last}; {b_first}", "Correct. A semicolon joins two related independent clauses.")
    elif kind == "conj":
        correct = (f"{a_last}, {conj} {b_first}", f"Correct. A comma and the coordinating "
                                                  f"conjunction '{conj}' join two independent clauses.")
    elif kind == "semi_adv":
        correct = (f"{a_last}; {adv}, {b_first}", f"Correct. A conjunctive adverb like '{adv}' "
                                                  "needs a semicolon before it and a comma after it.")
    else:
        correct = (f"{a_last}. {cap(adv)}, {b_first}", f"Correct. The clauses are separated by a "
                                                       f"period, and '{adv}' opens the new sentence.")
    pool = [
        (f"{a_last}, {b_first}", "Comma splice: a comma alone cannot join two independent clauses."),
        (f"{a_last} {b_first}", "Run-on: two independent clauses are fused with no punctuation."),
        (f"{a_last}; {conj} {b_first}", f"A semicolon should not be paired with the conjunction '{conj}'."),
        (f"{a_last}, {adv}, {b_first}", f"'{adv}' is a conjunctive adverb, not a conjunction; "
                                        "commas alone leave a comma splice."),
        (f"{a_last}; {conj}, {b_first}", f"A semicolon plus '{conj}' plus a comma piles up "
                                         "punctuation that does not belong together."),
        (f"{a_last}, {conj}, {b_first}", f"No comma should follow the conjunction '{conj}'."),
    ]
    pool.append((f"{a_last}, {conj} {adv}, {b_first}", f"'{conj}' and '{adv}' signal the same link; "
                                                       "pairing them is redundant and the comma "
                                                       "after the conjunction is wrong."))
    if kind in ("semi_adv", "period_adv"):
        ds = [pool[3], pool[0], pool[6]]
    elif kind == "conj":
        ds = [pool[0], pool[2], pool[5]]
    else:
        ds = [pool[0], pool[1], pool[2]]
    text = f"{a_rest} ___ {b_rest}."
    return build(rng, fill(text, conv_stem(rng)), correct, ds, subskill="clause_joining",
                 explanation=("Both halves are independent clauses, so they must be joined with a "
                              "period, a semicolon, or a comma plus a coordinating conjunction."),
                 tags=["conventions", "boundaries", "junction"])


@family(fill_in=True)
def bnd_conjunctive_adverb(rng, difficulty):
    """Conjunctive adverbs (however, therefore) need a semicolon, not a comma."""
    a, b, rel = rng.choice(_BND)
    adv = rng.choice(_BND_ADV[rel])
    sub = rng.choice(_BND_SUB[rel])
    conj = _BND_CONJ[rel]
    if difficulty == "easy":
        correct = (f"; {adv},", f"Correct. '{adv}' is a conjunctive adverb, so a semicolon "
                                "comes before it and a comma after it.")
        ds = [(f", {adv},", "Comma splice: a conjunctive adverb does not have the joining "
                            "power of a conjunction."),
              (f" {adv},", "Run-on: nothing separates the two independent clauses."),
              (f", {conj} {adv},", f"'{conj}' and '{adv}' both signal the same link; "
                                   "the pairing is redundant and awkward.")]
        text = f"{a}___ {b}."
    elif difficulty == "medium":
        bw = b.split()
        b_first, b_rest = bw[0], " ".join(bw[1:])
        correct = (f"; {adv}, {b_first}", f"Correct. A semicolon joins the clauses and '{adv}' "
                                          "is set off with a comma.")
        ds = [(f", {adv}, {b_first}", "Comma splice: a conjunctive adverb cannot join clauses with commas alone."),
              (f", {conj} {adv}, {b_first}", f"'{conj}' and '{adv}' signal the same relationship; "
                                             "the pairing is redundant."),
              (f" {adv}, {b_first}", "Run-on: the independent clauses are fused.")]
        text = f"{a}___ {b_rest}."
    else:
        # adverb inside the second clause: "A. B-subject, however, rest."
        b_subj, b_rest = _split_subject(b)
        correct = (f". {cap(b_subj)}, {adv}, {b_rest}", f"Correct. A period ends the first "
                                                        f"sentence, and '{adv}' inside the "
                                                        "second is set off by commas.")
        ds = [(f", {b_subj}, {adv}, {b_rest}", "Comma splice between two independent clauses."),
              (f"; {b_subj}, {adv} {b_rest}", f"The semicolon is fine, but '{adv}' needs a "
                                              "comma on both sides when it interrupts a clause."),
              (f", {conj} {b_subj}, {adv}, {b_rest}", f"'{conj}' and '{adv}' both signal the same "
                                                      "relationship; one of them is redundant.")]
        text = f"{a}___."
    return build(rng, fill(text, conv_stem(rng)), correct, ds, subskill="clause_joining",
                 explanation=(f"Words like '{adv}' are conjunctive adverbs, not conjunctions: "
                              "they cannot join two independent clauses with a comma, so a "
                              "semicolon or period is required."),
                 tags=["conventions", "boundaries", "conjunctive-adverb"], est=50)


_BND_LISTS = [
    ("The exhibit features three local artists", ["Lena Marsh", "Omar Haddad", "Priya Sen"]),
    ("The committee approved three projects", ["a new footbridge", "a riverside park", "a branch library"]),
    ("The hike passes four landmarks", ["a waterfall", "an abandoned mill", "a stone chapel", "a lookout tower"]),
    ("The recipe calls for only three ingredients", ["flour", "butter", "sea salt"]),
    ("The course covers three periods", ["the early republic", "the industrial age", "the postwar decades"]),
    ("The lab studies three kinds of pollinators", ["bees", "moths", "hummingbirds"]),
    ("The festival awards prizes in three categories", ["documentary", "animation", "short fiction"]),
    ("The clinic offers three services at no cost", ["vision screening", "flu shots", "dental checkups"]),
    ("The orchestra performed works by three composers", ["Haydn", "Price", "Takemitsu"]),
    ("The report identifies three risks", ["rising costs", "staff turnover", "aging equipment"]),
]
_BND_EXPLAIN = [
    ("The results surprised the team", "every sample contained traces of copper"),
    ("The decision was easy", "the second site was closer to the river"),
    ("One detail stood out", "none of the witnesses had heard the alarm"),
    ("The reason is simple", "the bridge cannot bear heavy trucks"),
    ("The verdict was unanimous", "the design clearly deserved the prize"),
    ("The plan had a flaw", "it depended on a single supplier"),
    ("The crew faced a new problem", "the only road to the site had washed out"),
    ("The data told a clear story", "the colony had doubled in size"),
    ("The audience had one complaint", "the hall was far too cold"),
    ("The coach made an unusual request", "the team would practice in silence"),
    ("Her answer surprised the panel", "she had never taken a formal lesson"),
    ("The experiment had an obvious limitation", "it lasted only a single week"),
]


@family(fill_in=True)
def bnd_colon(rng, difficulty):
    """A colon after a complete clause introduces a list or an explanation."""
    if difficulty == "easy" or (difficulty == "medium" and rng.random() < 0.5):
        lead, items = rng.choice(_BND_LISTS)
        lst = ", ".join(items[:-1]) + f", and {items[-1]}"
        first = items[0]
        rest = lst[len(first):]
        correct = (f"{lead.split()[-1]}: {first}", "Correct. A colon follows a complete "
                                                   "clause to introduce the list.")
        ds = [(f"{lead.split()[-1]}; {first}", "A semicolon must have an independent clause "
                                                "on each side; a list is not a clause."),
              (f"{lead.split()[-1]}. {cap(first)}", "A period leaves the list standing alone "
                                                      "as a fragment."),
              (f"{lead.split()[-1]}, including: {first}", "A colon cannot follow 'including'; "
                                                           "the colon must come directly after "
                                                           "a complete clause.")]
        text = f"{' '.join(lead.split()[:-1])} ___{rest}."
        expl = ("The words before the blank form a complete sentence, so a colon can "
                "introduce the list that follows; a semicolon or period would leave a fragment.")
    else:
        lead, expl_clause = rng.choice(_BND_EXPLAIN)
        w = expl_clause.split()
        correct = (f"{lead.split()[-1]}: {w[0]}", "Correct. A colon after a complete clause "
                                                  "introduces the explanation that follows.")
        ds = [(f"{lead.split()[-1]}, {w[0]}", "Comma splice: two independent clauses cannot "
                                               "be joined by a comma alone."),
              (f"{lead.split()[-1]} {w[0]}", "Run-on: the two independent clauses are fused."),
              (f"{lead.split()[-1]}: and {w[0]}", "A colon should not be followed by 'and'; "
                                                   "the colon alone does the introducing.")]
        if difficulty == "hard":
            ds[1] = (f"{lead.split()[-1]} being {w[0]}",
                     "'being' is not a connector; this leaves a run-on with a dangling participle.")
        text = f"{' '.join(lead.split()[:-1])} ___ {' '.join(w[1:])}."
        expl = ("A colon can join two independent clauses when the second explains the first; "
                "a comma alone makes a splice.")
    return build(rng, fill(text, conv_stem(rng)), correct, ds, subskill="clause_joining",
                 explanation=expl, tags=["conventions", "boundaries", "colon"], est=50)


@family(fill_in=True)
def bnd_dependent(rng, difficulty):
    """Subordinate clause + main clause: fragment vs. correct comma join."""
    a, b, rel = rng.choice(_BND)
    sub = rng.choice(_BND_SUB[rel])
    conj = _BND_CONJ[rel]
    if difficulty == "easy":
        correct = (f"{low(a)}, {b}", f"Correct. The clause beginning with '{sub}' is dependent "
                                     "and is joined to the main clause with a comma.")
        ds = [(f"{low(a)}. {cap(b)}", "The first part is a dependent clause; a period leaves it "
                                      "as a fragment."),
              (f"{low(a)}; {b}", "A semicolon needs an independent clause on both sides."),
              (f"{low(a)}, {conj} {b}", f"A dependent clause cannot be joined with ', {conj}'; "
                                       "the sentence would have no main clause.")]
        text = f"{sub} ___."
    elif difficulty == "medium":
        # dependent clause second: no comma before most subordinators
        aw = a.split()
        a_first, a_rest = low(aw[0]), " ".join(aw[1:])
        correct = (f"{low(sub)} {a_first}", f"Correct. When the '{low(sub)}' clause comes second, "
                                            "it attaches without extra punctuation.")
        ds = [(f"; {low(sub)} {a_first}", "A semicolon cannot precede a dependent clause."),
              (f". {sub} {a_first}", f"'{sub} {low(a)}' cannot stand alone; it is a fragment."),
              (f", {conj} {low(sub)} {a_first}", f"'{conj}' plus '{low(sub)}' doubles the connector "
                                                  "and leaves the structure muddled.")]
        text = f"{cap(b)} ___ {a_rest}."
    else:
        # relative clause fragment: "which" trap
        bw = b.split()
        b_first, b_rest = bw[0], " ".join(bw[1:])
        correct = (f"{conj} {b_first}", f"Correct. Two independent clauses joined by a comma and the "
                                        f"coordinating conjunction '{conj}'.")
        ds = [(f"which {b_first}", "Adding 'which' turns the second half into a relative clause "
                                   "that has nothing sensible to modify."),
              (f"{b_first}", "Comma splice: a comma alone cannot join independent clauses."),
              (f"being that {b_first}", "'being that' is nonstandard and does not properly join "
                                        "the two clauses.")]
        text = f"{a}, ___ {b_rest}."
    prompt = fill(text, conv_stem(rng))
    est = 45
    return build(rng, prompt, correct, ds, subskill="clause_joining",
                 explanation=("A dependent clause cannot stand alone as a sentence and cannot be "
                              "attached with a semicolon; it joins the main clause with a comma "
                              "(or no punctuation when it comes second)."),
                 tags=["conventions", "boundaries", "dependent-clause"], est=est)


# (lead, clause A, clause B, relation, close) — coherent 3-sentence mini-passages
_BND_PASS = [
    ("Honeybees communicate the location of flowers with a dance.",
     "A scout performs a looping figure eight on the comb", "the angle of the loop points toward the food", "addition",
     "Other bees then fly off in that direction."),
    ("The town library was built in 1911 with a gift from a local merchant.",
     "The reading room still has its original oak tables", "the lighting was replaced last year", "contrast",
     "Visitors rarely notice the change."),
    ("Mangrove forests line much of the island's southern coast.",
     "Their tangled roots slow incoming waves", "the shoreline behind them erodes far less", "cause",
     "Planners now protect the forests as a flood defense."),
    ("Nina spent the summer cataloging her grandmother's recipes.",
     "Many of the cards were written in pencil", "a few had faded almost completely", "addition",
     "She scanned each one before the writing disappeared."),
    ("The city's bike-share program launched in April.",
     "Riders took twelve thousand trips in the first week", "most of those trips replaced short car rides", "addition",
     "Officials plan to add fifty more stations by fall."),
    ("The telescope's original mirror measured two meters across.",
     "Engineers replaced it with a four-meter mirror", "the instrument's resolution doubled", "cause",
     "Astronomers immediately requested more observing time."),
    ("The marsh had lost nearly half its area since 1990.",
     "Volunteers replanted native grasses two springs ago", "bird sightings rose the following year", "cause",
     "The count is repeated every May."),
    ("Caleb's robotics team entered its first regional competition in March.",
     "The robot's arm jammed during the opening round", "the team finished in the top ten anyway", "contrast",
     "They have already started redesigning the arm."),
    ("The bakery's sourdough starter is more than forty years old.",
     "The owners feed it every morning before dawn", "the loaves it produces sell out by noon", "addition",
     "Regulars arrive early to be sure of a loaf."),
    ("A small startup designed the city's new transit app.",
     "The app was free to download", "it earned revenue through partnerships with cafés near each stop", "contrast",
     "Investors took notice within months."),
    ("The old lighthouse stopped operating in 1987.",
     "Its lamp was automated decades ago", "a keeper still lives on the island", "contrast",
     "She leads tours for visitors every summer."),
    ("The coral nursery was built in a shallow lagoon.",
     "Divers grow fragments on underwater frames", "they replant the fragments on damaged reefs", "sequence",
     "More than seventy percent survive."),
]


@family(fill_in=True)
def bnd_passage(rng, difficulty):
    """Three-sentence passage; the junction blank is in the middle sentence."""
    lead, a, b, rel, close = rng.choice(_BND_PASS)
    conj = {"cause": "so", "contrast": "but", "addition": "and", "sequence": "and then"}[rel]
    adv = {"cause": "as a result", "contrast": "however", "addition": "in addition",
           "sequence": "then"}[rel]
    aw, bw = a.split(), b.split()
    a_last, a_rest = aw[-1], " ".join(aw[:-1])
    b_first, b_rest = bw[0], " ".join(bw[1:])
    kind = rng.choice({"easy": ["period", "semi"], "medium": ["semi", "conj", "period"],
                       "hard": ["conj", "semi_adv"]}[difficulty])
    if kind == "period":
        correct = (f"{a_last}. {cap(b_first)}", "Correct. A period separates the two independent clauses.")
    elif kind == "semi":
        correct = (f"{a_last}; {b_first}", "Correct. A semicolon joins two related independent clauses.")
    elif kind == "conj":
        correct = (f"{a_last}, {conj} {b_first}", f"Correct. A comma plus '{conj}' joins the two "
                                                  "independent clauses.")
    else:
        correct = (f"{a_last}; {adv}, {b_first}", f"Correct. '{adv}' is a conjunctive adverb, so "
                                                  "it follows a semicolon and takes a comma.")
    ds_all = [(f"{a_last}, {b_first}", "Comma splice: a comma alone cannot join two independent clauses."),
              (f"{a_last} {b_first}", "Run-on: the independent clauses are fused."),
              (f"{a_last}; {conj} {b_first}", f"A semicolon should not be paired with '{conj}'."),
              (f"{a_last}, {adv}, {b_first}", f"'{adv}' does not have the joining power of a "
                                              "conjunction; this is a comma splice.")]
    ds_all.append((f"{a_last}, {conj} {adv}, {b_first}", f"'{conj}' and '{adv}' signal the same "
                                                         "link; pairing them is redundant."))
    ds = ds_all[:3] if kind != "semi_adv" else [ds_all[3], ds_all[0], ds_all[4]]
    if difficulty == "hard" and kind == "conj":
        ds = [ds_all[0], ds_all[3], ds_all[2]]
    text = f"{lead} {a_rest} ___ {b_rest}. {close}"
    return build(rng, fill(text, conv_stem(rng)), correct, ds, subskill="clause_joining",
                 explanation=("The middle sentence contains two independent clauses, which must be "
                              "separated by a period or semicolon or joined with a comma and a "
                              "coordinating conjunction."),
                 tags=["conventions", "boundaries", "passage"], est=55)


# =========================================================================== #
# PUNCTUATION
# =========================================================================== #
_SING_NOUNS = [
    ("scientist", "scientist's"), ("city", "city's"), ("author", "author's"),
    ("company", "company's"), ("teacher", "teacher's"), ("gardener", "gardener's"),
    ("artist", "artist's"), ("coach", "coach's"), ("school", "school's"),
    ("engineer", "engineer's"), ("designer", "designer's"), ("committee", "committee's"),
]
_PLUR_NOUNS = [
    ("students", "students'"), ("workers", "workers'"), ("birds", "birds'"),
    ("teachers", "teachers'"), ("players", "players'"), ("residents", "residents'"),
    ("artists", "artists'"), ("companies", "companies'"), ("neighbors", "neighbors'"),
    ("divers", "divers'"),
]
_IRREG_PLUR = [("children", "children's"), ("women", "women's"), ("people", "people's"),
               ("mice", "mice's")]
_POSS_FRAMES = [
    "The {n} ___ discovery surprised everyone",
    "Nobody expected the {n} ___ schedule to change at the last minute",
    "The {n} ___ design won several awards",
    "Over the years the {n} ___ reputation grew steadily",
    "The {n} ___ results were published online in March",
    "Judges praised the {n} ___ performance",
    "The {n} ___ request was approved after a short debate",
]
# Determiners that fix the owner's number, so exactly one possessive form fits
# ("this player's", "the three players'"). Without them "The ___ reputation"
# took either "player's" or "players'" and the key was a coin flip.
_POSS_DET = {"singular": ["this", "each"],
             "plural": ["the two", "the three", "the four", "both", "these"]}
_POSS_ITEMS = ["discovery", "schedule", "design", "reputation", "results", "performance",
               "request"]


@family(fill_in=True)
def punct_possessive(rng, difficulty):
    """Possessive apostrophes: singular, plural, irregular plural."""
    if difficulty == "easy":
        base, poss = rng.choice(_SING_NOUNS)
        kind = "singular"
    elif difficulty == "medium":
        base, poss = rng.choice(_SING_NOUNS + _PLUR_NOUNS)
        kind = "plural" if base.endswith("s") else "singular"
    else:
        base, poss = rng.choice(_PLUR_NOUNS + _IRREG_PLUR)
        kind = "irregular plural" if base in dict(_IRREG_PLUR) else "plural"
    frame = rng.choice(_POSS_FRAMES)
    item = frame.split("___ ")[1].split()[0]
    pre, post = frame.split(" ___ ")
    lead, _the = pre.replace(" {n}", "").rsplit(" ", 1) if " the {n}" in pre else ("", pre)
    det = rng.choice(_POSS_DET["singular" if kind == "singular" else "plural"])
    pre = f"{lead} {det}" if lead else cap(det)
    if kind == "singular":
        ds = [(f"{base}s", "A plain -s makes a plural, not a possessive."),
              (f"{base}s'", "This puts the apostrophe after a plural -s, but the owner is singular."),
              (f"{base}", "The plain noun does not show possession.")]
    elif kind == "plural":
        ds = [(f"{base[:-1]}'s", "This marks a single owner, but the owner here is plural."),
              (f"{base}'s", "Do not add 's to a plural that already ends in -s."),
              (f"{base}", "The plain plural does not show possession.")]
    else:
        ds = [(f"{base}s'", f"'{base}' is already plural; adding -s' is a double plural."),
              (f"{base}'", f"'{base}' does not end in -s, so it takes 's, not a bare apostrophe."),
              (f"{base}", "The plain noun does not show possession.")]
    correct = (poss, f"Correct. A {kind} noun shows possession with "
                     f"{'just an apostrophe after the -s' if kind == 'plural' else chr(39) + 's'}.")
    text = f"{pre} ___ {post}."
    return build(rng, fill(text, conv_stem(rng)), correct, ds, subskill="punctuation",
                 explanation=(f"The noun owns the {item}, so it needs a possessive form: "
                              f"'s for a singular (or irregular plural) noun, a bare apostrophe "
                              "after a plural -s."),
                 tags=["conventions", "punctuation", "possessive"])


_ITS = [
    ("The company announced that ___ profits had doubled", "poss"),
    ("The museum reopened ___ east wing after a two-year renovation", "poss"),
    ("The spacecraft adjusted ___ course as it approached the moon", "poss"),
    ("The orchestra tuned ___ instruments before the concert began", "poss"),
    ("The city repaved ___ oldest streets last summer", "poss"),
    ("The novel earned praise for ___ vivid descriptions of the coast", "poss"),
    ("The committee defended ___ decision at the public meeting", "poss"),
    ("The river changed ___ course after the flood", "poss"),
    ("The lab reported that ___ unlikely the samples were contaminated", "contr"),
    ("Residents say ___ been years since the fountain last worked", "contr"),
    ("The forecast suggests ___ going to rain all weekend", "contr"),
    ("Critics agree that ___ the director's most ambitious film", "contr"),
    ("The guide warned that ___ easy to lose the trail in fog", "contr"),
    ("Everyone knows ___ the first warm day of spring", "contr"),
]


@family(fill_in=True)
def punct_its(rng, difficulty):
    """its (possessive) vs. it's (it is / it has)."""
    text, kind = rng.choice(_ITS)
    if kind == "poss":
        correct = ("its", "Correct. The possessive 'its' has no apostrophe.")
        ds = [("it's", "'it's' means 'it is' or 'it has,' which makes no sense here."),
              ("its'", "'its'' is not a word."),
              ("their", "'their' is plural, but the owner is a singular noun.")]
        expl = "The pronoun shows ownership, so it is the possessive 'its' (no apostrophe)."
    else:
        correct = ("it's", "Correct. 'it's' is the contraction of 'it is' or 'it has.'")
        ds = [("its", "The possessive 'its' cannot replace 'it is' or 'it has.'"),
              ("its'", "'its'' is not a word."),
              ("it", "'it' alone leaves the clause without a verb.")]
        expl = "Read the sentence with 'it is' or 'it has' in the blank: it works, so 'it's' is correct."
    if difficulty != "easy":
        close = rng.choice(["The announcement surprised no one.", "Few people noticed at first.",
                            "The news spread quickly."])
        lead = rng.choice(["According to the latest newsletter, ", "As the report explains, ",
                           "By most accounts, "])
        text = lead + low(text)
        if difficulty == "hard":
            text = f"{text}. {close}"
            text = text.replace(". .", ".")
        else:
            text = f"{text}."
    else:
        text = f"{text}."
    return build(rng, fill(text, conv_stem(rng)), correct, ds, subskill="punctuation",
                 explanation=expl, tags=["conventions", "punctuation", "its-its"])


_APPOS = [
    ("The author", "a former journalist", "grew up in a fishing village"),
    ("The bridge", "the longest in the region", "closed for repairs last spring"),
    ("Priya Sen", "the lab's youngest researcher", "presented the findings"),
    ("The festival", "now in its twentieth year", "draws visitors from three states"),
    ("The violin", "made in 1721", "sold at auction for a record price"),
    ("Mount Harlan", "the tallest peak in the park", "is hidden by clouds most mornings"),
    ("The new library", "designed by a local firm", "opened to the public in May"),
    ("Coach Ruiz", "who retired last year", "returned to lead the final practice"),
    ("The recipe", "handed down from her grandmother", "calls for a pinch of nutmeg"),
    ("The mural", "painted by students in 1998", "was restored this summer"),
    ("The telescope", "the largest of its kind", "can detect planets around distant stars"),
    ("Theo Alvarez", "a second-year architecture student", "won the design competition"),
]


@family(fill_in=True)
def punct_nonrestrictive(rng, difficulty):
    """A nonessential appositive needs a matching pair of commas (or dashes)."""
    head, app, pred = rng.choice(_APPOS)
    style = "comma" if difficulty == "easy" else rng.choice(["comma", "dash"])
    if style == "comma":
        correct = (f", {app},", "Correct. A nonessential phrase is set off by a comma on each side.")
        ds = [(f", {app}", "The phrase needs a closing comma as well as an opening one."),
              (f" {app},", "The phrase needs an opening comma as well as a closing one."),
              (f", being {app},", "Adding 'being' is wordy and unidiomatic; the appositive "
                                   "stands on its own between commas.")]
    else:
        correct = (f" — {app} —", "Correct. A pair of dashes can set off a nonessential phrase, "
                                  "as long as both dashes are present.")
        ds = [(f" — {app},", "The punctuation must match on both sides: a dash cannot be "
                              "paired with a comma."),
              (f", {app} —", "The punctuation must match on both sides: a comma cannot be "
                              "paired with a dash."),
              (f" — being {app} —", "Adding 'being' is wordy and unidiomatic; the phrase "
                                     "stands on its own between the dashes.")]
    text = f"{head}___ {pred}."
    if difficulty == "hard":
        text = text + " " + rng.choice(["Few people know the story.", "The detail is easy to miss.",
                                        "Guides mention it on every tour."])
    return build(rng, fill(text, conv_stem(rng)), correct, ds, subskill="punctuation",
                 explanation=(f"'{app}' is extra information that could be lifted out, so it "
                              "is enclosed by a matched pair of commas or dashes."),
                 tags=["conventions", "punctuation", "nonrestrictive"], est=50)


_SERIES = [
    ("At the market Lena bought", ["apples", "fresh bread", "a jar of honey"], ""),
    ("The expedition carried", ["two tents", "a satellite phone", "a week of dried food"], ""),
    ("The course covers", ["grammar", "composition", "public speaking"], ""),
    ("The garden attracts", ["bees", "butterflies", "hummingbirds"], " all summer"),
    ("The museum's collection includes", ["maps", "ship models", "sailors' letters"], ""),
    ("Before the storm the crew", ["secured the sails", "checked the radio", "closed the hatches"], ""),
    ("For the recital Omar practiced", ["scales", "two sonatas", "a short piece of his own"], ""),
    ("The trail passes", ["a waterfall", "an old mill", "a stone chapel"], ""),
    ("The report recommends", ["smaller classes", "longer lunch periods", "a new gym"], ""),
    ("The documentary features", ["farmers", "fishermen", "lighthouse keepers"], " from the coast"),
    ("The workshop teaches", ["welding", "basic carpentry", "small-engine repair"], ""),
    ("The exhibit traces the history of", ["the harbor", "the cannery", "the ferry line"], ""),
    ("The hikers packed", ["a compass", "two liters of water", "an extra sweater"], ""),
    ("The playlist mixes", ["jazz", "folk ballads", "early electronic music"], ""),
    ("The clinic treats", ["sprains", "minor burns", "seasonal allergies"], ""),
    ("The grant funds", ["new microscopes", "summer internships", "a visiting lecturer"], ""),
    ("The ferry carries", ["cars", "bicycles", "the island's mail"], " every morning"),
    ("The archive preserves", ["letters", "ledgers", "hand-drawn maps"], ""),
    ("The bakery's shelves hold", ["rye loaves", "seeded rolls", "a single wheel of cheese"], ""),
    ("The clinic's staff includes", ["two nurses", "a dentist", "a visiting pediatrician"], ""),
]


@family(fill_in=True)
def punct_series(rng, difficulty):
    """Commas in a series of three (and the no-comma-before-the-first-item rule)."""
    lead, items, tail = rng.choice(_SERIES)
    a, b, c = items
    correct = (f"{a}, {b}, and {c}", "Correct. Items in a series are separated by commas, "
                                     "with 'and' before the last item.")
    ds = [(f"{a} {b} and {c}", "A series of three needs commas between the items."),
          (f"{a}, {b} and, {c}", "A comma never follows 'and' in a series."),
          (f"{a}, {b}, and, {c}", "No comma belongs after 'and' in a series.")]
    if difficulty != "easy":
        ds[0] = (f", {a}, {b}, and {c}", "No comma should separate the verb from the list that "
                                          "follows it.")
    if difficulty == "hard":
        ds[1] = (f"{a}; {b}; and {c}", "Semicolons separate list items only when the items "
                                       "themselves contain commas; plain items take commas.")
    text = f"{lead} ___{tail}."
    return build(rng, fill(text, conv_stem(rng)), correct, ds, subskill="punctuation",
                 explanation=("Separate the items of a simple series with commas; do not put a "
                              "comma before the first item or after 'and'."),
                 tags=["conventions", "punctuation", "series"])


_NO_COMMA = [
    ("The students who finished early", "left", "the hall quietly"),
    ("The researchers at the marine station", "measured", "the water temperature daily"),
    ("A sudden change in the wind", "pushed", "the sailboat toward the rocks"),
    ("The bakery on the corner", "sells", "pastries until noon"),
    ("The committee that reviewed the plan", "rejected", "its original budget"),
    ("Visitors to the observatory", "can see", "four planets on a clear night"),
    ("The engineers who designed the dam", "monitored", "its sensors around the clock"),
    ("The letters discovered in the attic", "describe", "life on the frontier"),
    ("The mural outside the station", "shows", "the town's founding families"),
    ("Everyone on the night shift", "praised", "the new schedule"),
    ("The sculptures along the waterfront", "attract", "photographers at sunset"),
    ("The first bus of the morning", "leaves", "the depot at five"),
    ("Whoever wins the raffle", "receives", "two tickets to the concert"),
    ("The apples from the upper orchard", "ripen", "a week earlier than the rest"),
    ("The old map in the lobby", "marks", "the location of the original well"),
    ("The violinist who joined last year", "performs", "the solo in the second movement"),
    ("The ferry that leaves at dawn", "carries", "the island's mail"),
    ("A thick fog over the harbor", "delayed", "the morning crossings"),
    ("The bakers on the early shift", "shape", "three hundred loaves before six"),
    ("The marker hidden in the tall grass", "dates", "from the first survey"),
]


@family(fill_in=True)
def punct_no_comma(rng, difficulty):
    """Unnecessary commas between subject and verb or verb and object."""
    subj, verb, obj = rng.choice(_NO_COMMA)
    correct = (f"{verb}", "Correct. No comma separates a subject from its verb or a verb "
                          "from its object.")
    ds = [(f", {verb}", "A comma must not separate the subject from its verb."),
          (f"{verb},", "A comma must not separate the verb from its object."),
          (f", {verb},", "Commas around the verb wrongly cut it off from both subject and object.")]
    if difficulty == "easy":
        text = f"{subj} ___ {obj}."
    elif difficulty == "medium":
        text = f"{subj} ___ {obj}, " + rng.choice(["and nobody objected", "which surprised no one",
                                                    "as planned"]) + "."
    else:
        lead = rng.choice(["Despite the forecast, ", "As the records show, ", "In the end, "])
        text = f"{lead}{low(subj)} ___ {obj}."
    return build(rng, fill(text, conv_stem(rng)), correct, ds, subskill="punctuation",
                 explanation=("Commas set off extra material; they never split the core of a "
                              "clause (subject–verb–object)."),
                 tags=["conventions", "punctuation", "unnecessary-comma"])


@family(fill_in=True, small_space=True)
def punct_passage(rng, difficulty):
    """Mini passage mixing possessives and its/it's with the blank mid-passage."""
    cases = [
        ("The city's oldest bakery sits at the end of Harbor Street.",
         "ovens, built in 1931, still work", "its", "Its",
         "Tourists line up outside before the doors open."),
        ("Many sea turtles return to the beach where they hatched.",
         "sense of direction depends on Earth's magnetic field", "turtle's", "A turtle's",
         "Researchers tag the females to track their journeys."),
        ("The school's robotics team meets in a converted woodshop.",
         "designs have won three regional titles", "students'", "The students'",
         "A fourth competition is scheduled for March."),
        ("The lighthouse was automated in 1987.",
         "lamp now switches on by itself at dusk", "its", "Its",
         "A keeper still lives on the island."),
        ("Three companies bid on the harbor contract.",
         "proposals were reviewed over the summer", "companies'", "The companies'",
         "The council chose the lowest bid."),
        ("The children planted a vegetable garden behind the library.",
         "beans climbed the fence by July", "children's", "The children's",
         "The harvest was donated to a food bank."),
        ("Mateo's grandmother taught him to carve wooden birds.",
         "tools now hang above his own workbench", "grandmother's", "His grandmother's",
         "He has carved more than two hundred birds."),
        ("The orchestra's spring tour visited six cities.",
         "final concert sold out in an hour", "orchestra's", "The orchestra's",
         "Recordings will be released next year."),
        ("The coastal trail reopened after a year of repairs.",
         "new footbridges were built by local carpenters", "trail's", "The trail's",
         "Hikers returned within days."),
        ("Two divers mapped the sunken ferry last summer.",
         "photographs were published in a regional magazine", "divers'", "The divers'",
         "A museum has asked to display them."),
        ("The weather station on the ridge has operated since 1952.",
         "instruments are checked every morning at six", "its", "Its",
         "Records from the station fill forty binders."),
        ("The women who founded the clinic were all nurses.",
         "names are carved above the entrance", "women's", "The women's",
         "A plaque inside tells their story."),
    ]
    lead, rest, poss, opener, close = rng.choice(cases)
    pre = opener[:-len(poss)] if opener.endswith(poss) else ""
    if poss == "its":
        c = cap if difficulty != "hard" else low
        correct = (c("its"), "Correct. The possessive 'its' takes no apostrophe.")
        ds = [(c("it's"), "'It's' means 'it is,' which does not fit."),
              (c("its'"), "'Its'' is not a word."),
              (c("their"), "'Their' is plural, but the owner is singular.")]
        pre = ""
    else:
        base = poss[:-1] if poss.endswith("s'") else poss[:-2]
        if poss.endswith("s'"):
            correct = (poss, "Correct. A plural noun ending in -s takes a bare apostrophe to show possession.")
            ds = [(f"{base[:-1]}'s", "This marks one owner, but the owner here is plural."),
                  (f"{base}'s", "Do not add 's to a plural that already ends in -s."),
                  (f"{base}", "The plain plural does not show possession.")]
        else:
            correct = (poss, "Correct. A singular noun shows possession with 's.")
            ds = [(f"{base}s", "A plain -s makes a plural, not a possessive."),
                  (f"{base}s'", "The apostrophe-after-s form is for plural owners."),
                  (f"{base}", "The plain noun does not show possession.")]
    mid = f"{pre}___ {rest}."
    if difficulty == "easy":
        text = f"{lead} {mid}"
    elif difficulty == "medium":
        text = f"{lead} {mid} {close}"
    else:
        filler = rng.choice([" As visitors soon learn, ", " Perhaps surprisingly, ", " As the staff like to point out, "])
        text = f"{lead}{filler}{low(mid) if not mid.startswith('___') else mid} {close}"
    return build(rng, fill(text, conv_stem(rng)), correct, ds, subskill="punctuation",
                 explanation=("Decide who owns what and whether the owner is singular or plural; "
                              "then place the apostrophe accordingly (and remember 'its' has none)."),
                 tags=["conventions", "punctuation", "passage"], est=55)


_DASH_PAIR = [
    ("The bridge", "built in 1902", "still carries traffic every day"),
    ("The novel", "her third in five years", "was finished in a rented cabin"),
    ("The reef", "once nearly lifeless", "now shelters dozens of fish species"),
    ("Our guide", "a retired geologist", "pointed out fossils in the cliff"),
    ("The engine", "rebuilt by volunteers", "started on the first try"),
    ("The mural", "forty feet long", "covers the entire north wall"),
    ("The festival", "now in its tenth year", "fills every hotel in town"),
    ("The telescope", "the largest in the hemisphere", "sits on a remote plateau"),
    ("The recipe", "handed down for four generations", "uses no sugar at all"),
    ("Her cousin", "a pilot for a regional airline", "flew in for the ceremony"),
    ("The orchard", "planted after the war", "still produces every autumn"),
    ("The tunnel", "nearly a mile long", "was dug entirely by hand"),
]


@family(fill_in=True)
def punct_paired(rng, difficulty):
    """Interrupting phrase: punctuation must match on both sides."""
    head, phrase, pred = rng.choice(_DASH_PAIR)
    kind = rng.choice(["comma", "dash", "paren"]) if difficulty != "easy" else "comma"
    opts = {"comma": (f", {phrase},", "a pair of commas"),
            "dash": (f" — {phrase} —", "a pair of dashes"),
            "paren": (f" ({phrase})", "parentheses")}
    ctext, label = opts[kind]
    correct = (ctext, f"Correct. {cap(label)} enclose the interrupting phrase, matching on both sides.")
    mism = [(f", {phrase} —", "A comma cannot be paired with a dash; the punctuation must match."),
            (f" — {phrase},", "A dash cannot be paired with a comma; the punctuation must match."),
            (f" ({phrase},", "A parenthesis cannot be closed with a comma."),
            (f", {phrase}", "The closing punctuation is missing, so the phrase runs into the verb."),
            (f" — {phrase}", "The closing dash is missing."),
            (f"; {phrase};", "Semicolons cannot enclose a phrase; they join independent clauses.")]
    rng.shuffle(mism)
    ds = [m for m in mism if m[0] != ctext][:2]
    ds.append((f", {phrase}, which", "Adding 'which' turns the rest of the sentence into a "
                                     "relative clause and leaves no main verb."))
    if difficulty == "hard":
        pred = pred + rng.choice([", much to everyone's relief", ", as the plaque explains",
                                  ", or so the story goes"])
    text = f"{head}___ {pred}."
    return build(rng, fill(text, conv_stem(rng)), correct, ds, subskill="punctuation",
                 explanation=("Whatever opens an interruption must also close it: two commas, "
                              "two dashes, or a pair of parentheses."),
                 tags=["conventions", "punctuation", "paired-punctuation"], est=50)


# =========================================================================== #
# PRONOUNS (case)
# =========================================================================== #
_PRON_SETS = {  # pronoun -> (subject, object, possessive, reflexive, label)
    "I": ("I", "me", "my", "myself"), "he": ("he", "him", "his", "himself"),
    "she": ("she", "her", "her", "herself"), "we": ("we", "us", "our", "ourselves"),
    "they": ("they", "them", "their", "themselves"),
}
_PRON_VERBS_OBJ = ["thanked", "invited", "called", "emailed", "congratulated", "interviewed",
                   "photographed", "reminded"]
_PRON_SUBJ_PAIRS = [("finished", "the survey"), ("presented", "the final report"),
                    ("organized", "the fundraiser"), ("led", "the cleanup"),
                    ("rehearsed", "the duet"), ("mapped", "the trail"),
                    ("planted", "the garden"), ("repaired", "the mural")]
_PRON_AGENTS = ["The coach", "The editor", "The mayor", "The curator", "The principal",
                "The judges", "The reporter", "The director"]
_PRON_TIMES = ["after the match", "before the ceremony", "at the end of the tour",
               "once the results were posted", "during the intermission"]


@family(fill_in=True)
def pron_compound(rng, difficulty):
    """Compound subjects/objects: test the pronoun alone to hear the case."""
    key = rng.choice(list(_PRON_SETS))
    subj, obj, poss, refl = _PRON_SETS[key]
    name = rng.choice(NAMES)
    role = rng.choice(["subject", "object"])
    if role == "object":
        agent = rng.choice(_PRON_AGENTS)
        verb = rng.choice(_PRON_VERBS_OBJ)
        time = rng.choice(_PRON_TIMES)
        order = rng.random() < 0.5
        pair = f"{name} and ___" if order else f"___ and {name}"
        text = f"{agent} {verb} {pair} {time}."
        correct = (obj, f"Correct. The pronoun is an object of '{verb},' so it takes the "
                        f"objective case '{obj}'. Test it alone: '{agent} {verb} {obj}.'")
        ds = [(subj, f"'{subj}' is subjective case; drop '{name}' and you would not say "
                     f"'{agent} {verb} {subj}.'"),
              (refl, "A reflexive pronoun needs the same person as the subject earlier in the clause."),
              (poss if poss != obj else "mine", "A possessive cannot be the object of the verb here.")]
        if poss == obj:
            ds[2] = ("hers" if key == "she" else "mine", "A possessive pronoun cannot be the object here.")
    else:
        verb, thing = rng.choice(_PRON_SUBJ_PAIRS)
        tail = rng.choice(["ahead of schedule", "over the weekend", "without any help",
                           "in record time"])
        text = f"{name} and ___ {verb} {thing} {tail}."
        correct = (subj, f"Correct. The pronoun is part of the subject, so it takes the "
                         f"subjective case '{subj}'. Test it alone: '{cap(subj)} {verb} {thing}.'")
        ds = [(obj, f"'{obj}' is objective case; you would not say '{cap(obj)} {verb} {thing}.'"),
              (refl, "A reflexive pronoun cannot serve as a subject."),
              (poss, f"'{poss}' is possessive and cannot act as the subject.")]
        if poss == obj:
            ds[2] = ("hers" if key == "she" else poss, "A possessive pronoun cannot act as the subject.")
    if difficulty != "easy":
        text = rng.choice(["According to the newsletter, ", "As everyone expected, ",
                           "To nobody's surprise, "]) + soft_low(text)
    if difficulty == "hard":
        text = text + " " + rng.choice(["The photograph ran in the paper the next day.",
                                        "Nobody mentioned it again.",
                                        "The story was retold for years."])
    return build(rng, fill(text, conv_stem(rng)), correct, ds, subskill="pronouns",
                 explanation=("Remove the other person from the compound and say the sentence "
                              "with the pronoun alone; the case that sounds right is the right one."),
                 tags=["conventions", "pronouns", "compound"])


_PERSONS = ["the scientist", "the author", "the candidate", "the musician", "the engineer",
            "the teacher", "the architect", "the journalist", "the volunteer", "the researcher",
            "the coach", "the director"]
_WHO_ACTS = ["designed the experiment", "wrote the report", "led the project", "won the award",
             "solved the puzzle", "organized the event", "restored the mural"]
_WHOM_ACTS = ["the committee selected", "the judges praised", "the editor hired",
              "the students admired", "the panel interviewed", "everyone trusted"]
_WHOSE_THINGS = ["first novel became a bestseller", "research changed the field",
                 "design won the competition", "voice carried across the hall",
                 "idea launched the company", "photographs toured the country"]
_WHO_FRAMES = ["The prize went to {p} ___ {a}.", "Reporters interviewed {p} ___ {a}.",
               "{P} ___ {a} spoke briefly at the ceremony.", "Few people know {p} ___ {a}."]


@family(fill_in=True)
def pron_who_whom(rng, difficulty):
    """who / whom / whose / which, chosen evenly so no wording tell appears."""
    person = rng.choice(_PERSONS)
    roll = rng.random()
    if difficulty == "easy":
        kinds = ["who", "whose", "which"]
    elif difficulty == "medium":
        kinds = ["who", "whom", "whose"]
    else:
        kinds = ["whom", "who", "whose", "whom_prep"]
    kind = rng.choice(kinds)
    frame = rng.choice(_WHO_FRAMES)
    if kind == "who":
        act = rng.choice(_WHO_ACTS)
        correct = ("who", "Correct. The pronoun is the subject of the verb that follows, so 'who' is required.")
        ds = [("whom", "'whom' is for objects; here the pronoun is the subject of the verb."),
              ("which", "'which' refers to things, not people."),
              ("whose", "'whose' is possessive and does not fit as the subject.")]
        expl = f"The pronoun does the action '{act}', so it is a subject: 'who'."
    elif kind == "whom":
        act = rng.choice(_WHOM_ACTS)
        correct = ("whom", "Correct. The pronoun is the object of the verb that follows, so 'whom' is required.")
        ds = [("who", "'who' is subjective; here the pronoun is the object of the verb."),
              ("which", "'which' refers to things, not people."),
              ("whose", "'whose' is possessive and does not fit as the object.")]
        expl = f"Rewrite the clause: '{act} him/her' — an object, so 'whom'."
    elif kind == "whom_prep":
        act = rng.choice(["the award was given", "the letter was addressed", "the lab was named",
                          "the team owed its success"])
        correct = ("to whom", "Correct. After a preposition the pronoun is an object: 'to whom'.")
        ds = [("to who", "'who' is subjective and cannot be the object of a preposition."),
              ("whom", "The preposition 'to' is needed to complete the idiom with the verb that follows."),
              ("to which", "'which' refers to things, not people.")]
        expl = "A pronoun that is the object of a preposition takes the objective case: 'to whom'."
    elif kind == "which":
        person = rng.choice(["the mural", "the bridge", "the novel", "the telescope", "the recipe"])
        act = rng.choice(["was finished last year", "took a decade to complete", "drew record crowds",
                          "won the design award"])
        correct = ("which", "Correct. 'which' refers to a thing.")
        ds = [("who", "'who' refers to people, not things."),
              ("whom", "'whom' refers to people, not things."),
              ("whose", "'whose' is possessive and does not fit here.")]
        expl = f"'{person}' is a thing, so the relative pronoun is 'which'."
    else:
        act = rng.choice(_WHOSE_THINGS)
        correct = ("whose", "Correct. The pronoun shows possession of the noun that follows, so 'whose' is required.")
        ds = [("who's", "'who's' means 'who is'; possession needs 'whose'."),
              ("who", "'who' is subjective and cannot show possession."),
              ("whom", "'whom' is objective and cannot show possession.")]
        expl = "The pronoun owns the noun after it, so the possessive 'whose' is needed."
    text = frame.format(p=person, P=cap(person), a=act)
    return build(rng, fill(text, conv_stem(rng)), correct, ds, subskill="pronouns",
                 explanation=expl, tags=["conventions", "pronouns", "relative"])


_PREP_FRAMES = [
    ("The invitation was addressed to {n} and ___", "to"),
    ("Just between you and ___, the plan has a flaw", "between"),
    ("The award will be shared among the finalists and ___", "among"),
    ("Everyone except {n} and ___ had already left", "except"),
    ("The manager saved the best seats for {n} and ___", "for"),
    ("Nobody besides {n} and ___ knew the combination", "besides"),
]


@family(fill_in=True)
def pron_preposition(rng, difficulty):
    """Objects of prepositions, including 'between you and me' and we/us + noun."""
    key = rng.choice(["I", "he", "she", "they", "we"])
    subj, obj, poss, refl = _PRON_SETS[key]
    name = rng.choice(NAMES)
    if difficulty == "hard" and rng.random() < 0.5:
        # we/us + noun appositive
        role = rng.choice(["subject", "object"])
        group = rng.choice(["volunteers", "students", "residents", "cyclists", "musicians"])
        if role == "subject":
            text = f"___ {group} finished the cleanup before noon."
            correct = ("We", f"Correct. Drop '{group}': 'We finished the cleanup.' The pronoun is the subject.")
            ds = [("Us", f"Drop '{group}' and 'Us finished' is clearly wrong; the subject needs 'We'."),
                  ("Ourselves", "A reflexive pronoun cannot be a subject."),
                  ("Our", "A possessive cannot be the subject of the sentence.")]
        else:
            text = f"The mayor thanked ___ {group} for finishing the cleanup before noon."
            correct = ("us", f"Correct. Drop '{group}': 'The mayor thanked us.' The pronoun is an object.")
            ds = [("we", f"Drop '{group}' and 'thanked we' is clearly wrong; an object needs 'us'."),
                  ("ourselves", "The subject is 'the mayor,' so a reflexive pronoun does not fit."),
                  ("our", "A possessive cannot be the object here.")]
        expl = "Say the sentence without the noun that follows the pronoun; the case that works is correct."
    else:
        frame, prep = rng.choice(_PREP_FRAMES)
        text = frame.format(n=name) + "."
        correct = (obj, f"Correct. The pronoun is an object of the preposition '{prep}', so it "
                        f"takes the objective case '{obj}'.")
        ds = [(subj, f"'{subj}' is subjective; a preposition's object needs the objective case."),
              (refl, "A reflexive pronoun is used only when the subject acts on itself."),
              (poss if poss != obj else ("hers" if key == "she" else "mine"),
               "A possessive cannot be the object of a preposition here.")]
        expl = (f"'{prep}' is a preposition, and every pronoun that follows it is an object: "
                f"'{prep} {name} and {obj}'.")
        if difficulty != "easy":
            text = rng.choice(["As it turned out, ", "In the end, ", "Strangely enough, "]) + low(text)
    return build(rng, fill(text, conv_stem(rng)), correct, ds, subskill="pronouns",
                 explanation=expl, tags=["conventions", "pronouns", "preposition"])


# Reflexive frames spell out that the subject acts on itself (no teacher, alone,
# "{P} own" mistake): with a bare "{N} taught ___ to read music", the object
# "him"/"her" (someone else) was just as grammatical as "himself"/"herself".
_REFL = [
    ("With no teacher in town, {N} taught ___ to read music from library books", True),
    ("Since the missed step had been {P} own mistake, {N} blamed ___ for the delay", True),
    ("Having met the deadline on {P} own, {N} treated ___ to a day off", True),
    ("Alone backstage, {N} quietly reminded ___ to breathe before the speech", True),
    ("Please send the revised forms to {N} or ___", False),
    ("The committee invited {N} and ___ to present the plan", False),
    ("The tickets were reserved for {N} and ___", False),
    ("Questions should be directed to {N} or ___", False),
]


@family(fill_in=True)
def pron_reflexive(rng, difficulty):
    """Reflexive pronouns only when the subject acts on itself; 'myself' is not a polite 'me'."""
    frame, needs_refl = rng.choice(_REFL)
    name = rng.choice(NAMES)
    s, o, p, r = pron(name)
    if needs_refl:
        correct = (r, f"Correct. {name} is both the subject and the object, so the reflexive "
                      f"'{r}' is required.")
        ds = [(o, f"'{o}' would refer to a different person; the subject acts on {r}."),
              (s, f"'{s}' is subjective case and cannot be the object."),
              (f"{s} {r}", f"'{s}' is subjective, and doubling the pronoun is ungrammatical here.")]
        expl = "When the subject and the object are the same person, use the reflexive pronoun."
    else:
        correct = ("me", "Correct. The pronoun is an object, so 'me' is needed; a reflexive "
                         "pronoun requires 'I' as the subject of the clause.")
        ds = [("myself", "'myself' is reflexive and needs 'I' as the subject earlier in the clause; "
                         "it is not a formal substitute for 'me'."),
              ("I", "'I' is subjective, but the pronoun here is an object."),
              ("my", "A possessive cannot stand alone as an object here.")]
        expl = ("A reflexive pronoun reflects the subject; when the subject is someone else, "
                "the plain object form 'me' is correct.")
    text = frame.format(N=name, P=p) + "."
    if difficulty != "easy" and not needs_refl:
        text = rng.choice(["Before the recital, ", "After the vote, ", "That winter, "]) + soft_low(text)
    if difficulty == "hard":
        text = text + " " + rng.choice(["It made a surprising difference.", "No one argued.",
                                        "The change was permanent."])
    return build(rng, fill(text, conv_stem(rng)), correct, ds, subskill="pronouns",
                 explanation=expl, tags=["conventions", "pronouns", "reflexive"])


_PRON_PASS = [
    ("Lena and her brother run a small bookshop near the station.",
     "Customers often ask {X} and ___ for recommendations", "object", "Lena",
     "Both of them are happy to oblige."),
    ("The debate team traveled to the state finals in April.",
     "The coach praised Omar and ___ for the closing argument", "object", "Omar",
     "The trophy now sits in the school lobby."),
    ("Priya and Diego restored a 1950s radio over the winter.",
     "By March, Diego and ___ had it playing again", "subject", "Diego",
     "They sold it at the spring fair."),
    ("Theo organizes the neighborhood cleanup every spring.",
     "This year, Theo and ___ collected forty bags of litter", "subject", "Theo",
     "The city sent a thank-you note."),
    ("Two students, Hana and Felix, mapped every tree on campus.",
     "The dean invited Hana and ___ to present the map to the trustees", "object", "Hana",
     "The map is now posted at the main gate."),
    ("Nadia and I entered the robotics contest as a team of two.",
     "In the final round, Nadia and ___ repaired a broken sensor in under a minute", "subject", "Nadia",
     "We finished third."),
]


@family(fill_in=True)
def pron_passage(rng, difficulty):
    """Mini passage: the pronoun's case depends on the middle sentence's structure."""
    lead, mid, role, partner, close = rng.choice(_PRON_PASS)
    key = rng.choice(["I", "he", "she", "we", "they"])
    if "I " in lead or "Nadia and I" in lead:
        key = "I"
    subj, obj, poss, refl = _PRON_SETS[key]
    if role == "subject":
        correct = (subj, f"Correct. '{partner} and ___' is the subject of the sentence, so the "
                         f"subjective case '{subj}' is needed.")
        ds = [(obj, f"'{obj}' is objective; test it alone: '{cap(obj)} had it playing' sounds wrong."),
              (refl, "A reflexive pronoun cannot be part of a subject."),
              (poss if poss != obj else ("hers" if key == "she" else "mine"),
               "A possessive cannot act as the subject.")]
    else:
        correct = (obj, f"Correct. '{partner} and ___' is an object of the verb, so the objective "
                        f"case '{obj}' is needed.")
        ds = [(subj, f"'{subj}' is subjective; test it alone and the sentence would read "
                     f"'...{subj}', which is wrong."),
              (refl, "A reflexive pronoun needs the same person as the subject of the clause."),
              (poss if poss != obj else ("hers" if key == "she" else "mine"),
               "A possessive cannot be the object here.")]
    mid_s = mid.format(X=partner) + "."
    if difficulty == "easy":
        text = f"{lead} {mid_s}"
    else:
        text = f"{lead} {mid_s} {close}"
    if difficulty == "hard":
        text = text.replace(mid_s, rng.choice(["Not surprisingly, ", "As the local paper reported, ",
                                               "By all accounts, "]) + soft_low(mid_s))
    return build(rng, fill(text, conv_stem(rng)), correct, ds, subskill="pronouns",
                 explanation=("Find the pronoun's job in its own sentence (subject or object) and "
                              "choose the matching case; test by dropping the other name."),
                 tags=["conventions", "pronouns", "passage"], est=55)


@family(fill_in=True)
def pron_clause_options(rng, difficulty):
    """Whole relative clauses as options (who/whom inside a longer clause)."""
    person = rng.choice(_PERSONS)
    name = rng.choice(NAMES)
    if rng.random() < 0.5:
        act = rng.choice(_WHO_ACTS)
        correct = (f"who {act}", "Correct. 'who' is the subject of the verb in the clause.")
        ds = [(f"whom {act}", "'whom' is objective, but the pronoun is doing the action."),
              (f"which {act}", "'which' cannot refer to a person."),
              (f"whose {act}", "'whose' is possessive and leaves the clause without a subject.")]
    else:
        act = rng.choice(_WHOM_ACTS)
        correct = (f"whom {act}", "Correct. The pronoun is the object of the clause's verb, so 'whom'.")
        ds = [(f"who {act}", "'who' is subjective, but the clause already has a subject; the pronoun is its object."),
              (f"which {act}", "'which' cannot refer to a person."),
              (f"that {act}, whom", "This doubles the relative pronoun and makes the clause ungrammatical.")]
    frames = [f"{name} introduced {person} ___.", f"Everyone wanted to meet {person} ___.",
              f"The documentary profiles {person} ___."]
    text = rng.choice(frames)
    if difficulty == "hard":
        text = text.replace(" ___", ", a longtime friend of the family, ___")
    return build(rng, fill(text, conv_stem(rng)), correct, ds, subskill="pronouns",
                 explanation=("Look inside the relative clause: if the pronoun performs the verb, "
                              "use 'who'; if it receives the action, use 'whom'."),
                 tags=["conventions", "pronouns", "clause-options"], est=50)


# =========================================================================== #
# MODIFIERS
# =========================================================================== #
# (opening modifier, correct noun, wrong noun 1, wrong noun 2, wrong noun 3,
#  predicate, lead sentence, closing sentence)
_MODIFIERS = [
    ("Walking through the old town,", "the travelers", "the cobblestones", "the photographs", "the afternoon",
     "admired the architecture", "The tour began at the harbor gate.", "They reached the cathedral by dusk."),
    ("Built more than a century ago,", "the bridge", "the engineers", "the traffic", "the commuters",
     "still carries thousands of cars each day", "The river has three crossings.", "Inspectors check it every spring."),
    ("Having studied all night,", "Maya", "the exam", "the results", "the room",
     "felt ready for the exam", "The chemistry final was scheduled for eight.", "She finished with ten minutes to spare."),
    ("Painted a bright shade of blue,", "the house", "the painter", "the neighbors", "the weather",
     "stood out on the quiet street", "Every other home on the block was white.", "Visitors used it as a landmark."),
    ("After finishing the marathon,", "the runner", "the medal", "the crowd", "the route",
     "could barely stand", "The course climbed two long hills.", "A volunteer handed him water."),
    ("Hidden beneath layers of dust,", "the manuscript", "the librarian", "the shelves", "the search",
     "had gone unread for decades", "The library's basement held forgotten boxes.", "It is now on display upstairs."),
    ("Excited about the discovery,", "the scientists", "the data", "the equipment", "the announcement",
     "published their findings at once", "The sensor had recorded an unexpected signal.", "Other labs rushed to confirm it."),
    ("Carefully wrapped in paper,", "the gift", "the child", "the table", "the party",
     "sat waiting on the table", "The birthday party started at noon.", "Nobody guessed what was inside."),
    ("Running low on fuel,", "the pilot", "the runway", "the storm", "the cargo",
     "decided to land early", "The flight had been diverted around a storm.", "The passengers never noticed."),
    ("Translated into a dozen languages,", "the novel", "the author", "the readers", "the prize",
     "reached readers worldwide", "The book was first printed in a run of five hundred.", "It has never gone out of print."),
    ("Worried about the deadline,", "the editor", "the article", "the printing press", "the office",
     "worked late into the night", "The magazine goes to press on Thursdays.", "The issue shipped on time."),
    ("Frozen solid overnight,", "the lake", "the skaters", "the town", "the morning",
     "was safe to walk across", "A cold front arrived in late December.", "Children were skating by noon."),
    ("Trained for years in the studio,", "the dancer", "the routine", "the audience", "the stage",
     "moved with effortless grace", "The company's new season opened in May.", "Critics singled her out."),
    ("Buried in the garden for centuries,", "the coins", "the gardener", "the museum", "the discovery",
     "gleamed when finally unearthed", "A gardener was digging a new bed.", "The coins now belong to the museum."),
    ("Eager to begin,", "the students", "the lesson", "the bell", "the classroom",
     "raced into the room", "The first day of the robotics course had arrived.", "The teacher could barely keep up."),
    ("Damaged by the flood,", "the records", "the clerk", "the weather report", "the summer",
     "had to be carefully restored", "Water rose two feet in the archive.", "The work took eighteen months."),
    ("Covered in fresh snow,", "the field", "the children", "the morning", "the forecast",
     "looked completely transformed", "The storm ended just before dawn.", "By noon the snow had melted."),
    ("Sealed for a hundred years,", "the letter", "the historian", "the mail carrier", "the family",
     "revealed a forgotten secret", "The envelope was found in an attic trunk.", "The family had never heard the story."),
    ("Startled by the noise,", "the deer", "the trail", "the forest", "the silence",
     "bolted into the trees", "A branch snapped on the trail.", "The hikers waited quietly for a minute."),
    ("Printed in bold letters,", "the headline", "the editor", "the readers", "the morning",
     "caught every reader's eye", "The paper's front page was redesigned.", "Sales rose that week."),
    ("Exhausted after the climb,", "the team", "the summit", "the gear", "the weather",
     "rested at the summit", "The ascent took eleven hours.", "They descended the next morning."),
    ("Polished to a shine,", "the trophy", "the winner", "the speech", "the ceremony",
     "gleamed under the lights", "The awards dinner was held in the gym.", "It now sits in the lobby case."),
    ("Lost in thought,", "the writer", "the deadline", "the office", "the afternoon",
     "barely noticed the time", "The chapter had stalled for days.", "She finished it that night."),
    ("Wrapped in fog,", "the harbor", "the weather report", "the noise", "the dawn",
     "was almost invisible at dawn", "A thick fog settled overnight.", "The ferries ran late all morning."),
]
_MOD_STEM = ("Which choice completes the sentence so that the introductory phrase modifies "
             "the correct noun?")


def _possessive(np_):
    return np_ + ("'" if np_.endswith("s") else "'s")


@family(fill_in=False, small_space=True)
def mod_whole_sentence(rng, difficulty):
    """Whole-sentence options; the subject after the modifier changes."""
    mod, right, w1, w2, w3, pred, lead, close = rng.choice(_MODIFIERS)
    correct = (f"{mod} {right} {pred}.", f"Correct. The modifier '{mod[:-1]}' logically describes "
                                         f"'{right}', which directly follows it.")
    ds = [(f"{mod} {w1} {pred}.", f"Dangling modifier: '{mod[:-1]}' cannot logically describe '{w1}'."),
          (f"{mod} {w2} {pred}.", f"The opening phrase does not sensibly modify '{w2}'."),
          (f"{mod} {w3} {pred}.", f"The opening phrase does not sensibly modify '{w3}'.")]
    if difficulty == "hard" or (difficulty == "easy" and rng.random() < 0.5):
        ds[2] = (f"{mod} {_possessive(right)} {w2.split()[-1]} {pred}.",
                 f"The modifier must describe '{right}', not something that belongs to them.")
    prompt = rng.choice([_MOD_STEM, "Which choice places the noun that the opening phrase describes "
                                    "directly after that phrase?"]) if difficulty == "easy" else (
        f"{lead}\n\nWhich choice gives the sentence that should come next, so that its "
        "introductory phrase modifies the correct noun?")
    return build(rng, prompt, correct, ds, subskill="modifiers",
                 explanation=("An introductory modifier must be immediately followed by the noun "
                              "it describes; otherwise it 'dangles.'"),
                 tags=["conventions", "modifiers"], est=50)


@family(fill_in=True)
def mod_blank_subject(rng, difficulty):
    """The blank is the subject right after the modifier; options are nouns."""
    mod, right, w1, w2, w3, pred, lead, close = rng.choice(_MODIFIERS)
    correct = (right, f"Correct. '{mod[:-1]}' describes '{right}', so that noun must come right after the phrase.")
    ds = [(w1, f"'{mod[:-1]}' cannot describe '{w1}'; the modifier would dangle."),
          (w2, f"The opening phrase does not sensibly describe '{w2}'."),
          (w3, f"The opening phrase does not sensibly describe '{w3}'.")]
    if difficulty != "easy":
        ds[1] = (f"{_possessive(right)} {w2.split()[-1]}",
                 f"The modifier describes '{right}', not something belonging to them; the "
                 "possessive makes the wrong noun the subject.")
    if difficulty == "hard":
        ds[2] = (f"it was {right} who", "This rewrites the clause so that 'it' follows the "
                                        "modifier, leaving the phrase dangling.")
    text = f"{mod} ___ {pred}."
    if difficulty == "medium" or (difficulty == "easy" and rng.random() < 0.5):
        text = f"{lead} {text}"
    elif difficulty == "hard":
        text = f"{lead} {text} {close}"
    if difficulty == "easy" and rng.random() < 0.5:
        ds[2] = (f"{_possessive(right)} {w3.split()[-1]}",
                 f"The possessive makes '{w3.split()[-1]}' the subject, which the modifier does not describe.")
    return build(rng, fill(text, conv_stem(rng)), correct, ds, subskill="modifiers",
                 explanation=(f"Ask who or what '{mod[:-1]}' describes: '{right}'. That noun must "
                              "immediately follow the opening phrase."),
                 tags=["conventions", "modifiers", "blank-subject"], est=50)


# (correct opening phrase, dangling 1, dangling 2, splice/awkward, rest of sentence)
_MOD_OPENINGS = [
    ("Built more than a century ago", "Having built it more than a century ago",
     "Being more than a century old by its builders", "Engineers built it more than a century ago",
     "the bridge still carries thousands of cars each day"),
    ("Hoping to finish before dark", "To be finished before dark",
     "With the hope of it being finished before dark by them", "The crew hoped to finish before dark",
     "the crew skipped its afternoon break"),
    ("Exhausted after the climb", "After the exhausting climb was over for them",
     "Being that the climb was exhausting", "The climb exhausted them",
     "the hikers rested at the summit"),
    ("Written in a single week", "Having written it in a single week",
     "Taking only a single week by its author", "The author wrote it in a single week",
     "the novel reads like a long letter"),
    ("Delayed by fog", "Because of being foggy that morning",
     "With fog delaying them that morning", "Fog delayed them",
     "the ferries ran two hours late"),
    ("Trained as a chemist", "With her training as a chemist complete",
     "Being trained as a chemist by her teachers", "She was trained as a chemist",
     "Rosa approached cooking like a laboratory experiment"),
    ("Unsure of the route", "The route being uncertain to him",
     "Without being sure what the route was to him", "He was unsure of the route",
     "Samir stopped to check the map"),
    ("Restored by volunteers", "After volunteers had restored it over the summer",
     "With its restoration by volunteers over the summer", "Volunteers restored it over the summer",
     "the old carousel reopened in June"),
    ("Startled by the thunder", "When the thunder startled them",
     "Being that the thunder was startling", "The thunder startled them",
     "the horses bolted across the field"),
    ("Discovered in a flea market", "Having discovered it in a flea market",
     "Being found by a collector in a flea market", "A collector discovered it in a flea market",
     "the painting turned out to be worth a fortune"),
    ("Raised on a farm", "With a farm upbringing behind her",
     "Being that she was raised on a farm", "She was raised on a farm",
     "Imani was comfortable around large animals"),
    ("Hidden behind a false wall", "Because the wall was false and hid it",
     "With a false wall hiding it for decades", "A false wall hid it for decades",
     "the staircase went unnoticed for decades"),
]


@family(fill_in=True)
def mod_opening_phrase(rng, difficulty):
    """Options are the opening phrase itself; only one fits the subject that follows."""
    good, d1, d2, splice, rest = rng.choice(_MOD_OPENINGS)
    subj = " ".join(rest.split()[:2]) if rest.startswith("the ") else rest.split()[0]
    correct = (good, f"Correct. '{good}' describes '{subj}', the noun that follows the comma.")
    ds = [(d1, f"This phrase does not describe '{subj}'; it dangles."),
          (d2, "This version is wordy and still fails to modify the subject that follows."),
          (splice, "This is an independent clause, so a comma alone creates a comma splice.")]
    if difficulty == "easy":
        ds = ds[:2] + [(splice, ds[2][1])]
    text = f"___, {rest}."
    if difficulty == "hard":
        text = rng.choice(["Few visitors know the story. ", "The guidebook tells the story briefly. ",
                           "The details are worth knowing. "]) + text
    return build(rng, fill(text, conv_stem(rng)), correct, ds, subskill="modifiers",
                 explanation=(f"The phrase before the comma must describe the subject that follows "
                              f"it ('{subj}'), and it must be a phrase, not a complete clause."),
                 tags=["conventions", "modifiers", "opening-phrase"], est=50)


# (correct sentence, misplaced 1, misplaced 2, misplaced 3)
_MOD_MISPLACED = [
    ("The chef served the guests a cake covered in chocolate.",
     "The chef served the guests covered in chocolate a cake.",
     "Covered in chocolate, the chef served the guests a cake.",
     "The chef, covered in chocolate, served the guests a cake."),
    ("Wearing a bright scarf, the guide led the group through the market.",
     "The guide led the group through the market wearing a bright scarf.",
     "The guide led the group wearing a bright scarf through the market.",
     "Wearing a bright scarf, the market was where the guide led the group."),
    ("The librarian found a letter written in 1880 inside the atlas.",
     "The librarian, written in 1880, found a letter inside the atlas.",
     "Written in 1880, the librarian found a letter inside the atlas.",
     "The librarian found a letter inside the atlas written in 1880."),
    ("Tessa sold the bicycle with the flat tire to a neighbor.",
     "Tessa sold the bicycle to a neighbor with the flat tire.",
     "With the flat tire, Tessa sold the bicycle to a neighbor.",
     "Tessa, with the flat tire, sold the bicycle to a neighbor."),
    ("The museum displayed a vase that was nearly three thousand years old.",
     "The museum, nearly three thousand years old, displayed a vase.",
     "Nearly three thousand years old, the museum displayed a vase.",
     "The museum displayed, nearly three thousand years old, a vase."),
    ("The farmer sold the tractor, which no longer ran, for scrap.",
     "The farmer, which no longer ran, sold the tractor for scrap.",
     "No longer running, the farmer sold the tractor for scrap.",
     "The farmer sold the tractor for scrap, which no longer ran."),
    ("Humming softly, Chloe finished the painting in a single afternoon.",
     "Chloe finished the painting humming softly in a single afternoon.",
     "Chloe finished the painting in a single afternoon, which was humming softly.",
     "Humming softly, the painting was finished by Chloe in a single afternoon."),
    ("The guide showed us a cave with ancient drawings on its walls.",
     "With ancient drawings on its walls, the guide showed us a cave.",
     "The guide, with ancient drawings on its walls, showed us a cave.",
     "The guide showed us, with ancient drawings on its walls, a cave."),
    ("Ravi photographed a heron standing in the shallow water.",
     "Standing in the shallow water, Ravi's camera captured a heron from the bridge above.",
     "Ravi, standing on the bridge above, photographed a heron in the shallow water that was standing.",
     "Ravi photographed, standing in the shallow water, a heron from the bridge above."),
    ("Nina gave the puppy that had been shivering a warm blanket.",
     "Nina gave the puppy a warm blanket that had been shivering.",
     "Shivering, a warm blanket was given to the puppy by Nina.",
     "Nina gave, that had been shivering, the puppy a warm blanket."),
    ("Covered in frost, the windshield took Diego ten minutes to clear.",
     "Covered in frost, Diego took ten minutes to clear the windshield.",
     "Diego, covered in frost, took ten minutes to clear the windshield.",
     "Covered in frost, ten minutes were needed by Diego to clear the windshield."),
    ("The students handed the teacher essays stapled at the corner.",
     "The students handed the teacher stapled at the corner essays.",
     "Stapled at the corner, the students handed the teacher essays.",
     "The students, stapled at the corner, handed the teacher essays."),
]


@family(fill_in=False, small_space=True)
def mod_misplaced(rng, difficulty):
    """Misplaced modifiers inside the sentence; options are whole sentences."""
    good, m1, m2, m3 = rng.choice(_MOD_MISPLACED)
    correct = (good, "Correct. Every modifier sits next to the word it describes.")
    ds = [(m1, "A modifier is separated from the word it describes, so the sentence says "
               "something illogical."),
          (m2, "The modifying phrase attaches to the wrong noun."),
          (m3, "The placement of the modifier makes the meaning absurd or unclear.")]
    stem = rng.choice(["Which choice places every modifier so that the sentence's meaning is clear?",
                       "In which choice is the sentence free of misplaced modifiers?"])
    if difficulty == "easy":
        ds = ds[:2] + [(m3, ds[2][1])]
    return build(rng, stem, correct, ds, subskill="modifiers",
                 explanation=("Place each descriptive phrase directly beside the word it "
                              "describes; a phrase that drifts attaches to the wrong noun."),
                 tags=["conventions", "modifiers", "misplaced"], est=55)


@family(fill_in=True)
def mod_passage(rng, difficulty):
    """Three-sentence passage; the dangling-modifier blank is in the middle."""
    mod, right, w1, w2, w3, pred, lead, close = rng.choice(_MODIFIERS)
    correct = (f"{right} {pred}", f"Correct. '{mod[:-1]}' describes '{right}', which follows it directly.")
    ds = [(f"{w1} {pred}", f"'{mod[:-1]}' cannot describe '{w1}'; the modifier dangles."),
          (f"{_possessive(right)} {w2.split()[-1]} {pred}",
           f"The possessive makes '{w2.split()[-1]}' the subject, which the modifier does not describe."),
          (f"there was {right} that {pred}", "Beginning with 'there was' leaves the modifier with "
                                            "nothing sensible to describe.")]
    if difficulty == "easy":
        ds[1] = (f"{w2} {pred}", f"The opening phrase does not sensibly describe '{w2}'.")
        ds[2] = (f"{w3} {pred}", f"The opening phrase does not sensibly describe '{w3}'.")
    text = f"{lead} {mod} ___. {close}" if not (difficulty == "easy" and rng.random() < 0.5) else f"{lead} {mod} ___."
    return build(rng, fill(text, conv_stem(rng)), correct, ds, subskill="modifiers",
                 explanation=("Read the opening phrase and ask who or what it describes; that noun "
                              "must be the subject that comes right after the comma."),
                 tags=["conventions", "modifiers", "passage"], est=55)


# =========================================================================== #
# TRANSITIONS
# =========================================================================== #
_TRANS_BANK = {
    "contrast": ["However", "Nevertheless", "By contrast", "On the other hand", "Still",
                 "Even so", "In spite of this"],
    "cause": ["Therefore", "As a result", "Consequently", "Thus", "For this reason", "Hence"],
    "addition": ["Moreover", "In addition", "Furthermore", "Additionally", "What is more"],
    "example": ["For example", "For instance", "To illustrate", "Specifically"],
    "sequence": ["Subsequently", "Later", "Afterward", "Next", "Soon after"],
    "emphasis": ["Indeed", "In fact", "Above all"],
}
_TRANS_ITEMS = [
    ("The new policy promised faster service.", "wait times actually grew longer in the first month.", "contrast"),
    ("Sea otters eat large numbers of sea urchins.", "kelp forests thrive where otters are present.", "cause"),
    ("The biography is meticulously researched.", "it is written in lively, accessible prose.", "addition"),
    ("Some metals expand significantly when heated.", "bridges are built with expansion joints.", "cause"),
    ("Many songbirds navigate using the stars.", "some species also sense the Earth's magnetic field.", "addition"),
    ("The committee expected the plan to save money.", "costs rose in the first quarter.", "contrast"),
    ("The recipe calls for very ripe bananas.", "the loaf turns out moist and naturally sweet.", "cause"),
    ("Renewable energy use has grown quickly.", "wind power capacity tripled in a decade.", "example"),
    ("The museum lacked space for its collection.", "it opened a second gallery downtown.", "cause"),
    ("The team practiced the play for weeks.", "they executed it perfectly in the final.", "cause"),
    ("Most planets in the system are rocky.", "the outermost one is a gas giant.", "contrast"),
    ("The volunteers cleared the trail of debris.", "they repaired the wooden footbridge.", "sequence"),
    ("The argument seemed convincing at first.", "it rested on a single, untested assumption.", "contrast"),
    ("Bees are vital pollinators for many crops.", "their populations have declined sharply.", "contrast"),
    ("The startup struggled to find customers early on.", "it became profitable within three years.", "contrast"),
    ("The novel explores themes of memory.", "it examines how stories shape identity.", "addition"),
    ("The drought reduced the harvest.", "food prices climbed across the region.", "cause"),
    ("Glass can be recycled almost indefinitely.", "recycling rates remain surprisingly low.", "contrast"),
    ("The professor outlined the theory in the first half of the lecture.", "she spent the second half demonstrating it with a simple experiment.", "sequence"),
    ("The bridge was closed for repairs.", "commuters had to take a long detour.", "cause"),
    ("Many readers found the ending abrupt.", "the author defended it as intentional.", "contrast"),
    ("The city installed hundreds of new bike lanes.", "cycling rose by nearly forty percent.", "cause"),
    ("The data supported the first hypothesis.", "it cast doubt on the second.", "contrast"),
    ("The species looks fragile.", "it survives in some of the harshest deserts.", "contrast"),
    ("The factory switched to solar power.", "its emissions fell dramatically.", "cause"),
    ("The lecture covered the basics of the method.", "the class moved to the lab to try it out.", "sequence"),
    ("The trail offers stunning views.", "it passes three historic landmarks.", "addition"),
    ("Critics praised the film's visuals.", "they found the plot thin.", "contrast"),
    ("The report identified several risks.", "it also listed the agencies responsible for each one.", "addition"),
    ("The bakery doubled its staff.", "lines at the counter grew even longer.", "contrast"),
    ("The heat wave bleached most of the reef's coral.", "dive shops that depended on the reef lost much of their business.", "cause"),
    ("The app is simple to use.", "it is free for students.", "addition"),
    ("The river rose above its banks.", "nearby roads were closed for days.", "cause"),
    ("The theory explained the early results.", "it failed to predict the later ones.", "contrast"),
    ("The farmers sowed the wheat in early spring.", "they harvested it in late summer.", "sequence"),
    ("The lecture was dense and technical.", "the audience followed it closely.", "contrast"),
    ("The vaccine reached remote villages.", "infection rates there dropped sharply.", "cause"),
    ("The museum is free to enter.", "it relies entirely on donations.", "cause"),
    ("The hikers underestimated the trail.", "they reached the peak hours late.", "cause"),
    ("The author writes for adults.", "her latest book delights children too.", "contrast"),
    ("The factory cut its water use.", "it also lowered its electricity bills.", "addition"),
    ("The plan looked promising on paper.", "it collapsed at the first real test.", "contrast"),
    ("The choir warmed up backstage.", "they walked out to perform.", "sequence"),
]
# Relations whose transitions are safe WRONG answers for an item keyed to the
# given relation. Neighbouring relations are left out on purpose: a "cause"
# item usually also reads as a time sequence ("The drought withered the corn.
# Later, yields fell") and an "addition" item as emphasis or an example, so
# offering those made two choices defensible (answer-key audit, phase 3).
# Nothing is keyed "emphasis": "Indeed"/"In fact" fit too many additions.
_TRANS_DISTRACTOR_RELS = {
    "contrast": ["addition", "cause", "emphasis", "example"],
    "cause": ["contrast", "example"],
    "addition": ["contrast", "sequence"],
    "example": ["contrast", "sequence"],
    "sequence": ["contrast", "example"],
}
_TRANS_REL_NAMES = {
    "contrast": "a contrast", "cause": "a cause-and-effect relationship",
    "addition": "an additional, similar idea", "example": "an example",
    "sequence": "a sequence of events", "emphasis": "emphasis",
}
_TRANS_STEMS = [
    "Which transition best fits the relationship between the two ideas?",
    "Which choice completes the text with the most logical transition?",
    "Which transition most logically connects the two sentences?",
]


def _trans_distractors(rng, rel, difficulty, used, fmt=lambda w: w, n=3):
    """``n`` wrong transitions for an item keyed to ``rel``, drawn only from
    relations that cannot also fit (see ``_TRANS_DISTRACTOR_RELS``). Each
    allowed relation is used once before any repeats; on hard items the first
    listed (most tempting) relation leads."""
    allowed = list(_TRANS_DISTRACTOR_RELS[rel])
    if difficulty != "hard":
        rng.shuffle(allowed)
    ds = []
    while len(ds) < n:
        progressed = False
        for r in allowed:
            if len(ds) == n:
                break
            choices = [w for w in _TRANS_BANK[r] if w.lower() not in used]
            if not choices:
                continue
            w = rng.choice(choices)
            used.add(w.lower())
            progressed = True
            ds.append((fmt(w), f"This signals {_TRANS_REL_NAMES[r]}, but the sentences need "
                               f"{_TRANS_REL_NAMES[rel]}."))
        if not progressed:
            break
    return ds


@family(fill_in=True)
def trans_blank(rng, difficulty):
    """'<S1>. ___, <S2>' with single-word/phrase transitions."""
    s1, s2, rel = rng.choice(_TRANS_ITEMS)
    word = rng.choice(_TRANS_BANK[rel])
    used = {word.lower()}
    ds = _trans_distractors(rng, rel, difficulty, used)
    correct = (word, f"Correct. The link between the ideas is {_TRANS_REL_NAMES[rel]}.")
    text = f"{s1} ___, {s2}"
    return build(rng, fill(text, rng.choice(_TRANS_STEMS)), correct, ds,
                 subskill="logical_transitions", qtype="multiple_choice",
                 explanation=(f"The second idea expresses {_TRANS_REL_NAMES[rel]} relative to the "
                              f"first, so a {rel}-signaling transition is needed."),
                 tags=["expression", "transitions"], est=50)


@family(fill_in=True)
def trans_opener(rng, difficulty):
    """Options carry their comma ('However,'); blank opens the second sentence."""
    s1, s2, rel = rng.choice(_TRANS_ITEMS)
    word = rng.choice(_TRANS_BANK[rel])
    used = {word.lower()}
    ds = _trans_distractors(rng, rel, difficulty, used, fmt=lambda w: f"{w},")
    correct = (f"{word},", f"Correct. '{word}' signals {_TRANS_REL_NAMES[rel]}, which is how the "
                           "second sentence relates to the first.")
    if difficulty == "hard":
        # semicolon version: options are lowercase
        ds = [(low(t), r) for t, r in ds]
        correct = (low(correct[0]), correct[1])
        text = f"{s1[:-1]}; ___ {s2}"
    else:
        text = f"{s1} ___ {s2}"
    return build(rng, fill(text, rng.choice(_TRANS_STEMS)), correct, ds,
                 subskill="logical_transitions", qtype="multiple_choice",
                 explanation=(f"Decide how the second sentence relates to the first "
                              f"({_TRANS_REL_NAMES[rel]}), then pick the transition that signals it."),
                 tags=["expression", "transitions", "opener"], est=50)


@family(fill_in=False)
def trans_sentence_options(rng, difficulty):
    """Whole-sentence options: the same second sentence with different transitions."""
    s1, s2, rel = rng.choice(_TRANS_ITEMS)
    word = rng.choice(_TRANS_BANK[rel])
    used = {word.lower()}
    ds = _trans_distractors(rng, rel, difficulty, used, fmt=lambda w: f"{w}, {s2}")
    correct = (f"{word}, {s2}", f"Correct. '{word}' expresses {_TRANS_REL_NAMES[rel]}, matching "
                                "the logic of the two ideas.")
    prompt = (f"{s1}\n\nWhich choice most logically follows the sentence above?")
    return build(rng, prompt, correct, ds, subskill="logical_transitions", qtype="multiple_choice",
                 explanation=(f"The idea that follows stands in {_TRANS_REL_NAMES[rel]} to the "
                              "first sentence, so only that transition fits."),
                 tags=["expression", "transitions", "sentence-options"], est=55)


# (lead, s1, s2, relation, close) coherent 3-4 sentence passages
_TRANS_PASS = [
    ("For decades, the harbor town relied on a single cannery.", "The cannery closed in 2003.",
     "the town had to find a new way to make a living.", "cause",
     "Today its old warehouses hold cafés and repair shops."),
    ("Desert tortoises spend most of the year underground.", "Their burrows stay cool even in July.",
     "dozens of other species shelter in the burrows during the hottest months.", "cause",
     "Biologists call the tortoise an engineer of its ecosystem."),
    ("The school's garden began as a single raised bed.", "Students added a bed each spring.",
     "the garden now supplies the cafeteria with salad greens.", "cause",
     "A greenhouse is planned for next year."),
    ("Early radio operators had to learn Morse code.", "The code is slow by modern standards.",
     "it can be sent with almost any equipment, even a flashlight.", "contrast",
     "Amateur operators still practice it today."),
    ("The city's oldest bridge was built for horse carts.", "Engineers reinforced it twice last century.",
     "heavy trucks are still banned from crossing it.", "contrast",
     "A second bridge now carries most freight."),
    ("Amara's grandmother kept bees behind the house.", "Amara helped with the harvest each August.",
     "she started a hive of her own at fourteen.", "sequence",
     "She now sells honey at the Saturday market."),
    ("Lichens grow on bare rock where little else survives.", "They release acids that slowly break the rock apart.",
     "they help create the first thin layer of soil on new ground.", "cause",
     "Mosses and grasses follow within a few decades."),
    ("The library's photograph archive was nearly lost in a flood.", "Volunteers dried each print by hand.",
     "they scanned every image so the collection could be viewed online.", "sequence",
     "The digital archive now receives thousands of visits a month."),
    ("Many migrating birds travel at night.", "Bright city lights can draw them off course.",
     "several cities now dim their skylines during peak migration.", "cause",
     "Early counts suggest fewer collisions."),
    ("The clock tower's mechanism dates from 1884.", "It must be wound by hand twice a week.",
     "the tower keeps time to within a few seconds a month.", "contrast",
     "A volunteer has climbed the stairs to wind it for thirty years."),
    ("The new stadium was designed to use less water.", "Rain is collected from the roof.",
     "the field is irrigated with recycled water from the concession stands.", "addition",
     "Water use has fallen by half since the stadium opened."),
    ("Vanilla comes from the pod of an orchid.", "Outside its native range, the orchid has no natural pollinator.",
     "farmers must pollinate each flower by hand.", "cause",
     "This is one reason real vanilla is so expensive."),
]


@family(fill_in=True, small_space=True)
def trans_passage(rng, difficulty):
    """Multi-sentence passage with the transition blank in the middle."""
    lead, s1, s2, rel, close = rng.choice(_TRANS_PASS)
    word = rng.choice(_TRANS_BANK[rel])
    used = {word.lower()}
    ds = _trans_distractors(rng, rel, difficulty, used)
    correct = (word, f"Correct. The sentence after the blank expresses {_TRANS_REL_NAMES[rel]} "
                     "relative to the one before it.")
    text = f"{lead} {s1} ___, {s2}" if difficulty == "easy" else f"{lead} {s1} ___, {s2} {close}"
    return build(rng, fill(text, rng.choice(_TRANS_STEMS)), correct, ds,
                 subskill="logical_transitions", qtype="multiple_choice",
                 explanation=(f"Read the sentences on either side of the blank: the second gives "
                              f"{_TRANS_REL_NAMES[rel]} relative to the first."),
                 tags=["expression", "transitions", "passage"], est=60)


_TRANS_STEPS = [
    ("To press flowers,", "lay the blooms between sheets of paper.", "set a heavy book on top for two weeks.",
     "mount the dried flowers on card stock."),
    ("To calibrate the telescope,", "point it at a bright star.", "adjust the focus until the star is a sharp point.",
     "lock the mount in place."),
    ("Before a performance,", "the choir warms up with scales.", "it rehearses the opening number once.",
     "the singers file onto the stage."),
    ("To make the dye,", "boil the onion skins for an hour.", "strain out the skins and add the wool.",
     "rinse the wool in cold water."),
    ("When the alarm sounds,", "the crew secures the hatches.", "it checks the radio.",
     "it reports to the bridge."),
    ("To reset the router,", "unplug it for thirty seconds.", "plug it back in and wait for the lights.",
     "reconnect each device."),
    ("Each spring,", "the farmers plow the lower field.", "they plant barley along the river.",
     "they repair the fences before the cattle return."),
    ("To build the kite,", "cut two thin spars from bamboo.", "tie them into a cross and stretch paper over the frame.",
     "attach the line and a long tail."),
    ("To test the sample,", "the technician heats it to two hundred degrees.", "she measures how much mass it loses.",
     "she records the result in the log."),
    ("At the start of each shift,", "the baker feeds the sourdough starter.", "she mixes the first batch of dough.",
     "she lights the ovens."),
]
_SEQ_WORDS = ["Next", "Then", "After that"]
_SEQ_FINAL = ["Finally", "Lastly"]


@family(fill_in=True, small_space=True)
def trans_sequence(rng, difficulty):
    """Steps of a process: the middle step needs a sequence transition."""
    lead, a, b, c = rng.choice(_TRANS_STEPS)
    fin = rng.choice(_SEQ_FINAL)
    word = rng.choice(_SEQ_WORDS)
    correct = (word, f"Correct. '{word}' marks the next step in the sequence of actions.")
    pool = {"easy": [("However", "'However' signals a contrast, but this is simply the next step."),
                     ("For example", "The step is not an example of the previous one."),
                     ("In conclusion", "The passage continues after this step; it is not the conclusion.")],
            "medium": [("Consequently", "The second step is not a result of the first; it just follows it."),
                       ("Meanwhile", "'Meanwhile' means at the same time, but these steps happen in order."),
                       ("In other words", "The step restates nothing; it adds a new action.")],
            "hard": [("Previously", "'Previously' points backward in time, but this step comes after the first."),
                     ("Likewise", "'Likewise' signals a similar idea, not the next step in a process."),
                     ("Consequently", "The second step is not caused by the first; it merely follows it.")]}
    ds = pool[difficulty]
    text = f"{lead} {a} ___, {b} {fin}, {c}"
    return build(rng, fill(text, rng.choice(_TRANS_STEMS)), correct, ds,
                 subskill="logical_transitions", qtype="multiple_choice",
                 explanation=("The passage lists steps in order (ending with 'Finally'), so the middle "
                              "step takes a sequence transition."),
                 tags=["expression", "transitions", "sequence"], est=50)


# =========================================================================== #
# v2.1 ADDITIONS — SENTENCE BOUNDARIES
# =========================================================================== #
_BND_MORE = [
    ("The ferry runs only twice a day in winter", "islanders plan their errands carefully", "cause"),
    ("The violinist broke a string during the finale", "she finished the piece on three strings", "contrast"),
    ("The town repaved Main Street last spring", "the potholes are already returning", "contrast"),
    ("The archive digitized its oldest maps", "scholars abroad can now consult them", "cause"),
    ("The storm knocked out power for two days", "the bakery kept its wood oven running", "contrast"),
    ("The garden club planted milkweed along the fence", "monarch butterflies returned within a month", "cause"),
    ("The lecture hall seats three hundred", "the talk drew twice that many", "contrast"),
    ("The river ferry was replaced by a bridge", "the old pilings still stand in the shallows", "addition"),
    ("The choir rehearses in a converted barn", "the acoustics are surprisingly good", "addition"),
    ("The telescope sits on a remote plateau", "astronomers travel for days to reach it", "cause"),
    ("The bakery introduced a rye loaf in March", "it outsold every other bread by June", "cause"),
    ("The marathon course climbs two long hills", "most runners slow dramatically after mile twenty", "cause"),
    ("The museum's new wing cost twice the estimate", "attendance has more than doubled", "contrast"),
    ("The clinic extended its evening hours", "fewer patients now use the emergency room", "cause"),
    ("The lighthouse keeper retired in 1987", "a volunteer still climbs the stairs each night", "contrast"),
    ("The robotics team practiced for six months", "its robot stalled in the first round", "contrast"),
]
_BND.extend(_BND_MORE)
_BND_SUBJ_WORDS.update({"she": 1, "the potholes": 2, "scholars abroad": 2, "the bakery": 2,
                        "monarch butterflies": 2, "the talk": 2, "the old pilings": 3,
                        "the acoustics": 2, "astronomers": 1, "it": 1, "most runners": 2,
                        "attendance": 1, "fewer patients": 2, "a volunteer": 2, "its robot": 2,
                        "islanders": 1})


@family(fill_in=True)
def bnd_mark_choice(rng, difficulty):
    """Semicolon vs. colon vs. dash vs. comma: only one mark fits the structure."""
    if rng.random() < 0.5:
        # a list follows a complete clause -> colon
        lead, items = rng.choice(_BND_LISTS)
        lst = ", ".join(items[:-1]) + f", and {items[-1]}"
        first = items[0]
        rest = lst[len(first):]
        last = lead.split()[-1]
        correct = (f"{last}: {first}", "Correct. A colon after a complete clause introduces a list.")
        ds = [(f"{last}; {first}", "A semicolon must have an independent clause on each side."),
              (f"{last} — {first}", "A dash can introduce a list only when the list is a short, "
                                    "emphatic afterthought; here the formal introduction of a "
                                    "numbered set calls for a colon.") if difficulty == "hard" else
              (f"{last}, {first}", "A comma cannot introduce a list that has been announced by a "
                                   "number ('three ...')."),
              (f"{last}. {cap(first)}", "A period leaves the list standing alone as a fragment.")]
        text = f"{' '.join(lead.split()[:-1])} ___{rest}."
        expl = "A complete clause followed by an announced list takes a colon."
    else:
        a, b, rel = rng.choice(_BND)
        adv = rng.choice(_BND_ADV[rel])
        aw, bw = a.split(), b.split()
        a_last, a_rest = aw[-1], " ".join(aw[:-1])
        b_first, b_rest = bw[0], " ".join(bw[1:])
        correct = (f"{a_last}; {adv}, {b_first}", f"Correct. Two independent clauses linked by the "
                                                  f"conjunctive adverb '{adv}' take a semicolon.")
        ds = [(f"{a_last}: {adv}, {b_first}", "A colon introduces an explanation or list; it does not "
                                              "join clauses through a conjunctive adverb."),
              (f"{a_last}, {adv}, {b_first}", "Comma splice: a conjunctive adverb cannot join clauses with commas."),
              (f"{a_last} — {adv} — {b_first}", "Dashes set off an interruption; they cannot join two "
                                                "independent clauses this way.")]
        text = f"{a_rest} ___ {b_rest}."
        expl = ("Two independent clauses joined by a conjunctive adverb need a semicolon before the "
                "adverb; colons, commas, and dashes do not do that job.")
    return build(rng, fill(text, conv_stem(rng)), correct, ds, subskill="clause_joining",
                 explanation=expl, tags=["conventions", "boundaries", "mark-choice"], est=50)


@family(fill_in=False)
def bnd_splice_repair(rng, difficulty):
    """Repair a comma splice; options are whole sentences, one uses the adverb correctly."""
    a, b, rel = rng.choice(_BND)
    adv = rng.choice(_BND_ADV[rel])
    conj = _BND_CONJ[rel]
    correct = (f"{a}; {adv}, {b}.", f"Correct. A semicolon joins the clauses and '{adv}' is set off by a comma.")
    ds = [(f"{a}, {adv}, {b}.", "Comma splice: '" + adv + "' is an adverb, not a conjunction."),
          (f"{a}, {adv}; {b}.", "The semicolon is in the wrong place; it must come before the adverb."),
          (f"{a} {adv}, {b}.", "Run-on: nothing separates the two independent clauses.")]
    if difficulty == "hard":
        ds[2] = (f"{a}, {conj} {adv}, {b}.", f"'{conj}' and '{adv}' signal the same link; pairing them is redundant.")
    if difficulty != "easy":
        ds[0] = (f"{a}; {conj} {adv}, {b}.", f"A semicolon should not be followed by the conjunction '{conj}'.")
    prompt = (f"{a}, {adv}, {b}.\n\nThe sentence above contains a comma splice. Which choice "
              "corrects it while keeping the transition?")
    return build(rng, prompt, correct, ds, subskill="clause_joining",
                 explanation=("A conjunctive adverb such as '" + adv + "' needs a semicolon (or period) "
                              "before it and a comma after it."),
                 tags=["conventions", "boundaries", "splice-repair"], est=50)


_BND_FRAG = [
    ("Having reviewed the budget for a week,", "the committee approved it without changes",
     "approving it without changes", "which the committee approved without changes",
     "the committee approving it without changes"),
    ("Built on a bluff above the harbor,", "the lighthouse is visible for twenty miles",
     "visible for twenty miles", "which is visible for twenty miles",
     "the lighthouse visible for twenty miles"),
    ("After the last ferry had left,", "the island fell silent",
     "the island falling silent", "which left the island silent",
     "the silence of the island"),
    ("Hoping to attract younger readers,", "the magazine redesigned its cover",
     "redesigning its cover", "which redesigned its cover",
     "the magazine redesigning its cover"),
    ("Although the trail is short,", "it climbs nearly two thousand feet",
     "climbing nearly two thousand feet", "which climbs nearly two thousand feet",
     "its climb of nearly two thousand feet"),
    ("Because the river had flooded the lower fields,", "the farmers planted on the ridge",
     "the farmers planting on the ridge", "who planted on the ridge",
     "planting on the ridge instead"),
    ("Wrapped in a fog that lasted all morning,", "the harbor was nearly invisible",
     "nearly invisible", "which was nearly invisible",
     "the harbor nearly invisible"),
    ("Once the mural was finished,", "the city held a small ceremony",
     "the city holding a small ceremony", "which the city celebrated with a ceremony",
     "a small ceremony by the city"),
    ("Trained as a chemist,", "Rosa approaches cooking like an experiment",
     "approaching cooking like an experiment", "who approaches cooking like an experiment",
     "Rosa's approach to cooking as an experiment"),
    ("While the orchestra tuned,", "the audience settled into its seats",
     "the audience settling into its seats", "which settled the audience into its seats",
     "the settling of the audience"),
    ("Discovered in a flea market,", "the painting turned out to be worth a fortune",
     "turning out to be worth a fortune", "which turned out to be worth a fortune",
     "the painting worth a fortune"),
    ("Even though the forecast promised sun,", "a thunderstorm rolled in by noon",
     "a thunderstorm rolling in by noon", "which rolled in by noon",
     "the arrival of a thunderstorm by noon"),
]


@family(fill_in=True)
def bnd_fragment_clause(rng, difficulty):
    """Fragment repair: the blank must hold a complete main clause."""
    opening, main, w_ing, w_which, w_noun = rng.choice(_BND_FRAG)
    correct = (main, "Correct. This supplies a subject and a finite verb, giving the sentence a main clause.")
    ds = [(w_ing, "An -ing phrase has no finite verb, so the sentence remains a fragment."),
          (w_which, "A 'which'/'who' clause is subordinate; the sentence still has no main clause."),
          (w_noun, "A noun phrase alone cannot serve as the main clause.")]
    text = f"{opening} ___."
    if difficulty != "easy":
        text = rng.choice(["Few people know the story. ", "The reason is simple. ",
                           "The details are worth recalling. "]) + text
    if difficulty == "hard":
        text = text + " " + rng.choice(["Nobody objected.", "The decision was unanimous.",
                                        "The story is still told today."])
    stem = rng.choice(["Which choice completes the text so that it is a complete sentence?",
                       conv_stem(rng)])
    return build(rng, fill(text, stem), correct, ds, subskill="clause_joining",
                 explanation=("The opening phrase is subordinate, so what follows the comma must be an "
                              "independent clause with its own subject and verb."),
                 tags=["conventions", "boundaries", "fragment"], est=50)


# =========================================================================== #
# v2.1 ADDITIONS — SUBJECT-VERB AGREEMENT
# =========================================================================== #
_SVA_OF.extend([
    ("The price of the tickets", False, "t"), ("The flavor of the peppers", False, "t"),
    ("The history of the islands", False, "t"), ("The manager of the stores", False, "p"),
    ("The spokesperson for the unions", False, "p"), ("The pilot of the gliders", False, "p"),
    ("The keys to the cabinet", True, "t"), ("The branches of the old oak", True, "t"),
    ("The members of the council", True, "p"), ("The guards at the gate", True, "p"),
    ("The photographs in the album", True, "t"), ("The ferries across the bay", True, "t"),
])
_SVA_QTY = [
    ("Twenty dollars", "a fair price for the tour", "amount of money"),
    ("Three hours", "not enough time for the climb", "span of time"),
    ("Five miles", "a long way to walk in the heat", "distance"),
    ("Ten percent of the budget", "set aside for repairs", "single share"),
    ("Two cups of flour", "all the recipe requires", "quantity"),
    ("Six weeks", "the usual wait for a permit", "span of time"),
    ("Forty acres", "enough land for the orchard", "area"),
    ("Half a ton of gravel", "needed for the path", "quantity"),
    ("Thirty minutes", "plenty of time to reach the gate", "span of time"),
    ("Two hundred pages", "a lot to read in one night", "quantity"),
    ("Fifteen dollars", "the usual fee for the ferry", "amount of money"),
    ("Three quarters of the orchard", "planted with apples", "single share"),
    ("Nine innings", "the standard length of a game", "span"),
    ("A thousand pounds of ice", "delivered every morning", "quantity"),
]
_SVA_TITLES = [
    ("'Tales of the Harbor'", "a collection of twelve stories"),
    ("'The Gardeners'", "the author's best-known play"),
    ("The Hollow Hills", "a village of two hundred people"),
    ("'Notes on Weather'", "assigned in every section of the course"),
    ("Mathematics", "offered at eight in the morning"),
    ("'Letters from the Mill'", "being reprinted this year"),
    ("'Bridges of the North'", "the museum's most popular exhibit"),
    ("The United Islands", "home to fewer than a thousand people"),
    ("'Three Sisters'", "performed every spring by the drama club"),
    ("Economics", "taught in the oldest building on campus"),
]


@family(fill_in=True)
def sva_quantity(rng, difficulty):
    """Amounts, titles, and plural-looking singulars take singular verbs."""
    if difficulty == "easy" or rng.random() < 0.6:
        subj, tail, kind = rng.choice(_SVA_QTY)
        rule = f"'{subj}' names one {kind}, so it takes a singular verb"
    else:
        subj, tail = rng.choice(_SVA_TITLES)
        rule = f"{subj} is a single title or name even though it looks plural, so the verb is singular"
    pairs = {"easy": [("is", "are", "were"), ("was", "were", "are")],
             "medium": [("is", "are", "were"), ("was", "were", "are"), ("has been", "have been", "being")],
             "hard": [("was", "were", "are"), ("has been", "have been", "being"), ("is", "are", "were")]}[difficulty]
    right, wrong, other = rng.choice(pairs)
    correct = (right, f"Correct. {cap(rule)}.")
    ds = [(wrong, "Agreement error: the subject is grammatically singular despite the plural word in it."),
          (other, "This form is the wrong number or cannot serve as the main verb here."),
          ("to be", "An infinitive cannot be the main verb.")]
    text = f"{subj} ___ {tail}."
    if difficulty == "hard":
        text = rng.choice(["According to the guide, ", "As the clerk explained, ", "In the end, "]) + \
            (low(text) if not subj.startswith("'") and subj not in ("Mathematics", "The Hollow Hills") else text)
    return build(rng, fill(text, conv_stem(rng)), correct, ds, subskill="subject_verb_agreement",
                 explanation=f"{cap(rule)}.", tags=["conventions", "agreement", "quantity-title"])


_SVA_GERUND = [
    ("Running marathons", "the runners", "requires", "require", "months of training"),
    ("Collecting old maps", "the maps", "has become", "have become", "her favorite pastime"),
    ("Restoring antique clocks", "the clocks", "demands", "demand", "patience and a steady hand"),
    ("Reading the letters aloud", "the letters", "brings", "bring", "the history to life"),
    ("Counting the nests each spring", "the nests", "takes", "take", "the volunteers a full week"),
    ("Mapping the sea caves", "the caves", "was", "were", "the expedition's main goal"),
    ("Baking the festival loaves", "the loaves", "begins", "begin", "before dawn"),
    ("Grading the essays", "the essays", "keeps", "keep", "the teachers busy all weekend"),
    ("Photographing the migrating cranes", "the cranes", "is", "are", "harder than it looks"),
    ("Repairing the stone walls", "the walls", "falls", "fall", "to the oldest farmers"),
    ("Translating the diaries", "the diaries", "has taken", "have taken", "three summers"),
    ("Feeding the goats", "the goats", "starts", "start", "the day on the farm"),
    ("Sorting the donated books", "the books", "occupies", "occupy", "most of the volunteers' morning"),
    ("Tuning the organ's pipes", "the pipes", "requires", "require", "a specialist from the city"),
    ("Painting the lighthouses", "the lighthouses", "was", "were", "once a summer job for sailors"),
    ("Replanting the dunes", "the dunes", "protects", "protect", "the road behind them"),
]


@family(fill_in=True)
def sva_gerund(rng, difficulty):
    """A gerund phrase is a singular subject, whatever plural noun it contains."""
    ger, bait, sing, plur, tail = rng.choice(_SVA_GERUND)
    head = ger.split()[0]
    correct = (sing, f"Correct. The subject is the gerund phrase '{ger}', a single activity, so the "
                     f"verb is singular.")
    ds = [(plur, f"Agreement error: '{bait.split()[-1]}' is not the subject; the activity '{head.lower()}' is."),
          (_ing(plur), "This form cannot serve as the main verb."),
          (f"to {plur.split()[0]}" if plur not in ("are", "were") else "to be",
           "An infinitive cannot be the main verb here.")]
    if difficulty == "easy":
        text = f"{ger} ___ {tail}."
    elif difficulty == "medium":
        text = f"{ger}, {rng.choice(['as any volunteer will tell you', 'according to the guide', 'in most years'])}, ___ {tail}."
    else:
        pair = rng.choice(_SVA_GERUND)
        text = f"{ger} and {low(pair[0])} ___ {tail}." if pair is not ger and rng.random() < 0.5 else \
            f"{ger}, together with {low(pair[0]) if pair[0] != ger else 'everything else'}, ___ {tail}."
        if " and " in text:
            correct = (plur, "Correct. Two gerund phrases joined by 'and' form a plural subject.")
            ds = [(sing, "Agreement error: two activities joined by 'and' make a plural subject."),
                  ("being", "'being' cannot stand alone as the main verb."),
                  (f"to {plur.split()[0]}" if plur not in ("are", "were") else "to be",
                   "An infinitive cannot be the main verb here.")]
    return build(rng, fill(text, conv_stem(rng)), correct, ds, subskill="subject_verb_agreement",
                 explanation=("A gerund phrase ('-ing' activity) is one thing and takes a singular verb; "
                              "two gerund phrases joined by 'and' take a plural verb."),
                 tags=["conventions", "agreement", "gerund-subject"])


_SVA_EO_P = [("the manager", "the clerks"), ("the coach", "the players"), ("the editor", "the reporters"),
             ("the conductor", "the musicians"), ("the captain", "the rowers"), ("the mayor", "the council members")]
_SVA_EO_T = [("the bridge", "the tunnels"), ("the mural", "the sculptures"), ("the engine", "the brakes"),
             ("the lobby", "the hallways"), ("the budget", "the schedules"), ("the recipe", "the photographs")]


@family(fill_in=True)
def sva_either_or(rng, difficulty):
    """either...or / neither...nor / not only...but also: agree with the nearer subject."""
    cat = rng.choice(["p", "t"])
    a, b = rng.choice(_SVA_EO_P if cat == "p" else _SVA_EO_T)
    verbs = rng.choice(_SVA_VERBS_P if cat == "p" else _SVA_VERBS_T)
    pair = rng.choice({"easy": ["either", "neither"], "medium": ["either", "neither", "not only"],
                       "hard": ["either", "neither", "not only"]}[difficulty])
    near_plural = rng.random() < 0.5
    first, second = (a, b) if near_plural else (b, a)
    frames = {"either": f"Either {first} or {second}", "neither": f"Neither {first} nor {second}",
              "not only": f"Not only {first} but also {second}"}
    subj = frames[pair]
    correct, ds, right = _sva_opts(near_plural, verbs)
    text = f"{subj} ___ {verbs[4]}."
    if difficulty == "hard":
        text = f"{subj}, " + rng.choice(["according to the report,", "as a rule,", "for better or worse,"]) + f" ___ {verbs[4]}."
    nearer = second.split()[-1]
    return build(rng, fill(text, conv_stem(rng)), correct, ds, subskill="subject_verb_agreement",
                 explanation=(f"With '{pair}...', the verb agrees with the subject nearer to it "
                              f"('{nearer}'), which is {'plural' if near_plural else 'singular'}: '{right}'."),
                 tags=["conventions", "agreement", "proximity-rule"])


# =========================================================================== #
# v2.1 ADDITIONS — PUNCTUATION
# =========================================================================== #
_POSS_FRAMES.extend(["Everyone admired the {n} ___ garden",
                     "Reporters described the {n} ___ response as swift",
                     "The {n} ___ archive was opened to researchers last spring"])
_SING_NOUNS.extend([("mayor", "mayor's"), ("village", "village's"), ("pilot", "pilot's"),
                    ("library", "library's")])
_PLUR_NOUNS.extend([("sailors", "sailors'"), ("farmers", "farmers'"), ("singers", "singers'")])

_HYPHEN = [
    ("a", "well-known", "author", "well known", "well-known-author"),
    ("a", "twelve-year-old", "violinist", "twelve year old", "twelve-year old"),
    ("a", "long-term", "plan", "long term", "long-term-plan"),
    ("a", "state-of-the-art", "laboratory", "state of the art", "state-of-the art"),
    ("a", "fast-moving", "storm", "fast moving", "fast-moving-storm"),
    ("a", "high-speed", "rail line", "high speed", "high-speed-rail"),
    ("a", "first-rate", "performance", "first rate", "first-rate-performance"),
    ("a", "last-minute", "change", "last minute", "last-minute-change"),
    ("a", "hard-won", "victory", "hard won", "hard-won-victory"),
    ("a", "world-famous", "orchestra", "world famous", "world-famous-orchestra"),
    ("an", "open-air", "market", "open air", "open-air-market"),
    ("a", "part-time", "job", "part time", "part-time-job"),
    ("a", "once-in-a-lifetime", "chance", "once in a lifetime", "once-in-a-lifetime-chance"),
    ("a", "slow-moving", "river", "slow moving", "slow-moving-river"),
    ("a", "nineteenth-century", "map", "nineteenth century", "nineteenth-century-map"),
    ("a", "two-hour", "delay", "two hour", "two-hour-delay"),
    ("a", "salt-crusted", "pier", "salt crusted", "salt-crusted-pier"),
    ("a", "hand-carved", "canoe", "hand carved", "hand-carved-canoe"),
]
_HYPHEN_TAILS = ["drew a large crowd", "was announced yesterday", "surprised the critics",
                 "is described in the report", "impressed the judges", "appears in the brochure"]


@family(fill_in=True)
def punct_hyphen(rng, difficulty):
    """Compound adjectives before a noun are hyphenated."""
    art, comp, noun, bare, overhyph = rng.choice(_HYPHEN)
    tail = rng.choice(_HYPHEN_TAILS)
    correct = (f"{comp} {noun}", f"Correct. '{comp}' works as a single adjective before '{noun}', so its "
                                 "parts are joined with hyphens.")
    ds = [(f"{bare} {noun}", "Without hyphens the words do not read as one compound adjective."),
          (overhyph, "A hyphen must not attach the adjective to the noun it modifies."),
          (f"{comp}, {noun}", "No comma separates a compound adjective from its noun.")]
    if difficulty == "hard":
        ds[2] = (f"{comp.replace('-', ' ', 1)} {noun}", "Every part of the compound must be hyphenated, "
                                                         "not just the last pair.") if comp.count("-") > 1 else \
                (f"{comp.replace('-', '- ')} {noun}", "A space after the hyphen breaks the compound apart.")
    text = f"The newspaper praised {art} ___ that {tail}." if difficulty == "easy" else \
        rng.choice([f"According to the brochure, {art} ___ {tail}.",
                    f"Critics agree that {art} ___ {tail}.",
                    f"Nobody expected {art} ___, but one {tail}."])
    return build(rng, fill(text, conv_stem(rng)), correct, ds, subskill="punctuation",
                 explanation="Hyphenate the words of a compound adjective that comes before its noun.",
                 tags=["conventions", "punctuation", "hyphen"])


_QUOTES = [
    ("The results", "she said", "are final"), ("The bridge", "the engineer warned", "cannot bear heavy trucks"),
    ("This recipe", "my grandmother insisted", "needs more salt"), ("The ferry", "the captain announced", "will leave at dawn"),
    ("Our budget", "the mayor admitted", "is already spent"), ("The fog", "the guide explained", "lifts by noon"),
    ("The map", "Omar said", "is a century old"), ("The exhibit", "the curator added", "closes on Sunday"),
    ("The tide", "the harbormaster said", "turns at four"), ("Your essay", "the teacher wrote", "needs a stronger ending"),
    ("The vote", "the chair declared", "is unanimous"), ("This loaf", "the baker promised", "will keep for a week"),
    ("The comet", "Hana whispered", "is brighter than last night"), ("The road", "the ranger warned", "closes at dusk"),
]


@family(fill_in=True, small_space=True)
def punct_quotation(rng, difficulty):
    """Commas and periods go inside closing quotation marks; a split quotation needs two commas."""
    first, attr, rest = rng.choice(_QUOTES)
    if difficulty == "easy":
        text = f'"{first} {rest}___ {attr}.'
        correct = (',"', "Correct. The comma that separates the quotation from its attribution goes inside the closing quotation mark.")
        ds = [('",', "In American English the comma goes inside the closing quotation mark, not after it."),
              ('"', "A comma is needed to separate the quotation from the words that attribute it."),
              ('."', "A period would end the sentence before the attribution, leaving a fragment.")]
        expl = "Put the comma inside the closing quotation mark, before the attribution."
    else:
        text = f'"{first}___{rest}."'
        correct = (f'," {attr}, "', f"Correct. An interrupting attribution ('{attr}') is set off by commas, "
                                     "each placed inside the quotation marks it belongs with.")
        ds = [(f'" {attr}, "', "A comma must come before the attribution, inside the first closing quotation mark."),
              (f'," {attr} "', "A comma is needed after the attribution as well as before it."),
              (f'," {attr}; "', "A semicolon cannot set off an attribution inside a quotation.")]
        expl = "A quotation interrupted by an attribution takes a comma on each side of the attribution."
    return build(rng, fill(text, conv_stem(rng)), correct, ds, subskill="punctuation",
                 explanation=expl, tags=["conventions", "punctuation", "quotation"], est=50)


_SEMI_LISTS = [
    ("The tour stops in", [("Lyon", "France"), ("Turin", "Italy"), ("Basel", "Switzerland")]),
    ("The panel includes", [("Lena Marsh", "a marine biologist"), ("Omar Haddad", "an architect"), ("Priya Sen", "a historian")]),
    ("The orchestra will perform in", [("Portland", "Maine"), ("Austin", "Texas"), ("Boise", "Idaho")]),
    ("The judges were", [("Rosa Ibarra", "a chef"), ("Victor Lane", "a baker"), ("Hana Sato", "a food writer")]),
    ("The expedition visited", [("Tromsø", "Norway"), ("Nuuk", "Greenland"), ("Reykjavík", "Iceland")]),
    ("The grant funds", [("new microscopes", "ordered in May"), ("a visiting lecturer", "arriving in fall"), ("two internships", "starting in June")]),
    ("The festival honored", [("Mateo Ruiz", "a sculptor"), ("Wren Adler", "a poet"), ("Idris Bello", "a filmmaker")]),
    ("The relay passed through", [("Dover", "Delaware"), ("Salem", "Oregon"), ("Helena", "Montana")]),
    ("The museum acquired", [("a map", "drawn in 1790"), ("a ledger", "kept by the first mayor"), ("a quilt", "sewn by mill workers")]),
    ("The crew included", [("Chloe Park", "the navigator"), ("Felix Moreau", "the cook"), ("Nadia Rahman", "the medic")]),
]


@family(fill_in=True, small_space=True)
def punct_semicolon_list(rng, difficulty):
    """Items that contain commas are separated by semicolons."""
    lead, items = rng.choice(_SEMI_LISTS)
    (a1, a2), (b1, b2), (c1, c2) = items
    correct = (f"{a1}, {a2}; {b1}, {b2}; and {c1}, {c2}", "Correct. Because each item contains a comma, "
                                                           "semicolons separate the items.")
    ds = [(f"{a1}, {a2}, {b1}, {b2}, and {c1}, {c2}", "With commas everywhere, the reader cannot tell "
                                                        "where one item ends and the next begins."),
          (f"{a1}, {a2}; {b1}, {b2}; and, {c1}, {c2}", "No comma follows 'and' in a series."),
          (f"{a1}; {a2}, {b1}; {b2}, and {c1}; {c2}", "The semicolons split items apart instead of separating them.")]
    if difficulty == "hard":
        ds[1] = (f"{a1}, {a2}; {b1}, {b2}, and {c1}, {c2}", "The separator must be consistent: the last "
                                                             "item also needs a semicolon before 'and'.")
    text = f"{lead} ___."
    if difficulty != "easy":
        text = rng.choice(["As the program notes, ", "According to the brochure, ", "This year, "]) + low(text)
    return build(rng, fill(text, conv_stem(rng)), correct, ds, subskill="punctuation",
                 explanation=("When list items themselves contain commas, separate the items with "
                              "semicolons, including before the final 'and'."),
                 tags=["conventions", "punctuation", "semicolon-list"], est=55)


_DASH_PAREN = [
    ("The three founders", "Lena, Omar, and Priya", "met in a college chemistry lab"),
    ("Two of the bridges", "the oldest and the longest", "closed for repairs last spring"),
    ("The main ingredients", "flour, butter, and sea salt", "cost almost nothing"),
    ("Several instruments", "a cello, two violins, and a harp", "were donated to the school"),
    ("The winning entries", "a mural, a short film, and a poem", "will tour the county"),
    ("The three largest towns", "Harlan, Weston, and Mill Creek", "share a single hospital"),
    ("Four of the volunteers", "Tessa, Bruno, Esme, and Gavin", "stayed until midnight"),
    ("The oldest trees", "two oaks, an elm, and a beech", "predate the village"),
    ("The band's instruments", "a fiddle, a banjo, and an upright bass", "fit in one small van"),
    ("Several crops", "barley, oats, and rye", "survived the late frost"),
    ("Three of the paintings", "the harbor scenes, the portrait, and the storm", "were sold at auction"),
    ("The island's exports", "wool, honey, and smoked fish", "travel by ferry twice a week"),
]


@family(fill_in=True, small_space=True)
def punct_dash_paren(rng, difficulty):
    """An interruption that itself contains commas needs dashes (or parentheses), not commas."""
    head, inner, pred = rng.choice(_DASH_PAREN)
    use_paren = difficulty != "easy" and rng.random() < 0.4
    if use_paren:
        correct = (f" ({inner})", "Correct. Parentheses enclose the interruption and keep its internal commas "
                                  "from confusing the reader.")
        ds = [(f", {inner},", "Commas around an interruption that already contains commas leave the reader "
                              "unable to see where the aside begins and ends."),
              (f" ({inner},", "The closing parenthesis is missing."),
              (f" ({inner}) which", "Adding 'which' turns the rest of the sentence into a relative clause "
                                   "with no main verb.")]
    else:
        correct = (f" — {inner} —", "Correct. A pair of dashes sets off the interruption, whose internal "
                                    "commas would be confusing between ordinary commas.")
        ds = [(f", {inner},", "Commas around an interruption that already contains commas leave the reader "
                              "unable to see where the aside begins and ends."),
              (f" — {inner},", "The punctuation must match on both sides: dash with dash."),
              (f" — {inner} — which", "Adding 'which' turns the rest of the sentence into a relative "
                                     "clause with no main verb.")]
    text = f"{head}___ {pred}."
    if difficulty == "hard":
        text = text + " " + rng.choice(["The story is well known locally.", "Few people remember the details.",
                                        "A plaque marks the spot."])
    return build(rng, fill(text, conv_stem(rng)), correct, ds, subskill="punctuation",
                 explanation=("When an interrupting phrase contains its own commas, enclose it in a "
                              "matched pair of dashes or parentheses so its boundaries stay clear."),
                 tags=["conventions", "punctuation", "dash-paren"], est=50)


# =========================================================================== #
# v2.1 ADDITIONS — PRONOUNS
# =========================================================================== #
_SHIFT = [
    ("If one wants to master the cello,", "must practice every day", "one"),
    ("When you reach the summit,", "can see three states", "you"),
    ("Once a person learns to sail,", "never forgets the feel of the wind", "he or she"),
    ("If one reads the manual carefully,", "will find the answer on the first page", "one"),
    ("When you plant tomatoes too early,", "risk losing them to frost", "you"),
    ("If a visitor arrives after noon,", "will find the gates locked", "he or she"),
    ("Once one has tasted the rye loaf,", "rarely goes back to white bread", "one"),
    ("When you enter the archive,", "must sign the register", "you"),
    ("If a student misses the deadline,", "forfeits the deposit", "he or she"),
    ("When one volunteers at the shelter,", "learns patience quickly", "one"),
    ("If you want the best seats,", "should arrive an hour early", "you"),
    ("When a hiker reaches the ridge,", "can see the whole valley", "he or she"),
    ("If one studies the tide tables,", "can predict the best time to launch", "one"),
    ("When you taste the rye loaf,", "understand why the line is so long", "you"),
    ("If a traveler misses the last ferry,", "must stay the night on the island", "he or she"),
    ("Once one has learned the knots,", "never forgets them", "one"),
]
# Never offer "they" beside a keyed "he or she": singular "they" is standard
# for "a visitor", so both would be right. "I" is an unambiguous shift instead.
_SHIFT_WRONG = {"one": ["you", "I", "we"], "you": ["one", "I", "we"],
                "he or she": ["you", "one", "we"]}


@family(fill_in=True)
def pron_shift(rng, difficulty):
    """Keep the point of view consistent (one / you / a person)."""
    lead, pred, right = rng.choice(_SHIFT)
    wrongs = _SHIFT_WRONG[right]
    rationale = {"you": "Shifting to 'you' changes the point of view established in the first clause.",
                 "one": "Shifting to 'one' changes the point of view established in the first clause.",
                 "they": "'they' does not match the singular, consistent point of view of the first clause.",
                 "we": "'we' introduces a new point of view not used earlier.",
                 "I": "'I' shifts to the first person, a point of view not used earlier."}
    if right == "he or she":
        correct = (right, "Correct. The first clause is about one person in the third person, so the "
                          "second clause keeps that point of view.")
    else:
        correct = (right, f"Correct. The first clause uses '{right}', so the second clause keeps the same "
                          "point of view.")
    ds = [(w, rationale[w]) for w in wrongs]
    text = f"{lead} ___ {pred}."
    if difficulty != "easy":
        lead = rng.choice(["As the guide puts it, ", "Everyone agrees on one thing: ", "The rule is simple. "])
        text = lead + (text if lead.endswith(". ") else low(text))
    if difficulty == "hard":
        text = text + " " + rng.choice(["There are no exceptions.", "The lesson is quickly learned.",
                                        "Most people find this out the hard way."])
    return build(rng, fill(text, conv_stem(rng)), correct, ds, subskill="pronouns",
                 explanation="A sentence must not shift between 'one', 'you', and third-person pronouns.",
                 tags=["conventions", "pronouns", "shift"])


# (lead clause, clear noun phrase, tail shared by the vague versions)
_VAGUE = [
    ("The ferry was canceled and the road flooded", "a combination that stranded the island for two days",
     "stranded the island for two days"),
    ("The company cut prices and doubled its staff", "moves that paid off within a year", "paid off within a year"),
    ("The orchestra lost its conductor and its hall in the same month", "two blows that nearly ended the season",
     "nearly ended the season"),
    ("The river rose and the levee held", "an outcome that surprised the engineers", "surprised the engineers"),
    ("The bakery raised its prices and shortened its hours", "changes that cost it several regulars",
     "cost it several regulars"),
    ("The team practiced in silence for a week", "an experiment that the coach called a success",
     "was something the coach called a success"),
    ("The library closed on Mondays and opened later on Saturdays", "hours that confused many patrons",
     "confused many patrons"),
    ("The storm toppled the old oak and spared the barn", "the result the farmer still cannot explain",
     "is something the farmer still cannot explain"),
    ("The clinic added evening hours and hired two nurses", "steps that cut waiting times in half",
     "cut waiting times in half"),
    ("The mural was finished a week early and under budget", "news that delighted the council",
     "delighted the council"),
    ("The glacier retreated and the valley greened", "a shift that puzzled the first surveyors",
     "puzzled the first surveyors"),
    ("The team lost its first six games and then won nine straight", "a turnaround no one had predicted",
     "was a turnaround no one had predicted"),
]


@family(fill_in=True)
def pron_vague(rng, difficulty):
    """Vague 'this' / 'which' with no single noun antecedent: supply a noun instead."""
    lead, noun_phrase, tail = rng.choice(_VAGUE)
    adv = rng.choice(["ultimately", "predictably", "unfortunately", "in the end,"])
    correct = (noun_phrase, "Correct. Naming the idea with a noun gives the clause a clear antecedent.")
    # No "which" option: broad-reference "which" ("..., which confused many
    # patrons") is accepted by many editors, so it made two answers defensible.
    ds = [(f"that {adv} {tail}", "'that' has no single noun to refer to, and after a comma it starts a "
                                 "new independent clause, creating a comma splice."),
          (f"this {adv} {tail}", "'this' has no clear antecedent and creates a comma splice."),
          (f"it {adv} {tail}", "'it' has no clear antecedent, and the clause becomes a comma splice.")]
    text = f"{lead}, ___."
    if difficulty != "easy":
        text = rng.choice(["Last winter, ", "In 2019, ", "That spring, "]) + low(text)
    if difficulty == "hard":
        text = text + " " + rng.choice(["Nobody had predicted it.", "The lesson was not lost on anyone.",
                                        "The story is still told in town."])
    return build(rng, fill(text, conv_stem(rng)), correct, ds, subskill="pronouns",
                 explanation=("A pronoun must point to one specific noun; when it would refer to a whole "
                              "idea, replace it with a noun phrase that names that idea."),
                 tags=["conventions", "pronouns", "vague-reference"], est=50)


_REFL_COMP = [
    ("The director gave the award to {N} and ___", "object"),
    ("The invitation was meant for {N} and ___", "object"),
    ("The coach chose {N} and ___ to lead the drills", "object"),
    ("Please return the keys to {N} or ___", "object"),
    ("{N} and ___ will present the plan on Monday", "subject"),
    ("Neither {N} nor ___ expected the storm", "subject"),
]


@family(fill_in=True)
def pron_reflexive_compound(rng, difficulty):
    """Reflexives misused in compound subjects and objects (him/her/us/them, not -self)."""
    frame, role = rng.choice(_REFL_COMP)
    key = rng.choice(["he", "she", "we", "they"])
    subj, obj, poss, refl = _PRON_SETS[key]
    name = rng.choice(NAMES)
    text = frame.format(N=name) + "."
    if role == "object":
        correct = (obj, f"Correct. The pronoun is an object, so '{obj}' is needed; a reflexive is wrong "
                        "because the subject is someone else.")
        ds = [(refl, f"'{refl}' is reflexive; it needs '{subj}' as the subject of the same clause."),
              (subj, f"'{subj}' is subjective case, but the pronoun is an object here."),
              (poss if poss != obj else ("hers" if key == "she" else poss),
               "A possessive cannot be the object here.")]
        if poss == obj:
            ds[2] = ("hers", "A possessive cannot be the object here.")
    else:
        correct = (subj, f"Correct. The pronoun is part of the subject, so the subjective '{subj}' is needed.")
        ds = [(refl, "A reflexive pronoun can never be a subject."),
              (obj, f"'{obj}' is objective case, but the pronoun is part of the subject."),
              (poss if poss != obj else ("hers" if key == "she" else poss), "A possessive cannot be the subject.")]
        if poss == obj:
            ds[2] = ("hers", "A possessive cannot be the subject.")
    if difficulty != "easy":
        text = rng.choice(["In the end, ", "To nobody's surprise, ", "As planned, "]) + soft_low(text)
    if difficulty == "hard":
        text = text + " " + rng.choice(["No one objected.", "The announcement came on Friday.",
                                        "The decision was final."])
    return build(rng, fill(text, conv_stem(rng)), correct, ds, subskill="pronouns",
                 explanation=("A reflexive pronoun ('himself', 'ourselves') is used only when the subject "
                              "acts on itself; in a compound subject or object, use the plain subjective or "
                              "objective form."),
                 tags=["conventions", "pronouns", "reflexive-compound"])


# =========================================================================== #
# v2.1 ADDITIONS — MODIFIERS
# =========================================================================== #
_MODIFIERS.extend([
    ("Soaked by the sudden downpour,", "the hikers", "the trail", "the map", "the afternoon",
     "took shelter under a ledge", "The forecast had promised sun.", "The rain stopped within an hour."),
    ("Restored by local volunteers,", "the carousel", "the children", "the riders", "the summer",
     "reopened in June", "The carousel had sat idle for a decade.", "Lines formed on the first day."),
    ("Known for her patience,", "the teacher", "the lesson", "the classroom", "the bell",
     "waited for every hand to go down", "The class was unusually restless.", "The quiet lasted the rest of the hour."),
    ("Forged from a single piece of iron,", "the gate", "the blacksmith", "the garden", "the century",
     "has never needed repair", "The estate dates from the 1700s.", "It still swings without a sound."),
    ("Tired of the long commute,", "Samir", "the train", "the office", "the schedule",
     "moved closer to the city", "The trip took ninety minutes each way.", "He now walks to work."),
    ("Praised by every critic,", "the novel", "the author", "the readers", "the prize",
     "sold out its first printing in a week", "The publisher had printed only a few thousand copies.", "A second printing followed."),
    ("Left in the sun all afternoon,", "the chocolate", "the picnic", "the children", "the basket",
     "melted into a puddle", "Nobody had thought to pack a cooler.", "The sandwiches survived."),
    ("Written in haste,", "the letter", "the clerk", "the office", "the deadline",
     "contained three spelling errors", "The deadline fell on a Friday.", "The errors were caught the next morning."),
    ("Warned about the ice,", "the drivers", "the road", "the bridge", "the night",
     "slowed to a crawl", "A cold front had arrived at dusk.", "No accidents were reported."),
    ("Fed twice a day,", "the goats", "the farmer", "the barn", "the winter",
     "grew fat by spring", "The hay came from the upper field.", "The kids were born in April."),
    ("Carved from a single log,", "the canoe", "the carver", "the river", "the village",
     "weighs less than fifty pounds", "The log came from a fallen cedar.", "It has crossed the lake many times."),
    ("Alarmed by the smoke,", "the neighbors", "the fire", "the kitchen", "the alarm",
     "called the fire department", "The smoke turned out to be burnt toast.", "Everyone laughed about it later."),
    ("Delayed by fog,", "the ferries", "the lighthouse", "the harbor", "the gulls",
     "ran two hours late", "A thick fog settled over the bay at dawn.", "The last boat left after dark."),
    ("Hoping to attract younger readers,", "the magazine", "the readers", "the cover", "the newsstand",
     "redesigned its cover", "Sales had slipped for three years.", "Subscriptions rose that fall."),
    ("Perched on the cliff,", "the lighthouse", "the sailors", "the waves", "the storm",
     "can be seen for twenty miles", "The cliff rises three hundred feet above the surf.", "Its lamp still turns each night."),
    ("Weakened by years of flooding,", "the old pier", "the fishermen", "the tide", "the forecast",
     "was finally torn down", "The pier had stood since 1902.", "A new one opened the next summer."),
    ("Grateful for the rain,", "the farmers", "the fields", "the crops", "the forecast",
     "postponed the irrigation", "The spring had been the driest in decades.", "The barley recovered within weeks."),
    ("Stacked to the ceiling,", "the boxes", "the movers", "the hallway", "the afternoon",
     "blocked the only window", "The archive had run out of shelf space.", "Volunteers sorted them over the winter."),
    ("Famous for its sourdough,", "the bakery", "the customers", "the street", "the morning",
     "sells out by ten", "The shop has stood on Elm Street since 1962.", "Regulars arrive before the doors open."),
    ("Nervous before the audition,", "Chloe", "the violin", "the judges", "the hall",
     "practiced the opening bars one more time", "The audition was held in the old concert hall.", "She won the seat."),
    ("Hidden by tall grass,", "the stone marker", "the hikers", "the ranger", "the summer",
     "went unnoticed for years", "The marker dates from the first survey of the valley.", "A ranger found it last July."),
    ("Rebuilt after the fire,", "the barn", "the farmer", "the horses", "the winter",
     "now has a metal roof", "Lightning struck the old barn in August.", "The horses moved back in by spring."),
    ("Impressed by the design,", "the judges", "the bridge", "the drawings", "the ceremony",
     "awarded first prize to the students", "The competition drew entries from six schools.", "The bridge will be built next year."),
])
_MOD_OPENINGS.extend([
    ("Worried about the forecast", "With the forecast being a worry to them",
     "Being that the forecast was worrying", "They worried about the forecast",
     "the organizers moved the concert indoors"),
    ("Praised by every critic", "Having praised it, every critic",
     "With every critic's praise of it", "Every critic praised it",
     "the novel sold out in a week"),
    ("Fed twice a day", "Being fed by the farmer twice a day by him",
     "With twice-daily feedings from the farmer", "The farmer fed them twice a day",
     "the goats grew fat by spring"),
    ("Alarmed by the smoke", "Because the smoke was alarming to them",
     "With smoke alarming them", "The smoke alarmed them",
     "the neighbors called the fire department"),
    ("Known for her patience", "With her patience being well known",
     "Being that she was known for patience", "She was known for her patience",
     "the teacher waited for the room to settle"),
    ("Carved from a single log", "Having carved it from a single log",
     "With its carving from a single log by the maker", "The maker carved it from a single log",
     "the canoe weighs less than fifty pounds"),
    ("Delayed by fog", "With fog delaying them for hours",
     "Being that there was fog that morning", "Fog delayed them for hours",
     "the ferries ran two hours late"),
    ("Perched on the cliff", "With its perch being on the cliff",
     "Having been perched there by its builders", "Its builders perched it on the cliff",
     "the lighthouse can be seen for twenty miles"),
    ("Nervous before the audition", "With her nerves before the audition",
     "Being that she was nervous", "She was nervous before the audition",
     "Chloe practiced the opening bars once more"),
    ("Impressed by the design", "Having impressed them with the design",
     "With the design being impressive to them", "The design impressed them",
     "the judges awarded first prize to the students"),
    ("Rebuilt after the fire", "After the farmer rebuilt it following the fire",
     "With its rebuilding after the fire by the farmer", "The farmer rebuilt it after the fire",
     "the barn now has a metal roof"),
    ("Grateful for the rain", "With gratitude for the rain being theirs",
     "Being that the rain was welcome", "The rain was welcome to them",
     "the farmers postponed the irrigation"),
])

_ONLY = [
    ("Of the ten questions on the quiz, Maya answered three.", "In other words, Maya ___ three questions.",
     "answered only", "only answered", "answered three only of the", "only three answered"),
    ("The museum opens on Saturdays and no other day.", "That is, the museum ___ on Saturdays.",
     "opens only", "only opens", "opens on only", "only Saturdays opens"),
    ("The recipe calls for one egg, not two.", "Put another way, the recipe ___ one egg.",
     "calls for only", "only calls for", "calls only for", "only one calls for"),
    ("Nearly every seat was taken; a handful were empty.", "In other words, the hall was ___ full.",
     "almost", "almost not", "fully almost", "nearly not"),
    ("The ferry crosses to the island and nowhere else.", "That is, the ferry ___ to the island.",
     "crosses only", "only crosses", "crosses to only", "only to crosses"),
    ("Of the five bridges, two are open to trucks.", "In other words, ___ two bridges are open to trucks.",
     "only", "two only", "only to", "just only"),
    ("The lab's budget covers equipment, but nothing else.", "Put simply, the budget ___ equipment.",
     "covers only", "only covers", "covers only for", "only equipment covers"),
    ("Theo has read the first chapter and no more.", "In other words, Theo has ___ the first chapter.",
     "read only", "only read", "read only of", "only of read"),
    ("The bakery sells rye bread on Fridays and on no other day.", "That is, the bakery ___ on Fridays.",
     "sells rye bread only", "only sells rye bread", "sells only rye bread", "only on sells rye bread"),
    ("Two of the twelve divers reached the lower deck.", "Put another way, ___ two divers reached the lower deck.",
     "only", "two only", "only of", "just only"),
    ("The telescope can be used by staff and by nobody else.", "In other words, the telescope ___ by staff.",
     "can be used only", "only can be used", "can only be used by only", "can be used by only staff"),
    ("Nearly all the tickets were sold; a dozen remained.", "That is, the concert was ___ sold out.",
     "almost", "almost not", "nearly not", "not almost"),
]


@family(fill_in=True, small_space=True)
def mod_only(rng, difficulty):
    """Place 'only'/'almost' next to the word it limits (meaning fixed by a context sentence)."""
    context, frame, right, w1, w2, w3 = rng.choice(_ONLY)
    correct = (right, "Correct. The limiting word sits directly before the word it limits, matching "
                      "the meaning of the first sentence.")
    ds = [(w1, "Placed here, the limiting word modifies the verb, suggesting that nothing else was done."),
          (w2, "This placement is unidiomatic and does not express the intended limit."),
          (w3, "This word order is ungrammatical.")]
    text = f"{context} {frame}"
    if difficulty == "hard":
        text = text + " " + rng.choice(["The distinction matters.", "Nobody disputes the figure.",
                                        "The point is easy to miss."])
    stem = rng.choice(["Which choice completes the second sentence so that it matches the meaning of the first?",
                       conv_stem(rng)])
    return build(rng, fill(text, stem), correct, ds, subskill="modifiers",
                 explanation=("Words like 'only' and 'almost' limit whatever comes right after them; put "
                              "them directly before the word the meaning calls for."),
                 tags=["conventions", "modifiers", "only-placement"], est=50)


_PASSIVE_DANGLE = [
    ("Having finished the exam,", "the students handed in their papers",
     "the papers were handed in by the students", "the papers were collected",
     "their papers having been handed in"),
    ("After reviewing the evidence,", "the jury reached a verdict",
     "a verdict was reached by the jury", "a verdict was announced",
     "the verdict was reached"),
    ("To reach the summit before noon,", "the climbers left camp at four",
     "camp was left at four by the climbers", "an early start was needed",
     "the camp was abandoned at four"),
    ("While repairing the roof,", "the carpenter found a wasp nest",
     "a wasp nest was found by the carpenter", "a wasp nest was discovered",
     "there was a wasp nest found"),
    ("Hoping to save money,", "the family canceled the trip",
     "the trip was canceled by the family", "the trip was called off",
     "the cancellation of the trip was decided"),
    ("Before entering the archive,", "visitors must sign the register",
     "the register must be signed by visitors", "the register must be signed",
     "signing the register is required"),
    ("Using a borrowed telescope,", "Hana spotted the comet first",
     "the comet was spotted first by Hana", "the comet was seen first",
     "the first sighting of the comet was Hana's"),
    ("After tasting the sauce,", "the chef added more salt",
     "more salt was added by the chef", "more salt was needed",
     "the sauce was given more salt"),
    ("Upon hearing the alarm,", "the crew secured the hatches",
     "the hatches were secured by the crew", "the hatches were closed",
     "securing the hatches was done by the crew"),
    ("While walking the dog,", "Omar noticed the broken streetlight",
     "the broken streetlight was noticed by Omar", "the streetlight was found broken",
     "the broken streetlight came to Omar's attention"),
    ("After checking the tide tables,", "the captain delayed the crossing",
     "the crossing was delayed by the captain", "the crossing was postponed",
     "a delay of the crossing was decided"),
    ("Having mapped the caves,", "the divers published their survey",
     "the survey was published by the divers", "the survey was released",
     "the publication of the survey followed"),
    ("To protect the seedlings,", "the gardeners covered the beds",
     "the beds were covered by the gardeners", "the beds were covered",
     "covers were placed on the beds"),
    ("While tuning the organ,", "the technician found a cracked pipe",
     "a cracked pipe was found by the technician", "a cracked pipe was discovered",
     "there was a cracked pipe found"),
]


@family(fill_in=True, small_space=True)
def mod_passive_dangle(rng, difficulty):
    """Passive main clauses leave an opening modifier dangling; options are whole clauses."""
    opening, right, w_by, w_agentless, w_other = rng.choice(_PASSIVE_DANGLE)
    doer = right.split()[0] if not right.startswith("the ") else " ".join(right.split()[:2])
    correct = (right, f"Correct. '{doer}' is the one who {opening.strip(',').lower()}, and it sits right after the modifier.")
    ds = [(w_by, "The passive puts the wrong noun next to the modifier, so the phrase dangles."),
          (w_agentless, "With no doer named, the opening phrase has nothing it can logically describe."),
          (w_other, "This rewording still fails to place the doer of the opening action next to the phrase.")]
    text = f"{opening} ___."
    if difficulty != "easy":
        text = rng.choice(["The rest of the story is short. ", "Here is what happened next. ",
                           "The sequence was simple. "]) + text
    if difficulty == "hard":
        text = text + " " + rng.choice(["No one was surprised.", "The rest followed quickly.",
                                        "It was over in minutes."])
    return build(rng, fill(text, conv_stem(rng)), correct, ds, subskill="modifiers",
                 explanation=("Rewriting the main clause in the passive moves the doer away from the opening "
                              "phrase, which then dangles; keep the doer as the subject."),
                 tags=["conventions", "modifiers", "passive-dangling"], est=55)


_SQUINT = [
    ("Riding a bicycle", "quickly", "improves fitness", "the benefit comes fast",
     "Riding a bicycle improves fitness quickly.", "Riding a bicycle quickly improves fitness.",
     "Quickly riding a bicycle improves fitness.", "Riding quickly a bicycle improves fitness."),
    ("Students who review their notes", "often", "pass the exam", "the reviewing is frequent",
     "Students who often review their notes pass the exam.", "Students who review their notes often pass the exam.",
     "Students who review their notes pass often the exam.", "Often students who review their notes pass the exam."),
    # Time phrases at the END of "told X to rest on Friday" still attach to either verb,
    # so these items key the fronted version (the telling/saying/promising time).
    ("The coach told the players", "on Friday", "to rest", "the telling happened on Friday",
     "On Friday the coach told the players to rest.", "The coach told the players on Friday to rest.",
     "The coach told the players to rest on Friday.", "The coach told on Friday the players to rest."),
    # "Walking the trail slowly reveals..." is itself squinting: the adverb goes first.
    ("Walking the trail", "slowly", "reveals its beauty", "the walking is slow",
     "Slowly walking the trail reveals its beauty.", "Walking the trail slowly reveals its beauty.",
     "Walking the trail reveals its beauty slowly.", "Walking slowly the trail reveals its beauty."),
    ("The manager said", "on Monday", "the store would close", "the announcement was made on Monday",
     "On Monday the manager said the store would close.", "The manager said on Monday the store would close.",
     "The manager said the store would close on Monday.", "The manager said the store on Monday would close."),
    ("Teachers who grade essays", "carefully", "help their students", "the grading is careful",
     "Teachers who carefully grade essays help their students.", "Teachers who grade essays carefully help their students.",
     "Teachers who grade essays help carefully their students.", "Carefully teachers who grade essays help their students."),
    ("Nina promised", "after the concert", "to call", "the promise was made after the concert",
     "After the concert Nina promised to call.", "Nina promised after the concert to call.",
     "Nina promised to call after the concert.", "Nina promised to after the concert call."),
]


@family(fill_in=False, small_space=True)
def mod_squinting(rng, difficulty):
    """A squinting modifier; the intended meaning is stated and only one sentence conveys it."""
    base, mod, rest, intent, good, squint, other, bad = rng.choice(_SQUINT)
    correct = (good, f"Correct. '{mod}' sits where it can modify only the intended idea ({intent}).")
    ds = [(squint, f"Placed between two verbs, '{mod}' 'squints': it could modify either one."),
          (other, f"This placement makes '{mod}' modify the wrong part of the sentence."),
          (bad, "This word order is awkward or ungrammatical.")]
    prompt = (f"A writer wants to say that {intent}.\n\n"
              + rng.choice(["Which choice places the modifier so that the sentence has only that meaning?",
                            "Which version of the sentence expresses that meaning unambiguously?"]))
    return build(rng, prompt, correct, ds, subskill="modifiers",
                 explanation=("A modifier placed between two things it could describe is ambiguous; move "
                              "it next to the one word or phrase it should modify."),
                 tags=["conventions", "modifiers", "squinting"], est=55)


# =========================================================================== #
# v2.1 ADDITIONS — TRANSITIONS
# =========================================================================== #
_TRANS_ITEMS.extend([
    ("The clinic added evening hours in March.", "fewer patients now visit the emergency room.", "cause"),
    ("The tunnel shortens the drive by an hour.", "most trucks still use the mountain road.", "contrast"),
    ("The robot's arm jammed in the first round.", "the team finished in the top ten.", "contrast"),
    ("The lighthouse was automated decades ago.", "its lens is cleaned by hand every spring.", "contrast"),
    ("The bakery's rye loaf sold out by noon.", "the owners doubled the batch the next day.", "cause"),
    ("The archive's letters were scanned last year.", "researchers in three countries have already cited them.", "cause"),
    ("The marsh lost half its area after 1990.", "bird counts have risen since the grasses were replanted.", "contrast"),
    ("The telescope's mirror was replaced in 2021.", "its resolution doubled.", "cause"),
    ("Many desert plants store water in their stems.", "the barrel cactus can hold a gallon.", "example"),
    ("The orchestra rehearsed the finale a dozen times.", "the performance still ran long.", "contrast"),
    ("The choir auditioned new members in September.", "it added a second rehearsal night.", "sequence"),
    ("Kite festivals draw crowds in many coastal towns.", "the one in Harlan fills every hotel.", "example"),
    ("The ferry company added a third boat.", "weekend crossings carry twice as many bicycles.", "cause"),
    ("The mill employed half the town in the 1950s.", "it closed in 1983.", "contrast"),
    ("The new filter removes nearly all the sediment.", "the water still tastes faintly of iron.", "contrast"),
    ("The glacier has retreated a mile since 1950.", "it has thinned by nearly two hundred feet.", "addition"),
])

# (paragraph 1, paragraph 2 without its opening transition, relation)
_TRANS_PARA = [
    ("For most of the twentieth century, the harbor town depended on a single cannery. The plant employed "
     "nearly half the adults in town, and its whistle set the rhythm of every day.",
     "the cannery closed in 2003, and the town had to reinvent itself. Today its warehouses hold cafés, "
     "a climbing gym, and a bicycle repair shop.", "contrast"),
    ("Desert tortoises spend most of the year underground. Their burrows stay cool through the hottest "
     "afternoons and hold warmth on winter nights.",
     "dozens of other species shelter in those burrows during the hottest months. Biologists call the tortoise an engineer "
     "of its ecosystem.", "cause"),
    ("The school garden began as a single raised bed behind the cafeteria. Each spring a new class added "
     "another bed, and by the fifth year the beds filled the whole courtyard.",
     "the garden now supplies the cafeteria with salad greens from April to October. A greenhouse is "
     "planned for next year.", "cause"),
    ("Early radio operators had to master Morse code. The code is slow by modern standards, and learning "
     "it took months of nightly practice.",
     "it can be sent with almost any equipment, even a flashlight. Amateur operators still practice it "
     "today for exactly that reason.", "contrast"),
    ("The clock tower's mechanism dates from 1884. It must be wound by hand twice a week, a job that "
     "takes a volunteer up two hundred stairs.",
     "the tower keeps time to within a few seconds a month. The volunteer who winds it has done so for "
     "thirty years.", "contrast"),
    ("Lichens grow on bare rock where little else survives. They release weak acids that slowly break the "
     "rock's surface into grains.",
     "they help create the first thin layer of soil on new ground. Mosses and grasses follow within a few "
     "decades.", "cause"),
    ("Vanilla comes from the pod of an orchid. Outside its native range, the orchid has no natural "
     "pollinator, and its flowers open for only a single day.",
     "farmers must pollinate each flower by hand during that one day. This is one reason real vanilla "
     "costs so much.", "cause"),
    ("The library's photograph archive was nearly lost in a flood. Volunteers dried each print by hand "
     "over a long winter.",
     "they scanned every image so that the collection could be viewed online. The digital archive now "
     "receives thousands of visits a month.", "sequence"),
    ("The new stadium was designed to use as little water as possible. Rain is collected from the roof and "
     "stored in tanks beneath the stands.",
     "the field is irrigated with recycled water from the concession stands. Water use has fallen by half "
     "since the stadium opened.", "addition"),
    ("Many migrating birds travel at night, navigating by the stars. Bright city lights can draw them off "
     "course and into windows.",
     "several cities now dim their skylines during peak migration. Early counts suggest far fewer "
     "collisions.", "cause"),
    ("Amara's grandmother kept bees behind the house and let Amara help with the harvest every August. "
     "By ten, Amara could lift a frame without gloves.",
     "she started a hive of her own at fourteen. She now sells honey at the Saturday market.", "sequence"),
    ("The city's oldest bridge was built for horse carts. Engineers reinforced it twice last century, "
     "adding steel beneath the original stone.",
     "heavy trucks are still banned from crossing it. A second bridge now carries most freight.", "contrast"),
]


@family(fill_in=True, small_space=True)
def trans_paragraph(rng, difficulty):
    """Transition opening a second paragraph."""
    p1, p2, rel = rng.choice(_TRANS_PARA)
    word = rng.choice(_TRANS_BANK[rel])
    used = {word.lower()}
    ds = _trans_distractors(rng, rel, difficulty, used)
    correct = (word, f"Correct. The second paragraph stands in {_TRANS_REL_NAMES[rel]} to the first.")
    text = f"{p1}\n\n___, {p2}"
    stem = rng.choice(["Which transition most logically begins the second paragraph?",
                       "Which choice completes the text with the most logical transition?"])
    # keep the stem as the final paragraph: the paragraph break inside the text is fine
    return build(rng, fill(text, stem), correct, ds, subskill="logical_transitions", qtype="multiple_choice",
                 explanation=(f"Compare the main idea of each paragraph: the second expresses "
                              f"{_TRANS_REL_NAMES[rel]} relative to the first."),
                 tags=["expression", "transitions", "paragraph"], est=70)


# (sentence 1, sentence 2 that simply continues with no logical connector)
_TRANS_DELETE = [
    ("The bakery opens at six.", "The first customers are usually fishermen heading to the docks."),
    ("The trail begins behind the ranger station.", "A wooden sign marks the first turn."),
    ("The museum's new wing holds the textile collection.", "A tapestry of woven silk hangs at the far end."),
    ("Nadia restores antique clocks in a small workshop.", "She keeps a drawer of spare parts sorted by century."),
    ("The orchestra toured three cities over spring break.", "Recordings of the concerts are posted online."),
    ("The coral nursery sits in a shallow lagoon.", "Divers check the frames twice a month."),
    ("The city archive holds thousands of letters from the 1890s.", "Volunteers transcribe them one page at a time."),
    ("The kite festival takes place on the first Saturday in June.", "Prizes go to the largest kite and the most unusual design."),
    ("The robotics club meets after school on Tuesdays.", "Its next competition is in March."),
    ("The lighthouse was built in 1874.", "A keeper's cottage stands beside it."),
    ("The ferry crosses to the island four times a day.", "Tickets are sold at a booth on the pier."),
    ("The olive grove covers the hillside above the village.", "Farmers harvest the fruit by hand with long rakes."),
]
_DELETE_TEXT = "DELETE it"


@family(fill_in=False, small_space=True)
def trans_delete(rng, difficulty):
    """Decide whether a bracketed transition should be kept, replaced, or deleted."""
    delete_case = rng.random() < 0.5
    if delete_case:
        s1, s2 = rng.choice(_TRANS_DELETE)
        shown = rng.choice(["Therefore", "However", "Consequently"] if difficulty == "easy"
                           else ["Therefore", "However", "For example", "Consequently", "Nevertheless"])
        # Only relations a plain continuation clearly lacks: an addition word
        # ("Moreover") or a sequence word ("Next") could arguably stay.
        others = [w for r in ("contrast", "cause", "example") for w in _TRANS_BANK[r] if w != shown]
        rng.shuffle(others)
        correct = (_DELETE_TEXT, "Correct. The second sentence simply adds a detail; no cause, contrast, or "
                                 "example is being signaled, so any transition word is misleading.")
        ds = []
        for w in others[:3]:
            rel = [r for r in _TRANS_BANK if w in _TRANS_BANK[r]][0]
            ds.append((f"{w},", f"'{w}' signals {_TRANS_REL_NAMES[rel]}, a relationship the two sentences do not have."))
        expl = ("Transitions must signal a real relationship between ideas; when the second sentence merely "
                "continues the description, no transition is needed.")
    else:
        # Keep-a-transition items use contrasts only: dropping the connector
        # from a cause/addition/example pair still reads acceptably, which made
        # "DELETE it" defensible too.
        s1, s2, rel = rng.choice([t for t in _TRANS_ITEMS if t[2] == "contrast"])
        word = rng.choice(_TRANS_BANK[rel])
        shown = rng.choice([w for r in _TRANS_DISTRACTOR_RELS[rel] for w in _TRANS_BANK[r]])
        used = {word.lower(), shown.lower()}
        ds = _trans_distractors(rng, rel, difficulty, used, fmt=lambda w: f"{w},")[:2]
        ds.append((_DELETE_TEXT, f"Deleting the transition hides the {_TRANS_REL_NAMES[rel]} between the sentences."))
        correct = (f"{word},", f"Correct. The second sentence expresses {_TRANS_REL_NAMES[rel]}, which '{word}' signals.")
        expl = (f"The second sentence stands in {_TRANS_REL_NAMES[rel]} to the first, so a transition that "
                "signals that relationship should be kept.")
    prompt = (f"{s1} [{shown},] {low(s2)}\n\nThe writer is considering the bracketed transition. "
              "Which choice is best?")
    return build(rng, prompt, correct, ds, subskill="logical_transitions", qtype="multiple_choice",
                 explanation=expl, tags=["expression", "transitions", "delete"], est=55)


_CONCESSION = [
    ("the trail is short", "it climbs nearly two thousand feet"),
    ("the museum is free", "it relies entirely on donations"),
    ("the recipe looks simple", "the sauce took three attempts to get right"),
    ("the novel received glowing reviews", "sales were disappointing"),
    ("the team lost its first six games", "it finished with a winning record"),
    ("the lighthouse was automated in 1987", "a keeper still lives on the island"),
    ("the glacier has retreated a mile", "the valley below is greener than ever"),
    ("the forecast called for clear skies", "a thunderstorm rolled in by noon"),
    ("the bakery doubled its staff", "the lines grew even longer"),
    ("the tunnel shortens the drive by an hour", "most trucks still use the mountain road"),
]


@family(fill_in=True)
def trans_concession(rng, difficulty):
    """Concession (although/even though) vs. contrast adverbs (however) and wrong logic."""
    a, b = rng.choice(_CONCESSION)
    if difficulty == "easy" or rng.random() < 0.5:
        word = rng.choice(["Although", "Even though", "Though", "While"])
        correct = (word, f"Correct. '{word}' concedes the first point and lets the main clause contrast with it.")
        ds = [("However", "'However' is a conjunctive adverb; it cannot introduce a dependent clause "
                          "joined with a comma."),
              ("Because", "'Because' claims a cause-and-effect link that the ideas do not have."),
              ("In spite of", "'In spite of' must be followed by a noun phrase, not a full clause.")]
        text = f"___ {a}, {b}."
        expl = "A concession clause begins with a subordinator such as 'although'; 'however' cannot do that job."
    else:
        word = rng.choice(["however", "nevertheless", "even so", "still"])
        correct = (word, f"Correct. After a semicolon, the adverb '{word}' signals the contrast between two "
                         "independent clauses.")
        ds = [("although", "'although' makes the second clause dependent, which cannot follow a semicolon."),
              ("therefore", "'therefore' signals a result, but the second idea contrasts with the first."),
              ("for example", "'for example' signals an illustration, not a contrast.")]
        text = f"{cap(a)}; ___, {b}."
        expl = ("Two independent clauses joined by a semicolon take a contrast adverb; a subordinator like "
                "'although' cannot follow a semicolon.")
    if difficulty == "hard":
        text = rng.choice(["Few visitors expect it. ", "The numbers tell the story. ", "The paradox is real. "]) + text
    return build(rng, fill(text, rng.choice(_TRANS_STEMS)), correct, ds, subskill="logical_transitions",
                 qtype="multiple_choice", explanation=expl,
                 tags=["expression", "transitions", "concession"], est=50)


# =========================================================================== #
# FAMILY TABLE + LEGACY DISPATCHERS
# =========================================================================== #
FAMILIES = {
    "sentence_boundaries": {
        "easy": [bnd_join_whole, bnd_blank_junction, bnd_dependent, bnd_passage, bnd_conjunctive_adverb,
                 bnd_fragment_clause, bnd_mark_choice, bnd_splice_repair],
        "medium": [bnd_join_whole, bnd_blank_junction, bnd_conjunctive_adverb, bnd_colon, bnd_passage, bnd_dependent,
                   bnd_fragment_clause, bnd_mark_choice, bnd_splice_repair],
        "hard": [bnd_join_whole, bnd_blank_junction, bnd_conjunctive_adverb, bnd_colon, bnd_passage, bnd_dependent,
                 bnd_fragment_clause, bnd_mark_choice, bnd_splice_repair],
    },
    "subject_verb_agreement": {
        "easy": [sva_of_phrase, sva_compound, sva_indefinite, sva_inverted, sva_passage, sva_collective,
                 sva_gerund, sva_quantity],
        "medium": [sva_of_phrase, sva_compound, sva_indefinite, sva_inverted, sva_relative, sva_collective, sva_passage,
                   sva_quantity, sva_gerund, sva_either_or],
        "hard": [sva_of_phrase, sva_compound, sva_indefinite, sva_inverted, sva_relative, sva_collective, sva_passage,
                 sva_clause_options, sva_either_or, sva_quantity, sva_gerund],
    },
    "punctuation": {
        "easy": [punct_possessive, punct_its, punct_series, punct_no_comma, punct_nonrestrictive,
                 punct_hyphen, punct_quotation, punct_semicolon_list],
        "medium": [punct_possessive, punct_its, punct_nonrestrictive, punct_series, punct_passage, punct_paired,
                   punct_hyphen, punct_quotation, punct_semicolon_list, punct_dash_paren],
        "hard": [punct_possessive, punct_its, punct_nonrestrictive, punct_paired, punct_passage, punct_no_comma, punct_series,
                 punct_hyphen, punct_quotation, punct_semicolon_list, punct_dash_paren],
    },
    "pronouns": {
        "easy": [pron_compound, pron_who_whom, pron_reflexive, pron_preposition, pron_passage,
                 pron_shift, pron_reflexive_compound],
        "medium": [pron_compound, pron_who_whom, pron_preposition, pron_reflexive, pron_passage,
                   pron_shift, pron_vague, pron_reflexive_compound],
        "hard": [pron_compound, pron_who_whom, pron_preposition, pron_reflexive, pron_passage, pron_clause_options,
                 pron_shift, pron_vague, pron_reflexive_compound],
    },
    "modifiers": {
        "easy": [mod_whole_sentence, mod_blank_subject, mod_opening_phrase, mod_passage,
                 mod_only, mod_passive_dangle],
        "medium": [mod_whole_sentence, mod_blank_subject, mod_opening_phrase, mod_misplaced, mod_passage,
                   mod_only, mod_passive_dangle, mod_squinting],
        "hard": [mod_whole_sentence, mod_blank_subject, mod_opening_phrase, mod_misplaced, mod_passage,
                 mod_only, mod_passive_dangle, mod_squinting],
    },
    "transitions": {
        "easy": [trans_blank, trans_opener, trans_sentence_options, trans_sequence, trans_passage,
                 trans_paragraph, trans_concession],
        "medium": [trans_blank, trans_opener, trans_sentence_options, trans_passage, trans_sequence,
                   trans_paragraph, trans_delete, trans_concession],
        "hard": [trans_blank, trans_opener, trans_sentence_options, trans_passage, trans_sequence,
                 trans_paragraph, trans_delete, trans_concession],
    },
}


def gen_boundaries(rng: random.Random, difficulty: str = "medium"):
    return dispatch(FAMILIES["sentence_boundaries"], rng, difficulty)


def gen_sva(rng: random.Random, difficulty: str = "medium"):
    return dispatch(FAMILIES["subject_verb_agreement"], rng, difficulty)


def gen_punctuation(rng: random.Random, difficulty: str = "medium"):
    return dispatch(FAMILIES["punctuation"], rng, difficulty)


def gen_pronouns(rng: random.Random, difficulty: str = "medium"):
    return dispatch(FAMILIES["pronouns"], rng, difficulty)


def gen_modifiers(rng: random.Random, difficulty: str = "medium"):
    return dispatch(FAMILIES["modifiers"], rng, difficulty)


def gen_transition(rng: random.Random, difficulty: str = "medium"):
    return dispatch(FAMILIES["transitions"], rng, difficulty)


def pool_transitions(rng: random.Random):
    items = []
    for s1, s2, rel in _TRANS_ITEMS:
        correct_word = rng.choice(_TRANS_BANK[rel])
        distractors = _trans_distractors(rng, rel, "medium", {correct_word.lower()})
        correct = (correct_word, f"Correct. The relationship is {_TRANS_REL_NAMES[rel]}.")
        options, ci, rats = shuffle_with_correct(rng, correct, distractors)
        prompt = (f"{s1} ___, {s2}\n\nWhich transition best fits the relationship "
                  "between the two ideas?")
        items.append(mc(prompt, options, ci, rats, subskill="logical_transitions",
                        qtype="multiple_choice",
                        explanation=(f"The second sentence expresses {_TRANS_REL_NAMES[rel]} "
                                     f"relative to the first, so a {rel}-signaling "
                                     f"transition is needed."),
                        tags=["expression", "transitions"], est=50))
    return items



# --------------------------------------------------------------------------- #
# Authored pool: concision
# --------------------------------------------------------------------------- #
_CONCISION = [
    ("the meeting was postponed", "the meeting was postponed until a later time",
     "the meeting, which had been on the schedule, was put off and postponed",
     "due to the fact that of scheduling, the meeting was postponed"),
    ("the results were unexpected", "the results were unexpected and not what was expected",
     "the results, in terms of what they were, were unexpected",
     "the results were a surprise that surprised everyone unexpectedly"),
    ("she completed the project early", "she completed and finished the project early ahead of time",
     "she, being someone who works fast, completed the project early",
     "the project was completed early by her at an earlier time than expected"),
    ("the museum is free on Sundays", "the museum, on the day of Sunday, is free of charge",
     "the museum is free and costs nothing on Sundays",
     "on Sundays, which come once a week, the museum is free"),
    ("the bridge connects the two towns", "the bridge connects together the two separate towns",
     "the bridge, in terms of connection, connects the two towns",
     "the bridge joins and connects the two towns to each other"),
    ("the data clearly support the theory", "the data, which is information, clearly support the theory",
     "the data support and back up the theory in a clear and obvious way",
     "the data clearly and obviously support the theory in a clear manner"),
    ("the recipe requires three eggs", "the recipe requires a total of three eggs in number",
     "the recipe, for it to work, requires three eggs",
     "three eggs are what the recipe requires in order to be made"),
    ("the storm caused widespread damage", "the storm caused damage that was widespread and broad",
     "the storm, being severe, caused widespread damage everywhere",
     "widespread damage was the result that the storm caused"),
    ("the author revised the final chapter", "the author revised and rewrote the final last chapter",
     "the author, who wrote the book, revised the final chapter",
     "the final chapter was revised by the author who changed it"),
    ("volunteers cleaned the entire park", "volunteers cleaned the entire whole park completely",
     "volunteers, a group of people, cleaned the entire park",
     "the entire park was cleaned completely by volunteers in full"),
    ("the train arrives every hour", "the train arrives each and every single hour",
     "the train, which runs on a schedule, arrives every hour",
     "every hour is when the train arrives on an hourly basis"),
    ("the experiment confirmed the prediction", "the experiment confirmed and verified the prediction",
     "the experiment, in its results, confirmed the prediction",
     "the prediction was confirmed by the experiment which proved it true"),
    ("the new law reduced traffic", "the new law reduced and lowered the amount of traffic",
     "the new law, once passed, reduced traffic on the roads",
     "traffic was reduced by the new law that lowered it"),
    ("the lecture lasted two hours", "the lecture lasted for a duration of two hours in length",
     "the lecture, given by the professor, lasted two hours",
     "two hours is how long the lecture lasted in terms of time"),
    ("the garden attracts many butterflies", "the garden attracts and draws in many butterflies",
     "the garden, full of flowers, attracts many butterflies",
     "many butterflies are attracted to the garden that draws them"),
    ("the report omitted key details", "the report omitted and left out key important details",
     "the report, when finished, omitted key details",
     "key details were omitted and left out of the report"),
    ("the company expanded into new markets", "the company expanded and grew into new markets",
     "the company, seeking growth, expanded into new markets",
     "new markets were entered by the company as it expanded"),
    ("the path winds along the coast", "the path winds and curves along the coastline by the coast",
     "the path, which is scenic, winds along the coast",
     "along the coast is where the path winds in a curving way"),
    ("the policy improved air quality", "the policy improved and bettered the quality of the air",
     "the policy, after enactment, improved air quality",
     "air quality was improved by the policy that made it better"),
    ("the choir rehearsed twice a week", "the choir rehearsed two times a week on a weekly basis",
     "the choir, made of singers, rehearsed twice a week",
     "twice a week is when the choir rehearsed on a regular basis"),
    ("the device saves energy", "the device saves and conserves energy efficiently",
     "the device, being modern, saves energy",
     "energy is saved by the device that conserves it"),
    ("the city repaired the old roads", "the city repaired and fixed the old, aging roads",
     "the city, using its budget, repaired the old roads",
     "the old roads were repaired by the city that fixed them"),
    ("the film received strong reviews", "the film received strong and positive good reviews",
     "the film, after release, received strong reviews",
     "strong reviews were received by the film that critics liked"),
    ("the species adapts quickly", "the species adapts and adjusts quickly and fast",
     "the species, when threatened, adapts quickly",
     "quick adaptation is something the species does rapidly"),
    ("the museum reopened in May", "the museum reopened once again in the month of May",
     "the museum, after being closed, reopened in May",
     "May was the month in which the museum reopened to visitors"),
    ("the bridge is closed for repairs", "the bridge is closed and shut for repairs and fixes",
     "the bridge, which spans the river, is closed for repairs",
     "for repairs, the bridge is currently in a closed condition"),
    ("the survey reached many readers", "the survey reached and got to many different readers",
     "the survey, once distributed, reached many readers",
     "many readers are the ones whom the survey reached"),
    ("the engine runs on solar power", "the engine runs and operates on solar power from the sun",
     "the engine, which is modern, runs on solar power",
     "solar power is the source on which the engine runs"),
    ("the team practiced every morning", "the team practiced each and every single morning",
     "the team, eager to improve, practiced every morning",
     "every morning was when the team did its practicing"),
    ("the report was finished on time", "the report was finished and completed on time punctually",
     "the report, after much work, was finished on time",
     "on time is when the report ended up being finished"),
    ("the trail reopened to hikers", "the trail reopened and was opened again to hikers",
     "the trail, now cleared, reopened to hikers",
     "hikers are the people to whom the trail reopened"),
    ("the bakery lowered its prices", "the bakery lowered and reduced its prices to be cheaper",
     "the bakery, hoping for sales, lowered its prices",
     "its prices were lowered by the bakery to draw customers"),
    ("the lake froze in December", "the lake froze solid and icy in the month of December",
     "the lake, which is shallow, froze in December",
     "December was the time during which the lake froze"),
    ("the author thanked her editor", "the author thanked and expressed gratitude to her editor",
     "the author, in her speech, thanked her editor",
     "her editor was the person whom the author thanked"),
    ("the school added new courses", "the school added and introduced brand-new courses",
     "the school, responding to demand, added new courses",
     "new courses are what the school decided to add"),
    ("the garden needs little water", "the garden needs only a little bit of minimal water",
     "the garden, full of cacti, needs little water",
     "little water is all that the garden actually needs"),
    ("the festival drew large crowds", "the festival drew and attracted large, sizable crowds",
     "the festival, held downtown, drew large crowds",
     "large crowds were drawn to the festival that weekend"),
    ("the printer jammed again", "the printer jammed and got stuck yet again once more",
     "the printer, an old model, jammed again",
     "again is when the printer experienced another jam"),
    ("the coach praised the rookie", "the coach praised and complimented the new rookie player",
     "the coach, pleased with the win, praised the rookie",
     "the rookie was the one whom the coach chose to praise"),
    ("the road curves near the cliff", "the road curves and bends sharply near the steep cliff",
     "the road, which is narrow, curves near the cliff",
     "near the cliff is the place where the road curves"),
]


def pool_concision(rng: random.Random):
    items = []
    # Order easy -> hard: longer ideas with longer (subtler) wordy options read
    # harder, so the in-order tier draw ramps in difficulty.
    ordered = sorted(
        _CONCISION,
        key=lambda it: len(it[0]) + max(len(w) for w in it[1:]),
    )
    for concise, *wordy in ordered:
        correct = (concise[0].upper() + concise[1:] + ".",
                   "Correct. This version states the idea without redundancy or padding.")
        distractors = [(w[0].upper() + w[1:] + ".",
                        "Wordy: this repeats ideas or adds words that don't add meaning.")
                       for w in wordy]
        options, ci, rats = shuffle_with_correct(rng, correct, distractors)
        prompt = ("Which choice best states the idea while following the convention "
                  "of concision (no redundancy or wordiness)?")
        items.append(mc(prompt, options, ci, rats, subskill="eliminate_redundancy",
                        qtype="multiple_choice",
                        explanation=("The concise choice keeps the meaning while "
                                     "removing repeated ideas and filler phrases."),
                        tags=["expression", "concision"], est=45))
    return items


# --------------------------------------------------------------------------- #
# Authored pool: rhetorical synthesis
# --------------------------------------------------------------------------- #
# (topic, notes[list], goal, correct_sentence, distractors[list])
# Each distractor is a full sentence of length comparable to the key, but it
# fails the stated goal (wrong emphasis, mere listing, or an off-goal point).
_SYNTHESIS = [
    ("a hummingbird study",
     ["Hummingbirds beat their wings up to 80 times per second.",
      "They have the fastest metabolism of any bird.",
      "A researcher recorded their heart rates in the wild."],
     "emphasize the birds' extreme physiology",
     "With wings beating up to 80 times per second and the fastest metabolism of any bird, hummingbirds push avian physiology to its limits.",
     ["A researcher who recorded hummingbirds' heart rates in the wild found that they have the fastest metabolism of any bird.",
      "Although hummingbirds beat their wings quickly, the study focused mainly on how a researcher recorded their heart rates outdoors.",
      "Hummingbirds, which a researcher studied in the wild, are among the many bird species that beat their wings to stay aloft."]),
    ("a coastal restoration project",
     ["The marsh lost 40% of its area since 1990.",
      "Volunteers replanted native grasses in 2023.",
      "Bird sightings rose the following spring."],
     "present the project's result",
     "After volunteers replanted native grasses, bird sightings in the marsh rose the following spring.",
     ["Having lost 40% of its area since 1990, the marsh had clearly declined long before volunteers ever arrived to help.",
      "In 2023, a group of dedicated volunteers who care deeply about the coast decided to replant native grasses in the marsh.",
      "The marsh, which had lost much of its area since 1990, is the kind of place where native grasses can be replanted."]),
    ("a telescope upgrade",
     ["The old mirror was 2 meters wide.",
      "The new mirror is 4 meters wide.",
      "The upgrade doubled the telescope's resolution."],
     "highlight the improvement",
     "By replacing the 2-meter mirror with a 4-meter one, the upgrade doubled the telescope's resolution.",
     ["The telescope, once fitted with a 2-meter mirror, was changed at some point so that it now carries a wider mirror instead.",
      "The old 2-meter mirror was fairly small, which is one of several reasons astronomers decided the telescope was due for work.",
      "Astronomers rely on large telescopes like this one to gather light and study faint, distant objects across the night sky."]),
    ("a community garden",
     ["The garden has 30 plots.",
      "Residents grow vegetables and herbs.",
      "Surplus produce is donated to a food bank."],
     "explain how the garden benefits others",
     "Beyond its 30 plots of vegetables and herbs, the garden donates surplus produce to a local food bank.",
     ["Across its 30 plots, the residents of the neighborhood grow a wide variety of fresh vegetables and fragrant herbs.",
      "The garden is divided into 30 separate plots, each tended by a different resident who grows their own produce.",
      "A food bank, which gathers and distributes donated food, is one of many organizations that serve people in need."]),
    ("an ancient road discovery",
     ["Archaeologists found a stone road buried under a field.",
      "The road is about 2,000 years old.",
      "It connected two former market towns."],
     "introduce the discovery to readers",
     "Archaeologists have uncovered a 2,000-year-old stone road, buried beneath a field, that once linked two market towns.",
     ["The road that the archaeologists studied, now roughly 2,000 years old, must have seemed quite modern when it was first built.",
      "Long ago, the stone road connected two market towns whose traders likely carried goods back and forth along its surface.",
      "Archaeologists, the scientists who study the human past, often spend years carefully excavating sites buried under fields."]),
    ("a recycling program",
     ["The town added curbside glass pickup.",
      "Glass recycling rose 60% in one year.",
      "Landfill waste dropped noticeably."],
     "emphasize the program's impact",
     "After the town added curbside glass pickup, glass recycling jumped 60% and landfill waste dropped noticeably.",
     ["The town decided to add curbside glass pickup so that residents would no longer need to haul their bottles to a center.",
      "Glass recycling in the town rose by 60% over a single year, a figure that the program's organizers found encouraging.",
      "Recycling, the process of collecting used materials so they can be remade, is practiced by many towns in different ways."]),
    ("a language preservation effort",
     ["Only 200 fluent speakers of the language remain.",
      "A school began teaching it to children in 2020.",
      "Enrollment has grown each year since."],
     "convey both the threat and the response",
     "With only 200 fluent speakers left, a school began teaching the language to children in 2020, and enrollment has grown every year since.",
     ["In 2020 a school began teaching the language to children, and the number enrolling in those classes has grown each year.",
      "With only about 200 fluent speakers still living, the language is in real danger of disappearing within a generation.",
      "A language, which is a shared system that lets a community communicate, can fade once its fluent speakers grow few."]),
    ("a solar farm",
     ["The farm covers 50 acres.",
      "It powers about 9,000 homes.",
      "It replaced a closed coal plant."],
     "stress the shift from fossil fuels",
     "Built on the site of a closed coal plant, the 50-acre solar farm now powers about 9,000 homes.",
     ["Stretching across 50 acres, the solar farm is large enough to supply electricity to roughly 9,000 nearby homes.",
      "The solar farm, which now occupies 50 acres of open land, delivers enough power for about 9,000 households in the area.",
      "Solar farms such as this one generate electricity by capturing sunlight with rows of panels spread across the ground."]),
    ("a bicycle-sharing launch",
     ["The city placed 500 bikes at 60 stations.",
      "Riders took 12,000 trips in the first week.",
      "Most trips replaced short car rides."],
     "show that the program changed how people travel",
     "In its first week, the 500-bike program logged 12,000 trips, most of them replacing short car rides.",
     ["To launch the program, the city carefully placed a fleet of 500 bicycles at 60 docking stations across the downtown area.",
      "In just its first week of operation, the new bike-sharing program recorded an impressive total of 12,000 separate trips.",
      "Bicycles, a common and affordable form of city transportation, are used by commuters and visitors alike in many places."]),
    ("a coral nursery",
     ["Divers grow coral fragments on underwater frames.",
      "Fragments are replanted on damaged reefs.",
      "Survival rates exceed 70%."],
     "explain the method and its success",
     "Divers grow coral fragments on underwater frames and replant them on damaged reefs, where more than 70% survive.",
     ["More than 70% of the transplanted coral fragments survive, a rate the nursery's divers consider a genuine success.",
      "Working below the surface, divers carefully grow small coral fragments on specially built underwater frames.",
      "Coral reefs, which shelter a quarter of all marine species, are among the most important ecosystems in the ocean."]),
    ("a library renovation",
     ["The library added a quiet study wing.",
      "Weekly visits rose by a third.",
      "Evening hours were extended."],
     "report the effect of the changes",
     "After the library added a quiet study wing and extended evening hours, weekly visits rose by a third.",
     ["As part of the renovation, the library added a brand-new quiet study wing and kept its doors open later into the evening.",
      "Weekly visits to the library rose by a full third, a jump the staff were pleased to see after months of construction.",
      "A public library, which lends books and other materials at no charge, serves readers of every age in its community."]),
    ("a wetland bird census",
     ["Counters logged 84 species in spring.",
      "That is up from 61 a decade ago.",
      "Restored marshland likely drove the gain."],
     "highlight the increase over time",
     "Spring counts have climbed from 61 species a decade ago to 84 today, a gain likely driven by restored marshland.",
     ["This spring, the volunteer counters carefully logged a total of 84 different bird species across the wetland.",
      "The gain in the number of species is most likely the result of the marshland that was restored in recent years.",
      "A census, which is a careful count of a population, is repeated regularly so that changes can be tracked over time."]),
    ("a 3D-printed housing project",
     ["A printer builds each wall in under 24 hours.",
      "Material costs are roughly half those of brick.",
      "The first ten homes were occupied this year."],
     "emphasize speed and cost",
     "Printing each wall in under a day and at roughly half the material cost of brick, the project delivered its first ten homes this year.",
     ["The very first ten homes built by the project were finished and occupied by families earlier this year.",
      "Using a large printer, crews are able to build each individual wall of a house in well under twenty-four hours.",
      "3D printing, which forms objects by adding material layer upon layer, is now being applied to houses as well."]),
]


def pool_synthesis(rng: random.Random):
    items = []
    # Order easy -> hard by prose density so the tiers (drawn in order) ramp.
    ordered = sorted(
        _SYNTHESIS,
        key=lambda it: len(it[3]) + sum(len(n) for n in it[1]),
    )
    for topic, notes, goal, correct_s, wrongs in ordered:
        note_block = "\n".join(f"• {n}" for n in notes)
        correct = (correct_s, f"Correct. This sentence uses the notes to {goal}.")
        distractors = [(w, f"This is accurate but does not {goal} as the prompt asks.")
                       for w in wrongs]
        options, ci, rats = shuffle_with_correct(rng, correct, distractors)
        prompt = (f"While researching {topic}, a student took the following notes:\n"
                  f"{note_block}\n\n"
                  f"The student wants to {goal}. Which choice most effectively uses "
                  "the relevant information to accomplish this goal?")
        items.append(mc(prompt, options, ci, rats, subskill="synthesize_notes",
                        qtype="multiple_choice",
                        explanation=(f"The goal is to {goal}; only the correct choice "
                                     "selects and combines the notes to do that."),
                        tags=["expression", "synthesis"], est=70))
    return items


# Extend the authored pools with additional original items (kept in a separate
# module so it can be generated/expanded independently).
from .pools_extra import TRANS2, CONCISION2, SYNTH2  # noqa: E402
_TRANS_ITEMS.extend(TRANS2)
_CONCISION.extend(CONCISION2)
_SYNTHESIS.extend(SYNTH2)
