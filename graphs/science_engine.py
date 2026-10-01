"""
AksharSetu — Class 8 Science Subject Engine (Master Coordinator)

Orchestrates Phases 1 through 10 for Class 8 General Science:
- Phase 1: Science Corpus Ingestion (corpus/science_loader.py)
- Phase 2: Physical Document Graph (graphs/science_physical_graph.py)
- Phase 3: Science Grammar (graphs/science_grammar.py)
- Phase 4: Learning Graph (graphs/science_learning_graph.py)
- Phase 5: Teaching Graph (graphs/science_teaching_graph.py)
- Phase 6: Narration Planner (orchestrator/science_narration_planner.py)
- Phase 7: Speaking Style (SCIENCE_STYLE_PROFILES)
- Phase 8: Pronunciation Knowledge Layer (corpus/science_pronunciation.py)
- Phase 9: Grounded Tutor & RAG Engine (orchestrator/science_tutor_engine.py)
- Phase 10: Granular Invalidation Caching (graphs/science_cache.py)
"""

from typing import Dict, List, Optional, Any, Tuple
from dataclasses import asdict
import re

from corpus.science_loader import science_corpus_loader, ScienceChapterMetadata
from graphs.science_physical_graph import science_physical_graph, SciencePhysicalDocumentGraph
from graphs.science_grammar import science_grammar_engine, ScienceGrammarEngine
from graphs.science_learning_graph import science_learning_graph, ScienceLearningGraph
from graphs.science_teaching_graph import science_teaching_graph, ScienceTeachingGraph
from orchestrator.science_narration_planner import science_narration_planner, ScienceNarrationPlanner
from corpus.science_pronunciation import science_pronunciation_kb, SciencePronunciationKB
from orchestrator.science_tutor_engine import science_tutor_engine, ScienceTutorEngine
from graphs.science_cache import science_cache, ScienceCacheLayer


class ScienceSubjectEngine:
    """
    Central Coordinator for the Class 8 Science Subject Engine.
    Serves as the Master Reference Implementation for Science in AksharSetu.
    """

    def __init__(self):
        self.loader = science_corpus_loader
        self.physical_graph = science_physical_graph
        self.grammar = science_grammar_engine
        self.learning_graph = science_learning_graph
        self.teaching_graph = science_teaching_graph
        self.narration_planner = science_narration_planner
        self.pronunciation_kb = science_pronunciation_kb
        self.tutor_engine = science_tutor_engine
        self.cache = science_cache
        self._initialized = False

    def ensure_initialized(self):
        if not self._initialized:
            self.loader.validate_and_load()
            self.physical_graph.build_graph()
            self.learning_graph.build_graph()
            self.teaching_graph.build_graph()
            self.pronunciation_kb.build_lexicon()
            self._initialized = True

    # --- Phase 1: Manifest & Inventory ---

    def get_manifest(self) -> Dict[str, Any]:
        self.ensure_initialized()
        cached = self.cache.get(ScienceCacheLayer.CHAPTER_STRUCTURE, "MANIFEST")
        if cached:
            return cached

        manifest = asdict(self.loader.manifest)
        manifest["cross_chapter_grammar"] = self.loader.grammar_metadata
        manifest["total_glossary_terms"] = len(self.loader.glossary_terms)
        self.cache.put(ScienceCacheLayer.CHAPTER_STRUCTURE, "MANIFEST", manifest)
        return manifest

    def list_chapters(self) -> List[Dict[str, Any]]:
        self.ensure_initialized()
        chapters = []
        for ch in self.loader.list_all_chapters():
            d = asdict(ch)
            d["genre_pattern"] = asdict(self.grammar.get_pattern_for_chapter(ch.chapter_id))
            chapters.append(d)
        return chapters

    def get_chapter_detail(self, chapter_id: str) -> Optional[Dict[str, Any]]:
        self.ensure_initialized()
        ch_upper = chapter_id.upper()
        ch = self.loader.get_chapter(ch_upper)
        if not ch:
            return None

        cached = self.cache.get(ScienceCacheLayer.CHAPTER_STRUCTURE, ch_upper)
        if cached:
            return cached

        data = asdict(ch)
        data["learning_units_detail"] = [
            asdict(u) for u in self.learning_graph.get_units_for_chapter(ch_upper)
        ]
        data["teaching_nodes"] = [
            n.to_dict() for n in self.teaching_graph.get_nodes_for_chapter(ch_upper)
        ]
        data["grammar_profile"] = self.grammar.get_grammar_profile(ch_upper)
        data["pronunciation_lexicon"] = [
            e.to_dict() for e in self.pronunciation_kb.list_entries(ch_upper)
        ]

        self.cache.put(ScienceCacheLayer.CHAPTER_STRUCTURE, ch_upper, data)
        return data

    # --- Phase 4: Learning Units ---

    def get_chapter_learning_units(self, chapter_id: str) -> List[Dict[str, Any]]:
        self.ensure_initialized()
        units = self.learning_graph.get_units_for_chapter(chapter_id.upper())
        return [asdict(u) for u in units]

    def get_learning_unit(self, unit_id: str) -> Optional[Dict[str, Any]]:
        self.ensure_initialized()
        u = self.learning_graph.get_learning_unit(unit_id)
        if not u:
            return None
        data = asdict(u)
        data["concepts"] = [asdict(c) for c in self.learning_graph.get_concepts_for_unit(unit_id)]
        return data

    # --- Phase 6: Narration Planning ---

    def get_chapter_narration(self, chapter_id: str, version: str = "1.0") -> Dict[str, Any]:
        self.ensure_initialized()
        plan = self.narration_planner.plan_chapter_narration(chapter_id.upper(), version=version)
        return plan.to_dict()

    # --- Phase 8: Pronunciation Lexicon ---

    def get_pronunciation_lexicon(self, chapter_id: Optional[str] = None) -> List[Dict[str, Any]]:
        self.ensure_initialized()
        entries = self.pronunciation_kb.list_entries(chapter_id)
        return [e.to_dict() for e in entries]

    # --- Phase 7 & Audio Synthesis ---

    def get_chapter_audio(self, chapter_id: str, voice: Optional[str] = "shreya") -> Dict[str, Any]:
        self.ensure_initialized()
        ch_upper = chapter_id.upper()
        plan = self.narration_planner.plan_chapter_narration(ch_upper)

        audio_playlist = []
        for item in plan.normal_reading_items:
            audio_playlist.append({
                "item_id": item.item_id,
                "text": item.speech_text,
                "speaking_style": item.style.style.value,
                "base_pace": item.style.base_pace,
                "pause_after_sentence_ms": item.style.pause_after_sentence_ms,
                "pause_after_paragraph_ms": item.style.pause_after_paragraph_ms,
                "voice": voice or "shreya",
                "audio_url": f"/api/tts/synthesize?text={item.item_id}"
            })

        return {
            "chapter_id": ch_upper,
            "voice": voice or "shreya",
            "total_audio_tracks": len(audio_playlist),
            "playlist": audio_playlist
        }

    # --- Reader Payload for Frontend UI ---

    def get_reader_payload(self, chapter_id: str) -> Dict[str, Any]:
        """
        Synthesizes complete, verified reader payload consumed by the Reader UI (/read).
        Includes full page pagination (PDF start to end), paragraph blocks,
        learning unit links, and pedagogical prompts.
        """
        self.ensure_initialized()
        ch_upper = chapter_id.upper()
        ch = self.loader.get_chapter(ch_upper)
        if not ch:
            raise KeyError(f"Science chapter '{chapter_id}' not found.")

        cached = self.cache.get(ScienceCacheLayer.READER_PAYLOAD, ch_upper)
        if cached:
            return cached

        pages_payload = []
        spoken_sequence = []

        ch_pages = self.physical_graph.get_chapter(ch_upper)
        if ch_pages:
            for pg in ch_pages.get_pages():
                paragraphs = []
                for reg in pg.regions:
                    # Clean sentence segmentation
                    raw_sents = [s.strip() for s in re.split(r'(?<=[।?!.])\s+', reg.text) if s.strip()]
                    if not raw_sents:
                        raw_sents = [reg.text]

                    sentences_data = []
                    for s_idx, sent in enumerate(raw_sents, 1):
                        sentences_data.append({
                            "id": s_idx,
                            "text": sent,
                            "tokens": [{"text": t} for t in sent.split()],
                            "para_id": reg.region_id,
                            "pdf_page": reg.pdf_page_number,
                            "printed_page": reg.printed_page_number
                        })

                    # Supporting visual detection
                    visuals = []
                    if "आकृती" in reg.text or "तक्ता" in reg.text:
                        visuals.append({
                            "material_id": f"{reg.region_id}_vis",
                            "material_type": "diagram",
                            "title": reg.text[:50] + ("..." if len(reg.text) > 50 else ""),
                            "caption_text": reg.text,
                            "explanation": f"प्रकरण {ch.chapter_number} : '{ch.title_marathi}' मधील वैज्ञानिक आकृती किंवा तक्ता.",
                            "auto_narrate": False
                        })

                    # Block type mapping
                    b_type = "paragraph"
                    if reg.region_type == "heading":
                        b_type = "heading"
                    elif reg.region_type == "activity_box":
                        b_type = "activity_box"
                    elif reg.region_type == "boxed_fact":
                        b_type = "boxed_fact"
                    elif reg.region_type == "exercise_header":
                        b_type = "exercise_header"

                    block = {
                        "id": reg.region_id,
                        "block_id": reg.region_id,
                        "block_type": b_type,
                        "primary_content": True,
                        "canonical_text": reg.text,
                        "pdf_page": reg.pdf_page_number,
                        "printed_page": reg.printed_page_number,
                        "sentences": sentences_data,
                        "dialogue_turns": [],
                        "supporting_visuals": visuals,
                        "tutor": f"प्रकरण {ch.chapter_number} : '{ch.title_marathi}' मधील महत्त्वाची वैज्ञानिक माहिती.",
                        "tutor_plan": {
                            "topic": ch.title_marathi,
                            "explanation": f"या भागात '{ch.title_marathi}' मधील संकल्पना आणि प्रायोगिक निरीक्षणाचे मार्गदर्शन केले आहे."
                        },
                        "narration_plan": {
                            "policy": ch.narration_policy,
                            "style": ch.speaking_style
                        }
                    }
                    paragraphs.append(block)

                    spoken_sequence.append({
                        "step_id": reg.region_id,
                        "block_id": reg.region_id,
                        "text": reg.text,
                        "style": ch.speaking_style,
                        "policy": ch.narration_policy
                    })

                pages_payload.append({
                    "page_id": pg.page_id,
                    "pdf_page": pg.pdf_page_number,
                    "printed_page": pg.printed_page_number,
                    "paragraphs": paragraphs,
                    "total_blocks": len(paragraphs),
                    "total_regions": len(paragraphs)
                })

        reader_data = {
            "chapter": {
                "chapter_id": ch.chapter_id,
                "document_id": "AKS_SCIENCE_CLASS8_SCIENCE",
                "title": f"सामान्य विज्ञान प्रकरण {ch.chapter_number} : {ch.title_marathi}",
                "subject": "सामान्य विज्ञान (Class 8 Science, Reference)",
                "pdf_start_page": ch.pdf_page_range[0],
                "pdf_end_page": ch.pdf_page_range[1],
                "printed_start_page": ch.printed_page_range[0],
                "printed_end_page": ch.printed_page_range[1],
                "total_pages": len(pages_payload),
                "total_physical_regions": sum(p["total_regions"] for p in pages_payload)
            },
            "manifest": {
                "document_id": "AKS_SCIENCE_CLASS8_SCIENCE",
                "subject": "science",
                "grade": 8,
                "learning_units": ch.learning_units,
                "key_concepts": [c.concept for c in ch.key_concepts],
                "genre": ch.chapter_type
            },
            "pages": pages_payload,
            "spoken_sequence": spoken_sequence
        }

        self.cache.put(ScienceCacheLayer.READER_PAYLOAD, ch_upper, reader_data)
        return reader_data

    # --- Phase 9: Grounded Tutor Retrieval ---

    def retrieve_grounded_tutor_context(
        self,
        query: str,
        chapter_id: str,
        learning_unit_id: Optional[str] = None,
        region_id: Optional[str] = None
    ) -> Dict[str, Any]:
        res = self.tutor_engine.query_tutor(
            query=query,
            chapter_id=chapter_id,
            learning_unit_id=learning_unit_id,
            region_id=region_id
        )
        return res.to_dict()


science_engine = ScienceSubjectEngine()
