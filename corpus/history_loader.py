"""
AksharSetu — Class 8 History Corpus Loader (Phase 1)

Loads and validates the baseline History corpus:
- corpus/dataset/history/corpus_structured.json
- corpus/dataset/history/page_source_extract.jsonl
- corpus/dataset/history/corpus_analysis.md
- corpus/dataset/history/History.pdf

Enforces:
- Schema validation without modifying source files.
- Provenance tracking (SOURCE_VERIFIED, SUPPORTED_INFERENCE, AKSHARSETU_RECOMMENDATION, TEACHER_OUTPUT, UNVERIFIED).
- Exact chapter page ranges (Front matter pp. 1-9, Content pp. 10-74, Back cover p. 75).
- 14 chapters inventory with learning units, concepts, named entities, and assessment structures.
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
class DocumentManifest:
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
    back_cover_pdf_page_range: List[int]
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
class ChapterAssessment:
    mcq_count: int
    reasoned_statements_count: int
    short_notes_count: int
    concept_map_count: int
    activity_projects_count: int
    types_present: List[str]


@dataclass
class HistoryChapterMetadata:
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
    assessment: ChapterAssessment
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
    extraction_caveats: List[str]
    source_status: str


class HistoryCorpusLoader:
    """
    Dedicated, immutable corpus loader for Class 8 History.
    Validates data integrity across JSON, JSONL, MD, and PDF.
    """

    def __init__(self, base_dir: Optional[str] = None):
        self.base_dir = base_dir or os.path.join("corpus", "dataset", "history")
        self.structured_json_path = os.path.join(self.base_dir, "corpus_structured.json")
        self.page_extract_jsonl_path = os.path.join(self.base_dir, "page_source_extract.jsonl")
        self.analysis_md_path = os.path.join(self.base_dir, "corpus_analysis.md")
        self.pdf_path = os.path.join(self.base_dir, "History.pdf")

        self.manifest: Optional[DocumentManifest] = None
        self.chapters: Dict[str, HistoryChapterMetadata] = {}
        self.pages: Dict[int, ExtractedPageSource] = {}
        self.grammar_metadata: Dict[str, Any] = {}
        self.pronunciation_lexicon: List[Dict[str, Any]] = []

    def validate_and_load(self) -> "HistoryCorpusLoader":
        """Loads and strictly validates all corpus files."""
        # 1. Check existence of all 4 baseline files
        for path, name in [
            (self.structured_json_path, "corpus_structured.json"),
            (self.page_extract_jsonl_path, "page_source_extract.jsonl"),
            (self.analysis_md_path, "corpus_analysis.md"),
            (self.pdf_path, "History.pdf")
        ]:
            if not os.path.exists(path):
                raise FileNotFoundError(f"History corpus baseline file missing: {name} at {path}")

        # 2. Load structured JSON
        with open(self.structured_json_path, "r", encoding="utf-8") as f:
            structured_data = json.load(f)

        raw_manifest = structured_data.get("document_manifest", {})
        if raw_manifest.get("document_id") != "AKS_HISTORY_CLASS8_HISTORY":
            raise ValueError(f"Unexpected document_id: {raw_manifest.get('document_id')}")
        if raw_manifest.get("subject") != "history" or raw_manifest.get("class") != 8:
            raise ValueError("Corpus is not Class 8 History")

        self.manifest = DocumentManifest(
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
            back_cover_pdf_page_range=raw_manifest["back_cover_pdf_page_range"],
            printed_page_offset=raw_manifest["printed_page_offset"],
            source_status=raw_manifest["source_status"],
            note=raw_manifest.get("note", ""),
            pdf_path=self.pdf_path
        )

        self.grammar_metadata = structured_data.get("cross_chapter_class8_history_grammar", {})

        # 3. Load Chapter Inventory (14 chapters)
        raw_chapters = structured_data.get("chapter_inventory", [])
        if len(raw_chapters) != 14:
            raise ValueError(f"Expected 14 chapters in History corpus, found {len(raw_chapters)}")

        for ch in raw_chapters:
            ch_id = ch["chapter_id"]
            assessment_data = ch.get("assessment", {})
            assessment = ChapterAssessment(
                mcq_count=assessment_data.get("mcq_count", 0),
                reasoned_statements_count=assessment_data.get("reasoned_statements_count", 0),
                short_notes_count=assessment_data.get("short_notes_count", 0),
                concept_map_count=assessment_data.get("concept_map_count", 0),
                activity_projects_count=assessment_data.get("activity_projects_count", 0),
                types_present=assessment_data.get("types_present", [])
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
                for b in ch.get("visual_and_boxed_elements", [])
            ]

            meta = HistoryChapterMetadata(
                chapter_id=ch_id,
                chapter_number=ch["chapter_number"],
                title_marathi=ch["title_marathi"],
                title_english_gloss=ch.get("title_english_gloss", ""),
                pdf_page_range=ch["pdf_page_range"],
                printed_page_range=ch["printed_page_range"],
                chapter_type=ch.get("chapter_type", "history_narrative_expository"),
                structural_pattern=ch.get("structural_pattern", {}),
                learning_units=ch.get("learning_units", []),
                key_concepts=concepts,
                pronunciation_risk_entities=ch.get("pronunciation_risk_named_entities", []),
                visual_and_boxed_elements=boxed,
                assessment=assessment,
                narration_policy=ch.get("narration_policy", "READ_THEN_EXPLAIN"),
                speaking_style=ch.get("speaking_style", "historical_narration"),
                audience=ch.get("audience", "STUDENT"),
                student_relevance=ch.get("student_relevance", "ESSENTIAL"),
                source_status=ch.get("source_status", "SOURCE_VERIFIED"),
                verification_status=ch.get("verification_status", "TEACHER_OUTPUT")
            )
            self.chapters[ch_id] = meta

            # Collect pronunciation entities
            for ent in meta.pronunciation_risk_entities:
                self.pronunciation_lexicon.append({
                    "canonical_text": ent,
                    "chapter_id": ch_id,
                    "subject": "history",
                    "risk_type": "proper_noun_historical",
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
                    document_id=row.get("document_id", "AKS_HISTORY_CLASS8_HISTORY"),
                    pdf_page_number=page_num,
                    section=row.get("section", ""),
                    chapter_id=row.get("chapter_id"),
                    raw_extracted_text=row.get("raw_extracted_text", ""),
                    extraction_method=row.get("extraction_method", ""),
                    extraction_caveats=row.get("extraction_caveats", []),
                    source_status=row.get("source_status", "SOURCE_VERIFIED")
                )
                self.pages[page_num] = page_src

        # 5. Validate corpus_analysis.md integrity
        with open(self.analysis_md_path, "r", encoding="utf-8") as f:
            analysis_text = f.read()
        required_analysis_headers = [
            "## A. Document manifest",
            "## B. Complete chapter inventory",
            "## C. Discovered textbook grammar",
            "## D. Narration & speaking-style grammar",
            "## E. Pronunciation-risk lexicon",
            "## F. Assessment structure",
            "## G. Cacheable artifacts",
            "## H. Chapter-specific exceptions",
            "## I. Human verification queue",
            "## J. Scope and what's deferred"
        ]
        for hdr in required_analysis_headers:
            if hdr not in analysis_text:
                raise ValueError(f"Corpus analysis markdown missing mandatory section: '{hdr}'")

        # 6. Validate Contiguous Chapter Page Ranges (PDF pp. 10 to 74)
        sorted_chs = sorted(self.chapters.values(), key=lambda c: c.chapter_number)
        current_expected_start = 10
        for ch in sorted_chs:
            start_p, end_p = ch.pdf_page_range
            if start_p != current_expected_start:
                raise ValueError(
                    f"Page range discontinuity in {ch.chapter_id}: expected start {current_expected_start}, found {start_p}"
                )
            if end_p < start_p:
                raise ValueError(f"Invalid page range in {ch.chapter_id}: [{start_p}, {end_p}]")
            current_expected_start = end_p + 1

        if current_expected_start != 75:
            raise ValueError(f"Chapters content did not conclude at PDF page 74 (next expected: {current_expected_start})")

        return self

    def get_chapter(self, chapter_id: str) -> Optional[HistoryChapterMetadata]:
        return self.chapters.get(chapter_id)

    def get_pages_for_chapter(self, chapter_id: str) -> List[ExtractedPageSource]:
        ch = self.chapters.get(chapter_id)
        if not ch:
            return []
        start, end = ch.pdf_page_range
        return [self.pages[p] for p in range(start, end + 1) if p in self.pages]

    def list_all_chapters(self) -> List[HistoryChapterMetadata]:
        return list(sorted(self.chapters.values(), key=lambda c: c.chapter_number))

    # --- Corpus Trust Model & Invariant Enforcers ---

    def is_golden_truth(self, entity_or_status: Any) -> bool:
        """
        CORPUS TRUST MODEL RULE:
        SOURCE_VERIFIED does NOT automatically mean GOLDEN_TRUTH.
        The current History corpus is v0.1 baseline, where region-level bounding boxes
        and complete visual verification are explicitly deferred.
        Therefore, no baseline entity is promoted to GOLDEN_TRUTH without verified physical inspection.
        """
        return False

    def get_trust_level(self, status: str) -> ProvenanceStatus:
        try:
            return ProvenanceStatus(status)
        except ValueError:
            return ProvenanceStatus.UNVERIFIED


history_corpus_loader = HistoryCorpusLoader()
