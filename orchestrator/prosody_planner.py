"""
AksharSetu — Provider-Neutral Prosody Planner (§12 & Discourse Intent Rule)

PROSODY MUST NOT DEPEND ONLY ON SENTIMENT ANALYSIS.
Uses pedagogical / discourse intent:
- narration
- explanation
- question
- answer
- dialogue_teacher
- dialogue_student
- emphasis
- contrast
- correction
- encouragement
- surprise
- transition
- recap
- storytelling

Provider-neutral: Sarvam and IndicF5 adapters translate only supported fields.
"""

from dataclasses import dataclass, field, asdict
from typing import Dict, List, Optional, Any

@dataclass
class ProsodyPlan:
    discourse_intent: str = "narration" # "narration" | "explanation" | "question" | "dialogue_teacher" | "dialogue_student" | etc.
    pace: float = 1.0 # 0.7 to 1.3
    energy: str = "warm" # "warm" | "steady" | "inquisitive" | "dynamic" | "gentle"
    pause_before_ms: int = 0
    pause_after_ms: int = 250
    emphasis_terms: List[str] = field(default_factory=list)
    question_intonation: bool = False
    sentence_boundary_strength: float = 0.5
    temperature: float = 0.70

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)

class ProsodyPlanner:
    """
    Creates provider-neutral prosody plans driven by educational discourse intent.
    Does not invent unsupported TTS parameters.
    """
    def plan_prosody(
        self,
        text: str,
        discourse_intent: str = "narration",
        speaker_role: Optional[str] = None,
        base_pace: float = 1.0,
        emphasis_terms: Optional[List[str]] = None
    ) -> ProsodyPlan:
        intent = discourse_intent
        clean_text = text.strip()
        is_question = clean_text.endswith("?") or clean_text.endswith("?") or "का?" in clean_text or "कसे?" in clean_text or "सांगा" in clean_text

        # Override intent if sentence is clearly an inquiry
        if is_question and intent not in ("dialogue_student", "dialogue_teacher"):
            intent = "question"

        if speaker_role == "student":
            # Inquisitive, brighter student cadence
            return ProsodyPlan(
                discourse_intent="dialogue_student",
                pace=min(1.15, base_pace * 1.03), # Slightly brisker, energetic student pace
                energy="inquisitive",
                pause_before_ms=250, # Natural pause between speakers
                pause_after_ms=350,
                emphasis_terms=emphasis_terms or [],
                question_intonation=is_question,
                temperature=0.76
            )
        elif speaker_role == "teacher":
            # Warm, steady, authoritative teacher cadence
            return ProsodyPlan(
                discourse_intent="dialogue_teacher",
                pace=max(0.75, base_pace * 0.95), # More deliberate, clear delivery
                energy="warm",
                pause_before_ms=250,
                pause_after_ms=400,
                emphasis_terms=emphasis_terms or [],
                question_intonation=is_question,
                temperature=0.72
            )
        elif intent == "question":
            return ProsodyPlan(
                discourse_intent="question",
                pace=base_pace,
                energy="inquisitive",
                pause_before_ms=150,
                pause_after_ms=450,
                emphasis_terms=emphasis_terms or [],
                question_intonation=True,
                temperature=0.75
            )
        elif intent == "explanation":
            return ProsodyPlan(
                discourse_intent="explanation",
                pace=max(0.75, base_pace * 0.95),
                energy="warm",
                pause_before_ms=200,
                pause_after_ms=500,
                emphasis_terms=emphasis_terms or [],
                question_intonation=False,
                temperature=0.74
            )
        elif intent == "transition":
            return ProsodyPlan(
                discourse_intent="transition",
                pace=base_pace,
                energy="warm",
                pause_before_ms=200,
                pause_after_ms=350,
                emphasis_terms=[],
                question_intonation=False,
                temperature=0.72
            )
        elif intent == "heading":
            return ProsodyPlan(
                discourse_intent="heading",
                pace=max(0.8, base_pace * 0.92),
                energy="steady",
                pause_before_ms=100,
                pause_after_ms=600,
                emphasis_terms=emphasis_terms or [],
                temperature=0.65
            )
        else:
            # Standard textbook narrative prose
            return ProsodyPlan(
                discourse_intent="narration",
                pace=base_pace,
                energy="steady",
                pause_before_ms=0,
                pause_after_ms=300,
                emphasis_terms=emphasis_terms or [],
                question_intonation=is_question,
                temperature=0.68
            )

prosody_planner = ProsodyPlanner()
