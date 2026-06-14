"""Original SAT-style Reading & Writing question generators.

Two families:
  * Combinatorial conventions (boundaries, subject-verb agreement, punctuation,
    pronouns, modifiers) — built from clause/noun pools so each item is unique and
    has exactly one defensible correct answer.
  * Authored pools (transitions, concision, rhetorical synthesis) — curated lists.

Reading-comprehension items (main idea, inference, evidence, structure,
words-in-context, cross-text) live in passages.py because they need original prose.
"""
from __future__ import annotations

import random

from .util import mc, shuffle_with_correct

NAMES = ["Maya", "Liam", "Aria", "Noah", "Priya", "Diego", "Ivy", "Omar",
         "Lena", "Theo", "Zoe", "Caleb", "Nina", "Ravi", "Sora", "Jonas",
         "Elena", "Marcus", "Yuki", "Tariq"]


# --------------------------------------------------------------------------- #
# Combinatorial: sentence boundaries (joining two independent clauses)
# --------------------------------------------------------------------------- #
_IND_A = [
    "The museum extended its hours for the festival",
    "Coral reefs support a quarter of all marine species",
    "The new bridge cut the commute in half",
    "Volunteers planted three hundred saplings along the river",
    "The orchestra rehearsed the symphony for weeks",
    "Solar panels now cover the school's roof",
    "The bakery sells out of sourdough by noon",
    "Migrating cranes stop at the wetland each autumn",
    "The committee approved the revised budget",
    "Heavy rain delayed the construction schedule",
    "The library digitized its oldest manuscripts",
    "A small startup designed the award-winning app",
    "The athletes trained at high altitude for months",
    "The documentary premiered to a packed theater",
    "Engineers tested the rover in the desert",
]
_IND_B = [
    "attendance doubled within a week",
    "their loss would ripple through the food web",
    "local businesses reported a surge in customers",
    "the banks are already more stable",
    "the premiere drew a standing ovation",
    "the building's energy bills dropped sharply",
    "regular customers arrive early to be sure",
    "birdwatchers gather to count them",
    "the new plan takes effect next month",
    "the crew worked double shifts to catch up",
    "researchers can now study them remotely",
    "investors took notice almost immediately",
    "their endurance improved dramatically",
    "critics praised its honest storytelling",
    "every system performed flawlessly",
]


def gen_boundaries(rng: random.Random):
    a = rng.choice(_IND_A)
    b = rng.choice(_IND_B)
    b_cap = b[0].upper() + b[1:]
    correct = (f"{a}. {b_cap}", "Correct. Two independent clauses can stand as two "
               "separate sentences joined by a period.")
    distractors = [
        (f"{a}, {b}", "Comma splice: a comma alone cannot join two independent clauses."),
        (f"{a} {b}", "Run-on (fused sentence): the two clauses need punctuation between them."),
        (f"{a}; and {b}", "A semicolon should not be paired with a coordinating conjunction like 'and'."),
    ]
    options, ci, rats = shuffle_with_correct(rng, correct, distractors)
    prompt = ("Which choice most effectively joins the two ideas while following "
              "the conventions of standard English?")
    return mc(prompt, options, ci, rats, subskill="clause_joining",
              qtype="grammar_editing",
              explanation=("Each clause is independent (it could stand alone), so they "
                           "must be separated by a period or semicolon — not a comma "
                           "(splice) or nothing (run-on)."),
              tags=["conventions", "boundaries"], est=45)


# --------------------------------------------------------------------------- #
# Combinatorial: subject-verb agreement
# --------------------------------------------------------------------------- #
# (subject phrase, is_plural). Intervening phrases are built to bait the wrong number.
_SUBJECTS = [
    ("The collection of rare coins", False),
    ("Each of the new employees", False),
    ("The list of approved vendors", False),
    ("Neither of the proposals", False),
    ("The box of old photographs", False),
    ("Every student in the advanced classes", False),
    ("The team of researchers", False),
    ("One of the museum's exhibits", False),
    ("The set of instructions", False),
    ("A bouquet of fresh flowers", False),
    ("The students in the orchestra", True),
    ("Several of the volunteers", True),
    ("The results of the experiment", True),
    ("Both of the candidates", True),
    ("The shelves near the entrance", True),
    ("Many of the old buildings", True),
]
# verb families: (singular, plural, -ing, infinitive), with a present-tense tail.
_VERBS = [
    ("requires", "require", "requiring", "to require", "careful attention"),
    ("includes", "include", "including", "to include", "a detailed summary"),
    ("appears", "appear", "appearing", "to appear", "in the final report"),
    ("remains", "remain", "remaining", "to remain", "unchanged each year"),
    ("reflects", "reflect", "reflecting", "to reflect", "the team's effort"),
    ("supports", "support", "supporting", "to support", "the main conclusion"),
    ("arrives", "arrive", "arriving", "to arrive", "before the deadline"),
    ("contains", "contain", "containing", "to contain", "useful information"),
]


def gen_sva(rng: random.Random):
    subj, plural = rng.choice(_SUBJECTS)
    sing, plur, ing, inf, tail = rng.choice(_VERBS)
    correct_word = plur if plural else sing
    wrong_word = sing if plural else plur
    correct = (correct_word, f"Correct. The subject '{subj}' is "
               f"{'plural' if plural else 'singular'}, so the verb must be "
               f"'{correct_word}'.")
    distractors = [
        (wrong_word, f"Agreement error: this verb is "
         f"{'singular' if plural else 'plural'}, but the subject is "
         f"{'plural' if plural else 'singular'}. Ignore the words between the subject and verb."),
        (ing, "An -ing form alone cannot serve as the main verb of the sentence."),
        (inf, "An infinitive cannot serve as the main verb here."),
    ]
    options, ci, rats = shuffle_with_correct(rng, correct, distractors)
    prompt = (f"{subj} ___ {tail}.\n\n"
              "Which choice completes the sentence so that it conforms to the "
              "conventions of standard English?")
    return mc(prompt, options, ci, rats, subskill="subject_verb_agreement",
              qtype="grammar_editing",
              explanation=(f"Strip away the modifying phrase and the core subject is "
                           f"{'plural' if plural else 'singular'}, which takes "
                           f"'{correct_word}'."),
              tags=["conventions", "agreement"], est=45)


# --------------------------------------------------------------------------- #
# Combinatorial: punctuation (possessives + nonrestrictive commas)
# --------------------------------------------------------------------------- #
_SING_NOUNS = [
    ("scientist", "scientist's"), ("city", "city's"), ("author", "author's"),
    ("company", "company's"), ("teacher", "teacher's"), ("river", "river's"),
    ("artist", "artist's"), ("dog", "dog's"), ("school", "school's"),
    ("engineer", "engineer's"),
]
_PLUR_NOUNS = [
    ("students", "students'"), ("workers", "workers'"), ("birds", "birds'"),
    ("teachers", "teachers'"), ("players", "players'"), ("residents", "residents'"),
    ("artists", "artists'"), ("companies", "companies'"),
]
_POSS_TAILS = [
    "discovery surprised everyone",
    "schedule changed at the last minute",
    "design won several awards",
    "reputation grew steadily",
    "results were published online",
    "performance impressed the judges",
]


def gen_punctuation(rng: random.Random):
    use_plural = rng.random() < 0.5
    if use_plural:
        base, possessive = rng.choice(_PLUR_NOUNS)
        plain = base
        wrong_apos = base[:-1] + "'s" if not base.endswith("s") else base + "'s"
    else:
        base, possessive = rng.choice(_SING_NOUNS)
        plain = base
        wrong_apos = base + "s'"
    tail = rng.choice(_POSS_TAILS)
    correct = (possessive, "Correct. A possessive noun needs an apostrophe placed "
               "correctly for its number.")
    distractors = [
        (plain, "This is the plain (non-possessive) form, but possession is required here."),
        (wrong_apos, "The apostrophe is misplaced for this noun's number."),
        (base + ("s" if not base.endswith("s") else "es"),
         "Adding a plain -s shows a plural, not possession."),
    ]
    # ensure unique option texts
    seen = {possessive}
    cleaned = []
    for t, r in distractors:
        if t in seen:
            continue
        seen.add(t)
        cleaned.append((t, r))
    while len(cleaned) < 3:
        cand = base + "'" + ("s" if rng.random() < .5 else "")
        if cand in seen:
            cand = base + "es"
        if cand in seen:
            break
        seen.add(cand)
        cleaned.append((cand, "This punctuation does not correctly show possession."))
    options, ci, rats = shuffle_with_correct(rng, correct, cleaned[:3])
    prompt = (f"The {plain} ___ {tail}.\n\n"
              "Which choice correctly shows that the noun possesses what follows?")
    return mc(prompt, options, ci, rats, subskill="punctuation",
              qtype="grammar_editing",
              explanation=("Possession is marked with an apostrophe: add 's to a "
                           "singular noun and just an apostrophe after a plural noun "
                           "already ending in -s."),
              tags=["conventions", "punctuation", "possessive"], est=45)


# --------------------------------------------------------------------------- #
# Combinatorial: pronouns (case)
# --------------------------------------------------------------------------- #
def gen_pronouns(rng: random.Random):
    kind = rng.choice(["object_compound", "subject_compound", "who_whom"])
    if kind == "object_compound":
        n = rng.choice(NAMES)
        verb = rng.choice(["thanked", "invited", "called", "emailed", "joined"])
        correct = ("me", "Correct. As the object of the verb, the pronoun takes the "
                   "objective case 'me'.")
        distractors = [
            ("I", "'I' is subjective case; an object requires 'me'."),
            ("myself", "A reflexive pronoun needs a matching subject earlier in the clause."),
            ("mine", "'mine' is possessive and cannot be the object of the verb."),
        ]
        prompt = (f"The coach {verb} {n} and ___ after the match.\n\n"
                  "Which choice conforms to the conventions of standard English?")
        sub = "pronouns"
    elif kind == "subject_compound":
        n = rng.choice(NAMES)
        verb = rng.choice(["finished", "won", "presented", "organized", "led"])
        correct = ("I", "Correct. As part of the subject, the pronoun takes the "
                   "subjective case 'I'.")
        distractors = [
            ("me", "'me' is objective case; a subject requires 'I'."),
            ("myself", "A reflexive pronoun cannot serve as the subject."),
            ("my", "'my' is possessive and cannot be the subject.")]
        prompt = (f"{n} and ___ {verb} the project ahead of schedule.\n\n"
                  "Which choice conforms to the conventions of standard English?")
        sub = "pronouns"
    else:
        thing = rng.choice(["the scientist", "the author", "the candidate",
                            "the musician", "the engineer"])
        correct = ("who", "Correct. The pronoun is the subject of the verb that "
                   "follows, so 'who' is required.")
        distractors = [
            ("whom", "'whom' is for objects; here the pronoun is the subject of the verb."),
            ("which", "'which' refers to things, not people."),
            ("whose", "'whose' is possessive and does not fit as the subject here.")]
        prompt = (f"The award went to {thing} ___ designed the experiment.\n\n"
                  "Which choice conforms to the conventions of standard English?")
        sub = "pronouns"
    options, ci, rats = shuffle_with_correct(rng, correct, distractors)
    return mc(prompt, options, ci, rats, subskill=sub, qtype="grammar_editing",
              explanation=("Choose pronoun case by the pronoun's job: subjective for "
                           "subjects (I, who), objective for objects (me, whom)."),
              tags=["conventions", "pronouns"], est=45)


# --------------------------------------------------------------------------- #
# Combinatorial: modifiers (dangling/misplaced)
# --------------------------------------------------------------------------- #
_MODIFIERS = [
    ("Walking through the old town,", "the travelers", "the cobblestones",
     "the photographs", "the afternoon"),
    ("Built more than a century ago,", "the bridge", "the engineers",
     "the traffic", "the city"),
    ("Having studied all night,", "Maya", "the exam", "the results", "the room"),
    ("Painted a bright shade of blue,", "the house", "the painter",
     "the neighbors", "the weather"),
    ("After finishing the marathon,", "the runner", "the medal",
     "the crowd", "the route"),
    ("Hidden beneath layers of dust,", "the manuscript", "the librarian",
     "the shelves", "the search"),
    ("Excited about the discovery,", "the scientists", "the data",
     "the equipment", "the announcement"),
    ("Carefully wrapped in paper,", "the gift", "the child",
     "the table", "the party"),
    ("Running low on fuel,", "the pilot", "the runway", "the storm", "the cargo"),
    ("Translated into a dozen languages,", "the novel", "the author",
     "the readers", "the prize"),
    ("Worried about the deadline,", "the editor", "the article",
     "the printer", "the office"),
    ("Frozen solid overnight,", "the lake", "the skaters", "the town", "the morning"),
    ("Trained for years in the studio,", "the dancer", "the routine",
     "the audience", "the stage"),
    ("Buried in the garden for centuries,", "the coins", "the gardener",
     "the museum", "the discovery"),
    ("Eager to begin,", "the students", "the lesson", "the bell", "the classroom"),
    ("Damaged by the flood,", "the records", "the clerk", "the basement", "the city"),
]
_MOD_PRED = {
    "Walking through the old town,": "admired the architecture",
    "Built more than a century ago,": "still carries thousands of cars each day",
    "Having studied all night,": "felt ready for the exam",
    "Painted a bright shade of blue,": "stood out on the quiet street",
    "After finishing the marathon,": "could barely stand",
    "Hidden beneath layers of dust,": "had gone unread for decades",
    "Excited about the discovery,": "published their findings at once",
    "Carefully wrapped in paper,": "sat waiting on the table",
    "Running low on fuel,": "decided to land early",
    "Translated into a dozen languages,": "reached readers worldwide",
    "Worried about the deadline,": "worked late into the night",
    "Frozen solid overnight,": "was safe to walk across",
    "Trained for years in the studio,": "moved with effortless grace",
    "Buried in the garden for centuries,": "gleamed when finally unearthed",
    "Eager to begin,": "raced into the room",
    "Damaged by the flood,": "had to be carefully restored",
}


def gen_modifiers(rng: random.Random):
    mod, right, w1, w2, w3 = rng.choice(_MODIFIERS)
    pred = _MOD_PRED[mod]
    correct = (f"{mod} {right} {pred}.",
               f"Correct. The modifier '{mod[:-1]}' logically describes "
               f"'{right}', which directly follows it.")
    distractors = [
        (f"{mod} {w1} {pred}.",
         f"Misplaced/dangling modifier: '{mod[:-1]}' cannot logically describe '{w1}'."),
        (f"{mod} {w2} {pred}.",
         f"The opening phrase does not sensibly modify '{w2}'."),
        (f"{mod} {w3} {pred}.",
         f"The opening phrase does not sensibly modify '{w3}'."),
    ]
    options, ci, rats = shuffle_with_correct(rng, correct, distractors)
    prompt = ("Which choice completes the sentence so that the introductory phrase "
              "modifies the correct noun?")
    return mc(prompt, options, ci, rats, subskill="modifiers", qtype="grammar_editing",
              explanation=("An introductory modifier must be immediately followed by "
                           "the noun it describes; otherwise it 'dangles.'"),
              tags=["conventions", "modifiers"], est=50)


# --------------------------------------------------------------------------- #
# Authored pool: transitions
# --------------------------------------------------------------------------- #
# Each entry: (sentence1, sentence2, needed_relation, correct_transition)
_TRANS_BANK = {
    "contrast": ["However", "Nevertheless", "By contrast", "On the other hand", "Still"],
    "cause": ["Therefore", "As a result", "Consequently", "Thus"],
    "addition": ["Moreover", "In addition", "Furthermore", "Additionally"],
    "example": ["For example", "For instance"],
    "sequence": ["Subsequently", "Later", "Afterward"],
    "emphasis": ["Indeed", "In fact"],
}
_TRANS_ITEMS = [
    ("The new policy promised faster service.", "wait times actually grew longer in the first month.", "contrast"),
    ("Sea otters eat large numbers of sea urchins.", "kelp forests thrive where otters are present.", "cause"),
    ("The author spent years researching the topic.", "she interviewed dozens of experts in the field.", "addition"),
    ("Some metals expand significantly when heated.", "bridges are built with expansion joints.", "cause"),
    ("Many songbirds navigate using the stars.", "some species also sense the Earth's magnetic field.", "addition"),
    ("The committee expected the plan to save money.", "costs rose in the first quarter.", "contrast"),
    ("The recipe calls for very ripe bananas.", "the loaf turns out dense and bland.", "cause"),
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
    ("The professor outlined the theory clearly.", "she illustrated it with a simple experiment.", "sequence"),
    ("The bridge was closed for repairs.", "commuters had to take a long detour.", "cause"),
    ("Many readers found the ending abrupt.", "the author defended it as intentional.", "contrast"),
    ("The city installed hundreds of new bike lanes.", "cycling rose by nearly forty percent.", "cause"),
    ("The data supported the first hypothesis.", "it cast doubt on the second.", "contrast"),
    ("The species looks fragile.", "it survives in some of the harshest deserts.", "contrast"),
    ("The factory switched to solar power.", "its emissions fell dramatically.", "cause"),
    ("The lecture covered the basics of the method.", "the lab session put it into practice.", "sequence"),
    ("The trail offers stunning views.", "it passes three historic landmarks.", "addition"),
    ("Critics praised the film's visuals.", "they found the plot thin.", "contrast"),
    ("The plant needs very little water.", "it can survive weeks of neglect.", "emphasis"),
    ("The report identified several risks.", "it proposed concrete solutions for each.", "addition"),
]


def pool_transitions(rng: random.Random):
    items = []
    rel_names = {"contrast": "a contrast", "cause": "a cause-and-effect relationship",
                 "addition": "an additional, similar idea", "example": "an example",
                 "sequence": "a sequence of events", "emphasis": "emphasis"}
    for s1, s2, rel in _TRANS_ITEMS:
        correct_word = rng.choice(_TRANS_BANK[rel])
        wrong_rels = [r for r in _TRANS_BANK if r != rel]
        rng.shuffle(wrong_rels)
        distractors = []
        for r in wrong_rels[:3]:
            distractors.append((rng.choice(_TRANS_BANK[r]),
                                f"This signals {rel_names[r]}, but the sentences require "
                                f"{rel_names[rel]}."))
        correct = (correct_word, f"Correct. The relationship is {rel_names[rel]}.")
        options, ci, rats = shuffle_with_correct(rng, correct, distractors)
        prompt = (f"{s1} ___, {s2}\n\nWhich transition best fits the relationship "
                  "between the two ideas?")
        items.append(mc(prompt, options, ci, rats, subskill="logical_transitions",
                        qtype="multiple_choice",
                        explanation=(f"The second sentence expresses {rel_names[rel]} "
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
]


def pool_concision(rng: random.Random):
    items = []
    for concise, *wordy in _CONCISION:
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
_SYNTHESIS = [
    ("a hummingbird study",
     ["Hummingbirds beat their wings up to 80 times per second.",
      "They have the fastest metabolism of any bird.",
      "A researcher recorded their heart rates in the wild."],
     "emphasize the birds' extreme physiology",
     "With wings beating up to 80 times per second and the fastest metabolism of any bird, hummingbirds push avian physiology to its limits.",
     ["A researcher recorded the heart rates of hummingbirds in the wild.",
      "Hummingbirds are birds that have a fast metabolism and beat their wings.",
      "The study of hummingbirds was conducted in the wild by a researcher."]),
    ("a coastal restoration project",
     ["The marsh lost 40% of its area since 1990.",
      "Volunteers replanted native grasses in 2023.",
      "Bird sightings rose the following spring."],
     "present the project's result",
     "After volunteers replanted native grasses, bird sightings in the marsh rose the following spring.",
     ["The marsh lost 40% of its area since 1990, a serious decline.",
      "Volunteers, who care about nature, replanted native grasses in 2023.",
      "The marsh is a place where native grasses can grow."]),
    ("a telescope upgrade",
     ["The old mirror was 2 meters wide.",
      "The new mirror is 4 meters wide.",
      "The upgrade doubled the telescope's resolution."],
     "highlight the improvement",
     "By replacing the 2-meter mirror with a 4-meter one, the upgrade doubled the telescope's resolution.",
     ["The telescope has a mirror that was upgraded to be wider than before.",
      "The old mirror was 2 meters wide, which is fairly small.",
      "Astronomers use telescopes to study distant objects in space."]),
    ("a community garden",
     ["The garden has 30 plots.",
      "Residents grow vegetables and herbs.",
      "Surplus produce is donated to a food bank."],
     "explain how the garden benefits others",
     "Beyond its 30 plots of vegetables and herbs, the garden donates surplus produce to a local food bank.",
     ["The garden has 30 plots where residents grow things.",
      "Residents grow vegetables and herbs in the community garden.",
      "A food bank is a place that receives donations of food."]),
    ("an ancient road discovery",
     ["Archaeologists found a stone road buried under a field.",
      "The road is about 2,000 years old.",
      "It connected two former market towns."],
     "introduce the discovery to readers",
     "Archaeologists have uncovered a 2,000-year-old stone road, buried beneath a field, that once linked two market towns.",
     ["The road is about 2,000 years old, which is very old indeed.",
      "It connected two former market towns to each other long ago.",
      "Archaeologists are scientists who study the human past."]),
    ("a recycling program",
     ["The town added curbside glass pickup.",
      "Glass recycling rose 60% in one year.",
      "Landfill waste dropped noticeably."],
     "emphasize the program's impact",
     "After the town added curbside glass pickup, glass recycling jumped 60% and landfill waste dropped noticeably.",
     ["The town added curbside glass pickup for residents to use.",
      "Glass recycling rose 60% in one year in the town.",
      "Recycling is the process of reusing materials."]),
    ("a language preservation effort",
     ["Only 200 fluent speakers of the language remain.",
      "A school began teaching it to children in 2020.",
      "Enrollment has grown each year since."],
     "convey both the threat and the response",
     "With only 200 fluent speakers left, a school began teaching the language to children in 2020, and enrollment has grown every year since.",
     ["A school began teaching the language to children in 2020.",
      "Only 200 fluent speakers of the language remain today.",
      "Languages are systems of communication used by people."]),
    ("a solar farm",
     ["The farm covers 50 acres.",
      "It powers about 9,000 homes.",
      "It replaced a closed coal plant."],
     "stress the shift from fossil fuels",
     "Built on the site of a closed coal plant, the 50-acre solar farm now powers about 9,000 homes.",
     ["The farm covers 50 acres of land in the area.",
      "It powers about 9,000 homes in the region.",
      "Solar farms generate electricity from sunlight."]),
    ("a bicycle-sharing launch",
     ["The city placed 500 bikes at 60 stations.",
      "Riders took 12,000 trips in the first week.",
      "Most trips replaced short car rides."],
     "show that the program changed how people travel",
     "In its first week, the 500-bike program logged 12,000 trips, most of them replacing short car rides.",
     ["The city placed 500 bikes at 60 stations around town.",
      "Riders took 12,000 trips in the first week of the program.",
      "Bicycles are a common form of urban transportation."]),
    ("a coral nursery",
     ["Divers grow coral fragments on underwater frames.",
      "Fragments are replanted on damaged reefs.",
      "Survival rates exceed 70%."],
     "explain the method and its success",
     "Divers grow coral fragments on underwater frames and replant them on damaged reefs, where more than 70% survive.",
     ["Survival rates exceed 70% in the coral nursery program.",
      "Divers grow coral fragments on underwater frames carefully.",
      "Coral reefs are important ecosystems in the ocean."]),
    ("a library renovation",
     ["The library added a quiet study wing.",
      "Weekly visits rose by a third.",
      "Evening hours were extended."],
     "report the effect of the changes",
     "After the library added a quiet study wing and extended evening hours, weekly visits rose by a third.",
     ["The library added a quiet study wing for patrons.",
      "Weekly visits rose by a third at the library.",
      "Libraries lend books and other materials to the public."]),
    ("a wetland bird census",
     ["Counters logged 84 species in spring.",
      "That is up from 61 a decade ago.",
      "Restored marshland likely drove the gain."],
     "highlight the increase over time",
     "Spring counts have climbed from 61 species a decade ago to 84 today, a gain likely driven by restored marshland.",
     ["Counters logged 84 species in spring this year.",
      "Restored marshland likely drove the gain in species.",
      "A census is a count of a population."]),
    ("a 3D-printed housing project",
     ["A printer builds each wall in under 24 hours.",
      "Material costs are roughly half those of brick.",
      "The first ten homes were occupied this year."],
     "emphasize speed and cost",
     "Printing each wall in under a day and at roughly half the material cost of brick, the project delivered its first ten homes this year.",
     ["The first ten homes were occupied this year by families.",
      "A printer builds each wall in under 24 hours at the site.",
      "3D printing creates objects layer by layer."]),
]


def pool_synthesis(rng: random.Random):
    items = []
    for topic, notes, goal, correct_s, wrongs in _SYNTHESIS:
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
