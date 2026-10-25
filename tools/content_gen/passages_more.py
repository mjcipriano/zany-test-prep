"""A third pool of original reading passages and comprehension questions.

This module supplements passages.py and passages_extra.py with more original
prose written for this project, covering the genres the SAT and ACT reading
sections draw on: literary narrative (original fiction, some first-person),
social science, humanities (arts, history, philosophy), natural science, and
several pieces with a quantitative slant. Lengths run from about 110 to 190
words so the complexity ordering in passages.build_reading has real spread.

Each single passage in PASSAGES3 yields five questions (main idea, inference,
text structure/purpose, words-in-context, command of evidence). Paired passages
in PAIRED3 are two 90-140 word texts that genuinely engage with each other and
yield three or four cross-text questions.

Distractors are full, plausible statements of length comparable to the key, so
the correct answer does not stand out by length (tools/tests/test_passages.py
measures this). correct_index values are deliberately varied across 0-3. The
rationale for the correct option begins with "Correct." and no other does.

A question spec is (prompt, [opt0..opt3], correct_index, [rat0..rat3], explanation).
"""
from __future__ import annotations

PASSAGES3 = [
    {
        "id": "lamp_room", "title": "The Lamp Room",
        "text": (
            "Every evening at dusk, Ines climbed the one hundred and twelve iron steps "
            "to the lamp room, counting them under her breath as her father had taught "
            "her. He was ill that winter, and the keeper's log, which he had kept in his "
            "cramped, careful hand for twenty years, now bore her looser script. She "
            "trimmed the wick, polished the great lens until her own face swam in it, "
            "and set the clockwork turning. Below, the sea worried at the rocks. Ines did "
            "not love the lighthouse, exactly; she loved the moment when the beam first "
            "swung out across the water and she imagined a ship's mate, miles off, "
            "lifting his head. It was the only conversation she had ever had with "
            "strangers, and it consisted of a single word, repeated all night: here."),
        "main_idea": (
            "Which choice best states the main idea of the text?",
            ["Ines takes over her ill father's duties and finds meaning in the beam's silent message to distant sailors.",
             "Ines resents the lighthouse and performs her father's duties only because no one else in the family is willing.",
             "Ines has grown so skilled at tending the lamp that she now keeps the log far more carefully than her father ever did.",
             "Ines dreams of leaving the lighthouse so that she can finally speak with the sailors whose ships pass at night."],
            0,
            ["Correct. The text follows Ines doing her father's work and locates her feeling in the beam reaching unseen sailors.",
             "The text says she does not love the lighthouse 'exactly,' but it describes attachment, not resentment, and no other family members appear.",
             "Her script is described as 'looser' than her father's careful hand, so she is not more careful than he was.",
             "She values the imagined contact with sailors; nothing suggests she wants to leave."],
            "The passage centers on Ines's quiet stewardship of the light and the one-word 'conversation' it lets her have."),
        "inference": (
            "Based on the text, it can reasonably be inferred that Ines",
            ["has learned the routine of the lighthouse from her father over a period of time",
             "has only recently arrived at the lighthouse and is teaching herself the work without help",
             "regards the keeper's log as a formality that she rarely bothers to fill in",
             "believes the crews of passing ships can clearly see her in the lamp room"],
            0,
            ["Correct. She counts the steps 'as her father had taught her' and performs the routine without hesitation.",
             "Her father taught her, and she knows the steps by heart, so she is not new or self-taught.",
             "The log 'now bore her looser script,' so she is filling it in.",
             "She only imagines a sailor lifting his head; nothing says she is visible to them."],
            "Her practiced routine and the reference to her father's teaching imply long familiarity."),
        "structure": (
            "The sentence 'Ines did not love the lighthouse, exactly' primarily serves to",
            ["reveal that she plans to abandon her post as soon as her father recovers",
             "introduce a list of the lighthouse's physical defects and dangers",
             "qualify a possible assumption before specifying what she does value",
             "contrast her feelings about the lighthouse with her father's stated opinions"],
            2,
            ["No plan to leave is mentioned.",
             "No defects or dangers are listed afterward.",
             "Correct. The word 'exactly' corrects a simple reading and sets up the precise thing she loves: the beam's reach.",
             "Her father's opinions about the lighthouse are never given."],
            "The sentence refines rather than denies her attachment, leading into what she actually loves."),
        "wic": (
            "As used in the text, the word “worried” most nearly means",
            ["gnawed at persistently", "felt anxious about", "troubled with questions", "wore away completely"],
            0,
            ["Correct. The sea repeatedly tugs and chews at the rocks, as a dog worries a bone.",
             "The sea cannot feel anxiety; the sense is physical.",
             "No questioning is involved.",
             "The rocks are not destroyed; the verb describes ongoing action, not a finished result."],
            "'Worried' here is the physical sense of persistently biting or tugging at something."),
        "evidence": (
            "Which quotation from the text best supports the idea that Ines's father has been unable to perform his usual duties?",
            ["'the keeper's log ... now bore her looser script'",
             "'counting them under her breath as her father had taught her'",
             "'She trimmed the wick, polished the great lens until her own face swam in it'",
             "'It was the only conversation she had ever had with strangers'"],
            0,
            ["Correct. The log he kept for twenty years is now in her handwriting, showing he can no longer keep it.",
             "This shows he taught her, not that he is unable to work now.",
             "This describes her tasks without indicating why she performs them.",
             "This concerns her feelings about the beam, not her father's condition."],
            "The handover of the log is the detail that directly shows the father's incapacity."),
    },
    {
        "id": "proof_box", "title": "Proof",
        "text": (
            "The summer I was sixteen, I worked the four a.m. shift at Delgado's, mostly "
            "because nobody else would. Mrs. Delgado did not believe in teaching; she "
            "believed in watching. For two weeks I shaped loaves beside her while she "
            "said nothing, and for two weeks my loaves came out of the oven squat and "
            "sullen, like they resented being made. Then one morning she pressed a finger "
            "into my dough, frowned, and said, 'You are in a hurry. Bread is not.' That "
            "was all. I slowed down. I let the dough rest in the proof box until it had "
            "nearly doubled, instead of until I got bored. The loaf that came out that day "
            "was not perfect, but it rose. I have thought about that sentence more often "
            "than anything I learned in school, mostly when I am about to rush something "
            "that will not be rushed."),
        "main_idea": (
            "The primary purpose of the text is to",
            ["describe the technical steps involved in baking a loaf of bread from scratch",
             "recount how a brief remark from a mentor taught the narrator a lesson about patience",
             "argue that practical summer jobs teach adolescents far more than formal schooling ever can",
             "explain why the narrator eventually chose a career as a professional baker"],
            1,
            ["Only a few steps are mentioned, and they serve the story rather than instruct.",
             "Correct. The text builds to Mrs. Delgado's remark and the narrator's lasting lesson about not rushing.",
             "The narrator compares the remark favorably with school but makes no general argument about jobs.",
             "Nothing indicates the narrator became a baker."],
            "The narrative exists to deliver the lesson 'Bread is not' in a hurry and its effect on the narrator."),
        "inference": (
            "It can most reasonably be inferred that Mrs. Delgado's silence during the first two weeks",
            ["was a deliberate approach to instruction rather than a sign of indifference",
             "reflected her belief that the narrator could not be taught to bake",
             "resulted from her failure to notice the flaws in the narrator's loaves",
             "ended only because the narrator finally asked her directly for help"],
            0,
            ["Correct. She 'believed in watching,' and her eventual remark shows she had been observing closely.",
             "She does intervene with a precise diagnosis, so she did not think the narrator hopeless.",
             "Her single remark pinpoints the problem, so she had noticed.",
             "The narrator does not ask; Mrs. Delgado speaks unprompted."],
            "Her stated philosophy of watching rather than teaching frames the silence as method."),
        "structure": (
            "Which choice best describes the function of the final sentence?",
            ["It reveals that the narrator eventually abandoned baking for schoolwork.",
             "It summarizes the specific steps the narrator took to improve the dough.",
             "It extends the lesson of the bakery beyond baking into the narrator's later life.",
             "It introduces a new mentor who replaced Mrs. Delgado in the narrator's life."],
            2,
            ["The sentence says nothing about abandoning baking.",
             "The steps were given earlier; the final sentence looks forward, not back.",
             "Correct. The narrator applies the remark to any situation 'that will not be rushed.'",
             "No new mentor appears."],
            "The closing sentence generalizes the bakery lesson to the rest of the narrator's life."),
        "wic": (
            "In the context of the text, “sullen” most nearly means",
            ["burned and blackened", "oversized and airy", "sweet and delicate", "dull and heavy"],
            3,
            ["Nothing suggests burning; the problem is that the loaves failed to rise.",
             "The loaves are 'squat,' the opposite of airy.",
             "Flavor is never mentioned.",
             "Correct. Paired with 'squat,' 'sullen' describes loaves that are dense and lifeless."],
            "The personified 'sullen' loaves are low and heavy, lacking the lift of a good rise."),
        "evidence": (
            "Which quotation best supports the idea that the narrator's early failures stemmed from impatience?",
            ["'instead of until I got bored'",
             "'mostly because nobody else would'",
             "'she believed in watching'",
             "'The loaf that came out that day was not perfect'"],
            0,
            ["Correct. The narrator had been ending the rest when boredom set in rather than when the dough was ready.",
             "This explains why the narrator took the shift, not why the loaves failed.",
             "This describes Mrs. Delgado's method.",
             "This concerns the improved loaf, not the cause of the earlier failures."],
            "The admission that proofing ended with boredom shows the impatience behind the flat loaves."),
    },
    {
        "id": "night_noise", "title": "Measuring the Night",
        "text": (
            "Complaints about city noise are easy to collect and hard to interpret, since "
            "the people who complain are rarely a representative sample. A team of "
            "researchers therefore took a different approach. They lent wrist monitors to "
            "412 residents of a mid-sized city, placed sound meters in each bedroom, and "
            "recorded both for three weeks. The results were less tidy than headlines "
            "about 'noisy cities' suggest. Average nightly noise explained only a small "
            "share of the variation in sleep quality. What mattered far more was the "
            "number of sudden peaks—a siren, a slammed door, a motorcycle—above the "
            "background hum. Residents who experienced more than eight such peaks per "
            "night slept, on average, forty minutes less than those with fewer than three, "
            "even when their average noise levels were nearly identical. The finding "
            "suggests that policies aimed at lowering a neighborhood's overall decibel "
            "level may be targeting the wrong number."),
        "main_idea": (
            "Which choice best states the main finding described in the text?",
            ["Sudden spikes in nighttime noise disrupt sleep more than overall noise levels do.",
             "Residents of noisy cities lose roughly forty minutes of sleep every single night.",
             "Noise complaints provide an accurate picture of which neighborhoods are loudest.",
             "Average decibel levels in bedrooms are the best available predictor of sleep quality."],
            0,
            ["Correct. The study found peaks, not average levels, drove the differences in sleep.",
             "The forty-minute gap was between high-peak and low-peak groups, not a citywide average loss.",
             "The text says complainers are not a representative sample.",
             "Average levels explained only a small share of the variation."],
            "The passage's central result is that the count of noise peaks predicts sleep loss."),
        "inference": (
            "Based on the text, the researchers most likely chose to use monitors rather than complaints because",
            ["residents could not be trusted to report their own sleep habits honestly",
             "complaints come from a self-selected group that may not reflect residents as a whole",
             "wrist monitors are far cheaper to deploy than collecting and sorting written complaints",
             "city officials had refused to share the complaints they had already received"],
            1,
            ["Honesty is not raised; the issue is who complains.",
             "Correct. The opening sentence says complainers are 'rarely a representative sample.'",
             "Cost is never discussed.",
             "No refusal by officials is mentioned."],
            "The text frames the monitors as a response to the sampling problem with complaints."),
        "structure": (
            "The text is organized mainly by",
            ["contrasting the sleep habits of city residents with those of people living in quieter rural areas",
             "listing several sources of urban noise in order from the most disruptive to the least disruptive",
             "identifying a flaw in a common method, describing an alternative study, and drawing a policy implication",
             "narrating the daily experiences of a single resident who took part in a noise study for three weeks in a mid-sized city"],
            2,
            ["Rural areas are never discussed.",
             "The sources named are examples, not a ranked list.",
             "Correct. It moves from the problem with complaints to the monitor study to what policy should target.",
             "The study involved 412 residents and no individual is profiled."],
            "The passage proceeds from method problem to study to implication."),
        "wic": (
            "Which choice gives the closest meaning of “tidy” as it is used in the text?",
            ["simple and clear-cut", "neat and well organized", "small and compact", "profitable and substantial"],
            0,
            ["Correct. The results were less straightforward than headlines imply.",
             "Physical neatness is not at issue.",
             "Size is irrelevant here.",
             "A 'tidy sum' sense does not fit results."],
            "'Less tidy' means the findings resisted a simple summary."),
        "evidence": (
            "Which detail from the text best supports the claim that average noise is not the key factor?",
            ["The researchers lent wrist monitors to 412 residents of a mid-sized city and recorded their sleep for three weeks.",
             "Complaints about city noise are easy to collect but hard to interpret.",
             "Sound meters were placed in each bedroom and recorded for three weeks.",
             "Residents with similar average noise slept differently depending on how many peaks they experienced."],
            3,
            ["This describes the sample, not the finding.",
             "This concerns complaints, not average noise.",
             "This describes method, not results.",
             "Correct. Holding average noise constant, peak count still produced a forty-minute gap."],
            "The comparison at equal average levels isolates peaks as the operative factor."),
    },
    {
        "id": "ship_planks", "title": "The Same Ship",
        "text": (
            "An old puzzle asks us to imagine a wooden ship whose planks are replaced one "
            "at a time as they rot, until not a single original board remains. Is it still "
            "the same ship? Most people say yes; a ship is not its planks but a pattern "
            "that persists through them. Now suppose someone collected every discarded "
            "plank and reassembled them in a warehouse. Which vessel is the original: the "
            "one that sailed continuously, or the one built from the original wood? The "
            "puzzle is not really about ships. It asks what makes anything the same thing "
            "over time, including a person whose cells, memories, and opinions turn over "
            "across decades. One tempting answer is that identity is a matter of "
            "continuity rather than of material: the ship that kept sailing, and the "
            "person who kept living, carry their history forward even as their substance "
            "is exchanged. Whether that answer is correct, it at least explains why the "
            "warehouse ship feels like an imposter."),
        "main_idea": (
            "Which choice best describes the central idea of the text?",
            ["Philosophers have conclusively shown that identity depends on the materials an object is made of.",
             "A classic puzzle about a rebuilt ship raises the broader question of what makes something the same over time.",
             "A ship built from original planks has a stronger claim to being the original than one that was repaired.",
             "People, unlike ships, remain the same over time because their memories never change."],
            1,
            ["The text offers continuity, not material, as the tempting answer, and settles nothing conclusively.",
             "Correct. The author uses the ship to pose a general question about identity, including personal identity.",
             "The text says the warehouse ship 'feels like an imposter.'",
             "The text says a person's memories 'turn over across decades.'"],
            "The ship is a vehicle for the general question of sameness over time."),
        "inference": (
            "The author would most likely agree that the 'continuity' answer",
            ["is appealing and explanatory but not established beyond doubt",
             "has been decisively refuted by the example of the warehouse ship",
             "applies to ships but cannot sensibly be extended to persons",
             "shows that material composition is all that matters to identity"],
            0,
            ["Correct. The author calls it 'tempting' and says 'whether that answer is correct, it at least explains' the intuition.",
             "The warehouse ship is what the answer explains, not what refutes it.",
             "The author explicitly applies it to 'the person who kept living.'",
             "Continuity is offered as an alternative to material composition."],
            "The hedged phrasing marks the answer as attractive but unproven."),
        "structure": (
            "The author introduces the warehouse ship primarily to",
            ["prove that most people's initial answer to the puzzle is mistaken",
             "describe a historical practice of preserving old vessels in warehouses",
             "complicate the puzzle by offering a rival candidate for the original",
             "shift the discussion from ships to the more important case of people"],
            2,
            ["The author does not say the initial answer is wrong.",
             "The warehouse is hypothetical, not historical.",
             "Correct. The reassembled ship creates a second claimant and sharpens the question.",
             "The shift to people comes later and is made explicitly, not through the warehouse example."],
            "The second ship turns a yes-or-no question into a choice between competing candidates."),
        "wic": (
            "As used in the text, the phrase “turn over” most nearly means",
            ["are gradually replaced", "flip upside down", "surrender to an authority", "consider carefully"],
            0,
            ["Correct. Cells, memories, and opinions are exchanged for new ones over decades, like the planks.",
             "No physical flipping is meant.",
             "Nothing is being handed over to anyone.",
             "The phrase describes change, not thought."],
            "'Turn over' parallels the replacement of planks: old parts are swapped for new."),
        "evidence": (
            "Which quotation best supports the idea that the puzzle has implications beyond the example of the ship?",
            ["'Most people say yes; a ship is not its planks but a pattern that persists through them'",
             "'Now suppose someone collected every discarded plank'",
             "'the warehouse ship feels like an imposter'",
             "'It asks what makes anything the same thing over time, including a person'"],
            3,
            ["This stays within the ship example.",
             "This develops the ship example rather than extending it.",
             "This is about the ship, not about wider implications.",
             "Correct. The sentence explicitly widens the puzzle to 'anything,' including persons."],
            "The generalizing sentence is the one that moves beyond ships."),
    },
    {
        "id": "waggle", "title": "Dancing Directions",
        "text": (
            "When a honeybee forager returns to the hive after finding a rich patch of "
            "flowers, she does not simply hand over nectar and leave. She performs a dance "
            "on the vertical face of the comb, running forward in a straight line while "
            "shaking her abdomen, then circling back to repeat the run. Decades of "
            "experiments have shown that the dance is a map. The angle of the run relative "
            "to straight up corresponds to the angle of the food relative to the sun, and "
            "the duration of the waggling encodes distance: roughly one second of waggling "
            "for every kilometer. Other bees crowd around, touch the dancer with their "
            "antennae, and later fly out in the direction described. The system is "
            "imperfect; recruits often land a hundred meters off target. But a forager who "
            "dances for a good site sends many sisters toward it, and small errors are "
            "corrected when those sisters return and dance themselves."),
        "main_idea": (
            "Which choice best states the main idea of the text?",
            ["The honeybee's waggle dance communicates the direction and distance of food to other foragers.",
             "Honeybees locate flowers mainly by following the scent of nectar carried by returning foragers.",
             "The waggle dance is too imprecise to be of much practical use to the colony as a whole.",
             "Honeybee foragers hand over their nectar and immediately leave the hive to gather more."],
            0,
            ["Correct. The passage explains how the dance encodes direction and distance and how others use it.",
             "Scent is never mentioned; the dance is the mechanism described.",
             "The text calls the system imperfect but shows how errors are corrected and recruits sent.",
             "The opening sentence says the forager does not simply hand over nectar and leave."],
            "The passage is an account of the dance as a map read by other bees."),
        "inference": (
            "It can reasonably be inferred that a forager who waggles for about three seconds has found food that is",
            ["about three times richer than an average site",
             "located three degrees from the sun's position",
             "roughly three kilometers from the hive",
             "about a hundred meters from the hive"],
            2,
            ["Duration encodes distance, not richness.",
             "Angle, not duration, encodes direction.",
             "Correct. At roughly one second per kilometer, three seconds signals about three kilometers.",
             "A hundred meters is the typical recruit error, not the distance encoded."],
            "Applying the stated rate of one second per kilometer gives three kilometers."),
        "structure": (
            "The author mentions that recruits 'often land a hundred meters off target' in order to",
            ["argue that the dance has been misinterpreted by researchers",
             "acknowledge a limitation before explaining why it matters little",
             "show that older foragers dance more accurately than younger ones",
             "introduce a competing theory of how bees find food"],
            1,
            ["The author accepts the map interpretation.",
             "Correct. The sentence concedes imperfection, then 'But' explains how numbers and repetition correct errors.",
             "Age of foragers is never discussed.",
             "No competing theory is introduced."],
            "The concession sets up the explanation of how the colony tolerates error."),
        "wic": (
            "In the context of the passage, the word “rich” most nearly means",
            ["wealthy in money", "heavy and fatty", "deeply colored", "abundant in resources"],
            3,
            ["Flowers have no money.",
             "The food-texture sense does not apply to a patch of flowers.",
             "Color is not at issue.",
             "Correct. A 'rich patch' is one with plentiful nectar."],
            "'Rich' describes a site with abundant food."),
        "evidence": (
            "Which detail best supports the claim that the dance encodes direction?",
            ["The angle of the run relative to straight up matches the angle of the food relative to the sun.",
             "The forager runs forward in a straight line while shaking her abdomen.",
             "Other bees touch the dancer with their antennae as she performs.",
             "Roughly one second of waggling corresponds to every kilometer of distance between the hive and the food."],
            0,
            ["Correct. The angle correspondence is the direction code.",
             "This describes the motion without saying what it encodes.",
             "This describes how bees read the dance, not what it encodes.",
             "This is the distance code, not the direction code."],
            "Direction is encoded by angle; the angle detail is the supporting evidence."),
    },
    {
        "id": "railway_time", "title": "Noon by Agreement",
        "text": (
            "Until the 1880s, noon in most American towns was simply the moment the sun "
            "stood highest over that town. A traveler heading west from one city to the "
            "next could find the clocks a few minutes behind at each stop, and nobody "
            "minded, because few people traveled fast enough to notice. The railroads "
            "changed this. A train running on a timetable built from dozens of local "
            "noons was a train waiting to collide with another. In 1883, the major rail "
            "companies divided the continent into four broad zones and declared that every "
            "clock within a zone would read the same. The federal government did not "
            "endorse the scheme for another thirty-five years, and some towns refused "
            "outright, keeping 'sun time' as a point of pride. But commerce followed the "
            "trains. Within a few years, most people had quietly agreed to let a company's "
            "timetable, rather than the sky, tell them what time it was."),
        "main_idea": (
            "Which choice best states the main idea of the text?",
            ["The federal government imposed four time zones on the railroads in 1883 over the strong objections of the major rail companies.",
             "Most American towns before the 1880s kept their clocks carefully synchronized with the clocks of neighboring cities.",
             "Railroads replaced local sun-based time with standard zones, and most people adopted the change before any official backing.",
             "Towns that refused to adopt standard time were eventually forced to comply by the rail companies that served them."],
            2,
            ["The rail companies created the zones; the government did not endorse them for thirty-five years.",
             "Clocks differed from town to town, and nobody minded.",
             "Correct. The passage traces the shift from sun time to railroad zones and notes the public adopted it before the government did.",
             "The text says some towns refused; it never says they were forced."],
            "The passage is about how railroad time displaced local time through practice rather than law."),
        "inference": (
            "The text most strongly suggests that before 1883, differences in local time",
            ["were tolerable because travel was too slow for them to cause problems",
             "were a frequent source of accidents between horse-drawn coaches",
             "were corrected by federal regulations that most towns simply ignored",
             "arose because towns deliberately set their clocks apart from their rivals"],
            0,
            ["Correct. 'Nobody minded, because few people traveled fast enough to notice.'",
             "Collisions are mentioned only as a risk for trains.",
             "No federal regulation existed; the government acted decades later.",
             "Local time came from the sun, not from rivalry."],
            "The passage attributes the earlier tolerance to the slow pace of travel."),
        "structure": (
            "The sentence 'But commerce followed the trains' primarily functions to",
            ["introduce a discussion of the goods that trains carried between cities",
             "explain why the railroads' scheme prevailed despite resistance",
             "suggest that merchants opposed the new time zones",
             "signal that the federal government finally acted"],
            1,
            ["No goods are discussed.",
             "Correct. After noting refusals, the sentence explains that economic life aligned with the railroads, carrying the public along.",
             "Commerce following the trains implies merchants adopted the zones.",
             "Government action came thirty-five years later and is not what this sentence introduces."],
            "The 'But' pivots from resistance to the reason the scheme won anyway."),
        "wic": (
            "As used in the text, the word “endorse” most nearly means",
            ["sign on the back of", "publicly criticize", "financially support", "officially approve"],
            3,
            ["The banking sense of signing a check does not fit.",
             "This is the opposite of the meaning.",
             "Money is not at issue.",
             "Correct. The government did not formally sanction the zones for decades."],
            "To endorse a scheme is to give it official approval."),
        "evidence": (
            "Which quotation best supports the idea that the adoption of standard time was not universal?",
            ["'some towns refused outright, keeping \"sun time\" as a point of pride'",
             "'A traveler heading west ... could find the clocks a few minutes behind at each stop'",
             "'the major rail companies divided the continent into four broad zones'",
             "'most people had quietly agreed to let a company's timetable ... tell them what time it was'"],
            0,
            ["Correct. The refusing towns show that adoption was incomplete.",
             "This describes conditions before standard time existed.",
             "This describes the creation of the zones, not their reception.",
             "This shows widespread adoption, the opposite of the point."],
            "The towns that kept sun time are the direct evidence of holdouts."),
    },
    {
        "id": "library_case", "title": "More Than Books",
        "text": (
            "Whenever a city faces a budget shortfall, someone proposes cutting the "
            "library. The reasoning is familiar: books are cheap, the internet is "
            "everywhere, and surely a building full of shelves is a luxury. This reasoning "
            "misunderstands what a library now does. In most cities the library is the "
            "only indoor public space where no one is required to buy anything. It is "
            "where people without a home address receive mail, where job seekers print "
            "résumés, where children whose parents work late are safe until dinner, and "
            "where someone learning a new language can practice without embarrassment. "
            "None of these services appears in a count of books checked out, which is why "
            "library budgets look so easy to trim. A city that closes its library does not "
            "save the cost of the services the library provided. It simply transfers that "
            "cost, in a less visible form, to its emergency rooms, its police, and its "
            "schools."),
        "main_idea": (
            "Which choice best states the author's main argument?",
            ["Cities should fund libraries because printed books remain more reliable than online sources.",
             "Libraries provide essential services that are overlooked when their value is measured by book circulation alone.",
             "Libraries have become obsolete as public spaces now that internet access is nearly universal.",
             "Emergency rooms and police departments should take over the services that libraries currently offer."],
            1,
            ["The author does not defend books against the internet; the argument is about other services.",
             "Correct. The author lists services invisible in circulation counts and argues cutting them only shifts costs.",
             "This is the view the author is rebutting.",
             "The author says those institutions would absorb the cost, not that they should."],
            "The argument is that libraries' real value lies in services that budget metrics miss."),
        "inference": (
            "The author implies that cutting a library budget",
            ["produces savings that are partly illusory because the costs reappear elsewhere",
             "is justified only in cities that already have widespread internet access",
             "is usually proposed by officials who have never set foot in a library",
             "would be acceptable if libraries first reduced the size of their book collections"],
            0,
            ["Correct. The final sentences say the cost is 'transferred, in a less visible form' to other services.",
             "The author rejects the internet argument rather than accepting it conditionally.",
             "The author does not characterize the proposers' habits.",
             "Book collections are not the author's concern; services are."],
            "The closing claim that costs are transferred rather than saved implies the savings are illusory."),
        "structure": (
            "The author presents the 'familiar' reasoning in the second sentence in order to",
            ["concede that libraries are indeed a luxury in most cities",
             "summarize the evidence that supports the author's own position",
             "state an opposing view before explaining why it is mistaken",
             "describe the process by which a city sets its annual budget"],
            2,
            ["The author immediately calls the reasoning a misunderstanding.",
             "The familiar reasoning is the opposing view, not the author's evidence.",
             "Correct. The next sentence begins 'This reasoning misunderstands,' marking a rebuttal.",
             "Budget procedure is not described."],
            "The sentence sets up the position the rest of the passage refutes."),
        "wic": (
            "Which choice best captures the meaning of “trim” as used in the text?",
            ["reduce", "decorate", "neaten", "balance"],
            0,
            ["Correct. Budgets that look easy to trim are easy to cut.",
             "Decoration is irrelevant to budgets.",
             "Tidying is not the sense here.",
             "Balancing a budget is different from trimming one line of it."],
            "'Trim' in a budget context means to cut."),
        "evidence": (
            "Which quotation best supports the idea that the library's value is hard to measure?",
            ["'books are cheap, the internet is everywhere'",
             "'the library is the only indoor public space where no one is required to buy anything'",
             "'It simply transfers that cost, in a less visible form'",
             "'None of these services appears in a count of books checked out'"],
            3,
            ["This is the opposing view, not a point about measurement.",
             "This describes a service, not the difficulty of measuring it.",
             "This concerns what happens after closure, not measurement of value.",
             "Correct. The sentence says directly that the services are missing from the standard metric."],
            "The statement that services do not appear in circulation counts is the measurement point."),
    },
    {
        "id": "camp_letter", "title": "A Letter from the Camp",
        "text": (
            "Dear Margaret, You will forgive the hand; I am writing on the lid of a trunk "
            "by the light of a lamp that smokes. We reached the river camp on Tuesday, two "
            "days later than the captain promised and a full week later than Father "
            "feared, which puts the truth, as usual, somewhere between hope and worry. The "
            "country here is nothing like the engravings. The hills are brown and lie "
            "about in heaps, and the river is the color of weak coffee. I had expected to "
            "be lonely and find instead that I am never alone, which is worse. There are "
            "forty of us in a space meant for twenty. Still, this morning a boy no older "
            "than you showed me how to find water by watching where the birds go at dusk, "
            "and I thought: here is something I would not have learned at home. Tell "
            "Mother I am eating. It is nearly true. Your brother, Thomas."),
        "main_idea": (
            "Which choice best describes the overall impression the letter conveys?",
            ["The writer is disappointed by the camp but finds small compensations in the experience.",
             "The writer is thrilled by the beauty of the landscape and eager for his family to join him there soon.",
             "The writer regrets leaving home and plans to return to his family as soon as he possibly can.",
             "The writer believes the captain deceived the travelers and intends to expose his dishonesty."],
            0,
            ["Correct. Thomas catalogs disappointments but values the lesson about finding water.",
             "He says the country is 'nothing like the engravings' and describes it unflatteringly.",
             "He expresses no plan to return.",
             "He treats the captain's lateness wryly, not as deception to be exposed."],
            "The letter balances complaint with a note of something gained."),
        "inference": (
            "The remark 'It is nearly true' most strongly suggests that Thomas",
            ["has been lying to Margaret throughout the entire letter",
             "is eating better at the camp than he ever did at home",
             "is softening unpleasant facts to spare his family worry",
             "expects Margaret to pass the letter to their mother unread"],
            2,
            ["He is candid with Margaret about the camp; the softening is for Mother.",
             "'Nearly true' implies he is not eating well.",
             "Correct. He asks Margaret to reassure Mother, then admits the reassurance is only approximately true.",
             "He asks Margaret to relay a message, which implies she will read it."],
            "The aside reveals a protective half-truth meant for their mother."),
        "structure": (
            "The writer's comparison between the captain's promise and Father's fear serves mainly to",
            ["accuse the captain of deliberately misleading the travelers about the journey",
             "establish a wry, measured tone toward both optimism and worry",
             "explain the specific reasons the journey took longer than expected",
             "show that Father's judgment is far more reliable than the captain's"],
            1,
            ["The tone is amused, not accusatory.",
             "Correct. 'Somewhere between hope and worry' treats both the promise and the fear with gentle irony.",
             "No reasons for the delay are given.",
             "Father's fear was also wrong, by a week in the other direction."],
            "The sentence sets the letter's dry, balanced voice."),
        "wic": (
            "In the first sentence of the letter, the word “hand” most nearly means",
            ["assistance", "applause", "handwriting", "a hired worker"],
            2,
            ["He is not asking forgiveness for help.",
             "Applause makes no sense here.",
             "Correct. He apologizes for his penmanship, explaining he is writing on a trunk lid by poor light.",
             "No worker is meant."],
            "'Forgive the hand' asks pardon for messy writing."),
        "evidence": (
            "Which quotation best supports the idea that the camp is overcrowded?",
            ["'There are forty of us in a space meant for twenty'",
             "'I am writing on the lid of a trunk by the light of a lamp that smokes'",
             "'The hills are brown and lie about in heaps'",
             "'I had expected to be lonely'"],
            0,
            ["Correct. Twice the intended occupancy is a direct statement of overcrowding.",
             "This describes his writing conditions, not the number of people.",
             "This describes the landscape.",
             "This describes an expectation, not the crowding itself."],
            "The forty-in-a-space-for-twenty detail states the overcrowding outright."),
    },
    {
        "id": "reef_census", "title": "Counting the Reef",
        "text": (
            "A coral reef looks like rock, but it is a city of animals, each polyp hosting "
            "algae that feed it through photosynthesis and lend it color. When water grows "
            "too warm, the polyps expel their algae and turn ghostly white, a process "
            "called bleaching. Bleached coral is not dead, but it is starving. Surveys of "
            "one large reef system tracked the share of coral cover that bleached during "
            "three heat events. In the first, water temperatures exceeded the local summer "
            "maximum by one degree Celsius for four weeks, and about 30 percent of "
            "surveyed colonies bleached. In the second, the same excess lasted eight "
            "weeks, and bleaching rose to roughly 60 percent. In the third, a two-degree "
            "excess for four weeks produced bleaching comparable to the second event. The "
            "pattern suggests that what harms coral is not temperature alone but "
            "accumulated heat—how far above normal, multiplied by how long. Reefs that "
            "recovered fully did so only when more than a decade passed between events."),
        "main_idea": (
            "Which choice best states the main idea of the text?",
            ["Bleached coral is dead and cannot recover even if water temperatures return to normal quickly.",
             "Coral bleaching depends on both the size and the duration of a temperature excess.",
             "A single degree of warming for four weeks is enough to kill most of the coral on a large reef.",
             "Coral reefs are made of rock that is gradually colored by algae living on its surface."],
            1,
            ["The text says bleached coral 'is not dead' and that reefs can recover.",
             "Correct. The three events show that heat excess multiplied by duration predicts bleaching.",
             "One degree for four weeks bleached about 30 percent, and bleaching is not death.",
             "The text says reefs only look like rock; they are animals."],
            "The passage's conclusion is the accumulated-heat idea drawn from the three events."),
        "inference": (
            "Based on the text, a one-degree excess lasting twelve weeks would most likely produce bleaching that is",
            ["greater than that of the second event",
             "about equal to that of the first event",
             "less than that of the third event",
             "impossible to estimate from the pattern described"],
            0,
            ["Correct. Twelve weeks at one degree is more accumulated heat than eight weeks at one degree, which bleached 60 percent.",
             "The first event was only four weeks; twelve weeks is three times the accumulated heat.",
             "The third event equaled the second; twelve weeks exceeds both.",
             "The accumulated-heat pattern gives a clear basis for the estimate."],
            "More accumulated heat than the second event implies more bleaching."),
        "structure": (
            "The author describes the reef as 'a city of animals' primarily to",
            ["emphasize how crowded modern reefs have become",
             "suggest that reefs should be managed the way cities are governed",
             "introduce the concept of accumulated heat",
             "correct a common misperception about what coral is"],
            3,
            ["Crowding is not the point.",
             "Management is never discussed.",
             "Accumulated heat comes later, from the survey data.",
             "Correct. The phrase follows 'looks like rock, but' and reframes coral as living animals."],
            "The metaphor replaces the rock impression with the reality of living polyps."),
        "wic": (
            "As used in the text, the word “comparable” most nearly means",
            ["similar in degree", "worthy of praise", "able to be measured", "clearly superior"],
            0,
            ["Correct. The third event's bleaching was about the same as the second's.",
             "No praise is involved.",
             "Measurability is not the sense.",
             "The text draws an equivalence, not a ranking."],
            "'Comparable' here means roughly equal."),
        "evidence": (
            "Which finding best supports the author's claim about accumulated heat?",
            ["Bleached coral is starving rather than dead.",
             "Polyps expel their algae and turn white when water grows too warm.",
             "Two degrees for four weeks bleached about as much coral as one degree for eight weeks.",
             "Reefs that recovered fully did so only when more than a decade passed between successive heat events."],
            2,
            ["This describes the state of bleached coral, not what causes it.",
             "This explains bleaching generally, not the role of duration.",
             "Correct. Equal products of degrees and weeks gave equal bleaching, which is the accumulated-heat idea.",
             "This concerns recovery, not the cause of bleaching."],
            "The matching results for two degrees-times-four and one degree-times-eight support the claim."),
    },
    {
        "id": "fresco_clean", "title": "Scrubbing the Centuries",
        "text": (
            "When restorers cleaned a famous ceiling fresco in the 1980s, removing five "
            "hundred years of soot, candle smoke, and old varnish, they revealed colors so "
            "bright that some critics refused to believe them. The pale blues and acid "
            "greens, the critics argued, could not be the painter's own; the cleaning must "
            "have stripped away a final layer of shading the artist had applied by hand. "
            "The restorers answered that the dark layer was glue, applied by earlier "
            "restorers to revive a surface dulled by smoke, and that the chemistry of the "
            "residue supported their account. The dispute was never fully settled, and "
            "perhaps it could not be. Every cleaning is a wager about which layers are the "
            "work and which are the damage. The restorers wagered that the painter wanted "
            "brilliance; the critics wagered that he wanted depth. Both sides claimed to "
            "speak for an artist who had been dead for four centuries and who, "
            "inconveniently, had left no instructions."),
        "main_idea": (
            "Which choice best states the central idea of the text?",
            ["Chemical analysis proved beyond question that the critics were wrong about the dark layer on the fresco.",
             "The restorers damaged the fresco by removing shading that the painter had applied with his own hand.",
             "The restoration dispute could not be resolved because both sides had to guess at the painter's intentions.",
             "Critics of the restoration were motivated chiefly by a dislike of bright colors in art."],
            2,
            ["The text says the chemistry 'supported' the restorers but the dispute 'was never fully settled.'",
             "This is the critics' claim, which the text does not endorse.",
             "Correct. The text frames both positions as wagers about an artist who left no instructions.",
             "The critics' motive is presented as a belief about shading, not a taste for dull color."],
            "The passage's conclusion is that the disagreement rests on unknowable intentions."),
        "inference": (
            "The author most likely says the painter left no instructions 'inconveniently' in order to suggest that",
            ["his silence left both parties free to project their own preferences onto him",
             "he deliberately concealed his methods from the restorers of future centuries",
             "artists of the period were generally careless about documenting their work",
             "the dispute would have been avoided had the restorers consulted art historians"],
            0,
            ["Correct. Both sides 'claimed to speak for' the artist, and the lack of instructions lets each do so.",
             "No deliberate concealment is implied.",
             "The text makes no claim about artists in general.",
             "Historians are not mentioned as a remedy."],
            "The ironic adverb points to how the absence of instructions enables competing claims."),
        "structure": (
            "The text is structured as",
            ["a chronological history of the fresco from its original painting through five centuries to the present day",
             "a presentation of two competing positions followed by a reflection on why neither can prevail",
             "an argument that the critics were right, supported by chemical evidence",
             "a step-by-step description of the techniques used to clean a fresco"],
            1,
            ["Only the 1980s cleaning is narrated.",
             "Correct. Critics and restorers are each given their case, then the author explains the impasse.",
             "The chemistry supported the restorers, and the author sides with neither.",
             "Techniques are not described in steps."],
            "The passage sets out two sides and then reflects on the stalemate."),
        "wic": (
            "As used in the text, the word “revive” most nearly means",
            ["bring back to life", "perform once again", "restore brightness to", "remember fondly"],
            2,
            ["A painted surface is not alive.",
             "Performance does not apply.",
             "Correct. Earlier restorers applied glue to freshen a surface 'dulled by smoke.'",
             "Memory is not the sense."],
            "To revive a dulled surface is to brighten it."),
        "evidence": (
            "Which quotation best supports the restorers' position?",
            ["'colors so bright that some critics refused to believe them'",
             "'the chemistry of the residue supported their account'",
             "'Every cleaning is a wager'",
             "'the critics wagered that he wanted depth'"],
            1,
            ["This describes the critics' reaction, not evidence for the restorers.",
             "Correct. The chemical evidence is cited directly in support of the restorers' account.",
             "This is the author's neutral reflection.",
             "This states the critics' position."],
            "The chemistry of the residue is the one piece of evidence credited to the restorers."),
    },
    {
        "id": "queue_norms", "title": "The Logic of the Line",
        "text": (
            "A line is a strange institution. No law requires a crowd at a bus stop to "
            "arrange itself in order of arrival, and no one is paid to enforce the "
            "arrangement; yet in many places the line forms anyway, and someone who cuts "
            "in provokes a resentment far out of proportion to the few seconds lost. "
            "Economists who study such norms point out that the line solves a problem "
            "that would otherwise be solved by pushing, and that everyone in it, including "
            "the person at the back, benefits from a rule that keeps the strong from "
            "simply going first. Field studies reveal a subtler pattern. People will "
            "tolerate a cutter who offers a reason, even a flimsy one, far more readily "
            "than one who offers none, and they will defend the place of a stranger ahead "
            "of them almost as fiercely as their own. The line, in other words, is less a "
            "queue of individuals than a small, temporary society with a shared sense of "
            "what is owed."),
        "main_idea": (
            "Which choice best states the main idea of the text?",
            ["Waiting lines are self-enforced social norms that function like small societies.",
             "Laws requiring orderly lines are necessary because people will otherwise push to the front.",
             "People at the back of a line gain nothing from the rule of first come, first served.",
             "Line cutting is tolerated in most situations as long as it costs other people little time."],
            0,
            ["Correct. The passage explains the line as an unenforced norm and ends by calling it a temporary society.",
             "The text says no law requires lines, yet they form anyway.",
             "The text says everyone, including the person at the back, benefits.",
             "Cutting provokes resentment 'far out of proportion' to the time lost."],
            "The passage builds from the puzzle of unenforced order to the idea of the line as a society."),
        "inference": (
            "The text most strongly suggests that people's anger at a line cutter is driven by",
            ["the belief that the cutter is physically stronger than they are",
             "a sense that a shared rule has been violated rather than by the time lost",
             "the fear that others will immediately begin cutting once one person does",
             "a desire to be compensated for the seconds that they have lost"],
            1,
            ["Strength is mentioned only as what the line prevents from deciding order.",
             "Correct. The resentment is 'out of proportion to the few seconds lost,' and people defend strangers' places too.",
             "Contagion of cutting is not discussed.",
             "The text says the time lost does not explain the reaction."],
            "Defending strangers' places shows the reaction is about the rule, not personal loss."),
        "structure": (
            "The phrase 'in other words' signals that the final sentence",
            ["introduces a counterexample to the field studies",
             "shifts the discussion to how lines work in other countries and cultures",
             "begins a list of specific rules that lines follow",
             "restates the preceding evidence as a general interpretation"],
            3,
            ["Nothing in the final sentence contradicts the studies.",
             "No other countries are discussed.",
             "No list follows.",
             "Correct. The sentence sums up the findings as the line being a 'small, temporary society.'"],
            "'In other words' marks a summarizing restatement."),
        "wic": (
            "As used in the text, the word “flimsy” most nearly means",
            ["weak or unconvincing", "thin and easily torn", "lightweight and delicate", "hastily constructed"],
            0,
            ["Correct. A flimsy reason is one that does not hold up well, yet it is still accepted.",
             "Physical thinness does not apply to a reason.",
             "Delicacy is not the sense.",
             "Construction speed is irrelevant."],
            "A 'flimsy' excuse is a weak one."),
        "evidence": (
            "Which detail best supports the claim that a line is 'a small, temporary society'?",
            ["No one is paid to enforce the order of a line.",
             "Economists say the line prevents disputes from being settled by pushing.",
             "People defend a stranger's place in line almost as fiercely as their own.",
             "The person at the back of the line also benefits from the rule."],
            2,
            ["This shows the norm is unenforced, not that people act on others' behalf.",
             "This explains the line's function, not its social character.",
             "Correct. Defending a stranger shows members acting for the group's shared rule, as in a society.",
             "This is about individual benefit, not shared obligation."],
            "Acting on behalf of strangers is what makes the line society-like."),
    },
    {
        "id": "moraine", "title": "Stones Out of Place",
        "text": (
            "Travelers across the farmland of the northern plains sometimes notice a "
            "boulder the size of a cart sitting alone in a field, miles from any rock of "
            "its kind. Farmers once called such stones 'erratics,' and the name was apt: "
            "nothing in the surrounding geology could explain how they got there. The "
            "explanation lay to the north. During the last ice age, sheets of ice more "
            "than a kilometer thick crept south, plucking rock from the bedrock beneath "
            "and carrying it, frozen in place, for hundreds of kilometers. When the "
            "climate warmed and the ice melted, everything it carried dropped where it "
            "stood. The ridges of gravel that mark the farthest advance of the ice, called "
            "moraines, now run across the landscape like the rim of a dried puddle. By "
            "matching an erratic's minerals to the bedrock where they originate, "
            "geologists can trace the path of ice that vanished ten thousand years ago, "
            "reading a map drawn by something that no longer exists."),
        "main_idea": (
            "Which choice best states the main idea of the text?",
            ["Farmers of the northern plains have long struggled to clear the enormous boulders that litter their fields and block their plows.",
             "The last ice age ended when sheets of ice more than a kilometer thick melted rapidly within a single warm century.",
             "Geologists have been unable to explain how boulders came to rest in fields far from any rock of the same kind.",
             "Out-of-place boulders and gravel ridges are traces of ancient ice sheets that geologists use to reconstruct their movement."],
            3,
            ["Farming difficulty is never discussed.",
             "The speed of melting is not stated, and the passage is about what the ice left behind.",
             "The passage gives the explanation: the ice carried them.",
             "Correct. The passage explains erratics and moraines as glacial deposits and ends with geologists reading them as a map."],
            "The passage explains the origin of erratics and how they let geologists trace vanished ice."),
        "inference": (
            "It can reasonably be inferred that a moraine marks the place where",
            ["the ice sheet stopped advancing and began to melt back",
             "the ice sheet was thickest during the ice age",
             "the bedrock beneath the ice was hardest",
             "erratics are least likely to be found"],
            0,
            ["Correct. Moraines mark 'the farthest advance of the ice,' where carried material dropped as melting began.",
             "Thickness is not linked to moraines.",
             "Bedrock hardness is not discussed.",
             "Material dropped where the ice stood, so erratics would be common there."],
            "The 'farthest advance' is the edge where the ice halted and released its load."),
        "structure": (
            "The author compares moraines to 'the rim of a dried puddle' in order to",
            ["suggest that the ice sheets were much smaller than once believed",
             "help the reader picture how melting ice left a ridge at its edge",
             "argue that moraines are temporary features that will soon vanish",
             "illustrate how farmers mistook moraines for natural hills"],
            1,
            ["Scale is not the point of the comparison.",
             "Correct. A dried puddle leaves a ring where its edge was, just as melting ice left a ridge at its farthest extent.",
             "Nothing suggests moraines are vanishing.",
             "Farmers' views of moraines are not mentioned."],
            "The image explains the ridge as the mark of a former edge."),
        "wic": (
            "Which choice gives the closest meaning of “apt” as it is used in the text?",
            ["likely", "quick to learn", "fitting", "inclined"],
            2,
            ["Probability is not the sense.",
             "The learning sense applies to people, not names.",
             "Correct. The name 'erratic' suited stones that seemed to have wandered.",
             "Tendency is not meant."],
            "An apt name is a suitable one."),
        "evidence": (
            "Which quotation best supports the claim that erratics can reveal the path of vanished ice?",
            ["'geologists can trace the path of ice that vanished ten thousand years ago'",
             "'nothing in the surrounding geology could explain how they got there'",
             "'plucking rock from the bedrock beneath and carrying it, frozen in place, for hundreds of kilometers'",
             "'everything it carried dropped where it stood'"],
            0,
            ["Correct. This states that matching minerals to bedrock lets geologists trace the ice.",
             "This describes the original mystery, not its use.",
             "This explains how rocks were moved, not how geologists use them.",
             "This explains deposition, not tracing."],
            "The sentence about tracing the ice's path is the direct support."),
    },
    {
        "id": "within_reach", "title": "What Is Ours",
        "text": (
            "I used to keep a list of things that had gone wrong that week, with the idea "
            "that reviewing it would make me wiser. It made me miserable instead, and I "
            "eventually understood why. Most of the items were not mine. The weather, a "
            "colleague's mood, the outcome of a vote in a city I had never visited: I had "
            "been grading myself on events in which I had no vote. An ancient school of "
            "philosophers drew a line that I have since found useful. On one side are the "
            "things within our power—our judgments, our efforts, our intentions. On the "
            "other side is everything else. They did not say that the second category is "
            "unimportant, only that it is not ours, and that confusing the two is the "
            "chief source of unhappiness. I still keep a list. It is shorter now, and "
            "every item on it is something I actually did, or failed to do. On bad weeks "
            "it is a harder list to read. On good weeks it is the only one that counts."),
        "main_idea": (
            "Which choice best states the main idea of the text?",
            ["Separating what one controls from what one does not makes self-assessment more honest and less painful.",
             "Keeping a written record of weekly failures is the most reliable way to become wiser over the course of a lifetime.",
             "The ancient philosophers were wrong to claim that events outside our control are of little importance to our lives.",
             "Judging oneself by the moods of colleagues and the outcomes of distant events is a sign of unusual conscientiousness."],
            0,
            ["Correct. The author adopts the philosophers' line and finds the resulting list truer and more bearable.",
             "The original list made the author miserable, not wiser.",
             "The text says the philosophers did not call external events unimportant.",
             "The author presents this habit as a mistake, not a virtue."],
            "The essay's arc is from a self-punishing list to one limited to what is 'ours.'"),
        "inference": (
            "The author implies that the original list was unhelpful because it",
            ["was too short to capture everything that had gone wrong",
             "omitted the author's own judgments and intentions entirely",
             "held the author responsible for things the author could not influence",
             "focused only on events in distant cities"],
            2,
            ["The new list is the shorter one; length was not the problem.",
             "The author does not say such items were absent, only that most items were not the author's.",
             "Correct. 'Most of the items were not mine,' and the author was 'grading' on events with 'no vote.'",
             "Distant votes were one example among several."],
            "The problem was accountability for the uncontrollable."),
        "structure": (
            "The final three sentences function mainly to",
            ["admit that the new list has proven no more useful than the old one",
             "show the practical consequence of adopting the philosophers' distinction",
             "introduce a second ancient school with a competing view of control",
             "explain why the author eventually gave up keeping lists altogether"],
            1,
            ["The author calls the new list 'the only one that counts.'",
             "Correct. The shorter list of things actually done is the distinction put into practice.",
             "No second school appears.",
             "The author still keeps a list."],
            "The ending shows the idea applied to the author's own habit."),
        "wic": (
            "As used in the text, the word “grading” most nearly means",
            ["leveling a surface", "sorting by size", "ranking against others", "evaluating"],
            3,
            ["The construction sense does not fit.",
             "Size is irrelevant.",
             "No comparison with other people is implied.",
             "Correct. The author was judging personal performance by outside events."],
            "'Grading myself' means assessing myself."),
        "evidence": (
            "Which quotation best supports the idea that the philosophers did not dismiss external events?",
            ["'They did not say that the second category is unimportant, only that it is not ours'",
             "'On one side are the things within our power—our judgments, our efforts, our intentions'",
             "'confusing the two is the chief source of unhappiness'",
             "'I had been grading myself on events in which I had no vote'"],
            0,
            ["Correct. This states directly that the external category was not called unimportant.",
             "This lists what is within our power, not the philosophers' view of the rest.",
             "This concerns the cost of confusion, not the value of external events.",
             "This is the author's own error, not the philosophers' view."],
            "The sentence explicitly denies that the philosophers dismissed externals."),
    },
    {
        "id": "endgame", "title": "Forty Moves",
        "text": (
            "By the thirtieth move, Priya had stopped seeing the pieces as pieces. The "
            "knight on the rim was a trapped thing with one way out; the pawn on the sixth "
            "rank was a promise she had made twenty moves earlier and now had to keep. "
            "Across the table her opponent, a boy in a sweatshirt who had not looked up "
            "once, took her bishop with an unhurried hand and pressed the clock. Nine "
            "minutes left for her, fourteen for him. Her coach's voice surfaced: when you "
            "are behind on time, do not think faster; think about fewer things. She let "
            "the whole board blur except for the pawn and the two squares in front of it. "
            "There was a path. It required giving up the knight, which her hand did not "
            "want to do, and she noticed, with something like amusement, that her hand "
            "had opinions. She moved the knight anyway. The boy looked up."),
        "main_idea": (
            "Which choice best describes what happens in the text?",
            ["A chess player loses her knight through carelessness and realizes too late that the game is lost.",
             "Under time pressure, a chess player narrows her focus and commits to a sacrifice that unsettles her opponent.",
             "A chess coach interrupts a tournament match to advise his student on managing her remaining time.",
             "Two chess players agree to a draw after both run short of time in a long and evenly matched game."],
            1,
            ["The knight is given up deliberately, as part of a plan.",
             "Correct. Priya applies her coach's advice, finds a path requiring the knight, and the boy finally looks up.",
             "The coach's voice is remembered, not present.",
             "No draw occurs."],
            "The scene turns on Priya's focused decision and its effect on her opponent."),
        "inference": (
            "The detail that the boy 'looked up' at the end most strongly suggests that",
            ["Priya's move has surprised him or disturbed his sense of control",
             "he has realized that the clock is running out for both of the players",
             "he intends to offer Priya a draw out of sympathy for her",
             "he had not noticed until then that his opponent was a girl"],
            0,
            ["Correct. He 'had not looked up once' until her sacrifice; the change signals that the move registered.",
             "He has more time than she does and has shown no concern about the clock.",
             "Nothing suggests sympathy or a draw.",
             "His not looking up conveys detachment, not ignorance of who she is."],
            "The contrast with his earlier indifference makes the look a reaction to her move."),
        "structure": (
            "The author includes the coach's advice primarily to",
            ["suggest that Priya has been poorly prepared for competitive tournament play",
             "contrast the coach's calm with the opponent's impatience",
             "reveal that the coach is watching the game from across the room",
             "motivate the shift in Priya's thinking that leads to her decisive move"],
            3,
            ["The advice helps her, which implies good preparation.",
             "The opponent is unhurried, not impatient.",
             "The voice 'surfaced' in memory; the coach is not present.",
             "Correct. 'Think about fewer things' leads directly to her letting the board blur and finding the path."],
            "The remembered advice is the hinge between pressure and clarity."),
        "wic": (
            "As used in the text, the word “surfaced” most nearly means",
            ["rose to the top of the water", "was spoken aloud", "came to mind", "appeared on the board"],
            2,
            ["No water is involved.",
             "The coach is absent; the voice is remembered.",
             "Correct. The coach's words rose into Priya's awareness.",
             "A voice cannot appear on a board."],
            "A remembered voice 'surfacing' is one coming to mind."),
        "evidence": (
            "Which quotation best supports the idea that Priya feels reluctance about her chosen move?",
            ["'her hand did not want to do'",
             "'the pawn on the sixth rank was a promise'",
             "'Nine minutes left for her, fourteen for him'",
             "'She let the whole board blur'"],
            0,
            ["Correct. Her hand's unwillingness to give up the knight is the reluctance.",
             "This describes her commitment to the pawn, not reluctance.",
             "This states the time situation.",
             "This describes her narrowing of focus."],
            "The personified hand that 'did not want to' is the expression of reluctance."),
    },
    {
        "id": "two_tongues", "title": "Switching Costs",
        "text": (
            "For years, popular articles claimed that growing up with two languages "
            "sharpens the mind in general, making bilingual children better at switching "
            "between any two tasks. The claim rested on laboratory experiments in which "
            "children sorted cards first by color and then, abruptly, by shape. Bilingual "
            "children, in several early studies, made the switch a few hundredths of a "
            "second faster. Later and larger studies complicated the picture. When "
            "researchers pooled results from more than a hundred experiments involving "
            "several thousand children, the average advantage shrank to nearly nothing, "
            "and it vanished entirely once they accounted for differences in family "
            "income and schooling. The early studies were not fraudulent; they were small, "
            "and small studies that found an effect were more likely to be published than "
            "small studies that found none. The episode is less a verdict on "
            "bilingualism, which has obvious practical value, than a lesson in how a "
            "modest finding can grow, through repetition, into a claim the evidence never "
            "supported."),
        "main_idea": (
            "Which choice best states the main idea of the text?",
            ["Bilingual children consistently outperform monolingual children on card-sorting tasks by several hundredths of a second.",
             "Early researchers who studied bilingual children fabricated their results in order to secure publication in scientific journals.",
             "A widely reported cognitive advantage of bilingualism largely disappeared under larger, better-controlled studies.",
             "Learning two languages in childhood has no practical value and should not be encouraged by parents or by schools."],
            2,
            ["The pooled advantage shrank to nearly nothing.",
             "The text says the early studies 'were not fraudulent.'",
             "Correct. The passage traces the claim from small early studies to its collapse in pooled, controlled analyses.",
             "The text says bilingualism 'has obvious practical value.'"],
            "The passage is about a finding that did not survive scrutiny."),
        "inference": (
            "The text suggests that the early studies' results were misleading mainly because",
            ["studies that found an effect were likelier to be published than those that found none",
             "the children who participated in them came from unusually wealthy families",
             "the card-sorting task is not a valid measure of attention in young children",
             "the researchers deliberately excluded monolingual children from their samples altogether"],
            0,
            ["Correct. The text attributes the distortion to small studies and publication favoring positive results.",
             "Income was a confound in the pooled analysis, but the text does not say early samples were wealthy.",
             "The task's validity is not questioned.",
             "No exclusion is mentioned, and the studies compared bilingual with other children."],
            "Publication bias toward positive small studies is the explanation offered."),
        "structure": (
            "The sentence 'The early studies were not fraudulent' serves to",
            ["concede that the early findings were in fact correct after all",
             "head off an overly harsh interpretation before offering a more precise one",
             "shift blame from the researchers to the journalists who publicized the work",
             "introduce a description of how the card-sorting task is administered"],
            1,
            ["The text maintains that the effect vanished.",
             "Correct. It rules out fraud and then explains the real problem: small size and selective publication.",
             "Journalists are not blamed here.",
             "The task was described earlier."],
            "The sentence clears the researchers of dishonesty before diagnosing the actual flaw."),
        "wic": (
            "In the final sentence, the word “modest” most nearly means",
            ["humble in manner", "decently dressed", "reasonably priced", "small in size"],
            3,
            ["A finding has no manner.",
             "Clothing is irrelevant.",
             "Price is irrelevant.",
             "Correct. A 'modest finding' is a small effect, contrasted with the claim it grew into."],
            "'Modest' describes the smallness of the original effect."),
        "evidence": (
            "Which detail best supports the claim that the advantage was not real?",
            ["The pooled effect vanished once income and schooling were taken into account.",
             "Children sorted cards first by color and then abruptly by shape.",
             "Bilingualism has obvious practical value for those who possess it.",
             "Popular articles claimed that two languages sharpen the mind in general."],
            0,
            ["Correct. An effect that disappears with proper controls is not a real effect.",
             "This describes the task, not the result.",
             "This concerns practical value, not the cognitive claim.",
             "This is the claim, not evidence against it."],
            "The disappearance under controls is the decisive evidence."),
    },
    {
        "id": "torpor", "title": "The Cold Sleep",
        "text": (
            "A hummingbird burns energy faster, for its size, than almost any other "
            "vertebrate. Its heart can beat more than a thousand times a minute, and it "
            "must feed every few minutes during the day simply to stay alive. Night poses "
            "an obvious problem: twelve hours without nectar would exhaust a bird that "
            "weighs less than a coin. The solution is a state called torpor. As darkness "
            "falls, the bird's body temperature drops by twenty degrees or more, its heart "
            "slows to a few dozen beats a minute, and its breathing becomes so faint that "
            "early naturalists sometimes mistook torpid hummingbirds for dead ones. Energy "
            "use falls by as much as ninety percent. Torpor is not without cost. A bird in "
            "deep torpor cannot flee a predator, and warming back up at dawn takes time "
            "and energy of its own. Hummingbirds therefore seem to use the state "
            "judiciously, sinking deepest on cold nights or when their fat reserves are "
            "low, and staying nearer to wakefulness when they can afford to."),
        "main_idea": (
            "Which choice best states the main idea of the text?",
            ["Hummingbirds have the fastest heartbeat of any animal and must feed continuously in order to survive.",
             "Early naturalists were mistaken in believing that hummingbirds die each night and revive at dawn.",
             "Torpor is so dangerous to hummingbirds that they enter it only as a last resort on freezing nights.",
             "Hummingbirds survive the night in a low-energy state that they appear to regulate according to need."],
            3,
            ["The heartbeat detail is background; the passage is about torpor.",
             "The naturalists' error is a passing detail.",
             "The text says they sink deepest on cold nights but use torpor regularly and flexibly.",
             "Correct. The passage explains torpor and ends with the birds using it 'judiciously.'"],
            "The passage describes torpor and the apparent regulation of its depth."),
        "inference": (
            "Based on the text, a well-fed hummingbird on a mild night would most likely",
            ["enter a shallower torpor than it would on a cold night",
             "remain fully active and continue feeding throughout the night",
             "enter the deepest torpor possible in order to conserve its fat",
             "be unable to warm itself again before dawn arrives"],
            0,
            ["Correct. Birds stay 'nearer to wakefulness when they can afford to,' and sink deepest when cold or low on fat.",
             "There is no nectar at night, and the text does not describe nighttime feeding.",
             "Deep torpor is for cold nights or low reserves.",
             "Warming is a cost, not an impossibility."],
            "A bird with reserves on a mild night can afford shallower torpor."),
        "structure": (
            "The sentence 'Torpor is not without cost' marks a transition from",
            ["the daytime habits of hummingbirds to their nighttime habits",
             "the observations of early naturalists to modern measurements",
             "describing the benefits of torpor to describing its drawbacks",
             "a general claim about vertebrates to a specific claim about birds"],
            2,
            ["The night has already been introduced.",
             "The naturalists appear before this sentence, not after.",
             "Correct. After the energy savings, the text turns to predators and the cost of rewarming.",
             "The vertebrate comparison opened the passage."],
            "The sentence pivots from advantages to disadvantages."),
        "wic": (
            "As used in the text, the word “judiciously” most nearly means",
            ["in a legal manner", "with careful judgment", "reluctantly and rarely", "according to fixed habit"],
            1,
            ["Law is irrelevant.",
             "Correct. The birds adjust the depth of torpor sensibly to conditions.",
             "They use torpor nightly, so not rarely.",
             "The use varies with conditions, so it is not fixed."],
            "'Judiciously' means with good judgment, adjusting to circumstances."),
        "evidence": (
            "Which detail best supports the claim that torpor involves a dramatic drop in activity?",
            ["The heart slows to a few dozen beats a minute from more than a thousand.",
             "A hummingbird weighs less than a coin.",
             "Warming back up at dawn takes time and energy.",
             "The bird must feed every few minutes throughout the day simply to stay alive."],
            0,
            ["Correct. The fall from over a thousand beats to a few dozen is the drop in activity.",
             "Weight is not activity.",
             "This is a cost of torpor, not a measure of its depth.",
             "This describes daytime, not torpor."],
            "The heart-rate comparison quantifies the drop."),
    },
    {
        "id": "faithful_lie", "title": "The Translator's Choice",
        "text": (
            "Readers often assume that a good translation is a transparent one, a pane of "
            "glass through which the original can be seen undistorted. The assumption is "
            "flattering to translators and entirely false. Every language carves the "
            "world differently. A word that is ordinary in one tongue may have no single "
            "equivalent in another, only a cluster of near-misses, each of which drags in "
            "connotations the author never intended. The translator must choose, and "
            "every choice is a small act of authorship. Consider a poem whose rhythm "
            "depends on short, blunt words. Rendered into a language whose common words "
            "run to four syllables, it can keep its meaning or keep its music, but rarely "
            "both. Some translators preserve the sense and let the poem go slack; others "
            "invent new images to save the beat. Neither is wrong, and neither is the "
            "original. The honest translator does not pretend to be a window. She admits "
            "to being a second author, and asks to be judged as one."),
        "main_idea": (
            "Which choice best states the author's central claim?",
            ["Translation inevitably involves creative choices, so translators are better seen as co-authors than as neutral conduits.",
             "Translators who preserve the rhythm of a poem are more faithful to the original than those who preserve its meaning.",
             "Most readers are capable of judging the accuracy of a translation without any knowledge of the original language.",
             "The best translations are those that render each word of the original with its single exact equivalent in the new language."],
            0,
            ["Correct. The passage argues that every translation requires choices and ends by calling the translator a second author.",
             "The text says neither approach is wrong.",
             "Readers' judgment is not the topic.",
             "The text says single exact equivalents often do not exist."],
            "The argument moves from the window metaphor's falseness to the translator as author."),
        "inference": (
            "The author would most likely agree with which statement about a translator who 'invents new images to save the beat'?",
            ["The translator has betrayed the author and produced a clearly inferior work.",
             "The translator has made a defensible choice that nonetheless departs from the original.",
             "The translator has produced the only acceptable version of the poem.",
             "The translator has succeeded in being a perfectly transparent window."],
            1,
            ["The author says 'Neither is wrong.'",
             "Correct. The author defends both strategies while noting that 'neither is the original.'",
             "The author treats the alternative strategy as equally legitimate.",
             "Inventing images is the opposite of transparency."],
            "The author legitimizes the choice without pretending it is the original."),
        "structure": (
            "The author uses the example of the poem with 'short, blunt words' to",
            ["prove that poetry, unlike prose, cannot be translated at all",
             "praise a specific translation that the author particularly admires",
             "show that languages with long words are less suited to poetry",
             "illustrate a concrete case in which the translator cannot avoid a trade-off"],
            3,
            ["The author describes two workable approaches, not impossibility.",
             "No specific translation is named.",
             "No judgment about languages' suitability is made.",
             "Correct. The poem can keep meaning or music 'but rarely both,' forcing a choice."],
            "The example makes the abstract point about choice concrete."),
        "wic": (
            "As used in the text, the phrase “go slack” most nearly means",
            ["become loosely fastened", "lose tension or energy", "fall inactive in business", "grow careless about duty"],
            1,
            ["Nothing is fastened.",
             "Correct. A poem whose rhythm is lost loses its tautness.",
             "The commercial sense does not apply.",
             "Duty is not at issue."],
            "A poem that goes slack has lost its rhythmic tension."),
        "evidence": (
            "Which quotation best supports the claim that exact equivalence between languages is often impossible?",
            ["'The assumption is flattering to translators and entirely false'",
             "'only a cluster of near-misses, each of which drags in connotations the author never intended'",
             "'Some translators preserve the sense and let the poem go slack; others invent new images to save the beat'",
             "'She admits to being a second author'"],
            1,
            ["This rejects the window assumption without explaining why.",
             "Correct. The 'near-misses' describe the lack of a single equivalent.",
             "This describes translators' strategies, not the underlying problem.",
             "This is the conclusion, not the evidence."],
            "The 'cluster of near-misses' is the statement of non-equivalence."),
    },
    {
        "id": "icefish", "title": "Blood That Will Not Freeze",
        "text": (
            "The waters around Antarctica hover just below the freezing point of fresh "
            "water all year, kept liquid only by their salt. A fish's blood is less salty "
            "than the sea, so by rights the fish that live there should freeze solid from "
            "the inside. They do not, and the reason is a family of proteins unlike "
            "anything in warm-water species. These antifreeze proteins do not lower the "
            "freezing point of blood the way salt does. Instead they attach to the faces "
            "of any ice crystal that begins to form and stop it from growing, so that the "
            "crystal stays microscopic and harmless. The strategy is cheap: a small amount "
            "of protein guards an enormous volume of blood. Genetic comparisons suggest "
            "the proteins arose from a digestive enzyme whose gene was copied and "
            "gradually altered over millions of years. The fish did not invent a new "
            "molecule from nothing. It repurposed an old one, which is how evolution "
            "usually proceeds."),
        "main_idea": (
            "Which choice best states the main idea of the text?",
            ["Antarctic fish keep their blood liquid by maintaining a salt concentration higher than that of the surrounding seawater.",
             "The waters around Antarctica are warmer than commonly believed, which allows fish to survive there year-round.",
             "Antarctic fish avoid freezing through proteins that block ice growth, proteins that evolved from an existing enzyme.",
             "Evolution frequently produces entirely new molecules to meet the demands of extreme environments."],
            2,
            ["Fish blood is less salty than the sea.",
             "The waters are just below the freezing point of fresh water.",
             "Correct. The passage explains the proteins' mechanism and their origin in a repurposed enzyme.",
             "The text says evolution usually repurposes rather than invents."],
            "Mechanism plus evolutionary origin is the passage's content."),
        "inference": (
            "It can most reasonably be inferred that salt keeps seawater liquid by",
            ["lowering the temperature at which the water freezes",
             "attaching to ice crystals and preventing their growth",
             "warming the water through chemical reactions with it",
             "preventing ice crystals from ever beginning to form"],
            0,
            ["Correct. The proteins 'do not lower the freezing point of blood the way salt does,' implying that is what salt does.",
             "This is the proteins' mechanism, contrasted with salt's.",
             "No warming is described.",
             "The text contrasts salt with crystal-blocking, so this is not salt's role."],
            "The contrast with the proteins tells us salt works by lowering the freezing point."),
        "structure": (
            "The final two sentences serve mainly to",
            ["cast doubt on the genetic comparisons described earlier",
             "draw a general lesson about evolution from the specific case",
             "introduce a competing explanation for the fish's survival in frigid water",
             "summarize how the antifreeze proteins attach to ice"],
            1,
            ["They build on the comparisons rather than doubting them.",
             "Correct. The fish's repurposed enzyme is presented as 'how evolution usually proceeds.'",
             "No alternative explanation is offered.",
             "The mechanism was summarized earlier."],
            "The ending generalizes from the fish to evolution at large."),
        "wic": (
            "Which choice best captures the meaning of “cheap” as used in the text?",
            ["of poor or inferior quality", "easily bought in stores", "economical", "unworthy of respect"],
            2,
            ["The strategy is effective, not shoddy.",
             "Nothing is purchased.",
             "Correct. A small amount of protein protects a large volume of blood, so the cost is low.",
             "No contempt is implied."],
            "'Cheap' here means low in cost to the organism."),
        "evidence": (
            "Which detail best supports the claim that the proteins work differently from salt?",
            ["They attach to ice crystals and halt their growth rather than lowering the freezing point.",
             "A fish's blood is less salty than the surrounding sea.",
             "Genetic comparisons suggest the proteins arose from a copied digestive-enzyme gene altered over millions of years.",
             "A small amount of protein guards an enormous volume of blood."],
            0,
            ["Correct. This states the alternative mechanism in contrast with salt's.",
             "This explains why fish should freeze, not how the proteins work.",
             "This is about origin, not mechanism.",
             "This is about efficiency, not the contrast with salt."],
            "The crystal-blocking mechanism is the difference from salt."),
    },
    {
        "id": "platform_clock", "title": "The Eleven-Forty",
        "text": (
            "The station at Harwell had two platforms and one clock, and the clock was "
            "wrong, which everyone in town knew and no one corrected. Mrs. Abernathy stood "
            "under it in her good coat with a hatbox at her feet. She had told her sister "
            "she was going to visit a cousin in the city for a fortnight. The cousin "
            "existed; the fortnight did not. In her handbag, beneath the gloves, was a "
            "letter from a music conservatory addressed to a Miss E. Abernathy, which she "
            "had not been for twelve years, and which she had opened at the kitchen table "
            "that morning while the kettle screamed and nobody came to take it off. The "
            "eleven-forty was late. It was always late, by exactly the amount the clock "
            "was wrong, so that it arrived, in a manner of speaking, on time. She picked "
            "up the hatbox when she heard it. She had not yet decided whether she would "
            "get on."),
        "main_idea": (
            "Which choice best describes the text's central concern?",
            ["A woman is annoyed that her town has never bothered to repair the station's unreliable clock.",
             "A woman is traveling to the city to care for an ailing cousin for a period of two weeks.",
             "A woman has decided to leave her family permanently in order to pursue a career in music.",
             "A woman stands between the life she has and an opportunity she had set aside."],
            3,
            ["The clock is atmosphere, not her concern.",
             "The cousin is a cover story; 'the fortnight did not' exist.",
             "She 'had not yet decided whether she would get on.'",
             "Correct. The letter from her past and her indecision on the platform frame the choice."],
            "The scene is a woman poised between two lives."),
        "inference": (
            "The detail that the letter is addressed to 'Miss E. Abernathy' most strongly suggests that",
            ["the opportunity it offers belongs to an identity she gave up when she married",
             "the letter was delivered to her by mistake and is actually meant for her sister",
             "she has been using a false name in her correspondence with the conservatory",
             "the conservatory has confused her with a younger relative of the same name"],
            0,
            ["Correct. She 'had not been' Miss Abernathy for twelve years, pointing to a married life that displaced an earlier one.",
             "She opened and kept the letter as hers.",
             "'Miss E. Abernathy' is who she was, not a false name.",
             "No younger relative is mentioned."],
            "The maiden name marks the letter as belonging to her former self."),
        "structure": (
            "The author's remark that the train arrives 'in a manner of speaking, on time' primarily serves to",
            ["explain the mechanical reason the station clock cannot be repaired",
             "establish a wry tone and hint at a town where errors are quietly accommodated",
             "indicate that Mrs. Abernathy has badly misjudged how much time she has left to decide",
             "suggest that the railway company is far more reliable than the townspeople"],
            1,
            ["No mechanical explanation is given.",
             "Correct. The joke about matching errors echoes the town's habit of knowing and not correcting.",
             "Her timing is not at issue; the train arrives as expected.",
             "The train is always late; reliability is not the point."],
            "The ironic aside colors the whole setting."),
        "wic": (
            "As used in the text, the word “good” most nearly means",
            ["morally upright", "in working condition", "reserved for special occasions", "kind and generous"],
            2,
            ["A coat has no morals.",
             "Function is not the sense.",
             "Correct. Her 'good coat' is her best one, worn for an important day.",
             "Kindness does not apply to a coat."],
            "'Good coat' is the one kept for best."),
        "evidence": (
            "Which quotation best supports the idea that Mrs. Abernathy has not been honest with her family?",
            ["'The cousin existed; the fortnight did not'",
             "'the clock was wrong, which everyone in town knew and no one corrected'",
             "'while the kettle screamed and nobody came to take it off'",
             "'She had not yet decided whether she would get on'"],
            0,
            ["Correct. The two-week visit she described to her sister is a fiction.",
             "This is about the town, not her.",
             "This describes her household's inattention, not her dishonesty.",
             "This is her indecision, not deception."],
            "The false fortnight is the lie."),
    },
    {
        "id": "guild_years", "title": "Seven Years of Silence",
        "text": (
            "In the workshops of medieval European towns, a boy of twelve might be bound "
            "to a master craftsman for seven years. The contract, signed by his parents, "
            "obliged the master to feed, house, and teach him and obliged the boy to obey, "
            "keep the trade's secrets, and accept no wages. To modern eyes the arrangement "
            "looks exploitative, and sometimes it was. But the guilds that oversaw these "
            "contracts had reasons that went beyond cheap labor. A trade such as "
            "glassmaking or dyeing depended on knowledge that was never written down, "
            "partly because it could not be: how long to hold a rod in the furnace, how a "
            "vat should smell when the color is ready. Such knowledge passed only through "
            "years of watching and failing. The long term also protected the town. A "
            "half-trained craftsman who set up shop could ruin the reputation of a whole "
            "trade. Seven years was the guild's guarantee to its customers that anyone "
            "selling under its name had earned the right."),
        "main_idea": (
            "Which choice best states the main idea of the text?",
            ["Medieval guilds exploited children by binding them to masters who were under no obligation to teach them anything useful.",
             "Long medieval apprenticeships transmitted unwritten skills and protected a trade's reputation, not just supplying cheap labor.",
             "Glassmaking and dyeing were the only medieval trades whose techniques were deliberately kept secret from outsiders.",
             "Modern observers have correctly recognized that medieval apprenticeship contracts offered no benefits to the apprentice."],
            1,
            ["Masters were obliged to feed, house, and teach.",
             "Correct. The passage explains two purposes of the long term beyond labor.",
             "The two trades are examples, not an exhaustive list.",
             "The author pushes back against the purely exploitative view."],
            "The passage defends the long term as serving knowledge and reputation."),
        "inference": (
            "The text suggests that a craft manual, had one existed, would have been",
            ["of limited use, because key skills could only be learned by experience",
             "forbidden by the guilds in order to protect their monopoly on the trade",
             "sufficient to train a competent craftsman in far less than seven years",
             "written in a language that most apprentices would have been unable to read"],
            0,
            ["Correct. Knowledge 'could not be' written down and passed 'only through years of watching and failing.'",
             "The text gives the impossibility of writing, not a ban, as the reason.",
             "The text says such knowledge required years of experience.",
             "Literacy is not discussed."],
            "Skills like judging smell and timing could not be captured in writing."),
        "structure": (
            "The author concedes that the arrangement 'sometimes' was exploitative in order to",
            ["argue that guilds deserve condemnation from modern historians",
             "introduce specific historical cases of masters who mistreated their apprentices",
             "contrast medieval apprenticeships with modern internships",
             "acknowledge a valid objection before explaining the system's other purposes"],
            3,
            ["The author goes on to defend the system's logic.",
             "No specific cases follow.",
             "Modern internships are not mentioned.",
             "Correct. The concession is followed by 'But the guilds ... had reasons that went beyond cheap labor.'"],
            "The concession prepares the turn to the system's rationale."),
        "wic": (
            "In the context of the passage, the word “bound” most nearly means",
            ["tied with rope", "certain to happen", "committed by contract", "headed in a direction"],
            2,
            ["No physical binding is meant.",
             "The sense of inevitability does not fit.",
             "Correct. The boy was legally obligated to the master by a signed contract.",
             "Direction is irrelevant."],
            "To be bound to a master is to be contracted to him."),
        "evidence": (
            "Which quotation best supports the claim that the long apprenticeship benefited the community?",
            ["'A half-trained craftsman who set up shop could ruin the reputation of a whole trade'",
             "'The contract, signed by his parents, obliged the master to feed, house, and teach him'",
             "'how long to hold a rod in the furnace, how a vat should smell when the color is ready'",
             "'Such knowledge passed only through years of watching and failing'"],
            0,
            ["Correct. Protecting a trade's reputation served the town and its customers.",
             "This concerns the apprentice's welfare.",
             "These are examples of unwritten knowledge.",
             "This concerns learning, not community benefit."],
            "The reputation of the trade is the communal stake."),
    },
    {
        "id": "commute_paradox", "title": "The Commuter's Bargain",
        "text": (
            "Economists expect people to make trades that leave them better off. A worker "
            "who accepts a longer commute, for example, should be compensated by a larger "
            "house, a higher salary, or some other benefit that offsets the time lost in "
            "traffic. Survey data tell a more puzzling story. In one long-running study of "
            "several thousand households, people whose commutes grew by twenty minutes "
            "each way reported a decline in life satisfaction roughly equal to the gain "
            "from a nineteen percent raise. Yet they rarely received anything close to "
            "that raise, and most did not move. Researchers have offered several "
            "explanations. Perhaps people misjudge how much they will mind a commute, "
            "imagining the first week rather than the thousandth. Perhaps the costs fall "
            "on one family member while the benefits are shared by all. Or perhaps the "
            "data overstate the effect, capturing people who were already dissatisfied for "
            "other reasons. Whatever the cause, the commute remains one of the few daily "
            "experiences that people seem unable to get used to."),
        "main_idea": (
            "Which choice best states the main idea of the text?",
            ["People who accept longer commutes are usually compensated with a raise of about nineteen percent.",
             "Survey data on commuting are unreliable because they capture only people who were already unhappy.",
             "Long commutes reduce well-being more than theory predicts, and researchers disagree about why.",
             "Most workers quickly adapt to longer commutes, exactly as economists have long predicted they would."],
            2,
            ["They 'rarely received anything close to that raise.'",
             "This is one of three possible explanations, not the main idea.",
             "Correct. The passage presents the puzzle and three competing explanations.",
             "The text says the commute is something people 'seem unable to get used to.'"],
            "The puzzle and the open question of its cause organize the passage."),
        "inference": (
            "The text suggests that the phrase 'the first week rather than the thousandth' refers to",
            ["people's tendency to underestimate the cumulative burden of a repeated experience",
             "the amount of time it typically takes a worker to receive a raise",
             "the period during which a new commute is at its most unpleasant",
             "the total number of households that were surveyed over the many years of the long-running study"],
            0,
            ["Correct. Imagining only the first week misses how the burden accumulates over many repetitions.",
             "Raises are not the subject of this phrase.",
             "The point is the opposite: the later weeks, not the first, are what people fail to imagine.",
             "The phrase is about time, not sample size."],
            "The phrase captures a failure to anticipate repetition."),
        "structure": (
            "The author introduces the three explanations in order to",
            ["argue that the survey data should be disregarded entirely by economists",
             "present competing accounts of the puzzle without endorsing one",
             "show that economists have fully resolved the puzzle",
             "list the benefits that commuters typically receive"],
            1,
            ["Only the third explanation questions the data, and the author does not adopt it.",
             "Correct. Each begins with 'Perhaps,' and the author concludes 'Whatever the cause.'",
             "The author leaves the cause open.",
             "The explanations concern costs, not benefits."],
            "The hedged list leaves the question unsettled."),
        "wic": (
            "As used in the text, the word “offsets” most nearly means",
            ["prints", "postpones", "measures", "counterbalances"],
            3,
            ["The printing sense is irrelevant.",
             "Delay is not meant.",
             "Measurement is not the sense.",
             "Correct. A benefit that offsets lost time compensates for it."],
            "'Offsets' means balances out."),
        "evidence": (
            "Which detail best supports the claim that the commuters' trade did not leave them better off?",
            ["Economists expect people to make trades that leave them better off.",
             "The decline in satisfaction matched a nineteen percent raise, yet commuters rarely received anything close.",
             "The costs may fall on one family member while the benefits are shared.",
             "The study followed several thousand households over many years."],
            1,
            ["This is the expectation the data contradict.",
             "Correct. The loss was large and the compensation was not, so the trade left them worse off.",
             "This is a proposed explanation, not the evidence of the gap.",
             "Sample size does not show the trade was bad."],
            "The mismatch between loss and compensation is the evidence."),
    },
    {
        "id": "deep_end", "title": "Learning Late",
        "text": (
            "I learned to swim at thirty-four, in a municipal pool that smelled of "
            "chlorine and other people's shampoo, in a class otherwise made up of "
            "children. The instructor, a patient woman named Rosa, treated me exactly as "
            "she treated the eight-year-olds, which I resented for one lesson and was "
            "grateful for ever after. Children, it turns out, are not afraid of the water "
            "in the way adults are. They are afraid of it the way they are afraid of the "
            "dark: thoroughly, and without any theory about it. I had theories. I knew "
            "about buoyancy and breath control and the physics of floating, and all of it "
            "deserted me the moment my feet left the bottom. What Rosa taught me, in the "
            "end, was not a technique but a sequence of permissions. You may put your "
            "face in. You may let go of the wall. You may trust that the water, which "
            "does not care about you, will nevertheless hold you up. By the fourth week I "
            "could cross the pool. By the eighth I had stopped counting."),
        "main_idea": (
            "Which choice best states the main idea of the text?",
            ["The narrator overcame an adult's fear of water by learning to trust rather than by acquiring knowledge.",
             "The narrator found that understanding the physics of floating was the key to finally learning to swim.",
             "The narrator was humiliated by being placed in a swimming class made up entirely of young children.",
             "Children learn to swim more easily than adults because they have no fear of the water whatsoever."],
            0,
            ["Correct. Knowledge 'deserted' the narrator; what worked was Rosa's 'sequence of permissions.'",
             "The physics knowledge failed the narrator in the water.",
             "The narrator resented it for one lesson and was grateful afterward.",
             "The text says children are afraid, just differently."],
            "The lesson was trust, not theory."),
        "inference": (
            "The narrator's comment 'I had theories' most strongly implies that",
            ["she had studied swimming more thoroughly than her instructor had",
             "she believed that the children's fear was far more rational than her own was",
             "she intended to teach swimming herself once she had learned",
             "her knowledge about swimming did not help her once she was in the water"],
            3,
            ["No comparison with Rosa's knowledge is made.",
             "She contrasts the children's theory-free fear with her own, but does not call theirs more rational.",
             "No such intention is expressed.",
             "Correct. The next sentence says all of it 'deserted me the moment my feet left the bottom.'"],
            "The theories are set up to be shown useless."),
        "structure": (
            "The sentence 'By the eighth I had stopped counting' functions to",
            ["indicate that the narrator lost interest in the lessons and quit",
             "suggest that swimming had become natural enough not to require measuring",
             "show that the narrator could no longer keep track of how many weeks had passed",
             "reveal that the class had grown too large for the municipal pool"],
            1,
            ["Nothing suggests quitting.",
             "Correct. After measuring progress in weeks and pool widths, she stops needing to measure at all.",
             "The point is about progress, not memory.",
             "Class size is not mentioned."],
            "Ceasing to count signals ease."),
        "wic": (
            "As used in the text, the word “deserted” most nearly means",
            ["left uninhabited", "abandoned", "rewarded", "fled from military service"],
            1,
            ["The landscape sense does not apply.",
             "Correct. The narrator's knowledge left her when she needed it.",
             "This is unrelated.",
             "The military sense does not fit."],
            "Knowledge that deserts you abandons you."),
        "evidence": (
            "Which quotation best supports the idea that the narrator's progress depended on letting go of control?",
            ["'You may trust that the water, which does not care about you, will nevertheless hold you up'",
             "'a municipal pool that smelled of chlorine and other people's shampoo'",
             "'I knew about buoyancy and breath control and the physics of floating, and all of it deserted me'",
             "'By the fourth week I could cross the pool'"],
            0,
            ["Correct. Trusting the water to hold her is the act of surrendering control.",
             "This is setting.",
             "This describes the failure of knowledge, not the act of letting go.",
             "This is the result, not the cause."],
            "The permission to trust is the key moment."),
    },
    {
        "id": "kelp_otter", "title": "The Otter's Shadow",
        "text": (
            "Along parts of the northern Pacific coast, forests of kelp rise thirty "
            "meters from the seafloor, sheltering fish, crabs, and the young of many "
            "open-water species. In the twentieth century, some of these forests vanished, "
            "leaving stretches of bare rock that ecologists called urchin barrens. The "
            "cause was not pollution or warming water but the absence of a single "
            "predator. Sea otters, hunted nearly to extinction for their fur, had once "
            "eaten enormous quantities of sea urchins. Without otters, urchin populations "
            "exploded, and the urchins, which graze on kelp, mowed the forests down. Where "
            "otters were later reintroduced, the sequence ran in reverse: urchins "
            "declined, kelp recovered, and within a decade fish returned. The otter is "
            "what ecologists call a keystone species, an organism whose influence on its "
            "ecosystem is far larger than its numbers would suggest. Remove the keystone "
            "and the arch does not weaken gradually. It falls."),
        "main_idea": (
            "Which choice best states the main idea of the text?",
            ["Pollution and warming water destroyed the kelp forests of the northern Pacific coast during the twentieth century.",
             "The loss and return of sea otters shows how one predator can govern a whole coastal ecosystem.",
             "Sea urchins are the most destructive grazers in the ocean and must be controlled through direct human intervention.",
             "Kelp forests recover only slowly and partially after sea otters are reintroduced to a stretch of coastline."],
            1,
            ["The text says the cause 'was not pollution or warming water.'",
             "Correct. The passage traces the otter-urchin-kelp chain in both directions and names the otter a keystone.",
             "Human control of urchins is not proposed.",
             "Kelp recovered and fish returned within a decade."],
            "The otter's outsized role is the point."),
        "inference": (
            "Based on the text, it can be inferred that fish returned after otters were reintroduced because",
            ["the recovering kelp provided the shelter they needed",
             "the otters drove away the larger predators that had been eating the fish",
             "the urchins that had preyed on the fish were finally eliminated",
             "the water became cleaner once the otters returned to the coast"],
            0,
            ["Correct. The opening says kelp forests shelter fish, and fish returned after kelp recovered.",
             "Otters are described eating urchins, not driving off predators.",
             "Urchins graze on kelp; they do not prey on fish.",
             "Water quality is not part of the explanation."],
            "Kelp is the fish habitat; its return brought the fish."),
        "structure": (
            "The author's final image of a keystone and an arch serves to",
            ["describe the physical structure of a mature kelp forest",
             "compare the strength of the otter to that of stone",
             "convey the suddenness of collapse when a keystone species is removed",
             "suggest that damaged ecosystems can be rebuilt as easily as buildings are"],
            2,
            ["The arch is a metaphor, not a description of kelp.",
             "Strength is not the comparison.",
             "Correct. 'The arch does not weaken gradually. It falls' stresses abrupt collapse.",
             "Rebuilding is not the point of the image."],
            "The metaphor emphasizes how total and sudden the effect of removal is."),
        "wic": (
            "As used in the text, the word “mowed” most nearly means",
            ["trimmed neatly", "harvested for later use", "stacked in orderly piles", "cut down wholesale"],
            3,
            ["The forests vanished, which is more than trimming.",
             "No use is made of the kelp.",
             "Stacking is irrelevant.",
             "Correct. The urchins leveled the kelp forests entirely."],
            "'Mowed down' means destroyed completely."),
        "evidence": (
            "Which detail best supports the claim that otters, not pollution, caused the kelp loss?",
            ["Kelp recovered where otters were reintroduced.",
             "Kelp forests rise thirty meters from the seafloor.",
             "Otters were hunted nearly to extinction for their fur in earlier centuries.",
             "Ecologists called the bare stretches of rock urchin barrens."],
            0,
            ["Correct. If restoring otters restores kelp, otters were the missing factor.",
             "Height is irrelevant to cause.",
             "This explains why otters were absent, not that their absence caused the loss.",
             "The name describes the result, not the cause."],
            "The reversal upon reintroduction is the test of the causal claim."),
    },
    {
        "id": "remembered_flood", "title": "The Flood as Remembered",
        "text": (
            "Oral historians who interviewed survivors of a 1927 river flood fifty years "
            "afterward noticed something unsettling. The survivors agreed on the broad "
            "shape of events—the levee broke at night, the water rose faster than anyone "
            "expected—but they also agreed on details that the written record "
            "contradicts. Many remembered a church bell ringing a warning; the church had "
            "no bell. Several recalled a rescue by boat on a street that, according to "
            "maps, was never flooded. These were not careless witnesses. They were people "
            "who had told the story many times, at reunions and to grandchildren, and "
            "that was precisely the problem. Each retelling smoothed the account, "
            "borrowed vivid details from neighbors' versions, and filled gaps with what "
            "seemed to make sense. Memory, the historians concluded, is not a recording "
            "but a reconstruction, and a community can reconstruct in unison. The "
            "interviews remain valuable, but not as evidence of what happened on the "
            "night of the flood. They are evidence of what the flood became."),
        "main_idea": (
            "Which choice best states the main idea of the text?",
            ["The survivors of the 1927 flood were unreliable witnesses whose testimony should be disregarded by serious historians.",
             "Written records of the 1927 flood were discovered to be less accurate than the memories of the people who lived through it.",
             "Oral historians have developed techniques that allow them to recover the precise details of events from decades earlier.",
             "Survivors' shared memories were reshaped by retelling, making them evidence of the flood's meaning rather than its facts."],
            3,
            ["The text calls the interviews valuable and the witnesses not careless.",
             "The written record is treated as the check on memory, not the reverse.",
             "No such techniques are described.",
             "Correct. The passage explains how retelling altered the memories and what they remain evidence of."],
            "Reconstruction through retelling and its consequence for evidence is the thesis."),
        "inference": (
            "The text suggests that the survivors' shared false memories arose partly because",
            ["they had absorbed details from one another's accounts over years of retelling",
             "they had been coached by the historians before the interviews took place",
             "they were too young at the time of the flood to understand what was happening",
             "they wished to make the flood seem less frightening than it had actually been"],
            0,
            ["Correct. Each retelling 'borrowed vivid details from neighbors' versions.'",
             "No coaching is mentioned.",
             "Ages are not given, and the explanation offered is retelling.",
             "The false details (a warning bell, a rescue) are not reassuring softenings."],
            "Borrowing from neighbors explains the shared errors."),
        "structure": (
            "The sentence 'These were not careless witnesses' serves to",
            ["defend the accuracy of the written record against the survivors' challenges to it",
             "dismiss one explanation before introducing the author's actual explanation",
             "introduce a comparison with witnesses to a different disaster",
             "concede that the survivors' memories were accurate after all"],
            1,
            ["The sentence is about the witnesses, not the record.",
             "Correct. Having ruled out carelessness, the text explains that repeated retelling was the problem.",
             "No other disaster is mentioned.",
             "The memories are still described as contradicting the record."],
            "The sentence clears away a simple explanation to make room for the real one."),
        "wic": (
            "As used in the text, the word “smoothed” most nearly means",
            ["flattened a rough surface", "calmed an angry listener", "made more orderly and coherent", "removed all emotion from"],
            2,
            ["No physical surface is involved.",
             "Listeners' moods are not at issue.",
             "Correct. Each retelling tidied the story, removing gaps and inconsistencies.",
             "The retellings added vivid details rather than draining emotion."],
            "Smoothing an account makes it neater and more consistent."),
        "evidence": (
            "Which quotation best supports the claim that the memories conflict with the documentary record?",
            ["'Many remembered a church bell ringing a warning; the church had no bell'",
             "'the levee broke at night, the water rose faster than anyone expected'",
             "'They were people who had told the story many times, at reunions and to grandchildren'",
             "'Memory, the historians concluded, is not a recording but a reconstruction'"],
            0,
            ["Correct. A remembered bell at a bell-less church is a direct conflict with fact.",
             "These are the details on which memory and record agree.",
             "This explains the cause, not the conflict.",
             "This is the conclusion, not the evidence."],
            "The nonexistent bell is the concrete contradiction."),
    },
    {
        "id": "call_response", "title": "Answering the Horn",
        "text": (
            "A visitor to a jazz club for the first time may wonder how a band with no "
            "sheet music avoids chaos. Part of the answer is a structure older than jazz "
            "itself. In call and response, one voice makes a statement and another "
            "answers it, as a preacher's line is answered by a congregation or a field "
            "song by a chorus. Jazz musicians absorbed this pattern and made it the "
            "grammar of improvisation. A trumpet plays a phrase; the saxophone replies, "
            "perhaps repeating the phrase, perhaps mocking it, perhaps turning it upside "
            "down. The drummer, hearing both, answers with an accent that comments on the "
            "exchange. Nothing is written down because nothing needs to be. Each player "
            "is bound to listen, since the rules of the form make a reply to what was "
            "just played the only acceptable move. What sounds to the newcomer like "
            "freedom is in fact a conversation, with the same obligations any "
            "conversation carries: to attend, to respond, and to leave room."),
        "main_idea": (
            "Which choice best states the main idea of the text?",
            ["Jazz musicians avoid chaos by secretly memorizing sheet music before they perform in public.",
             "The call-and-response pattern originated in jazz clubs and later spread to churches and to work songs.",
             "Jazz improvisation is organized by call and response, which works like the rules of a conversation.",
             "Drummers hold the most important role in a jazz band because they comment on every single exchange."],
            2,
            ["The text says nothing is written down.",
             "The structure is 'older than jazz itself.'",
             "Correct. The passage explains call and response as the organizing grammar and ends with the conversation analogy.",
             "The drummer is one participant among several."],
            "Call and response as conversational grammar is the thesis."),
        "inference": (
            "The text implies that a jazz musician who ignored the other players would be",
            ["violating the basic rules of the form",
             "exercising the freedom that defines jazz for newcomers",
             "following the example set by the preacher",
             "playing in a style that is older than jazz"],
            0,
            ["Correct. 'Each player is bound to listen,' since a reply is 'the only acceptable move.'",
             "The text says the apparent freedom is actually obligation.",
             "The preacher's line is answered; ignoring others breaks the pattern.",
             "The older style is also call and response."],
            "Listening is mandatory, so ignoring others breaks the form."),
        "structure": (
            "The author refers to a preacher and a congregation in order to",
            ["argue that jazz is at bottom a religious form of music",
             "show that the structure predates jazz and is familiar from other settings",
             "contrast the formality of church music with the apparent looseness of jazz",
             "describe the setting in which jazz was first performed"],
            1,
            ["No religious claim about jazz is made.",
             "Correct. The examples illustrate call and response as 'a structure older than jazz itself.'",
             "The examples show kinship, not contrast.",
             "The church is not presented as a jazz venue."],
            "The examples establish the pattern's age and familiarity."),
        "wic": (
            "Which choice gives the closest meaning of “grammar” as it is used in the text?",
            ["the formal study of language", "a textbook for students", "correct spelling and usage", "underlying set of rules"],
            3,
            ["No academic study is meant.",
             "No textbook is involved.",
             "Spelling is irrelevant to music.",
             "Correct. Call and response is the rule system that governs improvisation."],
            "'Grammar' here is the structure that makes improvisation coherent."),
        "evidence": (
            "Which quotation best supports the claim that improvisation is constrained rather than free?",
            ["'the rules of the form make a reply to what was just played the only acceptable move'",
             "'the saxophone replies, perhaps repeating the phrase, perhaps mocking it, perhaps turning it upside down'",
             "'Nothing is written down because nothing needs to be'",
             "'What sounds to the newcomer like freedom'"],
            0,
            ["Correct. 'The only acceptable move' is a constraint.",
             "This lists options, which emphasizes variety rather than constraint.",
             "This concerns notation, not constraint.",
             "This names the appearance of freedom without stating the constraint."],
            "The 'only acceptable move' phrase states the constraint directly."),
    },
    {
        "id": "half_lives", "title": "The Clock in the Bone",
        "text": (
            "Every living thing takes in carbon, and a tiny fraction of that carbon is a "
            "radioactive form called carbon-14, produced in the upper atmosphere and mixed "
            "through the air and oceans. While an organism lives, the fraction in its "
            "tissues matches the fraction in its surroundings. When it dies, the intake "
            "stops, and the carbon-14 it holds begins to decay at a known rate: half of "
            "it is gone after about 5,700 years, half of what remains after another "
            "5,700, and so on. Measuring what fraction remains therefore tells how long "
            "ago the organism died. A bone retaining one-quarter of the expected "
            "carbon-14 has been dead for roughly two half-lives, or 11,400 years. The "
            "method has limits. After ten half-lives so little carbon-14 remains that the "
            "measurement drowns in background noise, which is why the technique says "
            "nothing about dinosaurs. And because the atmospheric fraction has drifted "
            "over the centuries, raw dates must be corrected against tree rings and other "
            "records whose ages are independently known."),
        "main_idea": (
            "Which choice best states the main idea of the text?",
            ["Radiocarbon dating estimates age from carbon-14 decay, within limits set by its half-life and atmospheric change.",
             "Radiocarbon dating is the most accurate method available for determining the age of dinosaur fossils and other ancient remains.",
             "The fraction of carbon-14 in the atmosphere has remained perfectly constant for tens of thousands of years, which makes dating simple.",
             "Tree rings provide a more reliable way of dating organic remains than measurements of carbon-14 ever could."],
            0,
            ["Correct. The passage explains the method, works an example, and states its two limits.",
             "The text says the technique 'says nothing about dinosaurs.'",
             "The atmospheric fraction 'has drifted,' requiring correction.",
             "Tree rings are used to correct radiocarbon dates, not replace them."],
            "Method plus limits is the passage's content."),
        "inference": (
            "Based on the text, a sample retaining one-eighth of the expected carbon-14 would be roughly",
            ["5,700 years old", "11,400 years old", "17,100 years old", "45,600 years old"],
            2,
            ["One half-life leaves one-half, not one-eighth.",
             "Two half-lives leave one-quarter.",
             "Correct. One-eighth is three half-lives, and three times 5,700 is 17,100.",
             "Eight half-lives would leave one two-hundred-fifty-sixth."],
            "Each halving is one half-life; one-eighth takes three."),
        "structure": (
            "The final two sentences of the text serve to",
            ["explain the chemistry by which carbon-14 is produced in the atmosphere",
             "identify limitations of the method described earlier",
             "argue that the method should be abandoned in favor of others",
             "provide a second worked example of a dated sample"],
            1,
            ["Production was mentioned at the start.",
             "Correct. They follow 'The method has limits' and give two.",
             "The limits are described as requiring correction, not abandonment.",
             "No second example is worked."],
            "The ending states the method's constraints."),
        "wic": (
            "As used in the text, the word “drifted” most nearly means",
            ["floated along on water", "changed gradually", "wandered without purpose", "piled up in heaps"],
            1,
            ["No water is involved.",
             "Correct. The atmospheric fraction has shifted slowly over time.",
             "Purposelessness is not the point.",
             "The snowdrift sense does not apply."],
            "A fraction that has drifted has changed slowly."),
        "evidence": (
            "Which detail best supports the claim that the method is useless for very old remains?",
            ["After ten half-lives too little carbon-14 remains to measure above background noise.",
             "Every living thing takes in carbon from its surroundings while it is alive.",
             "The atmospheric fraction of carbon-14 has drifted over the centuries.",
             "Half of the carbon-14 is gone after about 5,700 years."],
            0,
            ["Correct. Too little remaining carbon-14 to measure is why very old samples cannot be dated.",
             "This is background, not a limit.",
             "This limit concerns accuracy, not age range.",
             "This gives the rate, not the limit."],
            "The background-noise limit is the age ceiling."),
    },
    {
        "id": "idle_hours", "title": "In Defense of Doing Nothing",
        "text": (
            "We have made an idol of productivity. Every hour is to be optimized, every "
            "habit tracked, every pause justified as 'recharging' for the work to come. "
            "Even rest is permitted only as an investment. I want to argue for something "
            "less respectable: time that is not for anything. The case is not "
            "sentimental. Most people can name the moment a stubborn problem came loose, "
            "and it was rarely at the desk. It was in the shower, on a walk, in the dull "
            "middle of a long drive. The mind does its deepest sorting when it is left "
            "alone, and it cannot be left alone on a schedule. A culture that fills every "
            "gap does not merely tire its members; it starves the very faculty it claims "
            "to prize. I do not propose that anyone work less. I propose that when the "
            "work is done, we stop pretending that the hours afterward owe us a return. "
            "Some of them will pay anyway. That is not why they are worth having."),
        "main_idea": (
            "Which choice best states the author's main argument?",
            ["People should work fewer hours so that they have more time to rest and recover from their demanding jobs.",
             "Unstructured time is valuable in itself and is also the condition for the insight that productivity culture wants.",
             "Tracking habits and optimizing schedules are the most effective ways of solving stubborn intellectual problems quickly.",
             "Rest should be understood primarily as an investment that yields returns in the quality of later work."],
            1,
            ["The author says 'I do not propose that anyone work less.'",
             "Correct. The author defends time 'not for anything' and notes that insight comes from it anyway.",
             "The author says problems come loose away from the desk.",
             "This is the view the author criticizes."],
            "Idle time is defended both for its own sake and for what it yields."),
        "inference": (
            "The author would most likely view a person who takes walks 'in order to be more creative' as",
            ["still treating idle time as a means rather than an end",
             "having fully adopted the author's recommendation",
             "likely to produce fewer insights than someone who never rests",
             "wasting time that would be better spent at the desk working"],
            0,
            ["Correct. The author objects to rest 'permitted only as an investment,' which such a walk still is.",
             "The author wants hours that do not 'owe us a return.'",
             "The author says insight often comes away from the desk.",
             "The author defends time away from the desk."],
            "A walk taken for a payoff is still rest-as-investment."),
        "structure": (
            "The sentence 'The case is not sentimental' prepares the reader for",
            ["a personal anecdote about the author's own habits of rest",
             "a concession that the author's position is weak",
             "a list of the emotional benefits of doing nothing",
             "a practical argument rather than an appeal to feeling"],
            3,
            ["What follows is a general observation, not a personal anecdote.",
             "No concession follows.",
             "The benefits named are intellectual, not emotional.",
             "Correct. The next sentences give the practical point that problems come loose away from the desk."],
            "The sentence signals a hard-headed argument."),
        "wic": (
            "As used in the text, the word “respectable” most nearly means",
            ["of good family", "socially approved", "fairly large in amount", "honest and law-abiding"],
            1,
            ["Family is irrelevant.",
             "Correct. Purposeless time is less admired by a productivity culture than rest-as-investment.",
             "Quantity is not the sense.",
             "Legality is not at issue."],
            "'Less respectable' means less approved of."),
        "evidence": (
            "Which quotation best supports the claim that constant activity undermines thinking?",
            ["'it starves the very faculty it claims to prize'",
             "'Every hour is to be optimized, every habit tracked, every pause justified'",
             "'I do not propose that anyone work less'",
             "'Some of them will pay anyway'"],
            0,
            ["Correct. Starving the faculty is the harm to thinking.",
             "This describes the culture without stating the harm.",
             "This is a clarification of the proposal.",
             "This concedes a payoff, not a harm."],
            "The 'starves' sentence states the damage."),
    },
    {
        "id": "one_face", "title": "The Moon's Hidden Side",
        "text": (
            "No one on Earth had seen the far side of the Moon until a spacecraft "
            "photographed it in 1959, and the reason is not that the Moon fails to "
            "rotate. It rotates exactly once for every orbit it completes, so that the "
            "same hemisphere always faces us. This coincidence is not a coincidence. "
            "Early in its history the Moon spun faster, but Earth's gravity raised a "
            "slight bulge in its body, and that bulge, dragged along by the Moon's "
            "rotation, was pulled back by Earth's gravity in a way that acted as a brake. "
            "Over hundreds of millions of years the spin slowed until the bulge pointed "
            "steadily at Earth and the braking stopped. Astronomers call the result tidal "
            "locking, and it is common: most large moons in the solar system show one "
            "face to their planets. Earth is subject to the same effect from the Moon. "
            "Our days are lengthening by about two milliseconds per century, which is why "
            "the Moon, patient as it is, has not yet managed to lock us."),
        "main_idea": (
            "Which choice best states the main idea of the text?",
            ["The Moon does not rotate, which is why its far side could not be seen until a spacecraft photographed it.",
             "Earth's rotation has already been locked by the Moon's gravity, so the same hemisphere of Earth always faces the Moon.",
             "The Moon shows Earth one face because gravitational braking slowed its spin, a process common among moons.",
             "Tidal locking is a rare phenomenon that has been observed only in the case of Earth's own Moon."],
            2,
            ["The text says the Moon does rotate, once per orbit.",
             "Earth is being slowed but 'has not yet' been locked.",
             "Correct. The passage explains the braking mechanism and notes that most large moons are locked.",
             "The text says tidal locking 'is common.'"],
            "Mechanism and prevalence of tidal locking organize the passage."),
        "inference": (
            "The text implies that the far side of the Moon",
            ["is a hemisphere that rotates with the Moon but never turns toward Earth",
             "is permanently dark because sunlight never reaches it",
             "faces Earth briefly once every few hundred million years",
             "was visible from Earth within recorded history, before the Moon's spin slowed"],
            0,
            ["Correct. The Moon rotates, but one rotation per orbit keeps the same hemisphere toward Earth.",
             "Sunlight is never discussed; 'far' does not mean dark.",
             "The locking is steady, with no periodic turning.",
             "The slowing took hundreds of millions of years, long before any recorded history."],
            "Rotation matched to orbit hides one hemisphere permanently."),
        "structure": (
            "The author writes 'This coincidence is not a coincidence' in order to",
            ["admit that astronomers cannot account for the Moon's rotation",
             "signal that an explanation for the apparent coincidence follows",
             "suggest that the 1959 photographs were taken by chance",
             "emphasize how unusual the Moon's behavior is among moons"],
            1,
            ["An explanation follows immediately.",
             "Correct. The paradoxical sentence introduces the braking mechanism that explains the match.",
             "The photographs are not the subject.",
             "The text says the behavior is common."],
            "The sentence sets up the causal explanation."),
        "wic": (
            "As used in the text, the word “raised” most nearly means",
            ["lifted to a higher position", "brought up from childhood", "increased in amount", "caused to form"],
            3,
            ["The bulge is not lifted; it is created.",
             "The parenting sense is irrelevant.",
             "No quantity is increased.",
             "Correct. Earth's gravity produced a bulge in the Moon's body."],
            "To raise a bulge is to bring one into being."),
        "evidence": (
            "Which detail best supports the claim that Earth is subject to the same braking effect?",
            ["Earth's days are lengthening by about two milliseconds per century.",
             "The Moon rotates exactly once for every orbit it completes.",
             "Most large moons in the solar system show one face to their planets.",
             "The far side of the Moon was first photographed in 1959."],
            0,
            ["Correct. Lengthening days show Earth's spin is being slowed.",
             "This concerns the Moon, not Earth.",
             "This concerns other moons.",
             "This is historical, not evidence about Earth's rotation."],
            "The slowing of Earth's rotation is the evidence."),
    },
    {
        "id": "fig_tree", "title": "What She Planted",
        "text": (
            "My grandmother's fig tree should not have survived a single winter in our "
            "city. Every November she wrapped it in burlap and old blankets and tied the "
            "bundle with twine, so that for four months the backyard held what looked like "
            "a mummy standing guard over the frozen tomato beds. The neighbors found this "
            "eccentric. I found it embarrassing, in the way that everything about her was "
            "embarrassing to me at fourteen: the accent, the plastic bags folded and "
            "saved, the way she called across the yard to me in a language I answered in "
            "English. The figs came in August. They were small and purple and split at "
            "the bottom when ripe, and she would not let anyone else pick them. The "
            "summer after she died, I unwrapped the tree myself and found I had been "
            "watching her more carefully than I knew: I remembered the order of the "
            "knots. The tree bore that year. I ate the first fig standing in the yard, "
            "and I did not call anyone."),
        "main_idea": (
            "Which choice best describes the central idea of the text?",
            ["The narrator resents being forced to take over the care of a fig tree that the grandmother should never have planted in a cold climate.",
             "The narrator's grandmother was so protective of her fig tree that she refused to let the family eat any of the fruit it produced.",
             "The neighbors' disapproval of the grandmother's gardening methods eventually persuaded the narrator to remove the fig tree.",
             "The narrator's adolescent embarrassment gives way, after the grandmother's death, to an inherited care for what she loved."],
            3,
            ["The narrator unwraps the tree voluntarily and eats the fig; no resentment is expressed.",
             "She would not let others pick the figs; nothing says the family could not eat them.",
             "The tree is kept and tended, not removed.",
             "Correct. The passage moves from embarrassment at fourteen to the narrator tending the tree and eating the first fig alone."],
            "Inheritance of care replaces adolescent embarrassment."),
        "inference": (
            "The detail that the narrator 'did not call anyone' most strongly suggests that",
            ["the moment was a private act of remembrance",
             "the narrator had become estranged from the rest of the family",
             "the narrator wanted to keep all of the figs for herself",
             "the narrator was ashamed to be seen tending the tree"],
            0,
            ["Correct. Eating the first fig alone, in the grandmother's place, is a quiet tribute.",
             "No estrangement is suggested.",
             "Greed does not fit the tone.",
             "The narrator's embarrassment belongs to the past."],
            "Solitude marks the moment as personal."),
        "structure": (
            "The sentence 'I remembered the order of the knots' functions to",
            ["explain the technical method by which the tree was protected from frost",
             "reveal that the narrator had absorbed more from the grandmother than she had realized",
             "show that the grandmother had explicitly taught the narrator how to wrap the tree each fall",
             "indicate that the narrator had forgotten everything else about the grandmother"],
            1,
            ["The method is not explained; the point is memory.",
             "Correct. It follows 'I had been watching her more carefully than I knew.'",
             "The watching was unacknowledged, not formal teaching.",
             "Nothing suggests other memories were lost."],
            "The knots prove the unnoticed attention."),
        "wic": (
            "As used in the text, the word “bore” most nearly means",
            ["tolerated patiently", "carried a heavy weight", "produced fruit", "drilled a hole"],
            2,
            ["Tolerance does not apply to a tree.",
             "No weight is carried.",
             "Correct. 'The tree bore that year' means it yielded figs.",
             "Drilling is irrelevant."],
            "A tree that bears produces fruit."),
        "evidence": (
            "Which quotation best supports the idea that the narrator once viewed the grandmother's habits with discomfort?",
            ["'everything about her was embarrassing to me at fourteen'",
             "'Every November she wrapped it in burlap and old blankets and tied the bundle with twine'",
             "'she would not let anyone else pick them'",
             "'The tree bore that year'"],
            0,
            ["Correct. This states the narrator's past embarrassment directly.",
             "This describes the grandmother's method, not the narrator's feeling.",
             "This describes the grandmother's possessiveness.",
             "This is about the tree."],
            "The confession of embarrassment is the direct evidence."),
    },
    {
        "id": "stone_light", "title": "Walls of Glass",
        "text": (
            "The builders of the great twelfth-century cathedrals faced a contradiction. "
            "They wanted walls that soared and windows that filled with colored light, but "
            "a tall stone wall pierced by large windows is a wall waiting to fall. The "
            "weight of a vaulted ceiling pushes not only down but outward, and the thicker "
            "the wall needed to resist that push, the smaller the windows it could afford. "
            "The solution was to move the support outside. Half-arches of stone, later "
            "called flying buttresses, leaned against the upper walls from the exterior, "
            "catching the outward thrust and carrying it down to massive piers set well "
            "away from the building. Freed from holding up the roof, the walls between "
            "the piers could become little more than frames for glass. Contemporaries "
            "were not universally impressed; one critic complained that the cathedrals "
            "looked as though they were held up by crutches. But the crutches worked. "
            "Churches that would have collapsed under their own ambition instead stood "
            "for eight centuries, their interiors lit like no stone buildings before "
            "them."),
        "main_idea": (
            "Which choice best states the main idea of the text?",
            ["Flying buttresses resolved the conflict between tall, light-filled walls and stability by moving support outside.",
             "Twelfth-century cathedrals were praised by everyone who saw them for the elegance of their exterior supports.",
             "Medieval builders abandoned the goal of large windows because thick walls were required to support vaulted ceilings.",
             "The critics who compared flying buttresses to crutches were correct that the structures were dangerously unstable."],
            0,
            ["Correct. The passage states the contradiction and explains how external supports resolved it.",
             "The text says contemporaries 'were not universally impressed.'",
             "The builders achieved large windows rather than abandoning them.",
             "The buildings stood for eight centuries."],
            "The buttress as solution to the contradiction is the thesis."),
        "inference": (
            "The text implies that, without flying buttresses, a cathedral with very large windows would",
            ["have required a wooden rather than a stone ceiling",
             "have been at risk of collapse from the outward thrust of its vault",
             "have been considered ugly by its contemporaries",
             "have admitted even more light than the cathedrals that were actually built"],
            1,
            ["Wooden ceilings are not discussed.",
             "Correct. A tall wall with big windows is 'a wall waiting to fall' under the vault's outward push.",
             "Appearance is not the issue; stability is.",
             "Such a building would have fallen, not admitted more light."],
            "Large windows weaken a wall against outward thrust."),
        "structure": (
            "The author includes the critic's complaint about 'crutches' in order to",
            ["argue that medieval critics understood engineering better than builders did",
             "suggest that the buttresses were a temporary fix that was later removed",
             "explain the origin of the term 'flying buttress' in medieval usage",
             "acknowledge contemporary skepticism before affirming the solution's success"],
            3,
            ["The critic is answered by 'But the crutches worked.'",
             "The buttresses remained and the churches stood for centuries.",
             "The term's origin is not explained.",
             "Correct. The complaint is raised and then rebutted."],
            "The complaint sets up the vindication."),
        "wic": (
            "As used in the text, the word “afford” most nearly means",
            ["pay for", "accommodate without failing", "supply to others", "be willing to risk"],
            1,
            ["Money is not the issue.",
             "Correct. A thick wall could structurally bear only small windows.",
             "Supplying is not the sense.",
             "Risk is not quite the sense; capacity is."],
            "The windows a wall 'could afford' are those it could bear."),
        "evidence": (
            "Which quotation best explains why thick walls limited window size?",
            ["'the thicker the wall needed to resist that push, the smaller the windows it could afford'",
             "'They wanted walls that soared and windows that filled with colored light'",
             "'Half-arches of stone, later called flying buttresses, leaned against the upper walls from the exterior'",
             "'their interiors lit like no stone buildings before them'"],
            0,
            ["Correct. This states the trade-off between wall thickness and window size.",
             "This states the goal, not the constraint.",
             "This describes the solution.",
             "This describes the result."],
            "The trade-off sentence is the direct explanation."),
    },
    {
        "id": "free_sample", "title": "The Price of a Gift",
        "text": (
            "Grocery stores do not give away cubes of cheese on toothpicks out of "
            "generosity. The practice exploits one of the most reliable regularities in "
            "human behavior: a person who receives something, even something trivial and "
            "unrequested, feels obliged to give something back. In one field experiment, "
            "waiters who left a single mint with the bill saw tips rise by about three "
            "percent. Two mints raised tips by fourteen percent. The most striking result "
            "came when the waiter left one mint, began to walk away, then turned back and "
            "offered a second 'for you especially.' Tips rose by twenty-three percent, "
            "though the customers received exactly what the two-mint group had received. "
            "The difference lay in the apparent intention. A gift that seems personal "
            "creates a larger debt than one that seems routine. The obligation operates "
            "below the level of argument; customers who were later told about the "
            "experiment generally insisted the mints had not affected them. "
            "Anthropologists have documented the same pull in societies with no "
            "restaurants and no mints. The gift, it seems, has always come with a "
            "string."),
        "main_idea": (
            "Which choice best states the main idea of the text?",
            ["Restaurants can reliably increase their tips by instructing waiters to leave exactly two mints with every bill they present.",
             "Receiving a gift, especially one that seems personal, creates an obligation that shapes behavior without people's awareness.",
             "Customers who are told about experiments on tipping become more generous because they appreciate the researchers' honesty.",
             "Grocery stores give away free samples primarily because shoppers are more likely to buy products they have already tasted."],
            1,
            ["Two mints were not the most effective condition, and the passage is about the general principle.",
             "Correct. The experiment, the role of apparent intention, and the unconscious nature of the pull all support this.",
             "Informed customers denied any effect; generosity is not mentioned.",
             "Tasting is not the explanation the text gives; reciprocity is."],
            "Reciprocity, intensified by perceived intention and operating unconsciously, is the thesis."),
        "inference": (
            "The text suggests that the 'for you especially' group tipped more than the two-mint group because",
            ["the second mint appeared to reflect a personal decision rather than a policy",
             "they received a greater number of mints than the two-mint group had received",
             "the waiter spent more time at their table than at the other tables",
             "they had been informed about the experiment before the meal began"],
            0,
            ["Correct. 'The difference lay in the apparent intention'; the gift seemed personal.",
             "The text says they received 'exactly what the two-mint group had received.'",
             "Time at the table is not mentioned.",
             "Customers were told afterward, not before."],
            "Perceived personal intention enlarged the sense of debt."),
        "structure": (
            "The reference to anthropologists in the second-to-last sentence serves to",
            ["introduce evidence that contradicts the results of the restaurant experiment",
             "explain why some societies developed without restaurants",
             "suggest that the pattern is not limited to one setting or culture",
             "shift the discussion to the history of mints as a confection"],
            2,
            ["The anthropological evidence agrees with the experiment.",
             "The absence of restaurants is incidental.",
             "Correct. 'The same pull' appears in very different societies, showing generality.",
             "Mints are not the topic."],
            "The sentence broadens the finding beyond restaurants."),
        "wic": (
            "As used in the text, the word “exploits” most nearly means",
            ["treats unfairly", "performs heroically", "explores in detail", "makes use of"],
            3,
            ["The sense is strategic use, not mistreatment.",
             "Heroism is irrelevant.",
             "Exploration is not meant.",
             "Correct. The practice takes advantage of a behavioral regularity."],
            "'Exploits' here means takes advantage of."),
        "evidence": (
            "Which detail best supports the claim that the obligation operates 'below the level of argument'?",
            ["Customers who learned of the experiment insisted the mints had not influenced them.",
             "Two mints raised tips by fourteen percent compared with the group that received none.",
             "Grocery stores give away cheese on toothpicks to shoppers.",
             "Anthropologists have documented the same pull in other societies."],
            0,
            ["Correct. Denying an effect that the data show demonstrates it operates unconsciously.",
             "This shows the effect's size, not its unconscious nature.",
             "This is an example of the practice.",
             "This shows generality, not unconsciousness."],
            "The denial by affected customers is the evidence."),
    },
    {
        "id": "lichen_rock", "title": "First on the Stone",
        "text": (
            "On a fresh lava flow or a boulder newly exposed by a retreating glacier, the "
            "first living thing to arrive is usually something most people would not "
            "notice: a gray or orange crust, flat as paint, called a lichen. A lichen is "
            "not one organism but two. A fungus provides the structure and anchors itself "
            "to bare rock; algae living inside it carry out photosynthesis and supply "
            "sugars to both. Neither partner could survive alone on stone, but together "
            "they can live where there is no soil at all. Over decades the lichen "
            "secretes weak acids that etch the rock surface, and its own dead layers mix "
            "with windblown dust to form the first thin smear of soil. Mosses follow, "
            "then grasses, then shrubs whose roots pry the rock apart further. The lichen "
            "is long gone by the time trees arrive, shaded out by the forest it made "
            "possible. Ecologists call it a pioneer species, and like many pioneers it "
            "does not get to enjoy what it built."),
        "main_idea": (
            "Which choice best states the main idea of the text?",
            ["Lichens are the only organisms capable of surviving on bare rock, and they persist there long after forests have grown.",
             "Mosses and grasses are more important than lichens in creating soil because they arrive earlier on newly exposed rock.",
             "Lichens, a fungus-algae partnership, begin the process that turns bare rock into soil for other life.",
             "Fungi can survive on bare stone without any partner because they extract nutrients directly from the rock."],
            2,
            ["Lichens are shaded out once trees arrive.",
             "Lichens arrive first, before mosses and grasses.",
             "Correct. The passage explains the partnership and the lichen's role in starting soil formation.",
             "The text says neither partner could survive alone."],
            "The lichen as soil-making pioneer is the thesis."),
        "inference": (
            "It can reasonably be inferred that the fungus benefits from its partnership with algae by",
            ["receiving the sugars that the algae produce",
             "gaining protection from windblown dust",
             "obtaining the weak acids needed to etch rock",
             "being shaded from direct sunlight on the stone"],
            0,
            ["Correct. The algae 'supply sugars to both.'",
             "Dust is a soil ingredient, not a threat.",
             "The lichen secretes acids; they are not supplied by the algae.",
             "Shading is what eventually kills the lichen."],
            "Sugars from photosynthesis are the fungus's gain."),
        "structure": (
            "The author describes the lichen as not getting 'to enjoy what it built' in order to",
            ["argue that lichens deserve more legal protection than forests do",
             "end with a reflective note on the irony of the pioneer's fate",
             "explain the chemical process by which acids etch stone",
             "introduce the next stage of forest growth after trees"],
            1,
            ["No protection argument is made.",
             "Correct. The closing remark reflects on how the lichen is displaced by what it enabled.",
             "The chemistry came earlier.",
             "The passage ends there."],
            "The ending is a reflective flourish."),
        "wic": (
            "In the context of the text, “smear” most nearly means",
            ["thin layer", "false accusation", "dirty mark", "medical sample"],
            0,
            ["Correct. The first soil is a thin coating on the rock.",
             "No accusation is involved.",
             "Dirtiness is not the sense.",
             "The medical sense does not apply."],
            "A 'thin smear of soil' is a thin layer."),
        "evidence": (
            "Which detail best supports the claim that lichens create soil?",
            ["Their dead layers mix with windblown dust to form the first soil.",
             "They are flat as paint and gray or orange in color.",
             "Neither partner could survive alone on bare stone.",
             "Shrubs' roots pry the rock apart further."],
            0,
            ["Correct. This describes the lichen's direct contribution to soil.",
             "Appearance is irrelevant to soil.",
             "This is about the partnership, not soil.",
             "This is a later stage, not the lichen's role."],
            "Dead lichen plus dust is the first soil."),
    },
    {
        "id": "blank_coast", "title": "The Unfinished Coast",
        "text": (
            "My master, Mr. Hallam, had drawn maps for the Admiralty for thirty years, and "
            "in all that time, he told me, he had never once drawn a line he had not been "
            "given reason to believe. I was nineteen and thought this a modest ambition. "
            "It was my task that winter to copy the surveys sent back from the northern "
            "voyage, and I came to a stretch of coast where the ship's log simply stopped: "
            "fog for nine days, then open sea. The chart before me showed a gap. I "
            "proposed to close it with a gentle curve, as any sensible coast would run. "
            "Mr. Hallam took the pen from my hand. 'A sailor who trusts that curve,' he "
            "said, 'will put his ship on rocks we have not seen, and he will do it in the "
            "dark, and he will do it because you were tidy.' He left the gap. I have "
            "since drawn a great many maps, and some of them have gaps, and I have come "
            "to think of the gaps as the most honest lines on them."),
        "main_idea": (
            "Which choice best states the main idea of the text?",
            ["A mapmaker's refusal to invent a coastline taught the narrator that honesty about ignorance outweighs a finished look.",
             "The narrator's master was so cautious in his work that he failed to complete most of the charts the Admiralty had commissioned from him.",
             "A northern voyage failed to survey a stretch of coast because of nine days of fog, forcing the Admiralty to send a second expedition.",
             "The narrator came to believe that a map with gaps is useless to sailors and should never be issued by the Admiralty."],
            0,
            ["Correct. Hallam leaves the gap, and the narrator comes to see gaps as 'the most honest lines.'",
             "Nothing suggests Hallam failed to complete charts.",
             "No second expedition is mentioned; the fog is the occasion, not the subject.",
             "The narrator values gaps, not rejects them."],
            "Honesty about what is unknown is the lesson."),
        "inference": (
            "The narrator's remark that he 'thought this a modest ambition' suggests that at nineteen he",
            ["shared Hallam's conviction about the importance of accuracy in charts",
             "believed Hallam should have been promoted to a higher post long before",
             "doubted that Hallam had really worked for the Admiralty for thirty years",
             "underestimated how demanding Hallam's standard of honesty actually was"],
            3,
            ["He proposes to invent a curve, so he did not yet share the conviction.",
             "Promotion is not mentioned.",
             "He does not doubt Hallam's history.",
             "Correct. Calling it 'modest' shows he did not yet grasp its difficulty, as the episode then proves."],
            "The later lesson reveals the remark's youthful misjudgment."),
        "structure": (
            "Hallam's speech functions in the text to",
            ["reveal that Hallam himself had once put a ship on rocks through his own carelessness",
             "make vivid the real consequences of the narrator's seemingly harmless proposal",
             "demonstrate that Hallam was unreasonably harsh toward his young apprentices",
             "explain the proper technique for drawing an accurate coastline on a chart"],
            1,
            ["No such confession is made.",
             "Correct. The sailor on the rocks 'in the dark' shows what a tidy curve could cost.",
             "The speech is firm but the narrator credits the lesson.",
             "No technique is explained."],
            "The speech turns a drafting habit into a matter of life and death."),
        "wic": (
            "As used in the text, the word “tidy” most nearly means",
            ["orderly in personal habits", "considerable in amount", "eager for neatness", "clean and well washed"],
            2,
            ["Personal habits are not at issue.",
             "Quantity is irrelevant.",
             "Correct. The narrator wanted the chart to look complete and neat.",
             "Cleanliness is not meant."],
            "Hallam accuses the narrator of valuing neatness over truth."),
        "evidence": (
            "Which quotation best supports the idea that the narrator's view of maps changed permanently?",
            ["'I have come to think of the gaps as the most honest lines on them'",
             "'It was my task that winter to copy the surveys sent back from the northern voyage'",
             "'I was nineteen and thought this a modest ambition'",
             "'Mr. Hallam took the pen from my hand'"],
            0,
            ["Correct. The present-tense reflection shows a lasting change.",
             "This describes the task.",
             "This describes the earlier, unchanged view.",
             "This is the moment of intervention, not its lasting effect."],
            "The closing reflection states the enduring change."),
    },
    {
        "id": "hot_hand", "title": "Streaks",
        "text": (
            "Basketball fans share a conviction: a player who has made several shots in a "
            "row is 'hot' and more likely to make the next one. In the 1980s, researchers "
            "examined thousands of shots from professional games and reported that the "
            "conviction was an illusion. A player's chance of making a shot after a "
            "string of hits was no higher than after a string of misses. Streaks were "
            "simply what randomness looks like, the way a fair coin produces runs of "
            "heads. The finding became a textbook example of how people see patterns in "
            "noise. Then, three decades later, two economists noticed a subtle flaw. If "
            "you select, from a random sequence, the shots that follow three hits, the "
            "remaining pool is slightly depleted of hits, so the expected success rate in "
            "that selected pool is actually below the player's overall average. Measured "
            "against the correct baseline, the original data showed a modest hot hand "
            "after all—a few percentage points, not the dramatic effect fans imagine, "
            "but real. The textbook example of a bias turned out to contain a bias of its "
            "own."),
        "main_idea": (
            "Which choice best states the main idea of the text?",
            ["Basketball players who have made several shots in a row are far more likely to make their next shot than even their fans realize.",
             "A famous finding that shooting streaks are illusory was itself undermined by a statistical error, revealing a small real effect.",
             "Researchers in the 1980s proved beyond any doubt that streaks in basketball are the product of pure randomness.",
             "Economists have shown that the hot hand is a much larger effect than coaches and fans have traditionally believed."],
            1,
            ["The effect is 'a few percentage points,' smaller than fans imagine.",
             "Correct. The passage recounts the original finding, the flaw, and the modest real effect.",
             "The finding was later overturned.",
             "The effect is smaller, not larger, than fans believe."],
            "The reversal of a famous finding is the story."),
        "inference": (
            "Based on the text, the original researchers' error was that they",
            ["compared streak shots to a baseline that their selection method had biased downward",
             "examined too few shots to detect any effect at all",
             "relied on the impressions of fans and coaches rather than on records of actual professional games",
             "failed to account for differences in skill between individual players"],
            0,
            ["Correct. Selecting shots after three hits depletes the pool of hits, lowering the expected rate.",
             "They examined thousands of shots.",
             "They used records of professional games.",
             "Player skill is not the flaw identified."],
            "The selection effect on the baseline is the flaw."),
        "structure": (
            "The author's final sentence serves to",
            ["introduce a third study of the hot hand",
             "argue that textbooks should be rewritten",
             "highlight the irony of the episode",
             "restate the original 1980s finding"],
            2,
            ["No third study follows.",
             "No such argument is made.",
             "Correct. A famous example of bias containing its own bias is the irony.",
             "The sentence comments on the reversal, not the original finding."],
            "The sentence is an ironic capstone."),
        "wic": (
            "As used in the text, the word “depleted” most nearly means",
            ["exhausted from effort", "emptied completely", "lowered in value", "reduced in supply"],
            3,
            ["Fatigue is irrelevant.",
             "The pool is 'slightly' depleted, not emptied.",
             "Value is not the sense.",
             "Correct. The remaining pool has fewer hits than average."],
            "'Depleted of hits' means having fewer hits."),
        "evidence": (
            "Which detail best supports the claim that the hot hand is real but small?",
            ["The corrected analysis showed an effect of a few percentage points.",
             "A fair coin produces runs of heads.",
             "Fans believe a player who has made several shots is hot.",
             "The finding became a textbook example of seeing patterns in noise."],
            0,
            ["Correct. 'A few percentage points ... but real' is the size and reality of the effect.",
             "This illustrates randomness, not the effect.",
             "This is belief, not evidence.",
             "This concerns the original finding's reputation."],
            "The few-percentage-points detail is the evidence."),
    },
    {
        "id": "pencil_lead", "title": "Not Lead at All",
        "text": (
            "The 'lead' in a pencil has never been lead. The substance is graphite, a soft "
            "form of carbon, and the confusion dates to the 1560s, when a storm in "
            "northern England uprooted a tree and exposed a deposit of shiny black "
            "mineral beneath it. Shepherds used it to mark their sheep; they assumed it "
            "was a kind of lead and called it so. The deposit turned out to be unusually "
            "pure, and for two centuries it was the only known source of graphite solid "
            "enough to be cut into sticks. The mine was guarded, flooded between "
            "diggings, and its output smuggled, since the mineral was also useful for "
            "lining the molds in which cannonballs were cast. The modern pencil arrived "
            "when a French inventor, cut off from English graphite by war, ground up "
            "impure graphite, mixed it with clay, and fired the mixture in a kiln. "
            "Varying the clay changed the hardness. The product of a wartime shortage "
            "became the standard, and the pure English deposit, no longer necessary, was "
            "exhausted and forgotten."),
        "main_idea": (
            "Which choice best states the main idea of the text?",
            ["Pencils were originally made from the metal lead until the dangers of lead poisoning became widely known in the 1560s.",
             "The French inventor who mixed graphite with clay was attempting to improve the casting of cannonballs during a war.",
             "The pencil's misnamed core has a history shaped by chance discovery, a guarded monopoly, and wartime invention.",
             "English shepherds in the sixteenth century were the first people to use graphite for writing and drawing on paper."],
            2,
            ["The text says the lead 'has never been lead.'",
             "The inventor was making pencils, not cannonballs.",
             "Correct. The passage follows graphite from the storm to the mine to the clay process.",
             "Shepherds marked sheep; paper writing is not mentioned."],
            "The history of the pencil core is the thread."),
        "inference": (
            "The text suggests that the English mine was guarded mainly because",
            ["its graphite had military as well as civilian uses",
             "pencils had become extremely valuable luxury items",
             "the shepherds who found it refused to share the deposit",
             "the mine was in constant danger of flooding"],
            0,
            ["Correct. The mineral lined cannonball molds, which explains the guarding and smuggling.",
             "Pencil prices are not mentioned.",
             "The shepherds are not said to control the mine.",
             "Flooding was done deliberately as a security measure."],
            "Military usefulness explains the security."),
        "structure": (
            "The text is organized primarily as",
            ["a comparison between English and French methods of making pencils",
             "a chronological account of how an everyday object came to be",
             "an argument that graphite should be renamed to avoid confusion",
             "a description of the chemical differences between lead and graphite"],
            1,
            ["The French method appears only as a stage in the story.",
             "Correct. The passage proceeds from the 1560s through two centuries to the modern pencil.",
             "No renaming is proposed.",
             "Chemistry is mentioned only in passing."],
            "The passage is a history."),
        "wic": (
            "As used in the text, the phrase “cut off from” most nearly means",
            ["severed physically from", "interrupted while speaking about", "denied access to", "excluded from an inheritance of"],
            2,
            ["No physical severing is meant.",
             "Speech is irrelevant.",
             "Correct. War prevented the inventor from obtaining English graphite.",
             "Inheritance is irrelevant."],
            "To be cut off from a supply is to be unable to get it."),
        "evidence": (
            "Which quotation best supports the claim that the French method made the English deposit unnecessary?",
            ["'the pure English deposit, no longer necessary, was exhausted and forgotten'",
             "'The deposit turned out to be unusually pure, and for two centuries it was the only known source'",
             "'The mine was guarded, flooded between diggings, and its output smuggled'",
             "'ground up impure graphite, mixed it with clay, and fired the mixture in a kiln'"],
            0,
            ["Correct. This states the consequence directly.",
             "This describes the deposit's earlier importance.",
             "This describes security, not obsolescence.",
             "This describes the method without stating its effect on the English mine."],
            "The 'no longer necessary' clause is the direct support."),
    },
    {
        "id": "hot_streets", "title": "Islands of Heat",
        "text": (
            "On a summer night, the center of a large city can be as much as seven "
            "degrees Celsius warmer than the farmland an hour's drive away. "
            "Meteorologists call the phenomenon an urban heat island, and its causes are "
            "not mysterious. Asphalt and dark roofing absorb sunlight by day and release "
            "the heat slowly after dark. Buildings block the wind that would carry warmth "
            "away. Pavement sheds rain into drains instead of letting it soak into soil, "
            "so the city loses the cooling that evaporation from damp ground would "
            "provide. Engines and air conditioners add their own exhaust heat. What is "
            "less obvious is how unevenly the burden falls. In one city's survey, "
            "neighborhoods with the fewest trees were on average four degrees warmer "
            "than those with the most, and those neighborhoods were, almost without "
            "exception, the poorest. Planting trees is slow, but studies of streets that "
            "received them suggest that a mature canopy can erase much of the difference, "
            "and that the shade arrives, for once, exactly where it is needed most."),
        "main_idea": (
            "Which choice best states the main idea of the text?",
            ["Urban heat islands are caused mainly by the exhaust from engines and air conditioners, which raise temperatures by seven degrees.",
             "Meteorologists remain uncertain about why city centers are warmer at night than the surrounding countryside is.",
             "Planting trees in cities is too slow a process to have any measurable effect on summer temperatures in poor neighborhoods.",
             "Cities are hotter than their surroundings for known reasons, and the excess heat falls hardest on neighborhoods with few trees."],
            3,
            ["Exhaust is one of several causes, and seven degrees is the total difference.",
             "The text says the causes 'are not mysterious.'",
             "Studies suggest a mature canopy can erase much of the difference.",
             "Correct. The passage lists the causes and then turns to the uneven burden and the tree remedy."],
            "Causes plus inequity is the structure of the passage."),
        "inference": (
            "The text suggests that rain falling on a city is less cooling than rain falling on farmland because",
            ["on pavement it runs into drains before it can evaporate from the ground",
             "city air is too warm for the rain to reach the ground",
             "tall buildings block most of the rain from ever reaching the streets below",
             "drains carry the water to reservoirs where it is heated"],
            0,
            ["Correct. Pavement 'sheds rain into drains,' losing the cooling of evaporation from soil.",
             "Rain reaches the ground; the issue is where it goes.",
             "Buildings block wind, not rain.",
             "Reservoirs are not mentioned."],
            "Lost evaporation from drained pavement is the mechanism."),
        "structure": (
            "The sentence beginning 'What is less obvious' marks a shift from",
            ["describing summer conditions to describing winter conditions",
             "explaining the causes of the heat island to examining its uneven effects",
             "the author's own casual observations to the formal findings of meteorologists",
             "a discussion of large cities to a discussion of small towns"],
            1,
            ["Winter is never discussed.",
             "Correct. After the list of causes, the text turns to who bears the heat.",
             "Meteorologists were cited earlier.",
             "Small towns are not discussed."],
            "The sentence pivots from cause to distribution."),
        "wic": (
            "Which choice best captures the meaning of “sheds” as used in the text?",
            ["loses hair or skin", "stores in a small building", "gives off light", "diverts away"],
            3,
            ["The biological sense does not apply.",
             "The building sense is irrelevant.",
             "Light is not involved.",
             "Correct. Pavement channels rain off into drains."],
            "To shed rain is to carry it off."),
        "evidence": (
            "Which detail best supports the claim that the burden of heat falls unevenly?",
            ["Neighborhoods with the fewest trees were four degrees warmer and almost always the poorest.",
             "Asphalt and dark roofing absorb sunlight by day and release it slowly at night.",
             "City centers can be seven degrees warmer than farmland an hour's drive away.",
             "A mature tree canopy can erase much of the temperature difference between neighborhoods over time."],
            0,
            ["Correct. The temperature gap aligned with poverty is the unevenness.",
             "This is a cause, not distribution.",
             "This is the overall city-country gap, not the gap within the city.",
             "This is the remedy, not the problem."],
            "The tree-poverty-temperature correlation is the evidence."),
    },
    {
        "id": "the_clock", "title": "Division",
        "text": (
            "'You take the clock,' Dana said. 'You always liked it.' 'I never liked it,' "
            "said Ben. 'I wound it because nobody else would.' They were sitting on the "
            "floor of their mother's apartment with the lists between them, hers typed, "
            "his on the back of an envelope. It was the fourth hour. They had agreed "
            "easily on the furniture, which neither wanted, and the photographs, which "
            "they would scan and share, and had come, as they had both known they would, "
            "to the small things: the clock, the chipped blue bowl, the cheap ring their "
            "mother had worn in place of the good one she kept in a drawer. 'Then I'll "
            "take it,' Dana said, and wrote it down, and Ben watched her write and felt, "
            "absurdly, that something had been taken from him. 'Or we could sell it,' she "
            "said, not looking up. 'No,' he said, too quickly, and they both heard it. "
            "She crossed it off her list. He picked up the clock. It was heavier than he "
            "remembered."),
        "main_idea": (
            "Which choice best describes the central concern of the text?",
            ["Two siblings discover, while dividing their mother's belongings, that their attachments are stronger than they had admitted.",
             "Two siblings argue bitterly over a valuable clock, and the dispute reveals a long-standing rivalry between them that dates to childhood.",
             "Two siblings efficiently divide their mother's possessions by assigning each item to whichever of them has the better claim to it.",
             "A brother agrees to sell his mother's clock because he has never liked it and has no use for it in his own apartment."],
            0,
            ["Correct. Ben's 'No,' said 'too quickly,' exposes an attachment he had denied.",
             "There is no bitterness and no rivalry; the clock is one of the 'small things,' not a valuable item.",
             "The small things are exactly where easy division fails.",
             "He refuses to sell it."],
            "Unacknowledged attachment surfacing is the heart of the scene."),
        "inference": (
            "Ben's reaction when Dana writes down the clock most strongly suggests that",
            ["he believes Dana is taking more than her fair share of the belongings",
             "he intends to sell the clock and keep the money for himself",
             "he wants the clock more than he has acknowledged, even to himself",
             "he is relieved to be free of the duty of winding it"],
            2,
            ["Fairness is not raised.",
             "He refuses to sell it.",
             "Correct. He feels 'absurdly, that something had been taken from him' after denying he liked it.",
             "Relief is the opposite of what he feels."],
            "The sense of loss contradicts his stated indifference."),
        "structure": (
            "The description of the two lists, 'hers typed, his on the back of an envelope,' serves to",
            ["show that Dana is more attached to the belongings than Ben is",
             "suggest a contrast in the siblings' approaches to the task",
             "explain why the division has taken four hours",
             "reveal that Ben has not taken the task seriously"],
            1,
            ["Attachment is not what the lists indicate.",
             "Correct. The detail quietly contrasts Dana's organization with Ben's improvisation.",
             "The lists do not explain the duration.",
             "Ben's reaction to the clock shows he is deeply invested."],
            "The lists characterize the two siblings."),
        "wic": (
            "As used in the text, the word “absurdly” most nearly means",
            ["in a comical manner", "loudly and dramatically", "with deliberate exaggeration", "in a way that defied reason"],
            3,
            ["Nothing is comic here.",
             "The feeling is silent.",
             "The feeling is involuntary, not exaggerated.",
             "Correct. Ben knows the feeling makes no sense, since Dana offered him the clock."],
            "'Absurdly' marks the feeling as irrational."),
        "evidence": (
            "Which quotation best supports the idea that the siblings had anticipated difficulty with the smaller items?",
            ["'had come, as they had both known they would, to the small things'",
             "'They had agreed easily on the furniture, which neither wanted, and the photographs'",
             "'It was the fourth hour'",
             "'It was heavier than he remembered'"],
            0,
            ["Correct. 'As they had both known they would' shows the anticipation.",
             "This describes the easy part.",
             "This shows duration, not anticipation.",
             "This is Ben's final perception."],
            "The clause about knowing is the direct evidence."),
    },
]

PAIRED3 = [
    {
        "id": "remote_work",
        "text_a": (
            "Supporters of remote work point to a decade of surveys in which employees "
            "report doing more in fewer hours when they work from home. The savings are not "
            "mysterious: no commute, fewer interruptions, and the freedom to schedule deep "
            "work when one's attention is sharpest. Companies that measured output rather "
            "than hours, the author notes, found that productivity held steady or rose "
            "when offices closed, while turnover fell. The office, on this view, was never "
            "where the work got done; it was where the work got watched. A firm that "
            "insists on attendance is paying for supervision it does not need and losing "
            "workers who can find flexibility elsewhere."),
        "text_b": (
            "The productivity gains reported by remote workers are real but misleading, "
            "this author argues, because they measure the wrong period. In the first year "
            "of working from home, employees drew on relationships and shared knowledge "
            "built over years in the office. The question is what happens when that stock "
            "runs down. Studies tracking new hires who never met their colleagues in "
            "person find slower skill growth and weaker ties to the people who could help "
            "them. Individual output may hold up; the collective capacity to train, "
            "mentor, and improvise together erodes quietly. The office, the author "
            "concludes, was less a place of supervision than a place of apprenticeship."),
        "questions": [
            ("Which choice best describes the relationship between the two texts?",
             ["Text 2 accepts the evidence cited in Text 1 but argues that it overlooks longer-term costs.",
              "Text 2 rejects the surveys cited in Text 1 as fabrications produced by supporters of remote work.",
              "Text 1 and Text 2 agree that the office served mainly to supervise employees.",
              "Text 1 and Text 2 both argue that remote work should be abandoned entirely."],
             0,
             ["Correct. Text 2 calls the gains 'real but misleading' and points to costs that appear later.",
              "Text 2 calls the gains real, not fabricated.",
              "Text 2 calls the office 'a place of apprenticeship,' not supervision.",
              "Text 1 favors remote work, and Text 2 does not call for abandoning it."],
             "Text 2 grants the data and shifts the time frame."),
            ("How would the author of Text 2 most likely respond to Text 1's claim that the office was 'where the work got watched'?",
             ["by agreeing that supervision was the office's only real purpose",
              "by arguing that the office's more important role was developing workers' skills and relationships",
              "by insisting that remote employees are in fact monitored far more closely than office workers ever were",
              "by denying that any companies ever measured output rather than hours"],
             1,
             ["Text 2 explicitly rejects supervision as the office's main role.",
              "Correct. Text 2 says the office 'was less a place of supervision than a place of apprenticeship.'",
              "Monitoring of remote workers is not discussed in Text 2.",
              "Text 2 does not dispute the output measurements."],
             "Text 2 reframes the office as a site of apprenticeship."),
            ("Based on the texts, both authors would most likely agree that",
             ["new hires are better served by remote work than by working alongside colleagues in an office",
              "companies should return to measuring hours rather than output",
              "individual productivity did not decline when employees began working from home",
              "the relationships built in offices are of little value to employees"],
             2,
             ["Text 2 says new hires fare worse remotely.",
              "Neither text advocates measuring hours.",
              "Correct. Text 1 reports steady or rising productivity, and Text 2 says 'individual output may hold up.'",
              "Text 2 values those relationships highly."],
             "Both accept that individual output held up."),
        ],
    },
    {
        "id": "wolf_return",
        "text_a": (
            "When wolves were returned to a mountain national park after seventy years' "
            "absence, the author observes, the landscape itself seemed to change. Elk, "
            "which had grazed riverbanks bare without fear, began to move and to avoid "
            "open valleys. Willows and aspens recovered along the streams, beavers "
            "returned to build dams in the slower water, and songbirds followed the new "
            "cover. Ecologists describe the pattern as a trophic cascade: the effect of a "
            "top predator flowing down through the food web to reshape plants and even "
            "the course of rivers. The wolves, in this account, did not merely add a "
            "species. They restored a process that the park had been missing."),
        "text_b": (
            "The story of wolves remaking a park is appealing, this author concedes, but "
            "the evidence is thinner than the popular version suggests. Willow recovery "
            "along some streams coincided with the wolves' return, yet other streams show "
            "no recovery at all, and the elk population was also being reduced by hunting "
            "outside the park and by harsh winters. Separating the wolves' contribution "
            "from these other factors has proven difficult. The author does not deny that "
            "predators matter. The concern is that a tidy narrative, repeated often "
            "enough, substitutes for the messier work of measurement, and that managers "
            "elsewhere may expect results that a single reintroduction cannot guarantee."),
        "questions": [
            ("Which choice best describes how Text 2 responds to Text 1?",
             ["It denies that willows or beavers returned to the park after the wolves did.",
              "It argues that wolves should never have been reintroduced to the park in the first place.",
              "It offers additional evidence that confirms the trophic cascade described in Text 1.",
              "It questions whether the changes Text 1 describes can be attributed to wolves alone."],
             3,
             ["Text 2 accepts that willow recovery occurred along some streams.",
              "Text 2 takes no position against reintroduction.",
              "Text 2 complicates rather than confirms the account.",
              "Correct. Text 2 points to hunting and harsh winters as other factors that are hard to separate."],
             "Text 2's point is about attribution, not denial."),
            ("The author of Text 2 would most likely say that the phrase 'the landscape itself seemed to change' in Text 1",
             ["captures an appealing story that may outrun the available evidence",
              "understates the dramatic effect that the wolves actually had on the park",
              "correctly identifies the wolves as the sole cause of the willow recovery",
              "ignores the important role that beavers played in reshaping the streams"],
             0,
             ["Correct. Text 2 calls the story 'appealing' but the evidence 'thinner than the popular version suggests.'",
              "Text 2 thinks the effect is overstated, not understated.",
              "Text 2 doubts that wolves were the sole cause.",
              "Beavers are part of Text 1's account, and Text 2 does not raise them."],
             "Text 2 regards the dramatic framing as a tidy narrative."),
            ("Based on the texts, the two authors would most likely agree that",
             ["hunting outside the park had no effect on the elk population",
              "predators can have effects that extend beyond the animals they eat",
              "the wolves' return fully explains the recovery of streamside vegetation",
              "reintroducing wolves elsewhere will reliably produce the same results"],
             1,
             ["Text 2 cites hunting as a factor.",
              "Correct. Text 1 describes a cascade, and Text 2 'does not deny that predators matter.'",
              "Text 2 disputes a full explanation.",
              "Text 2 warns against exactly this expectation."],
             "Both grant that predators matter beyond their prey."),
            ("Which choice best states a point on which Text 2 directly challenges Text 1?",
             ["whether elk had grazed the riverbanks before the wolves returned",
              "whether ecologists are correct to use the term trophic cascade for patterns of this kind",
              "whether every stream in the park showed willow recovery after the wolves returned",
              "whether wolves had been absent from the park for seventy years"],
             2,
             ["Neither text disputes the earlier grazing.",
              "The term is not contested.",
              "Correct. Text 2 notes that 'other streams show no recovery at all.'",
              "The absence is not disputed."],
             "The uneven stream recovery is Text 2's factual challenge."),
        ],
    },
    {
        "id": "by_heart",
        "text_a": (
            "Requiring students to memorize poems, the author argues, is not an antique "
            "practice but a gift. A poem carried in memory is available anywhere: on a "
            "bus, in a hospital waiting room, at a graveside. Students who learn lines by "
            "heart come to feel the rhythm of the language from the inside, in a way that "
            "reading silently never provides, and they acquire a store of phrases that "
            "will shape how they write and speak for the rest of their lives. The "
            "objection that memorization is mere rote misses the point. One does not "
            "memorize a poem instead of understanding it. One memorizes it in order to "
            "understand it slowly, over years."),
        "text_b": (
            "Memorization has its pleasures, this author grants, but classroom time is "
            "scarce and should go where it does the most good. An hour spent drilling "
            "lines is an hour not spent discussing what a poem means, comparing it with "
            "another, or writing in response to it. The students who thrive at recitation "
            "are often those who already love the material; for the rest, the assignment "
            "confirms a suspicion that poetry is a performance of obedience. If the goal "
            "is a lifelong relationship with poems, the author suggests, it is better "
            "served by teaching students how to find and read new ones than by fixing a "
            "few old ones in their heads."),
        "questions": [
            ("Which choice best describes the relationship between the texts?",
             ["They agree that memorization is the best way to understand a poem.",
              "They disagree about whether memorizing poems is a good use of class time.",
              "Text 2 provides evidence that supports the central claim of Text 1.",
              "They disagree about whether poetry should be taught in schools at all."],
             1,
             ["Text 2 prefers discussion and writing to memorization.",
              "Correct. Text 1 calls memorization a gift; Text 2 says the time is better spent otherwise.",
              "Text 2 argues against Text 1's recommendation.",
              "Both assume poetry belongs in school."],
             "The dispute is over the value of memorization as instruction."),
            ("How would the author of Text 1 most likely respond to Text 2's claim that memorization is 'a performance of obedience'?",
             ["by arguing that memorization is a route to understanding rather than a substitute for it",
              "by conceding that memorization is only appropriate for students who already love poetry on their own",
              "by agreeing that class time should be spent on discussion rather than on recitation",
              "by denying that any students ever find memorization difficult or unpleasant"],
             0,
             ["Correct. Text 1 says one memorizes 'in order to understand it slowly, over years.'",
              "Text 1 makes no such concession.",
              "Text 1 defends memorization as class work.",
              "Text 1 does not address students' feelings about difficulty."],
             "Text 1's reply is that memorization serves understanding."),
            ("Both authors would most likely agree that",
             ["memorized poems are most useful in hospital waiting rooms",
              "students should be taught to find new poems rather than to memorize old ones",
              "the rhythm of a poem can only be felt by reciting it aloud",
              "a lasting relationship with poetry is a worthwhile goal of instruction"],
             3,
             ["Only Text 1 mentions waiting rooms.",
              "This is Text 2's position only.",
              "This is Text 1's position only.",
              "Correct. Text 1 speaks of phrases that last 'the rest of their lives,' and Text 2 of 'a lifelong relationship with poems.'"],
             "Both aim at a lifelong connection; they differ on means."),
        ],
    },
    {
        "id": "whose_artifacts",
        "text_a": (
            "Objects taken from their countries of origin during periods of conquest, the "
            "author argues, should be returned to the communities from which they came. A "
            "ceremonial mask displayed in a glass case thousands of miles from the people "
            "who made it has been severed from its meaning; it has become a decoration. "
            "The argument that large museums 'preserve' such objects for all humanity "
            "assumes that the original owners cannot be trusted with their own heritage, "
            "a claim that would be recognized as insulting in any other context. Return is "
            "not a loss to the world's knowledge. It is a correction, and the museums that "
            "make it will find their remaining collections easier to defend."),
        "text_b": (
            "The author agrees that many objects were acquired unjustly and that some "
            "should go home. But a blanket rule of return, the text cautions, would treat "
            "every case as identical when they are not. Some objects were purchased "
            "fairly; some come from peoples who no longer exist as a community; some are "
            "claimed by more than one modern nation. Large museums, whatever their "
            "origins, allow a visitor from anywhere to encounter the art of everywhere in "
            "a single afternoon, an experience with real value. The better path, the "
            "author suggests, is case-by-case negotiation, long-term loans, and shared "
            "custody, rather than a principle that sounds just and resolves nothing."),
        "questions": [
            ("Which choice best describes how Text 2 relates to Text 1?",
             ["It rejects Text 1's claim that any objects were acquired unjustly.",
              "It extends Text 1's argument to objects that were purchased fairly.",
              "It accepts part of Text 1's argument while objecting to its universal application.",
              "It agrees with Text 1 that museums should return every contested object to its country of origin."],
             2,
             ["Text 2 agrees many objects were acquired unjustly.",
              "Text 2 treats fair purchases as a reason against return.",
              "Correct. Text 2 agrees some objects should go home but rejects 'a blanket rule.'",
              "Text 2 opposes a universal rule."],
             "Partial agreement plus objection to a blanket rule is the relationship."),
            ("The author of Text 2 would most likely respond to Text 1's description of a mask as 'a decoration' by",
             ["noting that the museum encounter has value of its own even if some meaning is lost",
              "agreeing that the mask has no value whatsoever once removed from its original community",
              "arguing that masks of that kind were never actually used in ceremonies",
              "insisting that the mask should be destroyed rather than put on display"],
             0,
             ["Correct. Text 2 says encountering 'the art of everywhere' is 'an experience with real value.'",
              "Text 2 defends the museum experience.",
              "Text 2 does not dispute the objects' origins.",
              "Destruction is not suggested."],
             "Text 2 would defend the museum visit's value."),
            ("Based on the texts, the authors would most likely disagree about whether",
             ["some objects in museums were taken during periods of conquest",
              "a general principle of return is preferable to negotiating individual cases",
              "museums have any responsibility toward the communities that made the objects they hold",
              "ceremonial masks were made by specific communities"],
             1,
             ["Both accept this.",
              "Correct. Text 1 argues for return as a principle; Text 2 prefers case-by-case negotiation.",
              "Both accept some responsibility.",
              "Neither disputes this."],
             "Principle versus case-by-case is the disagreement."),
        ],
    },
    {
        "id": "clock_change",
        "text_a": (
            "Changing the clocks twice a year, the author argues, is a ritual whose costs "
            "have outlived its purpose. The shift was introduced to save fuel, but modern "
            "studies find the savings negligible, and the week after each change brings "
            "measurable increases in traffic accidents, heart attacks, and workplace "
            "injuries as millions of people lose an hour of sleep at once. Fixing the "
            "clock permanently to standard time, which matches the sun most closely, "
            "would end the disruption. The darker winter evenings some people fear would "
            "be no darker than they are now; the only change would be that nobody had to "
            "adjust."),
        "text_b": (
            "The author agrees that the twice-yearly change should end but argues that "
            "the clock should be fixed on the summer schedule instead. Most people are "
            "awake for far more hours after work than before it, and an extra hour of "
            "evening light is used: for exercise, for errands, for time outdoors with "
            "children. Evening light also reduces crime and road deaths in the hours when "
            "most people are traveling. Standard time, the text concedes, aligns better "
            "with the body's internal clock, but that benefit is largely theoretical for "
            "people who spend their mornings indoors anyway. The question is not which "
            "time is natural, but which one people will actually enjoy."),
        "questions": [
            ("Which choice best describes the relationship between the texts?",
             ["They agree the clock change should end but disagree about which time to keep.",
              "They disagree about whether the twice-yearly clock change causes any harm at all.",
              "Text 2 argues that the twice-yearly clock change should continue indefinitely.",
              "They agree that standard time should be adopted on a permanent basis."],
             0,
             ["Correct. Both oppose the change; Text 1 wants standard time and Text 2 wants summer time.",
              "Both accept that the change is harmful.",
              "Text 2 agrees the change should end.",
              "Text 2 prefers the summer schedule."],
             "Shared goal, different fixed time."),
            ("How would the author of Text 1 most likely respond to Text 2's emphasis on evening light?",
             ["by agreeing that evening light matters more than alignment with the sun",
              "by denying that people spend more waking hours after work than before it",
              "by arguing that the twice-yearly clock change should be kept to provide both kinds of benefit",
              "by pointing out that standard time matches the sun and the body's rhythms most closely"],
             3,
             ["Text 1 bases its case on matching the sun.",
              "Text 1 does not address waking hours.",
              "Text 1 wants the change ended.",
              "Correct. Text 1's reason for standard time is that it 'matches the sun most closely.'"],
             "Text 1 would appeal to alignment with the sun."),
            ("Both authors mention which of the following in support of their positions?",
             ["fuel savings from the clock change",
              "effects on road safety",
              "the sleep lost by schoolchildren",
              "the preferences of farmers"],
             1,
             ["Only Text 1 mentions fuel, and as a failed rationale.",
              "Correct. Text 1 cites traffic accidents after the change; Text 2 cites road deaths reduced by evening light.",
              "Schoolchildren are not mentioned.",
              "Farmers are not mentioned."],
             "Road safety appears in both arguments."),
        ],
    },
    {
        "id": "moon_money",
        "text_a": (
            "Spending billions to send people to other worlds while problems remain "
            "unsolved at home, the author argues, reflects misplaced priorities. The money "
            "devoted to a single crewed mission could fund clean water for millions or "
            "research into diseases that kill every year. Robots, moreover, can collect "
            "most of the scientific data humans could, at a fraction of the cost and risk. "
            "The romance of exploration is real, but romance is a poor basis for budgets. "
            "A government's first obligation is to the people who already live on the "
            "planet it governs, and every launch should be weighed against what the same "
            "money could do for them."),
        "text_b": (
            "The author does not dispute that needs on Earth are urgent, but argues that "
            "framing the choice as exploration versus welfare is false. Space budgets are "
            "a small fraction of national spending, far smaller than most people guess, "
            "and cutting them would not transfer the savings to clean water; it would "
            "simply reduce them. Meanwhile, the engineering required to keep humans alive "
            "in hostile environments has produced water purification, medical monitoring, "
            "and weather forecasting that serve people who will never leave Earth. The "
            "question, the text suggests, is not whether to look up or down, but whether "
            "we can do both well."),
        "questions": [
            ("Which choice best describes how Text 2 responds to Text 1?",
             ["It agrees that robots can gather all of the data that human explorers could.",
              "It argues that the problems on Earth are far less urgent than Text 1 makes them out to be.",
              "It challenges the assumption that money not spent on space would be spent on other needs.",
              "It accepts that crewed missions should be ended in favor of welfare spending."],
             2,
             ["Text 2 does not address robots.",
              "Text 2 does 'not dispute that needs on Earth are urgent.'",
              "Correct. Text 2 says cutting space budgets 'would not transfer the savings to clean water.'",
              "Text 2 defends crewed engineering's benefits."],
             "Text 2 attacks the either-or framing."),
            ("Based on the texts, the two authors would most likely agree that",
             ["problems on Earth deserve serious attention and resources",
              "space exploration should be left entirely to robots",
              "space budgets make up a large share of national spending",
              "the romance of exploration justifies almost any expense"],
             0,
             ["Correct. Text 1 prioritizes them, and Text 2 does not dispute their urgency.",
              "Only Text 1 raises robots.",
              "Text 2 says the share is small.",
              "Text 1 calls romance a poor basis for budgets."],
             "Both grant Earth's needs."),
            ("The author of Text 1 would most likely respond to Text 2's point about water purification and weather forecasting by",
             ["agreeing that crewed missions are the best source of such technologies",
              "arguing that such benefits could be pursued directly without crewed missions",
              "denying that any useful technology has ever come from space programs",
              "claiming that weather forecasting is of no value to people on Earth"],
             1,
             ["Text 1 wants spending directed at Earth's problems directly.",
              "Correct. Text 1's logic is that money should go straight to the needs, and that robots suffice for space science.",
              "Text 1 does not deny past benefits.",
              "Text 1 would not dismiss forecasting's value."],
             "Text 1 would favor the direct route to such benefits."),
        ],
    },
    {
        "id": "grade_free",
        "text_a": (
            "Grades, the author argues, are a poor measure of learning and a worse "
            "motivator. Students taught to chase a letter learn to ask what will be on the "
            "test rather than what is true, and they abandon a subject the moment the "
            "grade is secured. Schools that have replaced grades with written feedback "
            "report students taking harder courses, asking more questions, and revising "
            "work they would once have discarded. The letter grade compresses a semester "
            "of thinking into a single symbol that tells a student almost nothing about "
            "what to do next. Feedback tells them exactly that, and does so while there "
            "is still time to act on it."),
        "text_b": (
            "Written feedback is valuable, this author agrees, and no one defends a grade "
            "as a complete account of a student. But grades do work that feedback cannot. "
            "They are comparable across teachers and schools, which lets a college or "
            "employer read a transcript from a school it has never heard of. They make it "
            "harder for bias to hide, since a vague paragraph can flatter one student and "
            "damn another without ever stating a standard. And for many students, a clear "
            "target is not a corruption of learning but the thing that gets them to the "
            "desk at all. The right reform is to improve grades, not to abolish them."),
        "questions": [
            ("Which choice best describes the relationship between the texts?",
             ["Text 2 denies that written feedback has any real value for students.",
              "Text 2 agrees with Text 1 about the value of feedback but defends grades on other grounds.",
              "Both texts argue that letter grades should be abolished entirely in favor of written feedback.",
              "Text 1 argues in favor of grades while Text 2 argues against them."],
             1,
             ["Text 2 calls feedback 'valuable.'",
              "Correct. Text 2 grants feedback's value and argues grades do other necessary work.",
              "Text 2 wants grades improved, not abolished.",
              "The positions are reversed."],
             "Agreement on feedback, disagreement on grades."),
            ("How would the author of Text 2 most likely respond to Text 1's claim that a grade 'tells a student almost nothing'?",
             ["by agreeing that grades are limited while noting that they serve readers other than the student",
              "by arguing that grades tell students everything they need to know about their work",
              "by conceding that grades should therefore be replaced with written feedback",
              "by insisting that written feedback is actually more comparable across schools and teachers than grades are"],
             0,
             ["Correct. Text 2 concedes grades are incomplete but stresses colleges and employers who read transcripts.",
              "Text 2 says no one defends a grade as a complete account.",
              "Text 2 opposes abolition.",
              "Text 2 says grades, not feedback, are comparable."],
             "Text 2 shifts attention to the other readers of grades."),
            ("Based on Text 2, the author would most likely say that the schools described in Text 1 that replaced grades",
             ["have proven that grades are unnecessary for motivating students to do their work",
              "have eliminated the possibility of bias in evaluation",
              "should be adopted as a model by every other school",
              "may have made it harder for outsiders to interpret their students' records"],
             3,
             ["Text 2 says a clear target motivates many students.",
              "Text 2 says vague feedback lets bias hide.",
              "Text 2 opposes abolishing grades.",
              "Correct. Text 2 values grades because they let outsiders read a transcript."],
             "Comparability for outsiders is Text 2's concern."),
        ],
    },
    {
        "id": "bike_lanes",
        "text_a": (
            "Converting a traffic lane on a busy street into a protected bicycle lane, the "
            "author argues, benefits even the drivers who complain about it. Separated "
            "lanes draw riders who would otherwise avoid the street, and each of those "
            "riders is a car that is not in the queue ahead. Cities that have built "
            "networks of such lanes report fewer collisions for everyone, including "
            "pedestrians, since the design narrows crossings and slows turning vehicles. "
            "Shops along converted streets, despite early fears, have generally seen sales "
            "hold steady or rise as foot and bicycle traffic increases. The lane looks "
            "like a gift to cyclists. It is, the author contends, a repair to the street."),
        "text_b": (
            "The author supports cycling but warns that the benefits of protected lanes "
            "depend heavily on where they are built. On a dense commercial street with "
            "many short trips, a lane can replace car journeys; on an arterial road "
            "through a spread-out district, it may serve a handful of riders while pushing "
            "congestion onto parallel streets that were never designed for it. Delivery "
            "drivers, people with disabilities, and residents without transit options bear "
            "costs that rarely appear in the studies cited by advocates. The text does not "
            "oppose bicycle lanes. It asks that each one be judged on its own street, with "
            "its own numbers, rather than on averages drawn from the places where lanes "
            "work best."),
        "questions": [
            ("Which choice best describes how Text 2 responds to Text 1?",
             ["It rejects Text 1's claim that bicycle lanes reduce collisions for pedestrians.",
              "It argues that bicycle lanes should be removed from dense commercial streets.",
              "It qualifies Text 1's conclusion by arguing that results vary with the setting.",
              "It agrees that every busy street would benefit from a protected lane."],
             2,
             ["Text 2 does not dispute the collision findings.",
              "Text 2 says dense commercial streets are where lanes work.",
              "Correct. Text 2 says benefits 'depend heavily on where they are built.'",
              "Text 2 warns against generalizing."],
             "Text 2 adds a condition rather than a contradiction."),
            ("The author of Text 2 would most likely say that the studies cited in Text 1",
             ["may reflect the streets where lanes succeed rather than typical conditions",
              "were conducted by researchers who are opposed to cycling",
              "show that protected lanes harm the sales of shops located along converted streets",
              "prove that lanes never increase congestion on nearby streets"],
             0,
             ["Correct. Text 2 objects to 'averages drawn from the places where lanes work best.'",
              "Text 2 refers to studies 'cited by advocates,' not opponents.",
              "Text 2 does not address shops.",
              "Text 2 says lanes can push congestion onto parallel streets."],
             "Selection of favorable sites is Text 2's worry."),
            ("Both authors would most likely agree that",
             ["drivers are the main beneficiaries of protected bicycle lanes",
              "protected bicycle lanes can benefit a city under the right conditions",
              "delivery drivers' concerns are adequately addressed in existing studies",
              "bicycle lanes should be built on every busy street in a city"],
             1,
             ["Text 1 says drivers benefit too, not mainly; Text 2 does not say this.",
              "Correct. Text 1 praises lanes; Text 2 'supports cycling' and says lanes work on dense streets.",
              "Text 2 says those costs 'rarely appear' in studies.",
              "Text 2 rejects a blanket approach."],
             "Both see value in lanes; Text 2 adds conditions."),
        ],
    },
    {
        "id": "mammoth_return",
        "text_a": (
            "Using recovered genetic material to bring back vanished species, the author "
            "argues, is the most hopeful project in modern biology. A herd of cold-adapted "
            "elephants grazing the northern tundra could help restore grasslands that once "
            "held carbon in their soils, and the techniques developed along the way, from "
            "gene editing to artificial wombs, would serve the conservation of species "
            "that are endangered now. Extinction has always been treated as a final "
            "verdict. For the first time, it might become an appeal. The author "
            "acknowledges the project is expensive but sees in it something the field has "
            "lacked for decades: a reason for optimism."),
        "text_b": (
            "Resurrecting a mammoth, this author contends, would produce not a mammoth but "
            "an elephant with a few mammoth genes, raised without the mother, the herd, or "
            "the climate that made the original what it was. The money, measured in "
            "hundreds of millions, would protect dozens of species that are vanishing "
            "today and need only habitat and enforcement rather than invention. The author "
            "worries most about the lesson. If the public comes to believe that extinction "
            "is reversible, the urgency that drives conservation drains away. Hope is "
            "valuable. False hope, the author warns, is worse than none."),
        "questions": [
            ("Which choice best describes the central disagreement between the texts?",
             ["whether gene editing is technically possible with recovered genetic material",
              "whether any species are currently in danger of extinction",
              "whether mammoths once lived on the northern tundra",
              "whether reviving extinct species is a wise use of conservation resources"],
             3,
             ["Neither text disputes the technical possibility.",
              "Both accept that species are endangered now.",
              "Neither disputes this.",
              "Correct. Text 1 calls the project hopeful; Text 2 says the money should go to living species."],
             "The dispute is about wisdom and priorities."),
            ("How would the author of Text 2 most likely respond to Text 1's hope that extinction 'might become an appeal'?",
             ["by warning that such a belief could weaken the public's commitment to preventing extinction",
              "by agreeing that reversing extinction is now a realistic goal for modern biology",
              "by arguing that courts rather than scientists should decide which species are revived",
              "by claiming that extinction has never been a serious problem for ecosystems"],
             0,
             ["Correct. Text 2 fears that belief in reversibility drains conservation's urgency.",
              "Text 2 says the result would not truly be a mammoth.",
              "Courts are not mentioned.",
              "Text 2 treats extinction as urgent."],
             "Text 2's chief worry is the lesson the public draws."),
            ("Both authors would most likely agree that",
             ["the revived animals would be genuine mammoths in every respect",
              "the project would require a very large financial investment",
              "the public's beliefs about extinction are unimportant",
              "conservation has recently enjoyed abundant optimism"],
             1,
             ["Text 2 denies this.",
              "Correct. Text 1 acknowledges the project is expensive; Text 2 cites hundreds of millions.",
              "Text 2 cares deeply about public belief.",
              "Text 1 says optimism has been lacking."],
             "Cost is common ground."),
        ],
    },
    {
        "id": "pen_keyboard",
        "text_a": (
            "Students who take notes by hand, the author reports, consistently remember "
            "more of a lecture than those who type. Because writing is slower, they cannot "
            "transcribe, so they must decide what matters and put it in their own words, "
            "and that act of compression is itself a form of learning. Typists, by "
            "contrast, tend to produce near-verbatim records that they never fully "
            "process. In several experiments, the handwriting advantage held even when "
            "typists were explicitly warned not to transcribe. The author concludes that "
            "the pen's limitations are a feature, and recommends that lecture halls "
            "discourage laptops."),
        "text_b": (
            "The author accepts the finding that handwriting aids memory in the lecture "
            "hall but questions the recommendation that follows. The experiments measured "
            "recall of a single lecture within a week. They did not measure what students "
            "did afterward with their notes, and typed notes are far easier to search, "
            "reorganize, and share when preparing for an exam weeks later. Nor did the "
            "studies include students with disabilities, for whom a keyboard may be the "
            "only practical option. Rather than banning laptops, the author suggests "
            "teaching students to type the way good note-takers write: selectively, in "
            "their own words, and with the lecture rather than the screen as the focus."),
        "questions": [
            ("Which choice best describes the relationship between the texts?",
             ["Text 2 accepts Text 1's evidence but disputes the policy that Text 1 draws from it.",
              "Text 2 presents new experiments that contradict the findings reported in Text 1.",
              "Text 1 and Text 2 agree that laptops should be discouraged in lecture halls.",
              "Text 2 argues that handwriting actually harms memory for lectures."],
             0,
             ["Correct. Text 2 'accepts the finding' but 'questions the recommendation.'",
              "Text 2 cites no new experiments.",
              "Text 2 opposes banning laptops.",
              "Text 2 accepts that handwriting aids memory."],
             "Agreement on data, disagreement on policy."),
            ("The author of Text 2 would most likely say that the experiments described in Text 1",
             ["were so poorly designed that they should be disregarded entirely",
              "showed that typed notes are better for immediate recall of lectures",
              "measured too narrow an outcome to justify a general rule",
              "included an adequate range of students with different needs"],
             2,
             ["Text 2 accepts the finding.",
              "Text 2 accepts that handwriting won on recall.",
              "Correct. Text 2 notes they measured only one lecture's recall within a week.",
              "Text 2 says students with disabilities were not included."],
             "Narrow outcome measurement is Text 2's critique."),
            ("Based on the texts, both authors would most likely agree that",
             ["verbatim notes are the most useful kind for later study",
              "putting ideas in one's own words helps learning",
              "the speed of typing is its chief advantage for learning",
              "laptops should be prohibited in all lecture halls"],
             1,
             ["Text 1 criticizes verbatim notes; Text 2 wants selective typing.",
              "Correct. Text 1 praises compression into one's own words; Text 2 wants typists to do the same.",
              "Neither says this.",
              "Text 2 opposes prohibition."],
             "Own-words processing is common ground."),
            ("Text 2 raises which consideration that Text 1 does not address?",
             ["the difference in speed between handwriting and typing",
              "whether typists were warned against transcribing",
              "the tendency of typists to produce verbatim notes",
              "the needs of students with disabilities"],
             3,
             ["Text 1 discusses speed.",
              "Text 1 mentions the warning.",
              "Text 1 describes this tendency.",
              "Correct. Only Text 2 mentions students for whom a keyboard is the only practical option."],
             "Accessibility is Text 2's added consideration."),
        ],
    },
    {
        "id": "four_days",
        "text_a": (
            "Companies that have tried a four-day week without cutting pay, the author "
            "reports, have mostly kept it. Employees, given a day back, cut the meetings "
            "and idle hours that had filled the fifth, and output in trials across several "
            "countries held steady while sick days fell and resignations dropped by more "
            "than a third. The author argues that the five-day week was never a law of "
            "nature; it was a compromise struck a century ago for factory labor, and "
            "knowledge work has simply inherited it. A schedule that produces the same "
            "work with less exhaustion is not a perk, the text concludes. It is the "
            "correction of a mistake."),
        "text_b": (
            "The four-day trials are encouraging, this author allows, but they share a "
            "flaw: the companies that volunteer for them are the ones most likely to "
            "succeed. They are small, office-based, and already flexible. A hospital, a "
            "school, or a restaurant cannot compress a week; it can only hire more people, "
            "which the trials' accounting never includes. Even in offices, the author "
            "notes, the gains came partly from cutting work that was wasteful in the first "
            "place, which a firm could do on any schedule. The text does not oppose "
            "shorter weeks. It warns that a result from firms that chose to be studied "
            "cannot be assumed to hold for firms that did not."),
        "questions": [
            ("Which choice best describes how Text 2 responds to Text 1?",
             ["It denies that any firm has successfully adopted a four-day week.",
              "It questions whether the trial results can be generalized beyond the firms that volunteered.",
              "It agrees that the five-day week was a historical mistake that should be corrected everywhere.",
              "It argues that employees in the trials worked much harder than before."],
             1,
             ["Text 2 calls the trials 'encouraging.'",
              "Correct. Text 2's central point is that volunteers are 'the ones most likely to succeed.'",
              "Text 2 warns against generalizing.",
              "Text 2 attributes gains partly to cutting waste, not harder work."],
             "Selection bias is Text 2's objection."),
            ("How would the author of Text 2 most likely respond to Text 1's claim that the four-day week is 'the correction of a mistake'?",
             ["by observing that some workplaces cannot shorten the week without hiring more staff",
              "by agreeing that factory schedules should govern all knowledge work",
              "by arguing that the five-day week has always been a law of nature",
              "by insisting that sick days and resignations actually rose during the four-day trials"],
             0,
             ["Correct. Text 2 says hospitals, schools, and restaurants 'can only hire more people.'",
              "Text 2 does not defend factory schedules.",
              "Text 2 does not make this claim.",
              "Text 2 does not dispute the sick-day data."],
             "Text 2 points to workplaces that cannot compress."),
            ("Both authors would most likely agree that",
             ["hospitals and restaurants can easily adopt a four-day week",
              "the trials prove the four-day week works for every employer",
              "the firms in the trials eliminated some wasteful activity",
              "employees in the trials produced less than they had before"],
             2,
             ["Text 2 says they cannot compress a week.",
              "Text 2 denies this.",
              "Correct. Text 1 says employees cut idle meetings; Text 2 says gains came from cutting wasteful work.",
              "Both say output held steady."],
             "Cutting waste is common ground."),
        ],
    },
    {
        "id": "bag_ban",
        "text_a": (
            "Banning thin plastic grocery bags, the author argues, is one of the rare "
            "environmental policies that costs almost nothing and works. Within a year of "
            "one city's ban, the number of plastic bags found in storm drains and along "
            "the shoreline fell by roughly half, and shoppers adapted within weeks, as "
            "they had been told they would not. The bag itself was never essential; it "
            "was a convenience that had become a habit, and habits can be changed by a "
            "small, well-timed push. The author sees the ban as a model: pick the waste "
            "that is most visible, most avoidable, and least missed."),
        "text_b": (
            "The bans do reduce litter, this author agrees, but their effect on the "
            "environment as a whole is less clear. When thin bags disappear, shoppers buy "
            "thicker plastic bags for trash cans and pet waste, and many of the reusable "
            "bags handed out in their place are made of materials that require dozens of "
            "uses before they outperform the bag they replaced. Studies in several cities "
            "find total plastic consumption falling by far less than the bag count "
            "suggests. The author does not call for repealing the bans. The point is that "
            "a visible result is not the same as a large one, and that policy should be "
            "judged by the second."),
        "questions": [
            ("Which choice best describes the relationship between the texts?",
             ["Text 2 argues that bag bans should be repealed because they have failed to reduce litter at all.",
              "Text 1 and Text 2 agree that bag bans have little effect on anything at all.",
              "Text 2 argues that shoppers have largely failed to adapt to the bans.",
              "Text 2 accepts that the bans reduce litter but questions their broader environmental benefit."],
             3,
             ["Text 2 does not call for repeal and agrees litter fell.",
              "Text 1 says the bans work.",
              "Adaptation is not disputed.",
              "Correct. Text 2 grants the litter reduction and questions the total effect."],
             "Partial agreement, broader doubt."),
            ("How would the author of Text 2 most likely respond to Text 1's advice to 'pick the waste that is most visible'?",
             ["by cautioning that visibility is a poor guide to the size of a policy's real effect",
              "by agreeing that visible waste is the most environmentally harmful kind",
              "by proposing that bans be extended immediately to all plastic products",
              "by denying that plastic bags are ever found in storm drains"],
             0,
             ["Correct. Text 2 says 'a visible result is not the same as a large one.'",
              "Text 2 distinguishes visibility from harm.",
              "Text 2 proposes no such extension.",
              "Text 2 accepts that litter fell."],
             "Visibility versus magnitude is Text 2's point."),
            ("Which finding from Text 2 most directly complicates the claim in Text 1 that the bag 'was never essential'?",
             ["Studies in several cities measured total plastic consumption.",
              "Shoppers buy thicker bags for uses the thin bags had served.",
              "Reusable bags require dozens of uses to outperform thin ones.",
              "The bans do reduce litter along shorelines."],
             1,
             ["Measurement alone does not address essentiality.",
              "Correct. Buying replacements for trash and pet waste shows the bag served real uses.",
              "This concerns reusable bags, not whether thin bags were needed.",
              "This supports Text 1."],
             "Replacement purchases show the bag had functions."),
        ],
    },
    {
        "id": "screen_age",
        "text_a": (
            "Raising the minimum age for social media accounts to sixteen, the author "
            "argues, is the least a society can do for its adolescents. The years between "
            "twelve and fifteen are when self-image is most fragile, and platforms built "
            "to maximize attention have learned to exploit that fragility with comparison, "
            "notification, and the quiet arithmetic of likes. Surveys of teenagers "
            "themselves find that most wish they used the apps less and cannot manage to. "
            "An age limit does not solve everything. It gives families a rule to point to, "
            "and it gives the youngest users three more years before the pressure begins."),
        "text_b": (
            "The evidence linking social media to adolescent distress, this author notes, "
            "is weaker and more mixed than headlines suggest, and age limits carry costs "
            "that advocates rarely weigh. For isolated teenagers, including those in rural "
            "areas or with uncommon interests, the apps are where they find the only "
            "people who understand them. A ban would push younger users onto platforms "
            "with no safety features at all, since enforcement by birthdate is trivially "
            "evaded. The author favors stricter design rules, such as limits on "
            "notifications and infinite scrolling, that would apply to every user. Fix the "
            "product, the text argues, rather than fencing off the people."),
        "questions": [
            ("Which choice best describes the central disagreement between the texts?",
             ["whether adolescents use social media at all",
              "whether social media platforms are deliberately designed to capture users' attention",
              "whether an age limit is the right response to concerns about social media",
              "whether rural teenagers have access to the internet"],
             2,
             ["Both assume adolescents use it.",
              "Both describe attention-capturing design.",
              "Correct. Text 1 wants an age limit; Text 2 wants design rules instead.",
              "Not in dispute."],
             "Age limit versus design rules is the disagreement."),
            ("How would the author of Text 2 most likely respond to the survey cited in Text 1?",
             ["by noting that the broader evidence of harm is less clear than such surveys suggest",
              "by agreeing that it proves an age limit is necessary",
              "by arguing that teenagers' own reports about their habits should be given no weight whatsoever",
              "by claiming that most teenagers actually want to use the apps more"],
             0,
             ["Correct. Text 2 says the evidence is 'weaker and more mixed than headlines suggest.'",
              "Text 2 opposes an age limit.",
              "Text 2 does not dismiss self-reports outright.",
              "Text 2 makes no such claim."],
             "Text 2 would question what the evidence shows."),
            ("Both authors would most likely agree that",
             ["an age limit would be easy to enforce",
              "some features of social media platforms are harmful to young users",
              "isolated teenagers have little to gain from social media",
              "design rules limiting notifications would be ineffective"],
             1,
             ["Text 2 says enforcement is trivially evaded.",
              "Correct. Text 1 cites notifications and likes; Text 2 wants limits on notifications and infinite scrolling.",
              "Text 2 says isolated teens benefit.",
              "Text 2 proposes design rules."],
             "Both see harmful design features."),
        ],
    },
]
