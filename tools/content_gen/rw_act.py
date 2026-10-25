"""ACT English "Knowledge of Language" generators: usage and idioms.

One skill, ``usage_idioms``, with several families per difficulty (see
registry.py for the FAMILIES contract). Subskills:

  * confused_words        — affect/effect, than/then, fewer/less, among/between,
                            accept/except, lie/lay, principal/principle,
                            complement/compliment, farther/further, ...
  * idiomatic_prepositions — different from, capable of, interested in,
                            prefer ... to, ...
  * comparatives          — -er/more with two items, -est/most with three or more
  * precision_redundancy  — the most precise word for the register; no redundancy

Every family here fills a blank, so each prompt is
"<text with one ___>\\n\\n<instruction stem>" and ``fn.fill_in`` is True.
(who/whom lives in rw_gen pronouns and its/it's in punctuation, so they are
deliberately absent here.)
"""
from __future__ import annotations

import random

from .rw_gen import NAMES, build, cap, conv_stem, dispatch, family, fill, low, soft_low

SUBSKILLS = {
    "usage_idioms": ["confused_words", "idiomatic_prepositions", "comparatives",
                     "precision_redundancy"],
}
# v2.1: confused_words also covers whether/if, number/amount, who/that and double
# negatives; idiomatic_prepositions covers prepositions after comparison words;
# precision_redundancy covers wordy-to-precise substitutions.

_ACT_STEMS = [
    "Which choice completes the text so that it conforms to the conventions of Standard English?",
    "Which choice best completes the text in keeping with standard written English?",
    "Which choice completes the sentence with the correct word?",
]


def _stem(rng):
    return rng.choice(_ACT_STEMS)


# --------------------------------------------------------------------------- #
# Commonly confused words
# (text with ___, correct, [(wrong, rationale)...], why-correct, tier)
# --------------------------------------------------------------------------- #
_CONF = [
    # than / then
    ("{N} finished the puzzle faster ___ anyone expected.", "than",
     [("then", "'then' refers to time or sequence; a comparison needs 'than'."),
      ("that", "'that' does not complete the comparison 'faster ___'."),
      ("as", "'faster as' is not idiomatic; 'faster than' is.")],
     "The sentence compares two speeds, so it needs 'than'.", "easy"),
    ("First the batter rests for an hour; ___ it is poured into the pan.", "then",
     [("than", "'than' makes comparisons; a sequence in time needs 'then'."),
      ("so", "'so' would signal a result, but the sentence lists steps in order."),
      ("thus", "'thus' signals a conclusion, not the next step in a process.")],
     "The sentence describes what happens next in time, so 'then' is correct.", "easy"),
    # accept / except
    ("Everyone ___ {N} had already left the lab by six.", "except",
     [("accept", "'accept' means to receive willingly; the sentence means 'other than'."),
      ("excepting for", "'excepting for' is nonstandard here; 'except' alone is idiomatic."),
      ("but for", "'but for' means 'if not for,' which changes the meaning.")],
     "'Except' means 'other than,' which is the meaning needed.", "easy"),
    ("The committee voted to ___ the revised proposal without changes.", "accept",
     [("except", "'except' means 'other than'; the committee receives the proposal, so 'accept'."),
      ("accede", "'accede' needs 'to' and means to agree to a demand; it is awkward here."),
      ("excerpt", "'excerpt' means to take a passage from a text.")],
     "The committee agrees to receive the proposal, which is 'accept'.", "easy"),
    # affect / effect
    ("The late frost did not ___ the apple harvest as much as farmers feared.", "affect",
     [("effect", "As a verb, 'effect' means to bring about; the frost influences the harvest, so 'affect'."),
      ("affects", "The verb follows 'did not,' so it must be the base form."),
      ("effected", "'effected' means 'brought about,' and the tense is wrong after 'did not'.")],
     "'Affect' is the verb meaning 'to influence.'", "medium"),
    ("Researchers measured the ___ of the new fertilizer on root growth.", "effect",
     [("affect", "'affect' is a verb; after 'the' a noun is needed, and the noun is 'effect'."),
      ("affects", "'affects' is a verb form, but the sentence needs a noun."),
      ("affection", "'affection' means fondness, which makes no sense here.")],
     "'Effect' is the noun meaning 'result.'", "medium"),
    ("The new schedule ___ a complete change in the way the clinic handles walk-ins.", "effected",
     [("affected", "'affected' means 'influenced'; the sentence means the schedule brought the change about."),
      ("effects", "The tense is wrong, and the verb needs the past form 'effected'."),
      ("had affect on", "'had affect on' is not idiomatic; the noun is 'effect'.")],
     "As a verb, 'effect' means 'to bring about,' which is the sense here.", "hard"),
    # fewer / less
    ("The new checkout lane is for shoppers with ten items or ___.", "fewer",
     [("less", "'less' is for quantities that cannot be counted; items are counted, so 'fewer'."),
      ("lesser", "'lesser' means 'smaller in importance,' not 'a smaller number.'"),
      ("few", "'ten items or few' is ungrammatical; the comparative is needed.")],
     "Countable nouns like 'items' take 'fewer.'", "easy"),
    ("The reservoir held ___ water in August than at any time since 1988.", "less",
     [("fewer", "'fewer' is for things you count; water is measured, not counted, so 'less'."),
      ("lesser", "'lesser' means 'smaller in importance,' not a smaller amount."),
      ("least", "'least' is a superlative, but only two times are being compared.")],
     "Uncountable nouns like 'water' take 'less.'", "medium"),
    ("The survey took ___ than fifteen minutes, so most students completed it.", "less",
     [("fewer", "A span of time is treated as a single amount, so 'less than fifteen minutes'."),
      ("lesser", "'lesser' is not used for amounts of time."),
      ("few", "'few than' is ungrammatical.")],
     "Periods of time, money, and distance are treated as amounts and take 'less.'", "hard"),
    # among / between
    ("The prize money was divided ___ the three finalists.", "among",
     [("between", "'between' is for two parties; with three or more, use 'among'."),
      ("amongst of", "'amongst of' is ungrammatical."),
      ("in between", "'in between' is for physical position, not sharing among a group.")],
     "'Among' is used for three or more.", "easy"),
    ("The agreement ___ the two villages has lasted for a century.", "between",
     [("among", "'among' is for three or more; two villages take 'between'."),
      ("amid", "'amid' means 'surrounded by,' not a relationship of two parties."),
      ("betwixt", "'betwixt' is archaic and not standard written English.")],
     "'Between' is used for exactly two.", "easy"),
    # lie / lay
    ("Exhausted, the hikers decided to ___ down beside the stream.", "lie",
     [("lay", "'lay' needs an object (you lay something down); the hikers themselves recline, so 'lie'."),
      ("laid", "'laid' is the past tense of 'lay' and needs an object."),
      ("lain", "'lain' is a past participle and needs a helping verb such as 'had.'")],
     "'Lie' means to recline and takes no object.", "medium"),
    ("Please ___ the wet towels on the railing so they can dry.", "lay",
     [("lie", "'lie' takes no object, but here the towels are being placed, so 'lay'."),
      ("lain", "'lain' is a past participle of 'lie' and cannot be a command."),
      ("laying", "An -ing form cannot serve as the main verb of a command.")],
     "'Lay' means to place something and takes an object.", "medium"),
    ("The dog had ___ in the shade all afternoon before the storm broke.", "lain",
     [("laid", "'laid' is the past participle of 'lay' and needs an object."),
      ("lay", "After 'had,' the past participle 'lain' is needed, not the past tense 'lay'."),
      ("lied", "'lied' means 'told a falsehood.'")],
     "The dog reclines (no object), and after 'had' the participle of 'lie' is 'lain.'", "hard"),
    ("Yesterday {N} ___ the blueprints across the table for everyone to see.", "laid",
     [("lay", "'lay' as a past tense means 'reclined'; placing blueprints needs 'laid'."),
      ("lied", "'lied' means 'told a falsehood.'"),
      ("lain", "'lain' is a participle of 'lie' and cannot take an object.")],
     "Placing an object in the past is 'laid.'", "hard"),
    # principal / principle
    ("The ___ reason for the delay was a shortage of steel.", "principal",
     [("principle", "'principle' is a rule or belief; the adjective meaning 'main' is 'principal'."),
      ("principled", "'principled' means 'having strong morals.'"),
      ("principally", "An adverb cannot modify the noun 'reason.'")],
     "'Principal' as an adjective means 'main.'", "medium"),
    ("The judge based her ruling on a simple ___: contracts must be honored.", "principle",
     [("principal", "'principal' means 'main' or 'head of a school'; a rule or belief is a 'principle'."),
      ("principality", "'principality' is a small state ruled by a prince."),
      ("principled", "'principled' is an adjective and cannot follow 'a simple'.")],
     "'Principle' is a fundamental rule.", "medium"),
    # complement / compliment
    ("The tart cherries ___ the richness of the chocolate.", "complement",
     [("compliment", "'compliment' means to praise; to complete or go well with is 'complement'."),
      ("complements", "The subject 'cherries' is plural, so the verb needs no -s."),
      ("compliments", "Wrong word and wrong number.")],
     "'Complement' means to go well with or complete.", "medium"),
    ("The critic paid the young cellist a rare ___ after the concert.", "compliment",
     [("complement", "'complement' means something that completes; praise is a 'compliment'."),
      ("complementary", "This is an adjective, but a noun is needed after 'a rare'."),
      ("complimenting", "An -ing form cannot be the object of 'paid.'")],
     "'Compliment' is an expression of praise.", "medium"),
    # farther / further
    ("The trailhead is two miles ___ down the valley than the map shows.", "farther",
     [("further", "'further' is preferred for degree; a physical distance takes 'farther'."),
      ("farthest", "A comparison of two points needs the comparative, not the superlative."),
      ("far", "'far down the valley than' is ungrammatical; the comparative is needed.")],
     "Physical distance takes 'farther.'", "hard"),
    ("The board refused to discuss the merger any ___ until the audit was complete.", "further",
     [("farther", "'farther' is for physical distance; degree or extent takes 'further'."),
      ("furthest", "Only two situations are compared, so the comparative is needed."),
      ("more far", "'more far' is not standard English.")],
     "Degree or extent (not distance) takes 'further.'", "hard"),
    # cite / site / sight ; allude / elude ; ensure / insure ; precede / proceed
    ("The report fails to ___ a single source for its most surprising figure.", "cite",
     [("site", "'site' is a place; to refer to a source is to 'cite' it."),
      ("sight", "'sight' is vision; the report should 'cite' sources."),
      ("sites", "'sites' is a noun and the wrong word.")],
     "'Cite' means to refer to a source.", "medium"),
    ("The sprinter's record ___ every challenger for a decade.", "eluded",
     [("alluded", "'alluded' means 'referred indirectly to'; escaping someone is 'eluded'."),
      ("illuded", "'illuded' is not a standard word."),
      ("eluding", "An -ing form cannot be the main verb here.")],
     "'Elude' means to escape or evade.", "hard"),
    ("Please ___ that the gate is locked before you leave.", "ensure",
     [("insure", "'insure' refers to insurance policies; to make certain is 'ensure'."),
      ("assure", "'assure' takes a person as its object ('assure me that...')."),
      ("ensuring", "An -ing form cannot be the main verb of a request.")],
     "'Ensure' means to make certain.", "medium"),
    ("A short film will ___ the main feature at tonight's screening.", "precede",
     [("proceed", "'proceed' means to go forward; coming before is 'precede'."),
      ("proceeds", "'proceeds' means money earned and is the wrong word."),
      ("preceed", "This is a misspelling.")],
     "'Precede' means to come before.", "hard"),
    ("The warm weather had little ___ on the early blooms.", "effect",
     [("affect", "As a noun, 'affect' is a technical psychology term; the ordinary noun is 'effect'."),
      ("effecting", "An -ing form cannot follow 'little' as a noun here."),
      ("affects", "This is a verb form, but a noun is required after 'little'.")],
     "After 'little,' a noun is needed, and the noun is 'effect.'", "easy"),
    ("Most of the volunteers were ___ than twenty years old.", "younger",
     [("more young", "'more young' is not standard; the comparative is 'younger'."),
      ("youngest", "Only the volunteers' ages are compared with twenty, so the comparative is needed."),
      ("young", "'young than' is ungrammatical.")],
     "A comparison with 'than' takes the comparative form.", "easy"),
    ("The grant was awarded to ___ of the two teams had the stronger proposal.", "whichever",
     [("whoever", "'whoever' refers to people; the subject is a team, and the sentence refers to teams as things."),
      ("which ever", "'whichever' is one word."),
      ("whatever", "'whatever' does not refer to one member of a specified pair.")],
     "'Whichever' selects one of a stated set of things.", "hard"),
]


@family(fill_in=True)
def ui_confused(rng, difficulty):
    """Commonly confused word pairs in a single sentence."""
    tiers = {"easy": ["easy"], "medium": ["easy", "medium"], "hard": ["medium", "hard"]}[difficulty]
    pool = [c for c in _CONF if c[4] in tiers]
    text, right, wrongs, why, _ = rng.choice(pool)
    name = rng.choice(NAMES)
    text = text.format(N=name)
    if difficulty == "hard":
        text = rng.choice(["According to the minutes, ", "As the newsletter notes, ", "In the end, "]) + soft_low(text)
    correct = (right, f"Correct. {why}")
    return build(rng, fill(text, _stem(rng)), correct, wrongs, subskill="confused_words",
                 explanation=why, tags=["usage", "confused-words"])


# --------------------------------------------------------------------------- #
# Idiomatic prepositions
# (frame with ___, correct preposition, wrong preps, rule)
# --------------------------------------------------------------------------- #
_PREP = [
    ("The new recipe is different ___ the one my grandmother used.", "from", ["than", "to", "with"],
     "'different from' is the standard idiom."),
    ("The intern proved capable ___ running the lab on her own.", "of", ["to", "for", "in"],
     "'capable of' is the idiom."),
    ("{N} has always been interested ___ the history of bridges.", "in", ["on", "about", "for"],
     "'interested in' is the idiom."),
    ("Most of the committee preferred the shorter proposal ___ the longer one.", "to", ["than", "over than", "from"],
     "'prefer X to Y' is the standard idiom."),
    ("The guide insisted ___ checking every harness twice.", "on", ["in", "to", "for"],
     "'insist on' is the idiom."),
    ("The results are consistent ___ last year's survey.", "with", ["to", "of", "for"],
     "'consistent with' is the idiom."),
    ("The town is famous ___ its covered bridges.", "for", ["of", "by", "with"],
     "'famous for' is the idiom."),
    ("The researchers were surprised ___ how quickly the moss recovered.", "by", ["of", "for", "on"],
     "'surprised by' is the idiom; 'surprised at' also occurs, but it is not offered."),
    ("The new policy complies ___ state regulations.", "with", ["to", "by", "for"],
     "'comply with' is the idiom."),
    ("{N} apologized ___ arriving late to the rehearsal.", "for", ["of", "about", "at"],
     "'apologize for' is the idiom."),
    ("The design was based ___ sketches from the 1920s.", "on", ["off of", "from", "in"],
     "'based on' is the idiom; 'based off of' is nonstandard."),
    ("The bakery is adjacent ___ the old post office.", "to", ["of", "with", "from"],
     "'adjacent to' is the idiom."),
    ("The coach was pleased ___ the team's effort in the second half.", "with", ["of", "for", "at"],
     "'pleased with' is the idiom."),
    ("The museum was named in honor ___ its first curator.", "of", ["for", "to", "by"],
     "'in honor of' is the idiom."),
    ("The scientists agreed ___ a single method for counting the nests.", "on", ["with", "to", "about"],
     "'agree on (a plan)' is the idiom; 'agree with' takes a person."),
    ("The sculpture consists ___ three bronze rings.", "of", ["in", "with", "from"],
     "'consist of' is the idiom."),
    ("The town has been independent ___ the county since 1902.", "of", ["from", "to", "with"],
     "'independent of' is the idiom."),
    ("The mayor is responsible ___ approving the final budget.", "for", ["of", "to", "with"],
     "'responsible for' is the idiom."),
]


@family(fill_in=True)
def ui_preposition(rng, difficulty):
    """Idiomatic prepositions after common adjectives and verbs."""
    frame, right, wrongs, rule = rng.choice(_PREP)
    name = rng.choice(NAMES)
    text = frame.format(N=name)
    correct = (right, f"Correct. {rule}")
    ds = [(w, f"'{w}' is not the preposition this expression takes in standard English.") for w in wrongs]
    if difficulty == "medium":
        text = rng.choice(["As the brochure explains, ", "By all accounts, ", "As it happens, "]) + soft_low(text)
    elif difficulty == "hard":
        close = rng.choice(["No one disputed the point.", "The wording was never in doubt.",
                            "The detail is easy to miss."])
        text = rng.choice(["As the brochure explains, ", "As it happens, "]) + soft_low(text) + " " + close
    return build(rng, fill(text, _stem(rng)), correct, ds, subskill="idiomatic_prepositions",
                 explanation=rule, tags=["usage", "idiom", "preposition"])


_PREP_PAIRS = [
    ("different", "from", "than"), ("capable", "of", "to"), ("interested", "in", "about"),
    ("consistent", "with", "to"), ("responsible", "for", "of"), ("independent", "of", "from"),
]
_PREP_PASS = [
    ("The harbor festival began in 1961 as a one-day boat parade.",
     "Today's event is very different ___ that first parade", "from", ["than", "to", "with"],
     "It now runs for three days and fills every dock."),
    ("Amara joined the observatory as a volunteer at sixteen.",
     "Within a year she was capable ___ operating the main telescope alone", "of", ["to", "in", "for"],
     "She now trains the newer volunteers."),
    ("The mill's water wheel has turned since the 1840s.",
     "Engineers were surprised ___ how little the oak gears had worn", "by", ["of", "on", "for"],
     "The wheel still grinds flour every Saturday."),
    ("The town council debated the park plan for months.",
     "Members finally agreed ___ a design with two playgrounds", "on", ["with", "to", "about"],
     "Construction begins in the spring."),
    ("The new bakery opened beside the station in May.",
     "Its owners prefer local flour ___ imported brands", "to", ["than", "over than", "from"],
     "Customers say they can taste the difference."),
    ("Nadia's documentary follows three lighthouse keepers.",
     "The film is based ___ interviews she recorded over two winters", "on", ["off of", "from", "in"],
     "It premiered at a festival last fall."),
]


@family(fill_in=True, small_space=True)
def ui_prep_passage(rng, difficulty):
    """Mini passage with an idiomatic preposition in the middle sentence."""
    lead, mid, right, wrongs, close = rng.choice(_PREP_PASS)
    correct = (right, f"Correct. The idiom requires '{right}' here.")
    ds = [(w, f"'{w}' does not form the standard idiom with the word before the blank.") for w in wrongs]
    if difficulty == "easy":
        text = f"{lead} {mid}."
    elif difficulty == "medium":
        text = f"{lead} {mid}. {close}"
    else:
        text = f"{lead} " + rng.choice(["As regulars will tell you, ", "As it happens, ",
                                        "According to the staff, "]) + soft_low(mid) + f". {close}"
    return build(rng, fill(text, _stem(rng)), correct, ds, subskill="idiomatic_prepositions",
                 explanation="Certain adjectives and verbs pair with a fixed preposition; memorize the idiom.",
                 tags=["usage", "idiom", "preposition", "passage"], est=50)


# --------------------------------------------------------------------------- #
# Comparatives and superlatives
# --------------------------------------------------------------------------- #
_ADJ = {
    "routes": [("short", "shorter", "shortest"), ("steep", "steeper", "steepest"),
               ("busy", "busier", "busiest"), ("scenic", "more scenic", "most scenic")],
    "towers": [("tall", "taller", "tallest"), ("old", "older", "oldest"),
               ("narrow", "narrower", "narrowest"), ("famous", "more famous", "most famous")],
    "trains": [("fast", "faster", "fastest"), ("early", "earlier", "earliest"),
               ("crowded", "more crowded", "most crowded"), ("cheap", "cheaper", "cheapest"),
               ("reliable", "more reliable", "most reliable")],
    "bridges": [("old", "older", "oldest"), ("long", "longer", "longest"),
                ("busy", "busier", "busiest"), ("expensive", "more expensive", "most expensive")],
    "ovens": [("hot", "hotter", "hottest"), ("reliable", "more reliable", "most reliable"),
              ("expensive", "more expensive", "most expensive"), ("old", "older", "oldest")],
    "drafts": [("short", "shorter", "shortest"), ("good", "better", "best"),
               ("clear", "clearer", "clearest"), ("ambitious", "more ambitious", "most ambitious")],
}
_CMP_PAIRS = [("the coastal route", "the mountain route", "routes"), ("the north tower", "the south tower", "towers"),
              ("the morning train", "the evening train", "trains"), ("the old bridge", "the new bridge", "bridges"),
              ("the brick oven", "the gas oven", "ovens"), ("the first draft", "the second draft", "drafts")]
_CMP_GROUPS = [("the three routes", "the coastal route", "routes"), ("the four towers", "the north tower", "towers"),
               ("the five trains", "the morning train", "trains"), ("all the bridges in the county", "the old bridge", "bridges"),
               ("the six ovens in the bakery", "the brick oven", "ovens"), ("the many drafts", "the first draft", "drafts")]


@family(fill_in=True)
def ui_comparative(rng, difficulty):
    """-er/more for two items; -est/most for three or more; no double forms."""
    two = rng.random() < 0.5
    if two:
        a, b, plural = rng.choice(_CMP_PAIRS)
        base, cmp_, sup = rng.choice(_ADJ[plural])
        text = rng.choice([f"Of the two {plural}, {a} is ___.",
                           f"{cap(a)} is ___ than {b}.",
                           f"Between {a} and {b}, the first is clearly ___."])
        correct = (cmp_, f"Correct. Two items are compared, so the comparative '{cmp_}' is needed.")
        if " " not in cmp_:
            more = (f"more {cmp_}", "This doubles up the comparative ('more' plus -er), which is nonstandard.")
        else:
            more = (f"the {sup}", "This uses the superlative, which is for three or more items.")
        ds = [(sup, f"The superlative '{sup}' is for three or more items; only two are compared."),
              more,
              (base, f"The plain form '{base}' cannot complete a comparison of two items.")]
        rule = "Use the comparative (-er or 'more') when exactly two things are compared."
    else:
        group, item, key = rng.choice(_CMP_GROUPS)
        base, cmp_, sup = rng.choice(_ADJ[key])
        text = rng.choice([f"Of {group}, {item} is the ___.",
                           f"{cap(item)} is the ___ of {group}.",
                           f"Among {group}, {item} is by far the ___."])
        correct = (sup, f"Correct. Three or more items are compared, so the superlative '{sup}' is needed.")
        most = f"most {cmp_}"
        ds = [(cmp_, f"The comparative '{cmp_}' is for two items; here there are three or more."),
              (most, "This stacks two superlative markers, which is nonstandard."),
              (base, f"The plain form '{base}' does not single out one item from the group.")]
        rule = "Use the superlative (-est or 'most') when three or more things are compared."
    if difficulty != "easy":
        text = rng.choice(["According to the guidebook, ", "As most visitors agree, ", "In my experience, "]) + low(text)
    if difficulty == "hard":
        text = text + " " + rng.choice(["The others are rarely mentioned.", "Few would argue the point.",
                                        "The difference is easy to see."])
    return build(rng, fill(text, _stem(rng)), correct, ds, subskill="comparatives",
                 explanation=rule, tags=["usage", "comparative"])


# --------------------------------------------------------------------------- #
# Precision and redundancy
# (text, precise word, [(wrong, rationale)], why)
# --------------------------------------------------------------------------- #
_PRECISE = [
    ("The study ___ that the moss can survive months without water.", "demonstrates",
     [("says", "'says' is vague and informal for a scientific finding."),
      ("shows off", "'shows off' means to display proudly, which does not fit the register."),
      ("tells", "'tells' needs a listener and is imprecise here.")],
     "'Demonstrates' precisely states that the study provides evidence for the finding."),
    ("The architect ___ the damaged wing rather than demolishing it.", "restored",
     [("fixed up", "'fixed up' is informal and vague for a formal description of architectural work."),
      ("redid", "'redid' is imprecise; it does not say the wing was returned to its original state."),
      ("remade", "'remade' suggests building something new, not returning it to its former condition.")],
     "'Restored' precisely means returned to its original condition."),
    ("Because the data were ___, the team repeated the experiment.", "inconsistent",
     [("weird", "'weird' is informal and vague for a scientific report."),
      ("off", "'off' is slang and imprecise."),
      ("inconsistently", "An adverb cannot follow 'were' as a description of the data.")],
     "'Inconsistent' precisely describes data that do not agree with one another."),
    ("The treaty ___ the border dispute that had simmered for decades.", "resolved",
     [("got rid of", "'got rid of' is informal and imprecise."),
      ("solved", "'solved' is used for problems or puzzles; disputes are 'resolved'."),
      ("dissolved", "'dissolved' means broke up or melted, not settled.")],
     "'Resolved' precisely means settled or brought to an end."),
    ("Volunteers ___ more than two hundred native seedlings along the creek.", "planted",
     [("put in", "'put in' is vague and informal."),
      ("installed", "'installed' is for equipment, not living plants."),
      ("inserted", "'inserted' is imprecise for placing plants in soil.")],
     "'Planted' is the precise verb for placing seedlings in the ground."),
    ("The committee will ___ the proposal before voting next week.", "review",
     [("look at", "'look at' is vague and informal."),
      ("peek at", "'peek at' suggests a quick, casual glance, which does not fit a formal process."),
      ("overlook", "'overlook' means to fail to notice, the opposite of the intended meaning.")],
     "'Review' precisely means to examine carefully."),
    ("The curator ___ the painting to the early 1600s based on its pigments.", "dated",
     [("guessed", "'guessed' suggests no evidence, but the curator used the pigments."),
      ("figured", "'figured' is informal."),
      ("aged", "'aged' means grew older; it does not mean assigned a date.")],
     "'Dated' precisely means assigned a date to."),
    ("Rising fuel costs ___ the ferry company to raise its fares.", "compelled",
     [("made it so", "'made it so' is wordy and informal."),
      ("told", "A cost cannot 'tell' a company anything."),
      ("compelling", "An -ing form cannot be the main verb.")],
     "'Compelled' precisely means forced by circumstances."),
    ("The lighthouse keeper ___ the weather in a logbook every evening.", "recorded",
     [("wrote about", "'wrote about' is vague; a logbook holds precise entries."),
      ("jotted", "'jotted' suggests hasty notes, which does not fit a daily official log."),
      ("recited", "'recited' means spoke aloud from memory.")],
     "'Recorded' precisely describes keeping a written log."),
    ("The new filter ___ nearly all of the sediment from the river water.", "removes",
     [("gets out", "'gets out' is informal and imprecise."),
      ("kills", "Sediment is not alive; 'kills' is the wrong word."),
      ("moves", "'moves' does not say the sediment is taken out.")],
     "'Removes' precisely states that the sediment is taken out."),
    ("The biologist ___ the frogs by the pattern of spots on their backs.", "identified",
     [("found out", "'found out' is informal and vague."),
      ("knew", "'knew' does not describe the act of telling the frogs apart."),
      ("identifying", "An -ing form cannot be the main verb.")],
     "'Identified' precisely means recognized and named."),
    ("The drought ___ the region's wheat harvest by nearly half.", "reduced",
     [("shrunk down", "'shrunk down' is informal and redundant."),
      ("lowered", "'lowered' is used for levels or prices, not harvests."),
      ("deducted", "'deducted' means subtracted from a total, which is the wrong sense.")],
     "'Reduced' precisely describes making the harvest smaller."),
]
# (text with ___, concise correct, [(redundant/imprecise, rationale)], why)
_REDUND = [
    ("The two companies ___ to share the cost of the new bridge.", "agreed",
     [("mutually agreed together", "'mutually' and 'together' repeat what 'agreed' already says."),
      ("came to a mutual agreement together", "This is wordy and doubly redundant."),
      ("consented", "'consented' implies permission rather than a joint decision.")],
     "'Agreed' states the idea once, without repetition."),
    ("The archive ___ every photograph before the move.", "cataloged",
     [("made a list and catalog of", "'list' and 'catalog' say the same thing twice."),
      ("cataloged and listed in order", "'listed in order' repeats what 'cataloged' means."),
      ("counted", "'counted' gives a total, not an organized record.")],
     "'Cataloged' is precise and complete on its own."),
    ("The museum will ___ its east wing in the spring.", "reopen",
     [("reopen again", "'reopen' already means 'open again.'"),
      ("open back up again", "'back up again' is doubly redundant with 'open'."),
      ("unclose", "'unclose' is not standard English.")],
     "'Reopen' already contains the idea of 'again.'"),
    ("The engineers ___ the bridge's original design.", "kept",
     [("kept and retained", "'kept' and 'retained' mean the same thing."),
      ("continued to keep on with", "This is wordy and repetitive."),
      ("held onto", "'held onto' is informal for a formal description of design work.")],
     "'Kept' says it once."),
    ("The storm ___ the harbor's wooden pier.", "destroyed",
     [("completely and totally destroyed", "'completely' and 'totally' add nothing to 'destroyed'."),
      ("destroyed to the point of ruin", "'to the point of ruin' repeats what 'destroyed' means."),
      ("damaged", "'damaged' understates it; the pier was destroyed.")],
     "'Destroyed' is already absolute; intensifiers are redundant."),
    ("At dawn the fishing boats ___ the harbor.", "left",
     [("departed and left", "'departed' and 'left' are the same idea."),
      ("exited out of", "'exited' already means 'went out of.'"),
      ("fled", "'fled' implies escaping danger, which the sentence does not suggest.")],
     "'Left' is complete and precise."),
    ("The council ___ the plan after a brief debate.", "approved",
     [("approved and gave its approval to", "This states the same action twice."),
      ("gave the go-ahead for", "This is informal for an official decision."),
      ("tolerated", "'tolerated' implies reluctant acceptance, not formal approval.")],
     "'Approved' is the precise formal word."),
    ("The ___ chapter of the novel takes place in a lighthouse.", "final",
     [("final and last", "'final' and 'last' mean the same thing."),
      ("last final", "This doubles the same idea."),
      ("terminal", "'terminal' is used for stations or illnesses, not chapters.")],
     "'Final' alone is precise."),
    ("Scientists ___ the comet in 1986.", "observed",
     [("observed and saw", "'observed' and 'saw' are redundant together."),
      ("made observations and looked at", "This is wordy and repetitive."),
      ("eyeballed", "'eyeballed' is slang and does not fit a scientific sentence.")],
     "'Observed' is precise and sufficient."),
    ("The new rule ___ to every employee.", "applies",
     [("applies to each and every one of", "'each and every one of' is redundant with 'every.'"),
      ("is applicable and applies", "This repeats the same idea."),
      ("belongs", "'belongs to' means ownership, not being governed by a rule.")],
     "'Applies' states the relationship once."),
    ("The two trails ___ at a wooden footbridge.", "meet",
     [("meet together", "'together' repeats what 'meet' already means."),
      ("join up and meet", "'join up' and 'meet' are the same idea."),
      ("collide", "'collide' means crash, which is the wrong sense for trails.")],
     "'Meet' is complete on its own."),
    ("The committee ___ its decision until spring.", "postponed",
     [("postponed until later", "'until later' repeats what 'postponed' means, and the sentence already gives the time."),
      ("put off and postponed", "'put off' and 'postponed' say the same thing."),
      ("canceled", "'canceled' means the decision will not happen at all, which contradicts 'until spring'.")],
     "'Postponed' says it once and precisely."),
]


@family(fill_in=True)
def ui_precision(rng, difficulty):
    """Choose the most precise word for the register."""
    text, right, wrongs, why = rng.choice(_PRECISE)
    correct = (right, f"Correct. {why}")
    if difficulty != "easy":
        text = rng.choice(["According to the article, ", "As the report explains, ", "By most accounts, "]) + low(text) \
            if not text.startswith("Because") else text
    if difficulty == "hard":
        text = text + " " + rng.choice(["The finding was not disputed.", "The detail appears in a footnote.",
                                        "No one objected."])
    return build(rng, fill(text, rng.choice([
        "Which choice provides the most precise word in the context of the sentence?",
        "Which choice best fits the formal tone and precise meaning of the sentence?"])),
                 correct, wrongs, subskill="precision_redundancy",
                 explanation=why, tags=["usage", "precision"], est=50)


@family(fill_in=True, small_space=True)
def ui_redundancy(rng, difficulty):
    """Avoid redundant and wordy phrasing."""
    text, right, wrongs, why = rng.choice(_REDUND)
    correct = (right, f"Correct. {why}")
    if difficulty != "easy":
        text = rng.choice(["As the records show, ", "In the end, ", "As it happens, "]) + low(text) \
            if not text.startswith("At dawn") else text
    if difficulty == "hard":
        text = text + " " + rng.choice(["The change took effect immediately.", "Nobody objected.",
                                        "Residents noticed at once."])
    return build(rng, fill(text, rng.choice([
        "Which choice expresses the idea most concisely and precisely?",
        "Which choice completes the sentence without redundancy?"])),
                 correct, wrongs, subskill="precision_redundancy",
                 explanation=why, tags=["usage", "redundancy", "concision"], est=50)


_CONF_PASS = [
    ("Two routes lead to the summit.", "The western trail is ___ than the eastern one, but it is steeper", "shorter",
     [("shortest", "Only two trails are compared, so the superlative is wrong."),
      ("more short", "'more short' is nonstandard; the comparative is 'shorter'."),
      ("short", "'short than' is ungrammatical.")],
     "Most hikers choose it anyway."),
    ("The clinic switched to an online booking system last year.", "Since ___, missed appointments have fallen by a third", "then",
     [("than", "'than' is for comparisons; a point in time needs 'then'."),
      ("that", "'since that' is vague and does not mark the time."),
      ("when", "'since when' does not fit a statement.")],
     "Staff say the phones are finally quiet."),
    ("The cannery once employed most of the town.", "Its closing had a lasting ___ on the harbor district", "effect",
     [("affect", "A noun is needed after 'lasting'; the noun is 'effect'."),
      ("effecting", "An -ing form cannot be the object of 'had'."),
      ("affection", "'affection' means fondness.")],
     "Several warehouses stood empty for a decade."),
    ("The reading room seats forty people.", "On exam weeks there are far ___ seats than students", "fewer",
     [("less", "Seats are counted, so 'fewer' is correct."),
      ("lesser", "'lesser' means lower in importance."),
      ("few", "'few than' is ungrammatical.")],
     "The library adds folding tables in the hall."),
    ("Three bakeries entered the county fair's bread contest.", "The judges divided the top prize ___ all three", "among",
     [("between", "'between' is for two parties; three take 'among'."),
      ("in between", "'in between' describes physical position."),
      ("amongst of", "'amongst of' is ungrammatical.")],
     "None of the bakers objected."),
    ("The fence along the ridge was built in 1911.", "Hikers often ___ their packs against it while they rest", "lay",
     [("lie", "'lie' takes no object; placing packs needs 'lay'."),
      ("lain", "'lain' is a participle and cannot be the main verb here."),
      ("laying", "An -ing form cannot be the main verb.")],
     "The posts are worn smooth."),
    ("The orchestra's conductor retired after thirty years.", "Her replacement has a very different style ___ hers", "from",
     [("than", "'different from' is the standard idiom."),
      ("to", "'different to' is not standard in American English."),
      ("with", "'different with' is not idiomatic.")],
     "Audiences have warmed to it slowly."),
    ("The mill pond froze early this year.", "Skaters were ___ to try the ice before the town tested it", "eager",
     [("anxious", "'anxious' means worried; the skaters are enthusiastic, not fearful."),
      ("eagerly", "An adverb cannot follow 'were' to describe the skaters."),
      ("eagerness", "A noun cannot complete 'were ___ to try'.")],
     "The town posted warnings on the bank."),
]


@family(fill_in=True, small_space=True)
def ui_passage(rng, difficulty):
    """Mini passage with a usage/idiom blank in the middle sentence."""
    lead, mid, right, wrongs, close = rng.choice(_CONF_PASS)
    correct = (right, f"Correct. '{right}' is the standard choice in this context.")
    if difficulty == "easy":
        text = f"{lead} {mid}."
    elif difficulty == "medium":
        text = f"{lead} {mid}. {close}"
    else:
        text = f"{lead} " + rng.choice(["As regulars will tell you, ", "As it happens, ",
                                        "According to the staff, "]) + soft_low(mid) + f". {close}"
    return build(rng, fill(text, _stem(rng)), correct, wrongs, subskill="confused_words",
                 explanation=("Read the sentence around the blank for its meaning, then pick the word "
                              "whose standard meaning and form match it."),
                 tags=["usage", "passage"], est=50)


# --------------------------------------------------------------------------- #
# v2.1 ADDITIONS
# --------------------------------------------------------------------------- #
_CONF.extend([
    ("The council has not decided ___ to extend the deadline.", "whether",
     [("if", "'if' introduces a condition; a choice between alternatives takes 'whether'."),
      ("weather", "'weather' refers to the climate."),
      ("whether or not if", "This piles up connectors and is ungrammatical.")],
     "'Whether' introduces alternatives ('whether to extend or not').", "easy"),
    ("Please let us know ___ you can attend the ceremony.", "whether",
     [("if or not", "'if or not' is not standard; 'whether or not' is."),
      ("weather", "'weather' refers to the climate."),
      ("that whether", "Two connectors cannot be stacked here.")],
     "'Whether' is the standard choice before an alternative ('can attend or cannot').", "medium"),
    ("The ___ of volunteers doubled after the article appeared.", "number",
     [("amount", "'amount' is for things that cannot be counted; volunteers are counted, so 'number'."),
      ("quantity", "'quantity' is used for measured material, not people."),
      ("numbers", "The singular 'number' is needed after 'the ___ of'.")],
     "Countable nouns take 'number of'.", "easy"),
    ("A surprising ___ of rain fell in a single afternoon.", "amount",
     [("number", "'number' is for countable things; rain is measured, so 'amount'."),
      ("quantities", "The plural is wrong after 'a surprising'."),
      ("sum", "'sum' refers to money or a total of numbers.")],
     "Uncountable nouns like 'rain' take 'amount of'.", "medium"),
    ("The engineer ___ designed the dam retired last year.", "who",
     [("which", "'which' refers to things, not people."),
      ("whom", "'whom' is objective, but the pronoun is the subject of 'designed'."),
      ("what", "'what' cannot introduce a clause describing a person here.")],
     "Use 'who' for people.", "easy"),
    ("The bridge ___ spans the gorge was finished in 1902.", "that",
     [("who", "'who' refers to people, not things."),
      ("whom", "'whom' refers to people and is objective."),
      ("what", "'what' cannot introduce a relative clause here.")],
     "Use 'that' or 'which' for things; 'who' is reserved for people.", "easy"),
    ("The crew could ___ see the buoy through the fog.", "hardly",
     [("not hardly", "'not hardly' is a double negative."),
      ("hardly not", "'hardly' is already negative; adding 'not' creates a double negative."),
      ("scarcely not", "'scarcely not' is a double negative.")],
     "'Hardly' is itself negative, so it is not paired with 'not'.", "medium"),
    ("The clinic does not have ___ appointments left this week.", "any",
     [("no", "'does not have no' is a double negative."),
      ("none", "'none' cannot modify 'appointments' here, and it doubles the negative."),
      ("no more of", "This is both a double negative and unidiomatic.")],
     "After a negative verb, use 'any', not 'no'.", "medium"),
    ("Nobody on the committee ___ the proposal before the vote.", "had read",
     [("hadn't read", "'Nobody ... hadn't' is a double negative."),
      ("had not never read", "'not never' is a double negative."),
      ("hadn't never read", "This stacks two negatives.")],
     "'Nobody' is already negative; the verb must stay positive.", "hard"),
    ("The new policy is quite different ___ the one it replaced.", "from",
     [("than", "'different than' is nonstandard in careful writing; 'different from' is the idiom."),
      ("to", "'different to' is not standard American English."),
      ("with", "'different with' is not idiomatic.")],
     "'Different from' is the standard comparison idiom.", "medium"),
    ("Compared ___ last year's harvest, this year's is small.", "with",
     [("than", "'compared than' is not idiomatic."),
      ("of", "'compared of' is not idiomatic."),
      ("by", "'compared by' changes the meaning (who did the comparing).")],
     "'Compared with' (or 'compared to') is the idiom.", "medium"),
    ("The new sauce is superior ___ the old recipe in every way.", "to",
     [("than", "'superior' is not a comparative with 'than'; it takes 'to'."),
      ("over", "'superior over' is not idiomatic."),
      ("from", "'superior from' is not idiomatic.")],
     "'Superior to' and 'inferior to' take 'to'.", "hard"),
    ("The results differ sharply ___ those reported in 2019.", "from",
     [("than", "'differ than' is not idiomatic; 'differ from' is."),
      ("to", "'differ to' is not standard."),
      ("against", "'differ against' is not idiomatic.")],
     "'Differ from' is the idiom.", "hard"),
])

_WORDY = [
    ("___ the storm, the ferry stayed in port.", "Because of",
     [("Due to the fact of", "This phrase is padded; 'because of' says the same thing in two words."),
      ("In light of the fact that there was", "Wordy and awkward."),
      ("On account of the reason of", "Redundant and unidiomatic.")]),
    ("The committee will meet ___ to review the plan.", "tomorrow",
     [("at a later point in time tomorrow", "'At a later point in time' adds nothing to 'tomorrow'."),
      ("in the near future of tomorrow", "Padded and unidiomatic."),
      ("tomorrow at some point in time", "'At some point in time' is empty filler.")]),
    ("___ the trail is closed, hikers must use the ridge road.", "If",
     [("In the event that", "'In the event that' is a wordy substitute for 'if'."),
      ("Under circumstances in which", "Wordy and stiff."),
      ("Should it be the case that", "Padded phrasing for a simple condition.")]),
    ("The library ___ its hours during exam week.", "extends",
     [("makes an extension of", "A noun phrase where a single verb does the job."),
      ("has a policy of extending", "Padded; the simple verb is clearer."),
      ("is in the practice of extending", "Wordy and indirect.")]),
    ("The report ___ three risks.", "identifies",
     [("makes an identification of", "A padded noun phrase for a simple verb."),
      ("serves to identify", "'serves to' adds nothing."),
      ("is identifying the existence of", "Wordy and vague.")]),
    ("___, the harvest was small.", "This year",
     [("At this point in time this year", "'At this point in time' is filler."),
      ("In the current year that we are in", "Redundant."),
      ("During the course of this present year", "Padded.")]),
    ("The mayor spoke ___ about the budget.", "briefly",
     [("for a short period of time", "Five words where one adverb will do."),
      ("in a brief manner of speaking", "'Manner of speaking' is filler."),
      ("in a way that was brief", "Wordy.")]),
    ("The divers ___ the wreck twice a month.", "inspect",
     [("conduct an inspection of", "A padded noun phrase for a simple verb."),
      ("make it a point to carry out inspections of", "Wordy."),
      ("are responsible for the inspecting of", "Indirect and wordy.")]),
    ("___ the price, the tickets sold out.", "Despite",
     [("In spite of the fact of", "'Despite' says it in one word."),
      ("Regardless of the fact that there was", "Wordy and ungrammatical here."),
      ("Notwithstanding the consideration of", "Stiff and padded.")]),
    ("The band ___ for two hours.", "rehearsed",
     [("held a rehearsal session lasting", "A padded noun phrase for a simple verb."),
      ("engaged in the activity of rehearsing", "Wordy."),
      ("did some rehearsing over a period of", "Vague and padded.")]),
]


@family(fill_in=True, small_space=True)
def ui_wordy(rng, difficulty):
    """Replace a padded phrase with the precise short form."""
    text, right, wrongs = rng.choice(_WORDY)
    correct = (right, f"Correct. '{right}' states the idea directly, without filler.")
    if difficulty != "easy" and not text.startswith("___"):
        text = rng.choice(["As the minutes note, ", "In the end, ", "As usual, "]) + low(text)
    if difficulty == "hard":
        text = text + " " + rng.choice(["Nobody minded.", "The reason was never explained.", "It was over quickly."])
    stem = rng.choice(["Which choice expresses the idea most concisely?",
                       "Which choice completes the sentence without wordiness?"])
    return build(rng, fill(text, stem), correct, wrongs, subskill="precision_redundancy",
                 explanation="Prefer the direct word or phrase; padding such as 'due to the fact that' adds length, not meaning.",
                 tags=["usage", "wordiness", "concision"], est=45)


_WHO_THAT = [
    ("the engineer", "designed the dam", "p"), ("the violinist", "won the audition", "p"),
    ("the baker", "opened the second shop", "p"), ("the guide", "led us through the caves", "p"),
    ("the bridge", "spans the gorge", "t"), ("the recipe", "calls for rye flour", "t"),
    ("the mural", "covers the north wall", "t"), ("the ferry", "crosses to the island", "t"),
    ("the historian", "catalogued the letters", "p"), ("the telescope", "sits on the plateau", "t"),
]


@family(fill_in=True)
def ui_who_that(rng, difficulty):
    """'who' for people; 'that'/'which' for things."""
    noun, act, cat = rng.choice(_WHO_THAT)
    name = rng.choice(NAMES)
    frames = [f"{name} thanked {noun} ___ {act}.", f"Everyone remembers {noun} ___ {act}.",
              f"The article profiles {noun} ___ {act}."] if cat == "p" else \
             [f"{name} photographed {noun} ___ {act}.", f"Everyone remembers {noun} ___ {act}.",
              f"The article describes {noun} ___ {act}."]
    text = rng.choice(frames)
    if cat == "p":
        correct = ("who", f"Correct. '{noun}' is a person, so 'who' introduces the clause.")
        ds = [("which", "'which' refers to things, not people."),
              ("whom", "'whom' is objective, but the pronoun is the subject of the clause."),
              ("what", "'what' cannot introduce a relative clause here.")]
    else:
        correct = ("that", f"Correct. '{noun}' is a thing, so 'that' introduces the clause.")
        ds = [("who", "'who' refers to people, not things."),
              ("whom", "'whom' refers to people and is objective."),
              ("what", "'what' cannot introduce a relative clause here.")]
    if difficulty != "easy":
        text = rng.choice(["As it happens, ", "By all accounts, ", "In the end, "]) + soft_low(text)
    if difficulty == "hard":
        text = text + " " + rng.choice(["The story is well known.", "Few people know the details.", "A plaque marks the spot."])
    return build(rng, fill(text, _stem(rng)), correct, ds, subskill="confused_words",
                 explanation="Use 'who' for people and 'that' or 'which' for things.",
                 tags=["usage", "who-that"])


_CMP_PREP = [
    ("The study compares the new vaccine ___ the older formula.", "with", ["than", "to of", "by"]),
    ("The guide contrasted the limestone caves ___ the lava tubes to the south.", "with", ["than", "to", "by"]),
    ("Her second novel differs ___ her first in almost every way.", "from", ["than", "to", "against"]),
    ("The committee weighed the new plan ___ the old one for a month.", "against", ["than", "to", "from"]),
    ("The lab contrasted the morning samples ___ those taken at dusk.", "with", ["than", "to", "by"]),
    ("The new schedule varies ___ the old one only on Fridays.", "from", ["than", "to", "with"]),
    ("The copy is identical ___ the original in every detail.", "to", ["with", "than", "as"]),
    ("The brick oven is superior ___ the gas oven for bread.", "to", ["than", "over", "from"]),
    ("The valley's climate is similar ___ that of the coast.", "to", ["with", "than", "as"]),
    ("Nothing in the archive is comparable ___ the 1890 letters.", "to", ["than", "with of", "against"]),
    ("The new route is preferable ___ the old one in winter.", "to", ["than", "over", "from"]),
    ("The sketch bears little resemblance ___ the finished mural.", "to", ["with", "of", "than"]),
    ("Measured ___ last year's total, the harvest was small.", "against", ["than", "to", "by of"]),
]


@family(fill_in=True)
def ui_compare_prep(rng, difficulty):
    """Prepositions after verbs and adjectives of comparison."""
    text, right, wrongs = rng.choice(_CMP_PREP)
    correct = (right, f"Correct. This expression of comparison takes '{right}'.")
    ds = [(w, f"'{w}' does not form the standard comparison idiom here.") for w in wrongs]
    if difficulty != "easy":
        text = rng.choice(["According to the report, ", "As the guide explained, ", "In short, "]) + low(text)
    if difficulty == "hard":
        text = text + " " + rng.choice(["The difference is striking.", "Few would disagree.", "The point is rarely disputed."])
    return build(rng, fill(text, _stem(rng)), correct, ds, subskill="idiomatic_prepositions",
                 explanation="Comparison words carry fixed prepositions: compare with, differ from, identical to, superior to.",
                 tags=["usage", "idiom", "comparison-preposition"])


_DOUBLE_NEG = [
    ("The crew could ___ see the buoy through the fog.", "hardly", ["not hardly", "hardly not", "scarcely not"]),
    ("The clinic does not have ___ appointments left this week.", "any", ["no", "none", "no more of"]),
    ("{N} has ___ been to the island.", "never", ["not never", "never not", "not ever never"]),
    ("There was ___ anyone left in the hall by midnight.", "scarcely", ["not scarcely", "scarcely not", "hardly not"]),
    ("The guide did not say ___ about the closed trail.", "anything", ["nothing", "nothing at all", "none of nothing"]),
    ("We could not find the key ___.", "anywhere", ["nowhere", "not nowhere", "nowheres"]),
    ("The ferry ___ runs late in winter.", "rarely", ["doesn't rarely", "rarely doesn't", "not rarely"]),
    ("Nobody ___ the second letter.", "had seen", ["hadn't seen", "had not never seen", "hadn't never seen"]),
]


@family(fill_in=True)
def ui_double_negative(rng, difficulty):
    """Avoid double negatives (hardly, never, any vs. no)."""
    text, right, wrongs = rng.choice(_DOUBLE_NEG)
    name = rng.choice(NAMES)
    text = text.format(N=name)
    correct = (right, "Correct. A single negative expresses the meaning; adding another would cancel or muddle it.")
    ds = [(w, f"'{w}' creates a double negative.") for w in wrongs]
    if difficulty != "easy":
        text = rng.choice(["As it turned out, ", "By all accounts, ", "In short, "]) + soft_low(text)
    if difficulty == "hard":
        text = text + " " + rng.choice(["Nobody was surprised.", "That much was clear.", "The matter ended there."])
    return build(rng, fill(text, _stem(rng)), correct, ds, subskill="confused_words",
                 explanation=("Words like 'hardly', 'never', and 'nobody' are already negative; pair them with "
                              "positive forms ('any', 'anything'), not with 'no' or 'not'."),
                 tags=["usage", "double-negative"])


_NUM_AMT = [
    ("The ___ of visitors doubled after the bridge opened.", "number", "visitors"),
    ("A large ___ of sand washed onto the road overnight.", "amount", "sand"),
    ("The ___ of applicants surprised the committee.", "number", "applicants"),
    ("The ___ of water in the reservoir fell by a third.", "amount", "water"),
    ("A small ___ of coins was found under the floor.", "number", "coins"),
    ("The ___ of sunlight the garden receives varies by season.", "amount", "sunlight"),
    ("The ___ of bridges in the county has not changed since 1950.", "number", "bridges"),
    ("The ___ of flour in the recipe can be halved.", "amount", "flour"),
    ("The ___ of volunteers grew every year.", "number", "volunteers"),
    ("A surprising ___ of rain fell in a single afternoon.", "amount", "rain"),
    ("The ___ of ferries crossing each day doubled in summer.", "number", "ferries"),
    ("The ___ of honey from the hives varies with the weather.", "amount", "honey"),
    ("A record ___ of kites filled the sky on Saturday.", "number", "kites"),
    ("The ___ of gravel needed for the path surprised the crew.", "amount", "gravel"),
    ("The ___ of letters in the archive exceeds ninety thousand.", "number", "letters"),
    ("The ___ of snow on the ridge is measured every morning.", "amount", "snow"),
]


@family(fill_in=True)
def ui_number_amount(rng, difficulty):
    """number (countable) vs. amount (uncountable), with fewer/less companions."""
    text, right, noun = rng.choice(_NUM_AMT)
    countable = right == "number"
    correct = (right, f"Correct. '{noun}' is {'counted' if countable else 'measured, not counted'}, so '{right}' is the word.")
    ds = [("amount" if countable else "number", f"'{'amount' if countable else 'number'}' is for "
                                                 f"{'things that cannot be counted' if countable else 'things that are counted'}; '{noun}' is not."),
          ("quantity" if countable else "sum", "This word does not fit the kind of thing being described."),
          ("numbers" if countable else "amounts", "The singular is needed after 'the ___ of'.")]
    if difficulty != "easy":
        text = rng.choice(["According to the survey, ", "As the ranger noted, ", "Last year, "]) + low(text)
    if difficulty == "hard":
        text = text + " " + rng.choice(["The trend continues.", "No one could explain it.", "The figure is now posted online."])
    return build(rng, fill(text, _stem(rng)), correct, ds, subskill="confused_words",
                 explanation="'Number' goes with things you count; 'amount' goes with things you measure.",
                 tags=["usage", "number-amount"])


FAMILIES = {
    "usage_idioms": {
        "easy": [ui_confused, ui_preposition, ui_comparative, ui_redundancy, ui_passage,
                 ui_who_that, ui_number_amount, ui_wordy],
        "medium": [ui_confused, ui_preposition, ui_comparative, ui_precision, ui_redundancy, ui_prep_passage, ui_passage,
                   ui_who_that, ui_number_amount, ui_compare_prep, ui_double_negative, ui_wordy],
        "hard": [ui_confused, ui_preposition, ui_precision, ui_comparative, ui_redundancy, ui_prep_passage, ui_passage,
                 ui_compare_prep, ui_double_negative, ui_wordy, ui_number_amount],
    },
}


def gen_usage_idioms(rng: random.Random, difficulty: str = "medium"):
    return dispatch(FAMILIES["usage_idioms"], rng, difficulty)
