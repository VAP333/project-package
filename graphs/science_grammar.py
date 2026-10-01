"""
AksharSetu — Class 8 Science Grammar Engine (Phase 3)

Subject-Specific Grammar for Class 8 General Science:
1. Universal Macro-Structure:
   - थोड़े आठवा / सांगा पाहू (prior grade recall & discussion)
   - Body prose interleaved with 'करून पहा' (hands-on experiment) and 'जरा डोके चालवा'
   - स्वाध्याय (multi-format assessment)
2. 7 Distinct Scientific Genre Patterns:
   - mathematical_formula_heavy (CH_03, CH_14, CH_16)
   - historical_model_sequence (CH_05)
   - biology_catalogue (CH_10, CH_11)
   - environmental_social_issue (CH_08, CH_09, CH_17, CH_18)
   - chemistry_reaction (CH_07, CH_12, CH_13)
   - category_survey_activity (CH_01, CH_02, CH_06, CH_04, CH_15)
   - astronomical_evolution (CH_19)
3. Safety-Critical Flags (IMMEDIATE narration priority):
   - CH_09: earthquake & fire emergency protocols
   - CH_12: chemical handling & acid explosion safety
"""

from enum import Enum
from dataclasses import dataclass, field, asdict
from typing import Dict, List, Optional, Any


class ScienceGenre(str, Enum):
    CATEGORY_SURVEY_ACTIVITY = "category_survey_activity"
    MATHEMATICAL_FORMULA_HEAVY = "mathematical_formula_heavy"
    HISTORICAL_MODEL_SEQUENCE = "historical_model_sequence"
    BIOLOGY_CATALOGUE = "biology_catalogue"
    ENVIRONMENTAL_SOCIAL_ISSUE = "environmental_social_issue"
    CHEMISTRY_REACTION = "chemistry_reaction"
    ASTRONOMICAL_EVOLUTION = "astronomical_evolution"


@dataclass
class ScienceStructuralPattern:
    pattern_id: str
    genre: ScienceGenre
    name: str
    description: str
    associated_chapters: List[str]
    pedagogical_focus: str
    evidence_status: str = "SUPPORTED_INFERENCE"


SCIENCE_PATTERNS: Dict[ScienceGenre, ScienceStructuralPattern] = {
    ScienceGenre.CATEGORY_SURVEY_ACTIVITY: ScienceStructuralPattern(
        pattern_id="PAT_SCI_01",
        genre=ScienceGenre.CATEGORY_SURVEY_ACTIVITY,
        name="Category Survey with Hands-on Activity",
        description="recall -> classification -> per-category hands-on activity (करून पहा) -> observations",
        associated_chapters=["CH_01", "CH_02", "CH_04", "CH_06", "CH_15"],
        pedagogical_focus="Classification of living world, health diseases, electricity, matter, and sound."
    ),
    ScienceGenre.MATHEMATICAL_FORMULA_HEAVY: ScienceStructuralPattern(
        pattern_id="PAT_SCI_02",
        genre=ScienceGenre.MATHEMATICAL_FORMULA_HEAVY,
        name="Mathematical / Formula-Heavy Derivation",
        description="concept -> formula derivation -> units -> step-by-step worked numerical examples (सोडवलेली उदाहरणे)",
        associated_chapters=["CH_03", "CH_14", "CH_16"],
        pedagogical_focus="Mechanics, heat measurement, and reflection of light with numerical problem solving."
    ),
    ScienceGenre.HISTORICAL_MODEL_SEQUENCE: ScienceStructuralPattern(
        pattern_id="PAT_SCI_03",
        genre=ScienceGenre.HISTORICAL_MODEL_SEQUENCE,
        name="Historical Model Sequence",
        description="sequential scientist-model pairs (Dalton -> Thomson -> Rutherford -> Bohr) with experimental evidence and limitations",
        associated_chapters=["CH_05"],
        pedagogical_focus="Evolution of atomic structure models and discovery of subatomic particles."
    ),
    ScienceGenre.BIOLOGY_CATALOGUE: ScienceStructuralPattern(
        pattern_id="PAT_SCI_04",
        genre=ScienceGenre.BIOLOGY_CATALOGUE,
        name="Biological Organelle / System Catalogue",
        description="organelle / organ survey -> microscopic structure -> physiological function -> health connections",
        associated_chapters=["CH_10", "CH_11"],
        pedagogical_focus="Cell organelles and human organ systems (respiratory, circulatory, heart)."
    ),
    ScienceGenre.ENVIRONMENTAL_SOCIAL_ISSUE: ScienceStructuralPattern(
        pattern_id="PAT_SCI_05",
        genre=ScienceGenre.ENVIRONMENTAL_SOCIAL_ISSUE,
        name="Environmental Policy & Social Impact",
        description="ecological problem -> causes -> human / societal impact -> mitigation & disaster management protocols",
        associated_chapters=["CH_08", "CH_09", "CH_17", "CH_18"],
        pedagogical_focus="Pollution, disaster management, man-made materials, and ecosystem conservation."
    ),
    ScienceGenre.CHEMISTRY_REACTION: ScienceStructuralPattern(
        pattern_id="PAT_SCI_06",
        genre=ScienceGenre.CHEMISTRY_REACTION,
        name="Chemical Properties & Reaction Equations",
        description="substance properties -> chemical indicators -> word / symbolic equations (reactants -> products) -> bonding",
        associated_chapters=["CH_07", "CH_12", "CH_13"],
        pedagogical_focus="Metals/non-metals, acids/bases, and chemical bonding and reactions."
    ),
    ScienceGenre.ASTRONOMICAL_EVOLUTION: ScienceStructuralPattern(
        pattern_id="PAT_SCI_07",
        genre=ScienceGenre.ASTRONOMICAL_EVOLUTION,
        name="Scale & Stellar Evolutionary Trajectory",
        description="cosmic scale comparisons -> interstellar clouds -> equilibrium -> mass-dependent final stellar states",
        associated_chapters=["CH_19"],
        pedagogical_focus="Life cycle of stars from birth to white dwarf, neutron star, or black hole."
    ),
}


class ScienceGrammarEngine:
    """
    Grammar engine evaluating scientific structural patterns and safety constraints.
    """

    def __init__(self):
        self.patterns = SCIENCE_PATTERNS
        self.chapter_genre_map: Dict[str, ScienceGenre] = {}
        for genre, pat in self.patterns.items():
            for ch in pat.associated_chapters:
                self.chapter_genre_map[ch] = genre

    def get_genre_for_chapter(self, chapter_id: str) -> ScienceGenre:
        ch_upper = chapter_id.upper()
        return self.chapter_genre_map.get(ch_upper, ScienceGenre.CATEGORY_SURVEY_ACTIVITY)

    def get_pattern_for_chapter(self, chapter_id: str) -> ScienceStructuralPattern:
        genre = self.get_genre_for_chapter(chapter_id)
        return self.patterns[genre]

    def is_safety_critical(self, chapter_id: str, text: str) -> bool:
        """Flags life-safety critical passages requiring immediate attention."""
        ch_upper = chapter_id.upper()
        if ch_upper in ("CH_09", "CH_12"):
            safety_keywords = [
                "भूकंप", "आग", "विषारी", "स्पर्श करू नका", "चव घेऊ नका",
                "पाणी ओतू नका", "धोका", "खबरदारी", "आपत्ती", "प्रथमोपचार"
            ]
            return any(k in text for k in safety_keywords)
        return False

    def get_grammar_profile(self, chapter_id: str) -> Dict[str, Any]:
        ch_upper = chapter_id.upper()
        pattern = self.get_pattern_for_chapter(ch_upper)
        return {
            "chapter_id": ch_upper,
            "pattern_id": pattern.pattern_id,
            "genre": pattern.genre.value,
            "pattern_name": pattern.name,
            "description": pattern.description,
            "pedagogical_focus": pattern.pedagogical_focus,
            "macro_template": "थोडे आठवा -> करून पहा / जरा डोके चालवा -> स्वाध्याय",
            "has_safety_critical_elements": ch_upper in ("CH_09", "CH_12")
        }


science_grammar_engine = ScienceGrammarEngine()
