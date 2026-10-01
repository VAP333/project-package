# -*- coding: utf-8 -*-
"""
AksharSetu — Chapter-Level Pedagogical Blueprint & Teaching Graph (§0 - §20)

Represents:
1. CHAPTER PEDAGOGICAL BLUEPRINT (Pedagogical pattern, learning outcomes, recommended sequence)
2. CHAPTER TEACHING GRAPH (Semantic meaning, prerequisite chains, supporting relationships)
3. AUDIENCE & CONTENT PRIORITY CLASSIFICATION (Student vs Teacher-only, essential vs never-spoken)
4. ACCESSIBILITY POLICIES (Blind/Low-vision description, non-interrupting visual policies)
5. STRICT PHYSICAL VS TEACHING GRAPH SEPARATION:
   Physical Graph answers: "Where is this in the document?"
   Teaching Graph answers: "Why is this here and how should it be taught?"
"""

from enum import Enum
from dataclasses import dataclass, field, asdict
from typing import List, Dict, Optional, Any, Set

class AudienceType(str, Enum):
    STUDENT = "STUDENT"
    TEACHER = "TEACHER"
    BOTH = "BOTH"
    REFERENCE = "REFERENCE"
    NON_SPOKEN = "NON_SPOKEN"

class StudentRelevance(str, Enum):
    ESSENTIAL = "essential"
    USEFUL = "useful"
    OPTIONAL = "optional"
    TEACHER_ONLY = "teacher_only"
    NON_RELEVANT = "non_relevant"

class SpokenPriority(str, Enum):
    IMMEDIATE = "immediate"
    LATER = "later"
    ON_DEMAND = "on_demand"
    NEVER = "never"

class PedagogicalRole(str, Enum):
    INTRODUCTION = "introduction"
    CONCEPT = "concept"
    EXPLANATION = "explanation"
    DEFINITION = "definition"
    EXAMPLE = "example"
    ILLUSTRATION = "illustration"
    EVIDENCE = "evidence"
    DIALOGUE = "dialogue"
    ACTIVITY = "activity"
    REFLECTION = "reflection"
    EXERCISE = "exercise"
    RECAP = "recap"
    ASSESSMENT = "assessment"
    TEACHER_INSTRUCTION = "teacher_instruction"
    SUPPLEMENTARY = "supplementary"
    REFERENCE = "reference"

class GenreType(str, Enum):
    POEM = "poem"
    STORY = "story"
    PROSE = "prose"
    GEOGRAPHY = "geography"
    SCIENCE = "science"
    HISTORY = "history"
    MATHEMATICS = "mathematics"
    GRAMMAR = "grammar"
    ACTIVITY = "activity"
    EXERCISE = "exercise"
    REFERENCE = "reference"

class SemanticTeachingRelation(str, Enum):
    EXPLAINS = "explains"
    ILLUSTRATES = "illustrates"
    SUPPORTS = "supports"
    DEFINES = "defines"
    DEMONSTRATES = "demonstrates"
    CONTINUES = "continues"
    PREREQUISITE_FOR = "prerequisite_for"
    FOLLOWS = "follows"
    CHECKS_UNDERSTANDING_OF = "checks_understanding_of"
    BELONGS_TO = "belongs_to"
    CAPTION_FOR = "caption_for"
    RELATED_TO = "related_to"
    CONTRASTS_WITH = "contrasts_with"
    SUMMARIZES = "summarizes"
    APPLIES = "applies"
    EXPANDS = "expands"
    REINFORCES = "reinforces"

class TeachingNodeType(str, Enum):
    CHAPTER = "chapter"
    LEARNING_UNIT = "learning_unit"
    CONCEPT = "concept"
    PARAGRAPH = "paragraph"
    DIALOGUE = "dialogue"
    FIGURE = "figure"
    MAP = "map"
    CAPTION = "caption"
    DEFINITION = "definition"
    EXAMPLE = "example"
    ACTIVITY = "activity"
    QUESTION = "question"
    EXERCISE = "exercise"
    VOCABULARY = "vocabulary"
    OBJECTIVE = "objective"
    CHECKPOINT = "checkpoint"

@dataclass
class AccessibilityPolicy:
    spoken_automatically: bool = True
    available_on_demand: bool = True
    requires_visual_description: bool = False
    visual_description: Optional[str] = None
    tactile_spatial_notes: Optional[str] = None

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)

@dataclass
class TeachingNode:
    node_id: str
    node_type: TeachingNodeType
    title: str
    canonical_text: str
    region_id: Optional[str] = None # Provenance link to Physical Document Graph
    learning_unit_id: str = "main"
    audience: AudienceType = AudienceType.STUDENT
    student_relevance: StudentRelevance = StudentRelevance.ESSENTIAL
    spoken_priority: SpokenPriority = SpokenPriority.IMMEDIATE
    pedagogical_role: PedagogicalRole = PedagogicalRole.EXPLANATION
    accessibility: AccessibilityPolicy = field(default_factory=AccessibilityPolicy)
    metadata: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        d = asdict(self)
        d["node_type"] = self.node_type.value
        d["audience"] = self.audience.value
        d["student_relevance"] = self.student_relevance.value
        d["spoken_priority"] = self.spoken_priority.value
        d["pedagogical_role"] = self.pedagogical_role.value
        d["accessibility"] = self.accessibility.to_dict()
        return d

@dataclass
class TeachingEdge:
    source_id: str
    target_id: str
    relation: SemanticTeachingRelation
    weight: float = 1.0
    pedagogical_note: str = ""

    def to_dict(self) -> Dict[str, Any]:
        d = asdict(self)
        d["relation"] = self.relation.value
        return d

@dataclass
class SupportingVisualPolicy:
    visual_id: str
    concept_supported_id: str
    learning_unit_id: str
    is_essential: bool = False
    narration_behavior: str = "do_not_interrupt_narration" # "do_not_interrupt_narration" | "available_on_demand" | "auto_announce"
    accessibility_description: str = ""
    tactile_spatial_notes: Optional[str] = None

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)

@dataclass
class LearningObjective:
    objective_id: str
    title: str
    description: str
    bloom_level: str = "understand" # "recall" | "understand" | "apply" | "analyze" | "evaluate"
    mapped_learning_units: List[str] = field(default_factory=list)

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)

@dataclass
class TeachingTransition:
    transition_id: str
    from_node_id: str
    to_node_id: str
    grounded_speech: str # Spoken only in Tutor mode, never replaces canonical text
    role: str = "pedagogical_bridge" # "concept_to_visual" | "visual_to_explanation" | "explanation_to_activity"

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)

@dataclass
class ChapterTeachingGraph:
    graph_id: str
    nodes: Dict[str, TeachingNode] = field(default_factory=dict)
    edges: List[TeachingEdge] = field(default_factory=list)

    def add_node(self, node: TeachingNode) -> None:
        self.nodes[node.node_id] = node

    def add_edge(self, source_id: str, target_id: str, relation: SemanticTeachingRelation, note: str = "") -> None:
        self.edges.append(TeachingEdge(
            source_id=source_id,
            target_id=target_id,
            relation=relation,
            pedagogical_note=note
        ))

    def get_student_audible_nodes(self) -> List[TeachingNode]:
        """Returns nodes eligible for normal student textbook reading."""
        return [
            node for node in self.nodes.values()
            if node.audience in (AudienceType.STUDENT, AudienceType.BOTH)
            and node.spoken_priority in (SpokenPriority.IMMEDIATE, SpokenPriority.LATER)
        ]

    def get_teacher_only_nodes(self) -> List[TeachingNode]:
        """Returns classroom instructions and teacher-only guidance."""
        return [
            node for node in self.nodes.values()
            if node.audience == AudienceType.TEACHER
            or node.student_relevance == StudentRelevance.TEACHER_ONLY
            or node.spoken_priority == SpokenPriority.NEVER
        ]

    def to_dict(self) -> Dict[str, Any]:
        return {
            "graph_id": self.graph_id,
            "nodes": {nid: n.to_dict() for nid, n in self.nodes.items()},
            "edges": [e.to_dict() for e in self.edges]
        }

@dataclass
class ChapterPedagogicalBlueprint:
    blueprint_id: str
    document_id: str
    chapter_id: str
    chapter_title: str
    subject: str
    grade: int
    genre: GenreType
    pedagogical_pattern: str
    objectives: List[LearningObjective] = field(default_factory=list)
    learning_units: List[Dict[str, Any]] = field(default_factory=list)
    recommended_learning_sequence: List[str] = field(default_factory=list) # Ordered list of node_ids
    teaching_graph: ChapterTeachingGraph = field(default_factory=lambda: ChapterTeachingGraph("default_graph"))
    supporting_visuals: List[SupportingVisualPolicy] = field(default_factory=list)
    transitions: List[TeachingTransition] = field(default_factory=list)
    versioning: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "blueprint_id": self.blueprint_id,
            "document_id": self.document_id,
            "chapter_id": self.chapter_id,
            "chapter_title": self.chapter_title,
            "subject": self.subject,
            "grade": self.grade,
            "genre": self.genre.value,
            "pedagogical_pattern": self.pedagogical_pattern,
            "objectives": [o.to_dict() for o in self.objectives],
            "learning_units": self.learning_units,
            "recommended_learning_sequence": self.recommended_learning_sequence,
            "teaching_graph": self.teaching_graph.to_dict(),
            "supporting_visuals": [v.to_dict() for v in self.supporting_visuals],
            "transitions": [t.to_dict() for t in self.transitions],
            "versioning": self.versioning
        }
