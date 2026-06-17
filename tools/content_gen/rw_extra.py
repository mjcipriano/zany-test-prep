"""Additional SAT Reading & Writing generators (combinatorial, high-volume).

Covers Standard English Conventions types not in rw_gen.py — verb tense/form,
parallel structure, pronoun-antecedent agreement — plus quantitative Command of
Evidence (a claim supported by a small data table). All wording is original and
each item has exactly one defensible answer.
"""
from __future__ import annotations

import random

from .util import mc, shuffle_with_correct

_NAMES = ["Maya", "Liam", "Aria", "Noah", "Priya", "Diego", "Ivy", "Omar",
          "Lena", "Theo", "Zoe", "Caleb", "Nina", "Ravi", "Sora", "Jonas",
          "Elena", "Marcus", "Yuki", "Tariq"]


# --------------------------------------------------------------------------- #
# Verb tense / form (time cue fixes the tense; plural subjects avoid SVA noise)
# --------------------------------------------------------------------------- #
_VT_SUBJECTS = [
    "the researchers", "the students", "the volunteers", "the engineers",
    "the dancers", "the farmers", "the editors", "the players", "the climbers",
    "the musicians", "the historians", "the workers", "the designers",
    "the travelers",
]
# (base, past, future_marker handled, -ing)
_VT_VERBS = [
    ("travel", "traveled"), ("study", "studied"), ("present", "presented"),
    ("repair", "repaired"), ("design", "designed"), ("publish", "published"),
    ("complete", "completed"), ("explore", "explored"), ("record", "recorded"),
    ("organize", "organized"), ("rebuild", "rebuilt"), ("review", "reviewed"),
    ("launch", "launched"), ("measure", "measured"),
]
_VT_TAILS = [
    "the new exhibit", "the final route", "the annual report",
    "the old bridge", "the research site", "the entire collection",
    "the city archive", "the wetland survey",
]
_VT_TIME = {
    "past": ["Last year", "Yesterday", "A decade ago", "Last summer", "In 2009"],
    "present": ["Each day", "These days", "Every season", "Routinely", "Currently"],
    "future": ["Next year", "Soon", "By next month", "In the coming weeks", "Tomorrow"],
}
_VT_NEED = {"past": "the past tense", "present": "the present tense",
            "future": "the future tense"}


def gen_verb_tense(rng: random.Random, difficulty: str = "medium"):
    tense = rng.choice(["past", "present", "future"])
    subj = rng.choice(_VT_SUBJECTS)
    base, past = rng.choice(_VT_VERBS)
    tail = rng.choice(_VT_TAILS)
    cue = rng.choice(_VT_TIME[tense])
    present = base                      # plural subject -> base form
    future = f"will {base}"
    ing = f"{base}ing" if not base.endswith("e") else base[:-1] + "ing"
    forms = {"past": past, "present": present, "future": future}
    correct_word = forms[tense]
    others = [v for k, v in forms.items() if k != tense] + [ing]
    correct = (correct_word, f"Correct. '{cue}' calls for {_VT_NEED[tense]}.")
    distractors = []
    labels = {past: "past tense", present: "present tense", future: "future tense",
              ing: "an -ing form, which cannot be the main verb here"}
    for w in others:
        distractors.append((w, f"'{w}' is {labels.get(w, 'the wrong form')}; "
                            f"the time marker '{cue}' requires {_VT_NEED[tense]}."))
    options, ci, rats = shuffle_with_correct(rng, correct, distractors[:3])
    prompt = (f"{cue}, {subj} ___ {tail}.\n\n"
              "Which choice completes the text so that it conforms to the "
              "conventions of standard English?")
    return mc(prompt, options, ci, rats, subskill="verb_tense",
              qtype="grammar_editing",
              explanation=(f"The time marker '{cue}' sets {_VT_NEED[tense]}, so "
                           f"'{correct_word}' is correct."),
              tags=["conventions", "verb-tense"], est=45)


# --------------------------------------------------------------------------- #
# Parallel structure (a list should keep the same grammatical form)
# --------------------------------------------------------------------------- #
_PAR_ROLES = ["job", "internship", "role", "program", "course", "position",
              "fellowship", "workshop"]
_PAR_GERUNDS = [
    ("managing the budget", "manage the budget"),
    ("writing weekly reports", "write weekly reports"),
    ("training new staff", "train new staff"),
    ("scheduling interviews", "schedule interviews"),
    ("analyzing the data", "analyze the data"),
    ("editing the manuscript", "edit the manuscript"),
    ("planning the events", "plan the events"),
    ("testing the software", "test the software"),
    ("designing the posters", "design the posters"),
    ("tracking expenses", "track expenses"),
    ("leading discussions", "lead discussions"),
    ("reviewing applications", "review applications"),
]


def gen_parallelism(rng: random.Random, difficulty: str = "medium"):
    role = rng.choice(_PAR_ROLES)
    picks = rng.sample(_PAR_GERUNDS, 3)
    (g1, _), (g2, _), (g3, base3) = picks
    correct = (g3, "Correct. The list uses -ing forms, so the third item must be "
               "parallel (also an -ing form).")
    verb = base3.split()[0]
    rest = base3[len(verb):]
    distractors = [
        (f"to {base3}", "Not parallel: an infinitive breaks the list of -ing forms."),
        (f"{verb}s{rest}", "Not parallel: a present-tense verb breaks the -ing pattern."),
        (f"{verb}ed{rest}" if not verb.endswith("e") else f"{verb}d{rest}",
         "Not parallel: a past-tense verb breaks the -ing pattern."),
    ]
    options, ci, rats = shuffle_with_correct(rng, correct, distractors)
    prompt = (f"The {role} involves {g1}, {g2}, and ___.\n\n"
              "Which choice completes the text so that it conforms to the "
              "conventions of standard English?")
    return mc(prompt, options, ci, rats, subskill="parallel_structure",
              qtype="grammar_editing",
              explanation=("Items in a series must share the same grammatical form; "
                           "the first two are -ing forms, so the third must be too."),
              tags=["conventions", "parallelism"], est=50)


# --------------------------------------------------------------------------- #
# Pronoun-antecedent agreement (its vs. their, by antecedent number)
# --------------------------------------------------------------------------- #
_PA_SING = ["The company", "The team", "The committee", "The school", "The city",
            "The orchestra", "The museum", "The agency", "Each student",
            "Every applicant", "The university", "The startup"]
_PA_PLUR = ["The players", "The teachers", "The volunteers", "The residents",
            "The scientists", "The workers", "The artists", "Both companies",
            "The members", "The engineers", "The students", "The farmers"]
_PA_TAILS = [
    "released ___ annual report on time",
    "celebrated ___ hard-won victory",
    "updated ___ official website",
    "defended ___ final decision",
    "published ___ research findings",
    "expanded ___ original plan",
]


def gen_pronoun_antecedent(rng: random.Random, difficulty: str = "medium"):
    plural = rng.random() < 0.5
    if difficulty == "easy":
        plural = False
    elif difficulty == "hard":
        plural = True
    ante = rng.choice(_PA_PLUR if plural else _PA_SING)
    tail = rng.choice(_PA_TAILS)
    correct_word = "their" if plural else "its"
    wrong_num = "its" if plural else "their"
    correct = (correct_word, f"Correct. '{ante}' is "
               f"{'plural' if plural else 'singular'}, so the pronoun is "
               f"'{correct_word}'.")
    distractors = [
        (wrong_num, f"Agreement error: '{ante}' is "
         f"{'plural' if plural else 'singular'}, so the pronoun must be "
         f"'{correct_word}', not '{wrong_num}'."),
        ("it's", "'it's' means 'it is' and is not a possessive pronoun."),
        ("they're", "'they're' means 'they are' and is not a possessive pronoun."),
    ]
    options, ci, rats = shuffle_with_correct(rng, correct, distractors)
    prompt = (f"{ante} {tail}.\n\n"
              "Which choice completes the text so that it conforms to the "
              "conventions of standard English?")
    return mc(prompt, options, ci, rats, subskill="pronoun_antecedent",
              qtype="grammar_editing",
              explanation=("A possessive pronoun must agree with its antecedent in "
                           f"number: '{ante}' takes '{correct_word}'."),
              tags=["conventions", "pronoun-antecedent"], est=45)


# --------------------------------------------------------------------------- #
# Quantitative Command of Evidence (claim supported by a small data table)
# --------------------------------------------------------------------------- #
_QE_TOPICS = [
    ("Annual rainfall", "City reservoir levels", "millimeters", "rose"),
    ("Library visits", "the downtown branch", "thousands", "increased"),
    ("Solar installations", "the county", "units", "grew"),
    ("Recycling rate", "the town", "percent", "climbed"),
    ("Average commute", "the metro area", "minutes", "fell"),
    ("Wetland bird species", "the reserve", "species", "increased"),
    ("Ticket sales", "the festival", "thousands", "rose"),
    ("Coral cover", "the reef", "percent", "declined"),
]


def gen_quantitative_evidence(rng: random.Random, difficulty: str = "medium"):
    metric, place, unit, verb = rng.choice(_QE_TOPICS)
    rising = verb in ("rose", "increased", "grew", "climbed")
    # Difficulty ramp: more rows, bigger numbers, and uneven year-to-year steps
    # (so "rose by the same amount each year" becomes a tempting wrong answer).
    n = {"easy": 4, "medium": 5, "hard": 6}.get(difficulty, 5)
    years = [2018 + rng.randint(0, 2) + i for i in range(n)]
    if difficulty == "easy":
        start = rng.randint(20, 60)
        steps = [rng.choice([3, 4, 5, 6, 8])] * (n - 1)  # constant step
    elif difficulty == "medium":
        start = rng.randint(40, 120)
        steps = [rng.choice([4, 6, 8, 10]) for _ in range(n - 1)]  # uneven
    else:
        start = rng.randint(120, 400)
        steps = [rng.choice([7, 9, 11, 15, 20]) for _ in range(n - 1)]  # uneven
    asc = [start]
    for s in steps:
        asc.append(asc[-1] + s)
    vals = asc if rising else asc[::-1]
    rows = [[str(y), str(v)] for y, v in zip(years, vals)]
    first, last = vals[0], vals[-1]
    direction = "up" if rising else "down"
    opp = "down" if rising else "up"
    dir_verb = rng.choice(
        ["rose", "increased", "climbed"] if rising else ["fell", "declined", "dropped"]
    )
    avg_step = round(abs(last - first) / (n - 1))
    max_step = max(steps)
    big = max_step + rng.choice([10, 15, 20])
    midi = n // 2
    mid_year, mid_val = years[midi], vals[midi]

    claim = (f"A researcher claims that {metric.lower()} in {place} {verb} "
             f"steadily from {years[0]} to {years[-1]}.")

    # Correct statement: vary the opener so the right answer isn't guessable by
    # its first word (a real tell when every key started with the same word).
    correct_text = rng.choice([
        f"From {years[0]} to {years[-1]}, the value {dir_verb} every year, going "
        f"from {first} to {last} {unit}.",
        f"The value {dir_verb} each year, moving from {first} to {last} {unit} "
        f"over the period.",
        f"Year over year the figure {dir_verb}, reaching {last} {unit} by "
        f"{years[-1]} from {first} {unit}.",
        f"Across all {n} years shown, the value {dir_verb} from {first} to "
        f"{last} {unit}.",
    ])
    correct = (correct_text, "Correct. This matches the steady, one-direction "
               "trend the claim describes across every year shown.")

    pool = {
        "steady": (
            f"The value held steady near {first} {unit} for most of the span "
            f"before a single change late in {years[-1]}.",
            "The table shows the value changing every year, not holding steady."),
        "peaked": (
            f"It peaked in {mid_year} at {mid_val} {unit} and then reversed "
            f"course for the rest of the period.",
            "The largest value is at an endpoint, not the middle year."),
        "mixed": (
            f"In some years the value moved {opp} and in others {direction}, "
            f"rather than in a single direction.",
            "Every year moves the same direction, so this misreads the table."),
        "constant": (
            f"The value changed by the same amount every year, a constant "
            f"{avg_step} {unit} per year.",
            f"The year-to-year changes vary, so the change was not a constant "
            f"{avg_step} {unit}."),
        "subset": (
            f"Almost all of the change happened between {years[0]} and "
            f"{years[1]}, with little movement afterward.",
            "The value changes in every year shown, not just the first span."),
        "bigjump": (
            f"The value {dir_verb} by more than {big} {unit} in a single year.",
            f"The largest one-year change was only {max_step} {unit}."),
    }
    if difficulty == "easy":
        keys = ["steady", "peaked", "mixed"]
    elif difficulty == "medium":
        keys = ["constant", "peaked", "mixed"]
    else:
        keys = ["constant", "subset", "bigjump"]
    distractors = [pool[k] for k in keys]

    prompt = (f"{claim}\n\n" + rng.choice([
        "Which choice best uses data from the table to support the "
        "researcher's claim?",
        "Which statement is best supported by the data in the table?",
        "Which finding from the table most directly supports the claim?",
    ]))
    options, ci, rats = shuffle_with_correct(rng, correct, distractors)
    return mc(prompt, options, ci, rats, subskill="quantitative_evidence",
              qtype="data_interpretation", explanation=(
                  "The supporting statement must reflect the table's actual, "
                  "consistent trend across all the years shown."),
              tags=["reading", "evidence", "quantitative"], est=80,
              stimulus={"type": "table", "table": {
                  "caption": f"{metric} in {place} ({unit})",
                  "headers": ["Year", metric], "rows": rows}})
