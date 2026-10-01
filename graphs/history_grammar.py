"""
AksharSetu — Class 8 History Grammar Engine (Phase 3)

First Subject-Specific Grammar implementation:
1. Universal Macro-Structure: Framing opener -> Body -> 5-part स्वाध्याय template.
2. 8 Distinct Historical Genre Patterns (never forcing chapters into a single rigid mold).
3. Chapter-Specific Exceptions & Nuances (interleaved storylines, blank visual plates, reflective boxes).
4. Historical Sensitivity Flags for measured narration delivery.
"""

from enum import Enum
from dataclasses import dataclass, field, asdict
from typing import Dict, List, Optional, Any


class HistoryGenre(str, Enum):
    CATEGORY_SURVEY = "category_survey"
    CHRONOLOGICAL_THEMATIC = "chronological_thematic"
    CAUSE_EVENT_CONSEQUENCE = "cause_event_consequence"
    ORGANIZATION_SURVEY = "organization_survey"
    FOUNDING_FACTIONAL = "founding_factional"
    BIOGRAPHY_LED = "biography_led"
    FLAGSHIP_EVENT = "flagship_event"
    STATE_FORMATION = "state_formation"


@dataclass
class HistoryStructuralPattern:
    pattern_id: str
    genre: HistoryGenre
    name: str
    description: str
    associated_chapters: List[str]
    pedagogical_focus: str
    evidence_status: str = "SUPPORTED_INFERENCE"


HISTORY_PATTERNS: Dict[HistoryGenre, HistoryStructuralPattern] = {
    HistoryGenre.CATEGORY_SURVEY: HistoryStructuralPattern(
        pattern_id="PAT_HIST_01",
        genre=HistoryGenre.CATEGORY_SURVEY,
        name="Category Survey",
        description="introduce domain -> enumerate subtypes -> illustrate each with concrete historical examples",
        associated_chapters=["CH_01"],
        pedagogical_focus="Classification of physical, written, oral and audiovisual sources."
    ),
    HistoryGenre.CHRONOLOGICAL_THEMATIC: HistoryStructuralPattern(
        pattern_id="PAT_HIST_02",
        genre=HistoryGenre.CHRONOLOGICAL_THEMATIC,
        name="Chronological Thematic",
        description="chronological era sequence with thematic causal threads (Renaissance -> Industrial Revolution -> Company Rule)",
        associated_chapters=["CH_02", "CH_03"],
        pedagogical_focus="Evolution of European imperialism and administrative/economic impacts in India."
    ),
    HistoryGenre.CAUSE_EVENT_CONSEQUENCE: HistoryStructuralPattern(
        pattern_id="PAT_HIST_04",
        genre=HistoryGenre.CAUSE_EVENT_CONSEQUENCE,
        name="Cause -> Event -> Consequence",
        description="socio-political sparks -> regional insurrection sequence -> Queen's Proclamation & reorganization",
        associated_chapters=["CH_04"],
        pedagogical_focus="Comprehensive breakdown of 1857 freedom struggle causes, events, and aftermath."
    ),
    HistoryGenre.ORGANIZATION_SURVEY: HistoryStructuralPattern(
        pattern_id="PAT_HIST_05",
        genre=HistoryGenre.ORGANIZATION_SURVEY,
        name="Organization-by-Organization Survey",
        description="reform organizations -> founders & leaders -> ideological tenets -> social emancipation impact",
        associated_chapters=["CH_05", "CH_11"],
        pedagogical_focus="Social and religious reform movements; peasant, workers, and Dalit movements."
    ),
    HistoryGenre.FOUNDING_FACTIONAL: HistoryStructuralPattern(
        pattern_id="PAT_HIST_06",
        genre=HistoryGenre.FOUNDING_FACTIONAL,
        name="Conditions -> Founding -> Evolution",
        description="socio-political discontent -> establishment of National Congress -> moderate vs extremist strands",
        associated_chapters=["CH_06"],
        pedagogical_focus="Early nationalist awakening, partition of Bengal, and four-point programme."
    ),
    HistoryGenre.BIOGRAPHY_LED: HistoryStructuralPattern(
        pattern_id="PAT_HIST_07",
        genre=HistoryGenre.BIOGRAPHY_LED,
        name="Biography-Led Campaign Chronology",
        description="flagship leadership principles -> multi-phased mass mobilization -> pan-Indian resistance",
        associated_chapters=["CH_07", "CH_10"],
        pedagogical_focus="Gandhian non-violent mass campaigns and armed revolutionary sacrifices."
    ),
    HistoryGenre.FLAGSHIP_EVENT: HistoryStructuralPattern(
        pattern_id="PAT_HIST_08",
        genre=HistoryGenre.FLAGSHIP_EVENT,
        name="Single Flagship Event / Campaign",
        description="singular national struggle spark -> nationwide civil disobedience / Quit India resolution -> parallel governance",
        associated_chapters=["CH_08", "CH_09"],
        pedagogical_focus="Salt Satyagraha, Round Table Conferences, 1942 Quit India, and Azad Hind Fauj."
    ),
    HistoryGenre.STATE_FORMATION: HistoryStructuralPattern(
        pattern_id="PAT_HIST_12",
        genre=HistoryGenre.STATE_FORMATION,
        name="State Formation & Territorial Integration",
        description="boundary commissions / constitutional proposals -> mass popular agitation -> territorial integration",
        associated_chapters=["CH_12", "CH_13", "CH_14"],
        pedagogical_focus="Indian Independence, integration of princely states, and Samyukta Maharashtra Movement."
    )
}


@dataclass
class SwadhyayExerciseSpec:
    section_index: int
    exercise_name_marathi: str
    exercise_type: str
    description: str
    narration_policy: str = "EXCLUDE_FROM_NORMAL_READING"
    on_demand_available: bool = True


@dataclass
class HistorySwadhyayGrammar:
    pattern_scope: str = "COMMON"
    exercises: List[SwadhyayExerciseSpec] = field(default_factory=lambda: [
        SwadhyayExerciseSpec(1, "योग्य पर्याय निवडून विधाने पुन्हा लिहा", "mcq", "Multiple choice statements with word bank"),
        SwadhyayExerciseSpec(2, "पुढील विधाने सकारण स्पष्ट करा", "reasoned_statement", "Reasoned causal explanations"),
        SwadhyayExerciseSpec(3, "थोडक्यात टीपा लिहा / उत्तरे लिहा", "short_notes", "Short and detailed descriptive responses"),
        SwadhyayExerciseSpec(4, "संकल्पना चित्र / कालरेषा / तक्ता पूर्ण करा", "structured_completion", "Graphic organizer, timeline or matrix completion"),
        SwadhyayExerciseSpec(5, "उपक्रम / प्रकल्प", "activity_project", "Research or presentation project activity")
    ])


@dataclass
class ChapterGrammarNuance:
    chapter_id: str
    nuance_type: str
    description: str
    sensitivity_flag: Optional[str] = None
    structural_rule: str = "default_linear"


CHAPTER_NUANCES: Dict[str, ChapterGrammarNuance] = {
    "CH_01": ChapterGrammarNuance(
        chapter_id="CH_01",
        nuance_type="procedural_activity_box",
        description="Features 'करून पहा' (gather patriotic songs and perform) and 'माहीत आहे का तुम्हांला' (Aga Khan Palace archives).",
        structural_rule="category_enumeration_pacing"
    ),
    "CH_02": ChapterGrammarNuance(
        chapter_id="CH_02",
        nuance_type="procedural_info_box",
        description="Features 'चला जाणून घेऊया' box discussing European maritime expeditions.",
        structural_rule="thematic_causality_flow"
    ),
    "CH_04": ChapterGrammarNuance(
        chapter_id="CH_04",
        nuance_type="historical_violence_sensitivity",
        description="Detailed military battles of 1857 and punitive crackdowns.",
        sensitivity_flag="measured_non_dramatized_tone",
        structural_rule="cause_event_consequence"
    ),
    "CH_05": ChapterGrammarNuance(
        chapter_id="CH_05",
        nuance_type="reflective_question_box",
        description="Unique 'जरा विचार करा' (ponder over this) reflective box not repeated in other chapters.",
        structural_rule="organization_survey_with_reflection"
    ),
    "CH_09": ChapterGrammarNuance(
        chapter_id="CH_09",
        nuance_type="interleaved_parallel_strands",
        description="Two parallel storylines: domestic Quit India mobilization and Netaji's Azad Hind Sena. Must not be forced into a single strictly serial timeline.",
        sensitivity_flag="factual_solemn_tone_nandurbar_martyrs",
        structural_rule="interleaved_parallel_timeline"
    ),
    "CH_12": ChapterGrammarNuance(
        chapter_id="CH_12",
        nuance_type="visual_plate_caveat",
        description="PDF page 66 returned blank text layer. It is a full-page plate/map/photo; must be tracked as UNVERIFIED rather than absent.",
        sensitivity_flag="solemn_tone_martyrdom",
        structural_rule="handle_visual_plate_caveat"
    ),
    "CH_14": ChapterGrammarNuance(
        chapter_id="CH_14",
        nuance_type="state_formation_martyrs",
        description="Samyukta Maharashtra movement and the sacrifice of 106 Hutatmas.",
        sensitivity_flag="respectful_solemn_delivery",
        structural_rule="commission_agitation_formation"
    )
}


class HistoryGrammarEngine:
    """
    Dedicated subject-specific grammar engine for Class 8 History.
    """

    def __init__(self):
        self.patterns = HISTORY_PATTERNS
        self.swadhyay = HistorySwadhyayGrammar()
        self.nuances = CHAPTER_NUANCES

    def get_pattern_for_chapter(self, chapter_id: str) -> HistoryStructuralPattern:
        ch_upper = chapter_id.upper()
        for p in self.patterns.values():
            if ch_upper in p.associated_chapters:
                return p
        return self.patterns[HistoryGenre.CHRONOLOGICAL_THEMATIC]

    def get_chapter_nuance(self, chapter_id: str) -> Optional[ChapterGrammarNuance]:
        return self.nuances.get(chapter_id.upper())

    def get_swadhyay_template(self) -> HistorySwadhyayGrammar:
        return self.swadhyay

    def get_grammar_profile(self, chapter_id: str) -> Dict[str, Any]:
        ch_upper = chapter_id.upper()
        pattern = self.get_pattern_for_chapter(ch_upper)
        nuance = self.get_chapter_nuance(ch_upper)

        return {
            "chapter_id": ch_upper,
            "subject": "history",
            "structural_skeleton": "framing_opener -> historical_body -> 5_part_swadhyay",
            "pattern": asdict(pattern),
            "nuance": asdict(nuance) if nuance else None,
            "swadhyay_structure": [asdict(e) for e in self.swadhyay.exercises],
            "narration_policy_default": "READ_THEN_EXPLAIN",
            "provenance": {
                "source": "corpus/dataset/history/corpus_analysis.md",
                "status": "SUPPORTED_INFERENCE"
            }
        }


history_grammar_engine = HistoryGrammarEngine()
