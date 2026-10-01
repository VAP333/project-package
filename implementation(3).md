# AksharSetu — Implementation Strategy

## Subject-Aware Textbook Intelligence, Speaking Style, Pronunciation, Caching & Apprenticeship

> **Status:** Architecture and implementation strategy  
> **Goal:** Build AksharSetu as a fast, reliable, textbook-specific educational accessibility system for visually impaired and low-vision students.

---

## 1. Executive Summary

AksharSetu is not merely a PDF reader and should not be implemented as:

```text
PDF → text extraction → line-by-line reading → TTS
```

That architecture causes the current failures:

- poems are read line by line without understanding stanza structure;
- word meanings and supplementary sections are treated like ordinary prose;
- teacher-only instructions are spoken to students;
- maps, graphs, figures and captions can interrupt the main narrative;
- explanations are regenerated instead of reused;
- pronunciation can become incorrect when Romanized phonetic text is passed through another TTS interpretation layer;
- Marathi joined/compound words (`जोडशब्द`) and technical/proper vocabulary need special handling;
- speaking style is not sufficiently adapted to subject/content type;
- the same textbook can trigger repeated expensive analysis.

The target architecture is:

```text
                         TEXTBOOK
                            │
                            ▼
                 ┌─────────────────────┐
                 │ DOCUMENT ANALYSIS   │
                 │ "What exists?"      │
                 └──────────┬──────────┘
                            ▼
                 ┌─────────────────────┐
                 │ STRUCTURE MODEL     │
                 │ "What is this?"     │
                 └──────────┬──────────┘
                            ▼
                 ┌─────────────────────┐
                 │ LEARNING MODEL      │
                 │ "What does it mean?"│
                 └──────────┬──────────┘
                            ▼
                 ┌─────────────────────┐
                 │ TEACHING MODEL      │
                 │ "How should it be  │
                 │ taught?"            │
                 └──────────┬──────────┘
                            ▼
                 ┌─────────────────────┐
                 │ NARRATION POLICY    │
                 │ "What to speak?"    │
                 └──────────┬──────────┘
                            ▼
                 ┌─────────────────────┐
                 │ SPEAKING STYLE      │
                 │ "How to say it?"    │
                 └──────────┬──────────┘
                            ▼
                 ┌─────────────────────┐
                 │ PRONUNCIATION       │
                 │ "How to pronounce?" │
                 └──────────┬──────────┘
                            ▼
                           TTS
```

The system must separate **what is being taught**, **what is spoken**, **how it is spoken**, **how words are pronounced**, and **how audio is generated**.

---

## 2. Core Product Principle

AksharSetu should optimize for the student's experience:

> **Fastest reliable path to already-verified educational content.**

For the fixed textbook corpus, expensive intelligence should happen primarily during build/preprocessing/training time.

Runtime should be predominantly:

```text
Student request → retrieve verified artifact → deliver
```

not:

```text
Student request
→ ask LLM to understand textbook again
→ ask LLM to explain again
→ ask TTS again
→ wait
```

---

## 3. Fixed-Corpus Strategy

Initial AksharSetu should focus on a known educational ecosystem rather than attempting to understand every possible textbook.

Target corpus:

```text
Maharashtra SSC
Marathi-medium
Target grade
Known textbook editions
Known subjects
Known chapter structures
Known terminology
Known educational conventions
```

Initial subject families:

- Marathi
- Geography
- History
- Political Science / Civics
- Mathematics
- Science & Technology
- other prescribed subjects as the corpus expands

The exact textbook editions must be verified before ingestion.

Adding a new book should mean:

```text
new textbook → analyze → verify → precompute → cache
```

rather than redesigning the application.

---

# 4. Three Graph Layers

## 4.1 Physical Document Graph

Answers:

> **WHERE IS IT?**

Contains:

- document, textbook, chapter and page;
- PDF page number and printed page number;
- region;
- bounding box/polygon;
- physical reading order;
- spatial adjacency;
- containment;
- preceding/following relationships;
- canonical extracted text;
- figures, maps, graphs, tables, diagrams and captions;
- activities and exercises;
- teacher-only content;
- decorative elements.

Physical order must remain separate from pedagogical order.

## 4.2 Learning Graph

Answers:

> **WHAT DOES IT MEAN?**

Contains:

- concepts;
- definitions;
- examples;
- vocabulary;
- learning units;
- learning objectives;
- prerequisites;
- concept relationships;
- exercises;
- evidence;
- checkpoints.

## 4.3 Chapter Teaching Graph

Answers:

> **WHY IS THIS HERE?**  
> **HOW SHOULD IT BE TAUGHT?**

Contains:

- pedagogical roles;
- pedagogical sequence;
- audience;
- student relevance;
- spoken priority;
- teaching transitions;
- checkpoints;
- activities;
- accessibility policy;
- explanation, illustration, prerequisite, reinforcement and assessment relationships.

Semantic relationships must not be inferred solely from spatial proximity.

---

# 5. Subject-Aware Strategy

Do not create one universal textbook template.

```text
                       AKSHARSETU CORE
                             │
              ┌──────────────┼──────────────┐
              ▼              ▼              ▼
          MARATHI        GEOGRAPHY       MATHEMATICS
              │              │              │
        Poetry Grammar   Map/Graph       Math Grammar
        Prose Grammar    Field Study     Problem Solving
        Vocabulary       Data            Formula/Steps
              │              │              │
              └──────────────┼──────────────┘
                             ▼
                  Other Subject Engines
                  Science / History / Civics
```

These subject engines do not initially need to be completely independent neural networks. They can consist of subject-specific schemas, classifiers, structural patterns, training labels, pedagogical policies, domain vocabulary, deterministic rules and ML models where useful.

---

# 6. Textbook Grammar Corpus

Before heavy model training, construct an:

# AksharSetu Textbook Grammar Corpus

For every textbook/chapter/page/region capture:

```text
Subject
Grade
Book
Chapter
Page
Region
Region Type
Physical Reading Order
Semantic Role
Pedagogical Role
Audience
Student Relevance
Spoken Priority
Learning Unit
Concept
Prerequisite
Teaching Relationship
Visual Relationship
Narration Style
Speaking Style
Pronunciation Requirement
Assessment Type
```

This corpus becomes the foundation for:

- model training;
- evaluation;
- deterministic rules;
- subject-specific grammar;
- RAG;
- narration;
- accessibility;
- caching.

---

# 7. Page-Level Analysis

Every page should be analyzed for:

- heading;
- subheading;
- paragraph;
- stanza;
- dialogue;
- author information;
- figure;
- photograph;
- caption;
- map;
- graph;
- chart;
- table;
- information box;
- activity;
- example;
- definition;
- exercise;
- question;
- answer;
- footnote;
- header;
- footer;
- page number;
- decorative element;
- supplementary material;
- teacher instruction.

Each region should preserve:

```text
region_id
page_id
bbox
region_type
canonical_text
physical_order
parent_region
caption_target
semantic_role
pedagogical_role
audience
student_relevance
spoken_priority
```

---

# 8. Chapter-Level Analysis

A chapter must be analyzed as a complete educational unit.

Do not infer chapter pedagogy independently from isolated pages.

Determine:

- genre;
- subject;
- grade;
- pedagogical pattern;
- chapter structure;
- learning units;
- learning objectives;
- prerequisites;
- concepts;
- vocabulary;
- teaching sequence;
- supporting material;
- activities;
- checkpoints;
- assessment structure;
- accessibility decisions;
- audience classification;
- spoken priorities;
- visual relationships;
- teacher-only material;
- narration strategy;
- speaking styles.

Page boundaries are physical boundaries, not semantic boundaries.

---

# 9. Dynamic Pedagogical Blueprints

Retain reusable blueprint families, but never make them rigid templates.

Examples:

| Genre | Example Blueprint |
|---|---|
| Marathi poem | `poetic_appreciation_recitation` |
| Geography | `exploratory_field_study` |
| Science | `inquiry_hypothesis_experiment` |
| Mathematics | `concrete_visual_abstract_practice` |
| Prose/story | `narrative_moral_comprehension` |

These are blueprint families, not mandatory sequences.

For example, two science chapters may legitimately have:

```text
Observation → Explanation → Diagram → Experiment → Application
```

or:

```text
Question → Hypothesis → Experiment → Observation → Conclusion
```

The chapter-specific teaching graph is authoritative.

---

# 10. Subject Grammars

## Marathi

Potential structures:

```text
Chapter
Poem
Stanza
Verse
Author Introduction
Word Meanings
भावार्थ
काव्यसौंदर्य
रसग्रहण
भाषिक वैशिष्ट्ये
Activity
Question
Grammar
Writing Exercise
Teacher Instruction
Supplementary Content
```

A poem must not be narrated as arbitrary lines.

Possible pedagogical flow:

```text
Introduction
→ Poem Title
→ Author / Context
→ Stanza Recitation
→ Meaning / Explanation
→ Important Vocabulary
→ Poetic Interpretation
→ Theme / Appreciation
→ Activity
→ Questions
```

The actual chapter may differ.

## Geography

Potential structures:

```text
Concept
Definition
Map
Map Legend
Graph
Table
Case Study
Field Observation
Photograph
Caption
Discussion
Activity
Data Interpretation
Question
```

Maps and figures should normally be attached to their relevant learning unit.

Default:

```text
auto_narrate = false
```

unless the teaching graph determines the visual is essential.

## Mathematics

Mathematics must not be treated as ordinary prose.

Represent:

```text
Problem
→ Known quantities
→ Unknown quantity
→ Operation / rule
→ Transformation
→ Intermediate result
→ Final result
→ Verification
```

Preserve mathematical semantics rather than relying only on string-to-speech conversion.

Potential structures:

```text
Definition
Formula
Theorem
Problem
Worked Example
Step
Diagram
Proof
Exercise
Answer
```

Speaking style should be precise, procedural, stepwise and explicit around operations and transitions.

## Science

Potential structures:

```text
Phenomenon
Question
Hypothesis
Definition
Concept
Diagram
Apparatus
Observation
Experiment
Result
Law
Example
Application
Activity
Conclusion
Assessment
```

Do not force every science chapter into one sequence.

## History / Civics

History may contain:

```text
Period
Event
Person
Place
Cause
Effect
Timeline
Evidence
Map
Image
Caption
Explanation
Comparison
Activity
Question
```

Civics / Political Science may contain:

```text
Concept
Definition
Institution
Process
Example
Case
Rights
Duties
Constitutional reference
Diagram
Comparison
Activity
Question
```

These patterns must be discovered and verified from the actual corpus.

---

# 11. Audience Classification

Every region should be classified across three orthogonal dimensions.

### Audience

```text
STUDENT
TEACHER
BOTH
REFERENCE
NON_SPOKEN
```

### Student Relevance

```text
essential
useful
optional
teacher_only
non_relevant
```

### Spoken Priority

```text
immediate
later
on_demand
never
```

Teacher-only material must remain in the source/document graph while being excluded from normal student narration.

Example:

```text
"प्रस्तुत प्रार्थना ही काव्यानंदासाठी घेतली असून ती विद्यार्थ्यांकडून तालासुरांत म्हणवून घ्यावी."
```

Possible classification:

```text
audience = TEACHER
student_relevance = teacher_only
spoken_priority = never
pedagogical_role = teacher_instruction
```

The poem itself remains student-essential.

---

# 12. Narration Architecture

Separate:

## WHAT TO READ

Document Graph + Learning Graph + Teaching Graph

## WHAT TO TEACH

Pedagogical Planner + RAG

## HOW TO SAY IT

Narration Planner + Speaking Style + Prosody Planner

## HOW TO GENERATE AUDIO

TTS Provider

Never collapse all four into one LLM prompt.

---

# 13. Speaking Style as a First-Class Training Target

Architecture:

```text
Content Type
+
Pedagogical Intent
+
Subject
+
Student Context
+
Discourse Structure
        ↓
Speaking Style Specification
        ↓
Prosody Planner
        ↓
TTS
```

Examples:

### Poem

```text
style = literary_recitation
rhythm = stanza_aware
pace = moderate
intonation = expressive
pause_policy = stanza_aware
emphasis = semantic
rhyme_awareness = true
```

### Geography

```text
style = explanatory_teacher
pace = moderate
tone = calm
spatial_explicitness = high
```

### Mathematics

```text
style = procedural
precision = high
pause_policy = operation_aware
step_boundaries = explicit
```

### Story

```text
style = narrative
character_awareness = true
dialogue_awareness = true
expressiveness = controlled
```

### Question

```text
style = interrogative
intonation = question
pause_before_answer = true
```

Example structured specification:

```json
{
  "content_type": "poetry_stanza",
  "pedagogical_role": "recitation",
  "speaking_style": "literary_recitation",
  "pace": "moderate",
  "pause_policy": "stanza_aware",
  "emphasis_policy": "semantic",
  "sentence_boundary_policy": "preserve"
}
```

---

# 14. Poetry and Rhyme

Preserve:

- stanza boundaries;
- verse boundaries;
- line relationships;
- refrain;
- rhyme information where detectable;
- poetic repetition;
- poetic pauses;
- poetic emphasis;
- poem-specific pedagogical explanation.

Do not reduce a poem to ordinary prose paragraphs.

The narration engine should know when to:

- recite;
- explain;
- pause;
- transition to meaning;
- transition to vocabulary;
- discuss poetic devices;
- summarize the theme.

---

# 15. Punctuation and Prosody

Punctuation is metadata/control information, not content to be spoken literally.

Canonical text remains unchanged.

Speech-layer interpretation may derive:

```text
comma → short natural pause
full stop → sentence-final pause
question mark → question intonation
exclamation → expressive emphasis
colon → explanatory/list transition
semicolon → medium pause
ellipsis → longer pause
```

Do not hard-code universal millisecond values.

Use discourse-aware prosody.

Never speak punctuation names when punctuation is merely structural.

---

# 16. Pronunciation Architecture

Canonical spelling and pronunciation must remain separate.

Avoid:

```text
Canonical Marathi
→ Romanized approximation
→ TTS interpretation
→ potentially wrong pronunciation
```

Prefer:

```text
Canonical Word
   │
   ├── Canonical Spelling
   ├── Pronunciation Representation
   └── Approved Reference Pronunciation
                │
                ▼
          TTS Pronunciation
```

---

# 17. Admin Pronunciation Workflow

Desired workflow:

```text
Admin selects word
        ↓
Admin speaks word
        ↓
Temporary audio capture
        ↓
Pronunciation extraction / analysis
        ↓
Admin approval
        ↓
Persistent pronunciation representation
        ↓
Temporary recording deletion
```

Do not delete the reference recording before validating that the derived pronunciation representation is sufficient.

After successful approval and validation, temporary audio may be deleted to save storage.

---

# 18. Pronunciation Knowledge Base

Each entry should support:

```text
canonical_text
word_type
compound_status
morpheme_information
pronunciation_representation
phoneme_sequence (optional)
reference_audio (optional / temporary)
language
locale
source
scope
version
approved
```

Scope hierarchy:

```text
document
→ textbook
→ subject
→ global
→ standard TTS
```

More specific approved pronunciation overrides broader defaults.

---

# 19. Marathi Pronunciation Benchmark

Create explicit evaluation categories for:

- जोडशब्द / compounds;
- consonant clusters;
- vowel length;
- nasalization;
- difficult Marathi phonemes;
- proper nouns;
- geographical names;
- scientific terminology;
- mathematical terminology;
- Sanskrit-derived vocabulary;
- textbook-specific terminology.

Pronunciation errors must be tracked separately from recognition, semantic, narration and TTS voice errors.

---

# 20. Voice vs Pronunciation vs Prosody

Keep these distinct.

### Voice
Who is speaking?

### Pronunciation
How is a word pronounced?

### Prosody
How is the sentence/paragraph delivered?

### Teaching Behavior
What is said and when?

Therefore:

```text
Teaching Behavior
      ↓
Prosody
      ↓
Pronunciation
      ↓
TTS Voice
```

Do not solve a teaching problem by changing the TTS voice.

Do not solve a pronunciation problem by changing the teaching model.

---

# 21. Admin Reference Pronunciation

If future TTS technology supports reference-audio conditioning, the system may use an approved pronunciation reference while preserving the selected system voice.

Desired objective:

```text
Admin's pronunciation
+
AksharSetu's selected voice
=
correct pronunciation in AksharSetu voice
```

This must not be confused with voice cloning.

Provider capabilities must be experimentally verified. Never assume arbitrary word-level pronunciation conditioning exists.

---

# 22. TTS Strategy

Sarvam remains a current prototype/baseline.

IndicF5 and other self-hosted candidates should be benchmarked later.

Do not begin TTS fine-tuning before:

1. chapter structure is stable;
2. narration policy is stable;
3. speaking-style schema is stable;
4. pronunciation pipeline is stable;
5. benchmark dataset exists.

Otherwise the system may optimize audio generation for incorrect upstream input.

---

# 23. Caching Is a First-Class Architecture

Recommended layers:

```text
Document Hash
      ↓
Parsed Document Cache
      ↓
Page Structure Cache
      ↓
Learning Graph Cache
      ↓
Teaching Graph Cache
      ↓
Narration Plan Cache
      ↓
Explanation Cache
      ↓
Pronunciation Cache
      ↓
TTS Audio Cache
```

The student runtime should primarily retrieve these artifacts.

---

# 24. Versioned Cache Keys

A TTS artifact should consider:

```text
document_hash
chapter_hash
structure_version
teaching_graph_version
narration_policy_version
speaking_style_version
pronunciation_version
tts_provider
tts_voice
tts_model_version
```

If only the TTS voice changes, do not regenerate graphs, explanations or pronunciation knowledge.

Only regenerate the affected audio layer.

---

# 25. Precomputed Textbook Pack

For fixed textbooks, build a deployable/cacheable:

# AksharSetu Textbook Pack

Example:

```text
AksharSetuTextbookPack/
│
├── Marathi/
│   ├── textbook_manifest
│   ├── chapter_graphs
│   ├── learning_units
│   ├── teaching_graphs
│   ├── narration_plans
│   ├── explanations
│   ├── pronunciation_lexicon
│   └── audio
│
├── Geography/
│   ├── ...
├── History/
│   ├── ...
├── Civics/
│   ├── ...
├── Mathematics/
│   ├── ...
└── Science/
    ├── ...
```

Student flow:

```text
Select Chapter
→ fetch verified manifest
→ fetch cached structure
→ fetch cached narration
→ fetch cached audio
→ play
```

---

# 26. Cache Invalidation

Invalidate only affected downstream artifacts.

```text
PDF changed
→ invalidate downstream artifacts

Teaching graph changed
→ invalidate narration/explanation/audio

Pronunciation changed
→ invalidate affected TTS audio

Speaking style changed
→ invalidate affected narration/audio

TTS provider changed
→ invalidate provider-specific audio only
```

Do not rebuild an entire textbook unnecessarily.

---

# 27. Gemini Teacher / AksharSetu Apprentice

Gemini is a teacher during build/training.

Gemini should analyze:

- document structure;
- chapter structure;
- semantic relationships;
- pedagogical relationships;
- audience;
- student relevance;
- spoken priority;
- learning objectives;
- prerequisites;
- accessibility;
- speaking-style metadata;
- subject-specific patterns.

Gemini should produce structured annotations, not merely prose explanations.

---

# 28. Teacher Annotation Lifecycle

```text
Gemini Teacher
      ↓
Structured Annotation
      ↓
Schema Validation
      ↓
Source Consistency
      ↓
Critical Token Checks
      ↓
Human Review where required
      ↓
VERIFIED_TRAINING_SAMPLE
      ↓
Training Dataset
```

Use three distinct states:

```text
TEACHER_OUTPUT
VERIFIED_TRAINING_SAMPLE
GOLDEN_TRUTH
```

Never automatically treat raw Gemini output as Golden Truth.

---

# 29. Independent Model Training

```text
Gemini Teacher
      ↓
Verified Dataset
      ↓
AksharSetu Model
      ↓
Independent Evaluation
      ↓
Error Analysis
      ↓
Corrected Examples
      ↓
Retraining
```

Do not define success as "AksharSetu matches Gemini."

Gemini is a teacher/reference source, not the ultimate truth.

The benchmark should be human-verified.

---

# 30. Locked Benchmark

Use:

```text
TRAIN
VALIDATION
LOCKED TEST
```

Prefer chapter-level splits, not random page splits.

The locked test set should contain genuinely unseen chapters.

Evaluate separately:

- region classification;
- reading order;
- genre;
- learning-unit segmentation;
- learning objectives;
- prerequisites;
- pedagogical role;
- audience;
- student relevance;
- spoken priority;
- teaching edges;
- visual relationships;
- checkpoint placement;
- RAG grounding;
- provenance;
- speaking style;
- pronunciation;
- student-facing behavior.

Do not hide all quality behind one overall score.

---

# 31. Error-Driven Apprenticeship

```text
Prediction
   ↓
Independent Evaluation
   ↓
Error Analysis
   ↓
Error Category
   ↓
Reviewed Corrected Example
   ↓
Training Dataset Version
   ↓
Retraining
   ↓
Benchmark
```

Suggested categories:

```text
layout
reading_order
genre
learning_unit
pedagogical_role
audience
relevance
spoken_priority
teaching_edge
objective
prerequisite
visual_relationship
accessibility
RAG_grounding
provenance
speaking_style
pronunciation
TTS
```

Do not automatically dump every failure into training.

Review and classify failures first.

---

# 32. Runtime After Graduation

Production runtime:

```text
Student
 ↓
AksharSetu
 ↓
Physical Document Graph
 ↓
Learning Graph
 ↓
Teaching Graph
 ↓
RAG
 ↓
Pedagogical Orchestrator
 ↓
Reading / Tutor / Activity
 ↓
Pronunciation KB
 ↓
Prosody Planner
 ↓
TTS
```

Gemini must not be a normal runtime dependency.

An optional experimental fallback may exist behind an explicit feature flag, but must never silently become the production authority.

---

# 33. RAG Strategy

RAG should retrieve structured educational context, not simply nearest text chunks.

For:

> Why are we going to Alibag?

retrieve:

- current learning unit;
- chapter objective;
- relevant concepts;
- teaching graph edges;
- canonical source regions;
- relevant map/figure;
- previous/next learning context where useful;
- verified explanatory artifacts.

Preserve:

```text
document_id
chapter_id
page_id
region_id
learning_unit_id
concept_id
pedagogical_role
```

RAG must never rewrite canonical textbook content.

---

# 34. Reading Mode vs Tutor Mode

## Reading Mode

Preserve:

- canonical textbook content;
- verified sequence;
- verified narration;
- verified pronunciation;
- precomputed speaking style.

No invented explanations in ordinary reading.

## Tutor Mode

May add:

- grounded transitions;
- explanations;
- examples;
- clarification;
- accessibility descriptions;
- learning checks.

Tutor responses must remain grounded in the teaching/learning graph and source evidence.

---

# 35. Visual Accessibility

For maps, diagrams, photographs, graphs and tables store:

```text
visual_id
visual_type
source_region
learning_unit
caption
semantic_role
accessibility_description
auto_narrate
```

Default:

```text
auto_narrate = false
```

unless the teaching graph determines the visual is essential.

---

# 36. Student Experience Requirements

Student experience should prioritize:

1. correctness;
2. predictability;
3. speed;
4. natural narration;
5. accessibility;
6. personalization.

Target:

```text
Select textbook
→ Select chapter
→ Start learning
→ Immediate verified content
```

The system should not regenerate known artifacts.

---

# 37. Model Allocation Strategy

## Deterministic Logic

Use for:

- page numbering;
- hashes;
- cache keys;
- canonical text preservation;
- critical tokens;
- manifest generation;
- cache invalidation;
- known textbook metadata.

## ML / Deep Learning

Use for:

- layout detection;
- region classification;
- reading order;
- semantic classification;
- subject/genre classification;
- visual relationships;
- anomaly detection;
- pronunciation analysis;
- future speaking-style prediction.

## LLM

Use primarily during:

- teacher bootstrap;
- chapter-level pedagogical analysis;
- annotation generation;
- difficult semantic interpretation;
- training-data construction;
- teacher corpus creation.

## Runtime

Prefer:

```text
precomputed structured artifacts
+
RAG
+
trained AksharSetu models
+
deterministic rules
+
TTS
```

---

# 38. Build Order

## Phase 0 — Corpus

Acquire and verify the fixed textbook corpus.

## Phase 1 — Physical Structure

Build reliable document/page/region representation.

## Phase 2 — Subject Grammar

Analyze all chapters and discover subject-specific patterns.

## Phase 3 — Learning Graph

Construct concepts, learning units, objectives and prerequisites.

## Phase 4 — Teaching Graph

Construct pedagogical relationships and narration policy.

## Phase 5 — Speaking Style Corpus

Create subject/content-specific speaking-style annotations.

## Phase 6 — Pronunciation Corpus

Build verified Marathi vocabulary and pronunciation knowledge.

## Phase 7 — Precomputation

Generate and cache graphs, narration plans, explanations, pronunciation and audio.

## Phase 8 — Model Training

Train AksharSetu models from verified annotations.

## Phase 9 — Independent Evaluation

Evaluate on locked unseen chapters.

## Phase 10 — Error-Driven Improvement

Review failures and retrain.

## Phase 11 — TTS Benchmarking

Benchmark Sarvam, IndicF5 and other candidates after the upstream pipeline is stable.

## Phase 12 — Graduation

Remove Gemini from normal runtime after independent benchmark criteria are satisfied.

---

# 39. What Must NOT Happen

Do not:

- read every PDF line blindly;
- treat poems as ordinary prose;
- speak teacher-only instructions to students;
- treat word meanings as ordinary narrative;
- let figures/maps randomly interrupt narration;
- regenerate explanations every session;
- use Romanized pronunciation as unquestioned truth;
- assume TTS alone fixes pronunciation;
- train TTS before upstream structure is stable;
- force one universal pedagogical template;
- compare Gemini and AksharSetu confidence at runtime;
- make Gemini a permanent runtime dependency;
- claim model training merely because a pipeline script passes;
- claim graduation without locked independent evaluation.

---

# 40. Acceptance Criteria

The architecture is ready for model training when:

- [ ] fixed textbook corpus is acquired and versioned;
- [ ] page-level structure is reliable;
- [ ] chapter boundaries are correct;
- [ ] physical document graph is stable;
- [ ] learning graph is implemented;
- [ ] teaching graph is implemented;
- [ ] subject-specific content types are catalogued;
- [ ] chapter-specific pedagogical patterns are represented;
- [ ] teacher-only material is preserved but excluded from student narration;
- [ ] narration policy is separate from source content;
- [ ] speaking style is represented explicitly;
- [ ] pronunciation knowledge is separate from canonical spelling;
- [ ] Marathi critical pronunciation cases are benchmarked;
- [ ] RAG preserves provenance;
- [ ] cache layers exist;
- [ ] cache invalidation is dependency-aware;
- [ ] repeated processing of the same textbook is avoided;
- [ ] teacher annotations are versioned;
- [ ] raw teacher output is distinct from verified training samples;
- [ ] Golden Truth is locked;
- [ ] chapter-level train/validation/test split exists;
- [ ] unseen chapter evaluation exists;
- [ ] error taxonomy exists;
- [ ] runtime can operate without Gemini;
- [ ] TTS is treated as a downstream layer;
- [ ] existing UI remains functional.

---

# 41. Definition of "Trained"

Use explicit lifecycle states:

```text
PIPELINE IMPLEMENTED
    ↓
TEACHER DATA GENERATED
    ↓
DATA VERIFIED
    ↓
MODEL TRAINED
    ↓
MODEL EVALUATED
    ↓
MODEL PASSED BENCHMARK
    ↓
MODEL GRADUATED
```

Only use the corresponding status when evidence exists.

---

# 42. Definition of "Graduated"

AksharSetu graduates from Gemini dependency when:

1. it independently processes unseen chapters;
2. it produces acceptable document/learning/teaching structures;
3. it satisfies predefined project-specific benchmark thresholds;
4. those thresholds are evaluated against locked human-verified truth;
5. critical pronunciation and accessibility requirements pass;
6. RAG remains grounded;
7. runtime does not require Gemini.

Graduation is NOT:

```text
AksharSetu confidence > Gemini confidence
```

and NOT:

```text
AksharSetu output ≈ Gemini output
```

---

# 43. Immediate Next Step

Do not begin by adding another model.

First build the corpus:

```text
PDF
 ↓
Complete chapter extraction
 ↓
Page/region analysis
 ↓
Chapter analysis
 ↓
Subject grammar extraction
 ↓
Speaking-style annotation
 ↓
Pronunciation annotation
 ↓
Human verification
 ↓
Textbook Grammar Corpus
```

After several complete subjects are analyzed, identify:

```text
Which structures are universal?
Which are subject-specific?
Which are chapter-specific?
Which require deterministic rules?
Which require classifiers?
Which require deep learning?
Which require LLM teacher annotations?
Which artifacts can be permanently cached?
```

Only then finalize the AksharSetu model-training architecture.

---

# 44. Long-Term Architecture

```text
                    FIXED TEXTBOOK CORPUS
                             │
                             ▼
                     GEMINI TEACHER
                             │
                Complete chapter analysis
                             │
                             ▼
                  VERIFIED ANNOTATIONS
                             │
             ┌───────────────┼────────────────┐
             ▼               ▼                ▼
       Physical Graph   Learning Graph   Teaching Graph
             │               │                │
             └───────────────┼────────────────┘
                             ▼
                    TRAINING CORPUS
                             │
                             ▼
                      AKSHARSETU
                             │
                    Independent Test
                             │
                    ┌────────┴────────┐
                    ▼                 ▼
                  PASS              FAIL
                    │                 │
                    ▼                 ▼
              Graduation        Error Analysis
                                      │
                                      ▼
                                  Retraining
                                      │
                                      └────→ Test


                  PRODUCTION RUNTIME

Student
  ↓
AksharSetu
  ↓
Physical Document Graph
  ↓
Learning Graph
  ↓
Teaching Graph
  ↓
RAG
  ↓
Pedagogical Orchestrator
  ↓
Reading / Tutor / Activity
  ↓
Speaking Style
  ↓
Pronunciation KB
  ↓
Prosody
  ↓
Cached / Generated TTS
  ↓
Student
```

The long-term objective is not to make AksharSetu continuously "think" about the textbook.

The objective is to make AksharSetu **understand the textbook once, verify that understanding, learn from it, cache it, and then deliver it reliably and naturally to the student.**
