# AksharSetu Corpus Analysis — Class 8 General Science (Maharashtra State Board, Marathi Medium)

`document_id: AKS_SCIENCE_CLASS8_SCIENCE` · schema `aksharsetu_v0.1_pilot` · source: `Science.pdf` (148 PDF pages, 19 chapters, first edition 2018, Balbharati)

Companion to `corpus_structured.json` (machine-readable) and `page_source_extract.jsonl` (raw per-page text). Covers all 19 chapters at chapter/learning-unit granularity (Levels 1–4), same scope and caveats as the History corpus (see that `corpus_analysis.md` for the shared methodology note).

---

## A. Document manifest

| Field | Value |
|---|---|
| Title | सामान्य विज्ञान, इयत्ता आठवी |
| Board / Publisher | Maharashtra State Board — Balbharati, Pune |
| Medium | Marathi |
| Edition | First edition 2018 |
| PDF pages | 148 (front matter pp.1–10, content pp.11–144, glossary pp.145–146, back cover pp.147–148) |
| Printed-page offset | printed page = PDF page − 10 (verified for all 19 chapter openings) |
| Chapters | 19 |

**Notable find:** the back matter (pdf pp.145–146) contains a *शब्दसूची* (glossary) of ~150 technical terms, each with Marathi term, English term, **and a phonetic Marathi transliteration of the English pronunciation** (e.g. "अणुअंक - atomic number - अ'टॉमिक्‍न'म्बर"). This is a ready-made, textbook-authored pronunciation resource — it should be ingested directly as a seed for the pronunciation-risk lexicon rather than re-derived from scratch (still flagged for human verification per the spec's caution against treating any single source as automatically authoritative).

## B. Complete chapter inventory (all 19 chapters)

| # | Chapter title | PDF pp. | Printed pp. | Domain |
|---|---|---|---|---|
| 1 | सजीव सृष्टी व सूक्ष्मजीवांचे वर्गीकरण | 11–15 | 1–5 | Biology — classification |
| 2 | आरोग्य व रोग | 16–23 | 6–13 | Biology — health |
| 3 | बल व दाब | 24–32 | 14–22 | Physics — mechanics |
| 4 | धाराविद्युत आणि चुंबकत्व | 33–37 | 23–27 | Physics — electricity/magnetism |
| 5 | अणूचे अंतरंग | 38–48 | 28–38 | Chemistry — atomic structure |
| 6 | द्रव्याचे संघटन | 49–58 | 39–48 | Chemistry — matter composition |
| 7 | धातू-अधातू | 59–63 | 49–53 | Chemistry — metals/non-metals |
| 8 | प्रदूषण | 64–71 | 54–61 | Environmental science |
| 9 | आपत्ती व्यवस्थापन | 72–76 | 62–66 | Environmental/safety |
| 10 | पेशी व पेशीअंगके | 77–84 | 67–74 | Biology — cell |
| 11 | मानवी शरीर व इंद्रिय संस्था | 85–92 | 75–82 | Biology — human body |
| 12 | आम्ल, आम्लारी ओळख | 93–98 | 83–88 | Chemistry — acids/bases |
| 13 | रासायनिक बदल व रासायनिक बंध | 99–104 | 89–94 | Chemistry — reactions/bonding |
| 14 | उष्णतेचे मापन व परिणाम | 105–113 | 95–103 | Physics — heat |
| 15 | ध्वनी | 114–119 | 104–109 | Physics — sound |
| 16 | प्रकाशाचे परावर्तन | 120–125 | 110–115 | Physics — light |
| 17 | मानवनिर्मित पदार्थ | 126–131 | 116–121 | Materials science |
| 18 | परिसंस्था | 132–138 | 122–128 | Ecology |
| 19 | ताऱ्यांची जीवनयात्रा | 139–144 | 129–134 | Astronomy |

Full learning-unit breakdown, key concepts, pronunciation-risk terms, activity/visual inventories, and assessment structure for every chapter are in `corpus_structured.json → chapter_inventory`.

**Book-level shape worth noting:** the sequence runs microscopic → macroscopic (microbes in Ch.1, atoms in Ch.5, ending with stars in Ch.19) — flagged in the JSON as a possible book-level narrative arc, distinct from History's strictly chronological arc.

## C. Discovered textbook grammar (cross-chapter, COMMON scope)

Every chapter follows: **थोडे आठवा / सांगा पाहू** (recall/discussion) → **body interleaved with करून पहा (hands-on activity) and जरा डोके चालवा (reasoning prompt)** → **स्वाध्याय**. This is structurally analogous to History's template but **activity-centred rather than narrative-centred** — करून पहा appears in all 19 chapters, often multiple times per chapter, and is the single defining element of this subject's grammar.

### Recurring boxed elements
- **करून पहा** — hands-on activity/experiment, the backbone of the book. Needs `READ_DIRECTLY` narration as literal step-by-step procedure, not summarized.
- **माहीत आहे का तुम्हांला** — enrichment facts, very frequent (every chapter).
- **इंटरनेट माझा मित्र / माहिती मिळवा** — research prompts sending the student elsewhere; correctly `EXCLUDE_FROM_NORMAL_READING`.
- **सोडवलेली/सोडविलेली उदाहरणे** — worked numerical examples, concentrated in CH_03, CH_14, CH_16 (the more mathematical chapters).
- **परिचय शास्त्रज्ञांचा / असे होऊन गेले / मागे वळून पाहताना** — scientist-biography or history-of-science vignettes (CH_03 Archimedes, CH_10 Golgi, CH_11 Harvey, CH_18 "ecosystem" etymology) — a genre exception within an otherwise activity-driven book.

### Genre sub-patterns
- **Mathematical/formula-heavy**: CH_03, CH_14, CH_16 — these need a distinct `mathematical_narration` speaking style (state given values → formula → substitution → answer), never collapsed to prose.
- **Historical-model-sequence**: CH_05 uniquely walks through four sequential scientist/model pairs (Dalton→Thomson→Rutherford→Bohr) — closer to History's narrative arc than to the rest of Science.
- **Biology catalogue**: CH_10, CH_11 — organelle/organ-system by organelle/organ-system, each with structure→function.
- **Environmental/social-issue**: CH_08, CH_09, CH_17 (impact sections), CH_18 (impact sections).
- **Chemistry-reaction**: CH_07, CH_12, CH_13 — need a chemical-equation speaking convention (reactants → "yields" → products).

## D. Narration & speaking-style grammar

| Content type | Narration policy | Rationale |
|---|---|---|
| Body prose | `READ_THEN_EXPLAIN` | default |
| करून पहा activity steps | `READ_DIRECTLY` | procedural, literal |
| सोडवलेली उदाहरणे | `READ_THEN_EXPLAIN` + **mathematical_narration style** | never treat as prose (per spec §20) |
| इंटरनेट माझा मित्र / research prompts | `EXCLUDE_FROM_NORMAL_READING` | not narratable content itself |
| **Safety-critical content** (see below) | **`IMMEDIATE`** regardless of chapter default | life-safety stakes override normal policy |

**New speaking styles this subject introduces** (absent from History): `mathematical_narration` (CH_03/14/16 worked examples) and `procedural/instructional` (करून पहा steps).

### Safety-critical flags (highest narration priority)
- **CH_09** (आपत्ती व्यवस्थापन): earthquake and fire dos/don'ts — genuinely life-safety content.
- **CH_12** (आम्ल आम्लारी): two explicit warnings — never taste/smell/touch unknown chemicals; never add water to concentrated sulfuric acid (explosion risk). Both should be flagged `IMMEDIATE`.

## E. Pronunciation-risk lexicon (summary)

Unlike History (personal/place-name dense), Science's risk is **technical terminology density**: chemical compound names, physics units, taxonomic terms, plus a real mix of mostly non-Indian scientist names (Dalton, Thomson, Rutherford, Bohr, Archimedes, Golgi, Harvey, Landsteiner). The book's own glossary (§A above) should seed this lexicon. Diagram-dense chapters (CH_01, CH_05, CH_10, CH_11, CH_16, CH_19) compound the risk since formula/label text inside diagrams is not reliably captured by text extraction at all.

## F. Assessment structure

All 19 chapters end in स्वाध्याय but with more format variety than History: fill-in-the-blank (often with word banks), matching, true/false, numerical problems (concentrated in CH_03/14/16), diagram-drawing/labeling requests, and short/long answers. Exact per-chapter counts and exercise-type lists are in the JSON. As with History, full verbatim question text lives in `page_source_extract.jsonl`, not duplicated into the structured JSON.

## G. Cacheable artifacts

See `corpus_structured.json → cacheable_artifacts`. Notably: the CH_06 criss-cross molecular-formula method and the worked-example solution patterns in CH_03/14/16 are **fully algorithmic** — strong candidates for a deterministic rule-based solver rather than repeated LLM narration.

## H. Chapter-specific exceptions

- **CH_05**: structured as a historical model-sequence, closer to History's narrative pattern than Science's usual activity-driven pattern.
- **CH_09, CH_12**: contain safety-critical content needing `IMMEDIATE` override (see §D).
- **CH_02**: case-study paragraph (Gaurav, child from a poor family with an alcoholic father) — needs the same careful, non-judgmental tone as sensitive History content.
- **CH_08**: the Bhopal gas tragedy (~8000 deaths) — measured, non-dramatized delivery required, same as History's violence/tragedy content.
- **CH_17**: real carcinogenicity/health-hazard content about thermocol/styrene — factual, non-alarmist tone.
- **CH_18**: the "Divija and the bee sting" scenario briefly shifts to narrative/empathy-building framing — worth preserving.

## I. Human verification queue

- **HIGH_RISK**: all chemical formulas/equations and numerical worked-example arithmetic (OCR of subscripts/superscripts/special symbols is unreliable — confirmed imperfect in raw extraction); scientist names and transliterations; the glossary's own phonetic transliterations (still needs human-speaker cross-check); all diagrams, especially in the diagram-dense chapters listed above; reading order at pages mixing tables and diagrams.
- **MEDIUM_RISK**: narration-policy/speaking-style assignments; structural-pattern labels; the safety-critical `IMMEDIATE` flagging logic itself, given the stakes of getting it wrong.
- **LOW_RISK**: chapter titles/page ranges; assessment type counts.

## J. Scope and what's deferred

Same scope statement as the History corpus: this pass covers Levels 1–4 for all 19 chapters from text-layer evidence plus targeted verification. It does not yet include Level 6–7 region-level graphs with bounding boxes, or verified accessibility descriptions of diagrams — and this matters *more* here than for History, since Science's diagrams (atomic models, cell organelles, circuit diagrams, ray-tracing geometry) are frequently load-bearing for comprehension, not merely illustrative.

**Recommended next step**: page-rasterization and visual verification, prioritizing CH_05, CH_10, and CH_16 given their diagram density and conceptual dependence on visuals, before generating narration or TTS for this book.
