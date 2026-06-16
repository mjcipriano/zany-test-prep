"""Original reading passages and their comprehension questions.

All prose here is original, written for this project. Each single passage yields
five questions (main idea, inference, text structure/purpose, words-in-context,
command of evidence). Paired passages yield cross-text questions.

Distractors are written to be full, plausible statements of length comparable to
the key, so the correct answer does not stand out by length. The builders shuffle
option order (seeded) so the correct choice is not always in the same position.

A question spec is (prompt, [opt0..opt3], correct_index, [rat0..rat3], explanation).
"""
from __future__ import annotations

import random

from .util import mc

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
            ["The octopus changes color through a muscular pigment system it cannot itself see.",
             "The octopus relies on its keen color vision to match its surroundings closely.",
             "The octopus changes color mainly to communicate with other nearby octopuses.",
             "The octopus shifts color slowly, building up a disguise over many minutes."],
            0,
            ["Correct. The passage centers on the surprising mechanism of color change in a colorblind animal.",
             "The passage says the octopus is colorblind, not keen-sighted.",
             "Communication between octopuses is never mentioned.",
             "The change happens in under a second, not over many minutes."],
            "The passage builds toward the paradox of an animal that produces colors it cannot perceive."),
        "inference": (
            "It can reasonably be inferred from the passage that the octopus's color change is",
            ["produced by muscles widening sacs of pigment beneath the skin",
             "triggered by the temperature of the surrounding seawater",
             "learned only gradually over the course of the animal's life",
             "perceptible to the octopus itself but not to other animals"],
            0,
            ["Correct. The passage states muscles widen the sacs to reveal color.",
             "Temperature is never mentioned as a cause.",
             "The change happens in under a second, not slowly over a lifetime.",
             "The octopus is colorblind, so it cannot perceive its own colors."],
            "The text directly ties color change to muscles pulling on pigment sacs."),
        "structure": (
            "Which choice best describes the overall structure of the passage?",
            ["It introduces a surprising trait, explains its mechanism, then notes a deeper puzzle.",
             "It compares two different species of octopus and weighs their abilities.",
             "It argues that octopuses are endangered and should be protected from fishing.",
             "It lists, in order, the steps a diver should follow to observe an octopus."],
            0,
            ["Correct. The passage moves from a striking fact to a mechanism to the colorblindness paradox.",
             "Only one animal is discussed, not two species.",
             "The passage makes no argument about protection.",
             "No how-to steps are given."],
            "The passage's purpose is to explain and then deepen a surprising fact, not to argue or instruct."),
        "wic": (
            "As used in the passage, the word “flush” most nearly means",
            ["become suffused with color", "rinse clean with water",
             "discard or empty out", "grow red with embarrassment"],
            0,
            ["Correct. The octopus's skin fills with red color.",
             "No rinsing is described.",
             "Nothing is being discarded.",
             "An octopus does not feel embarrassment; the sense here is about color."],
            "In context, to 'flush deep red' means to fill with color."),
        "evidence": (
            "Which detail best supports the idea that the octopus cannot perceive its own display?",
            ["the statement that the octopus is colorblind and cannot see the hues it makes",
             "the statement that the octopus has no bones and almost no color of its own",
             "the statement that its color can bloom or vanish in less than a second",
             "the statement that each sac of pigment is ringed by a band of muscle"],
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
            ["Gutenberg's reusable metal type made books far easier to reproduce and to spread.",
             "Handwritten books remained more beautiful and more valued than any printed book.",
             "The price of books dropped instantly once Gutenberg's printing press appeared.",
             "Scribes abandoned their work as soon as the first printing presses were built."],
            0,
            ["Correct. The passage emphasizes how reusable type transformed the reproduction and reach of books.",
             "Beauty of handwriting is not the passage's claim.",
             "The passage explicitly says costs did not fall overnight.",
             "It notes scholars still prized handwritten volumes, so scribes did not vanish at once."],
            "The passage frames the press as a turning point in how widely texts could circulate."),
        "inference": (
            "The passage most strongly suggests that, before Gutenberg, identical copies of a text were",
            ["rare, because copying by hand was slow and introduced small variations",
             "common, since nearly every European town had its own busy copyists",
             "produced even faster by hand than printed copies later would be",
             "widely dismissed as worthless by the scholars of the period"],
            0,
            ["Correct. Hand-copying was slow and the passage stresses the novelty of identical printed copies.",
             "The passage implies the opposite of commonness.",
             "Hand-copying took a year, far slower than printing.",
             "Scholars are said to prize handwritten books, not scorn them."],
            "The contrast the passage draws implies hand-copied texts were neither fast nor uniform."),
        "structure": (
            "The author notes that 'the cost of a book did not fall overnight' primarily to",
            ["qualify the idea of instant change before describing the long-term effect",
             "argue that the printing press was, on the whole, a costly failure",
             "suggest that the scribes of the time were dishonest about their prices",
             "begin a step-by-step guide to operating an early printing press"],
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
            ["the statement that within fifty years presses had produced millions of books",
             "the statement that a single scribe could spend a year copying one book",
             "the statement that many scholars still prized their handwritten volumes",
             "the statement that Gutenberg cast each individual letter out of metal"],
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
            ["The tardigrade endures extreme conditions by drying into a protected, revivable state.",
             "The tardigrade is the smallest animal that scientists have ever discovered on Earth.",
             "Scientists have now fully explained exactly how the tardigrade protects its cells.",
             "The tardigrade can survive only in the vacuum and radiation of outer space."],
            0,
            ["Correct. The passage centers on how the tardigrade endures extremes by drying out.",
             "The passage compares its size to salt but never calls it the smallest animal.",
             "The text says scientists are 'still untangling' the mechanism.",
             "Space is one extreme it can survive, not its home."],
            "The passage's focus is the dehydration survival strategy and its partial explanation."),
        "inference": (
            "It can reasonably be inferred that the 'tun' state is best described as a form of",
            ["suspended dormancy from which the animal can later revive",
             "rapid growth that lets the animal enlarge under stress",
             "permanent death that ends the animal's life for good",
             "social cooperation among many tardigrades at once"],
            0,
            ["Correct. The animal halts activity yet can revive, indicating dormancy.",
             "Drying into a husk is not growth.",
             "It can be revived, so it is not dead.",
             "No social behavior is described."],
            "Because the creature can be revived after years, the tun is a dormant, not lethal, state."),
        "structure": (
            "The passage is organized mainly by",
            ["introducing the animal, then its survival ability, then a proposed mechanism",
             "comparing the tardigrade in detail with a single named rival animal",
             "tracing the history of tardigrade research decade by decade in order",
             "presenting and defending an argument for funding human space travel"],
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
            "Which detail best supports the claim that the tardigrade can revive after a long delay?",
            ["the statement that years later a single drop of water can revive the creature",
             "the statement that the animal plods along on eight short, stubby legs",
             "the statement that the tardigrade is smaller than a single grain of salt",
             "the statement that it expels most of its water as it dries into a husk"],
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
            ["A fine instrument reveals the skill Nadia had built through her earlier struggle.",
             "Nadia decides to give up the violin entirely once the recital has ended.",
             "Battered school instruments are always better for learning than fine ones.",
             "Nadia's teacher refuses to let her borrow the fine loaner violin at all."],
            0,
            ["Correct. The closing lines tie the fine violin to the skill she had quietly built.",
             "She does not quit; she gains insight.",
             "The passage shows the loaner as finer than her battered school violin.",
             "The teacher hands her the loaner rather than refusing."],
            "The narrative resolves on the idea that her growth, not just the violin, produced the beautiful playing."),
        "inference": (
            "It can reasonably be inferred that Nadia almost refused the loaner because she",
            ["felt unworthy of playing such a fine and valuable instrument",
             "strongly disliked the pieces she was assigned for the recital",
             "actually preferred instruments whose tuning pegs kept slipping",
             "had never learned how to read the music set before her"],
            0,
            ["Correct. 'It felt wrong to play something so fine' signals a sense of unworthiness.",
             "Her feelings about the pieces are not the reason given.",
             "She struggled with slipping pegs; she did not prefer them.",
             "Nothing suggests she cannot read music."],
            "Her hesitation stems from feeling the instrument was too fine for her."),
        "structure": (
            "The passage is structured as",
            ["a moment of doubt that gradually gives way to a realization",
             "a numbered list of tips for choosing a good violin",
             "a back-and-forth debate between two rival musicians",
             "a chronological history of one town's orchestra"],
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
            ["the detail that notes she had fought for all year now arrived easily",
             "the detail that two of her school violin's pegs slipped every lesson",
             "the detail that she returned the borrowed violin to its case afterward",
             "the detail that she had nearly refused the instrument to begin with"],
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
            ["Sparrows learn local song dialects that vary by place and shift across generations.",
             "Every white-crowned sparrow sings exactly the same unchanging song everywhere.",
             "Sparrows are born already knowing the full song they will sing as adults.",
             "Human accents are largely caused by people imitating nearby birdsong."],
            0,
            ["Correct. The passage explains learned, place-based dialects that change over generations.",
             "The passage stresses variation, not sameness.",
             "Birds must learn the song; they are not born knowing it.",
             "The human-accent comparison is an analogy, not a cause."],
            "The passage's through-line is learned, drifting song dialects."),
        "inference": (
            "It can reasonably be inferred that a sparrow's ability to learn a full song depends on",
            ["hearing adult song during a brief window early in its life",
             "the particular color and pattern of the feathers on its crown",
             "the overall size of the meadow in which it happens to live",
             "the age of any sound recordings made nearby in past decades"],
            0,
            ["Correct. A bird that hears no song in that window sings only a thin tune.",
             "Crown color is not linked to learning.",
             "Meadow size is never mentioned as a factor.",
             "Old recordings illustrate drift, not a bird's learning ability."],
            "The passage ties full song to exposure during the early learning window."),
        "structure": (
            "The comparison to human accents primarily serves to",
            ["help readers understand how song dialects can drift over time",
             "prove that birds and human beings are in fact closely related",
             "argue that making recordings of birdsong should be banned",
             "list, in order, the stages of a single sparrow's life cycle"],
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
            ["the detail that a bird hearing no song early on sings only a thin, simplified tune",
             "the detail that the basic melody stays roughly the same across the regions",
             "the detail that a decades-old recording may sound subtly foreign today",
             "the detail that white-crowned sparrows make their homes in open meadows"],
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
            ["Sleep is an active process that supports memory and brain upkeep, in the right amount.",
             "Staying awake for longer stretches reliably improves a person's memory over time.",
             "The brain does essentially nothing of value during the hours a person sleeps.",
             "The more hours a person sleeps each night, the better that person performs."],
            0,
            ["Correct. The passage presents sleep as active and beneficial within an optimal range.",
             "The experiment shows the opposite of this claim.",
             "The passage argues the brain is busy during sleep.",
             "The passage explicitly rejects 'more is always better.'"],
            "The passage's balanced claim is that sleep actively helps the brain, but only in adequate amounts."),
        "inference": (
            "The passage suggests that the link between sleep and performance is",
            ["strongest at a moderate amount rather than at either extreme",
             "strongest when a person sleeps as little as they possibly can",
             "essentially unrelated to how well a person remembers things",
             "exactly the same for every person regardless of timing or amount"],
            0,
            ["Correct. The 'curve' detail implies a moderate optimum.",
             "Too little sleep is linked to poorer performance.",
             "The passage ties sleep to memory consolidation.",
             "It mentions 'the right times,' implying timing matters."],
            "The curve description implies a middle optimum, not an extreme."),
        "structure": (
            "The author includes the word-list experiment mainly to",
            ["provide concrete evidence that sleep helps the brain store memories",
             "argue that studying before a test is, on the whole, pointless",
             "describe a reliable method for falling asleep more quickly",
             "compare two unrelated regions of the human brain in detail"],
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
            ["the finding that students who slept after studying recalled more words than those who stayed awake",
             "the statement that waves of electrical activity sweep across the sleeping cortex",
             "the statement that sleep may also clear away molecular waste from the brain",
             "the statement that the sleep-performance relationship appears to follow a curve"],
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
            ["Volcanic ash builds fertile soil, drawing farmers despite the danger of eruptions.",
             "Volcanoes pose essentially no danger to the villages that sit beside them.",
             "Farming is effectively impossible anywhere within reach of a volcano.",
             "Potassium is the single mineral that crops need in order to grow well."],
            0,
            ["Correct. The passage explains the fertility-versus-danger trade-off that keeps farmers near volcanoes.",
             "The passage notes a real danger, so volcanoes are not harmless.",
             "The passage says many people do farm there.",
             "It names potassium and phosphorus, not a single required mineral."],
            "The passage balances the benefit of fertile soil against eruption risk."),
        "inference": (
            "It can reasonably be inferred that farmers near volcanoes",
            ["accept a known risk in exchange for unusually productive land",
             "have no idea that the nearby volcano could ever erupt at all",
             "manage to harvest crops only in the years without any eruption",
             "would actually rather farm poor soil than the rich volcanic soil"],
            0,
            ["Correct. The passage describes weighing the gift of soil against the danger.",
             "They 'weigh' the danger, so they are aware of it.",
             "No such yearly pattern is stated.",
             "They value the rich soil, not poor soil."],
            "The 'uneasy bargain' framing implies an accepted, known risk."),
        "structure": (
            "The phrase 'the bargain is uneasy' marks a shift from",
            ["describing a clear benefit to acknowledging a real danger",
             "telling a personal story to listing a set of instructions",
             "praising the region's farmers to sharply criticizing them",
             "discussing volcanic ash to discussing the distant oceans"],
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
            ["the statement that slopes near certain volcanoes are crowded with farms and villages",
             "the statement that volcanic ash is rich in minerals such as potassium and phosphorus",
             "the statement that the same mountain that feeds the fields can also threaten them",
             "the statement that the scattered ash takes years to break down into soil"],
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
            ["The bicycle evolved through gradual improvements into a popular means of free travel.",
             "The very first bicycle was an immediate and widely celebrated popular success.",
             "Early bicycles still depended on a horse in order to move from place to place.",
             "Working foot pedals were a built-in part of the very first bicycle design."],
            0,
            ["Correct. The passage traces stepwise improvements leading to the bicycle's popularity and freedom of movement.",
             "The first version was mocked and faded, not an immediate success.",
             "The passage says it needed no horse.",
             "The earliest version had no pedals."],
            "The passage's arc is incremental improvement culminating in widespread, independent travel."),
        "inference": (
            "It can reasonably be inferred that the bicycle's popularity in the 1890s depended on",
            ["earlier technical improvements such as pedals, a chain, and air-filled tires",
             "the complete disappearance of nearly all roads across the countryside",
             "a broad return to horse-drawn travel after a brief period of decline",
             "the original 1817 design being kept almost entirely unchanged"],
            0,
            ["Correct. The passage links each improvement to new riders before the craze.",
             "Roads did not disappear; rough roads were a problem.",
             "The bicycle's appeal was needing no horse.",
             "The design changed substantially from 1817."],
            "Popularity followed the accumulation of improvements."),
        "structure": (
            "The passage is organized mainly as",
            ["a chronological account of how one invention developed over time",
             "a side-by-side comparison of two competing rival inventors",
             "a set of numbered instructions for building a bicycle at home",
             "an argument warning readers against modern forms of transportation"],
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
            ["the statement that it offered cheap, independent travel needing no horse and no rails",
             "the statement that the earliest version was built in 1817 from a wooden frame",
             "the statement that people mocked the very earliest version of the machine",
             "the statement that rutted roads made the first version quite impractical"],
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
            ["Plastic breaks into tiny, far-spread particles that resist removal, so prevention is best.",
             "Microplastics can be filtered out of the open ocean cheaply and quite easily.",
             "Scientists have firmly proven that microplastics pose no danger to human health.",
             "Plastic disappears completely and harmlessly once sunlight has acted on it."],
            0,
            ["Correct. The passage describes the spread and persistence of microplastics and favors prevention.",
             "The passage says filtering is nearly impossible.",
             "It says health effects are not yet clear.",
             "It says plastic fragments rather than vanishes."],
            "The passage links persistence and spread to a prevention-first conclusion."),
        "inference": (
            "The passage most strongly implies that, regarding health effects, scientists are",
            ["cautious, because the available evidence is still incomplete",
             "certain that microplastics carry no health risk whatsoever",
             "certain that the health risk is already proven to be severe",
             "largely uninterested in studying the question at all"],
            0,
            ["Correct. They 'caution' that effects are 'not yet clear.'",
             "They do not claim there is no risk.",
             "They warn against easy conclusions, severe or not.",
             "Their cautions show interest, not indifference."],
            "The hedged language signals careful uncertainty."),
        "structure": (
            "The final sentence functions mainly to",
            ["present the author's recommended response to the problem",
             "introduce a brand-new scientific study and its findings",
             "define the term microplastic for the first time in the text",
             "describe the long history of how plastic is manufactured"],
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
            ["the statement that they have turned up in river water, Arctic ice, and the bodies of animals",
             "the statement that the cheapest fix is to keep plastic out of the environment",
             "the statement that the full health effects of the particles are not yet clear",
             "the statement that plastic breaks down under steady sunlight and waves"],
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
            ["The library pursued a sweeping goal of universal knowledge whose ideal outlived it.",
             "The library was destroyed in a single, well-documented, and sudden great fire.",
             "Only scholars who lived in the local city were ever allowed to use the library.",
             "The library, as a matter of policy, refused to copy any scroll brought to it."],
            0,
            ["Correct. The passage stresses the ambition of universal collection and the lasting power of that idea.",
             "The passage says the single-fire story oversimplifies a slow decline.",
             "Scholars came from distant lands.",
             "The library actively copied scrolls."],
            "The passage's emphasis is the ambitious ideal and its endurance, not a single dramatic end."),
        "inference": (
            "It can reasonably be inferred that the library obtained many of its scrolls by",
            ["copying texts that happened to arrive aboard ships at the harbor",
             "buying them only from a small number of local city sellers",
             "forbidding any visitor from bringing a book through its doors",
             "having scribes write out every single scroll purely from memory"],
            0,
            ["Correct. Scrolls aboard docking ships were searched and copied.",
             "The passage describes copying ships' scrolls, not only local purchases.",
             "Scholars were welcomed, not forbidden.",
             "Copying, not memory, is described."],
            "The ship-copying practice explains how the collection grew."),
        "structure": (
            "The author mentions the 'single great fire' story primarily to",
            ["correct a popular belief that oversimplifies what happened",
             "establish the exact date on which the library finally ended",
             "argue that the famous library never actually existed at all",
             "give a complete list of the books the library once owned"],
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
            ["the statement that we know less than we would like about how the library declined",
             "the statement that scrolls aboard docking ships were searched and then copied",
             "the statement that scholars came from distant lands to read, argue, and write",
             "the statement that the collection may have held hundreds of thousands of scrolls"],
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
            ["Fog nets can supply useful drinking water in suitable coastal areas, within real limits.",
             "Fog nets can completely replace every other source of water in any location.",
             "Harvesting water from fog demands complex machinery and a steady power supply.",
             "Fog almost never holds enough moisture to be worth trying to collect at all."],
            0,
            ["Correct. The passage presents fog harvesting as useful where conditions fit, while noting limits.",
             "The passage calls it a supplement, not a universal replacement.",
             "It relies on gravity and simple mesh, not complex machinery.",
             "The passage says nets can collect many liters."],
            "The balanced claim is that fog nets work well in the right setting but are not a cure-all."),
        "inference": (
            "It can reasonably be inferred that fog harvesting is most practical in places that have",
            ["frequent fog together with steady, reliable winds",
             "heavy rainfall spread evenly throughout the whole year",
             "no moving air or wind of any kind at any time",
             "long, very cold winters lasting much of the year"],
            0,
            ["Correct. The passage says it works only where fog is frequent and winds steady.",
             "Such places would not need fog harvesting as much.",
             "Steady winds are required, so 'no wind' is wrong.",
             "Cold winters are not mentioned as a requirement."],
            "Suitability depends on frequent fog and steady wind."),
        "structure": (
            "The sentence beginning 'The method is not a cure-all' mainly serves to",
            ["acknowledge the conditions and upkeep that limit the technique",
             "introduce an entirely different water-gathering technology",
             "summarize the long history of one particular village",
             "explain, step by step, how the mesh nets are manufactured"],
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
            ["the statement that a single large net can collect many liters on a good day",
             "the statement that the mesh nets require regular upkeep to keep working",
             "the statement that the method works only where fog happens to be frequent",
             "the statement that moist air rolls in toward the hillsides from the sea"],
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
             "Mapmakers of the past genuinely believed that sea monsters filled the oceans.",
             "Maps drawn in earlier centuries in fact contained no errors of any kind.",
             "Explorers of the period actually preferred to use inaccurate, guesswork maps."],
            0,
            ["Correct. The passage traces the replacement of guesses by measurements and honors the effort behind it.",
             "The passage says monsters were decoration 'less from belief.'",
             "The passage describes early errors.",
             "Explorers corrected maps; they did not prefer errors."],
            "The passage's point is the slow, effortful move from guesswork to accuracy."),
        "inference": (
            "It can reasonably be inferred that a 'clean line' on a finished map represents",
            ["a once-open question that exploration eventually answered",
             "a deliberate decoration much like a painted sea monster",
             "a region that, even now, remains completely unknown",
             "a mistake that no mapmaker ever got around to correcting"],
            0,
            ["Correct. The passage says every clean line 'was once a question,' settled by explorers.",
             "Clean lines replaced decorations, not added them.",
             "Clean lines mark known, corrected regions.",
             "The line marks a settled answer, not an uncorrected mistake."],
            "A clean line stands for a once-open question now resolved."),
        "structure": (
            "The passage develops its main point primarily by",
            ["contrasting early guesswork with the later, corrected knowledge",
             "listing the names of the era's most famous sea explorers",
             "giving the reader directions for drawing an accurate map",
             "comparing two competing modern digital mapping apps"],
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
            ["the statement that, as explorers returned with measurements, the guesses were slowly corrected",
             "the statement that some old maps added sea monsters as a form of decoration",
             "the statement that a finished, accurate map can hide how hard it was to make",
             "the statement that mapmakers filled blank spaces with mountains they imagined"],
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
            ["The honeybee's waggle dance is a symbolic code for a food source's direction and distance.",
             "Honeybees actually speak to one another using a range of distinct vocal sounds.",
             "Honeybees locate rich patches of flowers almost entirely by chance and luck.",
             "The honeybee's waggle dance carries no consistent or reliable meaning at all."],
            0,
            ["Correct. The passage explains how the dance encodes direction and distance.",
             "The passage stresses communication 'without sound.'",
             "The dance communicates location, not luck.",
             "The dance reliably encodes specific information."],
            "The passage frames the waggle dance as a precise symbolic language."),
        "inference": (
            "It can reasonably be inferred that the angle of the waggle run is meaningful because it",
            ["relates the direction of the food to the position of the sun",
             "reveals the particular color of the flowers that were found",
             "indicates the current temperature inside the bees' hive",
             "measures the age of the individual bee that is dancing"],
            0,
            ["Correct. The angle against gravity encodes direction relative to the sun.",
             "Color is not encoded by the dance.",
             "Temperature is not mentioned.",
             "The bee's age is irrelevant to the dance."],
            "The angle's meaning comes from its relation to the sun's direction."),
        "structure": (
            "The passage is organized mainly by",
            ["describing a behavior and then explaining what it communicates",
             "comparing the honeybee with the wasp point by point",
             "listing, one by one, the separate parts of a flower",
             "arguing that bees deserve far less scientific study"],
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
            ["the statement that the length of the bee's straight run signals distance",
             "the statement that the bee dances on a vertical comb in total darkness",
             "the statement that other bees crowd around and follow the dancer closely",
             "the statement that the dance passes its information without any sound"],
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
            ["Glass is endlessly recyclable in principle, but flawed systems keep much of it from reuse.",
             "Glass loses a noticeable amount of its quality each time it is recycled again.",
             "Glass, unlike most materials, simply cannot be recycled by any method at all.",
             "Sorting glass by color is what actually makes recycling glass impossible to do."],
            0,
            ["Correct. The passage contrasts glass's ideal recyclability with system failures.",
             "The passage says glass keeps its quality when remade.",
             "It says glass can be remade again and again.",
             "Color sorting is offered as a solution, not an obstacle to recycling."],
            "The passage's point is the gap between glass's ideal recyclability and imperfect systems."),
        "inference": (
            "It can reasonably be inferred that mixing glass colors during recycling",
            ["reduces the usefulness, and so the value, of the recycled material",
             "improves the overall strength of the new bottles that result",
             "is actually required by most existing recycling regulations",
             "has no real effect of any kind on the recycling process"],
            0,
            ["Correct. The passage says mixing colors lowers the value of recycled glass.",
             "Mixing lowers value; it does not improve strength.",
             "Sorting is recommended, not color mixing.",
             "Mixing clearly has a negative effect."],
            "Mixed colors lower the recycled material's value, the passage states."),
        "structure": (
            "The author contrasts 'this ideal' with 'reality' mainly to",
            ["highlight the gap between what is possible and what actually happens",
             "argue that glass, on balance, should not be recycled at all",
             "describe in detail the process by which new glass is manufactured",
             "compare glass with plastic across several points of difference"],
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
            ["the statement that much glass ends up in landfills because collection is uneven",
             "the statement that a bottle recycled today can become a bottle next month",
             "the statement that glass can be melted down and remade without losing quality",
             "the statement that the material is willing while our systems need redesigning"],
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
             "Lighthouses stopped working and went dark once automation was introduced.",
             "Lighthouse keepers were never really necessary for the lights to function.",
             "Modern lighthouses still need a keeper to climb the tower every night."],
            0,
            ["Correct. The passage contrasts improved reliability with the loss of the human keeper.",
             "The lights 'still shine,' more reliably than before.",
             "Keepers performed essential tasks for centuries.",
             "Automation withdrew the keepers."],
            "The passage balances technical gain against a human loss."),
        "inference": (
            "It can reasonably be inferred that, before automation, a lighthouse's reliability depended on",
            ["the constant nightly labor of a dedicated human keeper",
             "the complete absence of storms along that stretch of coast",
             "electric lamps, timers, and remote sensors doing the work",
             "the sheer height of the tower above the surrounding water"],
            0,
            ["Correct. Keepers performed the nightly tasks that kept the light burning.",
             "Storms occurred and made the work dangerous.",
             "Timers and sensors came later, with automation.",
             "Height alone did not keep the light lit."],
            "Reliability rested on the keeper's constant labor."),
        "structure": (
            "The passage is organized mainly as a shift from",
            ["a human-run past to an automated present",
             "a list of the world's most famous lighthouses",
             "a back-and-forth debate between two keepers",
             "a set of instructions for building a tower"],
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
            ["the statement that the lights still shine, more reliably than ever before",
             "the statement that storms made the keeper's nightly work dangerous",
             "the statement that the keepers were gradually withdrawn over time",
             "the statement that isolation made the work of the keeper lonely"],
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
             "The frozen seed vault is opened and drawn upon by its keepers every single day.",
             "Seeds kept in the frozen vault lose the ability to sprout within about a year.",
             "The mountain vault was built mainly to store bars of gold rather than seeds."],
            0,
            ["Correct. The passage explains the vault as a rarely used backup that protects crop variety.",
             "The keepers hope it is rarely needed.",
             "The cold lets seeds sprout even after decades.",
             "It values seeds 'more than gold,' figuratively."],
            "The passage frames the vault as a safeguard for crop diversity."),
        "inference": (
            "The comparison to a fire extinguisher mainly suggests that the vault is",
            ["valuable precisely because it is ready even if it is rarely used",
             "dangerous and therefore risky to keep anywhere nearby",
             "drawn upon constantly throughout every month of the year",
             "useful for nothing other than literally putting out fires"],
            0,
            ["Correct. Like an extinguisher, its worth lies in readiness for a rare emergency.",
             "No danger is implied.",
             "The passage hopes it is rarely needed.",
             "The analogy is about readiness, not literal firefighting."],
            "The analogy stresses preparedness for an uncommon emergency."),
        "structure": (
            "The passage develops its main idea primarily by",
            ["explaining the vault's purpose and how its cold preserves the seeds",
             "listing, one by one, the many countries that helped build it",
             "comparing two rival seed vaults located in different regions",
             "providing recipes that make use of the crops stored inside"],
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
            ["the statement that even after decades the stored seeds can still sprout",
             "the statement that the vault is built deep inside a frozen mountain",
             "the statement that the seeds were gathered from around the world",
             "the statement that the vault serves as a backup against crop loss"],
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
        "text_a": ("Assigning homework in the early grades teaches children "
                   "responsibility and reinforces the day's lessons. A short, regular "
                   "task helps young students build the habit of independent work long "
                   "before the stakes are high."),
        "text_b": ("For young children, nightly homework offers little measurable "
                   "benefit and can sour their attitude toward school. Time spent on "
                   "worksheets, the author argues, would be better spent reading for "
                   "pleasure or playing outside."),
        "questions": [
            ("How would the author of Text 2 most likely respond to the claim in Text 1 that homework 'reinforces the day's lessons'?",
             ["by arguing that the benefit is small and is outweighed by drawbacks for young children",
              "by agreeing that homework is clearly essential in the early grades for every child",
              "by insisting that young children should be assigned more worksheets, not fewer",
              "by claiming that homework has no effect on responsibility at any age whatsoever"],
             0,
             ["Correct. Text 2 says the benefit is little and the costs (souring attitudes) are real.",
              "Text 2 disagrees that homework is essential for the young.",
              "Text 2 favors reading and play over worksheets.",
              "Text 2 addresses early grades, not 'any age,' so this overstates its claim."],
             "Text 2 would counter that the reinforcing benefit is minor and outweighed for young children."),
            ("Which choice best describes the relationship between the two texts?",
             ["they reach opposing conclusions about homework in the early grades",
              "they fully agree on the clear value of homework in the early grades",
              "Text 2 mainly offers evidence that supports the conclusion of Text 1",
              "both texts argue that the amount of homework should be increased"],
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
             ["zoos are the best available way to build public support for conservation",
              "protecting natural habitats from harm is a desirable goal worth pursuing",
              "animals can ever be seen by the public in filmed nature documentaries",
              "zoos, as a simple matter of fact, keep animals housed within enclosures"],
             0,
             ["Correct. Text 1 calls the zoo connection hard to replace; Text 2 says reserves and films can do it.",
              "Both value habitat protection.",
              "Both accept documentaries exist; that is not the dispute.",
              "Both agree zoos contain animals."],
             "Their disagreement is whether zoos are the best route to public support."),
            ("How does Text 2 respond to a central benefit claimed in Text 1?",
             ["it offers alternatives that, it claims, achieve the benefit without confinement",
              "it denies that members of the public care about wild animals at all",
              "it agrees that zoos are truly the only option for inspiring the public",
              "it argues that zoos should hold an even larger number of animals"],
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
             ["reading on a screen is as good as print for the purpose of learning",
              "students should be permitted to read texts of any kind at all",
              "a typical library building actually contains physical books",
              "the font size of text can be adjusted on an electronic screen"],
             0,
             ["Correct. Text 1 praises screens; Text 2 favors print for comprehension.",
              "Both assume students read.",
              "Both accept libraries hold books.",
              "Both would accept that screens adjust font size."],
             "The dispute is whether screens match print for learning."),
            ("The author of Text 2 would most likely respond to Text 1's emphasis on convenience by",
             ["acknowledging the convenience but giving priority to comprehension",
              "denying outright that screens are able to store many texts at once",
              "agreeing that printed books should be abandoned in the classroom",
              "claiming that the font size of screen text can never be adjusted"],
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
            ("Based on the texts, how do the authors differ in their overall view of remote work?",
             ["Text 1 emphasizes its benefits, while Text 2 emphasizes its drawbacks",
              "both authors conclude that remote work ought to be banned outright",
              "both authors conclude that remote work has essentially no downsides",
              "Text 1 firmly opposes remote work, while Text 2 strongly supports it"],
             0,
             ["Correct. Text 1 highlights benefits; Text 2 highlights drawbacks.",
              "Neither calls for a ban.",
              "Text 2 names downsides.",
              "Their stances are reversed in this option."],
             "Text 1 stresses benefits; Text 2 stresses drawbacks."),
            ("The author of Text 2 would most likely point to which idea as a weakness of the view in Text 1?",
             ["casual in-person conversations that spark new ideas may be lost",
              "the commutes that workers face are simply too short to matter",
              "employees are, in practice, not free to choose where they live",
              "being productive while working from home is entirely impossible"],
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
             ["overstated, because several other factors also contributed to the recovery",
              "completely correct in every detail and in need of no qualification at all",
              "clear proof that the reintroduced wolves had no real effect on the park",
              "evidence that the park's deer had never actually been overgrazing at all"],
             0,
             ["Correct. Text 2 says crediting wolves alone oversimplifies a multi-cause story.",
              "Text 2 questions, not endorses, the claim's completeness.",
              "Text 2 does not deny wolves had any effect.",
              "Text 2 does not dispute overgrazing."],
             "Text 2 sees Text 1's single-cause claim as overstated."),
            ("Which choice best describes how Text 2 relates to Text 1?",
             ["it complicates the explanation in Text 1 by adding several other causes",
              "it restates the explanation in Text 1 without changing anything at all",
              "it supplies precise numerical proof for the explanation in Text 1",
              "it argues that the wolves should now be removed from the park"],
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
             ["learning cursive deserves a share of limited classroom time",
              "students ought to learn to write down their thoughts at all",
              "the practice of typing on a keyboard genuinely exists today",
              "any historical documents were ever written by hand in cursive"],
             0,
             ["Correct. Text 1 defends teaching cursive; Text 2 would spend the time elsewhere.",
              "Both assume students write.",
              "Both accept typing exists.",
              "Both accept historical documents exist."],
             "The disagreement is whether cursive warrants class time."),
            ("How would the author of Text 2 most likely respond to Text 1's concern about 'a link to the past'?",
             ["by granting the value but arguing that limited time better serves practical writing",
              "by denying that the past holds any value or interest for students at all",
              "by agreeing that cursive should be the main focus of writing instruction",
              "by claiming that students today are simply unable to learn how to type"],
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
             ["tourism is, on the whole, good for a small town's wellbeing",
              "the visitors who come to a town actually spend any money there",
              "a typical small town has streets that visitors can walk along",
              "the restaurants in a small town employ any workers at all"],
             0,
             ["Correct. Text 1 sees tourism as a lifeline; Text 2 warns it can hollow a town out.",
              "Both accept tourists spend money.",
              "Both accept towns have streets.",
              "Both accept restaurants employ people."],
             "Their dispute is the net effect of tourism on a town."),
            ("The author of Text 2 would most likely respond to Text 1's emphasis on economic benefit by",
             ["noting that unchecked growth can erode a town's appeal and its affordability",
              "denying that tourism creates any new jobs for local residents at all",
              "agreeing that a larger number of visitors is always better for a town",
              "claiming that small towns contain no shops for visitors to spend at"],
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
             ["letter grades are an effective way to represent a student's learning",
              "students physically attend a school building during the academic year",
              "colleges receive any applications at all from prospective students",
              "written feedback can, as a practical matter, be recorded on paper"],
             0,
             ["Correct. Text 1 praises grades' clarity; Text 2 says they distort and hide learning.",
              "Both assume students attend school.",
              "Both accept colleges get applications.",
              "Both accept feedback can be written."],
             "The dispute is whether letter grades effectively represent learning."),
            ("Which choice best states how Text 2 challenges Text 1?",
             ["it argues that a single letter grade conceals what a student can really do",
              "it agrees that letter grades capture a student's understanding perfectly",
              "it claims that employers ignore academic records of every kind entirely",
              "it says that students ought not to receive any feedback on their work"],
             0,
             ["Correct. Text 2's key challenge is that a letter hides actual ability.",
              "Text 2 disputes that grades capture understanding.",
              "Text 2 does not make a claim about employers ignoring records.",
              "Text 2 favors detailed feedback."],
             "Text 2 challenges Text 1 by noting a letter conceals real ability."),
        ],
    },
]


def _shuffle(rng, options, correct_index, rationales):
    order = list(range(len(options)))
    rng.shuffle(order)
    new_options = [options[i] for i in order]
    new_rats = [rationales[i] for i in order]
    return new_options, order.index(correct_index), new_rats


def _reading_q(passage, skill, qtype, est, rng):
    prompt, options, ci, rats, expl = passage[skill]
    options, ci, rats = _shuffle(rng, options, ci, rats)
    stim = {"type": "passage", "title": passage["title"], "text": passage["text"]}
    skill_tag = {"main_idea": "main-idea", "inference": "inference",
                 "structure": "structure", "wic": "vocabulary",
                 "evidence": "evidence"}[skill]
    sub = {"main_idea": "central_idea", "inference": "implied_meaning",
           "structure": "overall_structure", "wic": "vocabulary",
           "evidence": "textual_evidence"}[skill]
    return mc(prompt, options, ci, rats, subskill=sub, qtype=qtype,
              explanation=expl, tags=["reading", skill_tag], est=est, stimulus=stim)


def _passage_complexity(p) -> float:
    """A rough reading-difficulty proxy from prose density: longer passages with
    longer sentences and words read harder. Used to order tiers so easy -> hard
    actually trends harder instead of following authoring order."""
    text = p["text"]
    words = text.split()
    sents = [s for s in text.replace("!", ".").replace("?", ".").split(".") if s.strip()]
    avg_word = sum(len(w) for w in words) / max(1, len(words))
    avg_sent = sum(len(s.split()) for s in sents) / max(1, len(sents))
    return len(text) + 12 * avg_sent + 40 * avg_word


def build_reading(skill: str, rng: random.Random):
    """Return one question body per passage for the given reading skill key,
    ordered hardest-first. The generator pops from the end per tier (easy first),
    so the simplest passages land in the easy tier and the densest in hard."""
    qtype = "passage_reading"
    est = 80 if skill in ("evidence", "structure") else 70
    ordered = sorted(PASSAGES, key=_passage_complexity, reverse=True)
    return [_reading_q(p, skill, qtype, est, rng) for p in ordered]


def build_cross_text(rng: random.Random):
    """Return all cross-text question bodies from paired passages."""
    items = []
    for pair in PAIRED:
        stim = {"type": "paired_passages", "title": "Paired passages",
                "text": pair["text_a"], "text_b": pair["text_b"]}
        for prompt, options, ci, rats, expl in pair["questions"]:
            options, ci, rats = _shuffle(rng, options, ci, rats)
            items.append(mc(prompt, options, ci, rats,
                            subskill="compare_viewpoints", qtype="passage_reading",
                            explanation=expl, tags=["reading", "cross-text"],
                            est=90, stimulus=stim))
    return items


# Additional original passages (kept separate for independent expansion).
from .passages_extra import PASSAGES2, PAIRED2  # noqa: E402
PASSAGES.extend(PASSAGES2)
PAIRED.extend(PAIRED2)
