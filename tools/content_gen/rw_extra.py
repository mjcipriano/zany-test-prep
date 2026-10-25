"""Additional SAT/ACT Reading & Writing generators (combinatorial, high-volume).

Family tables (see registry.py) for Standard English Conventions skills not in
rw_gen.py — verb tense/form, parallel structure, pronoun-antecedent agreement —
plus quantitative Command of Evidence (claims checked against a small data
table whose numbers are computed, so the key is verifiably true).

Fill-in families follow the "<text with one ___>\\n\\n<stem>" convention and
are marked ``fn.fill_in = True``; the table-based evidence families contain no
blank and are marked ``fn.fill_in = False``.
"""
from __future__ import annotations

import random

from .util import mc
from .rw_gen import (NAMES, build, cap, conv_stem, dispatch, family, fill, low, pron, soft_low)

_NAMES = NAMES


# =========================================================================== #
# VERB TENSE / FORM
# =========================================================================== #
# (base, 3rd-person singular, past, past participle, -ing)
_VERBS = [
    ("travel", "travels", "traveled", "traveled", "traveling"),
    ("study", "studies", "studied", "studied", "studying"),
    ("present", "presents", "presented", "presented", "presenting"),
    ("repair", "repairs", "repaired", "repaired", "repairing"),
    ("design", "designs", "designed", "designed", "designing"),
    ("publish", "publishes", "published", "published", "publishing"),
    ("complete", "completes", "completed", "completed", "completing"),
    ("explore", "explores", "explored", "explored", "exploring"),
    ("record", "records", "recorded", "recorded", "recording"),
    ("organize", "organizes", "organized", "organized", "organizing"),
    ("review", "reviews", "reviewed", "reviewed", "reviewing"),
    ("measure", "measures", "measured", "measured", "measuring"),
]
_IRREG = [
    ("begin", "begins", "began", "begun", "beginning"),
    ("write", "writes", "wrote", "written", "writing"),
    ("see", "sees", "saw", "seen", "seeing"),
    ("take", "takes", "took", "taken", "taking"),
    ("go", "goes", "went", "gone", "going"),
    ("choose", "chooses", "chose", "chosen", "choosing"),
    ("drive", "drives", "drove", "driven", "driving"),
    ("speak", "speaks", "spoke", "spoken", "speaking"),
    ("break", "breaks", "broke", "broken", "breaking"),
    ("grow", "grows", "grew", "grown", "growing"),
    ("run", "runs", "ran", "run", "running"),
    ("swim", "swims", "swam", "swum", "swimming"),
    ("ring", "rings", "rang", "rung", "ringing"),
    ("forget", "forgets", "forgot", "forgotten", "forgetting"),
]
_VT_SUBJ_PL = ["the researchers", "the students", "the volunteers", "the engineers",
               "the dancers", "the farmers", "the editors", "the players", "the climbers",
               "the musicians", "the historians", "the designers"]
_VT_SUBJ_SG = ["the committee", "the museum", "the orchestra", "the mayor", "the lab",
               "the company", "the chef", "the pilot"]
_VT_TAILS_BY_VERB = {
    "travel": ["to the research site", "across the northern valley", "to the coast for the survey"],
    "study": ["the wetland birds", "the old harbor maps", "the effects of the new fertilizer"],
    "present": ["the annual report", "the findings at the conference", "a plan for the new exhibit"],
    "repair": ["the old bridge", "the stage lights", "the greenhouse roof"],
    "design": ["the new exhibit", "a lighter bicycle frame", "the festival posters"],
    "publish": ["the annual report", "the wetland survey", "a guide to the city archive"],
    "complete": ["the wetland survey", "the final route", "the renovation of the lobby"],
    "explore": ["the sea caves", "the research site", "the ruins north of town"],
    "record": ["the harvest totals", "the temperature at dawn", "every bird call on the trail"],
    "organize": ["the harvest festival", "the winter schedule", "the city archive"],
    "review": ["the winter schedule", "the safety plan", "the entire collection"],
    "measure": ["the snowpack", "the width of the river", "the growth of the saplings"],
    "begin": ["the harvest early", "the renovation of the lobby", "a new series of lectures"],
    "write": ["a guide to the trails", "the annual report", "a history of the mill"],
    "see": ["the comet from the ridge", "the first cranes of the season", "the finished mural"],
    "take": ["the ferry to the island", "samples from the reef", "a shorter route home"],
    "go": ["to the research station", "on a tour of the archive", "to the harvest festival"],
    "choose": ["a new director", "the site for the garden", "a route through the valley"],
    "drive": ["to the research site", "the supplies up the mountain", "across the salt flats"],
    "speak": ["at the opening ceremony", "to the city council", "about the wetland survey"],
    "break": ["the old attendance record", "ground on the new library", "the ice on the pond"],
    "grow": ["tomatoes behind the station", "wheat on the upper field", "herbs for the kitchen"],
    "run": ["the summer workshop", "the ferry on weekends", "the city archive"],
    "swim": ["across the harbor", "in the cold lake", "before the morning tide"],
    "ring": ["the bell at noon", "the old tower bell", "in the new year"],
    "forget": ["the keys to the archive", "the lines of the play", "the way to the site"],
}


def _tail(rng, base):
    return rng.choice(_VT_TAILS_BY_VERB[base])
_VT_TIME = {
    "past": ["Last year", "Yesterday", "A decade ago", "Last summer", "In 2009", "Two weeks ago"],
    "present": ["Each day", "These days", "Every season", "Routinely", "Currently", "Every spring"],
    "future": ["Next year", "Soon", "By next month", "In the coming weeks", "Tomorrow", "Later this year"],
}
_VT_NEED = {"past": "the past tense", "present": "the present tense",
            "future": "the future tense"}


@family(fill_in=True)
def vt_time_cue(rng, difficulty):
    """A time marker fixes the tense; singular and plural subjects both appear."""
    tense = rng.choice(["past", "present", "future"])
    plural = rng.random() < 0.5
    subj = rng.choice(_VT_SUBJ_PL if plural else _VT_SUBJ_SG)
    if difficulty == "easy":
        name = rng.choice(_NAMES)
        subj = name if rng.random() < 0.4 else subj
        plural = plural and subj != name
    base, s3, past, pp, ing = rng.choice(_VERBS if difficulty != "hard" else _VERBS + _IRREG)
    tail = _tail(rng, base)
    cue = rng.choice(_VT_TIME[tense])
    present = base if plural else s3
    forms = {"past": past, "present": present, "future": f"will {base}"}
    right = forms[tense]
    correct = (right, f"Correct. '{cue}' calls for {_VT_NEED[tense]}.")
    labels = {"past": "the past tense", "present": "the present tense", "future": "the future tense"}
    ds = [(forms[k], f"'{forms[k]}' is {labels[k]}, but the time marker '{cue}' requires "
                     f"{_VT_NEED[tense]}.") for k in forms if k != tense]
    if difficulty == "hard" and tense == "past":
        ds[0] = (pp if pp != past else f"has {pp}", f"'{pp if pp != past else 'has ' + pp}' is not the "
                                                   "simple past; the completed, dated action needs "
                                                   f"'{past}'.")
    ds.append((ing, "An -ing form alone cannot be the main verb of the sentence."))
    text = f"{cue}, {subj} ___ {tail}."
    if difficulty == "hard":
        text = f"{cue}, {subj}, " + rng.choice(["after months of planning,", "despite the weather,",
                                                 "with help from the city,"]) + f" ___ {tail}."
    return build(rng, fill(text, conv_stem(rng)), correct, ds[:3], subskill="verb_tense",
                 explanation=f"The time marker '{cue}' sets {_VT_NEED[tense]}, so '{right}' is correct.",
                 tags=["conventions", "verb-tense"])


# (opening words, later-action verb forms (past, pp, base, s3), subject of the earlier
#  action, earlier verb base, object, closing sentence)
_VT_SEQ = [
    ("By the time the guests", ("arrived", "arrived", "arrive", "arrives"), "{N}", "set", "the table", "The dinner began at eight."),
    ("Before the bridge", ("opened", "opened", "open", "opens"), "commuters", "use", "a ferry across the river", "The crossing took forty minutes."),
    ("When the inspectors finally", ("visited", "visited", "visit", "visits"), "the crew", "finish", "most of the repairs", "Only the roof remained."),
    ("By the time the rain", ("stopped", "stopped", "stop", "stops"), "the river", "flood", "the lower fields", "Farmers lost the early crop."),
    ("When the orchestra", ("took the stage", "taken the stage", "take the stage", "takes the stage"), "the audience", "wait", "for nearly an hour", "The applause was still warm."),
    ("Before the museum", ("reopened", "reopened", "reopen", "reopens"), "curators", "clean", "every painting in the east wing", "Visitors noticed the difference at once."),
    ("By the time {N}", ("reached the summit", "reached the summit", "reach the summit", "reaches the summit"), "the fog", "roll", "in across the valley", "The view was gone."),
    ("When the printing press", ("arrived", "arrived", "arrive", "arrives"), "monks", "copy", "manuscripts by hand for centuries", "The change was swift."),
    ("By the time the ferry", ("docked", "docked", "dock", "docks"), "the storm", "pass", "over the island", "Passengers stepped off into sunshine."),
    ("When the archivist", ("retired", "retired", "retire", "retires"), "she", "catalog", "more than ninety thousand letters", "Her successor inherited a tidy index."),
]
_VT_PAST_FORMS = {"set": ("set", "set"), "use": ("used", "used"), "finish": ("finished", "finished"),
                  "flood": ("flooded", "flooded"), "wait": ("waited", "waited"),
                  "clean": ("cleaned", "cleaned"), "roll": ("rolled", "rolled"), "copy": ("copied", "copied"),
                  "pass": ("passed", "passed"), "catalog": ("cataloged", "cataloged")}


@family(fill_in=True)
def vt_sequence(rng, difficulty):
    """Past perfect for the earlier of two past events."""
    opening, (lpast, lpp, lbase, ls3), subj, base, obj, close = rng.choice(_VT_SEQ)
    name = rng.choice(_NAMES)
    opening = opening.format(N=name)
    subj = subj.format(N=name)
    past, pp = _VT_PAST_FORMS[base]
    s3 = base + ("es" if base.endswith("sh") or base.endswith("ss") else "s") if not base.endswith("y") else base[:-1] + "ies"
    already = "already " if difficulty != "easy" else ""
    if rng.random() < 0.5:
        # blank = the earlier action -> past perfect
        correct = (f"had {already}{pp}", "Correct. This action was completed before another past action, "
                                         "so the past perfect ('had' + past participle) is needed.")
        ds = [(f"has {already}{pp}", "The present perfect links to the present, but both events are in the past."),
              (f"{already}{s3}" if already else s3, "The present tense does not fit a sequence of two past events."),
              (f"will have {already}{pp}" if difficulty != "easy" else f"is {base}ing",
               "This form points to the future, but the sentence describes the past.")]
        if difficulty == "hard":
            ds[1] = (f"would have {already}{pp}", "'would have' describes a hypothetical, but the "
                                                 "action really happened.")
        text = f"{opening} {lpast}, {subj} ___ {obj}."
    else:
        # blank = the later action -> simple past
        correct = (lpast, "Correct. The later of the two past actions takes the simple past; the "
                          "earlier one is already in the past perfect.")
        ds = [(f"had {lpp}", "The past perfect belongs to the earlier action, which the main clause already has."),
              (ls3, "The present tense does not fit a sequence of two past events."),
              (f"have {lpp}" if difficulty != "easy" else f"will {lbase}",
               "This form does not place the action in the past alongside the main clause.")]
        text = f"{opening} ___, {subj} had {already}{pp} {obj}."
    if difficulty != "easy":
        text = f"{text} {close}"
    return build(rng, fill(text, conv_stem(rng)), correct, ds, subskill="verb_tense",
                 explanation=("When one past action is finished before another past action, the "
                              "earlier one takes the past perfect ('had' + past participle) and the "
                              "later one the simple past."),
                 tags=["conventions", "verb-tense", "past-perfect"], est=50)


_VT_IRREG_FRAMES = [
    ("The orchestra has ___ rehearsing the final movement.", "begin"),
    ("By noon the volunteers had ___ every letter in the box.", "write"),
    ("Nobody on the team had ___ the ocean before the trip.", "see"),
    ("The committee has ___ a different approach this year.", "take"),
    ("The last ferry had already ___ when we reached the dock.", "go"),
    ("The jury has ___ a winner from the twelve finalists.", "choose"),
    ("{N} had ___ the old truck across three states.", "drive"),
    ("The guest lecturer has ___ at the college twice before.", "speak"),
    ("The cold snap had ___ a water main under the square.", "break"),
    ("The colony has ___ to nearly a thousand birds.", "grow"),
    ("The river had ___ dry by the end of August.", "run"),
    ("{N} has ___ across the lake every summer since childhood.", "swim"),
    ("The bell had ___ before anyone reached the door.", "ring"),
    ("The crew had nearly ___ about the spare key.", "forget"),
    ("{N} has ___ the same route to work for a decade.", "take"),
    ("The valley had ___ dark long before the climbers returned.", "grow"),
    ("The students have ___ their letters to the mayor.", "write"),
    ("The glass had ___ into a hundred pieces.", "break"),
]
_VT_IRREG_PAST_FRAMES = [
    ("Last spring the orchestra ___ rehearsing a new symphony.", "begin"),
    ("In 1890 the diarist ___ the last of her entries.", "write"),
    ("From the ridge, the hikers ___ the whole valley.", "see"),
    ("The committee ___ a different approach last year.", "take"),
    ("The jury ___ a winner after two days of debate.", "choose"),
    ("{N} ___ the old truck across three states in 2015.", "drive"),
    ("The guest lecturer ___ to a packed hall yesterday.", "speak"),
    ("The cold snap ___ a water main under the square.", "break"),
    ("The river ___ dry by the end of last August.", "run"),
    ("{N} ___ across the lake every summer as a child.", "swim"),
    ("The bell ___ twice before the doors opened.", "ring"),
    ("The crew ___ the rope ladder down to the dock.", "take"),
    ("The storm ___ in from the west just after midnight.", "go"),
    ("The vines ___ over the fence by midsummer.", "grow"),
    ("{N} ___ the spare key in the garden shed.", "forget"),
    ("The lecturer ___ for nearly two hours without notes.", "speak"),
]


@family(fill_in=True, small_space=True)
def vt_irregular(rng, difficulty):
    """Irregular past vs. past participle (began/begun, saw/seen)."""
    forms = {v[0]: v for v in _IRREG}
    name = rng.choice(_NAMES)
    if difficulty == "easy" or (difficulty == "medium" and rng.random() < 0.4):
        frame, base = rng.choice(_VT_IRREG_PAST_FRAMES)
        b, s3, past, pp, ing = forms[base]
        correct = (past, f"Correct. With no helping verb, the simple past '{past}' is needed.")
        ds = [(pp, f"'{pp}' is the past participle; it needs a helping verb such as 'had' or 'has'."),
              (ing, "An -ing form alone cannot serve as the main verb."),
              (base if base != pp else s3, "This present-tense form does not show the past time the sentence describes.")]
        if past == pp:
            ds[0] = (f"had {pp}", "The past perfect is not needed; there is no earlier past action to "
                                  "set it before.")
        expl = f"There is no helping verb, so the verb must be the simple past form '{past}'."
    else:
        frame, base = rng.choice(_VT_IRREG_FRAMES)
        b, s3, past, pp, ing = forms[base]
        correct = (pp, f"Correct. After 'has' or 'had,' the past participle '{pp}' is required.")
        ds = [(past, f"'{past}' is the simple past; after a helping verb the participle '{pp}' is needed."),
              (ing, "An -ing form after 'has/had' would need 'been' and still changes the meaning."),
              (base if base != pp else f"been {ing}", "This form cannot follow 'has' or 'had' here.")]
        if past == pp:
            ds[0] = (s3, "A present-tense form cannot follow 'has' or 'had.'")
        expl = f"'has/had' must be followed by the past participle, which for '{base}' is '{pp}'."
    text = frame.format(N=name)
    if difficulty == "hard":
        text = rng.choice(["According to the program notes, ", "As the logbook shows, ",
                           "By every account, "]) + soft_low(text)
    return build(rng, fill(text, conv_stem(rng)), correct, ds, subskill="verb_tense",
                 explanation=expl, tags=["conventions", "verb-tense", "irregular"])


# (lead, verb base, object, plural subject?)
_VT_SINCE = [
    ("Since 2015, the lab", "publish", "more than forty papers", False),
    ("For the past decade, the festival", "attract", "visitors from across the country", False),
    ("Since the renovation, the library", "host", "a lecture every Thursday", False),
    ("Ever since the flood, the town", "maintain", "a wall of sandbags along the river", False),
    ("For three generations, the family", "run", "the mill on the hill", False),
    ("Since her first recital, {N}", "perform", "in more than twenty cities", False),
    ("Over the last five years, the reef", "recover", "much of its lost coral", False),
    ("Since the merger, the company", "open", "offices in four countries", False),
    ("Since 2015, the lab's researchers", "publish", "more than forty papers", True),
    ("For the past decade, the organizers", "attract", "visitors from across the country", True),
    ("Since the renovation, the librarians", "host", "a lecture every Thursday", True),
    ("Ever since the flood, the residents", "maintain", "a wall of sandbags along the river", True),
    ("For three generations, the Alvarez brothers", "run", "the mill on the hill", True),
    ("Over the last five years, the reefs", "recover", "much of their lost coral", True),
    ("Since the merger, the two companies", "open", "offices in four countries", True),
    ("Since the trail opened, hikers", "report", "sightings of the rare orchid", True),
]
_VT_PP = {"publish": "published", "attract": "attracted", "host": "hosted", "maintain": "maintained",
          "run": "run", "perform": "performed", "recover": "recovered", "open": "opened", "report": "reported"}
_VT_S3 = {"publish": "publishes", "attract": "attracts", "host": "hosts", "maintain": "maintains",
          "run": "runs", "perform": "performs", "recover": "recovers", "open": "opens", "report": "reports"}


@family(fill_in=True)
def vt_present_perfect(rng, difficulty):
    """'Since/for' spans reaching the present take the present perfect."""
    lead, base, obj, plural = rng.choice(_VT_SINCE)
    name = rng.choice(_NAMES)
    lead = lead.format(N=name)
    pp, s3 = _VT_PP[base], _VT_S3[base]
    aux = "have" if plural else "has"
    pres = base if plural else s3
    prog = ("are" if plural else "is") + " " + (f"{base}ing".replace("eing", "ing") if base != "run" else "running")
    correct = (f"{aux} {pp}", "Correct. A period that began in the past and continues to now takes "
                              f"the present perfect ('{aux}' + past participle).")
    ds = [(pres, "The simple present does not express an action spanning a period up to now."),
          (f"will {base}", "The future tense contradicts the 'since/for' phrase, which reaches to the present."),
          (prog, "The present progressive describes what is happening right now, not a total over a period.")]
    if difficulty == "hard":
        ds[0] = (f"had {pp}", "The past perfect would place the whole period before some other past "
                              "moment, but the span continues into the present.")
    text = f"{lead} ___ {obj}."
    if difficulty != "easy":
        text = f"{text} " + rng.choice(["The record is unlikely to be matched.", "Few expected such a run.",
                                        "The pace shows no sign of slowing."])
    return build(rng, fill(text, conv_stem(rng)), correct, ds, subskill="verb_tense",
                 explanation=("'Since...' and 'for the past...' mark a span that reaches the present, "
                              "which calls for the present perfect."),
                 tags=["conventions", "verb-tense", "present-perfect"])


_VT_PASS = [
    ("In 1911 a crew of six set out to map the northern coast.", "past",
     "Along the way, the team", "record", "the location of every inlet", "Their charts were used for decades."),
    ("Every autumn the village holds a harvest fair on the green.", "present",
     "Each year, the bakers", "sell", "hundreds of apple tarts before noon", "The recipe has not changed in a century."),
    ("The new observatory will open to the public next spring.", "future",
     "On clear nights, visitors", "view", "the rings of Saturn through the main telescope", "Tickets go on sale in March."),
    ("Last summer Hana spent two months at a marine station.", "past",
     "Most mornings, she", "count", "the fish along a stretch of reef", "The data went into a regional survey."),
    ("The city's streetcar line reopened in 2019 after a long closure.", "present",
     "Today the cars", "carry", "about nine thousand riders a day", "A second line is planned."),
    ("The bakery plans to move to a larger shop next year.", "future",
     "After the move, the ovens", "run", "around the clock", "The owners expect to hire six more bakers."),
    ("In the 1950s the mill employed half the town.", "past",
     "Each shift, the workers", "produce", "miles of cotton cloth", "The mill closed in 1983."),
    ("Mateo coaches a youth soccer team on weekends.", "present",
     "Before each match, he", "walk", "the field to check for holes", "The players rarely notice."),
    ("In 1962 the town built a small planetarium beside the library.", "past",
     "On Friday nights, families", "fill", "every seat under the dome", "The projector was replaced in 2010."),
    ("The ferry company will add a third boat next summer.", "future",
     "With the extra boat, crews", "carry", "twice as many bicycles on weekend crossings", "Cyclists have asked for this for years."),
    ("Every winter the pond behind the school freezes solid.", "present",
     "Most afternoons, students", "skate", "until the light fades", "A custodian checks the ice each morning."),
    ("Last spring a late frost hit the orchard.", "past",
     "For a week, the growers", "light", "small fires between the rows at night", "Most of the blossoms survived."),
]
_VT_FORMS = {"record": ("records", "record", "recorded", "will record", "recording"),
             "sell": ("sells", "sell", "sold", "will sell", "selling"),
             "view": ("views", "view", "viewed", "will view", "viewing"),
             "count": ("counts", "count", "counted", "will count", "counting"),
             "carry": ("carries", "carry", "carried", "will carry", "carrying"),
             "run": ("runs", "run", "ran", "will run", "running"),
             "produce": ("produces", "produce", "produced", "will produce", "producing"),
             "walk": ("walks", "walk", "walked", "will walk", "walking"),
             "fill": ("fills", "fill", "filled", "will fill", "filling"),
             "skate": ("skates", "skate", "skated", "will skate", "skating"),
             "light": ("lights", "light", "lit", "will light", "lighting")}
_VT_SING_SUBJ = {"she", "he"}


@family(fill_in=True, small_space=True)
def vt_passage(rng, difficulty):
    """Mini passage: the lead sentence sets the time frame for the blank."""
    lead, tense, pre, base, obj, close = rng.choice(_VT_PASS)
    s3, pl, past, fut, ing = _VT_FORMS[base]
    subj_word = pre.split()[-1]
    plural = subj_word not in _VT_SING_SUBJ
    present = pl if plural else s3
    forms = {"present": present, "past": past, "future": fut}
    right = forms[tense]
    label = {"present": "present", "past": "past", "future": "future"}
    correct = (right, f"Correct. The passage is set in the {label[tense]}, so the verb keeps that tense.")
    ds = [(forms[k], f"'{forms[k]}' shifts to the {label[k]} tense, breaking the time frame set by the "
                     "first sentence.") for k in forms if k != tense]
    ds.append((ing, "An -ing form alone cannot serve as the main verb."))
    if difficulty == "easy":
        text = f"{lead} {pre} ___ {obj}."
    elif difficulty == "medium":
        text = f"{lead} {pre} ___ {obj}. {close}"
    else:
        text = f"{lead} {pre}, " + rng.choice(["as the records show,", "weather permitting,",
                                                "according to the logbook,"]) + f" ___ {obj}. {close}"
    return build(rng, fill(text, conv_stem(rng)), correct, ds[:3], subskill="verb_tense",
                 explanation=("Keep the tense consistent with the time frame established by the "
                              f"surrounding sentences ({label[tense]})."),
                 tags=["conventions", "verb-tense", "passage"], est=55)


@family(fill_in=True)
def vt_clause_options(rng, difficulty):
    """Options are whole clauses that differ in verb tense/form."""
    tense = rng.choice(["past", "present", "future"])
    cue = rng.choice(_VT_TIME[tense])
    subj = rng.choice(_VT_SUBJ_PL + _VT_SUBJ_SG)
    plural = subj in _VT_SUBJ_PL
    base, s3, past, pp, ing = rng.choice(_VERBS)
    tail = _tail(rng, base)
    present = base if plural else s3
    forms = {"past": past, "present": present, "future": f"will {base}"}
    right = forms[tense]
    correct = (f"{subj} {right} {tail}", f"Correct. '{cue}' calls for {_VT_NEED[tense]}.")
    ds = [(f"{subj} {forms[k]} {tail}", f"'{forms[k]}' is {_VT_NEED[k]}, which conflicts with '{cue}'.")
          for k in forms if k != tense]
    ds.append((f"{subj} {ing} {tail}", "An -ing form leaves the clause without a main verb."))
    frame = rng.choice(["{cue}, ___.", "{cue}, as planned, ___.", "{cue} ___, to everyone's relief."])
    text = frame.format(cue=cue)
    if difficulty == "hard":
        ds[2] = (f"{subj} {'have' if plural else 'has'} {pp} {tail}",
                 "The present perfect does not fit a specific time marker like '{cue}'.".format(cue=cue))
    return build(rng, fill(text, conv_stem(rng)), correct, ds[:3], subskill="verb_tense",
                 explanation=f"The time marker '{cue}' fixes the tense of the whole clause as {_VT_NEED[tense]}.",
                 tags=["conventions", "verb-tense", "clause-options"], est=50)


# =========================================================================== #
# PARALLEL STRUCTURE
# =========================================================================== #
_PAR_ROLES = ["job", "internship", "role", "program", "course", "position", "fellowship", "workshop"]
# (gerund phrase, base phrase, past phrase, noun phrase)
_PAR_ACTS = [
    ("managing the budget", "manage the budget", "managed the budget", "budget management"),
    ("writing weekly reports", "write weekly reports", "wrote weekly reports", "weekly reports"),
    ("training new staff", "train new staff", "trained new staff", "staff training"),
    ("scheduling interviews", "schedule interviews", "scheduled interviews", "interview scheduling"),
    ("analyzing the data", "analyze the data", "analyzed the data", "data analysis"),
    ("editing the manuscript", "edit the manuscript", "edited the manuscript", "manuscript editing"),
    ("planning the events", "plan the events", "planned the events", "event planning"),
    ("testing the software", "test the software", "tested the software", "software testing"),
    ("designing the posters", "design the posters", "designed the posters", "poster design"),
    ("tracking expenses", "track expenses", "tracked expenses", "expense tracking"),
    ("leading discussions", "lead discussions", "led discussions", "discussion leadership"),
    ("reviewing applications", "review applications", "reviewed applications", "application review"),
    ("mapping the trails", "map the trails", "mapped the trails", "trail mapping"),
    ("cataloging the fossils", "catalog the fossils", "cataloged the fossils", "fossil cataloging"),
]
_PAR_FRAMES_G = ["The {role} involves {a}, {b}, and ___.",
                 "Her duties at the {role} include {a}, {b}, and ___.",
                 "Most of the {role} consists of {a}, {b}, and ___."]
_PAR_FRAMES_I = ["The {role} requires interns to {a}, to {b}, and ___.",
                 "In the {role}, {N} learned to {a}, {b}, and ___."]


@family(fill_in=True)
def par_series(rng, difficulty):
    """Third item of a series must match the form of the first two."""
    role = rng.choice(_PAR_ROLES)
    name = rng.choice(_NAMES)
    (g1, b1, p1, n1), (g2, b2, p2, n2), (g3, b3, p3, n3) = rng.sample(_PAR_ACTS, 3)
    form = rng.choice(["gerund", "gerund", "infinitive"] if difficulty != "easy" else ["gerund"])
    if form == "gerund":
        text = rng.choice(_PAR_FRAMES_G).format(role=role, a=g1, b=g2)
        correct = (g3, "Correct. The first two items are -ing phrases, so the third must be too.")
        ds = [(f"to {b3}", "An infinitive breaks the pattern of -ing phrases."),
              (p3, "A past-tense verb breaks the -ing pattern."),
              (n3, "A plain noun phrase breaks the pattern of -ing phrases.")]
        if difficulty == "hard":
            ds[2] = (f"{name} {p3}", "A full clause with its own subject breaks the series of phrases.")
    else:
        frame = rng.choice(_PAR_FRAMES_I)
        text = frame.format(role=role, a=b1, b=b2, N=name)
        if "to {b}" in frame:
            correct = (f"to {b3}", "Correct. Each item repeats 'to' + verb, so the third does too.")
            ds = [(b3, "Without 'to' the third item no longer matches the first two."),
                  (g3, "An -ing phrase breaks the series of infinitives."),
                  (f"that {name} {p3}", "A clause breaks the parallel series of infinitives.")]
        else:
            correct = (b3, "Correct. After 'learned to,' the series continues with base verbs.")
            ds = [(f"to {b3}", "Repeating 'to' only on the last item breaks the pattern 'to a, b, and c'."),
                  (g3, "An -ing phrase breaks the pattern of base verbs."),
                  (p3, "A past-tense verb breaks the pattern set by the first two items.")]
    return build(rng, fill(text, conv_stem(rng)), correct, ds, subskill="parallel_structure",
                 explanation=("Items in a series must share one grammatical form; match the third "
                              "item to the first two."),
                 tags=["conventions", "parallelism", "series"], est=50)


_PAR_CORR = [
    ("not only", "but also"), ("either", "or"), ("neither", "nor"), ("both", "and"),
]
# (first quality, second quality, -ing distractor, clause distractor)
_PAR_CORR_ITEMS = [
    ("its clarity", "its humor", "being humorous", "that it is humorous"),
    ("its speed", "its reliability", "being reliable", "that it is reliable"),
    ("its low cost", "its simplicity", "being simple", "that it is simple"),
    ("its originality", "its practicality", "being practical", "that it is practical"),
    ("its maps", "its clear directions", "giving clear directions", "that its directions are clear"),
    ("its detail", "its accuracy", "being accurate", "that it is accurate"),
    ("its color", "its texture", "having texture", "that it has texture"),
    ("its honesty", "its wit", "being witty", "that it is witty"),
]
_PAR_CORR_VERBS = [
    ("sing", "dance", "dancing", "to dance"), ("swim", "run", "running", "to run"),
    ("paint", "sculpt", "sculpting", "to sculpt"), ("read", "write", "writing", "to write"),
]


@family(fill_in=True)
def par_correlative(rng, difficulty):
    """Correlative pairs (not only...but also, either...or) need matching forms."""
    name = rng.choice(_NAMES)
    first, second = rng.choice(_PAR_CORR)
    if rng.random() < 0.5:
        a, b, w1, w2 = rng.choice(_PAR_CORR_ITEMS)
        frames = {
            "not only": f"The judges praised the entry not only for {a} but also for ___.",
            "either": f"The committee will reward the proposal either for {a} or for ___.",
            "neither": f"The critics admired the design neither for {a} nor for ___.",
            "both": f"Readers value the guide both for {a} and for ___.",
        }
        text = frames[first]
        correct = (b, f"Correct. After '{first}...for {a},' the second half repeats the same "
                      f"'for' + noun pattern: 'for {b}'.")
        ds = [(w1, "An -ing phrase does not match the noun phrase in the first half."),
              (f"its {w1}", "This wordy '-ing' nominalization does not match the simple noun phrase in the first half."),
              (f"for {b}", "'for' is already supplied before the blank; repeating it doubles the preposition.")]
        if difficulty == "hard":
            ds[0] = (w2, "A clause does not match the noun phrase in the first half.")
    else:
        a, b, g, inf = rng.choice(_PAR_CORR_VERBS)
        frames = {
            "not only": f"{name} can not only {a} but also ___.",
            "either": f"At the recital, {name} will either {a} or ___.",
            "neither": f"Under the new rules, contestants may neither {a} nor ___.",
            "both": f"The program teaches students both to {a} and ___.",
        }
        text = frames[first]
        if first == "both":
            correct = (f"to {b}", f"Correct. 'both to {a} and to {b}' keeps the infinitives parallel.")
            ds = [(b, "Without 'to' the second item does not match 'to " + a + "'."),
                  (g, "An -ing form does not match the infinitive in the first half."),
                  (f"how to {b}", "'how to' adds a structure the first half lacks.")]
        else:
            correct = (b, f"Correct. '{first} {a} {second} {b}' pairs two matching base verbs.")
            ds = [(g, "An -ing form does not match the base verb in the first half."),
                  (inf, "An infinitive does not match the base verb in the first half."),
                  (f"{name} can {b}" if first == "not only" else f"{name} will {b}" if first == "either" else f"they may {b}",
                   "Repeating the subject and helping verb breaks the parallel pair.")]
    if difficulty == "hard":
        text = text + " " + rng.choice(["Few disagreed.", "The decision was unanimous.", "Everyone noticed."])
    return build(rng, fill(text, conv_stem(rng)), correct, ds, subskill="parallel_structure",
                 explanation=(f"Whatever follows '{first}' must have the same grammatical form as "
                              f"what follows '{second}'."),
                 tags=["conventions", "parallelism", "correlative"], est=50)


_PAR_COMP = [
    ("Reading the novel", "watching the film", "to watch the film", "the film", "when she watched the film"),
    ("Hiking the ridge trail", "driving to the overlook", "to drive to the overlook", "the overlook road", "if you drive to the overlook"),
    ("Growing tomatoes from seed", "buying seedlings", "to buy seedlings", "seedlings", "when you buy seedlings"),
    ("Learning to sail", "learning to row", "to row a boat", "a rowboat", "if one rows instead"),
    ("Repairing the old clock", "replacing it", "to replace it", "a replacement", "that it be replaced"),
    ("Walking to the market", "taking the bus", "to take the bus", "the bus route", "when the bus is taken"),
    ("Writing the report by hand", "typing it", "to type it", "a typed version", "that it is typed"),
    ("Recording the interviews", "taking notes", "to take notes", "notes", "when notes are taken"),
]
_PAR_COMP_ADJ = ["more rewarding than", "far slower than", "less expensive than", "more tiring than",
                 "just as satisfying as", "no harder than"]


@family(fill_in=True)
def par_comparison(rng, difficulty):
    """Compared items must share a form ('Reading X is better than watching Y')."""
    a, b, inf, noun, clause = rng.choice(_PAR_COMP)
    adj = rng.choice(_PAR_COMP_ADJ)
    text = f"{a} was {adj} ___."
    if difficulty != "easy":
        text = rng.choice(["In the end, ", "For most of the group, ", "As it turned out, "]) + low(text)
    if difficulty == "hard":
        text = text + " " + rng.choice(["Nobody regretted the choice.", "The difference was striking.",
                                        "The group agreed."])
    correct = (b, f"Correct. '{a}' is an -ing phrase, so the item it is compared with must be one too.")
    ds = [(inf, "An infinitive does not match the -ing phrase being compared."),
          (noun, f"This compares an activity ('{low(a)}') with a thing, not with another activity."),
          (clause, "A clause does not match the -ing phrase on the other side of the comparison.")]
    return build(rng, fill(text, conv_stem(rng)), correct, ds, subskill="parallel_structure",
                 explanation=("Both sides of a comparison must have the same grammatical form: "
                              "an -ing phrase is compared with another -ing phrase."),
                 tags=["conventions", "parallelism", "comparison"], est=50)


# (subject, verb 1, verb 2, base of verb 3, correct verb 3, -ing verb 3, tense, pronoun)
_PAR_VERB_SERIES = [
    ("The volunteers", "cleared the trail", "repaired the footbridge", "paint", "painted the signs", "painting the signs", "past", "they"),
    ("Before the storm, the crew", "secured the sails", "checked the radio", "close", "closed the hatches", "closing the hatches", "past", "they"),
    ("Each morning the baker", "feeds the starter", "mixes the dough", "light", "lights the ovens", "lighting the ovens", "present", "she"),
    ("During the dig, the team", "mapped the site", "photographed each layer", "label", "labeled every find", "labeling every find", "past", "they"),
    ("On tour, the band", "plays two sets", "signs posters", "pack", "packs the van itself", "packing the van itself", "present", "it"),
    ("Every spring the farmers", "plow the lower field", "plant barley", "repair", "repair the fences", "repairing the fences", "present", "they"),
    ("After the flood, the librarians", "dried the prints", "rebuilt the shelves", "scan", "scanned the collection", "scanning the collection", "past", "they"),
    ("For the recital, Omar", "practiced scales", "memorized two sonatas", "write", "wrote a short piece of his own", "writing a short piece of his own", "past", "he"),
    ("At dawn the rangers", "unlock the gates", "check the trail cameras", "log", "log the overnight temperatures", "logging the overnight temperatures", "present", "they"),
    ("Last winter the council", "approved the budget", "hired two planners", "schedule", "scheduled a public hearing", "scheduling a public hearing", "past", "it"),
    ("Each summer the lifeguards", "repaint the towers", "restring the buoys", "test", "test the rescue boats", "testing the rescue boats", "present", "they"),
    ("Before the recital, Hana", "tuned the cello", "warmed up with scales", "review", "reviewed the program notes", "reviewing the program notes", "past", "she"),
    ("Every Friday the curator", "unlocks the archive", "checks the humidity gauges", "rotate", "rotates the fragile prints", "rotating the fragile prints", "present", "she"),
    ("During the drought the farmers", "dug a deeper well", "mulched the orchard", "ration", "rationed water for the cattle", "rationing water for the cattle", "past", "they"),
]


@family(fill_in=True)
def par_verb_series(rng, difficulty):
    """Verbs in a series keep the same tense and form."""
    subj, v1, v2, base, right, ing, tense, pn = rng.choice(_PAR_VERB_SERIES)
    plural = pn == "they"
    correct = (right, f"Correct. The first two verbs are in the {tense} tense, so the third matches.")
    if tense == "present":
        other = (f"{base}ed" if not base.endswith("e") else f"{base}d")
    else:
        other = f"{base}s" if plural else f"{base}s"
    if tense == "present" and not plural:
        other = f"{base}ed" if not base.endswith("e") else f"{base}d"
    other_phrase = other + right[len(right.split()[0]):]
    ds = [(ing, "An -ing form breaks the series of finite verbs."),
          (other_phrase, f"This shifts tense; the series is in the {tense} tense."),
          (f"to {base}{right[len(right.split()[0]):]}", "An infinitive breaks the pattern of finite verbs.")]
    if difficulty != "easy":
        ds[2] = (f"{pn} {right}", "Adding a new subject turns the last item into a clause, breaking the series.")
    text = f"{subj} {v1}, {v2}, and ___."
    if difficulty == "hard":
        text = text + " " + rng.choice(["The work took all day.", "Nothing was left to chance.",
                                        "The routine never varies."])
    return build(rng, fill(text, conv_stem(rng)), correct, ds, subskill="parallel_structure",
                 explanation="Verbs in a series must share the same tense and form.",
                 tags=["conventions", "parallelism", "verb-series"], est=50)


@family(fill_in=False)
def par_whole_sentence(rng, difficulty):
    """Whole-sentence options: only one keeps the series parallel."""
    role = rng.choice(_PAR_ROLES)
    (g1, b1, p1, n1), (g2, b2, p2, n2), (g3, b3, p3, n3) = rng.sample(_PAR_ACTS, 3)
    lead = rng.choice([f"The {role} involves", f"Her duties in the {role} include",
                       f"The {role} mostly consists of"])
    correct = (f"{lead} {g1}, {g2}, and {g3}.", "Correct. All three items are -ing phrases.")
    ds = [(f"{lead} {g1}, {g2}, and to {b3}.", "The third item is an infinitive, breaking the pattern."),
          (f"{lead} {g1}, {n2}, and {g3}.", "The second item is a plain noun phrase, not an -ing phrase."),
          (f"{lead} {g1}, {g2}, and she {p3}.", "The third item is a clause with its own subject.")]
    if difficulty == "easy":
        ds[1] = (f"{lead} {g1}, {p2}, and {g3}.", "The second item is a past-tense verb, not an -ing phrase.")
    stem = rng.choice(["Which choice keeps the items in the series parallel?",
                       "Which version of the sentence conforms to the conventions of Standard English?"])
    return build(rng, stem, correct, ds, subskill="parallel_structure",
                 explanation="Every item in a series must take the same grammatical form.",
                 tags=["conventions", "parallelism", "whole-sentence"], est=55)


_PAR_PASS = [
    ("The community garden opened with twelve plots.", "Members spend their Saturdays {a}, {b}, and ___.",
     "Surplus vegetables go to a food bank.",
     [("weeding the beds", "weed the beds", "weeded the beds"), ("watering seedlings", "water seedlings", "watered seedlings"),
      ("trading tips with neighbors", "trade tips with neighbors", "traded tips with neighbors"),
      ("repairing the fence", "repair the fence", "repaired the fence")]),
    ("The expedition reached base camp on the third day.", "From there, the climbers planned to {a}, {b}, and ___.",
     "Weather delayed them a week.",
     [("rest for a day", "resting for a day", "rested for a day"), ("sort their gear", "sorting their gear", "sorted their gear"),
      ("scout the upper route", "scouting the upper route", "scouted the upper route"),
      ("cache extra food", "caching extra food", "cached extra food")]),
    ("The museum's conservation lab is open to visitors on Fridays.", "Guests can watch the staff {a}, {b}, and ___.",
     "Tours fill up weeks ahead.",
     [("clean old canvases", "cleaning old canvases", "cleaned old canvases"), ("repair torn pages", "repairing torn pages", "repaired torn pages"),
      ("rebind damaged books", "rebinding damaged books", "rebound damaged books"),
      ("test pigments", "testing pigments", "tested pigments")]),
    ("Rosa's bakery runs on a strict morning routine.", "By six she has {a}, {b}, and ___.",
     "The doors open at seven.",
     [("shaped the loaves", "shaping the loaves", "shape the loaves"), ("lit the ovens", "lighting the ovens", "light the ovens"),
      ("brewed the first coffee", "brewing the first coffee", "brew the first coffee"),
      ("swept the front step", "sweeping the front step", "sweep the front step")]),
]


@family(fill_in=True)
def par_passage(rng, difficulty):
    """Mini passage; the series with the blank sits in the middle sentence."""
    lead, mid, close, items = rng.choice(_PAR_PASS)
    (a_r, a_w1, a_w2), (b_r, b_w1, b_w2), (c_r, c_w1, c_w2) = rng.sample(items, 3)
    text = mid.format(a=a_r, b=b_r)
    correct = (c_r, f"Correct. '{c_r}' matches the form of '{a_r}' and '{b_r}'.")
    ds = [(c_w1, "This form does not match the first two items in the series."),
          (c_w2, "This form breaks the pattern set by the first two items."),
          (f"also {c_w1}", "Adding 'also' does not fix the mismatched form.")]
    if difficulty == "hard":
        ds[2] = (f"they {c_w2}" if "has" not in mid else f"she {c_w2}",
                 "A clause with its own subject breaks the series of matching phrases.")
    if difficulty == "easy":
        full = f"{lead} {text}"
    else:
        full = f"{lead} {text} {close}"
    return build(rng, fill(full, conv_stem(rng)), correct, ds, subskill="parallel_structure",
                 explanation="The blank completes a series, so it must match the form of the earlier items.",
                 tags=["conventions", "parallelism", "passage"], est=55)


# =========================================================================== #
# PRONOUN-ANTECEDENT AGREEMENT
# =========================================================================== #
_PA_SING = ["The company", "The team", "The committee", "The school", "The city",
            "The orchestra", "The museum", "The agency", "The university", "The startup",
            "The clinic", "The council"]
_PA_PLUR = ["The players", "The teachers", "The volunteers", "The residents", "The scientists",
            "The workers", "The artists", "Both companies", "The members", "The engineers",
            "The students", "The farmers", "The divers", "The founders"]
_PA_TAILS = ["released ___ annual report on time", "celebrated ___ hard-won victory",
             "updated ___ official website", "defended ___ final decision",
             "published ___ research findings", "expanded ___ original plan",
             "renamed ___ summer program", "opened ___ doors to the public"]
_PA_BAIT_SHORT = {"plural": ["of the two founders", "with the regional offices", "near the rival teams",
                             "from the three towns"],
                  "singular": ["on the national team", "from the central office", "in the league",
                               "at the main campus"]}
_PA_BAIT_LONG = {"plural": ["along with several partner organizations that joined last year",
                            "together with the dozens of branches it had opened abroad",
                            "despite objections from the neighboring districts"],
                 "singular": ["which had grown out of a single research lab downtown",
                              "as part of the larger national federation it belonged to",
                              "after a long meeting with the regional director"]}


@family(fill_in=True)
def pa_possessive(rng, difficulty):
    """its vs. their, with an opposite-number noun between antecedent and pronoun."""
    plural = rng.random() < 0.5
    ante = rng.choice(_PA_PLUR if plural else _PA_SING)
    bait = "singular" if plural else "plural"
    if difficulty == "easy":
        mid = ""
    elif difficulty == "medium":
        mid = " " + rng.choice(_PA_BAIT_SHORT[bait])
    else:
        mid = ", " + rng.choice(_PA_BAIT_LONG[bait]) + ","
    tail = rng.choice(_PA_TAILS)
    right = "their" if plural else "its"
    wrong = "its" if plural else "their"
    num = "plural" if plural else "singular"
    correct = (right, f"Correct. '{ante}' is {num}, so the pronoun is '{right}'.")
    ds = [(wrong, f"Agreement error: '{ante}' is {num}, so the pronoun must be '{right}', not '{wrong}'."),
          ("it's", "'it's' means 'it is' and is not a possessive pronoun."),
          ("they're", "'they're' means 'they are' and is not a possessive pronoun.")]
    text = f"{ante}{mid} {tail}."
    return build(rng, fill(text, conv_stem(rng)), correct, ds, subskill="pronoun_antecedent",
                 explanation=f"A possessive pronoun agrees with its antecedent in number: '{ante}' takes '{right}'.",
                 tags=["conventions", "pronoun-antecedent"])


_PA_SUBJ_FRAMES = [
    ("When {A} met last week,", "voted to extend the season"),
    ("After {A} reviewed the plans,", "asked for a second survey"),
    ("Once {A} finished the tour,", "posted photographs online"),
    ("Although {A} expected delays,", "finished ahead of schedule"),
    ("Because {A} needed more space,", "moved to a larger building"),
    ("As soon as {A} received the grant,", "ordered new equipment"),
]
_PA_SUBJ_SING = ["the committee", "the team", "the orchestra", "the company", "the agency",
                 "the council", "the startup", "the clinic", "the choir", "the museum"]
_PA_SUBJ_PLUR = ["the players", "the volunteers", "the scientists", "the engineers",
                 "the students", "the founders", "the divers", "the members", "the singers",
                 "the curators"]
_PA_SUBJ_BAIT = {"plural": {"short": ["with offices in three towns", "of forty members",
                                      "with dozens of volunteers"],
                            "long": ["which had grown out of a single research lab downtown",
                                     "together with the dozens of branches it had opened abroad"]},
                 "singular": {"short": ["from the main office", "on the night shift", "in the league"],
                              "long": ["along with a partner organization that joined last year",
                                       "despite objections from the neighboring district"]}}


@family(fill_in=True)
def pa_subject(rng, difficulty):
    """it / they as the subject referring back to a singular or plural noun."""
    plural = rng.random() < 0.5
    ante = rng.choice(_PA_SUBJ_PLUR if plural else _PA_SUBJ_SING)
    frame, pred = rng.choice(_PA_SUBJ_FRAMES)
    right = "they" if plural else "it"
    wrong = "it" if plural else "they"
    num = "plural" if plural else "singular"
    ante = cap(ante)
    correct = (right, f"Correct. '{ante}' is {num}, so the subject pronoun is '{right}'.")
    ds = [(wrong, f"'{wrong}' does not agree with the {num} antecedent '{ante}'."),
          ("them" if plural else "its", "This form cannot be the subject of the clause."),
          ("one" if not plural else "those", "This pronoun does not refer clearly back to the antecedent.")]
    a_low = low(ante)
    text = f"{cap(frame.format(A=a_low))} ___ {pred}."
    bait_num = "singular" if plural else "plural"
    if difficulty == "medium":
        bait = rng.choice(_PA_SUBJ_BAIT[bait_num]["short"])
        text = f"{cap(frame.format(A=a_low + ' ' + bait))} ___ {pred}."
    elif difficulty == "hard":
        bait = rng.choice(_PA_SUBJ_BAIT[bait_num]["long"])
        text = f"{cap(frame.format(A=a_low + ', ' + bait + ','))} ___ {pred}."
    return build(rng, fill(text, conv_stem(rng)), correct, ds, subskill="pronoun_antecedent",
                 explanation=f"The pronoun refers to '{ante}', which is {num}, so '{right}' is required.",
                 tags=["conventions", "pronoun-antecedent", "subject-pronoun"])


_PA_AMBIG = [
    ("When {A} handed {B} the report,", "noticed a typo on the first page", "B"),
    ("After {A} called {B} about the schedule,", "agreed to switch shifts", "B"),
    ("Before {A} interviewed {B},", "reviewed the application twice", "A"),
    ("Although {A} had coached {B} for years,", "never mentioned the award", "A"),
    ("Once {A} emailed {B} the directions,", "left for the airport", "B"),
    ("While {A} was tutoring {B},", "kept checking the clock", "B"),
]


@family(fill_in=True)
def pa_ambiguous(rng, difficulty):
    """Two possible antecedents: the clear choice repeats the noun."""
    frame, pred, who = rng.choice(_PA_AMBIG)
    group = [n for n in _NAMES if pron(n)[0] == rng.choice(["she", "he"])]
    a, b = rng.sample(group, 2)
    target = a if who == "A" else b
    s, o, p, r = pron(target)
    other = b if who == "A" else a
    text = frame.format(A=a, B=b) + " ___ " + pred + "."
    correct = (target, f"Correct. Naming {target} makes clear who {pred.split()[0]} "
                       f"{' '.join(pred.split()[1:])}; a pronoun could refer to either person.")
    ds = [(s, f"'{s}' could refer to either {a} or {b}, so the reference is ambiguous."),
          (f"{s} {r}", f"Even with the emphatic '{r}', '{s}' could still be either {a} or {b}."),
          (o, f"'{o}' is objective case and cannot be the subject of the clause.")]
    if difficulty == "hard":
        text = text + " " + rng.choice(["The matter was dropped.", "Neither mentioned it again.",
                                        "The mistake was fixed by noon."])
    elif difficulty == "medium":
        text = rng.choice(["Later that week, ", "On Monday, ", "That afternoon, "]) + low(text)
    return build(rng, fill(text, conv_stem(rng)), correct, ds, subskill="pronoun_antecedent",
                 explanation=("A pronoun must point to exactly one antecedent; when two nouns could "
                              "be its referent, repeat the intended noun instead."),
                 tags=["conventions", "pronoun-antecedent", "ambiguous"], est=50)


_PA_PASS = [
    ("The orchestra toured for six weeks last spring.", "By the final concert, ___ members were exhausted", "its",
     "Recordings from the tour were released in June."),
    ("The city's three public pools open on the first of June.", "Lifeguards inspect ___ filters every morning", "their",
     "Attendance peaks in late July."),
    ("The committee met for nine hours on Tuesday.", "At midnight ___ finally approved the budget", "it",
     "The vote was unanimous."),
    ("Two rival bakeries share a wall on Elm Street.", "Every morning ___ ovens heat the whole block", "their",
     "Neighbors say they do not mind."),
    ("The research station sits above the Arctic Circle.", "During the winter ___ crew drops to six people", "its",
     "Supplies arrive twice a year."),
    ("The volunteers arrived before sunrise.", "Within an hour ___ had cleared the entire beach", "they",
     "The city sent a thank-you note."),
    ("The museum's oldest gallery was closed for a year.", "When ___ reopened, the ceiling had been restored", "it",
     "Visitors lined up around the block."),
    ("The founders of the company still work in the original garage.", "Most mornings ___ arrive before the staff", "they",
     "The garage is now a small museum."),
    ("The town's weather station has operated since 1952.", "Every morning ___ readings are posted at the post office", "its",
     "Farmers still check them before planting."),
    ("The twin lighthouses guard the northern channel.", "On foggy nights ___ horns sound every thirty seconds", "their",
     "Ships still rely on them."),
    ("The robotics club meets in a converted woodshop.", "Last month ___ won a regional title", "it",
     "A banner now hangs in the lobby."),
    ("The divers mapped the sunken ferry over two summers.", "By the second August ___ had photographed every deck", "they",
     "A museum has asked to display the images."),
]


@family(fill_in=True, small_space=True)
def pa_passage(rng, difficulty):
    """Antecedent in the previous sentence; pronoun in the middle sentence."""
    lead, mid, right, close = rng.choice(_PA_PASS)
    plural = right in ("their", "they")
    num = "plural" if plural else "singular"
    kind = "possessive" if right in ("its", "their") else "subject"
    if kind == "possessive":
        wrong = "its" if plural else "their"
        ds = [(wrong, f"'{wrong}' does not agree with the {num} antecedent in the previous sentence."),
              ("it's" if not plural else "they're", "This is a contraction, not a possessive."),
              ("there", "'there' is not a possessive pronoun.")]
    else:
        wrong = "it" if plural else "they"
        ds = [(wrong, f"'{wrong}' does not agree with the {num} antecedent in the previous sentence."),
              ("them" if plural else "its", "This form cannot be the subject of the clause."),
              ("one", "'one' does not refer back clearly to the antecedent.")]
    correct = (right, f"Correct. The pronoun refers to a {num} noun in the previous sentence, so '{right}' agrees.")
    text = f"{lead} {mid}." if difficulty == "easy" else f"{lead} {mid}. {close}"
    if difficulty == "hard":
        text = f"{lead} " + rng.choice(["As the local paper reported, ", "Not surprisingly, ",
                                        "According to the staff, "]) + low(mid) + f". {close}"
    return build(rng, fill(text, conv_stem(rng)), correct, ds, subskill="pronoun_antecedent",
                 explanation=("Find the noun the pronoun stands for, even when it is in the previous "
                              f"sentence; it is {num}, so the pronoun must be {num} too."),
                 tags=["conventions", "pronoun-antecedent", "passage"], est=55)


@family(fill_in=False)
def pa_whole_sentence(rng, difficulty):
    """Whole-sentence options; only one keeps every pronoun agreeing with its noun."""
    plural = rng.random() < 0.5
    ante = rng.choice(_PA_PLUR if plural else _PA_SING)
    tail = rng.choice(_PA_TAILS)
    right = "their" if plural else "its"
    wrong = "its" if plural else "their"
    mid = "" if difficulty == "easy" else " " + rng.choice(_PA_BAIT_SHORT["singular" if plural else "plural"])
    def sent(pr):
        return f"{ante}{mid} {tail.replace('___', pr)}."
    correct = (sent(right), f"Correct. '{right}' agrees with the {'plural' if plural else 'singular'} '{ante}'.")
    ds = [(sent(wrong), f"'{wrong}' does not agree with '{ante}'."),
          (sent("it's" if not plural else "they're"), "A contraction cannot show possession."),
          (sent("there"), "'there' is not a possessive pronoun.")]
    stem = rng.choice(["Which version of the sentence conforms to the conventions of Standard English?",
                       "In which choice does the pronoun agree with its antecedent?"])
    return build(rng, stem, correct, ds, subskill="pronoun_antecedent",
                 explanation=f"The possessive pronoun must match '{ante}' in number.",
                 tags=["conventions", "pronoun-antecedent", "whole-sentence"], est=50)


# =========================================================================== #
# QUANTITATIVE COMMAND OF EVIDENCE (table stimulus; numbers are computed)
# =========================================================================== #
_QE_TOPICS = [
    ("Annual rainfall", "the city", "millimeters", "rose"),
    ("Library visits", "the downtown branch", "thousand", "increased"),
    ("Solar installations", "the county", "units", "grew"),
    ("Recycling rate", "the town", "percent", "climbed"),
    ("Average commute", "the metro area", "minutes", "fell"),
    ("Wetland bird species", "the reserve", "species", "increased"),
    ("Ticket sales", "the festival", "thousand", "rose"),
    ("Coral cover", "the reef", "percent", "declined"),
    ("Bicycle trips", "the river district", "thousand", "rose"),
    ("Water use", "the campus", "million liters", "fell"),
]
_QE_STEMS = ["Which choice best uses data from the table to support the researcher's claim?",
             "Which statement is best supported by the data in the table?",
             "Which finding from the table most directly supports the claim?"]
# (label, plural label, category names, measure, unit)
_QE_CATS = [
    ("Region", "regions", ["North", "South", "East", "West", "Central"], "share of households with solar panels", "percent"),
    ("Species", "species", ["Oak", "Maple", "Birch", "Pine", "Elm"], "seedling survival rate", "percent"),
    ("Branch", "branches", ["Harbor", "Hillside", "Downtown", "Riverside", "Eastgate"], "monthly visitor count", "thousand"),
    ("Crop", "crops", ["Wheat", "Barley", "Oats", "Rye", "Corn"], "yield per acre", "bushels"),
    ("Team", "teams", ["Falcons", "Otters", "Comets", "Herons", "Badgers"], "points scored", "points"),
    ("Material", "materials", ["Glass", "Paper", "Plastic", "Metal", "Textiles"], "share recycled", "percent"),
]


def _poss(name):
    return name + ("'" if name.endswith("s") else "'s")


def _qe_table(caption, headers, rows):
    return {"type": "table", "table": {"caption": caption, "headers": headers,
                                       "rows": [[str(c) for c in r] for r in rows]}}


def _qe_mc(rng, prompt, correct, ds, stimulus, explanation, est=80):
    return build(rng, prompt, correct, ds, subskill="quantitative_evidence",
                 qtype="data_interpretation", explanation=explanation,
                 tags=["reading", "evidence", "quantitative"], est=est, stimulus=stimulus)


@family(fill_in=False)
def qe_trend(rng, difficulty):
    """Steady one-direction trend over several years."""
    metric, place, unit, verb = rng.choice(_QE_TOPICS)
    rising = verb in ("rose", "increased", "grew", "climbed")
    n = {"easy": 4, "medium": 5, "hard": 6}[difficulty]
    y0 = 2016 + rng.randint(0, 3)
    years = [y0 + i for i in range(n)]
    if difficulty == "easy":
        start = rng.randint(20, 60)
        steps = [rng.choice([3, 4, 5, 6, 8])] * (n - 1)
    elif difficulty == "medium":
        start = rng.randint(40, 120)
        steps = [rng.choice([4, 6, 8, 10]) for _ in range(n - 1)]
    else:
        start = rng.randint(120, 400)
        steps = [rng.choice([7, 9, 11, 15, 20]) for _ in range(n - 1)]
    if unit == "percent":
        start = rng.randint(10, 35)
        steps = [max(2, st // 3) for st in steps]
    asc = [start]
    for st in steps:
        asc.append(asc[-1] + st)
    vals = asc if rising else asc[::-1]
    rows = [[y, v] for y, v in zip(years, vals)]
    first, last = vals[0], vals[-1]
    direction, opp = ("up", "down") if rising else ("down", "up")
    dir_verb = rng.choice(["rose", "increased", "climbed"] if rising else ["fell", "declined", "dropped"])
    avg_step = round(abs(last - first) / (n - 1))
    max_step = max(steps)
    big = max_step + rng.choice([10, 15, 20])
    midi = n // 2
    mid_year, mid_val = years[midi], vals[midi]
    claim = (f"A researcher claims that {metric.lower()} in {place} {verb} steadily from "
             f"{years[0]} to {years[-1]}.")
    correct_text = rng.choice([
        f"From {years[0]} to {years[-1]}, the value {dir_verb} every year, going from {first} to {last} {unit}.",
        f"The value {dir_verb} each year, moving from {first} to {last} {unit} over the period.",
        f"Year over year the figure {dir_verb}, reaching {last} {unit} by {years[-1]} from {first} {unit}.",
        f"Across all {n} years shown, the value {dir_verb} from {first} to {last} {unit}.",
    ])
    correct = (correct_text, "Correct. This matches the steady, one-direction trend across every year shown.")
    pool = {
        "steady": (f"The value held steady near {first} {unit} for most of the span before a single "
                   f"change late in {years[-1]}.", "The table shows the value changing every year, not holding steady."),
        "peaked": (f"It peaked in {mid_year} at {mid_val} {unit} and then reversed course for the rest "
                   "of the period.", "The largest value is at an endpoint, not the middle year."),
        "mixed": (f"In some years the value moved {opp} and in others {direction}, rather than in a "
                  "single direction.", "Every year moves the same direction, so this misreads the table."),
        "constant": (f"The value changed by the same amount every year, a constant {avg_step} {unit} per year.",
                     f"The year-to-year changes vary, so the change was not a constant {avg_step} {unit}."),
        "subset": (f"Almost all of the change happened between {years[0]} and {years[1]}, with little "
                   "movement afterward.", "The value changes in every year shown, not just the first span."),
        "bigjump": (f"The value {dir_verb} by more than {big} {unit} in a single year.",
                    f"The largest one-year change was only {max_step} {unit}."),
    }
    keys = {"easy": ["steady", "peaked", "mixed"], "medium": ["constant", "peaked", "mixed"],
            "hard": ["constant", "subset", "bigjump"]}[difficulty]
    ds = [pool[k] for k in keys]
    prompt = f"{claim}\n\n{rng.choice(_QE_STEMS)}"
    return _qe_mc(rng, prompt, correct, ds,
                  _qe_table(f"{metric} in {place} ({unit})", ["Year", metric], rows),
                  "The supporting statement must reflect the table's actual, consistent trend "
                  "across all the years shown.")


@family(fill_in=False)
def qe_category_max(rng, difficulty):
    """Bar-style read: which category is largest/smallest, by how much."""
    label, plural, cats, measure, unit = rng.choice(_QE_CATS)
    k = {"easy": 3, "medium": 4, "hard": 5}[difficulty]
    names = rng.sample(cats, k)
    vals = rng.sample(range(12, 90), k)
    rows = list(zip(names, vals))
    hi = max(rows, key=lambda r: r[1])
    lo = min(rows, key=lambda r: r[1])
    second = sorted(rows, key=lambda r: -r[1])[1]
    gap = hi[1] - lo[1]
    claim = rng.choice([
        f"A student argues that the {measure} varied considerably across the {plural} studied.",
        f"A report claims that one {label.lower()} stood out from the others in {measure}.",
    ])
    correct_text = rng.choice([
        f"{hi[0]} had the highest {measure}, at {hi[1]} {unit}, while {lo[0]} had the lowest, at {lo[1]} {unit}.",
        f"At {hi[1]} {unit}, {hi[0]} exceeded the lowest {label.lower()}, {lo[0]}, by {gap} {unit}.",
        f"{_poss(hi[0])} figure ({hi[1]} {unit}) was {gap} {unit} higher than {_poss(lo[0])}.",
    ])
    correct = (correct_text, "Correct. These figures are read directly from the table and compare "
                             "the highest and lowest values.")
    ds = [(f"{lo[0]} had the highest {measure}, at {lo[1]} {unit}, while {hi[0]} had the lowest, at {hi[1]} {unit}.",
           f"This reverses the table: {hi[0]} had the highest value and {lo[0]} the lowest."),
          (f"{second[0]} led all {plural} with {second[1]} {unit}, ahead of {hi[0]} at {hi[1]} {unit}.",
           f"{second[0]} was second; {hi[0]} had the highest value, {hi[1]} {unit}."),
          (f"Every {label.lower()} recorded roughly the same {measure}, within a few {unit} of {hi[1]} {unit}.",
           f"The values range from {lo[1]} to {hi[1]} {unit}, so they are not roughly the same.")]
    if difficulty == "hard":
        ds[2] = (f"At {hi[1]} {unit}, {hi[0]} exceeded the lowest {label.lower()}, {lo[0]}, by {gap + rng.choice([5, 8, 10])} {unit}.",
                 f"The actual gap is {hi[1]} − {lo[1]} = {gap} {unit}.")
    prompt = (f"{claim}\n\n" + rng.choice([
        "Which choice most effectively uses data from the table to support the claim?",
        "Which statement about the data in the table is accurate?"]))
    return _qe_mc(rng, prompt, correct, ds,
                  _qe_table(f"{cap(measure)} by {label.lower()} ({unit})", [label, cap(measure)], rows),
                  "Find the largest and smallest values in the table and check each statement's "
                  "numbers against them.")


@family(fill_in=False)
def qe_compare_two(rng, difficulty):
    """Two categories tracked over the same years; compare them."""
    label, plural, cats, measure, unit = rng.choice(_QE_CATS)
    a, b = rng.sample(cats, 2)
    n = {"easy": 3, "medium": 4, "hard": 5}[difficulty]
    y0 = 2017 + rng.randint(0, 3)
    years = [y0 + i for i in range(n)]
    base_a = rng.randint(30, 60)
    # b starts far enough ahead that a (rising <=4/yr) cannot pass b (falling <=2/yr)
    # before the final year, where the hard tier forces a crossing.
    base_b = base_a + rng.randint(6 * (n - 1) + 2, 6 * (n - 1) + 12)
    a_vals = [base_a + i * rng.choice([2, 3, 4]) for i in range(n)]
    b_vals = [base_b - i * rng.choice([1, 2]) for i in range(n)]
    if difficulty == "hard":
        # make the lines cross in the final year
        b_vals[-1] = a_vals[-1] - rng.randint(1, 4)
    rows = [[y, av, bv] for y, av, bv in zip(years, a_vals, b_vals)]
    crossed = b_vals[-1] < a_vals[-1]
    a_change = a_vals[-1] - a_vals[0]
    b_change = b_vals[0] - b_vals[-1]
    claim = f"A researcher claims that the gap between {b} and {a} in {measure} has been closing."
    if crossed:
        correct_text = rng.choice([
            f"{b} led in every year until {years[-1]}, when {a} moved ahead, {a_vals[-1]} to {b_vals[-1]} {unit}.",
            f"By {years[-1]}, {a} ({a_vals[-1]} {unit}) had overtaken {b} ({b_vals[-1]} {unit}).",
        ])
        ds = [(f"{b} exceeded {a} in every year shown, finishing {years[-1]} at {b_vals[-1]} {unit} to {_poss(a)} {a_vals[-1]}.",
               f"In {years[-1]} {a} was ahead, {a_vals[-1]} to {b_vals[-1]}."),
              (f"{a} led {b} throughout the period, from {years[0]} ({a_vals[0]} {unit}) through {years[-1]} ({a_vals[-1]} {unit}).",
               f"{b} was ahead in every year before {years[-1]}."),
              (f"The gap between {a} and {b} widened each year, reaching its largest in {years[-1]}.",
               "The gap shrank and then reversed.")]
    else:
        gap0, gap1 = b_vals[0] - a_vals[0], b_vals[-1] - a_vals[-1]
        correct_text = rng.choice([
            f"The gap between {b} and {a} narrowed from {gap0} {unit} in {years[0]} to {gap1} {unit} in {years[-1]}.",
            f"{a} rose by {a_change} {unit} over the period while {b} fell by {b_change} {unit}.",
            f"{b} stayed ahead in every year, but its lead shrank from {gap0} to {gap1} {unit}.",
        ])
        ds = [(f"{a} exceeded {b} in {years[-1]}, finishing at {a_vals[-1]} {unit} to {_poss(b)} {b_vals[-1]} {unit}.",
               f"{b} was still ahead in {years[-1]}, {b_vals[-1]} to {a_vals[-1]}."),
              (f"The gap between {b} and {a} widened from {gap0} {unit} in {years[0]} to {gap0 + 4} {unit} in {years[-1]}.",
               f"The gap actually narrowed to {gap1} {unit}."),
              (f"{b} rose every year while {a} fell, so {b} pulled further ahead over the period.",
               f"{a} rose and {b} fell, the opposite of this statement.")]
    correct = (correct_text, "Correct. The statement matches the two columns year by year.")
    prompt = f"{claim}\n\n{rng.choice(_QE_STEMS)}"
    return _qe_mc(rng, prompt, correct, ds,
                  _qe_table(f"{cap(measure)} ({unit})", ["Year", a, b], rows),
                  "Compare the two columns in each row; note which is larger and how the "
                  "difference changes over time.")


@family(fill_in=False)
def qe_undermine(rng, difficulty):
    """Which data point most directly weakens a sweeping claim?"""
    label, plural, cats, measure, unit = rng.choice(_QE_CATS)
    k = {"easy": 3, "medium": 4, "hard": 5}[difficulty]
    names = rng.sample(cats, k)
    y1, y2 = 2019 + rng.randint(0, 2), 2022 + rng.randint(0, 2)
    rows = []
    for nm in names:
        v1 = rng.randint(20, 70)
        v2 = v1 + rng.randint(3, 15)
        rows.append([nm, v1, v2])
    odd = rng.randrange(k)
    drop = rng.randint(2, 9)
    rows[odd][2] = rows[odd][1] - drop
    claim = f"A columnist claims that the {measure} improved for every {label.lower()} between {y1} and {y2}."
    o = rows[odd]
    correct_text = rng.choice([
        f"{o[0]} fell from {o[1]} to {o[2]} {unit}, so not every {label.lower()} improved.",
        f"For {o[0]}, the {y2} figure ({o[2]} {unit}) is lower than the {y1} figure ({o[1]} {unit}).",
        f"{o[0]} declined by {drop} {unit} over the period.",
    ])
    correct = (correct_text, "Correct. One category moved the opposite way, which directly contradicts "
                             "the claim that every category improved.")
    others = [r for i, r in enumerate(rows) if i != odd]
    r1 = others[0]
    r2 = others[1] if len(others) > 1 else others[0]
    ds = [(f"{r1[0]} rose from {r1[1]} to {r1[2]} {unit} between {y1} and {y2}, the pattern the columnist describes.",
           "This supports the claim rather than weakening it."),
          (f"{r2[0]} improved by {r2[2] - r2[1]} {unit}, one of the gains the columnist points to.",
           "This is consistent with the claim; it does not undermine it."),
          (f"The average across all {plural} was higher in {y2} than in {y1}, as the columnist suggests.",
           "An average can rise even when one category falls; it does not test the word 'every'.")]
    prompt = (f"{claim}\n\n" + rng.choice([
        "Which choice uses data from the table to most directly challenge the columnist's claim?",
        "Which finding from the table most effectively undermines the claim?"]))
    return _qe_mc(rng, prompt, correct, ds,
                  _qe_table(f"{cap(measure)} ({unit})", [label, str(y1), str(y2)], rows),
                  "A claim about 'every' category is disproved by a single category that moved "
                  "the other way; find the row whose value fell.")


@family(fill_in=False)
def qe_support_point(rng, difficulty):
    """Which single data point best supports a specific claim?"""
    label, plural, cats, measure, unit = rng.choice(_QE_CATS)
    k = {"easy": 3, "medium": 4, "hard": 5}[difficulty]
    names = rng.sample(cats, k)
    vals = rng.sample(range(15, 85), k)
    rows = list(zip(names, vals))
    srt = sorted(rows, key=lambda r: r[1])
    lo, hi = srt[0], srt[-1]
    mid = srt[len(srt) // 2]
    kind = rng.choice(["lowest", "highest"])
    tgt = lo if kind == "lowest" else hi
    thresh = (tgt[1] + rng.choice([3, 5, 8])) if kind == "lowest" else (tgt[1] - rng.choice([3, 5, 8]))
    claim = (f"A writer argues that {tgt[0]} lags well behind the other {plural} in {measure}."
             if kind == "lowest" else
             f"A writer argues that {tgt[0]} leads the other {plural} in {measure}.")
    nxt = srt[1] if kind == "lowest" else srt[-2]
    correct_text = rng.choice([
        f"{tgt[0]} recorded {tgt[1]} {unit}, the {kind} value of any {label.lower()} in the table.",
        f"At {tgt[1]} {unit}, {tgt[0]} was {abs(nxt[1] - tgt[1])} {unit} {'below' if kind == 'lowest' else 'above'} the next-{kind} {label.lower()}, {nxt[0]}.",
    ])
    correct = (correct_text, f"Correct. {tgt[0]}'s figure is the {kind} in the table, which is exactly what the claim needs.")
    ds = [(f"{mid[0]} recorded {mid[1]} {unit}, placing it near the middle of the {plural} shown.",
           f"{mid[0]}'s value says nothing about {tgt[0]}."),
          (f"{tgt[0]} recorded {thresh} {unit}, the {kind} value of any {label.lower()} in the table.",
           f"The table shows {tgt[1]} {unit} for {tgt[0]}, not {thresh}."),
          (f"{nxt[0]} recorded the {kind} value, {nxt[1]} {unit}, with {tgt[0]} next at {tgt[1]} {unit}.",
           f"{nxt[0]} is not the {kind}; {tgt[0]} is, at {tgt[1]} {unit}.")]
    prompt = (f"{claim}\n\n" + rng.choice([
        "Which choice most effectively uses data from the table to support the writer's claim?",
        "Which data point from the table best supports the claim?"]))
    return _qe_mc(rng, prompt, correct, ds,
                  _qe_table(f"{cap(measure)} by {label.lower()} ({unit})", [label, cap(measure)], rows),
                  f"The claim concerns {tgt[0]} specifically, so the supporting data must be "
                  f"{tgt[0]}'s own value and its rank among the others.")


# =========================================================================== #
# v2.1 ADDITIONS — VERB TENSE
# =========================================================================== #
_COND = [
    ("If I ___ you, I would take the earlier train.", "were", ["was", "am", "would be"],
     "A wish or a situation contrary to fact uses the subjunctive 'were'."),
    ("If the bridge ___ wider, trucks could use it.", "were", ["was", "is", "would be"],
     "The bridge is not wider, so the contrary-to-fact subjunctive 'were' is required."),
    ("The coach insisted that every player ___ on time.", "be", ["is", "was", "will be"],
     "After verbs of demand such as 'insist that,' the base form (subjunctive) is used."),
    ("The committee recommended that the museum ___ its hours.", "extend", ["extends", "extended", "will extend"],
     "After 'recommend that,' the base form of the verb is used."),
    ("If {N} ___ the deadline, the grant would already be approved.", "had met", ["met", "has met", "would meet"],
     "A past condition that did not happen takes the past perfect ('had met') with 'would' in the main clause."),
    ("If the ferry ___ on time, we would have caught the last bus.", "had left", ["left", "has left", "would leave"],
     "An unreal past condition takes the past perfect."),
    ("It is essential that the sample ___ frozen immediately.", "be", ["is", "was", "will be"],
     "After 'it is essential that,' the subjunctive base form is used."),
    ("If the river ___ to rise overnight, the lower road would close.", "were", ["was", "is", "will be"],
     "A hypothetical future uses 'were to.'"),
    ("The judge requested that the witness ___ her answer.", "repeat", ["repeats", "repeated", "will repeat"],
     "After 'request that,' the base form is used."),
    ("If {N} ___ here now, she would know what to do.", "were", ["was", "is", "had been"],
     "A present situation contrary to fact uses 'were.'"),
    ("The director demanded that the set ___ finished by Friday.", "be", ["is", "was", "will be"],
     "After 'demand that,' the subjunctive base form 'be' is used."),
    ("The board suggested that the museum ___ free on Sundays.", "be", ["is", "was", "will be"],
     "After 'suggest that,' the base form is used."),
    ("The rules require that each entry ___ original.", "be", ["is", "was", "will be"],
     "After 'require that,' the base form is used."),
    ("The guide asked that visitors ___ quiet in the nursery.", "remain", ["remains", "remained", "will remain"],
     "After 'ask that,' the base form is used."),
]


@family(fill_in=True)
def vt_conditional(rng, difficulty):
    """Conditionals and the subjunctive (if I were, insist that he be, had met)."""
    pool = _COND if difficulty != "easy" else [c for c in _COND if c[1] in ("were", "be")]
    frame, right, wrongs, rule = rng.choice(pool)
    name = rng.choice(_NAMES)
    text = frame.format(N=name)
    correct = (right, f"Correct. {rule}")
    ds = [(w, f"'{w}' is the ordinary indicative form; this construction calls for '{right}'.") for w in wrongs]
    if difficulty == "hard":
        text = rng.choice(["As she later admitted, ", "Looking back, ", "Everyone agreed: "]) + soft_low(text)
    return build(rng, fill(text, conv_stem(rng)), correct, ds, subskill="verb_tense",
                 explanation=rule, tags=["conventions", "verb-tense", "subjunctive"])


_FUT_PERF = [
    ("By 2030, the lab", "publish", "its hundredth paper"),
    ("By the time the ferry docks, the storm", "pass", "over the island"),
    ("By next spring, the volunteers", "plant", "ten thousand trees"),
    ("By the end of the tour, the choir", "sing", "in twelve cities"),
    ("By noon tomorrow, the crew", "repair", "the last section of track"),
    ("By the time you read this, the comet", "fade", "from view"),
    ("By 2040, the glacier", "retreat", "another mile"),
    ("By the final whistle, the goalkeeper", "face", "forty shots"),
    ("By the time the exhibit opens, the curators", "label", "every case"),
    ("By midnight, the bakers", "shape", "three hundred loaves"),
    ("By the end of the decade, the town", "replace", "every wooden bridge"),
    ("By the time the ferry returns, the tide", "turn", "twice"),
]
_FP_PP = {"publish": "published", "pass": "passed", "plant": "planted", "sing": "sung", "repair": "repaired",
          "fade": "faded", "retreat": "retreated", "face": "faced", "label": "labeled", "shape": "shaped",
          "replace": "replaced", "turn": "turned"}
_FP_S3 = {"publish": "publishes", "pass": "passes", "plant": "plants", "sing": "sings", "repair": "repairs",
          "fade": "fades", "retreat": "retreats", "face": "faces", "label": "labels", "shape": "shapes",
          "replace": "replaces", "turn": "turns"}


@family(fill_in=True, small_space=True)
def vt_future_perfect(rng, difficulty):
    """'By <future time>' + an action completed before it -> future perfect."""
    lead, base, obj = rng.choice(_FUT_PERF)
    pp, s3 = _FP_PP[base], _FP_S3[base]
    plural = lead.split()[-1] in ("volunteers", "curators", "bakers")
    correct = ("will have " + pp, "Correct. An action that will be complete before a future point takes the "
                                  "future perfect: 'will have' + past participle.")
    ds = [("will " + base, "The simple future does not show that the action is finished by the stated time."),
          (("have " if plural else "has ") + pp, "The present perfect looks back from now, not from a future point."),
          ("would have been " + pp, "'would have been' belongs to hypothetical statements, not a plain prediction.")]
    if difficulty == "hard":
        ds[1] = ("will have been " + base + "ing" if not base.endswith("e") else "will have been " + base[:-1] + "ing",
                 "The progressive form stresses ongoing activity rather than completion by the deadline, "
                 "which the sentence's total requires.")
    text = f"{lead} ___ {obj}."
    if difficulty != "easy":
        text = text + " " + rng.choice(["The milestone has been long awaited.", "Few doubt the prediction.",
                                        "The pace has been steady."])
    return build(rng, fill(text, conv_stem(rng)), correct, ds, subskill="verb_tense",
                 explanation="'By <a future time>' marks a deadline; use the future perfect for what will be done by then.",
                 tags=["conventions", "verb-tense", "future-perfect"])


_REPORTED = [
    ("{N} said that the train", "was", "late", ["is", "will be", "being"], "past"),
    ("The guide explained that the castle", "was built", "in 1210", ["is built", "builds", "has built"], "past"),
    ("The forecaster warned that the storm", "would reach", "the coast by dawn", ["will reach", "reaches", "reaching"], "past"),
    ("The curator told us that the mural", "had been", "restored twice", ["has been", "is", "being"], "past"),
    ("{N} announced that the bakery", "would open", "a second shop", ["will open", "opens", "opening"], "past"),
    ("The teacher reminded the class that water", "boils", "at 100 degrees Celsius", ["boiled", "would boil", "boiling"], "fact"),
    ("The pilot reported that the runway", "was", "clear", ["is", "will be", "being"], "past"),
    ("The mayor admitted that the budget", "had run", "out in March", ["has run", "runs", "running"], "past"),
    ("The lecturer noted that light", "travels", "faster than sound", ["traveled", "would travel", "traveling"], "fact"),
    ("The coach said that the team", "had practiced", "in silence all week", ["has practiced", "practices", "practicing"], "past"),
]


@family(fill_in=True)
def vt_reported(rng, difficulty):
    """Tense in reported speech: shift back after a past reporting verb; general truths stay present."""
    pool = _REPORTED if difficulty != "easy" else [r for r in _REPORTED if r[4] == "past"]
    lead, right, obj, wrongs, kind = rng.choice(pool)
    name = rng.choice(_NAMES)
    text = f"{lead.format(N=name)} ___ {obj}."
    if kind == "past":
        rule = ("After a past-tense reporting verb ('said', 'explained'), the reported verb shifts back "
                "a tense as well.")
        correct = (right, f"Correct. {rule}")
        ds = [(w, f"'{w}' does not shift back to match the past reporting verb.") for w in wrongs]
    else:
        rule = "A general truth stays in the simple present even after a past reporting verb."
        correct = (right, f"Correct. {rule}")
        ds = [(w, f"'{w}' wrongly shifts a timeless fact out of the present tense.") for w in wrongs]
    if difficulty == "hard":
        text = text + " " + rng.choice(["Nobody questioned it.", "The remark was repeated later.",
                                        "The claim turned out to be right."])
    return build(rng, fill(text, conv_stem(rng)), correct, ds, subskill="verb_tense",
                 explanation=rule, tags=["conventions", "verb-tense", "reported-speech"])


# =========================================================================== #
# v2.1 ADDITIONS — PARALLEL STRUCTURE
# =========================================================================== #
_AS_AS = [
    ("{N} finds it as rewarding to teach as ___", "to perform", ["performing", "a performance", "when she performs"]),
    ("The new bridge is as useful to cyclists as ___", "to drivers", ["driving", "the drivers' use", "for those who drive"]),
    ("Reading the letters was as moving as ___", "hearing them read aloud", ["to hear them read aloud", "the readings aloud", "when they were read aloud"]),
    ("The garden is as beautiful in October as ___", "in May", ["May", "it was in May's beauty", "during May's"]),
    ("Learning to row is as demanding as ___", "learning to swim", ["to learn to swim", "swimming lessons", "when one learns to swim"]),
    ("The ferry is as crowded on weekdays as ___", "on weekends", ["weekends", "it is crowded on weekends", "during the weekend's"]),
    ("Restoring a clock is as much about patience as ___", "about skill", ["skill", "being skillful", "having skill is"]),
    ("The choir sounds as rich in rehearsal as ___", "in performance", ["performing", "a performance", "when it performs"]),
]


@family(fill_in=True)
def par_as_as(rng, difficulty):
    """'as ... as' comparisons need matching forms on both sides."""
    frame, right, wrongs = rng.choice(_AS_AS)
    name = rng.choice(_NAMES)
    text = frame.format(N=name) + "."
    first_half = frame.split(" as ")[1] if " as " in frame else ""
    correct = (right, f"Correct. '{right}' mirrors the form of the first half of the comparison.")
    ds = [(wrongs[0], "This form does not match the phrase on the other side of 'as...as'."),
          (wrongs[1], "A different kind of phrase breaks the parallel comparison."),
          (wrongs[2], "A clause does not match the phrase on the other side of the comparison.")]
    if difficulty != "easy":
        text = rng.choice(["In the end, ", "As most people agree, ", "Surprisingly, "]) + soft_low(text)
    if difficulty == "hard":
        text = text + " " + rng.choice(["Few would argue otherwise.", "The comparison holds every year.",
                                        "The point is often overlooked."])
    return build(rng, fill(text, conv_stem(rng)), correct, ds, subskill="parallel_structure",
                 explanation="The two halves of an 'as ... as' comparison must take the same grammatical form.",
                 tags=["conventions", "parallelism", "as-as"], est=50)


_INF_GER = [
    ("The program teaches participants", ["to budget", "to cook", "to negotiate", "to plan meals"],
     ["budgeting", "cooking", "negotiating", "planning meals"]),
    ("Volunteers are expected", ["to arrive early", "to sign in", "to stay until closing", "to wear a badge"],
     ["arriving early", "signing in", "staying until closing", "wearing a badge"]),
    ("The residents enjoy", ["hiking", "fishing", "kayaking", "birdwatching"],
     ["to hike", "to fish", "to kayak", "to birdwatch"]),
    ("Her hobbies include", ["carving", "sketching", "baking", "gardening"],
     ["to carve", "to sketch", "to bake", "to garden"]),
    ("The guide reminded us", ["to carry water", "to watch the tide", "to stay on the path", "to respect the nests"],
     ["carrying water", "watching the tide", "staying on the path", "respecting the nests"]),
    ("The job mostly involves", ["answering calls", "filing reports", "greeting visitors", "updating the schedule"],
     ["to answer calls", "to file reports", "to greet visitors", "to update the schedule"]),
]


@family(fill_in=True)
def par_infinitive_gerund(rng, difficulty):
    """Lists of infinitives vs. gerunds: match the form the lead verb takes."""
    lead, good, bad = rng.choice(_INF_GER)
    idx = rng.sample(range(4), 3)
    a, b, c = (good[i] for i in idx)
    c_bad = bad[idx[2]]
    form = "infinitive" if good[0].startswith("to ") else "gerund"
    correct = (c, f"Correct. The list uses {form}s, so the final item is a{'n' if form == 'infinitive' else ''} {form} too.")
    noun_c = c.replace("to ", "", 1) if form == "infinitive" else c
    ds = [(c_bad, f"This {'gerund' if form == 'infinitive' else 'infinitive'} breaks the series of {form}s."),
          (f"{noun_c.split()[0]}s {' '.join(noun_c.split()[1:])}".strip(), "A finite verb breaks the series."),
          (f"they {noun_c.split()[0]} {' '.join(noun_c.split()[1:])}".strip(), "A clause with its own subject breaks the series.")]
    if difficulty != "easy":
        ds[1] = (c.replace("to ", "and to ", 1) if form == "infinitive" else f"also {c}",
                 "An extra connector inside the last item breaks the pattern of the series.")
    text = f"{lead} {a}, {b}, and ___."
    if difficulty == "hard":
        text = text + " " + rng.choice(["The schedule rarely changes.", "Most people enjoy it.",
                                        "The list is posted by the door."])
    return build(rng, fill(text, conv_stem(rng)), correct, ds, subskill="parallel_structure",
                 explanation="All items in a series after a lead verb must share one form: all infinitives or all gerunds.",
                 tags=["conventions", "parallelism", "infinitive-gerund"], est=50)


_CORR_VERBS = [
    ("The committee will either approve the plan or ___", "reject it", ["rejecting it", "it will reject it", "to reject it"]),
    ("The storm not only flooded the road but also ___", "toppled the old oak", ["toppling the old oak", "the old oak toppled", "to topple the old oak"]),
    ("Visitors may neither touch the exhibits nor ___", "photograph them", ["photographing them", "they may photograph them", "to photograph them"]),
    ("{N} both repaired the engine and ___", "repainted the hull", ["repainting the hull", "the hull was repainted", "to repaint the hull"]),
    ("The new filter not only removes sediment but also ___", "improves the taste", ["improving the taste", "the taste improves", "to improve the taste"]),
    ("The guide would rather walk the ridge than ___", "drive the valley road", ["driving the valley road", "she would drive the valley road", "to drive the valley road"]),
    ("Each spring the farmers either plow the lower field or ___", "let it rest", ["letting it rest", "it is left to rest", "to let it rest"]),
    ("The library will not only extend its hours but also ___", "add a second reading room", ["adding a second reading room", "a second reading room will be added", "to add a second reading room"]),
    ("The ranger either closes the trail or ___", "posts a warning at the gate", ["posting a warning at the gate", "a warning is posted at the gate", "to post a warning at the gate"]),
    ("{N} would rather repair the old canoe than ___", "buy a new one", ["buying a new one", "she would buy a new one", "to buy a new one"]),
    ("The drought not only withered the corn but also ___", "dried the creek", ["drying the creek", "the creek dried", "to dry the creek"]),
    ("The choir will both record an album and ___", "tour the coast", ["touring the coast", "a tour of the coast", "to tour the coast"]),
]


@family(fill_in=True, small_space=True)
def par_correlative_verbs(rng, difficulty):
    """Correlative pairs joining verb phrases."""
    frame, right, wrongs = rng.choice(_CORR_VERBS)
    name = rng.choice(_NAMES)
    text = frame.format(N=name) + "."
    correct = (right, f"Correct. '{right}' matches the verb phrase after the first half of the pair.")
    ds = [(wrongs[0], "An -ing phrase does not match the verb phrase in the first half."),
          (wrongs[1], "A full clause does not match the verb phrase in the first half."),
          (wrongs[2], "An infinitive does not match the finite verb phrase in the first half.")]
    if difficulty != "easy":
        text = rng.choice(["As expected, ", "According to the minutes, ", "In the end, "]) + soft_low(text)
    if difficulty == "hard":
        text = text + " " + rng.choice(["The vote was unanimous.", "Nobody was surprised.", "The work took all summer."])
    return build(rng, fill(text, conv_stem(rng)), correct, ds, subskill="parallel_structure",
                 explanation=("With correlative pairs (either/or, not only/but also, neither/nor), the words "
                              "after each half must have the same form."),
                 tags=["conventions", "parallelism", "correlative-verbs"], est=50)


# =========================================================================== #
# v2.1 ADDITIONS — PRONOUN-ANTECEDENT
# =========================================================================== #
_PA_COLL = [("The jury", "verdict"), ("The committee", "recommendation"), ("The orchestra", "program"),
            ("The team", "lineup"), ("The council", "budget"), ("The faculty", "schedule"),
            ("The crew", "route"), ("The board", "decision"), ("The choir", "repertoire"), ("The cast", "bows")]


@family(fill_in=True)
def pa_collective(rng, difficulty):
    """A collective noun acting as a unit takes 'it'/'its', even with 'members' nearby."""
    ante, thing = rng.choice(_PA_COLL)
    noun = ante.split()[1]
    kind = rng.choice(["poss", "subj"])
    members = rng.choice(["whose members rarely agree", "made up of twelve members",
                          "which includes several newcomers", "despite its many members"])
    if kind == "poss":
        right, wrong = "its", "their"
        pred = rng.choice([f"announced ___ {thing} at noon", f"revised ___ {thing} twice", f"defended ___ {thing}"])
        ds = [(wrong, f"'{noun}' acts as a single unit here, so the possessive is 'its', not 'their'."),
              ("it's", "'it's' means 'it is' and is not possessive."),
              ("there", "'there' is not a possessive pronoun.")]
    else:
        right, wrong = "it", "they"
        pred = rng.choice([f"when ___ announced the {thing}", f"before ___ revised the {thing}",
                           f"after ___ approved the {thing}"])
        ds = [(wrong, f"'{noun}' acts as one unit, so the subject pronoun is 'it'."),
              ("them", "'them' is objective and cannot be the subject."),
              ("one", "'one' does not refer back to the collective noun.")]
    correct = (right, f"Correct. '{ante}' is a collective noun acting as one unit, so '{right}' agrees with it.")
    if kind == "poss":
        text = f"{ante} {pred}." if difficulty == "easy" else f"{ante}, {members}, {pred}."
    else:
        text = f"The reporters waited outside {pred.replace('___', '___')}" if False else \
            f"The hall fell silent {pred}." if difficulty == "easy" else f"The hall, packed with reporters, fell silent {pred}."
        text = text.replace("silent when", "silent when").replace(f"silent after", "silent after")
        if difficulty != "easy":
            text = text.replace(f"{ante}", f"{ante}, {members},") if ante in text else text
        text = text.replace("___ announced", f"___ announced").replace("the hall", "the hall")
        # make the antecedent explicit
        text = f"{ante} met for nine hours. " + text if difficulty != "hard" else \
            f"{ante}, {members}, met for nine hours. " + text
    if difficulty == "hard" and kind == "poss":
        text = text + " " + rng.choice(["The announcement surprised no one.", "Reporters had waited all day."])
    return build(rng, fill(text, conv_stem(rng)), correct, ds, subskill="pronoun_antecedent",
                 explanation=(f"A collective noun such as '{noun}' names one group acting together; "
                              "the pronoun that refers to it is singular."),
                 tags=["conventions", "pronoun-antecedent", "collective"])


_PA_INDEF = [("Neither of the companies", "released ___ annual report"), ("Each of the branches", "updated ___ hours"),
             ("One of the ferries", "changed ___ schedule"), ("Either of the proposals", "could win on ___ merits"),
             ("Every one of the clinics", "posted ___ address at the gate"), ("Neither of the bridges", "has had ___ deck replaced"),
             ("Each of the orchards", "sells ___ harvest at the market"), ("One of the museums", "reopened ___ east wing"),
             ("Neither of the choirs", "has chosen ___ program"), ("Each of the ferries", "carries ___ own mechanic"),
             ("One of the bakeries", "doubled ___ staff"), ("Every one of the lighthouses", "still has ___ original lens")]


@family(fill_in=True)
def pa_indefinite(rng, difficulty):
    """Indefinite pronouns (each, neither, one of) are singular antecedents."""
    ante, pred = rng.choice(_PA_INDEF)
    head = ante.split()[0]
    plural_noun = ante.split()[-1]
    pred = pred + rng.choice(["", ", as the newsletter reports", ", to nobody's surprise"])
    correct = ("its", f"Correct. '{head}' is singular, so the pronoun is 'its'; the plural '{plural_noun}' "
                      "is the object of 'of', not the antecedent.")
    ds = [("their", f"'their' agrees with '{plural_noun}', but the antecedent is the singular '{head}'."),
          ("its'", "'its'' is not a word."),
          ("it's", "'it's' means 'it is' and cannot show possession.")]
    text = f"{ante} {pred}."
    if difficulty == "medium":
        text = rng.choice(["According to the newsletter, ", "As of this month, ", "To the surprise of many, "]) + low(text)
    elif difficulty == "hard":
        text = f"{ante}, {rng.choice(['after months of debate', 'along with its partners', 'despite the cost'])}, {pred}. " + \
            rng.choice(["The decision drew little notice.", "Nobody noticed at first.", "The change was overdue."])
    return build(rng, fill(text, conv_stem(rng)), correct, ds, subskill="pronoun_antecedent",
                 explanation=f"Indefinite pronouns such as '{head.lower()}' are singular, whatever plural noun follows 'of'.",
                 tags=["conventions", "pronoun-antecedent", "indefinite"])


_PA_DISTANT = [
    ("The lighthouse was built in 1874.", "For a century a keeper lived in the cottage beside it, trimming the wick each night.",
     "Today ___ lamp switches on by itself at dusk", "its", "lighthouse"),
    ("The three founders still meet every Friday.", "The company they started has grown to four hundred employees.",
     "Even so, ___ keep the same corner table at the diner", "they", "founders"),
    ("The orchestra toured six cities last spring.", "Critics in every city praised the young soloist.",
     "By the final concert ___ members were exhausted but elated", "its", "orchestra"),
    ("The divers mapped the sunken ferry over two summers.", "The wreck lies in forty feet of murky water.",
     "By the second August ___ had photographed every deck", "they", "divers"),
    ("The weather station has operated since 1952.", "Farmers in the valley check the readings before planting.",
     "Every morning ___ instruments are inspected at six", "its", "station"),
    ("The twin lighthouses guard the northern channel.", "Ships bound for the harbor pass between them.",
     "On foggy nights ___ horns sound every thirty seconds", "their", "lighthouses"),
    ("The bakery's starter is more than forty years old.", "Customers line up before the doors open.",
     "The owners feed ___ every morning before dawn", "it", "starter"),
    ("The volunteers arrived before sunrise.", "The beach was littered with debris from the storm.",
     "Within an hour ___ had cleared the entire shoreline", "they", "volunteers"),
]


@family(fill_in=True, small_space=True)
def pa_distant(rng, difficulty):
    """The antecedent is two sentences back, with a closer noun of the other number as bait."""
    s1, s2, s3, right, ante = rng.choice(_PA_DISTANT)
    plural = right in ("their", "they")
    num = "plural" if plural else "singular"
    if right in ("its", "their"):
        wrong = "their" if right == "its" else "its"
        ds = [(wrong, f"'{wrong}' agrees with a nearer noun, but the pronoun refers to '{ante}', which is {num}."),
              ("it's" if not plural else "they're", "A contraction cannot show possession."),
              ("there", "'there' is not a possessive pronoun.")]
    elif right in ("it", "they"):
        wrong = "they" if right == "it" else "it"
        ds = [(wrong, f"'{wrong}' matches a nearer noun, but the antecedent '{ante}' is {num}."),
              ("them" if plural else "its", "This form cannot be the subject of the clause."),
              ("one", "'one' does not refer back to the antecedent.")]
    correct = (right, f"Correct. The pronoun refers to '{ante}' in the first sentence, which is {num}.")
    text = f"{s1} {s2} {s3}." if difficulty != "easy" else f"{s1} {s3}."
    if difficulty == "hard":
        text = text + " " + rng.choice(["Visitors rarely notice.", "The routine never varies.", "Few people know this."])
    return build(rng, fill(text, conv_stem(rng)), correct, ds, subskill="pronoun_antecedent",
                 explanation=("Trace the pronoun back to the noun it really stands for, even when another "
                              "noun sits closer to it."),
                 tags=["conventions", "pronoun-antecedent", "distant"], est=55)


# =========================================================================== #
# v2.1 ADDITIONS — QUANTITATIVE EVIDENCE
# =========================================================================== #
@family(fill_in=False)
def qe_percent_change(rng, difficulty):
    """Percent change computed from two table values."""
    label, plural, cats, measure, unit = rng.choice(_QE_CATS)
    k = {"easy": 3, "medium": 4, "hard": 5}[difficulty]
    names = rng.sample(cats, k)
    y1, y2 = 2018 + rng.randint(0, 2), 2022 + rng.randint(0, 2)
    rows = []
    for nm in names:
        v1 = rng.choice([20, 25, 40, 50, 60, 80])
        pct = rng.choice([10, 20, 25, 50]) if difficulty != "hard" else rng.choice([10, 15, 20, 25, 30, 50])
        v2 = v1 + v1 * pct // 100
        if v1 * pct % 100:
            v2 = v1 + round(v1 * pct / 100)
        rows.append([nm, v1, v2])
    i = rng.randrange(k)
    nm, v1, v2 = rows[i]
    pct = round((v2 - v1) / v1 * 100)
    diff = v2 - v1
    claim = f"A journalist writes that {nm} showed the kind of growth in {measure} the region hoped for."
    tmpl = rng.choice([
        lambda v: f"{nm} rose from {v1} to {v2} {unit}, an increase of about {v} percent.",
        lambda v: f"From {y1} to {y2}, {nm} climbed from {v1} to {v2} {unit}, up roughly {v} percent.",
        lambda v: f"{_poss(nm)} figure grew by about {v} percent, from {v1} to {v2} {unit}.",
    ])
    correct = (tmpl(pct), f"Correct. ({v2} − {v1}) ÷ {v1} = {pct}% growth.")
    cands = [(diff, f"{diff} is the change in {unit}, not a percent; the percent change is {pct}%."),
             (round(diff / v2 * 100), "This divides by the later value instead of the starting value."),
             (pct * 2, f"The percent change is {pct}%, not double that."),
             (pct + 10, f"The percent change is {pct}%; this figure is simply too high."),
             (max(pct - 5, 1), f"The percent change is {pct}%; this figure is too low.")]
    ds, seen = [], {pct}
    for val, why in cands:
        if val in seen:
            continue
        seen.add(val)
        ds.append((tmpl(val), why))
        if len(ds) == 3:
            break
    prompt = (f"{claim}\n\n" + rng.choice(["Which choice most accurately uses data from the table to support the statement?",
                                           "Which statement about the table's data is accurate?"]))
    return _qe_mc(rng, prompt, correct, ds,
                  _qe_table(f"{cap(measure)} ({unit})", [label, str(y1), str(y2)], rows),
                  "Percent change = (new − old) ÷ old × 100; compute it from the table's starting value.")


@family(fill_in=False)
def qe_contradict_year(rng, difficulty):
    """Which year's data contradicts a 'rose every year' claim?"""
    metric, place, unit, verb = rng.choice(_QE_TOPICS)
    rising = verb in ("rose", "increased", "grew", "climbed")
    n = {"easy": 4, "medium": 5, "hard": 6}[difficulty]
    y0 = 2016 + rng.randint(0, 3)
    years = [y0 + i for i in range(n)]
    start = rng.randint(40, 120) if unit != "percent" else rng.randint(10, 35)
    steps = [rng.choice([4, 6, 8, 10]) if unit != "percent" else rng.choice([2, 3, 4, 5]) for _ in range(n - 1)]
    vals = [start]
    for st in steps:
        vals.append(vals[-1] + st)
    if not rising:
        vals = vals[::-1]
    dip = rng.randrange(1, n)  # index of the year that reverses
    rev = rng.choice([2, 3, 5])
    vals[dip] = vals[dip - 1] - rev if rising else vals[dip - 1] + rev
    # restore monotone after the dip relative to the dip value
    for j in range(dip + 1, n):
        vals[j] = max(vals[j], vals[j - 1] + 2) if rising else min(vals[j], vals[j - 1] - 2)
    rows = [[y, v] for y, v in zip(years, vals)]
    dir_word = "rose" if rising else "fell"
    opp = "fell" if rising else "rose"
    claim = f"A report claims that {metric.lower()} in {place} {dir_word} every single year from {years[0]} to {years[-1]}."
    correct_text = rng.choice([
        f"In {years[dip]} the value {opp} to {vals[dip]} {unit} from {vals[dip - 1]} {unit} the year before.",
        f"The figure for {years[dip]} ({vals[dip]} {unit}) is {'lower' if rising else 'higher'} than the figure for {years[dip - 1]} ({vals[dip - 1]} {unit}).",
    ])
    correct = (correct_text, f"Correct. {years[dip]} breaks the pattern: the value {opp} that year.")
    others = [i for i in range(1, n) if i != dip]
    o1 = others[0]
    o2 = others[-1]
    ds = [(f"In {years[o1]} the value {dir_word} to {vals[o1]} {unit} from {vals[o1 - 1]} {unit}.",
           "This year follows the claimed pattern, so it does not contradict the report."),
          (f"The figure for {years[o2]} ({vals[o2]} {unit}) is {'higher' if rising else 'lower'} than the figure for {years[o2 - 1]} ({vals[o2 - 1]} {unit}).",
           "This year follows the claimed pattern."),
          (f"Over the whole period the value {dir_word} from {vals[0]} to {vals[-1]} {unit}.",
           "The overall change is consistent with the claim; only a single year's reversal contradicts 'every year'.")]
    prompt = (f"{claim}\n\n" + rng.choice(["Which choice uses data from the table to identify the year that contradicts the report?",
                                           "Which finding from the table most directly contradicts the claim?"]))
    return _qe_mc(rng, prompt, correct, ds,
                  _qe_table(f"{metric} in {place} ({unit})", ["Year", metric], rows),
                  "A claim about 'every year' is refuted by any single year that moves the other way.")


@family(fill_in=False)
def qe_two_groups(rng, difficulty):
    """Two groups measured in two years; compare their changes."""
    label, plural, cats, measure, unit = rng.choice(_QE_CATS)
    a, b = rng.sample(cats, 2)
    y1, y2 = 2017 + rng.randint(0, 2), 2022 + rng.randint(0, 2)
    a1 = rng.randint(20, 50)
    b1 = rng.randint(20, 50)
    da = rng.choice([4, 6, 8, 10, 12])
    db = rng.choice([1, 2, 3, -2, -4])
    while abs(db) == da:
        db = rng.choice([1, 2, 3, -2, -4])
    a2, b2 = a1 + da, b1 + db
    rows = [[str(y1), a1, b1], [str(y2), a2, b2]]
    claim = f"A researcher argues that {a} improved far more than {b} in {measure} between {y1} and {y2}."
    b_dir = "rose" if db > 0 else "fell"
    correct_text = rng.choice([
        f"{a} rose by {da} {unit} while {b} {b_dir} by {abs(db)} {unit}.",
        f"{_poss(a)} figure climbed {da} {unit}; {_poss(b)} {b_dir} {abs(db)} {unit}.",
        f"From {y1} to {y2}, {a} gained {da} {unit} and {b} {b_dir} {abs(db)} {unit}.",
    ])
    correct = (correct_text, "Correct. The changes are read directly from the two rows for each group.")
    ds = [(f"{b} rose by {da} {unit} while {a} {b_dir} by {abs(db)} {unit}.", "This swaps the two groups."),
          (f"{a} and {b} both rose by about {da} {unit}.", f"{b} changed by {db:+} {unit}, not {da}."),
          (f"In {y2}, {a} recorded {a2} {unit} and {b} recorded {b2} {unit}, so {b} improved more.",
           f"The {y2} values alone do not show change; {a} gained {da} and {b} {b_dir} by {abs(db)}.")]
    if difficulty == "hard":
        ds[1] = (f"{a} rose by {da} {unit} while {b} {b_dir} by {abs(db) + 3} {unit}.",
                 f"{b} changed by {abs(db)} {unit}, not {abs(db) + 3}.")
    prompt = f"{claim}\n\n{rng.choice(_QE_STEMS)}"
    return _qe_mc(rng, prompt, correct, ds,
                  _qe_table(f"{cap(measure)} ({unit})", ["Year", a, b], rows),
                  "Compute each group's change from its own two values before comparing the two groups.")


# =========================================================================== #
# FAMILY TABLE + LEGACY DISPATCHERS
# =========================================================================== #
FAMILIES = {
    "verb_tense": {
        "easy": [vt_time_cue, vt_irregular, vt_present_perfect, vt_passage, vt_sequence,
                 vt_conditional, vt_future_perfect, vt_reported],
        "medium": [vt_time_cue, vt_sequence, vt_irregular, vt_present_perfect, vt_passage, vt_clause_options,
                   vt_conditional, vt_future_perfect, vt_reported],
        "hard": [vt_time_cue, vt_sequence, vt_irregular, vt_present_perfect, vt_passage, vt_clause_options,
                 vt_conditional, vt_future_perfect, vt_reported],
    },
    "parallel_structure": {
        "easy": [par_series, par_verb_series, par_correlative, par_whole_sentence, par_passage,
                 par_infinitive_gerund, par_correlative_verbs],
        "medium": [par_series, par_correlative, par_comparison, par_verb_series, par_passage, par_whole_sentence,
                   par_as_as, par_infinitive_gerund, par_correlative_verbs],
        "hard": [par_series, par_correlative, par_comparison, par_verb_series, par_passage, par_whole_sentence,
                 par_as_as, par_infinitive_gerund, par_correlative_verbs],
    },
    "pronoun_antecedent": {
        "easy": [pa_possessive, pa_subject, pa_passage, pa_ambiguous, pa_whole_sentence,
                 pa_collective, pa_indefinite, pa_distant],
        "medium": [pa_possessive, pa_subject, pa_ambiguous, pa_passage, pa_whole_sentence,
                   pa_collective, pa_indefinite, pa_distant],
        "hard": [pa_possessive, pa_subject, pa_ambiguous, pa_passage, pa_whole_sentence,
                 pa_collective, pa_indefinite, pa_distant],
    },
    "quantitative_evidence": {
        "easy": [qe_trend, qe_category_max, qe_compare_two, qe_support_point, qe_undermine,
                 qe_percent_change, qe_contradict_year, qe_two_groups],
        "medium": [qe_trend, qe_category_max, qe_compare_two, qe_undermine, qe_support_point,
                   qe_percent_change, qe_contradict_year, qe_two_groups],
        "hard": [qe_trend, qe_category_max, qe_compare_two, qe_undermine, qe_support_point,
                 qe_percent_change, qe_contradict_year, qe_two_groups],
    },
}


def gen_verb_tense(rng: random.Random, difficulty: str = "medium"):
    return dispatch(FAMILIES["verb_tense"], rng, difficulty)


def gen_parallelism(rng: random.Random, difficulty: str = "medium"):
    return dispatch(FAMILIES["parallel_structure"], rng, difficulty)


def gen_pronoun_antecedent(rng: random.Random, difficulty: str = "medium"):
    return dispatch(FAMILIES["pronoun_antecedent"], rng, difficulty)


def gen_quantitative_evidence(rng: random.Random, difficulty: str = "medium"):
    return dispatch(FAMILIES["quantitative_evidence"], rng, difficulty)
