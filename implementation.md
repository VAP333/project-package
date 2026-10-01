# AksharSetu — Implementation Guide
**For: Antigravity (agentic build environment)**
**Source: AksharSetu Revised Research & System Methodology v2.0 (Sept 2026)**
**Purpose of this file:** a build-ready, phase-gated implementation plan an agent can execute against, task by task, without re-deriving architecture decisions from the research document each time.

---

## 0. Read This First — Non-Negotiable Principles

These are architectural laws, not preferences. Any code, prompt, or design that violates one of these is a bug, even if it "works":

1. **The textbook is the authority.** No model — Gemini or AksharSetu — decides what the textbook says. The PDF's native text/geometry is ground truth.
2. **Generative AI never silently rewrites canonical content.** Reading Mode outputs must be traceable verbatim to source. Tutor Mode may explain, never replace.
3. **No confidence fusion, ever.** Never average, vote, or blend Gemini's confidence with AksharSetu's. Teacher supervises during training; student is evaluated independently at inference. Do not build a "comparison engine."
4. **Critical tokens are non-overridable by language plausibility.** Numbers, units, dates, formulas, chemical/scientific notation, names, chapter/question numbers must pass an independent verification path. A language model "correcting" `50 kg` to `500 kg` because it's more fluent is a critical failure — write tests specifically to catch this.
5. **Cache only truth.** Unverified model output never enters the Golden Corpus or production cache as if it were verified.
6. **Reading Mode ≠ Tutor Mode.** Keep these as separate code paths with separate guarantees. Reading Mode: fidelity above all. Tutor Mode: grounded explanation, faithfulness-checked.
7. **MVP-first sequencing is mandatory.** Do not build Models C/D/E, the full voice stack, or Camera Mode before Phase 3's gate clears. Resist scope creep even if it looks easy to add.
8. **Every phase has a gate (§ below). Do not start the next phase until the current gate passes.** This is the single most important discipline in this document.

---

## 1. Phase-Gate Map (execute in this order)

| Phase | Deliverable | Hard Gate to Proceed |
|---|---|---|
| 0 | Foundation + Licensing + Feasibility | Licensing cleared; dataset feasibility checkpoint passed |
| 1 | Gemini Teacher Pipeline (pilot) | Structured annotations usable on pilot set; acceptable human-reviewer agreement |
| 2 | Golden Corpus + verification workflow | Verification pipeline operational; non-trivial verified sample count |
| 3 | Model A (OCR) + Model B (Layout) | Safe-page rate & CER/WER clear agreed threshold on held-out pages |
| 4 | Reading Mode (first user-facing deliverable) | Ships as soon as Phase 3 gate clears — do not wait for later models |
| 5 | Models C/D/E (reading-order, semantic relation, NLP layer) | Only funded after Phase 3 gate; not before |
| 6 | Pedagogical Engine & Tutor Mode | Faithfulness checks passing on benchmark set |
| 7 | Voice Interface (ASR/VAD/conversation) | Reading Mode stable in production |
| 8 | Camera Mode | PDF pipeline robust and stable first |

Do not let an agent (human or AI) jump ahead of this table. If asked to "just build the voice interface first," push back and point to this table.

---

## 2. Phase 0 — Foundation & Blocking Gates

### 2.1 Engineering tasks
- [x] PDF ingestion service: accept AksharBharati/Balbharati PDFs, extract native text, coordinates, embedded images, vector graphics, metadata, page structure.
- [x] Document hashing (`source_hash`) for every ingested PDF/page — this is the provenance root.
- [x] Database schema (PostgreSQL) for: documents, pages, regions, provenance chain.
- [x] Object storage wiring for raw PDFs, extracted images, cached artifacts.
- [x] Cache layer (Redis) — but see Principle 5: nothing enters cache as "truth" until verified.
- [x] Provenance chain scaffold: `PDF → page → region → text → verification → Golden Corpus entry → learning graph → tutor answer`. Build this as a queryable chain from day one, not bolted on later.
- [x] Fallback path: when a PDF is scanned/non-text, route to image processing — this should be the exception path, not the default (§6 of source doc — PDF-first).

### 2.2 Licensing — BLOCKING, do not proceed past Phase 0 without these resolved
- [x] Confirm Balbharati/AksharBharati content redistribution rights.
- [x] Review Gemini API terms of service for how submitted textbook content may be used/retained.
- [x] Confirm license terms for the pretrained OCR/vision-language base model chosen for Stage A.
- [x] Confirm license terms for MahaBERT/L3Cube components, IndicConformer, IndicF5, and any other third-party model/dataset used.
- [x] Document all of the above in a `LICENSING.md` with dates checked and renewal/review dates.

### 2.3 Dataset Feasibility Checkpoint — BLOCKING before Stage C (see §7 below)
- [x] Inventory: how many textbook pages, across which grades/subjects, are actually available and licensed?
- [x] Run a small pilot (200–500 pages) through the Gemini teacher to estimate annotation quality and volume needed per model.
- [x] Estimate what fraction of pilot pages need human review before being trustworthy.
- [x] Compare available/licensed page count against what the pilot suggests is needed. If far short — this is a go/no-go signal now, not a surprise discovered mid-training.

### 2.4 Compute & Infra Plan (reconciling the 8GB local constraint)
| Workload | Where it runs |
|---|---|
| PDF parsing, hashing, caching, DB, API | Local / low-cost VM (no GPU) |
| Gemini teacher calls | Cloud (Google API) |
| Model fine-tuning (LoRA/QLoRA) | Rented GPU (pay-per-use) or lab allocation — **not** the 8GB local machine |
| Trained model inference (production) | Quantized model on modest/local hardware |

- [x] Do not attempt to train any vision-language component on the local 8GB machine. Budget short bursts of rented GPU time instead.
- [x] Confirm LoRA/QLoRA, selective fine-tuning, distillation, and quantization are the default training approach — not full retraining — for every stage.

---

## 3. Data Model Specs

### 3.1 Physical Document Graph (answers "where is everything?")
Each region record:
```
region_id, page_id, bbox/polygon, region_type, native_text,
visual_content, source_coordinates, parent_region,
adjacent_regions, preceding_region, following_region
```
region_type vocabulary: heading, paragraph, poetry, figure, caption, diagram, map, table, information_box, activity, example, definition, exercise, question, footnote, ...

### 3.2 Learning Graph (answers "what does it mean?")
Hierarchy: Chapters → Lessons → Learning Units (concepts, examples, figures) + vocabulary + activities.
Relationship types: `continues, explains, illustrates, defines, contrasts_with, asks_about, belongs_to, summarizes, precedes, follows`.
**Invariant to enforce in code:** every physical region must link to a semantic entity, which links to a learning unit. Write a validator that fails CI if this chain is broken for any region in the Golden Corpus.

### 3.3 Golden Corpus record schema
```
document_id, edition, book, subject, chapter, page, region,
source_hash, canonical_text, region_type, coordinates,
reading_order, semantic_relations, learning_units,
verification_status, verification_source, model_version, timestamp,
license/provenance
```
Three-tier promotion: `Teacher Output → Verified Training Sample → Golden Truth`. Only the last tier is production truth. Build this as an explicit state machine, not an implicit status flag.

### 3.4 Gemini Teacher output contract (structured annotation, not raw OCR)
```json
{
  "page_id": "book10_ch03_p042",
  "regions": [
    {"id": "r1", "type": "heading", "text": "...", "bbox": [...]},
    {"id": "r2", "type": "main_text", "text": "...", "bbox": [...]},
    {"id": "r3", "type": "figure", "bbox": [...]},
    {"id": "r4", "type": "caption", "text": "...", "bbox": [...]}
  ],
  "reading_order": ["r1", "r2", "r3", "r4"],
  "semantic_relations": [{"source": "r3", "target": "r2", "relation": "illustrates"}],
  "learning_units": [{"id": "lu1", "regions": ["r2", "r3", "r4"], "concepts": ["..."]}]
}
```
This is a **training target**, never a comparison/voting target (Principle 3).

---

## 4. Gemini Teacher — Implementation Rules

- [x] Treat the teacher model as a **role**, filled by the current-generation Gemini Flash-tier multimodal model. Do not hardcode a model name in prompts, business logic, or architecture code — only in a versioned config value (§ Versioning).
- [x] Deprecation policy: whenever Google deprecates the pinned model, re-run a fixed regression sample through the candidate replacement, compare against the regression baseline, and record the change in a model-version ledger before switching the pipeline over.
- [x] Re-check the cost-per-page estimate whenever the pinned model changes — Flash-tier pricing moves between releases.
- [x] Gemini's structured JSON output is a **hypothesis**, never auto-promoted to Golden Corpus truth. Route through the verification workflow (§3.3) regardless of confidence score.

---

## 5. Model Build Plan (Stage-gated, MVP-scoped)

### 5.1 MVP models (Phase 3 target — build these two only, first)
- **Model A — Text Recognition:** vision encoder → text decoder → Marathi text. Start from a TrOCR-style architecture, fine-tuned (not trained from scratch).
- **Model B — Layout Understanding:** page image + PDF evidence → region type. Train on Gemini-generated structural annotations + manually verified examples.

### 5.2 Later-phase models (Phase 5 — do NOT start until Phase 3 gate clears)
- **Model C — Reading-Order Prediction:** physical arrangement → logical sequence.
- **Model D — Semantic Relationship Model:** paragraph→figure, concept→definition, question→exercise, etc. Feeds the Learning Graph.
- **Model E / Marathi NLP layer:** use existing L3Cube/MahaNLP ecosystem (MahaBERT for contextual candidate ranking, Marathi NER for extraction) — do not train new language models from scratch.

### 5.3 Training stages (apply to each model in order)
1. **Stage A — Base model:** start from an existing open-source vision-language/document model. No from-scratch foundation model training.
2. **Stage B — Domain adaptation:** Marathi educational pages, Devanagari typography, educational vocabulary.
3. **Stage C — Teacher-supervised fine-tuning:** Gemini-generated structured examples as training targets. **Gated on §2.3 dataset feasibility checkpoint.**
4. **Stage D — Human-reviewed correction:** subject-expert review of selected examples → highest-quality training tier. Treat this as a required throughput line item, not optional polish.

Use LoRA/QLoRA, selective fine-tuning, distillation, quantization throughout (see §2.4).

### 5.4 OCR correction / critical-token pipeline (build as its own module)
Pipeline order:
```
raw OCR → normalization → dictionary → subject glossary →
Devanagari rules → character similarity → edit distance →
MahaBERT context → verified candidate
```
- [x] Build an independent, non-overridable verification path specifically for: numbers, dates, units, formulas, percentages, scientific notation, chemical expressions, names, chapter/question numbers.
- [x] Write regression tests asserting language-model plausibility never overrides source evidence for these token classes (the `50 kg` → `500 kg` failure mode from Principle 4).

### 5.5 Active learning loop (post-MVP, once AksharSetu has baseline competence)
- [ ] Auto-triage new pages: routine → process locally; unusual layout / rare vocabulary / new diagram-table type / ambiguous continuation → route to teacher or human reviewer.
- [ ] Verified results feed back into the corpus for retraining.

---

## 6. Evaluation Framework (build these as CI-gated metrics, not manual spot checks)

### 6.1 Dataset hygiene
- [x] Document-level train/validation/test split — no page or near-duplicate page may cross splits.

### 6.2 OCR-level metrics
- Character Error Rate (CER)
- Word Error Rate (WER)
- Critical-token accuracy (see §5.4)
- Layout accuracy: region classification, bounding boxes, reading order

### 6.3 Higher-level metrics
- Reading-order accuracy
- Region classification accuracy
- Semantic relation accuracy
- **Safe-page rate** — % of pages readable without an unsafe substantive error. Treat this as the headline accessibility metric.

### 6.4 Tutor Mode metrics
- Factual correctness
- Source faithfulness
- Relevance
- Brevity
- Marathi quality
- Hallucination rate
- Context continuity
- Interruption recovery

### 6.5 Human evaluation
- [ ] Teachers/subject experts: correctness + pedagogical/textbook fidelity.
- [ ] Blind/low-vision students: comprehension, navigation, cognitive load, naturalness, independence.
- [ ] Do not skip the student evaluation panel — the system is built for them, not for the eval script.

### 6.6 Phase-gate thresholds to formally define before each gate
| Gate | Bar |
|---|---|
| Phase 0 → 1 | Licensing cleared; dataset feasibility passed |
| Phase 1 → 2 | Pilot annotations usable; acceptable reviewer agreement |
| Phase 3/4 → later models | Safe-page rate & CER/WER clear agreed threshold on held-out pages |
| AksharSetu → primary role (Gemini → fallback) | AksharSetu's safe-page rate and critical-token accuracy match or exceed Gemini's on benchmark set, independently verified |

---

## 7. Cost Model (build a tracking dashboard for this, don't estimate once and forget)

- [x] Estimate cost per page = input tokens (page image/PDF context) + output tokens (structured annotation JSON).
- [x] Multiply by total intended bootstrap-phase page count.
- [x] Track teacher-pipeline (bootstrap, ~one-time per page) cost **separately** from Tutor Mode inference cost (per student-interaction, recurring indefinitely).
- [x] Re-run this estimate every time the pinned teacher model changes (§4).

---

## 8. Data Governance for Minors — build these BEFORE any student ever uses the system

- [x] Explicit, age-appropriate consent flow (via parent/guardian or school, depending on deployment context) before any student voice/interaction data leaves the device.
- [x] Minimize what reaches the Gemini teacher pipeline to textbook content only. Student voice/interaction data (Tutor Mode) must go through a **separate, more conservative** retention policy than bootstrap textbook annotation.
- [x] Define and implement a retention window + deletion policy for conversation logs and cached tutor sessions.
- [x] Make retention/deletion policy inspectable by the deploying school/institution (e.g., an admin-facing report, not just an internal doc).
- [x] Treat all of the above as day-one design inputs. Do not schedule this as a "later" security task — retrofitting consent/deletion into a built system is significantly harder and is explicitly called out as a project risk.

---

## 9. Security & Privacy

- [x] Minimize retention of: student voice, personal information, conversation logs, uploaded documents — beyond what §8 requires.
- [x] Review the specific storage/retention behavior of whichever Gemini API mechanism is used (context caching vs. file storage) — retention characteristics differ by feature and model version. Re-check this whenever the pinned model changes.

---

## 10. Technology Stack

| Layer | Choice |
|---|---|
| Document layer | PDF parser, native extraction, layout intelligence |
| Vision | Layout detection, region classification, figure understanding |
| OCR | Marathi TrOCR-style specialized recognizer |
| Marathi NLP | MahaNLP, MahaBERT, Marathi NER, lexical resources |
| Teacher | Current-generation Gemini Flash-tier model (pinned as config, re-validated on deprecation) |
| Student | AksharSetu deep-learning models (A–E) |
| ASR | AI4Bharat IndicConformer (Marathi monolingual) |
| VAD | Silero VAD |
| TTS | IndicF5 (benchmark against alternatives before freezing) |
| Backend | FastAPI, PostgreSQL, Redis, object storage, vector/search layer as needed |
| Frontend | React/TypeScript — accessible student shell; separate teacher/admin dashboards |

- [x] Before freezing the stack: verify current status/versions of IndicConformer, IndicF5, and MahaBERT/L3Cube against upstream repos — these move independently of this project.

---

## 11. Versioning — build this as an actual data table/service, not documentation

Track version identifiers for:
```
textbook edition, document hash, dataset version, annotation version,
model version, prompt version, teacher model version,
Golden Corpus version, TTS version
```
- [x] The pinned Gemini model string (§4) lives here as data — never hardcoded in prose/architecture code.
- [x] Every Golden Corpus record and every tutor answer must be traceable to a specific value in this table.

---

## 12. System Architecture (reference diagram)

```
AksharBharati/Balbharati PDF
        |
PDF Evidence Preservation (native text, geometry, images/vectors)
        |
Document Perception -> Physical Document Graph
        |
Gemini Teacher Layer -> Teacher-Generated Corpus -> Golden Training Data
        |
AksharSetu Deep Models -> Learning Graph
        |
Pedagogical Orchestrator
        |
   +----+----+
Reading Mode   Tutor Mode
   |               |
Canonical text   Grounded, verified explanation
   +----+----+
        |
Response Planner -> Marathi TTS -> Audio
```
Camera ingestion (Phase 8): capture → quality check → normalization → same downstream pipeline as PDFs. Do not build it as a separate system.

---

## 13. Limitations & Open Risks (keep visible in project tracker, revisit each phase gate)

- **Model drift risk:** teacher model will keep changing; annotation quality/format may shift between versions — re-validate each time (§4).
- **Annotation noise risk:** Gemini's output is a hypothesis, not ground truth — Stage D human review (§5.3) is not optional; its throughput may bottleneck the whole pipeline.
- **Scope risk:** the full architecture (5 models, 3 graphs, full voice stack) is multi-year. Without strict MVP-first sequencing (§1), there's a real risk of building infrastructure before any student uses the system.
- **Legal risk:** unresolved licensing (§2.2) can block deployment regardless of technical progress.
- **Cost risk:** teacher-pipeline + tutor-inference costs (§7) scale with corpus size and usage in ways not historically budgeted.
- **Equity/access risk:** cloud-API dependence needs an offline/low-connectivity fallback story for low-resource-school contexts — the exact contexts where this tool matters most. Track this as an explicit open design question, not a "nice to have."

---

## 14. Suggested Repo Structure

```
aksharsetu/
├── LICENSING.md                     # §2.2 — must be filled before Phase 1
├── implementation.md                # this file
├── docs/
│   └── methodology_v2.pdf
├── infra/
│   ├── db/                          # Postgres schemas: documents, pages, regions, corpus
│   ├── cache/                       # Redis config
│   └── storage/                     # object storage config
├── ingestion/
│   ├── pdf_parser/                  # native text/coords/images/vectors extraction
│   ├── camera_ingestion/            # Phase 8 only — do not build early
│   └── hashing.py                   # source_hash / provenance root
├── teacher/
│   ├── gemini_client.py             # role-based, versioned model config (§4)
│   ├── prompts/
│   └── regression_sample/           # fixed set for re-validation on deprecation
├── corpus/
│   ├── schema.py                    # Golden Corpus record (§3.3)
│   ├── verification/                # Teacher Output -> Verified -> Golden Truth
│   └── provenance_chain.py
├── models/
│   ├── model_a_ocr/                 # MVP
│   ├── model_b_layout/              # MVP
│   ├── model_c_reading_order/       # post-MVP, gated
│   ├── model_d_semantic_relation/   # post-MVP, gated
│   └── model_e_nlp_layer/           # post-MVP, uses MahaBERT/L3Cube
├── correction/
│   └── critical_token_pipeline.py   # §5.4
├── graphs/
│   ├── physical_document_graph.py
│   └── learning_graph.py
├── orchestrator/
│   ├── reading_mode.py
│   └── tutor_mode.py
├── voice/                           # Phase 7 only
│   ├── asr_indicconformer/
│   ├── vad_silero/
│   └── tts_indicf5/
├── governance/
│   ├── consent_flow.py              # §8
│   └── retention_policy.py          # §8
├── eval/
│   ├── ocr_metrics.py
│   ├── higher_level_metrics.py
│   ├── tutor_metrics.py
│   └── phase_gate_checks.py         # automated gate verification (§6.6)
├── cost_model/
│   └── teacher_cost_tracker.py      # §7
├── backend/                         # FastAPI
├── frontend/                        # React/TypeScript
└── versioning/
    └── version_ledger.py            # §11
```

---

## 15. First Sprint Checklist for Antigravity (concrete starting tasks)

1. Scaffold repo structure above.
2. Implement `hashing.py` + provenance chain skeleton.
3. Implement PDF ingestion (native text/coords/images/vectors extraction) for a single sample AksharBharati PDF.
4. Draft and get sign-off on `LICENSING.md` — **do not proceed further until this is resolved.**
5. Implement `gemini_client.py` with model name as a config value (never hardcoded), pointing at current-gen Gemini Flash-tier.
6. Run the 200–500 page pilot (§2.3) once licensing allows; produce the feasibility checkpoint report.
7. Build Golden Corpus schema + three-tier verification state machine.
8. Only after 1–7: begin Model A / Model B training per §5.3.
