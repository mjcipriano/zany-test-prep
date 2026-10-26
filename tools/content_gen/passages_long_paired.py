"""Original ACT-style paired-passage sets (Passage A + Passage B), each with
nine questions: three on Passage A, three on Passage B and three that compare
the two, as in the enhanced ACT's paired-passage section.

All prose is original, written for this project. Each passage runs about
330-430 words (together about 700-850), split into numbered paragraphs that
questions cite as "paragraph N of Passage A/B". Question tuples have the same
shape as in passages_long_sets.py: (kind, prompt, options, correct_index,
rationales, explanation).
"""
from __future__ import annotations

LONG_PAIRED = [
    {
        "id": "school-start-times", "genre": "social", "difficulty": "easy",
        "title": "When Should School Start?",
        "paragraphs_a": [
            "Ask a teenager to fall asleep at nine o'clock at night and you are likely to be "
            "disappointed, not because of stubbornness, but because of biology. During "
            "adolescence, the body's internal clock shifts later. The hormone that helps signal "
            "that it is time to sleep begins to be released later in the evening than it was in "
            "childhood, so many teenagers simply do not feel tired until eleven o'clock or "
            "after.",

            "At the same time, teenagers still need a great deal of sleep; most experts "
            "recommend somewhere between eight and ten hours a night. A student who cannot fall "
            "asleep before eleven and must wake at six to catch an early bus is, night after "
            "night, falling short. Sleeping late on weekends can make up some of the difference, "
            "but it also pushes the internal clock even later, making Monday morning harder "
            "still. Over a school year, the shortfall adds up.",

            "The consequences are not trivial. Sleep-deprived students have more trouble paying "
            "attention, remembering what they learned, and controlling their moods. They are "
            "more likely to doze off in class and, for those old enough to drive, more likely to "
            "be involved in car accidents. Grades, too, can suffer when students arrive at their "
            "first class too tired to think clearly. Some research has linked chronic sleep loss "
            "in adolescence to higher rates of depression.",

            "For these reasons, several major medical organizations have recommended that "
            "middle and high schools begin classes no earlier than 8:30 in the morning. "
            "Districts that have made the change have generally reported that students sleep "
            "longer on school nights, and some have reported better attendance and fewer "
            "students falling asleep in class. The change does not ask teenagers to become "
            "different people. It simply asks schools to fit the day to the students they "
            "actually have.",

            "Adults sometimes respond that teenagers would sleep more if they put away their "
            "phones. Screens do make the problem worse, and good habits matter. But no amount of "
            "discipline will move a teenager's internal clock back to where it was at age ten.",
        ],
        "paragraphs_b": [
            "I have read the research on adolescent sleep, and I do not dispute it. When our "
            "district's school board asked me to study whether we should move the high school's "
            "start time later, I expected the hardest part would be persuading skeptics of the "
            "science. Instead, the science turned out to be the easy part. The hard part was the "
            "buses.",

            "Like many districts, ours uses the same fleet of buses and the same drivers for "
            "several routes each morning. The high school route runs first, then the middle "
            "school, then the elementary schools. Pushing the high school later would mean either "
            "hiring more drivers, who are already difficult to find, or pushing the younger "
            "children's start times earlier, which would put eight-year-olds at bus stops in the "
            "dark. Our transportation office estimated that even the cheapest workable plan "
            "would require several new routes. Neither option is free, and neither is simple.",

            "Then there are the afternoons. A later start means a later dismissal. Our athletic "
            "teams already travel to games at schools with earlier schedules, and students would "
            "miss more class time to get there. Students with after-school jobs, many of whom "
            "help support their families, told us that a later dismissal could cost them hours "
            "of work. Parents who rely on older siblings to watch younger ones after school "
            "raised similar concerns.",

            "I do not offer these complications as reasons to do nothing. Several neighboring "
            "districts have made the change, and their experiences suggest that many of the "
            "problems can be solved with time and money. Some found ways to arrange their routes "
            "more efficiently; others raised taxes to pay for additional drivers. My point is "
            "that a start time is not a single decision. It is connected to transportation "
            "budgets, labor markets, sports schedules, and family routines, and a change that "
            "looks obvious on paper can shift costs onto the people least able to absorb them.",

            "Our board is still deciding. Whatever it chooses, I hope it chooses with all of "
            "those people in view.",
        ],
        "questions": [
            ("main_idea",
             "Which of the following best states the main idea of Passage A?",
             ["Teenagers sleep too little mainly because they keep using their phones late at night.",
              "Because teenagers' internal clocks shift later, later school start times would better suit them.",
              "Schools should shorten the school day so that students have more time left over for sleep.",
              "Adults need more sleep than teenagers do but rarely manage to get as much as they need."],
             1,
             ["Passage A says screens make the problem worse but are not the main cause.",
              "Correct. Passage A explains the biological shift and argues for starting no earlier than 8:30.",
              "Passage A proposes a later start, not a shorter day.",
              "Adults' sleep needs are never discussed."],
             "Passage A moves from biology to consequences to the recommendation of later start times."),
            ("detail",
             "According to Passage A, several major medical organizations have recommended that middle and high schools begin classes:",
             ["no later than 7:30 in the morning",
              "no earlier than 8:30 in the morning",
              "at a different time for each grade",
              "only after students have had breakfast"],
             1,
             ["The recommendation sets an earliest time, not a latest one.",
              "Correct. Paragraph 4 of Passage A gives “no earlier than 8:30.”",
              "Grade-by-grade times are not mentioned.",
              "Breakfast is not mentioned."],
             "Paragraph 4 of Passage A states the recommendation."),
            ("function",
             "In Passage A, the final paragraph primarily serves to:",
             ["introduce new research showing that screens have no effect on sleep",
              "suggest that teenagers lack the discipline needed to change their habits",
              "answer an objection by granting part of it while keeping the main claim",
              "summarize the recommendations made by major medical organizations"],
             2,
             ["The paragraph says screens “do make the problem worse.”",
              "It says discipline cannot reset the internal clock, not that teenagers lack it.",
              "Correct. It concedes screens matter but insists the clock shift is biological.",
              "The recommendations appear in paragraph 4."],
             "The paragraph addresses the “put away their phones” objection."),
            ("inference",
             "In Passage B, the author's statement that “the science turned out to be the easy part” suggests that the author:",
             ["doubts that the research on teenage sleep is accurate",
              "accepts the research but found practical problems harder",
              "believes the school board misunderstood the research",
              "found the research too technical to evaluate fairly"],
             1,
             ["The author says, “I do not dispute it.”",
              "Correct. The author accepts the science; the buses and schedules were the hard part.",
              "The board's understanding is not questioned.",
              "The author says the science was easy, not too technical."],
             "Paragraph 1 of Passage B sets up the contrast between science and logistics."),
            ("detail",
             "According to Passage B, moving the high school's start later without hiring more drivers would require:",
             ["ending the high school day earlier",
              "starting the elementary schools earlier",
              "canceling some of the athletic events",
              "combining the middle and high school routes"],
             1,
             ["A later start means a later dismissal, not an earlier one.",
              "Correct. The alternative to new drivers is pushing younger children's start times earlier.",
              "Athletics are a separate afternoon concern.",
              "Combining routes is not mentioned."],
             "Paragraph 2 of Passage B lays out the two options."),
            ("vocab",
             "As it is used in paragraph 4 of Passage B, the word “absorb” most nearly means:",
             ["handle the burden of", "soak up like a sponge", "learn and understand", "take over completely"],
             0,
             ["Correct. The costs fall on people least able to bear them.",
              "The literal sense of soaking up liquid does not fit costs.",
              "The sentence is about bearing costs, not learning.",
              "No one is taking control of anything."],
             "To absorb a cost is to bear it."),
            ("comparison",
             "The authors of both passages would most likely agree that:",
             ["teenagers' sleep patterns differ from those of younger children",
              "later start times should be adopted immediately by every district",
              "transportation costs make later start times impossible to adopt",
              "after-school jobs are the main cause of sleep loss among teenagers"],
             0,
             ["Correct. Passage A describes the shift, and the author of Passage B accepts the research.",
              "Passage B's author has not decided and urges caution.",
              "Passage B says neighboring districts solved the problems, so not impossible.",
              "Neither passage blames jobs for sleep loss."],
             "Passage B: “I have read the research on adolescent sleep, and I do not dispute it.”"),
            ("comparison",
             "How would the author of Passage B most likely respond to Passage A's claim that a later start “simply asks schools to fit the day to the students they actually have”?",
             ["by arguing that teenagers should adjust to the existing schedule",
              "by agreeing that the change requires no additional resources",
              "by pointing out that the change is not simple for buses, jobs, and families",
              "by questioning whether teenagers truly need eight to ten hours of sleep"],
             2,
             ["Passage B does not ask teenagers to adjust.",
              "Passage B stresses the resources needed, such as drivers and routes.",
              "Correct. Passage B says a start time “is not a single decision.”",
              "Passage B accepts the sleep research."],
             "Passage B's whole argument is that the change is not simple."),
            ("comparison",
             "Which of the following best describes the main difference in focus between the two passages?",
             ["Passage A focuses on bus schedules, while Passage B focuses on sleep hormones.",
              "Passage A argues against later start times, while Passage B argues for them.",
              "Passage A is written by a student, while Passage B is written by a parent.",
              "Passage A stresses students' biology; Passage B, a schedule change's practical effects."],
             3,
             ["The focuses are reversed.",
              "Passage A favors later times; Passage B has not taken a side.",
              "Passage B's author studies the issue for a school board, not as a parent.",
              "Correct. A explains the biology; B examines buses, jobs and families."],
             "One passage is about why; the other is about how and at what cost."),
        ],
    },
    {
        "id": "letters-and-archives", "genre": "humanities", "difficulty": "medium",
        "title": "Saving Everyday Writing",
        "paragraphs_a": [
            "When historians want to know what ordinary people thought and felt in the past, "
            "they often turn to letters. Official documents record what governments decided; "
            "newspapers record what editors judged worth printing. Letters record something more "
            "intimate: the worries of a farmer writing to a brother in the city, the excitement "
            "of a young woman describing her first train journey, the small jokes and complaints "
            "that make up most of a life.",

            "The value of letters comes partly from their abundance. In the nineteenth century, "
            "cheap postage and rising literacy turned letter writing into a habit for millions "
            "of people, and families saved what they received. Letters were tied in ribbon, "
            "tucked into Bibles, packed into trunks that passed from one generation to the next. "
            "Many were lost, of course, but enough survived that archives today hold enormous "
            "collections written by people who never imagined anyone but the recipient would "
            "read them.",

            "That lack of self-consciousness is precious. A writer who expects publication "
            "chooses words carefully and presents a polished self. A writer dashing off a note to "
            "a sister about a sick cow or a quarrel with a neighbor does neither. Spelling and "
            "grammar, too, can reveal where a writer grew up and how much schooling he or she "
            "received. Letters also preserve the texture of their moment in physical ways: the "
            "quality of the paper, the handwriting that grows shaky in old age, the stain of a "
            "coffee cup, the pressed flower that falls out when the envelope is opened.",

            "I sometimes worry that future historians will have nothing comparable. People today "
            "write more than ever, but much of what they write is brief, scattered across many "
            "services, and easily deleted. No one ties a bundle of text messages in ribbon. "
            "Perhaps some of today's messages will survive by accident, as many old letters did. "
            "But accident is a poor archivist. When I imagine a historian a century from now "
            "trying to understand how an ordinary family lived in our time, I picture her "
            "searching for a trunk that no one thought to fill.",
        ],
        "paragraphs_b": [
            "It is common to hear that our era will leave behind a “digital dark age,” a gap in "
            "the historical record caused by fragile files and forgotten passwords. The worry is "
            "understandable, and it is not baseless. Storage formats become obsolete, companies "
            "shut down their services, and data that is not actively maintained can become "
            "unreadable within a few decades. Anyone who has tried to open an old document "
            "created with software that no longer exists knows the feeling.",

            "But the fear of a dark age often rests on a romantic picture of the past. The "
            "letters that survive from earlier centuries are not a representative sample of what "
            "people wrote. They are the ones that happened to be saved, disproportionately by "
            "literate, settled, relatively prosperous families with attics to store them in. "
            "Countless letters by the poor, the mobile, and the unlucky were burned, thrown out, "
            "or left to rot. The archive we inherited was shaped by chance and by privilege as "
            "much as by anyone's design.",

            "The digital record, by contrast, is in danger of being too large rather than too "
            "small. Ordinary people now produce staggering quantities of writing, and much of it "
            "is stored, at least for a time, on servers that keep far more than any attic could "
            "hold. The challenge for archivists is not mainly that this material will vanish on "
            "its own but that no one will make deliberate decisions about what to keep, in what "
            "formats, and with what protections for the privacy of the people who wrote it.",

            "Those decisions are already being made in libraries and archives around the world, "
            "where specialists collect websites, preserve email collections donated by writers "
            "and organizations, and move files to new formats before the old ones fail. The work "
            "is unglamorous and underfunded. Yet it suggests that the historical record of our "
            "time will depend less on luck than the record of earlier times did, provided that "
            "we are willing to pay for the effort and to argue openly about what deserves to be "
            "saved.",
        ],
        "questions": [
            ("main_idea",
             "The main idea of Passage A is that:",
             ["official documents are more reliable than letters as sources about the past",
              "most nineteenth-century letter writers expected their letters to be published",
              "historians must learn to read old handwriting before they can study the past",
              "personal letters give an intimate view of the past that today's writing may not"],
             3,
             ["Passage A values letters precisely because they record what official documents do not.",
              "Passage A says writers “never imagined anyone but the recipient would read them.”",
              "Reading handwriting is not the passage's concern.",
              "Correct. Passage A praises letters and worries that nothing comparable will survive from today."],
             "Passage A moves from the value of letters to a worry about the present."),
            ("detail",
             "According to Passage A, letter writing became a habit for millions of people in the nineteenth century because of:",
             ["the invention of the typewriter",
              "cheap postage and rising literacy",
              "the spread of long-distance train travel",
              "government programs that required it"],
             1,
             ["Typewriters are not mentioned.",
              "Correct. Paragraph 2 of Passage A names cheap postage and rising literacy.",
              "A train journey appears only as a letter's subject.",
              "No government requirement is mentioned."],
             "Paragraph 2 of Passage A gives the two causes."),
            ("vocab",
             "As it is used in paragraph 3 of Passage A, the word “texture” most nearly means:",
             ["rough surface", "distinctive character", "woven fabric", "thickness of paper"],
             1,
             ["The examples go beyond surfaces to stains, handwriting and flowers.",
              "Correct. The letters preserve the particular feel and character of their moment.",
              "Fabric is not the subject.",
              "Paper quality is only one example of the texture, not its meaning."],
             "“The texture of their moment” is the moment's distinctive feel."),
            ("function",
             "The reference in paragraph 2 of Passage B to families “with attics to store them in” primarily serves to:",
             ["describe where most archives keep their collections of letters today",
              "explain why paper letters decay faster than digital files usually do",
              "suggest that surviving letters came mostly from better-off families",
              "show that the author grew up in a house that was full of old letters"],
             2,
             ["Modern archives are discussed in paragraph 4, not here.",
              "Decay rates of paper and files are not compared here.",
              "Correct. Letters were saved “disproportionately” by prosperous families with room to keep them.",
              "The author's childhood is never mentioned."],
             "The attic detail points to privilege shaping what survived."),
            ("detail",
             "According to Passage B, the main challenge facing archivists of digital material is:",
             ["finding enough material to fill their collections",
              "persuading writers to stop sending one another email",
              "deciding deliberately what to keep and how to protect it",
              "reading the handwriting on old scanned documents"],
             2,
             ["Passage B says the digital record may be “too large rather than too small.”",
              "No such campaign is described.",
              "Correct. The danger is that “no one will make deliberate decisions about what to keep.”",
              "Handwriting is not Passage B's concern."],
             "Paragraph 3 of Passage B names the challenge."),
            ("inference",
             "The author of Passage B would most likely agree that the surviving record of earlier centuries is:",
             ["a complete record of what ordinary people once wrote",
              "skewed toward the writing of relatively well-off people",
              "less valuable to historians than today's digital record",
              "made up mostly of official government documents"],
             1,
             ["Passage B says surviving letters are “not a representative sample.”",
              "Correct. It was shaped “by chance and by privilege.”",
              "Passage B does not rank the two records' value.",
              "Passage B discusses surviving letters, not official documents."],
             "Paragraph 2 of Passage B describes the bias in what survived."),
            ("comparison",
             "How would the author of Passage B most likely respond to the worry in the last paragraph of Passage A?",
             ["by agreeing that historians a century from now will have nothing to study",
              "by suggesting that people should go back to writing letters by hand",
              "by arguing that the worry overlooks how uneven the old record already is",
              "by insisting that text messages are more revealing than letters ever were"],
             2,
             ["Passage B says the digital record may be too large, not empty.",
              "Passage B never proposes a return to handwriting.",
              "Correct. Passage B calls the fear of a dark age a “romantic picture of the past.”",
              "Passage B does not compare how revealing the two forms are."],
             "Passage B challenges the idea that the past left a full, fair record."),
            ("comparison",
             "Both passages suggest that:",
             ["a great deal of everyday writing from any period may fail to survive",
              "digital files are far more durable than paper letters have ever been",
              "historians should rely mainly on official documents and newspapers",
              "the nineteenth century produced little writing that was worth saving"],
             0,
             ["Correct. Passage A notes many letters were lost; Passage B notes countless letters destroyed and fragile files.",
              "Passage B calls digital storage fragile without maintenance.",
              "Passage A values letters over official records.",
              "Both passages treat nineteenth-century letters as valuable."],
             "Loss of everyday writing is common ground between the passages."),
            ("comparison",
             "Compared with the author of Passage A, the author of Passage B is more concerned with:",
             ["the emotional qualities of handwritten letters",
              "the deliberate choices that determine what is kept",
              "the daily lives of nineteenth-century farmers",
              "the personal working habits of historians"],
             1,
             ["That is Passage A's emphasis.",
              "Correct. Passage B focuses on archivists' decisions about what to keep and how.",
              "Farmers appear only as an example in Passage A.",
              "Neither passage focuses on historians' habits."],
             "Passage B shifts the question from luck to deliberate choice."),
        ],
    },
    {
        "id": "de-extinction", "genre": "natural", "difficulty": "hard",
        "title": "Bringing Back the Mammoth?",
        "paragraphs_a": [
            "For most of history, extinction has meant forever. When the last member of a "
            "species died, everything that species was, including its behavior, its role in its "
            "ecosystem, and the genetic code that built it, was gone. Advances in genetics have "
            "begun to raise a startling possibility: that some lost species, or at least close "
            "approximations of them, might be brought back.",

            "The leading approaches do not involve resurrecting an extinct animal in any literal "
            "sense. Instead, researchers recover fragments of DNA from preserved remains, compare "
            "them with the genomes of the extinct species' closest living relatives, and then "
            "edit the relatives' DNA to carry some of the traits that made the lost species "
            "distinctive. A project aimed at the woolly mammoth, for example, would produce an "
            "elephant engineered to have a mammoth's dense hair, thick fat, and tolerance for "
            "cold. The result would not be a mammoth in the full sense, but it might live where "
            "mammoths once lived and do some of what they once did.",

            "Supporters argue that such work could do more than satisfy curiosity. Some extinct "
            "animals played important roles in their ecosystems. Large grazers, for instance, "
            "may once have helped maintain open grasslands in the far north by trampling snow "
            "and knocking down trees, and some scientists have suggested that restoring such "
            "grazing could help keep frozen soils from thawing. Bringing back a lost species, or "
            "a functional substitute for it, might in such cases help restore a damaged "
            "landscape.",

            "The techniques developed along the way could also help species that are not yet "
            "extinct. Many endangered animals survive in populations so small that they have "
            "lost much of their genetic diversity, leaving them vulnerable to disease. The same "
            "tools used to edit traits into an elephant's genome might one day be used to restore "
            "lost diversity to a struggling population, using DNA preserved in museum specimens. "
            "Seen this way, de-extinction research is less a rival to conservation than a new set "
            "of instruments for it.",

            "Finally, there is the matter of responsibility. Human activity drove many species "
            "to extinction. If we develop the means to undo some of that damage, it is worth "
            "asking whether we have an obligation to try.",
        ],
        "paragraphs_b": [
            "The prospect of seeing a mammoth, or something like one, walk across the tundra is "
            "undeniably thrilling. But thrill is not the same as wisdom, and the case for "
            "de-extinction looks weaker the more closely it is examined.",

            "Consider first what would actually be produced. An elephant edited to carry some "
            "mammoth traits is not a mammoth. It would lack the knowledge that real mammoths "
            "passed from one generation to the next, such as where to find food in winter and how "
            "to avoid predators, because there would be no mammoths left to teach it. It would be "
            "raised by elephants or by people, in a world whose climate, plants, and other "
            "animals have changed enormously over thousands of years. Whether such an animal "
            "could thrive, or would even fill the ecological role its supporters imagine, is far "
            "from clear.",

            "Consider next the cost. Conservation budgets are small, and every dollar and every "
            "hour of expert attention spent on reviving a lost species is unavailable for "
            "protecting a living one. Thousands of species are threatened right now by habitat "
            "loss, pollution, and climate change, and many could be saved with measures that are "
            "already understood: protecting land, restoring wetlands, regulating hunting. These "
            "measures are rarely dramatic, which is perhaps why they struggle to attract "
            "attention. Even the most successful revival would produce, at enormous expense, a "
            "handful of animals; protecting a single stretch of habitat can shelter thousands.",

            "There is also a subtler danger. If people come to believe that extinction can be "
            "reversed, they may take it less seriously. A developer weighing whether to clear a "
            "forest, or a government deciding whether to fund a wildlife refuge, might reason "
            "that a lost species could always be brought back later. Even if no scientist makes "
            "such a promise, the mere idea could weaken the urgency that conservation depends "
            "on.",

            "None of this means that genetic research has nothing to offer. Tools for studying "
            "and even restoring genetic diversity in endangered populations may prove valuable. "
            "But that work can be pursued directly, for the sake of living species, without the "
            "spectacle of resurrection.",
        ],
        "questions": [
            ("main_idea",
             "Passage A is primarily concerned with:",
             ["presenting reasons that research into reviving lost species may be worthwhile",
              "describing the daily behavior of woolly mammoths during the last ice age",
              "warning that genetic editing poses unacceptable risks to living elephants",
              "explaining why museums have stopped preserving the specimens of animals"],
             0,
             ["Correct. Passage A offers ecological, conservation and moral reasons for the research.",
              "Mammoth behavior is not described.",
              "Passage A does not warn about risks to elephants.",
              "Passage A says museum specimens may supply useful DNA."],
             "Passage A lays out the case for de-extinction research."),
            ("detail",
             "According to Passage A, a project aimed at the woolly mammoth would most likely produce:",
             ["a mammoth cloned from a single frozen cell",
              "an elephant engineered to have mammoth traits",
              "a new species unrelated to elephants or mammoths",
              "a computer model of how mammoths once behaved"],
             1,
             ["Passage A says the approaches do not resurrect an animal “in any literal sense.”",
              "Correct. It would be “an elephant engineered to have a mammoth's dense hair, thick fat, and tolerance for cold.”",
              "The animal would be an edited elephant.",
              "No computer model is mentioned."],
             "Paragraph 2 of Passage A describes the edited elephant."),
            ("function",
             "The final paragraph of Passage A mainly serves to:",
             ["argue that the industries that caused extinctions should pay for the research",
              "suggest that people may have a moral reason to pursue de-extinction",
              "concede that de-extinction research cannot be justified on ethical grounds",
              "explain why so few species have gone extinct in the last few centuries"],
             1,
             ["No industries or payments are mentioned.",
              "Correct. It asks “whether we have an obligation to try.”",
              "It raises an ethical reason for the research, not against it.",
              "It says human activity drove many species to extinction."],
             "The closing paragraph adds a moral argument to the practical ones."),
            ("vocab",
             "As it is used in paragraph 4 of Passage B, the word “subtler” most nearly means:",
             ["less obvious", "more delicate in flavor", "more skillful", "smaller in size"],
             0,
             ["Correct. The danger is indirect: people might take extinction less seriously.",
              "Flavor is unrelated.",
              "Skill is not the sense here.",
              "Size is not the sense here."],
             "A subtler danger is one that is harder to notice."),
            ("detail",
             "According to Passage B, an edited elephant would lack the knowledge real mammoths had because:",
             ["its brain would be too small to learn complex behavior",
              "no mammoths would remain to pass that knowledge on to it",
              "scientists would deliberately remove those instincts",
              "the tundra no longer contains the plants mammoths ate"],
             1,
             ["Brain size is not mentioned.",
              "Correct. There “would be no mammoths left to teach it.”",
              "Nothing is said about removing instincts.",
              "Changed plants are a separate point about its world, not the reason it lacks knowledge."],
             "Paragraph 2 of Passage B ties lost knowledge to the absence of teachers."),
            ("inference",
             "The author of Passage B would most likely describe protecting land and restoring wetlands as:",
             ["effective but underappreciated ways of saving species",
              "dramatic measures that attract too much public attention",
              "outdated methods that genetic tools will soon replace",
              "expensive projects with little proven benefit for wildlife"],
             0,
             ["Correct. They “could” save many species but “struggle to attract attention.”",
              "Passage B says these measures are “rarely dramatic.”",
              "Passage B treats them as proven and current.",
              "Passage B says a stretch of habitat “can shelter thousands.”"],
             "Paragraph 3 of Passage B praises these quiet measures."),
            ("comparison",
             "On which of the following points would the authors of both passages most likely agree?",
             ["Genetic tools might help restore diversity in endangered populations.",
              "De-extinction should be the top priority of conservation budgets.",
              "An edited elephant would be identical to a woolly mammoth.",
              "Public excitement about mammoths will weaken conservation."],
             0,
             ["Correct. Passage A suggests this in paragraph 4; Passage B grants it in its last paragraph.",
              "Neither author says this; Passage B argues the opposite.",
              "Both authors say the edited animal would not truly be a mammoth.",
              "Only Passage B raises this concern."],
             "Both passages see value in tools for restoring genetic diversity."),
            ("comparison",
             "How would the author of Passage B most likely respond to Passage A's claim that de-extinction research is “less a rival to conservation than a new set of instruments for it”?",
             ["by agreeing that it is the most promising conservation tool there is",
              "by claiming that conservation has no need for any new instruments",
              "by arguing that it competes with conservation for scarce money",
              "by noting that most endangered species have never been studied"],
             2,
             ["Passage B calls the case for de-extinction weak.",
              "Passage B welcomes tools for genetic diversity.",
              "Correct. Passage B says money spent on revival “is unavailable for protecting a living one.”",
              "Passage B makes no such claim."],
             "Passage B's cost argument directly answers Passage A's “not a rival” claim."),
            ("comparison",
             "Which of the following best describes how the two passages treat an edited animal that resembles an extinct one?",
             ["Passage A says a true mammoth could be revived, while Passage B denies elephants can be edited.",
              "Passage A focuses on its cost, while Passage B focuses only on its physical appearance.",
              "Passage A sees value in it as a substitute; Passage B doubts it could fill that role.",
              "Both passages treat it as identical to the original species in every important way."],
             2,
             ["Passage A says the result “would not be a mammoth in the full sense.”",
              "Cost is Passage B's concern, and Passage B also discusses knowledge and ecology.",
              "Correct. Passage A hopes it could do some of what mammoths did; Passage B says that is “far from clear.”",
              "Both passages deny it would be identical."],
             "The passages agree it is not a true mammoth but disagree about its usefulness."),
        ],
    },
]
