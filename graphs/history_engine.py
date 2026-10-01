"""
AksharSetu — Class 8 History Subject Engine (Master Coordinator)

Orchestrates Phases 1 through 10:
- Phase 1: History Corpus Ingestion (corpus/history_loader.py)
- Phase 2: Physical Document Graph (graphs/history_physical_graph.py)
- Phase 3: History Grammar (graphs/history_grammar.py)
- Phase 4: Learning Graph (graphs/history_learning_graph.py)
- Phase 5: Teaching Graph (graphs/history_teaching_graph.py)
- Phase 6: Narration Planner (orchestrator/history_narration_planner.py)
- Phase 7: Speaking Style (STYLE_PROFILES)
- Phase 8: Pronunciation Knowledge Layer (corpus/history_pronunciation.py)
- Phase 9: Grounded Tutor & RAG Engine (orchestrator/history_tutor_engine.py)
- Phase 10: Granular Invalidation Caching (graphs/history_cache.py)
"""

from typing import Dict, List, Optional, Any, Tuple
from dataclasses import asdict

from corpus.history_loader import history_corpus_loader, HistoryChapterMetadata
from graphs.history_physical_graph import history_physical_graph, HistoryPhysicalDocumentGraph
from graphs.history_grammar import history_grammar_engine, HistoryGrammarEngine
from graphs.history_learning_graph import history_learning_graph, HistoryLearningGraph
from graphs.history_teaching_graph import history_teaching_graph, HistoryTeachingGraph
from orchestrator.history_narration_planner import history_narration_planner, HistoryNarrationPlanner
from corpus.history_pronunciation import history_pronunciation_kb, HistoryPronunciationKB
from orchestrator.history_tutor_engine import history_tutor_engine, HistoryTutorEngine
from graphs.history_cache import history_cache, HistoryCacheLayer


class HistorySubjectEngine:
    """
    Central Coordinator for the Class 8 History Subject Engine.
    Serves as the Master Reference Implementation for AksharSetu.
    """

    def __init__(self):
        self.loader = history_corpus_loader
        self.physical_graph = history_physical_graph
        self.grammar = history_grammar_engine
        self.learning_graph = history_learning_graph
        self.teaching_graph = history_teaching_graph
        self.narration_planner = history_narration_planner
        self.pronunciation_kb = history_pronunciation_kb
        self.tutor_engine = history_tutor_engine
        self.cache = history_cache
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
        cached = self.cache.get(HistoryCacheLayer.CHAPTER_STRUCTURE, "MANIFEST")
        if cached:
            return cached

        manifest = asdict(self.loader.manifest)
        manifest["cross_chapter_grammar"] = self.loader.grammar_metadata
        self.cache.put(HistoryCacheLayer.CHAPTER_STRUCTURE, "MANIFEST", manifest)
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

        # Check Cache
        cached = self.cache.get(HistoryCacheLayer.CHAPTER_STRUCTURE, ch_upper)
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

        self.cache.put(HistoryCacheLayer.CHAPTER_STRUCTURE, ch_upper, data)
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
        data["edges"] = [asdict(e) for e in self.learning_graph.get_edges_for_node(unit_id)]
        data["physical_regions"] = [
            r.to_dict() for r in self.physical_graph.get_regions_for_learning_unit(unit_id)
        ]
        return data

    # --- Phase 6: Narration Planning ---

    def get_chapter_narration(self, chapter_id: str) -> Dict[str, Any]:
        self.ensure_initialized()
        plan = self.narration_planner.plan_chapter_narration(chapter_id.upper())
        return plan.to_dict()

    # --- Audio Synthesis Endpoint (§Phase 11) ---

    def get_chapter_audio(self, chapter_id: str, voice: Optional[str] = None) -> Dict[str, Any]:
        self.ensure_initialized()
        ch_upper = chapter_id.upper()
        selected_voice = voice or self.cache.ledger.tts_voice

        # Check Cache
        cached = self.cache.get(HistoryCacheLayer.TTS_AUDIO, ch_upper, {"voice": selected_voice})
        if cached:
            return cached

        plan = self.narration_planner.plan_chapter_narration(ch_upper)
        normal_items = plan.normal_reading_items

        # Build simulated/cached audio playlist for the chapter's narration items
        playlist = []
        for item in normal_items:
            # Resolve pronunciation
            resolved_text, prons = self.pronunciation_kb.resolve_for_tts(item.speech_text)
            playlist.append({
                "item_id": item.item_id,
                "region_id": item.source_region_id,
                "unit_id": item.learning_unit_id,
                "text": resolved_text,
                "style": item.style.style.value,
                "pace": item.style.base_pace,
                "voice": selected_voice,
                "duration_estimate_sec": round(len(resolved_text.split()) * 0.4 / item.style.base_pace, 2)
            })

        audio_res = {
            "chapter_id": ch_upper,
            "provider": self.cache.ledger.tts_provider,
            "voice": selected_voice,
            "total_audio_tracks": len(playlist),
            "estimated_chapter_duration_min": round(sum(p["duration_estimate_sec"] for p in playlist) / 60, 1),
            "tracks": playlist
        }

        self.cache.put(HistoryCacheLayer.TTS_AUDIO, ch_upper, audio_res, {"voice": selected_voice})
        return audio_res

    # --- Complete Reader Payload (Reader UI) ---

    def get_reader_payload(self, chapter_id: str) -> Dict[str, Any]:
        self.ensure_initialized()
        ch_upper = chapter_id.upper()
        ch = self.loader.get_chapter(ch_upper)
        if not ch:
            raise KeyError(f"Chapter '{chapter_id}' not found in History corpus.")

        # Check Cache
        cached = self.cache.get(HistoryCacheLayer.CHAPTER_STRUCTURE, f"{ch_upper}_READER")
        if cached:
            return cached

        ch_pages = self.physical_graph.get_chapter(ch_upper)
        pages_payload = []
        spoken_sequence = []

        if ch_pages:
            for pg in ch_pages.get_pages():
                paragraphs = []
                for reg in pg.regions:
                    # Clean sentence segmentation
                    import re
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

                    block = {
                        "id": reg.region_id,
                        "block_id": reg.region_id,
                        "block_type": "paragraph" if reg.region_type == "body_paragraph" else "section_header",
                        "primary_content": True,
                        "canonical_text": reg.text,
                        "pdf_page": reg.pdf_page_number,
                        "printed_page": reg.printed_page_number,
                        "sentences": sentences_data,
                        "dialogue_turns": [],
                        "supporting_visuals": [],
                        "tutor": f"प्रकरण {ch.chapter_number} : '{ch.title_marathi}' मधील महत्त्वाचा संदर्भ.",
                        "tutor_plan": {
                            "topic": ch.title_marathi,
                            "explanation": f"या भागात '{ch.title_marathi}' मधील ऐतिहासिक घटनांची माहिती दिली आहे."
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
                "document_id": "AKS_HISTORY_CLASS8_HISTORY",
                "title": f"इतिहास प्रकरण {ch.chapter_number} : {ch.title_marathi}",
                "subject": "इतिहास (Class 8 History, Reference)",
                "pdf_start_page": ch.pdf_page_range[0],
                "pdf_end_page": ch.pdf_page_range[1],
                "printed_start_page": ch.printed_page_range[0],
                "printed_end_page": ch.printed_page_range[1],
                "total_pages": len(pages_payload),
                "total_physical_regions": sum(p["total_regions"] for p in pages_payload)
            },
            "manifest": {
                "document_id": "AKS_HISTORY_CLASS8_HISTORY",
                "subject": "history",
                "grade": 8,
                "learning_units": ch.learning_units,
                "key_concepts": [c.concept for c in ch.key_concepts],
                "genre": ch.chapter_type
            },
            "pages": pages_payload,
            "spoken_sequence": spoken_sequence
        }

        self.cache.put(HistoryCacheLayer.CHAPTER_STRUCTURE, f"{ch_upper}_READER", reader_data)
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


history_engine = HistorySubjectEngine()
