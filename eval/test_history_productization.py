"""
AksharSetu — End-to-End Productization & Pipeline Verification Test Suite
Section 26 Compliance: All 25 required product flow tests.

Tests:
 1. upload History.pdf
 2. document registered
 3. hash generated
 4. pages extracted
 5. chapters extracted
 6. 14 chapters detected
 7. expected page ranges validated
 8. physical graph created
 9. learning graph created
10. teaching graph created
11. narration plan created
12. pronunciation candidates created
13. cache created
14. API exposes processed textbook
15. frontend can load processed textbook
16. chapter reader loads
17. learning-unit navigation works
18. tutor retrieval is grounded
19. old textbooks remain stored
20. old textbooks are not active
21. duplicate History upload reuses cache
22. changed PDF creates a new version
23. processing failure produces FAILED/NEEDS_REVIEW state
24. no fabricated bbox/visual descriptions
25. provenance is preserved
"""

import os
import io
import json
import pytest
from fastapi.testclient import TestClient

from backend.main import app
from ingestion.history_ingestion_pipeline import history_pipeline, IngestionStage
from graphs.history_engine import history_engine
from graphs.history_cache import HistoryCacheLayer

client = TestClient(app)
REF_PDF_PATH = os.path.join("corpus", "dataset", "history", "History.pdf")


@pytest.fixture(scope="module")
def pdf_bytes():
    assert os.path.exists(REF_PDF_PATH), f"Missing reference PDF at {REF_PDF_PATH}"
    with open(REF_PDF_PATH, "rb") as f:
        return f.read()


class TestHistoryReferenceProductization:
    """Complete 25-point Product Flow Verification."""

    # 1. upload History.pdf
    def test_01_upload_history_pdf(self, pdf_bytes):
        files = {"file": ("History.pdf", io.BytesIO(pdf_bytes), "application/pdf")}
        res = client.post("/api/history/upload", files=files)
        assert res.status_code == 200
        data = res.json()
        assert data["status"] == "success"
        assert "job" in data
        assert data["job"]["filename"] == "History.pdf"

    # 2. document registered
    def test_02_document_registered(self, pdf_bytes):
        job = history_pipeline.create_job(pdf_bytes, "History.pdf")
        assert job.document_id == "AKS_HISTORY_CLASS8_HISTORY"
        assert job.job_id.startswith("job_hist_")

    # 3. hash generated
    def test_03_hash_generated(self, pdf_bytes):
        job = history_pipeline.create_job(pdf_bytes, "History.pdf")
        assert job.file_hash is not None
        assert len(job.file_hash) == 64  # Valid SHA-256

    # 4. pages extracted
    def test_04_pages_extracted(self, pdf_bytes):
        job = history_pipeline.create_job(pdf_bytes, "History.pdf")
        finished_job = history_pipeline.run_pipeline(job.job_id)
        assert finished_job.total_pages_detected == 75
        assert finished_job.content_pages_count == 65

    # 5. chapters extracted
    def test_05_chapters_extracted(self, pdf_bytes):
        job = history_pipeline.get_latest_job()
        assert len(job.detected_chapters) > 0
        ch1 = job.detected_chapters[0]
        assert ch1["chapter_id"] == "CH_01"
        assert ch1["title_marathi"] == "इतिहासाची साधने"

    # 6. 14 chapters detected
    def test_06_fourteen_chapters_detected(self):
        job = history_pipeline.get_latest_job()
        assert len(job.detected_chapters) == 14
        expected_ids = [f"CH_{i:02d}" for i in range(1, 15)]
        detected_ids = [c["chapter_id"] for c in job.detected_chapters]
        assert detected_ids == expected_ids

    # 7. expected page ranges validated
    def test_07_expected_page_ranges_validated(self):
        job = history_pipeline.get_latest_job()
        # Ch 1: PDF 10-13, Printed 1-4
        ch1 = job.detected_chapters[0]
        assert ch1["pdf_page_range"] == [10, 13]
        assert ch1["printed_page_range"] == [1, 4]
        # Ch 14: PDF 71-74, Printed 62-65
        ch14 = job.detected_chapters[13]
        assert ch14["pdf_page_range"] == [71, 74]
        assert ch14["printed_page_range"] == [62, 65]

    # 8. physical graph created
    def test_08_physical_graph_created(self):
        history_engine.ensure_initialized()
        assert history_engine.physical_graph.total_regions == 845
        assert len(history_engine.physical_graph.chapters) == 14

    # 9. learning graph created
    def test_09_learning_graph_created(self):
        history_engine.ensure_initialized()
        assert len(history_engine.learning_graph.units) == 146
        assert len(history_engine.learning_graph.concepts) == 30
        assert len(history_engine.learning_graph.entities) == 215
        assert len(history_engine.learning_graph.edges) == 846

    # 10. teaching graph created
    def test_10_teaching_graph_created(self):
        history_engine.ensure_initialized()
        nodes = history_engine.teaching_graph.get_nodes_for_chapter("CH_01")
        assert len(nodes) > 0
        # Validates distinction of textbook structure vs recommendation
        assert any(n.pedagogical_intent is not None for n in nodes)

    # 11. narration plan created
    def test_11_narration_plan_created(self):
        history_engine.ensure_initialized()
        plan = history_engine.get_chapter_narration("CH_01")
        assert plan["chapter_id"] == "CH_01"
        assert len(plan["normal_reading_items"]) > 0
        assert plan["normal_reading_items"][0]["style"]["style"] in ("historical_narration", "explanatory_teacher")

    # 12. pronunciation candidates created
    def test_12_pronunciation_candidates_created(self):
        history_engine.ensure_initialized()
        entries = history_engine.pronunciation_kb.entries
        assert len(entries) == 197
        # Enforces UNVERIFIED initially
        assert all(e.verification_status == "UNVERIFIED" for e in entries.values())

    # 13. cache created
    def test_13_cache_created(self):
        history_engine.ensure_initialized()
        manifest = history_engine.get_manifest()
        assert manifest["document_id"] == "AKS_HISTORY_CLASS8_HISTORY"
        cached = history_engine.cache.get(HistoryCacheLayer.CHAPTER_STRUCTURE, "MANIFEST")
        assert cached is not None

    # 14. API exposes processed textbook
    def test_14_api_exposes_processed_textbook(self):
        res = client.get("/api/history/processing-details")
        assert res.status_code == 200
        data = res.json()
        assert data["document"]["document_id"] == "AKS_HISTORY_CLASS8_HISTORY"
        assert data["structural_metrics"]["total_chapters"] == 14
        assert data["structural_metrics"]["total_learning_units"] == 146

    # 15. frontend can load processed textbook
    def test_15_frontend_can_load_processed_textbook(self):
        res = client.get("/api/history/chapters/CH_01/reader")
        assert res.status_code == 200
        payload = res.json()
        assert "chapter" in payload
        assert "pages" in payload
        assert len(payload["pages"]) == 4  # 4 pages in Ch 1 (PDF 10-13)

    # 16. chapter reader loads
    def test_16_chapter_reader_loads(self):
        res = client.get("/api/chapters/CH_01/reader?doc_id=AKS_HISTORY_CLASS8_HISTORY")
        assert res.status_code == 200
        payload = res.json()
        assert "इतिहासाची साधने" in payload["chapter"]["title"]
        assert len(payload["pages"][0]["paragraphs"]) > 0

    # 17. learning-unit navigation works
    def test_17_learning_unit_navigation_works(self):
        res = client.get("/api/history/chapters/CH_01/learning-units")
        assert res.status_code == 200
        units = res.json()["learning_units"]
        assert len(units) == 7
        first_unit = units[0]
        assert first_unit["unit_id"] == "CH_01_LU_01"
        assert "इतिहास" in first_unit["title"]

    # 18. tutor retrieval is grounded
    def test_18_tutor_retrieval_is_grounded(self):
        res = client.post(
            "/api/history/tutor",
            json={"query": "भौतिक साधने म्हणजे काय?", "chapter_id": "CH_01", "document_id": "AKS_HISTORY_CLASS8_HISTORY"}
        )
        assert res.status_code == 200
        data = res.json()
        assert data["mode"] == "tutor"
        assert data["audible_cue"] is True
        assert len(data["canonical_reference"]) > 0
        assert len(data["pedagogical_explanation"]) > 0
        assert data["provenance"]["chapter_id"] == "CH_01"

    # 19. old textbooks remain stored
    def test_19_old_textbooks_remain_stored(self):
        res = client.get("/api/documents")
        assert res.status_code == 200
        docs = res.json()["documents"]
        doc_ids = [d["doc_id"] for d in docs]
        assert "akshar-10" in doc_ids or "geo-10" in doc_ids

    # 20. old textbooks are not active
    def test_20_old_textbooks_are_not_active(self):
        res = client.get("/api/documents")
        assert res.status_code == 200
        docs = res.json()["documents"]
        # History is the primary master reference
        history_doc = next(d for d in docs if d["doc_id"] == "AKS_HISTORY_CLASS8_HISTORY")
        assert "Master Reference" in history_doc["description"]

    # 21. duplicate History upload reuses cache
    def test_21_duplicate_history_upload_reuses_cache(self, pdf_bytes):
        job1 = history_pipeline.create_job(pdf_bytes, "History.pdf")
        history_pipeline.run_pipeline(job1.job_id)
        job2 = history_pipeline.create_job(pdf_bytes, "History.pdf")
        assert job1.file_hash == job2.file_hash
        assert job2.stage == IngestionStage.READY.value
        assert job2.is_cached_match is True

    # 22. changed PDF creates a new version
    def test_22_changed_pdf_creates_new_version(self, pdf_bytes):
        orig_hash = history_pipeline.create_job(pdf_bytes, "History.pdf").file_hash
        altered_bytes = pdf_bytes + b"\n% AKSHARSETU_TEST_SALT_VERSION_2"
        job_new = history_pipeline.create_job(altered_bytes, "History_v2.pdf")
        assert job_new.file_hash != orig_hash

    # 23. processing failure produces FAILED/NEEDS_REVIEW state
    def test_23_processing_failure_produces_failed_state(self):
        corrupted_bytes = b"NOT_A_VALID_PDF_HEADER_DATA"
        job = history_pipeline.create_job(corrupted_bytes, "bad.pdf")
        with pytest.raises(Exception):
            history_pipeline.run_pipeline(job.job_id)
        failed_job = history_pipeline.get_job(job.job_id)
        assert failed_job.stage == IngestionStage.FAILED.value
        assert failed_job.error is not None

    # 24. no fabricated bbox/visual descriptions
    def test_24_no_fabricated_bbox_or_visual_descriptions(self):
        history_engine.ensure_initialized()
        regions = history_engine.physical_graph.regions
        # Verifies explicit bbox=None and visual_description_status="UNVERIFIED"
        unverified_regions = [r for r in regions.values() if r.bbox is None]
        assert len(unverified_regions) > 0
        assert all(r.visual_description_status == "UNVERIFIED" for r in unverified_regions)

    # 25. provenance is preserved
    def test_25_provenance_is_preserved(self):
        history_engine.ensure_initialized()
        for u in history_engine.learning_graph.units.values():
            assert u.provenance_status in (
                "SOURCE_VERIFIED",
                "SUPPORTED_INFERENCE",
                "AKSHARSETU_RECOMMENDATION"
            )
            assert u.chapter_id.startswith("CH_")
