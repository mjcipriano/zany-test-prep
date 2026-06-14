"""Original reading passages and their comprehension questions.

All prose here is original, written for this project. Each single passage yields
five questions (main idea, inference, text structure/purpose, words-in-context,
command of evidence). Paired passages yield cross-text questions.

The builders convert the compact data below into question bodies (with a passage
or paired-passage stimulus) for the orchestrator.
"""
from __future__ import annotations

import random

from .util import mc

# Each passage: dict with text + one question spec per reading skill.
# A question spec is (prompt, [opt0..opt3], correct_index, [rat0..rat3], explanation).
PASSAGES = [
    {
        "id": "octopus", "title": "The Color of Thought",
        "text": (
            "An octopus has no bones and, oddly, almost no color of its own. Yet in "
            "less than a second it can flush deep red with alarm or fade to match the "
            "speckled gray of a stone. Beneath its skin lie millions of tiny sacs of "
            "pigment, each ringed by muscle. When the muscles pull, the sacs widen and "
            "color blooms; when they relax, the color vanishes. Stranger still, the "
            "octopus is colorblind, so it cannot see the very hues it produces. Some "
            "researchers suspect its skin itself senses light, letting the animal paint "
            "a disguise it can never admire."),
        "main_idea": (
            "Which choice best states the main idea of the passage?",
            ["The octopus rapidly changes color through a muscular pigment system it cannot itself see.",
             "The octopus is the only sea creature that lacks bones.",
             "Researchers have fully explained how octopus skin detects light.",
             "Octopuses prefer to hide near gray stones rather than red coral."],
            0,
            ["Correct. The passage centers on the surprising mechanism of color change in a colorblind animal.",
             "The passage never claims octopuses are unique in lacking bones.",
             "The passage calls the skin-sensing idea a suspicion, not a settled explanation.",
             "No preference for gray over red is described; both are examples of camouflage."],
            "The passage builds toward the paradox of an animal that produces colors it cannot perceive."),
        "inference": (
            "It can reasonably be inferred from the passage that the octopus's color change is",
            ["controlled by muscles acting on pigment sacs",
             "caused by the surrounding water temperature",
             "learned slowly over the animal's lifetime",
             "visible only to other octopuses"],
            0,
            ["Correct. The passage states muscles widen the sacs to reveal color.",
             "Temperature is never mentioned as a cause.",
             "The change happens in under a second, not slowly over a lifetime.",
             "The passage does not say only octopuses can see the colors."],
            "The text directly ties color change to muscles pulling on pigment sacs."),
        "structure": (
            "Which choice best describes the overall structure of the passage?",
            ["It introduces a surprising trait, explains its mechanism, then notes a deeper puzzle.",
             "It compares two species of octopus in detail.",
             "It argues that octopuses should be protected from fishing.",
             "It lists steps a reader could follow to observe an octopus."],
            0,
            ["Correct. The passage moves from a striking fact to a mechanism to the colorblindness paradox.",
             "Only one animal is discussed, not two species.",
             "The passage makes no argument about protection.",
             "No how-to steps are given."],
            "The passage's purpose is to explain and then deepen a surprising fact, not to argue or instruct."),
        "wic": (
            "As used in the passage, the word “flush” most nearly means",
            ["become suffused with color", "rinse with water",
             "discard or empty out", "become embarrassed"],
            0,
            ["Correct. The octopus's skin fills with red color.",
             "No rinsing is described.",
             "Nothing is being discarded.",
             "An octopus does not feel embarrassment; the sense here is about color."],
            "In context, to 'flush deep red' means to fill with color."),
        "evidence": (
            "Which detail best supports the idea that the octopus cannot perceive its own display?",
            ["The statement that the octopus is colorblind.",
             "The statement that it has no bones.",
             "The statement that color blooms in under a second.",
             "The statement that pigment sacs are ringed by muscle."],
            0,
            ["Correct. Colorblindness directly explains why it cannot see the hues it makes.",
             "Lacking bones is unrelated to perceiving color.",
             "Speed of change does not address perception.",
             "The muscle ring explains how color appears, not whether the animal sees it."],
            "The claim about perception is supported specifically by the detail that the animal is colorblind."),
    },
    {
        "id": "press", "title": "Letters of Lead",
        "text": (
            "Before the 1450s, a book in Europe was copied by hand, a task that could "
            "occupy a scribe for a year. Johannes Gutenberg changed that arithmetic. By "
            "casting individual letters in metal, he could arrange them into a page, "
            "print hundreds of copies, then rearrange the same letters for the next "
            "page. The cost of a book did not fall overnight, and many scholars still "
            "prized handwritten volumes. But within fifty years, presses across the "
            "continent had produced millions of books. Ideas that once crept from city "
            "to city now traveled in bulk, and a reader in one town could hold the exact "
            "words read by a stranger far away."),
        "main_idea": (
            "Which choice best states the central idea of the passage?",
            ["Gutenberg's reusable metal type made books far easier to reproduce and spread.",
             "Handwritten books were always more beautiful than printed ones.",
             "Books became cheap immediately after the press was invented.",
             "Scribes disappeared the moment the printing press arrived."],
            0,
            ["Correct. The passage emphasizes how reusable type transformed the reproduction and reach of books.",
             "Beauty of handwriting is not the passage's claim.",
             "The passage explicitly says costs did not fall overnight.",
             "It notes scholars still prized handwritten volumes, so scribes did not vanish at once."],
            "The passage frames the press as a turning point in how widely texts could circulate."),
        "inference": (
            "The passage most strongly suggests that, before Gutenberg, identical copies of a text were",
            ["rare, because hand-copying introduced variation and took great effort",
             "common in every European town",
             "produced faster than printed books",
             "considered worthless by scholars"],
            0,
            ["Correct. Hand-copying was slow and the passage stresses the novelty of identical printed copies.",
             "The passage implies the opposite of commonness.",
             "Hand-copying took a year, far slower than printing.",
             "Scholars are said to prize handwritten books, not scorn them."],
            "The contrast the passage draws implies hand-copied texts were neither fast nor uniform."),
        "structure": (
            "The author mentions that 'the cost of a book did not fall overnight' primarily to",
            ["qualify the claim that the press caused instant change",
             "argue that the press was a failure",
             "prove that scribes were dishonest",
             "introduce a step-by-step printing guide"],
            0,
            ["Correct. The detail tempers the idea of an immediate revolution before noting the long-term effect.",
             "The passage treats the press as transformative, not a failure.",
             "Scribes' honesty is never discussed.",
             "No printing guide follows."],
            "The clause adds nuance, acknowledging change was real but gradual."),
        "wic": (
            "As used in the passage, the word “crept” most nearly means",
            ["moved slowly", "complained quietly", "crawled on hands and knees", "frightened people"],
            0,
            ["Correct. Ideas moved slowly from city to city before the press.",
             "No complaining is meant.",
             "Ideas do not literally crawl; the sense is slow movement.",
             "Nothing about fear is implied."],
            "Contrasted with traveling 'in bulk,' 'crept' conveys slow movement."),
        "evidence": (
            "Which detail best supports the idea that printing dramatically increased the number of books?",
            ["Within fifty years, presses had produced millions of books.",
             "A scribe could spend a year on one copy.",
             "Many scholars still prized handwritten volumes.",
             "Gutenberg cast individual letters in metal."],
            0,
            ["Correct. The figure of millions in fifty years directly shows the surge in output.",
             "This describes the old method, not the increase.",
             "This shows continued demand for manuscripts, not the scale of printing.",
             "This explains the method but not the resulting quantity."],
            "The claim about volume is supported by the 'millions of books' figure."),
    },
    {
        "id": "tardigrade", "title": "The Survivor",
        "text": (
            "Smaller than a grain of salt, the tardigrade looks almost comical, plodding "
            "on eight stubby legs. Its talent, however, is anything but ordinary. When "
            "its surroundings dry out, the creature expels most of its water and curls "
            "into a husk called a tun. In this state it can endure boiling heat, the "
            "vacuum of space, and doses of radiation that would kill nearly any other "
            "animal. Years later, a single drop of water can revive it. Scientists are "
            "still untangling how the tardigrade protects its cells, but one clue is a "
            "special set of proteins that seem to harden into glass, cradling delicate "
            "structures until water returns."),
        "main_idea": (
            "Which choice best states the main idea of the passage?",
            ["The tardigrade survives extreme conditions by drying into a protected, revivable state.",
             "The tardigrade is the smallest animal on Earth.",
             "Scientists have completely explained the tardigrade's survival.",
             "The tardigrade lives only in outer space."],
            0,
            ["Correct. The passage centers on how the tardigrade endures extremes by drying out.",
             "The passage compares its size to salt but never calls it the smallest animal.",
             "The text says scientists are 'still untangling' the mechanism.",
             "Space is one extreme it can survive, not its home."],
            "The passage's focus is the dehydration survival strategy and its partial explanation."),
        "inference": (
            "It can reasonably be inferred that the 'tun' state is best described as a form of",
            ["suspended dormancy", "rapid growth", "permanent death", "social cooperation"],
            0,
            ["Correct. The animal halts activity yet can revive, indicating dormancy.",
             "Drying into a husk is not growth.",
             "It can be revived, so it is not dead.",
             "No social behavior is described."],
            "Because the creature can be revived after years, the tun is a dormant, not lethal, state."),
        "structure": (
            "The passage is organized mainly by",
            ["introducing the animal, then describing its survival ability and a proposed mechanism",
             "comparing the tardigrade with a named competitor",
             "tracing the history of tardigrade research by decade",
             "presenting an argument for funding space travel"],
            0,
            ["Correct. It moves from description to ability to a tentative explanation.",
             "No specific competitor is named.",
             "No decade-by-decade history is given.",
             "The passage does not argue for funding."],
            "The structure proceeds from portrait to capability to mechanism."),
        "wic": (
            "As used in the passage, the word “cradling” most nearly means",
            ["protectively holding", "rocking to sleep", "complaining about", "measuring carefully"],
            0,
            ["Correct. The proteins shield delicate structures.",
             "No literal rocking occurs.",
             "Nothing is being complained about.",
             "Measuring is not the sense here."],
            "The proteins 'cradle' structures in the sense of protectively holding them."),
        "evidence": (
            "Which detail best supports the claim that the tardigrade's revival can occur after a long delay?",
            ["Years later, a single drop of water can revive it.",
             "It plods on eight stubby legs.",
             "It is smaller than a grain of salt.",
             "It expels most of its water when drying out."],
            0,
            ["Correct. 'Years later' directly establishes the long delay before revival.",
             "Its legs are unrelated to revival timing.",
             "Its size does not address the delay.",
             "Expelling water describes entering the tun, not the delay before revival."],
            "The long-delay claim rests on the 'years later' detail."),
    },
    {
        "id": "violin", "title": "The Borrowed Violin",
        "text": (
            "Nadia had practiced on a school instrument so battered that two of its pegs "
            "slipped during every lesson. When her teacher handed her a loaner violin for "
            "the recital, she nearly refused; it felt wrong to play something so fine. But "
            "as she drew the bow across the strings, the tone opened like a window onto a "
            "bright street. Notes she had fought for all year now arrived easily, as if "
            "the instrument had been waiting for her. Afterward, returning it to its case, "
            "she understood that her old struggles had not been wasted. The fine violin "
            "had simply revealed the player she had quietly become."),
        "main_idea": (
            "Which choice best captures the main idea of the passage?",
            ["A fine instrument reveals the skill Nadia had developed through earlier struggle.",
             "Nadia decides to quit playing the violin after the recital.",
             "School instruments are always better than loaners.",
             "Nadia's teacher refuses to let her use the loaner violin."],
            0,
            ["Correct. The closing lines tie the fine violin to the skill she had quietly built.",
             "She does not quit; she gains insight.",
             "The passage shows the loaner as finer than her battered school violin.",
             "The teacher hands her the loaner rather than refusing."],
            "The narrative resolves on the idea that her growth, not just the violin, produced the beautiful playing."),
        "inference": (
            "It can reasonably be inferred that Nadia almost refused the loaner because she",
            ["felt unworthy of such a fine instrument",
             "disliked the recital pieces",
             "preferred instruments with slipping pegs",
             "could not read the music"],
            0,
            ["Correct. 'It felt wrong to play something so fine' signals a sense of unworthiness.",
             "Her feelings about the pieces are not the reason given.",
             "She struggled with slipping pegs; she did not prefer them.",
             "Nothing suggests she cannot read music."],
            "Her hesitation stems from feeling the instrument was too fine for her."),
        "structure": (
            "The passage is structured as",
            ["a moment of doubt that gives way to a realization",
             "a list of tips for choosing a violin",
             "a debate between two musicians",
             "a chronological history of an orchestra"],
            0,
            ["Correct. It moves from Nadia's hesitation to her concluding insight.",
             "No tips are offered.",
             "There is no debate between characters.",
             "It is a single scene, not an orchestra's history."],
            "The arc runs from doubt to epiphany."),
        "wic": (
            "As used in the passage, the word “drew” most nearly means",
            ["pulled", "sketched", "attracted a crowd", "concluded"],
            0,
            ["Correct. She pulled the bow across the strings.",
             "No drawing or sketching is involved.",
             "No crowd is attracted in that sentence.",
             "It does not mean 'concluded' here."],
            "To 'draw the bow' means to pull it across the strings."),
        "evidence": (
            "Which detail best supports the idea that Nadia's playing improved on the loaner?",
            ["Notes she had fought for all year now arrived easily.",
             "Two of the pegs slipped during every lesson.",
             "She returned the violin to its case.",
             "She nearly refused the instrument."],
            0,
            ["Correct. The ease of once-difficult notes shows improved playing.",
             "Slipping pegs describe the old instrument, not improvement.",
             "Returning the violin does not show improved playing.",
             "Her near-refusal is about hesitation, not improvement."],
            "Improvement is shown by once-hard notes arriving easily."),
    },
    {
        "id": "birdsong", "title": "Songs With Accents",
        "text": (
            "A white-crowned sparrow raised near San Francisco does not sing quite like "
            "one raised a hundred miles north. The basic melody is the same, but small "
            "flourishes differ from place to place, forming what biologists call song "
            "dialects. Young sparrows learn these dialects by listening to adult males "
            "during a brief window in their first months. A bird that hears no song in "
            "that window grows up to sing a thin, simplified tune. The dialects can drift "
            "over generations, much as human accents do, so a recording made decades ago "
            "may sound subtly foreign to the birds singing in the same meadow today."),
        "main_idea": (
            "Which choice best states the central idea of the passage?",
            ["Sparrows learn local song dialects that vary by place and shift over time.",
             "All white-crowned sparrows sing exactly the same song.",
             "Sparrows are born already knowing their full song.",
             "Human accents are caused by birdsong."],
            0,
            ["Correct. The passage explains learned, place-based dialects that change over generations.",
             "The passage stresses variation, not sameness.",
             "Birds must learn the song; they are not born knowing it.",
             "The human-accent comparison is an analogy, not a cause."],
            "The passage's through-line is learned, drifting song dialects."),
        "inference": (
            "It can reasonably be inferred that a sparrow's ability to learn a full song depends on",
            ["hearing adult song during an early window",
             "the color of its crown",
             "the size of the meadow it lives in",
             "the age of nearby recordings"],
            0,
            ["Correct. A bird that hears no song in that window sings only a thin tune.",
             "Crown color is not linked to learning.",
             "Meadow size is never mentioned as a factor.",
             "Old recordings illustrate drift, not a bird's learning ability."],
            "The passage ties full song to exposure during the early learning window."),
        "structure": (
            "The comparison to human accents primarily serves to",
            ["help readers understand how dialects can drift over time",
             "prove that birds and humans are closely related",
             "argue that recordings should be banned",
             "list the steps of a sparrow's life cycle"],
            0,
            ["Correct. The analogy clarifies generational drift in song.",
             "The passage draws an analogy, not a claim of kinship.",
             "No argument about banning recordings appears.",
             "It is an analogy, not a life-cycle list."],
            "The accent comparison is an explanatory analogy for drift."),
        "wic": (
            "As used in the passage, the word “drift” most nearly means",
            ["change gradually", "float on water", "pile up like snow", "fall asleep"],
            0,
            ["Correct. Dialects change gradually over generations.",
             "No floating is meant.",
             "No snow-like piling is meant.",
             "It has nothing to do with sleep."],
            "Here 'drift' means to change slowly over time."),
        "evidence": (
            "Which detail best supports the claim that song is learned rather than innate?",
            ["A bird that hears no song in its early window sings only a thin, simplified tune.",
             "The basic melody is the same across regions.",
             "A recording may sound foreign decades later.",
             "Sparrows live in meadows."],
            0,
            ["Correct. Deprivation of song leading to a poor tune shows learning is required.",
             "Shared melody alone does not prove learning.",
             "Drift over decades concerns change, not whether song is learned.",
             "Habitat does not address learning."],
            "The deprivation result is the key evidence that song is learned."),
    },
    {
        "id": "sleep", "title": "The Night Shift of the Brain",
        "text": (
            "Sleep can look like idleness, but the brain is busy. During deep sleep, "
            "waves of electrical activity sweep across the cortex, and researchers think "
            "these waves help move the day's memories into longer-term storage. In one "
            "line of experiments, students who slept after studying a list of words "
            "remembered more of them than students who stayed awake the same number of "
            "hours. Sleep may also clear away molecular waste that builds up while we are "
            "awake. None of this means more sleep is always better; the relationship "
            "appears to follow a curve, with both too little and too much linked to poorer "
            "performance. What the brain seems to need is enough, at the right times."),
        "main_idea": (
            "Which choice best states the main idea of the passage?",
            ["Sleep is an active process that supports memory and brain maintenance, in the right amount.",
             "Staying awake longer always improves memory.",
             "The brain does nothing useful during sleep.",
             "More sleep is always better for performance."],
            0,
            ["Correct. The passage presents sleep as active and beneficial within an optimal range.",
             "The experiment shows the opposite of this claim.",
             "The passage argues the brain is busy during sleep.",
             "The passage explicitly rejects 'more is always better.'"],
            "The passage's balanced claim is that sleep actively helps the brain, but only in adequate amounts."),
        "inference": (
            "The passage suggests that the link between sleep and performance is",
            ["best at a moderate amount rather than at extremes",
             "strongest when people sleep as little as possible",
             "unrelated to memory",
             "identical for every person regardless of timing"],
            0,
            ["Correct. The 'curve' detail implies a moderate optimum.",
             "Too little sleep is linked to poorer performance.",
             "The passage ties sleep to memory consolidation.",
             "It mentions 'the right times,' implying timing matters."],
            "The curve description implies a middle optimum, not an extreme."),
        "structure": (
            "The author includes the word-list experiment mainly to",
            ["provide evidence that sleep aids memory",
             "argue that studying is pointless",
             "describe how to fall asleep faster",
             "compare two unrelated brain regions"],
            0,
            ["Correct. The experiment supports the memory-consolidation claim.",
             "The passage does not dismiss studying.",
             "No sleep-onset advice is given.",
             "No two regions are compared."],
            "The experiment functions as supporting evidence."),
        "wic": (
            "As used in the passage, the word “clear” most nearly means",
            ["remove", "make transparent", "earn as profit", "leap over"],
            0,
            ["Correct. Sleep removes molecular waste.",
             "Transparency is not the sense here.",
             "No profit is meant.",
             "No leaping is meant."],
            "To 'clear away waste' is to remove it."),
        "evidence": (
            "Which detail best supports the claim that sleep aids memory?",
            ["Students who slept after studying remembered more words than those who stayed awake.",
             "Waves of activity sweep across the cortex.",
             "Sleep may clear molecular waste.",
             "The relationship follows a curve."],
            0,
            ["Correct. The comparison of sleepers to non-sleepers directly supports the memory claim.",
             "The waves describe a mechanism, not the memory outcome.",
             "Waste clearance is a separate benefit.",
             "The curve concerns amount, not the memory result itself."],
            "The strongest support is the experimental comparison of recall."),
    },
    {
        "id": "soil", "title": "Gifts of the Volcano",
        "text": (
            "It seems strange that people would farm in the shadow of a volcano, but many "
            "do, and for good reason. When a volcano erupts, it scatters ash rich in "
            "minerals such as potassium and phosphorus. Over years, this ash breaks down "
            "into some of the most fertile soil on Earth. Crops planted in it can grow "
            "unusually well, which is why slopes near certain volcanoes are crowded with "
            "farms and villages. The bargain is uneasy: the same mountain that feeds the "
            "fields can also threaten them. Farmers weigh the steady gift of rich soil "
            "against the rare but real danger overhead, and generation after generation, "
            "many choose to stay."),
        "main_idea": (
            "Which choice best states the central idea of the passage?",
            ["Volcanic ash creates fertile soil, drawing farmers despite the danger of eruptions.",
             "Volcanoes are harmless to nearby villages.",
             "Farming is impossible near volcanoes.",
             "Potassium is the only mineral plants need."],
            0,
            ["Correct. The passage explains the fertility-versus-danger trade-off that keeps farmers near volcanoes.",
             "The passage notes a real danger, so volcanoes are not harmless.",
             "The passage says many people do farm there.",
             "It names potassium and phosphorus, not a single required mineral."],
            "The passage balances the benefit of fertile soil against eruption risk."),
        "inference": (
            "It can reasonably be inferred that farmers near volcanoes",
            ["accept a known risk in exchange for productive land",
             "are unaware that volcanoes can erupt",
             "harvest crops only in years without eruptions",
             "prefer poor soil to rich soil"],
            0,
            ["Correct. The passage describes weighing the gift of soil against the danger.",
             "They 'weigh' the danger, so they are aware of it.",
             "No such yearly pattern is stated.",
             "They value the rich soil, not poor soil."],
            "The 'uneasy bargain' framing implies an accepted, known risk."),
        "structure": (
            "The phrase 'the bargain is uneasy' marks a shift from",
            ["describing a benefit to acknowledging a danger",
             "telling a story to listing instructions",
             "praising farmers to criticizing them",
             "discussing ash to discussing oceans"],
            0,
            ["Correct. The passage pivots from fertile-soil benefits to the danger overhead.",
             "No instructions follow.",
             "The passage does not criticize farmers.",
             "Oceans are never discussed."],
            "The phrase signals the turn from benefit to risk."),
        "wic": (
            "As used in the passage, the word “scatters” most nearly means",
            ["spreads widely", "frightens away", "destroys completely", "collects together"],
            0,
            ["Correct. The eruption spreads ash widely.",
             "Nothing is being frightened.",
             "It spreads ash, not destroys it.",
             "Scattering is the opposite of collecting."],
            "To 'scatter ash' is to spread it over a wide area."),
        "evidence": (
            "Which detail best supports the claim that volcanic regions attract dense settlement?",
            ["Slopes near certain volcanoes are crowded with farms and villages.",
             "Ash contains potassium and phosphorus.",
             "The same mountain can threaten the fields.",
             "Ash takes years to break down."],
            0,
            ["Correct. 'Crowded with farms and villages' directly shows dense settlement.",
             "Mineral content explains fertility, not settlement density.",
             "The threat detail concerns risk, not attraction.",
             "Breakdown time does not address settlement."],
            "Settlement density is shown by the 'crowded' detail."),
    },
    {
        "id": "bicycle", "title": "The Machine That Walked",
        "text": (
            "The earliest ancestor of the bicycle had no pedals at all. Built in 1817, it "
            "was a wooden frame on two wheels that a rider straddled and pushed along with "
            "the feet, like walking while seated. People mocked it, and rutted roads made "
            "it impractical, so it soon faded. Decades passed before inventors added "
            "pedals, then a chain, then air-filled tires that smoothed the ride. Each "
            "change drew new riders, and by the 1890s the bicycle had become a craze. It "
            "offered something rare for the time: cheap, independent travel that needed no "
            "horse and no rails. For many people, especially those long denied easy "
            "movement, the machine quietly widened the boundaries of daily life."),
        "main_idea": (
            "Which choice best states the central idea of the passage?",
            ["The bicycle evolved through gradual improvements into a popular means of independent travel.",
             "The first bicycle was an immediate success.",
             "Bicycles required horses to operate.",
             "Pedals were part of the very first bicycle design."],
            0,
            ["Correct. The passage traces stepwise improvements leading to the bicycle's popularity and freedom of movement.",
             "The first version was mocked and faded, not an immediate success.",
             "The passage says it needed no horse.",
             "The earliest version had no pedals."],
            "The passage's arc is incremental improvement culminating in widespread, independent travel."),
        "inference": (
            "It can reasonably be inferred that the bicycle's popularity in the 1890s depended on",
            ["earlier technical improvements like pedals, chains, and tires",
             "the disappearance of all roads",
             "a return to horse-drawn travel",
             "the original 1817 design remaining unchanged"],
            0,
            ["Correct. The passage links each improvement to new riders before the craze.",
             "Roads did not disappear; rough roads were a problem.",
             "The bicycle's appeal was needing no horse.",
             "The design changed substantially from 1817."],
            "Popularity followed the accumulation of improvements."),
        "structure": (
            "The passage is organized mainly as",
            ["a chronological account of an invention's development",
             "a comparison of two competing inventors",
             "a set of instructions for building a bicycle",
             "an argument against modern transportation"],
            0,
            ["Correct. It proceeds from 1817 through later improvements to the 1890s.",
             "No two inventors are compared.",
             "No build instructions are given.",
             "It does not argue against transportation."],
            "The structure is a chronological development story."),
        "wic": (
            "As used in the passage, the word “widened” most nearly means",
            ["expanded", "measured", "flattened", "delayed"],
            0,
            ["Correct. The bicycle expanded the boundaries of daily life.",
             "No measuring is meant.",
             "Flattening is not the sense here.",
             "It does not mean to delay."],
            "To 'widen the boundaries' is to expand them."),
        "evidence": (
            "Which detail best supports the idea that the bicycle offered unusual freedom of movement?",
            ["It offered cheap, independent travel that needed no horse and no rails.",
             "It was built in 1817 as a wooden frame.",
             "People mocked the earliest version.",
             "Rutted roads made the first version impractical."],
            0,
            ["Correct. Independent travel without horse or rails directly shows the freedom it offered.",
             "Its construction date does not address freedom.",
             "Mockery concerns the early version's reception.",
             "Poor roads describe an obstacle, not the freedom."],
            "Freedom of movement is supported by the 'no horse and no rails' detail."),
    },
    {
        "id": "microplastic", "title": "Small Pieces, Wide Reach",
        "text": (
            "Plastic does not simply vanish. Exposed to sunlight and waves, a bottle or "
            "bag breaks into ever-smaller fragments until the pieces are too tiny to see. "
            "These microplastics have turned up in river water, in Arctic ice, and even "
            "in the bodies of fish and birds. Because the particles are so small, "
            "filtering them out of the ocean is nearly impossible. Researchers caution "
            "that the full effects on health are not yet clear, and they warn against "
            "easy conclusions. What is clear is that the cheapest fix is also the "
            "simplest: keeping plastic out of the environment in the first place, before "
            "it can shatter into pieces no net can catch."),
        "main_idea": (
            "Which choice best states the central idea of the passage?",
            ["Plastic breaks into tiny, widespread particles that are hard to remove, making prevention the best response.",
             "Microplastics are easy to filter from the ocean.",
             "Scientists have proven microplastics are harmless.",
             "Plastic disappears completely when exposed to sunlight."],
            0,
            ["Correct. The passage describes the spread and persistence of microplastics and favors prevention.",
             "The passage says filtering is nearly impossible.",
             "It says health effects are not yet clear.",
             "It says plastic fragments rather than vanishes."],
            "The passage links persistence and spread to a prevention-first conclusion."),
        "inference": (
            "The passage most strongly implies that, regarding health effects, scientists are",
            ["cautious because the evidence is still incomplete",
             "certain that there is no risk",
             "certain that the risk is severe",
             "uninterested in the question"],
            0,
            ["Correct. They 'caution' that effects are 'not yet clear.'",
             "They do not claim there is no risk.",
             "They warn against easy conclusions, severe or not.",
             "Their cautions show interest, not indifference."],
            "The hedged language signals careful uncertainty."),
        "structure": (
            "The final sentence functions mainly to",
            ["present the author's recommended response",
             "introduce a new scientific study",
             "define the word microplastic",
             "describe the history of plastic manufacturing"],
            0,
            ["Correct. It offers prevention as the best fix.",
             "No new study is introduced there.",
             "The term is used earlier, not defined at the end.",
             "Manufacturing history is not discussed."],
            "The closing sentence delivers the recommendation."),
        "wic": (
            "As used in the passage, the word “shatter” most nearly means",
            ["break apart", "shine brightly", "freeze solid", "expand"],
            0,
            ["Correct. Plastic breaks apart into tiny pieces.",
             "No shining is meant.",
             "Freezing is unrelated.",
             "It breaks down, not expands."],
            "Here 'shatter into pieces' means to break apart."),
        "evidence": (
            "Which detail best supports the claim that microplastics are widespread?",
            ["They have turned up in river water, Arctic ice, and the bodies of fish and birds.",
             "The cheapest fix is prevention.",
             "Health effects are not yet clear.",
             "Plastic breaks down under sunlight and waves."],
            0,
            ["Correct. The list of far-flung locations directly shows how widespread they are.",
             "The 'fix' detail concerns response, not spread.",
             "Uncertain health effects do not address spread.",
             "Breakdown explains origin, not the geographic reach."],
            "Their spread is supported by the list of places they appear."),
    },
    {
        "id": "alexandria", "title": "A House for Every Book",
        "text": (
            "The ancient library at Alexandria aimed at something audacious: to gather a "
            "copy of every book in the world. Ships docking at the harbor were searched, "
            "and any scrolls aboard were copied; sometimes the library kept the original "
            "and returned the copy. Scholars from distant lands came to read, argue, and "
            "write, and the collection may have held hundreds of thousands of scrolls. We "
            "know less than we would like about how the library declined, and popular "
            "stories of a single great fire oversimplify a slow loss across centuries. "
            "Still, the idea behind it endured. The dream of one place that holds all "
            "knowledge has reappeared, in new forms, ever since."),
        "main_idea": (
            "Which choice best states the central idea of the passage?",
            ["The Library of Alexandria pursued a sweeping goal of universal knowledge whose ideal outlived it.",
             "The library was destroyed in a single, well-documented fire.",
             "Only local scholars were allowed to use the library.",
             "The library refused to copy any scrolls."],
            0,
            ["Correct. The passage stresses the ambition of universal collection and the lasting power of that idea.",
             "The passage says the single-fire story oversimplifies a slow decline.",
             "Scholars came from distant lands.",
             "The library actively copied scrolls."],
            "The passage's emphasis is the ambitious ideal and its endurance, not a single dramatic end."),
        "inference": (
            "It can reasonably be inferred that the library obtained many of its scrolls by",
            ["copying texts that arrived by ship",
             "purchasing them only from local sellers",
             "forbidding visitors from bringing books",
             "writing every scroll from memory"],
            0,
            ["Correct. Scrolls aboard docking ships were searched and copied.",
             "The passage describes copying ships' scrolls, not only local purchases.",
             "Scholars were welcomed, not forbidden.",
             "Copying, not memory, is described."],
            "The ship-copying practice explains how the collection grew."),
        "structure": (
            "The author mentions the 'single great fire' story primarily to",
            ["correct an oversimplified popular belief",
             "prove the exact date of the library's end",
             "argue that the library never existed",
             "list the books the library owned"],
            0,
            ["Correct. The passage says that story oversimplifies a slow loss.",
             "It admits we lack precise knowledge of the decline.",
             "The passage treats the library as real.",
             "No book list is given."],
            "The fire reference serves to debunk an oversimplification."),
        "wic": (
            "As used in the passage, the word “audacious” most nearly means",
            ["boldly ambitious", "carelessly rushed", "quietly modest", "openly dishonest"],
            0,
            ["Correct. Gathering every book is a boldly ambitious goal.",
             "Nothing suggests carelessness.",
             "The aim is the opposite of modest.",
             "No dishonesty is implied."],
            "An 'audacious' aim is a boldly ambitious one."),
        "evidence": (
            "Which detail best supports the claim that the library's decline is poorly understood?",
            ["We know less than we would like about how the library declined.",
             "Ships' scrolls were searched and copied.",
             "Scholars came from distant lands.",
             "The collection may have held hundreds of thousands of scrolls."],
            0,
            ["Correct. This statement directly expresses limited knowledge of the decline.",
             "Copying scrolls concerns growth, not decline.",
             "Visiting scholars do not address the decline.",
             "Collection size does not address the decline."],
            "The uncertainty claim is stated directly in that sentence."),
    },
    {
        "id": "fog", "title": "Catching Water From Air",
        "text": (
            "In a few dry coastal regions, drinking water can be harvested from fog. Tall "
            "mesh nets are strung across hillsides where moist air rolls in from the sea. "
            "As the fog drifts through, droplets cling to the mesh, merge, and trickle "
            "down into troughs and storage tanks. A single large net can collect many "
            "liters on a good day, enough to supplement a village's supply. The method is "
            "not a cure-all: it works only where fog is frequent and winds are steady, and "
            "the nets need upkeep. Yet in the right place, it turns a passing cloud into a "
            "dependable resource, using little more than gravity and patience."),
        "main_idea": (
            "Which choice best states the central idea of the passage?",
            ["Fog nets can supply useful water in suitable coastal areas, within real limits.",
             "Fog nets can replace all other water sources everywhere.",
             "Fog harvesting requires complex machinery and electricity.",
             "Fog never contains enough moisture to collect."],
            0,
            ["Correct. The passage presents fog harvesting as useful where conditions fit, while noting limits.",
             "The passage calls it a supplement, not a universal replacement.",
             "It relies on gravity and simple mesh, not complex machinery.",
             "The passage says nets can collect many liters."],
            "The balanced claim is that fog nets work well in the right setting but are not a cure-all."),
        "inference": (
            "It can reasonably be inferred that fog harvesting is most practical in places that have",
            ["frequent fog and steady winds",
             "heavy year-round rainfall",
             "no wind at all",
             "very cold winters"],
            0,
            ["Correct. The passage says it works only where fog is frequent and winds steady.",
             "Such places would not need fog harvesting as much.",
             "Steady winds are required, so 'no wind' is wrong.",
             "Cold winters are not mentioned as a requirement."],
            "Suitability depends on frequent fog and steady wind."),
        "structure": (
            "The sentence beginning 'The method is not a cure-all' mainly serves to",
            ["acknowledge the limitations of the technique",
             "introduce a different technology",
             "summarize the village's history",
             "explain how mesh is manufactured"],
            0,
            ["Correct. It lays out the conditions and upkeep that limit the method.",
             "No new technology is introduced.",
             "No village history is summarized.",
             "Mesh manufacturing is not explained."],
            "The sentence concedes the method's limits."),
        "wic": (
            "As used in the passage, the word “cling” most nearly means",
            ["stick", "shout", "hurry", "shrink"],
            0,
            ["Correct. Droplets stick to the mesh.",
             "No shouting is meant.",
             "No hurrying is meant.",
             "Shrinking is not the sense."],
            "Droplets that 'cling' stick to the surface."),
        "evidence": (
            "Which detail best supports the claim that fog harvesting can meaningfully add to a water supply?",
            ["A single large net can collect many liters on a good day.",
             "The nets need upkeep.",
             "It works only where fog is frequent.",
             "Moist air rolls in from the sea."],
            0,
            ["Correct. The volume collected shows a meaningful contribution.",
             "Upkeep is a limitation, not a benefit.",
             "Frequency is a condition, not the yield.",
             "Incoming moist air explains the source, not the amount collected."],
            "The 'many liters' figure supports the usefulness claim."),
    },
    {
        "id": "mapmaker", "title": "The Edge of the Map",
        "text": (
            "Old maps are full of guesses. Where knowledge ran out, mapmakers filled the "
            "blank spaces with mountains they had never seen and coastlines that bent the "
            "wrong way. Some added sea monsters, less from belief than from a need to "
            "decorate the unknown. As explorers returned with measurements, the guesses "
            "were slowly corrected, and the monsters swam off the page. But a finished, "
            "accurate map can hide how hard it was to make. Every clean line was once a "
            "question, settled only by someone willing to sail past the edge of what was "
            "known and come back with an answer."),
        "main_idea": (
            "Which choice best states the central idea of the passage?",
            ["Accurate maps were achieved gradually, replacing guesses with hard-won measurements.",
             "Old mapmakers genuinely believed in sea monsters.",
             "Maps have never contained any errors.",
             "Explorers preferred inaccurate maps."],
            0,
            ["Correct. The passage traces the replacement of guesses by measurements and honors the effort behind it.",
             "The passage says monsters were decoration 'less from belief.'",
             "The passage describes early errors.",
             "Explorers corrected maps; they did not prefer errors."],
            "The passage's point is the slow, effortful move from guesswork to accuracy."),
        "inference": (
            "It can reasonably be inferred that the 'clean line' on a finished map represents",
            ["a question that was eventually answered through exploration",
             "a deliberate decoration like a sea monster",
             "a region that remains entirely unknown",
             "a mistake no one ever corrected"],
            0,
            ["Correct. The passage says every clean line 'was once a question,' settled by explorers.",
             "Clean lines replaced decorations, not added them.",
             "Clean lines mark known, corrected regions.",
             "The line marks a settled answer, not an uncorrected mistake."],
            "A clean line stands for a once-open question now resolved."),
        "structure": (
            "The passage develops its main point primarily by",
            ["contrasting early guesswork with later, corrected knowledge",
             "listing the names of famous explorers",
             "giving directions for drawing a map",
             "comparing two modern map apps"],
            0,
            ["Correct. It sets blank-space guesses against corrections from exploration.",
             "No explorers are named.",
             "No drawing directions are given.",
             "No modern apps are compared."],
            "The structure contrasts early guesses with later corrections."),
        "wic": (
            "As used in the passage, the word “settled” most nearly means",
            ["resolved", "calmed down", "moved to live somewhere", "sank to the bottom"],
            0,
            ["Correct. The question was resolved by an answer.",
             "No calming is meant.",
             "No relocation is meant.",
             "No sinking is meant."],
            "A question that is 'settled' is resolved."),
        "evidence": (
            "Which detail best supports the claim that maps improved as exploration advanced?",
            ["As explorers returned with measurements, the guesses were slowly corrected.",
             "Some maps added sea monsters as decoration.",
             "A finished map can hide how hard it was to make.",
             "Mapmakers filled blank spaces with imagined mountains."],
            0,
            ["Correct. Corrections following explorers' measurements show improvement over time.",
             "Decorative monsters do not show improvement.",
             "Hidden difficulty is a reflection, not evidence of improvement.",
             "Imagined mountains describe the early errors, not the improvement."],
            "Improvement is supported by corrections from returning explorers."),
    },
    {
        "id": "honeybee", "title": "Dances in the Dark",
        "text": (
            "A foraging honeybee that finds a rich patch of flowers cannot simply tell the "
            "hive where to go. Instead, it dances. On the vertical comb, in darkness, the "
            "bee runs a straight line while waggling its body, then loops back to repeat "
            "the move. The angle of that straight run, measured against the pull of "
            "gravity, encodes the direction of the flowers relative to the sun. The length "
            "of the run signals distance. Watching bees crowd around and follow, "
            "researchers realized they were seeing a kind of symbolic language, one that "
            "passes precise information without sight, sound, or a single spoken word."),
        "main_idea": (
            "Which choice best states the central idea of the passage?",
            ["The honeybee's waggle dance is a symbolic code that communicates a food source's direction and distance.",
             "Honeybees can speak to one another in sounds.",
             "Honeybees find flowers only by luck.",
             "The waggle dance has no consistent meaning."],
            0,
            ["Correct. The passage explains how the dance encodes direction and distance.",
             "The passage stresses communication 'without sound.'",
             "The dance communicates location, not luck.",
             "The dance reliably encodes specific information."],
            "The passage frames the waggle dance as a precise symbolic language."),
        "inference": (
            "It can reasonably be inferred that the angle of the waggle run is meaningful because it",
            ["relates the direction of food to the position of the sun",
             "shows the color of the flowers",
             "indicates the temperature of the hive",
             "measures the age of the dancing bee"],
            0,
            ["Correct. The angle against gravity encodes direction relative to the sun.",
             "Color is not encoded by the dance.",
             "Temperature is not mentioned.",
             "The bee's age is irrelevant to the dance."],
            "The angle's meaning comes from its relation to the sun's direction."),
        "structure": (
            "The passage is organized mainly by",
            ["describing a behavior and then explaining what it communicates",
             "comparing honeybees with wasps",
             "listing the parts of a flower",
             "arguing that bees should be studied less"],
            0,
            ["Correct. It first describes the dance, then decodes its meaning.",
             "No wasp comparison appears.",
             "Flower anatomy is not listed.",
             "The passage does not argue against study."],
            "The structure moves from behavior to interpretation."),
        "wic": (
            "As used in the passage, the word “encodes” most nearly means",
            ["represents as information", "locks with a key", "hides forever", "translates aloud"],
            0,
            ["Correct. The angle represents directional information.",
             "No literal locking occurs.",
             "The information is conveyed, not hidden forever.",
             "Nothing is translated aloud."],
            "To 'encode' here is to represent something as information."),
        "evidence": (
            "Which detail best supports the claim that the dance conveys distance?",
            ["The length of the run signals distance.",
             "The bee dances on a vertical comb in darkness.",
             "Bees crowd around and follow the dancer.",
             "The dance uses no sound."],
            0,
            ["Correct. Run length signaling distance directly supports the distance claim.",
             "The setting does not address distance.",
             "Followers show interest, not the distance code.",
             "Absence of sound concerns the medium, not distance."],
            "Distance is supported by the 'length of the run' detail."),
    },
    {
        "id": "glass", "title": "The Endless Material",
        "text": (
            "Glass has a quiet superpower: it can be melted down and remade again and "
            "again without losing quality. A bottle recycled today can become a bottle "
            "next month, then another after that, in a loop that, in principle, never "
            "wears out. Compared with this ideal, reality lags. Much glass still ends up "
            "in landfills because collection is uneven and because mixing colors lowers "
            "the value of the recycled material. Sorting by color and keeping glass out of "
            "general trash would let more of it re-enter the loop. The material is willing; "
            "it is our systems, the author suggests, that need redesigning."),
        "main_idea": (
            "Which choice best states the central idea of the passage?",
            ["Glass is endlessly recyclable in principle, but flawed systems keep much of it from being reused.",
             "Glass loses quality each time it is recycled.",
             "Glass can never be recycled at all.",
             "Color sorting makes recycling impossible."],
            0,
            ["Correct. The passage contrasts glass's ideal recyclability with system failures.",
             "The passage says glass keeps its quality when remade.",
             "It says glass can be remade again and again.",
             "Color sorting is offered as a solution, not an obstacle to recycling."],
            "The passage's point is the gap between glass's ideal recyclability and imperfect systems."),
        "inference": (
            "It can reasonably be inferred that mixing glass colors during recycling",
            ["reduces the usefulness of the recycled material",
             "improves the strength of new bottles",
             "is required by recycling rules",
             "has no effect on recycling"],
            0,
            ["Correct. The passage says mixing colors lowers the value of recycled glass.",
             "Mixing lowers value; it does not improve strength.",
             "Sorting is recommended, not color mixing.",
             "Mixing clearly has a negative effect."],
            "Mixed colors lower the recycled material's value, the passage states."),
        "structure": (
            "The author contrasts 'this ideal' with 'reality' mainly to",
            ["highlight the gap between what is possible and what happens",
             "argue that glass should not be recycled",
             "describe how glass is manufactured",
             "compare glass with plastic in detail"],
            0,
            ["Correct. The contrast spotlights the gap the author wants fixed.",
             "The author supports recycling.",
             "Manufacturing is not described.",
             "Plastic is not compared in detail."],
            "The ideal-versus-reality contrast frames the central problem."),
        "wic": (
            "As used in the passage, the word “lags” most nearly means",
            ["falls short", "ties tightly", "runs ahead", "rests quietly"],
            0,
            ["Correct. Reality falls short of the ideal.",
             "No tying is meant.",
             "It falls behind, not ahead.",
             "Resting is not the sense."],
            "Here 'lags' means falls short of or behind."),
        "evidence": (
            "Which detail best supports the claim that current systems limit glass recycling?",
            ["Much glass ends up in landfills because collection is uneven.",
             "A bottle can become a bottle next month.",
             "Glass can be melted down without losing quality.",
             "The material is willing."],
            0,
            ["Correct. Uneven collection sending glass to landfills shows a system limitation.",
             "This describes the ideal, not the limit.",
             "Quality retention is a property of glass, not a system failure.",
             "'The material is willing' is figurative, not specific evidence."],
            "System limits are supported by the uneven-collection detail."),
    },
    {
        "id": "lighthouse", "title": "Keeping the Light",
        "text": (
            "For centuries, a lighthouse meant a keeper. Someone had to climb the tower "
            "each night, trim the wick, polish the lens, and wind the clockwork that "
            "turned the light. Storms made the work dangerous, and isolation made it "
            "lonely, but ships depended on that faithful beam. In the twentieth century, "
            "automation arrived. Electric lamps, timers, and remote sensors took over the "
            "tasks one by one, and keepers were gradually withdrawn. The lights still "
            "shine, more reliably than ever, yet something human slipped away with the "
            "last keeper. The machines kept the promise of the light; they could not keep "
            "its company."),
        "main_idea": (
            "Which choice best states the central idea of the passage?",
            ["Automation made lighthouses more reliable but ended the human role of the keeper.",
             "Lighthouses stopped working after automation.",
             "Lighthouse keepers were never necessary.",
             "Modern lighthouses still require nightly keepers."],
            0,
            ["Correct. The passage contrasts improved reliability with the loss of the human keeper.",
             "The lights 'still shine,' more reliably than before.",
             "Keepers performed essential tasks for centuries.",
             "Automation withdrew the keepers."],
            "The passage balances technical gain against a human loss."),
        "inference": (
            "It can reasonably be inferred that, before automation, a lighthouse's reliability depended on",
            ["the constant labor of a human keeper",
             "the absence of any storms",
             "electric timers and sensors",
             "the height of the tower alone"],
            0,
            ["Correct. Keepers performed the nightly tasks that kept the light burning.",
             "Storms occurred and made the work dangerous.",
             "Timers and sensors came later, with automation.",
             "Height alone did not keep the light lit."],
            "Reliability rested on the keeper's constant labor."),
        "structure": (
            "The passage is organized mainly as a shift from",
            ["a human-run past to an automated present",
             "a list of lighthouse locations",
             "a debate between two keepers",
             "instructions for building a tower"],
            0,
            ["Correct. It moves from the era of keepers to the era of automation.",
             "No locations are listed.",
             "There is no debate between characters.",
             "No building instructions appear."],
            "The structure contrasts a manual past with an automated present."),
        "wic": (
            "As used in the passage, the word “faithful” most nearly means",
            ["dependable", "religious", "exactly accurate", "full of faith in others"],
            0,
            ["Correct. The beam was dependable for ships.",
             "No religious sense is intended.",
             "It is not about precise copying.",
             "The beam does not have faith."],
            "A 'faithful beam' is a dependable one."),
        "evidence": (
            "Which detail best supports the claim that automation improved reliability?",
            ["The lights still shine, more reliably than ever.",
             "Storms made the work dangerous.",
             "Keepers were gradually withdrawn.",
             "Isolation made the work lonely."],
            0,
            ["Correct. 'More reliably than ever' directly supports improved reliability.",
             "Dangerous storms concern the old hardship, not reliability gains.",
             "Withdrawal of keepers is the human cost, not the reliability claim.",
             "Loneliness describes the old role, not reliability."],
            "Improved reliability is stated directly in that detail."),
    },
    {
        "id": "seedbank", "title": "A Vault for Seeds",
        "text": (
            "Deep inside a frozen mountain, a vault holds something more valuable than "
            "gold: seeds. Hundreds of thousands of varieties of crops, gathered from "
            "around the world, rest in sealed packets at temperatures far below freezing. "
            "The cold slows the seeds' aging to a crawl, so that even after decades they "
            "can still sprout. The vault is a backup. If a war, flood, or disease wipes "
            "out a crop somewhere, a sample can be withdrawn and grown again. Its keepers "
            "hope it will rarely be needed, the way one hopes never to use a fire "
            "extinguisher. Its value lies precisely in being ready and almost never used."),
        "main_idea": (
            "Which choice best states the central idea of the passage?",
            ["A frozen seed vault preserves crop diversity as a backup against future losses.",
             "The seed vault is opened and used every day.",
             "Frozen seeds lose the ability to sprout within a year.",
             "The vault stores gold rather than seeds."],
            0,
            ["Correct. The passage explains the vault as a rarely used backup that protects crop variety.",
             "The keepers hope it is rarely needed.",
             "The cold lets seeds sprout even after decades.",
             "It values seeds 'more than gold,' figuratively."],
            "The passage frames the vault as a safeguard for crop diversity."),
        "inference": (
            "The comparison to a fire extinguisher mainly suggests that the vault is",
            ["valuable because it is ready even if rarely used",
             "dangerous to keep nearby",
             "used constantly throughout the year",
             "useful only for putting out fires"],
            0,
            ["Correct. Like an extinguisher, its worth lies in readiness for a rare emergency.",
             "No danger is implied.",
             "The passage hopes it is rarely needed.",
             "The analogy is about readiness, not literal firefighting."],
            "The analogy stresses preparedness for an uncommon emergency."),
        "structure": (
            "The passage develops its main idea primarily by",
            ["explaining the vault's purpose and how its cold preserves seeds",
             "listing the countries that built it",
             "comparing two rival seed vaults",
             "giving recipes that use the stored crops"],
            0,
            ["Correct. It describes the vault's backup purpose and the role of cold.",
             "No countries are listed.",
             "No rival vault is compared.",
             "No recipes appear."],
            "The structure explains purpose and preserving mechanism."),
        "wic": (
            "As used in the passage, the word “crawl” most nearly means",
            ["a very slow pace", "a swimming stroke", "an act of begging", "a baby's movement"],
            0,
            ["Correct. Aging slows to a very slow pace.",
             "The swimming sense does not fit.",
             "No begging is meant.",
             "The figurative 'slow pace' sense fits, not a literal baby."],
            "Slowing 'to a crawl' means to a very slow pace."),
        "evidence": (
            "Which detail best supports the claim that the cold preserves the seeds' ability to grow?",
            ["Even after decades, the seeds can still sprout.",
             "The vault is built inside a frozen mountain.",
             "The seeds come from around the world.",
             "The vault is a backup."],
            0,
            ["Correct. Sprouting after decades shows preservation of viability.",
             "The location alone does not show preserved viability.",
             "The seeds' origins do not address viability.",
             "Calling it a backup states purpose, not preservation."],
            "Preserved viability is shown by sprouting after decades."),
    },
]


# Paired passages for cross-text connections. Each: two short texts that share a
# topic but differ in stance, plus two cross-text questions.
PAIRED = [
    {
        "id": "homework",
        "title_a": "Text 1", "title_b": "Text 2",
        "text_a": ("Assigning homework in the early grades teaches children "
                   "responsibility and reinforces the day's lessons. A short, regular "
                   "task helps young students build the habit of independent work long "
                   "before the stakes are high."),
        "text_b": ("For young children, nightly homework offers little measurable "
                   "benefit and can sour their attitude toward school. Time spent on "
                   "worksheets, the author argues, would be better spent reading for "
                   "pleasure or playing outside."),
        "questions": [
            ("Based on the two texts, how would the author of Text 2 most likely respond to the claim in Text 1 that homework 'reinforces the day's lessons'?",
             ["By arguing that the benefit is small and outweighed by drawbacks for young children.",
              "By agreeing that homework is essential in the early grades.",
              "By insisting that children should have more worksheets, not fewer.",
              "By claiming that homework has no effect on responsibility ever, at any age."],
             0,
             ["Correct. Text 2 says the benefit is little and the costs (souring attitudes) are real.",
              "Text 2 disagrees that homework is essential for the young.",
              "Text 2 favors reading and play over worksheets.",
              "Text 2 addresses early grades, not 'any age,' so this overstates its claim."],
             "Text 2 would counter that the reinforcing benefit is minor and outweighed for young children."),
            ("Which choice best describes the relationship between the two texts?",
             ["They reach opposing conclusions about early-grade homework.",
              "They fully agree on the value of early-grade homework.",
              "Text 2 provides evidence that supports Text 1's conclusion.",
              "Both texts argue that homework should be increased."],
             0,
             ["Correct. Text 1 favors early homework; Text 2 opposes it.",
              "They disagree rather than agree.",
              "Text 2 undercuts, not supports, Text 1.",
              "Text 2 argues for less, not more."],
             "The texts take opposing positions on the same question."),
        ],
    },
    {
        "id": "zoos",
        "text_a": ("Modern zoos fund conservation and let millions of people encounter "
                   "animals they would never see in the wild, building public support "
                   "for protecting habitats. That connection, supporters say, is hard to "
                   "create any other way."),
        "text_b": ("Even well-run zoos confine animals to spaces far smaller than their "
                   "natural ranges. The author contends that documentaries and protected "
                   "reserves can inspire the public without keeping individual animals in "
                   "enclosures."),
        "questions": [
            ("Based on the texts, the author of Text 1 and the author of Text 2 would most likely disagree about whether",
             ["zoos are the best way to build public support for conservation",
              "habitat protection is desirable",
              "animals can be seen in documentaries",
              "zoos contain animals"],
             0,
             ["Correct. Text 1 calls the zoo connection hard to replace; Text 2 says reserves and films can do it.",
              "Both value habitat protection.",
              "Both accept documentaries exist; that is not the dispute.",
              "Both agree zoos contain animals."],
             "Their disagreement is whether zoos are the best route to public support."),
            ("How does Text 2 respond to a central benefit claimed in Text 1?",
             ["It offers alternatives that, it claims, achieve the benefit without confinement.",
              "It denies that the public cares about animals.",
              "It agrees that zoos are the only option.",
              "It argues zoos should hold even more animals."],
             0,
             ["Correct. Text 2 proposes documentaries and reserves as substitutes.",
              "Text 2 does not deny public interest.",
              "Text 2 rejects the 'only option' view.",
              "Text 2 opposes confinement."],
             "Text 2 counters by proposing confinement-free alternatives."),
        ],
    },
    {
        "id": "screens",
        "text_a": ("Reading on screens lets students carry an entire library, search text "
                   "instantly, and adjust font size for comfort. For many learners, the "
                   "author notes, these tools make reading more accessible, not less."),
        "text_b": ("Studies suggest readers often comprehend and remember more from print "
                   "than from screens, perhaps because paper invites slower, more focused "
                   "attention. The author urges keeping print central in classrooms."),
        "questions": [
            ("Based on the texts, the two authors would most likely disagree about whether",
             ["screen reading is as good as print for learning",
              "students should be allowed to read at all",
              "libraries contain books",
              "font size can be changed on screens"],
             0,
             ["Correct. Text 1 praises screens; Text 2 favors print for comprehension.",
              "Both assume students read.",
              "Both accept libraries hold books.",
              "Both would accept that screens adjust font size."],
             "The dispute is whether screens match print for learning."),
            ("The author of Text 2 would most likely respond to Text 1's emphasis on convenience by",
             ["acknowledging the convenience but prioritizing comprehension",
              "denying that screens can store many texts",
              "agreeing that print should be abandoned",
              "claiming font size cannot be adjusted"],
             0,
             ["Correct. Text 2 values comprehension over the conveniences Text 1 cites.",
              "Text 2 does not dispute storage capacity.",
              "Text 2 wants to keep print central.",
              "Text 2 does not make that claim."],
             "Text 2 would grant the convenience yet stress comprehension."),
        ],
    },
    {
        "id": "remote",
        "text_a": ("Remote work lets employees skip long commutes, focus without office "
                   "noise, and live where they choose. The author points to surveys in "
                   "which workers report higher satisfaction and steady productivity."),
        "text_b": ("Working from home, the author warns, can blur the line between job and "
                   "rest and weaken the casual conversations that spark new ideas. Some "
                   "collaboration, this text argues, happens best in person."),
        "questions": [
            ("Based on the texts, how do the authors differ in their view of remote work?",
             ["Text 1 emphasizes its benefits, while Text 2 emphasizes its drawbacks.",
              "Both conclude remote work should be banned.",
              "Both conclude remote work has no downsides.",
              "Text 1 opposes it, while Text 2 supports it."],
             0,
             ["Correct. Text 1 highlights benefits; Text 2 highlights drawbacks.",
              "Neither calls for a ban.",
              "Text 2 names downsides.",
              "Their stances are reversed in this option."],
             "Text 1 stresses benefits; Text 2 stresses drawbacks."),
            ("The author of Text 2 would most likely point to which idea as a weakness of the view in Text 1?",
             ["Casual in-person conversations that spark ideas may be lost.",
              "Commutes are too short to matter.",
              "Workers cannot choose where to live.",
              "Productivity is impossible at home."],
             0,
             ["Correct. Text 2 warns that remote work weakens idea-sparking conversations.",
              "Text 1 stresses skipping long commutes, not short ones.",
              "Text 1 says workers can choose where to live.",
              "Text 2 does not claim productivity is impossible, only that some collaboration suffers."],
             "Text 2's key concern is the loss of spontaneous collaboration."),
        ],
    },
    {
        "id": "wolves",
        "text_a": ("Reintroducing wolves to a national park, the author argues, restored "
                   "balance: with deer no longer overgrazing, young trees returned, and "
                   "with them came birds and beavers. A single predator, the text says, "
                   "revived a whole landscape."),
        "text_b": ("Crediting wolves alone for the park's recovery oversimplifies a messy "
                   "story, this author cautions. Weather, other species, and human "
                   "management all shifted at once, making the wolves' exact role hard to "
                   "isolate."),
        "questions": [
            ("Based on the texts, the author of Text 2 would most likely characterize the claim in Text 1 as",
             ["overstated, because other factors also contributed",
              "completely correct in every detail",
              "proof that wolves had no effect",
              "evidence that deer were never overgrazing"],
             0,
             ["Correct. Text 2 says crediting wolves alone oversimplifies a multi-cause story.",
              "Text 2 questions, not endorses, the claim's completeness.",
              "Text 2 does not deny wolves had any effect.",
              "Text 2 does not dispute overgrazing."],
             "Text 2 sees Text 1's single-cause claim as overstated."),
            ("Which choice best describes how Text 2 relates to Text 1?",
             ["It complicates Text 1's explanation by adding other causes.",
              "It restates Text 1's explanation without change.",
              "It provides numerical proof for Text 1.",
              "It argues wolves should be removed."],
             0,
             ["Correct. Text 2 introduces additional factors that complicate the single-cause story.",
              "Text 2 adds nuance rather than restating.",
              "Text 2 offers caution, not numerical proof.",
              "Text 2 does not call for removing wolves."],
             "Text 2 complicates Text 1 by adding multiple causes."),
        ],
    },
    {
        "id": "cursive",
        "text_a": ("Teaching cursive, the author maintains, trains fine motor skills, "
                   "lets students read historical documents, and gives them a personal, "
                   "fluent hand. Dropping it, the text warns, cuts a link to the past."),
        "text_b": ("Class time is limited, and this author argues it is better spent on "
                   "typing and clear print, the writing students will actually use. "
                   "Cursive, the text suggests, has become a charming but optional skill."),
        "questions": [
            ("Based on the texts, the two authors most clearly disagree about whether",
             ["cursive deserves dedicated class time",
              "students should learn to write at all",
              "typing exists",
              "historical documents were ever written"],
             0,
             ["Correct. Text 1 defends teaching cursive; Text 2 would spend the time elsewhere.",
              "Both assume students write.",
              "Both accept typing exists.",
              "Both accept historical documents exist."],
             "The disagreement is whether cursive warrants class time."),
            ("How would the author of Text 2 most likely respond to Text 1's concern about 'a link to the past'?",
             ["By granting the value but arguing limited time is better used on practical writing.",
              "By denying that the past matters in any way.",
              "By agreeing cursive should be the main focus.",
              "By claiming students cannot learn to type."],
             0,
             ["Correct. Text 2 weighs the trade-off and prioritizes practical writing.",
              "Text 2 calls cursive 'charming,' not worthless.",
              "Text 2 would not center cursive.",
              "Text 2 favors teaching typing."],
             "Text 2 would acknowledge the value yet prioritize practical skills."),
        ],
    },
    {
        "id": "tourism",
        "text_a": ("Tourism brings jobs and money to small towns, the author observes, "
                   "funding restaurants, guides, and shops that might not otherwise "
                   "survive. Visitors, the text says, can keep a struggling community "
                   "alive."),
        "text_b": ("When crowds overwhelm a small place, this author argues, rents rise, "
                   "streets clog, and the very charm visitors came for begins to fade. "
                   "Growth without limits, the text warns, can hollow a town out."),
        "questions": [
            ("Based on the texts, the authors would most likely disagree about whether",
             ["tourism is, on balance, good for a small town",
              "tourists spend money",
              "small towns have streets",
              "restaurants employ workers"],
             0,
             ["Correct. Text 1 sees tourism as a lifeline; Text 2 warns it can hollow a town out.",
              "Both accept tourists spend money.",
              "Both accept towns have streets.",
              "Both accept restaurants employ people."],
             "Their dispute is the net effect of tourism on a town."),
            ("The author of Text 2 would most likely respond to Text 1's emphasis on economic benefit by",
             ["noting that unchecked growth can erode the town's appeal and affordability",
              "denying that tourism creates any jobs",
              "agreeing that more visitors are always better",
              "claiming small towns have no shops"],
             0,
             ["Correct. Text 2 warns of rising rents, crowding, and fading charm.",
              "Text 2 does not deny job creation.",
              "Text 2 warns against limitless growth.",
              "Text 2 does not claim towns lack shops."],
             "Text 2 counters with the costs of unlimited growth."),
        ],
    },
    {
        "id": "grades",
        "text_a": ("Letter grades give students clear targets and tell colleges and "
                   "employers, at a glance, how a student performed. That clarity, the "
                   "author argues, is hard to replace."),
        "text_b": ("Grades, this author counters, can push students to chase points "
                   "instead of understanding, and a single letter hides what a learner "
                   "can actually do. Detailed feedback, the text says, teaches more."),
        "questions": [
            ("Based on the texts, the two authors most clearly disagree about whether",
             ["letter grades are an effective way to represent learning",
              "students attend school",
              "colleges receive applications",
              "feedback can be written down"],
             0,
             ["Correct. Text 1 praises grades' clarity; Text 2 says they distort and hide learning.",
              "Both assume students attend school.",
              "Both accept colleges get applications.",
              "Both accept feedback can be written."],
             "The dispute is whether letter grades effectively represent learning."),
            ("Which choice best states how Text 2 challenges Text 1?",
             ["It argues that a single letter conceals what a student can really do.",
              "It agrees that grades capture understanding perfectly.",
              "It claims employers ignore all records.",
              "It says students should not receive feedback."],
             0,
             ["Correct. Text 2's key challenge is that a letter hides actual ability.",
              "Text 2 disputes that grades capture understanding.",
              "Text 2 does not make a claim about employers ignoring records.",
              "Text 2 favors detailed feedback."],
             "Text 2 challenges Text 1 by noting a letter conceals real ability."),
        ],
    },
]


def _reading_q(passage, skill, qtype, est):
    spec = passage[skill]
    prompt, options, ci, rats, expl = spec
    stim = {"type": "passage", "title": passage["title"], "text": passage["text"]}
    skill_tag = {"main_idea": "main-idea", "inference": "inference",
                 "structure": "structure", "wic": "vocabulary",
                 "evidence": "evidence"}[skill]
    sub = {"main_idea": "central_idea", "inference": "implied_meaning",
           "structure": "overall_structure", "wic": "vocabulary",
           "evidence": "textual_evidence"}[skill]
    return mc(prompt, options, ci, rats, subskill=sub, qtype=qtype,
              explanation=expl, tags=["reading", skill_tag], est=est, stimulus=stim)


def build_reading(skill: str):
    """Return one question body per passage for the given reading skill key."""
    qtype = "passage_reading"
    est = 80 if skill in ("evidence", "structure") else 70
    return [_reading_q(p, skill, qtype, est) for p in PASSAGES]


def build_cross_text():
    """Return all cross-text question bodies from paired passages."""
    items = []
    for pair in PAIRED:
        stim = {"type": "paired_passages", "title": "Paired passages",
                "text": pair["text_a"], "text_b": pair["text_b"]}
        for prompt, options, ci, rats, expl in pair["questions"]:
            items.append(mc(prompt, options, ci, rats,
                            subskill="compare_viewpoints", qtype="passage_reading",
                            explanation=expl, tags=["reading", "cross-text"],
                            est=90, stimulus=stim))
    return items
