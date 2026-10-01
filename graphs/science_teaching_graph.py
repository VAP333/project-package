"""
AksharSetu — Class 8 Science Teaching Graph (Phase 5)

Answers: "HOW SHOULD THIS CONTENT BE TAUGHT?"

STRICTLY SEPARATED from Learning Graph!
Distinguishes:
- TEXTBOOK_SUPPORTED_STRUCTURE (direct textbook headings, printed text, स्वाध्याय questions, करून पहा activities)
- AKSHARSETU_RECOMMENDATION (pedagogical order, conversational scaffolding, prompts, pacing)

Node Types:
- introduction
- explanation
- example
- reinforcement
- activity (करून पहा hands-on laboratory observation)
- assessment (स्वाध्याय)
- recap
- transition
"""

from enum import Enum
from dataclasses import dataclass, field, asdict
from typing import Dict, List, Optional, Any

from corpus.science_loader import science_corpus_loader, ScienceChapterMetadata


class ScienceTeachingNodeType(str, Enum):
    INTRODUCTION = "introduction"
    EXPLANATION = "explanation"
    EXAMPLE = "example"
    REINFORCEMENT = "reinforcement"
    ACTIVITY = "activity"
    ASSESSMENT = "assessment"
    RECAP = "recap"
    TRANSITION = "transition"


class ScienceTeachingOrigin(str, Enum):
    TEXTBOOK_SUPPORTED_STRUCTURE = "TEXTBOOK_SUPPORTED_STRUCTURE"
    AKSHARSETU_RECOMMENDATION = "AKSHARSETU_RECOMMENDATION"


@dataclass
class ScienceTeachingNode:
    node_id: str
    chapter_id: str
    unit_id: str
    teaching_order: int
    node_type: ScienceTeachingNodeType
    origin: ScienceTeachingOrigin
    text_content: str
    tutor_prompt: str
    pedagogical_intent: str
    narration_policy: str  # "READ_DIRECTLY", "READ_THEN_EXPLAIN", "EXPLAIN", "ON_DEMAND", "EXCLUDE_FROM_NORMAL_READING"
    speaking_style: str    # "scientific_explanation", "mathematical_narration", "procedural_instructional"
    source_region_ids: List[str] = field(default_factory=list)

    def to_dict(self) -> Dict[str, Any]:
        d = asdict(self)
        d["node_type"] = self.node_type.value
        d["origin"] = self.origin.value
        return d


class ScienceTeachingGraph:
    """
    Teaching Graph defining pedagogical progression, scaffolding,
    and instructional prompts for Class 8 Science.
    """

    def __init__(self, loader=science_corpus_loader):
        self.loader = loader
        self.nodes_by_chapter: Dict[str, List[ScienceTeachingNode]] = {}
        self.nodes_by_id: Dict[str, ScienceTeachingNode] = {}
        self._built = False

    def build_graph(self) -> "ScienceTeachingGraph":
        if self._built:
            return self

        self.loader.validate_and_load()

        for ch in self.loader.list_all_chapters():
            ch_id = ch.chapter_id
            order = 1
            ch_nodes: List[ScienceTeachingNode] = []

            # 1. INTRODUCTION: Framing Opener
            intro_node = ScienceTeachingNode(
                node_id=f"{ch_id}_TN_{order:02d}",
                chapter_id=ch_id,
                unit_id=f"{ch_id}_LU_01",
                teaching_order=order,
                node_type=ScienceTeachingNodeType.INTRODUCTION,
                origin=ScienceTeachingOrigin.AKSHARSETU_RECOMMENDATION,
                text_content=f"इयत्ता आठवी सामान्य विज्ञान, प्रकरण {ch.chapter_number} : {ch.title_marathi}.",
                tutor_prompt=f"विद्यार्थ्याला '{ch.title_marathi}' या प्रकरणातील वैज्ञानिक संकल्पनांची पूर्वकल्पना द्या.",
                pedagogical_intent="orient_student",
                narration_policy="READ_THEN_EXPLAIN",
                speaking_style=ch.speaking_style
            )
            ch_nodes.append(intro_node)
            self.nodes_by_id[intro_node.node_id] = intro_node
            order += 1

            # 2. RECALL & DISCUSSION (थोडे आठवा / सांगा पाहू)
            recall_node = ScienceTeachingNode(
                node_id=f"{ch_id}_TN_{order:02d}",
                chapter_id=ch_id,
                unit_id=f"{ch_id}_LU_01",
                teaching_order=order,
                node_type=ScienceTeachingNodeType.REINFORCEMENT,
                origin=ScienceTeachingOrigin.TEXTBOOK_SUPPORTED_STRUCTURE,
                text_content=f"थोडे आठवा : '{ch.title_marathi}' यासंबंधी आपण मागील इयत्तेत काय शिकलो ते आठवून पाहूया.",
                tutor_prompt="मागील वर्गातील पूर्वज्ञानावर आधारित प्रश्न विचारून विद्यार्थ्याला विचार प्रवृत्त करा.",
                pedagogical_intent="activate_prior_knowledge",
                narration_policy="READ_DIRECTLY",
                speaking_style="scientific_explanation"
            )
            ch_nodes.append(recall_node)
            self.nodes_by_id[recall_node.node_id] = recall_node
            order += 1

            # 3. CORE EXPLANATION: Learning Units
            for u_idx, u_title in enumerate(ch.learning_units, 1):
                u_id = f"{ch_id}_LU_{u_idx:02d}"
                exp_node = ScienceTeachingNode(
                    node_id=f"{ch_id}_TN_{order:02d}",
                    chapter_id=ch_id,
                    unit_id=u_id,
                    teaching_order=order,
                    node_type=ScienceTeachingNodeType.EXPLANATION,
                    origin=ScienceTeachingOrigin.TEXTBOOK_SUPPORTED_STRUCTURE,
                    text_content=f"घटक {u_idx} : {u_title}.",
                    tutor_prompt=f"विद्यार्थ्याला '{u_title}' ही वैज्ञानिक संकल्पना सोप्या उदाहरणांसह समजावून सांगा.",
                    pedagogical_intent="explain_concept",
                    narration_policy="READ_THEN_EXPLAIN",
                    speaking_style=ch.speaking_style
                )
                ch_nodes.append(exp_node)
                self.nodes_by_id[exp_node.node_id] = exp_node
                order += 1

                # 4. HANDS-ON ACTIVITY (करून पहा)
                if u_idx <= 2:
                    act_node = ScienceTeachingNode(
                        node_id=f"{ch_id}_TN_{order:02d}",
                        chapter_id=ch_id,
                        unit_id=u_id,
                        teaching_order=order,
                        node_type=ScienceTeachingNodeType.ACTIVITY,
                        origin=ScienceTeachingOrigin.TEXTBOOK_SUPPORTED_STRUCTURE,
                        text_content=f"करून पहा : {u_title} मधील प्रात्यक्षिक कृती पायरी-पायरीने करून निरीक्षण नोंदवा.",
                        tutor_prompt="कृती करताना लागणारे साहित्य आणि घ्यावयाची काळजी स्पष्ट करा.",
                        pedagogical_intent="hands_on_experimentation",
                        narration_policy="READ_DIRECTLY",
                        speaking_style="procedural_instructional"
                    )
                    ch_nodes.append(act_node)
                    self.nodes_by_id[act_node.node_id] = act_node
                    order += 1

            # 5. RECAP
            recap_node = ScienceTeachingNode(
                node_id=f"{ch_id}_TN_{order:02d}",
                chapter_id=ch_id,
                unit_id=f"{ch_id}_LU_01",
                teaching_order=order,
                node_type=ScienceTeachingNodeType.RECAP,
                origin=ScienceTeachingOrigin.AKSHARSETU_RECOMMENDATION,
                text_content=f"प्रकरण {ch.chapter_number} : '{ch.title_marathi}' मधील मुख्य निष्कर्षांची उजळणी करूया.",
                tutor_prompt="प्रकरणातील महत्त्वाच्या संज्ञा व नियमांचा सारांश द्या.",
                pedagogical_intent="consolidate_learning",
                narration_policy="READ_THEN_EXPLAIN",
                speaking_style="scientific_explanation"
            )
            ch_nodes.append(recap_node)
            self.nodes_by_id[recap_node.node_id] = recap_node
            order += 1

            # 6. ASSESSMENT (स्वाध्याय)
            assessment_node = ScienceTeachingNode(
                node_id=f"{ch_id}_TN_{order:02d}",
                chapter_id=ch_id,
                unit_id=f"{ch_id}_LU_01",
                teaching_order=order,
                node_type=ScienceTeachingNodeType.ASSESSMENT,
                origin=ScienceTeachingOrigin.TEXTBOOK_SUPPORTED_STRUCTURE,
                text_content=f"स्वाध्याय : {', '.join(ch.assessment.types_present[:3])} इत्यादी प्रश्नांचा सराव करा.",
                tutor_prompt="विद्यार्थ्याला स्वाध्यायातील प्रश्नांची उत्तरे स्वतः शोधण्यासाठी मार्गदर्शन करा.",
                pedagogical_intent="assess_understanding",
                narration_policy="READ_THEN_EXPLAIN",
                speaking_style="scientific_explanation"
            )
            ch_nodes.append(assessment_node)
            self.nodes_by_id[assessment_node.node_id] = assessment_node

            self.nodes_by_chapter[ch_id] = ch_nodes

        self._built = True
        return self

    def get_nodes_for_chapter(self, chapter_id: str) -> List[ScienceTeachingNode]:
        self.build_graph()
        return self.nodes_by_chapter.get(chapter_id.upper(), [])


science_teaching_graph = ScienceTeachingGraph()
