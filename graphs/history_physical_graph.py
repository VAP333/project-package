"""
AksharSetu — Class 8 History Physical Document Graph (Phase 2)

Answers: "WHERE IS THIS INFORMATION IN THE TEXTBOOK?"

Minimum Entities:
1. Document (HistoryPhysicalDocument)
2. Chapter (HistoryPhysicalChapter)
3. Page (HistoryPhysicalPage)
4. Region (HistoryPhysicalRegion)
5. SourceElement (HistoryPhysicalSourceElement)

Minimum Relationships:
1. Document -> Chapter
2. Chapter -> Page
3. Page -> Region
4. Region -> Region (preceding, following, adjacent)
5. Region -> LearningUnit

Provenance & Invariants:
- All objects preserve document_id, chapter_id, page_id, region_id, source_type, source_status, verification_status.
- bbox is EXPLICITLY None (never fabricated).
- visual_description_status is EXPLICITLY "UNVERIFIED" (never fabricated).
- verification_status distinguishes SOURCE_VERIFIED from GOLDEN_TRUTH.
"""

from dataclasses import dataclass, field, asdict
from typing import Dict, List, Optional, Any, Tuple
import re

from corpus.history_loader import history_corpus_loader, HistoryChapterMetadata, ExtractedPageSource


@dataclass
class HistoryPhysicalSourceElement:
    element_id: str
    region_id: str
    document_id: str
    chapter_id: str
    page_id: str
    raw_text: str
    source_type: str = "raw_extracted_line"
    source_status: str = "SOURCE_VERIFIED"
    verification_status: str = "UNVERIFIED"

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


@dataclass
class HistoryPhysicalRegion:
    region_id: str
    document_id: str
    chapter_id: str
    page_id: str
    pdf_page_number: int
    printed_page_number: int
    region_type: str  # "heading", "body_paragraph", "boxed_fact", "activity_box", "exercise_header", "caption"
    text: str
    source_type: str = "pdf_extracted_text"
    source_elements: List[HistoryPhysicalSourceElement] = field(default_factory=list)
    bbox: Optional[List[float]] = None  # EXPLICITLY None per spec - unverified in text extraction
    visual_description_status: str = "UNVERIFIED"  # EXPLICITLY UNVERIFIED
    source_status: str = "SOURCE_VERIFIED"
    verification_status: str = "TEACHER_OUTPUT"  # Not GOLDEN_TRUTH
    preceding_region_id: Optional[str] = None
    following_region_id: Optional[str] = None
    adjacent_region_ids: List[str] = field(default_factory=list)
    learning_unit_id: Optional[str] = None

    def to_dict(self) -> Dict[str, Any]:
        d = asdict(self)
        d["source_elements"] = [e.to_dict() for e in self.source_elements]
        return d


@dataclass
class HistoryPhysicalPage:
    page_id: str
    document_id: str
    pdf_page_number: int
    printed_page_number: int
    section: str  # "front_matter", "chapter_content", "back_cover"
    chapter_id: Optional[str]
    regions: List[HistoryPhysicalRegion] = field(default_factory=list)
    source_status: str = "SOURCE_VERIFIED"
    verification_status: str = "SOURCE_VERIFIED"

    def get_regions(self) -> List[HistoryPhysicalRegion]:
        return self.regions

    def to_dict(self) -> Dict[str, Any]:
        return {
            "page_id": self.page_id,
            "document_id": self.document_id,
            "pdf_page_number": self.pdf_page_number,
            "printed_page_number": self.printed_page_number,
            "section": self.section,
            "chapter_id": self.chapter_id,
            "total_regions": len(self.regions),
            "regions": [r.to_dict() for r in self.regions],
            "source_status": self.source_status,
            "verification_status": self.verification_status
        }


@dataclass
class HistoryPhysicalChapter:
    chapter_id: str
    chapter_number: int
    title_marathi: str
    title_english_gloss: str
    document_id: str
    pdf_page_range: List[int]
    printed_page_range: List[int]
    pages: Dict[int, HistoryPhysicalPage] = field(default_factory=dict)
    source_status: str = "SOURCE_VERIFIED"
    verification_status: str = "SOURCE_VERIFIED"

    def get_pages(self) -> List[HistoryPhysicalPage]:
        return [self.pages[p] for p in range(self.pdf_page_range[0], self.pdf_page_range[1] + 1) if p in self.pages]

    def to_dict(self) -> Dict[str, Any]:
        return {
            "chapter_id": self.chapter_id,
            "chapter_number": self.chapter_number,
            "title_marathi": self.title_marathi,
            "title_english_gloss": self.title_english_gloss,
            "document_id": self.document_id,
            "pdf_page_range": self.pdf_page_range,
            "printed_page_range": self.printed_page_range,
            "total_pages": len(self.pages),
            "pages": [p.to_dict() for p in self.get_pages()],
            "source_status": self.source_status,
            "verification_status": self.verification_status
        }


class HistoryPhysicalDocumentGraph:
    """
    Physical Document Graph representing the spatial and structural location of
    all content in Class 8 History.
    Answers: "WHERE IS THIS INFORMATION IN THE TEXTBOOK?"
    """

    def __init__(self, loader=history_corpus_loader):
        self.loader = loader
        self.document_id = "AKS_HISTORY_CLASS8_HISTORY"
        self.title = "इतिहास व नागरिकशास्त्र, इयत्ता आठवी (इतिहास विभाग)"
        self.total_pages = 75
        self.chapters: Dict[str, HistoryPhysicalChapter] = {}
        self.pages: Dict[int, HistoryPhysicalPage] = {}
        self.regions_by_id: Dict[str, HistoryPhysicalRegion] = {}
        self.regions_by_unit: Dict[str, List[str]] = {}
        self._built = False

    def build_graph(self) -> "HistoryPhysicalDocumentGraph":
        """Builds and links the complete physical document graph."""
        if self._built:
            return self

        self.chapters.clear()
        self.pages.clear()
        self.regions_by_id.clear()
        self.regions_by_unit.clear()

        self.loader.validate_and_load()

        # 1. Instantiate pages for all 75 pages
        for page_num in range(1, 76):
            page_src = self.loader.pages.get(page_num)
            printed_num = page_num - 9 if page_num >= 10 else page_num
            ch_id = page_src.chapter_id if page_src else None
            section = page_src.section if page_src else ("front_matter" if page_num < 10 else "chapter_content")

            p_graph = HistoryPhysicalPage(
                page_id=f"AKS_HIST_P{page_num:02d}",
                document_id=self.document_id,
                pdf_page_number=page_num,
                printed_page_number=printed_num,
                section=section,
                chapter_id=ch_id,
                regions=[],
                source_status="SOURCE_VERIFIED",
                verification_status="SOURCE_VERIFIED"
            )
            self.pages[page_num] = p_graph

        # 2. Instantiate all 14 chapters
        for ch_meta in self.loader.list_all_chapters():
            ch_graph = HistoryPhysicalChapter(
                chapter_id=ch_meta.chapter_id,
                chapter_number=ch_meta.chapter_number,
                title_marathi=ch_meta.title_marathi,
                title_english_gloss=ch_meta.title_english_gloss,
                document_id=self.document_id,
                pdf_page_range=ch_meta.pdf_page_range,
                printed_page_range=ch_meta.printed_page_range,
                pages={},
                source_status="SOURCE_VERIFIED",
                verification_status="SOURCE_VERIFIED"
            )

            # Link Chapter -> Page
            start_p, end_p = ch_meta.pdf_page_range
            for p in range(start_p, end_p + 1):
                page_obj = self.pages[p]
                ch_graph.pages[p] = page_obj

            self.chapters[ch_meta.chapter_id] = ch_graph

        # 3. Extract and link Regions within each page & Chapter
        all_chapter_regions: List[HistoryPhysicalRegion] = []

        for ch_meta in self.loader.list_all_chapters():
            ch_id = ch_meta.chapter_id
            units = ch_meta.learning_units
            start_p, end_p = ch_meta.pdf_page_range

            ch_regions: List[HistoryPhysicalRegion] = []

            for p_num in range(start_p, end_p + 1):
                p_obj = self.pages[p_num]
                p_src = self.loader.pages.get(p_num)
                raw_text = p_src.raw_extracted_text if p_src else ""

                lines = [l.strip() for l in raw_text.split("\n") if l.strip()]
                reg_idx = 1
                curr_para: List[str] = []

                # Associate learning units across pages
                unit_idx = min(len(units) - 1, max(0, int((p_num - start_p) / max(1, end_p - start_p) * len(units))))
                assigned_unit = f"{ch_id}_LU_{unit_idx + 1:02d}"

                for line in lines:
                    is_box = any(box in line for box in ["माहीत आहे का तुम्हांला", "करून पहा", "जरा विचार करा", "चला जाणून घेऊया"])
                    is_exercise = "स्वाध्याय" in line

                    if is_box or is_exercise:
                        if curr_para:
                            reg_id = f"{ch_id}_p{p_num}_r{reg_idx}"
                            region = self._create_region(
                                reg_id=reg_id,
                                ch_id=ch_id,
                                p_num=p_num,
                                printed_num=p_obj.printed_page_number,
                                r_type="body_paragraph",
                                text=" ".join(curr_para),
                                unit_id=assigned_unit
                            )
                            ch_regions.append(region)
                            p_obj.regions.append(region)
                            self.regions_by_id[reg_id] = region
                            reg_idx += 1
                            curr_para = []

                        r_type = "exercise_header" if is_exercise else "boxed_fact"
                        reg_id = f"{ch_id}_p{p_num}_r{reg_idx}"
                        region = self._create_region(
                            reg_id=reg_id,
                            ch_id=ch_id,
                            p_num=p_num,
                            printed_num=p_obj.printed_page_number,
                            r_type=r_type,
                            text=line,
                            unit_id=f"{ch_id}_LU_ASSESS" if is_exercise else assigned_unit
                        )
                        ch_regions.append(region)
                        p_obj.regions.append(region)
                        self.regions_by_id[reg_id] = region
                        reg_idx += 1
                    else:
                        curr_para.append(line)
                        if len(curr_para) >= 4 or line.endswith(("।", "?", "!", ".")):
                            reg_id = f"{ch_id}_p{p_num}_r{reg_idx}"
                            region = self._create_region(
                                reg_id=reg_id,
                                ch_id=ch_id,
                                p_num=p_num,
                                printed_num=p_obj.printed_page_number,
                                r_type="body_paragraph",
                                text=" ".join(curr_para),
                                unit_id=assigned_unit
                            )
                            ch_regions.append(region)
                            p_obj.regions.append(region)
                            self.regions_by_id[reg_id] = region
                            reg_idx += 1
                            curr_para = []

                if curr_para:
                    reg_id = f"{ch_id}_p{p_num}_r{reg_idx}"
                    region = self._create_region(
                        reg_id=reg_id,
                        ch_id=ch_id,
                        p_num=p_num,
                        printed_num=p_obj.printed_page_number,
                        r_type="body_paragraph",
                        text=" ".join(curr_para),
                        unit_id=assigned_unit
                    )
                    ch_regions.append(region)
                    p_obj.regions.append(region)
                    self.regions_by_id[reg_id] = region

            # Link Region -> Region (preceding, following, adjacent within chapter)
            for i, r in enumerate(ch_regions):
                if i > 0:
                    r.preceding_region_id = ch_regions[i - 1].region_id
                if i < len(ch_regions) - 1:
                    r.following_region_id = ch_regions[i + 1].region_id

                # Adjacent regions on the same page
                page_siblings = [sibling.region_id for sibling in ch_regions if sibling.page_id == r.page_id and sibling.region_id != r.region_id]
                r.adjacent_region_ids = page_siblings

                # Track Region -> LearningUnit
                if r.learning_unit_id:
                    if r.learning_unit_id not in self.regions_by_unit:
                        self.regions_by_unit[r.learning_unit_id] = []
                    self.regions_by_unit[r.learning_unit_id].append(r.region_id)

            all_chapter_regions.extend(ch_regions)

        self._built = True
        return self

    def _create_region(
        self,
        reg_id: str,
        ch_id: str,
        p_num: int,
        printed_num: int,
        r_type: str,
        text: str,
        unit_id: Optional[str] = None
    ) -> HistoryPhysicalRegion:
        page_id = f"AKS_HIST_P{p_num:02d}"

        # Source elements correspond to raw lines
        lines = text.split(" ")
        src_elements = [
            HistoryPhysicalSourceElement(
                element_id=f"{reg_id}_el{i}",
                region_id=reg_id,
                document_id=self.document_id,
                chapter_id=ch_id,
                page_id=page_id,
                raw_text=line,
                source_type="raw_extracted_text",
                source_status="SOURCE_VERIFIED",
                verification_status="UNVERIFIED"
            )
            for i, line in enumerate(lines[:10], 1)
        ]

        return HistoryPhysicalRegion(
            region_id=reg_id,
            document_id=self.document_id,
            chapter_id=ch_id,
            page_id=page_id,
            pdf_page_number=p_num,
            printed_page_number=printed_num,
            region_type=r_type,
            text=text,
            source_type="pdf_extracted_text",
            source_elements=src_elements,
            bbox=None,  # EXPLICITLY None - no fabricated bboxes
            visual_description_status="UNVERIFIED",  # EXPLICITLY UNVERIFIED
            source_status="SOURCE_VERIFIED",
            verification_status="TEACHER_OUTPUT",
            preceding_region_id=None,
            following_region_id=None,
            adjacent_region_ids=[],
            learning_unit_id=unit_id
        )

    # --- Query API ---

    def get_document(self) -> Dict[str, Any]:
        self.build_graph()
        return {
            "document_id": self.document_id,
            "title": self.title,
            "total_pages": self.total_pages,
            "total_chapters": len(self.chapters),
            "source_status": "SOURCE_VERIFIED",
            "verification_status": "SOURCE_VERIFIED"
        }

    def get_chapter(self, chapter_id: str) -> Optional[HistoryPhysicalChapter]:
        self.build_graph()
        return self.chapters.get(chapter_id)

    def get_page(self, pdf_page_number: int) -> Optional[HistoryPhysicalPage]:
        self.build_graph()
        return self.pages.get(pdf_page_number)

    def get_region(self, region_id: str) -> Optional[HistoryPhysicalRegion]:
        self.build_graph()
        return self.regions_by_id.get(region_id)

    def get_regions_for_learning_unit(self, unit_id: str) -> List[HistoryPhysicalRegion]:
        self.build_graph()
        reg_ids = self.regions_by_unit.get(unit_id, [])
        return [self.regions_by_id[rid] for rid in reg_ids if rid in self.regions_by_id]

    @property
    def total_regions(self) -> int:
        self.build_graph()
        return len(self.regions_by_id)

    @property
    def regions(self) -> Dict[str, HistoryPhysicalRegion]:
        self.build_graph()
        return self.regions_by_id


history_physical_graph = HistoryPhysicalDocumentGraph()
# Cache-bust reload: Class 8 History Chapter 1 Page 11 (printed page 2) extract populated
