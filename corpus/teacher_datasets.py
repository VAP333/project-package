"""
AksharSetu — Datasets for Future Teacher Behavior & Open Marathi TTS (§0 & Part 6)

Strictly separates:
1. DATASET A: TEACHER BEHAVIOR (Pedagogy, reasoning, transitions, framing)
   Answers: "HOW A TEACHER TEACHES"
2. DATASET B: TEACHER SPEECH (Acoustic audio, exact Marathi transcripts, prosody, pauses)
   Answers: "HOW THAT TEACHER SOUNDS"

Guarantees:
- Clear separation between pedagogical model fine-tuning and acoustic TTS voice training.
- Exact schemas ready for dataset collection, curation, and verification.
"""

from dataclasses import dataclass, field, asdict
from typing import Dict, List, Optional, Any
import json
import os

@dataclass
class TeacherBehaviorSample:
    """
    DATASET A — TEACHER BEHAVIOR
    Used to train/fine-tune AksharSetu's pedagogical intelligence.
    """
    sample_id: str
    subject: str # "geography", "marathi", "science", etc.
    chapter: str
    learning_unit: str
    student_context: str
    textbook_context: str
    teacher_response: str
    teaching_intent: str # "clarify_concept", "guide_observation", "encourage_reflection"
    transition: str
    difficulty: str = "basic" # "basic", "intermediate", "advanced"
    metadata: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)

@dataclass
class ProsodyMetadata:
    pace: float = 0.95
    emphasis: List[str] = field(default_factory=list)
    pause_points: List[Dict[str, Any]] = field(default_factory=list) # e.g. [{"word_after": "नळदुर्ग", "pause_ms": 300}]

@dataclass
class TeacherSpeechSample:
    """
    DATASET B — TEACHER SPEECH
    Used to train/adapt candidate Marathi TTS models (such as IndicF5).
    """
    sample_id: str
    text: str
    audio_path: str
    speaker: str # e.g. "teacher_marathi_female_1"
    language: str = "mr-IN"
    style: str = "teacher_explanation" # "teacher_explanation", "teacher_transition", "canonical_reading"
    intent: str = "clarify_concept"
    transcript: str = ""
    prosody_metadata: Dict[str, Any] = field(default_factory=dict)
    sample_rate_hz: int = 24000
    duration_sec: float = 0.0

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)

class TeacherDatasetManager:
    """Manages persistence and retrieval of Teacher Behavior & Teacher Speech datasets."""
    def __init__(self, storage_dir: str = "corpus/teacher_data"):
        self.storage_dir = storage_dir
        self.behavior_dir = os.path.join(storage_dir, "dataset_a_behavior")
        self.speech_dir = os.path.join(storage_dir, "dataset_b_speech")
        os.makedirs(self.behavior_dir, exist_ok=True)
        os.makedirs(self.speech_dir, exist_ok=True)

    def add_behavior_sample(self, sample: TeacherBehaviorSample):
        path = os.path.join(self.behavior_dir, f"{sample.sample_id}.json")
        with open(path, "w", encoding="utf-8") as f:
            json.dump(sample.to_dict(), f, ensure_ascii=False, indent=2)

    def add_speech_sample(self, sample: TeacherSpeechSample):
        path = os.path.join(self.speech_dir, f"{sample.sample_id}.json")
        with open(path, "w", encoding="utf-8") as f:
            json.dump(sample.to_dict(), f, ensure_ascii=False, indent=2)

    def count_samples(self) -> Dict[str, int]:
        behaviors = len([f for f in os.listdir(self.behavior_dir) if f.endswith(".json")])
        speech = len([f for f in os.listdir(self.speech_dir) if f.endswith(".json")])
        return {
            "dataset_a_behavior_samples": behaviors,
            "dataset_b_speech_samples": speech
        }
