"""
Regression & Acceptance Test Suite for AksharSetu Narration Architecture
Tests:
1. Semantic Narration Blocks (Document -> Chapter -> SemanticBlock -> Paragraph -> Sentence -> Word)
2. Paragraph-First Narration & Natural Chunking (not single lines)
3. Dialogue Blocks (DialogueTurns with roles, styles, and timing)
4. Supporting Visuals (Maps/Figures attached with auto_narrate=False)
5. Pronunciation KB & Scope Resolution Hierarchy (document > textbook > subject > global)
6. Pre-TTS Pronunciation Resolution without altering canonical text
7. Provider-Neutral Prosody Planner (educational discourse intent, not pure sentiment)
8. RAG Contextual Retrieval (preserving source provenance and attached visuals)
"""

import sys
from pathlib import Path

# Add project root to sys.path
PROJECT_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

from graphs.semantic_blocks import (
    SemanticBlockType,
    DialogueTurn,
    SupportingMaterial,
    SemanticSentence,
    SemanticNarrationBlock
)
from corpus.pronunciation_kb import (
    PronunciationEntry,
    PronunciationKnowledgeBase,
    PronunciationResolver
)
from orchestrator.prosody_planner import ProsodyPlanner, ProsodyPlan
from orchestrator.narration_planner import NarrationPlanner
from orchestrator.rag_context_engine import RAGContextEngine, AssembledRAGContext, RetrievedContextSource
from ingestion.chapter_processor import ChapterProcessor


def test_rag_context_engine():
    print("[TEST 3] RAG Context Engine Provenance & Visuals...")
    rag = RAGContextEngine()
    
    # Construct block with attached supporting visual
    block_intro = SemanticNarrationBlock(
        block_id="block_p1",
        block_type=SemanticBlockType.PARAGRAPH,
        canonical_text="नळदुर्ग ते अलिबाग या प्रवासादरम्यान आपण प्राकृतिक रचनेतील बदल पाहणार आहोत.",
        chapter_id="ch_1",
        page_id="12",
        pdf_page=12,
        printed_page=1,
        learning_unit_id="lu_field_visit_prep",
        source_region_ids=["p12_reg_02"],
        supporting_visuals=[
            SupportingMaterial(
                material_id="map_1_1",
                material_type="map",
                title="आकृती १.१ : क्षेत्रभेटीचा मार्ग",
                caption_text="नळदुर्ग ते अलिबाग प्रवासाचा नकाशा",
                supports_learning_unit_id="lu_field_visit_prep",
                auto_narrate=False,
                is_essential=True,
                explanation="सोलापूर, पुणे मार्गे अलिबागकडे जाणारा प्रवास मार्ग."
            )
        ]
    )
    
    context = rag.assemble_context(
        query="या नकाशात कोणता मार्ग दाखवला आहे?",
        document_id="geo-10",
        chapter_id="ch_1",
        current_block=block_intro
    )
    
    assert context.document_id == "geo-10"
    assert context.chapter_id == "ch_1"
    assert context.active_learning_unit_id == "lu_field_visit_prep"
    assert len(context.supporting_visuals) >= 1, "RAG must retrieve supporting visual (map/diagram)"
    assert context.supporting_visuals[0].get("material_id") == "map_1_1"
    assert context.supporting_visuals[0].get("auto_narrate") is False, "Supporting visual must not auto-interrupt narrative"
    
    # Verify provenance on all retrieved sources
    assert len(context.retrieved_sources) >= 2, "Must retrieve at least paragraph and visual sources"
    for src in context.retrieved_sources:
        assert src.document_id == "geo-10"
        assert src.chapter_id == "ch_1"
        assert src.learning_unit_id == "lu_field_visit_prep"
        assert src.region_id in ["p12_reg_02", "map_1_1"]
    print("  -> Passed RAG Context Engine test")

def test_pronunciation_kb_and_hierarchy():
    print("[TEST 1] Pronunciation KB & Scope Hierarchy...")
    kb = PronunciationKnowledgeBase()
    
    # Check default entries loaded
    naldurg_entries = kb.get_entries_for_word("नळदुर्ग")
    assert len(naldurg_entries) > 0, "Failed to load default pronunciation for 'नळदुर्ग'"
    assert naldurg_entries[0].approved is True, "Pronunciation must be approved"
    
    # Test scope hierarchy: Document overrides textbook, textbook overrides global
    kb.add_entry(PronunciationEntry(
        canonical_text="घाट",
        preferred_pronunciation="घाट (सामान्य)",
        scope="global",
        approved=True
    ))
    kb.add_entry(PronunciationEntry(
        canonical_text="घाट",
        preferred_pronunciation="घाट (भूगोल विषय)",
        scope="subject",
        target_id="geography",
        approved=True
    ))
    kb.add_entry(PronunciationEntry(
        canonical_text="घाट",
        preferred_pronunciation="घाट (इयत्ता १०)",
        scope="textbook",
        target_id="geo-10",
        approved=True
    ))
    kb.add_entry(PronunciationEntry(
        canonical_text="घाट",
        preferred_pronunciation="घाट (प्रकरण १ नळदुर्ग मार्ग)",
        scope="document",
        target_id="doc_geo_ch1",
        approved=True
    ))
    
    resolver = PronunciationResolver(kb)
    
    # Query with full doc context -> should get document scope
    res_doc = resolver.resolve_word("घाट", document_id="doc_geo_ch1", textbook_id="geo-10", subject="geography")
    assert res_doc and res_doc.preferred_pronunciation == "घाट (प्रकरण १ नळदुर्ग मार्ग)", f"Expected doc scope, got {res_doc}"
    
    # Query with another doc in same textbook -> should get textbook scope
    res_tb = resolver.resolve_word("घाट", document_id="doc_geo_ch2", textbook_id="geo-10", subject="geography")
    assert res_tb and res_tb.preferred_pronunciation == "घाट (इयत्ता १०)", f"Expected textbook scope, got {res_tb}"
    
    # Query with unknown textbook in same subject -> should get subject scope
    res_subj = resolver.resolve_word("घाट", document_id="other_doc", textbook_id="other_tb", subject="geography")
    assert res_subj and res_subj.preferred_pronunciation == "घाट (भूगोल विषय)", f"Expected subject scope, got {res_subj}"
    
    # Query with unknown subject -> should get global scope
    res_global = resolver.resolve_word("घाट", document_id="other_doc", textbook_id="other_tb", subject="marathi")
    assert res_global and res_global.preferred_pronunciation == "घाट (सामान्य)", f"Expected global scope, got {res_global}"
    
    # Test text resolution preserving canonical text
    sample_text = "आम्ही नळदुर्ग येथून निघालो आणि घाटावर पोहोचलो."
    resolved_speech_text, applied = resolver.resolve_speech_text(sample_text, document_id="doc_geo_ch1", textbook_id="geo-10")
    assert "नळ-दुर्ग" in resolved_speech_text
    assert sample_text != resolved_speech_text, "Speech text should be phoneticized"
    assert len(applied) >= 1, "Should apply at least 1 correction"
    print("  -> Passed Pronunciation KB & Scope Hierarchy test")


def test_narration_planner_chunking_and_dialogue():
    print("[TEST 2] Narration Planner Chunking & Dialogue...")
    planner = NarrationPlanner()
    
    # Test 1: Long paragraph chunking (Paragraph-first, chunked into 2-3 sentences for TTS)
    sent_texts = [
        "शिक्षिका : 'विद्यार्थ्यांनो, आता आपण सोलापूर शहर ओलांडून पुढे जात आहोत.",
        "आता आपण ज्या भागात आहोत, तो बालाघाट डोंगररांगेच्या दक्षिणेकडील भाग आहे.",
        "हा प्रदेश पर्जन्यछायेचा असल्यामुळे येथे वनस्पती विरळ आणि शुष्क स्वरूपाच्या आहेत.",
        "रस्त्याच्या दोन्ही बाजूंना बाभूळ, कोरफड आणि निवडुंग यांसारख्या वनस्पती दिसत आहेत.",
        "येथील घरे प्रामुख्याने धाब्याची असून भिंती मातीच्या आहेत.'"
    ]
    long_para = " ".join(sent_texts)
    
    block_para = SemanticNarrationBlock(
        block_id="block_long_p1",
        block_type=SemanticBlockType.PARAGRAPH,
        canonical_text=long_para,
        chapter_id="ch_1",
        page_id="p13",
        pdf_page=13,
        printed_page=2,
        learning_unit_id="lu_solapur_route",
        sentences=[SemanticSentence(sentence_id=i, text=s) for i, s in enumerate(sent_texts)]
    )
    
    plan_para = planner.plan_narration(block_para)
    assert plan_para.block_type == "paragraph"
    assert len(plan_para.chunks) >= 2, f"Long paragraph should be chunked into at least 2 segments, got {len(plan_para.chunks)}"
    for chunk in plan_para.chunks:
        assert chunk.pause_after_ms > 0, "Each chunk must specify prosody pause"
        assert chunk.speech_text, "Chunk must have resolved speech text"
        
    # Test 2: Dialogue Block with turns
    dialogue_block = SemanticNarrationBlock(
        block_id="block_dialogue_1",
        block_type=SemanticBlockType.DIALOGUE_BLOCK,
        canonical_text="शिक्षिका : नकाशा पहा.\nराहुल : मॅडम, हा राष्ट्रीय महामार्ग आहे का?",
        dialogue_turns=[
            DialogueTurn(
                turn_id="turn_1",
                speaker="शिक्षिका",
                speaker_role="teacher",
                text="विद्यार्थ्यांनो, नकाशात दाखवलेला प्रवास मार्ग नीट पहा.",
                order=1,
                learning_unit_id="lu_field_visit_prep",
                source_region_id="p12_reg_08"
            ),
            DialogueTurn(
                turn_id="turn_2",
                speaker="राहुल",
                speaker_role="student",
                text="मॅडम, आपण आता राष्ट्रीय महामार्ग क्रमांक ६५ वरून प्रवास करत आहोत का?",
                order=2,
                learning_unit_id="lu_field_visit_prep",
                source_region_id="p12_reg_09"
            )
        ],
        chapter_id="ch_1",
        page_id="p12",
        pdf_page=12,
        printed_page=1,
        learning_unit_id="lu_field_visit_prep"
    )
    
    plan_dialogue = planner.plan_narration(dialogue_block)
    assert plan_dialogue.block_type == "dialogue_block"
    assert len(plan_dialogue.dialogue_turns) == 2, f"Expected 2 dialogue turns, got {len(plan_dialogue.dialogue_turns)}"
    assert plan_dialogue.dialogue_turns[0].speaker_role == "teacher"
    assert plan_dialogue.dialogue_turns[1].speaker_role == "student"
    assert plan_dialogue.dialogue_turns[0].pause_after_ms >= 350, "Dialogue turn must have conversational pause"
    print("  -> Passed Narration Planner Chunking & Dialogue test")




import urllib.request
import json

def test_chapter_processor_semantic_blocks():
    print("[TEST 4] Geography Chapter 1 Semantic Block Ingestion...")
    url = "http://127.0.0.1:8000/api/chapters/ch_1/reader?doc_id=geo-10"
    req = urllib.request.Request(url)
    with urllib.request.urlopen(req) as resp:
        data = json.loads(resp.read().decode("utf-8"))
    
    chapter = data["chapter"]
    assert chapter["document_id"] == "geo-10"
    assert chapter["chapter_id"] == "ch_1"
    assert len(data["pages"]) >= 1
    
    p1 = data["pages"][0]
    blocks = p1.get("paragraphs", [])
    assert len(blocks) > 0, "Page 1 must contain semantic blocks"
    
    block_types = [b["block_type"] for b in blocks]
    assert "heading" in block_types, "Must contain chapter heading"
    assert "paragraph" in block_types, "Must contain intro paragraph"
    assert "dialogue_block" in block_types, "Must contain dialogue block"
    assert "discussion" in block_types, "Must contain discussion block"
    
    # Check supporting visuals attachment
    intro_block = next((b for b in blocks if b["block_type"] == "paragraph" and "क्षेत्रभेट" in b["canonical_text"]), None)
    assert intro_block is not None, "Introductory paragraph block missing"
    assert len(intro_block.get("supporting_visuals", [])) >= 1, "Intro block must have map attached as supporting visual"
    assert intro_block["supporting_visuals"][0]["auto_narrate"] is False, "Attached map must be auto_narrate=False"
    
    print(f"  -> Passed Geography Chapter 1 Ingestion: {len(blocks)} semantic blocks verified")


def run_all():
    print("=" * 60)
    print("RUNNING AKSHARSETU NARRATION ARCHITECTURE REGRESSION SUITE")
    print("=" * 60)
    test_pronunciation_kb_and_hierarchy()
    test_narration_planner_chunking_and_dialogue()
    test_rag_context_engine()
    test_chapter_processor_semantic_blocks()
    print("=" * 60)
    print("ALL NARRATION ARCHITECTURE REGRESSION TESTS PASSED SUCCESSFULLY!")
    print("=" * 60)


if __name__ == "__main__":
    run_all()
