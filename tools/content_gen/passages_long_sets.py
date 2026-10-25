"""Original ACT-length single reading passages, each with a full question set.

All prose here is original, written for this project (no copyrighted text).
There are three passages for each of the four ACT Reading genres -- literary
narrative, social science, humanities and natural science -- at easy, medium
and hard difficulty. Each passage runs about 650-800 words, is split into
numbered paragraphs (questions cite "paragraph N"), and carries nine questions,
as on the enhanced ACT (four passages x nine questions = the 36-item section).

A question is (kind, prompt, [opt0..opt3], correct_index, [rat0..rat3],
explanation). ``kind`` is one of passages_long.KINDS and decides which reading
skill the item trains. The key's rationale starts with "Correct." and no other
one does; quoted words/phrases in a prompt (“...”) appear verbatim in the
passage (tools/tests/test_passages_long.py checks both).
"""
from __future__ import annotations

LONG_PASSAGES = [
    # ------------------------------------------------------------------ #
    # Literary narrative
    # ------------------------------------------------------------------ #
    {
        "id": "the-ledger", "genre": "literary", "difficulty": "easy",
        "title": "The Ledger",
        "paragraphs": [
            "On the last Saturday in August, my grandfather turned the sign on the door of "
            "Okafor Cycle Repair from OPEN to CLOSED for the final time. Then, because he could "
            "not help himself, he turned it back. “Someone might have a flat,” he said, as though "
            "the whole town had spent forty-one years waiting for this particular afternoon to "
            "need him. I was fifteen, and I had come to help him pack, which mostly meant "
            "wrapping wrenches in newspaper while he told me where each one had come from.",

            "The shop was narrower than our kitchen at home and smelled of rubber and oil and "
            "the peppermints he kept in a coffee can by the register. Inner tubes hung from the "
            "ceiling like gray streamers. Along the back wall, under a calendar that had stopped "
            "at March of some year before I was born, stood the workbench, its surface so scarred "
            "by tools that it looked less like wood than like a map of rivers. I had spent whole "
            "summers on the stool beside that bench, handing him spokes and pretending to "
            "understand what he meant when he said a wheel was “almost true.”",

            "By three o'clock most of the shelves were empty, and I found the ledger. It was "
            "wedged behind the drawer of the register, a green clothbound book with a broken "
            "spine, and when I pulled it out a few loose receipts fluttered to the floor. Inside, "
            "in my grandfather's slanted capitals, were names, dates, and repairs: NEW CHAIN, TWO "
            "TUBES, REBUILT BRAKES. Beside most entries he had written PAID and the date. But "
            "beside many others, more than I could count at a glance, there was only a small "
            "penciled circle.",

            "“What do the circles mean?” I asked. He was on a ladder, unhooking the last of the "
            "inner tubes, and he did not turn around right away. “They mean the bike went home,” "
            "he said finally. I told him that every bike went home; that was the point of fixing "
            "them. He came down the ladder slowly, one rung at a time, the way he did everything "
            "now, and took the book from me. He ran his thumb down a page as if he were reading "
            "the names with his hand rather than his eyes.",

            "“This one,” he said, tapping a circle, “was a boy who delivered newspapers. His "
            "chain broke on a Monday, and if he could not deliver on Tuesday he would lose the "
            "route. This one was a nurse who rode to the hospital at night because the buses "
            "stopped running at ten. This one I do not remember at all.” He smiled at that. "
            "“Maybe he was just a man with a bicycle and no money that week. That happens to "
            "people, too.”",

            "I did the arithmetic in my head, the way my mother had taught me to do at the "
            "grocery store, and it came to a lot. Not a fortune, maybe, but enough that I thought "
            "of the summer he had sold his car, and of the winter he had kept the shop's heat "
            "turned so low that he worked in his coat. I wanted to be angry on his behalf. I "
            "wanted to find the newspaper boy, who would be a grown man now, and present him "
            "with a bill.",

            "Instead I asked whether he had ever been tempted to collect. My grandfather "
            "considered the question with the seriousness he gave to bent wheels. “A bill is a "
            "kind of door,” he said. “Some people, when you hand it to them, they walk through it "
            "and never come back. I would rather they came back.” He closed the ledger and set it "
            "on top of the box marked KEEP, not the one marked RECYCLING, though there was no "
            "longer any business for it to record.",

            "Near five o'clock the bell over the door rang. A woman about my mother's age stood "
            "in the doorway holding a child's bicycle with a flat front tire, and she looked "
            "embarrassed to find the shelves bare. “I heard you were closing,” she said. “I "
            "wasn't sure.” My grandfather was already reaching for the one pump we had not "
            "packed. I watched him kneel beside the little wheel, and I understood, without "
            "anyone explaining it to me, why he had turned the sign back around.",
        ],
        "questions": [
            ("main_idea",
             "Which of the following statements best describes the passage as a whole?",
             ["A teenager persuades her grandfather to keep his bicycle shop open after he decides to retire.",
              "A grandfather teaches his granddaughter the repair skills she will need to take over his business.",
              "A teenager helping close her grandfather's shop comes to understand the generosity behind his unpaid accounts.",
              "A grandfather admits to his granddaughter that he regrets the money he lost by never collecting his customers' debts."],
             2,
             ["The shop still closes; the narrator never argues that it should stay open.",
              "The narrator packs tools; no handing-over of the business is described.",
              "Correct. The ledger's circles lead the narrator to see why her grandfather let struggling customers take their bikes home.",
              "He shows no regret; he says he would rather customers came back than pay."],
             "The passage moves from packing up, to the ledger's unpaid entries, to the narrator understanding her grandfather's choice."),
            ("detail",
             "According to the passage, the narrator found the ledger:",
             ["inside the box marked KEEP",
              "wedged behind the register's drawer",
              "in the coffee can of peppermints",
              "under the calendar on the back wall"],
             1,
             ["The grandfather puts the ledger on the KEEP box later; that is not where it was found.",
              "Correct. Paragraph 3 says it was wedged behind the drawer of the register.",
              "The coffee can holds peppermints, not the ledger.",
              "The calendar hangs above the workbench; the ledger was not there."],
             "Paragraph 3: “It was wedged behind the drawer of the register.”"),
            ("detail",
             "According to the grandfather, the nurse he mentions in paragraph 5 rode a bicycle because:",
             ["she could not afford to keep a car of her own",
              "the hospital was too close to bother driving to",
              "the buses stopped running at ten o'clock at night",
              "her own car had broken down earlier that same winter"],
             2,
             ["Affording a car is never mentioned for the nurse (the grandfather is the one who sold his car).",
              "The hospital's distance is never mentioned.",
              "Correct. He says she rode at night because the buses stopped running at ten.",
              "No broken-down car is mentioned for her."],
             "Paragraph 5: “a nurse who rode to the hospital at night because the buses stopped running at ten.”"),
            ("inference",
             "Based on the passage, the small penciled circles in the ledger most likely mark repairs that:",
             ["were finished and returned to customers who never paid for them",
              "the grandfather had not yet finished when he decided to close the shop",
              "customers had paid for in advance, before any work was done",
              "required parts that had to be ordered from another town"],
             0,
             ["Correct. The circles sit where PAID is missing, and he describes customers who had no money that week.",
              "He says “the bike went home,” so the work was done.",
              "Paid entries are marked PAID; the circles mark the ones without payment.",
              "Ordering parts is never mentioned."],
             "The circles appear where PAID is absent, and the stories he tells are about customers who could not pay."),
            ("inference",
             "The grandfather's remark that “A bill is a kind of door” (paragraph 7) suggests that he believes:",
             ["customers deserve a written record of every repair that is done",
              "demanding payment might drive struggling customers away for good",
              "a shop owner must be firm with customers in order to earn respect",
              "most people will pay what they owe if they are reminded politely"],
             1,
             ["He is not talking about record-keeping; he already keeps a ledger.",
              "Correct. He says people handed a bill may “walk through it and never come back.”",
              "He chooses gentleness over firmness, the opposite of this idea.",
              "He suggests bills drive people off, not that reminders bring payment."],
             "He prefers that customers return rather than be pushed away by a bill they cannot pay."),
            ("vocab",
             "As it is used in paragraph 2, the word “true” most nearly means:",
             ["evenly aligned", "honest and sincere", "loyal to a friend", "accurate in fact"],
             0,
             ["Correct. A wheel that is “almost true” is almost straight and evenly aligned.",
              "Honesty describes people, not bicycle wheels.",
              "Loyalty describes people, not bicycle wheels.",
              "Factual accuracy applies to statements, not to a wheel."],
             "Used of a bicycle wheel, “true” means straight and properly aligned."),
            ("function",
             "The narrator's description of the workbench in paragraph 2 mainly serves to:",
             ["suggest that the grandfather was careless with his tools and equipment",
              "explain why the shop was finally forced to close at the end of the summer",
              "convey how many years of steady work the shop and its owner have seen",
              "contrast the cluttered shop with the narrator's tidier kitchen at home"],
             2,
             ["The scars come from long use, not carelessness; he treats his work seriously.",
              "The workbench description gives no reason for the closing.",
              "Correct. A surface so scarred it looks like “a map of rivers” shows decades of use.",
              "The kitchen is compared only for size (the shop is narrower), not tidiness."],
             "The worn workbench is a visual record of the shop's long history."),
            ("structure",
             "The final paragraph mainly serves to:",
             ["reveal that the grandfather has decided not to close the shop after all",
              "introduce a former customer who has come to repay an old debt",
              "suggest that the narrator will one day take over her grandfather's work",
              "present an event that shows why the grandfather turned the sign back"],
             3,
             ["Nothing indicates he changes his decision; the shelves are bare.",
              "The woman brings a flat tire; no debt is mentioned.",
              "The narrator watches and understands; no plan to take over is given.",
              "Correct. A customer arrives needing help, and the narrator understands why he reopened the sign."],
             "The last-minute customer confirms the grandfather's instinct from paragraph 1."),
            ("view",
             "In paragraph 6, the narrator's reaction to adding up the unpaid repairs is best described as:",
             ["admiration for the customers' honesty",
              "relief that the total was so small",
              "indignation on her grandfather's behalf",
              "confusion about how the ledger was kept"],
             2,
             ["She wants to bill a customer, not praise them.",
              "The sum “came to a lot,” so she is not relieved.",
              "Correct. She wants “to be angry on his behalf” and to present a bill.",
              "She understands the ledger well enough to add it up."],
             "She thinks of his sacrifices and wants to be angry for him."),
        ],
    },
    {
        "id": "night-ferry", "genre": "literary", "difficulty": "medium",
        "title": "Night Ferry",
        "paragraphs": [
            "The ferry left the mainland at eleven, and by the time it cleared the breakwater, "
            "Teo was the only passenger still on the open deck. The others had gone inside, "
            "where the benches were warm and a television bolted to the ceiling showed a game no "
            "one was watching. He preferred the cold. After nine months of dormitory radiators "
            "that clanked all night and a roommate who slept with the window shut, the wind off "
            "the strait felt like something he had been owed.",

            "He had imagined this crossing many times during the spring, usually in the middle "
            "of an exam. In the imagined version he stood at the rail exactly as he was standing "
            "now, and the lights of the island rose out of the dark one by one, and he felt the "
            "whole year fall away from him like a coat he no longer needed. What he had not "
            "imagined was how small the lights would look. From the dormitory, the island had "
            "seemed enormous, the place where everything important had happened. From the deck, "
            "it looked like a handful of sparks someone had forgotten to put out.",

            "“You're Ana Reyes's boy.” The voice came from behind him, and Teo turned to find a "
            "man in oil-stained coveralls leaning in the doorway of the engine room, wiping his "
            "hands on a rag that was dirtier than his hands. Teo recognized him vaguely, the way "
            "he recognized most adults on the island: as part of the scenery, like the church "
            "steeple or the tide charts posted outside the post office. “Hollis,” the man said. "
            "“I've run the engines on this boat since before you were born. Your mother used to "
            "ride out with her algebra homework. Never once finished it before we docked.”",

            "Teo laughed, surprised. His mother taught math at the island's only school now, and "
            "the idea of her as a girl struggling with equations on a rolling deck seemed both "
            "impossible and entirely obvious. Hollis came to stand beside him at the rail. For a "
            "while neither of them spoke. The engines thudded beneath their feet with a "
            "steadiness Teo could feel in his teeth.",

            "“So,” Hollis said eventually. “Is it what you expected? The mainland?” Teo started "
            "to give the answer he had been giving all year, on the phone to his parents and in "
            "messages to friends who had stayed behind: that it was great, that he was busy, that "
            "the library was open until two in the morning. But the dark made it easier to say "
            "something truer. “It's bigger,” he said. “Everyone there is from somewhere else, so "
            "nobody asks where you're from. I thought I'd like that more than I did.”",

            "Hollis nodded as if this were information about the weather. “Your mother said the "
            "same thing, near enough, the first summer she came back.” He folded the rag into a "
            "neat square and tucked it into his pocket. “She said the trouble with leaving is "
            "that you change, and the trouble with coming back is that the island doesn't. Then "
            "she said she was wrong about the second part.”",

            "“Wrong how?” Teo asked. Hollis shrugged. “Island changes, too. Just slower. Harbor's "
            "been dredged twice since you were little. The bakery's under new owners, and they "
            "put walnuts in everything now, which some people consider a crime. Old Mrs. "
            "Petrakis finally retired from the post office.” He paused. “Thing is, when you live "
            "here, you don't see it happening. You need to go away for a while before you can "
            "notice.”",

            "The lights of the harbor had grown larger as they talked, and now Teo could pick out "
            "individual shapes: the floodlit fuel dock, the red blink of the channel marker, the "
            "square yellow windows of houses along the hill where people were still awake. One "
            "of those windows, he knew, was his own kitchen, where his mother would be sitting "
            "with a cup of tea she had let go cold, pretending not to wait for him.",

            "Hollis pushed himself away from the rail. “Engines don't watch themselves,” he said, "
            "and disappeared below. Teo stayed where he was. The island was no longer a handful "
            "of sparks. It was not enormous, either. It was simply the size it was, and for the "
            "first time all year he thought he might be able to see it clearly.",
        ],
        "questions": [
            ("main_idea",
             "The passage mainly focuses on:",
             ["a ferry engineer's attempt to persuade a young man to stay on the island for good",
              "a young man's decision to leave college and take a job aboard the island's ferry",
              "the quarrel between longtime islanders and the newcomers who now run its businesses",
              "a young man's shifting view of his home as he returns to it after a year away"],
             3,
             ["Hollis never urges Teo to stay; he simply talks with him.",
              "Teo is coming home for the summer; he takes no job on the ferry.",
              "The bakery's new owners are a passing detail, not a quarrel the passage explores.",
              "Correct. The crossing and the talk with Hollis change how Teo sees the island."],
             "The passage traces Teo's view of the island from “enormous” to “sparks” to “the size it was.”"),
            ("detail",
             "According to Hollis, Teo's mother used to ride the ferry while:",
             ["grading stacks of math tests for the island's only school",
              "working on algebra homework she never finished before docking",
              "copying the tide charts posted outside the island post office",
              "keeping Hollis company in the engine room until they docked"],
             1,
             ["She teaches math now; Hollis describes her as a student.",
              "Correct. Hollis says she rode out with her algebra homework and never finished it before they docked.",
              "The tide charts are part of Teo's scenery, not his mother's activity.",
              "Hollis does not say she sat with him in the engine room."],
             "Paragraph 3: “Your mother used to ride out with her algebra homework.”"),
            ("detail",
             "Which of the following changes to the island does Hollis NOT mention?",
             ["The harbor has been dredged twice.",
              "The bakery has come under new owners.",
              "The church steeple has been rebuilt.",
              "A postal worker has finally retired."],
             2,
             ["Hollis does mention this change, so it cannot be the answer.",
              "Hollis does mention this change, so it cannot be the answer.",
              "Correct. The steeple appears only as part of Teo's familiar scenery; Hollis never says it changed.",
              "Hollis does mention this change (Mrs. Petrakis), so it cannot be the answer."],
             "Hollis lists the harbor, the bakery and Mrs. Petrakis; the steeple is never described as changed."),
            ("inference",
             "It can reasonably be inferred from paragraph 5 that the answer Teo had been giving all year was:",
             ["a deliberate lie meant to hide the fact that he was failing his classes",
              "a joke that his friends on the island had not been able to understand",
              "an incomplete account that left out how he really felt about the mainland",
              "an accurate summary that he now regrets having shared with his parents and friends"],
             2,
             ["Nothing suggests he was failing; he was busy and studying late.",
              "The friends are not said to misunderstand anything.",
              "Correct. The dark made it easier to say “something truer,” so the usual answer left things out.",
              "The usual answer was not the whole truth, so it was not simply accurate."],
             "“Something truer” implies the earlier answer was partial rather than false or complete."),
            ("inference",
             "Based on the passage, Hollis most likely believes that people who leave the island and later return:",
             ["should not expect anyone there to remember who they are",
              "can notice changes that year-round residents tend to miss",
              "usually end up regretting that they ever chose to leave",
              "tend to exaggerate how much the island has really changed"],
             1,
             ["Hollis recognizes Teo at once as Ana Reyes's son.",
              "Correct. He says that when you live there you don't see the changes; you must go away to notice.",
              "He describes no regret about leaving.",
              "He says the island does change, so returning islanders are not exaggerating."],
             "Paragraph 7: “You need to go away for a while before you can notice.”"),
            ("vocab",
             "As it is used in paragraph 8, the phrase “pick out” most nearly means:",
             ["select for purchase", "remove by hand", "distinguish", "find fault with"],
             2,
             ["Nothing is being bought.",
              "He is looking from the deck, not removing anything.",
              "Correct. As the lights grow larger, he can distinguish individual shapes.",
              "He is not criticizing what he sees."],
             "To “pick out individual shapes” is to make them out or distinguish them."),
            ("function",
             "The description of the island in paragraph 2 as “a handful of sparks” mainly serves to:",
             ["convey how unexpectedly small the island seems to Teo from the deck",
              "suggest that a fire has recently broken out somewhere on the island",
              "show that Teo is relieved to have finally left the island behind him",
              "indicate that the island's lights have been left on to guide the ferry"],
             0,
             ["Correct. The image contrasts with how “enormous” the island had seemed from the dormitory.",
              "The sparks are a figure of speech for distant lights, not a real fire.",
              "Teo is returning to the island, not glad to have left it.",
              "No one is said to light the way for the ferry."],
             "The figurative image stresses how small the island looks compared with Teo's memory of it."),
            ("structure",
             "Which of the following best describes how the final paragraph relates to paragraph 2?",
             ["It repeats the earlier image to show that Teo's feelings about the island have not changed.",
              "It contradicts Hollis's claim that the island changes only very slowly.",
              "It introduces the island for the first time as Teo sees it from shore.",
              "It revises Teo's earlier impression of the island into a more balanced view."],
             3,
             ["The image is recalled in order to be set aside: the island is “no longer a handful of sparks.”",
              "The last paragraph says nothing about how fast the island changes.",
              "Teo is still on the ferry, and the island was already described in paragraph 2.",
              "Correct. The island is neither tiny sparks nor enormous; it is “simply the size it was.”"],
             "The ending answers paragraph 2's two extremes with a clear-eyed middle view."),
            ("view",
             "The passage suggests that Teo's mother, as she waits in the kitchen, is:",
             ["annoyed that the ferry is running later than scheduled",
              "eager for Teo's return but reluctant to let it show",
              "unaware that her son is coming home on this ferry",
              "busy preparing tomorrow's lessons for her students"],
             1,
             ["No delay or annoyance is mentioned.",
              "Correct. She has let her tea go cold while “pretending not to wait for him.”",
              "Teo knows she is waiting, so she knows he is coming.",
              "Lesson planning is never mentioned."],
             "Paragraph 8: a cold cup of tea and “pretending not to wait” show restrained eagerness."),
        ],
    },
    {
        "id": "the-translator", "genre": "literary", "difficulty": "hard",
        "title": "The Translator",
        "paragraphs": [
            "For most of my childhood I was my father's voice in English, a job no one assigned "
            "me and that I could not have described if anyone had asked. It began, as far as I "
            "can reconstruct, at the counter of a pharmacy when I was seven. My father had a "
            "prescription in one hand and a dictionary in the other, and the pharmacist, a "
            "patient man with a gray mustache, kept repeating a question about allergies more "
            "slowly and more loudly, as though volume were a kind of translation. I said the word "
            "in our language. My father answered. I said his answer in English. The pharmacist "
            "looked at me with an expression I would come to know well: relief mixed with a "
            "faint discomfort, as if he had been rescued by someone too small to be holding the "
            "rope.",

            "After that, I was summoned to banks, to the landlord's office, to parent-teacher "
            "conferences at which I translated my own report card. I became expert in a "
            "vocabulary no other child in my class possessed: escrow, deductible, premium, lien. "
            "I learned that adults say the most important thing last, after a great deal of "
            "preamble, and that if you translate too quickly you miss it. I also learned, though "
            "I would not have put it this way, that the person who carries the words between two "
            "people holds a small and unofficial power. When the landlord said something cruel, I "
            "could soften it. When my father said something proud, I could make it sound polite.",

            "I used that power more often than I like to admit. I told my father the bank teller "
            "had been “very sorry” when she had not been sorry at all. I told my teacher my "
            "father was “very busy at work” when he was, in fact, too embarrassed to sit in a "
            "classroom and be spoken to through his daughter. These were not lies, exactly, or "
            "they were the kind of lies that hold a roof up. I was protecting him, I believed, "
            "and protecting the strangers, too, from the friction of meeting each other without "
            "a cushion.",

            "It took me many years, and in the end a single afternoon, to understand what the "
            "cushion had cost. I was nineteen and home from college, and my father needed to "
            "dispute a bill from the electric company. I had a summer job and could not come, "
            "and so for the first time in my memory he went alone. I spent the afternoon "
            "expecting a phone call that never arrived. When I got home he was at the kitchen "
            "table, the bill flattened under the sugar bowl, a new figure written beside the old "
            "one in his careful hand.",

            "“How did you manage?” I asked, and I could hear in my own voice something I did not "
            "like, a note of surprise that was close to condescension. He looked at me for a long "
            "moment. “I talked,” he said. “She talked. It was slow. Twice we had to start "
            "again.” Then he added, in English, with an accent I had spent years trying to make "
            "invisible on his behalf: “She was nice to me. To me, not to you.”",

            "I have thought about that sentence more than almost anything anyone has ever said to "
            "me. For years I had imagined that I was building a bridge between my father and the "
            "English-speaking world. It had not occurred to me that a bridge can also be a wall, "
            "that by standing in the middle of every conversation, I had made sure no one ever "
            "spoke to him directly. The clerk at the electric company had not been kinder than "
            "the clerks I remembered. She had simply been talking to the person in front of her, "
            "and for the first time, that person was him.",

            "I do not regret the years of translating; I am not sure we would have managed "
            "without them. But I no longer think of them as purely a gift I gave. They were also "
            "something I took, a little at a time, without either of us noticing: the chance for "
            "my father to be clumsy, and patient, and understood on his own terms.",
        ],
        "questions": [
            ("main_idea",
             "Which of the following best states the central idea of the passage?",
             ["The narrator explains why she decided to study languages in college after so many years of translating for her family.",
              "The narrator argues that immigrant families should never rely on their children to translate for them.",
              "The narrator describes how her father taught himself English by studying a dictionary at home.",
              "The narrator realizes that her years of translating, though helpful, also kept her father from speaking for himself."],
             3,
             ["Her college studies are never described.",
              "She makes no general argument; she says she does not regret translating.",
              "The dictionary appears once, at the pharmacy; his learning is not the subject.",
              "Correct. The electric-company visit shows her that her help also stood between her father and others."],
             "The passage builds to the realization that a bridge “can also be a wall.”"),
            ("detail",
             "According to the narrator, the first time she can recall translating for her father was at:",
             ["a bank", "a pharmacy counter", "the landlord's office", "a parent-teacher conference"],
             1,
             ["Banks come later in her list (“After that, I was summoned to banks”).",
              "Correct. Paragraph 1 says it began at the counter of a pharmacy when she was seven.",
              "The landlord's office comes later.",
              "Conferences come later."],
             "“It began, as far as I can reconstruct, at the counter of a pharmacy when I was seven.”"),
            ("detail",
             "According to the father's account in paragraph 5, during his visit to the electric company he and the clerk:",
             ["were helped by a second clerk who spoke his first language",
              "had to start the conversation over twice before finishing",
              "agreed to wait until the narrator could join them by phone",
              "decided to leave the bill as it was and settle it later"],
             1,
             ["No second clerk or shared language is mentioned.",
              "Correct. He says, “It was slow. Twice we had to start again.”",
              "The phone call the narrator expected “never arrived.”",
              "He came home with “a new figure written beside the old one,” so the bill was changed."],
             "The father reports a slow conversation that had to restart twice."),
            ("inference",
             "In paragraph 3, the narrator's comparison of her softened translations to “the kind of lies that hold a roof up” suggests that she viewed them as:",
             ["careless mistakes caused by her limited childhood vocabulary",
              "jokes that she and her father privately enjoyed sharing",
              "protective falsehoods that kept things from falling apart",
              "serious betrayals that she soon confessed to her father"],
             2,
             ["She says she was “expert” in adult vocabulary; the changes were deliberate.",
              "Nothing suggests the changes were jokes shared with her father.",
              "Correct. Like supports holding up a roof, the small lies were meant to protect everyone.",
              "No confession is described."],
             "She believed she was “protecting him” and the strangers from friction."),
            ("inference",
             "The father's comment “To me, not to you” (paragraph 5) most nearly expresses his:",
             ["satisfaction at being treated as the person actually in the conversation",
              "resentment that clerks had always been rude to his daughter in the past",
              "confusion about why the clerk had been so unusually friendly toward him",
              "wish that his daughter had been able to come along and help him that day"],
             0,
             ["Correct. The narrator explains that the clerk was simply talking to the person in front of her, and “that person was him.”",
              "No earlier rudeness toward the daughter is described.",
              "He is not confused; he states plainly that she was nice to him.",
              "His comment stresses what he gained by going alone, not a wish for help."],
             "Paragraph 6 interprets the remark: for the first time he was the one being spoken to."),
            ("vocab",
             "As it is used in paragraph 2, the word “preamble” most nearly means:",
             ["introductory remarks", "legal documents", "angry complaints", "careful translations"],
             0,
             ["Correct. Adults say the important thing last, after much introductory talk.",
              "The word refers to talk before the main point, not to documents.",
              "Nothing about the talk is described as angry.",
              "The adults are speaking, not translating."],
             "Preamble is the talk that comes before the main point."),
            ("function",
             "The narrator lists the words “escrow, deductible, premium, lien” in paragraph 2 primarily to:",
             ["show that she struggled to understand financial language",
              "criticize banks for using needlessly confusing terms",
              "illustrate the unusual adult vocabulary her role gave her",
              "list words that her father had already taught her at home"],
             2,
             ["She calls herself “expert” in these words, not confused by them.",
              "She does not criticize the banks' language.",
              "Correct. These are terms “no other child in my class possessed.”",
              "She learned them by translating, not from her father."],
             "The list demonstrates the specialized vocabulary she acquired."),
            ("structure",
             "Paragraph 6 marks a shift in the passage from:",
             ["describing the narrator's childhood to describing her father's childhood",
              "recounting an event to reflecting on what that event revealed to her",
              "praising the narrator's translations to criticizing the electric company",
              "a hopeful view of the future to a regretful view of the present"],
             1,
             ["The father's childhood is never described.",
              "Correct. After narrating the visit, she reflects on the bridge that was also a wall.",
              "She does not criticize the electric company; its clerk was kind.",
              "The passage is retrospective, not about the future."],
             "Paragraph 6 opens with “I have thought about that sentence…” and turns to reflection."),
            ("view",
             "The narrator's attitude toward her years of translating, as expressed in the final paragraph, is best described as:",
             ["entirely regretful, since she believes the work harmed her father",
              "proud and untroubled, since the work helped her family get by",
              "indifferent, since she seldom thinks about that time anymore",
              "grateful for their necessity but aware of their hidden cost"],
             3,
             ["She says plainly, “I do not regret the years of translating.”",
              "She no longer sees them as “purely a gift,” so she is troubled.",
              "She has thought about that time “more than almost anything.”",
              "Correct. She is not sure they would have managed without it, yet sees what it took from him."],
             "The final paragraph holds both the value and the cost of her role."),
        ],
    },
    # ------------------------------------------------------------------ #
    # Social science
    # ------------------------------------------------------------------ #
    {
        "id": "desire-paths", "genre": "social", "difficulty": "easy",
        "title": "The Paths People Choose",
        "paragraphs": [
            "Walk across almost any college campus or city park and you will find them: narrow "
            "ribbons of bare earth cutting diagonally across the grass, worn smooth by thousands "
            "of shoes. Landscape architects call them desire paths. They appear wherever the "
            "route people want to take differs from the route a designer has paved for them, and "
            "they are, in their quiet way, a form of protest. Each one records a small decision "
            "made again and again by people who will never meet: the paved path goes around, but "
            "I am going through.",

            "For a long time, the standard response to desire paths was to fight them. "
            "Groundskeepers put up fences, planted hedges, and posted signs asking pedestrians to "
            "keep off the grass. These measures rarely worked for long. A sign can be ignored, "
            "and a hedge, sooner or later, develops a gap exactly the width of a person. The "
            "trouble was not that people were careless. It was that the paved paths had been "
            "laid out according to what looked orderly on a drawing, with neat right angles and "
            "symmetrical loops, rather than according to where people actually needed to go.",

            "Some designers began to wonder whether the paths might be useful rather than merely "
            "annoying. If thousands of people independently chose the same shortcut, perhaps "
            "they were collectively solving a problem the designers had missed. A few "
            "universities have taken this idea to its logical conclusion. Rather than paving "
            "walkways when a new building opens, they plant the surrounding area with grass and "
            "wait. Over a season or two, students wear their own routes into the lawn. Only then "
            "do the planners pour concrete, following the lines the walkers have drawn. The "
            "result can look a little unusual from above, with walkways that branch at odd "
            "angles, but the grass on either side stays green because no one has a reason to "
            "leave the path.",

            "The approach has an obvious appeal. It costs little, it produces paths that people "
            "will actually use, and it treats pedestrians as experts in their own movement. It "
            "also reflects a broader shift in how planners think about public space. Older "
            "approaches often began with a fixed vision and expected people to conform to it. "
            "Newer ones are more likely to start by observing behavior, such as counting foot "
            "traffic, watching where people pause, and noticing which benches go unused, and to "
            "treat that behavior as evidence rather than as a problem to be corrected.",

            "Still, desire paths are not always a reliable guide. A shortcut that saves a few "
            "seconds on a dry afternoon may become a mud slide in the spring, and a route that "
            "suits students in a hurry may be too steep or uneven for someone using a wheelchair "
            "or pushing a stroller. Some paths form simply because one person cut a corner and "
            "others followed the visible trail, not because the route was especially efficient. "
            "In those cases, the path records habit more than need.",

            "There is also the question of what gets lost. A lawn crisscrossed with paths is a "
            "lawn with less grass, and in some places the ground being worn away is not "
            "ornamental turf but fragile habitat. In national parks, rangers work hard to keep "
            "visitors on marked trails precisely because shortcuts can erode hillsides and "
            "damage plants that take decades to recover. What counts as a sensible shortcut in a "
            "city park may be a scar in a wilderness.",

            "Perhaps the most useful lesson of desire paths, then, is not that the crowd is "
            "always right but that the crowd is always communicating. A worn strip of earth is "
            "information. It tells designers where their plans and people's needs have come "
            "apart. Sometimes the right response is to pave the path; sometimes it is to make "
            "the official route more appealing; occasionally it is to put up the fence after "
            "all. But ignoring the message entirely is rarely the right choice.",
        ],
        "questions": [
            ("main_idea",
             "The main purpose of the passage is to:",
             ["argue that every walkway should be built only after people have worn their own paths",
              "explain what desire paths reveal and discuss how planners might best respond to them",
              "describe one university's long struggle to protect its lawns from careless students",
              "criticize pedestrians who ignore signs and damage the grass in public parks"],
             1,
             ["The author notes cases where paving a desire path would be wrong, so “every” overstates the view.",
              "Correct. The passage defines desire paths, weighs responses to them, and concludes they are information.",
              "No single university's struggle is described; the passage says people were not careless.",
              "The author explicitly says “The trouble was not that people were careless.”"],
             "The passage explains the phenomenon and evaluates a range of responses."),
            ("detail",
             "According to the passage, some universities that use desire paths in planning:",
             ["fence off new lawns until students agree to use only the paved walkways",
              "ask students to vote on where each new walkway should be built",
              "plant grass around a new building and pave the routes students wear",
              "pave every possible route at once so that no shortcuts can form"],
             2,
             ["Fences are part of the old approach of fighting the paths.",
              "No voting is described; students show their routes by walking.",
              "Correct. Paragraph 3: they plant grass, wait, then pour concrete along the worn lines.",
              "They wait before paving anything, rather than paving everything."],
             "Paragraph 3 describes planting grass and paving the worn routes later."),
            ("detail",
             "The passage states that rangers in national parks keep visitors on marked trails because shortcuts:",
             ["make it harder for rangers to count foot traffic",
              "can erode hillsides and damage slow-growing plants",
              "cause visitors to become lost on unmarked routes",
              "cost far more to maintain than the paved walkways do"],
             1,
             ["Counting foot traffic is mentioned for planners, not rangers.",
              "Correct. Paragraph 6 says shortcuts can erode hillsides and damage plants that take decades to recover.",
              "Getting lost is never mentioned.",
              "Maintenance costs in parks are never discussed."],
             "Paragraph 6 gives erosion and plant damage as the reason."),
            ("inference",
             "Based on paragraph 2, the author would most likely agree that earlier efforts to stop desire paths failed mainly because:",
             ["groundskeepers did not post enough signs to inform passing pedestrians",
              "pedestrians in the past were more careless than they are today",
              "the paved routes did not match where people actually needed to go",
              "hedges were too expensive for most parks and campuses to plant"],
             2,
             ["The author says signs can simply be ignored; more of them would not fix the design.",
              "The author states “The trouble was not that people were careless.”",
              "Correct. The paths were laid out to look orderly on a drawing, not to match real routes.",
              "Cost is not given as the reason hedges failed; people wore gaps in them."],
             "The author locates the problem in the design, not the people."),
            ("inference",
             "The author suggests that a desire path formed because “one person cut a corner and others followed” is one that:",
             ["may reflect people's habit of following a trail more than a real need",
              "is the most efficient route that planners could possibly choose",
              "should be fenced off at once to protect any fragile habitat",
              "will probably disappear without any action within a season"],
             0,
             ["Correct. The author says such a path “records habit more than need.”",
              "The author says this kind of path forms “not because the route was especially efficient.”",
              "Fencing and habitat are raised separately, not as the response to this kind of path.",
              "Nothing suggests these paths vanish on their own."],
             "Paragraph 5 contrasts habit-made paths with routes that reflect real need."),
            ("vocab",
             "As it is used in paragraph 4, the word “conform” most nearly means:",
             ["adapt their behavior", "sign a formal agreement", "give a shape to", "complain openly"],
             0,
             ["Correct. Older plans expected people to adapt to a fixed vision.",
              "No written agreement is involved.",
              "People are expected to fit the plan, not to shape it.",
              "Conforming is the opposite of protesting."],
             "To conform to a vision is to adjust one's behavior to fit it."),
            ("function",
             "The author's reference to wheelchairs and strollers in paragraph 5 mainly serves to:",
             ["argue that every campus walkway should be paved with concrete",
              "show that a popular shortcut may not suit everyone who uses a space",
              "explain why desire paths most often appear in city parks and lawns",
              "illustrate how quickly worn grass can recover after heavy foot traffic"],
             1,
             ["The author does not call for paving everything.",
              "Correct. A route that suits hurried students may be too steep or uneven for others.",
              "The example is about who can use a path, not where paths appear.",
              "Grass recovery is not the point of the example."],
             "The example shows a limit of treating desire paths as a guide."),
            ("structure",
             "Which of the following best describes the structure of the passage as a whole?",
             ["It presents a problem, offers a single solution, and dismisses all objections to it.",
              "It tells the story of one city park and then compares it with several national parks nearby.",
              "It lists, in order, the steps a planner should follow when designing a new walkway.",
              "It defines a phenomenon, traces changing responses to it, notes limits, and concludes."],
             3,
             ["The author raises objections (mud, access, habitat) and takes them seriously.",
              "No single park's story is told.",
              "The passage is not a set of instructions.",
              "Correct. Definition (1), old and new responses (2-4), limits (5-6), conclusion (7)."],
             "The passage moves from definition to responses to limitations to a closing lesson."),
            ("view",
             "The author's attitude toward using desire paths to guide design can best be described as:",
             ["enthusiastic and without any reservations",
              "skeptical to the point of rejecting the idea",
              "favorable but tempered by its limitations",
              "neutral, since the author takes no position"],
             2,
             ["The author devotes two paragraphs to the approach's limits.",
              "The author calls the approach appealing and says ignoring the paths is rarely right.",
              "Correct. The author values the paths as information while noting when they mislead.",
              "The author clearly takes a position in the final paragraph."],
             "The approach “has an obvious appeal,” yet desire paths “are not always a reliable guide.”"),
        ],
    },
    {
        "id": "value-of-effort", "genre": "social", "difficulty": "medium",
        "title": "The Value of Effort",
        "paragraphs": [
            "Anyone who has spent an evening assembling a bookcase from a flat box knows the "
            "peculiar pride that follows. The shelves may lean slightly; there may be a "
            "mysterious screw left over. Yet the finished piece feels more valuable than an "
            "identical bookcase delivered fully built. Behavioral researchers have given this "
            "feeling a name, sometimes calling it the “IKEA effect” after the furniture company "
            "famous for selling products that customers put together themselves, and they have "
            "spent a good deal of effort trying to understand it.",

            "In a typical experiment, participants are asked to build something simple: a "
            "storage box, a folded paper animal, a small set of plastic bricks. Afterward, they "
            "are asked how much they would pay for their own creation. Other participants, who "
            "did not build anything, are asked to price the same objects. Again and again, "
            "builders place a higher value on their own work than non-builders do. In some "
            "versions of the study, builders priced their own lopsided creations at nearly the "
            "same level as versions made by skilled hobbyists. The effect appears even when the "
            "builders' results are noticeably clumsy.",

            "Why should labor make an object seem more valuable? One explanation draws on an "
            "older idea in psychology called effort justification. People tend to dislike "
            "believing that they have wasted their time or energy. When we work hard for "
            "something, we resolve that discomfort, often without realizing it, by deciding that "
            "the thing must have been worth the work. The more we invest, the more we need the "
            "investment to have been wise. Psychologists have observed related patterns "
            "elsewhere: people who endure a difficult initiation to join a group, for instance, "
            "often report liking the group more than those who joined easily.",

            "A second explanation focuses on competence. Completing a task, even a small one, is "
            "a demonstration to ourselves that we are capable. The finished object becomes a "
            "kind of trophy, a physical reminder of a skill successfully exercised. Consistent "
            "with this view, the effect seems to depend on actually finishing. In some studies, "
            "participants who built an object and then took it apart, or who were stopped before "
            "completing it, valued it no more highly than people who had never touched it.",

            "Marketers noticed these findings quickly. Meal kits that arrive as a box of raw "
            "ingredients and a recipe card, toys that must be assembled before they can be "
            "played with, craft sets that leave the final steps to the buyer: all of these, "
            "whatever else they offer, give the customer a small role in production. Some "
            "historians of advertising have suggested that early instant cake mixes sold better "
            "once the recipe was changed to require a fresh egg, though the story is often told "
            "more neatly than the evidence supports. Either way, the customer does a little of "
            "the work and, in exchange, may feel a little more attached to the result.",

            "But the same tendency that makes a homemade bookcase feel special can also lead "
            "people astray. Managers sometimes overvalue projects they designed themselves and "
            "continue funding them long after the evidence suggests they should stop. Writers "
            "may be reluctant to cut a paragraph that took hours to draft, even when it weakens "
            "the piece. Because the value we assign to our work is partly a reflection of the "
            "effort we spent, our judgments about that work are not entirely about the work "
            "itself. Homeowners who renovate a house themselves may likewise expect buyers to "
            "pay for the hours they spent, not just for the result.",

            "None of this means that pride in one's own labor is foolish. The satisfaction of "
            "making something, and the attachment that follows, are among the ordinary pleasures "
            "of being human, and they may encourage people to learn skills and take care of what "
            "they own. The point is narrower: when we evaluate something we have built, we are "
            "not neutral judges. Knowing that can help us enjoy the crooked bookcase while still "
            "noticing that it leans.",
        ],
        "questions": [
            ("main_idea",
             "Which of the following best states the main idea of the passage?",
             ["Furniture that customers assemble at home is usually of lower quality than furniture sold fully built.",
              "Marketers have tricked customers into doing work that companies ought to pay their employees to do.",
              "People tend to value things more after working to make them, a tendency with benefits and pitfalls.",
              "Psychologists have concluded that pride in one's own work is a harmful and irrational habit."],
             2,
             ["Furniture quality is not compared; the bookcase is only an opening example.",
              "The author describes marketing neutrally and never calls it trickery.",
              "Correct. The passage explains the effect, its causes, its uses, and its risks.",
              "The last paragraph says pride in one's labor is not foolish."],
             "The passage defines the effect, explains it, and weighs its good and bad consequences."),
            ("detail",
             "According to the passage, participants in the experiments described in paragraph 2 who had built an object:",
             ["were usually unable to finish it in the time they were given",
              "valued it more highly than participants who had built nothing",
              "preferred to buy versions of the object made by skilled experts",
              "priced it lower once they noticed how clumsy their work was"],
             1,
             ["Nothing says they failed to finish.",
              "Correct. “Builders place a higher value on their own work than non-builders do.”",
              "Builders priced their own work near the experts' versions; no preference for experts is described.",
              "The effect appears “even when the builders' results are noticeably clumsy.”"],
             "Paragraph 2 reports that builders consistently valued their own creations more."),
            ("detail",
             "According to paragraph 4, participants who built an object and then took it apart:",
             ["valued it even more than people who had kept theirs whole",
              "asked to build a second, sturdier version of the object",
              "valued it no more highly than people who never touched it",
              "lost interest in the experiment and left before it ended"],
             2,
             ["The passage says the opposite: their valuation did not rise.",
              "No second version is mentioned.",
              "Correct. They valued it “no more highly than people who had never touched it.”",
              "Nothing says anyone left the experiment."],
             "Paragraph 4 uses this result to support the competence explanation."),
            ("inference",
             "The author's comment on the cake mix story in paragraph 5 suggests that the author:",
             ["considers the story plausible but doubts that it is as tidy as often told",
              "believes the story proves beyond any reasonable doubt that the effect is real",
              "thinks the story was invented recently by modern advertising firms",
              "views baking as an unusually difficult and time-consuming task"],
             0,
             ["Correct. The story is “often told more neatly than the evidence supports.”",
              "The author hedges the story, so it is not offered as proof.",
              "The author attributes the story to historians and does not call it invented.",
              "The difficulty of baking is not discussed."],
             "The author repeats the story with a clear caution about the evidence."),
            ("inference",
             "Based on paragraph 6, the author would most likely say that a manager who keeps funding a failing project of her own design is:",
             ["showing admirable loyalty to the employees on her team",
              "letting her investment of effort distort her judgment",
              "following the most reliable evidence that is available",
              "unaware of how much money the project has already cost"],
             1,
             ["Loyalty to employees is not discussed.",
              "Correct. The author says such managers overvalue their own projects because of the effort spent.",
              "She continues “long after the evidence suggests” stopping, so she is not following it.",
              "The problem described is biased judgment, not missing information."],
             "Paragraph 6: judgments about our own work “are not entirely about the work itself.”"),
            ("vocab",
             "As it is used in paragraph 3, the word “resolve” most nearly means:",
             ["firmly decide", "ease or settle", "break into parts", "make clearer to see"],
             1,
             ["“Firmly decide” is another sense of resolve, but one does not decide a discomfort.",
              "Correct. People settle the discomfort of wasted effort by valuing the result.",
              "Nothing is being separated into parts.",
              "The sense is not about sharpness of an image."],
             "To resolve a discomfort is to relieve or settle it."),
            ("function",
             "The author most likely includes the examples of meal kits and toys in paragraph 5 in order to:",
             ["prove that most customers prefer to cook their own meals",
              "contrast products that require assembly with those that do not",
              "explain why the effect fades once an object has been completed",
              "show how businesses build a small customer role into products"],
             3,
             ["Customer cooking preferences are not claimed.",
              "No contrasting set of ready-made products is offered.",
              "Paragraph 4 says the effect depends on finishing; it does not fade on completion.",
              "Correct. Each example gives the customer “a small role in production.”"],
             "The examples illustrate marketers' use of the effect."),
            ("structure",
             "The last paragraph functions mainly to:",
             ["introduce a new experiment that contradicts the earlier findings",
              "qualify the warning in paragraph 6 by affirming pride in one's work",
              "summarize the history of the company named in the first paragraph",
              "argue that people should avoid building their own furniture"],
             1,
             ["No new experiment is introduced.",
              "Correct. After the warning, it says pride is not foolish and narrows the point.",
              "The company is not discussed again.",
              "The author encourages enjoying the crooked bookcase."],
             "“None of this means that pride in one's own labor is foolish. The point is narrower…”"),
            ("view",
             "Which choice best describes the author's tone in the passage?",
             ["alarmed and urgent in its warnings",
              "bitter and openly sarcastic toward marketers",
              "sentimental and nostalgic about craftsmanship",
              "measured and explanatory, with a light touch"],
             3,
             ["The warnings in paragraph 6 are calm and are qualified in paragraph 7.",
              "Marketing is described without sarcasm.",
              "The author is not longing for the past.",
              "Correct. The author explains evenly, with gentle humor about leftover screws and leaning shelves."],
             "Even-handed explanation plus small jokes (the mysterious screw, the crooked bookcase) set the tone."),
        ],
    },
    {
        "id": "keeping-a-language", "genre": "social", "difficulty": "hard",
        "title": "Keeping a Language Alive",
        "paragraphs": [
            "When linguists speak of a language as endangered, they rarely mean that its words "
            "are disappearing from dictionaries. Dictionaries, after all, can preserve a "
            "language indefinitely, in the way a museum preserves a fossil. What linguists mean "
            "is that fewer and fewer children are learning it at home. A language can have tens "
            "of thousands of speakers and still be in danger if almost all of those speakers are "
            "grandparents; it can have only a few hundred and be relatively secure if those few "
            "hundred include toddlers. The crucial measure is not size but transmission: whether "
            "the language is being handed from one generation to the next.",

            "Transmission tends to break down for reasons that have little to do with the "
            "language itself. When a family moves to a city, when schools teach in a single "
            "national language, when jobs and opportunity seem to require a different tongue, "
            "parents often make a reasonable calculation: their children will be better served by "
            "the language of power. Sometimes the calculation is forced on them. In many "
            "countries, children were punished in school for speaking their home language well "
            "into the twentieth century, and the shame attached to that punishment could last "
            "long after the policy ended.",

            "Efforts to reverse this process, known as language revitalization, have multiplied "
            "in recent decades, and they have taught advocates some uncomfortable lessons. The "
            "first is that documentation, however valuable, is not the same as revival. "
            "Recording elderly speakers, compiling grammars, and archiving stories can preserve "
            "an extraordinary amount of knowledge, and these materials are often indispensable "
            "to later learners. But a language that exists only in recordings is, in an "
            "important sense, no longer being used to do anything: to argue, to joke, to comfort "
            "a child at night.",

            "The second lesson is that classroom instruction alone rarely produces fluent "
            "speakers. A child who studies a heritage language for an hour a day, then spends "
            "the rest of the day in the dominant language, may learn a great deal about it "
            "without ever coming to think in it. For this reason, some of the most closely "
            "watched programs are immersion programs, in which young children spend the entire "
            "school day, and sometimes much of their home life, in the language being revived. "
            "The approach demands enormous resources: teachers who are fluent, materials that "
            "must often be written from scratch, and families willing to commit to it.",

            "A third lesson concerns what counts as success. Revitalized languages almost always "
            "change. New learners, many of whom grew up speaking another language first, bring "
            "with them sounds, idioms, and patterns of grammar from that language. Elders "
            "sometimes find the speech of younger speakers jarring, even incorrect. Linguists "
            "who study these situations tend to be less troubled. Every living language "
            "changes, they point out, and a language spoken imperfectly by children is in a far "
            "stronger position than one spoken perfectly by no one.",

            "This view is not universally shared, and the disagreement is not merely academic. "
            "For some communities, the purpose of revitalization is to recover a connection with "
            "ancestors, and a language that has drifted far from the speech of those ancestors "
            "may feel like a loss disguised as a gain. For others, the purpose is to give the "
            "language a future, and change is the price of that future. Both positions reflect "
            "real values, and the programs that seem to last are often those that make room for "
            "both, treating elders as the keepers of an authoritative tradition while allowing "
            "young speakers to make the language their own.",

            "What revitalization cannot do is simply restore the past. A language that returns "
            "from the edge of disappearance returns into a different world from the one it left. "
            "That may be the most important lesson of all: a revived language is not a relic "
            "brought back to life but a new chapter in an old story, written by people who "
            "decided the story was worth continuing.",
        ],
        "questions": [
            ("main_idea",
             "The passage is primarily concerned with:",
             ["the history of how dictionaries came to preserve rare and ancient languages",
              "the reasons national governments chose to adopt a single official language",
              "a detailed comparison of the grammar of several endangered languages",
              "the challenges and lessons of efforts to keep endangered languages in use"],
             3,
             ["Dictionaries appear only as a comparison in paragraph 1.",
              "National language policy is one cause mentioned briefly in paragraph 2.",
              "No specific languages or grammars are compared.",
              "Correct. The passage defines endangerment and walks through revitalization's lessons."],
             "Most of the passage is organized around the “lessons” of revitalization."),
            ("detail",
             "According to the passage, the most important measure of whether a language is endangered is:",
             ["the total number of people who are able to speak it",
              "whether children are learning it from the generation before",
              "whether a complete dictionary of it has been compiled",
              "how many of its speakers have moved away from home to large cities"],
             1,
             ["The author says “The crucial measure is not size.”",
              "Correct. “The crucial measure is not size but transmission.”",
              "Dictionaries can preserve a language that is no longer spoken.",
              "Moving to cities is a cause of decline, not the measure of it."],
             "Paragraph 1 names transmission between generations as the crucial measure."),
            ("detail",
             "According to paragraph 4, immersion programs require all of the following EXCEPT:",
             ["teachers who speak the language fluently",
              "learning materials that are often newly written",
              "families willing to commit to the program",
              "approval from a national language authority"],
             3,
             ["Fluent teachers are listed, so this is not the exception.",
              "Materials “written from scratch” are listed, so this is not the exception.",
              "Committed families are listed, so this is not the exception.",
              "Correct. No national authority is mentioned among the program's demands."],
             "Paragraph 4 lists fluent teachers, new materials and committed families."),
            ("inference",
             "It can reasonably be inferred from paragraph 2 that the author regards parents who stop speaking a heritage language to their children as:",
             ["careless about their family's traditions and history",
              "often making a sensible choice in difficult conditions",
              "unaware that their children are learning another language",
              "responsible for the language policies of their schools"],
             1,
             ["The author calls their decision “a reasonable calculation,” not carelessness.",
              "Correct. The author describes a reasonable calculation, sometimes forced on them.",
              "The parents choose the other language deliberately.",
              "The schools' policies are described as imposed on families."],
             "The author treats the parents' choice sympathetically."),
            ("inference",
             "Based on paragraph 5, linguists would most likely respond to an elder's complaint that young speakers use the language incorrectly by noting that:",
             ["young speakers should be corrected until they sound like the elders",
              "the elders' own version of the language was never truly authentic",
              "documentation is a more reliable way to preserve any language",
              "change is normal in any language that people actually speak"],
             3,
             ["Linguists are “less troubled” by the changes, not eager to correct them.",
              "Linguists do not challenge the elders' authenticity.",
              "Paragraph 3 says documentation is not the same as revival.",
              "Correct. “Every living language changes, they point out.”"],
             "The linguists' reply rests on the normality of change."),
            ("vocab",
             "As it is used in paragraph 5, the word “jarring” most nearly means:",
             ["unsettling", "stored in containers", "loud and violent", "surprisingly pleasant"],
             0,
             ["Correct. Elders find the new speech disturbing, “even incorrect.”",
              "This literal sense of “jar” does not fit speech.",
              "Nothing suggests the speech is loud or violent.",
              "The elders object to the speech, so it is not pleasant to them."],
             "Jarring speech is speech that strikes the listener as off or disturbing."),
            ("function",
             "The comparison of a dictionary to a museum preserving a fossil (paragraph 1) primarily serves to:",
             ["praise dictionaries as the best way to rescue endangered languages",
              "suggest that recording a language differs from keeping it alive",
              "explain how linguists first became interested in ancient languages",
              "argue that museums should collect recordings of rare languages"],
             1,
             ["A fossil is preserved but not alive, so the comparison is not praise.",
              "Correct. A fossil is kept but no longer living, like a language that only survives on paper.",
              "The origins of linguists' interest are not discussed.",
              "Museums are a comparison here, not a proposal."],
             "The image prepares the distinction between documentation and revival."),
            ("structure",
             "Paragraph 6 primarily serves to:",
             ["reject the linguists' view described in paragraph 5 as mistaken",
              "describe the funding problems faced by immersion programs",
              "present two community aims and how lasting programs balance them",
              "summarize the reasons that languages become endangered at all"],
             2,
             ["The author says “Both positions reflect real values,” rather than rejecting one.",
              "Funding is discussed in paragraph 4, not here.",
              "Correct. It contrasts connection-to-ancestors with giving the language a future, and notes programs that make room for both.",
              "Causes of endangerment are in paragraph 2."],
             "Paragraph 6 lays out a disagreement and a way programs reconcile it."),
            ("view",
             "In the final paragraph, the author characterizes a revived language as:",
             ["an exact recovery of the language as it was once spoken long ago",
              "a failure, since it differs from the original language",
              "a continuation shaped by the choices of present speakers",
              "a museum piece of interest mainly to scholars"],
             2,
             ["The author says revitalization “cannot … simply restore the past.”",
              "The author calls it “a new chapter,” not a failure.",
              "Correct. It is “a new chapter in an old story, written by people who decided the story was worth continuing.”",
              "That is the opposite of the living language the author describes."],
             "The final paragraph frames revival as continuation rather than restoration."),
        ],
    },
    # ------------------------------------------------------------------ #
    # Humanities
    # ------------------------------------------------------------------ #
    {
        "id": "quilts-as-archives", "genre": "humanities", "difficulty": "easy",
        "title": "Stitched Records",
        "paragraphs": [
            "In the back room of a small county museum, a quilt lies folded in acid-free tissue, "
            "brought out only a few times a year. At first glance it is an ordinary object: a "
            "grid of fabric squares, faded in places, its stitches slightly uneven near one "
            "corner. But to the historians who study it, the quilt is something closer to a "
            "document. Each square was cut from clothing worn by members of a single farming "
            "family over roughly forty years. Read carefully, it records births, weddings, hard "
            "winters, and at least one year of unusual prosperity.",

            "Historians have not always taken quilts seriously. For a long time, the objects "
            "that filled history books were the ones that powerful people left behind: letters, "
            "laws, ledgers, monuments. Women who worked at home, especially poor and rural women, "
            "rarely wrote memoirs or kept diaries that survived. Their lives were recorded "
            "instead in the things they made, and those things were often treated as decoration "
            "rather than evidence. A quilt might be admired for its colors and then put away, its "
            "story unasked. Historians who went looking for those women's lives often found "
            "that the written record simply went quiet.",

            "That attitude began to change in the second half of the twentieth century, as "
            "historians grew more interested in ordinary lives and as museums began to collect "
            "everyday objects with new seriousness. Researchers discovered that quilts could "
            "answer questions that written records left blank. The fabrics in a quilt can often "
            "be dated by their dyes and printing methods, which changed over time in known ways. "
            "A sudden appearance of expensive imported cloth might signal a good harvest; a "
            "quilt pieced entirely from feed sacks might suggest a family stretching every "
            "resource.",

            "The stitching itself can be revealing. Some quilts show the work of several "
            "different hands, with tight, regular stitches in one section and looser ones in "
            "another, suggesting that they were made collectively, perhaps at a gathering where "
            "neighbors worked side by side. Others contain names or initials embroidered into "
            "individual squares, a practice that turned a quilt into something like a signed "
            "petition or a guest book. In some communities, quilts were given to departing "
            "friends, each square contributed by a different person, so that the traveler "
            "carried a whole neighborhood along.",

            "None of this means that a quilt can be read as simply as a letter. Its “language” "
            "is ambiguous, and historians must be careful not to invent stories that the "
            "evidence will not support. A dark square might mark a death in the family, or it "
            "might simply be the only fabric that was available that week. Popular legends have "
            "sometimes attached dramatic meanings to quilt patterns with little proof behind "
            "them. Responsible researchers combine what the quilt itself shows with other "
            "sources, such as census records, local newspapers, and family recollections, and "
            "acknowledge what remains uncertain.",

            "For the families who made them, of course, most quilts were not meant to be "
            "evidence of anything. They were meant to keep people warm. That practical purpose "
            "is part of what makes them so valuable to historians now. Because quilts were made "
            "for use rather than for posterity, they capture the texture of daily life without "
            "the polish that people tend to apply when they know they are being recorded. A "
            "diary may be written for future readers; a blanket is written, so to speak, for a "
            "cold night.",

            "The quilt in the county museum will probably never be used on a bed again. Visitors "
            "who come to see it are shown not only the pattern but a chart identifying, as nearly "
            "as researchers can tell, whose shirt or dress each square came from. Some squares "
            "are still labeled with a question mark. The museum's curators have decided to leave "
            "those question marks in place, on the principle that an honest gap in a record is "
            "better than a confident guess.",
        ],
        "questions": [
            ("main_idea",
             "The main idea of the passage is that:",
             ["quilts made by farming families were more skillfully stitched than those made in towns",
              "museums should display their quilts more often instead of keeping them in back rooms",
              "quilts, once treated as decoration, can serve as valuable if imperfect historical evidence",
              "written records are no longer considered useful sources by most professional historians today"],
             2,
             ["No comparison of farm and town quilts is made.",
              "Display policy is not the author's concern.",
              "Correct. The passage explains how quilts became evidence and how carefully they must be read.",
              "Researchers combine quilts with written records such as census data."],
             "The passage traces quilts' shift from decoration to evidence, with cautions."),
            ("detail",
             "According to the passage, the fabrics in a quilt can often be dated by:",
             ["the number of squares the quilt contains",
              "their dyes and printing methods",
              "the names embroidered into each square",
              "the census records of the maker's county"],
             1,
             ["The number of squares says nothing about dates.",
              "Correct. Paragraph 3 says dyes and printing methods changed over time in known ways.",
              "Embroidered names identify people, not fabric dates.",
              "Census records are a separate source used alongside quilts."],
             "Paragraph 3: fabrics “can often be dated by their dyes and printing methods.”"),
            ("detail",
             "According to paragraph 4, quilts given to departing friends in some communities were special because:",
             ["the traveler could sell them for money during the journey",
              "each square had been contributed by a different person",
              "they recorded the route the traveler was planning to take",
              "only the traveler's closest relatives were allowed to sew them"],
             1,
             ["Selling the quilts is never mentioned.",
              "Correct. Each square came from a different person, so the traveler “carried a whole neighborhood along.”",
              "No route is recorded in the quilts.",
              "The squares came from many people, not only relatives."],
             "Paragraph 4: “each square contributed by a different person.”"),
            ("inference",
             "It can most reasonably be inferred from paragraph 2 that historians in earlier periods:",
             ["overlooked sources that recorded the lives of women who worked at home",
              "studied quilts more closely than they studied letters, laws, and ledgers",
              "believed that rural women had written many diaries that were later lost",
              "refused to visit small county museums to examine their collections"],
             0,
             ["Correct. The things these women made were treated as decoration rather than evidence.",
              "The passage says the reverse: quilts were not taken seriously.",
              "The passage says such diaries rarely existed or survived, not what historians believed.",
              "Visits to museums are not discussed."],
             "Paragraph 2 says women's lives were recorded in objects historians treated as decoration."),
            ("inference",
             "The curators' decision to leave question marks on some squares (paragraph 7) suggests that they:",
             ["plan to remove the uncertain squares from the quilt soon",
              "doubt that the quilt was really made by a single family",
              "value honesty about what is unknown over a fuller story",
              "were unable to pay for any further research on the quilt"],
             2,
             ["Nothing suggests altering the quilt itself.",
              "The single-family origin is presented as established.",
              "Correct. They believe “an honest gap in a record is better than a confident guess.”",
              "Funding is never mentioned."],
             "The stated principle is honesty about gaps."),
            ("vocab",
             "As it is used in paragraph 6, the word “posterity” most nearly means:",
             ["public display", "future generations", "careful decoration", "personal wealth"],
             1,
             ["Display is not the contrast being drawn.",
              "Correct. Quilts were made for use, not for future readers.",
              "Decoration is not the sense here.",
              "Wealth is not the sense here."],
             "The contrast with a diary “written for future readers” fixes the meaning."),
            ("function",
             "The author includes the example of a dark square in paragraph 5 most likely to:",
             ["prove that the family suffered a death during a hard winter",
              "illustrate how a quilt's details can support several readings",
              "show that dark fabrics were the most expensive ones available",
              "explain how historians date fabrics by their dyes and prints"],
             1,
             ["The point is that the square might not mean a death.",
              "Correct. A dark square might mark a death or simply be the only fabric available.",
              "Fabric prices are not the point of the example.",
              "Dating by dye is discussed in paragraph 3, not here."],
             "The example demonstrates the ambiguity of a quilt's “language.”"),
            ("structure",
             "The final sentence of paragraph 6, “a blanket is written, so to speak, for a cold night,” mainly serves to:",
             ["suggest that quilts were used more in winter than in summer",
              "argue that diaries are less reliable than official records",
              "contrast a quilt's practical purpose with a diary's audience",
              "introduce the idea that quilts were sometimes sent as letters"],
             2,
             ["Seasonal use is not the point; the image is about purpose.",
              "Official records are not part of this comparison.",
              "Correct. Diaries may be written for future readers; quilts were made for use.",
              "Quilts as letters are not introduced."],
             "The sentence sums up the paragraph's contrast between use and posterity."),
            ("view",
             "The author's attitude toward the popular legends mentioned in paragraph 5 is best described as:",
             ["cautious, since many lack solid proof",
              "enthusiastic, since they attract visitors",
              "dismissive of all quilt history as legend",
              "unsure whether quilts carry any meaning"],
             0,
             ["Correct. The legends attach dramatic meanings “with little proof behind them.”",
              "The author never praises the legends.",
              "The author treats quilt history as real evidence when handled carefully.",
              "The whole passage argues quilts carry meaning."],
             "The author warns against inventing stories the evidence will not support."),
        ],
    },
    {
        "id": "music-for-silents", "genre": "humanities", "difficulty": "medium",
        "title": "Music for Silent Pictures",
        "paragraphs": [
            "The phrase “silent film” has always been something of a misnomer. In the decades "
            "before synchronized sound arrived in the late 1920s, almost no one watched a movie "
            "in silence. In large city theaters, orchestras of thirty or more musicians played "
            "elaborate scores. In small-town movie houses, a single pianist or organist sat "
            "below the screen, often playing for several hours a day, six or seven days a week. "
            "The pictures were silent; the experience of seeing them was anything but.",

            "What these musicians did is difficult to reconstruct, because much of it was never "
            "written down. Studios sometimes distributed cue sheets suggesting appropriate pieces "
            "for each scene, such as a lively march for a parade or something mournful for a "
            "deathbed, and publishers sold thick anthologies of short, adaptable pieces sorted by "
            "mood. But many accompanists, especially in smaller theaters, improvised. They "
            "watched the screen and made up music to fit it, shifting key and tempo as a chase "
            "gave way to a love scene or a storm broke over a ship at sea. A good accompanist "
            "could make an audience laugh at a pratfall a split second before it happened, or "
            "hold a room perfectly still.",

            "The work demanded an unusual combination of skills. An accompanist needed a large "
            "repertoire, a quick ear, and the stamina to play through a whole program without a "
            "break. Above all, he or she needed to watch the film as closely as any audience "
            "member while performing for that audience at the same time. Accompanists spoke of "
            "“catching” a film, as if it were something moving that had to be met at exactly the "
            "right moment. A beat too late, and a joke fell flat; a mood held too long, and a "
            "tragedy turned comic.",

            "When synchronized sound arrived, these musicians lost their jobs with remarkable "
            "speed. Within a few years, thousands of theater musicians across the country were "
            "out of work, replaced by recorded soundtracks that were identical at every showing. "
            "Some found work in radio or in the new sound studios, but they were the fortunate "
            "few. Musicians' unions protested, sometimes with newspaper advertisements warning "
            "audiences that “canned music” would make films colder and cheaper. The public, "
            "delighted by the novelty of hearing actors speak, largely did not listen.",

            "It would be easy to tell this story as a simple loss, and in many ways it was one. "
            "But it is worth noticing what was gained along with what disappeared. A recorded "
            "score allowed filmmakers to control exactly what audiences heard, so that a film in "
            "a small town sounded the same as a film in a grand theater. Composers could write "
            "music shaped to every second of a scene, knowing it would be played precisely the "
            "same way each time. Much of the film music that audiences now admire depends on "
            "that precision.",

            "What disappeared was something harder to name: the sense that each showing was a "
            "live event, shaped in part by the person at the piano and by the room itself. An "
            "accompanist could respond to a particular audience, stretching a gag that was "
            "getting big laughs or hurrying through a scene that had the crowd restless. No two "
            "screenings were quite the same. Musicians who played the same film all week often "
            "said that no two audiences laughed in exactly the same places. The film was fixed; the performance around it was "
            "not.",

            "In recent decades, that older experience has enjoyed a modest revival. Film "
            "festivals and archives now present restored silent films with live musicians, some "
            "playing historical scores and others improvising in the old way. Audiences who "
            "attend these screenings often describe being surprised by how alive the films feel. "
            "The surprise is itself revealing. We have grown so used to films that are identical "
            "every time that we have forgotten they were once something closer to a concert: a "
            "collaboration, renewed every night, between the screen and the people in front of "
            "it.",
        ],
        "questions": [
            ("main_idea",
             "Which of the following best describes the main point of the passage?",
             ["Silent films were less popular than sound films because audiences found them dull.",
              "Recorded soundtracks were a costly mistake that filmmakers and their audiences have since come to regret deeply.",
              "Cue sheets allowed studios to control the music played in nearly every theater.",
              "Live music once made each silent film showing a unique performance, a quality largely lost with sound."],
             3,
             ["The passage says the experience of silent films was “anything but” silent or dull.",
              "The author notes real gains from recorded scores; no regret is described.",
              "Cue sheets only suggested pieces, and many accompanists improvised.",
              "Correct. The passage describes live accompaniment, its disappearance, and what was lost and gained."],
             "The passage centers on live accompaniment and what changed when sound arrived."),
            ("detail",
             "According to the passage, studios sometimes distributed cue sheets that:",
             ["listed the names of approved theater musicians",
              "suggested suitable pieces of music for each scene",
              "recorded how audiences reacted at each showing",
              "provided complete scores written for orchestras"],
             1,
             ["Musicians are not named on cue sheets.",
              "Correct. Cue sheets suggested “appropriate pieces for each scene.”",
              "Audience reactions were not recorded.",
              "Full scores are mentioned only for large orchestras, not as cue sheets."],
             "Paragraph 2 defines cue sheets as suggestions of pieces for each scene."),
            ("detail",
             "According to paragraph 4, musicians' unions responded to synchronized sound by:",
             ["training their members to compose recorded soundtracks",
              "persuading theaters to keep live musicians for comedies",
              "warning audiences in advertisements about “canned music”",
              "refusing to play in any theater that showed sound films"],
             2,
             ["Training for soundtracks is not mentioned.",
              "No such agreement with theaters is described.",
              "Correct. Unions ran newspaper ads warning that canned music would make films colder and cheaper.",
              "No boycott is described."],
             "Paragraph 4 describes the unions' newspaper advertisements."),
            ("inference",
             "Based on paragraph 3, an accompanist who held a mournful mood “too long” during a sad scene would most likely have:",
             ["made the audience cry harder than the scene alone would have",
              "caused viewers to find the scene unintentionally funny",
              "forced the projectionist to stop the film",
              "been replaced at once by a full orchestra"],
             1,
             ["The passage says the opposite effect would follow.",
              "Correct. “A mood held too long, and a tragedy turned comic.”",
              "Stopping the film is never mentioned.",
              "No replacement is described."],
             "Mistimed music could turn tragedy into comedy."),
            ("inference",
             "It can reasonably be inferred that audiences at modern screenings with live music are surprised because they:",
             ["did not know that silent films had ever been made",
              "expected the musicians to play recorded scores",
              "are used to films that sound the same every time",
              "find most modern films less entertaining than old ones"],
             2,
             ["They choose to attend screenings of silent films.",
              "Nothing suggests they expected recordings from live musicians.",
              "Correct. “We have grown so used to films that are identical every time.”",
              "Modern films are not compared for entertainment."],
             "The author explains the surprise by our habit of identical showings."),
            ("vocab",
             "As it is used in paragraph 1, the word “misnomer” most nearly means:",
             ["an inaccurate name", "a spelling mistake", "an outdated machine", "a short musical piece"],
             0,
             ["Correct. “Silent film” is a misleading name, since films were rarely watched in silence.",
              "The phrase is not misspelled.",
              "Misnomer does not refer to machines.",
              "Misnomer does not refer to music."],
             "The passage immediately explains why the name is inaccurate."),
            ("function",
             "The author's mention of accompanists “catching” a film (paragraph 3) primarily serves to:",
             ["suggest that films were often damaged during projection",
              "show that accompanists rarely paid attention to the screen",
              "emphasize how precisely the music had to match the action",
              "compare the work of accompanists to that of baseball players"],
             2,
             ["Damage to film is not the subject.",
              "Accompanists had to watch “as closely as any audience member.”",
              "Correct. The image of meeting something moving “at exactly the right moment” stresses timing.",
              "No sports comparison is made."],
             "The metaphor highlights split-second timing."),
            ("structure",
             "Paragraph 5 primarily serves to:",
             ["argue that accompanists were paid far too little for their work",
              "explain why the unions failed to protect theater musicians",
              "acknowledge gains from recorded sound, complicating the loss",
              "describe the training required to become an accompanist"],
             2,
             ["Pay is never discussed.",
              "The unions' failure was covered in paragraph 4.",
              "Correct. It notes what recorded scores made possible before paragraph 6 names what was lost.",
              "Training is not described."],
             "“It would be easy to tell this story as a simple loss…”"),
            ("view",
             "The author's attitude toward the arrival of recorded sound is best described as:",
             ["openly hostile, viewing it as a disaster for films",
              "wholly celebratory, viewing it as pure progress",
              "balanced, recognizing both its costs and its gains",
              "indifferent, treating it as a minor technical change"],
             2,
             ["The author credits recorded sound with real gains.",
              "The author also describes what “disappeared.”",
              "Correct. Paragraphs 5 and 6 weigh what was gained against what was lost.",
              "The author treats the change as significant."],
             "The passage is even-handed about the transition."),
        ],
    },
    {
        "id": "restoration-debate", "genre": "humanities", "difficulty": "hard",
        "title": "What Is an Old Building?",
        "paragraphs": [
            "In the middle of the nineteenth century, many of Europe's great medieval churches "
            "were in poor condition. Centuries of weather, war, neglect, and well-meaning "
            "alteration had left them cracked, patched, and in some cases half-ruined. Some had "
            "been stripped of their sculpture during revolutions; others had been modernized in "
            "styles that clashed with their original design. Out of the effort to save them came "
            "one of the most enduring arguments in the history of architecture, an argument not "
            "about how to repair old buildings, exactly, but about what it means for an old "
            "building to be authentic.",

            "On one side stood the French architect Eugène Viollet-le-Duc, who oversaw the "
            "restoration of a number of France's most famous medieval buildings. Viollet-le-Duc "
            "was a brilliant scholar of Gothic construction, and his ambition was "
            "correspondingly large. To restore a building, he wrote, is not to maintain it or "
            "repair it but to reestablish it in a finished state that may never have existed at "
            "any given moment. Where a church had been left incomplete, or altered by later "
            "builders, he was willing to design and build what he believed its original makers "
            "would have built, had they been able.",

            "On the other side stood the English critic John Ruskin, for whom this approach was "
            "not merely mistaken but destructive. Restoration, Ruskin argued, was “the most total "
            "destruction which a building can suffer,” because it replaced the actual marks of "
            "the original builders, including their particular chisel strokes, their "
            "irregularities, and the wear of centuries, with a modern imitation. The value of an "
            "old building lay precisely in its age and in the labor of the specific people who "
            "made it. A restored church might look more complete, but it would be, in his view, a "
            "kind of lie. Better to protect a building with careful maintenance, Ruskin urged, "
            "and when it could no longer stand, to let it fall.",

            "It is tempting to cast this disagreement as a contest between boldness and caution, "
            "or between imagination and respect. But both men loved medieval architecture "
            "deeply, and both believed they were honoring it. Their difference lay in where they "
            "located a building's value. For Viollet-le-Duc, value resided in the design, the "
            "idea of the building, which a skilled architect could understand and complete. For "
            "Ruskin, value resided in the physical object itself, in the irreplaceable material "
            "history that no design could reproduce.",

            "The practical consequences of these views can still be seen. Some buildings "
            "restored in the nineteenth century carry towers, spires, and ornaments that are, in "
            "effect, Victorian-era additions dressed in medieval style. Many visitors cannot "
            "tell the difference, and some of these additions have become beloved in their own "
            "right; several cities have had to decide whether a celebrated nineteenth-century "
            "addition is now old enough to deserve protection itself. Meanwhile, the movement "
            "Ruskin helped inspire, which favored repair over reinvention, shaped the "
            "conservation principles adopted in the following century, many of which call for "
            "new work to be clearly distinguishable from old.",

            "Yet neither position escapes difficulty when applied strictly. Ruskin's approach, "
            "followed to its logical end, would allow much of the world's architectural heritage "
            "to crumble rather than be touched. Viollet-le-Duc's approach, followed to its "
            "logical end, would allow a confident architect to replace history with his own "
            "theory of it. Even the decision to do nothing is a decision, with consequences that "
            "someone must answer for. Most conservators today work somewhere between these "
            "poles, making case-by-case judgments about when a missing element should be rebuilt "
            "and when an absence should simply be respected.",

            "The debate endures because the question at its center has no final answer. When we "
            "stand in front of an old building, are we looking at an idea that happens to be made "
            "of stone, or at stone that happens to carry an idea? Each generation of architects "
            "answers a little differently, and each answer leaves its own marks, which future "
            "generations, in turn, will have to decide whether to keep.",
        ],
        "questions": [
            ("main_idea",
             "The passage is primarily concerned with:",
             ["the engineering methods used to repair medieval churches in France",
              "a lasting dispute over what makes an old building authentic and how to treat it",
              "the rivalry between French and English architects for public commissions",
              "the reasons so many medieval churches had fallen into disrepair by the nineteenth century"],
             1,
             ["Engineering methods are not described.",
              "Correct. The passage presents Viollet-le-Duc's and Ruskin's views and their legacy.",
              "Ruskin was a critic, and no competition for commissions is described.",
              "The churches' decay is only the opening context."],
             "Paragraph 1 names the argument “about what it means for an old building to be authentic.”"),
            ("detail",
             "According to the passage, Viollet-le-Duc believed that restoring a building meant:",
             ["maintaining it with small repairs so that it never needed rebuilding",
              "allowing it to fall once it could no longer stand safely on its own",
              "bringing it to a finished state that may never actually have existed",
              "copying exactly the building's appearance when it was first used"],
             2,
             ["Careful maintenance is Ruskin's preference, not Viollet-le-Duc's.",
              "Letting a building fall is Ruskin's position.",
              "Correct. He wrote that restoration reestablishes a finished state “that may never have existed at any given moment.”",
              "He was willing to build what the makers would have built, beyond any past appearance."],
             "Paragraph 2 paraphrases his definition of restoration."),
            ("detail",
             "According to paragraph 5, many conservation principles adopted in the twentieth century call for:",
             ["missing towers to be rebuilt in a medieval style",
              "new work to be clearly distinguishable from old",
              "nineteenth-century additions to be removed",
              "unstable buildings to be taken down at once"],
             1,
             ["Rebuilding in medieval style is closer to Viollet-le-Duc's approach.",
              "Correct. These principles “call for new work to be clearly distinguishable from old.”",
              "The passage notes some additions are now valued and even protected.",
              "Demolition is not among the principles mentioned."],
             "Paragraph 5 states the principle directly."),
            ("inference",
             "Based on paragraph 4, which of the following would Ruskin most likely value most in a medieval church?",
             ["a newly built spire that completes the church's original design",
              "a scholar's drawing of how the church was meant to look when finished",
              "worn stones that still bear the marks of the church's original builders",
              "modern ornaments carved in a convincing and accurate medieval style"],
             2,
             ["Completing a design is Viollet-le-Duc's ideal.",
              "A drawing captures the idea of the building, which is where Viollet-le-Duc located value.",
              "Correct. Ruskin located value in “the irreplaceable material history” of the object.",
              "Ruskin called modern imitation “a kind of lie.”"],
             "For Ruskin, value resided in the physical object and its history."),
            ("inference",
             "The author suggests that Viollet-le-Duc's approach, “followed to its logical end,” could lead to:",
             ["the loss of much architectural heritage through simple neglect",
              "an architect's theory replacing the actual history of a building",
              "a steady decline in public interest in visiting medieval buildings",
              "a rule that every repair must be made in a modern style"],
             1,
             ["Crumbling heritage is the danger the author attributes to Ruskin's approach.",
              "Correct. It “would allow a confident architect to replace history with his own theory of it.”",
              "Public interest is not discussed as a risk.",
              "Modern-style repair is not part of Viollet-le-Duc's approach."],
             "Paragraph 6 names each approach's extreme consequence."),
            ("vocab",
             "As it is used in paragraph 4, the word “resided” most nearly means:",
             ["was located", "lived as a tenant", "stayed unchanged", "was paid for"],
             0,
             ["Correct. Value “resided in the design” means value was located in the design.",
              "Living as a tenant is the literal sense, which does not fit an abstract idea like value.",
              "The sentence is about where value is found, not whether it changes.",
              "Payment is not involved."],
             "The paragraph is about where each man “located a building's value.”"),
            ("function",
             "The question in the final paragraph about “an idea that happens to be made of stone” primarily serves to:",
             ["suggest that the author has finally sided with Viollet-le-Duc",
              "restate the two positions in a way that shows why the debate lasts",
              "introduce a third position that neither man ever considered",
              "mock visitors who cannot tell old stonework from new additions"],
             1,
             ["The question is left open; the author does not choose a side.",
              "Correct. The two halves of the question match the two men's views, and it “has no final answer.”",
              "The question restates the two existing positions.",
              "The tone is reflective, not mocking."],
             "The question compresses the design-versus-material disagreement."),
            ("structure",
             "Paragraph 4 differs from paragraphs 2 and 3 in that it:",
             ["presents a new historical figure who finally settled the debate",
              "describes the physical condition of the churches in close detail",
              "analyzes the root of the disagreement rather than each man's view",
              "argues that Ruskin's position was the more reasonable of the two"],
             2,
             ["No new figure is introduced.",
              "Physical condition is covered in paragraph 1.",
              "Correct. Paragraphs 2 and 3 describe each man's view; paragraph 4 explains where their difference lies.",
              "Paragraph 4 says both men honored the buildings and does not take a side."],
             "Paragraph 4 moves from description to analysis."),
            ("view",
             "The author's own position on the debate is best described as:",
             ["firmly with Ruskin, since restoration always destroys old buildings",
              "firmly with Viollet-le-Duc, since buildings should be completed",
              "sympathetic to both sides while noting the risks of each extreme",
              "uninterested, since the debate has no practical consequences"],
             2,
             ["The author also notes the problems with Ruskin's view.",
              "The author warns against replacing history with theory.",
              "Correct. Both men are said to honor architecture, and each approach is faulted when applied strictly.",
              "Paragraph 5 describes consequences that “can still be seen.”"],
             "Paragraphs 4 and 6 show the author's even-handedness."),
        ],
    },
    # ------------------------------------------------------------------ #
    # Natural science
    # ------------------------------------------------------------------ #
    {
        "id": "autumn-leaves", "genre": "natural", "difficulty": "easy",
        "title": "Why Leaves Turn",
        "paragraphs": [
            "Every autumn, in the forests of eastern North America and in many other temperate "
            "regions, millions of people make trips simply to look at leaves. The spectacle is so "
            "familiar that it is easy to forget how strange it is. A maple that was uniformly "
            "green in August turns scarlet in October; a birch becomes gold; an oak goes a deep "
            "rusty brown. Then, within a few weeks, the leaves fall and the branches stand bare "
            "until spring. Some travelers even plan their vacations around predictions of when the color will "
            "peak in a particular valley. What is actually happening inside those leaves?",

            "Much of the answer has to do with a pigment called chlorophyll. Chlorophyll is the "
            "molecule that allows plants to capture energy from sunlight and use it to make "
            "sugars from water and carbon dioxide, the process known as photosynthesis. It "
            "absorbs red and blue light strongly but reflects green light, which is why healthy "
            "leaves look green to us. During the growing season, a leaf is full of chlorophyll, "
            "but the molecule is fragile. Sunlight breaks it down constantly, and the tree must "
            "keep producing more to replace it.",

            "As autumn approaches, the days grow shorter and the nights cooler. Trees respond to "
            "these signals by preparing for winter, a season in which their broad, thin leaves "
            "would be more of a burden than a benefit: they would lose water, be damaged by "
            "freezing, and collect heavy snow. One step in this preparation is to stop replacing "
            "chlorophyll. Rather than simply abandoning the molecule, the tree breaks much of it "
            "down and moves valuable nutrients, especially nitrogen, back into its branches and "
            "roots, where they can be stored and reused in spring.",

            "As the chlorophyll disappears, other pigments that were present in the leaf all "
            "along become visible. These are the carotenoids, the same family of molecules that "
            "make carrots orange and corn yellow. Carotenoids help the leaf capture light and "
            "protect it from damage during the summer, but their yellow and orange colors are "
            "usually hidden beneath the dominant green. When the green fades, they are revealed. "
            "The gold of a birch or a hickory, in other words, is not a new color produced for "
            "autumn; it is an old color finally allowed to show.",

            "The brilliant reds and purples of some trees have a different origin. These come "
            "from pigments called anthocyanins, which, in many species, are not present in the "
            "leaf during the summer at all. Instead, the tree produces them in autumn, at the "
            "very time it is shutting the leaf down. This has long puzzled scientists, since "
            "making new pigments costs energy that a tree preparing for winter might be expected "
            "to save. One leading explanation is that anthocyanins act as a kind of sunscreen, "
            "shielding the leaf's remaining machinery from excess light while nutrients are being "
            "withdrawn. Other explanations have been proposed, and the question is not fully "
            "settled.",

            "Weather influences how vivid the display will be. A run of sunny days and cool, but "
            "not freezing, nights tends to produce the most intense reds, because those "
            "conditions favor the production of anthocyanins. A warm, cloudy autumn often yields "
            "duller colors, and an early hard frost can kill leaves before they reach their peak. "
            "Drought during the summer may cause leaves to change color and drop early. This is "
            "why the same hillside can look spectacular one year and muted the next.",

            "Finally, at the base of each leaf stem, a layer of specialized cells forms a kind of "
            "seam. As the season progresses, this layer weakens until the leaf is held on by "
            "little more than a few strands of tissue, and a breeze is enough to carry it away. "
            "The scar left on the branch is sealed, protecting the tree through the winter. The "
            "leaf, its nutrients already reclaimed, falls to the ground, where it will decay and, "
            "in time, return some of what remains to the soil.",
        ],
        "questions": [
            ("main_idea",
             "The main purpose of the passage is to:",
             ["argue that autumn tourism is harming the forests of eastern North America",
              "compare the leaves of maples, birches, and oaks during the summer months",
              "explain the processes that make many trees' leaves change color and fall",
              "describe how farmers use carotenoids to improve the color of their crops"],
             2,
             ["Tourism is mentioned only as a sign of the spectacle's popularity.",
              "The trees are compared only by their autumn colors, and only briefly.",
              "Correct. The passage traces chlorophyll loss, revealed and new pigments, weather, and leaf drop.",
              "Farming is never discussed."],
             "The opening question, “What is actually happening inside those leaves?”, sets the purpose."),
            ("detail",
             "According to the passage, chlorophyll makes healthy leaves look green because it:",
             ["absorbs green light more strongly than any other color",
              "reflects green light while absorbing red and blue light",
              "is found only in the leaves of evergreen trees and shrubs",
              "combines with carotenoids to form a new green pigment"],
             1,
             ["It is the reverse: chlorophyll reflects green light.",
              "Correct. Paragraph 2: it “absorbs red and blue light strongly but reflects green light.”",
              "The passage describes chlorophyll in maples, birches and oaks.",
              "Carotenoids are separate pigments hidden beneath the green."],
             "Paragraph 2 explains the color directly."),
            ("detail",
             "According to paragraph 3, before winter a tree moves nitrogen from its leaves into:",
             ["the soil around its trunk", "its branches and roots", "its newest buds", "the nearest trees"],
             1,
             ["Nutrients reach the soil only later, as fallen leaves decay.",
              "Correct. Nutrients go “back into its branches and roots, where they can be stored.”",
              "Buds are not mentioned.",
              "Other trees are not mentioned."],
             "Paragraph 3 names branches and roots as storage."),
            ("inference",
             "Based on paragraph 4, the yellow of a birch leaf in autumn is best described as:",
             ["a pigment the tree makes in response to cool nights",
              "a color that was in the leaf but hidden all summer",
              "a sign that the leaf has been damaged by early frost",
              "the result of nutrients flowing back into the leaf"],
             1,
             ["Making new pigment in autumn describes anthocyanins (reds), not carotenoids.",
              "Correct. The gold is “an old color finally allowed to show.”",
              "Frost kills leaves; it does not create yellow.",
              "Nutrients flow out of the leaf, not into it."],
             "Carotenoids were present all along, masked by chlorophyll."),
            ("inference",
             "Based on the passage, which autumn conditions would most likely produce the most intense red leaves?",
             ["several weeks of warm, cloudy weather",
              "an early hard frost in late September",
              "sunny days followed by cool nights above freezing",
              "a hot, dry summer followed by a cool and rainy autumn"],
             2,
             ["Warm, cloudy autumns yield “duller colors.”",
              "A hard frost can kill leaves before their peak.",
              "Correct. Sunny days and cool, not freezing, nights favor anthocyanin production.",
              "Summer drought makes leaves change and drop early."],
             "Paragraph 6 links sun and cool nights to the brightest reds."),
            ("vocab",
             "As it is used in paragraph 4, the word “dominant” most nearly means:",
             ["most aggressive", "most noticeable", "commanding others", "longest lasting"],
             1,
             ["Aggression does not apply to a color.",
              "Correct. The green is the most visible color, hiding the yellows.",
              "Control over others does not apply to a color.",
              "The green fades in autumn, so it is not the longest lasting."],
             "The green stands out over, and hides, the carotenoids' colors."),
            ("function",
             "The author mentions carrots and corn in paragraph 4 most likely to:",
             ["suggest that leaves and vegetables share a common ancestor",
              "explain why carotenoids are important in the human diet",
              "give familiar examples of the colors carotenoids produce",
              "show that carotenoids appear only in a few kinds of plants"],
             2,
             ["Ancestry is not discussed.",
              "Diet is not discussed.",
              "Correct. Orange carrots and yellow corn help readers picture the carotenoid colors.",
              "The examples show carotenoids are widespread, not rare."],
             "The examples connect an unfamiliar pigment to familiar foods."),
            ("structure",
             "Which of the following best describes the organization of the passage?",
             ["It presents a theory and then lists the evidence against it.",
              "It compares autumn in several regions and then ranks them.",
              "It describes a single tree's life from seedling to old age.",
              "It poses a question, then explains the changes roughly in order."],
             3,
             ["No single theory is opposed.",
              "Only eastern North America and “many other temperate regions” are mentioned.",
              "The passage covers one season, not a tree's whole life.",
              "Correct. After the opening question, it moves from chlorophyll loss to pigments to weather to leaf drop."],
             "The passage follows the season's events after asking what happens in leaves."),
            ("view",
             "The author's attitude toward the explanation that anthocyanins act as a sunscreen is best described as:",
             ["certain that it has been proved correct",
              "convinced that it has been proved false",
              "open to it while noting it is not settled",
              "uninterested in whether it is true or not"],
             2,
             ["The author says the question “is not fully settled.”",
              "The author calls it “one leading explanation.”",
              "Correct. It is “one leading explanation,” but “other explanations have been proposed.”",
              "The author discusses it with clear interest."],
             "Paragraph 5 presents the idea as leading but unsettled."),
        ],
    },
    {
        "id": "wandering-stones", "genre": "natural", "difficulty": "medium",
        "title": "The Wandering Stones",
        "paragraphs": [
            "Scattered across the farm fields and forests of northern Europe and North America "
            "lie boulders that do not belong where they are. Some are the size of a car; a few "
            "are as large as a house. Many are made of a type of rock entirely different from "
            "the bedrock beneath them, such as granite resting on limestone, and some can be "
            "traced to outcrops hundreds of kilometers away. For centuries, these misplaced "
            "stones posed a puzzle. Something had moved them, and whatever it was had been "
            "powerful enough to carry enormous weights across great distances.",

            "Geologists call such boulders erratics, from a Latin word meaning “to wander.” In "
            "the early nineteenth century, the most widely accepted explanation for them was a "
            "vast flood. According to this view, a great deluge had swept across the continents, "
            "and the boulders had been carried along by the rushing water or by icebergs "
            "floating on its surface. The flood theory had the advantage of explaining erratics "
            "in many places at once, and it fit comfortably with traditional accounts of the "
            "earth's history.",

            "Yet the theory had problems. Moving water sorts the material it carries: it drops "
            "heavy stones first and carries fine sand and silt farther, leaving neat layers "
            "behind. The deposits found alongside many erratics were not sorted at all. Boulders, "
            "gravel, sand, and clay lay jumbled together, as if they had been dumped all at once "
            "by something that did not distinguish between large and small. In addition, the "
            "bedrock in many of these regions was marked by long, parallel scratches, all running "
            "in roughly the same direction, as though something heavy had been dragged across "
            "it.",

            "The explanation that eventually prevailed came from observers who had spent time in "
            "the Alps. There, glaciers could be seen doing exactly what the flood theory "
            "struggled to explain. A glacier is a river of ice, and as it creeps downhill it "
            "plucks rocks from the land beneath and beside it, carries them along, and grinds "
            "them against the bedrock, leaving scratches. When the ice melts, it drops everything "
            "it carries in unsorted heaps. Alpine residents had long noticed boulders lying far "
            "below the current edges of glaciers and concluded that the ice had once reached much "
            "farther.",

            "In the late 1830s, the Swiss-born naturalist Louis Agassiz took this reasoning to a "
            "dramatic conclusion. If glaciers in the Alps had once been larger, he argued, then "
            "perhaps ice had once covered vast areas of the Northern Hemisphere, including lands "
            "that are now temperate. The erratics of northern Europe and North America, the "
            "jumbled deposits, the scratched bedrock: all of these could be explained by sheets "
            "of ice far larger than any glacier then existing. The idea of an ice age met strong "
            "resistance at first. It required imagining a world dramatically different from the "
            "present one, and it challenged both the flood theory and the assumption that the "
            "earth's climate had always been roughly the same.",

            "Over the following decades, however, evidence accumulated. Geologists mapped the "
            "scratches on bedrock and found that they formed consistent patterns radiating "
            "outward from a few centers, just as one would expect if great ice sheets had spread "
            "from those centers. They traced erratics back to their sources and found that the "
            "stones had moved in the directions the scratches indicated. By the end of the "
            "nineteenth century, the idea that large parts of the Northern Hemisphere had once "
            "been buried under ice was widely accepted.",

            "Today, scientists understand that there was not one ice age but many cycles of "
            "glacial advance and retreat over the past few million years. The erratics are "
            "reminders of the most recent of these advances, which ended more than ten thousand "
            "years ago. Some have become local landmarks, given names and climbed by generations "
            "of children; others serve as fence corners in farmers' fields, their history "
            "unnoticed. They sit where the ice abandoned them, ordinary-looking stones that once "
            "forced people to imagine an entirely different world.",
        ],
        "questions": [
            ("main_idea",
             "Which of the following best states the main idea of the passage?",
             ["A great flood once carried boulders across the continents, as most geologists today still believe it did.",
              "Puzzling boulders and related clues led scientists to conclude that ice once covered much of the north.",
              "Alpine glaciers have grown steadily larger over the past several thousand years.",
              "Louis Agassiz proved that granite boulders are always younger than limestone."],
             1,
             ["The flood theory was abandoned in favor of the ice age.",
              "Correct. The passage follows the evidence from erratics to the ice age theory.",
              "The passage says Alpine glaciers were once larger, not that they are growing.",
              "Rock ages are never compared."],
             "The passage traces how erratics and related evidence established the ice age idea."),
            ("detail",
             "According to the passage, the word “erratic” comes from a Latin word meaning:",
             ["to break apart", "to carry", "to wander", "to freeze"],
             2,
             ["Not the meaning given in the passage.",
              "Not the meaning given in the passage.",
              "Correct. Paragraph 2: “from a Latin word meaning ‘to wander.’”",
              "Not the meaning given in the passage."],
             "Paragraph 2 gives the meaning directly."),
            ("detail",
             "According to paragraph 6, geologists who traced erratics to their sources found that the stones had:",
             ["all come from a single outcrop in each region",
              "been carried by floodwaters flowing from the south",
              "moved in the directions shown by bedrock scratches",
              "traveled no more than a few kilometers from home"],
             2,
             ["The passage does not say each region's erratics share one source.",
              "The flood theory had already been undermined.",
              "Correct. The stones “had moved in the directions the scratches indicated.”",
              "Paragraph 1 says some came from hundreds of kilometers away."],
             "Paragraph 6 reports that erratics and scratches told the same story."),
            ("inference",
             "Based on paragraph 3, unsorted deposits counted against the flood theory because moving water:",
             ["cannot move boulders of any size at all",
              "scratches only the softest kinds of bedrock",
              "tends to separate heavy material from light",
              "freezes before it can carry stones very far"],
             2,
             ["Rushing water can move stones; the issue is how it leaves them.",
              "Scratches are a separate clue, not part of the sorting argument.",
              "Correct. Water “drops heavy stones first,” leaving neat layers, unlike the jumbled deposits.",
              "Freezing water is not part of this argument."],
             "Jumbled deposits are not what sorting water leaves behind."),
            ("inference",
             "It can reasonably be inferred from paragraph 5 that the ice age idea met resistance partly because:",
             ["many people assumed the earth's climate had always been much like today's",
              "Agassiz had never personally observed a glacier in the Alps or elsewhere",
              "the boulders in North America were too small to have been moved by ice",
              "geologists had already mapped every scratch on the bedrock of Europe"],
             0,
             ["Correct. The idea challenged “the assumption that the earth's climate had always been roughly the same.”",
              "Agassiz was Swiss-born and reasoned from Alpine glaciers.",
              "Some erratics are as large as houses; size was not the objection.",
              "Mapping the scratches came later and supported the theory."],
             "Paragraph 5 lists the assumptions the idea challenged."),
            ("vocab",
             "As it is used in paragraph 4, the word “plucks” most nearly means:",
             ["pulls loose", "plays a stringed instrument", "chooses carefully", "removes feathers from"],
             0,
             ["Correct. The glacier pulls rocks loose from the land beneath and beside it.",
              "Music is not involved.",
              "A glacier does not choose anything.",
              "This literal sense does not fit rocks."],
             "A glacier plucks rocks by tearing them free as it moves."),
            ("function",
             "The author describes glaciers in the Alps in paragraph 4 primarily to:",
             ["argue that the Alps are the oldest mountains anywhere in Europe",
              "describe the dangers that travelers face when crossing glaciers",
              "explain why no erratics are found anywhere in the Alpine region",
              "show processes that could be watched and that fit the evidence"],
             3,
             ["The age of the Alps is not discussed.",
              "Travel dangers are not discussed.",
              "Alpine residents saw boulders below the glaciers, so erratics are found there.",
              "Correct. Glaciers visibly plucked, carried, scratched and dumped unsorted debris."],
             "The Alps offered living examples of what the flood theory could not explain."),
            ("structure",
             "Which of the following best describes the way the passage is organized?",
             ["It describes a modern experiment and then explains its results.",
              "It presents a puzzle, a rejected answer, and how a new one won out.",
              "It compares two scientists' lives and then judges their characters.",
              "It lists types of rock and then explains how each type forms."],
             1,
             ["No modern experiment is described.",
              "Correct. Erratics (1), the flood theory and its problems (2-3), glaciers and the ice age (4-6).",
              "Only one scientist is named, and his character is not judged.",
              "Rock formation is not the subject."],
             "The passage follows the history of an explanation."),
            ("view",
             "The author's attitude toward the flood theory is best described as:",
             ["mocking, since the theory was obviously foolish",
              "respectful of its appeal, though it failed the evidence",
              "supportive, since the author believes it is correct",
              "indifferent, since the author never evaluates it"],
             1,
             ["The author credits its advantages instead of mocking it.",
              "Correct. It “had the advantage of explaining erratics in many places,” yet “had problems.”",
              "The author presents the ice age theory as the one that prevailed.",
              "Paragraph 3 evaluates its problems directly."],
             "The author gives the flood theory its due before showing why it failed."),
        ],
    },
    {
        "id": "bacterial-chorus", "genre": "natural", "difficulty": "hard",
        "title": "The Bacterial Chorus",
        "paragraphs": [
            "For much of the twentieth century, bacteria were regarded as the ultimate loners. "
            "Each cell, according to the prevailing view, went about its business independently, "
            "absorbing nutrients, dividing, and responding to its surroundings without any "
            "regard for its neighbors. A colony of bacteria was simply a crowd of individuals "
            "that happened to be in the same place. That picture has changed dramatically. "
            "Researchers now know that many bacteria communicate with chemicals, and that by "
            "doing so they can act together in ways no single cell could manage.",

            "Some of the earliest clues came from a glowing marine bacterium now called Vibrio "
            "fischeri. In laboratory cultures, scientists noticed something odd: when the "
            "bacteria were sparse, they produced no light at all, but when the population grew "
            "dense, the entire culture began to glow, more or less at once. Individual cells were "
            "clearly capable of producing light. Why would they wait until there were many of "
            "them to do it?",

            "The answer turned out to involve a small molecule that each cell releases into its "
            "surroundings. When only a few bacteria are present, the molecule drifts away and its "
            "concentration stays low. As the population grows, more cells release more of the "
            "molecule, and its concentration rises. Once it passes a certain threshold, it "
            "triggers a change inside every cell: genes that had been switched off are switched "
            "on, and the cells begin to produce light. Because the signal reflects how many cells "
            "are nearby, researchers named the phenomenon quorum sensing, borrowing a term for "
            "the minimum number of members a group needs before it can make decisions.",

            "Quorum sensing makes sense of a behavior that would otherwise seem wasteful. "
            "Producing light requires a great deal of energy. A single bacterium glowing in the "
            "open ocean would spend that energy for nothing, since its light would be far too "
            "faint to matter. But billions of bacteria glowing together can produce light bright "
            "enough to have an effect, and in the case of V. fischeri, that effect is put to use "
            "by an animal. The bacteria live inside a special organ of a small squid found in "
            "shallow Hawaiian waters. At night, the squid hunts near the surface, where moonlight "
            "from above would ordinarily cast its shadow downward, revealing it to predators "
            "below. The light produced by its bacterial partners is thought to cancel that "
            "shadow, helping to hide the squid. In return, the bacteria receive a protected, "
            "nutrient-rich home where they can reach the dense populations that switch on their "
            "glow.",

            "Since the discovery of quorum sensing in light-producing bacteria, researchers have "
            "found that the strategy is remarkably widespread. Many bacteria use chemical signals "
            "to coordinate activities that pay off only when performed by large numbers of "
            "cells. Some disease-causing bacteria, for instance, appear to hold back the "
            "production of harmful substances until their numbers are large enough to overwhelm a "
            "host's defenses. Acting too early, when the population is small, might simply alert "
            "the immune system without accomplishing much.",

            "That observation has opened an intriguing possibility for medicine. Most antibiotics "
            "work by killing bacteria or stopping their growth, and bacteria that survive a "
            "treatment can pass on whatever traits helped them survive, which over time produces "
            "resistant strains. Some researchers have proposed a different approach: rather than "
            "killing bacteria, interfere with their signals. If the bacteria never detect that "
            "they have reached a quorum, they may never launch the coordinated behaviors that "
            "make them dangerous. Because such a treatment would not directly threaten the "
            "bacteria's survival, some scientists have suggested that resistance might develop "
            "more slowly, though whether that hope will hold up in practice remains an open "
            "question.",

            "Whatever its medical future, quorum sensing has changed how biologists think about "
            "the smallest forms of life. The notion of bacteria as solitary individuals has given "
            "way to a picture of populations that monitor, signal, and respond to one another. Even "
            "the simplest organisms, it turns out, may be listening to their neighbors.",
        ],
        "questions": [
            ("main_idea",
             "The passage is primarily concerned with:",
             ["the life cycle of a small squid that lives in shallow Hawaiian waters",
              "the reasons that antibiotics have become less effective over the years",
              "the methods scientists use to grow bacteria in laboratory cultures",
              "how the discovery of chemical signaling changed views of bacteria"],
             3,
             ["The squid is one example within a larger discussion.",
              "Antibiotic resistance is raised only in paragraph 6.",
              "Laboratory methods are not described.",
              "Correct. The passage moves from “ultimate loners” to populations that signal one another."],
             "The first and last paragraphs frame the change in how bacteria are understood."),
            ("detail",
             "According to the passage, V. fischeri cultures in the laboratory produced light only when:",
             ["the cultures were placed under moonlight",
              "the bacterial population had grown dense",
              "a squid's light organ was added to them",
              "the bacteria were deprived of nutrients"],
             1,
             ["Moonlight is part of the squid example, not the laboratory finding.",
              "Correct. Sparse cultures did not glow; dense ones glowed “more or less at once.”",
              "The laboratory observation involved no squid.",
              "Nutrients are not mentioned as a trigger."],
             "Paragraph 2 describes glowing at high density."),
            ("detail",
             "According to paragraph 4, the squid benefits from the bacteria's light because the light:",
             ["attracts small prey toward the squid at night",
              "warns predators that the squid is poisonous",
              "is thought to cancel the squid's moonlit shadow",
              "helps the squid find its way back to the shore"],
             2,
             ["Attracting prey is not mentioned.",
              "No poison is mentioned.",
              "Correct. The light “is thought to cancel that shadow, helping to hide the squid.”",
              "Navigation is not mentioned."],
             "The bacterial light conceals the squid from predators below."),
            ("inference",
             "Based on paragraph 3, if the signaling molecule were continually removed from a dense culture of V. fischeri, the bacteria would most likely:",
             ["fail to glow even though many cells were present",
              "glow even more brightly than they had glowed before",
              "begin dividing far more rapidly than usual",
              "stop releasing the molecule altogether"],
             0,
             ["Correct. Without the molecule passing its threshold, the light genes would stay switched off.",
              "Brighter glow requires more signal, not less.",
              "Division rates are not linked to the signal in the passage.",
              "The passage says each cell releases the molecule; nothing suggests removal stops that."],
             "Glowing depends on the molecule's concentration, not on cell numbers directly."),
            ("inference",
             "It can reasonably be inferred from paragraph 5 that some disease-causing bacteria “hold back” harmful substances in order to:",
             ["save energy that they need for producing light",
              "allow the host to grow stronger before an attack",
              "avoid alerting the host's defenses too early",
              "keep other kinds of bacteria from detecting them"],
             2,
             ["Light production is discussed for V. fischeri, not these bacteria.",
              "Strengthening the host would work against the bacteria.",
              "Correct. Acting early “might simply alert the immune system without accomplishing much.”",
              "Other bacteria are not mentioned."],
             "Waiting lets them act when they can overwhelm the host."),
            ("vocab",
             "As it is used in paragraph 2, the word “sparse” most nearly means:",
             ["few in number", "poorly fed", "widely admired", "unusually small"],
             0,
             ["Correct. Sparse cultures are contrasted with dense populations.",
              "Feeding is not the contrast being drawn.",
              "Admiration is unrelated.",
              "The contrast is about how many cells there are, not their size."],
             "The contrast with “dense” fixes the meaning."),
            ("function",
             "The author's explanation of the word “quorum” at the end of paragraph 3 primarily serves to:",
             ["suggest that bacteria hold meetings in order to make group decisions",
              "show that the phenomenon was first noticed by political scientists",
              "argue that the term should be replaced with a more accurate name",
              "clarify why a word from group decision-making fits a population signal"],
             3,
             ["The term is borrowed as an analogy, not a literal description.",
              "Who first noticed it is not related to the term's origin.",
              "The author does not object to the term.",
              "Correct. A quorum is a minimum number of members, just as the signal tracks how many cells are nearby."],
             "The definition explains the name of the phenomenon."),
            ("structure",
             "Paragraph 6 primarily serves to:",
             ["explain the chemical structure of the signaling molecule",
              "describe a possible medical use of quorum sensing and its limits",
              "argue that doctors should stop prescribing antibiotics entirely now",
              "describe how quorum sensing was first discovered in the lab"],
             1,
             ["The molecule's structure is never described.",
              "Correct. It proposes interfering with signals and notes the hope “remains an open question.”",
              "It suggests an alternative approach, not an end to antibiotics.",
              "The discovery is described in paragraphs 2 and 3."],
             "Paragraph 6 turns from biology to a tentative medical idea."),
            ("view",
             "The author's attitude toward treating infections by interfering with bacterial signals is best described as:",
             ["certain that it will soon replace all antibiotics",
              "dismissive, regarding it as scientifically impossible",
              "neutral, since the author never actually describes it",
              "interested but cautious about whether it will work"],
             3,
             ["The author calls the outcome “an open question.”",
              "The author calls it “an intriguing possibility.”",
              "The author describes it in detail in paragraph 6.",
              "Correct. It is “an intriguing possibility,” yet its promise “remains an open question.”"],
             "Interest and caution sit side by side in paragraph 6."),
        ],
    },
]
