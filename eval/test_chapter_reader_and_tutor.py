"""
AksharSetu — Complete Chapter Traversal, Manifest & Teacher-Like Tutor Regression Test Suite

Asserts:
1. Chapter page count matches chapter manifest (8 pages for Geography Ch 1: PDF 12-19).
2. First page is correct (PDF 12, printed 1).
3. Last page is correct (PDF 19, printed 8).
4. All expected page IDs are present exactly once.
5. All expected learning units are present.
6. All spoken regions belong to the chapter.
7. Traversal reaches the final region from the first region.
8. No region appears twice.
9. No canonical region is silently dropped (244 physical regions for Geography Ch 1).
10. Physical order != pedagogical order != spoken order (Three Orders preserved).
11. Canonical text immutability: Tutor Mode does NOT mutate or replace canonical text.
12. Tutor response schema: includes teaching_intent, transition, explanation, and 3 distinct audio segments.
13. Pluggable TTS Provider Abstraction: SarvamTTSProvider and candidate IndicF5TTSProvider.
14. Teacher Datasets: Dataset A (Behavior) and Dataset B (Speech) schemas.
"""

import os
import sys
import unittest

if sys.stdout.encoding != 'utf-8':
    try:
        sys.stdout.reconfigure(encoding='utf-8')
    except Exception:
        pass

from ingestion.pdf_structure import DocumentStructureAnalyzer
from ingestion.chapter_processor import ChapterProcessor
from ingestion.chapter_manifest import ChapterManifest
from tutor.pedagogical_planner import PedagogicalPlanner, TutorResponse, SpeechSegment
from voice.tts_service import TTSService, SpeechStylePlan, SarvamTTSProvider, IndicF5TTSProvider
from corpus.teacher_datasets import TeacherBehaviorSample, TeacherSpeechSample, TeacherDatasetManager

class TestCompleteChapterReaderAndTutor(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.analyzer = DocumentStructureAnalyzer()
        cls.processor = ChapterProcessor()
        cls.planner = PedagogicalPlanner()
        cls.geo_pdf_path = os.path.join("dataset", "SSC-10th-Class-Geography-Textbook-in-Marathi.pdf")
        cls.marathi_pdf_path = os.path.join("dataset", "AksharBharti-Marathi-10th-English-Medium-.pdf")

    # -------------------------------------------------------------------------
    # PART 1: GEOGRAPHY CHAPTER 1 COMPLETE MANIFEST & 8-PAGE TRAVERSAL (PDF 12-19)
    # -------------------------------------------------------------------------
    def test_01_geography_chapter1_complete_manifest(self):
        """Validates Geography Chapter 1 explicit manifest over PDF pages 12-19 and 244 regions."""
        struct = self.analyzer.analyze_document(self.geo_pdf_path)
        payload = self.processor.get_chapter_reader_payload(struct, "ch_1")

        chapter = payload["chapter"]
        manifest = payload["manifest"]
        pages = payload["pages"]
        spoken = payload["spoken_sequence"]

        # 1. Chapter page count matches manifest
        self.assertEqual(len(pages), 8, "Geography Ch 1 must contain exactly 8 pages")
        self.assertEqual(manifest["total_pages"], 8)
        self.assertEqual(chapter["total_pages"], 8)

        # 2. First page is correct (PDF 12, printed 1)
        first_page = pages[0]
        self.assertEqual(first_page["pdf_page"], 12)
        self.assertEqual(first_page["printed_page"], 1)
        self.assertEqual(manifest["pdf_start_page"], 12)
        self.assertEqual(manifest["printed_start_page"], 1)

        # 3. Last page is correct (PDF 19, printed 8)
        last_page = pages[-1]
        self.assertEqual(last_page["pdf_page"], 19)
        self.assertEqual(last_page["printed_page"], 8)
        self.assertEqual(manifest["pdf_end_page"], 19)
        self.assertEqual(manifest["printed_end_page"], 8)

        # 4. All expected page IDs are present exactly once
        expected_page_ids = [f"page_{p}" for p in range(12, 20)]
        actual_page_ids = [p["page_id"] for p in pages]
        self.assertEqual(actual_page_ids, expected_page_ids)
        self.assertEqual(len(set(actual_page_ids)), len(actual_page_ids), "No duplicate pages allowed")

        # 5. All expected learning units are present
        learning_units = payload["learning_units"]
        unit_ids = [u["unit_id"] for u in learning_units]
        self.assertIn("unit_ch_1_main", unit_ids)
        self.assertIn("unit_ch_1_vocab", unit_ids)
        self.assertIn("unit_ch_1_exercise", unit_ids)

        # 6. Total physical regions: exactly 244 across all 8 pages
        self.assertEqual(manifest["total_physical_regions"], 244)
        self.assertEqual(len(manifest["physical_region_ids"]), 244)

        # 7. No region appears twice
        self.assertEqual(len(set(manifest["physical_region_ids"])), 244, "Every physical region must be unique")

        # 8. All spoken regions belong to the chapter
        chapter_rids = set(manifest["physical_region_ids"])
        for s in spoken:
            self.assertIn(s["region_id"], chapter_rids, f"Spoken region {s['region_id']} must belong to chapter manifest")

        # 9. Traversal reaches the final region from the first region
        first_spoken = spoken[0]
        last_spoken = spoken[-1]
        self.assertEqual(first_spoken["pdf_page"], 12, "First spoken item must start on first page (PDF 12)")
        self.assertEqual(last_spoken["pdf_page"], 19, "Last spoken item must finish on final page (PDF 19)")
        self.assertGreater(len(spoken), 200, "Spoken sequence must span the complete 8-page chapter")

    # -------------------------------------------------------------------------
    # PART 2: THREE ORDERS SEPARATE VERIFICATION
    # -------------------------------------------------------------------------
    def test_02_three_orders_remain_separate(self):
        """Validates that Physical 2D Order, Pedagogical Order, and Spoken Order remain distinct."""
        struct = self.analyzer.analyze_document(self.geo_pdf_path)
        payload = self.processor.get_chapter_reader_payload(struct, "ch_1")
        manifest = payload["manifest"]

        phys = manifest["physical_region_ids"]
        ped = manifest["pedagogical_order"]
        spoken = manifest["spoken_order"]

        self.assertNotEqual(phys, ped, "Physical layout order and pedagogical order must NOT be identical")
        self.assertNotEqual(ped, spoken, "Pedagogical regions and spoken sentence sequence must NOT be collapsed")

    # -------------------------------------------------------------------------
    # PART 3: MARATHI CHAPTER 1 VERIFICATION
    # -------------------------------------------------------------------------
    def test_03_marathi_chapter1_reader_hierarchy(self):
        """Validates Marathi Chapter 1 'तू बुद्धी दे' reader hierarchy."""
        struct = self.analyzer.analyze_document(self.marathi_pdf_path)
        payload = self.processor.get_chapter_reader_payload(struct, "ch_1")

        self.assertEqual(len(payload["pages"]), 1)
        self.assertEqual(payload["manifest"]["pdf_start_page"], 10)
        self.assertEqual(payload["manifest"]["printed_start_page"], 1)
        self.assertIn("तू बुद्धी दे", payload["chapter"]["title"])
        self.assertEqual(len(payload["pages"][0]["paragraphs"]), 9) # 1 heading + 4 stanzas + 4 vocabulary definitions

    # -------------------------------------------------------------------------
    # PART 4: TUTOR MODE GROUNDING & AUDIO SEGMENTATION
    # -------------------------------------------------------------------------
    def test_04_tutor_mode_grounding_and_segments(self):
        """Validates structured TutorResponse and 3 distinct audio segments."""
        canonical_line = "उस्मानाबाद जिल्ह्यातील नळदुर्ग ते रायगड जिल्ह्यातील अलिबाग येथे क्षेत्रभेटीसाठी निघाले आहेत."
        resp = self.planner.plan_tutor_response(
            canonical_text=canonical_line,
            subject="Geography",
            region_type="paragraph",
            concept="क्षेत्रभेट",
            learning_unit_id="unit_ch_1_main"
        )

        # 1. Canonical text immutability: canonical text must be untouched
        self.assertEqual(resp.canonical_text, canonical_line)
        self.assertNotIn("स्पष्टीकरण", resp.canonical_text)

        # 2. Teaching intent and grounding
        self.assertEqual(resp.teaching_intent, "clarify_concept")
        self.assertEqual(resp.subject, "Geography")
        self.assertTrue(len(resp.transition) > 0)
        self.assertTrue(len(resp.explanation) > 0)
        self.assertIn("क्षेत्रभेट", resp.explanation)

        # 3. Audio segmentation: exactly 3 segments [canonical, transition, explanation]
        self.assertEqual(len(resp.segments), 3)
        seg_canonical = resp.segments[0]
        seg_transition = resp.segments[1]
        seg_explanation = resp.segments[2]

        self.assertEqual(seg_canonical.type, "canonical")
        self.assertEqual(seg_canonical.text, canonical_line)
        self.assertEqual(seg_canonical.prosody_style, "canonical_reading")

        self.assertEqual(seg_transition.type, "transition")
        self.assertEqual(seg_transition.prosody_style, "teacher_transition")

        self.assertEqual(seg_explanation.type, "explanation")
        self.assertIn(seg_explanation.prosody_style, ("teacher_explanation", "teacher_guidance", "teacher_observation"))
        self.assertLessEqual(seg_explanation.pace, 0.95, "Teacher explanation must use measured cadence")

    # -------------------------------------------------------------------------
    # PART 5: PLUGGABLE TTS PROVIDER ABSTRACTION & SPEECH STYLE PLAN
    # -------------------------------------------------------------------------
    def test_05_tts_provider_abstraction(self):
        """Validates TTSService provider abstraction and SpeechStylePlan mediation."""
        tts = TTSService()
        providers = tts.list_providers()
        prov_names = [p["name"] for p in providers]

        # 1. Providers registered
        self.assertIn("sarvam", prov_names)
        self.assertIn("indicf5", prov_names)

        # 2. Sarvam provider resolves
        sarvam_prov = tts.get_provider("sarvam")
        self.assertIsInstance(sarvam_prov, SarvamTTSProvider)
        self.assertEqual(sarvam_prov.provider_name, "sarvam")

        # 3. IndicF5 candidate stub resolves
        indic_prov = tts.get_provider("indicf5")
        self.assertIsInstance(indic_prov, IndicF5TTSProvider)
        self.assertEqual(indic_prov.provider_name, "indicf5")

        # 4. SpeechStylePlan factory methods
        plan_canon = SpeechStylePlan.for_canonical_reading(1.0)
        self.assertEqual(plan_canon.style, "canonical")
        self.assertEqual(plan_canon.intent, "reading")

        plan_teacher = SpeechStylePlan.for_teacher_explanation(1.0, ["क्षेत्रभेट"])
        self.assertEqual(plan_teacher.style, "teacher")
        self.assertEqual(plan_teacher.intent, "explanation")
        self.assertEqual(plan_teacher.emphasis_terms, ["क्षेत्रभेट"])

    # -------------------------------------------------------------------------
    # PART 6: TEACHER BEHAVIOR & SPEECH DATASETS (DATASET A & B)
    # -------------------------------------------------------------------------
    def test_06_teacher_datasets_schemas(self):
        """Validates Dataset A (Teacher Behavior) and Dataset B (Teacher Speech) separation."""
        # Dataset A: How a teacher teaches
        sample_a = TeacherBehaviorSample(
            sample_id="tb_geo_001",
            subject="geography",
            chapter="१. क्षेत्रभेट",
            learning_unit="unit_ch_1_main",
            student_context="विद्यार्थी नळदुर्ग ते अलिबाग प्रवासाचा मार्ग नकाशा पाहत आहेत.",
            textbook_context="आकृती १.१ : क्षेत्रभेटीचा मार्ग",
            teacher_response="नकाशाचे निरीक्षण करताना दिशा आणि अंतराची नोंद कशी करावी याकडे लक्ष द्या.",
            teaching_intent="guide_observation",
            transition="या आकृतीचे काळजीपूर्वक निरीक्षण करा."
        )
        self.assertEqual(sample_a.teaching_intent, "guide_observation")
        self.assertIn("teacher_response", sample_a.to_dict())

        # Dataset B: How that teacher sounds
        sample_b = TeacherSpeechSample(
            sample_id="ts_geo_001",
            text="नकाशाचे निरीक्षण करताना दिशा आणि अंतराची नोंद कशी करावी याकडे लक्ष द्या.",
            audio_path="recordings/teacher_01/ts_geo_001.wav",
            speaker="teacher_marathi_female_1",
            language="mr-IN",
            style="teacher_explanation",
            intent="guide_observation",
            prosody_metadata={"pace": 0.95, "emphasis": ["नकाशा", "दिशा"]}
        )
        self.assertEqual(sample_b.speaker, "teacher_marathi_female_1")
        self.assertEqual(sample_b.prosody_metadata["pace"], 0.95)

if __name__ == "__main__":
    unittest.main()
