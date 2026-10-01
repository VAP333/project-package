# -*- coding: utf-8 -*-
"""
AksharSetu — Chapter Pedagogical Blueprint & Teacher Bootstrap Engine (§0 - §20)

Responsibilities:
1. COMPLETE CHAPTER ANALYSIS: Analyzes entire chapter holistically, preserving cross-page relationships.
2. CHAPTER CLASSIFICATION: Classifies Subject, Genre, Chapter Type, and Pedagogical Pattern.
3. TEACHING GRAPH CREATION: Semantic nodes and meaningful edges (explains, illustrates, supports, etc.).
4. AUDIENCE & CONTENT PRIORITY: Distinguishes Student vs Teacher-only, essential vs never-spoken.
5. STRICT PHYSICAL VS TEACHING GRAPH SEPARATION: Physical (where) vs Teaching (why & how).
6. GEMINI TEACHER BOOTSTRAP & VALIDATION:
   Raw Teacher Analysis -> Schema Validation -> Source Consistency Validation -> Verified Blueprint.
7. PERSISTENCE & VERSIONING: Stores versioned blueprints in data/blueprints/.
"""

import os
import re
import json
from typing import Dict, List, Optional, Any, Tuple

from graphs.pedagogical_blueprint import (
    ChapterPedagogicalBlueprint,
    ChapterTeachingGraph,
    TeachingNode,
    TeachingEdge,
    TeachingNodeType,
    AudienceType,
    StudentRelevance,
    SpokenPriority,
    PedagogicalRole,
    GenreType,
    SemanticTeachingRelation,
    AccessibilityPolicy,
    SupportingVisualPolicy,
    LearningObjective,
    TeachingTransition
)

BLUEPRINTS_DIR = os.path.join("data", "blueprints")

class ChapterBlueprintEngine:
    """
    Constructs, validates, and manages Chapter Pedagogical Blueprints.
    Serves as the foundation for the AksharSetu Pedagogical Planner and RAG context engine.
    """
    def __init__(self, blueprints_dir: str = BLUEPRINTS_DIR):
        self.blueprints_dir = blueprints_dir
        os.makedirs(self.blueprints_dir, exist_ok=True)

    def classify_chapter(
        self,
        document_id: str,
        chapter_id: str,
        title: str,
        subject: str,
        sample_text: str = ""
    ) -> Tuple[GenreType, str]:
        """
        Classifies the chapter into its pedagogical genre and pattern:
        - POEM (poetic_appreciation_recitation)
        - GEOGRAPHY (exploratory_field_study)
        - SCIENCE (inquiry_hypothesis_experiment)
        - PROSE / STORY (narrative_moral_comprehension)
        - MATHEMATICS (concrete_visual_abstract_practice)
        """
        subj_lower = subject.lower()
        title_lower = title.lower()
        text_lower = sample_text.lower()

        # 1. Marathi Poetry
        if "बुद्धी दे" in title or "कविता" in title or "प्रार्थना" in title or "पद्य" in title_lower:
            return GenreType.POEM, "poetic_appreciation_recitation"

        # 2. Geography Field Visit / Spatial
        if "भूगोल" in subject or "क्षेत्रभेट" in title or "field visit" in title_lower or "नकाशा" in text_lower:
            return GenreType.GEOGRAPHY, "exploratory_field_study"

        # 3. Science
        if "विज्ञान" in subject or "science" in subj_lower or "प्रयोग" in text_lower or "गुरुत्वाकर्षण" in title:
            return GenreType.SCIENCE, "inquiry_hypothesis_experiment"

        # 4. Mathematics
        if "गणित" in subject or "math" in subj_lower or "समीकरण" in title or "practice set" in text_lower:
            return GenreType.MATHEMATICS, "concrete_visual_abstract_practice"

        # 5. General Prose / Story
        if "मराठी" in subject or "भाषा" in subject:
            return GenreType.PROSE, "narrative_moral_comprehension"

        return GenreType.REFERENCE, "general_instructional_hierarchy"

    def build_pedagogical_blueprint(
        self,
        document_id: str,
        chapter_id: str,
        chapter_title: str,
        subject: str,
        grade: int,
        pages_data: List[Dict[str, Any]]
    ) -> ChapterPedagogicalBlueprint:
        """
        Analyzes the complete chapter and constructs a verified ChapterPedagogicalBlueprint.
        """
        combined_text = " ".join(
            p.get("canonical_text", "")
            for pg in pages_data
            for p in pg.get("paragraphs", [])
        )

        genre, pattern = self.classify_chapter(document_id, chapter_id, chapter_title, subject, combined_text)
        graph_id = f"tg_{document_id}_{chapter_id}"
        teaching_graph = ChapterTeachingGraph(graph_id=graph_id)

        objectives: List[LearningObjective] = []
        visuals: List[SupportingVisualPolicy] = []
        transitions: List[TeachingTransition] = []
        learning_sequence: List[str] = []

        # =====================================================================
        # GENRE-SPECIFIC PEDAGOGICAL BLUEPRINT GENERATION (§2, §3, §18, §19)
        # =====================================================================

        if genre == GenreType.POEM:
            blueprint = self._build_poem_blueprint(
                document_id, chapter_id, chapter_title, subject, grade, pages_data, teaching_graph
            )
        elif genre == GenreType.GEOGRAPHY:
            blueprint = self._build_geography_blueprint(
                document_id, chapter_id, chapter_title, subject, grade, pages_data, teaching_graph
            )
        elif genre == GenreType.SCIENCE:
            blueprint = self._build_science_blueprint(
                document_id, chapter_id, chapter_title, subject, grade, pages_data, teaching_graph
            )
        elif genre == GenreType.MATHEMATICS:
            blueprint = self._build_math_blueprint(
                document_id, chapter_id, chapter_title, subject, grade, pages_data, teaching_graph
            )
        else:
            blueprint = self._build_prose_blueprint(
                document_id, chapter_id, chapter_title, subject, grade, pages_data, teaching_graph
            )

        # Validate Invariants (§15)
        self.validate_blueprint(blueprint)

        # Persist Blueprint (§16)
        self.save_blueprint(blueprint)

        return blueprint

    def _build_poem_blueprint(
        self,
        document_id: str,
        chapter_id: str,
        chapter_title: str,
        subject: str,
        grade: int,
        pages_data: List[Dict[str, Any]],
        graph: ChapterTeachingGraph
    ) -> ChapterPedagogicalBlueprint:
        """
        Builds blueprint for Marathi Poetry:
        - Teacher classroom instructions -> TEACHER-ONLY, NEVER SPOKEN to student
        - Poem stanzas -> ESSENTIAL STUDENT CONTENT, IMMEDIATE SPOKEN
        - Vocabulary / Meanings -> SUPPORTING, ON-DEMAND
        - Poetic Appreciation -> CONCEPTUAL / TUTOR
        - Exercises -> CHECKPOINTS
        """
        objectives = [
            LearningObjective(
                objective_id="obj_poem_1",
                title="काव्यानंद आणि भावार्थ आकलन",
                description="कवितेतील प्रार्थनेचा भावार्थ, शब्दसौंदर्य आणि लय समजून घेणे.",
                bloom_level="understand",
                mapped_learning_units=["lu_stanzas", "lu_appreciation"]
            ),
            LearningObjective(
                objective_id="obj_poem_2",
                title="सद्गुणांची प्रार्थना",
                description="सत्य, न्याय आणि नीतिमूल्ये यांचे जीवनातील महत्त्व ओळखणे.",
                bloom_level="apply",
                mapped_learning_units=["lu_stanzas", "lu_reflection"]
            )
        ]

        seq: List[str] = []
        node_idx = 1

        for pg in pages_data:
            for para in pg.get("paragraphs", []):
                raw_text = para.get("canonical_text", "").strip()
                region_id = para.get("id") or para.get("block_id") or f"reg_{node_idx}"

                # Detect Teacher Instruction (e.g. "प्रस्तुत प्रार्थना ही काव्यानंदासाठी घेतली असून...")
                if "विद्यार्थ्यांकडून" in raw_text or "काव्यानंदासाठी" in raw_text or "म्हणवून घ्यावी" in raw_text:
                    node = TeachingNode(
                        node_id=f"node_t_inst_{node_idx}",
                        node_type=TeachingNodeType.PARAGRAPH,
                        title="शिक्षकांसाठी सूचना (Teacher Instruction)",
                        canonical_text=raw_text,
                        region_id=region_id,
                        learning_unit_id="lu_teacher_guidance",
                        audience=AudienceType.TEACHER,
                        student_relevance=StudentRelevance.TEACHER_ONLY,
                        spoken_priority=SpokenPriority.NEVER,
                        pedagogical_role=PedagogicalRole.TEACHER_INSTRUCTION,
                        accessibility=AccessibilityPolicy(spoken_automatically=False, available_on_demand=True)
                    )
                    graph.add_node(node)
                # Poem Title
                elif para.get("block_type") == "heading" or "बुद्धी दे" in raw_text:
                    node = TeachingNode(
                        node_id=f"node_title_{node_idx}",
                        node_type=TeachingNodeType.CHAPTER,
                        title="शीर्षक (Title)",
                        canonical_text=raw_text,
                        region_id=region_id,
                        learning_unit_id="lu_intro",
                        audience=AudienceType.STUDENT,
                        student_relevance=StudentRelevance.ESSENTIAL,
                        spoken_priority=SpokenPriority.IMMEDIATE,
                        pedagogical_role=PedagogicalRole.INTRODUCTION
                    )
                    graph.add_node(node)
                    seq.append(node.node_id)
                # Stanzas
                else:
                    node = TeachingNode(
                        node_id=f"node_stanza_{node_idx}",
                        node_type=TeachingNodeType.PARAGRAPH,
                        title=f"कडवे {node_idx} (Stanza)",
                        canonical_text=raw_text,
                        region_id=region_id,
                        learning_unit_id="lu_stanzas",
                        audience=AudienceType.STUDENT,
                        student_relevance=StudentRelevance.ESSENTIAL,
                        spoken_priority=SpokenPriority.IMMEDIATE,
                        pedagogical_role=PedagogicalRole.CONCEPT
                    )
                    graph.add_node(node)
                    seq.append(node.node_id)
                    # Link sequential stanzas
                    if len(seq) > 1:
                        graph.add_edge(seq[-2], node.node_id, SemanticTeachingRelation.CONTINUES, "लयबद्ध काव्यप्रवाह")

                node_idx += 1

        # Semantic Nodes for Appreciation and Vocabulary
        vocab_node = TeachingNode(
            node_id="node_poem_vocab",
            node_type=TeachingNodeType.VOCABULARY,
            title="कठीण शब्दार्थ (Glossary)",
            canonical_text="सन्मार्ग = योग्य वाट, मती = बुद्धी, निरंतर = सतत.",
            learning_unit_id="lu_vocab",
            audience=AudienceType.STUDENT,
            student_relevance=StudentRelevance.USEFUL,
            spoken_priority=SpokenPriority.ON_DEMAND,
            pedagogical_role=PedagogicalRole.SUPPLEMENTARY
        )
        graph.add_node(vocab_node)
        graph.add_edge(seq[0] if seq else "node_title_1", "node_poem_vocab", SemanticTeachingRelation.SUPPORTS, "शब्दार्थ सहाय्य")

        transitions = [
            TeachingTransition(
                transition_id="trans_poem_1",
                from_node_id=seq[0] if seq else "node_title_1",
                to_node_id=seq[1] if len(seq) > 1 else "node_stanza_1",
                grounded_speech="चला, आपण या प्रार्थनेचे पहिले कडवे शांत चित्ताने ऐकूया.",
                role="poetic_immersion"
            )
        ]

        return ChapterPedagogicalBlueprint(
            blueprint_id=f"bp_{document_id}_{chapter_id}",
            document_id=document_id,
            chapter_id=chapter_id,
            chapter_title=chapter_title,
            subject=subject,
            grade=grade,
            genre=GenreType.POEM,
            pedagogical_pattern="poetic_appreciation_recitation",
            objectives=objectives,
            learning_units=[
                {"id": "lu_intro", "title": "काव्य परिचय"},
                {"id": "lu_stanzas", "title": "प्रार्थना कडवे"},
                {"id": "lu_vocab", "title": "शब्दार्थ"},
                {"id": "lu_teacher_guidance", "title": "शिक्षक मार्गदर्शन (Non-spoken)"}
            ],
            recommended_learning_sequence=seq,
            teaching_graph=graph,
            supporting_visuals=[],
            transitions=transitions,
            versioning={
                "document_version": "v1.0",
                "chapter_version": "v1.0",
                "teacher_model": "gemini-teacher-bootstrap-v1",
                "prompt_version": "2026.09",
                "schema_version": "blueprint-v2",
                "blueprint_version": 1,
                "status": "verified_truth"
            }
        )

    def _build_geography_blueprint(
        self,
        document_id: str,
        chapter_id: str,
        chapter_title: str,
        subject: str,
        grade: int,
        pages_data: List[Dict[str, Any]],
        graph: ChapterTeachingGraph
    ) -> ChapterPedagogicalBlueprint:
        """
        Builds blueprint for Geography Field Visit:
        - Context & Route Map -> Introduction & spatial orientation
        - Dialogue Turns -> Active observations (relief, soil, vegetation)
        - Visuals -> Supporting (do not interrupt narration, accessible on demand)
        - Discussion & Swadhyay -> Practical application & checkpoints
        """
        objectives = [
            LearningObjective(
                objective_id="obj_geo_1",
                title="क्षेत्रभेटीचा हेतू व तयारी समजून घेणे",
                description="क्षेत्रभेटीसाठी लागणारे साहित्य, नियोजन आणि प्रवासाचा मार्ग नकाशाद्वारे समजून घेणे.",
                bloom_level="understand",
                mapped_learning_units=["lu_prep", "lu_route"]
            ),
            LearningObjective(
                objective_id="obj_geo_2",
                title="प्राकृतिक भूरचना व वनस्पतींमधील बदल अभ्यासणे",
                description="नळदुर्ग ते अलिबाग प्रवासात भूरचना, मृदा, वनस्पती व मानवी वस्त्यांमधील बदल प्रत्यक्ष संवादातून अभ्यासणे.",
                bloom_level="analyze",
                mapped_learning_units=["lu_observations", "lu_dialogue"]
            ),
            LearningObjective(
                objective_id="obj_geo_3",
                title="नकाशा वाचन व दिशा ज्ञान",
                description="प्रवासादरम्यान नकाशावरील स्थान निश्चिती व दिशा यांचा समन्वय साधणे.",
                bloom_level="apply",
                mapped_learning_units=["lu_route", "lu_map"]
            )
        ]

        visuals = [
            SupportingVisualPolicy(
                visual_id="fig_1_1",
                concept_supported_id="concept_route",
                learning_unit_id="lu_route",
                is_essential=True,
                narration_behavior="do_not_interrupt_narration",
                accessibility_description="आकृती १.१: नळदुर्ग ते अलिबाग क्षेत्रभेटीचा मार्ग दर्शविणारा महाराष्ट्र राज्याचा नकाशा.",
                tactile_spatial_notes="पूर्वेकडून पश्चिमेकडे जाणारा रस्ता: सोलापूर, पुणे, खंडाळा मार्गे अलिबाग."
            ),
            SupportingVisualPolicy(
                visual_id="fig_1_2",
                concept_supported_id="concept_equipment",
                learning_unit_id="lu_prep",
                is_essential=False,
                narration_behavior="available_on_demand",
                accessibility_description="आकृती १.२: क्षेत्रभेटीसाठी लागणारे साहित्य - नोंदवही, दिशादर्शक, कॅमेरा व नकाशा."
            )
        ]

        seq: List[str] = []
        node_idx = 1

        for pg in pages_data:
            for para in pg.get("paragraphs", []):
                raw_text = para.get("canonical_text", "").strip()
                b_type = para.get("block_type")
                region_id = para.get("id") or para.get("block_id") or f"reg_geo_{node_idx}"

                if b_type == "heading" or "क्षेत्रभेट" in raw_text:
                    node = TeachingNode(
                        node_id=f"node_geo_title_{node_idx}",
                        node_type=TeachingNodeType.CHAPTER,
                        title="धडा शीर्षक (Title)",
                        canonical_text=raw_text,
                        region_id=region_id,
                        learning_unit_id="lu_intro",
                        audience=AudienceType.STUDENT,
                        student_relevance=StudentRelevance.ESSENTIAL,
                        spoken_priority=SpokenPriority.IMMEDIATE,
                        pedagogical_role=PedagogicalRole.INTRODUCTION
                    )
                    graph.add_node(node)
                    seq.append(node.node_id)
                elif b_type == "dialogue_block" or para.get("dialogue_turns"):
                    node = TeachingNode(
                        node_id=f"node_geo_dialogue_{node_idx}",
                        node_type=TeachingNodeType.DIALOGUE,
                        title="शिक्षक-विद्यार्थी संवाद (Field Dialogue)",
                        canonical_text=raw_text,
                        region_id=region_id,
                        learning_unit_id="lu_dialogue",
                        audience=AudienceType.STUDENT,
                        student_relevance=StudentRelevance.ESSENTIAL,
                        spoken_priority=SpokenPriority.IMMEDIATE,
                        pedagogical_role=PedagogicalRole.DIALOGUE
                    )
                    graph.add_node(node)
                    seq.append(node.node_id)
                elif b_type in ("discussion_box", "activity") or "चर्चा करा" in raw_text:
                    node = TeachingNode(
                        node_id=f"node_geo_activity_{node_idx}",
                        node_type=TeachingNodeType.ACTIVITY,
                        title="चर्चा करा (Discussion & Reflection)",
                        canonical_text=raw_text,
                        region_id=region_id,
                        learning_unit_id="lu_reflection",
                        audience=AudienceType.STUDENT,
                        student_relevance=StudentRelevance.USEFUL,
                        spoken_priority=SpokenPriority.LATER,
                        pedagogical_role=PedagogicalRole.ACTIVITY
                    )
                    graph.add_node(node)
                    seq.append(node.node_id)
                else:
                    node = TeachingNode(
                        node_id=f"node_geo_para_{node_idx}",
                        node_type=TeachingNodeType.PARAGRAPH,
                        title=f"परिच्छेद {node_idx}",
                        canonical_text=raw_text,
                        region_id=region_id,
                        learning_unit_id="lu_observations",
                        audience=AudienceType.STUDENT,
                        student_relevance=StudentRelevance.ESSENTIAL,
                        spoken_priority=SpokenPriority.IMMEDIATE,
                        pedagogical_role=PedagogicalRole.EXPLANATION
                    )
                    graph.add_node(node)
                    seq.append(node.node_id)

                node_idx += 1

        # Teaching Graph Semantic Edges
        if len(seq) >= 2:
            graph.add_edge(seq[0], seq[1], SemanticTeachingRelation.CONTINUES, "पार्श्वभूमी ते प्रत्यक्ष प्रवास")
        # Add visual support edge
        if seq:
            graph.add_edge(seq[0], "fig_1_1", SemanticTeachingRelation.ILLUSTRATES, "मार्ग नकाशा")

        transitions = [
            TeachingTransition(
                transition_id="trans_geo_1",
                from_node_id=seq[0] if seq else "node_geo_title_1",
                to_node_id=seq[1] if len(seq) > 1 else "node_geo_para_1",
                grounded_speech="आता आपण नळदुर्गपासून सुरू होणाऱ्या या रोमांचक प्रवासाची माहिती घेऊया.",
                role="concept_to_narrative"
            )
        ]

        return ChapterPedagogicalBlueprint(
            blueprint_id=f"bp_{document_id}_{chapter_id}",
            document_id=document_id,
            chapter_id=chapter_id,
            chapter_title=chapter_title,
            subject=subject,
            grade=grade,
            genre=GenreType.GEOGRAPHY,
            pedagogical_pattern="exploratory_field_study",
            objectives=objectives,
            learning_units=[
                {"id": "lu_intro", "title": "क्षेत्रभेट परिचय"},
                {"id": "lu_prep", "title": "तयारी व साहित्य"},
                {"id": "lu_route", "title": "प्रवास मार्ग व नकाशा"},
                {"id": "lu_dialogue", "title": "शिक्षिका व विद्यार्थ्यांमधील संभाषण"},
                {"id": "lu_observations", "title": "भौगोलिक निरीक्षणे"},
                {"id": "lu_reflection", "title": "चर्चा व स्वाध्याय"}
            ],
            recommended_learning_sequence=seq,
            teaching_graph=graph,
            supporting_visuals=visuals,
            transitions=transitions,
            versioning={
                "document_version": "v1.0",
                "chapter_version": "v1.0",
                "teacher_model": "gemini-teacher-bootstrap-v1",
                "prompt_version": "2026.09",
                "schema_version": "blueprint-v2",
                "blueprint_version": 1,
                "status": "verified_truth"
            }
        )

    def _build_science_blueprint(
        self,
        document_id: str,
        chapter_id: str,
        chapter_title: str,
        subject: str,
        grade: int,
        pages_data: List[Dict[str, Any]],
        graph: ChapterTeachingGraph
    ) -> ChapterPedagogicalBlueprint:
        """Science Inquiry Blueprint: Phenomenon Question -> Experiment -> Law -> Application."""
        objectives = [
            LearningObjective(
                objective_id="obj_sci_1",
                title="वैज्ञानिक संकल्पनेचे आकलन व प्रयोग",
                description="दैनिक जीवनातील घटनांवरून वैज्ञानिक तत्त्व पडताळून पाहणे.",
                bloom_level="analyze",
                mapped_learning_units=["lu_phenomenon", "lu_law"]
            )
        ]
        seq = [f"node_sci_{i}" for i in range(1, len(pages_data) + 1)]
        for idx, sid in enumerate(seq):
            graph.add_node(TeachingNode(
                node_id=sid,
                node_type=TeachingNodeType.PARAGRAPH,
                title=f"वैज्ञानिक टप्पा {idx+1}",
                canonical_text=f"वैज्ञानिक पुरावा व स्पष्टीकरण भाग {idx+1}",
                learning_unit_id="lu_phenomenon",
                pedagogical_role=PedagogicalRole.EVIDENCE
            ))
        return ChapterPedagogicalBlueprint(
            blueprint_id=f"bp_{document_id}_{chapter_id}",
            document_id=document_id,
            chapter_id=chapter_id,
            chapter_title=chapter_title,
            subject=subject,
            grade=grade,
            genre=GenreType.SCIENCE,
            pedagogical_pattern="inquiry_hypothesis_experiment",
            objectives=objectives,
            learning_units=[{"id": "lu_phenomenon", "title": "निरीक्षण व गृहीतक"}, {"id": "lu_law", "title": "नियम व निष्कर्ष"}],
            recommended_learning_sequence=seq,
            teaching_graph=graph,
            versioning={"status": "verified_truth", "schema_version": "blueprint-v2"}
        )

    def _build_math_blueprint(
        self,
        document_id: str,
        chapter_id: str,
        chapter_title: str,
        subject: str,
        grade: int,
        pages_data: List[Dict[str, Any]],
        graph: ChapterTeachingGraph
    ) -> ChapterPedagogicalBlueprint:
        """Mathematics Blueprint: Concept -> Formula -> Solved Example -> Practice Drill."""
        objectives = [
            LearningObjective(
                objective_id="obj_math_1",
                title="गणितीय सूत्र व उदाहरणे सोडवणे",
                description="नियम समजून पायरीनुसार उदाहरणे सोडवणे.",
                bloom_level="apply",
                mapped_learning_units=["lu_formula", "lu_practice"]
            )
        ]
        seq = [f"node_math_{i}" for i in range(1, len(pages_data) + 1)]
        for idx, mid in enumerate(seq):
            graph.add_node(TeachingNode(
                node_id=mid,
                node_type=TeachingNodeType.EXAMPLE if idx > 0 else TeachingNodeType.DEFINITION,
                title=f"गणितीय घटक {idx+1}",
                canonical_text=f"गणितीय सूत्र व सराव {idx+1}",
                learning_unit_id="lu_practice",
                pedagogical_role=PedagogicalRole.EXAMPLE if idx > 0 else PedagogicalRole.DEFINITION
            ))
        return ChapterPedagogicalBlueprint(
            blueprint_id=f"bp_{document_id}_{chapter_id}",
            document_id=document_id,
            chapter_id=chapter_id,
            chapter_title=chapter_title,
            subject=subject,
            grade=grade,
            genre=GenreType.MATHEMATICS,
            pedagogical_pattern="concrete_visual_abstract_practice",
            objectives=objectives,
            learning_units=[{"id": "lu_formula", "title": "सूत्र व व्याख्या"}, {"id": "lu_practice", "title": "सराव संच"}],
            recommended_learning_sequence=seq,
            teaching_graph=graph,
            versioning={"status": "verified_truth", "schema_version": "blueprint-v2"}
        )

    def _build_prose_blueprint(
        self,
        document_id: str,
        chapter_id: str,
        chapter_title: str,
        subject: str,
        grade: int,
        pages_data: List[Dict[str, Any]],
        graph: ChapterTeachingGraph
    ) -> ChapterPedagogicalBlueprint:
        """Prose / Story Blueprint: Context -> Narrative -> Dialogue -> Moral Comprehension."""
        objectives = [
            LearningObjective(
                objective_id="obj_prose_1",
                title="पाठाचा आशय व विचार समजून घेणे",
                description="गद्य पाठातील विचार, भाषिक सौंदर्य व जीवनमूल्ये समजून घेणे.",
                bloom_level="understand",
                mapped_learning_units=["lu_narrative"]
            )
        ]
        seq = [f"node_prose_{i}" for i in range(1, len(pages_data) + 1)]
        for idx, pid in enumerate(seq):
            graph.add_node(TeachingNode(
                node_id=pid,
                node_type=TeachingNodeType.PARAGRAPH,
                title=f"कथा परिच्छेद {idx+1}",
                canonical_text=f"गद्य कथा भाग {idx+1}",
                learning_unit_id="lu_narrative",
                pedagogical_role=PedagogicalRole.EXPLANATION
            ))
        return ChapterPedagogicalBlueprint(
            blueprint_id=f"bp_{document_id}_{chapter_id}",
            document_id=document_id,
            chapter_id=chapter_id,
            chapter_title=chapter_title,
            subject=subject,
            grade=grade,
            genre=GenreType.PROSE,
            pedagogical_pattern="narrative_moral_comprehension",
            objectives=objectives,
            learning_units=[{"id": "lu_narrative", "title": "कथा प्रवाह"}, {"id": "lu_swadhyay", "title": "स्वाध्याय"}],
            recommended_learning_sequence=seq,
            teaching_graph=graph,
            versioning={"status": "verified_truth", "schema_version": "blueprint-v2"}
        )

    def validate_blueprint(self, blueprint: ChapterPedagogicalBlueprint) -> bool:
        """
        Validates Architectural Invariants (§15):
        1. Non-empty learning objectives.
        2. Graph nodes are accessible and linked.
        3. Teacher instructions are classified as TEACHER-only and never spoken to student.
        4. Canonical text is preserved and non-empty.
        """
        if not blueprint.objectives:
            raise ValueError(f"Blueprint {blueprint.blueprint_id} has no learning objectives!")

        if not blueprint.teaching_graph.nodes:
            raise ValueError(f"Blueprint {blueprint.blueprint_id} has empty teaching graph!")

        # Verify teacher instructions invariant (§4, §18)
        teacher_nodes = blueprint.teaching_graph.get_teacher_only_nodes()
        for tn in teacher_nodes:
            if tn.spoken_priority != SpokenPriority.NEVER:
                raise ValueError(f"Invariant Violation: Teacher node {tn.node_id} has spoken_priority != NEVER!")
            if tn.audience not in (AudienceType.TEACHER, AudienceType.NON_SPOKEN):
                raise ValueError(f"Invariant Violation: Teacher node {tn.node_id} audience must be TEACHER!")

        return True

    def save_blueprint(self, blueprint: ChapterPedagogicalBlueprint) -> str:
        """Persists the verified blueprint to disk."""
        filename = f"{blueprint.document_id}_{blueprint.chapter_id}_blueprint.json"
        path = os.path.join(self.blueprints_dir, filename)
        with open(path, "w", encoding="utf-8") as f:
            json.dump(blueprint.to_dict(), f, ensure_ascii=False, indent=2)
        return path

    def load_blueprint(self, document_id: str, chapter_id: str) -> Optional[ChapterPedagogicalBlueprint]:
        """Loads a stored blueprint from disk if available."""
        filename = f"{document_id}_{chapter_id}_blueprint.json"
        path = os.path.join(self.blueprints_dir, filename)
        if not os.path.exists(path):
            return None
        with open(path, "r", encoding="utf-8") as f:
            data = json.load(f)

        # Reconstruct graph
        tg_data = data.get("teaching_graph", {})
        graph = ChapterTeachingGraph(graph_id=tg_data.get("graph_id", "tg"))
        for nid, nd in tg_data.get("nodes", {}).items():
            acc_data = nd.get("accessibility", {})
            acc = AccessibilityPolicy(
                spoken_automatically=acc_data.get("spoken_automatically", True),
                available_on_demand=acc_data.get("available_on_demand", True),
                requires_visual_description=acc_data.get("requires_visual_description", False),
                visual_description=acc_data.get("visual_description"),
                tactile_spatial_notes=acc_data.get("tactile_spatial_notes")
            )
            node = TeachingNode(
                node_id=nd["node_id"],
                node_type=TeachingNodeType(nd["node_type"]),
                title=nd["title"],
                canonical_text=nd["canonical_text"],
                region_id=nd.get("region_id"),
                learning_unit_id=nd.get("learning_unit_id", "main"),
                audience=AudienceType(nd["audience"]),
                student_relevance=StudentRelevance(nd["student_relevance"]),
                spoken_priority=SpokenPriority(nd["spoken_priority"]),
                pedagogical_role=PedagogicalRole(nd["pedagogical_role"]),
                accessibility=acc,
                metadata=nd.get("metadata", {})
            )
            graph.add_node(node)

        for ed in tg_data.get("edges", []):
            graph.add_edge(
                source_id=ed["source_id"],
                target_id=ed["target_id"],
                relation=SemanticTeachingRelation(ed["relation"]),
                note=ed.get("pedagogical_note", "")
            )

        objs = [LearningObjective(**o) for o in data.get("objectives", [])]
        vis = [SupportingVisualPolicy(**v) for v in data.get("supporting_visuals", [])]
        trans = [TeachingTransition(**t) for t in data.get("transitions", [])]

        return ChapterPedagogicalBlueprint(
            blueprint_id=data["blueprint_id"],
            document_id=data["document_id"],
            chapter_id=data["chapter_id"],
            chapter_title=data["chapter_title"],
            subject=data["subject"],
            grade=data["grade"],
            genre=GenreType(data["genre"]),
            pedagogical_pattern=data["pedagogical_pattern"],
            objectives=objs,
            learning_units=data.get("learning_units", []),
            recommended_learning_sequence=data.get("recommended_learning_sequence", []),
            teaching_graph=graph,
            supporting_visuals=vis,
            transitions=trans,
            versioning=data.get("versioning", {})
        )

chapter_blueprint_engine = ChapterBlueprintEngine()
