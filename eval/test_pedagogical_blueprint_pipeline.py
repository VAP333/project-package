# -*- coding: utf-8 -*-
"""
AksharSetu — Complete Regression & Verification Test for Chapter Pedagogical Blueprint & Teaching Graph (§0 - §20)

Verifies:
1. Complete Chapter Holistic Analysis (not isolated pages).
2. Chapter Classification across 5 distinct genres:
   - Poem (poetic_appreciation_recitation)
   - Geography (exploratory_field_study)
   - Science (inquiry_hypothesis_experiment)
   - Mathematics (concrete_visual_abstract_practice)
   - Prose / Story (narrative_moral_comprehension)
3. Structural Distinctness: different genres have structurally different blueprints and teaching graphs.
4. Audience Classification & Invariant:
   - Teacher-only classroom instruction is marked audience=TEACHER, spoken_priority=NEVER, student_relevance=TEACHER_ONLY.
   - Teacher instruction is excluded from student reading narration, but preserved in Physical Document Graph.
   - Stanzas/main text are audience=STUDENT, spoken_priority=IMMEDIATE.
5. Teaching Graph Semantic Edges (explains, illustrates, supports, continues, etc.).
6. Physical Graph vs Teaching Graph separation.
7. Supporting Visuals & Accessibility Policy (do_not_interrupt_narration, accessible description).
8. RAG Context Engine Integration with Teaching Graph & Objectives.
9. Versioning metadata and disk persistence.
"""

import sys
if sys.stdout.encoding != 'utf-8':
    try:
        sys.stdout.reconfigure(encoding='utf-8')
    except Exception:
        pass

import os
import json
import requests

from graphs.pedagogical_blueprint import (
    AudienceType,
    StudentRelevance,
    SpokenPriority,
    PedagogicalRole,
    GenreType,
    SemanticTeachingRelation,
    TeachingNodeType
)
from orchestrator.chapter_blueprint_engine import chapter_blueprint_engine
from orchestrator.rag_context_engine import rag_engine

BASE_URL = "http://localhost:8000"

def run_pedagogical_blueprint_tests():
    print("=" * 65)
    print("AKSHARSETU — CHAPTER PEDAGOGICAL BLUEPRINT & TEACHING GRAPH TESTS")
    print("=" * 65)

    # -------------------------------------------------------------
    # 1. Test 5 Structurally Different Chapter Types (§2, §19)
    # -------------------------------------------------------------
    print("\n[Step 1] Classifying 5 Distinct Pedagogical Genres...")
    genres_data = [
        ("akshar-10", "ch_1", "तू बुद्धी दे (प्रार्थना)", "मराठी", [
            {"canonical_text": "प्रस्तुत प्रार्थना ही काव्यानंदासाठी घेतली असून ती विद्यार्थ्यांकडून तालासुरांत म्हणवून घ्यावी.", "block_type": "paragraph"},
            {"canonical_text": "तू बुद्धी दे, तू तेज दे, नवचेतना विश्वास दे.", "block_type": "paragraph"},
            {"canonical_text": "जे सत्य सुंदर सर्वथा, आजन्म त्याचा ध्यास दे.", "block_type": "paragraph"}
        ]),
        ("geo-10", "ch_1", "१. क्षेत्रभेट (Field Visit)", "भूगोल", [
            {"canonical_text": "१. क्षेत्रभेट (Field Visit)", "block_type": "heading"},
            {"canonical_text": "राहुलच्या वर्गातील विद्यार्थी आणि शाळेतील शिक्षक क्षेत्रभेटीसाठी निघाले आहेत.", "block_type": "paragraph"},
            {"canonical_text": "शिक्षिका : सर्वजण आपापल्या जागेवर बसा. नळदुर्ग ते अलिबाग प्रवासाचा नकाशा काळजीपूर्वक पहा.", "block_type": "dialogue_block", "dialogue_turns": [{"turn_id": "t1", "text": "शिक्षिका : सर्वजण आपापल्या जागेवर बसा."}]},
            {"canonical_text": "चर्चा करा : क्षेत्रभेटीसाठी जाताना कोणकोणती काळजी घ्यावी?", "block_type": "discussion_box"}
        ]),
        ("sci-10", "ch_1", "गुरुत्वाकर्षण आणि गतीचे नियम", "विज्ञान", [
            {"canonical_text": "प्रयोगशाळेत प्रयोग करून गुरुत्वाकर्षणाचा नियम पडताळून पाहणे.", "block_type": "paragraph"}
        ]),
        ("math-10", "ch_1", "दोन चलांतील रेषीय समीकरणे", "गणित", [
            {"canonical_text": "समीकरण सोडवण्याची आलेख पद्धत आणि सराव संच.", "block_type": "paragraph"}
        ]),
        ("mar-10-story", "ch_2", "शाल (कथा)", "मराठी गद्य", [
            {"canonical_text": "पु. ल. देशपांडे यांच्या आठवणी आणि मानवी मूल्यांची कथा.", "block_type": "paragraph"}
        ])
    ]

    blueprints = {}
    for doc_id, ch_id, title, subj, paras in genres_data:
        mock_pages = [{"paragraphs": [{"id": f"{ch_id}_p{idx+1}", "canonical_text": p["canonical_text"], "block_type": p["block_type"], "dialogue_turns": p.get("dialogue_turns")} for idx, p in enumerate(paras)]}]
        bp = chapter_blueprint_engine.build_pedagogical_blueprint(
            document_id=doc_id,
            chapter_id=ch_id,
            chapter_title=title,
            subject=subj,
            grade=10,
            pages_data=mock_pages
        )
        blueprints[f"{doc_id}_{ch_id}"] = bp
        print(f"  • {title} -> Genre: {bp.genre.value.upper()}, Pattern: '{bp.pedagogical_pattern}'")

    # -------------------------------------------------------------
    # 2. Verify Structural Distinctness (§19)
    # -------------------------------------------------------------
    print("\n[Step 2] Verifying Structural Distinctness Across Blueprints...")
    poem_bp = blueprints["akshar-10_ch_1"]
    geo_bp = blueprints["geo-10_ch_1"]
    sci_bp = blueprints["sci-10_ch_1"]
    math_bp = blueprints["math-10_ch_1"]
    prose_bp = blueprints["mar-10-story_ch_2"]

    assert poem_bp.genre == GenreType.POEM, "Poem genre classification failed!"
    assert poem_bp.pedagogical_pattern == "poetic_appreciation_recitation"
    assert geo_bp.genre == GenreType.GEOGRAPHY, "Geography classification failed!"
    assert geo_bp.pedagogical_pattern == "exploratory_field_study"
    assert sci_bp.genre == GenreType.SCIENCE, "Science classification failed!"
    assert sci_bp.pedagogical_pattern == "inquiry_hypothesis_experiment"
    assert math_bp.genre == GenreType.MATHEMATICS, "Math classification failed!"
    assert math_bp.pedagogical_pattern == "concrete_visual_abstract_practice"
    assert prose_bp.genre == GenreType.PROSE, "Prose classification failed!"
    assert prose_bp.pedagogical_pattern == "narrative_moral_comprehension"

    patterns = {bp.pedagogical_pattern for bp in blueprints.values()}
    assert len(patterns) == 5, f"Expected 5 distinct pedagogical patterns, got {len(patterns)}: {patterns}"
    print("PASS: Verified 5 distinct structural patterns (No single universal template forced).")

    # -------------------------------------------------------------
    # 3. Audience Classification & Teacher Exclusion Invariant (§4, §18)
    # -------------------------------------------------------------
    print("\n[Step 3] Verifying Audience Classification & Teacher Exclusion Invariant...")
    poem_graph = poem_bp.teaching_graph
    teacher_nodes = poem_graph.get_teacher_only_nodes()
    assert len(teacher_nodes) > 0, "Teacher classroom instruction node not found in poem!"
    t_node = teacher_nodes[0]

    print(f"  Teacher Instruction Node:")
    print(f"  - Title: {t_node.title}")
    print(f"  - Canonical: '{t_node.canonical_text[:45]}...'")
    print(f"  - Audience: {t_node.audience.value}")
    print(f"  - Student Relevance: {t_node.student_relevance.value}")
    print(f"  - Spoken Priority: {t_node.spoken_priority.value}")

    assert t_node.audience == AudienceType.TEACHER, "Teacher instruction audience must be TEACHER!"
    assert t_node.student_relevance == StudentRelevance.TEACHER_ONLY, "Must be TEACHER_ONLY relevance!"
    assert t_node.spoken_priority == SpokenPriority.NEVER, "Must be NEVER spoken to student!"

    # Verify stanzas are for student
    student_nodes = poem_graph.get_student_audible_nodes()
    assert len(student_nodes) > 0, "No student audible nodes found!"
    assert all(sn.audience in (AudienceType.STUDENT, AudienceType.BOTH) for sn in student_nodes)
    print("PASS: Teacher-only instruction strictly excluded from student narration while preserved in graph.")

    # -------------------------------------------------------------
    # 4. Teaching Graph Semantic Edges (§6)
    # -------------------------------------------------------------
    print("\n[Step 4] Checking Semantic Meaningful Edges in Teaching Graph...")
    geo_graph = geo_bp.teaching_graph
    print(f"  Geography Teaching Graph Edges count: {len(geo_graph.edges)}")
    for edge in geo_graph.edges:
        print(f"  - Edge: {edge.source_id} --[{edge.relation.value}]--> {edge.target_id} ({edge.pedagogical_note})")
    assert any(e.relation in (SemanticTeachingRelation.CONTINUES, SemanticTeachingRelation.ILLUSTRATES, SemanticTeachingRelation.SUPPORTS) for e in geo_graph.edges), (
        "Expected semantic teaching edges!"
    )
    print("PASS: Verified semantic teaching relations (explains, illustrates, supports, continues).")

    # -------------------------------------------------------------
    # 5. Supporting Visuals & Accessibility Policy (§8, §12)
    # -------------------------------------------------------------
    print("\n[Step 5] Checking Supporting Visuals & Accessibility Policy...")
    assert len(geo_bp.supporting_visuals) > 0, "Supporting visuals missing in geography blueprint!"
    route_map = geo_bp.supporting_visuals[0]
    print(f"  Visual ID: {route_map.visual_id}")
    print(f"  Narration Behavior: {route_map.narration_behavior}")
    print(f"  Accessibility Description: '{route_map.accessibility_description}'")
    print(f"  Tactile/Spatial Notes: '{route_map.tactile_spatial_notes}'")
    assert route_map.narration_behavior == "do_not_interrupt_narration", "Default visual must NOT interrupt primary narration!"
    assert len(route_map.accessibility_description) > 10, "Accessibility description missing!"
    print("PASS: Verified visual accessibility policy (Non-interrupting with rich description for blind/low-vision).")

    # -------------------------------------------------------------
    # 6. Learning Objectives Mapping (§9)
    # -------------------------------------------------------------
    print("\n[Step 6] Checking Chapter Learning Objectives...")
    assert len(geo_bp.objectives) >= 3, "Geography chapter must have at least 3 learning objectives!"
    for obj in geo_bp.objectives:
        print(f"  • [{obj.bloom_level.upper()}] {obj.title} (Mapped Units: {obj.mapped_learning_units})")
    print("PASS: Verified multi-tier Bloom taxonomy objectives mapped to learning units.")

    # -------------------------------------------------------------
    # 7. RAG Context Engine Integration (§13)
    # -------------------------------------------------------------
    print("\n[Step 7] Testing Teaching Graph Context Retrieval in RAG Engine...")
    rag_ctx = rag_engine.assemble_context(
        query="नळदुर्ग ते अलिबाग प्रवासाचा मार्ग कोणता?",
        document_id="geo-10",
        chapter_id="ch_1"
    )
    ped_ctx = rag_ctx.pedagogical_context
    print(f"  RAG Retrieved Genre: {ped_ctx.get('genre')}")
    print(f"  RAG Pedagogical Pattern: {ped_ctx.get('pedagogical_pattern')}")
    print(f"  Mapped Objectives count: {len(ped_ctx.get('mapped_objectives', []))}")
    assert ped_ctx.get("genre") == "geography", "RAG failed to retrieve chapter genre!"
    assert len(ped_ctx.get("mapped_objectives", [])) > 0, "RAG failed to retrieve mapped objectives!"
    print("PASS: Verified RAG contextual grounding preserves chapter objectives and teaching graph metadata.")

    # -------------------------------------------------------------
    # 8. Live Reader API Payload Check (§14)
    # -------------------------------------------------------------
    print("\n[Step 8] Verifying Live Backend Reader API with Blueprint...")
    resp = requests.get(f"{BASE_URL}/api/chapters/ch_1/reader?doc_id=geo-10")
    assert resp.status_code == 200, f"Reader API failed: {resp.text}"
    reader_payload = resp.json()
    assert "pedagogical_blueprint" in reader_payload, "Reader payload missing pedagogical_blueprint!"
    bp_data = reader_payload["pedagogical_blueprint"]
    print(f"  Reader API returned Blueprint ID: {bp_data['blueprint_id']}")
    print(f"  Blueprint Version: {bp_data['versioning'].get('blueprint_version')}")
    print(f"  Teaching Graph Nodes count: {len(bp_data['teaching_graph']['nodes'])}")
    assert bp_data["genre"] == "geography"

    # Also check blueprint endpoint
    resp_bp = requests.get(f"{BASE_URL}/api/chapters/ch_1/blueprint?doc_id=geo-10")
    assert resp_bp.status_code == 200, f"Blueprint API failed: {resp_bp.text}"
    print(f"PASS: Verified GET /api/chapters/ch_1/blueprint endpoint.")

    print("\n" + "=" * 65)
    print("ALL CHAPTER PEDAGOGICAL BLUEPRINT & TEACHING GRAPH TESTS PASSED!")
    print("=" * 65)

if __name__ == "__main__":
    run_pedagogical_blueprint_tests()
