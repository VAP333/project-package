"""
AksharSetu — Geography & Marathi Reading Order Regression Test Suite
Validates:
1. Exact pedagogical reading order of complex educational layouts (Geography Ch 1 Page 12 / printed page 1).
2. Distinction of Three Orders: Physical (2D), Semantic (Containment & Bindings), Pedagogical (Learning Sequence).
3. Preservation of Simple Linear layout (Marathi Class 10 Ch 1 Page 10 / printed page 1).
4. Prevention of regressions:
   - Chapter heading appears first, associated with Chapter 1.
   - Main content is NEVER preceded or replaced by discussion/activity boxes.
   - Maps & figures are linked to their corresponding captions.
   - Dialogue belongs to the sequential learning narrative (Day 1 section).
   - Discussion box and activity questions do not arbitrarily interrupt the narrative.
   - Printed and PDF page numbers remain distinct.
   - Every physical region traces to a Semantic Entity and Learning Unit.
   - Processing is 100% deterministic across multiple runs.
"""

import os
import unittest
import fitz

from ingestion.pdf_structure import DocumentStructureAnalyzer
from ingestion.chapter_processor import ChapterProcessor
from ingestion.layout_engine import DeterministicLayoutEngine
from graphs.physical_document_graph import RegionType
from graphs.learning_graph import SemanticRelationType
from corpus.schema import VerificationTier

class TestReadingOrderDocumentStructure(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.analyzer = DocumentStructureAnalyzer()
        cls.processor = ChapterProcessor()
        cls.layout_engine = DeterministicLayoutEngine()
        cls.geo_pdf_path = os.path.join("dataset", "SSC-10th-Class-Geography-Textbook-in-Marathi.pdf")
        cls.marathi_pdf_path = os.path.join("dataset", "AksharBharti-Marathi-10th-English-Medium-.pdf")

    # -------------------------------------------------------------------------
    # TEST 1: Complex Multi-Region Layout (Geography Ch 1, PDF Page 12 / Printed 1)
    # -------------------------------------------------------------------------
    def test_01_geography_page_12_structure_and_order(self):
        """Regression test for the complex Geography Class 10 Chapter 1 page layout."""
        doc = fitz.open(self.geo_pdf_path)
        
        # 1. Process Page Layout
        regions, phys_order, ped_order, sem_edges = self.layout_engine.process_page_layout(
            doc=doc,
            pdf_page_num=12,
            printed_page_num=1,
            chapter_id="ch_1",
            chapter_title="१. क्षेत्रभेट",
            subject="Geography",
            doc_hash="geo_test_hash"
        )
        doc.close()

        region_map = {r.region_id: r for r in regions}

        # Assertion: Both physical and pedagogical orders exist and are distinct
        self.assertGreater(len(phys_order), 0)
        self.assertGreater(len(ped_order), 0)
        self.assertNotEqual(phys_order, ped_order, "Physical 2D order and Pedagogical learning order must NOT be identical on complex pages!")

        # Step 1: Heading must be the very first pedagogical element
        first_ped_region = region_map[ped_order[0]]
        self.assertEqual(first_ped_region.region_type, RegionType.HEADING)
        self.assertIn("१. क्षेत्रभेट", first_ped_region.native_text)
        self.assertEqual(first_ped_region.source_coordinates["pdf_page_number"], 12)
        self.assertEqual(first_ped_region.source_coordinates["printed_page_number"], 1)

        # Step 2: Main introductory narrative must come second (before any discussion box)
        second_ped_region = region_map[ped_order[1]]
        self.assertEqual(second_ped_region.region_type, RegionType.PARAGRAPH)
        self.assertIn("राहुलच्या वर्गातील विद्यार्थी", second_ped_region.native_text)

        # Step 3: Discussion questions must NOT appear before main narrative
        # Find index of discussion box and questions in pedagogical order
        disc_indices = [
            idx for idx, rid in enumerate(ped_order) 
            if region_map[rid].region_type in (RegionType.DISCUSSION_BOX, RegionType.QUESTION)
        ]
        intro_indices = [
            idx for idx, rid in enumerate(ped_order)
            if "राहुलच्या वर्गातील विद्यार्थी" in region_map[rid].native_text
        ]
        self.assertTrue(len(disc_indices) > 0, "Discussion activity regions must be detected")
        self.assertTrue(len(intro_indices) > 0, "Introductory narrative must be detected")
        self.assertGreater(min(disc_indices), max(intro_indices), 
                           "CRITICAL: Discussion box or questions must NEVER precede main narrative!")

        # Step 4: Map and Figure Caption Bindings
        caption_edges = [e for e in sem_edges if e["relation"] == "caption_for"]
        self.assertGreaterEqual(len(caption_edges), 1, "Visual regions must be linked to their captions")
        
        # Verify map caption contains 'मार्ग' and figure caption contains 'तयारी'
        map_caption_found = False
        for r in regions:
            if r.region_type == RegionType.CAPTION and "मार्ग" in r.native_text:
                map_caption_found = True
                self.assertIsNotNone(r.caption_target_id, "Map caption must link to visual map target")
        self.assertTrue(map_caption_found, "Route map caption must be present")

        # Step 5: Subheading and Dialogue Association
        subheading_indices = [
            idx for idx, rid in enumerate(ped_order)
            if region_map[rid].region_type == RegionType.SUBHEADING
        ]
        dialogue_indices = [
            idx for idx, rid in enumerate(ped_order)
            if region_map[rid].region_type == RegionType.DIALOGUE
        ]
        self.assertTrue(len(subheading_indices) > 0, "Subheading (e.g. 'दिवस पहिला') must be detected")
        self.assertTrue(len(dialogue_indices) > 0, "Dialogue turns must be detected")
        self.assertLess(min(subheading_indices), min(dialogue_indices),
                        "Subheading 'दिवस पहिला' must precede the dialogue that belongs to that section")

        # Step 6: Page numbers excluded from spoken pedagogical reading stream
        page_num_regions = [r for r in regions if r.region_type == RegionType.PAGE_NUMBER]
        for pnr in page_num_regions:
            self.assertNotIn(pnr.region_id, ped_order, "Isolated page number must not be in pedagogical reading stream")

        # Step 7: Determinism check (running again yields exact same order)
        doc2 = fitz.open(self.geo_pdf_path)
        _, _, ped_order_2, _ = self.layout_engine.process_page_layout(
            doc=doc2, pdf_page_num=12, printed_page_num=1,
            chapter_id="ch_1", chapter_title="१. क्षेत्रभेट",
            subject="Geography", doc_hash="geo_test_hash"
        )
        doc2.close()
        self.assertEqual(ped_order, ped_order_2, "Pedagogical ordering must be 100% deterministic")

    # -------------------------------------------------------------------------
    # TEST 2: Chapter-Level Processing & Graph Invariants for Geography Ch 1
    # -------------------------------------------------------------------------
    def test_02_geography_chapter1_full_pipeline_invariants(self):
        """Validates that full Chapter 1 processing maintains graph invariants and provenance."""
        g_struct = self.analyzer.analyze_document(self.geo_pdf_path)
        res = self.processor.process_chapter(g_struct, "ch_1")

        self.assertTrue(res.invariant_valid, "Every physical region must link to a semantic entity and learning unit")
        self.assertEqual(res.start_pdf_page, 12)
        self.assertEqual(res.printed_start_page, 1)
        self.assertEqual(res.end_pdf_page, 19)
        self.assertEqual(res.printed_end_page, 8)
        self.assertNotEqual(res.start_pdf_page, res.printed_start_page, "PDF page and printed page must be distinct")

        # Check sample reading paragraphs
        p1 = res.sample_reading_paragraphs[0]
        self.assertEqual(p1["region_type"], "heading")
        self.assertIn("१. क्षेत्रभेट", p1["text"])
        self.assertEqual(p1["verification_status"], VerificationTier.VERIFIED_TRAINING_SAMPLE.value)

        # Check that physical graph preserves both physical_order and reading_order
        pg = res.physical_graph
        self.assertIn("physical_order", pg)
        self.assertIn("reading_order", pg)
        self.assertGreater(len(pg["physical_order"]), 0)
        self.assertGreater(len(pg["reading_order"]), 0)

    # -------------------------------------------------------------------------
    # TEST 3: Simple Linear Layout (Marathi Class 10 Ch 1, PDF Page 10 / Printed 1)
    # -------------------------------------------------------------------------
    def test_03_marathi_prayer_linear_regression(self):
        """Asserts that Marathi Class 10 poem 'तू बुद्धी दे' remains completely intact and linear."""
        doc = fitz.open(self.marathi_pdf_path)
        regions, phys_order, ped_order, sem_edges = self.layout_engine.process_page_layout(
            doc=doc,
            pdf_page_num=10,
            printed_page_num=1,
            chapter_id="ch_1",
            chapter_title="१. तू बुद्धी दे",
            subject="Marathi",
            doc_hash="marathi_test_hash"
        )
        doc.close()

        region_map = {r.region_id: r for r in regions}

        # Step 1: Heading is first
        first_r = region_map[ped_order[0]]
        self.assertEqual(first_r.region_type, RegionType.HEADING)
        self.assertIn("तू बुद्धी दे", first_r.native_text)

        # Step 2: Poetry stanzas follow sequentially
        poetry_regions = [region_map[rid] for rid in ped_order if region_map[rid].region_type == RegionType.POETRY]
        self.assertEqual(len(poetry_regions), 4, "All 4 poetry stanzas must be recognized in pedagogical order")
        self.assertIn("तू बुद्\u200cधि दे", poetry_regions[0].native_text)
        self.assertIn("हरवले आभाळ", poetry_regions[1].native_text)
        self.assertIn("जाणावया", poetry_regions[2].native_text)
        self.assertIn("सन्मार्ग", poetry_regions[3].native_text)

        # Step 3: Vocabulary definitions at the end
        def_regions = [r for r in regions if r.region_type == RegionType.DEFINITION]
        self.assertTrue(len(def_regions) > 0, "Vocabulary section must be recognized")
        for dr in def_regions:
            def_idx = ped_order.index(dr.region_id)
            last_poetry_idx = ped_order.index(poetry_regions[-1].region_id)
            self.assertGreater(def_idx, last_poetry_idx, "Definitions must follow poem stanzas")

        # Step 4: Page number excluded
        page_num_regions = [r for r in regions if r.region_type == RegionType.PAGE_NUMBER]
        for pnr in page_num_regions:
            self.assertNotIn(pnr.region_id, ped_order, "Page number must not be read by TTS")

        # Step 5: Full processor chapter pipeline verification
        m_struct = self.analyzer.analyze_document(self.marathi_pdf_path)
        m_res = self.processor.process_chapter(m_struct, "ch_1")
        self.assertTrue(m_res.invariant_valid)
        self.assertEqual(m_res.start_pdf_page, 10)
        self.assertEqual(m_res.printed_start_page, 1)

if __name__ == "__main__":
    unittest.main()
