"""
AksharSetu — Class 8 Science Corpus Loader (Phase 1)

Loads and validates the baseline General Science corpus:
- corpus/dataset/Science/corpus_structured.json
- corpus/dataset/Science/page_source_extract.jsonl
- corpus/dataset/Science/corpus_analysis.md
- corpus/dataset/Science/Science.pdf

Enforces:
- Schema validation without modifying source files.
- Provenance tracking (SOURCE_VERIFIED, SUPPORTED_INFERENCE, AKSHARSETU_RECOMMENDATION, TEACHER_OUTPUT, UNVERIFIED).
- Exact chapter page ranges (Front matter pp. 1-10, Content pp. 11-144, Back matter/glossary pp. 145-148).
- 19 chapters inventory with learning units, concepts, pronunciation risks, and activity/boxed structures.
- Back-matter शब्दसूची (pp. 145-146) glossary ingestion.
"""

import os
import json
from dataclasses import dataclass, field, asdict
from typing import Dict, List, Optional, Any, Tuple
from enum import Enum


class ProvenanceStatus(str, Enum):
    SOURCE_VERIFIED = "SOURCE_VERIFIED"
    SUPPORTED_INFERENCE = "SUPPORTED_INFERENCE"
    AKSHARSETU_RECOMMENDATION = "AKSHARSETU_RECOMMENDATION"
    TEACHER_OUTPUT = "TEACHER_OUTPUT"
    UNVERIFIED = "UNVERIFIED"
    CONFLICTING = "CONFLICTING"


@dataclass
class ScienceDocumentManifest:
    document_id: str
    title_marathi: str
    title_english: str
    subject: str
    class_num: int
    medium: str
    curriculum_board: str
    publisher: str
    first_edition_year: int
    pdf_total_pages: int
    content_pdf_page_range: List[int]
    front_matter_pdf_page_range: List[int]
    back_matter_pdf_page_range: List[int]
    printed_page_offset: str
    source_status: str
    note: str
    pdf_path: str


@dataclass
class KeyConcept:
    concept: str
    gloss: str


@dataclass
class BoxedElement:
    type: str
    topic: str
    narration_policy: str


@dataclass
class ScienceChapterAssessment:
    types_present: List[str]
    raw_counts: Dict[str, Any]


@dataclass
class ScienceChapterMetadata:
    chapter_id: str
    chapter_number: int
    title_marathi: str
    title_english_gloss: str
    pdf_page_range: List[int]
    printed_page_range: List[int]
    chapter_type: str
    structural_pattern: Dict[str, Any]
    learning_units: List[str]
    key_concepts: List[KeyConcept]
    pronunciation_risk_entities: List[str]
    visual_and_boxed_elements: List[BoxedElement]
    assessment: ScienceChapterAssessment
    narration_policy: str
    speaking_style: str
    audience: str
    student_relevance: str
    source_status: str
    verification_status: str


@dataclass
class ExtractedPageSource:
    document_id: str
    pdf_page_number: int
    section: str
    chapter_id: Optional[str]
    raw_extracted_text: str
    extraction_method: str
    extraction_caveats: str
    source_status: str


@dataclass
class GlossaryTerm:
    marathi_term: str
    english_term: str
    phonetic_transliteration: str
    page_number: int


class ScienceCorpusLoader:
    """
    Dedicated, immutable corpus loader for Class 8 Science.
    Validates data integrity across JSON, JSONL, MD, and PDF.
    """

    def __init__(self, base_dir: Optional[str] = None):
        default_dir = os.path.join("corpus", "dataset", "Science")
        if not os.path.exists(default_dir):
            default_dir = os.path.join("corpus", "dataset", "science")
        self.base_dir = base_dir or default_dir
        self.structured_json_path = os.path.join(self.base_dir, "corpus_structured.json")
        self.page_extract_jsonl_path = os.path.join(self.base_dir, "page_source_extract.jsonl")
        self.analysis_md_path = os.path.join(self.base_dir, "corpus_analysis.md")
        self.pdf_path = os.path.join(self.base_dir, "Science.pdf")

        self.manifest: Optional[ScienceDocumentManifest] = None
        self.chapters: Dict[str, ScienceChapterMetadata] = {}
        self.pages: Dict[int, ExtractedPageSource] = {}
        self.grammar_metadata: Dict[str, Any] = {}
        self.pronunciation_lexicon: List[Dict[str, Any]] = []
        self.glossary_terms: List[GlossaryTerm] = []
        self._loaded = False

    def validate_and_load(self) -> "ScienceCorpusLoader":
        """Loads and strictly validates all corpus files."""
        if self._loaded:
            return self

        # 1. Check existence of baseline files
        for path, name in [
            (self.structured_json_path, "corpus_structured.json"),
            (self.page_extract_jsonl_path, "page_source_extract.jsonl"),
            (self.analysis_md_path, "corpus_analysis.md"),
            (self.pdf_path, "Science.pdf")
        ]:
            if not os.path.exists(path):
                raise FileNotFoundError(f"Science corpus baseline file missing: {name} at {path}")

        # 2. Load structured JSON
        with open(self.structured_json_path, "r", encoding="utf-8") as f:
            structured_data = json.load(f)

        raw_manifest = structured_data.get("document_manifest", {})
        if raw_manifest.get("document_id") != "AKS_SCIENCE_CLASS8_SCIENCE":
            raise ValueError(f"Unexpected document_id: {raw_manifest.get('document_id')}")
        if raw_manifest.get("subject") != "science" or raw_manifest.get("class") != 8:
            raise ValueError("Corpus is not Class 8 Science")

        self.manifest = ScienceDocumentManifest(
            document_id=raw_manifest["document_id"],
            title_marathi=raw_manifest["title_marathi"],
            title_english=raw_manifest["title_english"],
            subject=raw_manifest["subject"],
            class_num=raw_manifest["class"],
            medium=raw_manifest["medium"],
            curriculum_board=raw_manifest["curriculum_board"],
            publisher=raw_manifest["publisher"],
            first_edition_year=raw_manifest["first_edition_year"],
            pdf_total_pages=raw_manifest["pdf_total_pages"],
            content_pdf_page_range=raw_manifest["content_pdf_page_range"],
            front_matter_pdf_page_range=raw_manifest["front_matter_pdf_page_range"],
            back_matter_pdf_page_range=raw_manifest.get("back_matter_pdf_page_range", [145, 148]),
            printed_page_offset=raw_manifest["printed_page_offset"],
            source_status=raw_manifest["source_status"],
            note=raw_manifest.get("note", ""),
            pdf_path=self.pdf_path
        )

        self.grammar_metadata = structured_data.get("cross_chapter_class8_science_grammar", {})

        # 3. Load Chapter Inventory (19 chapters)
        raw_chapters = structured_data.get("chapter_inventory", [])
        if len(raw_chapters) != 19:
            raise ValueError(f"Expected 19 chapters in Science corpus, found {len(raw_chapters)}")

        for ch in raw_chapters:
            ch_id = ch["chapter_id"]
            assessment_data = ch.get("assessment", {})
            types_present = assessment_data.get("types_present", [])
            assessment = ScienceChapterAssessment(
                types_present=types_present,
                raw_counts={k: v for k, v in assessment_data.items() if k != "types_present"}
            )

            concepts = [
                KeyConcept(concept=c.get("concept", ""), gloss=c.get("gloss", ""))
                for c in ch.get("key_concepts_defined", [])
            ]

            boxed = [
                BoxedElement(
                    type=b.get("type", ""),
                    topic=b.get("topic", ""),
                    narration_policy=b.get("narration_policy", "")
                )
                for b in ch.get("visual_and_activity_elements", [])
            ]

            pron_terms = ch.get("pronunciation_risk_terms", []) or ch.get("pronunciation_risk_named_entities", [])

            meta = ScienceChapterMetadata(
                chapter_id=ch_id,
                chapter_number=ch["chapter_number"],
                title_marathi=ch["title_marathi"],
                title_english_gloss=ch.get("title_english_gloss", ""),
                pdf_page_range=ch["pdf_page_range"],
                printed_page_range=ch["printed_page_range"],
                chapter_type=ch.get("chapter_type", "science_expository"),
                structural_pattern=ch.get("structural_pattern", {}),
                learning_units=ch.get("learning_units", []),
                key_concepts=concepts,
                pronunciation_risk_entities=pron_terms,
                visual_and_boxed_elements=boxed,
                assessment=assessment,
                narration_policy=ch.get("narration_policy", "READ_THEN_EXPLAIN"),
                speaking_style=ch.get("speaking_style", "scientific_explanation"),
                audience=ch.get("audience", "STUDENT"),
                student_relevance=ch.get("student_relevance", "ESSENTIAL"),
                source_status=ch.get("source_status", "SOURCE_VERIFIED"),
                verification_status=ch.get("verification_status", "TEACHER_OUTPUT")
            )
            self.chapters[ch_id] = meta

            for ent in meta.pronunciation_risk_entities:
                self.pronunciation_lexicon.append({
                    "canonical_text": ent,
                    "chapter_id": ch_id,
                    "subject": "science",
                    "risk_type": "technical_terminology",
                    "verification_status": "UNVERIFIED"
                })

        # 4. Load page_source_extract.jsonl
        with open(self.page_extract_jsonl_path, "r", encoding="utf-8") as f:
            for line_num, line in enumerate(f, 1):
                if not line.strip():
                    continue
                row = json.loads(line)
                page_num = row.get("pdf_page_number")
                if page_num is None:
                    raise ValueError(f"Missing pdf_page_number at JSONL line {line_num}")
                page_src = ExtractedPageSource(
                    document_id=row.get("document_id", "AKS_SCIENCE_CLASS8_SCIENCE"),
                    pdf_page_number=page_num,
                    section=row.get("section", ""),
                    chapter_id=row.get("chapter_id"),
                    raw_extracted_text=row.get("raw_extracted_text", ""),
                    extraction_method=row.get("extraction_method", ""),
                    extraction_caveats=str(row.get("extraction_caveats", "")),
                    source_status=row.get("source_status", "RAW_EXTRACTED_TEXT")
                )
                self.pages[page_num] = page_src

                # Parse glossary terms from back matter pages (145, 146)
                if page_src.section == "back_matter_glossary":
                    self._parse_glossary_page(page_src.raw_extracted_text, page_num)

        self._loaded = True
        return self

    def _parse_glossary_page(self, text: str, page_num: int):
        """Extracts high-value Marathi-English-phonetic term triplets from back matter."""
        import re
        lines = text.split("\n")
        for line in lines:
            line = line.strip()
            if not line or "इयत्ता आठवी" in line or "सामान्य विज्ञान" in line:
                continue
            parts = re.split(r'\s{4,}', line)
            for part in parts:
                triplet = [p.strip() for p in part.split(" - ") if p.strip()]
                if len(triplet) >= 3:
                    marathi_t = triplet[0]
                    english_t = triplet[1]
                    phonetic_t = triplet[2]
                    self.glossary_terms.append(GlossaryTerm(
                        marathi_term=marathi_t,
                        english_term=english_t,
                        phonetic_transliteration=phonetic_t,
                        page_number=page_num
                    ))

    def get_chapter(self, chapter_id: str) -> Optional[ScienceChapterMetadata]:
        self.validate_and_load()
        ch_key = chapter_id.upper()
        if ch_key in self.chapters:
            return self.chapters[ch_key]
        if ch_key.startswith("CH_"):
            try:
                num = int(ch_key.split("_")[1])
                fmt_key = f"CH_{num:02d}"
                return self.chapters.get(fmt_key)
            except Exception:
                pass
        return None

    def list_all_chapters(self) -> List[ScienceChapterMetadata]:
        self.validate_and_load()
        return sorted(self.chapters.values(), key=lambda c: c.chapter_number)

    def get_pages_for_chapter(self, chapter_id: str) -> List[ExtractedPageSource]:
        self.validate_and_load()
        ch = self.get_chapter(chapter_id)
        if not ch:
            return []
        start_p, end_p = ch.pdf_page_range
        return [self.pages[p] for p in range(start_p, end_p + 1) if p in self.pages]


science_corpus_loader = ScienceCorpusLoader()
