"""
AksharSetu — Contextual Knowledge & RAG Engine (§6)

Contextual knowledge layer for grounded teacher tutoring.
DOES NOT determine raw PDF reading order.
Retrieves rich pedagogical context:
- current semantic block / paragraph
- surrounding narrative context (previous & next paragraphs)
- current learning unit and key concepts
- attached figures, maps, and captions
- vocabulary definitions and glossary items
- approved pronunciation rules
- verified teacher pedagogical notes
"""

from typing import Dict, List, Optional, Any
from dataclasses import dataclass, field, asdict

from graphs.semantic_blocks import SemanticNarrationBlock, SupportingMaterial
from graphs.learning_graph import LearningGraph
from corpus.pronunciation_kb import pronunciation_kb, PronunciationEntry

@dataclass
class RetrievedContextSource:
    source_type: str # "canonical_paragraph" | "figure" | "definition" | "learning_unit" | "pronunciation" | "teaching_graph_node"
    document_id: str
    chapter_id: str
    page_id: str
    pdf_page: int
    region_id: str
    learning_unit_id: str
    content: str
    relevance_score: float = 1.0
    metadata: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)

@dataclass
class AssembledRAGContext:
    query: str
    document_id: str
    chapter_id: str
    active_block_id: str
    active_learning_unit_id: str
    current_paragraph: Optional[str] = None
    previous_context: Optional[str] = None
    next_context: Optional[str] = None
    supporting_visuals: List[Dict[str, Any]] = field(default_factory=list)
    definitions: List[Dict[str, Any]] = field(default_factory=list)
    pronunciation_guides: List[Dict[str, Any]] = field(default_factory=list)
    retrieved_sources: List[RetrievedContextSource] = field(default_factory=list)
    pedagogical_context: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        d = asdict(self)
        d["retrieved_sources"] = [s.to_dict() for s in self.retrieved_sources]
        return d

class RAGContextEngine:
    """
    Retrieves grounded educational context for Student/Tutor interactions.
    Guarantees every retrieved piece of evidence preserves exact provenance.
    """
    def __init__(self, learning_graph: Optional[LearningGraph] = None):
        self.learning_graph = learning_graph

    def assemble_context(
        self,
        query: str,
        document_id: str,
        chapter_id: str,
        current_block: Optional[SemanticNarrationBlock] = None,
        previous_block: Optional[SemanticNarrationBlock] = None,
        next_block: Optional[SemanticNarrationBlock] = None,
        all_blocks_in_chapter: Optional[List[SemanticNarrationBlock]] = None
    ) -> AssembledRAGContext:
        blocks = all_blocks_in_chapter or []
        retrieved_sources: List[RetrievedContextSource] = []
        supporting_visuals: List[Dict[str, Any]] = []
        definitions: List[Dict[str, Any]] = []
        pronunciations: List[Dict[str, Any]] = []

        cur_text = current_block.canonical_text if current_block else ""
        cur_unit = current_block.learning_unit_id if current_block else "main"
        cur_page = current_block.pdf_page if current_block else 12
        cur_id = current_block.block_id if current_block else ""

        # 1. Current Block Source
        if current_block:
            retrieved_sources.append(RetrievedContextSource(
                source_type="canonical_paragraph",
                document_id=document_id,
                chapter_id=chapter_id,
                page_id=current_block.page_id,
                pdf_page=current_block.pdf_page,
                region_id=current_block.source_region_ids[0] if current_block.source_region_ids else current_block.block_id,
                learning_unit_id=current_block.learning_unit_id,
                content=current_block.canonical_text,
                relevance_score=1.0,
                metadata={"block_type": current_block.block_type.value}
            ))

            # Attached visuals
            for vis in current_block.supporting_visuals:
                supporting_visuals.append(vis.to_dict())
                retrieved_sources.append(RetrievedContextSource(
                    source_type="figure",
                    document_id=document_id,
                    chapter_id=chapter_id,
                    page_id=current_block.page_id,
                    pdf_page=current_block.pdf_page,
                    region_id=vis.material_id,
                    learning_unit_id=vis.supports_learning_unit_id or cur_unit,
                    content=f"[{vis.material_type.upper()}] {vis.title} : {vis.caption_text}",
                    relevance_score=0.95,
                    metadata={"explanation": vis.explanation}
                ))

        # 2. Narrative Continuity (Previous & Next Paragraphs)
        prev_text = previous_block.canonical_text if previous_block else None
        next_text = next_block.canonical_text if next_block else None

        if previous_block:
            retrieved_sources.append(RetrievedContextSource(
                source_type="canonical_paragraph",
                document_id=document_id,
                chapter_id=chapter_id,
                page_id=previous_block.page_id,
                pdf_page=previous_block.pdf_page,
                region_id=previous_block.block_id,
                learning_unit_id=previous_block.learning_unit_id,
                content=previous_block.canonical_text,
                relevance_score=0.85,
                metadata={"role": "previous_narrative_context"}
            ))

        # 3. Retrieve relevant visuals across chapter if query asks about map/image
        q_lower = query.lower()
        if any(w in q_lower for w in ("नकाशा", "map", "figure", "आकृती", "चित्र", "सिंहगड", "मार्ग")):
            for blk in blocks:
                for v in blk.supporting_visuals:
                    if v.material_id not in [s["material_id"] for s in supporting_visuals]:
                        supporting_visuals.append(v.to_dict())
                        retrieved_sources.append(RetrievedContextSource(
                            source_type="figure",
                            document_id=document_id,
                            chapter_id=chapter_id,
                            page_id=blk.page_id,
                            pdf_page=blk.pdf_page,
                            region_id=v.material_id,
                            learning_unit_id=v.supports_learning_unit_id or cur_unit,
                            content=f"{v.title}: {v.caption_text}. {v.explanation}",
                            relevance_score=0.92
                        ))

        # 4. Check for vocabulary definitions
        for blk in blocks:
            if blk.block_type.value == "definition":
                definitions.append({
                    "term": blk.canonical_text,
                    "unit": blk.learning_unit_id,
                    "pdf_page": blk.pdf_page
                })

        # 5. Retrieve approved pronunciation guides for words in current block
        if cur_text:
            for word in cur_text.split():
                clean_w = word.strip(",।?!.–—;:'\"")
                entry = pronunciation_kb.get_entries_for_word(clean_w)
                if entry and entry[0].approved:
                    pronunciations.append(entry[0].to_dict())

        # 6. Retrieve Chapter Pedagogical Blueprint & Teaching Graph (§13)
        pedagogical_context: Dict[str, Any] = {}
        try:
            from orchestrator.chapter_blueprint_engine import chapter_blueprint_engine
            blueprint = chapter_blueprint_engine.load_blueprint(document_id, chapter_id)
            if blueprint:
                # Objectives mapped to current unit or entire chapter if general query
                mapped_objs = [
                    obj.to_dict() for obj in blueprint.objectives
                    if not obj.mapped_learning_units or cur_unit in ("main", "all", "") or any(u in obj.mapped_learning_units for u in (cur_unit, "all"))
                ]
                connected_edges = [
                    e.to_dict() for e in blueprint.teaching_graph.edges
                    if e.source_id == cur_id or e.target_id == cur_id
                ]
                pedagogical_context = {
                    "genre": blueprint.genre.value,
                    "pedagogical_pattern": blueprint.pedagogical_pattern,
                    "learning_unit_id": cur_unit,
                    "mapped_objectives": mapped_objs,
                    "teaching_edges": connected_edges
                }
                for obj in mapped_objs:
                    retrieved_sources.append(RetrievedContextSource(
                        source_type="teaching_graph_node",
                        document_id=document_id,
                        chapter_id=chapter_id,
                        page_id="",
                        pdf_page=cur_page,
                        region_id=obj["objective_id"],
                        learning_unit_id=cur_unit,
                        content=f"अध्यापन उद्दिष्ट: {obj['title']} - {obj['description']}",
                        relevance_score=0.98,
                        metadata={"bloom_level": obj["bloom_level"], "pedagogical_role": "objective"}
                    ))
        except Exception as e:
            pedagogical_context = {"error": str(e)}

        return AssembledRAGContext(
            query=query,
            document_id=document_id,
            chapter_id=chapter_id,
            active_block_id=cur_id,
            active_learning_unit_id=cur_unit,
            current_paragraph=cur_text,
            previous_context=prev_text,
            next_context=next_text,
            supporting_visuals=supporting_visuals,
            definitions=definitions,
            pronunciation_guides=pronunciations,
            retrieved_sources=retrieved_sources,
            pedagogical_context=pedagogical_context
        )

rag_engine = RAGContextEngine()
