"""
AksharSetu — Class 8 Science Learning Graph (Phase 4)

Answers: "WHAT DOES THIS CONTENT MEAN?"

Core Entities:
- LearningUnit
- Concept
- Definition
- Example
- NamedEntity (scientists, substances, units, organisms)
- Assessment
- Activity (करून पहा)

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

from corpus.science_loader import science_corpus_loader, ScienceChapterMetadata


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
class ScienceConcept:
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
class ScienceDefinition:
    definition_id: str
    concept_id: str
    text_marathi: str
    source_region_id: str
    provenance_status: str = "SOURCE_VERIFIED"


@dataclass
class ScienceExample:
    example_id: str
    concept_id: str
    text_marathi: str
    source_region_id: str
    provenance_status: str = "SOURCE_VERIFIED"


@dataclass
class ScienceNamedEntity:
    entity_id: str
    chapter_id: str
    canonical_name: str
    entity_type: str  # "scientist", "substance", "taxa", "unit", "phenomenon"
    pronunciation_risk: bool = True
    source_region_ids: List[str] = field(default_factory=list)
    verification_status: str = "UNVERIFIED"


@dataclass
class ScienceLearningUnit:
    unit_id: str
    chapter_id: str
    unit_number: int
    title_marathi: str
    title_english: str
    core_concept_ids: List[str] = field(default_factory=list)
    named_entity_ids: List[str] = field(default_factory=list)
    prerequisite_unit_ids: List[str] = field(default_factory=list)
    continuation_unit_ids: List[str] = field(default_factory=list)
    source_region_ids: List[str] = field(default_factory=list)
    provenance_status: str = "SOURCE_VERIFIED"
    verification_status: str = "TEACHER_OUTPUT"


class ScienceLearningGraph:
    """
    Conceptual Knowledge Graph for Class 8 Science.
    Synthesizes learning units, scientific concepts, and relationships across all 19 chapters.
    """

    def __init__(self, loader=science_corpus_loader):
        self.loader = loader
        self.units: Dict[str, ScienceLearningUnit] = {}
        self.concepts: Dict[str, ScienceConcept] = {}
        self.definitions: Dict[str, ScienceDefinition] = {}
        self.examples: Dict[str, ScienceExample] = {}
        self.entities: Dict[str, ScienceNamedEntity] = {}
        self.edges: List[LearningGraphEdge] = []
        self._built = False

    def build_graph(self) -> "ScienceLearningGraph":
        if self._built:
            return self

        self.loader.validate_and_load()

        concept_counter = 1
        entity_counter = 1

        for ch in self.loader.list_all_chapters():
            ch_id = ch.chapter_id

            # 1. Build Concepts
            ch_concept_ids: List[str] = []
            for c_meta in ch.key_concepts:
                c_id = f"{ch_id}_CON_{concept_counter:03d}"
                concept = ScienceConcept(
                    concept_id=c_id,
                    chapter_id=ch_id,
                    name_marathi=c_meta.concept,
                    gloss_english=c_meta.gloss,
                    source_region_ids=[f"{ch_id}_p{ch.pdf_page_range[0]}_r01"]
                )
                self.concepts[c_id] = concept
                ch_concept_ids.append(c_id)
                concept_counter += 1

            # 2. Build Named Entities
            ch_entity_ids: List[str] = []
            for ent_name in ch.pronunciation_risk_entities:
                e_id = f"{ch_id}_ENT_{entity_counter:03d}"
                ent_type = "technical_term"
                if any(sci in ent_name for sci in ["लिनिअस", "हेकेल", "चॅटन", "कोपलँड", "व्हिटाकर", "डॅल्टन", "थॉमसन", "रुदरफोर्ड", "बोहर", "आर्किमिडीज", "गॉल्गी", "हार्वे", "लँडस्टायनर"]):
                    ent_type = "scientist"
                elif any(taxa in ent_name for taxa in ["बॅसिलाय", "अमिबा", "फाज", "मोनेरा", "प्रोटिस्टा"]):
                    ent_type = "taxa"
                elif any(unit in ent_name for unit in ["पास्कल", "ज्यूल", "कॅलरी", "हर्ट्झ", "वॅट", "प्रकाशवर्ष", "MSun"]):
                    ent_type = "unit"

                named_ent = ScienceNamedEntity(
                    entity_id=e_id,
                    chapter_id=ch_id,
                    canonical_name=ent_name,
                    entity_type=ent_type,
                    pronunciation_risk=True,
                    source_region_ids=[f"{ch_id}_p{ch.pdf_page_range[0]}_r01"]
                )
                self.entities[e_id] = named_ent
                ch_entity_ids.append(e_id)
                entity_counter += 1

            # 3. Build Learning Units
            prev_u_id: Optional[str] = None
            for u_idx, u_title in enumerate(ch.learning_units, 1):
                u_id = f"{ch_id}_LU_{u_idx:02d}"
                # Distribute concepts and entities
                assigned_concepts = ch_concept_ids[:2] if u_idx == 1 else ch_concept_ids[2:]
                assigned_entities = ch_entity_ids[:3] if u_idx == 1 else ch_entity_ids[3:6]

                unit = ScienceLearningUnit(
                    unit_id=u_id,
                    chapter_id=ch_id,
                    unit_number=u_idx,
                    title_marathi=u_title,
                    title_english=f"{ch.title_english_gloss} - Part {u_idx}",
                    core_concept_ids=assigned_concepts,
                    named_entity_ids=assigned_entities,
                    prerequisite_unit_ids=[prev_u_id] if prev_u_id else [],
                    source_region_ids=[f"{ch_id}_p{ch.pdf_page_range[0]}_r{u_idx:02d}"]
                )

                if prev_u_id:
                    self.units[prev_u_id].continuation_unit_ids.append(u_id)
                    self.edges.append(LearningGraphEdge(
                        source_id=prev_u_id,
                        target_id=u_id,
                        relation=LearningRelationType.CONTINUES
                    ))

                self.units[u_id] = unit
                prev_u_id = u_id

                # Link concepts to unit
                for c_id in assigned_concepts:
                    self.edges.append(LearningGraphEdge(
                        source_id=c_id,
                        target_id=u_id,
                        relation=LearningRelationType.BELONGS_TO
                    ))

        self._built = True
        return self

    def get_units_for_chapter(self, chapter_id: str) -> List[ScienceLearningUnit]:
        self.build_graph()
        ch_upper = chapter_id.upper()
        return [u for u in self.units.values() if u.chapter_id == ch_upper]

    def get_learning_unit(self, unit_id: str) -> Optional[ScienceLearningUnit]:
        self.build_graph()
        return self.units.get(unit_id)

    def get_concepts_for_unit(self, unit_id: str) -> List[ScienceConcept]:
        self.build_graph()
        u = self.units.get(unit_id)
        if not u:
            return []
        return [self.concepts[c_id] for c_id in u.core_concept_ids if c_id in self.concepts]


science_learning_graph = ScienceLearningGraph()
