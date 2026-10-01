"""
AksharSetu — Learning Graph (§3.2 of Implementation Guide)
Answers: "What does it mean?"
Hierarchy: Chapters -> Lessons -> Learning Units (concepts, examples, figures) + vocabulary + activities.
Relationship types: continues, explains, illustrates, defines, contrasts_with, asks_about, belongs_to, summarizes, precedes, follows.

INVARIANT ENFORCED:
Every physical region in the Golden Corpus must link to a semantic entity, which links to a learning unit.
A validator method `validate_region_learning_chain` asserts this.
"""

from enum import Enum
from dataclasses import dataclass, field, asdict
from typing import List, Dict, Optional, Any, Set

class SemanticRelationType(str, Enum):
    CONTINUES = "continues"
    EXPLAINS = "explains"
    ILLUSTRATES = "illustrates"
    DEFINES = "defines"
    CONTRASTS_WITH = "contrasts_with"
    ASKS_ABOUT = "asks_about"
    BELONGS_TO = "belongs_to"
    SUMMARIZES = "summarizes"
    PRECEDES = "precedes"
    FOLLOWS = "follows"

@dataclass
class SemanticEntity:
    entity_id: str
    physical_region_id: str # Link back to physical document graph
    title: str
    concepts: List[str] = field(default_factory=list)
    vocabulary: List[Dict[str, str]] = field(default_factory=list) # e.g. [{"word": "टेकडी", "meaning": "लहान डोंगर"}]
    pedagogical_summary: str = ""

@dataclass
class LearningUnit:
    unit_id: str
    title: str
    chapter_id: str
    lesson_id: str
    entity_ids: List[str] = field(default_factory=list)
    key_takeaways: List[str] = field(default_factory=list)

@dataclass
class LearningGraphEdge:
    source_entity_id: str
    target_entity_id: str
    relation: SemanticRelationType

@dataclass
class LearningGraph:
    graph_id: str
    learning_units: Dict[str, LearningUnit] = field(default_factory=dict)
    semantic_entities: Dict[str, SemanticEntity] = field(default_factory=dict)
    edges: List[LearningGraphEdge] = field(default_factory=list)

    def add_learning_unit(self, unit: LearningUnit) -> None:
        self.learning_units[unit.unit_id] = unit

    def add_semantic_entity(self, entity: SemanticEntity, unit_id: str) -> None:
        if unit_id not in self.learning_units:
            raise KeyError(f"LearningUnit {unit_id} not found")
        self.semantic_entities[entity.entity_id] = entity
        if entity.entity_id not in self.learning_units[unit_id].entity_ids:
            self.learning_units[unit_id].entity_ids.append(entity.entity_id)

    def add_edge(self, source_id: str, target_id: str, relation: SemanticRelationType) -> None:
        self.edges.append(LearningGraphEdge(
            source_entity_id=source_id,
            target_entity_id=target_id,
            relation=relation
        ))

    def validate_region_learning_chain(self, physical_region_ids: List[str]) -> bool:
        """
        ARCHITECTURAL INVARIANT (§3.2):
        Every physical region must link to a semantic entity, which links to a learning unit.
        Fails if any region has no unbroken link.
        """
        # Map physical_region_id -> semantic_entity_id
        region_to_entity = {e.physical_region_id: e.entity_id for e in self.semantic_entities.values()}
        
        # Map semantic_entity_id -> unit_id
        entity_to_unit: Dict[str, str] = {}
        for uid, unit in self.learning_units.items():
            for eid in unit.entity_ids:
                entity_to_unit[eid] = uid

        for rid in physical_region_ids:
            if rid not in region_to_entity:
                raise ValueError(f"Invariant Violation: Physical region '{rid}' is not linked to any Semantic Entity.")
            eid = region_to_entity[rid]
            if eid not in entity_to_unit:
                raise ValueError(f"Invariant Violation: Semantic Entity '{eid}' (for region '{rid}') is not linked to any Learning Unit.")
        
        return True

    def to_dict(self) -> Dict[str, Any]:
        return {
            "graph_id": self.graph_id,
            "learning_units": {k: asdict(v) for k, v in self.learning_units.items()},
            "semantic_entities": {k: asdict(v) for k, v in self.semantic_entities.items()},
            "edges": [{"source": e.source_entity_id, "target": e.target_entity_id, "relation": e.relation.value} for e in self.edges]
        }
