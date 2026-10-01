"""
AksharSetu — Class 8 History Narration & Speaking Style Planner (Phases 6 & 7)

Phase 6: Narration Planning
- Decouples raw textbook text from TTS.
- Resolves narration policies:
  - READ_DIRECTLY
  - READ_THEN_EXPLAIN
  - EXPLAIN
  - ON_DEMAND
  - EXCLUDE_FROM_NORMAL_READING
- Configurable & versioned as AKSHARSETU_RECOMMENDATION.

Phase 7: Speaking Style
- Strictly separated from TTS Voice.
- Styles:
  - historical_narration (measured event-sequence prose)
  - explanatory_teacher (definition/policy pedagogical exposition)
  - descriptive (enumerative category survey)
- Includes pace, pause policies, sentence boundary behaviors, and discourse intent.
"""

from enum import Enum
from dataclasses import dataclass, field, asdict
from typing import Dict, List, Optional, Any, Tuple
import re

from corpus.history_loader import history_corpus_loader, HistoryChapterMetadata
from graphs.history_physical_graph import history_physical_graph, HistoryPhysicalRegion


class NarrationPolicy(str, Enum):
    READ_DIRECTLY = "READ_DIRECTLY"
    READ_THEN_EXPLAIN = "READ_THEN_EXPLAIN"
    EXPLAIN = "EXPLAIN"
    ON_DEMAND = "ON_DEMAND"
    EXCLUDE_FROM_NORMAL_READING = "EXCLUDE_FROM_NORMAL_READING"


class SpeakingStyle(str, Enum):
    HISTORICAL_NARRATION = "historical_narration"
    EXPLANATORY_TEACHER = "explanatory_teacher"
    DESCRIPTIVE = "descriptive"


@dataclass
class HistorySpeakingStyleProfile:
    style: SpeakingStyle
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


STYLE_PROFILES: Dict[SpeakingStyle, HistorySpeakingStyleProfile] = {
    SpeakingStyle.HISTORICAL_NARRATION: HistorySpeakingStyleProfile(
        style=SpeakingStyle.HISTORICAL_NARRATION,
        base_pace=1.0,
        pause_after_sentence_ms=250,
        pause_after_paragraph_ms=500,
        sentence_boundary_behavior="clear_full_stop",
        transition_behavior="measured_objective",
        intonation_intent="narration"
    ),
    SpeakingStyle.EXPLANATORY_TEACHER: HistorySpeakingStyleProfile(
        style=SpeakingStyle.EXPLANATORY_TEACHER,
        base_pace=0.92,  # Deliberate, clear cadence for comprehension
        pause_after_sentence_ms=350,
        pause_after_paragraph_ms=650,
        sentence_boundary_behavior="soft_deceleration",
        transition_behavior="conversational_warmth",
        intonation_intent="explanation"
    ),
    SpeakingStyle.DESCRIPTIVE: HistorySpeakingStyleProfile(
        style=SpeakingStyle.DESCRIPTIVE,
        base_pace=0.96,
        pause_after_sentence_ms=300,
        pause_after_paragraph_ms=550,
        sentence_boundary_behavior="rhythmic_enumeration",
        transition_behavior="structured_pacing",
        intonation_intent="narration"
    )
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
    style: HistorySpeakingStyleProfile
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
class HistoryChapterNarrationPlan:
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


class HistoryNarrationPlanner:
    """
    Narration and Speaking Style Planner for Class 8 History.
    Computes deterministic, versioned narration sequences.
    """

    def __init__(self, loader=history_corpus_loader, physical_graph=history_physical_graph):
        self.loader = loader
        self.physical_graph = physical_graph
        self.style_profiles = STYLE_PROFILES
        self._cached_plans: Dict[str, HistoryChapterNarrationPlan] = {}

    def plan_chapter_narration(self, chapter_id: str, version: str = "1.0") -> HistoryChapterNarrationPlan:
        ch_upper = chapter_id.upper()
        cache_key = f"{ch_upper}:{version}"
        if cache_key in self._cached_plans:
            return self._cached_plans[cache_key]

        self.loader.validate_and_load()
        self.physical_graph.build_graph()

        ch_meta = self.loader.get_chapter(ch_upper)
        if not ch_meta:
            raise KeyError(f"Chapter '{chapter_id}' not found in History corpus.")

        # Determine default chapter speaking style profile
        raw_style = ch_meta.speaking_style.lower()
        if "explanatory" in raw_style:
            style_profile = self.style_profiles[SpeakingStyle.EXPLANATORY_TEACHER]
        elif "descriptive" in raw_style:
            style_profile = self.style_profiles[SpeakingStyle.DESCRIPTIVE]
        else:
            style_profile = self.style_profiles[SpeakingStyle.HISTORICAL_NARRATION]

        normal_items: List[PlannedNarrationItem] = []
        on_demand_items: List[PlannedNarrationItem] = []

        pages = self.loader.get_pages_for_chapter(ch_upper)
        item_counter = 1

        for p_src in pages:
            p_graph = self.physical_graph.get_page(p_src.pdf_page_number)
            if not p_graph:
                continue

            for reg in p_graph.regions:
                # 1. Resolve Narration Policy per region type
                if reg.region_type == "exercise_header":
                    policy = NarrationPolicy.EXCLUDE_FROM_NORMAL_READING
                    normal = False
                    on_demand = True
                elif reg.region_type == "boxed_fact":
                    policy = NarrationPolicy.READ_THEN_EXPLAIN
                    normal = True
                    on_demand = True
                elif reg.region_type == "activity_box":
                    policy = NarrationPolicy.READ_DIRECTLY
                    normal = True
                    on_demand = True
                elif reg.region_type == "caption":
                    policy = NarrationPolicy.ON_DEMAND
                    normal = False
                    on_demand = True
                else:
                    policy = NarrationPolicy.READ_THEN_EXPLAIN
                    normal = True
                    on_demand = True

                # 2. Sentence Segmentation
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
                    context_note=f"Region {reg.region_id} ({reg.region_type})"
                )
                item_counter += 1

                if normal:
                    normal_items.append(item)
                else:
                    on_demand_items.append(item)

        plan = HistoryChapterNarrationPlan(
            plan_id=f"{ch_upper}_NARRATION_PLAN_{version}",
            chapter_id=ch_upper,
            version=version,
            total_items=len(normal_items) + len(on_demand_items),
            normal_reading_items=normal_items,
            on_demand_items=on_demand_items
        )

        self._cached_plans[cache_key] = plan
        return plan


history_narration_planner = HistoryNarrationPlanner()
