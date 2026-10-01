"""
End-to-End Validation Test: PDF-Document-First Architecture
Tests:
1. Document Structure Analysis for Marathi & Geography reference textbooks
2. Page Inventory distinction: physical PDF page vs printed page
3. Chapter 1 segmentation & boundary metadata
4. Physical Document Graph construction & reading order
5. Learning Graph construction & semantic relations
6. Architectural Invariant Assertion: validate_region_learning_chain
7. FastAPI endpoint responses
"""

import os
import sys
import unittest
from fastapi.testclient import TestClient

from backend.main import app, corpus_mgr
from ingestion.pdf_structure import DocumentStructureAnalyzer
from ingestion.chapter_processor import ChapterProcessor

class TestPDFDocumentFirstPipeline(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.client = TestClient(app)
        cls.analyzer = DocumentStructureAnalyzer()
        cls.processor = ChapterProcessor(corpus_manager=corpus_mgr)

    def test_01_marathi_document_structure(self):
        """Validates whole-document ingestion for Marathi 10th textbook."""
        path = os.path.join("dataset", "AksharBharti-Marathi-10th-English-Medium-.pdf")
        self.assertTrue(os.path.exists(path), f"Dataset file missing: {path}")

        struct = self.analyzer.analyze_document(path)
        self.assertEqual(struct.document_id, "akshar-10")
        self.assertEqual(struct.subject, "Marathi")
        self.assertEqual(struct.total_pages, 90)
        self.assertEqual(struct.front_matter_pages_count, 9)
        self.assertEqual(struct.offset_to_printed_pages, 9)
        self.assertTrue(len(struct.chapters) >= 1)

        # Invariant: PDF page != Printed page
        p10 = struct.page_inventory[9] # 0-indexed 9 is PDF page 10
        self.assertEqual(p10.pdf_page_number, 10)
        self.assertEqual(p10.printed_page_number, 1)

        # Chapter 1 boundary
        ch1 = struct.chapters[0]
        self.assertEqual(ch1.number, 1)
        self.assertEqual(ch1.start_pdf_page, 10)
        self.assertEqual(ch1.end_pdf_page, 10)
        self.assertEqual(ch1.printed_start_page, 1)
        self.assertEqual(ch1.printed_end_page, 1)

    def test_02_geography_document_structure(self):
        """Validates whole-document ingestion for Geography 10th textbook."""
        path = os.path.join("dataset", "SSC-10th-Class-Geography-Textbook-in-Marathi.pdf")
        self.assertTrue(os.path.exists(path), f"Dataset file missing: {path}")

        struct = self.analyzer.analyze_document(path)
        self.assertEqual(struct.document_id, "geo-10")
        self.assertEqual(struct.subject, "Geography")
        self.assertEqual(struct.total_pages, 82)
        self.assertEqual(struct.front_matter_pages_count, 11)
        self.assertEqual(struct.offset_to_printed_pages, 11)
        self.assertTrue(len(struct.chapters) >= 1)

        # Invariant: PDF page != Printed page
        p12 = struct.page_inventory[11] # PDF page 12
        self.assertEqual(p12.pdf_page_number, 12)
        self.assertEqual(p12.printed_page_number, 1)

        # Chapter 1 boundary (Field visit: 8 pages)
        ch1 = struct.chapters[0]
        self.assertEqual(ch1.number, 1)
        self.assertEqual(ch1.start_pdf_page, 12)
        self.assertEqual(ch1.end_pdf_page, 19)
        self.assertEqual(ch1.printed_start_page, 1)
        self.assertEqual(ch1.printed_end_page, 8)
        self.assertEqual(ch1.page_count, 8)

    def test_03_chapter1_processing_and_graph_invariants(self):
        """Validates Chapter 1 processing: Physical Graph, Learning Graph, and Invariants."""
        m_path = os.path.join("dataset", "AksharBharti-Marathi-10th-English-Medium-.pdf")
        m_struct = self.analyzer.analyze_document(m_path)
        m_res = self.processor.process_chapter(m_struct, "ch_1")

        self.assertTrue(m_res.invariant_valid)
        self.assertEqual(m_res.total_regions, 12)
        self.assertEqual(m_res.corpus_records_count, 9)
        self.assertEqual(m_res.start_pdf_page, 10)
        self.assertEqual(m_res.printed_start_page, 1)

        # Geography Chapter 1
        g_path = os.path.join("dataset", "SSC-10th-Class-Geography-Textbook-in-Marathi.pdf")
        g_struct = self.analyzer.analyze_document(g_path)
        g_res = self.processor.process_chapter(g_struct, "ch_1")

        self.assertTrue(g_res.invariant_valid)
        self.assertEqual(g_res.total_regions, 244)
        self.assertEqual(g_res.corpus_records_count, 203)
        self.assertEqual(g_res.start_pdf_page, 12)
        self.assertEqual(g_res.printed_start_page, 1)

    def test_04_fastapi_endpoints(self):
        """Validates API endpoints for documents, analyze, and chapter processing."""
        # 1. GET /api/documents
        res_docs = self.client.get("/api/documents")
        self.assertEqual(res_docs.status_code, 200)
        docs = res_docs.json()["documents"]
        self.assertTrue(any(d["doc_id"] == "akshar-10" for d in docs))
        self.assertTrue(any(d["doc_id"] == "geo-10" for d in docs))

        # 2. POST /api/document/analyze
        res_analyze = self.client.post("/api/document/analyze", json={"doc_id": "akshar-10"})
        self.assertEqual(res_analyze.status_code, 200)
        struct_data = res_analyze.json()
        self.assertEqual(struct_data["document_id"], "akshar-10")
        self.assertEqual(struct_data["total_pages"], 90)

        # 3. POST /api/chapter/process
        res_ch = self.client.post("/api/chapter/process", json={"doc_id": "akshar-10", "chapter_id": "ch_1"})
        self.assertEqual(res_ch.status_code, 200)
        data = res_ch.json()
        self.assertEqual(data["status"], "success")
        self.assertTrue(data["result"]["invariant_valid"])
        self.assertEqual(data["result"]["start_pdf_page"], 10)
        self.assertEqual(data["result"]["printed_start_page"], 1)

if __name__ == "__main__":
    unittest.main()
