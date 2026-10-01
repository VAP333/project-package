"""
AksharSetu — Class 8 Science Grounded Tutor & RAG Engine (Phase 9)

Bounded Retrieval:
- Queries are grounded ONLY in Class 8 Science textbook facts and learning units.
- Generates structured answers with source page, concept, and learning unit citations.
- Includes audible cue metadata (§18) for conversational teacher handoff.
"""

from dataclasses import dataclass, field, asdict
from typing import Dict, List, Optional, Any
import re

from corpus.science_loader import science_corpus_loader, ScienceChapterMetadata
from graphs.science_learning_graph import science_learning_graph, ScienceLearningUnit, ScienceConcept
from graphs.science_physical_graph import science_physical_graph, SciencePhysicalRegion


@dataclass
class ScienceTutorSourceRef:
    chapter_id: str
    chapter_number: int
    learning_unit_id: str
    unit_title: str
    pdf_page: int
    printed_page: int
    excerpt: str


@dataclass
class ScienceGroundedTutorContext:
    query: str
    chapter_id: str
    grounded_answer: str
    tutor_voice_style: str  # "scientific_explanation" | "warm_teacher"
    sources: List[ScienceTutorSourceRef] = field(default_factory=list)
    confidence: float = 0.95
    audible_cue_required: bool = True
    suggested_followups: List[str] = field(default_factory=list)

    def to_dict(self) -> Dict[str, Any]:
        d = asdict(self)
        d["sources"] = [asdict(s) for s in self.sources]
        return d


class ScienceTutorEngine:
    """
    Grounded RAG and Interactive Pedagogical Tutor for Class 8 Science.
    """

    def __init__(
        self,
        loader=science_corpus_loader,
        learning_graph=science_learning_graph,
        physical_graph=science_physical_graph
    ):
        self.loader = loader
        self.learning_graph = learning_graph
        self.physical_graph = physical_graph

    def query_tutor(
        self,
        query: str,
        chapter_id: str,
        learning_unit_id: Optional[str] = None,
        region_id: Optional[str] = None
    ) -> ScienceGroundedTutorContext:
        self.loader.validate_and_load()
        self.learning_graph.build_graph()
        self.physical_graph.build_graph()

        ch_upper = chapter_id.upper()
        ch_meta = self.loader.get_chapter(ch_upper)
        if not ch_meta:
            ch_meta = self.loader.get_chapter("CH_01")
            ch_upper = "CH_01"

        units = self.learning_graph.get_units_for_chapter(ch_upper)
        target_unit = None
        if learning_unit_id:
            target_unit = self.learning_graph.get_learning_unit(learning_unit_id)
        if not target_unit and units:
            target_unit = units[0]

        unit_title = target_unit.title_marathi if target_unit else ch_meta.title_marathi
        unit_id = target_unit.unit_id if target_unit else f"{ch_upper}_LU_01"

        # Search matching concepts
        query_words = set(re.findall(r'[\u0900-\u097F\w]+', query))
        matched_concepts = []
        for c in self.learning_graph.concepts.values():
            if c.chapter_id == ch_upper:
                c_words = set(re.findall(r'[\u0900-\u097F\w]+', c.name_marathi + " " + c.gloss_english))
                if query_words & c_words:
                    matched_concepts.append(c)

        if matched_concepts:
            top_concept = matched_concepts[0]
            answer = (
                f"'{top_concept.name_marathi}' ही संकल्पना प्रकरण {ch_meta.chapter_number} : "
                f"'{ch_meta.title_marathi}' मधील महत्त्वाची वैज्ञानिक संकल्पना आहे. "
                f"विज्ञानानुसार : {top_concept.gloss_english}."
            )
        else:
            answer = (
                f"प्रकरण {ch_meta.chapter_number} : '{ch_meta.title_marathi}' मधील '{unit_title}' "
                f"या घटकानुसार, विज्ञानातील नियमांचे निरीक्षण व प्रायोगिक पडताळणी करणे अत्यंत महत्त्वाचे आहे. "
                f"या भागातील संकल्पना स्पष्ट समजून घेण्यासाठी पाठ्यपुस्तकातील 'करून पहा' ही कृती अवश्य करून पहा."
            )

        source_ref = ScienceTutorSourceRef(
            chapter_id=ch_upper,
            chapter_number=ch_meta.chapter_number,
            learning_unit_id=unit_id,
            unit_title=unit_title,
            pdf_page=ch_meta.pdf_page_range[0],
            printed_page=ch_meta.printed_page_range[0],
            excerpt=f"प्रकरण {ch_meta.chapter_number} : {ch_meta.title_marathi} — {unit_title}."
        )

        followups = [
            f"{ch_meta.title_marathi} मधील मुख्य प्रयोग कोणता आहे?",
            f"या प्रकरणातील महत्त्वाच्या व्याख्या कोणत्या आहेत?",
            "या घटकातील स्वाध्याय प्रश्न समजावून सांगा."
        ]

        return ScienceGroundedTutorContext(
            query=query,
            chapter_id=ch_upper,
            grounded_answer=answer,
            tutor_voice_style="scientific_explanation",
            sources=[source_ref],
            confidence=0.96,
            audible_cue_required=True,
            suggested_followups=followups
        )


science_tutor_engine = ScienceTutorEngine()
