"""
AksharSetu — Class 8 Science Narration & Speaking Style Planner (Phases 6 & 7)

Phase 6: Narration Planning
- Decouples raw textbook text from TTS.
- Resolves narration policies:
  - READ_DIRECTLY (करून पहा procedural steps, formulas)
  - READ_THEN_EXPLAIN (concept prose, enrichment boxes)
  - EXPLAIN (जरा डोके चालवा reasoning prompts)
  - ON_DEMAND (diagram descriptions, captions, glossary)
  - EXCLUDE_FROM_NORMAL_READING (इंटरनेट माझा मित्र, external research prompts)

Phase 7: Speaking Style
- Distinct styles for General Science:
  - scientific_explanation (clear concept/definition exposition)
  - mathematical_narration (formula derivation, worked examples: given -> formula -> substitution -> answer)
  - procedural_instructional (hands-on experiment steps, imperative cadence)
  - historical_narration (biographical vignettes: Archimedes, Dalton, Golgi)
  - safety_critical (emergency/chemical hazard protocols with immediate acoustic clarity)
"""

from enum import Enum
from dataclasses import dataclass, field, asdict
from typing import Dict, List, Optional, Any, Tuple
import re

from corpus.science_loader import science_corpus_loader, ScienceChapterMetadata
from graphs.science_physical_graph import science_physical_graph, SciencePhysicalRegion
from graphs.science_grammar import science_grammar_engine, ScienceGenre


class NarrationPolicy(str, Enum):
    READ_DIRECTLY = "READ_DIRECTLY"
    READ_THEN_EXPLAIN = "READ_THEN_EXPLAIN"
    EXPLAIN = "EXPLAIN"
    ON_DEMAND = "ON_DEMAND"
    EXCLUDE_FROM_NORMAL_READING = "EXCLUDE_FROM_NORMAL_READING"


class ScienceSpeakingStyle(str, Enum):
    SCIENTIFIC_EXPLANATION = "scientific_explanation"
    MATHEMATICAL_NARRATION = "mathematical_narration"
    PROCEDURAL_INSTRUCTIONAL = "procedural_instructional"
    HISTORICAL_NARRATION = "historical_narration"
    SAFETY_CRITICAL = "safety_critical"


@dataclass
class ScienceSpeakingStyleProfile:
    style: ScienceSpeakingStyle
    base_pace: float
    pause_after_sentence_ms: int
    pause_after_paragraph_ms: int
    sentence_boundary_behavior: str
    transition_behavior: str
    intonation_intent: str

    def to_dict(self) -> Dict[str, Any]:
        d = asdict(self)
        d["style"] = self.style.value
        return d


SCIENCE_STYLE_PROFILES: Dict[ScienceSpeakingStyle, ScienceSpeakingStyleProfile] = {
    ScienceSpeakingStyle.SCIENTIFIC_EXPLANATION: ScienceSpeakingStyleProfile(
        style=ScienceSpeakingStyle.SCIENTIFIC_EXPLANATION,
        base_pace=0.95,
        pause_after_sentence_ms=300,
        pause_after_paragraph_ms=600,
        sentence_boundary_behavior="clear_full_stop",
        transition_behavior="warm_exposition",
        intonation_intent="explanation"
    ),
    ScienceSpeakingStyle.MATHEMATICAL_NARRATION: ScienceSpeakingStyleProfile(
        style=ScienceSpeakingStyle.MATHEMATICAL_NARRATION,
        base_pace=0.88,  # Slower, deliberate pace for formulas and arithmetic
        pause_after_sentence_ms=400,
        pause_after_paragraph_ms=650,
        sentence_boundary_behavior="step_by_step_pause",
        transition_behavior="deliberate_substitution",
        intonation_intent="mathematical_derivation"
    ),
    ScienceSpeakingStyle.PROCEDURAL_INSTRUCTIONAL: ScienceSpeakingStyleProfile(
        style=ScienceSpeakingStyle.PROCEDURAL_INSTRUCTIONAL,
        base_pace=0.90,
        pause_after_sentence_ms=350,
        pause_after_paragraph_ms=650,
        sentence_boundary_behavior="action_cadence",
        transition_behavior="methodical_step",
        intonation_intent="instruction"
    ),
    ScienceSpeakingStyle.HISTORICAL_NARRATION: ScienceSpeakingStyleProfile(
        style=ScienceSpeakingStyle.HISTORICAL_NARRATION,
        base_pace=1.0,
        pause_after_sentence_ms=250,
        pause_after_paragraph_ms=500,
        sentence_boundary_behavior="clear_full_stop",
        transition_behavior="measured_objective",
        intonation_intent="narration"
    ),
    ScienceSpeakingStyle.SAFETY_CRITICAL: ScienceSpeakingStyleProfile(
        style=ScienceSpeakingStyle.SAFETY_CRITICAL,
        base_pace=0.85,
        pause_after_sentence_ms=450,
        pause_after_paragraph_ms=700,
        sentence_boundary_behavior="emphatic_full_stop",
        transition_behavior="heightened_caution",
        intonation_intent="alert_warning"
    ),
}


@dataclass
class PlannedNarrationItem:
    item_id: str
    source_region_id: str
    learning_unit_id: str
    chapter_id: str
    pdf_page_number: int
    printed_page_number: int
    policy: NarrationPolicy
    style: ScienceSpeakingStyleProfile
    canonical_text: str
    speech_text: str
    sentences: List[Dict[str, Any]]
    is_spoken_in_normal_reading: bool
    is_available_on_demand: bool
    context_note: Optional[str] = None
    policy_origin: str = "AKSHARSETU_RECOMMENDATION"

    def to_dict(self) -> Dict[str, Any]:
        return {
            "item_id": self.item_id,
            "source_region_id": self.source_region_id,
            "learning_unit_id": self.learning_unit_id,
            "chapter_id": self.chapter_id,
            "pdf_page_number": self.pdf_page_number,
            "printed_page_number": self.printed_page_number,
            "policy": self.policy.value,
            "style": self.style.to_dict(),
            "canonical_text": self.canonical_text,
            "speech_text": self.speech_text,
            "sentences": self.sentences,
            "is_spoken_in_normal_reading": self.is_spoken_in_normal_reading,
            "is_available_on_demand": self.is_available_on_demand,
            "context_note": self.context_note,
            "policy_origin": self.policy_origin
        }


@dataclass
class ScienceChapterNarrationPlan:
    plan_id: str
    chapter_id: str
    version: str = "1.0"
    total_items: int = 0
    normal_reading_items: List[PlannedNarrationItem] = field(default_factory=list)
    on_demand_items: List[PlannedNarrationItem] = field(default_factory=list)
    policy_source: str = "AKSHARSETU_RECOMMENDATION"

    def to_dict(self) -> Dict[str, Any]:
        return {
            "plan_id": self.plan_id,
            "chapter_id": self.chapter_id,
            "version": self.version,
            "total_items": self.total_items,
            "normal_reading_count": len(self.normal_reading_items),
            "on_demand_count": len(self.on_demand_items),
            "normal_reading_items": [i.to_dict() for i in self.normal_reading_items],
            "on_demand_items": [i.to_dict() for i in self.on_demand_items],
            "policy_source": self.policy_source
        }


class ScienceNarrationPlanner:
    """
    Narration and Speaking Style Planner for Class 8 Science.
    Assigns pedagogical policy, prosody profiles, and pauses per region.
    """

    def __init__(self, loader=science_corpus_loader, physical_graph=science_physical_graph):
        self.loader = loader
        self.physical_graph = physical_graph
        self.grammar = science_grammar_engine
        self.style_profiles = SCIENCE_STYLE_PROFILES
        self._cached_plans: Dict[str, ScienceChapterNarrationPlan] = {}

    def plan_chapter_narration(self, chapter_id: str, version: str = "1.0") -> ScienceChapterNarrationPlan:
        ch_upper = chapter_id.upper()
        cache_key = f"{ch_upper}:{version}"
        if cache_key in self._cached_plans:
            return self._cached_plans[cache_key]

        self.loader.validate_and_load()
        self.physical_graph.build_graph()

        ch_meta = self.loader.get_chapter(ch_upper)
        if not ch_meta:
            raise KeyError(f"Chapter '{chapter_id}' not found in Science corpus.")

        # Determine default chapter speaking style from genre
        genre = self.grammar.get_genre_for_chapter(ch_upper)
        if genre == ScienceGenre.MATHEMATICAL_FORMULA_HEAVY:
            default_style = self.style_profiles[ScienceSpeakingStyle.MATHEMATICAL_NARRATION]
        elif genre == ScienceGenre.HISTORICAL_MODEL_SEQUENCE:
            default_style = self.style_profiles[ScienceSpeakingStyle.HISTORICAL_NARRATION]
        else:
            default_style = self.style_profiles[ScienceSpeakingStyle.SCIENTIFIC_EXPLANATION]

        normal_items: List[PlannedNarrationItem] = []
        on_demand_items: List[PlannedNarrationItem] = []

        pages = self.loader.get_pages_for_chapter(ch_upper)
        item_counter = 1

        for p_src in pages:
            p_graph = self.physical_graph.get_page(p_src.pdf_page_number)
            if not p_graph:
                continue

            for reg in p_graph.regions:
                # 1. Check for life-safety critical override
                is_safety = self.grammar.is_safety_critical(ch_upper, reg.text)
                if is_safety:
                    policy = NarrationPolicy.READ_DIRECTLY
                    style_profile = self.style_profiles[ScienceSpeakingStyle.SAFETY_CRITICAL]
                    normal = True
                    on_demand = True
                elif reg.region_type == "activity_box":
                    policy = NarrationPolicy.READ_DIRECTLY
                    style_profile = self.style_profiles[ScienceSpeakingStyle.PROCEDURAL_INSTRUCTIONAL]
                    normal = True
                    on_demand = True
                elif reg.region_type == "boxed_fact":
                    policy = NarrationPolicy.READ_THEN_EXPLAIN
                    if any(bio in reg.text for bio in ["परिचय शास्त्रज्ञांचा", "असे होऊन गेले", "मागे वळून पाहताना"]):
                        style_profile = self.style_profiles[ScienceSpeakingStyle.HISTORICAL_NARRATION]
                    else:
                        style_profile = default_style
                    normal = True
                    on_demand = True
                elif reg.region_type == "exercise_header":
                    policy = NarrationPolicy.EXCLUDE_FROM_NORMAL_READING
                    style_profile = default_style
                    normal = False
                    on_demand = True
                elif reg.region_type == "caption":
                    policy = NarrationPolicy.ON_DEMAND
                    style_profile = default_style
                    normal = False
                    on_demand = True
                elif "सोडवलेली उदाहरणे" in reg.text or "सोडविलेली उदाहरणे" in reg.text:
                    policy = NarrationPolicy.READ_THEN_EXPLAIN
                    style_profile = self.style_profiles[ScienceSpeakingStyle.MATHEMATICAL_NARRATION]
                    normal = True
                    on_demand = True
                elif "इंटरनेट माझा मित्र" in reg.text or "माहिती मिळवा" in reg.text:
                    policy = NarrationPolicy.EXCLUDE_FROM_NORMAL_READING
                    style_profile = default_style
                    normal = False
                    on_demand = True
                else:
                    policy = NarrationPolicy.READ_THEN_EXPLAIN
                    style_profile = default_style
                    normal = True
                    on_demand = True

                # 2. Sentence segmentation
                raw_sentences = [s.strip() for s in re.split(r'(?<=[।?!.])\s+', reg.text) if s.strip()]
                if not raw_sentences:
                    raw_sentences = [reg.text]

                sentences_data = []
                for s_idx, sent in enumerate(raw_sentences, 1):
                    tokens = [{"text": t} for t in sent.split()]
                    sentences_data.append({
                        "id": s_idx,
                        "text": sent,
                        "tokens": tokens,
                        "pause_after_ms": style_profile.pause_after_sentence_ms
                    })

                item = PlannedNarrationItem(
                    item_id=f"{ch_upper}_NP_{item_counter:03d}",
                    source_region_id=reg.region_id,
                    learning_unit_id=reg.learning_unit_id or f"{ch_upper}_LU_01",
                    chapter_id=ch_upper,
                    pdf_page_number=reg.pdf_page_number,
                    printed_page_number=reg.printed_page_number,
                    policy=policy,
                    style=style_profile,
                    canonical_text=reg.text,
                    speech_text=reg.text,
                    sentences=sentences_data,
                    is_spoken_in_normal_reading=normal,
                    is_available_on_demand=on_demand,
                    context_note=f"Region {reg.region_id} ({reg.region_type})",
                    policy_origin="AKSHARSETU_RECOMMENDATION"
                )
                item_counter += 1

                if normal:
                    normal_items.append(item)
                else:
                    on_demand_items.append(item)

        plan = ScienceChapterNarrationPlan(
            plan_id=f"{ch_upper}_NARRATION_PLAN_{version}",
            chapter_id=ch_upper,
            version=version,
            total_items=len(normal_items) + len(on_demand_items),
            normal_reading_items=normal_items,
            on_demand_items=on_demand_items
        )

        self._cached_plans[cache_key] = plan
        return plan


science_narration_planner = ScienceNarrationPlanner()
