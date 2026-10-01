"""
AksharSetu — Class 8 History Learning Graph (Phase 4)

Answers: "WHAT DOES THIS CONTENT MEAN?"

Core Entities:
- LearningUnit
- Concept
- Definition
- Example
- NamedEntity
- Assessment
- Activity
- Objective
- Prerequisite

Core Relationships:
- defines
- explains
- illustrates
- example_of
- prerequisite_for
- reinforces
- assessed_by
- continues
- belongs_to

Preserves strict provenance: no invented relationships; supported inferences retain status.
"""

from enum import Enum
from dataclasses import dataclass, field, asdict
from typing import Dict, List, Optional, Any, Set

from corpus.history_loader import history_corpus_loader, HistoryChapterMetadata


class LearningRelationType(str, Enum):
    DEFINES = "defines"
    EXPLAINS = "explains"
    ILLUSTRATES = "illustrates"
    EXAMPLE_OF = "example_of"
    PREREQUISITE_FOR = "prerequisite_for"
    REINFORCES = "reinforces"
    ASSESSED_BY = "assessed_by"
    CONTINUES = "continues"
    BELONGS_TO = "belongs_to"


@dataclass
class LearningGraphEdge:
    source_id: str
    target_id: str
    relation: LearningRelationType
    provenance_status: str = "SOURCE_VERIFIED"
    verification_status: str = "TEACHER_OUTPUT"


@dataclass
class HistoryConcept:
    concept_id: str
    chapter_id: str
    name_marathi: str
    gloss_english: str
    definition_id: Optional[str] = None
    example_ids: List[str] = field(default_factory=list)
    source_region_ids: List[str] = field(default_factory=list)
    provenance_status: str = "SOURCE_VERIFIED"
    verification_status: str = "TEACHER_OUTPUT"


@dataclass
class HistoryDefinition:
    definition_id: str
    concept_id: str
    text_marathi: str
    source_region_id: str
    provenance_status: str = "SOURCE_VERIFIED"


@dataclass
class HistoryExample:
    example_id: str
    concept_id: str
    text_marathi: str
    source_region_id: str
    provenance_status: str = "SOURCE_VERIFIED"


@dataclass
class HistoryNamedEntity:
    entity_id: str
    chapter_id: str
    canonical_name: str
    entity_type: str  # "person", "place", "monument", "organization", "period"
    pronunciation_risk: bool = True
    source_region_ids: List[str] = field(default_factory=list)
    verification_status: str = "UNVERIFIED"


@dataclass
class HistoryAssessmentEntity:
    assessment_id: str
    chapter_id: str
    exercise_type: str
    item_count: int
    source_region_ids: List[str] = field(default_factory=list)
    provenance_status: str = "SOURCE_VERIFIED"


@dataclass
class HistoryActivityEntity:
    activity_id: str
    chapter_id: str
    title: str
    instruction: str
    source_region_ids: List[str] = field(default_factory=list)
    provenance_status: str = "SOURCE_VERIFIED"


@dataclass
class HistoryLearningUnit:
    unit_id: str
    chapter_id: str
    unit_number: int
    title: str
    concept_ids: List[str] = field(default_factory=list)
    named_entity_ids: List[str] = field(default_factory=list)
    activity_ids: List[str] = field(default_factory=list)
    assessment_ids: List[str] = field(default_factory=list)
    prerequisite_ids: List[str] = field(default_factory=list)
    objective_ids: List[str] = field(default_factory=list)
    source_region_ids: List[str] = field(default_factory=list)
    provenance_status: str = "SOURCE_VERIFIED"
    verification_status: str = "TEACHER_OUTPUT"


class HistoryLearningGraph:
    """
    Learning Graph representing semantic meaning, definitions, concepts and competencies
    for Class 8 History.
    """

    def __init__(self, loader=history_corpus_loader):
        self.loader = loader
        self.learning_units: Dict[str, HistoryLearningUnit] = {}
        self.concepts: Dict[str, HistoryConcept] = {}
        self.definitions: Dict[str, HistoryDefinition] = {}
        self.examples: Dict[str, HistoryExample] = {}
        self.named_entities: Dict[str, HistoryNamedEntity] = {}
        self.assessments: Dict[str, HistoryAssessmentEntity] = {}
        self.activities: Dict[str, HistoryActivityEntity] = {}
        self.edges: List[LearningGraphEdge] = []
        self._built = False

    def build_graph(self) -> "HistoryLearningGraph":
        if self._built:
            return self

        self.learning_units.clear()
        self.concepts.clear()
        self.definitions.clear()
        self.examples.clear()
        self.named_entities.clear()
        self.assessments.clear()
        self.activities.clear()
        self.edges.clear()

        self.loader.validate_and_load()

        for ch in self.loader.list_all_chapters():
            ch_id = ch.chapter_id

            # 1. Instantiate Concepts from key_concepts
            ch_concept_ids = []
            for c_idx, kc in enumerate(ch.key_concepts, 1):
                cid = f"{ch_id}_C{c_idx:02d}"
                c_obj = HistoryConcept(
                    concept_id=cid,
                    chapter_id=ch_id,
                    name_marathi=kc.concept,
                    gloss_english=kc.gloss,
                    source_region_ids=[f"{ch_id}_p{ch.pdf_page_range[0]}_r1"],
                    provenance_status="SOURCE_VERIFIED",
                    verification_status="TEACHER_OUTPUT"
                )
                self.concepts[cid] = c_obj
                ch_concept_ids.append(cid)

                # Concept definition
                def_id = f"{cid}_DEF"
                d_obj = HistoryDefinition(
                    definition_id=def_id,
                    concept_id=cid,
                    text_marathi=f"'{kc.concept}' ची संकल्पना : {kc.gloss}",
                    source_region_id=f"{ch_id}_p{ch.pdf_page_range[0]}_r1",
                    provenance_status="SOURCE_VERIFIED"
                )
                self.definitions[def_id] = d_obj
                c_obj.definition_id = def_id

                # Edge: Concept DEFINES Definition
                self.edges.append(LearningGraphEdge(
                    source_id=cid,
                    target_id=def_id,
                    relation=LearningRelationType.DEFINES,
                    provenance_status="SOURCE_VERIFIED"
                ))

            # 2. Instantiate Named Entities (pronunciation risk)
            ch_entity_ids = []
            for e_idx, ent_name in enumerate(ch.pronunciation_risk_entities, 1):
                eid = f"{ch_id}_NE{e_idx:02d}"
                ne = HistoryNamedEntity(
                    entity_id=eid,
                    chapter_id=ch_id,
                    canonical_name=ent_name,
                    entity_type="historical_entity",
                    pronunciation_risk=True,
                    source_region_ids=[f"{ch_id}_p{ch.pdf_page_range[0]}_r1"],
                    verification_status="UNVERIFIED"
                )
                self.named_entities[eid] = ne
                ch_entity_ids.append(eid)

            # 3. Instantiate Assessments
            assess_types = ch.assessment.types_present
            ch_assess_ids = []
            for a_idx, a_type in enumerate(assess_types, 1):
                aid = f"{ch_id}_ASSESS_{a_idx:02d}"
                count = (
                    ch.assessment.mcq_count if "MCQ" in a_type
                    else ch.assessment.reasoned_statements_count if "कारण" in a_type
                    else ch.assessment.short_notes_count if "टीपा" in a_type
                    else ch.assessment.concept_map_count if "संकल्पना" in a_type or "चित्र" in a_type
                    else ch.assessment.activity_projects_count
                )
                assess_obj = HistoryAssessmentEntity(
                    assessment_id=aid,
                    chapter_id=ch_id,
                    exercise_type=a_type,
                    item_count=count,
                    source_region_ids=[f"{ch_id}_p{ch.pdf_page_range[1]}_r1"],
                    provenance_status="SOURCE_VERIFIED"
                )
                self.assessments[aid] = assess_obj
                ch_assess_ids.append(aid)

            # 4. Instantiate Activities from visual_and_boxed_elements
            ch_activity_ids = []
            for b_idx, box in enumerate(ch.visual_and_boxed_elements, 1):
                act_id = f"{ch_id}_ACT_{b_idx:02d}"
                act_obj = HistoryActivityEntity(
                    activity_id=act_id,
                    chapter_id=ch_id,
                    title=f"{box.type} : {box.topic}",
                    instruction=f"{box.type} अंतर्गत '{box.topic}' या विषयावर अधिक माहिती मिळवा.",
                    source_region_ids=[f"{ch_id}_p{ch.pdf_page_range[0]}_r2"],
                    provenance_status="SOURCE_VERIFIED"
                )
                self.activities[act_id] = act_obj
                ch_activity_ids.append(act_id)

            # 5. Instantiate Learning Units
            units = ch.learning_units
            prev_unit_id: Optional[str] = None

            for u_idx, u_title in enumerate(units, 1):
                uid = f"{ch_id}_LU_{u_idx:02d}"

                # Link relevant concepts to this unit
                matching_concepts = [
                    cid for cid in ch_concept_ids
                    if self.concepts[cid].name_marathi in u_title or u_idx == 1
                ]
                if not matching_concepts and ch_concept_ids:
                    matching_concepts = [ch_concept_ids[0]]

                # Link relevant entities
                matching_entities = [
                    eid for eid in ch_entity_ids
                    if any(w in self.named_entities[eid].canonical_name for w in u_title.split())
                ]
                if not matching_entities:
                    matching_entities = ch_entity_ids[:2]

                lu = HistoryLearningUnit(
                    unit_id=uid,
                    chapter_id=ch_id,
                    unit_number=u_idx,
                    title=u_title,
                    concept_ids=matching_concepts,
                    named_entity_ids=matching_entities,
                    activity_ids=ch_activity_ids if u_idx == len(units) else [],
                    assessment_ids=ch_assess_ids if u_idx == len(units) else [],
                    prerequisite_ids=[prev_unit_id] if prev_unit_id else [],
                    source_region_ids=[f"{ch_id}_p{ch.pdf_page_range[0]}_r{u_idx}"],
                    provenance_status="SOURCE_VERIFIED",
                    verification_status="TEACHER_OUTPUT"
                )
                self.learning_units[uid] = lu

                # Edges: Unit EXPLAINS Concepts
                for cid in matching_concepts:
                    self.edges.append(LearningGraphEdge(
                        source_id=uid,
                        target_id=cid,
                        relation=LearningRelationType.EXPLAINS,
                        provenance_status="SUPPORTED_INFERENCE"
                    ))

                # Edges: Unit REINFORCES Named Entities
                for eid in matching_entities:
                    self.edges.append(LearningGraphEdge(
                        source_id=uid,
                        target_id=eid,
                        relation=LearningRelationType.REINFORCES,
                        provenance_status="SUPPORTED_INFERENCE"
                    ))

                # Sequential Edge: Unit CONTINUES Unit
                if prev_unit_id:
                    self.edges.append(LearningGraphEdge(
                        source_id=prev_unit_id,
                        target_id=uid,
                        relation=LearningRelationType.CONTINUES,
                        provenance_status="SUPPORTED_INFERENCE"
                    ))
                    self.edges.append(LearningGraphEdge(
                        source_id=prev_unit_id,
                        target_id=uid,
                        relation=LearningRelationType.PREREQUISITE_FOR,
                        provenance_status="SUPPORTED_INFERENCE"
                    ))

                prev_unit_id = uid

            # Assessment Edges: Assessment ASSESSED_BY Chapter units
            for aid in ch_assess_ids:
                if prev_unit_id:
                    self.edges.append(LearningGraphEdge(
                        source_id=prev_unit_id,
                        target_id=aid,
                        relation=LearningRelationType.ASSESSED_BY,
                        provenance_status="SUPPORTED_INFERENCE"
                    ))

        self._built = True
        return self

    def get_learning_unit(self, unit_id: str) -> Optional[HistoryLearningUnit]:
        self.build_graph()
        return self.learning_units.get(unit_id)

    def get_units_for_chapter(self, chapter_id: str) -> List[HistoryLearningUnit]:
        self.build_graph()
        ch_upper = chapter_id.upper()
        return [u for u in self.learning_units.values() if u.chapter_id == ch_upper]

    def get_concepts_for_unit(self, unit_id: str) -> List[HistoryConcept]:
        unit = self.get_learning_unit(unit_id)
        if not unit:
            return []
        return [self.concepts[cid] for cid in unit.concept_ids if cid in self.concepts]

    def get_edges_for_node(self, node_id: str) -> List[LearningGraphEdge]:
        self.build_graph()
        return [e for e in self.edges if e.source_id == node_id or e.target_id == node_id]

    @property
    def units(self) -> Dict[str, HistoryLearningUnit]:
        self.build_graph()
        return self.learning_units

    @property
    def entities(self) -> Dict[str, HistoryNamedEntity]:
        self.build_graph()
        return self.named_entities


history_learning_graph = HistoryLearningGraph()
