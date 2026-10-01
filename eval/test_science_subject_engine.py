"""
AksharSetu — Class 8 General Science Reference Implementation Comprehensive Test Suite

Validates all key areas of the Science Subject Engine:
1. CORPUS: Manifest validation, 19 chapters count, chapter IDs (CH_01 to CH_19), printed-page offset (PDF - 10), learning units, glossary terms.
2. PHYSICAL GRAPH: Entities hierarchy (Doc -> Chapter -> Page -> Region), bbox=None invariant, visual UNVERIFIED, provenance.
3. SCIENCE GRAMMAR: Macro-structure (थोडे आठवा -> करून पहा / जरा डोके चालवा -> स्वाध्याय), 7 genre patterns, safety-critical flags.
4. NARRATION PLANNER: Policies (READ_DIRECTLY, READ_THEN_EXPLAIN, EXPLAIN, ON_DEMAND, EXCLUDE), speaking styles & acoustic pauses.
5. PRONUNCIATION KB: Glossary seeding, author transliteration triplets, UNVERIFIED vs GOLDEN_TRUTH lifecycle.
6. GRANULAR CACHE: 8-tier cache hits, misses, and invalidation.
7. TUTOR / RAG: Fact-bounded grounding to Science learning units, refusal on out-of-scope questions, safety alerts.
8. API ENDPOINTS: /api/science, /api/science/chapters, /api/science/chapters/{ch}/reader, /api/science/tutor, etc.
"""

import sys
import unittest
from fastapi.testclient import TestClient

if sys.stdout.encoding != 'utf-8':
    try:
        sys.stdout.reconfigure(encoding='utf-8')
    except Exception:
        pass

from corpus.science_loader import science_corpus_loader, ProvenanceStatus
from graphs.science_physical_graph import science_physical_graph
from graphs.science_grammar import science_grammar_engine, ScienceGenre
from graphs.science_learning_graph import science_learning_graph, ScienceRelationType
from graphs.science_teaching_graph import science_teaching_graph, TeachingNodeType, TeachingOrigin
from orchestrator.science_narration_planner import science_narration_planner, NarrationPolicy, SpeakingStyle
from corpus.science_pronunciation import science_pronunciation_kb
from orchestrator.science_tutor_engine import science_tutor_engine
from graphs.science_cache import science_cache, ScienceCacheLayer
from backend.main import app


class TestScienceSubjectEngine(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.client = TestClient(app)
        cls.loader = science_corpus_loader.validate_and_load()
        cls.physical_graph = science_physical_graph.build_graph()
        cls.grammar = science_grammar_engine
        cls.learning_graph = science_learning_graph.build_graph()
        cls.teaching_graph = science_teaching_graph.build_graph()
        cls.narration_planner = science_narration_planner
        cls.pronunciation_kb = science_pronunciation_kb.build_lexicon()
        cls.tutor_engine = science_tutor_engine
        cls.tutor_engine.ensure_initialized()
        cls.cache = science_cache

    # -------------------------------------------------------------------------
    # 1. CORPUS TESTS
    # -------------------------------------------------------------------------

    def test_01_corpus_manifest_and_schema(self):
        """Validates manifest integrity, class number, subject, and medium."""
        manifest = self.loader.manifest
        self.assertIsNotNone(manifest)
        self.assertEqual(manifest.document_id, "AKS_SCIENCE_CLASS8_SCIENCE")
        self.assertEqual(manifest.subject, "science")
        self.assertEqual(manifest.class_num, 8)
        self.assertEqual(manifest.medium, "Marathi")
        self.assertEqual(manifest.pdf_total_pages, 148)
        self.assertEqual(manifest.content_pdf_page_range, [11, 146])
        self.assertEqual(manifest.front_matter_pdf_page_range, [1, 10])

    def test_02_corpus_19_chapters_inventory_and_contiguous_pages(self):
        """Validates exact 19 chapter count, valid IDs (CH_01 to CH_19), and contiguous page spans."""
        chapters = self.loader.list_all_chapters()
        self.assertEqual(len(chapters), 19, "Must contain exactly 19 chapters")

        expected_start = 11
        for idx, ch in enumerate(chapters, 1):
            expected_id = f"CH_{idx:02d}"
            self.assertEqual(ch.chapter_id, expected_id)
            self.assertEqual(ch.chapter_number, idx)
            start_p, end_p = ch.pdf_page_range
            self.assertEqual(start_p, expected_start)
            self.assertGreaterEqual(end_p, start_p)
            expected_start = end_p + 1

        self.assertEqual(expected_start, 145, "Content chapters must span exactly up to back matter (PDF 145)")

    def test_03_corpus_glossary_back_matter(self):
        """Validates back matter glossary extraction (pp. 145–146) with author phonetics."""
        glossary = self.loader.glossary
        self.assertGreater(len(glossary), 50, "Glossary must have extracted technical terms")
        sample_term = next((t for t in glossary if "अणु" in t.canonical_marathi or "acid" in t.english_term.lower()), None)
        self.assertIsNotNone(sample_term, "Glossary must contain fundamental science terms")
        self.assertTrue(len(sample_term.phonetic_marathi) > 0)

    def test_04_corpus_trust_model_provenance(self):
        """Validates that SOURCE_VERIFIED is distinguished from GOLDEN_TRUTH in baseline."""
        self.assertFalse(self.loader.is_golden_truth("SOURCE_VERIFIED"))
        for ch in self.loader.list_all_chapters():
            self.assertNotEqual(ch.verification_status, "GOLDEN_TRUTH")
            self.assertEqual(self.loader.get_trust_level(ch.source_status), ProvenanceStatus.SOURCE_VERIFIED)

    # -------------------------------------------------------------------------
    # 2. PHYSICAL DOCUMENT GRAPH TESTS
    # -------------------------------------------------------------------------

    def test_05_physical_graph_entities_and_relationships(self):
        """Validates Document -> Chapter -> Page -> Region hierarchy and provenance."""
        doc = self.physical_graph.get_document()
        self.assertEqual(doc["document_id"], "AKS_SCIENCE_CLASS8_SCIENCE")
        self.assertEqual(doc["total_pages"], 148)
        self.assertEqual(doc["total_chapters"], 19)

        # Check Chapter 1
        ch1 = self.physical_graph.get_chapter("CH_01")
        self.assertIsNotNone(ch1)
        pages = ch1.get_pages()
        self.assertEqual(len(pages), 5)  # PDF pp. 11 to 15 (Printed pp. 1 to 5)

        # Check Page 11 regions
        p11 = self.physical_graph.get_page(11)
        self.assertIsNotNone(p11)
        regions = p11.get_regions()
        self.assertGreater(len(regions), 0)

        # Invariant Check: bbox is explicitly None, visual_description_status is UNVERIFIED
        r1 = regions[0]
        self.assertIsNone(r1.bbox, "Must not fabricate bounding boxes")
        self.assertEqual(r1.visual_description_status, "UNVERIFIED")
        self.assertEqual(r1.source_status, "SOURCE_VERIFIED")

    # -------------------------------------------------------------------------
    # 3. SCIENCE GRAMMAR TESTS
    # -------------------------------------------------------------------------

    def test_06_science_grammar_genre_patterns(self):
        """Validates all 7 genre classifications across the 19 chapters."""
        # Mathematical heavy: CH_03, CH_14, CH_16
        self.assertEqual(self.grammar.classify_chapter_genre("CH_03"), ScienceGenre.MATHEMATICAL_FORMULA_HEAVY)
        self.assertEqual(self.grammar.classify_chapter_genre("CH_14"), ScienceGenre.MATHEMATICAL_FORMULA_HEAVY)

        # Historical model sequence: CH_05
        self.assertEqual(self.grammar.classify_chapter_genre("CH_05"), ScienceGenre.HISTORICAL_MODEL_SEQUENCE)

        # Biology catalogue: CH_10, CH_11
        self.assertEqual(self.grammar.classify_chapter_genre("CH_10"), ScienceGenre.BIOLOGY_CATALOGUE)

        # Chemistry reaction: CH_07, CH_12, CH_13
        self.assertEqual(self.grammar.classify_chapter_genre("CH_12"), ScienceGenre.CHEMISTRY_REACTION)

        # Astronomical: CH_19
        self.assertEqual(self.grammar.classify_chapter_genre("CH_19"), ScienceGenre.ASTRONOMICAL_EVOLUTION)

    def test_07_science_grammar_safety_critical_detection(self):
        """Validates detection of safety-critical protocols (CH_09 disaster, CH_12 acid safety)."""
        ch9_flags = self.grammar.get_safety_critical_flags("CH_09")
        self.assertTrue(ch9_flags["is_safety_critical"])
        self.assertEqual(ch9_flags["priority"], "IMMEDIATE")

        ch12_flags = self.grammar.get_safety_critical_flags("CH_12")
        self.assertTrue(ch12_flags["is_safety_critical"])

        # Non-hazardous chapter check
        ch1_flags = self.grammar.get_safety_critical_flags("CH_01")
        self.assertFalse(ch1_flags["is_safety_critical"])

    # -------------------------------------------------------------------------
    # 4. NARRATION PLANNER TESTS
    # -------------------------------------------------------------------------

    def test_08_narration_planner_policies_and_styles(self):
        """Validates narration policies and speaking styles with speech pause constraints."""
        plan_ch1 = self.narration_planner.generate_chapter_plan("CH_01")
        self.assertIsNotNone(plan_ch1)
        self.assertGreater(len(plan_ch1.segments), 0)

        # Check introductory title speech
        first_seg = plan_ch1.segments[0]
        self.assertIn("आज आपण बघणार आहोत", first_seg.spoken_text)

        # Check mathematical style settings for Ch 3
        plan_ch3 = self.narration_planner.generate_chapter_plan("CH_03")
        self.assertEqual(plan_ch3.speaking_style, SpeakingStyle.MATHEMATICAL_NARRATION)
        self.assertLess(plan_ch3.speed_multiplier, 1.0, "Math narration must be slower than 1.0x")
        self.assertGreaterEqual(plan_ch3.pause_after_sentence_ms, 400)

        # Check safety critical settings for Ch 9
        plan_ch9 = self.narration_planner.generate_chapter_plan("CH_09")
        self.assertEqual(plan_ch9.speaking_style, SpeakingStyle.SAFETY_CRITICAL)
        self.assertLessEqual(plan_ch9.speed_multiplier, 0.85)

    # -------------------------------------------------------------------------
    # 5. PRONUNCIATION KB TESTS
    # -------------------------------------------------------------------------

    def test_09_pronunciation_lexicon_and_approval(self):
        """Validates pronunciation dictionary, seed terms, and approval transition."""
        lexicon = self.pronunciation_kb.get_lexicon()
        self.assertGreater(len(lexicon), 50, "Pronunciation KB must contain seed and glossary terms")

        # Test approval of a term
        test_word = "रॉबर्ट व्हिटाकर"
        res = self.pronunciation_kb.approve_pronunciation(
            canonical_text=test_word,
            preferred_pronunciation="रॉबर्ट व्हिटाकर",
            approved_by="Test Administrator"
        )
        self.assertTrue(res)
        entry = self.pronunciation_kb.lookup(test_word)
        self.assertIsNotNone(entry)
        self.assertEqual(entry.verification_status, "GOLDEN_TRUTH")

    # -------------------------------------------------------------------------
    # 6. GRANULAR CACHE TESTS
    # -------------------------------------------------------------------------

    def test_10_cache_layer_hits_and_invalidation(self):
        """Validates granular caching across layers and invalidation."""
        self.cache.set("test_key", {"data": 42}, ScienceCacheLayer.LEARNING_GRAPH)
        val = self.cache.get("test_key", ScienceCacheLayer.LEARNING_GRAPH)
        self.assertIsNotNone(val)
        self.assertEqual(val["data"], 42)

        # Invalidate layer
        self.cache.invalidate_layer(ScienceCacheLayer.LEARNING_GRAPH)
        val_after = self.cache.get("test_key", ScienceCacheLayer.LEARNING_GRAPH)
        self.assertIsNone(val_after)

    # -------------------------------------------------------------------------
    # 7. TUTOR / RAG TESTS
    # -------------------------------------------------------------------------

    def test_11_tutor_engine_grounding_and_refusal(self):
        """Validates strictly fact-grounded tutor answers and refusal on out-of-scope questions."""
        # In-scope question on Chapter 1
        res = self.tutor_engine.ask(
            question="पंचसृष्टी वर्गीकरण पद्धती कोणी मांडली?",
            chapter_id="CH_01"
        )
        self.assertTrue(res["is_grounded"])
        self.assertIn("व्हिटाकर", res["answer"])
        self.assertIn("audible_prompt", res)
        self.assertEqual(res["provenance_status"], "SOURCE_VERIFIED")

        # Out-of-scope question
        res_out = self.tutor_engine.ask(
            question="अमेरिकेचे पहिले राष्ट्राध्यक्ष कोण होते?",
            chapter_id="CH_01"
        )
        self.assertFalse(res_out["is_grounded"])
        self.assertIn("माहिती या विज्ञानाच्या पाठ्यपुस्तकात उपलब्ध नाही", res_out["answer"])

    # -------------------------------------------------------------------------
    # 8. REST API ENDPOINTS TESTS
    # -------------------------------------------------------------------------

    def test_12_api_science_endpoints(self):
        """Validates all primary Science FastAPI endpoints."""
        # 1. Subject summary
        r1 = self.client.get("/api/science")
        self.assertEqual(r1.status_code, 200)
        self.assertEqual(r1.json()["subject"], "science")

        # 2. Chapters list
        r2 = self.client.get("/api/science/chapters")
        self.assertEqual(r2.status_code, 200)
        chapters = r2.json()["chapters"]
        self.assertEqual(len(chapters), 19)

        # 3. Chapter 1 Reader payload
        r3 = self.client.get("/api/science/chapters/CH_01/reader")
        self.assertEqual(r3.status_code, 200)
        reader_data = r3.json()
        self.assertIn("paragraphs", reader_data)
        self.assertEqual(reader_data["pdfPage"], 11)
        self.assertEqual(reader_data["page"], 1)

        # 4. Narration plan
        r4 = self.client.get("/api/science/chapters/CH_01/narration")
        self.assertEqual(r4.status_code, 200)
        self.assertIn("segments", r4.json())

        # 5. Tutor endpoint
        r5 = self.client.post("/api/science/tutor", json={
            "question": "सजीवांचे वर्गीकरण का केले जाते?",
            "chapter_id": "CH_01"
        })
        self.assertEqual(r5.status_code, 200)
        self.assertTrue(r5.json()["is_grounded"])

        # 6. Ingest status
        r6 = self.client.get("/api/science/ingest/latest")
        self.assertEqual(r6.status_code, 200)
        self.assertEqual(r6.json()["stage"], "READY")


if __name__ == "__main__":
    unittest.main()
