You are an expert Flutter mobile engineer, product designer, educational content architect, test engineer, and release engineer.

Build a complete, polished, offline-first SAT preparation app in Flutter. This must be a fully functional app, not a prototype, scaffold, demo, mockup, or half-baked MVP.

The app should work like a Duolingo-style learning app for SAT prep: short 5–15 minute challenge lessons, gamified progression, XP, streaks, levels, mastery, review lessons, unlockable skill paths, and smooth animations. The app must work completely offline after install.

This project is Android-first, but it must be architected as a cross-platform Flutter app so that iOS, web, desktop, ACT prep, and AP prep can be added later.

The first release target is a private/internal Android APK published through GitHub Releases. Do not make Google Play release requirements a blocker, but structure the app so future Google Play/App Bundle signing and release is straightforward.

## Core requirements

Use:

* Flutter stable
* Dart
* Material 3
* Android-first responsive layout
* Riverpod or another clean state-management solution
* GoRouter or another clean navigation solution
* Local SQLite persistence using Drift, Isar, Hive, or another robust local persistence layer
* Structured offline content assets
* GitHub Actions for CI and APK release builds
* Real unit/widget/integration tests
* Animations where appropriate
* No backend
* No login
* No network requirement
* No copyrighted College Board questions

All SAT practice content must be original SAT-style content.

## Important architecture requirement

Although this first app is SAT-focused, design the content and app architecture to support future expansion to:

* ACT
* AP Biology
* AP Chemistry
* AP Calculus
* AP Statistics
* Other standardized exams

Do this by making the content model exam-agnostic.

For example, content should support fields like:

* exam_id
* exam_name
* domain
* section
* skill
* subskill
* lesson_id
* question_id
* difficulty
* question_type
* explanation
* tags
* version

Do not hardcode SAT-only assumptions deep in the app logic. SAT can be the only enabled exam in the initial UI, but the data model and content pipeline should support adding other exams later.

## Initial content requirement

Seed the app with a substantial offline question bank.

Minimum initial content:

* 50 complete lessons
* 1,000 original SAT-style questions
* At least 500 Reading/Writing questions
* At least 500 Math questions
* Every question must have:

  * correct answer
  * full explanation
  * wrong-answer rationales where applicable
  * skill metadata
  * difficulty metadata
  * estimated time
  * tags
  * content version
* Every lesson must have:

  * teaching card or short concept explanation
  * 8–25 questions
  * skill mapping
  * difficulty progression
  * estimated completion time
  * prerequisite/unlock metadata

Do not use lorem ipsum, placeholder questions, copied official SAT questions, or copyrighted test-prep material.

The initial 1,000 questions may be generated as original SAT-style content, but they must be placed into structured content files and validated by automated tests.

## SAT content coverage

The SAT content should cover the Digital SAT broadly.

Reading and Writing:

* Main idea
* Inference
* Words in context
* Text structure and purpose
* Command of evidence
* Cross-text connections
* Grammar and punctuation
* Sentence boundaries
* Transitions
* Rhetorical synthesis
* Concision
* Standard English conventions

Math:

* Linear equations
* Linear inequalities
* Systems of equations
* Functions
* Quadratics
* Exponents and radicals
* Polynomial expressions
* Ratios, percentages, and units
* Proportions
* Data analysis
* Statistics
* Probability
* Geometry
* Area and volume
* Circles
* Right triangles
* Basic trigonometry
* Word problems

Create a balanced skill map and lesson progression.

## Content-generation and expansion pipeline

Create a durable content-generation and validation system so that future AI coding/content agents can safely extend the lesson and question bank.

Add a `/content` directory with a clear structure, such as:

```text
content/
  exams/
    sat/
      exam.yaml
      skills.yaml
      lessons/
        rw/
        math/
      questions/
        rw/
        math/
  schemas/
    lesson.schema.json
    question.schema.json
  prompts/
    generate_sat_lesson.md
    generate_sat_questions.md
    expand_question_bank.md
    review_question_quality.md
    verify_math_questions.md
    verify_rw_questions.md
  validators/
    README.md
```

The exact structure can differ if better, but it must be clean, documented, and scalable.

Create prompts that future AI agents can use to generate more content. These prompt files should be explicit, reusable, and include strict output requirements.

At minimum, include prompt files for:

1. Generating a new SAT lesson
2. Generating SAT Reading/Writing question sets
3. Generating SAT Math question sets
4. Expanding an existing skill area
5. Auditing generated questions for quality
6. Checking math answer correctness
7. Checking grammar/reading question correctness
8. Converting generated content into the required JSON/YAML schema

The prompts should instruct agents to:

* produce original questions only
* avoid copyrighted official SAT content
* include explanations
* include wrong-answer rationales
* follow the schema exactly
* avoid ambiguous questions
* avoid multiple correct answers
* mark difficulty accurately
* include answer-verification notes
* include estimated time
* include skill/subskill metadata
* avoid trick questions unless pedagogically useful
* keep wording similar in style to standardized tests without copying real items

## Content validation pipeline

Create automated validators that run locally and in CI.

Validation must check:

* All JSON/YAML parses correctly
* All required fields are present
* IDs are unique
* Lesson IDs referenced by questions exist
* Skill IDs referenced by lessons/questions exist
* Every lesson has enough questions
* Every question has an answer
* Every question has an explanation
* Multiple choice questions have exactly one correct answer
* Student-produced response questions have valid numeric/string answer format
* Difficulty values are valid
* Estimated time values are valid
* No obvious placeholder text
* No duplicate question IDs
* No duplicate or near-duplicate prompts if feasible
* Content version exists
* Exam ID exists
* No lesson references missing prerequisite lessons
* The app can load all content without runtime errors

For math questions, add additional validation where feasible:

* Numeric answers parse correctly
* Accepted numeric tolerances are valid
* Rational/equivalent forms are represented clearly
* For generated arithmetic/algebra questions, include a machine-checkable answer field when possible
* Add tests for representative math questions to ensure answer checking works

For Reading/Writing questions, add validation where feasible:

* One correct answer only
* Explanation supports correct answer
* Wrong-answer rationales exist when choices exist
* Passage/question/choices are not empty
* Grammar questions include the sentence/passage context needed to answer

Add a command like one of these:

```bash
dart run tool/validate_content.dart
```

or

```bash
python tools/validate_content.py
```

Pick the best approach for the repo, document it, and make CI run it.

## App features

### 1. Onboarding

Create a complete onboarding flow:

* Welcome screen
* Explanation that the app works offline
* User selects exam, initially SAT only
* User selects target test date or skips
* User selects daily goal: 5, 10, or 15 minutes
* Optional diagnostic start
* Local profile creation without login
* Smooth transitions
* Ability to reset profile later from settings

### 2. Home / learning path

Create a Duolingo-style home screen.

It should show:

* Current streak
* XP
* Level
* Daily goal progress
* Current exam
* Skill path nodes
* Locked/unlocked lessons
* Completed lessons
* Review lessons
* Suggested next lesson
* Continue button
* Animated lesson unlocks
* Animated XP/streak feedback

The home screen should be attractive and feel like a real app.

### 3. Lesson engine

Each lesson should support:

* Brief teaching card
* 8–25 questions
* Immediate feedback after each answer
* Correct-answer explanation
* Wrong-answer rationale where applicable
* Progress indicator
* XP reward
* Mastery update
* End-of-lesson summary
* Mistake review
* Continue to next lesson
* Exit/resume behavior

Supported question types:

* Multiple choice
* Student-produced numeric answer
* Passage-based reading question
* Grammar/editing question
* Data/table interpretation question
* Multi-step math question

### 4. Gamification

Implement real gamification.

Include:

* XP
* Levels
* Streaks
* Daily goals
* Badges/achievements
* Lesson stars/crowns
* Skill mastery
* Review queue
* Unlockable lessons
* Celebration screen
* Animated XP gain
* Animated correct/incorrect feedback
* Animated streak continuation
* Animated lesson completion

The logic must be real and persisted locally.

### 5. Adaptive review and mastery

Implement a simple local mastery system.

Track:

* Attempts per question
* Correct/incorrect
* Response time
* Skill-level mastery
* Lesson-level mastery
* Missed questions
* Review queue
* Last reviewed date
* Repeated correct answers during review

Use a simple explainable algorithm, such as:

* Mastery ranges from 0–100 per skill
* Correct answer increases mastery
* Wrong answer decreases or slows mastery
* Harder questions affect mastery more
* Missed questions enter the review queue
* Correct review answers reduce review priority
* Weak skills are prioritized in suggested lessons

Add unit tests for this logic.

### 6. Offline persistence

Persist all important state locally:

* User profile
* Selected exam
* Daily goal
* Target test date
* XP
* Level
* Streak
* Badge state
* Lesson progress
* Question attempts
* Skill mastery
* Review queue
* Settings
* Last active date

The app must survive force close and restart without losing state.

### 7. Settings

Create a full settings screen:

* Daily goal
* Selected exam, initially SAT only
* Sound on/off
* Haptics on/off
* Theme: system/light/dark
* Reset progress
* About page
* Content version
* App version
* Offline privacy note

The privacy note should explain that the app stores progress locally and does not require a backend.

### 8. Design and polish

The app should feel like a polished consumer learning app.

Include:

* Material 3 visual system
* Consistent spacing, typography, and components
* Smooth navigation transitions
* Lesson completion animation
* Correct/incorrect answer animations
* XP/streak animation
* Locked/unlocked lesson visuals
* Accessible colors
* Large touch targets
* Responsive layout
* Small Android screen support
* Dark mode
* No broken screens
* No placeholder-only UI
* No dead buttons

Animations should improve the experience without making the app slow or annoying.

## Testing requirements

Add a serious test suite.

Required tests:

* Unit tests for XP calculation
* Unit tests for level calculation
* Unit tests for streak logic
* Unit tests for daily goal logic
* Unit tests for mastery updates
* Unit tests for lesson unlock logic
* Unit tests for review queue behavior
* Unit tests for answer checking
* Unit tests for numeric answer tolerance
* Unit tests for content parsing
* Unit tests for content validation
* Widget tests for onboarding
* Widget tests for home screen
* Widget tests for lesson flow
* Widget tests for question rendering
* Widget tests for lesson completion screen
* Widget tests for settings screen
* Persistence tests for save/load behavior
* Integration test covering:

  * launch app
  * complete onboarding
  * complete lesson
  * see XP update
  * see progress persist after restart or simulated reload

Do not create fake tests that only check that objects exist. Tests must assert real behavior.

## GitHub Actions

Create GitHub Actions workflows.

Required workflows:

### CI workflow

Run on push and pull request.

Must:

* Checkout
* Set up Flutter
* Install dependencies
* Run code generation if needed
* Check formatting
* Run analyzer
* Run unit/widget tests
* Run content validation
* Upload useful failure logs if appropriate

### Android APK build workflow

Run on push to main or manual dispatch.

Must:

* Build debug or profile APK
* Upload APK as GitHub artifact

### Internal release workflow

Run manually and/or on version tag.

Must:

* Build release APK
* Build Android App Bundle if easy and not blocking
* Upload release APK artifact
* Create or attach to GitHub Release when run on a tag
* Include release notes or generated changelog if practical

Do not hardcode private signing keys. If release signing is added, use GitHub secrets and document how to configure them.

Private internal APK release is the primary requirement. Google Play preparation is nice to have but must not block completion.

## Documentation

Create useful documentation.

Include:

* README.md
* How to run locally
* How to run tests
* How to validate content
* How to build APK
* How to generate a private release
* How to add new exams later
* How to add ACT/AP content later
* How to add new SAT lessons
* How to add new questions
* Content schema documentation
* Content-generation prompt documentation
* Architecture overview
* Persistence model overview
* Gamification model overview
* Release process
* Known limitations
* Future roadmap

## Developer experience

Add or update:

* `.gitignore`
* `analysis_options.yaml`
* sensible lint rules
* codegen instructions if needed
* scripts/tools for content validation
* clear project structure
* no broken imports
* no unused major dependencies
* no TODO stubs for core functionality
* no placeholder-only screens

## Suggested project structure

Use this or improve it:

```text
lib/
  app/
  core/
  design/
  features/
    onboarding/
    home/
    lessons/
    questions/
    review/
    settings/
    achievements/
  data/
    local/
    repositories/
  domain/
    models/
    services/
  content/
    content_loader.dart
    answer_checker.dart
    mastery_engine.dart
    unlock_engine.dart

content/
  exams/
    sat/
      exam.yaml
      skills.yaml
      lessons/
      questions/
  schemas/
  prompts/

tools/
  validate_content.dart
  generate_content_index.dart

test/
  unit/
  widget/
  integration/
```

The exact structure can differ, but it must be clean, scalable, and documented.

## Acceptance criteria

The work is complete only when all of the following are true:

* Flutter app launches successfully on Android
* App is Android-first but cross-platform-ready
* User can complete onboarding
* User can select SAT as the initial exam
* User can complete a full lesson
* User can answer multiple question types
* Feedback and explanations work
* XP updates correctly
* Level updates correctly
* Streak updates correctly
* Daily goal updates correctly
* Mastery updates correctly
* Lesson unlocks work
* Review queue works after missed questions
* Progress persists after app restart
* Settings screen works
* Theme setting works
* Reset progress works
* Content is loaded from structured offline assets
* Initial content includes at least 50 lessons
* Initial content includes at least 1,000 original questions
* No copyrighted official SAT questions are used
* Content-generation prompts are included
* Content-validation tools are included
* Content validation runs in CI
* Unit tests pass
* Widget tests pass
* Integration test passes
* GitHub Actions CI workflow exists
* GitHub Actions APK build workflow exists
* GitHub Actions release workflow exists
* APK artifact is produced by GitHub Actions
* README explains how to run, test, validate content, and build APK
* No placeholder-only screens remain
* No fake buttons remain
* No core TODO stubs remain
* No fake tests remain

## Implementation approach

Inspect the repository first.

If it is empty or not a Flutter project, create a new Flutter project.

Work in complete vertical slices, not endless scaffolding.

Suggested order:

1. Flutter app shell
2. Theme and navigation
3. Exam/content data model
4. Content schemas
5. Initial SAT skill map
6. Content validator
7. Content loader
8. Local persistence
9. Onboarding
10. Home learning path
11. Lesson engine
12. Question rendering
13. Answer checking
14. Feedback and explanations
15. XP/streak/level logic
16. Mastery/review logic
17. Settings
18. Animations and polish
19. Initial 50 lessons / 1,000 questions
20. Tests
21. GitHub Actions
22. Documentation

Do not stop at partial completion. Continue until the acceptance criteria are met.

## Quality bar

This should feel like a real app that a student could use.

Avoid:

* placeholder UI
* lorem ipsum
* copied SAT questions
* official College Board content
* broken navigation
* mock-only persistence
* fake tests
* brittle hardcoded paths
* undocumented content format
* unvalidated AI-generated content
* release workflow without artifacts
* huge unreviewable single files
* messy architecture that prevents ACT/AP expansion

Prefer simple, reliable, complete implementation over complex unfinished architecture.

## Final response required from coding agent

When finished, report:

* What was built
* App architecture summary
* Content system summary
* Number of lessons created
* Number of questions created
* How content validation works
* How future AI agents can add more lessons/questions
* Commands to run the app
* Commands to run tests
* Commands to validate content
* Commands to build APK locally
* Location of GitHub Actions workflows
* Location of APK artifacts
* Any assumptions made
* Any remaining limitations

Do not spend all effort on scaffolding. Prioritize a working vertical slice early, then expand to the full 50 lessons / 1,000 questions and validation system.

This repository can be found at https://github.com/mjcipriano/zany-test-prep
