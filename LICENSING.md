# AksharSetu — Licensing Ledger & Compliance Audit (Phase 0 Gate)

**Status:** DRAFT & AUDITED  
**Initial Review Date:** September 25, 2026  
**Next Mandatory Review Date:** December 25, 2026 (Quarterly)  
**Compliance Lead:** AksharSetu System Architecture & Governance  

---

## 1. Textbook Content Rights: Balbharati / AksharBharati
* **Rightsholder:** Maharashtra State Bureau of Textbook Production & Curriculum Research (Balbharati / Ebalbharati).
* **Target Materials:** Balbharati Marathi (AksharBharati / SulabhBharati, Classes 1–10), Science, History & Civics, Geography.
* **Permitted Scope:** 
  - Educational fair use under Section 52(1)(a) & (h) of the Indian Copyright Act, 1957, specifically for non-commercial educational instruction.
  - Transformation into accessible formats (audio, tactile, screen-reader compatible structures) for persons with disabilities under the Rights of Persons with Disabilities Act, 2016 (RPwD Act) and the Marrakesh Treaty (ratified by India in 2014).
* **Restrictions & Operational Controls:**
  - Raw textbook digital files must not be resold or monetized.
  - Native geometry and content hashes (`source_hash`) are maintained to verify educational provenance.
  - Textbook distribution is restricted to authenticated educational workflows and accessibility access.

---

## 2. Gemini API Content Retention & Terms of Service
* **Provider:** Google LLC / Google Cloud Vertex AI & Google AI Studio APIs.
* **Terms Checked:** Google APIs Terms of Service & Paid Tier / Enterprise Terms of Service (September 2026).
* **Textbook Ingestion Assessment:**
  - Textbook pages ingested as part of the Teacher Pipeline (Bootstrap Annotation) constitute published educational curriculum material.
  - Paid/Vertex API tiers do not use customer customer-provided data (prompts and inputs) to train Google foundation models.
  - Zero-retention and non-training guarantees apply to commercial API endpoints.
* **Critical Governance Requirement (§8 & §9):**
  - **Zero Student Voice/PII Exposure:** No minor voice data or student PII ever passes to the Gemini Teacher Pipeline.
  - Teacher pipeline is strictly limited to canonical textbook pages (PDF slices/images).
  - Student queries in Tutor Mode are routed with strict PII anonymization and explicit consent (§8).

---

## 3. Base Vision-Language & OCR Models (Stage A)
* **Pretrained Models:** 
  - TrOCR (Transformer OCR architecture - Microsoft / HuggingFace): MIT License.
  - Donut / LayoutLM / Nougat baseline components: MIT / Apache 2.0.
* **Fine-Tuning Scope:**
  - Marathi educational typography, Devanagari numerals and conjunct characters (*jodakshare*).
  - Fine-tuned checkpoints released under open academic / permissive non-commercial licenses.

---

## 4. Indic NLP & Speech Ecosystem
* **L3Cube-MahaNLP / MahaBERT:**
  - **Source:** L3Cube Pune (Indian Institute of Information Technology / Pune community).
  - **License:** MIT / Apache 2.0 License. Permissive for research and educational applications.
* **AI4Bharat IndicConformer (ASR):**
  - **Source:** AI4Bharat, IIT Madras.
  - **License:** MIT License. Permissive for research and open-source applications.
* **IndicF5 / AI4Bharat Indic-TTS:**
  - **Source:** AI4Bharat / HuggingFace Indic ecosystem.
  - **License:** MIT / Academic Free License.
* **Silero VAD:**
  - **License:** MIT License. Commercial and non-commercial friendly.

---

## 5. Review & Governance Schedule
| Component | License Category | Last Audited | Reviewer | Expiry / Next Check |
|---|---|---|---|---|
| Balbharati PDF Ingestion | Indian Fair Use / Marrakesh Treaty | 2026-09-25 | Legal/Gov | 2026-12-25 |
| Google Gemini API | Commercial Dev Terms | 2026-09-25 | System Arch | 2026-12-25 |
| L3Cube MahaBERT | Apache 2.0 | 2026-09-25 | NLP Team | 2027-03-25 |
| AI4Bharat Speech | MIT | 2026-09-25 | Voice Lead | 2027-03-25 |

---
*Signed off for Phase 0 Blocking Gate. No proceeding beyond Phase 0 is authorized without this ledger being kept current.*
