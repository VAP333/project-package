"""
AksharSetu — Class 8 History Teaching Graph (Phase 5)

Answers: "HOW SHOULD THIS CONTENT BE TAUGHT?"

STRICTLY SEPARATED from Learning Graph!
Distinguishes:
- TEXTBOOK_SUPPORTED_STRUCTURE (direct textbook headings, printed text, स्वाध्याय questions)
- AKSHARSETU_RECOMMENDATION (pedagogical order, conversational scaffolding, prompts, pacing)

Node Types:
- introduction
- explanation
- example
- reinforcement
- activity
- assessment
- recap
- transition
"""

from enum import Enum
from dataclasses import dataclass, field, asdict
from typing import Dict, List, Optional, Any

from corpus.history_loader import history_corpus_loader, HistoryChapterMetadata


class TeachingNodeType(str, Enum):
    INTRODUCTION = "introduction"
    EXPLANATION = "explanation"
    EXAMPLE = "example"
    REINFORCEMENT = "reinforcement"
    ACTIVITY = "activity"
    ASSESSMENT = "assessment"
    RECAP = "recap"
    TRANSITION = "transition"


class TeachingOrigin(str, Enum):
    TEXTBOOK_SUPPORTED_STRUCTURE = "TEXTBOOK_SUPPORTED_STRUCTURE"
    AKSHARSETU_RECOMMENDATION = "AKSHARSETU_RECOMMENDATION"


@dataclass
class HistoryTeachingNode:
    node_id: str
    chapter_id: str
    unit_id: str
    teaching_order: int
    node_type: TeachingNodeType
    origin: TeachingOrigin
    text_content: str
    tutor_prompt: str
    pedagogical_intent: str
    narration_policy: str  # "READ_DIRECTLY", "READ_THEN_EXPLAIN", "EXPLAIN", "ON_DEMAND", "EXCLUDE_FROM_NORMAL_READING"
    speaking_style: str    # "historical_narration", "explanatory_teacher", "descriptive"
    source_region_ids: List[str] = field(default_factory=list)

    def to_dict(self) -> Dict[str, Any]:
        d = asdict(self)
        d["node_type"] = self.node_type.value
        d["origin"] = self.origin.value
        return d


class HistoryTeachingGraph:
    """
    Teaching Graph defining the pedagogical progression, scaffolding,
    and instructional prompts for Class 8 History.
    """

    def __init__(self, loader=history_corpus_loader):
        self.loader = loader
        self.nodes_by_chapter: Dict[str, List[HistoryTeachingNode]] = {}
        self.nodes_by_id: Dict[str, HistoryTeachingNode] = {}
        self._built = False

    def build_graph(self) -> "HistoryTeachingGraph":
        if self._built:
            return self

        self.loader.validate_and_load()

        for ch in self.loader.list_all_chapters():
            ch_id = ch.chapter_id
            order = 1
            ch_nodes: List[HistoryTeachingNode] = []

            # 1. INTRODUCTION: Framing Opener (Textbook title + AksharSetu orientation)
            intro_node = HistoryTeachingNode(
                node_id=f"{ch_id}_TN_{order:02d}",
                chapter_id=ch_id,
                unit_id=f"{ch_id}_LU_01",
                teaching_order=order,
                node_type=TeachingNodeType.INTRODUCTION,
                origin=TeachingOrigin.AKSHARSETU_RECOMMENDATION,
                text_content=f"इयत्ता आठवी इतिहास, प्रकरण {ch.chapter_number} : {ch.title_marathi}.",
                tutor_prompt=f"विद्यार्थ्याला '{ch.title_marathi}' या प्रकरणातील मुख्य ऐतिहासिक प्रवाहांची पूर्वकल्पना द्या.",
                pedagogical_intent="orient_student",
                narration_policy="READ_DIRECTLY",
                speaking_style=ch.speaking_style,
                source_region_ids=[f"{ch_id}_p{ch.pdf_page_range[0]}_r1"]
            )
            ch_nodes.append(intro_node)
            self.nodes_by_id[intro_node.node_id] = intro_node
            order += 1

            # 2. TRANSITION: Contextual bridging
            trans_node = HistoryTeachingNode(
                node_id=f"{ch_id}_TN_{order:02d}",
                chapter_id=ch_id,
                unit_id=f"{ch_id}_LU_01",
                teaching_order=order,
                node_type=TeachingNodeType.TRANSITION,
                origin=TeachingOrigin.AKSHARSETU_RECOMMENDATION,
                text_content=f"या ऐतिहासिक कालखंडाची पार्श्वभूमी समजून घेऊया.",
                tutor_prompt=f"या प्रकरणातील घटनांचा मागील प्रकरणाशी असलेला संबंध स्पष्ट करा.",
                pedagogical_intent="bridge_context",
                narration_policy="EXPLAIN",
                speaking_style="explanatory_teacher",
                source_region_ids=[f"{ch_id}_p{ch.pdf_page_range[0]}_r1"]
            )
            ch_nodes.append(trans_node)
            self.nodes_by_id[trans_node.node_id] = trans_node
            order += 1

            # 3. EXPLANATION & EXAMPLES for each Learning Unit
            for u_idx, u_title in enumerate(ch.learning_units, 1):
                unit_id = f"{ch_id}_LU_{u_idx:02d}"

                # Core Explanation (Textbook Content)
                exp_node = HistoryTeachingNode(
                    node_id=f"{ch_id}_TN_{order:02d}",
                    chapter_id=ch_id,
                    unit_id=unit_id,
                    teaching_order=order,
                    node_type=TeachingNodeType.EXPLANATION,
                    origin=TeachingOrigin.TEXTBOOK_SUPPORTED_STRUCTURE,
                    text_content=f"घटक : {u_title}",
                    tutor_prompt=f"विद्यार्थ्याला '{u_title}' या घटकाचा नेमका अर्थ आणि त्यातील ऐतिहासिक घटनाक्रम सांगा.",
                    pedagogical_intent="clarify_concept",
                    narration_policy=ch.narration_policy,
                    speaking_style=ch.speaking_style,
                    source_region_ids=[f"{ch_id}_p{ch.pdf_page_range[0]}_r{u_idx}"]
                )
                ch_nodes.append(exp_node)
                self.nodes_by_id[exp_node.node_id] = exp_node
                order += 1

                # Example / Historical Case Study if key concepts defined
                matching_concepts = [c for c in ch.key_concepts if c.concept in u_title]
                if matching_concepts:
                    ex_node = HistoryTeachingNode(
                        node_id=f"{ch_id}_TN_{order:02d}",
                        chapter_id=ch_id,
                        unit_id=unit_id,
                        teaching_order=order,
                        node_type=TeachingNodeType.EXAMPLE,
                        origin=TeachingOrigin.TEXTBOOK_SUPPORTED_STRUCTURE,
                        text_content=f"उदाहरणासह संकल्पना स्पष्टीकरण : {matching_concepts[0].concept} — {matching_concepts[0].gloss}",
                        tutor_prompt=f"'{matching_concepts[0].concept}' या संकल्पनेचे इतिहासातील उदाहरण देऊन महत्त्व स्पष्ट करा.",
                        pedagogical_intent="illustrate_with_example",
                        narration_policy="READ_THEN_EXPLAIN",
                        speaking_style="explanatory_teacher",
                        source_region_ids=[f"{ch_id}_p{ch.pdf_page_range[0]}_r{u_idx}"]
                    )
                    ch_nodes.append(ex_node)
                    self.nodes_by_id[ex_node.node_id] = ex_node
                    order += 1

            # 4. REINFORCEMENT: Boxed features & Enrichment
            for b_idx, box in enumerate(ch.visual_and_boxed_elements, 1):
                box_node = HistoryTeachingNode(
                    node_id=f"{ch_id}_TN_{order:02d}",
                    chapter_id=ch_id,
                    unit_id=f"{ch_id}_LU_01",
                    teaching_order=order,
                    node_type=TeachingNodeType.REINFORCEMENT,
                    origin=TeachingOrigin.TEXTBOOK_SUPPORTED_STRUCTURE,
                    text_content=f"{box.type} : {box.topic}",
                    tutor_prompt=f"या माहिती चौकटीतील माहितीवर आधारित प्रश्न विचारून विद्यार्थ्यांची जिज्ञासा वाढवा.",
                    pedagogical_intent="enrich_knowledge",
                    narration_policy=box.narration_policy,
                    speaking_style="explanatory_teacher",
                    source_region_ids=[f"{ch_id}_p{ch.pdf_page_range[0]}_r{order}"]
                )
                ch_nodes.append(box_node)
                self.nodes_by_id[box_node.node_id] = box_node
                order += 1

            # 5. RECAP: Synthesis
            recap_node = HistoryTeachingNode(
                node_id=f"{ch_id}_TN_{order:02d}",
                chapter_id=ch_id,
                unit_id=f"{ch_id}_LU_RECAP",
                teaching_order=order,
                node_type=TeachingNodeType.RECAP,
                origin=TeachingOrigin.AKSHARSETU_RECOMMENDATION,
                text_content=f"प्रकरण {ch.chapter_number} चा सारांश : {ch.title_marathi} मधील प्रमुख निष्पत्ती.",
                tutor_prompt="प्रकरणातील मुख्य शिकलेल्या मुद्द्यांची उजळणी करा.",
                pedagogical_intent="synthesize_learnings",
                narration_policy="EXPLAIN",
                speaking_style="explanatory_teacher",
                source_region_ids=[f"{ch_id}_p{ch.pdf_page_range[1]}_r1"]
            )
            ch_nodes.append(recap_node)
            self.nodes_by_id[recap_node.node_id] = recap_node
            order += 1

            # 6. ASSESSMENT: स्वाध्याय Review
            assess_node = HistoryTeachingNode(
                node_id=f"{ch_id}_TN_{order:02d}",
                chapter_id=ch_id,
                unit_id=f"{ch_id}_LU_ASSESS",
                teaching_order=order,
                node_type=TeachingNodeType.ASSESSMENT,
                origin=TeachingOrigin.TEXTBOOK_SUPPORTED_STRUCTURE,
                text_content=f"स्वाध्याय : {len(ch.assessment.types_present)} प्रकारचे प्रश्न उपलब्ध.",
                tutor_prompt="स्वाध्यायातील प्रश्नांवर सराव करा आणि मार्गदर्शन द्या.",
                pedagogical_intent="assess_understanding",
                narration_policy="EXCLUDE_FROM_NORMAL_READING",
                speaking_style="explanatory_teacher",
                source_region_ids=[f"{ch_id}_p{ch.pdf_page_range[1]}_r2"]
            )
            ch_nodes.append(assess_node)
            self.nodes_by_id[assess_node.node_id] = assess_node

            self.nodes_by_chapter[ch_id] = ch_nodes

        self._built = True
        return self

    def get_nodes_for_chapter(self, chapter_id: str) -> List[HistoryTeachingNode]:
        self.build_graph()
        return self.nodes_by_chapter.get(chapter_id.upper(), [])

    def get_node(self, node_id: str) -> Optional[HistoryTeachingNode]:
        self.build_graph()
        return self.nodes_by_id.get(node_id)


history_teaching_graph = HistoryTeachingGraph()
