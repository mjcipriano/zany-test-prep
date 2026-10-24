"""Teaching cards for the ACT English "Knowledge of Language" skills added in
rw_act.py. Same shape as the entries in teaching.py (title, body, key_points,
worked_example, screens[2-4])."""

TEACHING_ACT = {
    "usage_idioms": {
        "title": "Usage and Idioms",
        "body": ("ACT English tests whether you use the right word, not just a grammatical "
                 "one. Commonly confused pairs (affect/effect, than/then, fewer/less, "
                 "lie/lay), fixed prepositions (different from, capable of), comparatives "
                 "versus superlatives, and precise, non-redundant wording all show up here. "
                 "Read for meaning first, then match the word to the job it must do."),
        "key_points": [
            "Decide the part of speech the blank needs, then pick the word that fits it.",
            "Count the things compared: two take -er/more, three or more take -est/most.",
            "Learn idioms as pairs: different from, capable of, interested in, prefer X to Y.",
            "Cut words that repeat an idea already stated ('reopen again', 'final and last').",
        ],
        "worked_example": ("'The frost did not ___ the harvest.' A verb is needed, so 'affect' "
                           "(to influence), not the noun 'effect'."),
        "screens": [
            {"title": "Confusable pairs",
             "body": ("Many wrong answers are real words in the wrong job. 'Affect' is usually "
                      "the verb, 'effect' the noun. 'Than' compares; 'then' orders events in "
                      "time. 'Fewer' counts things; 'less' measures amounts. 'Lie' means to "
                      "recline (lie, lay, lain); 'lay' means to place something (lay, laid, "
                      "laid) and always takes an object."),
             "key_points": ["affect = verb (influence); effect = noun (result).",
                            "fewer for countable nouns; less for amounts.",
                            "lay needs an object; lie does not."]},
            {"title": "Idioms and prepositions",
             "body": ("Some words are glued to a particular preposition: different FROM, "
                      "capable OF, interested IN, consistent WITH, prefer X TO Y, based ON. "
                      "There is no rule to derive these; when a choice swaps the preposition, "
                      "say the phrase aloud and trust the standard pairing."),
             "key_points": ["different from (not 'than'); prefer ... to (not 'than').",
                            "based on, not 'based off of'."]},
            {"title": "Comparing two vs. three or more",
             "body": ("Use the comparative (-er or 'more') when exactly two things are "
                      "compared and the superlative (-est or 'most') for three or more. Never "
                      "stack markers: 'more shorter' and 'most tallest' are always wrong."),
             "key_points": ["Of the two routes, the coastal one is SHORTER.",
                            "Of the three routes, the coastal one is the SHORTEST."]},
            {"title": "Precise, not padded",
             "body": ("Choose the word that says exactly what is meant in the sentence's "
                      "register: a study 'demonstrates', a dispute is 'resolved', seedlings "
                      "are 'planted'. Then strip redundancy: 'reopen again', 'mutually agreed "
                      "together', and 'final and last' each say one thing twice."),
             "worked_example": "The museum will reopen (not 'reopen again') its east wing in May."},
        ],
    },
}
