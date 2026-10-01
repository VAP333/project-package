"""
AksharSetu — Semantic Narration Blocks & Hierarchy (§1, §2, §3, §4, §5)

Replaces fragment-level PDF line parsing with human-like Paragraph & Dialogue Narration.
Hierarchy:
Document
└── Chapter
    └── Learning Unit
        └── Semantic Block (Paragraph, Dialogue Block, Stanza, Activity, etc.)
            ├── Sentences (Internal timing & token highlights)
            └── Words / Tokens (BBoxes & Pronunciation anchors)
"""

from enum import Enum
from dataclasses import dataclass, field, asdict
from typing import Dict, List, Optional, Any

class SemanticBlockType(str, Enum):
    PARAGRAPH = "paragraph"
    HEADING = "heading"
    SUBHEADING = "subheading"
    POETRY_STANZA = "poetry_stanza"
    DIALOGUE_BLOCK = "dialogue_block"
    FIGURE = "figure"
    FIGURE_CAPTION = "figure_caption"
    TABLE = "table"
    ACTIVITY = "activity"
    DISCUSSION = "discussion"
    EXAMPLE = "example"
    DEFINITION = "definition"
    EXERCISE = "exercise"
    QUESTION = "question"
    ANSWER = "answer"
    SUPPLEMENTARY_BOX = "supplementary_box"

@dataclass
class DialogueTurn:
    """Individual speaker turn within a Dialogue Block."""
    turn_id: str
    speaker: str # e.g. "शिक्षिका", "राहुल", "साक्षी"
    speaker_role: str # "teacher" | "student" | "narrator"
    text: str # Clean speech text (e.g. without redundant "शिक्षिका : " prefix)
    order: int
    learning_unit_id: str
    source_region_id: str
    voice_profile: str = "shreya"
    prosody_style: str = "dialogue_teacher" # or "dialogue_student"
    pause_after_ms: int = 400

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)

@dataclass
class SupportingMaterial:
    """Non-interrupting visual or supplementary content attached to a concept."""
    material_id: str
    material_type: str # "map" | "figure" | "table" | "equipment" | "supplementary_box"
    title: str
    caption_text: str = ""
    caption_region_id: Optional[str] = None
    target_region_id: Optional[str] = None
    supports_learning_unit_id: str = ""
    supports_concept: str = ""
    auto_narrate: bool = False # Main prose has priority; visuals narrated on-demand
    is_essential: bool = True
    image_url: Optional[str] = None
    bbox: List[float] = field(default_factory=list)
    explanation: str = ""

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)

@dataclass
class SemanticSentence:
    """Internal sentence boundary preserved for word-level highlighting and resume position."""
    sentence_id: int
    text: str
    tokens: List[Dict[str, Any]] = field(default_factory=list) # [{text, flagged, bbox}]
    bbox: List[float] = field(default_factory=list)
    start_char: int = 0
    end_char: int = 0

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)

@dataclass
class SemanticNarrationBlock:
    """
    Primary user-facing narration and UI unit.
    Encompasses complete paragraphs, dialogue blocks, or stanzas rather than tiny line cards.
    """
    block_id: str
    block_type: SemanticBlockType
    chapter_id: str
    page_id: str
    pdf_page: int
    printed_page: Optional[int]
    learning_unit_id: str
    primary_content: bool = True # True = Main narrative flow, False = Supplementary/Supporting
    canonical_text: str = ""
    sentences: List[SemanticSentence] = field(default_factory=list)
    dialogue_turns: List[DialogueTurn] = field(default_factory=list)
    supporting_visuals: List[SupportingMaterial] = field(default_factory=list)
    source_region_ids: List[str] = field(default_factory=list)
    bbox: List[float] = field(default_factory=list)
    tutor_explanation: Optional[str] = None
    tutor_plan: Optional[Dict[str, Any]] = None
    metadata: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        d = asdict(self)
        d["block_type"] = self.block_type.value
        return d
