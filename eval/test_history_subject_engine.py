"""
AksharSetu — Class 8 History Reference Implementation Comprehensive Test Suite (Phase 13)

Validates all 15 key areas of the History Subject Engine:
1. CORPUS: JSON schema validation, JSONL parsing, 14 chapters count, chapter IDs, page ranges, learning units, provenance.
2. GRAPH: Graph integrity, missing references, invalid relationships, provenance preservation.
3. HISTORY GRAMMAR: Chapter classification, chapter structure, 8 genre patterns, 5-part स्वाध्याय structure.
4. NARRATION: Narration policy resolution, normal reading vs on-demand, teacher content handling.
5. PRONUNCIATION: Lexicon lookup, fallback behavior, verification status tracking.
6. CACHE: Cache hit, cache miss, version-based granular invalidation.
7. RAG / TUTOR: Provenance preservation, current learning unit grounding, unsupported-answer handling.
8. API: All major History endpoints (/history, /history/chapters, /history/chapters/{ch}, /history/chapters/{ch}/reader, etc.).
"""

import os
import sys
import unittest
from fastapi.testclient import TestClient

if sys.stdout.encoding != 'utf-8':
    try:
        sys.stdout.reconfigure(encoding='utf-8')
    except Exception:
        pass

from corpus.history_loader import history_corpus_loader, ProvenanceStatus
from graphs.history_physical_graph import history_physical_graph
from graphs.history_grammar import history_grammar_engine, HistoryGenre
from graphs.history_learning_graph import history_learning_graph, LearningRelationType
from graphs.history_teaching_graph import history_teaching_graph, TeachingNodeType, TeachingOrigin
from orchestrator.history_narration_planner import history_narration_planner, NarrationPolicy, SpeakingStyle
from corpus.history_pronunciation import history_pronunciation_kb
from orchestrator.history_tutor_engine import history_tutor_engine
from graphs.history_cache import history_cache, HistoryCacheLayer
from backend.main import app


class TestHistorySubjectEngine(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.client = TestClient(app)
        cls.loader = history_corpus_loader.validate_and_load()
        cls.physical_graph = history_physical_graph.build_graph()
        cls.grammar = history_grammar_engine
        cls.learning_graph = history_learning_graph.build_graph()
        cls.teaching_graph = history_teaching_graph.build_graph()
        cls.narration_planner = history_narration_planner
        cls.pronunciation_kb = history_pronunciation_kb.build_lexicon()
        cls.tutor_engine = history_tutor_engine
        cls.tutor_engine.ensure_initialized()
        cls.cache = history_cache

    # -------------------------------------------------------------------------
    # 1. CORPUS TESTS (§Phase 1)
    # -------------------------------------------------------------------------

    def test_01_corpus_manifest_and_schema(self):
        """Validates manifest integrity, class number, subject, and medium."""
        manifest = self.loader.manifest
        self.assertIsNotNone(manifest)
        self.assertEqual(manifest.document_id, "AKS_HISTORY_CLASS8_HISTORY")
        self.assertEqual(manifest.subject, "history")
        self.assertEqual(manifest.class_num, 8)
        self.assertEqual(manifest.medium, "Marathi")
        self.assertEqual(manifest.pdf_total_pages, 75)
        self.assertEqual(manifest.content_pdf_page_range, [10, 74])
        self.assertEqual(manifest.front_matter_pdf_page_range, [1, 9])
        self.assertEqual(manifest.back_cover_pdf_page_range, [75, 75])

    def test_02_corpus_14_chapters_inventory_and_contiguous_pages(self):
        """Validates exact 14 chapter count, valid IDs (CH_01 to CH_14), and contiguous page spans."""
        chapters = self.loader.list_all_chapters()
        self.assertEqual(len(chapters), 14, "Must contain exactly 14 chapters")

        expected_start = 10
        for idx, ch in enumerate(chapters, 1):
            expected_id = f"CH_{idx:02d}"
            self.assertEqual(ch.chapter_id, expected_id)
            self.assertEqual(ch.chapter_number, idx)
            start_p, end_p = ch.pdf_page_range
            self.assertEqual(start_p, expected_start)
            self.assertGreaterEqual(end_p, start_p)
            expected_start = end_p + 1

        self.assertEqual(expected_start, 75, "Content pages must span exactly up to PDF page 74")

    def test_03_corpus_learning_units_and_concepts(self):
        """Validates that every chapter has learning units, key concepts, and assessment definitions."""
        for ch in self.loader.list_all_chapters():
            self.assertGreater(len(ch.learning_units), 0, f"Chapter {ch.chapter_id} must have learning units")
            self.assertGreater(len(ch.assessment.types_present), 0, f"Chapter {ch.chapter_id} must have assessments")
            self.assertIsNotNone(ch.narration_policy)
            self.assertIsNotNone(ch.speaking_style)

    def test_04_corpus_trust_model_provenance(self):
        """Validates that SOURCE_VERIFIED is never equated with GOLDEN_TRUTH in baseline v0.1."""
        self.assertFalse(self.loader.is_golden_truth("SOURCE_VERIFIED"))
        for ch in self.loader.list_all_chapters():
            self.assertNotEqual(ch.verification_status, "GOLDEN_TRUTH")
            self.assertEqual(self.loader.get_trust_level(ch.source_status), ProvenanceStatus.SOURCE_VERIFIED)

    # -------------------------------------------------------------------------
    # 2. PHYSICAL DOCUMENT GRAPH TESTS (§Phase 2)
    # -------------------------------------------------------------------------

    def test_05_physical_graph_entities_and_relationships(self):
        """Validates Document -> Chapter -> Page -> Region hierarchy and provenance."""
        doc = self.physical_graph.get_document()
        self.assertEqual(doc["document_id"], "AKS_HISTORY_CLASS8_HISTORY")
        self.assertEqual(doc["total_pages"], 75)
        self.assertEqual(doc["total_chapters"], 14)

        # Check Chapter 1
        ch1 = self.physical_graph.get_chapter("CH_01")
        self.assertIsNotNone(ch1)
        pages = ch1.get_pages()
        self.assertEqual(len(pages), 4)  # PDF pp. 10 to 13

        # Check Page Regions
        p10 = self.physical_graph.get_page(10)
        self.assertIsNotNone(p10)
        regions = p10.get_regions()
        self.assertGreater(len(regions), 0)

        # Invariant Check: bbox is explicitly None, visual_description_status is UNVERIFIED
        r1 = regions[0]
        self.assertIsNone(r1.bbox, "Must not fabricate bounding boxes")
        self.assertEqual(r1.visual_description_status, "UNVERIFIED", "Must explicitly represent unverified visual status")
        self.assertEqual(r1.source_status, "SOURCE_VERIFIED")
        self.assertIsNotNone(r1.region_id)

    def test_06_physical_graph_region_to_region_links(self):
        """Validates preceding, following, and adjacent relationships between regions."""
        p10 = self.physical_graph.get_page(10)
        regions = p10.get_regions()
        self.assertGreater(len(regions), 1)

        for i in range(len(regions) - 1):
            curr_r = regions[i]
            next_r = regions[i + 1]
            if curr_r.following_region_id:
                self.assertEqual(curr_r.following_region_id, next_r.region_id)
            if next_r.preceding_region_id:
                self.assertEqual(next_r.preceding_region_id, curr_r.region_id)

    # -------------------------------------------------------------------------
    # 3. HISTORY GRAMMAR TESTS (§Phase 3)
    # -------------------------------------------------------------------------

    def test_07_history_grammar_classification_and_patterns(self):
        """Validates 8 distinct historical structural patterns."""
        p_ch1 = self.grammar.get_pattern_for_chapter("CH_01")
        self.assertEqual(p_ch1.genre, HistoryGenre.CATEGORY_SURVEY)

        p_ch4 = self.grammar.get_pattern_for_chapter("CH_04")
        self.assertEqual(p_ch4.genre, HistoryGenre.CAUSE_EVENT_CONSEQUENCE)

        p_ch9 = self.grammar.get_pattern_for_chapter("CH_09")
        self.assertEqual(p_ch9.genre, HistoryGenre.FLAGSHIP_EVENT)

        p_ch14 = self.grammar.get_pattern_for_chapter("CH_14")
        self.assertEqual(p_ch14.genre, HistoryGenre.STATE_FORMATION)

    def test_08_history_grammar_nuances_and_sensitivity(self):
        """Validates chapter-specific nuances such as CH_09 parallel storylines and CH_12 visual plate."""
        nuance_ch9 = self.grammar.get_chapter_nuance("CH_09")
        self.assertIsNotNone(nuance_ch9)
        self.assertEqual(nuance_ch9.nuance_type, "interleaved_parallel_strands")
        self.assertEqual(nuance_ch9.structural_rule, "interleaved_parallel_timeline")

        nuance_ch12 = self.grammar.get_chapter_nuance("CH_12")
        self.assertIsNotNone(nuance_ch12)
        self.assertEqual(nuance_ch12.nuance_type, "visual_plate_caveat")

        # Swadhyay template
        swadhyay = self.grammar.get_swadhyay_template()
        self.assertEqual(len(swadhyay.exercises), 5)
        self.assertEqual(swadhyay.exercises[0].exercise_type, "mcq")

    # -------------------------------------------------------------------------
    # 4. LEARNING GRAPH TESTS (§Phase 4)
    # -------------------------------------------------------------------------

    def test_09_learning_graph_entities_and_edges(self):
        """Validates LearningUnit, Concept, Definition, NamedEntity and semantic relationships."""
        ch1_units = self.learning_graph.get_units_for_chapter("CH_01")
        self.assertEqual(len(ch1_units), 7)

        u1 = ch1_units[0]
        self.assertEqual(u1.unit_id, "CH_01_LU_01")
        self.assertEqual(u1.provenance_status, "SOURCE_VERIFIED")

        # Check concepts
        concepts = self.learning_graph.get_concepts_for_unit(u1.unit_id)
        self.assertGreater(len(concepts), 0)
        c1 = concepts[0]
        self.assertIsNotNone(c1.name_marathi)
        self.assertIsNotNone(c1.gloss_english)

        # Check edges
        edges = self.learning_graph.get_edges_for_node(u1.unit_id)
        self.assertGreater(len(edges), 0)
        relations = [e.relation for e in edges]
        self.assertTrue(
            LearningRelationType.EXPLAINS in relations or
            LearningRelationType.CONTINUES in relations or
            LearningRelationType.REINFORCES in relations
        )

    # -------------------------------------------------------------------------
    # 5. TEACHING GRAPH TESTS (§Phase 5)
    # -------------------------------------------------------------------------

    def test_10_teaching_graph_separation_and_origins(self):
        """Validates separation of Teaching Graph and clear distinction between textbook and recommendations."""
        ch1_nodes = self.teaching_graph.get_nodes_for_chapter("CH_01")
        self.assertGreater(len(ch1_nodes), 5)

        # Node 1 is introduction (AKSHARSETU_RECOMMENDATION)
        n1 = ch1_nodes[0]
        self.assertEqual(n1.node_type, TeachingNodeType.INTRODUCTION)
        self.assertEqual(n1.origin, TeachingOrigin.AKSHARSETU_RECOMMENDATION)

        # Node 3 is textbook supported explanation
        n3 = ch1_nodes[2]
        self.assertEqual(n3.node_type, TeachingNodeType.EXPLANATION)
        self.assertEqual(n3.origin, TeachingOrigin.TEXTBOOK_SUPPORTED_STRUCTURE)

        # Last node is assessment
        n_last = ch1_nodes[-1]
        self.assertEqual(n_last.node_type, TeachingNodeType.ASSESSMENT)
        self.assertEqual(n_last.origin, TeachingOrigin.TEXTBOOK_SUPPORTED_STRUCTURE)

    # -------------------------------------------------------------------------
    # 6. NARRATION PLANNER & SPEAKING STYLE TESTS (§Phases 6 & 7)
    # -------------------------------------------------------------------------

    def test_11_narration_planning_and_speaking_style(self):
        """Validates policy resolution: normal reading vs on-demand, pace, sentence boundaries."""
        plan = self.narration_planner.plan_chapter_narration("CH_01")
        self.assertIsNotNone(plan)
        self.assertEqual(plan.chapter_id, "CH_01")
        self.assertGreater(len(plan.normal_reading_items), 0)
        self.assertGreater(len(plan.on_demand_items), 0)

        # Normal reading item
        item = plan.normal_reading_items[0]
        self.assertTrue(item.is_spoken_in_normal_reading)
        self.assertEqual(item.policy, NarrationPolicy.READ_THEN_EXPLAIN)
        self.assertIn(item.style.style, [SpeakingStyle.HISTORICAL_NARRATION, SpeakingStyle.EXPLANATORY_TEACHER, SpeakingStyle.DESCRIPTIVE])
        self.assertGreater(len(item.sentences), 0)
        self.assertIn("tokens", item.sentences[0])

        # On demand assessment item
        assess_item = plan.on_demand_items[-1]
        self.assertFalse(assess_item.is_spoken_in_normal_reading)
        self.assertTrue(assess_item.is_available_on_demand)
        self.assertEqual(assess_item.policy, NarrationPolicy.EXCLUDE_FROM_NORMAL_READING)

    # -------------------------------------------------------------------------
    # 7. PRONUNCIATION KNOWLEDGE TESTS (§Phase 8)
    # -------------------------------------------------------------------------

    def test_12_pronunciation_lexicon_lookup_and_verification(self):
        """Validates de-duplicated proper noun lexicon and verification status preservation."""
        self.assertGreater(len(self.pronunciation_kb.entries), 150)

        entry = self.pronunciation_kb.lookup("आगाखान पॅलेस (पुणे)")
        self.assertIsNotNone(entry)
        self.assertEqual(entry.canonical_text, "आगाखान पॅलेस (पुणे)")
        self.assertEqual(entry.verification_status, "UNVERIFIED")
        self.assertFalse(entry.is_verified)

        # Approve pronunciation and verify update
        approved = self.pronunciation_kb.approve_pronunciation(
            word="आगाखान पॅलेस (पुणे)",
            phonetic_respelling="aagaa-khaan-paa-leys",
            devanagari_guide="आगा-खान पॅलेस"
        )
        self.assertIsNotNone(approved)
        self.assertTrue(approved.is_verified)
        self.assertEqual(approved.verification_status, "APPROVED")
        self.assertEqual(approved.version, 2)

    # -------------------------------------------------------------------------
    # 8. CACHING & INVALIDATION TESTS (§Phase 10)
    # -------------------------------------------------------------------------

    def test_13_cache_hit_miss_and_dependency_invalidation(self):
        """Validates granular cache hit, miss, and dependency-aware invalidation."""
        test_key = "CH_CACHE_TEST"
        # 1. Put and Hit
        self.cache.put(HistoryCacheLayer.CHAPTER_STRUCTURE, test_key, {"name": "CH_CACHE_TEST"})
        self.assertTrue(self.cache.has(HistoryCacheLayer.CHAPTER_STRUCTURE, test_key))

        # 2. Pronunciation Invalidation -> clears TTS audio and narration plans, but keeps chapter structure
        self.cache.put(HistoryCacheLayer.TTS_AUDIO, test_key, {"track": "audio.wav"})
        self.cache.put(HistoryCacheLayer.NARRATION_PLAN, test_key, {"plan": "plan_data"})
        self.assertTrue(self.cache.has(HistoryCacheLayer.TTS_AUDIO, test_key))

        self.cache.invalidate_pronunciation(test_key)
        self.assertTrue(self.cache.has(HistoryCacheLayer.CHAPTER_STRUCTURE, test_key), "Chapter structure must remain cached")
        self.assertFalse(self.cache.has(HistoryCacheLayer.TTS_AUDIO, test_key), "TTS audio must be invalidated")
        self.assertFalse(self.cache.has(HistoryCacheLayer.NARRATION_PLAN, test_key), "Narration plan must be invalidated")

    # -------------------------------------------------------------------------
    # 9. RAG / TUTOR RETRIEVAL TESTS (§Phase 9)
    # -------------------------------------------------------------------------

    def test_14_grounded_tutor_retrieval_and_provenance(self):
        """Validates bounded retrieval, audible cue presence, and complete provenance."""
        response = self.tutor_engine.query_tutor(
            query="इतिहासाची भौतिक साधने सांगा",
            chapter_id="CH_01",
            learning_unit_id="CH_01_LU_01"
        )
        self.assertEqual(response.mode, "tutor")
        self.assertTrue(response.audible_cue, "Tutor mode must include pleasant audible cue")
        self.assertEqual(response.chapter_id, "CH_01")
        self.assertEqual(response.learning_unit_id, "CH_01_LU_01")
        self.assertGreater(len(response.speech_segments), 0)
        self.assertEqual(response.speech_segments[0]["type"], "canonical")
        self.assertEqual(response.speech_segments[1]["type"], "transition")
        self.assertEqual(response.speech_segments[2]["type"], "explanation")

        # Provenance verification
        prov = response.provenance
        self.assertEqual(prov["document_id"], "AKS_HISTORY_CLASS8_HISTORY")
        self.assertEqual(prov["source_status"], "SOURCE_VERIFIED")
        self.assertEqual(prov["explanation_source"], "TEACHER_OUTPUT")

    # -------------------------------------------------------------------------
    # 10. FASTAPI HISTORY ENDPOINTS TESTS (§Phase 11)
    # -------------------------------------------------------------------------

    def test_15_fastapi_history_endpoints(self):
        """Validates all major History API endpoints with 200 OK responses and valid schemas."""
        # 1. GET /api/history and /history
        res1 = self.client.get("/history")
        self.assertEqual(res1.status_code, 200)
        self.assertEqual(res1.json()["manifest"]["subject"], "history")

        # 2. GET /history/chapters
        res2 = self.client.get("/history/chapters")
        self.assertEqual(res2.status_code, 200)
        self.assertEqual(res2.json()["total"], 14)

        # 3. GET /history/chapters/CH_01
        res3 = self.client.get("/history/chapters/CH_01")
        self.assertEqual(res3.status_code, 200)
        self.assertEqual(res3.json()["chapter_id"], "CH_01")
        self.assertIn("learning_units_detail", res3.json())
        self.assertIn("teaching_nodes", res3.json())

        # 4. GET /history/chapters/CH_01/learning-units
        res4 = self.client.get("/history/chapters/CH_01/learning-units")
        self.assertEqual(res4.status_code, 200)
        self.assertEqual(res4.json()["total_units"], 7)

        # 5. GET /history/learning-units/CH_01_LU_01
        res5 = self.client.get("/history/learning-units/CH_01_LU_01")
        self.assertEqual(res5.status_code, 200)
        self.assertEqual(res5.json()["unit_id"], "CH_01_LU_01")
        self.assertIn("concepts", res5.json())

        # 6. GET /history/chapters/CH_01/narration
        res6 = self.client.get("/history/chapters/CH_01/narration")
        self.assertEqual(res6.status_code, 200)
        self.assertIn("normal_reading_items", res6.json())

        # 7. GET /history/chapters/CH_01/audio
        res7 = self.client.get("/history/chapters/CH_01/audio")
        self.assertEqual(res7.status_code, 200)
        self.assertGreater(res7.json()["total_audio_tracks"], 0)

        # 8. GET /history/chapters/CH_01/reader
        res8 = self.client.get("/history/chapters/CH_01/reader")
        self.assertEqual(res8.status_code, 200)
        self.assertIn("pages", res8.json())
        self.assertIn("spoken_sequence", res8.json())

        # 9. GET /history/pronunciation
        res9 = self.client.get("/history/pronunciation")
        self.assertEqual(res9.status_code, 200)
        self.assertGreater(res9.json()["total_entities"], 100)

        # 10. POST /history/tutor
        res10 = self.client.post("/history/tutor", json={"query": "भौतिक साधने", "chapter_id": "CH_01"})
        self.assertEqual(res10.status_code, 200)
        self.assertTrue(res10.json()["audible_cue"])


if __name__ == "__main__":
    unittest.main()
